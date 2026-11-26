"""Apply findings from the source/first-redraw comparison to the frozen cut."""
from pathlib import Path
import json

root=Path(__file__).resolve().parent
data=json.loads((root/'content.v1.json').read_bytes())
aux=json.loads((root/'translations.v1.json').read_bytes())
obj={o['id'].rsplit(':',1)[-1]:o for u in data['lesson']['units'] for o in u.get('elements',[]) if o['type']=='informative_image'}
data['data_version']='2026-11-26-experiment-redraw-2'
for key in ('same-direction','toward-each-other','apart'):
    item=obj[key]
    description=item['structured_description']
    relation=description['relations'][0]
    symbol,op=('қаш.','+') if key=='apart' else ('жақ.','−' if key=='same-direction' else '+')
    relation['formula_tokens']=[{'text':'v','subscript':symbol},{'text':' = '},
                                {'text':'v','subscript':'1'},{'text':f' {op} '},{'text':'v','subscript':'2'}]
    item['page_refs'][0]['bbox'][3]=948
    data['crop_assets'][item['crop_asset_id']]['bbox'][3]=948
    if key=='apart':
        description['description_kk']+=' Формулада қашықтау жылдамдығының «қаш.» индексі берілген.'
        aux['objects'][item['id']]+=' 图中的公式下标「қаш.」表示远离。'
    else:
        description['description_kk']+=' Формулада жақындау жылдамдығының «жақ.» индексі берілген.'
        aux['objects'][item['id']]+=' 图中的公式下标「жақ.」表示接近。'

item=obj['motorcycles']
item['structured_description']['relations'][0]['distances'][0]['annotation']='brace_below_segment'
item['structured_description']['description_kk']+=' 50 км деген жазу төменгі доғамен екі бастапқы нүктеге ғана жалғанған.'
aux['objects'][item['id']]+=' 下方 50 千米弧线只连接两车的起点。'

item=obj['vehicles']
d=item['structured_description']
r=d['relations'][0]
r['distances'][0]['annotation']='brace_below_segment'
r['annotations']=[{'kind':'forward_arrow_label','from':'bus','direction':'right','color':'#ab392f','label':r.pop('unknown_label')}]
d['description_kk']+=' S = 60 км жақшасы екі бастапқы нүктенің астында. t = ? сағ жазуы автобус нүктесінен оңға созылған қызыл жебенің үстінде.'
aux['objects'][item['id']]+=' 60 千米的括线连在两起点下方。未知时间写在从公交车起点向右延伸的红箭头上方。'

item=obj['distance-time']
d=item['structured_description']
r=d['relations'][0]
r['grid_cells']={'x':1,'y':100,'shape':'square'}
r['grid_extent']=[18,600]
r['shared_path']={'series':['Арман','Әлия'],'vertices':[[7,500],[12,500],[17,0]],
                  'label':'Ортақ бөлік: 7–17 мин'}
for s in r['series']:
    s['segments']=[{'from':a,'to':b,'distance_change':('increase' if b[1]>a[1] else 'decrease' if b[1]<a[1] else 'constant')}
                   for a,b in zip(s['vertices'],s['vertices'][1:])]
d['description_kk']=(
    'Көлденең ось t (мин), әр торкөз 1 минут, әр 2 минут сайын сан жазылған. '
    'Тік ось S (м), әр торкөз 100 м. Көк сызық Армандікі: 0–2 минутта 0-ден 300 м-ге дейін, '
    '2–5 минутта 300 м-де өзгермейді, 5–7 минутта 300-ден 500 м-ге дейін. '
    'Қызыл сызық Әлиянікі: 5 минутта 0-ден басталып, 7 минутта 500 м-ге жетеді. '
    '7–12 минутта екі сызық 500 м деңгейінде, 12–17 минутта 500 м-ден 0-ге дейін түседі. '
    '7–17 минутта координаталары бірдей.')
aux['objects'][item['id']]=(
    '横轴 t 为时间，每小格 1 分钟，每 2 分钟标数。纵轴 S 为离起点的距离，每小格 100 米。'
    '蓝线为阿尔曼。0–2 分钟从 0 米到 300 米，2–5 分钟保持在 300 米，5–7 分钟升至 500 米。'
    '红线为阿丽娅。第 5 分钟从 0 米出发，第 7 分钟到 500 米。'
    '两条线在 7–12 分钟均保持在 500 米，12–17 分钟均由 500 米降至 0 米。'
    '第 7 至 17 分钟两条线的坐标相同。')
item['review_flags']=[{'code':'overlap_print_offset',
                       'description_kk':'Ортақ бөліктегі екі түстің баспа сызықтары аздап ығысқан. Торда олар бір мәнге жатады.'}]
aux['objects'][item['id']+'#overlap_print_offset']='两种颜色的印刷笔画略有错位，按同一网格坐标解释。可对照原图复核。'

for name,payload in [('content.v2.json',data),('translations.v2.json',aux)]:
    with (root/name).open('x',encoding='utf-8') as f:
        f.write(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
