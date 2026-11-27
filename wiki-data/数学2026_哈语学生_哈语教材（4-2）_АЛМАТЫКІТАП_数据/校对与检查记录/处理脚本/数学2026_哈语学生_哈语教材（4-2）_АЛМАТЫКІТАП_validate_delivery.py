from pathlib import Path
import json,hashlib,subprocess
from PIL import Image
R=Path('/workspace/github-delivery-01');B='数学2026_哈语学生_哈语教材（4-2）_АЛМАТЫКІТАП';T=R/'wiki-data'/(B+'_数据');read=lambda p:json.loads(p.read_text());w=read(T/(B+'_Wiki.json'));assert len(w['pages'])==180 and w['language']=='kk-Cyrl';look={}
for page in w['pages']:
 n=page['pdf_page_number'];assert n==len(look)+1;look[n]=page;assert Image.open(T/page['image']).size==(1190,1684)
 final=read(T/'逐页数据/最终校对'/(B+f'_页{n:03}_最终校对.json'));raw=read(T/'逐页数据/原始OCR'/(B+f'_页{n:03}_原始OCR.json'));assert {l['id'] for l in raw['lines']}<={l['id'] for l in final['lines']};assert len(final['lines'])==len(page['lines']);fm={l['id']:l for l in final['lines']}
 for l in page['lines']:assert l['text']==fm[l['source_line_id']]['text']
 for kind in ['第一轮校对','第二轮校对','版面分析']:assert (T/'逐页数据'/kind/(B+f'_页{n:03}_{kind}.json')).exists()
 for l in page['lines']:
  for ref in l.get('source_line_ids',[]):assert ref in {v['id'] for v in page['lines']}
for a in w['assets']:assert (T/a['path']).is_file(),a
assert hashlib.file_digest((T/w['source_pdf']['path']).open('rb'),'sha256').hexdigest()=='cbf4523add551ffe045c456f2042e813c4ac84bff49105cb9a0fe091bb2b49d4'
assert (T/w['corrected_pdf']['path']).resolve()==(R/(B+'_OCR.pdf')).resolve()
old=json.loads(subprocess.check_output(['git','show','HEAD:wiki-data/catalog.json'],cwd=R));new=read(R/'wiki-data/catalog.json');assert len(new['books'])==len(old['books'])+1
for a in old['books']:assert a==next(b for b in new['books'] if b['book_id']==a['book_id'])
report={'book_id':w['book_id'],'pages':180,'raw_and_final_line_traceability':True,'two_round_files_all_present':True,'all_original_text_ids_preserved':True,'all_wiki_text_matches_final':True,'all_asset_paths_exist':True,'source_original_sha256_verified':True,'existing_catalog_entries_unchanged':True,'assets':len(w['assets']),'active_final_lines':sum(l['active'] for p in w['pages'] for l in p['lines'])};(T/'校对与检查记录'/(B+'_交付验证.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
