"""AST-identical physical-line formatting; never changes the original submission.

This is a manual usability repair, NOT evidence of original model compliance.
"""
import argparse,ast,hashlib,json
from pathlib import Path
def compact(code,limit):
 tree=ast.parse(code);lines=ast.unparse(tree).splitlines();out=[]
 simple=(ast.Assign,ast.AnnAssign,ast.AugAssign,ast.Expr,ast.Return,ast.Raise,ast.Assert,ast.Pass,ast.Break,ast.Continue,ast.Delete,ast.Import,ast.ImportFrom,ast.Global,ast.Nonlocal)
 def ok(text):
  try:return all(isinstance(n,simple) for n in ast.parse(text.strip()).body)
  except SyntaxError:return False
 for i,line in enumerate(lines):
  prev=out[-1] if out else ''
  if out and len(out)+len(lines)-i>=limit and len(line)-len(line.lstrip())==len(prev)-len(prev.lstrip()) and ok(prev) and ok(line):out[-1]=prev+'; '+line.lstrip()
  else:out.append(line)
 text='\n'.join(out)+'\n'
 # Inline simple suites only when a full-tree equality check proves semantics unchanged.
 while len(text.splitlines()) >= limit:
  lines=text.splitlines();changed=False
  for i in range(len(lines)-2,-1,-1):
   if not lines[i].rstrip().endswith(':'):continue
   indent=len(lines[i])-len(lines[i].lstrip());j=i+1
   while j<len(lines) and len(lines[j])-len(lines[j].lstrip())>indent:j+=1
   body=lines[i+1:j]
   if not body or any(len(x)-len(x.lstrip())!=indent+4 for x in body) or not all(ok(x) for x in body):continue
   candidate='\n'.join(lines[:i]+[lines[i]+' '+'; '.join(x.strip() for x in body)]+lines[j:])+'\n'
   try:equal=ast.dump(tree)==ast.dump(ast.parse(candidate))
   except SyntaxError:equal=False
   if equal:text=candidate;changed=True;break
  if not changed:raise ValueError('Cannot meet physical-line limit using permitted AST-identical formatting')
 assert ast.dump(tree)==ast.dump(ast.parse(text));assert len(text.splitlines())<limit
 return text
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('destination',type=Path);p.add_argument('--limit',type=int,default=240);a=p.parse_args();assert not a.destination.exists();o=json.loads(a.source.read_text());old=o['code'];o.update(code=compact(old,a.limit),repair_type='AST_identical_format_only',patch_description=o.get('patch_description','')+' Mechanical AST-identical physical-line formatting; original format violation remains historical.',AST_equivalent=True,parent_submission_file=str(a.source),parent_submission_sha256=hashlib.sha256(a.source.read_bytes()).hexdigest(),AST_sha256=hashlib.sha256(ast.dump(ast.parse(old)).encode()).hexdigest());a.destination.parent.mkdir(parents=True,exist_ok=True);a.destination.write_text(json.dumps(o,indent=2)+'\n');print('AST identical:',len(old.splitlines()),'->',len(o['code'].splitlines()),'lines')
