/**
 * Pope catalog — 教宗名錄
 *
 * 起始策略（2026-05-27 user 確認）：21 世紀往回做，方濟各 → 本篤十六 → 若望保祿二 → ...
 * 良十四世（Leo XIV, 2025-）暫不收錄，缺官方中譯。
 *
 * 4-15c 早期教宗在後續 Phase 5（等 [[fathers]] 中譯成熟後）回頭補。
 */

import type { Pope } from './types'

export const POPES: Pope[] = [
  // ── 21 世紀 ──────────────────────────────────────────────
  {
    slug: 'francis',
    nameZh: '方濟各',
    nameEn: 'Francis',
    nameLat: 'Franciscus',
    birthName: 'Jorge Mario Bergoglio',
    pontificateStart: '2013-03-13',
    pontificateEnd: '2025-04-21',
    century: 21,
    nationality: '阿根廷',
    notesZh: '第 266 任教宗。第一位來自美洲與南半球、亦為首位耶穌會出身的教宗。任內以社會訓導（《願祢受讚頌》通諭論生態危機、《眾位弟兄》通諭論友愛與社會友誼）、改革羅馬教廷組織（2022 年使徒憲令《你們去宣講福音》Praedicate Evangelium）與牧靈面向（《福音的喜樂》宗座勸諭）見稱。',
  },
  {
    slug: 'benedict-xvi',
    nameZh: '本篤十六世',
    nameEn: 'Benedict XVI',
    nameLat: 'Benedictus PP. XVI',
    birthName: 'Joseph Aloisius Ratzinger',
    pontificateStart: '2005-04-19',
    pontificateEnd: '2013-02-28',
    century: 21,
    nationality: '德國',
    notesZh: '第 265 任教宗。原任教義部部長（前身為信理部），任內頒布三道「神學三部曲」通諭：《天主是愛》(2005)、《在希望中得救》(2007)、《在真理中的愛德》(2009)。2013 年自願請辭，為近 600 年來首位生前退位的教宗。',
  },

  // ── 20 世紀 ──────────────────────────────────────────────
  {
    slug: 'john-paul-ii',
    nameZh: '若望保祿二世',
    nameEn: 'John Paul II',
    nameLat: 'Ioannes Paulus PP. II',
    birthName: 'Karol Józef Wojtyła',
    pontificateStart: '1978-10-16',
    pontificateEnd: '2005-04-02',
    century: 20,
    nationality: '波蘭',
    notesZh: '第 264 任教宗。455 年來首位非義大利籍教宗。在位 26 年餘，頒布 14 道通諭，是近代訓導文獻最豐沛的教宗之一。代表作含《人類救主》(1979)、《真理的光輝》(1993)、《生命的福音》(1995)、《信仰與理性》(1998)、《願他們合而為一》(1995)。',
  },
  {
    slug: 'john-paul-i',
    nameZh: '若望保祿一世',
    nameEn: 'John Paul I',
    nameLat: 'Ioannes Paulus PP. I',
    birthName: 'Albino Luciani',
    pontificateStart: '1978-08-26',
    pontificateEnd: '1978-09-28',
    century: 20,
    nationality: '義大利',
    notesZh: '第 263 任教宗。在位僅 33 天即逝世。未頒布通諭。',
  },
  {
    slug: 'paul-vi',
    nameZh: '保祿六世',
    nameEn: 'Paul VI',
    nameLat: 'Paulus PP. VI',
    birthName: 'Giovanni Battista Enrico Antonio Maria Montini',
    pontificateStart: '1963-06-21',
    pontificateEnd: '1978-08-06',
    century: 20,
    nationality: '義大利',
    notesZh: '第 262 任教宗。繼若望二十三世主持完成梵二大公會議。頒布 7 道通諭，含 1968 年具爭議性的《人類生命》通諭，重申天主教對人工避孕的立場。',
  },
  {
    slug: 'john-xxiii',
    nameZh: '若望二十三世',
    nameEn: 'John XXIII',
    nameLat: 'Ioannes PP. XXIII',
    birthName: 'Angelo Giuseppe Roncalli',
    pontificateStart: '1958-10-28',
    pontificateEnd: '1963-06-03',
    century: 20,
    nationality: '義大利',
    notesZh: '第 261 任教宗。1962 年召開梵二大公會議。代表通諭《和平於世》(1963) 首次將通諭收件對象擴及「所有善意人士」。',
  },
  {
    slug: 'pius-xii',
    nameZh: '碧岳十二世',
    nameEn: 'Pius XII',
    nameLat: 'Pius PP. XII',
    birthName: 'Eugenio Maria Giuseppe Giovanni Pacelli',
    pontificateStart: '1939-03-02',
    pontificateEnd: '1958-10-09',
    century: 20,
    nationality: '義大利',
    notesZh: '第 260 任教宗。頒布 41 道通諭。1943 年《在聖神默感之下》(Divino Afflante Spiritu) 開啟現代天主教聖經研究；1950 年使徒憲令《廣施恩寵的天主》(Munificentissimus Deus) 定義聖母蒙召升天信理。',
  },
  {
    slug: 'pius-xi',
    nameZh: '碧岳十一世',
    nameEn: 'Pius XI',
    nameLat: 'Pius PP. XI',
    birthName: 'Ambrogio Damiano Achille Ratti',
    pontificateStart: '1922-02-06',
    pontificateEnd: '1939-02-10',
    century: 20,
    nationality: '義大利',
    notesZh: '第 259 任教宗。1929 年與義大利簽訂《拉特朗條約》，建立梵蒂岡城國。代表通諭《貞潔婚姻》(1930)、《四十年》(1931，紀念《新事》40 周年的社會訓導續篇)、《以憂傷的關切》(1937 德文，譴責納粹)。',
  },
  {
    slug: 'benedict-xv',
    nameZh: '本篤十五世',
    nameEn: 'Benedict XV',
    nameLat: 'Benedictus PP. XV',
    birthName: 'Giacomo Paolo Giovanni Battista della Chiesa',
    pontificateStart: '1914-09-03',
    pontificateEnd: '1922-01-22',
    century: 20,
    nationality: '義大利',
    notesZh: '第 258 任教宗。一戰期間極力斡旋和平。代表通諭《撫慰至深》(1914，反戰)、《撫慰至切》(1920，論慈愛)。',
  },
  {
    slug: 'pius-x',
    nameZh: '碧岳十世',
    nameEn: 'Pius X',
    nameLat: 'Pius PP. X',
    birthName: 'Giuseppe Melchiorre Sarto',
    pontificateStart: '1903-08-04',
    pontificateEnd: '1914-08-20',
    century: 20,
    nationality: '義大利',
    notesZh: '第 257 任教宗。1907 年《應牧放主羊》(Pascendi Dominici Gregis) 大力譴責現代主義。1954 年封聖。',
  },

  // ── 19 世紀 ──────────────────────────────────────────────
  {
    slug: 'leo-xiii',
    nameZh: '良十三世',
    nameEn: 'Leo XIII',
    nameLat: 'Leo PP. XIII',
    birthName: 'Vincenzo Gioacchino Raffaele Luigi Pecci',
    pontificateStart: '1878-02-20',
    pontificateEnd: '1903-07-20',
    century: 19,
    nationality: '義大利',
    notesZh: '第 256 任教宗。頒布 88 道通諭，現代教廷通諭體裁的奠定者。1891 年《新事》(Rerum Novarum) 開啟近代天主教社會訓導傳統，至今每 10 年由後繼教宗紀念續寫。',
  },
  {
    slug: 'pius-ix',
    nameZh: '碧岳九世',
    nameEn: 'Pius IX',
    nameLat: 'Pius PP. IX',
    birthName: 'Giovanni Maria Mastai-Ferretti',
    pontificateStart: '1846-06-16',
    pontificateEnd: '1878-02-07',
    century: 19,
    nationality: '義大利',
    notesZh: '第 255 任教宗。在位 31 年餘，史上最長。1854 年使徒憲令《不可言傳的天主》(Ineffabilis Deus) 定義聖母無染原罪信理；1864 年《我們是何等關切》(Quanta Cura) 附《當代謬論彙編》(Syllabus Errorum)；1869-70 召開梵一大公會議，確立教宗無謬論信理。',
  },
]

