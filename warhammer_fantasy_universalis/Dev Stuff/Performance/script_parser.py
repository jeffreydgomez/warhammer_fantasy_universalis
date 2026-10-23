from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[2]
TOKEN=re.compile(r'\s+|\#[^\n]*|"(?:\\.|[^"\\])*"|[{}]|[<>!=?]+|[^\s{}=<>!?#"]+')
class Node:
 def __init__(self,k,v,s,e,body=None): self.k,self.v,self.s,self.e,self.body=k,v,s,e,body
 def get(self,k):
  a=[n for n in self.v if n.k==k]; assert len(a)==1,(self.k,k,len(a)); return a[0]
 def has(self,k,v=None): return any(n.k==k and (v is None or n.v==v) for n in self.v)
def parse(text, allow_unclosed=False):
 ts=[m for m in TOKEN.finditer(text) if not m[0].isspace() and not m[0].startswith('#')]; i=0
 def block(nested=False):
  nonlocal i
  out=[]
  while i<len(ts):
   a=ts[i]; i+=1
   if a[0]=='}':
    if not nested:
     assert allow_unclosed, 'unmatched closing brace'
     continue
    return out,a.end()
   assert a[0]!='{',(a.start(),text[max(0,a.start()-120):a.start()+120])
   if i<len(ts) and ts[i][0] in ('=','<','>','>=','<=','!=','?='):
    i+=1; val=ts[i]; i+=1; body=None
    if val[0]=='{': body=val.end(); v,end=block(True)
    else: v,end=val[0].strip('"'),val.end()
    out.append(Node(a[0],v,a.start(),end,body))
   elif i<len(ts) and ts[i][0]=='{':
    body=ts[i].end(); i+=1;v,end=block(True);out.append(Node(a[0],v,a.start(),end,body))
   else: out.append(Node(a[0],None,a.start(),a.end()))
  assert not nested or allow_unclosed,'unclosed block'
  return out,len(text)
 return block()[0]
def walk(nodes,parents=()):
 for n in nodes:
  yield n,parents
  if isinstance(n.v,list): yield from walk(n.v,parents+(n,))
def read(path):return (ROOT/path).read_text(encoding='utf-8-sig')
def write(path,text):
 p=ROOT/path; bom=p.exists() and p.read_bytes().startswith(b'\xef\xbb\xbf'); p.write_text(text,encoding='utf-8-sig' if bom else 'utf-8')
def apply(text,edits):
 last=len(text)
 for a,b,v in sorted(edits,reverse=True): assert b<=last,(a,b,last);text=text[:a]+v+text[b:]; last=a
 parse(text);return text
def indent(text,n):return re.match(r'[\t ]*',text[text.rfind('\n',0,n.s)+1:]).group()
def raw(text,n):return text[n.s:n.e]
