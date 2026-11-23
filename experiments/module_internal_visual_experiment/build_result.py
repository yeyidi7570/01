"""Temporary visual experiment assembly. All module bounds are immutable input.
The explicit element plan below records Codex's direct visual judgments on 11 originals.
No OCR, model training, database schema, module resegmentation or source writes.
"""
from pathlib import Path
import json,hashlib,math,collections,base64,html,shutil,re,datetime
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent;P=R/'experiments/ai_textbook_pilot'
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
qall=[json.loads(l) for l in (P/'exercises.jsonl').read_text().splitlines()];M=load(P/'manifest.json');Q={(int(q['lesson_number']),int(q['exercise_number'])):q for q in qall};AS={a['pdf_page_number']:a for a in M['assets'] if a['role']=='source_page'};source_hashes={n:sha(P/n) for n in ['exercises.jsonl','labels.jsonl','manifest.json']};ALL=[];F=[];issues=[];TYPES=['module_badge','module_number','text','informative_image','table','formula','module_note','example','uncertain','other'];COLORS=dict(zip(TYPES,['#7c3aed','#be123c','#0369a1','#15803d','#b45309','#b91c1c','#a21caf','#0f766e','#d97706','#64748b']))

def choose(lesson,num,page=None):
 q=Q[lesson,num];n=page or q['bbox_refs'][0]['pdf_page_number'];b=next(v['bbox'] for v in q['bbox_refs'] if v['pdf_page_number']==n);f={'fragment_id':q['id']+f':p{n:03}','module_id':q['id'],'lesson_number':q['lesson_number'],'module_number':q['exercise_number'],'pdf_page_number':n,'scope':'context_only' if n==30 else 'sample','fixed_bbox':b[:],'elements':[],'background_layers':[{'type':'other','bbox':b[:],'role':'original_panel_background_border_and_watermark','notes':'背景、边框与原稿水印保持在扫描底图，不当作题干或新增模块，不计有效内容覆盖。'}],'inherited_issues':q['structure_status']['inherited_uncertainties']};F.append(f);return f

def refseq(f,seq):
 if not seq:return []
 if isinstance(seq,str):seq=seq.split()
 return [{'pdf_page_number':f['pdf_page_number'],'line_id':str(i)} for i in seq]
def getunits(f):return {(u['source_ref']['pdf_page_number'],u['source_ref']['line_id']):u for u in next(q for q in qall if q['id']==f['module_id'])['text_units']}
def rawtext(f,rr):
 U=getunits(f);return '\n'.join(U[r['pdf_page_number'],r['line_id']]['text'] for r in rr)
def unionbox(bb):return [min(b[0] for b in bb),min(b[1] for b in bb),max(b[2] for b in bb),max(b[3] for b in bb)]
def add(f,typ,seq='',bbox=None,parent=None,role='',note='',candidates=None,internal=None,problems=None):
 rr=refseq(f,seq);U=getunits(f)
 if bbox is None:
  assert rr,(typ,role);b=unionbox([U[r['pdf_page_number'],r['line_id']]['bbox'] for r in rr]);bbox=[b[0]-2,b[1]-2,b[2]+2,b[3]+2]
 original=bbox[:];b=f['fixed_bbox'];box=[max(b[0],bbox[0]),max(b[1],bbox[1]),min(b[2],bbox[2]),min(b[3],bbox[3])];assert box[0]<box[2] and box[1]<box[3],(typ,box,role)
 e={'element_id':f['fragment_id']+f':e{len([x for x in ALL if x["fragment_id"]==f["fragment_id"]])+1:03}','module_id':f['module_id'],'fragment_id':f['fragment_id'],'pdf_page_number':f['pdf_page_number'],'type':typ,'role':role,'bbox':box,'unclipped_visual_bbox':original,'original_ocr':rawtext(f,rr),'source_line_ids':rr,'children':[],'notes':note,'problems':list(problems or []),'candidate_types':candidates or [],'internal':internal,'is_container':typ in ['module_note','example'],'text_source':'existing_final_OCR_verbatim_no_rerun'}
 if original!=box:e['problems'].append('FIXED_BOUNDARY_CLIP：内部框被原模块边界裁切，未扩大原模块。')
 for r in rr:
  text=U[r['pdf_page_number'],r['line_id']]['text']
  if typ!='formula' and re.search(r'[-‐‑]$',text):e['problems'].append('POSSIBLE_WORD_SPLIT：原印换行或OCR断词候选，保留原行末字符：'+text)
 if typ=='formula' and len(rr)>1:e['problems'].append('MULTILINE_MATH_OCR：多行/竖式文字不是可靠线性公式，图像为准，未补写LaTeX、符号或答案。')
 if typ=='uncertain':e['problems'].append('TYPE_UNCERTAIN：'+note)
 (parent['children'] if parent else f['elements']).append(e);ALL.append(e);return e

def nums(f):
 q=next(q for q in qall if q['id']==f['module_id'])
 for r in q['numbering_evidence']:
  if r['source_ref']['pdf_page_number']!=f['pdf_page_number']:continue
  b=[r['bbox'][0]-3,r['bbox'][1]-3,r['bbox'][2]+3,r['bbox'][3]+3];pr=[]
  if (f['pdf_page_number'],r['source_ref']['line_id'])==(73,'30'):b=[113,881,155,919];pr=['原OCR编号框偏窄，视觉框覆盖整枚2А文字；原OCR内容不改。']
  add(f,'module_number',r['source_ref']['line_id'],b,role='printed_number_or_lettered_part',problems=pr)
def text(f,s,**kw):return add(f,'text',s,**kw)
def badge(f,s,**kw):return add(f,'module_badge',s,role='top_centered_capsule',**kw)
def formula(f,s,bbox=None,**kw):return add(f,'formula',s,bbox,**kw)

def cells_table(f,bbox,xs,ys,cellspec,notes,relations=None):
 rr=[];cells=[]
 for row,col,rs,cs,seq in cellspec:
  refs=refseq(f,seq);rr+=refs;cell={'row':row,'column':col,'rowspan':rs,'colspan':cs,'bbox':[xs[col],ys[row],xs[col+cs],ys[row+rs]],'original_ocr':rawtext(f,refs),'source_line_ids':refs,'line_boxes':[{'line_id':r['line_id'],'bbox':getunits(f)[r['pdf_page_number'],r['line_id']]['bbox'],'original_ocr':getunits(f)[r['pdf_page_number'],r['line_id']]['text']} for r in refs],'blank_in_original':not bool(refs)};cells.append(cell)
 seq=[r['line_id'] for r in rr];e=add(f,'table',seq,bbox,role='real_data_table',note=notes,internal={'row_count':len(ys)-1,'column_count':len(xs)-1,'cells':cells,'row_boundaries':ys,'column_boundaries':xs,'relations':relations or [],'blank_policy':'原版空白单元格保持空白，不补零或答案。','multiline_policy':'单元格内原OCR分行和连字符照留。'});return e

