export const meta = {
  name: 'dazangjing-research',
  description: '為基督教大藏經某一(時代×藏×正/外)上網研究候選書目，去重＋對抗式查核，產出待審提案（不自動入庫）',
  phases: [
    { title: 'Research', detail: '多權威來源並行列候選書目' },
    { title: 'Verify', detail: '逐筆對抗式查核真偽與 metadata' },
  ],
}

// args = {
//   era, eraName, boundary, collection, collectionName, canon('zheng'|'wai'),
//   canonLabel, goal:{ goal, zhengScope:[], waiScope:[], sources:[] },
//   existingTitles:[...]  // 該時代既有 title_zh，用於去重
// }
let a = args || {}
if (typeof a === 'string') { try { a = JSON.parse(a) } catch (e) { a = {} } }
const scope = a.canon === 'wai' ? (a.goal?.waiScope || []) : (a.goal?.zhengScope || [])
const sources = (a.goal?.sources && a.goal.sources.length) ? a.goal.sources : ['權威學術全集與工具書']
const existing = new Set((a.existingTitles || []).map((t) => String(t).replace(/\s/g, '')))

const CAND_SCHEMA = {
  type: 'object',
  properties: {
    works: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          title_zh: { type: 'string' }, title_orig: { type: 'string' },
          author: { type: 'string' }, era: { type: 'string' },
          place: { type: 'string' }, language: { type: 'string' },
          division: { type: 'string' }, parent: { type: 'string' }, extent: { type: 'string' },
          intro: { type: 'string' }, source_citation: { type: 'string' },
        },
        required: ['title_zh', 'author', 'era', 'place', 'language', 'intro', 'source_citation'],
      },
    },
  },
  required: ['works'],
}

const VERDICT_SCHEMA = {
  type: 'object',
  properties: {
    isReal: { type: 'boolean' }, confidence: { type: 'number' },
    corrected: { type: 'object' }, note: { type: 'string' },
  },
  required: ['isReal', 'confidence'],
}

// 實測可用的真實圖書館目錄 endpoint（2026-06-19 親測，非模型記憶）。
// 鐵律：研究 agent 必須真的 WebFetch / WebSearch 這些 endpoint，只列「目錄實際回傳」的書。
const CATALOG_GUIDE =
  `【目錄查詢手冊——你必須真的上網查，禁止憑記憶杜撰書名】\n` +
  `先用 ToolSearch 載入 WebFetch 與 WebSearch（query: "select:WebFetch,WebSearch"），再實際呼叫：\n` +
  `① 德國國家圖書館 DNB（SRU，開放可用 ✅）：\n` +
  `   https://services.dnb.de/sru/dnb?version=1.1&operation=searchRetrieve&recordSchema=oai_dc&maximumRecords=30&query=WOE%3D<關鍵詞用+號連>\n` +
  `   （WOE=任意詞；可用作者名或拉丁/德文書題或主題詞。回 dc:title/dc:creator/dc:date）\n` +
  `② 法國國家圖書館 BnF（SRU，開放可用 ✅）：\n` +
  `   http://catalogue.bnf.fr/api/SRU?version=1.2&operation=searchRetrieve&maximumRecords=30&query=bib.author+all+%22<作者>%22+and+bib.subject+all+%22<主題>%22\n` +
  `   （也可 bib.title all "..."；回 MARCXML，看 datafield 200/700/210）\n` +
  `③ OpenLibrary（開放 JSON ✅，英文書目廣度）：\n` +
  `   https://openlibrary.org/search.json?limit=30&fields=title,author_name,first_publish_year,language&q=<關鍵詞用+號連>\n` +
  `④ 美國國會圖書館 LoC（JSON/SRU 被擋，改用 WebSearch 限定網域）：\n` +
  `   WebSearch(query:"<作者或書題> works", allowed_domains:["loc.gov","catalog.loc.gov","id.loc.gov"])\n` +
  `   權威人名/主題用 id.loc.gov（規範作者拼法、LCC 主題），書目用 loc.gov/item。\n` +
  `⑤ Internet Archive（開放，可補全文）：https://archive.org/advancedsearch.php?output=json&rows=30&fl[]=title&fl[]=creator&fl[]=year&q=<查詢>\n` +
  `（HathiTrust 403、WorldCat 需金鑰、梵蒂岡 opac 回全館分面殼——這三者抓不動，別倚賴；能查到再加分。）\n` +
  `每筆 source_citation 必須是「目錄實際回傳的紀錄定位」：DNB/BnF 控制號或 SRU 命中、OpenLibrary key、loc.gov/item URL、id.loc.gov URL、archive.org id 之一。查不到實際紀錄的書一律不列。`

