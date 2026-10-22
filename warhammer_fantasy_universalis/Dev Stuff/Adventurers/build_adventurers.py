"""Build the authored adventurer events; run with Python 3 from any directory.

event_data.json is the editable source of localization and exact option effects.
Only the marked blocks in shared game files are replaced.
"""
from pathlib import Path
import json
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
DATA = json.loads((HERE / 'event_data.json').read_text())
CHARS = {c['code']: c for c in DATA['characters']}
MAP = json.loads((HERE / 'map_eligibility.json').read_text())

def write(relative, text, bom=False):
    p = ROOT / relative
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text.rstrip() + '\n', encoding='utf-8-sig' if bom else 'utf-8')

def marked(relative, name, content, before=None):
    p = ROOT / relative
    text = p.read_text()
    start, end = f'# BEGIN {name}', f'# END {name}'
    block = start + '\n' + content.rstrip() + '\n' + end
    if start in text:
        text = re.sub(re.escape(start) + r'.*?' + re.escape(end), lambda _: block, text, flags=re.S)
    elif before:
        assert before in text, (relative, before)
        text = text.replace(before, block + '\n' + before, 1)
    else:
        text = text.rstrip() + '\n\n' + block + '\n'
    p.write_text(text)

def fmt(n):
    return f'{n:g}'

def indent(text, depth=1):
    return '\n'.join('\t' * depth + line if line else '' for line in text.splitlines())

def effect_lines(option):
    lines = []
    for effect in option['effects']:
        key, value = effect['key'], effect['value']
        if key == 'add_prestige_or_monarch_power':
            code = f'{key} = {{ amount = {fmt(value)} }}'
        elif key == 'spawn_rebels':
            code = f'spawn_rebels = {{ type = particularist_rebels size = {fmt(value)} }}'
        else:
            code = f'{key} = {fmt(value)}'
        if effect.get('province'):
            code = 'event_target:war_adventurer_province = {\n' + indent(code) + '\n}'
        lines.append(code)
    return '\n'.join(lines)

def home_triggers():
    homes = {
        'empire': 'superregion = the_empire_superregion',
        'western_mountains': '''OR = {
    superregion = western_mountains_superregion
    region = world_edge_mountains_region
    region = southern_world_edge_mountains_region
    region = karak_eight_peaks_region
}''',
        'ulthuan': 'superregion = ulthuan_superregion',
        'underempire': '''OR = {
    superregion = skavenblight_superregion
    area = skavenblight_area
    area = skavenblight_tunnels_area
}''',
        'lustria': 'OR = { superregion = north_lustria_superregion superregion = south_lustria_superregion }',
    }
    out = ['# Province scope. Geography is fixed and never inferred from the owner.']
    for key, body in homes.items():
        out.append(f'war_adventurer_home_{key} = {{\n{indent(body)}\n}}')
    refs = {
        'GEL': 'war_adventurer_home_empire = yes',
        'TEC': 'war_adventurer_home_ulthuan = yes',
        'SNI': 'OR = { war_adventurer_home_underempire = yes superregion = cathay_superregion region = nippon_region }',
        'BUG': 'OR = { war_adventurer_home_empire = yes war_adventurer_home_western_mountains = yes }',
        'BAR': 'OR = { war_adventurer_home_empire = yes region = grey_mountains_region region = world_edge_mountains_region region = southern_world_edge_mountains_region region = karak_eight_peaks_region }',
        'HAR': 'OR = { region = norsca_region superregion = chaos_wastes_superregion superregion = eastern_steppes_superregion }',
        'ABH': 'OR = { region = nehekhara_region region = lahmia_region }',
        'ELS': 'war_adventurer_home_empire = yes',
        'WUL': 'war_adventurer_home_empire = yes',
        'GOF': 'OR = { war_adventurer_home_empire = yes war_adventurer_home_western_mountains = yes }',
        'REP': 'region = bretonnia_region',
        'SIE': 'OR = { war_adventurer_home_empire = yes region = estalia_region }',
        'MAL': 'war_adventurer_home_western_mountains = yes',
        'TYR': 'war_adventurer_home_ulthuan = yes',
        'GOR': 'war_adventurer_home_lustria = yes',
        'NAK': 'war_adventurer_home_lustria = yes',
        'THA': 'war_adventurer_home_underempire = yes',
        'GRO': 'war_adventurer_home_western_mountains = yes',
    }
    for code, c in CHARS.items():
        out.append(f'war_adventurer_{c["slug"]}_home = {{\n\t{refs[code]}\n}}')
    return '\n\n'.join(out)

