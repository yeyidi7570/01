"""Inject errors in temporary copies to prove validator rejects corrupt records."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,tempfile,shutil,traceback
from validate import validate
P=Path(__file__).resolve().parents[1];R=P.parents[1];cases=[]
for name in ['readable_text_changed','dangling_exercise_reference','missing_image','lost_unknown','wrong_child_parent','wrong_source_bundle']:
 with tempfile.TemporaryDirectory(prefix='ai_textbook_guard_') as td:
  d=Path(td)/'pilot';shutil.copytree(P,d,ignore=shutil.ignore_patterns('__pycache__'));rows=[json.loads(l) for l in (d/'exercises.jsonl').read_text().splitlines()]
  if name=='readable_text_changed':rows[0]['readable_text']+='UNAUTHORIZED'
  elif name=='dangling_exercise_reference':next(q for q in rows if any(r['explicit'] for r in q['references']))['references'][0]['target_id']='ex_does_not_exist'
  elif name=='wrong_child_parent':next(q for q in rows if q['subquestions'])['subquestions'][0]['parent_exercise_id']='ex_wrong_parent'
  elif name=='wrong_source_bundle':rows[0]['text_units'][0]['source_ref']['source_bundle_id']='not-the-source'
  elif name=='missing_image':
   m=json.loads((d/'manifest.json').read_text());(d/next(a['path'] for a in m['assets'] if a['role']=='crop')).unlink()
  elif name=='lost_unknown':
   m=json.loads((d/'manifest.json').read_text());m['uncertainties']=m['uncertainties'][1:];(d/'manifest.json').write_text(json.dumps(m,ensure_ascii=False))
  (d/'exercises.jsonl').write_text(''.join(json.dumps(q,ensure_ascii=False)+'\n' for q in rows))
  try:validate(d,R,False)
  except (AssertionError,ValueError,FileNotFoundError) as e:cases.append({'case':name,'rejected':True,'validator_line':traceback.extract_tb(e.__traceback__)[-1].lineno,'reason':str(e) or 'Invariant violation'})
  else:raise AssertionError('Validator accepted corrupt case: '+name)
result={'status':'passed','cases':cases,'original_outputs_modified':False};(P/'guard_results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))
