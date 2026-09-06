import { describe, expect, it } from 'vitest'
import {
  AVESTAN_WORD_SEPARATOR,
  avestanAlphabet,
  isCleanlyConvertible,
  toAvestanScript,
} from '~/utils/avestanScript'
import {
  CANONS,
  allTexts,
  canonTextCount,
  findText,
  searchTexts,
  tallyColumns,
  textIndex,
  volumeTextCount,
  volumesOf,
} from '~/data/avesta'

describe('阿維斯陀字母轉換', () => {
  it('字母表覆蓋 Unicode 阿維斯陀區的 55 個字母', () => {
    const rows = avestanAlphabet()
    expect(rows).toHaveLength(55)
    // 全部落在 U+10B00–U+10B36 的字母段（標點段 10B39+ 不收）
    for (const r of rows) {
      const cp = r.glyph.codePointAt(0)!
      expect(cp).toBeGreaterThanOrEqual(0x10B00)
      expect(cp).toBeLessThanOrEqual(0x10B36)
    }
    // 一個轉寫只能對一個字元，一個字元也只能被一個轉寫指到
    expect(new Set(rows.map(r => r.glyph)).size).toBe(rows.length)
  })

  it('長字串優先：ā 不會被 a 先吃掉', () => {
    // 若比對順序寫錯，'ā' 會轉成 a 的字元再留一個游離的長音符號。
    const { script, unmapped } = toAvestanScript('ā')
    expect(script).toBe('\u{10B01}')
    expect(unmapped).toEqual([])
    expect(toAvestanScript('a').script).toBe('\u{10B00}')
  })

  it('已知詞逐字正確：ahura mazdā', () => {
    const { script, unmapped } = toAvestanScript('ahura mazdā')
    expect(unmapped).toEqual([])
    expect(script).toBe(
      '\u{10B00}\u{10B36}\u{10B0E}\u{10B2D}\u{10B00}'
      + AVESTAN_WORD_SEPARATOR
      + '\u{10B28}\u{10B00}\u{10B31}\u{10B1B}\u{10B01}',
    )
  })

  it('已知詞逐字正確：ašəm vohū（阿舍姆‧沃胡）', () => {
    const { script, unmapped } = toAvestanScript('ašəm vohū')
    expect(unmapped).toEqual([])
    expect(script).toBe(
      '\u{10B00}\u{10B32}\u{10B06}\u{10B28}'
      + AVESTAN_WORD_SEPARATOR
      + '\u{10B2C}\u{10B0A}\u{10B36}\u{10B0F}',
    )
  })

  it('全教第一禱詞的首句可乾淨轉換', () => {
    // yaθā ahū vairyō —— 阿胡納‧瓦伊里亞的第一句
    expect(isCleanlyConvertible('yaθā ahū vairyō')).toBe(true)
  })

  it('結合符號的字母不論輸入的正規化形式都轉得到', () => {
    // ə̄ 沒有預組字，NFC 與 NFD 下都是「基字＋U+0304」；ṣ̌ 同理。
    for (const w of ['ə̄', 'ṣ̌', 't̰', 'ŋ́', 'x́', 'š́']) {
      expect(toAvestanScript(w.normalize('NFC')).unmapped).toEqual([])
      expect(toAvestanScript(w.normalize('NFD')).unmapped).toEqual([])
    }
  })

  it('查無此字時記進 unmapped 而不是靜默丟掉', () => {
    // 這是本模組唯一會「看起來成功其實失敗」的路徑，必須釘住。
    const { script, unmapped } = toAvestanScript('aQa')
    expect(unmapped).toEqual(['Q'])
    expect(script).toContain('Q') // 原樣保留，不吞字
    expect(isCleanlyConvertible('aQa')).toBe(false)
  })

  it('連續空白只出一個詞分隔點，換行保留', () => {
    expect(toAvestanScript('a  a').script).toBe(`\u{10B00}${AVESTAN_WORD_SEPARATOR}\u{10B00}`)
    expect(toAvestanScript('a\na').script).toBe('\u{10B00}\n\u{10B00}')
  })
})

