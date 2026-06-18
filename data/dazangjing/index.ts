import type { DazangEra } from './types'
import { ANCIENT_ERA } from './ancient'
import { MEDIEVAL_ERA } from './medieval'
import { EARLY_MODERN_ERA } from './early-modern'
import { MODERN_ERA } from './modern'

export * from './types'
export * from './collection-goals'

// 四個時代：古代 → 中世紀 → 近代 → 現代
// 仿佛教《大藏經》「正藏／續藏」的切割：古代為「正藏」，中世紀以降為「續藏」。
const PRE_CHRISTIAN_ERA: DazangEra = {
  key: 'pre',
  name: '前基督教大藏經',
  name_en: 'Pre-Canonical Antecedents',
  glyph: '前',
  subtitle: '前藏 — 邊界劃分之前的原始啟示母體；同列十藏（經律論宣函儀詩譯史類），唯無正／外之分',
  boundary: '上帝在歷史長河中尚未被特定宗教群體「邊界劃分」之前的原始啟示母體——普遍之道（Logos）在人類文明初期的漫溢。前基督教時代同列十藏，唯不分正／外，皆屬「前藏」。',
  enabled: true,
  collections: [
    {
      key: 'jing',
      name: '經藏',
      name_en: 'Scriptures (Antecedents)',
      glyph: '經',
      genres: '神話‧史詩‧啟示',
      summary: '尚未被任何宗教群體劃下邊界之前的原始啟示母體——近東與地中海的創世、洪水與神話史詩，是後世一神教宇宙觀與救恩敘事共同汲取的源頭。',
      soleCanonLabel: '前藏',
      zheng: {
        divisions: [
          {
            key: 'r-wisdom-lament', label: '智慧與哀歌部', label_en: 'Wisdom and Lament',
            works: [
              { title_zh: '伊普味陳辭（一位埃及賢者的告誡）', title_orig: 'The Admonitions of Ipuwer / Papyrus Leiden I 344 recto', author: '伊普味（託名賢者，作者不詳）', era: '約公元前1850–1600年（中王國末至第二中間期，現存抄本第19王朝）', place: '古埃及', language: '中埃及語（聖書體／僧侶體）', intro: '古埃及著名的「國難文學」與哀歌，描寫社會秩序崩解、上下顛倒、尼羅河泛血、僕人成主、貴族流離的末世圖景，並渴求公義之主再臨。長期被視為對社會秩序與神聖王權之神學反省，其災異意象常被拿來與《出埃及記》十災比較。為兩河—埃及智慧／預言文學進入猶太—基督教啟示母體的重要前驅文獻。' },
              { title_zh: '辯命者與其靈魂的對話（厭世者對話）', title_orig: 'The Dispute between a Man and His Ba', author: '佚名（中王國埃及文士）', era: '約公元前1937–1759年（第十二王朝，現存柏林紙草3024）', place: '古埃及', language: '中埃及語', intro: '一名厭世者與自己的「巴」（靈魂）就生與死、自殺與來世展開辯論，文中以連串優美的迭句歌詠死亡如病癒、如歸鄉、如蓮花之香。為古代近東少見的存在性哲思詩篇，觸及苦難、神義與靈魂歸宿，常與《約伯記》及希臘悲觀文學並置研究，是前基督教啟示母體中關於人之終局的代表作。' },
              { title_zh: '雄辯農夫的申訴', title_orig: 'The Eloquent Peasant / The Tale of the Eloquent Peasant', author: '佚名（中王國埃及文士）', era: '約公元前1850年（第十二王朝）', place: '古埃及（赫拉克利奧波利斯地區）', language: '中埃及語', intro: '敘述一名遭官吏掠奪財物的農夫，以九篇雄辯滔滔的陳情向地方總管申訴，反覆呼求「瑪阿特」（公義／真理／秩序）。文中將公義人格化為宇宙與社會的根本秩序，是古埃及關於正義、廉能與神聖法度最完整的論說，常與希伯來先知對社會公義的呼籲互相對照，屬前基督教倫理啟示母體要籍。' },
              { title_zh: '巴比倫神義論（智者對話）', title_orig: 'The Babylonian Theodicy', author: '薩吉爾-沙杜-烏布利（Saggil-kinam-ubbib，名見離合詩）', era: '約公元前1000年前後', place: '巴比倫尼亞', language: '阿卡德語', intro: '以離合詩體寫成的二十七節對話，受苦者與其友人辯論神義與義人受難之謎：何以敬神者貧病、惡人亨通。結論訴諸神意難測、人心受造即不正。與《約伯記》《傳道書》同屬古近東神義論智慧文學核心，是前基督教啟示母體中探討苦難與神之公義的關鍵文本。' },
              { title_zh: '我要讚美智慧之主（巴比倫約伯）', title_orig: 'Ludlul bēl nēmeqi ("I Will Praise the Lord of Wisdom")', author: '舒布希-梅舍-馬爾杜克（Šubši-mešrê-Šakkan，文中受苦者）', era: '約公元前1300–1100年（卡西特時期）', place: '巴比倫尼亞', language: '阿卡德語', intro: '又稱「巴比倫的約伯」，一位被神馬爾杜克離棄、遍歷疾病屈辱的貴族，歷盡苦難後蒙神轉怒為恩、得醫治復興而獻上頌讚。全詩反思義人受苦、神意難測與終獲拯救，是古近東神義論智慧文學的巔峰，與《約伯記》結構互相輝映，屬前基督教啟示母體必收要籍。' },
            ],
          },
          {
            key: 'r-myth-legend', label: '神話傳說部', label_en: 'Myths and Legends',
            works: [
              { title_zh: '辛努亥的故事', title_orig: 'The Story of Sinuhe / The Tale of Sinuhe', author: '佚名（中王國埃及文士）', era: '約公元前1875年（第十二王朝阿蒙涅姆赫特一世卒後）', place: '古埃及', language: '中埃及語', intro: '古埃及文學的瑰寶，敘述廷臣辛努亥於王逝之際出逃至敘利亞—巴勒斯坦（雷特努），客居異邦顯赫，終蒙王恩召返埃及安葬。文中對王權神聖、流亡與歸鄉、神意眷顧的描寫，呈現古近東關於天命與神人關係的世界觀，並提供與族長敘事相鄰的迦南背景，為前基督教啟示母體中傳記與天命文學的典範。' },
            ],
          },
          {
            key: 'r-meso-hymn', label: '兩河頌歌部', label_en: 'Mesopotamian Hymns',
            works: [
              { title_zh: '尼努爾塔頌詩（盧伽爾-埃）', title_orig: 'Lugal-e (Ninurta and the Stones) / Lugal ud melambi nirgal', author: '佚名（蘇美爾祭司詩人）', era: '約公元前2000年前後（古巴比倫抄本，傳承更早）', place: '蘇美爾／巴比倫尼亞', language: '蘇美爾語（後附阿卡德語對照）', intro: '蘇美爾大型敘事頌詩，歌詠戰神尼努爾塔擊敗山中惡魔阿薩格、整治洪水、為大地立定秩序並判定群石命運。屬「創造—混沌之戰」（Chaoskampf）神話類型，與《埃努瑪‧埃利什》及希伯來詩篇中神制伏大水的意象同源，是研究古近東宇宙秩序與神聖王權的重要前基督教啟示母體文獻。' },
              { title_zh: '伊南娜下冥府', title_orig: 'Inanna\'s Descent to the Netherworld', author: '佚名（蘇美爾祭司詩人）', era: '約公元前2000–1600年（古巴比倫抄本，傳承更早）', place: '蘇美爾（尼普爾等地）', language: '蘇美爾語', intro: '蘇美爾神話名篇，敘述天后伊南娜下降姊妹埃列什基伽勒所統治的冥界，七道門前逐一卸去衣飾權柄，終至死亡，後賴智慧神恩基所造之使者得以復生，並以其夫杜牧茲為替身。為古近東「下陰府—復生」神話的核心文本，常與基督復活、降在陰間的母題作比較宗教研究，屬前基督教啟示母體要籍。' },
              { title_zh: '蘇美爾王表', title_orig: 'The Sumerian King List', author: '佚名（蘇美爾／古巴比倫編者）', era: '約公元前2100–1800年（烏爾第三王朝至古巴比倫）', place: '蘇美爾（尼普爾、伊辛等地）', language: '蘇美爾語', intro: '蘇美爾的王朝編年表，列舉「王權自天而降」後諸城邦在位君王及其超長享年，並以一場大洪水劃分洪前與洪後王朝。其洪前長壽諸王與《創世記》第五章洪前族長譜，以及對「洪水分界」的歷史想像，長期為比較研究焦點，是前基督教啟示母體中關於王權神授與原史編年的關鍵文獻。' },
              { title_zh: '埃爾拉與伊舒姆史詩', title_orig: 'The Epic of Erra (Erra and Ishum)', author: '傳為卡布提-伊拉尼-馬爾杜克（Kabti-ilani-Marduk）', era: '約公元前8世紀（一說前11世紀）', place: '巴比倫尼亞', language: '阿卡德語（巴比倫方言）', intro: '巴比倫晚期史詩，敘述瘟疫與戰禍之神埃爾拉在隨從伊舒姆勸阻下，趁馬爾杜克離位而傾覆巴比倫城、降下浩劫，終得平息並應許復興。文末自稱由神親授作者於夢中，具護身辟邪功能。為古近東少見自帶「神諭啟示」框架的災異—神義文學，是前基督教啟示母體中關於神怒、毀滅與復興的代表作。' },
              { title_zh: '舒爾帕乞除咒文集', title_orig: 'Šurpu ("Burning") incantation series', author: '佚名（巴比倫祭司）', era: '約公元前2千紀末至前1千紀（標準版定型於前1千紀）', place: '巴比倫尼亞／亞述', language: '阿卡德語（附蘇美爾語）', intro: '九塊泥板的標準祓除咒文叢書，藉焚燒物事象徵性地解除病人因觸犯禁忌、違誓、得罪神人而招致的咒詛與不潔，其中第二板列舉大量道德與儀禮罪過，近似「罪過清單」與認罪文。為研究古近東罪、潔淨、贖罪觀念的核心儀文，與利未記潔淨律及悔罪神學互相對照，屬前基督教啟示母體文獻。' },
            ],
          },

          {
            key: 'cosmogony', label: '創世神話部', label_en: 'Creation Myths',
            works: [
              { title_zh: '埃努瑪‧埃利什（巴比倫創世史詩）', title_orig: 'Enūma Eliš (The Creation Epic)', author: '佚名（巴比倫祭司傳統）', era: '約前 12 世紀定型（題材更古，古巴比倫時期）', place: '巴比倫', language: '阿卡德文（巴比倫方言，楔形文字）', intro: '以「天之上未名、地之下未喚」開篇的巴比倫創世史詩，共七版泥板。敘述馬爾杜克擊敗原始混沌之母提亞瑪特，剖其屍身造天地，再以血造人服事眾神，終受眾神尊為主。其以神聖言語與爭戰締造秩序的母題，與創世記神戰勝混沌、以言創世遙相呼應，是研究希伯來宇宙論不可繞過的近東母體。' },
              { title_zh: '孟斐斯神學（夏巴卡石碑）', title_orig: 'The Theology of Memphis (Shabaka Stone)', author: '佚名（孟斐斯祭司傳統；法老夏巴卡令刊石）', era: '前 8 世紀刊石（自稱抄自更古文本）', place: '埃及（孟斐斯）', language: '古埃及文（聖書體）', intro: '刻於夏巴卡石碑的孟斐斯創世神學，宣稱造物神普塔以「心思」構想、以「舌（言語）」說出而造成萬物與眾神。此以思與言創世的觀念，被視為近東「言語創造」與後世「邏各斯（道）」神學最古老的先驅之一，與創世記神「說有就有」及約翰福音「太初有道」的思想遙相輝映，分量極重。' },
              { title_zh: '神譜', title_orig: 'Hesiod, Theogony (Θεογονία)', author: '赫西俄德', era: '約前 8 世紀末至前 7 世紀初', place: '希臘（彼奧提亞‧阿斯克拉）', language: '古希臘文', intro: '現存最早的希臘系統性宇宙起源與諸神譜系詩，以六步格寫成。自混沌（卡俄斯）、大地（蓋亞）開始，敘諸神世代更迭直至宙斯確立統治。其「太初有混沌」的開篇與創世神話母題，常被拿來與《創世記》起首對照，是後世一神教與希臘哲學共同汲取的宇宙論土壤，亦為神義論與神性思辨的源頭文本。' },
            ],
          },
          {
            key: 'flood', label: '洪水史詩部', label_en: 'Flood Epics',
            works: [
              { title_zh: '吉爾伽美什史詩', title_orig: 'The Epic of Gilgamesh', author: '佚名（標準版傳為 Sîn-lēqi-unninni 編輯）', era: '古巴比倫期始（前 18 世紀），標準版約前 13–11 世紀', place: '美索不達米亞（烏魯克／巴比倫）', language: '阿卡德文（楔形文字）', intro: '人類最古老的長篇史詩，敘述烏魯克王吉爾伽美什與野人恩奇杜結誼、恩奇杜之死、及主角為求永生之遠行。第十一版泥板載烏特那匹什提姆親述大洪水：眾神降水滅世、一人造方舟、放鳥探水的情節，與創世記挪亞洪水驚人雷同，為比較研究的經典範本。' },
              { title_zh: '阿特拉哈西斯史詩', title_orig: 'Atrahasis (The Atrahasis Epic)', author: '佚名（傳抄者 Ipiq-Aya 等）', era: '古巴比倫期（約前 17 世紀）', place: '美索不達米亞', language: '阿卡德文（楔形文字）', intro: '巴比倫「原史」型史詩，自造人講到洪水。眾神因人類繁衍喧嘩而先以瘟疫、饑荒、終以洪水滅世，獨智者阿特拉哈西斯受恩基暗示造舟得救。它把創造—墮落—洪水串成一條連貫敘事線，結構上最接近創世記一至九章的「太古史」，是探討希伯來太古史框架來源的關鍵文本。' },
              { title_zh: '蘇美爾洪水神話（大洪水）', title_orig: 'A Sumerian Myth: The Deluge', author: '佚名（蘇美爾傳統）', era: '約前 17 世紀抄本（題材更古）', place: '蘇美爾（尼普爾）', language: '蘇美爾文（楔形文字）', intro: '今存最古老的洪水神話蘇美爾版本，泥板殘缺。敘述眾神決意降洪滅人，虔敬的祭司王兹烏蘇德拉得神示造大船，洪水七日七夜後船停、王獻祭得永生。它是吉爾伽美什與阿特拉哈西斯洪水母題的更早源頭，見證近東洪水傳統自蘇美爾一脈相承直至希伯來聖經。' },
            ],
          },
          {
            key: 'canaan', label: '迦南神話部', label_en: 'Canaanite Myths',
            works: [
              { title_zh: '巴力與阿娜特詩篇（巴力史詩）', title_orig: 'The Poems about Baal and Anath (Baal Cycle)', author: '佚名（傳抄者書記 Ilimilku）', era: '約前 14 世紀抄本', place: '烏加列（敘利亞拉斯沙姆拉）', language: '烏加列文（字母楔形文字）', intro: '烏加列出土的迦南最重要神話群，敘述風暴與豐饒之神巴力擊敗海神雅姆、建造宮殿、再與死神墨特交戰而死又復生的循環，反映農耕季節的死生節律。文中巴力「駕雲者」的稱號、與海／死的爭戰母題，照亮了希伯來詩篇與先知書中耶和華形象的迦南背景。' },
              { title_zh: '阿赫特傳說', title_orig: 'The Tale of Aqhat', author: '佚名（傳抄者書記 Ilimilku）', era: '約前 14 世紀抄本', place: '烏加列（敘利亞拉斯沙姆拉）', language: '烏加列文（字母楔形文字）', intro: '烏加列史詩之一。賢君達尼伊勒久無子嗣，得巴力代求而獲麟兒阿赫特；少年因拒讓神弓予女神阿娜特而被害，引發旱災與其姊復仇。詩中達尼伊勒「在城門口為孤兒寡婦伸冤」的義王形象，與希伯來智慧及先知的公義理想相呼應，亦見證迦南文學的高度成熟。' },
              { title_zh: '凱雷特王傳說', title_orig: 'The Legend of King Keret', author: '佚名（傳抄者書記 Ilimilku）', era: '約前 14 世紀抄本', place: '烏加列（敘利亞拉斯沙姆拉）', language: '烏加列文（字母楔形文字）', intro: '烏加列王室史詩。凱雷特王喪盡妻兒，主神伊勒於夢中示其出兵求得新后、重建家室並承神賜多子之福；後王患重病、其子覬覦王位，引出王權與孝道的張力。詩中神在夢中向王立約賜後裔的母題，與族長敘事中神對亞伯拉罕的應許頗可對讀，是迦南王權神學的珍貴見證。' },
            ],
          },
          {
            key: 'persia', label: '波斯啟示部', label_en: 'Persian Revelation',
            works: [
              { title_zh: '伽薩頌詩', title_orig: 'Gathas (Gāθās)', author: '傳為先知瑣羅亞斯德（查拉圖斯特拉）', era: '古伊朗（學界多繫於前 1000 年以前，語言層約前 600 年）', place: '古伊朗（東伊朗地區）', language: '古阿維斯陀文', intro: '《阿維斯陀》中最古老的核心，是十七首阿維斯陀文古頌詩，傳為先知瑣羅亞斯德親作，長期口傳後始書錄。頌詩向至高善神阿胡拉‧馬茲達祈禱頌讚，闡發善惡二元對立、自由抉擇、末日審判與善終得救的教義。其一神傾向、二元論與末世論，被認為深刻影響了猶太教與基督教的天使、撒旦、審判與復活觀念，是波斯啟示母體的根本經典。' },
            ],
          },
        ],
      },
      wai: { divisions: [] },
    },
    {
      key: 'lu',
      name: '律藏',
      name_en: 'Law (Antecedents)',
      glyph: '律',
      genres: '律法',
      summary: '古代近東的成文律法傳統，以同態報復與判例體例規範社會，是希伯來西奈律法的近東背景。',
      soleCanonLabel: '前藏',
      zheng: {
        divisions: [
          {
            key: 'law', label: '古代律法部', label_en: 'Ancient Law',
            works: [
              { title_zh: '漢摩拉比法典', title_orig: 'The Code of Hammurabi', author: '漢摩拉比王', era: '約前 1750 年', place: '巴比倫', language: '阿卡德文（楔形文字）', intro: '古巴比倫漢摩拉比王頒布的法典，刻於黑石碑上，碑頂浮雕王自太陽神沙瑪什手中領受權柄。含序言、約 282 條判例式律法與跋語，涵蓋商業、婚姻、傷害、奴隸等，以「以眼還眼」的同態報復著稱。其體例與條文與出埃及記《約書》多有可比之處，是研究西奈律法近東背景的首要對照文獻。' },
            ],
          },
        ],
      },
      wai: { divisions: [] },
    },
    {
      key: 'lun',
      name: '論藏',
      name_en: 'Treatises (Antecedents)',
      glyph: '論',
      genres: '哲學‧思辨',
      summary: '希臘羅馬的哲學思辨傳統，從宇宙論、形上學到斯多葛倫理，為基督教神學提供了理性語彙與思想工具。',
      soleCanonLabel: '前藏',
      zheng: {
        divisions: [
          {
            key: 'r-presocratic', label: '前蘇格拉底部', label_en: 'Pre-Socratics',
            works: [
              { title_zh: '前期希臘哲學（Loeb 新編「前蘇格拉底」九卷集）', title_orig: 'Early Greek Philosophy (9 vols.)', author: 'André Laks、Glenn W. Most（編譯）', era: '原典約公元前 6–5 世紀；本版 2016 年', place: '編譯於歐美；原典出於愛奧尼亞、義大利大希臘等地', language: '古希臘文／英文對照', parent: 'Early Greek Philosophy', extent: '9 卷', intro: '哈佛 Loeb 於 2016 年推出的前蘇格拉底哲人新編全集，取代舊「Presocratics」之名，凡九卷。收錄赫拉克利特、巴門尼德、恩培多克勒、阿那克薩哥拉、德謨克利特、畢達哥拉斯派等殘篇與見證，附導論與索引。為後世基督教神學汲取「邏各斯」「元素」「靈魂」概念之希臘母體源頭。' },
              { title_zh: '論自然（阿那克西曼德殘篇）', title_orig: 'Anaximander, Περὶ φύσεως (On Nature) — DK 12 B', author: '阿那克西曼德', era: '約公元前六世紀中葉（約前 547 年前後）', place: '希臘（小亞細亞‧米利都）', language: '古希臘文（伊奧尼亞方言，散文）', parent: '前蘇格拉底殘篇集（第爾斯—克朗茲輯）', intro: '傳為希臘第一部散文體自然哲學著作，僅存後世徵引的一句直接殘篇與大量旁證。提出無限定者「阿派朗」（ἄπειρον）為萬物本原，諸物由其分出又依「時序」償還不義而復歸於彼。其以宇宙秩序為一種公義償付的構想，是西方形上學與宇宙論的源頭，亦為後世邏各斯與創造秩序神學提供了最早的理性語彙。' },
              { title_zh: '論自然（阿那克西美尼殘篇）', title_orig: 'Anaximenes, Περὶ φύσεως (On Nature) — DK 13 B', author: '阿那克西美尼', era: '約公元前六世紀（約前 546–525 年）', place: '希臘（小亞細亞‧米利都）', language: '古希臘文（伊奧尼亞方言，散文）', parent: '前蘇格拉底殘篇集（第爾斯—克朗茲輯）', intro: '米利都學派第三代哲人之作，今佚，僅存後世旁證與少數殘句。主張「氣」（ἀήρ）為萬物本原，藉「稀薄」與「凝聚」之作用化生火、風、雲、水、土，並以氣為宇宙與靈魂的維繫者。其以單一質料經量變生成萬有的機制，是早期一元論宇宙生成論的重要環節，影響及於斯多葛的氣息（pneuma）學說。' },
              { title_zh: '論自然（赫拉克利特殘篇）', title_orig: 'Heraclitus, Περὶ φύσεως (On Nature) — DK 22 B', author: '赫拉克利特', era: '約公元前 500 年前後', place: '希臘（小亞細亞‧以弗所）', language: '古希臘文（伊奧尼亞方言，箴言體散文）', parent: '前蘇格拉底殘篇集（第爾斯—克朗茲輯）', extent: '約 130 條 B 殘篇', intro: '以晦澀箴言著稱的以弗所哲人遺著，存約一百三十條 B 殘篇。倡萬物流轉（「人不能兩次踏進同一條河」）、對立統一，並以「邏各斯」（λόγος）為貫通萬有、人所當聆聽的普遍理性與宇宙法度。其邏各斯學說經斯多葛中介，深刻影響《約翰福音》「太初有道」的神學表述，是基督教道論最重要的希臘哲學前驅。' },
              { title_zh: '諷刺詩與哀歌殘篇（克塞諾芬尼）', title_orig: 'Xenophanes, Σίλλοι (Silloi) & Elegies — DK 21 B', author: '克塞諾芬尼', era: '約公元前六世紀後期（盛年約前 540–537 年，享壽逾九十）', place: '希臘（小亞細亞‧科洛封，後流寓大希臘）', language: '古希臘文（六步格、哀歌體、抑揚格詩）', parent: '前蘇格拉底殘篇集（第爾斯—克朗茲輯）', intro: '科洛封游吟詩人兼哲人之詩作殘篇，含《諷刺詩》（Silloi）與哀歌。猛烈批判荷馬與赫西俄德把偷盜姦淫加諸諸神，並譏神人同形論（謂牛馬若能繪畫亦將造出牛馬之神），轉而推尊一位「至大唯一、不似有死者形貌與心思」之神。其對擬人多神論的哲學批判與單一神觀，被視為希臘理性一神論的先聲，與聖經反偶像傳統遙相呼應。' },
              { title_zh: '論自然（巴門尼德教誨詩）', title_orig: 'Parmenides, Περὶ φύσεως (On Nature) — DK 28 B', author: '巴門尼德', era: '約公元前五世紀前期（盛年約前 504–501 年）', place: '大希臘（南義大利‧埃利亞）', language: '古希臘文（六步格教誨詩）', parent: '前蘇格拉底殘篇集（第爾斯—克朗茲輯）', extent: '三部式長詩，僅存約 160 行殘篇', intro: '埃利亞學派奠基者之長篇教誨詩，存約一百六十行，分〈序詩〉〈真理之道〉〈意見之道〉三部。藉女神啟示宣告「存有者存在、非存有者不存在」，論定真實之「有」乃不生不滅、單一、不動、完滿的圓球。其關於「存有」（τὸ ἐόν）之單一、永恆、不變的論證，奠定西方存有論基礎，並為後世闡述神之單純性、不變性與永恆性提供了形上學語彙。' },
              { title_zh: '論自然（芝諾悖論殘篇）', title_orig: 'Zeno of Elea, fragments (the Paradoxes) — DK 29 B', author: '埃利亞的芝諾', era: '約公元前五世紀中葉（生年約前 490 年）', place: '大希臘（南義大利‧埃利亞）', language: '古希臘文（散文）', parent: '前蘇格拉底殘篇集（第爾斯—克朗茲輯）', intro: '巴門尼德弟子之著作，原書已佚，今由亞里斯多德《物理學》及辛普利修斯註釋保存其論證與少數直接殘篇。以「二分」「阿基里斯追龜」「飛矢不動」「運動場」等悖論，反證多與運動之概念自相矛盾，藉歸謬法捍衛師說「唯一不動之有」。被亞里斯多德譽為辯證法之祖，其無窮分割與連續性難題深刻影響後世數學與哲學。' },
              { title_zh: '論自然或論存有（梅利索斯殘篇）', title_orig: 'Melissus of Samos, Περὶ φύσεως ἢ περὶ τοῦ ὄντος (On Nature or On What Exists) — DK 30 B', author: '薩摩斯的梅利索斯', era: '約公元前五世紀中葉', place: '希臘（薩摩斯島）', language: '古希臘文（伊奧尼亞方言，散文）', parent: '前蘇格拉底殘篇集（第爾斯—克朗茲輯）', intro: '埃利亞學派最後一位代表的散文論著，殘篇多由辛普利修斯註釋亞里斯多德《物理學》《論天》時保存。系統論證「存有」乃無始無終（故為無限）、單一、不變、不可分、無痛苦煩惱者，將巴門尼德之說推向嚴格一元論。其以散文清晰陳述「有」之無限與不變，是早期形上學論證最完整的范本之一，對神之無限性論述有所啟發。' },
              { title_zh: '論自然與淨化（恩培多克勒殘篇）', title_orig: 'Empedocles, Περὶ φύσεως (On Nature) & Καθαρμοί (Purifications) — DK 31 B', author: '恩培多克勒', era: '約公元前五世紀前半（約前 495–435 年）', place: '大希臘（西西里‧阿克拉加斯）', language: '古希臘文（六步格詩）', parent: '前蘇格拉底殘篇集（第爾斯—克朗茲輯）', intro: '阿克拉加斯哲人兼詩人之六步格詩篇，傳含《論自然》與《淨化》二題（一說同篇），存逾百行 B 殘篇，2000 年又有斯特拉斯堡紙草增補。提出地、水、氣、火四「根」說，並以「愛」與「爭」二力主宰其聚合分離，構成宇宙循環；《淨化》則言靈魂輪迴轉世與淨化得救。其四元素說與愛之凝聚力，影響亞里斯多德及後世自然哲學甚鉅。' },
              { title_zh: '論自然（阿那克薩哥拉殘篇）', title_orig: 'Anaxagoras, Περὶ φύσεως (On Nature) — DK 59 B', author: '阿那克薩哥拉', era: '約公元前五世紀中葉（約前 500–428 年）', place: '希臘（小亞細亞‧克拉佐美奈，後居雅典）', language: '古希臘文（伊奧尼亞方言，散文）', parent: '前蘇格拉底殘篇集（第爾斯—克朗茲輯）', intro: '首位將哲學帶入雅典的伊奧尼亞哲人遺著，殘篇多賴辛普利修斯保存。主張萬物原為一切「種子」（種質）之無限混合，「一切之中有一切」，而由超越萬物、純一無雜的「努斯」（νοῦς，心智）發動旋轉、使之分離成序。其以理性心智為宇宙生成之動因的構想，被柏拉圖、亞里斯多德繼承發揮，是目的論與心智—宇宙關係思想的關鍵源頭。' },
              { title_zh: '論自然（阿波羅尼亞的第歐根尼殘篇）', title_orig: 'Diogenes of Apollonia, Περὶ φύσεως (On Nature) — DK 64 B', author: '阿波羅尼亞的第歐根尼', era: '約公元前五世紀後半', place: '希臘‧阿波羅尼亞（學界主流定為黑海沿岸阿波羅尼亞〔Apollonia Pontica，今索佐波爾〕；克里特一說多被否定）；曾活躍於雅典', language: '古希臘文（伊奧尼亞方言，散文）', parent: '前蘇格拉底殘篇集（第爾斯—克朗茲輯）', intro: '晚期伊奧尼亞自然哲學家之作，殘篇主要由辛普利修斯保存。復興阿那克西美尼的「氣」本原說，並賦予其智性：謂「氣」乃具有理智（noēsis）、神聖而無所不在者，藉之安排萬物盡善盡美、調節呼吸與生命。其將宇宙本原視為兼具神性與理智的安排者，呈現早期哲學一神論與目的論色彩，於阿里斯托芬《雲》中亦見其影。' },
              { title_zh: '原子論殘篇（留基伯）', title_orig: 'Leucippus, Μέγας διάκοσμος (The Great World-System) — DK 67 B', author: '留基伯', era: '約公元前五世紀中葉', place: '希臘（傳為米利都或阿布德拉、埃利亞）', language: '古希臘文（散文）', parent: '前蘇格拉底殘篇集（第爾斯—克朗茲輯）', intro: '原子論奠基者之遺著，傳著《大宇宙論》（Megas diakosmos），今幾乎全佚，僅存一句直接殘篇（言「無一物無故而生，皆出於理與必然」）及大量旁證。首創萬物由不可分的「原子」在「虛空」中運動聚散而成的學說，與其弟子德謨克利特共構古代原子論。其因果必然性的機械宇宙觀，是後世伊壁鳩魯派與近代原子論的遠源。' },
              { title_zh: '倫理與自然殘篇（德謨克利特）', title_orig: 'Democritus, Ethical & Physical fragments — DK 68 B', author: '德謨克利特', era: '約公元前五世紀後半至前四世紀初（約前 460–370 年）', place: '希臘（色雷斯‧阿布德拉）', language: '古希臘文（伊奧尼亞方言，散文）', parent: '前蘇格拉底殘篇集（第爾斯—克朗茲輯）', extent: '倫理格言數百條', intro: '「笑的哲人」德謨克利特之大量殘篇，物理學說多賴旁證、倫理格言則直接傳世（含斯托拜俄斯所輯數百條）。承留基伯原子論，主張萬物由原子與虛空構成、感覺為約定俗成；倫理上則倡「歡愉」（euthymia，心境寧靜）為人生至善，重節制與自省。其原子唯物論與內在心安的倫理觀，是伊壁鳩魯派的直接先驅，影響西方自然主義傳統深遠。' },
              { title_zh: '論自然（阿爾克邁翁殘篇）', title_orig: 'Alcmaeon of Croton, Περὶ φύσεως (On Nature) — DK 24 B', author: '克羅頓的阿爾克邁翁', era: '約公元前六世紀末至前五世紀初', place: '大希臘（南義大利‧克羅頓）', language: '古希臘文（散文）', parent: '前蘇格拉底殘篇集（第爾斯—克朗茲輯）', intro: '克羅頓的醫者兼哲人之著作，傳為最早以散文論自然與醫學者之一，殘篇存其開篇語。首倡腦為感覺與思維之中樞、區別感知與理解，並以對立兩極（如冷熱、乾濕）之「均衡」（isonomia）為健康、其偏勝為疾病。其靈魂不朽（因永動如日月星辰）之說與身心醫哲思想，影響畢達哥拉斯派與柏拉圖，是醫學哲學的奠基文獻。' },
              { title_zh: '論自然（菲洛勞斯殘篇，畢達哥拉斯派）', title_orig: 'Philolaus of Croton, Περὶ φύσεως (On Nature) — DK 44 B', author: '克羅頓的菲洛勞斯', era: '約公元前五世紀後半（約前 470–385 年）', place: '大希臘（南義大利‧克羅頓，後居底比斯）', language: '古希臘文（多里斯方言，散文）', parent: '前蘇格拉底殘篇集（第爾斯—克朗茲輯）', intro: '傳為畢達哥拉斯學派第一部成書者，殘篇真偽經學界辨析後有一批被認可為真。主張萬物由「有限者」與「無限者」藉「和諧」（harmonia）依數而結合構成，唯有透過數方能認識萬有；並提出地球非宇宙中心、繞「中央之火」運行的天文模型。其數本原論與宇宙和諧思想，是柏拉圖《蒂邁歐篇》與後世數理神學的重要源頭。' },
              { title_zh: '殘篇（塔蘭托的阿爾庫塔斯）', title_orig: 'Archytas of Tarentum, fragments — DK 47 B', author: '塔蘭托的阿爾庫塔斯', era: '約公元前四世紀前半（盛年約前 400–350 年）', place: '大希臘（南義大利‧塔蘭托）', language: '古希臘文（多里斯方言，散文）', parent: '前蘇格拉底殘篇集（第爾斯—克朗茲輯）', intro: '畢達哥拉斯學派晚期領袖、數學家兼政治家之殘篇（公認之真品數則，另有大量託名偽作）。論算術、幾何、天文、音樂「四藝」之相互關聯與數之比例，並以數理和諧為認識與政治和睦之本。其關於宇宙是否有界的著名論證（伸手於天界之邊外）流傳後世；身為柏拉圖友人，對學園之數理傾向影響甚深，是連結畢氏傳統與柏拉圖主義的關鍵人物。' },
              { title_zh: '雙重論證（對置之論）', title_orig: 'Dissoi Logoi (Δισσοὶ λόγοι, \'Twofold Arguments\') — DK 90', author: '佚名（智者派傳統，託名不明）', era: '約公元前五世紀末至前四世紀初（約前 400 年前後）', place: '希臘（多里斯方言區，或大希臘／伯羅奔尼撒）', language: '古希臘文（多里斯方言，散文）', parent: '前蘇格拉底殘篇集（第爾斯—克朗茲輯）', intro: '第爾斯—克朗茲輯第九十章所收的匿名智者派論文，以多里斯方言寫成。就善惡、美醜、正義與不義、真假等題目，逐一陳列「正反兩面皆可成立」之對立論證，展現智者派相對主義與辯論術的訓練樣貌。為現存最完整的早期智者派文獻之一，見證蘇格拉底時代論辯文化，是修辭學與相對主義思想的珍貴原始材料。' },
              { title_zh: '安提豐殘篇（論真理‧論和睦）', title_orig: 'Antiphon the Sophist, Περὶ ἀληθείας (On Truth) & Περὶ ὁμονοίας (On Concord) — DK 87 B', author: '智者安提豐', era: '約公元前五世紀後半', place: '希臘（雅典）', language: '古希臘文（散文）', parent: '前蘇格拉底殘篇集（第爾斯—克朗茲輯）', intro: '雅典智者安提豐之殘篇，部分賴牛津紙草（Oxyrhynchus）出土增補。於《論真理》中區別「自然」（physis）與「約定」（nomos），主張自然之命令真實必然、人為法律則多違自然，並以此論及人皆平等（不分希臘人與蠻族）。其自然法與約定法之張力、人類平等思想，是西方自然法觀念與政治哲學的早期源頭，影響及於斯多葛與後世法理學。' },
              { title_zh: '克里底亞殘篇（西緒福斯片段）', title_orig: 'Critias, fragments incl. the \'Sisyphus\' fragment — DK 88 B', author: '克里底亞', era: '約公元前五世紀後半（卒於前 403 年）', place: '希臘（雅典）', language: '古希臘文（韻文與散文）', parent: '前蘇格拉底殘篇集（第爾斯—克朗茲輯）', intro: '雅典政治家兼文人克里底亞（柏拉圖之表舅、三十僭主之一）的詩文殘篇，最著名者為託名薩堤洛斯劇《西緒福斯》之長段。其中藉劇中人之口，提出「諸神乃聰明之人為使人畏懼、暗中亦不敢為惡而虛構出來」的宗教起源說。此片段是古代最早、最直白的「宗教乃人為發明」之無神論論證，於宗教批判史與宗教起源理論中具標誌性地位。' },
              { title_zh: '普羅塔哥拉殘篇（論真理‧論神）', title_orig: 'Protagoras, Ἀλήθεια (Truth) & Περὶ θεῶν (On the Gods) — DK 80 B', author: '普羅塔哥拉', era: '約公元前五世紀（約前 490–420 年）', place: '希臘（色雷斯‧阿布德拉，活躍於雅典）', language: '古希臘文（散文）', parent: '前蘇格拉底殘篇集（第爾斯—克朗茲輯）', intro: '首位自稱「智者」的阿布德拉哲人之殘篇，原著已佚，存其著名命題。《論真理》開篇宣告「人是萬物的尺度」，奠定相對主義；《論神》則以「關於諸神，我無從知其有無，亦不知其形貌，因題目晦澀而人生短促」開篇，據傳因此遭控不敬神而著作被焚。其相對主義知識論與宗教不可知論，是古代懷疑思想與宗教批判的關鍵原典。' },
              { title_zh: '高爾吉亞殘篇（論非有或論自然‧海倫頌）', title_orig: 'Gorgias, Περὶ τοῦ μὴ ὄντος (On Non-Being) & Ἑλένης ἐγκώμιον (Encomium of Helen) — DK 82 B', author: '萊昂蒂尼的高爾吉亞', era: '約公元前五世紀（約前 483–375 年）', place: '大希臘（西西里‧萊昂蒂尼，活躍於雅典）', language: '古希臘文（散文）', parent: '前蘇格拉底殘篇集（第爾斯—克朗茲輯）', intro: '西西里智者兼修辭大師高爾吉亞之殘篇。《論非有（或論自然）》以三段命題（無物存在；縱有亦不可知；縱可知亦不可傳）戲仿並顛覆埃利亞存有論，是懷疑論與語言哲學的奇文；《海倫頌》則藉為海倫辯護，盛論言辭（logos）對人心如藥物般的巨大力量。二篇展現智者修辭術的高峰，對語言、勸服與真理之關係的反思影響深遠。' },
            ],
          },
          {
            key: 'r-greek-roman-supp', label: '希臘羅馬哲學補部', label_en: 'Greek-Roman Philosophy (suppl.)',
            works: [
              { title_zh: '克律西波斯殘篇（《古斯多亞殘篇》所輯）', title_orig: 'Chrysippos, fragmenta (apud SVF, Stoicorum Veterum Fragmenta)', author: '克律西波斯（索利／雅典）', era: '約公元前279—前206年', place: '雅典', language: '古希臘文', parent: '古斯多亞殘篇集（SVF）', intro: '古斯多亞學派第三任掌門、體系集大成者克律西波斯著作逾百種（一說約 705–750 部），今僅存殘篇與述評（馮‧阿尼姆輯《古斯多亞殘篇》SVF）。其邏輯、命運、攝理（pronoia）與宇宙理性（Logos）學說奠定斯多葛體系，並最早將命題邏輯立為一門學問；古諺謂「無克律西波斯則無斯多葛」。是教父攝理論與自然法思想的重要對話對象。' },
              { title_zh: '芝諾殘篇（《古斯多亞殘篇》所輯）', title_orig: 'Zēnōn ho Kitieus, fragmenta (apud SVF)', author: '季蒂昂的芝諾', era: '約公元前334—前262年', place: '雅典', language: '古希臘文', parent: '古斯多亞殘篇集（SVF）', intro: '斯多葛學派創始人芝諾之著作今僅存殘篇與述評（輯入 SVF）。於雅典「彩繪柱廊」（Stoa Poikile）講學，學派因而得名。其「順應自然而生活」之倫理綱領、邏各斯宇宙論與理想城邦《理想國》構想，奠定斯多葛傳統，並透過西塞羅、塞內加流入西方倫理與基督教自然法思想。' },
              { title_zh: '宙斯頌歌', title_orig: 'Cleanthes, Hymn to Zeus (Ὕμνος εἰς Δία)', author: '阿索斯的克勒安提斯', era: '約公元前 3 世紀', place: '希臘（雅典）', language: '古希臘文（詩體）', parent: '古斯多亞殘篇集（SVF）', intro: '斯多葛學派第二代領袖、芝諾的繼任者克勒安提斯所作的哲理頌詩，是早期斯多葛思想罕見的完整存世文獻。頌歌讚美宙斯為宇宙至高理性、普遍法則與天命的化身，萬物循其律而行，唯惡人逆理而亂，並祈求神引人歸於理性與善。其近乎一神論的禱頌語調與對神聖法則、天命的虔敬，被視為異教虔誠最接近聖經敬拜的高峰之一；《使徒行傳》保羅在雅典所引「我們也是他所生的」一語即出自斯多葛詩人傳統。' },
              { title_zh: '愛比克泰德《談話錄》', title_orig: 'Epiktētos, Diatribai (Discourses, rec. Arrianus)', author: '愛比克泰德（記錄者：尼科米底亞的阿里安）', era: '約公元108年（弟子阿里安筆錄）', place: '尼科波利斯（伊庇魯斯，希臘西北）', language: '古希臘文／英文對照', parent: '愛比克泰德語錄', extent: '現存 4 卷（Loeb LCL 131＋218）', intro: '出身奴隸的斯多葛哲人愛比克泰德之講學實錄，由弟子阿里安筆錄，現存四卷（原八卷）。倡分辨「在我者」與「不在我者」、順應神意、內心自由。其堅忍、順服天意之教，與早期基督教的受苦觀、信靠攝理多有共鳴。Loeb 分兩卷：LCL 131（卷1–2）與 LCL 218（卷3–4，附殘篇與手冊）。' },
              { title_zh: '愛比克泰德《手冊》', title_orig: 'Epiktētos, Encheiridion (Handbook)', author: '愛比克泰德（記錄者：阿里安）', era: '公元2世紀初', place: '尼科波利斯（伊庇魯斯）', language: '古希臘文', parent: '愛比克泰德語錄', intro: '《談話錄》精要的格言手冊，凝練斯多葛修身要訣於數十短章，便於誦記力行。其簡潔的修心箴言廣為流傳，後經基督教化改寫為修道院靈修讀本（如尼羅斯本），是斯多葛與基督教靈修融通的顯例。' },
              { title_zh: '伊比鳩魯《致美諾寇書》', title_orig: 'Epikouros, Epistolē pros Menoikea (Letter to Menoeceus)', author: '伊比鳩魯', era: '約公元前300年前後', place: '希臘（雅典）', language: '古希臘文', parent: '名哲言行錄（第歐根尼‧拉爾修，第十卷）', intro: '伊比鳩魯倫理綱要書簡，全文保存於第歐根尼‧拉爾修《名哲言行錄》第十卷。論神不干預世界、死亡不足懼、快樂為去苦的恬靜（ataraxia），提出著名的「四味良藥」。其無懼死亡與無神干預的自然觀，為教父批判的對象，亦是基督教與享樂主義對話的核心文本。' },
              { title_zh: '伊比鳩魯《主要信條》（要義集）', title_orig: 'Epikouros, Kyriai Doxai (Principal Doctrines)', author: '伊比鳩魯', era: '約公元前4世紀末—前3世紀初', place: '希臘（雅典）', language: '古希臘文', parent: '名哲言行錄（第歐根尼‧拉爾修，第十卷）', extent: '40 則格言', intro: '伊比鳩魯學派四十條核心教義格言集，供門徒誦記，全文保存於第歐根尼‧拉爾修第十卷末。開篇四句即「四味良藥」（神不足懼、死不足憂、善易得、惡易忍），其下論快樂、正義（正義即契約）、友誼與心靈的安寧。其格言體系是理解伊比鳩魯主義的鑰匙，亦為古代倫理與正義觀的重要他者。' },
              { title_zh: '物性論', title_orig: 'Lucretius, De Rerum Natura (On the Nature of Things)', author: '盧克萊修（W. H. D. Rouse 英譯，M. F. Smith 修訂）', era: '約公元前 1 世紀中葉（約前 99—前 55 年）', place: '羅馬共和國', language: '拉丁文／英文對照', extent: '全 6 卷', intro: '盧克萊修以六步格拉丁長詩闡發伊比鳩魯原子論與唯物自然觀，論宇宙、靈魂、感覺、宗教恐懼之破除與死亡無懼。為現存最完整的伊比鳩魯主義文獻，文藝復興後重現，深刻影響近代唯物論、無神論論辯與基督教護教回應。' },
              { title_zh: '西塞羅《論神性》（附學園派哲學）', title_orig: 'Cicero, De Natura Deorum (On the Nature of the Gods. Academics)', author: '西塞羅（H. Rackham 英譯）', era: '約公元前 45 年', place: '羅馬', language: '拉丁文／英文對照', parent: '西塞羅哲學著作', intro: '西塞羅以對話體陳列伊比鳩魯派、斯多葛派與學園派論神之本性、神意與宇宙治理之諸說，並附學園派懷疑論認識論探討。為古代神學爭論最完整的拉丁總覽，其斯多葛自然神學論證與懷疑派詰難，被拉克坦提烏斯、奧古斯丁等教父大量徵引轉化。' },
              { title_zh: '西塞羅《論占卜》', title_orig: 'Cicero, De Divinatione (On Divination)', author: '西塞羅（W. A. Falconer 英譯）', era: '約公元前 44 年', place: '羅馬', language: '拉丁文／英文對照', parent: '西塞羅哲學著作', extent: '全 2 卷', intro: '西塞羅以兄弟對話評議占卜的真偽與理據，斯多葛派為占卜辯護、學院派則施以理性批判。其對迷信與徵兆的懷疑論析，成為早期基督教批判異教占卜、區分真啟示與迷信的重要思想武器。（亦與《論老年》《論友誼》同收於 Loeb LCL 154）' },
              { title_zh: '西塞羅《論老年‧論友誼》', title_orig: 'Cicero, De Senectute. De Amicitia (On Old Age. On Friendship)', author: '西塞羅（W. A. Falconer 英譯）', era: '公元前 44 年', place: '羅馬', language: '拉丁文／英文對照', parent: '西塞羅哲學著作', intro: '收西塞羅二篇對話：《論老年》以坦言衰老之安慰，《論友誼》論真摯友愛。二篇與《論占卜》同卷收於 Loeb LCL 154。其對友愛與生命終局的省思，為基督教論友誼、安慰與面對年老死亡提供拉丁資源。' },
              { title_zh: '西塞羅《圖斯庫盧姆論辯》', title_orig: 'Cicero, Tusculanae Disputationes (Tusculan Disputations)', author: '西塞羅', era: '約公元前 45 年', place: '羅馬共和國（圖斯庫盧姆別墅）', language: '拉丁文', parent: '西塞羅哲學著作', extent: '全 5 卷', intro: '西塞羅五卷對話，論輕死、忍痛、克制憂懼激情與德性自足以致福。融合斯多葛與柏拉圖傳統的心靈療癒之作，其論死亡與靈魂、德福一致之說，為教父（如安波羅修、奧古斯丁）論慰藉、克己與面對死亡的拉丁範本。' },
              { title_zh: '西塞羅《論至善與至惡》', title_orig: 'Cicero, De Finibus Bonorum et Malorum (On the Ends of Good and Evil)', author: '西塞羅', era: '約公元前 45 年', place: '羅馬', language: '拉丁文', parent: '西塞羅哲學著作', extent: '全 5 卷', intro: '西塞羅五卷對話，系統評述伊比鳩魯派、斯多葛派與學院派對「至善」（人生終極目的）的界定與論證，為理解希臘化倫理學的拉丁要籍。其對各派善惡標準的精審比較，是西方倫理思想史與基督教德福論的重要傳遞橋樑。' },
              { title_zh: '西塞羅《論命運》', title_orig: 'Cicero, De Fato (On Fate)', author: '西塞羅', era: '約公元前 44 年', place: '羅馬', language: '拉丁文', parent: '西塞羅哲學著作', intro: '西塞羅論命運、必然與人的自由意志之短篇（今存殘卷），析評斯多葛決定論與伊比鳩魯為保全自由而設的原子「偏斜」說，力圖在因果決定論與道德責任之間保留自由抉擇的空間。是古代自由意志與決定論之爭的核心文本，預示並滋養了奧古斯丁以降基督教關於恩典、預定與自由意志的長期爭論。' },
            ],
          },

          {
            key: 'greek', label: '希臘哲學部', label_en: 'Greek Philosophy',
            works: [
              { title_zh: '蒂邁歐篇', title_orig: 'Plato, Timaeus (Τίμαιος)', author: '柏拉圖', era: '約前 360 年', place: '希臘（雅典）', language: '古希臘文', intro: '柏拉圖晚期對話錄，借蒂邁歐之口闡述宇宙生成論：神聖工匠「巨匠造物者」（Demiurge）依永恆理型秩序，將混沌質料塑造為有靈魂、有理性的可見宇宙。其創造善神、世界靈魂與時間觀，深刻形塑斐洛、教父及中世紀的創造神學，是希臘哲學與聖經創世敘事對話的關鍵橋樑，影響直貫整個西方宇宙論傳統。' },
              { title_zh: '理想國', title_orig: 'Plato, Republic (Πολιτεία)', author: '柏拉圖', era: '約前 375 年', place: '希臘（雅典）', language: '古希臘文', intro: '柏拉圖最宏偉的對話錄，藉探討「正義」建構理想城邦，並提出洞穴喻、線段喻與善的理型（至善）學說，論靈魂三分與哲學王統治。其「善的理型」作為一切存有與可知性之源的構想，被新柏拉圖主義與教父神學吸收為理解至高神的哲學語彙，對後世一神論形上學與政治神學影響深遠。' },
              { title_zh: '形上學', title_orig: 'Aristotle, Metaphysics (Τὰ μετὰ τὰ φυσικά)', author: '亞里斯多德', era: '約前 4 世紀後期', place: '希臘（雅典）', language: '古希臘文', intro: '亞里斯多德論「作為存有的存有」的奠基之作，探討實體、本質、潛能與實現，並在第十二卷論證一位作為「不動的推動者」（第一因、純粹現實）的至高神。此「不動的推動者」概念經阿拉伯與經院哲學中介，成為基督教證明神存在與闡述神之單純性、永恆性的核心哲學資源，是自然神學的根本源頭。' },
              { title_zh: '九章集', title_orig: 'Plotinus, Enneads (Ἐννεάδες)', author: '普羅提諾', era: '約 3 世紀（約 254–270 年成篇）', place: '羅馬帝國（羅馬）', language: '古希臘文', intro: '新柏拉圖主義開山之作，由弟子波菲利編為六組九篇（故名「九章」）。論超越一切、不可言說的「太一」流溢出「智性」與「靈魂」三本體，及靈魂藉淨化默觀回歸太一的上升之路。其否定神學、流溢說與神祕合一思想，深刻塑造奧古斯丁、託名狄奧尼修斯與整個基督教神祕主義傳統。' },
              { title_zh: '愛比克泰德語錄（附手冊）', title_orig: 'Epictetus, Discourses & Encheiridion (Διατριβαί / Ἐγχειρίδιον)', author: '愛比克泰德（弟子阿里安筆錄）', era: '約 2 世紀初（約 108 年後）', place: '羅馬帝國（尼科波利斯）', language: '古希臘文', intro: '出身奴隸的斯多葛大師愛比克泰德之講授，由弟子阿里安筆錄。教人辨明「在我能力之內者」與「不在我能力之內者」，唯求內在意志的自由與順服宇宙理性（邏各斯/天命）。其對天命順服、良心自省與普世弟兄之愛的強調，與早期基督教倫理高度共鳴，《手冊》更成為後世修道與靈修的箴言典範。' },
              { title_zh: '沉思錄（馬可·奧理略）', title_orig: 'Marcus Aurelius, Meditations (Τὰ εἰς ἑαυτόν)', author: '馬可‧奧理略', era: '約 2 世紀後期（約 170–180 年）', place: '羅馬帝國（多瑙河前線等地）', language: '古希臘文', intro: '羅馬皇帝兼斯多葛哲人馬可‧奧理略寫給自己的省思札記，原題《致我自己》。以希臘文記錄面對權位、無常與死亡時的自律、克己與順應宇宙理性之道，反覆默想萬物流轉、人皆同源於普世理性。其內省的靈性日記體與道德嚴肅性，被視為異教智慧逼近基督教虔敬的最高峰之一。' },
            ],
          },
          {
            key: 'roman', label: '羅馬哲學部', label_en: 'Roman Philosophy',
            works: [
              { title_zh: '論神性', title_orig: 'Cicero, De Natura Deorum (On the Nature of the Gods)', author: '西塞羅', era: '前 45 年', place: '羅馬共和國（羅馬）', language: '拉丁文', intro: '西塞羅以對話體呈現伊壁鳩魯派、斯多葛派與學園懷疑派三方對神之存在、本性與天命護佑的論辯。書中斯多葛派的宇宙目的論與「設計論」證明，及對神性、天命的哲學分析，成為後世自然神學與護教學（如拉克坦提烏、米努修）論證神存在的重要古典範本，是異教神學思辨的拉丁集大成之作。' },
            ],
          },
        ],
      },
      wai: { divisions: [] },
    },
    {
      key: 'xuandao',
      name: '宣道藏',
      name_en: 'Proclamation (Antecedents)',
      glyph: '宣',
      genres: '勸諭',
      summary: '古代勸諭與宗教宣講文獻（待續搜羅）。',
      soleCanonLabel: '前藏',
      zheng: {
        divisions: [

        ],
      },
      wai: { divisions: [] },
    },
    {
      key: 'shuxin',
      name: '書函藏',
      name_en: 'Letters (Antecedents)',
      glyph: '函',
      genres: '書簡',
      summary: '古代哲人以書信形式傳遞的道德與靈性教導，是書信體靈修傳統的先聲。',
      soleCanonLabel: '前藏',
      zheng: {
        divisions: [
          {
            key: 'letters', label: '哲人書簡部', label_en: 'Philosophers Letters',
            works: [
              { title_zh: '道德書信集', title_orig: 'Seneca, Epistulae Morales ad Lucilium (Moral Epistles)', author: '塞內加', era: '約 62–65 年', place: '羅馬帝國（羅馬／坎帕尼亞）', language: '拉丁文', intro: '斯多葛哲人塞內加致友人盧基利烏斯的一百二十四封道德書信，論德行、死亡、時間、良心與內在自由，文風親切而充滿格言。其對良心自省、捨棄外物、神內住人心的論述與基督教倫理高度相通，致教父耶柔米將其列入聖徒名錄，後世更偽造《保羅致塞內加書》以攀附之，足見其與早期信仰的深厚淵源。' },
            ],
          },
        ],
      },
      wai: { divisions: [] },
    },
    {
      key: 'liyi',
      name: '禮儀藏',
      name_en: 'Liturgy (Antecedents)',
      glyph: '儀',
      genres: '禮儀‧喪葬',
      summary: '古代的喪葬與祭祀禮儀文獻，以咒文與儀軌導引亡者與神聖界相通，是宗教禮儀想像的母體。',
      soleCanonLabel: '前藏',
      zheng: {
        divisions: [
          {
            key: 'funerary', label: '喪葬禮儀部', label_en: 'Funerary Liturgy',
            works: [
              { title_zh: '亡靈書（阿尼紙草本）', title_orig: 'Book of the Dead — Papyrus of Ani', author: '佚名（為底比斯書記阿尼編製）', era: '約前 1250 年（新王國第十九王朝）', place: '埃及底比斯', language: '古埃及文（聖書體草書）', intro: '古埃及最著名的喪葬文獻抄本，為底比斯書記阿尼及其妻所製的紙草卷，長約 24 公尺，集咒語、禱文與彩繪插圖於一身，引導亡者通過冥界審判。其「秤心」場景——以亡者之心對瑪特女神羽毛稱量、否認四十二罪的「消極懺悔」——是後世末日審判、良心檢省觀念的古老母體。大英博物館藏品編號 EA 10470，1888 年於阿尼墓出土。' },
              { title_zh: '金字塔銘文', title_orig: 'Pyramid Texts', author: '佚名（祭司編纂）', era: '古王國第五至第八王朝（約前 2400–前 2300 年起）', place: '古埃及（薩卡拉金字塔）', language: '古埃及文', intro: '現存最古老的古埃及宗教文獻，刻於古王國末期金字塔內壁，是專為法老來世復活與升天而設的咒語、祈禱與儀式集。內容環繞國王死後與諸神（尤其奧西里斯與拉）合一、登天成神的主題，是後世棺槨銘文與《亡靈書》的源頭。其升天、復活與神人關係的想像，構成埃及來世信仰最深的根基。' },
            ],
          },
        ],
      },
      wai: { divisions: [] },
    },
    {
      key: 'shiwen',
      name: '詩藝藏',
      name_en: 'Poetry and Arts (Antecedents)',
      glyph: '詩',
      genres: '頌詩‧智慧‧文學',
      summary: '古代的頌神詩、智慧訓誨與文學經典，與希伯來詩篇、箴言遙相呼應，是宗教詩藝與智慧傳統的母體。',
      soleCanonLabel: '前藏',
      zheng: {
        divisions: [
          {
            key: 'wisdom', label: '智慧訓誨部', label_en: 'Wisdom Instructions',
            works: [
              { title_zh: '亞希夸書', title_orig: 'Story of Ahiqar', author: '佚名', era: '亞述（前 7 世紀）', place: '亞述／埃及（象島）', language: '亞蘭文', intro: '前七世紀亞述宮廷背景的亞蘭文智慧傳奇，今存最早抄本出於埃及象島的猶太屯墾區。全篇敘述國王重臣、智者亞希夸遭養子陷害卻終獲昭雪的宮廷陰謀故事，並穿插大量箴言式的處世與道德教訓。它是近東最古老的智慧文學之一，後為猶太《多比傳》明文吸收歸化，又流傳於敘利亞、亞美尼亞、阿拉伯等多語傳統，見證以色列智慧傳統與更廣大的近東文化母體之間的深厚淵源。', link: '/apocrypha' },
              { title_zh: '普塔霍特普箴言', title_orig: 'The Instruction of the Vizier Ptah-hotep', author: '傳為宰相普塔霍特普', era: '古王國末至中王國（約前 24–20 世紀）', place: '埃及', language: '古埃及文（聖書體／僧侶體）', intro: '今存最古老的埃及「訓誨文學」（sebayt）之一，託名老宰相普塔霍特普向繼任之子傳授處世之道。內容含謙遜、節制言語、敬上恤下、慎防婦人與貪婪等格言，以父誡子的體裁鋪陳。其形式與主題與希伯來《箴言》的「我兒，要聽」訓誨高度同源，是近東智慧傳統的奠基之作。' },
              { title_zh: '阿門內摩培訓誨', title_orig: 'Instruction of Amenemope', author: '傳為書記阿門內摩培（Amenemope son of Kanakht）', era: '約前 1300–1075 年（新王國拉美西斯時代）', place: '埃及底比斯', language: '古埃及文（僧侶體）', intro: '以三十章格言寫成的埃及智慧文學，勸人謙遜、節制、慷慨與誠實，戒驕傲、欺詐與偽證。學界公認《箴言》22:17–24:22「智慧人言語三十條」與本篇有直接文本淵源，部分經文近乎逐字承襲，是希伯來智慧傳統汲取埃及母體的關鍵見證。大英博物館藏最完整抄本，編號 EA 10474。' },
            ],
          },
          {
            key: 'hymn', label: '頌詩部', label_en: 'Hymns',
            works: [
              { title_zh: '阿頓大頌詩', title_orig: 'Great Hymn to the Aten', author: '傳為法老阿肯那頓（或其廷臣，存於廷臣阿伊之墓）', era: '第十八王朝阿瑪納時代（約前 14 世紀中葉）', place: '古埃及阿瑪納（阿肯塔頓）', language: '古埃及文', intro: '阿瑪納時代崇奉唯一日盤神阿頓的長篇頌詩，傳為推行一神崇拜改革的法老阿肯那頓所作，刻於廷臣阿伊墓中。詩中讚頌阿頓為萬物的獨一創造與維繫者，日昇日落、生靈作息皆由其賜。學者每將其與《詩篇》第 104 篇並比，視為近東一神論與創造頌歌傳統的先聲，被譽為前荷馬世界最壯麗的詩篇之一。' },
              { title_zh: '奧西里斯大頌詩（阿門摩斯石碑）', title_orig: 'Great Hymn to Osiris — Stele of Amenmose (Louvre C 286)', author: '佚名（奉獻者為阿蒙牧群總管伊門摩斯）', era: '約前 1550–1295 年（新王國第十八王朝）', place: '埃及', language: '古埃及文（聖書體）', intro: '刻於石灰岩石碑上的二十八行頌詩，是現存最完整、最早明確敘述奧西里斯神話的埃及文本：神王遇害、伊西斯尋夫復起、何露斯繼位申冤。死而復生、由義子昭雪的主題，構成古近東救贖與復活想像的重要母體，學者常以之與基督教復活神學對照。羅浮宮藏品編號 C 286。' },
              { title_zh: '智慧之主的讚歌（義人受苦之詩）', title_orig: 'Ludlul bēl nēmeqi ("I Will Praise the Lord of Wisdom")', author: '傳託舒布希‧馬什拉‧沙坎（Šubši-mašrâ-Šakkan）', era: '約前 14–13 世紀（卡西特時期，王 Nazi-Maruttaš 在位約前 1307–1282）成書，前 7 世紀抄本', place: '巴比倫尼亞／抄本出尼尼微', language: '阿卡德文（楔形文字）', intro: '被稱為「巴比倫的約伯記」的智慧詩篇，敘述一位虔敬貴族無故遭神離棄、染惡疾、眾叛親離，呼喊神義何在，終蒙馬爾杜克垂憐復原。它與《約伯記》同樣處理「義人為何受苦」的神義論難題，是希伯來智慧文學探討苦難主題的近東先聲。大英博物館藏亞述巴尼拔圖書館多份抄本。' },
            ],
          },
          {
            key: 'pastoral', label: '田園詩部', label_en: 'Pastoral Poetry',
            works: [
              { title_zh: '牧歌（含第四牧歌）', title_orig: 'Virgil, Eclogues (Bucolica), incl. Eclogue IV', author: '維吉爾', era: '約前 42–前 38 年', place: '羅馬共和國（義大利）', language: '拉丁文', intro: '維吉爾十首田園牧歌，其中〈第四牧歌〉預言一名神童降生、開啟黃金時代與大地復和，自古代晚期起即被基督徒（如君士坦丁、奧古斯丁）讀為對基督降生的異教預言，維吉爾因而被尊為「不自覺的先知」。此詩是異教文學被納入救恩史框架、塑造中世紀維吉爾崇拜的關鍵文本。' },
            ],
          },
        ],
      },
      wai: { divisions: [] },
    },
    {
      key: 'yijiao',
      name: '譯校藏',
      name_en: 'Translation (Antecedents)',
      glyph: '譯',
      genres: '譯本‧校勘',
      summary: '古代文本跨語言的翻譯與傳抄（待續搜羅）。',
      soleCanonLabel: '前藏',
      zheng: {
        divisions: [

        ],
      },
      wai: { divisions: [] },
    },
    {
      key: 'shizhuan',
      name: '史傳藏',
      name_en: 'History (Antecedents)',
      glyph: '史',
      genres: '史銘',
      summary: '古代王室銘文與史傳，記述帝王功業與政權更迭，其中不乏與聖經歷史交涉者。',
      soleCanonLabel: '前藏',
      zheng: {
        divisions: [
          {
            key: 'inscription', label: '王銘部', label_en: 'Royal Inscriptions',
            works: [
              { title_zh: '居魯士圓柱', title_orig: 'Cyrus Cylinder (BM 90920)', author: '波斯王居魯士二世（奉其名所頒）', era: '前 539 年後（征服巴比倫）', place: '巴比倫', language: '阿卡德文巴比倫方言（楔形文字）', intro: '圓柱形黏土文書，記居魯士征服巴比倫、推翻納波尼度後頒佈的詔令：修復神廟、遣返被擄民族歸鄉、容許各族敬奉己神。被譽為最早的「人權宣言」之一，與《以斯拉記》《以賽亞書》所載居魯士准猶太人歸回重建聖殿的記述互相印證，是波斯啟示母體影響聖經救恩史的關鍵物證。大英博物館藏，編號 BM 90920（1880,0617.1941）。' },
            ],
          },
        ],
      },
      wai: { divisions: [] },
    },
    {
      key: 'leishu',
      name: '類書藏',
      name_en: 'Reference (Antecedents)',
      glyph: '類',
      genres: '彙編',
      summary: '古代的彙編、辭書與占驗類文獻（待續搜羅）。',
      soleCanonLabel: '前藏',
      zheng: {
        divisions: [

        ],
      },
      wai: { divisions: [] },
    },
  ],
}

// 十藏定稿順序（user 2026-06-16，word-2 最後結論）：經‧律‧論‧宣‧函‧儀‧詩‧譯‧史‧類。
// 各時代資料檔內部可任意排列；此處統一依 CANON_ORDER 重排，作為全站顯示順序的單一真相。
export const CANON_ORDER = ['jing', 'lu', 'lun', 'xuandao', 'shuxin', 'liyi', 'shiwen', 'yijiao', 'shizhuan', 'leishu']

function orderCollections(era: DazangEra): DazangEra {
  return {
    ...era,
    collections: [...era.collections].sort(
      (a, b) => CANON_ORDER.indexOf(a.key) - CANON_ORDER.indexOf(b.key),
    ),
  }
}

export const ERAS: DazangEra[] = [
  PRE_CHRISTIAN_ERA,
  ANCIENT_ERA,
  MEDIEVAL_ERA,
  EARLY_MODERN_ERA,
  MODERN_ERA,
].map(orderCollections)

export function findEra(key: string): DazangEra | undefined {
  return ERAS.find(e => e.key === key)
}
