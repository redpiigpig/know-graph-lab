import type { ZoroCanon } from './types'

// 銘文附錄 — 阿契美尼德古波斯語與薩珊中古波斯語王室銘文
//
// 🚨 這一藏 scriptural = false，版面上必須與前三藏區分開。
//
// 阿契美尼德王室銘文是不是祆教文獻，學界至今沒有共識，而且爭得很兇：
//   支持者說——大流士只拜阿胡拉‧馬茲達、講「真理對謊言」、行王權神授，
//     這一整套語彙在阿維斯陀裡一一對得上。
//   反對者說——銘文裡從頭到尾沒有出現查拉圖斯特拉、沒有伽薩的專門術語、
//     沒有不朽聖者、沒有寂靜之塔（大流士是土葬的），
//     而希羅多德所記的波斯祭儀與阿維斯陀規定也對不上。
//
// 本站的處理：**收，但不算經，並把爭議寫在版面上。**
// 收的理由只有一個而且很強——這是這個信仰世界最早的、有確切年代與作者的
// 文字證據（前 520 年代），比任何一份阿維斯陀寫本早了兩千年。
// 阿維斯陀的年代全靠語言學推定，而貝希斯敦銘文刻在山壁上、署了名、寫了日期。

const OP = '古波斯語（楔形文字）'

