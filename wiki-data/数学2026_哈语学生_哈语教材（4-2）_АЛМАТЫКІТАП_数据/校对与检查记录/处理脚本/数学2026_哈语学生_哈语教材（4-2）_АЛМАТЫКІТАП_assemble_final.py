from pathlib import Path
import json,re,copy,collections
P=Path('/workspace/math2026p2_work');load=lambda p:json.loads(p.read_text());reviews=load(P/'main_reviews_final.json');diffs=load(P/'differences.json');bykey={d['key']:d for d in diffs};decisions=[]
def norm(s):return re.sub(r'\s+','',s).replace('–','−').replace('—','−')
def plain(s):
 for _ in range(5):s=re.sub(r'\\frac\{([^{}]*)\}\{([^{}]*)\}',r'\1/\2',s)
 return s.replace('\\cdot','·').replace('\\times','×').replace('\\div',':')
def area(b):return max(1,(b[2]-b[0])*(b[3]-b[1]))
def ov(a,b):return max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
def near(a,b):return ov(a,b)/min(area(a),area(b))>.3 or (abs((a[0]+a[2]-b[0]-b[2])/2)<22 and abs((a[1]+a[3]-b[1]-b[3])/2)<20)
def pick(d):
 choice=reviews['choices'].get(d['key'],'a' if d['kind']=='spacing' else 'b');t=reviews['custom'].get(d['key'],d[choice]);decisions.append(dict(d,chosen_round=choice,final_text=t,main_source_crop_review=d['kind']!='spatial_line'));return choice,t
for n in range(1,181):
 raw=load(P/'raw'/f'{n:03}.json');a=load(P/'round1'/f'{n:03}.json');b=load(P/'round2'/f'{n:03}.json');out=copy.deepcopy(raw);regions=[];adds=[]
 for kind,field,textkey in [('math','math_regions','transcription'),('addition','additions','text')]:
  aa=a.get(field,[]);bb=b.get(field,[]);useda=set();usedb=set();picked=[]
  for d in diffs:
   if d['page']!=n or d['kind']!=kind:continue
   ia,ib=d.get('a_index'),d.get('b_index');
   if ia is not None:useda.add(ia)
   if ib is not None:usedb.add(ib)
   side,t=pick(d);idx=ia if side=='a' else ib
   if not t:continue
   source=(aa if side=='a' else bb)[idx] if idx is not None else {'bbox':d['bbox']}
   z=copy.deepcopy(source);z[textkey]=plain(t);z['adjudication_key']=d['key'];z['reviewer_transcription']=t;picked.append(z)
  for ia,z in enumerate(aa):
   if ia in useda:continue
   j=next((j for j,w in enumerate(bb) if j not in usedb and near(z['bbox'],w['bbox']) and norm(z.get(textkey,''))==norm(w.get(textkey,''))),None)
   if j is not None:usedb.add(j)
   zz=copy.deepcopy(z);zz[textkey]=plain(zz.get(textkey,''));zz['agreement']='two_rounds' if j is not None else 'retained_unmatched';picked.append(zz)
  if kind=='math':regions=picked
  else:adds=picked
 # Prefer complete, source-verified formula blocks over contained fragment regions.
 regions=sorted(regions,key=lambda z:-area(z['bbox']));rr=[]
 for z in regions:
  if any(ov(z['bbox'],w['bbox'])>.85*area(z['bbox']) for w in rr):continue
  rr.append(z)
 regions=rr;out['math_regions']=regions;unc=[]
 for r in [a,b]:
  for u in r.get('uncertainties',[]):
   if u not in unc:unc.append(u)
 out['uncertainties']=unc;out['lines']=[]
 for l in raw['lines']:
  z=copy.deepcopy(l);key=f'L{n:03}:{l["id"]}';aa=a['corrections'].get(l['id'],l['text']);bb=b['corrections'].get(l['id'],l['text']);d=bykey.get(key)
  if aa==bb:t=aa;reason='two_rounds_agree'
  elif d['kind']!='spatial_line':_,t=pick(d);reason='main_scan_adjudication'
  else:
   # A fragmented raw OCR line is suppressed only where a complete reviewed region replaces it.
   covered=any(ov(l['bbox'],r['bbox'])>.4*area(l['bbox']) for r in regions)
   t='' if covered else (aa if aa else bb);reason='reviewed_region_replaces_fragment' if covered else 'retain_uncovered_source_fragment'
  z.update(text=t,raw_text=l['text'],review_decision=reason)
  if key in reviews['geometry']:z['raw_bbox']=z['bbox'];z['bbox']=reviews['geometry'][key]
  if (6<=n<=174 and re.fullmatch(r'\d{2,3}(?:\s*[-–]\s*\d{2,3})?',t.strip()) and z['bbox'][1]<160 and z['bbox'][0]<250):z['source_graphic']=True
  if key in reviews['graphics'] or (n in [176,177] and t.strip().isdigit() and z['bbox'][0]>.8*1190):z['source_graphic']=True
  # Every raw line keeps its ID, including disabled fragments.
  out['lines'].append(z)
 # Mathematics uses localized source graphics, with a single searchable transcription per reviewed region.
 for i,r in enumerate(regions):
  ids=[]
  for l in out['lines']:
   if ov(l['bbox'],r['bbox'])>.55*area(l['bbox']):ids.append(l['id']);l['suppressed_region_text']=l['text'];l['text']='';l['review_decision']='localized_math_region'
  bbx=r['bbox'];out['lines'].append({'id':f'math_{i+1}','text':r['transcription'],'bbox':bbx,'source_graphic':True,'source_line_ids':ids,'poly':[[bbx[0],bbx[1]],[bbx[2],bbx[1]],[bbx[2],bbx[3]],[bbx[0],bbx[3]]],'origin':'main_reviewed_math_region'})
 for i,z in enumerate(adds):
  t=z['text'];bbx=z['bbox']
  if any(ov(bbx,r['bbox'])>.7*area(bbx) for r in regions):continue
  if any(l['text'] and norm(t) in norm(l['text']) and ov(bbx,l['bbox'])>.25*min(area(bbx),area(l['bbox'])) for l in out['lines']):continue
  out['lines'].append({'id':f'add_{i+1}','text':t,'bbox':bbx,'poly':[[bbx[0],bbx[1]],[bbx[2],bbx[1]],[bbx[2],bbx[3]],[bbx[0],bbx[3]]],'source_graphic':True,'origin':'proofreading_addition','adjudication':z})
 out['review']={'rounds':2,'independent_image_proofreading':True,'main_adjudication':'source_crop_comparison','source_preserved':True};(P/'final'/f'{n:03}.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
(P/'review'/'main_adjudication.json').write_text(json.dumps({'reviews':reviews,'decisions':decisions,'spatial_fragment_policy':'raw IDs retained; fragments replaced only within reviewed localized source math regions'},ensure_ascii=False,indent=2));print('pages',180,'active_lines',sum(bool(l['text']) for n in range(1,181) for l in load(P/'final'/f'{n:03}.json')['lines']))
