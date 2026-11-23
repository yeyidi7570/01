"""Validate existing review views; requires openpyxl and playwright + Chromium."""
from pathlib import Path
import json,hashlib,argparse,shutil,threading,functools
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from openpyxl import load_workbook
from playwright.sync_api import sync_playwright
P=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--views',type=Path,default=P);ap.add_argument('--data',type=Path,default=P.parent/'ai_textbook_pilot');ap.add_argument('--screenshot',type=Path);args=ap.parse_args();O=args.views;D=args.data
rows=[json.loads(l) for l in (D/'exercises.jsonl').read_text().splitlines()];labels=[json.loads(l) for l in (D/'labels.jsonl').read_text().splitlines()];m=json.loads((D/'manifest.json').read_text());saved=json.loads((O/'review_validation.json').read_text());wb=load_workbook(O/'textbook_review.xlsx');ws=wb['父题验收'];assert ws.max_row-1==len(rows) and ws.max_column==21;byid={r['id']:r for r in rows}
for cells in ws.iter_rows(min_row=2):
 q=byid[cells[0].value];assert cells[7].value==q['readable_text'];assert cells[19].value is None and cells[20].value is None
 loc=cells[0].hyperlink.location;assert loc.startswith("'全文阅读'!A");start=int(loc.split('!A')[1])+1;expected=q['readable_text'].split('\n');actual=[wb['全文阅读'].cell(start+i,2).value or '' for i in range(len(expected))];assert actual==expected
assert ws.freeze_panes=='D2';assert any(v.formula1=='"通过,有问题,待确认"' and str(v.sqref)==f'T2:T{len(rows)+1}' for v in ws.data_validations.dataValidation);assert len(wb['全文阅读']['B'])>len(rows)
for p in ['exercises.jsonl','labels.jsonl','manifest.json']:assert hashlib.file_digest((D/p).open('rb'),'sha256').hexdigest()==saved['source_sha256'][p]
for a in m['assets']:assert hashlib.file_digest((O/a['path']).open('rb'),'sha256').hexdigest()==a['sha256']
class QuietHandler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(QuietHandler,directory=str(O)));threading.Thread(target=server.serve_forever,daemon=True).start();url='http://127.0.0.1:'+str(server.server_port)+'/textbook_review.html'
errors=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=shutil.which('chromium'),headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1440,'height':1050});page.on('pageerror',lambda e:errors.append(str(e)));page.goto(url,wait_until='load');assert page.locator('.exercise').count()==len(rows);assert page.locator('[data-sub-id]').count()==saved['subquestion_nodes'];assert page.locator('.exercise:visible').count()==len(rows)
 for q in rows:
  card=page.locator('[id="'+q['id']+'"]');assert card.locator(':scope > pre.stem').text_content()==q['readable_text']
  def check_children(z):
   for a in z['subquestions']:
    assert page.locator('[data-sub-id="'+a['id']+'"]').locator(':scope > pre.subtext').text_content()==a['readable_text'];check_children(a)
  check_children(q)
 tested_page=74 if any(74 in r['page_refs'] for r in rows) else min(p for r in rows for p in r['page_refs']);expected_count=sum(tested_page in r['page_refs'] for r in rows);page.select_option('#page-select',str(tested_page));assert page.locator('.exercise:visible').count()==expected_count;assert page.locator('#visible-count').inner_text()==f'{expected_count} / {len(rows)} 道父题'
 context_pages=m.get('sample_scope',{}).get('context_content_pages',[])
 if context_pages:
  page.select_option('#page-select',str(context_pages[0]));assert page.locator('.exercise:visible').count()==sum(context_pages[0] in r['page_refs'] for r in rows);assert '上下文' in page.locator('#page-select option:checked').inner_text()
 first=rows[0]['id'];page.goto(url+'#'+first,wait_until='load');page.wait_for_timeout(120);assert page.locator('.exercise:visible').count()==len(rows);card=page.locator('[id="'+first+'"]');card.locator('.img-open').first.click();assert page.locator('#image-dialog').is_visible();page.locator('#large-image').wait_for(state='visible');assert page.locator('#large-image').evaluate('(im)=>im.complete && im.naturalWidth>0');page.click('#close-dialog');assert not page.locator('#image-dialog').is_visible()
 if args.screenshot:
  page.goto(url,wait_until='load');page.screenshot(path=str(args.screenshot),full_page=False)
 assert not errors,errors;browser.close()
server.shutdown();server.server_close()
print(json.dumps({'status':'passed','parent_rows':len(rows),'excel_rows_match':True,'subquestion_nodes':saved['subquestion_nodes'],'full_text_exact':True,'tested_page':tested_page,'page_jump_visible_parents':expected_count,'context_jump_checked':bool(context_pages),'offline_images_open':True,'dropdown_and_freeze_verified':True,'input_jsonl_unchanged':True},ensure_ascii=False))
