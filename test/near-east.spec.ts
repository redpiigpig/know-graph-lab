import { describe, expect, it } from 'vitest'
import {
  CANONS,
  allTexts,
  canonTextCount,
  findText,
  relatedOf,
  searchTexts,
  tallyColumns,
  tallyStatus,
  textIndex,
  volumeTextCount,
} from '~/data/near-east'

describe('古近東大藏經 — 結構', () => {
  it('八藏＋附錄，只有附錄非經典', () => {
    expect(CANONS.map(c => c.key)).toEqual([
      'egypt', 'sumer', 'akkad', 'anatolia', 'ugarit', 'levant', 'arabia', 'highlands', 'testimonia',
    ])
    expect(CANONS.filter(c => !c.scriptural).map(c => c.key)).toEqual(['testimonia'])
  })

  it('slug 全藏唯一，計數一致', () => {
    const idx = textIndex()
    expect(idx.size).toBe(allTexts().length)
    expect(CANONS.reduce((n, c) => n + canonTextCount(c), 0)).toBe(idx.size)
  })

  it('卷 key 與卷次符號在藏內唯一', () => {
    for (const c of CANONS) {
      const keys = c.volumes.map(v => v.key)
      const sigils = c.volumes.map(v => v.sigil)
      expect(new Set(keys).size, `${c.key} 卷 key 重複`).toBe(keys.length)
      expect(new Set(sigils).size, `${c.key} 卷次符號重複`).toBe(sigils.length)
    }
  })

  it('沒有空卷、空部', () => {
    for (const c of CANONS) {
      for (const v of c.volumes) {
        expect(volumeTextCount(v), `${c.key}/${v.key} 是空卷`).toBeGreaterThan(0)
        for (const d of v.divisions) expect(d.texts.length, `${c.key}/${v.key}/${d.key} 是空部`).toBeGreaterThan(0)
      }
    }
  })

  it('🚨 seealso 不得懸空（指錯 slug 會讓互見靜默消失）', () => {
    for (const { text } of allTexts()) {
      for (const s of text.seealso ?? []) {
        expect(findText(s), `${text.slug} 的互見 '${s}' 找不到`).toBeTruthy()
      }
      expect(relatedOf(text).length).toBe((text.seealso ?? []).length)
    }
  })
})

describe('古近東大藏經 — 體例', () => {
  it('佚書一律註明轉引出處', () => {
    for (const { text } of allTexts()) {
      if (text.status === 'lost-cited' || text.status === 'lost-listed') {
        expect(text.via, `${text.slug}（${text.status}）未註明轉引出處`).toBeTruthy()
      }
    }
  })

  it('每一藏都寫明下限的依據（各藏止於自己的文字死亡）', () => {
    for (const c of CANONS) expect(c.terminus.length, `${c.key} 沒寫下限依據`).toBeGreaterThan(10)
  })

  it('🚨 蘇美藏的編號一律是 ETCSL（不自編）', () => {
    const sumer = allTexts().filter(l => l.canon.key === 'sumer' && l.text.siglum)
    expect(sumer.length).toBeGreaterThan(40)
    for (const { text } of sumer) expect(text.siglum, text.slug).toMatch(/^ETCSL \d/)
  })

  it('🚨 赫梯藏前八卷有編號者一律是 CTH', () => {
    const hit = allTexts().filter(l => l.canon.key === 'anatolia' && l.volume.key !== 'iron-age' && l.text.siglum)
    for (const { text } of hit) expect(text.siglum, text.slug).toMatch(/^(CTH \d|RS )/)
  })

  it('烏加里特藏一律用 KTU 編號', () => {
    for (const { text } of allTexts().filter(l => l.canon.key === 'ugarit')) {
      expect(text.siglum, text.slug).toMatch(/KTU 1\.\d/)
    }
  })

  it('希伯來聖經不入藏：沒有任何條目的語言是聖經希伯來文的正典書卷', () => {
    // 以色列與猶大只收銘文；收錄的古希伯來語條目必須是銘文或殘篇
    for (const { text } of allTexts().filter(l => l.text.language === '古希伯來語')) {
      expect(['inscription', 'fragment']).toContain(text.status)
    }
  })

  it('使用者定名（2026-10-02）落實在資料裡', () => {
    const all = JSON.stringify(CANONS)
    for (const bad of ['馬爾杜克', '吾珥', '以攔', '搭模斯', '書珊', '西台']) {
      expect(all.includes(bad), `資料裡還有「${bad}」`).toBe(false)
    }
    for (const good of ['馬杜克', '伊絲塔', '烏爾', '埃蘭', '杜牧茲', '蘇薩', '赫梯']) {
      expect(all.includes(good), `資料裡沒有「${good}」`).toBe(true)
    }
  })
})

describe('古近東大藏經 — 統計與搜尋', () => {
  it('三欄與狀態統計的分母等於全藏篇數', () => {
    const total = allTexts().length
    const t = tallyColumns()
    for (const col of ['orig', 'en', 'zh'] as const) {
      expect(Object.values(t[col]).reduce((a, b) => a + b, 0)).toBe(total)
    }
    expect(Object.values(tallyStatus()).reduce((a, b) => a + b, 0)).toBe(total)
  })

  it('搜尋吉爾伽美什找得到蘇美與阿卡德兩藏', () => {
    const canons = new Set(searchTexts('吉爾伽美什').map(l => l.canon.key))
    expect(canons.has('sumer')).toBe(true)
    expect(canons.has('akkad')).toBe(true)
  })
})
