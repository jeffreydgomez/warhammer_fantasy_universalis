#!/usr/bin/env python3
"""Check artifact rollback integrity and the reported decision visibility cases.
Static script checks only; this does not emulate EU4's event-target implementation.
"""
import itertools,re,subprocess
from script_parser import ROOT,parse,walk,read
BASELINE='85be098c'
RESTORED=['decisions/Artifact_decisions.txt','common/new_diplomatic_actions/00_war_artifacts.txt','common/scripted_effects/war_artifact_effects.txt','common/on_actions/war_startup_on_actions.txt','events/Bretonnia.txt','missions/00_Generic_missions_high_elves.txt','missions/01_Generic_missions_vampire.txt','missions/02_Asur_missions.txt','missions/02_Dwarf_missions.txt']
CACHE=re.compile(r'\b(?:war_artifact_(?:owned_by|controlled_by|holder_relation|can_relocate|locations_initialized_v1)|war_initialize_artifact_locations|war_relocate_artifact|war_nagash_holder(?:_exists)?|war_location_of_\w+)\b')

class DecisionWorld:
 def __init__(self,holder,neighbor,enemy,skaven,occupied):
  self.holder=holder;self.neighbor=neighbor;self.enemy=enemy;self.skaven=skaven;self.occupied=occupied
  self.provinces={'capital':('root','root'),'other_owned':('root','root'),'foreign':('other','root' if occupied else 'other')}
 def test(self,ns,scope='root'):
  return all(self.node(n,scope) for n in ns)
 def node(self,n,scope):
  k,v=n.k,n.v
  if k=='OR':return any(self.node(c,scope) for c in v)
  if k=='NOT':return not any(self.node(c,scope) for c in v)
  if k=='ai':return v=='no'
  if k=='is_at_war':return self.enemy==(v=='yes')
  if k=='technology_group':return self.skaven and v=='tech_skaven'
  if k=='has_province_modifier':return scope==self.holder and v=='location_of_the_fellblade'
  if k=='controlled_by':return self.provinces[scope][1]=='root'
  if k=='capital_scope':return self.test(v,'capital')
  if k in {'any_neighbor_country','any_war_enemy_country'}:
   return (self.neighbor if k=='any_neighbor_country' else self.enemy) and self.test(v,'other')
  if k in {'any_owned_province','all_owned_province','any_province'}:
   ps=[p for p,(owner,controller) in self.provinces.items() if k=='any_province' or owner==scope]
   return (all if k=='all_owned_province' else any)(self.test(v,p) for p in ps)
  raise AssertionError(('unsupported condition',k))

def validate():
 prefix=subprocess.check_output(['git','rev-parse','--show-prefix'],cwd=ROOT,text=True).strip()
 for f in RESTORED:
  original=subprocess.check_output(['git','show',BASELINE+':'+prefix+f],cwd=ROOT)
  assert (ROOT/f).read_bytes()==original,('not an exact rollback',f)
  parse(read(f))
 assert not (ROOT/'common/scripted_triggers/war_artifact_triggers.txt').exists()
 for folder in ['common','events','decisions','missions']:
  for p in (ROOT/folder).rglob('*.txt'):
   text=p.read_text(encoding='utf-8-sig',errors='replace')
   assert not CACHE.search(text),('cache reference remains',p)
 for f in ['missions/02_Nagashizzar_Missions.txt','missions/02_Naggaroth_missions.txt']:parse(read(f))
 print('PASS: exact rollback of 9 artifact-only files; no artifact-cache hooks or callers remain')
 decisions=parse(read('decisions/Artifact_decisions.txt'))[0]
 take=[n for n in decisions.v if n.k.startswith('take_')]
 for n in take:
  own=n.get('potential').get('all_owned_province').get('NOT').get('has_province_modifier').v
  assert n.get('allow').get('any_province').has('has_province_modifier',own),n.k
  for relation in ['any_neighbor_country','any_war_enemy_country']:
   refs=[c for c,ps in walk(n.get('potential').v) if c.k==relation]
   assert len(refs)==1 and refs[0].get('any_owned_province').has('has_province_modifier',own),n.k
 print('PASS:',len(take),'capture decisions check actual ownership, neighbors, war enemies and occupation')
 fellblade=decisions.get('take_the_fellblade');cases=0
 for holder,neighbor,enemy,skaven,occupied in itertools.product(['capital','other_owned','foreign',None],[False,True],[False,True],[False,True],[False,True]):
  w=DecisionWorld(holder,neighbor,enemy,skaven,occupied)
  expected=holder not in {'capital','other_owned'} and (skaven or holder=='foreign' and (neighbor or enemy))
  assert w.test(fellblade.get('potential').v)==expected,(holder,neighbor,enemy,skaven)
  assert w.test(fellblade.get('allow').v)==(holder in {'capital','other_owned'} or holder=='foreign' and occupied)
  cases+=1
 print('PASS:',cases,'Fellblade ownership/neighbor/war/occupation cases, including the reported regressions')

if __name__=='__main__':validate()
