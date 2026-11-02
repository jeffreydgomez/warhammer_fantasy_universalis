#!/usr/bin/env python3
"""Check adventurer choice budgets, province scope, building gates and pulse eligibility.

Executes the relevant trigger/effect subset against state fixtures. It is not a
live EU4 test. Uses only the standard library and does not rewrite mod files.
"""
from collections import Counter
from itertools import product
from pathlib import Path
import re
import runpy

builder = runpy.run_path(str(Path(__file__).with_name('rebalance_adventurer_events.py')))
ROOT = builder['ROOT']


def parse(text):
    result = []
    for key, body, start, end in builder['blocks'](text):
        result.append((key, parse(body) if re.match(r'[^\s=]+\s*=\s*\{', text[start:end]) else body.strip('"')))
    return result


def get(body, key, default=None):
    return next((v for k, v in body if k == key), default)


def walk(body):
    for key, value in body:
        yield key, value
        if isinstance(value, list):
            yield from walk(value)


def evaluate(body, scope, world):
    if scope is None:
        return False
    for key, value in body:
        if key == 'NOT':
            ok = not any(evaluate([term], scope, world) for term in value)
        elif key == 'OR':
            ok = any(evaluate([term], scope, world) for term in value)
        elif key == 'AND':
            ok = evaluate(value, scope, world)
        elif key.startswith('event_target:'):
            ok = evaluate(value, world['targets'].get(key.split(':', 1)[1]), world)
        elif key == 'owner':
            ok = evaluate(value, scope.get('owner'), world)
        elif key == 'owned_by':
            assert value == 'ROOT'
            ok = scope.get('owner') is world['root']
        elif key == 'has_province_modifier':
            ok = value in scope.get('modifiers', set())
        elif key == 'has_country_modifier':
            ok = value in scope.get('modifiers', set())
        elif key == 'has_country_flag':
            ok = value in scope.get('flags', set())
        elif key.startswith('war_adventurer_') and key.endswith('_home'):
            ok = scope['home'] == (value == 'yes')
        elif key.startswith('war_adventurer_enemy_'):
            ok = scope['enemy'] == (value == 'yes')
        elif key == 'war_adventurer_destination_country':
            ok = scope['destination'] == (value == 'yes')
        elif key in {'has_port', 'is_at_war'}:
            ok = scope[key] == (value == 'yes')
        elif key in {'has_winter', 'has_climate', 'trade_goods'}:
            ok = scope[key] == value
        elif key == 'has_building':
            ok = value in scope.get('buildings', set())
        else:
            raise AssertionError(('Unsupported trigger', key, value))
        if not ok:
            return False
    return True


# Independent allowed magnitudes from the guide, plus the requested building scale.
ALLOWED = {
    ('add_base_tax', '2'): (1, 'province'),
    ('add_base_production', '2'): (1, 'province'),
    ('add_base_manpower', '2'): (1, 'province'),
    ('add_local_autonomy', '50'): (-1, 'province'),
    ('add_devastation', '50'): (-1, 'province'),
    ('change_innovativeness', '1'): (1, 'country'),
    ('add_army_professionalism', '0.02'): (1, 'country'),
    ('add_years_of_income', '-0.5'): (-1, 'country'),
    ('add_prestige', '-25'): (-1, 'country'),
}


def execute(body, scope, world, changes):
    prior_branch = False
    for key, value in body:
        if key in {'name', 'ai_chance', 'trigger', 'custom_tooltip'}:
            continue
        if key == 'if':
            prior_branch = evaluate(get(value, 'limit'), scope, world)
            if prior_branch:
                execute([(k, v) for k, v in value if k != 'limit'], scope, world, changes)
        elif key == 'else':
            if not prior_branch:
                execute(value, scope, world, changes)
        elif key.startswith('event_target:'):
            target = world['targets'].get(key.split(':', 1)[1])
            if target is not None:
                execute(value, target, world, changes)
        elif key == 'set_country_flag':
            scope['flags'].add(value)
        elif key in {'add_building', 'remove_building'}:
            assert scope['kind'] == 'province'
            assert value in world['building_ids'], value
            if key == 'add_building':
                assert value not in scope['buildings'], 'Redundant building reward'
                scope['buildings'].add(value)
                weight = 1
            else:
                assert value in scope['buildings'], 'Destruction of absent building'
                scope['buildings'].remove(value)
                weight = -1
            changes.append((weight, 'province'))
        elif key == 'add_prestige_or_monarch_power':
            assert value == [('amount', '25')] and scope['kind'] == 'country'
            changes.append((1, 'country'))
        else:
            weight, kind = ALLOWED[(key, value)]
            assert scope['kind'] == kind, (key, scope['kind'])
            changes.append((weight, kind))


