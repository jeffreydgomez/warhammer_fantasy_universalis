#!/usr/bin/env python3
"""Apply the reviewed province-focused choices and regenerate pulse eligibility.

The TSV is the authored choice/eligibility plan. Event files retain authored story
paragraphs, special prerequisites, movement, and arrival notices. This tool does
not regenerate presence modifiers, startup, portraits, or the adventurer browser.
Run from any directory with Python 3; no dependencies are required.
"""
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
PLAN = HERE / 'adventurer_event_balance.tsv'
PROVINCE = 'event_target:war_adventurer_province'
ROSTER = ['gelt', 'teclis', 'snikch', 'bugman', 'bardin', 'harald', 'abhorash',
          'elspeth', 'wulfhart', 'gotrek_felix', 'repanse', 'sienna', 'malakai',
          'tyrion', 'gor_rok', 'nakai', 'thanquol', 'grombrindal']
# One direct +/-1 effect per choice; no stacked country rewards or penalties.
# Building additions/removals use the user's explicit +/-1 example scale.
EFFECTS = {
    'tax': (1, 'province', 'add_base_tax = 2'),
    'prod': (1, 'province', 'add_base_production = 2'),
    'men': (1, 'province', 'add_base_manpower = 2'),
    'auto': (-1, 'province', 'add_local_autonomy = 50'),
    'devast': (-1, 'province', 'add_devastation = 50'),
    'study': (1, 'country', 'change_innovativeness = 1'),
    'drill': (1, 'country', 'add_army_professionalism = 0.02'),
    'prestige': (1, 'country', 'add_prestige_or_monarch_power = { amount = 25 }'),
    'cost': (-1, 'country', 'add_years_of_income = -0.5'),
    'shame': (-1, 'country', 'add_prestige = -25'),
    'none': (0, 'none', ''),
}


def blocks(text, key=None):
    """Return top-level Clausewitz assignments and exact offsets, ignoring comments."""
    tokens = list(re.finditer(r'"(?:\\.|[^"\\])*"|#[^\n]*|[{}=]|[^\s{}=#]+', text))
    tokens = [t for t in tokens if not t.group().startswith('#')]
    i = 0
    while i < len(tokens):
        name = tokens[i].group()
        assert tokens[i + 1].group() == '=', (name, 'missing equals')
        start, i = tokens[i].start(), i + 2
        value = tokens[i]
        if value.group() == '{':
            depth, j = 1, i + 1
            while depth:
                depth += (tokens[j].group() == '{') - (tokens[j].group() == '}')
                j += 1
            end = tokens[j - 1].end()
            body = text[value.end():tokens[j - 1].start()]
            i = j
        else:
            end, body, i = value.end(), value.group(), i + 1
        if key is None or key == name:
            yield name, body, start, end


def scalar(text, key):
    return next(body.strip() for _, body, _, _ in blocks(text, key))


def parse_plan():
    result = {}
    for line in PLAN.read_text().splitlines():
        if not line.strip() or line.startswith('#'):
            continue
        eid, eligibility, *choices = line.strip().split('|')
        assert eid not in result and 2 <= len(choices) <= 4
        assert eligibility in {'=', '**', 'F*', 'E*', '*H', '*A'}
        result[eid] = (eligibility, [c.split(':', 1) for c in choices])
    assert len(result) == 360
    return result


def building_requirement(code):
    building = code.split('_', 1)[1]
    if code.startswith('lose_'):
        return f'has_building = {building}'
    requirement = f'NOT = {{ has_building = {building} }}'
    if building == 'counting_house':
        requirement += '\nNOT = { trade_goods = gold }'
    return requirement


def indent(text, count=1):
    return '\n'.join('\t' * count + line for line in text.splitlines())


def format_block(text, level=0):
    lines = []
    for key, body, start, end in blocks(text):
        if re.match(r'[^\s=]+\s*=\s*\{', text[start:end]):
            lines += ['\t' * level + key + ' = {', format_block(body, level + 1), '\t' * level + '}']
        else:
            lines.append('\t' * level + key + ' = ' + body)
    return '\n'.join(lines)