# PDF14 / Q1: real place-value table. Ordinary digit cells are not formulas.
f=choose(3,1);nums(f);text(f,'14 15 16',role='prompt');add(f,'uncertain','',[767,400,865,418],role='overhanging_source_decoration',note='页首角色的局部进入旧模块上沿，是否应算模块装饰待人工确认。',candidates=['other','informative_image'])
xs=[114,212,311,411,499,587,675,762,834,907];ys=[531,628,719,767,815,864,911,960];cs=[(0,0,1,3,'17 20'),(0,3,1,3,'18 21'),(0,6,1,3,'19 22')]
for col,s in enumerate(['23 32 42','24 33 43','25 34 44','26 36','28 37','29 38','30 39','27 35 40','31 41']):cs.append((1,col,1,1,s))
for row,ss in enumerate([['','','','','','45','46','47','48'],['','','','','50','51','52','53','54'],['','','','57','58','59','60','61','62'],['','','','64','65','66','67','68','69'],['','','71','72','73','74','75','76','77']],2):
 for col,s in enumerate(ss):cs.append((row,col,1,1,s))
cells_table(f,[114,531,907,960],xs,ys,cs,'上层三个类标题各跨3列，下层9个数位标题，多行断词保持原样；5行数值的空白不是0。')

# PDF29 Q1 and Q2 / PDF30 continuation: note owns printed examples, never new modules.
f=choose(7,1);nums(f);text(f,'10 11 12',role='prompt')
f=choose(7,2,29);nums(f);text(f,'13',role='prompt');note=add(f,'module_note','',[85,612,880,1305],role='remember_panel',note='同模块内部“记住”框，含说明、原印示例与解释步骤；不建独立模块。');text(f,'14',parent=note,role='note_title');text(f,'15 16 17 18 19',parent=note,role='note_body')
for b,s in [([101,934,279,1075],'22 a3 24 28'),([331,934,528,1075],'23 a4 25 29'),([101,1075,325,1247],'33 36 a5 39 41'),([331,1075,528,1247],'34 a6 37 40')]:
 ex=add(f,'example','',b,parent=note,role='printed_worked_example',note='题干原文要求解释每个例子，源图已印运算和结果。');formula(f,s,b,parent=ex,role='column_addition')
text(f,'20 21 26 27 30 31 32 35 38 42 43',bbox=[532,883,868,1260],parent=note,role='printed_algorithm_explanation',note='1–7是原印算法步骤号，不是模块编号。')
f=choose(7,2,30);text(f,'2',role='continuation_instruction');note=add(f,'module_note','',[112,267,910,836],role='remember_panel',note='第29页同模块续页，未印新模块号，不补造编号。');text(f,'3',parent=note,role='note_title');text(f,'4 5 6 7 8 9 10 11 12',parent=note,role='note_body')
for b,s in [([143,523,329,647],'15 a12 20 26'),([371,511,571,647],'16 a13 a0 27'),([143,664,329,809],'a1 a2 a3 37 a14 a10 54'),([342,664,571,809],'a4 a5 a6 a7 a8 a9 a15 a11 55')]:
 ex=add(f,'example','',b,parent=note,role='printed_worked_example');formula(f,s,b,parent=ex,role='column_subtraction_with_borrowing',problems=['竖式借位数字及划线仅保留原图和OCR行，不重建运算逻辑。'])
text(f,'13 14 17 18 19 24 25 28 29 30 36 44 45 47 56 57 58 59 60',bbox=[605,503,881,823],parent=note,role='printed_algorithm_explanation')

# PDF46 ordinary arithmetic, prose quantities stay text.
f=choose(11,4);nums(f);text(f,'3',role='instruction')
for i in range(4,13):formula(f,str(i),role='printed_expression')
f=choose(11,5);nums(f);text(f,'14',role='instruction')
for s in ['15','16','17','19','20 22','21','23','24','25']:formula(f,s,role='printed_division_expression',problems=['OCR将子题字母或单位与式子同行/分行记录，保持原字串。'] if s in ['15','19','20 22'] else [])
text(f,'18',role='conclusion_prompt');text(f,'26',role='conclusion_prompt')
f=choose(11,6);nums(f);text(f,'27 28',role='instruction');text(f,'29 30 31 32 33',role='subquestion_a');text(f,'34 35 36',role='subquestion_ae',note='正文中的25、20、500、50、5等数值仍是叙述条件，不独立标公式。')
f=choose(11,7);nums(f);text(f,'37',role='instruction')
for s,b in [('38 39 40',[150,1215,305,1258]),('41 42',[545,1215,835,1259]),('43 44',[150,1250,433,1292]),('45 46 47',[545,1250,837,1293])]:formula(f,s,b,role='conversion_with_blank_boxes',problems=['空白答案框保留原图；OCR未检出的框不补写到文字。'])

# PDF62 merged cells / bracket total.
f=choose(15,7);nums(f);badge(f,'2');text(f,'3',role='instruction');text(f,'4 5 6 7',role='word_problem')
f=choose(15,8);nums(f);badge(f,'8');text(f,'10',role='instruction_a');text(f,'11 12',role='subquestion_a');text(f,'14',role='instruction_ae')
cs=[(0,i,1,1,str(j)) for i,j in enumerate([15,16,17,18])]+[(1,0,1,1,'19'),(1,1,1,1,'20'),(1,2,2,1,'22'),(1,3,2,1,'21 26 23'),(2,0,1,1,'24'),(2,1,1,1,'25')]
t=cells_table(f,[114,660,906,773],[114,311,508,708,906],[660,702,736,773],cs,'数量“бірдей”与费用栏分别跨两行。两个问号与70 $同在合并费用区域，不虚构第五列。',[{'kind':'brace_shared_total','target_body_rows':[1,2],'total_source_line_ids':refseq(f,'23'),'brace_bbox':[789,702,811,769],'notes':'70 $是两行总价，不只属于Нан行。'}])
cost=next(c for c in t['internal']['cells'] if c['row']==1 and c['column']==3)
cost['layout']='two_row_unknowns_with_brace_and_shared_total';cost['value_line_ids']=['21','26'];cost['shared_total_line_id']='23'
f=choose(15,9);nums(f);badge(f,'27');text(f,'28',role='instruction');text(f,'29 30 31',role='word_problem')
f=choose(15,10);nums(f);badge(f,'32');text(f,'34',role='instruction');text(f,'36 38 40 41 42',role='word_problem');add(f,'other','35 37 39',[749,1059,932,1307],role='decorative_character_and_pedagogical_slogan',note='右侧角色及口号不增加题目数量条件，也非顶端居中模块标签。')