describe('祆教經典書目', () => {
  it('四藏齊備，前三藏為經典、王室銘文為附錄', () => {
    expect(CANONS.map(c => c.key)).toEqual(['avestan', 'pahlavi', 'later', 'epigraphy'])
    expect(CANONS.filter(c => c.scriptural).map(c => c.key)).toEqual(['avestan', 'pahlavi', 'later'])
    expect(CANONS.find(c => c.key === 'epigraphy')!.scriptural).toBe(false)
  })

  it('slug 全藏唯一（重複會在建索引時擲錯）', () => {
    expect(() => textIndex()).not.toThrow()
    const texts = allTexts()
    expect(new Set(texts.map(t => t.text.slug)).size).toBe(texts.length)
  })

  it('每一條都有 slug、中文定名與編號', () => {
    for (const { text, canon } of allTexts()) {
      expect(text.slug, `${canon.name} 缺 slug`).toMatch(/^[a-z0-9-]+$/)
      expect(text.title_zh.trim().length, `${text.slug} 缺中文定名`).toBeGreaterThan(0)
      expect(text.siglum.trim().length, `${text.slug} 缺編號`).toBeGreaterThan(0)
    }
  })

  it('每個「部」所列的卷都存在（打錯卷 key 會讓整部從索引頁消失）', () => {
    for (const canon of CANONS) {
      for (const part of canon.parts) {
        const resolved = volumesOf(canon, part)
        expect(resolved.length, `${canon.name}／${part.label} 有卷 key 對不到`).toBe(part.volumes.length)
      }
      // 反向：每一卷都要被某個部收走，否則它在索引頁上根本不會出現
      const claimed = new Set(canon.parts.flatMap(p => p.volumes))
      for (const v of canon.volumes) {
        expect(claimed.has(v.key), `${canon.name}／${v.name} 沒有被任何部收錄`).toBe(true)
      }
    }
  })

  it('禮儀單位的數目照薩珊傳統，不得擅改', () => {
    const avestan = CANONS.find(c => c.key === 'avestan')!
    const count = (key: string) => volumeTextCount(avestan.volumes.find(v => v.key === key)!)
    expect(count('yasna'), '亞斯納 72 章').toBe(72)
    expect(count('visperad'), '維斯帕拉德 24 章').toBe(24)
    expect(count('vendidad'), '萬迪達德 22 章').toBe(22)
    expect(count('yasht'), '亞什特 21 首').toBe(21)
    expect(count('nask'), '二十一納斯克').toBe(21)
  })

  it('亞斯納的章次連續且無跳號', () => {
    const avestan = CANONS.find(c => c.key === 'avestan')!
    const yasna = avestan.volumes.find(v => v.key === 'yasna')!
    const nums = yasna.divisions.flatMap(d => d.texts).map(t => Number(t.siglum.replace('Y ', '')))
    expect(nums).toEqual(Array.from({ length: 72 }, (_, i) => i + 1))
  })

  it('五組伽薩的章次與傳統一致', () => {
    // 伽薩＝ Y28–34、43–46、47–50、51、53。錯一章就是動到全教最古的文本。
    const gathas = allTexts()
      .filter(l => l.division.key.startsWith('y-gatha'))
      .map(l => Number(l.text.siglum.replace('Y ', '')))
      .sort((a, b) => a - b)
    expect(gathas).toEqual([
      28, 29, 30, 31, 32, 33, 34,
      43, 44, 45, 46,
      47, 48, 49, 50,
      51,
      53,
    ])
    expect(gathas).toHaveLength(17)
  })

  it('佚失的納斯克標為 lost-summary 並註明轉引出處', () => {
    const nasks = allTexts().filter(l => l.volume.key === 'nask')
    const lost = nasks.filter(l => l.text.status === 'lost-summary')
    // 二十一部中僅《萬迪達德》完整、《讚頌書》部分傳世，其餘全佚
    expect(lost.length).toBe(19)
    for (const l of lost) {
      expect(l.text.via, `${l.text.slug} 未註明轉引出處`).toBeTruthy()
    }
  })

  it('中文欄現況誠實：目前全藏尚無任何一篇有中譯', () => {
    // 這條會隨翻譯進度改。它存在的意義是：中譯上架時必須有人回來改這個數字，
    // 而不是讓頁面默默宣稱有中文卻是空的。
    const t = tallyColumns()
    expect(t.zh.ready ?? 0).toBe(0)
    expect(t.total).toBe(allTexts().length)
  })

  it('丹卡爾德第 3、6 卷標為版權內——英文欄的真實缺口', () => {
    for (const slug of ['denkard-03', 'denkard-06']) {
      const loc = findText(slug)!
      expect(loc.text.columns?.en ?? loc.division.columns?.en).toBe('copyright')
    }
  })

  it('搜尋可用中文、原文與編號找到同一篇', () => {
    for (const q of ['伽薩', 'Yasna 30', 'Y 30']) {
      expect(searchTexts(q).length, `搜「${q}」找不到`).toBeGreaterThan(0)
    }
    expect(findText('yasna-30')!.text.title_zh).toContain('兩靈')
    expect(findText('bisotun')).toBeUndefined() // slug 是 op-bisotun，別名不通
  })

  it('全藏規模', () => {
    const total = CANONS.reduce((n, c) => n + canonTextCount(c), 0)
    expect(total).toBe(allTexts().length)
    expect(total).toBeGreaterThan(200)
  })
})