phase('Research')
const batches = await parallel(sources.map((src) => () =>
  agent(
    `你在為「基督教大藏經」研究候選書目（嚴謹漢語神學文獻編目，務必準確、勿杜撰）。\n` +
    `目標時代＝${a.eraName}（斷代＝時代精神：${a.boundary}）。\n` +
    `目標分類＝${a.collectionName}‧${a.canonLabel}。\n` +
    `${CATALOG_GUIDE}\n` +
    `你的任務是「目錄驅動系統枚舉」：實際查上述目錄，把屬於此(時代×藏×正/外)、尚未被收錄的真實書卷逐一抄列，力求窮盡（本批請列 15–30 部以上）。\n` +
    `‧ 本批側重來源／主題視角：「${src}」——以此為查詢切入點（作者群、全集卷目、主題詞），但務必交叉查 ≥2 個上列 endpoint 確認紀錄存在。\n` +
    `收錄範圍定向（提示，非窮舉）：${scope.join('；')}。\n` +
    `每部需給：title_zh(繁體中文定名，沿用良好古譯、託名不寫偽)、title_orig(原文/西文名)、author、era(寫作年代)、place、language、division(建議歸入的「部」名)、intro(100–160字繁中簡介)、source_citation(目錄實際回傳的紀錄定位，見手冊)。\n` +
    `合集處理：遇「合集」（塔木德／聖訓集／全集等）枚舉其子單位為個別卷，各標 parent；太短碎者整部一卷並以 extent 標示。\n` +
    `鐵則：寧缺勿濫，目錄查不到實際紀錄或 metadata 不明者一律不列；目錄明載者與合集子卷盡量收全。`,
    { label: `research:${String(src).slice(0, 20)}`, phase: 'Research', schema: CAND_SCHEMA },
  ).then((r) => (r?.works || []))))

const cands = batches.flat().filter(Boolean)
const seen = new Set()
const fresh = []
for (const w of cands) {
  const k = String(w.title_zh || '').replace(/\s/g, '')
  if (!k || existing.has(k) || seen.has(k)) continue
  seen.add(k)
  fresh.push(w)
}
log(`候選 ${cands.length} 筆 → 對既有去重(${existing.size}筆)後 ${fresh.length} 筆`)

phase('Consolidate')
let merged = fresh
if (fresh.length > 1) {
  const m = await agent(
    `以下多來源候選書目可能含「同一部書、不同譯名」的近似重複。請合併重複者：每部只留一筆，選 metadata 最完整者、title_zh 取最通行定名，保留 parent/extent/division。輸出去重後清單。\n${JSON.stringify(fresh)}`,
    { label: 'consolidate', phase: 'Consolidate', schema: CAND_SCHEMA },
  )
  if (m && m.works && m.works.length) merged = m.works
}
log(`近似重複合併：${fresh.length} → ${merged.length}`)

phase('Verify')
const verified = await parallel(merged.map((w) => () =>
  agent(
    `對抗式查核這筆大藏經候選書目是否為「真實存在的文獻」且 metadata 正確。預設懷疑，查不到可靠佐證就判 isReal=false。\n` +
    `候選：${JSON.stringify(w)}\n` +
    `回傳 isReal(布林)、confidence(0–1)、corrected(需修正的欄位物件，無則空物件)、note(佐證或駁回理由)。`,
    { label: `verify:${String(w.title_zh).slice(0, 16)}`, phase: 'Verify', schema: VERDICT_SCHEMA },
  ).then((v) => ({ ...w, ...((v && v.corrected) || {}), _isReal: v?.isReal, _confidence: v?.confidence, _note: v?.note }))))

const proposed = verified
  .filter(Boolean)
  .filter((w) => w._isReal && (w._confidence ?? 0) >= 0.6)

log(`查核通過 ${proposed.length} / ${merged.length} 筆，產出待審提案`)
return {
  target: { era: a.era, collection: a.collection, canon: a.canon },
  candidateCount: cands.length,
  freshCount: fresh.length,
  mergedCount: merged.length,
  proposedCount: proposed.length,
  proposed,
}