# PDF73-74: numeric card labels are informative-image content, not formulas.
f=choose(19,1);nums(f);text(f,'13 14 15',role='instruction');add(f,'informative_image','16 17 18 19 20 21 22 23 24 25 26 27',[95,447,870,787],role='balloon_and_number_card_scene',note='气球与卡片上的数值/词语用于选择和建立对应关系；人物属同一复合插图，数值不另当公式。')
f=choose(19,2,73);nums(f);badge(f,'28');text(f,'29 31 32',role='instruction_a');ex=add(f,'example','',[145,1000,860,1278],role='worked_multiplication_demonstration',note='原文要求观察已完成的算法；黄色背景不自动等于module_note。');formula(f,'a1 38 39 41',[150,1069,352,1215],parent=ex,role='column_multiplication');text(f,'33 34 37 40 42 43 44',bbox=[430,1024,835,1259],parent=ex,role='printed_algorithm_explanation')
f=choose(19,2,74);nums(f);badge(f,'14');text(f,'15 16 17 18 19',role='instruction_ae');ex=add(f,'example','',[159,480,888,890],role='worked_division_demonstration');formula(f,'a2 a3 a4 a5 a6 a7 a8 a9 a10 a11 a12 a13 a14 a15 a16 a17 a18 a19',[160,505,504,879],parent=ex,role='long_division_not_table');text(f,'20 25 30 37 40 42 44 46 48 49 50',bbox=[541,494,861,877],parent=ex,role='printed_algorithm_explanation')
f=choose(19,3);nums(f);badge(f,'52');text(f,'53',role='instruction')
for i in range(54,62):formula(f,str(i),role='printed_expression')

# PDF87 information-bearing quantitative diagrams vs uncertain fruit illustrations.
f=choose(22,7);nums(f);badge(f,'2');text(f,'4',role='instruction_a');text(f,'5 6 7 8',role='subquestion_a');add(f,'informative_image','9 10 11 12 13',[129,414,548,537],role='quantitative_brace_diagram',note='36、70、98等是同一关系示意图的标签，不是独立公式。');add(f,'uncertain','',[550,407,873,541],role='fruit_illustration',note='水果图重复文字对象类别，是否提供额外信息不能仅凭存在图片认定。',candidates=['informative_image','other']);add(f,'uncertain','14',role='repeated_subsection_capsule',note='同一固定父模块内部第二部分的居中胶囊，不在整模块最上方；module_badge口径待判。',candidates=['module_badge','text','other']);text(f,'16',role='instruction_ae');add(f,'informative_image','17 18 a0 19',[128,700,609,834],role='brace_diagram_with_blank_answers',internal={'blank_regions':[[271,712,338,741],[430,771,498,800],[540,747,605,774]],'notes':'空框不补数，保留“бірдей”与括号跨行关系。'});add(f,'uncertain','',[611,709,877,823],role='berry_illustration',note='对象图可能仅装饰/重复类别，信息性待人工判定。',candidates=['informative_image','other'])
f=choose(22,8);nums(f);text(f,'22',role='instruction');text(f,'23 24 25 26',role='word_problem');add(f,'informative_image','27 28 29 30',[130,1155,567,1276],role='proportional_segment_diagram',note='分段线长度、括号与8 кг等标签共同表达关系。');add(f,'uncertain','',[574,1150,869,1285],role='berry_and_sugar_illustration',note='图标是否承担示意线图例或仅重复对象，版面证据不足。',candidates=['informative_image','other'])

# PDF109-110: printed reference 5-тапсырмадағы is text, not a module number.
f=choose(29,3);nums(f);badge(f,'2');text(f,'3 4',role='instruction')
for s in ['5 6','7 8','9 10 11 12']:text(f,s,role='word_problem_part',note='正文数量与速度单位不自动当作公式。')
f=choose(29,4);nums(f);badge(f,'22');text(f,'23 24',role='instruction_with_reference',note='5-тапсырмадағы明确指向同页第5模块，不新建模块编号。');formula(f,'25 26',[150,975,425,1020],role='conversion_with_blank_line');formula(f,'27 28',[550,975,800,1020],role='conversion_with_blank_line')
f=choose(29,5);nums(f);badge(f,'29');text(f,'30',role='instruction');text(f,'31 32',role='word_problem_a');text(f,'33 34',role='word_problem_ae')
f=choose(29,6);nums(f);text(f,'2',role='instruction')
for i in range(3,11):formula(f,str(i),role='printed_expression')
f=choose(29,7);nums(f);text(f,'11',role='instruction');text(f,'12 13 14',role='word_problem')
f=choose(29,8);nums(f);badge(f,'15');text(f,'16',role='instruction');text(f,'17 18 19',role='word_problem',note='叙述中的9、35、4、38、63不因是数字就标公式。')
f=choose(29,9);nums(f);badge(f,'20');text(f,'21',role='instruction');text(f,'22 23 24 25 26',role='word_problem')
f=choose(29,10);nums(f);badge(f,'27');text(f,'29 31',role='instruction');cs=[(0,0,1,1,''),(0,1,1,1,'33 36'),(0,2,1,1,'34 37'),(0,3,1,1,'35 38')]
for rr,seqs in [(1,['39','40','41','42']),(2,['43','44','45','46'])]:
 for c,s in enumerate(seqs):cs.append((rr,c,1,1,s))
cells_table(f,[114,1175,766,1312],[114,294,488,594,766],[1175,1237,1273,1312],cs,'原版空白左上表头保留；表头多行及(v)/(t)/(S)保留，不当新公式。右侧角色遮挡边缘处不补字。');add(f,'other','30 32 a4',[748,1080,918,1320],role='decorative_character_and_pedagogical_slogan',problems=['SOURCE_OCCLUSION：角色覆盖表格右上边缘，原图与重叠关系保留。'])

# PDF139 geometric images, not tables or isolated formulas.
f=choose(38,7);nums(f);text(f,'2',role='instruction');text(f,'3 4 5 7 8 9',role='word_problem');add(f,'informative_image','6',[589,312,850,467],role='split_square_diagram',note='分割线、灰色区和4 см括号是图示条件；单个长度标签不另标公式。')
f=choose(38,8);nums(f);badge(f,'11');text(f,'12',role='instruction');text(f,'13 14 15 16 17 18',role='word_problem');add(f,'informative_image','',[550,683,870,881],role='box_and_cubes_diagram',note='空间排列补充题意，不推算遮挡方块或答案。')
f=choose(38,9);nums(f);badge(f,'19');text(f,'20',role='instruction');text(f,'21 22 25 27',role='word_problem');add(f,'informative_image','',[518,1088,671,1240],role='shaded_measurement_grid_not_table',note='阴影格是几何图，不因有行列就当数据表。');add(f,'other','23 24 26',[694,1044,907,1312],role='decorative_character_and_pedagogical_slogan')

