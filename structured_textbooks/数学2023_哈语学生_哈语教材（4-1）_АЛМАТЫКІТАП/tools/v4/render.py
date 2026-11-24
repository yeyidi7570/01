"""Render both offline review editions from a shared dataset and interface."""
import base64
import io
import json
from pathlib import Path

from PIL import Image

HERE = Path(__file__).parent

def script_json(data):
    return json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('<', r'\u003c')

def png_uri(data):
    return 'data:image/png;base64,' + base64.b64encode(data).decode()

def render(data, supplement, source, out):
    scans = {}
    images = {}
    for page in data['pages']:
        p = page['pdf_page']
        file = source / f'scan{p}.png'
        with Image.open(file) as scan:
            assert scan.size == (page['width'], page['height'])
            scans[p] = scan.copy()
        images[page['scan_asset_id']] = png_uri(file.read_bytes())
    for key, loc in data['crop_assets'].items():
        stream = io.BytesIO()
        scans[loc['pdf_page']].crop(tuple(loc['bbox'])).save(stream, format='PNG', optimize=True)
        images[key] = png_uri(stream.getvalue())
    template = (HERE/'review.html').read_text()
    for lang, localized in supplement.items():
        html = template.replace('@@LANG@@',lang).replace('@@CSS@@',(HERE/'review.css').read_text()).replace(
            '@@JS@@',(HERE/'review.js').read_text()).replace('@@DATA@@',script_json(data)).replace(
            '@@IMAGES@@',script_json(images)).replace('@@AUX@@',script_json(localized))
        (out/f'math_grade4_lesson1_review_{lang}_v4.html').write_text(html)
