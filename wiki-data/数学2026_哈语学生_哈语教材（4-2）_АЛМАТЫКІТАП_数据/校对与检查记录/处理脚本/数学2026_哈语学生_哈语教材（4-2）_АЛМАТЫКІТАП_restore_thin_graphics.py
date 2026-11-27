"""Preserve sparse colored source curves that palette vectorization can weaken."""
from pathlib import Path
import sys,io
sys.path.append('/workspace/ocr_work/venv/lib/python3.12/site-packages')
import cv2,numpy as np,fitz
from PIL import Image
P=Path('/workspace/math2026p2_work')
def boxes(rgb,lines):
 a=rgb.astype('float32');mx=a.max(axis=2);mn=a.min(axis=2);sat=(mx-mn)/np.maximum(mx,1);ink=((sat>.32)&(mx>100)&(mn<210)).astype('uint8')*255
 dil=cv2.dilate(ink,np.ones((5,5),np.uint8));cs,_=cv2.findContours(dil,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE);out=[];H,W=rgb.shape[:2]
 for c in cs:
  x,y,w,h=cv2.boundingRect(c)
  if w<40 or h<25 or w*h>W*H*.08 or w*h<1800:continue
  if (ink[y:y+h,x:x+w]>0).mean()>.15:continue
  b=[max(0,x-10),max(0,y-10),min(W,x+w+10),min(H,y+h+10)]
  bad=False
  for l in lines:
   if len(l['text'])<60:continue
   z=l['bbox'];inter=max(0,min(b[2],z[2])-max(b[0],z[0]))*max(0,min(b[3],z[3])-max(b[1],z[1]));area=max(1,(z[2]-z[0])*(z[3]-z[1]))
   if inter>.12*area:bad=True;break
  if not bad:out.append(b)
 return out
def restore(page,data,audit=None):
 n=data['page'];im=Image.open(P/'original'/f'{n:03}.png').convert('RGB');rgb=np.array(im);bs=boxes(rgb,data['lines'])
 if n==156:
  bs.extend([[max(0,int(v)-3) if j<2 else int(v)+3 for j,v in enumerate(l['bbox'])] for l in data['lines'] if l['id']=='35'])
 if n==158:
  chosen=[l['bbox'] for l in data['lines'] if any(x in l['text'] for x in ['КӨК','ЖӨН','КӨЗ','СӨЗ'])]
  if chosen:bs.append([int(min(b[0] for b in chosen))-5,int(min(b[1] for b in chosen))-5,int(max(b[2] for b in chosen))+5,int(max(b[3] for b in chosen))+5])
 # A source illustration crop can touch part of a typeset caption. Restore only
 # those intersecting local rows, preventing a scan glyph plus a rebuilt glyph.
 if audit:
  placements=[list(z['bbox']) for z in page.get_image_info()];seen=set();lookup={l['id']:l for l in data['lines']}
  for span in audit['spans']:
   if span.get('graphic') or 'bbox' not in span:continue
   b=span['bbox'];area=max(1,(b[2]-b[0])*(b[3]-b[1]))
   hit=any(max(0,min(b[2],q[2])-max(b[0],q[0]))*max(0,min(b[3],q[3])-max(b[1],q[1]))>.05*area for q in placements)
   if not hit or span['id'] in seen:continue
   seen.add(span['id']);ids=span.get('source_line_ids',[span['id']]);rows=[lookup[v]['bbox'] for v in ids if v in lookup]
   if not rows:continue
   r=[int(min(z[0] for z in rows)),int(min(z[1] for z in rows)),int(max(z[2] for z in rows)),int(max(z[3] for z in rows))]
   if r[3]-r[1]<=110 and (r[2]-r[0])*(r[3]-r[1])<1190*1684*.06:bs.append(r)
  audit['source_caption_overlap_rows']=list(seen)
 for b in bs:
  stream=io.BytesIO();im.crop(b).save(stream,format='PNG');r=fitz.Rect(b[0]*page.rect.width/1190,b[1]*page.rect.height/1684,b[2]*page.rect.width/1190,b[3]*page.rect.height/1684);page.insert_image(r,stream=stream.getvalue())
 return bs
