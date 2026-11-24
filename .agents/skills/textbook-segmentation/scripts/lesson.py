#!/usr/bin/env python3
"""Plan, render and validate textbook Lesson packages; no OCR or Git mutations."""
import argparse
import base64
import hashlib
from html import escape
from html.parser import HTMLParser
from io import BytesIO
import json
from pathlib import Path
import re
import sys
import unicodedata

ASSETS = Path(__file__).resolve().parents[1] / 'assets' / 'review'
FILES = ('content.json', 'review_zh.html', 'review_kk.html')
MAX_BYTES = 100 * 1024 * 1024


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def integer(value):
    return type(value) is int


def selected_lessons(selector, available):
    if selector == 'all':
        require(bool(available), 'all requires --catalog with confirmed boundaries')
        return sorted(available)
    numbers = set()
    for part in re.split(r'[,，]', selector):
        match = re.fullmatch(r'\s*([0-9]+)(?:\s*[-–—]\s*([0-9]+))?\s*', part)
        require(match is not None, f'invalid lesson selection: {part}')
        first, last = int(match[1]), int(match[2] or match[1])
        require(0 < first <= last, f'invalid lesson range: {part}')
        if available:
            require(last-first+1 <= len(available), f'lesson range outside catalog: {part}')
        numbers.update(range(first, last + 1))
    require(not available or numbers <= available.keys(), 'some selected lessons are outside the catalog')
    return sorted(numbers)


def catalog(path):
    result = {}
    if path:
        for entry in read(path)['lessons']:
            n, pages, printed = (entry[k] for k in ('number', 'pdf_pages', 'printed_pages'))
            require(integer(n) and n > 0 and n not in result, 'invalid or duplicate catalog lesson number')
            require(pages and all(integer(p) and p > 0 for p in pages)
                    and pages == sorted(set(pages)) and len(pages) == len(printed)
                    and entry['title_kk'] and entry['boundary_evidence'],
                    f'missing or invalid boundary evidence for lesson {n}')
            result[n] = entry
    return result


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def plan(args):
    require(args.book not in ('', '.', '..') and '/' not in args.book and '\\' not in args.book,
            'use the full textbook directory name as one path component')
    base = args.repo.resolve() / 'structured_textbooks'
    book = base / args.book
    require(book.is_dir() and book.resolve().parent == base.resolve(), f'textbook directory missing: {book}')
    known = catalog(args.catalog)
    results = []
    for n in selected_lessons(args.lessons, known):
        slug = f'lesson_{n:03}'
        dst = book / '01_segmentation' / slug
        review = book / '02_segmentation_review' / slug
        present = [name for name in FILES if (dst / name).is_file()]
        state = 'rerun_candidate' if args.rerun and present else 'inspect_existing' if present else 'new'
        results.append(dict(lesson=slug, path=str(dst), action=state, existing_files=present,
                            boundary=known.get(n), feedback={str(p.relative_to(book)):sha(p)
                            for p in sorted(review.rglob('*.json')) if p.is_file()}))
    print(json.dumps(results, ensure_ascii=False, indent=2))


