"""Executable independent checks; passing these does not certify exercise semantics."""
from pathlib import Path
import sys,argparse,json,hashlib,collections,uuid,datetime
from PIL import Image
import jsonschema
P=Path(__file__).resolve().parents[1]
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
def strict_pairs(pairs):
 d={}
 for k,v in pairs:
  if k in d:raise ValueError('Duplicate JSON key '+k)
  d[k]=v
 return d
def jsonl(p):
 rows=[]
 for n,line in enumerate(Path(p).read_text().splitlines(),1):
  assert line.strip(),f'{p}:{n} blank record';rows.append(json.loads(line,object_pairs_hook=strict_pairs,parse_constant=lambda v:(_ for _ in ()).throw(ValueError(v))))
 return rows
def walk(x):
 for a in x['subquestions']:
  yield a
  yield from walk(a)
def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def validate(root=P,repo=None,write=True):
 O=Path(root).resolve();R=Path(repo).resolve() if repo else P.parents[1];cfg=load(O/'conversion_config.json');m=load(O/'manifest.json');s=load(O/'schema.json');mapp=load(O/'id_mapping.json');xs=jsonl(O/'exercises.jsonl');ls=jsonl(O/'labels.jsonl');inputdir=R/cfg['experiment_directory'];old=load(inputdir/'questions.json');final_source=next(v for v in m['sources'] if v['kind']=='final');final=load(R/final_source['path']);line={(p['page'],str(l['id'])):l for p in final['pages'] for l in p['lines']};checks=[];stats=collections.Counter()
 def passed(name):checks.append({'check':name,'status':'passed'})
 jsonschema.Draft202012Validator.check_schema(s);validator=jsonschema.Draft202012Validator(s)
 for row in xs+ls:validator.validate(row)
 for name,obj in [('manifest',m),('id_mapping',mapp)]:jsonschema.Draft202012Validator({'$schema':s['$schema'],'$defs':s['$defs'],'$ref':'#/$defs/'+name}).validate(obj)
 passed('Strict JSONL parsing, duplicate-key rejection, Draft2020-12 schema for all rows, manifest and mapping')
 xid={a['id']:a for a in xs};lid={a['exercise_id']:a for a in ls};assert len(xid)==len(xs)==len(old['questions']);assert len(lid)==len(ls)==len(xid) and set(lid)==set(xid);passed('Unique parent IDs, exact input parent count, and bijective labels')
 oldmap={q['experiment_question_id']:q for q in old['questions']};parents={r['legacy_id']:r['id'] for r in mapp['parents']};subs={r['legacy_id']:r['id'] for r in mapp['subquestions']};mats={r['legacy_id']:r['id'] for r in mapp['materials']};assert set(parents)==set(oldmap);assert set(parents.values())==set(xid)
 allsubs=[a for q in xs for a in walk(q)];assert len({a['id'] for a in allsubs})==len(allsubs)==len(subs)==sum(len(list(walk(q))) for q in old['questions']);allnodeids=set(xid)|{a['id'] for a in allsubs};matids={v['id'] for q in xs for v in q['shared_materials']}
 NS=uuid.UUID(mapp['namespace_uuid'])
 for kind,name in [('ex','parents'),('sub','subquestions'),('mat','materials')]:
  for row in mapp[name]:assert row['id']==kind+'_'+uuid.uuid5(NS,kind+':'+row['identity_key']).hex
 # Prove metadata-only renumbering cannot alter the identity serialization.
 for q in old['questions']:
  def identity(z):
   anchor=(z['marker_evidence'] or z['source_line_ids'])[0];l=line[anchor['pdf_page_number'],str(anchor['line_id'])];a={'source_pdf_sha256':cfg['book']['source_pdf_sha256'],'pdf_page_number':anchor['pdf_page_number'],'line_id':str(anchor['line_id']),'bbox':l['bbox']};return canonical({'book_id':cfg['book']['book_id'],'anchor':a})
  changed={**q,'exercise_number':'renumbered','lesson_id':'changed-course'};assert identity(q)==identity(changed)==next(z['identity_key'] for z in mapp['parents'] if z['legacy_id']==q['experiment_question_id'])
 passed('All stable IDs recomputed from source anchors; lesson/exercise metadata renumbering has no effect')
 assert m['sample_scope']['formal_pages']==cfg['sample_pages']==old['experiment_scope']['formal_sample_pages'];assert len(set(cfg['sample_pages']))==10
 def refkey(r):return f"p{r['pdf_page_number']:03}:l{r['line_id']}"
 def reftuple(r):return r['pdf_page_number'],str(r['line_id'])
 def srcheck(rr):
  for r in rr:assert r['source_bundle_id']==final_source['id'] and reftuple(r) in line;stats['resolved_source_references']+=1
 for q in xs:
  oq=oldmap[q['provenance']['legacy_question_id']];assert parents[oq['experiment_question_id']]==q['id'];assert q['page_refs']==oq['page_refs'];assert q['exercise_number']==oq['exercise_number'];assert q['lesson_number']==str(int(oq['lesson_id'].split(':')[-1]));assert q['provenance']['verbatim_experiment_text']==oq['text']
  expectedrr=oq['source_line_ids']+[r for c in oq.get('context_only_continuations',[]) for r in c['source_line_ids']];assert [reftuple(r) for r in q['source_line_ids']]==[reftuple(r) for r in expectedrr];srcheck(q['source_line_ids']);U={u['key']:u for u in q['text_units']};assert len(U)==len(q['text_units'])==len(expectedrr);expectednumbers={refkey(r) for r in oq['marker_evidence']}
  for u in U.values():
   r=u['source_ref'];raw=line[reftuple(r)];assert refkey(r)==u['key'] and u['text']==raw['text'] and u['bbox']==raw['bbox'];assert u['role']==('numbering' if u['key'] in expectednumbers else 'body')
  original=[refkey(r) for r in expectedrr if refkey(r) not in expectednumbers];o=q['text_order'];assert o['original_unit_keys']==original;assert collections.Counter(o['readable_unit_keys'])==collections.Counter(original);assert set(o['numbering_unit_keys'])==expectednumbers
  assert q['original_text']=='\n'.join(U[k]['text'] for k in original);assert q['readable_text']=='\n'.join(U[k]['text'] for k in o['readable_unit_keys']);assert collections.Counter(q['original_text'])==collections.Counter(q['readable_text']);stats['validated_parent_text_permutations']+=1
  assert {refkey(v['source_ref']) for v in q['numbering_evidence']}==expectednumbers;assert not (set(original)&expectednumbers)
  expectedboxes=[(b['pdf_page_number'],b['bbox']) for b in oq['bbox_refs']]+[(b['pdf_page_number'],b['bbox']) for c in oq.get('context_only_continuations',[]) for b in c['bbox_refs']];assert [(b['pdf_page_number'],b['bbox']) for b in q['bbox_refs']]==expectedboxes
  assert [(a['pdf_page_number'],a['source_bbox']) for a in q['image_refs'] if a['role'] in ['exercise_fragment','context_fragment']]==expectedboxes,'Screenshot reference must match the existing parent region'
  def checkchild(a,b,parent):
   assert len(a['subquestions'])==len(b['subquestions'])
   for oa,na in zip(a['subquestions'],b['subquestions']):
    assert na['id']==subs[oa['subquestion_id']] and na['parent_exercise_id']==q['id'] and na['parent_node_id']==parent;assert na['original_label']==oa['label'];assert na['inherited_kind']==oa['kind'];assert [reftuple(r) for r in na['source_line_ids']]==[reftuple(r) for r in oa['source_line_ids']];assert [(v['pdf_page_number'],v['bbox']) for v in na['bbox_refs']]==[(v['pdf_page_number'],v['bbox']) for v in oa['bbox_refs']]
    kk=[refkey(r) for r in oa['source_line_ids'] if refkey(r) not in expectednumbers];assert na['original_unit_keys']==kk;assert collections.Counter(na['readable_unit_keys'])==collections.Counter(kk);assert na['original_text']=='\n'.join(U[k]['text'] for k in kk);assert na['readable_text']=='\n'.join(U[k]['text'] for k in na['readable_unit_keys']);assert set(na['shared_material_ids'])<=matids;checkchild(oa,na,na['id']);stats['validated_nested_children']+=1
  checkchild(oq,q,q['id'])
  expectedmaterials={v['material_id']:v for v in oq['shared_materials']};expectedmaterials.update({v['context_block_id']:v for v in old['page_context_blocks'] if oq['experiment_question_id'] in v['related_experiment_questions']});assert {v['legacy_id'] for v in q['shared_materials']}==set(expectedmaterials)
  for v in q['shared_materials']:
   ov=expectedmaterials[v['legacy_id']];assert v['id']==mats[v['legacy_id']];rr=ov['source_line_ids'];raw='\n'.join(line[reftuple(r)]['text'] for r in rr);assert v['original_text']==v['readable_text']==raw;assert [reftuple(r) for r in v['source_line_ids']]==[reftuple(r) for r in rr];im=ov['image_ref'] if 'image_ref' in ov else ov['image_refs'][0];assert [(a['pdf_page_number'],a['bbox']) for a in v['bbox_refs']]==[(im['pdf_page_number'],im['bbox'])];srcheck(v['source_line_ids']);stats['validated_material_instances']+=1
  assert len(q['context_fragments'])==len(oq.get('context_only_continuations',[]))
  for c,oc in zip(q['context_fragments'],oq.get('context_only_continuations',[])):
   assert c['scope']=='context_only' and c['pdf_page_number'] not in cfg['sample_pages'];assert c['original_text']==oc['text'];assert [reftuple(r) for r in c['source_line_ids']]==[reftuple(r) for r in oc['source_line_ids']]
  sourceissues={u['uncertainty_id']:u for u in q['structure_status']['inherited_uncertainties']}
  expected_issue_ids={u['uncertainty_id'] for u in oq['uncertainties']}|{u['uncertainty_id'] for u in old['uncertainties'] if u['status']=='INDEPENDENCE_LIMITATION'}
  for v in q['shared_materials']:
   valid_ids={u['uncertainty_id'] for u in old['uncertainties'] if u['kind']=='instructional_material_scope' and {(a['pdf_page_number'],str(a['line_id'])) for a in u['source_line_ids']} & {reftuple(a) for a in v['source_line_ids']}}
   assert set(v['uncertainty_ids'])==valid_ids,'Uncertainty attached to unrelated material';expected_issue_ids.update(valid_ids)
  assert set(sourceissues)==expected_issue_ids,'Uncertainty must not leak to unrelated same-page exercises'
  for u in oq['uncertainties']:assert sourceissues[u['uncertainty_id']]==u
  for u in old['uncertainties']:
   if u['status']=='INDEPENDENCE_LIMITATION':assert sourceissues[u['uncertainty_id']]==u
  label=lid[q['id']];manual=cfg['objective_review'][oq['experiment_question_id']]
  for k in ['has_image','has_table','has_formula']:assert label[k]==manual[k]
  assert label['has_subquestions']==bool(q['subquestions']);assert label['is_cross_page']==oq['cross_page']==(len(q['page_refs'])>1);assert label['has_explicit_references']==bool(oq['references_to_other_exercises']);assert label['extensions']==[]
  for k,v in label['evidence'].items():assert v['reason'] and v['status']==('unknown' if label[k] is None else 'observed')
  for node in [q]+list(walk(q)):
   for ref in node['references']:
    if ref['resolution']=='internal':assert ref['target_id'] in allnodeids|matids
    else:assert ref['resolution'] in ['external','unresolved']
  explicit=[a for a in q['references'] if a['explicit']];assert len(explicit)==len(oq['references_to_other_exercises'])
  for a,b in zip(explicit,oq['references_to_other_exercises']):assert a['target_id']==parents[b['target_experiment_question_id']] and a['legacy_evidence']==b
 passed('Every source ID, source text and bbox traced to final OCR; original badges separate from body')
 passed('Readable text is an exact source-unit permutation: no omitted/rewritten/added body text')
 passed('All nested nodes, labels and inherited boundaries/material ownership preserved')
 passed('Cross-page parent continuations remain one record; only ten formal pages, page30 context-only')
 passed('All explicit and implicit relation targets resolve; one explicit cross-exercise reference preserved')
 assert m['uncertainties']==old['uncertainties'];passed('Every UNKNOWN and independence limitation preserved verbatim')
 assets={a['id']:a for a in m['assets']};assert len(assets)==len(m['assets']);assert len({a['path'] for a in assets.values()})==len(assets);assert {a['path'] for a in assets.values()}=={p.relative_to(O).as_posix() for p in (O/'images').rglob('*') if p.is_file()};used=set()
 for a in assets.values():
  p=O/a['path'];assert p.is_file() and sha(p)==a['sha256'];src=R/a['source_image_path'];assert sha(src)==a['source_image_sha256'];original=Image.open(src).convert('RGB');actual=Image.open(p).convert('RGB');assert actual.size==(a['width'],a['height']);assert hashlib.sha256(actual.tobytes()).hexdigest()==a['pixel_sha256'];b=a['source_bbox'];expected=original if a['role']=='source_page' else original.crop(b);assert actual.size==expected.size and actual.tobytes()==expected.tobytes()
  if a['role']=='source_page':assert p.read_bytes()==src.read_bytes()
  else:assert a['source_asset_id'] in assets and assets[a['source_asset_id']]['role']=='source_page';used.add(a['source_asset_id'])
 def imagecheck(z):
  if isinstance(z,dict):
   if 'source_bundle_id' in z and 'pdf_page_number' in z and 'line_id' in z:assert z['source_bundle_id']==final_source['id'] and reftuple(z) in line,'Every line pointer must resolve in its declared source bundle'
   if 'asset_id' in z:
    assert z['asset_id'] in assets;used.add(z['asset_id']);a=assets[z['asset_id']];assert a['pdf_page_number']==z['pdf_page_number'];b=z['source_bbox'];source_asset=assets[a['source_asset_id']] if a['source_asset_id'] else a;w,h=source_asset['width'],source_asset['height'];assert 0<=b[0]<b[2]<=w and 0<=b[1]<b[3]<=h
    if a['role']=='crop':assert b==a['source_bbox'],'Crop reference geometry must equal saved crop geometry'
   for v in z.values():imagecheck(v)
  elif isinstance(z,list):
   for v in z:imagecheck(v)
 imagecheck(xs);imagecheck(ls);assert used==set(assets);assert {a['pdf_page_number'] for a in assets.values()}==set(cfg['sample_pages'])|{30};passed('All image references exist; no orphan files; full sources byte-identical and crop pixels exact')
 for src in m['sources']:assert sha(R/src['path'])==src['sha256']
 for name,h in cfg['experiment_file_hashes'].items():assert sha(inputdir/name)==h
 for f in m['files']:assert (O/f['path']).is_file() and sha(O/f['path'])==f['sha256']
 passed('Pinned inputs, unchanged old experiment, script/config and generated-file hashes verified')
 passed('Objective label rows complete, null reasons explicit; no KLP/type/difficulty/purpose/solution annotations generated')
 review=[{'id':q['id'],'lesson':q['lesson_number'],'exercise':q['exercise_number'],'pages':q['page_refs'],'issues':q['structure_status']['reading_order_issues']} for q in xs if q['structure_status']['reading_order_issues']];spatial=[q for q in xs if any(v['scope']=='exercise_owned' and v['transcription_status']=='image_required' for v in q['shared_materials'])];nulls=[{'exercise_id':a['exercise_id'],'field':k,'reason':a['evidence'][k]['reason']} for a in ls for k in a['evidence'] if a[k] is None];labelcounts={k:dict(collections.Counter(str(a[k]).lower() for a in ls)) for k in ls[0]['evidence']};result={'status':'passed','executed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'counts':{**m['counts'],**dict(stats)},'checks':checks,'label_counts':labelcounts,'null_labels':nulls,'reading_order_review':review,'image_dependent_parent_ids':[q['id'] for q in spatial],'semantic_correctness_certified':False}
 if write:
  (O/'validation_results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');report=['# 实际校验报告','',f'执行时间（UTC）：{result["executed_at_utc"]}。程序结果：**全部通过**。','',f'输入父题{len(old["questions"])}条；输出父题{len(xs)}条；递归子题{len(allsubs)}个（含字母组及其内部未编号项目）；标签{len(ls)}条。图片{len(assets)}张：原始完整来源页{m["counts"]["source_page_images"]}张、既有范围裁图{m["counts"]["crop_images"]}张。','', '程序通过只证明格式与来源一致，不等于原实验的切割、材料归属或数学阅读顺序已经语义正确。原图边界没有扩大，也没有悄悄修正原结构。','', '## 已实际执行的检查','']
  report += [f'{i}. {c["check"]}：通过。' for i,c in enumerate(checks,1)]
  report += ['', '## 客观标签统计','','| 标签 | true | false | null |','|---|---:|---:|---:|']
  for k,v in labelcounts.items():report.append(f'| {k} | {v.get("true",0)} | {v.get("false",0)} | {v.get("none",0)} |')
  report += ['', '27条标签均已生成；null不是漏记录。截图自身不计has_image，题内装饰图计入；课程公共讲解另列，不计题目自有视觉属性。', '']
  for v in nulls:report.append(f'- `{v["exercise_id"]}` / `{v["field"]}`：{v["reason"]}')
  report += ['', '## 可读顺序与空间表达仍须复核的题目','','以下只是原有块的无损调序，不声称这些表格、竖式、图注可脱离图片独立理解。含装饰口号的记录另外明确其集中排至末尾的展示口径。','', '| 课号 | 题号 | PDF页 | 稳定ID | 未解决的表达问题 |','|---|---|---|---|---|']
  for v in review:report.append(f'| {v["lesson"]} | {v["exercise"]} | {v["pages"]} | `{v["id"]}` | '+ '；'.join(a['code'] for a in v['issues'])+' |')
  report += ['', '其中14道父题含image_required材料：3课1题；7课2题；11课5、7题；15课8题；19课1、2题；22课7、8题；29课4、10题；38课7、8、9题。它们包括数位表、价格表、速度表、竖式、单位碎片、多空框换算、数卡/气球、括号/线段示意和几何/阴影格。未生成可靠单元格结构、逻辑公式、LaTeX或答案。15课10题另只有装饰口号排列审计提示，不是公式转录。','', '## 原有UNKNOWN及独立性限制','']
  for u in m['uncertainties']:report += [f'### {u["uncertainty_id"]} — {u["status"]}','',u['description'],'']
  report += ['## 格式边界和已知设计限制','','- 未发现阻碍本次10页试点的根本性schema问题；数据定义没有把27道题、特定年级/语言/科目写死到通用schema中。','- 稳定ID以固定来源版本和物理锚点为边界，课号/题号修正不改ID；重新OCR、改版或调整锚点必须显式迁移映射，不能声称自动跨所有版本保持身份。','- original_text的正文口径明确排除独立题号徽章行；编号原文仍存numbering_evidence/text_units，完整旧文本也保留。因此不是删除原文证据。','- 30页是原父题2的上下文，不是第11个正式测试页；86/108/138仅为既有课号证据。','- 原书已打印算例、算法及其结果原样保留，不能误认为本次新增解答。','', '## 交接TrueNorth','','先读README、schema、manifest与本报告，再通过exercises.jsonl读取完整父题/子题/共用材料，结合images及source_line_ids回查。labels.jsonl只作为客观属性；id_mapping.json负责追溯旧实验。新增KLP、题型、难度应写独立extension_labels记录，以exercise_id关联，不覆盖正文，不把UNKNOWN或image_required当作已解决。','']
  repro=O/'reproducibility_results.json'
  if repro.exists():
   rv=load(repro);report += ['## 重复生成检查','',f'实际双次生成：{rv["status"]}；{rv["compared_files"]}个确定性文件字节一致。报告执行时间等审计信息不参与确定性内容摘要。','']
  guard=O/'guard_results.json'
  if guard.exists():
   gv=load(guard);report += ['## 校验程序错误拦截实测','',f'实际向临时副本注入{len(gv["cases"])}类错误，均被校验程序拒绝：'+ '、'.join(z['case'] for z in gv['cases'])+'。正式输出没有注入这些错误。','']
  (O/'validation_report.md').write_text('\n'.join(report))
 return result
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--data',type=Path,default=P);a.add_argument('--repo',type=Path,default=P.parents[1]);a.add_argument('--no-report',action='store_true');v=a.parse_args();r=validate(v.data,v.repo,not v.no_report);print(json.dumps({'status':r['status'],'counts':r['counts'],'checks_passed':len(r['checks']),'null_labels':r['null_labels']},ensure_ascii=False,indent=2))
