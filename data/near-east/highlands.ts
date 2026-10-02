// 埃蘭與高地藏 —— 埃蘭、米坦尼、烏拉爾圖
//
// 使用者要求「其他古近東沒有提到的也可以再增加」而新設的一藏。
// 兩河流域東邊與北邊的山地文明：伊朗西南的埃蘭、敘利亞北部的胡里特國家米坦尼、亞美尼亞高原的烏拉爾圖。
// 三者材料都少，各自不足以成藏，但都是自成一套的神廟體系，不能塞進巴比倫或赫梯。
//
// 🚨 胡里特宗教的主體（庫瑪爾比組詩、基茲瓦特納儀式）已在「赫梯與胡里特藏」——本藏只收米坦尼王國
//   自身的國家宗教材料，尤其是條約神表裡那四位印度—雅利安神祇。
//
// 斷限：埃蘭語行政文書止於阿契美尼德時代（約前 4 世紀末）；烏拉爾圖約前 590 年亡。
//   波斯波利斯泥板裡的埃蘭神與阿胡拉‧馬茲達並列受祭，以互見接祆教經典。

import type { NeCanon } from './types'

export const HIGHLANDS_CANON: NeCanon = {
  key: 'highlands',
  name: '埃蘭與高地藏',
  name_en: 'Elam and the Highlands',
  glyph: '高',
  subtitle: '埃蘭、米坦尼、烏拉爾圖——兩河流域東北山地的神',
  scriptural: true,
  language: '埃蘭語（線形埃蘭文與楔形）、阿卡德語、烏拉爾圖語',
  era: '約前 2250 – 前 4 世紀',
  terminus: '埃蘭語的最後宗教記錄是阿契美尼德朝的波斯波利斯泥板（約前 500–460），埃蘭語文書止於前 4 世紀末。',
  columns: { orig: 'available', en: 'copyright', zh: 'none' },
  summary:
    '埃蘭兩千年間是巴比倫的宿敵與鄰居，主神印舒希納克是冥府的審判者，喬加贊比勒的塔廟至今是伊朗保存最好的一座。'
    + '米坦尼王國的條約神表裡出現了密特拉、伐樓那、因陀羅與雙馬童——比梨俱吠陀更早的印度—雅利安神名。'
    + '烏拉爾圖的國神哈爾迪在山壁上的「神門」受祭，碑文列出眾神與每位應得的牛羊數。',
  volumes: [
    {
      key: 'elam',
      sigil: '高一',
      name: '埃蘭',
      name_en: 'Elam',
      era: '約前 2250 – 前 460',
      summary: '從阿卡德時代的條約到波斯帝國的配給泥板：一個常被當成巴比倫「外國」的文明自己的神。',
      divisions: [
        {
          key: 'elamite',
          label: '埃蘭銘文',
          label_en: 'Elamite Inscriptions',
          texts: [
            { slug: 'naram-sin-treaty', title_zh: '納拉姆辛與埃蘭的條約', title_orig: 'Treaty of Narām-Sîn with Elam', era: '約前 2250', language: '古埃蘭語（楔形）', provenance: '蘇薩；羅浮宮藏', status: 'fragment', note: '現存最早的埃蘭語文本，以三十七位神為見證——埃蘭萬神殿的第一份名單。開頭是「眾神聽著」。' },
            { slug: 'puzur-inshushinak', title_zh: '普祖爾—印舒希納克銘文', title_orig: 'Inscriptions of Puzur-Inšušinak (Linear Elamite)', era: '約前 2100', language: '埃蘭語（線形埃蘭文，近年部分解讀）與阿卡德語', provenance: '蘇薩', status: 'inscription', columns: { orig: 'available', en: 'none', zh: 'none' }, note: '向印舒希納克奉獻的雙文字銘文。線形埃蘭文 2020 年代才有解讀方案，學界尚未定論。' },
            { slug: 'choga-zanbil', title_zh: '喬加贊比勒塔廟磚銘', title_orig: 'Choga Zanbil (Dur-Untash) brick inscriptions', era: '約前 1250（溫塔什—納皮瑞沙）', language: '中埃蘭語', provenance: '伊朗胡齊斯坦喬加贊比勒', status: 'inscription', extent: '逾五千塊銘文磚', note: '王為印舒希納克與納皮瑞沙建塔廟與新城。每塊磚都記一次奉獻。' },
            { slug: 'shilhak-inshushinak', title_zh: '席勒哈克—印舒希納克碑', title_orig: 'Stelae of Šilhak-Inšušinak', era: '約前 1140', language: '中埃蘭語', provenance: '蘇薩', status: 'inscription', note: '中埃蘭盛世之王為神廟修建所立的長篇碑銘。同一時期埃蘭人把漢摩拉比法典碑與馬杜克神像從巴比倫掠回蘇薩。', seealso: ['hammurabi', 'marduk-prophecy'] },
          ],
        },
        {
          key: 'achaemenid',
          label: '阿契美尼德時代',
          label_en: 'Achaemenid Period',
          texts: [
            { slug: 'persepolis-fortification', title_zh: '波斯波利斯城防泥板中的祭祀配給', title_orig: 'Persepolis Fortification tablets (offerings, lan-sacrifice)', era: '前 509 – 前 493', language: '晚期埃蘭語', provenance: '波斯波利斯；芝加哥大學東方研究所整理', status: 'fragment', extent: '泥板約一萬五千件，宗教相關數百件', note: '帝國倉庫撥給祭司的酒、穀、羊，受祭者有阿胡拉‧馬茲達、埃蘭神胡姆班、巴比倫神阿達德，以及山川河流——大流士一世時代的宗教實況並非單一。', xref: ['祆教經典‧王室銘文附錄'] },
          ],
        },
      ],
    },
    {
      key: 'mitanni-urartu',
      sigil: '高二',
      name: '米坦尼與烏拉爾圖',
      name_en: 'Mitanni and Urartu',
      era: '約前 1350 – 前 590',
      summary: '胡里特人的米坦尼王國與鐵器時代的烏拉爾圖，後者的語言與胡里特語同族。',
      divisions: [
        {
          key: 'mitanni',
          label: '米坦尼',
          label_en: 'Mitanni',
          texts: [
            { slug: 'shattiwaza-treaty', title_zh: '蘇庇路里烏瑪與沙提瓦扎條約神表', title_orig: 'Treaty between Šuppiluliuma I and Šattiwaza (divine witnesses)', siglum: 'CTH 51–52', era: '約前 1350', language: '阿卡德語', provenance: '哈圖沙（另有米坦尼一方的抄本）', status: 'fragment', note: '米坦尼一方的見證神祇中有 Mitra-ššil、Aruna-ššil（伐樓那）、Indara（因陀羅）、Našatiyanna（雙馬童）——比任何吠陀文獻都早的印度—雅利安神名。', xref: ['祆教經典（密特拉）'] },
          ],
        },
        {
          key: 'urartu',
          label: '烏拉爾圖',
          label_en: 'Urartu',
          texts: [
            { slug: 'meher-kapisi', title_zh: '梅赫爾門神表', title_orig: 'Meher Kapısı inscription', era: '約前 800（伊什普伊尼與梅努阿）', language: '烏拉爾圖語', provenance: '土耳其凡城附近岩壁上的「神門」', status: 'inscription', note: '列出約八十位神祇與各自應得的牛羊數，以哈爾迪居首——烏拉爾圖國家宗教的官方編制表。' },
            { slug: 'kelishin', title_zh: '凱利欣雙語碑', title_orig: 'Kelishin stela', era: '約前 800', language: '烏拉爾圖語—亞述語（阿卡德語）雙語', provenance: '伊朗—伊拉克邊境山口', status: 'inscription', note: '烏拉爾圖王前往穆薩西爾的哈爾迪神廟朝拜獻祭的記錄。' },
            { slug: 'musasir-sack', title_zh: '薩爾貢二世第八次戰役書信（劫掠穆薩西爾）', title_orig: 'Sargon II\'s Letter to Aššur (Eighth Campaign)', siglum: 'AO 5372', era: '前 714', language: '標準巴比倫語', provenance: '亞述城；羅浮宮藏', status: 'whole', note: '寫給亞述爾神的戰報，逐件列出從哈爾迪神廟搬走的神像與寶物——一份由敵人寫下的神廟清單。' },
          ],
        },
      ],
    },
  ],
}
