/**
 * 拉丁轉寫 → 阿維斯陀字母（Unicode U+10B00–U+10B3F）
 *
 * 為什麼主欄是轉寫而不是字母：學界一律以轉寫引用，字母欄是給眼睛看的。
 * 轉換方向也只做這一向——**字母 → 轉寫不做**，因為那是有損的（見下）。
 *
 * 🚨 這支函式最危險的失敗方式不是報錯，是「安靜地少轉幾個字」：
 *    ā 沒收進表就當成 a，頁面照樣顯示、字母欄照樣是一串阿維斯陀字，
 *    只是拼錯了，而沒有人看得出來。所以 toAvestanScript() 一律回傳
 *    unmapped 清單，呼叫端必須處理；test/avestan-script.spec.ts 釘住
 *    「全表往返一致」與「已知詞逐字正確」兩件事。
 *
 * 轉寫規範採霍夫曼式（Hoffmann），即 avesta.org 與 TITUS 通行的那一套。
 * 輸入先做 NFC 正規化，再以「長字串優先」比對——ā 必須排在 a 前面，
 * 否則 ā 會先被 a 吃掉、剩一個游離的長音符號。
 */

/** 阿維斯陀字母表：轉寫 → 字元。順序無關（比對時另行按長度排序）。 */
const LETTERS: Record<string, string> = {
  // ── 母音 ──
  'a': '\u{10B00}', 'ā': '\u{10B01}', 'å': '\u{10B02}', 'ā̊': '\u{10B03}',
  'ą': '\u{10B04}', 'ą̇': '\u{10B05}', 'ə': '\u{10B06}', 'ə̄': '\u{10B07}',
  'e': '\u{10B08}', 'ē': '\u{10B09}', 'o': '\u{10B0A}', 'ō': '\u{10B0B}',
  'i': '\u{10B0C}', 'ī': '\u{10B0D}', 'u': '\u{10B0E}', 'ū': '\u{10B0F}',
  // ── 塞音與擦音 ──
  'k': '\u{10B10}', 'x': '\u{10B11}', 'x́': '\u{10B12}', 'xᵛ': '\u{10B13}',
  'g': '\u{10B14}', 'ġ': '\u{10B15}', 'γ': '\u{10B16}',
  'c': '\u{10B17}', 'j': '\u{10B18}',
  't': '\u{10B19}', 'θ': '\u{10B1A}', 'd': '\u{10B1B}', 'δ': '\u{10B1C}',
  't̰': '\u{10B1D}',
  'p': '\u{10B1E}', 'f': '\u{10B1F}', 'b': '\u{10B20}', 'β': '\u{10B21}',
  // ── 鼻音 ──
  'ŋ': '\u{10B22}', 'ŋ́': '\u{10B23}', 'ŋᵛ': '\u{10B24}',
  'n': '\u{10B25}', 'ń': '\u{10B26}', 'ṇ': '\u{10B27}',
  'm': '\u{10B28}', 'm̨': '\u{10B29}',
  // ── 半母音與流音 ──
  'ẏ': '\u{10B2A}', 'y': '\u{10B2B}', 'v': '\u{10B2C}',
  'r': '\u{10B2D}', 'l': '\u{10B2E}', 'w': '\u{10B2F}',
  // ── 齒擦音 ──
  's': '\u{10B30}', 'z': '\u{10B31}', 'š': '\u{10B32}', 'ž': '\u{10B33}',
  'š́': '\u{10B34}', 'ṣ̌': '\u{10B35}', 'h': '\u{10B36}',
}

/**
 * 抄本裡詞與詞之間以圓點分隔，不用空白。這裡用 U+00B7 而非 Avestan 區的
 * 標點（U+10B3A 以下），因為中間點在任何字型下都畫得出來，而 Avestan
 * 標點少有字型支援，缺字時會變成豆腐方塊——那比用一個通用符號更糟。
 */
export const AVESTAN_WORD_SEPARATOR = '·'

// 表裡多數附加符號沒有預組字（ə̄、t̰、ṣ̌、ŋ́ 都是基字＋結合符），
// 而輸入端可能是任一種正規化形式。兩邊都過 NFC 才比得上。
const NORMALIZED: Record<string, string> = Object.fromEntries(
  Object.entries(LETTERS).map(([k, v]) => [k.normalize('NFC'), v]),
)

/** 逐一比對用的鍵，長者優先。ā 必須排在 a 之前。 */
const KEYS = Object.keys(NORMALIZED).sort((a, b) => b.length - a.length)

/** 不參與轉換、原樣保留的字元：數字、常見標點、換行。 */
const PASSTHROUGH = /[\d\s.,;:!?()[\]{}'"«»—–\-…*†‡§¶/\\|]/u

export interface AvestanConversion {
  /** 轉換後的阿維斯陀字母 */
  script: string
  /** 表裡查不到、原樣留下的字元（去重）。非空即代表這一段轉寫有東西沒轉到。 */
  unmapped: string[]
}

/**
 * 把霍夫曼式拉丁轉寫轉成阿維斯陀字母。
 *
 * 未收錄的字元原樣保留並記入 unmapped——**不要靜默丟棄**，
 * 呼叫端據此決定是否顯示字母欄。
 */
export function toAvestanScript(translit: string): AvestanConversion {
  const src = translit.normalize('NFC')
  const out: string[] = []
  const unmapped = new Set<string>()

  let i = 0
  while (i < src.length) {
    // 空白 → 詞分隔圓點（連續空白只出一個；換行原樣保留）
    if (src[i] === '\n' || src[i] === '\r') {
      out.push(src[i])
      i += 1
      continue
    }
    if (src[i] === ' ' || src[i] === '\t') {
      while (i < src.length && (src[i] === ' ' || src[i] === '\t')) i += 1
      out.push(AVESTAN_WORD_SEPARATOR)
      continue
    }

    let matched = false
    for (const key of KEYS) {
      if (src.startsWith(key, i)) {
        out.push(NORMALIZED[key])
        i += key.length
        matched = true
        break
      }
    }
    if (matched) continue

    // 大寫：轉寫本身無大小寫之分，但英譯夾注常有；先降格再試一次。
    const lower = src[i].toLowerCase()
    if (lower !== src[i] && NORMALIZED[lower]) {
      out.push(NORMALIZED[lower])
      i += 1
      continue
    }

    if (!PASSTHROUGH.test(src[i])) unmapped.add(src[i])
    out.push(src[i])
    i += 1
  }

  return { script: out.join(''), unmapped: [...unmapped] }
}

/** 這段轉寫能不能乾淨地轉成字母？供 UI 決定要不要給切換鈕。 */
export function isCleanlyConvertible(translit: string): boolean {
  return toAvestanScript(translit).unmapped.length === 0
}

/** 字母表本身，供測試與說明頁列出對照。 */
export function avestanAlphabet(): Array<{ translit: string; glyph: string; code: string }> {
  return Object.entries(LETTERS).map(([translit, glyph]) => ({
    translit,
    glyph,
    code: `U+${glyph.codePointAt(0)!.toString(16).toUpperCase()}`,
  }))
}
