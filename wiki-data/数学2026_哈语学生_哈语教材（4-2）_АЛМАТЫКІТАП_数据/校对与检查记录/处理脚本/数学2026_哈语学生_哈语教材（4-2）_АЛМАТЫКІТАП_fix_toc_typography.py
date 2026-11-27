from pathlib import Path
import json,io,hashlib
import fitz
from PIL import Image,ImageDraw
P=Path('/workspace/math2026p2_work');R=Path('/workspace/github-delivery-01');B='数学2026_哈语学生_哈语教材（4-2）_АЛМАТЫКІТАП';T=R/'wiki-data'/(B+'_数据');f=Path('/workspace/output')/(B+'_OCR.pdf');d=fitz.open(f);w=json.loads((T/(B+'_Wiki.json')).read_text());changes=[]
for n in [176,177]:
 b=[1030,200,1190,1580];im=Image.open(P/'original'/f'{n:03}.png').crop(b);buf=io.BytesIO();im.save(buf,format='PNG');p=d[n-1];rect=fitz.Rect(b[0]*p.rect.width/1190,b[1]*p.rect.height/1684,b[2]*p.rect.width/1190,b[3]*p.rect.height/1684);p.insert_image(rect,stream=buf.getvalue());asset='图片/版面裁剪/'+B+f'_页{n:03}_目录页码原字形.png';im.save(T/asset);w['assets'].append({'id':f'math-2026-grade4-part2:p{n:03}:toc_typography','path':asset,'kind':'source_typography_crop','page_id':f'math-2026-grade4-part2:p{n:03}','bbox':b,'description':'Original TOC page-number glyphs retained to prevent number-width distortion.'});changes.append({'page':n,'bbox':b,'source':f'来源/页面/{B}_页{n:03}.png','reason':'TOC page-number glyph widths preserved exactly.'})
d.saveIncr();d.close();d=fitz.open(f)
for n in [176,177]:d[n-1].get_pixmap(matrix=fitz.Matrix(2,2),alpha=False).save(P/'rendered'/f'{n:03}.png')
import shutil
shutil.copy2(f,R/f.name);w['corrected_pdf']['sha256']=hashlib.file_digest(f.open('rb'),'sha256').hexdigest();w['validation']['assets']=len(w['assets']);(T/(B+'_Wiki.json')).write_text(json.dumps(w,ensure_ascii=False,indent=2)+'\n');c=json.loads((R/'wiki-data/catalog.json').read_text());next(x for x in c['books'] if x['book_id']==w['book_id'])['assets']=len(w['assets']);(R/'wiki-data/catalog.json').write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n');(T/'校对与检查记录'/(B+'_目录字形修复.json')).write_text(json.dumps(changes,ensure_ascii=False,indent=2)+'\n');shutil.copy2(__file__,T/'校对与检查记录/处理脚本'/(B+'_fix_toc_typography.py'))
clean=lambda s:''.join(s.split()).replace('□','');missing=[]
for i,p in enumerate(d):
 tx=clean(p.get_text());data=json.loads((P/'final'/f'{i+1:03}.json').read_text());missing.extend((i+1,l['id']) for l in data['lines'] if l['text'] and clean(l['text']) not in tx)
assert not missing,missing
print('TOC typography repaired; all 180 pages copy validation: zero missing lines; sha256',w['corrected_pdf']['sha256'])
