from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,re,math,collections
P=Path('/workspace/math2026p2_work');O=P/'adjudication';O.mkdir(exist_ok=True)
load=lambda p:json.loads(p.read_text());items=[];decisions=[]
def norm(s):
 s=re.sub(r'\s+','',s or '').replace('–','−').replace('—','−')
 return s

def ov(a,b):return max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
def area(b):return max(1,(b[2]-b[0])*(b[3]-b[1]))
def near(a,b):return ov(a,b)/min(area(a),area(b))>.3 or (abs((a[0]+a[2]-b[0]-b[2])/2)<22 and abs((a[1]+a[3]-b[1]-b[3])/2)<20)
for n in range(1,181):
 r=load(P/'raw'/f'{n:03}.json');a=load(P/'round1'/f'{n:03}.json');b=load(P/'round2'/f'{n:03}.json');regions=a.get('math_regions',[])+b.get('math_regions',[])
 for l in r['lines']:
  aa=a['corrections'].get(l['id'],l['text']);bb=b['corrections'].get(l['id'],l['text'])
  if aa==bb:continue
  if norm(aa)==norm(bb):kind='spacing'
  elif any(ov(l['bbox'],z['bbox'])>.4*area(l['bbox']) for z in regions):kind='spatial_line'
  else:kind='text'
  items.append({'key':f'L{n:03}:{l["id"]}','kind':kind,'page':n,'bbox':l['bbox'],'raw':l['text'],'a':aa,'b':bb})
 # Addition correspondence records are geometric and textual, not model authority.
 used=set()
 for ia,aa in enumerate(a['additions']):
  matches=[(j,bb) for j,bb in enumerate(b['additions']) if j not in used and near(aa['bbox'],bb['bbox'])]
  same=next(((j,bb) for j,bb in matches if norm(aa['text'])==norm(bb['text'])),None)
  if same:used.add(same[0]);continue
  best=max(matches,key=lambda v:ov(aa['bbox'],v[1]['bbox'])/min(area(aa['bbox']),area(v[1]['bbox'])),default=None)
  if best:
   j,bb=best;used.add(j);box=[min(aa['bbox'][0],bb['bbox'][0]),min(aa['bbox'][1],bb['bbox'][1]),max(aa['bbox'][2],bb['bbox'][2]),max(aa['bbox'][3],bb['bbox'][3])];items.append({'key':f'A{n:03}:{ia}:{j}','kind':'addition','page':n,'bbox':box,'a':aa['text'],'b':bb['text'],'a_index':ia,'b_index':j})
  else:items.append({'key':f'A{n:03}:{ia}:-','kind':'addition','page':n,'bbox':aa['bbox'],'a':aa['text'],'b':'','a_index':ia,'b_index':None})
 for j,bb in enumerate(b['additions']):
  if j not in used:items.append({'key':f'A{n:03}:-:{j}','kind':'addition','page':n,'bbox':bb['bbox'],'a':'','b':bb['text'],'a_index':None,'b_index':j})
 # Full math-region transcripts: exact text agreement needs no new adjudication.
 used=set()
 for ia,aa in enumerate(a.get('math_regions',[])):
  matches=[(j,bb) for j,bb in enumerate(b.get('math_regions',[])) if j not in used and near(aa['bbox'],bb['bbox'])]
  same=next(((j,bb) for j,bb in matches if norm(aa.get('transcription',''))==norm(bb.get('transcription',''))),None)
  if same:used.add(same[0]);continue
  best=max(matches,key=lambda v:ov(aa['bbox'],v[1]['bbox'])/min(area(aa['bbox']),area(v[1]['bbox'])),default=None)
  if best:
   j,bb=best;used.add(j);box=[min(aa['bbox'][0],bb['bbox'][0]),min(aa['bbox'][1],bb['bbox'][1]),max(aa['bbox'][2],bb['bbox'][2]),max(aa['bbox'][3],bb['bbox'][3])];items.append({'key':f'M{n:03}:{ia}:{j}','kind':'math','page':n,'bbox':box,'a':aa.get('transcription',''),'b':bb.get('transcription',''),'a_index':ia,'b_index':j})
  else:items.append({'key':f'M{n:03}:{ia}:-','kind':'math','page':n,'bbox':aa['bbox'],'a':aa.get('transcription',''),'b':'','a_index':ia,'b_index':None})
 for j,bb in enumerate(b.get('math_regions',[])):
  if j not in used:items.append({'key':f'M{n:03}:-:{j}','kind':'math','page':n,'bbox':bb['bbox'],'a':'','b':bb.get('transcription',''),'a_index':None,'b_index':j})
(P/'differences.json').write_text(json.dumps(items,ensure_ascii=False,indent=2));print(dict(collections.Counter(i['kind'] for i in items)))
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',19);small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
# Per-group contact sheets contain actual source crops, plus both proposals. No decisions are prefilled.
for kind in ['text','addition','math','spacing','spatial_line']:
 group=[i for i in items if i['kind']==kind];per=10 if kind in ['math','addition'] else 12
 for start in range(0,len(group),per):
  part=group[start:start+per];tilew=1100;tileh=260 if kind in ['math','addition'] else 225;sheet=Image.new('RGB',(tilew*2,tileh*math.ceil(len(part)/2)),'#eef2f5');dr=ImageDraw.Draw(sheet)
  for j,it in enumerate(part):
   xx=(j%2)*tilew;yy=(j//2)*tileh;b=it['bbox'];x0=max(0,int(b[0])-12);y0=max(0,int(b[1])-10);x1=min(1190,int(b[2])+12);y1=min(1684,int(b[3])+10);im=Image.open(P/'original'/f'{it["page"]:03}.png').crop((x0,y0,x1,y1));im.thumbnail((tilew-24,tileh-110));sheet.paste(im,(xx+12,yy+32));dr.text((xx+8,yy+3),it['key'],font=font,fill='navy')
   labely=yy+tileh-80
   for k,color in [('a','#7a241b'),('b','#155b34')]:
    s=it[k].replace('\n',' | ');out='';cnt=0
    for c in s:
     if dr.textlength(out+c,font=small)>tilew-40:break
     out+=c
    if out!=s:out+=' …'
    dr.text((xx+12,labely),k.upper()+': '+(out or '∅'),font=small,fill=color);labely+=32
  f=O/f'{kind}_{start//per:03}.png';sheet.save(f)
 print(kind,len(group),'sheets',math.ceil(len(group)/per))
