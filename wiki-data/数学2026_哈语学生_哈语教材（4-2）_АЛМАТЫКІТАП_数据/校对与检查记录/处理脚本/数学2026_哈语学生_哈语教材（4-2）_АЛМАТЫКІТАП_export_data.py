"""Export retained OCR artifacts without changing the proofread text."""
from pathlib import Path
import collections
import hashlib
import json
import math
import re
import shutil
import statistics
import sys

import fitz
from PIL import Image

ROOT = Path('/workspace')
REPO = ROOT / 'math2026p2_delivery'
OUT = REPO / 'wiki-data'
OUT.mkdir(parents=True,exist_ok=True)


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def write(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(p):
    return hashlib.file_digest(p.open('rb'), 'sha256').hexdigest()


def union(boxes):
    return [min(b[0] for b in boxes), min(b[1] for b in boxes),
            max(b[2] for b in boxes), max(b[3] for b in boxes)]


def intersection(a, b):
    return max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))


def area(b):
    return max(1, b[2]-b[0]) * max(1, b[3]-b[1])


def visual_order(lines):
    # A geometric convenience view, not an adjudicated reading order.
    rows = []
    for line in sorted(lines, key=lambda z: ((z['bbox'][1]+z['bbox'][3])/2, z['bbox'][0])):
        b = line['bbox']; cy = (b[1]+b[3])/2
        compatible = [r for r in rows[-8:] if abs(cy-r['cy']) < .35 * min(b[3]-b[1], r['h'])]
        if compatible:
            r = min(compatible, key=lambda r: abs(cy-r['cy']))
            r['lines'].append(line)
        else:
            rows.append({'cy':cy, 'h':b[3]-b[1], 'lines':[line]})
    return [line for r in sorted(rows, key=lambda r:r['cy'])
            for line in sorted(r['lines'], key=lambda z:z['bbox'][0])]


BOOKS = [('math-2026-grade4-part2', 'math2026p2_work', '数学2026_哈语学生_哈语教材（4-2）_АЛМАТЫКІТАП.pdf', 180)]

