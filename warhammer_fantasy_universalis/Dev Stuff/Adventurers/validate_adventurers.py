"""Static integrity checks and executable tests of the actual relocation script.

Run with Python 3, no dependencies. This is not a substitute for an EU4 playtest.
The small interpreter below fails on unknown statements rather than pretending
to model the entire engine. It reads the generated Clausewitz files directly.
"""
from pathlib import Path
from dataclasses import dataclass, field
from collections import Counter
import copy
import hashlib
import itertools
import json
import re
import struct

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
DATA = json.loads((HERE / 'event_data.json').read_text())


def parse(text):
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|#[^\n]*|[{}=]|[^\s{}=#"]+', text.lstrip('\ufeff'))
    tokens = [t for t in tokens if not t.startswith('#')]
    position = 0

    def item():
        nonlocal position
        token = tokens[position]
        position += 1
        if token == '{':
            return block(True)
        assert token not in ('}', '='), (position, token)
        return token[1:-1] if token.startswith('"') else token

    def block(nested=False):
        nonlocal position
        result = []
        while position < len(tokens):
            if tokens[position] == '}':
                assert nested, 'Unexpected closing brace'
                position += 1
                return result
            key = item()
            if position < len(tokens) and tokens[position] == '=':
                position += 1
                result.append((key, item()))
            else:
                result.append(key)
        assert not nested, 'Unclosed block'
        return result

    return block()


def read(relative):
    return parse((ROOT / relative).read_text(encoding='utf-8-sig'))


def get(block, key, default=None):
    values = all_values(block, key)
    assert len(values) <= 1, ('Repeated singleton', key)
    return values[0] if values else default


def all_values(block, key):
    return [v for item in block if isinstance(item, tuple) for k, v in [item] if k == key]


def walk(block):
    for item in block:
        if isinstance(item, tuple):
            key, value = item
            yield key, value
            if isinstance(value, list):
                yield from walk(value)


TRIGGERS = dict(read('common/scripted_triggers/war_adventurer_triggers.txt'))
EFFECTS = dict(read('common/scripted_effects/war_adventurer_effects.txt'))
ELIGIBLE = set(json.loads((HERE / 'map_eligibility.json').read_text())['allowed'])
GROUPS = {k: {int(v) for v in b if isinstance(v, str) and v.isdigit()}
          for k, b in read('map/provincegroup.txt') if isinstance(b, list)}
ARRIVALS = {}


@dataclass
class Entity:
    key: str
    kind: str
    owner: object = None
    provinces: list = field(default_factory=list)
    neighbors: list = field(default_factory=list)
    modifiers: set = field(default_factory=set)
    flags: dict = field(default_factory=dict)
    variables: dict = field(default_factory=dict)
    attrs: dict = field(default_factory=dict)