def build_triggers():
    presence = '\n'.join('\t\thas_province_modifier = war_adventurer_' + c['slug'] for c in CHARS.values())
    text = '''# Country scope. Only Alignment / Racial Administration determine hostility.
war_adventurer_enemy_a = {
    OR = {
        has_country_modifier = chaos_nation
        has_country_modifier = destruction_nation
        has_country_modifier = orcish_administration
        has_country_modifier = skaven_administration
        has_country_modifier = undead_administration
    }
}
war_adventurer_enemy_b = {
    NOT = { has_country_modifier = skaven_administration }
}
war_adventurer_enemy_c = {
    OR = { has_country_modifier = order_nation has_country_modifier = undead_administration }
}
war_adventurer_enemy_d = {
    OR = {
        has_country_modifier = chaos_nation
        has_country_modifier = orcish_administration
        has_country_modifier = skaven_administration
        AND = {
            has_country_modifier = destruction_nation
            NOT = { has_country_modifier = undead_administration }
        }
    }
}

# Province scope; shared by selection and transfer, so characters never stack.
war_adventurer_present = {
    OR = {
PRESENCE
    }
}
war_adventurer_destination_province = {
    is_city = yes
    province_group = war_adventurer_mainlands
    NOT = { war_adventurer_present = yes }
}
# Country scope. random_country weights countries, not their province counts.
war_adventurer_destination_country = {
    NOT = { tag = event_target:war_adventurer_origin_country }
    any_owned_province = { war_adventurer_destination_province = yes }
}
# Province scope. A short rest prevents rapid hops between different countries' pulse dates.
war_adventurer_ready = {
    OR = {
        NOT = { has_province_flag = war_adventurer_event_open }
        # Recover a stale lock if an event disappeared with an annexed recipient.
        had_province_flag = { flag = war_adventurer_event_open days = 365 }
    }
    OR = {
        NOT = { has_province_flag = war_adventurer_arrived }
        had_province_flag = { flag = war_adventurer_arrived days = 365 }
    }
}
'''.replace('PRESENCE', presence)
    write('common/scripted_triggers/war_adventurer_triggers.txt', text + '\n' + home_triggers())

