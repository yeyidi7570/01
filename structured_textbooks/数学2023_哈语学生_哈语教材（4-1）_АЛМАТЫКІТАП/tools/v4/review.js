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
let active, pdf=7, selectedCell, draw, drawnBox;
const sortRecords = (a,b) => a.record_id.localeCompare(b.record_id);

function add(o, owner, depth) {
  const nextOwner = o.type==='module' ? o.id : owner;
  byId.set(o.id,{o,owner:nextOwner,depth});
  ordered.push(o);
  for (const child of o.elements ?? []) add(child,nextOwner,depth+1);
}
for (const page of D.pages) {
  const p=page.pdf_page;
  add({id:page.id,type:'page',page_refs:[{pdf_page:p,printed_page:page.printed_page,scan_asset_id:page.scan_asset_id,bbox:[0,0,page.width,page.height]}]},null,0);
  for (const unit of L.units.filter(o => pageOf(o)===p)) add(unit,null,0);
  for (const link of L.teaching_links.filter(o => pageOf(o)===p)) add(link,link.parent_id,0);
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
    object_type:o.type,pdf_page:pdf,source_locations:o.page_refs,status,review_scope,
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
    update();
    message(ui.imported);
  } catch(e) { message(e.message===ui.duplicate?ui.duplicate:ui.importError,true); }
  files.value='';
};
$('reviewer').oninput=persist;

