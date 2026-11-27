import sys,os,json,math,pathlib,re,io
sys.path.append('/workspace/ocr_work/venv/lib/python3.12/site-packages')
import fitz,numpy as np,cv2
from PIL import Image,ImageFont,ImageDraw
P=pathlib.Path('/workspace/ocr_work')
FONTBASE='/usr/share/fonts/truetype/liberation/LiberationSans-'
fonts={k:fitz.Font(fontfile=FONTBASE+v+'.ttf') for k,v in {'R':'Regular','B':'Bold','I':'Italic','BI':'BoldItalic'}.items()}
pilfonts={k:ImageFont.truetype(FONTBASE+v+'.ttf',100) for k,v in {'R':'Regular','B':'Bold','I':'Italic','BI':'BoldItalic'}.items()}

def trim(mask):
 ys,xs=np.where(mask>0)
 return (int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)) if len(xs) else None

def template(text,key):
 f=pilfonts[key];b=f.getbbox(text); im=Image.new('L',(max(1,b[2]-b[0]+4),max(1,b[3]-b[1]+4)),0)
 ImageDraw.Draw(im).text((2-b[0],2-b[1]),text,font=f,fill=255)
 a=np.array(im);bb=trim(a>128)
 return a[bb[1]:bb[3],bb[0]:bb[2]],b