# Finalization, overlap ownership and audit. Containers do not mask content coverage.
def flatten(es):
 for e in es:
  yield e
  yield from flatten(e['children'])
def order(es):
 es.sort(key=lambda e:(round(e['bbox'][1]/14),e['bbox'][0]));
 for i,e in enumerate(es,1):
  e['reading_order']=i;order(e['children'])
  if e['is_container']:
   seen=set();rr=[]
   for a in flatten(e['children']):
    for r in a['source_line_ids']:
     key=(r['pdf_page_number'],r['line_id'])
     if key not in seen:rr.append(r);seen.add(key)
   e['source_line_ids']=rr;e['original_ocr']=rawtext(next(f for f in F if f['fragment_id']==e['fragment_id']),rr)
for f in F:
 order(f['elements']);leaf=[e for e in flatten(f['elements']) if not e['is_container']];covered={(r['pdf_page_number'],r['line_id']) for e in leaf for r in e['source_line_ids']};U=getunits(f);expected={(n,i) for n,i in U if n==f['pdf_page_number']};f['uncovered_ocr_lines']=[{'pdf_page_number':n,'line_id':i,'text':U[n,i]['text'],'bbox':U[n,i]['bbox']} for n,i in sorted(expected-covered)];assert not f['uncovered_ocr_lines'],(f['module_number'],f['pdf_page_number'],f['uncovered_ocr_lines'])
 f['module_badge_element_ids']=[e['element_id'] for e in flatten(f['elements']) if e['type']=='module_badge'] or None
 f['module_number_element_ids']=[e['element_id'] for e in flatten(f['elements']) if e['type']=='module_number'] or None
 # Candidate dark-ink coverage, not a semantic completeness claim. Ignore borders/background watermark.
 im=np.array(Image.open(P/AS[f['pdf_page_number']]['path']).convert('L'));b=f['fixed_bbox'];mask=np.zeros(im.shape,dtype=bool)
 for e in leaf:
  a,c,d,g=e['bbox'];mask[max(0,c-3):g+3,max(0,a-3):d+3]=True
 candidate=[];step=24
 for yy in range(b[1]+10,b[3]-10,step):
  for xx in range(b[0]+10,b[2]-10,step):
   x1=min(xx+step,b[2]-10);y1=min(yy+step,b[3]-10);dark=(im[yy:y1,xx:x1]<105)&~mask[yy:y1,xx:x1]
   if int(dark.sum())>=6:candidate.append((xx,yy,x1,y1,int(dark.sum())))
 # Tiles are kept as candidate hints; no automatic reclassification into elements.
 f['uncovered_ink_candidates']=[{'bbox':list(c[:4]),'dark_pixel_count':c[4],'status':'candidate_not_semantic_ground_truth','note':'可能是边框、水印或元素框外图文，人工核对；未据此改变模块。'} for c in candidate]
 for e in flatten(f['elements']):
  if e['problems'] or e['type']=='uncertain':issues.append({'module_id':f['module_id'],'page':f['pdf_page_number'],'element_id':e['element_id'],'type':e['type'],'role':e['role'],'problems':e['problems'],'notes':e['notes']})
# Place visual labels in nearby low-ink regions; this never changes an element bbox.
for n in sorted(AS):
 pix=np.array(Image.open(P/AS[n]['path']).convert('L'));hh,ww=pix.shape;used=[]
 for f in [f for f in F if f['pdf_page_number']==n]:
  for e in flatten(f['elements']):
   a,b,c,d=e['bbox'];w=int(len(e['type'])*7.4+6);h=17
   opts=[(a,b-h-3),(a-w-3,(b+d)/2-h/2),(c+3,(b+d)/2-h/2),(c-w,b-h-3),(a,d+3),(a+3,b+3)]
   choices=[]
   for xx,yy in opts:
    xx=int(max(1,min(ww-w-1,xx)));yy=int(max(1,min(hh-h-1,yy)));box=[xx,yy,xx+w,yy+h];ink=float((pix[yy:yy+h,xx:xx+w]<170).mean());overlap=sum(max(0,min(box[2],u[2])-max(box[0],u[0]))*max(0,min(box[3],u[3])-max(box[1],u[1])) for u in used)/(w*h);choices.append((ink+overlap*10,xx,yy,box))
   _,xx,yy,bb=min(choices);used.append(bb);e['display_label']={'x':xx,'y':yy+13,'note':'显示标签位置，不是元素边界。'}

# Existing lesson-context regions outside fixed modules remain page-level warnings, not new modules.
outside=[];seen=set()
for q in qall:
 for v in q['shared_materials']:
  if v['scope']!='lesson_context' or v['id'] in seen:continue
  seen.add(v['id']);bb=v['bbox_refs'][0];outside.append({'warning_id':v['legacy_id'],'pdf_page_number':bb['pdf_page_number'],'bbox':bb['bbox'],'original_ocr':v['original_text'],'source_line_ids':v['source_line_ids'],'observed_content':'module_note / 原有知识提示，含标题和正文；109页还含原印换算示例','status':'outside_fixed_module_boundaries_not_a_new_module','note':'因保持既有模块边界，未作为内部元素吸收，也没有拆成独立模块。'})
