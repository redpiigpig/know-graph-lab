/**
 * Lazy text loader for large creed/council documents.
 *
 * 用 import.meta.glob 的 lazy（非 eager）模式 — 每個 .txt 只有在實際呼叫
 * loader 時才會被 fetch + 加入 bundle，避免列表 page 或 SSR 階段 eager
 * 載入 16 份梵二 × 3 語 × 平均 50KB = ~9MB 文本撐爆 Vite IPC buffer。
 *
 * textKey 對應規則：
 *   - 'sc-latin' / 'sc-english' / 'sc-chinese' -> data/creeds/ecumenical-councils/vatican-ii/sc-latin.txt
 *   - 同樣對應 16 份梵二文件（im / lg / oe / ur / cd / pc / ot / ge / na / dv / aa / dh / ag / po / gs）
 */

const vat2Loaders = import.meta.glob(
  './ecumenical-councils/vatican-ii/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

/** 已載入過的 text cache（避免重複網路 / fs 載入） */
const cache = new Map<string, string>()

export async function loadCreedText(textKey: string): Promise<string> {
  if (cache.has(textKey)) return cache.get(textKey)!
  const path = `./ecumenical-councils/vatican-ii/${textKey}.txt`
  const loader = vat2Loaders[path]
  if (!loader) throw new Error(`Creed text not found for key: ${textKey} (path: ${path})`)
  const text = await loader()
  cache.set(textKey, text)
  return text
}

export function availableTextKeys(): string[] {
  return Object.keys(vat2Loaders).map(p =>
    p.replace('./ecumenical-councils/vatican-ii/', '').replace(/\.txt$/, ''),
  )
}