def validate_content(data):
    lesson = data['lesson']
    require(data['data_version'] and data['book']['id'] and data['book']['title_kk']
            and lesson['id'] and lesson['title_kk'] and integer(lesson['number']) and lesson['number'] > 0,
            'missing book, Lesson or version metadata')
    require(data['review_status'] == lesson['review_status'] == 'pending_review',
            'initial segmentation must be pending_review')
    require(lesson['boundary_evidence'] and data['source'] and lesson['units'],
            'missing source, Lesson boundary evidence or visual units')
    note_badges = set(data['schema_rules']['instructional_note_badges'])
    require(bool(note_badges), 'missing confirmed Instructional Note badges')
    pages = {p['pdf_page']:p for p in data['pages']}
    ids = {}
    scans = set()
    require(pages and list(pages) == sorted(pages) and len(pages) == len(data['pages'])
            and all(integer(p) and p > 0 for p in pages), 'invalid or duplicate PDF pages')
    require(lesson['pdf_page_range'] == [min(pages), max(pages)], 'PDF range does not match pages')
    if 'printed_page_range' in lesson:
        require(lesson['printed_page_range'] == [pages[min(pages)]['printed_page'], pages[max(pages)]['printed_page']],
                'printed range does not match pages')
    for p in pages.values():
        require(all(integer(p[k]) and p[k] > 0 for k in ('width','height')), 'invalid scan dimensions')
        require(p['scan_asset_id'] not in scans and p['scan_asset_id'] and p['scan_path'], 'invalid scan reference')
        scans.add(p['scan_asset_id'])

    def register(obj):
        key = obj['id']
        require(isinstance(key,str) and key and key not in ids, f'duplicate or missing object ID: {key!r}')
        ids[key] = obj

    def location(ref):
        p = pages[ref['pdf_page']]
        box = ref['bbox']
        require(ref['scan_asset_id'] == p['scan_asset_id'] and ref['printed_page'] == p['printed_page'],
                f'conflicting page reference: {ref}')
        require(len(box)==4 and all(integer(x) for x in box), f'invalid box: {ref}')
        x,y,r,b = box
        require(0 <= x < r <= p['width'] and 0 <= y < b <= p['height'], f'box outside scan: {ref}')

    for p in pages.values():
        register(p)
    for ref in data.get('crop_assets',{}).values():
        location(ref)

    def visit(items, order, parent):
        require(order == [o['id'] for o in items], f'content_order mismatch for {parent}')
        for o in items:
            register(o)
            require(o['parent_id'] == parent and o['page_refs'] and o['review_status'], f'missing parent, region or status: {o["id"]}')
            for ref in o['page_refs']:
                location(ref)
            kind = o['type']
            if kind == 'instructional_note':
                require(parent==lesson['id'] and o['instructional_note_badge'] in note_badges, f'invalid Note: {o["id"]}')
            if kind == 'module_badge' and o.get('badge_origin')=='lesson_inherited':
                is_self_check = lesson['title_kk'].strip().upper()=='ӨЗІҢДІ ТЕКСЕР' or lesson.get('self_check') is True
                require(is_self_check and o.get('text_kk','').strip().upper()=='ӨЗІҢДІ ТЕКСЕР',
                        f'unjustified inherited Badge: {o["id"]}')
            if kind == 'subtask_number':
                text = o['text_kk'].strip()
                require(all(not c.isalpha() or c.isupper() and 'CYRILLIC' in unicodedata.name(c,'')
                            for c in text), f'non-uppercase-Cyrillic subtask number: {o["id"]}')
            if o.get('crop_asset_id'):
                require(o['crop_asset_id'] in data['crop_assets'], f'missing crop asset: {o["id"]}')
            if kind == 'informative_image':
                require(o.get('crop_asset_id') and (o.get('structured_description') or o.get('review_flags')),
                        f'image needs a crop and description or a review flag: {o["id"]}')
            if kind == 'table' and 'cells' in o:
                occupied=set()
                require(all(integer(o[k]) and o[k]>0 for k in ('row_count','column_count')), f'invalid table: {o["id"]}')
                for cell in o['cells']:
                    register(cell)
                    r,c,rs,cs=(cell[k] for k in ('row','column','rowspan','colspan'))
                    require(all(integer(v) for v in (r,c,rs,cs)) and rs>0 and cs>0
                            and 0<=r<r+rs<=o['row_count'] and 0<=c<c+cs<=o['column_count'], f'invalid cell span: {cell["id"]}')
                    span={(i,j) for i in range(r,r+rs) for j in range(c,c+cs)}
                    require(not occupied & span, f'overlapping cell: {cell["id"]}')
                    occupied.update(span)
                    for ref in cell.get('page_refs',[]):
                        location(ref)
                require(len(occupied)==o['row_count'] * o['column_count'], f'cells do not cover grid: {o["id"]}')
            if kind == 'table' and 'cells' not in o:
                require(o.get('crop_asset_id') and o.get('review_flags'), f'unresolved table needs a crop and review flag: {o["id"]}')
            visit(o.get('elements',[]),o.get('content_order',[]),o['id'])

    visit(lesson['units'],lesson['content_order'],lesson['id'])
    for link in lesson['teaching_links']:
        require(all(link[k] in ids for k in ('parent_id','from_id','to_id'))
                and link['relationship'] in ('supports','uses_as_material')
                and link['from_id']!=link['to_id'] and link.get('rationale_kk')
                and link['page_refs'] and link['review_status'], f'invalid teaching link: {link["id"]}')
        for ref in link['page_refs']:
            location(ref)
        register(link)
    suggestions = {}
    for o in data['ocr_suggestions']:
        require(o['id'] not in suggestions and o['id'] not in ids and o['object_id'] in ids
                and o['reason_kk'] and o['review_status'] and o['page_refs'], f'invalid OCR suggestion: {o["id"]}')
        for ref in o['page_refs']:
            location(ref)
        suggestions[o['id']] = o['object_id']
    require(suggestions == {sid:o['id'] for o in ids.values() for sid in o.get('ocr_suggestion_ids',[])},
            'OCR suggestion references do not match evidence records')
    return ids, scans | set(data.get('crop_assets',{}))


