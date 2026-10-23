#!/usr/bin/env python3
"""Inventory uncommented vanilla identifiers; candidates require semantic review.
Uses the installed game's catalogs as primary evidence, never localized names.
"""
from pathlib import Path
from collections import Counter, defaultdict
import csv,json,sys
from script_parser import ROOT,parse,walk
BASE=Path(sys.argv[1]) if len(sys.argv)>1 else Path.home()/'Library/Application Support/Steam/steamapps/common/Europa Universalis IV'
OUT=Path(__file__).resolve().parent
errors=[]
def nodes(p):
 try:return parse(p.read_text(encoding='utf-8-sig',errors='replace'))
 except Exception as e:
  errors.append((str(p),str(e)))
  # Recover missing closing braces only for inventory; validation remains strict.
  return parse(p.read_text(encoding='utf-8-sig',errors='replace'),allow_unclosed=True)
def catalog(root):
 out=defaultdict(set)
 for p in (root/'common/religions').glob('*.txt'):
  for n in nodes(p):
   if not isinstance(n.v,list):continue
   out['religion_group'].add(n.k)
   for r in n.v:
    if isinstance(r.v,list) and r.has('color') and r.has('icon'):out['religion'].add(r.k)
 for p in (root/'common/cultures').glob('*.txt'):
  for n in nodes(p):
   if not isinstance(n.v,list):continue
   out['culture_group'].add(n.k)
   for c in n.v:
    if isinstance(c.v,list) and c.k not in ('male_names','female_names','dynasty_names','country','province','graphical_culture'):
     out['culture'].add(c.k)
 for kind,filename in [('area','area.txt'),('region','region.txt'),('superregion','superregion.txt'),('continent','continent.txt')]:
  p=root/'map'/filename
  if p.exists():out[kind].update(n.k for n in nodes(p) if isinstance(n.v,list))
 for p in (root/'common/tradenodes').glob('*.txt'):out['trade_node'].update(n.k for n in nodes(p) if isinstance(n.v,list))
 return out
vanilla=catalog(BASE);mod=catalog(ROOT)
keys={
 'religion':'religion','religion_group':'religion_group','secondary_religion':'religion','dominant_religion':'religion','original_religion':'religion','ruler_religion':'religion','heir_religion':'religion','consort_religion':'religion','province_religion':'religion','has_religion':'religion','religion_is_in_group':'religion_group',
 'culture':'culture','primary_culture':'culture','accepted_culture':'culture','dominant_culture':'culture','ruler_culture':'culture','heir_culture':'culture','consort_culture':'culture','is_accepted_culture':'culture','culture_group':'culture_group',
 'area':'area','region':'region','superregion':'superregion','continent':'continent','trade_node':'trade_node','home_trade_node':'trade_node','is_strongest_trade_power':'trade_node','most_province_trade_power':'trade_node','has_merchant':'trade_node','has_trader':'trade_node','has_privateers':'trade_node',
 'change_religion':'religion','change_culture':'culture','change_primary_culture':'culture','add_accepted_culture':'culture','remove_accepted_culture':'culture'}
# Include unknown scalar-key uses of exact catalog IDs to avoid missing rare triggers;
# such rows are explicitly marked for manual classification rather than auto-disabling.
reverse=defaultdict(list)
for kind,ids in vanilla.items():
 for x in ids:reverse[x].append(kind)