class Script:
    def __init__(self, countries, root):
        self.countries = countries
        self.root = root
        self.targets = {}
        self.global_flags = set()
        self.day = 1000
        self.choices = []
        self.pools = []
        self.applied = []
        self.dispatched = []
        self.entities = {x.key: x for c in countries for x in [c, *c.provinces]}

    def resolve(self, value):
        if value == 'ROOT':
            return self.root
        if value.startswith('event_target:'):
            return self.targets.get(value.split(':', 1)[1])
        return self.entities.get(value)

    def candidates(self, key, entity):
        if key.endswith('_neighbor_country'):
            return entity.neighbors
        if key.endswith('_owned_province'):
            return entity.provinces
        if key.endswith('_country'):
            return self.countries
        raise AssertionError(('Unknown selector', key))

    def test(self, block, entity):
        if entity is None:
            return False
        return all(self.test_one(k, v, entity) for k, v in block)

    def test_one(self, key, value, entity):
        if key == 'OR':
            return any(self.test_one(k, v, entity) for k, v in value)
        if key in ('AND', 'limit'):
            return self.test(value, entity)
        if key == 'NOT':
            return not self.test(value, entity)
        if key in TRIGGERS:
            return self.test(TRIGGERS[key], entity) == (value == 'yes')
        if key == 'owner':
            return self.test(value, entity.owner)
        if key == 'ROOT' or key.startswith('event_target:') or key.isdigit():
            return self.test(value, self.resolve(key))
        if key.startswith('any_'):
            return any(self.test(value, p) for p in self.candidates(key, entity))
        if key == 'always':
            return value == 'yes'
        if key in ('has_country_modifier', 'has_province_modifier'):
            return value in entity.modifiers
        if key == 'has_global_flag':
            return value in self.global_flags
        if key == 'has_province_flag':
            return value in entity.flags
        if key == 'had_province_flag':
            return get(value, 'flag') in entity.flags and self.day - entity.flags[get(value, 'flag')] >= int(get(value, 'days'))
        if key == 'check_variable':
            return entity.variables.get(get(value, 'which'), 0) >= float(get(value, 'value'))
        if key == 'owned_by':
            return entity.owner is self.resolve(value)
        if key == 'tag':
            return entity is self.resolve(value)
        if key == 'is_empty':
            return (entity.owner is None) == (value == 'yes')
        if key == 'is_city':
            return entity.attrs.get('city', True) == (value == 'yes')
        if key == 'province_group':
            return int(entity.key) in GROUPS[value]
        if key in ('trade_goods', 'area', 'region', 'superregion', 'has_winter', 'has_climate', 'has_port', 'is_at_war'):
            return entity.attrs.get(key) == value
        raise AssertionError(('Unsupported trigger in test interpreter', key, value))

    def run(self, block, entity):
        previous_if = None
        for key, value in block:
            if key == 'if':
                previous_if = self.test(get(value, 'limit'), entity)
                if previous_if:
                    self.run([(k, v) for k, v in value if k != 'limit'], entity)
            elif key == 'else':
                assert previous_if is not None
                if not previous_if:
                    self.run(value, entity)
            elif key in ('limit', 'ai_chance', 'name', 'custom_tooltip'):
                continue
            elif key == 'hidden_effect':
                self.run(value, entity)
            elif key in EFFECTS:
                assert isinstance(value, list) or value == 'yes'
                params = dict(value) if isinstance(value, list) else {}

                def expand(tree):
                    if isinstance(tree, str):
                        for k, v in params.items():
                            tree = tree.replace('$' + k + '$', v)
                        return tree
                    return [(expand(k), expand(v)) for k, v in tree]

                self.run(expand(EFFECTS[key]), entity)
            elif key.startswith(('random_', 'every_')):
                pool = [p for p in self.candidates(key, entity) if self.test(get(value, 'limit', []), p)]
                if key.startswith('random_'):
                    self.pools.append((key, [p.key for p in pool]))
                    index = self.choices.pop(0) if self.choices else 0
                    pool = [pool[index % len(pool)]] if pool else []
                for target in pool:
                    self.run([(k, v) for k, v in value if k != 'limit'], target)
            elif key == 'owner':
                assert entity.owner
                self.run(value, entity.owner)
            elif key == 'ROOT' or key.startswith('event_target:') or key.isdigit():
                target = self.resolve(key)
                assert target is not None, ('Missing effect target', key)
                self.run(value, target)
            elif key in ('save_event_target_as', 'save_global_event_target_as'):
                self.targets[value] = entity
            elif key == 'set_global_flag':
                self.global_flags.add(value)
            elif key == 'set_province_flag':
                entity.flags[value] = self.day
            elif key == 'clr_province_flag':
                entity.flags.pop(value, None)
            elif key in ('set_variable', 'change_variable'):
                name, amount = get(value, 'which'), float(get(value, 'value'))
                entity.variables[name] = amount + (entity.variables.get(name, 0) if key == 'change_variable' else 0)
            elif key == 'add_province_modifier':
                assert entity.kind == 'province'
                entity.modifiers.add(get(value, 'name'))
            elif key == 'remove_province_modifier':
                assert entity.kind == 'province'
                entity.modifiers.discard(value)
            elif key == 'country_event':
                assert entity.kind == 'country'
                event_id = get(value, 'id')
                assert event_id in ARRIVALS and len(value) == 1
                # A child event receives its own ROOT and a snapshot of the local targets.
                report = Script(self.countries, entity)
                report.targets = self.targets.copy()
                assert report.test(get(ARRIVALS[event_id], 'trigger'), entity), ('Premature or misdirected arrival', event_id)
                self.dispatched.append((event_id, entity, report.targets))
            elif key in UNIT_PRICE:
                expected = 'province' if key in PROVINCE_EFFECTS else 'country'
                assert entity.kind == expected, (key, entity.kind, expected)
                self.applied.append((key, entity.key, value))
            else:
                raise AssertionError(('Unsupported effect in test interpreter', key, value))