class ReviewHTML(HTMLParser):
    """Collect the data-bearing scripts and check the offline document shell."""
    def __init__(self, text):
        super().__init__(convert_charrefs=False)
        self.sections = {}
        self.lang = None
        self.csp = None
        self.current = None
        self.ids = set()
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if 'id' in values:
            require(values['id'] not in self.ids, f'duplicate HTML ID: {values["id"]}')
            self.ids.add(values['id'])
        if tag == 'html':
            self.lang = values.get('lang')
        if tag == 'meta' and values.get('http-equiv', '').lower() == 'content-security-policy':
            self.csp = values.get('content')
        require(not ({'src','srcset','poster','data','background'} & values.keys())
                and tag not in {'link','iframe','base','object','embed'},
                f'non-inline resource reference: {tag}')
        if tag in ('script', 'style'):
            key = values.get('id', tag)
            require(key not in self.sections, f'duplicate HTML section: {key}')
            self.sections[key] = ''
            self.current = key

    def handle_data(self, data):
        if self.current:
            self.sections[self.current] += data

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.current = None


def audit_package(directory, allow_legacy=False):
    for name in FILES:
        p=directory/name
        require(p.is_file() and 0 < p.stat().st_size <= MAX_BYTES, f'missing, empty or oversized file: {p}')
    data=read(directory/'content.json')
    ids, asset_ids=validate_content(data)
    slug=f'lesson_{data["lesson"]["number"]:03}'
    if re.fullmatch(r'lesson_\d+', directory.name):
        require(directory.name==slug, f'folder name must be {slug}')
    paired={}
    for lang in ('zh','kk'):
        html=ReviewHTML((directory/f'review_{lang}.html').read_text(encoding='utf-8'))
        require(html.lang==lang and html.csp and "default-src 'none'" in html.csp, f'invalid offline shell: {lang}')
        require(allow_legacy or {'cards','review-scroll'} <= html.ids, f'continuous reviewer missing: {lang}')
        require(json.loads(html.sections['dataset'])==data, f'embedded dataset does not match content.json: {lang}')
        assets=json.loads(html.sections['assets'])
        require(set(assets)==asset_ids, f'embedded asset IDs do not match content.json: {lang}')
        payloads={}
        for asset, uri in assets.items():
            prefix, sep, b64=uri.partition(',')
            require(sep and prefix in {'data:image/png;base64','data:image/jpeg;base64','data:image/webp;base64'},
                    f'invalid inline image: {asset}')
            payloads[asset]=base64.b64decode(b64,validate=True)
            require(payloads[asset], f'empty embedded image: {asset}')
        for p in data['pages']:
            if p.get('scan_sha256'):
                require(hashlib.sha256(payloads[p['scan_asset_id']]).hexdigest()==p['scan_sha256'],
                        f'embedded scan checksum mismatch: {p["scan_asset_id"]}')
        behavior=(assets, html.sections['script'], html.sections['style'])
        aux=json.loads(html.sections['translations'])
        require(lang=='zh' or not aux, 'Kazakh page must not depend on Chinese translations')
        paired[lang]=behavior
    require(paired['zh']==paired['kk'], 'both editions must embed identical assets and logic')
    return dict(lesson_id=data['lesson']['id'], objects=len(ids), assets=len(asset_ids),
                notes=sum(o.get('type')=='instructional_note' for o in ids.values()),
                modules=sum(o.get('type')=='module' for o in ids.values()),
                ocr_suggestions=len(data['ocr_suggestions']))


def script_json(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',',':'), allow_nan=False).replace('<','\\u003c')


