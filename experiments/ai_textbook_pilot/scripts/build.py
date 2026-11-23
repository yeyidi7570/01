"""Deterministic format conversion only. Never OCR or infer new exercise boundaries."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import argparse,json,hashlib,uuid,shutil,collections,subprocess,importlib.metadata
from PIL import Image
from schema_definition import schema
P=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
def dump(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def load(p):return json.loads(Path(p).read_text())
def keys(rr):return [f"p{r['pdf_page_number']:03}:l{r['line_id']}" for r in rr]
def walk(z):
 for a in z['subquestions']:
  yield a
  yield from walk(a)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,default=P.parents[1]);ap.add_argument('--out',type=Path,default=P);args=ap.parse_args();R=args.repo.resolve();O=args.out.resolve();O.mkdir(parents=True,exist_ok=True);cfg=load(P/'conversion_config.json');D=R/cfg['experiment_directory'];assert O!=D and 'wiki-data' not in O.parts
 for f,h in cfg['experiment_file_hashes'].items():assert sha(D/f)==h,('Changed experiment',f)
 for f in cfg['experiment_file_hashes']:
  actual=subprocess.check_output(['git','hash-object',str(D/f)],cwd=R,text=True).strip();expected=subprocess.check_output(['git','rev-parse',cfg['experiment_commit']+':'+cfg['experiment_directory']+'/'+f],cwd=R,text=True).strip();assert actual==expected
 x=load(D/'questions.json');book=cfg['book']['book_id'];source=x['provenance']['inputs']['final'];assert sha(R/source['path'])==source['sha256'];final=load(R/source['path']);pages={p['page']:p for p in final['pages']};lines={(p['page'],str(l['id'])):l for p in final['pages'] for l in p['lines']};bundle=book+':final';NS=uuid.UUID(cfg['id_namespace_uuid']);sources=[]
 def stable(kind,key):return kind+'_'+uuid.uuid5(NS,kind+':'+key).hex
 def sr(r):return {'source_bundle_id':bundle,'pdf_page_number':r['pdf_page_number'],'line_id':str(r['line_id'])}
 def txt(rr):return '\n'.join(lines[(r['pdf_page_number'],str(r['line_id']))]['text'] for r in rr)
 for name,data in x['provenance']['inputs'].items():
  assert sha(R/data['path'])==data['sha256'];sources.append({'id':bundle if name=='final' else book+':'+name,'kind':name,'path':data['path'],'commit':x['provenance']['commit'],'sha256':data['sha256']})
 for name,h in cfg['experiment_file_hashes'].items():sources.append({'id':'experiment:'+name,'kind':'experiment','path':cfg['experiment_directory']+'/'+name,'commit':cfg['experiment_commit'],'sha256':h})
 def anchor(rr):
  r=rr[0];l=lines[r['pdf_page_number'],str(r['line_id'])];return {'source_pdf_sha256':cfg['book']['source_pdf_sha256'],'pdf_page_number':r['pdf_page_number'],'line_id':str(r['line_id']),'bbox':l['bbox']}
 mapping={'schema_version':cfg['schema_version'],'algorithm':'UUIDv5(namespace, entity kind + book/source-version + physical source anchor). Printed lesson, exercise and child labels are excluded. Preserve this registry for migration across re-OCR/source changes.','namespace_uuid':str(NS),'input_commit':cfg['experiment_commit'],'parents':[],'subquestions':[],'materials':[],'formal_wiki_module_ids_modified':False};idm={};matmap={}
 for q in x['questions']:
  rr=q['marker_evidence'] or q['source_line_ids'];a=anchor(rr);key=canonical({'book_id':book,'anchor':a});i=stable('ex',key);assert i not in idm.values();idm[q['experiment_question_id']]=i;mapping['parents'].append({'legacy_id':q['experiment_question_id'],'id':i,'identity_key':key,'anchor':a})
  def childids(z,parent):
   for a in z['subquestions']:
    an=anchor(a['source_line_ids']);key=canonical({'parent_id':parent,'anchor':an});i=stable('sub',key);assert i not in idm.values();idm[a['subquestion_id']]=i;mapping['subquestions'].append({'legacy_id':a['subquestion_id'],'id':i,'identity_key':key,'anchor':an});childids(a,i)
  childids(q,i)
 def matid(legacy,im):
  a={'source_image_sha256':im['source_image_sha256'],'pdf_page_number':im['pdf_page_number'],'bbox':im['bbox']};key=canonical({'book_id':book,'anchor':a});i=stable('mat',key)
  if legacy not in matmap:mapping['materials'].append({'legacy_id':legacy,'id':i,'identity_key':key,'anchor':a});matmap[legacy]=i
  return i
 for q in x['questions']:
  for v in q['shared_materials']:matid(v['material_id'],v['image_ref'])
 for c in x['page_context_blocks']:
  if c['related_experiment_questions']:matid(c['context_block_id'],c['image_refs'][0])
 assets={};assetkeys={};base=cfg['book']['name']
 def image(n,b=None):
  src=R/x['provenance']['source_images'][str(n)];sourcehash=sha(src);im=Image.open(src).convert('RGB');w,h=im.size
  if b is None:
   k=canonical({'source':sourcehash,'page':n,'role':'full_source'});i=stable('img',k)
   if i not in assets:
    rel='images/source/'+src.name;dest=O/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest);assets[i]={'id':i,'path':rel,'role':'source_page','sha256':sha(dest),'pixel_sha256':hashlib.sha256(im.tobytes()).hexdigest(),'width':w,'height':h,'pdf_page_number':n,'source_image_path':src.relative_to(R).as_posix(),'source_image_sha256':sourcehash,'source_commit':x['provenance']['commit'],'source_bbox':[0,0,w,h],'source_asset_id':None}
   return i
  assert all(isinstance(v,int) for v in b) and 0<=b[0]<b[2]<=w and 0<=b[1]<b[3]<=h
  k=canonical({'source':sourcehash,'page':n,'bbox':b});i=stable('img',k)
  if i not in assets:
   sourceid=image(n);crop=im.crop(b);rel=f'images/crops/{base}_页{n:03}_{i[4:16]}_题图.png';dest=O/rel;dest.parent.mkdir(parents=True,exist_ok=True);crop.save(dest,compress_level=9);assets[i]={'id':i,'path':rel,'role':'crop','sha256':sha(dest),'pixel_sha256':hashlib.sha256(crop.tobytes()).hexdigest(),'width':crop.width,'height':crop.height,'pdf_page_number':n,'source_image_path':src.relative_to(R).as_posix(),'source_image_sha256':sourcehash,'source_commit':x['provenance']['commit'],'source_bbox':list(b),'source_asset_id':sourceid}
  return i
 def ir(n,b,role):return {'asset_id':image(n,b),'role':role,'pdf_page_number':n,'source_bbox':list(b)}
 def br(n,b,ptr,scope=None):return {'pdf_page_number':n,'bbox':list(b),'coordinate_system':'source_png_pixels','scope':scope or ('sample' if n in cfg['sample_pages'] else 'context_only'),'origin_pointer':ptr}
 def refs_new(old,fromid=None):
  out=[]
  for v in old:
   oldtarget=v.get('target_experiment_question_id') or v.get('target_subquestion_id');target=idm.get(oldtarget);scope='internal' if target else ('external' if oldtarget else 'unresolved');out.append({'type':'subquestion' if 'target_subquestion_id' in v else 'exercise','target_id':target,'resolution':scope,'explicit':v.get('reference_type')=='explicit_exercise_reference' or v.get('explicit_number_in_reference') is True,'source_line_ids':[sr(r) for r in v.get('source_line_ids',[])],'legacy_evidence':v})
  return out
 image_required={'place_value_table','price_quantity_cost_table','speed_time_distance_table','four_worked_column_additions','worked_column_multiplication','worked_long_division','division_expression_groups','conversion_equations_and_blank_boxes','speed_conversions_and_blank_answer_lines','balloons_number_cards_and_children','tree_count_brace_diagram','berry_brace_diagram_with_blank_boxes','proportional_bar_diagram','split_square_diagram','box_and_unit_cubes_diagram','shaded_square_grid','fruit_illustrations','berry_illustrations','berry_and_sugar_illustrations'}
 out=[];labels=[]
 for qi,q in enumerate(x['questions']):
  qid=idm[q['experiment_question_id']];allrr=list(q['source_line_ids']);continuations=q.get('context_only_continuations',[])
  for c in continuations:allrr+=c['source_line_ids']
  assert len(keys(allrr))==len(set(keys(allrr)))
  assert txt(q['source_line_ids'])==q['text'];numberkeys=set(keys(q['marker_evidence']));units=[]
  for r,k in zip(allrr,keys(allrr)):
   l=lines[r['pdf_page_number'],str(r['line_id'])];units.append({'key':k,'source_ref':sr(r),'text':l['text'],'bbox':l['bbox'],'scope':'sample' if r['pdf_page_number'] in cfg['sample_pages'] else 'context_only','role':'numbering' if k in numberkeys else 'body'})
  U={u['key']:u for u in units};bodykeys=[u['key'] for u in units if u['role']=='body'];bodyset=set(bodykeys)
  def joint(ks):return '\n'.join(U[k]['text'] for k in ks)
  # Lossless block ordering: use only existing child membership and material line sets.
  def ordered(node,ks):
   ks=[k for k in ks if k in bodyset];pos={k:i for i,k in enumerate(ks)};remaining=set(ks);groups=[]
   for a in node.get('subquestions',[]):
    kk=[k for k in keys(a['source_line_ids']) if k in remaining];remaining.difference_update(kk)
    if kk:groups.append((min(pos[k] for k in kk),ordered(a,kk)))
   own=node.get('subquestion_id');mats=[v for v in q['shared_materials'] if v['owner_subquestion_id']==own]
   for v in mats:
    kk=[k for k in keys(v['source_line_ids']) if k in remaining];remaining.difference_update(kk)
    if kk:groups.append((min(pos[k] for k in kk),kk))
   groups += [(pos[k],[k]) for k in ks if k in remaining];result=[k for _,part in sorted(groups,key=lambda z:z[0]) for k in part];assert collections.Counter(result)==collections.Counter(ks)
   return result
  readable=ordered(q,bodykeys);anc=set(keys(q['ancillary_line_refs']));readable=[k for k in readable if k not in anc]+[k for k in readable if k in anc]
  materials=[]
  def material(v,context=False):
   im=v['image_refs'][0] if context else v['image_ref'];legacy=v['context_block_id'] if context else v['material_id'];rr=v['source_line_ids'];mid=matmap[legacy];ui=[u['uncertainty_id'] for u in x['uncertainties'] if u['kind']=='instructional_material_scope' and {(r['pdf_page_number'],str(r['line_id'])) for r in u['source_line_ids']} & {(r['pdf_page_number'],str(r['line_id'])) for r in rr}];role='decorative' if v['kind']=='ancillary_mascot_prompt' else ('lesson_material' if context else 'material');return {'id':mid,'legacy_id':legacy,'kind':v['kind'],'scope':'lesson_context' if context else 'exercise_owned','owner_subquestion_id':None if context else idm.get(v['owner_subquestion_id']),'original_text':txt(rr),'readable_text':txt(rr),'source_line_ids':[sr(r) for r in rr],'bbox_refs':[br(im['pdf_page_number'],im['bbox'],legacy)],'image_refs':[ir(im['pdf_page_number'],im['bbox'],role)],'transcription_status':'image_required' if v['kind'] in image_required else 'text_with_source_geometry','notes':('课程背景，沿用旧实验关联；不并入父题正文。' if context else v['notes']),'uncertainty_ids':ui}
  for v in q['shared_materials']:materials.append(material(v))
  for c in x['page_context_blocks']:
   if q['experiment_question_id'] in c['related_experiment_questions']:materials.append(material(c,True))
  primary=[];bounds=[]
  for bi,b in enumerate(q['bbox_refs']):
   n=b['pdf_page_number'];primary.append(ir(n,b['bbox'],'exercise_fragment'));bounds.append(br(n,b['bbox'],f'questions[{qi}].bbox_refs[{bi}]'))
  fragments=[]
  for ci,c in enumerate(continuations):
   ims=[];bs=[]
   for bi,b in enumerate(c['bbox_refs']):ims.append(ir(b['pdf_page_number'],b['bbox'],'context_fragment'));bs.append(br(b['pdf_page_number'],b['bbox'],f'questions[{qi}].context_only_continuations[{ci}].bbox_refs[{bi}]','context_only'))
   kk=keys(c['source_line_ids']);fragments.append({'pdf_page_number':c['pdf_page_number'],'scope':'context_only','original_text':joint(kk),'readable_text':joint([k for k in readable if k in set(kk)]),'source_line_ids':[sr(r) for r in c['source_line_ids']],'bbox_refs':bs,'image_refs':ims});primary+=ims;bounds+=bs
  fullimgs=[{'asset_id':image(n),'role':'source_page','pdf_page_number':n,'source_bbox':[0,0,pages[n]['width'],pages[n]['height']]} for n in q['page_refs']]
  def sub(a,parent):
   aid=idm[a['subquestion_id']];rr=a['source_line_ids'];kk=[k for k in keys(rr) if k in bodyset];ro=ordered(a,kk);bb=[br(b['pdf_page_number'],b['bbox'],a['subquestion_id']) for b in a['bbox_refs']];ims=[{'asset_id':image(b['pdf_page_number']),'role':'subquestion_source','pdf_page_number':b['pdf_page_number'],'source_bbox':b['bbox']} for b in a['bbox_refs']];return {'id':aid,'parent_exercise_id':qid,'parent_node_id':parent,'original_label':a['label'],'inherited_kind':a['kind'],'original_text':joint(kk),'readable_text':joint(ro),'source_line_ids':[sr(r) for r in rr],'original_unit_keys':kk,'readable_unit_keys':ro,'bbox_refs':bb,'image_refs':ims,'subquestions':[sub(b,aid) for b in a['subquestions']],'shared_material_ids':[matmap[i] for i in a.get('inherited_material_refs',[]) if i in matmap],'references':refs_new(a['context_dependencies'])}
  subs=[sub(a,qid) for a in q['subquestions']];inherited=list(q['uncertainties']);ui={u['uncertainty_id'] for u in inherited}
  for v in materials:
   for ident in v['uncertainty_ids']:
    if ident not in ui:inherited.append(next(u for u in x['uncertainties'] if u['uncertainty_id']==ident));ui.add(ident)
  for u in x['uncertainties']:
   if u['status']=='INDEPENDENCE_LIMITATION' and u['uncertainty_id'] not in ui:inherited.append(u);ui.add(u['uncertainty_id'])
  orderissues=[];owned_image_mats=[v for v in materials if v['scope']=='exercise_owned' and v['transcription_status']=='image_required']
  if owned_image_mats:orderissues.append({'code':'SPATIAL_MATERIAL_NOT_FULLY_LINEARIZED','description':'表格、图形、标签或竖式仅按既有块分组；行文字不等于可靠单元格、公式或几何转录，必须结合原图。'})
  if anc:orderissues.append({'code':'DECORATIVE_LETTERING_SEPARATE_FROM_PROSE','description':'沿用旧实验附属行标记，可读文本把装饰口号行集中至末尾，不改字或删除。'})
  if q['context_page_refs']:orderissues.append({'code':'CONTEXT_ONLY_CONTINUATION_SCOPE','description':'第30页仅是旧实验父题的上下文续接；其结构归属U01不在本次裁决。'})
  references=refs_new(q['references_to_other_exercises'])
  # Make inherited implicit sibling relation reachable from the complete parent as well.
  for a in walk(q):references+=refs_new(a['context_dependencies'])
  r={'record_type':'exercise','schema_version':cfg['schema_version'],'id':qid,'book_id':book,'lesson_number':q['lesson_id'].split(':')[-1].lstrip('0') or '0','exercise_number':q['exercise_number'],'page_refs':q['page_refs'],'page_scopes':[{'pdf_page_number':n,'scope':'sample' if n in cfg['sample_pages'] else 'context_only'} for n in q['page_refs']],'original_text':joint(bodykeys),'readable_text':joint(readable),'text_units':units,'text_order':{'original_unit_keys':bodykeys,'readable_unit_keys':readable,'numbering_unit_keys':[u['key'] for u in units if u['role']=='numbering'],'method':'Only inherited child/material membership groups unchanged source-line units; standalone badge tokens are kept as metadata; decorative lettering is grouped last. No sentence rewriting, hyphen repair or formula reconstruction.'},'numbering_evidence':[{'source_ref':sr(v),'text':v['text'],'bbox':v['bbox']} for v in q['marker_evidence']],'subquestions':subs,'shared_materials':materials,'image_refs':primary+fullimgs,'source_line_ids':[sr(a) for a in allrr],'bbox_refs':bounds,'references':references,'context_fragments':fragments,'structure_status':{'state':'needs_review' if any(u['status']=='UNKNOWN' for u in inherited) or orderissues else 'preserved_not_semantically_verified','reading_order':'block_grouped_needs_visual_review' if orderissues else 'line_sequence_preserved','reading_order_issues':orderissues,'inherited_uncertainties':inherited},'provenance':{'input_commit':cfg['experiment_commit'],'legacy_question_id':q['experiment_question_id'],'verbatim_experiment_text':q['text'],'legacy_context_dependencies':q['context_dependencies'],'structure_origin':'inherited_experiment_not_resplit'}};out.append(r)
  manual=cfg['objective_review'][q['experiment_question_id']];lv={k:manual[k] for k in ['has_image','has_table','has_formula']};lv.update(has_subquestions=bool(subs),is_cross_page=q['cross_page'],has_explicit_references=bool(q['references_to_other_exercises']));ev={}
  for name,value in lv.items():
   reason=manual.get(name+'_reason',{'has_subquestions':'既有子题数组是否非空，不重新拆分。','is_cross_page':'既有父题page_refs是否跨多个PDF页，包含同题的上下文页。','has_explicit_references':'仅统计原文明确指向其他编号练习的引用；同父题隐式类比不计。'}.get(name,''));ev[name]={'method':'manual_visual_review' if name in manual else 'computed_from_structure','status':'unknown' if value is None else 'observed','reason':reason,'page_refs':q['page_refs'],'source_line_ids':[sr(a) for a in q['source_line_ids']],'material_ids':[v['id'] for v in materials if v['scope']=='exercise_owned'],'asset_ids':[v['asset_id'] for v in primary]}
  labels.append({'record_type':'objective_labels','schema_version':cfg['schema_version'],'exercise_id':qid,**lv,'scope':cfg['label_scope'],'evidence':ev,'extensions':[]})
 assert len(out)==len(x['questions']) and sum(len(list(walk(q))) for q in out)==sum(len(list(walk(q))) for q in x['questions'])
 for name,data in [('exercises.jsonl',out),('labels.jsonl',labels)]:
  with (O/name).open('w') as f:
   for row in data:f.write(json.dumps(row,ensure_ascii=False,separators=(',',':'))+'\n')
 dump(O/'id_mapping.json',mapping);dump(O/'schema.json',schema())
 readme='''# AI 专用教材库：10页保存格式试点

本目录只转换commit `6d67153ea65b105366c0ebf436ff76a3373a0650` 的已有Codex实验；没有重新OCR、切题、改动旧实验或正式Wiki，也没有生成KLP、题型语义、难度、用途、答案或新解法。原书已打印的算例、结果、算法讲解是原文留存，不是本次生成的解答。

## 数据入口

- `exercises.jsonl`：一行一父题；子题递归嵌套。检索 `(book_id,lesson_number,exercise_number)` 可返回一个或多个稳定ID，印刷编号不担任永久身份。
- `labels.jsonl`：每父题一行客观标签，`exercise_id`关联；将来添加KLP/题型/难度应另写`extension_labels`文件，通过相同ID关联，避免修改正文。
- `schema.json`：JSON Schema 2020-12。根规范验证一条exercise/objective_labels/extension_labels；manifest和ID映射分别用`$defs.manifest`与`$defs.id_mapping`验证。支持多教材、未知编号、多页、递归子题、多图、跨题/外部引用及独立扩展标签。
- `manifest.json`：教材、输入commit、实际页范围、所有图片及来源、校验和和检索索引。
- `id_mapping.json`：旧实验父题/子题/材料ID到新ID的映射；不读取或覆盖正式Wiki模块ID。
- `validation_report.md`：实际执行的自动检查、阅读顺序与图片转录限制、所有UNKNOWN。
- `images/source/`：原始完整页PNG，原字节复制；`images/crops/`：直接使用已有bbox裁剪，无新增语义边界。
- `conversion_config.json`及`scripts/`：固定输入/规则和实际生成、校验、检索程序。

## 文字保存口径

`original_text`只由最终校对OCR的原行拼接，包含题内题干、图表标签、原印算法和同题上下文续页；独立题号徽章行移到`numbering_evidence`。没有删除数学运算中的数字或正文引用。完整旧实验文字另存`provenance.verbatim_experiment_text`，用于审核，不能当作经过整理的题干。

`text_units`为逐行不可变文字、原ID和原bbox；`text_order`给出原始及可读的unit-key序列。`readable_text`仅按已有子题/材料关联整块调序，同一父题的body unit恰好出现一次。保留行末连字符、空格和标点，不翻译、不补字、不修正文句。嵌入在同一OCR行内的а)、ә)等原印子题前缀保留，不能为去标签而改写整行。

表格、竖式、括号示意、阴影格等不伪装成可靠线性公式；`transcription_status=image_required`表示仍须看原图。没有生成单元格答案、LaTeX或几何推理。课程共用讲解框保存在`shared_materials(scope=lesson_context)`，不混入父题正文。

所有source_line_ids通过manifest的source_bundle_id指向最终校对JSON；实际身份为bundle+PDF页序+原页内line_id。原文、展示顺序、继承的AI结构和本轮客观观察分字段保存。

## 范围与稳定身份

正式样本固定为PDF页14、29、46、62、73、74、87、109、110、139。30页只完成旧父题2的context_only续接，没有新增正式页/父题；86/108/138页仅保留旧课号证据，不新增课程切分或练习。

UUIDv5 ID取固定命名空间、教材标识/来源PDF哈希、物理锚点（原页序、原行ID、原bbox），不读取课号或题号内容。相同输入重复生成的ID和数据/图片字节一致；修改课号、题号元数据不会改ID。将来重新OCR、换版或改变物理锚点时必须通过现有ID映射显式迁移，不声称跨任意来源版本自动保持身份。

## 客观标签

has_image只统计题目自有片段与同题续页的实际插图/示意/题内装饰，不统计截图自身、纯表格、竖式格纸、答题框；仅继承的课程讲解不计入。has_table为真实数据表格；has_formula为原印运算/等式/换算/竖式，单独数量、单位、变量表头或要求写算式的指令不计。

每个标签有证据、判断口径和unknown理由；null不等于false。第14页第1题装饰图上沿归属未精确标注，has_image保守为null。其余三个结构标签由旧结构直接计算，不生成主观标签。

## 重现与调用

在仓库根目录，使用Python及requirements.txt列出的依赖：

```bash
python experiments/ai_textbook_pilot/scripts/build.py
python experiments/ai_textbook_pilot/scripts/validate.py
python experiments/ai_textbook_pilot/scripts/reproducibility.py
python experiments/ai_textbook_pilot/scripts/query.py --book math-2023-grade4-part1 --lesson 29 --exercise 4 --include-references
```

build也支持`--repo REPOSITORY --out EMPTY_OR_PILOT_DIRECTORY`。脚本先检查固定输入哈希，拒绝被替换的旧实验。生成时间固定在配置中，以免同输入重跑造成数据差异；validation_report是实际校验审计，执行时间可变化，不参与可重现内容摘要。

下一阶段TrueNorth先读本README、schema、manifest、validation_report，再读exercises与labels及所需images；通过id_mapping回溯旧实验。不要以图片存在就判has_image，不要忽略UNKNOWN或image_required，不要在已有text内混写推理标签；生成新题时将本库当参考来源，另存新题及source_exercise_ids，勿覆盖原题。
'''
 (O/'README.md').write_text(readme)
 if O!=P:
  (O/'scripts').mkdir(exist_ok=True)
  for f in (P/'scripts').glob('*.py'):shutil.copy2(f,O/'scripts'/f.name)
  shutil.copy2(P/'conversion_config.json',O/'conversion_config.json')
 (O/'requirements.txt').write_text('Pillow=='+importlib.metadata.version('Pillow')+'\njsonschema=='+importlib.metadata.version('jsonschema')+'\n')
 lookup=collections.defaultdict(list)
 for q in out:lookup[(q['book_id'],q['lesson_number'],q['exercise_number'])].append(q['id'])
 files=[{'path':f.relative_to(O).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)} for f in sorted(O.rglob('*')) if f.is_file() and f.name not in ['manifest.json','validation_report.md','validation_results.json','reproducibility_results.json','guard_results.json'] and '__pycache__' not in f.parts and f.suffix!='.pyc']
 manifest={'schema_version':cfg['schema_version'],'generated_at_utc':cfg['generated_at_utc'],'books':[cfg['book']],'sources':sources,'experiment_input':{'commit':cfg['experiment_commit'],'directory':cfg['experiment_directory'],'previous_version':x['schema_version']},'sample_scope':{'formal_pages':cfg['sample_pages'],'context_content_pages':[30],'lesson_evidence_pages':[86,108,138],'book_id':book},'counts':{'parent_exercises':len(out),'subquestion_nodes':sum(len(list(walk(q))) for q in out),'labels':len(labels),'source_page_images':sum(a['role']=='source_page' for a in assets.values()),'crop_images':sum(a['role']=='crop' for a in assets.values()),'all_images':len(assets),'formal_sample_pages':10},'assets':list(assets.values()),'lookup_index':[{'book_id':k[0],'lesson_number':k[1],'exercise_number':k[2],'exercise_ids':v} for k,v in sorted(lookup.items())],'lessons':x['lessons'],'uncertainties':x['uncertainties'],'input_unchanged':True,'generation':{'script':'scripts/build.py','validation_script':'scripts/validate.py','ordering_policy':'Lossless permutation of immutable final-OCR body units, using inherited grouping only; numbering separately stored; spatial transcription explicitly not verified.','id_policy':mapping['algorithm'],'label_policy':cfg['label_scope'],'printed_examples_policy':'Preserve source-printed examples and algorithms; generate no answers or solutions.'},'files':files};dump(O/'manifest.json',manifest)
 print(json.dumps(manifest['counts'],ensure_ascii=False),flush=True)
if __name__=='__main__':main()