describe('已上架正文與書目的對應', () => {
  it('每一份正文 JSON 的 slug 都對得上書目', async () => {
    // 🚨 對不上的 JSON，reader 走不到、書目頁照樣顯示——沒有任何地方看得出來。
    const { TEXT_REFS } = await import('~/data/avesta/sources')
    for (const ref of TEXT_REFS) {
      expect(findText(ref.slug), `正文 ${ref.slug}.json 在書目裡找不到對應條目`).toBeTruthy()
    }
  })

  it('正文所宣稱的藏與卷要跟書目一致', async () => {
    const { TEXT_REFS, loadText } = await import('~/data/avesta/sources')
    for (const ref of TEXT_REFS) {
      const doc = (await loadText(ref.slug))!
      const loc = findText(ref.slug)!
      expect(doc.canon, `${ref.slug} 的 canon 對不上`).toBe(loc.canon.key)
      expect(doc.volume, `${ref.slug} 的 volume 對不上`).toBe(loc.volume.key)
      expect(doc.siglum, `${ref.slug} 的編號對不上`).toBe(loc.text.siglum)
    }
  })

  it('書目標為已上架（ready）的篇章，正文必須真的存在', async () => {
    // 反向閘：標了 ready 卻沒檔案，頁面會顯示「正文尚未上架」而狀態燈是綠的。
    const { hasText } = await import('~/data/avesta/sources')
    for (const { text, division, canon } of allTexts()) {
      const c = text.columns ?? division.columns
      if (c?.orig === 'ready' || c?.en === 'ready' || c?.zh === 'ready') {
        expect(hasText(text.slug), `${canon.name}／${text.slug} 標為 ready 但無正文檔`).toBe(true)
      }
    }
  })

  it('萬迪達德 22 章全數上架，且每段都有引用式', async () => {
    const { TEXT_REFS, loadText } = await import('~/data/avesta/sources')
    const vd = TEXT_REFS.filter(r => r.slug.startsWith('vendidad-'))
    expect(vd).toHaveLength(22)
    for (const ref of vd) {
      const doc = (await loadText(ref.slug))!
      expect(doc.segments.length, `${ref.slug} 無段落`).toBeGreaterThan(0)
      for (const seg of doc.segments) {
        expect(seg.ref, `${ref.slug} 有段落缺引用式`).toMatch(/^Vd \d+\.\d+(-\d+)?$/)
      }
      // 舊式羅馬轉寫：站上不得開阿維斯陀字母切換
      expect(doc.orig_scheme).toBe('geldner-roman')
    }
  })
})
