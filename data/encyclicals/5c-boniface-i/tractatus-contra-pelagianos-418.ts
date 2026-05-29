import type { PapalDocument } from '../types'

export const tractatusContraPelagianos418: PapalDocument = {
  slug: 'tractatus-contra-pelagianos-418',
  popeSlug: 'boniface-i',
  category: 'epistola',
  titleLat: 'Tractatus contra Pelagianos',
  titleEn: 'Treatise Against the Pelagians',
  titleZh: '《反 Pelagian 論》',
  promulgationDate: '418-09-30',
  century: 5,
  summaryZh: `教宗博尼法一世 418 年延續前任 Zosimus 對 Pelagianism 的譴責立場，並支持 Carthage 第十六會議的 9 條 anti-Pelagian canons（《Indiculus》一部分）。是 5c 前期 Pelagian 論辯的西方教廷終結性訓導文件。文獻收 DH 222-230 範圍。`,
  topics: ['Pelagian 論辯', '418 Carthage canons', 'Augustine 神學支持'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'tractatus-contra-pelagianos-418-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文（待補）',
      textKey: 'tractatus-contra-pelagianos-418-english',
      placeholder: true,
    },
    {
      lang: 'lat',
      label: '拉丁原文（待補 — Migne PL 20）',
      textKey: 'tractatus-contra-pelagianos-418-latin',
      placeholder: true,
    },
  ],
  displayMode: 'paragraph-aligned',
}