def option_script(eid, index, code, label):
    building = code.startswith(('build_', 'lose_'))
    weight = (1 if code.startswith('build_') else -1) if building else EFFECTS[code][0]
    lines = [f'\t# {label}. Option Weighing Value: {weight:+d}.',
             '\toption = {', f'\t\tname = {eid}.option_{chr(97 + index)}',
             '\t\tai_chance = { factor = 1 }']
    if building:
        requirement = building_requirement(code)
        lines += ['\t\ttrigger = {', '\t\t\t' + PROVINCE + ' = {',
                  indent(requirement, 4), '\t\t\t}', '\t\t}']
        verb = 'add_building' if code.startswith('build_') else 'remove_building'
        # Recheck on resolution: a building may have changed while the report was open.
        effect = ('if = {\n\tlimit = {\n' + indent(requirement, 2) + '\n\t}\n'
                  f'\t{verb} = {code.split("_", 1)[1]}\n}}')
        lines += ['\t\t' + PROVINCE + ' = {', indent(effect, 3), '\t\t}']
    else:
        _, scope, effect = EFFECTS[code]
        if scope == 'province':
            lines += ['\t\t' + PROVINCE + ' = {', indent(effect, 3), '\t\t}']
        elif scope == 'country':
            lines += [indent(effect, 2)]
    lines += ['\t\tif = {', '\t\t\tlimit = {',
              '\t\t\t\tevent_target:war_adventurer_destination_country = { war_adventurer_destination_country = yes }',
              '\t\t\t}', '\t\t\tcustom_tooltip = war_adventurer_leaves_tt', '\t\t}',
              '\t\telse = { custom_tooltip = war_adventurer_stays_tt }', '\t}']
    return '\n'.join(lines)


def revised_trigger(body, eligibility, slug):
    if eligibility[1:] == '*':
        body = re.sub(r'^[ \t]*war_adventurer_' + slug + r'_home = (yes|no)\s*\n', '', body, flags=re.M)
    if eligibility.startswith('*'):
        body = re.sub(r'^[ \t]*owner = \{ war_adventurer_enemy_[a-d] = (yes|no) \}\s*\n', '', body, flags=re.M)
    return body


def pulse_output(event_triggers):
    path = ROOT / 'common/scripted_effects/war_adventurer_pulse_effects.txt'
    old = path.read_text()
    # Preserve the global ownership snapshot and host scheduler exactly.
    prefix = old[:old.index('# Country scope. Cache a scheduled visitor')]
    lines = [prefix.rstrip(), '',
        '# Country scope. Cache a scheduled visitor still owned by this host.',
        '# Per-story geography, relationship and special prerequisites are checked in the draw.',
        'war_adventurer_cache_pulse_candidate = {',
        '    if = {', '        limit = {',
        '            has_country_flag = war_adventurer_pulse_$SLUG$_scheduled',
        '            event_target:war_adventurer_location_$SLUG$ = {',
        '                owned_by = ROOT',
        '                has_province_modifier = war_adventurer_$SLUG$',
        '            }', '        }',
        '        set_country_flag = war_adventurer_pulse_has_candidate',
        '        set_country_flag = war_adventurer_pulse_$SLUG$_eligible',
        '    }', '}', '',
        '# Country scope. One uniform draw over eligible stories for snapshotted visitors.',
        '# No fixed five-story categories: each entry mirrors its encounter trigger.',
        'war_adventurer_dispatch_pulse = {']
    for slug in ROSTER:
        lines.append(f'\twar_adventurer_cache_pulse_candidate = {{ SLUG = {slug} }}')
    lines += ['', '\t# The world destination search runs once per host, never once per story.',
        '\tif = {', '\t\tlimit = { has_country_flag = war_adventurer_pulse_has_candidate }',
        '\t\tif = {', '\t\t\tlimit = {', '\t\t\t\tany_country = {',
        '\t\t\t\t\tNOT = { tag = ROOT }',
        '\t\t\t\t\tany_owned_province = { war_adventurer_destination_province = yes }',
        '\t\t\t\t}', '\t\t\t}', '\t\t\trandom_list = {']
    for slug in ROSTER:
        for number in range(1, 21):
            eid = f'war_adventurer_{slug}.{number}'
            condition = event_triggers[eid]
            # Normalize indentation without changing the actual trigger tree.
            condition = format_block(condition)
            lines += ['\t\t\t\t1 = {', '\t\t\t\t\ttrigger = {',
                f'\t\t\t\t\t\thas_country_flag = war_adventurer_pulse_{slug}_eligible',
                indent(condition, 6), '\t\t\t\t\t}',
                f'\t\t\t\t\tcountry_event = {{ id = {eid} }}', '\t\t\t\t}']
    lines += ['\t\t\t}', '\t\t}', '\t}', '',
        '\t# Clear all scheduling state, including caches left by the older dispatcher.']
    for slug in ROSTER:
        for suffix in ('scheduled', 'eligible', 'home', 'enemy'):
            lines.append(f'\tclr_country_flag = war_adventurer_pulse_{slug}_{suffix}')
        lines.append(f'\tset_variable = {{ which = war_adventurer_pulse_{slug}_weight value = 0 }}')
    lines += ['\tclr_country_flag = war_adventurer_pulse_has_candidate', '}', '']
    return '\n'.join(lines)


