#!/usr/bin/env python3
"""Script-driven regressions for cache lifecycles and narrowed mission conditions.
This is a limited interpreter, not EU4: unsupported conditions/effects fail loudly.
Run from any directory. Original scripts come from the commit before this change.
"""
from pathlib import Path
from collections import Counter
import copy,itertools,subprocess,random
from script_parser import ROOT,parse,walk,read,raw
BASELINE='85be098c'
PREFIX=subprocess.check_output(['git','rev-parse','--show-prefix'],cwd=ROOT,text=True).strip()
def baseline(path):return subprocess.check_output(['git','show',BASELINE+':'+PREFIX+path],cwd=ROOT).decode('utf-8-sig')
def defs(text):return {n.k:n for n in parse(text)}
TRIGGER_TEXT=read('common/scripted_triggers/war_artifact_triggers.txt')+'\n'+read('common/scripted_triggers/war_pigbarter_mission_triggers.txt')
EFFECT_TEXT=read('common/scripted_effects/war_artifact_effects.txt')
TRIGGERS=defs(TRIGGER_TEXT); EFFECTS=defs(EFFECT_TEXT)
MODS=[n.k for n in parse(read('common/event_modifiers/war_artifacts.txt')) if n.k.startswith('location_of_')]
def expanded(text,n,args):
 s=text[n.body:n.e-1]
 if isinstance(args,list):
  for a in args:s=s.replace('$'+a.k+'$',a.v)
 assert '$' not in s,('unresolved argument',n.k,s)
 return parse(s)
