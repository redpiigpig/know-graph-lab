// 蘇美藏 —— 蘇美語宗教文學
//
// 🚨 兩個年代，不可混為一談（types.ts 檔頭第三條）：
//   成書多在烏爾第三王朝（約前 2112–2004）或伊辛時代，但**現存抄本幾乎全是古巴比倫時代
//   （約前 1800–1700）尼普爾與烏爾的書吏學校習作**——那時蘇美語已是死語言，
//   學生抄它就像中世紀抄拉丁文。我們讀到的「蘇美文學」其實是巴比倫人的蘇美古典課本。
//
// 編號：一律用牛津 ETCSL（Electronic Text Corpus of Sumerian Literature）的分類號，
//   2026-10-02 逐條對過 etcsl.orinst.ox.ac.uk 的線上目錄。ETCSL 有轉寫與英文散文譯本，
//   供非商業學術使用。
//
// 歸藏：依「成書語言」。蘇美—阿卡德雙語本（盧伽爾—埃、烏都格惡魔咒）歸此藏，
//   因為阿卡德語欄是後加的行間譯文。

import type { NeCanon } from './types'

const SUM = '蘇美語'
const OB = '古巴比倫時代抄本（約前 1800–1700）'

export const SUMER_CANON: NeCanon = {
  key: 'sumer',
  name: '蘇美藏',
  name_en: 'Sumerian Canon',
  glyph: '蘇',
  subtitle: '人類最早的文學——以及巴比倫人替它保存下來的那一份',
  scriptural: true,
  language: '蘇美語（含女性與哀歌祭司專用的「埃美薩方言」）',
  era: '約前 2600 – 前 1 世紀',
  terminus: '蘇美語約前 1800 年已不再是口語，但哀歌祭司以埃美薩方言誦唸的禮儀哀歌一直抄到塞琉古時代，與楔形文字同終。',
  columns: { orig: 'available', en: 'available', zh: 'none' },
  summary:
    '蘇美人留下了人類最早的神話、讚歌、哀歌與箴言。最古的抄本出自約前 2600 年的法拉與阿布薩拉比赫，'
    + '大宗則是古巴比倫時代書吏學校的課本——那時蘇美語早已不在街上說了，卻仍是神廟與學問的語言，'
    + '一如拉丁文之於中世紀。本藏依文類分卷，編號用牛津 ETCSL。',
  volumes: [
    {
      key: 'myths',
      sigil: '蘇一',
      name: '神話',
      name_en: 'Myths',
      era: '成書約前 2100 – 前 1800',
      summary:
        '恩基、恩利爾、伊南娜與尼努爾塔四組神話。蘇美的神不是遙遠的主宰，而是會醉、會病、會被騙、會挨罰的城邦之主——'
        + '每一位神都有一座城，神話常常就是城與城之間的關係史。',
      divisions: [
        {
          key: 'enki',
          label: '恩基神話',
          label_en: 'Enki',
          texts: [
            { slug: 'enki-ninhursag', title_zh: '恩基與寧胡爾薩格', title_orig: 'Enki and Ninḫursaĝa', siglum: 'ETCSL 1.1.1', copies: OB, language: SUM, note: '迪爾蒙樂土，「獅子不殺生、狼不叼羊」。恩基吃了禁食的八株植物而病倒，女神為他身上八處病痛各生一神。', bible: '創 2–3 樂園；肋骨（蘇美語 ti 兼有「肋」與「生命」）之說出於此', xref: ['基督教大藏經‧前藏'] },
            { slug: 'enki-ninmah', title_zh: '恩基與寧瑪赫', title_orig: 'Enki and Ninmaḫ', siglum: 'ETCSL 1.1.2', copies: OB, language: SUM, note: '眾神厭倦勞役，恩基以泥造人代神工作；酒宴中兩神比賽造殘缺之人，恩基為每一個都找到用處。', bible: '創 2:7 以泥造人' },
            { slug: 'enki-world-order', title_zh: '恩基與世界秩序', title_orig: 'Enki and the world order', siglum: 'ETCSL 1.1.3', copies: OB, language: SUM, note: '恩基巡行各地，分派職司給眾神、定立河流與耕作之法。伊南娜抱怨沒分到東西。' },
            { slug: 'enki-nibru', title_zh: '恩基往尼普爾之旅', title_orig: 'Enki\'s journey to Nibru', siglum: 'ETCSL 1.1.4', copies: OB, language: SUM, note: '恩基建成埃利都神廟後赴尼普爾，向恩利爾求祝福。' },
            { slug: 'inana-enki', title_zh: '伊南娜與恩基（神力之授）', title_orig: 'Inana and Enki', siglum: 'ETCSL 1.3.1', copies: OB, language: SUM, note: '伊南娜灌醉恩基，騙得一百多項「梅」（me，文明的神聖法則：王權、祭司職、木工、性、哀哭……）運回烏魯克。' },
          ],
        },
        {
          key: 'enlil',
          label: '恩利爾神話',
          label_en: 'Enlil',
          texts: [
            { slug: 'enlil-ninlil', title_zh: '恩利爾與寧利爾', title_orig: 'Enlil and Ninlil', siglum: 'ETCSL 1.2.1', copies: OB, language: SUM, note: '恩利爾強佔少女寧利爾而被眾神逐出尼普爾，入冥府途中三度化身再與她結合，生下冥界諸神與月神。' },
            { slug: 'enlil-sud', title_zh: '恩利爾與蘇德', title_orig: 'Enlil and Sud', siglum: 'ETCSL 1.2.2', copies: OB, language: SUM, note: '同一位女神的另一版本：恩利爾依禮求婚，蘇德婚後改名寧利爾。與上篇並置——同一樁婚姻有暴力版與聘禮版。' },
            { slug: 'nanna-nibru', title_zh: '南納—蘇恩往尼普爾之旅', title_orig: 'Nanna-Suen\'s journey to Nibru', siglum: 'ETCSL 1.5.1', copies: OB, language: SUM, note: '月神自烏爾乘船載滿貢物往尼普爾見父恩利爾——城邦之間獻貢的神話化。' },
            { slug: 'hymn-ekur', title_zh: '恩利爾在埃庫爾', title_orig: 'Enlil in the E-kur (Enlil A)', siglum: 'ETCSL 4.05.1', copies: OB, language: SUM, note: '讚頌恩利爾在尼普爾的神廟「山之屋」：沒有恩利爾，城不得建、牛棚不得立。' },
          ],
        },
        {
          key: 'inana',
          label: '伊南娜神話',
          label_en: 'Inana',
          texts: [
            { slug: 'inana-ebih', title_zh: '伊南娜與埃比赫山', title_orig: 'Inana and Ebiḫ', siglum: 'ETCSL 1.3.2', author: '傳為恩赫杜安娜', copies: OB, language: SUM, note: '山不向女神低頭，伊南娜摧毀了它。' },
            { slug: 'inana-shukaletuda', title_zh: '伊南娜與舒卡雷圖達', title_orig: 'Inana and Šu-kale-tuda', siglum: 'ETCSL 1.3.3', copies: OB, language: SUM, note: '園丁趁女神熟睡侵犯她，伊南娜降血於井水、追索犯者。' },
            { slug: 'inana-an', title_zh: '伊南娜與安', title_orig: 'Inana and An', siglum: 'ETCSL 1.3.5', copies: OB, language: SUM, status: 'fragment', note: '伊南娜從天神安手中取得埃安娜神廟。' },
            { slug: 'inana-bilulu', title_zh: '伊南娜與比盧魯', title_orig: 'Inana and Bilulu', siglum: 'ETCSL 1.4.4', copies: OB, language: SUM, note: '女神為亡夫杜牧茲向害死他的老婦復仇，將其化為皮水袋。' },
          ],
        },
        {
          key: 'ninurta',
          label: '尼努爾塔神話',
          label_en: 'Ninurta',
          texts: [
            { slug: 'lugal-e', title_zh: '盧伽爾—埃（尼努爾塔的功業）', title_orig: 'Lugal-e / Ninurta\'s exploits', siglum: 'ETCSL 1.6.2', copies: '古巴比倫至新亞述、塞琉古抄本，後期附阿卡德語行間譯文', language: `${SUM}（附阿卡德語對譯）`, extent: '約 700 行', note: '戰神擊敗山中惡魔阿薩格，以石堆成山引水灌溉，並逐一判定群石的命運。', xref: ['基督教大藏經‧前藏（尼努爾塔頌詩）'] },
            { slug: 'angim', title_zh: '尼努爾塔返回尼普爾', title_orig: 'Ninurta\'s return to Nibru (An-gim dim-ma)', siglum: 'ETCSL 1.6.1', copies: '古巴比倫至新亞述', language: `${SUM}（後期附阿卡德語對譯）`, note: '凱旋的戰神載著戰利品返回父神之城。' },
            { slug: 'ninurta-turtle', title_zh: '尼努爾塔與烏龜', title_orig: 'Ninurta and the turtle', siglum: 'ETCSL 1.6.3', copies: OB, language: SUM, status: 'fragment', note: '驕傲的尼努爾塔被恩基造的烏龜拖入坑中——神也會被教訓。' },
          ],
        },
        {
          key: 'others',
          label: '其他神祇',
          label_en: 'Other Deities',
          texts: [
            { slug: 'sumerian-flood', title_zh: '蘇美洪水故事', title_orig: 'The Flood story (Eridu Genesis)', siglum: 'ETCSL 1.7.4', copies: '古巴比倫抄本一件（尼普爾）', language: SUM, status: 'fragment', note: '創人、立王城、眾神決意降洪，虔敬的王吉烏蘇德拉造船得救而獲永生。殘缺約三分之二。', bible: '創 6–9', seealso: ['atrahasis', 'gilgamesh-sb'], xref: ['基督教大藏經‧前藏（蘇美爾洪水神話）'] },
            { slug: 'marriage-martu', title_zh: '馬圖的婚事', title_orig: 'The marriage of Martu', siglum: 'ETCSL 1.7.1', copies: OB, language: SUM, note: '遊牧民族之神馬圖求娶城市女神，女友勸她：「他吃生肉、不住房子、死了也不埋」——城市人眼中的遊牧者。' },
            { slug: 'ningishzida-netherworld', title_zh: '寧吉什齊達入冥府', title_orig: 'Ninĝišzida\'s journey to the nether world', siglum: 'ETCSL 1.7.3', copies: OB, language: SUM, note: '植物之神死而入冥府，姊妹哀悼。' },
            { slug: 'grain-sumer', title_zh: '穀物如何來到蘇美', title_orig: 'How grain came to Sumer', siglum: 'ETCSL 1.7.6', copies: OB, language: SUM, status: 'fragment', note: '兩位神從山中帶來大麥——農業的起源神話。' },
          ],
        },
      ],
    },
    {
      key: 'inana-dumuzid',
      sigil: '蘇二',
      name: '伊南娜與杜牧茲',
      name_en: 'Inana and Dumuzid',
      era: '成書約前 2100 – 前 1800',
      summary:
        '天之女王與牧人之神的戀歌、婚禮與死亡。王在新年扮演杜牧茲與女神成婚（「聖婚」），保證土地豐饒；'
        + '杜牧茲每年死去、每年被哀哭——後世以西結書所見「婦女為杜牧茲哭泣」的源頭。',
      divisions: [
        {
          key: 'descent',
          label: '入冥府',
          label_en: 'Descent',
          texts: [
            { slug: 'inana-descent', title_zh: '伊南娜入冥府', title_orig: 'Inana\'s descent to the nether world', siglum: 'ETCSL 1.4.1', copies: OB, language: SUM, extent: '約 410 行', note: '女神穿過七道門、每門被脫去一件衣飾，赤身到姊姊埃列什基伽爾面前被殺，掛在釘上三日。得救後須找替身——她選了不為她哀悼的丈夫杜牧茲。', seealso: ['ishtar-descent'], bible: '結 8:14' },
            { slug: 'dumuzid-dream', title_zh: '杜牧茲之夢', title_orig: 'Dumuzid\'s dream', siglum: 'ETCSL 1.4.3', copies: OB, language: SUM, note: '牧人夢見自己的死，姊姊吉什提南娜解夢；冥界惡鬼追捕他，太陽神三度助他變形逃走。' },
            { slug: 'dumuzid-geshtinana', title_zh: '杜牧茲與吉什提南娜', title_orig: 'Dumuzid and Ĝeštin-ana', siglum: 'ETCSL 1.4.1.1', copies: OB, language: SUM, note: '姊姊願替弟弟在冥府服役半年——一年一死一生的季節循環。' },
          ],
        },
        {
          key: 'love-songs',
          label: '戀歌與聖婚歌',
          label_en: 'Love Songs and Sacred Marriage',
          desc: 'ETCSL 4.08 收戀歌近三十首，此處只列有代表性者；其餘以一條合集代表。',
          texts: [
            { slug: 'dumuzid-enkimdu', title_zh: '杜牧茲與恩基姆杜（牧農之爭）', title_orig: 'Dumuzid and Enkimdu', siglum: 'ETCSL 4.08.33', copies: OB, language: SUM, note: '牧人與農夫爭娶伊南娜，女神原屬意農夫，最後嫁給牧人。', bible: '創 4 該隱與亞伯（牧農對立，結局相反）' },
            { slug: 'song-lettuce', title_zh: '萵苣之歌', title_orig: 'The song of the lettuce (Dumuzid-Inana E)', siglum: 'ETCSL 4.08.05', copies: OB, language: SUM, note: '「他長出了，他萌芽了，他是水邊的萵苣。」新婚的情歌。', bible: '歌 4–5' },
            { slug: 'dumuzid-inana-songs', title_zh: '伊南娜與杜牧茲戀歌集', title_orig: 'Dumuzid-Inana songs A–F1', siglum: 'ETCSL 4.08.01–4.08.32', copies: OB, language: SUM, extent: '約三十首', note: '對唱、求婚、新房、母親的盤問。雅歌的遠親。', bible: '雅歌' },
            { slug: 'iddin-dagan-a', title_zh: '伊丁—達干聖婚頌', title_orig: 'A šir-namursaĝa to Ninsiana for Iddin-Dagan (Iddin-Dagan A)', siglum: 'ETCSL 2.5.3.1', copies: OB, language: SUM, note: '伊辛王在新年與女神同寢的儀式頌歌——聖婚儀式最直接的描述。' },
          ],
        },
      ],
    },
    {
      key: 'uruk-epics',
      sigil: '蘇三',
      name: '烏魯克英雄史詩',
      name_en: 'Epics of Uruk',
      era: '成書約前 2100（烏爾第三王朝）',
      summary:
        '烏魯克三代王恩美爾卡、盧伽爾班達、吉爾伽美什的故事。烏爾第三王朝的王自稱吉爾伽美什之弟，'
        + '這些史詩因此也是王室的家譜。吉爾伽美什的五篇蘇美故事後來被巴比倫人改寫成一部史詩（見巴比倫亞述藏）。',
      divisions: [
        {
          key: 'enmerkar',
          label: '恩美爾卡與盧伽爾班達',
          label_en: 'Enmerkar and Lugalbanda',
          texts: [
            { slug: 'enmerkar-aratta', title_zh: '恩美爾卡與阿拉塔之主', title_orig: 'Enmerkar and the lord of Aratta', siglum: 'ETCSL 1.8.2.3', copies: OB, language: SUM, note: '口信太長使者記不住，恩美爾卡便把話刻在泥板上——蘇美人自己講的文字起源。另有「巧言之咒」：萬民原本同說一種語言。', bible: '創 11:1–9 巴別塔' },
            { slug: 'enmerkar-ensuhgirana', title_zh: '恩美爾卡與恩蘇吉安納', title_orig: 'Enmerkar and En-suḫgir-ana', siglum: 'ETCSL 1.8.2.4', copies: OB, language: SUM, note: '兩城以巫術鬥法，爭伊南娜的眷顧。' },
            { slug: 'lugalbanda-cave', title_zh: '盧伽爾班達在山洞', title_orig: 'Lugalbanda in the mountain cave', siglum: 'ETCSL 1.8.2.1', copies: OB, language: SUM, note: '病倒被遺棄在山洞的王子向日、月、星祈求而痊癒。' },
            { slug: 'lugalbanda-anzud', title_zh: '盧伽爾班達與安祖鳥', title_orig: 'Lugalbanda and the Anzud bird', siglum: 'ETCSL 1.8.2.2', copies: OB, language: SUM, note: '王子餵養巨鳥的雛鳥，得到神行的能力。', seealso: ['anzu'] },
          ],
        },
        {
          key: 'gilgamesh-sumerian',
          label: '吉爾伽美什的蘇美故事',
          label_en: 'Sumerian Gilgamesh Poems',
          texts: [
            { slug: 'gilgamesh-aga', title_zh: '吉爾伽美什與阿伽', title_orig: 'Gilgameš and Aga', siglum: 'ETCSL 1.8.1.1', copies: OB, language: SUM, note: '基什王圍攻烏魯克——唯一一篇沒有神話成分的吉爾伽美什故事，有「長老會與青年會」兩院議事的記載。' },
            { slug: 'gilgamesh-huwawa', title_zh: '吉爾伽美什與胡瓦瓦', title_orig: 'Gilgameš and Ḫuwawa (Versions A, B)', siglum: 'ETCSL 1.8.1.5；1.8.1.5.1', copies: OB, language: SUM, note: '為了不朽的名聲，入雪松林斬殺森林守護者。' },
            { slug: 'gilgamesh-bull', title_zh: '吉爾伽美什與天牛', title_orig: 'Gilgameš and the bull of heaven', siglum: 'ETCSL 1.8.1.2', copies: OB, language: SUM, status: 'fragment', note: '拒絕伊南娜之後，女神遣天牛報復。' },
            { slug: 'gilgamesh-netherworld', title_zh: '吉爾伽美什、恩奇杜與冥府', title_orig: 'Gilgameš, Enkidu and the nether world', siglum: 'ETCSL 1.8.1.4', copies: OB, language: SUM, note: '恩奇杜下冥府取回遺落的球杖而回不來，其魂上來向吉爾伽美什逐一描述亡者的境遇：有七子者如何、無人祭祀者如何。巴比倫標準版第十二塊泥板即其後半的阿卡德語直譯。' },
            { slug: 'gilgamesh-death', title_zh: '吉爾伽美什之死', title_orig: 'The death of Gilgameš', siglum: 'ETCSL 1.8.1.3', copies: OB, language: SUM, status: 'fragment', note: '眾神告訴臨終的英雄：你得了王權，但沒有得到永生。' },
          ],
        },
      ],
    },
    {
      key: 'hymns',
      sigil: '蘇四',
      name: '神廟頌與王頌',
      name_en: 'Temple Hymns and Royal Hymns',
      era: '約前 2600 – 前 1750',
      summary:
        '人類最早的署名作者恩赫杜安娜在此：阿卡德王薩爾貢之女、烏爾月神的女祭司，為四十二座神廟各作一頌，'
        + '又為伊南娜寫下第一人稱的長篇禱詩。王頌則把王寫成神的愛子——烏爾第三王朝的舒爾吉王甚至自稱神。',
      divisions: [
        {
          key: 'temple',
          label: '神廟頌',
          label_en: 'Temple Hymns',
          texts: [
            { slug: 'kesh-temple-hymn', title_zh: '凱什神廟頌', title_orig: 'The Keš temple hymn', siglum: 'ETCSL 4.80.2', era: '約前 2600', copies: '法拉期抄本（約前 2600）與古巴比倫抄本', language: SUM, note: '人類現存最古的文學作品之一，八百年後仍在抄寫，文字幾乎沒變。' },
            { slug: 'temple-hymns', title_zh: '神廟頌集', title_orig: 'The temple hymns', siglum: 'ETCSL 4.80.1', author: '恩赫杜安娜', era: '約前 2250（阿卡德王朝）', copies: OB, language: SUM, extent: '42 首', note: '為蘇美與阿卡德四十二座神廟各作一頌。結尾署名：「編者恩赫杜安娜。我的王啊，有人做了前所未有的事。」' },
            { slug: 'gudea-cylinders', title_zh: '古地亞圓柱銘（寧吉蘇神廟落成記）', title_orig: 'The building of Ninĝirsu\'s temple (Gudea, cylinders A and B)', siglum: 'ETCSL 2.1.7', era: '約前 2125', language: SUM, provenance: '吉爾蘇（泰洛）；羅浮宮藏', status: 'whole', extent: '兩柱共約 1,360 行', note: '拉格什王夢見神命他建廟，請女神解夢，依神示建廟並舉行落成禮——蘇美文學最長的單一文本。', bible: '王上 5–8 所羅門建殿；出 25 帳幕樣式由神指示' },
          ],
        },
        {
          key: 'enheduanna',
          label: '恩赫杜安娜的伊南娜頌',
          label_en: 'Enheduana\'s Hymns to Inana',
          texts: [
            { slug: 'nin-me-sara', title_zh: '伊南娜之頌讚（寧美薩拉）', title_orig: 'The exaltation of Inana (Inana B, nin-me-šara)', siglum: 'ETCSL 4.07.2', author: '恩赫杜安娜', era: '約前 2250', copies: OB, language: SUM, extent: '153 行', note: '女祭司被叛軍逐出烏爾，向伊南娜訴冤求伸——第一人稱的流亡禱詩，人類第一首署名的長詩。' },
            { slug: 'in-nin-sagura', title_zh: '伊南娜頌（大心之女主）', title_orig: 'A hymn to Inana (Inana C, in-nin ša-gur-ra)', siglum: 'ETCSL 4.07.3', author: '傳為恩赫杜安娜', copies: OB, language: SUM, extent: '274 行', note: '伊南娜能「使男變女、女變男」，掌管倒轉與逾越。' },
          ],
        },
        {
          key: 'deities',
          label: '眾神頌',
          label_en: 'Hymns to Deities',
          texts: [
            { slug: 'nanse-a', title_zh: '南舍頌', title_orig: 'A hymn to Nanše (Nanše A)', siglum: 'ETCSL 4.14.1', copies: OB, language: SUM, note: '女神每年在新年審查人心：照顧孤兒寡婦，懲罰改動度量衡者。', bible: '申 25:13–16；箴 11:1' },
            { slug: 'nisaba-a', title_zh: '尼沙巴頌', title_orig: 'A hymn to Nisaba (Nisaba A)', siglum: 'ETCSL 4.16.1', copies: OB, language: SUM, note: '穀物與書寫女神——書吏學校每篇抄本結尾都寫「讚美尼沙巴」。' },
            { slug: 'nanna-hymns', title_zh: '南納月神頌', title_orig: 'Hymns to Nanna (Nanna A–K)', siglum: 'ETCSL 4.13.01–4.13.11', copies: OB, language: SUM, extent: '十一首', note: '烏爾月神的讚歌群。' },
            { slug: 'asarluhi-a', title_zh: '阿薩盧希頌', title_orig: 'A hymn to Asarluḫi (Asarluḫi A)', siglum: 'ETCSL 4.01.1', copies: OB, language: SUM, note: '驅魔之神阿薩盧希後來與馬杜克合一，他的咒術職能成了巴比倫主神的一部分。', seealso: ['enuma-elish'] },
          ],
        },
        {
          key: 'royal',
          label: '王頌',
          label_en: 'Royal Hymns',
          texts: [
            { slug: 'urnamma-a', title_zh: '烏爾納姆之死', title_orig: 'The death of Ur-Namma (Ur-Namma A)', siglum: 'ETCSL 2.4.1.1', copies: OB, language: SUM, note: '烏爾第三王朝開國之王戰死，在冥府向七位冥界之神獻禮——王也會死、也要在冥府排座次。' },
            { slug: 'shulgi-a', title_zh: '舒爾吉頌', title_orig: 'A praise poem of Šulgi (Šulgi A)', siglum: 'ETCSL 2.4.2.01', copies: OB, language: SUM, note: '王一日之內從尼普爾跑到烏爾再跑回來，同一天在兩城舉行節慶。王的自我神化。' },
            { slug: 'shulgi-royal-hymns', title_zh: '舒爾吉王頌集', title_orig: 'Šulgi hymns', siglum: 'ETCSL 2.4.2.01–2.4.2.26', copies: OB, language: SUM, extent: '二十餘首', note: '書吏學校背誦最多的一組王頌。' },
            { slug: 'ishme-dagan-hymns', title_zh: '伊什美—達干王頌集', title_orig: 'Išme-Dagan hymns', siglum: 'ETCSL 2.5.4', copies: OB, language: SUM, extent: '二十餘首', note: '伊辛王朝延續烏爾第三王朝的王頌傳統。' },
          ],
        },
      ],
    },
    {
      key: 'laments',
      sigil: '蘇五',
      name: '哀歌',
      name_en: 'Laments',
      era: '約前 2000 – 前 1 世紀',
      summary:
        '城被毀，是因為神離開了它。烏爾第三王朝覆亡後寫成的五篇城市哀歌，描寫神祇棄城、敵軍屠戮、'
        + '屍首塞滿街道；結尾神回轉、城重建。後來演變成哀歌祭司（gala）以埃美薩方言誦唸的定期禮儀哀歌，'
        + '一直唱到塞琉古時代。耶利米哀歌的體裁與主題都在這裡。',
      divisions: [
        {
          key: 'city',
          label: '城市哀歌',
          label_en: 'City Laments',
          texts: [
            { slug: 'lament-urim', title_zh: '烏爾哀歌', title_orig: 'The lament for Urim', siglum: 'ETCSL 2.2.2', era: '約前 1950', copies: OB, language: SUM, extent: '約 440 行', note: '烏爾的守護女神寧加爾哭求恩利爾收回成命而不得，眼見自己的城被毀。', bible: '耶利米哀歌' },
            { slug: 'lament-sumer-urim', title_zh: '蘇美與烏爾哀歌', title_orig: 'The lament for Sumer and Urim', siglum: 'ETCSL 2.2.3', copies: OB, language: SUM, extent: '約 520 行', note: '眾神集會決定終結烏爾王朝：「王權從無永遠。」', bible: '耶利米哀歌；結 10 神的榮耀離開聖殿' },
            { slug: 'lament-nibru', title_zh: '尼普爾哀歌', title_orig: 'The lament for Nibru', siglum: 'ETCSL 2.2.4', copies: OB, language: SUM, note: '結尾轉為伊辛王重建尼普爾的頌歌。' },
            { slug: 'lament-unug', title_zh: '烏魯克哀歌', title_orig: 'The lament for Unug', siglum: 'ETCSL 2.2.5', copies: OB, language: SUM, status: 'fragment' },
            { slug: 'lament-eridug', title_zh: '埃利都哀歌', title_orig: 'The lament for Eridug', siglum: 'ETCSL 2.2.6', copies: OB, language: SUM, status: 'fragment' },
            { slug: 'curse-agade', title_zh: '阿卡德之咒', title_orig: 'The cursing of Agade', siglum: 'ETCSL 2.1.5', copies: OB, language: SUM, note: '阿卡德王納拉姆辛拆毀恩利爾神廟，眾神詛咒阿卡德城永遠荒廢——咒語應驗了，阿卡德城至今未被找到。', bible: '賽 13–14 對巴比倫的詛咒' },
          ],
        },
        {
          key: 'emesal',
          label: '禮儀哀歌（埃美薩方言）',
          label_en: 'Emesal Liturgies',
          texts: [
            { slug: 'balag', title_zh: '巴拉格哀歌', title_orig: 'balaĝ laments', era: '古巴比倫時代起，抄至塞琉古時代', copies: '古巴比倫、新亞述、塞琉古抄本，後期附阿卡德語對譯', language: '蘇美語埃美薩方言（附阿卡德語）', extent: '標準曲目約五十首', note: '以巴拉格鼓伴奏、在神廟修繕或拆舊牆前唱給神聽的長篇哀歌，安撫神怒。' },
            { slug: 'ershema', title_zh: '埃爾舍瑪哀歌', title_orig: 'eršema laments', copies: '古巴比倫至塞琉古', language: '蘇美語埃美薩方言', note: '以舍姆鼓伴奏的短篇哀歌，常接在巴拉格之後。' },
            { slug: 'ershahunga', title_zh: '心之平息禱', title_orig: 'eršaḫuĝa (prayers to appease the heart)', copies: '中巴比倫至新巴比倫', language: '蘇美語埃美薩方言（附阿卡德語）', note: '個人悔罪禱文：「我的神啊，我的罪多……求你平息你的心。」', bible: '詩 6；詩 38；詩 51（悔罪詩）' },
          ],
        },
      ],
    },
    {
      key: 'wisdom',
      sigil: '蘇六',
      name: '智慧、辯論與諺語',
      name_en: 'Wisdom, Debates and Proverbs',
      era: '約前 2500 – 前 1700',
      summary:
        '人類最早的教子書、最早的「義人受苦」詩、最早的諺語集，以及一種蘇美特有的文體：兩物相爭誰更有用，由神裁判。',
      divisions: [
        {
          key: 'instructions',
          label: '訓言與受苦者',
          label_en: 'Instructions and the Sufferer',
          texts: [
            { slug: 'shuruppag', title_zh: '舒魯帕克訓言', title_orig: 'The instructions of Šuruppag', siglum: 'ETCSL 5.6.1', era: '約前 2500', copies: '阿布薩拉比赫期抄本（約前 2500）與古巴比倫抄本', language: SUM, note: '洪水英雄之父教子：「不要買驢子，若牠會叫……」現存最古的智慧文學。', seealso: ['sumerian-flood'] },
            { slug: 'man-and-god', title_zh: '人與其神', title_orig: 'A man and his god', siglum: 'ETCSL 5.2.4', copies: OB, language: SUM, extent: '約 140 行', note: '一個無故受苦的人向自己的保護神哭訴，終於得到回應——「蘇美的約伯」。', bible: '約伯記' },
            { slug: 'early-rulers', title_zh: '古王之歌', title_orig: 'The poem of early rulers', siglum: 'ETCSL 5.2.5', copies: '古巴比倫抄本；另有烏加里特、埃馬爾出土的雙語抄本', language: SUM, note: '吉爾伽美什、阿伽、烏納皮什提如今在哪裡？——及時行樂之歌。', bible: '傳 1–2', seealso: ['harpers-song'] },
            { slug: 'farmers-instructions', title_zh: '農夫訓言', title_orig: 'The farmer\'s instructions', siglum: 'ETCSL 5.6.3', copies: OB, language: SUM, note: '恩利爾之子尼努爾塔教人耕作一年的工序。' },
          ],
        },
        {
          key: 'debates',
          label: '辯論詩',
          label_en: 'Debate Poems',
          texts: [
            { slug: 'hoe-plough', title_zh: '鋤與犁之辯', title_orig: 'The debate between Hoe and Plough', siglum: 'ETCSL 5.3.1', copies: OB, language: SUM },
            { slug: 'grain-sheep', title_zh: '穀與羊之辯', title_orig: 'The debate between Grain and Sheep', siglum: 'ETCSL 5.3.2', copies: OB, language: SUM, note: '開頭是一段創世：眾神造穀與羊之前，人類赤身吃草如羊。' },
            { slug: 'winter-summer', title_zh: '冬與夏之辯', title_orig: 'The debate between Winter and Summer', siglum: 'ETCSL 5.3.3', copies: OB, language: SUM },
            { slug: 'bird-fish', title_zh: '鳥與魚之辯', title_orig: 'The debate between Bird and Fish', siglum: 'ETCSL 5.3.5', copies: OB, language: SUM },
            { slug: 'song-hoe', title_zh: '鋤之歌', title_orig: 'The song of the hoe', siglum: 'ETCSL 5.5.4', copies: OB, language: SUM, note: '恩利爾以鋤破土，人如植物從地裡長出——另一種造人神話。' },
          ],
        },
        {
          key: 'proverbs',
          label: '諺語集',
          label_en: 'Proverb Collections',
          texts: [
            { slug: 'sumerian-proverbs', title_zh: '蘇美諺語集', title_orig: 'Proverbs: collections 1–28 and others', siglum: 'ETCSL 6.1.01–6.2.5', copies: OB, language: SUM, extent: '二十八集，逾千條', note: '「窮人死了比活著好。」「友誼一日，親戚永遠。」書吏學校的抄寫練習。', bible: '箴言' },
          ],
        },
      ],
    },
    {
      key: 'history',
      sigil: '蘇七',
      name: '王表與聖史',
      name_en: 'King Lists and Sacred History',
      era: '約前 2100 – 前 1700',
      summary: '王權「從天而降」，洪水之前有八王共治二十四萬一千二百年，洪水之後王權再降——蘇美人自己寫的世界史，神學多於史實。',
      divisions: [
        {
          key: 'lists',
          label: '王表',
          label_en: 'King Lists',
          texts: [
            { slug: 'sumerian-king-list', title_zh: '蘇美王表', title_orig: 'The Sumerian king list', siglum: 'ETCSL 2.1.1', era: '烏爾第三王朝成書，伊辛時代續修', copies: '古巴比倫抄本十餘件，以魏德納稜柱（WB 444）最完整', language: SUM, note: '洪水前諸王動輒在位數萬年，洪水後遞減——與創世記第五章的壽數遞減結構相同。', bible: '創 5；創 11:10–26' },
            { slug: 'lagash-rulers', title_zh: '拉格什諸王', title_orig: 'The rulers of Lagaš', siglum: 'ETCSL 2.1.2', copies: OB, language: SUM, note: '被蘇美王表刻意遺漏的拉格什，自己寫了一份王表回應，開頭從洪水之後人類不懂耕作寫起。' },
            { slug: 'tummal', title_zh: '圖馬勒記', title_orig: 'The history of the Tummal', siglum: 'ETCSL 2.1.3', copies: OB, language: SUM, note: '尼普爾寧利爾聖所的歷代修建者名單，吉爾伽美什也在其中。' },
          ],
        },
      ],
    },
    {
      key: 'incantations',
      sigil: '蘇八',
      name: '咒文與古代書目',
      name_en: 'Incantations and Ancient Catalogues',
      era: '約前 2600 – 前 1 世紀',
      summary:
        '最古的蘇美咒文出自約前 2600 年的法拉，與最早的文學作品同時。另收古代書吏自己編的文學書目——'
        + '書目上的篇名有一部分至今未曾出土，只知其名。',
      divisions: [
        {
          key: 'incantations',
          label: '咒文',
          label_en: 'Incantations',
          texts: [
            { slug: 'fara-incantations', title_zh: '法拉與埃卜拉早期咒文', title_orig: 'Early Dynastic incantations (Fara, Ebla)', era: '約前 2600 – 前 2400', language: '蘇美語（埃卜拉本以埃卜拉語讀出）', provenance: '法拉（舒魯帕克）、埃卜拉', status: 'fragment', note: '現存最古的咒文，對付蛇、蠍與惡鬼；埃卜拉出土的同一批咒文顯示它們早已越過語言邊界流傳。' },
            { slug: 'udug-hul', title_zh: '烏都格惡魔咒', title_orig: 'Udug-ḫul / Utukkū lemnūtu', era: '古巴比倫時代成形，第一千紀定為十六塊泥板', copies: '古巴比倫至塞琉古', language: '蘇美語（附阿卡德語對譯）', note: '驅逐惡鬼的大型咒文系列，以恩基與其子阿薩盧希的對話為框架：「我該怎麼辦？」「我知道的你也知道。」', seealso: ['asarluhi-a', 'maqlu'] },
          ],
        },
        {
          key: 'catalogues',
          label: '古代文學書目',
          label_en: 'Ancient Literary Catalogues',
          texts: [
            { slug: 'literary-catalogues', title_zh: '尼普爾與烏爾文學書目', title_orig: 'Ur III and OB literary catalogues', siglum: 'ETCSL 0.1.1–0.2.13', era: '烏爾第三王朝至古巴比倫', language: SUM, status: 'fragment', note: '書吏以每篇首行為名列出館藏——人類最早的圖書目錄。' },
            { slug: 'lost-sumerian-works', title_zh: '書目中未出土的篇章', title_orig: 'Works known only from catalogue incipits', language: SUM, status: 'lost-listed', via: '尼普爾與烏爾文學書目（ETCSL 0.1–0.2）', note: '書目上的首行有數十條對不上任何已出土的作品。它們存在過、被抄過、被編目過，然後沒了。' },
          ],
        },
      ],
    },
  ],
}