def build_movement():
    write('common/scripted_effects/war_adventurer_effects.txt', '''# Country scope. Called only after the destination COUNTRY has been selected.
# Bugman prefers beer within that country; this never changes country selection weights.
war_adventurer_pick_destination_province = {
    if = {
        limit = {
            always = $BEER$
            any_owned_province = {
                war_adventurer_destination_province = yes
                trade_goods = beer
            }
        }
        random_owned_province = {
            limit = { war_adventurer_destination_province = yes trade_goods = beer }
            save_event_target_as = war_adventurer_destination
        }
    }
    else = {
        random_owned_province = {
            limit = { war_adventurer_destination_province = yes }
            save_event_target_as = war_adventurer_destination
        }
    }
}

# Province scope. MODIFIER and LOCATION identify this one persistent adventurer.
# ARRIVAL_EVENT notifies the new owner only after a successful transfer.
# The origin remains intact if no eligible country exists anywhere.
war_adventurer_move = {
    save_event_target_as = war_adventurer_origin
    save_event_target_as = war_adventurer_destination
    ROOT = { save_event_target_as = war_adventurer_origin_country }
    if = {
        limit = { is_empty = no }
        owner = {
            save_event_target_as = war_adventurer_origin_country
            set_variable = { which = war_adventurer_neighbor_count value = 0 }
            every_neighbor_country = {
                event_target:war_adventurer_origin_country = {
                    change_variable = { which = war_adventurer_neighbor_count value = 1 }
                }
            }
            if = {
                limit = {
                    check_variable = { which = war_adventurer_neighbor_count value = 2 }
                    any_neighbor_country = { war_adventurer_destination_country = yes }
                }
                random_neighbor_country = {
                    limit = { war_adventurer_destination_country = yes }
                    war_adventurer_pick_destination_province = { BEER = $BEER$ }
                }
            }
            else = {
                # Zero/one neighbor, or a completely blocked neighbor pool: world travel.
                random_country = {
                    limit = { war_adventurer_destination_country = yes }
                    war_adventurer_pick_destination_province = { BEER = $BEER$ }
                }
            }
            set_variable = { which = war_adventurer_neighbor_count value = 0 }
        }
    }
    else = {
        # Ownership disappeared while the report was open. Preserve the traveller.
        random_country = {
            limit = { war_adventurer_destination_country = yes }
            war_adventurer_pick_destination_province = { BEER = $BEER$ }
        }
    }
    event_target:war_adventurer_destination = {
        if = {
            limit = { war_adventurer_destination_province = yes }
            add_province_modifier = { name = $MODIFIER$ duration = -1 }
            set_province_flag = war_adventurer_arrived
            save_global_event_target_as = $LOCATION$
            event_target:war_adventurer_origin = {
                remove_province_modifier = $MODIFIER$
                clr_province_flag = war_adventurer_arrived
                clr_province_flag = war_adventurer_event_open
            }
            # Keep this report's province independent of later global location changes.
            save_event_target_as = war_adventurer_arrival_province
            owner = { country_event = { id = $ARRIVAL_EVENT$ } }
        }
    }
}
''')

def build_setup():
    lines = ['namespace = war_adventurer_setup', '',
             '# Seed the eighteen unique travellers once, including when first loading an older save.',
             'country_event = {', '\tid = war_adventurer_setup.1', '\thidden = yes',
             '\tis_triggered_only = yes', '\ttrigger = { NOT = { has_global_flag = war_adventurers_initialized } }',
             '\timmediate = {', '\t\tif = {',
             '\t\t\tlimit = { NOT = { has_global_flag = war_adventurers_initialized } }',
             '\t\t\tset_global_flag = war_adventurers_initialized']
    for c in CHARS.values():
        slug = c['slug']
        placement = f'''add_province_modifier = {{ name = war_adventurer_{slug} duration = -1 }}
save_global_event_target_as = war_adventurer_location_{slug}'''
        lines += [f'\t\t\t# {c["name"]}; approved mainland start, or an owned mainland in an older save.',
                  '\t\t\tif = {', f'\t\t\t\tlimit = {{ {c["start"]} = {{ is_empty = no war_adventurer_destination_province = yes }} }}',
                  f'\t\t\t\t{c["start"]} = {{', indent(placement, 5), '\t\t\t\t}', '\t\t\t}',
                  '\t\t\telse = {', '\t\t\t\trandom_country = {',
                  '\t\t\t\t\tlimit = { any_owned_province = { war_adventurer_destination_province = yes } }',
                  f'\t\t\t\t\twar_adventurer_pick_destination_province = {{ BEER = {"yes" if c["code"] == "BUG" else "no"} }}',
                  '\t\t\t\t\tevent_target:war_adventurer_destination = {', indent(placement, 6),
                  '\t\t\t\t\t}', '\t\t\t\t}', '\t\t\t}']
    lines += ['\t\t}', '\t}', '\t# Hidden acknowledgement; all placement happens immediately.',
              '\toption = { name = war_adventurer_setup.1.a }', '}']
    write('events/War_Adventurer_Setup.txt', '\n'.join(lines))
    marked('common/on_actions/war_startup_on_actions.txt', 'WAR_ADVENTURER_STARTUP',
           '\t\twar_adventurer_setup.1\t# One-time unique adventurer placement',
           before='\t\twarhammer_setup.1')

