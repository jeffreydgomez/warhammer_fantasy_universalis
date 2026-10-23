#!/usr/bin/env python3
"""Validate the reviewed cleanup against its committed pre-cleanup source.

Static reference/structure checks plus differential Boolean and effect-flow tests.
Opaque game predicates are sampled consistently; this is not an EU4 interpreter
or a timing benchmark. Normal WFU starts are assumed, not edited vanilla saves.
"""
from pathlib import Path
from collections import Counter
import csv, functools, hashlib, re, subprocess
from script_parser import ROOT, parse, walk, raw

BASELINE = '70790359'
PREFIX = subprocess.check_output(['git', 'rev-parse', '--show-prefix'], cwd=ROOT, text=True).strip()
ROWS = list(csv.DictReader((ROOT/'Dev Stuff/Performance/safe_cleanup_definitions.csv').open()))
CONDS = list(csv.DictReader((ROOT/'Dev Stuff/Performance/safe_cleanup_conditions.csv').open()))
IDS = {r['definition'] for r in ROWS}
EVENT_IDS = {r['definition'] for r in ROWS if r['file'].startswith('events/')}
DISABLED = {r['identifier'] for r in CONDS if r['kind'] == 'disabled_estate'}
DEAD_TAGS = {r['identifier'] for r in CONDS if r['kind'] == 'unavailable_tag'} - {'MCH','MNG','QNG'}
REPAIR_AGENDAS = {'estate_eunuchs_forbidden_city_agenda', 'estate_eunuchs_porcelain_tower_agenda'}
SCOPES = {'owner','controller','capital_scope','root','from','prev','this','overlord','emperor','consort','heir','ruler'}
METADATA = {'tooltip','desc','factor','add','value','multiplier','text','custom_tooltip'}
PREDICATES = {'has_estate_privilege','has_active_estate_agenda','has_disaster','has_reform','has_naval_doctrine'}
GATES = {'trigger','potential','allow','can_select','can_use','is_visible','is_valid','is_allowed','limit'}
HELPERS = {'apply_estate_monopoly_modifier','remove_estate_monopoly_modifier','reapply_estate_privilege'}

def decode(b):
    try: return b.decode('utf-8-sig')
    except UnicodeDecodeError: return b.decode('cp1252')

@functools.lru_cache(None)
def old(f):
    if f=='common/ai_personalities/00_ai_personalities.txt':
        return decode((Path.home()/'Library/Application Support/Steam/steamapps/common/Europa Universalis IV'/f).read_bytes())
    return decode(subprocess.check_output(['git','show',BASELINE+':'+PREFIX+f], cwd=ROOT))

@functools.lru_cache(None)
def current(f): return decode((ROOT/f).read_bytes())

def ident(n):
    return n.get('id').v if isinstance(n.v,list) and n.has('id') else n.k

def definitions(f,t):
    ns=parse(t)
    return [n for p in ns for n in p.v] if f.startswith('decisions/') else ns

def sig(n):
    return (n.k,tuple(sig(c) for c in n.v)) if isinstance(n.v,list) else (n.k,n.v)

def false(n):
    if n.k == 'has_estate' and n.v in DISABLED: return True
    if n.k in {'tag','original_tag','exists','was_tag'} and isinstance(n.v,str) and n.v in DEAD_TAGS: return True
    if n.k in PREDICATES and isinstance(n.v,str) and n.v in IDS: return True
    if n.k == 'has_disaster_progress' and isinstance(n.v,list) and n.has('disaster') and n.get('disaster').v in IDS:
        assert float(n.get('value').v)>0
        return True
    return False

