from pathlib import Path
import json,hashlib,shutil
R=Path('/workspace/github-delivery-01/wiki-data');B='数学2026_哈语学生_哈语教材（4-2）_АЛМАТЫКІТАП';T=R/(B+'_数据')
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def item(p,root):return {'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
for script in ['update_checksums.py']:
 shutil.copy2(Path('/workspace/math2026p2_work')/script,T/'校对与检查记录/处理脚本'/(B+'_'+script))
m=T/(B+'_checksums.json');m.write_text(json.dumps({'algorithm':'sha256','files':[item(p,T) for p in sorted(T.rglob('*')) if p.is_file() and p!=m]},ensure_ascii=False,indent=2)+'\n')
g=R/'checksums.json';old=json.loads(g.read_text());mapping={v['path']:v for v in old['files']}
for f in [R/'README.md',R/'catalog.json',*sorted(p for p in T.rglob('*') if p.is_file())]:v=item(f,R);mapping[v['path']]=v
old['files']=[mapping[k] for k in sorted(mapping)];g.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n');print('Book and global SHA-256 manifests updated',len(old['files']))