rows=[]; definitions=defaultdict(list)
condition_names={'trigger','potential','allow','limit','can_use','can_select','is_visible','is_allowed','ai_will_do','ai_chance','modifier','provinces_to_highlight','chance','possible'}
for folder in ['events','decisions','common','missions']:
 for p in sorted((ROOT/folder).rglob('*.txt')):
  text=p.read_text(encoding='utf-8-sig',errors='replace');ns=nodes(p)
  for n,parents in walk(ns):
   if not parents:continue
   names=[x.k for x in parents]
   is_shared='scripted_triggers' in p.parts
   context='condition' if is_shared or any(x in condition_names or x.endswith('_trigger') for x in names) else 'effect_or_setup'
   if folder not in ('events','decisions') and not is_shared and context!='condition':continue
   matches=[];confidence='typed reference'
   if isinstance(n.v,str) and n.k in keys:
    kind=keys[n.k]
    if n.v in vanilla[kind]:matches=[(kind,n.v)]
   elif isinstance(n.v,list):
    matches=[(kind,n.k) for kind in ('area','region','superregion','continent','trade_node') if n.k in vanilla[kind]]
   elif isinstance(n.v,str) and n.v in reverse:
    # Exclude tooltip/text/flag IDs and declarations that merely share a word.
    if n.k not in ('id','name','title','desc','tooltip','custom_tooltip','picture','sprite','set_country_flag','has_country_flag','set_global_flag','has_global_flag','save_event_target_as','save_global_event_target_as'):
     matches=[(kind,n.v) for kind in reverse[n.v]];confidence='unclassified exact identifier; inspect key'
   elif n.v is None and n.k in reverse:
    matches=[(kind,n.k) for kind in reverse[n.k]];confidence='list entry; inspect parent'
   if not matches:continue
   top=parents[0];defn=top.k;execution='shared trigger' if is_shared else 'other trigger'
   if folder=='events' and top.k in ('country_event','province_event'):
    defn=top.get('id').v if top.has('id') else 'MISSING_ID'
    execution='triggered event' if top.has('is_triggered_only','yes') else 'polled '+top.k
   elif folder=='decisions':
    defn=parents[1].k if len(parents)>1 else n.k;execution='decision'
   elif folder=='missions':
    mission=next((a for a in parents if isinstance(a.v,list) and a.has('icon') and a.has('trigger')),None)
    if mission:defn=mission.k
    execution='mission'
   for kind,value in matches:
    site='shared trigger' if is_shared else ' / '.join(x.k for x in parents[:3])
    if folder=='events':
     site=next((x.k for x in parents[1:] if x.k in ('trigger','mean_time_to_happen','immediate','option','desc','after')), 'event metadata')
    status='retained identifier' if value in mod[kind] else 'absent from mod catalog'
    if kind=='continent' and value in mod[kind]:status='reused map identifier; retain'
    row=dict(file=str(p.relative_to(ROOT)),line=text.count('\n',0,n.s)+1,definition=defn,execution=execution,context=context,evaluation_site=site,kind=kind,identifier=value,catalog_status=status,key=n.k,path=' / '.join(names),classification=confidence)
    rows.append(row);definitions[(row['file'],defn,execution)].append(row)
with (OUT/'vanilla_reference_inventory.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
summary=[]
for (file,defn,execution),rs in sorted(definitions.items()):
 checked=[r for r in rs if r['context']=='condition' and r['catalog_status']!='reused map identifier; retain']
 if not checked:continue
 summary.append(dict(file=file,line=min(r['line'] for r in checked),definition=defn,execution=execution,evaluation_sites='; '.join(sorted(set(r['evaluation_site'] for r in checked))),kinds='; '.join(sorted(set(r['kind'] for r in checked))),identifiers='; '.join(sorted(set(r['identifier'] for r in checked))),missing_from_mod='; '.join(sorted(set(r['identifier'] for r in checked if r['catalog_status']=='absent from mod catalog'))),review='Review the whole condition and callers before commenting out; NOT/OR and mixed WFU branches may remain relevant.'))
with (OUT/'vanilla_condition_candidates.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
lines=['VANILLA REFERENCE AUDIT','',f'Catalog source: {BASE}',f'Scope: active .txt files in mod events, decisions, scripted triggers, and condition blocks throughout common/missions.', 'Comments and .bak files are excluded. Files inherited from the base game but absent from the mod are outside this report.',f'{len(rows)} references across {len(definitions)} definitions. {len(summary)} definitions contain non-continent vanilla condition references.', '', 'Files:', 'vanilla_condition_candidates.csv: one row per event, decision, shared trigger or other definition to review.', 'vanilla_reference_inventory.csv: every match with exact line, nesting, condition/effect context and catalog status.', '', 'Do not blanket-disable these rows. Negated checks and OR branches can apply to WFU countries; a shared trigger can have WFU callers.', 'Retained religions/cultures are still defined in this mod, even when they have no intended starting population.', 'Continent names (europe, asia, africa, north_america, etc.) are intentionally reused for the Warhammer map and are not removal candidates.', 'Absent mod-catalog IDs may still be inherited unless the mod descriptor replaces that base-game path.', '', 'Condition candidates by execution:']
lines += [f'{k}: {v}' for k,v in Counter(r['execution'] for r in summary).most_common()]
lines+=['','Polled event and decision candidates (highest priority for runtime review):']+[f"{r['file']}:{r['line']} | {r['definition']} | {r['execution']} | {r['evaluation_sites']} | {r['identifiers']}" for r in summary if r['execution'].startswith('polled') or r['execution']=='decision']
lines+=['','Most candidate-heavy files:']+[f'{n}: {c}' for n,c in Counter(r['file'] for r in summary).most_common(35)]
lines+=['','Catalog overlap (vanilla IDs also defined by mod):']+[f'{k}: {len(vanilla[k]&mod[k])}/{len(vanilla[k])}' for k in vanilla]
lines+=['','Pre-existing parse problems (recovered for inventory; files were not edited):']+[f'{p}: {err}' for p,err in errors]
if not errors:lines+=['None.']
(OUT/'Vanilla Reference Audit.txt').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines[:9]));print('Parse failures:',len(errors));print('Candidate counts:',dict(Counter(r['execution'] for r in summary)))
