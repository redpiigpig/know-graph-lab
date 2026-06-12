/**
 * 東方聖書（The Sacred Books of the East）store
 *
 * 馬克斯‧穆勒主編、牛津 Clarendon Press 1879–1910 出版的 50 卷東方經典英譯集。
 * 性質為「譯本集」而非穆勒著作，故獨立於 /collected-works 之外自成 corpus／portal。
 *
 * - portal：/sacred-books-east（簡介＋按宗教傳統分組的 50 卷目錄）
 * - 單卷未來轉錄後沿用 /ebook/[id] reader（volume.ebookId 連過去）
 *
 * 編輯方式：直接改本檔（沿用 stores/collectedWorks.ts、stores/speech.ts 的 repo-committed 模式）。
 * 卷目為穆勒原版 50 卷的權威編號；繁中卷名為本站擬定，譯者中英並列。
 * 全部公有領域（最末卷 1910，life+70 早過期），archive.org 有乾淨全文，待逐卷轉錄。
 */
import { defineStore } from 'pinia'

export type SbeStatus =
  | 'done' // 已轉錄上架，可進 reader
  | 'in-progress' // 轉錄中
  | 'planned' // 已排入、尚未轉錄

/** 宗教傳統分組（portal 的主要瀏覽軸） */
export interface SbeTradition {
  key: string
  label: string // 繁中傳統名
  labelEn: string
  blurb: string // 一句話介紹
  color: string // tailwind 色（safelist 見 tailwind.config.ts）
  emoji: string
}

export interface SbeVolume {
  vol: number // 穆勒原版卷號 1–50
  titleZh: string // 繁中卷名（本站擬定）
  titleEn: string // 原書名
  translatorZh: string // 譯者繁中
  translatorEn: string // 譯者原名
  year: number
  tradition: string // SbeTradition.key
  status: SbeStatus
  ebookId?: string // 轉錄後連 /ebook/[id]
  archiveId?: string // archive.org item（轉錄來源，逐卷補）
  note?: string
}

