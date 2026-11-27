from pathlib import Path
import json,shutil,hashlib
P=Path('/workspace/math2026p2_work');R=Path('/workspace/github-delivery-01');D=Path('/workspace/math2026p2_delivery/wiki-data/math-2026-grade4-part2');B='数学2026_哈语学生_哈语教材（4-2）_АЛМАТЫКІТАП';T=R/'wiki-data'/(B+'_数据');assert not T.exists(),'New textbook directory already exists; inspect before replacing'
replacements={};files=sorted(x for x in D.rglob('*') if x.is_file());tags={'raw':'原始OCR','final':'最终校对','round1':'第一轮校对','round2':'第二轮校对','layout':'版面分析'}
for f in files:
 rel=f.relative_to(D).as_posix();parts=f.relative_to(D).parts
 if rel in [x+'.json' for x in tags]:new=B+'_'+tags[f.stem]+'.json'
 elif rel=='wiki.json':new=B+'_Wiki.json'
 elif parts[0]=='archive':new='逐页数据/'+tags[parts[1]]+'/'+B+'_页'+f.stem+'_'+tags[parts[1]]+'.json'
 elif rel.startswith('source/pages/'):new='来源/页面/'+B+'_页'+f.stem+'.png'
 elif parts[0]=='source':new='来源/'+f.name
 elif rel.startswith('assets/layout-crops/'):new='图片/版面裁剪/'+B+'_'+f.name
 elif rel.startswith('assets/pdf-images/'):new='图片/PDF插图/'+B+'_'+f.name
 elif parts[0]=='review':new='校对与检查记录/'+B+'_'+f.name
 else:new=B+'_'+f.name
 replacements[rel]=new
for rel,new in replacements.items():
 f=D/rel;t=T/new;t.parent.mkdir(parents=True,exist_ok=True)
 if f.suffix=='.json':
  obj=json.loads(f.read_text())
  def cv(x):
   if isinstance(x,str):return replacements.get(x,x)
   if isinstance(x,list):return [cv(i) for i in x]
   if isinstance(x,dict):return {k:cv(v) for k,v in x.items()}
   return x
  t.write_text(json.dumps(cv(obj),ensure_ascii=False,indent=2)+'\n')
 else:shutil.copy2(f,t)
for name in ['main_reviews_final.json','validation.json','render_audit.json','source_profile.json']:
 shutil.copy2(P/name,T/'校对与检查记录'/(B+'_'+name))
shutil.copy2(P/'review/source_uncertainties.json',T/'校对与检查记录'/(B+'_待确认事项.json'))
shutil.copy2(P/'review/main_adjudication.json',T/'校对与检查记录'/(B+'_主审裁决.json'))
for name in ['prepare.py','run_ocr.py','run_layout.py','compare_reviews.py','assemble_final.py','render_book.py','finish_pdf.py','export_data.py','publish_prepare.py','validate_delivery.py','restore_thin_graphics.py']:
 t=T/'校对与检查记录'/'处理脚本'/(B+'_'+name);t.parent.mkdir(exist_ok=True);shutil.copy2(P/name,t)
for extra in ['process.json','render_adjustments.json']:
 shutil.copy2(P/'review'/extra,T/'校对与检查记录'/(B+'_'+extra))
# Renderer dependencies are retained so the delivered script is traceable.
for src,suffix in [('/workspace/math2023p2_work/rebuild.py','renderer_geometry.py'),('/workspace/ocr_work/rebuild.py','renderer_fonts.py')]:shutil.copy2(src,T/'校对与检查记录'/'处理脚本'/(B+'_'+suffix))
shutil.copy2(Path('/workspace/output')/(B+'_OCR.pdf'),R/(B+'_OCR.pdf'))
wiki=json.loads((T/(B+'_Wiki.json')).read_text());wiki['corrected_pdf']['path']='../../'+B+'_OCR.pdf';wiki['provenance']['final_authority']='逐页数据/最终校对/'+B+'_页NNN_最终校对.json';(T/(B+'_Wiki.json')).write_text(json.dumps(wiki,ensure_ascii=False,indent=2)+'\n')
cpath=R/'wiki-data/catalog.json';catalog=json.loads(cpath.read_text());assert all(z['book_id']!='math-2026-grade4-part2' for z in catalog['books']);catalog['books'].append({'book_id':'math-2026-grade4-part2','source_filename':B+'.pdf','pages':180,'wiki_json':T.name+'/'+B+'_Wiki.json','raw_json':T.name+'/'+B+'_原始OCR.json','final_json':T.name+'/'+B+'_最终校对.json','source_pdf_sha256':wiki['source_pdf']['sha256'],**wiki['validation'],'directory':T.name,'original_basename':B});cpath.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
rpath=R/'wiki-data/README.md';txt=rpath.read_text();txt+='\n## 新增教材（2026 年）\n\n`'+B+'_数据`：180 页，语言为哈萨克语（kk-Cyrl）。保留原始 OCR、两轮独立图像校对、主审裁决、最终文本、版面候选、全部源图及局部图像。源 PDF 和重建 OCR PDF 超过 GitHub 普通文件大小限制，以 Git LFS 保留完整字节。重建 PDF 为根目录的 `'+B+'_OCR.pdf`。复杂分数、竖式和刻度保留局部原图与可搜索转录；Wiki 结构仅作候选索引，本次未进行正式语义切题。\n';txt=txt.replace('本目录包含十五份教材共 1283 页','本目录包含十六份教材共 '+str(sum(z['pages'] for z in catalog['books']))+' 页',1)
row='| `'+B+'_数据` | '+B+' | 180 |\n'
txt=txt.replace('\n## 每份教材中的文件', '\n'+row+'\n## 每份教材中的文件',1)
txt+='\n两份 PDF 使用 Git LFS：下载时使用文件页面的 Download 按钮或 Git LFS；GitHub 仓库 ZIP 可能只含 PDF 指针。JSON 与逐页源图可直接下载。\n'
rpath.write_text(txt)
manifest=[]
for f in sorted(T.rglob('*')):
 if f.is_file():manifest.append({'path':f.relative_to(T).as_posix(),'bytes':f.stat().st_size,'sha256':hashlib.file_digest(f.open('rb'),'sha256').hexdigest()})
(T/(B+'_checksums.json')).write_text(json.dumps({'algorithm':'sha256','files':manifest},ensure_ascii=False,indent=2)+'\n');print(T,'files',len(manifest),'bytes',sum(z['bytes'] for z in manifest))
