/**
 * 碩士論文口述訪談紀錄 store
 *
 * 兩個資料源：
 *   1) 已發佈到 /thesis?tab=interviews 的訪談紀錄（published）
 *   2) G:\我的雲端硬碟\公事\國北教\碩士論文\口述訪談\ 各日期資料夾，
 *      但 Drive 上「沒有正式 *口述訪談紀錄.docx*」的人，
 *      只剩錄音或逐字稿草稿。
 */
import { defineStore } from 'pinia'

export type InterviewCategory = '法師' | '學者' | '宗教對話' | '社運界' | '其他'

/** 已正式整理、可在網站閱讀的訪談 */
export interface PublishedInterview {
  id: string
  name: string
  role: string
  date: string // YYYY.MM.DD
  category: InterviewCategory
  filename: string // 對應 /content/interviews/${filename}.txt
}

/** Drive 上沒有正式紀錄 docx 的人（訪問已完成或進行中） */
export type DriveAsset = 'outline' | 'audio' | 'draft-txt' | 'photo'

export interface PendingInterview {
  id: string
  name: string
  role: string
  date: string // YYYY.MM.DD（Drive 資料夾日期；以實際訪談日為準）
  category: InterviewCategory
  driveFolder: string // 相對於 G:\...\口述訪談\
  has: DriveAsset[] // 目前 Drive 上有什麼資產
  note?: string
}