export function findPope(slug: string): Pope | undefined {
  return POPES.find(p => p.slug === slug)
}

/** 依 pontificate 起訖推算教宗任期所跨的世紀（含起訖兩端）。
 *  例：John Paul II 1978-2005 → [20, 21]；Leo XIII 1878-1903 → [19, 20]。
 *  在位中（pontificateEnd 空字串）以當下年份計。 */
export function centuriesOfPope(p: Pope): number[] {
  const startY = parseInt(p.pontificateStart.slice(0, 4), 10)
  const endY = p.pontificateEnd
    ? parseInt(p.pontificateEnd.slice(0, 4), 10)
    : new Date().getFullYear()
  const cStart = Math.floor((startY - 1) / 100) + 1
  const cEnd = Math.floor((endY - 1) / 100) + 1
  const out: number[] = []
  for (let c = cStart; c <= cEnd; c++) out.push(c)
  return out
}

/** 按世紀分組教宗（新→舊）。跨世紀的教宗會在兩邊都出現。 */
export function popesByCentury(): { century: number; popes: Pope[] }[] {
  const map = new Map<number, Pope[]>()
  for (const p of POPES) {
    for (const c of centuriesOfPope(p)) {
      if (!map.has(c)) map.set(c, [])
      map.get(c)!.push(p)
    }
  }
  return [...map.entries()]
    .sort((a, b) => b[0] - a[0])
    .map(([century, popes]) => ({
      century,
      popes: popes.sort((a, b) => b.pontificateStart.localeCompare(a.pontificateStart)),
    }))
}

export function popesInCentury(century: number): Pope[] {
  return POPES
    .filter(p => centuriesOfPope(p).includes(century))
    .sort((a, b) => b.pontificateStart.localeCompare(a.pontificateStart))
}
