"""Retrieve complete parents by metadata; optionally follow existing exercise references."""
from pathlib import Path
import argparse,json
P=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--data',type=Path,default=P);a.add_argument('--book',required=True);a.add_argument('--lesson',required=True);a.add_argument('--exercise',required=True);a.add_argument('--include-references',action='store_true');v=a.parse_args();rows=[json.loads(l) for l in (v.data/'exercises.jsonl').read_text().splitlines()];labels={l['exercise_id']:l for l in map(json.loads,(v.data/'labels.jsonl').read_text().splitlines())};m=json.loads((v.data/'manifest.json').read_text());byid={r['id']:r for r in rows};found=[r for r in rows if r['book_id']==v.book and r['lesson_number']==v.lesson and r['exercise_number']==v.exercise];queue=found[:];used=set();results=[]
while queue:
 r=queue.pop(0)
 if r['id'] in used:continue
 used.add(r['id']);results.append(r)
 if v.include_references:
  for ref in r['references']:
   if ref['type']=='exercise' and ref['resolution']=='internal':queue.append(byid[ref['target_id']])
assets={}
def collect(z):
 if isinstance(z,dict):
  if 'asset_id' in z:assets[z['asset_id']]=True
  for value in z.values():collect(value)
 elif isinstance(z,list):
  for value in z:collect(value)
collect(results);print(json.dumps({'matches':len(found),'complete_parent_records':results,'objective_labels':[labels[r['id']] for r in results],'assets':[r for r in m['assets'] if r['id'] in assets]},ensure_ascii=False,indent=2))
