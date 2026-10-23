#!/usr/bin/env python3
"""Validate geographic sets, relationship filters, distinct artifact quotas and design sync."""
from pathlib import Path
from collections import Counter
import json,random,subprocess,itertools
from script_parser import ROOT,parse,walk,read
BASELINE='85be098c'
PREFIX=subprocess.check_output(['git','rev-parse','--show-prefix'],cwd=ROOT,text=True).strip()
def previous(p,revision=BASELINE):return subprocess.check_output(['git','show',revision+':'+PREFIX+p],cwd=ROOT).decode('utf-8-sig')
def sig(ns):return [(n.k,sig(n.v) if isinstance(n.v,list) else n.v) for n in ns]
def lookup(ns,k):return next(n for n in ns if n.k==k)
def scalar_ids(ns):return {n.k for n in ns if n.v is None and n.k.isdecimal()}
areas={n.k:scalar_ids(n.v) for n in parse(read('map/area.txt')) if isinstance(n.v,list)}
regions={n.k:set().union(*(areas.get(x.k,set()) for x in n.get('areas').v)) for n in parse(read('map/region.txt')) if isinstance(n.v,list) and n.has('areas')}
continents={n.k:scalar_ids(n.v) for n in parse(read('map/continent.txt')) if isinstance(n.v,list)}
geography={**areas,**regions,**continents}
all_provinces=set().union(*geography.values())
# Validate each narrowed Pigbarter quota against its old geographic predicate.
p='common/scripted_triggers/war_pigbarter_mission_triggers.txt'
old=parse(previous(p));new=parse(read(p))
control=lookup(new,'swine_controlled_province');assert sig(control.v)==sig(lookup(old,control.k).v)
assert sig(lookup(new,'swine_commercial_partner').v)==sig(lookup(old,'swine_commercial_partner').v)
for helper in old:
 if not helper.k.endswith('_settled'):continue
 before=[n for n,_ in walk(helper.v) if n.k=='calc_true_if']
 if not before:continue
 after=[n for n,_ in walk(lookup(new,helper.k).v) if n.k=='calc_true_if']
 assert len(before)==len(after)==1
 b,a=before[0],after[0];assert b.get('amount').v==a.get('amount').v
 world=b.get('all_province');geo=next((n for n in world.v if n.k in ('region','area')),None)
 if geo:expected=geography[geo.v]
 else:expected={n.v for n,_ in walk(lookup(old,'swine_vorag_hinterland').v) if n.k=='province_id'}
 inner=[n for n in a.v if n.k!='amount']
 if len(inner)==1 and inner[0].k in geography:
  actual=geography[inner[0].k];assert inner[0].has('type','all') and inner[0].has('swine_controlled_province','yes')
 else:
  actual={n.k for n in inner};assert all(n.has('swine_controlled_province','yes') for n in inner)
 assert expected==actual,helper.k
 print(f'PASS: {helper.k}: {len(actual)} geographically scoped provinces, quota {a.get("amount").v}')
# Country state boundary: the unchanged controlled helper permits direct owners or
# direct subjects with liberty desire strictly below 50, regardless of subject type.
assert any(n.k=='liberty_desire' and n.v=='50' and parents[-1].k=='NOT' for n,parents in walk(control.v))
print('PASS: Pigbarter control/loyalty and commercial-partner predicates are unchanged')

# Compare requested relation scopes to the old direct relationship clauses.
files=['02_Tomb_King_Missions.txt','00_Generic_missions_tomb_kings.txt','02_Nagashizzar_Missions.txt','02_Westerland_missions.txt','00_Generic_missions_dark_elf.txt','02_Nippon_missions.txt','02_Naggaroth_missions.txt','02_Greenskin_missions.txt','02_Hobgoblin_Khanate_missions.txt','02_Bretonnian_Missions.txt']
count=Counter()
for file in files:
 old=parse(previous('missions/'+file));new=parse(read('missions/'+file))
 for n,parents in walk(old):
  if n.k not in ('any_country','all_country') or not any(a.k in ('trigger','provinces_to_highlight') for a in parents):continue
  rel=next((k for k in ('is_subject_of','alliance_with','war_with') if n.has(k,'ROOT')),None)
  if not rel:continue
  suffix={'is_subject_of':'subject_country','alliance_with':'ally','war_with':'war_enemy_country'}[rel]
  replacement=n.k.split('_')[0]+'_'+suffix
  # Relationship scopes imply their corresponding ROOT check. Preserve other qualifiers;
  # an unfiltered ally quota can use the native num_of_allies counter.
  expected=[x for x in n.v if not (x.k==rel and x.v=='ROOT')]
  if not expected:
   assert rel=='alliance_with' and parents[-1].k=='calc_true_if'
   quota=parents[-1].get('amount').v
   assert any(x.k=='num_of_allies' and x.v==quota for x,_ in walk(new)),file
  else:
   assert any(x.k==replacement and sig(x.v)==sig(expected) for x,_ in walk(new)),(file,rel)
  count['highlight' if any(a.k=='provinces_to_highlight' for a in parents) else 'objective']+=1