def body(n):return n.v
class World:
 def __init__(self):
  self.countries={k:dict(id=k,mods=set(),flags=set(),allies=set(),overlord=None,trust=50) for k in ['root','from','third']}
  self.provinces={str(i):dict(id=str(i),owner=o,controller=o,mods=set(),siege=False,neighbors=set()) for i,o in [(1,'root'),(2,'from'),(3,'root'),(4,None),(5,'third')]}
  self.countries['root']['capital']='1';self.countries['from']['capital']='2';self.countries['third']['capital']='5'
  self.provinces['1']['neighbors']={'3','4'}
  self.provinces['4']['neighbors']={'1'}
  self.targets={};self.flags=set();self.log=[];self.scans=0
 def resolve(self,k,scope):
  if k in ('ROOT','FROM'):return ('c',k.lower())
  if k=='THIS':return scope
  if k.startswith('event_target:'):
   assert k[13:] in self.targets,('missing target dereference',k)
   return self.targets[k[13:]]
  if k.isdecimal():return ('p',k)
  raise AssertionError(('unhandled reference',k))
 def obj(self,s):return (self.countries if s[0]=='c' else self.provinces)[s[1]]
 def pool(self,k,s):
  if k in ('every_province','any_province','all_province'):self.scans+=1;return [('p',p) for p in self.provinces]
  if k in ('every_country','random_country','all_country','any_country'):return [('c',c) for c in self.countries]
  if k in ('every_owned_province','any_owned_province','all_owned_province'):return [('p',p) for p,x in self.provinces.items() if x['owner']==s[1]]
  if k in ('any_empty_neighbor_province','every_empty_neighbor_province'):return [('p',p) for p in self.obj(s)['neighbors'] if self.provinces[p]['owner'] is None]
  if k in ('all_ally','any_ally'):return [('c',c) for c in self.obj(s)['allies']]
  if k=='all_subject_country':return [('c',c) for c,x in self.countries.items() if x['overlord']==s[1]]
  raise AssertionError(('unhandled pool',k))
 def scoped(self,k,s):
  o=self.obj(s)
  if k=='owner':return ('c',o['owner']) if o['owner'] else None
  if k=='capital_scope':return ('p',o['capital'])
  return self.resolve(k,s)
 def test(self,ns,s=('c','root')):
  answers=[];branch=False
  for n in ns:
   k,v=n.k,n.v;o=self.obj(s)
   if k in ('tooltip','amount','type'):continue
   if k=='if':
    branch=self.test(n.get('limit').v,s)
    answer=self.test([c for c in v if c.k!='limit'],s) if branch else True
   elif k=='else':answer=True if branch else self.test(v,s)
   elif k in ('AND','hidden_trigger','custom_trigger_tooltip'):answer=self.test(v,s)
   elif k=='OR':answer=any(self.test([c],s) for c in v)
   elif k=='NOT':answer=not self.test(v,s)
   elif k=='always':answer=v=='yes'
   elif k in TRIGGERS:answer=self.test(expanded(TRIGGER_TEXT,TRIGGERS[k],v),s)==(v!='no')
   elif k=='has_saved_event_target':answer=v in self.targets
   elif k=='has_global_flag':answer=v in self.flags
   elif k in ('has_province_modifier','has_country_modifier'):answer=v in o['mods']
   elif k=='has_ruler_flag':answer=v in o.get('flags',set())
   elif k in ('owned_by','controlled_by'):answer=o['owner' if k=='owned_by' else 'controller']==self.resolve(v,s)[1]
   elif k=='province_id':answer=s==self.resolve(v,s)
   elif k=='is_capital':answer=(o['owner'] is not None and self.countries[o['owner']]['capital']==s[1])==(v=='yes')
   elif k=='has_siege':answer=o['siege']==(v=='yes')
   elif k=='exists':answer=v=='yes' and any(p['owner']==s[1] for p in self.provinces.values())
   elif k=='alliance_with':answer=self.resolve(v,s)[1] in o['allies']
   elif k=='is_subject_of':answer=o['overlord']==self.resolve(v,s)[1]
   elif k=='trust':answer=o['trust']>=int(n.get('value').v)
   elif k=='calc_true_if':
    count=0
    for c in v:
     if c.k=='amount':continue
     if c.k.startswith('all_'):count+=sum(self.test(c.v,x) for x in self.pool(c.k,s))
     else:count+=self.test([c],s)
    answer=count>=int(n.get('amount').v)
   elif k.startswith(('any_','all_')):
    fn=any if k.startswith('any_') else all;answer=fn(self.test(v,x) for x in self.pool(k,s))
   elif k in ('ROOT','FROM','owner','capital_scope') or k.startswith('event_target:') or k.isdecimal():
    target=self.scoped(k,s);answer=target is not None and self.test(v,target)
   else:raise AssertionError(('unhandled trigger',k))
   answers.append(answer)
  return all(answers)
 def effect(self,ns,s=('c','root')):
  branch=False
  for n in ns:
   k,v=n.k,n.v;o=self.obj(s)
   if k=='if':
    branch=self.test(n.get('limit').v,s)
    if branch:self.effect([x for x in v if x.k!='limit'],s)
   elif k=='else':
    if not branch:self.effect(v,s)
   elif k in EFFECTS:self.effect(expanded(EFFECT_TEXT,EFFECTS[k],v),s)
   elif k in ('effect','on_accept','hidden_effect'):self.effect(v,s)
   elif k=='custom_tooltip':pass
   elif k=='save_global_event_target_as':self.targets[v]=s
   elif k=='clear_global_event_target':self.targets.pop(v,None)
   elif k=='set_global_flag':self.flags.add(v)
   elif k in ('add_permanent_province_modifier','add_country_modifier'):o['mods'].add(n.get('name').v)
   elif k in ('remove_province_modifier','remove_country_modifier'):o['mods'].discard(v)
   elif k in ('every_province','every_owned_province','every_empty_neighbor_province','random_country'):
    candidates=[x for x in self.pool(k,s) if not n.has('limit') or self.test(n.get('limit').v,x)]
    if k=='random_country':candidates=candidates[:1]
    for x in candidates:self.effect([c for c in v if c.k!='limit'],x)
   elif k in ('ROOT','FROM','owner','capital_scope') or k.startswith('event_target:'):
    target=self.scoped(k,s)
    if target is not None:self.effect(v,target)
   elif k in ('country_event','kill_ruler','add_manpower','add_treasury','add_favors'):
    signature=tuple((c.k,c.v) for c in v) if isinstance(v,list) else v
    self.log.append((s,k,signature))
   else:raise AssertionError(('unhandled effect',k))
 def initialize(self):self.effect(EFFECTS['war_initialize_artifact_locations'].v)
 def visible_state(self):return (self.provinces,self.countries,self.flags-{'war_artifact_locations_initialized_v1'},self.log)

