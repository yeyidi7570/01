"""Mechanical invariants and actual local-browser interactions, not semantic grading."""
from pathlib import Path
import json,hashlib,collections,functools,threading,shutil,base64,datetime
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent;P=R/'experiments/ai_textbook_pilot';x=json.loads((O/'result.json').read_text());qall=[json.loads(l) for l in (P/'exercises.jsonl').read_text().splitlines()];Q={q['id']:q for q in qall}
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def flat(es):
 for e in es:yield e;yield from flat(e['children'])
all_elements=[e for f in x['fragments'] for e in flat(f['elements'])];assert x['confirmed_pages']==[14,29,30,46,62,73,74,87,109,110,139];assert len(Q)==len({f['module_id'] for f in x['fragments']})==27;assert len(x['fragments'])==29;assert len({e['element_id'] for e in all_elements})==len(all_elements)==186
for n,h in x['input_sha256'].items():assert sha(P/n)==h
for p in x['pages']:assert sha(P/p['source_image'])==p['source_sha256'];assert (R/p['original_scan_repository_path']).exists() and sha(R/p['original_scan_repository_path'])==p['source_sha256']
tables=[]
for f in x['fragments']:
 q=Q[f['module_id']];assert f['fixed_bbox']==next(b['bbox'] for b in q['bbox_refs'] if b['pdf_page_number']==f['pdf_page_number']);U={(u['source_ref']['pdf_page_number'],u['source_ref']['line_id']):u for u in q['text_units']};covered=set()
 for e in flat(f['elements']):
  assert e['module_id']==f['module_id'] and e['fragment_id']==f['fragment_id'];a,b,c,d=e['bbox'];aa,bb,cc,dd=f['fixed_bbox'];assert aa<=a<c<=cc and bb<=b<d<=dd;assert e['type'] in x['type_colors'];assert e['original_ocr']=='\n'.join(U[r['pdf_page_number'],r['line_id']]['text'] for r in e['source_line_ids'])
  if not e['is_container']:covered.update((r['pdf_page_number'],r['line_id']) for r in e['source_line_ids'])
  for child in e['children']:
   a,b,c,d=child['bbox'];assert e['bbox'][0]<=a<c<=e['bbox'][2] and e['bbox'][1]<=b<d<=e['bbox'][3]
  if e['type']=='table':
   t=e['internal'];grid=collections.Counter()
   for cell in t['cells']:
    for row in range(cell['row'],cell['row']+cell['rowspan']):
     for col in range(cell['column'],cell['column']+cell['colspan']):grid[row,col]+=1
    assert cell['original_ocr']=='\n'.join(U[r['pdf_page_number'],r['line_id']]['text'] for r in cell['source_line_ids']);assert cell['blank_in_original']==(not cell['source_line_ids'])
    for b in cell['line_boxes']:
     raw=U[f['pdf_page_number'],b['line_id']];assert b['bbox']==raw['bbox'] and b['original_ocr']==raw['text']
   assert set(grid)=={(r,c) for r in range(t['row_count']) for c in range(t['column_count'])} and set(grid.values())=={1};tables.append((f['pdf_page_number'],len(t['cells'])))
 assert covered=={r for r in U if r[0]==f['pdf_page_number']} and not f['uncovered_ocr_lines'];assert not f['uncovered_ink_candidates']
assert tables==[(14,57),(62,10),(110,12)]
ctx=next(f for f in x['fragments'] if f['pdf_page_number']==30);assert ctx['module_number_element_ids'] is None;assert ctx['module_id']==next(f['module_id'] for f in x['fragments'] if f['pdf_page_number']==29 and f['module_number']=='2')
assert {w['pdf_page_number'] for w in x['outside_module_warnings']}=={14,74,109};assert sum(e['type']=='uncertain' for e in all_elements)==5
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(O)));threading.Thread(target=server.serve_forever,daemon=True).start();errors=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=shutil.which('chromium'),headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1700,'height':1100});page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/module_internal_review.html',wait_until='load');assert page.locator('#page-select option').count()==11;assert page.locator('#module-select option').count()==28
 page.select_option('#page-select','14');table=next(e for e in all_elements if e['pdf_page_number']==14 and e['type']=='table');page.locator('g[data-element-id="'+table['element_id']+'"]').dispatch_event('click');assert page.locator('#inspector table td').count()==57;assert page.locator('#inspector table td[colspan="3"]').count()==3;page.locator('#inspector table td[data-cell="0"]').click();assert page.locator('.cell-highlight').count()==1;page.screenshot(path='/workspace/module_visual_table14.png')
 page.select_option('#page-select','62');table=next(e for e in all_elements if e['pdf_page_number']==62 and e['type']=='table');page.locator('g[data-element-id="'+table['element_id']+'"]').dispatch_event('click');assert page.locator('#inspector table td').count()==10;assert page.locator('#inspector table td[rowspan="2"]').count()==2;assert '70 $' in page.locator('#inspector table').inner_text();page.screenshot(path='/workspace/module_visual_table62.png')
 page.select_option('#page-select','29');note=next(e for e in all_elements if e['pdf_page_number']==29 and e['type']=='module_note');page.locator('g[data-element-id="'+note['element_id']+'"]').dispatch_event('click');assert 'ЕСІҢДЕ САҚТА!' in page.locator('.selected-ocr').inner_text();page.select_option('#module-select',note['module_id']);page.check('#focus');page.select_option('#page-select','30');assert page.locator('#module-select').input_value()==note['module_id'];assert page.locator('g.el').count()>0;page.screenshot(path='/workspace/module_visual_note30.png')
 page.click('#show-ambiguities');assert page.locator('#ambiguity-dialog').is_visible() and page.locator('.amb-item').count()==5;page.locator('.amb-item').last.click();assert not page.locator('#ambiguity-dialog').is_visible();assert page.locator('#inspector h3').inner_text()=='uncertain';page.screenshot(path='/workspace/module_visual_uncertain87.png');assert not errors,errors;browser.close()
server.shutdown();server.server_close()
checks={'status':'passed','executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'confirmed_pages':11,'fixed_modules':27,'fixed_fragments':29,'elements':len(all_elements),'types':dict(collections.Counter(e['type'] for e in all_elements)),'table_cell_counts':tables,'uncertain_elements':5,'uncovered_ocr_lines':0,'uncovered_ink_candidate_tiles':0,'original_module_bounds_unchanged':True,'original_ocr_strings_unchanged':True,'source_scan_bytes_verified':True,'table_grid_no_overlap_or_holes':True,'page_module_navigation_and_clicks_tested':True,'table_cell_highlight_tested':True,'nested_note_example_display_tested':True,'uncertainty_dialog_tested':True,'source_jsonl_unchanged':True,'semantic_correctness_not_certified':True};(O/'validation_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n');print(json.dumps(checks,ensure_ascii=False))