PROVINCE_EFFECTS = {'add_base_tax', 'add_base_production', 'add_base_manpower', 'add_devastation', 'spawn_rebels'}
# Units per one Weighing Value, from Jeff's guide. Losses use symmetric pricing.
UNIT_PRICE = {'add_adm_power': 50, 'add_dip_power': 50, 'add_mil_power': 50,
              'add_years_of_income': .5, 'add_yearly_manpower': 1,
              'change_innovativeness': 1, 'add_army_professionalism': .02,
              'add_base_tax': 2, 'add_base_production': 2, 'add_base_manpower': 2,
              'add_prestige': 25, 'add_prestige_or_monarch_power': 25,
              'add_devastation': -25, 'spawn_rebels': -.5}
INTEGER_EFFECTS = {'add_adm_power', 'add_dip_power', 'add_mil_power', 'change_innovativeness',
                   'add_base_tax', 'add_base_production', 'add_base_manpower', 'add_devastation'}


def amount(key, value):
    if key == 'add_prestige_or_monarch_power':
        return float(get(value, 'amount'))
    if key == 'spawn_rebels':
        assert get(value, 'type') == 'particularist_rebels'
        return float(get(value, 'size'))
    return float(value)


def world(neighbors=2):
    countries = [Entity(k, 'country') for k in ('A', 'B', 'C', 'D')]
    for i, country in enumerate(countries):
        for number in (1 + 2 * i, 2 + 2 * i):
            province = Entity(str(number), 'province', owner=country, attrs={'trade_goods': 'grain'})
            country.provinces.append(province)
    countries[0].neighbors = countries[1:1 + neighbors]
    state = Script(countries, countries[0])
    origin = countries[0].provinces[0]
    origin.modifiers.add('war_adventurer_bugman')
    state.targets['war_adventurer_location_bugman'] = origin
    return state, origin


def move(state, origin, beer='yes'):
    call = [('war_adventurer_move', [('MODIFIER', 'war_adventurer_bugman'),
                                   ('LOCATION', 'war_adventurer_location_bugman'), ('BEER', beer),
                                   ('ARRIVAL_EVENT', 'war_adventurer_bugman.21')])]
    sent_before = len(state.dispatched)
    state.run(call, origin)
    locations = [p for c in state.countries for p in c.provinces if 'war_adventurer_bugman' in p.modifiers]
    assert len(locations) == 1
    assert state.targets['war_adventurer_location_bugman'] is locations[0]
    assert len(state.dispatched) == sent_before + (locations[0] is not origin)
    if locations[0] is not origin:
        event_id, recipient, targets = state.dispatched[-1]
        assert event_id == 'war_adventurer_bugman.21'
        assert recipient is locations[0].owner
        assert targets['war_adventurer_arrival_province'] is locations[0]
        assert not state.test(TRIGGERS['war_adventurer_ready'], locations[0])
        state.day += 364
        assert not state.test(TRIGGERS['war_adventurer_ready'], locations[0])
        state.day += 1
        assert state.test(TRIGGERS['war_adventurer_ready'], locations[0])
    return locations[0]