def build_modifiers():
    lines = ['# Approved presence modifiers: identical for all owner relationships.',
             '# Balance Guide has national equivalents but no direct valuation for these local forms.',
             '# Preserve the approved local benefit / +2 local unrest package.',
             '# User-requested +10% province trade power makes every traveller visible in trade map mode.',
             '# Thanquol already used this key: replace his +5% with +10%, without a duplicate entry.']
    for c in CHARS.values():
        bonuses = {c['bonus']: 0.05, 'province_trade_power_modifier': 0.1, 'local_unrest': 2}
        lines += ['', f'# {c["name"]}: the modifier follows the adventurer.',
                  f'war_adventurer_{c["slug"]} = {{']
        lines += [f'\t{key} = {fmt(value)}' for key, value in bonuses.items()]
        lines += ['\tpicture = "war_adventurer_icon"', '}']
    write('common/event_modifiers/war_adventurer_modifiers.txt', '\n'.join(lines))

def build_events():
    localization = ['l_english:']
    pulse = []
    for c in CHARS.values():
        slug = c['slug']; namespace = 'war_adventurer_' + slug
        lines = [f'namespace = {namespace}', '',
                 '# Generated from Dev Stuff/Adventurers/event_data.json; edit that authored source.',
                 '# Budget source: Dev Stuff/Examples/Balance Guide.txt. No MTTH.', '']
        modifier_name = c.get('modifier_name', c['name'] + ', Adventurer')
        localization += [f' {namespace}:0 "{escape(modifier_name)}"',
                         f' desc_{namespace}:0 "{escape(c["modifier_description"])}"']
        pulse.append(f'\t\t# {c["name"]}: five eligible home/abroad and friendly/enemy variants.')
        for e in [e for e in DATA['events'] if e['code'] == c['code']]:
            id = namespace + '.' + str(e['number'])
            assert e.get('description') and all('effects' in o for o in e['options']), e['concept_id']
            home = 'yes' if e['category'].endswith('H') else 'no'
            enemy = 'yes' if e['category'].startswith('E') else 'no'
            extra = e.get('province_trigger', '')
            trigger = f'''event_target:war_adventurer_location_{slug} = {{
    owned_by = ROOT
    has_province_modifier = {namespace}
    war_adventurer_ready = yes
    war_adventurer_{slug}_home = {home}
    owner = {{ war_adventurer_enemy_{c['profile']} = {enemy} }}
    owner = {{
        any_country = {{
            NOT = {{ tag = ROOT }}
            any_owned_province = {{ war_adventurer_destination_province = yes }}
        }}
    }}
{indent(extra) if extra else ''}
}}'''
            lines += [f'# {e["concept_id"]}: {e["title"]}. Intended event Weighing Value: {e["weight"]:+}. Lore: {e["lore"]}.',
                      'country_event = {', f'\tid = {id}', f'\ttitle = {id}.t', f'\tdesc = {id}.d',
                      f'\tpicture = WAR_ADVENTURER_{c["code"]}_eventPicture', '\tis_triggered_only = yes',
                      '\ttrigger = {', indent(trigger, 2), '\t}',
                      '\timmediate = {', f'\t\tevent_target:war_adventurer_location_{slug} = {{',
                      '\t\t\tsave_event_target_as = war_adventurer_province', '\t\t\tset_province_flag = war_adventurer_event_open',
                      '\t\t}', '\t}', '\tgoto = war_adventurer_province']
            for i, option in enumerate(e['options']):
                letter = chr(97 + i)
                weight = option['weight']
                assert abs(weight-e['weight']) <= 1, (e['concept_id'],i,weight)
                lines += ['', f'\t# {option["label"]}. Option Weighing Value: {weight:+g}.',
                          '\toption = {', f'\t\tname = {id}.option_{letter}', '\t\tai_chance = { factor = 1 }',
                          indent(effect_lines(option), 2),
                          '\t\tcustom_tooltip = war_adventurer_leaves_tt', '\t}']
                localization.append(f' {id}.option_{letter}:0 "{escape(option["label"])}"')
            lines += ['', '\tafter = {', '\t\thidden_effect = {', '\t\t\tevent_target:war_adventurer_province = {',
                      '\t\t\t\tclr_province_flag = war_adventurer_event_open', '\t\t\t\tif = {',
                      f'\t\t\t\t\tlimit = {{ has_province_modifier = {namespace} }}',
                      f'\t\t\t\t\twar_adventurer_move = {{ MODIFIER = {namespace} LOCATION = war_adventurer_location_{slug} BEER = {"yes" if c["code"] == "BUG" else "no"} ARRIVAL_EVENT = {namespace}.21 }}',
                      '\t\t\t\t}', '\t\t\t}', '\t\t}', '\t}', '}', '']
            localization += [f' {id}.t:0 "{escape(e["title"])}"', f' {id}.d:0 "{escape(e["description"])}"']
            pulse.append(f'\t\t400 = {id}')
        # Arrival notices are invoked by movement, never drawn from the encounter pulse.
        arrival_id = namespace + '.21'
        verb = 'have' if c['code'] in ('GOF', 'THA') else 'has'
        arrival_title = c['name'] + ' ' + verb + ' arrived in [war_adventurer_arrival_province.GetName]'
        lines += [f'# Arrival report: introduce {c["name"]} to the new owner. No mechanical effects.',
                  'country_event = {', f'\tid = {arrival_id}', f'\ttitle = {arrival_id}.t',
                  f'\tdesc = {arrival_id}.d', f'\tpicture = WAR_ADVENTURER_{c["code"]}_eventPicture',
                  '\tis_triggered_only = yes', '\ttrigger = {',
                  '\t\tevent_target:war_adventurer_arrival_province = {',
                  '\t\t\towned_by = ROOT', f'\t\t\thas_province_modifier = {namespace}',
                  '\t\t}', '\t}',
                  '\t# Acknowledge the arrival report. Option Weighing Value: 0.',
                  '\toption = { name = war_adventurer_arrival_acknowledge }', '}', '']
        localization += [f' {arrival_id}.t:0 "{escape(arrival_title)}"',
                         f' {arrival_id}.d:0 "{escape(c["arrival_description"])}"']
        write(f'events/War_Adventurer_{slug}.txt', '\n'.join(lines))
    localization += [' war_adventurer_setup.1.a:0 "Their journeys begin."',
                     ' war_adventurer_arrival_acknowledge:0 "Noted."',
                     ' war_adventurer_leaves_tt:0 "The adventurer departs for another eligible country. With two or more neighbours, an eligible neighbour is chosen; with zero or one, the destination is chosen worldwide. If all neighbouring destinations are blocked, travel also becomes worldwide. If no destination exists, the adventurer remains until a later encounter."',
                     ' war_adventurer_mainlands:0 "Adventurer Mainlands"']
    write('localisation/war_adventurers_l_english.yml', '\n'.join(localization), bom=True)
    # This exact active block is unique to pulse 5 in the current mod.
    p = ROOT / 'common/on_actions/00_on_actions.txt'
    text = p.read_text(); start = text.index('on_bi_yearly_pulse_5 = {')
    opening = text.index('random_events = {', start)
    boundary = text.index('\n', opening) + 1
    marker = '# BEGIN WAR_ADVENTURER_PULSE_5'
    content = '\t\t' + marker + '\n' + '\n'.join(pulse) + '\n\t\t# END WAR_ADVENTURER_PULSE_5\n'
    if marker in text:
        text = re.sub(r'\t*# BEGIN WAR_ADVENTURER_PULSE_5.*?# END WAR_ADVENTURER_PULSE_5\n', lambda _: content, text, flags=re.S)
    else:
        text = text[:boundary] + content + text[boundary:]
    p.write_text(text)

def escape(text):
    return text.replace('"', "'").replace('\n\n', '\\n\\n').replace('\n', ' ')

def main():
    ids = MAP['allowed']
    body = '# Pixel-connected mainlands, plus the principal Ulthuan and Nippon landmasses.\nwar_adventurer_mainlands = {\n'
    body += '\n'.join('\t' + ' '.join(map(str,ids[i:i+24])) for i in range(0,len(ids),24)) + '\n}\n'
    marked('map/provincegroup.txt', 'WAR_ADVENTURER_MAINLANDS', body)
    build_triggers(); build_movement(); build_setup(); build_modifiers(); build_events()
    print('Built 360 encounters, eighteen arrival notices, eighteen presence modifiers, startup, movement, pulse registration, and BOM localization.')

if __name__ == '__main__':
    main()