result={'experiment':'模块内部视觉切割Prompt效果试验','generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'input_pilot_commit':'a733d2eccca6111667813730a4cc626e0d143314','source_root_repository_path':'experiments/ai_textbook_pilot','confirmed_pages':sorted(AS),'formal_pages':M['sample_scope']['formal_pages'],'context_only_pages':[30],'module_count':len(qall),'fragment_count':len(F),'coordinate_system':'original PNG pixels [x0,y0,x1,y1]','type_colors':COLORS,'method':'Current Codex directly inspected all 11 original scans and enlarged the three real tables. Explicit visual decisions are recorded in this script; code only assembles evidence and renders. Existing OCR preserved verbatim, no OCR rerun.','prompt_file':'prompt.md','scope_note':'第30页仅既有模块2的跨页片段，不新增模块或正式样本。','reading_order_note':'同层按纵向与近似同行的横向位置排序，独立栏保持整块；不声称由OCR重建了数学运算顺序。','input_sha256':source_hashes,'pages':[{'pdf_page_number':n,'source_image':AS[n]['path'],'original_scan_repository_path':AS[n]['source_image_path'],'source_commit':AS[n]['source_commit'],'source_sha256':AS[n]['sha256'],'width':AS[n]['width'],'height':AS[n]['height'],'scope':'context_only' if n==30 else 'sample'} for n in sorted(AS)],'fragments':F,'outside_module_warnings':outside,'ambiguities':issues,'coverage_warning':'OCR行已关联不代表图片/语义无遗漏；未覆盖暗像素网格仅候选，不把容器矩形、背景或水印当作内容覆盖证明。','no_new_database_or_official_schema':True,'visual_review_adjustments':[{'page':30,'role':'fourth_column_subtraction_example_and_formula','initial_bbox':[371,664,571,809],'final_bbox':[342,664,571,809],'reason':'未覆盖暗像素提示包含原印减号a15；直接放大原图确认后仅扩大内部例式框，原模块bbox与OCR文字不变。'}]}
for name,h in source_hashes.items():assert sha(P/name)==h
assert len(F)==29 and len({f['module_id'] for f in F})==27
for f in F:assert f['fixed_bbox']==next(b['bbox'] for q in qall if q['id']==f['module_id'] for b in q['bbox_refs'] if b['pdf_page_number']==f['pdf_page_number'])
(O/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('RESULT',len(F),'fragments;',len(ALL),'elements;',collections.Counter(e['type'] for e in ALL),'uncovered ink candidates',sum(len(f['uncovered_ink_candidates']) for f in F),flush=True)
# Rendering follows below.
# Standalone original-image viewer; temporary JSON is the sole annotation payload, not an official schema.
def esc(t):return html.escape(str(t),quote=True)
images={str(n):'data:image/png;base64,'+base64.b64encode((P/a['path']).read_bytes()).decode() for n,a in AS.items()}
payload=json.dumps(result,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('&','\\u0026');bank=json.dumps(images,separators=(',',':'))
css='''*{box-sizing:border-box}body{margin:0;background:#edf2f6;color:#193145;font:14px/1.55 system-ui,sans-serif}header{background:#173e58;color:white;padding:18px 26px}h1{margin:0;font-size:25px}header p{margin:6px 0 0}.toolbar{position:sticky;top:0;z-index:20;background:white;border-bottom:1px solid #cbd9e1;padding:10px 18px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}select,button,input{font:inherit}select{padding:6px 8px;max-width:540px;border:1px solid #acbeca;border-radius:5px}button{padding:6px 10px;cursor:pointer;border:1px solid #9fb4c4;background:white;border-radius:5px}.legend{display:flex;gap:9px;flex-wrap:wrap;padding:10px 18px;background:#f8fbfd}.legend label{font-size:12px;white-space:nowrap}.legend i{display:inline-block;width:12px;height:12px;border:2px solid;margin-right:4px;vertical-align:middle}.layout{display:grid;grid-template-columns:minmax(600px,1fr) 450px;align-items:start;gap:16px;margin:16px}.page-card{padding:12px;background:white;border:1px solid #cfdae3;border-radius:8px;overflow:auto}.page-card h2{font-size:16px;margin:0 0 10px}.canvas{max-width:1100px;margin:auto}.canvas svg{display:block;width:100%;height:auto;background:white}.sidebar{position:sticky;top:122px;height:calc(100vh - 140px);overflow:auto;background:white;border:1px solid #cfdae3;border-radius:8px;padding:14px}.status{padding:10px;margin-bottom:10px;background:#e7f1f8;border-radius:6px}.warn{background:#fff4de;border-left:4px solid #ca851b;padding:10px;margin:10px 0}.ok{background:#eaf6ed;padding:8px}.module-item{margin-top:10px;border:1px solid #cfdae3;border-left:4px solid #1e293b;border-radius:5px;padding:8px}.module-item strong{display:block;font-size:14px}.id{font:10px/1.5 monospace;overflow-wrap:anywhere;color:#607a8c}.element-row{display:block;width:100%;text-align:left;margin:4px 0;padding:5px 8px;font-size:12px;border-left-width:4px}.selected-row{background:#fff2cc}.inspector{border-top:2px solid #91acc0;margin-top:14px;padding-top:10px}.inspector h3{font-size:16px;margin:0 0 8px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:13px/1.65 system-ui,sans-serif;margin:6px 0}.meta{font-size:12px;color:#536f82}details{margin-top:8px}summary{cursor:pointer;font-weight:600}.crop-preview svg{max-height:420px;width:100%;border:1px solid #d6dfe5}table{border-collapse:collapse;width:100%;font-size:12px;margin-top:10px}td,th{border:1px solid #acbcc8;padding:5px;vertical-align:middle;white-space:pre-wrap;cursor:pointer}td.blank{background:#f5f8fa}td:hover{background:#fff2cc}.table-wrap{overflow:auto}rect.module-outline{fill:none;stroke:#172b3a;stroke-width:3;stroke-dasharray:12 6;pointer-events:none}.el rect{fill:transparent;stroke-width:2.5;cursor:pointer}.el:hover rect,.el.active rect{fill-opacity:.1;fill:currentColor;stroke-width:5}.el text{paint-order:stroke;stroke:white;stroke-width:4;stroke-linejoin:round;fill:currentColor;font-size:12px;font-weight:650;cursor:pointer}.el.container rect{stroke-dasharray:9 5}.el.uncertain rect{stroke-dasharray:4 3;stroke-width:3}.module-label{font-size:14px;fill:#172b3a;paint-order:stroke;stroke:white;stroke-width:4;font-weight:bold;pointer-events:none}.outside rect{fill:#94a3b8;fill-opacity:.07;stroke:#64748b;stroke-dasharray:7 6;pointer-events:none}.outside text{font-size:12px;fill:#475569;paint-order:stroke;stroke:white;stroke-width:3;pointer-events:none}.coverage rect{fill:#ef4444;fill-opacity:.13;stroke:#ef4444;stroke-dasharray:3 3;pointer-events:none}.cell-highlight{fill:#fbbf24;fill-opacity:.2;stroke:#c2410c;stroke-width:3;pointer-events:none}.minor{font-size:12px;color:#607589}dialog{max-width:900px;max-height:85vh;overflow:auto;border:1px solid #cbd5e1;border-radius:10px;padding:20px}dialog::backdrop{background:#10283899}.amb-item{display:block;width:100%;text-align:left;margin:10px 0;padding:12px;background:#fff7e6}.source-link{margin:8px 0}.notice{padding:10px 18px;background:#fff7e6;border-bottom:1px solid #e6d5b4;font-size:12px}@media(max-width:1050px){.layout{display:block}.sidebar{position:static;height:auto;margin-top:12px}.canvas{min-width:650px}}'''
body='''<header><h1>模块内部视觉切割实验</h1><p>11张原扫描页 · 27个固定父模块 · 29个页片段 · 只切内部元素，不改模块边界</p></header><nav class="toolbar"><label>页码 <select id="page-select"></select></label><button id="prev">上一页</button><button id="next">下一页</button><button id="show-ambiguities">疑点总览</button><label>模块 <select id="module-select"><option value="">本页全部模块</option></select></label><label><input type="checkbox" id="focus">聚焦所选模块</label><label><input type="checkbox" id="labels" checked>元素类型文字</label><label><input type="checkbox" id="coverage" checked>未覆盖/边界外提示</label></nav><div class="legend" id="legend"></div><div class="notice">底图为原始扫描PNG。只处理黑框内；页眉页脚等边界外内容不计内部切割，已知边界外知识框另示警。黑色虚线为原有模块边界；彩框为本次内部元素，虚线彩框是容器/uncertain。example或module_note与内部formula/text重合表示嵌套，不是重复模块。点击框或右侧条目查看原OCR、坐标及表格结构。</div><main class="layout"><section class="page-card"><h2 id="page-title"></h2><div class="canvas" id="canvas"></div></section><aside class="sidebar"><div class="status" id="status"></div><div id="warnings"></div><div id="module-list"></div><section class="inspector" id="inspector"><h3>点击任一元素</h3><p>可以查看未改写的原OCR、识别类型、疑点及内部结构。表格可查看合并单元格；点击单元格高亮其原图位置。</p></section></aside></main><dialog id="ambiguity-dialog"><button id="close-ambiguities">关闭</button><h2>类型待判与边界外提示</h2><div id="ambiguity-content"></div></dialog>'''
js=r'''
const DATA=JSON.parse(document.getElementById('data').textContent),IMAGES=JSON.parse(document.getElementById('images').textContent),NS='http://www.w3.org/2000/svg',PAGE=document.getElementById('page-select'),MOD=document.getElementById('module-select');let selected=null,cell=null;const enabled=new Set(Object.keys(DATA.type_colors));
function h(t){return String(t??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}function flat(es,depth=0){return es.flatMap(e=>[{e,depth},...flat(e.children,depth+1)])}function node(tag,attrs={},text=null){let z=document.createElementNS(NS,tag);for(const [k,v]of Object.entries(attrs))z.setAttribute(k,v);if(text!==null)z.textContent=text;return z}function rect(b){return{x:b[0],y:b[1],width:b[2]-b[0],height:b[3]-b[1]}}function current(){return Number(PAGE.value)}function fragments(){return DATA.fragments.filter(f=>f.pdf_page_number===current()&&(!MOD.value||f.module_id===MOD.value))}function svgImage(vb,n){let z=node('svg',{viewBox:vb.join(' '),xmlns:NS});let p=DATA.pages.find(p=>p.pdf_page_number===n);z.append(node('image',{href:IMAGES[n],x:0,y:0,width:p.width,height:p.height}));return z}
for(const p of DATA.pages){let o=document.createElement('option');o.value=p.pdf_page_number;o.textContent='PDF '+p.pdf_page_number+(p.scope==='context_only'?'（跨页补充）':'');PAGE.append(o)}let seen=new Set;for(const f of DATA.fragments){if(seen.has(f.module_id))continue;seen.add(f.module_id);let o=document.createElement('option');o.value=f.module_id;let pages=DATA.fragments.filter(z=>z.module_id===f.module_id).map(z=>z.pdf_page_number);o.textContent='第'+f.lesson_number+'课 / 模块'+f.module_number+' · PDF '+pages.join('、');MOD.append(o)}
for(const [t,c]of Object.entries(DATA.type_colors)){let l=document.createElement('label');l.innerHTML='<input type="checkbox" checked data-type="'+t+'"><i style="border-color:'+c+'"></i>'+t;l.querySelector('input').onchange=e=>{e.target.checked?enabled.add(t):enabled.delete(t);render()};document.getElementById('legend').append(l)}
function render(){if(!selected)document.getElementById('inspector').innerHTML='<h3>点击任一元素</h3><p>查看本页对应原文、类型、疑点和内部结构。</p>';let n=current(),p=DATA.pages.find(p=>p.pdf_page_number===n),fs=fragments();if(!fs.length&&MOD.value){let f=DATA.fragments.find(f=>f.module_id===MOD.value);PAGE.value=f.pdf_page_number;return render()}let vb=[0,0,p.width,p.height];if(document.getElementById('focus').checked&&MOD.value&&fs.length){let b=fs[0].fixed_bbox;vb=[0,Math.max(0,b[1]-30),p.width,Math.min(p.height,b[3]+20)-Math.max(0,b[1]-30)]}let svg=svgImage(vb,n);document.getElementById('canvas').replaceChildren(svg);document.getElementById('page-title').textContent='PDF '+n+' / 原图 '+p.width+'×'+p.height+(p.scope==='context_only'?' / 仅同模块跨页补充':'');let warn=DATA.outside_module_warnings.filter(w=>w.pdf_page_number===n);let uncovered=fs.reduce((s,f)=>s+f.uncovered_ocr_lines.length,0),ink=fs.reduce((s,f)=>s+f.uncovered_ink_candidates.length,0);document.getElementById('status').innerHTML='<strong>本页 '+fs.length+' 个固定模块片段</strong><br>元素 '+fs.reduce((s,f)=>s+flat(f.elements).length,0)+'；uncertain '+fs.reduce((s,f)=>s+flat(f.elements).filter(z=>z.e.type==='uncertain').length,0)+'<br>未关联OCR行 '+uncovered+'；未覆盖暗像素候选 '+ink+'<p class="minor">OCR覆盖不是图像/语义完整性的证明；空白、边框和水印不应当作有效内容覆盖率。</p>';document.getElementById('warnings').innerHTML=warn.map(w=>'<div class="warn"><strong>原模块边界之外的知识提示</strong><p>'+h(w.note)+'</p><details><summary>原OCR内容</summary><pre>'+h(w.original_ocr)+'</pre></details></div>').join('');
if(document.getElementById('coverage').checked){for(const w of warn){let g=node('g',{class:'outside'});g.append(node('rect',rect(w.bbox)));g.append(node('text',{x:w.bbox[0]+3,y:w.bbox[1]+13},'边界外知识提示（不计新模块）'));svg.append(g)}}let list=document.getElementById('module-list');list.replaceChildren();for(const f of fs){svg.append(node('rect',{...rect(f.fixed_bbox),class:'module-outline'}));svg.append(node('text',{x:f.fixed_bbox[0]+4,y:Math.max(14,f.fixed_bbox[1]-7),class:'module-label'},'M'+f.module_number+' / 课'+f.lesson_number));let block=document.createElement('div');block.className='module-item';block.innerHTML='<strong>第'+h(f.lesson_number)+'课 · 模块'+h(f.module_number)+(f.scope==='context_only'?'（续页）':'')+'</strong><div class="id">'+h(f.module_id)+'</div><div class="minor">模块顶部标签：'+(f.module_badge_element_ids?'见 module_badge 框':'空')+'；原印编号：'+(f.module_number_element_ids?'见 module_number 框':'本续页未印，不补造')+'</div>';for(const {e,depth}of flat(f.elements)){let bt=document.createElement('button');bt.type='button';bt.className='element-row'+(selected===e.element_id?' selected-row':'');bt.style.borderLeftColor=DATA.type_colors[e.type];bt.style.marginLeft=Math.min(36,depth*12)+'px';bt.style.width='calc(100% - '+Math.min(36,depth*12)+'px)';bt.textContent=e.type+' · '+e.role+(e.problems.length?' ⚠':'');bt.onclick=()=>select(e);block.append(bt);if(!enabled.has(e.type))continue;let g=node('g',{class:'el '+(e.is_container?'container ':'')+(e.type==='uncertain'?'uncertain ':'')+(selected===e.element_id?'active':''),'data-element-id':e.element_id,style:'color:'+DATA.type_colors[e.type]});g.append(node('rect',{...rect(e.bbox),stroke:DATA.type_colors[e.type]}));if(document.getElementById('labels').checked){g.append(node('text',{x:e.display_label.x,y:e.display_label.y},e.type))}g.addEventListener('click',ev=>{ev.stopPropagation();select(e)});svg.append(g)}list.append(block);if(document.getElementById('coverage').checked){for(const u of f.uncovered_ocr_lines){let g=node('g',{class:'coverage'});g.append(node('rect',rect(u.bbox)));svg.append(g)}for(const u of f.uncovered_ink_candidates){let g=node('g',{class:'coverage'});g.append(node('rect',rect(u.bbox)));svg.append(g)}}}if(cell&&cell.n===n)svg.append(node('rect',{...rect(cell.b),class:'cell-highlight'}));}
function tableHTML(t,e){let grid=Array.from({length:t.row_count},()=>Array(t.column_count).fill(null)),skip=new Set;for(let i=0;i<t.cells.length;i++){let c=t.cells[i];grid[c.row][c.column]={c,i};for(let r=c.row;r<c.row+c.rowspan;r++)for(let col=c.column;col<c.column+c.colspan;col++)if(r!==c.row||col!==c.column)skip.add(r+':'+col)}let s='<div class="table-wrap"><table data-table-id="'+e.element_id+'">';for(let r=0;r<t.row_count;r++){s+='<tr>';for(let c=0;c<t.column_count;c++){if(skip.has(r+':'+c))continue;let z=grid[r][c];if(!z){s+='<td>未提供结构</td>';continue}s+='<td class="'+(z.c.blank_in_original?'blank':'')+'" data-cell="'+z.i+'" rowspan="'+z.c.rowspan+'" colspan="'+z.c.colspan+'" title="row '+r+' col '+c+' / 点击高亮原图"><pre>'+h(z.c.original_ocr)+'</pre></td>'}s+='</tr>'}return s+'</table></div>'}
function select(e){selected=e.element_id;cell=null;render();let box=document.getElementById('inspector');box.innerHTML='<h3 style="color:'+DATA.type_colors[e.type]+'">'+e.type+'</h3><div class="id">所属模块 '+h(e.module_id)+'</div><p class="meta">PDF '+e.pdf_page_number+' · bbox '+h(JSON.stringify(e.bbox))+' · 同层阅读顺序 '+e.reading_order+'</p><p>'+h(e.notes)+'</p>'+(e.candidate_types.length?'<div class="warn">候选类型：'+h(e.candidate_types.join(' / '))+'</div>':'')+'<h4>对应原OCR（未改写）</h4><pre class="selected-ocr">'+h(e.original_ocr||'无独立OCR文字；图像证据见下方。')+'</pre>'+(e.problems.length?'<div class="warn">'+e.problems.map(h).join('<br>')+'</div>':'')+'<div class="crop-preview" id="crop-preview"></div>'+(e.type==='table'?'<h4>行列/合并单元格（点击单元格高亮）</h4>'+tableHTML(e.internal,e):'')+(e.internal?'<details><summary>内部结构/关联</summary><pre>'+h(JSON.stringify(e.internal,null,2))+'</pre></details>':'')+'<details><summary>原行引用、完整识别记录</summary><pre>'+h(JSON.stringify(e,null,2))+'</pre></details>';let b=e.bbox;document.getElementById('crop-preview').append(svgImage([b[0],b[1],b[2]-b[0],b[3]-b[1]],e.pdf_page_number));box.querySelectorAll('td[data-cell]').forEach(td=>{let c=e.internal.cells[Number(td.dataset.cell)];if(c.layout==='two_row_unknowns_with_brace_and_shared_total'){let get=id=>c.line_boxes.find(z=>z.line_id===id).original_ocr;td.innerHTML='<div style="display:grid;grid-template-columns:1fr 14px 1fr;align-items:center"><pre style="grid-row:1;grid-column:1">'+h(get(c.value_line_ids[0]))+'</pre><pre style="grid-row:2;grid-column:1">'+h(get(c.value_line_ids[1]))+'</pre><span aria-label="原图括号" style="grid-row:1/3;grid-column:2;font-size:40px">}</span><pre style="grid-row:1/3;grid-column:3">'+h(get(c.shared_total_line_id))+'</pre></div>'}});box.querySelectorAll('td[data-cell]').forEach(td=>td.onclick=()=>{let c=e.internal.cells[Number(td.dataset.cell)];cell={n:e.pdf_page_number,b:c.bbox};render();td.style.background='#fff2cc'});let back=document.createElement('button');back.textContent='返回本页元素列表';back.onclick=()=>document.querySelector('.sidebar').scrollTo({top:0,behavior:'smooth'});box.prepend(back);document.querySelector('.sidebar').scrollTo({top:box.offsetTop-8,behavior:'smooth'});}
document.getElementById('show-ambiguities').onclick=()=>{let d=document.getElementById('ambiguity-content');d.innerHTML='<p>这些元素保留uncertain，没有强行归类。原OCR断词、竖式、裁切等其他提示在各元素详情中。</p>';for(const f of DATA.fragments){for(const {e} of flat(f.elements)){if(e.type!=='uncertain')continue;let b=document.createElement('button');b.className='amb-item';b.textContent='PDF '+f.pdf_page_number+' / 模块'+f.module_number+'：'+e.notes+' 候选 '+e.candidate_types.join('/');b.onclick=()=>{document.getElementById('ambiguity-dialog').close();PAGE.value=f.pdf_page_number;MOD.value=f.module_id;select(e)};d.append(b)}}for(const w of DATA.outside_module_warnings){let p=document.createElement('p');p.textContent='PDF '+w.pdf_page_number+'：'+w.note;d.append(p)}document.getElementById('ambiguity-dialog').showModal()};document.getElementById('close-ambiguities').onclick=()=>document.getElementById('ambiguity-dialog').close();
PAGE.onchange=()=>{if(MOD.value&&!DATA.fragments.some(f=>f.module_id===MOD.value&&f.pdf_page_number===current()))MOD.value='';selected=null;cell=null;render()};MOD.onchange=()=>{selected=null;cell=null;render()};document.getElementById('prev').onclick=()=>move(-1);document.getElementById('next').onclick=()=>move(1);function move(d){let i=DATA.pages.findIndex(p=>p.pdf_page_number===current());i=Math.max(0,Math.min(DATA.pages.length-1,i+d));PAGE.value=DATA.pages[i].pdf_page_number;PAGE.onchange()}for(const id of ['focus','labels','coverage'])document.getElementById(id).onchange=()=>render();PAGE.value=DATA.pages[0].pdf_page_number;render();
'''
htmltext='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>模块内部视觉切割实验</title><style>'+css+'</style></head><body>'+body+'<script type="application/json" id="data">'+payload+'</script><script type="application/json" id="images">'+bank+'</script><script>'+js+'</script></body></html>'
(O/'module_internal_review.html').write_text(htmltext)
report=['# 模块内部视觉切割实验：人工复核清单','','范围：原10页+30页跨页补充，共11张扫描页；27个原模块、29个原页片段。未重新OCR、未修改原模块边界或原JSONL。本次JSON只为临时实验输出，没有设计数据库或正式schema。','', '## 类型判断仍有歧义','']
for e in ALL:
 if e['type']=='uncertain':report += [f'- PDF {e["pdf_page_number"]} / `{e["module_id"]}` / `{e["element_id"]}`：{e["notes"]} 候选：'+ '、'.join(e['candidate_types'])+'。']
report += ['', '## 表格复核','','- 第14页：9列、7个逻辑行；第1行三个类标题各跨3列；第2行数位标题保留多行断词；后5行数据空白不填零。共57个物理单元格。','- 第62页：4列、3个逻辑行；数量“бірдей”跨两行，费用区域跨两行并保留两个问号及70 $的括号总价关系。共10个物理单元格，未虚构第5列。','- 第110页：4列、3行，左上表头原版为空，多行标题及(v)/(t)/(S)保持。共12个物理单元格；角色图与右上表格边缘重叠，遮挡内容不补写。','', '## 跨页、知识提示与示例','','- 第29–30页是同一固定模块2。两页内部“记住！”各为module_note，原有算例为其内部example/formula，右侧步骤为教材原印text，不能把1–7步骤号当模块编号。30页没有新编号，不补造。','- 第73–74页是同一父模块2的两个页片段；已给出的乘法/除法竖式及讲解作为example内部formula/text。黄色背景本身不构成module_note判断依据。','- 第109页“5-тапсырмадағы”仍是正文引用，第110页从新模块6开始，未合并两页不同题。','- 第14、74、109页的“记住！”框在所有固定模块边界外，作为页面警示保留原图和旧OCR，未扩大模块，也未另立模块。109页其中含原印换算示例，仍不越界纳入内部结果。','- 第87页第二小题的重复居中胶囊不在合并父模块最上方，保持uncertain，供人工统一module_badge口径。','', '## OCR与边界限制','','- 断词/连字符候选逐元素标出，不把原印换行一概断定为OCR错误，未拼接或润色。','- 竖式、借位标记、长除法、下划线/空框的OCR不是可靠线性公式。保留原文与原图，未生成LaTeX或运算答案。','- 第46页单位а被拆成独立OCR行，沿用原行并关联对应公式；原图里的空框若OCR未检出，不补进文字。','- 第73页2А的原OCR编号框偏窄，本次视觉框覆盖整枚编号文字；原模块边界和OCR字串均不变。','- 已有边界裁到居中胶囊顶部或装饰脚部的几处框按原边界裁切，记录FIXED_BOUNDARY_CLIP，不悄悄扩大模块。','- 第30页第四个竖式初框漏出减号，覆盖像素候选提示后已直接放大确认并调整内部框；过程记在result.json的visual_review_adjustments，原模块不变。','', '## 未覆盖提示与验证的边界','']
report += [f'- 模块内原OCR行未关联：{sum(len(f["uncovered_ocr_lines"]) for f in F)}。',f'- 未覆盖暗像素候选网格：{sum(len(f["uncovered_ink_candidates"]) for f in F)}。','- 原图中的背景、框线和水印作为other背景层保留，但不计为有效内容覆盖。空白也不强行补元素。','- “没有未覆盖候选”不等于视觉语义完全正确，图片信息性、元素类型和表格关系仍需人工验收。','- 本次是Codex按同一Prompt直接查看原图后的视觉判断，不是无人工裁决的批量模型评分；没有另一个Agent结果作标准答案。','', '## 元素数量','']
report += [f'- {t}: {sum(e["type"]==t for e in ALL)}' for t in TYPES]
report += ['', '完整原OCR、坐标、类型候选、表格单元格与每条问题在HTML点击框或右侧条目查看。源扫描页只作底图，未重排、清洗或重编码。','']
(O/'ambiguities.md').write_text('\n'.join(report))
(O/'README.md').write_text('''# 11页模块内部视觉切割实验

打开module_internal_review.html即可离线验收，扫描底图已嵌入。切换页码、模块，勾选“聚焦所选模块”，点击彩框或右侧条目查看原文与识别结果。表格可查看多行/合并单元格，点击单元格高亮原图。不同类型可独立开关。边界外知识框用灰色提示，不是新模块。

result.json仅是临时实验记录；prompt.md保存本次Prompt，ambiguities.md列人工复核事项；build_result.py保存本次显式视觉判读坐标及装配/展示脚本。没有数据库、正式schema、KLP或新答案。

数据来源固定为ai_textbook_pilot已有模块及11张原扫描页。27模块和29个页片段的bbox逐项与原数据相同；原JSONL只读。原OCR行按原样引用，文字修改、错误符号补全均未进行。临时元素ID仅用于此HTML点击定位，不是正式模块ID。

执行：在本仓库运行 python experiments/module_internal_visual_experiment/build_result.py（Python、Pillow、numpy）。它只重新装配本次已经记录的视觉判断，不调用OCR，不自动重新理解扫描页。重新实验Prompt时应另存新结果，不能把脚本固定坐标复放当作新模型效果。
''')
print('HTML ready', (O/'module_internal_review.html').stat().st_size,'bytes; JSON',(O/'result.json').stat().st_size,flush=True)