assert count=={'objective':18,'highlight':3},count
print('PASS: all 18 relationship objectives and three associated highlight checks retain equivalent requirements without redundant relationship checks')

# Check the original geography-only optimization against its historical source.
# The later approved Nippon redesign changes homeland religion requirements;
# its current predicate/scenarios are covered by Nippon/validate_missions.py.
old_help=parse(previous('common/scripted_triggers/war_nippon_mission_triggers.txt'))
optimized_help=parse(previous('common/scripted_triggers/war_nippon_mission_triggers.txt','70790359'))
new_help=parse(read('common/scripted_triggers/war_nippon_mission_triggers.txt'))
old_home=next(n for n,_ in walk(lookup(old_help,'war_nippon_homeland_restored').v) if n.k=='any_province')
optimized_home=next(n for n,_ in walk(lookup(optimized_help,'war_nippon_homeland_restored').v) if n.k=='nippon_region')
new_home=next(n for n,_ in walk(lookup(new_help,'war_nippon_homeland_restored').v) if n.k=='nippon_region')
assert sig([n for n in old_home.v if n.k!='region'])==sig(optimized_home.v)
assert new_home.has('is_city','yes') and not new_home.has('type','all')
assert not any(n.k=='any_province' for n,_ in walk(lookup(new_help,'war_nippon_homeland_restored').v))
assert geography['nippon_region']=={p for p in all_provinces if p in regions['nippon_region']}
new_nippon=parse(read('missions/02_Nippon_missions.txt'))
assert not any(n.k=='any_province' for n,_ in walk(new_nippon))
# The redesigned missions replace some discovery objectives with city counts.
# Retain the original conversion checks on the optimization commit rather than
# requiring obsolete objectives to reappear in the live tree.
optimized_nippon=parse(previous('missions/02_Nippon_missions.txt','70790359'))
for continent in ['underempire','north_america','south_america']:
 assert continent in geography and geography[continent]
 assert any(n.k==continent and n.has('has_discovered','ROOT') for n,_ in walk(optimized_nippon))
for region in ['north_khuresh_region','south_khuresh_region']:
 assert any(n.k==region and n.has('has_port','yes') and n.has('has_discovered','ROOT') for n,_ in walk(optimized_nippon))
print('PASS: historical Nippon geographic conversions; current homeland stays regional and the live tree has no world-province searches')

mods={n.k for n in parse(read('common/event_modifiers/war_artifacts.txt')) if n.k.startswith('location_of_')}
ultimate=next(n for n,_ in walk(new_nippon) if n.k=='nippon_second_dawn')
quotas=[n for n,_ in walk(ultimate.get('trigger').v) if n.k=='calc_true_if'];assert len(quotas)==1
quota=quotas[0];assert quota.get('amount').v=='14'
checks=[n for n in quota.v if n.k!='amount']
assert len(checks)==len(mods)
assert all(n.k=='AND' and len(n.v)==1 and n.v[0].k=='any_owned_province' for n in checks)
assert {n.get('any_owned_province').get('has_province_modifier').v for n in checks}==mods
print('PASS: Nippon ultimate counts 14 distinct directly owned artifact identities, including stacked relics')

for folder,file in [('Nippon','02_Nippon_missions.txt'),('Swinetrade Empire','02_Pigbarter_missions.txt')]:
 ns=parse(read('missions/'+file));missions={n.k:n for n,_ in walk(ns) if isinstance(n.v,list) and n.has('icon') and n.has('trigger')}
 for m in json.loads(read('Dev Stuff/'+folder+'/mission_design.json'))['missions']:
  assert sig(parse(m['trigger']))==sig(missions[m['id']].get('trigger').v),m['id']
  if 'highlight' in m:assert sig(parse(m['highlight']))==sig(missions[m['id']].get('provinces_to_highlight').v),m['id']
assert (ROOT/'localisation/war_pigbarter_missions_l_english.yml').read_bytes().startswith(b'\xef\xbb\xbf')
print('PASS: both mission design sources match gameplay triggers/highlights; localisation retains UTF-8 BOM')

# Coordinator gates reject all but rank one, ahead of the world-wide completion check.
end=next(n for n in parse(read('events/end_times_events.txt')) if isinstance(n.v,list) and n.has('id','end_times_events.1999'))
gate=end.get('trigger');assert gate.has('is_great_power','yes')
rank=next(n for n in gate.v if n.k=='NOT' and n.has('great_power_rank','2'))
assert gate.v.index(rank)<next(i for i,n in enumerate(gate.v) if n.k=='all_province')
for r in range(1,21):assert ((r<=8) and not(r>=2))==(r==1)
oldend=next(n for n in parse(previous('events/end_times_events.txt')) if isinstance(n.v,list) and n.has('id','end_times_events.1999'))
assert sig(end.get('mean_time_to_happen').v)==sig(oldend.get('mean_time_to_happen').v)
assert sig(end.get('trigger').get('all_province').v)==sig(oldend.get('trigger').get('all_province').v)
ogre=parse(read('decisions/Ogre_decisions.txt'));assert not any(n.k=='any_country' for n,_ in walk(ogre))
print('PASS: one End Times coordinator, unchanged completion condition/timing, direct Great Feast owner lookup')
