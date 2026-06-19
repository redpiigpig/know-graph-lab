export const meta = {
  name: 'dazangjing-sweep',
  description: '普查圖書館目錄中與基督教相關的書目，逐筆分類歸入（時代×藏×正/外），產出待審提案（不自動入庫）',
  phases: [
    { title: 'Sweep', detail: '多來源並行查目錄、抓真實書目紀錄' },
    { title: 'Classify', detail: '逐筆歸 era×藏×正/外 並寫定名/簡介' },
    { title: 'Verify', detail: '對抗式查核真偽與分類合理性' },
  ],
}

// args = {
//   sliceName,                 // 這次切片的名稱（如「近代宗教改革神學」）
//   subjects: [ ... ],         // 查詢切入點（主題詞/作者群/LCC 類），每個生一個 sweep agent
//   existingTitles: [ ... ],   // 既有 title_zh / title_orig，用於去重（盡量傳全 corpus）
//   eraHint,                   // 可選：本切片大致落在哪個時代（提示分類，非強制）
// }
let a = args || {}
if (typeof a === 'string') { try { a = JSON.parse(a) } catch (e) { a = {} } }
const subjects = (a.subjects && a.subjects.length) ? a.subjects : ['基督教神學']
const norm = (s) => String(s || '').toLowerCase().replace(/[（(].*?[）)]/g, '').replace(/[\s,;:．。.\-—/／’'·‧]/g, '')
const existing = new Set((a.existingTitles || []).map(norm))

const CATALOG_GUIDE =
  `【目錄查詢手冊——你必須真的上網查，禁止憑記憶杜撰書名】\n` +
  `先用 ToolSearch 載入 WebFetch 與 WebSearch（query: "select:WebFetch,WebSearch"），再實際呼叫：\n` +
  `① 德國國家圖書館 DNB（SRU ✅）：https://services.dnb.de/sru/dnb?version=1.1&operation=searchRetrieve&recordSchema=oai_dc&maximumRecords=40&query=WOE%3D<關鍵詞+號連>\n` +
  `② 法國國家圖書館 BnF（SRU ✅）：http://catalogue.bnf.fr/api/SRU?version=1.2&operation=searchRetrieve&maximumRecords=40&query=bib.subject+all+%22<主題>%22 （或 bib.author/bib.title all "..."）\n` +
  `③ OpenLibrary（JSON ✅）：https://openlibrary.org/search.json?limit=40&fields=title,author_name,first_publish_year,language&q=<關鍵詞+號連>\n` +
  `④ 美國國會圖書館 LoC（JSON/SRU 被擋，改 WebSearch）：WebSearch(query:"<作者或主題> works", allowed_domains:["loc.gov","catalog.loc.gov","id.loc.gov"])\n` +
  `⑤ Internet Archive（JSON ✅）：https://archive.org/advancedsearch.php?output=json&rows=40&fl[]=title&fl[]=creator&fl[]=year&q=<查詢>\n` +
  `（HathiTrust 403／WorldCat 需金鑰／梵蒂岡 opac 回全館分面殼——抓不動別倚賴。）`

const RAW_SCHEMA = {
  type: 'object',
  properties: {
    records: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          title_orig: { type: 'string' }, author: { type: 'string' },
          year: { type: 'string' }, place: { type: 'string' }, language: { type: 'string' },
          locator: { type: 'string' },
        },
        required: ['title_orig', 'author', 'locator'],
      },
    },
  },
  required: ['records'],
}

const ERA_RULES =
  `時代（依「時代精神」斷代，非死年分）：\n` +
  `‧ 前＝基督教/猶太教之前、被後世吸收的異教母體（埃及/兩河/希臘/羅馬哲學等）。\n` +
  `‧ 古＝正統確立期（約 1–800）：教父、大公會議、早期異端、猶太教(≤400)。\n` +
  `‧ 中＝約 800–1500：伊斯蘭交鋒＋政教權之爭（經院、拜占庭、敘利亞/東方教會、伊斯蘭/猶太哲學、巴比倫塔木德）。\n` +
  `‧ 近＝約 1500–1900：人文主義＋宗教改革＋反宗教改革＋新教正統與敬虔＋近代護教與宗教哲學＋啟蒙批判。\n` +
  `‧ 現＝約 1900–今：普世合一運動為主軸（新正統、解放/處境、天主教現代神學、漢語神學、東正教復興、世俗批判）。\n` +
  `外教/衍生宗教依「與之交鋒的那個時代」歸代。`

const CANG_RULES =
  `十藏（擇一最貼合者）：\n` +
  `經藏＝聖經正典與次經、影子聖經(異端福音/書信/啟示)；律藏＝教會法/會規/教法(費格赫)；論藏＝護教反異端系統神學釋經神祕哲學；` +
  `宣道藏＝講道/佈道/宣教方略與刊物；書函藏＝書信集與教宗通諭書信；禮儀藏＝禮典/聖事禮文/日課/聖頌儀軌；` +
  `詩藝藏＝聖詩/讚美詩/宗教詩/音樂受難曲/藝術；譯校藏＝聖經譯本與經文校勘/古卷；史傳藏＝教會史/編年/傳記/遊記/殉道紀錄；類書藏＝辭典/百科/工具書/書目彙編。\n` +
  `正藏＝尼西亞教會接受的主流；外藏＝偽典/異端/猶太教/外教見證/衍生宗教/世俗批判。`