new_decisions=defs(read('decisions/Artifact_decisions.txt'))['country_decisions']
old_decisions=defs(baseline('decisions/Artifact_decisions.txt'))['country_decisions']
# A pre-cache save can already have moved artifacts. Initialization finds real locations,
# including unowned land; subsequent calls do not scan again or respawn consumed relics.
w=World()
for i,m in enumerate(MODS[:22]):w.provinces[str(i%5+1)]['mods'].add(m)
w.countries['from']['mods'].add('nagash_resurrected_modifier');w.initialize()
for m in MODS[:22]:assert m in w.obj(w.targets['war_'+m])['mods']
assert w.scans==1
w.initialize();assert w.scans==1
assert w.targets['war_nagash_holder']==('c','from')
for m in MODS[22:]:assert not w.test(parse(f'war_artifact_owned_by = {{ ARTIFACT = {m} COUNTRY = ROOT }}'))
# Target exists but modifier has gone: the cache cannot produce a false positive.
m=MODS[0];w.obj(w.targets['war_'+m])['mods'].remove(m)
assert not w.test(parse(f'war_artifact_owned_by = {{ ARTIFACT = {m} COUNTRY = ROOT }}'))
print('PASS: one migration scan, idempotence, missing/consumed artifacts, and existing Nagash holder')

capture_count=0
for decision in new_decisions.v:
 if not decision.k.startswith('take_'):continue
 mods={x.v for x,_ in walk(decision.get('effect').v) if x.k=='remove_province_modifier'};assert len(mods)==1
 m=mods.pop()
 for pid in ('2','4'):
  old=World();old.provinces[pid]['mods'].add(m);new=copy.deepcopy(old);new.initialize();new.scans=0
  old.effect(old_decisions.get(decision.k).get('effect').v);new.effect(decision.get('effect').v)
  assert old.visible_state()==new.visible_state(),decision.k
  assert new.targets['war_'+m]==('p','1') and new.scans==0
  assert new.test(parse(f'war_artifact_owned_by = {{ ARTIFACT = {m} COUNTRY = ROOT }}'))
  # Conquest automatically changes the holder without touching the province target.
  new.provinces['1']['owner']='from'
  assert not new.test(parse(f'war_artifact_owned_by = {{ ARTIFACT = {m} COUNTRY = ROOT }}'))
  capture_count+=1
print('PASS:',capture_count,'capture/conquest scenarios preserve modifiers, ruler effects and notifications')

old_dip=defs(baseline('common/new_diplomatic_actions/00_war_artifacts.txt'))
new_dip=defs(read('common/new_diplomatic_actions/00_war_artifacts.txt'))
for k,n in new_dip.items():
 m=next(x.v for x,_ in walk(n.get('on_accept').v) if x.k=='remove_province_modifier')
 old=World();source='1' if k.startswith('dip_gift_') else '2';old.provinces[source]['mods'].add(m)
 new=copy.deepcopy(old);new.initialize();new.scans=0
 old.effect(old_dip[k].get('on_accept').v);new.effect(n.get('on_accept').v)
 assert old.visible_state()==new.visible_state(),k
 expected='2' if k.startswith('dip_gift_') else '1'
 assert new.targets['war_'+m]==('p',expected) and new.scans==0
print('PASS:',len(new_dip),'request/gift actions preserve favors, penalties and destinations')

for pid,siege,neighbor in itertools.product(('1','2','3','4','5'),(False,True),(False,True)):
 old=World();m=MODS[0];old.provinces[pid]['mods'].add(m);old.provinces[pid]['siege']=siege
 old.provinces['1']['neighbors']={'4'} if neighbor else set()
 new=copy.deepcopy(old);new.initialize();new.scans=0
 old.effect(old_decisions.get('relocate_artifacts').get('effect').v)
 new.effect(new_decisions.get('relocate_artifacts').get('effect').v)
 assert old.visible_state()==new.visible_state(),(pid,siege,neighbor)
 dest=next(p for p,x in new.provinces.items() if m in x['mods'])
 assert new.targets['war_'+m]==('p',dest) and new.scans==0
# The Grail remains excluded from relocation, as in the previous script.
w=World();w.provinces['3']['mods'].add('location_of_the_grail');w.initialize()
w.effect(new_decisions.get('relocate_artifacts').get('effect').v)
assert 'location_of_the_grail' in w.provinces['3']['mods']
print('PASS: 40 relocation cases cover capitals, siege, ownership and empty neighbors; Grail exception preserved')