def fixture(slug, home=True, enemy=False, port=True, undead=False, war=False, cold=False):
    country = {'kind': 'country', 'enemy': enemy, 'flags': set(), 'is_at_war': war,
               'modifiers': {'undead_administration'} if undead else set()}
    province = {'kind': 'province', 'owner': country, 'home': home, 'has_port': port,
                'has_winter': 'severe_winter' if cold else 'mild_winter',
                'has_climate': 'arctic' if cold else 'temperate', 'trade_goods': 'grain',
                'modifiers': {f'war_adventurer_{slug}'}, 'buildings': set()}
    return {'root': country, 'province': province, 'targets': {
        f'war_adventurer_location_{slug}': province, 'war_adventurer_province': province,
        'war_adventurer_destination_country': {'destination': True}}, 'building_ids': BUILDINGS}


BUILDINGS = set(re.findall(r'^(\w+)\s*=\s*\{', (ROOT / 'common/buildings/00_buildings.txt').read_text(), re.M))


def main():
    plan = builder['parse_plan']()
    loc_bytes = (ROOT / 'localisation/war_adventurers_l_english.yml').read_bytes()
    assert loc_bytes.startswith(b'\xef\xbb\xbf')
    loc_pairs = re.findall(r'^\s*(\S+):\d+\s+"(.*)"', loc_bytes.decode('utf-8-sig'), re.M)
    loc = dict(loc_pairs)
    assert len(loc) == len(loc_pairs)
    events, arrivals = {}, {}
    totals = Counter()
    for slug in builder['ROSTER']:
        text = (ROOT / f'events/War_Adventurer_{slug}.txt').read_text()
        intended = re.findall(r'Intended event Weighing Value: ([+-]\d+)\.', text)
        assert len(intended) == 20 and set(intended) <= {'+1', '-1'}
        comments = [int(n) for n in re.findall(r'Option Weighing Value: ([+-]?\d+)\.', text)]
        option_weights = []
        for key, node in parse(text):
            if key != 'country_event':
                continue
            eid = get(node, 'id')
            number = int(eid.split('.')[-1])
            assert get(node, 'is_triggered_only') == 'yes' and get(node, 'mean_time_to_happen') is None
            if number == 21:
                arrivals[eid] = node
                assert get(node, 'goto') == 'war_adventurer_arrival_province'
                assert get(node, 'option') == [('name', 'war_adventurer_arrival_acknowledge')]
                option_weights.append(0)
                continue
            assert eid not in events
            events[eid] = node
            assert get(node, 'goto') == 'war_adventurer_province'
            province_trigger = get(get(node, 'trigger'), f'event_target:war_adventurer_location_{slug}')
            assert get(province_trigger, 'owned_by') == 'ROOT'
            assert get(province_trigger, 'has_province_modifier') == f'war_adventurer_{slug}'
            assert list(dict(get(node, 'immediate'))) == ['hidden_effect']
            moves = [v for k, v in walk(get(node, 'after')) if k == 'war_adventurer_move']
            assert len(moves) == 1 and get(moves[0], 'ARRIVAL_EVENT') == f'war_adventurer_{slug}.21'
            description = loc[get(node, 'desc')].split(r'\n\n')
            counts = [len(re.split(r'(?<=[.!?])\s+', p)) for p in description]
            assert 2 <= len(counts) <= 3 and all(2 <= c <= 4 for c in counts) and 6 <= sum(counts) <= 10
            assert 'Our officials ask whether we should ' in description[-1]
            choices = [o for k, o in node if k == 'option']
            assert 2 <= len(choices) <= 4
            assert sum(get(o, 'trigger') is None for o in choices) >= 2
            for index, choice in enumerate(choices):
                code, label = plan[f'{slug}.{number}'][1][index]
                assert loc[get(choice, 'name')] == label
                world = fixture(slug)
                if code.startswith('lose_'):
                    world['province']['buildings'].add(code.split('_', 1)[1])
                assert evaluate(get(choice, 'trigger', []), world['root'], world)
                changes = []
                execute(choice, world['root'], world, changes)
                assert len(changes) <= 1, (eid, label, 'Stacked effects')
                weight = sum(c[0] for c in changes)
                assert weight in {-1, 0, 1} and abs(weight - int(intended[number-1])) <= 1
                option_weights.append(weight)
                totals['options'] += 1
                totals[changes[0][1] if changes else 'no_effect'] += 1
                totals[f'weight_{weight}'] += 1
                if code.startswith(('build_', 'lose_')):
                    # The actual option trigger and effect guard must reject stale building state.
                    assert not evaluate(get(choice, 'trigger'), world['root'], world)
                    changes = []
                    execute(choice, world['root'], world, changes)
                    assert changes == []
                    if code == 'build_counting_house':
                        world = fixture(slug)
                        world['province']['trade_goods'] = 'gold'
                        assert not evaluate(get(choice, 'trigger'), world['root'], world)
                    totals['building_options'] += 1
        assert comments == option_weights, ('Budget comments differ from effects', slug)
    assert len(events) == 360 and len(arrivals) == 18
    pulse = parse((ROOT / 'common/scripted_effects/war_adventurer_pulse_effects.txt').read_text())
    dispatch = get(pulse, 'war_adventurer_dispatch_pulse')
    assert sum(k == 'any_country' for k, _ in walk(dispatch)) == 1
    draws = [v for k, v in walk(dispatch) if k == 'random_list']
    assert len(draws) == 1 and len(draws[0]) == 360
    entries = {}
    for weight, entry in draws[0]:
        assert weight == '1'
        eid = get(get(entry, 'country_event'), 'id')
        assert eid not in entries and eid in events
        entries[eid] = entry
        slug = eid.removeprefix('war_adventurer_').split('.')[0]
        trigger = get(entry, 'trigger')
        assert trigger[0] == ('has_country_flag', f'war_adventurer_pulse_{slug}_eligible')
        assert trigger[1:] == get(events[eid], 'trigger'), ('Pulse/event eligibility drift', eid)
    assert set(entries) == set(events)
    for slug in builder['ROSTER']:
        cache = get(pulse, 'war_adventurer_cache_pulse_candidate')
        cache = parse(builder['format_block'](next(b for k, b, _, _ in builder['blocks'](
            (ROOT / 'common/scripted_effects/war_adventurer_pulse_effects.txt').read_text())
            if k == 'war_adventurer_cache_pulse_candidate')).replace('$SLUG$', slug))
        for state in product([False, True], repeat=6):
            world = fixture(slug, *state)
            flag = f'war_adventurer_pulse_{slug}_eligible'
            # A newly arrived visitor without a snapshot flag must not enter this round.
            execute(cache, world['root'], world, [])
            assert flag not in world['root']['flags']
            world['root']['flags'].add(f'war_adventurer_pulse_{slug}_scheduled')
            execute(cache, world['root'], world, [])
            assert flag in world['root']['flags']
            eligible = 0
            for number in range(1, 21):
                eid = f'war_adventurer_{slug}.{number}'
                actual = evaluate(get(entries[eid], 'trigger'), world['root'], world)
                assert actual == evaluate(get(events[eid], 'trigger'), world['root'], world)
                eligible += actual
                totals['eligibility_cases'] += 1
            assert eligible >= 1, (slug, state, 'No eligible stories')
            world['province']['modifiers'].clear()
            assert not any(evaluate(get(entries[f'war_adventurer_{slug}.{n}'], 'trigger'), world['root'], world)
                           for n in range(1, 21))
        world = fixture(slug)
        world['root']['flags'].add(f'war_adventurer_pulse_{slug}_scheduled')
        world['province']['owner'] = {'kind': 'country'}
        execute(cache, world['root'], world, [])
        assert f'war_adventurer_pulse_{slug}_eligible' not in world['root']['flags']
        for suffix in ('scheduled', 'eligible', 'home', 'enemy'):
            assert ('clr_country_flag', f'war_adventurer_pulse_{slug}_{suffix}') in dispatch
    # A repeated build is byte-identical and never touches unrelated systems.
    for filename, content in builder['build']().items():
        assert (ROOT / filename).read_bytes() == content, ('Non-idempotent output', filename)
    print('PASS: 360 encounters, 18 effect-free arrival notices, budgets/scopes/building gates, pulse eligibility and snapshot safety.')
    print(dict(totals))
    print('Static/script-fixture checks only; no live EU4 execution.')


if __name__ == '__main__':
    main()
