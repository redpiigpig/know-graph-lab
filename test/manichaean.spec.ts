import { describe, expect, it } from 'vitest'
import {
  CANONS,
  CANON_CANON,
  CHINESE_CANON,
  TESTIMONIA_CANON,
  allTexts,
  canonTextCount,
  columnsOf,
  findCanon,
  findText,
  relatedOf,
  searchTexts,
  tallyColumns,
  tallyStatus,
  textIndex,
  volumeTextCount,
  volumesOf,
} from '~/data/manichaean'

describe('摩尼教經典 — 結構', () => {
  it('五藏俱在，且只有敵證藏非經典', () => {
    expect(CANONS.map(c => c.key)).toEqual(['canon', 'coptic', 'iranian', 'chinese', 'testimonia'])
    const nonScriptural = CANONS.filter(c => !c.scriptural)
    expect(nonScriptural.map(c => c.key)).toEqual(['testimonia'])
  })

  it('slug 全藏唯一（重複會讓兩篇共用一頁而版面完全正常）', () => {
    // textIndex() 本身在重複時會擲錯；這裡再驗一次總數對得上。
    const idx = textIndex()
    expect(idx.size).toBe(allTexts().length)
    const total = CANONS.reduce((n, c) => n + canonTextCount(c), 0)
    expect(total).toBe(idx.size)
  })

  it('每一部的 parts 所列 volume key 都存在（拼錯會讓整卷從索引頁消失）', () => {
    for (const canon of CANONS) {
      for (const part of canon.parts) {
        const found = volumesOf(canon, part)
        expect(found.length, `${canon.key}/${part.key} 有 volume key 對不上`).toBe(part.volumes.length)
      }
      // 反向：每一卷都要被某個 part 收進去，否則索引頁看不到它
      const claimed = new Set(canon.parts.flatMap(p => p.volumes))
      for (const v of canon.volumes) {
        expect(claimed.has(v.key), `${canon.key}/${v.key} 沒有被任何 part 收錄`).toBe(true)
      }
    }
  })

  it('卷與篇的計數一致', () => {
    for (const canon of CANONS) {
      const sum = canon.volumes.reduce((n, v) => n + volumeTextCount(v), 0)
      expect(canonTextCount(canon)).toBe(sum)
    }
  })
})

