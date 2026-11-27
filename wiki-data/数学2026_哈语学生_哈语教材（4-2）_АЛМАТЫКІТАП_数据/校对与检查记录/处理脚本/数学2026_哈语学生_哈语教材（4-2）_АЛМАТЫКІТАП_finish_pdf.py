from pathlib import Path
import fitz,json,collections,re
from PIL import Image,ImageDraw
from restore_thin_graphics import restore
P=Path('/workspace/math2026p2_work');name='数学2026_哈语学生_哈语教材（4-2）_АЛМАТЫКІТАП';out=Path('/workspace/output')/(name+'_OCR.pdf');doc=fitz.open();audit=[]
for j in range(6):
 d=fitz.open(P/f'batch{j}.pdf');assert len(d)==30;
 
 for k in range(len(d)):
  n=j*30+k+1
  if n in [82,97,168,173]:
   q=[82,97,168,173].index(n);doc.insert_pdf(fitz.open(P/'repair_ranges.pdf'),from_page=q,to_page=q)
  else:doc.insert_pdf(d,from_page=k,to_page=k,final=0 if k<29 else 1)
 audit.extend(json.loads((P/f'batch{j}_audit.json').read_text()))
for n,a in zip([82,97,168,173],json.loads((P/'repair_ranges_audit.json').read_text())):audit[n-1]=a
# Rebuild only the localized graphics' invisible Unicode layer at readable logical glyph sizes.
# Dense protractor/array strings must not be squeezed to subpixel character widths.
font=fitz.Font(fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
for i,page in enumerate(doc):
 if i%30==0:print('Unicode layer',i+1,flush=True)
 for xref in page.get_contents():
  stream=doc.xref_stream(xref)
  stream=re.sub(rb'BT\b.*?\bET',lambda m:b'' if re.search(rb'\b3\s+Tr\b',m.group()) else m.group(),stream,flags=re.S)
  doc.update_stream(xref,stream)
 page.insert_font(fontname='LookupUnicode',fontbuffer=font.buffer)
 data=json.loads((P/'final'/f'{i+1:03}.json').read_text());lookup={l['id']:l for l in data['lines']}
 audit[i]['thin_colored_graphic_preservation']=restore(page,data,audit[i])
 for a in audit[i]['spans']:
  if not a.get('graphic'):continue
  line=lookup.get(a['id']);text=(line['text'] if line else a['text']).strip()
  if not text:continue
  b=(line['bbox'] if line else a.get('bbox'))
  if not b:continue
  x,y,x1,y1=[b[0]*594.96/1190,b[1]*841.92/1684,b[2]*594.96/1190,b[3]*841.92/1684];width=max(6,x1-x);size=4.;rows=[]
  for physical in text.splitlines():
   current=''
   for word in physical.split(' '):
    candidate=(current+' '+word).strip()
    if current and font.text_length(candidate,fontsize=size)>width:rows.append(current);current=word
    else:current=candidate
   if current:rows.append(current)
  size=min(size,max(1.5,(y1-y)/max(1,len(rows))/1.2))
  for j,row in enumerate(rows):
   fs=size;length=font.text_length(row,fontsize=fs);sc=min(1,width/max(.01,length));anchor=fitz.Point(x,min(page.rect.height-2,y+fs+j*fs*1.2));page.insert_text(anchor,row,fontname='LookupUnicode',fontsize=fs,render_mode=3,morph=(anchor,fitz.Matrix(sc,1)))
doc.set_metadata({'title':name,'subject':'PP-OCRv5; two independent proofreading rounds; source-layout reconstruction','language':'kk-Cyrl'} if False else {'title':name,'subject':'PP-OCRv5; two independent proofreading rounds; source-layout reconstruction'});doc.save(out,garbage=1,deflate=True);doc.close();doc=fitz.open(out);assert len(doc)==180
stats=[];missing=[];fonts={};glyphs=collections.Counter();clean=lambda s:re.sub(r'\s+','',s).replace('□','')
for i,page in enumerate(doc):
 n=i+1;data=json.loads((P/'final'/f'{n:03}.json').read_text());assert abs(page.rect.width-594.96)<.01 and abs(page.rect.height-841.92)<.01
 txt=page.get_text();glyphs.update(c for c in txt if c in 'ӘҒҚҢӨҰҮҺІәғқңөұүһі');spans=[s for b in page.get_text('dict')['blocks'] if b['type']==0 for l in b['lines'] for s in l['spans']];visible=sum(s.get('alpha',255)>0 for s in spans)
 for f in page.get_fonts():fonts[f[0]]=f
 for l in data['lines']:
  if l['text'] and clean(l['text']) not in clean(txt):missing.append({'page':n,'id':l['id'],'text':l['text']})
 page.get_pixmap(matrix=fitz.Matrix(2,2),alpha=False).save(P/'rendered'/f'{n:03}.png');stats.append({'page':n,'text_chars':len(txt),'text_spans':len(spans),'images':len(page.get_images()),'vector_paths':len(page.get_drawings())})
print('All pages rendered and text checked',flush=True)
fontchecks=[]
for x,f in fonts.items():
 name,ext,typ,buf=doc.extract_font(x);fontchecks.append({'name':name,'type':typ,'embedded':bool(buf)})
report={'pages':180,'source_page_sizes_preserved':True,'fonts':fontchecks,'kazakh_glyph_counts':dict(glyphs),'copy_line_mismatches':missing,'page_statistics':stats,'limits':['Fonts approximated using embedded Cyrillic-capable fonts.','Localized complex fractions, vertical arithmetic, scales and illustrations retain source graphics with searchable transcriptions; copying does not reconstruct two-dimensional mathematics.','Unresolved tiny decorative text remains flagged in proofreading records.']};(P/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));(P/'render_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2));print(out,out.stat().st_size,'copy mismatches',len(missing),flush=True)
# Paired source/rebuild overview, every page represented at the same scale.
for start in range(0,180,12):
 sheet=Image.new('RGB',(1800,6*450),'#edf0f2');draw=ImageDraw.Draw(sheet)
 for j,n in enumerate(range(start+1,min(start+13,181))):
  x=(j%2)*900;y=(j//2)*450;draw.text((x+8,y+4),f'PDF {n}  source / rebuild',fill='black')
  for z,folder in enumerate(['original','rendered']):
   im=Image.open(P/folder/f'{n:03}.png');im.thumbnail((300,420));sheet.paste(im,(x+80+z*390,y+24))
 sheet.save(P/'review'/f'comparison_{start//12:02}.jpg',quality=90)
