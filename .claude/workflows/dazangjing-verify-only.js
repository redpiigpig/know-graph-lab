export const meta = {
  name: 'dazangjing-verify-only',
  description: '對一批已分類的大藏經候選做對抗式查核（verify-only），產出通過清單',
  phases: [
    { title: 'Verify', detail: '逐筆對抗式查核真偽與分類合理性' },
  ],
}
// args = { candidates: [ {title_zh,title_orig,author,era,cang,canon,division,eraYear,...}, ... ], model }
let a = args || {}
if (typeof a === 'string') { try { a = JSON.parse(a) } catch (e) { a = {} } }
const cands = a.candidates || []
const model = a.model || 'sonnet'

const VERDICT_SCHEMA = {
  type: 'object',
  properties: {
    isReal: { type: 'boolean' }, confidence: { type: 'number' },
    corrected: { type: 'object' }, note: { type: 'string' },
  },
  required: ['isReal', 'confidence'],
}

phase('Verify')
const verified = await parallel(cands.map((w) => () =>
  agent(
    `對抗式查核這筆「基督教大藏經」候選是否為真實存在的文獻、metadata 正確、且 era/cang/canon 分類合理。預設懷疑；查不到可靠佐證判 isReal=false。\n` +
    `候選：${JSON.stringify(w)}\n` +
    `回傳 isReal、confidence(0–1)、corrected(僅需修正的欄位，含分類修正；無則省略)、note(一句佐證或疑點)。`,
    { label: `verify:${String(w.title_zh).slice(0, 16)}`, phase: 'Verify', schema: VERDICT_SCHEMA, model },
  ).then((v) => ({ title_zh: w.title_zh, _isReal: v?.isReal, _confidence: v?.confidence, _note: v?.note, _corrected: (v && v.corrected) || null }))))

const ok = verified.filter(Boolean).filter((w) => w._isReal && (w._confidence ?? 0) >= 0.6)
const fail = verified.filter(Boolean).filter((w) => !(w._isReal && (w._confidence ?? 0) >= 0.6))
log(`查核通過 ${ok.length}/${cands.length}；未過 ${fail.length}`)
return { total: cands.length, passCount: ok.length, pass: ok, fail }