def build():
    plan = parse_plan()
    path = ROOT / 'localisation/war_adventurers_l_english.yml'
    loc_text = path.read_text(encoding='utf-8-sig')
    loc = dict(re.findall(r'^\s*(\S+):\d+\s+"(.*)"', loc_text, re.M))
    event_triggers, outputs, updates = {}, {}, {}
    for slug in ROSTER:
        relative = f'events/War_Adventurer_{slug}.txt'
        text = (ROOT / relative).read_text()
        for _, body, start, end in reversed(list(blocks(text, 'country_event'))):
            eid = scalar(body, 'id')
            number = int(eid.split('.')[-1])
            if number > 20:
                continue
            eligibility, options = plan[f'{slug}.{number}']
            opts = list(blocks(body, 'option'))
            after_start = next(s for _, _, s, _ in blocks(body, 'after'))
            # Include the preceding option-intent comments when replacing the choice block.
            opt_start = body.rfind('\n\t# ', 0, opts[0][2])
            assert opt_start >= 0
            body = body[:opt_start].rstrip() + '\n\n' + '\n\n'.join(
                option_script(eid, i, code, label) for i, (code, label) in enumerate(options)
            ) + '\n\n\t' + body[after_start:]
            _, trigger, ts, te = next(blocks(body, 'trigger'))
            trigger = revised_trigger(trigger, eligibility, slug)
            event_triggers[eid] = trigger
            body = body[:ts] + 'trigger = {' + trigger + '}' + body[te:]
            text = text[:start] + 'country_event = {' + body + '}' + text[end:]
            for i, (_, label) in enumerate(options):
                updates[f'{eid}.option_{chr(97+i)}'] = label
            description = loc[eid + '.d'].split(r'\n\n')
            last_sentence = re.split(r'(?<=[.!?])\s+', description[-1])[-1]
            first, second = (label[0].lower() + label[1:] for _, label in options[:2])
            description[-1] = (f'Our officials ask whether we should {first}. '
                               f'Another proposal is to {second}. ' + last_sentence)
            updates[eid + '.d'] = r'\n\n'.join(description)
        text = text.replace('# Generated from Dev Stuff/Adventurers/event_data.json; edit that authored source.',
                            '# Choices and eligibility: Dev Stuff/Tools/adventurer_event_balance.tsv.')
        text = re.sub(r'Intended event Weighing Value: ([+-])\d+(?:\.\d+)?\.',
                      lambda m: 'Intended event Weighing Value: ' + m[1] + '1.', text)
        outputs[relative] = text.encode()
    def replace(match):
        prefix, key, value = match.groups()
        return prefix + '"' + updates.get(key, value).replace('"', "'") + '"'
    loc_text = re.sub(r'^(\s*(\S+):\d+\s+)"(.*)"', replace, loc_text, flags=re.M)
    # Preserve existing localisation order; append any newly added fourth choice.
    new_keys = updates.keys() - loc.keys()
    for key in sorted(new_keys):
        loc_text += f' {key}:0 "{updates[key]}"\n'
    outputs['localisation/war_adventurers_l_english.yml'] = loc_text.encode('utf-8-sig')
    outputs['common/scripted_effects/war_adventurer_pulse_effects.txt'] = pulse_output(event_triggers).encode()
    return outputs


if __name__ == '__main__':
    for filename, content in build().items():
        (ROOT / filename).write_bytes(content)
    print('Updated 360 encounters and 1,049 choices, BOM localisation, and uniform eligible-story dispatch.')