describe('摩尼教經典 — 體例（這些數字釘住的是判斷，不是統計）', () => {
  it('正藏的七部大經一部不多一部不少', () => {
    const seven = CANON_CANON.volumes.find(v => v.key === 'seven-treatises')!
    expect(volumeTextCount(seven)).toBe(7)
  })

  it('🚨 七部大經沒有一部是全本——這是本藏經的核心事實', () => {
    const seven = CANON_CANON.volumes.find(v => v.key === 'seven-treatises')!
    const texts = seven.divisions.flatMap(d => d.texts)
    for (const t of texts) {
      expect(t.status, `${t.slug} 不該是全本`).not.toBe('whole')
      expect(t.status, `${t.slug} 不該是闕本`).not.toBe('partial')
    }
  })

  it('佚書與敵證一律註明轉引出處', () => {
    for (const { text } of allTexts()) {
      if (text.status === 'lost-cited' || text.status === 'lost-listed' || text.status === 'hostile') {
        expect(text.via, `${text.slug}（${text.status}）未註明轉引出處`).toBeTruthy()
      }
    }
  })

  it('🚨 敵證必須標等級——沒標就會被當成摩尼教原話引用', () => {
    for (const { text } of allTexts()) {
      if (text.status === 'hostile') {
        expect(text.hostile, `${text.slug} 是敵證卻未標等級`).toBeTruthy()
      }
    }
    // 反過來：敵證藏裡標了 hostile 的，status 也必須是 hostile
    for (const { text } of allTexts()) {
      if (text.hostile) expect(text.status, `${text.slug} 標了等級卻不是敵證`).toBe('hostile')
    }
  })

  it('敵證藏裡唯一的教內文獻（特貝薩抄本）不帶敵證等級', () => {
    const t = findText('tebessa-codex')!
    expect(t.canon.key).toBe('testimonia')
    expect(t.text.hostile).toBeUndefined()
    expect(t.text.status).toBe('fragment')
  })

  it('奧古斯丁逐句引錄的三種標 verbatim——它們是七經僅存原文的載體', () => {
    for (const slug of ['contra-epistulam-fundamenti', 'contra-faustum', 'de-natura-boni']) {
      expect(findText(slug)!.text.hostile, slug).toBe('verbatim')
    }
    // 《阿基勞斯行傳》整本是虛構辯論，不可當史料
    expect(findText('acta-archelai')!.text.hostile).toBe('framed')
  })

  it('🚨 漢文藏的 orig 與 zh 狀態一致（原文即中文，不可兩欄打架）', () => {
    for (const { text, division, canon } of allTexts()) {
      if (canon.key !== 'chinese') continue
      const c = columnsOf(text, division)
      expect(c.orig, `${text.slug} 的原文與繁中欄狀態不一致`).toBe(c.zh)
    }
  })

  it('敦煌三經俱在，且《儀略》《下部讚》為全本', () => {
    const dunhuang = CHINESE_CANON.volumes.find(v => v.key === 'dunhuang')!
    expect(volumeTextCount(dunhuang)).toBe(3)
    expect(findText('yilue')!.text.status).toBe('whole')
    expect(findText('xiabuzan')!.text.status).toBe('whole')
    expect(findText('canjing')!.text.status).toBe('partial')
  })

  it('互見指得到的都解得開，指不到的不擲錯（seealso 可指向待辦）', () => {
    // 《巨人書》在正藏與東方語文藏各有一條，互相指認——這是本藏經互見的典型。
    const giants = findText('book-of-giants')!
    const related = relatedOf(giants.text)
    expect(related.map(r => r.text.slug)).toContain('giants-iranian')
    // 反向也要通
    expect(relatedOf(findText('giants-iranian')!.text).map(r => r.text.slug)).toContain('book-of-giants')
    // 指向不存在的 slug 時靜靜略過，不擲錯
    expect(relatedOf({ slug: 'x', title_zh: 'x', siglum: 'x', seealso: ['does-not-exist'] })).toEqual([])
  })
})