export const EPIGRAPHY_CANON: ZoroCanon = {
  key: 'epigraphy',
  name: '王室銘文',
  name_en: 'Royal Inscriptions',
  glyph: '銘',
  subtitle: '附錄 — 阿契美尼德與薩珊王室石刻（非經典）',
  scriptural: false,
  language: '古波斯語、中古波斯語、帕提亞語（多語並刻）',
  era: '約前 520 – 公元 4 世紀',
  summary:
    '波斯兩大王朝刻在岩壁與石柱上的王室文告。**本附錄不是經典**：阿契美尼德銘文是否屬於祆教，學界至今無定論——它們敬拜阿胡拉‧馬茲達、以「真理對謊言」構築世界觀，卻從未提及查拉圖斯特拉，也不見伽薩的專門術語。收錄的唯一理由是年代：這是這個信仰世界最早的、有確切紀年與具名作者的文字證據，比現存最早的阿維斯陀寫本早了約兩千年。閱讀時務必記住，這些是國王的政治文告，不是祭司的禮儀文本。',
  parts: [
    {
      key: 'p-achaemenid', label: '阿契美尼德部', label_en: 'Achaemenid',
      desc: '前 6–4 世紀，古波斯語楔形文字，多與埃蘭語、阿卡德語並刻。',
      volumes: ['achaemenid'],
    },
    {
      key: 'p-sasanian', label: '薩珊部', label_en: 'Sasanian',
      desc: '公元 3–4 世紀，中古波斯語，多與帕提亞語、希臘語並刻。祭司卡爾提爾的四處銘文另見巴列維文獻‧史傳部。',
      volumes: ['sasanian'],
    },
  ],
  volumes: [
    {
      key: 'achaemenid', sigil: '契', name: '阿契美尼德銘文', name_en: 'Achaemenid Inscriptions',
      era: '約前 520 – 前 338 年', extent: '約 10 種主要銘文',
      summary:
        '大流士一世以降諸王的石刻文告。宗教史上的價值集中在幾個反覆出現的要素：獨尊阿胡拉‧馬茲達為「創造此地、創造彼天、創造人、創造人之福樂」的大神；以「真理」（arta）與「謊言」（drauga）構成世界秩序的對立；王權出於神的授予。這些要素與阿維斯陀高度呼應，卻又缺了阿維斯陀最核心的幾樣東西——這個「像又不像」正是整個爭議的所在。',
      divisions: [
        {
          key: 'ac-all', label: '主要銘文', label_en: 'Principal Inscriptions',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: [
            { slug: 'op-dna', title_zh: '大流士‧納克什伊魯斯塔姆銘文（甲）', title_orig: 'DNa', siglum: 'DNa', language: OP, era: '約前 490 年', status: 'inscription', note: '「一位大神是阿胡拉‧馬茲達，他創造此地、創造彼天、創造人、創造人之福樂。」祆教創世語彙最早的碑刻形式。' },
            { slug: 'op-dnb', title_zh: '大流士‧納克什伊魯斯塔姆銘文（乙）', title_orig: 'DNb', siglum: 'DNb', language: OP, era: '約前 490 年', status: 'inscription', note: '大流士自述德行與治身之道：不縱怒、不偏聽、賞罰依功過。祆教倫理與波斯王德觀最重要的交會點。' },
            { slug: 'op-bisotun', title_zh: '貝希斯敦銘文', title_orig: 'DB (Bīsotūn)', siglum: 'DB', language: `${OP}／埃蘭語／阿卡德語`, era: '約前 520 年', status: 'inscription', extent: '5 欄 76 節', note: '大流士平定諸叛的長篇自述，全篇以「謊言」為叛亂的根源、以阿胡拉‧馬茲達的助佑為勝利之由。楔形文字的解讀即由此碑破譯，其地位相當於兩河文明的羅塞塔石。', intro: '刻於今伊朗克爾曼沙赫省貝希斯敦山崖高處的三語巨碑，大流士一世於前 520 年前後所立。內容敘其如何在一年之內平定九王之叛、重建帝國，全篇的解釋框架是宗教性的：叛者皆因「謊言」（drauga）而起，大流士因守「真理」而蒙阿胡拉‧馬茲達助佑得勝。文末大流士反覆告誡後人「勿信謊言」。十九世紀羅林森據此碑破譯楔形文字，是亞述學的起點。**碑文完全沒有提到查拉圖斯特拉，這是阿契美尼德祆教爭議的核心事實之一。**' },
            { slug: 'op-dpd', title_zh: '大流士‧波斯波利斯銘文', title_orig: 'DPd', siglum: 'DPd', language: OP, era: '前 5 世紀初', status: 'inscription', note: '求阿胡拉‧馬茲達護此邦免於敵軍、荒年與謊言。' },
            { slug: 'op-dse', title_zh: '大流士‧書珊銘文', title_orig: 'DSe / DSf', siglum: 'DSe', language: OP, era: '前 5 世紀初', status: 'inscription', note: '書珊王宮營建誌，逐項記各地貢材與工匠來源。' },
            { slug: 'op-xph', title_zh: '薛西斯「迭瓦銘文」', title_orig: 'XPh (Daiva Inscription)', siglum: 'XPh', language: OP, era: '約前 480 年', status: 'inscription', note: '薛西斯自述搗毀「迭瓦之所」、禁其祭祀，改以正法敬拜阿胡拉‧馬茲達。**祆教史上最受爭議的一段碑文**——它像極了阿維斯陀的「棄絕迭瓦」，卻也可能只是鎮壓叛亂地方神廟的政治宣告。' },
            { slug: 'op-a2sa', title_zh: '亞達薛西二世銘文', title_orig: 'A²Sa / A²Ha', siglum: 'A²Sa', language: OP, era: '前 4 世紀初', status: 'inscription', note: '首次在王室銘文中與阿胡拉‧馬茲達並列呼求阿娜希塔與密特拉；阿契美尼德晚期宗教變化的關鍵證據。' },
            { slug: 'op-cma', title_zh: '帕薩爾加德銘文', title_orig: 'CMa', siglum: 'CMa', language: OP, era: '前 6 世紀末（歸屬有爭議）', status: 'inscription', note: '傳為居魯士所立，但多數學者認為是大流士追刻。' },
          ],
        },
      ],
    },
    {
      key: 'sasanian', sigil: '薩', name: '薩珊王室銘文', name_en: 'Sasanian Royal Inscriptions',
      era: '公元 3–4 世紀', extent: '約 5 種',
      summary:
        '薩珊諸王的多語石刻。與阿契美尼德不同，薩珊王室的祆教身分沒有爭議——他們自稱「馬茲達崇拜者」，設國教、立祭司長、建火廟。這一卷篇幅雖小，卻提供了祆教成為國教之後的官方語彙，也是同時期基督宗教、摩尼教處境的一手旁證。',
      divisions: [
        {
          key: 'sa-all', label: '王室銘文', label_en: 'Royal Inscriptions',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: [
            { slug: 'mp-skz', title_zh: '沙普爾一世‧瑣羅亞斯德立方體銘文', title_orig: 'ŠKZ (Res Gestae Divi Saporis)', siglum: 'ŠKZ', language: '中古波斯語／帕提亞語／希臘語', era: '約公元 262 年', status: 'inscription', note: '沙普爾一世自述三敗羅馬、俘瓦勒良皇帝，並詳列其所建火廟與供養。薩珊史料的第一文獻。' },
            { slug: 'mp-nrb', title_zh: '阿爾達希爾一世‧納克什伊魯斯塔姆銘文', title_orig: 'ANRm', siglum: 'ANRm', language: '中古波斯語／帕提亞語／希臘語', era: '3 世紀前期', status: 'inscription', note: '王權受自阿胡拉‧馬茲達的圖文並陳——浮雕上馬茲達親手將王權環授予國王。' },
            { slug: 'mp-paikuli', title_zh: '派庫利銘文', title_orig: 'NPi (Paikuli)', siglum: 'NPi', language: '中古波斯語／帕提亞語', era: '約公元 293 年', status: 'inscription', note: '納爾塞奪位的自辯長文，殘損嚴重，近年綴合有進展。' },
            { slug: 'mp-shapur-sar-mashhad', title_zh: '沙普爾‧哈吉阿巴德銘文', title_orig: 'ŠH', siglum: 'ŠH', language: '中古波斯語／帕提亞語', era: '3 世紀', status: 'inscription' },
            { slug: 'mp-mihr-narseh', title_zh: '米赫爾‧納爾塞橋銘', title_orig: 'MNFd', siglum: 'MNFd', language: '中古波斯語', era: '5 世紀', status: 'inscription', note: '宰相造橋題記，末句求造橋之功歸於己魂——祆教善功觀的日常表現。' },
          ],
        },
      ],
    },
  ],
}
