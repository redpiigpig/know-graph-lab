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
  summary: '近代基督教大藏經之經藏。依正典封閉法則，正經藏留白（伊拉斯謨校勘、宗教改革各語譯本與近代校勘學成果已歸譯校藏）；外經藏收摩門教與巴哈伊教等近代自稱新啟示的經典。',
  portal: { to: '/scripture', label: '聖經閱讀器' },
  zheng: {
    summary: '正典封閉法則：使徒時代新約正典封閉後，基督教不再有新「正經」。近代各語聖經譯本（路德、欽定、杜埃、神天聖書）與經文校勘成果一律歸入譯校藏；此處正經藏留白，以書架之空無宣告「啟示已在基督裡完成」。外經藏則收近代自稱新啟示的摩門教與巴哈伊教經典。',
    divisions: [],
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
  summary: '近代基督教大藏經之律藏，收近代大公會議決議、新教各派信條與教會章程，及新興宗教與啟蒙世俗政權的宗教法度。宗教改革使基督教分裂為眾多宗派，各以信條界定信仰、以章程規範體制；天主教則以脫利騰大公會議重整教規回應改革；啟蒙時代更生出政教關係的世俗立法。',
  zheng: {
    summary: '正經部收近代天主教大公會議與教廷法度、新教各派信條，及各宗派教會治理章程。脫利騰大公會議奠定反改革時代的天主教規制，新教則以奧斯堡、西敏等信條確立各自正統，教會章程則規範長老、公理、衛理諸制的運作。',
    divisions: [
      {
        key: 'gonghui',
        label: '大公會議與教廷部',
        label_en: 'Councils and the Holy See',
        desc: '反改革時代天主教的會議決議與教廷法度。',
        works: [
          { title_zh: '脫利騰大公會議文獻', title_orig: 'Canones et Decreta Concilii Tridentini', author: '脫利騰大公會議', era: '1545-1563', place: '脫利騰', language: '拉丁文', intro: '天主教為回應宗教改革而召開的大公會議，斷續歷時十八年。會議重申聖傳與聖經並重、七件聖事、煉獄與善功等教義，駁斥新教主張，並整頓神職紀律、設立修院制度。其決議奠定此後四百年天主教信仰與規制的基礎，開啟反改革(天主教改革)時代，是近代天主教最關鍵的會議。', link: '/creeds' },
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
        ,
          { title_zh: '沃蒂烏斯教會政治學', title_orig: 'Gisberti Voetii Politicae ecclesiasticae [partes I-III]', author: '吉斯貝圖·沃蒂烏斯 (Gisbertus Voetius)', era: '1663-1676', place: '阿姆斯特丹', language: '拉丁文', intro: '沃蒂烏斯為十七世紀荷蘭改革宗神學家與烏特勒支大學神學教授。本書三卷系統闡述教會政治秩序與組織原則，成為宗教改革後新教正統派的重要論著。內容涵蓋教會治理結構、牧職權限、長老制度與基督教國家的政教關係，特別強調聖經在教會政治中的權威性。此作影響深遠，塑造了改革宗與敬虔主義神學傳統對教會組織的理解，是近代新教政治神學的典範文獻。' }
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
            key: 'r-reformed-dogma', label: '改革宗教義論部', label_en: 'Reformed Dogmatics',
            works: [
              { title_zh: '《基督死亡中之死亡的死亡》', title_orig: 'The Death of Death in the Death of Christ (Salus Electorum, Sanguis Jesu)', author: '約翰‧歐文（John Owen）', era: '1648 年初版（內封題獻日期作 1647 舊式紀年，正式出版為 1648）', place: '英格蘭（時於埃塞克斯郡科吉歇爾任牧）', language: '英文', parent: '歐文全集（The Works of John Owen, Goold 編 16 卷本）', extent: '全集第 10 卷所收', intro: '清教神學家歐文最著名的救贖論專著，系統論證「限定代贖」（particular redemption）：基督的死真實成就了選民的救恩，而非僅使救恩成為可能。全書以嚴密的演繹邏輯駁斥阿民念派與普世救贖論，是改革宗五要點中「限定救贖」的經典文獻，深刻影響後世加爾文主義神學。' },
              { title_zh: '《基督教信仰體系》', title_orig: 'The Christian\'s Reasonable Service (Redelijke Godsdienst)', author: '威廉繆斯‧阿‧布拉克（Wilhelmus à Brakel）', era: '1700 年初版', place: '荷蘭鹿特丹', language: '荷蘭文', intro: '荷蘭「再進一步改革運動」（Nadere Reformatie）的代表性系統神學兼敬虔鉅著，將改革宗教義（按使徒信經與要理體例）與經驗性敬虔（experimentele godgeleerdheid）熔於一爐。全書四卷，兼論教義、經歷與基督徒生活實踐，三百年來為荷蘭改革宗家庭最常研讀的神學經典。' },
              { title_zh: '《辯神學要義》', title_orig: 'Institutio Theologiae Elencticae', author: '弗朗西斯‧圖倫丁（Francis Turretin）', era: '1679–1685 年', place: '瑞士日內瓦', language: '拉丁文', intro: '日內瓦學院教授屠靈所著的改革宗經院正統神學集大成之作，採「論辯（elenctic）」體例，逐題提出問題、列舉各方立場再加以裁斷。全書三卷二十論題，是十七世紀改革宗正統最縝密的系統神學，曾長期為普林斯頓神學院教科書，深刻塑造老普林斯頓神學傳統。' },
              { title_zh: '《意志的自由》', title_orig: 'A Careful and Strict Enquiry into the Modern Prevailing Notions of that Freedom of Will', author: '約拿單‧愛德華茲（Jonathan Edwards）', era: '1754 年初版', place: '北美麻薩諸塞殖民地斯托克布里奇（Stockbridge）', language: '英文', intro: '愛德華茲最具哲學份量的論著，駁斥阿民念派「自由意志自決論」，主張意志必依最強動機而行，從而調和神的絕對主權與人的道德責任。全書邏輯嚴密，被視為美洲思想史上的哲學神學里程碑，鞏固了加爾文主義在新英格蘭的論證基礎。' },
              { title_zh: '《敬虔願望》（或《虔誠的渴望》）', title_orig: 'Pia Desideria', author: '菲利普‧雅各‧施本爾（Philipp Jakob Spener）', era: '1675 年初版', place: '德意志法蘭克福', language: '德文', intro: '德國敬虔主義（Pietismus）的奠基性綱領文獻，原為阿恩特講道集所作之序。施本爾診斷路德宗教會的屬靈頹敗，提出六項改革主張：勤研聖經、信徒皆祭司、信仰見諸實踐、節制論爭、敬虔的神學教育、講道造就人心。此書點燃敬虔運動，影響深及衛理運動與近代宣教。' },
              { title_zh: '《基督徒的成全》', title_orig: 'A Plain Account of Christian Perfection', author: '約翰‧衛斯理（John Wesley）', era: '1766 年初版（屢經增訂）', place: '英格蘭布里斯托（Bristol，1766 年初版由 William Pine 印行）；後續修訂版在倫敦發行', language: '英文', intro: '衛斯理闡述其「全然成聖／基督徒完全」核心教義的代表作，自述他自 1725 年以來對成聖的思想發展，主張信徒可藉信心在今生達到完全的愛。此書是衛理運動聖潔神學的根本文獻，奠定後世聖潔運動與五旬節運動的神學源頭。' },
              { title_zh: '《福音的奧祕》', title_orig: 'The Marrow of Modern Divinity', author: '愛德華‧費雪（Edward Fisher，署名 E. F.）', era: '1645 年（第一部）', place: '英格蘭倫敦', language: '英文', intro: '以對話體寫成的清教神學要義，闡明律法與恩典之別，力主白白恩典的福音、抵禦律法主義與反律主義兩端。十八世紀蘇格蘭因托馬斯‧波士頓推薦此書而引發「精髓之爭」（Marrow Controversy），成為蘇格蘭福音派神學史上的關鍵文獻。' },
            
          { title_zh: '禱告的回應', title_orig: 'The Returne of Prayers', author: 'Thomas Goodwin', era: '1643', place: 'London', language: '英文', intro: '英格蘭清教徒神學家古德溫（Thomas Goodwin，1600–1680）一六四一年的靈修實踐論著，以《詩篇》八十五篇 8 節為本，闡述如何辨識上帝對禱告的回應。古德溫為公理派獨立教會領袖、克倫威爾的隨身牧師，曾任牛津抹大拉學院院長。書中將禱告喻為「與神往來、興旺有益的交易」，剖析人忽略禱告的緣由、除去操練中的試探與灰心，並引導信徒在似乎未蒙垂聽時仍信靠神的信實，是清教徒「實踐神學」釋經與靈修傳統的代表作。' },
          { title_zh: '希伯來書註釋', title_orig: 'An Exposition of the Epistle to the Hebrews', author: '約翰‧歐文（John Owen）', era: '約 1668–1684 年', place: '英格蘭', language: '英文', intro: '英格蘭清教徒神學家約翰‧歐文晚年的鉅著，逐節詳解《希伯來書》，凡七大卷，是其畢生釋經與系統神學功力的集大成。書中以歸正神學立場闡發基督的大祭司職分、新舊約的更替與救贖之約，並穿插冗長的釋經緒論與神學旁論，被譽為英語世界最完備的希伯來書註釋之一，深刻影響後世清教徒與福音派的釋經傳統。' },
          { title_zh: '腓立比書第三章釋義', title_orig: 'An exposition of the third chapter of the Epistle of St. Pavl to the Philippians', author: 'Richard Sibbes（理查‧西布斯）', era: '1639', place: '倫敦（London）', language: '英文', intro: '英格蘭清教徒名牧理查‧西布斯（1577–1635）對保羅《腓立比書》第三章的逐節釋義，身後於 1647 年在倫敦刊行。內容承其講壇講道整理而成，闡發「以認識基督為至寶、丟棄律法義而追求因信稱義」之主題，並勉信徒忘記背後、努力面前、奔向標竿。屬改革宗敬虔派釋經代表作，兼具神學詮釋與屬靈牧養關懷。' },
          { title_zh: '為公教徒解鎖：揭破耶穌會的詭辯', title_orig: 'A key for Catholicks, to open the jugling of the Jesuits', author: 'Richard Baxter（理查‧巴克斯特）', era: '1659', place: 'London（倫敦）', language: '英文', intro: '英格蘭清教徒神學家巴克斯特一六五九年的護教論辯之作。書名「為公教徒解鎖」意在助一般信徒看穿耶穌會士的詭辯手法，揭露其在教義、權威與論證上的「障眼法」。全書站在改革宗立場，逐一駁斥羅馬教會與耶穌會控辯家的主張，是宗教改革後新教反天主教論戰的典型文獻，反映十七世紀英國新教正統與羅馬公教之間激烈的教義交鋒。' },
          { title_zh: '真實的聖徒；及，真誠的試金石', title_orig: 'The saint indeed; and, The touchstone of sincerity', author: '約翰‧傅萊福（John Flavel）', era: '原著約1660年代', place: '英格蘭（原著倫敦）', language: '英文', intro: '英格蘭清教徒長老會牧師傅萊福（約1627–1691）兩篇實踐神學合刊。《真實的聖徒》論「守心之工」，教信徒看守內心、操練敬虔；《真誠的試金石》則為自省指南，分辨真假信仰、檢驗恩典是否真實。二書同屬清教徒「心靈之工」傳統，注重歸正後的內在生命、自我察驗與聖潔生活，是改革宗敬虔派靈修經典，影響後世福音派靈命塑造甚深。' },
          { title_zh: '信心的生活', title_orig: 'The Life of Faith in Three Parts', author: 'Richard Baxter（理查‧巴克斯特）', era: '1670', place: '倫敦', language: '英文', intro: '英格蘭清教徒牧者理查‧巴克斯特（1615–1691）之實踐神學名著，初為御前講道，後擴寫成書。全書環繞希伯來書十一章對「信」的界說，闡明信心如何使不可見的屬天實在成為當下生命的真實憑據，督促信徒以信而非以見來生活、勝過罪與世俗。文筆懇切務實，集清教徒「實踐敬虔」之大成，與《聖徒永恆的安息》同為巴氏靈修代表作，深刻影響近代新教敬虔傳統。' },
          { title_zh: '聖潔國度，或政治箴言（A Holy Commonwealth, or Political Aphorisms）', title_orig: 'A Holy Commonwealth', author: 'Richard Baxter（理查‧巴克斯特）', era: '1659', place: '倫敦（London）', language: '英文', intro: '英格蘭清教徒牧師理查‧巴克斯特一六五九年應哈靈頓之邀而作，又名《政治格言》。全書自上帝存在與人性等第一原理推演，論證基督教文明秩序之必要，並探討教會與行政官之關係、英國內戰之根源，是保守清教徒何以擁護議會與克倫威爾的坦率自白。書出後極具爭議，巴克斯特一六七○年自行否定，一六八三年牛津當局更下令與霍布斯、彌爾頓著作一同焚毀，為近代新教政治神學之重要文獻。' },
          { title_zh: '新教信仰真詮與辯正', title_orig: 'The Protestant Religion truly stated and justified', author: 'Richard Baxter（理查‧巴克斯特）', era: '1692', place: '倫敦（London）', language: '英文', intro: '英格蘭清教徒神學家巴克斯特晚年所撰、歿後（1692）於倫敦由威廉斯與西爾維斯特整理付梓的護教辯難之作。全書針對天主教論辯家凱里森《改革宗福音之試金石》的攻訐逐一回應，正面陳述並辯護新教信仰之本質與正當性，釐清因信稱義、聖經權威、教會與聖統等爭議要點，駁斥羅馬教廷對新教的指控。文風溫和而說理綿密，為清教徒護教與英國宗教改革後新教正統思想的代表性原典之一。' },
          { title_zh: '基督的彰顯', title_orig: 'Christ Set Forth', author: '托馬斯‧古德溫（Thomas Goodwin）', era: '1642', place: '倫敦（London）', language: '英文', intro: '英格蘭清教徒、西敏會議成員古德溫於一六四二年於倫敦初版刊行的基督論專著（一六四五年有再版，locator 指向此再版）。全題標明「基督在其死亡、復活、升天、坐於神右手與代求中，被陳明為稱義之根據與信心之對象」。本書系統闡述基督完成之救贖工作如何成為信徒稱義的客觀基礎，引導信心仰望居於父右、永遠代求的基督，是改革宗正統與清教徒虔敬神學結合的典範之作。' },
          { title_zh: '實用神學體系（通行亦譯「神性體系」或「神學大全」；原題 A Body of Practical Divinity，現代重印多簡稱 A Body of Divinity）', title_orig: 'A Body of Practical Divinity', author: '托馬斯‧華森', era: '1692初版', place: '英格蘭', language: '英文', intro: '英格蘭清教徒牧者托馬斯‧華森依《西敏小要理問答》逐條闡發的實用神學鉅著，以一百七十六篇講章體系統鋪陳上帝、創造、墮落、救贖、稱義、成聖與律法等改革宗教義。文風樸實懇切、譬喻生動，兼具教義精確與牧養溫度，是清教徒「敬虔派系統神學」的代表，數百年來廣受改革宗傳統推崇傳誦。' },
          { title_zh: '論教會治理與崇拜五辯', title_orig: 'Five Disputations of Church-Government, and Worship', author: '理查‧巴克斯特（Richard Baxter）', era: '1659 年', place: '倫敦（London）', language: '英文', intro: '英格蘭清教徒神學家巴克斯特的論爭體著作，以五篇辯論探討教會治理與公共崇拜之爭議。書中折衷主教制、長老制與獨立會眾制之間的對立，主張溫和的混合治理與循序漸進的崇拜改革，反對純粹分立主義，亦反對僵化的禮儀儀式。此書反映英國內戰後動盪時期清教徒對教會體制與敬拜形式的反思，是十七世紀新教教會論與崇拜神學的重要原典。' },
          { title_zh: '教皇制的裹屍布', title_orig: 'A winding-sheet for popery', author: 'Richard Baxter（理查‧巴克斯特）', era: '1657', place: '倫敦（London）', language: '英文', intro: '英國清教徒神學家理查‧巴克斯特一六五七年於倫敦刊行的反羅馬天主教論戰小冊。書名「裹屍布」喻意為教皇制裹上殮葬之布，宣告其當亡。全書以新教立場逐項駁斥天主教教義與教廷權柄，屬宗教改革後新教護教反異端文獻，反映十七世紀英格蘭新舊教爭辯之激烈氛圍，亦見巴克斯特折衷溫和卻堅守改革宗信仰的論辯風格。' },
          { title_zh: '論罪與恩的統治', title_orig: 'A Treatise of the Dominion of Sin and Grace', author: '約翰‧歐文', era: '約 1683', place: '倫敦', language: '英文', intro: '英國清教徒與改革宗神學家約翰‧歐文晚年論著，依羅馬書六章「罪必不能作你們的主，因你們不在律法之下，乃在恩典之下」展開，剖析罪在人心中「轄制」之權勢、信徒因恩典脫離其統治的神學根據與屬靈爭戰之道。承奧古斯丁恩典論與宗教改革「唯獨恩典」傳統，屬清教徒實踐神學與成聖論的代表作。本版為作者身後一七三九年倫敦重印本。' },
          { title_zh: '論稱義：四場辯論', title_orig: 'Of Justification four disputations', author: 'Richard Baxter', era: '1658', place: '倫敦', language: '英文', intro: '英國清教神學家理查‧巴克斯特（1615–1691）著，1658年倫敦刊行。全書以四場「辯論」（disputations）的學院論辯體裁，系統處理宗教改革核心爭議——稱義論。巴克斯特力陳因信稱義，同時調和信心與順服、律法與恩典之張力，回應安提諾米派與唯信派之偏，自成所謂「巴克斯特主義」之稱義觀。此書為清教正統護教與系統神學原典，深刻反映十七世紀英格蘭新教內部對救恩論的激辯。' }
        ,
          { title_zh: '恩約開啟：恩約論', title_orig: 'The covenant of life opened: or, A treatise of the covenant of grace', author: 'Samuel Rutherford', era: '1655', place: 'Edinburgh', language: '英文', intro: '蘇格蘭清教神學家盧瑟福之代表作，系統闡述改革宗救恩論核心之恩約教義。全書遵循加爾文傳統，深入探討約的本質、恩約與行為之約的區別、信仰在救恩中的角色等神學問題。為新教正統派與敬虔運動時期之重要神學著述，對清教派靈命塑造與護教論辯有深遠影響。' },
          { title_zh: '長老會正當的權利，或平和地辯護蘇格蘭基督教政體', title_orig: 'Due right of presbyteries, or, A peaceable plea for the government of the Church of Scotland', author: '塞繆爾‧盧瑟福（Samuel Rutherford）', era: '1644', place: '倫敦', language: '英文', intro: '蘇格蘭盟約派長老宗神學家塞繆爾‧盧瑟福為長老制教會治理權與政體結構所作的系統性神學辯護。成書於英格蘭內戰期間，乃至盧瑟福出仕西敏斯特議會時期。作者論證長老會治理乃聖經確立之制度，超越主教制，成為改革宗正統教政理論的重要典範。全書旁徵博引聖經、教父與宗教改革家著述，駁斥主教制倡議，奠定蘇格蘭長老宗的神學基礎。' },
          { title_zh: '與神聯合', title_orig: 'Communion with God', author: 'John Owen', era: '1657', place: 'London', language: '英文', intro: '英國清教神學家歐文(1616-1683)之靈修神學傑作。系統探討與聖父、聖子、聖靈三者分別之聯合與交通，以加爾文主義與敬虔傳統詮釋成聖論。強調聖靈於信仰生活中之內住與工作，融合改革宗正統神學與清教靈命深化實踐，對近代新教靈修神學影響深遠。' },
          { title_zh: '論上帝的存在與屬性', title_orig: 'Discourses Upon the Existence and Attributes of God', author: '史蒂芬‧查諾克 (Stephen Charnock)', era: '1680', place: '倫敦', language: '英文', intro: '清教宗派代表人物查諾克關於上帝存在與屬性的系統論述。本著作以護教立場，通過聖經、理性論據與駁異端等方法，將上帝的存在性、永恆性、全能、全知、聖潔等屬性逐一論證，體現改革宗與清教神學的核心關懷。該書影響深遠，為近代新教正統神學奠定護教基礎，至今仍被宗教學者與神學家徵引。' },
          { title_zh: '論神聖天意', title_orig: 'A Treatise of Divine Providence', author: '斯蒂芬‧查諾克 (Stephen Charnock)', era: '1680', place: '倫敦', language: '英文', intro: '英格蘭清教徒神學家查諾克的護教與神學系統著作，論述上帝的天意（divine providence）之本質與運作。全書以改革宗正統立場，運用聖經、理性與經驗論證神的主權與眷顧如何支配天地人事，回應自然神論與懷疑論對神聖干預的質疑。查諾克融合清教徒敬虔傳統與經院神學的嚴謹，被視為十七世紀英語護教與神學的重要文獻，深刻影響後世改革宗與福音派的天意論。' },
          { title_zh: '雅各書實踐註釋', title_orig: 'A practical commentary, or, An exposition with notes upon the Epistle of James', author: 'Thomas Manton', era: '1653', place: 'London', language: '英文', intro: '英國清教派神學家曼頓針對雅各書所著的詳盡釋經註疏。全書秉持改革宗傳統，將聖經教義與基督徒實踐相結合，著重於信仰在日常生活中的應用。曼頓以其精鑿的邏輯分析和豐富的聖經交叉引用著稱，對後世清教派釋經傳統產生深遠影響。本書為17世紀新教正統聖經詮釋的典範之作。' },
          { title_zh: '聖約的恩典觀景', title_orig: 'A View of the Covenant of Grace', author: '湯瑪士‧波士頓', era: '1734', place: '愛丁堡', language: '英文', intro: '蘇格蘭長老教會牧師波士頓對聖約神學的系統論述。聖約恩典觀乃改革宗正統的核心教義，強調神與信徒的盟約關係。本著深化清教敬虔傳統，闡述救恩論與倫理實踐的統一性，成為十八世紀新教正統護教的重要典範。' },
          { title_zh: '人性四態論', title_orig: 'Human Nature in its Fourfold State', author: '湯瑪斯‧波士頓（Thomas Boston）', era: '1729', place: '愛丁堡', language: '英文', intro: '蘇格蘭改革宗牧師湯瑪斯‧波士頓之系統神學著作。全書運用釋經與靈修傳統，闡述人性在受造、墮落、救贖、榮化四重狀態下的本質變化與救恩論意涵。代表清教派與蘇格蘭敬虔主義傳統對人論、恩典論、成聖論的深度詮釋。著成於宗教改革後期，對英語新教靈修傳統與改革宗神學教育影響深遠。' },
          { title_zh: '基督教義闡明', title_orig: 'An Illustration of the Doctrines of the Christian Religion', author: 'Thomas Boston', era: '1677-1732', place: 'Edinburgh', language: '英文', intro: 'Boston（1676–1732）為蘇格蘭清教派神學家，本著《基督教義闡明》系統闡述基督教信仰之核心教義，涵蓋三一論、救贖論、聖禮論、聖靈論等要點。著作以改革宗正統立場駁異端、辯護信仰，兼融理性推證與聖經權威，代表17–18世紀新教敬虔運動之學院神學思想，為英語世界清教傳統重要文獻。' },
          { title_zh: '律法與恩典教義展開', title_orig: 'The Doctrine of the Law and Grace Unfolded', author: '約翰‧班揚', era: '1659', place: '倫敦', language: '英文', intro: '班揚（1628–1688）為英國清教徒靈修神學家，本著作闡述律法與恩典在基督教救贖論中的關鍵角色。班揚透過釋經與系統論辯，展開加爾文與改革宗傳統對律法功用、恩典運行的深入論述，特別強調聖靈於靈魂中的動工與救贖的確據。著作融合神學論證與靈修實踐，為清教徒敬虔運動的重要護教文獻，影響英語新教傳統數世紀。' },
          { title_zh: '天意的奧秘', title_orig: 'The Mystery of Providence', author: '約翰‧弗拉維爾', era: '1685', place: 'London', language: '英文', intro: '約翰‧弗拉維爾是十七世紀英國清教徒神學家。本書以聖經為根據，探討上帝對人類歷史與個人生命的護理。弗拉維爾結合護教論述與靈性教導，深入闡述上帝的良善、全能與智慧如何在人生困厄中彰顯，回應早期啟蒙時期對神聖護理的理性質疑。全書兼具系統性的神學論證與實踐性的靈命指引，為清教敬虔傳統的重要文獻。' },
          { title_zh: '伊利尼庫姆：療癒上帝子民的分裂', title_orig: 'Irenicum: Healing the Divisions Among God\'s People', author: '耶利米亞‧伯勞斯', era: '1653', place: '倫敦', language: '英文', intro: '耶利米亞‧伯勞斯所著護教論文，於其逝世後七年（1653）由門弟子出版。本書針對英國內戰後宗教分裂問題，以清教神學視角調停教會紛爭，系統闡述新教正統立場。作者融合聖經釋經、敬虔實踐與教會政體論，主張透過基督徒德行與教義一致共識癒合教會傷痕。為17世紀英國清教思想史與護教學重要原典。' }
        ],
          },
          {
            key: 'r-piety', label: '敬虔實踐部', label_en: 'Piety and Practice',
            works: [
              { title_zh: '《論罪與試探》', title_orig: 'Of Temptation; Of the Mortification of Sin in Believers; Of Indwelling Sin', author: '約翰‧歐文（John Owen）', era: '1656–1667 年', place: '英格蘭牛津／倫敦', language: '英文', parent: '歐文全集（The Works of John Owen, Goold 編 16 卷本）', extent: '全集第 6 卷所收三篇', intro: '歐文論信徒內在屬靈爭戰的三部代表作合卷，包括《論治死信徒中的罪》《論試探》《論內住之罪》。以細膩的屬靈心理剖析罪如何在重生者心中運作，並提出「治死罪」的具體操練之道，是清教徒敬虔神學（experimental divinity）的典範，至今仍為改革宗靈修核心文本。' },
              { title_zh: '《基督徒的全副軍裝》', title_orig: 'The Christian in Complete Armour', author: '威廉‧顧納爾（William Gurnall）', era: '1655–1662 年（三部分陸續出版）', place: '英格蘭薩福克郡拉文翰（Lavenham）', language: '英文', intro: '顧納爾以以弗所書六章 10–20 節「神的全副軍裝」為綱，逐節展開的鉅幅清教徒靈修神學專著，篇幅逾千頁。全書以屬靈爭戰為主軸，論述信徒如何披戴真理、公義、信德、救恩與聖靈寶劍抵擋撒但，文筆雄辯、應用細密，司布真譽之為最佳清教徒實用神學作品之一。' },
              { title_zh: '《聖徒永恆的安息》', title_orig: 'The Saints\' Everlasting Rest', author: '理查‧巴克斯特（Richard Baxter）', era: '1650 年初版', place: '英格蘭基德明斯特（Kidderminster）', language: '英文', intro: '巴克斯特在病中默想天堂而寫成的靈修經典，論述信徒在天家所要進入的「永恆安息」，並教導以默想天上福樂為日常敬虔操練之法。全書兼具教義闡釋與牧養勸勉，是十七世紀英語世界最暢銷的敬虔著作之一，奠定巴克斯特作為清教牧者典範的地位。' },
              { title_zh: '《宗教情感真偽辨》', title_orig: 'A Treatise Concerning Religious Affections', author: '約拿單‧愛德華茲（Jonathan Edwards）', era: '1746 年初版', place: '北美麻薩諸塞殖民地北安普頓（Northampton）', language: '英文', intro: '愛德華茲總結大覺醒復興經驗的神學名著，辨析真實的「宗教情感」與虛假宗教熱忱之別，提出十二項真信仰的恩典標記，最終以「合乎福音的基督徒實踐」為試金石。此書是宗教經驗心理學與屬靈分辨的經典，至今為福音派靈修神學奠基之作。' },
              { title_zh: '《虔敬生活的嚴肅呼召》', title_orig: 'A Serious Call to a Devout and Holy Life', author: '威廉‧勞（William Law）', era: '1729 年初版', place: '英格蘭', language: '英文', intro: '英國國教非宣誓派（Non-juror）作家勞的靈修經典，主張真信仰必表現於全然奉獻神的日常生活，以生動人物刻畫對比敬虔與世俗。此書深刻影響約翰‧衛斯理、懷特腓與福音奮興運動，被視為十八世紀英語靈修文學的高峰之作。' },
            ],
          },
          {
            key: 'r-pastoral', label: '牧養神學部', label_en: 'Pastoral Theology',
            works: [
              { title_zh: '《革新的牧者》', title_orig: 'Gildas Salvianus; The Reformed Pastor', author: '理查‧巴克斯特（Richard Baxter）', era: '1656 年初版', place: '英格蘭基德明斯特', language: '英文', intro: '巴克斯特對牧職的經典反省之作，「revived（更新）」而非宗派意義的「改革」。全書本於使徒行傳二十章 28 節，呼籲牧者首先看顧自己、再逐家牧養全群，特別強調逐戶問道教理（catechizing）。此書奠定近代福音派牧養神學基礎，影響極為深遠。' },
            ],
          },

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
        ,
          { title_zh: '脫利騰會議議事錄附解毒劑', title_orig: 'Acta Synodi Tridentinae cum Antidoto', author: '加爾文（Jean Calvin）', era: '1547', place: '瑞士日內瓦', language: '拉丁文', intro: '加爾文於脫利騰大公會議第一期（1545–1547）結束後，逐條引錄議事決議並附以反駁——即所謂「解毒劑」（Antidotum）。全書針對天主教反宗教改革所確立的稱義論、聖禮觀、傳統與聖經關係等核心教義，從改革宗立場作系統性護教駁論，是十六世紀新教與天主教神學論爭最重要的原典文獻之一，充分體現改革宗正統建構期的神學論辯風格。' }
        ,
          { title_zh: '論教宗哈德良提案之審議建言', title_orig: 'Suggestio deliberandi super propositione Hadriani Nerobergae facta', author: '慈運理（Ulrich Zwingli, 1484–1531）', era: '1522年11月', place: '蘇黎世（Zürich）', language: '拉丁文', intro: '瑞士改教家慈運理一五二二年匿名所撰的論爭性建言。針對教宗哈德良六世於紐倫堡帝國會議向德意志諸侯提出、欲鎮壓路德運動之提案，作者以「兼顧基督公共福祉與德意志自由」之姿向諸侯陳辭，主張不應屈從羅馬壓制，應審慎權衡而捍衛福音與德意志之自由。屬宗教改革早期反教廷權柄的護教論爭文獻，是理解慈運理政教立場的重要原典。' },
          { title_zh: '主之言論：在我父家裏有許多住處（約翰福音第十四章釋義）', title_orig: 'Tractatio verborum Domini, in domo Patris mei mansiones multae sunt', author: '布靈格（Heinrich Bullinger, 1504–1575）', era: '1562', place: '蘇黎世（Zürich）', language: '拉丁文', intro: '蘇黎世改革宗領袖、慈運理繼任者布靈格之著作，據《約翰福音》第十四章「在我父家裏有許多住處」逐節釋義，論證信徒得救之盼望確鑿無疑，並闡明基督升天所往、被選者所歸之天乃在至高之處的實在所在。本書承續聖餐論爭脈絡，藉「右坐天父」之經文駁斥路德派「基督身體無所不在」（ubiquity）之說，為宗教改革時期改革宗釋經與系統教義之代表作。' },
          { title_zh: '兩種牧者之像', title_orig: 'The ymage of bothe pastoures', author: 'Zwingli, Ulrich (1484-1531)', era: '1550', place: 'London', language: '英文', intro: '瑞士宗教改革家茨溫利論牧職之作的英譯本，原為其 1524 年德文作品《牧者》（Der Hirt），由胡格諾信徒約翰‧維隆（John Veron Senonoys，卒 1563）據拉丁本譯為英文，1550 年於倫敦刊行。書中以「真牧者」與「假牧者」對舉，依福音標準界定教會牧者之職分與本分，正面闡述忠於聖道、餵養群羊的真牧人形象，反面則痛斥羅馬教廷只圖私利、棄羊群於不顧的假牧者。屬改革宗教會論與牧職神學要籍，反映英格蘭宗教改革對蘇黎世神學的承接。' },
          { title_zh: '就艾克於巴登辯論所作數則不實非基督教答辯之再答辯', title_orig: 'Dje ander Antwurt über etlich unwahrhaft, unchristenlich Antwurtten, die Egg uff der Disputation ze Baden ggeben hat', author: 'Zwingli, Huldrych (1484-1531)', era: '1526', place: 'Zürich', language: '德文', intro: '瑞士宗教改革家慈運理一五二六年所撰德語論戰小冊，乃針對天主教神學家艾克在巴登辯論（一五二六年五至六月）所提答辯而發之「再答辯」。慈運理因蘇黎世議會憂其安危未能親赴會場，遂以書信與密使遙控論戰並以文字反擊。本書逐條駁斥艾克所謂「不實、非基督教」之論點，捍衛改革宗在聖事、聖徒崇拜等議題上的立場，為早期瑞士改革運動護教論辯的代表文獻。' }
        ,
          { title_zh: '約翰福音釋義', title_orig: 'In D. Johannis Evangelion exegesis', author: '約翰尼斯‧勃朗茲（Johannes Brenz）', era: '1529', place: 'Hagenau (Hagenoae)', language: '拉丁文', intro: '約翰尼斯‧勃朗茲（1499–1570）宗教改革領軍路德宗神學家之釋經著作。本書為其約翰福音逐章詮釋，以講道文稿為基礎成書，闡釋路德宗聖經詮釋法。全書系統性闡明新教正統對福音書的神學詮釋，兼及護教反駁天主教與激進派異議。著者自 1554 年起歷任符騰堡公國首席神學家與公爵顧問至 1570 年逝世，其釋經著作在新教傳統中廣為流傳逾三百年，為路德宗論藏代表作。' },
          { title_zh: '論基督我主的威嚴', title_orig: 'De maiestate Domini nostri Iesu Christi ad dextram Dei Patris, et de vera praesentia corporis & sanguinis eius in coena', author: '約翰‧布倫茨', era: '1562', place: '法蘭克福', language: '拉丁文', intro: '布倫茨（1499–1570）是宗教改革時期路德宗最重要的神學家之一。本論著於1562年法蘭克福出版，針對基督的威嚴與聖餐中的真實臨在進行系統護教。回應改革宗神學家彼得‧馬蒂爾與海因里希‧布林格對聖餐性質的質疑，並透過闡述基督二性位格聯合與屬性交通（communicatio idiomatum）的教義為路德宗聖餐論護教。涉及基督論、救贖論與聖禮神學等核心宗教改革後期新教正統教義。' },
          { title_zh: '聖經之鑰', title_orig: 'Clavis Scripturae S.', author: 'Matthias Flacius Illyricus', era: '1574', place: '基爾', language: '拉丁文', intro: '馬提亞斯．弗拉修斯．伊利里庫斯（路德宗神學家、聖經釋經家）所著《聖經解碼鑰》為16–17世紀新教釋經工具書之典範。本書為詞彙索引與註釋彙編，體系化蒐集聖經人物、地名、神學概念之詮釋傳統，統整教父至宗教改革時期的釋經學成果。俾重要經文關鍵詞與教義核心課題得以系統查閱，成為宗教改革後新教釋經學之權威參考工具。' },
          { title_zh: '見證人錄', title_orig: 'Catalogus testium veritatis', author: '馬太亞斯‧弗拉齊烏斯‧伊里裡庫斯（Matthias Flacius Illyricus）', era: '1556', place: 'Basileae（巴塞爾）', language: '拉丁文', intro: '路德宗改革家弗拉齊烏斯所著護教巨著，彙編教父與教會史文獻以證新教教義之古老淵源。作品成於宗教改革激烈時期，標題「真理見證人」明示其論證策略：透過古代教會大家的言論駁斥天主教反改革的指控，強調新教教義乃回歸早期教會傳統。此書在16–17世紀新教正統中地位重要，對後世護教學影響深遠。' },
          { title_zh: '百零七條結論', title_orig: 'Hundert und siben Schlußreden', author: '雅各布‧安德烈亞(Jakob Andreae)', era: '1564', place: '烏爾姆(Ulm)', language: '德文', intro: '德國路德宗神學家雅各布‧安德烈亞於圖賓根出版的神學論著，共一百零七條。本書系統闡述路德宗信仰的核心要點，涵蓋三一論、基督道成肉身、救恩論、聖禮、教會與聖徒相通等重要教義。成書於宗教改革後期，路德宗正統化確立之時，代表德語系新教正統神學的典型立場。為理解十六世紀路德宗信仰與教義發展的重要文獻。' },
          { title_zh: '神學常例', title_orig: 'Loci communes theologici', author: '安德烈亞斯‧穆斯庫魯斯(Andreas Musculus)', era: '1563', place: 'Erfurt(埃爾福特)', language: '拉丁文', intro: '路德宗神學家穆斯庫魯斯依賴墨蘭頓傳統、系統闡述新教教義的論著。全書以「罪、律法、恩典」等主題分章，回應宗教改革時期的神學辯論，尤其針對天主教與其他新教派系的相關爭議。作為16世紀路德宗正統神學的重要文獻，本書與墨蘭頓的《神學要義》(1521)、加爾文的《基督教要義》並列為新教系統神學之開創性著作，深刻影響德意志與北歐路德宗傳統的教義整理與教會教育。' }
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
        ,
          { title_zh: '反路德派公共論題手冊', title_orig: 'Enchiridion locorum communium adversus Lutherum et alios hostes ecclesiae', author: 'Johann Eck（約翰‧艾克）', era: '1525', place: '歐洲', language: '拉丁文', intro: '英格爾施塔特大學神學教授艾克（1486–1543）撰，1525 年初版，1600 年前版次數 Wikipedia 載為 1525–1576 年間 46 版（候選稿「91 版」未獲可靠佐證，宜改為「46 版（1525–1576）」）。全書仿梅蘭希頓《神學公共論題》體例，按「公共論題」（loci communes）逐條列舉路德派異議，先徵引聖經，次援教父與大公會議，逐一駁斥。涵蓋稱義、聖事、教會權威、聖傳等核心爭點，供神父講道與教學應對宗教改革時直接使用，是反宗教改革論辯神學的奠基原典。' },
          { title_zh: '患難慰藉對話錄', title_orig: 'A dialogue of comfort against tribulation', author: 'Thomas More', era: '1534年', place: 'London', language: '英文', intro: '湯瑪斯‧摩爾（Sir Thomas More，1478–1535）身繫倫敦塔、待決前夕，以對話體寫就此靈修安慰之作。書中設匈牙利兩老親薩洛博（Anthony）與外甥文森（Vincent），在奧圖曼入侵陰影下論患難、苦難、誘惑與基督信仰的慰藉之道，深受波伊提烏斯《哲學的慰藉》傳統啟發。全書三卷，以人文主義筆法探討苦難的神學意涵、世俗榮辱的虛幻及為信仰殉道的意志，是天主教人文主義靈修文學的代表作，亦為宗教改革時代殉道神學的第一手見證。' }
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
        ,
          { title_zh: '改革宗教義學：沃勒比烏斯、福提烏斯、土倫丁', title_orig: 'Reformed Dogmatics: Seventeenth-Century Reformed Theology through the Writings of Wollebius, Voetius, and Turretin (ed. John W. Beardslee III)', author: 'Johannes Wollebius; Gisbertus Voetius; Francis Turretin; ed. John W. Beardslee III', era: '17世紀', place: 'New York（Oxford University Press）', language: '英文', intro: '十七世紀改革宗正統三位代表神學家原典選譯。沃勒比烏斯《基督教神學綱要》以簡明條目體系闡述歸正信仰；福提烏斯為荷蘭多特會議後嚴謹的經院式神學家；土倫丁《辯難神學要義》以論辯方式逐題駁斥天主教、阿米尼烏斯派與索西努派，為後世改革宗系統神學典範。三者同屬宗教改革後新教正統與經院神學脈絡，系統建構教義、護教反異端，故歸近代論藏正藏。Beardslee 僅為英譯編者。' },
          { title_zh: '昆施泰特：教義與論辯神學（神學體系）', title_orig: 'Theologia didactico-polemica sive systema theologicum (Johann Andreas Quenstedt, LC name authority n85069346)', author: '奎恩斯特（Johann Andreas Quenstedt, 1617–1688）', era: '1685', place: '德國威登堡（Wittenberg）', language: '拉丁文', intro: '奎恩斯特為十七世紀晚期路德宗正統最後一位集大成者，被譽為「路德宗正統的多瑪斯‧阿奎那」。任威登堡大學神學教授近三十年，集講義為《教義與論辯神學，即神學體系》逾一千八百頁拉丁文巨著，分「教義」與「論辯」兩部，先正面立論再駁斥異說，方法嚴謹、引證繁富，是路德宗經院神學的典範與該派系統神學的頂峰之作。' },
          { title_zh: '論重生', title_orig: 'A Treatise on Regeneration', author: '彼得‧范‧馬斯特里赫特（Petrus van Mastricht，1630-1706）', era: '1770', place: '紐黑文（New Haven）', language: '英文', intro: '荷蘭改革宗正統與「進深改革」（Nadere Reformatie）敬虔派神學家馬斯特里赫特之作，譯自其巨著《理論與實踐神學》。全篇以改革宗救恩論闡述「重生」教義：聖靈在揀選者心中所行更新之工，先於信心與悔改，乃恩典之約之根基。兼顧教義剖析與屬靈實踐，是清教徒與敬虔運動所重之名篇；愛德華茲曾譽馬氏神學最佳。1770 年紐黑文英譯本流通於新英格蘭教會。' },
          { title_zh: '理論與實踐神學', title_orig: 'Theoretico-practica theologia, qua, per singula capita theologica, pars exegetica, dogmatica, elenchtica & practica, perpetua successione conjugantur', author: '范‧馬斯特里赫特（Petrus van Mastricht, 1630–1706）', era: '初版 1682–1687；此本為 1724 年烏特勒支暨阿姆斯特丹增補版', place: '荷蘭烏特勒支與阿姆斯特丹（Trajecti ad Rhenum & Amstelodami）', language: '拉丁文', intro: '荷蘭歸正派經院神學家范‧馬斯特里赫特的代表巨著，為「荷蘭第二次宗教改革」（敬虔派）系統神學的高峰。全書逐一處理各神學主題，每題依「釋經—教義—駁異（elenctic）—實踐」四段一貫鋪陳，融嚴謹經院論證與牧養造就於一爐。曾駁笛卡兒理性主義，並深受愛德華茲推崇，視為僅次於聖經的神學佳作，是新教正統系統神學的典範文獻。' },
          { title_zh: '教宗制的絕望理據', title_orig: 'Desperata causa papatus', author: '吉斯伯特‧弗修斯（Gisbertus Voetius, 1589–1676）', era: '1635', place: '阿姆斯特丹', language: '拉丁文', intro: '荷蘭改革宗經院神學泰斗弗修斯之反天主教護教鉅著，1631–1633 年撰於霍伊斯登牧區，1635 年於阿姆斯特丹首刊，分三卷。書名直譯「教宗制乃絕望之訟案」，鋒芒直指後任伊普爾主教的楊森（Cornelius Jansenius），逐一駁斥羅馬教宗權柄與使徒統緒之主張。巴克斯特讚其徹底揭穿教宗制之無望。為宗教改革後新教正統時期典型的系統護教論辯文獻。' },
          { title_zh: '基督教神學總綱', title_orig: 'Syntagma theologiae christianae', author: '波拉努斯（Amandus Polanus von Polansdorf, 1561–1610）', era: '1609–1610', place: '巴塞爾／哈瑙（Hanau）', language: '拉丁文', intro: '瑞士巴塞爾改革宗神學家波拉努斯的代表巨著，為新教正統時期改革宗經院神學的奠基之作。全書以拉米斯式（Ramist）二分法逐層析論神學主題，由神論、聖約、揀選、基督論至教會與末世，結構嚴整、條理分明，影響其後正統時期的教義體系編纂甚鉅。1655 年哈瑙重印本沿襲此一架構，是宗教改革後改革宗系統神學的權威原典之一。' },
          { title_zh: '基督教神學：汲自聖經純淨泉源', title_orig: 'Theologia Christiana: ex puris S.S. literarum fontibus hausta', author: '本尼狄克‧皮克泰（Benedict Pictet, 1655-1724）', era: '約1696年', place: '布拉德福德（Bradford, Yorkshire）', language: '拉丁文', intro: '日內瓦改革宗神學家皮克泰（杜林之外甥、繼承其神學講席）的系統神學鉅著。書名標榜全書教義「汲自聖經純淨泉源」，體現新教唯獨聖經原則，亦兼顧理性論證與虔敬實踐。全書依改革宗正統架構鋪陳神論、人論、基督論、救恩論、教會論與末世論，是十七世紀末日內瓦學派經院化新教正統神學的代表作，曾廣譯流傳，影響後世改革宗教義學甚鉅。' },
          { title_zh: '基督教要義：依自然方法分兩卷詳述（論信仰與善行）', title_orig: 'The Substance of Christian Religion, Soundly Set Forth in Two Bookes, by Definitions and Partitions, Framed According to the Rules of a Naturall Method', author: 'Amandus Polanus von Polansdorf（阿曼杜斯‧波拉努斯）, 1561-1610', era: '1595', place: 'London（倫敦）', language: '英文', intro: '早期改革宗正統神學家波拉努斯的系統神學概要，由拉丁文譯為英文（E.W. 譯）。全書循拉米斯方法（Ramism）以定義與二分法層層剖析教義，分兩卷：第一卷論信仰，第二卷論善行，輔以提綱便覽。其行文簡明、體系嚴整，承襲亞里斯多德因果分析，為改革宗教義之精要陳述與護衛，是宗教改革後新教經院式系統神學的代表作之一。' },
          { title_zh: '神聖默想集', title_orig: 'Meditationes sacrae', author: '約翰‧革哈德(Johann Gerhard, 1582-1637)', era: '一六〇六', place: '耶拿(Jena)', language: '拉丁文', intro: '路德宗正統神學家革哈德的靈修默想經典。革哈德被譽為路德、契美尼茨之後第三位偉大的路德宗神學家，學識淵博而虔敬深篤。本書收五十一篇短默想，以聖經與奧古斯丁等教父為養分，引領讀者省察罪愆、仰望基督、操練悔改與信心。文辭凝煉而充滿屬靈溫度，調和正統教義與內心敬虔，問世後譯成多種語言、再版無數，成為近代新教流傳最廣的靈修讀本之一，亦預示其後敬虔運動之興。' },
          { title_zh: '論上帝的律法；論禮儀律與司法律（神學要義第十五至十六位）', title_orig: 'On the Law of God; On the Ceremonial and Forensic Laws', author: '約翰‧革哈德（Johann Gerhard, 1582-1637）', era: '約1610–1625', place: 'St. Louis', language: '英文', intro: '本書出自十七世紀路德宗正統首席神學家革哈德的鉅著《神學要義》(Loci Theologici)，為協同出版社「神學要義叢書」之一卷英譯。內含兩篇要目：〈論上帝的律法〉辨析道德律、禮儀律與司法律之別，以大量篇幅逐條詮釋十誡，並主張律法的三重用途（約束、明鏡、指引）；〈論禮儀律與司法律〉探討以色列關乎聖時、聖所與聖殿祭祀的禮儀規條，主張司法律隨基督而廢止、道德律則永存萬邦。為路德宗教義學經典原典。' }
        ,
          { title_zh: '論點神學集', title_orig: 'Loci Theologici cum pro adstruenda veritate tum pro destruenda quorumvis contradicentium falsitate per theses nervose solide et copiose explicati', author: '約翰‧格哈德', era: '1610–1650s', place: '漢堡', language: '拉丁文', intro: '約翰‧格哈德（1582–1637）著，為路德宗正統神學的集大成之作。全書以「論點」（loci）方式邏輯化地組織神學課題，兼具系統性與護教功能。既用於「建立真理」，亦用於「破除異議」，透過神經緊密、堅實充分的論證體系，成為宗教改革後新教神學的權威文獻，對德意志與北歐新教信仰體系產生深遠影響。' },
          { title_zh: '告白宗教信仰', title_orig: 'Confessio Catholica', author: 'Johann Gerhard（約翰‧葛哈德）', era: '1634-1637', place: 'Frankfurt & Leipzig', language: '拉丁文', intro: '葛哈德是路德宗正統派最重要的系統神學家。本書為其四卷護教論著（1634-1637），通過羅馬公教作家文獻，論證《奧斯堡信條》的福音與公教合一性，駁斥天主教反宗教改革論述。代表17世紀路德宗在反宗教改革時代的護教回應，乃新教正統主義對天主教系統的全面神學對抗。' },
          { title_zh: '神學論題彙編', title_orig: 'Systema locorum theologicorum', author: 'Abraham Calovius', era: '1655-1661', place: 'Wittenberg', language: '拉丁文', intro: '亞伯拉罕·卡羅夫（1612–1686）為德國路德宗正統派神學家。本書編纂於1655–1661年間，在威騰貝格完成，是新教正統宗教改革後期最具代表的系統神學論題彙編。作者以經院哲學與神學方法，將神學要義、倫理議題組織成簡明論題供學者查閱研究。在新教學院神學教育中影響深遠，代表路德正統派向敬虔主義過渡時期的神學思想整合。' },
          { title_zh: '正性神學', title_orig: 'Theologia positiva, per definitiones, causas, affectiones, et distinctiones, locos theologicos universos, succincte, justoque ordine proponens', author: '亞伯拉罕‧卡洛夫（Abraham Calov）', era: '1690', place: 'Frankfurt and Wittenberg', language: '拉丁文', intro: '德國路德宗正統神學家卡洛夫的主要系統神學著作，於其去世後四年出版。以簡潔而有序的方式，透過定義、原因、特徵、區分等方法，系統地呈現基督教神學的全部位置。代表十七世紀新教正統派護教與體系化的高峰，與同時代改革宗正統（如泛海姆）並駕齊驅，影響德語宗教改革思想直迄啟蒙時代。' },
          { title_zh: '索西努主義遭駁斥', title_orig: 'Socinismus profligatus', author: '卡洛夫（Abraham Calovii）', era: '1668', place: '維騰貝格', language: '拉丁文', intro: '卡洛夫(1612–1686)為路德宗正統派神學家，本著乃其反駁索西努主義異端之護教著作。索西努主義為16–17世紀東歐新教內的理性主義宗派，否定三位一體與基督之神性，主張純粹人文主義的救贖觀。卡洛夫以系統神學方法，從經文、教父傳統與信仰邏輯逐一駁斥其謬誤，維護尼西亞傳統的三位一體與基督論正統。本著為新教正統派對啟蒙理性主義先聲之預示性防守。' },
          { title_zh: '聖經舊新約詳解', title_orig: 'Biblia Testamenti Veteris et Novi Illustrata', author: 'Abraham Calovius', era: '1672–1676', place: 'Francofurti ad Moenum（法蘭克福）', language: '拉丁文', intro: '17世紀路德宗正統神學家Abraham Calovius所編，集結原文希伯來文‧希臘文本、武加大拉丁譯本與兩千年西方教父‧中世紀詮釋傳統的巨型聖經註釋彙編。對宗教改革後新教正統派護教、聖經詮釋與神學建構產生深遠影響，為改革宗與路德宗正統神學的重要基礎文獻。' },
          { title_zh: '考問神學綜述：神學特質與論戰編全', title_orig: 'Examen theologicum acroamaticum universam theologiam thetico-polemicam complectens', author: '大衛．霍拉茨', era: '1707', place: 'Unknown', language: '拉丁文', intro: '德國路德宗正統神學家荷拉茨於18世紀中葉成書之系統神學著作。標題所稱「特質與論戰」指其體系涵蓋教義正述與對異端駁論雙軌，為路德宗17–18世紀高展期標誌性護教文獻。全書按神學各部門組織論證，繼承斯坦溫及格哈德傳統，代表新教正統最後高峰。' },
          { title_zh: '神學論點彙編', title_orig: 'Compendium Locorum Theologicorum', author: '萊昂哈德‧胡特(Leonhard Hutter)', era: '1610', place: 'Wittenberg', language: '拉丁文', intro: '萊昂哈德‧胡特(1563–1616)著，宗教改革後路德宗正統派的代表作。以主題方式(loci theologici)系統彙編新教正統神學論點與教父見證，涵蓋上帝論、基督論、拯救論等核心教義。透過聖經與教父文獻的逐主題辯證，確立宗教改革後第一代正統神學的護教立場，深刻影響17–18世紀新教神學教育與體系建制。1609年被普魯士令指定為薩克遜三所公學(Fürstenschulen)的標準教材。' },
          { title_zh: '基督教和諧書', title_orig: 'Libri Christianae Concordiae', author: 'Leonhard Hutter（萊昂哈德‧胡特）', era: '1608', place: 'Wittenberg（威騰堡）', language: '拉丁文', intro: '萊昂哈德‧胡特著。威騰堡路德宗正統神學家所作的護教兼教義和諧論文。將新教改革的多家學說（路德、慈運理、加爾文等）的神學主張納入統一框架，試圖消除新教內部神學分歧。成為十七世紀路德宗正統神學的重要典籍，代表近代宗教改革後正統神學運動之護教精神，對後世新教教義綜合具有深遠影響。' },
          { title_zh: '加爾文主義者猶太化論', title_orig: 'Calvinus judaïzans, hoc est Judaïcae glossae et corruptelae, quibus Johannes Calvinus illustrissima Scripturae Sacrae loca et testimonia de gloriosa Trinitate corrumpere non exhorruit. Addita est corruptelarum confutatio per Aegidium Hunnium', author: '埃吉迪烏斯‧亨尼烏斯（Aegidius Hunnius）', era: '1595', place: '維騰堡（Witebergae）', language: '拉丁文', intro: '亨尼烏斯於維騰堡發表的系統神學駁論著作。針對加爾文預定論及其聖經詮釋提出激進批評，聲稱改革宗教義背離早期教會傳統，傾向於猶太拉比思想。本書特別攻擊加爾文對三位一體論的詮釋，指其採納猶太釋義傳統而扭曲聖經。作為16世紀末新教內部論爭的重要文獻，體現路德宗正統對加爾文主義的神學防衛，涵蓋預定論、恩典論、聖禮論與三位一體論等核心教義差異。' },
          { title_zh: '脫利騰會議考辨', title_orig: 'Examinis Concilii Tridentini', author: '馬丁·凱姆尼茨', era: '1565–1573', place: 'Frankfurt', language: '拉丁文', intro: '馬丁·凱姆尼茨所著四卷本系統考辨著作，逐條檢視脫利騰公會議（1545–1563）之教令，以路德宗正統立場反駁天主教反宗教改革神學。本書為新教正統時期之重要護教與系統神學文獻，確立路德教會對聖體聖事、恩典論、因信稱義等要點之教義立場，在近代西方基督教思想與教會論戰中佔重要地位。' },
          { title_zh: '神人之約的經濟', title_orig: 'De oeconomia foederum Dei cum hominibus libri quatuor', author: 'Herman Witsius（威特西烏斯）', era: '1677', place: 'Leeuwarden', language: '拉丁文', intro: '荷蘭改革宗神學家威特西烏斯的重要系統神學著作，以「約」(covenant)為核心框架，闡述從舊約到新約神與人的盟約關係，分四卷論述護教論、救贖論與實踐神學。此書奠定了近代改革宗盟約神學傳統的經典地位，對後世英美清教與改革宗正統產生深遠影響。盟約神學成為宗教改革後新教系統神學的重要支柱，聯繫聖經解釋與教義組織。' },
          { title_zh: '脫利騰公會議解剖——歷史與神學研究', title_orig: 'Concilii Tridentini anatome historico-theologica', author: 'Johann Heinrich Heidegger', era: '1672', place: '蘇黎世', language: '拉丁文', intro: '改革宗神學家海德格爾對脫利騰大公會議(1545–1563)的系統解析。該卷為十七世紀新教對天主教反宗教改革的權威回應，深入檢視大公會議在聖傳、聖事、因信稱義等教義的決議，並展開護教辯論。海德格爾以歷史與神學雙軌分析馬里亞尼等天主教思想家的論述，代表改革宗正統(Reformed Orthodoxy)對脫利騰的系統性批判。' },
          { title_zh: '神學精髓的精髓', title_orig: 'Medulla Medullae theologiae christianae', author: '約翰‧海因里希‧海德格爾（Johann Heinrich Heidegger）', era: '1697', place: '瑞士蘇黎世', language: '拉丁文', intro: '《神學精髓的精髓》由蘇黎世改革宗神學家海德格爾於一六九七年出版，是近代改革宗經院正統神學的集大成之作。全書採經院辯論體例，系統闡述改革宗的聖經觀、三一論、預定論、救恩論與教會論，並針對天主教、路德宗與其他異議立場逐一進行護教反駁。此書以簡潔而嚴密的拉丁文呈現改革宗信仰的理性架構，是十七世紀末歐洲改革宗神學教育的重要教科書，深刻影響後世日內瓦與普林斯頓等改革宗傳統。' },
          { title_zh: '布爾曼神學與神約經綸綜述', title_orig: 'Synopsis theologiae et speciatim oeconomiae Foederum Dei', author: '弗蘭西斯庫斯·布爾曼（Franciscus Burman / Frans Burman）', era: '1671', place: '烏得勒支（Utrecht', language: '拉丁文', intro: '布爾曼（1628–1679）為荷蘭改革宗神學家，1662年起任烏得勒支大學神學教授。本書乃其系統神學集大成之作，1671年於烏得勒支首版。核心論旨「神約經綸」（oeconomiae Foederum Dei）——即上帝透過聖約與人類聖恩互動的全景敘述——構成約翰·卡克思（Johannes Cocceius）聯邦神學的哲學基礎。全書以救贖史與神學經院哲學雙軌貫穿創造、墮落、救贖三軸線，嘗試調和笛卡爾理性主義與改革宗正統神學。拉丁文原著，在荷蘭與英語世界新教神學教育中傳播三世紀，代表改革宗聯邦神學與卡笛兒主義結合的典範之作。' },
          { title_zh: '精選神學諸論爭', title_orig: 'Selectarum disputationum theologicarum [pars prima]', author: '吉斯伯特·韋提烏斯', era: '1648', place: '烏特勒支', language: '拉丁文', intro: '荷蘭改革宗神學家韋提烏斯（1589–1676）所著。本作為其系統神學諸論爭之精選集，首卷成書於1648年。全書采取經院式論爭體例，逐一開展改革宗正統對宗教改革後期諸爭議之系統性辯護，涵蓋聖經論、救贖論、聖禮學、教會論等核心教義。代表17世紀中葉荷蘭改革宗神學之巔峰成就，與同時代新教正統及敬虔運動思想密切相關。' },
          { title_zh: '基督教神學簡纂', title_orig: 'Christianae theologiae compendium', author: '約翰尼斯·沃勒比烏斯(Johannes Wollebius)', era: '1626', place: '巴塞爾', language: '拉丁文', intro: '沃勒比烏斯《基督教神學簡纂》為 17 世紀改革宗正統神學代表著作。全書以四論架構呈現基督教信仰核心：上帝論、基督論、救贖論、教會論，兼及聖禮與聖事。這部系統神學在荷蘭、英格蘭清教運動與北美殖民地產生深遠影響，被視為介於加爾文與敬虔運動之間的橋樑。著作採問答體，便於教牧與教信一讀。新教正統時期的典型神學綱領。' }
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
    ,
      {
        key: 'modern-protestant-systematics',
        label: '近代新教系統神學部',
        label_en: 'Modern Protestant Systematics (19c)',
        desc: '十九世紀新教（浸信會、信義宗、自由派）系統神學教本，於達爾文主義與聖經批判衝擊下重構教義體系。',
        works: [
          { title_zh: '系統神學', title_orig: 'Systematic Theology', author: '史壯（Augustus Hopkins Strong）', era: '1886（1907–1909 三卷定本）', place: '美國紐約州羅徹斯特', language: '英文', intro: '史壯（Augustus Hopkins Strong，1836–1921）為美國浸信會神學家，長期擔任羅徹斯特神學院院長（1872–1912）暨系統神學講席。本書為其畢生心血之系統神學巨著，初版於 1886 年，後歷經數度增補，至 1907–1909 年定本共三卷（神論、人論、救贖論），涵蓋神論、人論、基督論、救贖論與末世論。史壯融合改革宗加爾文神學傳統與十九世紀有機進化思想，試圖在護教框架內回應達爾文主義衝擊。其嚴謹的聖經實證進路與宏大的體系建構，使本書成為近代新教保守正統神學最具代表性的教科書之一，廣泛影響北美浸信會與福音派神學院逾百年。' },
          { title_zh: '基督教神學綱要', title_orig: 'An Outline of Christian Theology', author: '克拉克（William Newton Clarke）', era: '1898', place: '美國紐約', language: '英文', intro: '克拉克（William Newton Clarke，1841–1912）為美國浸信會神學家，本書是十九世紀末北美自由派新教神學的代表性系統神學綱要。全書依神論、人論、基督論、救贖論、教會論、末世論次序鋪陳，以歷史批判精神與福音信仰相調和，嘗試將啟蒙後的理性主義與正統新教信仰整合為一貫神學體系。此書廣泛用於北美神學院，奠定二十世紀初自由神學的論述格局，為近代新教系統神學的重要一手原典。' },
          { title_zh: '信義宗教義綱要', title_orig: 'Kompendium der Dogmatik', author: '路德哈特（Christoph Ernst Luthardt）', era: '1865', place: '德國萊比錫', language: '德文', intro: '路德哈特（Christoph Ernst Luthardt，1823–1902）為德國萊比錫大學路德宗系統神學教授，以捍衛正統信義宗神學著稱。本書德文原題《Kompendium der Dogmatik》（1865 年初版，1893 年第九版），依傳統教義綱要次序論述上帝論、基督論、救贖論與末世論，力抗十九世紀自由主義神學浪潮，維護信條主義立場。英語神學院流通者係魏德納（R. F. Weidner）1888 年據本書改編之《教義神學導論》，非直接譯本。' }
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
    ,
      {
        key: 'anti-trinitarian-radical',
        label: '反三一與激進改革部',
        label_en: 'Anti-Trinitarian and Radical Reformation',
        desc: '宗教改革激進翼對尼西亞三一教義的否定，啟唯一神論與蘇西尼主義之先。',
        works: [
          { title_zh: '三位一體謬誤論七卷', title_orig: 'De Trinitatis erroribus libri septem', author: '塞爾維特（Michael Servetus）', era: '1531', place: '阿爾薩斯哈根諾（Hagenau）', language: '拉丁文', intro: '西班牙神學家塞爾維特（米迦勒‧塞爾韋圖斯，約 1511–1553）於 1531 年在哈根諾出版的反三位一體論著作，為宗教改革時代最激進的神學挑戰之一。全書七卷以聖經文本為據，主張尼西亞三位一體教義係希臘哲學污染之產物，耶穌非永恆的第二位格而是神性之子。此書同時觸怒天主教與改教陣營，終致塞爾維特 1553 年於日內瓦被審判火刑。本書為近代唯一神論與反尼西亞神學的奠基原典，具有不可忽略的神學史地位。' }
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
        ,
          { title_zh: '法蘭西改革宗教會史', title_orig: 'Histoire ecclésiastique des églises réformées au royaume de France', author: 'Théodore de Bèze', era: '1580', place: 'Anvers', language: '法文', intro: '加爾文繼承人、日內瓦改革宗領袖德‧貝則（Théodore de Bèze，1519–1605）主編之法國改革宗教會編年史，記述 1521 至 1563 年間法國胡格諾教會之興起、迫害、宗教戰爭與殉道事蹟，為宗教改革史最重要的第一手史料之一。全書實為法國改革宗教會集體編纂、以德‧貝則為主要編者，兼具史傳與護教性格，記錄改革宗信徒所受苦難，見證法蘭西新教運動的神學立場與教會組織，是研究胡格諾運動與十六世紀法國宗教改革不可或缺的原典文獻。' },
          { title_zh: '新教諸教會變遷史', title_orig: 'Histoire des variations des églises protestantes', author: 'Jacques-Bénigne Bossuet', era: '1688', place: 'Paris', language: '法文', intro: '法國天主教主教博敘埃（Bossuet）之反宗教改革論戰鉅作。全書追溯路德、加爾文、慈運理等改革家及各新教宗派自十六世紀以來在教義上屢次反覆更改的歷史，以「變遷」（variations）為核心論據，主張教義不一致正是新教缺乏神聖權威的明證，藉此護衛天主教傳統之不變性。此書兼具史傳與護教雙重性格，是天主教反宗教改革思想史上最具影響力的原典之一，亦是研究十七世紀公教與新教論辯不可或缺的第一手文獻。' },
          { title_zh: '查理五世治下宗教與共和國狀況史', title_orig: 'Histoire de l\'estat de la religion et république sous l\'empereur Charles cinquiesme（法譯本）；拉丁原著：Commentariorum de statu religionis et reipublicae, Carolo V. Caesare, libri XXVI', author: 'Johannes Sleidanus（施萊丹，1506–1556）；法譯者：Robert Le Prévost', era: '1558', place: '歐洲', language: '法文', intro: '施萊丹（Johannes Sleidanus, 1506–1556）為新教陣營最重要的宗教改革史家，曾任史特拉斯堡議員，親歷奧格斯堡議會等關鍵事件。其拉丁文原著《評述查理五世治下宗教與共和國狀況》（1555）按年逐條記錄路德、加爾文、慈運理等人的改革運動，並涵蓋帝國政治與神學爭議。本書為同年法文譯本，使宗教改革史料普及於法語世界。全書係一手見證性編年史，被後世視為新教史學奠基文獻，史料價值遠超一般二手研究。' },
          { title_zh: '教會重建：英格蘭教會改革史', title_orig: 'Ecclesia Restaurata; or, The History of the Reformation of the Church of England', author: 'Heylyn, Peter', era: '1661', place: 'London', language: '英文', intro: '彼得‧海林（1599–1662）為英格蘭國教會神職人員兼史學家，坎特伯里大主教勞德之忠實支持者。本書以「教會重建」為題，系統記述英格蘭宗教改革全程，自亨利八世與羅馬決裂，歷經愛德華六世新教化、血腥瑪麗復辟，至伊利沙白一世確立國教體制，為英格蘭改革史的重要一手史料。海林立場保守偏高教會派，對清教徒批評甚力。全書以編年體鋪陳，援引原始文獻，為十七世紀英國教會史學之代表作。' },
          { title_zh: '英格蘭教會改革史', title_orig: 'The History of the Reformation of the Church of England', author: 'Burnet, Gilbert', era: '1679', place: 'London', language: '英文', intro: '吉爾伯特‧伯內特（Gilbert Burnet，1643–1715）所著，為英語世界最重要的英格蘭宗教改革史著作之一。伯內特身為蘇格蘭裔聖公會主教，以第一手文獻（國家檔案、主教登錄冊、議會紀錄）為基礎，詳述自亨利八世與羅馬決裂至伊麗莎白一世確立聖公會體制的歷程。全書兼具史料匯編與護教辯護性質，首卷成書於1679年（第二卷1681年），英國議會為此投票致謝、牛津大學頒授榮譽神學博士。是研究英格蘭宗教改革不可或缺的同代史傳文獻。' },
          { title_zh: '馬格德堡世紀史', title_orig: 'Centuriae Magdeburgenses, seu, Historia ecclesiastica Novi Testamenti', author: 'Matthias Flacius Illyricus', era: '1559–1574', place: '歐洲', language: '拉丁文', intro: '新教第一部大型教會通史，由路德宗學者弗拉齊烏斯‧伊利里庫斯主持，馬格德堡一批神學家合力撰成，初刊於 1559–1574 年，以「世紀」為單位分十三冊，涵蓋至 1298 年。全書以嚴厲反教宗立場梳理歷代教義、禮儀、異端與教會制度，旨在証明羅馬教廷已偏離使徒傳統。其批判性史料運用方法奠定近代教會史學基礎，被後世視為歷史編纂學的里程碑。1757 年版即以《馬格德堡世紀》之名重刊流通。' },
          { title_zh: '英格蘭宗教改革暨教會設立編年紀——伊利沙伯女王盛世教會諸事錄', title_orig: 'Annals of the Reformation and Establishment of Religion, and Other Various Occurrences in the Church of England, during Queen Elizabeth\'s Happy Reign', author: 'Strype, John', era: '1709', place: 'London', language: '英文', intro: '英國教會史家史特萊普（John Strype, 1643–1737）編纂之英格蘭宗教改革編年鉅著，以伊利沙伯一世在位期間（1558–1603）教會設立與宗教事務為主軸，徵引大量原始文件、王室詔令與教會文告，逐年記述國教會組織確立、改革派神職任命及宗教政策演變。此書為近代英國教會史一手史料彙編，與史特萊普另著《大主教克蘭麥傳》等同為研究英國宗教改革不可或缺之原典性資料集。' },
          { title_zh: '教會史料彙編：亨利八世、愛德華六世與瑪麗一世宗教改革紀錄', title_orig: 'Ecclesiastical Memorials, Relating Chiefly to Religion, and the Reformation of It, under King Henry VIII, King Edward VI and Queen Mary I', author: 'Strype, John', era: '1721', place: 'London', language: '英文', intro: '英國教會史學家約翰‧史特萊普（John Strype，1643–1737）編著的大型史料彙編，系統蒐集亨利八世、愛德華六世、瑪麗一世三朝英格蘭宗教改革相關原始文獻，涵蓋教會法令、王室諭令、書信、殉道紀錄與改革家傳記資料。全書以文獻輯錄為核心，兼附編年敘事，是研究英格蘭宗教改革首要一手史料彙編，為後世英國教會史奠定文獻基礎，具不可替代的史料價值。' },
          { title_zh: '蘇格蘭教會改革史', title_orig: 'The History of the Reformation in Scotland（1644年版印題 The Historie of the Reformation of the Church of Scotland）', author: 'Knox, John', era: '約1559–1566年撰', place: 'London', language: '英文', intro: '約翰‧諾克斯（約1514–1572）是蘇格蘭宗教改革的核心領導人，本書為其親歷改革運動的第一手史述，記錄蘇格蘭教會自1560年代脫離羅馬教廷、確立長老制信仰的全過程。書中詳述諾克斯與瑪麗女王的多次對峙、各地改革浪潮、〈蘇格蘭信條〉訂立及政教衝突，語氣激昂，兼具神學論辯與原始史料價值。1644年倫敦版為身後出版，是研究十六世紀英倫宗教改革不可或缺的一手文獻。' },
          { title_zh: '路德主義歷史護教注疏', title_orig: 'Commentarius historicus et apologeticus de Lutheranismo, sive, De reformatione religionis ductu D. Martini Lutheri', author: 'Veit Ludwig von Seckendorf', era: '1692', place: 'Leipzig', language: '拉丁文', intro: '德意志政治家兼史家澤肯道夫（1626–1692）以拉丁文撰成，針對天主教史家梅博爾（Louis Maimbourg）對路德宗的批駁，逐條提出歷史佐證與神學辯護。全書分歷史（historia）與護教（apologia）兩體裁，廣引原始文獻重構馬丁‧路德領導宗教改革之始末，涵蓋從威登堡爭論到奧斯堡信條的關鍵事件，是十七世紀新教正統時期最重要的改革史護教巨著之一。' }
        ]
      },
      {
        key: 'martyrs-saints',
        label: '殉道與聖徒部',
        label_en: 'Martyrs and Saints',
        desc: '近代新教殉道錄與天主教反改革聖徒傳記，記信仰者受難與成聖的見證。',
        works: [
          { title_zh: '殉道者之書', title_orig: 'Acts and Monuments', author: '約翰‧福克斯（John Foxe）', era: '1563', place: '倫敦', language: '英文', intro: '福克斯這部巨著俗稱「殉道者之書」，自早期教會殉道追溯至英格蘭瑪麗一世治下被焚的新教徒，以血淚交織的個案串起一部「真教會受逼迫」的通史。書中詳載審訊對話、火刑場景與臨終遺言，並配以木刻插圖，文字煽動而動人。它塑造了英語世界的新教認同與反羅馬情緒，數百年間僅次於聖經而廣為流傳，是理解英國宗教改革集體記憶的關鍵文本。' },
          { title_zh: '反改革聖徒傳記', title_orig: 'Vitae Sanctorum / Acta Sanctorum', author: '波蘭定會（Bollandists，約翰‧博蘭德等）', era: '1643 起', place: '安特衛普', language: '拉丁文', intro: '此為耶穌會博蘭德學派啟動的浩大聖徒傳集成，按教會曆逐日蒐羅古今聖人事蹟。面對新教對聖徒崇拜的攻擊，編者一反中世紀傳奇的浮誇，力求考訂史源、辨偽存真，開創批判性聖傳學。其中收入脫利騰會議後新封的反改革聖徒，如羅耀拉、沙勿略、加爾默羅會德蘭等，既見證天主教靈修的更新，也展示近代史料考證方法在教會史上的萌芽。' },
          { title_zh: '近代殉道錄', title_orig: 'Martyrologium recentius', author: '佚名輯錄（天主教傳信部所傳）', era: '十七至十八世紀', place: '羅馬', language: '拉丁文', intro: '此錄彙集近代天主教在海外宣教與歐洲宗教衝突中殉難者的事蹟，以日本、越南、北美與英倫三島為重心。文中逐一記下殉道者姓名、會籍、受刑日期與方式，並附目擊者證詞與骸骨遺物去向，體例近於封聖程序的卷宗。它不僅是敬禮資料，更保存了宣教前線遭遇本地政權鎮壓的第一手線索，為近代教難史提供具體的人物與年代座標。' }
        ,
          { title_zh: '使徒傳：與使徒同代及繼承者生平事蹟殉道錄', title_orig: 'Apostolici: or, the history of the lives, acts, death and martyrdoms of those who were contemporary with, or immediately succeeded the apostles', author: 'William Cave', era: '1677', place: 'London', language: '英文', intro: '英國聖公會神學家威廉‧凱夫（William Cave, 1637–1713）所著早期教父傳記史，拉丁書名「Apostolici」意指「使徒傳人」（與其另一著作《Antiquitates Apostolicae》為不同書）。本書記錄與使徒同時代或緊接其後的早期基督徒之生平、事蹟、死亡與殉道，涵蓋亞納尼亞、革利免、伊格那修、坡旅甲等人物，為十七世紀英國教會史學的代表作之一，1682 年出第二版。凱夫曾任查理二世宮廷牧師、溫莎大教堂座堂教士。' },
          { title_zh: '聖方濟‧沙勿略傳——耶穌會士、印度與日本宗徒', title_orig: 'Vie de saint François Xavier, apôtre des Indes et du Japon', author: 'Dominique Bouhours', era: '1682', place: 'Paris', language: '法文', intro: '法國耶穌會士布厄爾（Dominique Bouhours）所撰聖方濟‧沙勿略（François Xavier, 1506–1552）傳記，1682 年巴黎出版。沙勿略為耶穌會創會元老之一，天主教最重要的傳教士，奉派至印度果阿、日本長崎等地宣教，被尊稱「印度宗徒」。本書以典雅法文敘述沙勿略生平事蹟、奇蹟與殉道精神，是反宗教改革時期傳教運動的重要史傳文獻，亦反映了十七世紀耶穌會對亞洲傳教事業的神學詮釋與靈修理想。' },
          { title_zh: '殉道錄——為福音真理而受迫害致死的殉道者史', title_orig: 'Actes des martyrs deduits en sept livres, depuis le temps de Wiclef & de Hus, jusques à présent', author: 'Crespin, Jean', era: '1565', place: 'Genève', language: '法文', intro: '克瑞斯班（Jean Crespin，1520–1572）為日內瓦改革宗出版家，此書為法語新教最重要的殉道錄，記載自早期教會至宗教改革時代諸殉道者遭天主教當局逼迫、刑拷與處決的史實，尤重法國、低地國、英格蘭等地新教信徒的見證與臨終陳詞。全書以一手文件為據，融傳記、案卷與神學詮釋為一體，與約翰‧福克斯《殉道史》並列為新教殉道文學雙璧，為研究宗教改革史及改革宗教會史不可或缺的一手原典。' },
          { title_zh: '聖父、殉道者暨諸主要聖人傳', title_orig: 'Vies des pères, des martyrs et des autres principaux saints', author: 'Butler, Alban；譯者 Godescard', era: '1756', place: 'Versailles', language: '法文', intro: '英國天主教神父阿爾班‧巴特勒（Alban Butler）所著《諸聖人傳》之法文譯本，由法國神父戈德斯卡爾（Jean-François Godescard，1728–1800）據英文原著自由意譯，Godescard 卒後由凡爾賽 Lebel 印刷所於 1811 年刊印新版（共 13 冊，第 13 冊由 Nagot 續譯，收活動慶日與教會年曆）。原著按曆書日期逐日編排，涵蓋教父、殉道者、修道先賢及全教會諸位主要聖人的生平事蹟與殉道紀錄，是天主教啟蒙時代最具規模的聖人傳記彙編之一，深受法語天主教世界廣泛流傳，兼具靈修、歷史與史料參考價值。' },
          { title_zh: '精選聖徒列傳五十二篇', title_orig: 'Quinquaginta duae vitae sanctorum selectiores', author: 'Surius, Laurentius（著）；Verhaer, Franciscus（編選）', era: '1588', place: 'Antverpiae', language: '拉丁文', intro: '加爾都西修士勞倫修‧蘇里烏斯（1522–1578）為反宗教改革時期最重要的天主教聖徒傳學家，畢生致力於整理、拉丁化與出版聖徒生平史料。本書為其身後出版之精選本，收錄五十二位重要聖徒傳記，取材自其六卷本《聖人事蹟可信史》（De probatis sanctorum historiis），兼具歷史考證與靈修建德雙重目的。蘇里烏斯所據底本多為希臘及拉丁教父時期原始資料，為脫利騰公會議後天主教聖傳文學之代表作，對後世羅馬殉道錄之修訂亦有深遠影響。' },
          { title_zh: '羅馬殉道錄（1613年安特衛普版）', title_orig: 'Martyrologium romanum ad nouam kalendarij rationem restitutum (Antwerp 1613 ed.)', author: 'Catholic Church; Baronio, Cesare', era: '1583', place: 'Antverpiae', language: '拉丁文', intro: '天主教教會官方殉道錄，依格列高利曆改革重整曆法次序，著名教會史家凱撒‧巴羅尼烏斯（Cesare Baronio）於1586、1589年考訂補注（刪除歷史可疑條目、補充原始文獻注腳），1583年首版、1584年第三版定為羅馬禮必用。本書按月日逐日列出殉道聖人姓名、受難地與簡傳，為後世聖人曆與教會史研究奠定規範。1613年安特衛普版由普蘭廷出版社（Plantin-Moretus）印行，乃重要早期刊本。此書係天主教反宗教改革時期強化聖徒崇敬、確立正統殉道傳統之核心史傳文獻。【注：intro原稿誤稱聖查理‧博羅梅奧主持修訂，文獻不支持此說，已刪除。】' },
          { title_zh: '殉道者史傳（第一部）', title_orig: 'Historien der Martyrer: erste Theil', author: 'Rabus, Ludwig', era: '1571', place: 'Straßburg', language: '德文', intro: '路德宗神學家路德維希‧拉布斯（Ludwig Rabus，1524–1592）所編纂的新教殉道錄，為宗教改革時期德語世界最早的系統性殉道史傳之一。全書追溯殉道見證人的脈絡，從舊約亞伯起經早期教會殉道者，直至宗教改革時代的新教烈士，旨在彰顯路德宗信仰乃「真正、古老、大公、正統基督教教義」的延續。1571年版為1554–1557年八卷本的修訂再刊，刊行於斯特拉斯堡。本書是研究宗教改革殉道神學與新教聖徒傳統的第一手原典文獻。' },
          { title_zh: '殉道者之鏡——無防衛基督徒殉道錄', title_orig: 'The bloody theater, or, Martyrs mirror of the defenseless Christians', author: 'Thieleman J. van Braght', era: '1660年初版', place: '歐洲', language: '荷蘭文', intro: '荷蘭門諾派執事范‧布拉赫特（Thieleman J. van Braght）編纂的里程碑式殉道錄，初版於1660年，1685年大幅擴充。全書收錄自初代教會至十六世紀再洗禮派（門諾、瑞士弟兄會）信徒遭受迫害與殉道的史料與供詞，以「無防衛基督徒」（defenseless Christians）為主軸，強調非暴力受苦的信仰見證。1837年英譯本廣傳於北美門諾社群，成為再洗禮派傳統最重要的信仰遺產文獻，亦是宗教改革激進派史傳藏的核心典籍。' },
          { title_zh: '諸聖行傳', title_orig: 'Acta sanctorum quotquot toto orbe coluntur', author: 'Bollandus, Joannes; Henschenius, Godefridus et al.', era: '1643–', place: 'Antverpiae', language: '拉丁文', intro: '耶穌會學者博蘭杜斯（Bollandus）與韓升紐斯（Henschenius）等人自 1643 年起在安特衛普出版的巨型聖徒行傳彙編，依教會曆年節序收錄古今普世所有聖人之行傳、殉道紀錄與奇蹟證詞，附原始文獻校勘與考證注疏。此計畫歷經數代博蘭德學派學者接力，最終逾百卷，是天主教聖徒傳記研究的奠基原典總匯，兼具史料彙編與批判考據雙重性質，為近代天主教反宗教改革學術傳統的代表作。' },
          { title_zh: '英格蘭名賢志', title_orig: 'The History of the Worthies of England', author: 'Fuller, Thomas', era: '1662', place: 'London', language: '英文', intro: '英國聖公會神職人員湯瑪斯‧富勒（Thomas Fuller，1608–1661）晚年力作，身後於1662年出版。全書依郡縣分卷，逐一記錄英格蘭各地歷史名賢，涵蓋主教、神學家、宗教改革家、殉道者、修道院長及一般世俗名流。富勒本人為護教史家，著有《英國教會史》，本書大量條目涉及聖公會與清教改革脈絡中的教會人物，是研究宗教改革後英國教會生態與聖職者傳記的重要原典文獻，具人物誌與地方教會史雙重價值。' },
          { title_zh: '多默‧摩爾爵士傳', title_orig: 'The life of Sir Thomas More', author: 'William Roper', era: '約 1556–1557 年撰', place: 'London', language: '英文', intro: '本書為多默‧摩爾爵士之女婿威廉‧羅柏（William Roper）親撰的傳記，約成書於 1556–1557 年，係現存最早、最貼近史實的摩爾一手傳記。多默‧摩爾（1478–1535）為英格蘭人文主義者、大法官，因拒絕承認亨利八世為教會首領而殉道，後被天主教會封聖。全書記其品德、信仰堅守及受難始末，是宗教改革時期天主教殉道文學的奠基之作。' },
          { title_zh: '坎特伯雷大主教湯瑪斯‧克蘭麥紀念傳', title_orig: 'Memorials of the Most Reverend Father in God Thomas Cranmer, sometime Lord Archbishop of Canterbury', author: 'Strype, John', era: '1694', place: 'London', language: '英文', intro: '英國宗教改革史家約翰‧史垂普（John Strype）所撰克蘭麥（Thomas Cranmer, 1489–1556）傳記，1694年於倫敦出版。克蘭麥為英格蘭宗教改革關鍵人物，首任坎特伯雷大主教，主導《公禱書》編纂，後於瑪麗女王統治期間以異端罪被燒死殉道。本書廣引原始文獻與書信，是研究英國宗教改革最重要的一手傳記史料，屬史傳藏改革家傳記性質，具典型殉道錄與改革家聖徒傳的雙重特徵。' },
          { title_zh: '教會最卓越教父傳：首四世紀', title_orig: 'Lives of the most eminent fathers of the church that flourished in the first four centuries', author: 'William Cave', era: '1683', place: 'Oxford', language: '英文', intro: '英國教會史家威廉‧凱夫（William Cave, 1637–1713）所著教父傳記集，收錄首四世紀最著名教父的生平事蹟與著作梗概，依時代先後編排。原著初版於1683年，題名《Ecclesiastici》，本版為1840年牛津重印本（H. Cary 編校，共三卷）。凱夫以廣博的拉丁希臘文獻為基礎，系統呈現使徒後教父至尼西亞前後諸教父（伊格那丟、坡旅甲、猶斯定、俄利根、居普良、亞他那修等）之生平、神學立場及殉道記錄，是英語世界研究早期教父傳記的重要近代參考文獻。' },
          { title_zh: '耶穌基督會眾之初愛——初代基督徒信仰與聖潔生活真貌', title_orig: 'Die erste Liebe der Gemeinen Jesu Christi, das ist: Wahre Abbildung der ersten Christen nach ihrem lebendigen Glauben und heiligen Leben', author: 'Gottfried Arnold', era: '1696', place: 'Frankfurt', language: '德文', intro: '德國敬虔主義神學家戈特弗里德‧阿諾德（Gottfried Arnold, 1666–1714）早期代表作，以德文寫成，出版於法蘭克福。全書旨在描繪初代基督徒的靈性面貌——他們活潑的信仰與聖潔的生活——作為敬虔運動對當時僵化國家教會的批判與更新呼召。阿諾德援引教父文獻與初期教會史料，勾勒出使徒時代會眾（Gemeinde）彼此相愛、捨棄世俗的理想圖景。本書為其後來更具影響力的《公正教會暨異端史》（1699）奠定基礎，是近代新教敬虔主義史傳文學的重要先驅，同時亦具初代教會靈修史的一手詮釋價值。' }
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
          { title_zh: '近代海外宣道會史', title_orig: 'History of the Modern Missionary Societies', author: '佚名輯（新教宣道會傳統）', era: '十九世紀', place: '倫敦', language: '英文', intro: '此編綜述十八世紀末以降新教宣教運動的勃興，自威廉‧克里赴印度、倫敦會與美部會的設立，到向非洲、太平洋與中國內地的拓展。書中以各差會為單元，記其成立宗旨、籌款體制、宣教士派遣與本地教會建立，並反映福音奮興與帝國擴張交織的時代氛圍。它把零散的差會報告整合為一部運動史，是理解新教全球化與近代宣教神學的入門綱要。' },
          { title_zh: '中華大帝國史', title_orig: 'Historia del Gran Reino de la China', author: '門多薩(Juan González de Mendoza)', era: '1585', place: '羅馬', language: '西班牙文', intro: '奧斯定會士門多薩（Juan González de Mendoza）受教宗委託編纂，於一五八五年在羅馬刊行，是歐洲第一部全面詳述中國的專著。全書匯整早期赴華傳教士、使節與商旅的見聞，記述中國的疆域、物產、典章制度、宗教風俗與印刷火炮等技藝。出版後數十年間譯成多種歐洲語文、再版數十次，成為大航海時代歐洲認識中國的權威讀本，深刻形塑近代早期歐人的「中華帝國」想像。' },
          { title_zh: '中華帝國全志', title_orig: 'Description géographique, historique, chronologique, politique et physique de l’Empire de la Chine', author: '杜赫德(Jean-Baptiste Du Halde)', era: '1735', place: '巴黎', language: '法文', intro: '耶穌會士杜赫德（Jean-Baptiste Du Halde）雖未親至中國，卻匯集在華會士寄回的報導、書信與譯稿，於一七三五年在巴黎刊行此四卷巨著。內容涵蓋中國各省地理、歷史沿革、政制律法、經濟物產、儒家經典與醫藥技藝，並附精細地圖。全書集耶穌會在華觀察之大成，迅即譯成多國文字，成為啟蒙時代歐洲認識中國的權威，伏爾泰（Voltaire）等思想家皆深受其影響。' },
          { title_zh: '中國上古史', title_orig: 'Sinicae Historiae Decas Prima', author: '衛匡國(Martino Martini)', era: '1658', place: '慕尼黑', language: '拉丁文', intro: '耶穌會士衛匡國（Martino Martini）依據中國正史與編年典籍，於一六五八年在慕尼黑刊行，是首部以西文向歐洲系統介紹中國上古信史的著作。全書自伏羲（伏羲氏）述起，歷述三皇五帝、夏商周三代以至西漢，並推算中國紀年遠早於通行的聖經編年。此說在歐洲引發年代學與《聖經》紀年的激烈爭論，對近代早期西方的世界史框架與漢學奠基影響深遠。' },
          { title_zh: '中國新史', title_orig: 'Nouvelle relation de la Chine', author: '安文思(Gabriel de Magalhães)', era: '1688', place: '巴黎', language: '法文(原葡文)', intro: '葡萄牙籍耶穌會士安文思（Gabriel de Magalhães）久居北京、供職清廷，以葡文撰成此書，身後於一六八八年在巴黎譯為法文刊行。全書為其親歷的第一手記述，描繪清初中國的政治體制、官僚科舉、宮廷生活、京城風貌、語言文字與物產工藝，尤詳於北京城與皇宮見聞。內容兼具細膩觀察與切身體驗，是十七世紀歐洲認識清初中國政教與社會的重要文獻。' }
        ,
          { title_zh: '耶穌會士關係文書：新法蘭西耶穌會傳教士旅行與探索紀錄（1610–1791）', title_orig: 'The Jesuit relations and allied documents: travels and explorations of the Jesuit missionaries in New France, 1610–1791', author: 'Reuben Gold Thwaites (ed.); Arthur Edward Jones (contrib.)', era: '1610–1791', place: 'Cleveland', language: '英文', intro: '本書彙集耶穌會士每年呈報羅馬與巴黎上級的「關係」（Relations）及相關文獻，記錄傳教士在北美新法蘭西（今加拿大魁北克、五大湖地區）的旅行、探索、佈道與殉道事蹟，時跨 1610 至 1791 年。文件兼含原住民族誌觀察與自然地理記述，是近代天主教海外傳教史最重要的一手史料叢刊之一。Thwaites 版共 73 卷，附英法對照，為學術標準版。' },
          { title_zh: '日本交趾馬拉巴爾錫蘭及東方諸國傳教紀略', title_orig: 'Relation de ce qui s\'est passé depuis quelques siècles, jusques à l\'an 1644 au Japon, à la Cochinchine, au Malabar, en l\'isle de Ceylan et en plusieurs autres isles et royaumes de l\'Orient compris sous le nom des provinces du Japon et du Malabar, de la Compagnie de Jésus', author: 'António Francisco Cardim（第一部）；Francesco Barretto（第二部）；法譯者：Jacques de Machault', era: '1645–1646', place: 'Paris', language: '法文', intro: '葡萄牙耶穌會士卡爾定（António Francisco Cardim）與巴雷多合著之東方傳教紀錄，成書於1645年巴黎。全書縱覽近數世紀間耶穌會在日本、交趾（越南）、馬拉巴爾（印度）及其他東方諸國的傳教經過，涵蓋殉道事跡、教務沿革與異文化接觸。卡爾定曾親歷日本禁教迫害，本書兼具親歷者目擊報告與史志性質，是反宗教改革時期天主教海外擴張的一手史料，對研究17世紀東亞傳教史具有重要文獻價值。' },
          { title_zh: '耶穌會士阿瓜維瓦神父赴大蒙兀兒傳教記', title_orig: 'Missione al Gran Mogor del padre Ridolfo Aquaviva della Compagnia di Gesù, sua vita e morte e d\'altri quattro compagni', author: 'Daniello Bartoli', era: '初版 1653 年', place: 'Roma', language: '義大利文', intro: '耶穌會官方史家巴爾托利（Daniello Bartoli）所著耶穌會士傳記。記述里多爾福‧阿瓜維瓦（Ridolfo Aquaviva）神父奉派赴蒙兀兒皇帝阿克巴宮廷（1580–1583）之傳教經歷，及其後在果亞薩爾塞特地區與四位同伴一同殉道始末。阿瓜維瓦為耶穌會在印度最早殉道者之一，本書兼具傳記、殉道錄與傳教史性質，為反宗教改革時代耶穌會東方傳教文獻之經典，收於巴爾托利《全集》中。' },
          { title_zh: '巴拉圭史：耶穌會傳教事業之建立', title_orig: 'Histoire du Paraguay, contenant l\'établissement des Jésuites dans ce pays, et leurs progrès chez divers peuples sauvages', author: 'Pierre-François-Xavier de Charlevoix', era: '1756', place: 'Paris', language: '法文', intro: '法國耶穌會士夏勒瓦（Charlevoix）所著巴拉圭史，詳述耶穌會在南美洲拉普拉塔地區建立「減縮村」（Reducciones）傳教體制的經過。全書以編年敘事鋪陳傳教士進入原住民瓜拉尼族社群、建立自治基督教公社的歷程，兼及政教衝突與殖民地行政。此書為十八世紀最完備的耶穌會南美傳教史料之一，亦是研究天主教反宗教改革海外宣教策略的重要原始文獻，具史傳藏傳教史部典型性格。' },
          { title_zh: '新法蘭西通史暨北美旅行歷史日誌', title_orig: 'Histoire et description générale de la Nouvelle France avec le journal historique d\'un voyage fait par ordre du roi dans l\'Amérique Septentrionale', author: 'Pierre-François-Xavier de Charlevoix', era: '1744', place: 'Paris', language: '法文', intro: '耶穌會士夏爾勒瓦（Pierre-François-Xavier de Charlevoix，1682–1761）奉法王之命赴北美考察後撰成之六卷本鉅著，1744年於巴黎刊行。前二卷為新法蘭西（阿卡迪亞、加拿大、路易斯安那）政治軍事史，第三卷為作者親歷之旅行日誌，記錄聖勞倫斯河至新奧爾良沿途見聞。全書詳述耶穌會傳教佈局、原住民歸化事業及法國天主教在北美之拓展，為北美傳教史不可或缺之第一手史料。' },
          { title_zh: '日本帝國基督教創立興衰史', title_orig: 'Histoire de l\'établissement, des progrès et de la décadence du Christianisme dans l\'empire du Japon', author: 'Pierre-François-Xavier de Charlevoix', era: '1715', place: 'Rouen', language: '法文', intro: '法國耶穌會士沙勒瓦（Pierre-François-Xavier de Charlevoix，1682–1761）所著，1715 年刊於盧昂，共三卷。全書在法國耶穌會士尚‧克拉塞（Jean Crasset）1689 年舊著基礎上大幅擴寫，系統記述十六至十七世紀耶穌會傳教士（方濟各‧沙勿略以降）在日本傳播基督教的始末：創立期的迅速擴張、幕府彈壓與殉道、最終遭禁絕的經過，並附日本風俗、地誌與博物誌廣泛注記。為天主教遠東傳教史最早的法語系統敘述之一，史料價值甚高，兼具編年與傳記體裁，屬近代反宗教改革傳教運動一手史著。後有 1736 年二卷本、1754 年六卷巴黎精修版等多個版本。' },
          { title_zh: '印地亞斯史', title_orig: 'Historia de las Indias', author: 'Bartolomé de las Casas', era: '1527–1561', place: 'Madrid', language: '西班牙文', intro: '多明我會士、恰帕斯主教巴托洛梅‧德‧拉斯‧卡薩斯（1484–1566）歷三十年撰成的美洲傳教史鉅著，涵蓋 1492 至 1520 年代西班牙人征服印地亞斯（西印度群島與美洲大陸）之始末。作者以親歷者身分記錄原住民遭受殖民暴行的第一手見聞，並從天主教倫理立場為其發聲，成為宗教改革時代護教人道主義的代表文獻，亦是拉丁美洲教會史與傳教學的基礎史料。' },
          { title_zh: '大中國志', title_orig: 'Imperio de la China i cultura evangelica en él, por los religiosos de la Compañía de Jesús', author: 'Álvaro Semedo（曾德昭）', era: '1642', place: 'Madrid', language: '西班牙文', intro: '葡萄牙籍耶穌會士曾德昭（謝務祿）在華傳教逾二十年後撰成此書，1642年以西班牙文刊於馬德里。全書分兩部：前半詳述中國地理、人口、風俗、禮制、科舉與宗教，係最早系統向歐洲介紹明末中國的第一手民族誌；後半記述耶穌會在華傳教史，含南京教難（1616）、景教碑發現等要事。原葡文稿先以義大利文（1643）出版，後譯英法等語，成17世紀歐洲漢學奠基文獻之一，兼具傳教報告與域外遊記性質。' },
          { title_zh: '耶穌會史——亞洲（八書）', title_orig: 'Dell\'istoria della Compagnia di Gesù l\'Asia libri otto', author: 'Daniello Bartoli', era: '1650', place: 'Roma', language: '義大利文', intro: '意大利耶穌會士巴爾托利所著《耶穌會史》亞洲卷，共八書，1653年初版於羅馬，為歐洲首部大規模義大利文亞洲傳教通史。內容涵蓋印度、波斯、麻六甲、果阿、中國、日本等地耶穌會宣教始末，尤詳日本教難與中國入教經過，兼錄各地風土民情。本書以地理分卷取代年代紀事體例，文學筆法卓越，是反宗教改革時期耶穌會對外傳教最重要的一手史料之一。' },
          { title_zh: '毀滅印地亞斯簡述', title_orig: 'Brevísima relación de la destruición de las Indias', author: 'Bartolomé de las Casas', era: '1552', place: 'Sevilla', language: '西班牙文', intro: '道明會士、恰帕斯主教拉斯‧卡薩斯親歷西班牙征服美洲的暴行，以第一人稱見證陳述向卡斯提亞王廷呈報，逐一羅列加勒比海、中美洲、南美洲各地原住民遭屠殺、奴役、強徵勞動的慘況。此書是天主教傳教史上最早的良心異議文獻之一，促成1542年「新法」護印人律令的頒布，亦開啟近代基督教社會倫理對殖民暴力的批判傳統，為研究十六世紀天主教傳教運動與殖民接觸史不可或缺的原典。' }
        ]
      },
      {
        key: 'overseas-ethnography',
        label: '域外民族誌部',
        label_en: 'Records of Overseas Peoples and Customs',
        desc: '近代天主教宣教士（多為耶穌會）對中國以外各地——日本、印度、美洲、非洲、大洋洲——民族、風俗、自然與宗教的記錄。',
        works: [
          { title_zh: '日本史', title_orig: 'História do Japão', author: '路易斯‧佛洛伊斯(Luís Fróis)', era: '約 1583–1597(稿本)', place: '日本', language: '葡萄牙文', intro: '久居日本三十餘年的耶穌會士佛洛伊斯(Luís Fróis)所撰，逐年詳載戰國時代日本的政教局勢、群雄戰亂與庶民風俗，對織田信長等人物有近身觀察。其筆下兼及佛教宗派與神道信仰，是歐人理解十六世紀日本社會的第一手史料；另著有歐洲與日本文化對照之作，以條列方式並陳兩地禮俗、衣食、婦女與信仰的差異，開比較民族誌之先聲。' },
          { title_zh: '印度習俗報告', title_orig: 'Informatio de quibusdam moribus nationis Indicae', author: '羅伯托‧德‧諾比利(Roberto de Nobili)', era: '約 1613', place: '印度馬杜賴(Madurai)', language: '拉丁文', intro: '在南印度馬杜賴(Madurai)宣教的耶穌會士諾比利(Roberto de Nobili)所撰，主張須區分宗教信仰與印度社會習俗，認為種姓、聖線等多屬世俗風俗而非異教崇拜。為此他採行婆羅門式生活與服飾以親近上層，記述當地種姓制度、潔淨觀與印度禮俗，是耶穌會「適應策略」在印度的代表文獻，亦為南印度社會的早期民族誌觀察。' },
          { title_zh: '印度自然與道德史', title_orig: 'Historia natural y moral de las Indias', author: '何塞‧德‧阿科斯塔(José de Acosta)', era: '1590', place: '塞維利亞(Sevilla)', language: '西班牙文', intro: '耶穌會士阿科斯塔(José de Acosta)根據親歷祕魯與墨西哥的見聞而成，前半論新大陸的地理、氣候、礦產與動植物，後半記述印第安民族的宗教、曆法、政制與風俗。他嘗試以自然因果解釋美洲物種與人群的由來，並比較阿茲特克、印加的信仰與制度，是歐洲認識新大陸自然史與美洲原住民民族誌的開創性著作，影響後世博物學與宗教史甚鉅。' },
          { title_zh: '耶穌會通訊集(新法蘭西報告)', title_orig: 'Relations des Jésuites de la Nouvelle-France', author: '在新法蘭西的耶穌會士', era: '1632–1673', place: '巴黎', language: '法文', intro: '北美新法蘭西(今加拿大魁北克一帶)的耶穌會士逐年寄回法國、彙編刊行的報告集。傳教士深入原住民部落，詳載休倫(Huron)、易洛魁(Iroquois)、阿爾岡昆等民族的語言、習俗、信仰、戰爭與季節生活，並記錄宣教的艱辛與殉道。內容兼具傳教紀錄與細緻觀察，是十七世紀北美原住民民族誌與語言研究最重要的第一手史料之一。' },
          { title_zh: '衣索比亞史', title_orig: 'História da Etiópia', author: '佩德羅‧派斯(Pedro Páez)', era: '約 1622', place: '衣索比亞', language: '葡萄牙文', intro: '久居衣索比亞的耶穌會士派斯(Pedro Páez)所撰，以親身遊歷與通曉當地語言的見聞，詳載衣索比亞的歷史、地理、物產與風土。他是公認首位親抵並記述青尼羅河源頭的歐洲人，書中亦深入描寫衣索比亞正教會的禮儀、教義與宮廷政教關係，駁正前人傳聞之誤，為歐洲認識東北非高原民族與基督教古國的重要史料。' },
          { title_zh: '靈性征服', title_orig: 'La Conquista Espiritual', author: '安東尼奧‧魯伊斯‧德‧蒙托亞(Antonio Ruiz de Montoya)', era: '1639', place: '馬德里', language: '西班牙文', intro: '耶穌會士蒙托亞(Antonio Ruiz de Montoya)記述其在巴拉圭一帶建立瓜拉尼(Guaraní)歸化區(reductions)的經過，描寫瓜拉尼人的生活、習俗、信仰與遷徙，以及歸化區面對奴隸獵人時的處境。作者通曉瓜拉尼語，另編有瓜拉尼語法與辭典，本書因而兼具宣教史、南美原住民民族誌與語言保存的多重價值，是認識瓜拉尼民族的關鍵文獻。' },
          { title_zh: '馬里亞納宣教記', title_orig: 'Marianas Mission Records', author: '迭戈‧路易斯‧德‧桑維托雷斯(Diego Luis de San Vitores)', era: '1668–1672', place: '關島(Guam，馬里亞納群島)', language: '西班牙文', intro: '耶穌會士桑維托雷斯(Diego Luis de San Vitores)在馬里亞納群島(關島一帶)宣教期間留下的記錄，是大洋洲密克羅尼西亞查莫羅(Chamorro)人最早的民族誌與宣教文獻，描寫其社會組織、習俗與信仰。作者致力於當地傳教並最終在島上殉道，相關報告為後世研究查莫羅原住民早期歷史、語言與歐人接觸提供了珍貴的第一手資料。' }
        ,
          { title_zh: '秘魯偶像崇拜之剷除', title_orig: 'Extirpación de la idolatría del Pirú', author: 'Pablo José de Arriaga', era: '1621', place: 'Lima', language: '西班牙文', intro: '耶穌會士阿里亞加（1564–1622）赴秘魯傳教逾三十年，此書為其主導安地斯「剷偶像」巡查運動的第一手報告，1621 年刊於利馬。全書記錄印加遺民的神祇、祭儀、神聖場所（瓦卡）及薩滿角色，兼附訊問指南與懺悔導引，是反宗教改革時期天主教傳教史與安地斯宗教民族誌的原典文獻，亦是研究殖民初期教會如何定義並打壓「偶像崇拜」的核心史料。' },
          { title_zh: '美洲原住民風俗與遠古風俗之比較', title_orig: 'Moeurs des sauvages amériquains comparées aux moeurs des premiers temps', author: 'Joseph-François Lafitau', era: '1724', place: 'Paris', language: '法文', intro: '法國耶穌會傳教士拉菲托（1681–1746）於北美新法蘭西駐紮五年，親身觀察易洛魁人的習俗、宗教信仰與社會制度，著成此書。書名「上古風俗」指希臘羅馬及近東古文明，作者以比較方法論證美洲原住民與古代諸民族存在深層共性，進而建立護教論據：全人類普遍認同神之存在與靈魂不滅，藉此反駁自然神論者與無神論者。此書是反宗教改革時期耶穌會傳教士民族誌的代表原典，亦為近代比較宗教學的先驅文獻。' },
          { title_zh: '葡萄牙人新世界發現與征服史', title_orig: 'Histoire des découvertes et conquestes des Portugais dans le Nouveau Monde', author: 'Joseph-François Lafitau', era: '1733', place: 'Paris', language: '法文', intro: '法國耶穌會士拉菲托（1681–1746）所著葡萄牙人新世界探險史，涵蓋1415至1580年代間達伽馬、麥哲倫、卡布拉爾等人的遠洋航行，兼記非洲沿海、印度、日本及南美洲見聞。作者以耶穌會傳教士視角貫穿全書，將葡萄牙帝國擴張與天主教傳教事業緊密相連，記述耶穌會在東印度群島與日本的佈道開拓，是近代天主教傳教史與域外民族誌的重要原始文獻。' },
          { title_zh: '印第安群島辯護概史', title_orig: 'Apologética historia sumaria', author: 'Bartolomé de las Casas', era: '約1550–1559年成書', place: 'Madrid', language: '西班牙文', intro: '西班牙道明會士、恰帕斯主教拉斯卡薩斯（Bartolomé de las Casas，約1484–1566）畢生為美洲原住民權利辯護。本書為其龐大民族誌力作，成書於1550年代，原為《印第安通史》（Historia general de las Indias）第68章，後獨立擴寫成卷。以亞里斯多德—基督教哲學架構系統比較美洲各族群與希臘羅馬之習俗、制度與理性能力，力證印第安人完全具備人的尊嚴與自治能力；與1550年瓦拉多利德辯論會密切相關（辯論所用文本為同期另著《爭論》，本書為其理論底本）。為近代天主教傳教史與護教論中最重要的域外民族誌原典之一。' }
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
        ,
          { title_zh: '古今教會史', title_orig: 'An ecclesiastical history, antient and modern, from the birth of Christ to the beginning of the present century', author: 'Johann Lorenz Mosheim', era: '1758', place: 'London', language: '英文', intro: '德國路德宗神學家莫斯海姆（Johann Lorenz Mosheim，1693–1755）所著教會通史巨作，英譯本於1758年在倫敦刊行。全書以編年體貫通耶穌降生至十八世紀初，按世紀分章，涵蓋教義發展、教會組織、異端興衰、宗教改革及各主要宗派演變，被譽為近代批判教會史學之奠基著作。莫斯海姆援引原始文獻、力求客觀，開啟啟蒙時代以學術方法治教會史的先河，深刻影響此後兩世紀的教會史編纂傳統。' },
          { title_zh: '教會編年史', title_orig: 'Annales ecclesiastici', author: 'Caesar Baronius（切撒雷‧巴羅尼奧）', era: '1588–1607', place: 'Romae', language: '拉丁文', intro: '天主教樞機主教巴羅尼奧耗費數十年撰成的十二卷拉丁文教會編年史，自耶穌降生紀元逐年鋪敘至1198年，以原始文獻為據逐條考辨。此書直接針對新教《馬德堡世紀史》而作，是反宗教改革最重要的史學回應，確立天主教教會史寫作的典範。巴羅尼奧廣徵梵蒂岡檔案與古抄本，詳述大公會議、宗徒繼承、殉道錄與帝教關係，迄今仍是研究早期至中世紀教會史不可或缺的一手史料。' },
          { title_zh: '君士坦丁大帝前基督教史事疏證', title_orig: 'Commentaries on the affairs of the Christians before the time of Constantine the Great', author: 'Johann Lorenz Mosheim', era: '1813', place: 'London', language: '英文', intro: '莫斯海姆（1693–1755）為近代教會史學奠基者，素有「近代教會史之父」之稱。本書為其晚年巨著，以拉丁文撰成，系統疏證君士坦丁大帝（313年）以前三百年間基督教會之史事，涵蓋早期護教、異端爭論、殉道浪潮、教會組織成形諸議題。莫氏採批判性文獻方法，力求史料徵信，擺脫教派護教偏見，開歐洲教會史學客觀化之先河。本英譯本1813年於愛丁堡刊行，為近代新教史傳藏中論早期教會史之重要原典文獻。' },
          { title_zh: '教會前六世紀史料彙編', title_orig: 'Mémoires pour servir à l\'histoire ecclésiastique des six premiers siècles', author: 'Louis-Sébastien Le Nain de Tillemont', era: '1693', place: 'Paris', language: '法文', intro: '法國楊森派學者蒂勒蒙（Tillemont，1637–1698）畢生巨著，全書共十六冊（1693–1712，後八冊由秘書 Michel Tronchay 身後整理出版），系統彙編並考證教會前六世紀（使徒時代至額我略一世）之史料，涵蓋殉道者事蹟、教父生平、大公會議始末及各地異端源流。體裁介乎編年與傳記之間，逐事附錄原始文獻出處，考辨精嚴，為後世教會史研究之奠基工具，英國史家吉朋撰《羅馬帝國衰亡史》時大量援引此書。' },
          { title_zh: '舊新約教會史略', title_orig: 'Kurtz gefaßte Kirchen-Historie des Alten und Neuen Testaments', author: 'Gottfried Arnold', era: '1708', place: 'Leipzig', language: '德文', intro: '德國敬虔主義史家戈特弗里德‧阿諾德（Gottfried Arnold, 1666–1714）所著教會史概要，以「舊約」與「新約」為雙主軸，貫通以色列至基督教初代的歷史脈絡，篇幅精簡（kurtz gefaßt），適合普及閱讀。阿諾德以《無偏黨教會暨異端史》（1699）享譽後世，此書延續其重視原始敬虔與忽視外在體制的史學立場，對早期教會精神生活著墨尤深，為近代新教教會史學重要一手文獻。' },
          { title_zh: '不列顛教會史', title_orig: 'The Church-History of Britain, from the Birth of Jesus Christ until the Year M.DC.XLVIII', author: 'Fuller, Thomas', era: '1655', place: 'London', language: '英文', intro: '湯瑪斯‧富勒（Thomas Fuller，1608–1661）所著英格蘭教會史鉅作，成書於1655年。全書涵蓋基督降生至1648年英格蘭內戰止，系統記述不列顛教會的興起、宗教改革、聖公會確立、清教徒運動與護國公時期的宗教變革。富勒以聖公會立場執筆，行文兼具史料引證與幽默筆法，是研究英格蘭宗教改革史與英國教會史不可或缺的近代一手文獻，亦為後世教會編年史學的重要典範。' },
          { title_zh: '脫利騰大公會議史', title_orig: 'Historia del Concilio Tridentino', author: 'Paolo Sarpi（薩爾皮）', era: '1619', place: 'London', language: '義大利文', intro: '威尼斯聖職修士保羅‧薩爾皮以筆名「皮耶特羅‧索阿韋‧波拉諾」在倫敦秘密出版，為脫利騰大公會議（1545–1563）首部大型批判性史著。全書依會期編年敘述神學辯論、教廷運作與各國政治角力，同情宗教改革立場，揭示羅馬教廷如何主導議程、壓制改革聲音。此書甫出版即遭天主教會列禁書目，旋即引發巴羅尼奧等人撰文反駁，成為反宗教改革時期教會史書寫論戰的核心文獻，對後世新教史學影響深遠。' },
          { title_zh: '原始基督教', title_orig: 'Primitive Christianity: or, the religion of the ancient Christians in the first ages of the gospel', author: 'William Cave', era: '1673', place: 'London', language: '英文', intro: '英國聖公會神職人員、教父學學者威廉‧凱夫（William Cave, 1637–1713）所著。初版於1673年，1675年出版增訂三部本（即本條目所據版本）。全書系統描述使徒時代至四世紀初期基督徒的信仰、敬拜、聖事、齋戒、佈道及日常生活習俗，意在證明英國國教傳統與古公教精神一脈相承。此書為宗教改革後英語世界最具代表性的「原始教會」溯源著作之一，與凱夫的《使徒古物志》（Antiquitates Apostolicae, 1675）及《使徒傳》（Apostolici, 1677）相輔相成，奠定後世聖公宗教父學研究之基礎。' },
          { title_zh: '不偏不倚教會暨異端通史', title_orig: 'Unparteyische Kirchen- und Ketzer-Historie, vom Anfang des Neuen Testaments bis auff das Jahr Christi 1688', author: 'Gottfried Arnold', era: '1699', place: 'Frankfurt am Main', language: '德文', intro: '德意志路德宗敬虔派神學家哥特弗里德‧阿諾德（Gottfried Arnold，1666–1714）之扛鼎之作。全書上起新約時代，下迄1688年，廣納教會正統與所謂異端之史料，以「公正」為標榜，大膽為諾斯底派、靈意派、中世紀異端等遭迫害者翻案，視其為真正福音精神的守護者。此書突破舊式護教史觀，開近代教會史批判研究之先河，對施萊爾馬赫等後世新教思想家影響深遠，是宗教改革後敬虔主義時代最重要的一手史著之一。' },
          { title_zh: '韃靼教會史', title_orig: 'Historia Tartarorum Ecclesiastica: Adjecta est Tartariæ Asiaticæ secundum recentiores Geographos in Mappa delineatio', author: 'Johann Lorenz von Mosheim', era: '1741', place: 'Helmstadii', language: '拉丁文', intro: '德國路德宗神學家莫斯海姆（1693–1755）所著拉丁文教會史，系統考述基督教（景教與天主教）在蒙古韃靼諸部中傳播的歷史，上溯中世紀蒙古帝國時期的傳教活動，下至近代傳教士入境中亞之努力，兼論蒙古統治者的宗教寬容政策及伊斯蘭、佛教之競爭。書末附史料輯錄（書信與文獻）及亞洲韃靼地區地圖。莫斯海姆為近代實用教會史學之奠基者，此書是早期對中亞基督教史的專門學術論著，具重要史料與研究雙重價值。' },
          { title_zh: '教會歷史論述', title_orig: 'Discours sur l\'histoire ecclésiastique', author: 'Claude Fleury', era: '1708', place: 'Paris', language: '法文', intro: '法國天主教神父、加里坎主義歷史學家弗勒里（Claude Fleury，1640–1723）所撰的教會史方法論論述，為其畢生鉅著《教會史》（Histoire ecclésiastique，20卷，涵蓋基督升天至1414年）的導論性文字。弗勒里在文中闡述如何閱讀與詮釋教會歷史，主張回歸原始史料、擺脫教派偏見，帶有加里坎主義色彩（限制教宗絕對權威）。作為近代教會史學方法的一手文獻，具重要史料價值。（首版1708年；OpenLibrary OL4763907W 為1747年再版）' }
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
        key: 'overseas-mission-versions',
        label: '域外宣教譯本部',
        label_en: 'Overseas Mission Vernacular Versions',
        desc: '近代新教宣教士為亞、非、美洲非漢語民族首譯的聖經，多為該語言史上第一部聖經。',
        works: [
          { title_zh: '艾略特印第安語聖經', title_orig: 'Mamusse Wunneetupanatamwe Up-Biblum God', author: '艾略特(John Eliot)', era: '1663', place: '麻薩諸塞劍橋', language: '麻薩諸塞(阿爾岡昆)語', intro: '清教徒宣教士艾略特(John Eliot)為麻薩諸塞原住民所譯，是北美大陸印刷出版的第一部完整聖經，也是英語世界最早將整本聖經譯入無文字傳統民族語言的壯舉。他先為阿爾岡昆語建立拼寫系統，再逐卷迻譯，於劍橋印行。此譯本見證了「祈禱城鎮」中的早期原住民歸信，雖該語言後來幾近失傳，近年卻成為族群復興語言的珍貴依據。' },
          { title_zh: '克里塞蘭坡諸語聖經', title_orig: 'Bible (Bengali, Sanskrit, etc.)', author: '克里(William Carey)及塞蘭坡同工', era: '孟加拉文新約 1801 起，多語陸續', place: '印度塞蘭坡', language: '孟加拉文等四十餘種印度語言', intro: '被尊為近代新教宣教之父的克里(William Carey)與塞蘭坡同工(Serampore Trio)在丹麥屬地塞蘭坡主持的大規模譯經工程。自一八〇一年孟加拉文新約問世起，數十年間陸續以梵文及四十餘種印度次大陸語言迻譯刊行，奠定南亞各民族文字聖經的根基。雖部分早期譯本以準確度受後人檢討，其拓荒規模與對印度諸語印刷文化的貢獻仍無可取代。' },
          { title_zh: '耶德遜緬甸語聖經', title_orig: 'The Holy Bible (Burmese)', author: '耶德遜(Adoniram Judson)', era: '新約 1832‧全本 1834', place: '緬甸毛淡棉', language: '緬甸文', intro: '美國浸信會宣教士耶德遜(Adoniram Judson)歷經牢獄與喪親之苦，在緬甸數十年間完成的緬甸文聖經，新約於一八三二年、全本於一八三四年告成。他同時編纂緬英辭典，為緬甸文聖經研究立下標準。此譯本文辭典雅、流傳廣遠，至今仍是緬甸教會公認沿用的標準譯本，堪稱新教在東南亞最深遠的譯經成果之一。' },
          { title_zh: '馬丁波斯文與烏爾都文新約', title_orig: 'New Testament (Persian & Hindustani)', author: '馬丁(Henry Martyn)', era: '約 1810–1812', place: '印度‧波斯', language: '波斯文‧烏爾都文', intro: '劍橋才俊馬丁(Henry Martyn)受聘東印度公司隨軍牧師後投身譯經，於印度與波斯之間完成烏爾都文(印度斯坦文)及波斯文新約。他語言天賦過人，譯文以精審典雅見稱，深得波斯文人推重。惜其積勞成疾，一八一二年返英途中病逝於小亞細亞，年僅三十一歲，所留精譯遂成早逝宣教學者的不朽見證。' },
          { title_zh: '莫法特茨瓦納文聖經', title_orig: 'The Holy Bible (Setswana)', author: '莫法特(Robert Moffat)', era: '全本 1857', place: '南非庫魯曼', language: '茨瓦納文', intro: '倫敦傳道會宣教士莫法特(Robert Moffat)長年駐守南非庫魯曼(Kuruman)宣教站，為茨瓦納人建立文字並逐卷迻譯，於一八五七年完成全本聖經。這是非洲本土語言中第一部譯齊的整本聖經，他更親自設印刷機刊行。莫法特亦是探險家李文斯頓(David Livingstone)的岳父與同工，其譯經奠定了南部非洲教會以母語誦讀聖言的傳統。' }
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
          { title_zh: '東方宗教經典初譯', title_orig: 'Oupnek\'hat (Anquetil-Duperron) 等', author: '安克蒂爾-杜佩龍 (Abraham Hyacinthe Anquetil-Duperron) 等', era: '十八世紀末', place: '巴黎', language: '拉丁文‧法文', intro: '安克蒂爾-杜佩龍率先將祆教《阿維斯陀》與印度《奧義書》(由波斯文轉譯) 介紹入歐,其拉丁文《奧義書》譯本曾深深觸動叔本華。此類東方經典的初譯篳路藍縷、訛誤難免,卻打開了歐洲認識亞洲宗教的門徑,催生了十九世紀比較宗教與東方學的勃興。' },
          { title_zh: '中國哲學家孔子', title_orig: 'Confucius Sinarum Philosophus', author: '柏應理(Philippe Couplet)、殷鐸澤(Prospero Intorcetta)等', era: '1687', place: '巴黎', language: '拉丁文', intro: '由柏應理(Philippe Couplet)領銜彙整、殷鐸澤(Prospero Intorcetta)等耶穌會士數十年之力，將《大學》《中庸》《論語》譯為拉丁文並題獻法王路易十四。書前附孔子傳與中國經籍源流，是歐洲認識孔子與儒學的奠基之作，深刻塑造萊布尼茲、伏爾泰等啟蒙思想家對中國的想像，開歐洲漢學與比較宗教之先河。其「以儒詮教」的調適立場，亦預示了往後激烈的中國禮儀之爭。' },
          { title_zh: '四書拉丁譯稿', title_orig: 'Tetrabiblion Sinense de moribus (羅明堅譯稿)', author: '羅明堅(Michele Ruggieri)', era: '約 1590 年代(稿本)', place: '羅馬', language: '拉丁文', intro: '由最早入華耶穌會士之一羅明堅(Michele Ruggieri)所譯，是史上第一份《四書》的西文(拉丁文)翻譯，比刊行的《中國哲學家孔子》早近一世紀。譯稿完成後未付梓，長埋羅馬耶穌會與義大利圖書館檔案中，遲至近世方重見天日，學界始知西方接觸儒典之始遠早於前人所想，為歐洲漢學與中西經典互譯的真正開端留下珍貴的最初見證。' },
          { title_zh: '中華帝國六經', title_orig: 'Sinensis Imperii Libri Classici Sex', author: '衛方濟(François Noël)', era: '1711', place: '布拉格', language: '拉丁文', intro: '由耶穌會士衛方濟(François Noël)續譯，將六部儒家經典——含《大學》《中庸》《論語》《孟子》《孝經》與《小學》——譯為拉丁文於布拉格刊行，首度把《孟子》全帙系統地引入歐洲。其譯本與同年另刊的中國禮儀考辯相呼應，正值中國禮儀之爭白熱之際，既擴充了歐洲對儒家倫理的整體認識，亦成為當時論辯祭祖祭孔性質的重要文獻依據。' }
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
  name: '書函藏',
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
    summary: '新教與天主教在宗教改革後各自整飭崇拜禮文，並以聖樂相輔。本部三分而觀其全：改教者重訂母語崇拜，脫利騰會議統一羅馬禮，作曲家則以詩篇與受難曲將神學化為聲音。',
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
        desc: '脫利騰會議後羅馬天主教統一頒行的彌撒、日課與聖事禮典，確立四百年通行的特倫多禮。',
        works: [
          { title_zh: '羅馬彌撒經書', title_orig: 'Missale Romanum', author: '教宗庇護五世（Pius V）頒行', era: '一五七〇年', place: '羅馬', language: '拉丁文', intro: '脫利騰會議授權、教宗庇護五世以《Quo primum》詔書頒行的羅馬天主教彌撒定本，統一了西方拉丁禮的彌撒舉行方式，史稱特倫多彌撒。經書詳載每日彌撒的禱文、經課、儀節與禮規，廢止諸多地方禮而立羅馬禮為通則。此本歷經數次小幅修訂沿用近四百年至一九六二年，是反改革時期天主教禮儀統一的核心成果，象徵教會面對新教挑戰的制度回應。' },
          { title_zh: '羅馬日課經', title_orig: 'Breviarium Romanum', author: '教宗庇護五世（Pius V）頒行', era: '一五六八年', place: '羅馬', language: '拉丁文', intro: '脫利騰改革後庇護五世頒行的天主教時辰祈禱定本，規範神職與修會每日七時辰的誦經、聖詠、讀經與禱文。日課以聖詠貫穿一週、配合教會年曆與聖人紀念，是神職人員的法定祈禱義務。此本整理繁雜的中世紀傳統,使全教會時辰祈禱趨於一致，與《羅馬彌撒經書》並為特倫多禮的兩大支柱，維繫了近代天主教靈修生活的節律與統一。' },
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
  name: '詩藝藏',
  name_en: 'Poetry and Arts Treasury',
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
        
          { title_zh: '懲戒之益處，或論希伯來書第十二章五至十一節之七篇講道', title_orig: 'Profit des chastimens, ou Sept sermons sur l\'exhortation contenue en l\'Epist. aux Hébrieux chap. XII. v. 5.6.7.8.9.10.11. faits en l\'église de Genève', author: 'Bénédict Turrettini（圖雷蒂尼），1588-1631', era: '1630', place: '日內瓦（Geneva）', language: '法文', intro: '日內瓦改革宗牧師暨神學家圖雷蒂尼（系統神學家弗朗西斯‧圖雷蒂尼之父）於日內瓦教會所講的七篇連續講道，逐節詮釋《希伯來書》十二章五至十一節「主所愛的祂必管教」之勸勉，闡發苦難與懲戒對信徒的屬靈益處與慈父般的管教神學。屬十七世紀初新教正統時期的牧養佈道作品，兼具加爾文派釋經與敬虔勸勉色彩，1630 年由 P. Aubert 在日內瓦印行。' },
          { title_zh: '五十講道集：論基督教信仰諸要義（分三卷）', title_orig: 'Sermonum decades quinque, de potissimis christianae religionis capitibus, in tres tomos digestae', author: 'Bullinger, Heinrich (1504-1575)（亨利‧布靈格）', era: '1549–1552', place: '蘇黎世（Zürich）', language: '拉丁文', intro: '瑞士改革宗神學家、慈運理繼任者布靈格的代表作《五十講道集》（Decades），原以五個「十講」共五十篇系統講道，闡述基督教信仰核心要義：神的話、信經、十誡、聖事、教會、稱義與善行等，兼具講道與教義綱要性質。此書於英格蘭被列為神職人員必讀，深刻形塑改革宗正統。本筆為 1586 年蘇黎世拉丁文三卷合訂重印本。' },
          { title_zh: '論基督之言六篇講道', title_orig: 'Sei homilie sopra le parole di Iesu Christo', author: '貝內迪克‧圖瑞汀（Bénédict Turrettini，1588-1631）', era: '1623', place: '日內瓦（Geneva）', language: '義大利文', intro: '日內瓦改革宗牧師暨神學教授圖瑞汀以義大利文寫成的六篇講道集，逐篇默想基督的話語，向僑居日內瓦的義大利歸正信徒群體宣講。作者為盧卡流亡家族後裔、名神學家弗朗西斯‧圖瑞汀之父，曾將多特會議信條引入法國。本書屬十七世紀新教正統與敬虔交會時期的牧養講道，文字虔敬、辯才出眾，見證宗教改革後義語歸正講道傳統。' }
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
        
          { title_zh: '恩典之道：論聖靈施行基督救贖之工（法譯本《祂要榮耀基督》）', title_orig: 'The Method of Grace in Gospel-Redemption（原著英文）；法譯本題作 Il parlera de Christ : l\'oeuvre du Saint-Esprit dans le salut', author: 'John Flavel（約翰‧弗拉維爾）', era: '原著 1681 年', place: '法譯本出版地：Chalon-sur-Saône（法國）；合作地 Gagnoa（科特迪瓦），出版商 Europresse', language: '英文', intro: '英格蘭清教徒、被逐長老派牧師弗拉維爾（約1628–1691）的救恩論名著，由三十五篇講道組成，逐層闡明聖靈如何將基督已成就的救贖實際施行於信徒心中——即恩典運行之法與得救次第。全書貫穿改革宗正統與敬虔精神，反覆催逼讀者省察基督是否已親身應用於己魂。此為法譯本，題作《祂要榮耀基督》，1995 年刊行。' },
          { title_zh: '勸悔改歸正得生', title_orig: 'A Call to the Unconverted to Turn and Live', author: 'Richard Baxter（理查‧巴克斯特）', era: '1658 年', place: '倫敦（London）', language: '英文', intro: '英國清教徒牧師理查‧巴克斯特（1615–1691）一六五八年於倫敦出版的福音勸勉之作。全書以以西結書「我斷不喜悅惡人死亡，惟喜悅他回頭離開所行的道而存活」為主軸，懇切呼籲尚未悔改歸正者離棄罪惡、轉向上帝而得永生。文字熱切懇摯，兼具教牧勸戒與佈道呼召，為清教敬虔運動經典，影響後世福音奮興甚鉅，當時即廣為流傳並譯成多種語言。' },
          { title_zh: '論不得重生者已逝靈魂在地獄囚牢中不可言喻之悲慘', title_orig: 'A discourse of the unspeakable misery of the departed spirits', author: 'John Flavel（約翰‧弗拉維爾）', era: '約 17 世紀末', place: 'London', language: '英文', intro: '英格蘭清教徒長老會牧師約翰‧弗拉維爾（約 1627–1691）的講道體論述。弗拉維爾任職於德文郡達特茅斯，為一六六二年大驅逐後堅守的不從國教派牧者，著作豐富、敬虔深刻。本篇以警世筆觸闡述失喪者死後靈魂所受不可言喻之痛苦，意在喚醒聽眾悔改歸正，是新教改革宗正統與敬虔傳統下典型的末世警誡講章；本書目為一七五○年倫敦重印本。' },
          { title_zh: '聖徒的強心劑', title_orig: 'The Saints Cordials', author: 'Richard Sibbes（理查‧西布斯）', era: '1629', place: '倫敦（London）', language: '英文', intro: '英格蘭清教徒名牧理查‧西布斯（1577–1635）的講道集，1629 年初版於倫敦，收錄二十九篇講章。西布斯終生留在英格蘭國教會內，依《公禱書》敬拜，被視為與柏金斯、卜雷斯頓並列的主流清教徒代表。其講道以「甘甜」著稱，常將聽者的心思情感引向救主基督，本書即為撫慰、堅固信徒靈魂的敬虔之作。近代研究指出，此 1629 版部分篇章或非西布斯親撰，三篇歸於他人（含胡克），另十一篇來源存疑。' },
          { title_zh: '剖開心腸，或：基督與教會之親密大愛、聯合與相通的揭示', title_orig: 'Bovvels Opened, or, A Discovery of the Neere and Deere Love, Union and Communion Betwixt Christ and the Church', author: 'Richard Sibbes（理查‧西布斯）；Thomas Goodwin（湯瑪斯‧古德溫）、Philip Nye（菲利普‧奈伊）編訂', era: '1639', place: 'London（倫敦）', language: '英文', intro: '英格蘭清教徒名牧理查‧西布斯逐節講解《雅歌》四至六章的講道集，由古德溫與奈伊於其身後輯錄付梓。書名取自《雅歌》「我為我的良人心腸激動」之意象，鋪陳基督與教會之間親密、深摯的大愛、聯合與相通。全書以新郎新婦的婚約比喻闡發基督的安慰與信徒的回應，兼具釋經、靈修與牧養關懷，是清教徒敬虔講道與「基督新婦」靈修傳統的代表作。' },
          { title_zh: '聖經與密室：如何讀經獲取最大屬靈益處', title_orig: 'The Bible and the closet: or, How we may read the Scriptures with the most spiritual profit', author: 'Thomas Watson（華森）', era: '十七世紀原著', place: '英國（倫敦）', language: '英文', intro: '英國清教徒牧師華森（Thomas Watson，卒於1686）之實用敬虔小品，合刊撒母耳‧李（Samuel Lee）論密室禱告之文。全書教導信徒如何以最得屬靈益處的方式研讀聖經，並如何成功經營私下禱告，為清教徒敬虔靈修傳統的代表作。此1844年版乃作者身後重印本，承襲改革宗讀經與祈禱的牧養教導。' },
          { title_zh: '壓傷的蘆葦與將殘的燈火', title_orig: 'The Bruised Reed and Smoaking Flax', author: '理查‧西布斯(Richard Sibbes)', era: '1630', place: '英國倫敦', language: '英文', intro: '英國清教徒講道家西布斯的代表作，源於其闡釋〈以賽亞書〉42章3節「壓傷的蘆葦，他不折斷；將殘的燈火，他不吹滅」（並引〈馬太福音〉12章20節）的系列講章，1630年首次刊行。全書以基督對軟弱信徒的溫柔憐憫為主題，安慰因罪疚與屬靈低落而灰心者，強調恩典必扶持微弱的信心直到得勝。文辭溫煦懇切，被譽為清教徒牧養神學與「實踐神學」(practical divinity)的典範，影響英美敬虔傳統甚鉅，至今仍為新教靈修經典。' },
          { title_zh: '心靈的爭戰與藉信戰勝自我', title_orig: 'The Soul\'s Conflict and Victory over Itself by Faith', author: '理查‧西布斯（Richard Sibbes）', era: '1635', place: '英格蘭', language: '英文', intro: '英格蘭清教徒名牧理查‧西布斯（1577–1635）以詩篇四十二篇11節為本所講的系列講道集，初版於一六三五年。全書分「心靈的爭戰」與「心靈的勝利」兩部，剖析信徒內心沮喪、憂悶與不安之根源，教導人如何藉信仰將意志順服於神、安息於神不變的同在與護理。屬清教徒「經歷神學」（experimental divinity）牧養傳統，文字溫煦撫慰，被鍾馬田譽為療癒心靈之作。' }
        ,
          { title_zh: '撒但詭計的珍貴醫治', title_orig: 'Precious Remedies Against Satan\'s Devices', author: '湯瑪斯·布魯克斯', era: '1652', place: '倫敦', language: '英文', intro: '十七世紀清教徒靈修大家湯瑪斯·布魯克斯所著，針對信徒靈命爭戰中面臨的撒但試誘提出系統的屬靈診斷與醫治之道。全書分別解析撒但慣用的各類詭計（如驕傲、懷疑、絕望、自滿等），逐一對應基督教信仰中的靈修解藥與防禦策略。代表清教傳統中關於屬靈爭戰的務實反思，兼具護教與靈修雙重特色，長期為英語宗教傳統的經典心靈輔導文獻。' },
          { title_zh: '沉默的基督在受苦中', title_orig: 'The Mute Christian Under the Smarting Rod', author: 'Thomas Brooks', era: '1659', place: 'London', language: '英文', intro: '英國清教徒神職人員布魯克斯所著的靈修勵志經典。成書於1660年，斯圖亞特復辟前夕，正值英國清教徒運動遭壓制、信仰群體面臨逆境的時代。作品以經文鑰句為綱，透過神學性冥想與靈修詩思，教導受苦信徒在患難中默然承受、仰望基督救恩，強調信心與忍耐的屬靈操練。為17世紀新教靈命建造與牧養文獻的代表作。' },
          { title_zh: '蒙恩者的心聲', title_orig: 'Grace Abounding to the Chief of Sinners', author: 'John Bunyan', era: '1666', place: 'London', language: '英文', intro: '約翰‧班揚著述的靈性自傳，敘述作者從放蕩生活經歷靈命覺醒、深陷宗教懷疑與良心控告，最終蒙受上帝恩典救贖的心靈歷程。全書交織個人悔改見證與清教神學思辨，展現英國清教運動時期的靈性實踐與救贖論思想，具有宣道與靈性牧養價值。' },
          { title_zh: '守護心靈', title_orig: 'Keeping the Heart', author: '約翰‧弗拉維爾(John Flavel)', era: 'c.1627–1691', place: '[未確認原版地點]', language: '英文', intro: '約翰‧弗拉維爾乃英國清教卓越靈修家，本書《守護心靈》為其經典著述，闡述基督徒當如何在信仰與品德上自我警醒、保持屬靈警惕。書中透過對聖經的深刻詮釋與切身靈修經驗，引導信徒理解心靈牧養之重要，兼具教義深度與實踐指引，為清教靈修傳統中最具影響力之作。現存版本多為近代重刊，1999年由Christian Focus Publications出版英文版。' },
          { title_zh: '珍寶：基督徒知足之心', title_orig: 'The Rare Jewel of Christian Contentment', author: '傑利邁亞‧巴羅斯(Jeremiah Burroughs)', era: 'c.1650s', place: 'Edinburgh', language: '英文', intro: '傑利邁亞‧巴羅斯所撰的靈修講道集，以「知足」為中心主題，揭示基督徒應如何面對生活困頓與心靈掙扎。本著作為英國清教運動中重要的牧養文獻，強調信心與順服的靈性修養，深刻影響近代基督教敬虔傳統與新教靈修實踐。透過系統論述，引導信眾在上帝主權下尋求內心平安與靈命成長。' },
          { title_zh: '罪之大惡', title_orig: 'The Evil of Evils, or The Exceeding Sinfulness of Sin', author: '耶利米亞‧伯羅斯（Jeremiah Burroughs）', era: '17 世紀', place: 'Edinburgh (original); USA 1992 modern edition', language: '英文', intro: '英國清教牧師伯羅斯的倫理護教著作，深入論述罪的本質與危害，強調罪乃人類靈性的根本敗壞。作品結合聖經詮釋與靈修實踐指導，闡明救恩論中罪的關鍵地位，代表 17 世紀清教倫理思想的重要成果。' },
          { title_zh: '天路確然指南', title_orig: 'A Sure Guide to Heaven', author: '約瑟夫‧艾倫（Joseph Alleine）', era: '1688', place: '倫敦', language: '英文', intro: '英國清教牧師艾倫之代表靈性著作。書中系統闡述新教救贖論與個人靈命轉變之道，強調信仰的確定性與實踐性。全書分明論證救贖的必要性、基督的中保地位、信心的性質，並提供靈魂自我檢驗的實踐指南。代表十七世紀英國清教敬虔運動對個人救贖與靈命成長的系統神學與護教反思，與同時代敬虔派在德國的運動並行發展，共同塑造近代新教靈性傳統。' },
          { title_zh: '天堂被風暴奪取', title_orig: 'Heaven Taken by Storm', author: 'Thomas Watson', era: '1669', place: '倫敦', language: '英文', intro: '托馬斯‧華特遜（1620–1686）著，清教運動中期倫敦威斯敏斯德禮拜堂牧師的代表講道集。以馬太福音 11:12「天堂被風暴奪取」為題，論述信仰的熱忱與屬靈爭戰；融合加爾文宗精微的約德論與經驗主義敬虔，是英文清教宣教傳統的典範著作，深刻影響後世新教講道學與靈命塑造。' }
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
        
          { title_zh: '吸引萬民歸依真教之唯一方式', title_orig: 'De unico vocationis modo omnium gentium ad veram religionem', author: '拉斯卡薩斯（Bartolomé de las Casas）', era: '約1537年', place: 'Mexico', language: '拉丁文', intro: '西班牙道明會士、恰帕斯主教拉斯卡薩斯（1484–1566）約於1537年寫成本書，現存第一部分。論旨鮮明：基督教傳教的唯一合法途徑是以理性說服與仁愛感召，而非武力征服。作者以《新約》福音書為基礎，系統駁斥暴力佈道之合理性，並直指西班牙殖民征服對原住民的不義。本書是天主教傳教神學史上最早的護教人道主義文獻之一，對近代宗教寬容論與傳教倫理學影響深遠。' }
        ],
      },
      {
        key: 'mission-periodicals',
        label: '宣教刊物部',
        label_en: 'Missionary Periodicals',
        desc: '近代來華新教宣教士創辦的中文與英文期刊，開近代中文報刊之先河，兼為傳教、西學東漸與漢學研究的園地。',
        works: [
          { title_zh: '察世俗每月統記傳', title_orig: 'Chinese Monthly Magazine', author: '米憐(William Milne)', era: '1815–1821', place: '麻六甲', language: '漢文', intro: '由倫敦會宣教士米憐(William Milne)在馬禮遜支持下於麻六甲創辦，是史上第一份近代中文期刊。以南洋華僑與識字華人為對象，木刻雕版、章回體行文，內容融貫基督教義、天文地理與西學新知，藉淺白文體傳教兼啟蒙。它開近代中文報刊之先河，奠定宣教士以期刊溝通中西文化的範式。' },
          { title_zh: '東西洋考每月統記傳', title_orig: 'Eastern Western Monthly Magazine', author: '郭實獵(Karl Gützlaff)', era: '1833–1838', place: '廣州‧新加坡', language: '漢文', intro: '由普魯士宣教士郭實獵(Karl Gützlaff)創辦，是中國境內出版的第一份近代中文期刊。以廣州一帶官紳士人為對象，刻意淡化教義、強調西方政教科學與時事，欲扭轉華人視外邦為夷狄之見。它把近代報刊由南洋帶入中土，是晚清士人認識世界的早期窗口，深具中西交流的開創意義。' },
          { title_zh: '遐邇貫珍', title_orig: 'Chinese Serial', author: '麥都思、奚禮爾、理雅各等', era: '1853–1856', place: '香港', language: '漢文', intro: '由倫敦會麥都思、奚禮爾、理雅各(James Legge)等主持，是香港第一份中文刊物，也是首份採用西式鉛字活版印刷的近代中文期刊。面向香港及華南讀者，率先引入新聞報導與商業廣告版面，兼載西學與時事。它在近代報刊史上開鉛印與新聞、廣告體例之先，為中文新式報業奠基。' },
          { title_zh: '六合叢談', title_orig: 'Shanghae Serial', author: '偉烈亞力(Alexander Wylie)', era: '1857–1858', place: '上海', language: '漢文', intro: '由倫敦會宣教士偉烈亞力(Alexander Wylie)主編，是上海第一份近代中文期刊，亦為綜合性新學刊物。以江南士人與知識階層為對象，系統介紹西方天文、數學、物理等科學新知，兼及時事文藝。它把西學東漸的重心推向上海，成為晚清士人吸收近代科學的重要媒介。' },
          { title_zh: '萬國公報', title_orig: 'A Review of the Times', author: '林樂知(Young John Allen)', era: '1868/1874–1907', place: '上海', language: '漢文', intro: '由美南監理會宣教士林樂知(Young John Allen)創辦，是晚清最具影響力的教會兼時事刊物。面向官紳士大夫與改革精英，廣傳西方政教制度與維新思想，康有為、梁啟超等皆深受其薰染。它由教會刊物躍為輿論重鎮，深刻牽動戊戌變法前後的思想風潮，在近代中西交流史上影響深遠。' },
          { title_zh: '教務雜誌', title_orig: 'The Chinese Recorder', author: '在華新教宣教士群', era: '1867–1941', place: '福州‧上海', language: '英文', intro: '由在華新教宣教士群體合辦，是在華宣教士最重要的英文機關刊物。以各差會宣教士為讀者，記錄宣教事業、教會動態與差會合作，並刊載大量漢學、民俗與宗教研究。它既是近代在華新教史的第一手檔案，也是西方漢學與中國研究的重要園地，見證中西文化長期互動。' }
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
        
          { title_zh: '基督教神學學生手冊', title_orig: 'The Student\'s Handbook of Christian Theology', author: '菲爾德（Benjamin Field）著；西蒙斯（John C. Symons）編', era: '1870', place: '英國倫敦（Hodder & Stoughton）', language: '英文', intro: '菲爾德（Benjamin Field，1823–1869）為循道宗牧師，原著 1868 年首刊於墨爾本；菲爾德逝世後由西蒙斯（John Christian Symons）整理其最終修訂、增補小傳，以「第二版」形式於 1870 年倫敦出版。書以神學生為對象，系統整理基督教神學各要項，涵蓋神論、基督論、救贖論、教會論等，條目簡明，代表十九世紀英語新教（循道宗）學院神學手冊傳統，具工具書性質。' }
        ,
          { title_zh: '神學研讀指南與書目', title_orig: 'Exercitia et bibliotheca studiosi theologiae', author: '吉斯伯特‧霍蒂烏斯（Gisbertus Voetius, 1589-1676）', era: '1644', place: '烏特勒支（Utrecht）', language: '拉丁文', intro: '荷蘭改革宗神學家、烏特勒支教授霍蒂烏斯應學生之請而作，近七百頁，系統規劃神學研讀的進程與方法，並附帶詳盡的神學書目導覽，堪稱十七世紀的「神學研讀指南」。書中強調學問須服事敬虔（pietas），亦設公私論辯之訓練；第二部以逾六十頁論辯護神學，駁斥異教、猶太教與伊斯蘭。1651 年出增訂版，深刻形塑改革宗的神學教育。' }
        ,
          { title_zh: '教會著述家文學史', title_orig: 'Scriptorum ecclesiasticorum historia litteraria, a Christo nato usque ad saeculum XIV', author: 'William Cave', era: '1688', place: 'London', language: '拉丁文', intro: '英國國教學者 William Cave（1637–1713）以拉丁文撰寫之教會著述家書目傳記總覽，涵蓋基督降生至十四世紀止。全書依年代排列，逐人條列生卒年、生平、著作真偽與版本源流，兼及著作思想評介，體例近乎「教父文學史辭典」。此書與其後續修訂版（Scriptorum ecclesiasticorum historia literaria, 1688–1698）並列十七世紀英國聖公會護教暨古學運動代表作，為後世教父學書目研究之重要參考工具。' }
        ],
      },
      {
        key: 'mission-lexicography',
        label: '宣教辭書與語文部',
        label_en: 'Missionary Lexicography and Philology',
        desc: '近代來華宣教士為習漢語、譯經傳教所編的字典、辭書與注音語文工具，多開漢外辭書與漢語拼音之先。',
        works: [
          { title_zh: '華英字典', title_orig: 'A Dictionary of the Chinese Language', author: '馬禮遜(Robert Morrison)', era: '1815–1823', place: '澳門', language: '漢文‧英文', intro: '由首位來華基督新教宣教士馬禮遜(Robert Morrison)歷時逾十五載編成，共六大冊，是史上第一部漢英／英漢對照大字典。全書廣收漢字字義、詞例與經史用語，並附部首與音序檢索，為西人習漢語立下典範。馬禮遜編纂之初衷在於譯經傳教，此書遂成其漢譯《聖經》與布道事工的根基，亦深刻影響其後一世紀的漢學與雙語辭書事業。' },
          { title_zh: '葡漢辭典', title_orig: 'Dicionário Português-Chinês', author: '羅明堅(Michele Ruggieri)、利瑪竇(Matteo Ricci)', era: '約 1583–1588(稿本)', place: '廣東肇慶', language: '葡萄牙文‧漢文', intro: '由耶穌會士羅明堅(Michele Ruggieri)與利瑪竇(Matteo Ricci)在肇慶傳教期間合編的稿本，是史上第一部歐洲語言與漢語對照的辭典。書中以葡萄牙文詞條對應漢字釋義，並嘗試以羅馬字標注字音，反映早期傳教士摸索漢語語音的歷程。此稿長期湮沒於羅馬檔案館，直至近世方被重新發現，為明末中西語言接觸與耶穌會適應策略的珍貴見證。' },
          { title_zh: '西儒耳目資', title_orig: '西儒耳目資', author: '金尼閣(Nicolas Trigault)', era: '1626', place: '杭州', language: '漢文(羅馬字注音)', intro: '由耶穌會士金尼閣(Nicolas Trigault)在華士人協助下編成，是首部以羅馬字母系統為漢字注音的韻書。全書設聲母、韻母與聲調符號，建立一套完整的拉丁字母拼讀方案，供西儒辨音識字、士人察音解韻之用。此書承接利瑪竇等人的注音嘗試而集其大成，被視為漢語拼音化的先驅，對後世音韻學與漢語羅馬字方案影響深遠。' },
          { title_zh: '英漢字典', title_orig: 'Chinese and English Dictionary', author: '麥都思(Walter Henry Medhurst)', era: '1842–1843', place: '巴達維亞', language: '英文‧漢文', intro: '由倫敦會宣教士麥都思(Walter Henry Medhurst)在巴達維亞主持的傳教印刷所編印，承馬禮遜之緒而成。全書以英文詞條對應漢字釋義與譯詞，廣採口語與書面用例，便於西人習漢語、譯文獻與布道之需。麥都思精於印刷與漢語，此書用字精審、編排清晰，是十九世紀中葉新教宣教士辭書事業承先啟後的重要一環，亦為其後英漢辭書所取資。' },
          { title_zh: '英華字典', title_orig: 'English and Chinese Dictionary', author: '羅存德(Wilhelm Lobscheid)', era: '1866–1869', place: '香港', language: '英文‧漢文', intro: '由德裔宣教士羅存德(Wilhelm Lobscheid)在香港編成，分數冊陸續刊行，是十九世紀規模最大的英漢辭書之一。全書收錄大量對應西學新事物的譯詞與新造詞語，涵蓋政治、科學、宗教諸領域。這些譯詞經由幕末明治的日本辭書轉介，再回流影響近代中國，成為東亞新詞匯流的關鍵樞紐，於漢語近代詞彙史與宣教文教事業皆具深遠意義。' },
          { title_zh: '漢英韻府', title_orig: 'A Syllabic Dictionary of the Chinese Language', author: '衛三畏(Samuel Wells Williams)', era: '1874', place: '上海', language: '漢文‧英文', intro: '由美部會宣教士兼漢學家衛三畏(Samuel Wells Williams)編成，以音節排序、按韻檢字而得名「韻府」。全書廣收漢字字音、字義與詞例，並標注官話與方音讀法，兼具辭書與正音工具之用。衛三畏久居中國、譯經辦報，此書凝聚其畢生漢語造詣，編排嚴謹、釋義詳贍，長期為西人研習漢語與從事宣教、翻譯所倚重，是晚清漢英辭書的集大成之作。' }
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
