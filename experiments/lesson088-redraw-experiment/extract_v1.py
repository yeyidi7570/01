"""Construct the first cut from source scans and the accompanying source OCR."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'source'
manifest = json.loads((SOURCE / 'manifest.json').read_bytes())
book_id = 'math-2023-grade4-part3'
lesson_id = f'{book_id}:lesson-088'
status = 'pending_review'
page_numbers = (29, 30, 31)
fixed = {p: {l['id']:l for l in json.loads((SOURCE/f'{p}-final.json').read_bytes())['lines']} for p in page_numbers}
raw = {p: {l['id']:l for l in json.loads((SOURCE/f'{p}-raw.json').read_bytes())['lines']} for p in page_numbers}
units, crops, suggestions, translations = [], {}, [], {}
title = 'Бір бағыттағы қуып жету қозғалысына берілген есептер. Қозғалыс графиктері'
theme = 'Табиғат өзгерістері. Көшкін және сырғыма'

def location(p, box):
    return dict(pdf_page=p, printed_page=str(p), bbox=list(box), scan_asset_id=f'{book_id}:p{p:03}:scan')

def span(p, ids):
    bounds = [fixed[p][i]['bbox'] for i in ids]
    return [min(b[0] for b in bounds), min(b[1] for b in bounds),
            max(b[2] for b in bounds), max(b[3] for b in bounds)]

def normalized(p, ids):
    return re.sub(r'\s+', ' ', re.sub(r'-\s+(?=[а-яәіңғүұқөһ])', '', ' '.join(fixed[p][i]['text'] for i in ids))).strip()

def add(parent, key, kind, p, ids='', box=None, kk=None, zh=None, *, crop=False, **fields):
    ids = ids.split()
    parent_id = parent['id'] if parent else lesson_id
    ref = location(p, box or span(p, ids))
    obj = dict(id=f'{parent_id}:{key}', parent_id=parent_id, type=kind,
               review_status=status, page_refs=[ref], **fields)
    if parent:
        parent.setdefault('elements',[]).append(obj)
        parent.setdefault('content_order',[]).append(obj['id'])
    else:
        units.append(obj)
    if zh:
        translations[obj['id']] = zh
    if crop:
        asset = obj['id']+':crop'
        crops[asset] = ref
        obj['crop_asset_id'] = asset
    if ids:
        evidence = [dict(line_id=i, raw=raw[p].get(i,{}).get('text'), existing_corrected=fixed[p][i]['text']) for i in ids]
        obj['ocr_evidence'] = evidence
    if kk is not None or (ids and kind not in ('module','informative_image','table')):
        obj['text_kk'] = kk if kk is not None else normalized(p, ids)
        if ids and (obj['text_kk'] != normalized(p,ids) or
                    any(e['raw'] != e['existing_corrected'] for e in evidence)):
            suggestion(obj, evidence, obj['text_kk'],
                       'Баспа жолдары мен таңбалары түпнұсқа бетінен тексерілді.')
    return obj

def suggestion(obj, evidence, value, reason):
    sid=obj['id']+':ocr'
    obj['ocr_suggestion_ids']=[sid]
    suggestions.append(dict(id=sid,object_id=obj['id'],category='structure_recognition' if not evidence else 'ocr_character',
                            reason_kk=reason,page_refs=obj['page_refs'],review_status=status,source_lines=evidence,
                            suggested_value=value,proposed_changes=[dict(op='restore_transcription',target_id=obj['id'],field='text_kk',value=value)]))

def module(number, page, box, marker, prompt, chinese, badge=None):
    obj=add(None,f'm{number:02}','module',page,box=box,module_number=number)
    add(obj,'number','module_number',page,marker)
    if badge:
        src, label=badge
        add(obj,'badge','module_badge',page,src,zh=label,badge_origin='printed',scope_ids=[obj['id']])
    add(obj,'instruction','text',page,prompt,zh=chinese)
    return obj

def dot(key, slot):
    return {'id':key,'slot':slot}

def arrow(start, direction, label):
    return {'from':start,'direction':direction,'label':label}

def diagram(parent, key, box, ids, kk, zh, relation, page=29):
    return add(parent,key,'informative_image',page,ids,box=box,zh=zh,crop=True,
               structured_description={'description_kk':kk,'relations':[relation]})

header=add(None,'heading','other',29,box=[30,55,665,150],role='lesson_header')
add(header,'number','text',29,'2 5',kk='88\nСАБАҚ',zh='第 88 课',role='lesson_number')
add(header,'title','text',29,'3 4',kk=title,zh='同向追及问题与运动图线',role='lesson_title')
add(header,'theme','text',29,'6',zh='自然变化。雪崩和滑坡',role='lesson_context')
intro=add(None,'orientation','other',29,box=[82,180,770,327],role='lesson_orientation')
add(intro,'badge','badge',29,'9',zh='巩固练习',badge_origin='printed',scope_ids=[intro['id']])
add(intro,'objective','text',29,'12 14 15',zh='你将用列方程的方法解答同向追及问题。')
add(intro,'topic-terms','text',29,'7 8 10 11 13',kk='ҚУЫП ЖЕТУ ҚОЗҒАЛЫСЫНА БЕРІЛГЕН ЕСЕПТЕРДІ ШЫҒАРУДЫҢ АЛГЕБРАЛЫҚ ТӘСІЛІ, ҚОЗҒАЛЫС ГРАФИГІ',
    zh='追及问题的代数解法、运动图线')

m=module(1,29,[85,350,881,697],'a0','16','按指定顺序填入各答案所对应的字母，读出这个词。')
for i,(src,letter_src,equation,letter) in enumerate([
    ('17','20','420 000 : 700','к'),('18','21','140 000 : 700','ө'),('19','22','6 300 000 : 700','н'),
    ('23','26','350 000 : 700','ш'),('24','27','21 000 : 700','к'),('25','','560 000 : 700','і')]):
    col,x=i%3,[138,380,622][i%3]
    y=[458,528][i//3]
    group=add(m,f'pair-{i+1}','other',29,box=[x,y,x+199,y+65],role='expression_letter_pair')
    add(group,'formula','formula',29,src,kk=equation)
    character=add(group,'letter','text',29,letter_src,box=[719,562,730,586] if not letter_src else None,kk=letter,role='paired_letter')
    if not letter_src:
        suggestion(character,[],letter,'Оң жақ төменгі ұяшықта «і» әрпі басылған, OCR-де жоқ.')
xs=[87,217,349,482,613,745,877]
ys=[603,648,694]
tab=add(m,'answer-table','table',29,box=[xs[0],ys[0],xs[-1],ys[-1]],crop=True,row_count=2,column_count=6,header_rows=[0],cells=[])
for r in range(2):
    for c,src in enumerate(['30','32','33','34','35','36']):
        cell=dict(id=f"{tab['id']}:r{r+1}c{c+1}",parent_id=tab['id'],row=r,column=c,
                  rowspan=1,colspan=1,header=r==0,text_kk=fixed[29][src]['text'] if r==0 else '',
                  page_refs=[location(29,[xs[c],ys[r],xs[c+1],ys[r+1]])],review_status=status)
        if r==0:
            cell['ocr_evidence']=[dict(line_id=src, raw=raw[29].get(src,{}).get('text'),
                                       existing_corrected=fixed[29][src]['text'])]
        else:
            cell['empty']=True
        tab['cells'].append(cell)

m=module(2,29,[85,722,881,966],'39','38 40','看两个物体的运动示意图，说明各图表示什么，并解释公式。')
for key,box,ids,formula_ids,arrows,flag,formula,kk,zh,formula_zh in [
    ('same-direction',[102,846,333,906],'a1 a2','43','left right left right','right',
     'vжақ. = v₁ − v₂','Екі жебе де оңға; v₁ артқы, v₂ алдыңғы денеге тиесілі. Ту оң жақта.',
     '两个物体均向右。v₁ 属于后方，v₂ 属于前方。旗标位于右侧。','接近速度 = v₁ − v₂'),
    ('toward-each-other',[384,845,614,906],'41','45','left right right left','middle',
     'vжақ. = v₁ + v₂','Сол жақ дене оңға, оң жақ дене солға бағытталған. Ту екеуінің арасында.',
     '左侧物体向右，右侧物体向左。旗标在两者中间。','接近速度 = v₁ + v₂'),
    ('apart',[655,845,864,906],'42','46','middle left middle right',None,
     'vқаш. = v₁ + v₂','Екі дене ортақ бастапқы нүктеден қарама-қарсы жақтарға қозғалады.',
     '两物体从同一点背向出发，v₁ 向左，v₂ 向右。','远离速度 = v₁ + v₂'),
]:
    source1,dir1,source2,dir2=arrows.split()
    if key=='same-direction':
        source2='middle'
    relation=dict(kind='motion_diagram',points=[dot('left',0),dot('middle',1),dot('right',2)],
                  arrows=[arrow(source1,dir1,'v₁'),arrow(source2,dir2,'v₂')],formula=formula)
    if flag:
        relation['flag_at']=flag
    diagram(m,key,box,ids,kk,zh,relation)
    symbol='жақ.' if key!='apart' else 'қаш.'
    add(m,f'{key}-formula','formula',29,formula_ids,kk=formula,zh=formula_zh,crop=True,
        subscripts=[{'base':'v','subscript_kk':symbol},{'base':'v','subscript_kk':'1'},{'base':'v','subscript_kk':'2'}])

m=module(3,29,[85,994,881,1307],'47','48','解题。')
add(m,'problem','text',29,'49 51 52 54 55',
    zh='两位摩托车手相距 50 千米。第一位每小时行 40 千米，第二位每小时行 50 千米。多久后第二位会追上第一位？')
diagram(m,'motorcycles',[548,1125,872,1234],'50 53',
        'Екі жебе оңға бағытталған. Сол жақта v₂ = 50 км/сағ, ал оң жақта v₁ = 40 км/сағ. Аралық 50 км, ту оң жақта.',
        '两箭头均向右。左侧是 v₂ = 50 千米/时，右侧是 v₁ = 40 千米/时。间距 50 千米，旗标在右侧。',
        dict(kind='motion_diagram',points=[dot('rear',0),dot('front',1),dot('destination',2)],
             arrows=[arrow('rear','right','v₂ = 50 км/сағ'),arrow('front','right','v₁ = 40 км/сағ')],
             distances=[dict(start='rear',end='front',label='50 км')],flag_at='destination'))
m=module(4,30,[112,154,911,533],'a0','3','列方程解题。',('2','独立练习'))
add(m,'problem','text',30,'4 5 6 7',
    zh='小汽车和公交车相距 60 千米，速度分别为 70 千米/时和 50 千米/时。如果两车保持这两个速度，小汽车几小时后追上公交车？')
diagram(m,'vehicles',[236,412,802,510],'8 9 10 11',
        'Автокөлік сол жақта, автобус оң жақта. Жебелер оңға бағытталған: автокөліктің жылдамдығы v₁ = 70 км/сағ, автобустың жылдамдығы v₂ = 50 км/сағ. Бастапқы аралық 60 км, t белгісіз.',
        '小汽车在左，公交车在右，均向右行驶。小汽车 v₁ = 70 千米/时，公交车 v₂ = 50 千米/时。起点相距 60 千米，时间未知。',
        dict(kind='motion_diagram',points=[{**dot('car',0),'label':'Автокөлік'},{**dot('bus',1),'label':'Автобус'}],
             arrows=[arrow('car','right','v₁ = 70 км/сағ'),arrow('bus','right','v₂ = 50 км/сағ')],
             distances=[dict(start='car',end='bus',label='S = 60 км')],unknown_label='t = ? сағ'),page=30)
m=module(5,30,[112,548,910,1041],'a1','14','完成任务。',('13','小组合作'))
problem=add(m,'problem','text',30,'15 16 17 18 19 20 21 23 26 29 31',
    zh='观察阿尔曼（蓝线）和阿丽娅（红线）的运动图线。求阿尔曼最初 2 分钟的速度。接下来的 3 分钟他在做什么？阿丽娅晚出发了多久？求阿丽娅最初 2 分钟的速度。为什么第 7 到第 12 分钟之间，运动图线与时间轴平行？再根据图线想一些问题。')
problem['page_refs']=[location(30,[156,668,708,859]),location(30,[156,859,490,1021])]
for s in suggestions:
    if s['object_id']==problem['id']:
        s['page_refs']=problem['page_refs']
diagram(m,'distance-time',[506,881,904,1023],'22 24 25 27 28 30 32 33',
        'Көлденең ось t (мин), тік ось S (м). Көк сызық Армандікі, қызыл сызық Әлиянікі. Сынық сызықтар 7 минуттан кейін бірдей нүктелер арқылы өтеді.',
        '横轴为时间 t（分钟），纵轴为 S（米）。蓝线属于阿尔曼，红线属于阿丽娅。两条折线从第 7 分钟起经过相同的点。',
        dict(kind='coordinate_graph',x_label='t (мин)',y_label='S (м)',x_ticks=[0,2,4,6,8,10,12,14,16],
             y_ticks=[0,100,200,300,400,500],series=[
                 {'name':'Арман','color':'#27477a','vertices':[[0,0],[2,300],[5,300],[7,500],[12,500],[17,0]]},
                 {'name':'Әлия','color':'#ae3e35','vertices':[[5,0],[7,500],[12,500],[17,0]]}]),page=30)
m=module(6,30,[111,1051,911,1309],'a2','35','解题。',('34','日常生活中的数学'))
add(m,'problem','text',30,'36 37 38 39',
    zh='温室种了 900 株花，630 株是紫菀，其余是郁金香。紫菀每畦种 35 株，郁金香每畦种 30 株。一共种了多少畦？')
m=module(7,31,[85,169,879,487],'a0','2','解题。')
add(m,'problem','text',31,'3 4 6 8 10 11',
    zh='水池的两根管同时打开。一根每小时注入 50 立方米，另一根每小时排出 40 立方米。开管时池里没有水。多久后水池里有 270 立方米水？')
m=module(8,31,[85,496,880,758],'a1','13','想一想，再回答。',('12','你来探究'))
add(m,'problem','text',31,'14 15 16 17',
    zh='橡树和杨树上一共有 26 只鸟。杨树上飞走 6 只，橡树上又有 4 只飞到杨树上。这时两棵树上的鸟一样多。原来每棵树上各有多少只鸟？')
m=module(9,31,[85,773,883,1210],'a2','19','完成任务。',('18','家庭作业'))
add(m,'problem','text',31,'20 21 22 23 24 25 26 28 29',
    zh='两名滑雪者同时在积雪覆盖的平地上向同一方向出发，起初相距 700 米。后面的人每分钟滑 200 米，前面的人每分钟滑 150 米。后面的人多久能追上前面的人？')
add(None,'closing','other',31,'30 31 32',kk='ОЙЛАСТЫР\nОЙЫҢМЕН БӨЛІС\nҰСЫН',zh='想一想\n分享你的想法\n提出建议',role='lesson_closing_prompt')
boundary=dict(contents={'pdf_page':159,'printed_page':'159','lesson_start':29,'next_lesson_start':32},
              previous_lesson_end={'pdf_page':28,'number':87,'last_module_number':9},
              start_heading={'pdf_page':29,'number':88,'title_kk':title},
              continuation_headers=[{'pdf_page':30,'number':88,'title_kk':title},{'pdf_page':31,'theme_kk':theme}],
              end_of_lesson={'pdf_page':31,'module_number':9}, next_lesson={'pdf_page':32,'number':89,'title_kk':'Бір бағыттағы қалып қою қозғалысы'})
pages=[dict(id=f'{book_id}:p{p:03}',pdf_page=p,printed_page=str(p),width=992,height=1418,scan_asset_id=f'{book_id}:p{p:03}:scan',
            scan_path=manifest[f'{p}-scan.png']['path'],scan_sha256=manifest[f'{p}-scan.png']['sha256']) for p in page_numbers]
data=dict(data_version='2026-11-26-experiment-redraw-1',review_status=status,
          book=dict(id=book_id,title_kk='Математика',grade=4,part=3,year=2023,language='kk-Cyrl',publisher_kk='АЛМАТЫКІТАП БАСПАСЫ'),
          source=dict(repository='yeyidi7570/01',original_pdf=manifest['original_pdf'],content_authority='original_scan',
                      page_sources={k:v for k,v in manifest.items() if k[:2] in {'29','30','31'}}),
          coordinate_system=dict(origin='top_left',unit='pixel'),
          schema_rules=dict(instructional_note_badges=['ЕСІҢДЕ САҚТА!','ОСЫЛАЙ ТАЛДА!','КАЛЬКУЛЯТОР'],teaching_link_types=['supports','uses_as_material']),
          lesson=dict(id=lesson_id,number=88,title_kk=title,theme_kk=theme,review_status=status,
                      pdf_page_range=[29,31],printed_page_range=['29','31'],boundary_evidence=boundary,
                      units=units,content_order=[u['id'] for u in units],teaching_links=[]),
          pages=pages,crop_assets=crops,ocr_suggestions=suggestions)

def dump(path, payload, freeze=False):
    with (ROOT/path).open('x' if freeze else 'w',encoding='utf-8') as f:
        f.write(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')

dump('content.v1.json',data,True)
dump('translations.v1.json',{'title':'同向追及问题与运动图线','theme':'自然变化。雪崩和滑坡','objects':translations},True)
dump('scans.json',{p['scan_asset_id']:f'source/{p["pdf_page"]}-scan.png' for p in pages})
