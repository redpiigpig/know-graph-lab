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
