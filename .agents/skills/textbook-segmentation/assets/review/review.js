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
    draft:'浏览器草稿仅保存在本机。请导出 JSON 留存。',noDraft:'此浏览器无法保存本地草稿。请在关闭前导出 JSON。',saved:'已保存审核。',skipped:'已跳过，审核状态保留。',exported:'已发起 JSON 下载。请确认文件已保存。',exportError:'无法发起下载。',imported:'导入完成，原有审核历史已保留。',importError:'导入失败。请使用与本课及当前数据版本匹配的审核 JSON。',conflict:'存在互相冲突的审核或修正。导出将保留各方记录，需人工裁定。',notes:'审核备注',kind:'问题类型',corrected:'建议修正内容（选填）',rawText:'哈萨克语原文',translation:'中文参考翻译',advanced:'高级信息',children:'所含内容',currentRecords:'当前审核记录',known:'人工复核提示',suggestions:'待审核的识别修正',showPage:'查看位置',printed:'印刷',moduleNumber:'任务',missing:'遗漏内容',drag:'在原图上拖动框选，或直接按页报告。',pageOnly:'按页报告',selectedRegion:'已框选遗漏区域。',possible:'可能的内容类型',save:'保存并继续',newType:'修正后的类型',parent:'修正后的归属',order:'同级阅读顺序位置（从 1 开始）',bbox:'新切割框（像素坐标 x0, y0, x1, y1）',redraw:'在原图上重新框选',badBox:'坐标无效，请重新框选或输入有效坐标。',change:'建议操作',keep:'保留当前值',replace:'修改',remove:'删除关联',supports:'提供知识或方法',uses_as_material:'直接使用材料',whichPage:'所在页',noEdit:'发现的问题可在备注中描述。',cell:'已选单元格',reason:'原因（选填）',issueNote:'问题说明（选填）',linked:'打开对象',select:'请选择',root:'本课',record:'记录',blank:'空白',printedVersion:'印刷排法',structure:'结构化说明',region:'位置',suggestionConfirm:'通过会记录对本对象所列修正建议的确认。',protected:'整体通过会保留带疑点、修正建议或既有问题的子项。',partial:'部分子项仍需单独审核。',draftError:'本地草稿无法恢复。可导入已导出的记录。',pageAudit:'这里可确认该页的切割覆盖，也可直接报告遗漏。',sourceOCR:'原始 OCR / 已有校对',badgeScope:'标签作用范围',unsure:'待确认',duplicate:'导入文件里同一记录 ID 对应不同内容。',
  },
  kk:{
    reviewer:'Тексеруші (міндетті емес)',import:'Жазбаларды импорттау',export:'JSON жазбаларын экспорттау',scan:'Оқулықтың түпнұсқа беті',review:'Тексерілетін нысан',page:'Бет',zoom:'Масштаб',elements:'Ішкі жиектер',omission:'Бетте қалып қойған мазмұн бар',cancel:'Бас тарту',module:'Тапсырма',filter:'Сүзгі',object:'Нысан',prev:'Алдыңғы',next:'Келесі',nextUnreviewed:'Келесі тексерілмеген нысан',approve:'Мақұлдау',issue:'Ақау бар',unable:'Анықтай алмадым',skip:'Өткізіп жіберу',bulk:'Бөлім мен күмәнсіз ішкі нысандарды мақұлдау',ocr:'Мәтінде қате бар',
    total:'Нысан',unreviewed:'Тексерілмеген',approved:'Мақұлданған',unable_to_verify:'Анықталмаған',all:'Барлығы',ocrOnly:'OCR және құрылым түзетулері',visual:'Сурет, кесте немесе өрнек',linkOnly:'Оқу байланыстары',none:'Бұл сүзгіде нысан жоқ',noPending:'Бұл сүзгіде басқа тексерілмеген нысан жоқ.',
    draft:'Нобай осы браузерде ғана сақталады. JSON файлын экспорттаңыз.',noDraft:'Осы браузерде нобайды сақтау мүмкін емес. Жабар алдында JSON файлын экспорттаңыз.',saved:'Тексеру жазбасы сақталды.',skipped:'Өткізілді, тексеру күйі сақталды.',exported:'JSON жүктеп алу басталды. Файлдың сақталғанын тексеріңіз.',exportError:'Жүктеп алу басталмады.',imported:'Импорт аяқталды, бұрынғы жазбалар сақталды.',importError:'Импортталмады. Осы сабақ пен деректер нұсқасына сәйкес JSON файлын таңдаңыз.',conflict:'Тексеру жазбаларында қайшылық бар. Экспортта барлық нұсқа сақталады, шешімді адам қабылдайды.',notes:'Тексерушінің ескертпесі',kind:'Ақау түрі',corrected:'Ұсынылатын түзету (міндетті емес)',rawText:'Қазақша түпнұсқа',translation:'Қытайша аударма',advanced:'Қосымша деректер',children:'Ішкі мазмұн',currentRecords:'Ағымдағы жазбалар',known:'Тексеруге арналған ескертпе',suggestions:'Тексеруді қажет ететін түзетулер',showPage:'Орнын көру',printed:'Баспа беті',moduleNumber:'Тапсырма',missing:'Қалып қойған мазмұн',drag:'Түпнұсқадан аймақты белгілеңіз немесе бүкіл бетке ескерту қалдырыңыз.',pageOnly:'Бүкіл бетке ескерту',selectedRegion:'Қалып қойған аймақ белгіленді.',possible:'Ықтимал мазмұн түрі',save:'Сақтау және жалғастыру',newType:'Түзетілген түрі',parent:'Тиесілі жаңа нысан',order:'Оқу ретіндегі орны (1-ден бастап)',bbox:'Жаңа жақтау (пиксельмен x0, y0, x1, y1)',redraw:'Түпнұсқада аймақты қайта белгілеу',badBox:'Координаттар жарамсыз. Аймақты қайта белгілеңіз немесе дұрыс координаттарды енгізіңіз.',change:'Ұсынылатын әрекет',keep:'Сақтау',replace:'Өзгерту',remove:'Байланысты жою',supports:'Білім не әдіспен қолдайды',uses_as_material:'Материалды тікелей пайдаланады',whichPage:'Орналасқан бет',noEdit:'Ақауды ескертпеде сипаттауға болады.',cell:'Таңдалған ұяшық',reason:'Себебі (міндетті емес)',issueNote:'Ақау сипаттамасы (міндетті емес)',linked:'Нысанды ашу',select:'Таңдаңыз',root:'Осы сабақ',record:'Жазба',blank:'Бос',printedVersion:'Баспа нұсқасы',structure:'Құрылымдық сипаттама',region:'Орналасуы',suggestionConfirm:'Мақұлдағанда осы нысанның түзету ұсыныстары расталады.',protected:'Тұтас мақұлдау кезінде күмәні, түзету ұсынысы немесе ақауы бар ішкі нысандардың күйі сақталады.',partial:'Кей ішкі нысанды жеке тексеру керек.',draftError:'Жергілікті нобай ашылмады. Бұрын экспортталған жазбаларды импорттай аласыз.',pageAudit:'Бет мазмұнының толық қамтылуын тексеріңіз немесе қалып қойған аймақ туралы хабарлаңыз.',sourceOCR:'Бастапқы OCR / бұрынғы түзету',badgeScope:'Белгінің қолданылу аясы',unsure:'Тексеру керек',duplicate:'Бір жазба идентификаторы импортта әртүрлі мазмұнға берілген.',
  }
}[lang];
const types = {
  page:'Page', module:'Module', instructional_note:'Instructional Note', subtask:'Subtask',
  example:'Example', other:'Other', text:'Text', formula:'Formula', table:'Table',
  informative_image:'Informative Image', badge:'Badge', module_number:'Module Number',
  module_badge:'Module Badge', instructional_note_badge:'Instructional Note Badge',
  subtask_number:'Subtask Number', teaching_link:'Teaching Link'
};
const codes = {
  subtask_number_error:['子题编号错误','Тармақ нөмірінің қатесі'],
  missing_region:['漏切','Қалып қойған аймақ'],extra_region:['多切','Артық бөлінген аймақ'],
  boundary:['边界错误','Жақтау қатесі'],assignment:['元素归属错误','Мазмұнның тиесілігі'],
  element_type:['内容类型错误','Мазмұн түрінің қатесі'],badge:['Badge 错误','Белгі қатесі'],
  instructional_note:['Instructional Note 错误','Оқу ескертпесінің қатесі'],teaching_link:['教学关联错误','Оқу байланысының қатесі'],
  ocr_character:['OCR 字符错误','OCR таңба қатесі'],ocr_linebreak:['断词或换行错误','Тасымал не жол үзілісі'],
  formula_structure:['公式错误','Өрнек қатесі'],table_structure:['表格结构错误','Кесте құрылымының қатесі'],
  image_relationship:['信息性图片理解错误','Суреттегі байланысты түсіндіру қатесі'],reading_order:['阅读顺序错误','Оқу реті қатесі'],
  cross_page:['跨页问题','Бетаралық ақау'],
  translation_zh:['中文辅助翻译错误','Қытайша аударма қатесі'],other:['其他','Басқа']
};
const local = pair => pair[lang==='zh'?0:1];
const nameOf = code => types[code] ?? code;
const linkRoles = {
  supports:[local(['提供方法或知识','Әдіс не білім беретін нысан']),local(['受支持的任务','Қолдау алатын тапсырма'])],
  uses_as_material:[local(['使用者','Пайдаланатын нысан']),local(['引用材料','Пайдаланылатын материал'])]
};
const byId = new Map();
const ordered = [];
const pages = new Map(D.pages.map(p => [p.pdf_page,p]));
const revision = D.review_revision;
const priorPackage = JSON.parse($('prior-review').textContent);
const currentPackage = JSON.parse($('current-review').textContent);
const equivalent = new Set(revision?.equivalent_object_ids ?? []);
const resolved = new Set(revision?.addressed_record_ids ?? []);
const priorObjectIds = new Set(revision?.source_object_ids ?? []);
const ancestry = new Map(Object.entries(revision?.ancestors ?? {}).map(([version, info]) =>
  [version, {ids:new Set(info.source_object_ids), equivalent:new Set(info.equivalent_object_ids)}]));
