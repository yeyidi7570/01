"""One-time audited configuration; repeat builds use the saved conversion_config.json."""
from pathlib import Path
import datetime,json,hashlib,subprocess
P=Path(__file__).resolve().parents[1];R=P.parents[1];D=R/'experiments/codex/2026-11-20_数学2023_哈语学生_哈语教材（4-1）_АЛМАТЫКІТАП';COMMIT='6d67153ea65b105366c0ebf436ff76a3373a0650'
assert not (P/'conversion_config.json').exists()
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
x=json.loads((D/'questions.json').read_text());cat=json.loads((R/'wiki-data/catalog.json').read_text());book=next(b for b in cat['books'] if b['book_id']==x['experiment_scope']['book_id'])
# Audited observable properties, not exercise-type, KLP, difficulty or solution labels.
# Pairs below: image / table / printed mathematical expression. Screenshot pixels never count as has_image.
rows={
 (3,1):(None,True,False),(7,1):(False,False,False),(7,2):(False,False,True),
 (11,4):(False,False,True),(11,5):(False,False,True),(11,6):(False,False,False),(11,7):(False,False,True),
 (15,7):(False,False,False),(15,8):(False,True,False),(15,9):(False,False,False),(15,10):(True,False,False),
 (19,1):(True,False,False),(19,2):(False,False,True),(19,3):(False,False,True),
 (22,7):(True,False,False),(22,8):(True,False,False),
 (29,3):(False,False,False),(29,4):(False,False,True),(29,5):(False,False,False),(29,6):(False,False,True),
 (29,7):(False,False,False),(29,8):(False,False,False),(29,9):(False,False,False),(29,10):(True,True,False),
 (38,7):(True,False,False),(38,8):(True,False,False),(38,9):(True,False,False)}
manual={}
for q in x['questions']:
 k=(int(q['lesson_id'].split(':')[-1]),int(q['exercise_number']));v=rows[k]
 manual[q['experiment_question_id']]={'has_image':v[0],'has_table':v[1],'has_formula':v[2],
  'has_image_reason':'父题上沿与页首角色图存在少量重叠，装饰图归属未精确标注；主体表格不能单凭截图判为插图。' if v[0] is None else ('原题区域存在插图、几何／线段示意或装饰角色；不把截图自身计作插图。' if v[0] else '原题区域无独立插图或几何示意；纯表格、竖式方格和答题框不按插图统计。'),
  'has_table_reason':'原有真实数据表格。' if v[1] else '未见数据表格；竖式格纸和示意图不按表格统计。',
  'has_formula_reason':'原印算式、等式、换算式或竖式。' if v[2] else '无原印运算式；单独数量、单位、变量表头或“请写算式”的指令不按已印公式统计。'}
c={'schema_version':'ai-textbook/1.0','generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'id_namespace_uuid':'d5eae730-2410-52a7-9760-e27308477ab9','experiment_commit':COMMIT,'experiment_directory':D.relative_to(R).as_posix(),'experiment_file_hashes':{f:sha(D/f) for f in ['questions.json','review.md','uncertainties.md','process.md']},'sample_pages':x['experiment_scope']['formal_sample_pages'],'context_content_pages':[30], 'book':{'book_id':book['book_id'],'name':book['original_basename'],'source_filename':book['source_filename'],'language':'kk-Cyrl','source_pdf_sha256':book['source_pdf_sha256']},'objective_review':manual,'objective_review_method':'人工参考10张原始测试页及既有区域记录，只判可见属性，不新增切割或解答。','label_scope':'题目自有页片段及同题续页；排除仅继承的课程公共讲解。题内装饰图计入has_image。'}
(P/'conversion_config.json').write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n');print('Saved fixed configuration for deterministic repeat builds')
