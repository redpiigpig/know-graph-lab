// 烏加里特藏
//
// 1928 年敘利亞拉斯沙姆拉一個農夫犁田犁出一座墓，次年起法國隊挖出烏加里特城與它的泥板庫。
// 這批泥板用一種三十個字母的楔形字母文字寫成，語言與希伯來語極近。
// 聖經學因此第一次讀到迦南人自己寫的宗教文獻——在此之前，迦南宗教只有它的敵人（希伯來先知）的描述。
//
// 斷限：烏加里特約前 1185 年被「海上民族」之亂焚毀，從此再未重建。本藏起訖只有兩百年。
//   🚨 最後一批泥板還在窯裡烘烤時城就毀了——有一封信寫著「敵船已到，城中已被焚燒」，
//   沒有寄出。
//
// 編號：一律用 KTU／CAT（Dietrich–Loretz–Sanmartín《烏加里特楔形字母文獻》）。
// 歸藏：烏加里特出土的胡里特語讚歌按宗教系統歸「赫梯與胡里特藏」，此處以互見指回；
//   烏加里特出土的阿卡德語文獻若屬本地祭儀（如三語神表），仍歸本藏。

import type { NeCanon } from './types'

const UG = '烏加里特語'
const RS = '烏加里特（拉斯沙姆拉）'

