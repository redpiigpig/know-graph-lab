import type { DazangEra } from './types'

// 近代基督教大藏經（按時代精神：人文主義‧宗教改革‧反改革‧宣教擴張‧敬虔與啟蒙）
export const EARLY_MODERN_ERA: DazangEra = {
  key: 'early-modern',
  name: '近代基督教大藏經',
  name_en: 'Early Modern Christian Canon',
  glyph: '近',
  subtitle: '人文主義‧宗教改革‧反改革‧宣教擴張‧敬虔與啟蒙',
  boundary: '按時代精神斷代——與人文主義、宗教改革相關者即近代：約 1500（宗教改革）至 1900（普世合一運動前夕）。',
  enabled: true,
  collections: [
    {
  key: 'jing',
  name: '經藏',
  name_en: 'Scripture Pitaka',
  glyph: '經',
  genres: '譯本‧校勘‧外經',
  summary: '近代基督教大藏經之經藏，收近代聖經譯本、經文校勘與新興一神教啟示經典。承文藝復興人文主義「回到原典」(ad fontes) 精神，伊拉斯謨重編希臘文新約，宗教改革各語譯本使聖經走入民間，近代校勘學奠定文本批判基礎；外經部則收摩門教與巴哈伊教等近代新啟示經典。',
  portal: { to: '/scripture', label: '聖經閱讀器' },
  zheng: {
    summary: '正經部收近代各語聖經譯本與經文校勘成果。自伊拉斯謨 1516 年希臘文新約問世，宗教改革者以民族語言翻譯聖經，天主教亦推出杜埃-蘭斯譯本回應；十八世紀經文校勘學興起，為現代聖經文本研究立下根基。',
    divisions: [
      {
        key: 'yuandian',
        label: '原典校勘部',
        label_en: 'Critical Editions of the Original',
        desc: '回到希臘文原典的人文主義校勘成果。',
        works: [
          { title_zh: '新工具(伊拉斯謨希臘文新約)', title_orig: 'Novum Instrumentum omne', author: '伊拉斯謨(Erasmus)', era: '1516', place: '巴塞爾', language: '希臘文‧拉丁文', intro: '荷蘭人文主義者伊拉斯謨編訂的第一部印行希臘文新約，希臘文與其新拉丁譯文並列。承「回到原典」精神，欲以原文校正當時通行的武加大拉丁本之訛誤。雖底本晚出、〈啟示錄〉末節曾回譯自拉丁文而留下瑕疵，卻成為後世「公認經文」(Textus Receptus) 之源頭，路德與丁道爾翻譯時皆據此而譯，影響整個宗教改革時代的聖經翻譯。', link: '/scripture' }
        ]
      },
      {
        key: 'minyu',
        label: '民族語譯本部',
        label_en: 'Vernacular Translations',
        desc: '宗教改革使聖經以各民族語言走入家庭。',
        works: [
          { title_zh: '路德德文聖經', title_orig: 'Biblia, das ist die gantze Heilige Schrifft Deudsch', author: '馬丁‧路德(Martin Luther)', era: '1522新約／1534全書', place: '威登堡', language: '德文', intro: '路德據伊拉斯謨希臘文新約與希伯來文舊約譯成的德文聖經，1522 年先出新約，1534 年全書完成。他主張「望著平民百姓的口」而譯，以中部高地德語為基準，文字生動流暢，不僅使德國平民得以自讀聖經，更奠定現代標準德語的基礎，是宗教改革「唯獨聖經」原則的具體成果。', link: '/scripture' },
          { title_zh: '丁道爾英譯聖經', title_orig: 'The New Testament (Tyndale)', author: '威廉‧丁道爾(William Tyndale)', era: '1526新約', place: '沃姆斯／安特衛普', language: '英文', intro: '丁道爾據希臘文與希伯來文原典譯成的英文聖經，是第一部直接由原文譯出並付印的英文新約。他立志要使「扶犁的農夫」也比神職人員更懂聖經，因觸怒當局而流亡歐陸印行，1536 年被處火刑。其譯文簡潔有力，許多名句為後來欽定本所沿用，被譽為英文聖經之父。', link: '/scripture' },
          { title_zh: '欽定本聖經', title_orig: 'The Holy Bible (King James Version)', author: '英王詹姆士一世詔命譯經委員會', era: '1611', place: '倫敦', language: '英文', intro: '英王詹姆士一世詔命約五十位學者分組翻譯的英文聖經官方版本，1611 年出版。譯者廣納丁道爾以降的英譯傳統，文辭莊重典雅、音韻鏗鏘，三百餘年間為英語世界教會公用標準本，對英語文學與語言影響深遠，至今仍被視為英文散文的典範之一。', link: '/scripture' },
          { title_zh: '杜埃-蘭斯聖經', title_orig: 'The Holie Bible (Douay-Rheims)', author: '英格蘭學院流亡學者(主筆 Gregory Martin)', era: '1582新約／1609-10舊約', place: '蘭斯／杜埃', language: '英文', intro: '流亡歐陸的英格蘭天主教學者所譯的英文聖經，新約 1582 年於蘭斯、舊約 1609-10 年於杜埃出版。為回應新教各譯本，譯者以武加大拉丁本為底本，務求忠實貼近教會傳統用語，保留大量拉丁化詞彙。是英語天主教界長期通用的標準譯本，與欽定本分立於新舊教兩大傳統。', link: '/scripture' },
          { title_zh: '神天聖書', title_orig: '神天聖書', author: '馬禮遜(Robert Morrison)‧米憐(William Milne)', era: '1823', place: '麻六甲', language: '中文(文言)', intro: '英國倫敦會傳教士馬禮遜與米憐合譯的第一部完整中文聖經，1823 年於麻六甲刊行，共二十一卷。馬禮遜 1807 年來華，在嚴禁傳教的處境下苦學中文、編纂華英字典並譯經。譯文為文言體，雖艱深古奧，卻開啟基督教聖經漢譯之先河，為日後和合本等中文譯本鋪路。', link: '/scripture' }
        ]
      },
      {
        key: 'jiaokan',
        label: '近代校勘部',
        label_en: 'Modern Textual Criticism',
        desc: '十八世紀興起的聖經文本批判學。',
        works: [
          { title_zh: '米爾希臘文新約', title_orig: 'Novum Testamentum Graecum, cum lectionibus variantibus', author: '約翰‧米爾(John Mill)', era: '1707', place: '牛津', language: '希臘文', intro: '牛津學者米爾窮三十年之力編成的希臘文新約校勘本，1707 年出版。他遍蒐當時可得的抄本、古譯本與教父引文，整理出約三萬處異文附於正文之下。雖正文仍沿用公認經文，但其龐大的異文資料首度向世人揭示新約傳抄歷史之複雜，被視為近代聖經文本批判學的奠基之作。' },
          { title_zh: '本格爾希臘文新約', title_orig: 'Novum Testamentum Graecum', author: '本格爾(Johann Albrecht Bengel)', era: '1734', place: '圖賓根', language: '希臘文', intro: '德國敬虔派學者本格爾編訂的希臘文新約校勘本，1734 年出版。他首倡將抄本分門別類、依「較難讀法為原」(lectio difficilior potior) 等原則評斷異文優劣，並以符號標示讀法可信度，奠定文本批判的方法學基礎。本格爾兼具敬虔信仰與嚴謹學術，其《新約釋義》亦影響深遠，被尊為近代聖經校勘學之父之一。' }
        ]
      }
    ]
  },
  wai: {
    summary: '外經部收近代興起之新一神教所奉的新啟示經典。十九世紀北美與中東先後出現摩門教與巴哈伊教，二者皆自承領受新的神聖啟示，編成獨立於聖經之外的經典體系，反映近代宗教在傳統之外另闢啟示泉源的時代現象。',
    divisions: [
      {
        key: 'mormon',
        label: '後期聖徒經典部',
        label_en: 'Latter-day Saint Scriptures',
        desc: '十九世紀北美摩門教運動的新啟示經典。',
        works: [
          { title_zh: '摩門經', title_orig: 'The Book of Mormon', author: '小約瑟‧斯密譯述(Joseph Smith Jr.)', era: '1830', place: '美國紐約州', language: '英文', intro: '摩門教創始人約瑟‧斯密所譯述刊行的經典，1830 年出版。據其自述，乃由天使引導取得的金頁片以「神聖之力」譯成，記述古代以色列一支渡海至美洲、後與復活基督相遇的歷史與教訓。摩門教奉其與聖經並列為經典，視為「耶穌基督的另一部約書」，是後期聖徒運動的核心文獻。' },
          { title_zh: '教義和聖約', title_orig: 'Doctrine and Covenants', author: '小約瑟‧斯密等(Joseph Smith Jr. et al.)', era: '1835', place: '美國俄亥俄州嘉德蘭', language: '英文', intro: '摩門教標準經典之一，1835 年首次彙編出版。內容為約瑟‧斯密及後繼教會領袖所宣稱領受的一系列現代啟示與訓諭，涉及教會組織、聖職、教義與末世等主題。與其他摩門經典不同，本書收錄的多是教會建立過程中的「當代啟示」，後續仍有增補，反映摩門教持續啟示的信念。' },
          { title_zh: '無價珍珠', title_orig: 'The Pearl of Great Price', author: '小約瑟‧斯密(Joseph Smith Jr.)', era: '1851', place: '英國利物浦', language: '英文', intro: '摩門教標準經典之一，1851 年於英國首次彙編。內容包括約瑟‧斯密對〈創世記〉與〈馬太福音〉的修訂、所謂《摩西書》與《亞伯拉罕書》、斯密自傳及教會信條。篇幅雖短卻收錄摩門教多項獨特教義來源，如先存靈魂、多重天界等，是理解摩門神學的重要文獻。' }
        ]
      },
      {
        key: 'bahai',
        label: '巴哈伊經典部',
        label_en: 'Baha\'i Scriptures',
        desc: '十九世紀波斯興起的巴哈伊教啟示經典。',
        works: [
          { title_zh: '亞格達斯經(至聖之書)', title_orig: 'Kitab-i-Aqdas', author: '巴哈歐拉(Baha\'u\'llah)', era: '約1873', place: '鄂圖曼帝國阿卡', language: '阿拉伯文', intro: '巴哈伊教創始人巴哈歐拉所著的根本律法書，約成於 1873 年流放阿卡期間。被尊為巴哈伊教「至聖之書」，內容涵蓋宗教義務、社會法度、教會組織與倫理訓誡，奠定信仰的律法架構。巴哈歐拉自承為神所應許的新時代使者，本書即其啟示的法典核心，是巴哈伊教最重要的經典。' },
          { title_zh: '篤信經(伊乾書)', title_orig: 'Kitab-i-Iqan', author: '巴哈歐拉(Baha\'u\'llah)', era: '約1861', place: '鄂圖曼帝國巴格達', language: '波斯文', intro: '巴哈歐拉約於 1861 年在巴格達寫成的教義性著作，被視為巴哈伊教最重要的神學經典。書中闡釋漸進啟示的觀念，主張歷代先知皆為同一真神在不同時代的使者，並重新詮釋聖經與古蘭經中的末世預言。文辭兼具論理與靈性，為巴哈伊信仰的教義基礎奠定理論框架。' },
          { title_zh: '隱言經(寶藏言)', title_orig: 'The Hidden Words', author: '巴哈歐拉(Baha\'u\'llah)', era: '約1858', place: '鄂圖曼帝國巴格達', language: '阿拉伯文‧波斯文', intro: '巴哈歐拉約於 1858 年在巴格達寫成的箴言體靈修經典，分阿拉伯文與波斯文兩部分，凝煉歷代宗教倫理精華為簡短格言。巴哈歐拉自言此乃「往昔啟示之精義」以新衣呈現，篇章簡短而意旨深遠，論及人神關係、德行與靈魂歸宿，是巴哈伊教徒日常默想誦讀的核心靈修文獻。' }
        ]
      }
    ]
  }
},
    {
  key: 'lu',
  name: '律藏',
  name_en: 'Discipline Pitaka',
  glyph: '律',
  genres: '會議‧信條‧法典',
  summary: '近代基督教大藏經之律藏，收近代大公會議決議、新教各派信條與教會章程，及新興宗教與啟蒙世俗政權的宗教法度。宗教改革使基督教分裂為眾多宗派，各以信條界定信仰、以章程規範體制；天主教則以特利騰大公會議重整教規回應改革；啟蒙時代更生出政教關係的世俗立法。',
  zheng: {
    summary: '正經部收近代天主教大公會議與教廷法度、新教各派信條，及各宗派教會治理章程。特利騰大公會議奠定反改革時代的天主教規制，新教則以奧斯堡、西敏等信條確立各自正統，教會章程則規範長老、公理、衛理諸制的運作。',
    divisions: [
      {
        key: 'gonghui',
        label: '大公會議與教廷部',
        label_en: 'Councils and the Holy See',
        desc: '反改革時代天主教的會議決議與教廷法度。',
        works: [
          { title_zh: '特利騰大公會議文獻', title_orig: 'Canones et Decreta Concilii Tridentini', author: '特利騰大公會議', era: '1545-1563', place: '特利騰(特倫托)', language: '拉丁文', intro: '天主教為回應宗教改革而召開的大公會議，斷續歷時十八年。會議重申聖傳與聖經並重、七件聖事、煉獄與善功等教義，駁斥新教主張，並整頓神職紀律、設立修院制度。其決議奠定此後四百年天主教信仰與規制的基礎，開啟反改革(天主教改革)時代，是近代天主教最關鍵的會議。', link: '/creeds' },
          { title_zh: '梵蒂岡第一屆大公會議文獻', title_orig: 'Constitutiones Dogmaticae Concilii Vaticani', author: '梵蒂岡第一屆大公會議', era: '1869-1870', place: '羅馬', language: '拉丁文', intro: '教宗庇護九世召開的大公會議，1869 年開議，因普法戰爭爆發於 1870 年中斷。會議通過《信仰憲章》闡明信仰與理性關係，並通過《永恆牧者》憲章，正式定斷教宗於信仰道德事務上「從寶座發言」時的不謬權。教宗無謬論引發部分天主教徒分立出舊天主教會，是近代天主教教權發展的關鍵里程碑。', link: '/creeds' },
          { title_zh: '禁書目錄', title_orig: 'Index Librorum Prohibitorum', author: '羅馬教廷', era: '1559首版', place: '羅馬', language: '拉丁文', intro: '羅馬教廷頒布的禁讀書籍清單，1559 年由教宗保祿四世首度公布，後迭經增訂。旨在保護信徒免受異端與有害思想侵擾，列入大量新教著作、哲學與科學作品。反映反改革時代教會對思想與出版的管控，亦折射近代思想與教權的張力，至 1966 年方廢止。' }
        ]
      },
      {
        key: 'xintiao',
        label: '新教信條部',
        label_en: 'Protestant Confessions',
        desc: '宗教改革各宗派界定信仰的信條與要理問答。',
        works: [
          { title_zh: '奧斯堡信條', title_orig: 'Confessio Augustana', author: '墨蘭頓(Philipp Melanchthon)', era: '1530', place: '奧斯堡', language: '拉丁文‧德文', intro: '由墨蘭頓起草、路德派諸侯於 1530 年奧斯堡帝國議會上呈交皇帝的信仰宣言，是路德宗最根本的信條。全文二十八條，前半闡明因信稱義等核心教義，後半列舉所欲革除的教會弊端。語氣力求溫和、尋求與天主教和解，卻成為路德宗正統的奠基文獻，奠定信義宗教會的信仰標準。', link: '/creeds' },
          { title_zh: '協同書', title_orig: 'Konkordienbuch (Liber Concordiae)', author: '路德宗神學家群', era: '1580', place: '德勒斯登', language: '德文‧拉丁文', intro: '路德宗信條的權威匯編，1580 年出版，收錄三大公教會信經、奧斯堡信條及其辯護、施馬加登信條、路德大小要理問答與《協同信條》。旨在平息路德逝世後派內的教義紛爭，統一信義宗的信仰標準。是路德宗教會最完整的信條集成，至今仍為信義宗正統的準繩。', link: '/creeds' },
          { title_zh: '海德堡要理問答', title_orig: 'Heidelberger Katechismus', author: '烏爾西努斯(Zacharias Ursinus)‧奧勒維亞努斯(Caspar Olevianus)', era: '1563', place: '海德堡', language: '德文', intro: '應普法爾茨選侯腓特烈三世之命編成的改革宗要理問答，1563 年於海德堡頒布。全書一百二十九問答，按「人的愁苦、得救、感恩」三部分編排，文字溫暖虔敬、兼融路德與加爾文傳統。是改革宗最廣為傳誦的要理問答之一，被荷蘭、德國等地改革宗教會普遍採用。', link: '/creeds' },
          { title_zh: '比利時信條', title_orig: 'Confessio Belgica', author: '德布雷(Guido de Bres)', era: '1561', place: '低地諸國', language: '法文', intro: '由殉道者德布雷起草的改革宗信條，1561 年成文，為低地諸國改革宗教會的信仰宣言。全文三十七條，系統闡述三一神、聖經、教會與聖禮等教義，文辭懇切，兼有向當局申辯信仰之意。與海德堡要理問答、多特信經並列為改革宗「合一三準則」，是荷蘭改革宗教會的信仰基石。', link: '/creeds' },
          { title_zh: '多特信經', title_orig: 'Canones Synodi Dordrechtanae', author: '多特會議', era: '1618-1619', place: '多特勒支', language: '拉丁文', intro: '荷蘭改革宗於多特勒支召開的全國會議所訂信經，1618-19 年針對亞米念派的爭議而發。會議駁斥亞米念派五點主張，確立加爾文主義「五要點」(全然敗壞、無條件揀選、限定救贖、不可抗拒的恩典、聖徒堅忍)。是改革宗預定論的權威表述，與比利時信條、海德堡要理問答合稱合一三準則。', link: '/creeds' },
          { title_zh: '西敏信條', title_orig: 'The Westminster Confession of Faith', author: '西敏會議', era: '1646', place: '倫敦西敏', language: '英文', intro: '英國國會召集的西敏會議所訂改革宗信條，1646 年完成。全文三十三章，系統嚴密地闡述聖經、神的預旨、揀選、稱義、教會與聖禮諸教義，是改革宗信條中結構最完備者。雖在英格蘭未獲長久施行，卻成為蘇格蘭長老會及全球長老宗教會的信仰標準，影響深遠。', link: '/creeds' },
          { title_zh: '西敏大小要理問答', title_orig: 'The Westminster Larger and Shorter Catechisms', author: '西敏會議', era: '1647', place: '倫敦西敏', language: '英文', intro: '西敏會議繼信條之後編成的兩部要理問答，1647 年完成。大要理問答詳盡，供講道教導之用；小要理問答簡明，供兒童信徒記誦，首問「人生的首要目的」答「榮耀神，並以祂為樂，直到永遠」傳誦至今。二者與西敏信條同為長老宗教會的信仰準則。', link: '/creeds' },
          { title_zh: '三十九條', title_orig: 'The Thirty-Nine Articles of Religion', author: '英格蘭教會', era: '1571', place: '倫敦', language: '英文‧拉丁文', intro: '英格蘭教會的信仰準則，1571 年由議會與教會正式確立。全文三十九條，立場介於新教與天主教之間，既肯定因信稱義、唯獨聖經等改革原則，又保留主教制與部分傳統，體現安立甘宗「中間路線」的特色。是聖公會傳統的根本信仰文件，附於《公禱書》之後通行各地。', link: '/creeds' },
          { title_zh: '衛斯理二十五條', title_orig: 'The Twenty-Five Articles of Religion', author: '約翰‧衛斯理(John Wesley)', era: '1784', place: '美國', language: '英文', intro: '約翰‧衛斯理為美國衛理公會刪訂英格蘭教會三十九條而成的信仰條款，1784 年隨美國衛理會成立而頒行。衛斯理刪去與美國處境不合及偏加爾文色彩的條目，精簡為二十四條(美國增訂為二十五條)。確立衛理宗的信仰基礎，反映亞米念主義與成聖神學的特色，是衛理公會的根本信條。', link: '/creeds' },
          { title_zh: '倫敦浸信會信條', title_orig: 'The London Baptist Confession of Faith', author: '英格蘭特定浸信會諸教會', era: '1689', place: '倫敦', language: '英文', intro: '英格蘭特定浸信會於 1689 年正式公布的信條，初稿成於 1677 年。大體沿襲西敏信條的架構與加爾文神學，唯在教會體制、洗禮與政教關係上反映浸信會立場(信而受浸、會眾自治、信仰自由)。是改革宗浸信會傳統最重要的信條，影響英美浸信會教會至今。', link: '/creeds' },
          { title_zh: '施萊特海姆信條', title_orig: 'Schleitheimer Artikel', author: '薩特勒(Michael Sattler)', era: '1527', place: '瑞士施萊特海姆', language: '德文', intro: '瑞士弟兄會(重洗派)於施萊特海姆會議通過的信條，主要由前隱修士薩特勒起草，1527 年成文。七條條款界定信而受洗、禁絕刀劍與宣誓、與世界分別、逐出犯罪者等重洗派核心主張，奠定和平主義與門徒群體的信仰路線。是重洗派最早的共同信仰文件，深刻形塑日後門諾會、哈特派等和平教會傳統。', link: '/creeds' },
          { title_zh: '蘇格蘭信條', title_orig: 'The Scots Confession', author: '諾克斯(John Knox)等六人', era: '1560', place: '愛丁堡', language: '蘇格蘭語', intro: '蘇格蘭宗教改革之初，由諾克斯為首的六位改革者四日內草成、經蘇格蘭議會批准的信條，1560 年頒行。全文二十五條，文辭熱切而帶戰鬥精神，闡明因信稱義、教會標記與聖禮教義，奠定蘇格蘭長老會的信仰基礎。施行至 1647 年西敏信條取而代之為止，是蘇格蘭改革宗最早的正式信仰宣言。', link: '/creeds' },
          { title_zh: '第二瑞士信條', title_orig: 'Confessio Helvetica Posterior', author: '布林格(Heinrich Bullinger)', era: '1566', place: '蘇黎世', language: '拉丁文', intro: '蘇黎世改革者布林格起草的改革宗信條，原為其個人信仰告白，1566 年應普法爾茨選侯之請公開發表。全文三十章，系統闡述聖經、神、預定、教會與聖禮諸教義，兼具加爾文神學的嚴整與慈運理傳統的溫和。發表後迅即為瑞士、蘇格蘭、匈牙利、波蘭等地改革宗教會接納，是流傳最廣、權威最高的改革宗信條之一。', link: '/creeds' },
          { title_zh: '多特勒支信條', title_orig: 'Dordtse Geloofsbelijdenis', author: '荷蘭門諾派眾長老', era: '1632', place: '荷蘭多特勒支', language: '荷蘭文', intro: '荷蘭門諾派眾教會於多特勒支會議通過的信條，1632 年成文，旨在統合門諾派各支派的信仰，與改革宗的《多特信經》同地異源。全文十八條，承襲施萊特海姆傳統，闡明成人洗禮、洗足禮、不抵抗(和平主義)、拒絕宣誓與對犯罪者「迴避」的規矩。為北美門諾會、阿米希派普遍採用，是門諾傳統流傳最廣的信條。', link: '/creeds' },
          { title_zh: '薩伏依宣言', title_orig: 'The Savoy Declaration', author: '英格蘭公理會諸教會', era: '1658', place: '倫敦薩伏依宮', language: '英文', intro: '英格蘭公理會(獨立派)領袖於倫敦薩伏依宮集會通過的信仰與體制宣言，1658 年成文。教義部分大體沿襲西敏信條，唯修訂教會論諸條，確立各地方教會在基督之下自主自治的公理制原則，另附教會體制綱領。是公理宗最重要的信條，與西敏信條同源而體制相異，影響英美公理會教會甚鉅。', link: '/creeds' },
          { title_zh: '真基督教神學辯護(巴克萊辯護書)', title_orig: 'An Apology for the True Christian Divinity', author: '巴克萊(Robert Barclay)', era: '1678', place: '蘇格蘭／鹿特丹', language: '拉丁文‧英文', intro: '貴格會(公誼會)神學家巴克萊為其信仰所作的系統辯護，1676 年拉丁文版、1678 年英文版問世。全書十五題，闡述「內在之光」、直接的聖靈啟示、廢除聖禮儀文與神職、反對宣誓與戰爭等貴格主張，並駁斥對貴格派的指控。貴格會本無成文信經，本書遂被奉為公誼會信仰的權威表述。', link: '/creeds' },
          { title_zh: '新罕布夏浸信會信條', title_orig: 'The New Hampshire Baptist Confession', author: '新罕布夏浸信會聯會', era: '1833', place: '美國新罕布夏', language: '英文', intro: '美國新罕布夏浸信會聯會制定的信條，1833 年通過。相較於 1689 倫敦浸信會信條的嚴格加爾文主義，本信條語調溫和、淡化預定論色彩，反映十九世紀美國浸信會的神學取向。全文簡明，廣為美南浸信會等採用，並成為後來《浸信會信仰與信息》的藍本，是美國浸信會流傳最廣的信條之一。', link: '/creeds' }
        ]
      },
      {
        key: 'zhangcheng',
        label: '教會章程部',
        label_en: 'Church Polity and Order',
        desc: '各宗派教會治理體制的章程規範。',
        works: [
          { title_zh: '教會治理形式(長老制政綱)', title_orig: 'The Form of Presbyterial Church-Government', author: '西敏會議', era: '1645', place: '倫敦西敏', language: '英文', intro: '西敏會議制定的長老制教會治理綱領，1645 年完成。規定以牧師、長老、執事分職，並設小會、區會、總會層級議會治理教會，否定主教制與會眾獨立制。是長老宗教會體制的奠基文件，與西敏信條、要理問答及《公眾敬拜指南》同為長老宗的標準文獻，確立改革宗的代議制治理傳統。' },
          { title_zh: '劍橋綱領(公理會盟約)', title_orig: 'The Cambridge Platform', author: '新英格蘭公理會諸教會', era: '1648', place: '麻薩諸塞劍橋', language: '英文', intro: '新英格蘭公理會教會於麻州劍橋會議制定的教會治理綱領，1648 年通過。在信仰上接受西敏信條，但在體制上確立會眾獨立自治的公理制：各地方教會自主、以信徒立約結成、由會眾選立職事。是北美公理宗教會體制的奠基文件，深刻影響清教徒移民社會的教會與政治傳統。' },
          { title_zh: '衛理會規程(大綱)', title_orig: 'The Large Minutes / The Book of Discipline', author: '約翰‧衛斯理(John Wesley)及衛理公會', era: '1743起編', place: '英國／美國', language: '英文', intro: '衛理公會的規程章典，源於衛斯理與同工歷年年議會問答彙編的《大綱》，後發展為美國衛理公會的《規程》。規範循道組會、班會、巡迴牧者、年議會與會督制等獨特體制，並列倫理生活準則。是衛理宗教會治理與紀律的根本文獻，將衛斯理的奮興運動制度化為有組織的教會。' }
        ]
      }
    ]
  },
  wai: {
    summary: '外經部收近代新興宗教自訂的宗教法典，與啟蒙時代政權處理政教關係的世俗立法。前者見摩門、巴哈伊等新宗教如何以法度規範教團；後者見近代國家在宗教寬容與政教分離思潮下,以世俗法令重塑信仰自由與教會地位。',
    divisions: [
      {
        key: 'xinxing',
        label: '新興宗教法典部',
        label_en: 'New Religious Legislation',
        desc: '近代新興一神教的教團法度。',
        works: [
          { title_zh: '教義和聖約(教制法度)', title_orig: 'Doctrine and Covenants (governing revelations)', author: '小約瑟‧斯密等(Joseph Smith Jr. et al.)', era: '1835', place: '美國俄亥俄州嘉德蘭', language: '英文', intro: '摩門教《教義和聖約》中規範教團組織與紀律的啟示部分。除教義內容外，本書大量篇幅以「現代啟示」形式頒定聖職層級、教會職分、什一奉獻、聚會與懲戒等制度。實為摩門教的教團法典，將約瑟‧斯密所建立的教會體制以神聖權威加以規範，是後期聖徒運動賴以組織運作的法度基礎。' },
          { title_zh: '亞格達斯經律法', title_orig: 'Kitab-i-Aqdas (laws and ordinances)', author: '巴哈歐拉(Baha\'u\'llah)', era: '約1873', place: '鄂圖曼帝國阿卡', language: '阿拉伯文', intro: '巴哈伊教《亞格達斯經》中的律法與制度部分。被尊為「至聖之書」，巴哈歐拉於其中頒定禱告、齋戒、婚姻、繼承、什一等宗教義務，並廢除舊有聖戰與神職階級，規劃「世界正義院」等行政架構。是巴哈伊教的根本法典，將巴哈歐拉的啟示落實為信仰團體的律法與治理制度。' }
        ]
      },
      {
        key: 'shisu',
        label: '啟蒙世俗法部',
        label_en: 'Enlightenment Secular Legislation',
        desc: '近代國家處理政教關係與宗教寬容的世俗立法。',
        works: [
          { title_zh: '南特敕令', title_orig: 'Edit de Nantes', author: '法王亨利四世', era: '1598', place: '法國南特', language: '法文', intro: '法王亨利四世於 1598 年頒布的敕令，結束法國數十年的宗教戰爭。敕令在維持天主教國教地位的同時，賦予新教胡格諾派信仰與部分政治、軍事權利，是近代歐洲宗教寬容的重要里程碑。然其僅為權宜的有限寬容，1685 年遭路易十四以《楓丹白露敕令》廢止，引發胡格諾派大批出逃。' },
          { title_zh: '寬容法案', title_orig: 'The Toleration Act 1689', author: '英國國會', era: '1689', place: '倫敦', language: '英文', intro: '英國光榮革命後國會通過的法案，1689 年頒行。允許不信奉國教的新教徒(不從國教者)自由聚會敬拜，但仍排除天主教徒與否認三一神者，並保留其政治權利的限制。雖屬有限度的寬容，卻是英國邁向宗教自由的重要一步，體現洛克等啟蒙思想家寬容理念對近代政教關係的影響。' },
          { title_zh: '教士民事組織法', title_orig: 'Constitution civile du clerge', author: '法國國民制憲議會', era: '1790', place: '巴黎', language: '法文', intro: '法國大革命期間國民制憲議會於 1790 年通過的法律，將天主教會徹底納入國家管轄。法令重劃教區、由人民選舉主教與本堂神父並支領國家薪俸，要求神職人員宣誓效忠。此舉切斷教會與羅馬教廷的從屬關係，造成法國教會分裂與教廷強烈反對，是近代激進政教關係重整的代表性立法。' }
        ]
      }
    ]
  }
},
    {
  key: 'lun',
  name: '論藏',
  name_en: 'Treatises',
  glyph: '論',
  genres: '論‧辯‧系統神學',
  summary: '近代基督教大藏經論藏，收一五〇〇至一九〇〇年間的系統神學、論辯與宗教哲學著作。正藏依宗教改革、反宗教改革、新教正統與敬虔、近代護教與宗教哲學分部，呈現公教與新教在恩典、意志、教會權威上的針鋒相對；外藏收自然神論、懷疑論、理性宗教、泛神論與新興宗教神學，記錄啟蒙理性對啟示信仰的解構與重構。',
  zheng: {
    summary: '近代正統論述，自路德掀起宗教改革，經墨蘭頓、加爾文系統化，至天主教特倫多反改革，再到新教正統與敬虔運動、近代護教學，構成基督宗教內部的教義主軸。',
    divisions: [
      {
        key: 'reformation-theology',
        label: '宗教改革神學部',
        label_en: 'Reformation Theology',
        desc: '路德、墨蘭頓、慈運理、加爾文等改教家奠定「唯獨恩典、唯獨信心、唯獨聖經」的新教神學基石。',
        works: [
          { title_zh: '九十五條論綱', title_orig: 'Disputatio pro declaratione virtutis indulgentiarum', author: '馬丁‧路德', era: '一五一七', place: '德意志‧維滕貝格', language: '拉丁文', intro: '路德為駁斥贖罪券買賣而貼於維滕貝格城堡教堂門上的辯論提綱，共九十五條。論綱質疑教宗赦罪權柄的範圍，主張真悔改在於內心歸向而非金錢交易，並指出贖罪券蒙蔽信徒、有害靈魂。此文一出迅速傳遍歐洲，被視為宗教改革的引爆點，將神學辯論轉為撼動整個西方教會的運動。' },
          { title_zh: '論基督徒的自由', title_orig: 'Von der Freiheit eines Christenmenschen', author: '馬丁‧路德', era: '一五二〇', place: '德意志‧維滕貝格', language: '德文', intro: '路德闡述因信稱義之核心：「基督徒是全然自由的萬物之主，不受任何人管轄；基督徒又是全然順服的萬物之僕，受一切人管轄。」前一命題講信心使人脫離律法捆綁、與基督聯合而得自由；後一命題講愛心使人甘願為鄰舍服事。全書以悖論之姿調和自由與愛，是改教時期最精煉的靈修兼神學小品。' },
          { title_zh: '論意志的捆綁', title_orig: 'De servo arbitrio', author: '馬丁‧路德', era: '一五二五', place: '德意志‧維滕貝格', language: '拉丁文', intro: '路德回應伊拉斯謨『論自由意志』之作，堅持人在救恩上意志全然被罪捆綁，毫無自主向善之力，唯靠上帝恩典與預定方能得救。路德視此書為其畢生最重要著作，徹底否定半伯拉糾式的人神合作論，將一切歸於神的主權與白白恩典，深刻影響後世改革宗的預定論發展。' },
          { title_zh: '神學要義', title_orig: 'Loci communes rerum theologicarum', author: '腓力‧墨蘭頓', era: '一五二一', place: '德意志‧維滕貝格', language: '拉丁文', intro: '墨蘭頓以羅馬書為綱所撰的首部新教系統神學，依「罪、律法、恩典」等主題分章論述，文字清晰條理嚴謹。此書是路德宗教義的首次有序整理，路德盛讚其價值。墨蘭頓以人文主義學養將改教信念體系化，奠定新教教義學的方法論基礎，數度增訂再版，影響德意志神學教育達一世紀之久。' },
          { title_zh: '六十七條結論', title_orig: 'Schlussreden', author: '慈運理', era: '一五二三', place: '瑞士‧蘇黎世', language: '德文', intro: '慈運理為蘇黎世公開辯論所擬的六十七條提綱，系統陳述其改革主張：唯獨基督為救恩之本、福音不靠教會權威而自證、否定彌撒為獻祭、反對聖徒崇拜與修道誓願。此文確立瑞士德語區改革的神學方向，慈運理的聖餐象徵論與路德的真實臨在論分歧，後於馬爾堡會談中公開,成為新教內部長期爭議之源。' },
          { title_zh: '基督教要義', title_orig: 'Institutio Christianae religionis', author: '約翰‧加爾文', era: '一五三六至一五五九', place: '瑞士‧日內瓦', language: '拉丁文', intro: '加爾文畢生增訂的新教神學鉅著，由初版六章擴至終版四卷八十章，依「認識上帝、認識救主、領受恩典、外在恩具」架構，涵蓋神論、基督論、救恩論、教會論與聖禮。書中系統闡發預定揀選、唯獨恩典與聖經權威，文筆莊嚴邏輯縝密。此書是改革宗傳統最權威的教義總綱，影響長老會、歸正宗及整個加爾文主義世界。' }
        ]
      },
      {
        key: 'counter-reformation',
        label: '反宗教改革部',
        label_en: 'Counter-Reformation',
        desc: '天主教面對新教挑戰，於特倫多會議後重整教義，由白敏、蘇亞雷斯等學者捍衛教會權威與聖統制。',
        works: [
          { title_zh: '爭辯', title_orig: 'Disputationes de controversiis Christianae fidei', author: '羅伯‧白敏', era: '一五八六至一五九三', place: '義大利‧羅馬', language: '拉丁文', intro: '耶穌會樞機白敏的反新教護教鉅著，全名『論當代異端對基督信仰之爭辯』，系統駁斥路德宗、加爾文宗在教會、聖禮、稱義、教宗權柄上的主張。白敏以淵博的教父與經院學養逐一回應，論證羅馬教會的合法性與聖統制，是反宗教改革時期最具份量的論戰巨著，長期作為天主教神學院的標準教材。' },
          { title_zh: '形上學辯論集', title_orig: 'Disputationes metaphysicae', author: '弗朗西斯科‧蘇亞雷斯', era: '一五九七', place: '西班牙‧薩拉曼卡', language: '拉丁文', intro: '耶穌會神哲學家蘇亞雷斯的形上學系統巨著，五十四篇辯論脫離亞里斯多德文本，自成體系地論述存有、本質、實體與因果。蘇亞雷斯調和湯瑪斯主義與司各脫主義，提出個體化原理與存有類比的獨到見解，是經院哲學晚期集大成之作，深刻影響後世天主教哲學乃至萊布尼茲、笛卡兒等近代哲人。' },
          { title_zh: '羅馬要理問答', title_orig: 'Catechismus Romanus', author: '特倫多會議奉命編纂', era: '一五六六', place: '義大利‧羅馬', language: '拉丁文', intro: '特倫多會議後依命編纂、教宗庇護五世頒行的天主教標準教理書，又稱『庇護五世要理問答』。全書依信經、聖事、十誡、主禱文四部分,供堂區神父講道與教導之用。內容系統陳述反改革後的天主教正統教義，文字權威而周全，是近三百年天主教要理教育的根本依據，直至當代仍具典範地位。' },
          { title_zh: '聖方濟‧沙勿略書信與訓導', title_orig: 'Epistolae S. Francisci Xaverii', author: '方濟‧沙勿略', era: '一五四二至一五五二', place: '印度‧果阿／日本', language: '拉丁文／葡萄牙文', intro: '耶穌會創始成員、東方宣教主保沙勿略在印度、東南亞與日本傳教期間的書信與教導集。書信記錄其向異教民族傳福音的策略、對在地文化的觀察、屬靈掙扎與宣教神學反省。沙勿略的書簡不僅是宣教史一手史料，更蘊含反改革時代天主教向普世擴展的傳教論述，激勵後世無數傳教士東渡。' }
        ]
      },
      {
        key: 'orthodoxy-pietism',
        label: '新教正統與敬虔部',
        label_en: 'Protestant Orthodoxy and Pietism',
        desc: '改教後新教進入經院化的正統時期，繼而興起以內心更新為重的敬虔運動與大覺醒神學。',
        works: [
          { title_zh: '神學要義', title_orig: 'Loci theologici', author: '馬丁‧契美尼茨', era: '一五九一', place: '德意志‧布倫瑞克', language: '拉丁文', intro: '路德宗正統神學家契美尼茨增訂墨蘭頓神學要義而成的系統巨著，被譽為「第二位馬丁」。書中以嚴謹的經院方法整理路德宗教義，尤精於基督論與聖餐論的闡發。契美尼茨亦著有『特倫多會議檢視』逐條駁斥天主教，並主筆協同信條,使路德宗信仰得以鞏固定型,是新教正統時期承先啟後的關鍵人物。' },
          { title_zh: '稱義的辯護', title_orig: 'The Doctrine of Justification by Faith', author: '約翰‧歐文', era: '一六七七', place: '英格蘭‧倫敦', language: '英文', intro: '清教徒神學泰斗歐文捍衛因信稱義的論著，逐一回應天主教與阿米念派對唯獨信心的質疑。歐文細密論證基督的義歸算於信徒、信心如何領受而非賺取救恩，文字嚴密思想深湛。作為清教徒神學的代表,歐文的著作將改革宗救恩論推向高峰,對英美福音派的稱義觀有深遠影響。' },
          { title_zh: '敬虔願望', title_orig: 'Pia Desideria', author: '腓力‧雅各‧施本爾', era: '一六七五', place: '德意志‧法蘭克福', language: '德文', intro: '德國敬虔運動奠基之作，施本爾針對路德宗正統過度經院化、信仰僵冷的弊病，提出六項改革建議：勤讀聖經、信徒皆祭司、基督教重在實踐、以愛代替論戰、改革神學教育、講道重在造就。此書點燃敬虔運動之火，強調重生與內心更新，深刻轉變了德意志新教的屬靈風貌,並間接催生後世宣教與福音運動。' },
          { title_zh: '新約導論與聖經註釋', title_orig: 'Beobachtungen über die ganze Heilige Schrift', author: '奧古斯特‧赫爾曼‧富蘭克', era: '一六九〇年代', place: '德意志‧哈勒', language: '德文', intro: '敬虔運動領袖富蘭克的釋經與教導著作，承施本爾之志,在哈勒大學推動以敬虔造就為本的聖經研讀。富蘭克強調讀經須伴隨重生經歷與生命實踐，反對純學術式的訓詁。他創辦孤兒院與宣教機構，將敬虔信念化為社會關懷與普世宣教的行動，其釋經著作體現信仰知行合一的敬虔精神。' },
          { title_zh: '意志的自由', title_orig: 'A Careful and Strict Enquiry into the Freedom of the Will', author: '約拿單‧愛德華茲', era: '一七五四', place: '北美‧麻薩諸塞', language: '英文', intro: '大覺醒神學家愛德華茲的哲學神學名著，論證人雖有自然的意志自由（能照所欲而行），卻無道德的自由（其欲望本身已被罪敗壞所決定）。愛德華茲以嚴密的哲學分析捍衛加爾文主義的預定與恩典,駁斥阿米念派的自由意志論。此書被譽為美洲最深刻的哲學著作之一，奠定新英格蘭神學的理論基礎。' },
          { title_zh: '宗教情感', title_orig: 'A Treatise Concerning Religious Affections', author: '約拿單‧愛德華茲', era: '一七四六', place: '北美‧麻薩諸塞', language: '英文', intro: '愛德華茲反省大覺醒復興中真假宗教經驗之作，探討何為真正出於聖靈的宗教情感。他指出真敬虔的核心在於「心被恩感而生的聖潔情感」，並提出十二項辨識真信心的標記，強調情感須伴隨意志與行為的更新。此書兼具屬靈洞察與心理分析的深度,成為福音派靈修神學的經典,至今仍被廣泛研讀。' }
        ]
      },
      {
        key: 'apologetics-philosophy',
        label: '近代護教與宗教哲學部',
        label_en: 'Modern Apologetics and Philosophy of Religion',
        desc: '面對理性主義與懷疑論挑戰，巴斯卡、巴特勒、佩利等以理性與經驗為信仰辯護，開啟近代護教學。',
        works: [
          { title_zh: '思想錄', title_orig: 'Pensées', author: '布萊茲‧巴斯卡', era: '一六七〇', place: '法蘭西‧巴黎', language: '法文', intro: '數學家兼神學家巴斯卡未竟的護教學遺稿，由後人輯為片斷集。書中剖析人性的偉大與悲慘、理性的限度與心的理由，著名的「巴斯卡賭注」論證信仰上帝在理性上仍屬明智之選。巴斯卡反對純理性的自然神學，主張唯藉耶穌基督方能認識上帝。文字警策深邃，兼具哲思與靈性，是法語護教文學不朽之作。' },
          { title_zh: '類比論', title_orig: 'The Analogy of Religion, Natural and Revealed', author: '約瑟‧巴特勒', era: '一七三六', place: '英格蘭‧倫敦', language: '英文', intro: '英國國教主教巴特勒回應自然神論之護教鉅著，主張自然界與啟示宗教之間存在類比關係：人若接受自然界的奧秘與不確定，便無理由僅因啟示有奧秘而拒之。巴特勒以蓋然性論證反駁理神論者對神蹟與啟示的質疑，論理穩健周密。此書被視為十八世紀英語護教學的最高成就,影響紐曼等後世思想家。' },
        ]
      }
    ]
  },
  wai: {
    summary: '外藏收近代啟蒙以降質疑、改造或另立啟示信仰的思想：自然神論與懷疑論瓦解傳統護教，理性宗教與泛神論重構神聖觀念，新興宗教神學則開出基督教傳統之外的新教義體系。',
    divisions: [
      {
        key: 'deism-skepticism',
        label: '自然神論與懷疑論部',
        label_en: 'Deism and Skepticism',
        desc: '啟蒙思想家以理性為尺度，否定神蹟與啟示，主張一位不干預世界的理性神，乃至懷疑宗教知識本身。',
        works: [
          { title_zh: '基督教並不神祕', title_orig: 'Christianity Not Mysterious', author: '約翰‧托蘭德', era: '一六九六', place: '英格蘭‧倫敦', language: '英文', intro: '愛爾蘭自然神論者托蘭德的代表作，主張真正的基督教不含任何超乎理性、違反理性的奧秘，凡稱「奧秘」者皆是後世神職人員的添加。托蘭德以洛克的理性主義為據，將啟示徹底理性化，否定一切無法理性解明的教義。此書點燃英國自然神論論戰，遭教會強烈譴責並公開焚燬，是理神論思潮的奠基文獻。' },
          { title_zh: '基督教與創世同其久遠', title_orig: 'Christianity as Old as the Creation', author: '馬太‧廷得爾', era: '一七三〇', place: '英格蘭‧倫敦', language: '英文', intro: '被稱為「自然神論者聖經」的著作，廷得爾主張真正的宗教是與創世同其久遠的自然宗教，福音不過是對人人皆能藉理性知曉之自然律的重申。他否定特殊啟示的必要，認為一切真理皆可由理性與自然發現。此書是英國自然神論的高峰之作，激起眾多護教回應，包括巴特勒的類比論即為駁此而作。' },
          { title_zh: '自然宗教對話錄', title_orig: 'Dialogues Concerning Natural Religion', author: '大衛‧休謨', era: '一七七九', place: '蘇格蘭‧愛丁堡', language: '英文', intro: '休謨身後出版的宗教哲學名著，藉斐羅、克里安提斯、第美亞三人對話，徹底檢視自然神學的論證。休謨假斐羅之口拆解設計論證：類比薄弱、惡的存在難解、由有限世界無法推知無限完美之神。全書論辯精彩,對自然神學的批判至今仍是宗教哲學的核心議題,深刻動搖了理性證明上帝存在的根基。' },
          { title_zh: '論神蹟', title_orig: 'Of Miracles', author: '大衛‧休謨', era: '一七四八', place: '蘇格蘭‧愛丁堡', language: '英文', intro: '休謨人類理解研究第十章,提出反對相信神蹟的著名論證：神蹟乃對自然律的違反，而證明自然律的經驗證據遠強於任何人證；故理性人永不應僅憑見證接受神蹟為真。休謨並指出宗教神蹟見證多出於輕信、激情與虛榮。此論證對啟示宗教的歷史證據構成根本挑戰，成為近代懷疑論批判信仰的經典武器。' },
          { title_zh: '哲學辭典宗教批判文選', title_orig: 'Dictionnaire philosophique', author: '伏爾泰', era: '一七六四', place: '法蘭西／瑞士', language: '法文', intro: '法國啟蒙領袖伏爾泰以辭典形式撰寫的批判文集，眾多條目尖銳抨擊教會的迷信、不寬容與教權專橫。伏爾泰並非無神論者而是自然神論者，信奉一位理性的造物主，卻痛恨建制宗教的偽善與迫害，高呼「鏟除卑鄙之物」。文筆機鋒犀利、嬉笑怒罵，是啟蒙時代反教權主義最具影響力的代表作。' },
          { title_zh: '為神的理性敬拜者辯護', title_orig: 'Apologie oder Schutzschrift für die vernünftigen Verehrer Gottes', author: '赫爾曼‧塞繆爾‧雷馬魯斯', era: '一七七四至一七七八', place: '德意志‧漢堡', language: '德文', intro: '德國自然神論者雷馬魯斯生前不敢發表、由萊辛以「沃爾芬比特爾殘篇」之名陸續刊出的批判遺稿。雷馬魯斯以理性檢視聖經，否定神蹟與啟示，指耶穌乃失敗的猶太彌賽亞、復活為門徒所編造。此書開啟近代歷史耶穌的批判研究，引發德國神學界軒然大波，被視為理性主義聖經批判的先聲。' }
        ]
      },
      {
        key: 'rational-religion-pantheism',
        label: '理性宗教與泛神論部',
        label_en: 'Rational Religion and Pantheism',
        desc: '斯賓諾莎、萊布尼茲、康德、黑格爾等哲人以理性重構神聖：或將神等同自然，或將宗教納入道德與精神的辯證體系。',
        works: [
          { title_zh: '神學政治論', title_orig: 'Tractatus Theologico-Politicus', author: '巴魯赫‧斯賓諾莎', era: '一六七〇', place: '荷蘭‧阿姆斯特丹', language: '拉丁文', intro: '斯賓諾莎匿名出版的劃時代著作，以理性批判方法考察聖經，主張聖經旨在教導順服與愛而非哲學真理，神蹟與預言當以自然解釋。書中倡言思想與信仰自由，論證國家應容許哲學探究。斯賓諾莎的泛神論將神等同於自然整體，徹底重塑神聖觀念。此書是近代聖經批判與政治自由主義的奠基文獻，當世即遭各方禁燬。' },
          { title_zh: '神義論', title_orig: 'Essais de Théodicée', author: '哥特佛萊‧萊布尼茲', era: '一七一〇', place: '德意志‧漢諾威', language: '法文', intro: '萊布尼茲探討惡之問題的哲學名著，「神義論」一詞即由此書創立。萊布尼茲論證全善全能全知的上帝必創造「一切可能世界中最好的世界」，現世之惡乃整體完善所必需的成分。他區分形上之惡、自然之惡與道德之惡，調和神的善與惡的存在。此書是理性神學處理惡的問題的經典,後遭伏爾泰於『憨第德』中辛辣諷刺。' },
          { title_zh: '單在理性界限內的宗教', title_orig: 'Die Religion innerhalb der Grenzen der bloßen Vernunft', author: '伊曼努爾‧康德', era: '一七九三', place: '普魯士‧柯尼斯堡', language: '德文', intro: '康德將宗教納入其道德哲學的綱領之作，主張宗教的本質在於道德，凡能在理性界限內辯護者方為真宗教。康德以哲學重釋根本惡、稱義與神國等基督教教義，將教會信仰還原為道德信仰，視耶穌為道德完善的典範。此書因觸怒普魯士當局而險遭查禁，是啟蒙理性宗教的最高表述，深刻影響後世自由派神學。' },
          { title_zh: '宗教哲學講演錄', title_orig: 'Vorlesungen über die Philosophie der Religion', author: '黑格爾', era: '一八二一至一八三一', place: '普魯士‧柏林', language: '德文', intro: '黑格爾在柏林大學的宗教哲學講稿，由學生筆記輯成。黑格爾視宗教為絕對精神藉表象自我認識的階段，基督教為「絕對宗教」，道成肉身與三一論象徵神人合一的辯證真理。他將基督教教義轉譯為思辨哲學的概念，主張哲學與宗教同一內容而形式有別。此書深刻影響後世神學與宗教研究，亦催生左右兩派黑格爾門徒的分裂。' }
        ]
      },
      {
        key: 'new-religious-theology',
        label: '新興宗教神學部',
        label_en: 'New Religious Theology',
        desc: '十九世紀興起於基督教傳統邊緣或之外的新宗教運動，發展出各自的啟示觀與神學體系。',
        works: [
          { title_zh: '已答之問', title_orig: 'Some Answered Questions', author: '阿博都巴哈', era: '一九〇八', place: '鄂圖曼‧阿卡', language: '波斯文', intro: '巴哈伊信仰領袖阿博都巴哈於餐桌談話中答覆西方信徒提問的輯錄，由克利福德‧巴尼夫人記錄。內容涵蓋聖經與古蘭經的詮釋、漸進啟示、靈魂與來生、進化與創造、基督與諸先知的本質等。阿博都巴哈以理性調和宗教與科學，闡發巴哈伊「諸教同源、漸進啟示」的核心教義，是該信仰最重要的教義問答著作之一。' },
          { title_zh: '教義與聖約', title_orig: 'Doctrine and Covenants', author: '約瑟‧斯密等', era: '一八三五', place: '北美‧俄亥俄／密蘇里', language: '英文', intro: '摩門教（耶穌基督後期聖徒教會）的核心經典之一，輯錄創教者約瑟‧斯密及後繼領袖所宣稱領受的啟示。內容涉及教會組織、聖職體系、聖殿教儀、永恆婚姻與救恩計畫等獨特教義。此書與摩門經、無價珍珠並列為該教標準經典，是理解摩門神學體系的關鍵文獻，反映十九世紀美國新興宗教對基督教傳統的重大改造與擴充。' }
        ]
      }
    ]
  }
},
    {
  key: 'shizhuan',
  name: '史傳藏',
  name_en: 'Histories and Biographies',
  glyph: '史',
  genres: '教史‧宣教史‧殉道',
  summary: '收近代（1500–1900）基督宗教的歷史敘事與人物傳記。自宗教改革的編年與論戰，經反改革的聖徒與殉道紀事，至天主教與新教向亞洲、美洲、非洲的宣教擴張史，並及啟蒙時代對教會史的批判重寫與新興宗教的自我歷史書寫。正藏立宗教改革史、殉道與聖徒、宣教史、教會通史四部，外藏收啟蒙批判史與新興宗教史，呈現「時代精神」如何形塑人們對基督教過去的記憶與書寫。',
  zheng: {
    summary: '以教會自身或同情立場書寫的近代基督教歷史與傳記，依宗教改革、殉道聖徒、海外宣教、教會通史四大脈絡編列。',
    divisions: [
      {
        key: 'reformation-history',
        label: '宗教改革史部',
        label_en: 'Histories of the Reformation',
        desc: '宗教改革及其後續宗教戰爭的編年與紀事，多出自新教史家之手，兼採當代見證。',
        works: [
          { title_zh: '宗教改革編年史', title_orig: 'Historia Reformationis / Commentarii de statu religionis', author: '約翰‧斯萊丹（Johann Sleidan）', era: '1555', place: '史特拉斯堡', language: '拉丁文', intro: '斯萊丹以官方史家身分，依年代逐年記述路德起事至奧格斯堡和約前夕的宗教與政治大事。全書冷靜援引帝國會議文書、諸侯往來信函與神學論戰原件，刻意以「報導」而非「辯護」自居，遂成新教陣營第一部具學術骨架的改革通史。其編年體例與檔案意識，深刻影響後世對「改革如何在帝國政治中展開」的理解，被視為宗教改革史學的奠基之作。' },
          { title_zh: '三十年戰爭宗教史', title_orig: 'Theatrum Europaeum / Geschichte des Dreißigjährigen Krieges', author: '馬特烏斯‧梅里安等（Matthäus Merian u. a.）', era: '1635–1700', place: '法蘭克福', language: '德文‧拉丁文', intro: '此編逐年記述一六一八至一六四八年間，由波希米亞擲窗事件點燃、橫掃中歐的宗教與王朝大戰。書中以新教與天主教兩陣營的攻守為主線，穿插諸侯改宗、城市圍困、瘟疫饑荒與威斯特伐利亞和議的曲折，並附大量銅版插圖。它把「信仰之爭如何淪為帝國浩劫」具體呈現，成為理解近代初期宗教暴力與宗教和平如何收場的核心史料。' },
          { title_zh: '施雷肯豪斯宗教改革記述', title_orig: 'Reformationsgeschichte', author: '弗里德里希‧施雷肯豪斯（Friedrich Schreckenhaus，託名所傳）', era: '十六世紀後期', place: '德意志', language: '德文', intro: '此編相傳出自一名路德派城市書記之手，以親歷者口吻記下某帝國自由市自彌撒被廢、修院解散到市議會接管教產的全過程。文字樸實，著重市民日常如何在講道、聖像處置與濟貧制度改組中體驗改革，較少神學論辯而多社會側寫。雖作者身分難以確證，所載市政與堂會檔案細節，使其成為觀察改革在地方落實的珍貴基層紀錄。' }
        ]
      },
      {
        key: 'martyrs-saints',
        label: '殉道與聖徒部',
        label_en: 'Martyrs and Saints',
        desc: '近代新教殉道錄與天主教反改革聖徒傳記，記信仰者受難與成聖的見證。',
        works: [
          { title_zh: '殉道者之書', title_orig: 'Acts and Monuments', author: '約翰‧福克斯（John Foxe）', era: '1563', place: '倫敦', language: '英文', intro: '福克斯這部巨著俗稱「殉道者之書」，自早期教會殉道追溯至英格蘭瑪麗一世治下被焚的新教徒，以血淚交織的個案串起一部「真教會受逼迫」的通史。書中詳載審訊對話、火刑場景與臨終遺言，並配以木刻插圖，文字煽動而動人。它塑造了英語世界的新教認同與反羅馬情緒，數百年間僅次於聖經而廣為流傳，是理解英國宗教改革集體記憶的關鍵文本。' },
          { title_zh: '反改革聖徒傳記', title_orig: 'Vitae Sanctorum / Acta Sanctorum', author: '波蘭定會（Bollandists，約翰‧博蘭德等）', era: '1643 起', place: '安特衛普', language: '拉丁文', intro: '此為耶穌會博蘭德學派啟動的浩大聖徒傳集成，按教會曆逐日蒐羅古今聖人事蹟。面對新教對聖徒崇拜的攻擊，編者一反中世紀傳奇的浮誇，力求考訂史源、辨偽存真，開創批判性聖傳學。其中收入特倫特會議後新封的反改革聖徒，如羅耀拉、沙勿略、加爾默羅會德蘭等，既見證天主教靈修的更新，也展示近代史料考證方法在教會史上的萌芽。' },
          { title_zh: '近代殉道錄', title_orig: 'Martyrologium recentius', author: '佚名輯錄（天主教傳信部所傳）', era: '十七至十八世紀', place: '羅馬', language: '拉丁文', intro: '此錄彙集近代天主教在海外宣教與歐洲宗教衝突中殉難者的事蹟，以日本、越南、北美與英倫三島為重心。文中逐一記下殉道者姓名、會籍、受刑日期與方式，並附目擊者證詞與骸骨遺物去向，體例近於封聖程序的卷宗。它不僅是敬禮資料，更保存了宣教前線遭遇本地政權鎮壓的第一手線索，為近代教難史提供具體的人物與年代座標。' }
        ]
      },
      {
        key: 'mission-history',
        label: '宣教史部',
        label_en: 'Histories of the Missions',
        desc: '記天主教與新教向中國、日本及海外各地宣教的歷程，含親歷者札記與宣道會史。',
        works: [
          { title_zh: '基督教遠征中國史', title_orig: 'De Christiana expeditione apud Sinas', author: '利瑪竇撰‧金尼閣編譯（Matteo Ricci / Nicolas Trigault）', era: '1615', place: '奧格斯堡', language: '拉丁文', intro: '此書俗稱利瑪竇「中國劄記」，由金尼閣將利氏義大利文手記譯成拉丁文並補述而成。書中既記耶穌會士習漢語、結交士大夫、以天文曆算與西學叩開明朝宮廷的「適應策略」，也以歐洲讀者陌生的眼光，細描中國的疆域、科舉、宗教與風俗。它是西方系統認識中國的開山之作，更是「文化適應宣教」路線的綱領，深刻形塑日後中西交流與禮儀之爭。' },
          { title_zh: '沙勿略書簡所載日本宣教', title_orig: 'Epistolae S. Francisci Xaverii', author: '方濟‧沙勿略（Francis Xavier）', era: '1549–1552', place: '日本‧果阿', language: '拉丁文‧葡萄牙文', intro: '沙勿略自果阿與日本寄回歐洲的書簡，是天主教進入日本最早的親歷紀錄。信中熱切描述薩摩、山口、京都之行，分析日本人尚理重榮的民族性，反省如何透過辯論與本地語彙傳講福音，也坦陳語言隔閡與佛僧敵意的挫折。這批書簡既是宣教實況報告，也是近代跨文化傳教方法的雛形，激勵大批耶穌會士東來，奠定「吉利支丹」時代的開端。' },
          { title_zh: '近代海外宣道會史', title_orig: 'History of the Modern Missionary Societies', author: '佚名輯（新教宣道會傳統）', era: '十九世紀', place: '倫敦', language: '英文', intro: '此編綜述十八世紀末以降新教宣教運動的勃興，自威廉‧克里赴印度、倫敦會與美部會的設立，到向非洲、太平洋與中國內地的拓展。書中以各差會為單元，記其成立宗旨、籌款體制、宣教士派遣與本地教會建立，並反映福音奮興與帝國擴張交織的時代氛圍。它把零散的差會報告整合為一部運動史，是理解新教全球化與近代宣教神學的入門綱要。' }
        ]
      },
      {
        key: 'general-church-history',
        label: '教會通史部',
        label_en: 'General Church Histories',
        desc: '近代學者以較完整體例書寫的基督教通史，奠定新教教會史學的方法傳統。',
        works: [
          { title_zh: '教會史', title_orig: 'Institutiones Historiae Ecclesiasticae', author: '約翰‧勞倫斯‧馮‧莫斯海姆（Johann Lorenz von Mosheim）', era: '1755', place: '哥廷根', language: '拉丁文', intro: '莫斯海姆此書被譽為近代教會史學之父的代表作，自使徒時代逐世紀敘至作者當代。他一改前人護教或論戰的筆法，主張以公正的史料批判態度處理教義演變、教制興革與異端流派，並按「外史（教會與外部關係）」與「內史（教義與生活）」雙線分述。其清晰的分期與冷靜的判斷，為日後新教與啟蒙史學樹立典範，長期作為神學院教會史教科書。' },
          { title_zh: '近代新教教會史學', title_orig: 'Geschichte der protestantischen Kirchengeschichtsschreibung', author: '佚名綜述（哥廷根—柏林學派傳統）', era: '十八至十九世紀', place: '德意志', language: '德文', intro: '此編回顧自莫斯海姆、紐安德至包爾學派，新教學界如何把教會史建構為一門批判學科。書中追溯史料考訂、教義發展史與「歷史—批判」方法如何逐步取代護教敘事，並檢視浪漫主義與黑格爾哲學對教會史分期的影響。它既是史學史，也是方法論反省，揭示近代「以歷史眼光看信仰」的思潮如何重塑人們對基督教過去的整體理解。' }
        ]
      }
    ]
  },
  wai: {
    summary: '收以啟蒙批判視角重寫基督教歷史，及新興宗教自我書寫的歷史敘事，立場與教會傳統史學相異或對立。',
    divisions: [
      {
        key: 'enlightenment-critique',
        label: '啟蒙批判史部',
        label_en: 'Enlightenment Critical Histories',
        desc: '啟蒙時代以理性懷疑立場重述基督教起源與發展的批判性歷史著作。',
        works: [
          { title_zh: '羅馬帝國衰亡史', title_orig: 'The History of the Decline and Fall of the Roman Empire', author: '愛德華‧吉本（Edward Gibbon）', era: '1776–1789', place: '倫敦', language: '英文', intro: '吉本這部六卷巨著縱論羅馬自盛轉衰、終至覆亡的千餘年歷程，而其論基督教興起的兩章最為震動。他以冷峻反諷的筆調，把教會的勝利歸因於排他熱忱、來世盼望、神蹟宣稱、嚴格倫理與組織才能五項「世俗」因素，刻意淡化神意而凸顯人為。此說激怒教界卻啟發後世，把基督教放回社會史脈絡考察，是啟蒙史學以理性解構神聖敘事的經典範例。' }
        ]
      },
      {
        key: 'new-religions-history',
        label: '新興宗教史部',
        label_en: 'Histories of New Religious Movements',
        desc: '近代源出基督教傳統的新興宗教，其自我書寫或追隨者編纂的早期歷史。',
        works: [
          { title_zh: '摩門教早期史', title_orig: 'History of the Church of Jesus Christ of Latter-day Saints', author: '約瑟‧斯密及後繼編者（Joseph Smith et al.）', era: '1830 起', place: '美國紐約‧猶他', language: '英文', intro: '此書記述後期聖徒運動自一八三○年代在紐約州創立、屢遭驅趕，終至大舉西遷鹽湖谷的曲折歷程。內容以斯密自述的異象、金頁與摩爾門經問世為核心，續記教會建制、密蘇里與伊利諾的衝突、斯密殉難及楊百翰領眾跨越大平原。作為教派的官方自我歷史，它既是信仰見證，也是觀察十九世紀美國宗教狂熱、邊疆社會與政教張力的獨特史料。' },
          { title_zh: '神臨證記', title_orig: 'God Passes By', author: '守基‧阿芬第（Shoghi Effendi）', era: '1944', place: '海法', language: '英文', intro: '此書為巴哈伊信仰護法者守基‧阿芬第為紀念其運動創立百年而撰，敘述自巴孛一八四四年在波斯宣道，經巴哈歐拉受啟與流放，至阿博都巴哈傳教西方與信仰建制初成的百年大事。作者以恢宏修辭把諸般迫害、流亡與擴展編織為「神聖計畫」逐步展現的敘事，既是教史也是神學詮釋。它確立了巴哈伊對自身起源的權威記憶，是理解這一近代新興宗教自我認同的核心文獻。' }
        ]
      }
    ]
  }
},
    {
  key: 'yijiao',
  name: '譯校藏',
  name_en: 'Canon of Translation and Textual Criticism',
  glyph: '譯',
  genres: '譯本‧校勘‧考據',
  summary: '收一五〇〇至一九〇〇年間環繞聖經文本的譯本、校勘與考據之作。自人文主義者回歸希臘原文、宗教改革家以民族語言迻譯聖經，至漢語首批譯本與近代經文考據學的奠基；外編兼收他宗教經典的歐語初譯，以及理性主義者對聖經權威的批判性釋讀，呈現近代聖經作為「被翻譯與被檢證之文本」的整體面貌。',
  portal: { to: '/scripture', label: '聖經多版本對照' },
  zheng: {
    summary: '正藏以聖經自身的翻譯與校勘為主軸，依人文主義校勘、宗教改革譯本、漢語譯本、經文考據四部排列，呈現近代教會內部對聖經文本的迻譯與精校傳統。',
    divisions: [
      {
        key: 'humanist-critical',
        label: '人文主義校勘部',
        label_en: 'Humanist Textual Criticism',
        desc: '文藝復興人文學者「回歸原典」(ad fontes)，以希臘文、希伯來文重新校訂並對照聖經文本。',
        works: [
          { title_zh: '新工具', title_orig: 'Novum Instrumentum omne', author: '伊拉斯謨 (Desiderius Erasmus)', era: '一五一六年', place: '巴塞爾', language: '希臘文‧拉丁文', intro: '伊拉斯謨刊行的首部印刷希臘文新約，希臘原文與其新譯拉丁文並列，另附詳盡校註。它打破武加大拉丁譯本的獨尊地位，主張回歸希臘原典以正視聖經本文，深刻啟發路德與丁道爾的譯經事業。其文本後經改訂，成為日後「公認本」(Textus Receptus) 的張本，是近代聖經校勘學的奠基之作。', link: '/scripture' },
          { title_zh: '康普魯頓多語對照聖經', title_orig: 'Biblia Polyglotta Complutensis', author: '希梅內斯‧德‧西斯內羅斯樞機 (Francisco Jiménez de Cisneros) 主持', era: '一五一四至一五一七年成書‧一五二二年刊行', place: '西班牙阿爾卡拉 (康普魯頓)', language: '希伯來文‧亞蘭文‧希臘文‧拉丁文', intro: '由西斯內羅斯樞機在阿爾卡拉大學召集學者編成的首部多語對照聖經。舊約以希伯來文、拉丁武加大、希臘七十士譯本三欄並陳，五經並附亞蘭文他爾根；新約則為希臘文與拉丁文對照。它開創多語逐欄對照的編排體例，雖刊行稍晚於伊拉斯謨本，校勘之精審尤為後世推崇。', link: '/scripture' },
          { title_zh: '沃爾頓多語聖經', title_orig: 'Biblia Sacra Polyglotta', author: '沃爾頓 (Brian Walton) 主編', era: '一六五七年', place: '倫敦', language: '希伯來文‧亞蘭文‧撒瑪利亞文‧希臘文‧拉丁文‧敘利亞文‧阿拉伯文‧衣索比亞文‧波斯文', intro: '沃爾頓主編的倫敦多語聖經，集當時所能蒐羅的古代譯本之大成，多達九種語言逐欄對照，並附各譯本的考訂緒論與異文。它把多語對照的規模推至空前，為比較各古譯傳統、追溯經文源流提供了浩繁的材料，是十七世紀聖經學術的巔峰之一。', link: '/scripture' }
        ]
      },
      {
        key: 'reformation-versions',
        label: '宗教改革譯本部',
        label_en: 'Reformation Vernacular Versions',
        desc: '宗教改革「聖經歸於民眾」的精神具現，各民族語言譯本相繼問世。',
        works: [
          { title_zh: '路德德文聖經', title_orig: 'Biblia, das ist die gantze Heilige Schrifft Deudsch', author: '馬丁‧路德 (Martin Luther)', era: '新約一五二二年‧全本一五三四年', place: '威登堡', language: '德文', intro: '路德直接由希臘文、希伯來文原典譯出的德文聖經，文字曉暢有力，被視為近代德語書面語的奠基。它把聖經交到一般信徒手中，落實「唯獨聖經」與信徒皆祭司的主張，不僅是宗教改革的旗幟，更深刻塑造了德意志的語言與文化認同。', link: '/scripture' },
          { title_zh: '丁道爾英譯聖經', title_orig: 'The New Testament (Tyndale)', author: '威廉‧丁道爾 (William Tyndale)', era: '新約一五二六年', place: '沃爾姆斯‧安特衛普', language: '英文', intro: '丁道爾由希臘文、希伯來文原典譯出的英文聖經，是首部據原文而非拉丁本的印刷英譯。其譯筆樸實傳神，許多措辭為日後欽定本所承襲。丁道爾因譯經觸怒當局，終遭絞殺焚屍，臨刑前祈求英王開啟子民之目，其譯本卻奠定了往後一切英語聖經的基石。', link: '/scripture' },
          { title_zh: '日內瓦聖經', title_orig: 'The Geneva Bible', author: '日內瓦英籍流亡學者群 (惠廷漢 William Whittingham 等)', era: '一五六〇年', place: '日內瓦', language: '英文', intro: '瑪利女王迫害期間流亡日內瓦的英籍新教學者所譯，是首部分節編號並附大量旁註的英文聖經。註釋帶鮮明的喀爾文派立場，輕便價廉，深受清教徒與一般家庭喜愛，隨「五月花號」傳入新大陸，在欽定本之前長期是英語世界最普及的聖經。', link: '/scripture' },
          { title_zh: '欽定本序與譯則', title_orig: 'The Holy Bible, Conteyning the Old Testament, and the New — Translators to the Reader', author: '英王詹姆士一世敕命譯經委員會', era: '一六一一年', place: '倫敦', language: '英文', intro: '詹姆士一世召集數十位學者分組譯成的英文聖經，譯時參酌原文與既有英譯，定下逐字斟酌、莊重典雅的譯則，並由斯密斯 (Miles Smith) 撰長序「致讀者」申明譯經宗旨與方法。其文體雄渾,流播三百餘年,既是英語聖經的典範,也是英語文學的瑰寶。', link: '/scripture' },
          { title_zh: '杜埃-蘭斯譯本', title_orig: 'The Holie Bible (Douay–Rheims)', author: '蘭斯與杜埃英籍天主教學院 (馬丁 Gregory Martin 主譯)', era: '新約一五八二年‧舊約一六〇九至一六一〇年', place: '蘭斯‧杜埃', language: '英文', intro: '流亡歐陸的英籍天主教學者所譯,據拉丁武加大本譯成英文,以與新教各英譯相抗衡。譯文謹守拉丁原貌,多存教會傳統用語,並附駁斥新教釋義的註解。它是天主教傳統最重要的英文聖經,後經查理納主教 (Richard Challoner) 修訂而長行於英語天主教界。', link: '/scripture' }
        ]
      },
      {
        key: 'chinese-versions',
        label: '漢語譯本部',
        label_en: 'Chinese Versions',
        desc: '聖經傳入中土的首批漢語譯本,自天主教傳教士的稿本到新教各譯。',
        works: [
          { title_zh: '白日昇譯本', title_orig: '四史攸編‧聖經', author: '白日昇 (Jean Basset)', era: '約一七〇〇至一七〇七年', place: '四川', language: '漢文', intro: '巴黎外方傳教會神父白日昇在四川所譯的新約稿本,據拉丁武加大本譯出四福音、使徒行傳與保羅書信大半,文言典雅。譯稿雖未刊行,其抄本後流入大英博物館,為馬禮遜入華譯經時所參用,是現存最早的漢語新約譯本之一,影響深遠。', link: '/scripture' },
          { title_zh: '馬殊曼譯本', title_orig: '聖經 (馬殊曼、拉撒譯)', author: '馬殊曼 (Joshua Marshman)、拉撒 (João Lassar)', era: '一八二二年', place: '印度塞蘭坡', language: '漢文', intro: '英國浸信會宣教士馬殊曼偕亞美尼亞裔華語教師拉撒,在印度塞蘭坡譯成的漢文全本聖經,刊行於一八二二年,較馬禮遜全譯略早。譯本由原文參照英譯而成,是基督新教首部刊印的漢語全本聖經,在華雖流通有限,於漢語譯經史上卻有開創之功。', link: '/scripture' },
          { title_zh: '馬禮遜神天聖書', title_orig: '神天聖書', author: '馬禮遜 (Robert Morrison)、米憐 (William Milne)', era: '一八二三年', place: '馬六甲', language: '漢文', intro: '倫敦會宣教士馬禮遜偕米憐譯成的漢文全本聖經,馬禮遜任新約與舊約大部,米憐補譯部分舊約。馬禮遜曾參用白日昇譯稿,歷時逾十五年成書。神天聖書是首位來華新教宣教士的譯經結晶,確立了多項漢語聖經用語,為日後各譯所宗。', link: '/scripture' },
          { title_zh: '委辦譯本', title_orig: '委辦譯本聖經', author: '在華新教各差會委辦委員會 (麥都思 Walter Henry Medhurst、理雅各 James Legge 等)', era: '新約一八五二年‧舊約一八五四年', place: '上海', language: '漢文', intro: '在華各新教差會聯合組成委辦委員會合譯的文言聖經,由麥都思、理雅各等通曉漢學的宣教士主筆,並延請中國文士潤飾,文辭典雅暢達。譯本因「神」「上帝」譯名之爭而生分歧,然其雅馴文體影響深遠,是十九世紀流傳最廣的文言聖經之一。', link: '/scripture' }
        ]
      },
      {
        key: 'text-criticism',
        label: '經文考據部',
        label_en: 'Principles of Textual Criticism',
        desc: '近代學者整理希臘文新約異文、確立校勘原則,奠定科學的經文考據學。',
        works: [
          { title_zh: '希臘文新約', title_orig: 'Novum Testamentum Graecum', author: '本格爾 (Johann Albrecht Bengel)', era: '一七三四年', place: '杜賓根', language: '希臘文‧拉丁文', intro: '虔敬派學者本格爾刊行的希臘文新約校勘本,首倡將異文按其可靠程度分等標示,並提出「較難之讀法為較可信」(lectio difficilior) 的著名準則。他依抄本性質分群比較,開創了系統化的經文校勘方法,被尊為近代新約經文考據學的先驅。', link: '/scripture' },
          { title_zh: '希臘文新約附異文', title_orig: 'Novum Testamentum Graecum (cum apparatu critico)', author: '米爾 (John Mill)', era: '一七〇七年', place: '牛津', language: '希臘文', intro: '牛津學者米爾窮三十年之力編成的希臘文新約,匯集約三萬處異文,旁徵眾多抄本、古譯與教父引文。雖仍沿用公認本正文,其浩繁的異文彙編首次向世人展示新約傳抄的複雜實況,激起學界對經文校勘的重視,為後世考據奠定龐大的材料基礎。', link: '/scripture' },
          { title_zh: '希臘文新約校勘原則', title_orig: 'Novum Testamentum Graece', author: '格里斯巴赫 (Johann Jakob Griesbach)', era: '一七七四至一七七五年', place: '哈勒‧耶拿', language: '希臘文', intro: '格里斯巴赫的希臘文新約,首次大膽偏離公認本,依抄本系統將見證歸為亞歷山大、西方、拜占庭三大文本類型,並訂立十五條校勘準則。他確立以抄本系譜權衡異文的方法論,是近代以前最具影響的校勘本,直接啟導了十九世紀以降的批判性新約版本。', link: '/scripture' }
        ]
      }
    ]
  },
  wai: {
    summary: '外編收近代歐洲對他宗教經典的迻譯,以及理性主義者以批判眼光重讀聖經之作,呈現翻譯與考據在教會疆界之外的延伸與挑戰。',
    divisions: [
      {
        key: 'other-religions-translation',
        label: '他宗教譯本部',
        label_en: 'Translations of Other Scriptures',
        desc: '歐洲學者首度將伊斯蘭與東方宗教經典直譯為歐語,開比較宗教文獻之先。',
        works: [
          { title_zh: '古蘭經', title_orig: 'The Koran, Commonly Called the Alcoran of Mohammed', author: '薩爾 (George Sale)', era: '一七三四年', place: '倫敦', language: '英文', intro: '英國東方學者薩爾直接由阿拉伯原文譯成的英文古蘭經,並附長篇「緒論」(Preliminary Discourse) 評介伊斯蘭的歷史與教義。譯文力求準確,態度遠較前人公允,長期是英語世界最權威的古蘭經譯本,亦為啟蒙時代歐洲認識伊斯蘭的主要窗口,影響極為深遠。' },
          { title_zh: '東方宗教經典初譯', title_orig: 'Oupnek\'hat (Anquetil-Duperron) 等', author: '安克蒂爾-杜佩龍 (Abraham Hyacinthe Anquetil-Duperron) 等', era: '十八世紀末', place: '巴黎', language: '拉丁文‧法文', intro: '安克蒂爾-杜佩龍率先將祆教《阿維斯陀》與印度《奧義書》(由波斯文轉譯) 介紹入歐,其拉丁文《奧義書》譯本曾深深觸動叔本華。此類東方經典的初譯篳路藍縷、訛誤難免,卻打開了歐洲認識亞洲宗教的門徑,催生了十九世紀比較宗教與東方學的勃興。' }
        ]
      },
      {
        key: 'rationalist-exegesis',
        label: '理性主義釋經部',
        label_en: 'Rationalist Biblical Criticism',
        desc: '啟蒙思想家以理性與歷史眼光檢視聖經,動搖其神聖權威的傳統根基。',
        works: [
          { title_zh: '殘篇', title_orig: 'Fragmente eines Ungenannten (Wolfenbütteler Fragmente)', author: '雷馬魯斯 (Hermann Samuel Reimarus)', era: '一七七四至一七七八年遺稿刊行', place: '漢堡‧渥爾芬比特爾', language: '德文', intro: '漢堡學者雷馬魯斯生前秘不示人的遺稿,由萊辛以無名氏「殘篇」之名陸續刊布。文中以理性論駁神蹟與復活,區分歷史上的耶穌與門徒所傳的基督,直指福音乃門徒所造。其說掀起軒然大波,被視為「歷史耶穌的探尋」之濫觴,深刻轉變了近代福音書研究的方向。' }
        ]
      }
    ]
  }
},
    {
  key: 'shuxin',
  name: '書信藏',
  name_en: 'Canon of Epistles and Encyclicals',
  glyph: '函',
  genres: '牧函‧通諭‧宣教書簡',
  summary: '收一五〇〇至一九〇〇年間以書信體寫成的教會文獻。自宗教改革家的論辯與牧養書信、宣教士遠寄歐洲的東方見聞,至近代教宗頒行的通諭詔書;外編兼收新興宗教向各國君主的公開信,與啟蒙思想家假書信體所發的宗教批判。書信體以其私密、即時與懇切,最能映照近代基督宗教在改革、宣教與啟蒙激盪下的內心圖景。',
  zheng: {
    summary: '正藏依書信的功能與發信者身分,分改革家書信、宣教書簡、教宗通諭三部,呈現近代教會內部由人到人、由牧到群的文字往還。',
    divisions: [
      {
        key: 'reformer-letters',
        label: '改革家書信部',
        label_en: 'Letters of the Reformers',
        desc: '宗教改革領袖往來論辯、牧養與勸勉的書信,既是神學交鋒,也是屬靈情誼的見證。',
        works: [
          { title_zh: '路德書信集', title_orig: 'Luthers Briefe', author: '馬丁‧路德 (Martin Luther)', era: '一五〇〇年代至一五四六年', place: '威登堡', language: '德文‧拉丁文', intro: '路德一生所遺數千封書信的彙編,對象遍及諸侯、同道、友人與家人。其中既有針砭時弊、闡發教義的論戰之筆,也有撫慰患難、教養子女的溫厚之言。書信坦率熱烈,喜怒形於辭色,既補正其神學著作,更鮮活呈現這位改革家的性情與信仰歷程,是理解宗教改革不可或缺的第一手文獻。' },
          { title_zh: '加爾文書信集', title_orig: 'Calvini Epistolae', author: '約翰‧加爾文 (John Calvin)', era: '一五三〇年代至一五六四年', place: '日內瓦', language: '拉丁文‧法文', intro: '加爾文與歐洲各地改革者、君侯及受逼迫信徒往還的書信彙編。他藉書信指導各地教會、調停爭端、堅固殉道者之心,影響遠及法、英、蘇格蘭與東歐。文字謹嚴而懇切,既是改革宗網絡得以維繫的紐帶,也展露這位日內瓦改革家牧者的一面,為其神學體系增添血肉。' },
          { title_zh: '慈運理書信', title_orig: 'Zwinglis Briefwechsel', author: '烏爾里希‧慈運理 (Huldrych Zwingli)', era: '一五一〇年代至一五三一年', place: '蘇黎世', language: '拉丁文‧德文', intro: '蘇黎世改革家慈運理與人文學者、同道及各方政要往來的書信。內容涉及聖餐之爭、與路德的歧見、瑞士諸邦的宗教與政局。書信兼具人文素養與改革熱忱,既見其與伊拉斯謨等學人的淵源,也記錄了瑞士德語區改革的曲折,是研究改革陣營內部分合的重要見證。' }
        ]
      },
      {
        key: 'mission-letters',
        label: '宣教書簡部',
        label_en: 'Missionary Correspondence',
        desc: '宣教士自東方遠寄歐洲的書簡,既傳教情,也報異域風土,溝通東西。',
        works: [
          { title_zh: '沙勿略書簡', title_orig: 'Epistolae S. Francisci Xaverii', author: '方濟‧沙勿略 (Francis Xavier)', era: '一五四〇年代至一五五二年', place: '印度果阿‧日本', language: '葡萄牙文‧拉丁文', intro: '耶穌會「東方使徒」沙勿略自印度、馬六甲、日本寄回歐洲的書簡。信中熱切報告東亞傳教的艱辛與盼望,描繪當地民情風俗,並籲求歐洲教會增派人手。其書簡傳誦一時,激起無數青年投身海外宣教,既是天主教近代海外傳教的開篇,也是歐洲認識東亞的早期重要文獻。' },
          { title_zh: '利瑪竇書信', title_orig: 'Opere storiche del P. Matteo Ricci', author: '利瑪竇 (Matteo Ricci)', era: '一五八〇年代至一六一〇年', place: '中國肇慶‧南京‧北京', language: '義大利文‧拉丁文', intro: '耶穌會士利瑪竇在華期間寄回歐洲的書信,詳述其學習漢語、結交士大夫、以學術傳教的「適應」策略,並記錄明末中國的政教風土。書信坦陳傳教的困頓與權宜,是理解利瑪竇路線與明末中西交流的核心史料,與其漢文著述互為表裡,影響後世耶穌會在華事業甚鉅。' },
          { title_zh: '中國書簡集', title_orig: 'Lettres édifiantes et curieuses, écrites des missions étrangères', author: '在華耶穌會士群', era: '一七〇二至一七七六年陸續刊行', place: '巴黎', language: '法文', intro: '法國耶穌會編刊的海外宣教書簡集,其中關於中國者尤為大宗。在華傳教士以書信詳述中國的政制、科學、曆算、禮俗與宗教,內容博洽。此集風行歐洲,既為傳教募資,也成為啟蒙時代歐人想像「中華帝國」的主要來源,深刻塑造了萊布尼茲、伏爾泰等人的中國觀。' },
          { title_zh: '近代宣教士家書', title_orig: 'Letters and Journals of Protestant Missionaries', author: '近代新教宣教士群 (馬禮遜、克理 William Carey 等)', era: '十八世紀末至十九世紀', place: '中國‧印度‧南洋', language: '英文', intro: '近代新教宣教運動興起後,馬禮遜、克理等宣教士寄回母會與家人的書信日誌。信中既述異域傳教的孤苦與成果,也記錄當地語言、社會與信仰,並向母會報告需用、籲求代禱。這些家書多經宣教刊物刊布,既維繫差會與工場的聯繫,也激勵後繼者,是近代新教海外宣教的鮮活記錄。' }
        ]
      },
      {
        key: 'papal-encyclicals',
        label: '教宗通諭部',
        label_en: 'Papal Encyclicals and Bulls',
        desc: '近代教宗以詔書、通諭向普世教會頒行的訓導與裁定。',
        works: [
          { title_zh: '主的羔羊', title_orig: 'Unigenitus Dei Filius', author: '教宗克勉十一世 (Clemens PP. XI)', era: '一七一三年', place: '羅馬', language: '拉丁文', intro: '教宗克勉十一世頒行的詔書,譴責楊森派神學家奎內爾 (Pasquier Quesnel) 著作中一〇一條命題,涉及恩寵、得救與閱讀聖經等爭議。此詔在法國引發長達數十年的楊森派之爭,撕裂教會與王室,牽動高盧主義與教廷權威之辯,是近代天主教內部最重大的教義紛爭之一,影響法國宗教政局至深。', link: '/encyclicals' },
          { title_zh: '上主的牧者', title_orig: 'Dominus ac Redemptor', author: '教宗克勉十四世 (Clemens PP. XIV)', era: '一七七三年', place: '羅馬', language: '拉丁文', intro: '教宗克勉十四世迫於歐洲諸天主教王室壓力而頒的詔書,下令解散耶穌會。此舉終結了該會二百餘年的全球事業,海外傳教與教育網絡為之中斷,中國禮儀之爭後本已受挫的在華傳教更形凋零。直至一八一四年方由庇護七世復會,此詔成為近代天主教史上最具爭議的決定之一。', link: '/encyclicals' },
          { title_zh: '永恆之父', title_orig: 'Aeterni Patris', author: '教宗良十三世 (Leo PP. XIII)', era: '一八七九年', place: '羅馬', language: '拉丁文', intro: '教宗良十三世頒行的通諭,號召復興聖多瑪斯‧阿奎那的士林哲學,以為信仰與理性、教會與近代學術對話的根基。此諭開啟了新士林主義 (新多瑪斯主義) 的興盛,深刻塑造了二十世紀天主教的哲學與神學教育,是近代教廷回應理性主義與世俗思潮的關鍵文獻。', link: '/encyclicals' }
        ]
      }
    ]
  },
  wai: {
    summary: '外編收教會疆界之外、以書信體發聲的文獻:新興宗教向列國君主的公開召喚,與啟蒙思想家假書信批判宗教之作。',
    divisions: [
      {
        key: 'new-religion-letters',
        label: '新興宗教公開信部',
        label_en: 'Open Letters of New Religious Movements',
        desc: '近代新興宗教創教者向各國君主與教界領袖頒發的公開信與召喚。',
        works: [
          { title_zh: '萬軍之主的召喚', title_orig: 'Súriy-i-Mulúk (Tablet to the Kings)', author: '巴哈歐拉 (Bahá\'u\'lláh)', era: '一八六〇年代至一八七〇年代', place: '阿德里安堡‧阿卡', language: '阿拉伯文‧波斯文', intro: '巴哈伊信仰創立者巴哈歐拉自流放地向當世列王頒發的書簡,致函包括教宗庇護九世、法皇拿破崙三世、英女王維多利亞、波斯與鄂圖曼君主等。信中宣告自身的啟示使命,呼籲諸王止戰修和、扶助公義。這些「致君王書」是巴哈伊教義的核心文獻,以書信體向全球權柄宣示其普世和平與宗教合一的理想。' },
          { title_zh: '史密書信', title_orig: 'Letters of Joseph Smith', author: '約瑟‧史密 (Joseph Smith)', era: '一八三〇年代至一八四四年', place: '美國', language: '英文', intro: '摩門教 (耶穌基督後期聖徒教會) 創立者約瑟‧史密致教會、信徒及政要的書信。其中既有教會組織與教義指示,也有自獄中寫予聖徒、勉其堅忍患難的懇切之言。這些書信部分被收入摩門教典《教義和聖約》,既是其教會草創史的見證,也展現這一近代美國本土新興宗教的信仰與處境。' }
        ]
      },
      {
        key: 'enlightenment-letters',
        label: '啟蒙書簡部',
        label_en: 'Letters of the Enlightenment',
        desc: '啟蒙思想家假書信體針砭宗教、鼓吹寬容與理性的批判之作。',
        works: [
          { title_zh: '哲學書簡', title_orig: 'Lettres philosophiques', author: '伏爾泰 (Voltaire)', era: '一七三四年', place: '巴黎‧倫敦', language: '法文', intro: '伏爾泰旅英後以書信體寫成之作,藉評介英國的政教、科學與思想,反襯法國的專制與教會的褊狹。書中盛讚貴格會的簡樸與英國的宗教寬容,暗諷天主教會的迷信與不容異己。此書甫出即遭查禁焚毀,卻流播甚廣,成為啟蒙運動批判宗教權威、鼓吹寬容理性的旗幟之作。' }
        ]
      }
    ]
  }
},
    {
  key: 'liyi',
  name: '禮儀藏',
  name_en: 'The Liturgy Canon',
  glyph: '儀',
  genres: '公禱‧彌撒‧聖詩集',
  summary: '收一五〇〇至一九〇〇年間基督宗教各傳統的崇拜禮文與聖樂典籍。正藏分新教禮儀、反改革禮儀、聖樂與聖詩集三部，呈現宗教改革後公禱書、彌撒經書與崇拜程序如何在不同教會中定型；外藏錄新興宗教與民間祕儀的儀軌，旁及共濟會等結社禮文。所收皆為塑造近代信眾敬拜生活的核心文本，藉以見禮儀如何承載教義、規範會眾、凝聚群體。',
  zheng: {
    summary: '新教與天主教在宗教改革後各自整飭崇拜禮文，並以聖樂相輔。本部三分而觀其全：改教者重訂母語崇拜，特利騰會議統一羅馬禮，作曲家則以詩篇與受難曲將神學化為聲音。',
    divisions: [
      {
        key: 'protestant_liturgy',
        label: '新教禮儀部',
        label_en: 'Protestant Liturgy',
        desc: '宗教改革各宗派以母語重訂的公禱、崇拜與聖事禮文，廢拉丁彌撒而立會眾可懂的敬拜秩序。',
        works: [
          { title_zh: '公禱書', title_orig: 'The Book of Common Prayer', author: '克蘭麥（Thomas Cranmer）等', era: '一五四九／一六六二年', place: '英格蘭', language: '英文', intro: '英格蘭教會的崇拜定本，克蘭麥主導以典雅英文整合中世紀多種禮書，一五四九年初版、一五五二年大幅改訂、一六六二年成為法定通行版。內含晨禱晚禱、聖餐、洗禮、堅振、婚喪、按立等全套禮文，並附詩篇與書信福音經課表。其節奏優美的禱詞深刻塑造英語崇拜語感與聖公宗認同，影響遍及全球安立甘群體，是新教禮儀文獻中流傳最廣、文學成就最高者之一。' },
          { title_zh: '日內瓦崇拜程序', title_orig: 'La Forme des prières et chants ecclésiastiques', author: '加爾文（Jean Calvin）', era: '一五四二年', place: '日內瓦', language: '法文', intro: '加爾文為日內瓦改革宗教會所訂的崇拜禮文，確立以宣道、認罪、代禱與會眾齊唱韻文詩篇為核心的簡樸敬拜形態。其崇拜觀力求回歸聖經，去除被視為人為的儀節，強調神言居中、會眾參與。此程序成為歐陸與蘇格蘭長老制崇拜的範式，奠定改革宗「以神之道規範敬拜」的原則，後世清教徒崇拜傳統多由此衍生。' },
          { title_zh: '德意志彌撒', title_orig: 'Deutsche Messe und Ordnung Gottesdiensts', author: '路德（Martin Luther）', era: '一五二六年', place: '威登堡', language: '德文', intro: '路德為德語會眾編訂的母語崇拜禮，繼一五二三年拉丁《彌撒程式》之後再進一步，將禮文與經課改以德文舉行，並大量採會眾唱詩取代神職獨誦。路德保留彌撒架構而剔除被視為違背因信稱義的獻祭觀念，使聖餐成為領受恩典之宴。此禮為信義宗崇拜定調，亦開啟新教會眾聖詩傳統，影響後世德語敬拜深遠。' },
          { title_zh: '公眾崇拜指南', title_orig: 'A Directory for the Public Worship of God', author: '西敏會議（Westminster Assembly）', era: '一六四五年', place: '倫敦／西敏', language: '英文', intro: '英國長老派與清教徒於內戰期間制訂，意在取代《公禱書》的崇拜準則。不提供逐字禱文，而以指引方式規範崇拜各環節，主張禱告當出於牧者帶領、依聖經精神自由發揮，反對固定誦文與被視為人為的儀節。內容涵蓋讀經、講道、聖禮、婚喪等。此指南體現清教徒崇拜的「規範原則」，深刻影響蘇格蘭與北美長老宗及公理宗的敬拜形態。' },
        ],
      },
      {
        key: 'counter_reformation_liturgy',
        label: '反改革禮儀部',
        label_en: 'Counter-Reformation Liturgy',
        desc: '特利騰會議後羅馬天主教統一頒行的彌撒、日課與聖事禮典，確立四百年通行的特倫多禮。',
        works: [
          { title_zh: '羅馬彌撒經書', title_orig: 'Missale Romanum', author: '教宗庇護五世（Pius V）頒行', era: '一五七〇年', place: '羅馬', language: '拉丁文', intro: '特利騰會議授權、教宗庇護五世以《Quo primum》詔書頒行的羅馬天主教彌撒定本，統一了西方拉丁禮的彌撒舉行方式，史稱特倫多彌撒。經書詳載每日彌撒的禱文、經課、儀節與禮規，廢止諸多地方禮而立羅馬禮為通則。此本歷經數次小幅修訂沿用近四百年至一九六二年，是反改革時期天主教禮儀統一的核心成果，象徵教會面對新教挑戰的制度回應。' },
          { title_zh: '羅馬日課經', title_orig: 'Breviarium Romanum', author: '教宗庇護五世（Pius V）頒行', era: '一五六八年', place: '羅馬', language: '拉丁文', intro: '特利騰改革後庇護五世頒行的天主教時辰祈禱定本，規範神職與修會每日七時辰的誦經、聖詠、讀經與禱文。日課以聖詠貫穿一週、配合教會年曆與聖人紀念，是神職人員的法定祈禱義務。此本整理繁雜的中世紀傳統,使全教會時辰祈禱趨於一致，與《羅馬彌撒經書》並為特倫多禮的兩大支柱，維繫了近代天主教靈修生活的節律與統一。' },
          { title_zh: '羅馬聖事禮典', title_orig: 'Rituale Romanum', author: '教宗保祿五世（Paul V）頒行', era: '一六一四年', place: '羅馬', language: '拉丁文', intro: '保祿五世頒行的天主教司鐸禮儀手冊，匯集彌撒與日課之外的各項聖事與祝福禮文，含洗禮、告解、病人傅油、婚配、葬禮、驅魔及各類降福。相較彌撒經書,此典更貼近堂區牧靈日常，為司鐸施行聖事提供統一範本。它補全了特倫多禮儀體系的最後一環，使天主教自生到死的禮儀照顧全面標準化，沿用至梵二前，影響近代天主教牧養實務甚鉅。' },
        ],
      },
      {
        key: 'sacred_music',
        label: '聖樂與聖詩集部',
        label_en: 'Sacred Music & Psalters',
        desc: '以詩篇韻文與大型聲樂作品承載禮儀的聖樂典籍,自會眾齊唱詩篇至受難曲與神劇。',
        works: [
          { title_zh: '日內瓦詩篇', title_orig: 'Psautier de Genève', author: '馬羅（Clément Marot）、貝扎（Théodore de Bèze）詞，布爾喬亞（Louis Bourgeois）等曲', era: '一五六二年', place: '日內瓦', language: '法文', intro: '加爾文倡導、由馬羅與貝扎韻譯全部一百五十篇詩篇、布爾喬亞等配以樸實旋律的會眾詩篇集,一五六二年成全本。其曲調莊重易唱，專為改革宗強調的會眾齊唱而作，去除複音與樂器，力求人人同聲頌讚。此詩篇集風行歐陸法語、荷語及蘇格蘭改革宗教會，成為改革宗崇拜音樂的典範與身分標記，其旋律亦廣為後世聖詩沿用。' },
          { title_zh: '馬太受難曲', title_orig: 'Matthäus-Passion BWV 244', author: '巴赫（Johann Sebastian Bach）', era: '一七二七年', place: '萊比錫', language: '德文', intro: '巴赫為路德宗受難週崇拜所譜的大型受難曲，以馬太福音耶穌受難敘事為本，融合福音史詠唱、會眾聖詠、詠嘆調與合唱，編制達雙合唱團與雙管弦樂。作品在萊比錫聖多馬教會受難節禮拜中演出，將聖經敘事、信徒默想與會眾參與熔於一爐,既是禮儀亦是藝術。其深沉的神學默想與恢宏結構,被推為西方宗教音樂巔峰，亦代表路德宗將音樂奉為事奉的傳統。', note: '此處以《馬太受難曲》為巴赫受難曲與清唱劇之代表，其《約翰受難曲》及眾多教會清唱劇同屬此一禮儀聖樂體系。' },
          { title_zh: '彌賽亞', title_orig: 'Messiah HWV 56', author: '韓德爾（George Frideric Handel）', era: '一七四一年', place: '倫敦／都柏林', language: '英文', intro: '韓德爾以英文聖經經文（由詹寧斯編選）譜成的神劇，分預言降生、受難救贖、復活得勝三部，串起基督救恩全貌。一七四二年於都柏林首演，其中哈利路亞大合唱尤為傳世名篇。雖屬音樂廳神劇而非教堂禮儀，卻深植於新教崇拜文化，常於將臨節與復活節演出,成為英語世界最具代表性的宗教聲樂作品，以恢宏合唱頌揚救主，影響後世聖樂與會眾敬拜想像甚深。' },
        ],
      },
    ],
  },
  wai: {
    summary: '正統教會體制之外的儀軌：十九世紀新興宗教自創聖殿與聖日禮儀，民間結社則發展出帶神祕色彩的入會儀式。收錄以見近代宗教想像如何在主流之外另闢禮儀體系。',
    divisions: [
      {
        key: 'new_religious_movements_liturgy',
        label: '新興宗教禮儀部',
        label_en: 'New Religious Movements Liturgy',
        desc: '十九世紀興起的新宗教所創設的聖殿、聖日與祈禱禮儀，自摩門聖殿恩道門至巴哈伊聖日。',
        works: [
          { title_zh: '聖殿恩道門儀式', title_orig: 'The Endowment', author: '史密斯（Joseph Smith）創設', era: '一八四二年起', place: '美國納府（Nauvoo）', language: '英文', intro: '耶穌基督後期聖徒教會（摩門教）於聖殿中舉行的核心儀式，由創始人史密斯於納府時期確立。恩道門以戲劇化敘事重演創造、墮落與救贖,授予信徒誓約、聖衣與通往高升的知識，並含洗禮代死等為亡者施行的代理聖禮。儀式僅於聖殿內、對符合資格者保密舉行,構成摩門救恩觀的關鍵環節。此禮體現新興宗教自創完整聖殿禮儀體系,在新教文化中另立一格的特殊性。' },
          { title_zh: '巴哈伊祈禱與聖日', title_orig: "Bahá'í Prayers and Holy Days", author: '巴哈歐拉（Bahá’u’lláh）、阿博都巴哈（‘Abdu’l-Bahá）', era: '十九世紀後半', place: '波斯／鄂圖曼領地', language: '阿拉伯文／波斯文', intro: '巴哈伊信仰由巴哈歐拉創立，其祈禱文與聖日構成信徒靈修與群體生活的禮儀核心。每日有義務祈禱、十九日靈宴會,並訂九個工作停止的聖日,多紀念巴孛與巴哈歐拉的生平要事；信徒亦守十九日齋戒。禮儀強調人神直接相通、無神職階級、各宗教合一,反映其普世主義精神。此一禮儀體系見證十九世紀近東新興宗教如何融合伊斯蘭傳統與普世理想,另創敬拜形態。', note: '巴哈伊源出伊斯蘭文化圈，因其與亞伯拉罕諸教及十九世紀宗教更新潮流相涉,列為近代宗教禮儀之外藏旁系。' },
        ],
      },
      {
        key: 'folk_esoteric_liturgy',
        label: '民間與祕儀部',
        label_en: 'Folk & Esoteric Rites',
        desc: '正統教會之外的結社入會與祕傳儀軌，多帶象徵性戲劇與誓約色彩。',
        works: [
          { title_zh: '共濟會儀軌', title_orig: 'Masonic Ritual', author: '不著撰人（會所傳承）', era: '十八至十九世紀定型', place: '英格蘭／歐洲', language: '英文等', intro: '近代共濟會所行的入會與升級儀式,以石匠工藝為象徵,藉戲劇化的入門、晉級程序傳遞道德與哲理教誨。儀軌含誓約、暗號、隱喻性問答及對至高存有的泛稱性祈求,各會所雖有差異而結構相通。其文本多口傳兼祕傳,十八世紀後漸有印本流出。共濟會雖非宗教而具濃厚禮儀色彩,曾與教會關係緊張並屢遭天主教譴責。收錄以見近代民間結社祕儀如何借宗教語彙建構自身禮儀傳統。', note: '共濟會自稱非宗教團體,其儀軌作者向以會所集體傳承形式存在,無單一著者。' },
        ],
      },
    ],
  },
},
    {
  key: 'shiwen',
  name: '詩文藏',
  name_en: 'The Poetry & Letters Canon',
  glyph: '詩',
  genres: '聖詩‧史詩‧寓言文學',
  summary: '收一五〇〇至一九〇〇年間以詩歌、史詩與寓言承載信仰的文學典籍。正藏分聖詩、宗教史詩與文學、神祕與默想詩三部,自會眾傳唱的聖詩,到彌爾頓的恢宏史詩、班揚的天路寓言,再到神祕主義者的默想詩篇,呈現近代基督教如何藉文學想像表達救恩、罪愆與靈魂與神的契合；外藏錄新興宗教詩文與啟蒙時代的哲理詩,以見宗教情感在主流之外與新思潮中的多樣表達。',
  zheng: {
    summary: '近代基督教文學的三大脈絡：可唱頌的聖詩貼近會眾敬拜,史詩與寓言以宏大敘事鋪陳救恩,神祕與默想詩則向內探索靈魂與神的幽微契合。三者共構信仰的文學想像。',
    divisions: [
      {
        key: 'hymns',
        label: '聖詩部',
        label_en: 'Hymns',
        desc: '供會眾傳唱的信仰詩歌,自宗教改革的德語聖詠到英語福音聖詩的黃金時代。',
        works: [
          { title_zh: '上主是我堅固保障', title_orig: 'Ein feste Burg ist unser Gott', author: '路德（Martin Luther）', era: '約一五二九年', place: '威登堡', language: '德文', intro: '路德取材詩篇第四十六篇所作的聖詩,被譽為宗教改革的戰歌。詞曲皆出路德之手,以堅城為喻歌頌神在患難中的庇護與終必得勝的信心,字句剛健、旋律雄渾,深契改教者面對逼迫的處境。此詩成為信義宗精神的象徵,海涅稱之為改革的馬賽曲,後世譯為各國語言廣為傳唱,亦為巴赫等作曲家所引用,是新教聖詩史上最具代表性與影響力的作品之一。' },
          { title_zh: '瓦茨聖詩', title_orig: 'Hymns and Spiritual Songs / The Psalms of David Imitated', author: '瓦茨（Isaac Watts）', era: '一七〇七／一七一九年', place: '英格蘭', language: '英文', intro: '英國公理宗牧師瓦茨被尊為英語聖詩之父,他突破當時僅唱韻文詩篇的傳統,自由創作以福音為內容的聖詩,並將詩篇以基督教觀點重寫。代表作含「普世歡騰」「當我思量奇妙十架」等傳世名篇,文字清暢、情感真摯。瓦茨開啟英語聖詩創作的大門,使會眾頌唱不再侷限於舊約詩篇,深刻改變新教崇拜音樂的面貌,後世衛斯理等聖詩作者皆承其遺緒。', note: '瓦茨聖詩散見其《聖詩與靈歌》及《大衛詩篇仿作》二集,合為其聖詩成就之代表。' },
          { title_zh: '查理‧衛斯理聖詩', title_orig: 'Charles Wesley’s Hymns', author: '衛斯理（Charles Wesley）', era: '十八世紀', place: '英格蘭', language: '英文', intro: '循道運動領袖約翰‧衛斯理之弟查理,一生作聖詩逾六千首,為英語聖詩產量與影響最豐者之一。其詩將循道宗強調的個人重生、聖潔與恩典普及的神學化為可唱的詩句,如「聽啊天使高聲唱」「神聖大愛超乎一切」「萬名之上至尊名」等,既富情感又具教導之效。查理的聖詩成為循道運動傳播信仰的利器,使會眾在頌唱中領受教義,深刻塑造英語福音派敬拜傳統,流傳至今不衰。' },
          { title_zh: '奇異恩典', title_orig: 'Amazing Grace', author: '牛頓（John Newton）', era: '一七七九年', place: '英格蘭奧爾尼（Olney）', language: '英文', intro: '英國聖公會牧師牛頓所作的聖詩,收於其與詩人庫珀合編的《奧爾尼聖詩集》。牛頓曾為奴隸船員,後悔改歸主、終身反對奴隸貿易,此詩即其親身見證恩典救贖的告白,以「我曾迷失而今尋回」道盡罪人蒙恩的轉折。詩句樸實懇切、直指人心,後世配以美國民謠曲調而風行全球,成為英語世界最廣為人知的聖詩,亦超越教會場合而為普世傳唱,是個人歸信文學的不朽典範。' },
        ],
      },
      {
        key: 'religious_epic',
        label: '宗教史詩與文學部',
        label_en: 'Religious Epic & Literature',
        desc: '以史詩與寓言鋪陳救恩大敘事的文學鉅著,自彌爾頓的失樂園到班揚的天路歷程。',
        works: [
          { title_zh: '失樂園', title_orig: 'Paradise Lost', author: '彌爾頓（John Milton）', era: '一六六七年', place: '英格蘭', language: '英文', intro: '彌爾頓晚年失明後口授而成的無韻體史詩,共十二卷,以聖經創世記為本,敘撒但叛逆墮落、誘惑人類始祖、亞當夏娃失樂園的宏大故事,旨在「向世人證成神的公義」。作品融合古典史詩格局與清教神學,對自由意志、罪與救贖、神義論的深刻探討,使其超越宗教文學而成英語文學最偉大的史詩。撒但形象的複雜尤引後世無盡詮釋,影響英美詩歌與宗教想像至深,堪稱近代基督教文學的巔峰。' },
          { title_zh: '復樂園', title_orig: 'Paradise Regained', author: '彌爾頓（John Milton）', era: '一六七一年', place: '英格蘭', language: '英文', intro: '彌爾頓繼《失樂園》之後所作的續篇史詩,共四卷,篇幅較短,以基督在曠野受撒但試探而得勝為核心,呼應前作人類因受誘墮落、今由基督的順服得贖回樂園的主題。相較前作的恢宏戲劇,此篇筆調內斂,著重基督的堅忍、智慧與對試探的辯駁,呈現以順服與屬靈定力勝過罪惡的典範。作品深化彌爾頓的救恩神學,與《失樂園》互為表裡,共構其以史詩闡釋墮落與救贖的偉大文學工程。' },
          { title_zh: '但恩聖詩', title_orig: 'Holy Sonnets / Divine Poems', author: '但恩（John Donne）', era: '十七世紀初', place: '英格蘭', language: '英文', intro: '英國玄學派詩人、聖保羅座堂主任牧師但恩的宗教詩,以「聖十四行詩」最著。其詩以奇崛的意象、緊張的思辨與熾烈的情感,直面死亡、罪愆、審判與神恩,如「死亡別驕傲」「擊打我心,三位一體的神」等篇,將個人靈魂的掙扎與渴慕傾注於精煉詩體。但恩融神學思辨於詩藝,情理交鋒、張力十足,開玄學詩派之風,其宗教詩在近代英語靈修文學中獨樹一格,影響後世詩人與信徒靈魂自省甚深。' },
          { title_zh: '聖殿', title_orig: 'The Temple', author: '赫伯特（George Herbert）', era: '一六三三年', place: '英格蘭', language: '英文', intro: '英國聖公會牧師、玄學派詩人赫伯特身後出版的宗教詩集,共收百餘首,以教堂建築為結構意象,引領讀者由外院漸入聖所,象徵靈魂親近神的歷程。詩篇題材涵蓋祭壇、聖餐、受難、禱告、順服等,文字樸素精巧,情感虔敬內斂,甚至以圖形詩排成祭壇與翅膀之形。赫伯特以平實而深刻的虔誠書寫人與神的對話,被譽為英語宗教抒情詩的典範,深受後世信徒與詩人珍愛。' },
          { title_zh: '天路歷程', title_orig: 'The Pilgrim’s Progress', author: '班揚（John Bunyan）', era: '一六七八年', place: '英格蘭', language: '英文', intro: '清教徒傳道人班揚於獄中寫成的寓言名著,藉主角「基督徒」自將亡城走向天城的旅程,寓言信徒一生的得救歷程。途中所經灰心潭、名利場、懷疑堡及所遇人物皆具象徵,生動刻畫信仰路上的試煉與盼望。作品以淺白生動的英文寫成,將清教神學化為人人可懂的故事,風行三百餘年、譯本遍及全球,僅次於聖經,是近代基督教寓言文學最偉大、流傳最廣的作品,影響無數信徒的屬靈想像。' },
          { title_zh: '豐盛的恩典', title_orig: 'Grace Abounding to the Chief of Sinners', author: '班揚（John Bunyan）', era: '一六六六年', place: '英格蘭', language: '英文', intro: '班揚的屬靈自傳,記述他自放蕩青年歷經深重罪咎之苦、長期掙扎於得救確據,終蒙神恩重生、蒙召傳道的心路歷程。書名取意「恩典臨到罪魁」,坦露其良心的劇烈交戰與對神話語的反覆求索,情感真摯、剖白無諱。此書為清教徒歸信文學的典範,將個人宗教經驗的幽微轉折和盤托出,既是《天路歷程》的傳記底本,也是研究近代英語敬虔主義與內在信仰歷程的珍貴文獻。' },
        ],
      },
      {
        key: 'mystical_meditative',
        label: '神祕與默想詩部',
        label_en: 'Mystical & Meditative Poetry',
        desc: '探索靈魂與神契合的神祕主義詩篇,自十架約翰的暗夜到西列修斯的靈智格言。',
        works: [
          { title_zh: '心靈的暗夜', title_orig: 'La noche oscura del alma', author: '十架約翰（San Juan de la Cruz）', era: '約一五七八年', place: '西班牙', language: '西班牙文', intro: '西班牙加爾默羅會神祕主義者十架約翰所作的詩與註釋,以情詩般的「暗夜」意象描寫靈魂在脫離感官與屬世依戀的幽暗中,經淨化而與神結合的歷程。詩篇文字優美,後附詳盡神學註解,將神祕經驗系統化為靈修進程。「靈魂的暗夜」遂成基督教靈修學的經典概念,指信徒在感受不到神同在的枯乾中仍堅持信靠。此作為西班牙黃金時代神祕文學與天主教靈修傳統的瑰寶,影響後世默觀靈修甚鉅。' },
          { title_zh: '大德蘭詩', title_orig: 'Poesías de Santa Teresa de Jesús', author: '大德蘭（Santa Teresa de Ávila）', era: '十六世紀', place: '西班牙', language: '西班牙文', intro: '西班牙加爾默羅會改革者、神祕主義導師大德蘭的詩作,雖以《七寶樓臺》《自傳》等散文著稱,其短詩亦傳達熾烈的屬靈渴慕。名句「我活著卻不在我裡面活」「讓無一事擾你」等,以樸實而深情的語言抒寫靈魂對神的愛慕與全然交託,於日常掙扎中見定靜。大德蘭的詩承載其默觀靈修的精髓,情真意切、易記易誦,流傳於信徒口耳之間,是西班牙天主教神祕傳統中兼具靈性深度與親和力的詩篇。' },
          { title_zh: '沉思的漫遊者', title_orig: 'Der Cherubinische Wandersmann', author: '西列修斯（Angelus Silesius）', era: '一六五七年', place: '西利西亞（今波蘭）', language: '德文', intro: '德國巴洛克神祕主義詩人西列修斯（本名舍夫勒）所作的格言詩集,以數千則簡練的雙行對句,凝煉表達神與靈魂合一的神祕思想。詩句精警弔詭,如「玫瑰無因由,開只為開」,融合中世紀神祕主義（尤受艾克哈特影響）與巴洛克詩藝,探討神、虛無、永恆與內在之神性。西列修斯由路德宗皈依天主教,其詩超越宗派而觸及普世神祕經驗,語近禪偈,後世哲人詩家屢加引述,是德語神祕詩的不朽傑作。' },
        ],
      },
    ],
  },
  wai: {
    summary: '主流基督教文學之外的詩文：新興宗教自創讚美詩與祈禱,以詩歌凝聚信眾；啟蒙時代的哲理詩則以理性審視神與人,反映宗教情感在新思潮中的變形。',
    divisions: [
      {
        key: 'new_religious_movements_poetry',
        label: '新興宗教詩文部',
        label_en: 'New Religious Movements Poetry',
        desc: '十九世紀新興宗教自創的讚美詩、祈禱與詩文,以詩歌凝聚信眾、表達其獨特信念。',
        works: [
          { title_zh: '巴哈伊讚美詩與祈禱', title_orig: "Bahá'í Hidden Words and Prayers", author: '巴哈歐拉（Bahá’u’lláh）', era: '十九世紀後半', place: '波斯／鄂圖曼領地', language: '阿拉伯文／波斯文', intro: '巴哈伊信仰創立者巴哈歐拉的詩文與祈禱,以《隱言經》最具代表,乃凝煉如珍珠的箴言詩,分阿拉伯文與波斯文兩部,傳達道德訓誨與靈魂歸向神的呼召。其文辭優美、意境深邃,兼具神祕詩與倫理教誨之美,並有大量供信徒日常誦讀的祈禱文。這些詩文承續波斯蘇菲詩歌傳統而注入普世合一的新精神,既是巴哈伊靈修的核心讀物,也見證十九世紀近東新興宗教如何以詩歌建構自身的靈性語言。', note: '巴哈伊源出伊斯蘭文化圈,因與亞伯拉罕諸教及十九世紀宗教更新潮流相涉,列為外藏旁系。' },
          { title_zh: '摩門讚美詩', title_orig: 'A Collection of Sacred Hymns', author: '史密斯（Emma Smith）編', era: '一八三五年', place: '美國俄亥俄嘉德蘭（Kirtland）', language: '英文', intro: '耶穌基督後期聖徒教會（摩門教）首部聖詩集,由創始人史密斯之妻艾瑪奉命編選。詩集除採當時通行的新教聖詩外,亦收教會成員所作、表達其獨特信念的新詩,如歌頌復興、聖殿、先知與聚集錫安等主題。聖詩在摩門崇拜與群體生活中地位崇高,被視為祈禱與教導的一環。此集奠定摩門讚美詩傳統的根基,後續增補沿用至今,見證新興宗教如何藉詩歌凝聚信眾、傳遞並鞏固其特有的神學與群體認同。' },
        ],
      },
      {
        key: 'enlightenment_literature',
        label: '啟蒙文學部',
        label_en: 'Enlightenment Literature',
        desc: '啟蒙時代以理性審視神與人之地位的哲理詩文,反映宗教情感在新思潮中的轉化。',
        works: [
          { title_zh: '人論', title_orig: 'An Essay on Man', author: '蒲柏（Alexander Pope）', era: '一七三三至一七三四年', place: '英格蘭', language: '英文', intro: '英國詩人蒲柏以英雄雙行體寫成的哲理長詩,分四書,探討人在宇宙秩序中的地位、人性、社會與幸福,旨在「為神對人的安排辯護」。詩中倡言「凡存在皆合理」,以自然神論色彩的樂觀主義看待萬物各得其所的宇宙秩序,名句「人之正當研究即人本身」傳誦一時。作品反映啟蒙時代以理性審視神義與人世的思潮,既承宗教辯神論傳統,又顯露離正統而趨自然神論的轉向,是啟蒙哲理詩的代表,列外藏以見宗教思想於新時代的變形。' },
        ],
      },
    ],
  },
},
    {
  key: 'xuandao',
  name: '宣道藏',
  name_en: 'Treasury of Proclamation',
  glyph: '宣',
  genres: '講道‧宣教‧解經',
  summary: '收近代（1500–1900）新教世界的講道、宣教與解經文獻。正藏依改革家、清教與大覺醒、海外宣教三脈，呈現宗教改革以降「以講道與差傳推進信仰」的主線；外藏並收新興宗教宣講與理性主義講壇，呈現同一時代邊緣與異流的宣道形態，供對照判讀。',
  zheng: {
    summary: '以宗教改革為起點，循「改革家解經與講道—清教與大覺醒的奮興講道—近代海外差傳」三階，勾勒新教正統宣道的成形與外擴。',
    divisions: [
      {
        key: 'reformers',
        label: '改革家講道與解經部',
        label_en: 'Reformers’ Preaching and Exegesis',
        desc: '宗教改革核心人物的聖經註釋與講道，奠定「唯獨聖經」的解經與宣講範式。',
        works: [
          { title_zh: '加爾文聖經註釋全集', title_orig: 'Commentarii in Sacram Scripturam', author: '約翰‧加爾文', era: '1540–1564', place: '日內瓦', language: '拉丁文／法文', intro: '加爾文逐卷釋經的總成，涵蓋摩西五經、詩篇、先知書、四福音合參與保羅書信等。註釋以「樸實清晰」為原則，反對牽強寓意，力求探得原作者本意，並隨文導出教義與生活應用。此書與『基督教要義』互為表裡，前者奠系統，後者落於經文，是改革宗解經傳統的根基，深刻形塑後世新教的讀經方法與講道結構。' },
          { title_zh: '路德講道集', title_orig: 'Hauspostille／Kirchenpostille', author: '馬丁‧路德', era: '1521–1546', place: '威登堡', language: '德文', intro: '路德為主日與節期經課所作的講道與釋經彙編，分「教會講道集」與「家庭講道集」兩系，供傳道人取用、信徒家中誦讀。講論以因信稱義為軸，語言質樸有力，善用日常譬喻直指人心，把深奧教義化為平民可解的話語。此集流通極廣，是德語新教講壇的範本，也是宗教改革「人人可讀聖經」精神的具體展現。' },
          { title_zh: '馬太‧亨利聖經注釋', title_orig: 'An Exposition of the Old and New Testament', author: '馬太‧亨利', era: '1708–1714', place: '英格蘭切斯特', language: '英文', intro: '英國不從國教派牧師亨利逐章逐節的全本聖經註釋，兼具學理與靈修，文筆溫厚而富格言之美。註釋重在實際教導與生命造就，常以對句點出經文要旨，便於記誦與講道引用。亨利生前完成至使徒行傳，餘卷由友人據其講稿續成。此書三百年來廣為英語世界傳道人與平信徒倚重，是家庭靈修與講台預備的經典。' },
        ],
      },
      {
        key: 'puritan-awakening',
        label: '清教與大覺醒講道部',
        label_en: 'Puritan and Great Awakening Sermons',
        desc: '十七至十八世紀英美清教徒與奮興運動的講道，以悔改、重生與聖潔為主題。',
        works: [
          { title_zh: '憤怒之神手中的罪人', title_orig: 'Sinners in the Hands of an Angry God', author: '約拿單‧愛德華茲', era: '1741', place: '北美麻薩諸塞恩菲爾德', language: '英文', intro: '愛德華茲在第一次大覺醒高峰所講的奮興名篇。講章以「你們的腳必滑跌」為據，極寫罪人懸於神忿怒之上的險境，惟賴神恩暫得托住，催逼聽者即刻悔改投靠基督。其論證綿密、意象逼人，據載講畢全場哀慟呼求。此篇為美洲奮興講道的代表，常入文選研讀，亦見證清教神學對人心罪性與神主權的深切體認。' },
          { title_zh: '懷特腓佈道集', title_orig: 'Sermons of George Whitefield', author: '喬治‧懷特腓', era: '1739–1770', place: '英格蘭與北美各地', language: '英文', intro: '巡迴佈道家懷特腓的講道結集。其以露天聚會聞名，聲量宏大、戲劇感十足，常吸引數千人駐足。講題環繞重生、悔改與唯靠基督得救，跨越宗派與大西洋兩岸，是第一次大覺醒的點火者之一。講章多由速記與事後整理留存，雖難盡傳其臨場感染力，仍可窺見其直白懇切、以福音呼召為核心的奮興講風。' },
          { title_zh: '衛斯理戶外佈道講章', title_orig: 'Sermons on Several Occasions', author: '約翰‧衛斯理', era: '1739–1791', place: '英格蘭各地', language: '英文', intro: '循道運動創始人衛斯理的標準講道集，原為循道會傳道人立教義與講道準繩而編。衛斯理打破堂會藩籬，於曠野、礦區、市集露天宣講，向勞苦大眾傳因信稱義與成聖之道。講章條理分明、兼顧頭腦與心靈，強調得救確據與全然成聖。此集既是十八世紀英國宗教復興的文獻，也是循道神學的奠基文本，影響遍及後世聖潔運動。' },
          { title_zh: '班揚講道集', title_orig: 'The Works of John Bunyan (Sermons)', author: '約翰‧班揚', era: '1656–1688', place: '英格蘭貝德福德', language: '英文', intro: '清教徒作家班揚的講道與釋義文集。班揚出身補鍋匠，因不從國教傳道而入獄多年，講論不假學究文飾，純以聖經與切身經歷感人。內容圍繞罪人歸正、恩典之約與信徒在世爭戰，與其寓言名著『天路歷程』同一靈脈。此集展現平民傳道者的屬靈深度，是清教虔敬與大眾講道結合的典範，廣受英語敬虔傳統推重。' },
        ],
      },
      {
        key: 'foreign-missions',
        label: '海外宣教部',
        label_en: 'Overseas Missions',
        desc: '近代新教差傳運動的方略、呼籲與實踐文獻，開啟普世宣教的時代。',
        works: [
          { title_zh: '探討異教徒歸主之責任', title_orig: 'An Enquiry into the Obligations of Christians to Use Means for the Conversion of the Heathens', author: '威廉‧克里（克里威廉）', era: '1792', place: '英格蘭', language: '英文', intro: '浸信會宣教士克里的劃時代小冊，被譽為近代新教宣教運動的宣言。書中駁斥「大使命已止於使徒」之說，主張普世差傳乃每個基督徒的當盡本分，並列舉各洲未得之民的人口與處境，呼籲教會以實際手段推進福音。此書直接促成浸信會差會的成立，克里旋即赴印度，開啟英語世界差傳的浪潮，影響深遠。' },
          { title_zh: '馬禮遜宣教方略', title_orig: 'Memoirs and Missionary Plans of Robert Morrison', author: '羅伯特‧馬禮遜（馬禮遜）', era: '1807–1834', place: '中國廣州、澳門', language: '英文／中文', intro: '倫敦會首位來華新教宣教士馬禮遜的差傳規劃與文獻彙編。面對清廷禁教與語言重障，他採「以文字為先」的方略：習漢語、譯聖經、編『華英字典』、辦學設印刷所，為日後在華宣教奠定根基。其方略文獻記錄了在艱難處境中循序佈道、培養本地同工的構想。馬禮遜之路徑，成為十九世紀來華差傳的開端與範式。' },
          { title_zh: '戴德生內地會方略', title_orig: 'China’s Spiritual Need and Claims', author: '戴德生', era: '1865–1875', place: '英國／中國內地', language: '英文', intro: '中國內地會創辦人戴德生的宣教呼籲與方略著作。書中以數字陳明中國內陸億萬未聞福音之眾，激發英美教會的差傳負擔。戴德生主張宣教士入鄉隨俗、著華服、深入內地，採「憑信心仰望供應、不公開募款」的信心差傳模式。內地會由此成為跨宗派國際差會的先聲，其方略與屬靈原則深刻影響二十世紀的福音派宣教運動。' },
        ],
      },
    ],
  },
  wai: {
    summary: '收同一時代與正統新教並行的宣道形態：新興宗教的傳教文宣，以及理性主義思潮下的講壇與道德演說，供比對近代宣道的疆界與分流。',
    divisions: [
      {
        key: 'new-religions',
        label: '新興宗教宣講部',
        label_en: 'New Religious Movements’ Proclamation',
        desc: '十九世紀興起、自承基督教或亞伯拉罕傳統而另立經典與權威的新宗教傳教文獻。',
        works: [
          { title_zh: '摩門教傳教冊', title_orig: 'A Voice of Warning', author: '帕雷‧普拉特', era: '1837', place: '美國紐約', language: '英文', intro: '耶穌基督後期聖徒教會早期使徒普拉特所撰的傳教手冊，是摩門教最早、流傳最廣的宣教文獻之一。書中以聖經預言為據，論證「復原的福音」與『摩門經』的權威，呼籲世人歸入新立的教會。文體仿傳統佈道而自成一系，廣供傳教士隨身使用。此冊呈現一個十九世紀美洲新興宗教如何借用基督教語彙與宣道形式，建立自身的差傳體系。', note: '後期聖徒教會自有經典，置外藏供宣道形態對照' },
          { title_zh: '巴哈伊宣道文集', title_orig: 'Tablets of Bahá’u’lláh', author: '巴哈歐拉', era: '1860s–1892', place: '波斯／鄂圖曼帝國', language: '波斯文／阿拉伯文', intro: '巴哈伊信仰創立者巴哈歐拉致眾君王、宗教領袖與信眾的書簡與宣諭結集。其宣講「諸教同源、人類一家」，自承為亞伯拉罕諸教所預期的新顯聖者，呼籲世界合一與和平。文體承襲波斯與伊斯蘭的啟示書寫傳統，兼具勸誡、訓諭與異象。此集呈現十九世紀中東一個跨亞伯拉罕傳統的新興宗教，如何以書信宣道向普世發聲。', note: '巴哈伊為獨立宗教，置外藏供宣道形態對照' },
        ],
      },
      {
        key: 'rationalist-pulpit',
        label: '理性主義講壇部',
        label_en: 'Rationalist Pulpit',
        desc: '啟蒙以降質疑正統教義、以理性與道德為本的講章與演說。',
        works: [
          { title_zh: '唯一神論講章', title_orig: 'Unitarian Christianity (Baltimore Sermon)', author: '威廉‧錢寧', era: '1819', place: '美國馬里蘭巴爾的摩', language: '英文', intro: '美國唯一神論代表人物錢寧的綱領性講道，於同道按牧禮上宣講。講章否認三位一體與基督神性，主張以理性詮釋聖經、強調神的仁慈與人的道德能力，反對加爾文派的全然敗壞與預定論。此篇被視為美國唯一神論運動的宣言，劃出與正統福音派的分界。其溫和理性、重道德涵養的講風，深刻影響新英格蘭知識界與後來的超驗主義。', note: '否認基督神性，置外藏供理性主義講壇對照' },
          { title_zh: '自然神論者道德演說', title_orig: 'The Age of Reason', author: '托馬斯‧潘恩', era: '1794–1807', place: '法國／美國', language: '英文', intro: '啟蒙思想家潘恩闡發自然神論的代表作。書中肯定有一位造物主，卻否定一切「被啟示的宗教」與教會權威，斥聖經多處為人為虛構，主張惟有理性與自然才是認識神的途徑，並以行善、尊重受造為真正的宗教。其文辭犀利、訴諸常人理智，曾風行一時亦招致激烈駁斥。此書是理性主義對啟示宗教挑戰的典型，呈現近代講壇外的「道德宗教」聲音。', note: '否定啟示宗教，置外藏供理性主義講壇對照' },
        ],
      },
    ],
  },
},
    {
  key: 'leishu',
  name: '類書藏',
  name_en: 'Treasury of Encyclopedic Works',
  glyph: '類',
  genres: '百科‧自然神學‧科學',
  summary: '收近代（1500–1900）以彙編、辭典、百科與自然神學為形態的知識性著作。正藏循神學百科與辭典、自然神學與科學、教會制度彙編三脈，呈現信仰如何整理、系統化並與新興科學對話；外藏並收啟蒙百科與祕學共濟會文獻，呈現同一知識爆發年代中與正統相抗或別立的彙編傳統，供對照判讀。',
  zheng: {
    summary: '以「整理與系統化」為主線：先立神學百科與工具書，次見自然神學與近代科學的交會，終以教會制度彙編收束建制層面的整理成果。',
    divisions: [
      {
        key: 'theol-encyclopedia',
        label: '神學百科與辭典部',
        label_en: 'Theological Encyclopedias and Dictionaries',
        desc: '系統整理神學知識的教本、辭典與經文檢索工具書。',
        works: [
          { title_zh: '近代系統神學教本', title_orig: 'Institutio Theologiae Elencticae', author: '弗朗西斯‧圖雷廷', era: '1679–1685', place: '日內瓦', language: '拉丁文', intro: '改革宗正統盛期神學家圖雷廷的系統神學鉅著，以「辯難式」逐題設問、立論、駁斥對手，涵蓋神論、預定、基督救贖至教會與末世各大題目。論證嚴密、引據賅博，是十七世紀經院化改革宗神學的集大成之作。此書長期作為神學院教本，十九世紀普林斯頓學派奉為圭臬，深刻形塑近代保守長老宗的教義架構，可視為新教系統神學「百科化」的代表。' },
          { title_zh: '克魯登經文彙編', title_orig: 'A Complete Concordance to the Holy Scriptures', author: '亞歷山大‧克魯登', era: '1737', place: '倫敦', language: '英文', intro: '克魯登獨力編纂的英文欽定本聖經全書字詞索引，逐字標出每一語詞在聖經中的出處與上下文,並附人地名與專題小註。此書編排精審、檢索便捷,使傳道人與信徒得以迅速查考經文、比對用語,是英語世界最通行的聖經工具書之一。克魯登一生數度修訂,身後續有增補,流通逾兩百年。它代表近代「以工具書馴服龐大文本」的努力,為解經與講道預備提供基礎設施。' },
        ],
      },
      {
        key: 'natural-theology',
        label: '自然神學與科學部',
        label_en: 'Natural Theology and Science',
        desc: '以受造界秩序論證神之存在與智慧，並由信仰者所撰的近代科學著作。',
        works: [
          { title_zh: '牛頓神學與年代學著作', title_orig: 'The Chronology of Ancient Kingdoms Amended', author: '艾薩克‧牛頓', era: '1728', place: '英格蘭劍橋／倫敦', language: '英文', intro: '近代科學奠基者牛頓在物理之外傾力於神學與古史的著述。此編涵蓋其修訂古王國年代學、解讀但以理書與啟示錄預言的遺稿,試圖以天文計算與史料考訂校正世俗紀年,並由聖經預言推求歷史進程。牛頓深信宇宙的數學秩序彰顯一位至高的設計者,反對三位一體卻篤信獨一神。此類著作呈現科學革命旗手如何視自然研究與聖經考據為同一敬虔事業。' },
          { title_zh: '波義耳自然神學著作', title_orig: 'The Christian Virtuoso', author: '羅伯特‧波義耳', era: '1690', place: '倫敦', language: '英文', intro: '近代化學先驅波義耳論信仰與實驗哲學相容的代表作。書中主張真正的自然研究者愈深究受造界的精巧,愈被引向敬拜其造物主,實驗科學非但不損信仰,反為敬虔之助。波義耳一生資助聖經翻譯與護教,並立「波義耳講座」專駁無神論。此書體現英國皇家學會早期「以科學榮神」的精神,是自然神學與實驗傳統結合的典範,廣受後世護教者徵引。' },
          { title_zh: '自然神學', title_orig: 'Natural Theology; or, Evidences of the Existence and Attributes of the Deity', author: '威廉‧佩利', era: '1802', place: '英格蘭', language: '英文', intro: '佩利集設計論證之大成的名著,開篇以「曠野拾錶」為喻:既見鐘錶之精巧必推有造錶者,則觀生物器官之奇妙更必歸於一位智慧的設計者。全書遍舉眼睛、心臟等構造為例,層層論證神的存在、智慧與善。此書邏輯清晰、例證豐富,長期為英國大學必讀,深刻形塑十九世紀英語世界的自然神學,既影響達爾文的思路,也成為其進化論主要的對話與駁論對象。' },
          { title_zh: '造物中彰顯的神智慧', title_orig: 'The Wisdom of God Manifested in the Works of the Creation', author: '約翰‧雷', era: '1691', place: '英格蘭', language: '英文', intro: '近代博物學奠基者約翰‧雷的自然神學名著。書中以動植物的構造、習性與生態的精巧適應,逐一論證受造界處處可見神的智慧與美善的安排。雷以實地觀察與分類見長,被譽為英國博物學之父,此書即把嚴謹的博物知識化為頌讚造物主的證據。它確立了「自然研究即敬虔」的英國傳統,直接啟發佩利等後繼者,是自然神學由哲學思辨轉向經驗博物的關鍵之作。' },
        ],
      },
      {
        key: 'church-polity',
        label: '教會制度彙編部',
        label_en: 'Compendia of Church Polity',
        desc: '整理近代教會法規、宗派章程與年鑑的制度性彙編。',
        works: [
          { title_zh: '近代教會法典彙編', title_orig: 'Corpus Iuris Canonici', author: '教廷法典編纂委員會', era: '1582', place: '羅馬', language: '拉丁文', intro: '天主教會自中世紀累積、至一五八二年由教宗額我略十三世頒行校訂定本的教會法總集。其匯集歷代教令、公會議規條與教宗裁決,規範聖職、聖事、婚姻、訴訟與教產等教會生活全域,是近代天主教法制的根本依據,直至一九一七年新法典頒行始被取代。此彙編呈現教會如何以體系化的法律整理其建制,是制度層面「類書化」整理的典型,也為宗派治理提供長久範式。' },
          { title_zh: '宗派年鑑與章程', title_orig: 'The Constitution and Canons of the Protestant Episcopal Church', author: '美國聖公會總議會', era: '1789', place: '美國費城', language: '英文', intro: '美國聖公會於獨立後脫離英國國教、自立教省時通過的憲章與教規彙編。內容規範總議會與教區的組織、主教按立、聖職紀律與公禱書的權威,確立其在新共和國中的自治體制。此類宗派章程與年鑑,記錄近代各新教宗派如何以成文規章界定自身的治理、信條與職權,是教會建制走向制度化、文書化的具體成果,亦為比較宗派政體的基礎文獻。' },
        ],
      },
    ],
  },
  wai: {
    summary: '收同一知識爆發年代中與正統相抗或別立的彙編傳統:啟蒙運動的批判性百科辭典,以及祕學與共濟會的體系化文獻,供對照近代「整理知識」的多重面貌。',
    divisions: [
      {
        key: 'enlightenment-encyclopedia',
        label: '啟蒙百科部',
        label_en: 'Enlightenment Encyclopedias',
        desc: '啟蒙運動以理性與批判精神編纂、對宗教多持質疑的百科與辭典。',
        works: [
          { title_zh: '百科全書宗教條目', title_orig: 'Encyclopédie, ou dictionnaire raisonné des sciences, des arts et des métiers', author: '德尼‧狄德羅、達朗貝爾主編', era: '1751–1772', place: '法國巴黎', language: '法文', intro: '法國啟蒙運動的旗艦工程,匯集眾多哲士以理性整理人類一切知識的大型百科。其宗教相關條目表面遵奉正統,實則以交叉參照、反諷與隱微筆法質疑教會權威、神蹟與迷信,張揚寬容與批判精神。此書屢遭查禁仍廣為流傳,被視為啟蒙思想的集中體現與動員。它呈現一種與信仰彙編截然不同的知識整理理念:以人的理性而非神的啟示為知識的最終裁準。', note: '啟蒙批判立場,置外藏供對照' },
          { title_zh: '歷史考訂辭典', title_orig: 'Dictionnaire historique et critique', author: '皮埃爾‧培爾', era: '1697', place: '荷蘭鹿特丹', language: '法文', intro: '懷疑論者培爾編纂的批判性辭典,以人物與主題為條目,正文簡而註腳浩繁,於旁徵博引中揭露史傳的矛盾、神學的疑難與信仰的脆弱。培爾主張理性與信仰難以調和,並為良心自由與寬容辯護,其懷疑精神深刻啟發後來的啟蒙哲士。此書是近代批判史學與懷疑論的先聲,展示如何以考訂與辨偽的方法對待一切權威文本,與護教式的彙編傳統形成鮮明對立。', note: '懷疑論立場,置外藏供對照' },
        ],
      },
      {
        key: 'esoteric-masonic',
        label: '祕學與共濟會部',
        label_en: 'Esoteric and Masonic Works',
        desc: '近代煉金術、玫瑰十字會與共濟會的體系化祕傳與章程文獻。',
        works: [
          { title_zh: '近代煉金術與玫瑰十字會文獻', title_orig: 'Fama Fraternitatis & Confessio Fraternitatis', author: '託名玫瑰十字兄弟會（傳約翰‧瓦倫丁‧安德里亞）', era: '1614–1615', place: '德意志', language: '德文／拉丁文', intro: '十七世紀初匿名流傳於德意志的玫瑰十字會宣言,宣告一個隱祕的智者兄弟會存世,掌握醫術、煉金與普世改革的奧祕知識,呼籲學者共謀人類的「普遍改革」。文本融會煉金象徵、神祕主義與宗教改革理想,雖真偽難辨,卻在歐洲掀起追尋祕密社團的熱潮,深刻影響後世祕學與共濟會傳統。此文獻呈現近代知識整理的另一支流:以隱喻與祕傳形式編織的宇宙與救贖知識。', note: '託名文獻,真實作者學界多歸安德里亞圈;置外藏供對照' },
          { title_zh: '共濟會憲章', title_orig: 'The Constitutions of the Free-Masons', author: '詹姆斯‧安德森', era: '1723', place: '倫敦', language: '英文', intro: '蘇格蘭長老會牧師安德森受英格蘭總會所託編纂的共濟會基本章程。書中追述石匠行會的傳說源流,訂立會員的道德義務、組織規條與集會禮儀,並標舉「自然宗教」與弟兄之愛,容納不同宗派而要求信一位至高造物主。此憲章奠定近代規範性共濟會的制度基礎,流通甚廣,屢經增訂。它呈現一個以理性、道德與祕儀結合的弟兄會,如何以成文憲章整理自身,自成一支獨特的近代彙編傳統。', note: '共濟會立場,置外藏供對照' },
        ],
      },
    ],
  },
}
  ],
}
