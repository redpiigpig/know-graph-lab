import type { PapalDocument } from '../types'

export const responsaBulgarorum866: PapalDocument = {
  slug: 'responsa-bulgarorum-866',
  popeSlug: 'nicholas-i',
  category: 'epistola',
  titleLat: 'Responsa ad consulta Bulgarorum',
  titleEn: 'Responses to the Questions of the Bulgars',
  titleZh: '《對保加利亞人疑問之答覆》★★★ — 對 Khan Boris 106 問答（中世紀東西教會交涉典範）',
  promulgationDate: '866-11-13',
  century: 9,
  summaryZh: `教宗尼閣一世 866 年 11 月 13 日致保加利亞 Khan Boris 的書信（Letter 99 in MGH Epistolae VI），回應保加利亞人剛皈依基督信仰後提出的 106 個生活、禮儀、信理疑問。Boris 於 864 年受洗後一度仰賴君士坦丁堡 Photius，後因 Photius 對保加利亞教會自治的處理引發摩擦，遂轉向羅馬教廷請示。本文是中世紀「東西教會在保加利亞」的關鍵交涉文件——包含齋戒守則／婚姻倫理／戰爭與獵殺／法律與司法／異教習俗的處理／巫術問題／聖事與禮儀／神職人員規範等百多項主題。其中第 6 章談「Roman customs vs Greek customs」、第 31 章談異教祭祀飲食、第 41 章談 polygamy、第 75 章談 Christianization 過程中的妥協原則等，是研究中世紀 inculturation 神學最豐富的單份史料。本對話也直接導致 867 年 Photius 與羅馬教廷的關係破裂（Photian Schism 起點）。`,
  topics: ['保加利亞皈依', '東西教會', 'Photian Schism', 'Inculturation', '中世紀禮儀', '婚姻倫理'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'responsa-bulgarorum-866-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文 (Fordham — Internet Medieval Sourcebook)',
      textKey: 'responsa-bulgarorum-866-english',
      source: 'https://sourcebooks.fordham.edu/basis/866nicholas-bulgar.asp',
    },
    {
      lang: 'lat',
      label: '拉丁原文（待補 — Migne PL 119）',
      textKey: 'responsa-bulgarorum-866-latin',
      placeholder: true,
    },
  ],
  displayMode: 'paragraph-aligned',
}
