import type { DazangEra } from './types'

// 現代基督教大藏經（按時代精神：以 1910 後普世合一運動為主軸＋現代精神）
export const MODERN_ERA: DazangEra = {
  key: 'modern',
  name: '現代基督教大藏經',
  name_en: 'Modern Christian Canon',
  glyph: '今',
  subtitle: '普世合一運動‧新正統與處境神學‧全球與漢語基督教',
  boundary: '按時代精神斷代——以 1910 年愛丁堡世界宣教會議開啟的普世合一運動為主軸：約 1900／1910 至今。',
  enabled: true,
  collections: [
    {
  key: 'jing',
  name: '經藏',
  name_en: 'Scripture Pitaka',
  glyph: '經',
  genres: '校勘版‧現代譯本‧外經',
  summary: '現代基督教大藏經之經藏。依正典封閉法則，正經藏留白（NA／UBS／BHS 校勘版與各語系現代譯本已歸譯校藏；死海古卷與納戈瑪第手抄本按原作時代歸古代譯校）；外經藏收拉斯塔法里、合一教等現代新興與合成宗教的新啟示經典。',
  portal: { to: '/scripture', label: '前往聖經閱讀器' },
  zheng: {
    summary: '正典封閉法則：使徒時代新約正典封閉後，基督教不再有新「正經」。現代批判校勘版、各語系現代譯本一律歸入譯校藏（死海古卷與納戈瑪第手抄本按原作時代歸古代譯校）；此處正經藏留白。外經藏則收現代自稱新啟示的新興與合成宗教經典。',
    divisions: [],
  },
  wai: {
    summary: '外經部收錄一九〇〇年後興起的新興宗教與合成宗教所產生的新啟示經典。這些經典或重新詮釋既有聖經傳統，或宣稱領受全新啟示，雖不為主流教會所承認，卻是理解現代宗教多元生態與基督教影響擴散的重要文本。',
    divisions: [
      {
        key: 'new-revelation',
        label: '現代新興宗教經典部',
        label_en: 'Modern New Religious Scriptures',
        desc: '二十世紀新興與合成宗教宣稱領受的新啟示或重構聖典，多脫胎於基督教傳統而另立新說。',
        works: [
          { title_zh: '聖比布理', title_orig: 'The Holy Piby', author: '羅伯特‧阿薩吉‧羅傑斯（Robert Athlyi Rogers）', era: '1924', place: '美國紐澤西、西印度群島', language: '英文', intro: '聖比布理由出身安圭拉的羅伯特‧阿薩吉‧羅傑斯於一九二四年編寫，又稱「黑人聖經」，是拉斯塔法里運動的重要先驅經典。書中以非洲為中心重述聖經敘事，宣揚非洲人的神聖揀選與返回非洲（衣索比亞）的盼望，並推崇加維的泛非主義。此書深刻影響了日後在牙買加興起的拉斯塔法里運動，被視為其神學雛形，反映了二十世紀非洲離散族群以基督教語彙建構自身解放神話的努力。' },
          { title_zh: '原理講論', title_orig: '원리강론 (原理講論)', author: '文鮮明（口述）、劉孝元（整理）', era: '1966／英譯 1973', place: '韓國首爾', language: '韓文（原）／繁體中文、英文（譯）', intro: '原理講論是文鮮明創立的世界基督教統一神靈協會（合一教／統一教）的根本教義書，一九六六年以韓文出版。書中以「神聖原理」重新詮釋創造、墮落與復歸的歷史，主張耶穌的使命因受難而未完成，需由再臨的「彌賽亞」完成人類的真正救贖與真家庭的建立。此書融合基督教末世論、東亞思想與冷戰反共意識，是二十世紀東亞新興合成宗教中影響最廣者之一，亦引發主流教會對其正統性的廣泛爭議。' },
          { title_zh: '寶瓶同謀耶穌基督福音', title_orig: 'The Aquarian Gospel of Jesus the Christ', author: '李維‧道林（Levi H. Dowling）', era: '1908', place: '美國', language: '英文', intro: '寶瓶同謀耶穌基督福音由美國通靈者李維‧道林於一九〇八年出版，宣稱透過「阿卡西記錄」接收而成，補述耶穌十二歲至三十歲間遊歷印度、波斯、埃及修道的「失落歲月」。此書融合神智學、東方宗教與基督教，是二十世紀初新時代運動的先驅文本之一，雖無歷史根據，卻廣泛流傳於西方靈性圈，反映現代人以新啟示經典重新想像耶穌生平的宗教創造力。' }
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
  genres: '大公會議‧普世合一文件‧法典',
  summary: '現代基督教大藏經之律藏，以一九一〇年愛丁堡世界宣教會議啟動的普世合一運動為主軸，收錄現代基督教的規範性文獻：天主教梵蒂岡第二屆大公會議文獻、現代教會法典與教理；普世合一運動的歷次宣言與共同聲明（WCC、利馬文件、因信稱義聯合聲明等）；新教與福音派的現代信條；以及新興宗教與世俗政教關係的規範文本。',
  zheng: {
    summary: '正經部收錄現代基督教主流宗派公認的規範性文獻，分為天主教梵蒂岡大公會議與法典、以普世合一運動為主軸的合一文件、以及新教與福音派現代信條三大支系，呈現二十世紀基督教在制度與信仰規範上的更新與彼此靠近。',
    divisions: [
      {
        key: 'vatican-canon',
        label: '大公會議與梵蒂岡部',
        label_en: 'Ecumenical Councils and the Vatican',
        desc: '天主教會在二十世紀的核心規範文獻：梵二會議十六文獻、現行教會法典與東方教會法典、以及天主教教理。',
        works: [
          { title_zh: '梵蒂岡第二屆大公會議文獻', title_orig: 'Documenta Concilii Oecumenici Vaticani II', author: '梵蒂岡第二屆大公會議（教宗若望二十三世召開、保祿六世續行）', era: '1962–1965', place: '羅馬梵蒂岡', language: '拉丁文（原）／繁體中文、英文（譯）', intro: '梵蒂岡第二屆大公會議由教宗若望二十三世召開、保祿六世續行，於一九六二至一九六五年間舉行，是天主教會現代化（aggiornamento）的關鍵轉捩。會議頒布四項憲章、九項法令與三項宣言共十六份文獻，涵蓋禮儀本地化、教會自我理解、啟示、現代世界、宗教自由與大公合一等議題。其中《大公主義法令》與《教會對非基督宗教態度宣言》尤其開啟了天主教與其他宗派及宗教的對話，使梵二成為普世合一運動時代天主教最重要的規範性文獻。', link: '/creeds' },
          { title_zh: '天主教法典', title_orig: 'Codex Iuris Canonici (1983)', author: '教宗若望保祿二世頒布', era: '1983', place: '羅馬梵蒂岡', language: '拉丁文（原）／繁體中文、英文（譯）', intro: '一九八三年天主教法典由教宗若望保祿二世頒布，取代一九一七年舊法典，是依梵二精神全面修訂的拉丁禮教會根本法。全典分七卷一千七百五十二條，規範教會總則、天主子民、訓導職、聖化職、教會財產、刑罰與訴訟程序。新法典吸納梵二的教會學，強調全體信友的共同職分與地方教會的角色，是當代拉丁禮天主教會治理與紀律的權威依據。', link: '/canon-law' },
          { title_zh: '東方教會法典', title_orig: 'Codex Canonum Ecclesiarum Orientalium (1990)', author: '教宗若望保祿二世頒布', era: '1990', place: '羅馬梵蒂岡', language: '拉丁文（原）／繁體中文、英文（譯）', intro: '東方教會法典由教宗若望保祿二世於一九九〇年頒布，是與天主教（拉丁）法典並立、專為二十餘個東方禮天主教會制定的共同法典。全典三十題一千五百四十六條，尊重東方教會的禮儀、靈修與教會治理傳統，特別保障牧首與大總主教制等東方固有體制。此法典與一九八三年拉丁法典共同構成天主教會的「一部法典」（Corpus），體現梵二對東方傳統多元性的肯定。', link: '/canon-law' },
          { title_zh: '天主教教理', title_orig: 'Catechismus Catholicae Ecclesiae (CCC)', author: '教宗若望保祿二世頒布（拉辛格樞機主編委會）', era: '1992／拉丁文定本 1997', place: '羅馬梵蒂岡', language: '拉丁文（原）／繁體中文、英文（譯）', intro: '天主教教理由教宗若望保祿二世於一九九二年頒布，編纂委員會由拉辛格樞機（後為教宗本篤十六世）主持，是繼特倫多教理後天主教首部全面的官方教理。全書依信經、聖事、誡命、祈禱四大部分組織，系統陳述天主教的信仰、禮儀、道德與祈禱生活，並大量徵引聖經、教父與梵二文獻。此教理為當代天主教信仰教導提供權威基準，廣被各地教會作為教學與要理講授的依據。' }
        ]
      },
      {
        key: 'ecumenical-documents',
        label: '普世合一文件部',
        label_en: 'Ecumenical Movement Documents',
        desc: '本律藏主軸：自一九一〇年愛丁堡會議以降的普世合一運動歷次里程碑文獻，記錄分裂教會走向合一與相互承認的歷程。',
        works: [
          { title_zh: '愛丁堡世界宣教會議報告', title_orig: 'World Missionary Conference, Edinburgh 1910 (Reports)', author: '世界宣教會議大會（穆德等主持）', era: '1910', place: '蘇格蘭愛丁堡', language: '英文（原）／繁體中文（譯）', intro: '一九一〇年愛丁堡世界宣教會議公認為現代普世合一運動的起點。來自全球新教各宗派的逾千名代表齊聚，在穆德（John R. Mott）等人領導下，圍繞八大委員會報告探討宣教合作，並深刻意識到宗派分裂對宣教使命的妨礙。會議催生了日後的「國際宣教協會」、「生活與工作」及「信仰與教制」三大運動，最終匯流為世界基督教協進會。其名言「我們這一代人完成普世宣教」標誌了二十世紀基督教合一意識的覺醒。' },
          { title_zh: '信仰與教制運動文獻', title_orig: 'Faith and Order Movement Documents', author: '信仰與教制委員會（首任主持布倫特主教）', era: '1927 洛桑首屆起', place: '瑞士洛桑、英國等', language: '英文（原）／繁體中文（譯）', intro: '信仰與教制運動源於愛丁堡會議後美國聖公會布倫特主教的倡議，於一九二七年在瑞士洛桑召開首屆世界大會，專門處理阻礙教會合一的教義、聖禮與教制分歧。有別於著重實踐合作的「生活與工作」運動，信仰與教制直面神學差異，循序探討聖經、信經、聖職與聖禮等議題。此運動後併入世界基督教協進會成為其重要委員會，其數十年的神學對話最終結晶為《洗禮、聖餐與聖職》（利馬文件）。' },
          { title_zh: '生活與工作運動文獻', title_orig: 'Life and Work Movement Documents (Stockholm 1925)', author: '生活與工作運動（瑞典大主教瑟德布盧姆倡議）', era: '1925 斯德哥爾摩首屆起', place: '瑞典斯德哥爾摩', language: '英文（原）／繁體中文（譯）', intro: '生活與工作運動由瑞典大主教瑟德布盧姆倡議，於一九二五年在斯德哥爾摩召開首屆世界大會，與「信仰與教制」並列為普世合一運動的兩大支柱。有別於後者著重教義對話，本運動主張「教義使我們分裂，服務使我們聯合」，聚焦於各教會在社會、經濟與國際和平議題上的共同實踐。它後與信仰與教制合流，於一九四八年共同組成世界基督教協進會，是現代教會社會關懷的合一先聲。' },
          { title_zh: '世界基督教協進會成立文件', title_orig: 'Constitution of the World Council of Churches (Amsterdam 1948)', author: '世界基督教協進會第一屆大會', era: '1948', place: '荷蘭阿姆斯特丹', language: '英文（原）／繁體中文（譯）', intro: '世界基督教協進會（WCC）於一九四八年在阿姆斯特丹召開首屆大會正式成立，匯合「信仰與教制」與「生活與工作」兩大運動，成為現代普世合一運動的制度核心。其成立基礎宣言界定 WCC 為「承認主耶穌基督為神與救主的眾教會的團契」，後於新德里大會（一九六一）擴充為三一論的基礎。如今 WCC 涵蓋逾三百五十個東正教、聖公會與新教宗派，是二十世紀基督教合一最具體的組織成果。', link: '/creeds' },
          { title_zh: '利馬文件', title_orig: 'Baptism, Eucharist and Ministry (BEM, Lima 1982)', author: '世界基督教協進會信仰與教制委員會', era: '1982', place: '秘魯利馬', language: '英文（原）／繁體中文（譯）', intro: '利馬文件，全名《洗禮、聖餐與聖職》，由 WCC 信仰與教制委員會於一九八二年在秘魯利馬通過，是普世合一運動逾半世紀神學對話的重大結晶。文件就向來分裂教會的三大聖禮與聖職議題尋求最大共識，呈現了天主教、東正教、聖公會與各新教傳統可共同肯認的神學基礎。各宗派的正式回應匯成數卷，本身即推進了相互理解。利馬文件被譽為二十世紀最廣受研讀的合一文獻，深刻形塑了當代各教會的聖禮神學。', link: '/creeds' },
          { title_zh: '因信稱義聯合聲明', title_orig: 'Joint Declaration on the Doctrine of Justification (JDDJ)', author: '羅馬天主教會與世界信義宗聯會', era: '1999', place: '德國奧格斯堡', language: '英文、德文（原）／繁體中文（譯）', intro: '因信稱義聯合聲明由羅馬天主教會與世界信義宗聯會於一九九九年在奧格斯堡共同簽署，就十六世紀宗教改革分裂的核心爭議——稱義教義——達成基礎共識，宣告雙方在此議題上彼此的譴責已不再適用於對方今日的教導。此歷史性文件化解了路德與天主教近五百年的根本對立，後並獲衛理公會（二〇〇六）、改革宗（二〇一七）與聖公會（二〇一七）認同加入，成為普世合一運動最具突破性的教義共識之一。', link: '/creeds' },
          { title_zh: '聖公會–羅馬天主教國際委員會文件', title_orig: 'ARCIC: Anglican–Roman Catholic International Commission', author: '聖公宗與羅馬天主教聯合委員會', era: '1970 起', place: '英國溫莎等', language: '英文（原）／繁體中文（譯）', intro: 'ARCIC 是聖公宗與羅馬天主教會於梵二後設立的正式神學對話機制，自一九七〇年起運作。委員會就向來分裂兩個傳統的核心議題——聖餐、聖職與按立、教會權威——發表一系列共同聲明，在諸多爭議上達成可觀的趨同。雖未促成完全的教會合一，其文件被視為雙邊合一對話的典範，展現了梵二《大公主義法令》所開啟的對話如何具體推進，深刻影響兩宗派的相互理解。' },
          { title_zh: '天主教–東正教聯合神學對話文件', title_orig: 'Joint Catholic–Orthodox Theological Dialogue (incl. Ravenna 2007)', author: '天主教與東正教聯合國際委員會', era: '1980 起', place: '帕特莫斯‧拉文納等', language: '英文、法文（原）／繁體中文（譯）', intro: '天主教與東正教自一九八〇年起設立聯合國際委員會，重啟自一〇五四年東西教會大分裂以來的正式神學對話。委員會就聖事、教會的聖統與共融等議題發表多份共同文件，其中二〇〇七年的《拉文納文件》就「教會性與權威」達成重要共識，並首度共同探討羅馬主教首席權的歷史角色。此對話雖仍面臨首席權等難題，卻是化解千年東西裂痕、邁向完全共融最受矚目的努力。' },
          { title_zh: '教會：邁向共同願景', title_orig: 'The Church: Towards a Common Vision', author: '世界基督教協進會信仰與教制委員會', era: '2013', place: '瑞士日內瓦', language: '英文（原）／繁體中文（譯）', intro: '《教會：邁向共同願景》由世界基督教協進會信仰與教制委員會於二〇一三年發表，是繼一九八二年《利馬文件》之後又一份里程碑式的合一文獻。文件首度嘗試就「教會的本質與使命」這一更根本的議題凝聚跨宗派共識，闡述教會作為三一上帝共融標記的神學，並坦陳各傳統在聖統、權威與倫理判斷上仍存的分歧。它代表普世合一運動從聖禮共識邁向教會論共識的新階段，是當代合一神學的重要參照。' }
        ]
      },
      {
        key: 'protestant-confessions',
        label: '新教與福音派信條部',
        label_en: 'Modern Protestant and Evangelical Confessions',
        desc: '二十世紀新教與福音派為回應時代挑戰所訂立的現代信條與宣言，界定信仰立場並凝聚跨宗派認同。',
        works: [
          { title_zh: '巴門神學宣言', title_orig: 'Die Barmer Theologische Erklärung', author: '德國認信教會（巴特起草）', era: '1934', place: '德國巴門', language: '德文（原）／繁體中文（譯）', intro: '巴門神學宣言由德國認信教會於一九三四年五月在巴門召開的首屆認信會議通過，主要起草人為神學家巴特。面對納粹支持的「德意志基督徒」運動企圖將教會納粹化，宣言以六項論題堅決重申耶穌基督是教會唯一的話語與主，斷然拒絕任何將其他權威（種族、民族、元首）置於基督之上的主張。此宣言是二十世紀基督教抵抗極權政治意識形態最堅定的信仰表態，至今仍是改革宗與信義宗傳統的重要認信文獻。', link: '/creeds' },
          { title_zh: '洛桑信約', title_orig: 'The Lausanne Covenant', author: '世界福音洛桑會議（斯托得主筆）', era: '1974', place: '瑞士洛桑', language: '英文（原）／繁體中文（譯）', intro: '洛桑信約由一九七四年在瑞士洛桑召開的世界福音會議通過，主要文字出自斯托得（John Stott）之手，是當代福音派最重要的綱領性文獻。信約以十五條重申聖經權威、基督獨一救恩與全球福音使命，同時突破性地將社會關懷與福音佈道並列為基督徒不可分割的責任。此信約凝聚了全球福音派的共同認同，催生了持續至今的洛桑運動，成為與普世合一運動並行的另一股跨宗派合作力量。', link: '/creeds' },
          { title_zh: '芝加哥聖經無誤宣言', title_orig: 'The Chicago Statement on Biblical Inerrancy', author: '國際聖經無誤協會', era: '1978', place: '美國芝加哥', language: '英文（原）／繁體中文（譯）', intro: '芝加哥聖經無誤宣言由國際聖經無誤協會於一九七八年在芝加哥發表，是逾三百位福音派學者回應現代自由派神學與高等批判的集體表態。宣言以十九條「肯定與否定」條款，系統界定「聖經無誤」（inerrancy）的內涵，主張聖經在其原稿中於一切所及之事上皆真確無誤。此文件成為當代福音派聖經觀的標準陳述，深刻影響了北美及全球保守派神學院與教會的釋經立場，亦標誌了福音派與自由派在聖經權威上的分野。', link: '/creeds' }
        ]
      }
    ]
  },
  wai: {
    summary: '外經部收錄現代基督教正統規範之外、卻與基督教世界密切互動的規範性文本：一為脫胎於基督教傳統的新興宗教所訂教規與倫理，二為界定現代政教關係的世俗法律與宗教自由公約。二者皆是理解基督教在現代多元社會中處境的重要參照。',
    divisions: [
      {
        key: 'new-religious-codes',
        label: '新興宗教法典部',
        label_en: 'New Religious Movement Codes',
        desc: '十九世紀末至當代由新興宗教與靈性運動所訂立的現代教規與倫理規範，多與基督教傳統有淵源或對話。',
        works: [
          { title_zh: '教義與聖約', title_orig: 'Doctrine and Covenants', author: '耶穌基督後期聖徒教會（小斯密及後繼會長）', era: '1835 初版／持續增補至當代', place: '美國', language: '英文（原）／繁體中文（譯）', intro: '教義與聖約是耶穌基督後期聖徒教會（摩門教）的標準經典之一，收錄該教自小斯密以降歷任會長所宣稱領受的「現代啟示」，內容涵蓋教會組織、聖職體制、聖殿教儀與生活誡命（如智慧語）。有別於古代經文，此書持續開放增補，例如一八九〇年停止多妻制的「正式宣言」與一九七八年向所有種族開放聖職的啟示皆收錄其中，是理解摩門教現代教規與制度演變的核心規範文本。' },
          { title_zh: '新世紀運動倫理文獻', title_orig: 'New Age Movement Ethical Writings', author: '新世紀運動諸作者（無統一權威）', era: '1970s 起', place: '歐美', language: '英文（原）／繁體中文（譯）', intro: '新世紀運動並非單一組織，而是二十世紀後期興起的鬆散靈性潮流，其倫理規範散見於各家著作而無統一權威經典。此類文獻普遍主張萬物一體、自我神性、業力因果與靈性進化，強調個人靈性自主、整全療癒（holistic healing）與地球生態關懷。其倫理觀融合東方宗教、神智學與心理學元素，並選擇性挪用基督教語彙。本部收錄此類代表性倫理書寫，以呈現現代後基督教靈性對傳統規範的解構與重構。' }
        ]
      },
      {
        key: 'secular-church-state',
        label: '世俗與政教法部',
        label_en: 'Secular and Church-State Law',
        desc: '現代界定宗教與國家關係、保障宗教自由的世俗憲法與國際公約，構成當代基督教存在的法律處境。',
        works: [
          { title_zh: '美國憲法第一修正案', title_orig: 'First Amendment to the United States Constitution', author: '美國國會（權利法案）', era: '1791／二十世紀司法詮釋', place: '美國', language: '英文（原）／繁體中文（譯）', intro: '美國憲法第一修正案以「設立條款」與「自由實踐條款」確立政教分離與宗教自由的原則，雖訂於一七九一年，其在現代政教關係上的決定性意涵卻是透過二十世紀美國最高法院的一系列判決（如禁止公校禱告、界定政府中立）逐步展開。此修正案成為現代民主國家處理政教關係的典範文本，深刻形塑了二十世紀以降基督教在世俗多元社會中的法律地位，亦引發政教界線的持續辯論。' },
          { title_zh: '消除基於宗教或信仰原因的歧視宣言', title_orig: 'Declaration on the Elimination of All Forms of Intolerance and of Discrimination Based on Religion or Belief', author: '聯合國大會', era: '1981', place: '美國紐約聯合國', language: '英文（原）／繁體中文（譯）', intro: '此宣言由聯合國大會於一九八一年通過，是國際社會保障宗教與信仰自由最重要的專門文件之一。宣言重申世界人權宣言所載思想、良心與宗教自由的權利，具體列舉信奉、實踐、禮拜與教導宗教的各項自由，並譴責一切基於宗教或信仰的不容忍與歧視。此文件為各國保障宗教少數、處理政教關係提供了國際規範基準，反映二十世紀後期普世人權框架下宗教自由的法律化進程。' }
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
  genres: '系統神學‧處境神學‧哲學',
  summary: '一九〇〇年以降的基督教義理論著總匯。新正統與辯證神學在一戰廢墟上重提「上帝是上帝」，存在神學、過程神學接續自由派傳統，天主教在梵二前後重構現代神學語彙，解放與處境神學從第三世界、女性與黑人經驗發聲，福音派護教學與漢語神學各成一脈。外編則收無神論批判、新興宗教神學與宗教多元論，以見現代基督教義理所面對的思想對話面。',
  zheng: {
    summary: '正編按義理路線分六部：以巴特為首的新正統與辯證神學部矯正自由派樂觀；自由與存在神學部承士萊馬赫而至田立克；天主教現代神學部鋪墊並回應梵二；處境與解放神學部從受壓迫者立場重讀福音；福音派與護教部守正統又向現代人說話；漢語神學部記華人本色神學的探索。',
    divisions: [
      {
        key: 'neo-orthodox',
        label: '新正統與辯證神學部',
        label_en: 'Neo-Orthodoxy and Dialectical Theology',
        desc: '一戰後對自由派文化樂觀的決裂，重申上帝的他在性與啟示的優先。',
        works: [
          { title_zh: '羅馬書釋義', title_orig: 'Der Römerbrief', author: '巴特（Karl Barth）', era: '1919／1922', place: '瑞士', language: '德文', intro: '巴特在一戰崩解的廢墟中重讀保羅，以「上帝是上帝，人是人」的無限質的差異，向十九世紀自由派文化神學投下炸彈。書中強調啟示的垂直突入、罪與恩典的辯證張力，宣告人不能由文化、道德或宗教經驗攀向上帝，唯上帝俯就自啟。此書奠定辯證神學運動，是二十世紀新正統的開山之作，影響遍及歐陸與英語世界。' },
          { title_zh: '教會教義學', title_orig: 'Die Kirchliche Dogmatik', author: '巴特（Karl Barth）', era: '1932–1967', place: '瑞士', language: '德文', intro: '巴特畢生未竟的鉅構，逾六百萬言十三冊，以耶穌基督為一切教義的中心與量度，從上帝聖言論、上帝論、創造論到和好論層層開展。他重構揀選論，主張基督既是揀選的上帝也是被揀選的人，揚棄雙重預定的陰影。全書以基督論貫穿、嚴拒自然神學，被視為改教傳統以降最浩瀚的系統神學，是現代教義學無可繞過的高峰。' },
          { title_zh: '相遇中的真理', title_orig: 'Wahrheit als Begegnung', author: '布倫納（Emil Brunner）', era: '1938', place: '瑞士', language: '德文', intro: '布倫納與巴特同屬辯證神學陣營，卻在「自然神學」與「接觸點」議題上與之決裂。他主張人雖墮落仍存上帝形像的形式殘餘，可作啟示的接觸點，真理不是抽象命題而是位格的相遇。本書發展其「我與你」的真理觀，將位格相遇置於信仰知識論核心，是新正統內部分歧與人格主義神學的重要文獻。' },
          { title_zh: '新約與神話學', title_orig: 'Neues Testament und Mythologie', author: '布特曼（Rudolf Bultmann）', era: '1941', place: '德國', language: '德文', intro: '布特曼提出「去神話化」綱領，主張新約以第一世紀神話宇宙觀包裹福音，現代人無法照字面接受，須以存在主義詮釋抽繹其生存呼召。福音的核心不在神蹟史實而在向人發出的本真存在抉擇。此文引爆二十世紀最激烈的詮釋學論戰，深刻形塑歷史耶穌研究、聖經詮釋與存在神學的走向。' },
          { title_zh: '作門徒的代價', title_orig: 'Nachfolge', author: '潘霍華（Dietrich Bonhoeffer）', era: '1937', place: '德國', language: '德文', intro: '潘霍華在納粹陰影下寫成，痛斥「廉價恩典」即不需悔改、不需作門徒的恩典，呼籲信徒付上「重價恩典」的代價跟隨基督。書中以登山寶訓為核心，闡明順服與信心不可分割，呼召教會在極權時代具體地背十字架。此書是二十世紀屬靈經典，亦預示作者日後以身殉道的抉擇。' },
          { title_zh: '人的本性與命運', title_orig: 'The Nature and Destiny of Man', author: '尼布爾（Reinhold Niebuhr）', era: '1941–1943', place: '美國', language: '英文', intro: '尼布爾的吉福德講座，以基督教現實主義剖析人性。他主張人既是受造有限又有自我超越，焦慮中以驕傲與情慾陷入罪，個人或可成聖而群體罪性難除。本書批判自由派的進步樂觀與正統的悲觀宿命，重提原罪的現實意涵，深刻影響美國公共神學、政治倫理與冷戰時代的道德思考。' }
        ,
          { title_zh: '教義學綱要', title_orig: 'Dogmatik im Grundriss', author: '巴特（Karl Barth）', era: '1947', place: '瑞士蘇黎世-佐利孔（講座於德國波昂）', language: '德文', intro: '巴特戰後重返波昂的講座結集，依《使徒信經》逐條開展，是其浩瀚《教會教義學》的精要普及版。他以耶穌基督為一切教義的中心與量度，簡明闡述上帝、創造、和好與盼望，文字凝練而充滿牧養關懷。此書被視為認識巴特神學最佳入門，亦見證一位神學家在廢墟之中對信仰根基的重述，影響遍及歐陸與英語世界。' },
          { title_zh: '信仰尋求理解', title_orig: 'Fides Quaerens Intellectum: Anselms Beweis der Existenz Gottes im Zusammenhang seines theologischen Programms', author: '巴特（Karl Barth）', era: '1931', place: '德國', language: '德文', intro: '巴特研究安瑟倫存在論證的專著，是他神學方法的轉捩之作。他主張安瑟倫的論證並非中立理性的自然神學，而是「信仰尋求理解」的內在運動——人惟在信仰中、在上帝自我啟示的光照下，方能領會上帝的實在。此書界定了巴特後期《教會教義學》拒斥自然神學、以啟示為唯一起點的方法論，是理解辯證神學知識論的關鍵文本。' },
          { title_zh: '神‧人', title_orig: 'Gott und Mensch', author: '布倫納（Emil Brunner）', era: '1930', place: '瑞士蘇黎世', language: '德文', intro: '布倫納辯證神學時期的論文結集，闡述上帝與人之間因罪而生的斷裂，以及惟靠基督方能跨越的鴻溝。他主張神學的任務在於忠實見證上帝的話語，而非建構人本的宗教哲學。書中既與自由派劃清界線，又流露其日後與巴特分歧的人格主義端倪，是辯證神學運動內部思想的重要文獻。' },
          { title_zh: '道德的人與不道德的社會', title_orig: 'Moral Man and Immoral Society', author: '尼布爾（Reinhold Niebuhr）', era: '1932', place: '美國紐約', language: '英文', intro: '尼布爾基督教現實主義的奠基之作。他剖析個人雖能臻於相當的道德，群體與社會卻受集體自利驅使而難以超越自身利益，故社會正義無法僅靠道德感化達成，必須訴諸權力的制衡。此書批判自由派對人性與進步的樂觀，重提原罪在政治社會層面的現實意涵，深刻形塑二十世紀美國的公共神學與政治倫理。' },
          { title_zh: '作為世界奧秘的上帝', title_orig: 'Gott als Geheimnis der Welt', author: '雲格爾（Eberhard Jüngel）', era: '1977', place: '德國杜賓根', language: '德文', intro: '雲格爾承巴特與布特曼之後，回應現代無神論對上帝可思性的質疑。他主張須從被釘十字架的耶穌出發重思上帝，「上帝之死」並非否定而是揭示上帝在愛中與必死者認同。書中以「上帝是愛」為核心，論述上帝的可言說性與三一存有。此書是二十世紀後期德語神學最具思辨深度的著作之一，深化了十字架神學與三一論的現代表述。' },
          { title_zh: '三一與上帝國', title_orig: 'The Trinity and the Kingdom', author: '莫特曼（Jürgen Moltmann）', era: '1980', place: '德國慕尼黑（München）', language: '德文', intro: '莫特曼的社會三一論代表作（德文原題 Trinität und Reich Gottes）。他批判西方一神論與君主制神觀對政治壓迫的助長，主張以三一位格間相互內在（perichoresis）的團契為範式，建構一種彼此關連、開放受苦的上帝觀，並引申出反對宰制的社會與教會願景。此書將三一論從抽象教義轉為具批判力的政治神學資源，影響當代三一論的復興。' },
          { title_zh: '不！答布倫納', title_orig: 'Nein! Antwort an Emil Brunner', author: '巴特（Karl Barth）', era: '1934', place: '瑞士／德國', language: '德文', intro: '巴特針對布倫納〈自然與恩典〉的激烈駁論。布倫納主張人墮落後仍存「接觸點」與自然啟示的可能，巴特斷然以「不！」回應，堅決否定任何自然神學，認為這正是德國基督徒迎合納粹的神學病根。此文標誌辯證神學內部巴特與布倫納的決裂，是二十世紀「自然神學論戰」最尖銳的文獻，界定了新正統對啟示獨一性的立場。' },
          { title_zh: '基督與文化', title_orig: 'Christ and Culture', author: '理查‧尼布爾（H. Richard Niebuhr）', era: '1951', place: '美國', language: '英文', intro: '理查‧尼布爾以「基督與文化」的張力為軸，歸納基督教史上五種典型立場：基督反乎文化、基督屬乎文化、基督在文化之上、基督與文化弔詭並立、基督轉化文化。他剖析各型的洞見與限度而傾向轉化論。此書成為討論信仰與文化關係繞不開的經典框架，深刻影響神學、倫理與宣教思考，至今仍是相關論辯的起點。' }
        ,
          { title_zh: '為眾人：合乎福音精神的新教神學', title_orig: 'Einer für Alle: Evangelische Theologie im Geist des Evangeliums', author: '達爾費特（Ingolf U. Dalferth）', era: '2026', place: '德國萊比錫', language: '德文', intro: '達爾費特（Ingolf U. Dalferth）為當代著名新教系統神學家，長期執教蘇黎世大學與克萊蒙特神學院。本書以「為眾人之一」為核心命題，從基督代贖的結構出發，系統闡述新教神學在福音精神中的內在邏輯，涵蓋神學認識論、基督論與救贖論的整合論述。全書屬原創系統神學著作，代表當代德語新教神學的前沿思考，與巴特、潘能伯格傳統一脈相承。' }
        ]
      },
      {
        key: 'liberal-existential',
        label: '自由與存在神學部',
        label_en: 'Liberal and Existential Theology',
        desc: '承士萊馬赫的近代自由傳統，發展出存在主義與過程的神學表述。',
        works: [
          { title_zh: '論宗教', title_orig: 'Über die Religion', author: '士萊馬赫（Friedrich Schleiermacher）', era: '1799', place: '德國', language: '德文', intro: '近代神學之父士萊馬赫的早期名著，雖成於十九世紀之前，卻是現代自由神學與宗教研究的源頭活水，故承先列此。他向「有教養的蔑視宗教者」申辯，主張宗教的本質既非教義亦非道德，而是「絕對倚賴感」的直觀與情感。此說將神學奠基於宗教經驗，開啟以人的意識為起點的近代神學典範，影響田立克以降整條自由派脈絡。' },
          { title_zh: '系統神學', title_orig: 'Systematic Theology', author: '田立克（Paul Tillich）', era: '1951–1963', place: '美國', language: '英文', intro: '田立克的三卷鉅著，以「關聯法」展開：由人的存在處境提問，由基督教啟示作答。他將上帝定義為「存在本身」與「終極關懷」，論述存在的勇氣、新存有的耶穌基督與聖靈中的生命。全書熔哲學、存在主義與神學於一爐，是二十世紀少數可與巴特並峙的系統神學鉅構，深刻形塑現代宗教思想的語彙。' },
          { title_zh: '存在的勇氣', title_orig: 'The Courage to Be', author: '田立克（Paul Tillich）', era: '1952', place: '美國', language: '英文', intro: '田立克最廣為流傳的小書，剖析現代人面對命運與死亡、空虛與無意義、罪咎與譴責三重焦慮。他主張真正的勇氣是「縱然如此仍然存在」，其根基在於人被「超越上帝的上帝」即存在本身所接納。此書將存在主義哲學與信仰交融，為信仰危機中的現代人提供出路，是宗教與哲學跨界的經典之作。' },
          { title_zh: '過程與實在', title_orig: 'Process and Reality', author: '懷德海（Alfred North Whitehead）', era: '1929', place: '美國', language: '英文', intro: '懷德海的歷程哲學鉅著，雖屬哲學，卻是過程神學的根本基礎，故列此承先。他以「實際存在」與「攝受」重構形上學，主張實在是流變生成而非靜態實體，上帝亦有「原初本性」與「後得本性」雙極，與世界互相影響、共同生成。哈茨霍恩、科布等承之發展出強調上帝可變、與世界共受的過程神學，挑戰古典的全能不變上帝觀。' }
        ,
          { title_zh: '神的相對性：上帝的社會性概念', title_orig: 'The Divine Relativity: A Social Conception of God', author: '哈茨霍恩（Charles Hartshorne）', era: '1948', place: '美國紐黑文（耶魯大學出版社，New Haven）', language: '英文', intro: '哈茨霍恩承懷德海歷程哲學而開展過程神學的奠基之作，源自其耶魯講座。他批判古典有神論將上帝設想為絕對不變者乃自相矛盾，主張上帝具雙極性：抽象本質恆常，具體面則與世界相互關連、共同生成、能受感動。他稱此立場為「超相對主義」或泛在神論。此書是過程神學最重要的哲學基石之一，深刻挑戰全能不變的傳統上帝觀，影響科布、葛里芬等整條過程神學脈絡。' },
          { title_zh: '過程神學：導論性闡述', title_orig: 'Process Theology: An Introductory Exposition', author: '科布（John B. Cobb, Jr.）、葛里芬（David Ray Griffin）', era: '1976', place: '美國費城（Philadelphia）', language: '英文', intro: '過程神學最廣為流傳的入門系統著作，由該學派兩位代表人物合著。書中梳理懷德海與哈茨霍恩哲學的基本概念（現實事態、攝受、創造性、上帝的原初與後得本性），並以此建構一套關於上帝、基督、教會、末世與倫理的歷程式神學綱要，逐章處理上帝論、基督論、人的存在與末世論，長期作為神學院過程神學教科書。', extent: '192 pp.' },
          { title_zh: '上帝的真實性及其他論文', title_orig: 'The Reality of God and Other Essays', author: '奧格登（Schubert M. Ogden）', era: '1966', place: '美國紐約（Harper & Row, New York）', language: '英文', intro: '奧格登過程神學與去神話化詮釋結合的代表論文集。他援哈茨霍恩的過程形上學，並批判性地接合布特曼的存在主義，主張上帝具「時間性」，而對生命意義與價值的根本信靠即是對上帝的隱含信仰。書收〈上帝的真實性〉〈上帝的時間性〉〈說「上帝在歷史中行動」有何意義〉〈神話與真理〉等篇。此書是北美過程神學由哲學轉入神學言說的關鍵文本，亦是過程神學與世俗神學交會的代表作。', extent: '237 pp.' },
          { title_zh: '上帝、權能與惡：一種過程神義論', title_orig: 'God, Power, and Evil: A Process Theodicy', author: '葛里芬（David Ray Griffin）', era: '1976', place: '美國費城（Westminster Press, Philadelphia）', language: '英文', intro: '葛里芬以過程哲學重構神義論的力作。他先批判性地檢視柏拉圖、奧古斯丁、阿奎那、加爾文、萊布尼茲、巴特、希克等西方神義論傳統，再從懷德海與哈茨霍恩的進路提出建構性方案：揚棄「無條件全能」的傳統假設，主張創造性大能內在於整個現實界，故上帝的作為是勸服而非強制。此書是過程神學處理惡與苦難問題最系統的著作。', extent: '336 pp.' },
          { title_zh: '言與信', title_orig: 'Wort und Glaube', author: '艾貝林（Gerhard Ebeling）', era: '德文1960／英譯1963', place: '德國杜賓根（J. C. B. Mohr [Paul Siebeck], Tübingen）', language: '德文', intro: '艾貝林新詮釋學神學的代表論文集，收十八篇開創性文章，含〈批判歷史方法對教會與神學的意義〉〈上帝的話與詮釋學〉〈耶穌與信仰〉等。他承布特曼而提出「言語事件」（Wortgeschehen）概念，主張神學真理並非靜態命題，而在詮釋的事件中生成；福音是向人發出、促成信仰的言說。他與福克斯並為二十世紀「新詮釋學」運動的領袖，此書深刻形塑現代詮釋學神學的走向。' },
          { title_zh: '詮釋學', title_orig: 'Hermeneutik', author: '福克斯（Ernst Fuchs）', era: '1954', place: '德國巴特坎施塔特（Bad Cannstatt）', language: '德文', intro: '福克斯為布特曼門生，與艾貝林同為二十世紀「新詮釋學」運動領袖。本書系統論述其詮釋學神學，以海德格後期語言哲學為基底，發展「語言事件」概念，主張上帝之言在講道與信仰的語言事件中臨在，使聖經在現今與人相遇、挑戰人作出抉擇、喚醒信心並成就救恩，對歷史耶穌與宣講的關係提出新解。' },
          { title_zh: '基督教神學原理', title_orig: 'Principles of Christian Theology', author: '麥奎利（John Macquarrie）', era: '1966', place: '英國／美國（SCM／Scribner）', language: '英文', intro: '麥奎利以海德格存在主義為哲學進路所撰的系統神學巨著，被視為二十世紀英語世界存在主義神學的代表性系統陳述。全書分「哲學神學」「象徵神學」「應用神學」三部，從人之存在分析入手，重述上帝、創造、基督、教會與聖禮諸教義，調和巴特與布特曼兩路傳統。' },
          { title_zh: '思維與存在：海德格之路與神學之路', title_orig: 'Denken und Sein: Der Weg Martin Heideggers und der Weg der Theologie', author: '奧特（Heinrich Ott）', era: '1959', place: '瑞士措利孔（Zollikon），福音出版社（Evangelischer Verlag）', language: '德文', intro: '奧特繼巴特之後任巴塞爾大學系統神學講席，師承巴特與布特曼。本書被譽為「為後期海德格做了布特曼為前期海德格所做之事」，循海德格後期思想探討存在、語言與神學之路的會通，是存在詮釋神學承先啟後的重要著作。', extent: '226 頁' }
        ]
      },
      {
        key: 'catholic-modern',
        label: '天主教現代神學部',
        label_en: 'Modern Catholic Theology',
        desc: '梵二前後的天主教神學更新，從新士林到教義發展與宇宙基督論。',
        works: [
          { title_zh: '神學探究', title_orig: 'Schriften zur Theologie', author: '拉納（Karl Rahner）', era: '1954–1984', place: '德國／奧地利', language: '德文', intro: '拉納以二十餘卷論文集重塑二十世紀天主教神學。他以先驗方法主張人本性即向無限開放的「奧秘之聆聽者」，提出「超驗基督論」與「匿名基督徒」說，肯定恩典普世臨在於人的存在結構。其思想是梵二的重要神學動力，調和士林傳統與現代主體哲學，影響遍及天主教神學各領域。' },
          { title_zh: '榮耀的神學', title_orig: 'Herrlichkeit', author: '巴爾塔薩（Hans Urs von Balthasar）', era: '1961–1969', place: '瑞士', language: '德文', intro: '巴爾塔薩三部曲之首，以「美」為起點重建神學美學，主張上帝的榮耀在基督裡自我彰顯為可被人感知的形式。他批判將神學化約為人類學或倫理學，力倡客觀啟示之美的優先。全書熔教父、神祕主義與文學於一爐，與拉納路線分庭抗禮，是當代天主教最具原創性的鉅構之一。' },
          { title_zh: '基督教教義發展論', title_orig: 'An Essay on the Development of Christian Doctrine', author: '紐曼（John Henry Newman）', era: '1845', place: '英國', language: '英文', intro: '紐曼歸信天主教之際的劃時代著作，雖成於十九世紀，卻是現代教義發展理論的根本，故承先列此。他提出教義如種子般在歷史中有機發展，並列七項判準辨別真正發展與訛變。此說化解新教對天主教「增添」教義的指控，深刻影響梵二的歷史意識與啟示觀，至今仍是論教義演變繞不開的經典。' },
          { title_zh: '神的氛圍', title_orig: 'Le Milieu Divin', author: '德日進（Pierre Teilhard de Chardin）', era: '1957', place: '法國', language: '法文', intro: '耶穌會古生物學家德日進的靈修名著，將演化宇宙觀與基督信仰結合。他主張整個受造界正朝「奧米加點」即宇宙基督收歛進化，人的工作與受苦皆可在神的氛圍中聖化，物質與屬靈交融為一。此書因觀點新穎生前未獲教廷出版許可，身後刊行，深刻影響生態神學與宇宙基督論。' }
        ,
          { title_zh: '信仰的基礎課程：基督教概念導論（英譯：基督信仰的基礎）', title_orig: 'Grundkurs des Glaubens: Einführung in den Begriff des Christentums', author: '拉納（Karl Rahner）', era: '1976', place: '德國／奧地利', language: '德文', intro: '拉納晚年對其畢生神學的系統總綱，1976 年由 Herder（Freiburg）出版。他以先驗（超驗）方法從人作為「向無限開放的超驗主體」出發，循序論述上帝、基督、教會與恩典，提出「匿名基督徒」與「超驗基督論」等標誌性命題。此書是其多卷論文集《神學探究》（Schriften zur Theologie / Theological Investigations）之外，唯一一部整全的單卷系統導論，調和士林傳統與現代主體哲學（特重海德格），是理解梵二後天主教神學主流路線繞不開的核心著作。' },
          { title_zh: '神劇', title_orig: 'Theodramatik', author: '巴爾塔薩（Hans Urs von Balthasar）', era: '1973–1983', place: '瑞士', language: '德文', intro: '巴爾塔薩神學三部曲之第二部，繼《榮耀的神學》論「美」之後，以「善」為主軸，借戲劇範疇展開救恩史。他將上帝與世界的關係視為一齣神聖戲劇，人在自由中回應上帝的召喚，基督的降臨、受難與復活是劇情高潮。全書熔神學、哲學與戲劇美學於一爐，是當代天主教最具原創性的救恩論與自由論建構。' },
          { title_zh: '公教精神', title_orig: 'Catholicisme: les aspects sociaux du dogme', author: '呂巴克（Henri de Lubac）', era: '1938', place: '法國巴黎（出版地，Éditions du Cerf, Paris）', language: '法文', intro: '呂巴克「新神學」運動的奠基之作。他回到教父傳統，力陳天主教信仰本質上是社會性與普世性的，救恩不是個人靈魂的私事，而是全人類在基督裡的團契與共融。此書批判近代個人主義式的虔敬，重申教會作為人類合一聖事的意義，為梵二的教會論與普世關懷鋪路，是二十世紀回歸教父源頭神學運動的代表。' },
          { title_zh: '教會中的真假改革', title_orig: 'Vraie et fausse réforme dans l\'Église', author: '孔加爾（Yves Congar）', era: '1950', place: '法國', language: '法文', intro: '孔加爾論教會改革的劃時代著作。他區辨真正的改革——在忠於信仰本質中回應歷史召喚、由內更新——與導致分裂的假改革，主張教會既需在歷史中不斷更新，又須保守其神聖認同。此書一度受教廷限制，卻深刻啟發梵二的更新精神（aggiornamento）與普世合一視野，是現代天主教改革神學與教會論的關鍵文獻。' },
          { title_zh: '成義／稱義', title_orig: 'Rechtfertigung: Die Lehre Karl Barths und eine katholische Besinnung', author: '孔漢思（Hans Küng）', era: '1957', place: '瑞士／德國', language: '德文', intro: '孔漢思的博士論文，以巴特的稱義論為對話對象，論證天主教教義與新教改革的稱義觀在根本上可以會通。此書在天主教與新教三百年隔閡之後重啟稱義論對話，巴特本人並為之背書認同。它預示了梵二的普世合一精神，亦是日後《天主教與信義宗稱義教義聯合聲明》的思想先聲，是現代合一神學的里程碑之作。' },
          { title_zh: '超性', title_orig: 'Surnaturel. Études historiques', author: '呂巴克（Henri de Lubac）', era: '1946', place: '法國', language: '法文', intro: '呂巴克最具爭議與影響力的歷史神學研究。他考掘士林傳統，質疑後期經院區分「純自然」與「超性」的二層架構，主張人受造即有對享見天主的自然渴望，恩典與本性不可全然割裂。此書引發天主教內部激烈論戰、一度受教廷壓制，卻深刻翻轉了二十世紀關於自然與恩典關係的討論，是當代天主教神學的分水嶺之作。' },
          { title_zh: '默觀的種子', title_orig: 'Seeds of Contemplation', author: '牟敦（Thomas Merton）', era: '1949', place: '美國', language: '英文', intro: '熙篤會隱修士牟敦的靈修經典。他以簡練深邃的默想短章，引導讀者在默觀祈禱中發現「真我」、棄絕「假我」，回歸與上帝合一的內在生命。書中熔中世紀神祕傳統與現代人的處境於一爐，文字清澈而具穿透力。此書後經大幅增補為《新默觀種子》，是二十世紀天主教靈修神學流傳最廣、影響最深的著作之一。' }
        ,
          { title_zh: '超自然之奧祕', title_orig: 'Le Mystère du surnaturel（英譯 The Mystery of the Supernatural）', author: '呂巴克（Henri de Lubac）', era: '法文1965／英譯1967', place: '法國巴黎（Aubier）', language: '法文（英譯）', intro: '呂巴克對其早年《超自然》（Surnaturel, 1946）核心論題的精煉與發展（與同年《奧斯定主義與現代神學》並稱「兩兄弟 les deux jumeaux」）。質疑經院「純粹本性」（pura natura）概念，主張人受造即被賦予趨向超自然之天命，自然與恩典不可截然二分。為二十世紀天主教恩寵神學最具影響力的爭議之作。' },
          { title_zh: '我信聖靈', title_orig: 'Je crois en l\'Esprit Saint（英譯 I Believe in the Holy Spirit）', author: '孔加爾（Yves Congar）', era: '法文1979–80', place: '法國巴黎（Cerf）', language: '法文（英譯）', intro: '孔加爾三卷本聖靈論巨著，是天主教學界少數對聖靈及其在教會生命中工作的全面論述，承續並深化梵二的聖靈論工作。涵蓋聖經、教父、聖靈降臨運動與和子句問題，為當代羅馬天主教聖靈論代表作。' },
          { title_zh: '耶穌：基督論的一項探索', title_orig: 'Jezus, het verhaal van een levende（英譯 Jesus: An Experiment in Christology）', author: '史希爾貝克斯（Edward Schillebeeckx）', era: '荷文1974／英譯1979', place: '荷蘭奈梅亨（Nijmegen / Bloemendaal）', language: '荷蘭文（英譯）', intro: '史希爾貝克斯論耶穌基督三部曲首卷，引發全球爭論的鉅著。運用歷史批判與詮釋學方法，以對觀福音（尤其馬可與Q傳統）為根據，建構一種「自下而上」的基督論，探究歷史耶穌的塵世生命中通向基督信仰、回應人類救恩追尋的線索。出版後成暢銷書亦引發羅馬訓導審查，是當代天主教批判性基督論代表作。' },
          { title_zh: '基督——與神相遇的聖事', title_orig: 'Christus, sacrament van de Godsontmoeting（英譯 Christ the Sacrament of the Encounter with God）', author: '史希爾貝克斯（Edward Schillebeeckx）', era: '1960（荷文）／1963（英譯）', place: '荷蘭／美國紐約（Sheed and Ward）', language: '荷蘭文（英譯）', intro: '史希爾貝克斯梵二前最著名的著作，對天主教聖事神學的更新有重大貢獻。書中借梅洛龐蒂等現象學人類學成果，將基督本身界定為人與神相遇的根本聖事，教會與七件聖事則為此相遇的延伸，為基督論與聖事論開出新方向。' },
          { title_zh: '論作基督徒', title_orig: 'Christ sein（英譯 On Being a Christian）', author: '龔漢斯（Hans Küng）', era: '德文1974／英譯1976', place: '德國慕尼黑（R. Piper Verlag, München）', language: '德文', intro: '龔漢斯面向「信而不安者」與現代人的大部頭護教與基督信仰總論暢銷書，德文版甫出即售逾二十萬冊。聚焦耶穌基督的生平、教導及其神性本質，論述各基督教群體之共通核心與選擇相信基督教的理由，主張跟隨耶穌引向真正人性的存在。與《上帝存在嗎？》同為其挑戰訓導、面向世俗世界的代表巨著；英譯使這位學院神學家廣為大眾所知。' },
          { title_zh: '上帝存在嗎？今日的解答', title_orig: 'Existiert Gott?（英譯 Does God Exist? An Answer for Today）', author: '龔漢斯（Hans Küng）', era: '德文1978／英譯1980', place: '德國慕尼黑（Piper）', language: '德文（英譯）', intro: '龔漢斯篇幅龐大的有神論辯護巨著，循近代思想史（笛卡兒、黑格爾、費爾巴哈、尼采、佛洛伊德至虛無主義）追問上帝存在問題，主張對實在的基本信任已蘊含對上帝的肯定。為當代天主教基要神學的重要文獻。' },
          { title_zh: '基督教導論：使徒信經講釋', title_orig: 'Einführung in das Christentum: Vorlesungen über das apostolische Glaubensbekenntnis', author: '拉辛格（Joseph Ratzinger，後為教宗本篤十六世）', era: '1968', place: '德國慕尼黑（Kösel-Verlag, München）', language: '德文', intro: '拉辛格任杜賓根大學教義學教授時，1967 年夏季學期的講座結集，其最重要、最廣為閱讀的著作之一。依《使徒信經》逐條開展，以更具當代共鳴的語言重述基督教信仰的核心，闡述信與知、上帝的位格性、基督論的「敘事」面向與教會中的信仰處所。初版印四千五百冊，至 1969 年累計售出四萬五千冊，譯為二十三種語言，為近代神學最具影響力文本之一，奠定其神學聲望，亦預示其日後作為信理部長與教宗的神學立場。' }
        ,
          { title_zh: '神學的新時代', title_orig: 'Un nouvel âge de la théologie', author: '革弗雷（Claude Geffré）', era: '1972', place: '法國巴黎', language: '法文', intro: '法國道明會神學家革弗雷（Claude Geffré，1926–2017）回應梵二後天主教神學轉型而作的方法論宣言。本書以詮釋學為核心，探問在現代性、世俗化與宗教多元衝擊下，神學如何重新確立自身的語言與任務。革弗雷繼承呂格爾詮釋傳統，主張神學必須以批判性詮釋重讀啟示，方能對當代人有效言說。全書是天主教現代神學詮釋轉向的代表性原典，與龔漢斯、拉納同列後梵二時期歐陸神學的重要一環。' },
          { title_zh: '神學之鄉：認識神學人物與思潮', title_orig: 'Au pays de la théologie', author: '謝努（Bruno Chenu）；諾什（Marcel Neusch）', era: '1994', place: '法國巴黎', language: '法文', intro: '本書為法國道明會神學家謝努（Bruno Chenu, 1942–2003）與聖母升天會神學家諾什（Marcel Neusch, 1935–2015）合著的二十世紀神學概覽，以約三十篇簡介呈現當代重要神學家與神學思潮，兼及依勒內、奧古斯丁、托馬斯‧阿奎那、路德等奠基者，每篇附選讀文本與書目。原版 1979 年由 Centurion 出版，1994 年由 Cerf 修訂再版，為面向非專業讀者的入門神學導覽。' }
        ]
      },
      {
        key: 'liberation-contextual',
        label: '處境與解放神學部',
        label_en: 'Liberation and Contextual Theology',
        desc: '從拉美貧者、女性、黑人與第三世界經驗出發，重讀福音的釋放面向。',
        works: [
          { title_zh: '解放神學', title_orig: 'Teología de la liberación', author: '古鐵雷茲（Gustavo Gutiérrez）', era: '1971', place: '祕魯', language: '西班牙文', intro: '拉美解放神學的奠基之作。古鐵雷茲主張神學是「對實踐的批判反省」，福音首要關懷是「優先選擇窮人」，救恩涵蓋政治、社會與經濟的全面解放。他借用社會分析揭露結構性罪惡，呼籲教會與受壓迫者站在一起。此書定義了一整個神學運動，深刻衝擊拉美教會與普世神學的版圖。' },
          { title_zh: '耶穌基督解放者', title_orig: 'Jesus Cristo Libertador', author: '波夫（Leonardo Boff）', era: '1972', place: '巴西', language: '葡萄牙文', intro: '波夫從拉美處境重構基督論，描繪一位與受壓迫者認同、帶來歷史解放的耶穌。他強調基督的人性與其反抗不義的實踐面向，後更發展教會論批判聖統制結構，因而與教廷信理部多次衝突乃至被禁言。此書是解放神學基督論的代表作，將底層經驗推至教義反省的核心。' },
          { title_zh: '她的紀念', title_orig: 'In Memory of Her', author: '舒斯勒‧菲奧倫薩（Elisabeth Schüssler Fiorenza）', era: '1983', place: '美國', language: '英文', intro: '女性主義神學的里程碑。作者以批判的詮釋學重構早期基督教，揭示婦女在耶穌運動中「門徒的同等團契」地位如何被父權傳統與經典編纂所遮蔽。她主張以「懷疑的詮釋」與「記憶的重建」還原女性的歷史能動性。此書奠定女性主義聖經詮釋的方法論，影響跨越神學與性別研究。' },
          { title_zh: '黑人神學與黑人權力', title_orig: 'Black Theology and Black Power', author: '孔恩（James H. Cone）', era: '1969', place: '美國', language: '英文', intro: '黑人解放神學的開山之作。孔恩在民權運動與黑人權力浪潮中宣告「上帝是黑人的」，福音的核心是與受壓迫者認同、釋放被擄者。他主張基督在當代與黑人受苦處境合一，神學若不站在被欺壓者一邊便背叛福音。此書將種族壓迫推至神學前沿，是北美處境神學最具爆發力的聲音。' },
          { title_zh: '亞洲的水牛神學', title_orig: 'Waterbuffalo Theology', author: '小山晃佑（Kosuke Koyama）', era: '1974', place: '泰國／日本', language: '英文', intro: '第三世界神學的代表作。日裔宣教師小山晃佑在泰北稻田間,主張神學須脫下西方亞里斯多德的外衣,以農民與水牛的生活處境重述福音。他以「三哩時速的上帝」描繪一位配合人步調、緩慢同行的神。此書以詩意的在地語言批判西方神學的抽象與優越,是亞洲處境神學的開創性聲音。' }
        ,
          { title_zh: '受壓迫者的上帝', title_orig: 'God of the Oppressed', author: '孔恩（James H. Cone）', era: '1975', place: '美國紐約', language: '英文', intro: '孔恩黑人解放神學成熟期的系統表述。他以黑人受苦與抗爭的經驗為詮釋聖經的鑰匙，主張上帝在基督裡與受壓迫者認同、釋放被擄者，凡不站在被欺壓者一邊的神學皆背叛福音。書中辨析社會處境如何形塑神學知識，並對白人學院神學的「中立」假象提出尖銳批判。此書是繼《黑人神學與黑人權力》之後，黑人神學最重要的方法論奠基之作。' }
        ,
          { title_zh: '加利利的耶穌（民眾神學）', title_orig: '갈릴래아의 예수（Gallilaeaui Yesu）', author: '安炳茂（Ahn Byung-mu）', era: '1990', place: '韓國（韓神大學出版／韓國神學研究所）', language: '韓文', intro: '韓國民眾（Minjung）神學奠基者安炳茂的代表作。他以新約學者的眼光重讀《馬可福音》，主張福音書中的「群眾」（ochlos）即受壓迫的「民眾」，耶穌與加利利的民眾認同並同行，乃至宣告「民眾即彌賽亞」。書中從民眾視角重釋上帝、罪、基督與聖靈諸教義。安氏曾兩度因政治立場被捕入獄，此書是韓國民眾神學最重要的聖經神學文獻。' },
          { title_zh: '民眾神學：作為歷史主體的民眾', title_orig: 'Minjung Theology: People as the Subjects of History', author: '金容福（Kim Yong Bock）編／亞洲基督教協會神學關懷委員會（CTC-CCA）', era: '1981', place: '新加坡（Commission on Theological Concerns, Christian Conference of Asia, Singapore）；1983 修訂版始由 Zed Press, London / Orbis Books, Maryknoll 出版', language: '英文', intro: '韓國民眾（Minjung）神學的綱領性首部英文文集，源於1979年韓國NCC神學委員會與亞洲基督教協會神學關懷委員會合辦的神學諮詢會。論述韓國1970年代神學發展、作為民眾彌賽亞運動的韓國基督教、馬可福音中的耶穌與民眾，主張受壓迫的「民眾」是歷史主體。詹姆士‧孔（James H. Cone）作序。', extent: '196 pp.' },
          { title_zh: '啟發性的探索（達利特神學）', title_orig: 'Heuristic Explorations', author: '尼爾末（Arvind P. Nirmal）', era: '1990', place: '印度（Gurukul Lutheran Theological College & Research Institute, Madras/Chennai）', language: '英文', intro: '印度達利特（賤民）神學主要奠基者尼爾末的論文集。他主張基督教神學應反映達利特的處境與關懷，提出耶穌自身即是達利特，並以「方法論排他主義」為達利特神學的進路，以「悲愴」（pathos）為其認識論基礎、以歷史性的達利特意識為詮釋學鑰匙。此書是達利特神學作為印度本土解放神學重要框架的奠基文獻，為「無聲者」發聲。' },
          { title_zh: '女性主義觀點下的人類解放：一種神學', title_orig: 'Human Liberation in a Feminist Perspective: A Theology', author: '羅素（Letty M. Russell）', era: '1974', place: '美國費城（Westminster Press, Philadelphia）', language: '英文', intro: '羅素融合女性主義與解放神學的開創之作。她以「邁向自由的旅程」為主軸，論人類解放與神學、尋找可用的過去、救恩與良知化、道成肉身與人性化、對話中的共融諸題，將解放神學的「自覺化」（conscientization）方法引入性別議題。此書是女性主義神學的早期奠基文獻，為其後的婦女神學（mujerista/womanist）擴展鋪下基礎。', extent: '213 pp.' },
          { title_zh: '上帝的諸模型：為生態核子時代的神學', title_orig: 'Models of God: Theology for an Ecological, Nuclear Age', author: '麥克費格（Sallie McFague）', era: '1987', place: '美國費城（Fortress Press, Philadelphia）', language: '英文', intro: '麥克費格生態女性神學的代表作，曾獲美國宗教學會卓越獎。她批判將上帝設想為君王的傳統君主制隱喻，改以「母親、戀人、朋友」三種關係性隱喻重思神聖，並提出「世界作為上帝的身體」之說，以回應生態危機與核子威脅。她主張一切神學語言皆是隱喻而為人所建構，當以實驗性的模型培育更具身體性、互依性的受造觀。此書深刻影響生態神學與隱喻神學。', extent: '224 pp.' },
          { title_zh: '第三眼神學：在亞洲處境中形成的神學', title_orig: 'Third-Eye Theology: Theology in Formation in Asian Settings', author: '宋泉盛（Choan-Seng Song）', era: '1979', place: '美國紐約馬利諾（Maryknoll, NY，Orbis）', language: '英文', intro: '台灣神學家宋泉盛奠定其亞洲處境神學的代表作。借日本禪師鈴木大拙「第三眼」之佛教意象開展亞洲式的故事神學與受苦神學，探討基督信仰與亞洲社會政治、文化宗教處境的互動，主張以亞洲民眾的苦難與文化經驗為神學素材，含〈十字架與蓮花〉〈希望的米〉〈復活的政治〉等章，為亞洲解放神學先聲。', extent: '274 pp.' },
          { title_zh: '從亞洲母胎而生的神學', title_orig: 'Theology from the Womb of Asia', author: '宋泉盛（Choan-Seng Song）', era: '1986', place: '美國紐約（Orbis）', language: '英文', intro: '宋泉盛以亞洲人民的思想與生活經驗拓展西方神學視野，解讀亞洲人的生命以見上帝在其歷史與文化中的救贖臨在。本書是亞洲故事神學（story theology）的代表性論述，深化處境化神學方法。' },
          { title_zh: '非洲宗教與哲學', title_orig: 'African Religions and Philosophy', author: '姆比提（John S. Mbiti）', era: '1969', place: '英國倫敦／美國（Heinemann）', language: '英文', intro: '肯亞聖公會神父姆比提奠定非洲神學的開山之作，系統研究非洲諸社會的宗教心態與信念。首度挑戰「非洲傳統宗教觀念為邪魔、反基督」的成見，主張其應與基督教、伊斯蘭、猶太教、佛教受同等尊重；著名提出非洲以「事件」而非數學量度的時間觀。' },
          { title_zh: '性別歧視與談論上帝：邁向女性主義神學', title_orig: 'Sexism and God-Talk: Toward a Feminist Theology', author: '魯瑟（Rosemary Radford Ruether）', era: '1983', place: '美國波士頓（Beacon Press, Boston）', language: '英文', intro: '女性主義神學的奠基性系統著作，首度從女性主義視角系統批判基督教神學。以女性主義為工具揭露古典神學的男性中心偏見，橫跨歷史、神學、基督教與政治脈絡分析性別歧視，於創造論、基督論、聖職、教會論、聖母論、末世論各領域建構含括兩性整全人性的信仰，兼及生態女性神學關懷。', extent: 'xi, 289 pp.' },
          { title_zh: '蓋婭與上帝：醫治大地的生態女性主義神學', title_orig: 'Gaia and God: An Ecofeminist Theology of Earth Healing', author: '魯瑟（Rosemary Radford Ruether）', era: '1992', place: '美國舊金山（HarperSanFrancisco）', language: '英文', intro: '生態女性主義神學奠基之作。魯瑟考察西方宗教與科學傳統如何導致今日的生態危機，批判統治與支配的世界觀，並從聖約傳統與聖禮傳統重建人與大地、男女與群體之間的療癒關係，融合女性主義、解放神學與生態神學三脈，影響當代環境神學。' },
          { title_zh: '十字路口的基督論：拉丁美洲的進路', title_orig: 'Cristología desde América Latina（英譯 Christology at the Crossroads: A Latin American Approach）', author: '索布里諾（Jon Sobrino）', era: '西文1976／英譯1978', place: '墨西哥／薩爾瓦多（Centro de Reflexión Teológica, México；UCA）', language: '西班牙文（英譯）', intro: '薩爾瓦多耶穌會神學家索布里諾的解放神學基督論代表作，補解放神學前此基督論之不足。主張須建構「從歷史底層」、以跟隨歷史的耶穌為起點的「操作性」基督論，在受壓迫者臨在的拉美處境中揭示耶穌徹底的歷史性與受壓迫者苦難間的根本聯繫，要求一種真切改變人生死與受苦方式的神學。' },
          { title_zh: '解放者耶穌：拿撒勒人耶穌的歷史—神學解讀', title_orig: 'Jesus the Liberator: A Historical-Theological Reading of Jesus of Nazareth（西 Jesucristo liberador）', author: '索布里諾（Jon Sobrino）', era: '1991（西文初版）', place: '西班牙馬德里（西文初版 Editorial Trotta）／美國紐約 Orbis（英譯）；作者長居薩爾瓦多', language: '西班牙文（英譯）', intro: '拉丁美洲解放神學基督論的代表作。索布里諾以受壓迫者與「受難民眾」（crucified people）的視角重讀拿撒勒人耶穌，強調歷史耶穌的天國宣講與十架的解放意義。本書與續篇《解放者基督》並為解放基督論雙璧，曾引梵蒂岡信理部關注。' },
          { title_zh: '神學的解放', title_orig: 'Liberación de la teología（英譯 The Liberation of Theology）', author: '塞貢多（Juan Luis Segundo）', era: '1975', place: '烏拉圭（原講於哈佛神學院）', language: '西班牙文', intro: '烏拉圭耶穌會神學家塞貢多的解放神學方法論經典，源於1974年哈佛神學院系列講座。提出「詮釋學循環」方法，主張意識形態批判與信仰處境的不斷往復，使神學從既有體制中解放出來，為拉美解放神學奠定方法論基礎。', extent: '241 pp.' }
        ]
      },
      {
        key: 'evangelical-apologetics',
        label: '福音派與護教部',
        label_en: 'Evangelical Theology and Apologetics',
        desc: '守正統信仰並向現代心靈申辯,兼含盼望神學等福音派系統思索。',
        works: [
          { title_zh: '返璞歸真', title_orig: 'Mere Christianity', author: '路易斯（C. S. Lewis）', era: '1952', place: '英國', language: '英文', intro: '路易斯由二戰時期 BBC 廣播講稿結集,以平易理性向大眾申辯基督信仰的核心。他從普世道德律推論造物主,論述基督宣稱的兩難、三一論與成聖之路,刻意撇開宗派分歧而守「純粹基督教」。此書是二十世紀最暢銷的護教經典,以清明的譬喻與邏輯引領無數讀者重思信仰,影響歷久不衰。' },
          { title_zh: '前車可鑑', title_orig: 'How Should We Then Live?', author: '薛華（Francis Schaeffer）', era: '1976', place: '美國／瑞士', language: '英文', intro: '薛華縱覽西方文明從羅馬、中世紀、文藝復興、宗教改革到現代的興衰,主張思想觀念決定文化走向,西方因離棄聖經的絕對真理而墜入相對主義與虛無。他呼籲基督徒以聖經世界觀回應後現代的破碎。此書結合藝術史、哲學與神學,是福音派文化護教的代表,深刻形塑當代福音派的世界觀意識。' },
          { title_zh: '認識神', title_orig: 'Knowing God', author: '巴刻（J. I. Packer）', era: '1973', place: '英國／加拿大', language: '英文', intro: '巴刻以改革宗清教徒傳統寫成的屬靈經典,主張認識神不止於關於神的知識,更是與神相交的生命關係。書中逐章默想神的屬性,從神的智慧、權能、慈愛到忿怒與恩典,引導讀者在認識中敬拜順服。此書平衡神學深度與牧養溫度,被譽為當代福音派最重要的靈修神學著作之一。' },
          { title_zh: '系統神學', title_orig: 'Systematische Theologie', author: '潘能伯格（Wolfhart Pannenberg）', era: '1988–1993', place: '德國', language: '德文', intro: '潘能伯格主張啟示透過普遍歷史顯明,基督的復活是歷史終末的預先實現,神學須在公共理性中經得起檢驗。他的三卷系統神學以三一論為架構,力圖在現代知識處境中重建教義的真理宣稱。此書反對信仰退守主觀的安全島,堅持神學的普遍可辯護性,是當代最具哲學企圖的福音派系統神學。' },
          { title_zh: '盼望神學', title_orig: 'Theologie der Hoffnung', author: '莫特曼（Jürgen Moltmann）', era: '1964', place: '德國', language: '德文', intro: '莫特曼以「盼望」為神學的核心範疇,主張基督教信仰本質上是末世論的,從基督復活迸發出對受造界未來的應許,推動信徒批判並改造現世的不義。他將希望哲學與聖經的應許傳統熔鑄,使末世論不再是教義附錄而是貫穿全局的視角。此書震撼戰後神學界,啟發政治神學與解放神學。' },
          { title_zh: '被釘十字架的上帝', title_orig: 'Der gekreuzigte Gott', author: '莫特曼（Jürgen Moltmann）', era: '1972', place: '德國', language: '德文', intro: '莫特曼從十字架重構上帝論,主張在基督受死中三一上帝自身經歷了苦難與棄絕,聖父在喪子之痛中、聖子在被棄之苦中,藉聖靈承擔世界一切的苦難與不義。他以此回應奧斯威辛之後「上帝何在」的詰問,否定希臘不受苦的神觀。此書是二十世紀十字架神學與受苦上帝論的代表,影響深遠。' }
        ,
          { title_zh: '品格的群體', title_orig: 'A Community of Character', author: '侯活士（Stanley Hauerwas）', era: '1981', place: '美國', language: '英文', intro: '侯活士敘事與德性倫理學的代表作（全名《品格的群體：邁向建構性的基督教社會倫理》A Community of Character: Toward a Constructive Christian Social Ethic）。他批判自由主義將倫理化約為抽象原則與個人選擇，主張基督教倫理植根於教會作為一個「敘事群體」——信徒在效法基督的故事與實踐中養成品格。他力倡教會須成為與世界有別的「對比群體」以見證上帝國。此書扭轉了二十世紀後期基督教倫理學的方向，深刻影響後自由主義神學。' },
          { title_zh: '神‧啟示‧權威', title_orig: 'God, Revelation and Authority', author: '卡爾‧亨利（Carl F. H. Henry）', era: '1976–1983', place: '美國', language: '英文', intro: '卡爾‧亨利六卷鉅著，是二十世紀福音派系統神學與認識論的扛鼎之作。他以「上帝已說話」為前提，捍衛聖經是上帝命題式、無誤的啟示，逐一回應現代主義、新正統與後現代對啟示與真理的瓦解。全書以十五項論題層層展開神論與啟示論，奠定戰後美國福音派的神學自我意識，是改革宗福音派護教傳統最浩瀚的成果。' },
          { title_zh: '系統神學：聖經教義導論', title_orig: 'Systematic Theology: An Introduction to Biblical Doctrine', author: '古德恩（Wayne Grudem）', era: '1994', place: '美國', language: '英文', intro: '古德恩面向信徒與神學生寫成的系統神學，以平易筆法逐章鋪陳聖經教義，每章附經文背誦、詩歌與應用，立場為改革宗兼溫和靈恩。全書近一千五百頁，因可讀性高而流通極廣，譯成多國語言，是二十世紀末英語福音派最暢銷的系統神學教本之一，深刻形塑當代保守福音派的教義意識與門徒訓練。' },
          { title_zh: '基督教神學', title_orig: 'Christian Theology', author: '艾利克森（Millard J. Erickson）', era: '1983–1985', place: '美國', language: '英文', intro: '艾利克森三卷本系統神學，立場屬溫和加爾文主義的浸信會福音派。他以當代神學議題為對話脈絡，逐一處理啟示、上帝、人、基督、救恩、教會與末世，兼顧聖經根據、歷史發展與現代回應。全書方法平衡、視野開闊，後合訂為單卷，成為北美福音派神學院最廣用的標準教科書之一，是當代福音派系統神學的中堅之作。' },
          { title_zh: '上帝群體的神學', title_orig: 'Theology for the Community of God', author: '葛倫斯（Stanley J. Grenz）', era: '1994', place: '加拿大／美國', language: '英文', intro: '葛倫斯以「群體」為統攝範疇重構福音派系統神學，主張神學的目的在塑造愛的群體，三一上帝自身即愛的團契，教會被召反映此團契。他試圖在後現代處境中更新福音派的方法，兼採敘事與社群進路而不失聖經根基。全書近九百頁，是二十世紀末福音派回應後現代、向群體與三一論轉向的代表性系統神學。' },
          { title_zh: '基督教教義學', title_orig: 'Systematic Theology', author: '伯克富（Louis Berkhof）', era: '1932／1938', place: '美國', language: '英文', intro: '伯克富集荷蘭改革宗（凱波爾、巴文克）傳統之大成的系統神學教本，全書依神論、人論、基督論、救恩論、教會論、末世論次第展開，立場嚴守加爾文主義與西敏信條。其架構清晰、引證厚實，二十世紀以來長期作為改革宗與保守福音派神學院的標準課本，影響英語與華語神學教育甚鉅，是現代改革宗系統神學最具代表性的入門鉅著。' }
        ,
          { title_zh: '改革宗教義學', title_orig: 'Gereformeerde Dogmatiek', author: '巴文克（Herman Bavinck）', era: '1895–1901', place: '荷蘭坎彭（J. H. Bos，Kampen；第二版起改由 J. H. Kok 出版）', language: '荷蘭文', intro: '荷蘭新加爾文主義神學家巴文克的四卷本系統神學鉅著，改革宗傳統的里程碑。綜合聖經釋義、歷史神學與哲學洞見，捍衛改革宗正統。四卷分論緒論、上帝與創造、罪基督與救恩、聖靈教會聖事與末世；長期僅有荷文，後由荷蘭改革宗翻譯學會譯為英文。' },
          { title_zh: '信仰的辯護', title_orig: 'The Defense of the Faith', author: '范泰爾（Cornelius Van Til）', era: '1955', place: '美國費城（Presbyterian and Reformed Publishing，西敏神學院）', language: '英文', intro: '范泰爾首度完整公開其前提主義／預設護教學（presuppositionalism）體系之作，整併其護教學講義並回應批評者。主張護教必須與基督教本質一致，以三一上帝及聖經啟示為一切思想的先決預設，駁斥中立理性的可能；論述基督教的實在哲學、知識哲學與行為哲學，闡發前提的角色、信與不信者的接觸點，以及基督教與非基督教世界觀之間的對立（antithesis）。' },
          { title_zh: '確證的基督教信念', title_orig: 'Warranted Christian Belief', author: '普蘭丁格（Alvin Plantinga）', era: '2000', place: '美國／英國（Oxford University Press, New York/Oxford）', language: '英文', intro: '普蘭丁格「確證」（warrant）知識論三部曲的壓卷之作，繼《保證：當前論辯》與《保證與恰當功能》之後出版。他將「恰當功能」概念應用於基督教信仰，檢視「確證」在有神論信念中的角色，論證接受基督教信念是否合理、正當、有確證，主張基督教信念若由正常運作的認知官能所形成即具確證，從而（若為真）即構成知識；他區辨「事實問題」與「法理問題」，並援「神性感」與聖靈之工。為改革宗知識論的集大成扛鼎之作。', extent: '528 pp.' },
          { title_zh: '福音派神學要義', title_orig: 'Essentials of Evangelical Theology', author: '布勒施（Donald G. Bloesch）', era: '1978–1979', place: '美國舊金山（Harper & Row, San Francisco）', language: '英文', intro: '布勒施兩卷本福音派系統神學的代表作。卷一論上帝、權威與救恩，卷二論生命、職事與盼望。他立足新正統與福音派之間，既肯定聖經的權威與福音的客觀性，又批判基要派的命題主義與自由派的內在主義，倡導一種「進步保守」的福音派立場。此書是二十世紀後期主流福音派系統神學兼具廣度與平衡的重要著作，在英語神學教育中流傳甚廣。', extent: '全二卷' },
          { title_zh: '基督教神學導論', title_orig: 'Christian Theology: An Introduction', author: '麥格夫（Alister E. McGrath）', era: '1994（多版修訂）', place: '英國牛津（Blackwell / Wiley-Blackwell, Oxford）', language: '英文', intro: '麥格夫廣為使用、當今國際上最受推崇、使用最廣的基督教神學標準教科書之一。綜述兩千年基督教思想的主要概念、主題與發展，兼顧歷史神學、來源與系統神學，由福音派背景學者所撰、跨宗派通用，歷經多版增訂（最新為 2024 年第七版，與 Matthew J. Thomas 合著），為當代神學教育的入門經典。', extent: '510 pp.' }
        ,
          { title_zh: '基督教神學：系統與聖經神學', title_orig: 'Christian Theology, Systematic and Biblical', author: '班克羅夫特（Emery H. Bancroft）', era: '1925', place: '美國紐約州（Bible School Park, NY）', language: '英文', intro: '美國浸信會神學家班克羅夫特（Emery H. Bancroft，卒 1944）所著系統神學教本，融合系統神學與聖經神學方法，逐題梳理上帝論、基督論、救恩論、聖靈論、末世論等核心教義，以歸納聖經為基礎，輔以保守福音派正統框架。全書結構清晰，長期用作浸信會神學院教材，代表二十世紀初新教保守系統神學的典型範式，兼具教學與護教功能。' }
        ]
      },
      {
        key: 'sinophone',
        label: '漢語神學部',
        label_en: 'Sinophone Theology',
        desc: '二十世紀華人本色神學與本土教會傳統的義理探索。',
        works: [
          { title_zh: '基督教哲學', title_orig: '基督教哲學', author: '趙紫宸', era: '1925', place: '中國', language: '中文', intro: '趙紫宸是民國最具代表性的本色神學家,試圖以中國思想資源詮釋基督信仰。本書融會儒家人格修養與基督教救贖,主張耶穌是道德人格的至高典範,信仰須與民族文化生命相連。他後期思想轉向更重啟示與十架,但此書仍是早期華人嘗試以理性與文化會通福音的代表,標誌中國神學主體意識的萌發。' },
          { title_zh: '奮進', title_orig: '奮進', author: '誠靜怡', era: '1920年代', place: '中國', language: '中文', intro: '誠靜怡是一九一〇愛丁堡宣教會議上華人的代表性聲音,畢生推動中國教會自立、自養、自傳與合一。其文集記錄他對本色教會、跨宗派合一與民族教會建設的思索。作為中華全國基督教協進會的領袖,他承接普世合一運動的精神而落實於中國處境,是漢語教會合一神學與本色化運動承先啟後的關鍵人物。' },
          { title_zh: '屬靈人', title_orig: '屬靈人', author: '倪柝聲', era: '1928', place: '中國', language: '中文', intro: '倪柝聲是地方教會運動的奠基者,本書系統闡述其靈、魂、體三元人觀,主張信徒須經魂與靈的剖分、十字架對己的對付,方能在靈裡與基督聯合。書中靈命神學細密而具實踐力,影響華人靈恩與聚會所傳統甚鉅。雖其三元論曾受爭議,此書仍是二十世紀華人屬靈神學最具系統與影響力的代表作。' },
          { title_zh: '我們是為了信仰', title_orig: '我們是為了信仰', author: '王明道', era: '1955', place: '中國', language: '中文', intro: '王明道是北方基要派教會的代表,以堅守純正信仰、拒絕加入官方教會運動著稱。此文是他面對政治壓力時的信仰宣告,逐條申明所信並拒與其視為「不信派」者妥協,終致長年繫獄。文中剛直不屈的信仰立場,成為華人教會在極權下持守良心的見證標誌,是漢語護教與殉道神學的重要文獻。' },
          { title_zh: '漢語神學運動文獻', title_orig: '漢語神學運動文獻', author: '劉小楓等', era: '1990年代以降', place: '中國／香港', language: '中文', intro: '一九九〇年代興起的漢語神學運動,由人文學界學者推動,主張在漢語語境與學術場域中思考基督教,而不限於教會建制。劉小楓等以「文化基督徒」與「學術神學」為標誌,翻譯西方神學經典、開展漢語的基督教思想。此一脈絡將神學引入華語人文學術,擴展了二十世紀末漢語基督教思想的深度與廣度。' }
        ,
          { title_zh: '基督教與中國文化', title_orig: '基督教與中國文化', author: '吳雷川', era: '1936', place: '中國', language: '中文', intro: '吳雷川晚年的代表作，受基督教青年會之邀而著。他試圖以中國固有文化會通基督信仰，將耶穌詮釋為提倡社會改造的革命家，主張基督教須與民族復興、社會革命的理想結合方有出路。此書是民國本色神學「社會福音」一脈的重要文獻，反映了華人知識分子在救亡圖存處境中對基督教社會意義的探尋，影響漢語神學對信仰與文化關係的思考。' },
          { title_zh: '耶穌傳', title_orig: '耶穌傳', author: '趙紫宸', era: '1935', place: '中國', language: '中文', intro: '趙紫宸以中國人的視角重寫的耶穌生平。他擺脫西方教義包裝，以文學筆法描繪一位有血有肉、體現至高道德人格的耶穌，強調其人格感召與社會理想。此書是民國本色神學的代表作，將基督論落實於華人的人格與文化生命體驗，標誌中國神學以本民族語言與心靈詮釋福音的自覺嘗試，在漢語基督教思想史上具承先啟後地位。' },
          { title_zh: '基督教與現代思想', title_orig: '基督教與現代思想', author: '謝扶雅', era: '1937', place: '中國', language: '中文', intro: '謝扶雅會通中西思想的代表作。他學貫哲學與宗教學，試圖在現代思潮、中國文化與基督信仰之間搭橋，主張基督教須與現代理性、科學及中國人文精神對話而非對立。此書展現民國學院派本色神學的廣度，以文化哲學的高度反思信仰的現代處境，是漢語基督教思想中「文化神學」一脈的重要奠基文獻。' },
          { title_zh: '神道學', title_orig: '神道學', author: '賈玉銘', era: '1921', place: '中國', language: '中文', intro: '賈玉銘的系統神學鉅著，是華人保守福音派最早的本土系統神學之一。全書依神論、人論、基督論、救恩論、教會論、末世論等綱目組織，承襲改革宗與凱錫克靈修傳統，以解經為基底，重視「完全救法」的屬靈經驗。賈氏被譽為華人解經王子，此書奠定中國保守教會神學教育的根基，影響近代華人福音派神學甚鉅。' },
          { title_zh: '基礎系統神學──真理與信仰體驗的整理', title_orig: '基礎系統神學──真理與信仰體驗的整理', author: '楊慶球', era: '2020年代', place: '香港／加拿大（天道書樓出版）', language: '中文', intro: '楊慶球面向華人處境寫成的系統神學教本。他以改革宗傳統為基底，將神學真理與信徒的信仰體驗相整合，逐章處理啟示、神論、基督、救恩、教會與末世，並留意中國思想與當代文化的對話。作者長期投身華人神學教育與中國文化會通研究，此書平衡學術深度與牧養應用，是當代華人系統神學的代表著作之一。' },
          { title_zh: '從基督教看中國孝道', title_orig: '從基督教看中國孝道', author: '何世明', era: '1960年代', place: '香港', language: '中文', intro: '香港聖公會牧師何世明會通儒家與基督教的代表作。他以基督信仰重新詮釋中國傳統孝道，主張孝親之德與敬天事神可在福音中得到提升與安頓，化解教會與華人家庭倫理的張力。此書是漢語本色神學處理倫理會通的重要文獻，反映港台教會在中國文化處境中為信仰尋求文化合法性的努力，影響華人對信仰與家庭倫理關係的反思。' },
          { title_zh: '邊緣上的神學反思——徘徊在大學、教會與社會之間', title_orig: '邊緣上的神學反思——徘徊在大學、教會與社會之間', author: '賴品超', era: '2001年', place: '香港', language: '中文', intro: '賴品超漢語神學與宗教對話的代表作。他主張漢語神學應自覺其「邊緣」處境——既處於華人文化與西方神學之間，又處於教會建制與人文學術之間——並化邊緣為對話與創造的位置。書中探討基督教與儒釋道、比較神學與處境神學等議題。此書是世紀之交漢語神學在文化與宗教多元處境中自我定位的重要思考，拓展了華人神學的對話視野。' },
          { title_zh: '正常的基督徒生活', title_orig: 'The Normal Christian Life', author: '倪柝聲', era: '1957', place: '中國／英國', language: '中文', intro: '倪柝聲據其釋放給歐洲信徒的信息整理而成的屬靈神學經典。他以《羅馬書》為綱，論述基督的血、基督的十字架、罪身的對付、與基督同死同活的聯合，闡明信徒由稱義到成聖的生命途徑。書中「知道、計算、獻上、行走」的進深架構影響深遠，是地方教會運動靈命神學的核心表述，亦廣傳於華人與西方教會，是二十世紀華人最具國際影響力的屬靈著作之一。' },
          { title_zh: '神學四講', title_orig: '神學四講', author: '趙紫宸', era: '1948', place: '中國', language: '中文', intro: '趙紫宸後期神學成熟之作，標誌他由早期人格主義、文化會通轉向更重啟示、罪與十字架的立場。全書以四講系統陳述其對上帝、基督、救恩與教會的理解，吸收新正統的洞見而仍植根華人處境。此書與其早年《基督教哲學》對照，呈現一位本色神學家思想的深化轉折，是漢語系統神學的重要里程碑。' },
          { title_zh: '復和神學與教會更新', title_orig: '復和神學與教會更新', author: '楊牧谷', era: '1987', place: '香港', language: '中文', intro: '楊牧谷以「復和」（reconciliation）為核心範疇建構的華人處境神學。他主張福音的精義在於上帝藉基督使人與神、人與人、人與受造界復和，並以此反省香港教會在社會撕裂中的更新使命。此書是八十年代香港本土神學的代表作，將普世的復和教義落實於華人社會處境，深刻影響其後香港教會的社會神學思考。' },
          { title_zh: '廣場上的漢語神學：從神學到基督宗教研究', title_orig: '廣場上的漢語神學：從神學到基督宗教研究', author: '賴品超', era: '2010年代', place: '香港', language: '中文', intro: '賴品超是當代香港具代表性的漢語神學與比較宗教學者。其著作主張漢語神學不應自限於教會建制，而當走入公共學術「廣場」，與儒釋道及現代思潮對話，並深入處理基督教對宗教多元與宗教分歧的論述。此一脈絡承九十年代漢語神學運動而開展，將華語基督教思想推向跨宗教、跨學科的公共領域，是當代漢語神學的重要進路。' }
        ,
          { title_zh: '會遇系統神學：真理與信仰體驗的整理', title_orig: '會遇系統神學──真理與信仰體驗的整理', author: '楊慶球', era: '2000', place: '香港（中國神學研究院）', language: '漢語', intro: '當代華人系統神學代表作。楊慶球以「會遇」（真理與信仰體驗的相遇）為架構整理系統神學各題，兼顧改革宗傳統與華人處境，是二十一世紀初香港漢語神學界重要的系統神學整理之作。' },
          { title_zh: '屬靈神學：倪柝聲思想的研究', title_orig: '屬靈神學：倪柝聲思想的研究', author: '林榮洪', era: '1985', place: '香港（中國神學研究院）', language: '中文', intro: '歷史神學學者林榮洪研究倪柝聲神學思想的重要學術著作，系統梳理這位影響深遠的華人本土教會領袖之「屬靈」神學體系。林氏並著有《中華神學五十年（1900–1949）》《曲高和寡：趙紫宸的生平與神學》《明道與中國教會》等，為漢語神學史研究重鎮。' },
          { title_zh: '成聖之道：北宋二程修養工夫論之研究', title_orig: '成聖之道：北宋二程修養工夫論之研究', author: '溫偉耀', era: '1996', place: '台灣（文史哲出版社；2004 河南大學出版社再版）', language: '中文', intro: '溫偉耀會通基督教成聖論與宋代儒家修養工夫的中西比較哲學力作。他以當代哲學與心理學透析北宋二程（程顥、程頤）的修養工夫論，揭示其對現代人自我追尋與靈性修養的啟迪，並暗中與基督教「成聖之道」對話。溫氏兼具牛津大學（現代德國哲學與基督教神學）與香港中文大學（宋代儒家道德哲學）雙哲學博士，此書是漢語神學處理基督教與中國思想會通的代表著作之一。' },
          { title_zh: '靈歷集光（宋尚節日記摘抄）', title_orig: '靈歷集光', author: '宋尚節（日記原著）；蔡選青等（摘抄整理）', era: '1930年代日記（後人摘抄刊行）', place: '中國／後於海外刊行', language: '中文', intro: '二十世紀華人奮興佈道家宋尚節的日記摘抄，記錄其屬靈歷程、奮興佈道、痛斥罪惡呼召悔改，以及靠聖靈醫病趕鬼的事蹟。宋氏曾留美獲化學博士，歸主後焚棄文憑，全心傳道，對一九三〇年代華人教會復興運動影響深遠。其日記四十餘本失而復得，後經整理刊行（另有《主僕宋尚節日記摘抄》增訂版）。此書是漢語靈修與奮興神學的重要見證文獻。' }
        ]
      },
      {
        key: 'orthodox',
        label: '東正教神學部',
        label_en: 'Modern Orthodox Theology',
        desc: '二十世紀東正教神學復興，俄僑神學家於流亡中重探希臘教父、否定神學與神化（theosis）傳統，並參與普世對話。',
        works: [
          { title_zh: '東方教會神祕神學', title_orig: 'Essai sur la théologie mystique de l\'Église d\'Orient', author: '洛斯基（Vladimir Lossky）', era: '1944', place: '法國巴黎', language: '法文', intro: '流亡巴黎的俄國神學家洛斯基最著名的著作，系統闡述東正教神學傳統。他主張一切神學本質上皆是神祕的，東方教會以否定神學（apophasis）、上帝本質與能力之分、神化（theosis）等貫通教義與經驗。此書向西方世界重新引介希臘教父與帕拉瑪斯傳統，深刻影響二十世紀東正教神學復興與東西方教會的相互理解，是現代正教神學的經典導論。' }
        ,
          { title_zh: '俄羅斯神學之路', title_orig: 'Пути русского богословия (Puti russkogo bogosloviia)', author: '弗洛羅夫斯基（Georges Florovsky）', era: '1937', place: '法國巴黎（Paris，俄僑流亡）', language: '俄文', intro: '俄僑神學家弗洛羅夫斯基鉅著，系統批判俄羅斯宗教哲學偏離正教教父傳統、吸納西方哲學範疇之失。主張「回到教父」（新教父綜合），成為二十世紀正教神學方法論的奠基。後收入《弗洛羅夫斯基著作集》第五至六卷。' },
          { title_zh: '聖經、教會、傳統：東正教觀點', title_orig: 'Bible, Church, Tradition: An Eastern Orthodox View', author: '弗洛羅夫斯基（Georges Florovsky）', era: '1972', place: '美國‧麻州貝爾蒙特（Belmont, Massachusetts／Nordland Publishing Company）', language: '英文', intro: '弗洛羅夫斯基全集首卷，集其論聖經權威、教會與聖傳關係的核心文章。系統表述東正教對啟示、正典與教父傳統的詮釋學立場，是當代正教神學方法論的代表性綱領。' },
          { title_zh: '神的羔羊：論神人性', title_orig: 'Агнец Божий (Agnets Bozhii)（英譯 The Lamb of God）', author: '布爾加科夫（Sergius Bulgakov）', era: '俄文1933／英譯2008', place: '法國巴黎（YMCA-Press，聖塞爾蓋學院）', language: '俄文（英譯，Boris Jakim 譯）', intro: '布爾加科夫「神人性」（О Богочеловечестве）大三部曲首卷，東正教索菲亞學（sophiology）基督論的奠基之作。透過道成肉身、神聖索菲亞在救恩經綸中的角色、基督的虛己（kenosis）作為人類神化的範式，建構索菲亞學的正面體系；其索菲亞學思辨曾遭俄羅斯流亡教會指為異端。為其大三部曲（《羔羊》《保惠師》《羔羊的新婦》）首部。', extent: '468 pp.' },
          { title_zh: '保惠師：論聖靈', title_orig: 'Утешитель (Uteshitel)（英譯 The Comforter）', author: '布爾加科夫（Sergius Bulgakov）', era: '俄文1936／英譯2004', place: '法國巴黎（YMCA-Press）', language: '俄文（英譯，Boris Jakim 譯）', intro: '布爾加科夫「神人性」三部曲第二卷，論聖靈的鉅著。百科全書式地探討正教傳統與教會史中的聖靈論，含早期基督教聖靈論發展、教父與拜占庭時期「和子說」（filioque）爭議、聖靈在三一論中的位置，被視為三部曲中最圓熟之卷。' },
          { title_zh: '羔羊的新婦：論教會與末世', title_orig: 'Невеста Агнца (Nevesta Agntsa)（英譯 The Bride of the Lamb）', author: '布爾加科夫（Sergius Bulgakov）', era: '俄文遺著1945／英譯2002', place: '法國巴黎（YMCA-Press，遺著刊行）', language: '俄文（英譯，Boris Jakim 譯）', intro: '布爾加科夫大三部曲終卷、公認其神學巔峰，亦被譽為現代正教最偉大著作之一。從索菲亞學論教會論與末世論，探討創造、自由、惡與普救（apokatastasis）等難題。遺著於1945年首刊。' },
          { title_zh: '以共融為存有：人格與教會研究', title_orig: 'Being as Communion: Studies in Personhood and the Church', author: '齊齊烏拉斯（John D. Zizioulas）', era: '1985', place: '美國紐約克雷斯特伍德（Crestwood, NY，St Vladimir\'s Seminary Press）', language: '英文', intro: '佩加蒙都主教齊齊烏拉斯最負盛名的著作，論文結集，邁延多夫作序。他從加帕多家教父與東正教傳統出發，提出以「共融」為核心的關係本體論：人格的獨特性不在於其實體所具的普遍範疇，而是在與他者的關係中被構成；存有即關係、即共融。全書貫通三一論、基督論、聖餐論、聖職與末世論，重塑人與教會的概念，對西方探討教會作為共融體的努力影響深遠。', extent: '269 pp.' },
          { title_zh: '為了世界的生命：聖事與正教信仰', title_orig: 'For the Life of the World: Sacraments and Orthodoxy', author: '施梅曼（Alexander Schmemann）', era: '1963（修訂擴版 1973）', place: '美國紐約（National Student Christian Federation；後 St Vladimir\'s Seminary Press, Crestwood, NY）', language: '英文', intro: '施梅曼禮儀神學最廣為流傳的經典普及之作，原為 1963 年全國學生基督徒聯會編寫的研讀本，已譯成十一種語言。他從東正教教會崇拜的不間斷經驗出發，主張世界本身即是上帝賜下的聖事、是「天國的聖事」，人受召作「祭司」將受造界獻回造物主以成感恩（Eucharist），由此批判世俗主義與割裂聖俗的虔敬，重申禮儀作為「世界的聖事、天國的聖事」的意義。' },
          { title_zh: '禮儀神學導論', title_orig: 'Introduction to Liturgical Theology', author: '施梅曼（Alexander Schmemann）', era: '俄文1961／英譯1966', place: '美國紐約（SVS Press）', language: '英文', intro: '施梅曼最重要的學術著作，源自其博士論文。論述禮儀（lex orandi）作為神學首要資源（lex credendi）的原理，並考察拜占庭日課與教會年曆的歷史發展，奠定二十世紀正教禮儀神學的方法論基礎。' },
          { title_zh: '聖餐：天國的聖事', title_orig: 'The Eucharist: Sacrament of the Kingdom', author: '施梅曼（Alexander Schmemann）', era: '遺著1983／英譯1988', place: '美國紐約（SVS Press）', language: '英文（俄文遺稿）', intro: '施梅曼臨終前數週完成的聖餐神學總結，是其龐大著作中對整個神聖禮儀最完整的釋義。逐段詮釋拜占庭聖體禮，闡發聖餐作為進入天國之事件的「升登」神學。為其禮儀神學畢生結晶。' },
          { title_zh: '拜占庭神學：歷史趨勢與教義主題', title_orig: 'Byzantine Theology: Historical Trends and Doctrinal Themes', author: '邁延多夫（John Meyendorff）', era: '1974', place: '美國紐約（Fordham University Press, New York）', language: '英文', intro: '邁延多夫首度以英文系統綜述拜占庭基督教思想之作。上篇述歷史趨勢（迦克墩後神學、基督論爭議、毀像危機、修道神學、教會論），下篇論教義主題（創造、人論、基督、聖靈、三一上帝、聖事），核心命題為：人性非靜態封閉之物，而是由與神之關係所規定的動態實在。為西方學界認識拜占庭神學的權威入門。', extent: '243 pp.' },
          { title_zh: '上帝的經驗：正教教義神學', title_orig: 'Teologia Dogmatică Ortodoxă（英譯 The Experience of God: Orthodox Dogmatic Theology）', author: '史塔尼洛阿耶（Dumitru Stăniloae）', era: '1978', place: '羅馬尼亞布加勒斯特（Editura Institutului Biblic, București）', language: '羅馬尼亞文', intro: '二十世紀羅馬尼亞正教神學泰斗斯塔尼洛阿耶的六卷本教義神學鉅著，韋爾（Kallistos Ware）作序。他長年於布加勒斯特任教義學教授，並以四十餘年譯成羅文《慕善集》。其進路非權威式的「教條」，而是闡明教會教導背後的理據與正教信仰的內在邏輯、統一性、連貫性及其對日常基督徒生活的切身意義，貫穿神化（theosis）傳統。英譯六卷分論啟示與三一上帝、世界與人、基督、教會、聖事、創造的成全。', extent: '全六卷' },
          { title_zh: '正教之道', title_orig: 'The Orthodox Way', author: '韋爾（Kallistos Ware）', era: '1979', place: '英國牛津（A. R. Mowbray & Co., Oxford）', language: '英文', intro: '迪奧克利亞主教韋爾繼《正教會》之後廣受歡迎的教義與靈修綜述。循「上帝作為奧祕／三一／創造者／成為人／聖靈／祈禱（永恆）」的架構展開，論及上帝的隱與顯、惡的難題、救恩的本質、信、祈禱與死後之事，將正教信仰呈現為一段朝聖旅程，強調教義非抽象命題而是攸關整全生命；與其《正教會》並列為英語世界認識正教的標準入門。' },
          { title_zh: '正教會', title_orig: 'The Orthodox Church', author: '韋爾（Kallistos Ware／原名 Timothy Ware）', era: '1963（多次修訂）', place: '英國倫敦（Penguin）', language: '英文', intro: '當代英語世界認識東正教最暢銷的入門經典，初版以俗名 Timothy Ware 出版。上篇述正教歷史，下篇述其信仰與崇拜，1993、2015 兩度修訂。是普世讀者了解正教歷史、教義與實踐的標準導論。' }
        ]
      }
    ]
  },
  wai: {
    summary: '外編收三部:無神論與世俗批判部直面對信仰的根本否定;新興宗教神學部記與基督教淵源相涉而自立的新運動義理;宗教多元論部處理諸宗教真理地位的當代論辯。三者皆現代基督教義理無可迴避的對話對象。',
    divisions: [
      {
        key: 'atheism-secular',
        label: '無神論與世俗批判部',
        label_en: 'Atheism and Secular Critique',
        desc: '對基督信仰根本性的哲學與科學否定,自尼采以降的批判脈絡。',
        works: [
          { title_zh: '敵基督', title_orig: 'Der Antichrist', author: '尼采（Friedrich Nietzsche）', era: '1895', place: '德國', language: '德文', intro: '尼采對基督教最猛烈的攻擊之作,雖成於十九世紀末,卻是二十世紀世俗批判的源頭,故承先列此。他指控基督教是「奴隸道德」,以憐憫、謙卑顛覆強者生命的價值,毒化西方文明的健康本能。書中「上帝已死」的宣告界定了現代虛無主義的處境。此書是無神論批判的經典,逼使整個現代神學必須回應其詰難。' },
          { title_zh: '我為甚麼不是基督徒', title_orig: 'Why I Am Not a Christian', author: '羅素（Bertrand Russell）', era: '1927', place: '英國', language: '英文', intro: '羅素以分析哲學家的明晰,逐一駁斥上帝存在的傳統論證,並批判基督教在歷史上助長恐懼、壓制理性與道德進步。他主張倫理應奠基於人類福祉而非神聖權威,人當以勇氣與理智面對無神的宇宙。此講演結集是二十世紀理性無神論最廣為流傳的通俗宣言,代表科學理性主義對宗教的世俗化挑戰。' },
          { title_zh: '上帝錯覺', title_orig: 'The God Delusion', author: '道金斯（Richard Dawkins）', era: '2006', place: '英國', language: '英文', intro: '演化生物學家道金斯的暢銷之作,新無神論運動的旗艦。他主張有神論是站不住腳的科學假設,宗教信仰是未經檢證的迷思,且常為暴力與蒙昧張本。他以演化論解釋宗教的起源,呼籲以科學世界觀取代信仰。此書引爆二十一世紀初的有神/無神論大辯,是當代世俗批判最具影響力與爭議的代表作。' }
        ]
      },
      {
        key: 'new-religious',
        label: '新興宗教神學部',
        label_en: 'New Religious Movements',
        desc: '現代與基督教淵源相涉、卻另立教義體系的新興宗教運動。',
        works: [
          { title_zh: '新世紀運動文獻', title_orig: 'New Age Movement Writings', author: '佚名（多人）', era: '1970年代以降', place: '歐美', language: '英文', intro: '新世紀運動是二十世紀後期興起的鬆散靈性潮流,雜糅東方神祕主義、神智學、心理學與基督教元素,強調個人靈性覺醒、宇宙意識與身心整全。其文獻多元而無統一教義,共通點在於對建制宗教的疏離與對自我神性的肯定。此一運動反映現代世俗社會中靈性需求的轉向,是當代宗教光譜中重要的非建制現象。' },
          { title_zh: '原理講論', title_orig: '원리강론', author: '文鮮明（統一教）', era: '1966', place: '韓國', language: '韓文', intro: '統一教的根本教典,由教主文鮮明的啟示整理而成。書中以「創造原理」「墮落論」「復歸原理」重述聖經史,主張耶穌的使命因被釘十架而未竟,須由再臨的「彌賽亞」完成肉身與屬靈的雙重救贖、建立理想家庭。其義理大幅改寫正統基督教教義,自成體系。此書是理解統一教世界觀與其爭議性的核心文獻。' },
          { title_zh: '拉斯塔法里神學文獻', title_orig: 'Rastafari Theology Writings', author: '佚名（多人）', era: '1930年代以降', place: '牙買加', language: '英文', intro: '拉斯塔法里運動發源於一九三〇年代的牙買加,尊衣索比亞皇帝海爾‧塞拉西一世為再臨的彌賽亞「賈」(Jah)的化身,融會聖經、非洲認同與反殖民意識。其神學以「巴比倫」象徵壓迫體制,以「錫安」象徵非洲歸回,強調黑人尊嚴與屬靈解放。此一文獻群是現代以聖經元素重構的黑人本土宗教運動的代表。' }
        ]
      },
      {
        key: 'religious-pluralism',
        label: '宗教多元論部',
        label_en: 'Religious Pluralism',
        desc: '當代對諸宗教真理地位與基督教獨一性的多元論挑戰。',
        works: [
          { title_zh: '宗教多元論', title_orig: 'An Interpretation of Religion', author: '希克（John Hick）', era: '1989', place: '英國', language: '英文', intro: '希克是宗教多元論最系統的倡導者。他主張各大宗教都是人類對同一「終極實在」的不同文化回應,如同盲人摸象,沒有一個傳統可獨佔真理。他呼籲基督論從「上帝道成肉身」轉向隱喻式理解,使基督教放棄獨一救恩的宣稱。此書以康德的現象/本體之分為架構,是宗教神學中多元論立場的奠基之作,激起與排他論、兼容論的長久論辯。' }
        ]
      }
    ]
  }
},
    {
  key: 'shizhuan',
  name: '史傳藏',
  name_en: 'History and Biography',
  glyph: '史',
  genres: '教史‧普世合一史‧傳記',
  summary: '一九〇〇年以降的基督教歷史、普世合一運動史與見證傳記總匯。本藏以一九一〇年愛丁堡宣教會議至普世教會協會的合一運動為主軸,記現代基督教如何從宗派林立走向對話與合一;旁及現代教會通史、二十世紀宣教與全球基督教南移,以及極權時代的殉道見證。外編收世俗化的社會學敘事與新興宗教的現代發展史,以見現代基督教所處的廣闊歷史脈絡。',
  zheng: {
    summary: '正編按史學脈絡分四部:現代教會通史部承接古典教會史傳統而述至當代;普世合一運動史部為本藏現代主軸,記一九一〇愛丁堡以降的合一進程與梵二轉向;宣教與全球基督教史部記福音的全球擴展與基督教重心南移;殉道與見證傳記部記二十世紀極權與苦難中的信仰見證。',
    divisions: [
      {
        key: 'modern-church-history',
        label: '現代教會通史部',
        label_en: 'Modern Church History',
        desc: '承古典教會史傳統而述至現代的綜覽性通史鉅著。',
        works: [
          { title_zh: '基督教會史', title_orig: 'History of the Christian Church', author: '夏夫（Philip Schaff）', era: '1858–1890', place: '美國', language: '英文', intro: '夏夫的八卷鉅著,雖大半成於十九世紀,卻是現代英語世界教會史學的奠基典範,故承先列此。全書自使徒時代述至宗教改革,以淵博的原典考據與寬廣的普世胸襟著稱,力求超越宗派偏見,呈現基督教發展的有機整體。此書至今仍是教會史的標準參考,夏夫亦因其合一精神被視為普世合一運動的先驅學者。' },
          { title_zh: '基督教擴展史', title_orig: 'A History of the Expansion of Christianity', author: '拉圖雷特（Kenneth Scott Latourette）', era: '1937–1945', place: '美國', language: '英文', intro: '拉圖雷特的七卷鉅構,以「擴展」為主軸,述基督教兩千年來的興衰起伏與全球傳布。他提出「漲落」史觀,將教會史視為一波波退潮與更大漲潮的交替,終歸於福音影響力的累進擴展。此書視野宏闊、資料浩繁,是二十世紀宣教史與全球基督教史的里程碑,作者亦為普世合一與宣教運動的重要推手。' },
          { title_zh: '基督教史', title_orig: 'The Story of Christianity', author: '岡薩雷斯（Justo L. González）', era: '1984／2010', place: '美國／古巴', language: '英文', intro: '岡薩雷斯的兩卷通史,以流暢可讀著稱,自初代教會述至當代,特別注重拉美與全球南方視角,糾正以歐美為中心的傳統敘事。他兼顧神學、社會與文化脈絡,使非專業讀者亦能掌握教會史的全貌。此書已成為神學院最廣用的教會史教材之一,是當代最具普及力與全球意識的基督教通史。' }
        ]
      },
      {
        key: 'ecumenical-history',
        label: '普世合一運動史部',
        label_en: 'History of the Ecumenical Movement',
        desc: '本藏現代主軸:自一九一〇愛丁堡會議至普世教會協會與梵二的合一進程。',
        works: [
          { title_zh: '一九一〇愛丁堡宣教會議實錄', title_orig: 'World Missionary Conference 1910 Report', author: '愛丁堡會議籌委會', era: '1910', place: '蘇格蘭', language: '英文', intro: '一九一〇年愛丁堡世界宣教會議被公認為現代普世合一運動的起點。來自各宗派與宣教機構的代表齊聚,共商全球宣教的合作與分工,催生了「信仰與教制」「生活與工作」「國際宣教協會」三大合一脈絡。此實錄記錄會議的議程、報告與決議,標誌基督教從宗派競爭轉向跨宗派協作的歷史轉折,是合一運動承先啟後的根本文獻。', link: '/creeds' },
          { title_zh: '普世教會協會憲章與多倫多聲明', title_orig: 'WCC Constitution and the Toronto Statement', author: '普世教會協會（WCC）', era: '1948／1950', place: '荷蘭／加拿大', language: '英文', intro: '普世教會協會於一九四八年在阿姆斯特丹成立,匯聚新教與東正教眾多教會,是合一運動的建制高峰。其憲章以「承認主耶穌基督為上帝與救主」為入會基礎;一九五〇年的多倫多聲明則釐清協會的教會學性質,聲明它不是「超級教會」亦不主張某一教會論。此二文獻界定了現代合一運動的根本架構與自我理解,是普世對話的基石。', link: '/creeds' },
          { title_zh: '利馬文件:洗禮、聖餐與聖職', title_orig: 'Baptism, Eucharist and Ministry', author: '普世教會協會信仰與教制委員會', era: '1982', place: '祕魯', language: '英文', intro: '俗稱「利馬文件」,是普世教會協會信仰與教制委員會歷經數十年神學對話的結晶,就洗禮、聖餐與聖職三項長期分裂諸宗派的議題達致空前的趨同表述。此文件廣徵各宗派回應,成為合一神學對話最重要的成果之一,推動了不同傳統間的相互承認。它標誌合一運動從合作層面深入到教義趨同,是現代普世對話的里程碑。', link: '/creeds' },
          { title_zh: '大公主義法令', title_orig: 'Unitatis Redintegratio', author: '梵蒂岡第二屆大公會議', era: '1964', place: '梵蒂岡', language: '拉丁文', intro: '梵二的大公主義法令標誌天主教正式投身普世合一運動。文件承認其他基督徒為「分離的弟兄」,肯定他們所屬團體含有真實的教會要素與得救的途徑,呼籲天主教徒在祈禱、對話與合作中追求合一。此法令扭轉了天主教長期的排他立場,為其與東正教及新教的對話開啟新紀元,是二十世紀合一史上影響最深遠的官方文獻之一。', link: '/creeds' },
          { title_zh: '梵二與普世對話史', title_orig: 'Vatican II and the History of Ecumenical Dialogue', author: '阿爾貝里戈（Giuseppe Alberigo）等', era: '1995–2006', place: '義大利', language: '義大利文', intro: '由博洛尼亞學派主編的梵二史鉅著與相關研究,系統考述第二屆梵蒂岡大公會議的籌備、議程與後續影響,特別著墨於天主教如何透過大公主義、宗教自由與宗教對話法令重新定位自身與其他基督徒及諸宗教的關係。此一史學工程以浩繁檔案重建梵二的歷史進程,是理解二十世紀後半天主教普世轉向與對話歷史的權威之作。' }
        ]
      },
      {
        key: 'mission-global',
        label: '宣教與全球基督教史部',
        label_en: 'Mission and Global Christianity',
        desc: '二十世紀宣教擴展與基督教重心向全球南方轉移的歷史。',
        works: [
          { title_zh: '二十世紀宣教史', title_orig: 'A History of Christian Missions', author: '尼爾（Stephen Neill）', era: '1964', place: '英國', language: '英文', intro: '尼爾的單卷宣教通史,以主教兼宣教士的親身經驗,述基督教自使徒時代至二十世紀的全球傳布。他特別關注近代宣教運動的興起、與殖民主義的糾葛,以及非西方教會的自立。書中既肯定宣教的成就,也坦陳其失誤與爭議。此書筆力雄健、判斷持平,長期是宣教史的標準入門經典,反映合一時代對宣教的反省。' },
          { title_zh: '下一個基督王國', title_orig: 'The Next Christendom', author: '詹金斯（Philip Jenkins）', era: '2002', place: '美國', language: '英文', intro: '詹金斯以人口統計與歷史分析,論證基督教的重心已不可逆轉地從歐美轉移到非洲、拉美與亞洲的全球南方,二十一世紀的「典型基督徒」將是南半球的有色人種。他剖析南方基督教的超自然取向、保守倫理與蓬勃增長,預示其將重塑世界基督教的面貌。此書是全球基督教研究的劃時代之作,改寫了人們對基督教未來的想像。' }
        ]
      },
      {
        key: 'martyrdom-witness',
        label: '殉道與見證傳記部',
        label_en: 'Martyrdom and Witness',
        desc: '二十世紀極權壓迫與苦難處境中的信仰見證與殉道傳記。',
        works: [
          { title_zh: '潘霍華:牧師、殉道者、先知、間諜', title_orig: 'Bonhoeffer: Pastor, Martyr, Prophet, Spy', author: '梅塔薩斯（Eric Metaxas）', era: '2010', place: '美國', language: '英文', intro: '潘霍華是二十世紀最著名的殉道神學家。本傳記詳述他從學者、牧師到投身抵抗納粹、參與刺殺希特勒密謀,終於戰爭結束前夕在集中營被處決的一生。書中刻畫他在認信教會中的領導、地下神學院的牧養,以及在重價恩典神學與政治抉擇間的掙扎。此書使潘霍華的見證廣為人知,是現代殉道傳記的代表之作。' },
          { title_zh: '二十世紀殉道見證錄', title_orig: 'Witnesses to the Faith in the Twentieth Century', author: '佚名（多人輯錄）', era: '20世紀', place: '全球', language: '多語', intro: '二十世紀被稱為基督教史上殉道者最多的世紀。本輯錄彙集納粹、蘇聯、東歐共產政權、中國文革及各地迫害下,無數因信仰而受苦受死者的見證,包括神職人員與平信徒。坎特伯雷大教堂與西敏寺亦立像紀念這些現代殉道者。此一見證群記錄極權與意識形態壓迫下信仰的堅韌,是現代教會苦難神學的歷史血肉。' },
          { title_zh: '德蕾莎修女傳', title_orig: 'Mother Teresa: Come Be My Light', author: '科洛迪丘克（Brian Kolodiejchuk）編', era: '2007', place: '印度／阿爾巴尼亞', language: '英文', intro: '德蕾莎修女在加爾各答貧民窟服事最貧窮垂死者,創立仁愛傳教修女會,成為二十世紀慈善與見證的象徵,獲諾貝爾和平獎並被封聖。本書集結其私人書信,意外揭露她在長年事奉中經歷漫長的「靈魂暗夜」,在感受不到上帝同在的乾枯中仍持守信德與愛德。此書既記其外在事功,更顯其內在信仰的深邃與真實,是現代聖徒見證的動人文獻。' }
        ]
      }
    ]
  },
  wai: {
    summary: '外編收兩部:世俗化批判史部記宗教社會學如何敘述現代世界的世俗化進程及其爭議;新興宗教史部記與基督教淵源相涉的新興宗教在現代的發展歷程。二者皆現代基督教史所處的廣闊脈絡。',
    divisions: [
      {
        key: 'secularization-history',
        label: '世俗化批判史部',
        label_en: 'History of Secularization',
        desc: '宗教社會學對現代世界世俗化進程的敘事與其後續修正。',
        works: [
          { title_zh: '世俗時代', title_orig: 'A Secular Age', author: '泰勒（Charles Taylor）', era: '2007', place: '加拿大', language: '英文', intro: '泰勒的哲學史鉅著,追問西方何以從五百年前信仰幾乎不可避免,變為今日信仰只是眾多選項之一。他細緻重構從「鑲嵌」於宇宙秩序的前現代自我,到「緩衝」的現代自我的轉變,主張世俗化不是宗教的單純消退,而是信仰與不信並存的新處境。此書深刻修正了素樸的世俗化論,是理解現代信仰條件的當代經典。' },
          { title_zh: '宗教社會學世俗化敘事文獻', title_orig: 'Secularization Thesis in the Sociology of Religion', author: '韋伯、伯格、布魯斯等', era: '20世紀', place: '歐美', language: '多語', intro: '自韋伯論「世界的除魅」以降,宗教社會學長期主張現代化必然帶來宗教的衰退,此即「世俗化論」。然而二十世紀後期全球宗教復興與美國信仰的持久,促使伯格等學者公開修正乃至撤回此說,而布魯斯等則為之辯護。此一文獻群記錄世俗化論的提出、鼎盛、危機與爭議,是理解現代社會宗教處境最重要的學術敘事脈絡。' }
        ]
      },
      {
        key: 'new-religious-history',
        label: '新興宗教史部',
        label_en: 'History of New Religious Movements',
        desc: '與基督教淵源相涉的新興宗教在現代的發展與制度化歷程。',
        works: [
          { title_zh: '摩門教史', title_orig: 'A History of the Latter-day Saints', author: '佚名（多人）', era: '19世紀以降', place: '美國', language: '英文', intro: '摩門教(耶穌基督後期聖徒教會)由斯密約瑟於一八三〇年創立,以摩門經為新經典,自稱為復原的真教會。此史記其從美國東部受迫害、西遷猶他、建立鹽湖城神權社群,到放棄多妻制、走向主流化與全球擴張的歷程。摩門教與正統基督教教義分歧甚大卻共用聖經傳統,是研究美國本土新興宗教制度化最重要的案例之一。' },
          { title_zh: '巴哈伊信仰史', title_orig: 'A History of the Bahá\'í Faith', author: '佚名（多人）', era: '19世紀以降', place: '波斯', language: '多語', intro: '巴哈伊信仰由巴孛預備、巴哈歐拉於十九世紀波斯創立,主張歷代宗教創始者皆是同一上帝漸進啟示的使者,倡導人類一家、宗教合一與世界和平。此史記其自波斯與鄂圖曼帝國的迫害流放,到發展為遍布全球的獨立宗教的歷程。巴哈伊雖非源於基督教,卻以普世啟示觀涵攝包括基督在內的諸先知,是現代普世性新興宗教的代表。' },
          { title_zh: '拉斯塔法里運動史', title_orig: 'A History of the Rastafari Movement', author: '佚名（多人）', era: '1930年代以降', place: '牙買加', language: '英文', intro: '拉斯塔法里運動自一九三〇年代興起於牙買加,與加維的黑人民族主義及對衣索比亞皇帝海爾‧塞拉西一世的尊崇緊密相連。此史記其從底層黑人的彌賽亞期盼,到藉雷鬼音樂與馬利等人傳布全球的歷程,以及其反殖民、肯定非洲認同的文化政治意涵。作為以聖經元素重構的現代黑人宗教運動,它是新興宗教與文化抵抗交織的獨特個案。' }
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
  genres: '校勘學‧現代譯本‧出土文獻',
  summary: '匯集二十世紀以降的聖經文本校勘、現代各語譯本、死海古卷與納戈瑪第等出土文獻刊行，以及批判學派的釋經成果與他宗教經典的現代學術譯介，呈現現代基督教在「文本」與「翻譯」層面的學術全貌。',
  zheng: {
    summary: '正藏收錄聖經本身的現代文本校勘、權威譯本，以及與聖經研究直接相關的出土與比較文獻刊行，是現代基督教大藏經文本基礎的核心。',
    divisions: [
          {
            key: 'r-corpora', label: '原典集成部', label_en: 'Patristic and Critical Corpora',
            works: [
              { title_zh: '基督教文獻集成‧拉丁卷', title_orig: 'Corpus Christianorum, Series Latina (CCSL)', author: 'Eligius Dekkers 創編；Brepols 出版社', era: '1953 年起（圖爾恩豪特）', place: '比利時圖爾恩豪特（Turnhout）', language: '拉丁文（附校勘）', extent: '持續出版，逾 200 卷', intro: '由本篤會士德克斯一九四七年倡議、Brepols 自一九五三年起陸續出版的拉丁教父原典校勘集成，收德爾圖良至可敬者比德（卒七三五）的全部拉丁基督教文獻。承維也納教會作家集成（CSEL）之後，採現代校勘學編訂權威拉丁底本，另有中世紀續編（CCCM）。為西方教父與中世紀拉丁神學研究不可或缺的批判版原典叢書。' },
              { title_zh: '基督教文獻集成‧希臘卷', title_orig: 'Corpus Christianorum, Series Graeca (CCSG)', author: 'Brepols 出版社（接續 Dekkers 計畫）', era: '1977 年起（蒂倫豪特）', place: '比利時蒂倫豪特（Turnhout）', language: '希臘文（附校勘）', extent: '持續出版', intro: '「基督教文獻集成」的希臘語分支，Brepols 自一九七七年起出版，收希臘教父原典的現代校勘版，補拉丁卷之不足。涵蓋從早期到拜占庭的希臘基督教作家，編訂以嚴格手稿譜系與校勘原則為基礎。與拉丁卷、中世紀續編並列，構成歐陸最權威的基督教原典批判集成，是東方教父與拜占庭神學研究的核心底本來源。' },
              { title_zh: '基督教原典叢書（法德對照本）', title_orig: 'Sources Chrétiennes', author: 'Henri de Lubac、Jean Daniélou 等創辦；里昂', era: '1942 年起（里昂／巴黎）', place: '法國里昂、巴黎', language: '希臘文／拉丁文原文＋法文對照', extent: '逾 600 卷', intro: '法國耶穌會神學家德‧呂巴克與達尼祿一九四二年於里昂創辦的教父原典叢書，由 Cerf 出版。每卷以原文（希臘或拉丁）與法譯對照，附導論與註釋，兼顧學術校勘與神學閱讀。已出版逾六百卷，涵蓋東西方教父、禮儀與中世紀作家，推動了二十世紀「回到本源」（ressourcement）神學運動，是現代教父學最具影響力的對照原典叢書。' },
              { title_zh: '東方教父文獻集成', title_orig: 'Patrologia Orientalis', author: 'René Graffin、François Nau 創編', era: '1903 年起（巴黎）', place: '法國巴黎', language: '敘利亞文／科普特文／亞美尼亞文／阿拉伯文／衣索比亞文等＋對照譯文', extent: '逾 50 卷', intro: '葛拉芬與諾一九〇三年創編、首卷一九〇四年問世的東方基督教文獻集成，承前身《敘利亞教父叢刊》(Patrologia Syriaca, 1897) 之後擴展，收以敘利亞、科普特、亞美尼亞、阿拉伯、衣索比亞(吉茲文)、喬治亞、斯拉夫等東方語言寫成的基督教原典，附拉丁或法、英、義對照譯文與校勘。涵蓋殉道錄、禮儀、講道、史傳與神學文獻，為研究東方諸教會不可或缺的權威原典叢書。' },
              { title_zh: '拉丁教父文獻彙編（米涅拉丁教父集）', title_orig: 'Patrologia Latina (Patrologiae Cursus Completus, Series Latina)', author: 'Jacques-Paul Migne 主編', era: '1841–1855 年（巴黎，索引卷 1862–1865）', place: '法國巴黎', language: '拉丁文', extent: '221 卷', intro: '米涅一八四四至一八五五年於巴黎編成的拉丁教父文獻巨帙，全 217 卷正文加 4 卷索引，收德爾圖良至教宗依諾增爵三世（一二一六）止的拉丁基督教著作。雖多沿用舊版而非新校，卻因收羅完備、卷帙浩瀚，長期作為西方教會文獻最便利的彙編，至今仍是研究查證的基礎工具書，並有數位化全文資料庫廣為使用。' },
              { title_zh: '希臘教父文獻彙編（米涅希臘教父集）', title_orig: 'Patrologia Graeca (Patrologiae Cursus Completus, Series Graeca)', author: 'Jacques-Paul Migne 主編', era: '1857–1866 年（巴黎）', place: '法國巴黎', language: '希臘文＋拉丁對照', extent: '161 卷', intro: '米涅繼拉丁卷後於一八五七至一八六六年編成的希臘教父文獻彙編，全 161 卷，希臘原文並附拉丁對照譯文，收自使徒教父至一四五三年君士坦丁堡陷落的希臘基督教著作。卷帙宏富、收錄齊備，雖非現代校勘版，仍為東方教父與拜占庭神學研究最廣為徵引的便利文獻總集，多數卷次已數位化供全文檢索。' },
              { title_zh: '舊約偽經（查爾斯沃思編，雙卷本）', title_orig: 'The Old Testament Pseudepigrapha', author: 'James H. Charlesworth 主編', era: '1983–1985 年（紐約）', place: '美國紐約', language: '英文（附原文研究）', extent: '2 卷', intro: '第二聖殿時期猶太—基督教偽經的標準英譯集成，Doubleday 出版，查爾斯沃思主編，全二卷收六十餘部文獻，各附導論、註釋與書目。涵蓋啟示、遺訓、智慧、詩篇與擴寫舊約等文類，由國際學者群據原文（希臘、敘利亞、衣索比亞等）譯註。為舊約偽經與第二聖殿猶太教研究的權威工具書，廣為釋經與歷史研究徵引。' },
            ],
          },

      {
        key: 'critical-text',
        label: '現代經文校勘部',
        label_en: 'Modern Critical Editions',
        desc: '以希臘文新約與希伯來文舊約的學術校勘本為主，奠定現代聖經研究的文本基準。',
        works: [
          { title_zh: '希臘文新約 第二十八版', title_orig: 'Novum Testamentum Graece (Nestle-Aland 28th Edition)', author: '聶斯特勒‧阿蘭德編輯團隊（Eberhard Nestle, Kurt Aland 等）', era: '初版1898，NA28為2012', place: '德國‧明斯特（聖經文本研究所）', language: '希臘文（附拉丁文與德文校勘符號）', intro: '現代新約研究最權威的希臘文校勘本，由德國明斯特聖經文本研究所主持。其下方的「校勘欄」（critical apparatus）羅列數千份抄本、古譯本與教父引文的異讀，使讀者得以追溯每一字句的傳承。第二十八版重新整理了公教書信的異文，採用「連貫基礎譜系法」（CBGM）建立譜系，是當代普世合一聖經學術的共同文本基礎，幾乎所有現代譯本皆以之為底本。' },
          { title_zh: '希臘文新約 聯合聖經公會版', title_orig: 'The Greek New Testament (UBS5)', author: '聯合聖經公會編輯委員會', era: '初版1966，UBS5為2014', place: '德國‧斯圖加特', language: '希臘文', intro: '聯合聖經公會出版的希臘文新約，文本與聶斯特勒‧阿蘭德版同一，但校勘欄為譯經者量身設計，只標示影響翻譯抉擇的重要異讀，並以ABCD四級評定異文的確定程度。此版專為全球譯經事工服務，是各語言聖經翻譯者最常使用的工作底本，體現現代聖經公會跨宗派合作、向萬民傳譯聖言的普世精神。' },
          { title_zh: '斯圖加特希伯來文聖經', title_orig: 'Biblia Hebraica Stuttgartensia (BHS)', author: '基特爾傳統編輯團隊（Karl Elliger, Wilhelm Rudolph 等）', era: '1967–1977', place: '德國‧斯圖加特', language: '希伯來文‧亞蘭文', intro: '以聖彼得堡列寧格勒抄本（Codex Leningradensis, 1008年）為底本的希伯來文舊約校勘本，是二十世紀下半葉希伯來聖經研究的標準版本。書頁下方詳列馬所拉傳統、撒瑪利亞五經、七十士譯本與死海古卷的異讀。BHS忠實重現單一抄本而不擅自校改正文，使學者得以在可靠的馬所拉文本上進行批判研究，廣為全球神學院採用。' },
          { title_zh: '希伯來文聖經 第五版（校訂本）', title_orig: 'Biblia Hebraica Quinta (BHQ)', author: '聯合聖經公會希伯來聖經校訂計畫', era: '2004年起陸續出版', place: '德國‧斯圖加特', language: '希伯來文‧亞蘭文', intro: 'BHS的接續者，是希伯來聖經校勘的最新世代成果，仍以列寧格勒抄本為底本，但全面更新校勘欄，納入死海古卷與最新抄本研究，並為每卷附上詳盡的文本評註與馬所拉小註（Masorah）的完整呈現。BHQ採分卷漸進出版，由國際學者協作，代表現代猶太—基督教共同的希伯來文本研究結晶，是二十一世紀舊約校勘的指標工程。' },
          { title_zh: '新約聖經抄本——傳遞、訛誤與校勘', title_orig: 'The Text of the New Testament: Its Transmission, Corruption, and Restoration', author: '布魯斯‧梅茨格、巴特‧葉爾曼', era: '初版1964，第四版2005', place: '美國‧普林斯頓', language: '英文', intro: '新約經文校勘學的經典入門與權威概論，由普林斯頓神學院的梅茨格撰寫，後與葉爾曼合修。全書系統介紹新約抄本的書寫材料、主要抄本與譯本、抄寫致誤的種類，以及從文藝復興到現代的校勘史與校勘方法。此書培養了數代聖經學者，使「為何不同譯本經文有別」這一問題得到嚴謹的學術解答，是理解現代聖經文本何以如此的必讀之作。' },
          { title_zh: '七十士譯本（哥廷根校訂版）', title_orig: 'Septuaginta (Göttingen Edition)', author: '哥廷根七十士譯本研究院', era: '二十世紀至今陸續出版', place: '德國‧哥廷根', language: '希臘文', intro: '希伯來聖經最早、最重要的古希臘文譯本的現代批判校訂，由哥廷根研究院以譜系方法重建最接近原始譯文的文本，附極詳盡的校勘欄。七十士譯本是新約作者與早期教會所用的聖經，也是研究希伯來文本早期形態的關鍵見證。此校訂工程是現代古典與聖經學術協作的典範，為舊約文本史與早期基督教研究奠定不可或缺的基礎。（七十士古譯本本身屬古代譯校藏，此為現代學術校訂版。）' }
        ]
      },
      {
        key: 'modern-versions',
        label: '現代譯本部',
        label_en: 'Modern Translations',
        desc: '收錄二十世紀以降英語與華語的權威現代譯本，反映普世合一時代各宗派共用聖經的努力。',
        works: [
          { title_zh: '修訂標準版聖經', title_orig: 'Revised Standard Version (RSV)', author: '美國全國基督教協進會聖經翻譯委員會', era: '新約1946，全書1952', place: '美國', language: '英文', intro: '承續欽定本傳統而以現代學術校勘本重譯的英語聖經，由全國基督教協進會主持，是二十世紀普世合一運動的重要成果。RSV兼顧文學典雅與學術準確，後更出版了天主教版與包含次經的合一版，成為新教、天主教與東正教學者可共同使用的英語譯本，奠定了「跨宗派聖經」的典範，影響後世幾乎所有英語譯本。' },
          { title_zh: '新修訂標準版聖經', title_orig: 'New Revised Standard Version (NRSV)', author: '美國全國基督教協進會聖經翻譯委員會', era: '1989', place: '美國', language: '英文', intro: 'RSV的全面修訂版，採用最新的希臘文與希伯來文校勘成果，並在語言上力求性別包容與當代可讀性。NRSV因其學術嚴謹與廣泛的教派接受度，成為英語世界神學院與學術引用的標準譯本，新教主流宗派、天主教與東正教皆有認可版本，是現代普世合一精神在聖經翻譯上最具代表性的結晶之一。' },
          { title_zh: '新國際版聖經', title_orig: 'New International Version (NIV)', author: '國際聖經協會（Biblica）譯經委員會', era: '新約1973，全書1978', place: '美國', language: '英文', intro: '由跨宗派福音派學者群合譯的英語聖經，目標是兼顧字義準確與當代流暢的「動態與形式平衡」譯法。NIV自問世以來成為全球銷量最大的英語現代譯本，廣受福音派教會採用。其翻譯哲學在「忠於原文」與「易於理解」之間取得平衡，深刻影響了二十世紀末以降英語讀經的習慣與聖經出版生態。' },
          { title_zh: '英文標準版聖經', title_orig: 'English Standard Version (ESV)', author: 'Crossway 譯經團隊', era: '2001', place: '美國', language: '英文', intro: '以RSV為基礎、走「本質直譯」（essentially literal）路線的英語譯本，強調盡量保留原文的字序、語法與神學詞彙。ESV因其文體莊重、貼近原文，受到福音派與改革宗教會的廣泛喜愛，常用於講道與研經。它代表現代英語譯本中偏向形式對等的一支，與動態對等的NIV形成互補，共同構成當代英語讀經的兩大路線。' },
          { title_zh: '現代中文譯本', title_orig: 'Today\'s Chinese Version (TCV)', author: '聯合聖經公會中文翻譯委員會', era: '初版1979，修訂版1997', place: '香港‧聯合聖經公會', language: '繁體中文', intro: '聯合聖經公會以「意義相符、效果相等」的功能對等原則重新翻譯的華語聖經，旨在用淺白現代的中文使一般讀者易於明白。譯本直接從希臘文與希伯來文校勘本翻出，擺脫文言遺風，是華語世界第一部全面採用現代語體的權威譯本，對華人教會的普及讀經與福音工作影響深遠。' },
          { title_zh: '和合本修訂版', title_orig: 'Revised Chinese Union Version (RCUV)', author: '聯合聖經公會和合本修訂委員會', era: '新約2006，全書2010', place: '香港‧聯合聖經公會', language: '繁體中文', intro: '對華人教會通行近百年的《和合本》進行的全面修訂，既保留原譯典雅莊重的語感與廣為熟悉的經文，又依據現代校勘本訂正譯文、更新已變遷的字詞用法。修訂工作歷時二十餘年，由跨宗派學者協力完成，使這部華語聖經的「標準本」得以在新世紀延續其權威地位，是華人普世合一讀經傳統的承先啟後之作。' },
          { title_zh: '思高聖經', title_orig: 'Studium Biblicum Version', author: '思高聖經學會（雷永明神父主持）', era: '1968（合訂本）', place: '香港‧思高聖經學會', language: '繁體中文', intro: '天主教華語世界最權威的聖經譯本，由方濟會雷永明神父創立的思高聖經學會自原文翻譯並詳加註釋，包含完整的次經（第二正典）。譯本前後歷時數十年，附有豐富的引言與註腳，學術性與牧靈性兼備。思高本是華語天主教會禮儀與研讀的標準聖經，也是新教學者研究次經與比對譯法的重要參照。', link: '/scripture' },
          { title_zh: '官話和合本', title_orig: '官話和合譯本', author: '狄考文、富善等中外譯經委員會', era: '1919', place: '中國上海', language: '繁體中文（白話文）', intro: '一九一九年出版的官話和合本，是新教在華宣教史上最重要的中文聖經譯本，由狄考文、富善等中外學者歷時近三十年合譯而成。其問世恰與愛丁堡世界宣教會議同期，採用淺白官話，文辭典雅流暢，奠定了現代漢語白話文與華人基督教信仰語言的基礎。和合本至今仍是華人教會最通行的譯本，其跨宗派合譯的歷程本身即是普世合一精神在華人世界的早期實踐。', link: '/scripture' },
          { title_zh: '聖經新譯本', title_orig: '聖經新譯本', author: '中文聖經新譯會', era: '1992', place: '香港', language: '繁體中文', intro: '聖經新譯本由華人聖經學者組成的中文聖經新譯會主持，於一九九二年完成全書，是少數完全由華人學者直接從原文翻譯的現代中文聖經。其譯文在忠實原文與現代語感之間求取平衡，並採用現代批判校勘版為底本，注重神學詞彙的精確。新譯本主要服事華人福音派教會，與和合本、思高本並列為當代重要的中文聖經系統，展現華人教會自主譯經的成熟。', link: '/scripture' }
        ]
      }
    ]
  },
  wai: {
    summary: '外藏收錄與基督教文本研究相關、但屬他宗教經典或批判學派的譯介與方法論著作，作為理解現代基督教學術處境的旁參。',
    divisions: [
      {
        key: 'other-religions',
        label: '他宗教經典現代譯介部',
        label_en: 'Modern Translations of Other Scriptures',
        desc: '收錄基督教學界對他宗教經典的現代學術譯介，反映宗教比較與對話的時代脈絡。',
        works: [
          { title_zh: '古蘭經（學術譯註本）', title_orig: 'The Study Quran: A New Translation and Commentary', author: '賽義德‧侯賽因‧納斯爾主編', era: '2015', place: '美國', language: '英文（譯自阿拉伯文）', intro: '當代最具學術份量的英譯古蘭經之一，由伊斯蘭學者群在納斯爾主持下完成，逐節附上引自歷代註釋傳統的詳盡評註，並收錄多篇主題論文。雖出自穆斯林學界，此書因其嚴謹的學術體例與對話精神，成為基督教神學院宗教比較課程的重要教材，體現現代普世合一時代基督徒理解、尊重伊斯蘭經典的努力。' },
          { title_zh: '東方聖書叢書', title_orig: 'The Sacred Books of the East', author: '馬克斯‧繆勒主編', era: '1879–1910', place: '英國‧牛津', language: '英文（譯自梵文、巴利文、波斯文、漢文、阿拉伯文等）', intro: '比較宗教學奠基者繆勒主編的鴻篇巨製，共五十卷，系統英譯印度教、佛教、瑣羅亞斯德教、伊斯蘭教、道教與儒家等東方宗教的根本經典。這套叢書首次以學術方式將東方聖典呈現於西方讀者面前，開創了現代比較宗教學，也為基督教神學提供與世界宗教對話的文本基礎，是十九世紀末至二十世紀宗教研究的里程碑。' }
        ]
      },
      {
        key: 'critical-exegesis',
        label: '批判學派釋經部',
        label_en: 'Critical Schools of Exegesis',
        desc: '收錄歷史批判、形式批判等現代釋經方法的代表著作，是現代聖經學術方法論的旁參。',
        works: [
          { title_zh: '歷史批判法導論', title_orig: 'Historical Criticism of the Bible', author: '現代聖經學界（以德國學派為主）', era: '十九世紀末至二十世紀', place: '德國', language: '德文‧英文', intro: '歷史批判法是現代聖經研究的主導方法，主張將聖經置於其歷史、語言與文化處境中考察，探究文本的來源、作者、年代與寫作意圖。它涵蓋來源批判、編修批判等多種進路，深刻改變了學界對聖經成書過程的理解。雖曾引發保守派的疑慮與爭論，這套方法已成為現代神學教育的基本訓練，是理解二十世紀聖經學術走向的關鍵脈絡。' },
          { title_zh: '形式批判與福音傳統', title_orig: 'Form Criticism and the Synoptic Tradition', author: '魯道夫‧布特曼、馬丁‧迪貝流斯', era: '1919–1921', place: '德國', language: '德文', intro: '形式批判由迪貝流斯與布特曼開創，主張福音書的素材在被寫定之前曾以口傳形式流傳，可依其「文學形式」（如神蹟故事、比喻、語錄）分類，並追溯其在早期教會生活處境中的功能。此方法將研究焦點從文本轉向口傳階段的群體，對福音書研究影響巨大，也引發關於歷史耶穌與信仰基督關係的長期神學討論。' },
          { title_zh: '耶穌研討會與五福音書', title_orig: 'The Five Gospels: The Search for the Authentic Words of Jesus', author: '羅伯特‧方克、耶穌研討會學者群', era: '1993', place: '美國', language: '英文', intro: '耶穌研討會是1985年成立的學者團體，以投票表決方式評估福音書中耶穌話語的歷史真實性，並將多馬福音與四福音並列為「五福音書」，以紅、粉、灰、黑四色標示話語可信度。其方法與結論引發學界與教會的激烈爭議，雖屢遭批評為過度懷疑，卻凸顯了現代歷史耶穌研究的方法論張力，是二十世紀末聖經批判學最受矚目的公共事件之一。' }
        ]
      }
    ]
  }
},
    {
  key: 'shuxin',
  name: '書函藏',
  name_en: 'Canon of Letters and Encyclicals',
  glyph: '函',
  genres: '通諭‧普世合一書信‧牧函',
  summary: '收錄現代教宗社會與合一通諭、教宗與東正教普世牧首及各宗派的合一往來文件、現代牧函與獄中書簡，以及新興宗教與世俗思潮的公開宣言，以「書信」之體呈現現代基督教向世界發聲、與分裂弟兄重歸於好的努力，是普世合一運動的核心見證。',
  zheng: {
    summary: '正藏以教宗通諭與普世合一書信為現代主軸，輔以體現信仰見證的現代牧函與獄中書簡，記錄現代教會的社會訓導與合一進程。',
    divisions: [
      {
        key: 'encyclicals',
        label: '教宗通諭部',
        label_en: 'Papal Encyclicals',
        desc: '【現代主軸之一】收錄良十三世以降歷任教宗的社會與合一通諭，是現代天主教訓導與普世關懷的權威文獻。',
        works: [
          { title_zh: '新事通諭', title_orig: 'Rerum Novarum', author: '良十三世', era: '1891', place: '梵蒂岡', language: '拉丁文', intro: '現代天主教社會訓導的奠基文獻，針對工業革命後勞資衝突與社會主義興起的「新事」而發。通諭一面肯定私有財產與工人組織工會的權利，一面譴責資本剝削，主張公道工資與國家對弱者的保護，奠定了「社會公義」「共同福祉」等核心原則。此文開啟了天主教持續至今的社會通諭傳統，深刻影響二十世紀的基督教社會關懷與政治倫理。', link: '/encyclicals' },
          { title_zh: '和平於世通諭', title_orig: 'Pacem in Terris', author: '若望二十三世', era: '1963', place: '梵蒂岡', language: '拉丁文', intro: '在古巴飛彈危機後、冷戰最緊張之際發布的歷史性通諭，是首篇明確致「全體善意人士」而非僅天主教徒的教宗文獻。通諭以人權與人性尊嚴為基礎，系統論述個人、社群、國家與國際社會四層次的權利義務，呼籲以信任取代核武嚇阻，建立有效的世界公權力。它體現梵二前夕教會向全人類開放的精神，成為現代基督教和平與人權思想的里程碑。', link: '/encyclicals' },
          { title_zh: '民族發展通諭', title_orig: 'Populorum Progressio', author: '保祿六世', era: '1967', place: '梵蒂岡', language: '拉丁文', intro: '將社會訓導從一國勞資問題擴展至全球發展正義的關鍵通諭。保祿六世提出「發展是和平的新名字」，譴責富國與窮國間日益擴大的不公，呼籲整全的人性發展、公平的國際貿易與富國對貧國的責任。此文回應了去殖民化時代的全球處境，把天主教社會思想提升到國際正義與人類團結的高度，影響了日後的解放神學與全球倫理討論。', link: '/encyclicals' },
          { title_zh: '願他們合而為一通諭', title_orig: 'Ut Unum Sint', author: '若望保祿二世', era: '1995', place: '梵蒂岡', language: '拉丁文', intro: '天主教歷史上首篇以基督徒合一為唯一主題的教宗通諭，標題取自耶穌「願他們合而為一」的祈禱。若望保祿二世在此明確將普世合一列為教會不可逆轉的使命，坦承過往分裂的罪責，並破天荒地邀請其他教會就「教宗職權如何行使方能服務合一」進行對話。此通諭是現代普世合一運動最重要的天主教文獻，向東正教與新教伸出和解之手，影響至今。', link: '/encyclicals' },
          { title_zh: '人類救主通諭', title_orig: 'Redemptor Hominis', author: '若望保祿二世', era: '1979', place: '梵蒂岡', language: '拉丁文', intro: '若望保祿二世就任後的首篇通諭，為其整個牧職定調。通諭以基督為人類的救主、也是「通往人的道路」為核心，強調教會的使命在於守護人性尊嚴與人權，並把基督救贖與當代人的具體處境緊密相連。此文奠定了他「基督人學」的神學基調，把對人的關懷、對自由與真理的捍衛貫穿其後二十餘年的訓導，是理解這位教宗思想的鑰匙。', link: '/encyclicals' },
          { title_zh: '真理的光輝通諭', title_orig: 'Veritatis Splendor', author: '若望保祿二世', era: '1993', place: '梵蒂岡', language: '拉丁文', intro: '若望保祿二世論基本道德神學的重要通諭，回應現代相對主義對客觀道德真理的挑戰。通諭重申存在著普遍而不可違背的道德規範，根植於人性與神聖律法，駁斥將良心與真理對立、以情境消解道德絕對的傾向。此文是二十世紀末天主教倫理訓導的奠基之作，對教會內外關於良心、自由與真理的辯論影響深遠。', link: '/encyclicals' },
          { title_zh: '上主與賦予生命者通諭', title_orig: 'Dominum et Vivificantem', author: '若望保祿二世', era: '1986', place: '梵蒂岡', language: '拉丁文', intro: '若望保祿二世論聖神在教會與世界中工作的通諭，完成其聖三系列三部曲。通諭闡述聖神作為「賦予生命者」如何使基督的救贖在歷史中實現，光照人心、定罪過、引向真理，並在現代世俗化、唯物主義盛行的處境中喚醒人對神的渴慕。此文深化了現代天主教的聖神論，並為跨宗派的靈恩與屬靈更新運動提供神學反思的資源。', link: '/encyclicals' },
          { title_zh: '在真理中實踐愛德通諭', title_orig: 'Caritas in Veritate', author: '本篤十六世', era: '2009', place: '梵蒂岡', language: '拉丁文', intro: '本篤十六世在全球金融危機背景下發布的社會通諭，承續並更新《民族發展通諭》的精神。通諭主張真正的發展必須以「在真理中的愛」為動力，把倫理重新置於經濟與全球化的核心，論及公益事業、市場道德、環境責任與全球治理。此文把愛德與正義、信仰與理性緊密結合，是二十一世紀天主教社會訓導對全球化時代的深刻回應。', link: '/encyclicals' },
          { title_zh: '願祢受讚頌通諭', title_orig: 'Laudato Si', author: '方濟各', era: '2015', place: '梵蒂岡', language: '拉丁文（並廣傳於各語譯本）', intro: '史上首篇以生態關懷為主題的教宗通諭，標題取自亞西西聖方濟的太陽歌。方濟各提出「整全生態學」，將環境危機與社會不公視為同一根源——人對受造界與弱者的剝削，呼籲全人類進行「生態皈依」，照顧「我們共同的家園」。此文超越宗教界限，致全球每一個人，對國際氣候談判與跨宗教環境運動產生實質影響，是現代基督教向世界發聲的標誌性文獻。', link: '/encyclicals' },
          { title_zh: '眾位弟兄通諭', title_orig: 'Fratelli Tutti', author: '方濟各', era: '2020', place: '梵蒂岡', language: '拉丁文（並廣傳於各語譯本）', intro: '方濟各論「弟兄情誼與社會友愛」的社會通諭，以慈善的撒瑪利亞人比喻為核心意象。通諭呼籲超越國界、宗教與種族的普世手足之愛，譴責民粹主義、戰爭、死刑與排外，倡議建立更具團結與包容的世界政治與經濟秩序。此文深受其與伊斯蘭長老共簽《人類兄弟情誼文件》的啟發，是現代基督教推動跨宗教和平與全球團結的重要宣言。', link: '/encyclicals' }
        ]
      },
      {
        key: 'ecumenical-letters',
        label: '普世合一書信部',
        label_en: 'Ecumenical Correspondence',
        desc: '收錄教宗與東正教普世牧首的共同聲明，及各宗派合一對話的往來文件，是普世合一運動的直接見證。',
        works: [
          { title_zh: '保祿六世與雅典納哥拉一世共同聲明', title_orig: 'Common Declaration of Pope Paul VI and Patriarch Athenagoras I', author: '保祿六世、君士坦丁堡普世牧首雅典納哥拉一世', era: '1965', place: '羅馬／伊斯坦堡', language: '拉丁文‧希臘文', intro: '羅馬天主教與東正教關係史上的劃時代文件。1054年東西教會大分裂時雙方互相絕罰，此共同聲明於梵二閉幕前夕同時在羅馬與伊斯坦堡宣讀，正式「從教會的記憶與當中除去」九百年前的相互絕罰，表達彼此的悔意與重歸於好的渴望。這象徵性的和解行動開啟了東西方教會持續至今的對話，是現代普世合一運動最動人的一刻。', link: '/creeds' },
          { title_zh: '若望保祿二世與迪米特里奧斯一世共同聲明', title_orig: 'Common Declaration of Pope John Paul II and Patriarch Dimitrios I', author: '若望保祿二世、君士坦丁堡普世牧首迪米特里奧斯一世', era: '1979', place: '伊斯坦堡', language: '希臘文‧拉丁文', intro: '若望保祿二世與普世牧首迪米特里奧斯一世在伊斯坦堡發表的共同聲明，正式宣布成立天主教與東正教神學對話聯合委員會，把前任所開啟的「愛的對話」推進為「真理的對話」。此文確立了兩大教會以神學議題為核心、有組織地尋求完全共融的長期進程，是東西方教會合一從象徵和解走向實質神學協商的關鍵轉折。', link: '/creeds' },
          { title_zh: '聯合稱義教義宣言', title_orig: 'Joint Declaration on the Doctrine of Justification', author: '羅馬天主教會與世界信義宗聯會', era: '1999', place: '德國‧奧格斯堡', language: '德文‧英文', intro: '天主教與信義宗（路德宗）就宗教改革核心爭議「因信稱義」達成的歷史性共識文件，於奧格斯堡簽署。雙方確認在稱義的基本真理上已有共同理解，使十六世紀彼此的相關定罪不再適用於今日的對話夥伴。此宣言化解了分裂西方教會近五百年的神學癥結，後更獲衛理公會等宗派認同,是新教與天主教合一對話最重大的成果之一。', link: '/creeds' },
          { title_zh: '方濟各與基里爾共同聲明', title_orig: 'Joint Declaration of Pope Francis and Patriarch Kirill', author: '方濟各、莫斯科及全俄羅斯宗主教基里爾', era: '2016', place: '古巴‧哈瓦那', language: '俄文‧義大利文', intro: '羅馬天主教教宗與莫斯科宗主教的首次會晤共同聲明，於古巴哈瓦那簽署，結束了天主教與俄羅斯東正教近千年來最高領袖從未相見的局面。聲明關注中東基督徒所受的迫害、家庭與生命的保護,以及世界和平,並坦誠面對兩教會間的歷史張力。此會晤雖有其政治背景與爭議,仍是現代東西教會關係的重要事件。', link: '/creeds' }
        ]
      },
      {
        key: 'pastoral-prison',
        label: '現代牧函與獄中書簡部',
        label_en: 'Modern Pastoral Letters and Prison Writings',
        desc: '收錄現代信仰見證者在困境中寫成的書信與主教團牧函,以書信之體傳遞信仰與良知的力量。',
        works: [
          { title_zh: '獄中書簡', title_orig: 'Widerstand und Ergebung (Letters and Papers from Prison)', author: '潘霍華', era: '1943–1945（1951年出版）', place: '德國‧柏林（蓋世太保監獄）', language: '德文', intro: '德國信義宗神學家潘霍華因參與反抗希特勒而被囚,在獄中寫給友人與家人的書信集,死後由其學生編輯出版。書中探討「非宗教性的基督教」「在世俗世界中如何談論神」「為他人而存在的教會」等前瞻命題,以及在絕境中對信仰、苦難與盼望的深刻沉思。潘霍華於戰爭結束前數週被處決,這部書簡成為二十世紀基督教殉道見證與神學思想的不朽經典。' },
          { title_zh: '伯明罕獄中書信', title_orig: 'Letter from Birmingham Jail', author: '馬丁路德金', era: '1963', place: '美國‧阿拉巴馬州伯明罕', language: '英文', intro: '美國民權運動領袖馬丁路德金因非暴力抗議種族隔離被捕,在獄中回應白人教牧批評其行動「不合時宜」而寫成的公開信。信中以聖經、奧古斯丁與阿奎那的傳統論證公民不服從的正當性,區分公義與不義的法律,並對沉默的「溫和派」提出沉痛呼籲。此信是二十世紀基督教社會良知與非暴力抗爭的經典文獻,將福音信仰與爭取人權的鬥爭緊密結合。' },
          { title_zh: '正義的經濟——天主教社會訓導與美國經濟牧函', title_orig: 'Economic Justice for All', author: '美國天主教主教團', era: '1986', place: '美國', language: '英文', intro: '美國天主教主教團發表的重要牧函,將天主教社會訓導的原則應用於美國經濟現況。牧函以人性尊嚴與「對窮人的優先選擇」為準繩,評估貧富差距、失業與貧困問題,呼籲建立更公道的經濟秩序。此文體現現代主教團以集體牧函介入公共政策、為弱勢發聲的傳統,是天主教社會思想在地化、面對具體國情的代表作。' }
        ]
      }
    ]
  },
  wai: {
    summary: '外藏收錄基督教傳統之外的新興宗教公開信與世俗思潮宣言,作為理解現代基督教所處的多元信仰與世俗化環境的旁參。',
    divisions: [
      {
        key: 'new-religions',
        label: '新興宗教公開信部',
        label_en: 'Open Letters of New Religious Movements',
        desc: '收錄現代新興宗教領袖致世界的公開信,反映現代多元宗教景觀對基督教的挑戰與對話空間。',
        works: [
          { title_zh: '巴哈歐拉致諸王書', title_orig: 'The Summons of the Lord of Hosts (Súriy-i-Mulúk)', author: '巴哈歐拉', era: '十九世紀中葉（現代英譯刊行）', place: '鄂圖曼帝國（流放地）', language: '阿拉伯文‧波斯文（譯為英文）', intro: '巴哈伊信仰創立者巴哈歐拉在流放期間致當時各國君王與宗教領袖的一系列公開書信,宣告新時代的來臨,呼籲世界統一、消弭戰爭、實現人類大同。書信致函包括鄂圖曼蘇丹、波斯國王、教宗庇護九世與歐洲諸君主。作為新興世界宗教的根本文獻之一,它以「公開信」之體向全人類發聲,其普世和平的訴求,在現代宗教對話的脈絡中常被論及。' }
        ]
      },
      {
        key: 'secular-manifestos',
        label: '世俗宣言部',
        label_en: 'Secular Manifestos',
        desc: '收錄現代世俗人文主義的宣言文獻,作為理解基督教在世俗化時代所面對的思想對話對象。',
        works: [
          { title_zh: '人文主義宣言（第一篇）', title_orig: 'Humanist Manifesto I', author: '一群美國人文主義者（雷蒙德‧布拉格起草等）', era: '1933', place: '美國', language: '英文', intro: '由三十餘位美國學者、神職人員與思想家共同簽署的宣言,提出以理性、科學與人類福祉為基礎的「宗教人文主義」,主張宇宙是自存的、人類是自然演化的產物,反對超自然神觀與來世盼望,強調在此世建立更公義的社會。此文是現代世俗人文主義運動的奠基文獻,代表二十世紀無神論與自然主義對傳統宗教的系統挑戰,是基督教護教與對話無法迴避的對象。' },
          { title_zh: '人文主義宣言（第二篇）', title_orig: 'Humanist Manifesto II', author: '保羅‧庫爾茲、愛德溫‧威爾遜起草', era: '1973', place: '美國', language: '英文', intro: '第一篇宣言問世四十年後,在經歷二戰、極權與核武威脅之後修訂的新版宣言。它在保留世俗人文主義核心的同時,語氣更為審慎,強調人權、民主、宗教自由、世界公民意識與科技倫理,並明確與一切極權主義劃清界限。此文反映二十世紀下半葉世俗思潮的成熟與自省,持續界定著現代基督教與世俗人文主義之間既對立又對話的複雜關係。' }
        ]
      }
    ]
  }
},
    {
  key: 'liyi',
  name: '禮儀藏',
  name_en: 'Liturgy & Worship Canon',
  glyph: '儀',
  genres: '禮儀改革‧聖樂‧靈修',
  summary: '收錄二十世紀以降基督宗教的禮儀運動、崇拜禮文修訂與聖樂創作，並及普世群體靈修操練與當代敬拜音樂；外藏旁收新興宗教與民間融合傳統的儀式文獻，呈現現代世界禮儀想像的廣闊光譜。',
  zheng: {
    summary: '正藏分三部，依「禮儀運動與改革—普世與群體靈修—現代聖樂」的脈絡，記錄二十世紀至今正統基督宗教崇拜的更新與重整。',
    divisions: [
      {
        key: 'liturgical-reform',
        label: '禮儀運動與改革部',
        label_en: 'Liturgical Movement & Reform',
        desc: '二十世紀禮儀運動及梵二《禮儀憲章》後的羅馬彌撒改革、新教公禱書修訂與合一崇拜禮文。',
        works: [
          { title_zh: '禮儀年', title_orig: 'Das Jahr des Heiles / The Church\'s Year of Grace', author: '加比尼‧瑪利亞‧拉特曼(Pius Parsch)', era: '1923–1934', place: '奧地利‧克洛斯特新堡', language: '德文', intro: '克洛斯特新堡奧斯定詠禮會士帕施（Pius Parsch）所編的禮儀年釋義鉅著，逐主日逐瞻禮疏解彌撒經文與日課，把學院化的禮儀學帶進堂區信眾。帕施與本篤會學者並列為二十世紀「禮儀運動」（Liturgical Movement）的奠基者，主張「彌撒是信眾的公共行動」而非神父獨演。此書以牧靈語言貫通聖經、教父與禮儀文本，深刻影響了梵二前的崇拜更新，被視為後來《禮儀憲章》強調「信眾完整、主動、有意識參與」的先聲。' },
          { title_zh: '禮儀精神', title_orig: 'Vom Geist der Liturgie / The Spirit of the Liturgy', author: '羅曼諾‧瓜爾迪尼(Romano Guardini)', era: '1918', place: '德國‧博伊隆', language: '德文', intro: '德國神學家瓜爾迪尼出自博伊隆本篤會傳統的小書，是禮儀運動最具影響力的綱領性著作。全書以「遊戲」「象徵」「群體」「風格」等範疇，論證禮儀並非個人虔敬的堆疊，而是教會作為基督奧體在時間中演出的客觀崇拜。瓜爾迪尼強調禮儀的「無目的性」——它不為功用而存在，正如孩童的遊戲。此書深植於拉辛格（後為本篤十六世）一代神學家心中，後者更以同名著作與之對話，可謂二十世紀崇拜神學的源頭活水。' },
          { title_zh: '羅馬彌撒經書(保祿六世版)', title_orig: 'Missale Romanum (editio typica 1970)', author: '梵蒂岡禮儀聖部', era: '1969–1970頒布', place: '梵蒂岡', language: '拉丁文', intro: '梵二大公會議《禮儀憲章》後，依保祿六世1969年《羅馬彌撒經書》宗座憲令所頒行的全新彌撒經書，史稱「保祿六世彌撒」或「新禮」。其改革幅度為千年所僅見：恢復信眾語言（本地語）誦念、重訂三年主日讀經週期、增訂多式感恩經（Eucharistic Prayers）、簡化重複經文並重申主日為復活慶典。此書取代了1570年特倫多後沿用四百年的庇護五世彌撒經書，是現代天主教崇拜的核心法定文本，至今仍為絕大多數堂區所用。' },
          { title_zh: '禮儀憲章', title_orig: 'Sacrosanctum Concilium', author: '梵蒂岡第二屆大公會議', era: '1963', place: '梵蒂岡', language: '拉丁文', intro: '梵二大公會議通過的第一份文獻，亦是整場會議改革精神的鑰匙。憲章宣告禮儀是「教會行動所趨向的頂峰，同時是教會一切力量的泉源」，並確立「信眾完整、有意識、主動的參與」為崇拜更新的最高原則。它授權使用本地語言、推動本地化（inculturation）、簡化儀節並重視聖言宣讀。此文件直接催生了新彌撒經書、新日課與全套聖事禮典的修訂，其影響溢出天主教，激勵了普世各宗派二十世紀後半的禮儀改革浪潮。' },
          { title_zh: '公禱書(1979美國聖公會版)', title_orig: 'The Book of Common Prayer (1979)', author: '美國聖公會', era: '1979', place: '美國', language: '英文', intro: '美國聖公會在禮儀運動與梵二影響下完成的公禱書全面修訂版，距1928年版逾半世紀。新版恢復古教會的崇拜結構，將感恩聖禮（Eucharist）重新置於主日崇拜中心，提供傳統語（Rite One）與現代語（Rite Two）兩套禮文，並大幅擴充聖洗禮、按手禮與每日禱告。它確立「洗禮聖約」為信徒身分的根基，影響了普世聖公宗各省的禮文修訂，是二十世紀英語世界最具份量的崇拜典籍之一。' },
          { title_zh: '利馬禮文', title_orig: 'Baptism, Eucharist and Ministry (Lima Liturgy)', author: '普世教會協會信仰與教制委員會', era: '1982', place: '秘魯‧利馬', language: '英文', intro: '普世教會協會（WCC）信仰與教制委員會在利馬通過《洗禮、聖餐與聖職》文件時，所附的一份示範感恩崇拜禮文。它嘗試以一套眾教會都能共用的聖餐禮，具體展現合一神學的可能，融會東正教的呼求聖靈（epiclesis）、天主教的獻祭語言與更正教的記念神學。利馬禮文雖無法定地位，卻成為二十世紀合一運動最重要的崇拜象徵，在無數普世聚會中被採用，體現「分裂的教會在同一張桌前」的盼望。' }
        ]
      },
      {
        key: 'ecumenical-spirituality',
        label: '普世與群體靈修部',
        label_en: 'Ecumenical & Communal Spirituality',
        desc: '泰澤短誦、依納爵神操的現代復興，及靈恩運動的讚美與敬拜。',
        works: [
          { title_zh: '泰澤團體歌詠與禱告', title_orig: 'Chants de Taizé', author: '羅哲修士(Frère Roger Schütz)與泰澤團體', era: '1940年代起', place: '法國‧泰澤', language: '法文‧拉丁文‧多語', intro: '泰澤是羅哲修士二戰期間在法國勃艮第創立的合一修道團體，其崇拜以簡短、反覆、多語的「短誦」（chant）著稱。一句經文配上冥想式的旋律，由會眾循環吟唱數分鐘乃至更久，使禱告沉入靜默與身體記憶。泰澤短誦由作曲家貝爾蒂耶（Jacques Berthier）等譜成，跨越天主教、更正教與東正教的藩籬，成為全球青年朝聖與普世靈修的共同語言，是二十世紀群體靈修最廣為流傳的果實。' },
          { title_zh: '神操', title_orig: 'Exercitia spiritualia', author: '依納爵‧羅耀拉(Ignatius of Loyola)', era: '十六世紀著作‧二十世紀復興', place: '西班牙(原典)‧全球(復興)', language: '拉丁文(原典)', intro: '《神操》原為十六世紀耶穌會創始人依納爵所著的避靜操練手冊，二十世紀經耶穌會靈修學者重新詮釋而大放異彩。現代復興強調「在日常生活中作神操」（第十九註釋避靜）、想像式默觀福音場景，及「分辨諸神」（discernment of spirits）的內在功夫。它從修院走入平信徒，成為個別靈修指導（spiritual direction）的方法核心。此處收其作為現代群體與個人靈修運動的活水源頭，見證古典操練在當代的再生。' },
          { title_zh: '哈利路亞讚美操練(靈恩敬拜)', title_orig: 'Praise & Worship (Charismatic Renewal)', author: '靈恩更新運動', era: '1960年代起', place: '美國‧全球', language: '英文‧多語', intro: '二十世紀中葉興起的靈恩更新運動（Charismatic Renewal），橫掃天主教、聖公會與各更正教宗派，帶來一種以「讚美與敬拜」（Praise & Worship）為核心的崇拜形態。其特徵為自發禱告、舉手、方言、按手醫治，及由短歌串接的長時段敬拜，強調聖靈當下臨在與信徒情感的直接投入。它顛覆了正典禮文的固定結構，催生了當代敬拜音樂產業，並深刻形塑了今日全球福音派與五旬節派的崇拜風貌。' }
        ]
      },
      {
        key: 'modern-sacred-music',
        label: '現代聖樂部',
        label_en: 'Modern Sacred Music',
        desc: '二十世紀聖詩與聖樂創作，及當代敬拜音樂。',
        works: [
          { title_zh: '時間終結四重奏', title_orig: 'Quatuor pour la fin du temps', author: '奧利維埃‧梅湘(Olivier Messiaen)', era: '1941', place: '德國‧戈爾利茨戰俘營', language: '法文(標題與註)', intro: '法國作曲家梅湘於二戰戰俘營中為小提琴、單簧管、大提琴與鋼琴所作的室內樂，被譽為二十世紀最深刻的宗教音樂之一。標題取自《啟示錄》第十章「天使宣告時間不再有了」，全曲八個樂章以梅湘獨特的「有限移位調式」與「不可逆節奏」，描繪永恆對時間的吞沒。身為虔誠天主教徒，梅湘視鳥鳴為造物的讚歌，視調式色彩為神聖之光的折射。此作在鐵絲網後首演，是信仰於極境中對永恆盼望的音樂見證。' },
          { title_zh: '為弦樂而作的悲歌交響曲(聖樂面向)', title_orig: 'Symphony No. 3 "Symphony of Sorrowful Songs"', author: '亨利克‧戈雷茨基(Henryk Górecki)', era: '1976', place: '波蘭', language: '波蘭文', intro: '波蘭作曲家戈雷茨基的第三號交響曲，以三段緩慢的女高音詠唱構成，歌詞分別取自十五世紀波蘭聖母哀歌、一名少女刻在蓋世太保牢房牆上的禱詞，與一首民間哀歌。全曲沉浸於聖母悲傷（Stabat Mater）的傳統意象，以極簡而綿長的音響承載大屠殺與母性受苦的記憶。它代表二十世紀末「神聖極簡主義」（holy minimalism）的高峰，在世俗化的時代以靜默與哀歌，重新打開了宗教音樂的當代空間。' },
          { title_zh: '當代敬拜詩歌選(Hillsong/Bethel/Vineyard)', title_orig: 'Contemporary Worship Music', author: 'Hillsong/Bethel Music/Vineyard 等', era: '1980年代起', place: '澳洲‧美國‧全球', language: '英文‧多語', intro: '源自葡萄園運動（Vineyard）與澳洲新頌教會（Hillsong）等的當代敬拜音樂，以搖滾與流行樂編制取代管風琴與聖詩本，成為全球福音派崇拜的主流聲音。其歌詞重抒情、重個人與神的親密，常以副歌反覆營造敬拜高潮；藉著唱片、版權授權（CCLI）與媒體傳播，形成跨國的崇拜文化工業。此處收其作為二十世紀末至今最具影響力的聖樂現象，其神學深淺與商業化爭議，亦是當代崇拜學的重要課題。' }
        ]
      }
    ]
  },
  wai: {
    summary: '外藏旁收基督宗教正統之外的現代禮儀文獻，記錄新興宗教與民間融合傳統如何挪用、轉化儀式語言，以見現代世界儀式想像的多元面貌。',
    divisions: [
      {
        key: 'new-religious-rites',
        label: '新興宗教禮儀部',
        label_en: 'New Religious Movement Rites',
        desc: '新世紀運動的冥想與儀式實踐。',
        works: [
          { title_zh: '新世紀冥想與儀式手冊', title_orig: 'New Age Meditation & Ritual', author: '新世紀運動(綜合)', era: '1970年代起', place: '美國‧西歐‧全球', language: '英文‧多語', intro: '新世紀運動（New Age）並無統一教義或經典，而是一鬆散的靈性潮流，雜揉東方禪修、瑜伽、靈媒通靈、水晶療癒、占星與西方神秘學。其「儀式」多為個人化的自我轉化操練——導引式冥想、觀想光與能量、節氣慶典與身心整合工作坊，強調「內在神性」與「意識揚升」。此處收其儀式實踐文獻作為外藏對照，呈現後基督教西方在制度宗教衰退後，如何以拼貼方式重構神聖經驗與身體儀式。' }
        ]
      },
      {
        key: 'folk-syncretic-rites',
        label: '民間與融合禮儀部',
        label_en: 'Folk & Syncretic Rites',
        desc: '拉斯塔法里 Nyabinghi 集會與雷鬼音樂中的儀式傳統。',
        works: [
          { title_zh: '尼亞賓基集會(Nyabinghi)儀典', title_orig: 'Nyabinghi (Binghi) Grounation', author: '拉斯塔法里運動', era: '1940年代起', place: '牙買加', language: '牙買加帕特瓦語‧英文', intro: '尼亞賓基（Nyabinghi）是拉斯塔法里運動最古老、最具儀式性的支派，其集會（grounation / groundation）以徹夜的擊鼓、吟唱聖詩與祈禱構成，鼓組分 bass、funde、repeater 三層，節奏被視為「大地的心跳」與通往至高者（Jah）的橋樑。集會中焚燒聖草、誦讀《詩篇》並讚頌海爾‧塞拉西一世為再臨的彌賽亞。此處收其作為融合非洲傳統、舊約敬拜與牙買加民間信仰的儀式體系，是雷鬼音樂的靈性母胎，亦現代外藏禮儀的鮮明案例。' }
        ]
      }
    ]
  }
},
    {
  key: 'shiwen',
  name: '詩藝藏',
  name_en: 'Poetry and Arts Treasury',
  glyph: '詩',
  genres: '文學‧聖詩‧藝術',
  summary: '收錄二十世紀以降的基督教文學、現代聖詩與靈修詩篇，自陀思妥耶夫斯基的承先，至路易斯、托爾金、艾略特、奧康納、遠藤周作的小說與戲劇，及霍普金斯、湯瑪斯的詩藝；外藏以拉斯塔法里與雷鬼神學的讚美詩為主軸，旁及新興宗教靈性文學。',
  zheng: {
    summary: '正藏分三部，依「敘事文學—聖詩讚美—詩與默想」的脈絡，呈現現代基督教如何以想像力與語言藝術承載信仰。',
    divisions: [
      {
        key: 'christian-literature',
        label: '基督教文學部',
        label_en: 'Christian Literature',
        desc: '二十世紀前後承先啟後的基督教小說與戲劇。',
        works: [
          { title_zh: '卡拉馬助夫兄弟們', title_orig: 'Братья Карамазовы', author: '費奧多爾‧陀思妥耶夫斯基(Fyodor Dostoevsky)', era: '1880', place: '俄國', language: '俄文', intro: '陀思妥耶夫斯基的最後鉅著，以一樁弒父案串起三兄弟的信仰、理性與肉慾衝突，被視為現代基督教文學的源頭與顛峰。書中「宗教大法官」一章假托基督重臨人間，逼問自由與麵包、信心與權力的兩難，成為神義論的經典文本；而佐西馬長老與阿廖沙則體現了東正教「主動之愛」與謙卑受苦的靈性。此書承十九世紀之終、啟二十世紀宗教思想之端，路易斯、巴特、巴爾塔薩無不受其震撼，是本藏「承先」的奠基之作。' },
          { title_zh: '納尼亞傳奇', title_orig: 'The Chronicles of Narnia', author: 'C.S.路易斯(C. S. Lewis)', era: '1950–1956', place: '英國‧牛津', language: '英文', intro: '路易斯為兒童所寫的七部曲奇幻小說，以獅王阿斯蘭（Aslan）為核心，藉異世界納尼亞重述創造、墮落、救贖與末世的基督教敘事。《獅子、女巫、魔衣櫥》中阿斯蘭代石桌上的艾德蒙受死又復活，是福音的童話轉寫。路易斯主張藉「假設的奇幻」繞過讀者對宗教的成見，讓真理「悄悄潛入」（steal past）防備之心。全系列以澄澈的想像與道德深度，成為二十世紀最暢銷亦最受爭議的護教文學，影響數代英語世界讀者的信仰啟蒙。' },
          { title_zh: '地獄來鴻', title_orig: 'The Screwtape Letters', author: 'C.S.路易斯(C. S. Lewis)', era: '1942', place: '英國‧牛津', language: '英文', intro: '路易斯以一名資深魔鬼「老魔」（Screwtape）寫給見習小鬼侄兒的三十一封信構成的諷刺體護教小說。藉魔鬼的「反向」視角，犀利剖析人性的自欺、虛榮、屬靈怠惰與日常罪的微妙機制——魔鬼最得意的不是滔天大惡，而是「不知不覺把人引向平緩的下坡」。此書以機智幽默包裹深刻的靈修洞察，是路易斯最受喜愛的作品之一，二戰期間連載於報端，鼓舞無數信徒在試探中保持警醒，至今仍為靈命操練的經典讀物。' },
          { title_zh: '魔戒', title_orig: 'The Lord of the Rings', author: 'J.R.R.托爾金(J. R. R. Tolkien)', era: '1954–1955', place: '英國‧牛津', language: '英文', intro: '托爾金窮數十年之功構築的史詩奇幻，以摧毀至尊魔戒的遠征，演繹犧牲、憐憫、盼望與惡的本質。身為虔誠天主教徒，托爾金否認故事是寓言，卻自承全書「根本上是宗教與天主教的作品」，其救贖深藏於情節肌理：弗羅多的捨己、咕嚕得憐憫而意外成全使命、「天命眷顧」（eucatastrophe）的悲喜翻轉。他更以《論童話故事》闡明福音乃「成真的童話」。此作確立了現代奇幻文類，亦為基督教想像力如何重塑神話提供了典範。' },
          { title_zh: '正統', title_orig: 'Orthodoxy', author: 'G.K.切斯特頓(G. K. Chesterton)', era: '1908', place: '英國', language: '英文', intro: '切斯特頓最著名的護教散文，以自傳體記述他如何「自行航向真理，卻發現早有教會抵達」的思想歷程。全書以悖論為利器——「神話幾近全真」「瘋子是失去一切只剩理性的人」「童話蘊含最深的常理」——論證正統信仰非但不窒礙生命，反是唯一容得下喜樂、冒險與健全理智的框架。其機鋒與想像力深深啟發了路易斯一代。此書與《卡拉馬助夫兄弟們》同列本藏「承先」之作，是二十世紀英語護教文學的奠基石。' },
          { title_zh: '四個四重奏', title_orig: 'Four Quartets', author: 'T.S.艾略特(T. S. Eliot)', era: '1943', place: '英國', language: '英文', intro: '艾略特皈依英國國教後的成熟詩作，由四首長詩組成，各以一地名為題，環繞時間、永恆、記憶與救贖默想。詩中「現在的時間與過去的時間，或許都臨在於未來的時間」開展對道成肉身——永恆切入時間的核心默觀，融會聖十字若望的神秘神學與但丁的宇宙觀。「靜止的轉點」（the still point）一意象，凝定了動與靜、言與默的張力。此作被譽為英語現代詩中最偉大的宗教詩篇，是冥想式信仰詩藝的頂峰。' },
          { title_zh: '大教堂謀殺案', title_orig: 'Murder in the Cathedral', author: 'T.S.艾略特(T. S. Eliot)', era: '1935', place: '英國‧坎特伯雷', language: '英文', intro: '艾略特為坎特伯雷大教堂藝術節所寫的詩劇，搬演1170年大主教托馬斯‧貝克特殉道的史事。全劇核心是貝克特面對四名「誘惑者」——尤以最後一名引誘他「為錯誤的理由求殉道之榮」，逼出對動機純粹性的尖銳叩問：「最大的叛逆是為了錯的理由做對的事。」劇中希臘式歌隊（坎特伯雷婦女）的合唱，將恐懼與聖潔交織。此作復興了英語詩劇傳統，是二十世紀宗教戲劇的典範，凝鍊地探討了自由意志、殉道與神聖意志的奧秘。' },
          { title_zh: '好人難尋', title_orig: 'A Good Man Is Hard to Find', author: '弗蘭納里‧奧康納(Flannery O\'Connor)', era: '1955', place: '美國‧喬治亞', language: '英文', intro: '美國南方天主教作家奧康納的短篇小說集代表作，以「南方哥德式」筆法描寫扭曲、暴力卻被恩典突襲的人物。同名短篇中，一家人遇上逃犯「不合時宜者」（The Misfit），祖母在槍口前的剎那竟伸手認他為「自己的孩子」，於暴力中迸現恩典的閃光。奧康納自言其小說充滿「怪誕」，因須以誇張的形象向「看不見的讀者」喊出真理。她的作品冷峻、不留情面，卻深植於道成肉身與原罪的信念，是二十世紀基督教文學最獨特的聲音之一。' },
          { title_zh: '沉默', title_orig: '沈黙', author: '遠藤周作(Endō Shūsaku)', era: '1966', place: '日本', language: '日文', intro: '日本天主教作家遠藤周作的長篇小說，以十七世紀禁教時期一名葡萄牙傳教士洛特里哥潛入日本、終至「踏繪」棄教的歷程，叩問神在受苦中的沉默。當信徒因他不肯棄教而受刑，神的緘默逼出全書最深的張力；而最終那「踏下去吧，我比誰都明白你腳的痛」的聲音，把背叛轉化為另一種跟隨。遠藤以「日本這片泥沼」反思基督教在異文化的扎根難題，及軟弱者的信仰。此作被譽為二十世紀最深刻的信仰小說之一，叩擊神義論與文化處境的雙重幽暗。' }
        ]
      },
      {
        key: 'modern-hymnody',
        label: '現代聖詩與讚美部',
        label_en: 'Modern Hymnody & Praise',
        desc: '二十世紀聖詩、福音詩歌與當代敬拜詩歌。',
        works: [
          { title_zh: '二十世紀聖詩選', title_orig: '20th Century Hymnody', author: '綜合(Timothy Dudley-Smith 等)', era: '二十世紀', place: '英國‧美國‧全球', language: '英文‧多語', intro: '二十世紀的英語聖詩經歷了一場「聖詩爆發」（hymn explosion），在傳統四聲部聖詩之外注入現代神學與當代語言。達德利—史密斯（Timothy Dudley-Smith）的〈尊主頌〉（Tell Out, My Soul）、葛林（Fred Pratt Green）與萊特（Brian Wren）等人的作品，回應社會公義、生態與普世合一等新議題，文字更貼近現代信徒的處境與疑惑。此處收其作為傳統聖詩本在現代的延續與更新，見證會眾歌唱如何承載每一時代的神學重心。' },
          { title_zh: '福音詩歌選', title_orig: 'Gospel Songs', author: '綜合(Thomas A. Dorsey 等)', era: '十九世紀末–二十世紀', place: '美國', language: '英文', intro: '福音詩歌（Gospel Songs）源自美國復興運動與非裔教會傳統，以朗朗上口的副歌、見證式的歌詞與情感充沛的演唱見長。多西（Thomas A. Dorsey）被譽為「福音音樂之父」，其〈寶貴主，請牽我手〉（Precious Lord, Take My Hand）融藍調與聖詩於一爐，成為跨越種族的安慰之歌。福音詩歌深植於受苦與盼望的張力，孕育了後來的靈魂樂與當代敬拜，是二十世紀美國最具生命力的聖樂傳統，亦對全球教會歌唱影響深遠。' },
          { title_zh: '當代敬拜詩歌選', title_orig: 'Contemporary Worship Songs', author: '綜合(Graham Kendrick/Matt Redman 等)', era: '1980年代起', place: '英國‧美國‧全球', language: '英文‧多語', intro: '當代敬拜詩歌（Contemporary Worship Songs）以流行與搖滾樂語彙重塑會眾歌唱，肯德里克（Graham Kendrick）的〈萬古磐石為我開〉、瑞德曼（Matt Redman）的〈頌讚之歌〉（10,000 Reasons）等，主導了過去數十年全球教會的崇拜聲音。其歌詞多以第一人稱抒發對神的渴慕與委身，結構簡潔、易於跟唱，藉版權授權系統與媒體跨國流通。此處收其作為當代聖詩的主流形態，其神學取向與商業化張力，亦是現代崇拜詩學的核心議題。' }
        ]
      },
      {
        key: 'poetry-meditation',
        label: '詩與默想部',
        label_en: 'Poetry & Meditation',
        desc: '霍普金斯、R.S.湯瑪斯與現代靈修詩。',
        works: [
          { title_zh: '霍普金斯詩集', title_orig: 'Poems of Gerard Manley Hopkins', author: '傑拉德‧曼利‧霍普金斯(Gerard Manley Hopkins)', era: '十九世紀作‧1918出版', place: '英國', language: '英文', intro: '霍普金斯是維多利亞時代的耶穌會神父詩人，生前幾不發表，逝後三十年詩作始問世，卻深刻塑造了現代詩。他獨創「跳躍節奏」（sprung rhythm）與「內景」（inscape）概念，以密實緊湊的音韻捕捉萬物獨一的神聖印記——「世界滿載神的壯麗」。其〈風鷹〉（The Windhover）獻給「我們的主基督」，在隼鳥的俯衝中見道成肉身的榮耀；而晚年「恐怖十四行」（terrible sonnets）則直面屬靈枯乾的幽暗。此集是宗教詩藝跨越世代的瑰寶，影響艾略特以降的現代詩人。' },
          { title_zh: 'R.S.湯瑪斯詩選', title_orig: 'Selected Poems of R. S. Thomas', author: 'R.S.湯瑪斯(R. S. Thomas)', era: '二十世紀', place: '英國‧威爾斯', language: '英文', intro: '湯瑪斯是威爾斯鄉村教區的英國國教牧師詩人，畢生在荒僻山村牧會，其詩以冷峻、簡約而充滿張力的語言著稱。他被稱為「神缺席的詩人」，反覆書寫向沉默的神禱告的經驗——神彷彿總是「剛剛離去的房間」，信仰即在虛空前的持守等待。其〈在曠野〉〈缺席〉等詩，將否定神學（apophatic theology）化為現代詩的肌理。湯瑪斯的宗教詩不予安慰，卻以誠實面對信仰的幽暗與荒涼，是二十世紀英語靈修詩最深沉的聲音之一。' },
          { title_zh: '現代靈修詩選', title_orig: 'Modern Devotional Poetry', author: '綜合(Denise Levertov/Wendell Berry 等)', era: '二十世紀', place: '美國‧英國‧全球', language: '英文', intro: '二十世紀後半，一群詩人在世俗化的語境中重新探索信仰的詩意。萊弗托夫（Denise Levertov）晚年皈依後寫下〈三位一體之謎〉等沉思之作，貝里（Wendell Berry）以安息日詩篇（Sabbath Poems）將土地、勞作與敬虔融為一體，奧利弗（Mary Oliver）則在自然中聽見禱告。這些詩多不依附特定教派，卻以細膩的觀照與敬畏，重啟現代人對神聖的感知。此處收其作為當代靈修詩的多元面貌，見證詩歌如何在懷疑的時代仍為默想開路。' }
        ]
      }
    ]
  },
  wai: {
    summary: '外藏以拉斯塔法里與雷鬼神學的詩文為現代外詩主軸，記錄聖經意象如何在加勒比海被重新挪用與吟唱，旁收新興宗教靈性文學。',
    divisions: [
      {
        key: 'rastafari-reggae',
        label: '拉斯塔法里與雷鬼神學部',
        label_en: 'Rastafari & Reggae Theology',
        desc: '【現代外詩主軸】拉斯塔法里讚美詩，及雷鬼樂中的聖經神學——巴比倫與錫安意象。',
        works: [
          { title_zh: '拉斯塔法里讚美詩', title_orig: 'Rastafari Hymns / Chants', author: '拉斯塔法里運動', era: '1930年代起', place: '牙買加', language: '牙買加帕特瓦語‧英文', intro: '拉斯塔法里運動的讚美詩多改編自更正教聖詩與《詩篇》，再注入運動獨有的信念——尊海爾‧塞拉西一世為再臨的神（Jah Rastafari），視衣索比亞為應許之地。在尼亞賓基集會中，這些聖詩與鼓樂交織，徹夜吟唱，把舊約的出埃及與被擄敘事，轉化為非洲離散族裔回歸與救贖的盼望。其語言混融牙買加帕特瓦語的節奏與聖經的莊嚴，是這一融合宗教最核心的詩文傳統，也是雷鬼音樂神學的直接母體。' },
          { title_zh: '雷鬼神學詩文(巴比倫與錫安)', title_orig: 'Reggae Theology: Babylon & Zion', author: 'Bob Marley/Burning Spear/Peter Tosh 等', era: '1970年代起', place: '牙買加', language: '牙買加帕特瓦語‧英文', intro: '雷鬼音樂是拉斯塔法里神學最廣為傳播的載體，其歌詞建構了一套「巴比倫對錫安」的二元神學：「巴比倫」象徵壓迫的西方殖民體系、警察與物質主義，「錫安」則是非洲與屬靈解放的應許之地。鮑伯‧馬利的〈出埃及〉（Exodus）、〈救贖之歌〉（Redemption Song）以出埃及與被擄歸回的舊約意象，唱出第三世界的受苦與盼望；燃燒之矛（Burning Spear）則吟誦先知般的歷史記憶。此處立為現代外詩主軸，見證聖經敘事在加勒比海如何被吟成抵抗與救贖的詩篇。' }
        ]
      },
      {
        key: 'new-religious-literature',
        label: '新興宗教文學部',
        label_en: 'New Religious Movement Literature',
        desc: '新世紀靈性文學。',
        works: [
          { title_zh: '新世紀靈性文學選', title_orig: 'New Age Spiritual Literature', author: '綜合(Eckhart Tolle/Paulo Coelho 等)', era: '二十世紀末起', place: '全球', language: '英文‧多語', intro: '新世紀靈性文學以暢銷書形式傳播一種去制度化、混融多源的靈修觀。托勒（Eckhart Tolle）的《當下的力量》倡言活在此刻、消解小我，柯艾略（Paulo Coelho）的《牧羊少年奇幻之旅》以寓言述說追隨「天命」的旅程，雜揉煉金術、蘇菲與基督教意象。這類作品常援引耶穌與聖經語句，卻置於泛靈與內在神性的框架中重新詮釋。此處收其作為外藏對照，呈現後基督教時代靈性需求如何在書市中被重新包裝與供應，及其與正統信仰的張力。' }
        ]
      }
    ]
  }
},
    {
  key: 'xuandao',
  name: '宣道藏',
  name_en: 'Canon of Preaching and Mission',
  glyph: '宣',
  genres: '講道‧佈道‧解經',
  summary: '收錄一九〇〇年以降現代基督宗教的講道、佈道與解經文獻，自承先啟後的講壇巨著、跨洲復興與佈道大會，到普世宣教與處境化神學的本色實踐。正藏循「講道解經‧大型佈道復興‧全球處境宣教」三部，呈現現代基督教如何在講壇與宣教場域上將福音傳遞於世；外藏則旁收新興宗教的逐戶宣教文宣，以及世俗人本與無神論的公共演說，以資對照。',
  zheng: {
    summary: '正藏三部，依「講壇解經—群眾佈道—普世宣教」的現代福音傳播脈絡編次。',
    divisions: [
      {
        key: 'modern-preaching-exegesis',
        label: '現代講道與解經部',
        label_en: 'Modern Preaching and Exposition',
        desc: '承襲清教徒講壇傳統的逐卷釋經與系統講道，講壇與書齋並重。',
        works: [
          { title_zh: '大衛的寶庫', title_orig: 'The Treasury of David', author: '司布真（Charles Haddon Spurgeon）', era: '一八六九–一八八五年', place: '英國倫敦', language: '英文', intro: '司布真歷時逾二十年完成的詩篇全卷釋經巨著，逐篇詳註並廣輯歷代解經家之說，兼具學術深度與講壇熱情。雖始撰於十九世紀，其完成、增訂與普世影響皆延入二十世紀，被尊為英語世界詩篇講道的標竿，承先啟後地將清教徒釋經傳統帶入現代講壇，故列為本部承先之作。' },
          { title_zh: '登山寶訓研究', title_orig: 'Studies in the Sermon on the Mount', author: '鍾馬田（D. Martyn Lloyd-Jones）', era: '一九五九–一九六〇年', place: '英國倫敦', language: '英文', intro: '鍾馬田於西敏寺教堂歷年講道的結集，逐節剖析馬太福音五至七章登山寶訓。全書以醫者之精準與牧者之懇切，揭示天國子民的內在生命與倫理，強調講道乃「燃燒的邏輯」。此書成為二十世紀福音派釋經講道的典範，影響英語世界講壇深遠。' },
          { title_zh: '每日研經叢書', title_orig: 'The Daily Study Bible', author: '巴克萊（William Barclay）', era: '一九五三–一九五九年', place: '英國格拉斯哥', language: '英文', intro: '巴克萊為平信徒撰寫的新約逐卷研經叢書，文字曉暢、廣納古典與文化背景，將深奧經文化為日用靈糧。全套涵蓋新約各卷，譯成多國語言、流通數千萬冊，是二十世紀普及解經最具影響力的著作之一，深刻塑造了現代信徒每日讀經的習慣。' }
        ]
      },
      {
        key: 'mass-evangelism-revival',
        label: '大型佈道與復興部',
        label_en: 'Mass Evangelism and Revival',
        desc: '城市佈道會、跨洲佈道大會與靈恩復興運動的講章與文獻。',
        works: [
          { title_zh: '慕迪佈道講章', title_orig: 'The Sermons of Dwight L. Moody', author: '慕迪（Dwight L. Moody）', era: '一八七五–一八九九年', place: '美國芝加哥', language: '英文', intro: '十九世紀末橫跨英美的城市佈道家慕迪所留下的佈道講章結集，以平實有力、訴諸悔改與恩典的信息聞名。其佈道模式與慕迪聖經學院的建立，奠定了二十世紀大型城市佈道的範式，承啟葛培理一脈的群眾佈道傳統，故收於本部之首。' },
          { title_zh: '葛培理佈道大會信息集', title_orig: 'Billy Graham Crusade Sermons', author: '葛培理（Billy Graham）', era: '一九四九–二〇〇五年', place: '美國北卡羅來納', language: '英文', intro: '二十世紀最具影響力的佈道家葛培理，自一九四九年洛杉磯帳棚佈道一舉成名後，於全球各大城市舉辦佈道大會，信息結集成冊。其講章核心始終為「聖經如此說」與決志歸主的呼召，據估親身聆聽者逾二億人。此集為現代跨洲群眾佈道的代表文獻。' },
          { title_zh: '阿蘇薩街復興記述', title_orig: 'The Azusa Street Revival Accounts', author: '西摩（William J. Seymour）等', era: '一九〇六–一九〇九年', place: '美國洛杉磯', language: '英文', intro: '一九〇六年起於洛杉磯阿蘇薩街使徒信心會的靈恩復興運動之講道與見證記述，以方言、醫治與跨種族敬拜為特徵。此復興被視為二十世紀全球五旬節運動的源頭，其佈道熱情與屬靈經驗論述深刻影響了往後遍及各洲的靈恩派宣教，故列入大型佈道與復興部。' }
        ]
      },
      {
        key: 'global-contextual-mission',
        label: '全球與處境宣教部',
        label_en: 'Global and Contextual Mission',
        desc: '普世宣教運動文獻、本色化神學與華人福音運動的宣教實踐。',
        works: [
          { title_zh: '本色化神學論集', title_orig: 'Essays on Contextual Theology', author: '宋泉盛等', era: '二十世紀後半', place: '亞洲', language: '中文‧英文', intro: '亞洲、非洲與拉美神學家探討福音如何在本土文化處境中生根的論述彙編，主張神學須回應在地的歷史、苦難與宗教經驗。此一處境化進路挑戰西方宣教的文化包袱，推動宣教由「移植」轉向「道成肉身」式的本色見證，是現代普世宣教思想的重要轉折。' },
          { title_zh: '中國福音化異象', title_orig: 'The China Evangelization Vision', author: '趙天恩', era: '一九七〇–二〇〇四年', place: '香港‧台灣', language: '中文', intro: '華人宣教學者趙天恩提出「三化異象」——中國福音化、教會國度化、文化基督化——的宣教論述與文獻彙編。其畢生致力於中國教會史研究與福音運動推展，將普世宣教關懷落實於華人處境，是二十世紀末華人本色宣教思想的代表，故收於全球與處境宣教部。' }
        ]
      }
    ]
  },
  wai: {
    summary: '外藏旁收非正統基督宗教與世俗思潮的宣講文獻，與正藏佈道傳統互為對照。',
    divisions: [
      {
        key: 'new-religious-proselytism',
        label: '新興宗教佈道部',
        label_en: 'Proselytism of New Religious Movements',
        desc: '十九世紀後興起之新興宗教的逐戶宣教與公開講座文宣。',
        works: [
          { title_zh: '逐戶傳道指南', title_orig: 'Reasoning from the Scriptures', author: '耶和華見證人守望台社', era: '一九八五年起', place: '美國紐約', language: '英文‧中文', intro: '耶和華見證人挨家挨戶傳道時所用的對話與護教手冊，按主題編排經文論據與常見質疑的應對。此宣教模式以高度組織化的逐戶探訪著稱，文宣大量翻譯流通於全球。因其基督論與正統教會相異，故列於外藏新興宗教佈道部，以供對照其宣講策略。' },
          { title_zh: '摩門教傳教士手冊', title_orig: 'Preach My Gospel', author: '耶穌基督後期聖徒教會', era: '二〇〇四年', place: '美國猶他', language: '英文‧中文', intro: '摩門教全球青年傳教士所用的標準宣教手冊，規範教導課程、邀請受洗的步驟與屬靈培育方法。其雙人結對、定期外展的傳教制度為當代新興宗教宣教之顯例。因其經典與教義逸出正統基督教範圍，故收於外藏，俾與正藏佈道文獻相互參照。' },
          { title_zh: '新世紀靈性講座文選', title_orig: 'New Age Spirituality Lectures', author: '新世紀運動諸講者', era: '二十世紀後半', place: '歐美', language: '英文', intro: '二十世紀後半興起的新世紀運動所辦各式靈性講座與工作坊之文宣與講稿選錄，融合東方冥想、神祕主義、自我提升與身心靈療癒。其宣講雖非傳統佈道，卻以類宗教方式廣傳於現代世俗社會，作為當代靈性市場的宣傳樣態收於外藏，與基督教佈道形成對照。' }
        ]
      },
      {
        key: 'secular-ethical-oratory',
        label: '世俗倫理演說部',
        label_en: 'Secular and Ethical Oratory',
        desc: '人本主義、無神論與世俗倫理的公共演說與宣言。',
        works: [
          { title_zh: '人本主義宣言', title_orig: 'Humanist Manifesto', author: '美國人本主義者協會', era: '一九三三‧一九七三‧二〇〇三年', place: '美國', language: '英文', intro: '由科學家、哲學家與倫理學者聯名發表並歷經三度修訂的世俗人本主義綱領性文件，主張以理性、科學與人類福祉取代超自然信仰為價值根基。此宣言以近乎信條的形式宣講無神論的倫理願景，是現代世俗思潮的代表文本，故收於外藏世俗倫理演說部以資對照。' },
          { title_zh: '無神論公共演說集', title_orig: 'Lectures on Atheism', author: '英格索爾（Robert G. Ingersoll）等', era: '十九世紀末–二十世紀', place: '美國', language: '英文', intro: '「偉大的不可知論者」英格索爾及其後繼者於公開講壇所發表的反宗教演說結集，以雄辯文采抨擊教條、倡導理性與世俗道德。此類演說以講壇之姿與基督教佈道針鋒相對，構成現代信仰與世俗論辯的重要一翼，作為對照樣本收於外藏。' }
        ]
      }
    ]
  }
},
    {
  key: 'leishu',
  name: '類書藏',
  name_en: 'Canon of Reference and Religious Studies',
  glyph: '類',
  genres: '神學辭典‧百科‧宗教研究',
  summary: '收錄一九〇〇年以降基督宗教與宗教研究的辭典、百科、工具書與科際整合著作。正藏循「神學辭典百科‧宗教研究科際整合‧工具書文獻彙編」三部，匯聚現代基督教的知識整理與學術自省；外藏則旁收世俗宗教學、心理分析與祕學百科，呈現現代學界與另類傳統對「宗教」此一範疇的不同建構，與正藏互為參照。',
  zheng: {
    summary: '正藏三部，依「辭典百科—研究整合—工具彙編」的現代知識體系編次。',
    divisions: [
          {
            key: 'r-reference', label: '神學百科與辭書部', label_en: 'Encyclopedias and Dictionaries',
            works: [
              { title_zh: '基督教神學百科全書（神學實用百科）', title_orig: 'Theologische Realenzyklopädie (TRE)', author: 'Gerhard Krause、Gerhard Müller 等主編', era: '1977–2007 年（正文 1977–2004，索引卷至 2006/2007；柏林）', place: '德國柏林', language: '德文', extent: '36 卷＋索引', intro: '二十世紀最重要的普世性神學百科之一，由 Walter de Gruyter（柏林）出版，全 36 卷另加索引（Gesamtregister）卷，收約二千篇長篇學術專文，逾二萬八千頁。以歷史—批判方法處理聖經、教義、教會史、各宗派與宗教學主題，跨宗派、國際取向，由十四位主編及橫跨數代的學者群執筆。為現代神學研究的標竿級工具書，常與《宗教的歷史與現況》(RGG) 並列德語神學雙璧。' },
              { title_zh: '宗教的歷史與現況（第四版）', title_orig: 'Religion in Geschichte und Gegenwart, 4. Auflage (RGG⁴)', author: 'Hans Dieter Betz、Don S. Browning、Bernd Janowski、Eberhard Jüngel 主編', era: '1998–2007 年（圖賓根）', place: '德國圖賓根', language: '德文', extent: '9 卷', intro: '德語世界最具權威的新教神學與宗教學百科之一，由 Mohr Siebeck 出版，第四版全九卷（含索引卷），收一萬五千餘條目與子條目，撰稿者近四千人，來自七十四國。內容涵蓋聖經研究、教義學、教會史、倫理、宗教社會學與世界宗教，跨學科、國際化，後另有英譯本《Religion Past and Present》。為現代宗教研究不可或缺的核心工具書。' },
              { title_zh: '天主教神學與教會辭典（第三版）', title_orig: 'Lexikon für Theologie und Kirche, 3. Auflage (LThK³)', author: 'Walter Kasper 等主編', era: '1993–2001 年（弗萊堡）', place: '德國弗萊堡', language: '德文', extent: '11 卷', intro: '天主教界最具代表性的德語神學辭典，由 Herder 出版，第三版全十卷加索引與梵二文獻補卷。承續一八四七年初版傳統，廣納教義、教會法、禮儀、靈修、教父學與宗教學條目，反映梵二後天主教神學的更新。撰述嚴謹、書目詳備，與新教的 TRE、RGG 並列為德語三大神學百科，廣為天主教學界引用。' },
              { title_zh: '新天主教百科全書（第二版）', title_orig: 'New Catholic Encyclopedia, 2nd Edition', author: 'Thomas Carson、Joann Cerrito 等主編；美國天主教大學', era: '2003 年（華盛頓）', place: '美國華盛頓特區', language: '英文', extent: '15 卷', intro: '英語世界天主教研究的標準大型百科，由美國天主教大學與 Gale（Thomson/Gale）合作出版，第二版全十五卷（十四卷正文＋第十五卷累計索引），收約一萬二千篇條目，各附以原典為主的書目。涵蓋教義、教會史、聖人、禮儀、教會法、神學家與當代議題，反映梵二後天主教學術。與舊版《天主教百科全書》（一九〇七—一九一四）區別明顯，為現代天主教神學與歷史查考的首選工具書。' },
              { title_zh: '牛津基督教會辭典', title_orig: 'The Oxford Dictionary of the Christian Church (ODCC)', author: 'F. L. Cross 初編；E. A. Livingstone 修訂', era: '1957 初版；1997 第三版（牛津）', place: '英國牛津', language: '英文', extent: '單卷', intro: '英語世界最便利權威的單卷基督教辭典，牛津大學出版社出版，克羅斯一九五七年初創，李文斯通數度修訂至第三版。收逾六千條目，涵蓋人物、教義、宗派、禮儀、聖經與教會史，條目精簡而附扼要書目。跨宗派、學術中立，為神職、學者與學生案頭必備的速查工具，被譽為基督宗教領域最實用的單冊參考書。' },
              { title_zh: '宗教百科全書（伊利亞德主編）', title_orig: 'The Encyclopedia of Religion', author: 'Mircea Eliade 主編（Lindsay Jones 第二版主編）', era: '1987 初版；2005 第二版（紐約）', place: '美國紐約', language: '英文', extent: '15 卷（第二版）', intro: '現代宗教學最重要的英語百科，由芝加哥學派宗教史家伊利亞德主持初版（一九八七，十六卷），二〇〇五年瓊斯主編增訂第二版（十五卷）。以比較宗教與宗教現象學視角，收錄各大宗教傳統、神話、儀式、人物與理論方法條目，撰稿者為各領域權威。雖非基督教專屬，卻是基督宗教置於世界宗教脈絡中研究的核心工具書。' },
              { title_zh: '安克爾聖經辭典', title_orig: 'The Anchor Bible Dictionary (ABD)', author: 'David Noel Freedman 主編', era: '1992 年（紐約）', place: '美國紐約', language: '英文', extent: '6 卷', intro: '英語聖經學界最具規模的學術辭典之一，Doubleday 出版，弗里德曼主編，全六卷收逾六千篇條目。涵蓋聖經人物、地名、書卷、神學主題、考古與古代近東背景，撰稿者逾八百位國際學者，採歷史—批判取向並附詳盡書目。為二十世紀末聖經研究的標誌性工具書，廣泛用於釋經、講道與學術研究。' },
              { title_zh: '靈修學辭典', title_orig: 'Dictionnaire de spiritualité ascétique et mystique', author: 'Marcel Viller 等創編；耶穌會', era: '1932–1995 年（巴黎）', place: '法國巴黎', language: '法文', extent: '17 卷（21 冊）', intro: '耶穌會主持、Beauchesne 出版的基督教靈修學權威辭典，構想始於 1928 年，一九三二至一九九五年陸續出齊，共 17 卷（分冊裝訂為 21 冊）。專收靈修、苦修與神祕神學的人物、流派、主題與術語，逾 6,500 個條目，深入且書目詳盡，涵蓋從教父到近代的靈修傳統。為靈修神學與默觀傳統研究的標準工具書，補一般神學百科之不足，學界引用極廣。' },
              { title_zh: '舊約神學辭典', title_orig: 'Theologisches Wörterbuch zum Alten Testament (TWAT / TDOT)', author: 'G. Johannes Botterweck、Helmer Ringgren、Heinz-Josef Fabry（自第 4 卷起）主編', era: '1970–2001 年（德文版，斯圖加特）；英譯 TDOT 1974–2018', place: '德國斯圖加特', language: '德文（另有英譯 TDOT）', extent: '德文版 10 卷（8 卷希伯來文＋1 卷亞蘭文＋1 卷索引）；英譯 TDOT 共 17 卷', intro: '舊約神學詞彙研究的標竿辭典，Kohlhammer 出版，博特威克、林格倫與法布里（自第 4 卷起）主編，德文原版共 10 卷（含亞蘭文卷與索引卷），與新約的《新約神學辭典》（Kittel TWNT）相對應。逐一深究希伯來文與亞蘭文神學語彙的字源、用法與神學意涵，旁及古代近東語言比較，附詳盡書目。英譯本 TDOT 由 Eerdmans 出版（共 17 卷），為舊約釋經與聖經神學研究不可或缺的詞彙學工具書。' },
              { title_zh: '聖經希伯來文與亞蘭文辭典（科勒—鮑姆加特納）', title_orig: 'The Hebrew and Aramaic Lexicon of the Old Testament (HALOT / HALAT)', author: 'Ludwig Koehler、Walter Baumgartner 等', era: '1967–1996 德文版；1994–2000 英譯（萊頓）', place: '瑞士／荷蘭萊頓', language: '德文／英文（釋義古希伯來文與亞蘭文）', extent: '5 冊（英譯）', intro: '現代聖經希伯來文與亞蘭文研究的標準學術辭典，科勒與鮑姆加特納編，第三版德文本一九六七至一九九六年出齊，英譯 HALOT 由 Brill 出版。釋義精確、廣納語源與古代近東語言比較及書目，取代舊有的 BDB 與 Gesenius，成為當代希伯來聖經詞彙考訂的首選工具書，學界釋經與翻譯廣泛倚重。' },
              { title_zh: '新約希臘文詞典（巴爾—丹克 BDAG）', title_orig: 'A Greek-English Lexicon of the New Testament and Other Early Christian Literature (BDAG), 3rd ed.', author: 'Walter Bauer 原著；Frederick W. Danker 第三版修訂', era: '2000 年第三版（芝加哥）', place: '美國芝加哥', language: '英文（釋義新約希臘文）', extent: '單卷', intro: '新約希臘文研究的權威詞典，源自鮑爾的德文《新約詞典》，丹克修訂的第三版（BDAG）由芝加哥大學出版社二〇〇〇年問世。釋義涵蓋新約與早期基督教文獻的希臘語詞彙，廣引古典與紙草文獻佐證，定義精準、書證詳備。為新約釋經、翻譯與希臘文研究最具公信力的案頭詞典，學界與神學院普遍採用。' },
            ],
          },

      {
        key: 'theological-dictionaries-encyclopedias',
        label: '神學辭典與百科部',
        label_en: 'Theological Dictionaries and Encyclopedias',
        desc: '系統性的神學辭典與宗教百科，現代聖經與神學研究的基礎工具。',
        works: [
          { title_zh: '新約神學辭典', title_orig: 'Theologisches Wörterbuch zum Neuen Testament', author: '基特爾（Gerhard Kittel）、弗里德里希（Gerhard Friedrich）主編', era: '一九三三–一九七九年', place: '德國斯圖加特', language: '德文', intro: '簡稱 TDNT，按希臘文神學詞彙逐條考釋其在七十士譯本、古典文獻與新約中的意涵，集眾多德語聖經學者之力歷時數十年完成，共十巨冊。此書為二十世紀新約字義研究的權威工具，英譯本流通全球神學院,雖其「詞彙神學」方法後遭巴爾批評,仍為現代聖經辭典的里程碑。' },
          { title_zh: '天主教百科全書', title_orig: 'The Catholic Encyclopedia', author: '赫伯曼（Charles Herbermann）等主編', era: '一九〇七–一九一四年', place: '美國紐約', language: '英文', intro: '二十世紀初由美國天主教學者編纂的十五卷大型百科,涵蓋教義、教會史、禮儀、聖徒、教會法與宗教文化各領域,條目詳實、引證豐富。雖立場明確、部分內容已隨梵二更新,其廣度與學術性使其長期為英語世界查考天主教知識的標準參考,故列神學辭典與百科部。' },
          { title_zh: '新國際聖經神學辭典', title_orig: 'New International Dictionary of New Testament Theology', author: '布朗（Colin Brown）主編', era: '一九七五–一九七八年', place: '英國', language: '英文', intro: '以新約神學概念為綱、按英文主題詞統攝相關希臘文詞群的綜合辭典,源自德文《神學概念辭典》並大幅增訂英語資料。全書兼顧字義考據與神學綜述,較 TDNT 更便於主題式查考,成為福音派聖經研究的重要案頭工具,廣為神學院採用。' }
        ,
          { title_zh: '基督教神學百科全書', title_orig: 'Encyclopedia of Christian Theology', author: '拉科斯特（Jean-Yves Lacoste）主編', era: '2005（法文原版 1998）', place: '美國紐約（Routledge）', language: '英文', intro: '法國現象學哲學家暨神學家拉科斯特主編，原以法文《批判神學辭典》由法國大學出版社（PUF）出版（1998 年初版），2005 年英譯擴編，由 Routledge 出版三冊套書。條目逾五百三十篇，逾二百五十位學者出自十五國撰稿，涵蓋系統神學、歷史神學、聖經詮釋、禮儀與靈修等核心範疇，廣納天主教、新教、東正教及普世合一運動視角，是當代最具份量的跨宗派基督教神學參考工具書之一。', extent: '三冊（逾 530 條目）' }
        ]
      },
      {
        key: 'religious-studies-interdisciplinary',
        label: '宗教研究與科際整合部',
        label_en: 'Religious Studies and Interdisciplinary Integration',
        desc: '宗教現象學、宗教社會學與科學神學對話的奠基與整合著作。',
        works: [
          { title_zh: '論神聖', title_orig: 'Das Heilige', author: '奧托（Rudolf Otto）', era: '一九一七年', place: '德國', language: '德文', intro: '奧托宗教現象學的奠基之作,提出「神聖者」(numinous)概念,將宗教經驗的核心界定為令人既敬畏戰慄又神往的「全然他者」。此書以非理性、不可化約的進路詮釋宗教感受,深刻影響伊利亞德與整個二十世紀宗教學,是現代研究宗教經驗最具開創性的著作之一,故收於本部之首。' },
          { title_zh: '聖與俗', title_orig: 'Le Sacré et le Profane', author: '伊利亞德（Mircea Eliade）', era: '一九五七年', place: '法國‧美國', language: '德文‧法文', intro: '宗教史家伊利亞德的代表作,系統闡述「神聖空間」與「神聖時間」如何在宗教人的世界中與凡俗對立並彰顯意義,廣引各文化的神話、儀式與象徵。此書奠定比較宗教學的現象學典範,使「神聖的顯現」(hierophany)成為宗教研究的核心範疇,影響跨學科極為深遠。' },
          { title_zh: '新教倫理與資本主義精神', title_orig: 'Die protestantische Ethik und der Geist des Kapitalismus', author: '韋伯（Max Weber）', era: '一九〇四–一九〇五年', place: '德國', language: '德文', intro: '社會學古典名著,論證喀爾文宗的天職觀與禁慾倫理如何在無意間培育出近代資本主義的理性化精神。韋伯以「理念型」方法將宗教信念與經濟行為相連,開創宗教社會學的核心議題,雖其因果論點後世爭辯不休,仍是科際整合研究宗教與社會關係的奠基文本。' },
          { title_zh: '科學與神學導論', title_orig: 'Science and Theology: An Introduction', author: '麥格拉思（Alister McGrath）', era: '一九九八年', place: '英國牛津', language: '英文', intro: '兼具分子生物學與神學訓練的麥格拉思,系統梳理科學與基督教神學自近代以來的互動史與方法論,主張二者並非衝突而可建設性對話。此書與物理學家神學家波金霍恩(John Polkinghorne)的著作並為當代科學與宗教對話的代表,展現現代神學向自然科學開放的科際整合努力。' }
        ]
      },
      {
        key: 'reference-works-compilations',
        label: '工具書與文獻彙編部',
        label_en: 'Reference Works and Source Compilations',
        desc: '經文彙編、教父原典現代叢刊與神學書目等查考工具。',
        works: [
          { title_zh: '聖經彙編', title_orig: 'Strong\'s Exhaustive Concordance of the Bible', author: '史特朗（James Strong）', era: '一八九〇年', place: '美國', language: '英文', intro: '史特朗主編的欽定本聖經全字彙編,將每個英文字逐一索引至經文,並附希伯來文與希臘文原文編號(史特朗編號),使不諳原文者亦能查考字義。此書於二十世紀廣為流通並數位化,成為英語聖經研究最普及的查經工具,其原文編號系統至今仍為各類聖經軟體沿用。' },
          { title_zh: '尼西亞前後教父集', title_orig: 'Ante-Nicene and Nicene and Post-Nicene Fathers', author: '沙夫（Philip Schaff）等編', era: '一八八五–一九〇〇年', place: '美國', language: '英文', intro: '沙夫主編的英譯教父原典大型叢刊,含尼西亞前教父十卷與尼西亞後教父兩系各十四卷,將希臘、拉丁教父著作系統英譯並加註。此叢刊與法國《基督教資料叢書》(SC)、《基督教拉丁文獻全集》(CCSL)同為現代研究教父學不可或缺的文獻彙編,流通逾百年仍為英語世界基準。' },
          { title_zh: '現代神學書目大全', title_orig: 'A Bibliography of Modern Theology', author: '各神學圖書館協會編', era: '二十世紀', place: '歐美', language: '英文‧德文', intro: '彙集現代神學各學科重要著作與期刊論文的分類書目工具,按聖經研究、歷史神學、系統神學、實踐神學等領域編排,並隨學術發展持續增補。此類書目為研究者掌握文獻、進行學術回顧的基礎工具,反映現代神學知識生產的規模與分工,故收於工具書與文獻彙編部。' }
        ,
          { title_zh: '神學實踐入門（第五卷：實踐）', title_orig: 'Initiation à la pratique de la théologie, vol. 5: Pratique', author: 'Bernard Lauret、François Refoulé 主編（集體撰著）', era: '1987', place: '法國巴黎', language: '法文', intro: '法國學者集體撰著之多卷本《神學實踐入門》第五卷，主題為「實踐」（Pratique），涵蓋實踐神學各領域，包括禮儀、牧養、宣教與基督徒倫理實踐等。全系列為法語天主教神學界二十世紀重要參考工具書，系統導引神學研究方法與各分支學科，供神學院教學與自學使用。本卷聚焦神學如何落實於教會生活與社會行動，具百科式導引性質。' }
        ]
      }
    ]
  },
  wai: {
    summary: '外藏旁收世俗與祕學傳統對宗教的研究與建構,與正藏神學工具書互為對照。',
    divisions: [
      {
        key: 'secular-religious-studies',
        label: '世俗宗教研究部',
        label_en: 'Secular Study of Religion',
        desc: '人類學與精神分析對宗教起源與功能的世俗化研究。',
        works: [
          { title_zh: '金枝', title_orig: 'The Golden Bough', author: '弗雷澤（James George Frazer）', era: '一八九〇–一九一五年', place: '英國', language: '英文', intro: '人類學家弗雷澤比較研究全球巫術、神話與宗教的鉅著,提出人類心智由巫術經宗教進化至科學的演化圖式,廣徵各民族「殺王」「植物神死而復生」等母題。此書雖其進化論架構與資料運用後遭學界批評,卻深刻影響現代宗教學、文學與心理學,是世俗化研究宗教的經典,故收於外藏。' },
          { title_zh: '圖騰與禁忌', title_orig: 'Totem und Tabu', author: '佛洛伊德（Sigmund Freud）', era: '一九一三年', place: '奧地利維也納', language: '德文', intro: '佛洛伊德以精神分析解釋宗教起源的著作,藉「原始部落弒父」的假說將圖騰崇拜、禁忌與伊底帕斯情結相連,主張宗教源於潛意識的罪疚與願望投射。此書將宗教化約為心理機制,雖其人類學根據薄弱,卻開啟以精神分析詮釋宗教的傳統,故與其晚年另一著作並收於外藏。' },
          { title_zh: '摩西與一神教', title_orig: 'Der Mann Moses und die monotheistische Religion', author: '佛洛伊德（Sigmund Freud）', era: '一九三九年', place: '奧地利‧英國', language: '德文', intro: '佛洛伊德晚年最後一部大著,大膽推論摩西原為埃及人、猶太一神教源自被壓抑的弒父記憶與後續的回返。此書以精神分析重構宗教史,論點高度爭議且史據薄弱,卻是佛洛伊德宗教觀的總結之作,展現精神分析對一神信仰的世俗化解讀,故收於外藏世俗宗教研究部。' },
          { title_zh: '心理學與宗教', title_orig: 'Psychology and Religion', author: '榮格（Carl Gustav Jung）', era: '一九三八年', place: '瑞士', language: '英文‧德文', intro: '榮格分析心理學探討宗教經驗的代表論述,主張宗教象徵為集體潛意識中原型的自發顯現,對個體的心理整全具不可或缺的功能。有別於佛洛伊德的化約,榮格賦予宗教正面的心理價值,其對曼荼羅、自性與神聖象徵的研究深刻影響後世宗教心理學與靈性論述,故收於外藏。' }
        ]
      },
      {
        key: 'new-age-occult-encyclopedia',
        label: '新世紀與祕學百科部',
        label_en: 'New Age and Occult Encyclopedia',
        desc: '神智學與祕學傳統的綜攝性百科與教義體系。',
        works: [
          { title_zh: '祕密教義', title_orig: 'The Secret Doctrine', author: '布拉瓦茨基（Helena Petrovna Blavatsky）', era: '一八八八年', place: '英國倫敦', language: '英文', intro: '神智學會創始人布拉瓦茨基的核心鉅著,自稱據古老《姜言之書》闡釋宇宙演化(宇宙起源論)與人類根族演化(人類起源論),綜攝印度教、佛教、卡巴拉與西方祕學於一爐。此書為現代神智學與新世紀運動的教義根基,以百科式的綜合自成體系,雖其來源備受質疑,影響另類靈性傳統甚鉅,故收於外藏。' },
          { title_zh: '揭開伊西斯的面紗', title_orig: 'Isis Unveiled', author: '布拉瓦茨基（Helena Petrovna Blavatsky）', era: '一八七七年', place: '美國紐約', language: '英文', intro: '布拉瓦茨基的早期鉅著,廣引古代宗教、神話、煉金術與祕學文獻,批判當時的物質主義科學與教條神學,主張存在一貫穿諸文明的「古老智慧宗教」。此書以龐雜的百科體例奠定神智學的思想基礎,是十九世紀末祕學復興的代表文本,作為新世紀祕學傳統的源頭文獻收於外藏。' }
        ]
      }
    ]
  }
}
  ],
}