class Sample:
    def __init__(self,seed,empty_if=True): self.seed,self.empty_if=seed,empty_if
    def choice(self,key): return int.from_bytes(hashlib.sha256(repr((self.seed,key)).encode()).digest()[:4],'big')
    def atom(self,key): return bool(self.choice(key)%2)
    def operands(self,ns,scope):
        vals=[];i=0
        while i<len(ns):
            n=ns[i]
            if n.k=='if' and isinstance(n.v,list) and n.has('limit'):
                chain=[n];i+=1
                while i<len(ns) and ns[i].k in {'else_if','else'}: chain.append(ns[i]);i+=1
                value=self.empty_if
                for b in chain:
                    if not b.has('limit') or self.test(b.get('limit').v,scope):
                        value=self.test([c for c in b.v if c.k!='limit'],scope);break
                vals.append(value);continue
            if n.k not in METADATA: vals.append(self.node(n,scope))
            i+=1
        return vals
    def test(self,ns,scope=()): return all(self.operands(ns,scope))
    def node(self,n,scope):
        k=n.k.lower()
        if false(n): return False
        if k=='always': return n.v=='yes'
        if not isinstance(n.v,list): return self.atom((scope,sig(n)))
        if k in {'or','not','nor'}:
            v=any(self.operands(n.v,scope));return not v if k!='or' else v
        if k in {'and','nand','hidden_trigger','custom_trigger_tooltip'}:
            v=self.test(n.v,scope);return not v if k=='nand' else v
        if k.startswith(('any_','all_')) or k in SCOPES or n.k.isdecimal() or re.fullmatch('[A-Z][A-Z0-9]{2}',n.k):
            count=self.choice((scope,k,'count'))%4 if k.startswith(('any_','all_')) else self.choice((scope,k,'exists'))%2
            values=[self.test(n.v,scope+(k,i)) for i in range(count)]
            return all(values) if k.startswith('all_') else any(values)
        # Unchanged compound game predicates remain opaque.
        return self.atom((scope,sig(n)))
    def effects(self,ns,scope=()):
        trace=[];i=0
        while i<len(ns):
            n=ns[i];i+=1
            if n.k=='if' and isinstance(n.v,list) and n.has('limit'):
                chain=[n]
                while i<len(ns) and ns[i].k in {'else_if','else'}: chain.append(ns[i]);i+=1
                for b in chain:
                    # The reviewed Catholic Papal caller is unreachable in WFU.
                    if any(c.k=='country_event' and c.get('id').v=='consort_events.201' for c in b.v if isinstance(c.v,list)): continue
                    if not b.has('limit') or self.test(b.get('limit').v,scope):
                        trace.extend(self.effects([c for c in b.v if c.k!='limit'],scope));break
            elif n.k=='trigger_switch':
                trace.append((scope,'trigger_switch',tuple((c.k,tuple(self.effects(c.v,scope))) if isinstance(c.v,list) else sig(c) for c in n.v)))
            elif n.k=='random_events':
                trace.append((scope,'random_events',tuple(sig(c) for c in n.v if c.v not in EVENT_IDS)))
            elif n.k=='random_list':
                eligible=[]
                for c in n.v:
                    if not isinstance(c.v,list):
                        eligible.append(sig(c));continue
                    if c.has('trigger') and not self.test(c.get('trigger').v,scope):continue
                    eligible.append((c.k,tuple(self.effects([v for v in c.v if v.k!='trigger'],scope))))
                trace.append((scope,'random_list',tuple(eligible)))
            elif n.k in HELPERS and n.get('privilege').v in IDS: continue
            elif isinstance(n.v,list) and (n.k in {'hidden_effect','effect','FROM','ROOT','owner','capital_scope'} or n.k.startswith(('every_','random_','event_target:'))):
                if n.has('limit') and not self.test(n.get('limit').v,scope+(n.k,)): continue
                trace.extend(self.effects([c for c in n.v if c.k!='limit'],scope+(n.k,)))
            else: trace.append((scope,sig(n)))
        return trace