def render(args):
    from PIL import Image

    raw=args.content.read_bytes()
    data=json.loads(raw)
    ids,_=validate_content(data)
    translations=read(args.translations)
    permitted=set(ids)
    permitted.update(o['id'] for o in data['ocr_suggestions'])
    permitted.update(f'{o["id"]}#{flag["code"]}' for o in ids.values() for flag in o.get('review_flags',[]))
    require(translations.get('title') and isinstance(translations['objects'],dict)
            and set(translations['objects']) <= permitted
            and all(isinstance(s,str) and s.strip() for s in translations['objects'].values()),
            'invalid Chinese auxiliary translations or unknown object IDs')
    paths=read(args.scans)
    require(set(paths)=={p['scan_asset_id'] for p in data['pages']}, 'scan manifest must match the Lesson scan IDs')
    imgs, images={}, {}
    def embed(fmt, blob):
        mime={'PNG':'png','JPEG':'jpeg','WEBP':'webp'}[fmt]
        return f'data:image/{mime};base64,' + base64.b64encode(blob).decode('ascii')
    for p in data['pages']:
        id_=p['scan_asset_id']
        blob=(args.scans.parent/paths[id_]).read_bytes()
        if p.get('scan_sha256'):
            require(hashlib.sha256(blob).hexdigest()==p['scan_sha256'], f'incorrect input scan checksum: {id_}')
        with Image.open(BytesIO(blob)) as im:
            require(im.size==(p['width'],p['height']), f'input scan size differs from coordinates: {id_}')
            images[id_]=embed(im.format,blob)
            imgs[id_]=im.copy()
    for id_, ref in data.get('crop_assets',{}).items():
        require(id_ not in images, f'duplicate asset ID: {id_}')
        with BytesIO() as stream:
            im=imgs[ref['scan_asset_id']].crop(tuple(ref['bbox']))
            if im.mode=='CMYK':
                im=im.convert('RGB')
            im.save(stream,format='PNG',optimize=True)
            images[id_]=embed('PNG',stream.getvalue())
    html=(ASSETS/'page.html').read_text(encoding='utf-8')
    fields=dict(DATA=script_json(data),IMAGES=script_json(images),CSS=(ASSETS/'review.css').read_text(encoding='utf-8'),
                JS=(ASSETS/'review.js').read_text(encoding='utf-8'))
    for key in (*fields,'LANG','TITLE','AUX'):
        require(html.count(f'@@{key}@@')==1, f'bad template marker: {key}')
    require(not args.output.exists(), f'output exists; choose a fresh staging directory: {args.output}')
    # Nothing is written into the canonical Lesson directory by this renderer.
    args.output.mkdir()
    (args.output/'content.json').write_bytes(raw)
    for lang in ('zh','kk'):
        title=data['lesson']['title_kk']
        translations_for_ui=translations if lang=='zh' else {}
        values=dict(fields,LANG=lang,TITLE=escape(title),AUX=script_json(translations_for_ui))
        page=re.sub(r'@@([A-Z]+)@@',lambda m:values[m[1]],html)
        (args.output/f'review_{lang}.html').write_text(page,encoding='utf-8')
    print(json.dumps(audit_package(args.output),ensure_ascii=False))


def compare(args):
    old = read(args.old)
    new = read(args.new)
    require(old['book']['id']==new['book']['id'] and old['lesson']['id']==new['lesson']['id']
            and old['lesson']['number']==new['lesson']['number'], 'different Lesson identity')
    a,_=validate_content(old)
    b,_=validate_content(new)
    shared=a.keys() & b.keys()
    def own(obj):
        return {k:v for k,v in obj.items() if k not in ('elements','cells')}
    changed={k for k in shared if own(a[k])!=own(b[k])}
    print(json.dumps(dict(old_version=old['data_version'],new_version=new['data_version'],
        unchanged=sorted(shared-changed),changed=sorted(changed),removed=sorted(a.keys()-b.keys()),
        added=sorted(b.keys()-a.keys())),ensure_ascii=False,indent=2))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('plan',help='read-only inventory for a textbook and Lesson selection')
    p.add_argument('--repo',type=Path,default=Path.cwd())
    p.add_argument('--book',required=True)
    p.add_argument('--lessons',required=True,help='e.g. 2, 5-8, 2,5-8, or all')
    p.add_argument('--catalog',type=Path)
    p.add_argument('--rerun',action='store_true')
    r=sub.add_parser('render',help='render three artifacts to a new staging directory from confirmed input data')
    for name in ('content','scans','translations','output'):
        r.add_argument(f'--{name}',type=Path,required=True)
    c=sub.add_parser('check',help='check content, assets and bilingual embedded parity')
    c.add_argument('--lesson-dir',type=Path,required=True)
    c.add_argument('--allow-legacy-review',action='store_true')
    d=sub.add_parser('compare',help='list stable, changed, removed and added IDs; no migration')
    d.add_argument('--old',type=Path,required=True)
    d.add_argument('--new',type=Path,required=True)
    args=parser.parse_args()
    try:
        if args.command=='plan':
            plan(args)
        elif args.command=='render':
            render(args)
        elif args.command=='check':
            print(json.dumps(audit_package(args.lesson_dir,args.allow_legacy_review),ensure_ascii=False))
        else:
            compare(args)
    except (OSError, ValueError, KeyError, TypeError, AttributeError, ImportError) as err:
        parser.exit(1,f'Error: {err}\n')


if __name__=='__main__':
    main()