function matching(o) {
  const selectedModule=$('module-filter').value;
  if (selectedModule && byId.get(o.id).owner!==selectedModule) return false;
  const f=$('filter').value;
  if (f==='all') return true;
  if (f==='ocr') return Boolean(o.ocr_suggestion_ids?.length);
  if (f==='visual') return visualKinds.includes(o.type);
  if (f==='teaching_link') return o.type===f;
  return state(o)===f;
}
function navigate(step, pending=false) {
  const i=ordered.findIndex(o => o.id===active?.id);
  const n=ordered.length;
  for (let j=1;j<=n;j++) {
    const o=ordered[(i+step*j+n*2)%n];
    if (o.id!==active?.id && matching(o) && (!pending || state(o)==='unreviewed')) {
      show(o,false);
      return true;
    }
  }
  if (pending) message(ui.noPending);
  return false;
}
function show(o, clearFilters=true, partPage=null) {
  if (clearFilters && !matching(o)) {
    $('filter').value='all';
    $('module-filter').value=byId.get(o.id).owner ?? '';
  }
  if (clearFilters) message();
  active=o;
  pdf=partPage ?? pageOf(o);
  selectedCell=null;
  clearDraw();
  clearForm();
  update(true);
}
function showPdf(p) {
  const o=ordered.find(v=>pageOf(v)===p && v.type==='page');
  show(o,true,p);
}
function optionsFor(fallback=false) {
  const opts=ordered.filter(matching);
  if (fallback && active && !opts.includes(active)) opts.unshift(active);
  return opts.map(o=>[o.id,'　'.repeat(byId.get(o.id).depth)+label(o)]);
}
function counts() {
  const stats=Object.fromEntries(['unreviewed',...recordStates].map(s=>[s,0]));
  for (const o of ordered) stats[state(o)]++;
  const aggregate=Object.entries({total:ordered.length,...stats});
  $('statistics').replaceChildren(...aggregate.map(([k,v]) => node('span',`${ui[k]} ${v}`)));
  $('meter').max=ordered.length;
  $('meter').value=ordered.length-stats.unreviewed;
  $('meter').setAttribute('aria-label',`${$('meter').value} / ${ordered.length}`);
}
function update(center=false) {
  counts();
  const options=optionsFor(true);
  optionSet($('objects'),options.length?options:[['',ui.none]]);
  $('objects').value=active?.id??'';
  $('page').value=String(pdf);
  drawSheet(center);
  detail();
}
function listFilter() {
  const candidate=ordered.find(o=>pageOf(o)===pdf && matching(o)) ?? ordered.find(matching);
  if (candidate) show(candidate,false);
  else {
    active=null;
    selectedCell=null;
    clearDraw();
    clearForm();
    update();
  }
}
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
  if (img.getAttribute('src')!==images[page.scan_asset_id]) img.src=images[page.scan_asset_id];
  $('sheet').style.width=$('zoom').value;
  const boxes=$('overlays');
  boxes.replaceChildren();
  let focus;
  for (const o of ordered) {
    if (!['module','instructional_note'].includes(o.type) && o!==active &&
        (!$('elements').checked || o.type==='page' || o.type==='teaching_link')) continue;
    for (const r of o.page_refs.filter(x=>x.pdf_page===pdf)) {
      const b=button('',()=>show(o,true,pdf),'box');
      b.title=label(o);
      b.setAttribute('aria-label',label(o));
      b.dataset.id=o.id;
      b.dataset.type=o.type;
      setBox(b,r.bbox,page);
      if (o===active) {
        b.classList.add('selected');
        b.tabIndex=-1;
        if (!focus && o.type!=='page') focus=r.bbox;
      }
      boxes.append(b);
    }
  }
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
function detail() {
  const div=$('detail');
  div.replaceChildren();
  for (const id of ['approve','issue','unable','skip']) $(id).disabled=!active;
  $('bulk').hidden=!active || !['module','instructional_note'].includes(active.type);
  $('ocr').hidden=!(active?.text_kk!==undefined || selectedCell);
  if (!active) {
    div.append(node('p',ui.none));
    return;
  }
  const o=active;
  const head=node('div',null,'detail-head');
  const stat=node('span',ui[state(o)],'state');
  stat.dataset.state=state(o);
  head.append(node('h3',label(o)),stat);
  div.append(head,node('p',`PDF ${pdf} · ${ui.printed} ${pages.get(pdf).printed_page}`,'caption'));
  if (conflict(o)) div.append(node('div',ui.conflict,'conflict'));
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
    img.src=images[o.crop_asset_id];
    img.alt=`${ui.scan} · ${nameOf(o.type)}`;
    div.append(img);
  }
  if (o.structured_description) block(div,ui.structure,o.structured_description.description_kk);
  if (o.cells) renderTable(div,o);
  if (o.type==='teaching_link') {
    block(div,ui.change,ui[o.relationship]);
    block(div,ui.rawText,o.rationale_kk);
    block(div,ui.translation,aux(o.id),'translation');
    const nav=node('div',null,'toolbar');
    for (const [key,id] of [['from',o.from_id],['to',o.to_id]]) {
      const tgt=byId.get(id).o;
      nav.append(button(`${ui[key]} · ${label(tgt)}`,()=>show(tgt)));
    }
    div.append(nav);
  }
  if (new Set(o.page_refs.map(r=>r.pdf_page)).size>1) {
    const nav=node('div',null,'pager');
    for (const p of new Set(o.page_refs.map(r=>r.pdf_page))) nav.append(button(`PDF ${p}`,()=>show(o,false,p)));
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
  if (o.elements?.length || o.teaching_links?.length) {
    div.append(node('div',ui.children,'caption'));
    const ls=node('div',null,'child-list');
    for (const item of [...(o.elements??[]),...(o.teaching_links??[]).map(id=>byId.get(id).o)]) ls.append(button(label(item),()=>show(item)));
    div.append(ls);
  }
  if (['module','instructional_note'].includes(o.type)) div.append(node('small',ui.protected));
  const recs=liveRecords(o.id,true);
  if (recs.length) {
    const d=node('details');
    d.append(node('summary',`${ui.currentRecords} (${recs.length})`));
    for (const r of recs) {
      const heading=[ui[r.status], r.issue_code?local(codes[r.issue_code]):'',r.reviewer??'',r.interface_language].filter(Boolean).join(' · ');
      block(d,heading,r.note||r.recorded_at);
      if (r.changes.length) d.append(node('pre',fmt(r.changes)));
    }
    div.append(d);
  }
  const d=node('details');
  d.append(node('summary',ui.advanced),node('pre',fmt({id:o.id,sources:o.page_refs,...original(o)})));
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
function renderTable(parent,o) {
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
        selectedCell=selectedCell?.id===c.id?null:c;
        detail();
        drawSheet(true);
      });
      b.setAttribute('aria-label',`${ui.cell} ${c.row+1}, ${c.column+1} ${c.text_kk||ui.blank}`);
      b.setAttribute('aria-pressed',String(selectedCell?.id===c.id));
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
  parent.append(wrap);
  if (selectedCell) block(parent,ui.cell,`${selectedCell.row+1}, ${selectedCell.column+1} · ${selectedCell.text_kk||ui.blank}`);
}
const form=$('review-form');
function clearForm() {
  form.hidden=true;
  form.replaceChildren();
}
function field(parent,id,label,control) {
  const wrapper=node('label',null,'form-row');
  const f=node(control);
  f.id=id;
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
function editor(title,onSave) {
  clearForm();
  form.hidden=false;
  form.append(node('h4',title));
  const content=node('div');
  form.append(content);
  const actions=node('div',null,'toolbar');
  const submit=node('button',ui.save,'accent');
  submit.type='submit';
  const cancel=button(ui.cancel,()=>{clearDraw();clearForm();});
  actions.append(submit,cancel);
  form.append(actions);
  form.onsubmit=e=>{
    e.preventDefault();
    if (onSave()!==false) { clearDraw(); clearForm(); }
  };
  return content;
}
const change = (op,target_id,field,old_value,value,extra={}) => ({op,target_id,field,old_value,value,...extra});
function originalText(o) {
  return selectedCell?.text_kk ?? o.text_kk ?? '';
}
function setFields(panel,code,o,initial) {
  panel.replaceChildren();
  const inputText=(value='',label=ui.corrected)=>{
    const f=field(panel,'new-value',label,'textarea');
    f.value=value;
    return f;
  };
  if (['ocr_character','ocr_linebreak'].includes(code)) inputText(originalText(o));
  else if (code==='translation_zh') inputText(aux(selectedCell?.id) ?? aux(o.id) ?? '');
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
    const number=Number(initial?.region_index ?? 0);
    const onPage=o.page_refs.filter(r=>r.pdf_page===pdf);
    const options=onPage.map((r,i)=>[String(i),`${i+1} · ${r.bbox.join(', ')}`]);
    const region=selectField(panel,'region-index',ui.region,options,String(number));
    const f=field(panel,'new-bbox',ui.bbox,'input');
    f.value=onPage[number]?.bbox.join(', ')??'';
    region.onchange=()=>{f.value=onPage[Number(region.value)].bbox.join(', ');};
    panel.append(button(ui.redraw,()=>startDraw('boundary')));
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
  } else if (code==='table_structure' && selectedCell) {
    inputText(selectedCell.text_kk);
    const f=field(panel,'new-rowspan',ui.rowSpan,'input');
    f.type='number'; f.min=1; f.max=o.row_count-selectedCell.row; f.value=selectedCell.rowspan;
    const g=field(panel,'new-colspan',ui.colSpan,'input');
    g.type='number'; g.min=1; g.max=o.column_count-selectedCell.column; g.value=selectedCell.colspan;
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
function issueChanges(o,code) {
  const list=[];
  const value=$('new-value')?.value;
  const cell=selectedCell;
  const put=(target,field,oldValue,newValue,op='replace_value',extra={})=>{
    if (JSON.stringify(oldValue??null)!==JSON.stringify(newValue??null)) list.push(change(op,target,field,oldValue??null,newValue??null,extra));
  };
  if (['ocr_character','ocr_linebreak'].includes(code)) {
    if (value || cell || o.text_kk!==undefined) put(cell?.id??o.id,'text_kk',originalText(o),value,'replace_value',cell?{table_id:o.id}:{});
  } else if (code==='translation_zh') {
    const target=cell?.id??o.id;
    put(target,'translation_zh',aux(target),value,'replace_auxiliary_translation');
  } else if (code==='element_type') put(o.id,'type',o.type,$('new-type').value);
  else if (code==='extra_region') list.push(change('remove_region',o.id,'page_refs',o.page_refs,null));
  else if (code==='assignment') put(o.id,'parent_id',o.parent_id,$('new-parent').value,'move_object');
  else if (code==='reading_order' && $('new-order').value) {
    list.push(change('reorder_object',o.id,'content_order',null,Number($('new-order').value),{parent_id:o.parent_id??L.id}));
  } else if (code==='boundary') {
    const page=pages.get(pdf);
    const input=$('new-bbox').value.trim().split(/[ ,]+/).map(Number);
    if (!validBbox(input,page)) throw Error(ui.badBox);
    const old=o.page_refs.filter(r=>r.pdf_page===pdf)[Number($('region-index').value)];
    put(o.id,'page_refs',old,{...old,bbox:input},'replace_region',{region_index:o.page_refs.indexOf(old)});
  } else if (code==='teaching_link') {
    const to=$('link-to')?.value;
    const action=$('link-action')?.value;
    if (o.type==='teaching_link') {
      if (action==='remove') list.push(change('remove_link',o.id,'teaching_links',original(o),null));
      else {
        const from=$('link-from').value;
        const next={from_id:from,to_id:to,relationship:$('link-relation').value,rationale_kk:value};
        if (from===to) throw Error(ui.invalidLink);
        put(o.id,'teaching_links',original(o),next,'update_link');
      }
    } else if (to && to!==o.id) {
      list.push(change('add_link',o.id,'teaching_links',null,{from_id:o.id,to_id:to,relationship:$('link-relation').value,rationale_kk:value}));
    }
  } else if (code==='badge') {
    put(o.id,'text_kk',o.text_kk,value);
    if ($('new-scope')) put(o.id,'scope_ids',o.scope_ids,[...$('new-scope').selectedOptions].map(opt=>opt.value));
  } else if (code==='instructional_note') {
    if ($('note-badge').value) put(o.id,'instructional_note_badge',o.instructional_note_badge,$('note-badge').value);
    if (value || o.text_kk!==undefined) put(o.id,'text_kk',o.text_kk,value);
  } else if (code==='table_structure' && cell) {
    const extra={table_id:o.id};
    put(cell.id,'text_kk',cell.text_kk,value,'replace_table_cell',extra);
    for (const span of ['rowspan','colspan']) {
      const v=$('new-'+span).value;
      if (v) put(cell.id,span,cell[span],Number(v),'replace_table_cell',extra);
    }
  } else if (code==='formula_structure' && o.vertical) {
    const next={...o.vertical};
    for (const key of ['upper','lower','operator','result','equivalence_kk']) {
      const v=$('vertical-'+key).value.trim();
      if (v || key in next) next[key]=v||null;
    }
    put(o.id,'vertical',o.vertical,next,'replace_formula_layout');
  } else if (code==='formula_structure') put(o.id,'text_kk',o.text_kk,value);
  else if (code==='image_relationship') put(o.id,'structured_description.description_kk',o.structured_description?.description_kk,value,'replace_visual_description');
  else if (code==='missing_region') {
    list.push(change('review_missing_region',o.id,'page_refs',null,{pdf_page:pdf,bbox:drawnBox??null,possible_type:$('missing-type')?.value||null}));
  }
  if (!list.length && ['boundary','assignment','reading_order','element_type','table_structure','formula_structure','image_relationship','teaching_link','instructional_note','ocr_character','ocr_linebreak','badge','translation_zh'].includes(code)) {
    list.push({op:'review_issue',target_id:cell?.id??o.id,issue_code:code});
  }
  return list;
}
function finish(text=ui.saved) {
  persist();
  const went=navigate(1,true);
  if (!went) update();
  message(text);
}
function issueForm(initial='other',pageLevel=false) {
  const o=active;
  if (!o) return;
  const panel=editor(pageLevel?ui.missing:ui.issue,()=>{
    const code=$('issue-kind')?.value??'missing_region';
    const note=$('note').value;
    const cell=selectedCell;
    try {
      const changes=issueChanges(o,code);
      const extra={issue_code:code,note,changes};
      if (code==='translation_zh') extra.original_auxiliary_translation=aux(cell?.id??o.id)??null;
      if (cell) {
        extra.source_locations=cell.page_refs;
        extra.cell_id=cell.id;
        extra.original_cell=cell;
      }
      if (pageLevel) {
        extra.report_kind='page_omission';
        extra.omission_region=drawnBox??null;
        extra.source_locations=drawnBox?[{...o.page_refs[0],bbox:drawnBox}]:o.page_refs;
      }
      append(o,'issue',extra);
      clearDraw();
      finish();
      return true;
    } catch(e) { message(e.message,true); return false; }
  });
  const fields=node('div');
  if (!pageLevel) {
    const pairs=Object.entries(codes).filter(([k])=>lang==='zh'||k!=='translation_zh').map(([k,v])=>[k,local(v)]);
    const sel=selectField(panel,'issue-kind',ui.kind,pairs,initial);
    sel.onchange=()=>setFields(fields,sel.value,o);
  }
  panel.append(fields);
  setFields(fields,pageLevel?'missing_region':initial,o);
  field(panel,'note',ui.issueNote,'textarea');
  form.scrollIntoView({block:'nearest'});
}
function unableForm() {
  const o=active;
  if (!o) return;
  const panel=editor(ui.unable,()=>{
    append(o,'unable_to_verify',{note:$('note').value});
    finish();
  });
  field(panel,'note',ui.reason,'textarea').focus();
}
function approveOne(o) {
  const ids=o.ocr_suggestion_ids??[];
  const changes=ids.map(id=>{
    const s=proposals.get(id);
    return {op:'confirm_scan_restoration',target_id:o.id,suggestion_id:s.id,category:s.category,
      source_lines:s.source_lines,source_locations:s.evidence_regions,suggested_value:s.suggested_value,
      value:s.suggested_value,...(s.proposed_changes?{proposed_changes:s.proposed_changes}:{})};
  });
  append(o,'approved',{confirmed_suggestion_ids:ids,changes,pdf_page:o.page_refs.some(r=>r.pdf_page===pdf)?pdf:pageOf(o)});
}
function bulkApprove() {
  const o=active;
  if (!o) return;
  const children=flatChildren(o);
  const eligible=children.filter(c=>state(c)==='unreviewed'&&!c.review_flags?.length&&!c.ocr_suggestion_ids?.length &&
    !flatChildren(c).some(d=>d.review_flags?.length||d.ocr_suggestion_ids?.length||['issue','unable_to_verify'].includes(state(d))));
  approveOne(o);
  for (const c of eligible) approveOne(c);
  finish(children.some(c=>state(c)!=='approved')?ui.saved+' '+ui.partial:ui.saved);
}
function clearDraw() {
  draw=null;
  drawnBox=null;
  $('cancel-draw').hidden=true;
  $('selection').hidden=true;
  $('draw-hint').replaceChildren();
  $('sheet').classList.remove('drawing');
}
function startDraw(mode) {
  drawnBox=null;
  draw={mode,anchor:null};
  $('selection').hidden=true;
  $('sheet').classList.add('drawing');
  $('cancel-draw').hidden=false;
  const hint=$('draw-hint');
  hint.textContent=mode==='omission'?ui.drag:ui.redraw;
  if (mode==='omission') {
    hint.append(' ',button(ui.pageOnly,()=>{
      clearDraw();
      issueForm('missing_region',true);
    }));
  }
}
const sheet=$('sheet');
function coords(e) {
  const b=sheet.getBoundingClientRect();
  const p=pages.get(pdf);
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
  if (!draw || e.button!==0) return;
  e.preventDefault();
  draw.anchor=coords(e);
  sheet.setPointerCapture(e.pointerId);
});
sheet.addEventListener('pointermove',e=>{
  if (!draw?.anchor) return;
  const el=$('selection');
  el.hidden=false;
  setBox(el,pointerBox(e),pages.get(pdf));
});
sheet.addEventListener('pointerup',e=>{
  if (!draw?.anchor) return;
  const b=pointerBox(e);
  draw.anchor=null;
  if (!validBbox(b,pages.get(pdf)) || b[2]-b[0]<4 || b[3]-b[1]<4) return;
  const mode=draw.mode;
  draw=null;
  drawnBox=b;
  $('sheet').classList.remove('drawing');
  $('draw-hint').textContent=mode==='omission'?ui.selectedRegion:'';
  $('selection').hidden=false;
  setBox($('selection'),b,pages.get(pdf));
  if (mode==='boundary') $('new-bbox').value=b.join(', ');
  else issueForm('missing_region',true);
});
sheet.addEventListener('pointercancel',()=>{if(draw)draw.anchor=null;});
$('cancel-draw').onclick=()=>{clearDraw();clearForm();};
$('omission').onclick=()=>{showPdf(pdf);startDraw('omission');};
$('page').onchange=e=>showPdf(Number(e.target.value));
$('zoom').onchange=()=>drawSheet(true);
$('elements').onchange=()=>drawSheet(false);
$('objects').onchange=e=>{const o=byId.get(e.target.value)?.o;if(o)show(o,false);};
$('filter').onchange=listFilter;
$('module-filter').onchange=listFilter;
$('prev').onclick=()=>navigate(-1);
$('next').onclick=()=>navigate(1);
$('next-unreviewed').onclick=()=>navigate(1,true);
$('approve').onclick=()=>{if(active){approveOne(active);finish();}};
$('issue').onclick=()=>issueForm(active?.type==='teaching_link'?'teaching_link':'other');
$('unable').onclick=unableForm;
$('skip').onclick=()=>{clearForm();clearDraw();if(!navigate(1,true))update();message(ui.skipped);};
$('bulk').onclick=bulkApprove;
$('ocr').onclick=()=>issueForm('ocr_character');
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
optionSet($('module-filter'),[['',ui.all],...L.units.filter(o=>o.type==='module').map(o=>[o.id,label(o)])]);
for (const t of ['module','instructional_note','text','informative_image','formula','table','module_badge','other']) {
  const item=node('span',nameOf(t));
  item.dataset.type=t;
  $('legend').append(item);
}
readDraft();
$('draft').textContent=durable?ui.draft:ui.noDraft;
show(ordered.find(o=>o.type==='module'),false);
})();
