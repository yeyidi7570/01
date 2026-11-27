from pathlib import Path
import fitz,json
P=Path('/workspace/math2026p2_work');src=P/'数学2026_哈语学生_哈语教材（4-2）_АЛМАТЫКІТАП.pdf';d=fitz.open(src)
for k in ['original','raw','layout','round1','round2','final','review','rendered']:(P/k).mkdir(exist_ok=True)
meta=[]
for i,page in enumerate(d):
 n=i+1;p=P/'original'/f'{n:03}.png'
 if not p.exists():
  tmp=p.with_suffix('.partial.png');page.get_pixmap(matrix=fitz.Matrix(2,2),alpha=False).save(tmp);tmp.replace(p)
 meta.append({'pdf_page_number':n,'width_pt':page.rect.width,'height_pt':page.rect.height,'rotation':page.rotation,'image_width':1190,'image_height':1684,'has_native_text':False})
 print(n,flush=True)
(P/'pages_profile.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