export const UGARIT_CANON: NeCanon = {
  key: 'ugarit',
  name: '烏加里特藏',
  name_en: 'Ugaritic Canon',
  glyph: '烏',
  subtitle: '迦南人自己寫下的迦南宗教',
  scriptural: true,
  language: '烏加里特語（楔形字母）；神表另有阿卡德語、胡里特語',
  era: '約前 1400 – 前 1185',
  terminus: '約前 1185 年城毀於海上民族之亂，從此未再重建；末批泥板還在窯中。',
  columns: { orig: 'available', en: 'copyright', zh: 'none' },
  summary:
    '巴力與海、與死亡之戰；至高神伊勒坐在兩河源頭的帳幕中，人稱「眾神與人之父」；'
    + '女戰神阿娜特涉血及膝。這些名字原本只在希伯來聖經的譴責裡出現，1929 年起才有了迦南人自己的版本。'
    + '詩篇與先知書裡「駕雲者」「打碎海怪的頭」「利維坦，那曲行的蛇」，原來都是巴力史詩的詞彙。',
  volumes: [
    {
      key: 'baal',
      sigil: '烏一',
      name: '巴力史詩',
      name_en: 'The Baal Cycle',
      era: '抄於約前 1350（書吏伊利米爾庫）',
      summary:
        '六塊泥板，由大祭司的書吏伊利米爾庫抄寫並署名。巴力戰勝海神雅姆、建成宮殿、被死神莫特吞下、'
        + '阿娜特劈殺莫特、巴力復活。雨季與旱季的循環，也是王權的神話。泥板間有缺，順序學界仍有爭議。',
      divisions: [
        {
          key: 'cycle',
          label: '三部',
          label_en: 'The Three Episodes',
          texts: [
            { slug: 'baal-cycle', title_zh: '巴力史詩（全組）', title_orig: 'Baal Cycle', siglum: 'KTU 1.1–1.6', author: '伊利米爾庫抄（署名）', language: UG, provenance: RS, extent: '六塊泥板，約 1,800 行（含缺損）', note: '全組概覽條，以下三條為其三個段落。', xref: ['基督教大藏經‧前藏'] },
            { slug: 'baal-yamm', title_zh: '巴力戰雅姆', title_orig: 'Baal and Yamm', siglum: 'KTU 1.1–1.2', language: UG, provenance: RS, status: 'fragment', note: '工匠神科塔為巴力造兩根棍棒「驅逐者」與「追趕者」，擊碎海神。「雅姆死了！巴力要作王！」', bible: '詩 74:13–14；詩 93；伯 26:12', seealso: ['astarte-papyrus'] },
            { slug: 'baal-palace', title_zh: '巴力的宮殿', title_orig: 'Baal\'s Palace', siglum: 'KTU 1.3–1.4', language: UG, provenance: RS, note: '阿娜特屠戮眾人涉血及膝；亞舍拉向伊勒求情，准巴力建宮。宮成後巴力開窗、雷聲響徹大地。', bible: '詩 29「耶和華的聲音」；撒下 7 建殿' },
            { slug: 'baal-mot', title_zh: '巴力與莫特', title_orig: 'Baal and Mot', siglum: 'KTU 1.5–1.6', language: UG, provenance: RS, note: '死神張口「一唇抵地、一唇抵天」吞下巴力。伊勒自坐於塵土哀哭。阿娜特以刀劈、以篩篩、以火燒、以磨磨、撒在田裡餵鳥。巴力復活，「天降油、溪流蜜」。', bible: '賽 25:8「祂要吞滅死亡直到永遠」；何 6:1–2；賽 27:1（利維坦）' },
          ],
        },
        {
          key: 'related',
          label: '巴力短篇',
          label_en: 'Other Baal Texts',
          texts: [
            { slug: 'baal-heifer', title_zh: '巴力與母牛', title_orig: 'Baal and the Heifer', siglum: 'KTU 1.10–1.11', language: UG, provenance: RS, status: 'fragment', note: '巴力與化身為母牛的阿娜特交合，生下一頭牛犢。' },
            { slug: 'baal-devourers', title_zh: '巴力與吞噬者', title_orig: 'Baal and the Devourers', siglum: 'KTU 1.12', language: UG, provenance: RS, status: 'fragment', note: '伊勒的婢女在曠野生下怪物，巴力前往獵殺而倒下。' },
          ],
        },
      ],
    },
    {
      key: 'legends',
      sigil: '烏二',
      name: '王者與英雄傳奇',
      name_en: 'Royal Legends',
      era: '抄於約前 1350',
      summary: '人間的王與英雄如何與神打交道：求子、立約、失信、喪子、復仇。族長故事的迦南鄰居。',
      divisions: [
        {
          key: 'legends',
          label: '傳奇',
          label_en: 'Legends',
          texts: [
            { slug: 'kirta', title_zh: '基塔傳奇', title_orig: 'Kirta Epic', siglum: 'KTU 1.14–1.16', author: '伊利米爾庫抄', language: UG, provenance: RS, status: 'fragment', extent: '三塊泥板', note: '王失去了全家，伊勒在夢中指示他出征迎娶公主；他途中向亞舍拉許願卻沒還願，因而病倒，兒子趁機要他讓位。', bible: '創 15、創 24 族長求子與求婚；伯 1 喪盡家人' },
            { slug: 'aqhat', title_zh: '阿哈特傳奇', title_orig: 'Aqhat Epic', siglum: 'KTU 1.17–1.19', author: '伊利米爾庫抄', language: UG, provenance: RS, status: 'fragment', extent: '三塊泥板', note: '義人達尼伊勒「在城門口為寡婦伸冤、為孤兒斷案」，求得一子阿哈特。阿娜特想要阿哈特的神弓，許他永生被拒，便殺了他；姊姊帕吉特喬裝去為弟弟復仇，故事在此中斷。', bible: '結 14:14、28:3 的「但以理」（Dnʾl）與約伯、挪亞並列為古代義人' },
            { slug: 'rephaim', title_zh: '拉菲烏姆文', title_orig: 'Rephaim Texts', siglum: 'KTU 1.20–1.22', language: UG, provenance: RS, status: 'fragment', note: '伊勒召請「拉菲烏姆」（王室亡靈）乘車赴宴——祖先崇拜的神話化。', bible: '賽 14:9、26:14；伯 26:5 的「利乏音」（陰魂）' },
          ],
        },
      ],
    },
    {
      key: 'short-myths',
      sigil: '烏三',
      name: '短篇神話與咒文',
      name_en: 'Short Myths and Incantations',
      era: '約前 1300 – 前 1185',
      summary: '多附有儀式指示，看得出是在祭儀中念的：神的婚禮、神的醉酒、對付毒蛇的咒文。',
      divisions: [
        {
          key: 'myths',
          label: '短篇神話',
          label_en: 'Short Myths',
          texts: [
            { slug: 'shahar-shalim', title_zh: '沙哈與沙林的誕生（嘉神之生）', title_orig: 'Birth of the Gracious Gods (Šaḥar and Šalim)', siglum: 'KTU 1.23', language: UG, provenance: RS, note: '伊勒在海邊與兩個女子交合，生下晨星沙哈與暮星沙林。附有演出的舞台指示。', bible: '賽 14:12「明亮之星，早晨之子」（ben-šaḥar）；「耶路撒冷」之名中的沙林（Šalim）' },
            { slug: 'nikkal-yarikh', title_zh: '尼卡與亞里赫的婚禮', title_orig: 'Nikkal and Yarikh', siglum: 'KTU 1.24', language: UG, provenance: RS, note: '月神向果園女神提親、議聘金——一首為人間婚禮唱的神界婚歌。', seealso: ['hurrian-hymn-nikkal'] },
            { slug: 'el-marzeah', title_zh: '伊勒的盛宴（伊勒醉酒）', title_orig: 'El\'s Divine Feast (marzeaḥ)', siglum: 'KTU 1.114', language: UG, provenance: RS, note: '伊勒在「馬澤阿」宴會上喝到爛醉，倒在自己的糞便裡，背面附治宿醉的藥方。', bible: '摩 6:7；耶 16:5 的 marzeaḥ（「宴樂」「喪家」）' },
          ],
        },
        {
          key: 'incantations',
          label: '咒文',
          label_en: 'Incantations',
          texts: [
            { slug: 'horon-snake', title_zh: '霍倫蛇咒', title_orig: 'Incantation against snakebite (Horon)', siglum: 'KTU 1.100', language: UG, provenance: RS, note: '母馬之女向十二位神逐一求解蛇毒都不成，最後霍倫砍下「檉柳」解了毒，娶她為妻。' },
            { slug: 'horon-1-107', title_zh: '蛇咒之二', title_orig: 'Incantation against snakebite', siglum: 'KTU 1.107', language: UG, provenance: RS, status: 'fragment' },
          ],
        },
      ],
    },
    {
      key: 'cult',
      sigil: '烏四',
      name: '祭儀',
      name_en: 'Cultic Texts',
      era: '約前 1300 – 前 1185',
      summary:
        '神表、獻祭表、王室喪禮與國難時的禱文——烏加里特神廟的實際運作。'
        + '利未記裡的祭名（平安祭 šlmm、燔祭）在這裡已經出現，用的是同一個詞。',
      divisions: [
        {
          key: 'pantheon',
          label: '神表與獻祭表',
          label_en: 'Pantheon and Offering Lists',
          texts: [
            { slug: 'ugarit-pantheon', title_zh: '烏加里特神表（三語）', title_orig: 'Pantheon list (Ugaritic, Akkadian, Hurrian)', siglum: 'KTU 1.47；1.118；RS 20.24', language: '烏加里特語、阿卡德語（另有胡里特語對照）', provenance: RS, status: 'whole', note: '「山之神、伊勒、達干、巴力……」三種語言各寫一份，可以逐條對出神名——阿卡德語本把巴力寫成「阿達德」。' },
            { slug: 'ugarit-offerings', title_zh: '獻祭與節期表', title_orig: 'Sacrificial and ritual calendars', siglum: 'KTU 1.39；1.41；1.87 等', language: UG, provenance: RS, status: 'fragment', note: '某月某日向哪位神獻什麼。1.41 與 1.87 是同一份節期的兩個抄本，可互補。', bible: '利 23；民 28–29', xref: ['基督教大藏經‧前藏（烏加列獻祭與神祇名錄）'] },
          ],
        },
        {
          key: 'royal-cult',
          label: '王室與國難',
          label_en: 'Royal Cult and National Crisis',
          texts: [
            { slug: 'royal-funerary-ugarit', title_zh: '王室喪葬儀文', title_orig: 'Royal funerary text', siglum: 'KTU 1.161', era: '約前 1200（末代王阿穆拉比即位時）', language: UG, provenance: RS, status: 'whole', note: '召喚歷代先王的亡靈（拉菲烏姆）前來，太陽女神引領亡王入冥府，最後為新王與城祈求「平安」。', seealso: ['rephaim'] },
            { slug: 'siege-prayer', title_zh: '城被圍時向巴力禱', title_orig: 'Prayer to Baal in time of siege', siglum: 'KTU 1.119', language: UG, provenance: RS, note: '「若強敵攻你的城門……你們要舉目向巴力：『巴力啊，求你趕走強敵……我們要獻上公牛、還願、獻頭生的……』巴力必聽你們的禱告。」', bible: '王下 3:27 摩押王獻長子' },
            { slug: 'national-atonement', title_zh: '全民贖罪儀文', title_orig: 'National atonement ritual', siglum: 'KTU 1.40', language: UG, provenance: RS, note: '為男人、女人、烏加里特人、外邦人各獻一次，求赦「無論是因忿怒、焦躁或言語而犯的罪」。', bible: '利 4–5；利 16' },
          ],
        },
        {
          key: 'divination',
          label: '占卜',
          label_en: 'Divination',
          texts: [
            { slug: 'ugarit-liver-models', title_zh: '烏加里特泥製肝模型', title_orig: 'Clay liver and lung models', siglum: 'KTU 1.127；1.141–1.144', language: UG, provenance: RS, status: 'inscription', note: '刻有兆辭的泥製羊肝與羊肺——巴比倫肝卜術傳到地中海岸的證據。', seealso: ['barutu'] },
            { slug: 'ugarit-birth-omens', title_zh: '畸胎兆辭', title_orig: 'Birth omens', siglum: 'KTU 1.103 + 1.145', language: UG, provenance: RS, status: 'fragment', seealso: ['shumma-izbu'] },
          ],
        },
      ],
    },
  ],
}
