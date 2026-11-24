(() => {
'use strict';
const $ = id => document.getElementById(id);
const lang = document.documentElement.lang;
const D = JSON.parse($('dataset').textContent);
const images = JSON.parse($('assets').textContent);
const translations = JSON.parse($('translations').textContent);
const L = D.lesson;
const manifest = {schema_version:'textbook-review/4.0', data_version:D.data_version, textbook_id:D.book.id, lesson_id:L.id};
const key = `${manifest.schema_version}/${manifest.data_version}/${L.id}/${lang}`;
const ui = {
  zh:{
    reviewer:'审核员（选填）',import:'导入记录',export:'导出记录 JSON',scan:'教材原图',review:'审核对象',page:'页码',zoom:'缩放',elements:'内部切割框',omission:'本页存在遗漏内容',cancel:'取消',module:'任务',filter:'筛选',object:'对象',prev:'上一项',next:'下一项',nextUnreviewed:'下一未审核项',approve:'通过',issue:'有问题',unable:'无法判断',skip:'跳过',bulk:'通过本单元及无疑点子项',ocr:'文字有误',
    total:'对象',unreviewed:'未审核',approved:'已通过',unable_to_verify:'无法判断',all:'全部',ocrOnly:'OCR 与结构修正建议',visual:'图片、表格或公式',linkOnly:'教学关联',none:'此筛选下没有对象',noPending:'此筛选下没有其他未审核对象。',
    draft:'浏览器草稿仅保存在本机。请导出 JSON 留存。',noDraft:'此浏览器无法保存本地草稿。请在关闭前导出 JSON。',saved:'已保存审核。',skipped:'已跳过，审核状态保留。',exported:'已发起 JSON 下载。请确认文件已保存。',exportError:'无法发起下载。',imported:'导入完成，原有审核历史已保留。',importError:'导入失败。请使用与本课及当前数据版本匹配的审核 JSON。',conflict:'存在互相冲突的审核或修正。导出将保留各方记录，需人工裁定。',notes:'审核备注',kind:'问题类型',corrected:'建议修正内容（选填）',rawText:'哈萨克语原文',translation:'中文参考翻译',advanced:'高级信息',children:'所含内容',currentRecords:'当前审核记录',known:'人工复核提示',suggestions:'待审核的识别修正',showPage:'查看位置',printed:'印刷',moduleNumber:'任务',missing:'遗漏内容',drag:'在原图上拖动框选，或直接按页报告。',pageOnly:'按页报告',selectedRegion:'已框选遗漏区域。',possible:'可能的内容类型',save:'保存并继续',newType:'修正后的类型',parent:'修正后的归属',order:'同级阅读顺序位置（从 1 开始）',bbox:'新切割框（像素坐标 x0, y0, x1, y1）',redraw:'在原图上重新框选',badBox:'坐标无效，请重新框选或输入有效坐标。',change:'建议操作',keep:'保留当前值',replace:'修改',remove:'删除关联',from:'使用者',to:'引用材料',supports:'提供知识或方法',uses_as_material:'直接使用材料',whichPage:'所在页',noEdit:'发现的问题可在备注中描述。',cell:'已选单元格',reason:'原因（选填）',issueNote:'问题说明（选填）',linked:'打开对象',select:'请选择',root:'本课',record:'记录',blank:'空白',printedVersion:'印刷排法',structure:'结构化说明',region:'位置',suggestionConfirm:'通过会记录对本对象所列修正建议的确认。',protected:'整体通过会保留带疑点、修正建议或既有问题的子项。',partial:'部分子项仍需单独审核。',draftError:'本地草稿无法恢复。可导入已导出的记录。',pageAudit:'这里可确认该页的切割覆盖，也可直接报告遗漏。',sourceOCR:'原始 OCR / 已有校对',badgeScope:'标签作用范围',unsure:'待确认',duplicate:'导入文件里同一记录 ID 对应不同内容。',
  },
  kk:{
    reviewer:'Тексеруші (міндетті емес)',import:'Жазбаларды импорттау',export:'JSON жазбаларын экспорттау',scan:'Оқулықтың түпнұсқа беті',review:'Тексерілетін нысан',page:'Бет',zoom:'Масштаб',elements:'Ішкі жиектер',omission:'Бетте қалып қойған мазмұн бар',cancel:'Бас тарту',module:'Тапсырма',filter:'Сүзгі',object:'Нысан',prev:'Алдыңғы',next:'Келесі',nextUnreviewed:'Келесі тексерілмеген нысан',approve:'Мақұлдау',issue:'Ақау бар',unable:'Анықтай алмадым',skip:'Өткізіп жіберу',bulk:'Бөлім мен күмәнсіз ішкі нысандарды мақұлдау',ocr:'Мәтінде қате бар',
    total:'Нысан',unreviewed:'Тексерілмеген',approved:'Мақұлданған',unable_to_verify:'Анықталмаған',all:'Барлығы',ocrOnly:'OCR және құрылым түзетулері',visual:'Сурет, кесте немесе өрнек',linkOnly:'Оқу байланыстары',none:'Бұл сүзгіде нысан жоқ',noPending:'Бұл сүзгіде басқа тексерілмеген нысан жоқ.',
    draft:'Нобай осы браузерде ғана сақталады. JSON файлын экспорттаңыз.',noDraft:'Осы браузерде нобайды сақтау мүмкін емес. Жабар алдында JSON файлын экспорттаңыз.',saved:'Тексеру жазбасы сақталды.',skipped:'Өткізілді, тексеру күйі сақталды.',exported:'JSON жүктеп алу басталды. Файлдың сақталғанын тексеріңіз.',exportError:'Жүктеп алу басталмады.',imported:'Импорт аяқталды, бұрынғы жазбалар сақталды.',importError:'Импортталмады. Осы сабақ пен деректер нұсқасына сәйкес JSON файлын таңдаңыз.',conflict:'Тексеру жазбаларында қайшылық бар. Экспортта барлық нұсқа сақталады, шешімді адам қабылдайды.',notes:'Тексерушінің ескертпесі',kind:'Ақау түрі',corrected:'Ұсынылатын түзету (міндетті емес)',rawText:'Қазақша түпнұсқа',translation:'Қытайша аударма',advanced:'Қосымша деректер',children:'Ішкі мазмұн',currentRecords:'Ағымдағы жазбалар',known:'Тексеруге арналған ескертпе',suggestions:'Тексеруді қажет ететін түзетулер',showPage:'Орнын көру',printed:'Баспа беті',moduleNumber:'Тапсырма',missing:'Қалып қойған мазмұн',drag:'Түпнұсқадан аймақты белгілеңіз немесе бүкіл бетке ескерту қалдырыңыз.',pageOnly:'Бүкіл бетке ескерту',selectedRegion:'Қалып қойған аймақ белгіленді.',possible:'Ықтимал мазмұн түрі',save:'Сақтау және жалғастыру',newType:'Түзетілген түрі',parent:'Тиесілі жаңа нысан',order:'Оқу ретіндегі орны (1-ден бастап)',bbox:'Жаңа жақтау (пиксельмен x0, y0, x1, y1)',redraw:'Түпнұсқада аймақты қайта белгілеу',badBox:'Координаттар жарамсыз. Аймақты қайта белгілеңіз немесе дұрыс координаттарды енгізіңіз.',change:'Ұсынылатын әрекет',keep:'Сақтау',replace:'Өзгерту',remove:'Байланысты жою',from:'Пайдаланатын нысан',to:'Пайдаланылатын материал',supports:'Білім не әдіспен қолдайды',uses_as_material:'Материалды тікелей пайдаланады',whichPage:'Орналасқан бет',noEdit:'Ақауды ескертпеде сипаттауға болады.',cell:'Таңдалған ұяшық',reason:'Себебі (міндетті емес)',issueNote:'Ақау сипаттамасы (міндетті емес)',linked:'Нысанды ашу',select:'Таңдаңыз',root:'Осы сабақ',record:'Жазба',blank:'Бос',printedVersion:'Баспа нұсқасы',structure:'Құрылымдық сипаттама',region:'Орналасуы',suggestionConfirm:'Мақұлдағанда осы нысанның түзету ұсыныстары расталады.',protected:'Тұтас мақұлдау кезінде күмәні, түзету ұсынысы немесе ақауы бар ішкі нысандардың күйі сақталады.',partial:'Кей ішкі нысанды жеке тексеру керек.',draftError:'Жергілікті нобай ашылмады. Бұрын экспортталған жазбаларды импорттай аласыз.',pageAudit:'Бет мазмұнының толық қамтылуын тексеріңіз немесе қалып қойған аймақ туралы хабарлаңыз.',sourceOCR:'Бастапқы OCR / бұрынғы түзету',badgeScope:'Белгінің қолданылу аясы',unsure:'Тексеру керек',duplicate:'Бір жазба идентификаторы импортта әртүрлі мазмұнға берілген.',
  }
}[lang];
const types = {
  page:['原图页','Түпнұсқа беті'],module:['任务','Тапсырма'],instructional_note:['教学说明','Оқу ескертпесі'],
  other:['其他内容','Басқа мазмұн'],text:['文字','Мәтін'],module_number:['任务编号','Тапсырма нөмірі'],
  subtask_number:['子题编号','Тармақ нөмірі'],module_badge:['任务标签','Тапсырма белгісі'],
  informative_image:['信息性图片','Ақпараттық сурет'],formula:['公式','Өрнек'],table:['表格','Кесте'],
  subtask:['子题','Тапсырма тармағы'],example:['示范','Үлгі'],teaching_link:['教学关联','Оқу байланысы']
};
const codes = {
  missing_region:['漏切','Қалып қойған аймақ'],extra_region:['多切','Артық бөлінген аймақ'],
  boundary:['边界错误','Жақтау қатесі'],assignment:['元素归属错误','Мазмұнның тиесілігі'],
  element_type:['内容类型错误','Мазмұн түрінің қатесі'],badge:['Badge 错误','Белгі қатесі'],
  instructional_note:['Instructional Note 错误','Оқу ескертпесінің қатесі'],teaching_link:['教学关联错误','Оқу байланысының қатесі'],
  ocr_character:['OCR 字符错误','OCR таңба қатесі'],ocr_linebreak:['断词或换行错误','Тасымал не жол үзілісі'],
  formula_structure:['公式错误','Өрнек қатесі'],table_structure:['表格结构错误','Кесте құрылымының қатесі'],
  image_relationship:['信息性图片理解错误','Суреттегі байланысты түсіндіру қатесі'],reading_order:['阅读顺序错误','Оқу реті қатесі'],
  translation_zh:['中文辅助翻译错误','Қытайша аударма қатесі'],other:['其他','Басқа']
};
const local = pair => pair[lang==='zh'?0:1];
const nameOf = code => local(types[code] ?? [code,code]);
const byId = new Map();
const ordered = [];
const pages = new Map(D.pages.map(p => [p.pdf_page,p]));
const proposals = new Map(D.ocr_suggestions.map(p => [p.id,p]));
const recordStates = ['approved','issue','unable_to_verify'];
const visualKinds = ['informative_image','table','formula'];
const filterOptions = [
  ['all','all'],['issue','issue'],['unreviewed','unreviewed'],['unable_to_verify','unable_to_verify'],
  ['ocr','ocrOnly'],['visual','visual'],['teaching_link','linkOnly']
];
const pageOf = o => o.page_refs[0].pdf_page;
const uid = () => globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random().toString(36).slice(2)}`;
let stream = uid(), records = new Map(), durable = true;
let active, pdf=D.pages[0].pdf_page, draw;
const groups = [];
const childLists = new Map();
const views = new Map();
const scroller = $('review-scroll');
const unitTypes = new Set(['module','instructional_note']);
const sortRecords = (a,b) => a.record_id.localeCompare(b.record_id);

function children(o) {
  if (!childLists.has(o.id)) {
    const elements = new Map((o.elements??[]).map(child=>[child.id,child]));
    const orderedElements = (o.content_order??[...elements.keys()]).map(id=>elements.get(id));
    childLists.set(o.id,[...orderedElements,...L.teaching_links.filter(link=>link.parent_id===o.id)]);
  }
  return childLists.get(o.id);
}
function add(o, parent, group) {
  const owner = unitTypes.has(o.type) ? o.id : parent?.owner??null;
  const depth = parent ? parent.depth+1 : 0;
  const item = {o,parent,owner,group,depth};
  byId.set(o.id,item);
  ordered.push(o);
  for (const child of children(o)) add(child,item,group);
}
function groupFor(p) {
  if (groups.at(-1)?.pdf!==p) groups.push({pdf:p,roots:[]});
  return groups.at(-1);
}
const units = new Map(L.units.map(o=>[o.id,o]));
for (const id of L.content_order) {
  const o=units.get(id);
  const group=groupFor(pageOf(o));
  group.roots.push(o);
  add(o,null,group);
}
for (const page of D.pages) {
  const group=groups.find(g=>g.pdf===page.pdf_page)??groupFor(page.pdf_page);
  const o={id:page.id,type:'page',page_refs:[{pdf_page:page.pdf_page,printed_page:page.printed_page,
    scan_asset_id:page.scan_asset_id,bbox:[0,0,page.width,page.height]}]};
  group.roots.push(o);
  add(o,null,group);
}
for (const link of L.teaching_links) {
  if (byId.has(link.id)) continue;
  const group=groups.find(g=>g.pdf===pageOf(link))??groupFor(pageOf(link));
  group.roots.push(link);
  add(link,null,group);
}
const recordables = new Set(ordered.map(o => o.id));
const omission = r => r.report_kind === 'page_omission';
const objectRecords = id => [...records.values()].filter(r => r.object_id===id);
function liveRecords(id, alsoOmissions=false) {
  const relevant = objectRecords(id).filter(r => alsoOmissions || !omission(r));
  const superseded = new Set(relevant.flatMap(r => r.supersedes ?? []));
  return relevant.filter(r => !superseded.has(r.record_id)).sort(sortRecords);
}
function signature(r) {
  return canonical([r.status,r.issue_code??null,r.changes??[],r.confirmed_suggestion_ids??[]]);
}
function conflict(o) {
  const live=liveRecords(o.id);
  return live.some((a,i)=>live.slice(i+1).some(b=>
    a.review_scope===b.review_scope &&
    (a.status!==b.status || (a.issue_code===b.issue_code && a.cell_id===b.cell_id && signature(a)!==signature(b)))));
}
function state(o) {
  const live=liveRecords(o.id);
  if (conflict(o) || (o.type==='page' && objectRecords(o.id).some(omission))) return 'issue';
  return live.find(r=>r.status==='issue')?.status ?? live.find(r=>r.review_scope==='textbook')?.status ?? 'unreviewed';
}

function node(tag,txt,cls) {
  const out=document.createElement(tag);
  if (txt!==undefined && txt!==null) out.textContent=txt;
  if (cls) out.className=cls;
  return out;
}
function button(txt,action,cls) {
  const b=node('button',txt,cls);
  b.type='button';
  b.addEventListener('click',action);
  return b;
}
function option(value,label) {
  const o=node('option',label);
  o.value=value;
  return o;
}
function optionSet(select,pairs) {
  select.replaceChildren(...pairs.map(([value,label]) => option(value,label)));
}
const aux = id => translations.objects?.[id];
const fmt = o => JSON.stringify(o,null,2);
function label(o) {
  const owner=byId.get(o.id)?.owner;
  const mod=owner && byId.get(owner).o.module_number;
  if (o.type==='module') return `${ui.moduleNumber} ${o.module_number}`;
  if (o.type==='page') return `PDF ${pageOf(o)} · ${ui.printed} ${o.page_refs[0].printed_page}`;
  if (o.type==='teaching_link') return `${nameOf(o.type)} · ${label(byId.get(o.from_id).o).split(' · ')[0]} → ${nameOf(byId.get(o.to_id).o.type)}`;
  const part=o.subtask_label ?? byId.get(o.parent_id)?.o.subtask_label;
  const prefix=part ?? mod;
  const excerpt=(o.text_kk??'').split('\n')[0];
  const hint=excerpt && !['subtask_number','module_number'].includes(o.type) ? ' · '+(excerpt.length>46?excerpt.slice(0,45)+'…':excerpt) : '';
  return (prefix ? prefix+' · ' : '')+nameOf(o.type)+hint;
}

function readDraft() {
  try {
    const raw=localStorage.getItem(key);
    if (!raw) return;
    const draft=JSON.parse(raw);
    merge(draft);
    stream=draft.stream || stream;
    $('reviewer').value=draft.reviewer ?? '';
  } catch(e) {
    durable=false;
    message(ui.draftError,true);
  }
}
function persist() {
  try {
    localStorage.setItem(key,JSON.stringify({...manifest,stream,reviewer:$('reviewer').value,records:[...records.values()]}));
    durable=true;
  } catch(e) { durable=false; }
  $('draft').textContent=durable?ui.draft:ui.noDraft;
}
function message(text='',error=false) {
  $('message').textContent=text;
  $('message').dataset.error=error;
}

function validRecord(r) {
  if (!r || typeof r.record_id!=='string' || typeof r.reviewer_stream_id!=='string' ||
      !recordables.has(r.object_id) || r.textbook_id!==manifest.textbook_id ||
      r.lesson_id!==manifest.lesson_id || r.data_version!==manifest.data_version ||
      !recordStates.includes(r.status) || !['zh','kk'].includes(r.interface_language) ||
      !pages.has(r.pdf_page) || !['textbook','auxiliary_translation','page_omission'].includes(r.review_scope) || !Array.isArray(r.changes) || !Array.isArray(r.supersedes) ||
      !Array.isArray(r.source_locations) || r.issue_code!=null && !(r.issue_code in codes)) return false;
  return r.supersedes.every(x=>typeof x==='string') &&
    r.changes.every(c=>c && typeof c.op==='string' && typeof c.target_id==='string');
}
function canonical(value) {
  if (!value || typeof value!=='object') return JSON.stringify(value);
  if (Array.isArray(value)) return '['+value.map(canonical).join(',')+']';
  return '{'+Object.keys(value).sort().map(k=>JSON.stringify(k)+':'+canonical(value[k])).join(',')+'}';
}
function merge(f) {
  if (!f || Object.entries(manifest).some(([k,v]) => f[k]!==v) || !Array.isArray(f.records)) throw Error(ui.importError);
  const next=new Map(records);
  for (const r of f.records) {
    if (!validRecord(r)) throw Error(ui.importError);
    const prior=next.get(r.record_id);
    if (prior && canonical(prior)!==canonical(r)) throw Error(ui.duplicate);
    next.set(r.record_id,r);
  }
  for (const r of next.values()) {
    if (r.supersedes.some(id=>{
      const old=next.get(id);
      return id===r.record_id || old && (old.object_id!==r.object_id || old.reviewer_stream_id!==r.reviewer_stream_id ||
        old.report_kind!==r.report_kind || old.review_scope!==r.review_scope || old.recorded_at>r.recorded_at);
    })) throw Error(ui.importError);
  }
  records=next;
}
function exportRecords() {
  try {
    const dump={...manifest,exported_at:new Date().toISOString(),export_interface_language:lang,records:[...records.values()].sort(sortRecords)};
    const url=URL.createObjectURL(new Blob([JSON.stringify(dump,null,2)],{type:'application/json'}));
    const a=node('a');
    a.href=url;
    a.download=`math_grade4_lesson1_review_records_${lang}_${new Date().toISOString().replace(/[:.]/g,'-')}.json`;
    document.body.append(a);
    a.click();
    a.remove();
    setTimeout(()=>URL.revokeObjectURL(url),30000);
    message(ui.exported);
  } catch(e) { message(ui.exportError,true); }
}
function original(o) {
  if (o.type==='teaching_link') return {from_id:o.from_id,to_id:o.to_id,relationship:o.relationship,rationale_kk:o.rationale_kk};
  if (o.type==='page') return {pdf_page:pageOf(o),printed_page:o.page_refs[0].printed_page};
  const fields=['type','parent_id','content_order','text_kk','cells','vertical','structured_description','scope_ids','instructional_note_badge','ocr_evidence'];
  return Object.fromEntries(fields.filter(k=>o[k]!==undefined).map(k=>[k,o[k]]));
}
function append(o,status,extra={}) {
  const report_kind=extra.report_kind ?? 'object_review';
  const id=uid();
  const at=new Date().toISOString();
  const isOmission=report_kind==='page_omission';
  const review_scope=isOmission?'page_omission':extra.issue_code==='translation_zh'?'auxiliary_translation':'textbook';
  const supersedes=isOmission?[]:liveRecords(o.id).filter(r=>
    r.reviewer_stream_id===stream && r.review_scope===review_scope &&
    (status!=='issue' || r.status!=='issue' || (r.issue_code===extra.issue_code && r.cell_id===extra.cell_id))
  ).map(r=>r.record_id);
  const data = {...manifest,record_id:id,reviewer_stream_id:stream,report_kind,object_id:o.id,
    object_type:o.type,pdf_page:pageOf(o),source_locations:o.page_refs,status,review_scope,
    issue_code:null,note:'',original_content:original(o),changes:[],confirmed_suggestion_ids:[],
    interface_language:lang,recorded_at:at,supersedes,...extra};
  if ($('reviewer').value.trim()) data.reviewer=$('reviewer').value.trim();
  records.set(id,data);
}
const files = $('file');
$('import').onclick=()=>files.click();
$('export').onclick=exportRecords;
files.onchange=async () => {
  if (!files.files.length) return;
  try {
    merge(JSON.parse(await files.files[0].text()));
    persist();
    refreshStates();
    drawSheet(false);
    message(ui.imported);
  } catch(e) { message(e.message===ui.duplicate?ui.duplicate:ui.importError,true); }
  files.value='';
};
$('reviewer').oninput=persist;

function setBox(el,b,page) {
  const [x,y,r,d]=b;
  Object.assign(el.style,{left:`${100*x/page.width}%`,top:`${100*y/page.height}%`,
    width:`${100*(r-x)/page.width}%`,height:`${100*(d-y)/page.height}%`});
}
function drawSheet(center) {
  const page=pages.get(pdf);
  const img=$('scan');
  img.alt=`${ui.scan} PDF ${pdf}`;
  img.width=page.width;
  img.height=page.height;
  if (img.dataset.assetId!==page.scan_asset_id) {
    img.src=images[page.scan_asset_id];
    img.dataset.assetId=page.scan_asset_id;
  }
  $('sheet').style.width=$('zoom').value;
  const boxes=$('overlays');
  boxes.replaceChildren();
  let focus;
  for (const o of ordered) {
    if (!['module','instructional_note'].includes(o.type) && o!==active &&
        (!$('elements').checked || o.type==='page' || o.type==='teaching_link')) continue;
    for (const r of o.page_refs.filter(x=>x.pdf_page===pdf)) {
      const b=button('',()=>jumpTo(o,pdf),'box');
      b.title=label(o);
      b.setAttribute('aria-label',label(o));
      b.dataset.id=o.id;
      b.dataset.type=o.type;
      setBox(b,r.bbox,page);
      if (o===active) {
        b.classList.add('selected');
        if (!focus && o.type!=='page') focus=r.bbox;
      }
      boxes.append(b);
    }
  }
  const selectedCell=views.get(active?.id)?.cell;
  if (selectedCell && selectedCell.page_refs[0].pdf_page===pdf) {
    const b=node('div',null,'box cell-picked');
    b.dataset.type='table';
    setBox(b,selectedCell.page_refs[0].bbox,page);
    boxes.append(b);
    focus=selectedCell.page_refs[0].bbox;
  }
  for (const r of objectRecords(page.id).filter(omission)) {
    if (!r.omission_region) continue;
    const marker=node('span',null,'box');
    marker.dataset.type='page';
    marker.style.pointerEvents='none';
    marker.style.setProperty('--box','#a33722');
    setBox(marker,r.omission_region,page);
    boxes.append(marker);
  }
  if (center) {
    const sc=$('scan-scroll');
    const sheet=$('sheet');
    sc.scrollTo(focus ? Math.max(0,(focus[0]+focus[2])*sheet.offsetWidth/(2*page.width)-sc.clientWidth/2) : 0,
      focus ? Math.max(0,focus[1]*sheet.offsetWidth/page.width-45) : 0);
  }
}
function block(parent,title,content,cls='') {
  if (!content) return;
  if (title) parent.append(node('div',title,'caption'));
  parent.append(node('div',content,`content ${cls}`));
}
function renderContent(div,o,view) {
  if (o.type==='page') block(div,null,ui.pageAudit);
  if (o.vertical) renderVertical(div,o.vertical);
  else block(div,ui.rawText,o.text_kk,o.type==='formula'?'equations':'');
  if (aux(o.id) && o.type!=='teaching_link') block(div,ui.translation,aux(o.id),'translation');
  if (o.scope_ids) {
    const scopes=o.scope_ids.map(id=>byId.get(id)?.o).filter(Boolean);
    block(div,ui.badgeScope,scopes.map(label).join(' · '));
  }
  if (o.crop_asset_id) {
    const img=node('img',null,'crop');
    img.loading='lazy';
    const [x,y,r,b]=D.crop_assets[o.crop_asset_id].bbox;
    img.width=r-x;
    img.height=b-y;
    img.src=images[o.crop_asset_id];
    img.alt=`${ui.scan} · ${nameOf(o.type)}`;
    div.append(img);
  }
  if (o.structured_description) block(div,ui.structure,o.structured_description.description_kk);
  if (o.cells) renderTable(div,o,view);
  if (o.type==='teaching_link') {
    block(div,ui.change,ui[o.relationship]);
    block(div,ui.rawText,o.rationale_kk);
    block(div,ui.translation,aux(o.id),'translation');
    const nav=node('div',null,'toolbar');
    for (const [key,id] of [['from',o.from_id],['to',o.to_id]]) {
      const tgt=byId.get(id).o;
      nav.append(button(`${ui[key]} · ${label(tgt)}`,()=>jumpTo(tgt)));
    }
    div.append(nav);
  }
  if (new Set(o.page_refs.map(r=>r.pdf_page)).size>1) {
    const nav=node('div',null,'pager');
    for (const p of new Set(o.page_refs.map(r=>r.pdf_page))) nav.append(button(`PDF ${p}`,()=>manualScan(o,p)));
    div.append(nav);
  }
  for (const flag of o.review_flags ?? []) {
    const item=node('div',null,'flag');
    block(item,ui.known,flag.description_kk);
    if (aux(o.id+'#'+flag.code)) block(item,null,aux(o.id+'#'+flag.code));
    div.append(item);
  }
  if (o.ocr_suggestion_ids?.length) {
    const d=node('details');
    d.append(node('summary',`${ui.suggestions} (${o.ocr_suggestion_ids.length})`),node('p',ui.suggestionConfirm));
    for (const id of o.ocr_suggestion_ids) {
      const s=proposals.get(id);
      block(d,local(codes[s.category]),s.reason_kk);
      if (aux(id)) block(d,null,aux(id));
      const ocr=node('details');
      ocr.append(node('summary',ui.sourceOCR));
      for (const item of s.source_lines) ocr.append(node('pre',`${item.line_id} · ${item.raw??'∅'}\n→ ${item.existing_corrected??'∅'}`));
      d.append(ocr);
    }
    div.append(d);
  }
  const d=node('details');
  d.append(node('summary',ui.advanced));
  d.addEventListener('toggle',()=>{
    if (d.open && d.childElementCount===1) d.append(node('pre',fmt({id:o.id,sources:o.page_refs,...original(o)})));
  });
  div.append(d);
}
function renderVertical(parent,v) {
  parent.append(node('div',ui.rawText,'caption'));
  const d=node('div',null,'vertical');
  if (v.expression_kk) d.append(node('div',v.expression_kk,'formula-caption'));
  const upper=node('span');
  function withHighlight(target, value, token) {
    const at=token ? value.indexOf(token) : -1;
    if (at<0) { target.textContent=value; return; }
    target.append(value.slice(0,at),node('strong',token,'marked'),value.slice(at+token.length));
  }
  withHighlight(upper,v.upper,v.highlight?.position?.startsWith('upper')?v.highlight.value:null);
  d.append(node('span'),upper,node('span',v.operator),node('span',v.lower));
  if (v.result_rule_printed!==false) d.append(node('span',null,'rule'));
  const result=node('span');
  const printed=v.equivalence_kk ?? v.result ?? `    ${v.result_blank_unit??''}`;
  withHighlight(result,printed,v.highlight?.position?.startsWith('first_digit')?v.highlight.value:null);
  d.append(node('span'),result);
  parent.append(d);
}
function timeText(btn,t) {
  for (const [i,time] of [t.start,t.end].entries()) {
    const [hh,mm]=time.split(':');
    if (i) btn.append(document.createTextNode(' – '));
    btn.append(document.createTextNode(String(Number(hh))));
    const sup=node('sup');
    sup.append(node('u',mm));
    btn.append(sup);
  }
}
function renderTable(parent,o,view) {
  const pick=node('p',null,'caption');
  pick.hidden=true;
  const wrap=node('div',null,'table-wrap');
  const table=node('table');
  const thead=node('thead'), tbody=node('tbody');
  for (let r=0;r<o.row_count;r++) {
    const tr=node('tr');
    for (const c of o.cells.filter(x=>x.row===r)) {
      const td=node(c.header?'th':'td');
      td.colSpan=c.colspan;
      td.rowSpan=c.rowspan;
      if (c.header) td.scope='col';
      const b=button(c.time_interval?'':c.printed_text_kk??c.text_kk,()=>{
        view.cell=view.cell?.id===c.id?null:c;
        table.querySelector('[aria-pressed="true"]')?.setAttribute('aria-pressed','false');
        b.setAttribute('aria-pressed',String(view.cell===c));
        pick.hidden=!view.cell;
        pick.textContent=view.cell?`${ui.cell} ${c.row+1}, ${c.column+1} · ${c.text_kk||ui.blank}`:'';
        manualScan(o,pageOf(o));
      });
      b.setAttribute('aria-label',`${ui.cell} ${c.row+1}, ${c.column+1} ${c.text_kk||ui.blank}`);
      b.setAttribute('aria-pressed','false');
      if (c.time_interval) timeText(b,c.time_interval);
      if (c.empty) b.append(node('span','\u00a0'));
      td.append(b);
      if (aux(c.id)) td.append(node('small',aux(c.id)));
      tr.append(td);
    }
    (o.header_rows.includes(r)?thead:tbody).append(tr);
  }
  table.append(thead,tbody);
  wrap.append(table);
  parent.append(wrap,pick);
}
function field(parent,id,label,control) {
  const wrapper=node('label',null,'form-row');
  const f=node(control);
  f.name=id;
  wrapper.append(node('span',label),f);
  parent.append(wrapper);
  return f;
}
function selectField(parent,id,label,options,value) {
  const f=field(parent,id,label,'select');
  optionSet(f,options);
  if (value!==undefined) f.value=value;
  return f;
}
function closeEditor(ctx) {
  if (draw?.ctx===ctx) clearDraw();
  ctx.view.form.hidden=true;
  ctx.view.form.replaceChildren();
  ctx.view.editor=null;
}
function editor(ctx,title,onSave) {
  const form=ctx.view.form;
  if (ctx.view.editor) closeEditor(ctx.view.editor);
  ctx.view.editor=ctx;
  form.hidden=false;
  form.append(node('h5',title));
  if (ctx.cell) form.append(node('p',`${ui.cell} ${ctx.cell.row+1}, ${ctx.cell.column+1}`,'caption'));
  const content=node('div');
  const actions=node('div',null,'toolbar');
  const submit=node('button',ui.save,'accent');
  submit.type='submit';
  const cancel=button(ui.cancel,()=>closeEditor(ctx));
  actions.append(submit,cancel);
  form.append(content,actions);
  form.onsubmit=e=>{
    e.preventDefault();
    if (onSave()!==false) keepPosition(()=>closeEditor(ctx));
  };
  return content;
}
function get(ctx,name) {
  return ctx.view.form.elements.namedItem(name);
}
const change = (op,target_id,field,old_value,value,extra={}) => ({op,target_id,field,old_value,value,...extra});
function originalText(o,cell) {
  return cell?.text_kk ?? o.text_kk ?? '';
}
function setFields(panel,code,ctx) {
  const {o,cell,pdf}=ctx;
  panel.replaceChildren();
  const inputText=(value='',label=ui.corrected)=>{
    const f=field(panel,'new-value',label,'textarea');
    f.value=value;
    return f;
  };
  if (['ocr_character','ocr_linebreak'].includes(code)) inputText(originalText(o,cell));
  else if (code==='translation_zh') inputText(aux(cell?.id) ?? aux(o.id) ?? '');
  else if (code==='element_type') selectField(panel,'new-type',ui.newType,Object.entries(types).filter(([t])=>!['page','teaching_link'].includes(t)).map(([t])=>[t,nameOf(t)]),o.type);
  else if (code==='assignment') {
    const p=o.elements?o.elements.map(x=>x.id):[];
    const descendants=new Set(flatChildren(o).map(x=>x.id));
    const candidates=ordered.filter(c=>c.elements && c.id!==o.id && !p.includes(c.id) && !descendants.has(c.id));
    selectField(panel,'new-parent',ui.parent,[[L.id,ui.root],...candidates.map(c=>[c.id,label(c)])],o.parent_id??L.id);
  } else if (code==='reading_order') {
    const f=field(panel,'new-order',ui.order,'input');
    f.type='number';
    f.min=1;
    f.step=1;
  } else if (code==='boundary') {
    const number=0;
    const onPage=o.page_refs.filter(r=>r.pdf_page===pdf);
    const options=onPage.map((r,i)=>[String(i),`${i+1} · ${r.bbox.join(', ')}`]);
    const region=selectField(panel,'region-index',ui.region,options,String(number));
    const f=field(panel,'new-bbox',ui.bbox,'input');
    f.value=onPage[number]?.bbox.join(', ')??'';
    region.onchange=()=>{f.value=onPage[Number(region.value)].bbox.join(', ');};
    panel.append(button(ui.redraw,()=>startDraw('boundary',ctx)));
  } else if (code==='teaching_link') {
    if (o.type==='teaching_link') {
      selectField(panel,'link-action',ui.change,[['replace',ui.replace],['remove',ui.remove]]);
      const candidates=ordered.filter(c=>!['page','teaching_link'].includes(c.type)).map(c=>[c.id,label(c)]);
      selectField(panel,'link-from',ui.from,candidates,o.from_id);
      selectField(panel,'link-to',ui.to,candidates,o.to_id);
      selectField(panel,'link-relation',ui.kind,[['supports',ui.supports],['uses_as_material',ui.uses_as_material]],o.relationship);
      inputText(o.rationale_kk);
    } else {
      const candidates=ordered.filter(c=>!['page','teaching_link'].includes(c.type)).map(c=>[c.id,label(c)]);
      selectField(panel,'link-to',ui.to,[['',ui.select],...candidates]);
      selectField(panel,'link-relation',ui.kind,[['supports',ui.supports],['uses_as_material',ui.uses_as_material]]);
      inputText();
    }
  } else if (code==='badge') {
    inputText(o.text_kk??'');
    const owner=byId.get(o.id)?.owner;
    if (o.type==='module_badge' && owner) {
      const parent=byId.get(owner).o;
      const scopes=[parent,...flatChildren(parent).filter(c=>c.type==='subtask')];
      const select=selectField(panel,'new-scope',ui.badgeScope,scopes.map(c=>[c.id,label(c)]));
      select.multiple=true;
      select.size=Math.min(5,scopes.length);
      for (const opt of select.options) opt.selected=o.scope_ids?.includes(opt.value);
    }
  } else if (code==='instructional_note') {
    selectField(panel,'note-badge',ui.kind,[['',ui.select],...D.schema_rules.instructional_note_badges.map(b=>[b,b])],o.instructional_note_badge??'');
    inputText(o.text_kk??'');
  } else if (code==='table_structure' && cell) {
    inputText(cell.text_kk);
    const f=field(panel,'new-rowspan',ui.rowSpan,'input');
    f.type='number'; f.min=1; f.max=o.row_count-cell.row; f.value=cell.rowspan;
    const g=field(panel,'new-colspan',ui.colSpan,'input');
    g.type='number'; g.min=1; g.max=o.column_count-cell.column; g.value=cell.colspan;
  } else if (code==='formula_structure' && o.vertical) {
    for (const [key,label] of [['upper',ui.upper],['lower',ui.lower],['operator',ui.operator],['result',ui.result],['equivalence_kk',ui.equivalence]]) {
      field(panel,'vertical-'+key,label,'input').value=o.vertical[key]??'';
    }
  } else if (code==='image_relationship') inputText(o.structured_description?.description_kk??'');
  else if (code==='formula_structure') inputText(o.text_kk??'');
  else if (code==='missing_region') {
    selectField(panel,'missing-type',ui.possible,[['',ui.unsure],...['module','instructional_note','text','table','formula','informative_image','other'].map(t=>[t,nameOf(t)])]);
  } else {
    panel.append(node('small',ui.noEdit));
  }
}
function flatChildren(o) {
  return (o.elements??[]).flatMap(x=>[x,...flatChildren(x)]);
}
function validBbox(b,p) {
  return b.length===4 && b.every(x=>Number.isInteger(x) && x>=0) && b[0]<b[2] && b[1]<b[3] && b[2]<=p.width && b[3]<=p.height;
}
function issueChanges(ctx,code) {
  const {o,cell,pdf,box}=ctx;
  const field=name=>get(ctx,name);
  const list=[];
  const value=field('new-value')?.value;
  const put=(target,field,oldValue,newValue,op='replace_value',extra={})=>{
    if (JSON.stringify(oldValue??null)!==JSON.stringify(newValue??null)) list.push(change(op,target,field,oldValue??null,newValue??null,extra));
  };
  if (['ocr_character','ocr_linebreak'].includes(code)) {
    if (value || cell || o.text_kk!==undefined) put(cell?.id??o.id,'text_kk',originalText(o,cell),value,'replace_value',cell?{table_id:o.id}:{});
  } else if (code==='translation_zh') {
    const target=cell?.id??o.id;
    put(target,'translation_zh',aux(target),value,'replace_auxiliary_translation');
  } else if (code==='element_type') put(o.id,'type',o.type,field('new-type').value);
  else if (code==='extra_region') list.push(change('remove_region',o.id,'page_refs',o.page_refs,null));
  else if (code==='assignment') put(o.id,'parent_id',o.parent_id,field('new-parent').value,'move_object');
  else if (code==='reading_order' && field('new-order').value) {
    list.push(change('reorder_object',o.id,'content_order',null,Number(field('new-order').value),{parent_id:o.parent_id??L.id}));
  } else if (code==='boundary') {
    const page=pages.get(pdf);
    const input=field('new-bbox').value.trim().split(/[ ,]+/).map(Number);
    if (!validBbox(input,page)) throw Error(ui.badBox);
    const old=o.page_refs.filter(r=>r.pdf_page===pdf)[Number(field('region-index').value)];
    put(o.id,'page_refs',old,{...old,bbox:input},'replace_region',{region_index:o.page_refs.indexOf(old)});
  } else if (code==='teaching_link') {
    const to=field('link-to')?.value;
    const action=field('link-action')?.value;
    if (o.type==='teaching_link') {
      if (action==='remove') list.push(change('remove_link',o.id,'teaching_links',original(o),null));
      else {
        const from=field('link-from').value;
        const next={from_id:from,to_id:to,relationship:field('link-relation').value,rationale_kk:value};
        if (from===to) throw Error(ui.invalidLink);
        put(o.id,'teaching_links',original(o),next,'update_link');
      }
    } else if (to && to!==o.id) {
      list.push(change('add_link',o.id,'teaching_links',null,{from_id:o.id,to_id:to,relationship:field('link-relation').value,rationale_kk:value}));
    }
  } else if (code==='badge') {
    put(o.id,'text_kk',o.text_kk,value);
    if (field('new-scope')) put(o.id,'scope_ids',o.scope_ids,[...field('new-scope').selectedOptions].map(opt=>opt.value));
  } else if (code==='instructional_note') {
    if (field('note-badge').value) put(o.id,'instructional_note_badge',o.instructional_note_badge,field('note-badge').value);
    if (value || o.text_kk!==undefined) put(o.id,'text_kk',o.text_kk,value);
  } else if (code==='table_structure' && cell) {
    const extra={table_id:o.id};
    put(cell.id,'text_kk',cell.text_kk,value,'replace_table_cell',extra);
    for (const span of ['rowspan','colspan']) {
      const v=field('new-'+span).value;
      if (v) put(cell.id,span,cell[span],Number(v),'replace_table_cell',extra);
    }
  } else if (code==='formula_structure' && o.vertical) {
    const next={...o.vertical};
    for (const key of ['upper','lower','operator','result','equivalence_kk']) {
      const v=field('vertical-'+key).value.trim();
      if (v || key in next) next[key]=v||null;
    }
    put(o.id,'vertical',o.vertical,next,'replace_formula_layout');
  } else if (code==='formula_structure') put(o.id,'text_kk',o.text_kk,value);
  else if (code==='image_relationship') put(o.id,'structured_description.description_kk',o.structured_description?.description_kk,value,'replace_visual_description');
  else if (code==='missing_region') {
    list.push(change('review_missing_region',o.id,'page_refs',null,{pdf_page:pdf,bbox:box??null,possible_type:field('missing-type')?.value||null}));
  }
  if (!list.length && ['boundary','assignment','reading_order','element_type','table_structure','formula_structure','image_relationship','teaching_link','instructional_note','ocr_character','ocr_linebreak','badge','translation_zh'].includes(code)) {
    list.push({op:'review_issue',target_id:cell?.id??o.id,issue_code:code});
  }
  return list;
}
function approveOne(o, sourcePage=pageOf(o)) {
  const ids=o.ocr_suggestion_ids??[];
  const changes=ids.map(id=>{
    const s=proposals.get(id);
    return {op:'confirm_scan_restoration',target_id:o.id,suggestion_id:s.id,category:s.category,
      source_lines:s.source_lines,source_locations:s.evidence_regions,suggested_value:s.suggested_value,
      value:s.suggested_value,...(s.proposed_changes?{proposed_changes:s.proposed_changes}:{})};
  });
  append(o,'approved',{confirmed_suggestion_ids:ids,changes,pdf_page:sourcePage});
}
const continuousLabels={
  zh:{review:'连续审核',jump:'跳到任务',toTop:'返回顶部',applyFilter:'刷新结果',autoCollapse:'通过后自动收起',
    expand:'展开',collapse:'收起',elementReview:'审核此元素',covered:'随整卡通过',save:'保存',
    childIssues:n=>`${n} 个子项有问题`,childUnable:n=>`${n} 个子项无法判断`,childPending:n=>`${n} 个子项需单独复核`,
    pageReview:'本页完整性',protected:'整卡通过涵盖普通子项。已记录的问题、无法判断和待复核建议仍保留。'},
  kk:{review:'Ретімен тексеру',jump:'Тапсырмаға өту',toTop:'Басына қайту',applyFilter:'Нәтижені жаңарту',
    autoCollapse:'Мақұлдаған соң жинау',expand:'Ашу',collapse:'Жинау',elementReview:'Элементті тексеру',covered:'Бөліммен бірге мақұлданды',
    save:'Сақтау',childIssues:n=>`${n} ішкі элементте ақау бар`,childUnable:n=>`${n} ішкі элемент анықталмады`,
    childPending:n=>`${n} ішкі элементті жеке тексеру қажет`,pageReview:'Беттің толықтығы',
    protected:'Бөлімді мақұлдау кәдімгі ішкі элементтерге қолданылады. Тіркелген ақаулар, анықталмаған күйлер және тексеру ұсыныстары сақталады.'}
};
Object.assign(ui,continuousLabels[lang]);
const mobile=matchMedia('(max-width:680px)');
const reviewStatus=new Map();
const explicitStatus=new Map();
const needsSeparateReview=o=>o.review_flags?.length || o.ocr_suggestion_ids?.length || o.type==='teaching_link';
const narrow=()=>mobile.matches;
let alignedTop=null, scrollFrame=0, highlightTimer, highlighted;
const scrollY=()=>narrow()?window.scrollY:scroller.scrollTop;
function setScroll(y) {
  if (narrow()) window.scrollTo({top:y,behavior:'instant'});
  else scroller.scrollTo({top:y,behavior:'instant'});
  alignedTop=scrollY();
}
function keepPosition(callback) {
  const y=scrollY();
  const result=callback();
  const scrollRoot=narrow()?document.scrollingElement:scroller;
  const remaining=scrollRoot.scrollHeight-scrollRoot.clientHeight;
  // Closing a form in the last card can otherwise clamp the current scroll offset.
  if (y>remaining) {
    const tail=$('review-tail');
    tail.style.height=`${tail.offsetHeight+y-remaining}px`;
  }
  setScroll(y);
  return result;
}
function statusOf(o) {
  return reviewStatus.get(o.id)??'unreviewed';
}
function covered(o) {
  let p=byId.get(o.id).parent;
  while (p) {
    if (unitTypes.has(p.o.type)) return explicitStatus.get(p.o.id)==='approved';
    p=p.parent;
  }
  return false;
}
function refreshStates() {
  for (const o of ordered) explicitStatus.set(o.id,state(o));
  const stats=Object.fromEntries(['unreviewed',...recordStates].map(s=>[s,0]));
  for (const o of ordered) {
    const direct=explicitStatus.get(o.id);
    const inherited=direct==='unreviewed' && !needsSeparateReview(o) && covered(o);
    const status=inherited?'approved':direct;
    reviewStatus.set(o.id,status);
    stats[status]++;
    const view=views.get(o.id);
    view.status.textContent=inherited?ui.covered:ui[status];
    view.status.dataset.state=status;
    view.card.dataset.state=status;
    view.conflict.hidden=!conflict(o);
    updateRecords(view,o);
  }
  for (const o of ordered.filter(o=>unitTypes.has(o.type))) {
    const view=views.get(o.id);
    const kids=descendants(o);
    const issues=kids.filter(c=>statusOf(c)==='issue');
    const unable=kids.filter(c=>statusOf(c)==='unable_to_verify');
    const pending=kids.filter(c=>statusOf(c)==='unreviewed'&&needsSeparateReview(c));
    const summary=[
      [issues,ui.childIssues,'problem'],[unable,ui.childUnable,''],[pending,ui.childPending,'']
    ].filter(([items])=>items.length && (items!==pending || statusOf(o)==='approved'));
    view.warning.replaceChildren(...summary.map(([items,label,cls])=>
      button(label(items.length),()=>jumpTo(items[0]),cls)));
    view.warning.hidden=summary.length===0;
  }
  const aggregate=Object.entries({total:ordered.length,...stats});
  $('statistics').replaceChildren(...aggregate.map(([k,v])=>node('span',`${ui[k]} ${v}`)));
  $('meter').max=ordered.length;
  $('meter').value=ordered.length-stats.unreviewed;
  $('meter').setAttribute('aria-label',`${$('meter').value} / ${ordered.length}`);
}
function descendants(o) {
  return children(o).flatMap(c=>[c,...descendants(c)]);
}
function updateRecords(view,o) {
  const recs=liveRecords(o.id,true);
  const signature=recs.map(r=>r.record_id).join();
  if (view.recordSignature===signature) return;
  view.recordSignature=signature;
  view.records.hidden=!recs.length;
  view.records.replaceChildren(node('summary',`${ui.currentRecords} (${recs.length})`));
  for (const r of recs) {
    const heading=[ui[r.status],r.issue_code?local(codes[r.issue_code]):'',r.reviewer??'',r.interface_language].filter(Boolean).join(' · ');
    block(view.records,heading,r.note||r.recorded_at);
    if (r.changes.length) {
      const changes=node('details');
      changes.append(node('summary',ui.change));
      changes.addEventListener('toggle',()=>{
        if (changes.open && changes.childElementCount===1) changes.append(node('pre',fmt(r.changes)));
      });
      view.records.append(changes);
    }
  }
}
function setCollapsed(view,on) {
  if (!view.toggle) return;
  view.body.hidden=on;
  view.toggle.textContent=on?ui.expand:ui.collapse;
  view.toggle.setAttribute('aria-expanded',String(!on));
}
const issueType=o=>({
  teaching_link:'teaching_link',table:'table_structure',formula:'formula_structure',
  informative_image:'image_relationship',module_badge:'badge',instructional_note:'instructional_note'
})[o.type]??'other';
function makeActions(o,view) {
  const actions=node('div',null,view.primary?'actions':'actions element-actions');
  const specs=[
    ['approve',ui.approve,()=>approveCard(o,view),'pass'],
    ['issue',ui.issue,()=>openIssue(o,issueType(o)),'problem'],
    ['unable',ui.unable,()=>openUnable(o),''],
  ];
  if (o.text_kk!==undefined || o.cells) specs.push(['ocr',ui.ocr,()=>openIssue(o,'ocr_character'),'']);
  for (const [id,label,action,cls] of specs) {
    const b=button(label,action,cls);
    b.dataset.action=id;
    actions.append(b);
  }
  return actions;
}
const roles={
  lesson_header:['课题','Сабақ тақырыбы'],lesson_objective:['课程说明','Сабақ мақсаты'],
  lesson_number:['课次','Сабақ нөмірі'],lesson_title:['课名','Сабақ атауы'],
  lesson_context:['主题','Ортақ тақырып'],lesson_type_badge:['课型标签','Сабақ түрінің белгісі'],
  running_header:['页眉','Бет тақырыбы'],illustration_caption:['插图文字','Сурет жазуы'],
  lesson_closing_prompt:['课末提示','Сабақ соңындағы нұсқау']
};
function renderCard(o,parent) {
  const primary=!byId.get(o.id).parent;
  const card=node('article',null,primary?'review-card':'review-element');
  card.dataset.objectId=o.id;
  card.dataset.type=o.type;
  card.dataset.role=o.role??'';
  const head=node('header',null,'card-head');
  head.tabIndex=-1;
  const title=roles[o.role]?local(roles[o.role]):o.subtask_label??(o.type==='page'?ui.pageReview:primary?label(o):nameOf(o.type));
  const heading=node(primary?'h3':'h4',title);
  const status=node('span',null,'state');
  const body=node('div',null,'card-body');
  const content=node('div',null,'card-content');
  const form=node('form',null,'review-form');
  form.hidden=true;
  const recordsPanel=node('details',null,'card-records');
  recordsPanel.hidden=true;
  const warning=node('div',null,'child-warning');
  warning.hidden=true;
  const conflictPanel=node('div',ui.conflict,'conflict');
  conflictPanel.hidden=true;
  const view={card,head,body,form,records:recordsPanel,status,conflict:conflictPanel,warning,primary};
  views.set(o.id,view);
  const tools=node('div',null,'card-head-tools');
  tools.append(status);
  if (primary) {
    const toggle=button('',()=>keepPosition(()=>setCollapsed(view,!body.hidden)),'subtle');
    view.toggle=toggle;
    tools.append(toggle);
    setCollapsed(view,false);
  }
  head.append(heading,tools);
  if (primary) {
    const nums=[...new Set(o.page_refs.map(r=>r.pdf_page))];
    heading.append(node('small',`PDF ${nums.join(' · ')}`));
  }
  renderContent(content,o,view);
  if (unitTypes.has(o.type)) content.append(node('p',ui.protected,'caption'));
  body.append(content);
  const sub=children(o);
  if (sub.length) {
    const branch=node('div',null,'review-children');
    for (const child of sub) renderCard(child,branch);
    body.append(branch);
  }
  card.append(head,warning,conflictPanel,body);
  if (primary) card.append(makeActions(o,view));
  else {
    const controls=node('details',null,'element-controls');
    controls.append(node('summary',ui.elementReview),makeActions(o,view));
    card.append(controls);
  }
  card.append(form,recordsPanel);
  parent.append(card);
}
function renderCards() {
  const root=$('cards');
  for (const group of groups) {
    const region=node('div',null,'page-group');
    region.dataset.pdfPage=group.pdf;
    region.append(node('h3',`PDF ${group.pdf} · ${ui.printed} ${pages.get(group.pdf).printed_page}`,'page-heading'));
    for (const o of group.roots) renderCard(o,region);
    group.region=region;
    root.append(region);
  }
}
function matchesFilter(o,key) {
  if (key==='all') return true;
  if (key==='ocr') return Boolean(o.ocr_suggestion_ids?.length);
  if (key==='visual') return visualKinds.includes(o.type);
  if (key==='teaching_link') return o.type===key;
  return statusOf(o)===key;
}
function applyFilter() {
  const key=$('filter').value;
  $('apply-filter').hidden=key==='all';
  function visible(o) {
    const related=children(o).map(visible).some(Boolean);
    const shown=related||matchesFilter(o,key);
    const view=views.get(o.id);
    view.card.hidden=!shown;
    if (key!=='all' && related) setCollapsed(view,false);
    return shown;
  }
  let first=null;
  for (const group of groups) {
    const shown=group.roots.filter(o=>visible(o));
    group.region.hidden=!shown.length;
    first??=shown[0];
  }
  $('no-cards').hidden=Boolean(first);
  return first;
}
function listFilter() {
  $('review-tail').style.height='';
  const first=applyFilter();
  if (first) jumpTo(first);
  else setScroll(narrow()?window.scrollY+scroller.getBoundingClientRect().top:0);
}
function focusScan(o,p=pageOf(o),center=true,force=false) {
  if (!force && active===o && pdf===p) return;
  if (draw && draw.ctx.pdf!==p) clearDraw();
  active=o;
  pdf=p;
  $('page').value=String(p);
  drawSheet(center);
}
function manualScan(o,p,center=true) {
  alignedTop=scrollY();
  focusScan(o,p,center,true);
}
function readingLine() {
  return (narrow()?0:scroller.getBoundingClientRect().top)+54;
}
function atLine() {
  const y=readingLine()+1;
  function find(items) {
    let previous;
    for (const o of items) {
      const view=views.get(o.id);
      if (view.card.hidden) continue;
      const rect=view.card.getBoundingClientRect();
      if (rect.top>y) return previous??o;
      if (rect.bottom>y) {
        if (!view.body.hidden) {
          const kids=children(o);
          const first=kids.find(c=>!views.get(c.id).card.hidden);
          if (first && views.get(first.id).card.getBoundingClientRect().top<=y) {
            const hit=find(kids);
            const box=hit&&views.get(hit.id).card.getBoundingClientRect();
            if (box && box.top<=y && box.bottom>y) return hit;
          }
        }
        return o;
      }
      previous=o;
    }
    return previous;
  }
  const visible=groups.filter(g=>!g.region.hidden);
  const group=visible.find(g=>g.region.getBoundingClientRect().bottom>y)??visible.at(-1);
  return group&&find(group.roots);
}
function syncScroll() {
  if (scrollFrame) return;
  scrollFrame=requestAnimationFrame(()=>{
    scrollFrame=0;
    if (scrollY()===alignedTop || (draw && !draw.done)) return;
    if (narrow() && scroller.getBoundingClientRect().top>readingLine()+80) return;
    alignedTop=null;
    const o=atLine();
    if (!o || o===active) return;
    focusScan(o,o.page_refs.some(r=>r.pdf_page===pdf)?pdf:pageOf(o));
  });
}
function jumpTo(o,p=pageOf(o),center=true) {
  const item=byId.get(o.id);
  const view=views.get(o.id);
  if (view.card.closest('[hidden]')) {
    $('filter').value='all';
    applyFilter();
  }
  for (let parent=item.parent;parent;parent=parent.parent) setCollapsed(views.get(parent.o.id),false);
  if (view.card.hidden) return;
  setScroll(scrollY()+view.head.getBoundingClientRect().top-readingLine());
  highlighted?.classList.remove('jumped');
  view.head.classList.add('jumped');
  highlighted=view.head;
  clearTimeout(highlightTimer);
  highlightTimer=setTimeout(()=>view.head.classList.remove('jumped'),1350);
  focusScan(o,p,center,true);
}
function saveReview(text=ui.saved) {
  persist();
  keepPosition(refreshStates);
  message(text);
}
function sourcePage(o) {
  return o.page_refs.some(r=>r.pdf_page===pdf)?pdf:pageOf(o);
}
function approveCard(o,view) {
  const p=sourcePage(o);
  approveOne(o,p);
  const children=descendants(o);
  if ($('auto-collapse').checked && view.primary &&
      state(o)==='approved' && !view.editor &&
      !children.some(c=>['issue','unable_to_verify'].includes(state(c))||views.get(c.id).editor)) {
    keepPosition(()=>setCollapsed(view,true));
  }
  saveReview();
}
function editorContext(o) {
  const view=views.get(o.id);
  return {o,view,pdf:sourcePage(o),cell:view.cell};
}
function openIssue(o,initial='other',ctx=editorContext(o),pageLevel=false) {
  manualScan(o,ctx.pdf,false);
  const panel=editor(ctx,pageLevel?ui.missing:ui.issue,()=>{
    const code=get(ctx,'issue-kind')?.value??'missing_region';
    const note=get(ctx,'note').value;
    try {
      const changes=issueChanges(ctx,code);
      const cell=ctx.cell;
      const extra={pdf_page:ctx.pdf,issue_code:code,note,changes};
      if (code==='translation_zh') extra.original_auxiliary_translation=aux(cell?.id??o.id)??null;
      if (cell) {
        extra.source_locations=cell.page_refs;
        extra.cell_id=cell.id;
        extra.original_cell=cell;
      }
      if (pageLevel) {
        extra.report_kind='page_omission';
        extra.omission_region=ctx.box??null;
        extra.source_locations=ctx.box?[{...o.page_refs[0],bbox:ctx.box}]:o.page_refs;
      }
      append(o,'issue',extra);
      saveReview();
      if (pageLevel) drawSheet(false);
      return true;
    } catch(e) { message(e.message,true); return false; }
  });
  const fields=node('div');
  if (!pageLevel) {
    const pairs=Object.entries(codes).filter(([k])=>lang==='zh'||k!=='translation_zh').map(([k,v])=>[k,local(v)]);
    const sel=selectField(panel,'issue-kind',ui.kind,pairs,initial);
    sel.onchange=()=>setFields(fields,sel.value,ctx);
  }
  panel.append(fields);
  setFields(fields,pageLevel?'missing_region':initial,ctx);
  field(panel,'note',ui.issueNote,'textarea');
  revealEditor(ctx);
}
function revealEditor(ctx) {
  const heading=ctx.view.form.firstElementChild;
  const rect=heading.getBoundingClientRect();
  const bottom=narrow()?innerHeight:scroller.getBoundingClientRect().bottom;
  if (rect.bottom+75>bottom) setScroll(scrollY()+rect.bottom+140-bottom);
}
function openUnable(o) {
  const ctx=editorContext(o);
  manualScan(o,ctx.pdf,false);
  const panel=editor(ctx,ui.unable,()=>{
    append(o,'unable_to_verify',{pdf_page:ctx.pdf,note:get(ctx,'note').value});
    saveReview();
  });
  field(panel,'note',ui.reason,'textarea');
  revealEditor(ctx);
}
function clearDraw() {
  draw=null;
  $('cancel-draw').hidden=true;
  $('selection').hidden=true;
  $('draw-hint').replaceChildren();
  $('sheet').classList.remove('drawing');
}
function startDraw(mode,ctx) {
  clearDraw();
  focusScan(ctx.o,ctx.pdf,mode==='boundary',true);
  draw={mode,ctx,anchor:null,done:false};
  $('sheet').classList.add('drawing');
  $('cancel-draw').hidden=false;
  const hint=$('draw-hint');
  hint.textContent=mode==='omission'?ui.drag:ui.redraw;
  if (mode==='omission') {
    hint.append(' ',button(ui.pageOnly,()=>{
      clearDraw();
      jumpTo(ctx.o,ctx.pdf,false);
      openIssue(ctx.o,'missing_region',ctx,true);
    }));
  }
}
const sheet=$('sheet');
function coords(e) {
  const b=sheet.getBoundingClientRect();
  const p=pages.get(draw.ctx.pdf);
  return [
    Math.round(Math.min(p.width,Math.max(0,(e.clientX-b.left)*p.width/b.width))),
    Math.round(Math.min(p.height,Math.max(0,(e.clientY-b.top)*p.height/b.height)))
  ];
}
function pointerBox(e) {
  const [x,y]=draw.anchor;
  const [xx,yy]=coords(e);
  return [Math.min(x,xx),Math.min(y,yy),Math.max(x,xx),Math.max(y,yy)];
}
sheet.addEventListener('pointerdown',e=>{
  if (!draw || draw.done || e.button!==0) return;
  e.preventDefault();
  draw.anchor=coords(e);
  sheet.setPointerCapture(e.pointerId);
});
sheet.addEventListener('pointermove',e=>{
  if (!draw?.anchor) return;
  $('selection').hidden=false;
  setBox($('selection'),pointerBox(e),pages.get(draw.ctx.pdf));
});
sheet.addEventListener('pointerup',e=>{
  if (!draw?.anchor) return;
  const b=pointerBox(e);
  const {mode,ctx}=draw;
  draw.anchor=null;
  if (!validBbox(b,pages.get(ctx.pdf)) || b[2]-b[0]<4 || b[3]-b[1]<4) {
    $('selection').hidden=true;
    return;
  }
  ctx.box=b;
  draw.done=true;
  $('sheet').classList.remove('drawing');
  $('draw-hint').textContent=mode==='omission'?ui.selectedRegion:'';
  $('selection').hidden=false;
  setBox($('selection'),b,pages.get(ctx.pdf));
  if (mode==='boundary') get(ctx,'new-bbox').value=b.join(', ');
  else {
    jumpTo(ctx.o,ctx.pdf,false);
    openIssue(ctx.o,'missing_region',ctx,true);
  }
});
sheet.addEventListener('pointercancel',()=>{
  if (draw && !draw.done) {
    draw.anchor=null;
    $('selection').hidden=true;
  }
});
$('cancel-draw').onclick=clearDraw;
$('omission').onclick=()=>{
  const page=byId.get(pages.get(pdf).id).o;
  startDraw('omission',editorContext(page));
};
$('page').onchange=e=>{
  const p=Number(e.target.value);
  const group=groups.find(g=>g.pdf===p);
  jumpTo(group.roots[0],p);
};
$('zoom').onchange=()=>drawSheet(true);
$('elements').onchange=()=>drawSheet(false);
$('module-jump').onchange=e=>{
  const item=byId.get(e.target.value);
  if (item) jumpTo(item.o);
  e.target.value='';
};
$('filter').onchange=listFilter;
$('apply-filter').onclick=listFilter;
$('to-top').onclick=()=>{
  $('review-tail').style.height='';
  setScroll(narrow()?Math.max(0,window.scrollY+$('review-heading').getBoundingClientRect().top):0);
  const group=groups.find(g=>!g.region.hidden);
  const first=group?.roots.find(o=>!views.get(o.id).card.hidden);
  if (first) focusScan(first);
};
scroller.addEventListener('scroll',()=>{if(!narrow())syncScroll();},{passive:true});
window.addEventListener('scroll',()=>{if(narrow())syncScroll();},{passive:true});

const extraLabels={
  zh:{upper:'上行',lower:'下行',operator:'运算符',result:'结果',equivalence:'等值换算',invalidLink:'关联两端必须为不同对象。',rowSpan:'跨行数',colSpan:'跨列数'},
  kk:{upper:'Жоғарғы жол',lower:'Төменгі жол',operator:'Амал таңбасы',result:'Нәтиже',equivalence:'Тең мәнді түрлендіру',invalidLink:'Байланыс екі бөлек нысанды қосуы керек.',rowSpan:'Қамтитын жол саны',colSpan:'Қамтитын баған саны'}
};
Object.assign(ui,extraLabels[lang]);
for (const el of document.querySelectorAll('[data-i]')) el.textContent=ui[el.dataset.i];
$('title').textContent=L.title_kk;
$('title').lang='kk';
$('course-meta').textContent=lang==='zh'? `四年级数学 · 第 1 册 · 第 1 课 · PDF ${L.pdf_page_range.join('–')}` :
  `Математика · 4-сынып · 1-бөлім · 1-сабақ · PDF ${L.pdf_page_range.join('–')}`;
$('translated-title').textContent=translations.title?`${translations.title} · ${translations.theme}`:L.context_kk;
$('reviewer').setAttribute('aria-label',ui.reviewer);
optionSet($('page'),D.pages.map(p=>[String(p.pdf_page),`PDF ${p.pdf_page} · ${ui.printed} ${p.printed_page}`]));
optionSet($('filter'),filterOptions.map(([v,key])=>[v,ui[key]]));
optionSet($('module-jump'),[['',ui.select],...L.content_order.map(id=>units.get(id)).filter(o=>unitTypes.has(o.type)).map(o=>[o.id,label(o)])]);
for (const t of ['module','instructional_note','text','informative_image','formula','table','module_badge','other']) {
  const item=node('span',nameOf(t));
  item.dataset.type=t;
  $('legend').append(item);
}
readDraft();
$('draft').textContent=durable?ui.draft:ui.noDraft;
renderCards();
refreshStates();
focusScan(groups[0].roots[0]);
})();
