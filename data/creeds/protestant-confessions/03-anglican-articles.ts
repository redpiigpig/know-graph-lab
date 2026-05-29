import type { Creed } from '../types'

export const anglicanArticles: Creed = {
  slug: 'anglican-articles',
  category: 'protestant-confession',
  order: 3003,
  nameZh: '聖公宗三十九條信綱',
  nameEn: 'Thirty-Nine Articles of Religion',
  nameLat: 'Articuli Religionis',
  year: 1571,
  location: '倫敦‧坎特伯里大主教會議',
  topic: '英格蘭教會 1571 確立之信仰宣言；介於宗教改革（路德/加爾文）與羅馬天主教之間的「中道」(via media) 神學立場',
  authors: [
    '坎特伯里大主教 Thomas Cranmer（1553 版「四十二條」原稿）',
    '坎特伯里大主教 Matthew Parker（1571 版定稿）',
    '伊麗莎白一世女王（核可頒佈）',
  ],
  acceptedBy: ['anglican', 'protestant'],
  displayMode: 'simple',
  versions: [
    {
      lang: 'zh-Hant-Catholic',
      label: '天主教中文版（Denzinger DH 5524-5562 摘錄）',
      text: '',
      textKey: 'anglican-articles-chinese',
      source: '《公教會之信仰與倫理教義選集》（Denzinger 中譯）— 光啟文化 2013 / ISBN 9789575467418，附錄五。',
      translator: '輔仁神學著作編譯會（紙本）',
    },
    {
      lang: 'en',
      label: 'English (1571 official text, 待補)',
      text: '',
      placeholder: true,
      source: 'Church of England Book of Common Prayer (BCP 1662) Appendix.',
    },
    {
      lang: 'lat',
      label: '拉丁原文（1563 Convocation 版，待補）',
      text: '',
      placeholder: true,
      source: '1563 Latin text approved by Convocation of Canterbury.',
    },
    {
      lang: 'zh-Hant-Anglican',
      label: '香港聖公會 / 中華聖公會中譯本（待補）',
      text: '',
      placeholder: true,
      source: '《公禱書》(Book of Common Prayer) 香港聖公會中譯本附錄。',
    },
  ],
  summaryZh: `1571 年伊麗莎白一世時期由坎特伯里大主教 Matthew Parker 主持定稿、由女王與議會核可頒佈的英格蘭教會官方信仰宣言。其雛形為 1553 年 Thomas Cranmer 起草的「四十二條」，瑪麗一世（天主教）時期遭廢止，伊麗莎白即位後修訂為現行 39 條。

本信條反映聖公宗「中道」(via media) 神學立場：在「聖經為信仰最高權威」「因信稱義」「兩件聖事（聖洗、聖餐）」等議題上呼應路德／加爾文宗教改革；同時保留主教制 (episcopacy)、禮儀傳統、《公禱書》(Book of Common Prayer)、使徒統緒等中世紀天主教遺產。

39 條至今仍是聖公宗 (Anglican Communion) 全球各地方教會的信仰參考基準之一，但具體解釋彈性甚大 — 高教會派 (Anglo-Catholic) 與低教會派 (Evangelical) 對若干條款有差異化詮釋。`,
  notes: `- 1553 Cranmer 起草「四十二條」（Forty-Two Articles）→ Mary I 廢止
- 1563 Convocation 修訂為 38 條 → 1571 確立 39 條最終版本
- 1571 經伊麗莎白一世與英國議會核可頒佈
- 三十九條主要架構：1-8 信仰要道；9-18 個人救恩；19-31 公禱書與聖事；32-39 教會與政治關係
- 接受傳統：聖公宗全球各教省；衛理宗（John Wesley 1784 修訂為「25 條」自用）也部分繼承
- 中譯來源：Denzinger 第 43 版（光啟 2013）僅收 DH 5524-5562 摘錄
- 「中道」(via media) 神學定位由 Richard Hooker 在《教會政治法理》(Of the Laws of Ecclesiastical Polity, 1593) 系統化闡述`,
  related: ['augsburg-confession', 'reformed-belgic'],
}
