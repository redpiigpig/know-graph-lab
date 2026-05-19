/**
 * 演講活動紀錄 store
 *
 * /speech 列表 + /speech/[id] 單場逐字稿。
 * 逐字稿存在 public/content/speech/${id}.md；PPT 存在 R2 (talks-ppt/...)。
 */
import { defineStore } from 'pinia'

export type TalkCategory =
  | 'lecture' // 學系專題講座 / 短期課程
  | 'seminar' // 研討會專題演講
  | 'public' // 公開講座 / 教會 / NGO
  | 'invited' // 受邀演講
  | 'panel' // 論壇與談

export interface Talk {
  id: string
  title: string
  subtitle?: string
  date: string // YYYY-MM-DD
  duration?: string // 例：08:30–10:15
  venue: string // 場地
  organizer: string // 主辦單位
  course?: string // 對應課程（如：宗教社會學 ‧ 專題演講）
  category: TalkCategory
  hasTranscript: boolean
  pptR2Key?: string // talks-ppt/2026-05-19-hsuanchuang.pptx
  description?: string
  posterPath?: string // /api/speech/poster/[id] — 走 R2 signed URL 302 redirect
}

export const useSpeechStore = defineStore('speech', () => {
  const talks = ref<Talk[]>([
    {
      id: '2026-05-19-hsuanchuang',
      title: '台灣佛教具有「民主基因」嗎？',
      subtitle: '從《民主妙法》談三大教團的制度演進與政教互動',
      date: '2026-05-19',
      duration: '08:30–10:15',
      venue: '玄奘大學 妙然樓 M401 教室',
      organizer: '玄奘大學宗教與文化學系',
      course: '宗教社會學 ‧ 專題演講',
      category: 'lecture',
      hasTranscript: true,
      pptR2Key: 'talks-ppt/2026-05-19-hsuanchuang.pptx',
      posterPath: '/api/speech/poster/2026-05-19-hsuanchuang',
      description:
        '以美國加大聖地亞哥分校社會學榮譽教授 Richard Madsen（趙文詞）2007 年著作 Democracy\'s Dharma《民主妙法》為對話起點，' +
        '回顧三大教團（法鼓山／慈濟／佛光山）在解嚴前後的制度演進，並用 2007 年之後近廿年的演變回頭檢驗其結論。',
    },
  ])

  const sorted = computed(() => [...talks.value].sort((a, b) => b.date.localeCompare(a.date)))

  return { talks, sorted }
})
