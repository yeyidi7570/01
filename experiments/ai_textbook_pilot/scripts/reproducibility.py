"""Build twice in clean temporary outputs and compare all deterministic artifacts."""
from pathlib import Path
import tempfile,subprocess,hashlib,json,sys
P=Path(__file__).resolve().parents[1];R=P.parents[1]
def inventory(p):return {f.relative_to(p).as_posix():hashlib.file_digest(f.open('rb'),'sha256').hexdigest() for f in p.rglob('*') if f.is_file() and f.name not in ['validation_report.md','validation_results.json','reproducibility_results.json','guard_results.json'] and '__pycache__' not in f.parts and f.suffix!='.pyc'}
with tempfile.TemporaryDirectory(prefix='ai_textbook_repro_') as td:
 out=[]
 for name in ['first','second']:
  d=Path(td)/name;subprocess.run([sys.executable,str(P/'scripts/build.py'),'--repo',str(R),'--out',str(d)],check=True);subprocess.run([sys.executable,str(P/'scripts/validate.py'),'--repo',str(R),'--data',str(d),'--no-report'],check=True,stdout=subprocess.DEVNULL);out.append(inventory(d))
 assert out[0]==out[1]==inventory(P),'Byte mismatch in repeat generation'
 result={'status':'passed','method':'Two fresh builds and full validation in separate temporary directories; compare to each other and current pilot.','compared_files':len(out[0]),'all_deterministic_bytes_equal':True,'ids_stable':True,'metadata_numbering_correction_test':'covered in validate.py source-anchor check','excluded_runtime_audit_files':['validation_report.md','validation_results.json','reproducibility_results.json','guard_results.json']};(P/'reproducibility_results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))