old=World()
ritual=old_decisions.get('resurrect_nagash_decision').get('effect')
consumed=[n.v for n,_ in walk(ritual.v) if n.k=='remove_province_modifier']
for m in consumed:old.provinces['3']['mods'].add(m)
new=copy.deepcopy(old);new.initialize();new.scans=0
old.effect(ritual.v);new.effect(new_decisions.get('resurrect_nagash_decision').get('effect').v)
assert old.visible_state()==new.visible_state()
assert new.scans==0 and new.targets['war_nagash_holder']==('c','root')
assert all('war_'+m not in new.targets for m in consumed)
# Change Nagash's capital and occupier, then evaluate another country's destruction decision.
w=World();w.countries['from']['mods'].add('nagash_resurrected_modifier');w.initialize()
w.countries['from']['capital']='5';w.provinces['5']['controller']='root'
assert w.test(new_decisions.get('destroy_nagash').get('allow').v)
w.provinces['5']['controller']='from';assert not w.test(new_decisions.get('destroy_nagash').get('allow').v)
w.effect(new_decisions.get('destroy_nagash').get('effect').v);assert 'war_nagash_holder' not in w.targets
# Grail appearance after startup supplies the absent location.
w=World();w.initialize()
grail_event=next(n for n in parse(read('events/Bretonnia.txt')) if isinstance(n.v,list) and any(x.k=='name' and x.v=='location_of_the_grail' for x,_ in walk(n.v)))
w.effect(grail_event.get('option').get('capital_scope').v,('p','1'))
assert w.targets['war_location_of_the_grail']==('p','1')
print('PASS: resurrection consumes five locations; Nagash follows his current capital; later Grail discovery is indexed')

# Exhaust the ally/subject intersection and trust boundary: a country counts once.
for quota,trust in [(2,60),(3,90),(4,75)]:
 for states in itertools.product(range(5),repeat=4):
  w=World();w.countries={k:v for k,v in w.countries.items() if k=='root'}
  eligible=0
  for i,state in enumerate(states):
   c=str(i);ally=state in (1,3);subject=state in (2,3);value=trust if state!=4 else trust-1
   w.countries[c]=dict(id=c,allies={'root'} if ally else set(),overlord='root' if subject else None,trust=value)
   if ally:w.countries['root']['allies'].add(c)
   eligible+=bool((ally or subject) and value>=trust)
  assert w.test(parse(f'swine_trusted_partners_{quota}_{trust} = yes'))==(eligible>=quota),(quota,states)
print('PASS: 1,875 ally/subject quota cases, including unrelated high-trust countries and double-count protection')

# Province quota narrowing preserves exact tiers and direct/subject ownership.
old=defs(baseline('missions/02_Tomb_King_Missions.txt'));new=defs(read('missions/02_Tomb_King_Missions.txt'))
project_locations={n.k:n.get('start').v for n in parse(read('common/great_projects/01_southland_monuments.txt')) if isinstance(n.v,list) and n.has('start')}
old_counts=[n for n,_ in walk(list(old.values())) if n.k=='calc_true_if' and n.has('all_province')]
new_counts=[n for n,_ in walk(list(new.values())) if n.k=='calc_true_if' and any(x.k.isdecimal() for x in n.v)]
assert len(old_counts)==len(new_counts)==10
rng=random.Random(734)
for previous,current in zip(old_counts,new_counts):
 assert previous.get('amount').v==current.get('amount').v
 prs=[x for x,_ in walk(previous.v) if x.k=='has_great_project']
 assert {x.k for x in current.v if x.k!='amount'}=={project_locations[x.get('type').v] for x in prs}
 for _ in range(100):
  states={x.get('type').v:(rng.randrange(4),rng.choice(['root','subject','foreign','empty'])) for x in prs}
  a=sum(states[x.get('type').v][0]==int(x.get('tier').v) and states[x.get('type').v][1] in ('root','subject') for x in prs)
  b=0
  for x in current.v:
   if x.k=='amount':continue
   pr=x.get('has_great_project');tier,owner=states[pr.get('type').v]
   assert x.get('OR').has('owned_by','ROOT') and x.get('OR').has('owned_by_subject_of','ROOT')
   b+=tier==int(pr.get('tier').v) and owner in ('root','subject')
  assert a==b
print('PASS: 1,000 monument states retain exact tiers, quotas and subject eligibility')
# The permanent artifact histories contain no duplicated artifact identities.
history_counts=Counter()
for p in (ROOT/'history/provinces').glob('*.txt'):
 for n,_ in walk(parse(p.read_text(encoding='utf-8-sig',errors='replace'))):
  if n.k=='name' and n.v in MODS:history_counts[n.v]+=1
assert all(n==1 for n in history_counts.values())
print('PASS: starting artifact identities are unique')
print('All performance regression checks passed. In-engine timing and save/load testing still required.')