phase('Sweep')
const sweeps = await parallel(subjects.map((subj) => () =>
  agent(
    `你在為「基督教大藏經」做圖書館目錄普查（嚴謹編目，務必準確、勿杜撰）。\n` +
    `本切片＝「${a.sliceName || '基督教文獻'}」；本批查詢切入點＝「${subj}」。\n` +
    `${CATALOG_GUIDE}\n` +
    `任務：實際查上述目錄，把與基督教相關、屬此切入點的真實書目紀錄逐一抄出（本批力求 20–40 筆）。\n` +
    `只列目錄實際回傳者；每筆給 title_orig(原文書題)、author、year(出版或寫作年)、place、language、locator(紀錄定位：DNB/BnF 控制號或 SRU 命中、OpenLibrary key、loc.gov/item 或 id.loc.gov URL、archive.org id 之一)。\n` +
    `查不到實際紀錄者一律不列。`,
    { label: `sweep:${String(subj).slice(0, 18)}`, phase: 'Sweep', schema: RAW_SCHEMA },
  ).then((r) => (r?.records || []))))

const raw = sweeps.flat().filter(Boolean)
const seen = new Set()
const fresh = []
for (const r of raw) {
  const k = norm(r.title_orig) + '|' + norm(r.author)
  const kt = norm(r.title_orig)
  if (!kt || existing.has(kt) || seen.has(k)) continue
  seen.add(k)
  fresh.push(r)
}
log(`普查 ${raw.length} 筆 → 去重(既有 ${existing.size})後 ${fresh.length} 筆待分類`)

const CLASS_SCHEMA = {
  type: 'object',
  properties: {
    title_zh: { type: 'string' }, title_orig: { type: 'string' }, author: { type: 'string' },
    era: { type: 'string', enum: ['前', '古', '中', '近', '現'] },
    cang: { type: 'string' }, canon: { type: 'string', enum: ['正', '外'] },
    division: { type: 'string' }, place: { type: 'string' }, language: { type: 'string' },
    eraYear: { type: 'string' }, intro: { type: 'string' }, locator: { type: 'string' },
    inScope: { type: 'boolean' },
  },
  required: ['title_zh', 'era', 'cang', 'canon', 'intro', 'inScope'],
}

phase('Classify')
const classified = await parallel(fresh.map((r) => () =>
  agent(
    `把這筆圖書館書目紀錄歸入「基督教大藏經」矩陣，並寫成大藏經條目。\n` +
    `紀錄：${JSON.stringify(r)}\n${a.eraHint ? `（切片時代提示：${a.eraHint}）\n` : ''}` +
    `${ERA_RULES}\n${CANG_RULES}\n` +
    `輸出：title_zh(繁體中文定名，沿用良好古譯、不杜撰)、title_orig、author、era(前/古/中/近/現)、cang(十藏其一的全名如「論藏」)、canon(正/外)、division(建議「部」名)、place、language、eraYear(寫作/成書年代)、intro(100–160字繁中簡介)、locator(沿用)、inScope(布林：是否真與基督教大藏經相關且值得收；現代純學術研究專著/二手研究若非原典，且不屬類書工具書，設 false)。\n` +
    `分類拿不準時 inScope 仍可為 true，但 era/cang/canon 給最合理判斷。純粹現代二手學術研究、與基督教無關者 inScope=false。`,
    { label: `classify:${String(r.title_orig).slice(0, 16)}`, phase: 'Classify', schema: CLASS_SCHEMA },
  )))

const inscope = classified.filter(Boolean).filter((w) => w.inScope && w.title_zh)
log(`分類完成，${inscope.length} 筆在收錄範圍`)

const VERDICT_SCHEMA = {
  type: 'object',
  properties: {
    isReal: { type: 'boolean' }, confidence: { type: 'number' },
    corrected: { type: 'object' }, note: { type: 'string' },
  },
  required: ['isReal', 'confidence'],
}

phase('Verify')
const verified = await parallel(inscope.map((w) => () =>
  agent(
    `對抗式查核這筆大藏經候選是否為「真實存在的文獻」、metadata 正確、且 era/cang/canon 分類合理。預設懷疑，查不到可靠佐證判 isReal=false。\n` +
    `候選：${JSON.stringify(w)}\n回傳 isReal、confidence(0–1)、corrected(需修正欄位物件，含分類修正)、note。`,
    { label: `verify:${String(w.title_zh).slice(0, 16)}`, phase: 'Verify', schema: VERDICT_SCHEMA },
  ).then((v) => ({ ...w, ...((v && v.corrected) || {}), _isReal: v?.isReal, _confidence: v?.confidence, _note: v?.note }))))

const proposed = verified.filter(Boolean).filter((w) => w._isReal && (w._confidence ?? 0) >= 0.6)

// 依 era→cang→canon 分組統計
const groups = {}
for (const w of proposed) {
  const g = `${w.era}/${w.cang}/${w.canon}`
  groups[g] = (groups[g] || 0) + 1
}
log(`查核通過 ${proposed.length} 筆，分佈：${Object.entries(groups).map(([k, v]) => `${k}:${v}`).join('  ')}`)

return {
  slice: a.sliceName,
  sweptCount: raw.length,
  freshCount: fresh.length,
  inScopeCount: inscope.length,
  proposedCount: proposed.length,
  groups,
  proposed,
}