describe('摩尼教經典 — 取源現況要誠實', () => {
  it('繁中欄：除漢文藏外尚無任何一篇上架', () => {
    // 這條會隨翻譯進度改。它存在的意義是：中譯上架時必須有人回來改這個數字，
    // 而不是讓頁面默默宣稱有中文卻是空的。
    // 🚨 漢文藏是例外：那一藏的「繁中」就是原文本身（敦煌三經已上架），
    //    不是翻譯成果，不可混進翻譯進度裡算。
    const t = tallyColumns()
    expect(t.total).toBe(allTexts().length)
    const nonChineseZhReady = allTexts()
      .filter(l => l.canon.key !== 'chinese')
      .filter(l => columnsOf(l.text, l.division).zh === 'ready')
    expect(nonChineseZhReady.map(l => l.text.slug)).toEqual([])
  })

  it('敦煌三經已上架，且正文 JSON 的段數與書目宣稱一致', async () => {
    // 🚨 標 ready 卻沒有正文檔，是這套資料最容易出的錯：
    //    書目頁顯示「已上架」，reader 打開卻是空的，兩邊都不會報錯。
    const { hasText } = await import('~/data/manichaean/sources')
    for (const slug of ['xiabuzan', 'yilue', 'canjing']) {
      const loc = findText(slug)!
      const c = columnsOf(loc.text, loc.division)
      expect(c.orig, `${slug} 原文欄`).toBe('ready')
      expect(c.zh, `${slug} 繁中欄（漢文藏＝原文）`).toBe('ready')
      expect(hasText(slug), `${slug} 標了 ready 卻沒有正文 JSON`).toBe(true)
    }
  })

  it('🚨 凡標 ready 的條目都必須真的有正文檔', async () => {
    const { hasText } = await import('~/data/manichaean/sources')
    for (const loc of allTexts()) {
      const c = columnsOf(loc.text, loc.division)
      if (c.orig === 'ready' || c.en === 'ready' || c.zh === 'ready') {
        expect(hasText(loc.text.slug), `${loc.text.slug} 標了 ready 卻沒有正文 JSON`).toBe(true)
      }
    }
  })

  it('吐魯番那一藏的原文與英譯非 available 即 ready（IAMS 選輯開放取用）', () => {
    // 這一藏的取源條件是五藏中最好的：IAMS 選輯把原文轉寫與英譯逐行並排刊出，
    // 所以不該有 copyright 或 none。已抓下來的轉成 ready，其餘維持 available。
    const iranian = findCanon('iranian')!
    for (const v of iranian.volumes) {
      for (const d of v.divisions) {
        for (const text of d.texts) {
          const c = columnsOf(text, d)
          expect(['available', 'ready'], `${text.slug} 原文欄`).toContain(c.orig)
          expect(['available', 'ready'], `${text.slug} 英譯欄`).toContain(c.en)
        }
      }
    }
  })

  it('IAMS 選輯已抓下來的四篇標 ready，且正文檔真的在', async () => {
    // 🚨 這四篇是過了配對率閘（≥65%）的。沒過閘的不得標 ready——
    //    對齊鍵挑錯時不會報錯，只會產出「兩欄都有東西但錯開一格」的檔。
    const { hasText } = await import('~/data/manichaean/sources')
    for (const slug of ['sabuhragan-turfan', 'book-of-giants', 'epistles', 'psalms-and-prayers']) {
      const loc = findText(slug)!
      const c = columnsOf(loc.text, loc.division)
      expect(c.orig, `${slug} 原文欄`).toBe('ready')
      expect(c.en, `${slug} 英譯欄`).toBe('ready')
      expect(hasText(slug), `${slug} 標了 ready 卻沒有正文 JSON`).toBe(true)
    }
  })

  it('科普特《凱法萊亞》兩部標 copyright——本藏經最大的缺口', () => {
    for (const slug of ['kephalaia-teacher', 'kephalaia-wisdom']) {
      const loc = findText(slug)!
      const c = columnsOf(loc.text, loc.division)
      expect(c.orig, slug).toBe('copyright')
      expect(c.en, slug).toBe('copyright')
    }
  })

  it('奧古斯丁諸書與《阿基勞斯行傳》標 available（ANF／NPNF 公有領域）', () => {
    for (const slug of ['contra-faustum', 'acta-archelai', 'ephrem-refutations']) {
      const loc = findText(slug)!
      expect(columnsOf(loc.text, loc.division).en, slug).toBe('available')
    }
  })

  it('存世狀態統計涵蓋全藏，且佚書佔相當比例', () => {
    const t = tallyStatus()
    const sum = Object.values(t).reduce((a, b) => a + b, 0)
    expect(sum).toBe(allTexts().length)
    // 正藏七經多為佚書，本藏經不該看起來收得滿滿的
    expect((t['lost-cited'] ?? 0) + (t['lost-listed'] ?? 0)).toBeGreaterThanOrEqual(6)
  })
})

describe('摩尼教經典 — 搜尋與檢索', () => {
  it('可用中文、原文轉寫、抄本編號找到同一批東西', () => {
    for (const q of ['巨人', 'Kawān', '下部讚', 'CMC', 'M 1']) {
      expect(searchTexts(q).length, `搜「${q}」找不到`).toBeGreaterThan(0)
    }
  })

  it('可用出土地檢索——這是本藏經的第一屬性', () => {
    expect(searchTexts('吐魯番').length).toBeGreaterThan(0)
    expect(searchTexts('都柏林').length).toBeGreaterThan(0)
    expect(searchTexts('敦煌').length).toBeGreaterThan(0)
  })

  it('空字串不回傳全部', () => {
    expect(searchTexts('')).toEqual([])
    expect(searchTexts('   ')).toEqual([])
  })
})

describe('已上架正文與書目的對應', () => {
  it('每一份正文 JSON 的 slug 都對得上書目', async () => {
    // 🚨 對不上的 JSON，reader 走不到、書目頁照樣顯示——沒有任何地方看得出來。
    const { TEXT_REFS } = await import('~/data/manichaean/sources')
    for (const ref of TEXT_REFS) {
      expect(findText(ref.slug), `正文 ${ref.slug}.json 在書目裡找不到對應條目`).toBeTruthy()
    }
  })

  it('敵證藏不是經典，但仍在總數之內', () => {
    expect(TESTIMONIA_CANON.scriptural).toBe(false)
    expect(canonTextCount(TESTIMONIA_CANON)).toBeGreaterThan(0)
  })
})