def movement_tests():
    cases = []
    for count in (0, 1, 2, 3):
        state, origin = world(count)
        move(state, origin)
        countries = next(pool for scope, pool in state.pools if scope.endswith('_country'))
        assert set(countries) == ({'B', 'C', 'D'} if count < 2 or count == 3 else {'B', 'C'})
        cases.append(f'{count} neighbours: correct country pool')
    state, origin = world(2)
    # All neighbouring provinces occupied by other adventurers: worldwide fallback.
    for country in state.countries[1:3]:
        for province in country.provinces:
            province.modifiers.add('war_adventurer_gelt')
    assert move(state, origin).owner.key == 'D'
    cases.append('blocked neighbours use worldwide fallback')
    state, origin = world(2)
    state.countries[1].provinces[1].attrs['trade_goods'] = 'beer'
    assert move(state, origin).key == '4'
    assert state.pools[0][1] == ['B', 'C']
    cases.append('Bugman prefers beer after selecting the country')
    state, origin = world(2)
    state.countries[1].provinces[1].attrs['trade_goods'] = 'beer'
    state.countries[1].provinces[1].modifiers.add('war_adventurer_gelt')
    assert move(state, origin).key == '3'
    cases.append('occupied beer province falls back to another eligible province')
    state, origin = world(2)
    state.countries[1].provinces[1].attrs['trade_goods'] = 'beer'
    assert move(state, origin, beer='no').key == '3'
    assert state.pools[-1][1] == ['3', '4']
    cases.append('other adventurers do not prefer beer')
    state, origin = world(2)
    island = state.countries[1].provinces[0]
    island.key = '484'
    island.attrs['trade_goods'] = 'beer'
    assert move(state, origin).key == '4'
    cases.append('offshore beer province is ineligible')
    state, origin = world(2)
    state.countries[1].provinces[0].attrs['city'] = False
    assert move(state, origin).key == '4'
    cases.append('unsettled province is ineligible')
    state, origin = world(2)
    state.countries[0].provinces.remove(origin)
    state.countries[3].provinces.append(origin)
    origin.owner = state.countries[3]
    origin.owner.neighbors = state.countries[1:3]
    assert move(state, origin).owner.key in ('B', 'C')
    assert state.targets['war_adventurer_origin_country'].key == 'D'
    cases.append('ownership change while event is open uses the new owner')
    state, origin = world(2)
    origin.owner = None
    assert move(state, origin) is not origin
    cases.append('disappearing origin owner retains and relocates the traveller')
    state, origin = world(2)
    for country in state.countries[1:]:
        for province in country.provinces:
            province.modifiers.add('war_adventurer_gelt')
    assert move(state, origin) is origin
    cases.append('no world destination preserves the origin and unique global target')
    cases.append('failed movement sends no arrival notice')
    state, origin = world(2)
    # Distinct country selection is unaffected by how many provinces it has.
    state.countries[1].provinces.extend(Entity(str(i), 'province', owner=state.countries[1]) for i in range(20, 35))
    move(state, origin)
    assert state.pools[0] == ('random_neighbor_country', ['B', 'C'])
    assert len(state.pools[1][1]) == 17
    cases.append('country chosen before province, without province-count country weighting')
    state, origin = world(2)
    origin.flags['war_adventurer_event_open'] = state.day
    assert not state.test(TRIGGERS['war_adventurer_ready'], origin)
    state.day += 365
    assert state.test(TRIGGERS['war_adventurer_ready'], origin)
    cases.append('stale pending-event lock recovers after one year')
    state, origin = world(2)
    first_destination = move(state, origin)
    first_report = state.dispatched[0]
    second_destination = move(state, first_destination)
    assert second_destination is not first_destination
    assert len(state.dispatched) == 2
    assert first_report[2]['war_adventurer_arrival_province'] is first_destination
    assert state.dispatched[1][2]['war_adventurer_arrival_province'] is second_destination
    cases.append('successive arrival notices retain their own destination province')
    cases.append('successful moves send exactly one notice to the actual destination owner')
    state, origin = world(2)
    state.choices = [1]  # Choose C, proving resolution does not reroll to default-first B.
    state.run([('war_adventurer_prepare_destination', 'yes')], origin)
    announced_country = state.targets['war_adventurer_destination_country']
    assert announced_country.key == 'C'
    assert 'war_adventurer_bugman' in origin.modifiers and not state.dispatched
    assert move(state, origin).owner is announced_country
    assert sum(scope.endswith('_country') for scope, _ in state.pools) == 1
    cases.append('displayed destination country is selected on opening and retained on resolution')
    state, origin = world(2)
    state.run([('war_adventurer_prepare_destination', 'yes')], origin)
    announced_country = state.targets['war_adventurer_destination_country']
    announced_country.provinces[0].modifiers.add('war_adventurer_gelt')
    announced_country.provinces[1].attrs['trade_goods'] = 'beer'
    assert move(state, origin) is announced_country.provinces[1]
    cases.append('province selection waits for resolution and preserves Bugman beer preference')
    state, origin = world(2)
    state.run([('war_adventurer_prepare_destination', 'yes')], origin)
    for p in state.targets['war_adventurer_destination_country'].provinces:
        p.modifiers.add('war_adventurer_gelt')
    assert move(state, origin).owner.key == 'C'
    cases.append('a destination blocked while the event is open is replaced safely')
    state, origin = world(2)
    state.run([('war_adventurer_prepare_destination', 'yes')], origin)
    for c in state.countries[1:]:
        for p in c.provinces:
            p.modifiers.add('war_adventurer_gelt')
    assert move(state, origin) is origin and not state.dispatched
    cases.append('all destinations lost after opening preserves the visitor without an arrival notice')
    state, origin = world(2)
    state.run([('war_adventurer_prepare_destination', 'yes')], origin)
    assert state.targets['war_adventurer_destination_country'].key == 'B'
    state.countries[0].provinces.remove(origin)
    state.countries[1].provinces.append(origin)
    origin.owner = state.countries[1]
    assert move(state, origin).owner is not origin.owner
    cases.append('ownership change to the announced destination forces a new country')
    state, origin = world(2)
    state.run([('war_adventurer_prepare_destination', 'yes')], origin)
    assert state.targets['war_adventurer_destination_country'].key == 'B'
    origin.owner.neighbors = state.countries[2:]
    assert move(state, origin).owner.key in ('C', 'D')
    cases.append('changed borders replace an announced country that is no longer a valid neighbor')
    return cases


