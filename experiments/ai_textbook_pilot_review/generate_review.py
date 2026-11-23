"""Generate presentation-only review views from existing parent JSONL and labels.
Usage: python generate_review.py --data ../ai_textbook_pilot --out .
No OCR, segmentation, semantic labels or writes to the input directory.
Requires openpyxl. HTML images are embedded for portable offline review.
"""
from pathlib import Path
import argparse,json,hashlib,html,base64,re,math,shutil,collections,datetime
from openpyxl import Workbook,load_workbook
from openpyxl.styles import Font,PatternFill,Alignment,Border,Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule
from openpyxl.comments import Comment
from openpyxl.worksheet.hyperlink import Hyperlink
HEADERS=['模块 ID','PDF 页码','课号','题号','模块类型','模块顶部标签/胶囊','标题','完整题干 readable_text','子题内容','是否有图','是否有信息性图片','是否必须依赖图片','是否有表格','是否跨页','题型','难度','KLP','图片链接','结构状态','人工验收结果','问题备注']
BOOLS={'has_image':'是否有图','has_table':'是否有表格','has_formula':'是否有公式/数学表达式','has_subquestions':'是否有子题','is_cross_page':'是否跨页','has_explicit_references':'是否显式引用其他题目'}
def sha(p):return hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
def readjson(p):return json.loads(Path(p).read_text())
def readlines(p):
 with Path(p).open() as f:return [json.loads(l) for l in f if l.strip()]
def esc(s):return html.escape(str(s),quote=True)
def render_value(v):
 if v is None:return ''
 if isinstance(v,bool):return '是' if v else '否'
 if isinstance(v,(list,dict)):return json.dumps(v,ensure_ascii=False)
 return str(v)
def bool_text(v):return '' if v is None else ('是' if v else '否')
def natural(s):return tuple((0,int(z)) if z.isdigit() else (1,z.casefold()) for z in re.split(r'(\d+)',str(s or '')) if z)
def nodes(z):
 for a in z.get('subquestions',[]):
  yield a
  yield from nodes(a)
def sub_text(z,depth=0):
 parts=[]
 for i,a in enumerate(z.get('subquestions',[]),1):
  tag=a.get('original_label');heading=str(tag) if tag is not None else f'未编号子项 {i}（展示序号）';parts.append('  '*depth+heading+'\n'+a.get('readable_text',''))
  nested=sub_text(a,depth+1)
  if nested:parts.append(nested)
 return '\n\n'.join(parts)
def existing(r,l,names):
 for obj in [r,l]:
  for k in names:
   if k in obj and obj[k] is not None:return obj[k]
 for ext in l.get('extensions',[]):
  if ext.get('name') in names and ext.get('value') is not None:return ext['value']
 return None
def title(r,l):
 pieces=[]
 for names,label in [(['original_title','book_title'],'原书标题'),(['ai_title','generated_title'],'AI生成标题')]:
  v=existing(r,l,names)
  if v is not None:pieces.append('['+label+'] '+render_value(v))
 if not pieces:
  v=existing(r,l,['title'])
  if v is not None:pieces.append('[标题来源未注明] '+render_value(v))
 return '\n'.join(pieces)
def status(r):
 s=r.get('structure_status',{});parts=[s.get('state',''),s.get('reading_order','')]
 parts += [i['code']+'：'+i['description'] for i in s.get('reading_order_issues',[])]
 parts += [u['uncertainty_id']+' / '+u['status']+'：'+u['description'] for u in s.get('inherited_uncertainties',[])]
 return '\n'.join(p for p in parts if p)
def statistics(rows,labels,manifest):
 pages=collections.defaultdict(list);formal=set(manifest.get('sample_scope',{}).get('formal_pages',[]))
 for r in rows:
  for p in r['page_refs']:pages[p].append({'id':r['id'],'lesson':r.get('lesson_number'),'exercise':r.get('exercise_number'),'context_only':p not in formal})
 image=collections.Counter('unknown' if labels[r['id']].get('has_image') is None else ('yes' if labels[r['id']]['has_image'] else 'no') for r in rows)
 structural=[r['id'] for r in rows if r.get('structure_status',{}).get('state')=='needs_review' or r.get('structure_status',{}).get('reading_order_issues') or any(u.get('status')=='UNKNOWN' for u in r.get('structure_status',{}).get('inherited_uncertainties',[]))]
 return {'parent_count':len(rows),'subquestion_node_count':sum(len(list(nodes(r))) for r in rows),'has_image':dict(image),'has_table_count':sum(labels[r['id']].get('has_table') is True for r in rows),'cross_page_count':sum(labels[r['id']].get('is_cross_page') is True for r in rows),'structure_issue_count':len(structural),'structure_issue_ids':structural,'pages':dict(sorted(pages.items())),'formal_pages':sorted(formal),'warning':'仅统计已有记录，不能证明原教材没有漏题；跨页父题在总数中只计一次，页表中可出现在多个页。','structure_issue_definition':'state=needs_review，或有reading_order_issues，或继承UNKNOWN；单独的历史接触限制不另计为题目结构疑点。'}