def get_rules(gray):
 ink=(gray<175).astype('uint8')*255
 hor=cv2.morphologyEx(ink,cv2.MORPH_OPEN,np.ones((1,65),np.uint8))
 ver=cv2.morphologyEx(ink,cv2.MORPH_OPEN,np.ones((45,1),np.uint8))
 rules=[];mask=np.zeros_like(ink)
 for typ,im in [('h',hor),('v',ver)]:
  cnt,_=cv2.findContours(im,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
  for c in cnt:
   x,y,w,h=cv2.boundingRect(c)
   if x<25 or x+w>895 or y<30 or y+h>1410:continue
   if (typ=='h' and h<=5 and w>=65) or (typ=='v' and w<=5 and h>=45):
    rules.append((typ,x,y,w,h));cv2.rectangle(mask,(x-1,y-1),(x+w+1,y+h+1),255,-1)
 cnt,_=cv2.findContours(ink,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
 boxes=[]
 for c in cnt:
  x,y,w,h=cv2.boundingRect(c)
  if 18<=w<=35 and 18<=h<=35 and .65<w/h<1.4 and x>40 and x+w<885:
   eps=cv2.approxPolyDP(c,1.3,True)
   # checkbox requires long continuous borders, empty centre and larger than body letters
   if len(eps)==4 and cv2.contourArea(c)/(w*h)>.80 and np.mean(ink[y+3:y+h-3,x+3:x+w-3])<35:
    if any(abs(x-a)<4 and abs(y-b)<4 for a,b,_,_ in boxes):continue
    boxes.append((x,y,w,h));cv2.rectangle(mask,(x-1,y-1),(x+w+1,y+h+1),255,-1)
 return ink,rules,boxes,mask

def word_spans(text,mask,fs):
 # Fit word breaks to observed blank columns using dynamic programming.
 words=text.split();h,w=mask.shape
 if len(words)<=1:return [(text,0,w)]
 runs=[];a=None
 cols=mask.any(axis=0)
 for x,v in enumerate(cols):
  if not v and a is None:a=x
  if v and a is not None:
   if x-a>=2 and a>0:runs.append((a,x))
   a=None
 m=len(words)
 if len(runs)<m-1:return [(text,0,w)]
 # Width prediction includes actual glyph bearings rather than advance widths.
 expected=[]
 for word in words:
  b=pilfonts['R'].getbbox(word);expected.append((b[2]-b[0])*fs/100)
 natural=sum(expected)
 # common horizontal scaling from scan; avoid absorbing justified word spaces
 scale=min(1.10,max(.86,(w-4*(m-1))/max(1,natural)))
 if w-natural>8*(m-1):scale=1
 expected=[z*scale for z in expected]
 cand=[(0,0)]+runs+[(w,w)];N=len(cand)
 costs={(0,0):(0,[])}
 prev={0:(0,[])}
 for i in range(m):
  nxt={}
  for j in range(1,N):
   if i==m-1 and j!=N-1:continue
   if i<m-1 and j==N-1:continue
   best=None
   for k,(cost,path) in prev.items():
    if k>=j:continue
    obs=cand[j][0]-cand[k][1]
    if obs<expected[i]*.42 or obs>expected[i]*1.7+12:continue
    dev=(obs-expected[i])/max(4,expected[i]*.12)
    gap=cand[j][1]-cand[j][0]
    score=cost+dev*dev-.15*min(gap,10)
    if best is None or score<best[0]:best=(score,path+[j])
   if best:nxt[j]=best
  prev=nxt
  if not prev:return [(text,0,w)]
 if N-1 not in prev:return [(text,0,w)]
 cuts=[0]+prev[N-1][1];out=[]
 for i,word in enumerate(words):out.append((word,cand[cuts[i]][1],cand[cuts[i+1]][0]))
 return out

def best_style(text,mask,allowed=('R','B','I','BI')):
 h,w=mask.shape
 if h<3 or w<2:return 'R'
 choices=[]
 for key in allowed:
  tm,_=template(text,key)
  tm=cv2.resize(tm,(w,h),interpolation=cv2.INTER_AREA)>150
  obs=mask>0
  # foreground density detects bold, overlap helps distinguish slanted forms
  density=abs(float(tm.mean())-float(obs.mean()))
  inter=np.logical_and(tm,obs).sum(); union=np.logical_or(tm,obs).sum()
  score=inter/max(1,union)-2.8*density
  if key in ('B','BI'):score-=.045
  if key in ('I','BI'):score-=.015
  choices.append((score,key))
 return max(choices)[1]

def line_slant(a):
 h,w=a.shape
 if h<8 or w<30:return 0
 scores=[]
 for k in np.arange(-.30,.331,.03):
  z=cv2.warpAffine(a,np.float32([[1,k,20-k*h/2],[0,1,0]]),(w+40,h),flags=cv2.INTER_NEAREST)
  proj=(z>0).sum(axis=0);scores.append((float((proj*proj).sum()),float(k)))
 return max(scores)[1]

def textline(page,line,ink,exclude,n,audit):
 s=line['text'].replace('□','').strip()
 if n==1 and line['id']=='0':s='О Қ У'
 if not s:return
 # Rectify the detected quadrilateral before measuring glyphs: scans have local tilt.
 poly=np.array(line.get('poly',[]),np.float32)
 if poly.shape==(4,2):
  ww=int(round((np.linalg.norm(poly[1]-poly[0])+np.linalg.norm(poly[2]-poly[3]))/2))
  hh=int(round((np.linalg.norm(poly[3]-poly[0])+np.linalg.norm(poly[2]-poly[1]))/2))
  if ww<2 or hh<2:return
  target=np.float32([[0,0],[ww-1,0],[ww-1,hh-1],[0,hh-1]])
  trans=cv2.getPerspectiveTransform(poly,target)
  a=cv2.warpPerspective(ink,trans,(ww,hh),flags=cv2.INTER_NEAREST)
  ex=cv2.warpPerspective(exclude,trans,(ww,hh),flags=cv2.INTER_NEAREST)
  a[ex>0]=0
  x0=int(round((poly[0,0]+poly[3,0])/2));y0=int(round((poly[0,1]+poly[1,1])/2))
  x1=x0+ww;y1=y0+hh
 else:
  x0,y0,x1,y1=[int(round(v)) for v in line['bbox']]
  x0=max(0,x0);y0=max(0,y0);x1=min(920,x1);y1=min(1446,y1)
  if x1<=x0 or y1<=y0:return
  a=ink[y0:y1,x0:x1].copy();a[exclude[y0:y1,x0:x1]>0]=0
 # Discard tiny fragments of an adjacent text line captured by an oversized detector polygon.
 row=(a>0).sum(axis=1);active=(row>2).astype('uint8')
 active=cv2.morphologyEx(active.reshape(-1,1),cv2.MORPH_CLOSE,np.ones((4,1),np.uint8)).ravel()
 bands=[];st=None
 for yy,v in enumerate(list(active)+[0]):
  if v and st is None:st=yy
  elif not v and st is not None:bands.append((int(row[st:yy].sum()),st,yy));st=None
 if bands:
  _,lo,hi=max(bands)
  if row[:lo].sum()+row[hi:].sum()<row.sum()*.20:a[:lo]=0;a[hi:]=0
 bb=trim(a)
 if bb is None:return
 xa,ya,xb,yb=bb;x0+=xa;y0+=ya;x1=x0+xb-xa;y1=y0+yb-ya;a=a[ya:yb,xa:xb]
 # font size from observed ink height and the precise glyph bounds
 tm,pb=template(s,'R');fs=(y1-y0)*100/max(1,tm.shape[0])
 if 5<=n<=97 and len(s)>5:fs=min(40,max(7,fs))
 if n==23 and line['id'] in ('27','28'):fs=18
 if n==98 and line['id']=='88':fs=18.8
 if n==98 and int(line['id'])<80:fs=22 if line['id']=='0' else 20
 if n==23 and line['id'] in ('27','28'):
  yy=1313 if line['id']=='27' else 1334
  xx=64;ww=290 if line['id']=='27' else 686
  anchor=fitz.Point(xx/2,yy/2);sx=(ww/2)/fonts['R'].text_length(s,fontsize=9)
  page.insert_text(anchor,s,fontname='R',fontsize=9,morph=(anchor,fitz.Matrix(sx,1)))
  audit.append({'id':line['id'],'word':s,'font':'R','size':9,'box':[xx/2,(yy-18)/2,(xx+ww)/2,yy/2]});return
 spans=word_spans(s,a,fs)
 linekey=best_style(s,a)
 italic=line_slant(a)>.09
 # infer the common baseline from glyph bottom in the full line
 textbbox=pilfonts['R'].getbbox(s,anchor='ls')
 baseline=y1-textbbox[3]*fs/100
 for j,(word,l,r) in enumerate(spans):
  wa=a[:,l:r];bb2=trim(wa)
  if not bb2:continue
  lx,ty,rx,by=bb2;wactual=rx-lx
  tight=wa[ty:by,lx:rx]
  key=best_style(word,tight)
  dt=cv2.distanceTransform(np.pad(tight,1),cv2.DIST_L2,5)
  stroke=float(dt[dt>0].mean()) if (dt>0).any() else 1
  basekey='I' if italic else 'R'
  tm,_=template(word,basekey);tm=cv2.resize(tm,(tight.shape[1],tight.shape[0]),interpolation=cv2.INTER_AREA)
  tmask=(tm>150).astype('uint8')*255
  td=cv2.distanceTransform(np.pad(tmask,1),cv2.DIST_L2,5)
  tstroke=float(td[td>0].mean()) if (td>0).any() else 1
  ratio=stroke/max(.01,tstroke)
  den=float((tight>0).mean())-float((tmask>0).mean())
  bold=ratio>1.095 and den>.06 and key in ('B','BI')
  key=('BI' if bold else 'I') if italic else ('B' if bold else 'R')
  if n in (1,3,100) and (len(s)<15 or n==100):key='R'
  if n==3 and line['id']=='5':key='B'
  if 5<=n<=97:
   if s.startswith(('Сұрақтарға жауап бер.','Тапсырманы орында.','Барлық сөз саны:','Оқуға кеткен уақыт:','Минутына оқылған сөз саны:','Бағасы:','Мұғалімнің қолы:')):key='B'
   if s.startswith('Оқу барысында оқушының'):key='BI'
   if re.match(r'^[–-] (баяу|шапшаң|өте баяу|орташа)',s):key='I'
   if line['bbox'][1]<130 and line['bbox'][0]>100 and line['id']=='0':key='B'
  if n in (7,12,23,83):key='B' if line['id']=='0' and line['bbox'][1]<130 else 'R'
  if n in (8,84):key='R'
  if n==98:
   key='R'
   if line['id'] in ('84','86') and j>=1:key='I'
   if line['id']=='85' and j>=2:key='I'

  f=fonts[key];pb2=pilfonts[key].getbbox(word,anchor='ls')
  # use line font size, with horizontal fitting for original justification
  natural=pilfonts[key].getlength(word)*fs/100
  glyphwidth=(pb2[2]-pb2[0])*fs/100
  scalex=wactual/max(1,glyphwidth)
  xx=x0+l+lx-pb2[0]*fs/100*scalex
  yy=baseline
  # precise per-word baseline if descender geometry supports it
  candidate=y0+by-pb2[3]*fs/100
  if abs(candidate-baseline)<3:yy=candidate
  color=(0,0,0)
  if n in (1,100):
   if ('ОҚУ' in s or 'ТЕХНИКАСЫ' in s):color=(1,.90,.06) if ('ТЕХНИКАСЫ' in s or n==100) else (.97,.97,.86)
   elif 'ISBN' in s or re.fullmatch(r'[0-9 ]+',s):color=(0,0,0)
   else:color=(1,1,1)
  anchor=fitz.Point(xx/2,yy/2)
  text=word+(' ' if j<len(spans)-1 else '')
  page.insert_text(anchor,text,fontname=key,fontsize=fs/2,color=color,morph=(anchor,fitz.Matrix(scalex,1)))
  audit.append({'id':line['id'],'word':word,'font':key,'size':round(fs/2,3),'box':[xx/2,(y0+ty)/2,(xx+wactual)/2,(y0+by)/2]})

def main():
 finaldir=P/('final' if (P/'final').exists() else 'raw')
 pages=[int(x) for x in sys.argv[1:]] if len(sys.argv)>1 else list(range(1,101))
 doc=fitz.open();audits=[];built=[]
 for n in pages:
  fn=finaldir/f'{n:03}.json'
  if not fn.exists():continue
  built.append(n)
  data=json.loads(fn.read_text());page=doc.new_page(width=460,height=723)
  for k,f in fonts.items():page.insert_font(fontname=k,fontbuffer=f.buffer)
  rgb=np.array(Image.open(P/'original'/f'{n:03}.png').convert('RGB'));gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY)
  ink,rules,boxes,exclude=get_rules(gray)
  ink=(gray<130).astype('uint8')*255
  # Preserve only meaningful artwork. Standard pages have a clean white ground.
  if n==3:
   for rect in [(198,370,380,523),(430,1280,490,1355)]:
    x0,y0,x1,y1=rect;im=Image.fromarray(rgb[y0:y1,x0:x1]);buf=io.BytesIO();im.save(buf,format='PNG');page.insert_image(fitz.Rect(x0/2,y0/2,x1/2,y1/2),stream=buf.getvalue())
  if n==48:
   x0,y0,x1,y1=320,650,572,933;im=Image.fromarray(rgb[y0:y1,x0:x1]);buf=io.BytesIO();im.save(buf,format='PNG');page.insert_image(fitz.Rect(x0/2,y0/2,x1/2,y1/2),stream=buf.getvalue())
  if n in (1,100):
   # Cover artwork is treated separately from the book's typeset text.
   clean=rgb.copy()
   if n==1:clean[:,:3]=clean[:,3:4];clean[:,916:]=clean[:,915:916]
   else:
    for yy in range(1446):
     for aa,bb,cc,dd in [(0,20,25,80),(890,920,820,875)]:
      patch=rgb[max(0,yy-10):min(1446,yy+11),cc:dd].reshape(-1,3).astype('int16')
      good=patch[(patch.max(axis=1)-patch.min(axis=1)<75)&(patch.mean(axis=1)>110)]
      if len(good):clean[yy,aa:bb]=np.median(good,axis=0).astype('uint8')
    clean[:8]=clean[9:10]

   buf=io.BytesIO();Image.fromarray(clean).save(buf,format='PNG');page.insert_image(page.rect,stream=buf.getvalue())
   # Rebuild the title bands as clean vector colour fields.
   bands=[(0,111,920,578),(0,1267,920,1343)] if n==1 else [(0,724,920,952)]
   for x0,y0,x1,y1 in bands:
    sample=rgb[int((y0+y1)/2),25:55] if n==1 else rgb[930,30:80]
    color=tuple(float(v)/255 for v in np.median(sample,axis=0))
    page.draw_rect(fitz.Rect(x0/2,y0/2,x1/2,y1/2),color=None,fill=color,overlay=True)
   # Barcode text is reset on its original white label.
   if n==100:
    for rect in [(400,1078,625,1107),(392,1196,622,1227)]:
     page.draw_rect(fitz.Rect(*[v/2 for v in rect]),color=None,fill=(1,1,1),overlay=True)
  else:
   shape=page.new_shape()
   if n==98:
    rules=[]
    shape.draw_line((122.5,590.5),(341,590.5));shape.draw_line((122.5,592.5),(341,592.5))
   for typ,x,y,w,h in rules:
    if typ=='h':shape.draw_line((x/2,(y+h/2)/2),((x+w)/2,(y+h/2)/2))
    else:shape.draw_line(((x+w/2)/2,y/2),((x+w/2)/2,(y+h)/2))
   for x,y,w,h in boxes:shape.draw_rect(fitz.Rect(x/2,y/2,(x+w)/2,(y+h)/2))
   shape.finish(color=(.15,.15,.15),width=.55);shape.commit()
  audit=[]
  if n==98:
   byid={l['id']:l for l in data['lines']}
   pairs=[(1,2),(6,7),(9,10),(13,14),(16,17),(20,21),(23,24),(27,28),(30,31),(34,35),(38,39),(42,43),(46,47),(50,51),(54,55),(58,59),(61,62),(65,66),(69,70),(73,74),(76,77),(4,5),(11,12),(18,19),(25,26),(32,33),(36,37),(40,41),(44,45),(48,49),(52,53),(56,57),(63,64),(67,68),(71,72),(78,79)]
   for t,num in pairs:
    a0=byid[str(t)]['bbox'];b0=byid[str(num)]['bbox'];yy=(a0[3]+b0[3])/4-1.6
    for xx in np.arange(a0[2]/2+1.5,b0[0]/2-1.5,2.75):page.draw_circle((float(xx),yy),.32,color=None,fill=(.12,.12,.12))
  for line in data['lines']:

   if n==3 and line['bbox'][1]>1250:continue
   if n in (1,100) and len(line['text'].strip())<3:continue
   lineink=ink
   if n in (1,100) and line['text'].strip() and not ('ISBN' in line['text'] or re.fullmatch(r'[0-9 ]+',line['text'].strip())):
    lineink=((rgb[:,:,0]>150)&(rgb[:,:,1]>150)&(rgb.astype('uint16').sum(axis=2)>480)).astype('uint8')*255
    if n==1:lineink[:125]=0;lineink[1340:]=0
   textline(page,line,lineink,exclude if n not in (1,100) else np.zeros_like(exclude),n,audit)
  audits.append({'page':n,'spans':audit,'rules':len(rules),'boxes':len(boxes)})
  print('rebuilt',n,len(audit),len(rules),len(boxes),flush=True)
 out=P/('draft.pdf' if sys.argv[1:] else 'rebuilt.pdf')
 doc.subset_fonts();doc.set_metadata({'title':'Оқу техникасы — 4-сынып','language':'kk'} if False else {'title':'Оқу техникасы — 4-сынып','subject':'Қазақ тіліндегі оқу техникасын тексеруге арналған жұмыс дәптері'})
 doc.save(out,garbage=4,deflate=True)
 (P/('build_audit_draft.json' if sys.argv[1:] else 'build_audit.json')).write_text(json.dumps(audits,ensure_ascii=False,indent=2))
 if sys.argv[1:]:
  for i,p in enumerate(doc):p.get_pixmap(matrix=fitz.Matrix(2,2)).save(P/f'draft_{built[i]:03}.png')
if __name__=='__main__':main()
