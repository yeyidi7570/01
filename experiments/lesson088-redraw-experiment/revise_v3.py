"""Keep the observed directional-arrow length ordering without assigning a scale."""
from pathlib import Path
import json

root=Path(__file__).resolve().parent
data=json.loads((root/'content.v2.json').read_bytes())
aux=json.loads((root/'translations.v2.json').read_bytes())
items={o['id'].rsplit(':',1)[-1]:o for unit in data['lesson']['units'] for o in unit.get('elements',[])}
data['data_version']='2026-11-26-experiment-redraw-3'
for name in ('same-direction','motorcycles','vehicles'):
    item=items[name]
    description=item['structured_description']
    longer,shorter=description['relations'][0]['arrows']
    longer['length_hint']='longer'
    shorter['length_hint']='shorter'
    description['description_kk']+=' Артқы дененің жебесі алдыңғы дененікінен ұзын; сызбада ұзындық масштабы берілмеген.'
    aux['objects'][item['id']]+=' 原图中后方箭头较长，原书未给箭头长度的比例尺。'
for name,payload in [('content.final.json',data),('translations.final.json',aux)]:
    with (root/name).open('x',encoding='utf-8') as f:
        f.write(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