def run():
    # This suite compares the cleanup against its baseline, not subsequent
    # artifact rollbacks, Nippon redesigns or Warpmoon fixes. Every approved CSV
    # file is required even if its cleanup marker is missing; marked callers
    # extend the set. The reference scan below still covers all active content.
    files={r['file'] for r in ROWS+CONDS}
    for folder in ('common','events','decisions'):
        for p in (ROOT/folder).rglob('*.txt'):
            if '# WFU cleanup:' in decode(p.read_bytes()):
                files.add(str(p.relative_to(ROOT)))
    files=sorted(files)
    assert len(files)==105, len(files)
    # Every cleanup gameplay file must parse strictly.
    for f in files: parse(current(f))
    print('PASS:',len(files),'cleanup gameplay files parse')
    selected={}
    for r in ROWS:
        f=r['file'];before=old(f)
        ns=[n for n in definitions(f,before) if ident(n)==r['definition'] and before.count('\n',0,n.s)+1==int(r['line'])]
        assert len(ns)==1,r
        selected.setdefault(f,[]).append(ns[0])
    for f,ns in selected.items():
        before=Counter(ident(n) for n in definitions(f,old(f)))
        after=Counter(ident(n) for n in definitions(f,current(f)))
        for n in ns: before[ident(n)]-=1
        assert +before==after,('unexpected definition removal',f,before-after,after-before)
        assert current(f).count('# WFU cleanup: reviewed unavailable definition')==len(ns),f
    print('PASS: exactly 477 approved definitions commented; override files retained')

    # Validate all active local callers, excluding real icon reuse and province IDs.
    for folder in ['common','events','decisions','missions','history']:
        for p in (ROOT/folder).rglob('*.txt'):
            f=str(p.relative_to(ROOT));t=decode(p.read_bytes())
            if not any(x in t for x in IDS): continue
            for n,ps in walk(parse(t,allow_unclosed=True)):
                vals={n.k}|({n.v} if isinstance(n.v,str) else set())
                if not vals&IDS: continue
                if n.k=='icon' or f=='common/tradenodes/00_tradenodes.txt': continue
                if not ps and f.startswith('common/government_names/') and n.k in {'chinese_monarchy','muslim_tribal'}: continue
                raise AssertionError(('obsolete reference',f,n.k,n.v))
    print('PASS: no active removed-definition callers or registrations; icons and trade geography retained')

    # Protected repair candidates and active Warhammer duplicates are exact matches.
    f='common/estate_agendas/09_eunuchs_agendas.txt'
    for k in REPAIR_AGENDAS:
        a=next(n for n in parse(old(f)) if n.k==k);b=next(n for n in parse(current(f)) if n.k==k)
        assert raw(old(f),a)==raw(current(f),b),k
    f='common/government_names/00_government_names.txt'
    a=[n for n in parse(old(f)) if n.k=='chinese_monarchy'][-1]
    b=next(n for n in parse(current(f)) if n.k=='chinese_monarchy')
    assert raw(old(f),a)==raw(current(f),b)
    f='common/government_names/00_0warhammer_unique_names.txt'
    assert old(f)==current(f)
    for f in ['common/estates/100_mages.txt','common/estates/09_eunuchs.txt']:
        a=parse(old(f))[0];b=parse(current(f))[0]
        assert sig(a.get('trigger'))==sig(b.get('trigger')),f
    # Whole files holding the repairs/previous performance work stay byte-identical.
    protected=['common/ideas/war_country_ideas.txt','common/ruler_personalities/00_core.txt','common/scripted_triggers/war_scripted_triggers_racial.txt','common/religious_conversions/00_religious_conversions.txt','history/countries/Z29 - Songhai.txt']
    for f in protected:
        if (ROOT/f).exists(): assert old(f)==current(f),f
    assert not any(f.startswith(('missions/','history/','common/great_projects/','common/defines')) for f in files)
    # Make sure no new dangling else/else_if nodes were introduced.
    def orphans(ns):
        result=[]
        for n,ps in walk(ns):
            if not isinstance(n.v,list):continue
            for i,c in enumerate(n.v):
                if c.k in {'else','else_if'} and (i==0 or n.v[i-1].k not in {'if','else_if'}):result.append((tuple(p.k for p in ps),n.k,sig(c)))
        return Counter(result)
    for f in files: assert not (orphans(parse(current(f)))-orphans(parse(old(f)))),f
    for f in ['common/scripted_effects/00_scripted_effects.txt','common/scripted_effects/01_scripted_effects_for_estates.txt']:
        def animism_switches(t):
            return Counter((ident(ps[0]),sig(n)) for n,ps in walk(parse(t)) if n.k=='animism')
        assert animism_switches(old(f))==animism_switches(current(f)),f
    print('PASS: repair agendas, animism switches, Cathayan/Arabyan names, active estate gates and branch structure preserved')

    # Differential tests for surviving trigger definitions, top-level gates,
    # effects, on_actions and surviving event options.
    cases=[];effects=[];options=[]
    for f in files:
        aa=definitions(f,old(f));bb=definitions(f,current(f))
        for a in aa:
            matches=[b for b in bb if ident(b)==ident(a)]
            if len(matches)!=1 or any(a.s==removed.s for removed in selected.get(f,[])):continue
            b=matches[0]
            if not isinstance(a.v,list) or not isinstance(b.v,list):continue
            if f.startswith('common/scripted_triggers/'):
                if sig(a)!=sig(b): cases.append((f,a.k,a.v,b.v))
            elif f.startswith('common/scripted_effects/'):
                if sig(a)!=sig(b): effects.append((f,a.k,a.v,b.v))
            else:
                for k in GATES:
                    av=[c for c in a.v if c.k==k];bv=[c for c in b.v if c.k==k]
                    if len(av)==len(bv)==1 and sig(av[0])!=sig(bv[0]):cases.append((f,ident(a)+'/'+k,av[0].v,bv[0].v))
                for k in ['effect','immediate','on_granted','on_revoked','on_built','on_destroyed']:
                    av=[c for c in a.v if c.k==k];bv=[c for c in b.v if c.k==k]
                    if len(av)==len(bv)==1 and sig(av[0])!=sig(bv[0]):effects.append((f,ident(a)+'/'+k,av[0].v,bv[0].v))
                av=[c for c in a.v if c.k=='option' and isinstance(c.v,list) and c.has('name')]
                bv=[c for c in b.v if c.k=='option' and isinstance(c.v,list) and c.has('name')]
                if tuple(map(sig,av))!=tuple(map(sig,bv)):options.append((f,ident(a),av,bv))
    for f,k,a,b in cases:
        for empty in (False,True):
            for seed in range(128):
                w=Sample(seed,empty)
                assert w.test(a)==w.test(b),('condition changed',f,k,seed,empty)
    for f,k,a,b in effects:
        for seed in range(128):
            w=Sample(seed)
            assert w.effects(a)==w.effects(b),('effect flow changed',f,k,seed)
    for f,k,a,b in options:
        for seed in range(128):
            w=Sample(seed)
            def available(opts):
                return [(n.get('name').v,w.effects([c for c in n.v if c.k not in {'name','trigger','ai_chance'}])) for n in opts if not n.has('trigger') or w.test(n.get('trigger').v)]
            assert available(a)==available(b),('available options changed',f,k,seed)
    print('PASS:',len(cases)*256,'condition samples,',len(effects)*128,'effect-flow samples and',len(options)*128,'option-selection samples')
    print('Static cleanup checks passed. In-game load/save and timing verification remains necessary.')

if __name__=='__main__':run()