let priorRecords = new Map();
const groupsOnly = new Set(['module','instructional_note','subtask','example']);
const structureCodes = new Set(['missing_region','extra_region','boundary','assignment','element_type',
  'reading_order','badge','instructional_note','formula_structure','table_structure','teaching_link','cross_page','other']);

const recordStates = ['approved','issue','unable_to_verify'];
const visualKinds = ['informative_image','table','formula'];
const filterOptions = [
  ['all','all'],['issue','issue'],['unreviewed','unreviewed'],['unable_to_verify','unable_to_verify'],
  ['visual','visual'],['teaching_link','linkOnly'],['page','pageReview']
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
function latest(items) {
  const superseded = new Set(items.flatMap(r=>r.supersedes));
  return items.filter(r=>!superseded.has(r.record_id)).sort(sortRecords);
}
function liveRecords(id, alsoOmissions=false) {
  return latest(objectRecords(id).filter(r=>alsoOmissions || !omission(r)));
}
function priorFor(id) {
  return latest([...priorRecords.values()].filter(r=>r.object_id===id));
}
function hasContent(o) {
  const kids=children(o);
  const noteBadge=o.instructional_note_badge &&
    !kids.some(c=>c.type==='instructional_note_badge' || c.text_kk===o.instructional_note_badge);
  return o.type==='page' || o.type==='teaching_link' || Boolean(o.text_kk?.trim() || o.cells?.length ||
    o.vertical || o.structured_description || noteBadge || (!kids.length && o.crop_asset_id));
}
const isContainer = o => groupsOnly.has(o.type) || children(o).length > 0;
const structureRecord = (o,r) => r.report_kind==='structure_review' || (!hasContent(o) && r.status!=='approved');
function signature(r) {
  const changes=r.changes??[];
  return canonical([r.status,r.issue_code??null,
    r.status==='approved'?changes.filter(c=>c.op!=='confirm_scan_restoration'):changes]);
}
function conflict(items) {
  return items.some((a,i)=>items.slice(i+1).some(b=>
    a.review_scope===b.review_scope &&
    (a.status!==b.status || (a.issue_code===b.issue_code && a.cell_id===b.cell_id && signature(a)!==signature(b)))));
}
function recordState(items) {
  if (conflict(items) || items.some(r=>r.status==='issue')) return 'issue';
  if (items.some(r=>r.status==='unable_to_verify')) return 'unable_to_verify';
  return items.some(r=>r.status==='approved' && r.review_scope==='textbook')?'approved':'unreviewed';
}
function historical(o) {
  return priorFor(o.id).filter(r=>!resolved.has(r.record_id));
}
function equivalentIn(record, id) {
  return (ancestry.get(record.data_version)?.equivalent ?? equivalent).has(id);
}
function contentState(o) {
  const current=liveRecords(o.id,true).filter(r=>!structureRecord(o,r));
  const retained=historical(o).filter(r=>!structureRecord(o,r) &&
    (equivalentIn(r,o.id) || r.status==='issue'));
  return recordState(current.length?[...current,...retained.filter(r=>r.status==='issue')]:retained);
}
function structureState(o) {
  const current=liveRecords(o.id).filter(r=>structureRecord(o,r));
  const retained=historical(o).filter(r=>structureRecord(o,r));
  const status=recordState([...current,...retained]);
  return status==='unreviewed' && !o.structure_recheck?'neutral':status;
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
function label(o) {
  const owner=byId.get(o.id)?.owner;
  const mod=owner && byId.get(owner).o.module_number;
  if (o.type==='module') return `${nameOf(o.type)} ${o.module_number}`;
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
    localStorage.setItem(key,JSON.stringify({...manifest,stream,reviewer:$('reviewer').value,records:[...records.values()],prior_records:[...priorRecords.values()]}));
    durable=true;
  } catch(e) { durable=false; }
  $('draft').textContent=durable?ui.draft:ui.noDraft;
}
function message(text='',error=false) {
  $('message').textContent=text;
  $('message').dataset.error=error;
}

function validRecord(r, version=manifest.data_version) {
  if (!r || typeof r.record_id!=='string' || typeof r.reviewer_stream_id!=='string' ||
      !(version===manifest.data_version?recordables:ancestry.get(version)?.ids ?? priorObjectIds).has(r.object_id) || r.textbook_id!==manifest.textbook_id ||
      r.lesson_id!==manifest.lesson_id || r.data_version!==version || r.schema_version!==manifest.schema_version ||
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
function mergeRecords(existing, incoming, version, historical=false) {
  if (!Array.isArray(incoming)) throw Error(ui.importError);
  const next=new Map(existing);
  for (const r of incoming) {
    const recordVersion=historical?r?.data_version:version;
    if ((historical && recordVersion!==revision.source_version && !ancestry.has(recordVersion)) ||
        !validRecord(r,recordVersion)) throw Error(ui.importError);
    const previous=next.get(r.record_id);
    if (previous && canonical(previous)!==canonical(r)) throw Error(ui.duplicate);
    next.set(r.record_id,r);
  }
  for (const r of next.values()) {
    if (r.supersedes.some(id=>{
      const old=next.get(id);
      return id===r.record_id || old && (old.object_id!==r.object_id || old.reviewer_stream_id!==r.reviewer_stream_id ||
        old.data_version!==r.data_version || old.report_kind!==r.report_kind ||
        old.review_scope!==r.review_scope || old.recorded_at>r.recorded_at);
    })) throw Error(ui.importError);
  }
  return next;
}
function merge(f) {
  if (!f || f.schema_version!==manifest.schema_version || f.textbook_id!==manifest.textbook_id ||
      f.lesson_id!==manifest.lesson_id) throw Error(ui.importError);
  if (revision && (f.data_version===revision.source_version || ancestry.has(f.data_version))) {
    const previous=mergeRecords(priorRecords,f.records,f.data_version);
    priorRecords=mergeRecords(previous,f.prior_records??[],null,true);
    return;
  }
  if (f.data_version!==manifest.data_version) throw Error(ui.importError);
  const next=mergeRecords(records,f.records,manifest.data_version);
  const prior=f.prior_records??[];
  if (!Array.isArray(prior) || (prior.length && !revision)) throw Error(ui.importError);
  if (revision) priorRecords=mergeRecords(priorRecords,prior,null,true);
  records=next;
}
function exportRecords() {
  try {
    const dump={...manifest,exported_at:new Date().toISOString(),export_interface_language:lang,records:[...records.values()].sort(sortRecords),
      ...(priorRecords.size?{prior_records:[...priorRecords.values()].sort(sortRecords)}:{})};
    const url=URL.createObjectURL(new Blob([JSON.stringify(dump,null,2)],{type:'application/json'}));
    const a=node('a');
    a.href=url;
    a.download=`${L.id.replace(/[^a-zA-Z0-9_-]/g,'_')}_review_records_${lang}_${new Date().toISOString().replace(/[:.]/g,'-')}.json`;
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
  const fields=['type','parent_id','content_order','exercise_input_ids','text_kk','cells','vertical','worked_sequence','structured_description','scope_ids','instructional_note_badge','ocr_evidence'];
  return Object.fromEntries(fields.filter(k=>o[k]!==undefined).map(k=>[k,o[k]]));
}
function append(o,status,extra={}) {
  const report_kind=extra.report_kind ?? 'object_review';
  const id=uid();
  const at=new Date().toISOString();
  const isOmission=report_kind==='page_omission';
  const review_scope=isOmission?'page_omission':extra.issue_code==='translation_zh'?'auxiliary_translation':'textbook';
  const supersedes=isOmission?[]:liveRecords(o.id).filter(r=>
    r.reviewer_stream_id===stream && r.review_scope===review_scope && r.report_kind===report_kind &&
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
const verticalLabels = {
  reconstructed:local(['重建竖式','Қайта құрылған бағандық есеп']),
  source:local(['原书裁图（对照）','Оқулықтан қиынды (салыстыру үшін)']),
  edit:local(['二维布局修正（JSON）','Екі өлшемді орналасуды түзету (JSON)']),
  invalid:local(['请输入有效的二维布局 JSON。','Екі өлшемді орналасудың жарамды JSON деректерін енгізіңіз.'])
};

function renderContent(div,o,view) {
  if (o.type==='page') block(div,null,ui.pageAudit);
  if (o.instructional_note_badge && o.instructional_note_badge!==o.text_kk &&
      !children(o).some(c=>c.type==='instructional_note_badge' || c.text_kk===o.instructional_note_badge)) {
    block(div,null,o.instructional_note_badge,'caption');
  }
  if (o.vertical) {
    div.append(node('div',verticalLabels.reconstructed,'caption'));
    renderVertical(div,o.vertical,o.text_kk);
  } else block(div,null,o.text_kk,o.type==='formula'?'equations':'');
  if (aux(o.id) && hasContent(o) && o.type!=='teaching_link') block(div,ui.translation,aux(o.id),'translation');
  if (o.scope_ids) {
    const scopes=o.scope_ids.map(id=>byId.get(id)?.o).filter(Boolean);
    block(div,ui.badgeScope,scopes.map(label).join(' · '));
  }
  const imageId=o.worked_sequence?.crop_asset_id ?? o.crop_asset_id;
  if (imageId) {
    const img=node('img',null,'crop');
    img.loading='lazy';
    const [x,y,r,b]=D.crop_assets[imageId].bbox;
    img.width=r-x;
    img.height=b-y;
    img.src=images[imageId];
    img.alt=`${ui.scan} · ${nameOf(o.type)}`;
    if (o.vertical) div.append(node('div',verticalLabels.source,'caption'));
    div.append(img);
  }
  if (o.worked_sequence) {
    block(div,null,o.worked_sequence.description_kk);
    block(div,ui.translation,aux(o.id+'#worked_sequence'),'translation');
  }
  if (o.structured_description) block(div,null,o.structured_description.description_kk);
  if (o.cells) renderTable(div,o,view);
  if (o.type==='teaching_link') {
    block(div,ui.kind,ui[o.relationship]);
    block(div,ui.rawText,o.rationale_kk);
    block(div,ui.translation,aux(o.id),'translation');
    const nav=node('div',null,'toolbar');
    const roles=linkRoles[o.relationship];
    for (const [i,id] of [o.from_id,o.to_id].entries()) {
      const tgt=byId.get(id).o;
      nav.append(button(`${roles[i]} · ${label(tgt)}`,()=>jumpTo(tgt)));
    }
    div.append(nav);
  }
  if (new Set(o.page_refs.map(r=>r.pdf_page)).size>1) {
    const nav=node('div',null,'pager');
    for (const p of new Set(o.page_refs.map(r=>r.pdf_page))) nav.append(button(`PDF ${p}`,()=>manualScan(o,p)));
    div.append(nav);
  }
  const flags=(o.review_flags??[]).filter(flag=>flag.requires_confirmation!==false &&
    !['source_blank','border_overlap'].includes(flag.code));
  if (flags.length) {
    const item=node('div',null,'flag');
    block(item,ui.known,[...new Set(flags.map(f=>f.description_kk))].join('\n'));
    const zh=flags.map(f=>aux(o.id+'#'+f.code)).filter(Boolean);
    if (zh.length) block(item,null,[...new Set(zh)].join('\n'),'translation');
    div.append(item);
  }
}
function renderVerticalGrid(layout,transcription) {
  const grid=node('div',null,'vertical-grid');
  grid.setAttribute('role','img');
  grid.setAttribute('aria-label',transcription);
  const positions=new Map(layout.columns.map((column,i)=>[column.id,i+1]));
  grid.style.gridTemplateColumns=layout.columns.map(column=>'place' in column?'1ch':'max-content').join(' ');
  grid.style.marginInlineStart=`${layout.indent_em??0}em`;
  for (const [i,row] of layout.rows.entries()) {
    for (const cell of row.cells) {
      const text=cell.kind==='unit'?layout.units[cell.value]:cell.value;
      const item=node('span',text,`vertical-cell vertical-${cell.kind}`);
      item.style.gridRow=String(i+1);
      item.style.gridColumn=`${positions.get(cell.column)} / span ${cell.span??1}`;
      grid.append(item);
    }
  }
  return grid;
}

function renderVertical(parent,v,transcription) {
  const figure=node('div',null,'vertical-figure');
  if (v.expression_kk) figure.append(node('div',v.expression_kk,'formula-caption'));
  if (v.layout) {
    figure.append(renderVerticalGrid(v.layout,transcription));
    parent.append(figure);
    return;
  }
  const d=node('div',null,'vertical');
  const row=(value,operator,token,suffix='')=>{
    const match=(value??'').match(/^(?:(.*?[^\d\s])\s+)?(\d[\d ]*)\s+(\S+)$/u);
    const [,prefix='',number=value??'',unit='']=match??[];
    const digits=node('span',null,'amount');
    const at=token ? number.indexOf(token) : -1;
    if (at<0) digits.textContent=number;
    else digits.append(number.slice(0,at),node('strong',token,'marked'),number.slice(at+token.length));
    d.append(node('span',operator,'operator'),node('span',prefix?.trim(),'larger-unit'),
      digits,node('span',unit,'small-unit'),node('span',suffix,'equivalence'));
  };
  row(v.upper,'',v.highlight?.position?.startsWith('upper')?v.highlight.value:undefined);
  row(v.lower,v.operator);
  if (v.result_rule_printed!==false) d.append(node('span'),node('span',null,'rule'),node('span'));
  const suffix=v.result && v.equivalence_kk?.startsWith(v.result)?v.equivalence_kk.slice(v.result.length):'';
  if (v.result==null && v.result_blank_unit) {
    d.append(node('span'),node('span'),node('span'),node('span',v.result_blank_unit,'small-unit'),node('span'));
  } else row(v.result ?? v.equivalence_kk,'',v.highlight?.position?.startsWith('first_digit')?v.highlight.value:undefined,suffix);
  if (v.equivalence_kk && !suffix && v.result && v.equivalence_kk!==v.result) {
    d.append(node('div',v.equivalence_kk,'formula-caption'));
  }
  figure.append(d);
  parent.append(figure);
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
  if (['ocr_character','ocr_linebreak','subtask_number_error'].includes(code)) inputText(originalText(o,cell));
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
    const editing=o.type==='teaching_link';
    if (editing) selectField(panel,'link-action',ui.change,[['replace',ui.replace],['remove',ui.remove]]);
    const candidates=ordered.filter(c=>!['page','teaching_link'].includes(c.type)).map(c=>[c.id,label(c)]);
    const relation=selectField(panel,'link-relation',ui.kind,Object.keys(linkRoles).map(key=>[key,ui[key]]),
      editing?o.relationship:linkOwner(o.id)==='instructional_note'?'supports':'uses_as_material');
    const from=selectField(panel,'link-from','',candidates,editing?o.from_id:o.id);
    const to=selectField(panel,'link-to','',[['',ui.select],...candidates],editing?o.to_id:'');
    const updateRoles=()=>{
      const [origin,target]=linkRoles[relation.value];
      from.previousElementSibling.textContent=origin;
      to.previousElementSibling.textContent=target;
    };
    relation.onchange=updateRoles;
    updateRoles();
    inputText(o.rationale_kk);
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
  } else if (code==='formula_structure' && o.vertical?.layout) {
    field(panel,'vertical-layout',verticalLabels.edit,'textarea').value=JSON.stringify(o.vertical.layout,null,2);
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
function linkOwner(id) {
  return byId.get(byId.get(id)?.owner)?.o.type;
}
function validLinkDirection(from,to,relationship) {
  if (!from || !to || from===to) return false;
  if (relationship==='supports') return linkOwner(from)==='instructional_note' && linkOwner(to)==='module';
  return relationship==='uses_as_material' && linkOwner(from)==='module';
}
function issueChanges(ctx,code) {
  const {o,cell,pdf,box}=ctx;
  const field=name=>get(ctx,name);
  const list=[];
  const value=field('new-value')?.value;
  const put=(target,field,oldValue,newValue,op='replace_value',extra={})=>{
    if (JSON.stringify(oldValue??null)!==JSON.stringify(newValue??null)) list.push(change(op,target,field,oldValue??null,newValue??null,extra));
  };
  if (['ocr_character','ocr_linebreak','subtask_number_error'].includes(code)) {
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
    const action=field('link-action')?.value;
    if (action==='remove') list.push(change('remove_link',o.id,'teaching_links',original(o),null));
    else {
      const from=field('link-from').value;
      const to=field('link-to').value;
      const relationship=field('link-relation').value;
      if (to || o.type==='teaching_link') {
        if (!validLinkDirection(from,to,relationship)) throw Error(ui.invalidLink);
        const next={from_id:from,to_id:to,relationship,rationale_kk:value};
        if (o.type==='teaching_link') {
          put(o.id,'teaching_links',original(o),next,'update_link');
        } else {
          list.push(change('add_link',o.id,'teaching_links',null,next));
        }
      }
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
  } else if (code==='formula_structure' && o.vertical?.layout) {
    let layout;
    try {
      layout=JSON.parse(field('vertical-layout').value);
    } catch {
      throw Error(verticalLabels.invalid);
    }
    if (!layout || !Array.isArray(layout.columns) || !Array.isArray(layout.rows) || !layout.units || !layout.given) {
      throw Error(verticalLabels.invalid);
    }
    put(o.id,'vertical',o.vertical,{...o.vertical,layout},'replace_formula_layout');
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
  if (!list.length && ['boundary','assignment','reading_order','element_type','table_structure','formula_structure','image_relationship','teaching_link','instructional_note','ocr_character','ocr_linebreak','subtask_number_error','badge','translation_zh'].includes(code)) {
    list.push({op:'review_issue',target_id:cell?.id??o.id,issue_code:code});
  }
  return list;
}
const continuousLabels={
  zh:{review:'连续审核',jump:'跳到 Module',toTop:'返回顶部',applyFilter:'刷新结果',
    save:'保存',pageReview:'页面完整性',structureIssue:'报告结构问题',structurePass:'确认结构修订',
    pending:'审核中',neutral:'',historyPending:'旧版记录需对照修订内容复核',detailsLabel:'反馈',
    contentTotal:'内容',pageTotal:'页面完整性',structureTotal:'结构待处理',overall:'审核进度',structurePending:'结构待复核',sync:'同步原图'},
  kk:{review:'Ретімен тексеру',jump:'Module таңдау',toTop:'Басына қайту',applyFilter:'Нәтижені жаңарту',
    save:'Сақтау',pageReview:'Беттің толықтығы',structureIssue:'Құрылым ақауын хабарлау',
    structurePass:'Құрылым түзетуін растау',pending:'Тексеріліп жатыр',neutral:'',
    historyPending:'Алдыңғы жазбаларды түзетілген мәтінмен салыстырыңыз',detailsLabel:'Пікір',
    contentTotal:'Мазмұн',pageTotal:'Беттің толықтығы',structureTotal:'Құрылымды тексеру',overall:'Тексеру барысы',
    structurePending:'Құрылымды қайта тексеру',sync:'Түпнұсқамен синхрондау'}
};
Object.assign(ui,continuousLabels[lang]);
const mobile=matchMedia('(max-width:680px)');
const reviewStatus=new Map();
const ownStatus=new Map();
const structureStatuses=new Map();
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
function refreshStates() {
  const counts=()=>Object.fromEntries(['unreviewed',...recordStates].map(state=>[state,0]));
  const content=counts(), page=counts(), structures=counts();
  for (const o of [...ordered].reverse()) {
    const own=hasContent(o)?contentState(o):'neutral';
    ownStatus.set(o.id,own);
    if (own!=='neutral') (o.type==='page'?page:content)[own]++;
    const structure=isContainer(o)?structureState(o):'neutral';
    structureStatuses.set(o.id,structure);
    if (structure!=='neutral') structures[structure]++;
    const states=[own,structure,...children(o).map(statusOf)].filter(s=>s!=='neutral');
    const status=states.includes('issue')?'issue':states.includes('unable_to_verify')?'unable_to_verify':
      states.some(s=>['unreviewed','pending'].includes(s))?(isContainer(o)?'pending':'unreviewed'):
      states.length?'approved':'neutral';
    reviewStatus.set(o.id,status);
    const view=views.get(o.id);
    view.status.textContent=ui[status]??'';
    view.status.dataset.state=status;
    view.card.dataset.state=status;
    if (view.ownStatus) view.ownStatus.textContent=ui[own];
    if (view.structurePass) {
      view.structurePass.hidden=structure!=='unreviewed' &&
        !liveRecords(o.id).some(r=>r.report_kind==='structure_review' && r.reviewer_stream_id===stream && r.status==='issue');
      view.structureReview.hidden=structure==='neutral'||structure==='approved';
      view.structureLabel.textContent=structure==='unreviewed'?ui.structurePending:`${ui.structurePending} · ${ui[structure]}`;
      (view.structureReview.hidden?view.head:view.structureReview).append(view.structureIssue);
    }
    updateFeedback(view,o);
  }
  const total=Object.values(content).reduce((sum,n)=>sum+n,0);
  const pageCount=Object.values(page).reduce((sum,n)=>sum+n,0);
  const pendingStructure=structures.unreviewed+structures.issue+structures.unable_to_verify;
  const approved=content.approved+page.approved+structures.approved;
  const taskCount=total+pageCount+structures.approved+pendingStructure;
  const lines=[
    `${ui.overall} · ${ui.approved} ${approved}/${taskCount} · ${ui.issue} ${content.issue+page.issue+structures.issue} · ${ui.unable_to_verify} ${content.unable_to_verify+page.unable_to_verify+structures.unable_to_verify} · ${ui.unreviewed} ${content.unreviewed+page.unreviewed+structures.unreviewed}`,
    `${ui.contentTotal} ${content.approved}/${total}`,
    `${ui.pageTotal} ${page.approved}/${pageCount} · ${ui.structureTotal} ${pendingStructure}`
  ];
  const unmatched=latest([...priorRecords.values()]).filter(r=>!recordables.has(r.object_id));
  if (unmatched.length) lines.push(`${ui.historyPending} · ${unmatched.length}`);
  $('statistics').replaceChildren(...lines.map(line=>node('span',line)));
  $('meter').max=Math.max(1,taskCount);
  $('meter').value=approved;
  $('meter').setAttribute('aria-label',`${approved} / ${taskCount}`);
}
function updateFeedback(view,o) {
  const current=liveRecords(o.id,true).filter(r=>r.status!=='approved');
  const previous=priorFor(o.id).filter(r=>r.status!=='approved' || (!equivalentIn(r,o.id) && hasContent(o)));
  const notes=[...new Set([...current,...previous].map(r=>r.note).filter(Boolean))];
  const pending=ownStatus.get(o.id)!=='approved' && previous.some(r=>!equivalentIn(r,o.id) || resolved.has(r.record_id));
  view.feedback.hidden=!notes.length && !pending;
  view.feedback.replaceChildren();
  if (pending) view.feedback.append(node('p',ui.historyPending));
  for (const note of notes) view.feedback.append(node('p',note));
}
const issueType=o=>({
  subtask_number:'subtask_number_error',teaching_link:'teaching_link',table:'table_structure',formula:'formula_structure',
  informative_image:'image_relationship',module_badge:'badge',instructional_note:'instructional_note'
})[o.type]??'other';
function makeActions(o) {
  const actions=node('div',null,'actions element-actions');
  for (const [id,title,act,cls] of [
    ['approve',ui.approve,()=>{append(o,'approved',{pdf_page:sourcePage(o)}); saveReview();},'pass'],
    ['issue',ui.issue,()=>openIssue(o,issueType(o)),'problem'],
    ['unable',ui.unable,()=>openUnable(o),'']
  ]) {
    const control=button(title,act,cls);
    control.dataset.action=id;
    actions.append(control);
  }
  return actions;
}
function renderCard(o,parent) {
  const primary=!byId.get(o.id).parent;
  const container=isContainer(o);
  const reviewable=hasContent(o);
  const card=node('article',null,container?'review-group':primary?'review-card':'review-element');
  card.dataset.objectId=o.id;
  card.dataset.type=o.type;
  card.dataset.role=o.role??'';
  card.dataset.reviewable=String(reviewable);
  const head=node('header',null,'card-head');
  head.tabIndex=-1;
  const title=o.type==='page'?ui.pageReview:
    [nameOf(o.type),o.module_number??o.subtask_label].filter(Boolean).join(' ');
  const heading=node(primary?'h3':'h4',title);
  const status=node('span',null,'state');
  const body=node('div',null,'card-body');
  const content=node('div',null,'card-content');
  const form=node('form',null,'review-form');
  form.hidden=true;
  const feedback=node('div',null,'feedback');
  feedback.hidden=true;
  const view={card,head,body,form,status,feedback};
  views.set(o.id,view);
  head.append(heading,status);
  if (container) {
    const structure=button(ui.structureIssue,()=>openIssue(o,'assignment',editorContext(o),false,true),'subtle');
    structure.dataset.action='structure';
    head.append(structure);
    const pass=button(ui.structurePass,()=>{
      append(o,'approved',{report_kind:'structure_review',pdf_page:sourcePage(o)});
      saveReview();
    },'subtle');
    pass.dataset.action='structure-approve';
    pass.classList.replace('subtle','pass');
    const review=node('div',null,'structure-review');
    view.structureLabel=node('strong',null,'structure-label');
    review.append(view.structureLabel,pass);
    view.structureIssue=structure;
    view.structureReview=review;
    view.structurePass=pass;
  }
  if (primary && o.type!=='page') {
    const nums=[...new Set(o.page_refs.map(r=>r.pdf_page))];
    heading.append(node('small',`PDF ${nums.join(' · ')}`));
  }
  renderContent(content,o,view);
  body.append(content);
  if (view.structureReview) body.append(view.structureReview);
  if (reviewable) {
    const actions=makeActions(o);
    if (container) {
      view.ownStatus=node('span',null,'state');
      actions.prepend(view.ownStatus);
    }
    body.append(actions);
  }
  body.append(form,feedback);
  const sub=children(o);
  if (sub.length) {
    const branch=node('div',null,'review-children');
    const exerciseInputs=new Set(o.exercise_input_ids??[]);
    let exerciseGroup;
    for (const child of sub) {
      if (!exerciseInputs.has(child.id)) {
        renderCard(child,branch);
        continue;
      }
      if (!exerciseGroup) {
        const title=local(['练习用数','Жаттығуға берілген сандар']);
        exerciseGroup=node('div',null,'exercise-inputs');
        exerciseGroup.setAttribute('role','group');
        exerciseGroup.setAttribute('aria-label',title);
        exerciseGroup.append(node('h4',title));
        branch.append(exerciseGroup);
      }
      renderCard(child,exerciseGroup);
    }
    body.append(branch);
  }
  card.append(head,body);
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
  if (key==='page') return o.type==='page';
  if (key==='visual') return visualKinds.includes(o.type);
  if (key==='teaching_link') return o.type===key;
  return statusOf(o)===key || ownStatus.get(o.id)===key || structureStatuses.get(o.id)===key;
}
function applyFilter() {
  const key=$('filter').value;
  $('apply-filter').hidden=key==='all';
  function visible(o,context=false) {
    const showChildren=context || (key!=='all' && structureStatuses.get(o.id)===key);
    const related=children(o).map(child=>visible(child,showChildren)).some(Boolean);
    const shown=context||related||matchesFilter(o,key);
    const view=views.get(o.id);
    view.card.hidden=!shown;
    return shown;
  }
  let first=null;
  for (const group of groups) {
    const shown=group.roots.filter(o=>visible(o));
    group.region.hidden=!shown.length;
    first??=shown[0];
  }
  $('no-cards').hidden=Boolean(first);
  return ordered.find(o=>matchesFilter(o,key))??first;
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
  if (!$('sync-scan').checked) return;
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
  const view=views.get(o.id);
  if (view.card.closest('[hidden]')) {
    $('filter').value='all';
    applyFilter();
  }
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
function editorContext(o) {
  const view=views.get(o.id);
  return {o,view,pdf:sourcePage(o),cell:view.cell};
}
function openIssue(o,initial='other',ctx=editorContext(o),pageLevel=false,structural=false) {
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
      if (structural) extra.report_kind='structure_review';
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
    const pairs=Object.entries(codes).filter(([k])=>(lang==='zh'||k!=='translation_zh') && (!structural||structureCodes.has(k))).map(([k,v])=>[k,local(v)]);
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
  zh:{upper:'上行',lower:'下行',operator:'运算符',result:'结果',equivalence:'等值换算',invalidLink:'请检查关系方向。提供方法的说明指向受支持的任务，使用材料的任务指向所用材料，两端须为不同对象。',rowSpan:'跨行数',colSpan:'跨列数'},
  kk:{upper:'Жоғарғы жол',lower:'Төменгі жол',operator:'Амал таңбасы',result:'Нәтиже',equivalence:'Тең мәнді түрлендіру',invalidLink:'Байланыс бағытын тексеріңіз. Әдіс беретін ескертпе қолдау алатын тапсырмаға, материалды қолданатын тапсырма сол материалға бағытталады. Екі нысан бөлек болуы керек.',rowSpan:'Қамтитын жол саны',colSpan:'Қамтитын баған саны'}
};
Object.assign(ui,extraLabels[lang]);
for (const el of document.querySelectorAll('[data-i]')) el.textContent=ui[el.dataset.i];
$('title').textContent=L.title_kk;
$('title').lang='kk';
const meta = lang==='zh'
  ? [D.book.title_kk,`第 ${D.book.grade??''} 年级`,`第 ${D.book.part??''} 册`,`第 ${L.number} 课`]
  : [D.book.title_kk,`${D.book.grade??''}-сынып`,`${D.book.part??''}-бөлім`,`${L.number}-сабақ`];
if (D.book.part==null) meta.splice(2,1);
if (D.book.grade==null) meta.splice(1,1);
$('course-meta').textContent = [...meta,`PDF ${L.pdf_page_range.join('–')}`].filter(Boolean).join(' · ');
$('translated-title').textContent=translations.title?[translations.title,translations.theme].filter(Boolean).join(' · '):L.context_kk;
$('reviewer').setAttribute('aria-label',ui.reviewer);
optionSet($('page'),D.pages.map(p=>[String(p.pdf_page),`PDF ${p.pdf_page} · ${ui.printed} ${p.printed_page}`]));
optionSet($('filter'),filterOptions.map(([v,key])=>[v,ui[key]]));
optionSet($('module-jump'),[['',ui.select],...L.content_order.map(id=>units.get(id)).filter(o=>unitTypes.has(o.type)).map(o=>[o.id,label(o)])]);
for (const t of ['module','instructional_note','text','informative_image','formula','table','module_badge','other']) {
  const item=node('span',nameOf(t));
  item.dataset.type=t;
  $('legend').append(item);
}
if (priorPackage) merge(priorPackage);
if (currentPackage) merge(currentPackage);
readDraft();
$('draft').textContent=durable?ui.draft:ui.noDraft;
renderCards();
refreshStates();
focusScan(groups[0].roots[0]);
})();