def textcell(cell,value):
 if isinstance(value,str):
  if len(value.encode('utf-16-le'))//2>32767:raise ValueError('Excel单元格超过32767字符；拒绝截断，需单独设计溢出展示：'+cell.coordinate)
  cell.value=value;cell.data_type='s'
 else:cell.value=value
 cell.alignment=Alignment(vertical='top',wrap_text=True)
def styled_header(ws,names):
 for i,t in enumerate(names,1):
  c=ws.cell(1,i,t);c.font=Font(name='Aptos',size=11,bold=True,color='FFFFFF');c.fill=PatternFill('solid',fgColor='173A55');c.alignment=Alignment(wrap_text=True,vertical='center')
 ws.row_dimensions[1].height=38;ws.sheet_view.showGridLines=False

def generate(data,out):
 data=Path(data).resolve();out=Path(out).resolve();assert out!=data and data not in out.parents and out not in data.parents,'Output must be separate from immutable pilot input';out.mkdir(parents=True,exist_ok=True)
 input_files=[data/n for n in ['exercises.jsonl','labels.jsonl','manifest.json']];before={p.name:sha(p) for p in input_files};rows=readlines(data/'exercises.jsonl');labs=readlines(data/'labels.jsonl');labels={l['exercise_id']:l for l in labs};assert len(labels)==len(labs) and {r['id'] for r in rows}==set(labels);assert len({r['id'] for r in rows})==len(rows)
 rows.sort(key=lambda r:(r.get('book_id',''),min(r['page_refs']),natural(r.get('exercise_number')),natural(r.get('lesson_number')),r['id']));manifest=readjson(data/'manifest.json');assets={a['id']:a for a in manifest['assets']};stats=statistics(rows,labels,manifest)
 for a in assets.values():
  rel=Path(a['path']);assert not rel.is_absolute() and '..' not in rel.parts
  src=data/a['path'];assert src.is_file() and sha(src)==a['sha256'];dest=out/a['path'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
 wb=Workbook();main=wb.active;main.title='父题验收';styled_header(main,HEADERS);main.freeze_panes='D2';main.sheet_properties.pageSetUpPr.fitToPage=True;main.print_options.horizontalCentered=True;main.page_setup.orientation='landscape';main.page_setup.paperSize=main.PAPERSIZE_A3;main.page_setup.fitToWidth=1;main.page_setup.fitToHeight=0;main.print_title_rows='1:1'
 widths=[40,16,9,9,18,24,30,95,90,11,18,18,12,12,18,12,25,30,80,16,42]
 for i,w in enumerate(widths,1):main.column_dimensions[main.cell(1,i).column_letter].width=w
 full=wb.create_sheet('全文阅读');styled_header(full,['模块 ID / 原有字段','逐行完整文字']);full.freeze_panes='B2';full.column_dimensions['A'].width=45;full.column_dimensions['B'].width=150;full.auto_filter.ref='A1:B1';details={};fr=2
 def fullblock(q,kind,content):
  nonlocal fr
  textcell(full.cell(fr,1),q['id']+'\n'+kind);full.cell(fr,1).fill=PatternFill('solid',fgColor='E6EFF7');full.cell(fr,1).font=Font(name='Aptos',bold=True,size=11);full.cell(fr,1).hyperlink=Hyperlink(ref=full.cell(fr,1).coordinate,location="'父题验收'!A"+str(rowindex[q['id']]));full.cell(fr,1).style='Hyperlink';full.row_dimensions[fr].height=32;fr+=1
  # One original text line per sheet row: avoids Excel's 409.5pt single-row limit.
  for line in content.split('\n'):
   textcell(full.cell(fr,2),line);full.cell(fr,2).font=Font(name='Aptos',size=11);full.row_dimensions[fr].height=max(17,math.ceil(max(1,len(line))/135)*16);fr+=1
  fr+=1
 rowindex={q['id']:i+2 for i,q in enumerate(rows)}
 for r in rows:
  details[r['id']]=fr;fullblock(r,'完整题干 readable_text',r['readable_text']);st=sub_text(r)
  if st:fullblock(r,'全部子题（保留已有层级与顺序）',st)
  for v in r.get('shared_materials',[]):fullblock(r,'已有材料 '+v['id']+' / '+v['scope'],v['readable_text'])
  fullblock(r,'结构状态和已有疑点',status(r))
 full.auto_filter.ref=f'A1:B{fr-1}'
 for ri,r in enumerate(rows,2):
  l=labels[r['id']];values=[r['id'],'、'.join(map(str,r['page_refs'])),r.get('lesson_number'),r.get('exercise_number'),render_value(existing(r,l,['module_type'])),render_value(existing(r,l,['top_labels','capsules','module_top_labels'])),title(r,l),r['readable_text'],sub_text(r),bool_text(l.get('has_image')),render_value(existing(r,l,['has_informative_image','has_informational_image'])),render_value(existing(r,l,['requires_image','must_rely_on_image','image_dependency'])),bool_text(l.get('has_table')),bool_text(l.get('is_cross_page')),render_value(existing(r,l,['exercise_type','question_type'])),render_value(existing(r,l,['difficulty'])),render_value(existing(r,l,['klp','KLP'])),f'打开本题全部截图（PDF {"、".join(map(str,r["page_refs"]))}）',status(r),None,None]
  for ci,value in enumerate(values,1):
   c=main.cell(ri,ci);textcell(c,value);c.font=Font(name='Aptos',size=11);c.fill=PatternFill('solid',fgColor='F1F6FA' if ri%2==0 else 'FFFFFF')
  for ci in [1,8,9]:
   if main.cell(ri,ci).value:main.cell(ri,ci).hyperlink=Hyperlink(ref=main.cell(ri,ci).coordinate,location=f"'全文阅读'!A{details[r['id']]}");main.cell(ri,ci).font=Font(name='Aptos',size=11,color='12629B',underline='single')
  main.cell(ri,18).hyperlink='textbook_review.html#'+r['id'];main.cell(ri,18).font=Font(name='Aptos',size=11,color='12629B',underline='single');main.cell(ri,18).comment=Comment('打开HTML内本题预览；所有题图、跨页截图、材料图和原图可查看。“图片索引”工作表另有每张PNG直接链接。','展示脚本')
  for ci in [8,9]:main.cell(ri,ci).comment=Comment('此单元格完整保存原文，未截断。Excel单行高度最多409.5磅；如未显示全部，点击本单元格或模块ID进入“全文阅读”表逐行查看。','展示脚本')
  maxlines=max(sum(max(1,math.ceil(len(t)/85)) for t in str(v or '').split('\n')) for v in [values[7],values[8],values[18]]);main.row_dimensions[ri].height=min(409.5,max(72,maxlines*14.5+12))
  for ci in [20,21]:main.cell(ri,ci).fill=PatternFill('solid',fgColor='FFF2CC')
 main.auto_filter.ref=f'A1:U{len(rows)+1}';validation=DataValidation(type='list',formula1='"通过,有问题,待确认"',allow_blank=True);validation.errorTitle='请选择验收结果';validation.error='允许值：通过、有问题、待确认。';validation.showErrorMessage=True;validation.showDropDown=False;main.add_data_validation(validation);validation.add(f'T2:T{len(rows)+1}')
 for value,color in [('通过','E2F0D9'),('有问题','FCE4D6'),('待确认','FFF2CC')]:main.conditional_formatting.add(f'T2:T{len(rows)+1}',CellIsRule(operator='equal',formula=['"'+value+'"'],fill=PatternFill('solid',fgColor=color)))
 summary=wb.create_sheet('验收统计');styled_header(summary,['统计项目 / PDF页码','数量 / 课号与题号','口径说明']);summary.freeze_panes='A2';summary.column_dimensions['A'].width=32;summary.column_dimensions['B'].width=105;summary.column_dimensions['C'].width=90
 metrics=[('总父题数',stats['parent_count'],'跨页父题只计一条'),('总子题节点数',stats['subquestion_node_count'],'含字母组及其内部未编号子项；不是新增父题数'),('有图',stats['has_image'].get('yes',0),'沿用has_image=true，不把截图本身当插图'),('无图',stats['has_image'].get('no',0),'沿用has_image=false'),('图片属性未知',stats['has_image'].get('unknown',0),'源标签null，主表留空'),('有表格',stats['has_table_count'],'沿用has_table=true'),('跨页父题',stats['cross_page_count'],'含第30页context_only续接'),('存在结构疑点',stats['structure_issue_count'],stats['structure_issue_definition'])]
 sr=2
 for a,b,c in metrics:
  for i,v in enumerate([a,b,c],1):textcell(summary.cell(sr,i),v)
  summary.row_dimensions[sr].height=35;sr+=1
 for p,items in stats['pages'].items():
  textcell(summary.cell(sr,1),f'PDF {p}'+('（正式样本）' if p in stats['formal_pages'] else '（仅上下文）'));textcell(summary.cell(sr,2),'；'.join(f'第{v["lesson"]}课 · 第{v["exercise"]}题' for v in items));textcell(summary.cell(sr,3),'跨页父题可在多个页出现，但总父题数不重复计数。');summary.row_dimensions[sr].height=35;sr+=1
 for line in [stats['warning'],'未标注的模块类型、胶囊、标题、信息性图片、图片依赖、题型、难度、KLP均留空，不由已有文字或图片推断补全。','本表是数据展示视图，不是权威数据源。最后两列仅供人工填写，不回写JSONL。','主表每父题一行且单元格完整存储。Excel行高有上限；点击模块ID、题干或子题进入“全文阅读”工作表，避免显示被行高收起。']:
  textcell(summary.cell(sr,1),'说明');textcell(summary.cell(sr,2),line);summary.row_dimensions[sr].height=45;sr+=1
 summary.auto_filter.ref=f'A1:C{sr-1}'
 index=wb.create_sheet('图片索引');styled_header(index,['模块 ID','PDF页码','图片角色','截图/材料文件（点击打开）','来源页文件（点击打开）','原始页bbox']);index.freeze_panes='C2'
 for col,width in zip('ABCDEF',[40,12,25,80,80,36]):index.column_dimensions[col].width=width
 ir=2
 for r in rows:
  refs=list(r['image_refs'])+[im for m in r['shared_materials'] for im in m['image_refs']];seen=set()
  for ref in refs:
   key=(ref['asset_id'],ref['role'])
   if key in seen:continue
   seen.add(key);a=assets[ref['asset_id']];src=assets[a['source_asset_id']] if a['source_asset_id'] else a
   for i,v in enumerate([r['id'],ref['pdf_page_number'],ref['role'],a['path'],src['path'],str(ref['source_bbox'])],1):textcell(index.cell(ir,i),v)
   for ci in [4,5]:index.cell(ir,ci).hyperlink=index.cell(ir,ci).value;index.cell(ir,ci).font=Font(color='12629B',underline='single')
   index.row_dimensions[ir].height=32;ir+=1
 index.auto_filter.ref=f'A1:F{ir-1}';wb.active=0;wb.save(out/'textbook_review.xlsx')
 # HTML: all original data text is escaped; all screenshots are embedded once, no network needed.
 def image_element(ref,caption):return f'<figure><button class="img-open" data-image="{esc(ref["asset_id"])}" type="button"><img loading="lazy" data-asset="{esc(ref["asset_id"])}" alt="{esc(caption)}"></button><figcaption>{esc(caption)} · bbox {esc(ref["source_bbox"])}</figcaption></figure>'
 def childhtml(z):
  items=[]
  for i,a in enumerate(z.get('subquestions',[]),1):
   label=a.get('original_label') or f'未编号子项 {i}（展示序号）';items.append(f'<section class="subquestion" data-sub-id="{esc(a["id"])}"><h4>{esc(label)}</h4><pre class="subtext">{esc(a.get("readable_text",""))}</pre>{childhtml(a)}</section>')
  return ''.join(items)
 cards=[]
 for r in rows:
  l=labels[r['id']];badges=''.join(f'<span class="badge">{esc(label)}：{esc("未标注" if l.get(k) is None else bool_text(l[k]))}</span>' for k,label in BOOLS.items());ims=''.join(image_element(v,f'PDF {v["pdf_page_number"]} · '+('同题上下文' if v['role']=='context_fragment' else '父题截图')) for v in r['image_refs'] if v['role'] in ['exercise_fragment','context_fragment']);fullims=''.join(image_element(v,f'PDF {v["pdf_page_number"]} · 完整来源页') for v in r['image_refs'] if v['role']=='source_page');materials=''
  for v in r['shared_materials']:
   materials+=f'<section class="material"><h4>{esc(v["kind"])} <small>{esc(v["scope"])} / {esc(v["transcription_status"])}</small></h4><pre>{esc(v["readable_text"])}</pre>'+''.join(image_element(im,f'PDF {im["pdf_page_number"]} · 已有材料') for im in v['image_refs'])+'</section>'
  titles=title(r,l);cards.append(f'<article class="exercise" id="{esc(r["id"])}" data-pages="{esc(json.dumps(r["page_refs"]))}"><div class="card-head"><h2>第{esc(r.get("lesson_number") or "")}课 · 第{esc(r.get("exercise_number") or "")}题</h2><span>PDF {esc("、".join(map(str,r["page_refs"])))}</span></div><p class="module-id">{esc(r["id"])}</p>'+ (f'<pre>{esc(titles)}</pre>' if titles else '')+f'<div class="badges">{badges}</div><h3>完整题干 readable_text</h3><pre class="stem">{esc(r["readable_text"])}</pre><div class="shots">{ims}</div><h3>全部子题（已有层级）</h3>'+ (childhtml(r) or '<p class="muted">源记录没有子题数组内容。</p>')+f'<details class="materials"><summary>查看共用/附属材料（{len(r["shared_materials"])}项，未重新归类）</summary>{materials}</details><details><summary>查看完整来源页</summary><div class="shots">{fullims}</div></details><details open class="issues"><summary>结构状态及已有待确认事项</summary><pre>{esc(status(r))}</pre></details></article>')
 pageoptions=''.join(f'<option value="{p}">PDF {p}'+('（上下文）' if p not in stats['formal_pages'] else '')+'</option>' for p in stats['pages']);pagerows=''.join('<tr><td>'+str(p)+('（上下文）' if p not in stats['formal_pages'] else '')+'</td><td>'+esc('；'.join(f'第{v["lesson"]}课·第{v["exercise"]}题' for v in items))+'</td></tr>' for p,items in stats['pages'].items());metricshtml=''.join(f'<div class="metric"><strong>{esc(v)}</strong><span>{esc(k)}</span></div>' for k,v,_ in metrics)
 bank={a['id']:'data:image/png;base64,'+base64.b64encode((data/a['path']).read_bytes()).decode() for a in assets.values()}
 css='''*{box-sizing:border-box}body{margin:0;background:#f2f5f8;color:#172b3a;font:16px/1.6 system-ui,sans-serif}header{background:#153b55;color:white;padding:26px max(24px,calc((100vw - 1200px)/2))}h1{margin:0;font-size:27px}header p{margin:6px 0 0}.toolbar{position:sticky;top:0;z-index:3;background:white;border-bottom:1px solid #cbd6de;padding:12px 24px;display:flex;align-items:center;gap:12px;flex-wrap:wrap}select,input,button{font:inherit}select,input{padding:6px 10px;border:1px solid #a5b7c5;border-radius:6px}main{max-width:1240px;margin:auto;padding:24px}.exercise,.stats{background:white;border:1px solid #dce4e9;border-radius:12px;padding:26px;margin-bottom:24px;box-shadow:0 2px 5px #1232}.card-head{display:flex;justify-content:space-between;gap:16px;align-items:center}.card-head h2{margin:0}.module-id{font:13px/1.5 monospace;overflow-wrap:anywhere;color:#516777}.badge{display:inline-block;padding:3px 9px;margin:3px;border-radius:12px;background:#e8f1f7;font-size:13px}pre{font:15px/1.7 system-ui,sans-serif;white-space:pre-wrap;overflow-wrap:anywhere;margin:10px 0}.stem{padding:16px;background:#f7fafc;border-left:4px solid #367daf}.subquestion{margin:12px 0 12px 14px;padding:10px 18px;border-left:3px solid #8dafc6;background:#fafcfd}.subquestion h4{margin:0}.shots{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px}figure{margin:12px 0}img{display:block;max-width:100%;height:auto}figcaption{font-size:12px;color:#536a79;overflow-wrap:anywhere}.img-open{display:block;padding:0;border:1px solid #dce4e9;background:white;cursor:zoom-in}.issues{background:#fff8e8;padding:12px;border-radius:8px}details{margin-top:16px}summary{cursor:pointer;font-weight:600}.material{border:1px solid #d8e3ea;padding:16px;margin-top:12px}small,.muted{color:#657a89}.metrics{display:flex;flex-wrap:wrap;gap:12px}.metric{padding:10px 16px;background:#edf4f8;border-radius:8px}.metric strong{display:block;font-size:26px}.metric span{font-size:13px}table{border-collapse:collapse;width:100%;margin-top:14px}td,th{text-align:left;padding:7px 12px;border-bottom:1px solid #d9e1e7}.warning{padding:12px;border-left:4px solid #bd8121;background:#fff6e2}dialog{border:0;padding:18px;max-width:96vw;max-height:94vh;overflow:auto;border-radius:8px}dialog::backdrop{background:#0009}dialog img{max-height:none;max-width:none;width:auto}dialog button{position:sticky;top:0;background:#fff;padding:8px 16px;cursor:pointer}@media(max-width:700px){main{padding:12px}.exercise,.stats{padding:16px}.shots{display:block}.card-head{display:block}}@media print{.toolbar{position:static}.exercise{break-inside:avoid}details>*{display:block}body{background:white}}'''
 js='''const bank=JSON.parse(document.getElementById('asset-bank').textContent);document.querySelectorAll('img[data-asset]').forEach(i=>i.src=bank[i.dataset.asset]);const cards=[...document.querySelectorAll('.exercise')],sel=document.getElementById('page-select'),search=document.getElementById('search');function filter(){let p=sel.value,q=search.value.trim().toLowerCase(),n=0;cards.forEach(c=>{let ok=(!p||JSON.parse(c.dataset.pages).includes(Number(p)))&&(!q||c.textContent.toLowerCase().includes(q));c.hidden=!ok;if(ok)n++});document.getElementById('visible-count').textContent=n+' / '+cards.length+' 道父题'}sel.addEventListener('change',()=>{filter();history.replaceState(null,'',sel.value?'#page-'+sel.value:location.pathname);document.getElementById('records').scrollIntoView({block:'start'})});search.addEventListener('input',filter);function followHash(){let h=decodeURIComponent(location.hash.slice(1));if(h.startsWith('page-')){sel.value=h.slice(5);filter()}else if(h){sel.value='';search.value='';filter();let target=document.getElementById(h);if(target){target.style.outline='3px solid #639bbd';setTimeout(()=>target.scrollIntoView(),50)}}}window.addEventListener('hashchange',followHash);document.querySelectorAll('.img-open').forEach(b=>b.addEventListener('click',()=>{document.getElementById('large-image').src=bank[b.dataset.image];document.getElementById('image-dialog').showModal()}));document.getElementById('close-dialog').addEventListener('click',()=>document.getElementById('image-dialog').close());filter();followHash();'''
 document='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>教材人工验收预览</title><style>'+css+'</style></head><body><header><h1>教材人工验收预览</h1><p>已有数据展示视图 · 不重新切题，不新增标签，不作为权威数据源</p></header><nav class="toolbar"><label>PDF页码 <select id="page-select"><option value="">全部父题</option>'+pageoptions+'</select></label><label>查找 <input id="search" type="search" placeholder="模块 ID / 原文"></label><strong id="visible-count"></strong></nav><main><section class="stats"><h2>验收统计</h2><p class="warning">'+esc(stats['warning'])+'</p><div class="metrics">'+metricshtml+'</div><details><summary>每页已有题号与统计口径</summary><table><thead><tr><th>PDF页码</th><th>已有课号与题号</th></tr></thead><tbody>'+pagerows+'</tbody></table><p>'+esc(stats['structure_issue_definition'])+'</p></details></section><div id="records">'+''.join(cards)+'</div></main><dialog id="image-dialog"><button id="close-dialog" type="button">关闭原尺寸图片</button><img id="large-image" alt="所选原教材截图"></dialog><script type="application/json" id="asset-bank">'+json.dumps(bank,separators=(',',':'))+'</script><script>'+js+'</script></body></html>'
 (out/'textbook_review.html').write_text(document)
 # Verify exact text in saved Excel and HTML source; no summary or silent truncation.
 saved=load_workbook(out/'textbook_review.xlsx');sh=saved['父题验收'];assert sh.max_row-1==len(rows);assert sh.freeze_panes=='D2' and sh.auto_filter.ref==f'A1:U{len(rows)+1}'
 for i,r in enumerate(rows,2):
  assert sh.cell(i,1).value==r['id'] and sh.cell(i,8).value==r['readable_text'];assert (sh.cell(i,9).value or '')==sub_text(r);assert sh.cell(i,20).value is None and sh.cell(i,21).value is None
  for col,names in [(5,['module_type']),(6,['top_labels','capsules','module_top_labels']),(11,['has_informative_image','has_informational_image']),(12,['requires_image','must_rely_on_image','image_dependency']),(15,['exercise_type','question_type']),(16,['difficulty']),(17,['klp','KLP'])]:
   if existing(r,labels[r['id']],names) is None:assert sh.cell(i,col).value is None
  assert esc(r['readable_text']) in document
  for a in nodes(r):assert esc(a.get('readable_text','')) in document
 for p in input_files:assert sha(p)==before[p.name]
 report={'generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'input_paths':[str(p) for p in input_files],'source_sha256':before,'input_unchanged':True,'parent_rows':len(rows),'excel_data_rows':sh.max_row-1,'subquestion_nodes':stats['subquestion_node_count'],'html_parent_cards':len(rows),'all_text_saved_verbatim':True,'manual_columns_initially_blank':True,'dropdown_values':['通过','有问题','待确认'],'source_images_copied':len(assets),'statistics':stats,'excel_display_limit':'Excel行高上限409.5磅，主表单元格保留全文并链接到逐行全文阅读表，HTML完整展开。'}
 (out/'review_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 (out/'README.md').write_text('''# 教材人工验收展示视图

本目录只展示指定数据目录的已有记录，不修改JSONL、不改变ID、不生成推断标签。

- textbook_review.xlsx：父题验收表（每父题一行）、验收统计、全文阅读和图片索引四张表。前3列与表头冻结，开启筛选；最后两列留空供人工填写，结果列带“通过/有问题/待确认”下拉。
- textbook_review.html：离线自包含预览，截图已嵌入，不依赖网络。按PDF页过滤；跨页父题只保留一张卡片。正式页和上下文页沿用源manifest，不新增测试页。
- images/：复制已有资产，供Excel图片索引直接打开；HTML自身已嵌图。
- review_validation.json：行数、来源哈希、完整文本校验和统计。统计不证明原教材无漏题。

Excel单行高度最多409.5磅。主表保留完整readable_text及子题，不做摘要、不截断；如屏幕未显示全部，点击模块ID/题干/子题跳到“全文阅读”表，其中文字逐行完整展示。点击主表“图片链接”打开HTML本题截图；“图片索引”另有PNG直接链接。下载Excel单文件仍能查看全部文字；若要使用本地图片链接，请一起保留HTML与images目录或下载整个目录包。

空白值代表源数据未标注；不把record_type推成模块类型，不把材料kind推成题型，不把image_required推成“是否必须依赖图片”。标题只有明确的原书/AI字段才区分显示，未标注则空白。现有胶囊、题型、难度、KLP等不存在时不从正文推断。已有父题全文可能本就包含子题，子题列仍按原有树再显示，重复来自源结构而非新增题目。

结构疑点统计口径见统计表；仅历史接触限制不单独算语义结构疑点。所有已有疑点说明均照录于HTML与Excel结构状态列。人工填写不会回写数据；这些展示文件不是新的权威来源。

重跑（Python + openpyxl）：

```bash
python generate_review.py --data ../ai_textbook_pilot --out .
```

脚本适用于同格式其他教材：每父题一行，按最早PDF页和原题号自然排序，使用exercise_id合并客观标签；支持递归子题、多页和多图。若单元格超过Excel32767字符上限，程序会明确报错，绝不静默截断。重新生成会覆盖展示文件，请先另存已填写的验收Excel。
''')
 print(json.dumps({'parent_rows':len(rows),'subquestion_nodes':stats['subquestion_node_count'],'images':len(assets),'statistics':{k:v for k,v in stats.items() if k not in ['pages','structure_issue_ids']},'output':str(out)},ensure_ascii=False))
 return report
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--data',type=Path,default=Path(__file__).resolve().parent.parent/'ai_textbook_pilot');parser.add_argument('--out',type=Path,default=Path(__file__).resolve().parent);args=parser.parse_args();generate(args.data,args.out)
