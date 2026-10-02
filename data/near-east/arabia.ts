// 阿拉伯藏 —— 前伊斯蘭阿拉伯半島的宗教銘文
//
// 使用者要求「其他古近東沒有提到的也可以再增加」而新設的一藏。
// 半島南部的示巴、米奈、卡塔班、哈德拉毛、希木葉爾諸國用南阿拉伯字母立了上萬件銘文；
// 北部則有泰馬、德丹（里赫顏）、納巴泰與沙漠遊牧者的塗鴉。
// 伊斯蘭以前的阿拉伯宗教，今人多半只從伊斯蘭作者（伊本‧卡勒比《偶像書》）的描述認識——
// 那屬附錄。本藏收的是半島居民自己刻下的。
//
// 斷限：約公元 380 年起希木葉爾王室銘文改稱「天之主」「慈悲者」（Raḥmānān），
//   不再向舊神奉獻，南阿拉伯多神銘文漸絕；北部塗鴉延至 4 世紀。

import type { NeCanon } from './types'

const SAB = '示巴語（古南阿拉伯語）'

export const ARABIA_CANON: NeCanon = {
  key: 'arabia',
  name: '阿拉伯藏',
  name_en: 'Ancient Arabian Canon',
  glyph: '阿',
  subtitle: '示巴、希木葉爾、納巴泰與沙漠遊牧者的神',
  scriptural: true,
  language: '古南阿拉伯語（示巴、米奈、卡塔班、哈德拉毛）、古北阿拉伯語諸方言（里赫顏、薩法、希斯馬）、納巴泰亞蘭語',
  era: '約前 8 世紀 – 公元 4 世紀',
  terminus: '約 380 年起希木葉爾王室銘文只稱「天之主」，向舊神的奉獻銘文漸絕。',
  columns: { orig: 'available', en: 'copyright', zh: 'none' },
  summary:
    '示巴女王的國度供奉月神（或日神，學界未定）阿瑪卡，馬里布的大神廟至今仍立著八根石柱。'
    + '南阿拉伯銘文中有一種近東獨有的文類：「懺悔銘文」——人在神廟裡公開承認自己犯了性禁忌或潔淨禁忌、受了神罰，刻石為記。'
    + '北方的納巴泰人奉杜沙拉為主神，以無像的方石為神的居所；沙漠中的遊牧者在岩石上刻下成千上萬句向阿拉特、杜沙拉的短禱。',
  volumes: [
    {
      key: 'south',
      sigil: '阿一',
      name: '南阿拉伯',
      name_en: 'South Arabia',
      era: '約前 8 世紀 – 公元 4 世紀',
      summary: '示巴、米奈、卡塔班、哈德拉毛、希木葉爾。神廟、朝聖、狩獵禮與懺悔。',
      divisions: [
        {
          key: 'saba',
          label: '示巴',
          label_en: 'Saba',
          texts: [
            { slug: 'karibil-watar', title_zh: '卡里布伊勒‧瓦塔大銘文', title_orig: 'Karibʾil Watar inscriptions', siglum: 'RES 3945–3946', era: '約前 7 世紀初', language: SAB, provenance: '西爾瓦赫阿瑪卡神廟', status: 'inscription', note: '示巴統一南阿拉伯的君主記其戰功，開頭記述他為阿塔爾神舉行的獻祭與以「一神、一王、一約」凝聚諸部族的儀式。' },
            { slug: 'awam-temple', title_zh: '阿瓦姆神廟奉獻銘', title_orig: 'Dedications from the Awām temple (Maḥram Bilqīs)', era: '約前 7 世紀 – 公元 4 世紀', language: SAB, provenance: '馬里布阿瑪卡大神廟', status: 'inscription', extent: '數百件', note: '向阿瑪卡獻銅像以謝病癒、生子、豐收、戰勝——南阿拉伯宗教最大的一座銘文庫。' },
            { slug: 'confession-inscriptions', title_zh: '懺悔銘文', title_orig: 'Sabaic and Minaic confession (penitential) inscriptions', era: '約前 1 世紀 – 公元 2 世紀', language: '示巴語、米奈語', provenance: '哈伊德‧阿爾—扎爾等神廟', status: 'inscription', note: '「某某承認並懺悔，因他在不潔時親近女人，又未洗淨即穿衣……神罰了他，他便悔過。」古代近東少見的個人公開認罪文類。', bible: '利 15；利 5:5「他要承認所犯的罪」' },
            { slug: 'qaniya-hymn', title_zh: '卡尼亞讚歌', title_orig: 'Hymn of Qāniya (to Shams / Dhāt Ḥimyam)', era: '約公元 1 世紀', language: SAB, provenance: '葉門卡尼亞', status: 'inscription', note: '已知唯一一首押韻的示巴語讚歌，向太陽女神祈雨。' },
          ],
        },
        {
          key: 'himyar',
          label: '希木葉爾的轉向',
          label_en: 'The Himyarite Turn',
          texts: [
            { slug: 'himyar-rahmanan', title_zh: '希木葉爾「慈悲者」銘文', title_orig: 'Himyarite monotheistic inscriptions (Raḥmānān, "Lord of Heaven")', era: '約公元 380 起', language: SAB, provenance: '札法爾、馬里布等', status: 'inscription', note: '王室銘文不再向阿瑪卡奉獻，改稱「天地之主」與「慈悲者」——南阿拉伯多神信仰在官方層面的終點。此後王室傾向猶太教。', xref: ['猶太教（規劃中）'] },
          ],
        },
      ],
    },
    {
      key: 'north',
      sigil: '阿二',
      name: '北阿拉伯與納巴泰',
      name_en: 'North Arabia and the Nabataeans',
      era: '約前 6 世紀 – 公元 4 世紀',
      summary: '綠洲城邦泰馬與德丹、從佩特拉到希格拉的納巴泰王國，以及敘利亞—約旦沙漠中數萬條遊牧者塗鴉。',
      divisions: [
        {
          key: 'oases',
          label: '綠洲與王國',
          label_en: 'Oases and Kingdoms',
          texts: [
            { slug: 'tayma-stone', title_zh: '泰馬石', title_orig: 'Tayma stone', siglum: 'KAI 228', era: '約前 5 世紀', language: '亞蘭語', provenance: '沙烏地阿拉伯泰馬；羅浮宮藏', status: 'inscription', note: '祭司為「馬赫拉姆的薩勒姆神」設立新祭儀並定祭司世襲俸地。巴比倫末代王那波尼度曾在此地住了十年。', seealso: ['nabonidus-harran'] },
            { slug: 'dedan-lihyan', title_zh: '德丹（里赫顏）奉獻銘', title_orig: 'Dadanitic (Lihyanite) dedications to Dhū-Ghābat', era: '約前 5 – 前 1 世紀', language: '德丹語（古北阿拉伯語）', provenance: '沙烏地阿拉伯烏拉', status: 'inscription', note: '向主神杜—加巴特獻祭的銘文，常記「獻上某人」為神廟僕役。' },
            { slug: 'nabataean-dushara', title_zh: '納巴泰杜沙拉銘文', title_orig: 'Nabataean inscriptions to Dushara and Allat', era: '約前 1 世紀 – 公元 2 世紀', language: '納巴泰亞蘭語', provenance: '佩特拉、希格拉（瑪甸沙勒）、布斯拉', status: 'inscription', note: '「杜沙拉，我們主的神」；神以方石（betyl）為象，不立人像。', xref: ['希臘羅馬大藏經（羅馬時代阿拉伯行省諸神）'] },
            { slug: 'hegra-tombs', title_zh: '希格拉墓銘', title_orig: 'Nabataean tomb inscriptions of Hegra', era: '公元前 1 – 公元 1 世紀', language: '納巴泰亞蘭語', provenance: '沙烏地阿拉伯希格拉（瑪甸沙勒）', status: 'inscription', extent: '約三十件', note: '墓主刻下誰可以葬入，並以杜沙拉、他的寶座與「曼諾塔特」咒詛擅入者——兼是法律文書與詛咒。' },
          ],
        },
        {
          key: 'nomads',
          label: '沙漠塗鴉',
          label_en: 'Desert Graffiti',
          texts: [
            { slug: 'safaitic', title_zh: '薩法塗鴉', title_orig: 'Safaitic inscriptions', era: '約前 1 世紀 – 公元 4 世紀', language: '薩法語（古北阿拉伯語）', provenance: '敘利亞南部、約旦東北黑石沙漠', status: 'inscription', extent: '逾三萬件', note: '「阿拉特啊，賜他平安」「巴力沙明啊，賜雨」。遊牧者在放牧、哀悼親人時隨手刻下的短禱，偶爾提到「拿巴泰人之年」「羅馬人來的那年」。' },
            { slug: 'hismaic', title_zh: '希斯馬塗鴉', title_orig: 'Hismaic inscriptions', era: '約前 1 世紀 – 公元 4 世紀', language: '希斯馬語（古北阿拉伯語）', provenance: '約旦南部、沙烏地西北', status: 'inscription', extent: '數千件', note: '同類的遊牧者塗鴉，向杜沙拉、阿拉特、「神」（ʾlh）呼求。' },
          ],
        },
      ],
    },
  ],
}
