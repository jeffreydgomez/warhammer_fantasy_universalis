#!/usr/bin/env python3
"""Static coverage and script-model regressions; not an EU4 engine/save-load test.

Missing event-target scopes are modeled as false, matching the intended adventurer
pattern. This assumption must also be checked in EU4, especially in decision tooltips.
"""
import copy
import itertools
from script_parser import ROOT, parse, walk, read
from validate_performance import World, MODS, baseline

DECISIONS = 'decisions/Artifact_decisions.txt'
DIPLOMACY = 'common/new_diplomatic_actions/00_war_artifacts.txt'
NAGASH = 'war_artifact_nagash_holder'


def target(modifier):
    return 'war_artifact_location_' + modifier.removeprefix('location_of_').removeprefix('the_')


def normalize(nodes, strip_tracking=False):
    return [(n.k, normalize(n.v, strip_tracking) if isinstance(n.v, list) else n.v)
            for n in nodes if not (strip_tracking and n.k in
            ('save_global_event_target_as', 'clear_global_event_target') and
            n.v.startswith('war_artifact_'))]


class ArtifactWorld(World):
    def __init__(self):
        super().__init__()
        self.ai = False
        self.enemy = False
        self.neighbor = False
        self.skaven = True

    def scoped(self, key, scope):
        if key.startswith('event_target:'):
            return self.targets.get(key[13:])
        return super().scoped(key, scope)

    def pool(self, key, scope):
        if key == 'any_neighbor_country':
            return [('c', 'from')] if self.neighbor else []
        if key == 'any_war_enemy_country':
            return [('c', 'from')] if self.enemy else []
        return super().pool(key, scope)

    def test(self, nodes, scope=('c', 'root')):
        # Delegate compound conditions to the shared interpreter; fail on unknown syntax.
        for n in nodes:
            if n.k == 'ai':
                result = self.ai == (n.v == 'yes')
            elif n.k == 'is_at_war':
                result = self.enemy == (n.v == 'yes')
            elif n.k == 'technology_group':
                assert n.v == 'tech_skaven'
                result = self.skaven
            else:
                result = super().test([n], scope)
            if not result:
                return False
        return True

    def bind(self, modifier, province):
        for p in self.provinces.values():
            p['mods'].discard(modifier)
        if province is None:
            self.targets.pop(target(modifier), None)
        else:
            self.provinces[province]['mods'].add(modifier)
            self.targets[target(modifier)] = ('p', province)


