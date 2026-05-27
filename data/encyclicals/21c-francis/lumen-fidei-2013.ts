import type { PapalDocument } from '../types'

export const lumenFidei2013: PapalDocument = {
  slug: 'lumen-fidei-2013',
  popeSlug: 'francis',
  category: 'encyclical',
  titleLat: 'Lumen Fidei',
  titleEn: 'On Faith',
  titleZh: '《信德之光》通諭',
  promulgationDate: '2013-06-29',
  century: 21,
  summaryZh: `教宗方濟各上任後三個月內頒布的第一道通諭，亦是方濟各與本篤十六世兩位教宗合著的特殊文件。本通諭以本篤十六世留下的草稿為主體（本意是與《天主是愛》《在希望中得救》《在真理中實踐愛》合成「德三部曲」的最後一卷），方濟各接續完成並署名頒布。

全文 60 段，分四章，論「信」、「愛」、「望」三超德之間的關係。第一章追溯亞巴郎、梅瑟、以色列傳統中的信德起源；第二章把信德置於認識真理的脈絡裡；第三章論信德與教會傳遞（聖事、信經、十誡、祈禱）的關係；第四章論信德與家庭、社會、痛苦等具體生活面向。`,
  topics: ['信德', '神學', '愛德', '望德', '本篤十六世遺稿', '基督論', '教會傳承'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（天主教會臺灣地區主教團 譯）',
      textKey: 'lumen-fidei-2013-chinese',
      source: 'https://www.vatican.va/content/francesco/zh_tw/encyclicals/documents/papa-francesco_20130629_enciclica-lumen-fidei.html',
      translator: '天主教會臺灣地區主教團',
    },
    {
      lang: 'en',
      label: '英文 (vatican.va)',
      textKey: 'lumen-fidei-2013-english',
      source: 'https://www.vatican.va/content/francesco/en/encyclicals/documents/papa-francesco_20130629_enciclica-lumen-fidei.html',
    },
    {
      lang: 'lat',
      label: '拉丁原文 (vatican.va)',
      textKey: 'lumen-fidei-2013-latin',
      source: 'https://www.vatican.va/content/francesco/la/encyclicals/documents/papa-francesco_20130629_enciclica-lumen-fidei.html',
    },
  ],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/francesco/en/encyclicals/documents/papa-francesco_20130629_enciclica-lumen-fidei.html',
  related: ['deus-caritas-est-2005', 'spe-salvi-2007', 'caritas-in-veritate-2009'],
  notes: `第 7 段方濟各親自承認本通諭主體出自本篤十六世手筆：「本篤十六世在這文獻的初稿上已做了很多寶貴的工作，我深感謝意；當我有幸接續他的牧職時，我加入了自己的看法。我把這通諭頒布為他思想的延續。」

頒布日 2013-06-29 是聖伯多祿與聖保祿瞻禮（兩大宗徒節日），刻意呼應通諭「信德的傳遞」核心主題。`,
}
