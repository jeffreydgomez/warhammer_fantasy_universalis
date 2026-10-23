#!/usr/bin/env python3
"""Static references and script-driven scenarios; not a substitute for EU4 playtesting."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]


def parse(path):
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|#[^\n]*|[{}=]|[^\s{}=#"]+',
                        path.read_text(encoding='utf-8-sig'))
    tokens = iter(t for t in tokens if not t.startswith('#'))

    def block(nested=False):
        result = []
        for key in tokens:
            if key == '}':
                assert nested, f'{path}: extra closing brace'
                return result
            assert next(tokens) == '=', (path, key)
            value = next(tokens)
            result.append((key, block(True) if value == '{' else value.strip('"')))
        assert not nested, f'{path}: missing closing brace'
        return result
    return block()


def read(path):
    return parse(ROOT / path)


def get(block, key, default=None):
    matches = [v for k, v in block if k == key]
    assert len(matches) <= 1, ('Duplicate key', key)
    return matches[0] if matches else default


def walk(block):
    for k, v in block:
        yield k, v
        if isinstance(v, list):
            yield from walk(v)


PROJECT = get(read('common/great_projects/01_old_world_monuments.txt'), 'war_warpmoon_project')
TRIGGERS = dict(read('common/scripted_triggers/war_warpmoon_triggers.txt'))
EFFECTS = dict(read('common/scripted_effects/war_warpmoon_effects.txt'))
MODIFIERS = dict(read('common/event_modifiers/war_warpmoon_modifiers.txt'))
DECISION = get(get(read('decisions/war_warpmoon_decisions.txt'), 'country_decisions'),
               'war_destroy_warpmoon_project')
EVENTS = dict((get(v, 'id'), v) for k, v in read('events/War_Warpmoon_Events.txt')
              if k == 'country_event')


class World:
    def __init__(self):
        self.flags, self.targets, self.events, self.ae, self.rolls = set(), {}, [], [], []
        self.countries = [dict(name=n, modifiers=set(), tech=12, production=20,
                               prestige=0, gold=0) for n in ('builder', 'rival', 'occupier', 'ally')]
        self.countries[0]['modifiers'].add('skaven_administration')
        self.countries[1]['modifiers'].add('skaven_administration')
        # Eligible examples include foreign, builder-owned, uncolonized and cavern land.
        self.provinces = [dict(name=str(i), terrain=t, owner=self.countries[i % 4],
                               controller=self.countries[i % 4], tier=None, sea=False,
                               wasteland=False, devastation=0, goods='grain', modifiers={})
                          for i, t in enumerate(('great_maze', 'plains', 'forest', 'cavern',
                                                'underway', 'dwarf_karak', 'warren_city',
                                                'plains', 'ocean', 'impassable'))]
        self.provinces[0]['tier'] = 1
        self.provinces[7]['owner'] = self.provinces[7]['controller'] = None
        self.provinces[8]['sea'] = True
        self.provinces[9]['wasteland'] = True

    def resolve(self, value, root):
        return self.targets[value.split(':', 1)[1]] if value.startswith('event_target:') else root

    def condition(self, block, scope, root):
        def check(k, v):
            if k in TRIGGERS:
                return self.condition(TRIGGERS[k], scope, root) == (v == 'yes')
            if k == 'OR':
                return any(self.condition([item], scope, root) for item in v)
            if k == 'NOT':
                return not self.condition(v, scope, root)
            if k == 'custom_trigger_tooltip':
                return self.condition([(a, b) for a, b in v if a != 'tooltip'], scope, root)
            if k == 'owner':
                return scope['owner'] is not None and self.condition(v, scope['owner'], root)
            if k == '4600':
                return self.condition(v, self.provinces[0], root)
            if k == 'province_id':
                assert v == '4600'
                return scope is self.provinces[0]
            if k == 'any_province':
                return any(self.condition(v, p, root) for p in self.provinces)
            if k == 'has_global_flag':
                return v in self.flags
            if k == 'has_country_modifier':
                return v in scope['modifiers']
            if k == 'mil_tech':
                return scope['tech'] >= int(v)
            if k == 'trade_goods_produced_amount':
                assert get(v, 'trade_goods') == 'warpstone'
                return scope['production'] >= float(get(v, 'amount'))
            if k == 'has_great_project':
                assert get(v, 'type') == 'war_warpmoon_project'
                return scope['tier'] == int(get(v, 'tier'))
            if k == 'controlled_by':
                return scope['controller'] is self.resolve(v, root)
            if k == 'tag':
                return scope is self.resolve(v, root)
            if k == 'has_terrain':
                return scope['terrain'] == v
            if k in ('is_sea', 'is_wasteland'):
                return scope[k[3:]] == (v == 'yes')
            raise AssertionError(('Unhandled trigger', k))
        return all(check(k, v) for k, v in block)

    def effect(self, block, scope, root, hit=True):
        branch = False
        for k, v in block:
            if k in ('if', 'else_if'):
                if k == 'if':
                    branch = False
                if not branch and self.condition(get(v, 'limit'), scope, root):
                    self.effect([(a, b) for a, b in v if a != 'limit'], scope, root, hit)
                    branch = True
            elif k in EFFECTS:
                self.effect(EFFECTS[k], scope, root, hit)
            elif k == '4600':
                self.effect(v, self.provinces[0], root, hit)
            elif k == 'hidden_effect':
                self.effect(v, scope, root, hit)
            elif k == 'custom_tooltip':
                pass
            elif k == 'save_event_target_as':
                self.targets[v] = scope
            elif k == 'set_global_flag':
                self.flags.add(v)
            elif k == 'owner':
                self.effect(v, scope['owner'], root, hit)
            elif k in ('every_country', 'every_province', 'random_province'):
                candidates = self.countries if k == 'every_country' else self.provinces
                candidates = [c for c in candidates if self.condition(get(v, 'limit', []), c, root)]
                if k == 'random_province':
                    candidates = candidates[:1]
                for c in candidates:
                    self.effect([(a, b) for a, b in v if a != 'limit'], c, root, hit)
            elif k == 'random':
                assert get(v, 'chance') == '15'
                self.rolls.append(scope['name'])
                if hit:
                    self.effect([(a, b) for a, b in v if a != 'chance'], scope, root, hit)
            elif k == 'add_great_project_tier':
                scope['tier'] += int(get(v, 'tier'))
            elif k == 'destroy_great_project':
                scope['tier'] = None
            elif k == 'add_devastation':
                scope['devastation'] = min(100, scope['devastation'] + int(v))
            elif k == 'change_trade_goods':
                scope['goods'] = v
            elif k == 'add_province_modifier':
                scope['modifiers'][get(v, 'name')] = int(get(v, 'duration'))
            elif k == 'add_country_modifier':
                assert get(v, 'duration') == '-1'
                scope['modifiers'].add(get(v, 'name'))
            elif k == 'add_aggressive_expansion':
                assert get(v, 'apply_calc') == 'no'
                self.ae.append((scope['name'], self.resolve(get(v, 'who'), root)['name'],
                                int(get(v, 'value'))))
            elif k == 'country_event':
                self.events.append((scope['name'], get(v, 'id'), self.targets.copy()))
            elif k in ('add_prestige', 'add_treasury'):
                scope['prestige' if k == 'add_prestige' else 'gold'] += int(v)
            else:
                raise AssertionError(('Unhandled effect', k))


def validate():
    assert get(PROJECT, 'start') == '4600' and (ROOT / 'history/provinces/4600.txt').exists()
    assert get(PROJECT, 'starting_tier') == '0' and get(PROJECT, 'can_be_moved') == 'no'
    for i, (months, cost) in enumerate(((0, 0), (240, 2000), (480, 5000), (960, 10000))):
        tier = get(PROJECT, f'tier_{i}')
        assert get(get(tier, 'upgrade_time'), 'months') == str(months)
        assert get(get(tier, 'cost_to_upgrade'), 'factor') == str(cost)
        for k in ('province_modifiers', 'country_modifiers', 'area_modifier'):
            assert get(tier, k) == []
    assert dict(MODIFIERS['war_we_destroyed_the_moon']) == dict(
        prestige='2', legitimacy='2', devotion='2', horde_unity='2',
        republican_tradition='1', tolerance_own='2', religious_unity='0.15')
    assert dict(MODIFIERS['war_warpmoon_impact_site']) == dict(attrition='100', max_attrition='100')

    w = World()
    p, builder, occupier = w.provinces[0], w.countries[0], w.countries[2]
    for key in ('build_trigger', 'can_use_modifiers_trigger', 'can_upgrade_trigger'):
        assert w.condition(get(PROJECT, key), p, p)
        for stat, low in (('tech', 11), ('production', 19.99)):
            original = builder[stat]
            builder[stat] = low
            assert not w.condition(get(PROJECT, key), p, p)
            builder[stat] = original
        builder['modifiers'].clear()
        assert not w.condition(get(PROJECT, key), p, p)
        builder['modifiers'].add('skaven_administration')

    # Fixed site: all nations see the decision; only its current controller can use it.
    p['owner'], p['controller'] = builder, occupier
    for tier in (0, 1, 2, 3):
        p['tier'] = tier
        for country in w.countries:
            assert w.condition(get(DECISION, 'potential'), country, country) == (tier in (1, 2))
            assert w.condition(get(DECISION, 'allow'), country, country) == (
                tier in (1, 2) and country is occupier)
        highlighted = [q for q in w.provinces if w.condition(
            get(DECISION, 'provinces_to_highlight'), q, occupier)]
        assert highlighted == ([p] if tier in (1, 2) else [])
    for tier in (1, 2):
        p['tier'] = tier
        w.effect(get(DECISION, 'effect'), occupier, occupier)
        assert p['tier'] == 0 and p['owner'] is builder
    assert (occupier['prestige'], occupier['gold']) == (100, 2000)
    ai = get(DECISION, 'ai_will_do')
    assert get(ai, 'factor') == '100' and get(get(ai, 'modifier'), 'factor') == '0'
    assert get(get(ai, 'modifier'), 'has_country_modifier') == 'skaven_administration'
    # A Skaven player remains eligible if they take control.
    p['tier'], p['controller'] = 1, builder
    assert w.condition(get(DECISION, 'allow'), builder, builder)

    # Every stage warning reaches every country, with the fixed site and current owner.
    for stage in (1, 2):
        w.events.clear()
        p['owner'] = w.countries[1]
        w.effect(get(get(PROJECT, f'tier_{stage}'), 'on_upgraded'), p, p)
        assert len(w.events) == len(w.countries)
        assert all(e[1] == f'war_warpmoon.{stage}' and e[2]['war_warpmoon_province'] is p
                   and e[2]['war_warpmoon_builder'] is w.countries[1] for e in w.events)

    # Exercise both outcomes of each 15% roll; a miss changes NOTHING.
    for hit in (False, True):
        w = World()
        p = w.provinces[0]
        p['tier'] = 3
        w.provinces[1]['devastation'] = 67
        w.effect(get(get(PROJECT, 'tier_3'), 'on_upgraded'), p, p, hit)
        assert p['tier'] is None
        assert 'war_we_destroyed_the_moon' in w.countries[0]['modifiers']
        assert w.rolls == ['1', '2', '3', '7']
        for q in w.provinces:
            affected = q['name'] in w.rolls and hit
            assert q['goods'] == ('warpstone' if affected else 'grain')
            assert q['modifiers'] == ({'war_warpmoon_impact_site': 365} if affected else {})
            assert q['devastation'] == (100 if affected else (67 if q['name'] == '1' else 0))
        assert w.ae == [('occupier', 'builder', 50), ('ally', 'builder', 50)]
        assert len(w.events) == 4 and all(e[1] == 'war_warpmoon.3' for e in w.events)
        # Owner requirements remain the three stated conditions. Project
        # destruction, not a visible global-flag requirement, removes access.
        assert w.condition(get(PROJECT, 'can_upgrade_trigger'), p, p)
        assert not w.condition(get(DECISION, 'potential'), w.countries[0], w.countries[0])
        before = (len(w.events), len(w.ae), len(w.rolls))
        w.effect(EFFECTS['war_warpmoon_destroy_moon'], p, p, hit)
        assert before == (len(w.events), len(w.ae), len(w.rolls)), 'Duplicate detonation'

    # Localisation, event links, artwork, IDs and paragraph structure.
    locpath = ROOT / 'localisation/war_warpmoon_l_english.yml'
    assert locpath.read_bytes().startswith(b'\xef\xbb\xbf')
    loc = dict(re.findall(r'^\s+(\S+):0 "(.*)"$', locpath.read_text(encoding='utf-8-sig'), re.M))
    assert len(loc) == len(re.findall(r'^\s+\S+:0', locpath.read_text(encoding='utf-8-sig'), re.M))
    pictures = (ROOT / 'interface/war_eventpictures.gfx').read_text()
    for event_id, event in EVENTS.items():
        assert f'name = "{get(event, "picture")}"' in pictures
        for key in ('title', 'desc'):
            assert get(event, key) in loc
        assert get(get(event, 'option'), 'name') in loc
        paragraphs = loc[get(event, 'desc')].split(r'\n\n')
        assert 2 <= len(paragraphs) <= 3
        assert all(2 <= len(re.findall(r'[.!?](?: |$)', x)) <= 4 for x in paragraphs)
        assert get(event, 'is_triggered_only') == 'yes'
        if event_id != 'war_warpmoon.3':
            assert get(event, 'goto') == 'war_warpmoon_province'
    for path in ('common/great_projects/01_old_world_monuments.txt',
                 'common/scripted_effects/war_warpmoon_effects.txt',
                 'decisions/war_warpmoon_decisions.txt', 'events/War_Warpmoon_Events.txt'):
        for k, v in walk(PROJECT if path.startswith('common/great_projects/') else read(path)):
            if k in ('custom_tooltip', 'tooltip'):
                assert v in loc, ('Missing localisation', v)
            if k == 'country_event':
                assert get(v, 'id') in EVENTS
    sprite = get(get(read('interface/war_warpmoon_project.gfx'), 'spriteTypes'), 'spriteType')
    assert get(sprite, 'name') == 'GFX_great_project_war_warpmoon_project'
    assert (ROOT / get(sprite, 'texturefile')).exists()
    for path in (ROOT / 'events').glob('*.txt'):
        if path.name != 'War_Warpmoon_Events.txt':
            assert not re.search(r'^\s*id\s*=\s*war_warpmoon\.\d+',
                                 path.read_text(errors='replace'), re.M), path
    print('PASS: structure, references, BOM, stage costs, access gates, fixed location, occupation,')
    print('      sabotage levels, AI policy, broadcasts, terrain exclusions, impact branches,')
    print('      exact devastation, modifier durations, AE direction, and single detonation.')


if __name__ == '__main__':
    validate()
