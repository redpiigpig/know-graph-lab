// 埃及藏 —— 古埃及宗教文獻（含庫施／努比亞）
//
// 斷限：金字塔文（約前 2350，烏納斯王金字塔）起，止於菲萊島。
//   · 最後一則聖書體銘文：菲萊，公元 394 年（埃斯梅特—阿霍姆塗鴉）
//   · 最後一則世俗體塗鴉：菲萊，公元 452 年
//   · 菲萊伊西斯神廟由查士丁尼下令關閉，約 535–537 年（普羅柯比《戰史》一‧19）
//   與希臘羅馬大藏經止於 529 年幾乎同時——不是編者安排，史料本來如此。
//
// 編號：紙草以館藏號為準（BM EA＝大英博物館埃及部；P. Berlin＝柏林埃及博物館），
//   喪葬文以 PT（金字塔文咒語）／CT（棺槨文咒語）／BD（亡靈書章）為準。

import type { NeCanon } from './types'

const EG = '古埃及文（中埃及語）'
const LATE = '古埃及文（新埃及語）'
const DEM = '世俗體埃及文'

export const EGYPT_CANON: NeCanon = {
  key: 'egypt',
  name: '埃及藏',
  name_en: 'Egyptian Canon',
  glyph: '埃',
  subtitle: '尼羅河谷三千年的神廟、墓室與書吏之學',
  scriptural: true,
  language: '古埃及文（古／中／新埃及語、世俗體）；庫施卷另有麥羅埃文',
  era: '約前 2350 – 公元 452',
  terminus: '止於菲萊島：最後一則聖書體銘文（394）與最後一則世俗體塗鴉（452）都刻在伊西斯神廟的牆上。',
  columns: { orig: 'available', en: 'available', zh: 'none' },
  summary:
    '古埃及宗教沒有一部「經」，有的是一整套為不同場合寫成的文書：刻在金字塔墓室牆上讓亡王升天的咒語、'
    + '寫在棺木內壁讓貴族也能復活的咒語、抄在紙草上隨葬的《亡靈書》、新王國王陵裡逐時描繪太陽夜行的冥界之書，'
    + '加上神廟牆上的創世神學、書吏學校背誦的智慧訓言、與民間的頌詩和魔法紙草。'
    + '本藏依文類分卷，卷內依成書早晚排列。喪葬文獻佔了大半——這不是編者偏好，而是乾燥的墓室替我們保存下來的就是這些。',
  volumes: [
    {
      key: 'pyramid-coffin',
      sigil: '埃一',
      name: '金字塔文與棺槨文',
      name_en: 'Pyramid Texts and Coffin Texts',
      era: '約前 2350 – 前 1650',
      summary:
        '人類現存最古的大型宗教文獻。古王國末期先刻在國王金字塔的墓室牆上，只為法老一人升天；'
        + '第一中間期以後，地方貴族把同類咒語寫在自己的棺木內壁——來世從王室特權變成凡人也能企求的事，'
        + '學者稱之為「來世的民主化」。',
      divisions: [
        {
          key: 'pt',
          label: '金字塔文',
          label_en: 'Pyramid Texts',
          texts: [
            { slug: 'pt-unas', title_zh: '烏納斯王金字塔文', title_orig: 'Pyramid Texts of Unas', siglum: 'PT（烏納斯本）', era: '約前 2350（第五王朝末）', language: '古埃及文（古埃及語）', provenance: '薩卡拉，烏納斯金字塔', status: 'inscription', extent: '228 篇咒語', note: '現存第一份金字塔文，刻滿墓室與前室的牆面。〈食人頌〉（PT 273–274）即在此：亡王吞食眾神以取其力。' },
            { slug: 'pt-teti-pepi', title_zh: '第六王朝諸王金字塔文', title_orig: 'Pyramid Texts of Teti, Pepi I, Merenre, Pepi II', siglum: 'PT', era: '約前 2340 – 前 2180', language: '古埃及文（古埃及語）', provenance: '薩卡拉', status: 'inscription', extent: '連同烏納斯本共約 800 篇', note: '各王陵的咒語組合不同、互有增刪；今日通行的「金字塔文」編號是近代學者把各陵合編後的序號，不是古人的分篇。' },
            { slug: 'pt-queens', title_zh: '王后金字塔文', title_orig: 'Pyramid Texts of the queens of Pepi II', siglum: 'PT', era: '約前 2200', language: '古埃及文（古埃及語）', provenance: '薩卡拉，奈特、伊普特、烏傑布滕諸王后金字塔', status: 'inscription', note: '金字塔文第一次用在國王以外的人身上，是「來世民主化」的第一步。' },
          ],
        },
        {
          key: 'ct',
          label: '棺槨文',
          label_en: 'Coffin Texts',
          texts: [
            { slug: 'ct-corpus', title_zh: '棺槨文', title_orig: 'Coffin Texts', siglum: 'CT 1–1185', era: '約前 2100 – 前 1650（第一中間期至中王國）', language: EG, provenance: '中埃及諸州墓地，以貝爾舍為最多', status: 'composite', extent: '1,185 篇咒語', note: '寫在貴族木棺內壁的咒語，承金字塔文而大幅擴充。CT 1130 有造物主自述「我造四風、造大水、造人人平等」——古代罕見的平等宣言。' },
            { slug: 'two-ways', title_zh: '兩道之書', title_orig: 'Book of Two Ways', siglum: 'CT 1029–1130', era: '約前 2000', language: EG, provenance: '貝爾舍棺木', status: 'composite', note: '畫在棺底的冥界地圖：水路與陸路兩道，中間隔著火湖。現存最古的「來世地圖」。' },
            { slug: 'ct-shu', title_zh: '舒神諸咒（赫利奧波利斯創世之說）', title_orig: 'Coffin Texts Spells 75–83 (Shu spells)', siglum: 'CT 75–83', era: '約前 2000', language: EG, provenance: '中埃及棺木', status: 'composite', note: '亡者化身為空氣之神舒，自述從阿圖姆的鼻息中被生出。赫利奧波利斯九神創世說最完整的早期陳述之一。', seealso: ['bremner-rhind-creation'] },
          ],
        },
      ],
    },
    {
      key: 'book-of-dead',
      sigil: '埃二',
      name: '亡靈書與晚期喪葬書',
      name_en: 'The Book of the Dead and Later Funerary Books',
      era: '約前 1650 – 公元 2 世紀',
      summary:
        '古埃及人自己的書名是《出於白晝之書》（rw nw prt m hrw）。新王國起抄在紙草上隨葬，'
        + '不是一部有固定篇章的書，而是一個咒語庫，每一卷由喪家按財力與偏好挑選抄寫。'
        + '第 125 章的「秤心」與四十二條否認罪過，是古代世界最早的系統化道德審判。',
      divisions: [
        {
          key: 'bd',
          label: '亡靈書',
          label_en: 'Book of the Dead',
          texts: [
            { slug: 'bd-corpus', title_zh: '亡靈書（出於白晝之書）', title_orig: 'rw nw prt m hrw', siglum: 'BD 1–192', era: '約前 1650 起（第二中間期），沿用至托勒密時代', language: EG, provenance: '底比斯等地墓葬', status: 'composite', extent: '約 192 章', note: '章次是 1842 年萊普修斯據都靈紙草所編，後世沿用；古代沒有任何一卷包含全部章節。' },
            { slug: 'bd-125', title_zh: '亡靈書第 125 章：秤心與否認罪過', title_orig: 'BD 125 (Negative Confession)', siglum: 'BD 125', era: '新王國', language: EG, status: 'composite', note: '亡者在奧西里斯與四十二位審判神前逐一宣告「我沒有……」，其心臟與瑪特之羽同秤。', bible: '可與伯 31 約伯的清白自誓對讀' },
            { slug: 'papyrus-ani', title_zh: '阿尼紙草', title_orig: 'Papyrus of Ani', siglum: 'BM EA 10470', era: '約前 1250（第十九王朝）', language: EG, provenance: '底比斯；大英博物館藏', status: 'whole', extent: '長約 24 公尺', note: '彩繪最精、最常被複製的一卷亡靈書。', xref: ['基督教大藏經‧前藏（亡靈書‧阿尼紙草本）'] },
            { slug: 'papyrus-hunefer', title_zh: '胡內費紙草', title_orig: 'Papyrus of Hunefer', siglum: 'BM EA 9901', era: '約前 1300（第十九王朝）', language: EG, provenance: '底比斯；大英博物館藏', status: 'whole', note: '秤心圖最清晰的版本之一，另有「開口儀式」場景。' },
            { slug: 'turin-bd', title_zh: '都靈亡靈書（伊烏菲安赫紙草）', title_orig: 'Papyrus of Iufankh', siglum: 'P. Turin 1791', era: '托勒密時代', language: EG, provenance: '都靈埃及博物館', status: 'whole', note: '萊普修斯據此編定今日通用的章次——「定本」其實是一卷很晚的抄本。' },
          ],
        },
        {
          key: 'late-funerary',
          label: '晚期喪葬書',
          label_en: 'Late Funerary Books',
          texts: [
            { slug: 'book-of-breathing', title_zh: '呼吸之書', title_orig: 'Book of Breathing (šꜥt n snsn)', era: '托勒密至羅馬時代', language: `${EG}；${DEM}`, status: 'composite', note: '晚期取代亡靈書的簡本，託名伊西斯為奧西里斯所作，讓亡者「每天呼吸」。' },
            { slug: 'traversing-eternity', title_zh: '穿越永恆之書', title_orig: 'Book of Traversing Eternity', era: '托勒密至羅馬時代', language: EG, status: 'composite', note: '亡者的魂遊歷各大神廟節慶，等於一份晚期埃及的聖地巡禮。' },
            { slug: 'opening-of-mouth', title_zh: '開口儀式', title_orig: 'Opening of the Mouth (wpt-r)', era: '古王國起，新王國定型', language: EG, provenance: '底比斯王陵與貴族墓（以塞提一世陵、雷赫米爾墓為完整）', status: 'composite', extent: '75 個儀節', note: '以器具觸碰木乃伊或神像之口，使其能食、能言、能見。同一套儀式也用於「啟用」神廟中的新神像。', seealso: ['mis-pi'] },
            { slug: 'embalming-ritual', title_zh: '防腐儀式', title_orig: 'Embalming Ritual', siglum: 'P. Boulaq 3 + P. Louvre 5158', era: '羅馬時代抄本', language: EG, status: 'fragment', note: '製作木乃伊每一步驟所配的誦詞——技術手冊與禮儀文本合一。' },
          ],
        },
      ],
    },
    {
      key: 'netherworld',
      sigil: '埃三',
      name: '冥界之書',
      name_en: 'Books of the Netherworld',
      era: '約前 1500 – 前 1070（新王國）',
      summary:
        '新王國王陵牆上的「宇宙論圖文」：太陽神每夜乘舟穿越冥界十二時辰，與混沌巨蛇阿波菲斯搏鬥，黎明時重生。'
        + '國王死後加入這趟航程。與亡靈書不同，這些書起初只供王陵使用，圖與文缺一不可。',
      divisions: [
        {
          key: 'night',
          label: '夜之諸書',
          label_en: 'Books of the Night Journey',
          texts: [
            { slug: 'amduat', title_zh: '冥界之書（阿姆杜阿特）', title_orig: 'Imy-dwꜣt (Amduat), "That Which Is in the Netherworld"', era: '約前 1500（圖特摩斯一世至三世）', language: EG, provenance: '帝王谷，圖特摩斯三世陵（KV 34）為最早的完整本', status: 'inscription', extent: '十二時辰', note: '現存最早的冥界之書，以夜間十二時辰分段。' },
            { slug: 'book-of-gates', title_zh: '門之書', title_orig: 'Book of Gates', era: '約前 1320（霍連赫布起）', language: EG, provenance: '帝王谷；塞提一世石棺（倫敦索恩博物館）', status: 'inscription', extent: '十二門', note: '每一時辰以一道有蛇守護的門分隔；第五時辰後有奧西里斯的審判廳。' },
            { slug: 'book-of-caverns', title_zh: '洞窟之書', title_orig: 'Book of Caverns', era: '第十九王朝', language: EG, provenance: '阿拜多斯奧西里昂；拉美西斯六世陵（KV 9）', status: 'inscription', note: '把冥界分為六段洞窟，著重描寫惡者在火坑中的刑罰——現存最早的「地獄」圖像之一。' },
            { slug: 'book-of-earth', title_zh: '大地之書', title_orig: 'Book of the Earth (Book of Aker)', era: '第二十王朝', language: EG, provenance: '拉美西斯六世陵（KV 9）等', status: 'inscription', note: '太陽穿越大地之神阿克爾的身體，在深處與奧西里斯的屍身結合而重生。' },
            { slug: 'litany-of-re', title_zh: '拉神連禱', title_orig: 'Litany of Re', era: '約前 1450 起', language: EG, provenance: '帝王谷諸王陵入口', status: 'inscription', extent: '75 個稱號', note: '呼求太陽神七十五種化身之名，國王藉此與拉合一。' },
          ],
        },
        {
          key: 'sky',
          label: '天之諸書',
          label_en: 'Books of the Sky',
          texts: [
            { slug: 'book-of-nut', title_zh: '努特之書', title_orig: 'Book of Nut (Fundamentals of the Course of the Stars)', era: '新王國（塞提一世衣冠塚始見），羅馬時代有世俗體註釋本', language: `${EG}；${DEM}（註釋）`, provenance: '阿拜多斯奧西里昂；塞提一世陵', status: 'inscription', note: '天空女神努特拱身於大地之上，太陽夜入其口、晨出其胎。兼是天文書——羅馬時代的世俗體註釋本逐句解說了它。' },
            { slug: 'book-of-day-night', title_zh: '晝之書與夜之書', title_orig: 'Book of the Day / Book of the Night', era: '第二十王朝', language: EG, provenance: '拉美西斯六世陵天花板', status: 'inscription', note: '畫在王陵天花板上的兩幅努特：一日一夜，太陽的完整循環。' },
            { slug: 'heavenly-cow', title_zh: '天牛之書（毀滅人類）', title_orig: 'Book of the Heavenly Cow', era: '新王國（最早見於圖坦卡門的金龕）', language: LATE, provenance: '圖坦卡門金龕；塞提一世、拉美西斯二世、三世陵', status: 'inscription', note: '人類謀反年老的拉，拉遣其眼（化為哈索爾—塞赫美特）屠殺人類，又以染紅的啤酒灌醉她才止住。之後拉乘天牛升天，神人分離。', bible: '創 6–9 洪水敘事的「神悔造人、毀而不盡」母題' },
          ],
        },
      ],
    },
    {
      key: 'theology',
      sigil: '埃四',
      name: '神學與創世',
      name_en: 'Theology and Creation',
      era: '約前 2000 – 公元 2 世紀',
      summary:
        '埃及沒有一套統一的創世論，而是幾座大城各有一套，彼此並存：赫利奧波利斯的阿圖姆自生九神、'
        + '孟斐斯的卜塔以心思口言造物、赫爾莫波利斯的八元神出於原水、底比斯的阿蒙隱而獨一。'
        + '本卷並置，不調和。另收奧西里斯神話的主要傳本，以及古代書目所載而已佚失的「托特之書」。',
      divisions: [
        {
          key: 'cosmogony',
          label: '各城創世論',
          label_en: 'Cosmogonies',
          texts: [
            { slug: 'shabaka-stone', title_zh: '孟斐斯神學（沙巴卡石）', title_orig: 'Memphite Theology (Shabaka Stone)', siglum: 'BM EA 498', era: '刻於約前 710（第二十五王朝沙巴卡王）；自稱抄自蟲蛀的古卷，實際成書年代爭議極大', language: EG, provenance: '孟斐斯；大英博物館藏', status: 'inscription', note: '卜塔以「心」構思、以「舌」說出而萬物生成——「以言創世」最早的明文。石板後來被當磨盤用，中段磨毀。', bible: '創 1「神說」；約 1:1「太初有道」' },
            { slug: 'bremner-rhind-creation', title_zh: '知曉拉之生成與擊倒阿波菲斯之書', title_orig: 'Book of Knowing the Creations of Re and of Overthrowing Apophis', siglum: 'BM EA 10188（布雷姆納—林德紙草）', era: '抄於約前 310（托勒密初）', language: EG, provenance: '底比斯；大英博物館藏', status: 'whole', note: '「我是那生成者……」造物主自述從獨一生出萬有。同卷另抄〈伊西斯與奈芙蒂斯哀歌〉。', seealso: ['ct-shu', 'lamentations-isis'] },
            { slug: 'hermopolis-ogdoad', title_zh: '赫爾莫波利斯八元神之說', title_orig: 'Ogdoad of Hermopolis', era: '中王國以前的觀念；主要見於托勒密時代神廟銘文', language: EG, provenance: '散見於棺槨文、底比斯梅迪內特哈布小神廟、艾德福神廟', status: 'fragment', via: '無單一文本，綴輯自各處神廟銘文', note: '四對男女神（原水、無限、黑暗、隱藏）在原初之丘上生出太陽。沒有一部書完整講述它——它是學者拼出來的。' },
            { slug: 'leiden-amun', title_zh: '萊頓阿蒙頌', title_orig: 'Leiden Hymn to Amun', siglum: 'P. Leiden I 350', era: '約前 1238（拉美西斯二世第 52 年）', language: LATE, provenance: '萊頓國立古物博物館', status: 'composite', extent: '原分「一章」至「千章」編號', note: '新王國神學的高峰：「眾神是三：阿蒙、拉、卜塔……他的名是阿蒙（隱者），他的臉是拉，他的身是卜塔。」一神隱於多神之中。' },
            { slug: 'edfu-building-texts', title_zh: '艾德福神廟建廟銘文', title_orig: 'Edfu Building Texts', era: '前 237 – 前 57（托勒密三世至十二世）', language: EG, provenance: '艾德福荷魯斯神廟外牆', status: 'inscription', note: '神廟自述其原初由眾神在混沌之水中建起——每一座神廟都是創世之丘的重現。' },
            { slug: 'esna-creation', title_zh: '艾斯納神廟創世頌', title_orig: 'Esna cosmogony hymns (Khnum and Neith)', era: '羅馬時代（1–3 世紀）', language: EG, provenance: '艾斯納克努姆神廟', status: 'inscription', note: '陶匠神克努姆在轉輪上塑造萬族之人；女神奈特從原水中說出三十個神名而造世界。最晚的大型埃及創世文本之一。' },
          ],
        },
        {
          key: 'osiris',
          label: '奧西里斯神話',
          label_en: 'The Osiris Myth',
          desc: '埃及文獻從未完整講述奧西里斯被弒、肢解、伊西斯尋屍重組、荷魯斯復仇的故事——那是禁忌。完整敘事要到普魯塔克的希臘文本才有，見附錄。',
          texts: [
            { slug: 'great-hymn-osiris', title_zh: '奧西里斯大頌（阿蒙摩斯碑）', title_orig: 'Great Hymn to Osiris', siglum: 'Louvre C 286', era: '第十八王朝', language: EG, provenance: '羅浮宮藏', status: 'inscription', note: '埃及本土對奧西里斯神話最連貫的一段敘述：伊西斯以翼搧風使亡夫復甦而受孕。', seealso: ['plutarch-isis'] },
            { slug: 'horus-seth', title_zh: '荷魯斯與塞特之爭', title_orig: 'The Contendings of Horus and Seth', siglum: 'P. Chester Beatty I', era: '約前 1150（拉美西斯五世）', language: LATE, provenance: '底比斯德爾麥地那；都柏林切斯特‧比替圖書館藏', status: 'whole', note: '眾神法庭為奧西里斯的王位纏訟八十年。粗俗、滑稽、性與暴力俱全——神話不必莊嚴。' },
            { slug: 'lamentations-isis', title_zh: '伊西斯與奈芙蒂斯哀歌', title_orig: 'Lamentations of Isis and Nephthys', siglum: 'P. Berlin 3008；BM EA 10188', era: '托勒密時代抄本', language: EG, status: 'whole', note: '奧西里斯節由兩名扮作女神的女子對唱的哀歌，呼喚亡神歸來。', seealso: ['khoiak-mysteries'] },
            { slug: 'khoiak-mysteries', title_zh: '科亞克月奧西里斯祕儀', title_orig: 'Osiris Mysteries of Khoiak (Dendera)', era: '托勒密晚期至羅馬初期', language: EG, provenance: '丹德拉哈索爾神廟屋頂奧西里斯祠', status: 'inscription', note: '每年科亞克月以泥與穀種塑奧西里斯像，令其發芽——穀物復活與神的復活合一的節慶儀程。' },
          ],
        },
        {
          key: 'lost-books',
          label: '佚書',
          label_en: 'Lost Books',
          texts: [
            { slug: 'books-of-thoth', title_zh: '托特四十二書', title_orig: 'The 42 Books of Hermes (Thoth)', era: '晚期埃及神廟藏書', language: EG, status: 'lost-listed', via: '亞歷山卓的克萊門《雜記》六‧4.35–37', note: '克萊門目睹埃及祭司遊行時所捧的神廟聖書：讚歌二、王者規範二、天文四、書吏之學十、獻祭十、祭司律十、醫書六。全部亡佚；書目只保存在一位基督教作家筆下。', xref: ['希臘羅馬大藏經 Υ 啟示書‧赫爾墨斯文集'] },
            { slug: 'house-of-life', title_zh: '生命之屋藏書目錄（艾德福圖書室）', title_orig: 'Library catalogue of the Edfu temple', era: '托勒密時代', language: EG, provenance: '艾德福荷魯斯神廟圖書室牆面', status: 'lost-listed', via: '艾德福神廟圖書室壁上書目', note: '神廟圖書室把藏書名刻在牆上：《擊退惡者之書》《保護城市之書》《知曉神廟祕密之書》……書名都在，書一本也沒留下。' },
          ],
        },
      ],
    },
    {
      key: 'hymns',
      sigil: '埃五',
      name: '頌詩與禱文',
      name_en: 'Hymns and Prayers',
      era: '約前 1900 – 公元 3 世紀',
      summary:
        '從國家神廟的大頌到工匠村民刻在小碑上的懺悔禱文。新王國中期出現「個人虔敬」：凡人直接向神求赦、'
        + '自承有罪、讚美神「聽窮人的呼求」——語氣與詩篇極近。',
      divisions: [
        {
          key: 'state',
          label: '國家神祇頌',
          label_en: 'Hymns of the State Cults',
          texts: [
            { slug: 'hymn-nile', title_zh: '尼羅河頌', title_orig: 'Hymn to Hapy (the Inundation)', era: '中王國成書；新王國抄本', language: EG, status: 'composite', note: '讚美氾濫之神哈皮帶來豐年——學校抄寫範文，抄本錯字極多。' },
            { slug: 'cairo-amun', title_zh: '開羅阿蒙—拉頌', title_orig: 'Cairo Hymn to Amun-Re', siglum: 'P. Boulaq 17', era: '第十八王朝初抄本，部分成書更早', language: EG, provenance: '開羅埃及博物館藏', status: 'whole', note: '阿蒙作為萬物之主、眷顧畜類與人類的創造者，為阿頓大頌的先聲。' },
            { slug: 'great-hymn-aten', title_zh: '阿頓大頌', title_orig: 'Great Hymn to the Aten', era: '約前 1340（埃赫那頓在位）', language: LATE, provenance: '阿瑪納，阿伊墓', status: 'inscription', note: '埃赫那頓宗教改革的核心文本：日輪阿頓是唯一的神，造萬國萬族、各賦語言膚色。', bible: '詩 104（逐段平行）', xref: ['基督教大藏經‧前藏'] },
            { slug: 'hymn-ptah', title_zh: '卜塔頌', title_orig: 'Hymn to Ptah', siglum: 'P. Berlin 3048', era: '第二十二王朝抄本', language: LATE, status: 'composite', note: '與孟斐斯神學同一系統：卜塔以心與舌造神造人。', seealso: ['shabaka-stone'] },
            { slug: 'isis-hymns-philae', title_zh: '菲萊伊西斯頌', title_orig: 'Hymns to Isis in the temple of Philae', era: '托勒密至羅馬時代', language: EG, provenance: '菲萊伊西斯神廟', status: 'inscription', note: '伊西斯作為萬名之女神、天之主、王者之母。希臘文伊西斯自述文的埃及本土對應物。', xref: ['希臘羅馬大藏經 Λ 祕儀書‧伊西斯自述文（希臘文）'] },
          ],
        },
        {
          key: 'personal',
          label: '個人虔敬',
          label_en: 'Personal Piety',
          texts: [
            { slug: 'neferabu-stelae', title_zh: '涅斐拉布懺悔碑', title_orig: 'Stelae of Neferabu', siglum: 'BM EA 589；Turin 50058', era: '約前 1250（第十九王朝）', language: LATE, provenance: '德爾麥地那工匠村', status: 'inscription', note: '工匠自述因發假誓而被神罰失明，求月神與山峰女神麥瑞塞格赦免——凡人第一人稱的悔罪與得赦見證。' },
            { slug: 'deir-medina-prayers', title_zh: '德爾麥地那還願碑群', title_orig: 'Votive stelae from Deir el-Medina', era: '第十九至二十王朝', language: LATE, provenance: '德爾麥地那', status: 'inscription', note: '「阿蒙是聽窮人呼求的，祂來救那受欺壓的」——平民對神的直接訴求。', bible: '詩 34:6；詩 72:12' },
            { slug: 'prayers-anastasi', title_zh: '書吏禱文（阿納斯塔西紙草）', title_orig: 'Prayers in Papyrus Anastasi II and IV', siglum: 'P. Anastasi II, IV（BM EA 10243, 10249）', era: '第十九王朝', language: LATE, provenance: '大英博物館藏', status: 'whole', note: '書吏學校抄本中夾的個人禱詞：「阿蒙啊，求你垂聽孤獨的人……」' },
          ],
        },
      ],
    },
    {
      key: 'wisdom',
      sigil: '埃六',
      name: '智慧書',
      name_en: 'Instructions (Sebayt)',
      era: '約前 2000 – 公元 1 世紀',
      summary:
        '埃及人稱為 sebayt（教誨），多託名古代賢臣或國王教子。書吏學校世代抄寫背誦，'
        + '核心理念是瑪特——真理、正義與宇宙秩序合一的一個詞。《阿蒙尼摩普訓言》與箴言書的逐段平行是聖經學最穩固的比較個案之一。',
      divisions: [
        {
          key: 'classical',
          label: '古典訓言',
          label_en: 'Classical Instructions',
          texts: [
            { slug: 'ptahhotep', title_zh: '卜塔霍特普訓言', title_orig: 'Instruction of Ptahhotep', siglum: 'P. Prisse（BnF）', era: '託名第五王朝宰相；實際成書約中王國', language: EG, provenance: '巴黎法國國家圖書館藏', status: 'whole', extent: '37 條箴言', note: '「善言比綠寶石更隱密，卻見於磨穀的婢女之中。」現存最完整的古埃及智慧書。' },
            { slug: 'kagemni', title_zh: '卡格姆尼訓言', title_orig: 'Instruction for Kagemni', siglum: 'P. Prisse（卷首）', era: '中王國', language: EG, status: 'fragment', note: '只存結尾一段，談節制與謙卑。' },
            { slug: 'hardjedef', title_zh: '哈傑德夫訓言', title_orig: 'Instruction of Hardjedef', era: '託名第四王朝王子；中王國成書', language: EG, status: 'fragment', note: '現存託名最早的訓言，只存開頭。' },
            { slug: 'merikare', title_zh: '梅里卡拉王訓言', title_orig: 'Instruction for Merikare', siglum: 'P. Hermitage 1116A', era: '託名第一中間期；中王國成書', language: EG, provenance: '聖彼得堡艾米塔吉博物館藏', status: 'composite', note: '老王教子為君，結尾一段頌讚造物主為人造天地、為人而設光與食物——「人是神的牲畜，神為他們造了天地」。' },
            { slug: 'amenemhat', title_zh: '阿蒙尼姆赫特一世訓言', title_orig: 'Instruction of Amenemhat I', era: '第十二王朝初', language: EG, status: 'composite', note: '遇刺身亡的國王從死後對兒子說話：不要相信任何人。' },
            { slug: 'loyalist', title_zh: '忠君訓言', title_orig: 'Loyalist Instruction', era: '第十二王朝', language: EG, status: 'composite', note: '王是滋養萬民的神；忠君即虔敬。' },
            { slug: 'ani', title_zh: '阿尼訓言', title_orig: 'Instruction of Ani', siglum: 'P. Boulaq 4', era: '第十八王朝', language: LATE, provenance: '開羅埃及博物館藏', status: 'composite', note: '平民書吏教子：論神廟中禱告當靜默、論孝敬母親。結尾兒子反駁父親「教誨太難」——智慧文學內部的對話。' },
            { slug: 'amenemope', title_zh: '阿蒙尼摩普訓言', title_orig: 'Instruction of Amenemope', siglum: 'BM EA 10474', era: '約前 1100（拉美西斯時代）', language: LATE, provenance: '大英博物館藏', status: 'whole', extent: '三十章', note: '三十章體與箴言書「三十條」逐段平行，是聖經直接借用外邦文本最無爭議的案例。', bible: '箴 22:17–24:22' },
          ],
        },
        {
          key: 'demotic-wisdom',
          label: '世俗體智慧書',
          label_en: 'Demotic Instructions',
          texts: [
            { slug: 'ankhsheshonq', title_zh: '安赫謝順克訓言', title_orig: 'Instruction of Ankhsheshonq', siglum: 'BM EA 10508', era: '前 1 世紀抄本（成書約前 4–3 世紀）', language: DEM, provenance: '大英博物館藏', status: 'composite', note: '祭司因牽連謀逆下獄，在陶片上寫格言給兒子。單句格言體，近於傳道書。', bible: '傳 11:1（「將你的糧食撒在水面」有近似句）' },
            { slug: 'papyrus-insinger', title_zh: '大世俗體智慧書（因辛格紙草）', title_orig: 'Papyrus Insinger', siglum: 'P. Insinger（萊頓）', era: '1 世紀抄本（成書約托勒密時代）', language: DEM, provenance: '萊頓國立古物博物館藏', status: 'composite', extent: '25 章', note: '每章以「命運與運氣由神所定」作結——晚期埃及最系統的倫理著作。' },
          ],
        },
      ],
    },
    {
      key: 'laments',
      sigil: '埃七',
      name: '哀歌、辯論與預言',
      name_en: 'Laments, Dialogues and Prophecies',
      era: '約前 1900 – 前 1 世紀',
      summary:
        '中王國書吏寫下的「悲觀文學」：天下大亂、正義不行、神是否還在看。'
        + '同一批作品裡有古代最早的自殺辯論、最早的「神在哪裡」質問，以及「預言」一位救世之王的到來。',
      divisions: [
        {
          key: 'pessimism',
          label: '悲觀文學',
          label_en: 'Pessimistic Literature',
          texts: [
            { slug: 'dispute-ba', title_zh: '厭世者與其魂之對話', title_orig: 'Dispute between a Man and His Ba', siglum: 'P. Berlin 3024', era: '第十二王朝', language: EG, provenance: '柏林埃及博物館藏', status: 'fragment', note: '一個想死的人與他的魂（ba）爭辯死亡是否值得。「死亡今日在我面前，如病人痊癒……」開頭殘缺。', bible: '可與約伯記、傳道書對讀' },
            { slug: 'ipuwer', title_zh: '伊普味陳辭', title_orig: 'Admonitions of Ipuwer', siglum: 'P. Leiden I 344', era: '中王國成書（爭議）；第十九王朝抄本', language: EG, provenance: '萊頓國立古物博物館藏', status: 'fragment', note: '「河成了血」「窮人成了富人」——描寫社會倒轉的長篇哀辭，並質問造物主為何坐視。', bible: '出 7:20（常被拿來比附出埃及災禍，學界不支持直接關聯）' },
            { slug: 'khakheperreseneb', title_zh: '卡赫佩拉塞內布的怨訴', title_orig: 'Complaints of Khakheperreseneb', siglum: 'BM EA 5645', era: '第十二王朝', language: EG, provenance: '大英博物館藏（木板）', status: 'fragment', note: '書吏苦於「找不到前人沒說過的話」——古代最早的文學焦慮。' },
            { slug: 'eloquent-peasant', title_zh: '能言農夫', title_orig: 'The Eloquent Peasant', siglum: 'P. Berlin 3023 + 3025', era: '第十二王朝', language: EG, provenance: '柏林埃及博物館藏', status: 'composite', note: '受欺的農夫九次陳情，論瑪特與司法公義。故事框架是國王故意不判，只為多聽他說。' },
            { slug: 'harpers-song', title_zh: '豎琴師之歌（因提夫王墓）', title_orig: 'Song from the Tomb of King Intef', siglum: 'P. Harris 500（BM EA 10060）', era: '中王國成書；新王國抄本', language: EG, status: 'whole', note: '「沒有人從那裡回來告訴我們他們如何……且隨你的心，歡度佳日。」質疑來世的及時行樂之歌。', bible: '傳 9:7–10' },
          ],
        },
        {
          key: 'prophecy',
          label: '預言',
          label_en: 'Prophecies',
          texts: [
            { slug: 'neferti', title_zh: '涅斐提預言', title_orig: 'Prophecy of Neferti', siglum: 'P. Hermitage 1116B', era: '第十二王朝初（事後預言）', language: EG, provenance: '艾米塔吉博物館藏', status: 'composite', note: '假託古王時代的祭司預言天下大亂後「一位南方來的王，名叫阿美尼」將重建瑪特——實為替阿蒙尼姆赫特一世背書。' },
            { slug: 'oracle-potter', title_zh: '陶匠神諭', title_orig: 'Oracle of the Potter', era: '前 2 世紀', language: '古希臘文（自稱譯自埃及文）', status: 'fragment', via: '三份希臘文紙草', note: '預言希臘人的城亞歷山卓將荒廢、埃及本土之王將復歸。反托勒密統治的埃及祭司末世論。' },
            { slug: 'demotic-chronicle', title_zh: '世俗體編年', title_orig: 'Demotic Chronicle', siglum: 'P. BnF 215', era: '前 3 世紀', language: DEM, provenance: '巴黎法國國家圖書館藏', status: 'composite', note: '以註釋隱晦神諭的方式評判歷代諸王：遵行律法者國祚長，背棄者短。' },
            { slug: 'lamb-bocchoris', title_zh: '博克霍利斯時代的羔羊', title_orig: 'The Lamb of Bocchoris', era: '羅馬時代抄本（4/5 年）', language: DEM, provenance: '維也納', status: 'fragment', note: '一隻羔羊開口預言埃及將受九百年災禍。' },
          ],
        },
      ],
    },
    {
      key: 'tales',
      sigil: '埃八',
      name: '神話與故事',
      name_en: 'Myths and Tales',
      era: '約前 1900 – 公元 2 世紀',
      summary: '書吏娛樂與教化用的敘事。神祇、魔法師與冥界在其中自由出入——不少故事是後世民間故事的祖型。',
      divisions: [
        {
          key: 'mk-nk',
          label: '中王國與新王國',
          label_en: 'Middle and New Kingdom',
          texts: [
            { slug: 'sinuhe', title_zh: '辛奴亥的故事', title_orig: 'The Story of Sinuhe', siglum: 'P. Berlin 3022 等', era: '第十二王朝', language: EG, provenance: '柏林埃及博物館藏', status: 'composite', note: '逃亡迦南的朝臣晚年返鄉求葬於埃及——「不葬於故土」是埃及人最深的恐懼。' },
            { slug: 'shipwrecked-sailor', title_zh: '船難水手', title_orig: 'The Shipwrecked Sailor', siglum: 'P. Hermitage 1115', era: '第十二王朝', language: EG, provenance: '艾米塔吉博物館藏', status: 'whole', note: '海島上的巨蛇神自述其族被天火燒盡，獨存一身——故事套故事。' },
            { slug: 'westcar', title_zh: '胡夫王與魔法師（韋斯特卡紙草）', title_orig: 'Papyrus Westcar', siglum: 'P. Berlin 3033', era: '第二中間期抄本', language: EG, provenance: '柏林埃及博物館藏', status: 'fragment', note: '魔法師分水取物、斷首復接；結尾預言拉神與祭司之妻所生三子將為第五王朝之王。', bible: '出 14 分海；王下 6:6 斧頭浮起' },
            { slug: 'two-brothers', title_zh: '兩兄弟的故事', title_orig: 'Tale of Two Brothers', siglum: 'P. D\'Orbiney（BM EA 10183）', era: '約前 1215（第十九王朝）', language: LATE, provenance: '大英博物館藏', status: 'whole', note: '兄嫂誘弟不成反誣——與約瑟和波提乏之妻的情節相同；後半段弟弟化為公牛與樹而重生。', bible: '創 39' },
            { slug: 'astarte-papyrus', title_zh: '阿斯塔特與海', title_orig: 'Astarte and the Insatiable Sea (Astarte Papyrus)', siglum: 'P. Amherst 9 + Pierpont Morgan', era: '第十八王朝（阿蒙霍特普二世）', language: LATE, status: 'fragment', note: '埃及文寫的迦南神話：海向眾神索貢，女神阿斯塔特被送去。與烏加里特的巴力戰雅姆同源。', seealso: ['baal-yamm'] },
            { slug: 'truth-falsehood', title_zh: '真理與虛偽', title_orig: 'The Blinding of Truth by Falsehood', siglum: 'P. Chester Beatty II', era: '第十九王朝', language: LATE, status: 'fragment', note: '擬人化的寓言：虛偽弄瞎了兄弟真理，真理之子為父復仇。' },
          ],
        },
        {
          key: 'demotic-tales',
          label: '世俗體故事',
          label_en: 'Demotic Tales',
          texts: [
            { slug: 'setne-1', title_zh: '塞特納與托特之書', title_orig: 'Setne Khamwas I', siglum: 'P. Cairo CG 30646', era: '托勒密時代', language: DEM, provenance: '開羅埃及博物館藏', status: 'composite', note: '拉美西斯二世之子塞特納盜取墓中的「托特之書」，遭亡者以幻術懲罰。', seealso: ['books-of-thoth'] },
            { slug: 'setne-2', title_zh: '塞特納與其子遊冥界', title_orig: 'Setne Khamwas II', siglum: 'BM EA 10822', era: '羅馬時代（1 世紀）', language: DEM, provenance: '大英博物館藏', status: 'fragment', note: '神童引父親參觀冥界：生前榮華的富人受苦，窮人卻穿上富人的壽衣坐在奧西里斯身旁。', bible: '路 16:19–31 財主與拉撒路' },
            { slug: 'myth-sun-eye', title_zh: '太陽之眼神話', title_orig: 'Myth of the Sun\'s Eye', siglum: 'P. Leiden I 384', era: '羅馬時代（2 世紀）', language: DEM, provenance: '萊頓國立古物博物館藏', status: 'composite', note: '離家出走到努比亞的太陽之眼（母獅女神）被托特化身的猴子以寓言勸回。另有希臘文譯本。' },
            { slug: 'petubastis', title_zh: '佩圖巴斯提斯故事群', title_orig: 'Inaros–Petubastis Cycle', era: '托勒密至羅馬時代', language: DEM, status: 'fragment', note: '晚期埃及的英雄史詩群，爭奪阿蒙神的鎧甲與聖舟。' },
          ],
        },
      ],
    },
    {
      key: 'ritual',
      sigil: '埃九',
      name: '神廟儀式、節期與魔法',
      name_en: 'Temple Ritual, Festivals and Magic',
      era: '約前 1900 – 公元 4 世紀',
      summary:
        '神廟每日為神像更衣奉食的儀式、節期曆、吉凶日、解夢書，以及護身與詛咒的魔法文書。'
        + '埃及人沒有把「宗教」與「魔法」分開——同一個詞 heka 既是神力也是咒術。',
      divisions: [
        {
          key: 'temple',
          label: '神廟儀式與節期',
          label_en: 'Temple Ritual and Festivals',
          texts: [
            { slug: 'daily-ritual', title_zh: '每日神廟儀式（阿蒙每日祭儀）', title_orig: 'Daily Temple Ritual of Amun', siglum: 'P. Berlin 3055', era: '第二十二王朝抄本', language: LATE, provenance: '柏林埃及博物館藏', status: 'whole', extent: '66 個儀節', note: '祭司每日黎明開啟神龕、焚香、為神像洗浴更衣奉食的逐節誦詞。', seealso: ['abydos-seti-ritual'] },
            { slug: 'abydos-seti-ritual', title_zh: '阿拜多斯塞提一世神廟儀式壁', title_orig: 'Ritual scenes of the temple of Seti I at Abydos', era: '約前 1290', language: LATE, provenance: '阿拜多斯', status: 'inscription', note: '七座神龕的牆上逐格刻出每日儀式的每一步——圖文並存的儀式手冊。' },
            { slug: 'cairo-calendar', title_zh: '吉日凶日曆', title_orig: 'Calendar of Lucky and Unlucky Days', siglum: 'P. Cairo JE 86637', era: '第十九王朝', language: LATE, provenance: '開羅埃及博物館藏', status: 'whole', note: '一年每一天標吉、凶或半吉半凶，並附當日神話事件與禁忌。' },
            { slug: 'opet-festival', title_zh: '奧佩特節', title_orig: 'Opet Festival reliefs', era: '第十八王朝（圖坦卡門浮雕）', language: LATE, provenance: '盧克索神廟柱廊', status: 'inscription', note: '阿蒙聖舟自卡納克出巡至盧克索，與王的神聖本質重新結合。' },
            { slug: 'sed-festival', title_zh: '塞德節（王位更新祭）', title_orig: 'Heb-Sed (Jubilee) reliefs', era: '古王國至托勒密', language: EG, provenance: '索列布、布巴斯提斯諸神廟', status: 'inscription', note: '王在位三十年舉行，跑繞場地以證其力，象徵王權重生。' },
          ],
        },
        {
          key: 'magic',
          label: '魔法與占驗',
          label_en: 'Magic and Divination',
          texts: [
            { slug: 'execration-texts', title_zh: '詛咒敵人文書', title_orig: 'Execration Texts', era: '中王國', language: EG, provenance: '薩卡拉、米爾吉薩等', status: 'fragment', note: '在陶碗或俘虜小像上寫下敵國與敵人之名，然後打碎掩埋。最早提到「耶路撒冷」（Rušalimum）的文獻之一。' },
            { slug: 'dream-book', title_zh: '解夢書', title_orig: 'Dream Book', siglum: 'P. Chester Beatty III（BM EA 10683）', era: '約前 1275', language: LATE, provenance: '大英博物館藏', status: 'fragment', note: '「若人夢見自己……好，意為……」逐條解夢，分吉凶。', bible: '創 40–41 約瑟解夢' },
            { slug: 'brooklyn-snake', title_zh: '布魯克林蛇咒紙草', title_orig: 'Brooklyn Papyrus (snakebite treatise)', siglum: 'Brooklyn 47.218.48 + 85', era: '第三十王朝', language: LATE, provenance: '布魯克林博物館藏', status: 'fragment', note: '分辨各種毒蛇並配以治療與咒語——醫學與宗教在同一卷裡。' },
            { slug: 'metternich-stela', title_zh: '梅特涅碑（荷魯斯護身碑）', title_orig: 'Metternich Stela', siglum: 'MMA 50.85', era: '約前 360（內克塔內布二世）', language: EG, provenance: '紐約大都會藝術博物館藏', status: 'inscription', note: '童子荷魯斯腳踏鱷魚、手握毒蛇；碑上刻伊西斯藏子於沼澤、幼子被蠍螫的神話。人們澆水於碑上而飲以治毒。' },
            { slug: 'london-leiden-magical', title_zh: '倫敦—萊頓世俗體魔法紙草', title_orig: 'London–Leiden Demotic Magical Papyrus', siglum: 'BM EA 10070 + P. Leiden I 383', era: '3 世紀', language: `${DEM}（夾希臘文與古科普特文註音）`, status: 'whole', note: '燈占、碗占、召神見面之術。與希臘魔法紙草同出於底比斯一批窖藏。', xref: ['希臘羅馬大藏經 Υ 啟示書‧希臘魔法紙草（PGM）'] },
          ],
        },
      ],
    },
    {
      key: 'royal',
      sigil: '埃十',
      name: '王室與神廟銘文',
      name_en: 'Royal and Temple Inscriptions',
      era: '約前 2400 – 公元 452',
      summary:
        '王是神在地上的兒子，王的碑文因此是神學文本：神授王權的神誕故事、神親自救駕的戰爭詩、'
        + '宗教改革的界碑，直到最後一位會寫聖書體的祭司在菲萊島刻下的塗鴉。',
      divisions: [
        {
          key: 'kingship',
          label: '神授王權',
          label_en: 'Divine Kingship',
          texts: [
            { slug: 'divine-birth', title_zh: '哈特謝普蘇特神誕銘', title_orig: 'Divine Birth reliefs of Hatshepsut', era: '約前 1470', language: EG, provenance: '德爾巴哈里女王祭廟', status: 'inscription', note: '阿蒙化身為國王去見王后，使其受孕，克努姆在轉輪上塑出王的身體。後世王室神誕敘事的範本。' },
            { slug: 'dream-stela', title_zh: '夢之碑', title_orig: 'Dream Stela of Thutmose IV', era: '約前 1400', language: EG, provenance: '吉薩大獅身人面像兩爪之間', status: 'inscription', note: '王子在獅身人面像陰影下午睡，神託夢：清除我身上的沙，我便使你為王。' },
            { slug: 'kadesh-poem', title_zh: '卡迭石戰役之詩', title_orig: 'Poem of the Battle of Qadesh', era: '約前 1274', language: LATE, provenance: '卡納克、盧克索、阿拜多斯、拉美西姆、阿布辛貝；另有紙草本', status: 'inscription', note: '拉美西斯二世被敵軍圍困，向阿蒙呼求：「我的父阿蒙啊，父會忘記他的兒子嗎？」神應聲而至。' },
            { slug: 'famine-stela', title_zh: '饑荒碑', title_orig: 'Famine Stela', era: '刻於托勒密時代，託名第三王朝左塞爾王', language: EG, provenance: '塞赫勒島', status: 'inscription', note: '七年饑荒，王夢見克努姆許諾氾濫重臨。託古以爭神廟產權。', bible: '創 41 七個荒年' },
          ],
        },
        {
          key: 'amarna',
          label: '阿瑪納改革',
          label_en: 'The Amarna Reform',
          texts: [
            { slug: 'boundary-stelae', title_zh: '埃赫那頓界碑', title_orig: 'Boundary Stelae of Akhetaten', era: '約前 1346–1341', language: LATE, provenance: '阿瑪納周邊崖壁，現存十六座', status: 'inscription', note: '王宣告阿頓親自指示新都的地點，誓言永不越界。', seealso: ['great-hymn-aten'] },
            { slug: 'restoration-stela', title_zh: '圖坦卡門復興碑', title_orig: 'Restoration Stela of Tutankhamun', siglum: 'CG 34183', era: '約前 1330', language: LATE, provenance: '卡納克；開羅埃及博物館藏', status: 'inscription', note: '宣告阿瑪納時代諸神離棄埃及、禱告無應，如今重修神廟、復歸舊神。改革失敗的官方定論。' },
          ],
        },
        {
          key: 'last',
          label: '最後的銘文',
          label_en: 'The Last Inscriptions',
          desc: '埃及宗教的終點不是一道詔令，而是一個書寫系統的死亡。最後會寫聖書體的祭司在菲萊島刻下他的名字。',
          texts: [
            { slug: 'philae-last-hieroglyph', title_zh: '埃斯梅特—阿霍姆塗鴉', title_orig: 'Graffito of Esmet-Akhom', siglum: 'Philae 436', era: '公元 394 年 8 月 24 日', language: `${EG}；${DEM}`, provenance: '菲萊島伊西斯神廟哈德良門', status: 'inscription', note: '現存最後一則有紀年的聖書體銘文，刻在一幅曼都利斯神像旁：「直到永遠」。' },
            { slug: 'philae-last-demotic', title_zh: '菲萊最後的世俗體塗鴉', title_orig: 'Last dated Demotic graffito at Philae', era: '公元 452 年', language: DEM, provenance: '菲萊島伊西斯神廟', status: 'inscription', note: '已知最後一則有紀年的世俗體文字。此後埃及語只以科普特文（希臘字母）書寫，載的是基督教。' },
          ],
        },
      ],
    },
    {
      key: 'kush',
      sigil: '埃十一',
      name: '庫施卷',
      name_en: 'Kush (Nubia)',
      era: '約前 750 – 公元 4 世紀',
      summary:
        '尼羅河上游的庫施王國先以埃及文書寫，自居為阿蒙信仰的正統守護者，甚至征服埃及成為第二十五王朝；'
        + '後期改用自創的麥羅埃文，供奉獅首神阿佩德馬克。麥羅埃文的字母已能讀音，**語言至今無法理解**——'
        + '這一卷的原文欄因此有一部分是真正的空白。',
      divisions: [
        {
          key: 'napata',
          label: '納帕塔時期（埃及文）',
          label_en: 'Napatan Period',
          texts: [
            { slug: 'piye-stela', title_zh: '皮耶凱旋碑', title_orig: 'Victory Stela of Piye', siglum: 'JE 48862', era: '約前 728', language: EG, provenance: '博爾戈爾山阿蒙神廟；開羅埃及博物館藏', status: 'inscription', note: '庫施王征服埃及，卻拒見未行潔淨禮、吃魚的北方諸侯——以宗教純潔為征服的正當理由。' },
            { slug: 'aspelta-election', title_zh: '阿斯佩爾塔選王碑', title_orig: 'Election Stela of Aspelta', era: '約前 600', language: EG, provenance: '博爾戈爾山', status: 'inscription', note: '王位候選人列於阿蒙神像前，由神像「選出」國王——神諭選王的完整記錄。' },
          ],
        },
        {
          key: 'meroe',
          label: '麥羅埃時期',
          label_en: 'Meroitic Period',
          columns: { orig: 'available', en: 'none', zh: 'none' },
          texts: [
            { slug: 'apedemak-hymn', title_zh: '阿佩德馬克頌', title_orig: 'Hymn to Apedemak (Lion Temple, Musawwarat es-Sufra)', era: '約前 3 世紀（阿內克哈瑪尼王）', language: '古埃及文（聖書體，內容為庫施本土神學）', provenance: '穆薩瓦拉特‧蘇夫拉獅子神廟', status: 'inscription', columns: { orig: 'available', en: 'available', zh: 'none' }, note: '以埃及文頌讚庫施本土的獅首戰神——兩套宗教在同一面牆上。' },
            { slug: 'meroitic-funerary', title_zh: '麥羅埃文喪葬銘文', title_orig: 'Meroitic funerary inscriptions', era: '前 2 – 公元 4 世紀', language: '麥羅埃文（未解讀）', provenance: '麥羅埃、卡拉諾格等墓地', status: 'inscription', extent: '逾千件', note: '開頭向伊西斯與奧西里斯呼求的套語可辨認，其餘內容無人能讀。' },
          ],
        },
      ],
    },
  ],
}
