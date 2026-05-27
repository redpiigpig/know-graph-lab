import type { PapalDocument } from '../types'

export const deusCaritasEst2005: PapalDocument = {
  slug: 'deus-caritas-est-2005',
  popeSlug: 'benedict-xvi',
  category: 'encyclical',
  titleLat: 'Deus Caritas Est',
  titleEn: 'God Is Love',
  titleZh: '《天主是愛》通諭 — 論基督徒之愛',
  promulgationDate: '2005-12-25',
  century: 21,
  summaryZh: `教宗本篤十六世第一道通諭，於就任後 8 個月頒布，刻意選擇聖誕節這個基督徒「愛的奧蹟」核心節期作為頒布日。全文 42 段，分兩部分。

第一部分（1-18 段）「在創造及救恩史中愛的一致性」是本通諭最具神學原創性的部分。本篤十六世以希臘哲學「性愛」（eros）與聖經「純愛」（agape）兩概念入手，反駁尼采「基督教毒化了 eros」的批評，論證 eros 與 agape 並非對立，而是同一個愛的不同向度。當代「愛」概念被簡化為性慾、被消費主義工具化的處境下，本通諭重新整合愛的內在統一性。

第二部分（19-42 段）「在教會的『愛的事工』中愛的踐行」處理教會慈善與正義工作的神學基礎。本篤強調慈善工作（caritas）不是教會的「可有可無的選項」，而是教會內在本質的三大職能之一（kerygma 宣道 / leitourgia 禮儀 / diakonia 服事）。`,
  topics: ['愛德', '神哲學', '性愛與純愛', '社會訓導', '教會慈善', '正義與愛'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（天主教會臺灣地區主教團 譯，繁中由簡中轉換）',
      textKey: 'deus-caritas-est-2005-chinese',
      source: 'https://www.vatican.va/content/dam/benedict-xvi/pdf/encyclicals/documents/hf_ben-xvi_enc_20051225_deus-caritas-est_zh.pdf',
      translator: '天主教會臺灣地區主教團（vatican.va 上線為簡中，本站轉繁中）',
    },
    {
      lang: 'en',
      label: '英文 (vatican.va)',
      textKey: 'deus-caritas-est-2005-english',
      source: 'https://www.vatican.va/content/benedict-xvi/en/encyclicals/documents/hf_ben-xvi_enc_20051225_deus-caritas-est.html',
    },
    {
      lang: 'lat',
      label: '拉丁原文 (vatican.va)',
      textKey: 'deus-caritas-est-2005-latin',
      source: 'https://www.vatican.va/content/benedict-xvi/la/encyclicals/documents/hf_ben-xvi_enc_20051225_deus-caritas-est.html',
    },
    {
      lang: 'it',
      label: '義大利文 (vatican.va，本篤十六起草語)',
      textKey: 'deus-caritas-est-2005-italian',
      source: 'https://www.vatican.va/content/benedict-xvi/it/encyclicals/documents/hf_ben-xvi_enc_20051225_deus-caritas-est.html',
      placeholder: false,
    },
  ],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/benedict-xvi/en/encyclicals/documents/hf_ben-xvi_enc_20051225_deus-caritas-est.html',
  related: ['spe-salvi-2007', 'caritas-in-veritate-2009', 'lumen-fidei-2013'],
  notes: `頒布日 2005-12-25 聖誕節是本篤十六世選擇的象徵性日期：聖誕節是基督徒紀念「天主之愛降生成人」的節日，與通諭主題「天主是愛」直接呼應。

本篤本人是德國神學家（拉辛格樞機，前 CDF 信理部部長 1981-2005），通諭起草語為其母語德文，正式版以義大利文先發布。vatican.va 中文版為「天主教會臺灣地區主教團」於 2006 年完成的官方繁中譯本，但 vatican.va 上線時誤上傳為簡中檔案，本站經 opencc s2tw 自動轉換為繁中。

第 25 段：「教會不能也不應自己擔負政治的責任，去推動最公義的社會。她不能也不應取代國家。但她也不能也不應遠離正義之爭。」此段成為日後天主教「政治倫理」討論中最常被引用的方濟教義基礎之一。`,
}
