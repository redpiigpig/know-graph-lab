import { describe, expect, it } from 'vitest'
import {
  ENTRIES, FULLTEXT_LABEL, KIND_LABEL, LANG_LABEL, RELIGION_META, THEME_META,
  columnsFor, entriesFor, findEntry, tallyFulltext, tallyReligion,
} from '~/data/sanyijiao'

describe('三夷教研究資料書目', () => {
  it('ref 全庫唯一——重複會讓兩筆共用一頁而版面正常', () => {
    expect(new Set(ENTRIES.map(e => e.ref)).size).toBe(ENTRIES.length)
  })

  it('每筆的列舉欄位都在合法值域內', () => {
    for (const e of ENTRIES) {
      expect(e.ref, `${e.title} 的 ref 不合法`).toMatch(/^[a-z0-9-]+$/)
      expect(RELIGION_META[e.religion], `${e.ref} religion 不合法`).toBeTruthy()
      expect(THEME_META[e.theme], `${e.ref} theme 不合法`).toBeTruthy()
      expect(KIND_LABEL[e.kind], `${e.ref} kind 不合法`).toBeTruthy()
      expect(FULLTEXT_LABEL[e.fulltext], `${e.ref} fulltext 不合法`).toBeTruthy()
      expect(e.authors.trim().length, `${e.ref} 缺作者`).toBeGreaterThan(0)
    }
  })

  it('非中文條目必須有中譯書名，否則列表全是外文', () => {
    for (const e of ENTRIES) {
      if (e.lang !== 'zh') {
        expect(e.title_zh, `${e.ref}（${e.lang}）缺 title_zh`).toBeTruthy()
      }
    }
  })

  it('互見必須雙向且指得到——單向互見等於有一邊看不到辯論的另一半', () => {
    for (const e of ENTRIES) {
      if (!e.seealso) continue
      const other = findEntry(e.seealso)
      expect(other, `${e.ref} 的互見 ${e.seealso} 找不到`).toBeTruthy()
      expect(other!.seealso, `${other!.ref} 沒有回指 ${e.ref}`).toBe(e.ref)
    }
  })

  it('大明國號之爭的兩造都在，且互相指到', () => {
    // 只收吳晗不收楊訥，等於把一場仍在進行的辯論寫成定論
    const wu = findEntry('wu-han-damingdiguo')!
    const yang = findEntry('yang-ne-bailianjiao')!
    expect(wu.seealso).toBe(yang.ref)
    expect(yang.seealso).toBe(wu.ref)
  })

  it('跨教通論對每一教都算數，不只出現在一個分頁', () => {
    const zoro = entriesFor('zoroastrian').map(e => e.ref)
    const mani = entriesFor('manichaean').map(e => e.ref)
    // 《中古三夷教辨證》一本涵蓋三教
    expect(zoro).toContain('lin-wushu-sanyijiao')
    expect(mani).toContain('lin-wushu-sanyijiao')
  })

  it('兩教都有實質收錄', () => {
    const t = tallyReligion()
    expect(t.zoroastrian ?? 0).toBeGreaterThan(15)
    expect(t.manichaean ?? 0).toBeGreaterThan(10)
    expect(t.cross ?? 0).toBeGreaterThan(0)
  })
})

describe('語言呈現規則（user 2026-09-06 定）', () => {
  it('英文原著出兩欄：英文原文／繁體中文', () => {
    const cols = columnsFor('en')
    expect(cols.map(c => c.key)).toEqual(['orig', 'zh'])
  })

  it('非英文原著出三欄：原文／英譯／繁體中文', () => {
    for (const lang of ['ja', 'de', 'fr', 'fa']) {
      const cols = columnsFor(lang)
      expect(cols.map(c => c.key), `${lang} 欄數不對`).toEqual(['orig', 'en', 'zh'])
      expect(cols[0].label).toContain(LANG_LABEL[lang])
    }
  })

  it('中文原著只出原文一欄——沒有翻譯問題', () => {
    expect(columnsFor('zh').map(c => c.key)).toEqual(['orig'])
  })

  it('🚨 任何語言都不會出現「只有中譯」的欄組合', () => {
    for (const lang of ['en', 'zh', 'ja', 'de', 'fr', 'fa', 'ru', 'gu']) {
      const keys = columnsFor(lang).map(c => c.key)
      expect(keys, `${lang} 只出了中譯欄`).not.toEqual(['zh'])
      expect(keys[0], `${lang} 的第一欄不是原文`).toBe('orig')
    }
  })

  it('取源現況統計加總等於書目總數', () => {
    const t = tallyFulltext()
    expect(Object.values(t).reduce((a, b) => a + b, 0)).toBe(ENTRIES.length)
  })
})