export const useSacredBooksEastStore = defineStore('sacredBooksEast', () => {
  const meta = {
    title: '東方聖書',
    titleEn: 'The Sacred Books of the East',
    editor: '弗里德里希‧馬克斯‧穆勒（主編）',
    editorEn: 'Friedrich Max Müller (ed.)',
    span: '1879–1910',
    publisher: '牛津 Clarendon Press',
    intro: [
      '《東方聖書》是馬克斯‧穆勒主編、牛津 Clarendon Press 於 1879 至 1910 年陸續出版的 50 卷東方宗教經典英譯叢書，是十九世紀比較宗教學最具規模的奠基工程。',
      '穆勒邀集當時最頂尖的東方學者，把印度教、佛教、耆那教、祆教（瑣羅亞斯德教）、儒家、道家與伊斯蘭的核心經典首次系統性地譯為英文，讓「以原典比較研究宗教」成為可能——這正是他「只知其一，便一無所知」治學精神的具體實踐。',
      '全套含 49 卷經文與 1 卷總索引；末卷 1910 年出版，全部早已進入公有領域。本站將逐卷收入原文／繁中逐段對照閱讀。',
    ],
  }

  const traditions = ref<SbeTradition[]>([
    { key: 'veda', label: '印度教（吠陀傳統）', labelEn: 'Hinduism / Vedic', emoji: '🕉️', color: 'amber',
      blurb: '吠陀讚歌、奧義書、法經、法論、家庭經、梵書與吠檀多——印度正統婆羅門傳統的核心經典。' },
    { key: 'buddhism', label: '佛教', labelEn: 'Buddhism', emoji: '☸️', color: 'orange',
      blurb: '律藏、法句經、經集、妙法蓮華經、彌蘭陀王問經與大乘經典，巴利與梵漢並收。' },
    { key: 'jainism', label: '耆那教', labelEn: 'Jainism', emoji: '🤲', color: 'cyan',
      blurb: '雅各比英譯的耆那教根本經典兩卷。' },
    { key: 'zoroastrian', label: '祆教（瑣羅亞斯德教）', labelEn: 'Zoroastrianism', emoji: '🔥', color: 'rose',
      blurb: '阿維斯陀（Zend-Avesta）與巴列維文獻——古波斯祆教的聖典與註疏。' },
    { key: 'china', label: '中國（儒家‧道家）', labelEn: 'Chinese Religions', emoji: '☯️', color: 'emerald',
      blurb: '理雅各英譯的儒家經籍（書‧詩‧易‧禮‧孝）與道家經典（道德經‧莊子）。' },
    { key: 'islam', label: '伊斯蘭', labelEn: 'Islam', emoji: '☪️', color: 'teal',
      blurb: '帕爾默英譯的《古蘭經》全文兩卷。' },
    { key: 'index', label: '總索引', labelEn: 'General Index', emoji: '📑', color: 'stone',
      blurb: '溫特尼茨編纂的全套 49 卷總索引。' },
  ])

  // 穆勒原版 50 卷權威編號（Oxford Clarendon, 1879–1910）。
  // 繁中卷名本站擬定；archiveId/ebookId 逐卷轉錄時補。
  const volumes = ref<SbeVolume[]>([
    { vol: 1, titleZh: '奧義書（上）', titleEn: 'The Upanishads, Part I', translatorZh: '穆勒', translatorEn: 'F. Max Müller', year: 1879, tradition: 'veda', status: 'in-progress', ebookId: '55555501-5555-4555-8555-555555555555', archiveId: 'upanishads01mluoft', note: '英文已上架；繁中逐段翻譯進行中。內含旃多格耶、由誰、愛多列雅、憍尸多基、自在等奧義書＋導論。' },
    { vol: 2, titleZh: '雅利安聖法（上）', titleEn: 'The Sacred Laws of the Âryas, Part I', translatorZh: '比勒', translatorEn: 'Georg Bühler', year: 1879, tradition: 'veda', status: 'planned' },
    { vol: 3, titleZh: '儒家經籍（一）：書經‧詩經宗教篇‧孝經', titleEn: 'The Texts of Confucianism, Part I', translatorZh: '理雅各', translatorEn: 'James Legge', year: 1879, tradition: 'china', status: 'planned' },
    { vol: 4, titleZh: '阿維斯陀（一）：祓魔法典', titleEn: 'The Zend-Avesta, Part I (Vendîdâd)', translatorZh: '達梅斯特', translatorEn: 'James Darmesteter', year: 1880, tradition: 'zoroastrian', status: 'in-progress', ebookId: '55555504-5555-4555-8555-555555555555', archiveId: 'zendavesta00darmgoog', note: '英文已上架；繁中翻譯進行中。' },
    { vol: 5, titleZh: '巴列維文獻（一）', titleEn: 'Pahlavi Texts, Part I', translatorZh: '韋斯特', translatorEn: 'E. W. West', year: 1880, tradition: 'zoroastrian', status: 'planned' },
    { vol: 6, titleZh: '古蘭經（上）', titleEn: "The Qur'ân, Part I", translatorZh: '帕爾默', translatorEn: 'E. H. Palmer', year: 1880, tradition: 'islam', status: 'in-progress', ebookId: '55555506-5555-4555-8555-555555555555', archiveId: 'mlbd.koransacredbooks0000unse_w1m9', note: '英文已上架（第 1–16 章）；繁中翻譯進行中。' },
    { vol: 7, titleZh: '毗濕奴法典', titleEn: 'The Institutes of Vishnu', translatorZh: '約利', translatorEn: 'Julius Jolly', year: 1880, tradition: 'veda', status: 'planned' },
    { vol: 8, titleZh: '薄伽梵歌（附桑那蘇伽提亞、續歌）', titleEn: 'The Bhagavadgîtâ, with the Sanatsugâtîya and the Anugîtâ', translatorZh: '特朗', translatorEn: 'Kâshinâth T. Telang', year: 1882, tradition: 'veda', status: 'planned' },
    { vol: 9, titleZh: '古蘭經（下）', titleEn: "The Qur'ân, Part II", translatorZh: '帕爾默', translatorEn: 'E. H. Palmer', year: 1880, tradition: 'islam', status: 'planned' },
    { vol: 10, titleZh: '法句經／經集', titleEn: 'The Dhammapada / The Sutta-Nipâta', translatorZh: '穆勒／法斯伯爾', translatorEn: 'F. Max Müller / V. Fausböll', year: 1881, tradition: 'buddhism', status: 'in-progress', ebookId: '55555510-5555-4555-8555-555555555555', archiveId: 'mlbd.dhammapadasuttni0000fmax', note: '英文已上架；繁中翻譯進行中。' },
    { vol: 11, titleZh: '佛教經文選', titleEn: 'Buddhist Suttas', translatorZh: '里斯‧戴維斯', translatorEn: 'T. W. Rhys Davids', year: 1881, tradition: 'buddhism', status: 'planned' },
    { vol: 12, titleZh: '百道梵書（一）', titleEn: 'The Satapatha-Brâhmana, Part I', translatorZh: '艾格林', translatorEn: 'Julius Eggeling', year: 1882, tradition: 'veda', status: 'planned' },
    { vol: 13, titleZh: '律藏（一）', titleEn: 'Vinaya Texts, Part I', translatorZh: '里斯‧戴維斯、奧登伯格', translatorEn: 'Rhys Davids & Oldenberg', year: 1881, tradition: 'buddhism', status: 'planned' },
    { vol: 14, titleZh: '雅利安聖法（下）', titleEn: 'The Sacred Laws of the Âryas, Part II', translatorZh: '比勒', translatorEn: 'Georg Bühler', year: 1882, tradition: 'veda', status: 'planned' },
    { vol: 15, titleZh: '奧義書（下）', titleEn: 'The Upanishads, Part II', translatorZh: '穆勒', translatorEn: 'F. Max Müller', year: 1884, tradition: 'veda', status: 'planned' },
    { vol: 16, titleZh: '儒家經籍（二）：易經', titleEn: 'The Texts of Confucianism, Part II (Yî King)', translatorZh: '理雅各', translatorEn: 'James Legge', year: 1882, tradition: 'china', status: 'in-progress', ebookId: '55555516-5555-4555-8555-555555555555', archiveId: 'sacredbooksofchi16conf', note: '英文已上架；繁中翻譯進行中。' },
    { vol: 17, titleZh: '律藏（二）', titleEn: 'Vinaya Texts, Part II', translatorZh: '里斯‧戴維斯、奧登伯格', translatorEn: 'Rhys Davids & Oldenberg', year: 1882, tradition: 'buddhism', status: 'planned' },
    { vol: 18, titleZh: '巴列維文獻（二）', titleEn: 'Pahlavi Texts, Part II', translatorZh: '韋斯特', translatorEn: 'E. W. West', year: 1882, tradition: 'zoroastrian', status: 'planned' },
    { vol: 19, titleZh: '佛所行讚', titleEn: 'The Fo-sho-hing-tsan-king (Buddhacarita)', translatorZh: '畢爾', translatorEn: 'Samuel Beal', year: 1883, tradition: 'buddhism', status: 'planned' },
    { vol: 20, titleZh: '律藏（三）', titleEn: 'Vinaya Texts, Part III', translatorZh: '里斯‧戴維斯、奧登伯格', translatorEn: 'Rhys Davids & Oldenberg', year: 1885, tradition: 'buddhism', status: 'planned' },
    { vol: 21, titleZh: '妙法蓮華經', titleEn: 'The Saddharma-pundarîka (Lotus of the True Law)', translatorZh: '克恩', translatorEn: 'H. Kern', year: 1884, tradition: 'buddhism', status: 'planned' },
    { vol: 22, titleZh: '耆那教經典（一）', titleEn: 'Jaina Sûtras, Part I', translatorZh: '雅各比', translatorEn: 'Hermann Jacobi', year: 1884, tradition: 'jainism', status: 'in-progress', ebookId: '55555522-5555-4555-8555-555555555555', archiveId: 'mlbd.jainasutraspt1tr00vol-22.unse_m8x0', note: '英文已上架（阿恰蘭迦＋劫波經）；繁中翻譯進行中。' },
    { vol: 23, titleZh: '阿維斯陀（二）', titleEn: 'The Zend-Avesta, Part II', translatorZh: '達梅斯特', translatorEn: 'James Darmesteter', year: 1883, tradition: 'zoroastrian', status: 'planned' },
    { vol: 24, titleZh: '巴列維文獻（三）', titleEn: 'Pahlavi Texts, Part III', translatorZh: '韋斯特', translatorEn: 'E. W. West', year: 1885, tradition: 'zoroastrian', status: 'planned' },
    { vol: 25, titleZh: '摩奴法論', titleEn: 'The Laws of Manu', translatorZh: '比勒', translatorEn: 'Georg Bühler', year: 1886, tradition: 'veda', status: 'planned' },
    { vol: 26, titleZh: '百道梵書（二）', titleEn: 'The Satapatha-Brâhmana, Part II', translatorZh: '艾格林', translatorEn: 'Julius Eggeling', year: 1885, tradition: 'veda', status: 'planned' },
    { vol: 27, titleZh: '儒家經籍（三）：禮記（上）', titleEn: 'The Texts of Confucianism, Part III (Lî Kî I)', translatorZh: '理雅各', translatorEn: 'James Legge', year: 1885, tradition: 'china', status: 'planned' },
    { vol: 28, titleZh: '儒家經籍（四）：禮記（下）', titleEn: 'The Texts of Confucianism, Part IV (Lî Kî II)', translatorZh: '理雅各', translatorEn: 'James Legge', year: 1885, tradition: 'china', status: 'planned' },
    { vol: 29, titleZh: '家庭經（一）', titleEn: 'The Grihya-Sûtras, Part I', translatorZh: '奧登伯格', translatorEn: 'Hermann Oldenberg', year: 1886, tradition: 'veda', status: 'planned' },
    { vol: 30, titleZh: '家庭經（二）', titleEn: 'The Grihya-Sûtras, Part II', translatorZh: '奧登伯格、穆勒', translatorEn: 'Oldenberg & Müller', year: 1892, tradition: 'veda', status: 'planned' },
    { vol: 31, titleZh: '阿維斯陀（三）：耶斯那等', titleEn: 'The Zend-Avesta, Part III (Yasna, Visparad, etc.)', translatorZh: '米爾斯', translatorEn: 'L. H. Mills', year: 1887, tradition: 'zoroastrian', status: 'planned' },
    { vol: 32, titleZh: '吠陀讚歌（一）', titleEn: 'Vedic Hymns, Part I', translatorZh: '穆勒', translatorEn: 'F. Max Müller', year: 1891, tradition: 'veda', status: 'planned' },
    { vol: 33, titleZh: '小法典（一）：那羅陀‧祭主仙', titleEn: 'The Minor Law-Books, Part I', translatorZh: '約利', translatorEn: 'Julius Jolly', year: 1889, tradition: 'veda', status: 'planned' },
    { vol: 34, titleZh: '吠檀多經（一）：商羯羅註', titleEn: 'The Vedânta-Sûtras, Part I (Sankarâkârya)', translatorZh: '蒂博', translatorEn: 'George Thibaut', year: 1890, tradition: 'veda', status: 'planned' },
    { vol: 35, titleZh: '彌蘭陀王問經（上）', titleEn: 'The Questions of King Milinda, Part I', translatorZh: '里斯‧戴維斯', translatorEn: 'T. W. Rhys Davids', year: 1890, tradition: 'buddhism', status: 'planned' },
    { vol: 36, titleZh: '彌蘭陀王問經（下）', titleEn: 'The Questions of King Milinda, Part II', translatorZh: '里斯‧戴維斯', translatorEn: 'T. W. Rhys Davids', year: 1894, tradition: 'buddhism', status: 'planned' },
    { vol: 37, titleZh: '巴列維文獻（四）', titleEn: 'Pahlavi Texts, Part IV', translatorZh: '韋斯特', translatorEn: 'E. W. West', year: 1892, tradition: 'zoroastrian', status: 'planned' },
    { vol: 38, titleZh: '吠檀多經（二）', titleEn: 'The Vedânta-Sûtras, Part II', translatorZh: '蒂博', translatorEn: 'George Thibaut', year: 1896, tradition: 'veda', status: 'planned' },
    { vol: 39, titleZh: '道家經籍（一）：道德經‧莊子（上）', titleEn: 'The Texts of Tâoism, Part I', translatorZh: '理雅各', translatorEn: 'James Legge', year: 1891, tradition: 'china', status: 'planned' },
    { vol: 40, titleZh: '道家經籍（二）：莊子（下）等', titleEn: 'The Texts of Tâoism, Part II', translatorZh: '理雅各', translatorEn: 'James Legge', year: 1891, tradition: 'china', status: 'planned' },
    { vol: 41, titleZh: '百道梵書（三）', titleEn: 'The Satapatha-Brâhmana, Part III', translatorZh: '艾格林', translatorEn: 'Julius Eggeling', year: 1894, tradition: 'veda', status: 'planned' },
    { vol: 42, titleZh: '阿闥婆吠陀讚歌', titleEn: 'Hymns of the Atharva-Veda', translatorZh: '布盧姆菲爾德', translatorEn: 'Maurice Bloomfield', year: 1897, tradition: 'veda', status: 'planned' },
    { vol: 43, titleZh: '百道梵書（四）', titleEn: 'The Satapatha-Brâhmana, Part IV', translatorZh: '艾格林', translatorEn: 'Julius Eggeling', year: 1897, tradition: 'veda', status: 'planned' },
    { vol: 44, titleZh: '百道梵書（五）', titleEn: 'The Satapatha-Brâhmana, Part V', translatorZh: '艾格林', translatorEn: 'Julius Eggeling', year: 1900, tradition: 'veda', status: 'planned' },
    { vol: 45, titleZh: '耆那教經典（二）', titleEn: 'Jaina Sûtras, Part II', translatorZh: '雅各比', translatorEn: 'Hermann Jacobi', year: 1895, tradition: 'jainism', status: 'planned' },
    { vol: 46, titleZh: '吠陀讚歌（二）', titleEn: 'Vedic Hymns, Part II', translatorZh: '奧登伯格', translatorEn: 'Hermann Oldenberg', year: 1897, tradition: 'veda', status: 'planned' },
    { vol: 47, titleZh: '巴列維文獻（五）', titleEn: 'Pahlavi Texts, Part V', translatorZh: '韋斯特', translatorEn: 'E. W. West', year: 1897, tradition: 'zoroastrian', status: 'planned' },
    { vol: 48, titleZh: '吠檀多經（三）：羅摩奴闍註', titleEn: 'The Vedânta-Sûtras, Part III (Râmânuja)', translatorZh: '蒂博', translatorEn: 'George Thibaut', year: 1904, tradition: 'veda', status: 'planned' },
    { vol: 49, titleZh: '大乘佛教經典', titleEn: 'Buddhist Mahâyâna Texts', translatorZh: '考埃爾、穆勒、高楠順次郎', translatorEn: 'Cowell, Müller & Takakusu', year: 1894, tradition: 'buddhism', status: 'planned' },
    { vol: 50, titleZh: '總索引', titleEn: 'General Index', translatorZh: '溫特尼茨', translatorEn: 'M. Winternitz', year: 1910, tradition: 'index', status: 'planned' },
  ])

  const traditionByKey = (key: string) => traditions.value.find((t) => t.key === key)

  /** 按傳統分組（依 traditions 順序，組內依卷號） */
  const groups = computed(() =>
    traditions.value.map((t) => ({
      tradition: t,
      volumes: volumes.value.filter((v) => v.tradition === t.key).sort((a, b) => a.vol - b.vol),
    })).filter((g) => g.volumes.length > 0)
  )

  const progress = computed(() => ({
    done: volumes.value.filter((v) => v.status === 'done').length,
    total: volumes.value.length,
  }))

  return { meta, traditions, volumes, traditionByKey, groups, progress }
})