catalog = []
for book_id, work_name, filename, expected in BOOKS:
    work = ROOT / work_name
    target = OUT / book_id
    target.mkdir(exist_ok=True)
    source_pdf = work/filename
    final_pdf = ROOT/'output'/filename.replace('.pdf', '_OCR.pdf')
    for sub in ['source/pages', 'assets/layout-crops', 'assets/pdf-images', 'archive', 'review']:
        (target/sub).mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_pdf, target/'source'/filename)
    # The mathematics final PDF already resides in the repository root.
    if (REPO/final_pdf.name).exists():
        corrected_path = '../../'+final_pdf.name
    else:
        shutil.copy2(final_pdf, REPO/final_pdf.name)
        corrected_path = '../../'+final_pdf.name

    bundles = {}
    for sub in ['raw', 'final', 'layout', 'round1', 'round2']:
        fs = sorted((work/sub).glob('[0-9][0-9][0-9].json'))
        assert len(fs) == expected, (book_id, sub, len(fs))
        (target/'archive'/sub).mkdir(exist_ok=True)
        for f in fs:
            shutil.copy2(f, target/'archive'/sub/f.name)
        bundles[sub] = [read(f) for f in fs]
        write(target/(sub+'.json'), {
            'schema_version':'ocr-page-bundle/1.0', 'book_id':book_id,
            'kind':sub, 'page_count':expected,
            'description':'Each pages element is the unchanged retained per-page JSON object.',
            'pages':bundles[sub]})

    for name in ['adjudications.json', 'diffs.json', 'validation.json',
                 'additions_unique_a.json', 'additions_unique_b.json',
                 'removed_scan_marks.json', 'addition_adjudications.json', 'bullet_adjudications.json', 'marker_position_adjustments.json', 'source_profile.json', 'native_text_adoption.json', 'main_choices.json', 'main_reviews_final.json', 'source_profile.json', 'visual_review.json', 'render_adjustments.json', 'copy_validation.json', 'source_issues.json', 'geometry_adjudications.json', 'image_integrity.json', 'thin_symbol_fallbacks.json', 'manual_layout_repairs.json', 'question_marker_candidates.json', 'math_graphic_review.json', 'duplicate_candidates.json', 'toc_leader_review.json', 'font_embedding_repairs.json']:
        if (work/name).exists():
            shutil.copy2(work/name, target/'review'/name)
    existing_files = sorted((work/'original').glob('*_existing.json'))
    if existing_files:
        (target/'source/pdf-text').mkdir(exist_ok=True)
        for f in existing_files:
            shutil.copy2(f, target/'source/pdf-text'/f.name)

    orig = fitz.open(source_pdf)
    rebuilt = fitz.open(final_pdf)
    assert len(orig) == len(rebuilt) == expected
    book = {
        'schema_version':'textbook-wiki/1.0', 'book_id':book_id,
        'source_filename':filename, 'language':'kk-Cyrl', 'secondary_languages':['ru-Cyrl'],
        'source_pdf':{'path':'source/'+filename, 'sha256':sha(source_pdf), 'page_count':expected},
        'corrected_pdf':{'path':corrected_path, 'sha256':sha(final_pdf), 'page_count':expected},
        'coordinate_system':{'origin':'top-left', 'axes':'x-right,y-down',
            'bbox_format':'[x0,y0,x1,y1]', 'unit':'source_page_image_pixel',
            'pdf_unit':'point (1/72 inch)',
            'conversion':'pdf_x = image_x * pdf_width_pt / image_width; similarly for y'},
        'provenance':{'ocr_family':'PP-OCRv5',
            'recognition_model':'cyrillic_PP-OCRv5_mobile_rec',
            'layout_model':'PP-DocLayout-S',
            'text_status':'retained_final_after_two_proofreading_rounds_and_adjudication',
            'semantic_structure_status':'automatic_candidates_not_manually_reviewed',
            'confidence_warning':'ocr_confidence describes original OCR only, not corrected text accuracy',
            'final_authority':'archive/final/*.json; these include post-adjudication adjustments',
            'source_integrity':'180 source pages rendered successfully; original PDF retained unchanged.',
            'question_boundary_method':'No new semantic segmentation performed in this OCR delivery.',
            'native_text_retained_pages':[]},
        'title_candidates':[], 'lesson_candidates':[], 'pages':[],
        'assets':[], 'validation':{}}
    image_dedup = {}
    total_questions = 0

    for idx in range(expected):
        n = idx+1; pid = f'{book_id}:p{n:03}'
        final = bundles['final'][idx]
        raw = bundles['raw'][idx]
        assert final['page'] == raw['page'] == n
        w,h = final['width'], final['height']
        image_file = work/'original'/f'{n:03}.png'
        page_image = f'source/pages/{n:03}.png'
        shutil.copy2(image_file, target/page_image)
        im = Image.open(image_file).convert('RGB')
        assert im.size == (w,h)
        rect = orig[idx].rect
        raw_by_id = {str(z['id']):z for z in raw['lines']}
        lines=[]
        for z in final['lines']:
            rid = str(z['id']); b = z['bbox']; r = raw_by_id.get(rid)
            line = {'id':pid+':l'+rid, 'source_line_id':rid, 'text':z['text'],
                'bbox':b, 'polygon':z.get('poly'),
                'bbox_pdf_pt':[round(b[0]*rect.width/w,4),round(b[1]*rect.height/h,4),
                               round(b[2]*rect.width/w,4),round(b[3]*rect.height/h,4)],
                'raw_text':r['text'] if r else None,
                'source_line_ids':[pid+':l'+str(v) for v in z.get('source_line_ids',[rid] if r else [])],
                'raw_bbox':z.get('raw_bbox'),
                'review_decision':z.get('review_decision'),
                'ocr_confidence':r.get('score') if r else None,
                'text_origin':('native_pdf_text' if z.get('native_text') else ('ocr' if r else 'proofreading_addition')),
                'render_role':('source_graphic_with_unicode' if z.get('source_graphic') else 'pdf_text'),
                'text_changed':(r['text'] != z['text']) if r else None,
                'active':bool(z['text'].strip()),
                'vertical':z.get('vertical',False)}
            lines.append(line)
        ordered = visual_order([l for l in lines if l['active']])
        line_lookup = {l['id']:l for l in lines}
        page = {'id':pid, 'pdf_page_index':idx, 'pdf_page_number':n,
            'printed_page_label':None, 'image':page_image,
            'image_width':w,'image_height':h, 'pdf_width_pt':rect.width,
            'pdf_height_pt':rect.height, 'pdf_rotation':orig[idx].rotation,
            'spread_status':'not_split; source PDF page retained',
            'lines':lines, 'reading_order_candidate':[l['id'] for l in ordered],
            'text_with_line_breaks':'\n'.join(l['text'] for l in ordered),
            'layout_regions':[], 'paragraph_candidates':[], 'question_candidates':[],
            'form_fields':[], 'assets':[], 'proofreading_notes':final.get('uncertainties',[])}
        labels = [l for l in ordered if l['bbox'][1] > h*.9 and
                  re.fullmatch(r'[–—\-]?\s*\d{1,3}\s*[–—\-]?',l['text'].strip())]
        if labels:
            page['printed_page_label']=max(labels,key=lambda l:l['bbox'][1])['text']

        boxes=bundles['layout'][idx].get('res',{}).get('boxes',[])
        for j,z in enumerate(boxes):
            b=z['coordinate']; lid=pid+f':region{j:03}'
            refs=[l['id'] for l in ordered if intersection(l['bbox'],b)/area(l['bbox'])>.5]
            region={'id':lid,'model_label':z['label'],'model_confidence':z.get('score'),
                'bbox':b,'line_ids':refs,'review_status':'model_detection_unreviewed'}
            if z['label']=='table':
                region['table_structure_status']='not_cell_transcribed'
                region['cells']=None
            if z['label']=='formula':
                region['latex']=None
                region['formula_status']='image_and_corrected_lines_only; no_generated_latex'
            if z['label'] in ['image','header_image','table','chart','formula','seal']:
                crop=[max(0,math.floor(b[0])-2),max(0,math.floor(b[1])-2),
                      min(w,math.ceil(b[2])+2),min(h,math.ceil(b[3])+2)]
                if crop[2]>crop[0] and crop[3]>crop[1]:
                    aid=pid+f':crop{j:03}'
                    path=f'assets/layout-crops/{n:03}_{j:03}_{z["label"]}.png'
                    im.crop(crop).save(target/path,optimize=True)
                    book['assets'].append({'id':aid,'path':path,'kind':'source_layout_crop',
                        'page_id':pid,'bbox':crop,'model_region_id':lid,
                        'description':'Source crop; can contain surrounding text or decoration.'})
                    region['asset_id']=aid; page['assets'].append(aid)
            page['layout_regions'].append(region)

        for j,item in enumerate(rebuilt[idx].get_image_info(xrefs=True)):
            xref=item['xref']
            if not xref:continue
            blob=rebuilt.extract_image(xref)
            digest=hashlib.sha256(blob['image']).hexdigest()
            if digest not in image_dedup:
                path=f'assets/pdf-images/{digest[:24]}.{blob["ext"]}'
                (target/path).write_bytes(blob['image'])
                aid=book_id+':image:'+digest[:24]
                image_dedup[digest]=aid
                book['assets'].append({'id':aid,'path':path,'kind':'rebuilt_pdf_embedded_image',
                    'sha256':digest,'width':blob['width'],'height':blob['height'],
                    'placements':[],'description':'Embedded illustration crop; vector artwork is represented by the source page and PDF.'})
            aid=image_dedup[digest]
            b=item['bbox']; pb=[b[0]*w/rect.width,b[1]*h/rect.height,b[2]*w/rect.width,b[3]*h/rect.height]
            asset=next(a for a in book['assets'] if a['id']==aid)
            asset['placements'].append({'page_id':pid,'bbox':pb,'bbox_pdf_pt':list(b)})
            if aid not in page['assets']:page['assets'].append(aid)

        # Paragraphs use model text regions first. Overlap is resolved once;
        # every remaining active line has a singleton block, so no text is lost.
        assigned=set()
        for region in sorted(page['layout_regions'], key=lambda r:area(r['bbox']),reverse=True):
            if region['model_label'] not in ['text','paragraph_title','doc_title','abstract','content']:
                continue
            refs=[rid for rid in region['line_ids'] if rid not in assigned]
            if not refs:continue
            refs=sorted(refs,key=lambda rid:page['reading_order_candidate'].index(rid))
            page['paragraph_candidates'].append({'id':region['id']+':block',
                'kind_candidate':region['model_label'], 'line_ids':refs,
                'bbox':union([line_lookup[r]['bbox'] for r in refs]),
                'text_with_line_breaks':'\n'.join(line_lookup[r]['text'] for r in refs),
                'review_status':'automatic_grouping_unreviewed'})
            assigned.update(refs)
        for l in ordered:
            if l['id'] not in assigned:
                page['paragraph_candidates'].append({'id':l['id']+':block',
                    'kind_candidate':'line','line_ids':[l['id']], 'bbox':l['bbox'],
                    'text_with_line_breaks':l['text'],'review_status':'ungrouped_line'})
        page['paragraph_candidates'].sort(key=lambda b:(b['bbox'][1],b['bbox'][0]))

        # OCR delivery only; no unverified question/module boundaries are published.
        for l in ordered:
            m=re.match(r'^(Оқуға кеткен уақыт|Минутына оқылған сөз саны|Бағасы|Мұғалімнің қолы|Барлық сөз саны)\s*:(.*)$',l['text'])
            if m:
                remainder=m.group(2).strip()
                page['form_fields'].append({'id':l['id']+':field', 'label':m.group(1)+':',
                    'line_id':l['id'], 'bbox':l['bbox'],
                    'printed_value':remainder if remainder else None,
                    'value':None,'status':'no_user_value_added',
                    'field_type_candidate':'signature' if 'қолы' in m.group(1) else 'measurement_or_score'})

        # Explicit math lesson headers are inherited only as candidate links.
        lesson=re.compile(r'^(\d{1,2})\s*[-–]?\s*сабақ\b',re.I)
        for l in ordered:
            m=lesson.match(l['text'])
            if m and l['bbox'][1]<h*.14:
                book['lesson_candidates'].append({'printed_number':m.group(1),
                    'header_text':l['text'],'page_id':pid,'line_id':l['id'],
                    'review_status':'explicit_header_candidate'})
        for region in page['layout_regions']:
            if region['model_label'] in ['doc_title','paragraph_title'] and region['line_ids']:
                book['title_candidates'].append({'id':region['id']+':title',
                    'page_id':pid,'line_ids':region['line_ids'],
                    'text_with_line_breaks':'\n'.join(line_lookup[r]['text'] for r in region['line_ids']),
                    'review_status':'model_title_candidate'})
        book['pages'].append(page)
        if n%25==0:print(book_id,n,flush=True)

    book['validation']={'page_count':len(book['pages']),
        'total_final_lines':sum(len(p['lines']) for p in book['pages']),
        'active_final_lines':sum(l['active'] for p in book['pages'] for l in p['lines']),
        'question_candidates':total_questions,'assets':len(book['assets']),
        'all_final_lines_exported':True}
    write(target/'wiki.json',book)
    catalog.append({'book_id':book_id,'source_filename':filename,
        'pages':expected,'wiki_json':book_id+'/wiki.json',
        'raw_json':book_id+'/raw.json','final_json':book_id+'/final.json',
        'source_pdf_sha256':book['source_pdf']['sha256'],**book['validation']})
    print(book_id,'DONE',book['validation'],flush=True)

write(OUT/'catalog.json',{'schema_version':'textbook-catalog/1.0', 'books':catalog})

# Hashes cover every delivered data file except the hash manifest itself.
manifest=[]
for p in sorted(OUT.rglob('*')):
    if p.is_file() and p.name!='checksums.json':
        manifest.append({'path':p.relative_to(OUT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
write(OUT/'checksums.json',{'algorithm':'sha256','files':manifest})
print('FILES',len(manifest),'BYTES',sum(z['bytes'] for z in manifest),flush=True)
