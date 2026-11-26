"""Build a local comparison page and extract source crops after SVG generation."""
from html import escape
from pathlib import Path
import json
from PIL import Image

root=Path(__file__).resolve().parent
data=json.loads((root/'content.v1.json').read_bytes())
notes={
 'm02-same-direction':'两箭头均向右，起点分别在后、前，旗标在最右。第二版显式标出公式的接近速度下标。',
 'm02-toward-each-other':'两箭头由外侧向内，旗标在中点。第二版显式标出公式的接近速度下标。',
 'm02-apart':'两箭头共用中央起点并背向，原图无旗标。第二版显式标出公式的远离速度下标。',
 'm03-motorcycles':'保留后方 v₂ 与前方 v₁ 的对应、最右旗标，并显示只跨两个起点的 50 千米括线。',
 'm04-vehicles':'明确 60 千米括线的两端，以及从公交车起点向右延伸、上方标未知时间的红箭头。',
 'm05-distance-time':'横向每小格 1 分钟，纵向每小格 100 米。标数与小格分开记录，7–17 分钟重合段用叠线表示。',
}
style='''body{margin:2rem auto;max-width:1380px;padding:0 1.3rem;font:16px/1.5 system-ui;color:#183049}
h1,h2{line-height:1.2} article{padding:1.25rem 0;border-top:1px solid #c5d3df} figure{margin:0}
.row{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1rem} figcaption{font-weight:650}
img{display:block;width:100%;border:1px solid #dae4ee;background:#fff;margin-top:.35rem}
@media(max-width:780px){.row{grid-template-columns:1fr}}'''
items=[]
for unit in data['lesson']['units']:
    for obj in unit.get('elements',[]):
        if obj['type']!='informative_image':
            continue
        ref=obj['page_refs'][0]
        key='-'.join(obj['id'].split(':')[-2:])
        png=root/'validation/original'/f'{key}.png'
        scan=Image.open(root/'source'/f"{ref['pdf_page']}-scan.png")
        bbox=ref['bbox'].copy()
        if unit['module_number']==2:
            bbox[3]=948  # the diagram and its formula share one printed panel
        scan.crop(bbox).save(png)
        figures=[]
        for folder,suffix,name in [('original','png','原书裁图'),('first','svg','首次重绘'),('final','svg','最终重绘')]:
            rel=f'validation/{folder}/{key}.{suffix}'
            if not (root/rel).exists():
                continue
            figures.append(f'<figure><figcaption>{name}</figcaption><img src="{rel}" alt="{name}"></figure>')
        items.append(f'<article id="{key}"><h2>第 {unit["module_number"]} 题 · {escape(key)}</h2>'
                     f'<div class="row">{"".join(figures)}</div><p>{escape(notes[key])}</p></article>')
(root/'comparison.html').write_text(
    '<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
    '<title>第 88 课必要图示重绘对照</title><style>'+style+'</style><main><h1>第 88 课必要图示重绘对照</h1>'
    '<p>PDF 与印刷第 29–31 页。示意图只校对数学信息，图形等距排版不表示原书规定了比例。'
    '折线重合段用两色实线与虚线叠加，两条线的坐标相同。</p>'+''.join(items)+'</main></html>\n',encoding='utf-8')
