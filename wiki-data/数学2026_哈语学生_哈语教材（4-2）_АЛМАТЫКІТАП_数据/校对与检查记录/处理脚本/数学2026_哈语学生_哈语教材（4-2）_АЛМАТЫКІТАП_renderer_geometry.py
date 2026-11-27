import os,sys,pathlib,json,math,io,re,functools,time
sys.path.append('/workspace/ocr_work/venv/lib/python3.12/site-packages');sys.path.insert(0,'/workspace/ocr_work')
import fitz,numpy as np,cv2
from PIL import Image,ImageFont,ImageDraw
import rebuild as base
P=pathlib.Path('/workspace/math2023p2_work');W,H=992,1418;PW,PH=496.06298828125,708.6610107421875;SX,SY=PW/W,PH/H
FONTBASE='/usr/share/fonts/truetype/open-sans/OpenSans-'
styles={'R':'Regular','B':'Bold','I':'Italic','BI':'BoldItalic'}
fonts={k:fitz.Font(fontfile=FONTBASE+v+'.ttf') for k,v in styles.items()}
fonts['S']=fitz.Font(fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
fonts['M']=fitz.Font(fontfile='/usr/share/fonts/truetype/noto/NotoSansSymbols-Regular.ttf')
fonts['N']=fitz.Font(fontfile='/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf')
pilfonts={k:ImageFont.truetype(FONTBASE+v+'.ttf',100) for k,v in styles.items()}
base.fonts=fonts;base.pilfonts=pilfonts
_plain_template=base.template
_special_pil=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',100)
@functools.lru_cache(maxsize=20000)
def safe_template(text,key):
 if all(fonts[key].has_glyph(ord(c)) for c in text):return _plain_template(text,key)
 b=_special_pil.getbbox(text);im=Image.new('L',(max(1,b[2]-b[0]+4),max(1,b[3]-b[1]+4)),0)
 ImageDraw.Draw(im).text((2-b[0],2-b[1]),text,font=_special_pil,fill=255)
 a=np.array(im);bb=base.trim(a>128)
 if bb is None:return np.ones((1,1),np.uint8)*255,b
 return a[bb[1]:bb[3],bb[0]:bb[2]],b
base.template=safe_template
import inspect
_wordcode=inspect.getsource(base.word_spans).replace("b=pilfonts['R'].getbbox(word)","b=(pilfonts['R'] if all(fonts['R'].has_glyph(ord(c)) for c in word) else _special_pil).getbbox(word)")
exec(_wordcode,globals())
base.word_spans=word_spans

def sample_line(rgb,line,rules):
 poly=np.float32(line.get('poly',[]))
 if poly.shape!=(4,2):
  x,y,x1,y1=line['bbox'];poly=np.float32([[x,y],[x1,y],[x1,y1],[x,y1]])
 ww=max(2,int(round((np.linalg.norm(poly[1]-poly[0])+np.linalg.norm(poly[2]-poly[3]))/2)))
 hh=max(2,int(round((np.linalg.norm(poly[3]-poly[0])+np.linalg.norm(poly[2]-poly[1]))/2)))
 if ww>1600 or hh>1600:return None
 tr=cv2.getPerspectiveTransform(poly,np.float32([[0,0],[ww-1,0],[ww-1,hh-1],[0,hh-1]]))
 patch=cv2.warpPerspective(rgb,tr,(ww,hh),borderValue=(255,255,255));ow,oh=ww,hh;vertical=bool(line.get('vertical')) or (hh>ww*1.45 and len(line['text'].strip())>=2 and len(line['text'].strip())<25 and not line['text'].strip().isdigit())
 if vertical:patch=np.rot90(patch,3).copy();ww,hh=hh,ww
 gray=cv2.cvtColor(patch,cv2.COLOR_RGB2GRAY)
 # A colour histogram distinguishes lettering from a pastel panel or blue title field.
 border=np.concatenate((patch[:2].reshape(-1,3),patch[-2:].reshape(-1,3),patch[:,:2].reshape(-1,3),patch[:,-2:].reshape(-1,3)))
 q=(border//16).astype('int16');codes=q[:,0]*256+q[:,1]*16+q[:,2];code=np.bincount(codes,minlength=4096).argmax();bg=border[codes==code].mean(axis=0);lum=float(np.dot(bg,[.299,.587,.114]))
 threshold,_=cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
 mask=(gray<=threshold) if lum>threshold else (gray>threshold)
 # Choose the minority ink cluster; the border histogram identifies the surrounding field.
 rulepatch=cv2.warpPerspective(rules,tr,(ow,oh),flags=cv2.INTER_NEAREST)
 if vertical:rulepatch=np.rot90(rulepatch,3).copy()
 if hh<55:mask[rulepatch>0]=0
 if line.get('black_text'):
  chroma=patch.max(axis=2).astype('int16')-patch.min(axis=2).astype('int16');mask &= (chroma<70)&(gray<170)
 if not mask.any():return None
 bb=base.trim(mask);xa,ya,xb,yb=bb;mask=(mask[ya:yb,xa:xb].astype('uint8')*255)
 # Remove isolated edge fragments from a neighbouring row.
 row=(mask>0).sum(axis=1);active=cv2.morphologyEx((row>1).astype('uint8').reshape(-1,1),cv2.MORPH_CLOSE,np.ones((3,1),np.uint8)).ravel();bands=[];st=None
 for yy,v in enumerate(list(active)+[0]):
  if v and st is None:st=yy
  elif not v and st is not None:bands.append((row[st:yy].sum(),st,yy));st=None
 if bands:
  _,lo,hi=max(bands)
  if row[:lo].sum()+row[hi:].sum()<row.sum()*.12:mask[:lo]=0;mask[hi:]=0
 bb2=base.trim(mask)
 if not bb2:return None
 u,v,u1,v1=bb2;xa+=u;ya+=v;mask=mask[v:v1,u:u1]
 x0=float((poly[0,0]+poly[3,0])/2)+xa;y0=float((poly[0,1]+poly[1,1])/2)+ya
 # Median foreground colour keeps black, white and the book's blue/orange headings.
 allmask=np.zeros((hh,ww),np.uint8);allmask[ya:ya+mask.shape[0],xa:xa+mask.shape[1]]=mask
 fg=patch[allmask>0];distance=np.linalg.norm(fg.astype('float32')-bg,axis=1) if len(fg) else np.array([])
 color=np.median(fg[distance>=np.percentile(distance,70)],axis=0)/255 if len(fg) else np.array([.2,.2,.2])
 # Map the glyph mask back to source pixels for removal, preserving diagram rules.
 originalmask=np.rot90(allmask,1).copy() if vertical else allmask
 ob=base.trim(originalmask)
 vrect=[float((poly[0,0]+poly[3,0])/2)+ob[0],float((poly[0,1]+poly[1,1])/2)+ob[1],float((poly[0,0]+poly[3,0])/2)+ob[2],float((poly[0,1]+poly[1,1])/2)+ob[3]]
 inv=cv2.getPerspectiveTransform(np.float32([[0,0],[ow-1,0],[ow-1,oh-1],[0,oh-1]]),poly)
 removal=cv2.warpPerspective(originalmask,inv,(W,H),flags=cv2.INTER_NEAREST)
 return dict(mask=mask,x=x0,y=y0,color=tuple(float(c) for c in color),removal=removal,bg=bg,flat=float((codes==code).mean())>.45,vertical=vertical,vrect=vrect,graphic=bool((bg[0]-bg[1]>75 and bg[1]-bg[2]<80 and bg[0]>140) or (float((codes==code).mean())<=.45 and len(line['text'].strip())<18)),pixels=patch[ya:ya+mask.shape[0],xa:xa+mask.shape[1]])

def get_rulemask(rgb,n=None):
 g=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY);z=rgb.astype('int16');cyan=(z[:,:,2]-z[:,:,0]>20)&(z[:,:,1]-z[:,:,0]>15)&(z[:,:,2]>100);ink=((g<150)|cyan).astype('uint8')*255
 hor=cv2.morphologyEx(ink,cv2.MORPH_OPEN,np.ones((1,40),np.uint8));ver=cv2.morphologyEx(ink,cv2.MORPH_OPEN,np.ones((50,1),np.uint8))
 result=np.zeros_like(ink)
 for im,typ in [(hor,'h'),(ver,'v')]:
  cs,_=cv2.findContours(im,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
  for c in cs:
   x,y,w,h=cv2.boundingRect(c)
   if (typ=='h' and h<=5 and w>=40) or (typ=='v' and w<=5 and h>=50):cv2.drawContours(result,[c],-1,255,-1)
 # Preserve printed rectangular endings without treating round letter counters as boxes.
 contours,_=cv2.findContours((g<160).astype('uint8')*255,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
 for c in contours:
  x,y,w,h=cv2.boundingRect(c)
  if not (13<=w<=110 and 17<=h<=45):continue
  poly=cv2.approxPolyDP(c,1.7,True).reshape(-1,2)
  if len(poly)!=4 or cv2.contourArea(c)<w*h*.65:continue
  if all(min(abs(xx-x),abs(xx-(x+w-1)))<=3 and min(abs(yy-y),abs(yy-(y+h-1)))<=3 for xx,yy in poly):cv2.polylines(result,[poly],True,255,2)
 if n is not None:
  for b in json.loads((P/'layout'/f'{n:03}.json').read_text())['res']['boxes']:
   if b['label']!='table' or b['score']<.3:continue
   x,y,x1,y1=map(int,b['coordinate']);white=(rgb[y:y1,x:x1].min(axis=2)>=245).astype('uint8')*255
   for kernel,typ in [(np.ones((1,40),np.uint8),'h'),(np.ones((40,1),np.uint8),'v')]:
    opened=cv2.morphologyEx(white,cv2.MORPH_OPEN,kernel);cs,_=cv2.findContours(opened,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    for c in cs:
     xx,yy,w,h=cv2.boundingRect(c)
     if (typ=='h' and h<=6 and w>=40) or (typ=='v' and w<=6 and h>=40):cv2.drawContours(result[y:y1,x:x1],[c],-1,255,-1)
 return result

def is_overlay(l):
 x,y,x1,y1=l['bbox'];s=l['text'].strip()
 return y1<41 or y>1362 or ('Все учебники Казахстана' in s) or ('Книга предоставлена' in s) or ('согласно Приказа Министра' in s)

def final_data(n,folder):
 d=json.loads((P/'raw'/f'{n:03}.json').read_text())
 if folder=='raw':return d
 r=json.loads((P/folder/f'{n:03}.json').read_text()) if folder!='final' else None
 if folder=='final':return json.loads((P/'final'/f'{n:03}.json').read_text())
 for l in d['lines']:l['text']=r['corrections'].get(l['id'],l['text'])
 for i,a in enumerate(r['additions']):d['lines'].append(dict(a,id='a'+str(i)))
 return d

EXTRA_ART={}
MANUAL_ART={}

def artwork_boxes(bg,n):
 candidates=list(EXTRA_ART.get(n,[]))
 layout=json.loads((P/'layout'/f'{n:03}.json').read_text())['res']['boxes']
 for b in layout:
  if b['label'] in ('image','chart','seal') and b['score']>.52:
   x,y,x1,y1=map(int,b['coordinate'])
   if (x1-x)*(y1-y)<W*H*.30:candidates.append((max(0,x-4),max(40,y-4),min(W,x1+4),min(1363,y1+4)))
 mask=np.zeros((H,W),np.uint8);bs=24;small=np.zeros(((H+bs-1)//bs,(W+bs-1)//bs),np.uint8)
 for yy in range(40,H-55,bs):
  for xx in range(0,W,bs):
   p=bg[yy:yy+bs,xx:xx+bs];q=(p.reshape(-1,3)//32).astype('int16');c=q[:,0]*64+q[:,1]*8+q[:,2];_,cnt=np.unique(c,return_counts=True);cnt=cnt[cnt>=3]
   if not len(cnt):continue
   pr=cnt/cnt.sum();entropy=-(pr*np.log2(pr)).sum()
   if len(cnt)>=12 and entropy>2.35:small[yy//bs,xx//bs]=255
 mask=cv2.resize(small,(small.shape[1]*bs,small.shape[0]*bs),interpolation=cv2.INTER_NEAREST)[:H,:W];mask=cv2.dilate(mask,np.ones((25,25),np.uint8))
 cnt,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
 for c in cnt:
  x,y,w,h=cv2.boundingRect(c)
  if w*h>700 and w*h<W*H*.42:candidates.append((max(0,x-4),max(40,y-4),min(W,x+w+4),min(1363,y+h+4)))
 # Actual tables must remain vector grids.
 tables=[b['coordinate'] for b in layout if b['label']=='table' and b['score']>.55]
 filtered=[]
 for a in candidates:
  x,y,x1,y1=a;area=max(1,(x1-x)*(y1-y));inside=0
  for tx,ty,tx1,ty1 in tables:inside+=max(0,min(x1,tx1)-max(x,tx))*max(0,min(y1,ty1)-max(y,ty))
  if inside/area<.45 or a in EXTRA_ART.get(n,[]):filtered.append(a)
 # Merge overlapping art crops to prevent many seams.
 changed=True
 while changed:
  changed=False;out=[]
  for a in filtered:
   hit=None
   for j,b in enumerate(out):
    ix=max(0,min(a[2],b[2])-max(a[0],b[0]));iy=max(0,min(a[3],b[3])-max(a[1],b[1]))
    if ix*iy>0:hit=j;break
   if hit is None:out.append(a)
   else:
    b=out[hit];out[hit]=(min(a[0],b[0]),min(a[1],b[1]),max(a[2],b[2]),max(a[3],b[3]));changed=True
  filtered=out
 return filtered

def paint_background(page,bg,n):
 art=artwork_boxes(bg,n);vec=bg.copy()
 for x,y,x1,y1 in art:vec[y:y1,x:x1]=255
 # Flat panels, grids, boxes and diagrams are real filled PDF vector paths.
 pal=Image.fromarray(vec).quantize(colors=48,method=Image.Quantize.FASTOCTREE,dither=Image.Dither.NONE);idx=np.array(pal);colors=np.array(pal.getpalette(),dtype='uint8').reshape(-1,3)
 paths=0
 for k,col in enumerate(colors[:48]):
  if np.min(col)>250:continue
  m=(idx==k).astype('uint8');cs,hierarchy=cv2.findContours(m,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE);shape=page.new_shape();have=False;thin=page.new_shape();hthin=False
  for c in cs:
   if len(c)<2:continue
   area=cv2.contourArea(c)
   bx,by,bw,bh=cv2.boundingRect(c)
   if area<4 and max(bw,bh)<10 and np.min(col)>160:continue
   c=cv2.approxPolyDP(c,.35,True).reshape(-1,2)
   if len(c)<2:continue
   pts=[fitz.Point(float(x)*SX,float(y)*SY) for x,y in c]
   if area<.8:
    if len(pts)>=2:thin.draw_polyline(pts);hthin=True
   else:shape.draw_polyline(pts+[pts[0]]);have=True
   paths+=1
  color=tuple(float(v)/255 for v in col)
  if have:shape.finish(color=color,fill=color,width=.50,even_odd=True,closePath=True);shape.commit()
  if hthin:thin.finish(color=color,width=.38,closePath=False);thin.commit()
 for x,y,x1,y1 in art:
  buf=io.BytesIO();Image.fromarray(bg[y:y1,x:x1]).save(buf,format='PNG');page.insert_image(fitz.Rect(x*SX,y*SY,x1*SX,y1*SY),stream=buf.getvalue())
 # Recover continuous and dotted grid rules after the text has been removed.
 g=cv2.cvtColor(bg,cv2.COLOR_RGB2GRAY);dark=(g<170).astype('uint8')*255
 for typ in ['h','v']:
  closed=cv2.morphologyEx(dark,cv2.MORPH_CLOSE,np.ones((1,5) if typ=='h' else (5,1),np.uint8))
  opened=cv2.morphologyEx(closed,cv2.MORPH_OPEN,np.ones((1,60) if typ=='h' else (60,1),np.uint8))
  cs,_=cv2.findContours(opened,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
  for c in cs:
   x,y,w,h=cv2.boundingRect(c)
   if not ((typ=='h' and h<=7 and w>=60) or (typ=='v' and w<=7 and h>=60)):continue
   if any(max(0,min(x+w,a[2])-max(x,a[0]))*max(0,min(y+h,a[3])-max(y,a[1]))>.3*w*h for a in art):continue
   yy=y+h//2;xx=x+w//2
   coverage=float((dark[yy,x:x+w]>0).mean()) if typ=='h' else float((dark[y:y+h,xx]>0).mean())
   pixels=bg[y:y+h,x:x+w][dark[y:y+h,x:x+w]>0];color=tuple(float(v)/255 for v in np.median(pixels,axis=0)) if len(pixels) else (.5,.5,.5)
   a=(x*SX,yy*SY) if typ=='h' else (xx*SX,y*SY);b=((x+w)*SX,yy*SY) if typ=='h' else (xx*SX,(y+h)*SY)
   page.draw_line(a,b,color=color,width=.35,dashes='[.6 1] 0' if coverage<.8 else None)
 return len(art),paths

def draw_line(page,line,samp,audit):
 text=line['text'].replace('□',' ').strip();text=re.sub(r'^➢\s*','➢ ',text);a=samp['mask'];h,w=a.shape
 if samp['graphic']:
  x0,y0,x1,y1=line['bbox'];anchor=fitz.Point(x0*SX,(y1-3)*SY);size=max(3,(y1-y0)*SY*.8);gkey='R' if all(fonts['R'].has_glyph(ord(c)) for c in text) else ('S' if all(fonts['S'].has_glyph(ord(c)) for c in text) else 'M');width=fonts[gkey].text_length(text,fontsize=size);sc=(x1-x0)*SX/max(.1,width)
  if text:page.insert_text(anchor,text,fontname=gkey,fontsize=size,render_mode=3,morph=(anchor,fitz.Matrix(sc,1)))
  audit.append({'id':line['id'],'text':text,'bbox':[x0*SX,y0*SY,x1*SX,y1*SY],'font':gkey,'size':size,'graphic':True});return
 if not text:return
 if samp['vertical']:
  rect=samp['vrect'];pb=pilfonts['R'].getbbox(text,anchor='ls');fs=(rect[2]-rect[0])*100/max(1,pb[3]-pb[1]);vv=(rect[3]-rect[1])/max(1,(pb[2]-pb[0])*fs/100);anchor=fitz.Point((rect[2]-pb[3]*fs/100)*SX,(rect[3]+pb[0]*fs/100)*SY)
  page.insert_text(anchor,text,fontname='R',fontsize=fs*SY,rotate=90,color=samp['color'],morph=(anchor,fitz.Matrix(1,vv)))
  audit.append({'id':line['id'],'text':text,'bbox':[rect[0]*SX,rect[1]*SY,rect[2]*SX,rect[3]*SY],'font':'R','size':fs*SY,'vertical':True});return
 tm,_=base.template(text,'R');fs=h*100/max(1,tm.shape[0]);fs=min(130,max(7,fs))
 # Exact short maths labels should not stretch to include surrounding diagram ink.
 spans=base.word_spans(text,a,fs)
 if text.startswith('➢ ') and text[2:].strip():
  cols=(a>0).any(axis=0);runs=[];st=None
  for xx,v in enumerate(list(cols)+[True]):
   if not v and st is None:st=xx
   elif v and st is not None:
    if st>3 and xx-st>=3:runs.append((st,xx))
    st=None
  if runs:
   lo,hi=runs[0];spans=[('➢',0,lo)]+[(word,l+hi,r+hi) for word,l,r in base.word_spans(text[2:],a[:,hi:],fs)]
 italic=base.line_slant(a)>.10
 tr,_=base.template(text,'I' if italic else 'R');tr=cv2.resize(tr,(w,h),interpolation=cv2.INTER_AREA)>150
 od0=cv2.distanceTransform(np.pad((a>0).astype('uint8'),1),cv2.DIST_L2,5);td0=cv2.distanceTransform(np.pad(tr.astype('uint8'),1),cv2.DIST_L2,5)
 line_ratio=od0[od0>0].mean()/max(.01,td0[td0>0].mean()) if (od0>0).any() and (td0>0).any() else 1
 line_bold=line_ratio>1.28 and ((a>0).mean()-tr.mean())>.04

 baseline=samp['y']+h-pilfonts['R'].getbbox(text,anchor='ls')[3]*fs/100
 for j,(word,l,r) in enumerate(spans):
  if not word.strip():continue
  wa=a[:,l:r];bb=base.trim(wa)
  if not bb:continue
  lx,ty,rx,by=bb;tight=wa[ty:by,lx:rx];basekey='I' if italic else 'R';tm,_=base.template(word,basekey);tt=cv2.resize(tm,(tight.shape[1],tight.shape[0]),interpolation=cv2.INTER_AREA);td=cv2.distanceTransform(np.pad((tt>150).astype('uint8'),1),cv2.DIST_L2,5);od=cv2.distanceTransform(np.pad((tight>0).astype('uint8'),1),cv2.DIST_L2,5)
  ratio=(od[od>0].mean() if (od>0).any() else 1)/max(.01,td[td>0].mean() if (td>0).any() else 1);density=(tight>0).mean()-(tt>150).mean()
  word_italic=italic
  if tight.shape[1]>=30 and len(word)>3:
   candidate_italic=base.line_slant(tight)>.13
   if candidate_italic:
    ri,_=base.template(word,'R');ii,_=base.template(word,'I');ri=cv2.resize(ri,(tight.shape[1],tight.shape[0]),interpolation=cv2.INTER_AREA)>128;ii=cv2.resize(ii,(tight.shape[1],tight.shape[0]),interpolation=cv2.INTER_AREA)>128;target=tight>0
    word_italic=float(np.mean(target!=ii))+.025<float(np.mean(target!=ri))
   else:word_italic=False
  if line.get('force_italic'):word_italic=True
  bold=line_bold or (len(word)>3 and ratio>1.45 and density>.07) or (j==0 and line.get('bold_first_word'))
  key=('BI' if bold else 'I') if word_italic else ('B' if bold else 'R')
  if text.isupper() and len(text)>=3:key='B'
  if not all(fonts[key].has_glyph(ord(c)) for c in word):key='S'
  word_fs=fs
  if key=='S':
   pb=_special_pil.getbbox(word,anchor='ls');word_fs=(by-ty)*100/max(1,pb[3]-pb[1]);glyphwidth=(pb[2]-pb[0])*word_fs/100;left=pb[0]*word_fs/100
  else:
   pb=pilfonts[key].getbbox(word,anchor='ls');glyphwidth=(pb[2]-pb[0])*fs/100;left=pb[0]*fs/100
  sx=(rx-lx)/max(1,glyphwidth);xx=samp['x']+l+lx-left*sx;yy=baseline
  if key=='S':yy=samp['y']+by-pb[3]*word_fs/100
  if key!='S':
   candidate=samp['y']+by-pb[3]*fs/100
   if abs(candidate-baseline)<3:yy=candidate
  anchor=fitz.Point(xx*SX,yy*SY)
  col=samp['color'];pp=samp['pixels'][ty:by,l+lx:l+rx];ink=tight>0
  if pp.shape[:2]==ink.shape and ink.any():
   pixels=pp[ink];dist=np.linalg.norm(pixels.astype('float32')-samp['bg'],axis=1);core=pixels[dist>=np.percentile(dist,70)];col=tuple(float(v)/255 for v in np.median(core,axis=0))
  page.insert_text(anchor,word+(' ' if j<len(spans)-1 else ''),fontname=key,fontsize=word_fs*SY,color=col,morph=(anchor,fitz.Matrix(sx*SX/SY,1)))
  audit.append({'id':line['id'],'text':word,'bbox':[xx*SX,(samp['y']+ty)*SY,(xx+rx-lx)*SX,(samp['y']+by)*SY],'font':key,'size':word_fs*SY})

def overlays(page,n):
 d=json.loads((P/'original'/f'{n:03}_existing.json').read_text())
 for b in d['blocks']:
  if 'lines' not in b:continue
  if b['bbox'][3]>20 and b['bbox'][1]<PH-32:continue
  for l in b['lines']:
   for s in l['spans']:
    text=s['text'];origin=fitz.Point(*s['origin']);size=s['size'];color=s['color'];c=tuple(((color>>x)&255)/255 for x in (16,8,0));
    if s.get('alpha',255)==0:
     image=np.array(Image.open(P/'original'/f'{n:03}.png').convert('RGB'));yy0=0 if s['bbox'][1]<20 else 1363;yy1=39 if yy0==0 else H;region=image[yy0:yy1];g=cv2.cvtColor(region,cv2.COLOR_RGB2GRAY);thr,_=cv2.threshold(g,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU);px=region[g<=thr];c=tuple(float(v)/255 for v in np.median(px,axis=0)) if len(px) else (.74,.73,.86)
    natural=fonts['N'].text_length(text,fontsize=size);desired=s['bbox'][2]-s['bbox'][0];scale=desired/max(.1,natural)
    page.insert_text(origin,text,fontname='N',fontsize=size,color=c,fill_opacity=(s.get('alpha',255)/255 if s.get('alpha',255)>0 else 1),morph=(origin,fitz.Matrix(scale,1)))

SOURCE=fitz.open('/workspace/attachments/cecec318-7f23-49d3-a715-571ce2214144/数学2023_哈语学生_哈语教材（4-2）_АЛМАТЫКІТАП.pdf')
NATIVE_PAGES={2,3,142,144}

def main():
 args=sys.argv[1:];folder=args.pop(0) if args and args[0] in ('raw','round1','round2','final') else 'final';nums=list(map(int,args)) if args else list(range(1,145));doc=fitz.open();audits=[];built=[]
 (P/'samples').mkdir(exist_ok=True)
 for n in nums:
  if not (P/'raw'/f'{n:03}.json').exists():continue
  t=time.time();data=final_data(n,folder);rgb=np.array(Image.open(P/'original'/f'{n:03}.png').convert('RGB'));rgb=cv2.resize(rgb,(W,H))
  if n in NATIVE_PAGES:
   doc.insert_pdf(SOURCE,from_page=n-1,to_page=n-1);page=doc[-1]
   page.clean_contents(sanitize=True)
   for k,f in fonts.items():page.insert_font(fontname=k,fontbuffer=f.buffer)
   for l in data['lines']:
    text=l['text'].replace('□',' ').strip()
    if not text or not l.get('native_graphic_extra'):continue
    x,y,u,v=l['bbox'];anchor=fitz.Point(x*SX,(v-1)*SY);key='R' if all(fonts['R'].has_glyph(ord(c)) for c in text) else 'S';sz=max(2.5,(v-y)*SY*.8);width=fonts[key].text_length(text,fontsize=sz);scale=(u-x)*SX/max(.1,width)
    page.insert_text(anchor,text,fontname=key,fontsize=sz,render_mode=3,morph=(anchor,fitz.Matrix(scale,1)))
   aa=[{'id':l['id'],'text':l['text'],'bbox':[l['bbox'][0]*SX,l['bbox'][1]*SY,l['bbox'][2]*SX,l['bbox'][3]*SY],'font':'native','size':max(2,(l['bbox'][3]-l['bbox'][1])*SY*.8),'native':True} for l in data['lines'] if l['text'].strip() and not is_overlay(l)]
   audits.append({'page':n,'spans':aa,'artworks':len(page.get_images()),'paths':len(page.get_drawings()),'native_preserved':True});built.append(n)
   print(n,'native preserved',len(aa),flush=True);continue
  EXTRA_ART[n]=list(MANUAL_ART.get(n,[]))
  yellow=((rgb[:,:,0]>175)&(rgb[:,:,1]>135)&(rgb[:,:,2]<185)&(rgb[:,:,0].astype('int16')-rgb[:,:,2]>40)&(rgb[:,:,1].astype('int16')-rgb[:,:,2]>20)).astype('uint8')*255
  yellow=cv2.morphologyEx(yellow,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))
  count,lab,stats,centroids=cv2.connectedComponentsWithStats(yellow)
  for x,y,w,h,ar in stats[1:]:
   if ar>10000 and w>120 and h>90 and ar/(w*h)>.45:EXTRA_ART[n].append((max(0,int(x)-3),max(40,int(y)-3),min(W,int(x+w)+3),min(1363,int(y+h)+3)))
  rules=get_rulemask(rgb,n);removal=np.zeros((H,W),np.uint8);samples=[]
  for line in data['lines']:
   if not line['text'].strip() or is_overlay(line):continue
   if False and re.match(r'^[А-ЯЁ][а-яё́-]+[. ]',line['text']) and 145<line['bbox'][0]<185:line=dict(line,bold_first_word=True)
   sample=sample_line(rgb,line,rules)
   if sample is None:continue
   if line.get('source_graphic') or line['text'].strip()=='□':
    sample['graphic']=True
    x,y,x1,y1=line['bbox'];EXTRA_ART[n].append((max(0,int(x)-2),max(40,int(y)-2),min(W,int(x1)+2),min(1363,int(y1)+2)))
   # Handwritten labels on yellow notes remain faithful illustration crops.
   if sample['bg'][0]>180 and sample['bg'][1]>150 and sample['bg'][2]<180:sample['graphic']=True
   x0,y0,x1,y1=line['bbox']
   if any(max(0,min(x1,a[2])-max(x0,a[0]))*max(0,min(y1,a[3])-max(y0,a[1]))>.45*max(1,(x1-x0)*(y1-y0)) for a in MANUAL_ART.get(n,[])):sample['graphic']=True
   if sample['graphic']:
    EXTRA_ART[n].append((max(0,int(x0)-2),max(40,int(y0)-2),min(W,int(x1)+2),min(1363,int(y1)+2)))
   if not sample['graphic']:removal|=sample['removal']
   samples.append((line,sample))
  protected=np.zeros((H,W),np.uint8)
  for line,sample in samples:
   if sample['graphic']:
    x,y,x1,y1=line['bbox'];cv2.rectangle(protected,(max(0,int(x)-2),max(0,int(y)-2)),(min(W-1,int(x1)+2),min(H-1,int(y1)+2)),255,-1)
  for x,y,x1,y1 in EXTRA_ART[n]:cv2.rectangle(protected,(x,y),(x1,y1),255,-1)
  removal=cv2.dilate(removal,np.ones((3,3),np.uint8));removal[(rules>0)|(protected>0)]=0
  bg=cv2.inpaint(rgb,removal,3,cv2.INPAINT_TELEA)
  for line,sample in samples:
   if (sample['flat'] or len(line['text'].strip())>12) and not sample['graphic']:
    poly=np.array(line.get('poly',[[line['bbox'][0],line['bbox'][1]],[line['bbox'][2],line['bbox'][1]],[line['bbox'][2],line['bbox'][3]],[line['bbox'][0],line['bbox'][3]]]),np.int32)
    m=np.zeros((H,W),np.uint8);cv2.fillPoly(m,[poly],255);m=cv2.dilate(m,np.ones((5,5),np.uint8));m[(rules>0)|(protected>0)]=0
    bg[m>0]=np.round(sample['bg']).clip(0,255).astype('uint8')
  # Restore only the pale publisher marks actually visible in the source, respecting opaque panels.
  z=rgb.astype('int16');pink=(z[:,:,0]>200)&(z[:,:,1]>170)&(z[:,:,2]>185)&(z[:,:,0]-z[:,:,1]>9)&(z[:,:,2]-z[:,:,1]>3)
  bg[pink]=rgb[pink]
  med=cv2.medianBlur(bg,3);near=np.max(np.abs(bg.astype('int16')-med.astype('int16')),axis=2)<20;bg[near]=med[near]

  for aa,bb in [(0,39),(1363,H)]:
   pixels=rgb[aa:bb].reshape(-1,3);q=(pixels//16).astype('int16');codes=q[:,0]*256+q[:,1]*16+q[:,2];co=np.bincount(codes,minlength=4096).argmax();bg[aa:bb]=np.median(pixels[codes==co],axis=0).astype('uint8')
  page=doc.new_page(width=PW,height=PH)
  for k,f in fonts.items():page.insert_font(fontname=k,fontbuffer=f.buffer)
  arts,paths=paint_background(page,bg,n);audit=[]
  for line,sample in samples:draw_line(page,line,sample,audit)
  overlays(page,n);audits.append({'page':n,'spans':audit,'artworks':arts,'paths':paths});built.append(n)
  print(n,'lines',len(samples),'words',len(audit),'arts',arts,'paths',paths,'sec',round(time.time()-t,1),flush=True)
  if args and len(nums)<10:Image.fromarray(bg).save(P/'samples'/f'{n:03}_clean.png')
 tag=os.environ.get('KAZ_BATCH','');out=P/(('batch_'+tag+'.pdf') if tag else ('draft.pdf' if args else 'rebuilt.pdf'));doc.subset_fonts();doc.save(out,garbage=2,deflate=True)
 (P/(('audit_'+tag+'.json') if tag else ('audit_draft.json' if args else 'audit.json'))).write_text(json.dumps(audits,ensure_ascii=False,indent=2))
 if args and len(nums)<10:
  for i,p in enumerate(doc):p.get_pixmap(matrix=fitz.Matrix(2,2)).save(P/'samples'/f'{built[i]:03}_rebuilt.png')
if __name__=='__main__':main()
