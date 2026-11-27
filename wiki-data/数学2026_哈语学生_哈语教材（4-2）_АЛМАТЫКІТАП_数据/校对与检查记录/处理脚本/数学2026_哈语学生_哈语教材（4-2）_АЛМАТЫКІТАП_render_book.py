"""Rebuild visible body text, vector panels/rules, and localized graphics. No full-page body scan overlay."""
import sys,os,json,time,io,functools,importlib.util,re
from pathlib import Path
sys.path.append('/workspace/ocr_work/venv/lib/python3.12/site-packages')
import fitz,numpy as np,cv2
from PIL import Image,ImageFont,ImageDraw
P=Path('/workspace/math2026p2_work');spec=importlib.util.spec_from_file_location('prior_math_renderer','/workspace/math2023p2_work/rebuild.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
W,H=1190,1684;PW,PH=594.96,841.92;SX,SY=PW/W,PH/H
m.P=P;m.W=W;m.H=H;m.PW=PW;m.PH=PH;m.SX=SX;m.SY=SY
families={}
for fam,prefix in [('T','/usr/share/fonts/truetype/liberation/LiberationSerif-'),('S','/usr/share/fonts/truetype/open-sans/OpenSans-')]:
 ff={k:fitz.Font(fontfile=prefix+name+'.ttf') for k,name in {'R':'Regular','B':'Bold','I':'Italic','BI':'BoldItalic'}.items()};pf={k:ImageFont.truetype(prefix+name+'.ttf',100) for k,name in {'R':'Regular','B':'Bold','I':'Italic','BI':'BoldItalic'}.items()};families[fam]=(ff,pf)
fallback={'S':fitz.Font(fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),'M':fitz.Font(fontfile='/usr/share/fonts/truetype/noto/NotoSansSymbols-Regular.ttf'),'N':fitz.Font(fontfile='/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf')}
CURRENT='T';registered={fam+k:f for fam,(ff,pf) in families.items() for k,f in ff.items()};registered.update({'U'+k:f for k,f in fallback.items()})
@functools.lru_cache(maxsize=40000)
def cached_template(fam,text,key):
 font=families[fam][1][key];bb=font.getbbox(text);im=Image.new('L',(max(1,bb[2]-bb[0]+4),max(1,bb[3]-bb[1]+4)),0);ImageDraw.Draw(im).text((2-bb[0],2-bb[1]),text,font=font,fill=255);a=np.array(im);b=m.base.trim(a>128)
 return (a[b[1]:b[3],b[0]:b[2]] if b else np.ones((1,1),np.uint8)*255),bb

def set_family(fam):
 global CURRENT
 CURRENT=fam;ff,pf=families[fam];m.fonts={**ff,**fallback};m.pilfonts=pf;m.base.fonts=m.fonts;m.base.pilfonts=pf
m.base.template=lambda text,key:cached_template(CURRENT,text,key)
set_family('T')
class Proxy:
 def __init__(self,page,fam):self.page=page;self.fam=fam
 def insert_text(self,*args,**kw):
  k=kw.get('fontname','R');kw['fontname']=('U'+k) if k in fallback else self.fam+k
  return self.page.insert_text(*args,**kw)
 def __getattr__(self,n):return getattr(self.page,n)

def choose_family(text,mask):
 h,w=mask.shape
 if len(text)<2:return ('S' if h>45 else 'T'),'R'
 if not text:return 'T','R'
 obs=mask>128;choices=[]
 for fam in ['T','S']:
  for sty in ['R','B','I','BI']:
   tm,_=cached_template(fam,text,sty);t=cv2.resize(tm,(w,h),interpolation=cv2.INTER_AREA)>128
   overlap=np.logical_and(t,obs).sum()/max(1,np.logical_or(t,obs).sum());density=abs(float(t.mean())-float(obs.mean()));score=overlap-1.2*density
   if len(text)>20 and h<45 and fam=='T':score+=.03
   if h>48 and fam=='S':score+=.02
   choices.append((score,fam,sty))
 best=max(choices);return best[1],best[2]
# Adapt the prior geometric background renderer to the full new page; source has no watermark bands.
import inspect
drawcode=inspect.getsource(m.draw_line).replace("if not all(fonts[key].has_glyph(ord(c)) for c in word):key='S'","if line.get('force_key'):key=line['force_key']\n  if not all(fonts[key].has_glyph(ord(c)) for c in word):key='S'")
exec(drawcode,m.__dict__)
code=inspect.getsource(m.artwork_boxes).replace('min(1363,','min(H,').replace('max(40,','max(0,').replace('range(40,H-55,','range(0,H,')
exec(code,m.__dict__)

def overlap(a,b):return max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
def box(l):return list(map(float,l['bbox']))
def graphics(n,data):
 regions=list(data.get('math_regions',[]));result=[list(map(int,r['bbox'])) for r in regions]
 # Covers are complete artwork. Ordinary textbook pages are rebuilt from text and vector/graphic fragments.
 if n in [1,180]:return [[0,0,W,H]]
 lay=json.loads((P/'layout'/f'{n:03}.json').read_text()).get('res',{})
 for b in lay.get('boxes',[]):
  if b['label'] not in ['image','chart','seal'] or b['score']<.65:continue
  a=[max(0,int(b['coordinate'][0])-3),max(0,int(b['coordinate'][1])-3),min(W,int(b['coordinate'][2])+3),min(H,int(b['coordinate'][3])+3)]
  if (a[2]-a[0])*(a[3]-a[1])<W*H*.30:result.append(a)
 return result

def inline_fraction_boxes(data,rgb):
 nums=[l for l in data['lines'] if re.fullmatch(r'\d{1,4}',l['text'].strip()) and l['bbox'][2]-l['bbox'][0]<120 and l['bbox'][3]-l['bbox'][1]<80]
 gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY);out=[]
 for a in nums:
  x,y,x1,y1=box(a);cx=(x+x1)/2;cy=(y+y1)/2
  for z in nums:
   xx,yy,xx1,yy1=box(z);cz=(yy+yy1)/2
   if not (8<cz-cy<65 and abs(cx-(xx+xx1)/2)<28 and max(x,xx)<min(x1,xx1)):continue
   bx=[max(0,int(min(x,xx))-2),max(0,int(y)-2),min(W,int(max(x1,xx1))+2),min(H,int(yy1)+2)]
   ink=(gray[bx[1]:bx[3],bx[0]:bx[2]]<125).astype('uint8')*255
   bars=cv2.morphologyEx(ink,cv2.MORPH_OPEN,np.ones((1,15),np.uint8));cs,_=cv2.findContours(bars,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
   if any(h<=4 and 15<=w<=110 and cy<by+bx[1]+h/2<cz for bx0,by,w,h in [cv2.boundingRect(c) for c in cs]):out.append(bx)
 return out

def draw_light_rules(page,rgb,data,art):
 gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY);ink=(gray<230).astype('uint8')*255
 for typ in ['h','v']:
  closed=cv2.morphologyEx(ink,cv2.MORPH_CLOSE,np.ones((1,7) if typ=='h' else (7,1),np.uint8));opened=cv2.morphologyEx(closed,cv2.MORPH_OPEN,np.ones((1,85) if typ=='h' else (85,1),np.uint8));cs,_=cv2.findContours(opened,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
  for c in cs:
   x,y,w,h=cv2.boundingRect(c);b=[x,y,x+w,y+h]
   if not ((typ=='h' and h<=6 and w>=85) or (typ=='v' and w<=6 and h>=85)):continue
   if any(overlap(b,a)>.3*w*h for a in art):continue
   if typ=='h' and any(l['bbox'][1]-2<=y+h/2<=l['bbox'][3]+2 and max(0,min(x+w,l['bbox'][2])-max(x,l['bbox'][0]))>.12*w for l in data['lines'] if l['text'].strip()):continue
   if typ=='v' and any(l['bbox'][0]-2<=x+w/2<=l['bbox'][2]+2 and max(0,min(y+h,l['bbox'][3])-max(y,l['bbox'][1]))>.12*h for l in data['lines'] if l['text'].strip()):continue
   mask=(gray[y:y+h,x:x+w]<230);pix=rgb[y:y+h,x:x+w][mask]
   if not len(pix):continue
   color=tuple(float(t)/255 for t in np.median(pix,axis=0));coverage=float(mask.mean());a=(x*SX,(y+h/2)*SY) if typ=='h' else ((x+w/2)*SX,y*SY);z=((x+w)*SX,(y+h/2)*SY) if typ=='h' else ((x+w/2)*SX,(y+h)*SY)
   page.draw_line(a,z,color=color,width=max(.25,min(.65,(h if typ=='h' else w)*SX)),dashes='[.6 1] 0' if coverage<.65 else None)

def merge_render_lines(data,art):
 items=[]
 for l in data['lines']:
  if not l['text'].strip():continue
  b=box(l);graphic=l.get('source_graphic') or (b[3]-b[1]>max(65,2*(b[2]-b[0]))) or any(overlap(b,a)>.3*max(1,(b[2]-b[0])*(b[3]-b[1])) for a in art)
  marker=(b[0]<W*.25 and re.fullmatch(r'\d{1,3}[А-ЯӘҒҚҢӨҰҮҺІа-яәғқңөұүһі]?',l['text'].strip()) and (b[2]-b[0]<65 or b[1]<160))
  items.append((l,graphic or marker or bool(re.fullmatch(r'\d{1,4}',l['text'].strip()))))
 rows=[];singles=[]
 for l,exclude in sorted(items,key=lambda v:((v[0]['bbox'][1]+v[0]['bbox'][3])/2,v[0]['bbox'][0])):
  b=box(l);hh=b[3]-b[1];cy=(b[1]+b[3])/2
  if exclude:singles.append(dict(l,_source_line_ids=[l['id']]));continue
  hit=None
  for row in reversed(rows[-5:]):
   if abs(row['cy']-cy)<min(row['h'],hh)*.23 and min(row['h'],hh)/max(row['h'],hh)>.60:hit=row;break
  if hit is None:rows.append({'cy':cy,'h':hh,'items':[l]})
  else:hit['items'].append(l)
 for row in rows:
  group=[]
  def push(group):
   if not group:return
   if len(group)==1:singles.append(dict(group[0],_source_line_ids=[group[0]['id']]));return
   bb=[min(x['bbox'][0] for x in group),min(x['bbox'][1] for x in group),max(x['bbox'][2] for x in group),max(x['bbox'][3] for x in group)]
   singles.append({'id':'row:'+','.join(x['id'] for x in group),'text':' '.join(x['text'].strip() for x in group),'bbox':bb,'poly':[[bb[0],bb[1]],[bb[2],bb[1]],[bb[2],bb[3]],[bb[0],bb[3]]],'_source_line_ids':[x['id'] for x in group]})
  for l in sorted(row['items'],key=lambda x:x['bbox'][0]):
   if group and l['bbox'][0]-group[-1]['bbox'][2]>30:push(group);group=[]
   group.append(l)
  push(group)
 return sorted(singles,key=lambda l:(round(l['bbox'][1]/7),l['bbox'][0]))

def build(nums,folder,tag):
 doc=fitz.open();audits=[]
 for n in nums:
  start=time.time();src=P/folder/f'{n:03}.json'
  if not src.exists():raise RuntimeError(f'Missing {src}')
  data=json.loads(src.read_text());rgb=np.array(Image.open(P/'original'/f'{n:03}.png').convert('RGB'));assert rgb.shape[:2]==(H,W)
  protected_regions=graphics(n,data)+inline_fraction_boxes(data,rgb);m.EXTRA_ART[n]=protected_regions[:]
  protected_regions+=m.artwork_boxes(rgb,n);m.EXTRA_ART[n]=protected_regions[:]
  if n in [1,180]:
   page=doc.new_page(width=PW,height=PH);page.insert_image(page.rect,filename=str(P/'original'/f'{n:03}.png'));audit=[]
   for k,f in registered.items():page.insert_font(fontname=k,fontbuffer=f.buffer)
   for l in data['lines']:
    t=l['text'].strip()
    if not t:continue
    b=box(l);size=max(2,(b[3]-b[1])*SY*.75);key='US';anchor=fitz.Point(b[0]*SX,b[3]*SY-size*.12);scale=(b[2]-b[0])*SX/max(.1,fallback['S'].text_length(t,fontsize=size));page.insert_text(anchor,t,fontname=key,fontsize=size,render_mode=3,morph=(anchor,fitz.Matrix(scale,1)));audit.append({'id':l['id'],'text':t,'graphic':True,'cover':True})
   audits.append({'page':n,'spans':audit,'cover_artwork':True});print(n,'cover',flush=True);continue
  rules=m.get_rulemask(rgb,n);samples=[];removal=np.zeros((H,W),np.uint8);protected=np.zeros((H,W),np.uint8)
  for a in protected_regions:cv2.rectangle(protected,(a[0],a[1]),(a[2],a[3]),255,-1)
  for line in merge_render_lines(data,protected_regions):
   t=line['text'].strip()
   if not t:continue
   b=box(line);art=line.get('source_graphic',False) or (b[3]-b[1]>max(65,2*(b[2]-b[0]))) or any(overlap(b,a)>.55*max(1,(b[2]-b[0])*(b[3]-b[1])) for a in protected_regions)
   sample=m.sample_line(rgb,line,np.zeros_like(rules))
   if sample is None:
    # No new text invented; explicitly preserve any source glyph and searchable value in a bounded crop.
    a=[max(0,int(b[0])-2),max(0,int(b[1])-2),min(W,int(b[2])+2),min(H,int(b[3])+2)];m.EXTRA_ART[n].append(a);cv2.rectangle(protected,(a[0],a[1]),(a[2],a[3]),255,-1)
    sample={'graphic':True,'mask':np.ones((max(1,int(b[3]-b[1])),max(1,int(b[2]-b[0]))),np.uint8),'color':(0,0,0),'vertical':False};samples.append((line,sample));continue
   art=art or (sample.get('graphic',False) and len(t)<45)
   sample['graphic']=art
   if art:
    a=[max(0,int(b[0])-2),max(0,int(b[1])-2),min(W,int(b[2])+2),min(H,int(b[3])+2)];m.EXTRA_ART[n].append(a);cv2.rectangle(protected,(a[0],a[1]),(a[2],a[3]),255,-1)
   else:removal|=sample['removal']
   samples.append((line,sample))
  removal=cv2.dilate(removal,np.ones((3,3),np.uint8));removal[protected>0]=0
  bg=cv2.inpaint(rgb,removal,3,cv2.INPAINT_TELEA)
  # Smooth the flat warm teaching panels after glyph removal; do not touch protected drawings.
  for line,sample in samples:
   col=np.asarray(sample.get('bg',[255,255,255]))
   if sample['graphic'] or len(line['text'])<8 or col[0]-col[2]<=25 or col.mean()<170:continue
   b=box(line);x0,y0,x1,y1=max(0,int(b[0])-1),max(0,int(b[1])-1),min(W,int(b[2])+1),min(H,int(b[3])+1)
   region=bg[y0:y1,x0:x1];free=protected[y0:y1,x0:x1]==0;region[free]=np.clip(col,0,255).astype('uint8')
  page=doc.new_page(width=PW,height=PH)
  for k,f in registered.items():page.insert_font(fontname=k,fontbuffer=f.buffer)
  arts,paths=m.paint_background(page,bg,n);audit=[]
  draw_light_rules(page,rgb,data,m.EXTRA_ART[n]+m.artwork_boxes(bg,n))
  for line,sample in samples:
   if sample['graphic']:
    # Localized source formula/illustration retains layout. Text object provides exact Unicode lookup.
    b=box(line);t=line['text'].strip().replace('\n',' | ');fs=max(2,(b[3]-b[1])*SY*.75);anchor=fitz.Point(b[0]*SX,(b[3]-2)*SY);sc=(b[2]-b[0])*SX/max(.1,fallback['S'].text_length(t,fontsize=fs));page.insert_text(anchor,t,fontname='US',fontsize=fs,render_mode=3,morph=(anchor,fitz.Matrix(sc,1)));audit.append({'id':line['id'],'text':t,'graphic':True,'bbox':b});continue
   fam,key=choose_family(line['text'],sample['mask']);key=('B' if fam=='T' and n>4 and not (len(line['text'])<14 and any(c.isalpha() and c.isascii() for c in line['text'])) else key);key=key.replace('I','') if key in ['I','BI'] and len(line['text'])>18 else key;key=key or 'R';
   badge=any(x in line['text'] for x in ['ЖАҢА ТАҚЫРЫПТЫ ОҚЫП-ҮЙРЕНУ','ПЫСЫҚТАУ','ТОПТЫҚ ЖҰМЫС','ӨЗДІК ЖҰМЫС','ЖҰПТЫҚ ЖҰМЫС','ҮЙ ТАПСЫРМАСЫ','ЕСТЕ САҚТА!','ОЙЛАН, ТАП!','ШЫҒАРМАШЫЛЫҚ ЖҰМЫС'])
   if n>4 and line['bbox'][1]<160 and len(line['text'])>3:fam,key='S','B'
   if n>4 and line['bbox'][1]>.15*H and not badge:fam,key='T','B'
   if fam=='T' and sample.get('bg',[0,0,0])[0]-sample.get('bg',[0,0,0])[2]>25:key='R'
   if badge:fam,key='S','R'
   if re.fullmatch(r'\d{1,3}',line['text'].strip()) and line['bbox'][1]>.94*H:fam,key='S','R'
   set_family(fam);before=len(audit);m.draw_line(Proxy(page,fam),dict(line,force_key=key),sample,audit)
   for a in audit[before:]:a['family']=fam;a['graphic']=False;a['source_line_ids']=line.get('_source_line_ids',[line['id']])
  audits.append({'page':n,'spans':audit,'artworks':arts,'paths':paths,'localized_graphic_regions':protected_regions})
  print(n,'text',sum(not a.get('graphic',False) for a in audit),'graphics',arts,'sec',round(time.time()-start,1),flush=True)
 doc.subset_fonts();target=P/f'{tag}.pdf';doc.save(target,garbage=3,deflate=True);(P/f'{tag}_audit.json').write_text(json.dumps(audits,ensure_ascii=False,indent=2));return target
if __name__=='__main__':
 folder=sys.argv[1];tag=sys.argv[2];nums=list(map(int,sys.argv[3:])) or list(range(1,181));print(build(nums,folder,tag),flush=True)
