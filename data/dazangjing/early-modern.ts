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
      },
      {
        key: 'african-religions',
        label: '撒南非洲本土宗教部',
        label_en: 'Sub-Saharan African Indigenous Religions',
        desc: '撒哈拉以南非洲的本土至高神信仰與宇宙論。傳統古老、多屬口傳，於接觸期(16–19世紀)經宣教士採錄並母語譯經而文本化；宣教士多取其既有的至高神之名譯「神」，故這些本土信仰成為基督教在非洲落地不可或缺的「種子概念」(薩內「可譯性」命題)。依年代規則歸近代外藏，並標記其種子功能與出處。',
        works: [
          { title_zh: '約魯巴至上神信仰（Olódùmarè‧Olórun）', title_orig: 'Yorùbá Supreme Being — Olódùmarè / Olórun', author: '約魯巴宗教傳統（口傳）', era: '傳統古老／文本化與譯經 19 世紀（克勞瑟約魯巴聖經 1884）', place: '西非（今奈及利亞西南）', language: '約魯巴語', intro: '約魯巴宗教以 Olódùmarè／Olórun 為造化萬有、至高在上的主宰,其下有眾 òrìṣà。獲釋奴隸、首位非裔聖公會主教克勞瑟譯約魯巴文聖經時,即以既有的 Olórun／Olódùmarè 譯「神」,使約魯巴的至上神信仰成為基督教在西非落地不可或缺的種子概念(薩內「可譯性」命題典型)。﹝口傳傳統‧接觸期文本化;承載譯本克勞瑟約魯巴語聖經在近代宣道/譯校藏,此處收本土宗教母體。﹞' },
          { title_zh: '阿肯至上神信仰（Nyame‧Onyankopɔn）', title_orig: 'Akan Supreme Being — Nyame / Onyankopɔn', author: '阿肯宗教傳統（口傳）', era: '傳統古老／文本化與譯經 19–20 世紀', place: '西非（今迦納一帶）', language: '契維語（阿肯）', intro: '阿肯人以 Nyame／Onyankopɔn 為獨一至高的天神,諺語「無人須教孩童認識至高神」(Obi nkyerɛ abɔfra Nyame) 傳誦不絕。契維文聖經與宣教即取 Onyankopɔn 譯「神」,阿肯本有的至上神觀遂成基督教在迦納落地的種子概念。﹝口傳傳統‧接觸期文本化。﹞' },
          { title_zh: '伊博至上神信仰（Chukwu‧Chineke）', title_orig: 'Igbo Supreme Being — Chukwu / Chineke', author: '伊博宗教傳統（口傳）', era: '傳統古老／文本化與譯經 19–20 世紀（聯合伊博語聖經 1913）', place: '西非（今奈及利亞東南）', language: '伊博語', intro: '伊博人以 Chukwu(大靈)／Chineke(造化之神)為至高造物主。聯合伊博語聖經即以 Chukwu／Chineke 譯「神」,使伊博的造物主信仰成為基督教在東奈及利亞落地的種子概念。﹝口傳傳統‧接觸期文本化;承載譯本聯合伊博語聖經在現代譯校藏。﹞' },
          { title_zh: '祖魯至上神信仰（uNkulunkulu）', title_orig: 'Zulu Supreme Being — uNkulunkulu', author: '祖魯宗教傳統（口傳）', era: '傳統古老／文本化與譯經 19 世紀（祖魯文聖經 1883；卡拉威《祖魯宗教體系》1870）', place: '南非', language: '祖魯語', intro: '祖魯人以 uNkulunkulu(至大者／始祖)為萬物之源。宣教士卡拉威輯錄其信仰(《祖魯宗教體系》),祖魯文聖經取 uNkulunkulu 譯「神」;「至大者究係至上神抑或第一祖先」之辯,更是非洲宗教研究的名案。祖魯至上神觀遂成基督教在南非落地的種子概念。﹝口傳傳統‧接觸期文本化。﹞' },
          { title_zh: '索托—茨瓦納至上神信仰（Modimo）', title_orig: 'Sotho-Tswana Supreme Being — Modimo', author: '索托—茨瓦納宗教傳統（口傳）', era: '傳統古老／文本化與譯經 19 世紀（莫法特茨瓦納語聖經 1857）', place: '南部非洲', language: '茨瓦納語／索托語', intro: '索托—茨瓦納諸族以 Modimo 為超越的至高存有。宣教士莫法特譯茨瓦納文聖經(南部非洲最早的完整聖經之一),即取 Modimo 譯「神」,使其至上神觀成為基督教在南部非洲落地的種子概念。﹝口傳傳統‧接觸期文本化;承載譯本在近代譯校/宣道藏。﹞' },
          { title_zh: '吉庫尤至上神信仰（Ngai）', title_orig: 'Gĩkũyũ Supreme Being — Ngai / Mwene-Nyaga', author: '吉庫尤宗教傳統（口傳）', era: '傳統古老／文本化與譯經 19–20 世紀', place: '東非（今肯亞中部）', language: '吉庫尤語', intro: '吉庫尤人以 Ngai(Mwene-Nyaga,光明山之主)為造物至高神,居於肯亞山巔。吉庫尤文宣教與聖經取 Ngai 譯「神」,其至上神信仰遂成基督教在東非落地的種子概念。﹝口傳傳統‧接觸期文本化。﹞' },
          { title_zh: '剛果宇宙論與至上神（Nzambi a Mpungu）', title_orig: 'Kongo Cosmology and Supreme Being — Nzambi a Mpungu', author: '剛果宗教傳統（口傳）', era: '傳統古老／文本化 16–17 世紀（剛果王國基督教 1491 起）', place: '中西非（剛果王國）', language: '基孔戈語', intro: '剛果人以 Nzambi a Mpungu 為至高造物主,並有生者—亡者兩界相通的宇宙圖式(dikenga)。剛果王恩津加受洗(1491)、阿方索一世立基督教為國教時,即以 Nzambi 譯「神」而承本土宇宙觀;金帕‧維塔的安東尼運動更以剛果意象重詮基督。剛果宇宙論遂成基督教在中非最早落地的種子概念。﹝口傳與早期文本化;為前基督教之後、接觸期本土宗教,依年代歸近代外藏。﹞' }
        
        ]
      },
      {
        key: 'amerindian-religions',
        label: '美洲原住民宗教部',
        label_en: 'Amerindian Religions',
        desc: '美洲原住民的本土宗教與宇宙論。瑪雅抄本為前接觸真跡；納瓦、安地斯、瑪雅諸傳統則於接觸期(16–17世紀)經宣教士(常為剷除偶像者)採錄而文本化，並在會通或對治中成為基督教在美洲落地的種子概念(如托南岑之於瓜達露佩)。依年代規則歸近代外藏。',
        works: [
          { title_zh: '納瓦神性觀（Teōtl‧Ōmeteōtl）', title_orig: 'Nahua Divinity — Teōtl / Ōmeteōtl', author: '納瓦宗教傳統（口傳，薩阿岡輯錄）', era: '傳統古老／文本化 16 世紀（《佛羅倫斯手抄本》約1577）', place: '中美洲（墨西哥中部）', language: '納瓦特爾語', intro: '納瓦人以 teōtl 統稱神聖能量,並有陰陽雙元的至高 Ōmeteōtl 之說。方濟會士薩阿岡為傳教與辨教而編《佛羅倫斯手抄本》,詳錄納瓦宗教;宣教士就「teōtl 可否譯 Dios」長期爭論,終多保留 Dios 以防混同。納瓦神性觀是基督教在墨西哥落地必須會通或對治的種子概念。﹝口傳‧接觸期文本化;承載文獻薩阿岡諸作在近代史傳/類書藏。﹞' },
          { title_zh: '託南岑→瓜達露佩（Tonantzin）', title_orig: 'Tonantzin and the Virgin of Guadalupe', author: '納瓦宗教傳統（口傳）／《寶多聶》', era: '傳統古老／文本化 17 世紀（《寶多聶》1649）', place: '中美洲（特佩亞克山）', language: '納瓦特爾語', intro: '特佩亞克山原為納瓦大地母神託南岑(Tonantzin,「我們的母親」)聖地;1531 年瓜達露佩聖母顯現傳說與納瓦文《寶多聶》(Nican Mopohua,1649)將之轉為聖母敬禮,遂爆炸性傳遍新西班牙。託南岑信仰是墨西哥聖母敬禮這一基督教本土化最強載體的種子概念。﹝口傳與納瓦文本化;母神底層與聖母敬禮混融的著名個案。﹞' },
          { title_zh: '安地斯聖地與帕查瑪瑪（Wak\'a‧Pachamama）', title_orig: 'Andean Wak\'a and Pachamama', author: '安地斯宗教傳統（口傳）', era: '傳統古老／文本化 16–17 世紀（剷偶像運動記錄）', place: '南美洲（安地斯）', language: '克丘亞語／艾馬拉語', intro: '安地斯人敬奉聖地聖物 wak\'a 與大地母神帕查瑪瑪(Pachamama)。西班牙「剷除偶像」運動一面摧毀、一面詳錄其信仰;帕查瑪瑪其後與聖母混融,成為今日安地斯基督教的底層。安地斯本土宗教是基督教在秘魯—玻利維亞落地會通與角力的種子概念。﹝口傳‧接觸期文本化。﹞' },
          { title_zh: '瓦洛奇裡手稿', title_orig: 'Huarochirí Manuscript', author: '佚名安地斯敘述者（阿維拉委錄）', era: '傳統古老／文本化約 1598–1608', place: '南美洲（秘魯瓦洛奇裡）', language: '克丘亞語', intro: '以克丘亞語記錄瓦洛奇裡地區神話、聖地與祭儀的手稿,由剷除偶像者神父阿維拉委人採錄——是前基督教安地斯宗教最完整的第一手紀錄,諷刺地出於迫害者之手。它既是安地斯宗教的活檔案,也是基督教在此傳播時「認識以對治/會通」本土信仰的關鍵文本。﹝接觸期克丘亞文本化。﹞' },
          { title_zh: '波波爾·烏', title_orig: 'Popol Vuh', author: '佚名基切瑪雅貴族（希梅內斯轉抄）', era: '傳統古老／文本化約 1554–1558（希梅內斯抄本約1701）', place: '中美洲（瓜地馬拉高地）', language: '基切瑪雅語', intro: '基切瑪雅的創世史詩,敘造物、雙生英雄與人由玉米受造,約 1550 年代由基切貴族以拉丁字母寫下,後為道明會士希梅內斯轉抄並拉—基對照。前基督教瑪雅宇宙觀的最完整文本,其創世與犧牲母題成為瑪雅基督教會通的種子概念。﹝前接觸傳統‧接觸期文本化。﹞' },
          { title_zh: '瑪雅抄本（德勒斯登‧馬德里‧巴黎）', title_orig: 'The Maya Codices (Dresden, Madrid, Paris)', author: '佚名瑪雅祭司—書記', era: '前接觸(約11–15世紀);蘭達主教1562焚燒殆盡,僅存三、四部', place: '中美洲（尤卡坦）', language: '瑪雅象形文字', intro: '以瑪雅象形文字寫成的曆算—占卜屏冊,是前哥倫布美洲唯一成熟文字的真跡文獻。蘭達主教 1562 年於馬尼焚毀大量抄本(「因含魔鬼之迷信與謊言」),正因它們是必須摧毀的「敵對經典」;倖存三、四部成瑪雅宗教的無價孤證。此為美洲嚴格意義的前基督教「書」,與基督教在尤卡坦的傳播形成毀滅—存續的張力。﹝真‧前接觸文獻;唯屬曆佔,非敘事。﹞' }
        
        ]
      },
      {
        key: 'oceanian-religions',
        label: '大洋洲本土宗教部',
        label_en: 'Oceanian Indigenous Religions',
        desc: '大洋洲(波利尼西亞為主)的本土神性觀與宇宙生成。幾全屬口傳，於19世紀接觸期經宣教士採錄、母語譯經而文本化；atua 等本土神名成為基督教在太平洋落地的種子概念。文獻最薄、年代最晚，依年代規則歸近代外藏，存疑處誠實標註。',
        works: [
          { title_zh: '波利尼西亞神性觀（atua‧mana‧tapu）', title_orig: 'Polynesian Divinity — atua, mana, tapu', author: '波利尼西亞宗教傳統（口傳）', era: '傳統古老／文本化 19 世紀（傳教士採錄）', place: '大洋洲（波利尼西亞）', language: '波利尼西亞諸語', intro: '波利尼西亞諸族以 atua(神／靈)、mana(神聖能力)、tapu(神聖禁忌,即「禁忌」一詞語源)構成宗教世界。倫敦會等宣教士採錄其信仰,並以既有的 atua 譯基督宗教之「神」;mana 與 tapu 更成宗教學通用術語。波利尼西亞本土神性觀是基督教在南太平洋落地的種子概念。﹝口傳‧接觸期文本化。﹞' },
          { title_zh: '毛利宇宙生成（Io‧Rangi-Papa）', title_orig: 'Māori Cosmogony — Io, Ranginui and Papatūānuku', author: '毛利宗教傳統（口傳）', era: '傳統古老／文本化 19–20 世紀（毛利語聖經 1868；Io 論爭 20 世紀初）', place: '大洋洲（紐西蘭）', language: '毛利語', intro: '毛利宇宙生成敘天父蘭吉(Ranginui)與地母帕帕(Papatūānuku)相擁,諸子分開天地而萬有生;另有至高神 Io 之說(是否前接觸有爭議)。毛利語聖經取 te Atua 譯「神」,毛利本土宇宙觀成為基督教在紐西蘭落地的種子概念。﹝口傳‧接觸期文本化;承載譯本毛利語聖經在現代譯校藏。﹞' },
          { title_zh: '庫姆利波（夏威夷創世頌）', title_orig: 'Kumulipo', author: '夏威夷宗教傳統（口傳，卡拉卡瓦刊行）', era: '傳統古老／文本化 1889（卡拉卡瓦刊；莉莉烏歐卡拉尼英譯1897）', place: '大洋洲（夏威夷）', language: '夏威夷語', intro: '夏威夷的宇宙生成譜系長頌,自太初幽暗(pō)逐級化生萬物與王族世系,共二千餘行。國王卡拉卡瓦刊行、末代女王莉莉烏歐卡拉尼繫獄中英譯。前基督教夏威夷宇宙觀的文學巔峰,其黑暗中生生不息的創世意象,與基督教在夏威夷傳播時的創造論相遇。﹝口傳‧19世紀末文本化。﹞' },
          { title_zh: '復活節島朗格朗格', title_orig: 'Rongorongo (Rapa Nui script)', author: '拉帕努伊書記傳統（未解讀）', era: '疑前接觸或接觸初期(19世紀採集);字符迄今未解讀', place: '大洋洲（復活節島）', language: '拉帕努伊語', intro: '復活節島木牌上的象形符號,是大洋洲唯一疑似本土文字,內容或為譜系與祭儀,迄今未能解讀;其為前歐洲接觸或受接觸啟發尚有爭議。多數木牌毀於 19 世紀動盪(部分傳教士曾收集)。此為大洋洲文字性宗教文獻的孤例,象徵本土聖傳在接觸下的殘存與失落。﹝未解讀;年代與性質存疑,誠實標註。﹞' }
        
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
          { title_zh: '新罕布夏浸信會信條', title_orig: 'The New Hampshire Baptist Confession', author: '新罕布夏浸信會聯會', era: '1833', place: '美國新罕布夏', language: '英文', intro: '美國新罕布夏浸信會聯會制定的信條，1833 年通過。相較於 1689 倫敦浸信會信條的嚴格加爾文主義，本信條語調溫和、淡化預定論色彩，反映十九世紀美國浸信會的神學取向。全文簡明，廣為美南浸信會等採用，並成為後來《浸信會信仰與信息》的藍本，是美國浸信會流傳最廣的信條之一。', link: '/creeds' },
          { title_zh: '路德小要理問答', title_orig: 'Der Kleine Katechismus', author: '馬丁‧路德', era: '1529', place: '維滕貝格', language: '德文', intro: '路德視察薩克森教區驚於無知而為家長與兒童編寫的小要理，十誡信經主禱文聖禮逐條淺解。「這是什麼意思？」的問句迴響五百年，新教教理教育的第一書。' },
          { title_zh: '路德大要理問答', title_orig: 'Der Große Katechismus', author: '馬丁‧路德', era: '1529', place: '維滕貝格', language: '德文', intro: '路德為牧者與教師詳解信仰要目的大要理，講道體例夾敘夾議。與小要理同入協同書的教導雙璧，路德神學的平民化總述。' },
          { title_zh: '日內瓦要理問答', title_orig: 'Catéchisme de l\'Église de Genève', author: '約翰‧加爾文', era: '1542', place: '日內瓦', language: '法文', intro: '加爾文以問答體重寫的日內瓦教會要理，信仰、律法、禱告與聖禮四部井然。改革宗要理傳統的源頭活水，海德堡與西敏要理的共同先驅。' },
          { title_zh: '法國信條', title_orig: 'Confessio Gallicana', author: '法國改革宗教會首屆全國總會（加爾文草稿）', era: '1559', place: '巴黎', language: '法文', intro: '法國改革宗教會秘密召開首屆總會通過的信條，以加爾文草稿為底。胡格諾教會在迫害中自我立憲的文件，拉羅歇爾會議確認後又稱拉羅歇爾信條。' },
          { title_zh: '拉科夫要理問答', title_orig: 'Katechizm Rakowski (Racovian Catechism)', author: '波蘭兄弟會（索齊尼派）', era: '1605', place: '拉科夫', language: '波蘭文／拉丁文', intro: '波蘭兄弟會系統陳述一位論神學的要理問答，否認三位一體與代贖而高舉理性釋經。近代反三一傳統的信仰綱領，歐洲各國屢遭焚禁而流傳不絕。' },
          { title_zh: '抗辯五條', title_orig: 'Remonstrantie (The Five Arminian Articles)', author: '阿民念派牧者聯署', era: '1610', place: '海牙', language: '荷蘭文', intro: '阿民念身後其徒聯署呈遞荷蘭國會的五條抗辯，就預定、救贖範圍與恩典可拒性修正正統加爾文主義。多特會議「五要點」所回應的原文本，阿民念主義的信仰憲章。' },
          { title_zh: '費城浸信會信條', title_orig: 'The Philadelphia Confession of Faith', author: '費城浸信會聯會', era: '1742', place: '費城', language: '英文', intro: '北美最早浸信會聯會以倫敦一六八九年信條為底增訂的信仰標準。美洲浸信會正統的奠基文件，南北浸信傳統共同的信仰母本。' },
          { title_zh: '莫拉維亞弟兄會紀律規程', title_orig: 'Ratio Disciplinae Unitatis Fratrum', author: '合一弟兄會（誇美紐斯編訂本 1660）', era: '1616（1660 刊行）', place: '波希米亞／阿姆斯特丹', language: '拉丁文', intro: '波希米亞弟兄會的教會紀律與治理規程，誇美紐斯流亡中刊行以存教統。白山之役後隱藏教會的制度火種，親岑多夫復興莫拉維亞教會的法統依據。' },
          { title_zh: '愛爾蘭信條', title_orig: 'The Irish Articles of Religion', author: '愛爾蘭教會（烏雪主導）', era: '1615', place: '都柏林', language: '英文', intro: '烏雪主導起草的一百零四條愛爾蘭教會信條，加爾文主義色彩較三十九條鮮明。西敏信條的直接底本，安立甘與清教神學交會的中繼文件。' },
          { title_zh: '第一瑞士信條', title_orig: 'Confessio Helvetica prior', author: '布靈格、米科尼烏斯等瑞士神學家', era: '1536', place: '巴塞爾', language: '拉丁文／德文', intro: '瑞士諸邦教會首度共同制定的信條，欲兼作與路德宗合一的基礎。瑞士改革宗聯合的第一份信仰文件，四十年後第二瑞士信條的先聲。' },
          { title_zh: '蘇黎世共識', title_orig: 'Consensus Tigurinus', author: '加爾文與布靈格', era: '1549', place: '蘇黎世', language: '拉丁文', intro: '加爾文與布靈格就聖餐教義達成的共識文件，彌合日內瓦與蘇黎世的路線分歧。改革宗傳統合流的關鍵協定，卻也觸發與路德宗的第二輪聖餐論戰。' },
          { title_zh: '瑞士共識公式', title_orig: 'Formula Consensus Helvetica', author: '海德格與圖雷蒂尼等', era: '1675', place: '蘇黎世', language: '拉丁文', intro: '瑞士正統派為抵禦索繆學派修正而制定的共識公式，連希伯來文母音符號的默示都在申明之列。改革宗經院正統的最後信條，嚴格主義時代的紀念碑。' }
        
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
          { title_zh: '沃蒂烏斯教會政治學', title_orig: 'Gisberti Voetii Politicae ecclesiasticae [partes I-III]', author: '吉斯貝圖·沃蒂烏斯 (Gisbertus Voetius)', era: '1663-1676', place: '阿姆斯特丹', language: '拉丁文', intro: '沃蒂烏斯為十七世紀荷蘭改革宗神學家與烏特勒支大學神學教授。本書三卷系統闡述教會政治秩序與組織原則，成為宗教改革後新教正統派的重要論著。內容涵蓋教會治理結構、牧職權限、長老制度與基督教國家的政教關係，特別強調聖經在教會政治中的權威性。此作影響深遠，塑造了改革宗與敬虔主義神學傳統對教會組織的理解，是近代新教政治神學的典範文獻。' },
          { title_zh: '蘇格蘭第一治理書', title_orig: 'The First Book of Discipline', author: '諾克斯等六約翰', era: '1560', place: '愛丁堡', language: '英文（蘇格蘭語）', intro: '諾克斯等人為新生的蘇格蘭教會起草的治理書，教區重整、濟貧與全民教育的藍圖並陳。蘇格蘭宗教改革的建國綱領，堂會制度與國民教育理想的源頭。' },
          { title_zh: '蘇格蘭第二治理書', title_orig: 'The Second Book of Discipline', author: '梅爾維爾主導', era: '1578', place: '愛丁堡', language: '英文（蘇格蘭語）', intro: '梅爾維爾主導修訂的治理書，確立教會屬靈管轄獨立於王權、長老制四級議會的原則。「兩個國度」論的憲章文本，蘇格蘭長老制的定型文件。' },
          { title_zh: '蘇格蘭國民盟約', title_orig: 'The National Covenant', author: '蘇格蘭盟約派（亨德森與約翰斯頓起草）', era: '1638', place: '愛丁堡灰衣修士教堂', language: '英文', intro: '抗拒查理一世強推禮書而全民簽署的國民盟約，灰衣修士墓園的簽名場面成民族記憶。盟約派時代的開卷文件，信仰自決與抵抗權的蘇格蘭表述。' },
          { title_zh: '神聖同盟與盟約', title_orig: 'The Solemn League and Covenant', author: '蘇格蘭總會與英格蘭國會', era: '1643', place: '愛丁堡／倫敦', language: '英文', intro: '蘇格蘭與英格蘭國會為宗教統一與共同防衛締結的盟約，西敏會議由此有蘇格蘭顧問列席。三王國戰爭的宗教軸心文件，長老制輸出英格蘭的未竟藍圖。' },
          { title_zh: '視察員訓令', title_orig: 'Unterricht der Visitatoren', author: '墨蘭頓（路德作序）', era: '1528', place: '維滕貝格', language: '德文', intro: '墨蘭頓為薩克森教會視察起草的訓令，規範講道、學校與牧者生活。新教領邦教會體制的第一份施政文件，宗教改革由運動轉為建制的起點。' },
          { title_zh: '丹麥-挪威教會條例', title_orig: 'Kirkeordinansen', author: '布根哈根起草', era: '1537／1539', place: '哥本哈根', language: '拉丁文／丹麥文', intro: '路德的同工布根哈根為丹麥-挪威王國制定的教會條例，主教改稱監督而體制全面路德化。北歐國教會的奠基法典，斯堪地那維亞宗教改革的制度樣板。' },
          { title_zh: '烏普薩拉會議決議', title_orig: 'Uppsala mötes beslut', author: '瑞典全國教會會議', era: '1593', place: '烏普薩拉', language: '瑞典文', intro: '瑞典全國會議確認奧斯堡信條、拒斥禮儀妥協的決議。瑞典教會路德宗認同的定錨文件，「瑞典永為一體同信」誓言所出。' },
          { title_zh: '多特教會條例', title_orig: 'Kerkorde van Dordrecht', author: '多特總會', era: '1619', place: '多德雷赫特', language: '荷蘭文', intro: '多特總會通過的教會條例，堂會、區會、總會三級與呼召程序詳備。荷蘭改革宗政體的標準章程，隨移民傳至南非與北美的治理母法。' },
          { title_zh: '日內瓦教會法令', title_orig: 'Ordonnances ecclésiastiques', author: '約翰‧加爾文', era: '1541', place: '日內瓦', language: '法文', intro: '加爾文重返日內瓦後制定的教會法令，牧師、教師、長老、執事四職與監督會制度確立。改革宗教會體制的原型設計，日內瓦「聖城」實驗的制度骨架。' },
          { title_zh: '一六〇四年教會法規', title_orig: 'Canons of 1604', author: '坎特伯裡教省會議（班克羅夫特主導）', era: '1604', place: '倫敦', language: '英文／拉丁文', intro: '詹姆士一世初年通過的一百四十一條教會法規，禮儀服制與教會法庭全面成文化。英格蘭教會沿用近三百五十年的法典，清教徒不從國教的法律分界線。' },
          { title_zh: '瑞典一六八六年教會法', title_orig: 'Kyrkolagen 1686', author: '瑞典王國（卡爾十一世治下）', era: '1686', place: '斯德哥爾摩', language: '瑞典文', intro: '卡爾十一世頒布的教會法，全民識字查經的家戶考問制度入法。瑞典國教體制兩百餘年的根本大法，北歐全民識字奇蹟的制度推手。' }
        
        ]
      },
      {
        key: 'jiaozong-fagui',
        label: '教宗法令與信理部',
        label_en: 'Papal Decrees and Catholic Norms',
        desc: '近代教宗詔書、通諭與天主教要理規範，反改革至十九世紀的教廷法度。',
        works: [
          { title_zh: '庇護四世信德宣認', title_orig: 'Professio fidei Tridentina', author: '教宗庇護四世', era: '1564', place: '羅馬', language: '拉丁文', intro: '脫利騰會議閉幕後庇護四世頒定的信仰宣認格式，凡任聖職者皆須宣誓。反改革時代天主教正統的試金石，四百年間入教與就職的法定誓文。' },
          { title_zh: '卡尼修斯要理問答', title_orig: 'Summa Doctrinae Christianae', author: '伯多祿‧卡尼修斯', era: '1555', place: '維也納', language: '拉丁文／德文', intro: '耶穌會士卡尼修斯為德語區編寫的大中小三級要理問答，刊行數百版遍及歐洲。天主教對抗路德要理的主力教材，「卡尼修斯」在德語中一度即要理問答的代名詞。' },
          { title_zh: '白敏要理問答', title_orig: 'Dottrina cristiana breve', author: '羅伯‧白敏', era: '1597', place: '羅馬', language: '義大利文', intro: '樞機白敏奉教宗克勉八世之命編寫的簡明要理，問答淺白供兒童與平民記誦。譯成數十種語言隨宣教全球流傳，天主教要理教育三百年的通行讀本。' },
          { title_zh: '格里曆改革詔書', title_orig: 'Inter gravissimas', author: '教宗格列高利十三世', era: '1582', place: '羅馬', language: '拉丁文', intro: '格列高利十三世頒布曆法改革的詔書，刪十日並改置閏之法，格里曆由此誕生。教會法令改寫全人類時間座標的孤例，復活節計算引發的科學工程。' },
          { title_zh: '教廷改組憲章', title_orig: 'Immensa aeterni Dei', author: '教宗西斯篤五世', era: '1588', place: '羅馬', language: '拉丁文', intro: '西斯篤五世設立十五個常設聖部的宗座憲章，樞機團由議事會轉為分部行政。近代教廷官僚體制的誕生證書，沿用至梵二後改革的治理骨架。' },
          { title_zh: '崇高的天主詔書', title_orig: 'Sublimis Deus', author: '教宗保祿三世', era: '1537', place: '羅馬', language: '拉丁文', intro: '保祿三世申明美洲原住民為真正的人、有權享自由財產且應以福音感召而非奴役的詔書。殖民時代人權論述的教會源頭，拉斯卡薩斯陣營的法理後盾。' },
          { title_zh: '自那一日詔書', title_orig: 'Ex illa die', author: '教宗克勉十一世', era: '1715', place: '羅馬', language: '拉丁文', intro: '克勉十一世重申禁止中國信徒祭祖祀孔的詔書，禮儀之爭至此定讞。康熙聞之禁教，中西第一次深度文明對話的法律句點。' },
          { title_zh: '奇特之事詔書', title_orig: 'Ex quo singulari', author: '教宗本篤十四世', era: '1742', place: '羅馬', language: '拉丁文', intro: '本篤十四世最終裁定中國禮儀之爭、要求宣教士宣誓遵禁的詔書。適應路線的百年實驗被畫上句號，直至一九三九年方獲鬆綁。' },
          { title_zh: '至大關懷詔書', title_orig: 'Omnium sollicitudinum', author: '教宗本篤十四世', era: '1744', place: '羅馬', language: '拉丁文', intro: '本篤十四世裁定印度馬拉巴禮儀之爭的詔書，禁止宣教士容許種姓習俗入教會生活。與中國禁令並列的亞洲禮儀雙判，適應宣教學的另一頁挫折。' },
          { title_zh: '五命題裁定詔書', title_orig: 'Cum occasione', author: '教宗依諾增爵十世', era: '1653', place: '羅馬', language: '拉丁文', intro: '依諾增爵十世裁定揚森《奧古斯丁》五命題為異端的詔書，恩寵論爭由此白熱化。巴斯卡《致外省人書》的直接背景，事實與法理之辨的著名案例。' },
          { title_zh: '在至高者座位詔書', title_orig: 'In eminenti apostolatus specula', author: '教宗克勉十二世', era: '1738', place: '羅馬', language: '拉丁文', intro: '克勉十二世首度禁止天主教徒加入共濟會的詔書，違者絕罰。教會與啟蒙結社兩百年對峙的第一紙禁令，後代教宗一再重申的先例。' },
          { title_zh: '抵達之際通諭', title_orig: 'Vix pervenit', author: '教宗本篤十四世', era: '1745', place: '羅馬', language: '拉丁文', intro: '本篤十四世重申貸款取利本質為高利貸之罪的通諭，兼容外在名目的補償。中世紀高利貸禁令在商業時代的最後防線，教會經濟倫理轉型的座標文件。' },
          { title_zh: '謬說要錄', title_orig: 'Syllabus errorum', author: '教宗庇護九世', era: '1864', place: '羅馬', language: '拉丁文', intro: '庇護九世隨《何等關懷》通諭附列八十條當代謬說的清單，泛神論至政教分離俱在譴責之列。教會與現代性正面對撞的宣言，十九世紀政教論戰的引爆點。' },
          { title_zh: '傳信部創立詔書', title_orig: 'Inscrutabili Divinae Providentiae', author: '教宗額我略十五世', era: '1622', place: '羅馬', language: '拉丁文', intro: '額我略十五世創設傳信部統籌全球宣教的詔書，宣教事務自此收歸教廷直轄。脫離保教權掣肘的制度嘗試，近代天主教宣教體制的奠基文件。' },
          { title_zh: '使徒關懷詔書', title_orig: 'Apostolicae curae', author: '教宗良十三世', era: '1896', place: '羅馬', language: '拉丁文', intro: '良十三世裁定聖公會聖秩「全然無效」的詔書，安立甘方面隨即發表反駁。聖公會與羅馬對話百年未解的法理節點，大公運動繞不開的文件。' },
          { title_zh: '至聖的天主詔書', title_orig: 'Benedictus Deus (1564)', author: '教宗庇護四世', era: '1564', place: '羅馬', language: '拉丁文', intro: '庇護四世批准脫利騰大公會議全部法令並保留解釋權於教廷的詔書。反改革法制生效的鑰匙文件，會議與教宗權柄關係的定調之筆。' },
          { title_zh: '審慎周詳詔書', title_orig: 'Sollicita ac provida', author: '教宗本篤十四世', era: '1753', place: '羅馬', language: '拉丁文', intro: '本篤十四世改革禁書審查程序的憲章，明定審查官須聽取辯護並附理由。書報檢查史上罕見的正當程序化嘗試，開明教宗立法的代表作。' },
          { title_zh: '信仰的創始者詔書', title_orig: 'Auctorem fidei', author: '教宗庇護六世', era: '1794', place: '羅馬', language: '拉丁文', intro: '庇護六世譴責皮斯托亞會議八十五條命題的詔書，揚森主義與國家教會論一併定讞。十八世紀改革公會議主義的法律終局，教會內啟蒙路線的封頂判決。' },
          { title_zh: '何等程度詔書', title_orig: 'Quod aliquantum', author: '教宗庇護六世', era: '1791', place: '羅馬', language: '拉丁文', intro: '庇護六世譴責法國《教士公民組織法》的詔書，斥其以國權改組教會為裂教之舉。教會與大革命決裂的法律文件，十九世紀政教對抗的開幕辭。' }
        
        ]
      },
      {
        key: 'zhengjiao-chiling',
        label: '政教敕令部',
        label_en: 'Church-State Edicts',
        desc: '各國君主與議會規範宗教事務的敕令法案，寬容與禁教並見。',
        works: [
          { title_zh: '容教詔令', title_orig: '康熙容教詔（1692）', author: '清聖祖康熙帝', era: '1692', place: '北京', language: '中文', intro: '康熙帝準天主教自由傳習、將教堂比照佛道寺觀保護的詔令。耶穌會曆算外交的收穫頂點，禮儀之爭後被禁教政策取代的短暫黃金時代見證。' },
          { title_zh: '伴天連追放令', title_orig: 'バテレン追放令', author: '豐臣秀吉', era: '1587（1614 德川禁教令繼之）', place: '筑前箱崎／江戶', language: '日文', intro: '豐臣秀吉驅逐傳教士的追放令，德川幕府一六一四年全面禁教繼之。吉利支丹世紀的終結法令，潛伏基督徒兩百五十年地下信仰的起點。' },
          { title_zh: '西發裡亞和約宗教條款', title_orig: 'Pax Westphalica (Instrumenta Pacis Osnabrugensis et Monasteriensis)', author: '神聖羅馬帝國與列強使節', era: '1648', place: '明斯特／奧斯納布呂克', language: '拉丁文', intro: '三十年戰爭終戰和約中確立路德宗、改革宗與天主教平等地位的宗教條款。「教隨國定」的最終定型與馴化，近代主權國家與宗教多元並存的法律起點。' },
          { title_zh: '奧格斯堡宗教和約', title_orig: 'Augsburger Religionsfrieden', author: '神聖羅馬帝國議會', era: '1555', place: '奧格斯堡', language: '德文', intro: '帝國議會承認路德宗合法地位的和約，確立「誰的領地，誰的宗教」原則。宗教戰爭第一階段的止戰法，也埋下三十年戰爭的未解伏筆。' },
          { title_zh: '託爾達敕令', title_orig: 'Edictum Tordense', author: '外西凡尼亞議會（約翰‧西吉斯蒙德治下）', era: '1568', place: '託爾達', language: '匈牙利文／拉丁文', intro: '外西凡尼亞議會宣告牧者得自由講道、信仰乃天主恩賜不得強制的敕令，天主教、路德、改革與一位論四教並容。歐洲最早的宗教寬容立法之一，一位論教會的法定出生證。' },
          { title_zh: '華沙聯盟公約', title_orig: 'Konfederacja warszawska', author: '波蘭立陶宛聯邦貴族議會', era: '1573', place: '華沙', language: '波蘭文', intro: '波蘭立陶宛貴族盟誓宗教歧異不得引發流血的公約，入列世界記憶名錄。宗教戰爭世紀中的「無火刑之國」憲章，貴族共和寬容傳統的基石。' },
          { title_zh: '至尊法案', title_orig: 'Act of Supremacy', author: '英格蘭國會', era: '1534', place: '倫敦', language: '英文', intro: '國會宣告亨利八世為英格蘭教會唯一至上元首的法案。英國宗教改革的法律開端，摩爾與費舍爾以死拒誓的那道命題。' },
          { title_zh: '一五五九年統一法案', title_orig: 'Act of Uniformity 1559', author: '英格蘭國會', era: '1559', place: '倫敦', language: '英文', intro: '伊利莎白一世重定公禱書為全國唯一合法禮儀並強制赴教堂的法案。「伊利莎白宗教解決」的支柱，安立甘中間路線的法律骨架。' },
          { title_zh: '一六六二年統一法案', title_orig: 'Act of Uniformity 1662', author: '英格蘭國會', era: '1662', place: '倫敦', language: '英文', intro: '王政復闢後強制牧者全盤接受公禱書的法案，兩千餘清教牧者於「聖巴多羅買日」被逐出聖職。英國不從國教派誕生的法律時刻，國教與自由教會分流的閘門。' },
          { title_zh: '維吉尼亞宗教自由法', title_orig: 'Virginia Statute for Religious Freedom', author: '湯瑪斯‧傑佛遜（起草）', era: '1786', place: '里奇蒙', language: '英文', intro: '傑佛遜起草、麥迪遜推動通過的宗教自由法，廢除國教稅並保障信仰不受強制。美國憲法第一修正案的直接前身，政教分離的世界性範本。' },
          { title_zh: '教士公民組織法', title_orig: 'Constitution civile du clergé', author: '法國國民制憲議會', era: '1790', place: '巴黎', language: '法文', intro: '法國大革命將教區改劃、主教民選並令教士宣誓效忠國家的法律。法國教會分裂為宣誓派與拒誓派的分水嶺，革命與教會百年恩怨的起點。' }
        
        ]
      },
      {
        key: 'dongfang-zhengjiao',
        label: '正教與東方教會法規部',
        label_en: 'Orthodox and Eastern Church Norms',
        desc: '近代東正教與東方諸教會的會議決議、信仰宣認與教會規程。',
        works: [
          { title_zh: '彼得大帝教會規程', title_orig: 'Духовный регламент', author: '費奧凡‧普羅科波維奇（起草）', era: '1721', place: '聖彼得堡', language: '俄文', intro: '彼得大帝廢牧首制、設神聖治理會議統轄俄國教會的規程，普羅科波維奇起草。俄國教會兩百年國家化的憲法，一九一七年恢復牧首制方告終結。' },
          { title_zh: '耶路撒冷會議決議', title_orig: 'Confessio Dosithei (Synodus Hierosolymitana)', author: '耶路撒冷牧首都西塞斯主持', era: '1672', place: '耶路撒冷／伯利恆', language: '希臘文', intro: '都西塞斯召集駁斥盧卡里斯加爾文傾向的會議，其信仰宣認成為近代正教最權威的教義文件之一。正教對宗教改革的正式回答，「伯利恆會議」的定調之作。' },
          { title_zh: '莫吉拉正教信仰宣認', title_orig: 'Confessio Orthodoxa', author: '基輔都主教彼得‧莫吉拉', era: '1642（雅西會議修訂）', place: '基輔／雅西', language: '拉丁文／希臘文', intro: '莫吉拉以問答體系統陳述正教信仰的宣認，雅西會議修訂後獲四大牧首確認。正教「信條化時代」的代表文件，基輔學術融會東西方法的結晶。' },
          { title_zh: '莫斯科大公會議決議（1666–1667）', title_orig: 'Московский большой собор', author: '俄國教會與東方牧首聯席會議', era: '1666–1667', place: '莫斯科', language: '俄文／希臘文', intro: '確認尼康禮儀改革、絕罰拒改舊禮者並廢黜尼康本人的大會議。舊禮儀派大分裂的法律定點，俄國宗教史最深的一道裂痕。' },
          { title_zh: '百章會議決議', title_orig: 'Стоглав', author: '莫斯科教會會議（伊凡四世召集）', era: '1551', place: '莫斯科', language: '教會斯拉夫文', intro: '伊凡雷帝召集、決議輯為百章的莫斯科教會會議，規範禮儀、聖像、教產與神職紀律。莫斯科「第三羅馬」自我立法的代表文獻，後為一六六七年會議部分推翻。' },
          { title_zh: '佈列斯特聯合條款', title_orig: 'Unio Brestensis', author: '基輔都主教區主教團', era: '1596', place: '佈列斯特', language: '教會斯拉夫文／拉丁文', intro: '基輔都主教區與羅馬共融、保留拜占庭禮儀的聯合條款。烏克蘭希臘禮天主教會的誕生文件，東西教會之間四百年張力的法律起點。' },
          { title_zh: '盧卡里斯東方信仰宣認', title_orig: 'Confessio fidei (Cyrillus Lucaris)', author: '君士坦丁堡牧首昔利爾‧盧卡里斯', era: '1629', place: '日內瓦刊行', language: '拉丁文／希臘文', intro: '牧首盧卡里斯以近乎加爾文立場發表的信仰宣認，震動東西教界，身後屢遭會議譴責。正教與新教相遇最戲劇性的文本，改革思想入東方的孤峰見證。' },
          { title_zh: '迪安珀會議法令', title_orig: 'Synod of Diamper (Udayamperoor)', author: '果阿總主教梅內塞斯主持', era: '1599', place: '印度烏達亞姆佩魯爾', language: '葡萄牙文／敘利亞文', intro: '葡萄牙教會強令印度聖多馬基督徒拉丁化、焚毀敘利亞禮書的會議法令。馬拉巴教會自主傳統的斷點，一六五三年「歪十字架誓言」反彈的遠因。' },
          { title_zh: '黎巴嫩山會議法令', title_orig: 'Synodus Montis Libani', author: '馬龍派教會（阿西馬尼協理）', era: '1736', place: '黎巴嫩魯韋薩谷', language: '阿拉伯文／拉丁文', intro: '馬龍派全面整編禮儀教區與修會制度的大會議，東方學家阿西馬尼自羅馬回鄉協理。馬龍派近代體制的奠基法典，東方公教會自我改革的代表案例。' },
          { title_zh: '克勞狄信仰確據', title_orig: 'Confessio Claudii', author: '衣索比亞皇帝格拉夫德沃斯（克勞狄）', era: '1555', place: '衣索比亞', language: '吉茲文', intro: '衣索比亞皇帝親筆回應耶穌會改宗壓力的信仰宣認，申明本國教會傳統的正統性。非洲君主的神學自辯書，衣索比亞教會面對歐洲的自主宣言。' }
        
        ]
      },
      {
        key: 'xiuhui-huixian',
        label: '修會會憲部',
        label_en: 'Religious Order Constitutions',
        desc: '近代新創與改革修會的會憲會規，天主教修道生活的制度文本。',
        works: [
          { title_zh: '耶穌會會憲', title_orig: 'Constitutiones Societatis Iesu', author: '依納爵‧羅耀拉', era: '1558（正式頒行）', place: '羅馬', language: '西班牙文／拉丁文', intro: '依納爵晚年親撰的耶穌會根本大法，取消詠經團、設長上集權與第四願服從教宗。近代最具效能的修會憲章，靈修與組織學結合的經典文本。' },
          { title_zh: '耶穌會研究規程', title_orig: 'Ratio Studiorum', author: '耶穌會（阿誇維瓦總會長任內定版）', era: '1599', place: '羅馬', language: '拉丁文', intro: '耶穌會統一全球學院課程與教學法的研究規程，古典人文與士林哲學階梯井然。近代歐洲最大教育網絡的操作手冊，全球數百學院同步的課程憲法。' },
          { title_zh: '加爾默羅赤足會憲', title_orig: 'Constituciones de las Carmelitas Descalzas', author: '亞維拉的德蘭', era: '1581（阿爾卡拉定版）', place: '亞維拉／阿爾卡拉', language: '西班牙文', intro: '大德蘭為改革後的赤足加爾默羅女修會親訂的會憲，靜默祈禱與貧窮團體生活成文。女性靈修家自立修會法度的里程碑，赤足改革運動的制度結晶。' },
          { title_zh: '烏爾蘇拉會規', title_orig: 'Regola della Compagnia di Sant\'Orsola', author: '安琪拉‧梅里奇', era: '1535', place: '佈雷西亞', language: '義大利文', intro: '梅里奇為在俗女性團體撰寫的會規，成員留居家中而共守貞潔與服務。女性使徒生活的制度創新，後世烏爾蘇拉教育修會的規章源頭。' },
          { title_zh: '慈善姊妹會會規', title_orig: 'Règles des Filles de la Charité', author: '文生‧德‧保祿與露薏絲‧德‧瑪利亞克', era: '1633 創會（會規 1655 定）', place: '巴黎', language: '法文', intro: '文生與露薏絲為服務貧病的姊妹團體共訂的會規，「以病人為主人」而不入隱院。女修會走出圍牆的制度突破，近代慈善護理體系的規章起點。' }
        
        ]
      },
      {
        key: 'quanqiu-fagui',
        label: '全球教會法規部',
        label_en: 'Global Church Norms',
        desc: '歐洲之外教省會議法令與新興教會章程，基督教全球化的法度見證。',
        works: [
          { title_zh: '太平天國天條書', title_orig: '天條書', author: '太平天國（洪秀全頒）', era: '1852', place: '永安／天京', language: '中文', intro: '太平天國頒行的宗教法規，十款天條改寫十誡並附讚美與悔罪儀文。基督教教規本土化最激烈的實驗文本，太平宗教體制的根本律法。' },
          { title_zh: '塞蘭坡宣教盟約', title_orig: 'The Serampore Form of Agreement', author: '克理威廉、馬士曼與沃德', era: '1805', place: '印度塞蘭坡', language: '英文', intro: '塞蘭坡三傑共訂的宣教團體盟約，尊重印度文化、培養本地牧者與自養原則成文。近代宣教方法論的先知性文件，本色化與三自思想的百年先聲。' },
          { title_zh: '非洲衛理聖公會紀律規程', title_orig: 'The Doctrines and Discipline of the African Methodist Episcopal Church', author: '理查‧艾倫等', era: '1817', place: '費城', language: '英文', intro: '獲釋奴隸艾倫創立非洲衛理聖公會後頒行的教義與紀律規程。黑人教會自立建制的第一部法典，種族壓迫下信仰自主的法律宣言。' },
          { title_zh: '利馬第三屆教省會議法令', title_orig: 'Tercer Concilio Limense', author: '利馬總主教莫格羅維霍主持', era: '1582–1583', place: '利馬', language: '西班牙文／克丘亞文', intro: '聖圖裡比奧主持的利馬教省會議，法令並命以西班牙文、克丘亞文與艾馬拉文三語要理教導原住民。美洲教會立法的高峰，安地斯語言首批印刷品的催生者。' },
          { title_zh: '墨西哥第三屆教省會議法令', title_orig: 'Tercer Concilio Provincial Mexicano', author: '墨西哥總主教孔特雷拉斯主持', era: '1585', place: '墨西哥城', language: '西班牙文／拉丁文', intro: '整合新西班牙教會法度的教省會議，原住民牧養與神職紀律並規。墨西哥教會三百年的根本法典，與利馬會議並列美洲雙柱。' },
          { title_zh: '果阿第一屆教省會議法令', title_orig: 'Primeiro Concílio Provincial de Goa', author: '果阿總主教加斯帕主持', era: '1567', place: '果阿', language: '葡萄牙文／拉丁文', intro: '葡屬亞洲首次教省會議的法令，規範改宗程序並禁強迫受洗。保教權體制下亞洲教會立法的起點，殖民與宣教張力的法律切片。' },
          { title_zh: '蘭柏四綱領', title_orig: 'The Lambeth Quadrilateral', author: '蘭柏會議（1888 決議）', era: '1888', place: '倫敦蘭柏宮', language: '英文', intro: '蘭柏會議定聖經、信經、二聖禮與歷史主教制四項為教會合一基礎的綱領。普世聖公宗自我定義的憲章，大公對話沿用至今的四邊座標。' },
          { title_zh: '普魯士聯合教會敕令', title_orig: 'Unionsurkunde der Evangelischen Kirche in Preußen', author: '腓特烈‧威廉三世', era: '1817', place: '柏林', language: '德文', intro: '普魯士王敕令路德宗與改革宗合併為聯合福音教會，紀念宗教改革三百年。國家主導教會合併的代表案例，「老路德派」出走美澳的歷史推力。' }
        
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
      "summary": "近代與基督教交鋒、對話、批判的他宗教哲學神學與世俗思想。歐洲自英國自然神論、法國啟蒙唯物論到德國的人本學還原與尼采的系譜學批判，形成對基督教最徹底的內部解構；猶太傳統以卡巴拉、哈西迪、猶太啟蒙與護教論戰回應；伊斯蘭世界有薩法維超越智慧學派與印度、阿拉伯的復興運動；南亞的梵社與吠檀多復興、錫蘭佛教護法論戰，以及明清中國的破邪闢邪與日本江戶排耶書，則構成非西方世界對基督教宣教最直接的思想抵抗。",
      "divisions": [
        {
          "key": "deism",
          "label": "自然神論與懷疑論部",
          "label_en": "Deism & Scepticism",
          "desc": "英國自然神論自赫伯特至潘恩——共同概念、祭司欺詐論、神蹟與預言的理性批判。",
          "works": [
            {
              "title_zh": "基督教並不神祕",
              "title_orig": "Christianity Not Mysterious",
              "author": "約翰‧托蘭德",
              "era": "一六九六",
              "place": "英格蘭‧倫敦",
              "language": "英文",
              "intro": "愛爾蘭自然神論者托蘭德的代表作，主張真正的基督教不含任何超乎理性、違反理性的奧秘，凡稱「奧秘」者皆是後世神職人員的添加。托蘭德以洛克的理性主義為據，將啟示徹底理性化，否定一切無法理性解明的教義。此書點燃英國自然神論論戰，遭教會強烈譴責並公開焚燬，是理神論思潮的奠基文獻。"
            },
            {
              "title_zh": "基督教與創世同其久遠",
              "title_orig": "Christianity as Old as the Creation",
              "author": "馬太‧廷得爾",
              "era": "一七三〇",
              "place": "英格蘭‧倫敦",
              "language": "英文",
              "intro": "被稱為「自然神論者聖經」的著作，廷得爾主張真正的宗教是與創世同其久遠的自然宗教，福音不過是對人人皆能藉理性知曉之自然律的重申。他否定特殊啟示的必要，認為一切真理皆可由理性與自然發現。此書是英國自然神論的高峰之作，激起眾多護教回應，包括巴特勒的類比論即為駁此而作。"
            },
            {
              "title_zh": "自然宗教對話錄",
              "title_orig": "Dialogues Concerning Natural Religion",
              "author": "大衛‧休謨",
              "era": "一七七九",
              "place": "蘇格蘭‧愛丁堡",
              "language": "英文",
              "intro": "休謨身後出版的宗教哲學名著，藉斐羅、克里安提斯、第美亞三人對話，徹底檢視自然神學的論證。休謨假斐羅之口拆解設計論證：類比薄弱、惡的存在難解、由有限世界無法推知無限完美之神。全書論辯精彩,對自然神學的批判至今仍是宗教哲學的核心議題,深刻動搖了理性證明上帝存在的根基。"
            },
            {
              "title_zh": "論神蹟",
              "title_orig": "Of Miracles",
              "author": "大衛‧休謨",
              "era": "一七四八",
              "place": "蘇格蘭‧愛丁堡",
              "language": "英文",
              "intro": "休謨人類理解研究第十章,提出反對相信神蹟的著名論證：神蹟乃對自然律的違反，而證明自然律的經驗證據遠強於任何人證；故理性人永不應僅憑見證接受神蹟為真。休謨並指出宗教神蹟見證多出於輕信、激情與虛榮。此論證對啟示宗教的歷史證據構成根本挑戰，成為近代懷疑論批判信仰的經典武器。"
            },
            {
              "title_zh": "哲學辭典宗教批判文選",
              "title_orig": "Dictionnaire philosophique",
              "author": "伏爾泰",
              "era": "一七六四",
              "place": "法蘭西／瑞士",
              "language": "法文",
              "intro": "法國啟蒙領袖伏爾泰以辭典形式撰寫的批判文集，眾多條目尖銳抨擊教會的迷信、不寬容與教權專橫。伏爾泰並非無神論者而是自然神論者，信奉一位理性的造物主，卻痛恨建制宗教的偽善與迫害，高呼「鏟除卑鄙之物」。文筆機鋒犀利、嬉笑怒罵，是啟蒙時代反教權主義最具影響力的代表作。"
            },
            {
              "title_zh": "為神的理性敬拜者辯護",
              "title_orig": "Apologie oder Schutzschrift für die vernünftigen Verehrer Gottes",
              "author": "赫爾曼‧塞繆爾‧雷馬魯斯",
              "era": "一七七四至一七七八",
              "place": "德意志‧漢堡",
              "language": "德文",
              "intro": "德國自然神論者雷馬魯斯生前不敢發表、由萊辛以「沃爾芬比特爾殘篇」之名陸續刊出的批判遺稿。雷馬魯斯以理性檢視聖經，否定神蹟與啟示，指耶穌乃失敗的猶太彌賽亞、復活為門徒所編造。此書開啟近代歷史耶穌的批判研究，引發德國神學界軒然大波，被視為理性主義聖經批判的先聲。"
            },
            {
              "title_zh": "論真理",
              "title_orig": "De veritate",
              "author": "切爾伯里的赫伯特（Edward Herbert of Cherbury）",
              "era": "一六二四（一六三三、一六四五增訂）",
              "place": "法蘭西‧巴黎／英格蘭‧倫敦",
              "language": "拉丁文",
              "intro": "英國自然神論之父的認識論與宗教哲學主著，提出人心「共同概念」與普世宗教五條真理，成為自然神論的信經雛型。"
            },
            {
              "title_zh": "論外邦人的宗教及其謬誤之緣由",
              "title_orig": "De religione gentilium",
              "author": "切爾伯里的赫伯特",
              "era": "一六六三（遺著）",
              "place": "荷蘭‧阿姆斯特丹",
              "language": "拉丁文",
              "intro": "以比較宗教方法考察異教諸民族信仰，論證各族皆保有五條共同宗教概念，謬誤出於祭司與政治操弄；近代比較宗教學先驅。"
            },
            {
              "title_zh": "神蹟並不違反自然律",
              "title_orig": "Miracles, no Violations of the Laws of Nature",
              "author": "查爾斯‧布朗特",
              "era": "一六八三",
              "place": "英格蘭‧倫敦",
              "language": "英文",
              "intro": "取斯賓諾莎與霍布斯之說改寫，主張神蹟不過是人未識其因的自然事件；比休謨〈論神蹟〉早六十餘年。"
            },
            {
              "title_zh": "大哉以弗所人的亞底米",
              "title_orig": "Great is Diana of the Ephesians",
              "author": "查爾斯‧布朗特",
              "era": "一六八〇",
              "place": "英格蘭‧倫敦",
              "language": "英文",
              "intro": "追溯偶像崇拜與獻祭起源，主張祭祀與神職特權皆僧侶謀利之發明，是英國「祭司欺詐論」的奠基文本。"
            },
            {
              "title_zh": "自由思想論",
              "title_orig": "A Discourse of Free-Thinking",
              "author": "安東尼‧柯林斯（Anthony Collins）",
              "era": "一七一三",
              "place": "英格蘭‧倫敦",
              "language": "英文",
              "intro": "主張人對一切宗教命題皆有以證據自行判斷之權，指教士壟斷解釋權為真理之敵；引發本特利、斯威夫特等大規模論戰。"
            },
            {
              "title_zh": "基督教之根據與理由論",
              "title_orig": "A Discourse of the Grounds and Reasons of the Christian Religion",
              "author": "安東尼‧柯林斯",
              "era": "一七二四",
              "place": "英格蘭‧倫敦",
              "language": "英文",
              "intro": "論證新約所引舊約預言字面上皆指當時猶太史事，惟寓意解經方能牽合於耶穌，動搖預言論證；引發數十年預言論戰。"
            },
            {
              "title_zh": "救主神蹟論第一篇",
              "title_orig": "A Discourse on the Miracles of our Saviour",
              "author": "托馬斯‧伍爾斯頓（Thomas Woolston）",
              "era": "一七二七",
              "place": "英格蘭‧倫敦",
              "language": "英文",
              "parent": "救主神蹟論六篇",
              "intro": "以奧利金寓意解經為據，主張福音書神蹟按字面理解則荒謬，須全作靈意解；銷量以萬計，最聳動的宗教論戰文本。"
            },
            {
              "title_zh": "神蹟能力自由探究",
              "title_orig": "A Free Inquiry into the Miraculous Powers…",
              "author": "康耶斯‧米德爾頓（Conyers Middleton）",
              "era": "一七四九",
              "place": "英格蘭‧倫敦（R. Manby & H. S. Cox 出版；作者任職劍橋三一學院／大學圖書館）",
              "language": "英文",
              "intro": "以史學考據論證教父時代所稱神蹟毫無可信見證，引爆十八世紀最大神學論戰；出版後聲勢一度蓋過休謨一七四八年〈論神蹟〉（休謨自陳其論文被此書掩蓋），並影響吉朋，是教會史批判研究的分水嶺。"
            },
            {
              "title_zh": "理性時代‧第一部",
              "title_orig": "The Age of Reason, Part the First",
              "author": "托馬斯‧潘恩（Thomas Paine）",
              "era": "一七九四",
              "place": "法蘭西‧巴黎",
              "language": "英文",
              "parent": "理性時代",
              "intro": "自陳「我信仰一位神，別無其他」，肯定造物主可由自然得知，斥建制宗教為權力發明；使自然神論成為跨大西洋大眾運動。"
            },
            {
              "title_zh": "人、風尚、意見與時代之特徵",
              "title_orig": "Characteristicks of Men, Manners, Opinions, Times",
              "author": "第三代沙夫茨伯里伯爵 安東尼‧艾希利‧庫珀（Anthony Ashley Cooper, 3rd Earl of Shaftesbury, 1671–1713）",
              "era": "一七一一（一七一四修訂增插圖版；一七二三第三版）",
              "place": "英格蘭‧倫敦",
              "language": "英文",
              "extent": "論文集三卷",
              "intro": "沙夫茨伯里自輯的論文總集，主張人天生具有「道德感」，善惡之辨源於內在的品味與情感，不待神的賞罰或啟示律令。他以優雅的對話與隨筆文體提倡自然的宗教情操，反對狂熱與教條，開英國道德感學派之先河，並深刻影響哈奇森、休謨與蘇格蘭啟蒙的倫理學傳統。"
            }
          ]
        },
        {
          "key": "rational-pantheism",
          "label": "理性宗教與泛神論部",
          "label_en": "Rational Religion & Pantheism",
          "desc": "斯賓諾莎、萊布尼茲、康德、黑格爾——以理性重構神、惡與宗教的哲學體系。",
          "works": [
            {
              "title_zh": "神學政治論",
              "title_orig": "Tractatus Theologico-Politicus",
              "author": "巴魯赫‧斯賓諾莎",
              "era": "一六七〇",
              "place": "荷蘭‧阿姆斯特丹",
              "language": "拉丁文",
              "intro": "斯賓諾莎匿名出版的劃時代著作，以理性批判方法考察聖經，主張聖經旨在教導順服與愛而非哲學真理，神蹟與預言當以自然解釋。書中倡言思想與信仰自由，論證國家應容許哲學探究。斯賓諾莎的泛神論將神等同於自然整體，徹底重塑神聖觀念。此書是近代聖經批判與政治自由主義的奠基文獻，當世即遭各方禁燬。"
            },
            {
              "title_zh": "神義論",
              "title_orig": "Essais de Théodicée",
              "author": "哥特佛萊‧萊布尼茲",
              "era": "一七一〇",
              "place": "德意志‧漢諾威",
              "language": "法文",
              "intro": "萊布尼茲探討惡之問題的哲學名著，「神義論」一詞即由此書創立。萊布尼茲論證全善全能全知的上帝必創造「一切可能世界中最好的世界」，現世之惡乃整體完善所必需的成分。他區分形上之惡、自然之惡與道德之惡，調和神的善與惡的存在。此書是理性神學處理惡的問題的經典,後遭伏爾泰於『憨第德』中辛辣諷刺。"
            },
            {
              "title_zh": "單在理性界限內的宗教",
              "title_orig": "Die Religion innerhalb der Grenzen der bloßen Vernunft",
              "author": "伊曼努爾‧康德",
              "era": "一七九三",
              "place": "普魯士‧柯尼斯堡",
              "language": "德文",
              "intro": "康德將宗教納入其道德哲學的綱領之作，主張宗教的本質在於道德，凡能在理性界限內辯護者方為真宗教。康德以哲學重釋根本惡、稱義與神國等基督教教義，將教會信仰還原為道德信仰，視耶穌為道德完善的典範。此書因觸怒普魯士當局而險遭查禁，是啟蒙理性宗教的最高表述，深刻影響後世自由派神學。"
            },
            {
              "title_zh": "宗教哲學講演錄",
              "title_orig": "Vorlesungen über die Philosophie der Religion",
              "author": "黑格爾",
              "era": "一八二一至一八三一",
              "place": "普魯士‧柏林",
              "language": "德文",
              "intro": "黑格爾在柏林大學的宗教哲學講稿，由學生筆記輯成。黑格爾視宗教為絕對精神藉表象自我認識的階段，基督教為「絕對宗教」，道成肉身與三一論象徵神人合一的辯證真理。他將基督教教義轉譯為思辨哲學的概念，主張哲學與宗教同一內容而形式有別。此書深刻影響後世神學與宗教研究，亦催生左右兩派黑格爾門徒的分裂。"
            },
            {
              "title_zh": "倫理學",
              "title_orig": "Ethica, ordine geometrico demonstrata",
              "author": "斯賓諾莎（Benedictus de Spinoza）",
              "era": "一六六一至一六七五年撰；一六七七年遺著刊行",
              "place": "尼德蘭‧海牙—阿姆斯特丹",
              "language": "拉丁文",
              "intro": "以幾何次序推演，主張唯一實體「神即自然」，取消位格神、神蹟與目的因；泛神論之爭與德國唯心論的共同源頭。"
            }
          ]
        },
        {
          "key": "enlightenment-atheism",
          "label": "啟蒙無神論與唯物論部",
          "label_en": "Enlightenment Atheism & Materialism",
          "desc": "法國啟蒙的唯物論與無神論——霍爾巴赫、梅利耶、拉美特利、狄德羅、盧梭的自然宗教。",
          "works": [
            {
              "title_zh": "自然的體系，或物理世界與道德世界的法則",
              "title_orig": "Système de la nature",
              "author": "霍爾巴赫男爵（託名 Mirabaud）",
              "era": "一七七〇",
              "place": "倫敦（實為阿姆斯特丹／巴黎地下印行）",
              "language": "法文",
              "extent": "全二卷",
              "intro": "時稱「無神論者的聖經」，以物質、運動與必然性解釋自然與人，否認靈魂不朽與第一因；遭巴黎高等法院焚燬仍風行全歐。"
            },
            {
              "title_zh": "梅利耶遺書",
              "title_orig": "Mémoire des pensées et des sentiments de Jean Meslier（Testament）",
              "author": "讓‧梅利耶（Jean Meslier）",
              "era": "約一七二〇年代撰成（生前秘密撰寫，一七二九年卒時遺留手稿）；伏爾泰一七六二年刊行節本，一八六四年阿姆斯特丹首次全文刊行",
              "place": "法蘭西‧阿登地區艾特雷皮尼（舊屬香檳省，全題作「艾特雷皮尼與比伊本堂神父」）",
              "language": "法文",
              "extent": "手稿逾千頁；一八六四年 Rudolf Charles 版全三卷",
              "intro": "本堂神父臨終手稿，自承終身不信，逐章駁斥啟示、神蹟與神的存在，並抨擊教會與貴族壓迫農民；歐洲第一部明確的無神論長篇著作。"
            },
            {
              "title_zh": "人是機器",
              "title_orig": "L'Homme machine",
              "author": "拉美特利（Julien Offray de La Mettrie）",
              "era": "一七四七年成稿，一七四八年刊行",
              "place": "萊頓",
              "language": "法文",
              "intro": "以醫學經驗把笛卡兒的動物機器推至人身，主張思想是腦的功能；十八世紀機械唯物論最著名的宣言。"
            },
            {
              "title_zh": "達朗貝爾之夢",
              "title_orig": "Le Rêve de d'Alembert（含前後談話）",
              "author": "狄德羅",
              "era": "一七六九年成稿，一八三〇年首刊",
              "place": "巴黎",
              "language": "法文",
              "extent": "三篇對話合一",
              "intro": "三聯對話闡述一元動態唯物論：物質普遍具感受性，意識由分子組織而生；十八世紀最深刻的唯物論文獻。"
            },
            {
              "title_zh": "基督教揭祕",
              "title_orig": "Le Christianisme dévoilé",
              "author": "霍爾巴赫（託名 Boulanger）",
              "era": "一七六六",
              "place": "南錫／阿姆斯特丹地下印行",
              "language": "法文",
              "intro": "反教系列開山之作，逐項檢討基督教教義原理與社會效果，論證其滋長狂熱、分裂與暴政。"
            },
            {
              "title_zh": "論精神",
              "title_orig": "De l'esprit",
              "author": "愛爾維修（Claude-Adrien Helvétius）",
              "era": "一七五八",
              "place": "巴黎（Durand）",
              "language": "法文",
              "intro": "以感覺論主張德行是正確理解的自利與良好立法的產物，宗教制裁多餘；遭索邦譴責焚燬，引發最大查禁風波。"
            },
            {
              "title_zh": "哲學思想錄",
              "title_orig": "Pensées philosophiques",
              "author": "德尼‧狄德羅（Denis Diderot）",
              "era": "一七四六",
              "place": "海牙（實為巴黎）",
              "language": "法文",
              "intro": "六十二則短章，由自然神論論證走向對啟示宗教的懷疑；出版即遭焚，是狄德羅邁向無神唯物論的第一步。"
            },
            {
              "title_zh": "人類精神進步史表綱要",
              "title_orig": "Esquisse d'un tableau historique des progrès de l'esprit humain",
              "author": "孔多塞侯爵",
              "era": "一七九四年成稿，一七九五年身後出版",
              "place": "巴黎",
              "language": "法文",
              "intro": "把人類史分十階段，敘理性掙脫祭司與神權，預言宗教偏見終將消亡；深刻影響孔德實證主義與世俗化理論。"
            },
            {
              "title_zh": "薩瓦助理司鐸的信仰告白",
              "title_orig": "Profession de foi du vicaire savoyard",
              "author": "盧梭（Jean-Jacques Rousseau）",
              "era": "一七六二",
              "place": "阿姆斯特丹／巴黎",
              "language": "法文",
              "parent": "愛彌兒，或論教育",
              "intro": "以良心與內在情感為據的自然宗教，既反唯物論亦拒啟示與教會權威；導致本書遭焚、作者流亡，深刻形塑自由派新教。"
            },
            {
              "title_zh": "廢墟，或帝國興衰之默想",
              "title_orig": "Les Ruines, ou Méditation sur les révolutions des empires",
              "author": "沃爾內（Constantin-François Volney）",
              "era": "一七九一",
              "place": "巴黎（一說日內瓦刊行，一七九二年巴黎 Desenne 版流通最廣）",
              "language": "法文",
              "intro": "於巴爾米拉廢墟冥想帝國衰亡，歸罪神權政治；末章萬國宗教大會使諸教當面對質，影響美國自然神論與比較神話學。"
            }
          ]
        },
        {
          "key": "german-critique",
          "label": "德國宗教批判部（青年黑格爾派與人本學無神論）",
          "label_en": "German Religious Critique",
          "desc": "費爾巴哈的人本學還原、鮑威爾與施特勞斯的福音書歷史批判、馬克思與施蒂納的宗教批判。",
          "works": [
            {
              "title_zh": "基督教的本質",
              "title_orig": "Das Wesen des Christenthums",
              "author": "費爾巴哈（Ludwig Feuerbach）",
              "era": "一八四一初版，一八四三二版",
              "place": "德國萊比錫",
              "language": "德文",
              "intro": "主張神學的祕密其實是人類學，上帝是人把類本質異化投射到天上的產物；為馬克思、恩格斯的宗教批判定調。"
            },
            {
              "title_zh": "被揭露的基督教",
              "title_orig": "Das entdeckte Christenthum",
              "author": "布魯諾‧鮑威爾",
              "era": "一八四三",
              "place": "瑞士蘇黎世與溫特圖爾",
              "language": "德文",
              "intro": "最激烈的反基督教檄文，判基督教使自我意識麻痺；印成即遭查禁銷毀，長期被視為佚書。"
            },
            {
              "title_zh": "黑格爾法哲學批判導言",
              "title_orig": "Zur Kritik der Hegel'schen Rechtsphilosophie. Einleitung",
              "author": "卡爾‧馬克思",
              "era": "一八四三年撰，一八四四年刊",
              "place": "法國巴黎",
              "language": "德文",
              "parent": "《德法年鑑》",
              "intro": "馬克思早期宗教批判的綱領性文獻，「宗教是人民的鴉片」名句即出於此。他承接費爾巴哈的人本學還原，宣告「對宗教的批判已經完成」，主張宗教是被壓迫者無可奈何的嘆息與虛幻慰藉，因此批判的任務須從天國轉向塵世、從神學轉向對現實社會關係與政治經濟的批判。"
            },
            {
              "title_zh": "唯一者及其所有物",
              "title_orig": "Der Einzige und sein Eigenthum",
              "author": "馬克斯‧施蒂納",
              "era": "一八四四",
              "place": "德國萊比錫",
              "language": "德文",
              "intro": "把宗教批判推到極端：人類、理性、道德乃至類本質皆為新神；刺激馬克思寫下《德意志意識形態》長篇反駁。"
            },
            {
              "title_zh": "耶穌傳——批判考訂",
              "title_orig": "Das Leben Jesu, kritisch bearbeitet",
              "author": "施特勞斯（David Friedrich Strauss）",
              "era": "一八三五至一八三六",
              "place": "德國圖賓根",
              "language": "德文",
              "extent": "全二卷",
              "intro": "另立「神話」範疇，主張福音敘事是初代群體以舊約期待為模子生成的無意識神話；歷史耶穌研究的分水嶺。"
            },
            {
              "title_zh": "符類福音史批判",
              "title_orig": "Kritik der evangelischen Geschichte der Synoptiker（第一、二卷，1841；第三卷題作 Kritik der evangelischen Geschichte der Synoptiker und des Johannes，1842）",
              "author": "布魯諾‧鮑威爾",
              "era": "一八四一至一八四二",
              "place": "德國萊比錫（Otto Wigand，第一、二卷）、布倫瑞克（Fr. Otto，第三卷）",
              "language": "德文",
              "extent": "全三卷",
              "intro": "主張福音書是個別作者的文學創作，馬可最先虛構敘事框架，由此推出耶穌歷史性無從證立；作者因而被撤銷教職。"
            },
            {
              "title_zh": "一切啟示之批判的嘗試",
              "title_orig": "Versuch einer Kritik aller Offenbarung",
              "author": "費希特（J. G. Fichte）",
              "era": "一七九二初版，一七九三二版",
              "place": "普魯士柯尼斯堡（今俄羅斯加里寧格勒）",
              "language": "德文",
              "intro": "以康德實踐理性為尺度追問啟示如何可能，把啟示的合法性完全繫於道德主體；初版匿名一度被誤為康德之作。"
            }
          ]
        },
        {
          "key": "life-philosophy",
          "label": "生命哲學與悲觀主義部",
          "label_en": "Life-Philosophy & Pessimism",
          "desc": "叔本華的意志形上學與尼采對基督教道德的系譜學批判。",
          "works": [
            {
              "title_zh": "作為意志與表象的世界",
              "title_orig": "Die Welt als Wille und Vorstellung",
              "author": "叔本華（Arthur Schopenhauer）",
              "era": "一八一九初版（一八一八年底印行、標記一八一九），一八四四增補二版",
              "place": "德國萊比錫",
              "language": "德文",
              "extent": "初版一卷，二版增補為二卷",
              "intro": "以世界為盲目意志之客體化，救贖在意志的自我否定，並取吠檀多與佛教解脫觀為典範；為十九世紀歐洲哲學正面援引印度宗教思想的代表性著作。"
            },
            {
              "title_zh": "敵基督者——對基督教的詛咒",
              "title_orig": "Der Antichrist. Fluch auf das Christenthum",
              "author": "尼采",
              "era": "一八八八年撰，一八九五年出版",
              "place": "德國萊比錫／義大利都靈",
              "language": "德文",
              "intro": "區分耶穌其人與保羅所創的教會宗教，指後者以怨恨與罪的觀念系統性敵視生命，末以反基督教法令宣告價值重估。"
            },
            {
              "title_zh": "論道德的系譜（道德譜系學）",
              "title_orig": "Zur Genealogie der Moral. Eine Streitschrift",
              "author": "尼采",
              "era": "一八八七",
              "place": "德國萊比錫",
              "language": "德文",
              "extent": "序言一篇＋三篇論文",
              "intro": "分論善惡對立出於怨恨、罪疚源於債務關係、禁欲理想如何賦予苦難意義；為基督教道德提供發生學解剖。"
            }
          ]
        },
        {
          "key": "kabbalah-hasidism",
          "label": "猶太卡巴拉與哈西迪部",
          "label_en": "Kabbalah & Hasidism",
          "desc": "盧里亞派卡巴拉的流溢與輪迴之說，及東歐哈西迪運動的靈修經典。",
          "works": [
            {
              "title_zh": "生命之樹",
              "title_orig": "עץ חיים / ʻEts ḥayim",
              "author": "哈依姆‧維塔爾",
              "era": "約一五七三至一五九〇年撰；一七八二年科雷茨初刊",
              "place": "采法特（撰）／科雷茨（刊）",
              "language": "希伯來文",
              "intro": "魯利亞卡巴拉的體系總綱，以收縮、破器、修補三環節重構神聖流溢；近世猶太神秘主義最具支配力的架構。"
            },
            {
              "title_zh": "石榴園",
              "title_orig": "פרדס רימונים / Pardes rimonim",
              "author": "摩西‧柯多維羅",
              "era": "一五四八年撰；一五九一至九二年刊",
              "place": "采法特／克拉科夫",
              "language": "希伯來文",
              "intro": "魯利亞之前采法特卡巴拉集大成之作，分三十二門系統整理十輝耀學說，調和神之超越與流溢顯現。"
            },
            {
              "title_zh": "輪迴之書",
              "title_orig": "ספר הגלגולים / Sefer ha-Gilgulim",
              "author": "哈依姆‧維塔爾",
              "era": "十六世紀末撰；一六八四年法蘭克福初刊",
              "place": "采法特／法蘭克福",
              "language": "希伯來文",
              "intro": "魯利亞派靈魂輪迴論專著，論靈魂之根、火花分散與附體機制，把個人命運納入宇宙修補的大敘事。"
            },
            {
              "title_zh": "坦尼亞",
              "title_orig": "ליקוטי אמרים – תניא / Liḳuṭe amarim – Tanya",
              "author": "利亞迪的施紐爾‧扎爾曼（Shneur Zalman of Liadi, 1745–1812）",
              "era": "一七九六年（希伯來曆五五五七年基斯流月）初刊",
              "place": "烏克蘭‧斯拉武塔（Slavuta，首刊地）；作者駐錫地為白俄羅斯‧利奧茲納—利亞迪",
              "language": "希伯來文",
              "intro": "哈巴德派根本典籍，被譽為「哈西迪派的成文律法」，以中間人為修行典型並提出徹底的泛在神論。"
            },
            {
              "title_zh": "其言傳於雅各",
              "title_orig": "מגיד דבריו ליעקב / Magid devarav le-Yaʻaḳov",
              "author": "梅茲里奇的大馬吉德‧多夫‧貝爾",
              "era": "一七八一年科雷茨初刊",
              "place": "波蘭—沃里尼亞‧梅茲里奇",
              "language": "希伯來文",
              "intro": "哈西迪派第一部系統性教義文獻，以「無」為神人相接之處，論自我消解與義人的中介職分。"
            },
            {
              "title_zh": "摩哈蘭語錄",
              "title_orig": "ליקוטי מוהר\"ן / Liḳuṭe Moharan",
              "author": "布拉茨拉夫的納賀曼",
              "era": "一八〇八年初刊，續編一八一一年",
              "place": "烏克蘭‧奧斯特羅（Ostroh，卷一一八〇八初刊）／莫吉列夫（Mogilev，卷二一八一一）；著述地為布拉茨拉夫—烏曼",
              "language": "希伯來文",
              "intro": "以奔放象徵論信心與懷疑的辯證、孤獨傾訴與喜樂的醫治力；因正視信仰危機而屢被近代宗教心理探討援引。"
            }
          ]
        },
        {
          "key": "jewish-philosophy-ethics",
          "label": "猶太哲學與倫理教化部",
          "label_en": "Jewish Philosophy & Ethical Literature",
          "desc": "布拉格馬哈拉爾的猶太性思辨、盧扎托的靈修倫理、德羅西的歷史批判與門德爾松的猶太啟蒙。",
          "works": [
            {
              "title_zh": "以色列的榮耀",
              "title_orig": "תפארת ישראל / Tifʼeret Yiśraʼel",
              "author": "布拉格的馬哈拉爾（Judah Loew ben Bezalel）",
              "era": "約一五八九至一五九九年間撰於布拉格；一五九九年（希伯來曆五三五九年）威尼斯初刊",
              "place": "撰於波希米亞‧布拉格；初刊於義大利‧威尼斯（Daniel Zanetti 印行）",
              "language": "希伯來文",
              "intro": "論妥拉與誡命之尊榮，闡述以色列（猶太民族）因領受妥拉而具的形上地位；以形式與質料等經院哲學語彙重釋選民觀與行誡命之理由（含「不解其因是否仍當行」之辯）。傳統上與五旬節（Shavuot）授律主題相繫。"
            },
            {
              "title_zh": "以色列的永恆",
              "title_orig": "נצח ישראל / Netsaḥ Yiśraʼel",
              "author": "布拉格的馬哈拉爾",
              "era": "一五九九年撰刊",
              "place": "布拉格",
              "language": "希伯來文",
              "intro": "論流散與救贖，視流亡為違反自然秩序的暫時狀態，故救贖必然來到；近世猶太救贖論代表作。"
            },
            {
              "title_zh": "神的大能",
              "title_orig": "גבורות השם / Gevurot ha-Shem",
              "author": "布拉格的馬哈拉爾",
              "era": "一五八二年初刊",
              "place": "布拉格／克拉科夫",
              "language": "希伯來文",
              "intro": "布拉格馬哈拉爾以出埃及敘事為軸心，論神蹟與自然秩序的關係。他反對邁蒙尼德一系將神蹟理性化、化約為自然現象的解釋，主張神蹟屬於比自然更高層級的實在，是神直接介入歷史的印記。書中亦闡發以色列受揀選的形上學意義，是猶太反理性主義神學的重要著作。"
            },
            {
              "title_zh": "正直者之路",
              "title_orig": "מסילת ישרים / Mesilat yesharim",
              "author": "盧扎托（Ramḥal）",
              "era": "一七三八年撰；一七四〇年阿姆斯特丹初刊",
              "place": "帕多瓦—阿姆斯特丹",
              "language": "希伯來文",
              "intro": "逐級論謹慎至聖潔的靈修進程之書，十九世紀成為立陶宛道德運動核心讀本，至今仍是猶太倫理學第一教材。"
            },
            {
              "title_zh": "主之道",
              "title_orig": "דרך ה׳ / Derekh Adonai",
              "author": "盧扎托（Ramḥal）",
              "era": "十八世紀上半撰",
              "place": "帕多瓦／阿姆斯特丹",
              "language": "希伯來文",
              "intro": "四部教義綱要，把卡巴拉宇宙論轉譯為可教授的系統神學；近世猶太最成功的教義綜合嘗試。"
            },
            {
              "title_zh": "明眸",
              "title_orig": "מאור עינים / Meʼor ʻenayim",
              "author": "亞撒利雅‧德‧羅西",
              "era": "一五七三年曼圖亞初刊",
              "place": "義大利‧曼圖亞—費拉拉",
              "language": "希伯來文",
              "intro": "引斐洛、約瑟夫斯與希臘羅馬史料質疑傳統猶太紀年，把人文主義文獻批判引入猶太學術；猶太科學研究的遠祖。"
            },
            {
              "title_zh": "耶路撒冷，或論宗教權力與猶太教",
              "title_orig": "Jerusalem, oder über religiöse Macht und Judentum",
              "author": "摩西‧門德爾松",
              "era": "一七八三年柏林刊",
              "place": "普魯士‧柏林",
              "language": "德文",
              "intro": "主張國家與教會職權分立、宗教不得強制，並界定猶太教非啟示教義而是啟示的立法；近代政教關係論述經典。"
            }
          ]
        },
        {
          "key": "jewish-polemic",
          "label": "猶太護教論戰部",
          "label_en": "Jewish Anti-Christian Polemics",
          "desc": "特羅基、莫德納、奧羅比奧等對基督教教義與經文詮釋的系統駁議。",
          "works": [
            {
              "title_zh": "信仰之堅固",
              "title_orig": "חזוק אמונה / Ḥizzuq emunah",
              "author": "特羅基的以撒",
              "era": "一五九三年撰；一六八一年附拉丁譯刊出",
              "place": "立陶宛‧特拉凱",
              "language": "希伯來文（多語譯本）",
              "intro": "近代最具影響力的猶太反基督教護教書，作者為立陶宛卡拉派（Karaite）猶太學者；駁彌賽亞論證並指新約矛盾。一五九三年成稿，作者次年辭世後由門生約瑟‧馬林諾夫斯基編定；一六八一年由瓦根賽爾（J. C. Wagenseil）收入《撒但的火箭》(Tela Ignea Satanae) 附拉丁譯刊出，反為啟蒙作家（伏爾泰等）所用。一八五一年 Moses Mocatta 出英譯《Faith Strengthened》。"
            },
            {
              "title_zh": "盾與櫓（磐楯與大盾）",
              "title_orig": "מאמר מגן וצנה / Maʼamar Magen ve-tsinah",
              "author": "里昂‧莫德納",
              "era": "約一六二六年撰；一八五六年由亞伯拉罕‧蓋格於布雷斯勞首刊",
              "place": "德國‧布雷斯勞（刊行地；撰於義大利‧威尼斯）",
              "language": "希伯來文",
              "intro": "莫德納對匿名之作《愚人之聲》(Kol Sakhal) 質疑口傳律法與拉比傳統的逐條駁覆，是為拉比猶太教辯護的護教之作；一八五六年蓋格刊本另附《盾與劍》(Magen va-Ḥerev) 節本與自傳《猶大生平》(Ḥayye Yehudah)。（原提案所述「批判卡巴拉、論證《光輝之書》晚出」實為莫德納另一部《獅吼》(Ari Nohem, 一六三九年撰、一八四〇年萊比錫首刊），非本書內容。）"
            },
            {
              "title_zh": "以色列得雪",
              "title_orig": "Israël vengé, ou Exposition naturelle des prophéties hébraïques que les chrétiens appliquent à Jésus, leur prétendu Messie（原作西班牙文稿 Prevenciones divinas contra la vana idolatría de las gentes，生前僅以手抄本流傳）",
              "author": "以撒‧奧羅比奧‧德‧卡斯特羅",
              "era": "十七世紀下半撰（作者卒於一六八七年）；一七七〇年由霍爾巴赫男爵（Baron d'Holbach）法譯刊行",
              "place": "阿姆斯特丹（撰，一六六〇年代末至一六八七年間）／扉頁題「倫敦」一七七〇年刊行（假託地名，實際印於阿姆斯特丹—巴黎一帶）",
              "language": "西班牙文（法譯本）",
              "intro": "奧羅比奧‧德‧卡斯特羅出身馬蘭諾（被迫改宗者），回歸猶太教後撰此書，以嚴密的理性論證逐條反駁基督教對先知書的彌賽亞式解讀，並質疑三位一體與原罪教義。全書譯成法文後廣為流傳，反而成為十八世紀歐洲自然神論者攻擊基督教啟示的常用資源。"
            },
            {
              "title_zh": "流散之井",
              "title_orig": "באר הגולה / Beʼer ha-golah",
              "author": "布拉格的馬哈拉爾",
              "era": "一五九八年初刊",
              "place": "布拉格",
              "language": "希伯來文",
              "intro": "為拉比傳統辯護，主張塔木德傳說屬象徵語言不可按字面理解；近世猶太護教學最具方法論意識的文本之一。"
            }
          ]
        },
        {
          "key": "islamic-revival",
          "label": "近代伊斯蘭思想與復興運動部",
          "label_en": "Early-Modern Islamic Thought & Revivalism",
          "desc": "薩法維超越智慧學派（穆拉薩德拉）、印度蘇菲改革（西爾信迪、沙阿瓦利烏拉）、瓦哈布運動與鄂圖曼思想。",
          "works": [
            {
              "title_zh": "四種旅程（超越智慧論四旅）",
              "title_orig": "al-Ḥikma al-mutaʿāliya fī al-asfār al-ʿaqliyya al-arbaʿa",
              "author": "穆拉‧薩德拉",
              "era": "約一六二〇—一六四〇年（歷時數十年陸續寫成，作者一六四〇年卒）",
              "place": "波斯‧卡哈克（庫姆近郊）／設拉子",
              "language": "阿拉伯文",
              "intro": "以靈魂四種旅程為架構統會逍遙、光照與蘇菲，立存有先於本質、存有等級與實體運動三大命題；伊斯蘭近代最龐大的形上學體系。"
            },
            {
              "title_zh": "神座智慧書",
              "title_orig": "al-Ḥikma al-ʿarshiyya",
              "author": "穆拉‧薩德拉",
              "era": "十七世紀前半",
              "place": "波斯‧設拉子",
              "language": "阿拉伯文",
              "intro": "穆拉‧薩德拉晚年的總結之作，分神論與末世論兩部。他以獨創的「實體運動」學說解釋靈魂在存有階序中的上升，主張復活並非肉身的復甦而是發生於「意象界」的實在事件。全書融合逍遙派哲學、照明學派與蘇菲證悟，是薩法維超越智慧學派的巔峰文本之一。"
            },
            {
              "title_zh": "證知者的靈藥（諸悟道者之靈丹）",
              "title_orig": "Iksīr al-ʿārifīn fī maʿrifat ṭarīq al-ḥaqq wa-l-yaqīn",
              "author": "穆拉‧薩德拉（薩德爾丁‧設拉子，1571/72–1640）",
              "era": "十七世紀前半",
              "place": "波斯‧設拉子",
              "language": "阿拉伯文",
              "intro": "穆拉‧薩德拉的短篇專論，闡述人的認識如何由感官出發，經理智的抽象作用，終至神祕的直接證悟。他主張知識並非心靈對外物的被動映照，而是靈魂自身存有等級的實際提升——認識愈高，存有愈真。是理解其「知識即存有」核心命題的入門文本。"
            },
            {
              "title_zh": "喚醒沉睡者",
              "title_orig": "Īqāẓ al-nāʾimīn",
              "author": "穆拉‧薩德拉",
              "era": "十七世紀前半",
              "place": "波斯‧設拉子（卒於巴斯拉；晚年在設拉子汗學院講學）",
              "language": "阿拉伯文",
              "intro": "穆拉‧薩德拉論存有一體（waḥdat al-wujūd）的專論，主張唯有必然存有者真實存在，萬有僅是其顯現的樣態與等級差異。全書兼具嚴格的哲學論證與蘇菲式的靈修勸誡，題名意在喚醒沉睡於多元表象中的心靈，回歸存有的唯一實在。"
            },
            {
              "title_zh": "艾哈邁德‧西爾信迪書信集",
              "title_orig": "Maktūbāt-i Imām-i Rabbānī",
              "author": "艾哈邁德‧西爾信迪",
              "era": "一五九九至一六二四年間",
              "place": "蒙兀兒印度‧西爾信德",
              "language": "波斯文（多語譯本）",
              "extent": "三卷、書信五三六通",
              "intro": "以「見證一體」修正伊本‧阿拉比的「存有一體」，主張證悟須以沙里亞為準繩並抨擊阿克巴的宗教折衷；南亞遜尼派復興的思想基調。"
            },
            {
              "title_zh": "先知使命證成論",
              "title_orig": "Ithbāt al-nubuwwa",
              "author": "艾哈邁德‧西爾信迪",
              "era": "十六世紀末至十七世紀初",
              "place": "蒙兀兒印度‧西爾信德",
              "language": "阿拉伯文",
              "intro": "以阿拉伯文論證理性與哲學思辨不足以獨立達致救贖真理，故人類必須有先知；並以奇蹟與經典內證確立穆罕默德的使命與「封印先知」之終極性。作者為蒙兀兒印度納格什班迪教團領袖、被尊為「第二千年革新者」（Mujaddid Alf-i Thānī），其駁斥對象是伊斯蘭哲學家（falāsifa）與偏離教法的神祕主義詮釋，以及阿克巴時期的宗教混融政策，而非基督教啟示論。"
            },
            {
              "title_zh": "始源與復歸",
              "title_orig": "Mabdaʾ wa Maʿād",
              "author": "艾哈邁德‧西爾信迪",
              "era": "約一六一〇年代",
              "place": "蒙兀兒印度‧西爾信德",
              "language": "波斯文",
              "intro": "西爾信迪的蘇菲形上學短論，系統陳述其著名的「見證一體」（waḥdat al-shuhūd）階序說。他修正伊本阿拉比的存有一體論，主張萬有並非真主本體的展開，而是其屬性投射的影像；證悟者所體驗的合一屬主觀見證而非客觀同一。此說成為印度蘇菲改革的思想基石。"
            },
            {
              "title_zh": "真主的決定性論證",
              "title_orig": "Ḥujjat Allāh al-Bāligha",
              "author": "沙阿‧瓦利烏拉‧德里維",
              "era": "十八世紀中葉",
              "place": "蒙兀兒印度‧德里",
              "language": "阿拉伯文（多語譯本）",
              "intro": "闡明沙里亞律例背後的理據，立哲學人類學並逐項解釋禮拜、齋戒等制度目的；近代伊斯蘭改革主義的奠基之作。"
            },
            {
              "title_zh": "祛除疑翳：論眾哈里發之統緒",
              "title_orig": "Izālat al-khafāʾ ʿan khilāfat al-khulafāʾ",
              "author": "沙阿‧瓦利烏拉‧德里維",
              "era": "十八世紀中葉",
              "place": "蒙兀兒印度‧德里",
              "language": "波斯文",
              "intro": "沙阿‧瓦利烏拉辨析「先知式哈里發」與「王權式哈里發」的分別，為前四位正統哈里發的統緒辯護，並回應什葉派對其正當性的質疑。他進而主張以宗教權威重整衰敗中的蒙兀兒政治秩序，是近代伊斯蘭政治神學與復興思想的關鍵文本。"
            },
            {
              "title_zh": "聖訓奧義釋",
              "title_orig": "Taʾwīl al-aḥādīth fī rumūz qiṣaṣ al-anbiyāʾ",
              "author": "沙阿‧瓦利烏拉‧德里維（Shāh Walī Allāh al-Dihlawī, 1703–1762）",
              "era": "十八世紀中葉",
              "place": "蒙兀兒印度‧德里",
              "language": "阿拉伯文",
              "intro": "以古蘭經先知故事為線索的釋義，把先知史視為神聖教育人類的漸進歷程；其耶穌敘事處理呈現伊斯蘭的詮釋立場。"
            },
            {
              "title_zh": "靈光片羽",
              "title_orig": "Lamaḥāt",
              "author": "沙阿‧瓦利烏拉‧德里維",
              "era": "十八世紀中葉",
              "place": "蒙兀兒印度‧德里",
              "language": "阿拉伯文（附英譯）",
              "extent": "短篇專論，常與 Saṭaʿāt 合刊",
              "intro": "沙阿‧瓦利烏拉的蘇菲形上學短論，嘗試調和伊本阿拉比的「存有一體說」與西爾信迪的「見證一體說」兩大對立傳統，另闢折衷之路。他主張兩說所述實為同一實在的不同觀看層次，而非彼此矛盾的主張，展現其融通印度蘇菲各派的整合企圖。"
            },
            {
              "title_zh": "論分歧之由的公允之言",
              "title_orig": "al-Inṣāf fī bayān sabab al-ikhtilāf (fī al-aḥkām al-fiqhīyah)",
              "author": "沙阿‧瓦利烏拉‧德里維",
              "era": "十八世紀中葉",
              "place": "蒙兀兒印度‧德里",
              "language": "阿拉伯文",
              "parent": "沙阿‧瓦利烏拉論集",
              "intro": "以歷史眼光說明四大教法學派分歧源於傳承與方法之異，主張博採諸派、直溯經訓；改革思潮的方法論宣言。"
            },
            {
              "title_zh": "認主獨一書",
              "title_orig": "Kitāb al-Tawḥīd",
              "author": "穆罕默德‧伊本‧阿卜杜勒‧瓦哈卜",
              "era": "十八世紀（約1740年代前後）",
              "place": "阿拉伯半島‧內志（烏萊納／胡賴米拉一帶撰成；後以迪爾伊耶為運動基地）",
              "language": "阿拉伯文",
              "intro": "瓦哈布運動奠基之作，嚴斥求庇聖墓、聖徒與護符為以物配主，主張回歸經訓字義；其嚴格一神論正面否定一切中保。"
            },
            {
              "title_zh": "穆罕默德之道",
              "title_orig": "al-Ṭarīqa al-Muḥammadiyya",
              "author": "比爾吉維‧穆罕默德‧埃芬迪",
              "era": "十六世紀後半",
              "place": "鄂圖曼帝國‧安納托利亞比爾吉",
              "language": "阿拉伯文",
              "intro": "比爾吉維的倫理與教義綱要，以簡明的體例陳述信仰要義、心性諸病與矯治之道，並力斥墳墓崇敬、蘇菲的過度儀式與一切宗教創新（bidʿa），主張回歸先知的原初實踐。此書成為鄂圖曼「卡迪扎德運動」的思想旗幟，影響後世伊斯蘭改革與復興思潮甚深。"
            },
            {
              "title_zh": "耶穌在印度",
              "title_orig": "Masīḥ Hindustān Mein / Jesus in India",
              "author": "米爾扎‧古拉姆‧艾哈邁德",
              "era": "一八九九年著；一九〇八年刊行",
              "place": "英屬印度‧旁遮普‧卡迪安",
              "language": "烏爾都文（後有英譯）",
              "intro": "主張耶穌未死於十字架而東行克什米爾終老，系統瓦解復活與升天教義；南亞穆斯林最具傳播力的反論。"
            }
          ]
        },
        {
          "key": "south-asian-reform",
          "label": "印度與南亞宗教改革回應部",
          "label_en": "Indian & South Asian Religious Reform",
          "desc": "梵社、雅利安社與吠檀多復興對基督教宣教的回應，及錫蘭佛教的護法論戰。",
          "works": [
            {
              "title_zh": "耶穌的訓誡：通往平安與福樂之導",
              "title_orig": "The Precepts of Jesus, the Guide to Peace and Happiness",
              "author": "羅姆‧摩罕‧羅伊（Rammohun Roy）",
              "era": "一八二〇年初版",
              "place": "印度‧加爾各答",
              "language": "英文（另有孟加拉文本）",
              "extent": "本編一卷，另附三次申辯：《申辯》（An Appeal, 1820）、《再申辯》（Second Appeal, 1821）、《終申辯》（Final Appeal, 1823）",
              "intro": "自四福音輯出耶穌的道德訓誨，略去神蹟與三一等教義，主張基督教精華在倫理；出版後引發與塞蘭坡浸信會馬士曼（Joshua Marshman）的長期公開論戰，為十九世紀初印度最著名的基督教神學公開論爭之一。"
            },
            {
              "title_zh": "為《耶穌的訓誡》向基督教公眾之申辯",
              "title_orig": "An Appeal to the Christian Public, in Defence of the \"Precepts of Jesus\"",
              "author": "羅姆‧摩罕‧羅伊",
              "era": "一八二〇",
              "place": "印度‧加爾各答",
              "language": "英文",
              "parent": "耶穌的訓誡",
              "intro": "羅姆‧摩罕‧羅伊回應浸信會傳教士馬士曼斥其為異端的首度答辯。他堅持自己只是把耶穌的道德教訓從教義爭議中分離出來，並純以聖經文本本身質疑三位一體的經據，主張基督的至高在於其訓誨而非其本體。是印度知識分子以基督教語彙反詰基督教的開端。"
            },
            {
              "title_zh": "為《耶穌的訓誡》向基督教公眾之再申辯",
              "title_orig": "Second Appeal…／A Treatise on Christian Doctrine",
              "author": "羅姆‧摩罕‧羅伊",
              "era": "一八二一（一八三四改題再刊）",
              "place": "印度‧加爾各答（一八三四改題再刊於英國‧倫敦）",
              "language": "英文",
              "parent": "耶穌的訓誡",
              "intro": "羅伊論戰的第二篇答辯，深入希伯來文與希臘文原文的釋義，逐條駁斥三位一體、基督的神性與代贖說，主張這些教義是後世附加而非耶穌本人所傳。此書使他在西方獲得廣泛注意，美國一神派尤引為同道，成為十九世紀跨宗教神學對話的先聲。"
            },
            {
              "title_zh": "為《耶穌的訓誡》向基督教公眾之終申辯",
              "title_orig": "Final Appeal to the Christian Public…",
              "author": "羅姆‧摩罕‧羅伊",
              "era": "一八二三（一八二八再版）",
              "place": "印度‧加爾各答",
              "language": "英文",
              "parent": "耶穌的訓誡",
              "intro": "三申辯終篇，處理約翰福音序言與道成肉身經文；因差會印刷所拒印而自設印刷所，成印度言論自主的象徵。"
            },
            {
              "title_zh": "一神論者的贈禮",
              "title_orig": "Tuhfat al-Muwahhidin",
              "author": "羅姆‧摩罕‧羅伊",
              "era": "約一八〇四年著；一八八四年英譯",
              "place": "印度孟加拉‧穆爾希達巴德／加爾各答",
              "language": "波斯文（阿拉伯文序）",
              "intro": "以凱拉姆與理性主義工具批判一切宗教的偶像崇拜與祭司權威，主張一神信仰乃人類共通理性本能。"
            },
            {
              "title_zh": "真理之光",
              "title_orig": "Satyārth Prakāś",
              "author": "達耶難陀‧薩拉斯瓦蒂",
              "era": "一八七五初版；一八八二–八三修訂（作者一八八三卒後刊行）",
              "place": "印度‧瓦拉納西（貝拿勒斯）初版；修訂本由阿傑梅爾「利他會」(Paropkarini Sabha) 傳布",
              "language": "印地文（多語譯本）",
              "extent": "全書十四章（samullas）；第十一章評駁印度各派、第十二章評駁順世／佛教／耆那、第十三章基督教、第十四章伊斯蘭",
              "intro": "雅利安社綱領之作，主張回歸吠陀本典並專章評駁耆那、佛教、基督教與伊斯蘭；印度教護教復興的代表文本。"
            },
            {
              "title_zh": "梵教法典",
              "title_orig": "Brahmo Dharma",
              "author": "提賓德羅那特‧泰戈爾",
              "era": "一八四八至一八五〇年編成；一九二八年英譯",
              "place": "印度‧加爾各答",
              "language": "孟加拉文／梵文",
              "intro": "梵社信仰與倫理手冊，捨吠陀無誤之說而以直觀良知為權威，藉以抵禦傳教士的改宗攻勢。"
            },
            {
              "title_zh": "耶穌基督：歐洲與亞洲",
              "title_orig": "Jesus Christ, Europe and Asia (亦作 Jesus Christ: Europe and Asia)",
              "author": "凱沙布‧錢德拉‧森",
              "era": "一八六六年五月加爾各答講演；一八六六年倫敦初刊、一八六九年加爾各答 Indian Mirror Press 版",
              "place": "印度‧加爾各答",
              "language": "英文",
              "intro": "高舉耶穌為亞洲人，指斥歐洲教會以西方文化包裝福音；亞洲「非教會的基督論」最早的代表文本之一。"
            },
            {
              "title_zh": "未來的教會",
              "title_orig": "The Future Church: Being the Substance of a Lecture Delivered on the Occasion of the Thirty-ninth Anniversary of the Brahmo Samaj",
              "author": "凱沙布‧錢德拉‧森",
              "era": "一八六九",
              "place": "印度‧加爾各答",
              "language": "英文",
              "intro": "構想超越宗派、融攝印度教虔信與基督教倫理的普世有神教會，為其後新天啟體系之先聲。"
            },
            {
              "title_zh": "新天啟",
              "title_orig": "The New Dispensation (Nava Vidhan)",
              "author": "凱沙布‧錢德拉‧森",
              "era": "一八七九年宣告；一八八四、一八九六年結集",
              "place": "印度‧加爾各答",
              "language": "英文",
              "intro": "宣告繼舊約新約之後的第三約，主張諸宗教精華在印度合流，並設聖餐洗禮式儀節與使徒制。"
            },
            {
              "title_zh": "王瑜伽",
              "title_orig": "Raja Yoga",
              "author": "辨喜（Swami Vivekananda）",
              "era": "一八九六",
              "place": "美國‧紐約",
              "language": "英文",
              "intro": "講稿與《瑜伽經》譯註合編，把印度修行傳統重述為可經驗驗證的宗教科學；近代印度教西傳的關鍵文本。"
            },
            {
              "title_zh": "芝加哥演講集",
              "title_orig": "Chicago Addresses",
              "author": "辨喜",
              "era": "一八九三年講（一九二三年結集出版）",
              "place": "美國芝加哥（世界宗教議會）",
              "language": "英文",
              "intro": "辨喜在一八九三年芝加哥世界宗教議會的講詞結集。他以吠檀多的普遍主義主張諸宗教殊途同歸、真理不為一教所獨佔，並公開抗議傳教士對印度文化的貶抑與誤現。這批演說使印度教首次以自信的姿態登上世界舞台，是東方宗教反向影響西方的標誌性事件。"
            },
            {
              "title_zh": "大辯論：佛教與基督教面對面（帕納杜勒論戰）",
              "title_orig": "Buddhism and Christianity Face to Face（Panadura Vadaya）",
              "author": "米格圖瓦特‧古納難陀長老 對辯 大衛‧德‧席爾瓦牧師與傳道員 F. S. 西里曼納；詹姆斯‧馬丁‧皮伯斯（J. M. Peebles, 1822–1922）編",
              "era": "一八七三年八月二十六、二十八日兩日論戰；當年由《錫蘭時報》系統刊出英文摘譯，全本英文書一八七八年在美國波士頓（Colby & Rich）出版",
              "place": "錫蘭‧帕納杜勒",
              "language": "僧伽羅文（原辯）／英文（刊本）",
              "intro": "兩日公開辯論的逐字記錄，就靈魂、造物主、涅槃與復活交鋒，佛教方普遍被認獲勝；促成奧爾科特等赴錫蘭並啟發達磨波羅。"
            },
            {
              "title_zh": "佛教問答",
              "title_orig": "A Buddhist Catechism",
              "author": "亨利‧斯蒂爾‧奧爾科特",
              "era": "一八八一年初版；作者生前持續修訂（卒於一九〇七年二月），身後仍續出至一九一五年第四十四版",
              "place": "錫蘭‧可倫坡（初版）；後續版本多由馬德拉斯／阿迪亞爾神智學會出版",
              "language": "英文與僧伽羅文對照初版",
              "intro": "仿基督教要理問答體例編成的錫蘭上座部佛教入門書，供神智學會創設之佛教學校（阿難陀學院等）使用以抗衡教會學校；為「新教式佛教」與宗教形式反向挪用的典型，內容帶神智學與理性主義色彩，非傳統上座部教科書。"
            },
            {
              "title_zh": "回歸正義",
              "title_orig": "Return to Righteousness",
              "author": "阿那伽利迦‧達磨波羅",
              "era": "一八九〇年代至一九三〇年代文稿；一九六五年結集",
              "place": "錫蘭／印度",
              "language": "英文",
              "extent": "演說、論文與書信合集一冊",
              "intro": "達磨波羅的文集，力斥英國殖民統治與基督教傳教事業對錫蘭本土文化與佛教的侵蝕。他主張佛教是理性且合乎科學的宗教，遠勝於依賴信仰與神蹟的基督教，並終身推動收回菩提伽耶聖地。其論述奠定了南亞佛教復興與反殖民民族主義的結合。"
            }
          ]
        },
        {
          "key": "east-asian-anti-christian",
          "label": "東亞闢邪排耶部",
          "label_en": "East Asian Anti-Christian Treatises",
          "desc": "明清中國的破邪闢邪文獻與日本江戶的排耶書——以華夷之辨、綱常倫理與佛教立場駁斥天主教。",
          "works": [
            {
              "title_zh": "闢邪論",
              "title_orig": "闢邪論",
              "author": "楊光先",
              "era": "一六五九年（順治十六年）撰，一六六五年前後收入《不得已》刊行",
              "place": "中國‧江南徽州府歙縣（作者籍貫）／北京（曆獄發生地）",
              "language": "漢文",
              "extent": "三篇（上、中、下），非獨立單行本，收入《不得已》上卷",
              "intro": "清初攻擊耶穌會士的核心論作，指控湯若望曆算錯誤、窺伺國政，終釀曆獄；中國儒者反教論的原型文本。"
            },
            {
              "title_zh": "辟邪紀實（亦作《闢邪紀實》）",
              "title_orig": "Death Blow to Corrupt Doctrines: A Plain Statement of Facts, Published by the Gentry and People（1870 上海英譯本）",
              "author": "託名「天下第一傷心人」編（湖南士紳集體託名，真實編者不詳）",
              "era": "原刻約一八六一；英譯本一八七〇",
              "place": "中國‧湖南／上海刊行",
              "language": "漢文原本；英文譯本",
              "intro": "晚清最具影響力的民間反教文獻之一，列舉所謂教會罪狀並附木刻插圖；1870 年在滬傳教士譯成英文出版，譯者序明言此書「大量促成近來遍傳中國、關於外僑與華人信徒的污衊謠言」，並稱其有助說明天津教案何以發生。"
            },
            {
              "title_zh": "西洋紀聞",
              "title_orig": "西洋紀聞",
              "author": "新井白石",
              "era": "約一七一五年撰成，一八八二年（明治十五）首刊",
              "place": "日本‧江戶",
              "language": "日文（和文體，非漢文訓讀體）",
              "parent": "新井白石全集",
              "extent": "三卷（上‧中‧下）",
              "intro": "據審訊耶穌會士西多提所得撰成，肯定西洋天文地理器械之學而判其宗教義理淺陋；鎖國體制下最具知性誠實的排耶論述。"
            },
            {
              "title_zh": "破提宇子",
              "title_orig": "破提宇子",
              "author": "不干齋巴鼻庵（Fabian Fucan）",
              "era": "一六二〇",
              "place": "日本‧長崎／肥前",
              "language": "日文",
              "intro": "棄教者所撰排耶書，逐條駁斥造物主、靈魂不滅與天堂地獄；出自內部人之手，東亞最具知識性的基督教批判之一。"
            },
            {
              "title_zh": "妙貞問答",
              "title_orig": "妙貞問答",
              "author": "不干齋巴鼻庵（Fabian Fucan）",
              "era": "一六〇五",
              "place": "日本‧京都",
              "language": "日文（近世和文）",
              "parent": "切支丹書‧護教書",
              "intro": "以兩位女性（切支丹幽貞與尼僧妙秀）問答形式寫成的三卷護教書，逐一破斥神道、儒教、佛教並陳述天主教義；原為女子修道／教理教育教材，後成為近世排耶書（含作者本人棄教後所著《破提宇子》）的直接論敵文本。"
            },
            {
              "title_zh": "破吉利支丹",
              "title_orig": "破吉利支丹",
              "author": "鈴木正三",
              "era": "一六六二",
              "place": "日本‧江戶／天草",
              "language": "日文",
              "intro": "曹洞宗禪僧鈴木正三以佛教立場撰寫的排耶論，逐條批駁天主教的造物主教義違背因果業報之理——若萬物由一全善之神所造，何以世間有惡與苦？他並質疑基督教否定祖先祭祀有悖孝道。此書是日本禁教期佛門排耶論述的代表作，反映佛教與基督教的正面思想交鋒。"
            },
            {
              "title_zh": "南蠻寺興廢記‧邪教大意（東洋文庫14）",
              "title_orig": "南蠻寺興廢記‧邪教大意",
              "author": "傳雪窗宗崔（雪窓宗崔）等；海老澤有道（海老沢有道）校注",
              "era": "傳十七世紀（《南蠻寺興廢記》學界多視為近世後期偽託之作，現存寫本有慶應四年一八六八序）；校注本一九六四",
              "place": "日本",
              "language": "日文（近世和文）",
              "intro": "平凡社東洋文庫第14冊，海老澤有道校注，同冊收《南蠻寺興廢記》《邪教大意》《妙貞問答》《破提宇子》四種。《邪教大意》為禁教期流通的排耶綱要；《南蠻寺興廢記》記京都南蠻寺興建與拆毀，兼具論戰與教會史料性格，惟其史實性可疑，一般視為近世後期依託之作，須作「排耶言說史料」而非信史使用。"
            },
            {
              "title_zh": "聖朝破邪集",
              "title_orig": "聖朝破邪集（破邪集）",
              "author": "徐昌治 輯",
              "era": "一六三九年（崇禎十二年）輯成",
              "place": "浙江",
              "language": "漢文",
              "extent": "八卷",
              "intro": "晚明反天主教文獻總集，徐昌治彙輯沈㴶「南京教案」奏疏以降的官紳與僧人闢教文字六十餘篇，含《參遠夷疏》、鍾始聲《天學初徵》《再徵》及釋氏破邪諸論。全書從華夷之辨、綱常倫理、祭祖問題與佛道立場多方駁斥利瑪竇一系的「天學」，是研究明末中西宗教衝突最集中的第一手史料，亦為東亞反基督教論述的代表作。"
            },
            {
              "title_zh": "不得已",
              "title_orig": "不得已",
              "author": "楊光先",
              "era": "一六六五年（康熙四年）刊",
              "place": "北京",
              "language": "漢文",
              "extent": "二卷",
              "intro": "楊光先攻擊耶穌會士湯若望與西洋曆法的論集，收〈闢邪論〉〈摘謬論〉〈選擇議〉等篇。他以「寧可使中夏無好曆法，不可使中夏有西洋人」一語著稱，指斥天主教敗壞綱常、曆法錯謬並圖謀不軌，直接促成康熙初年的曆獄，湯若望等下獄。此書是清初中西曆法與宗教衝突的關鍵文本，亦為儒者立場反教論述的典型。"
            }
          ]
        },
        {
          "key": "new-religions",
          "label": "新興宗教神學部",
          "label_en": "New Religious Movements",
          "desc": "巴哈伊與摩門等近代新興宗教的教義文獻。",
          "works": [
            {
              "title_zh": "已答之問",
              "title_orig": "Some Answered Questions",
              "author": "阿博都巴哈",
              "era": "一九〇八",
              "place": "鄂圖曼‧阿卡",
              "language": "波斯文",
              "intro": "巴哈伊信仰領袖阿博都巴哈於餐桌談話中答覆西方信徒提問的輯錄，由克利福德‧巴尼夫人記錄。內容涵蓋聖經與古蘭經的詮釋、漸進啟示、靈魂與來生、進化與創造、基督與諸先知的本質等。阿博都巴哈以理性調和宗教與科學，闡發巴哈伊「諸教同源、漸進啟示」的核心教義，是該信仰最重要的教義問答著作之一。"
            },
            {
              "title_zh": "教義與聖約",
              "title_orig": "Doctrine and Covenants",
              "author": "約瑟‧斯密等",
              "era": "一八三五",
              "place": "北美‧俄亥俄／密蘇里",
              "language": "英文",
              "intro": "摩門教（耶穌基督後期聖徒教會）的核心經典之一，輯錄創教者約瑟‧斯密及後繼領袖所宣稱領受的啟示。內容涉及教會組織、聖職體系、聖殿教儀、永恆婚姻與救恩計畫等獨特教義。此書與摩門經、無價珍珠並列為該教標準經典，是理解摩門神學體系的關鍵文獻，反映十九世紀美國新興宗教對基督教傳統的重大改造與擴充。"
            }
          ]
        },
        {
          "key": "antitrinitarian",
          "label": "反三一與激進改革部",
          "label_en": "Antitrinitarian & Radical Reformation",
          "desc": "塞爾維特等否定三一教義的激進改革思想。",
          "works": [
            {
              "title_zh": "三位一體謬誤論七卷",
              "title_orig": "De Trinitatis erroribus libri septem",
              "author": "塞爾維特（Michael Servetus）",
              "era": "1531",
              "place": "阿爾薩斯哈根諾（Hagenau）",
              "language": "拉丁文",
              "intro": "西班牙神學家塞爾維特（米迦勒‧塞爾韋圖斯，約 1511–1553）於 1531 年在哈根諾出版的反三位一體論著作，為宗教改革時代最激進的神學挑戰之一。全書七卷以聖經文本為據，主張尼西亞三位一體教義係希臘哲學污染之產物，耶穌非永恆的第二位格而是神性之子。此書同時觸怒天主教與改教陣營，終致塞爾維特 1553 年於日內瓦被審判火刑。本書為近代唯一神論與反尼西亞神學的奠基原典，具有不可忽略的神學史地位。"
            }
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
          { title_zh: '路德主義歷史護教注疏', title_orig: 'Commentarius historicus et apologeticus de Lutheranismo, sive, De reformatione religionis ductu D. Martini Lutheri', author: 'Veit Ludwig von Seckendorf', era: '1692', place: 'Leipzig', language: '拉丁文', intro: '德意志政治家兼史家澤肯道夫（1626–1692）以拉丁文撰成，針對天主教史家梅博爾（Louis Maimbourg）對路德宗的批駁，逐條提出歷史佐證與神學辯護。全書分歷史（historia）與護教（apologia）兩體裁，廣引原始文獻重構馬丁‧路德領導宗教改革之始末，涵蓋從威登堡爭論到奧斯堡信條的關鍵事件，是十七世紀新教正統時期最重要的改革史護教巨著之一。' },
          { title_zh: '帕克大主教生平事蹟錄——伊麗莎白女王時代坎特伯里首席大主教', title_orig: 'The Life and Acts of Matthew Parker, the First Archbishop of Canterbury in the Reign of Queen Elizabeth', author: 'Strype, John', era: '1711', place: 'London', language: '英文', intro: '英國聖公會神職人員兼教會史家史特萊普（John Strype，1643–1737）於1711年著成，記述馬太‧帕克（Matthew Parker，1504–1575）擔任坎特伯里大主教期間的生平與政教事業。帕克是伊麗莎白一世宗教改革之首席主教，主導三十九信條定稿、主教聖經編纂及英國國教體制奠定。本書廣泛援引帕克本人遺存文件與原始檔案，是研究伊麗莎白時代英國教會史不可或缺的早期傳記文獻，具史料一手性，非純粹二手學術研究。' },
          { title_zh: '格林達爾傳：倫敦首任主教暨約克與坎特伯里大主教行述', title_orig: 'The History of the Life and Acts of the Most Reverend Father in God, Edmund Grindal, the First Bishop of London, and the Second Archbishop of York and Canterbury', author: 'Strype, John', era: '1710', place: 'London', language: '英文', intro: '約翰‧史特萊普（John Strype）所著英國宗教改革史家傳，記述愛德蒙‧格林達爾（Edmund Grindal，約1519–1583）生平與事業。格林達爾歷任倫敦主教、約克大主教及坎特伯里大主教，於伊麗莎白一世時代力主清教士先知講道（prophesying），終以抗命女王而遭停職。本書為史特萊普系列改革時代主教傳記之一，徵引公文檔案與書信，是研究英格蘭國教會早期體制形成與清教主義萌芽的一手史傳要籍。' },
          { title_zh: '伯內特《英格蘭教會改革史》辨謬錄', title_orig: 'A Specimen of Some Errors and Defects in the History of the Reformation of the Church of England, Wrote by Gilbert Burnet', author: 'Wharton, Henry', era: '1693', place: 'London', language: '英文', intro: '英國聖公會學者亨利‧沃頓（Henry Wharton，1664–1695）針對吉爾伯特‧伯內特（Gilbert Burnet）所著《英格蘭教會改革史》提出系統性辨謬，逐條指出其史實訛誤與文獻疏漏。沃頓博覽中古教會原典，以第一手史料糾正伯內特的詮釋偏差，是英國宗教改革史學史上的重要史評文獻，體現十七世紀聖公會學界對本國改革傳承的嚴謹考辨態度，亦見證改革宗歷史書寫之爭議脈絡。' },
          { title_zh: '約翰‧諾克斯傳：蘇格蘭宗教改革史論', title_orig: 'Life of John Knox, containing Illustrations of the History of the Reformation in Scotland', author: 'M\'Crie, Thomas', era: '1811', place: 'Edinburgh', language: '英文', intro: '托馬斯‧麥克里（Thomas M\'Crie）所著，1813年愛丁堡初版，是十九世紀最具影響力的約翰‧諾克斯傳記。諾克斯（約1514–1572）為蘇格蘭宗教改革之父，主導建立長老制度並推動喀爾文主義在蘇格蘭生根。全書以翔實的一手史料與檔案為基礎，記述諾克斯的神學立場、與天主教勢力的衝突、《蘇格蘭信條》起草，以及改革宗教會的建立，兼具傳記與宗教改革史的雙重價值，是研究近代蘇格蘭教會史不可或缺的一手性敘事原典。' },
          { title_zh: '蘇格蘭教會與國家事務史（宗教改革初至1568年）', title_orig: 'History of the Affairs of Church and State in Scotland, from the Beginning of the Reformation to the Year 1568', author: 'Keith, Robert', era: '1734', place: 'Edinburgh', language: '英文', intro: '蘇格蘭主教暨史學家基斯（Robert Keith，1681–1757）所著教會史，記述蘇格蘭宗教改革肇始至1568年間教會與國家之交涉。本書依原始檔案與年代史料編纂，涵蓋瑪麗女王時代的宗教政爭、喀爾文主義長老教會興起、英格蘭聖公會勢力競逐，以及天主教舊教勢力衰退諸史事，為研究不列顛宗教改革史不可或缺之十八世紀第一手史學著作。' },
          { title_zh: '蘇格蘭教會真史——自改革肇始', title_orig: 'The True History of the Church of Scotland, from the Beginning of the Reformation', author: 'Calderwood, David', era: '約1620年代撰，1678年遺著刊行', place: 'London', language: '英文', intro: '卡德伍德（David Calderwood，1575–1650）為蘇格蘭長老會牧師及教會史家，本書為其畢生心血之作，詳記蘇格蘭宗教改革自16世紀初以降之始末，涵蓋改革宗教義確立、歷代大議會（General Assembly）決議、主教制廢立爭議及王權干涉諸事，為研究蘇格蘭長老宗體制形成的第一手史料。作者因反對詹姆士六世強推主教制而遭流亡，晚年方得返歸，全書抱持鮮明長老宗立場，遺著於1678年倫敦刊行。' }
        
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
          { title_zh: '耶穌基督會眾之初愛——初代基督徒信仰與聖潔生活真貌', title_orig: 'Die erste Liebe der Gemeinen Jesu Christi, das ist: Wahre Abbildung der ersten Christen nach ihrem lebendigen Glauben und heiligen Leben', author: 'Gottfried Arnold', era: '1696', place: 'Frankfurt', language: '德文', intro: '德國敬虔主義神學家戈特弗里德‧阿諾德（Gottfried Arnold, 1666–1714）早期代表作，以德文寫成，出版於法蘭克福。全書旨在描繪初代基督徒的靈性面貌——他們活潑的信仰與聖潔的生活——作為敬虔運動對當時僵化國家教會的批判與更新呼召。阿諾德援引教父文獻與初期教會史料，勾勒出使徒時代會眾（Gemeinde）彼此相愛、捨棄世俗的理想圖景。本書為其後來更具影響力的《公正教會暨異端史》（1699）奠定基礎，是近代新教敬虔主義史傳文學的重要先驅，同時亦具初代教會靈修史的一手詮釋價值。' },
          { title_zh: '蘇格蘭教會受難史', title_orig: 'The History of the Sufferings of the Church of Scotland from the Restoration to the Revolution', author: 'Wodrow, Robert', era: '1721', place: 'Edinburgh', language: '英文', intro: '本書為蘇格蘭長老會史家羅伯特‧沃德羅（Robert Wodrow, 1679–1734）依原始文件與親歷者證詞編撰的教會受難編年史，記述1660年英王查理二世復辟至1688年光榮革命期間，蘇格蘭長老派信徒在王政主教制強壓下所承受的迫害、流放與殉道事蹟。全書保存大量一手文獻，是認識「殺戮時代」（Killing Time）與蘇格蘭盟約運動不可或缺的史料原典，兼具殉道錄與教會史雙重性質。' }
        
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
          { title_zh: '毀滅印地亞斯簡述', title_orig: 'Brevísima relación de la destruición de las Indias', author: 'Bartolomé de las Casas', era: '1552', place: 'Sevilla', language: '西班牙文', intro: '道明會士、恰帕斯主教拉斯‧卡薩斯親歷西班牙征服美洲的暴行，以第一人稱見證陳述向卡斯提亞王廷呈報，逐一羅列加勒比海、中美洲、南美洲各地原住民遭屠殺、奴役、強徵勞動的慘況。此書是天主教傳教史上最早的良心異議文獻之一，促成1542年「新法」護印人律令的頒布，亦開啟近代基督教社會倫理對殖民暴力的批判傳統，為研究十六世紀天主教傳教運動與殖民接觸史不可或缺的原典。' },
          { title_zh: '大衛·布雷納德牧師生平記述', title_orig: 'An Account of the Life of the Late Reverend Mr. David Brainerd, Missionary among the Indians', author: 'Edwards, Jonathan', era: '1749', place: 'Boston', language: '英文', intro: '喬納森·愛德華茲（Jonathan Edwards）編輯整理大衛·布雷納德（David Brainerd，1718–1747）的日記與書信，出版此傳記。布雷納德是北美殖民地時代向印地安人傳教的清教徒宣教士，生命短暫卻充滿熱忱，其屬靈日記記錄了禱告、苦難與福音工作。本書成為近代新教宣教運動的經典靈修傳記，深遠影響威廉·克里、亨利·馬丁等後世宣教士，為敬虔主義傳統與宣教精神的重要原始文獻。' }
        
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
          { title_zh: '教會歷史論述', title_orig: 'Discours sur l\'histoire ecclésiastique', author: 'Claude Fleury', era: '1708', place: 'Paris', language: '法文', intro: '法國天主教神父、加里坎主義歷史學家弗勒里（Claude Fleury，1640–1723）所撰的教會史方法論論述，為其畢生鉅著《教會史》（Histoire ecclésiastique，20卷，涵蓋基督升天至1414年）的導論性文字。弗勒里在文中闡述如何閱讀與詮釋教會歷史，主張回歸原始史料、擺脫教派偏見，帶有加里坎主義色彩（限制教宗絕對權威）。作為近代教會史學方法的一手文獻，具重要史料價值。（首版1708年；OpenLibrary OL4763907W 為1747年再版）' },
          { title_zh: '英國居普良：坎特伯里大主教威廉‧勞德生平與殉道史', title_orig: 'Cyprianus Anglicus: or, The History of the Life and Death of William Laud, Lord Archbishop of Canterbury', author: 'Heylyn, Peter', era: '1668', place: 'London', language: '英文', intro: '彼得‧海林著，1668 年身後出版。以「英國居普良」為題，將坎特伯里大主教威廉‧勞德比附古代殉道主教居普良，記述其生平、主教事業、神學立場與1645年被議會處決始末。勞德力推高教會禮儀改革，試圖統一英格蘭與蘇格蘭禮拜儀式，觸發三王國戰爭，終遭清教徒主導之議會定罪。本書為同時代一手史料，兼具傳記、教會史與護教性質，是研究17世紀英國聖公會與主教制存廢之爭的重要文獻。' },
          { title_zh: '阿利烏再現：長老宗史', title_orig: 'Aerius Redivivus: or, The History of the Presbyterians', author: 'Heylyn, Peter', era: '1670（成書約1661年前後）', place: 'Oxford', language: '英文', intro: '英國高教會派神職人員希林（Peter Heylyn，1600–1662）所撰之長老宗論戰史。書名借用四世紀異端「阿利烏」之名，暗指長老宗乃古異端之復燃。全書涵蓋1536至1647年間長老宗的興起、擴張及其對君主制與主教制的衝擊，並記述其在英格蘭、蘇格蘭及歐陸諸邦引發的政治動盪。希林以查理一世與查理二世御用牧師的身份執筆，立場鮮明地捍衛英國國教主教制傳統，是研究英國宗教改革後期教派衝突的重要一手史料，亦是17世紀高教會護教文學的代表作。' },
          { title_zh: '英格蘭聖史：英格蘭歷代大主教與主教史料彙編', title_orig: 'Anglia Sacra, sive Collectio Historiarum, partim antiquitus, partim recenter scriptarum, de Archiepiscopis et Episcopis Angliae, a prima fidei Christianae susceptione ad annum MDXL', author: 'Wharton, Henry', era: '1691', place: 'London', language: '拉丁文', intro: '英國教會史學家亨利‧沃頓（Henry Wharton）於1691年編纂，為英格蘭歷代大主教與主教的史料總集，以拉丁文寫成，分兩冊收錄坎特伯雷、約克及其他教區的主教傳記、編年紀事與原始文獻。沃頓廣徵中世紀手稿，匯集諸多此前未刊行的教會史料，是研究盎格魯-薩克遜至中世紀英格蘭主教制度及教會組織的重要史傳工具書。此書奠定近代英國教會史研究基礎，至今仍是教會史與聖公宗學術研究的一手文獻依據。' },
          { title_zh: '大不列顛教會史', title_orig: 'An Ecclesiastical History of Great Britain, Chiefly of England, from the First Planting of Christianity to the End of the Reign of Charles the Second', author: 'Collier, Jeremy', era: '1708', place: 'London', language: '英文', intro: '英國國教會歷史學家傑里米‧科利爾（Jeremy Collier，1650–1726）所著大型教會史，以英格蘭為主軸，上溯基督教傳入不列顛之始，下迄查理二世駕崩（1685）。全書依年代編排，廣徵教廷文件、公會議紀錄、主教傳記及世俗史料，為近代英語世界最早系統性處理英國教會通史之巨著。科利爾身為非宣誓派英國國教司鐸，立場偏向高教會，書中對宗教改革及清教主義着墨甚多，是研究英格蘭教會史及聖公宗早期史學的重要一手史傳文獻。' },
          { title_zh: '不列顛教會源流考', title_orig: 'Origines Britannicae; or, The Antiquities of the British Churches', author: 'Stillingfleet, Edward', era: '1685', place: 'London', language: '英文', intro: '英國聖公會主教愛德華‧史蒂林弗利特（Worcester主教）所著，追溯基督教傳入不列顛群島的源流與早期教會史跡。全書廣徵古典文獻與早期教父史料，論證不列顛教會之使徒淵源，兼及凱爾特教會、羅馬教會進入英格蘭的歷史經過，具有強烈的英國國教護教立場。此書為17世紀英國教會史學的重要一環，體現宗教改革後新教主流對本國教會獨立古史的建構努力，至今仍為研究早期英格蘭教會史的一手參考文獻。' },
          { title_zh: '威廉‧勞德大主教患難受審始末錄', title_orig: 'The History of the Troubles and Tryal of the Most Reverend Father in God, William Laud, Lord Archbishop of Canterbury', author: 'Laud, William', era: '1695（成書約1640年代，身後出版）', place: 'London', language: '英文', intro: '威廉‧勞德（1573–1645）任英格蘭教會坎特伯雷大主教，為查理一世時代高教會派（High Church）首要領袖，力推禮儀統一與主教制，與清教徒及議會對立。本書記錄其遭彈劾、系獄倫敦塔及受審全程，兼收其本人日誌與答辯文書，係英國宗教改革後期教會政治衝突與殉難精神的第一手史料，對研究英國國教會與清教主義之角力具不可替代之史料價值。' },
          { title_zh: '蘇格蘭教會史', title_orig: 'The History of the Church of Scotland, beginning the year of our Lord 203, and continued to the end of the reign of King James VI', author: 'Spottiswoode, John', era: '1655', place: 'London', language: '英文', intro: '蘇格蘭聖公會大主教斯波蒂斯伍德（John Spottiswoode，1565–1639）所著蘇格蘭教會通史，自公元203年起迄詹姆士六世統治末年。作者曾任聖安德魯斯大主教，親歷蘇格蘭宗教改革後期政教角力，書中詳述蘇格蘭早期基督教傳入、宗教改革、長老制與主教制之爭，以及王室宗教政策演變，為研究蘇格蘭改革宗與聖公會歷史的重要一手史料，1655年身後出版。' },
          { title_zh: '日內瓦教會史：自宗教改革肇始至今日', title_orig: 'Histoire de l\'Église de Genève depuis le commencement de la réformation jusqu\'à nos jours', author: 'Gaberel, Jean-Pierre', era: '1855', place: 'Genève', language: '法文', intro: '法語教會史著作，記述日內瓦教會自十六世紀宗教改革肇始至十九世紀中葉的歷史沿革。日內瓦為喀爾文神學重鎮，本書系統梳理改革宗在此地的建制過程、神學論爭、教會治理及歷代牧者事蹟。作者加柏雷爾（Jean-Pierre Gaberel）以編年體鋪陳，涵蓋十六至十九世紀約三百年間喀爾文主義於日內瓦的發展脈絡，為研究改革宗教會史及瑞士新教史的重要原始文獻。' },
          { title_zh: '哈勒敬虔：世上神聖臨在足跡之公開見證', title_orig: 'Pietas Hallensis: or, a publick demonstration of the foot-steps of a divine being yet in the world', author: 'Francke, August Hermann', era: '1705', place: 'London', language: '英文', intro: '德國路德宗敬虔主義領袖法蘭克（August Hermann Francke，1663–1727）親筆撰就的哈勒孤兒院歷史紀錄，1705年出版英譯本。全書以「上帝足跡」為主軸，詳述作者如何在薩克森哈勒附近的格勞豪建立孤兒院及多所慈善機構，並以逐年紀事的方式見證神聖護佑的具體彰顯。此書既是哈勒敬虔主義運動的第一手原典，也是近代教會社會改革史的重要史傳文獻，深刻影響衛斯理兄弟及後來的宣教與慈善事業。' },
          { title_zh: '敬虔主義史', title_orig: 'Die Geschichte des Pietismus', author: 'Schmid, Heinrich', era: '1863', place: 'Erlangen', language: '德文', intro: '埃爾朗根大學路德宗神學家海因里希‧施密特於 1863 年撰寫的敬虔主義運動史，系統梳理自 17 世紀施本爾（Spener）、法蘭克（Francke）以降至 18 世紀欽岑道夫（Zinzendorf）的敬虔派發展脈絡，涵蓋其神學特徵、組織形態與對路德宗正統主義之衝擊。為19世紀德語教會史學的代表著作之一，具原典史料價值。' },
          { title_zh: '施本爾傳', title_orig: 'Philipp Jakob Spener', author: 'Grünberg, Paul', era: '1893', place: 'Göttingen', language: '德文', intro: '本書為德國神學者葛倫伯格（Paul Grünberg）所撰腓力‧雅各‧施本爾（Philipp Jakob Spener, 1635–1705）傳記，成書於 1893 年。施本爾為路德宗敬虔主義創始人，著《虔誠的期望》（Pia Desideria），力倡內在靈修、小組查經（collegia pietatis）及信徒皆祭司觀念，深刻影響近代新教靈命更新運動。本傳記詳述其生平、神學思想及在哈勒敬虔運動中的奠基角色，是研究近代新教敬虔主義的重要史傳文獻。' },
          { title_zh: '新舊約教會史簡編', title_orig: 'Kurtz-gefasste Kirchen-Historie des Alten und Neuen Testaments', author: 'Arnold, Gottfried', era: '1697', place: 'Frankfurt am Main', language: '德文', intro: '德國路德宗敬虔主義神學家暨教會史家葛特弗里德‧阿諾德（1666–1714）所撰，為其大型著作《公正的教會與異端史》（1699–1700）的簡編本，自舊約時代縱貫至十七世紀末的教會歷史。阿諾德以激進敬虔主義視角重新詮釋教會史，批判建制教會的權力腐化，為遭迫害的異端少數平反，主張他們才是保存真正基督信仰的群體。此書是近代新教教會史書寫的重要一手原典，反映敬虔主義時代「信仰個人化」的歷史意識，對啟蒙時期宗教史學影響深遠。' },
          { title_zh: '神祕神學歷史與描述', title_orig: 'Historie und Beschreibung der Mystischen Theologie', author: 'Arnold, Gottfried', era: '1703', place: 'Frankfurt am Main', language: '德文', intro: '德國路德宗敬虔派神學家戈特弗里德‧阿諾德（1666–1714）所著，全題為《神祕神學或隱祕神知歷史與描述，及古今神祕主義者述要》。阿諾德繼其1699年《無偏黨教會與異端史》後，轉以神祕靈修傳統為主題，梳理自教父至當代的神祕神學家譜系，並為其平反辯護。此書既是教會靈修史的一手史料，亦反映敬虔主義與路德正統之間的思想張力，為研究近代初期新教神祕主義的重要原典。' },
          { title_zh: '美洲基督偉蹟——新英格蘭教會史', title_orig: 'Magnalia Christi Americana, or, The Ecclesiastical History of New-England', author: 'Mather, Cotton（馬瑟‧科頓）', era: '1702', place: 'London', language: '英文', intro: '美洲清教徒最宏大的一手教會史著作。清教牧師科頓‧馬瑟（1663–1728）以七冊約八百頁對開本，記錄新英格蘭自 1620 年建殖至 1698 年的教會發展，內容含總督列傳、著名牧師傳記（篇幅最長）、哈佛學院史、崇拜方式、神意奇事誌，以及教會遭受侵害的歷史，並附薩勒姆巫審記述。全書以末世神學為主軸，論新英格蘭乃基督再臨前的「新耶路撒冷」，是研究北美清教主義的原典級文獻。' },
          { title_zh: '至尊博學科頓‧馬瑟博士傳', title_orig: 'The Life of the Very Reverend and Learned Cotton Mather, D.D. & F.R.S.', author: 'Mather, Samuel', era: '1729', place: 'Boston', language: '英文', intro: '本書為科頓‧馬瑟（Cotton Mather, 1663–1728）之子塞繆爾‧馬瑟（Samuel Mather）所撰當代傳記，成書於科頓辭世翌年（1729）。科頓‧馬瑟為北美殖民地清教主義最具代表性的公理宗牧師與神學家，兼任麻薩諸塞灣殖民地波士頓北端教會（Old North Church），著作逾400種，並為英國皇家學會院士（F.R.S.）。本傳記由親歷者撰寫，兼具第一手史料與信仰見證性質，記錄其神學立場、對女巫審判事件之態度及清教傳道事業，是研究北美新教初期歷史的重要原典史傳。' },
          { title_zh: '亞伯雖死仍言：棉頓先生生平與辭世', title_orig: 'Abel Being Dead Yet Speaketh, or, The Life and Death of Mr. John Cotton', author: 'Norton, John', era: '1658', place: 'London', language: '英文', intro: '約翰‧諾頓（John Norton）為清教徒牧師約翰‧棉頓（John Cotton，1585–1652）所撰傳記，出版於 1658 年。棉頓曾在英格蘭林肯郡波士頓任職，後移居麻薩諸塞灣殖民地，成為新英格蘭清教神學與政教秩序的核心人物。書名引希伯來書十一章四節「亞伯雖死，仍舊說話」，以殉道學典故崇揚棉頓一生事蹟與靈命遺產。此書為研究早期新英格蘭清教主義及宗教改革第二代傳播的第一手傳記文獻，具重要史料價值。' },
          { title_zh: '懷特菲爾德日誌', title_orig: 'George Whitefield\'s Journals', author: 'Whitefield, George', era: '1738', place: 'London', language: '英文', intro: '喬治‧懷特菲爾德（1714–1770）為英國衛理宗與大覺醒運動核心人物，本書收錄其自1737至1741年間親筆日誌，詳述英格蘭、威爾斯及北美佐治亞殖民地的宣道旅程、屬靈掙扎與大型野外聚會實況。日誌一手呈現十八世紀福音復興運動的地理擴張與靈性強度，為研究英美清教徒敬虔傳統及大覺醒運動不可或缺的原典史料，屬近代新教史傳一手文獻。' },
          { title_zh: '俄羅斯教會史', title_orig: 'Istoriia russkoi tserkvi (История русской церкви)', author: 'Makarij (Bulgakov), Metropolitan of Moscow', era: '1857–1883', place: 'Moskva', language: '俄文', intro: '莫斯科都主教馬卡里（布爾加科夫，1816–1882）畢生巨著，系統記述俄羅斯東正教會自基督教傳入斯拉夫諸族至近代的歷史演變，涵蓋教會建制、主教傳承、修道院運動、神學發展與政教關係。全書分多卷，援引原始教會文獻與國家檔案，是俄國正教史學的奠基性史傳著作。1994年莫斯科版為蘇聯解體後之重印本，使這部十九世紀正教史學經典重新流通。' },
          { title_zh: '大牧首與沙皇', title_orig: 'The Patriarch and the Tsar', author: 'Palmer, William', era: '1871–1876', place: 'London', language: '英文', intro: '英國牛津運動神學家威廉‧帕爾默（1811–1879）編譯之六卷文獻集，聚焦俄國大牧首尼康（Nikon，1605–1681）與沙皇阿列克謝之間的政教衝突。內容涵蓋尼康本人對貴族審問的答辯、安提阿牧首馬卡里烏斯巡遊俄國之阿拉伯文記述（由其子保羅撰寫）、1666–1667年莫斯科全體主教會議對尼康定罪之史錄，及其禮儀改革功過評析。為研究近代俄國教會自主化與政教關係的一手史料總匯。' },
          { title_zh: '從農民到宗主教：尼康聖下的誕生、成長與生平記述', title_orig: 'From Peasant to Patriarch: Account of the Birth, Upbringing, and Life of His Holiness Nikon', author: 'Shusherin, Ioann (trans. Kain, Kevin M.; Levintova, Katia)', era: '約1680年代成書（原著）；2007年英譯出版', place: 'Lanham, Maryland', language: '英文', intro: '俄羅斯東正教宗主教尼康（Nikon，1605–1681）的同時代傳記，原著者舒謝林（Ioann Shusherin）為尼康親信，以親歷見聞記述其出身農家、修道、擢升至莫斯科宗主教之全程，並涉及17世紀俄羅斯教會大分裂（Raskol）前後的禮儀改革與政教衝突。本書屬第一手聖徒行傳體傳記，2007年英譯本首度向西方學界開放此一珍貴史料，是研究近代俄羅斯東正教史與宗主教制度的原典性文獻。' },
          { title_zh: '俄羅斯教會史考', title_orig: 'Beyträge zur russischen Kirchengeschichte', author: 'Strahl, Philipp Carl', era: '1827', place: '德國哈勒', language: '德文', intro: '德國史家 Philipp Strahl 著，1827 年刊行，為德語學界早期研究俄羅斯東正教會史的奠基文獻。書名意為「俄羅斯教會史料叢考」，涵蓋俄羅斯基督教化過程、教會建制沿革、主教承傳及禮儀發展等議題，資料引自斯拉夫語及拉丁語原始文獻，反映啟蒙後期西歐學者以歷史批判眼光整理東方教會史料的治學取向，是近代歐洲東正教研究的重要先驅著作。' },
          { title_zh: '希臘教會史入門', title_orig: 'A Student\'s History of the Greek Church', author: 'Hore, Alexander Hugh', era: '1902', place: 'London', language: '英文', intro: '霍爾（Alexander Hugh Hore）於1902年在倫敦出版的希臘東正教會通史教科書，以學生讀者為對象，系統梳理希臘正教會自早期教會至近代的歷史發展脈絡，涵蓋大分裂、拜占庭帝國覆滅後的教會生存、鄂圖曼統治下的牧首制，及近代希臘獨立建國後的教會重建，為英語世界19世紀末東正教史入門要籍。' }
        
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
          { title_zh: '沃爾頓多語聖經', title_orig: 'Biblia Sacra Polyglotta', author: '沃爾頓 (Brian Walton) 主編', era: '一六五七年', place: '倫敦', language: '希伯來文‧亞蘭文‧撒瑪利亞文‧希臘文‧拉丁文‧敘利亞文‧阿拉伯文‧衣索比亞文‧波斯文', intro: '沃爾頓主編的倫敦多語聖經，集當時所能蒐羅的古代譯本之大成，多達九種語言逐欄對照，並附各譯本的考訂緒論與異文。它把多語對照的規模推至空前，為比較各古譯傳統、追溯經文源流提供了浩繁的材料，是十七世紀聖經學術的巔峰之一。', link: '/scripture' },
          { title_zh: '安特衛普多語聖經', title_orig: 'Biblia Regia (Antwerp Polyglot)', author: '蒙塔努斯主編（普朗坦印行）', era: '1568–1573', place: '安特衛普', language: '希伯來／希臘／拉丁／亞蘭／敘利亞文', intro: '腓力二世資助、普朗坦印坊八巨冊的「王家聖經」，首度加入敘利亞文新約，附語法辭典整套工具。康普魯頓的接棒之作，十六世紀印刷與東方學的合璧豐碑。' },
          { title_zh: '巴黎多語聖經', title_orig: 'Polyglotte de Paris', author: '勒‧傑伊主持', era: '1628–1645', place: '巴黎', language: '七語對照', intro: '十巨冊的巴黎多語聖經首度收入撒瑪利亞五經與阿拉伯文譯本，氣魄空前而近乎傾家蕩產。多語聖經競賽的法蘭西一峰，倫敦本即以之為藍本而後來居上。' },
          { title_zh: '新約註解（瓦拉）', title_orig: 'Adnotationes in Novum Testamentum', author: '洛倫佐‧瓦拉', era: '約 1444（1505 伊拉斯謨刊）', place: '羅馬／那不勒斯', language: '拉丁文', intro: '人文學宗師瓦拉以希臘原文校勘武加大的注記，半世紀後由伊拉斯謨發現刊行而點燃新約語文學。「回到原文」革命的火種文獻，文藝復興批判學轉入聖經的第一步。' },
          { title_zh: '勒菲弗聖經工程', title_orig: 'Quincuplex Psalterium / La Saincte Bible', author: '勒菲弗‧德‧埃塔普勒', era: '1509–1530', place: '巴黎／莫城', language: '拉丁文／法文', intro: '法國人文主義者勒菲弗自五重詩篇對照到首部法譯全本聖經的譯校志業，莫城改革圈的學術心臟。法語聖經傳統的源頭，奧利韋唐譯本的直接前驅。' },
          { title_zh: '帕格尼努斯直譯拉丁聖經', title_orig: 'Veteris et Novi Testamenti nova translatio', author: '桑特斯‧帕格尼努斯', era: '1528', place: '里昂', language: '拉丁文', intro: '道明會希伯來學家帕格尼努斯自原文逐字直譯的拉丁聖經，千年來第一部取代武加大的完整新譯。其字對字風格成為各語譯者的對照基準，譯經史的隱形樞紐。' },
          { title_zh: '卡斯泰利奧拉丁聖經', title_orig: 'Biblia sacra latina (Castellio)', author: '塞巴斯蒂安‧卡斯泰利奧', era: '1551', place: '巴塞爾', language: '拉丁文', intro: '寬容論先驅卡斯泰利奧以西塞羅式優雅拉丁重譯全本聖經，獻詞直諫愛德華六世寬待異見。與加爾文決裂的譯者之作，翻譯風格論戰「典雅對直譯」的經典一造。' },
          { title_zh: '特雷梅利烏斯拉丁舊約', title_orig: 'Biblia sacra (Tremellius-Junius)', author: '伊曼紐爾‧特雷梅利烏斯與尤尼烏斯', era: '1575–1579', place: '法蘭克福／海德堡', language: '拉丁文', intro: '猶太改宗學者特雷梅利烏斯自希伯來與敘利亞原文譯出的新教標準拉丁舊約。改革宗學界一百年的通用學術譯本，米爾頓與清教神學的案頭聖經。' },
          { title_zh: '穆斯特希伯來拉丁對照聖經', title_orig: 'Hebraica Biblia (Münster)', author: '塞巴斯蒂安‧穆斯特', era: '1534–1535', place: '巴塞爾', language: '希伯來文／拉丁文', intro: '希伯來學家穆斯特刊行的希伯來-拉丁對照舊約，注記廣引拉比註釋。新教希伯來學的橋頭堡，路德與英譯者案頭的原文工具。' },
          { title_zh: '埃斯蒂安分節希臘文新約', title_orig: 'Novum Testamentum (Stephanus 1551)', author: '羅貝爾‧埃斯蒂安', era: '1551', place: '日內瓦', language: '希臘文', intro: '王家印刷師埃斯蒂安在此版首創新約分節，傳說於巴黎至里昂馬背上劃定。今日全球聖經章節座標的誕生地，印刷者改寫讀經方式的著名一筆。' }
        
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
          { title_zh: '杜埃-蘭斯譯本', title_orig: 'The Holie Bible (Douay–Rheims)', author: '蘭斯與杜埃英籍天主教學院 (馬丁 Gregory Martin 主譯)', era: '新約一五八二年‧舊約一六〇九至一六一〇年', place: '蘭斯‧杜埃', language: '英文', intro: '流亡歐陸的英籍天主教學者所譯,據拉丁武加大本譯成英文,以與新教各英譯相抗衡。譯文謹守拉丁原貌,多存教會傳統用語,並附駁斥新教釋義的註解。它是天主教傳統最重要的英文聖經,後經查理納主教 (Richard Challoner) 修訂而長行於英語天主教界。', link: '/scripture' },
          { title_zh: '蘇黎世聖經', title_orig: 'Zürcher Bibel (Froschauer)', author: '茲文利與尤德等（弗羅紹爾印行）', era: '1531', place: '蘇黎世', language: '德文', intro: '茲文利圈完成的德語全本聖經，早路德全本三年，附插圖與序論。改革宗譯經傳統的第一部全書，瑞士德語的形塑文獻，至今蘇黎世聖經仍承其名。' },
          { title_zh: '奧利韋唐法譯聖經', title_orig: 'Bible d\'Olivétan', author: '皮埃爾‧羅貝爾‧奧利韋唐', era: '1535', place: '納沙泰爾', language: '法文', intro: '加爾文表兄奧利韋唐自原文譯出的首部新教法語聖經，瓦勒度派山谷信徒集資刊印，加爾文作拉丁序。法語新教聖經傳統的源頭，日內瓦聖經系譜的第一環。' },
          { title_zh: '熊聖經', title_orig: 'Biblia del Oso (Reina-Valera)', author: '卡西奧多羅‧德‧雷納（瓦萊拉修訂）', era: '1569（1602 修訂）', place: '巴塞爾／阿姆斯特丹', language: '西班牙文', intro: '逃亡修士雷納在異端裁判追緝下譯成的西語全本聖經，扉頁熊取蜜圖案得名，瓦萊拉修訂本沿用至今。西語世界新教的根本聖經，流亡者譯經的世紀傳奇。' },
          { title_zh: '阿爾梅達葡譯聖經', title_orig: 'Bíblia de Almeida', author: '若昂‧費雷拉‧德‧阿爾梅達', era: '1681（新約）起', place: '巴達維亞', language: '葡萄牙文', intro: '十四歲離鄉的阿爾梅達在荷屬東印度譯成葡語聖經，身後由同工補全舊約。葡語世界流傳最廣的譯本至今冠其名，殖民航路上誕生的母語聖經。' },
          { title_zh: '迪奧達蒂義譯聖經', title_orig: 'La Bibbia di Diodati', author: '喬瓦尼‧迪奧達蒂', era: '1607', place: '日內瓦', language: '義大利文', intro: '盧卡流亡世家的日內瓦教授迪奧達蒂獨力譯成的義語聖經，典雅足與欽定本並稱。義大利新教數百年的標準聖經，母國禁絕而在阿爾卑斯谷地與海外傳誦。' },
          { title_zh: '荷蘭國家譯本', title_orig: 'Statenvertaling', author: '多特會議委任譯者團', era: '1637', place: '萊頓', language: '荷蘭文', intro: '多特會議決議、國會出資的荷語聖經，譯注嚴謹並統一了荷蘭書面語。「國家譯本」之名名副其實，荷蘭語文與加爾文文化的共同奠基石。' },
          { title_zh: '克拉利茨聖經', title_orig: 'Bible kralická', author: '波希米亞弟兄合一會譯者團', era: '1579–1593', place: '克拉利茨', language: '捷克文', intro: '弟兄合一會在秘密印坊完成的六卷本捷克語聖經，自原文譯出並附詳注。捷克語的黃金標準，白山之敗後流亡者懷中的民族聖書，誇美紐斯稱之為最珍貴遺產。' },
          { title_zh: '維茲索裡聖經', title_orig: 'Vizsolyi Biblia (Károli)', author: '卡羅利‧加什帕爾', era: '1590', place: '維茲索裡', language: '匈牙利文', intro: '改革宗牧師卡羅利率團隊譯成的首部匈語全本聖經，於維茲索裡村邊印邊譯而成。匈牙利文學語言的奠基之作，四百年來新教匈人的「卡羅利聖經」。' },
          { title_zh: '武耶克波蘭聖經', title_orig: 'Biblia Wujka', author: '雅各‧武耶克', era: '1599', place: '克拉科夫', language: '波蘭文', intro: '耶穌會士武耶克自武加大譯出兼參原文的波蘭語聖經，文采使其超越宗派而為全民族誦讀。波蘭語的欽定本，沿用至二十世紀中葉的天主教標準譯本。' },
          { title_zh: '克里斯蒂安三世丹麥聖經', title_orig: 'Christian III\'s Bibel', author: '丹麥王室譯者團（承路德本）', era: '1550', place: '哥本哈根', language: '丹麥文', intro: '丹麥宗教改革後王室頒行的首部丹語全本聖經，依路德本轉譯而印製精美。丹麥挪威兩國的官定聖經，斯堪的納維亞路德宗化的語言工程。' },
          { title_zh: '古斯塔夫‧瓦薩聖經', title_orig: 'Gustav Vasas bibel', author: '佩特里兄弟等（瑞典王室委譯）', era: '1541', place: '烏普薩拉', language: '瑞典文', intro: '瓦薩王朝頒行的瑞典語全本聖經，確立瑞典語正字法與「å ä ö」字母。瑞典書面語的出生證明，語言史以此書分割古今瑞典語。' },
          { title_zh: '古德布蘭杜爾冰島聖經', title_orig: 'Guðbrandsbiblía', author: '古德布蘭杜爾‧索爾拉克松主教', era: '1584', place: '侯拉爾', language: '冰島文', intro: '侯拉爾主教古德布蘭杜爾在極北孤島自設印坊印成的冰島語全本聖經，插圖精美近乎奇蹟。冰島語得以純存至今，此書之功居半，最小語言社群的最大譯經壯舉。' },
          { title_zh: '阿格里科拉芬蘭語新約', title_orig: 'Se Wsi Testamenti', author: '米卡埃爾‧阿格里科拉', era: '1548', place: '斯德哥爾摩刊行', language: '芬蘭文', intro: '圖爾庫主教阿格里科拉為譯新約而創製芬蘭書面語，序言自陳「這語言從前無人書寫」。芬蘭文學語言的誕生文件，芬蘭至今以其日為「芬蘭語日」。' },
          { title_zh: '摩根威爾斯語聖經', title_orig: 'Y Beibl cyssegr-lan (William Morgan)', author: '威廉‧摩根', era: '1588', place: '倫敦刊行', language: '威爾斯文', intro: '摩根主教譯成的威爾斯語全本聖經，敕令置於全境教堂。凱爾特語中唯一未衰亡者，語言學家公認此譯本為威爾斯語存續的第一功臣。' },
          { title_zh: '貝多爾愛爾蘭語聖經', title_orig: 'Bedell\'s Irish Bible', author: '威廉‧貝多爾主教主持', era: '1640 譯成（1685 刊）', place: '基爾莫爾', language: '愛爾蘭文', intro: '英裔主教貝多爾力排眾議主持愛爾蘭語舊約翻譯，內戰中譯稿倖存而身後刊行。殖民語境中罕見的母語尊重個案，蓋爾語聖經傳統的基石。' },
          { title_zh: '主教聖經', title_orig: 'The Bishops\' Bible', author: '帕克大主教主持', era: '1568', place: '倫敦', language: '英文', intro: '伊莉莎白朝為抗衡日內瓦聖經而由主教團修訂的官定譯本，欽定本即以其為修訂底本。英譯系譜中承先啟後的官方一環，教堂誦讀本的都鐸標準。' },
          { title_zh: '達爾馬廷斯洛維尼亞聖經', title_orig: 'Dalmatinova Biblija', author: '尤里‧達爾馬廷', era: '1584', place: '維滕堡刊行', language: '斯洛維尼亞文', intro: '達爾馬廷譯成的斯洛維尼亞語全本聖經，反宗教改革焚書亦允天主教士留用，因無可替代。斯洛維尼亞語言與民族認同的第一書。' },
          { title_zh: '格呂克拉脫維亞聖經', title_orig: 'Glika Bībele', author: '恩斯特‧格呂克', era: '1685–1694', place: '里加', language: '拉脫維亞文', intro: '德裔牧師格呂克譯成的首部拉脫維亞語聖經，養女後為俄國女皇葉卡捷琳娜一世。拉脫維亞書面語的奠基之作，波羅的海譯經史的傳奇。' },
          { title_zh: '薩西法譯聖經', title_orig: 'Bible de Port-Royal (Sacy)', author: '勒梅特‧德‧薩西', era: '1667–1696', place: '巴黎（巴士底獄中部分譯成）', language: '法文', intro: '波爾-羅亞爾隱士薩西譯成的法語聖經，部分成於巴士底獄中，文體優雅為法語散文典範。天主教法語譯經的高峰，帕斯卡圈的聖經，通行法國兩百年。' },
          { title_zh: '馬爾提尼義譯聖經', title_orig: 'La Bibbia di Antonio Martini', author: '安東尼奧‧馬爾提尼', era: '1769–1781', place: '杜林', language: '義大利文', intro: '馬爾提尼總主教自武加大譯成並獲教宗嘉許的義語聖經，附註詳明。天主教義大利的官准譯本，十九二十世紀義國家庭的通行聖書。' },
          { title_zh: '奧斯特羅格聖經', title_orig: 'Острозька Біблія', author: '奧斯特羅格斯基公爵府學者團（費奧多羅夫印行）', era: '1581', place: '沃里尼亞奧斯特羅格', language: '教會斯拉夫文', intro: '奧斯特羅格公爵集希臘與斯拉夫學者、由先驅印刷師費奧多羅夫印成的首部斯拉夫語全本印刷聖經。東斯拉夫正教文化的堡壘工程，其文本規範此後一切斯拉夫聖經。' },
          { title_zh: '斯科裡納魯塞尼亞聖經', title_orig: 'Біблія руска (Skaryna)', author: '弗蘭齊斯克‧斯科裡納', era: '1517–1519', place: '布拉格／維爾紐斯', language: '魯塞尼亞文（教會斯拉夫混合）', intro: '白羅斯醫學博士斯科裡納在布拉格刊印的聖經諸卷，序跋以民語申明「令庶民識智慧」。東斯拉夫印刷與人文主義的黎明之作，白羅斯文化的第一座豐碑。' },
          { title_zh: '伊莉莎白欽定斯拉夫聖經', title_orig: 'Елизаветинская Библия', author: '俄國聖務院校訂團', era: '1751', place: '聖彼得堡', language: '教會斯拉夫文', intro: '彼得大帝發起、伊莉莎白女皇完成的斯拉夫聖經大校訂，依七十士本逐卷勘正。俄國正教會禮儀用經的定本至今，帝國學術與教會傳統的合鑄。' },
          { title_zh: '俄語會議譯本', title_orig: 'Синодальный перевод', author: '俄國聖務院譯者團（費拉列特推動）', era: '1876', place: '聖彼得堡／莫斯科', language: '俄文', intro: '歷經半世紀爭議方告完成的俄語白話聖經，都主教費拉列特力排「俗語褻聖」之議推動至終。杜斯妥也夫斯基世代的聖經，至今俄語世界新舊教共用的標準譯本。' },
          { title_zh: '布加勒斯特聖經', title_orig: 'Biblia de la București', author: '瓦拉幾亞公國譯者團', era: '1688', place: '布加勒斯特', language: '羅馬尼亞文', intro: '瓦拉幾亞公爵資助譯成的首部羅馬尼亞語全本聖經，統合先前各省譯稿。羅馬尼亞語文學語言的奠基文本，東正教俗語譯經的先行者。' },
          { title_zh: '卡拉季奇塞爾維亞語新約', title_orig: 'Novi zavjet (Vuk Karadžić)', author: '武克‧卡拉季奇', era: '1847', place: '維也納', language: '塞爾維亞文', intro: '語言改革家卡拉季奇以民間口語譯成塞爾維亞語新約，與其正字法改革同為「以民語立國」工程。教會斯拉夫語霸權的突破口，塞爾維亞現代語文的建國文本。' },
          { title_zh: '內奧菲特保加利亞語新約', title_orig: 'Новий Завет (Неофит Рилски)', author: '里拉的內奧菲特', era: '1840', place: '斯米爾納刊行', language: '保加利亞文', intro: '里拉修士內奧菲特譯成的新保加利亞語新約，聖經公會刊行而風行民間。保加利亞民族復興的語言事件，現代保語書面語的推手之一。' }
        
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
          { title_zh: '委辦譯本', title_orig: '委辦譯本聖經', author: '在華新教各差會委辦委員會 (麥都思 Walter Henry Medhurst、理雅各 James Legge 等)', era: '新約一八五二年‧舊約一八五四年', place: '上海', language: '漢文', intro: '在華各新教差會聯合組成委辦委員會合譯的文言聖經,由麥都思、理雅各等通曉漢學的宣教士主筆,並延請中國文士潤飾,文辭典雅暢達。譯本因「神」「上帝」譯名之爭而生分歧,然其雅馴文體影響深遠,是十九世紀流傳最廣的文言聖經之一。', link: '/scripture' },
          { title_zh: '郭實臘譯本', title_orig: '救世主耶穌新遺詔書（郭實臘）', author: '郭實臘（麥都思合作修訂）', era: '1839–1840', place: '新加坡／巴達維亞', language: '中文', intro: '郭實臘修訂麥都思新約而成的譯本，輾轉為太平天國採用翻印為《欽定前遺詔聖書》底本。譯本流入民間掀起天國風暴，譯經史與中國近代史意外交纏的一部書。' },
          { title_zh: '裨治文譯本', title_orig: '裨治文-克陛存譯本', author: '裨治文與克陛存', era: '1859–1862', place: '上海', language: '中文', intro: '美國宣教士裨治文與克陛存以直譯為尚的深文理譯本，「神」版立場的代表譯作。委辦譯本之外的另一系，美系宣教譯經傳統的主要成果。' },
          { title_zh: '北京官話新約譯本', title_orig: '北京官話譯本', author: '北京翻譯委員會（丁韙良、施約瑟等）', era: '1872', place: '北京', language: '中文（官話）', intro: '英美各會在京宣教士合譯的官話新約，開白話譯經之先河而風行北方。和合本之前最通行的官話聖經，白話文運動前夜的語言實驗場。' },
          { title_zh: '施約瑟官話舊約譯本', title_orig: '施約瑟官話舊約', author: '施約瑟', era: '1874', place: '北京', language: '中文（官話）', intro: '猶太裔主教施約瑟以希伯來原文獨力譯成的官話舊約，後癱瘓仍以雙指打字完成淺文理全書。譯經史最傳奇的個人成就，「二指聖經」的前篇。' },
          { title_zh: '楊格非淺文理譯本', title_orig: '楊格非淺文理新約', author: '楊格非', era: '1885', place: '漢口', language: '中文（淺文理）', intro: '華中宣道半世紀的楊格非以淺近文言譯成新約，兼顧士人可讀與庶民可解。文白之間的譯經探路者，和合本文體抉擇的先行實驗。' },
          { title_zh: '固裡東正教官話新約', title_orig: '固里譯本（東正教新約）', author: '固裡（卡爾波夫）', era: '1864', place: '北京', language: '中文（官話）', intro: '俄國東正教北京傳道團修士大司祭固裡譯成的官話新約，術語自成一系（如「福音」作「福音經」）。漢語東正教傳統的譯經孤本，新教天主教之外的第三譯脈。' },
          { title_zh: '南京官話譯本', title_orig: '南京官話新約（麥都思-施敦力）', author: '麥都思與施敦力', era: '1857', place: '上海刊行', language: '中文（南京官話）', intro: '麥都思與施敦力把委辦文理新約改寫為南京官話的譯本，為第一部官話新約。文言獨尊時代的白話先聲，官話譯經系譜的起點。' },
          { title_zh: '廈門白話字聖經', title_orig: 'Lán ê Kiù-chú Iâ-so͘ Ki-tok ê Sin-iok', author: '廈門宣教士團（打馬字等）', era: '1873（新約）／1884（舊約）', place: '廈門', language: '閩南語（白話字）', intro: '以羅馬字拼寫廈門音的閩南語聖經，文盲婦孺數週可學會誦讀。白話字文化圈的聖典，臺灣長老教會百年信仰語言的源頭，母語聖經的東亞典範。' }
        
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
          { title_zh: '莫法特茨瓦納文聖經', title_orig: 'The Holy Bible (Setswana)', author: '莫法特(Robert Moffat)', era: '全本 1857', place: '南非庫魯曼', language: '茨瓦納文', intro: '倫敦傳道會宣教士莫法特(Robert Moffat)長年駐守南非庫魯曼(Kuruman)宣教站，為茨瓦納人建立文字並逐卷迻譯，於一八五七年完成全本聖經。這是非洲本土語言中第一部譯齊的整本聖經，他更親自設印刷機刊行。莫法特亦是探險家李文斯頓(David Livingstone)的岳父與同工，其譯經奠定了南部非洲教會以母語誦讀聖言的傳統。' },
          { title_zh: '明治元譯聖書', title_orig: '明治元訳聖書', author: '翻譯委員社中（赫本、布朗與奧野昌綱等）', era: '1880–1887', place: '橫濱', language: '日文', intro: '赫本、布朗與日本助手奧野昌綱等合譯的首部日語全本聖經，文語典雅而深植日本文學。「元譯」確立日語聖經語彙，內村鑑三世代的信仰母語。' },
          { title_zh: '羅斯韓文新約', title_orig: '예수셩교젼셔（Ross Version）', author: '羅約翰與徐相崙、白鴻俊等', era: '1887', place: '瀋陽', language: '韓文', intro: '蘇格蘭宣教士羅約翰與朝鮮商人信徒在滿洲合譯的首部韓文新約，全用諺文以及庶民。譯本先於宣教士入境，信徒自行攜書歸國建立教會，「聖經先行」宣教史的著名個案。' },
          { title_zh: '萊德克馬來文聖經', title_orig: 'Alkitab Leydekker', author: '萊德克', era: '1733', place: '巴達維亞', language: '馬來文', intro: '荷蘭牧師萊德克譯成的馬來語全本聖經，為東南亞語言首部全譯本。馬來書面語發展的重要一環，印尼譯經傳統的十八世紀源頭。' },
          { title_zh: '坦米爾聖經', title_orig: 'Tamil Bible (Tranquebar)', author: '齊根巴爾格與法布里修斯', era: '1714–1796', place: '特蘭克巴', language: '坦米爾文', intro: '齊根巴爾格首譯新約、詩人譯者法布里修斯重譯全書的坦米爾聖經，後者被譽為「黃金譯本」。印度語言第一部印刷新約，南亞譯經傳統的開山。' },
          { title_zh: '大溪地聖經', title_orig: 'Te Bibilia Mo\'a (Nott)', author: '亨利‧諾特（波馬雷二世襄助）', era: '1838', place: '大溪地', language: '大溪地文', intro: '泥瓦匠宣教士諾特歷四十年譯成的大溪地語聖經，國王波馬雷二世親自參校。玻里尼西亞首部全本聖經，南太平洋書面語文化的第一書。' },
          { title_zh: '毛利語聖經', title_orig: 'Te Paipera Tapu', author: '威廉斯家族與毛利助手團', era: '1868（全本）', place: '派希亞／倫敦', language: '毛利文', intro: '威廉斯家族與毛利同工歷數十年譯成的毛利語全本聖經，其語彙深植毛利演說傳統。毛利識字率一度冠絕世界的推手，紐西蘭雙文化史的核心文本。' },
          { title_zh: '夏威夷語聖經', title_orig: 'Ka Baibala Hemolele', author: '賓漢等美部會宣教士與夏威夷學者', era: '1839', place: '檀香山', language: '夏威夷文', intro: '美部會與夏威夷學者合譯的夏威夷語聖經，配合王國全民教育使識字率躍居世界前列。夏威夷語復振運動今日仍賴其語料，太平洋譯經的燈塔。' },
          { title_zh: '薩摩亞語聖經', title_orig: 'O le Tusi Paia', author: '倫敦會宣教士與薩摩亞助手', era: '1855（全本）', place: '薩摩亞', language: '薩摩亞文', intro: '倫敦會與薩摩亞同工譯成的全本聖經，正字法確立薩摩亞書面語。「每屋一經」的島嶼由此得名，薩摩亞語文與教會文化的根基。' },
          { title_zh: '克勞瑟約魯巴語聖經', title_orig: 'Bibeli Mimọ (Yoruba)', author: '塞繆爾‧阿賈伊‧克勞瑟', era: '1862–1884', place: '拉哥斯／阿貝奧庫塔', language: '約魯巴文', intro: '獲救奴隸出身的克勞瑟主教主譯的約魯巴語聖經，聲調標記系統為非洲語言學立範。非洲人主譯母語聖經的第一例，約魯巴書面文化的奠基。' },
          { title_zh: '馬達加斯加語聖經', title_orig: 'Ny Baiboly Masina', author: '倫敦會宣教士與馬拉加西學者', era: '1835', place: '塔那那利佛', language: '馬拉加西文', intro: '迫害令下宣教士撤離前夕趕印完成的馬拉加西語聖經，地下信徒藏書山洞傳抄廿五年。「無宣教士的教會」賴此存續且倍增，譯本先於自由的殉道聖經。' },
          { title_zh: '阿布‧魯米阿姆哈拉語聖經', title_orig: 'Abu Rumi Amharic Bible', author: '阿布‧魯米（阿斯萊翻譯記錄）', era: '1810 年代譯成（1840 刊）', place: '開羅', language: '阿姆哈拉文', intro: '衣索比亞學者阿布‧魯米在開羅十年口譯筆錄而成的阿姆哈拉語全本聖經，聖經公會購稿刊行。非洲學者獨力完成的譯經巨業，現代衣索比亞語聖經的祖本。' },
          { title_zh: '克里語音節文字聖經', title_orig: 'Cree Syllabic Bible', author: '詹姆斯‧埃文斯創字、梅森等譯成', era: '1861–1862', place: '魯珀特地／倫敦', language: '克里文（音節文字）', intro: '衛理宣教士埃文斯自創音節文字使克里人「一日識字」，聖經全本隨之譯印。原住民文字發明與譯經合一的經典案例，加拿大原住民音節文字系統沿用至今。' },
          { title_zh: '格陵蘭語新約', title_orig: 'Testamente Nutak', author: '埃格德父子與摩拉維亞同工', era: '1766', place: '哥本哈根刊行', language: '格陵蘭文', intro: '「格陵蘭使徒」埃格德父子譯成的因紐特語新約，為極地語言譯經之先。北極圈的第一部聖經，因紐特書面語的起點文獻。' },
          { title_zh: '拉布拉多因紐特語新約', title_orig: 'Labrador Inuktitut New Testament', author: '摩拉維亞弟兄會宣教士', era: '1826', place: '拉布拉多／倫敦刊行', language: '因紐特文', intro: '摩拉維亞宣教士在拉布拉多冰岸譯成的因紐特語新約，聖經公會早期贊助的名案。極北小社群的母語聖經，摩拉維亞全球譯經網的代表果實。' },
          { title_zh: '阿留申語福音書', title_orig: 'Aleut Gospel of St Matthew', author: '英諾肯提（韋尼阿米諾夫）與雅各‧內茨維托夫', era: '1840 年代', place: '阿拉斯加', language: '阿留申文', intro: '英諾肯提與克里奧混血司祭內茨維托夫創制字母並譯成的阿留申語福音書。正教宣教語言學的代表成果，阿拉斯加原住民文字文化的開端。' },
          { title_zh: '凡戴克阿拉伯語聖經', title_orig: 'Smith–Van Dyck Arabic Bible', author: '史密斯與凡戴克（布斯塔尼、雅茲吉襄助）', era: '1865', place: '貝魯特', language: '阿拉伯文', intro: '美國宣教士與黎巴嫩文豪布斯塔尼、雅茲吉合作譯成的阿拉伯語聖經，文體典雅而通行至今。阿拉伯文藝復興的推手文本，今日阿語世界最通行的聖經。' },
          { title_zh: '阿里‧烏夫基土耳其語聖經', title_orig: 'Kitabı Mukaddes (Ali Ufkî)', author: '阿里‧烏夫基（沃伊切赫‧博博夫斯基）', era: '1662–1666 譯成', place: '伊斯坦堡', language: '鄂圖曼土耳其文', intro: '波蘭出身、被擄入鄂圖曼宮廷的音樂家博博夫斯基（阿里‧烏夫基）譯成的土耳其語聖經，二百年後刊行仍為標準。跨越基督教與伊斯蘭兩個世界的譯者傳奇。' }
        
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
          { title_zh: '希臘文新約校勘原則', title_orig: 'Novum Testamentum Graece', author: '格里斯巴赫 (Johann Jakob Griesbach)', era: '一七七四至一七七五年', place: '哈勒‧耶拿', language: '希臘文', intro: '格里斯巴赫的希臘文新約,首次大膽偏離公認本,依抄本系統將見證歸為亞歷山大、西方、拜占庭三大文本類型,並訂立十五條校勘準則。他確立以抄本系譜權衡異文的方法論,是近代以前最具影響的校勘本,直接啟導了十九世紀以降的批判性新約版本。', link: '/scripture' },
          { title_zh: '本格爾希臘文新約', title_orig: 'Novum Testamentum Graecum (Bengel)', author: '約翰‧阿爾布雷希特‧本格爾', era: '1734', place: '圖賓根', language: '希臘文', intro: '敬虔派學者本格爾的希臘文新約，首創異文分級與「較難讀法為優」原則。「勿把難處輕輕放過」的校勘倫理立此存照，近代經文評鑑學的方法奠基人。' },
          { title_zh: '威茨坦希臘文新約', title_orig: 'Novum Testamentum Graecum (Wettstein)', author: '約翰‧雅各‧威茨坦', era: '1751–1752', place: '阿姆斯特丹', language: '希臘文', intro: '威茨坦畢生蒐羅的異文與希臘拉丁猶太平行文獻大注，抄本編號系統肇端於此。因異端嫌疑流亡而成書，新約語文學的百科式豐碑。' },
          { title_zh: '格里斯巴赫希臘文新約', title_orig: 'Novum Testamentum Graece (Griesbach)', author: '約翰‧雅各‧格里斯巴赫', era: '1775–1807', place: '耶拿', language: '希臘文', intro: '格里斯巴赫首創抄本家族分類並敢於更動公認經文。共觀福音「格里斯巴赫假說」亦其手筆，經文評鑑由蒐集轉入系統的樞紐學者。' },
          { title_zh: '拉赫曼希臘文新約', title_orig: 'Novum Testamentum Graece (Lachmann)', author: '卡爾‧拉赫曼', era: '1831', place: '柏林', language: '希臘文', intro: '古典語文學家拉赫曼首度全然拋開「公認經文」、單依古抄本重建文本。經文評鑑學的獨立宣言，其方法論革命影響一切後續校勘。' },
          { title_zh: '蒂申多夫希臘文新約第八版', title_orig: 'Editio octava critica maior', author: '康斯坦丁‧馮‧蒂申多夫', era: '1869–1872', place: '萊比錫', language: '希臘文', intro: '發現西奈抄本的蒂申多夫集畢生抄本工作於第八大校勘版，異文檔案至今無可替代。抄本獵人與校勘家的世紀成就，西奈抄本的學術結晶。' },
          { title_zh: '特雷格勒斯希臘文新約', title_orig: 'Greek New Testament (Tregelles)', author: '塞繆爾‧特雷格勒斯', era: '1857–1872', place: '普利茅斯', language: '希臘文', intro: '自學成家的特雷格勒斯獨力核對諸大抄本編成的校勘本，虔敬與嚴謹並稱。與拉赫曼蒂申多夫並列十九世紀三大獨立校勘，威斯科特-霍特的直接前驅。' },
          { title_zh: '威斯科特-霍特希臘文新約', title_orig: 'The New Testament in the Original Greek', author: '威斯科特與霍特', era: '1881', place: '劍橋', language: '希臘文', intro: '劍橋雙傑廿八年合作的原文新約與方法導論，確立「中性文本」理論並終結公認經文時代。現代新約校勘本的直系祖本，其問世與英文修訂本同年震動世界。' },
          { title_zh: '米爾希臘文新約', title_orig: 'Novum Testamentum (John Mill)', author: '約翰‧米爾', era: '1707', place: '牛津', language: '希臘文', intro: '米爾窮卅年輯錄三萬異文的希臘文新約，刊後兩週辭世，異文之多引發「聖經可靠性」大論戰。經文評鑑學公共爭議的起點，惠特比與柯林斯論戰之源。' },
          { title_zh: '肯尼科特希伯來聖經異文大集', title_orig: 'Vetus Testamentum Hebraicum cum variis lectionibus', author: '班傑明‧肯尼科特', era: '1776–1780', place: '牛津', language: '希伯來文', intro: '肯尼科特動員全歐核對六百餘部希伯來抄本的異文總集，募款規模空前。舊約經文評鑑的第一次大普查，馬所拉文本穩定性的意外證人。' },
          { title_zh: '七十士譯本異文大集', title_orig: 'Vetus Testamentum Graecum cum variis lectionibus', author: '霍姆斯與帕森斯', era: '1798–1827', place: '牛津', language: '希臘文', intro: '牛津學者霍姆斯與帕森斯集三百餘抄本的七十士異文五巨冊。七十士研究的第一座大檔案庫，哥廷根七十士計畫的十九世紀前身。' },
          { title_zh: '英文修訂譯本', title_orig: 'The Revised Version', author: '英美修訂委員會', era: '1881–1885', place: '劍橋／牛津', language: '英文', intro: '依新校勘成果全面修訂欽定本的英譯，新約首日售出百萬部。三百年欽定本權威首度鬆動的歷史事件，現代英譯世系的開閘之作。' },
          { title_zh: '克萊孟定本武加大', title_orig: 'Vulgata Sixto-Clementina', author: '教廷修訂委員會（西斯篤五世－克萊孟八世）', era: '1592', place: '羅馬', language: '拉丁文', intro: '特倫託宣告武加大為權威後教廷刊定的標準本，西斯篤倉促版回收重修而成克萊孟定本。天主教官定聖經文本三百五十年，教會權威與文本學角力的紀念碑。' },
          { title_zh: '第二拉比聖經', title_orig: 'Mikraot Gedolot (Ben Hayyim)', author: '雅各‧本‧海因（邦貝格印行）', era: '1524–1525', place: '威尼斯', language: '希伯來文', intro: '基督徒印刷商邦貝格延聘猶太學者本‧海因校訂的拉比聖經，馬所拉文本自此有了印刷定本。此後四百年新舊教譯經共同的希伯來底本，猶太-基督出版合作的里程碑。' },
          { title_zh: '撒瑪利亞五經西傳刊本', title_orig: 'Samaritan Pentateuch (Paris Polyglot)', author: '德拉瓦萊購得抄本／莫里努斯刊佈', era: '1616 購得，1645 刊', place: '大馬士革／巴黎', language: '撒瑪利亞希伯來文', intro: '旅行家德拉瓦萊自大馬士革購得撒瑪利亞五經，巴黎多語聖經首刊震動學界。馬所拉之外的獨立文本傳統重見天日，舊約文本史觀的第一次擴容。' },
          { title_zh: '別西大首刊本', title_orig: 'Peshitta editio princeps (Widmanstetter)', author: '維德曼施泰特與摩西‧馬爾丁', era: '1555', place: '維也納', language: '敘利亞文', intro: '帝國顧問維德曼施泰特與敘利亞教會使者摩西合作刊印的敘利亞文新約首版。歐洲敘利亞學的開幕之作，東方教會與西方學術的第一次出版握手。' },
          { title_zh: '庫雷頓古敘利亞福音刊本', title_orig: 'Curetonian Syriac Gospels', author: '威廉‧庫雷頓刊佈', era: '1858', place: '倫敦', language: '敘利亞文', intro: '自埃及泥谷修道院購得的古敘利亞福音抄本經庫雷頓刊佈，證明別西大之前另有更古譯層。敘利亞譯本史的改寫文獻，福音文本早期形態的重要證人。' },
          { title_zh: '西奈古敘利亞福音重寫本', title_orig: 'Sinaitic Syriac Palimpsest', author: '艾格妮絲‧史密斯‧劉易斯發現', era: '1892 發現（4–5 世紀抄本）', place: '西奈聖凱瑟琳修道院', language: '敘利亞文', intro: '自學東方語的蘇格蘭孿生姊妹於西奈發現的古敘利亞福音重寫本，層下文本早於別西大。女性學者改寫文本史的著名一幕，十九世紀抄本大發現的壓卷。' },
          { title_zh: '奧斯坎亞美尼亞聖經首刊本', title_orig: 'Oskan Bible', author: '奧斯坎‧葉裡溫齊', era: '1666', place: '阿姆斯特丹', language: '亞美尼亞文', intro: '主教奧斯坎流轉歐洲於阿姆斯特丹印成的首部亞美尼亞文印刷聖經，附插圖精美。離散民族以印刷續命經典的壯舉，亞美尼亞書籍史的巔峰。' },
          { title_zh: '莫斯科喬治亞語聖經', title_orig: 'Moscow Georgian Bible (Bakar Bible)', author: '巴卡爾王子主持', era: '1743', place: '莫斯科', language: '喬治亞文', intro: '流亡莫斯科的喬治亞王子巴卡爾主持刊印的首部喬治亞文全本印刷聖經。高加索古老譯本的印刷定本，流亡宮廷的文化救亡工程。' },
          { title_zh: '威爾金斯科普特新約刊本', title_orig: 'Novum Testamentum Aegyptium (Wilkins)', author: '大衛‧威爾金斯刊佈', era: '1716', place: '牛津', language: '科普特文（波海利）', intro: '威爾金斯刊佈的首部科普特文新約印本，開歐洲科普特學之端。埃及古譯本進入西方校勘視野的起點，東方譯本徵引史的一環。' },
          { title_zh: '吉茲文詩篇首刊本', title_orig: 'Psalterium Aethiopicum (Potken)', author: '波特肯刊行', era: '1513', place: '羅馬', language: '吉茲文', intro: '德國教士波特肯在羅馬刊印的吉茲文詩篇，為衣索比亞文字首度付梓，誤稱其語為「迦勒底語」。歐洲衣索比亞學的搖籃印本，非洲文字印刷史的第一頁。' }
        
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
          { title_zh: '慈運理書信', title_orig: 'Zwinglis Briefwechsel', author: '烏爾里希‧慈運理 (Huldrych Zwingli)', era: '一五一〇年代至一五三一年', place: '蘇黎世', language: '拉丁文‧德文', intro: '蘇黎世改革家慈運理與人文學者、同道及各方政要往來的書信。內容涉及聖餐之爭、與路德的歧見、瑞士諸邦的宗教與政局。書信兼具人文素養與改革熱忱,既見其與伊拉斯謨等學人的淵源,也記錄了瑞士德語區改革的曲折,是研究改革陣營內部分合的重要見證。' },
          { title_zh: '墨蘭頓書信集', title_orig: 'Epistolae Philippi Melanchthonis', author: '菲利普‧墨蘭頓', era: '1518–1560', place: '維滕堡', language: '拉丁文', intro: '「德意志之師」墨蘭頓存世書信近萬封，調停路德宗內外紛爭、起草信條、與全歐學界通問，是宗教改革最大的書信網絡。其信兼具人文學者的優雅與調和者的憂勞，為改革運動的日常肌理留下最完整的檔案。' },
          { title_zh: '貝扎書信集', title_orig: 'Correspondance de Théodore de Bèze', author: '泰奧多爾‧貝扎', era: '1548–1605', place: '日內瓦', language: '拉丁文／法文', intro: '加爾文接班人貝扎主持日內瓦近半世紀的往來書信，指導法蘭西胡格諾教會度過宗教戰爭與聖巴多羅買之夜，兼與各國改革宗領袖協調。現代校刊本達數十冊，是國際加爾文主義成形的第一手網絡檔案。' },
          { title_zh: '布塞爾書信集', title_orig: 'Correspondance de Martin Bucer', author: '馬丁‧布塞爾', era: '1524–1551', place: '史特拉斯堡／劍橋', language: '拉丁文／德文', intro: '史特拉斯堡改革家布塞爾以書信斡旋於路德與茨溫利之間，力促聖餐和解，晚年流亡英格蘭續以書信襄助克蘭麥改革。其信是宗教改革「合一路線」的完整紀錄，教會合一運動屢屢回望的先例。' },
          { title_zh: '布林格書信集', title_orig: 'Briefwechsel Heinrich Bullingers', author: '海因裡希‧布林格', era: '1531–1575', place: '蘇黎世', language: '拉丁文／德文', intro: '茨溫利繼任者布林格存世書信一萬二千封，為十六世紀歐洲之最，通信對象自英格蘭女王至匈牙利牧者。蘇黎世由此成為改革宗世界的資訊樞紐，這批書信是宗教改革國際史無可替代的底層檔案。' },
          { title_zh: '諾克斯書信集', title_orig: 'Letters of John Knox', author: '約翰‧諾克斯', era: '1548–1572', place: '日內瓦／愛丁堡', language: '英文', intro: '蘇格蘭改革家諾克斯的書信，自划船奴生涯倖存後致信徒的牧函、與母后攝政的對峙文書，至寫給岳母包斯夫人的靈修私信，剛烈與柔情並存。這批信是蘇格蘭宗教改革的私人卷宗，諾克斯人格的雙面鏡。' },
          { title_zh: '克蘭麥書信集', title_orig: 'Letters of Thomas Cranmer', author: '託馬斯‧克蘭麥', era: '1533–1556', place: '坎特伯裡', language: '英文／拉丁文', intro: '坎特伯裡大主教克蘭麥的書信，邀布塞爾、維米利等歐陸學者赴英共建改革，並謀劃普世新教信條會議。至其繫獄反覆與終局的信件，呈現公禱書之父在王權與良心夾縫中的全部掙扎。' },
          { title_zh: '廷代爾獄中書信', title_orig: 'Letter from Vilvoorde Prison', author: '威廉‧廷代爾', era: '1535', place: '維爾福德堡（布拉班特）', language: '拉丁文', intro: '英譯聖經先驅廷代爾就義前自維爾福德獄中致典獄官的短信，只求一頂暖帽、一支蠟燭與他的希伯來文聖經、文法與辭典，「好在黑暗中繼續工作」。寥寥數行成為譯經者堅忍的千古見證，英語聖經史最動人的文物。' },
          { title_zh: '門諾‧西門斯書信集', title_orig: 'Brieven van Menno Simons', author: '門諾‧西門斯', era: '1536–1561', place: '低地國／荷爾斯泰因', language: '荷蘭文', intro: '和平再洗禮派領袖門諾亡命二十五年間致散居會眾的牧函，安慰受迫姊妹、調解教會紛爭、申辯非暴力立場。頭懸賞格而書信不輟，這批信件把瀕滅的再洗禮運動凝聚為延續至今的門諾會傳統。' },
          { title_zh: '殉道者之鏡獄中書信', title_orig: 'Martelaersspiegel: gevangenisbrieven', author: '荷蘭再洗禮派殉道者群', era: '1535–1592（1660 輯刊）', place: '低地國', language: '荷蘭文', intro: '《殉道者之鏡》輯錄的再洗禮派死囚書信：織工、主婦、少女在火刑前夕致兒女與會眾的訣別信，字句樸拙而信念如鐵。平民殉道者的親筆聲音在教會史上極為罕見，這批信是草根信仰史的最強文獻。' },
          { title_zh: '瑪格麗特與布里索內往來書信', title_orig: 'Correspondance de Marguerite d\'Angoulême et Guillaume Briçonnet', author: '納瓦拉的瑪格麗特／紀堯姆‧布里索內', era: '1521–1524', place: '莫城／法蘭西宮廷', language: '法文', intro: '法王之妹瑪格麗特與莫城主教布里索內的靈修通信百餘封，主教以密契言語引導公主，莫城改革圈的福音思想賴此滲入宮廷。這批信是法蘭西宗教改革前夜的溫床文獻，兼為女性靈修書寫的傑作。' },
          { title_zh: '珍‧格雷獄中書信', title_orig: 'Letters and Prayers of Lady Jane Grey', author: '珍‧格雷', era: '1553–1554', place: '倫敦塔', language: '英文', intro: '「九日女王」珍‧格雷就刑前的書信與禱文：致父親的寬恕、致妹妹凱瑟琳附於希臘文新約上的遺言、與費肯漢神父的辯道紀錄。十六歲少女以學識與信仰直面斷頭臺，這批文字是改革時代最清亮的殉道之聲。' },
          { title_zh: '牛津殉道者獄中書信', title_orig: 'Prison Letters of Ridley and Latimer', author: '裡德利與拉蒂默', era: '1554–1555', place: '牛津博卡多獄', language: '英文', intro: '瑪麗女王治下繫獄牛津的主教裡德利與拉蒂默彼此打氣、致信同道的獄中書信，拉蒂默名言「我們今日要點燃一支蠟燭，靠神恩典永不熄滅」即出火刑柱上。這批信經福克斯《殉道者之書》傳世，是英格蘭新教認同的奠基文本。' },
          { title_zh: '薩多雷託與加爾文往來書函', title_orig: 'Sadoleto\'s Letter and Calvin\'s Reply', author: '雅各‧薩多雷託／約翰‧加爾文', era: '1539', place: '里昂／史特拉斯堡', language: '拉丁文', intro: '人文主義樞機薩多雷託致函日內瓦勸其重歸羅馬，流亡中的加爾文受託覆函，六日寫就的答書申明改革非分裂、乃回歸古教會。攻守雙方俱屬一流之筆，這組往來被譽為新舊兩造最高水平的一次交鋒。' },
          { title_zh: '奧科蘭帕迪烏斯書信集', title_orig: 'Briefe und Akten zum Leben Oekolampads', author: '約翰內斯‧奧科蘭帕迪烏斯', era: '1522–1531', place: '巴塞爾', language: '拉丁文', intro: '巴塞爾改革家、希臘文教父學者奧科蘭帕迪烏斯的書信，記其推動城市改革、參與馬堡會談並首倡教會自主懲戒制。其信學養醇厚，是上萊茵人文主義與宗教改革交融的代表檔案。' },
          { title_zh: '維米利書信集', title_orig: 'Epistolae Petri Martyris Vermilii', author: '彼得‧馬蒂爾‧維米利', era: '1542–1562', place: '史特拉斯堡／牛津／蘇黎世', language: '拉丁文', intro: '義大利流亡改革家維米利的書信，輾轉史特拉斯堡、牛津、蘇黎世而通問全歐，為英格蘭聖餐神學與歸正教義的定型出力至鉅。其信見證義大利福音運動菁英流亡後如何反哺北方改革，跨國新教網絡的典型個案。' },
          { title_zh: '拉斯科書信集', title_orig: 'Epistolae Iohannis a Lasco', author: '約翰‧拉斯科', era: '1540–1560', place: '埃姆登／倫敦／波蘭', language: '拉丁文', intro: '波蘭貴族改革家拉斯科的書信，自弗里斯蘭到倫敦流亡者教會再返波蘭推動改革，與全歐同道往還。他為伊拉斯謨晚年摯友並購其藏書，其信是東歐宗教改革與流亡教會制度史的樞紐文獻。' },
          { title_zh: '朱里厄致法蘭西受迫信徒牧函', title_orig: 'Lettres pastorales adressées aux fidèles de France', author: '皮埃爾‧朱里厄', era: '1686–1689', place: '鹿特丹', language: '法文', intro: '南特敕令廢除後，流亡牧師朱里厄每兩週自荷蘭秘密寄入法國的牧函，堅固被迫改宗的胡格諾信徒，兼發展反暴政的政治神學。這批地下書信網絡是信仰抵抗與早期人權論述交會的重要文獻。' },
          { title_zh: '澤爾夫人書信與護教文', title_orig: 'Schriften und Briefe der Katharina Schütz Zell', author: '卡塔琳娜‧舒茲‧澤爾', era: '1524–1558', place: '史特拉斯堡', language: '德文', intro: '史特拉斯堡牧師之妻澤爾夫人以印行書信為受迫信徒辯護、慰問流亡婦女、駁斥責難教士婚姻者，自稱「教會之母」。她是宗教改革中著述最多的平信徒女性，其書信開創女性公開神學寫作的先例。' },
          { title_zh: '莫拉塔書信集', title_orig: 'Epistolae Olympiae Moratae', author: '奧林匹亞‧莫拉塔', era: '1550–1555', place: '費拉拉／德意志', language: '拉丁文／希臘文', intro: '費拉拉宮廷才女莫拉塔精希臘拉丁之學，因信奉新教流亡德意志，戰亂病困中致師友的書信與希臘文詩篇改寫傳世。廿九歲早逝的她被譽為文藝復興最有學問的女性之一，書信集是人文學識與福音信仰合一的絕唱。' },
          { title_zh: '福克斯書信集', title_orig: 'Epistles of George Fox', author: '喬治‧福克斯', era: '1652–1691', place: '英格蘭各地／獄中', language: '英文', intro: '貴格會創始人福克斯致「真理之友」的四百餘封公函，多成於八次繫獄之中，教導靜默聚會、拒誓與和平見證。這批書信是無聖職教派賴以維繫的組織血脈，友會傳統至今誦讀不輟。' },
          { title_zh: '瑪格麗特‧費爾書信', title_orig: 'Letters of Margaret Fell', author: '瑪格麗特‧費爾', era: '1652–1702', place: '斯沃斯莫爾莊園', language: '英文', intro: '「貴格會之母」費爾以斯沃斯莫爾莊園為運動樞紐，致各地聚會、國王與繫獄友人的書信數百封，並為婦女講道權著文辯護。她本人四度入獄而通信不絕，是十七世紀女性宗教領導力的最完整檔案。' }
        
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
          { title_zh: '近代宣教士家書', title_orig: 'Letters and Journals of Protestant Missionaries', author: '近代新教宣教士群 (馬禮遜、克理 William Carey 等)', era: '十八世紀末至十九世紀', place: '中國‧印度‧南洋', language: '英文', intro: '近代新教宣教運動興起後,馬禮遜、克理等宣教士寄回母會與家人的書信日誌。信中既述異域傳教的孤苦與成果,也記錄當地語言、社會與信仰,並向母會報告需用、籲求代禱。這些家書多經宣教刊物刊布,既維繫差會與工場的聯繫,也激勵後繼者,是近代新教海外宣教的鮮活記錄。' },
          { title_zh: '耶穌會日本年信', title_orig: 'Cartas que os padres e irmãos da Companhia de Jesus escreveram dos reynos de Japão', author: '在日耶穌會士群', era: '1549–1614', place: '日本諸口岸／歐洲刊行', language: '葡萄牙文／西班牙文', intro: '沙勿略以降在日耶穌會士的年度書信，報導大名改宗、信長秀吉政局與教會消長，於歐洲結集刊行而風靡一時。這批年信是歐洲認識日本的第一手管道，兼為日本戰國史與初期天主教史的核心史料。' },
          { title_zh: '諾佈雷加巴西書簡', title_orig: 'Cartas do Brasil (Manuel da Nóbrega)', author: '曼努埃爾‧達‧諾佈雷加', era: '1549–1570', place: '巴伊亞／聖保羅', language: '葡萄牙文', intro: '首任巴西耶穌會省會長諾佈雷加的書簡，記原住民宣教、抗議殖民者奴役印第安人、創建聖保羅學院的始末。他與安謝塔同為巴西教會與城市的奠基人，這批信是南美宣教與殖民倫理之爭最早的文獻。' },
          { title_zh: '範禮安巡閱使書信', title_orig: 'Cartas e escritos de Alessandro Valignano', author: '範禮安', era: '1573–1606', place: '果阿／澳門／日本', language: '義大利文／葡萄牙文', intro: '耶穌會東方巡閱使範禮安的書信與方策，定「文化適應」路線：令傳教士習日語華語、遣天正少年使節赴歐、命利瑪竇入華。其信是「適應主義」宣教戰略的決策檔案，東亞天主教史的總設計圖。' },
          { title_zh: '白晉與萊布尼茲往來書信', title_orig: 'Correspondance Bouvet–Leibniz', author: '白晉／萊布尼茲', era: '1697–1707', place: '北京／漢諾威', language: '法文／拉丁文', intro: '康熙宮廷的耶穌會士白晉與哲學家萊布尼茲的通信，白晉以易經卦象附會二進位算術，萊布尼茲驚為先聖遺數。這組書信是中西哲學數學相遇最奇特的一章，「索隱派」漢學與歐洲中國熱的思想現場。' },
          { title_zh: '巴多明致科學院書信', title_orig: 'Lettres du Père Parrenin à l\'Académie des Sciences', author: '巴多明', era: '1723–1740', place: '北京', language: '法文', intro: '耶穌會士巴多明自北京致法蘭西科學院的長信，報告滿文解剖學譯著、中國天文曆算與博物見聞，兼答杜赫德諸問。這批信展示在華傳教士充當中歐科學情報樞紐的角色，啟蒙時代「中國知識」的直接源頭。' },
          { title_zh: '樊恩書信與備忘錄', title_orig: 'Letters and Memoranda of Henry Venn', author: '亨利‧樊恩', era: '1841–1872', place: '倫敦英行教會總部', language: '英文', intro: '英行教會總幹事樊恩三十年間致各工場的書信與政策備忘錄，提出教會當「自養、自治、自傳」而宣教士應功成身退的原則，並力挺克勞瑟出任非洲主教。三自原則自此成為宣教學的中心語彙，這批文書即其原始出處。' },
          { title_zh: '賈德森夫婦緬甸書信', title_orig: 'Letters of Adoniram and Ann Judson', author: '賈德森與安‧賈德森', era: '1813–1850', place: '仰光／阿瓦', language: '英文', intro: '美國首批海外宣教士賈德森夫婦自緬甸的書信：緬文譯經、獄中之難與安氏營救丈夫的紀實，經教會報刊轉載而感動全美。安‧賈德森的書信尤開女性宣教書寫之先，是美國宣教運動的奠基敘事。' },
          { title_zh: '利文斯敦書信集', title_orig: 'Letters of David Livingstone', author: '大衛‧利文斯敦', era: '1841–1873', place: '南非／中非', language: '英文', intro: '宣教探險家利文斯敦自非洲腹地的書信，揭露東非奴隸貿易慘狀並籲以「商業與基督教」根除之，致《紐約先驅報》信末「願上天豐厚祝福凡助癒此世界瘡口者」鐫於其西敏寺墓。這批信改變了歐美對非洲的道德視線。' },
          { title_zh: '慕拉第書信', title_orig: 'Letters of Lottie Moon', author: '慕拉第', era: '1873–1912', place: '山東登州／平度', language: '英文', intro: '美南浸信會女宣教士慕拉第自山東的書信，力陳單身女性宣教的權利、抗議差會餉源枯竭，促成「聖誕奉獻」傳統。她饑荒中讓食至死，其書信塑造美南浸信會宣教文化逾百年，女性宣教史的豐碑。' },
          { title_zh: '英諾肯提阿拉斯加書信', title_orig: 'Письма Иннокентия (Вениаминова)', author: '英諾肯提（韋尼阿米諾夫）', era: '1824–1868', place: '阿拉斯加／雅庫次克', language: '俄文', intro: '「美洲宗徒」英諾肯提自阿留申群島與西伯利亞的書信，記創製阿留申文字、乘皮舟巡島施洗與譯經始末，後任莫斯科都主教猶力主宣教本地化。這批信是正教宣教學的實踐檔案，阿拉斯加正教傳統的源頭。' },
          { title_zh: '黃嗣永帛書', title_orig: '黃嗣永帛書', author: '黃嗣永', era: '1801', place: '朝鮮堤川', language: '漢文', intro: '辛酉教難中朝鮮教友黃嗣永以細字書於絹帛、擬送北京主教的萬言密信，詳述殉教實況並乞西方援手。帛書事洩而作者凌遲，原件輾轉入藏梵蒂岡。它是朝鮮天主教受難史最悲愴的文獻，東亞教案史的第一級史料。' },
          { title_zh: '齊根巴爾格書信與哈勒報告', title_orig: 'Hallesche Berichte (Ziegenbalg)', author: '巴多羅買‧齊根巴爾格', era: '1706–1719', place: '特蘭克巴（南印度）', language: '德文', intro: '更正教史上第一位海外宣教士齊根巴爾格自丹屬特蘭克巴的書信，經哈勒敬虔派刊為連續報告，記泰米爾文譯經、印刷與與婆羅門的對話。這批報告開新教宣教期刊之先河，兼為歐洲印度學的早期泉源。' },
          { title_zh: '克勞瑟主教書信', title_orig: 'Letters of Samuel Ajayi Crowther', author: '塞繆爾‧阿賈伊‧克勞瑟', era: '1841–1891', place: '尼日河流域／拉哥斯', language: '英文', intro: '約魯巴出身、獲救奴隸而成聖公會首位非洲主教的克勞瑟，其書信記尼日宣教、約魯巴文譯經與晚年遭歐洲少壯派奪權的屈辱。這批信是非洲人主導宣教的先聲及其挫敗的檔案，後殖民教會史的原點文獻。' },
          { title_zh: '摩拉維亞宣教書信集', title_orig: 'Briefe der Herrnhuter Missionare', author: '赫恩胡特宣教士群', era: '1732–1800 年代', place: '格陵蘭／加勒比／南非', language: '德文', intro: '摩拉維亞弟兄會自一七三二年遣使加勒比奴隸與格陵蘭因紐特人起，宣教士書信經《社區報導》流通各聚會。有宣教士自願賣身入蔗園與奴同工，這批信是近代新教宣教運動真正的第一批田野文獻。' },
          { title_zh: '坎皮恩勇敢宣言', title_orig: 'Campion\'s Brag (Challenge to the Privy Council)', author: '埃德蒙‧坎皮恩', era: '1580', place: '倫敦（地下）', language: '英文', intro: '耶穌會士坎皮恩潛回新教英格蘭前留下的自白書，聲明此行「唯關靈魂之事」、願與樞密院公開辯道，文氣慷慨如檄。宣言地下傳抄震動朝野，作者翌年車裂殉道，此文遂成英格蘭天主教地下時代的精神旗幟。' },
          { title_zh: '艾略特印第安宣教書信', title_orig: 'The Eliot Indian Tracts', author: '約翰‧艾略特', era: '1643–1671', place: '麻薩諸塞', language: '英文', intro: '「印第安人使徒」艾略特致英格蘭資助者的系列書信報告，記阿爾岡昆語譯經、「祈禱鎮」建設與原住民信徒問道實錄。這批小冊催生史上第一個宣教差會（新英格蘭福音傳播公司），北美宣教文獻的起點。' },
          { title_zh: '夸克海岸角書信', title_orig: 'Letters of Philip Quaque', author: '菲利普‧夸克', era: '1766–1811', place: '黃金海岸海岸角城堡', language: '英文', intro: '芳蒂族出身、英國聖公會首位非洲按立司鐸夸克，自黃金海岸奴隸堡壘任隨軍牧師五十年的書信，向倫敦報告在奴隸貿易陰影下傳道的孤絕與掙扎。這批信是十八世紀非洲聖職者處境的獨一無二自述。' },
          { title_zh: '馬廷書信集', title_orig: 'Letters of Henry Martyn', author: '亨利‧馬廷', era: '1806–1812', place: '印度／波斯', language: '英文', intro: '劍橋數學狀元出身的馬廷放棄前程赴印度，六年間譯成烏爾都語、波斯語新約，書信與日記記「願為神燃盡」的心志，三十一歲客死土耳其途中。其書信經傳記流傳，成為十九世紀宣教獻身精神的象徵文本。' }
        
        ]
      },
      {
        key: 'spiritual-letters',
        label: '靈修尺牘部',
        label_en: 'Spiritual Letters',
        desc: '近代天主教、新教與東正教的靈修指導書信——自依納爵、大德蘭至盧瑟福、提阿凡的屬靈通信傳統。',
        works: [
          { title_zh: '依納爵羅耀拉書信集', title_orig: 'Epistolae S. Ignatii de Loyola', author: '依納爵‧羅耀拉', era: '1524–1556', place: '羅馬', language: '西班牙文／拉丁文', intro: '耶穌會創始人依納爵存世書信近七千件，自羅馬總會所調度全球初創的傳教網絡，兼致貴婦與會士的靈修指導，「凡事為愈顯主榮」貫串其間。這批信是近代最大修會的創業檔案與依納爵靈修的實踐註腳。' },
          { title_zh: '鮑榮茂牧函與書信', title_orig: 'Epistolae S. Caroli Borromaei', author: '嘉祿‧鮑榮茂', era: '1560–1584', place: '米蘭', language: '義大利文／拉丁文', intro: '米蘭總主教鮑榮茂推行特倫託改革的牧函與書信，鉅細靡遺規劃堂區探訪、修院教育與瘟疫救濟，大疫中親率教士入疫區。這批文書是「特倫託模範主教」治理教區的完整樣本，近代天主教牧靈制度的原型。' },
          { title_zh: '文生‧德‧保祿書信集', title_orig: 'Correspondance de S. Vincent de Paul', author: '文生‧德‧保祿', era: '1607–1660', place: '巴黎', language: '法文', intro: '「慈善使徒」文生存世書信三萬餘件，調度遣使會與仁愛女修會的濟貧網絡：棄嬰、囚犯、戰災難民無所不及，事無鉅細皆以柔和之筆處置。這批信是十七世紀法國慈善革命的日常檔案，行動靈修的第一文獻。' },
          { title_zh: '露薏絲‧德‧馬裡亞克書信', title_orig: 'Lettres de Louise de Marillac', author: '露薏絲‧德‧馬裡亞克', era: '1626–1660', place: '巴黎', language: '法文', intro: '仁愛女修會共同創始人露薏絲致各地姊妹的書信，指導首個走出隱院、入戶服務窮人的女修會如何在街巷間持守祈禱。與文生的通信互為表裡，這批信是女性主動修會誕生的第一手紀錄。' },
          { title_zh: '大德蘭書信集', title_orig: 'Epistolario de Santa Teresa de Jesús', author: '亞維拉的德蘭', era: '1561–1582', place: '亞維拉／各創院途中', language: '西班牙文', intro: '大德蘭存世書信四百餘封，奔走十七座革新隱院之間，與國王、省會長、女兒們周旋院務、笑談病痛、密授祈禱。文筆機敏潑辣如其人，與其密契著作互補，呈現改革者兼密契者的血肉日常。' },
          { title_zh: '十字若望靈修書信', title_orig: 'Cartas de San Juan de la Cruz', author: '十字若望', era: '1581–1591', place: '格拉納達／塞哥維亞', language: '西班牙文', intro: '十字若望存世書信僅三十餘封，多致加爾默羅會修女，以「黑夜」與「一無所有」的語言撫慰靈魂的枯乾。臨終前遭會內整肅而信件多被焚毀，殘存者字字如金，是其密契神學最親切的註腳。' },
          { title_zh: '沙雷氏靈修書信集', title_orig: 'Lettres spirituelles de S. François de Sales', author: '方濟‧沙雷氏', era: '1593–1622', place: '安錫', language: '法文', intro: '沙雷氏存世書信數千封，大半為靈修指導，以溫柔的常識引導貴婦、修女與市民在各自身分中愛慕天主。《入德之門》即自書信增訂而成，這批信是「溫良靈修」傳統的活水源頭，靈修指導文學的典範。' },
          { title_zh: '尚達爾夫人書信集', title_orig: 'Lettres de S. Jeanne de Chantal', author: '尚達爾的珍妮', era: '1610–1641', place: '安錫／各聖母訪親會院', language: '法文', intro: '寡居男爵夫人尚達爾與沙雷氏共創聖母訪親會，晚年獨力治理八十餘院，致各院姊妹的書信教導「除了愛，別無所求」的單純祈禱。她親歷喪夫喪子喪師的暗夜，書信中的堅忍溫柔是女性靈修領導的高峰文獻。' },
          { title_zh: '芬乃倫靈修書信集', title_orig: 'Lettres spirituelles de Fénelon', author: '弗朗索瓦‧芬乃倫', era: '1689–1715', place: '凡爾賽／康佈雷', language: '法文', intro: '康佈雷總主教芬乃倫致宮廷男女的靈修書信，以外科醫生般的精準剖露自愛的千般偽裝，導向純粹之愛。他因護蓋恩夫人失寵遭貶而風骨不改，書信集跨越教派為衛斯理等新教領袖珍愛，法語靈修散文的絕品。' },
          { title_zh: '考薩德靈修書信', title_orig: 'Lettres spirituelles (L\'Abandon à la providence divine)', author: '讓-皮埃爾‧德‧考薩德', era: '1731–1740', place: '南錫', language: '法文', intro: '耶穌會士考薩德致訪親會修女的靈修書信，教導「當下時刻的聖事」——在每一刻的本分與際遇中領受天主。書信身後百餘年方輯刊為《委順於天主聖意》，遂成近代天主教靈修最受愛讀的小書之一。' },
          { title_zh: '貝魯爾書信集', title_orig: 'Correspondance du cardinal de Bérulle', author: '皮埃爾‧德‧貝魯爾', era: '1600–1629', place: '巴黎', language: '法文', intro: '法蘭西奧拉託利會創始人貝魯爾樞機的書信，推動「法蘭西學派」以降生聖言為中心的司鐸靈修，兼涉迎加爾默羅會入法與宮廷政務。這批信是十七世紀法國靈修復興的樞紐檔案，近代司鐸培育神學的源頭。' },
          { title_zh: '安傑莉克‧阿爾諾書信', title_orig: 'Lettres de la Mère Angélique Arnauld', author: '安傑莉克‧阿爾諾', era: '1620–1661', place: '波爾-羅亞爾修道院', language: '法文', intro: '波爾-羅亞爾女院長安傑莉克十一歲領院、十七歲厲行改革，其書信記修院革新與楊森派風暴中的堅持，「純潔如天使、驕傲如魔鬼」之譏正見其剛烈。這批信是法國十七世紀女性修道自主與良心抗爭的核心文獻。' },
          { title_zh: '盧瑟福書信集', title_orig: 'Letters of Samuel Rutherford', author: '塞繆爾‧盧瑟福', era: '1636–1661', place: '亞伯丁（流放中）／聖安德魯斯', language: '英文', intro: '蘇格蘭盟約派神學家盧瑟福被禁講道流放期間致教區信徒的書信，以熾烈的婚愛意象詠慕基督，「我浸在祂的愛中如魚在水」。司布真譽為「僅次於聖經最接近天堂的書」，清教靈修文學的最高峰。' },
          { title_zh: '牛頓心聲書信集', title_orig: 'Cardiphonia (John Newton)', author: '約翰‧牛頓', era: '1780', place: '倫敦／奧爾尼', language: '英文', intro: '前奴船船長、〈奇異恩典〉作者牛頓的靈修書信集《心聲》，以過來人的坦率輔導掙扎中的信徒，兼與威伯福斯通信堅其廢奴之志。書信平實如談心，是福音派靈修輔導文學的典範之作。' },
          { title_zh: '衛斯理書信集', title_orig: 'Letters of John Wesley', author: '約翰‧衛斯理', era: '1735–1791', place: '倫敦／巡迴各地', language: '英文', intro: '衛斯理五十年馬背生涯中的書信數千封，調度循道會社、指導平信徒傳道人、臨終前勉威伯福斯抗擊奴隸制「直到它消滅」。這批信是循道運動的組織神經與屬靈日誌，十八世紀福音復興的總檔案。' },
          { title_zh: '懷特腓書信集', title_orig: 'Letters of George Whitefield', author: '喬治‧懷特腓', era: '1734–1770', place: '英美兩洲巡迴', language: '英文', intro: '大覺醒佈道家懷特腓橫渡大西洋十三次，其書信聯絡英美復興網絡、與衛斯理論辯預定而終存弟兄之情。書信與其日誌同為跨大西洋福音主義成形的第一手文獻，佈道家內心世界的直接紀錄。' },
          { title_zh: '蘇珊娜‧衛斯理書信', title_orig: 'Letters of Susanna Wesley', author: '蘇珊娜‧衛斯理', era: '1709–1742', place: '愛普沃斯', language: '英文', intro: '衛斯理兄弟之母蘇珊娜致子女的書信，詳述其家庭教育法與每週逐一約談兒女的屬靈指導，約翰的「循規蹈矩」精神即其家學。這批信使她被尊為「循道會之母」，母職靈修與教育史的經典文獻。' },
          { title_zh: '施本爾神學諮議書信', title_orig: 'Theologische Bedencken', author: '菲利普‧雅各‧施本爾', era: '1700–1705 輯刊', place: '柏林', language: '德文', intro: '敬虔主義之父施本爾晚年輯刊的神學諮議書信四卷，answering 各地牧者信徒的良心疑難，把《敬虔願望》的綱領化為個案指導。這批信展示敬虔運動以書信網絡重塑德國教會的實際運作。' },
          { title_zh: '法蘭克哈勒書信', title_orig: 'Briefe August Hermann Franckes', author: '奧古斯特‧赫爾曼‧法蘭克', era: '1692–1727', place: '哈勒', language: '德文', intro: '哈勒敬虔派領袖法蘭克的書信，聯絡孤兒院、聖經社與丹麥-哈勒差會的全球網絡，通信遠及倫敦、莫斯科與特蘭克巴。這批信是敬虔主義「以機構改造世界」藍圖的檔案，近代新教慈善與宣教事業的母體。' },
          { title_zh: '麥克謙書信集', title_orig: 'Letters of Robert Murray M\'Cheyne', author: '羅伯特‧莫瑞‧麥克謙', era: '1836–1843', place: '丹地', language: '英文', intro: '蘇格蘭牧者麥克謙廿九歲早逝，其書信以聖潔的迫切勸勉會眾「按你所是的來到基督面前」，與其讀經曆並傳。身後《紀念集》風行英語世界，這批信是十九世紀福音派靈修的醇正標本。' },
          { title_zh: '提阿凡隱士書信集', title_orig: 'Письма Феофана Затворника', author: '隱士提阿凡', era: '1866–1894', place: '維沙隱修院', language: '俄文', intro: '俄國主教提阿凡退隱維沙廿八年，以書信指導各地信徒的祈禱與日常成聖，存世數千封，兼譯《慕善集》為俄文。這批信把愛索斯的心禱傳統化為平信徒可行的家常功課，十九世紀俄國靈修的最大寶庫。' },
          { title_zh: '奧普提納安博長老書信', title_orig: 'Письма Оптинского старца Амвросия', author: '奧普提納的安博', era: '1860–1891', place: '奧普提納隱修院', language: '俄文', intro: '奧普提納長老安博臥病斗室而日接百函，以諧語與洞見答俗人修士的萬般疑難，杜思妥也夫斯基筆下的佐西馬長老即以他為原型。這批書信是俄國長老制度（starchestvo）牧養智慧的第一手結集。' }
        
        ]
      },
      {
        key: 'scholars-controversy',
        label: '學者論戰與公共書信部',
        label_en: 'Scholarly and Public Letters',
        desc: '人文學者、科學家與公共人物以書信進行的信仰論辯——自伊拉斯謨、帕斯卡至紐曼、徐光啟。',
        works: [
          { title_zh: '伊拉斯謨書信集', title_orig: 'Opus Epistolarum Erasmi', author: '德西德里烏斯‧伊拉斯謨', era: '1484–1536', place: '鹿特丹／巴塞爾等地', language: '拉丁文', intro: '人文主義王者伊拉斯謨存世書信三千餘封，與君王、教宗、改革家與學者通問，儼然「文人共和國」的通訊總部。書信兼具文章典範與時代實錄，其於路德事件中的迂迴自持尤為思想史聚訟之點。' },
          { title_zh: '莫爾獄中書信', title_orig: 'Prison Letters of Thomas More', author: '託馬斯‧莫爾', era: '1534–1535', place: '倫敦塔', language: '英文', intro: '《烏託邦》作者莫爾拒認王上為教會元首而繫獄倫敦塔，以炭條寫給愛女瑪格麗特的訣別書信，論良心不可讓渡、笑談死亡如歸。這批信是良心自由史的最高文獻，「國王的好僕人，但首先是上帝的」之語千古迴響。' },
          { title_zh: '致外省人書', title_orig: 'Les Provinciales', author: '布萊茲‧帕斯卡', era: '1656–1657', place: '巴黎（匿名刊行）', language: '法文', intro: '帕斯卡為楊森派辯護、以假託外省友人的十八封公開信譏刺耶穌會決疑論，機鋒諧趣使全巴黎爭誦。書信雖被列入禁書而文體革命已成，法語散文自此有了現代的明快，宗教論戰文學的不朽傑作。' },
          { title_zh: '波舒哀與萊布尼茲教會合一通信', title_orig: 'Correspondance Bossuet–Leibniz sur la réunion des Églises', author: '波舒哀／萊布尼茲', era: '1691–1702', place: '巴黎／漢諾威', language: '法文／拉丁文', intro: '天主教雄辯家波舒哀與哲學家萊布尼茲就新舊教會復合的十年通信，逐條磋商特倫託教令的可讓與不可讓，終因「教會不可錯」一關而決裂。這組信是近代最認真的一次合一談判，普世運動的先驅檔案。' },
          { title_zh: '牛頓與本特利論神書信', title_orig: 'Four Letters from Sir Isaac Newton to Doctor Bentley', author: '以撒‧牛頓', era: '1692–1693', place: '劍橋', language: '英文', intro: '本特利據《原理》預備波義耳講座護教講道，牛頓覆以四函，申明重力體系「非出於盲目自然，必有智慧全能者設計」。這組書信是牛頓親筆的自然神學表白，科學革命與護教學聯盟的奠基文本。' },
          { title_zh: '伽利略致克莉絲蒂娜夫人書', title_orig: 'Lettera a Madama Cristina di Lorena', author: '伽利略‧伽利萊', era: '1615', place: '佛羅倫斯', language: '義大利文', intro: '伽利略致托斯卡納大公夫人的長信，申論「聖經教人如何上天堂，不教人天如何運行」，主張經文詮釋當讓位於已證明的自然真理。此信是科學與聖經詮釋關係的元典文本，四百年後仍是相關討論的起點。' },
          { title_zh: '紐曼致諾福克公爵書', title_orig: 'A Letter Addressed to the Duke of Norfolk', author: '約翰‧亨利‧紐曼', era: '1875', place: '伯明罕', language: '英文', intro: '格萊斯頓抨擊教宗不可錯誤論使天主教徒不能效忠國家，紐曼以致諾福克公爵公開信作答，界定不可錯誤的範圍並申言「先敬良心，後敬教宗」。此信是良心與教會權威關係最精緻的近代論述，梵二良心論的先聲。' },
          { title_zh: '果戈裡與友人書簡選', title_orig: 'Выбранные места из переписки с друзьями', author: '尼古拉‧果戈裡', era: '1847', place: '聖彼得堡刊行', language: '俄文', intro: '《死魂靈》作者果戈裡晚年刊行的書信選，宣講東正教的俄羅斯使命與靈魂改造，別林斯基以著名公開信痛斥其背叛啟蒙。這場書信論戰撕開俄國思想界「信仰與西化」的百年裂縫，杜思妥也夫斯基的問題意識由此而出。' },
          { title_zh: '徐光啟辨學章疏', title_orig: '辨學章疏', author: '徐光啟', era: '1616', place: '北京', language: '漢文', intro: '南京教案起，禮部侍郎徐光啟冒斥逐之險上疏為天主教辯，申言其教「事天愛人」可補儒佛、願以身家保西士無他，並倡「以西法佐曆」。此疏是中國士大夫公開衛教的第一文，儒家基督徒身分的奠基文獻。' },
          { title_zh: '拉瓦特爾與門德爾松論戰書信', title_orig: 'Lavater–Mendelssohn Briefwechsel', author: '約翰‧拉瓦特爾／摩西‧門德爾松', era: '1769–1770', place: '蘇黎世／柏林', language: '德文', intro: '蘇黎世牧師拉瓦特爾公開致函猶太哲學家門德爾松，迫其駁斥基督教或受洗；門德爾松以尊嚴與剋制答之，申明忠於祖傳信仰與理性寬容。這組書信震動啟蒙歐洲，是猶太解放與宗教寬容論爭的標誌事件。' },
          { title_zh: '施萊爾馬赫致呂克書信', title_orig: 'Sendschreiben an Lücke', author: '弗里德里希‧施萊爾馬赫', era: '1829', place: '柏林', language: '德文', intro: '施萊爾馬赫就《信仰論》再版致友人呂克的兩封公開信，自陳如何在近代科學與歷史批判中重述信仰，「難道基督教要與野蠻共存亡？」。此信是現代神學方法論的自我告白，理解其體系的最佳門徑。' },
          { title_zh: '朗塞與馬比雍論修道學問書信', title_orig: 'Controverse Rancé–Mabillon', author: '德‧朗塞／讓‧馬比雍', era: '1691–1693', place: '特拉普／巴黎', language: '法文', intro: '特拉普改革者朗塞主張修士當勞動苦修、不當治學，馬比雍以《修道研究論》溫文答辯，申明學問亦是祈禱。這場君子之爭界定了修道生活中苦行與學術的張力，本篤傳統自我理解的經典交鋒。' },
          { title_zh: '盧卡里斯書信集', title_orig: 'Epistolae Cyrilli Lucaris', author: '基裡羅斯‧盧卡里斯', era: '1602–1638', place: '君士坦丁堡／亞歷山卓', language: '希臘文／拉丁文', intro: '君士坦丁堡宗主教盧卡里斯與坎特伯裡、日內瓦及荷蘭改革宗的通信，贈英王亞歷山卓抄本、遣士子留學西歐，終遭鄂圖曼絞殺。其加爾文化的信仰告白掀起正教百年風暴，這批信是正教與新教相遇最深的一次檔案。' },
          { title_zh: '奧科姆書信', title_orig: 'Letters of Samson Occom', author: '參孫‧奧科姆', era: '1765–1792', place: '新英格蘭／倫敦', language: '英文', intro: '莫希幹族牧師奧科姆為印第安慈善學校赴英募款的書信，及發現善款轉建達特茅斯學院而背棄原住民後的抗議文字。他是北美原住民首位按立牧師與出版作家，書信是原住民基督徒自我發聲的開端文獻。' },
          { title_zh: '惠特利書信', title_orig: 'Letters of Phillis Wheatley', author: '菲利斯‧惠特利', era: '1770–1784', place: '波士頓', language: '英文', intro: '非洲出生、七歲被販為奴的詩人惠特利致奧科姆論自由的書信名篇：「每個人心中都植有對自由的原則性渴望」，以福音邏輯直刺蓄奴的偽善。她是美國第一位出版著作的非裔作者，書信是黑人神學傳統的晨星。' },
          { title_zh: '漢娜‧莫爾書信集', title_orig: 'Letters of Hannah More', author: '漢娜‧莫爾', era: '1774–1833', place: '布里斯托一帶', language: '英文', intro: '劇作家出身的福音派作家漢娜‧莫爾與克拉朋聯盟同道的往來書信，記其創辦貧童主日學校、以廉價道德小冊對抗激進思潮並襄助廢奴運動。她是十八世紀末英國最具影響力的女性公共知識分子，書信集是福音派社會改革網絡的女性視角檔案。' },
          { title_zh: '格里姆凱論兩性平等書信', title_orig: 'Letters on the Equality of the Sexes', author: '莎拉‧格里姆凱', era: '1838', place: '波士頓', language: '英文', intro: '南方蓄奴世家出身的貴格會廢奴者莎拉‧格里姆凱以聖經論證兩性受造平等的公開書信集，直言「男人握著聖經誤譯的權柄」。本書是以釋經爭女權的第一部系統著作，基督教女性主義的奠基文獻。' }
        
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
          { title_zh: '永恆之父', title_orig: 'Aeterni Patris', author: '教宗良十三世 (Leo PP. XIII)', era: '一八七九年', place: '羅馬', language: '拉丁文', intro: '教宗良十三世頒行的通諭,號召復興聖多瑪斯‧阿奎那的士林哲學,以為信仰與理性、教會與近代學術對話的根基。此諭開啟了新士林主義 (新多瑪斯主義) 的興盛,深刻塑造了二十世紀天主教的哲學與神學教育,是近代教廷回應理性主義與世俗思潮的關鍵文獻。', link: '/encyclicals' },
          { title_zh: '主啊，興起詔書', title_orig: 'Exsurge Domine', author: '教宗良十世', era: '1520', place: '羅馬', language: '拉丁文', intro: '良十世限令路德六十日內撤回四十一條主張的詔書，開篇引詩篇「主啊，興起，野豬闖入你的葡萄園」。路德當眾焚之於維滕堡城門，決裂遂不可逆。此詔是宗教改革分水嶺的官方文本，教廷面對改革的第一份正式回應。' },
          { title_zh: '御於至尊詔書', title_orig: 'Regnans in Excelsis', author: '教宗庇護五世', era: '1570', place: '羅馬', language: '拉丁文', intro: '庇護五世絕罰伊莉莎白一世並解除其臣民效忠的詔書，反使英格蘭天主教徒盡蒙叛國之嫌，迫害驟烈。此詔為教宗廢立權的最後一次實際行使，其適得其反的後果成為政教關係史的經典教訓。' },
          { title_zh: '禮儀之爭教廷禁約', title_orig: 'Ex illa die / Ex quo singulari', author: '克萊孟十一世／本篤十四世', era: '1715／1742', place: '羅馬', language: '拉丁文', intro: '教廷就中國禮儀之爭頒布的兩道禁約，斷禁教友祭祖祀孔，康熙批「以後不必西洋人在中國行教」，雍正繼以禁教。兩詔終結耶穌會適應路線，中西相遇的百年窗口就此關閉，直至一九三九年方告解除。' },
          { title_zh: '論法蘭西教士民事組織詔書', title_orig: 'Charitas (quae)', author: '教宗庇護六世', era: '1791', place: '羅馬', language: '拉丁文', intro: '庇護六世譴責法國大革命《教士民事組織法》及宣誓教士的詔書，斷其祝聖為「褻聖」，法國教會遂裂為宣誓與拒誓兩半。此詔開啟教廷與革命現代性的百年對峙，亦預告教宗本人被擄客死的命運。' },
          { title_zh: '汝等驚異通諭', title_orig: 'Mirari Vos', author: '教宗額我略十六世', era: '1832', place: '羅馬', language: '拉丁文', intro: '額我略十六世駁斥拉梅內派「自由天主教」的通諭，斥良心自由為「瘋話」、出版自由為毒泉。拉梅內遂棄教而去。此諭是十九世紀教廷對自由主義的第一聲斷喝，其立場至梵二《信仰自由宣言》方告翻轉。' },
          { title_zh: '何等關懷通諭與謬說要錄', title_orig: 'Quanta Cura et Syllabus Errorum', author: '教宗庇護九世', era: '1864', place: '羅馬', language: '拉丁文', intro: '庇護九世頒布通諭並附八十條《謬說要錄》，總斥理性主義、政教分離與「教宗應與進步、自由主義及現代文明和解」之說。歐洲輿論譁然，本篤文件是「圍城心態」天主教的紀念碑，梵一權威路線的前奏。' },
          { title_zh: '不可言喻的天主詔書', title_orig: 'Ineffabilis Deus', author: '教宗庇護九世', era: '1854', place: '羅馬', language: '拉丁文', intro: '庇護九世欽定聖母無染原罪為信理的詔書，為教宗首度不經大公會議獨自定斷信理，四年後露德顯現自稱「無原罪者」更添聲勢。此詔是聖母敬禮與教宗權威同步登頂的文本，直接預備了梵一的不可錯誤論。' },
          { title_zh: '上智天主通諭', title_orig: 'Providentissimus Deus', author: '教宗良十三世', era: '1893', place: '羅馬', language: '拉丁文', intro: '良十三世論聖經研究的通諭，鼓勵原文與東方學訓練以應對高等批判，同時重申默感無誤。它是教廷正面回應近代聖經學的第一份大憲章，梵二《啟示憲章》的百年伏線，天主教聖經運動皆溯源於此。' },
          { title_zh: '聖神恩賜通諭', title_orig: 'Divinum Illud Munus', author: '教宗良十三世', era: '1897', place: '羅馬', language: '拉丁文', intro: '良十三世論聖神在教會與靈魂中工作的通諭，籲全教會每年聖神降臨節前作九日敬禮。適值靈恩復興前夜，此諭被視為天主教聖神神學復甦的先聲，二十世紀「聖神的世紀」的官方序曲。' },
          { title_zh: '東方教會尊嚴通諭', title_orig: 'Orientalium Dignitas', author: '教宗良十三世', era: '1894', place: '羅馬', language: '拉丁文', intro: '良十三世保障東方禮天主教會禮儀與法統的通諭，嚴禁拉丁傳教士誘使東方信徒改禮。它扭轉數百年拉丁化政策，宣認東方傳統為普世教會的瑰寶，是近代教廷東方政策的轉捩文件與合一運動的遠因。' },
          { title_zh: '傳信部致代牧訓令', title_orig: 'Instructio Vicariorum Apostolicorum (1659)', author: '教廷傳信部', era: '1659', place: '羅馬', language: '拉丁文', intro: '傳信部致首批赴東亞宗座代牧的訓令，明言「勿移植歐洲風俗，唯傳信仰」，尊重各民族禮俗除非顯悖信德。此文為教廷本地化政策最開明的表述，與其後禮儀之爭的禁令對照如兩個教會，宣教學史的必讀文獻。' },
          { title_zh: '眾教會之關懷詔書', title_orig: 'Sollicitudo omnium ecclesiarum', author: '教宗庇護七世', era: '1814', place: '羅馬', language: '拉丁文', intro: '拿破崙覆亡之年，庇護七世頒詔恢復被解散四十一年的耶穌會，稱船遇風暴豈可拒斥老練槳手。流亡歸來的教宗以此詔重整教會元氣，耶穌會旋即重返教育與宣教前線，是復闢時代天主教復興的標誌文件。' }
        
        
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
          { title_zh: '路德洗禮小冊', title_orig: 'Das Taufbüchlein', author: '馬丁‧路德', era: '1523（1526 修訂）', place: '維滕堡', language: '德文', intro: '路德把拉丁洗禮禮文譯為德語並漸次刪削驅魔等儀節的小冊，使會眾首度以母語參與聖禮。其修訂軌跡具體呈現宗教改革「禮儀漸進本地化」的策略，為路德宗各邦教會洗禮禮文的共同底本。' },
          { title_zh: '拉丁彌撒儀式', title_orig: 'Formula Missae et Communionis', author: '馬丁‧路德', era: '1523', place: '維滕堡', language: '拉丁文', intro: '路德改革彌撒的第一步：保留拉丁文與大部分儀節，惟刪去奉獻經文等「祭獻」語言，恢復會眾領杯。本儀式與其後的德意志彌撒並行，確立路德宗「禮儀保守改革」的雙軌格局，影響北歐諸國教會至今。' },
          { title_zh: '蘇黎世聖餐禮文', title_orig: 'Action oder Brauch des Nachtmahls', author: '茨溫利', era: '1525', place: '蘇黎世', language: '德文', intro: '茨溫利廢除彌撒後為蘇黎世制定的聖餐禮文：木盤木杯傳遞會眾，全程無歌唱、無祭壇，唯讀經與紀念。它把「紀念說」神學化為最簡樸的禮儀形式，是改革宗禮儀傳統激進一翼的原型文獻。' },
          { title_zh: '史特拉斯堡崇拜禮文', title_orig: 'Grund und Ursach / Strassburger Gottesdienstordnung', author: '馬丁‧布塞爾', era: '1524–1539', place: '史特拉斯堡', language: '德文', intro: '布塞爾在史特拉斯堡漸次定型的德語崇拜程序，以講道為中心而保留每主日聖餐理想，並創詩篇會眾唱詠之風。加爾文流亡此城時深受其式塑，日內瓦禮文實承其緒，是改革宗禮儀的隱形母本。' },
          { title_zh: '科隆簡明教程', title_orig: 'Einfaltigs Bedencken (Consultatio)', author: '赫爾曼‧馮‧維德（布塞爾、墨蘭頓執筆）', era: '1543', place: '科隆', language: '德文／拉丁文', intro: '科隆大主教赫爾曼委託布塞爾與墨蘭頓起草的教區改革方案，含完整禮儀與教理規劃，事雖敗於帝國幹預，其禮文卻經克蘭麥大量移入《公禱書》。一部流產的德意志改革方案竟成英格蘭禮儀的血脈，是禮儀史的著名轉渡。' },
          { title_zh: '公共秩序書', title_orig: 'The Book of Common Order', author: '約翰‧諾克斯', era: '1564', place: '愛丁堡', language: '英文', intro: '諾克斯自日內瓦流亡社群禮文發展而成的蘇格蘭教會崇拜手冊，附韻文詩篇，供牧者以自由祈禱為主軸的框架。它確立蘇格蘭長老宗「有秩序而不拘禮文」的崇拜傳統，行用近一世紀直至西敏指南取代。' },
          { title_zh: '一六三七年蘇格蘭公禱書', title_orig: 'The Booke of Common Prayer for the Use of the Church of Scotland', author: '勞德與蘇格蘭主教團', era: '1637', place: '愛丁堡', language: '英文', intro: '查理一世與勞德強加蘇格蘭的公禱書，聖餐禮文較英格蘭版更近古公教傳統，頒行首日即在聖吉爾斯座堂引發擲凳暴動，直接點燃主教戰爭與三國內戰。一部禮書掀翻三個王國，是禮儀政治學最極端的案例。' },
          { title_zh: '薩伏依禮文', title_orig: 'The Savoy Liturgy (Reformed Liturgy)', author: '理查‧巴克斯特', era: '1661', place: '倫敦薩伏依會議', language: '英文', intro: '王政復闢後薩伏依會議上，巴克斯特倉促數日間為清教一方起草的替代禮文，全依聖經語言鋪陳聖餐與主日崇拜。方案遭主教方否決，次年兩千清教牧者被逐出國教，本禮文遂成英格蘭不從國教傳統的禮儀紀念碑。' },
          { title_zh: '衛斯理主日崇拜書', title_orig: 'The Sunday Service of the Methodists in North America', author: '約翰‧衛斯理', era: '1784', place: '倫敦（為北美編）', language: '英文', intro: '衛斯理為獨立後的北美循道會眾修訂《公禱書》而成的崇拜書，刪節日課、簡化條文並附其按立文書。它標誌循道運動由國教內團契轉為自立教會，是美國衛理公會禮儀傳統的奠基文件。' },
          { title_zh: '美國聖公會公禱書', title_orig: 'The Book of Common Prayer (Protestant Episcopal Church, 1789)', author: '美國聖公會總議會', era: '1789', place: '費城', language: '英文', intro: '美國獨立後聖公會自訂的公禱書，刪去為英王代禱，聖餐祝謝文採蘇格蘭主教傳統的呼求聖靈禱文，較英格蘭版更近東方古禮。它是公禱書傳統首度跨出王權框架的改編，此後全球聖公宗各自訂本皆循此例。' },
          { title_zh: '摩拉維亞弟兄會禮文集', title_orig: 'Liturgien der Brüdergemeine', author: '親岑多夫與合一弟兄會', era: '1727–1789', place: '赫恩胡特', language: '德文', intro: '重生的合一弟兄會在赫恩胡特發展出的禮文體系：愛筵、守望禱告、受難週逐日禮與復活節晨禮，歌唱貫穿一切。其「歌唱崇拜」與節期創意深刻影響衛斯理與後世新教，是敬虔運動禮儀創造力的結晶。' },
          { title_zh: '瑞典教會手冊', title_orig: 'Then Swenska Kyrkeordningen / Handbok', author: '勞倫提烏斯‧彼得裡', era: '1571', place: '烏普薩拉', language: '瑞典文', intro: '瑞典首任新教總主教勞倫提烏斯‧彼得裡編訂的教會手冊與禮規，保留主教制、祭衣與大量中世紀儀節而注入福音派講道。瑞典教會「保守的宗教改革」由此定型，為路德宗禮儀光譜中最近公教的一翼。' },
          { title_zh: '達特恩詩篇與禮文', title_orig: 'De Psalmen Davids / Liturgie (Petrus Dathenus)', author: '彼得‧達特恩', era: '1566', place: '法蘭肯塔爾（普法爾茨）', language: '荷蘭文', intro: '流亡牧師達特恩把日內瓦詩篇與普法爾茨禮文譯為荷蘭語，附洗禮聖餐禮文與教理問答，旋為荷蘭歸正教會採用逾兩世紀。低地國會眾至今傳唱其詩篇韻文，是荷蘭改革宗敬拜傳統的立基文本。' }
        
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
          { title_zh: '羅馬主教禮書', title_orig: 'Pontificale Romanum', author: '克萊孟八世頒布', era: '1595–1596', place: '羅馬', language: '拉丁文', intro: '特倫託改革後統一頒布的主教專用禮書，收按立、堅振、祝聖教堂與祝福修院等主教禮典，取代各地紛雜的中世紀主教禮書。它與彌撒經書、日課經合構特倫託禮儀體系的骨架，行用至二十世紀禮儀改革。' },
          { title_zh: '主教典禮書', title_orig: 'Caeremoniale Episcoporum', author: '克萊孟八世頒布', era: '1600', place: '羅馬', language: '拉丁文', intro: '規範主教座堂禮儀排場與職司分工的典禮書：主教大禮彌撒的每一鞠躬、持杖、脫冠皆有明文。它把巴洛克天主教的視覺神學編成條文，是研究近代天主教禮儀空間與身體語言的第一手法典。' },
          { title_zh: '羅馬殉道聖人錄', title_orig: 'Martyrologium Romanum', author: '巴羅尼烏斯修訂', era: '1583–1586', place: '羅馬', language: '拉丁文', intro: '教會史家巴羅尼烏斯考訂歷代殉道者與聖人紀唸的官方名錄，按曆日編排供日課誦讀。特倫託改革以此清理中世紀聖人崇敬的訛濫，兼具禮儀書與史學工程雙重性格，為天主教曆法敬禮的權威底冊。' },
          { title_zh: '額我略聖詠美第奇版', title_orig: 'Editio Medicaea (Graduale Romanum)', author: '阿內裡奧與蘇裡亞諾修訂', era: '1614–1615', place: '羅馬美第奇印書坊', language: '拉丁文', intro: '特倫託後官方刊行的額我略聖詠標準本，依當時審美削平中世紀旋律的裝飾音型。此版通行近三百年，至索雷姆修道院復原古譜方被取代，是聖詠傳統「近代化改寫」的著名案例，禮儀音樂史的關鍵座標。' },
          { title_zh: '聖母小日課修訂本', title_orig: 'Officium parvum Beatae Mariae Virginis (Pius V)', author: '庇護五世頒布', era: '1571', place: '羅馬', language: '拉丁文', intro: '庇護五世修訂頒行的聖母小日課，為平信徒與善會提供簡化的每日祈禱框架，附諸聖連禱。時值勒班陀之役，玫瑰經與小日課的普及構成近代天主教平信徒敬禮的雙翼，本書即其官定文本。' },
          { title_zh: '一七三八年巴黎彌撒經書', title_orig: 'Missale Parisiense', author: '巴黎總主教文提米耶主持', era: '1738', place: '巴黎', language: '拉丁文', intro: '法國教會自主編訂的「新加利剛」彌撒經書，經文悉出聖經、對經重新譜排，體現高盧主義的禮儀自信。十九世紀蓋朗熱力主羅馬統一而將其廢除，然其經文編排竟多為二十世紀羅馬新彌撒吸收，是禮儀史的迂迴伏筆。' },
          { title_zh: '論彌撒聖祭', title_orig: 'De sacrosancto missae sacrificio', author: '本篤十四世（蘭貝提尼）', era: '1748', place: '羅馬', language: '拉丁文', intro: '學者教宗本篤十四世論彌撒的專著，逐段考釋禮文源流與神學義蘊，兼裁決禮儀疑難。出自教宗之手的禮儀學術著作史所罕見，是十八世紀天主教禮儀學的權威總結。' },
          { title_zh: '蓋朗熱禮儀年', title_orig: 'L\'Année liturgique', author: '普羅斯佩‧蓋朗熱', era: '1841–1866', place: '索雷姆修道院', language: '法文', intro: '索雷姆修道院重建者蓋朗熱按禮儀年逐日詮釋彌撒與日課的鉅著十五卷，教平信徒「隨教會的禱」。本書掀起近代禮儀運動的第一波，使禮儀由教士專業重新成為信眾靈修的泉源，影響直達二十世紀禮儀改革。' },
          { title_zh: '索雷姆額我略聖詠復原本', title_orig: 'Liber Gradualis (Solesmes)', author: '波蒂埃與索雷姆聖詠學派', era: '1883', place: '索雷姆修道院', language: '拉丁文', intro: '索雷姆修士波蒂埃據中世紀抄本比勘復原的額我略聖詠刊本，推翻通行三百年的美第奇版。其古譜學方法開宗教音樂文獻學之先，一九〇三年獲教宗欽定為普世範本，是十九世紀「回到源頭」運動的音樂豐碑。' }
        
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
          { title_zh: '教宗瑪爾切羅彌撒', title_orig: 'Missa Papae Marcelli', author: '帕萊斯特里納', era: '約 1562', place: '羅馬', language: '拉丁文', intro: '帕萊斯特里納的六聲部彌撒曲，傳說以其歌詞清晰說服特倫託會議保留複音音樂。傳說雖經渲染，本曲確為「羅馬風格」的典範：聲部勻淨、詞義透明，此後四百年天主教會奉之為教會音樂的黃金準繩。' },
          { title_zh: '拉索懺悔詩篇', title_orig: 'Psalmi Davidis poenitentiales', author: '奧蘭多‧迪‧拉索', era: '1584 刊（作約 1560 年代）', place: '慕尼黑', language: '拉丁文', intro: '拉索為巴伐利亞公爵譜寫的七首懺悔詩篇連篇曲，情感刻畫細入肌理，原以泥金抄本秘藏宮廷。它把文藝復興複音的修辭表現力推向極致，是反宗教改革時代「以音樂懺悔」的最深沉文獻。' },
          { title_zh: '維多利亞聖週響應曲集', title_orig: 'Officium Hebdomadae Sanctae', author: '託馬斯‧路易斯‧德‧維多利亞', era: '1585', place: '羅馬', language: '拉丁文', intro: '西班牙司鐸作曲家維多利亞為聖週禮儀譜寫的全套音樂，暗夜禮響應曲哀切如泣，被視為天主教神秘主義的音樂化身。他終身只寫宗教音樂，本集是特倫託改革靈性最純粹的聲音結晶。' },
          { title_zh: '寄望於他', title_orig: 'Spem in alium', author: '託馬斯‧塔利斯', era: '約 1570', place: '英格蘭', language: '拉丁文', intro: '塔利斯為八組五聲部合唱共四十聲部而作的巨型經文歌，聲浪如穹頂環抱，為西方音樂史空間音響的奇蹟。成於新教英格蘭而以拉丁文歌詞頌上帝眷顧，其創作背景至今成謎，益增此曲的傳奇色彩。' },
          { title_zh: '伯德三聲部至五聲部彌撒曲', title_orig: 'Masses for Three, Four and Five Voices', author: '威廉‧伯德', era: '約 1592–1595', place: '英格蘭', language: '拉丁文', intro: '天主教徒伯德在新教英格蘭冒禁為地下彌撒譜寫的三套彌撒曲，秘密刊行不署標題頁。音樂內斂深摯，為受迫害群體的密室禮儀而生，是信仰堅忍與藝術完美合一的絕品，今日已成英國合唱經典。' },
          { title_zh: '蒙臺威爾第聖母晚禱', title_orig: 'Vespro della Beata Vergine', author: '克勞迪奧‧蒙臺威爾第', era: '1610', place: '曼託瓦／威尼斯', language: '拉丁文', intro: '蒙臺威爾第把新生的歌劇語彙傾注於晚禱音樂：獨唱花腔、迴聲對答與古聖詠定旋律並置，開巴洛克宗教音樂之門。本作獻給教宗而終老威尼斯聖馬可，是禮儀音樂由文藝復興轉入巴洛克的分水嶺。' },
          { title_zh: '許茨神聖交響曲', title_orig: 'Symphoniae sacrae', author: '海因裡希‧許茨', era: '1629–1650', place: '德勒斯登／威尼斯', language: '拉丁文／德文', intro: '許茨三度出版的聖經經文協唱曲集，把威尼斯的協奏風格嫁接於德語聖經，三十年戰爭的凋敝迫使他以最小編制寫出最深的哀懇。他是巴哈之前德國最偉大的教會作曲家，本集為德語宗教音樂的奠基石。' },
          { title_zh: '巴哈約翰受難曲', title_orig: 'Johannes-Passion', author: '約翰‧塞巴斯蒂安‧巴哈', era: '1724', place: '萊比錫', language: '德文', intro: '巴哈就任萊比錫樂長後首部受難曲，以約翰福音的莊嚴基督論為軸，戲劇張力較馬太受難曲更為峻急。開篇合唱「主，我們的主宰」如宇宙迴旋，本作與馬太受難曲同為路德宗禮儀音樂的至高雙峰。' },
          { title_zh: '巴哈B小調彌撒', title_orig: 'Messe in h-Moll', author: '約翰‧塞巴斯蒂安‧巴哈', era: '1749 完成', place: '萊比錫', language: '拉丁文', intro: '路德宗樂長巴哈晚年集畢生技藝完成的拉丁大彌撒，跨越宗派藩籬把信經逐句築成音響的大教堂。全曲超出任何實際禮儀所需，儼然音樂神學的總結性告白，屢被譽為西方音樂的最高成就。' },
          { title_zh: '巴哈聖誕神劇', title_orig: 'Weihnachts-Oratorium', author: '約翰‧塞巴斯蒂安‧巴哈', era: '1734', place: '萊比錫', language: '德文', intro: '巴哈為聖誕至主顯十二日節期編成的六部連環清唱劇，田園搖籃曲與號角合唱交織降生的奧秘與喜樂。本作依禮儀年逐日演出的設計，示範教會音樂如何伴隨會眾行走節期，至今仍是普世聖誕音樂的中心。' },
          { title_zh: '海頓創世記', title_orig: 'Die Schöpfung', author: '約瑟夫‧海頓', era: '1798', place: '維也納', language: '德文', intro: '海頓晚年以創世記與失樂園為本的神劇，「要有光」的C大調爆發為音樂史最著名的一瞬。啟蒙時代的自然頌讚與虔誠信仰在此渾然一體，海頓自言作曲時「未曾如此虔敬」，是古典時期宗教音樂的巔峰。' },
          { title_zh: '莫札特安魂曲', title_orig: 'Requiem in d-Moll KV 626', author: '莫札特（絕筆，敘斯邁爾補成）', era: '1791', place: '維也納', language: '拉丁文', intro: '莫札特臨終未竟的安魂彌撒，「落淚之日」寫至第八小節而筆落人亡，由弟子補全。神秘的委託與天才之死使本曲籠罩傳奇，其「震怒之日」與「奇妙號聲」把末日經文烙進世界的聽覺記憶。' },
          { title_zh: '貝多芬莊嚴彌撒', title_orig: 'Missa solemnis', author: '路德維希‧範‧貝多芬', era: '1819–1823', place: '維也納', language: '拉丁文', intro: '貝多芬自認畢生最偉大的作品，題辭「發自內心——願它再抵達人心」。降B大調的信經如信仰的攻堅戰，羔羊經中戰鼓逼近而祈和平之聲愈切。本作把個人靈魂的搏鬥注入彌撒通用文，是禮儀文本交響化的極限。' },
          { title_zh: '孟德爾頌以利亞', title_orig: 'Elias', author: '費利克斯‧孟德爾頌', era: '1846', place: '伯明罕首演', language: '德文／英文', intro: '猶太裔新教作曲家孟德爾頌以列王紀先知敘事譜成的神劇，迦密山鬥法與微聲中的上帝戲劇性十足。本作接續韓德爾-海頓神劇傳統而注入浪漫抒情，首演即轟動，成為英語世界合唱節文化的支柱曲目。' },
          { title_zh: '布拉姆斯德意志安魂曲', title_orig: 'Ein deutsches Requiem', author: '約翰內斯‧布拉姆斯', era: '1868', place: '不來梅首演', language: '德文', intro: '布拉姆斯棄拉丁通用文，自路德聖經親選經文譜成的安魂曲，不為亡者求息止而為生者求安慰。「凡有血氣者盡如草」的送葬進行曲沉痛如大地脈搏，是新教聖經靈性最偉大的音樂表達之一。' },
          { title_zh: '威爾第安魂曲', title_orig: 'Messa da Requiem', author: '朱塞佩‧威爾第', era: '1874', place: '米蘭', language: '拉丁文', intro: '威爾第為文豪曼佐尼逝世週年譜寫的安魂彌撒，「震怒之日」的大鼓重擊為音樂會的震撼名場面。歌劇之王以劇場火焰燃燒禮儀經文，虔敬與戲劇的邊界之辯隨之百年不休，本作自身則已成安魂曲傳統的高峰。' },
          { title_zh: '佛瑞安魂曲', title_orig: 'Requiem op. 48', author: '加布裡埃爾‧佛瑞', era: '1887–1890', place: '巴黎馬德萊娜教堂', language: '拉丁文', intro: '教堂樂師佛瑞刻意淡去震怒之日、以「在天國」的童聲收束的安魂曲，靜謐如搖籃曲，自稱「死亡的搖籃曲」。它代表法國教會音樂的內斂路線，與威爾第的戲劇路線互為兩極，同列安魂曲雙璧。' },
          { title_zh: '布魯克納感恩曲', title_orig: 'Te Deum', author: '安東‧布魯克納', era: '1884', place: '維也納', language: '拉丁文', intro: '虔誠的管風琴師布魯克納自視為「獻給上帝」的感恩頌，C大調的巨大音塊如大教堂石柱層層升起。他把交響樂的宏偉歸還禮儀讚歌，臨終猶囑以此曲代未完成的第九交響曲終樂章，是十九世紀信仰交響化的極致。' },
          { title_zh: '柴可夫斯基金口若望事奉聖禮', title_orig: 'Литургия святого Иоанна Златоуста', author: '彼得‧柴可夫斯基', era: '1878', place: '莫斯科', language: '教會斯拉夫文', intro: '柴可夫斯基為正教事奉聖禮全套禮文譜寫的無伴奏合唱，突破帝國教會對禮儀音樂的出版壟斷而涉訟，勝訴後開俄國作曲家自由創作教會音樂之路。本作是俄羅斯「新禮儀樂派」的先聲，拉赫瑪尼諾夫承其餘緒。' },
          { title_zh: '博爾特尼揚斯基聖頌協唱曲集', title_orig: 'Духовные концерты Бортнянского', author: '德米特里‧博爾特尼揚斯基', era: '約 1780–1825', place: '聖彼得堡', language: '教會斯拉夫文', intro: '烏克蘭出身的宮廷樂長博爾特尼揚斯基融義大利技法與斯拉夫聖詠寫成的三十五首聖頌協唱曲，貝多芬亦為之傾倒。他確立俄國無伴奏教會合唱的古典風範，其曲目至今仍為正教詩班的核心保留曲。' },
          { title_zh: '夏邦蒂埃感恩曲', title_orig: 'Te Deum H.146', author: '馬克-安託萬‧夏邦蒂埃', era: '約 1692', place: '巴黎', language: '拉丁文', intro: '夏邦蒂埃為路易十四時代勝利慶典譜寫的感恩頌，D大調前奏的號角迴旋曲光輝奪目。本作是法國巴洛克「大經文歌」傳統的代表，見證禮儀音樂與王權慶典的共生，前奏曲今為歐洲廣播聯盟的會歌。' },
          { title_zh: '維瓦爾第榮耀頌', title_orig: 'Gloria RV 589', author: '安東尼奧‧維瓦爾第', era: '約 1715', place: '威尼斯憐憫院', language: '拉丁文', intro: '「紅髮神父」維瓦爾第為威尼斯孤女院詩班譜寫的榮耀頌，明亮的協奏風格使禮儀讚歌如節慶陽光。孤女院的女聲合唱是巴洛克威尼斯的奇景，本作即其音樂事工的結晶，湮沒兩百年後重光而風行世界。' },
          { title_zh: '佩爾戈萊西聖母悼歌', title_orig: 'Stabat Mater', author: '喬瓦尼‧佩爾戈萊西', era: '1736', place: '波佐利', language: '拉丁文', intro: '廿六歲的佩爾戈萊西肺病垂死中為那不勒斯善會寫成的聖母悼歌，女聲二重的哀婉開篇成為十八世紀最流行的宗教音樂，巴哈亦改編之。天才早夭與哀母題材相映，本作是巴洛克晚期虔敬感性的代表作。' },
          { title_zh: '羅西尼聖母悼歌', title_orig: 'Stabat Mater (Rossini)', author: '焦阿基諾‧羅西尼', era: '1842', place: '巴黎', language: '拉丁文', intro: '歌劇退休後的羅西尼以美聲筆法譜寫的聖母悼歌，詠嘆調式的獨唱華彩引發「劇場侵入聖所」的著名論戰。本作與其晚年《小莊嚴彌撒》同為十九世紀義大利宗教音樂的代表，雅俗之辯的核心標本。' },
          { title_zh: '古諾聖則濟利亞莊嚴彌撒', title_orig: 'Messe solennelle de Sainte-Cécile', author: '夏爾‧古諾', era: '1855', place: '巴黎', language: '拉丁文', intro: '曾志於司鐸的古諾獻給音樂主保聖則濟利亞的莊嚴彌撒，旋律甜美如祈禱的歌劇。本作風靡第二帝國的巴黎，代表十九世紀法國「浪漫虔敬」的教會音樂路線，亦是聖則濟利亞節音樂傳統的名作。' },
          { title_zh: '李斯特基督', title_orig: 'Christus', author: '法蘭茲‧李斯特', era: '1862–1866', place: '羅馬', language: '拉丁文', intro: '晚年領受小品級的李斯特以三部十四曲鋪陳基督生平的神劇，自額我略聖詠素材織出前瞻的和聲語言。本作是他「以現代音樂更新教會藝術」宣言的實踐，湮沒百年後始獲公認為十九世紀宗教音樂的巨構。' },
          { title_zh: '德弗札克聖母悼歌', title_orig: 'Stabat Mater op. 58', author: '安東寧‧德弗札克', era: '1877', place: '布拉格', language: '拉丁文', intro: '德弗札克連喪三子後譜寫的聖母悼歌，把個人喪慟沉入中世紀哀歌文本，終曲於「樂園的榮耀」中破涕成光。本作使他揚名英倫，是捷克民族樂派獻給普世教會的第一件大禮，喪子之痛昇華為信仰安慰的典範。' },
          { title_zh: '瓦爾特維滕堡聖歌小冊', title_orig: 'Geystliche gesangk Buchleyn', author: '約翰‧瓦爾特（路德合作）', era: '1524', place: '維滕堡', language: '德文', intro: '路德的音樂夥伴瓦爾特編印的四聲部聖歌集，為新教史上第一部合唱聖詩集，收路德〈上主是我堅固保障〉前身諸曲。它確立「眾讚歌」為路德宗敬拜的核心，此一傳統直通巴哈的清唱劇宇宙。' },
          { title_zh: '波希米亞弟兄會聖詩集', title_orig: 'Kancionál Jednoty bratrské', author: '波希米亞弟兄合一會', era: '1501（1561 大擴編）', place: '布拉格／伊萬奇採', language: '捷克文', intro: '胡斯運動後裔弟兄合一會刊行的捷克語聖詩集，一五〇一年初版被視為史上第一部民族語會眾聖詩集。歷次擴編收詩逾七百首，流亡後由誇美紐斯續編，是新教會眾歌唱傳統真正的起點。' },
          { title_zh: '史滕霍爾德-霍普金斯詩篇全集', title_orig: 'The Whole Booke of Psalmes (Sternhold & Hopkins)', author: '史滕霍爾德與霍普金斯', era: '1562', place: '倫敦', language: '英文', intro: '英格蘭第一部完整韻文詩篇集，通用格律配民謠式曲調，與聖經、公禱書合訂進入每個教堂與家庭，兩百年間刊行逾六百版。它是英語世界會眾歌唱的實際起點，「舊版詩篇」之名沿用至瓦茨時代。' },
          { title_zh: '蘇格蘭韻文詩篇', title_orig: 'The Psalms of David in Meeter (Scottish Psalter)', author: '西敏會議與蘇格蘭教會修訂', era: '1650', place: '愛丁堡', language: '英文', intro: '蘇格蘭教會定本韻文詩篇，字句忠實而格律齊整，〈耶和華是我牧者〉（Crimond 調）由此傳唱世界。長老宗「唯獨詩篇」的敬拜傳統以此為聖典，蘇格蘭至今守之，是韻文詩篇文化的活化石。' },
          { title_zh: '海灣詩篇書', title_orig: 'The Bay Psalm Book', author: '麻薩諸塞灣清教牧者群譯', era: '1640', place: '劍橋（麻薩諸塞）', language: '英文', intro: '英屬北美刊行的第一部書籍：清教移民自希伯來原文重譯的韻文詩篇，序言申明「寧要真確、不求文采」。本書見證新大陸敬拜自給的決心，存世初版十一部為美洲印刷與宗教史的頭號文物。' },
          { title_zh: '神聖豎琴', title_orig: 'The Sacred Harp', author: '懷特與金（編）', era: '1844', place: '喬治亞州', language: '英文', intro: '美國南方形符記譜的無伴奏聖歌集，四形音符使不識譜的鄉民圍成方陣放聲而歌。「神聖豎琴歌唱」至今聚會不輟，是美國民間宗教音樂最強韌的活傳統，草根敬拜文化的代表文獻。' },
          { title_zh: '美國奴隸歌曲集', title_orig: 'Slave Songs of the United States', author: '艾倫、韋爾與加里森（輯）', era: '1867', place: '紐約', language: '英文', intro: '南北戰爭甫結束即輯錄的黑人靈歌一百三十六首，為非裔美國人宗教歌唱最早的系統文獻，〈走下去，摩西〉諸曲賴以傳世。靈歌自苦難中鍛出的盼望神學，經此書進入世界音樂史，是黑人教會敬拜的元典。' },
          { title_zh: '桑基福音聖歌集', title_orig: 'Sacred Songs and Solos', author: '艾拉‧桑基', era: '1873–1903 增編', place: '倫敦／紐約', language: '英文', intro: '慕迪佈道大會的歌手桑基編纂的福音聖歌集，副歌易記、伴奏簡明，隨佈道浪潮售逾八千萬冊。「福音詩歌」文類由此定型，芬妮‧克羅斯比諸作賴以流通，是近代大眾佈道音樂文化的總匯。' },
          { title_zh: '十字架上七言', title_orig: 'Die sieben letzten Worte unseres Erlösers am Kreuze', author: '約瑟夫‧海頓', era: '1786（合唱版 1796）', place: '加地斯／維也納', language: '德文／器樂', intro: '海頓應加地斯聖洞教堂聖週默想禮之邀而作：主教每誦一言，樂隊奏一段慢板引導會眾默想。作品後改編為弦樂四重奏與神劇版本，是禮儀默想直接催生器樂經典的罕例，聖週音樂傳統的名作。' },
          { title_zh: '舒伯特降E大調彌撒', title_orig: 'Messe Nr. 6 Es-Dur D 950', author: '法蘭茲‧舒伯特', era: '1828', place: '維也納', language: '拉丁文', intro: '舒伯特逝世前數月完成的最後彌撒曲，聖哉經的賦格與羔羊經的暗湧把個人的死亡預感織入禮儀經文。他慣於信經中略去「唯一聖而公教會」一句，其信仰的私人性與音樂的懇切同為後世聚訟的謎題。' }
        
        
        ],
      },
      {
        key: 'eastern-liturgy',
        label: '東方禮儀部',
        label_en: 'Eastern Liturgies',
        desc: '近代東方教會的禮儀書刊印傳統——基輔、莫斯科、亞美尼亞、馬龍派與科普特的禮典與刊本。',
        works: [
          { title_zh: '莫吉拉大禮典', title_orig: 'Trebnik (Euchologion) Petra Mohyly', author: '基輔都主教彼得‧莫吉拉', era: '1646', place: '基輔洞窟修道院', language: '教會斯拉夫文', intro: '基輔都主教莫吉拉編訂的大型禮典，收聖事與各式祝福禮文並附牧養指引，參酌希臘與拉丁學術而自成體系。它是近代東正教禮儀書刊印的最大工程，斯拉夫正教世界沿用其文本至今，兼證基輔學術的黃金時代。' },
          { title_zh: '尼康修訂事奉聖禮書', title_orig: 'Sluzhebnik (Nikonian revision)', author: '莫斯科宗主教尼康主持', era: '1655', place: '莫斯科', language: '教會斯拉夫文', intro: '宗主教尼康依希臘刊本校訂俄國事奉聖禮書，改三指畫十字等儀節，引發舊禮儀派大分裂，百萬信徒寧受迫害不從新禮。一部禮書的修訂撕裂俄羅斯宗教社會兩百年，是禮儀文本與民族認同糾纏的最沉重案例。' },
          { title_zh: '亞美尼亞初刊祈禱書', title_orig: 'Urbatagirk', author: '哈科布‧梅加帕特（刊印）', era: '1512', place: '威尼斯', language: '亞美尼亞文', intro: '亞美尼亞史上第一部印刷書籍：威尼斯刊行的《週五書》祈禱文集，收治病禳災禱文與納雷克的格列高利禱詞選。流散商人社群以印刷術續命民族禮儀傳統，本書是東方基督教印刷文化的破曉之作。' },
          { title_zh: '馬龍派羅馬刊本彌撒書', title_orig: 'Missale Chaldaicum iuxta ritum ecclesiae nationis Maronitarum', author: '馬龍派教會（羅馬東方語文印書院刊）', era: '1592–1594', place: '羅馬', language: '敘利亞文', intro: '羅馬美第奇東方印書院為馬龍派刊行的敘利亞語彌撒經書，是東方禮儀書在西方付印的先聲。它見證與羅馬共融的東方教會如何藉印刷保存古敘利亞禮儀，兼為近代東方學與教會外交交會的產物。' },
          { title_zh: '圖基科普特禮書刊本', title_orig: 'Missale Coptice et Arabice (Raphael Tuki)', author: '拉斐爾‧圖基', era: '1736–1764', place: '羅馬', language: '科普特文／阿拉伯文', intro: '科普特出身的羅馬主教圖基整理刊行的科普特-阿拉伯雙語禮書系列，含彌撒、日課與聖事禮文，為科普特禮儀首度系統付印。這批刊本長期為埃及教會實際使用，是科普特禮儀文本近代傳承的樞紐。' }
        
        ]
      },
      {
        key: 'devotional-prayer',
        label: '祈禱與敬虔書部',
        label_en: 'Prayer Books and Devotional Manuals',
        desc: '近代東西方的祈禱書、默想手冊與敬虔生活指南——自路德小祈禱書至朝聖者之路。',
        works: [
          { title_zh: '路德小祈禱書', title_orig: 'Betbüchlein', author: '馬丁‧路德', era: '1522', place: '維滕堡', language: '德文', intro: '路德為取代中世紀繁蕪的祈禱書而編的小冊，以十誡、信經、主禱文為骨架教人禱告，後續增詩篇與受難默想。它把改革的核心教導化為家庭靈修的日用品，是新教敬虔文獻的第一塊基石。' },
          { title_zh: '安德魯斯私禱集', title_orig: 'Preces Privatae', author: '蘭斯洛特‧安德魯斯', era: '約 1600–1626（1648 刊）', place: '倫敦', language: '希臘文／拉丁文', intro: '欽定本聖經主譯者安德魯斯以希臘拉丁文為自己編織的私禱手冊，按日按時輯綴聖經與古教會禱文，手稿浸滿淚痕。死後刊行而成聖公會靈修珍典，展示高教會派學識與虔敬合一的禱告世界。' },
          { title_zh: '泰勒聖潔生活', title_orig: 'The Rule and Exercises of Holy Living', author: '傑瑞米‧泰勒', era: '1650', place: '威爾斯（內戰流亡中）', language: '英文', intro: '聖公會神學家泰勒於清教當政、國教崩解之際寫成的聖潔生活指南，教平信徒在無教會可依時自行操練時間、貞潔與敬虔。文體華美如祈禱的散文詩，與姊妹作《聖潔死亡》同為英語靈修文學的冠冕。' },
          { title_zh: '貝利敬虔的實踐', title_orig: 'The Practice of Piety', author: '路易斯‧貝利', era: '約 1611', place: '威爾斯班戈', language: '英文', intro: '班戈主教貝利的敬虔生活全書，自晨禱至臨終逐項指引，兼附齋戒與領聖餐之法。本書刊行逾七十版、譯成歐洲諸語乃至麻薩諸塞印第安語，清教徒班揚由妻子的嫁妝書中讀到的正是它，堪稱十七世紀第一暢銷靈修書。' },
          { title_zh: '科西私禱集', title_orig: 'A Collection of Private Devotions', author: '約翰‧科西', era: '1627', place: '倫敦', language: '英文', intro: '科西應宮廷女官之需按時辰祈禱傳統編成的私禱集，恢復七時課架構而全取材聖經與古教會。清教徒抨其「羅馬化」，本書遂成國教會內部禮儀路線之爭的標本，亦是英語時辰靈修的優美範本。' },
          { title_zh: '與神同在的操練', title_orig: 'The Practice of the Presence of God', author: '勞倫斯弟兄', era: '1692 輯刊', place: '巴黎加爾默羅會院', language: '法文', intro: '赤足加爾默羅會廚房雜役勞倫斯弟兄的談話與書信輯錄，教人在洗碗鍋灶間時時轉念向神，「廚房與祭壇無別」。小書百餘頁而流傳三百年，跨越宗派為天主教與新教共愛，是日常靈修觀最樸素有力的表述。' },
          { title_zh: '簡易祈禱法', title_orig: 'Moyen court et très facile de faire oraison', author: '蓋恩夫人', era: '1685', place: '格勒諾布爾', language: '法文', intro: '蓋恩夫人教導人人皆可行的「單純注視」祈禱小書，主張放下自我意志沉入上帝臨在。書捲入寂靜主義論戰，作者繫獄巴士底而書遭禁毀，卻經芬乃倫與衛斯理傳入新教靈修血脈，是爭議與影響俱鉅的女性靈修經典。' },
          { title_zh: '屬靈爭戰', title_orig: 'Il combattimento spirituale', author: '羅倫佐‧斯庫波利', era: '1589', place: '威尼斯', language: '義大利文', intro: '戲阿蒂尼會士斯庫波利以「不信自己、全信上帝、善用身心、恆常祈禱」四兵器教導內心爭戰的手冊。沙雷氏的方濟終身攜之如聖經，東正教尼哥底母亦改編為《隱形爭戰》，是天主教與正教共尊的靈修兵法。' },
          { title_zh: '入德之門', title_orig: 'Introduction à la vie dévote', author: '方濟‧沙雷氏', era: '1609', place: '安錫', language: '法文', intro: '日內瓦主教沙雷氏為在俗貴婦「菲羅泰」寫的敬虔生活指南，主張虔敬不必出世，士兵、商婦、朝臣各按身分成聖。文筆溫雅如春風，刊行即風靡歐洲，是天主教改革「在俗成聖」靈修的定音之作。' },
          { title_zh: '宗教在靈魂中的興起與長進', title_orig: 'The Rise and Progress of Religion in the Soul', author: '腓力‧多德里奇', era: '1745', place: '北安普敦', language: '英文', intro: '不從國教牧者多德里奇追蹤靈魂自覺醒至成熟的階段指南，逐章附禱文。威伯福斯自承因本書歸正而投身廢奴，其教育與敬虔並重的路線影響福音派兩百年，是十八世紀英語靈修的代表作。' },
          { title_zh: '摩拉維亞每日箴言', title_orig: 'Die Losungen', author: '親岑多夫與赫恩胡特弟兄會', era: '1731 創刊', place: '赫恩胡特', language: '德文', intro: '親岑多夫自一七二八年起每日抽選聖句分發社區，一七三一年起印行為年冊《每日箴言》，抽籤定舊約句、配新約句與詩句，至今年年不輟、譯行數十語。近三百年無一日中斷的讀經日課，是敬虔運動最長壽的遺產。' },
          { title_zh: '朝聖者之路', title_orig: 'Откровенные рассказы странника', author: '佚名俄羅斯朝聖者', era: '約 1850–1860 年代', place: '俄羅斯（喀山刊 1881）', language: '俄文', intro: '佚名跛足朝聖者自述以「耶穌禱文」行遍俄羅斯的靈程記，把《慕善集》的心禱傳統化為道路上的故事。本書使不停息的耶穌禱文自修室走向大眾，二十世紀西傳後成為東正教靈修的世界名片。' },
          { title_zh: '聖潔之路', title_orig: 'The Way of Holiness', author: '菲比‧帕爾默', era: '1843', place: '紐約', language: '英文', intro: '衛理會平信徒婦女帕爾默以「祭壇神學」教導即時完全成聖：奉獻於壇、憑信宣告。她主持的週二聚會孕育聖潔運動，本書為其綱領，開女性講道與五旬節運動之先河，十九世紀美國靈修史的樞紐文獻。' },
          { title_zh: '天主聖教日課', title_orig: '天主聖教日課', author: '耶穌會士與中國奉教士人編訂', era: '約 1602–1638 定型', place: '北京／江南', language: '中文', intro: '晚明耶穌會與中國信徒合編的中文祈禱日課，將拉丁禱文譯為典雅文言，晨昏課、玫瑰經與諸聖禱文俱備。此書歷清代教難而抄傳不絕，行用至二十世紀，是漢語天主教敬禮傳統的根本文本。' },
          { title_zh: '禱告與默想書', title_orig: 'Libro de la oración y meditación', author: '路易斯‧德‧格拉納達', era: '1554', place: '里斯本', language: '西班牙文', intro: '道明會士格拉納達教導默想方法與材料的手冊，按週安排受難、死亡與天恩諸題。本書為十六世紀歐洲最暢銷書籍之一，譯成諸語逾百版，德蘭亦其讀者，卻一度被列禁書目錄，見證靈修普及與教權戒備的拉鋸。' },
          { title_zh: '肯恩主教禱文與頌歌手冊', title_orig: 'A Manual of Prayers... with Morning and Evening Hymns', author: '託馬斯‧肯恩', era: '1695', place: '溫徹斯特', language: '英文', intro: '不宣誓派主教肯恩為溫徹斯特公學學子編寫的禱告手冊，附其晨歌晚歌，末節「讚美真神萬福之源」成為英語世界傳唱最廣的三一頌。小書見證公學靈修傳統，一節頌歌則流入普世崇拜的血液。' },
          { title_zh: '隱形爭戰', title_orig: 'Ὁ Ἀόρατος Πόλεμος (Unseen Warfare)', author: '聖山的尼哥底母（改編斯庫波利）', era: '1796', place: '阿索斯聖山', language: '希臘文', intro: '聖山的尼哥底母把義大利靈修經典《屬靈爭戰》改編入東正教傳統，注入耶穌禱文與心禱教導，後經俄國隱修者提阿凡再訂。一部天主教手冊經正教兩度轉化而成《慕善集》傳統的姊妹篇，是跨傳統靈修交流的奇蹟文本。' }
        
        
        ]
      },
      {
        key: 'liturgical-scholarship',
        label: '禮儀學部',
        label_en: 'Liturgical Scholarship',
        desc: '近代禮儀源流考證與註釋——聖莫爾學派、義大利博學派與安立甘禮儀學的奠基著作。',
        works: [
          { title_zh: '斯帕羅公禱書釋義', title_orig: 'A Rationale upon the Book of Common Prayer', author: '安東尼‧斯帕羅', era: '1655', place: '劍橋', language: '英文', intro: '聖公會主教斯帕羅在公禱書遭禁的共和時期撰寫的逐項釋義，溯源古教會以辯護其合法。本書為公禱書註釋傳統的奠基作，王政復闢後屢刊不輟，是安立甘禮儀自我理解的經典文本。' },
          { title_zh: '論禮儀事務', title_orig: 'Rerum liturgicarum libri duo', author: '喬瓦尼‧博納', era: '1671', place: '羅馬', language: '拉丁文', intro: '熙篤會樞機博納考證彌撒禮儀源流的兩卷專著，遍稽抄本古籍而持論平允，兼具靈修家的溫度。本書開近代禮儀學實證研究之風，與其《引向天國之路》諸靈修作並傳，是十七世紀禮儀博學的代表。' },
          { title_zh: '高盧禮儀論', title_orig: 'De liturgia gallicana libri tres', author: '讓‧馬比雍', era: '1685', place: '巴黎聖日耳曼德佩修道院', language: '拉丁文', intro: '古文書學之父馬比雍據新發現抄本重構法蘭克教會古禮的專著，附呂克瑟伊經課書刊佈。本書把禮儀史研究奠於文獻批判之上，聖莫爾學派「以檔案治教會史」的典範，禮儀學作為科學的起點之一。' },
          { title_zh: '羅馬古禮儀集', title_orig: 'Liturgia Romana vetus', author: '洛多維科‧穆拉托里', era: '1748', place: '摩德納', language: '拉丁文', intro: '義大利史學巨匠穆拉托里輯刊羅馬古聖禮書的集成，收良俸、傑拉修與額我略三大聖事書並詳序考辨。本書使近代學界首度得窺特倫託以前的羅馬禮原貌，為禮儀溯源研究的標準史料庫。' },
          { title_zh: '彌撒禮儀史釋', title_orig: 'Explication littérale, historique et dogmatique des prières et des cérémonies de la messe', author: '皮埃爾‧勒布倫', era: '1716–1726', place: '巴黎', language: '法文', intro: '奧拉託利會士勒布倫以法語逐段解釋彌撒經文與儀節的四卷鉅著，兼比較東西方諸禮，考史而歸於奧義。本書把禮儀學識帶給識字信眾，是法國禮儀啟蒙的代表作，至今仍為彌撒史的重要參考。' },
          { title_zh: '東方禮儀集成', title_orig: 'Liturgiarum orientalium collectio', author: '歐塞布‧雷諾多', era: '1716', place: '巴黎', language: '拉丁文（譯自科普特／敘利亞文）', intro: '東方學家雷諾多輯譯科普特與敘利亞諸安納弗拉禱文的兩卷集成，首度讓西方系統得見東方聖餐禮的全幅譜系。本書為比較禮儀學的奠基文獻，後世論聖餐禱文源流者無不由此入手。' },
          { title_zh: '普世教會禮儀大全', title_orig: 'Codex liturgicus ecclesiae universae', author: '約瑟夫‧阿洛伊修斯‧阿瑟曼尼', era: '1749–1766', place: '羅馬', language: '拉丁文（多語文本）', intro: '馬龍派東方學世家阿瑟曼尼編纂的十三卷禮儀總集，東西方洗禮、按立、婚喪諸禮文並蓄，附考證。本書氣魄為禮儀文獻學空前，雖未竟全功，仍是十八世紀「普世禮儀知識」工程的最大紀念碑。' },
          { title_zh: '禮儀源流', title_orig: 'Origines liturgicae', author: '威廉‧帕爾默', era: '1832', place: '牛津', language: '英文', intro: '牛津學者帕爾默考證公禱書禮文上溯古教會源頭的專著，證安立甘禮儀承自初代傳統而非新創。本書直接滋養同年啟動的牛津運動，是聖公宗禮儀自覺與禮儀學復興的引爆文獻。' },
          { title_zh: '安立甘禮儀指南', title_orig: 'Directorium Anglicanum', author: '約翰‧珀奇斯（初版主編）', era: '1858', place: '倫敦', language: '英文', intro: '牛津運動禮儀派編纂的公禱書儀節指南，詳訂祭衣、燭光、鞠躬與香爐之用，附圖說。它把禮儀復興由書齋推向聖所，引發「儀式主義」訴訟浪潮，是十九世紀英國教會禮儀戰爭的核心手冊。' }
        
        ]
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
          { title_zh: '格哈特聖詩', title_orig: 'Geistliche Lieder Paul Gerhardts', author: '保羅‧格哈特', era: '1647–1667', place: '柏林／呂本', language: '德文', intro: '三十年戰爭世代的路德宗牧師格哈特寫下〈至聖之首受重傷〉〈把你的道路〉等聖詩百餘首，苦難中的信靠溫柔如晚禱。其詩經克呂格譜曲、巴哈引用而不朽，德語聖詩自客觀信條轉向內心信靠的分水嶺。' },
          { title_zh: '尼古拉雙頌歌', title_orig: 'Wachet auf / Wie schön leuchtet der Morgenstern', author: '菲利普‧尼古拉', era: '1599', place: '威斯特法倫翁納', language: '德文', intro: '瘟疫圍城中牧師尼古拉寫下〈醒來吧，守望者的聲音〉與〈晨星何等美麗〉，後世尊為「眾讚歌之王與後」。每週埋葬數十教友的絕境開出末世盼望的雙花，巴哈以之譜成同名清唱劇而傳唱不絕。' },
          { title_zh: '特斯特根聖詩', title_orig: 'Geistliches Blumengärtlein', author: '格哈德‧特斯特根', era: '1729', place: '米爾海姆', language: '德文', intro: '絲帶織工出身的平信徒密契者特斯特根的《屬靈花園》詩集，〈神在祂的聖殿中〉靜穆如深潭。他終身獨居講道慰苦，其詩把奧秘主義的靜默注入敬虔運動的歌唱，德語靈修詩的內向極品。' },
          { title_zh: '親岑多夫聖詩', title_orig: 'Lieder des Grafen Zinzendorf', author: '親岑多夫伯爵', era: '1725–1760', place: '赫恩胡特', language: '德文', intro: '摩拉維亞弟兄會領袖親岑多夫作詩兩千餘首，以「羔羊與其傷痕」的血與傷靈修直白熾烈，〈耶穌，你的寶血與義〉經衛斯理英譯而廣傳。其詩是敬虔運動情感宗教的極致，兼為循道會聖詩的接生婆。' },
          { title_zh: '諾瓦利斯靈歌', title_orig: 'Geistliche Lieder (Novalis)', author: '諾瓦利斯', era: '1799–1800', place: '魏森費爾斯', language: '德文', intro: '早夭的浪漫派詩人諾瓦利斯的十五首靈歌，以未婚妻之死的悲慟轉化為對基督的夜之戀慕，數首旋入德語聖詩集沿唱至今。浪漫主義與敬虔傳統的相遇，世俗化前夜歐洲宗教情感的迴光。' },
          { title_zh: '奧爾尼聖詩集', title_orig: 'Olney Hymns', author: '約翰‧牛頓與威廉‧古柏', era: '1779', place: '白金漢郡奧爾尼', language: '英文', intro: '前奴船船長牛頓與憂鬱詩人古柏為奧爾尼村禱告會合著的聖詩集，〈奇異恩典〉〈神蹟妙法〉皆出此帙。鄉村牧養的週週需用積成英語聖詩的礦脈，福音派會眾歌唱文化的奠基文獻。' },
          { title_zh: '威爾斯聖詩', title_orig: 'Emynau William Williams Pantycelyn', author: '潘特塞林的威廉‧威廉斯', era: '1744–1791', place: '威爾斯', language: '威爾斯文', intro: '威爾斯大復興的行吟詩人威廉斯作威爾斯語聖詩近千首，〈偉大耶和華，求你引導〉配〈布蘭溫德〉曲調成為民族的第二國歌。他使威爾斯成為「聖詩之邦」，凱爾特語聖詩傳統的最高峰。' },
          { title_zh: '託普雷迪聖詩', title_orig: 'Hymns of Augustus Toplady', author: '奧古斯都‧託普雷迪', era: '1776', place: '德文郡', language: '英文', intro: '加爾文派牧師託普雷迪的〈萬古磐石為我開〉相傳成於避雨巖穴，恩典的絕對性凝成四節詩行。他與衛斯理筆戰不休，其詩卻與對手之作同列英語聖詩最前排，教義之爭外的共同遺產。' },
          { title_zh: '希伯聖詩', title_orig: 'Hymns of Reginald Heber', author: '雷金納德‧希伯', era: '1811–1826', place: '什羅普郡／加爾各答', language: '英文', intro: '加爾各答主教希伯的聖詩集身後刊行，〈聖哉，聖哉，聖哉〉被譽為英語最完美的頌讚詩，宣教聖詩〈自格陵蘭冰山〉亦出其手。他以文學品味提升聖詩水準，開聖公會聖詩復興之先。' },
          { title_zh: '利特聖詩', title_orig: 'Hymns of Henry Francis Lyte', author: '亨利‧法蘭西斯‧利特', era: '1834–1847', place: '德文郡布里克瑟姆', language: '英文', intro: '漁村牧師利特臨終前數週寫成〈夕陽西沉（與我同住）〉，以垂死之目凝視不變的同在者。其〈讚美我靈〉為英王室婚禮頌歌，兩首詩使這位默默無聞的病牧成為英語臨終靈性的代言。' },
          { title_zh: '蒙哥馬利聖詩', title_orig: 'Hymns of James Montgomery', author: '詹姆斯‧蒙哥馬利', era: '1797–1854', place: '雪菲爾', language: '英文', intro: '摩拉維亞出身的報人蒙哥馬利兩度因言論繫獄，作聖詩四百餘首，〈天使歌唱在高天〉與〈禱告是靈魂的真誠願望〉傳唱至今。編輯檯與講壇之間的詩筆，見證聖詩與社會良知的結盟。' },
          { title_zh: '邦納聖詩', title_orig: 'Hymns of Horatius Bonar', author: '霍雷肖斯‧邦納', era: '1843–1889', place: '愛丁堡', language: '英文', intro: '蘇格蘭自由教會牧師邦納被稱「蘇格蘭聖詩王子」，〈我聽見耶穌柔聲說〉自福音的邀請寫出安息。長老宗原僅唱詩篇，其詩為蘇格蘭教會接納聖詩鋪路，福音派抒情傳統的北方代表。' },
          { title_zh: '克羅斯比福音詩歌', title_orig: 'Gospel Hymns of Fanny Crosby', author: '芬妮‧克羅斯比', era: '1864–1915', place: '紐約', language: '英文', intro: '失明的克羅斯比一生口述聖詩八千餘首，〈有福的確據〉〈榮耀歸於真神〉隨慕迪佈道傳遍世界。她以廉價稿酬濟貧民窟而自甘清寒，是福音詩歌時代最多產也最被傳唱的作者，女性聖詩史的巔峰。' },
          { title_zh: '艾略特聖詩', title_orig: 'Hymns of Charlotte Elliott', author: '夏洛特‧艾略特', era: '1834–1871', place: '布萊頓', language: '英文', intro: '久病不起的艾略特在自覺無用的黑夜寫下〈照我本相〉，「不待自潔，就我本相來」成為福音邀請的通用語言，葛培理大會以之呼召百萬人。病榻上的無力感化為最有力的詩，殘疾靈性的經典見證。' },
          { title_zh: '哈維格爾聖詩', title_orig: 'Hymns of Frances Ridley Havergal', author: '弗朗西絲‧哈維格爾', era: '1858–1879', place: '伍斯特郡', language: '英文', intro: '通曉六種語言的哈維格爾以〈奉獻身心〉把「將我的生命獻上」逐項數算至金銀與唇舌，並終身踐行變賣珠寶捐宣教。其「奉獻聖詩」定義了凱西克靈修運動的歌唱，維多利亞女性虔敬的代表聲音。' },
          { title_zh: '金戈聖詩', title_orig: 'Salmer af Thomas Kingo', author: '託馬斯‧金戈', era: '1674–1699', place: '丹麥歐登塞', language: '丹麥文', intro: '丹麥主教金戈的聖詩集為丹挪教會欽定歌本，受難詩沉鬱如北海冬濤，〈破曉金光〉則燦然生輝。他奠定丹麥語聖詩傳統，「金戈聖詩集」之名沿用至今，北歐巴洛克虔敬的第一詩筆。' },
          { title_zh: '格倫特維聖詩', title_orig: 'Salmer af N. F. S. Grundtvig', author: '尼古拉‧格倫特維', era: '1810–1872', place: '哥本哈根', language: '丹麥文', intro: '丹麥國父級神學家格倫特維作聖詩千餘首，以「活的話語」神學詠教會為古今信眾的相逢之家，〈教會是古老的房屋〉傳唱北歐。其聖詩與平民高校運動共同塑造丹麥的民族靈魂，聖詩作為民族教育的極致案例。' },
          { title_zh: '瓦林瑞典聖詩集', title_orig: 'Den svenska psalmboken 1819 (Wallin)', author: '約翰‧奧洛夫‧瓦林（主編）', era: '1819', place: '斯德哥爾摩', language: '瑞典文', intro: '日後的烏普薩拉大主教瓦林主編兼改寫的瑞典聖詩集，融正統、敬虔與啟蒙語彙於一爐，人稱「北方的大衛琴」。此集通行瑞典教會逾一世紀，是國教聖詩集編纂藝術的典範。' },
          { title_zh: '提拉克馬拉提聖詩', title_orig: 'Marathi Hymns of Narayan Vaman Tilak', author: '納拉揚‧瓦曼‧提拉克', era: '1895–1919', place: '印度馬哈拉施特拉', language: '馬拉提文', intro: '婆羅門詩人提拉克歸信後以馬拉提語的奉愛（bhakti）詩體寫基督讚歌數百首，自稱「印度的大門通往基督的是奉愛之路」。其詩至今為馬拉提教會主要歌本，福音本色化詩歌的先驅典範。' },
          { title_zh: '慈光導引', title_orig: 'Lead, Kindly Light (The Pillar of the Cloud)', author: '約翰‧亨利‧紐曼', era: '1833', place: '地中海船上', language: '英文', intro: '紐曼於西西里熱病初癒、歸舟困於風平的橙船上寫下的祈禱詩，「慈光導引，於幽暗中引我前行——我不求看見遠景，一步已足」。此詩成為英語世界最深入人心的信靠聖詩，維多利亞時代信仰徬徨的共同禱詞。' }
        
        
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
          { title_zh: '耶路撒冷的解放', title_orig: 'Gerusalemme liberata', author: '託爾誇託‧塔索', era: '1581', place: '費拉拉', language: '義大利文', intro: '塔索以第一次十字軍克復聖城為題的史詩，信仰的大義與騎士戀情交纏，成於特倫託時代的宗教焦慮之中。詩人晚年為正統疑懼而反覆自改，本詩仍成歐洲最後的偉大史詩之一，歌劇與繪畫取材不竭。' },
          { title_zh: '基督頌', title_orig: 'Christias', author: '馬爾科‧吉羅拉莫‧維達', era: '1535', place: '克雷莫納', language: '拉丁文', intro: '人文主義主教維達應教廷之望以維吉爾史詩體演述基督生平的六卷拉丁史詩，一時洛陽紙貴。它是文藝復興「以古典衣缽載福音」的代表工程，彌爾頓少作亦見其影，新拉丁宗教史詩的標竿。' },
          { title_zh: '創世週', title_orig: 'La Sepmaine ou Création du monde', author: '紀堯姆‧德‧薩呂斯特‧杜巴爾塔斯', era: '1578', place: '加斯科尼', language: '法文', intro: '胡格諾詩人杜巴爾塔斯以七日創世為綱的百科式史詩，融神學、博物與天文於頌讚，歐洲各語爭相翻譯，英譯本尤風行。彌爾頓承其餘緒，本詩是新教創世文學的第一座高峰。' },
          { title_zh: '仙后', title_orig: 'The Faerie Queene', author: '艾德蒙‧斯賓塞', era: '1590–1596', place: '倫敦／愛爾蘭', language: '英文', intro: '斯賓塞獻給伊莉莎白一世的寓言史詩，紅十字騎士護持「真理」尤娜的首卷即新教聖潔的寓言，反羅馬的意象貫穿全篇。它把宗教改革的屬靈爭戰譯為騎士傳奇，英語寓言詩傳統的巔峰。' },
          { title_zh: '鬥士參孫', title_orig: 'Samson Agonistes', author: '約翰‧彌爾頓', era: '1671', place: '倫敦', language: '英文', intro: '失明的彌爾頓以希臘悲劇體重寫失明的參孫，王政復闢後失敗的清教徒在囚徒的最後一搏中照見自身。「一切最好，雖然我們常疑惑」的收束句，是清教史詩傳統最沉痛的謝幕。' },
          { title_zh: '拉辛聖經悲劇', title_orig: 'Esther / Athalie', author: '讓‧拉辛', era: '1689／1691', place: '聖西爾', language: '法文', intro: '拉辛封筆多年後為聖西爾女校寫成的兩部聖經悲劇，《亞她利雅》以聖殿政變寫神意的隱密運行，被譽為法蘭西古典悲劇的絕頂。楊森派的恩典幽暗貫穿其間，世俗劇場向聖經敘事的最後鞠躬。' },
          { title_zh: '波利厄克特', title_orig: 'Polyeucte', author: '皮埃爾‧高乃依', era: '1643', place: '巴黎', language: '法文', intro: '高乃依以亞美尼亞殉道者波利厄克特為題的悲劇，新受洗者搗毀偶像慷慨赴死，妻子寶琳終亦皈依。恩典與榮譽的古典衝突在此以殉道超越，法蘭西古典主義處理信仰題材的最高成就。' },
          { title_zh: '卡爾德隆聖體劇', title_orig: 'El gran teatro del mundo (autos sacramentales)', author: '佩德羅‧卡爾德隆', era: '約 1635–1681', place: '馬德里', language: '西班牙文', intro: '卡爾德隆為聖體節廣場演出寫作聖體劇七十餘部，《世界大舞臺》以人生如戲喻造物主導演下的救恩。西班牙黃金時代把神學搬上街頭花車，本劇群是巴洛克公共宗教藝術的文學極致。' },
          { title_zh: '彌賽亞（克洛普施托克）', title_orig: 'Der Messias', author: '弗里德里希‧克洛普施托克', era: '1748–1773', place: '漢堡／哥本哈根', language: '德文', intro: '克洛普施托克以無韻六步格鋪陳救贖史的二十歌史詩，首三歌刊出即震動德語文壇，感傷的崇高開創德語詩新紀元。歌德筆下的少年維特與綠蒂共誦其名即泣，敬虔感性時代的文學紀念碑。' },
          { title_zh: '米開朗基羅宗教十四行詩', title_orig: 'Rime spirituali di Michelangelo', author: '米開朗基羅‧博納羅蒂', era: '約 1536–1560', place: '羅馬', language: '義大利文', intro: '晚年的米開朗基羅在十四行詩中懺悔藝術偶像化的一生，「繪畫與雕塑再不能安慰靈魂，唯有那在十字架上張臂的愛」。巨匠以詩卸下鑿刀的自白，文藝復興藝術宗教性的最深獨語。' },
          { title_zh: '科隆納靈性詩篇', title_orig: 'Rime spirituali di Vittoria Colonna', author: '維多利亞‧科隆納', era: '約 1538–1547', place: '羅馬／維泰博', language: '義大利文', intro: '寡居侯爵夫人科隆納的靈性十四行詩，唯獨恩典的暗流出入其間，與米開朗基羅的詩藝友誼傳為佳話。她是義大利福音派改革圈（spirituali）的中心人物，文藝復興女性宗教詩的第一名家。' },
          { title_zh: '夜思', title_orig: 'Night Thoughts', author: '愛德華‧楊格', era: '1742–1745', place: '赫特福德郡', language: '英文', intro: '喪妻失女的牧師楊格於長夜默想死亡、審判與永生的萬行無韻詩，風靡全歐半世紀，布雷克為之繪製巨幅插畫。「墓園詩派」以此為宗，啟蒙盛世裡死亡沉思的暗流主脈。' },
          { title_zh: '羅塞蒂宗教詩', title_orig: 'Religious Poems of Christina Rossetti', author: '克莉絲蒂娜‧羅塞蒂', era: '1862–1893', place: '倫敦', language: '英文', intro: '前拉斐爾派才女羅塞蒂兩度為信仰退婚，其宗教詩清冷如霜夜，〈在淒涼的隆冬〉譜曲後成聖誕經典。奉獻與剋制鍛出的詩藝，維多利亞女性宗教抒情的最純粹聲音。' },
          { title_zh: '傑隆修斯之夢（紐曼詩作）', title_orig: 'The Dream of Gerontius (poem)', author: '約翰‧亨利‧紐曼', era: '1865', place: '伯明罕', language: '英文', intro: '紐曼樞機描寫靈魂臨終過渡與煉淨之旅的長詩，守護天使的引領與「慈光」的迴響貫穿全篇。本詩使天主教末世想像重入英語文學主流，埃爾加據以譜成同名神劇，維多利亞宗教詩的壓卷。' },
          { title_zh: '惠特利詩集', title_orig: 'Poems on Various Subjects, Religious and Moral', author: '菲利斯‧惠特利', era: '1773', place: '波士頓／倫敦', language: '英文', intro: '被擄為奴的西非少女惠特利出版的詩集，為非裔美洲人第一部著作，頌詩與輓歌俱以福音盼望為底色。出版前須經波士頓名流「查驗」其真偽，本書的存在本身即是對奴役邏輯的詩學反駁。' },
          { title_zh: '頌上帝', title_orig: 'Бог (Ода)', author: '加夫里拉‧傑爾查文', era: '1784', place: '聖彼得堡', language: '俄文', intro: '俄國詩宗傑爾查文的頌詩《上帝》，自「我是蟲，我是神」的張力詠造物主的無限，譯成多語乃至傳入日本中國。俄語宗教抒情詩的開山名篇，普希金之前俄詩的最高峰。' },
          { title_zh: '約婚夫婦', title_orig: 'I promessi sposi', author: '亞歷山德羅‧曼佐尼', era: '1827（1842 定本）', place: '米蘭', language: '義大利文', intro: '曼佐尼歸信後寫成的歷史小說，瘟疫與強權下的平民婚約由天意迂迴成全，波羅梅奧樞機與悔改的「無名氏」為文學史最動人的恩典肖像。義大利國民小說，天主教敘事藝術的近代巔峰。' },
          { title_zh: '湯姆叔叔的小屋', title_orig: 'Uncle Tom\'s Cabin', author: '哈麗葉特‧比徹‧斯托', era: '1852', place: '緬因州', language: '英文', intro: '牧師之家出身的斯托夫人以基督式受難的黑奴湯姆控訴蓄奴制，首年售三十萬冊，林肯戲稱她「發動大戰的小婦人」。福音派良知寫成的小說撼動國史，宗教文學社會力量的最大案例。' },
          { title_zh: '賓虛：基督的故事', title_orig: 'Ben-Hur: A Tale of the Christ', author: '盧‧華萊士', era: '1880', place: '新墨西哥', language: '英文', intro: '南北戰爭將軍華萊士為查證信仰而寫成的耶穌時代小說，猶太王子的復仇之路終結於十字架下的饒恕。本書超越《湯姆叔叔的小屋》成為十九世紀美國最暢銷小說，聖經史詩文類的市場開創者。' },
          { title_zh: '你往何處去', title_orig: 'Quo Vadis', author: '亨利克‧顯克維奇', era: '1896', place: '華沙', language: '波蘭文', intro: '顯克維奇以尼祿迫害下的羅馬為場的殉道史詩小說，彼得城門外「主啊，你往何處去」一問回轉赴死。本書為作者摘下諾貝爾獎，譯成五十餘語，殉道敘事在現代大眾文學中的最大迴響。' },
          { title_zh: '紅字', title_orig: 'The Scarlet Letter', author: '納撒尼爾‧霍桑', era: '1850', place: '塞勒姆', language: '英文', intro: '霍桑以清教新英格蘭的通姦烙印剖開罪、恥與隱匿之罪的腐蝕，海絲特胸前的紅字終由恥辱繡成尊嚴。它是清教遺產的文學審判，美國小說處理罪與恩典的奠基之作。' },
          { title_zh: '悲慘世界', title_orig: 'Les Misérables', author: '維克多‧雨果', era: '1862', place: '根西島（流亡中）', language: '法文', intro: '雨果的鉅著以米里哀主教一對燭臺的饒恕開篇，苦役犯尚萬強的一生成為恩典改造人的長卷寓言。教會體制外的福音精神貫穿全書，十九世紀文學中最宏大的救贖敘事。' },
          { title_zh: '聖誕頌歌', title_orig: 'A Christmas Carol', author: '查爾斯‧狄更斯', era: '1843', place: '倫敦', language: '英文', intro: '狄更斯的聖誕小書使守財奴一夜之間被三靈引領悔改，「願上帝祝福我們每一個人」自此成為聖誕的公共祝詞。本書重塑了英語世界的聖誕想像，把節期靈性譯為城市時代的慈善倫理。' },
          { title_zh: '北風的背後', title_orig: 'At the Back of the North Wind', author: '喬治‧麥克唐納', era: '1871', place: '倫敦', language: '英文', intro: '蘇格蘭牧師麥克唐納的童話小說，馬夫之子小鑽石隨北風夜行，死亡化為溫柔的引路者。他開創基督教奇幻文類，路易斯自認「凡我所寫皆引用麥克唐納」，現代靈性奇幻的祖師之作。' },
          { title_zh: '聖戰', title_orig: 'The Holy War', author: '約翰‧班揚', era: '1682', place: '貝德福德', language: '英文', intro: '班揚以「人靈城」的失陷與光復寓言救贖史，沙代大王與魔王迪亞波羅斯反覆爭奪人心的城門。規模逾《天路歷程》而寓意更繁密，清教寓言文學的第二高峰。' },
          { title_zh: '三巴集', title_orig: '三巴集（天學詩）', author: '吳歷（漁山）', era: '約 1690–1718', place: '上海／澳門', language: '漢文', intro: '清初畫壇六大家之一吳歷入耶穌會為司鐸，以宋詩格律詠三位一體、聖體與澳門教會生活，結為《三巴集》。士大夫詩學與天主教義的真正融合首見於此，漢語基督教文學的開山詩集。' },
          { title_zh: '悼念集', title_orig: 'In Memoriam A.H.H.', author: '阿弗雷德‧丁尼生', era: '1850', place: '英格蘭', language: '英文', intro: '丁尼生為亡友哈勒姆寫作十七年的一百三十一首輓歌組詩，於地質學與演化陰影下追問不朽，「寧可愛過而失去」出於此。維多利亞女王喪偶後奉為聖經之次的安慰之書，信仰與懷疑角力的世紀之詩。' }
        
        
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
          { title_zh: '特拉赫恩世紀默想集', title_orig: 'Centuries of Meditations', author: '託馬斯‧特拉赫恩', era: '約 1670（1908 刊）', place: '赫裡福德', language: '英文', intro: '鄉村牧師特拉赫恩的默想散文湮沒二百餘年，二十世紀初自舊書攤重見天日，「麥浪是永恆的金黃」的童真視景震驚文壇。受造界的榮福直觀寫得如初晨，英語密契散文最喜樂的聲音。' },
          { title_zh: '燧石迸光', title_orig: 'Silex Scintillans', author: '亨利‧沃恩', era: '1650–1655', place: '威爾斯佈雷肯', language: '英文', intro: '威爾斯醫生詩人沃恩自赫伯特得火，內戰失敗與喪弟之慟擊出「燧石的火花」，〈我看見永恆如一環純光〉為英詩最著名的異象句。玄學派靈修詩的暮色高峰，浪漫主義自然靈視的遠源。' },
          { title_zh: '通往聖殿之階', title_orig: 'Steps to the Temple', author: '理查‧克拉肖', era: '1646', place: '劍橋／羅馬', language: '英文', intro: '克拉肖自聖公會轉入天主教流亡歐陸，其詩承大德蘭狂喜意象，〈燃燒的心〉炙熱如巴洛克祭壇。英語詩中最徹底的歐陸巴洛克感性，玄學派中孤懸的天主教一翼。' },
          { title_zh: '索爾‧胡安娜詩集', title_orig: 'Poemas de Sor Juana Inés de la Cruz', author: '索爾‧胡安娜‧伊內斯‧德‧拉‧克魯斯', era: '1680–1695', place: '墨西哥城', language: '西班牙文', intro: '新西班牙的修女詩人索爾‧胡安娜以《初夢》等詩兼攝神學與新科學，才名震動兩洋，終在教會壓力下售書櫃而封筆。「美洲第十繆斯」是殖民地女性求知權的殉道者，西語巴洛克的最亮星辰。' },
          { title_zh: '尼坎‧莫波瓦', title_orig: 'Nican Mopohua', author: '安東尼奧‧瓦萊裡亞諾（傳）', era: '約 1556（1649 刊）', place: '墨西哥谷', language: '納瓦特爾文', intro: '以納瓦特爾語記述瓜達盧佩聖母四度顯現於原住民胡安‧迭戈的敘事詩文，「我不在這裡嗎，我不是你的母親嗎」為美洲信仰的母語原點。原住民語言承載的顯現敘事，拉美宗教文學的第一文本。' },
          { title_zh: '危急時刻的禱告默想', title_orig: 'Devotions upon Emergent Occasions', author: '約翰‧多恩', era: '1624', place: '倫敦聖保羅座堂', language: '英文', intro: '聖保羅座堂主任多恩重病瀕死中逐日寫成的廿三段默想，「沒有人是孤島」「喪鐘為誰而鳴」皆出其中。病體成為神學的講章，英語散文以疾病默想存在的最高文本。' },
          { title_zh: '醫者的宗教', title_orig: 'Religio Medici', author: '託馬斯‧布朗', era: '1643', place: '諾裡奇', language: '英文', intro: '醫生布朗自剖信仰與科學共存之道的隨筆，寬容的懷疑與虔敬的驚奇交織，「我們裡面自有一個非洲與她的神奇」。本書風行歐陸而入禁書目錄，科學革命前夜信仰心靈的自畫像。' },
          { title_zh: '基督教年曆', title_orig: 'The Christian Year', author: '約翰‧基布爾', era: '1827', place: '牛津', language: '英文', intro: '基布爾按公禱書禮儀年逐主日配詩的詩集，半世紀刊行逾百版，為維多利亞家庭案頭必備。其含蓄溫潤的「保留」詩學預備了牛津運動的心靈土壤，禮儀年靈修詩的典範。' },
          { title_zh: '愛德華‧泰勒默想詩', title_orig: 'Preparatory Meditations', author: '愛德華‧泰勒', era: '1682–1725（1937 刊）', place: '麻薩諸塞西田', language: '英文', intro: '新英格蘭邊區牧師泰勒每逢聖餐前私撰默想詩，玄學派奇喻與清教聖餐虔敬交織，遺囑禁刊而沉睡二百年。二十世紀出土後被尊為殖民地美洲最偉大詩人，清教詩學的隱藏寶庫。' },
          { title_zh: '布拉茲特里特詩集', title_orig: 'The Tenth Muse / Poems of Anne Bradstreet', author: '安妮‧布拉茲特里特', era: '1650–1678', place: '麻薩諸塞', language: '英文', intro: '隨清教移民渡海的布拉茲特里特為英屬美洲第一位出版詩人，〈焚屋詩〉自灰燼仰望「天上更美的家業」。家務與荒野間寫就的信仰詩行，美洲女性文學與清教靈性的共同起點。' }
        
        ],
      },
      {
        key: 'sacred-art',
        label: '宗教藝術部',
        label_en: 'Sacred Art and Architecture',
        desc: '文藝復興至十九世紀的宗教繪畫、雕刻、版畫與教堂建築——自西斯汀天頂至聖家堂，兼及庫斯科畫派與瑪利亞觀音等非西方脈絡。',
        works: [
          { title_zh: '西斯汀聖母', title_orig: 'Madonna Sistina', author: '拉斐爾', era: '1512–1513', place: '羅馬（今藏德勒斯登）', language: '油畫（義大利）', intro: '拉斐爾為皮亞琴察修道院所繪的聖母抱子自雲端步出，下緣兩位小天使成為世界最著名的圖像之一。杜斯妥也夫斯基懸其摹本於書房凝視，稱之為人類理想之極，聖母像傳統的文藝復興頂點。' },
          { title_zh: '西斯汀禮拜堂天頂畫與最後審判', title_orig: 'Volta della Cappella Sistina / Giudizio Universale', author: '米開朗基羅', era: '1508–1512／1536–1541', place: '梵蒂岡', language: '濕壁畫（義大利）', intro: '米開朗基羅獨力繪成的創世天頂與晚年的最後審判，亞當指尖與審判者基督的旋風構成西方想像上帝與末日的視覺定本。教宗禮拜堂的牆面成為神學的公共記憶，基督教藝術的珠穆朗瑪。' },
          { title_zh: '伊森海姆祭壇畫', title_orig: 'Isenheimer Altar', author: '馬蒂亞斯‧格呂內瓦爾德', era: '約 1512–1516', place: '亞爾薩斯伊森海姆', language: '油畫（德意志）', intro: '為麥角中毒病患醫院所繪的多翼祭壇畫，釘痕潰爛的基督與燦爛的復活體並置，受苦者在祂身上看見自己的皮膚。醫療空間中的受難神學圖像，德意志藝術最震撼的十字架。' },
          { title_zh: '杜勒啟示錄木刻', title_orig: 'Apocalipsis cum figuris', author: '阿爾布雷希特‧杜勒', era: '1498', place: '紐倫堡', language: '木刻版畫（德意志）', intro: '杜勒自行出版的啟示錄十五幅大木刻，四騎士奔騰的構圖挾印刷術之力傳遍歐洲，末世想像自此有了標準畫面。藝術家自任出版者的第一案，版畫成為宗教大眾媒體的開端。' },
          { title_zh: '克拉納赫維滕堡祭壇畫', title_orig: 'Cranach-Altar der Stadtkirche Wittenberg', author: '老盧卡斯‧克拉納赫', era: '1547', place: '維滕堡', language: '油畫（德意志）', intro: '路德摯友克拉納赫為維滕堡城教堂繪製的宗教改革祭壇畫：聖餐、洗禮、告解三聯之下，路德講道手指十字架。以圖像申明「唯獨基督」的新教藝術綱領，改革陣營自己的祭壇神學。' },
          { title_zh: '聖馬太蒙召', title_orig: 'Vocazione di san Matteo', author: '卡拉瓦喬', era: '1599–1600', place: '羅馬聖王路易堂', language: '油畫（義大利）', intro: '卡拉瓦喬把稅吏蒙召畫進羅馬的昏暗賭室，一道側光沿基督的手指落在馬太錯愕的臉上。以市井寫實承載恩典的突襲，巴洛克明暗法的開山之作，至今仍懸於原委製的堂內小堂。' },
          { title_zh: '下十字架（魯本斯）', title_orig: 'De kruisafneming', author: '彼得‧保羅‧魯本斯', era: '1611–1614', place: '安特衛普主教座堂', language: '油畫（法蘭德斯）', intro: '魯本斯為安特衛普座堂繪製的三聯鉅作，慘白的基督沿斜貫的裹屍布滑落於眾手之間，力與慟一體。反宗教改革以藝術奪回感官的宣言，法蘭德斯巴洛克的祭壇典範。' },
          { title_zh: '浪子回頭（林布蘭）', title_orig: 'De terugkeer van de verloren zoon', author: '林布蘭‧範‧萊因', era: '約 1668', place: '阿姆斯特丹（今藏聖彼得堡）', language: '油畫（尼德蘭）', intro: '林布蘭絕筆期的浪子回頭：跪破鞋底的兒子埋首父懷，父親一雙手一剛一柔覆其背上。喪盡親財的畫家把一生的破碎畫進父愛，新教內在化信仰最深的圖像告白。' },
          { title_zh: '十字架上的基督（委拉斯奎茲）', title_orig: 'Cristo crucificado', author: '迭戈‧委拉斯奎茲', era: '約 1632', place: '馬德里', language: '油畫（西班牙）', intro: '委拉斯奎茲為修院所繪的十字架基督，漆黑背景中軀體靜穆如深夜的祭獻，垂髮半掩的面容引後世詩哲長吟。烏納穆諾為之作長詩，西班牙虔敬「靜默的基督」的視覺定像。' },
          { title_zh: '無染原罪（穆裡羅）', title_orig: 'La Inmaculada Concepción', author: '巴託洛梅‧穆裡羅', era: '約 1660–1678', place: '塞維亞', language: '油畫（西班牙）', intro: '穆裡羅一生繪無染原罪聖母二十餘幅，白衣藍帶、踏月而升的少女形象自此成為此端信理的通用圖式。塞維亞的甜美聖母走遍天下教堂與經卡，大眾聖母圖像的定稿者。' },
          { title_zh: '奧爾加斯伯爵的葬禮', title_orig: 'El entierro del conde de Orgaz', author: '埃爾‧格雷考', era: '1586–1588', place: '託萊多聖多默堂', language: '油畫（西班牙）', intro: '格雷考把地上葬禮與天上迎接疊為一畫：下層鐵甲貴族肅立，上層雲湧靈魂升入基督座前。拜占庭聖像訓練與威尼斯色彩在託萊多合體，天地兩界同框的殿堂級構圖。' },
          { title_zh: '聖德蘭的狂喜', title_orig: 'Estasi di Santa Teresa', author: '吉安‧洛倫佐‧貝尼尼', era: '1647–1652', place: '羅馬勝利之後聖母堂', language: '大理石雕刻（義大利）', intro: '貝尼尼把大德蘭自述的金箭刺心刻成大理石的暈眩瞬間，金光自暗窗傾瀉如天啟舞臺。密契經驗的可見化極限，巴洛克「總體藝術」小堂的教科書案例。' },
          { title_zh: '聖彼得大殿', title_orig: 'Basilica Sancti Petri (新堂)', author: '布拉曼特、米開朗基羅、貝尼尼等', era: '1506–1667', place: '梵蒂岡', language: '建築（義大利）', intro: '歷十六位教宗、一百六十年建成的新聖彼得大殿，米開朗基羅的穹頂與貝尼尼的柱廊擁抱普世。其募款贖罪券點燃宗教改革，其完工形塑天主教的世界形象，一座建築牽動整部近代教會史。' },
          { title_zh: '倫敦聖保羅座堂', title_orig: 'St Paul\'s Cathedral (Wren)', author: '克里斯多佛‧雷恩', era: '1675–1710', place: '倫敦', language: '建築（英格蘭）', intro: '倫敦大火後雷恩重建的聖保羅座堂，英格蘭巴洛克穹頂繼羅馬與君士坦丁堡而起，墓銘「欲尋其紀念碑，環顧四周即是」。新教國家的國家教堂典範，倫敦天際線三百年的錨點。' },
          { title_zh: '瓜達盧佩聖母聖像', title_orig: 'Tilma de Nuestra Señora de Guadalupe', author: '傳顯現於胡安‧迭戈斗篷', era: '1531', place: '墨西哥特佩亞克', language: '聖像（墨西哥）', intro: '傳為聖母顯現時印於原住民胡安‧迭戈龍舌蘭斗篷上的聖像，膚色黝黑、身佩阿茲特克象徵，五百年供奉於瓜達盧佩大殿。美洲皈依史的圖像原點，今日世界朝聖人次最多的聖像。' },
          { title_zh: '庫斯科畫派宗教繪畫', title_orig: 'Escuela cuzqueña', author: '安地斯原住民與混血畫師群', era: '17–18 世紀', place: '秘魯庫斯科', language: '油畫（安地斯）', intro: '西班牙畫師訓練的安地斯畫工自成一派：持火槍的天使、著印加服色的聖母、飲食羊駝的最後晚餐。歐洲圖式與安地斯宇宙觀的混血，殖民地藝術本色化最豐盛的果實。' },
          { title_zh: '瑪利亞觀音', title_orig: 'マリア観音（潜伏キリシタン聖像）', author: '日本隱匿基督徒社群', era: '17–19 世紀', place: '長崎／五島', language: '瓷像（日本）', intro: '禁教令下的日本信徒以白瓷觀音像暗奉聖母，佛龕深處藏十字，二百五十年口傳經文不輟。偽裝為生存的聖像學，長崎「潛伏切支丹」信仰韌性的無聲證物，今列世界遺產脈絡。' },
          { title_zh: '烏沙科夫聖像', title_orig: 'Иконы Симона Ушакова', author: '西蒙‧烏沙科夫', era: '1657–1686', place: '莫斯科兵器庫畫坊', language: '聖像（俄羅斯）', intro: '沙皇御用聖像師烏沙科夫在拜占庭平面傳統中引入西方明暗與立體感，「非人手所繪的救主」面容溫潤如生。俄國聖像由中世紀轉向近代的樞紐人物，傳統派與革新派論戰的焦點。' },
          { title_zh: '克里特畫派聖像', title_orig: 'Cretan School Icons (Theophanes the Cretan)', author: '克里特的狄奧法尼斯等', era: '16 世紀', place: '克里特／阿索斯／邁泰奧拉', language: '聖像（希臘）', intro: '拜占庭陷落後聖像傳統移居威尼斯治下的克里特，狄奧法尼斯為阿索斯與邁泰奧拉諸修道院繪製壁畫聖像，格雷考亦出此派。帝國亡而聖像不亡，後拜占庭藝術的黃金支脈。' },
          { title_zh: '孔戈尼亞斯先知群像', title_orig: 'Profetas de Congonhas', author: '阿萊雅迪尼奧（安東尼奧‧利斯博阿）', era: '1794–1804', place: '巴西米納斯吉拉斯', language: '皂石雕刻（巴西）', intro: '混血雕刻家阿萊雅迪尼奧晚年肢殘，工具縛於殘臂刻成善耶穌朝聖所前十二先知石像，巴洛克的戲劇性在美洲山巔迴旋。殖民地巴西藝術的最高成就，殘缺之軀的信仰雕刀。' },
          { title_zh: '聖母昇天（提香）', title_orig: 'Assunta', author: '提香', era: '1516–1518', place: '威尼斯聖方濟會榮耀聖母堂', language: '油畫（義大利）', intro: '提香為威尼斯方濟會大殿祭壇繪製的巨幅聖母昇天，紅衣聖母乘雲上騰、使徒仰臂如林。威尼斯畫派以色彩統攝神聖劇場的宣言，祭壇畫尺度與動勢的革命。' },
          { title_zh: '最後晚餐（丁託列託）', title_orig: 'Ultima Cena (San Giorgio Maggiore)', author: '丁託列託', era: '1592–1594', place: '威尼斯聖喬治馬焦雷堂', language: '油畫（義大利）', intro: '丁託列託臨終前完成的最後晚餐，餐桌斜插入畫、天使自油燈煙焰中湧現，聖體之光壓過達文西式的幾何靜穆。特倫託時代聖體敬禮的視覺神學，巴洛克動勢的先聲。' },
          { title_zh: '七聖事組畫', title_orig: 'Les Sept Sacrements', author: '尼古拉‧普桑', era: '1637–1642／1644–1648', place: '羅馬／巴黎', language: '油畫（法蘭西）', intro: '普桑兩度繪製七聖事組畫，以考古式的初代教會場景呈現洗禮至終傅，古典的莊嚴代替巴洛克的煽情。理性時代的聖事默想，法蘭西古典主義宗教畫的綱領之作。' },
          { title_zh: '山中十字架', title_orig: 'Das Kreuz im Gebirge (Tetschener Altar)', author: '卡斯帕‧大衛‧弗里德里希', era: '1808', place: '德勒斯登', language: '油畫（德意志）', intro: '弗里德里希把祭壇畫畫成夕照山巔的孤松十字，引發「風景豈可為祭壇」的著名論戰。自然成為啟示的聖所，浪漫主義宗教感的圖像宣言，現代「風景靈性」的起點。' },
          { title_zh: '拿撒勒畫派宗教壁畫', title_orig: 'Nazarener Fresken', author: '奧韋爾貝克、柯內留斯等', era: '1810–1830 年代', place: '羅馬／慕尼黑', language: '濕壁畫（德意志）', intro: '德意志青年畫家結社羅馬廢院，蓄髮如拿撒勒人，以復興拉斐爾前的虔誠壁畫為志。其復古理想主義影響前拉斐爾派與教堂藝術半世紀，浪漫時代宗教藝術復興運動的旗手。' },
          { title_zh: '晚禱（米勒）', title_orig: 'L\'Angélus', author: '讓-弗朗索瓦‧米勒', era: '1857–1859', place: '巴比松', language: '油畫（法蘭西）', intro: '暮色馬鈴薯田中，農民夫婦聞遠方鐘聲俯首誦三鐘經。米勒把農民勞動的尊嚴與日常虔敬凝為一幅，印刷複製品懸遍歐美農家，十九世紀最深入民間的宗教圖像。' },
          { title_zh: '世界之光（亨特）', title_orig: 'The Light of the World', author: '威廉‧霍爾曼‧亨特', era: '1851–1853', place: '牛津（凱布爾學院藏）', language: '油畫（英格蘭）', intro: '前拉斐爾派亨特繪基督提燈夜叩長滿荊蔓、無外把手的門，喻示心門唯能自內開啟。此畫巡迴英帝國各殖民地萬人爭睹，維多利亞時代最著名的佈道圖像，複製版懸於聖保羅座堂。' },
          { title_zh: '施諾爾圖畫聖經', title_orig: 'Die Bibel in Bildern', author: '尤利烏斯‧施諾爾‧馮‧卡羅斯費爾德', era: '1852–1860', place: '萊比錫', language: '木刻版畫（德意志）', intro: '拿撒勒派畫家施諾爾以二百四十幅木刻貫穿新舊約的圖畫聖經，構圖莊嚴如壁畫，各國翻印為主日學與家庭聖經的標準插圖。十九世紀聖經圖像的通用視覺辭典。' },
          { title_zh: '多雷聖經插畫', title_orig: 'La Sainte Bible illustrée par Gustave Doré', author: '古斯塔夫‧多雷', era: '1866', place: '巴黎', language: '木口木版畫（法蘭西）', intro: '多雷為大開本聖經繪製二百四十一幅插畫，光暗如歌劇、場面如史詩，自創世洪水至啟示錄烙入數代人的想像。至今電影的聖經場面仍脫不出其構圖，大眾聖經視覺化的總導演。' },
          { title_zh: '基督在父母家', title_orig: 'Christ in the House of His Parents', author: '約翰‧艾佛雷特‧米萊', era: '1849–1850', place: '倫敦', language: '油畫（英格蘭）', intro: '前拉斐爾派米萊把少年基督畫進滿地刨花的真實木匠舖，掌心的傷預表十架。狄更斯痛詆其「褻瀆的寫實」，論戰反使宗教畫的理想化傳統動搖，維多利亞宗教藝術寫實轉向的引爆點。' },
          { title_zh: '聖家堂', title_orig: 'Temple Expiatori de la Sagrada Família', author: '安東尼‧高第', era: '1882 動工（建造至今）', place: '巴塞隆納', language: '建築（加泰隆尼亞）', intro: '高第接手贖罪聖殿工程後以畢生獻之，樹狀石柱撐起如森林的中殿，誕生立面把福音刻滿石壁，自稱「為上帝工作不趕時間」。動工百四十年未竟而已列世遺，現代宗教建築的活的奇蹟。' }
        
        ]
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
          { title_zh: '論基督之言六篇講道', title_orig: 'Sei homilie sopra le parole di Iesu Christo', author: '貝內迪克‧圖瑞汀（Bénédict Turrettini，1588-1631）', era: '1623', place: '日內瓦（Geneva）', language: '義大利文', intro: '日內瓦改革宗牧師暨神學教授圖瑞汀以義大利文寫成的六篇講道集，逐篇默想基督的話語，向僑居日內瓦的義大利歸正信徒群體宣講。作者為盧卡流亡家族後裔、名神學家弗朗西斯‧圖瑞汀之父，曾將多特會議信條引入法國。本書屬十七世紀新教正統與敬虔交會時期的牧養講道，文字虔敬、辯才出眾，見證宗教改革後義語歸正講道傳統。' },
          { title_zh: '茨溫利講道與神學', title_orig: 'Predigten und Schriften (Huldrych Zwingli)', author: '烏爾裡希‧茨溫利', era: '1520 年代', place: '蘇黎世', language: '德文', intro: '蘇黎世改革家茨溫利逐卷連續講解聖經的講道與《論真假宗教》。改革宗連續解經講道的開創者，瑞士宗教改革的講壇奠基。' },
          { title_zh: '布靈格十講集', title_orig: 'Sermonum Decades quinque (Decades)', author: '海因裡希‧布靈格', era: '1549–1551', place: '蘇黎世', language: '拉丁文', intro: '茨溫利繼承者布靈格系統陳述改革宗信仰的五十篇講道，英格蘭教會列為教士必讀。改革宗教義講道的教科書，蘇黎世神學傳播歐洲的載體。' },
          { title_zh: '拉蒂默講道集', title_orig: 'Sermons (Hugh Latimer)', author: '休‧拉蒂默', era: '1548–1552', place: '倫敦', language: '英文', intro: '英格蘭改革家、殉道者拉蒂默痛斥社會不公的「犁頭講道」，御前直言無諱。都鐸英語講壇的良心之聲，火刑前「點亮永不熄滅之燭」名言的主人。' },
          { title_zh: '諾克斯講道與教會史', title_orig: 'The History of the Reformation in Scotland', author: '約翰‧諾克斯', era: '1560 年代', place: '愛丁堡', language: '英文（蘇格蘭語）', intro: '蘇格蘭改革家諾克斯的講道與宗教改革史，講壇雷霆撼動王座。蘇格蘭長老宗的奠基之聲，改革派政治講道的猛烈典型。' },
          { title_zh: '墨蘭頓講道範本', title_orig: 'Postilla Melanchthoniana', author: '菲利普‧墨蘭頓', era: '1540s', place: '維滕貝格', language: '拉丁文', intro: '路德的同工墨蘭頓為青年傳道人編寫的節期講道範本集。宗教改革講道教育的教材，路德宗講壇範式的傳播載體。' },
          { title_zh: '貝扎講道與神學', title_orig: 'Sermons sur l\'histoire de la Passion (Théodore de Bèze)', author: '泰奧多爾‧德‧貝扎', era: '1592', place: '日內瓦', language: '法文', intro: '加爾文繼承者貝扎論基督受難史的系列講道。日內瓦改革宗講壇的第二代宗師，法語改革宗講道傳統的鞏固者。' },
          { title_zh: '布塞珥講道與牧養論', title_orig: 'Von der waren Seelsorge (Martin Bucer)', author: '馬丁‧布塞珥', era: '1538', place: '斯特拉斯堡', language: '德文', intro: '斯特拉斯堡改革家布塞珥論真牧養職分的著作與講道。改革宗牧養神學的奠基文獻，加爾文與英國改革的橋樑人物。' }
        
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
          { title_zh: '天堂被風暴奪取', title_orig: 'Heaven Taken by Storm', author: 'Thomas Watson', era: '1669', place: '倫敦', language: '英文', intro: '托馬斯‧華特遜（1620–1686）著，清教運動中期倫敦威斯敏斯德禮拜堂牧師的代表講道集。以馬太福音 11:12「天堂被風暴奪取」為題，論述信仰的熱忱與屬靈爭戰；融合加爾文宗精微的約德論與經驗主義敬虔，是英文清教宣教傳統的典範著作，深刻影響後世新教講道學與靈命塑造。' },
          { title_zh: '歐文屬靈心思講道', title_orig: 'Sermons (John Owen)', author: '約翰‧歐文', era: '1650s–1680s', place: '英格蘭', language: '英文', intro: '清教神學巨擘歐文論屬靈心思與治死罪惡的講章。清教講壇的思想高峰，改革宗經驗神學的講道結晶。' },
          { title_zh: '福萊威講道集', title_orig: 'The Fountain of Life (John Flavel)', author: '約翰‧福萊威', era: '1671', place: '英格蘭達特茅斯', language: '英文', intro: '清教牧者福萊威論基督救贖之工的四十二篇講道。清教基督論講道的名著，牧養溫度與教義深度兼具的代表作。' },
          { title_zh: '愛德華滋神聖之美講道', title_orig: 'A Divine and Supernatural Light', author: '約拿單‧愛德華滋', era: '1734', place: '北安普頓', language: '英文', intro: '愛德華滋論屬靈之光直接照亮人心的講道，大覺醒的神學宣言。美洲清教講壇的哲思巔峰，宗教情感論的講道原型。' },
          { title_zh: '戴維斯維吉尼亞講道', title_orig: 'Sermons on Important Subjects (Samuel Davies)', author: '塞繆爾‧戴維斯', era: '1750s', place: '維吉尼亞', language: '英文', intro: '維吉尼亞長老會佈道家戴維斯向白人與黑奴同時傳道的講章。南方大覺醒的代表之聲，最早向奴隸群體大規模宣教的講壇。' },
          { title_zh: '厄斯金兄弟福音講道', title_orig: 'Sermons (Ebenezer and Ralph Erskine)', author: '厄本尼澤與拉爾夫‧厄斯金', era: '1720s–1750s', place: '蘇格蘭', language: '英文（蘇格蘭語）', intro: '蘇格蘭分立教會的厄斯金兄弟論白白恩典的福音講道。蘇格蘭福音復興的講壇代表，「馬羅神學」爭議的核心人物。' },
          { title_zh: '羅蘭‧希爾露天佈道', title_orig: 'Village Dialogues and Sermons (Rowland Hill)', author: '羅蘭‧希爾', era: '1770s–1830s', place: '倫敦', language: '英文', intro: '跨宗派露天佈道家羅蘭‧希爾風趣動人的講章與村談。福音派巡迴佈道的名家，主日學與宣教運動的推手。' },
          { title_zh: '李維香格里高蘇格蘭復興講道', title_orig: 'Sermons of the Kilsyth and Dundee Revival (W. C. Burns / M\'Cheyne)', author: '羅伯特‧默裡‧麥克謙', era: '1839–1843', place: '蘇格蘭鄧迪', language: '英文', intro: '蘇格蘭青年牧者麥克謙聖潔動人的講道與書信，鄧迪復興的核心。十九世紀蘇格蘭奮興的聖徒典範，其屬靈日記傳頌至今。' }
        
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
        
          { title_zh: '吸引萬民歸依真教之唯一方式', title_orig: 'De unico vocationis modo omnium gentium ad veram religionem', author: '拉斯卡薩斯（Bartolomé de las Casas）', era: '約1537年', place: 'Mexico', language: '拉丁文', intro: '西班牙道明會士、恰帕斯主教拉斯卡薩斯（1484–1566）約於1537年寫成本書，現存第一部分。論旨鮮明：基督教傳教的唯一合法途徑是以理性說服與仁愛感召，而非武力征服。作者以《新約》福音書為基礎，系統駁斥暴力佈道之合理性，並直指西班牙殖民征服對原住民的不義。本書是天主教傳教神學史上最早的護教人道主義文獻之一，對近代宗教寬容論與傳教倫理學影響深遠。' },
          { title_zh: '愛德華滋敘利亞宣教講道', title_orig: 'Sermons to the Nestorians (Justin Perkins tradition)', author: '賈斯汀‧珀金斯與波斯本地傳道', era: '1834–1869', place: '波斯烏爾米耶', language: '新敘利亞文', intro: '美部會在波斯向東方教會（景教後裔）宣教、以新敘利亞文所作的講章與見證。中東本土古教會的復興嘗試，新敘利亞文書面化的宣教成果。' },
          { title_zh: '克勞瑟約魯巴宣教日誌', title_orig: 'Journals (Samuel Ajayi Crowther)', author: '塞繆爾‧阿賈伊‧克勞瑟', era: '1843–1864', place: '奈及利亞尼日河', language: '英文／約魯巴文', intro: '獲釋奴隸、首位非裔聖公會主教克勞瑟溯尼日河宣教的日誌與講道，並譯約魯巴語聖經。非洲人宣教非洲的典範，本土主教制與本色化的先驅之聲。' },
          { title_zh: '馬士曼印度宣教與譯經', title_orig: 'Missionary Labours (Joshua Marshman)', author: '約書亞‧馬士曼', era: '1799–1837', place: '印度塞蘭坡', language: '英文／孟加拉文', intro: '塞蘭坡三傑之一馬士曼在孟加拉宣教、辦學與譯經的記述。近代印度宣教與本土語文教育的奠基，亞洲宣教方法論的實踐樣本。' },
          { title_zh: '李文斯頓宣教旅行記', title_orig: 'Missionary Travels and Researches in South Africa', author: '大衛‧李文斯頓', era: '1857', place: '倫敦', language: '英文', intro: '李文斯頓橫越非洲、以宣教與反奴貿易並舉的旅行記述。維多利亞時代非洲宣教的象徵，「基督教、商業與文明」宣教觀的代表。' },
          { title_zh: '郭士立中國沿海佈道記', title_orig: 'Journal of Three Voyages along the Coast of China', author: '郭實獵（郭士立）', era: '1834', place: '廣州', language: '英文', intro: '郭實獵沿中國海岸散發福音書冊的佈道航行記，倡本土傳道人先鋒之議。近代來華宣教方法的爭議樣本，福漢會與華人佈道網絡的先聲。' },
          { title_zh: '賓威廉客旅講道', title_orig: 'Sermons and Chinese Preaching (William Chalmers Burns)', author: '賓為霖', era: '1847–1868', place: '廈門／汕頭／北京', language: '英文／漢文', intro: '英國長老會宣教士賓為霖深入民間、以漢語佈道並譯《天路歷程》的講道與書信。以身作則融入華人的宣教典範，感召戴德生的屬靈前輩。' }
        
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
      {
        key: 'catholic-preaching',
        label: '天主教講壇部',
        label_en: 'Catholic Pulpit',
        desc: '近代天主教經典講道、追思演說與默想講章，法國古典講壇與伊比利亞、拉美講道傳統並收。',
        works: [
          { title_zh: '博須埃追思演說集', title_orig: 'Oraisons funèbres', author: '雅克‧博須埃', era: '1669–1687', place: '巴黎', language: '法文', intro: '莫城主教博須埃為王后與親王所作的追思演說，「夫人將死，夫人已死」一句震動全法。法國古典講壇的巔峰，將死亡與人世虛榮化為莊嚴詩篇的雄辯典範。' },
          { title_zh: '博須埃四旬期講道集', title_orig: 'Sermons de Carême', author: '雅克‧博須埃', era: '1660 年代', place: '巴黎', language: '法文', intro: '博須埃在羅浮宮御前所講的四旬期系列講章，論死亡、財富與良心，宮廷肅然。太陽王時代講壇雄辯的樣板，古典法語散文的錘鍊之地。' },
          { title_zh: '布爾達盧道德講道集', title_orig: 'Sermons (Bourdaloue)', author: '路易‧布爾達盧', era: '1670 年代', place: '巴黎', language: '法文', intro: '耶穌會士布爾達盧邏輯縝密、直刺良心的道德講章，聽眾自覺被逐一點名。「講壇的理性之王」，與博須埃並峙的法國古典講道雙峰。' },
          { title_zh: '馬西雍講道集', title_orig: 'Sermons (Massillon)', author: '讓‧巴蒂斯特‧馬西雍', era: '1699–1718', place: '巴黎', language: '法文', intro: '克萊蒙主教馬西雍柔和動人的講章，御前「小齋期」講道令路易十五為之動容。法國古典講壇的抒情一翼，伏爾泰譽其文體為法語散文典範。' },
          { title_zh: '維埃拉講道集', title_orig: 'Sermões (António Vieira)', author: '安東尼奧‧維埃拉', era: '1655–1697', place: '巴西馬拉尼昂／里斯本', language: '葡萄牙文', intro: '耶穌會士維埃拉在巴西為原住民與非洲奴隸疾呼、痛斥奴役者的講章，「聖安東尼向魚講道」寓意諷世。巴洛克葡語講壇的巔峰，殖民地良心的雄辯之聲。' },
          { title_zh: '路易斯講道與默想', title_orig: 'Obras (Fray Luis de Granada)', author: '格拉納達的路易斯', era: '1554–1588', place: '里斯本／格拉納達', language: '西班牙文', intro: '道明會士格拉納達的路易斯的講道與默想著作，《祈禱與默想之書》風行天主教世界。西班牙黃金時代靈修講道的大師，講道術與默觀傳統的集成者。' },
          { title_zh: '阿維拉的若望書信與講道', title_orig: 'Audi filia y Sermones (Juan de Ávila)', author: '阿維拉的若望', era: '16 世紀', place: '安達盧西亞', language: '西班牙文', intro: '「安達盧西亞的使徒」阿維拉的若望的講道與屬靈書信，影響大德蘭與方濟沙雷。西班牙教區傳道復興的推手，天主教改革講壇的靈修導師。' },
          { title_zh: '塞涅裡四旬期講道集', title_orig: 'Quaresimale (Paolo Segneri)', author: '保羅‧塞涅裡', era: '17 世紀', place: '義大利', language: '義大利文', intro: '耶穌會士塞涅裡赤足巡迴義大利鄉間佈道的四旬期講章，樸實動人催人悔改。義大利民間傳道復興的代表，巴洛克天主教巡迴佈道的典範。' },
          { title_zh: '拉科代爾聖母院講演集', title_orig: 'Conférences de Notre-Dame de Paris', author: '亨利‧拉科代爾', era: '1835–1851', place: '巴黎', language: '法文', intro: '重振法國道明會的拉科代爾在巴黎聖母院向青年知識分子的護教講演，座無虛席。革命後天主教講壇復興的號角，信仰與自由對話的十九世紀典範。' },
          { title_zh: '紐曼講道集', title_orig: 'Parochial and Plain Sermons', author: '若望‧亨利‧紐曼', era: '1834–1843', place: '牛津', language: '英文', intro: '紐曼任牛津聖母堂牧者時的講章，內省深邃、文辭清澈，牛津運動的靈魂之聲。英語講道文學的高峰，其後皈依羅馬前的心路詩篇。' },
          { title_zh: '費內隆屬靈書信與講道', title_orig: 'Œuvres spirituelles (Fénelon)', author: '弗朗索瓦‧費內隆', era: '1690s–1710s', place: '康佈雷', language: '法文', intro: '康佈雷總主教費內隆論純愛與內在生活的屬靈書信與講道。法國寂靜主義爭議的中心，天主教靈修講道的溫柔一脈。' },
          { title_zh: '沙雷的方濟講道與勸勉', title_orig: 'Sermons et entretiens (François de Sales)', author: '沙雷的方濟', era: '1600s–1620s', place: '日內瓦／安錫', language: '法文', intro: '《成聖捷徑》作者沙雷的方濟溫和平易、面向平信徒的講道與勸勉。天主教改革後平信徒靈修的推手，溫柔講道傳統的宗師。' },
          { title_zh: '聖文生‧德‧保祿使命講道', title_orig: 'Conférences (Vincent de Paul)', author: '文生‧德‧保祿', era: '1630s–1650s', place: '巴黎', language: '法文', intro: '遣使會創立者文生‧德‧保祿向鄉間窮人與傳教士的樸實講道與訓話。天主教社會關懷講壇的典範，鄉村使命與慈善事業的靈魂。' },
          { title_zh: '利古裡的亞豐索講道與默想', title_orig: 'Opere (Alfonso Maria de\' Liguori)', author: '利古裡的亞豐索', era: '18 世紀', place: '那不勒斯', language: '義大利文', intro: '贖主會創立者亞豐索論救贖大愛與聖母的講道與默想，《永生的準備》風行。天主教民間靈修的大師，倫理神學與講壇並重的教會聖師。' }
        
        ],
      },
      {
        key: 'pietist-holiness',
        label: '敬虔與成聖講道部',
        label_en: 'Pietist and Holiness Preaching',
        desc: '德語敬虔運動、莫拉維亞與英美成聖運動的講道與勸修文獻。',
        works: [
          { title_zh: '阿恩特真基督教', title_orig: 'Vier Bücher vom wahren Christentum', author: '約翰‧阿恩特', era: '1605–1610', place: '布倫瑞克', language: '德文', intro: '阿恩特論內在重生與效法基督的四卷勸修書，敬虔運動的靈修母本。路德宗最暢銷的靈修經典之一，斯佩納與衛斯理皆蒙其澤。' },
          { title_zh: '弗蘭克講道與孤院見證', title_orig: 'Segensvolle Fußstapfen (August Hermann Francke)', author: '奧古斯特‧赫爾曼‧弗蘭克', era: '1701', place: '哈勒', language: '德文', intro: '弗蘭克記述哈勒孤兒院憑信心興辦的見證與講道，敬虔付諸慈善事業。敬虔運動社會實踐的典範文獻，近代信心事工與宣教機構的先聲。' },
          { title_zh: '親岑多夫講道集', title_orig: 'Reden (Nikolaus Ludwig von Zinzendorf)', author: '親岑多夫伯爵', era: '18 世紀', place: '黑恩胡特', language: '德文', intro: '莫拉維亞弟兄會領袖親岑多夫論「心的宗教」與基督寶血的講道。近代普世宣教的先驅之聲，衛斯理靈性轉折的推手，情感敬虔的代表。' },
          { title_zh: '芬尼奮興講座', title_orig: 'Lectures on Revivals of Religion', author: '查爾斯‧芬尼', era: '1835', place: '紐約', language: '英文', intro: '奮興佈道家芬尼論如何促成復興的講座，新measures引發神學爭議。美國第二次大覺醒的方法論宣言，現代佈道術的爭議源頭。' },
          { title_zh: '凱瑟琳‧布思女性佈道論', title_orig: 'Female Ministry', author: '凱瑟琳‧布思', era: '1859', place: '倫敦', language: '英文', intro: '救世軍「軍母」布思為女性講道權辯護的小冊與講道，力主女子同得聖召。救世軍男女平等事奉的神學基石，維多利亞時代女性講壇的宣言。' },
          { title_zh: '慕迪佈道講章', title_orig: 'Sermons (Dwight L. Moody)', author: '德懷特‧慕迪', era: '1875–1899', place: '芝加哥／倫敦', language: '英文', intro: '鞋商出身的佈道家慕迪平白懇切、以愛為題的大型佈道講章，桑基聖詩相和。近代城市佈道會的原型，跨大西洋福音運動的代表人物。' },
          { title_zh: '司布真講壇', title_orig: 'The Metropolitan Tabernacle Pulpit', author: '查爾斯‧司布真', era: '1855–1892', place: '倫敦', language: '英文', intro: '「講道王子」司布真在倫敦大會堂逐週講道的講章結集，數千篇風行全球。維多利亞時代最偉大的講壇，改革宗福音講道的文字寶庫。' },
          { title_zh: '貝裡奇鄉村佈道', title_orig: 'The Christian World Unmasked (John Berridge)', author: '約翰‧貝裡奇', era: '1773', place: '英格蘭埃弗頓', language: '英文', intro: '福音派巡迴佈道家貝裡奇詼諧懇切的鄉村講道。英格蘭福音復興的草根之聲，衛斯理與懷特腓的同工。' },
          { title_zh: '波士頓生命之道', title_orig: 'Human Nature in its Fourfold State (Thomas Boston)', author: '託馬斯‧波士頓', era: '1720', place: '蘇格蘭埃特里克', language: '英文（蘇格蘭語）', intro: '蘇格蘭牧者波士頓論人性四境（無罪、墮落、恩典、榮耀）的講道結集。蘇格蘭平民神學的經典，鄉村講壇教義教育的典範。' },
          { title_zh: '弗萊契爾論成聖', title_orig: 'Checks to Antinomianism (John Fletcher)', author: '約翰‧弗萊契爾', era: '1771–1775', place: '英格蘭馬德利', language: '英文', intro: '衛斯理的神學繼承人弗萊契爾論成聖與反律法主義的辯護文集。循道神學的系統化奠基，衛斯理主義成聖論的權威闡釋。' }
        
        ],
      },
      {
        key: 'african-american-preaching',
        label: '非裔美洲講道部',
        label_en: 'African American Preaching',
        desc: '近代非裔美洲教會的講道、靈歌與見證，奴役與解放處境下的信仰之聲。',
        works: [
          { title_zh: '艾倫非洲衛理講道與生平', title_orig: 'The Life Experience and Gospel Labors of Richard Allen', author: '理查‧艾倫', era: '1833', place: '費城', language: '英文', intro: '獲釋奴隸、非洲衛理聖公會創立者艾倫的講道與自傳。黑人自主教會的奠基之聲，非裔美洲講壇傳統的源頭文獻。' },
          { title_zh: '海恩斯講道集', title_orig: 'Sermons (Lemuel Haynes)', author: '萊繆爾‧海恩斯', era: '1785–1820', place: '佛蒙特', language: '英文', intro: '美國首位受按立的非裔牧者海恩斯的講章，牧養白人會眾並論奴隸與自由。革命時代黑人講壇的先聲，加爾文主義與廢奴良心的結合。' },
          { title_zh: '耶麗娜‧李講道與靈程記', title_orig: 'The Life and Religious Experience of Jarena Lee', author: '耶麗娜‧李', era: '1836', place: '費城', language: '英文', intro: '非洲衛理聖公會首位女講道者耶麗娜‧李的巡迴佈道自述，跨越性別與種族雙重藩籬。黑人女性講壇的破冰之作，十九世紀美國宗教史的獨特之聲。' },
          { title_zh: '賈斯珀「日頭果然行動」講道', title_orig: 'De Sun Do Move (John Jasper)', author: '約翰‧賈斯珀', era: '約 1878', place: '里奇蒙', language: '英文', intro: '獲釋奴隸賈斯珀以民間語言演繹聖經、講「日頭果然行動」的名篇。非裔口傳講道藝術的代表，民間釋經與修辭激情的活標本。' },
          { title_zh: '特納非洲宣教講道', title_orig: 'Sermons and Addresses (Henry McNeal Turner)', author: '亨利‧麥克尼爾‧特納', era: '1868–1900', place: '喬治亞／賴比瑞亞', language: '英文', intro: '非洲衛理主教特納論黑人尊嚴、「上帝是黑人」與返非宣教的講道。重建時代黑人講壇的政治之聲，非裔美洲返非運動的宗教旗手。' },
          { title_zh: '阿曼達‧史密斯佈道自述', title_orig: 'An Autobiography (Amanda Berry Smith)', author: '阿曼達‧貝裡‧史密斯', era: '1893', place: '美國／印度／賴比瑞亞', language: '英文', intro: '獲釋奴隸出身的成聖佈道家阿曼達‧史密斯橫跨美印非三洲的佈道自述。黑人女性跨國宣教的傳奇，聖潔運動與世界宣教的交會之聲。' },
          { title_zh: '索傑納‧特魯斯見證與演說', title_orig: 'Narrative of Sojourner Truth', author: '索傑納‧特魯斯', era: '1850', place: '美國', language: '英文', intro: '獲自由的女奴、巡迴佈道家特魯斯的見證與「我豈不是女人」演說。廢奴與女權交會的先知之聲，非裔女性講壇的傳奇人物。' },
          { title_zh: '艾伯薩隆‧瓊斯感恩講道', title_orig: 'A Thanksgiving Sermon (Absalom Jones)', author: '艾伯薩隆‧瓊斯', era: '1808', place: '費城', language: '英文', intro: '首位非裔聖公會牧者瓊斯慶祝廢除奴隸貿易的感恩講道。黑人聖公會的奠基之聲，以出埃及記詮釋黑人解放的早期範例。' }
        
        ],
      },
      {
        key: 'chinese-preaching',
        label: '漢語宣道部',
        label_en: 'Chinese-Language Preaching',
        desc: '近代華人佈道家與本土傳道人的講章、勸世文與見證，漢語基督教宣道的自立之聲。',
        works: [
          { title_zh: '梁發勸世良言', title_orig: '勸世良言', author: '梁發', era: '1832', place: '廣州', language: '漢文', intro: '華人首位牧師梁發輯譯聖經與自撰講論而成的佈道文集，洪秀全得之而萌拜上帝之念。華人自撰宣道文獻的開山之作，深刻牽動太平天國與近代中國史。' },
          { title_zh: '何進善訓真篇', title_orig: '訓真篇', author: '何進善（何福堂）', era: '約 1852', place: '香港', language: '漢文', intro: '華人早期牧者何進善以文言撰寫的護教勸世論著，析辨真道以曉華人。華南本土傳道文獻的代表，倫敦會華人自立傳道的早期成果。' },
          { title_zh: '席勝魔悔改見證與詩歌', title_orig: '席勝魔傳道見證', author: '席勝魔（席子直）', era: '約 1880–1896', place: '山西', language: '漢文', intro: '由秀才、鴉片癮者轉為佈道家的席勝魔戒煙傳道的見證與自撰詩歌，設戒煙所遍山西。內地會華人佈道的傳奇，本土奮興與社會改造結合的典型。' },
          { title_zh: '王元深聖道東來考', title_orig: '聖道東來考', author: '王元深', era: '1899', place: '廣東', language: '漢文', intro: '巴色會華人牧者王元深考述基督教東傳源流的著作，兼含佈道與教會史。客家教會本土書寫的先聲，華人自述信仰源流的早期嘗試。' },
          { title_zh: '謝洪賚勸學與佈道文', title_orig: '謝洪賚文集', author: '謝洪賚', era: '1890 年代', place: '上海', language: '漢文', intro: '清末華人基督徒學者謝洪賚融會西學與信仰的講論與勸學文字。士人型華人佈道的代表，教育救國與福音傳播並行的知識分子之聲。' },
          { title_zh: '俞國楨自立會講章', title_orig: '中國耶穌教自立會講論', author: '俞國楨', era: '1900 前後', place: '上海', language: '漢文', intro: '倡導華人教會自立自養的俞國楨的講章與主張，脫離差會而自組教會。華人教會三自運動的先聲，本色化與教會自主的早期論述。' },
          { title_zh: '賓為霖廈語佈道文', title_orig: '廈門白話佈道文（賓為霖與本地傳道）', author: '賓為霖與閩南本地傳道人', era: '1850 年代', place: '廈門', language: '閩南白話字', intro: '以閩南白話字寫就的佈道講章與勸信文，供不識漢字的信徒誦讀。方言宣道文獻的代表，白話字識字運動與本土傳道結合的產物。' },
          { title_zh: '倪柝聲前身：福州本土講道', title_orig: '福州美以美會華人講章', author: '福州華人傳道群', era: '1870–1900', place: '福州', language: '漢文／福州話', intro: '福州美以美會華人傳道人以官話與福州話所作的講章結集。華東本土講壇的縮影，方言與官話並用的宣道實態見證。' }
        
        ],
      },
      {
        key: 'orthodox-anglican-pulpit',
        label: '正教與聖公會講壇部',
        label_en: 'Orthodox and Anglican Pulpit',
        desc: '近代東正教與英國國教講壇名家的講道與默想，禮儀傳統中的講道藝術。',
        works: [
          { title_zh: '扎東斯克的季洪講道與默想', title_orig: 'Сочинения (Тихон Задонский)', author: '扎東斯克的季洪', era: '18 世紀', place: '俄羅斯扎東斯克', language: '俄文', intro: '俄國主教聖季洪論真基督教與屬靈爭戰的講道與默想，杜斯妥也夫斯基筆下佐西馬長老之原型。俄國正教靈修講道的高峰，東方敬虔文學的代表。' },
          { title_zh: '莫斯科的斐拉列特講道集', title_orig: 'Слова и речи (Филарет Московский)', author: '莫斯科的斐拉列特', era: '19 世紀', place: '莫斯科', language: '俄文', intro: '莫斯科都主教斐拉列特莊重深湛的講道與《東正教基督教教理問答》。十九世紀俄國教會的思想中樞，正教講壇與教理教育的權威之聲。' },
          { title_zh: '羅斯托夫的季米特里講道與聖傳', title_orig: 'Четьи-Минеи (Димитрий Ростовский)', author: '羅斯托夫的季米特里', era: '1684–1705', place: '羅斯托夫', language: '教會斯拉夫文', intro: '羅斯托夫都主教季米特里編纂的聖徒月課大全與講道，俄國最通行的聖傳集。斯拉夫聖傳文學的集大成，正教講壇與民間敬虔的橋樑。' },
          { title_zh: '安德魯斯講道集', title_orig: 'XCVI Sermons (Lancelot Andrewes)', author: '蘭斯洛特‧安德魯斯', era: '1600–1620', place: '倫敦', language: '英文', intro: '欽定本譯經領袖之一安德魯斯的御前講道，字句雕琢、旁徵博引，艾略特譽之。詹姆士一世時代英國國教講壇的巔峰，玄學派講道文體的代表。' },
          { title_zh: '多恩講道集', title_orig: 'Sermons (John Donne)', author: '約翰‧多恩', era: '1620 年代', place: '倫敦', language: '英文', intro: '詩人牧者多恩任聖保羅座堂主任時的講道，論死亡與救恩激越深沉。「喪鐘為誰而鳴」之作者的講壇遺產，英語玄學講道的文學高峰。' },
          { title_zh: '泰勒聖潔生死論', title_orig: 'The Rule and Exercises of Holy Living and Holy Dying', author: '傑瑞米‧泰勒', era: '1650–1651', place: '英格蘭', language: '英文', intro: '「英國講壇的莎士比亞」泰勒論聖潔生活與善終的勸修雙書，文采斐然。英國國教靈修文學的經典，清教與國教之間的敬虔橋樑。' }
        
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
          { title_zh: '教會著述家文學史', title_orig: 'Scriptorum ecclesiasticorum historia litteraria, a Christo nato usque ad saeculum XIV', author: 'William Cave', era: '1688', place: 'London', language: '拉丁文', intro: '英國國教學者 William Cave（1637–1713）以拉丁文撰寫之教會著述家書目傳記總覽，涵蓋基督降生至十四世紀止。全書依年代排列，逐人條列生卒年、生平、著作真偽與版本源流，兼及著作思想評介，體例近乎「教父文學史辭典」。此書與其後續修訂版（Scriptorum ecclesiasticorum historia literaria, 1688–1698）並列十七世紀英國聖公會護教暨古學運動代表作，為後世教父學書目研究之重要參考工具。' },
          { title_zh: '赫爾佐格新教神學百科', title_orig: 'Realencyklopädie für protestantische Theologie und Kirche', author: '約翰‧雅各‧赫爾佐格（主編）', era: '1853–1868（三版至 1913）', place: '哥塔／萊比錫', language: '德文', intro: '德國新教學術的百科總匯，動員數百學者歷三版擴至廿四鉅冊，沙夫據以改編為英語世界的《沙夫-赫爾佐格百科》。十九世紀新教神學自信的紀念碑，至今仍為教會史檢索的深井。' },
          { title_zh: '韋策爾-韋爾特教會辭典', title_orig: 'Kirchenlexikon (Wetzer und Welte)', author: '韋策爾與韋爾特（主編）', era: '1847–1860（二版 1882–1903）', place: '弗萊堡', language: '德文', intro: '德語天主教對抗新教百科的辭典工程，十二巨冊網羅教義、教會法與聖人傳記。它是十九世紀天主教學術復興的旗艦工具書，《天主教百科全書》的直接前驅。' },
          { title_zh: '麥克林托克-斯特朗百科', title_orig: 'Cyclopaedia of Biblical, Theological, and Ecclesiastical Literature', author: '麥克林托克與斯特朗', era: '1867–1887', place: '紐約', language: '英文', intro: '美國衛理宗學者麥克林托克與斯特朗編纂的十二冊神學百科，兼收聖經、教會史與各國宗派，為十九世紀美洲最大的宗教參考書。新大陸神學教育自立的標誌工程。' },
          { title_zh: '史密斯聖經辭典', title_orig: 'A Dictionary of the Bible (William Smith)', author: '威廉‧史密斯（主編）', era: '1860–1863', place: '倫敦', language: '英文', intro: '古典學辭書名家史密斯主編的三卷聖經辭典，人地名物逐條考訂，風行英美數十年並衍生袖珍版入千萬家庭。維多利亞時代聖經知識普及的標準配備，後世聖經辭典的模板。' },
          { title_zh: '基督教傳記辭典', title_orig: 'A Dictionary of Christian Biography', author: '威廉‧史密斯與亨利‧韋斯（主編）', era: '1877–1887', place: '倫敦', language: '英文', intro: '收錄前八世紀基督教人物與宗派文獻的四卷傳記辭典，條目多出名家之手而考據紮實。與《古物辭典》互為姊妹，至今研究教父時代仍屢被徵引的英語標準參考。' },
          { title_zh: '基督教古物辭典', title_orig: 'A Dictionary of Christian Antiquities', author: '威廉‧史密斯與塞繆爾‧切特姆（主編）', era: '1875–1880', place: '倫敦', language: '英文', intro: '考訂早期教會禮儀、器物、建築與制度的兩卷辭典，把考古發現引入教會史工具書。十九世紀「基督教考古學」成果的總匯，禮儀與制度史檢索的經典。' },
          { title_zh: '哈斯丁斯聖經辭典', title_orig: 'A Dictionary of the Bible (James Hastings)', author: '詹姆斯‧哈斯丁斯（主編）', era: '1898–1904', place: '愛丁堡', language: '英文', intro: '蘇格蘭牧師哈斯丁斯主編的五卷聖經辭典，吸納批判學術而持平穩健，為二十世紀前半英語神學生的案頭標準。哈氏後續百科系列的開山之作，工具書編輯藝術的典範。' },
          { title_zh: '米涅神學百科全書', title_orig: 'Encyclopédie théologique (Migne)', author: '雅克-保羅‧米涅（主編）', era: '1844–1866', place: '巴黎', language: '法文', intro: '出版狂人米涅神父在教父文庫之外編印的百科系列，一百七十一冊涵蓋神學、教會法、聖徒與異端諸辭典。十九世紀法國教士的整套知識裝備，出版史上最龐大的宗教百科工程。' },
          { title_zh: '利希滕貝格宗教科學百科', title_orig: 'Encyclopédie des sciences religieuses', author: '弗雷德里克‧利希滕貝格（主編）', era: '1877–1882', place: '巴黎', language: '法文', intro: '巴黎新教神學院院長利希滕貝格主編的十三卷百科，法語新教學術的總集結，兼容自由與正統之聲。法國新教少數派以學術自立的紀念碑。' },
          { title_zh: '莫羅尼教會博識辭典', title_orig: 'Dizionario di erudizione storico-ecclesiastica', author: '加埃塔諾‧莫羅尼', era: '1840–1861', place: '威尼斯', language: '義大利文', intro: '教宗侍從莫羅尼以一人之力編成的一百零三冊教會博識辭典，教廷禮節、樞機傳記與各教區沿革鉅細靡遺。羅馬教廷內部知識的空前大公開，研究教宗制度的獨家寶庫。' },
          { title_zh: '卡爾梅聖經辭典', title_orig: 'Dictionnaire historique et critique de la Bible', author: '奧古斯丁‧卡爾梅', era: '1722–1728', place: '巴黎', language: '法文', intro: '本篤會學者卡爾梅的聖經歷史考證辭典，集其巨帙注釋之精華，譯成多語行銷全歐。啟蒙前夜天主教聖經學術的高峰，伏爾泰揶揄之而又處處抄之的名著。' },
          { title_zh: '杜康熱中古拉丁辭彙', title_orig: 'Glossarium mediae et infimae Latinitatis', author: '夏爾‧杜‧弗雷納‧杜康熱', era: '1678', place: '巴黎', language: '拉丁文', intro: '法學家杜康熱編纂的中古拉丁語大辭典，自教會文書與法典中輯出古典辭書不載的詞彙，歷代增補至十巨冊。中世紀研究由此成為可能，至今仍是中古文獻閱讀的必備工具。' },
          { title_zh: '蘇伊塞教父辭典', title_orig: 'Thesaurus ecclesiasticus e patribus Graecis', author: '約翰‧卡斯帕‧蘇伊塞', era: '1682', place: '阿姆斯特丹', language: '拉丁文／希臘文', intro: '蘇黎世學者蘇伊塞窮卅年之功編成的希臘教父用語辭典，逐詞輯錄教父文本中的神學語義。教父希臘語的第一部專業辭書，教義史語文學研究的奠基工具。' },
          { title_zh: '法布里修斯希臘書志', title_orig: 'Bibliotheca Graeca', author: '約翰‧阿爾伯特‧法布里修斯', era: '1705–1728', place: '漢堡', language: '拉丁文', intro: '漢堡學者法布里修斯編纂的十四卷希臘文獻總書志，自荷馬至拜占庭陷落的作家著作版本盡錄其中，教父文獻尤詳。「書志學之父」的最大工程，古典與教父研究的導航總圖。' },
          { title_zh: '法蘭西文學史', title_orig: 'Histoire littéraire de la France', author: '聖莫爾本篤會士（裡韋主持）', era: '1733 起', place: '巴黎', language: '法文', intro: '聖莫爾學派系統編纂的法蘭西作家文學史，按世紀逐一考訂中世紀教會作者生平著作，革命後由法蘭西學會續修至今。修道學術轉為國家工程的活化石，中世紀研究的基準書目。' },
          { title_zh: '史特朗經文彙編', title_orig: 'The Exhaustive Concordance of the Bible', author: '詹姆斯‧斯特朗', era: '1890', place: '紐約', language: '英文', intro: '斯特朗率百人團隊把英王欽定本每一字編入彙編，並創希伯來希臘原文編號系統。「史特朗號碼」成為跨語言查經的通用座標，平信徒直通原文的世紀工具，數位聖經時代仍賴其編碼。' },
          { title_zh: '楊格分析經文彙編', title_orig: 'Young\'s Analytical Concordance to the Bible', author: '羅伯特‧楊格', era: '1879', place: '愛丁堡', language: '英文', intro: '自學成家的東方語學者楊格按原文詞彙分析編排的經文彙編，同一英譯詞下分列不同原文。與史特朗並峙的另一座彙編高峰，直譯派查經傳統的標準裝備。' },
          { title_zh: '格森紐斯希伯來文辭典', title_orig: 'Hebräisches und aramäisches Handwörterbuch', author: '威廉‧格森紐斯', era: '1810–1812（歷版增訂）', place: '哈勒', language: '德文', intro: '格森紐斯以比較閃語學重建希伯來詞義，其辭典與文法把聖經希伯來語研究奠於科學基礎，英譯本 BDB 沿用至今。近代希伯來語文學的開山祖師，一切舊約研究的地基工具。' },
          { title_zh: '塞耶新約希臘文辭典', title_orig: 'A Greek-English Lexicon of the New Testament (Thayer)', author: '約瑟夫‧亨利‧塞耶（譯訂格林-威爾克）', era: '1886', place: '紐約', language: '英文', intro: '塞耶把德國格林的新約希臘文辭典譯訂為英語標準本，詞條兼顧古典用法與新約語義。二十世紀初英語世界的新約辭典霸主，至今仍與史特朗號碼掛鉤流通於查經軟體。' },
          { title_zh: '新約同義詞辨析', title_orig: 'Synonyms of the New Testament', author: '理查‧特倫奇', era: '1854', place: '都柏林', language: '英文', intro: '都柏林大主教特倫奇辨析新約近義詞的名著，「愛」與「愛」、「新」與「新」之別娓娓如講章。語文學與靈修合一的辭書小品，亦是其推動《牛津英語辭典》志業的姊妹作。' },
          { title_zh: '布克斯托夫希伯來辭典', title_orig: 'Lexicon Hebraicum et Chaldaicum / Lexicon Chaldaicum Talmudicum', author: '老約翰‧布克斯托夫（子續成）', era: '1607–1639', place: '巴塞爾', language: '拉丁文', intro: '巴塞爾的布克斯托夫父子兩代編成聖經希伯來語與塔木德亞蘭語大辭典，兼護馬所拉母音之古。新教希伯來學的第一世家，其辭書供基督教希伯來研究取汲兩百年。' },
          { title_zh: '卡斯特爾七語大辭典', title_orig: 'Lexicon Heptaglotton', author: '埃德蒙‧卡斯特爾', era: '1669', place: '倫敦', language: '拉丁文（七語對照）', intro: '卡斯特爾為倫敦多語聖經配套編纂的七語大辭典，希伯來、敘利亞、阿拉伯、衣索比亞諸語並列，耗盡家財目力，十七年僅售數部。近代東方語言學最悲壯的獨力工程，多語聖經學術的絕峰。' },
          { title_zh: '厄舍爾聖經年表', title_orig: 'Annales Veteris Testamenti', author: '詹姆斯‧厄舍爾', era: '1650–1654', place: '都柏林／倫敦', language: '拉丁文', intro: '愛爾蘭大主教厄舍爾據聖經世系推算創世於西元前四〇〇四年的編年鉅著，其年代自十八世紀起印入欽定本頁邊而深入人心。聖經年代學的登峰造極，亦是日後創造論爭議的座標原點。' },
          { title_zh: '佩塔維烏斯年代學', title_orig: 'Opus de doctrina temporum', author: '德尼‧佩託（佩塔維烏斯）', era: '1627', place: '巴黎', language: '拉丁文', intro: '耶穌會學者佩託的年代學大全，整合天文計算與史料考訂，確立紀年學的方法論並通用「西元前」記法。與其教義史鉅著同為耶穌會學術的雙璧，歷史時間學的奠基之作。' },
          { title_zh: '斯卡利傑年代學校正', title_orig: 'Opus de emendatione temporum', author: '約瑟夫‧斯卡利傑', era: '1583', place: '萊頓', language: '拉丁文', intro: '胡格諾大儒斯卡利傑以比較曆法重建普世年代學，創儒略日計數並整合波斯埃及紀年於聖經框架之外。近代年代學的創始之作，把神聖史納入普世時間科學的第一步。' },
          { title_zh: '霍恩聖經導論', title_orig: 'An Introduction to the Critical Study and Knowledge of the Holy Scriptures', author: '託馬斯‧哈特韋爾‧霍恩', era: '1818（歷版增訂）', place: '倫敦', language: '英文', intro: '霍恩集聖經版本、正典、詮釋與考古知識於一帙的導論全書，四巨冊為英語世界通用教本近百年。護教立場的聖經學百科，十九世紀牧者裝備的標準行囊。' },
          { title_zh: '朱利安聖詩學辭典', title_orig: 'A Dictionary of Hymnology', author: '約翰‧朱利安（主編）', era: '1892', place: '倫敦', language: '英文', intro: '朱利安動員各國學者編成的聖詩學大辭典，四十萬條考訂各語聖詩的作者、源流與譯本。聖詩研究由掌故升為學科的奠基工具，至今無可替代的單卷權威。' },
          { title_zh: '胡克教會辭典', title_orig: 'A Church Dictionary', author: '沃爾特‧法誇爾‧胡克', era: '1842', place: '裡茲', language: '英文', intro: '裡茲教區牧師胡克為平信徒編寫的教會知識辭典，禮儀、聖職與教義條分縷析，再版十餘次。維多利亞教會復興運動的普及讀物，堂區書架上的標準配備。' },
          { title_zh: '注釋與注釋家', title_orig: 'Commenting and Commentaries', author: '查爾斯‧司布真', era: '1876', place: '倫敦', language: '英文', intro: '司布真為牧者學院講評聖經注釋書目的指南，逐一品題千餘種注釋，妙語如「加爾文如金礦，馬太亨利如蜜房」。傳道人選書的世紀嚮導，注釋書目學的趣味經典。' },
          { title_zh: '神學書目大全', title_orig: 'Cyclopaedia Bibliographica', author: '詹姆斯‧達令', era: '1854–1859', place: '倫敦', language: '英文', intro: '倫敦神學書商達令編纂的神學文獻總書目，按作者與主題雙軌檢索數萬種著作。十九世紀神學閱讀地圖的總繪，圖書館學與神學交會的實用豐碑。' },
          { title_zh: '聖經文庫', title_orig: 'Bibliotheca Sacra (Le Long)', author: '雅克‧勒隆', era: '1709', place: '巴黎', language: '拉丁文', intro: '奧拉託利會士勒隆編纂的聖經版本總書志，網羅各語聖經印本抄本的出版源流。聖經書志學的奠基之作，後世一切聖經版本目錄的共同祖本。' },
          { title_zh: '安格斯聖經手冊', title_orig: 'The Bible Hand-book', author: '約瑟夫‧安格斯', era: '1853', place: '倫敦', language: '英文', intro: '浸信會學院院長安格斯的單卷聖經手冊，正典、歷史與逐卷導論兼備，流行英語世界並經譯介入華。平信徒聖經教育的袖珍百科，十九世紀查經運動的隨身工具。' },
          { title_zh: '俄羅斯教役者案頭手冊', title_orig: 'Настольная книга для священно-церковно-служителей', author: '謝爾蓋‧布爾加科夫（教會學者）', era: '1892（1913 增訂）', place: '哈爾科夫', language: '俄文', intro: '俄國教會學者布爾加科夫為司祭編纂的案頭大全，曆法、禮規、教會法與異端辨識一冊俱備。帝俄末期堂區聖職的實務百科，至今再印為正教神職的參考經典。' }
        
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
          { title_zh: '漢英韻府', title_orig: 'A Syllabic Dictionary of the Chinese Language', author: '衛三畏(Samuel Wells Williams)', era: '1874', place: '上海', language: '漢文‧英文', intro: '由美部會宣教士兼漢學家衛三畏(Samuel Wells Williams)編成，以音節排序、按韻檢字而得名「韻府」。全書廣收漢字字音、字義與詞例，並標注官話與方音讀法，兼具辭書與正音工具之用。衛三畏久居中國、譯經辦報，此書凝聚其畢生漢語造詣，編排嚴謹、釋義詳贍，長期為西人研習漢語與從事宣教、翻譯所倚重，是晚清漢英辭書的集大成之作。' },
          { title_zh: '翟理斯華英字典', title_orig: 'A Chinese-English Dictionary (Giles)', author: '翟理斯', era: '1892（1912 二版）', place: '上海／劍橋', language: '中文／英文', intro: '領事漢學家翟理斯編纂的大型華英字典，確立威妥瑪-翟理斯拼音體系，收字逾萬並附方言讀音。雖出領事之手而承宣教辭書傳統，二十世紀前半西方讀中文的標準門戶。' },
          { title_zh: '華語官話語法', title_orig: 'Arte de la lengua mandarina', author: '萬濟國（瓦羅）', era: '1703', place: '福安（刊於廣州）', language: '西班牙文', intro: '道明會士萬濟國在閩東傳教數十年寫成的官話語法，為史上第一部刊行的漢語語法書。以拉丁語法框架剖析漢語，開西方漢語語言學之先，宣教語言學的里程碑。' },
          { title_zh: '日本大文典', title_orig: 'Arte da Lingoa de Iapam', author: '陸若漢（羅德里格斯）', era: '1604–1608', place: '長崎', language: '葡萄牙文', intro: '耶穌會士陸若漢窮卅年學養寫成的日語大文法，敬語體系、和歌文體乃至書信禮式皆有分析。禁教前夕的天鵝之歌，至今仍是研究中世日語的第一級史料。' },
          { title_zh: '日葡辭書', title_orig: 'Vocabvlario da Lingoa de Iapam', author: '長崎耶穌會學院', era: '1603–1604', place: '長崎', language: '日文／葡萄牙文', intro: '耶穌會長崎學院集體編纂的日葡辭典，收詞三萬二千條，俗語、婦人語、佛教語逐一標注。安土桃山日語的活字典，日本國語學界至今倚為寶典的宣教辭書之王。' },
          { title_zh: '克里孟加拉語文法辭典', title_orig: 'A Grammar and Dictionary of the Bengalee Language', author: '威廉‧克里', era: '1801–1825', place: '塞蘭坡', language: '孟加拉文／英文', intro: '克里在塞蘭坡編纂的孟加拉語文法與大辭典，並主持鑄造孟加拉活字。譯經副產品成為孟加拉散文書面語的奠基工程，「孟加拉文藝復興」意外的宣教起點。' },
          { title_zh: '印第安語文法初階', title_orig: 'The Indian Grammar Begun', author: '約翰‧艾略特', era: '1666', place: '劍橋（麻薩諸塞）', language: '英文／馬薩諸塞語', intro: '艾略特為譯經而分析馬薩諸塞阿爾岡昆語寫成的文法，自謙「初階」而實為北美原住民語言的首部文法書。該語言十九世紀消亡後，此書與其譯經成為今日語言復振運動的救命文獻。' },
          { title_zh: '納瓦特爾語辭典', title_orig: 'Vocabulario en lengua castellana y mexicana', author: '阿隆索‧德‧莫利納', era: '1555（1571 增訂）', place: '墨西哥城', language: '西班牙文／納瓦特爾文', intro: '方濟會士莫利納編纂的西班牙語-納瓦特爾語雙向辭典，為美洲大陸第一部印行辭書。阿茲特克語言由此獲得書面工具，至今仍是古典納瓦特爾語研究的基準辭典。' },
          { title_zh: '克丘亞語辭典', title_orig: 'Vocabulario de la lengua general de todo el Perú llamada lengua qquichua', author: '迭戈‧岡薩雷斯‧奧爾金', era: '1608', place: '利馬', language: '西班牙文／克丘亞文', intro: '耶穌會士岡薩雷斯‧奧爾金編纂的克丘亞語大辭典，收詞宏富兼載安地斯風物。印加官話的最大殖民期辭書，今日克丘亞語復振與安地斯研究的第一參考。' },
          { title_zh: '史瓦希裡語辭典', title_orig: 'A Dictionary of the Suahili Language', author: '路德維希‧克拉普夫', era: '1882', place: '倫敦', language: '史瓦希里文／英文', intro: '德國宣教士克拉普夫東非卅年心血的史瓦希裡語辭典，身後刊行，並曾首譯聖經段落入該語。東非通用語的第一部大辭典，宣教語言學為非洲語文書面化奠基的代表。' },
          { title_zh: '越葡拉辭典', title_orig: 'Dictionarium Annamiticum Lusitanum et Latinum', author: '亞歷山德羅‧德‧羅德（羅歷山）', era: '1651', place: '羅馬', language: '越南文／葡萄牙文／拉丁文', intro: '耶穌會士羅歷山集前人之功刊行的越葡拉三語辭典，確立以羅馬字母拼寫越南語的系統。「國語字」由此誕生，一部宣教辭書改變一個民族文字的最著名案例。' },
          { title_zh: '裡德爾韓法辭典', title_orig: 'Dictionnaire coréen-français', author: '裡德爾主教（巴黎外方傳教會）', era: '1880', place: '橫濱刊行', language: '韓文／法文', intro: '巴黎外方傳教會朝鮮代牧裡德爾在教難流亡中主持編成的韓法辭典，為朝鮮語第一部近代辭書，次年續出文法。地下教會時代的語言學遺產，韓語近代辭書史的起點。' },
          { title_zh: '譯名之爭文獻', title_orig: 'The Term Question Documents', author: '在華宣教士群（麥都思、理雅各、文惠廉等）', era: '1847–1877', place: '上海／香港', language: '英文／中文', intro: '聖經漢譯當用「上帝」「神」抑或「天主」的世紀論戰文獻，麥都思與文惠廉各執一端、理雅各以儒典考證助陣。譯名之爭牽動神學與漢學的百年公案，漢語神學語彙成形的第一手檔案。' },
          { title_zh: '中國總論', title_orig: 'The Middle Kingdom', author: '衛三畏', era: '1848（1883 修訂）', place: '紐約', language: '英文', intro: '美部會宣教士衛三畏綜述中國地理、政制、經學與宗教的兩巨冊百科，修訂版集其四十年見聞。十九世紀英語世界認識中國的標準全書，宣教士漢學的集大成，作者後開耶魯漢學講座。' },
          { title_zh: '英華萃林韻府', title_orig: 'A Vocabulary and Hand-book of the Chinese Language', author: '盧公明', era: '1872', place: '福州', language: '中文／英文', intro: '美部會宣教士盧公明編纂的英華分類辭庫，兼收諺語、公文與科技新詞，儼然晚清社會的語彙百科。宣教辭書轉向實用百科的代表，研究近代漢語新詞與福州社會的富礦。' },
          { title_zh: '毛利語辭典', title_orig: 'A Dictionary of the New Zealand Language', author: '威廉‧威廉斯', era: '1844', place: '派希亞', language: '毛利文／英文', intro: '聖公會宣教士威廉斯編纂的毛利語辭典與文法，為毛利語書面化的奠基工程，家族四代續修至今仍為標準。《懷唐伊條約》的譯文語境即出此圈，太平洋宣教語言學的代表作。' },
          { title_zh: '宣教百科', title_orig: 'The Encyclopaedia of Missions', author: '埃德溫‧布利斯（主編）', era: '1891', place: '紐約', language: '英文', intro: '首部宣教專科百科全書，逐條記各差會、工場、語言譯本與統計地圖。十九世紀宣教運動自我盤點的總帳，愛丁堡一九一〇普查傳統的前驅工具書。' },
          { title_zh: '宣教地圖集', title_orig: 'Allgemeiner Missions-Atlas', author: '萊因霍爾德‧格倫德曼', era: '1867–1871', place: '哥塔', language: '德文', intro: '德國宣教學者格倫德曼繪製的世界宣教地圖集，各洲工場、差會轄區與宗教分佈首度系統成圖。宣教地理學的開山之作，其圖版為後世宣教統計的視覺範式。' },
          { title_zh: '宣教與社會進步統計', title_orig: 'Christian Missions and Social Progress', author: '詹姆斯‧丹尼斯', era: '1897–1906', place: '紐約', language: '英文', intro: '丹尼斯以三巨冊統計論證宣教對教育、醫療與社會改革的貢獻，附全球宣教統計圖表百餘幅。「宣教社會學」的首度嘗試，世紀之交宣教護教學的數據總匯。' },
          { title_zh: '巴勒斯坦聖經研究', title_orig: 'Biblical Researches in Palestine', author: '愛德華‧羅賓遜（史密斯同行）', era: '1841', place: '波士頓／柏林', language: '英文', intro: '美國學者羅賓遜與宣教士史密斯以阿拉伯地名比定聖經地點的踏查鉅著，一舉確認數百處古址。聖經地理學由書齋走入田野的開山之作，聖地考古學的奠基文獻。' },
          { title_zh: '聖地歷史地理', title_orig: 'The Historical Geography of the Holy Land', author: '喬治‧亞當‧史密斯', era: '1894', place: '愛丁堡', language: '英文', intro: '史密斯把巴勒斯坦地形與聖經敘事互證的名著，文筆如史詩，艾倫比將軍攻耶路撒冷時隨身攜之。聖經地理的文學化巔峰，百年間卅版不衰的地理釋經經典。' }
        
        ],
      },
      {
        key: 'source-collections',
        label: '文獻集成部',
        label_en: 'Source Collections and Critical Editions',
        desc: '近代學術對教會文獻的大規模輯刊——自博蘭德聖傳、曼西會議集、米涅教父文庫至魏瑪版路德全集。',
        works: [
          { title_zh: '大公會議大全', title_orig: 'Sacrorum Conciliorum nova et amplissima collectio', author: '喬瓦尼‧多梅尼科‧曼西', era: '1759–1798', place: '佛羅倫斯／威尼斯', language: '拉丁文', intro: '盧卡總主教曼西集歷代會議文獻之大成的三十一冊（後補至五十三冊），自使徒時代迄近代諸會議決議俱錄。引用大公與地方會議的標準總集，教會法史研究的基座文獻。' },
          { title_zh: '聖徒行傳大全', title_orig: 'Acta Sanctorum', author: '博蘭德學社', era: '1643 起', place: '安特衛普／布魯塞爾', language: '拉丁文', intro: '耶穌會博蘭德學社按聖人曆日考訂刊佈聖傳原始文獻的大全，三百餘年續修至六十八巨冊。以批判方法整理聖傳而屢觸禁忌，史料考證學的搖籃，聖人研究的第一泉源。' },
          { title_zh: '日耳曼歷史文獻集成', title_orig: 'Monumenta Germaniae Historica', author: '施泰因發起（佩茨首任主編）', era: '1826 起', place: '法蘭克福／柏林／慕尼黑', language: '拉丁文', intro: '「對祖國的神聖之愛賦予靈魂」為銘的德意志中世紀文獻集成，書信、法典、編年史按科學校勘刊佈，樹立近代史料編纂的標準。中世紀教會史研究的軍火庫，本藏多處書函律藏條目皆賴其刊本。' },
          { title_zh: '維也納教父文集', title_orig: 'Corpus Scriptorum Ecclesiasticorum Latinorum', author: '維也納科學院', era: '1866 起', place: '維也納', language: '拉丁文', intro: '維也納科學院發起的拉丁教父批判版文集，以抄本系譜學重建文本，取代米涅粗放翻印。教父文獻學進入批判時代的標誌，與柏林希臘教父文集東西呼應。' },
          { title_zh: '帕克學社文集', title_orig: 'Parker Society Publications', author: '帕克學社', era: '1841–1855', place: '劍橋', language: '英文', intro: '為回應牛津運動而創的帕克學社，十五年間刊印英格蘭宗教改革家著作五十四卷，克蘭麥、拉蒂默、朱厄爾全帙重光。以出版守護新教記憶的典型工程，都鐸教會史的標準文庫。' },
          { title_zh: '宗教改革者文集', title_orig: 'Corpus Reformatorum', author: '佈雷特施奈德發起', era: '1834 起', place: '哈勒／布倫瑞克', language: '拉丁文／法文／德文', intro: '收墨蘭頓、加爾文、茨溫利三家全部著作與書信的批判版文集，加爾文書信註記尤為研究命脈。宗教改革研究的文獻基座，本藏改革家書信諸條目的學術出處。' },
          { title_zh: '路德全集魏瑪版', title_orig: 'D. Martin Luthers Werke: Kritische Gesamtausgabe (Weimarer Ausgabe)', author: '魏瑪路德學會', era: '1883 起', place: '魏瑪', language: '德文／拉丁文', intro: '路德誕辰四百年啟動的批判版全集，著作、聖經譯註、桌邊談與書信四系一百二十餘冊，歷百廿年方竣。單一作者批判版的世界之最，路德研究的絕對座標「WA」。' },
          { title_zh: '魯伊納特殉道者真行錄', title_orig: 'Acta primorum martyrum sincera et selecta', author: '提耶裡‧魯伊納特', era: '1689', place: '巴黎', language: '拉丁文', intro: '馬比雍高弟魯伊納特自浩繁聖傳中甄選文獻可信的原始殉道紀錄七十餘篇，剔除後世增飾。「真行錄」的批判標準沿用至今，古代殉道研究的第一手文獻選集。' },
          { title_zh: '東方文庫', title_orig: 'Bibliotheca Orientalis Clementino-Vaticana', author: '約瑟夫‧西門‧阿瑟曼尼', era: '1719–1728', place: '羅馬', language: '拉丁文／敘利亞文', intro: '馬龍派學者阿瑟曼尼整理梵蒂岡敘利亞抄本編成的東方教會文獻總覽，敘利亞正統與東方教會著作家首度系統呈現於西方。歐洲敘利亞學的奠基文庫，本藏東方諸條目的源頭書志。' },
          { title_zh: '不列顛教會會議集', title_orig: 'Concilia Magnae Britanniae et Hiberniae', author: '大衛‧威爾金斯', era: '1737', place: '倫敦', language: '拉丁文', intro: '威爾金斯輯英格蘭與愛爾蘭自古至宗教改革的教會會議文獻四巨冊，取代斯佩爾曼舊編。不列顛教會法制史的標準總集，十九世紀方由哈登-斯塔布斯部分修訂。' },
          { title_zh: '牛津教父文庫', title_orig: 'A Library of Fathers of the Holy Catholic Church', author: '普西、紐曼與基布爾（主編）', era: '1838–1885', place: '牛津', language: '英文', intro: '牛津運動三傑主持的教父英譯文庫四十八卷，以「回到未分裂教會」為志，紐曼譯亞他那修尤為名譯。安立甘公教復興的學術支柱，英語教父閱讀文化的開端。' },
          { title_zh: '法布里修斯偽典集', title_orig: 'Codex pseudepigraphus Veteris Testamenti / Codex apocryphus Novi Testamenti', author: '約翰‧阿爾伯特‧法布里修斯', era: '1703–1723', place: '漢堡', language: '拉丁文／希臘文', intro: '法布里修斯輯刊新舊約偽典文本的雙料文集，首度把散佚的次經偽典整編成可徵引的學術語料。典外文獻研究的奠基工程，本藏經藏外典諸條目的學史源頭。' },
          { title_zh: '義大利史料集成', title_orig: 'Rerum Italicarum Scriptores', author: '洛多維科‧穆拉托里（主編）', era: '1723–1751', place: '米蘭', language: '拉丁文／義大利文', intro: '穆拉托里輯刊五百至一千五百年間義大利編年史與教會文獻的廿八巨冊集成，兼撰考辨序論。義大利史學的奠基工程，中世紀教會史料的南歐大庫，「穆拉托里殘篇」即其發現之一。' },
          { title_zh: '教會作家文獻史', title_orig: 'Scriptorum Ecclesiasticorum Historia Literaria', author: '威廉‧凱夫', era: '1688–1698', place: '倫敦', language: '拉丁文', intro: '凱夫按世紀編列歷代教會作家生平著作的文獻史巨著，逐位考訂真偽與版本。英國教父學術的代表工程，十八世紀學者案頭的教父書目總覽。' }
        
        
        
        ]
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
          { title_zh: '布里奇沃特論文集', title_orig: 'The Bridgewater Treatises', author: '布里奇沃特伯爵遺贈（八位學者）', era: '1833–1840', place: '倫敦', language: '英文', intro: '布里奇沃特伯爵遺囑資助八位名家論證「上帝在創造中的能力智慧與良善」，惠威爾論天文、巴克蘭論地質各成巨帙。自然神學的最後盛典，達爾文革命前夜的科學護教總集。' },
          { title_zh: '物理神學', title_orig: 'Physico-Theology', author: '威廉‧德勒姆', era: '1713', place: '倫敦', language: '英文', intro: '皇家學會會士德勒姆的波義耳講座結集，自大氣、眼睛至昆蟲論證設計者的智慧，並創「物理神學」一詞。十八世紀最暢銷的科學護教書，帕利《自然神學》的直接先驅。' },
          { title_zh: '查爾莫斯天文論道講話', title_orig: 'Astronomical Discourses', author: '託馬斯‧查爾莫斯', era: '1817', place: '格拉斯哥', language: '英文', intro: '蘇格蘭名牧查爾莫斯以天文學的無垠回應「基督教是否地球一隅之見」的質疑，講道結集當年售九版。科學佈道的世紀暢銷書，信仰與新宇宙觀和解的雄辯文本。' },
          { title_zh: '宗教的類比', title_orig: 'The Analogy of Religion', author: '約瑟夫‧巴特勒', era: '1736', place: '倫敦', language: '英文', intro: '巴特勒主教以自然與啟示的類比駁自然神論：自然界同樣充滿疑難，難不成也棄之？其或然性論證支配英語護教一世紀，牛津劍橋指定必讀，理性時代護教學的最高峰。' },
          { title_zh: '磐石的見證', title_orig: 'The Testimony of the Rocks', author: '休‧米勒', era: '1857', place: '愛丁堡', language: '英文', intro: '石匠出身的地質學家米勒調和地質年代與創世記的遺著，主張「日」為地質長代，成書之夜自盡而益增其悲。蘇格蘭平民科學與虔敬的結晶，維多利亞科學信仰之爭的標誌文本。' },
          { title_zh: '臍論', title_orig: 'Omphalos: An Attempt to Untie the Geological Knot', author: '菲利普‧亨利‧戈斯', era: '1857', place: '倫敦', language: '英文', intro: '博物學家戈斯提出「創造即帶歷史痕跡」——亞當有臍、巖層有化石，一舉調和地質學與六日創造。科學界與教會齊聲拒之，其孤絕成為信仰與科學糾結的著名寓言，子迴憶錄《父與子》更使其不朽。' },
          { title_zh: '地球新論', title_orig: 'A New Theory of the Earth', author: '威廉‧惠斯頓', era: '1696', place: '劍橋', language: '英文', intro: '牛頓接班人惠斯頓以彗星力學解釋創世與洪水，把摩西敘事翻譯為牛頓宇宙論。牛頓學派調和聖經與新科學的代表作，作者後因一位論失席，科學釋經的早期戲劇性案例。' },
          { title_zh: '地球神聖理論', title_orig: 'Telluris Theoria Sacra', author: '託馬斯‧伯內特', era: '1681–1689', place: '倫敦', language: '拉丁文／英文', intro: '伯內特想像創世至末日的地球史詩：伊甸的光滑地殼崩塌成洪水與山嶽，末火再造新天新地。以科學語言重寫救恩史的宏大嘗試，地質學想像與神學敘事交纏的巴洛克奇書。' }
        
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
          { title_zh: '英格蘭教會法典', title_orig: 'Codex Iuris Ecclesiastici Anglicani', author: '埃德蒙‧吉布森', era: '1713', place: '倫敦', language: '英文／拉丁文', intro: '倫敦主教吉布森輯英格蘭教會法令並附評註的兩巨冊法典，國教法制的權威總彙。「吉布森法典」為教會法庭與國會論辯的標準引據，安立甘教會法學的基石。' },
          { title_zh: '範艾斯彭教會法大全', title_orig: 'Jus ecclesiasticum universum', author: '齊格‧貝爾納‧範艾斯彭', era: '1700', place: '魯汶', language: '拉丁文', intro: '魯汶教會法學家範艾斯彭的教會法大全，重歷史考證而抑教廷集權，為高盧主義與約瑟夫主義的法學武庫。啟蒙時代最具影響的教會法著作，身後因楊森爭議客死異鄉。' },
          { title_zh: '論教區會議', title_orig: 'De synodo dioecesana', author: '本篤十四世（蘭貝提尼）', era: '1748', place: '羅馬', language: '拉丁文', intro: '學者教宗本篤十四世論教區會議的法學專著，主教治理的程序與界限條分縷析，兼裁百年疑案。出自教宗之手的法學教科書，特倫託體制運作的權威說明書。' },
          { title_zh: '費拉里斯教會法辭庫', title_orig: 'Prompta Bibliotheca canonica, juridica, moralis, theologica', author: '盧修斯‧費拉里斯', era: '1746', place: '波隆那', language: '拉丁文', intro: '方濟會士費拉里斯按字母編排的教會法實務辭庫，聖職、婚姻、俸祿諸題即查即用，歷版增補至十巨冊。舊法典時代教士書桌上的「活法典」，教會行政知識的百科形態。' },
          { title_zh: '衛理年會紀要', title_orig: 'Minutes of the Methodist Conferences', author: '約翰‧衛斯理與歷屆年會', era: '1744 起', place: '倫敦', language: '英文', intro: '自一七四四年首屆年會起連續刊行的衛理年會紀要，教義問答、巡迴傳道人名錄與會規逐年累積。循道運動由團契長成宗派的制度年輪，衛理政體的原始檔案。' },
          { title_zh: '美以美會教規', title_orig: 'The Doctrines and Discipline of the Methodist Episcopal Church', author: '美以美會總議會', era: '1784 起歷版', place: '巴爾的摩', language: '英文', intro: '聖誕年會創立美以美會時據衛斯理《大紀要》訂定的教規，教義、總則與治理章程合冊，逐屆總議會修訂。美國衛理宗政體的憲法傳統，蓄奴條款的歷次改動即教會與國史的互文。' },
          { title_zh: '克羅克福德教士名錄', title_orig: 'Crockford\'s Clerical Directory', author: '克羅克福德出版社', era: '1858 起', place: '倫敦', language: '英文', intro: '收錄英格蘭教會全體聖職履歷與聖俸的年度名錄，其匿名序言臧否教會時政成為傳統。國教人事的百年總帳，教會社會史研究的獨特連續史料。' },
          { title_zh: '宗座年鑑', title_orig: 'Annuario Pontificio', author: '教廷國務院（歷代編）', era: '1716 起（今名 1912 起）', place: '羅馬', language: '義大利文', intro: '教廷官方年鑑，自十八世紀《教廷要聞》演為今日紅皮巨冊，全球教區、樞機與聖統資料年年更新。天主教全球體制的年度快照，教會統計與人事的第一手官書。' }
        
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
