"""Run the lesson and comparison pages in Chromium without network access."""
import json
from pathlib import Path
from playwright.sync_api import expect, sync_playwright

BASE = 'http://localhost:47889'
ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT/'content.json').read_bytes())
LESSON = DATA['lesson']['id']
external = []

def respond(route):
    url = route.request.url
    relative = url.removeprefix(BASE + '/')
    path = (ROOT/relative).resolve()
    permitted = relative == 'comparison.html' or relative.startswith(('validation/','review/review_'))
    if url.startswith(BASE + '/') and path.is_relative_to(ROOT) and permitted and path.is_file():
        route.fulfill(path=path)
    else:
        external.append(url)
        route.abort()

def export(page):
    with page.expect_download() as capture:
        page.locator('#export').click()
    return json.loads(Path(capture.value.path()).read_bytes())

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    result = None
    for lang in ('zh','kk'):
        ctx = browser.new_context(offline=True,accept_downloads=True,viewport={'width':1360,'height':920})
        ctx.route('**/*',respond)
        page = ctx.new_page()
        errors = []
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto(f'{BASE}/review/review_{lang}.html')
        assert page.locator('html').get_attribute('lang') == lang
        expect(page.locator('article[data-type=module]')).to_have_count(9)
        expect(page.locator('article[data-type=informative_image]')).to_have_count(6)
        expect(page.locator('article[data-type=table]')).to_have_count(1)
        expect(page.locator('article[data-type=formula]')).to_have_count(9)
        table=page.locator('article[data-type=table] table')
        expect(table.locator('tr')).to_have_count(2)
        expect(table.locator('tr').nth(1).locator('td')).to_have_count(6)
        assert all(not value.strip() for value in table.locator('tr').nth(1).locator('td').all_text_contents())
        select=page.locator('#page')
        assert [opt.get_attribute('value') for opt in select.locator('option').all()]==['29','30','31']
        graph=page.locator(f'[data-object-id="{LESSON}:m05:distance-time"]')
        expect(graph).to_contain_text('每小格 100 米' if lang=='zh' else 'әр торкөз 100 м')
        graph.locator('img.crop').scroll_into_view_if_needed()
        expect(graph.locator('img.crop')).to_have_js_property('complete',True)
        assert graph.locator('img.crop').evaluate('img => img.naturalWidth')>0
        if result is None:
            graph.locator('button').get_by_text('通过',exact=True).click()
            expect(graph).to_have_attribute('data-state','approved')
            page.reload()
            expect(graph).to_have_attribute('data-state','approved')
            result=export(page)
            assert len(result['records'])==1 and result['records'][0]['status']=='approved'
        else:
            page.locator('#file').set_input_files(dict(name='verification-test.json',mimeType='application/json',
                                                       buffer=json.dumps(result).encode()))
            expect(page.locator('#message')).to_have_attribute('data-error','false')
            expect(graph).to_have_attribute('data-state','approved')
            assert export(page)['records']==result['records']
        assert not errors,errors
        print(f'{lang}: layout, original crop, translations, draft/import/export passed')
        ctx.close()
    comparison=browser.new_context(offline=True,viewport={'width':1260,'height':980})
    comparison.route('**/*',respond)
    page=comparison.new_page()
    page.goto(f'{BASE}/comparison.html')
    expect(page.locator('article')).to_have_count(6)
    expect(page.locator('article img')).to_have_count(18)
    assert page.locator('img').evaluate_all('items=>items.every(i=>i.complete && i.naturalWidth>0)')
    assert not external,external
    print('comparison: original + v1 + final loaded for all six images, no external requests')
