// Shared /gnostic display metadata — category order + labels + language labels.
// Mirrors CATEGORIES in scripts/gnostic_library.py (keys must stay in sync).

export const CATEGORY_ORDER: { key: string; label: string; label_en: string }[] = [
  { key: 'nag_hammadi',         label: '拿戈瑪第經集',       label_en: 'Nag Hammadi Library' },
  { key: 'gnostic_scriptures',  label: '古典諾斯底經典',     label_en: 'Classic Gnostic Scriptures' },
  { key: 'valentinus',          label: '瓦倫廷與其傳統',     label_en: 'Valentinus & His Tradition' },
  { key: 'hermetica',           label: '赫密士文集',         label_en: 'Corpus Hermeticum' },
  { key: 'mead',                label: 'G.R.S. Mead 文集',   label_en: 'GRS Mead Collection' },
  { key: 'manichaean',          label: '摩尼教文獻',         label_en: 'Manichaean Writings' },
  { key: 'mandaean',            label: '曼達教文獻',         label_en: 'Mandaean Writings' },
  { key: 'cathar',              label: '卡特里派文獻',       label_en: 'Cathar Writings' },
  { key: 'polemics',            label: '教父駁斥諾斯底文獻', label_en: 'Patristic Polemical Works' },
  { key: 'christian_apocrypha', label: '基督教偽典',         label_en: 'Christian Apocrypha' },
  { key: 'alchemical',          label: '煉金術文獻',         label_en: 'Alchemical Writings' },
  { key: 'modern',              label: '現代文獻與近代學術', label_en: 'Modern Texts & Scholarship' },
  { key: 'dead_sea',            label: '死海古卷',           label_en: 'Dead Sea Scrolls' },
]

const CATEGORY_LABEL: Record<string, string> = Object.fromEntries(
  CATEGORY_ORDER.map(c => [c.key, c.label]),
)
export function categoryLabel(key: string): string {
  return CATEGORY_LABEL[key] || key
}

const LANG_LABEL: Record<string, string> = {
  coptic: '科普特文', greek: '希臘文', syriac: '敘利亞文', mandaic: '曼達文',
  latin: '拉丁文', hebrew: '希伯來文', aramaic: '亞蘭文', persian: '波斯文',
}
export function languageLabel(key: string): string {
  return LANG_LABEL[key] || key
}
