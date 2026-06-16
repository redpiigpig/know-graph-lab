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
const a = args || {}
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
          division: { type: 'string' }, intro: { type: 'string' },
          source_citation: { type: 'string' },
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

phase('Research')
const batches = await parallel(sources.map((src) => () =>
  agent(
    `你在為「基督教大藏經」研究候選書目（這是嚴謹的漢語神學文獻編目，務必準確、勿杜撰）。\n` +
    `目標時代＝${a.eraName}（斷代＝時代精神：${a.boundary}）。\n` +
    `目標分類＝${a.collectionName}‧${a.canonLabel}。\n` +
    `收錄範圍：\n- ${scope.join('\n- ')}\n\n` +
    `請**僅**根據權威來源「${src}」，列出 8–15 部「符合此時代×藏×正/外、且尚未被收錄」的真實文獻。\n` +
    `每部需給：title_zh(繁體中文定名，沿用良好古譯、託名不寫偽)、title_orig(原文/西文名)、author(或傳說作者)、era(寫作年代)、place(寫作地點)、language、division(建議歸入的「部」名)、intro(100–160字繁中簡介)、source_citation(出處：書目/頁碼/可查證網址)。\n` +
    `鐵則：寧缺勿濫，任何不確定其真實存在或 metadata 者一律不列。`,
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
log(`候選 ${cands.length} 筆 → 去重(對既有${existing.size}筆)後 ${fresh.length} 筆待查核`)

phase('Verify')
const verified = await parallel(fresh.map((w) => () =>
  agent(
    `對抗式查核這筆大藏經候選書目是否為「真實存在的文獻」且 metadata 正確。預設懷疑，查不到可靠佐證就判 isReal=false。\n` +
    `候選：${JSON.stringify(w)}\n` +
    `回傳 isReal(布林)、confidence(0–1)、corrected(需修正的欄位物件，無則空物件)、note(佐證或駁回理由)。`,
    { label: `verify:${String(w.title_zh).slice(0, 16)}`, phase: 'Verify', schema: VERDICT_SCHEMA },
  ).then((v) => ({ ...w, ...((v && v.corrected) || {}), _isReal: v?.isReal, _confidence: v?.confidence, _note: v?.note }))))

const proposed = verified
  .filter(Boolean)
  .filter((w) => w._isReal && (w._confidence ?? 0) >= 0.6)

log(`查核通過 ${proposed.length} / ${fresh.length} 筆，產出待審提案`)
return {
  target: { era: a.era, collection: a.collection, canon: a.canon },
  candidateCount: cands.length,
  freshCount: fresh.length,
  proposedCount: proposed.length,
  proposed,
}