def validate():
    decisions = parse(read(DECISIONS))[0]
    original = parse(baseline(DECISIONS))[0]
    takes = [d for d in decisions.v if d.k.startswith('take_')]
    assert len(takes) == len(MODS) == 24
    # Ownership/neighbor visibility and all other gameplay remain the restored version.
    for d in decisions.v:
        old = original.get(d.k)
        changed_allow = d.k.startswith('take_') or d.k == 'destroy_nagash'
        current_nodes = [n for n in d.v if not (changed_allow and n.k == 'allow')]
        old_nodes = [n for n in old.v if not (changed_allow and n.k == 'allow')]
        assert normalize(current_nodes, True) == normalize(old_nodes), d.k
        if changed_allow:
            assert not any(n.k in ('any_province', 'all_province', 'any_country',
                                  'any_controlled_province', 'has_saved_event_target')
                           for n, _ in walk(d.get('allow').v)), d.k
    for f in (DIPLOMACY, 'events/Bretonnia.txt', 'missions/02_Dwarf_missions.txt'):
        assert normalize(parse(read(f)), True) == normalize(parse(baseline(f))), f
    assert not (ROOT / 'common/scripted_triggers/war_artifact_triggers.txt').exists()
    print('PASS: original visibility, highlights, transfer rules and rewards preserved; 25 allow world scans removed')

    # Audit every active placement, rather than just a hand-picked capture path.
    placements = 0
    for folder in ('common', 'events', 'decisions', 'missions'):
        for p in (ROOT / folder).rglob('*.txt'):
            text = p.read_text(encoding='utf-8-sig', errors='replace')
            if 'location_of_' not in text:
                continue
            for n, parents in walk(parse(text)):
                if n.k not in ('add_province_modifier', 'add_permanent_province_modifier'):
                    continue
                mod = n.get('name').v
                if mod not in MODS:
                    continue
                siblings = parents[-1].v
                index = siblings.index(n) + 1
                assert index < len(siblings), ('missing location hook', p, mod)
                hook = siblings[index]
                assert (hook.k, hook.v) == ('save_global_event_target_as', target(mod)), (p, mod)
                placements += 1
    assert placements == 118, placements
    setup = parse(read('events/War_Artifact_Setup.txt'))[1]
    assert setup.has('fire_only_once', 'yes') and setup.has('is_triggered_only', 'yes')
    assert read('common/on_actions/war_startup_on_actions.txt').count('war_artifact_setup.1') == 1
    print('PASS: all 118 placements update their province target; setup registered once and engine-gated once per campaign')

    # The setup reads relocated provinces, including unowned land, never history starts.
    for location in (None, '1', '2', '3', '4', '5'):
        w = ArtifactWorld()
        for mod in MODS:
            if location:
                w.provinces[location]['mods'].add(mod)
            w.targets[target(mod)] = ('p', '5')  # Stale targets must be overwritten/cleared.
        w.targets['war_location_of_the_fellblade'] = ('p', '1')
        w.flags.add('war_artifact_locations_initialized_v1')
        before = copy.deepcopy((w.countries, w.provinces))
        w.effect(setup.get('immediate').v)
        assert (w.countries, w.provinces) == before
        assert w.scans == 1
        for mod in MODS:
            assert w.targets.get(target(mod)) == (('p', location) if location else None)
        # Rebuilding is idempotent, although the startup event only runs once.
        first = copy.deepcopy(w.targets)
        w.effect(setup.get('immediate').v)
        assert w.targets == first
    print('PASS: absent, foreign, relocated and unowned artifacts initialize without moving/creating modifiers or reading legacy flags')

    fellblade = decisions.get('take_the_fellblade')
    mod = 'location_of_the_fellblade'
    cases = 0
    for location, neighbor, enemy, skaven, occupied, capital_controlled, ai in itertools.product(
            (None, '1', '2', '3'), *((False, True),) * 6):
        w = ArtifactWorld()
        w.neighbor, w.enemy, w.skaven, w.ai = neighbor, enemy, skaven, ai
        w.bind(mod, location)
        w.provinces['1']['controller'] = 'root' if capital_controlled else 'third'
        w.provinces['2']['controller'] = 'root' if occupied else 'from'
        visible = (not ai or enemy) and location not in ('1', '3') and (
            skaven or location == '2' and (neighbor or enemy))
        allowed = (not ai or enemy) and capital_controlled and (
            location in ('1', '3') or location == '2' and occupied)
        assert w.test(fellblade.get('potential').v) == visible
        assert w.test(fellblade.get('allow').v) == allowed
        assert w.scans == 0
        # A missing target must never affect ownership/neighbor visibility.
        w.targets.clear()
        assert w.test(fellblade.get('potential').v) == visible
        assert not w.test(fellblade.get('allow').v)
        cases += 1
    print(f'PASS: {cases} Fellblade ownership/neighbor/war/occupation/AI cases, including missing targets')

    for d in takes:
        mod = d.get('potential').get('all_owned_province').get('NOT').get('has_province_modifier').v
        w = ArtifactWorld()
        w.bind(mod, '2')
        w.provinces['2']['controller'] = 'root'
        assert w.test(d.get('allow').v), d.k
        # Changing ownership/occupation does not move the saved province target.
        w.provinces['2']['owner'] = 'third'
        assert w.test(d.get('allow').v), d.k
        w.provinces['2']['controller'] = 'third'
        assert not w.test(d.get('allow').v), d.k
        w.provinces['2']['controller'] = 'root'
        before = w.scans
        for _ in range(20):
            assert w.test(d.get('allow').v)
        assert w.scans == before
        # Stale target with no modifier must not enable a capture.
        w.provinces['2']['mods'].clear()
        assert not w.test(d.get('allow').v), d.k
        w.bind(mod, '2')
        w.effect(d.get('effect').v)
        assert w.targets[target(mod)] == ('p', '1')
        assert [p for p, value in w.provinces.items() if mod in value['mods']] == ['1']
    print('PASS: all 24 capture targets follow transfers; live controller checks reject third parties and stale modifiers')

    for d in parse(read(DIPLOMACY)):
        adds = [n for n, _ in walk(d.get('on_accept').v) if n.k == 'add_permanent_province_modifier']
        assert len(adds) == 1
        mod = adds[0].get('name').v
        w = ArtifactWorld()
        w.bind(mod, '3' if d.k.startswith('dip_gift') else '2')
        w.effect(d.get('on_accept').v)
        holders = [p for p, value in w.provinces.items() if mod in value['mods']]
        destination = '2' if d.k.startswith('dip_gift') else '1'
        assert holders == [destination] and w.targets[target(mod)] == ('p', destination), d.k
    relocate = decisions.get('relocate_artifacts')
    relocation_mods = {n.get('name').v for n, _ in walk(relocate.get('effect').v)
                       if n.k == 'add_permanent_province_modifier'}
    for mod in relocation_mods:
        for location, siege in itertools.product(('3', '4'), (False, True)):
            w = ArtifactWorld()
            w.bind(mod, location)
            w.provinces[location]['siege'] = siege
            w.effect(relocate.get('effect').v)
            destination = '3' if location == '3' and siege else '1'
            assert w.targets[target(mod)] == ('p', destination), (mod, location, siege)
    grail_event = next(n for n in parse(read('events/Bretonnia.txt'))
                       if n.k == 'country_event' and n.has('id', 'flavor_bretonnia.912'))
    w = ArtifactWorld()
    w.effect(grail_event.get('option').v[1:])  # Skip the option name.
    assert w.targets[target('location_of_the_grail')] == ('p', '1')
    dwarf_mission = next(n for n, _ in walk(parse(read('missions/02_Dwarf_missions.txt')))
                         if isinstance(n.v, list) and n.has('effect') and any(
                             c.k == 'add_permanent_province_modifier' and
                             c.has('name', 'location_of_the_gromril_crown')
                             for c, _ in walk(n.get('effect').v)))
    for already_forged in (False, True):
        w = ArtifactWorld()
        if already_forged:
            w.flags.add('gromril_crown_forged')
            w.bind('location_of_the_gromril_crown', '2')
        w.effect(dwarf_mission.get('effect').v)
        assert w.targets[target('location_of_the_gromril_crown')] == (
            'p', '2' if already_forged else '1')
    print('PASS: all 46 diplomatic transfers, 92 relocation/siege cases, Grail creation and one-time Crown forging update locations')

    resurrect = decisions.get('resurrect_nagash_decision')
    destroy = decisions.get('destroy_nagash')
    consumed = {n.v for n, _ in walk(resurrect.get('effect').v) if n.k == 'remove_province_modifier'}
    w = ArtifactWorld()
    for mod in MODS:
        w.bind(mod, '1')
    w.effect(resurrect.get('effect').v)
    assert len(consumed) == 5
    for mod in MODS:
        assert (target(mod) not in w.targets) == (mod in consumed)
        assert (mod not in w.provinces['1']['mods']) == (mod in consumed)
    assert w.targets[NAGASH] == ('c', 'root')
    # An existing save with a living Nagash must reconstruct the holder too.
    w.targets.clear()
    w.effect(setup.get('immediate').v)
    assert w.targets[NAGASH] == ('c', 'root')
    w.countries['root']['mods'].remove('nagash_resurrected_modifier')
    w.countries['from']['mods'].add('nagash_resurrected_modifier')
    w.targets[NAGASH] = ('c', 'from')
    assert not w.test(destroy.get('allow').v)
    w.provinces['2']['controller'] = 'root'
    assert w.test(destroy.get('allow').v)
    # Follow the holder's current capital, not its old capital province.
    w.provinces['5']['owner'] = 'from'
    w.countries['from']['capital'] = '5'
    assert not w.test(destroy.get('allow').v)
    w.provinces['5']['controller'] = 'root'
    assert w.test(destroy.get('allow').v)
    w.effect(destroy.get('effect').v)
    assert NAGASH not in w.targets and not w.test(destroy.get('allow').v)
    print('PASS: Nagash consumption clears only five targets; holder initialization, capital changes and destruction work in the model')
    print('Artifact static/model checks passed. EU4 parsing, tooltips, persistence and timing still need an engine test.')


if __name__ == '__main__':
    validate()