def main():
    event_nodes = {}
    for char in DATA['characters']:
        path = f'events/War_Adventurer_{char["slug"]}.txt'
        text = (ROOT / path).read_text()
        nodes = all_values(parse(text), 'country_event')
        assert len(nodes) == 21
        for node in nodes:
            event_id = get(node, 'id')
            assert event_id not in event_nodes and event_id not in ARRIVALS
            if event_id == 'war_adventurer_' + char['slug'] + '.21':
                ARRIVALS[event_id] = node
            else:
                event_nodes[event_id] = node
        assert 'mean_time_to_happen' not in dict(walk(parse(text)))
        assert len(re.findall(r'# [A-Z]{3}-(?:FH|FA|EH|EA)\d\d:.*\ncountry_event', text)) == 20
    assert len(event_nodes) == len(DATA['events']) == 360
    assert len(ARRIVALS) == 18
    all_mod_event_ids = Counter()
    for p in (ROOT / 'events').glob('*.txt'):
        # Only scan id assignments outside comments; avoid parsing unrelated mod files.
        clean = re.sub(r'#[^\n]*', '', p.read_text(errors='replace'))
        all_mod_event_ids.update(re.findall(r'\bid\s*=\s*(war_adventurer_\w+\.\d+)', clean))
    assert all(all_mod_event_ids[k] == 1 for k in (event_nodes | ARRIVALS))

    loc_path = ROOT / 'localisation/war_adventurers_l_english.yml'
    assert loc_path.read_bytes().startswith(b'\xef\xbb\xbf')
    loc = {}
    for line in loc_path.read_text(encoding='utf-8-sig').splitlines()[1:]:
        match = re.fullmatch(r' ([\w.]+):0 "([^"\r\n]*)"', line)
        assert match, ('Malformed localisation', line[:100])
        key, value = match.groups()
        assert key not in loc, key
        loc[key] = value
    assert len({e['description'] for e in DATA['events']}) == 360
    assert len({e['title'] for e in DATA['events']}) == 360
    assert loc['war_adventurer_leaves_tt'] == 'The Adventurer departs for [war_adventurer_destination_country.GetName].'
    assert loc['war_adventurer_stays_tt'] == 'The Adventurer remains here.'
    options_count = 0
    for e in DATA['events']:
        char = next(c for c in DATA['characters'] if c['code'] == e['code'])
        namespace = 'war_adventurer_' + char['slug']
        event_id = namespace + '.' + str(e['number'])
        node = event_nodes[event_id]
        assert get(node, 'is_triggered_only') == 'yes'
        assert get(node, 'goto') == 'war_adventurer_province'
        assert get(node, 'picture') == f'WAR_ADVENTURER_{char["code"]}_eventPicture'
        province_trigger = get(get(node, 'trigger'), 'event_target:war_adventurer_location_' + char['slug'])
        assert get(province_trigger, 'owned_by') == 'ROOT'
        assert get(province_trigger, 'has_province_modifier') == namespace
        assert get(province_trigger, namespace + '_home') == ('yes' if e['category'].endswith('H') else 'no')
        relationship = next(v for k, v in walk(province_trigger) if k == 'war_adventurer_enemy_' + char['profile'])
        assert relationship == ('yes' if e['category'].startswith('E') else 'no')
        assert get(province_trigger, 'war_adventurer_ready') == 'yes'
        assert any(k == 'any_country' for k, _ in walk(province_trigger))
        # Destination bookkeeping must not print scope headers or variable changes in the report.
        assert [k for k, _ in get(node, 'immediate')] == ['hidden_effect']
        assert any(k == 'save_event_target_as' and v == 'war_adventurer_province' for k, v in walk(get(node, 'immediate')))
        assert any(k == 'war_adventurer_prepare_destination' and v == 'yes' for k, v in walk(get(node, 'immediate')))
        movement = [v for k, v in walk(get(node, 'after')) if k == 'war_adventurer_move']
        assert len(movement) == 1
        assert dict(movement[0]) == {'MODIFIER': namespace,
                                     'LOCATION': 'war_adventurer_location_' + char['slug'],
                                     'BEER': 'yes' if char['code'] == 'BUG' else 'no',
                                     'ARRIVAL_EVENT': namespace + '.21'}
        description = loc[get(node, 'desc')].replace('\\n\\n', '\n\n')
        assert description == e['description'].replace('"', "'")
        assert char['event_introduction'] in re.split(r'(?<=[.!?])\s+', description)[0]
        assert loc[get(node, 'title')] == e['title'].replace('"', "'")
        paragraphs = description.split('\n\n')
        counts = [len(re.split(r'(?<=[.!?])\s+', p)) for p in paragraphs]
        assert len(counts) in (2, 3) and all(2 <= n <= 4 for n in counts) and 6 <= sum(counts) <= 10
        assert '[war_adventurer_province.GetName]' in description
        assert not re.search(r'early echo|2502|does not assume|no evidence places', description)
        options = all_values(node, 'option')
        assert len(options) == len(e['options']) and 2 <= len(options) <= 4
        options_count += len(options)
        for option, authored in zip(options, e['options']):
            assert loc[get(option, 'name')] == authored['label'].replace('"', "'")
            assert {v for k, v in walk(option) if k == 'custom_tooltip'} == {'war_adventurer_leaves_tt', 'war_adventurer_stays_tt'}
            actual = [(k, amount(k, v)) for k, v in walk(option) if k in UNIT_PRICE]
            expected = [(f['key'], float(f['value'])) for f in authored['effects']]
            assert actual == expected, (e['concept_id'], actual, expected)
            weight = sum(v / UNIT_PRICE[k] for k, v in actual)
            assert abs(weight - authored['weight']) < 1e-6
            assert abs(weight - e['weight']) <= 1.000001
            assert all(v.is_integer() for k, v in actual if k in INTEGER_EFFECTS)
            state, province = world()
            province.modifiers = {namespace}
            state.targets['war_adventurer_location_' + char['slug']] = province
            state.run(get(node, 'immediate'), state.root)
            assert state.targets['war_adventurer_province'] is province
            announced_country = state.targets['war_adventurer_destination_country']
            assert announced_country is not state.root
            assert namespace in province.modifiers and not state.dispatched
            state.run(option, state.root)
            assert len(state.applied) == len(expected)
            assert all(target == ('1' if k in PROVINCE_EFFECTS else 'A') for k, target, _ in state.applied)
            state.run(get(node, 'after'), state.root)
            destination = state.targets['war_adventurer_location_' + char['slug']]
            assert destination is not province and destination.owner is not state.root
            assert destination.owner is announced_country
            assert namespace not in province.modifiers and namespace in destination.modifiers
            assert 'war_adventurer_event_open' not in province.flags
            assert len(state.dispatched) == 1
            notice_id, recipient, targets = state.dispatched[0]
            assert notice_id == namespace + '.21' and recipient is destination.owner
            assert targets['war_adventurer_arrival_province'] is destination

    # Arrival notices are brief reports, with one acknowledgement and no mechanical effects.
    for char in DATA['characters']:
        namespace = 'war_adventurer_' + char['slug']
        event_id = namespace + '.21'
        node = ARRIVALS[event_id]
        assert set(dict(node)) == {'id', 'title', 'desc', 'picture', 'is_triggered_only', 'trigger', 'option'}
        assert get(node, 'is_triggered_only') == 'yes'
        assert get(node, 'picture') == f'WAR_ADVENTURER_{char["code"]}_eventPicture'
        assert get(node, 'trigger') == [('event_target:war_adventurer_arrival_province',
                                      [('owned_by', 'ROOT'), ('has_province_modifier', namespace)])]
        assert all_values(node, 'option') == [[('name', 'war_adventurer_arrival_acknowledge')]]
        assert loc['war_adventurer_arrival_acknowledge'] == 'Noted.'
        title = loc[get(node, 'title')]
        verb = 'have' if char['code'] in ('GOF', 'THA') else 'has'
        assert title == char['name'] + ' ' + verb + ' arrived in [war_adventurer_arrival_province.GetName]'
        description = loc[get(node, 'desc')].replace('\\n\\n', '\n\n')
        assert description == char['arrival_description'].replace('"', "'")
        assert char['event_introduction'] in re.split(r'(?<=[.!?])\s+', description)[0]
        assert '[war_adventurer_arrival_province.GetName]' in description
        counts = [len(re.split(r'(?<=[.!?])\s+', p)) for p in description.split('\n\n')]
        assert counts == [2, 2], (event_id, counts)

    actions = read('common/on_actions/00_on_actions.txt')
    pulse = get(get(actions, 'on_bi_yearly_pulse_5'), 'random_events')
    registered = [(k, v) for k, v in pulse if isinstance(v, str) and v.startswith('war_adventurer_')]
    assert len(registered) == 360 and {v for _, v in registered} == set(event_nodes)
    assert not {v for _, v in registered} & set(ARRIVALS)
    assert all(k == '400' for k, _ in registered)
    assert ('2000', '0') in pulse
    for action, body in actions:
        if action != 'on_bi_yearly_pulse_5':
            assert not any(isinstance(v, str) and v.startswith('war_adventurer_') for _, v in walk(body))
    startup = get(read('common/on_actions/war_startup_on_actions.txt'), 'on_startup')
    assert get(startup, 'events').count('war_adventurer_setup.1') == 1

    registry = get(read('interface/war_eventpictures.gfx'), 'spriteTypes')
    sprites = {get(b, 'name'): get(b, 'texturefile') for b in all_values(registry, 'spriteType')}
    art_sources = json.loads((HERE / 'art_sources.json').read_text())
    assert len(art_sources) == 18
    for char in DATA['characters']:
        name = f'WAR_ADVENTURER_{char["code"]}_eventPicture'
        assert sum(get(b, 'name') == name for b in all_values(registry, 'spriteType')) == 1
        path = ROOT / sprites[name]
        header = path.read_bytes()[:128]
        assert header[:4] == b'DDS ' and struct.unpack_from('<II', header, 12) == (132, 512)
        assert header[84:88] == b'DXT1'
        assert art_sources[char['code']]['asset'] == sprites[name]
        assert art_sources[char['code']]['dimensions'] == [512, 132]
    modifiers = dict(read('common/event_modifiers/war_adventurer_modifiers.txt'))
    assert len(modifiers) == 18
    icon = ROOT / 'gfx/interface/ideas_EU4/war_adventurer_icon.dds'
    icon_header = icon.read_bytes()[:128]
    assert icon_header[:4] == b'DDS ' and struct.unpack_from('<II', icon_header, 12) == (64, 64)
    assert icon_header[84:88] == b'DXT5'  # Alpha-preserving shared province modifier icon.
    for char in DATA['characters']:
        modifier = modifiers['war_adventurer_' + char['slug']]
        expected_modifier = {char['bonus']: '0.05', 'province_trade_power_modifier': '0.1',
                             'local_unrest': '2', 'picture': 'war_adventurer_icon'}
        assert len(modifier) == len(expected_modifier)  # No repeated trade-power key for Thanquol.
        assert dict(modifier) == expected_modifier
        assert loc['war_adventurer_' + char['slug']] == char.get('modifier_name', char['name'] + ', Adventurer')
        assert loc['desc_war_adventurer_' + char['slug']] == char['modifier_description']

    # Every geographical name resolves to an actual map definition.
    geography = {kind: dict(read(f'map/{kind}.txt')) for kind in ('area', 'region', 'superregion')}
    for key, value in walk(list(TRIGGERS.items())):
        if key in geography:
            assert value in geography[key], (key, value)
    assert GROUPS['war_adventurer_mainlands'] == ELIGIBLE
    for source, digest in json.loads((HERE / 'map_eligibility.json').read_text())['source_sha256'].items():
        assert hashlib.sha256((ROOT / source).read_bytes()).hexdigest() == digest, ('Map changed; rebuild mainland eligibility', source)
    assert not (ELIGIBLE & {484, 1828})
    assert {284, 1829, 4776} <= ELIGIBLE
    starts = [c['start'] for c in DATA['characters']]
    assert len(set(starts)) == 18 and set(starts) <= ELIGIBLE
    start_tags = []
    for number in starts:
        files = [p for p in (ROOT / 'history/provinces').glob(str(number) + '*.txt')
                 if re.match(r'^' + str(number) + r'(?:\D|$)', p.name)]
        assert len(files) == 1, (number, files)
        try:
            history_text = files[0].read_text(encoding='utf-8-sig')
        except UnicodeDecodeError:
            history_text = files[0].read_text(encoding='cp1252')
        history = parse(history_text)
        owner = get(history, 'owner')
        assert owner
        start_tags.append(owner)
    assert len(set(start_tags)) == 18, start_tags

    # Hostility is exhaustively checked against independent truth tables.
    flags = ['order_nation', 'neutral_nation', 'destruction_nation', 'chaos_nation',
             'orcish_administration', 'skaven_administration', 'undead_administration']
    for bits in itertools.product((False, True), repeat=7):
        good, neutral, evil, chaos, orc, skaven, undead = bits
        c = Entity('X', 'country', modifiers={f for f, bit in zip(flags, bits) if bit})
        state = Script([c], c)
        expected = {'a': chaos or evil or orc or skaven or undead,
                    'b': not skaven, 'c': good or undead,
                    'd': chaos or orc or skaven or (evil and not undead)}
        for profile, result in expected.items():
            assert state.test(TRIGGERS['war_adventurer_enemy_' + profile], c) == result
    for profile in 'abcd':
        assert all(k in ('OR', 'AND', 'NOT', 'has_country_modifier') for k, _ in walk(TRIGGERS['war_adventurer_enemy_' + profile]))

    # Each character retains all five incidents in every relationship/geography pool.
    assert set(Counter((e['code'], e['category']) for e in DATA['events']).values()) == {5}
    document = (ROOT / 'Dev Stuff/Adventurer Province Modifier Design.md').read_text()
    covered = set()
    for char in DATA['characters']:
        section = document.split('<a id="catalogue-' + char['code'].lower() + '"></a>')[1]
        section = section.split('<a id="catalogue-', 1)[0]
        anchors = set(re.findall(r'\| \*\*(L\d+)\*\*', section))
        assert anchors, char
        refs = {ref for e in DATA['events'] if e['code'] == char['code'] for ref in re.findall(r'L\d+', e['lore'])}
        assert anchors <= refs, (char['code'], anchors - refs)
        covered.update((char['code'], a) for a in anchors)
    assert len(covered) == 68

    cases = movement_tests()
    # Initialization is idempotent even if multiple queued startup events run.
    countries = [Entity(t, 'country') for t in start_tags]
    for c, number in zip(countries, starts):
        c.provinces.append(Entity(str(number), 'province', owner=c))
    setup = all_values(read('events/War_Adventurer_Setup.txt'), 'country_event')[0]
    state = Script(countries, countries[0])
    state.run(get(setup, 'immediate'), state.root)
    snapshot = [(p.key, sorted(p.modifiers)) for c in countries for p in c.provinces]
    state.run(get(setup, 'immediate'), state.root)
    assert snapshot == [(p.key, sorted(p.modifiers)) for c in countries for p in c.provinces]
    assert len(state.targets) == 18
    assert not state.dispatched
    for char, country in zip(DATA['characters'], countries):
        province = country.provinces[0]
        assert province.modifiers == {'war_adventurer_' + char['slug']}
        assert state.targets['war_adventurer_location_' + char['slug']] is province
    cases.append('startup initializes eighteen unique locations and is idempotent')
    # An older save can have an unowned preferred start. Seed an eligible owned replacement.
    countries = [Entity(t, 'country') for t in start_tags]
    for c, number in zip(countries, starts):
        c.provinces.append(Entity(str(number), 'province', owner=c))
    countries[0].provinces.extend([Entity('2', 'province', owner=countries[0], attrs={'trade_goods': 'grain'}),
                                   Entity('3', 'province', owner=countries[0], attrs={'trade_goods': 'beer'})])
    state = Script(countries, countries[0])
    bugman_start = countries[3].provinces.pop()
    bugman_start.owner = None
    state.run(get(setup, 'immediate'), state.root)
    assert state.targets['war_adventurer_location_bugman'].key == '3'
    assert all(len(p.modifiers) <= 1 for c in countries for p in c.provinces)
    assert len({state.targets['war_adventurer_location_' + c['slug']].key for c in DATA['characters']}) == 18
    assert not state.dispatched
    cases.append('unowned older-save start relocates without stacking and respects Bugman’s beer preference')
    cases.append('initial placement does not send movement notices')
    result = {'status': 'passed', 'events': len(event_nodes), 'options': options_count,
              'arrival_notices': len(ARRIVALS), 'arrival_options_without_effects': len(ARRIVALS),
              'portraits': 18, 'shared_modifier_icons': 1, 'modifier_trade_power': 0.1,
              'lore_anchors': len(covered), 'unique_starting_countries': len(set(start_tags)),
              'enemy_truth_table_cases': 512, 'mainland_provinces': len(ELIGIBLE),
              'full_option_and_departure_executions': options_count,
              'paragraph_counts': dict(Counter(e['description_paragraphs'] for e in DATA['events'])),
              'sentence_counts': dict(Counter(e['description_sentences'] for e in DATA['events'])),
              'movement_and_startup_tests': cases,
              'limitations': 'Static checks and a restricted script interpreter; no live EU4 execution.'}
    (HERE / 'validation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
