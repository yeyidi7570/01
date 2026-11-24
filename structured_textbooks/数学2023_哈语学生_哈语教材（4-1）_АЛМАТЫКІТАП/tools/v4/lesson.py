"""Assemble the scan-checked transcription and provenance for Lesson 1."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import sys

source = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/tmp/lesson1')
out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('/workspace')
here = Path(__file__).parent
repo = 'yeyidi7570/01'
tree = json.loads((source/'tree.json').read_text())
paths = json.loads((source/'sources.json').read_text())
original_path = next(x['path'] for x in tree['tree'] if x['path'].startswith('wiki-data/数学2023_哈语学生') and '（4-1）' in x['path'] and x['path'].endswith('.pdf'))
book = 'math-2023-grade4-part1'
lesson = book + ':lesson-001'
title = '3-сыныпта өткенді қайталау'
status = 'pending_review'
pages = {}
raw, proof = {}, {}
units, auxiliary, proposals, assets = [], {}, [], {}

def read(name):
    return json.loads((source/name).read_text())

wiki = read('wiki.json')
for p in range(7, 11):
    scanned = source/f'scan{p}.png'
    w = wiki['pages'][p-1]
    r, f = read(f'raw{p}.json'), read(f'proof{p}.json')
    raw[p], proof[p] = ({line['id']:line for line in e['lines']} for e in (r, f))
    pages[p] = dict(id=f'{book}:p{p:03}', pdf_page=p, printed_page=str(p), width=r['width'], height=r['height'],
                    scan_asset_id=f'{book}:p{p:03}:scan', scan_sha256=hashlib.sha256(scanned.read_bytes()).hexdigest(),
                    scan_path=paths[scanned.name], raw_ocr_path=paths[f'raw{p}.json'],
                    corrected_ocr_path=paths[f'proof{p}.json'], layout_path=paths[f'layout{p}.json'],
                    pdf_dimensions_pt=[w['pdf_width_pt'], w['pdf_height_pt']],
                    raw_ocr_lines=r['lines'], existing_corrected_ocr_lines=f['lines'],
                    previous_layout=read(f'layout{p}.json'), review_status=status)

def loc(p,b):
    return dict(pdf_page=p, printed_page=str(p), bbox=b, scan_asset_id=pages[p]['scan_asset_id'])

def ids(spec):
    result=[]
    for part in spec.split():
        if '-' in part:
            a,b=map(int,part.split('-'))
            result.extend(str(i) for i in range(a,b+1))
        else:
            result.append(part)
    return result

def ocr(p, spec):
    return [dict(line_id=i, wiki_line_id=f'{book}:p{p:03}:l{i}', raw=raw[p].get(i,{}).get('text'),
                 existing_corrected=proof[p].get(i,{}).get('text'))
            for i in ids(spec)]

def entity(suffix,t,p,b,kk=None,zh=None,lines='',**fields):
    oid = lesson+':'+suffix
    d = dict(id=oid, type=t, review_status=status, page_refs=[loc(p,box) for box in (b if isinstance(b[0],list) else [b])], **fields)
    if kk is not None: d['text_kk']=kk
    if zh is not None: auxiliary[oid]=zh
    if lines: d['ocr_evidence']=ocr(p,lines)
    return d

def unit(suffix,t,p,b,kk=None,zh=None,lines='',**fields):
    d=entity(suffix,t,p,b,kk,zh,lines,parent_id=lesson,elements=[],content_order=[],**fields)
    units.append(d)
    return d

def child(parent,key,t,b,kk=None,zh=None,lines='',**fields):
    p=parent['page_refs'][0]['pdf_page']
    suffix=parent['id'].removeprefix(lesson+':')+':'+key
    d=entity(suffix,t,p,b,kk,zh,lines,parent_id=parent['id'],**fields)
    parent['elements'].append(d)
    parent['content_order'].append(d['id'])
    return d

def module(n,p,b,num=None,lines=''):
    d=unit(f'm{n:02}','module',p,b,module_number=n)
    if num: child(d,'number','module_number',num,str(n),lines=lines)
    return d

def text(u,key,b,kk,zh,lines):
    return child(u,key,'text',b,kk,zh,lines)

def badge(u,b,kk,zh,lines,scope=None):
    d=child(u,'badge','module_badge',b,kk,zh,lines,badge_origin='printed',scope_ids=scope or [u['id']],capsule_order=1,label_order=1)
    u.setdefault('module_badge',[]).append(d['id'])
    return d

def crop(d):
    a=d['id']+':crop'
    d['crop_asset_id']=a
    assets[a]=d['page_refs'][0]

def suggestion(d,category,spec,reason,zh,value=None,proposed_changes=None):
    p=d['page_refs'][0]['pdf_page']
    evidence=ocr(p,spec)
    if proposed_changes is None:
        if d['type']=='table':
            proposed_changes=[dict(op='restore_table',target_id=d['id'],field='cells',value=value)] if category=='table_structure' else [
                dict(op='restore_table_cell_text',target_id=c['cell_id'],field='text_kk',value=c['text_kk']) for c in value]
        elif category=='image_relationship':
            proposed_changes=[dict(op='restore_visual_relationship',target_id=d['id'],field='structured_description',value=value)]
        elif category=='formula_structure':
            proposed_changes=[dict(op='restore_formula_layout',target_id=d['id'],field='vertical' if 'vertical' in d else 'printed_lines',value=value)]
        else:
            proposed_changes=[dict(op='restore_transcription',target_id=d['id'],field='text_kk',value=value)]
    proposal=dict(id=f"{d['id']}:suggestion-{len(d.get('ocr_suggestion_ids',[]))+1}", object_id=d['id'],category=category,
                  review_status=status,page_refs=d['page_refs'], source_lines=evidence, reason_kk=reason, baseline='repository_raw_ocr',
                  suggested_value=value, evidence_regions=[loc(p,proof[p].get(l['line_id'],raw[p].get(l['line_id']))['bbox']) for l in evidence])
    if proposed_changes: proposal['proposed_changes']=proposed_changes
    proposals.append(proposal)
    d.setdefault('ocr_suggestion_ids',[]).append(proposal['id'])
    auxiliary[proposal['id']]=zh

wrap=('Баспа жолының тасымалы біріктірілді.','合并印刷断词，保留段落和原词。')
space=('Беттелімдегі жол үзілістері мен аралықтар оқуға ыңғайланып реттелді.','重整排版换行和空格。')
glyph=('Таңбалар сканмен салыстырылды.','依据扫描校对字符。')
grid=('Скан бойынша жолдар, бағандар, бос ұяшықтар және математикалық жазылу қалпына келтірілді.','依据扫描恢复二维位置、空位和数学排版。')
miss=('Нөмір сканда бар, бастапқы OCR оны танымаған.','原图有编号，原始 OCR 漏识别。')
def s(d,category,spec,why,value=None,patch=None):
    suggestion(d,category,spec,*why,d.get('text_kk') if value is None else value,patch)

header=unit('header','other',7,[26,53,535,148],role='lesson_header')
child(header,'number','text',[28,53,120,148],'1\nСАБАҚ','第 1 课','1 5',role='lesson_number')
child(header,'title','text',[140,73,535,108],title,'复习三年级学过的内容','2',role='lesson_title')
child(header,'theme','text',[141,114,352,141],'Қазақстанның аумағы','哈萨克斯坦的国土面积','3',role='lesson_context')
intro=unit('intro','other',7,[84,183,751,298],role='lesson_objective')
intro_badge=child(intro,'label','text',[310,184,480,212],'ҚАЙТАЛАУ','复习','9',role='lesson_type_badge')
s(intro_badge,'ocr_character','9',glyph)
text(intro,'objective',[154,214,704,278],'Сандар мен шамалар, олармен есептеулер орындау туралы білетініңді қайталайсың.','你将复习有关数、量以及如何用它们进行计算的知识。','10 11')
cover=unit('cover-words','other',7,[780,101,885,186],'САНДАРДЫ ЖӘНЕ ШАМАЛАРДЫ ЕСЕПТЕУ','数与量的计算','4 6-8',role='illustration_caption')
s(cover,'ocr_character','6 8',glyph)
m1=module(1,7,[85,329,879,983],[103,334,163,393],'a0')
s(m1['elements'][0],'ocr_character','a0',miss)
text(m1,'prompt',[177,348,834,380],'Мәтінді оқы. Сандарды көшіріп, оларды өсу ретімен жаз.','阅读短文。抄写数字，并按从小到大的顺序排列。','12')
d=text(m1,'reading-a',[128,421,835,577],
 'Әлия энциклопедиядан Қазақстан аумағы батысында Еділ өзенінің төменгі ағысынан, шығысында Алтай тауларының етегіне дейін 3 000 км-ге, ал солтүстігінде Батыс Сібір жазығынан оңтүстіктегі Қызылқұм шөліне дейін 1 700 км-ге созылып жатқанын оқыды.',
 '阿莉娅从百科全书中读到，哈萨克斯坦的国土西起伏尔加河下游，东至阿尔泰山麓，延伸 3 000 千米；北起西西伯利亚平原，南至克孜勒库姆沙漠，延伸 1 700 千米。','13-18')
s(d,'ocr_linebreak','15 16',wrap)
s(d,'ocr_linebreak','14',space)
child(m1,'divider','other',[453,596,509,617],'* * *',lines='19',role='paragraph_separator')
d=text(m1,'reading-b',[129,646,839,954],
 'Арман интернеттен Қазақстан қалаларында тұратын халық саны туралы мәлімет білді:\n• 300 000-нан 400 000-ға дейінгі тұрғындар саны – Семей, Павлодар, Тараз және Өскеменде;\n• 200 000-нан 280 000-ға дейінгі тұрғындар саны – Қостанай, Қызылорда, Атырау және Петропавлда;\n• 110 000-нан 160 000-ға дейінгі тұрғындар саны – Екібастұз, Көкшетау, Рудный және Талдықорғанда.',
 '阿尔曼在网上了解到哈萨克斯坦各城市的人口资料：\n• 人口在 300 000 到 400 000 之间：塞梅伊、巴甫洛达尔、塔拉兹、厄斯克门；\n• 人口在 200 000 到 280 000 之间：科斯塔奈、克孜勒奥尔达、阿特劳、彼得罗巴甫尔；\n• 人口在 110 000 到 160 000 之间：埃基巴斯图兹、科克舍套、鲁德内、塔尔迪库尔干。','21-28')
s(d,'ocr_character','23 25',glyph)
s(d,'reading_order','21-28',('Үш тармақ пен жалғас жолдары скандағы тізім бойынша топталды.','恢复扫描中的三条列表及各条续行。'))
m2=module(2,7,[85,995,879,1302],[103,1028,162,1087],'a1')
s(m2['elements'][0],'ocr_character','a1',miss)
badge(m2,[388,997,578,1027],'ЖҰПТЫҚ ЖҰМЫС','两人合作','29')
text(m2,'prompt',[180,1039,688,1074],'Дұрыс жауапты таңда. Өз пікіріңді дәлелде.','选择正确答案。说明你的理由。','30')
d=text(m2,'problem',[129,1107,836,1234],
 'Картадағы масштаб бойынша 1 см – аймақтың 4 километріне сәйкес келеді.\nКартадағы екі қаланың арақашықтығы 8 см-ге тең. Осы қалалардың арақашықтығы қанша километр болады?',
 '按地图比例尺，图上 1 厘米对应实际 4 千米。\n地图上两座城市相距 8 厘米。这两座城市的实际距离是多少千米？','31-34')
s(d,'ocr_linebreak','33 34',wrap)
d=child(m2,'choices','text',[131,1249,766,1285],'а) 2 км    ә) 8 км    б) 16 км    в) 32 км','а) 2 千米　ә) 8 千米　б) 16 千米　в) 32 千米','35-38',
        choices=[dict(label=k,value=v,unit='км') for k,v in zip('аәбв',[2,8,16,32])])
s(d,'ocr_character','36 37',glyph)
def running(p,b,kk,zh,lines):
    return unit(f'header-p{p}','other',p,b,kk,zh,lines,role='running_header')
running(8,[110,84,477,113],'1-сабақ • '+title,'第 1 课 · 复习三年级学过的内容','2')
m3=module(3,8,[112,155,907,484],[132,186,192,246],'a0')
s(m3['elements'][0],'ocr_character','a0',miss)
badge(m3,[417,155,605,185],'ТОПТЫҚ ЖҰМЫС','小组合作','3')
d=text(m3,'prompt',[202,189,888,274],
 'Алдымен массаның, содан кейін уақыттың өлшем бірліктерін өсу ретімен жаз. Екі теңсіздіктен құрастыр. Шамалардың мәнін қалай салыстыру керек екенін түсіндір.',
 '先把质量的计量单位按从小到大的顺序写下来，再用同样的顺序写时间的计量单位。各组成两个不等式。说明怎样比较这些量的数值。','4-6')
s(d,'ocr_linebreak','4-6',wrap)
values=[['9 ц 8 кг','2 жыл','205 кг'],['2 ц 10 кг','658 жыл','810 күн'],
        ['6 ц 1 кг','7 ғасыр','98 кг'],['610 кг','42 жыл','345 күн']]
d=child(m3,'quantities','text',[190,312,802,451],'\n'.join('    '.join(r) for r in values),
        '9 公担 8 千克　｜　2 年　｜　205 千克\n2 公担 10 千克　｜　658 年　｜　810 天\n6 公担 1 千克　｜　7 世纪　｜　98 千克\n610 千克　｜　42 年　｜　345 天','7-18',printed_grid_kk=values,role='quantity_bank')
s(d,'ocr_character','15',glyph)
s(d,'ocr_linebreak','7 10 13 17',space)
m4=module(4,8,[112,507,908,1305],[132,525,192,582],'a1')
s(m4['elements'][0],'ocr_character','a1',miss)
text(m4,'prompt',[203,525,863,589],'Шамалармен амалдардың қалай орындалатынын есіңе түсір және есепте.',
 '回忆如何对带单位的量进行运算，然后计算。','19 20')
def example(key,b):
    return child(m4,key,'example',b,elements=[],content_order=[],role='worked_demonstration')
def formula(u,key,b,kk,lines,**fields):
    d=child(u,key,'formula',b,kk,lines=lines,**fields)
    if 'vertical' in fields: crop(d)
    return d
def vertical(u,key,b,kk,lines,upper,lower,op,result,**kw):
    d=formula(u,key,b,kk,lines,vertical=dict(upper=upper,lower=lower,operator=op,result=result,**kw),
              notation='vertical')
    s(d,'formula_structure',lines,grid,d['vertical'])
    return d
e=example('ex-conversion',[129,615,906,780])
d=text(e,'steps',[134,620,423,778],
 '1. Ірірек бірліктерді ұсақ бірліктермен ауыстырамын.\n2. Амалдарды орындаймын.\n3. Ұсақ бірліктерді ірірек бірліктермен ауыстырамын.',
 '1. 我把较大的单位换成较小的单位。\n2. 我进行运算。\n3. 我把较小的单位换成较大的单位。','21 24 27 31 34')
s(d,'ocr_linebreak','21 24 31 34',wrap)
vertical(e,'length',[429,639,639,765],'7 м 48 см − 1 м 69 см\n   748 см\n−  169 см\n─────────\n   579 см = 5 м 79 см','22 25 a2 28 32',
 '748 см','169 см','−','579 см',expression_kk='7 м 48 см − 1 м 69 см', equivalence_kk='579 см = 5 м 79 см')
vertical(e,'time',[653,638,905,767],'2 сағ 40 мин + 55 мин\n   160 мин\n+   55 мин\n──────────\n   215 мин = 3 сағ 35 мин','23 26 29 30 33',
 '160 мин','55 мин','+','215 мин',expression_kk='2 сағ 40 мин + 55 мин',equivalence_kk='215 мин = 3 сағ 35 мин')
e=example('ex-carry',[175,806,860,966])
d=vertical(e,'sum',[180,821,445,923],'   45 мин\n+  23 мин\n   68 мин = 1 сағ 8 мин','36 37 39 42',
 '45 мин','23 мин','+','68 мин',result_rule_printed=False,equivalence_kk='68 мин = 1 сағ 8 мин',highlight=dict(value='6',position='first_digit_of_68'))
exp=text(e,'explanation',[651,811,852,966],
 '60 минут 1 сағатқа тең болғандықтан, 60 минутты ірірек өлшем бірлік – 1 сағатқа ауыстырамын.',
 '因为 60 分钟等于 1 小时，我把 60 分钟换成较大的计量单位，也就是 1 小时。','35 38 40 43-45')
im=child(e,'arrow','informative_image',[216,925,628,958],zh='绿色箭头从右边的换算说明指向左边算式结果中的 68 分钟，数字 6 在原图中用绿色标出。',
 structured_description=dict(description_kk='Жасыл жебе оң жақтағы түсіндірмеден сол жақтағы 68 мин нәтижесіне бағытталады. 68 санының 6 цифры жасыл түсті.',
   relations=[dict(kind='arrow',direction='right_to_left',from_id=exp['id'],to_id=d['id'],target_kk='68 мин',highlighted_digit='6')]))
crop(im)
s(im,'image_relationship','35 42',grid,im['structured_description'])
e=example('ex-borrow',[118,1006,878,1170])
before=vertical(e,'first-layout',[119,1045,292,1151],'  1 сағ 16 мин\n−       45 мин\n─────────────\n           мин','49 a3 53 58','1 сағ 16 мин','45 мин','−',None,result_blank_unit='мин',highlight=dict(value='16',position='upper_minutes'))
exp=text(e,'explanation',[333,1011,541,1107],'Минут жетпейді. 1 сағатты ауыстырамын.','分钟数不够减。我把 1 小时换成分钟。','47 50 54')
s(exp,'ocr_linebreak','50 54',wrap)
d=formula(e,'equivalence',[339,1108,538,1167],'60 мин + 16 мин =\n= 76 мин','57 61',
          notation='continued_equation',printed_lines=['60 мин + 16 мин =','= 76 мин'])
s(d,'formula_structure','57 61',('Қатар соңындағы және келесі қатар басындағы теңдік белгілері сканда екеуі де бар.','原图上一行行尾与下一行行首均有等号，保留原版排法。'),d['printed_lines'])
mid=vertical(e,'transfer-layout',[591,1044,758,1151],'  1 сағ 16 мин\n−       45 мин\n─────────────\n           мин','51 a4 55 59','1 сағ 16 мин','45 мин','−',None,result_blank_unit='мин')
im=child(e,'arrow','informative_image',[619,1022,708,1048],'60','绿色弯箭头从小时所在位置指向上方的 60，表示把小时换算成分钟。','48',
 structured_description=dict(description_kk='Жасыл иілген жебе сағат тұрған жақтан жоғарыдағы 60 санына бағытталған. Түсіндірме бойынша 1 сағат минутқа ауыстырылады.',
    relations=[dict(kind='curved_arrow',direction='left_to_right',from_id=mid['id'],from_anchor='upper_hours_position',target_label='60',explained_by_id=exp['id'],interpreted_conversion=dict(from_value=1,from_unit='сағ',to_value=60,to_unit='мин'))]))
crop(im)
s(im,'image_relationship','48',grid,im['structured_description'])
vertical(e,'minutes-layout',[771,1044,877,1151],'   76 мин\n−  45 мин\n─────────\n   31 мин','52 a5 56 60','76 мин','45 мин','−','31 мин',highlight=dict(value='76',position='upper_minutes'))
for i,(b,kk,line) in enumerate([
 ([148,1219,396,1248],'9 м 34 см − 4 м 52 см','62'),([595,1219,800,1250],'3 ц 7 кг + 5 ц 16 кг','63'),
 ([148,1251,400,1281],'4 сағ 34 мин + 67 мин','64'),([595,1250,852,1283],'6 сағ 20 мин − 75 мин','65')],1):
    formula(m4,f'expression-{i}',b,kk,line,notation='linear')
running(9,[670,75,887,108],'Қазақстанның аумағы','哈萨克斯坦的国土面积','1')
m5=module(5,9,[[84,154,880,764],[84,821,719,916],[84,974,720,1098],[84,1154,721,1307]])
bid=badge(m5,[344,154,622,185],'ШЫҒАРМАШЫЛЫҚ ЖҰМЫС','创造性任务','2',[m5['id']+':part-a'])
def subpart(key,b,nb,label,line):
    d=child(m5,key,'subtask',b,elements=[],content_order=[],subtask_label=label)
    nd=child(d,'label','subtask_number',nb,label,lines=line)
    s(nd,'ocr_character',line,('Скандағы қазақша тапсырма белгісі бас әріппен, кирилл жазуымен берілді.','按原图和哈语子题排版规则使用大写西里尔字母。'))
    return d
a=subpart('part-a',[85,184,879,764],[104,185,163,245],'5А','3')
text(a,'prompt',[173,186,841,309],
     'Қазақстан мектептерінде бір сабақ 40 минутқа созылады. 4-сыныптың сабақ кестесіне қара. Балалар аптасына неше сағат математика мен қазақ тілін оқитындықтарын анықта. Кесте бойынша өзің сұрақтар мен есептер құрастыр.',
     '哈萨克斯坦的学校每节课为 40 分钟。看四年级课表。确定孩子们每周上多少小时的数学课和哈萨克语课。根据课表自己编写问题和应用题。','4-7')
cols=[86,130,263,386,509,633,753,878]
rows=[325,402,461,527,586,651,711,764]
table_values=[
 [('', '', ''),('Дс','周一','10'),('Сс','周二','11'),('Ср','周三','12'),('Бс','周四','13'),('Жм','周五','14'),('Қоңырау\nуақыты','上下课铃时间','9 15')],
 [('1','','19'),('Дүниет.','认识世界','16'),('Қаз. тілі','哈萨克语','17'),('Матем.','数学','20'),('Қаз. тілі','哈萨克语','21'),('Қаз. тілі','哈萨克语','22'),('8³⁰ – 9¹⁰','','23 24')],
 [('2','','27'),('Матем.','数学','28'),('Әдебиеттік оқу','文学阅读','25 32','Әдебиет-\nтік оқу'),('Әдебиеттік оқу','文学阅读','26 33','Әдебиет-\nтік оқу'),('Матем.','数学','29'),('Музыка','音乐','30'),('9²⁰ – 10⁰⁰','','31')],
 [('3','','34'),('АКТ','信息与通信技术','35'),('Матем.','数学','36'),('Ағылш.тілі','英语','37'),('Жарат.','自然科学','38'),('Матем.','数学','39'),('10²⁰ – 11⁰⁰','','40')],
 [('4','','45'),('Қаз. тілі','哈萨克语','46'),('Орыс тілі','俄语','47'),('Өзін-өзі т.','自我认识','48'),('Әдебиеттік оқу','文学阅读','43 50','Әдебиет-\nтік оқу'),('Көркем\nеңбек','美术与手工劳动','44 51'),('11²⁰ – 12⁰⁰','','49')],
 [('5','','52'),('Ағылш. тілі','英语','53'),('Жарат.','自然科学','54'),('Дене ш.','体育','55'),('Орыс тілі','俄语','56'),('Дене ш.','体育','57'),('12¹⁰ – 12⁵⁰','','58')],
 [('6','','60'),('Дене ш.','体育','61'),('','',''),('','',''),('','',''),('','',''),('13⁰⁰ – 13⁴⁰','','62')]]
table=child(a,'schedule','table',[85,324,880,765],row_count=7,column_count=7,header_rows=[0],cells=[])
crop(table)
intervals=[('08:30','09:10'),('09:20','10:00'),('10:20','11:00'),('11:20','12:00'),('12:10','12:50'),('13:00','13:40')]
for r,row in enumerate(table_values):
    for c,(val,zh,line,*printed) in enumerate(row):
        cell=dict(id=f"{table['id']}:r{r+1}c{c+1}",row=r,column=c,rowspan=1,colspan=1,header=r==0,empty=not val,text_kk=val,
                  page_refs=[loc(9,[cols[c],rows[r],cols[c+1],rows[r+1]])])
        if zh: auxiliary[cell['id']]=zh
        if line: cell['ocr_evidence']=ocr(9,line)
        if printed: cell['printed_text_kk']=printed[0]
        if r and c==6:
            start,end=intervals[r-1]
            cell['time_interval']=dict(start=start,end=end,minute_style='underlined_superscript')
        table['cells'].append(cell)
s(table,'table_structure','9-62',grid,table['cells'])
s(table,'ocr_character','23 24 31 35 40 49 50 58 62',glyph,
  [{'cell_id':c['id'],'text_kk':c['text_kk']} for c in table['cells'] if c.get('time_interval') or c['text_kk']=='АКТ' or (c['row']==4 and c['column']==4)])
s(table,'ocr_linebreak','25 26 32 33 43 50',wrap,
  [{'cell_id':c['id'],'text_kk':c['text_kk']} for c in table['cells'] if 'printed_text_kk' in c])
ae=subpart('part-ae',[85,821,719,916],[103,837,163,897],'5Ә','64')
p_ae=text(ae,'prompt',[173,838,696,901],'Берілген сабақ кестесі бойынша дүйсенбі күні үзіліс қанша уақытқа созылатынын есепте.',
 '根据给出的课表，计算周一课间休息有多长时间。','65 66')
b=subpart('part-b',[85,975,720,1097],[103,992,163,1051],'5Б','67')
p_b=text(b,'prompt',[174,991,722,1078],'Сабағыңның басталатын және аяқталатын уақытын анықта. Сен қанша уақытыңды мектепте өткізесің?',
 '确定你开始上课和结束上课的时间。你在学校度过多长时间？','68-70')
s(p_b,'ocr_linebreak','68-70',wrap)
v=subpart('part-v',[85,1154,721,1307],[103,1170,163,1231],'5В','71')
p_v=text(v,'prompt',[173,1171,721,1286],
 'Мектепке баратын және қайтатын жолға кететін уақытыңды анықта. Күнделікті үйде қанша уақыт болмайтыныңды есепте. Алдыңғы тапсырманың деректерін пайдалан.',
 '确定上学和放学回家路上所花的时间。计算你每天有多长时间不在家。使用上一小题的数据。','72-75')
s(p_v,'ocr_linebreak','72-74',wrap)
running(10,[110,84,477,113],'1-сабақ • '+title,'第 1 课 · 复习三年级学过的内容','1')
m6=module(6,10,[112,168,909,368],[132,185,193,246],'a0')
s(m6['elements'][0],'ocr_character','a0',miss)
text(m6,'prompt',[203,196,767,231],'Өрнектерді амалдар бойынша жазып, мәнін тап.','按运算步骤分别写出算式，并求值。','2')
for i,(bbox,kk,line) in enumerate([
 ([193,274,409,305],'240 + (118 − 80) · 3','3'),([575,273,790,305],'980 − 137 · 6 + 125','4'),
 ([193,306,420,336],'358 + (412 − 299) · 4','5'),([575,306,803,336],'631 − (683 − 185) : 6','6')],1):
    d=formula(m6,f'expression-{i}',bbox,kk,line,notation='linear')
    if i in (2,3,4): s(d,'ocr_character',line,glyph)
m7=module(7,10,[112,406,909,626],[132,422,193,480],'a1')
s(m7['elements'][0],'ocr_character','a1',miss)
text(m7,'prompt',[203,433,482,470],'Тиімді тәсілмен есепте.','用简便的方法计算。','7')
for i,(bbox,kk,line) in enumerate([
 ([203,506,352,538],'(95 + 305) : 5','8'),([586,506,730,538],'(123 + 77) · 2','9'),
 ([203,539,418,571],'241 + 123 + 59 + 27','10'),([588,539,759,570],'448 + 60 + 242','11'),
 ([203,573,406,602],'(330 + 30 + 90) : 3','12'),([587,572,770,601],'(12 + 18 + 20) · 6','13')],1):
    d=formula(m7,f'expression-{i}',bbox,kk,line,notation='linear')
    if i in (2,6): s(d,'ocr_character',line,glyph)
m8=module(8,10,[112,660,909,943],[132,677,192,737],'a2')
s(m8['elements'][0],'ocr_character','a2',miss)
text(m8,'prompt',[202,687,369,723],'Есепті шығар.','解答应用题。','14')
text(m8,'problem',[156,763,865,925],
     'Қазақстан бойынша пойызбен саяхат жасайтын оқушыларға купе вагонға 9 билет үшін 108 000 теңге төленді. Егер купеге қарағанда плацкарт вагонның бір билеті 3 000 теңгеге арзан екені белгілі болса, онда плацкарт вагонмен саяхат жасайтын топ үшін 11 билетке қанша ақша төленеді?',
     '在哈萨克斯坦乘火车旅行的学生购买包厢卧铺车厢的 9 张票，共付 108 000 坚戈。如果开放式卧铺车厢每张票比包厢卧铺车厢便宜 3 000 坚戈，那么乘坐开放式卧铺车厢的一组学生买 11 张票需要支付多少钱？','15-19')
m9=module(9,10,[112,963,908,1234],[132,995,192,1055],'a3')
s(m9['elements'][0],'ocr_character','a3',miss)
badge(m9,[404,963,618,993],'СЕН ЗЕРТТЕУШІСІҢ','你是研究者','20')
text(m9,'prompt',[203,1006,512,1042],'Пайымдай отырып шығар.','通过推理来解题。','21')
d=text(m9,'problem',[155,1077,866,1234],
 'Отбасында үш ағайынды бала бар. Олардан жастары қаншада екенін сұрағанда, үлкені былай деді: «Үшеуіміздің жасымызды қосқанда 27 шығады. Менің жасыма Арманның жасын қосқанда 22, ал Бауыржан мен Арманның жасын қосқанда 15 жас болады». Ағайындылардың әрқайсысының жасы қаншада?',
 '一家有三个兄弟。有人问他们各有多大时，老大说：“我们三人的年龄加起来是 27 岁。我的年龄加上阿尔曼的年龄是 22 岁，巴乌尔然和阿尔曼的年龄加起来是 15 岁。”三个兄弟各有多少岁？','22-26')
s(d,'ocr_linebreak','24 25',wrap)
reflection=unit('reflection','other',10,[646,1277,822,1355],'ОЙЛАСТЫР\nОЙЫҢМЕН БӨЛІС\nҰСЫН','想一想\n分享你的想法\n提出建议','27 28 30',role='lesson_closing_prompt')
s(reflection,'ocr_character','28 30',glyph)
for mod,first,last in [(m4,1,4),(m6,1,4),(m7,1,6)]:
    tasks=[item['id'] for item in mod['elements'] if item['id'].split(':')[-1].startswith('expression-')]
    assert len(tasks)==last-first+1
    mod['printed_expression_grid']=dict(row_major_ids=[tasks[i:i+2] for i in range(0,len(tasks),2)],
                                        sequence_rule='top_to_bottom_rows_and_left_to_right_in_each_row')

for d,ln in [(header['elements'][0],'5'),(m2['elements'][1],'29'),(m3['elements'][1],'3'),(bid,'2'),(m9['elements'][1],'20')]:
    s(d,'ocr_character',ln,glyph)

def link(key,kind,owner,source_object,material,kk,zh):
    obj=entity('link-'+key,'teaching_link',owner['page_refs'][0]['pdf_page'],
               [source_object['page_refs'][0]['bbox'], material['page_refs'][0]['bbox']],
               zh=zh,parent_id=owner['id'],relationship=kind,from_id=source_object['id'],to_id=material['id'],
               rationale_kk=kk,scope='within_module',evidence=[*source_object['page_refs'],*material['page_refs']])
    owner.setdefault('teaching_links',[]).append(obj['id'])
    return obj

links=[
 link('m05-ae-table','uses_as_material',m5,p_ae,table,'«Берілген сабақ кестесі бойынша» деген нұсқау 5А-дағы кестені пайдалануды талап етеді.','“根据给出的课表”明确指向 5А 的课表。'),
 link('m05-v-b','uses_as_material',m5,p_v,p_b,'«Алдыңғы тапсырманың деректерін пайдалан» деген нұсқау 5Б-да анықталатын өз сабақ уақытына сілтейді.','“使用上一小题的数据”指向 5Б 中确定的本人上学时间数据。'),
]

def flag(d,key,kk,zh):
    d.setdefault('review_flags',[]).append(dict(code=key,description_kk=kk))
    auxiliary[d['id']+'#'+key]=zh

flag(bid,'badge_scope','Белгі тек 5А жақтауының үстінде. 5Ә–5В-ға таралуы сканда анық көрсетілмеген.',
     '胶囊印在 5А 框上。原书未明确它是否也适用于 5Ә–5В，请确认作用范围。')
flag(table,'source_typography','Сабақ атауларының қысқартуларын, соңғы қатардың бос ұяшықтарын және асты сызылған жоғарғы минуттарды тексеріңіз.',
     '请核对科目缩写、第六节的空白单元格、分钟的带下划线的上标。')
flag(m4['elements'][2],'example_layout','Нұсқаулық пен үлгі амалдарының бір жақтауда орналасуын тексеріңіз.',
     '请核对并排步骤及竖式的归属和阅读顺序。')
flag(mid,'source_blank','Нәтиже жолында сан басылмаған, тек «мин» бар.',
     '这个竖式的结果行只印有“мин”，请核对原书空位。')
flag(m3['elements'][2],'translation_nuance','«Екі теңсіздіктен» тіркесі масса мен уақыт үшін екі-екіден деп аударылды.',
     '“Екі теңсіздіктен”按分配用法译为质量和时间各两个不等式，请复核教学语境。')
flag(m9,'border_overlap','Төменгі оң жақта кейіпкермен қабаттасқан сәндік жиек мәтін аймағынан тыс қалдырылды.',
     '右下角装饰盖住任务外框的一部分。切框以完整题干为界，请核对。')

supplement={
 'zh':dict(title='复习三年级学过的内容',theme='哈萨克斯坦的国土面积',objects=auxiliary),
 'kk':{}
}
data=dict(schema_version='textbook-lesson/4.0', data_version='v4.1',review_status=status,
          coordinate_system=dict(origin='top-left',unit='source_scan_pixel',bbox_format='[x0,y0,x1,y1]',page_number_base=1),
          book=dict(id=book,title_kk='Математика',grade=4,part=1,year=2023,language='kk-Cyrl',publisher_kk='АЛМАТЫКІТАП БАСПАСЫ',
                    authors_kk=['Ә. Б. Ақпаева','Л. А. Лебедева','М. Ж. Мыңжасарова','Т. В. Лихобабенко']),
          source=dict(repository=repo,revision=tree['sha'],original_pdf=dict(path=original_path,sha256=wiki['source_pdf']['sha256']),
                      corrected_pdf=dict(path=paths['book.pdf'],sha256=wiki['corrected_pdf']['sha256']),wiki_path=paths['wiki.json'],
                      visual_reference='experiments/module_internal_visual_experiment/',
                      content_authority='original_scan',transcription_method='scan_checked_with_existing_ocr_as_evidence'),
          schema_rules=dict(instructional_note_badges=['ЕСІҢДЕ САҚТА!','ОСЫЛАЙ ТАЛДА!','КАЛЬКУЛЯТОР'],
                            teaching_link_types=['supports','uses_as_material'],
                            inherited_badge=dict(text_kk='ӨЗІҢДІ ТЕКСЕР',origin='lesson_inherited',applies_only_to_explicit_self_check_lesson=True)),
          lesson=dict(id=lesson,parent_id=book,number=1,title_kk=title,context_kk='Қазақстанның аумағы',review_status=status,
                      pdf_page_range=[7,10],printed_page_range=['7','10'],boundary_evidence=dict(
                      contents=dict(pdf_page=149,printed_page='149',lesson_start=7,next_lesson_start=11),
                      guide_pdf_pages=[4,5],preceding_section_pdf_page=6,next_lesson=dict(pdf_page=11,number=2,title_kk=title,context_kk='ЭКСПО-2017')),
                      content_order=[u['id'] for u in units],units=units,teaching_links=links),
          pages=list(pages.values()),crop_assets=assets,ocr_suggestions=proposals)
def traverse(entities):
    for d in entities:
        yield d
        yield from traverse(d.get('elements',[]))
all_objects=list(traverse(units))+links
data['counts']=dict(Counter(o['type'] for o in all_objects),ocr_suggestions=len(proposals),
                    text_ocr_suggestions=sum(s['category'] in ('ocr_character','ocr_linebreak') for s in proposals),
                    structure_suggestions=sum(s['category'] not in ('ocr_character','ocr_linebreak') for s in proposals),
                    review_objects=len(all_objects)+len(pages))
(out/'math_grade4_lesson1_structured_v4.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':
    from render import render
    render(data,supplement,source,out)