export const useThesisInterviewsStore = defineStore('thesisInterviews', () => {
  // ── 已發佈訪談 ─────────────────────────────────────────
  const published = ref<PublishedInterview[]>([
    { id: 'chaohwei-1', name: '釋昭慧法師（上）', role: '玄奘大學宗教學系教授、佛教弘誓學院住持', date: '2023.04.06', category: '法師', filename: '04.06 釋昭慧法師口述訪談紀錄' },
    { id: 'chaohwei-2', name: '釋昭慧法師（下）', role: '玄奘大學宗教學系教授、佛教弘誓學院住持', date: '2023.05.18', category: '法師', filename: '05.18 釋昭慧法師口述訪談紀錄(下)' },
    { id: 'shingkuang', name: '釋性廣法師', role: '玄奘大學宗教學系教授、弘誓學院指導法師', date: '2024.04.17', category: '法師', filename: '04.17 釋性廣法師口述訪談紀錄' },
    { id: 'hongyin', name: '釋宏印法師', role: '印順學研究者、佛教推廣人士', date: '2024.04.18', category: '法師', filename: '04.18 釋宏印法師口述訪談紀錄' },
    { id: 'mingyi', name: '釋明一法師', role: '佛教弘誓學院前住持', date: '2023.12.05', category: '法師', filename: '12.05 釋明一法師口述訪談紀錄' },
    { id: 'changci', name: '釋長慈法師', role: '佛教弘誓學院', date: '2024.08.20', category: '法師', filename: '08.20 釋長慈法師口述訪談紀錄' },
    { id: 'qingde', name: '釋清德法師', role: '佛教弘誓學院', date: '2023.09.13', category: '法師', filename: '09.13 釋清德法師口述訪談紀錄' },
    { id: 'yuanmao', name: '釋圓貌法師', role: '佛教弘誓學院院長', date: '2024.01.16', category: '法師', filename: '01.16 釋圓貌法師口述訪談紀錄' },
    { id: 'xinyu', name: '釋心宇法師', role: '佛教弘誓學院', date: '2024.01.16', category: '法師', filename: '01.16 釋心宇法師口述訪談紀錄' },
    { id: 'yinyue', name: '釋印悅法師', role: '《弘誓》雙月刊總編輯、學務主任', date: '2024.01.16', category: '法師', filename: '01.16 釋印悅法師口述訪談紀錄' },
    { id: 'xinhao', name: '釋心皓法師', role: '弘誓僧團住持、弘誓文教基金會財務主任', date: '2024.01.17', category: '法師', filename: '01.17 釋心皓法師口述訪談紀錄' },
    { id: 'jianan', name: '釋見岸法師', role: '佛教弘誓學院法師', date: '2024.05.11', category: '法師', filename: '05.11 釋見岸法師口述訪談紀錄' },
    { id: 'changlei', name: '釋長叡法師', role: '台北市中山區慧日講堂住持', date: '2024.06.17', category: '法師', filename: '06.17 釋長叡法師口述訪談紀錄' },
    { id: 'xinqian', name: '釋心謙法師', role: '佛教弘誓學院法師', date: '2025.03.01', category: '法師', filename: '03.01 釋心謙法師口述訪談紀錄' },
    { id: 'xinxuan', name: '釋心玄法師', role: '玄奘大學宗教與文化學系', date: '2025.03.15', category: '法師', filename: '03.15 釋心玄法師口述訪談紀錄' },
    { id: 'houkh', name: '侯坤宏教授', role: '國史館研究員、指導教授', date: '2022.12.22', category: '學者', filename: '12.22 侯坤宏教授口述訪談紀錄' },
    { id: 'qiumj', name: '邱敏捷教授', role: '臺南大學國語文學系教授，印順學研究者', date: '2023.04.10', category: '學者', filename: '04.10 邱敏捷教授口述訪談紀錄' },
    { id: 'huangyh', name: '黃運喜教授', role: '玄奘大學宗教與文化學系教授', date: '2023.04.21', category: '學者', filename: '04.21 黃運喜教授口述訪談紀錄' },
    { id: 'yanghn', name: '楊惠南教授', role: '台灣大學哲學系退休教授', date: '2023.05.08', category: '學者', filename: '05.08 楊惠南教授口述訪談紀錄' },
    { id: 'kanzc', name: '闞正宗教授', role: '佛教史學者', date: '2023.06.05', category: '學者', filename: '06.05 闞正宗教授口述訪談紀錄' },
    { id: 'linjd', name: '林建德教授', role: '慈濟大學宗教與人文研究所教授', date: '2023.08.27', category: '學者', filename: '08.27 林建德教授口述訪談紀錄' },
    { id: 'wenjk', name: '溫金柯居士', role: '印順導師思想研究者', date: '2024.04.12', category: '學者', filename: '20250408修定 溫金柯居士口述訪談紀錄' },
    { id: 'herbs', name: '何日生教授', role: '慈濟基金會副執行長、玄奘大學兼任教授', date: '2024.01.23', category: '學者', filename: '01.23 何日生教授口述訪談紀錄' },
    { id: 'hongsc', name: '洪山川主教', role: '天主教台北總教區榮休總主教', date: '2024.05.07', category: '宗教對話', filename: '05.07 洪山川主教口述訪談紀錄' },
    { id: 'luji', name: '盧俊義牧師', role: '台灣基督長老教會牧師', date: '2023.12.27', category: '宗教對話', filename: '12.27 盧俊義牧師口述訪談紀錄' },
    { id: 'linda', name: '艾琳達教授', role: '外交官、台灣社運人士', date: '2024.02.02', category: '社運界', filename: '02.02 艾琳達教授口述訪談紀錄' },
    { id: 'yejl', name: '葉菊蘭女士', role: '前行政院院長、台灣政治人物', date: '2024.06.20', category: '社運界', filename: '06.20 葉菊蘭女士口述訪談紀錄0213(最終版)' },
    { id: 'hezx', name: '何宗勳先生', role: '台灣動物保護運動人士', date: '2024.01.16', category: '社運界', filename: '01.16 何宗勳先生口述訪談紀錄' },
    { id: 'huangmy', name: '黃美瑜女士・游雅婷女士', role: '社會運動工作者', date: '2024.05.02', category: '社運界', filename: '05.02 黃美瑜女士游雅婷女士口述訪談紀錄' },
    { id: 'zhangzd', name: '張章得先生', role: '關懷生命協會工作者', date: '2024.05.07', category: '社運界', filename: '05.07 張章得先生口述訪談紀錄' },
    { id: 'zhanxk', name: '詹錫奎先生', role: '動物保護運動人士', date: '2024.05.23', category: '社運界', filename: '05.23 詹錫奎先生口述訪談紀錄' },
    { id: 'zhuzh', name: '朱增宏先生', role: '台灣動物社會研究會創辦人', date: '2024.05.28', category: '社運界', filename: '05.28 朱增宏先生口述訪談紀錄' },
    { id: 'zhanglj', name: '張莉筠居士', role: '佛教弘誓學院護持者', date: '2024.03.26', category: '其他', filename: '03.26 張莉筠居士口述訪談紀錄' },
    { id: 'zhuangsx', name: '莊秀美女士', role: '日本龍谷大學教授', date: '2024.04.08', category: '其他', filename: '04.08 莊秀美女士口述訪談紀錄' },
    { id: 'wangch', name: '王彩虹居士', role: '弘誓學團常住居士、前法界出版社秘書', date: '2024.01.17', category: '其他', filename: '01.17 王彩虹居士口述訪談紀錄' },
    { id: 'chenyxl', name: '陳悅萱老師', role: '佛教音樂工作者', date: '2024.02.14', category: '其他', filename: '02.14 陳悅萱老師口述訪談紀錄' },
    { id: 'linrz', name: '林蓉芝居士', role: '中華佛寺協會工作者', date: '2024.09.03', category: '其他', filename: '09.03 林蓉芝居士口述訪談紀錄' },
  ])

  // ── Drive 上沒有正式紀錄 docx 的訪談 ──────────────────────
  // （網站可能已有手動整理過的逐字稿，但 Drive 上欠缺正式檔）
  const driveMissing = ref<PendingInterview[]>([
    // 只有 m4a.txt 逐字稿草稿（最接近可用狀態）
    { id: 'chenyxl', name: '陳悅萱老師', role: '佛教音樂工作者', date: '2024.02.14', category: '其他',
      driveFolder: '2024.02.14 陳悅萱老師訪談', has: ['outline', 'audio', 'draft-txt', 'photo'] },

    // 只有錄音 m4a，連逐字稿草稿都還沒有
    { id: 'huangmy', name: '黃美瑜、游雅婷女士', role: '社會運動工作者', date: '2024.05.02', category: '社運界',
      driveFolder: '2024.05.02 黃美瑜、游雅婷女士訪談', has: ['outline', 'audio', 'photo'],
      note: '錄音兩段（新錄音 36 / 37）' },
    { id: 'zhangzd', name: '張章得先生', role: '關懷生命協會工作者', date: '2024.05.07', category: '社運界',
      driveFolder: '2024.05.07 張章得先生訪談', has: ['outline', 'audio', 'photo'] },
    { id: 'jianan', name: '釋見岸法師', role: '佛教弘誓學院法師', date: '2024.05.11', category: '法師',
      driveFolder: '2024.05.11 釋見岸法師訪談', has: ['outline', 'audio', 'photo'] },
    { id: 'zhanxk', name: '詹錫奎先生', role: '動物保護運動人士', date: '2024.05.23', category: '社運界',
      driveFolder: '2024.05.23 詹錫奎先生訪談', has: ['outline', 'audio', 'photo'] },
    { id: 'zhuzh', name: '朱增宏先生', role: '台灣動物社會研究會創辦人', date: '2024.05.28', category: '社運界',
      driveFolder: '2024.05.28 朱增宏先生訪談', has: ['outline', 'audio', 'photo'] },
    { id: 'linrz', name: '林蓉芝居士', role: '中華佛寺協會工作者', date: '2024.09.03', category: '其他',
      driveFolder: '2024.09.03 林蓉芝居士訪談', has: ['outline', 'audio', 'photo'] },
    { id: 'kuanqian', name: '釋寬謙法師', role: '財團法人覺風佛教藝術文化基金會董事長', date: '2024.09.19', category: '法師',
      driveFolder: '2024.09.19 釋寬謙法師訪談', has: ['outline', 'audio', 'photo'],
      note: '網站尚未上架' },
    { id: 'xinqian', name: '釋心謙法師', role: '佛教弘誓學院法師', date: '2025.03.01', category: '法師',
      driveFolder: '2025.03.01 釋心謙法師訪談', has: ['outline', 'audio', 'photo'] },
    { id: 'xinxuan', name: '釋心玄法師', role: '玄奘大學宗教與文化學系', date: '2025.03.15', category: '法師',
      driveFolder: '2025.03.15 釋心玄法師訪談', has: ['outline', 'audio', 'photo'],
      note: '另附「慈恩精舍選佛場一一佛教空間整修設計範例研析0312.docx」參考資料' },
  ])

  // ── 派生 ─────────────────────────────────────────────
  const driveMissingByStatus = computed(() => {
    const draft: PendingInterview[] = []
    const audioOnly: PendingInterview[] = []
    const outlineOnly: PendingInterview[] = []
    for (const iv of driveMissing.value) {
      if (iv.has.includes('draft-txt')) draft.push(iv)
      else if (iv.has.includes('audio')) audioOnly.push(iv)
      else outlineOnly.push(iv)
    }
    return { draft, audioOnly, outlineOnly }
  })

  const publishedIds = computed(() => new Set(published.value.map(i => i.id)))

  /** 在網站上已上架，但 Drive 上仍沒有正式 docx 的人 */
  const publishedButDriveMissing = computed(() =>
    driveMissing.value.filter(iv => publishedIds.value.has(iv.id))
  )

  return {
    published,
    driveMissing,
    driveMissingByStatus,
    publishedButDriveMissing,
  }
})
