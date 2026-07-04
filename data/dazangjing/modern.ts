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
          { title_zh: '天主教教理', title_orig: 'Catechismus Catholicae Ecclesiae (CCC)', author: '教宗若望保祿二世頒布（拉辛格樞機主編委會）', era: '1992／拉丁文定本 1997', place: '羅馬梵蒂岡', language: '拉丁文（原）／繁體中文、英文（譯）', intro: '天主教教理由教宗若望保祿二世於一九九二年頒布，編纂委員會由拉辛格樞機（後為教宗本篤十六世）主持，是繼特倫多教理後天主教首部全面的官方教理。全書依信經、聖事、誡命、祈禱四大部分組織，系統陳述天主教的信仰、禮儀、道德與祈禱生活，並大量徵引聖經、教父與梵二文獻。此教理為當代天主教信仰教導提供權威基準，廣被各地教會作為教學與要理講授的依據。' },
          { title_zh: '教會憲章', title_orig: 'Lumen Gentium', author: '梵蒂岡第二屆大公會議', era: '1964', place: '羅馬', language: '拉丁文', parent: '梵蒂岡第二屆大公會議', intro: '梵二的教會學核心憲章，以「天主子民」重述教會自我理解，恢復主教團體性並宣認平信徒的普遍司祭職。「教會是普世救恩聖事」的定義扭轉數百年的社會完備論，二十世紀天主教最重要的一份文件。' },
          { title_zh: '天主的啟示教義憲章', title_orig: 'Dei Verbum', author: '梵蒂岡第二屆大公會議', era: '1965', place: '羅馬', language: '拉丁文', parent: '梵蒂岡第二屆大公會議', intro: '梵二論啟示與聖經的教義憲章，以「天主親自說話」的位格性啟示觀取代命題式默示論，鼓勵信友親近聖經。聖經運動、禮儀讀經改革與天主教釋經學的復興皆奠基於此，與《教會憲章》並列梵二雙柱。' },
          { title_zh: '論教會在現代世界牧職憲章', title_orig: 'Gaudium et Spes', author: '梵蒂岡第二屆大公會議', era: '1965', place: '羅馬', language: '拉丁文', parent: '梵蒂岡第二屆大公會議', intro: '開篇「人類的喜樂與希望……也是基督徒的喜樂與希望」，梵二以此憲章面向全人類議題：文化、經濟、政治、戰爭與家庭。教會由防禦轉向對話的大憲章，梵二精神最常被徵引的文本。' },
          { title_zh: '信仰自由宣言', title_orig: 'Dignitatis Humanae', author: '梵蒂岡第二屆大公會議', era: '1965', place: '羅馬', language: '拉丁文', parent: '梵蒂岡第二屆大公會議', intro: '宣認宗教自由植根於人性尊嚴、任何人不得被迫違背良心行事，正式告別「錯誤沒有權利」的舊說。美國神學家莫瑞為其主要起草者，此宣言逆轉十九世紀諸通諭立場，梵二最具戲劇性的教義發展。' },
          { title_zh: '教會對非基督宗教態度宣言', title_orig: 'Nostra Aetate', author: '梵蒂岡第二屆大公會議', era: '1965', place: '羅馬', language: '拉丁文', parent: '梵蒂岡第二屆大公會議', intro: '以短短五節重定教會與猶太教、伊斯蘭、印度教佛教的關係，鄭重否認猶太民族的「弒神」集體罪責。大屠殺後天主教自我反省的結晶，開啟半世紀的宗教對話，梵二篇幅最小而迴響最大的文件。' },
          { title_zh: '天主教教育宣言', title_orig: 'Gravissimum Educationis', author: '梵蒂岡第二屆大公會議', era: '1965', place: '羅馬', language: '拉丁文', parent: '梵蒂岡第二屆大公會議', intro: '梵二論教育的宣言，申明父母為子女教育的首要責任者，並界定天主教學校在多元社會中的使命。全球最大的私立教育網絡由此獲得現代化的憲章基礎。' },
          { title_zh: '東方公教會法令', title_orig: 'Orientalium Ecclesiarum', author: '梵蒂岡第二屆大公會議', era: '1964', place: '羅馬', language: '拉丁文', parent: '梵蒂岡第二屆大公會議', intro: '梵二論東方禮天主教會的法令，宣認東西方傳統平等尊嚴，令東方教會恢復固有禮儀與法統。它終結拉丁化政策的法理依據，亦為與正教會修好預備了制度語言。' },
          { title_zh: '主教牧職法令', title_orig: 'Christus Dominus', author: '梵蒂岡第二屆大公會議', era: '1965', place: '羅馬', language: '拉丁文', parent: '梵蒂岡第二屆大公會議', intro: '梵二論主教職務的法令，落實主教團體性於教區治理與主教團建制，全球各國主教團的法定地位由此確立。教會治理由中央集權向地方協同調整的制度文件。' },
          { title_zh: '司鐸職務與生活法令', title_orig: 'Presbyterorum Ordinis', author: '梵蒂岡第二屆大公會議', era: '1965', place: '羅馬', language: '拉丁文', parent: '梵蒂岡第二屆大公會議', intro: '梵二論司鐸的法令，以宣講聖言、聖事服務與牧養共融三職重述鐸職，並論司鐸靈修與獨身。後梵二司鐸身分的討論與危機，皆以此文本為座標。' },
          { title_zh: '司鐸之培養法令', title_orig: 'Optatam Totius', author: '梵蒂岡第二屆大公會議', era: '1965', place: '羅馬', language: '拉丁文', parent: '梵蒂岡第二屆大公會議', intro: '梵二修院改革法令，令培育計畫由各國主教團因地制宜，靈修、學術與牧民訓練並重，聖多瑪斯為師而向現代學術開放。全球修院課程的現代轉型自此啟動。' },
          { title_zh: '修會生活革新法令', title_orig: 'Perfectae Caritatis', author: '梵蒂岡第二屆大公會議', era: '1965', place: '羅馬', language: '拉丁文', parent: '梵蒂岡第二屆大公會議', intro: '梵二令各修會「雙重回歸」：回歸福音與會祖神恩，並適應時代需要而革新。其後數十年修會憲章全面重寫、會服會規丕變，本法令是當代修道生活重構的引信。' },
          { title_zh: '教友傳教法令', title_orig: 'Apostolicam Actuositatem', author: '梵蒂岡第二屆大公會議', era: '1965', place: '羅馬', language: '拉丁文', parent: '梵蒂岡第二屆大公會議', intro: '梵二論平信徒使徒工作的法令，宣認平信徒憑聖洗直接領受使命、非僅聖統的延伸。堂區議會、平信徒運動與職場福傳的神學基礎皆在於此，「平信徒的世紀」的官方開幕詞。' },
          { title_zh: '教會傳教工作法令', title_orig: 'Ad Gentes', author: '梵蒂岡第二屆大公會議', era: '1965', place: '羅馬', language: '拉丁文', parent: '梵蒂岡第二屆大公會議', intro: '梵二宣教法令，以「教會本質上是傳教的」定調，宣教植根於三一天主的派遣。本地教會養成與文化交談取代殖民時代模式，當代天主教宣教學的憲章。' },
          { title_zh: '大眾傳播工具法令', title_orig: 'Inter Mirifica', author: '梵蒂岡第二屆大公會議', era: '1963', place: '羅馬', language: '拉丁文', parent: '梵蒂岡第二屆大公會議', intro: '梵二最早通過的文件之一，論報刊、電影、廣播電視的福傳運用與倫理責任，並設立世界傳播日。雖被評為梵二最單薄的文件，卻是教會正面迎向媒體時代的第一份大公文本。' },
          { title_zh: '一九一七年天主教法典', title_orig: 'Codex Iuris Canonici (1917)', author: '聖座（本篤十五世頒布，甘斯帕裡主編）', era: '1917', place: '羅馬', language: '拉丁文', intro: '教會史上第一部現代法典化的教會法，甘斯帕裡樞機把千年教令彙編為兩千四百餘條，庇護十世發起、本篤十五世頒行。它以拿破崙法典式的體例重塑教會治理，行用至一九八三年新法典取代。' },
          { title_zh: '教會社會訓導彙編', title_orig: 'Compendium of the Social Doctrine of the Church', author: '宗座正義與和平委員會', era: '2004', place: '羅馬', language: '義大利文／拉丁文', intro: '教廷把自《新事》以降百餘年社會訓導系統彙編為一冊：人性尊嚴、公共福祉、輔助原則與優先關懷窮人四大支柱。天主教社會思想的官方總目錄，社會倫理教學的標準參考。' },
          { title_zh: '教會內的聖經詮釋', title_orig: 'L\'interprétation de la Bible dans l\'Église', author: '宗座聖經委員會', era: '1993', place: '羅馬', language: '法文', intro: '紀念《上智天主》百年的官方文件，肯定歷史批判法為「不可或缺」，同時評估各新興詮釋進路並戒基要主義讀經。天主教聖經學術百年和解的總結文件，釋經方法論的權威指南。' },
          { title_zh: '世界正義文件', title_orig: 'Iustitia in Mundo', author: '一九七一年世界主教會議', era: '1971', place: '羅馬', language: '拉丁文', intro: '世界主教會議宣告「為正義而行動是宣講福音的構成性幅度」，把社會正義自福傳的附屬提升為本質。拉美解放脈動進入普世訓導的關鍵文件，其名句至今為社會宣講的座右銘。' },
          { title_zh: '拉特朗條約', title_orig: 'Patti Lateranensi', author: '聖座與義大利王國', era: '1929', place: '羅馬拉特朗宮', language: '義大利文', intro: '聖座與義大利簽署的條約，結束一八七〇年以來的「羅馬問題」，創設梵蒂岡城國並確立政教協定體制。教宗由「梵蒂岡之囚」重返國際法主體，現代政教關係史的分水嶺文件。' },
          { title_zh: '帝國政教協定', title_orig: 'Reichskonkordat', author: '聖座與德意志帝國', era: '1933', place: '羅馬', language: '德文／義大利文', intro: '教廷與甫掌權的納粹政權締結的協定，以保障教會權益換取政治退場，旋遭納粹系統性違約。其功過至今聚訟——是護教的無奈還是為虎作倀的背書，二十世紀政教倫理的最大爭議文件。' },
          { title_zh: '梵蒂岡與以色列基本協定', title_orig: 'Fundamental Agreement between the Holy See and the State of Israel', author: '聖座與以色列國', era: '1993', place: '耶路撒冷', language: '英文', intro: '《我們的時代》宣言結出的外交果實：聖座與以色列建交的基本協定，確立教會在聖地的法律地位。天主教與猶太民族兩千年糾葛走入正常化的里程碑文件。' },
          { title_zh: '中梵主教任命臨時協議', title_orig: 'Accordo Provvisorio circa la nomina dei Vescovi', author: '聖座與中華人民共和國', era: '2018（歷次續簽）', place: '北京', language: '中文／義大利文', intro: '聖座與北京就主教任命達成的臨時協議，結束數十年「地上地下」雙軌任命的分裂狀態，條文至今未公開而爭論不休。中國天主教會處境的當代關鍵文件，政教談判倫理的活案例。' }
        
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
          { title_zh: '教會：邁向共同願景', title_orig: 'The Church: Towards a Common Vision', author: '世界基督教協進會信仰與教制委員會', era: '2013', place: '瑞士日內瓦', language: '英文（原）／繁體中文（譯）', intro: '《教會：邁向共同願景》由世界基督教協進會信仰與教制委員會於二〇一三年發表，是繼一九八二年《利馬文件》之後又一份里程碑式的合一文獻。文件首度嘗試就「教會的本質與使命」這一更根本的議題凝聚跨宗派共識，闡述教會作為三一上帝共融標記的神學，並坦陳各傳統在聖統、權威與倫理判斷上仍存的分歧。它代表普世合一運動從聖禮共識邁向教會論共識的新階段，是當代合一神學的重要參照。' },
          { title_zh: '耶路撒冷國際宣教大會報告', title_orig: 'Report of the Jerusalem Meeting of the IMC', author: '國際宣教協會', era: '1928', place: '耶路撒冷橄欖山', language: '英文', intro: '愛丁堡之後首次全球宣教大會，非西方教會代表比例大增，會議以「基督是我們的信息」回應世俗主義並論宣教與社會工業問題。宣教運動由西方獨白轉向世界教會對話的轉折點。' },
          { title_zh: '坦巴拉姆國際宣教大會報告', title_orig: 'The Tambaram Madras Series', author: '國際宣教協會', era: '1938', place: '馬德拉斯坦巴拉姆', language: '英文', intro: '二戰前夕於印度舉行的宣教大會，過半代表來自「青年教會」，克雷默《非基督教世界中的基督教信息》引發連續神學與斷裂神學的世紀論戰。本土教會成年禮的文獻，宣教神學史的分水嶺。' },
          { title_zh: '威靈根宣教大會文件', title_orig: 'Willingen Conference Documents', author: '國際宣教協會', era: '1952', place: '德國威靈根', language: '英文', intro: '中國門戶關閉的震撼中，威靈根大會提出「上帝的宣教」（missio Dei）：宣教出於三一上帝的本性，教會僅是參與者。二十世紀宣教神學的哥白尼轉向，此後一切宣教文件的共同前提。' },
          { title_zh: '洛桑信仰與教制大會文件', title_orig: 'Faith and Order: Lausanne 1927', author: '信仰與教制運動第一屆世界大會', era: '1927', place: '洛桑', language: '英文', intro: '布倫特主教推動的首屆信仰與教制大會，四百位各宗代表首次同席直面教義分歧，就福音、教會與聖職發表比較報告。教義合一對話的制度起點，WCC 信仰與教制委員會的直系源頭。' },
          { title_zh: '愛丁堡信仰與教制大會文件', title_orig: 'Faith and Order: Edinburgh 1937', author: '信仰與教制運動第二屆世界大會', era: '1937', place: '愛丁堡', language: '英文', intro: '第二屆信仰與教制大會就恩典教義達成著名的共識宣言，證明分裂教會仍可共同宣認核心信仰，並決議與生活與工作運動合組世界教協。戰雲下的合一意志，WCC 誕生的直接決議文件。' },
          { title_zh: '埃文斯頓大會報告', title_orig: 'WCC Evanston Assembly Report', author: '世界基督教協進會第二屆大會', era: '1954', place: '美國埃文斯頓', language: '英文', intro: 'WCC 第二屆大會以「基督——世界的盼望」為題，冷戰高峰中辯論末世盼望與社會責任的關係。美洲首次主辦普世大會，「負責任的社會」概念由此深化，戰後合一運動的定調文件。' },
          { title_zh: '新德里基礎宣言與大會報告', title_orig: 'WCC New Delhi Report', author: '世界基督教協進會第三屆大會', era: '1961', place: '新德里', language: '英文', intro: '新德里大會修訂 WCC 三一論基礎宣言、接納國際宣教協會併入，正教會與五旬節教會同年入會。「各地凡受洗者的合一」定義成為合一願景的經典表述，普世運動全球化的成年文件。' },
          { title_zh: '烏普薩拉大會報告', title_orig: 'WCC Uppsala Assembly Report', author: '世界基督教協進會第四屆大會', era: '1968', place: '烏普薩拉', language: '英文', intro: '一九六八風暴之年的 WCC 大會，「看哪，我造萬物皆新」轉向世界的更新，催生反種族主義計畫。合一運動政治化與福音派疏離的分水嶺，其激進轉向的功過至今仍在清算。' },
          { title_zh: '溫哥華大會報告', title_orig: 'WCC Vancouver Assembly Report', author: '世界基督教協進會第六屆大會', era: '1983', place: '溫哥華', language: '英文', intro: '以「耶穌基督——世界的生命」為題的溫哥華大會確立「正義、和平與受造界的完整」進程，禮儀生活空前豐富，利馬禮文於此首演。合一運動整合靈修與公義的高潮之會。' },
          { title_zh: '坎培拉大會報告', title_orig: 'WCC Canberra Assembly Report', author: '世界基督教協進會第七屆大會', era: '1991', place: '坎培拉', language: '英文', intro: '首次以聖靈為主題的 WCC 大會，鄭玄卿召喚眾靈的開幕神學引發正教與福音派強烈抗議，處境神學與傳統界限的張力全面爆發。合一運動多元與界限之辯的標誌文件。' },
          { title_zh: '釜山大會報告', title_orig: 'WCC Busan Assembly Report', author: '世界基督教協進會第十屆大會', era: '2013', place: '釜山', language: '英文', intro: '首次在東亞舉行的 WCC 大會，以「生命的上帝，引我們走向正義與和平」為題，韓國教會的分裂與熱情同時展演會場內外。普世運動重心南移與東移的見證文件。' },
          { title_zh: '一起走向生命', title_orig: 'Together towards Life', author: 'WCC 世界宣教與傳道委員會', era: '2013', place: '日內瓦', language: '英文', intro: 'WCC 半世紀來首份新宣教宣言，以聖靈為軸提出「從邊緣出發的宣教」：邊緣者不是宣教對象而是宣教主體。後西方時代宣教神學的官方總結，與洛桑《開普敦承諾》並讀的當代雙璧。' },
          { title_zh: '波爾沃共同聲明', title_orig: 'The Porvoo Common Statement', author: '英國與愛爾蘭聖公會諸教會及北歐波羅的海路德宗教會', era: '1992', place: '芬蘭波爾沃', language: '英文', intro: '聖公宗與北歐路德宗達成的共融聲明，相互承認聖職與主教統緒，建立可互換聖職的波爾沃共融。以「使徒統緒在於整個教會的延續」化解按立爭議，區域性完全共融的典範文本。' },
          { title_zh: '洛伊恩堡協定', title_orig: 'Konkordie reformatorischer Kirchen in Europa (Leuenberger Konkordie)', author: '歐洲路德宗與改革宗教會', era: '1973', place: '巴塞爾近郊洛伊恩堡', language: '德文', intro: '歐洲路德宗與改革宗宣告四百年聖餐爭議不再構成分裂，彼此授予講壇與聖餐的完全相通。以「有分歧的共融」模式化解宗教改革內戰，今歐洲百餘教會同屬洛伊恩堡共融體。' },
          { title_zh: '東方正統與東正教基督論共同聲明', title_orig: 'Agreed Statements between the Eastern Orthodox and Oriental Orthodox Churches', author: '兩大正教傳統聯合神學委員會', era: '1989–1990', place: '埃及安巴畢碩伊修道院／日內瓦尚貝西', language: '英文', intro: '迦克墩分裂一千五百年後，兩大正教家族宣告雙方始終持守同一基督論信仰，分歧僅在術語。神學和解已成而共融尚待，本聲明是古老分裂可以癒合的最有力當代證據。' },
          { title_zh: '天主教與東方亞述教會共同基督論宣言', title_orig: 'Common Christological Declaration between the Catholic Church and the Assyrian Church of the East', author: '若望保祿二世與馬爾丁克哈四世', era: '1994', place: '羅馬', language: '英文', intro: '天主教與「聶斯多留」教會共同宣認同一道成肉身信仰，以弗所陰影下一千五百年的指控就此撤銷。隨後的聖餐互領指引更屬突破，古代教會分裂中最早癒合的一道。' },
          { title_zh: '天主教與科普特正教共同基督論宣言', title_orig: 'Common Declaration of Paul VI and Shenouda III', author: '保祿六世與謝努達三世', era: '1973', place: '羅馬', language: '英文', intro: '保祿六世與科普特教宗謝努達三世簽署的共同宣言，就基督論達成一致表述，為迦克墩後首份此類文件。開創「以共同宣認化解古代絕罰」的模式，其後諸東方對話皆循此路。' },
          { title_zh: '天主教與敘利亞正教共同聲明', title_orig: 'Common Declaration of John Paul II and Ignatius Zakka I Iwas', author: '若望保祿二世與依納爵‧撒迦一世', era: '1984', place: '羅馬', language: '英文', intro: '天主教與敘利亞正教的共同聲明不僅確認基督論一致，更允許信眾在無法接近本教會聖事時互領告解、聖體與傅油。教義和解直接轉化為聖事實踐的先例，大公對話最具體的果實之一。' },
          { title_zh: '君士坦丁堡宗主教一九二〇通牒', title_orig: 'Unto the Churches of Christ Everywhere', author: '君士坦丁堡普世宗主教區', era: '1920', place: '君士坦丁堡', language: '希臘文', intro: '普世宗主教區致「各地基督教會」的通牒，倡議仿國際聯盟成立「教會聯盟」，早於 WCC 成立近三十年。正教主動發起合一運動的先聲文件，普世運動史的東方起點。' },
          { title_zh: '塞利斯貝格十點宣言', title_orig: 'The Ten Points of Seelisberg', author: '國際基督徒猶太人會議', era: '1947', place: '瑞士塞利斯貝格', language: '英文／法文', intro: '大屠殺甫結束，基督徒與猶太學者共同訂定講道教理中根除反猶教導的十點準則：勿以「猶太人」統稱耶穌之敵、勿言弒神詛咒。戰後基督教反省反猶主義的起點文件，《我們的時代》的先驅。' },
          { title_zh: '我們記得：對大屠殺的反省', title_orig: 'We Remember: A Reflection on the Shoah', author: '宗座促進基督徒合一委員會猶太關係組', era: '1998', place: '羅馬', language: '英文', intro: '教廷正式反省大屠殺的文件，承認基督徒的反猶太教導為納粹反猶鋪路，呼籲悔改（teshuvah）。雖被評為對庇護十二世著墨迴護，仍是教會體制面對歷史共罪的里程碑文本。' },
          { title_zh: '人類兄弟情誼文件', title_orig: 'Document on Human Fraternity', author: '教宗方濟各與大伊瑪目塔耶布', era: '2019', place: '阿布達比', language: '阿拉伯文／義大利文', intro: '教宗方濟各與艾資哈爾大伊瑪目共同簽署的兄弟情誼宣言，宣認宗教多元屬於天主的智慧旨意，共斥以神之名的暴力。天主教與遜尼伊斯蘭最高層級的共同文本，通諭《眾位弟兄》的直接前奏。' },
          { title_zh: '多元世界中的基督徒見證', title_orig: 'Christian Witness in a Multi-Religious World', author: '世界教協、宗座對話委員會與世界福音派聯盟', era: '2011', place: '日內瓦／羅馬', language: '英文', intro: '普世派、天主教與福音派三方首度共同簽署的文件，為多元宗教處境中的宣教訂定倫理準則：作見證是本質，強迫與利誘改宗是背離。涵蓋全球九成基督徒的空前共識文本。' },
          { title_zh: '福音派與天主教同行宣言', title_orig: 'Evangelicals and Catholics Together', author: '寇爾森與紐豪斯等（民間聯署）', era: '1994', place: '紐約', language: '英文', intro: '美國福音派與天主教領袖民間發起的共同宣言，宣認彼此為主內弟兄、在文化議題上並肩。未經教會授權而震動雙方陣營，改革宗內部批判蜂起，草根大公主義最具爭議的文本。' },
          { title_zh: '從衝突到共融', title_orig: 'From Conflict to Communion', author: '路德宗與天主教合一委員會', era: '2013', place: '日內瓦／羅馬', language: '英文', intro: '為宗教改革五百週年預備的共同文件，首次由兩教會共同敘述宗教改革史並互認罪責，導出二〇一六年隆德共同紀念。「分裂的週年變成共同的紀念」，和解記憶學的典範文本。' },
          { title_zh: '馬尼拉宣言', title_orig: 'The Manila Manifesto', author: '第二屆洛桑世界福音會議', era: '1989', place: '馬尼拉', language: '英文', intro: '洛桑運動第二屆大會的宣言，重申《洛桑信約》並深化整全福音、萬民皆祭司與「主後兩千年福音遍傳」的呼召。福音派全球化的中期總結，「未得之民」策略時代的綱領。' },
          { title_zh: '開普敦承諾', title_orig: 'The Cape Town Commitment', author: '第三屆洛桑世界福音會議', era: '2010', place: '開普敦', language: '英文', intro: '洛桑第三屆大會以「愛的語言」重寫福音派宣教神學：為真理作見證、關懷受造界、對抗貧窮與販運。全球南方聲音主導起草，當代福音派最完整的信仰與行動綱領。' }
        
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
          { title_zh: '芝加哥聖經無誤宣言', title_orig: 'The Chicago Statement on Biblical Inerrancy', author: '國際聖經無誤協會', era: '1978', place: '美國芝加哥', language: '英文（原）／繁體中文（譯）', intro: '芝加哥聖經無誤宣言由國際聖經無誤協會於一九七八年在芝加哥發表，是逾三百位福音派學者回應現代自由派神學與高等批判的集體表態。宣言以十九條「肯定與否定」條款，系統界定「聖經無誤」（inerrancy）的內涵，主張聖經在其原稿中於一切所及之事上皆真確無誤。此文件成為當代福音派聖經觀的標準陳述，深刻影響了北美及全球保守派神學院與教會的釋經立場，亦標誌了福音派與自由派在聖經權威上的分野。', link: '/creeds' },
          { title_zh: '浸信信仰與要道', title_orig: 'The Baptist Faith and Message', author: '美南浸信會', era: '1925／1963／2000', place: '美國', language: '英文', intro: '美南浸信會的信仰聲明，歷三版而漸趨保守，二千年版於聖經無誤與牧職性別上定調，成為北美最大新教宗派的教義邊界。「不設信條的浸信會」如何運用信仰聲明的百年案例。' },
          { title_zh: '一九六七年信仰告白', title_orig: 'The Confession of 1967', author: '美國聯合長老教會', era: '1967', place: '美國', language: '英文', intro: '美國長老教會以「和好」為軸的新告白，直面種族、貧窮、戰爭與兩性議題，並把西敏傳統納入「信仰告白書」的歷史系列。改革宗「告白須隨代更新」原則的當代實踐，通過時全美矚目。' },
          { title_zh: '斯圖加特悔罪宣言', title_orig: 'Stuttgarter Schuldbekenntnis', author: '德國福音教會領袖團', era: '1945', place: '斯圖加特', language: '德文', intro: '戰敗數月後，尼莫拉等德國教會領袖向普世代表宣認「我們控訴自己未更勇敢地作見證」。未提納粹一詞而承擔共罪，其自省為德國教會重返普世團契開路，戰後悔罪文獻的原型。' },
          { title_zh: '貝爾哈信條', title_orig: 'The Belhar Confession', author: '荷蘭歸正宣道會（南非）', era: '1982–1986', place: '開普敦貝爾哈', language: '南非語／英文', intro: '有色人種歸正教會針對種族隔離神學提出的信條：合一、和好與公義是福音本身，種族分隔的教會論即異端。首份出自全球南方而被北方教會接納的信條，改革宗信條史的當代新頁。' },
          { title_zh: '凱羅斯文件', title_orig: 'The Kairos Document', author: '南非黑人區神學家群（索韋託圈）', era: '1985', place: '約翰尼斯堡', language: '英文', intro: '緊急狀態中的南非神學家匿名發表的時刻文件，判「國家神學」為偶像崇拜、「教會神學」為廉價和解，召喚先知神學投入抗爭。政治神學介入的世紀範本，「凱羅斯」自此成為類型名。' },
          { title_zh: '韓國基督徒神學宣言', title_orig: '한국 그리스도인 신학적 성명 (Theological Declaration of Korean Christians)', author: '韓國基督徒匿名圈（維新體制下）', era: '1973', place: '首爾（地下發表）', language: '韓文', intro: '朴正熙維新獨裁下匿名流出的神學宣言，宣認上帝是歷史的主、教會必須為受壓者發聲，民眾神學由此萌芽。東亞政治神學的開山文件，韓國民主運動中教會角色的信仰根據。' },
          { title_zh: '臺灣基督長老教會國是聲明', title_orig: '台灣基督長老教會對國是的聲明與建議', author: '臺灣基督長老教會總會', era: '1971', place: '臺北', language: '中文', intro: '退出聯合國的風暴中，長老教會發表國是聲明，主張「臺灣的將來應由臺灣一千七百萬住民決定」。臺灣教會首度公開申論住民自決，戒嚴體制下信仰良知介入國家前途的先聲文件。' },
          { title_zh: '臺灣基督長老教會人權宣言', title_orig: '台灣基督長老教會人權宣言', author: '臺灣基督長老教會總會', era: '1977', place: '臺北', language: '中文', intro: '美中關係正常化前夕，長老教會促請政府「使臺灣成為新而獨立的國家」，教會因此承受高壓而不撤回。臺灣民主化史與教會史共同的關鍵文本，信仰告白化為政治承擔的極致案例。' },
          { title_zh: '臺灣基督長老教會信仰告白', title_orig: '台灣基督長老教會信仰告白', author: '臺灣基督長老教會總會', era: '1985', place: '臺北', language: '中文', intro: '長老教會總結宣教百廿年的信仰告白，宣認上帝使人「釘根於本地，認同所有的住民」，教會是「受苦大眾的教會」。改革宗信仰的臺灣本色化定式，三大聲明神學路線的信條化總結。' },
          { title_zh: '三自革新宣言', title_orig: '中國基督教在新中國建設中努力的途徑', author: '吳耀宗等四十人發起', era: '1950', place: '上海', language: '中文', intro: '吳耀宗等發起、數十萬信徒聯署的革新宣言，號召中國教會割斷與帝國主義的關係、實現自治自養自傳。中國基督教政教格局的奠基文件，其評價至今兩極，理解當代中國教會的第一文本。' },
          { title_zh: '中國家庭教會信仰告白', title_orig: '中國家庭教會信仰告白（1998）', author: '華北家庭教會團隊聯合（張榮亮等）', era: '1998', place: '河南', language: '中文', intro: '四大家庭教會系統領袖聯合發表的信仰告白與對政府態度聲明，申明信仰純正以別於異端、亦表明不加入三自的立場。地下教會首次公開的系統自白，中國教會生態的界碑文件。' },
          { title_zh: '日本基督教團戰爭責任告白', title_orig: '第二次大戦下における日本基督教団の責任についての告白', author: '日本基督教團（鈴木正久議長）', era: '1967', place: '東京', language: '日文', intro: '日本基督教團就戰時協力天皇制軍國主義發表的告白，承認教會「見張り」（守望）之職的失敗。亞洲教會戰責反省的先行文件，其後教團內部的路線撕裂亦由此起。' },
          { title_zh: '芝加哥社會關懷宣言', title_orig: 'The Chicago Declaration of Evangelical Social Concern', author: '福音派社會關懷工作坊（榮‧賽德等）', era: '1973', place: '芝加哥', language: '英文', intro: '五十位福音派領袖悔認福音派在種族、貧窮與性別上的沉默，呼籲社會公義為福音的當然要求。「福音派左翼」的出生證明，洛桑信約社會責任條款的美國先聲。' },
          { title_zh: '神召會基要真理聲明', title_orig: 'Statement of Fundamental Truths', author: '神召會總議會', era: '1916', place: '美國', language: '英文', intro: '神召會為劃清「唯獨耶穌」一位論爭議而訂的十六條基要真理，確立三一論與說方言為靈洗初證。全球最大五旬節宗派的教義基石，五旬節運動由復興轉入建制的標誌文件。' },
          { title_zh: '五點基要信仰宣言', title_orig: 'The Five Fundamentals (Presbyterian General Assembly)', author: '美北長老會總會', era: '1910', place: '美國', language: '英文', intro: '美北長老會總會針對自由神學列舉的五點必要教義：聖經無誤、童貞生子、代贖、肉身復活與神蹟真實。「基要派」之名由此而出，二十世紀美國新教大分裂的引信文件。' },
          { title_zh: '南印度教會合一方案', title_orig: 'The Scheme of Union of the Church of South India', author: '南印度聯合談判委員會', era: '1947', place: '馬德拉斯', language: '英文', intro: '聖公宗、衛理宗與長老公理諸會歷廿八年談判達成的合一方案，主教制與非主教制聖職首次融於一爐。教會合一由對話走入組織合併的世界第一例，其聖職過渡安排成為後續合一運動的判例。' },
          { title_zh: '北印度教會合一方案', title_orig: 'Plan of Church Union in North India', author: '北印度合一談判委員會', era: '1970', place: '那格浦爾', language: '英文', intro: '六宗派合成北印度教會的方案，浸信傳統加入使洗禮方式兼容成為新課題，與同年巴基斯坦教會同步成立。南亞合一教會家族的完成篇，後殖民教會自主整合的代表文件。' },
          { title_zh: '加拿大聯合教會合一基礎', title_orig: 'Basis of Union of the United Church of Canada', author: '衛理、長老與公理三宗聯合委員會', era: '1925', place: '多倫多', language: '英文', intro: '三宗派合組加拿大聯合教會的基礎文件，為西方世界第一個跨宗派有機合一的教會立憲。其二十條教義既守福音信仰又留神學空間，「合一先於一致」的早期實驗文本。' },
          { title_zh: '澳洲聯合教會合一基礎', title_orig: 'The Basis of Union (Uniting Church in Australia)', author: '公理、衛理與長老三宗聯合委員會', era: '1977', place: '雪梨', language: '英文', intro: '澳洲三宗合一的神學基礎文件，罕見地以基督論與宣教使命為軸而非教義清單，自稱「朝聖的子民」。二十世紀後期最具神學質量的合一文件之一，其後原住民公約續寫其精神。' },
          { title_zh: '聯合衛理公會教規', title_orig: 'The Book of Discipline of The United Methodist Church', author: '聯合衛理公會總議會', era: '1968 起歷屆修訂', place: '美國', language: '英文', intro: '聯合衛理公會的法規總書，承衛斯理《大會紀要》傳統，教義標準、社會原則與治理法規合為一冊，每四年總議會修訂。衛理宗「以法規承載靈命」傳統的當代形態，近年分裂之爭亦繞其條文而戰。' },
          { title_zh: '蘭柏會議決議彙編', title_orig: 'Resolutions of the Lambeth Conferences', author: '普世聖公宗蘭柏會議', era: '1908–1998（現代各屆）', place: '倫敦蘭柏宮／坎特伯裡', language: '英文', intro: '聖公宗全球主教十年一會的決議彙編：一九三〇年首開節育之禁、一九六八年論戰爭與和平、一九九八年第一一〇決議定性婚姻議題至今爭論不休。無中央法權的宗派如何以決議維繫共融的百年檔案。' },
          { title_zh: '克里特神聖大會議文件', title_orig: 'Documents of the Holy and Great Council of Crete', author: '正教會神聖大會議', era: '2016', place: '克里特', language: '希臘文（多語）', intro: '籌備半世紀餘的泛正教大會議終在克里特召開，通過散居、禁食、婚姻與對外關係六文件，惟四教會臨時缺席。千年來正教會最接近大公會議的嘗試，其成果與裂痕同為當代正教的寫照。' },
          { title_zh: '全俄地方教會會議文件', title_orig: 'Деяния Поместного Собора 1917–1918', author: '俄羅斯正教會全俄地方會議', era: '1917–1918', place: '莫斯科', language: '俄文', intro: '革命炮聲中召開的全俄教會會議，恢復中斷二百年的牧首制、選出吉洪，並通過教區自治與平信徒參與的改革方案。旋遭布爾什維克鎮壓而未及實施，二十世紀正教會憲政的未竟藍圖。' },
          { title_zh: '麥德林會議文件', title_orig: 'Documentos de Medellín', author: '拉丁美洲主教會議第二屆大會', era: '1968', place: '哥倫比亞麥德林', language: '西班牙文', intro: '拉美主教團把梵二落地為「優先選擇窮人」：指認制度性暴力、支持基層教會團體與良知化教育。解放神學的官方出生地，此後拉美與全球南方教會的路線圖文件。' },
          { title_zh: '黑人神學宣言', title_orig: 'Black Theology: Statement of the National Committee of Black Churchmen', author: '全國黑人教會人士委員會', era: '1969', place: '紐約', language: '英文', intro: '黑人力量運動中，黑人教會領袖宣告「黑人神學是黑人解放的神學」，同年科恩《黑人神學與黑人力量》出版。非裔教會自我神學化的憲章文件，處境神學浪潮的北美起點。' },
          { title_zh: '丹弗斯聲明', title_orig: 'The Danvers Statement', author: '聖經男女角色協會', era: '1988', place: '麻州丹弗斯', language: '英文', intro: '互補論陣營就兩性角色發表的聲明，主張男女平等尊嚴而職分有別，家庭與教會領導歸於男性。福音派性別論戰的定調文件之一，與平等論宣言相對而立，至今為神學院路線的試金石。' },
          { title_zh: '聖經平等宣言', title_orig: 'Men, Women and Biblical Equality', author: '聖經平等基督徒協會', era: '1989', place: '美國', language: '英文', intro: '平等論陣營的回應宣言，逐點申論恩賜與職分不依性別、婚姻為相互順服。與丹弗斯聲明構成福音派性別神學的兩極文本，其釋經之爭延燒至今。' },
          { title_zh: '世界華人福音會議宣言', title_orig: '世界華人福音會議宣言（華福宣言）', author: '第一屆世界華人福音會議', era: '1976', place: '香港', language: '中文', intro: '全球華人教會首次大團聚發表的宣言，立「華人教會，天下一心；廣傳福音，直到主臨」之志，成立華福運動。華人福音派跨國協作的憲章文件，離散華人教會身分的凝聚點。' },
          { title_zh: '巴勒斯坦凱羅斯文件', title_orig: 'Kairos Palestine: A Moment of Truth', author: '巴勒斯坦基督徒領袖聯合', era: '2009', place: '伯利恆', language: '阿拉伯文／英文', intro: '巴勒斯坦各宗派基督徒仿南非凱羅斯發表的真相時刻文件，宣認佔領是罪、抵抗以愛為法，向普世教會發出行動呼籲。中東本土基督徒罕見的共同神學發聲，當代政治神學的爭議文本。' },
          { title_zh: '衛理社會信條', title_orig: 'The Methodist Social Creed', author: '美以美會總議會', era: '1908', place: '巴爾的摩', language: '英文', intro: '美以美會針對工業社會苦況通過的社會信條，主張廢除童工、保障工資與休息日，同年為聯邦教會協進會採納。教會史上第一份宗派社會信條，社會福音運動的制度結晶。' },
          { title_zh: '泰澤規章', title_orig: 'La Règle de Taizé', author: '羅哲弟兄', era: '1954', place: '泰澤', language: '法文', intro: '羅哲為跨宗派的泰澤團體手訂的簡短規章，以「內心的喜樂、單純與憐憫」代替繁密條文。新教修道傳統中斷四百年後的再生憲章，普世共融生活的活規範。' },
          { title_zh: '仁愛傳教修女會會憲', title_orig: 'Constitutions of the Missionaries of Charity', author: '德蕾莎修女', era: '1950', place: '加爾各答', language: '英文', intro: '德蕾莎修女為服事「窮人中的至窮者」創立修會而訂的會憲，於三願外加第四願：全心免費服事至窮者。二十世紀最著名修會的立會文件，加爾各答的憐憫自此制度化為全球網絡。' },
          { title_zh: '阿克拉信仰告白', title_orig: 'The Accra Confession', author: '世界改革宗教會聯盟大會', era: '2004', place: '迦納阿克拉', language: '英文', intro: '世界改革宗聯盟於昔日奴堡之地通過的告白，宣認經濟不義與生態破壞是信仰問題，向新自由主義全球化說「不」。以 status confessionis 處理經濟議題的先例，南方改革宗的先知之聲。' },
          { title_zh: '曼哈頓宣言', title_orig: 'The Manhattan Declaration', author: '美國福音派、天主教與正教領袖聯署', era: '2009', place: '紐約', language: '英文', intro: '跨傳統保守派領袖就生命、婚姻與宗教自由發表的良心宣言，宣示不惜公民不服從。文化戰爭時代的跨教會結盟文本，簽署與拒簽本身即繪出美國基督教的斷層線。' },
          { title_zh: '全國福音派協會信仰聲明', title_orig: 'NAE Statement of Faith', author: '美國全國福音派協會', era: '1942', place: '聖路易', language: '英文', intro: '美國福音派為別於基要派的分離主義與主流派的自由神學而組成全國協會，其七條信仰聲明簡明界定福音派共識。「新福音派」運動的組織起點文件，戰後福音派身分的最小公分母。' }
        
        
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
          { title_zh: '基督教史', title_orig: 'The Story of Christianity', author: '岡薩雷斯（Justo L. González）', era: '1984／2010', place: '美國／古巴', language: '英文', intro: '岡薩雷斯的兩卷通史,以流暢可讀著稱,自初代教會述至當代,特別注重拉美與全球南方視角,糾正以歐美為中心的傳統敘事。他兼顧神學、社會與文化脈絡,使非專業讀者亦能掌握教會史的全貌。此書已成為神學院最廣用的教會史教材之一,是當代最具普及力與全球意識的基督教通史。' },
          { title_zh: '世界基督教運動史', title_orig: 'History of the World Christian Movement (Vol. 1–2)', author: '戴爾‧歐文與史考特‧孫奎斯特（Dale T. Irvin & Scott W. Sunquist）', era: '二十一世紀初', place: '美國', language: '英語', intro: '兩卷本通史以多極視角重構基督教二千年歷程，第一卷（2001）涵蓋遠古至1453年，第二卷（2012）延伸至當代，系統納入亞洲、非洲、拉丁美洲教會史，由Orbis Books出版，打破歐洲中心敘事框架。' },
          { title_zh: '亞洲基督教史', title_orig: 'A History of Christianity in Asia (Vol. 1–2)', author: '賽繆爾‧休‧穆飛特（Samuel Hugh Moffett）', era: '二十世紀末至二十一世紀初', place: '美國', language: '英語', intro: '美國學者穆飛特耗費數十年撰成兩卷亞洲基督教通史，第一卷（1992）追溯至1500年，第二卷（2005）延伸至1900年，由Orbis Books出版，揭示亞洲基督教悠久獨立的傳統，扭轉歐洲宣教為起點的偏見。' },
          { title_zh: '基督教：三千年的歷史', title_orig: 'Christianity: The First Three Thousand Years', author: '迪爾梅德‧麥卡洛克（Diarmaid MacCulloch）', era: '二十一世紀初', place: '英國', language: '英語', intro: '牛津大學史家麥卡洛克以千頁鉅著涵蓋基督教三千年全球演變，系統兼顧東方正教、非洲科普特、亞洲景教及拉丁美洲等邊緣傳統，2010年英國Allen Lane暨美國Viking出版，被學界公認為迄今最具全球視野的基督教單卷通史。' },
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
          { title_zh: '下一個基督王國', title_orig: 'The Next Christendom', author: '詹金斯（Philip Jenkins）', era: '2002', place: '美國', language: '英文', intro: '詹金斯以人口統計與歷史分析,論證基督教的重心已不可逆轉地從歐美轉移到非洲、拉美與亞洲的全球南方,二十一世紀的「典型基督徒」將是南半球的有色人種。他剖析南方基督教的超自然取向、保守倫理與蓬勃增長,預示其將重塑世界基督教的面貌。此書是全球基督教研究的劃時代之作,改寫了人們對基督教未來的想像。' },
          { title_zh: '南非的班圖先知', title_orig: 'Bantu Prophets in South Africa', author: 'Bengt G. M. Sundkler', era: '1948年初版；1961年修訂版', place: '南非', language: '英文', intro: '奠基性學術史著，系統考察南非祖魯族及班圖語系獨立教會與錫安教派，為非洲本土基督教研究領域的奠基典範之作。' },
          { title_zh: '祖魯錫安教派與若干史瓦帝錫安信徒', title_orig: 'Zulu Zion and Some Swazi Zionists', author: 'Bengt Sundkler', era: '1976年', place: '南非', language: '英文', intro: '聚焦以賽亞‧尚貝（Isaiah Shembe）所創拿撒勒浸信會及南部非洲錫安派各支系，兼論史瓦帝錫安信徒，為研究南非本土基督教祭禮與先知傳統的核心文獻。' },
          { title_zh: '阿拉杜拉：約魯巴族的宗教運動', title_orig: 'Aladura: A Religious Movement Among the Yoruba', author: 'J. D. Y. Peel', era: '1968年', place: '奈及利亞', language: '英文', intro: '社會人類學經典，考察奈及利亞約魯巴族阿拉杜拉（禱告派）獨立教會的興起、教義與社會功能，為非洲本土靈恩基督教最重要的田野研究著作之一。' },
          { title_zh: '非洲的教會，1450–1950', title_orig: 'The Church in Africa, 1450–1950', author: 'Adrian Hastings', era: '1994年', place: '非洲（全洲）', language: '英文', intro: '牛津基督教會史系列鉅著，涵蓋衣索匹亞正教、天主教、新教及非洲獨立教會五百年史，含加里克‧佈雷德（Garrick Braide）與錫安基督教會等非洲本土運動。' },
          { title_zh: '五旬節主義：全球起源與發展', title_orig: 'Pentecostalism: Origins and Developments Worldwide', author: 'Walter J. Hollenweger', era: '現代', place: '英國／美國', language: '英文', intro: '五旬節研究創始學者霍倫韋格的定論性全球概覽，識別五旬節主義五大歷史根源，綜合數十年口述與文獻研究，追蹤運動在各大洲的開展歷程。' },
          { title_zh: '恩典與恩賜：趙鏞基與汝矣島純福音教會的成長', title_orig: 'Charis and Charisma: David Yonggi Cho and the Growth of Yoido Full Gospel Church', author: 'Myung Sung-Hoon（主編）；Hong Young-Gi（主編）', era: '現代', place: '韓國', language: '英文', intro: '宣教研究叢書出版的汝矣島純福音教會主要學術研究，分析趙鏞基牧師領導風格、細胞小組結構與聖靈神學，探討全球最大單一會眾教會的成長機制。' },
          { title_zh: '火焰之舌：新教在拉丁美洲的爆炸性擴張', title_orig: 'Tongues of Fire: The Explosion of Protestantism in Latin America', author: 'David Martin', era: '現代', place: '英國', language: '英文', intro: '英國社會學家馬丁的奠基性著作，以巴西、智利、瓜地馬拉等國為案例，從宗教志願主義與社會轉型視角分析五旬節主義取代天主教成為拉丁美洲主導宗教力量的動因。' },
          { title_zh: '非洲五旬節主義導論', title_orig: 'African Pentecostalism: An Introduction', author: 'Ogbu Kalu', era: '現代', place: '奈及利亞／美國', language: '英文', intro: '牛津大學出版社出版的非洲五旬節主義首部全面學術概覽，涵蓋非洲本土獨立教會、宣教基督教的互動，以及1970年代後靈恩運動在西非、東非、中非、南非的區域發展。' },
          { title_zh: '聖靈的世紀：五旬節與靈恩更新百年史（1901–2001）', title_orig: 'The Century of the Holy Spirit: 100 Years of Pentecostal and Charismatic Renewal, 1901–2001', author: 'Vinson Synan（主編）', era: '現代', place: '美國', language: '英文', intro: '託馬斯‧尼爾遜出版社百年紀念鉅著，西南歷史學家西南、巴雷特、霍肯等人合撰，全面記述1901年託皮卡至世紀末天主教靈恩、新教靈恩與五旬節宗跨洲擴展的完整歷程。' },
          { title_zh: '韓國靈恩大復興及其後的苦難', title_orig: 'The Korean Pentecost and the Sufferings Which Followed', author: 'William N. Blair & Bruce F. Hunt', era: '現代', place: '韓國', language: 'English', intro: '布萊爾親歷1907年平壤大復興，其婿韓布仁續述日本統治與共產主義下的教會苦難，1977年由真理旗幟出版社出版，為韓國教會史最重要的第一手英文史料之一。' },
          { title_zh: '死線以前', title_orig: 'Before the Dawn（死線を越えて）', author: '賀川豐彥（Kagawa Toyohiko）', era: '現代', place: '日本', language: 'Japanese', intro: '賀川豐彥自傳體小說，1920年在日本出版即成暢銷書，描繪神戶貧民窟的社會救助實踐與基督信仰動力；英譯本1924年由喬治多蘭出版社發行，奠定其國際聲望。' },
          { title_zh: '智如蛇，純如鴿：中國基督徒的見證', title_orig: 'Wise as Serpents, Harmless as Doves: Christians in China Tell Their Story', author: '趙天恩（Jonathan Chao）& Richard Van Houten', era: '現代', place: '中國', language: 'English', intro: '趙天恩與萬理恩根據中國教會研究中心逾百份訪談整理而成，記錄1949至1984年三自愛國運動興起與家庭教會發展史，1988年出版，為研究中國地下教會的奠基學術著作。' },
          { title_zh: '印度賤民：基督徒與宗教的束縛或解放', title_orig: 'Dalits in India: Religion as a Source of Bondage or Liberation with Special Reference to Christians', author: 'James Massey', era: '1995', place: '印度', language: '英文', intro: '賤民神學先驅梅西考察印度基督徒賤民的歷史處境，分析宗教如何在種姓壓迫下成為束縛或解放力量，為達利特基督教研究奠定社會史基礎。' },
          { title_zh: '緬甸克倫族人民史', title_orig: 'The History of the Karen People of Burma', author: 'Angelene Naw', era: '2023', place: '緬甸（克倫族地區）', language: '英文', intro: '緬甸裔學者瑙撰述克倫族自十九世紀浸信會接觸以來的歸信、文化復興與政治抵抗史，強調克倫族自身能動性而非單純西方宣教敘事。' },
          { title_zh: '菲律賓教會史讀本', title_orig: 'Readings in Philippine Church History', author: 'John N. Schumacher, S.J.', era: '1979', place: '菲律賓', language: '英文', intro: '耶穌會史家舒馬赫主編，涵蓋西班牙殖民時期至二十世紀的菲律賓教會發展，收錄原始史料與論文，為東南亞天主教史的標準參考文獻。' },
          { title_zh: '與星共生：大洋洲基督教起源', title_orig: 'To Live Among the Stars: Christian Origins in Oceania', author: 'John Garrett', era: '1982', place: '大洋洲（斐濟、湯加、巴布亞紐幾內亞、密克羅尼西亞、玻里尼西亞）', language: '英文', intro: '世界教會協會出版，首部全面記述太平洋島嶼天主教與新教起源的區域教會史，呈現各島嶼民族在歸信過程中的主體參與與文化轉化。' },
          { title_zh: '拉丁美洲走向新教？福音派成長的政治學', title_orig: 'Is Latin America Turning Protestant? The Politics of Evangelical Growth', author: 'David Stoll', era: '現代', place: '拉丁美洲', language: '英文', intro: '史託爾1990年批判性政治史，檢視美國差會網絡、外國資金與在地社會動態對拉丁美洲福音派擴張的影響，立場較馬丁更具批判性，兩書對讀可見學界對此運動的多元詮釋張力。' },
          { title_zh: '巴西基督徒基層社區與社會變革', title_orig: 'Base Christian Communities and Social Change in Brazil', author: 'Warren Edward Hewitt', era: '現代', place: '巴西', language: '英文', intro: '赫威特以聖保羅總教區為田野，透過問卷調查實證考察1970至80年代基層教會社區（CEBs）如何成為社會變革與政治動員的組織核心，為英語學界最嚴謹的基層社區運動歷史研究。' },
          { title_zh: '翻轉的話語與世界：殖民拉丁美洲的原住民基督宗教', title_orig: 'Words and Worlds Turned Around: Indigenous Christianities in Colonial Latin America', author: 'David Tavárez（編）', era: '現代', place: '拉丁美洲', language: '英文', intro: '科羅拉多大學出版社2017年論文集，十一位歷史學家與人類學家從納瓦特爾文、薩波特克文、克丘亞文等八種原住民語原始文獻，重構墨西哥與安地斯原住民主動接受、改造並抵抗基督宗教的歷程。' },
          { title_zh: '謹慎與勇氣：俄羅斯與東歐的宗教處境', title_orig: 'Discretion and Valour: Religious Conditions in Russia and Eastern Europe', author: 'Trevor Beeson', era: '20世紀', place: '東歐', language: '英文', intro: '英國聖公會神職人員畢森綜覽蘇聯及東歐各共產國家中東正教、天主教與新教的處境，大量引用凱斯頓研究所蒐集的第一手文件與田野調查資料。初版由Fontana/Collins於1974年出版，修訂版1982年再版，是冷戰時期研究共產體制下教會生存狀況最具系統性的英文參考著作之一。' },
          { title_zh: '牧首與先知：今日俄羅斯東正教會的迫害', title_orig: 'Patriarch and Prophets: Persecution of the Russian Orthodox Church Today', author: 'Michael Bourdeaux', era: '20世紀', place: '俄羅斯', language: '英文', intro: '凱斯頓學院創辦人包度彙編蘇聯境內東正教神職人員的請願書、公開信與地下文件，系統記錄赫魯雪夫至布里茲涅夫時代國家對東正教的全面打壓。初版由Macmillan於1969年在倫敦出版，是以原始蘇聯文獻為據的學術倡議先驅之作。' },
          { title_zh: '非裔美國人經驗中的黑人教會', title_orig: 'The Black Church in the African American Experience', author: 'C. Eric Lincoln, Lawrence H. Mamiya', era: '現代（1900年至今）', place: '美國', language: '英文', intro: '林肯與馬米亞歷時十年、訪談逾1,800位黑人牧師的大規模田野研究，全面考察七大黑人主流宗派的歷史、神學與社會角色，1990年由杜克大學出版社出版，榮獲宗教社會學會年度最佳著作獎。' },
          { title_zh: '非洲女性神學家關懷圈史（一九八九—二〇〇七）', title_orig: 'A History of the Circle of Concerned African Women Theologians 1989–2007', author: 'Rachel NyaGondwe Fiedler', era: '現代（二十至二十一世紀）', place: '非洲（馬拉威、泛非）', language: '英文', intro: '記錄迦納神學家梅西‧奧杜尤葉於一九八九年創立「非洲女性神學家關懷圈」的始末與發展，詳述女性神學家如何以自身文化語境突破男性主導的非洲神學論述，建構以婦女為主體的組織網絡。' },
          { title_zh: '國母：南非曼亞諾婦女史', title_orig: 'Mothers of the Nation: Manyano Women in South Africa', author: 'Lihle Ngcobozi', era: '現代（二十至二十一世紀）', place: '南非', language: '英文', intro: '作者身為曼亞諾三代傳人，重新審視南非最古老的非洲母系組織——曼亞諾婦女祈禱運動，揭示其在種族隔離時代如何以信仰與姊妹情誼凝聚黑人女性，成為公共抵抗的隱形骨幹。' },
          { title_zh: '婦女、宗教與巴西基層教會的社會變革', title_orig: 'Women, Religion, and Social Change in Brazil\'s Popular Church', author: 'Carol Ann Drogus', era: '現代（二十世紀）', place: '巴西', language: '英文', intro: '以聖保羅基層教會社群（CEBs）為田野，訪談眾多婦女成員，揭示她們如何將解放神學的階級論述轉化為在地服務行動，主導社區衛生、托育與基礎建設的爭取，成為拉丁美洲民主化草根力量的核心。' },
          { title_zh: '朝鮮的性別與宣教相遇：新女性、舊秩序', title_orig: 'Gender and Mission Encounters in Korea: New Women, Old Ways', author: 'Hyaeweol Choi', era: '現代（二十世紀）', place: '韓國', language: '英文', intro: '梳理日本殖民時期美國女性傳教士與朝鮮女性的相遇史，分析「新女性」形象如何在基督信仰、儒家性別秩序與民族主義交織中被建構，呈現朝鮮婦女在宣教場域中的能動性與主體詮釋。' },
          { title_zh: '毛利族的先知：拉塔納運動史', title_orig: 'Ratana: The Man, The Church, The Political Movement', author: 'J. McLeod Henderson', era: '近現代（1918–1972）', place: '紐西蘭', language: '英文', intro: '記述毛利先知塔胡波蒂基‧威瑞穆‧拉塔納於1918年創立拉塔納教會的全過程，涵蓋其泛部落復興運動、議會政治影響及毛利語禮拜傳統，是首部系統梳理這一原住民主導基督教運動的學術史著。' },
          { title_zh: '彩虹靈性神學：澳洲原住民神學芻議', title_orig: 'Rainbow Spirit Theology: Towards an Australian Aboriginal Theology', author: 'Rainbow Spirit Elders（彩虹靈性長老群）', era: '近現代（1997年初版）', place: '澳大利亞', language: '英文', intro: '昆士蘭六個原住民族裔的天主教、路德宗、聖公會及聯合教會神學家聯合著述，嘗試以原住民造物傳統重新詮釋基督信仰，是澳洲原住民神學史上首部由族人自主發聲的集體神學宣言。' },
          { title_zh: '部落印度的基督教與政治：浸信宣教與那加民族主義', title_orig: 'Christianity and Politics in Tribal India: Baptist Missionaries and Naga Nationalism', author: 'G. Kanato Chophy（那加族學者）', era: '近現代（2021年）', place: '印度東北那加蘭邦', language: '英文', intro: '那加族人類學家以民族誌與歷史學雙重方法，梳理美南浸信會在印緬邊境那加山地的福音擴展如何催生出近三百萬人的那加民族認同與政治自主意識，突顯原住民主體在宗教轉化中的能動性。' },
          { title_zh: '米佐人：印度東北的身份認同與歸屬感', title_orig: 'Being Mizo: Identity and Belonging in Northeast India', author: 'Joy L. K. Pachuau（米佐族學者）', era: '近現代（2014年）', place: '印度米佐拉姆邦', language: '英文', intro: '米佐族歷史學家以歷史人類學方法考察十九世紀末威爾斯長老教會進入後米佐族群如何主動整合基督信仰、重構族群身份，為獨立後印度東北邊疆宗教文化研究的奠基性民族誌著作。' },
          { title_zh: '薩米人以自然為中心的基督教：歐洲北極圈的原住民神學', title_orig: 'Sámi Nature-Centered Christianity in the European Arctic: Indigenous Theology beyond Hierarchical Worldmaking', author: 'Tore Johnsen（薩米神學家）', era: '近現代（2022年）', place: '挪威芬馬克郡（薩普米地區）', language: '英文', intro: '薩米神學家基於對芬馬克郡二十八位受訪者的深度田野研究，揭示北薩米基督教傳統如何在官方挪威路德宗階層式宇宙觀之外，保存並發展出以自然共融為核心的去殖民原住民神學視野。' },
          { title_zh: '基督教史中的宣教運動：信仰傳播研究', title_orig: 'The Missionary Movement in Christian History: Studies in the Transmission of Faith', author: '安德魯‧沃爾斯（Andrew F. Walls）', era: '二十世紀末', place: '美國', language: '英語', intro: '蘇格蘭宣教學者沃爾斯以「翻譯典範」重詮跨文化宣教史，論證基督教本質上是不斷移植與在地化的運動，而非西方文化輸出，1996年由Orbis Books出版，書中收錄多篇論文，共同奠定世界基督教研究的方法論基礎。' },
          { title_zh: '萬民門徒：世界基督教的支柱', title_orig: 'Disciples of All Nations: Pillars of World Christianity', author: '拉明‧薩內（Lamin Sanneh）', era: '二十一世紀初', place: '美國', language: '英語', intro: '甘比亞裔耶魯大學學者薩內以「可譯性」概念為核心，論證基督教福音本身即驅動去殖民化詮釋而非強化西方文化霸權，系統剖析全球南方教會自主神學的形成，2008年牛津大學出版社出版，是後殖民宣教學的重要里程碑。' },
          { title_zh: '非洲的基督教：非西方宗教的更新', title_orig: 'Christianity in Africa: The Renewal of a Non-Western Religion', author: '誇米‧貝迪亞科（Kwame Bediako）', era: '二十世紀末', place: '英國', language: '英語', intro: '迦納神學家貝迪亞科從非洲傳統宗教與基督教之連續性切入，挑戰歐洲基督教中心預設，論證非洲神靈觀可作為理解基督論的恰當前理解，1995年愛丁堡大學出版社出版，為非洲本土神學在國際學術舞臺上的發展奠定基礎。' },
          { title_zh: '基督教宣教：基督教如何成為世界宗教', title_orig: 'Christian Mission: How Christianity Became a World Religion', author: '黛娜‧羅伯特（Dana L. Robert）', era: '二十一世紀初', place: '美國', language: '英語', intro: '波士頓大學宣教史學者羅伯特以全球視野梳理兩千年宣教歷程，強調女性傳教士、在地信徒與非西方社群在塑造基督教全球化中的關鍵角色，2009年Wiley-Blackwell出版，為宣教史教學提供去中心化的精要導論。' },
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
          { title_zh: '德蕾莎修女傳', title_orig: 'Mother Teresa: Come Be My Light', author: '科洛迪丘克（Brian Kolodiejchuk）編', era: '2007', place: '印度／阿爾巴尼亞', language: '英文', intro: '德蕾莎修女在加爾各答貧民窟服事最貧窮垂死者,創立仁愛傳教修女會,成為二十世紀慈善與見證的象徵,獲諾貝爾和平獎並被封聖。本書集結其私人書信,意外揭露她在長年事奉中經歷漫長的「靈魂暗夜」,在感受不到上帝同在的乾枯中仍持守信德與愛德。此書既記其外在事功,更顯其內在信仰的深邃與真實,是現代聖徒見證的動人文獻。' },
          { title_zh: '金班古：非洲先知與其教會', title_orig: 'Kimbangu: An African Prophet and His Church', author: 'Marie-Louise Martin（穆爾英譯）', era: '1975年', place: '剛果／英國牛津', language: '英文', intro: '記述剛果先知西蒙‧金班古（Simon Kimbangu）的生平、神蹟、殖民政權迫害與其所創金班古教會之興起，為金班古研究最具代表性的英語傳記。' },
          { title_zh: '先知哈里斯：非洲先知與其在象牙海岸、黃金海岸的群眾運動（1913–1915）', title_orig: 'The Prophet Harris: A Study of an African Prophet and His Mass-Movement in the Ivory Coast and the Gold Coast 1913–1915', author: 'Gordon MacKay Haliburton', era: '1971年', place: '西非（科特迪瓦、迦納）', language: '英文', intro: '考據威廉‧韋德‧哈里斯（William Wadé Harris）在西非的先知佈道運動，記錄其如何於兩年間使逾十萬人悔改，奠定哈里斯教會之歷史基礎。' },
          { title_zh: '先知哈里斯：西非的「黑色以利亞」', title_orig: 'Prophet Harris, the \'Black Elijah\' of West Africa', author: 'David A. Shank（默裡縮編）', era: '1994年', place: '賴比瑞亞／西非', language: '英文', intro: '尚克數十年田野調查成果，深入描繪哈里斯的神學觀、先知身份認同及其在賴比瑞亞至科特迪瓦的廣大復興影響，為最完整的哈里斯傳記。' },
          { title_zh: '威廉‧西摩與全球五旬節運動的起源：傳記與文獻史', title_orig: 'William J. Seymour and the Origins of Global Pentecostalism: A Biography and Documentary History', author: 'Gastón Espinosa', era: '現代', place: '美國', language: '英文', intro: '杜克大學出版社出版的西摩權威學術傳記，結合一手文獻史料，追溯1906年阿蘇薩街大復興的起源及其觸發全球六億餘五旬節信徒的歷史影響。' },
          { title_zh: '收成已白：查爾斯‧帕罕與五旬節主義的宣教起源', title_orig: 'Fields White unto Harvest: Charles F. Parham and the Missionary Origins of Pentecostalism', author: 'James R. Goff Jr.', era: '現代', place: '美國', language: '英文', intro: '阿肯色大學出版社出版的帕罕標準學術傳記，記述其1900年創辦託皮卡伯特利聖經學院、系統化「方言為靈洗初步憑據」教義，並考察其與西摩關係的複雜始末。' },
          { title_zh: '倪柝聲——當代神聖啟示的見證人', title_orig: 'Watchman Nee: A Seer of the Divine Revelation in the Present Age', author: 'Witness Lee（李常受）', era: '現代', place: '中國／美國', language: 'English', intro: '李常受以親歷者身份記述倪柝聲的屬靈見識、教會事奉與獄中見證，1991年由水流職事站出版，是研究地方召會運動創始人的第一手傳記史料。' },
          { title_zh: '中國三傑', title_orig: 'Three of China\'s Mighty Men', author: 'Leslie T. Lyall', era: '現代', place: '中國', language: 'English', intro: '英國內地會宣教士賴裡爾記述王明道、倪柝聲與楊紹唐三位華人教會領袖在共產政權迫害下的見證，1973年由海外基督使團出版，為二十世紀中國教會史重要英文史料。' },
          { title_zh: '宋尚節日記摘抄', title_orig: 'The Diary of John Sung: Extracts from His Journals and Notes', author: '宋天真（Levi Sung）整理', era: '現代', place: '中國', language: 'English', intro: '宋尚節之女宋天真整理父親親筆日記，2011年由新加坡盔甲出版社出版，呈現1927至1944年間這位佈道家在中國各地奮興事工的靈性歷程與病痛考驗。' },
          { title_zh: '我怎樣成為基督徒：日記摘錄', title_orig: 'How I Became a Christian: Out of My Diary', author: '內村鑑三（Uchimura Kanzō）', era: '現代', place: '日本', language: 'English', intro: '內村鑑三以英文親撰的回憶錄，1895年出版，記述明治時代日本知識分子接受基督信仰、赴美留學及返日後遭受不敬罪風波的心路歷程，無教會主義運動奠基文獻。' },
          { title_zh: '班底塔·拉瑪拜：她的一生', title_orig: 'Pandita Ramabai: The Story of Her Life', author: 'Helen S. Dyer', era: '1900', place: '印度（馬哈拉施特拉邦）', language: '英文', intro: '記錄印度梵文學者、社會改革者拉瑪拜從印度教歸信基督之歷程，兼述其創辦婦女庇護所的事業，是南亞女性本土信仰主體性的早期見證。' },
          { title_zh: '撒都孫達·辛格：親歷回憶錄', title_orig: 'Sadhu Sundar Singh: A Personal Memoir', author: 'C.F. Andrews', era: '1934', place: '印度／西藏', language: '英文', intro: '安德魯斯親歷記述錫克教背景苦行僧孫達‧辛格歸信基督後深入西藏傳道之生涯，展現印度本土靈修傳統與基督信仰相遇的獨特面貌。' },
          { title_zh: '瑪哈特瑪陰影下：主教阿薩裡亞與英屬印度基督教的磨難', title_orig: 'In the Shadow of the Mahatma: Bishop V.S. Azariah and the Travails of Christianity in British India', author: 'Susan Billington Harper', era: '2000', place: '印度（泰米爾納德／安得拉邦）', language: '英文', intro: '學術傳記，記述首位印度裔聖公會主教阿薩裡亞（1874–1945）領導大眾歸信運動、推動教會本土化，並周旋於甘地民族主義浪潮之間的一生。' },
          { title_zh: '羅梅洛傳：一個生命', title_orig: 'Romero: A Life', author: 'James R. Brockman, S.J.', era: '現代', place: '薩爾瓦多', language: '英文', intro: '耶穌會士布洛克曼所著薩爾瓦多總主教奧斯卡‧羅梅洛定本傳記，取材日記、講道與訪談，記錄其由謹慎保守轉為殉道先知的歷程，1980年遇刺至今仍為英語世界最權威的羅梅洛傳。' },
          { title_zh: '和平的暴力：埃爾德爾‧卡馬拉傳', title_orig: 'Dom Hélder Câmara: The Violence of a Peacemaker', author: 'José de Broucker（白夫人 Herma Briffault 譯）', era: '現代', place: '巴西', language: '英文', intro: '新聞人德布魯克深入巴西累西腓實地採訪，以對話體呈現「貧民主教」卡馬拉非暴力抵抗軍政府的信念與行動，為拉丁美洲進步主教傳記的先驅文本，1970年由奧比斯書局出版。' },
          { title_zh: '榮耀之門——五位殉道宣教士的故事', title_orig: 'Through Gates of Splendor', author: 'Elisabeth Elliot', era: '現代', place: '厄瓜多', language: '英文', intro: '伊利莎白‧艾略特親歷記述，五位宣教士赴厄瓜多爾深林向瓦歐達尼人傳道遭殺害，女性目擊者第一人稱敘事，彰顯犧牲神學與宣教呼召。1957年出版，成為二十世紀宣教文學經典。' },
          { title_zh: '慕拉第傳', title_orig: 'The New Lottie Moon Story', author: 'Catherine B. Allen', era: '現代', place: '中國', language: '英文', intro: '慕拉第（Lottie Moon，1840–1912）赴華南浸信宣教逾三十年，在山東平度自立佈道、創設女子事工，最終因饑荒餓病殉道。艾倫傳記為南美會官方定本，1980年出版，史料嚴謹。' },
          { title_zh: '艾偉德傳——小婦人大使命', title_orig: 'The Small Woman', author: 'Alan Burgess', era: '現代', place: '中國', language: '英文', intro: '艾偉德（Gladys Aylward，1902–1970）孤身赴中國山西傳道，於抗日戰火中率百名孤兒橫越太行山。伯吉斯1957年傳記根據第一手訪談寫就，後改編為電影《六福客棧》。' },
          { title_zh: '事實原貌——印度南方宣教紀實', title_orig: 'Things as They Are: Mission Work in Southern India', author: 'Amy Carmichael', era: '現代', place: '印度', language: '英文', intro: '艾美‧卡麥可（Amy Carmichael，1867–1951）親筆記述在印度多拿烏救援廟妓童女的艱辛歷程，不美化現實，直陳殖民地宣教困境。1905年出版，是近代宣教誠實自述的先驅文本。' },
          { title_zh: '加拉巴的瑪麗‧斯萊索——先驅宣道者', title_orig: 'Mary Slessor of Calabar: Pioneer Missionary', author: 'W. P. Livingstone', era: '現代', place: '奈及利亞', language: '英文', intro: '瑪麗‧斯萊索（Mary Slessor，1848–1915）出身蘇格蘭貧工家庭，赴奈及利亞卡拉巴達五十年，廢止殺嬰習俗、擔任部族仲裁者。李文斯頓傳記1916年出版，為非洲宣教史傳奠基之作。' },
          { title_zh: '賜我此山——羅西維爾醫療宣教自傳', title_orig: 'Give Me This Mountain', author: 'Helen Roseveare', era: '現代', place: '剛果', language: '英文', intro: '海倫‧羅西維爾（Helen Roseveare，1925–2016）醫師赴剛果東北省行醫佈道，歷經1964年辛巴叛亂被擄受辱仍堅持返回工場。本書1966年出版，為苦難神學與女性宣教韌性之見證。' },
          { title_zh: '特蕾小姐——摩洛哥福音使團先驅毛德‧凱瑞傳', title_orig: 'Miss Terri! The Story of Maude Cary, Pioneer GMU Missionary in Morocco', author: 'Evelyn Stenbock', era: '現代', place: '摩洛哥', language: '英文', intro: '毛德‧凱瑞（Maude Cary，1878–1967）在摩洛哥事奉逾五十年，二戰期間獨撐工場、主持聖經學院、訓練本地傳道人。斯滕伯克1970年傳記為北非穆斯林地區女性宣教史珍貴記錄。' },
          { title_zh: '長日將盡：桃樂西‧戴自傳', title_orig: 'The Long Loneliness: The Autobiography of Dorothy Day', author: 'Dorothy Day', era: '現代', place: '美國', language: '英文', intro: '天主教工人運動創辦人桃樂西‧戴的自傳，記述其皈依歷程、服事紐約貧困者之使命，及以工人之家實踐福音社會主義的一生見證。' },
          { title_zh: '藏匿處：彭柯麗的真實故事', title_orig: 'The Hiding Place', author: 'Corrie ten Boom with John and Elizabeth Sherrill', era: '現代', place: '荷蘭／美國', language: '英文', intro: '荷蘭鐘錶匠之女彭柯麗回憶二戰期間藏匿猶太人、身陷納粹集中營仍見證基督寬恕的信仰傳記，廣譯逾三十語言，為二十世紀最著名的殉道見證之一。' },
          { title_zh: '等待上帝：西蒙‧韋伊靈修文集', title_orig: 'Waiting for God (Attente de Dieu)', author: 'Simone Weil', era: '現代', place: '法國', language: '法文', intro: '法國猶太裔哲學家西蒙‧韋伊的書信與靈修隨筆結集，記述其接觸基督教神秘傳統、選擇與工人苦難連結、最終拒絕受洗而殉道於信仰臨界的獨特見證。' },
          { title_zh: '一粒麥子：艾迪特‧斯坦因自傳', title_orig: 'Life in a Jewish Family (Aus dem Leben einer jüdischen Familie)', author: 'Edith Stein', era: '現代', place: '德國', language: '德文', intro: '艾迪特‧斯坦因親筆自傳，記述十九至二十世紀初猶太家庭生活、從無神論到現象學研究、再皈依天主教的心路歷程，為殉道聖女留存的唯一自傳原典。' },
          { title_zh: '雕刻基督：卡莉爾‧豪斯蘭德的靈修作品', title_orig: 'The Reed of God', author: 'Caryll Houselander', era: '現代', place: '英國', language: '英文', intro: '英國天主教神秘主義者卡莉爾‧豪斯蘭德的代表靈修作品，以蘆葦為喻詮釋聖母馬利亞的接受性靈命，融合異象體驗與藝術家視野，為二十世紀英語天主教靈修文學經典。' },
          { title_zh: '愛的暴力：羅梅洛總主教牧靈講道選', title_orig: 'The Violence of Love', author: 'Óscar A. Romero（編譯：James R. Brockman, S.J.）', era: '現代', place: '薩爾瓦多', language: 'Spanish / English', intro: '薩爾瓦多羅梅洛總主教（1917–1980）彌撒講道選集，見證其在軍政府暴力統治下為窮人發聲之信仰立場，1980年於聖壇前遭暗殺前的預言性話語悉數收錄。' },
          { title_zh: '賈南尼：一位殉道者的塑造', title_orig: 'Janani: The Making of a Martyr', author: 'Margaret Ford', era: '現代', place: '烏幹達', language: 'English', intro: '烏幹達聖公會大主教賈南尼‧盧武姆（1922–1977）傳記，記述其在伊迪‧阿敏獨裁政權下對抗人權暴行，1977年遭政府殺害，為非洲聖公會二十世紀重要殉道見證。' },
          { title_zh: '為他人而活：亞吾許維茲的聖人瑪西米連‧葛白', title_orig: 'A Man for Others: Maximilian Kolbe, the Saint of Auschwitz', author: 'Patricia Treece', era: '現代', place: '波蘭', language: 'English', intro: '波蘭方濟各會神父瑪西米連‧葛白（1894–1941）傳記，依親歷者證詞重建其在亞吾許維茲集中營中自願替代一名父親赴死的殉道行動，1982年由教宗若望保祿二世封聖。' },
          { title_zh: '二十一人：科普特殉道者之旅', title_orig: 'The 21: A Journey into the Land of Coptic Martyrs', author: 'Martin Mosebach', era: '現代', place: '利比亞／埃及', language: 'German / English', intro: '2015年二月二十一名科普特基督徒在利比亞海灘遭「伊斯蘭國」斬首；德國作家莫澤巴赫親赴埃及阿爾烏爾村採訪殉道者家屬，以田野報導與神學反思重建二十一人的信仰面貌。' },
          { title_zh: '布痕瓦德的牧師：保羅‧施奈德傳', title_orig: 'Paul Schneider: The Pastor of Buchenwald', author: 'Edwin H. Robertson（譯自施奈德遺孀瑪格麗特述作）', era: '現代', place: '德國', language: 'German / English', intro: '德國信義宗牧師保羅‧施奈德（1897–1939）傳記，依遺孀述作及日記信件譯成，記述其拒絕向納粹政權低頭、入獄布痕瓦德集中營後仍持續傳道，終遭注射處決，為護教殉道典型。' },
          { title_zh: '可怕的抉擇：二十世紀基督教殉道史', title_orig: 'The Terrible Alternative: Christian Martyrdom in the Twentieth Century', author: 'ed. Andrew Chandler', era: '現代', place: '全球（含中國、烏幹達、南非、巴布亞紐幾內亞、巴基斯坦）', language: 'English', intro: '配合西敏寺1998年揭幕十尊殉道者雕像而出版的學術論文集，收錄王志明（中國文革）、曼奇‧馬塞莫拉（南非）、盧西安‧塔皮帝（巴布亞紐幾內亞）等十位二十世紀殉道者個案研究。' },
          { title_zh: '為基督受苦', title_orig: 'Tortured for Christ', author: 'Richard Wurmbrand', era: '20世紀', place: '羅馬尼亞', language: '英文', intro: '作者沃爾布蘭德為羅馬尼亞信義宗牧師，因從事地下教會工作，於1948年遭共產政權逮捕，在獄中承受十四年酷刑。1966年獲釋後赴美，親赴參議院作證，此書即根據其證詞寫成，出版於1967年，銷量逾千萬冊，成為迫害時代最廣傳的殉道見證文獻。' },
          { title_zh: '阿爾謝尼神父：司祭、囚徒、靈魂導師', title_orig: 'Father Arseny, 1893–1973: Priest, Prisoner, Spiritual Father', author: 'Anonymous (ed.); tr. Vera Bouteneff', era: '20世紀', place: '俄羅斯', language: '俄文', intro: '本書彙集多位倖存者口述，記錄俄羅斯東正教司祭阿爾謝尼在蘇聯古拉格勞改營中秘密為獄友祈禱、施聖禮的靈性牧養。原稿以秘密手抄本形式流傳，1998年由聖弗拉基米爾神學院出版社出版英譯本，是東正教殉道傳統的核心見證。' },
          { title_zh: '獄中遺書', title_orig: 'Testament from Prison', author: 'Georgi Vins', era: '20世紀', place: '俄羅斯', language: '俄文', intro: '維恩斯為蘇聯未登記浸信會「福音浸信會教會理事會」總書記，多次因信仰遭捕入獄。本書收錄其在獄中秘密傳出的書信、詩歌與靈修省思，記錄蘇聯浸信會信徒所受的系統性迫害。1975年由David C. Cook出版社出版英譯本，維恩斯於1979年在美蘇囚犯交換中獲釋流亡西方。' },
          { title_zh: '內在的自由：維辛斯基樞機主教獄中筆記', title_orig: 'Zapiski więzienne (A Freedom Within: The Prison Notes of Stefan Cardinal Wyszyński)', author: 'Stefan Cardinal Wyszyński', era: '20世紀', place: '波蘭', language: '波蘭文', intro: '波蘭首席主教暨樞機主教維辛斯基於1953至1956年遭共產政府軟禁期間，以日記形式記錄靈修祈禱與心路歷程。英譯本由Harcourt Brace Jovanovich於1983年出版，是天主教會抵抗東歐共產主義的重要文獻，展現信仰在政治高壓下的內在力量。' },
          { title_zh: '分水嶺：金恩年代的美國，1954–1963', title_orig: 'Parting the Waters: America in the King Years, 1954–63', author: 'Taylor Branch', era: '現代（1900年至今）', place: '美國', language: '英文', intro: '泰勒‧布蘭奇以十年資料撰成的三部曲首卷，以馬丁‧路德‧金恩為核心，全景重建1954至1963年美國民權運動，榮獲1989年普立茲歷史獎，被譽為二十世紀美國史最重要的傳記之一。' },
          { title_zh: '邁向自由：蒙哥馬利的故事', title_orig: 'Stride Toward Freedom: The Montgomery Story', author: 'Martin Luther King, Jr.', era: '現代（1900年至今）', place: '美國', language: '英文', intro: '馬丁‧路德‧金恩親筆回憶錄，記述1955至1956年蒙哥馬利公車杯葛運動的始末與神學省思，1958年由哈珀兄弟出版，是金恩思想與非暴力哲學的第一手見證文獻。' },
          { title_zh: '耶穌與被棄絕者', title_orig: 'Jesus and the Disinherited', author: 'Howard Thurman', era: '現代（1900年至今）', place: '美國', language: '英文', intro: '神學家霍華德‧瑟曼1949年的神學論著，主張耶穌本身屬於被壓迫的邊緣族群，為非裔美國人的解放神學奠定基礎，深刻影響馬丁‧路德‧金恩及整個民權運動世代。' },
          { title_zh: '為自由而戰：芬妮‧盧‧哈默的生平', title_orig: 'For Freedom\'s Sake: The Life of Fannie Lou Hamer', author: 'Chana Kai Lee', era: '現代（1900年至今）', place: '美國', language: '英文', intro: '李蔡娜‧凱所著的傳記，細述密西西比棉農出身的民權女鬥士芬妮‧盧‧哈默如何以信仰為力量對抗種族壓迫，1999年由伊利諾大學出版社出版，被譽為美國民權史中女性見證的重要文獻。' },
          { title_zh: '沒有寬恕就沒有未來', title_orig: 'No Future Without Forgiveness', author: 'Desmond Tutu', era: '現代（1900年至今）', place: '南非', language: '英文', intro: '諾貝爾和平獎得主屠圖大主教親筆記述擔任南非真相與和解委員會主席的親身見證，1999年由雙日出版社出版，深刻探討基督教神學中寬恕與正義的辯證，是後種族隔離時代最重要的見證著作之一。' },
          { title_zh: '愛麗絲‧冷希娜的盧姆帕教會', title_orig: 'The Lumpa Church of Alice Lenshina', author: 'Andrew Roberts', era: '現代（二十世紀）', place: '尚比亞', language: '英文', intro: '記述尚比亞女先知愛麗絲‧冷希娜於一九五三年神秘復甦後創立盧姆帕教會的歷程，教眾一度達十萬人；一九六四年獨立前夕衝突中數百信徒罹難，冷希娜在軟禁中離世，全書呈現其作為非洲女性宗教領袖的主體抉擇。' },
          { title_zh: '上帝是紅色的：一個原住民的宗教觀', title_orig: 'God Is Red: A Native View of Religion', author: 'Vine Deloria Jr.（德洛里亞）', era: '近現代（1973年初版）', place: '美國', language: '英文', intro: '拉科塔族學者德洛里亞以北美原住民宗教傳統為基礎，批判西方基督教的歷史線性觀與人類中心主義，主張原住民靈性根植於具體地景，為二十世紀最具影響力的原住民神學批判名著。' },
          { title_zh: '七重山', title_orig: 'The Seven Storey Mountain', author: 'Thomas Merton（默頓）', era: '現代', place: '美國', language: '英文', intro: '默頓自傳，記述其從浪蕩知識青年皈依天主教、入肯塔基州革責瑪尼熙篤修院之歷程。1948年出版後旋即成為二十世紀最具影響力的靈修文學經典，啟示出版有臺灣繁體中譯本。' },
          { title_zh: '泰澤的羅哲弟兄傳', title_orig: 'Frère Roger, de Taizé. Avec presque rien…', author: 'Sabine Laplane', era: '現代', place: '法國', language: '法文', intro: '記述羅哲‧修士（Frère Roger）創立泰澤共融團體之生平與精神遺產。泰澤位於法國勃艮第，吸引全球青年朝聖，羅哲弟兄於2005年崇拜中遭刺身亡，成為現代修道復興象徵。' },
          { title_zh: '查理‧德‧富高：摩洛哥探險家‧撒哈拉隱士', title_orig: 'Charles de Foucauld: Explorateur du Maroc, Ermite au Sahara', author: 'René Bazin', era: '現代', place: '法國', language: '法文', intro: '軍官出身的富高（Charles de Foucauld）皈依後隱居撒哈拉沙漠、為圖阿雷格人服務，1916年殉道。本傳記為其最權威早期傳記，亦是耶穌小兄弟會精神根源的原典。' },
          { title_zh: '昨日之糧', title_orig: 'Il pane di ieri', author: 'Enzo Bianchi', era: '現代', place: '義大利', language: '義大利文', intro: '波斯修道院（Bose）創辦人恩佐‧比安基（Enzo Bianchi）之回憶錄，記述其1965年獨自在比耶拉山區創建跨宗派混合修道社群的歷程，為義大利戰後修道復興的重要見證。' },
          { title_zh: '亞陀山長老西路安', title_orig: 'Старец Силуан（Saint Silouan the Athonite）', author: '索弗羅尼修士（Archimandrite Sophrony Sakharov）', era: '現代', place: '希臘（亞陀山）', language: '俄文', intro: '索弗羅尼依據西路安長老（1866–1938）日記與教導所寫傳記，1952年巴黎初版。西路安為俄羅斯農民出身的亞陀山修士，其耶穌禱文靈修影響二十世紀東方修道復興甚鉅。' },
          { title_zh: '無法抗拒的革命', title_orig: 'The Irresistible Revolution: Living as an Ordinary Radical', author: 'Shane Claiborne（謝恩‧克萊伯恩）', era: '現代', place: '美國', language: '英文', intro: '克萊伯恩記述其放棄主流生活、在費城北部貧民區創建「單純之道」新修道社群的親身歷程。2006年出版，為新修道主義運動（New Monasticism）最具代表性的宣言式回憶錄。' },
          { title_zh: '靈魂日記', title_orig: 'Il giornale dell\'anima (Journal of a Soul)', author: '若望二十三世教宗（Pope John XXIII）著；英譯：Dorothy White', era: '現代（1964年出版）', place: '義大利', language: '義大利文（英譯本：McGraw-Hill, 1965；Image Books, 1999，ISBN 9780385497541）', intro: '若望二十三世教宗一生靈修日記，記錄1895至1962年間內心祈禱與自我省察，為召開梵蒂岡第二屆大公會議的改革教宗留下珍貴精神見證。' },
          { title_zh: '望德的見證：若望保祿二世傳', title_orig: 'Witness to Hope: The Biography of Pope John Paul II', author: 'George Weigel 著', era: '現代（1999年）', place: '美國', language: '英文（Cliff Street Books／HarperCollins, 1999，ISBN 9780060187934）', intro: '授權傳記，逾九百頁，記錄若望保祿二世從波蘭神父到推動鐵幕崩潰的教宗一生，為現代天主教史最重要傳記之一。' },
          { title_zh: '聖人：莫洛凱的達米盎神父', title_orig: 'Holy Man: Father Damien of Molokai', author: 'Gavan Daws 著', era: '現代（1973年）', place: '美國／夏威夷', language: '英文（Harper & Row, 1973，ISBN 9780060109974；夏威夷大學出版社平裝重印 ISBN 9780824809201）', intro: '比利時聖心會士德來義（達米盎）自願赴夏威夷莫洛凱麻風病島服事，最終染病殉職，2009年封聖。本書為最權威英文傳記，資料嚴謹。' },
          { title_zh: '亞馬遜的殉道者：達琳修女傳', title_orig: 'Martyr of the Amazon: The Life of Sister Dorothy Stang', author: 'Roseanne Murphy, SND de Namur 著', era: '現代（2007年）', place: '美國／巴西', language: '英文（Orbis Books, 2007，ISBN 9781570757358）', intro: '美國聖母德來撒修女多羅德（Dorothy Stang）長期在巴西亞馬遜為窮農維權，2005年2月遭地主僱兇射殺，本書由同會修女執筆，記錄其殉道始末。' },
          { title_zh: '烏干達殉道者：非洲燔祭', title_orig: 'African Holocaust: The Story of the Uganda Martyrs', author: 'J. F. Faupel 著', era: '現代（1962年，1964年封聖前夕）', place: '英國／烏干達', language: '英文（Geoffrey Chapman, London, 1962；St Paul\'s Publications Africa 平裝重印 1984）', intro: '1886年烏干達國王姆旺加迫害天主教廷臣，查理‧盧旺加（Charles Lwanga）等二十二位青年信徒被焚殺殉道，1964年封聖。本書為標準歷史記述，出版於封聖前兩年。' },
          { title_zh: '比奧神父：真實的故事', title_orig: 'Padre Pio: The True Story (3rd ed.)', author: 'C. Bernard Ruffin 著', era: '現代（初版1982年；第三版2012年）', place: '美國', language: '英文（Our Sunday Visitor, 2012，ISBN 9781612788821）', intro: '方濟嘉布遣會士比奧神父（Padre Pio）身負五傷、一生神秘，2002年封聖。本書為最具權威的英文傳記，歷三版修訂，五百餘頁，資料詳盡客觀。' },
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
          { title_zh: '柏林希臘教父文集', title_orig: 'Die griechischen christlichen Schriftsteller (GCS)', author: '柏林科學院', era: '1897 起', place: '柏林', language: '希臘文', intro: '哈納克主持發起的前三世紀希臘教父批判版文集，以抄本系譜學全面取代米涅翻印。德國古代教會文獻學的旗艦工程，與維也納拉丁文集東西並峙。' },
          { title_zh: '東方基督教文獻集成', title_orig: 'Corpus Scriptorum Christianorum Orientalium (CSCO)', author: '魯汶與美國天主教大學合辦', era: '1903 起', place: '魯汶／華盛頓', language: '敘利亞／科普特／阿拉伯／亞美尼亞／吉茲文等', intro: '東方諸語基督教文獻的原文與譯文對冊叢刊，逾六百五十卷仍在續出。東方基督教研究的第一文庫，本藏敘利亞科普特諸條目的現代學術出處。' },
          { title_zh: '敘利亞教父文庫', title_orig: 'Patrologia Syriaca / Patrologia Orientalis 敘利亞卷', author: '格拉芬主編', era: '1894–1926', place: '巴黎', language: '敘利亞文', intro: '格拉芬發起的敘利亞教父原文對譯文庫，後擴為《東方教父文獻集成》。艾弗冷、阿弗拉哈特諸家的現代校勘刊佈自此起步，敘利亞學建制化的起點。' },
          { title_zh: '新約次經（施奈梅爾歇編）', title_orig: 'Neutestamentliche Apokryphen (Schneemelcher)', author: '亨內克與施奈梅爾歇（主編）', era: '1904 初版（歷版增訂）', place: '圖賓根', language: '德文（譯編）', intro: '新約次經的標準學術譯編，偽福音、行傳、書信與啟示逐篇附導論。典外文獻研究的世紀工具書，英譯本同為各語學界的通用門戶。' },
          { title_zh: '舊約次經偽典（查爾斯編）', title_orig: 'The Apocrypha and Pseudepigrapha of the Old Testament (Charles)', author: 'R.H.查爾斯（主編）', era: '1913', place: '牛津', language: '英文（譯編）', intro: '查爾斯主編的舊約次經偽典雙卷，首度把禧年書以諾書等系統呈現英語學界。第二聖殿文獻研究的奠基總集，查爾斯沃思新編之前的七十年標準。' },
          { title_zh: '猶大曠野發現叢刊', title_orig: 'Discoveries in the Judaean Desert (DJD)', author: '死海古卷國際編輯團', era: '1955–2010', place: '牛津', language: '希伯來／亞蘭／希臘文', intro: '死海古卷官方刊佈叢刊四十卷，歷半世紀壟斷與開放之爭終告全帙。二十世紀最大文獻發現的正式出版，聖經文本史研究的新地基。' },
          { title_zh: '拿戈瑪第文庫英譯本', title_orig: 'The Nag Hammadi Library in English (Robinson)', author: '詹姆斯‧羅賓遜（主編）', era: '1977', place: '克萊蒙特', language: '英文（譯自科普特文）', intro: '羅賓遜團隊把拿戈瑪第十三冊抄本全數英譯刊行，打破小圈壟斷。諾斯底研究大眾化與學術化的雙重引擎，本站 /gnostic 工程的學術遠源。' },
          { title_zh: '使徒教父文集（賴特富特校譯）', title_orig: 'The Apostolic Fathers (Lightfoot)', author: '賴特富特（哈默續成）', era: '1885–1891', place: '劍橋', language: '希臘文／英文', intro: '賴特富特主教以畢生考據校譯克勉、依納爵與坡旅甲文獻，確立依納爵書信七封真本。使徒教父研究的分水嶺，英語教父學術的最高紀念碑。' },
          { title_zh: '漢語基督教經典文庫集成', title_orig: '漢語基督教經典文庫集成', author: '道風書社（漢語基督教文化研究所）', era: '2003 起', place: '香港', language: '中文', intro: '漢語學界系統重刊明清以降漢語基督教原典的文庫工程，利瑪竇徐光啟至民國諸家逐卷校點。漢語神學自建文獻學的標誌，本藏漢語條目的現代整理出處。' }
        
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
          { title_zh: '七十士譯本（哥廷根校訂版）', title_orig: 'Septuaginta (Göttingen Edition)', author: '哥廷根七十士譯本研究院', era: '二十世紀至今陸續出版', place: '德國‧哥廷根', language: '希臘文', intro: '希伯來聖經最早、最重要的古希臘文譯本的現代批判校訂，由哥廷根研究院以譜系方法重建最接近原始譯文的文本，附極詳盡的校勘欄。七十士譯本是新約作者與早期教會所用的聖經，也是研究希伯來文本早期形態的關鍵見證。此校訂工程是現代古典與聖經學術協作的典範，為舊約文本史與早期基督教研究奠定不可或缺的基礎。（七十士古譯本本身屬古代譯校藏，此為現代學術校訂版。）' },
          { title_zh: '馮‧索登希臘文新約', title_orig: 'Die Schriften des Neuen Testaments (von Soden)', author: '赫爾曼‧馮‧索登', era: '1902–1913', place: '柏林', language: '希臘文', intro: '馮‧索登動員數十助手普查抄本自創分類系統的巨型校勘版，體系雖敗而材料長存。二十世紀初最大的私人校勘工程，其抄本普查為後世鋪路。' },
          { title_zh: '內斯特勒希臘文新約初版', title_orig: 'Novum Testamentum Graece (Nestle 1898)', author: '埃伯哈德‧內斯特勒', era: '1898', place: '斯圖加特', language: '希臘文', intro: '內斯特勒取三大校勘版多數讀法編成的袖珍希臘文新約，廉價精準而風行課堂。「內斯特勒本」百年世系的第一版，公認經文最後陣地的終結者。' },
          { title_zh: '新約大校勘版', title_orig: 'Editio Critica Maior (ECM)', author: '明斯特新約文本研究所', era: '1997 起', place: '明斯特', language: '希臘文', intro: '以「一致性譜系法」（CBGM）重建文本流變的世紀工程，公函與行傳啟示錄已刊。電腦系譜學重塑校勘範式的現場，NA 世系的上游母版。' },
          { title_zh: '國際希臘文新約計畫', title_orig: 'International Greek New Testament Project (IGNTP)', author: '英美學界聯合團隊', era: '1948 起', place: '牛津／伯明罕', language: '希臘文', intro: '英美合作徵引全部抄本異文的長程計畫，路加福音兩巨冊與約翰福音電子版為其成果。異文「全錄」理想的代表工程，數位校勘時代的先聲。' },
          { title_zh: '新約文本評註', title_orig: 'A Textual Commentary on the Greek New Testament', author: '布魯斯‧梅茨格', era: '1971', place: '普林斯頓', language: '英文', intro: '梅茨格代表 UBS 委員會逐處說明異文取捨理由的評註，委員分歧亦如實記錄。校勘決策首度全面透明化，譯者與學生案頭的必備解密書。' },
          { title_zh: '新約希臘文抄本總目', title_orig: 'Kurzgefasste Liste der griechischen Handschriften des NT', author: '庫爾特‧阿蘭', era: '1963（持續更新）', place: '明斯特', language: '德文', intro: '阿蘭建立的新約抄本統一編號總目，蒲草紙、安色爾、小寫體與經課本盡錄。全球抄本研究的共同座標系統，明斯特研究所的鎮所之典。' },
          { title_zh: '拉爾夫斯七十士手訂本', title_orig: 'Septuaginta (Rahlfs)', author: '阿爾弗雷德‧拉爾夫斯', era: '1935', place: '斯圖加特', language: '希臘文', intro: '拉爾夫斯依三大抄本編成的七十士手訂雙卷，於其逝世之年刊行。八十年來全球讀七十士的標準文本，哥廷根大版未竟前的通用聖經。' },
          { title_zh: '劍橋七十士大本', title_orig: 'The Old Testament in Greek (Brooke-McLean-Thackeray)', author: '布魯克、麥克萊恩與薩克雷', era: '1906–1940', place: '劍橋', language: '希臘文', intro: '以梵蒂岡抄本為底、廣註異文的七十士外交式校勘版，八經至歷史書刊成而中輟。與哥廷根重建式路線相對的另一方法典範，七十士學史的劍橋一翼。' },
          { title_zh: '基特爾希伯來聖經', title_orig: 'Biblia Hebraica (Kittel, BHK)', author: '魯道夫‧基特爾', era: '1906（1937 三版改用列寧格勒抄本）', place: '萊比錫／斯圖加特', language: '希伯來文', intro: '基特爾首創附校勘欄的希伯來聖經，三版起以最古完整的列寧格勒抄本為底。BHS/BHQ 世系的開山之作，舊約研究工作臺的百年基座。' },
          { title_zh: '希伯來大學聖經計畫', title_orig: 'Hebrew University Bible Project (HUBP)', author: '希伯來大學聖經計畫團隊', era: '1956 起', place: '耶路撒冷', language: '希伯來文', intro: '以阿勒頗抄本為底、四欄異文平行呈現的大型校勘工程，以賽亞耶利米以西結已刊。猶太學界自主的聖經文本學旗艦，與 BHQ 互映的耶路撒冷路線。' },
          { title_zh: '本篤會大修訂武加大', title_orig: 'Biblia Sacra iuxta Latinam Vulgatam versionem', author: '羅馬聖耶柔米修道院本篤會團隊', era: '1926–1995', place: '羅馬', language: '拉丁文', intro: '庇護十一世設修道院專責重建耶柔米原文的世紀工程，十八巨冊歷七十年告成。武加大文本學的最大成就，新武加大的學術地基。' },
          { title_zh: '斯圖加特武加大', title_orig: 'Biblia Sacra Vulgata (Weber-Gryson)', author: '韋伯與格里松（主編）', era: '1969（歷版修訂）', place: '斯圖加特', language: '拉丁文', intro: '單卷手訂的武加大校勘本，濃縮羅馬大版與牛津新約成果。學界日用的武加大標準本，拉丁聖經引用的通行座標。' },
          { title_zh: '新武加大', title_orig: 'Nova Vulgata', author: '教廷新武加大委員會', era: '1979', place: '羅馬', language: '拉丁文', intro: '梵二後依原文修訂耶柔米譯文的官定拉丁聖經，若望保祿二世頒為禮儀典範本。教會權威文本與現代文本學的正式和解，拉丁禮儀書的現行底本。' },
          { title_zh: '萊頓別西大校勘版', title_orig: 'The Old Testament in Syriac (Leiden Peshitta)', author: '萊頓別西大研究所', era: '1966 起', place: '萊頓', language: '敘利亞文', intro: '以安布羅削抄本為底的別西大舊約校勘叢刊，國際敘利亞學界協力半世紀。別西大研究的標準文本，敘利亞聖經學的萊頓總部。' },
          { title_zh: '博伊倫古拉丁聖經校勘版', title_orig: 'Vetus Latina: Die Reste der altlateinischen Bibel', author: '博伊倫古拉丁研究所', era: '1949 起', place: '博伊倫修道院', language: '拉丁文', intro: '本篤會博伊倫研究所自教父引文與抄本重建武加大之前拉丁聖經的世紀工程。古拉丁文本的總戶籍，拉丁聖經史研究的深水井。' },
          { title_zh: '霍納科普特新約校勘版', title_orig: 'The Coptic Version of the New Testament (Horner)', author: '喬治‧霍納', era: '1898–1924', place: '牛津', language: '科普特文', intro: '霍納獨力完成波海利與沙希地新約校勘各四卷與七卷，附直譯與異文。科普特新約研究的百年標準，一人一世代的譯本校勘傳奇。' },
          { title_zh: '施特萊特貝格哥德聖經校勘版', title_orig: 'Die gotische Bibel (Streitberg)', author: '威廉‧施特萊特貝格', era: '1908', place: '海德堡', language: '哥德文／希臘文', intro: '施特萊特貝格重建烏爾菲拉譯本並附推定希臘底本的對照校勘版。哥德語研究的標準文本至今，日耳曼語文學的基準工具。' },
          { title_zh: '希伯來聖經文本評鑑學', title_orig: 'Textual Criticism of the Hebrew Bible', author: '伊曼紐爾‧托夫', era: '1992（歷版修訂）', place: '耶路撒冷', language: '英文', intro: '死海古卷總編輯托夫的舊約文本學總論，以古卷證據重寫文本史框架。後古卷時代的標準教科書，「多元文本」範式的定調之作。' },
          { title_zh: '四福音對觀', title_orig: 'Synopsis Quattuor Evangeliorum (Aland)', author: '庫爾特‧阿蘭', era: '1963（歷版修訂）', place: '斯圖加特', language: '希臘文', intro: '阿蘭編製的四福音全文平行對觀，附多馬福音對照。共觀問題研究與釋經課堂的標準工具，福音比較閱讀的現代定本。' },
          { title_zh: '死海古卷聖經英譯', title_orig: 'The Dead Sea Scrolls Bible', author: '阿貝格、弗林特與烏爾裡希', era: '1999', place: '聖地牙哥', language: '英文', intro: '首部按古卷文本譯出的英文舊約，逐卷標示與馬所拉的出入。古卷文本學走向普及讀者的里程碑，「最古的聖經」的直接閱讀通道。' },
          { title_zh: '七十士新英譯本', title_orig: 'A New English Translation of the Septuagint (NETS)', author: '國際七十士學會譯者團', era: '2007', place: '牛津', language: '英文', intro: '依哥廷根文本譯出的七十士學術英譯，體例嚴格對映希伯來本差異。七十士研究復興的標誌成果，希臘舊約首獲現代標準英譯。' },
          { title_zh: '西奈抄本數位聯合計畫', title_orig: 'Codex Sinaiticus Project', author: '大英圖書館等四館聯合', era: '2005–2009', place: '倫敦／萊比錫／聖彼得堡／西奈', language: '希臘文（數位）', intro: '分藏四國的西奈抄本經高解析攝影與轉錄在線上虛擬合體。抄本學數位時代的旗艦示範，散葉古卷「數位重聚」的第一大案。' },
          { title_zh: '西奈新發現抄本群', title_orig: 'Sinai New Finds (1975)', author: '聖凱瑟琳修道院', era: '1975 發現', place: '西奈', language: '希臘／敘利亞／喬治亞文等', intro: '修道院北牆密室意外重見的千餘件抄本殘卷，含西奈抄本佚葉與高加索阿爾巴尼亞重寫本。二十世紀後期最大的抄本發現，多語聖經文獻的新礦脈。' }
        
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
          { title_zh: '聖經新譯本', title_orig: '聖經新譯本', author: '中文聖經新譯會', era: '1992', place: '香港', language: '繁體中文', intro: '聖經新譯本由華人聖經學者組成的中文聖經新譯會主持，於一九九二年完成全書，是少數完全由華人學者直接從原文翻譯的現代中文聖經。其譯文在忠實原文與現代語感之間求取平衡，並採用現代批判校勘版為底本，注重神學詞彙的精確。新譯本主要服事華人福音派教會，與和合本、思高本並列為當代重要的中文聖經系統，展現華人教會自主譯經的成熟。', link: '/scripture' },
          { title_zh: '呂振中譯本', title_orig: '呂振中譯本', author: '呂振中', era: '1946（新約）／1970（全書）', place: '北平／香港', language: '中文', intro: '呂振中牧師以一人之力自原文直譯全本聖經，寧拗口而求極貼原文語序。華人獨力譯經的最大成就，研經者對照原文的漢語利器，三十年孤詣的譯經豐碑。' },
          { title_zh: '施約瑟淺文理譯本', title_orig: '施約瑟淺文理新舊約聖經', author: '施約瑟', era: '1902', place: '上海', language: '中文（淺文理）', intro: '施約瑟主教癱瘓後以兩指擊打字機完成的淺文理全書，人稱「二指聖經」。譯經史最堅忍的身影，官話舊約之後其畢生志業的完成篇。' },
          { title_zh: '深文理和合譯本', title_orig: '文理和合譯本', author: '文理和合翻譯委員會', era: '1919', place: '上海', language: '中文（文理）', intro: '與官話和合本同年出版的文言版和合譯本，供士林與文言讀者。白話浪潮下文言聖經的絕唱，和合工程的另一半成果。' },
          { title_zh: '王宣忱新約譯本', title_orig: '王宣忱譯本', author: '王宣忱', era: '1933', place: '青島', language: '中文', intro: '實業家王宣忱自譯的新約全書，為華人個人譯經刊行之先聲。曾任和合本譯經助理的他以母語者身分獨立成書，華人自主譯經的開路者。' },
          { title_zh: '朱寶惠新約譯本', title_orig: '朱寶惠譯本', author: '朱寶惠（賽兆祥前期合作）', era: '1936', place: '南京', language: '中文', intro: '朱寶惠與賽兆祥合譯新約遇難後獨力重訂的譯本，力求原文精確兼白話流暢。賽珍珠之父與華人牧者合作未竟的成果，民國譯經多元嘗試的代表。' },
          { title_zh: '聖詠譯義初稿', title_orig: '聖詠譯義初稿', author: '吳經熊', era: '1946', place: '上海', language: '中文（文言韻體）', intro: '法學家吳經熊以詩經楚辭體重譯全部詩篇，蔣中正逐篇批閱潤色。「明明在上，赫赫其臨」——聖經漢譯文學化的極致實驗，民國文化史的奇葩。' },
          { title_zh: '新經全集', title_orig: '新經全集（吳經熊）', author: '吳經熊', era: '1949', place: '上海／香港', language: '中文（文言）', intro: '吳經熊繼聖詠後以典雅文言譯成新約全書，教廷嘉許刊行。文言譯經傳統的最後高峰，天主教漢語譯經的文人路線代表。' },
          { title_zh: '蕭靜山新經全集', title_orig: '新經全集（蕭靜山）', author: '蕭靜山', era: '1922', place: '獻縣', language: '中文', intro: '耶穌會士蕭靜山譯成的白話新約，思高全書問世前天主教通行數十年的中文新約。獻縣教區印書館的代表出版，天主教白話譯經的先行本。' },
          { title_zh: '嚴復馬可福音試譯', title_orig: '馬可所傳福音（嚴復譯）', author: '嚴復', era: '1908', place: '上海', language: '中文（文言）', intro: '譯界宗師嚴復應聖經公會之邀試譯馬可福音前四章，以桐城古文出之。「信達雅」大師與聖經的唯一交會，譯經史與翻譯史的著名擦肩。' },
          { title_zh: '巴克禮臺語譯本', title_orig: 'Sin-kū-iok ê Sèng-keng（巴克禮修訂）', author: '巴克禮', era: '1916（新約）／1933（舊約）', place: '臺南／廈門', language: '台語（白話字）', intro: '巴克禮牧師晚年自原文重譯的白話字新舊約，八旬猶伏案逐節推敲。臺灣教會百年誦讀的「巴克禮譯本」，臺語文學與信仰語言的定礎之作。' },
          { title_zh: '現代臺語譯本', title_orig: '現代台語譯本聖經', author: '臺灣聖經公會譯經團隊', era: '2021（全書）', place: '臺北', language: '台語（漢羅並列）', intro: '以現代臺語重譯的新舊約全書，漢字與白話字對照排印。巴克禮之後百年的臺語再譯，母語聖經在臺灣的當代接力。' },
          { title_zh: '客語聖經現代譯本', title_orig: '客語聖經：現代台灣客語譯本', author: '客語聖經翻譯委員會', era: '1993（新約）／2012（全書）', place: '臺北', language: '客語（漢羅對照）', intro: '臺灣客家教會歷卅年譯成的客語新舊約，漢字羅馬字並列。客家母語的第一部全本聖經，弱勢語言復振與信仰傳承的雙重工程。' },
          { title_zh: '臺灣原住民語聖經', title_orig: '台灣原住民族語聖經（阿美、太魯閣、布農、泰雅、排灣等）', author: '各族譯經委員會與聖經公會', era: '1957 起陸續出版', place: '臺灣', language: '南島語系諸語', intro: '阿美語、太魯閣語、布農語等原住民語聖經的長期譯經工程，多族已成全書。南島語言書面化與族語保存的核心文獻，臺灣教會最深的本土化成果。' },
          { title_zh: '粵語聖經', title_orig: '新廣東話聖經', author: '香港聖經公會譯經團隊', era: '1997', place: '香港', language: '粵語', intro: '以口語粵語譯成的新舊約全書，承十九世紀羊城土白譯本傳統而全面更新。方言聖經在當代的存續個案，粵語書面化的宗教一翼。' },
          { title_zh: '美國標準譯本', title_orig: 'American Standard Version (ASV)', author: '美國修訂委員會', era: '1901', place: '紐約', language: '英文', intro: '英國修訂本的美方定版，直譯嚴謹而以「耶和華」譯神名。二十世紀美國譯本世系的共同母本，RSV 與 NASB 皆其嫡裔。' },
          { title_zh: '新英語聖經', title_orig: 'The New English Bible (NEB)', author: '英國各宗派聯合譯委會（多德主持）', era: '1961–1970', place: '牛津／劍橋', language: '英文', intro: '多德主持、全然拋開欽定本傳統的全新英譯，文學顧問潤色如當代散文。「意義對意義」路線的英國旗艦，出版首日排隊搶購的譯經事件。' },
          { title_zh: '耶路撒冷聖經', title_orig: 'The Jerusalem Bible / La Bible de Jérusalem', author: '耶路撒冷聖經學院（法文原版）', era: '1956（法）／1966（英）', place: '耶路撒冷／巴黎', language: '法文／英文', intro: '道明會耶路撒冷聖經學院以原文譯注的天主教聖經，注釋豐富如小型百科，託爾金曾潤英譯約拿書。天主教聖經運動的旗艦成果，JB 家族的共同源頭。' },
          { title_zh: '新美國聖經', title_orig: 'New American Bible (NAB)', author: '美國天主教聖經協會', era: '1970', place: '華盛頓', language: '英文', intro: '美國天主教依原文譯成的官方聖經，梵二後禮儀讀經即用其文。北美彌撒中每主日誦讀的文本，天主教英語譯經的建制成果。' },
          { title_zh: '現代英文譯本', title_orig: 'Good News Translation (Today\'s English Version)', author: '美國聖經公會（奈達理論指導）', era: '1966–1976', place: '紐約', language: '英文', intro: '以奈達功能對等理論譯成的平白英文聖經，插畫線條簡雅，售逾億冊。翻譯理論落地的最大實驗場，全球「通俗語譯本」浪潮的原型。' },
          { title_zh: '信息本聖經', title_orig: 'The Message', author: '尤金‧畢德生', era: '1993–2002', place: '溫哥華', language: '英文', intro: '牧者學者畢德生以當代口語意譯全本聖經，「道成了肉身，搬進我們的街坊」。意譯光譜的極限之作，靈修閱讀的暢銷伴本，毀譽皆極的個人譯經。' },
          { title_zh: '德語統一譯本', title_orig: 'Einheitsübersetzung', author: '德語區天主教會（新教參與詩篇新約）', era: '1980（2016 修訂）', place: '斯圖加特', language: '德文', intro: '德語天主教會的統一官方譯本，初版新約與詩篇曾獲新教共同認可。德語區禮儀與教學的通用文本，大公合作譯經的德國個案。' },
          { title_zh: '法語普世合一譯本', title_orig: 'Traduction Œcuménique de la Bible (TOB)', author: '天主教與新教東正教聯合譯委會', era: '1975', place: '巴黎', language: '法文', intro: '天主教與新教學者逐卷共譯共注、東正教參與的法語聖經，羅馬書由昔日論敵合注尤具象徵。譯經史上最徹底的大公合作，合一運動的文本結晶。' },
          { title_zh: '拉丁美洲牧靈聖經', title_orig: 'Biblia Latinoamericana', author: '貝納爾‧胡羅特等', era: '1972', place: '智利', language: '西班牙文', intro: '智利工人堂區誕生的西語牧靈聖經，注釋直面貧窮與壓迫，軍政府一度指為顛覆。解放神學脈絡的平民聖經，拉美銷量數千萬的爭議譯本。' },
          { title_zh: '雷納-瓦萊拉1960修訂版', title_orig: 'Reina-Valera 1960', author: '聯合聖經公會修訂團', era: '1960', place: '紐約／馬德里', language: '西班牙文', intro: '熊聖經世系的二十世紀標準修訂，成為西語新教世界壓倒性的通用本。拉美福音派爆炸增長的隨身文本，西語世界的「欽定本」。' },
          { title_zh: '日語新共同譯聖經', title_orig: '新共同訳聖書', author: '日本聖書協會共同譯委會', era: '1987', place: '東京', language: '日文', intro: '日本天主教與新教共同譯成的聖經，取代口語訳成為教會通用本。日語譯經百年的大公總結，教會與文學界共用的標準文本。' },
          { title_zh: '韓語改譯聖經', title_orig: '성경개역（改譯聖經）', author: '朝鮮聖書公會改譯委員會', era: '1938（1961 한글판）', place: '首爾', language: '韓文', intro: '承羅斯譯本世系全面改譯的韓語聖經，其一九六一年韓字版至今為韓國新教主流用本。韓國教會爆炸成長世代的共同聖經，韓語宗教語彙的定型者。' },
          { title_zh: '韓語共同譯聖經', title_orig: '공동번역성서（共同翻譯聖書）', author: '韓國天主教與新教共同譯委會', era: '1977', place: '首爾', language: '韓文', intro: '韓國新舊教首度共譯的聖經，天主教沿用至今而新教主流未採。東亞大公譯經的先行實驗，南北韓天主教會共同的文本紐帶。' },
          { title_zh: '烏克蘭語聖經', title_orig: 'Біблія (переклад Огієнка)', author: '伊拉里翁‧奧希延科', era: '1962', place: '流亡溫尼伯刊行', language: '烏克蘭文', intro: '都主教奧希延科流亡中譯成的烏克蘭語全本聖經，蘇聯禁絕而海外傳承。民族語聖經與流亡教會的共命文本，今日烏克蘭的通用譯本之一。' },
          { title_zh: '波蘭千禧年聖經', title_orig: 'Biblia Tysiąclecia', author: '波蘭本篤會泰涅茨修道院主編', era: '1965', place: '波茲南', language: '波蘭文', intro: '紀念波蘭受洗千年的天主教原文新譯，旋成禮儀官定本。共黨時代波蘭教會的精神武備，若望保祿二世講道所引的母語聖經。' },
          { title_zh: '捷克普世譯本', title_orig: 'Český ekumenický překlad', author: '捷克各宗派聯合譯委會', era: '1979', place: '布拉格', language: '捷克文', intro: '共黨統治下捷克新舊教學者秘密協力廿年譯成的普世譯本。鐵幕內的大公譯經奇蹟，克拉利茨傳統的二十世紀繼承者。' },
          { title_zh: '義大利主教團譯本', title_orig: 'Bibbia CEI', author: '義大利主教團', era: '1971（2008 修訂）', place: '羅馬', language: '義大利文', intro: '義大利主教團的官方聖經，禮儀誦讀與教理教學的統一文本。馬爾提尼世系的當代接棒，義語天主教會的標準聖經。' },
          { title_zh: '藏語聖經', title_orig: '藏文聖經（1948）', author: '耶什克、雷卻勒與格爾根等三代譯者', era: '1948', place: '拉合爾刊行', language: '藏文', intro: '自摩拉維亞宣教士耶什克創譯至藏人基督徒格爾根續成，歷九十年三代完成的藏文全本聖經。譯經史最漫長的接力之一，喜馬拉雅宣教的文字遺產。' },
          { title_zh: '越南語聖經', title_orig: 'Kinh Thánh Việt Ngữ (1926)', author: '卡德曼夫婦與潘魁等', era: '1926', place: '河內', language: '越南文', intro: '宣道會卡德曼夫婦與越南文人潘魁合譯的國語字全本聖經。越南新教的通用譯本至今，國語字文學的重要早期文本。' },
          { title_zh: '阿姆哈拉語欽定新譯', title_orig: 'Haile Selassie Amharic Bible', author: '衣索比亞譯經委員會（海爾‧塞拉西敕修）', era: '1962', place: '阿迪斯阿貝巴', language: '阿姆哈拉文', intro: '海爾‧塞拉西皇帝敕命重譯的阿姆哈拉語聖經，取代阿布‧魯米世系。非洲君主主導譯經的當代個案，衣索比亞正教與新教共用的文本。' },
          { title_zh: '豪薩語聖經', title_orig: 'Littafi Mai Tsarki (Hausa)', author: '聖經公會譯經團', era: '1932', place: '拉哥斯／倫敦', language: '豪薩文', intro: '西非最大通用語豪薩語的全本聖經，穆斯林多數區宣教的語文成果。西非聖經流通的主力文本，非洲語言譯經的重鎮之作。' },
          { title_zh: '伊博語聯合譯本', title_orig: 'Union Igbo Bible', author: '聖公會譯經團（丹尼斯主持）', era: '1913', place: '奧尼查', language: '伊博文', intro: '整合伊博諸方言而成的「聯合伊博語」聖經，譯就而譯者丹尼斯歸途沉船殉職。奈及利亞東部教會的百年文本，語言標準化與譯經互造的個案。' },
          { title_zh: '史瓦希裡合一譯本', title_orig: 'Swahili Union Version', author: '東非聖經公會譯經團', era: '1952', place: '奈洛比／達累斯薩拉姆', language: '史瓦希里文', intro: '整合桑吉巴與內陸譯本傳統的史瓦希裡語聯合聖經。東非通用語的標準聖經，克拉普夫百年志業的成全之卷。' },
          { title_zh: '納瓦霍語聖經', title_orig: 'Diyin God Bizaad (Navajo Bible)', author: '納瓦霍譯經團隊與威克里夫同工', era: '1985', place: '美國西南', language: '納瓦霍文', intro: '歷四十年譯成的納瓦霍語全本聖經，族人譯者主導定稿。北美原住民語言的最大譯經成果，族語存續運動的信仰支柱。' },
          { title_zh: '海地克里奧爾語聖經', title_orig: 'Bib La (Haitian Creole)', author: '海地聖經公會譯經團', era: '1985', place: '太子港', language: '海地克里奧爾文', intro: '以全民母語克里奧爾語譯成的聖經，突破法語獨尊的文字階層。克里奧爾語書面地位的推進器，加勒比草根信仰的母語文本。' },
          { title_zh: '格陵蘭語全本聖經', title_orig: 'Grønlandsk Bibel (1900)', author: '摩拉維亞與丹麥教會譯者', era: '1900', place: '哥本哈根', language: '格陵蘭文', intro: '承埃格德世系補齊舊約的格陵蘭語全本聖經。北極圈語言的完整聖經，極地教會百年譯業的完成。' },
          { title_zh: '卡西安主教新約譯本', title_orig: 'Новый Завет (перевод еп. Кассиана)', author: '卡西安主教（別佐布拉佐夫）', era: '1970', place: '巴黎聖塞爾吉學院', language: '俄文', intro: '巴黎流亡的卡西安主教依批判文本重譯的俄語新約，矯正會議譯本之古。俄僑神學圈的譯經成果，俄語聖經現代化的先聲。' },
          { title_zh: '威克里夫聖經翻譯會與少數語言譯經運動', title_orig: 'Wycliffe Bible Translators / SIL International', author: '金綸‧湯遜創立', era: '1942 起', place: '全球', language: '多語', intro: '湯遜自賣西語聖經受拒於卡奇克爾族起念，創立威克里夫會與 SIL，推動數千語言的識字與譯經。「人人用母語讀經」運動的引擎，當代譯經的最大組織力量。' },
          { title_zh: '翻譯科學探索', title_orig: 'Toward a Science of Translating', author: '尤金‧奈達', era: '1964', place: '萊頓', language: '英文', intro: '奈達以語言學重構翻譯的奠基之作，「形式對等／動態對等」的區分改寫譯經與翻譯學。聖經翻譯理論的世紀原點，現代翻譯學的開山文獻之一。' },
          { title_zh: '聖經翻譯期刊', title_orig: 'The Bible Translator', author: '聯合聖經公會', era: '1950 創刊', place: '倫敦／紐約', language: '英文', intro: '聯合聖經公會的譯經專業期刊，理論與各語個案並載七十餘年。全球譯經者的共同課堂，翻譯理論與田野實踐的交匯檔案。' },
          { title_zh: '聯合聖經公會翻譯手冊系列', title_orig: 'UBS Handbook Series', author: '聯合聖經公會譯經顧問群', era: '1961 起', place: '紐約／斯圖加特', language: '英文', intro: '逐卷指導譯者處理原文難點與譯入語策略的手冊叢書，數十冊覆蓋全聖經。數千個譯本背後的隱形教科書，譯經知識的制度化載體。' },
          { title_zh: 'YouVersion 聖經軟體與數位讀經運動', title_orig: 'YouVersion Bible App', author: '生命教會（格倫謝爾團隊）', era: '2008 起', place: '奧克拉荷馬', language: '多語（逾兩千譯本）', intro: '匯集兩千餘種語言譯本的免費聖經應用，安裝逾五億次，讀經計畫與經文分享重塑日常讀經。數位時代聖經流通的最大平臺，譯本傳播史的新章。' }
        
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
          { title_zh: '眾位弟兄通諭', title_orig: 'Fratelli Tutti', author: '方濟各', era: '2020', place: '梵蒂岡', language: '拉丁文（並廣傳於各語譯本）', intro: '方濟各論「弟兄情誼與社會友愛」的社會通諭，以慈善的撒瑪利亞人比喻為核心意象。通諭呼籲超越國界、宗教與種族的普世手足之愛，譴責民粹主義、戰爭、死刑與排外，倡議建立更具團結與包容的世界政治與經濟秩序。此文深受其與伊斯蘭長老共簽《人類兄弟情誼文件》的啟發，是現代基督教推動跨宗教和平與全球團結的重要宣言。', link: '/encyclicals' },
          { title_zh: '牧放主羊通諭', title_orig: 'Pascendi Dominici Gregis', author: '教宗庇護十世', era: '1907', place: '羅馬', language: '拉丁文', intro: '庇護十世系統譴責「現代主義」為「眾異端之匯」的通諭，隨後設審查與反現代主義誓詞。它凍結天主教批判學術半世紀，梵二前夜的解凍正以此為背景，二十世紀天主教思想史的高壓座標。' },
          { title_zh: '夫至大牧函', title_orig: 'Maximum Illud', author: '教宗本篤十五世', era: '1919', place: '羅馬', language: '拉丁文', intro: '一戰甫終，本篤十五世痛斥宣教淪為殖民工具，令培育本地聖職、勿以傳教謀國家利益。中國首批六位國籍主教七年後祝聖即其果實，天主教宣教「去殖民化」的憲章文件。' },
          { title_zh: '施慰之神通諭', title_orig: 'Spiritus Paraclitus', author: '教宗本篤十五世', era: '1920', place: '羅馬', language: '拉丁文', intro: '紀念耶柔米逝世一千五百年的聖經通諭，重申默感無誤而戒過激批判。它是《上智天主》與《聖神默感》之間的中繼站，天主教聖經學觀念史的必經環節。' },
          { title_zh: '基督君王通諭', title_orig: 'Quas Primas', author: '教宗庇護十一世', era: '1925', place: '羅馬', language: '拉丁文', intro: '庇護十一世創立基督君王節的通諭，宣告基督統治權超越一切世俗政權，直指方興的極權主義與世俗主義。禮儀年新節日承載政治神學宣言的著名案例，墨西哥迫害中殉道者的臨終口號即出於此。' },
          { title_zh: '論基督徒婚姻通諭', title_orig: 'Casti Connubii', author: '教宗庇護十一世', era: '1930', place: '羅馬', language: '拉丁文', intro: '回應蘭柏會議開放節育而頒的婚姻通諭，重申婚姻三善並斥節育、墮胎與優生立法。二十世紀天主教婚姻倫理的基石文件，《論人類生命》的直接前身。' },
          { title_zh: '四十年通諭', title_orig: 'Quadragesimo Anno', author: '教宗庇護十一世', era: '1931', place: '羅馬', language: '拉丁文', intro: '紀念《新事》四十年的社會通諭，首創「輔助原則」一詞並批判自由放任與社會主義兩極。大蕭條中提出「社會秩序重建」藍圖，天主教社會訓導的第二座里程碑。' },
          { title_zh: '燃燒的憂慮通諭', title_orig: 'Mit brennender Sorge', author: '教宗庇護十一世（帕切利與福爾哈伯起草）', era: '1937', place: '羅馬', language: '德文', intro: '以德語寫成、偷運入德國於棕枝主日千座講壇同時宣讀的反納粹通諭，斥種族與國家的偶像化背離信仰。教廷對第三帝國最公開的一擊，蓋世太保翌日全面查抄，通諭史上最戲劇性的一份。' },
          { title_zh: '神聖救贖主通諭', title_orig: 'Divini Redemptoris', author: '教宗庇護十一世', era: '1937', place: '羅馬', language: '拉丁文', intro: '與《燃燒的憂慮》同月頒布的反共通諭，判「無神共產主義」本質上敗壞而不可合作，兼申社會正義方為解毒之方。冷戰前夜天主教反共立場的定調文件，與反納粹通諭合為雙面鋒刃。' },
          { title_zh: '奧秘身體通諭', title_orig: 'Mystici Corporis Christi', author: '教宗庇護十二世', era: '1943', place: '羅馬', language: '拉丁文', intro: '戰火中頒布的教會論通諭，以「基督奧體」重述教會本質，糾正純法制化的教會觀。梵二《教會憲章》的直接鋪路之作，二十世紀教會論復興的官方起點。' },
          { title_zh: '聖神默感通諭', title_orig: 'Divino Afflante Spiritu', author: '教宗庇護十二世', era: '1943', place: '羅馬', language: '拉丁文', intro: '鼓勵據原文與文學類型研究聖經的通諭，被譽為天主教聖經學的「大憲章」，解除《牧放主羊》時代的寒蟬效應。半世紀聖經運動由此奔流，梵二《啟示憲章》的學術前提。' },
          { title_zh: '人類通諭', title_orig: 'Humani Generis', author: '教宗庇護十二世', era: '1950', place: '羅馬', language: '拉丁文', intro: '針對「新神學」與演化論思潮的通諭，容許研究人類身體源於演化而堅守靈魂直造與原祖單一。既戒新潮又留門縫，戰後天主教神學路線之爭的官方仲裁文本。' },
          { title_zh: '廣賜恩寵的天主詔書', title_orig: 'Munificentissimus Deus', author: '教宗庇護十二世', era: '1950', place: '羅馬', language: '拉丁文', intro: '庇護十二世以教宗不可錯誤權欽定聖母靈魂肉身蒙召昇天為信理的詔書，為梵一後此權唯一一次正式行使。聖母敬禮千年傳統的信理化頂點，與各教會對話中最常被檢視的近代定斷。' },
          { title_zh: '慈母與導師通諭', title_orig: 'Mater et Magistra', author: '教宗若望二十三世', era: '1961', place: '羅馬', language: '拉丁文', intro: '若望二十三世的社會通諭，把社會訓導擴及農業、發展中國家與國際失衡，語調由防禦轉為對話。「教會是眾人的慈母與導師」開篇即定其溫度，梵二精神的社會先聲。' },
          { title_zh: '論教會通諭', title_orig: 'Ecclesiam Suam', author: '教宗保祿六世', era: '1964', place: '羅馬', language: '拉丁文', intro: '保祿六世的就職通諭以「對話」為綱：教會與自身、與諸宗教、與世界的三重對話。「對話」自此成為梵二教會的關鍵詞，本諭即其方法論的自我宣告。' },
          { title_zh: '論人類生命通諭', title_orig: 'Humanae Vitae', author: '教宗保祿六世', era: '1968', place: '羅馬', language: '拉丁文', intro: '保祿六世逆專家委員會多數意見重申人工節育不可行的通諭，全球輿論與教會內部異議空前。教宗訓導權與信友良心關係的世紀試金石，其接受史本身即當代天主教的縮影。' },
          { title_zh: '在新世界中傳福音勸諭', title_orig: 'Evangelii Nuntiandi', author: '教宗保祿六世', era: '1975', place: '羅馬', language: '拉丁文', intro: '保祿六世論福傳的宗座勸諭，宣認「教會存在為了福傳」，並首度正式使用「福音與文化」「整體解放」語彙。被歷任教宗譽為梵二後最重要文件，當代宣教神學的天主教定本。' },
          { title_zh: '工作通諭', title_orig: 'Laborem Exercens', author: '教宗若望保祿二世', era: '1981', place: '羅馬', language: '拉丁文', intro: '波蘭教宗在團結工聯風暴之年頒布的勞動通諭，申言「勞動先於資本」、人是勞動的主體。親歷共產與資本兩制的哲學家教宗把人格主義注入社會訓導，勞動神學的當代高峰。' },
          { title_zh: '社會事務關懷通諭', title_orig: 'Sollicitudo Rei Socialis', author: '教宗若望保祿二世', era: '1987', place: '羅馬', language: '拉丁文', intro: '紀念《民族發展》二十年的通諭，直指東西兩集團的「罪的結構」共同壓迫南方，倡「關懷休慼」（solidarity）為德行。冷戰末期的南北問題總診斷，「連帶」概念的訓導定型。' },
          { title_zh: '百年通諭', title_orig: 'Centesimus Annus', author: '教宗若望保祿二世', era: '1991', place: '羅馬', language: '拉丁文', intro: '《新事》百年、柏林圍牆倒塌後的社會通諭，剖析共產失敗的人類學根源，肯定市場而戒「消費主義的資本主義」。後冷戰秩序的天主教判詞，社會訓導百年的總結卷。' },
          { title_zh: '救主的使命通諭', title_orig: 'Redemptoris Missio', author: '教宗若望保祿二世', era: '1990', place: '羅馬', language: '拉丁文', intro: '重申向萬民宣教的永久有效性的通諭，回應「宣教已過時」之說，界定福傳、新福傳與對話的關係。當代天主教宣教學的權威總綱，與 WCC 諸宣言對讀的天主教座標。' },
          { title_zh: '生命的福音通諭', title_orig: 'Evangelium Vitae', author: '教宗若望保祿二世', era: '1995', place: '羅馬', language: '拉丁文', intro: '以「生命文化對抗死亡文化」為軸的通諭，對墮胎與安樂死作近乎信理層級的譴責，並質疑死刑的正當性。當代天主教生命倫理的總憲章，公共論辯中被引用最頻的教宗文件之一。' },
          { title_zh: '信仰與理性通諭', title_orig: 'Fides et Ratio', author: '教宗若望保祿二世', era: '1998', place: '羅馬', language: '拉丁文', intro: '開篇名句「信仰與理性如雙翼，人的精神賴以飛向真理的默觀」。哲學家教宗為形上學與真理問題辯護，兼斥信仰主義與理性主義，二十世紀信理與哲學關係的總結性文件。' },
          { title_zh: '婦女尊嚴牧函', title_orig: 'Mulieris Dignitatem', author: '教宗若望保祿二世', era: '1988', place: '羅馬', language: '拉丁文', intro: '聖母年頒布的論婦女尊嚴與聖召牧函，提出「女性天才」概念並申母性與童貞的雙重榮耀。當代天主教性別神學的基準文本，讚譽與批評皆環繞其「互補」框架。' },
          { title_zh: '致藝術家書', title_orig: 'Lettera agli artisti', author: '教宗若望保祿二世', era: '1999', place: '羅馬', language: '義大利文', intro: '劇作家出身的教宗致全球藝術家的公開信，稱藝術家為「創造主形象的特殊肖像」，籲美成為通往超越的道路。教會與現代藝術百年疏離後的修好之書，「美的福傳」綱領。' },
          { title_zh: '東方之光牧函', title_orig: 'Orientale Lumen', author: '教宗若望保祿二世', era: '1995', place: '羅馬', language: '拉丁文', intro: '讚頌東方基督教傳統的牧函，名言「教會必須用兩肺呼吸」。呼籲拉丁教會向東方的修道、禮儀與神學學習，與《願他們合一》同年而成合一雙璧，東西方修好的抒情文本。' },
          { title_zh: '致家庭書', title_orig: 'Gratissimam Sane (Letter to Families)', author: '教宗若望保祿二世', era: '1994', place: '羅馬', language: '拉丁文', intro: '國際家庭年致全球家庭的長信，以「家庭是教會與社會之路」鋪陳其身體神學與家庭靈修。教宗以家書體裁行使訓導的親切嘗試，家庭牧靈的綱領文件。' },
          { title_zh: '天主是愛通諭', title_orig: 'Deus Caritas Est', author: '教宗本篤十六世', era: '2005', place: '羅馬', language: '拉丁文', intro: '本篤十六世的就職通諭，論愛欲與聖愛的合一及教會慈善的本質，文風如神學家的情書。輿論預期的「鐵衛教宗」以愛開篇，其細膩震動教內外，廿一世紀通諭的文體標竿。' },
          { title_zh: '在希望中得救通諭', title_orig: 'Spe Salvi', author: '教宗本篤十六世', era: '2007', place: '羅馬', language: '拉丁文', intro: '論基督徒盼望的通諭，與馬克思主義及進步主義的救贖觀正面對話，引阮文順獄中經驗為盼望的見證。神學家教宗最個人化的思想結晶，末世論通諭的罕見範例。' },
          { title_zh: '上主的話勸諭', title_orig: 'Verbum Domini', author: '教宗本篤十六世', era: '2010', place: '羅馬', language: '拉丁文', intro: '聖言主教會議後的勸諭，總結《啟示憲章》以來的聖經運動，力倡以聖言誦讀貫穿教會全部生活。當代天主教聖經牧靈的集大成文件，釋經學者教宗的本行之作。' },
          { title_zh: '信德之光通諭', title_orig: 'Lumen Fidei', author: '教宗方濟各（承本篤十六世草稿）', era: '2013', place: '羅馬', language: '拉丁文', intro: '信德年通諭由本篤起草、方濟各完成頒布，「四手聯彈」完成信望愛三部曲。兩任教宗合著的破例文件，教宗更替之際訓導連續性的具體象徵。' },
          { title_zh: '福音的喜樂勸諭', title_orig: 'Evangelii Gaudium', author: '教宗方濟各', era: '2013', place: '羅馬', language: '西班牙文／拉丁文', intro: '方濟各的施政綱領勸諭：教會當是「走出去的教會」，寧要碰傷的教會不要病態自閉的教會，並痛斥「排斥的經濟」。其任期一切改革的路線圖，當代教會最常被引用的文件。' },
          { title_zh: '愛的喜樂勸諭', title_orig: 'Amoris Laetitia', author: '教宗方濟各', era: '2016', place: '羅馬', language: '拉丁文', intro: '兩屆家庭主教會議後的勸諭，以牧靈分辨處理離婚再婚者領聖事等難題，第八章引發樞機「疑問」公開對峙。方濟各牧靈路線最具爭議的文件，當代教會張力的風暴眼。' },
          { title_zh: '親愛的亞馬遜勸諭', title_orig: 'Querida Amazonia', author: '教宗方濟各', era: '2020', place: '羅馬', language: '西班牙文', intro: '亞馬遜主教會議後以四個「夢想」寫成的勸諭：社會的、文化的、生態的與教會的夢。以詩入訓導的文體實驗，原住民教會與生態皈依議程的代表文件。' },
          { title_zh: '讚美天主勸諭', title_orig: 'Laudate Deum', author: '教宗方濟各', era: '2023', place: '羅馬', language: '西班牙文', intro: '《願禰受讚頌》八年後的氣候續篇，直指氣候否認論與技術官僚範式，語氣急切如警鐘。教宗訓導直接介入氣候政治的最新標誌，生態訓導的第二樂章。' },
          { title_zh: '基督徒教育通諭', title_orig: 'Divini Illius Magistri', author: '教宗庇護十一世', era: '1929', place: '羅馬', language: '拉丁文', intro: '論基督徒教育的通諭，申明家庭、教會與國家的教育權序位，抗衡極權國家壟斷青年。天主教教育權利論的經典文件，與法西斯義大利的青年組織之爭互為背景。' },
          { title_zh: '論電影通諭', title_orig: 'Vigilanti Cura', author: '教宗庇護十一世', era: '1936', place: '羅馬', language: '拉丁文', intro: '史上第一道專論電影的通諭，肯定電影的巨大教育潛能並支持美國「端正聯盟」的分級運動。教會面對大眾媒體的首度系統回應，媒體倫理訓導的開山文件。' },
          { title_zh: '信德恩賜通諭', title_orig: 'Fidei Donum', author: '教宗庇護十二世', era: '1957', place: '羅馬', language: '拉丁文', intro: '呼籲歐美教區司鐸志願赴非洲服務的宣教通諭，「信德恩賜司鐸」自此成為跨教區宣教的制度。去殖民化前夜的非洲教會總動員令，天主教宣教人力史的轉轍文件。' },
          { title_zh: '救主之母通諭', title_orig: 'Redemptoris Mater', author: '教宗若望保祿二世', era: '1987', place: '羅馬', language: '拉丁文', intro: '聖母年通諭以「信德的朝聖之旅」重述瑪利亞在救恩史與教會中的地位，兼向東方教會的聖母敬禮致意。「全屬於禰」的教宗其聖母神學的正式陳述，現代聖母論的均衡文本。' },
          { title_zh: '本篤十五世和平照會', title_orig: 'Dès le début (Peace Note)', author: '教宗本篤十五世', era: '1917', place: '羅馬', language: '法文', intro: '一戰膠著中教宗向交戰各國提出的和平方案：裁軍、仲裁、海洋自由與互免賠償，遭雙方同拒而史稱「無用的屠殺」諫言。教廷現代和平外交的開端文件，威爾遜十四點的先聲。' },
          { title_zh: '庇護十二世聖誕文告', title_orig: 'Radiomessaggi natalizi di Pio XII', author: '教宗庇護十二世', era: '1939–1957（尤 1942）', place: '羅馬', language: '義大利文', intro: '庇護十二世歷年聖誕廣播文告，一九四二年篇痛陳「數十萬人僅因民族或血統而被置於死地」，為其對大屠殺最接近點名的公開發言。其措辭之審慎成為「庇護論戰」的核心證物，廣播時代教宗公共言說的代表。' },
          { title_zh: '本篤十六世致中國教會信函', title_orig: 'Lettera ai Cattolici in Cina', author: '教宗本篤十六世', era: '2007', place: '羅馬', language: '中文／義大利文', intro: '本篤十六世致中國天主教徒的牧函，申明教會共融原則、體諒地上地下兩群體的處境，籲修和而不妥協信理。當代中國教會問題的教廷基準文件，中梵關係史的神學座標。' },
          { title_zh: '富於慈悲的天主通諭', title_orig: 'Dives in Misericordia', author: '教宗若望保祿二世', era: '1980', place: '羅馬', language: '拉丁文', intro: '若望保祿二世論天主慈悲的通諭，以浪子比喻重讀救恩史，宣認慈悲是「愛的第二個名字」。承波蘭傅天娜修女的慈悲敬禮而入普世訓導，其後慈悲主日與慈悲禧年皆由此脈絡開展。' }
        
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
          { title_zh: '方濟各與基里爾共同聲明', title_orig: 'Joint Declaration of Pope Francis and Patriarch Kirill', author: '方濟各、莫斯科及全俄羅斯宗主教基里爾', era: '2016', place: '古巴‧哈瓦那', language: '俄文‧義大利文', intro: '羅馬天主教教宗與莫斯科宗主教的首次會晤共同聲明，於古巴哈瓦那簽署，結束了天主教與俄羅斯東正教近千年來最高領袖從未相見的局面。聲明關注中東基督徒所受的迫害、家庭與生命的保護,以及世界和平,並坦誠面對兩教會間的歷史張力。此會晤雖有其政治背景與爭議,仍是現代東西教會關係的重要事件。', link: '/creeds' },
          { title_zh: '拉文納文件', title_orig: 'The Ravenna Document', author: '天主教與正教國際神學對話聯合委員會', era: '2007', place: '拉文納', language: '英文', intro: '天主教與正教就「教會共融、大公會議性與權威」達成的共同文件，首度共同承認普世層級存在首席。羅馬首席權對話的破冰文本，雖俄羅斯代表退席而其框架仍導引至今的對話。' },
          { title_zh: '巴拉曼德聲明', title_orig: 'The Balamand Statement', author: '天主教與正教國際神學對話聯合委員會', era: '1993', place: '黎巴嫩巴拉曼德', language: '英文／法文', intro: '蘇聯解體後東儀教會復出引發衝突，雙方聲明否定「合併主義」為合一模式、承認彼此為姊妹教會。處理四百年「烏尼亞」傷口的關鍵文件，東歐教會地緣張力的神學調停。' },
          { title_zh: '保祿六世與拉姆齊共同宣言', title_orig: 'Common Declaration of Paul VI and Michael Ramsey', author: '保祿六世與坎特伯裡大主教拉姆齊', era: '1966', place: '羅馬', language: '英文', intro: '宗教改革後坎特伯裡大主教首度正式訪問教宗，共同宣言啟動聖公宗-天主教對話（ARCIC）。教宗以自己的主教戒指相贈，四百年隔絕破冰的儀式性文本。' },
          { title_zh: '天主教與亞美尼亞教會共同聲明', title_orig: 'Common Declaration of John Paul II and Karekin I', author: '若望保祿二世與卡列金一世', era: '1996', place: '羅馬', language: '英文', intro: '天主教與亞美尼亞使徒教會就基督論發表共同聲明，確認一千五百年的分歧屬表述而非信仰。迦克墩問題在亞美尼亞一線的正式和解，古老東方對話系列的重要一環。' },
          { title_zh: '信義宗與門諾會和解文件', title_orig: 'Healing Memories: Lutheran-Mennonite Reconciliation', author: '世界信義宗聯會與門諾會世界大會', era: '2010', place: '斯圖加特', language: '英文', intro: '信義宗全球大會為十六世紀迫害再洗禮派正式請求寬恕，門諾會以「我們寬恕」相答，全場跪禱。以悔罪治療五百年記憶的典範儀式文件，大公運動「醫治記憶」方法的最動人案例。' },
          { title_zh: '韋爾比與方濟各共同宣言', title_orig: 'Common Declaration of Pope Francis and Archbishop Justin Welby', author: '方濟各與坎特伯裡大主教韋爾比', era: '2016', place: '羅馬', language: '英文', intro: '紀念教宗與坎特伯裡對話五十年的共同宣言，坦承按立女性與性倫理的新分歧，仍差遣聖公會與天主教主教兩兩結伴出行宣教。「分歧中同行」模式的當代文本。' },
          { title_zh: '巴爾多祿茂環境文告', title_orig: 'Environmental Encyclicals of Patriarch Bartholomew', author: '普世宗主教巴爾多祿茂一世', era: '1997 起', place: '君士坦丁堡', language: '希臘文／英文', intro: '「綠色牧首」巴爾多祿茂歷年環境文告，首創「對受造界犯罪即是罪」的表述，每年九月一日定為受造界祈禱日。正教生態神學的官方聲音，《願禰受讚頌》亦引為先聲。' }
        
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
          { title_zh: '正義的經濟——天主教社會訓導與美國經濟牧函', title_orig: 'Economic Justice for All', author: '美國天主教主教團', era: '1986', place: '美國', language: '英文', intro: '美國天主教主教團發表的重要牧函,將天主教社會訓導的原則應用於美國經濟現況。牧函以人性尊嚴與「對窮人的優先選擇」為準繩,評估貧富差距、失業與貧困問題,呼籲建立更公道的經濟秩序。此文體現現代主教團以集體牧函介入公共政策、為弱勢發聲的傳統,是天主教社會思想在地化、面對具體國情的代表作。' },
          { title_zh: '高俊明獄中書信', title_orig: '高俊明獄中書信', author: '高俊明', era: '1980–1984', place: '臺灣（軍法監獄）', language: '中文', intro: '臺灣基督長老教會總幹事高俊明因美麗島事件藏匿施明德入獄四年餘，獄中致家人與教會的書信堅信「愛與受苦」的信仰路。臺灣民主化與教會史交會的第一手文獻，島嶼的獄中神學。' },
          { title_zh: '倪柝聲獄中家書', title_orig: '倪柝聲獄中家書', author: '倪柝聲', era: '1952–1972', place: '上海提籃橋監獄／安徽白茅嶺', language: '中文', intro: '倪柝聲繫獄二十年間致妻子張品蕙及家人的書信，談病體、問寒暖，信仰只在字縫中隱然。臨終遺紙「我維持我的喜樂」為其絕筆，中國教會受苦世代最靜默的見證文獻。' },
          { title_zh: '希望之路', title_orig: 'Đường Hy Vọng (The Road of Hope)', author: '阮文順', era: '1975–1988', place: '越南（獄中）', language: '越南文', intro: '西貢陷落後被囚十三年的阮文順總主教，在日曆紙背寫下千則短箋由信友傳抄，以「希望之路」召喚地下教會。後任教廷正義和平主席、獲本篤十六世通諭引述，越南教會的獄中靈修經典。' },
          { title_zh: '維辛斯基獄中筆記', title_orig: 'Zapiski więzienne', author: '斯特凡‧維辛斯基樞機', era: '1953–1956', place: '波蘭（軟禁中）', language: '波蘭文', intro: '波蘭首席主教維辛斯基遭共黨軟禁三年的日記與靈修筆記，籌劃將全民族奉獻聖母的「大九日」更新。「千年首席主教」抵抗與韌性的內在紀錄，波蘭教會不屈的心靈檔案。' },
          { title_zh: '吉洪牧首文告', title_orig: 'Послания Патриарха Тихона', author: '莫斯科牧首吉洪', era: '1918–1925', place: '莫斯科', language: '俄文', intro: '新任牧首吉洪絕罰迫害教會者、譴責處決沙皇的歷次文告，及被捕前後的牧函。革命風暴中正教會的公開良心，其軟化與堅持並存的文本群是蘇維埃教會史的第一手核心。' },
          { title_zh: '塞爾吉都主教宣言', title_orig: 'Декларация митрополита Сергия', author: '代理牧首塞爾吉', era: '1927', place: '莫斯科', language: '俄文', intro: '塞爾吉宣告教會對蘇維埃政權忠誠、「你們的喜樂即我們的喜樂」，換取教會殘存的法律地位。地下教會與境外教會因此決裂數十年，順服與背叛之辨的最痛文本。' },
          { title_zh: '認信教會致希特勒備忘錄', title_orig: 'Denkschrift der Bekennenden Kirche an Hitler', author: '認信教會臨時領導層', era: '1936', place: '柏林', language: '德文', intro: '認信教會秘密呈遞希特勒的備忘錄，抗議種族仇恨、集中營與蓋世太保恐怖，外洩後執筆者被捕殉難。教會直諫極權的罕見文件，較公開的巴門宣言更進一步點名罪惡。' },
          { title_zh: '加倫主教反安樂死牧函', title_orig: 'Predigten und Hirtenbriefe des Bischofs von Galen', author: '克萊門斯‧馮‧加倫', era: '1941', place: '明斯特', language: '德文', intro: '「明斯特之獅」加倫主教連續三篇講道牧函公開揭發納粹「安樂死」屠殺病患，抄本隨盟軍傳單飄散全德，政權被迫名義中止 T4 行動。教會公開言說擊退暴政的最著名個案。' },
          { title_zh: '荷蘭主教團抗議驅猶牧函', title_orig: 'Herderlijk schrijven tegen de Jodendeportaties', author: '荷蘭天主教主教團（德容總主教主導）', era: '1942', place: '烏得勒支', language: '荷蘭文', intro: '荷蘭主教團全國宣讀抗議驅逐猶太人的牧函，納粹報復性逮捕改宗天主教的猶太人，埃迪特‧施泰因由此殉難奧許維茲。先知性抗議與其代價的最悲愴案例，教會抵抗史的兩難文本。' },
          { title_zh: '薩利耶主教抗議迫猶牧函', title_orig: 'Lettre pastorale de Mgr Saliège', author: '朱爾‧薩利耶總主教', era: '1942', place: '土魯斯', language: '法文', intro: '土魯斯總主教薩利耶命全教區宣讀的短牧函：「猶太人是人，猶太婦女是人……不可任意加害」。維琪法國教會抵抗的第一聲驚雷，地下抄傳鼓舞救援網絡，義人記憶的典範文獻。' },
          { title_zh: '波德主教團和解書信', title_orig: 'Orędzie biskupów polskich do niemieckich', author: '波蘭主教團（科米內克起草）', era: '1965', place: '羅馬（梵二會場）', language: '德文／波蘭文', intro: '波蘭主教團致德國主教團的和解信，「我們寬恕，並請求寬恕」一語震動兩國，共黨政權發動圍剿。以福音語言重啟波德和解的先驅文件，歐洲記憶政治的教會篇章。' },
          { title_zh: '和平的挑戰牧函', title_orig: 'The Challenge of Peace', author: '美國天主教主教團', era: '1983', place: '華盛頓', language: '英文', intro: '冷戰核對峙高峰美國主教團論戰爭與和平的集體牧函，有條件容忍核威懾而否定核戰爭，起草過程公開聽證。主教團體性訓導介入國防政策的分水嶺，與《正義的經濟》並為姊妹文件。' },
          { title_zh: '羅梅洛牧函', title_orig: 'Cartas pastorales de Óscar Romero', author: '奧斯卡‧羅梅洛', era: '1977–1980', place: '聖薩爾瓦多', language: '西班牙文', intro: '羅梅洛總主教四道牧函漸次申論教會與窮人、暴力與解放，臨終前致美國總統卡特函籲停止軍援。牧函與其廣播講道共構「窮人之聲」，殉道前的完整神學遺囑。' },
          { title_zh: '辛海棉樞機人民力量呼籲', title_orig: 'Radio Appeals of Cardinal Jaime Sin', author: '辛海棉樞機', era: '1986', place: '馬尼拉', language: '英文／他加祿語', intro: '馬可仕竊選後，辛海棉樞機透過天主教電臺呼籲民眾走上 EDSA 大道保護倒戈軍人，百萬人以玫瑰經與鮮花擋下坦克。教會聲音直接觸發不流血革命的世界性案例。' },
          { title_zh: '金大中獄中書信', title_orig: '김대중 옥중서신', author: '金大中', era: '1980–1982', place: '清州監獄', language: '韓文', intro: '死刑陰影下的金大中致家人的獄中家書，密密麻麻寫滿明信片，信仰、讀書與寬恕政敵之志交織。天主教徒政治家的受難文獻，韓國民主化的心靈檔案，後獲諾貝爾和平獎。' },
          { title_zh: '貝里根獄中書信', title_orig: 'Prison Letters of Daniel Berrigan', author: '丹尼爾‧貝里根', era: '1968–1972', place: '丹伯裡聯邦監獄', language: '英文', intro: '耶穌會詩人貝里根因焚毀徵兵檔案入獄的書信與詩文，把反越戰的公民不服從寫成十字架的門徒操練。「凱頓斯維爾九人」的精神文本，美國天主教和平主義的代表文獻。' },
          { title_zh: '畢奧神父書信集', title_orig: 'Epistolario di Padre Pio', author: '畢奧神父（皮耶垂西那）', era: '1910–1968', place: '聖喬凡尼羅通多', language: '義大利文', intro: '五傷嘉布遣會士畢奧神父致神師與屬靈子女的書信四巨冊，記其靈魂暗夜、屬靈爭戰與對告解者的指導。二十世紀最著名神秘者的內在檔案，其封聖案的核心文獻。' },
          { title_zh: '來作我的光', title_orig: 'Come Be My Light', author: '德蕾莎修女（科洛迪耶楚克編）', era: '1929–1994（2007 刊）', place: '加爾各答', language: '英文', intro: '德蕾莎致神師的私信身後刊行，揭露她半世紀的內在黑暗——「天堂彷彿空無」卻笑著服事至死。聖徒與懷疑共存的震撼文獻，改寫世人對信心的想像，當代靈修史的大事件。' },
          { title_zh: '致馬爾科姆論祈禱', title_orig: 'Letters to Malcolm: Chiefly on Prayer', author: 'C.S.路易斯', era: '1964', place: '牛津', language: '英文', intro: '路易斯以致虛構友人的書信體遺作漫談祈禱的困惑：分心、代求與煉淨，坦率如爐邊夜話。護教家卸甲後最柔軟的一部書，書信體靈修的現代典範。' },
          { title_zh: '生存的習慣', title_orig: 'The Habit of Being', author: '弗蘭納裡‧奧康納', era: '1948–1964（1979 刊）', place: '喬治亞米利奇維爾', language: '英文', intro: '奧康納與友人編輯的千封書信，紅斑狼瘡陰影下談寫作、孔雀與聖體，「若聖體只是象徵，就讓它見鬼去」。美國文學最鋒利的天主教心靈自畫像，書信文學的當代經典。' },
          { title_zh: '託爾金書信集', title_orig: 'The Letters of J.R.R. Tolkien', author: 'J.R.R.託爾金', era: '1914–1973（1981 輯）', place: '牛津', language: '英文', intro: '託爾金書信選集自陳《魔戒》為「根本上宗教性與天主教的作品」，致子談聖體為「地上至美」。神話創作與信仰互證的第一手文獻，中土世界的神學註腳。' },
          { title_zh: '致一位修道人的信', title_orig: 'Lettre à un religieux', author: '西蒙娜‧薇依', era: '1942', place: '馬賽／紐約', language: '法文', intro: '薇依向道明會神父裴倫列陳卅五點信仰疑難，自陳愛基督卻止步洗禮之門、願與受苦者同在門外。門檻上的靈魂最誠實的告白，二十世紀信與不信邊界的代表文獻。' },
          { title_zh: '巴特與哈納克公開通信', title_orig: 'Barth–Harnack Briefwechsel', author: '卡爾‧巴特與阿道夫‧馮‧哈納克', era: '1923', place: '柏林（《基督教世界》刊）', language: '德文', intro: '自由神學泰斗哈納克公開十五問質疑辯證神學，巴特逐一作答再往復兩輪。學術神學與啟示神學的世代對決以書信體上演，二十世紀神學轉向的現場記錄。' },
          { title_zh: '巴特致赫羅馬德卡書信', title_orig: 'Brief an Josef Hromádka', author: '卡爾‧巴特', era: '1938', place: '巴塞爾', language: '德文', intro: '慕尼黑危機中巴特致布拉格神學家赫羅馬德卡的公開信，言捷克士兵若抵抗希特勒「亦是為教會而戰」。神學家論正義防衛的爭議文本，其政治神學轉折的標誌信件。' },
          { title_zh: '默頓與米沃什通信集', title_orig: 'Striving Towards Being: The Letters of Thomas Merton and Czesław Miłosz', author: '託馬斯‧默頓與切斯瓦夫‧米沃什', era: '1958–1968', place: '革責瑪尼／柏克萊', language: '英文', intro: '隱修士與流亡詩人十年通信，論冷戰、自然之惡與信仰的可能，彼此坦率互駁。修道院與世界文學的高空對話，兩位二十世紀心靈的互為告解。' },
          { title_zh: '安德希爾靈修書信', title_orig: 'The Letters of Evelyn Underhill', author: '伊夫林‧安德希爾', era: '1907–1941', place: '倫敦', language: '英文', intro: '安德希爾致受導者的靈修指導書信，把密契神學化為家常英語：「把你的宗教當作生活，而非裝飾」。女性平信徒執靈修指導之職的先驅檔案，英語靈修書簡的溫潤典範。' },
          { title_zh: '許格爾致姪女靈修書信', title_orig: 'Letters from Baron Friedrich von Hügel to a Niece', author: '弗里德里希‧馮‧許格爾', era: '1918–1924', place: '倫敦', language: '英文', intro: '天主教現代主義風暴的倖存者許格爾男爵晚年指導姪女的書信，教她「在宗教中保持廣度、深度與幽默」。危機神學家轉為溫柔導師的晚年結晶，靈修指導文學的小經典。' },
          { title_zh: '多蘿西‧戴書信集', title_orig: 'All the Way to Heaven: The Selected Letters of Dorothy Day', author: '多蘿西‧戴', era: '1923–1980', place: '紐約', language: '英文', intro: '天主教工人運動創始人戴的書信，致情人、主教與獄友，貧民收容所的日常與和平主義的堅持交織。「一路都是天堂」的行動靈修檔案，美國激進門徒職的第一手文獻。' },
          { title_zh: '薛華書信集', title_orig: 'Letters of Francis A. Schaeffer', author: '法蘭西斯‧薛華', era: '1948–1984', place: '瑞士拉布裡', language: '英文', intro: '拉布裡團契創辦人薛華答問尋道者的書信選，存在疑惑、婚姻與文化議題逐一懇談。福音派文化護教運動的私人面向，「誠實的答案給誠實的問題」的書信實踐。' },
          { title_zh: '帕伊西奧斯長老書信', title_orig: 'Επιστολές (Γέροντας Παΐσιος)', author: '聖山長老帕伊西奧斯', era: '1966–1994', place: '阿索斯聖山', language: '希臘文', intro: '聖山長老帕伊西奧斯致修道者與平信徒的書信，以農夫的比喻談驕傲、病苦與代禱，二〇一五年封聖。當代正教長老傳統的鮮活文獻，希臘世界最受愛讀的靈修書簡。' },
          { title_zh: '圖圖致總理公開信', title_orig: 'Open Letter to Prime Minister Vorster', author: '戴斯蒙‧圖圖', era: '1976', place: '約翰尼斯堡', language: '英文', intro: '時任約堡座堂主任的圖圖致種族隔離政權總理弗斯特的公開信，預警怒火將至，數週後索韋托起義爆發。先知書信的當代標本，圖圖公共角色的起點文獻。' },
          { title_zh: '卡馬拉文告與書信', title_orig: 'Cartas e pronunciamentos de Dom Hélder Câmara', author: '赫爾德‧卡馬拉', era: '1964–1985', place: '累西腓', language: '葡萄牙文', intro: '巴西「貧民窟主教」卡馬拉在軍政府新聞封殺下以書信與海外演說傳聲，名言「我濟貧被稱聖徒，我問貧因被稱共黨」。非暴力解放路線的代表文獻，拉美教會良心的私人檔案。' },
          { title_zh: '明真諦樞機牧函與文告', title_orig: 'Mindszenty bíboros levelei és nyilatkozatai', author: '明真諦樞機', era: '1945–1975', place: '布達佩斯／美國使館', language: '匈牙利文', intro: '匈牙利首席主教明真諦歷經納粹與共黨兩度監禁、美國使館避難十五年，其牧函與文告貫穿東歐教會的鐵幕歲月。冷戰教會抵抗的象徵人物之文本群，殉道未死的白色殉道檔案。' },
          { title_zh: '辛巴威主教團牧函', title_orig: 'God Hears the Cry of the Oppressed', author: '辛巴威天主教主教團', era: '2007', place: '哈拉雷', language: '英文', intro: '辛巴威主教團於經濟崩潰與鎮壓高峰發表的牧函，直言危機根源是「治理的罪」，政權震怒而教會不撤。當代非洲教會先知性發聲的代表，牧函文類的現役見證。' }
        
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
          { title_zh: '利馬禮文', title_orig: 'Baptism, Eucharist and Ministry (Lima Liturgy)', author: '普世教會協會信仰與教制委員會', era: '1982', place: '秘魯‧利馬', language: '英文', intro: '普世教會協會（WCC）信仰與教制委員會在利馬通過《洗禮、聖餐與聖職》文件時，所附的一份示範感恩崇拜禮文。它嘗試以一套眾教會都能共用的聖餐禮，具體展現合一神學的可能，融會東正教的呼求聖靈（epiclesis）、天主教的獻祭語言與更正教的記念神學。利馬禮文雖無法定地位，卻成為二十世紀合一運動最重要的崇拜象徵，在無數普世聚會中被採用，體現「分裂的教會在同一張桌前」的盼望。' },
          { title_zh: '聖樂自動詔書', title_orig: 'Tra le sollecitudini', author: '教宗庇護十世', era: '1903', place: '羅馬', language: '義大利文／拉丁文', intro: '庇護十世即位首年頒布的聖樂自動詔書，斥劇場風格、復額我略聖詠與帕萊斯特里納複音，並首度使用「主動參與」一語。禮儀運動奉此語為旗幟，半世紀後開花為梵二改革，本詔即二十世紀禮儀更新的起跑槍聲。' },
          { title_zh: '天主的中保通諭', title_orig: 'Mediator Dei', author: '教宗庇護十二世', era: '1947', place: '羅馬', language: '拉丁文', intro: '史上第一道專論禮儀的通諭，肯定禮儀運動的健康路線而戒其考古主義，界定禮儀為「基督奧體的公共敬禮」。它使禮儀更新獲得官方神學基礎，梵二《禮儀憲章》的直接前驅，二十世紀禮儀神學的分水嶺。' },
          { title_zh: '聖週改革禮令', title_orig: 'Ordo Hebdomadae Sanctae instauratus', author: '庇護十二世（禮儀部頒）', era: '1951–1955', place: '羅馬', language: '拉丁文', intro: '庇護十二世先復活夜後全聖週的禮儀改革：守夜禮還於深夜、會眾重新更新聖洗誓願，儀式時辰與參與方式全面重整。這是特倫託以來羅馬禮首次大幅手術，梵二全面改革的試刀之作。' },
          { title_zh: '羅馬彌撒經書總論', title_orig: 'Institutio Generalis Missalis Romani', author: '禮儀部（保祿六世頒）', era: '1969（歷次修訂）', place: '羅馬', language: '拉丁文', intro: '新彌撒經書卷首的總論，以神學敘述代替舊「禮規」的法條體，闡明彌撒各部意義與各職務的參與。它是梵二禮儀神學的濃縮法典，各國彌撒實踐的依據文本，禮儀爭論每每回到其字句。' },
          { title_zh: '時辰祈禱禮', title_orig: 'Liturgia Horarum', author: '禮儀部（保祿六世頒）', era: '1971', place: '羅馬', language: '拉丁文', intro: '梵二後全面重編的日課，四週詩篇循環取代一週誦畢，增教父選讀並邀平信徒共禱。千年修道日課自此改為「天主子民的祈禱」，是禮儀改革中規模最大的文本工程。' },
          { title_zh: '成人入教禮典', title_orig: 'Ordo Initiationis Christianae Adultorum', author: '禮儀部', era: '1972', place: '羅馬', language: '拉丁文', intro: '恢復古代慕道制度的成人入門聖事禮典：分階段的收錄、揀選、考核與復活夜入門聖事，使歸信成為團體伴行的旅程。本禮典重塑全球堂區的福傳形態，是梵二「回歸源頭」原則最成功的落實。' },
          { title_zh: '教會的敬禮', title_orig: 'La piété de l\'Église', author: '朗貝爾‧博杜安', era: '1914', place: '魯汶山頂修道院', language: '法文', intro: '本篤會士博杜安的小冊宣言，主張禮儀本身即是信眾靈修的正途，勿使敬虔淪為私人附加。此書點燃比利時禮儀運動，其「禮儀是教會的祈禱」綱領貫穿至梵二，是禮儀運動的創始文獻。' },
          { title_zh: '敬禮的奧蹟', title_orig: 'Das christliche Kultmysterium', author: '奧多‧卡塞爾', era: '1932', place: '瑪利亞‧拉赫修道院', language: '德文', intro: '本篤會士卡塞爾提出「奧蹟臨在」說：禮儀非紀念過去，而是救恩奧蹟在儀式中的真實臨在。此說重塑二十世紀聖事神學，《禮儀憲章》的奧蹟語言即其迴響，禮儀神學史的哥白尼轉向。' },
          { title_zh: '羅馬禮彌撒溯源', title_orig: 'Missarum Sollemnia', author: '約瑟夫‧榮格曼', era: '1948', place: '因斯布魯克', language: '德文', intro: '耶穌會士榮格曼追溯彌撒每一部分歷史演變的兩卷鉅著，於戰時禁教中寫成。它以史學證明禮儀本是活的發展，為梵二改革提供了學術彈藥，禮儀史研究的二十世紀第一書。' },
          { title_zh: '禮儀的形成', title_orig: 'The Shape of the Liturgy', author: '格雷戈裡‧迪克斯', era: '1945', place: '納什多姆修道院', language: '英文', intro: '聖公會本篤會士迪克斯提出感恩禮的「四重動作」——拿起、祝謝、擘開、分給——為跨宗派禮儀修訂共同採納。名段「自那夜以來，人們何曾停止行此禮」傳誦不絕，英語禮儀學最有影響的一部書。' },
          { title_zh: '基督教崇拜導論', title_orig: 'Introduction to Christian Worship', author: '詹姆斯‧懷特', era: '1980', place: '諾特丹大學', language: '英文', intro: '衛理宗禮儀學家懷特縱覽各傳統崇拜史與神學的教科書，首創新教崇拜傳統的九系分類。本書為北美神學院通用教材數十年，把禮儀學從天主教專科變為普世新教的共同課目。' },
          { title_zh: '拜占庭禮儀簡史', title_orig: 'The Byzantine Rite: A Short History', author: '羅伯特‧塔夫特', era: '1992', place: '羅馬宗座東方學院', language: '英文', intro: '耶穌會東方禮司鐸塔夫特以畢生考據濃縮而成的拜占庭禮發展史，五階段分期成為學界通說。他使東方禮儀史成為嚴格學科，本書是其龐大論著的門戶，東西禮儀互識的橋樑之作。' },
          { title_zh: '薩伊禮彌撒', title_orig: 'Missel Romain pour les diocèses du Zaïre', author: '薩伊主教團（教廷核准）', era: '1988', place: '金夏沙', language: '法文／林加拉語', intro: '教廷正式核准的第一部非洲本地化彌撒：祖先呼請、舞蹈遊行與呼應對答納入羅馬禮框架。剛果教會以之證明「羅馬禮的非洲面孔」可能，是梵二本地化原則最大膽的官方成果。' },
          { title_zh: '菲律賓人民彌撒', title_orig: 'Misa ng Bayang Pilipino', author: '菲律賓主教團禮儀委員會（安斯卡‧丘彭科主持）', era: '1976', place: '馬尼拉', language: '他加祿語', intro: '禮儀學家丘彭科主持起草的他加祿語本地化彌撒，融入菲律賓的敬長禮節與節慶感性，呈教廷審核而長懸未決。它是亞洲禮儀本地化最完整的方案，其起草與擱置本身即本地化張力的教科書案例。' },
          { title_zh: '一九二八年英格蘭提案公禱書', title_orig: 'The Deposited Book (Proposed BCP 1928)', author: '英格蘭教會（國會否決）', era: '1927–1928', place: '倫敦', language: '英文', intro: '英格蘭教會歷二十年修訂的公禱書，因聖餐禮文趨近公教而兩度遭下議院否決，引發「國會可否裁決敬拜」的憲政危機。禮書雖未立法而實際通行，是國教體制與禮儀自主衝突的標誌文件。' },
          { title_zh: '共同崇拜', title_orig: 'Common Worship', author: '英格蘭教會', era: '2000', place: '倫敦', language: '英文', intro: '英格蘭教會取代《替代禮書》的新禮書家族，以多軌選項並存傳統與現代語體，把公禱書傳統帶入多元時代。其「叢書式禮書」形態反映當代禮儀的彈性轉向，聖公宗禮儀史的新章。' },
          { title_zh: '南印度教會聖餐禮文', title_orig: 'The Order for the Lord\'s Supper, Church of South India', author: '南印度教會', era: '1950', place: '馬德拉斯', language: '英文／泰米爾語等', intro: '聖公會、衛理與長老等宗派合一而成的南印度教會所定聖餐禮文，融各傳統精華並採東方禮元素，被譽為二十世紀最佳禮儀創作之一。合一教會的禮文反哺各母會修訂，普世禮儀運動的燈塔。' },
          { title_zh: '路德宗崇拜書', title_orig: 'Lutheran Book of Worship', author: '北美路德宗聯合委員會', era: '1978', place: '明尼亞波利斯', language: '英文', intro: '北美路德宗諸會聯合編訂的崇拜書，恢復每主日聖餐理想與豐富的禮儀年，兼收現代語禱文與聖詩。它是路德宗禮儀復興的里程碑，顯示禮儀運動如何跨越宗派重塑新教主流的敬拜。' },
          { title_zh: '共同敬拜書', title_orig: 'Book of Common Worship (PCUSA)', author: '美國長老教會', era: '1906（1993 大修）', place: '費城／路易維爾', language: '英文', intro: '美國長老教會的敬拜書，自一九〇六年初版突破「無禮文」傳統，至一九九三年版全面吸收禮儀運動成果。改革宗由拒斥禮文到擁抱共同禱文的百年轉身，本書系即其軌跡的文本紀錄。' },
          { title_zh: '中華聖公會公禱書', title_orig: '中華聖公會公禱書', author: '中華聖公會', era: '1932－1957 修訂', place: '上海', language: '中文', intro: '中華聖公會歷經數十年翻譯修訂的中文公禱書，文言與白話並陳，兼採中國節期與祖先追思的調適。它是公禱書傳統漢語化的集成，華人聖公宗禮儀身分的奠基文本，餘緒及於港臺教省禮書。' },
          { title_zh: '天主教漢語彌撒經書', title_orig: '漢語彌撒經書（梵二後譯本）', author: '主教團禮儀委員會（臺港）', era: '1968 起陸續頒行', place: '臺北／香港', language: '中文', intro: '梵二開放母語後，華語主教團陸續譯頒的中文彌撒經書，經文措辭斟酌文白與神學於一爐，「上主，求禰垂憐」自此響於華人祭臺。它是漢語成為正式禮儀語言的歷史文本，華文教會禮儀生活的基石。' },
          { title_zh: '紐西蘭公禱書', title_orig: 'A New Zealand Prayer Book / He Karakia Mihinare o Aotearoa', author: '紐西蘭聖公會', era: '1989', place: '奧克蘭', language: '英文／毛利文', intro: '紐西蘭聖公會的雙語公禱書，毛利語禱文與大地意象貫穿全書，詩篇重譯亦顧及性別語言。它被譽為當代最富詩意的禮書，原住民語言與殖民者語言在祭壇上首度平起平坐的官方文本。' },
          { title_zh: '修訂共同經課表', title_orig: 'Revised Common Lectionary', author: '英語禮儀諮商會', era: '1992', place: '北美／國際', language: '英文', intro: '跨宗派共用的三年主日讀經表，據羅馬《彌撒讀經集》修訂而為聖公、路德、長老、衛理等共同採納。全球數十萬會眾每主日同讀一經，是禮儀合一運動最日常也最深遠的成果。' },
          { title_zh: '禮儀與文化奈洛比宣言', title_orig: 'Nairobi Statement on Worship and Culture', author: '世界信義宗聯會禮儀研究組', era: '1996', place: '奈洛比', language: '英文', intro: '信義宗全球研究計畫的總結宣言，提出敬拜與文化的四重關係：超文化、處境化、反文化、跨文化。四原則成為本地化神學的通用框架，是禮儀本地化討論被引用最多的當代文件。' },
          { title_zh: '亞美尼亞殉道者列聖禮文', title_orig: 'Canonization Service of the Armenian Genocide Martyrs', author: '亞美尼亞使徒教會', era: '2015', place: '埃奇米阿津', language: '古典亞美尼亞文', intro: '大屠殺百週年之日，亞美尼亞教會以四百年來首次列聖禮把一百五十萬殉難者集體宣聖，鐘聲響遍全球亞美尼亞教堂。以禮儀承載民族創傷的當代最大個案，殉道敬禮傳統的莊嚴重啟。' },
          { title_zh: '俄國新殉道者列聖禮文', title_orig: 'Службы новомученикам российским', author: '俄國正教會（境外與莫斯科先後）', era: '1981／2000', place: '紐約／莫斯科', language: '教會斯拉夫文', intro: '蘇聯迫害殉難者的列聖禮文與紀念禮儀，境外教會先行、莫斯科宗主教區於二千年大規模跟進，沙皇一家與千萬無名者同入聖冊。禮文直面二十世紀最大殉道潮，是禮儀回應極權記憶的核心文本。' }
        
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
          { title_zh: '哈利路亞讚美操練(靈恩敬拜)', title_orig: 'Praise & Worship (Charismatic Renewal)', author: '靈恩更新運動', era: '1960年代起', place: '美國‧全球', language: '英文‧多語', intro: '二十世紀中葉興起的靈恩更新運動（Charismatic Renewal），橫掃天主教、聖公會與各更正教宗派，帶來一種以「讚美與敬拜」（Praise & Worship）為核心的崇拜形態。其特徵為自發禱告、舉手、方言、按手醫治，及由短歌串接的長時段敬拜，強調聖靈當下臨在與信徒情感的直接投入。它顛覆了正典禮文的固定結構，催生了當代敬拜音樂產業，並深刻形塑了今日全球福音派與五旬節派的崇拜風貌。' },
          { title_zh: '愛奧那團體敬拜書', title_orig: 'Iona Abbey Worship Book', author: '愛奧那團體', era: '1988（歷次增訂）', place: '蘇格蘭愛奧那島', language: '英文', intro: '麥克勞德重建愛奧那修道院而創的普世團體所編敬拜書，把凱爾特意象、社會公義與日常勞動織入禮文。其「把敬拜帶回街頭」的精神使凱爾特靈修於當代復興，社群禮儀創作的代表文本。' },
          { title_zh: '庫蒂裡耶合一祈禱文獻', title_orig: 'Écrits sur l\'œcuménisme spirituel (Paul Couturier)', author: '保羅‧庫蒂裡耶', era: '1935–1953', place: '里昂', language: '法文', intro: '里昂司鐸庫蒂裡耶把合一祈禱週改造為「照基督所願的合一」共同祈求，使各宗派得以無保留同禱，並倡「看不見的修道院」屬靈網絡。他被尊為屬靈合一運動之父，這批文獻是合一靈修的憲章。' },
          { title_zh: '為了世界的生命', title_orig: 'For the Life of the World', author: '亞歷山大‧施梅曼', era: '1963', place: '紐約聖弗拉基米爾神學院', language: '英文', intro: '施梅曼為青年大會寫的小書，以「人是感恩祭司」重述聖事世界觀：世界即聖禮，俗聖二分才是墮落。本書使正教禮儀神學風行西方，跨宗派讀者奉為聖事靈修的入門經典。' },
          { title_zh: '團契生活', title_orig: 'Gemeinsames Leben', author: '迪特里希‧潘霍華', era: '1939', place: '芬肯瓦爾德', language: '德文', intro: '潘霍華把認信教會地下神學院的共同生活提煉成書：共同晨禱、認罪與代求，戒除對「理想團契」的幻夢之愛。蓋世太保關閉學院後此書問世，是逼迫下操練群體靈修的經典，至今為團契生活的首選讀本。' },
          { title_zh: '屬靈操練禮讚', title_orig: 'Celebration of Discipline', author: '傅士德', era: '1978', place: '美國', language: '英文', intro: '貴格會學者傅士德重新引介默想、禁食、獨處、簡樸等十二項屬靈操練，把古典靈修傳統譯入當代福音派語彙。本書售逾數百萬冊，掀起「靈命塑造」運動，二十世紀後期最具影響力的靈修著作之一。' },
          { title_zh: '靈性操練真諦', title_orig: 'The Spirit of the Disciplines', author: '魏樂德', era: '1988', place: '南加州大學', language: '英文', intro: '哲學教授魏樂德為屬靈操練建立神學根基：恩典不是反對努力、而是反對賺取，身體是靈命的場所。本書與傅士德之作互為表裡，把門徒訓練從決志主義導向生命重塑，靈命塑造運動的理論支柱。' },
          { title_zh: '浪子回頭', title_orig: 'The Return of the Prodigal Son', author: '盧雲', era: '1992', place: '多倫多黎明之家', language: '英文', intro: '盧雲凝視林布蘭名畫兩年而寫成的默想：自認小兒子、驚覺大兒子、終被召成為父親。他自哈佛講席退隱智障者團體的生命轉折貫穿全書，是二十世紀靈修文學最被鍾愛的一部。' },
          { title_zh: '天路客的行囊', title_orig: 'A Long Obedience in the Same Direction', author: '尤金‧畢德生', era: '1980', place: '馬裡蘭', language: '英文', intro: '畢德生以上行之詩十五篇對治「即食文化」的靈性浮躁，題句借尼采語「在同一方向上恆久的順服」。本書確立其牧養靈修學的聲音，緩慢、在地、一生之久的門徒之路自此成為當代靈修的關鍵語彙。' },
          { title_zh: '敞開心靈', title_orig: 'Open Mind, Open Heart', author: '多瑪斯‧基廷', era: '1986', place: '科羅拉多斯諾馬斯修道院', language: '英文', intro: '熙篤會士基廷把《不知之雲》傳統整理為「歸心祈禱」四要領，讓平信徒得以操練默觀。歸心祈禱運動由此風行全球並進入華語教會，是古典默觀民主化的代表文本。' },
          { title_zh: '基督徒默想', title_orig: 'Christian Meditation (The Gethsemani Talks)', author: '若望‧邁恩', era: '1977', place: '倫敦／蒙特婁', language: '英文', intro: '本篤會士邁恩自沙漠教父的短誦傳統恢復「馬拉納塔」默禱法，創立普世基督徒默想團體。其身後運動遍及百餘國，把曼陀羅式的單純專注歸還基督教自身傳統，當代默觀復興的另一主脈。' },
          { title_zh: '崇拜認古識今', title_orig: 'Worship Old and New', author: '羅伯特‧韋伯', era: '1982', place: '惠頓學院', language: '英文', intro: '福音派禮儀學者韋伯呼籲自由教會重拾古教會的聖餐、禮儀年與入門禮，開「古今崇拜」運動與「重返正典傳統」呼聲。本書使無數低禮儀教會重新發現禮儀，福音派敬拜更新的教科書。' },
          { title_zh: '敬拜', title_orig: 'Worship (Evelyn Underhill)', author: '伊夫林‧安德希爾', era: '1936', place: '倫敦', language: '英文', intro: '密契研究名家安德希爾晚年綜論各傳統敬拜的神學與心理，自猶太會堂至貴格靜默逐一同情剖析。女性平信徒執筆的敬拜神學經典，兼具學識與靈觀，英語世界禮儀靈修的常青書。' },
          { title_zh: '沙漠來信', title_orig: 'Lettere dal deserto', author: '卡洛‧卡雷託', era: '1964', place: '撒哈拉沙漠', language: '義大利文', intro: '義大利公教行動領袖卡雷託四十四歲遁入撒哈拉加入耶穌小兄弟會，自沙漠寫回的靈修書信體悟「祈禱即凝視」。本書風行歐洲數十版，把富高的沙漠靈修傳給戰後世代，行動者轉向默觀的經典自述。' },
          { title_zh: '東西方的婚姻', title_orig: 'The Marriage of East and West', author: '比德‧格里菲斯', era: '1982', place: '印度香提凡南靜修院', language: '英文', intro: '本篤會士格里菲斯在印度基督徒靜修院（ashram）四十年的沉思，主張西方理性須與東方直觀成婚方得整全福音。其跨宗教默觀實驗極具爭議亦極富開創，是基督教與印度靈性對話的代表文本。' },
          { title_zh: '渴慕神', title_orig: 'The Pursuit of God', author: '陶恕', era: '1948', place: '芝加哥', language: '英文', intro: '宣道會牧師陶恕在火車上一夜寫就的靈修經典，痛陳福音派「有正確教義而無神的臨在」，召人以全心尋求神自己。本書譯行全球歷久不衰，華語教會亦人手一冊，二十世紀福音派靈修的先知之聲。' },
          { title_zh: '禱告出來的能力', title_orig: 'Power Through Prayer', author: '邦茲', era: '1907', place: '美國田納西', language: '英文', intro: '衛理會牧師邦茲論禱告的傳世小書，開篇即言「教會需要的不是更好的方法，而是更偉大的禱告的人」。其八部禱告著作身後方大行於世，本書為其冠，復興傳統禱告文學的代表。' },
          { title_zh: '禱告', title_orig: 'Fra bønnens verden', author: '奧‧哈勒斯比', era: '1931', place: '奧斯陸', language: '挪威文', intro: '挪威神學家哈勒斯比以「禱告就是讓耶穌進來」重新定義祈禱：無助本身即是禱告的心。作者後因反抗納粹入集中營，本書譯成數十種語言，北歐敬虔傳統給普世教會的最溫柔禮物。' }
        
        ]
      },
      {
        key: 'prayer-devotion',
        label: '祈禱與敬虔部',
        label_en: 'Prayer Books and Devotional Classics',
        desc: '現代祈禱書、靈修日課與普世共禱文獻——自荒漠甘泉、竭誠為主至世界公禱日禮文。',
        works: [
          { title_zh: '荒漠甘泉', title_orig: 'Streams in the Desert', author: '考門夫人', era: '1925', place: '洛杉磯', language: '英文', intro: '宣教士考門夫人於丈夫病榻旁輯成的每日靈修選文，以曠野與溪水意象撫慰苦難中的信徒。中譯本自一九三九年風行華人世界，蔣中正日日批讀尤為著名，是華語圈流傳最廣的靈修日課。' },
          { title_zh: '竭誠為主', title_orig: 'My Utmost for His Highest', author: '章伯斯（遺孀輯錄）', era: '1927', place: '倫敦／開羅', language: '英文', intro: '蘇格蘭教師章伯斯歿於埃及軍中服事後，遺孀以速記講稿輯成的每日靈修，句句刀鋒直指奉獻的徹底。本書百年不絕版，為英語世界最暢銷的靈修日課，「為神捨盡」的屬靈嚴峻主義代表作。' },
          { title_zh: '靈命日糧', title_orig: 'Our Daily Bread', author: '探索事工（RBC）', era: '1956 創刊', place: '大湍城', language: '英文（多語版）', intro: '廣播聖經課事工創刊的季度靈修小冊，每日一文一經一禱，免費索閱而發行數千萬份，華文版遍及全球華人教會。它是二十世紀「靈修小冊」文化的最大品牌，日常讀經運動的隱形推手。' },
          { title_zh: '幽谷之聲', title_orig: 'The Valley of Vision', author: '亞瑟‧貝內特（輯）', era: '1975', place: '愛丁堡', language: '英文', intro: '貝內特自清教徒著作輯出的禱文集，以「山上使我看見幽谷，幽谷使我仰望高山」開篇，重燃當代對清教禱告傳統的熱愛。本書成為改革宗靈修的常備禱本，歷史禱文復興運動的代表。' },
          { title_zh: '私禱日記', title_orig: 'A Diary of Private Prayer', author: '約翰‧貝利', era: '1936', place: '愛丁堡', language: '英文', intro: '愛丁堡神學家貝利為一月三十一日編寫的晨晚禱文，語言典雅而誠摯，兼顧書桌與街市的信仰。本書售逾百萬冊而長銷不衰，展示學院神學家也能寫出全民的禱告書，蘇格蘭敬虔的現代結晶。' },
          { title_zh: '詩篇：聖經的祈禱書', title_orig: 'Das Gebetbuch der Bibel', author: '迪特里希‧潘霍華', era: '1940', place: '柏林', language: '德文', intro: '潘霍華論以詩篇學習祈禱的小書：我們不會禱告，須進入基督的禱告——詩篇即祂的禱詞。此為其生前最後出版物，納粹旋即禁其著述；猶太人的詩篇被高舉之時，正是本書的無聲抗議。' },
          { title_zh: '世界公禱日禮文', title_orig: 'World Day of Prayer Services', author: '世界公禱日國際委員會（各國婦女輪值）', era: '1927 起', place: '全球輪值', language: '多語', intro: '由各國婦女輪流執筆、每年三月首週五全球同步使用的公禱禮文，自美國宣教婦女運動發展為最大的普世祈禱網絡。「知情的禱告、禱告的行動」為其格言，是女性主導普世禮儀創作的百年傳統。' },
          { title_zh: '基督徒合一祈禱週禮文', title_orig: 'Week of Prayer for Christian Unity Services', author: '信仰與教制委員會／宗座合一委員會合編', era: '1908 創始，1966 起合編', place: '日內瓦／羅馬', language: '多語', intro: '每年一月十八至廿五日全球教會共用的合一祈禱禮文，自聖公會華生創始，經庫蒂裡耶轉化，至天主教與世界教協共同編訂。它是分裂教會每年一度的共同呼吸，普世運動最持久的祈禱建制。' },
          { title_zh: '非洲禱文集', title_orig: 'An African Prayer Book', author: '戴斯蒙‧圖圖（編）', era: '1995', place: '開普敦', language: '英文', intro: '圖圖編選的非洲禱文集，自古埃及與衣索比亞禱文、部落口傳禱詞至反種族隔離的呼求，展示「非洲人本是祈禱的民族」。本集把非洲靈修帶入世界讀者的案頭，大公禱告傳統的南方擴容。' },
          { title_zh: '哈普古德正教禮書英譯本', title_orig: 'Service Book of the Holy Orthodox-Catholic Apostolic Church', author: '伊莎貝爾‧哈普古德（譯）', era: '1906', place: '紐約', language: '英文', intro: '美國聖公會學者哈普古德以十年之功譯成的正教禮書英譯，得莫斯科與北美正教會祝福刊行。此書使英語世界首度得窺拜占庭禮全貌，至今仍為通行譯本，一位女性學者搭起的東西禮儀之橋。' }
        
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
          { title_zh: '當代敬拜詩歌選(Hillsong/Bethel/Vineyard)', title_orig: 'Contemporary Worship Music', author: 'Hillsong/Bethel Music/Vineyard 等', era: '1980年代起', place: '澳洲‧美國‧全球', language: '英文‧多語', intro: '源自葡萄園運動（Vineyard）與澳洲新頌教會（Hillsong）等的當代敬拜音樂，以搖滾與流行樂編制取代管風琴與聖詩本，成為全球福音派崇拜的主流聲音。其歌詞重抒情、重個人與神的親密，常以副歌反覆營造敬拜高潮；藉著唱片、版權授權（CCLI）與媒體傳播，形成跨國的崇拜文化工業。此處收其作為二十世紀末至今最具影響力的聖樂現象，其神學深淺與商業化爭議，亦是當代崇拜學的重要課題。' },
          { title_zh: '徹夜禱', title_orig: 'Всенощное бдение (Rachmaninoff)', author: '謝爾蓋‧拉赫瑪尼諾夫', era: '1915', place: '莫斯科', language: '教會斯拉夫文', intro: '拉赫瑪尼諾夫以古俄聖詠為底的無伴奏徹夜禱十五曲，戰時首演即轟動，兩年後革命令其在故土沉寂七十年。作曲家自選第五曲〈主，容你的僕人安然去世〉為己葬禮之樂，俄國教會音樂的至高峰。' },
          { title_zh: '傑隆修斯之夢', title_orig: 'The Dream of Gerontius', author: '愛德華‧埃爾加', era: '1900', place: '伯明罕', language: '英文', intro: '埃爾加以紐曼樞機的臨終靈魂之詩譜成的神劇，天主教的煉獄意象一度令英國座堂卻步，終成英語神劇自《彌賽亞》以來的最高傑作。靈魂過渡的音樂描寫深邃懾人，二十世紀宗教音樂的開卷之作。' },
          { title_zh: '英國聖詩集', title_orig: 'The English Hymnal', author: '珀西‧迪爾默編、佛漢威廉斯音樂主編', era: '1906', place: '倫敦', language: '英文', intro: '佛漢威廉斯任音樂主編的聖詩集，大量採用英格蘭民謠曲調並委創新曲，〈萬古磐石〉之外更有 Sine Nomine 等傳世新聲。它把聖詩音樂水準推至藝術高度，二十世紀英語聖詩集的典範。' },
          { title_zh: 'G小調彌撒', title_orig: 'Mass in G minor (Vaughan Williams)', author: '雷夫‧佛漢威廉斯', era: '1921', place: '倫敦', language: '拉丁文', intro: '自稱不可知論者的佛漢威廉斯為西敏主教座堂詩班寫的無伴奏彌撒，復興都鐸複音而出以現代調式。一戰後的英格蘭在古老聖樂語法中尋得安魂之聲，「懷疑者的彌撒」反成二十世紀禮儀音樂復興的路標。' },
          { title_zh: '詩篇交響曲', title_orig: 'Symphonie de psaumes', author: '伊果‧斯特拉溫斯基', era: '1930', place: '巴黎', language: '拉丁文', intro: '斯特拉溫斯基「為上帝的榮耀」譜寫的合唱交響曲，取拉丁詩篇三段，終樂章的「哈利路亞」如天體靜靜迴轉。新古典的嚴峻與重獲的正教信仰相遇，二十世紀宗教音樂最莊嚴的傑作之一。' },
          { title_zh: '榮耀頌', title_orig: 'Gloria (Poulenc)', author: '法蘭西斯‧普朗克', era: '1959', place: '巴黎', language: '拉丁文', intro: '普朗克喪友歸信後的宗教創作高峰，榮耀頌寫得歡快近乎頑皮，自辯「修士踢足球上帝也喜悅」。神聖與諧趣並存的法式虔敬，與其《加爾默羅會修女對話》同證二十世紀天主教音樂的復興。' },
          { title_zh: '主的誕生', title_orig: 'La Nativité du Seigneur', author: '奧立維耶‧梅湘', era: '1935', place: '巴黎聖三一堂', language: '管風琴曲（法文標題）', intro: '聖三一堂管風琴師梅湘以自創調式與鳥鳴語彙默想道成肉身的九樂章，把神學命題逐一化為音響色彩。他終身以管風琴事奉禮儀，本作是二十世紀禮儀音樂前衛化的里程碑，管風琴文獻的新約。' },
          { title_zh: '戰爭安魂曲', title_orig: 'War Requiem', author: '班傑明‧布瑞頓', era: '1962', place: '考文垂新座堂', language: '拉丁文／英文', intro: '為戰火焚毀重建的考文垂座堂獻堂而作，安魂彌撒經文與歐文的一戰詩並置互刺，德英俄三國獨唱家同臺象徵和解。和平主義者布瑞頓的至高傑作，禮儀文本承載反戰見證的世紀之作。' },
          { title_zh: '彌撒（伯恩斯坦）', title_orig: 'MASS: A Theatre Piece for Singers, Players and Dancers', author: '雷納德‧伯恩斯坦', era: '1971', place: '華盛頓甘迺迪中心', language: '拉丁文／英文', intro: '伯恩斯坦應賈桂琳‧甘迺迪之邀而作的劇場彌撒，搖滾、百老匯與拉丁禮文相撞，司祭在信仰危機中摔碎聖器復又童聲重建。越戰時代信仰動盪的音樂紀念碑，禮儀與劇場邊界的極限實驗。' },
          { title_zh: '奇徹斯特詩篇', title_orig: 'Chichester Psalms', author: '雷納德‧伯恩斯坦', era: '1965', place: '奇徹斯特座堂', language: '希伯來文', intro: '英國聖公會座堂委託猶太作曲家以希伯來原文譜寫詩篇，第二樂章詩篇廿三的童聲與「萬邦為何爭鬧」的怒吼並置。跨信仰委創的經典案例，戰後普世和解精神的音樂結晶。' },
          { title_zh: '路加受難曲', title_orig: 'Passio secundum Lucam (Penderecki)', author: '克里斯多夫‧潘德列茨基', era: '1966', place: '明斯特', language: '拉丁文', intro: '波蘭作曲家潘德列茨基以音簇與嘶喊寫成的受難曲，於共產波蘭公然採宗教題材，紀念奧許維茲的時代創傷隱然其中。前衛語法承載古老受難敘事，鐵幕下宗教音樂不屈的最強音。' },
          { title_zh: '約翰受難曲（帕特）', title_orig: 'Passio Domini nostri Jesu Christi secundum Ioannem', author: '阿福‧帕特', era: '1982', place: '柏林（愛沙尼亞流亡中）', language: '拉丁文', intro: '愛沙尼亞正教徒帕特以自創「鐘鳴風格」寫成的受難曲，全篇如一口鐘的莊嚴擺動，七十分鐘不設高潮而張力不墜。蘇聯流亡者以極簡靜默對抗喧囂，本作使「神聖極簡主義」成為當代聖樂主流。' },
          { title_zh: '羔羊', title_orig: 'The Lamb (Tavener)', author: '約翰‧塔文納', era: '1982', place: '倫敦', language: '英文', intro: '塔文納為姪兒三歲生日以布雷克詩一夕譜成的合唱小品，鏡像和聲純淨如初雪，遂成當代最常演唱的聖誕曲目。皈依正教的作曲家以「聖像式音樂」自許，本曲是其靈性美學最精純的縮影。' },
          { title_zh: '安魂曲（杜魯弗萊）', title_orig: 'Requiem op. 9 (Duruflé)', author: '莫里斯‧杜魯弗萊', era: '1947', place: '巴黎', language: '拉丁文', intro: '管風琴師杜魯弗萊全以額我略聖詠為素材織成的安魂曲，古調浮游於近代和聲之上如香煙繞樑。戰後法國以千年聖歌療傷的代表作，與佛瑞安魂曲並稱法系安魂雙璧。' },
          { title_zh: '多爾西福音歌曲集', title_orig: 'Gospel Songs of Thomas A. Dorsey', author: '湯瑪斯‧多爾西', era: '1932–1965', place: '芝加哥', language: '英文', intro: '藍調樂手多爾西喪妻夭子之夜寫下〈親愛主，牽我手〉，從此開創「福音音樂」之名與文類，芝加哥朝聖浸信會為其基地。黑人教會音樂由靈歌轉入福音時代的開山文獻，金恩喪禮亦唱其歌。' },
          { title_zh: '普天頌讚', title_orig: '普天頌讚（Hymns of Universal Praise）', author: '六公會聯合聖歌委員會（劉廷芳等）', era: '1936', place: '上海', language: '中文', intro: '中華基督教會等六宗派聯合編印的中文聖詩集，收詩五百餘首，趙紫宸譯詞、範天祥配曲的本色聖詩雜然其間。它是華語教會第一部大型聯合聖詩集，本色化聖樂運動的豐碑，修訂版沿用至今。' },
          { title_zh: '臺語聖詩', title_orig: 'Sèng-si（台灣基督長老教會聖詩）', author: '臺灣基督長老教會聖詩委員會', era: '1964（2009 新版）', place: '臺南／臺北', language: '台語（白話字）', intro: '臺灣基督長老教會的臺語聖詩集，承一八七〇年代廈門白話字聖詩傳統，二〇〇九年新版更收原住民與世界詩歌。母語吟唱貫穿禁說方言的年代，是臺語信仰文化與認同的聲音檔案。' },
          { title_zh: '讚美之泉敬拜詩歌集', title_orig: '讚美之泉敬拜讚美專輯', author: '讚美之泉（遊智婷等）', era: '1995 起', place: '洛杉磯', language: '中文', intro: '華人敬拜讚美運動的旗艦事工，自〈讓讚美飛揚〉起發行專輯數十張，曲目傳遍全球華人教會聚會。它把當代敬拜模式漢語化而不失原創，是華語教會音樂世代交替的標誌品牌。' },
          { title_zh: '盧巴彌撒', title_orig: 'Missa Luba', author: '居多‧哈津（與金夏沙少年合唱團）', era: '1958', place: '比屬剛果', language: '拉丁文（剛果曲風）', intro: '比利時方濟會士哈津與剛果歌者以盧巴族即興傳統唱出的拉丁彌撒，全憑鼓聲與人聲，錄音風行世界。梵二前夜非洲音樂已入彌撒的先聲，禮儀本地化最著名的音響見證。' },
          { title_zh: '尼加拉瓜農民彌撒', title_orig: 'Misa Campesina Nicaragüense', author: '卡洛斯‧梅希亞‧戈多伊', era: '1975', place: '索倫蒂納梅群島', language: '西班牙文', intro: '尼加拉瓜民謠歌手戈多伊為農民團體譜寫的彌撒，「你是工人的神、勞動的神」直入信經，蘇慕薩政權旋即查禁。解放神學基層團體的音樂聖典，拉美民眾教會最嘹亮的自我表達。' },
          { title_zh: '克里奧爾彌撒', title_orig: 'Misa Criolla', author: '阿里爾‧拉米雷斯', era: '1964', place: '布宜諾斯艾利斯', language: '西班牙文', intro: '梵二開放母語同年，拉米雷斯即以阿根廷民俗節奏譜成西語彌撒，恰卡雷拉與卡納瓦利托舞曲承載垂憐與羔羊經。首批母語彌撒音樂的代表作，銷行千萬張，拉美認同與禮儀更新的交響。' },
          { title_zh: '你真偉大', title_orig: 'How Great Thou Art (O store Gud)', author: '卜柏格詞、斯圖爾特‧海因英譯', era: '1885 原詩，1949 英譯定型', place: '瑞典／英國', language: '瑞典文／英文', intro: '瑞典牧師卜柏格的雷雨靈感詩，經俄國宣教士海因英譯增節，葛培理佈道大會唱徹全球，屢選為英語世界最愛聖詩之首。一首北歐讚美詩的環球旅程，二十世紀聖詩傳播史的縮影。' },
          { title_zh: '蓋瑟福音歌曲集', title_orig: 'Gaither Gospel Songs', author: '比爾與葛蘿莉亞‧蓋瑟', era: '1964 起', place: '印第安納', language: '英文', intro: '蓋瑟夫婦創作〈因祂活著〉等福音歌曲七百餘首，並以「家庭聚唱」影音把南方福音音樂帶入千萬客廳。戰後美國福音音樂產業化的中心人物，其歌曲已入各語聖詩集，華語教會亦傳唱不輟。' },
          { title_zh: '伯沙撒王的盛宴', title_orig: 'Belshazzar\'s Feast', author: '威廉‧沃爾頓', era: '1931', place: '裡茲音樂節', language: '英文', intro: '沃爾頓以但以理書的宮牆文字譜成的合唱神劇，爵士節奏與雙銅管隊轟然並進，首演即震動英倫。座堂一度以其「野蠻」拒演，終成英語合唱曲目的支柱，聖經敘事音樂的現代爆發。' },
          { title_zh: '大衛王', title_orig: 'Le Roi David', author: '阿蒂爾‧奧涅格', era: '1921', place: '瑞士梅濟耶爾', language: '法文', intro: '瑞士作曲家奧涅格為露天劇場譜寫的「交響詩篇」，敘述者與合唱鋪陳大衛一生，古以色列頌歌與現代和聲交錯。本作使其一夕成名，開二十世紀「敘事神劇」復興之先。' },
          { title_zh: '布達佩斯感恩曲', title_orig: 'Budavári Te Deum', author: '佐爾坦‧科達伊', era: '1936', place: '布達佩斯', language: '拉丁文', intro: '科達伊為布達光復二百五十年而作的感恩曲，馬扎爾民歌音調與帕萊斯特里納式對位熔於一爐。民族樂派與教會傳統互證，匈牙利現代聖樂的代表，其後《匈牙利詩篇》並峙同高。' },
          { title_zh: '格拉高利彌撒', title_orig: 'Glagolská mše', author: '萊奧什‧雅納捷克', era: '1926', place: '布爾諾', language: '教會斯拉夫文', intro: '雅納捷克以古教會斯拉夫語譜寫的彌撒，銅管如雷、管風琴獨奏狂飆，自稱要「向斯拉夫民族的靈魂致敬」。老作曲家的泛神式狂喜與千年禮文相撞，斯拉夫禮儀傳統最桀驁的現代迴響。' },
          { title_zh: '合唱協奏曲', title_orig: 'Концерт для хора (Schnittke)', author: '阿爾弗雷德‧施尼特凱', era: '1985', place: '莫斯科', language: '俄文', intro: '施尼特凱取亞美尼亞聖者納雷克的格列高利《哀歌之書》俄譯為詞的無伴奏合唱協奏曲，於無神論蘇聯公然詠唱千年懺悔詩。俄國合唱傳統與中世紀亞美尼亞靈魂的相遇，晚期蘇聯宗教復甦的音樂事件。' },
          { title_zh: '約翰受難曲（古拜杜麗娜）', title_orig: 'Johannes-Passion (Gubaidulina)', author: '索菲亞‧古拜杜麗娜', era: '2000', place: '斯圖加特', language: '俄文', intro: '韃靼裔女作曲家古拜杜麗娜受巴哈受難曲千禧委創而作，約翰福音與啟示錄雙線並置，末日審判滲入受難敘事。她自言「作曲即是事奉」，本作是女性作曲家在受難曲傳統中的歷史性登場。' },
          { title_zh: '詩篇一百三十', title_orig: 'Psaume 130: Du fond de l\'abîme', author: '莉莉‧布蘭潔', era: '1917', place: '巴黎', language: '法文', intro: '首位獲羅馬大獎的女作曲家莉莉‧布蘭潔臥病譜成的「自深淵」詩篇，管絃如暗潮、女低音自谷底呼求，翌年廿四歲辭世。其姊娜迪亞終身傳其遺音，本作是女性宗教音樂創作的早逝豐碑。' },
          { title_zh: '羔羊經（巴伯）', title_orig: 'Agnus Dei (Barber)', author: '塞繆爾‧巴伯', era: '1967', place: '紐約', language: '拉丁文', intro: '巴伯親手把〈弦樂慢板〉改編為合唱羔羊經，舉世最哀慟的旋律自此有了禮文的名字。自甘迺迪國葬至九一一追悼皆奏此曲，世俗哀樂與禮儀經文互相成全的獨特個案。' },
          { title_zh: '讚美詩（新編）', title_orig: '讚美詩（新編）', author: '中國基督教兩會聖詩委員會', era: '1983', place: '上海', language: '中文', intro: '文革後中國教會重開之初編成的聯合聖詩集，收詩四百首，中國創作近百首，〈平安夜〉與〈茉莉花〉調聖詩並存。它是後三自時代中國教會敬拜的統一聲音，發行數千萬冊的華語第一大聖詩集。' },
          { title_zh: '生命聖詩', title_orig: '生命聖詩（Hymns of Life）', author: '宣道出版社聖詩委員會', era: '1986', place: '香港', language: '中文', intro: '香港宣道出版社編印的華語聖詩集，五百餘首兼收古典聖詩新譯與華人創作，港臺與海外華人福音派教會廣為採用。它與《普天頌讚》分踞華語聖詩的兩大譜系，福音派敬拜傳統的代表選本。' },
          { title_zh: '齊聲歌唱', title_orig: 'Lift Every Voice and Sing II (African American Hymnal)', author: '美國聖公會非裔聖樂委員會', era: '1993（歌 1900）', place: '紐約', language: '英文', intro: '以「黑人國歌」〈齊聲歌唱〉為名的非裔聖公會聖詩集，靈歌、福音音樂與聖公會傳統同冊並列。主流宗派正式接納黑人音樂遺產的標誌文本，禮儀多元化的世代成果。' },
          { title_zh: '肯德里克敬拜詩歌與讚美遊行', title_orig: 'Graham Kendrick Songs / March for Jesus', author: '葛雷肯‧肯德里克', era: '1987 起', place: '倫敦', language: '英文', intro: '英國敬拜創作者肯德里克以〈榮耀歸於至高神〉等詩歌與「為耶穌遊行」運動，把敬拜自禮堂帶上街頭，全球數千萬人參與。當代敬拜音樂與公共見證結合的代表，英式敬拜更新的輸出品牌。' }
        
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
          { title_zh: '沉默', title_orig: '沈黙', author: '遠藤周作(Endō Shūsaku)', era: '1966', place: '日本', language: '日文', intro: '日本天主教作家遠藤周作的長篇小說，以十七世紀禁教時期一名葡萄牙傳教士洛特里哥潛入日本、終至「踏繪」棄教的歷程，叩問神在受苦中的沉默。當信徒因他不肯棄教而受刑，神的緘默逼出全書最深的張力；而最終那「踏下去吧，我比誰都明白你腳的痛」的聲音，把背叛轉化為另一種跟隨。遠藤以「日本這片泥沼」反思基督教在異文化的扎根難題，及軟弱者的信仰。此作被譽為二十世紀最深刻的信仰小說之一，叩擊神義論與文化處境的雙重幽暗。' },
          { title_zh: '權力與榮耀', title_orig: 'The Power and the Glory', author: '格雷厄姆‧葛林', era: '1940', place: '倫敦', language: '英文', intro: '葛林以墨西哥禁教時期為場，寫一名酗酒神父在追捕中屢逃屢返、終為送終告解而赴死。「威士忌神父」成為罪中恩典的文學定像，天主教小說的世紀代表作，教廷一度疑其誨淫而終獲平反。' },
          { title_zh: '事物的核心', title_orig: 'The Heart of the Matter', author: '格雷厄姆‧葛林', era: '1948', place: '獅子山自由城', language: '英文', intro: '西非殖民地警官斯考比因憐憫而通姦、因不忍褻瀆聖體而自盡，憐憫成為他的沉淪之路。葛林把道德神學的兩難寫成悶熱的熱帶悲劇，戰後天主教文學論戰的中心文本。' },
          { title_zh: '慾望莊園', title_orig: 'Brideshead Revisited', author: '伊夫林‧沃', era: '1945', place: '倫敦', language: '英文', intro: '沃以牛津戀慕與貴族莊園的頹美，寫天主教信仰如「看不見的釣線」把浪蕩的弗萊特家一一收回。世俗讀者為其懷舊傾倒，作者自言主題是「恩典的運作」，英國天主教小說的華麗巔峰。' },
          { title_zh: '卿卿如晤', title_orig: 'A Grief Observed', author: 'C.S.路易斯', era: '1961', place: '牛津', language: '英文', intro: '路易斯喪妻後以化名出版的悼亡手記，護教大師坦承信仰在喪慟前如紙屋崩塌，再一磚一瓦重建。理性辯護者的赤裸哀哭反成其最有力的見證，悲傷文學與信仰書寫的現代經典。' },
          { title_zh: '基列家書', title_orig: 'Gilead', author: '瑪麗蓮‧羅賓遜', era: '2004', place: '愛荷華', language: '英文', intro: '垂老的公理會牧師寫給幼子的長信，三代牧職的恩怨與草原小鎮的光影緩緩流過，普立茲獎加冕。羅賓遜以加爾文主義的莊嚴重寫美國文學的心靈，當代基督教小說復興的旗艦之作。' },
          { title_zh: '智血', title_orig: 'Wise Blood', author: '弗蘭納裡‧奧康納', era: '1952', place: '喬治亞州', language: '英文', intro: '退伍青年黑茲爾創立「沒有基督的教會」沿街佈道，愈逃離愈被恩典追獵，終以自瞎苦行收場。奧康納自言為「基督縈繞的南方」作傳，怪誕哥德筆法下的severe mercy，美國天主教文學的利刃。' },
          { title_zh: '鄉村神父日記', title_orig: 'Journal d\'un curé de campagne', author: '喬治‧貝爾納諾斯', era: '1936', place: '法國北部', language: '法文', intro: '胃癌垂死的年輕神父在冷漠的教區日記中掙扎，臨終遺言「一切皆是恩典」。貝爾納諾斯把聖徒性寫成失敗者的隱密光輝，法國天主教文藝復興的代表小說，佈列松改編的電影同為經典。' },
          { title_zh: '毒蛇結', title_orig: 'Le Nœud de vipères', author: '弗朗索瓦‧莫里亞克', era: '1932', place: '波爾多', language: '法文', intro: '守財老律師以遺書向家人傾吐一生的恨，怨毒的長信寫至末頁竟被恩典反轉。諾貝爾獎得主莫里亞克解剖布爾喬亞天主教家庭的偽善與救贖，法語心理小說與信仰書寫的絕頂之作。' },
          { title_zh: '緞子鞋', title_orig: 'Le Soulier de satin', author: '保羅‧克洛岱爾', era: '1929', place: '巴黎', language: '法文', intro: '克洛岱爾以四日跨四洲的巴洛克巨劇寫不可能之愛的獻祭：普蘿艾絲把緞鞋獻給聖母，「使我奔向惡時瘸腿」。世界為舞臺、天使做場記，天主教總體劇場的極限，法國詩劇的世紀高峰。' },
          { title_zh: '貞德慈善之奧秘', title_orig: 'Le Mystère de la charité de Jeanne d\'Arc', author: '夏爾‧佩吉', era: '1910', place: '巴黎', language: '法文', intro: '社會主義者佩吉重返信仰後，以反覆迴旋的禱告式詩劇寫少女貞德對地獄與苦難的不忍。他四年後戰死於馬恩河，本劇是其「希望的小女孩」神學的開端，法國現代宗教詩劇的奠基作。' },
          { title_zh: '克莉絲汀的一生', title_orig: 'Kristin Lavransdatter', author: '西格麗德‧溫塞特', era: '1920–1922', place: '奧斯陸', language: '挪威文', intro: '溫塞特以三部曲寫十四世紀挪威女子克莉絲汀自任性之愛至臨終皈依的一生，中世紀的信仰世界纖毫畢現。本書使她獲諾貝爾獎並皈依天主教，女性視角的宗教史詩小說無出其右。' },
          { title_zh: '大師與瑪格麗特', title_orig: 'Мастер и Маргарита', author: '米哈伊爾‧布爾加科夫', era: '1928–1940（1966 刊）', place: '莫斯科', language: '俄文', intro: '魔鬼造訪無神論的莫斯科，殉道的作家「大師」筆下彼拉多與耶書亞的對話貫穿全書。布爾加科夫焚稿又重寫，「手稿不會燃燒」成為蘇聯地下文學的信條，極權時代最偉大的宗教小說。' },
          { title_zh: '齊瓦哥醫生', title_orig: 'Доктор Живаго', author: '鮑里斯‧帕斯捷爾納克', era: '1957', place: '莫斯科（義大利刊行）', language: '俄文', intro: '醫生詩人齊瓦哥在革命洪流中守護個體生命與愛，卷末廿五首詩以客西馬尼收束全書。小說僅能國外出版，作者被迫拒領諾貝爾獎，福音的生命觀對抗歷史決定論的世紀文本。' },
          { title_zh: '深河', title_orig: '深い河', author: '遠藤周作', era: '1993', place: '東京', language: '日文', intro: '遠藤絕筆長篇，日本旅人各懷創傷同赴恆河，落第神父大津在印度貧民間背負垂死者。自《沉默》的踏繪走到恆河岸邊，遠藤以「洋蔥」稱呼那位陪伴的基督，日本天主教文學的臨終總結。' },
          { title_zh: '冰點', title_orig: '氷点', author: '三浦綾子', era: '1965', place: '旭川', language: '日文', intro: '養女陽子被告知生父是殺女兇手，「你可愛的女兒體內流著罪」的試煉直指原罪與饒恕。主婦三浦綾子以此獲千萬圓懸賞小說首獎，連載風靡全日，戰後日本最成功的基督教大眾小說。' },
          { title_zh: '綴網勞蛛', title_orig: '綴網勞蛛', author: '許地山', era: '1922', place: '北京', language: '中文', intro: '文學研究會作家許地山的短篇名作，棄婦尚潔如蜘蛛補網般默然承受命運，寬恕中自有信仰的靜光。許地山治宗教學而深浸基督教與佛道，本篇是五四文學中罕見的宗教靈性書寫。' },
          { title_zh: '施洗的河', title_orig: '施洗的河', author: '北村', era: '1993', place: '福建', language: '中文', intro: '先鋒派作家北村歸信後的長篇，民國梟雄劉浪自暴虐與虛無中被引到「施洗的河」邊。中國當代文學首見以皈依為敘事核心的嚴肅小說，先鋒文學轉向神聖的標誌文本。' },
          { title_zh: '地毯的那一端', title_orig: '地毯的那一端', author: '張曉風', era: '1966', place: '臺北', language: '中文', intro: '張曉風以婚前寫給未婚夫的散文集成名，把愛情、婚約與感恩寫成向造物者的頌歌，獲中山文藝獎。她一生以基督信仰潤澤中文散文，本書是臺灣文學中信仰與美文合流的起點名作。' },
          { title_zh: '生而為王', title_orig: 'The Man Born to be King', author: '多蘿西‧榭爾絲', era: '1941–1942', place: '倫敦 BBC', language: '英文', intro: '推理女王榭爾絲為 BBC 寫作的十二集耶穌生平廣播劇，讓基督以現代口語開口，播出前輿論嘩然、播出後舉國動容。把福音書寫成戲劇的現代里程碑，路易斯自言每年重讀。' },
          { title_zh: '教堂尖塔', title_orig: 'The Spire', author: '威廉‧戈爾丁', era: '1964', place: '索爾茲伯裡', language: '英文', intro: '諾貝爾獎得主戈爾丁寫中世紀座堂主任喬斯林不顧地基執意加建尖塔，異象與傲慢、獻身與情慾在塔身升高中糾纏崩解。信仰心理的哥德式解剖，英語現代小說中最陡峭的宗教寓言。' },
          { title_zh: '高德里克', title_orig: 'Godric', author: '弗雷德里克‧比克納', era: '1980', place: '佛蒙特', language: '英文', intro: '長老會牧師小說家比克納以中世紀隱士高德里克的臨終回憶寫聖徒性的粗糲：商人、海盜而後隱修者。普立茲獎決選之作，其「聆聽你的生命」的神學貫穿全書，美國信仰文學的秀異之聲。' },
          { title_zh: '布朗神父探案', title_orig: 'Father Brown Stories', author: 'G.K.切斯特頓', era: '1911–1936', place: '倫敦', language: '英文', intro: '其貌不揚的布朗神父憑聽告解識透人心而屢破奇案，「我就是兇手——在心裡」。切斯特頓讓神學洞察成為推理方法，偵探文學史上唯一以恩典為底色的系列，福爾摩斯之外的另一極。' },
          { title_zh: '時間的皺摺', title_orig: 'A Wrinkle in Time', author: '瑪德琳‧蘭歌', era: '1962', place: '紐約', language: '英文', intro: '少女梅格穿越時空自黑暗星球救回父親與弟弟，武器唯有愛。聖公會作家蘭歌把宇宙論與約翰福音的光暗織入少年科幻，獲紐伯瑞獎而屢遭保守派禁書之議，信仰想像文學的現代經典。' },
          { title_zh: '萬聖節前夕', title_orig: 'All Hallows\' Eve', author: '查爾斯‧威廉斯', era: '1945', place: '牛津', language: '英文', intro: '淡墨會成員威廉斯的最後小說，兩名死於空襲的女子遊走倫敦的生死夾層，代禱與「互相內住」的神學化為超自然驚悚。路易斯與託爾金的這位同儕以「靈界驚悚」自成一格，玄秘的都市神學小說。' },
          { title_zh: '末日迷蹤', title_orig: 'Left Behind', author: '提姆‧拉海與傑裡‧詹金斯', era: '1995', place: '芝加哥', language: '英文', intro: '以「被提」後的地球為場的末世驚悚系列首卷，十六冊售逾八千萬，改編電影遊戲俱全。時代論末世觀藉大眾類型小說攻佔暢銷榜，是福音派次文化出版力量的現象級展示，毀譽皆為文化史材料。' },
          { title_zh: '小屋', title_orig: 'The Shack', author: '威廉‧保羅‧楊', era: '2007', place: '奧勒岡', language: '英文', intro: '喪女的父親受邀重返兇案小屋，與化身黑人婦人的天父共度週末。自印小說口耳相傳售逾二千萬冊，三一論的家常化引發神學論戰，廿一世紀信仰大眾閱讀現象的代表個案。' },
          { title_zh: '裸顏', title_orig: 'Till We Have Faces', author: 'C.S.路易斯', era: '1956', place: '牛津', language: '英文', intro: '路易斯自認最成熟的小說，重寫丘比特與賽姬神話：醜陋的姊姊奧璐兒向諸神提出控訴，直到「有了臉」才能面對面。信仰的遮蔽與揭示寫成神話的深度心理劇，其虛構作品的巔峰。' }
        
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
          { title_zh: '當代敬拜詩歌選', title_orig: 'Contemporary Worship Songs', author: '綜合(Graham Kendrick/Matt Redman 等)', era: '1980年代起', place: '英國‧美國‧全球', language: '英文‧多語', intro: '當代敬拜詩歌（Contemporary Worship Songs）以流行與搖滾樂語彙重塑會眾歌唱，肯德里克（Graham Kendrick）的〈萬古磐石為我開〉、瑞德曼（Matt Redman）的〈頌讚之歌〉（10,000 Reasons）等，主導了過去數十年全球教會的崇拜聲音。其歌詞多以第一人稱抒發對神的渴慕與委身，結構簡潔、易於跟唱，藉版權授權系統與媒體跨國流通。此處收其作為當代聖詩的主流形態，其神學取向與商業化張力，亦是現代崇拜詩學的核心議題。' },
          { title_zh: '古舊十架', title_orig: 'The Old Rugged Cross', author: '喬治‧貝納德', era: '1912', place: '密西根', language: '英文', intro: '巡迴佈道家貝納德在奮興會間寫成的十架頌歌，「我要永遠高舉古舊十架，直到見主面」。二十世紀美國最受歡迎的福音聖詩之一，自鄉村教堂唱進貓王的錄音室，十架敬虔的大眾聖歌。' },
          { title_zh: '祂看顧麻雀', title_orig: 'His Eye Is on the Sparrow', author: '西維拉‧馬丁詞、查爾斯‧加布裡埃爾曲', era: '1905', place: '紐約', language: '英文', intro: '馬丁夫人探望臥病友人聞「祂既看顧麻雀，必然看顧我」而成此歌，經黑人教會與埃塞爾‧沃特斯的演唱成為靈魂樂級的信心頌。女性創作、黑人聲音發揚的福音金曲，苦難中盼望的世紀旋律。' },
          { title_zh: '破曉頌', title_orig: 'Morning Has Broken', author: '埃莉諾‧法傑恩詞（蓋爾民謠曲）', era: '1931', place: '倫敦', language: '英文', intro: '童詩作家法傑恩為蓋爾古調填寫的晨光讚美詩，「第一隻鳥鳴，第一道晨光，都自伊甸新造」。一九七一年經卡特‧史蒂文斯翻唱躍居流行榜，聖詩跨入流行文化的著名個案。' },
          { title_zh: '天韻詩歌集', title_orig: '天韻詩歌', author: '天韻合唱團', era: '1963 起', place: '臺北', language: '中文', intro: '救世傳播協會天韻合唱團自創的中文詩歌，〈野地的花〉〈禰真偉大〉的溫柔和聲陪伴數代華人信徒。臺灣本土詩歌創作的先行者，把中文敬拜由譯詞時代帶入原創時代的里程碑。' },
          { title_zh: '迦南詩選', title_orig: '迦南詩選', author: '呂小敏', era: '1990 起', place: '河南', language: '中文', intro: '河南農村姊妹呂小敏未受音樂訓練，自一九九〇年起領受詩歌千餘首，〈中國的早晨五點鐘〉唱遍家庭教會。土地氣息與受苦教會的盼望渾然一體，中國本土聖詩最大的草根創作現象。' },
          { title_zh: '讚美詩學與世界聖詩運動文獻', title_orig: 'Hymn Society / Cantate Domino 文獻', author: '世界聖詩學會群體', era: '1924 起', place: '倫敦／日內瓦', language: '英文（多語）', intro: '英美聖詩學會與普世教協《萬國頌讚》（Cantate Domino）歷版所代表的世界聖詩運動，推動各洲聖詩互譯共用，亞非拉創作進入普世歌本。聖詩由西方出口轉為多向流動的建制見證。' }
        
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
          { title_zh: '現代靈修詩選', title_orig: 'Modern Devotional Poetry', author: '綜合(Denise Levertov/Wendell Berry 等)', era: '二十世紀', place: '美國‧英國‧全球', language: '英文', intro: '二十世紀後半，一群詩人在世俗化的語境中重新探索信仰的詩意。萊弗托夫（Denise Levertov）晚年皈依後寫下〈三位一體之謎〉等沉思之作，貝里（Wendell Berry）以安息日詩篇（Sabbath Poems）將土地、勞作與敬虔融為一體，奧利弗（Mary Oliver）則在自然中聽見禱告。這些詩多不依附特定教派，卻以細膩的觀照與敬畏，重啟現代人對神聖的感知。此處收其作為當代靈修詩的多元面貌，見證詩歌如何在懷疑的時代仍為默想開路。' },
          { title_zh: '時禱書', title_orig: 'Das Stunden-Buch', author: '萊納‧瑪利亞‧裡爾克', era: '1905', place: '巴黎／俄羅斯行旅', language: '德文', intro: '裡爾克託體為俄國修士向「鄰人上帝」的三卷禱告詩，「我繞著上帝、繞著古塔盤旋千年」。承俄羅斯朝聖經驗的神秘詩學，雖溢出教義而滋養無數尋道者，現代德語宗教抒情的起點。' },
          { title_zh: '聖灰星期三', title_orig: 'Ash-Wednesday', author: 'T.S.艾略特', era: '1930', place: '倫敦', language: '英文', intro: '艾略特受洗入聖公會後的首部長詩，自「因我不再盼望回轉」的枯骨中攀上悔改的旋梯。《荒原》的詩人轉身向信，現代主義詩學與古典靈修在此接枝，二十世紀皈依詩的第一文本。' },
          { title_zh: '暫時如此', title_orig: 'For the Time Being: A Christmas Oratorio', author: 'W.H.奧登', era: '1944', place: '紐約', language: '英文', intro: '奧登重返信仰後以聖誕清唱劇體寫成的長詩，希律王的獨白與「暫時如此」的節後平庸直指現代人的信仰處境。知性詩人的道成肉身默想，戰時英語詩最深的神學之作。' },
          { title_zh: '第二空間', title_orig: 'Druga przestrzeń', author: '切斯瓦夫‧米沃什', era: '2002', place: '克拉科夫', language: '波蘭文', intro: '諾貝爾獎得主米沃什九十歲的晚年詩集，追問天堂地獄的「第二空間」何以自現代想像退場，兼以長詩重述奧古斯丁與神學師友。世紀見證者的臨終神學筆記，波蘭宗教詩的高峰收束。' },
          { title_zh: '溪流與藍寶石', title_orig: 'The Stream and the Sapphire', author: '丹尼絲‧萊維托夫', era: '1997', place: '西雅圖', language: '英文', intro: '萊維托夫自選卅八首信仰歷程詩的合集，自懷疑的〈門檻上〉到聖母領報的〈Annunciation〉。猶太裔反戰詩人晚年皈依天主教，本集是美國當代詩壇最坦然的信仰自述。' },
          { title_zh: '安息日詩集', title_orig: 'Sabbaths', author: '溫德爾‧貝裡', era: '1979 起', place: '肯塔基農場', language: '英文', intro: '農夫作家貝裡數十年間每主日獨行林間所得的安息日詩，土地、勞動與復活的盼望循環如四季。農耕靈性與創造神學的詩化實踐，美國生態信仰書寫的長河之作。' },
          { title_zh: '詹寧斯詩集', title_orig: 'Collected Poems of Elizabeth Jennings', author: '伊麗莎白‧詹寧斯', era: '1953–2001', place: '牛津', language: '英文', intro: '「運動派」中唯一的天主教徒詹寧斯以清澈格律寫祈禱、病苦與藝術，貧居牛津而詩行不輟。其宗教詩不設防亦不喧嚷，戰後英國詩壇最持久的信仰聲音之一。' },
          { title_zh: '安納特瑪塔', title_orig: 'The Anathemata', author: '大衛‧瓊斯', era: '1952', place: '倫敦', language: '英文', intro: '威爾斯裔畫家詩人瓊斯以彌撒為框架，把不列顛的地質、傳說與聖杯記憶織成「碎片的獻禮」。奧登譽為世紀英語最佳長詩，天主教聖事想像與現代主義拼貼的孤峰。' },
          { title_zh: '五大頌歌', title_orig: 'Cinq Grandes Odes', author: '保羅‧克洛岱爾', era: '1910', place: '巴黎／天津', language: '法文', intro: '外交官詩人克洛岱爾自繆斯呼喚寫到「一切事物的共融」的五首巨型頌歌，長句如浪湧的「克洛岱爾詩節」自此定型。部分成於中國任所，法語天主教詩的宇宙級呼吸。' },
          { title_zh: '安魂曲（阿赫瑪託娃）', title_orig: 'Реквием', author: '安娜‧阿赫瑪託娃', era: '1935–1961', place: '列寧格勒', language: '俄文', intro: '阿赫瑪託娃為大清洗中獄牆外的母親們寫下的組詩，口耳密傳三十年，〈釘十字架〉一節以聖母立於刑場收束眾母之慟。以受難圖像承載極權創傷的世紀輓歌，俄語詩的良心文本。' },
          { title_zh: '米斯特拉爾宗教詩', title_orig: 'Poemas religiosos de Gabriela Mistral', author: '加夫列拉‧米斯特拉爾', era: '1922–1954', place: '智利／流寓各地', language: '西班牙文', intro: '拉美首位諾貝爾文學獎得主米斯特拉爾的詩浸透聖經與方濟各靈性，《柔情》與《塔拉》詠母性、麵包與十字架。鄉村女教師成為大陸的詩母，西語美洲女性宗教抒情的最高代表。' },
          { title_zh: '八木重吉詩集', title_orig: '八木重吉詩集（秋の瞳・貧しき信徒）', author: '八木重吉', era: '1925–1927', place: '東京近郊', language: '日文', intro: '英語教師八木重吉廿九歲死於結核，遺詩如「我願成為一根蘆笛，讓神吹奏」，短句澄澈近乎祈禱本身。日本基督教詩最純粹的聲音，身後由遺孀守護出版而漸成國民愛讀。' },
          { title_zh: '天空、風、星與詩', title_orig: '하늘과 바람과 별과 詩', author: '尹東柱', era: '1941（1948 刊）', place: '首爾／福岡獄中歿', language: '韓文', intro: '基督徒詩人尹東柱在日治末期寫下「仰望天空一無愧怍」的序詩，因參與朝鮮獨立思想入獄，死於福岡獄中年僅廿七。遺稿友人冒死保存，戰後刊行成為韓國最愛的詩集，殉道詩學的民族聖典。' },
          { title_zh: '桑戈爾詩集', title_orig: 'Poèmes de Léopold Sédar Senghor', author: '利奧波德‧塞達爾‧桑戈爾', era: '1945–1980', place: '達卡／巴黎', language: '法文', intro: '塞內加爾開國總統桑戈爾的詩融黑性運動與天主教感恩於一體，〈向面具祈禱〉與聖詠語調共振。政治家、法蘭西學院院士與詩人三位一體，非洲法語宗教抒情的立國之聲。' },
          { title_zh: '汀克溪畔的朝聖者', title_orig: 'Pilgrim at Tinker Creek', author: '安妮‧迪拉德', era: '1974', place: '維吉尼亞藍嶺', language: '英文', intro: '迪拉德在溪谷一年的觀看筆記，自寄生蜂的殘酷到光的顯現追問造物者的臉，廿九歲獲普立茲獎。自然書寫與否定神學的相遇，「看」作為靈操的當代經典。' },
          { title_zh: '獻給無名的傳道者', title_orig: '獻給無名的傳道者', author: '邊雲波', era: '1948', place: '南京', language: '中文', intro: '大學生邊雲波在時局劇變前夕通宵寫成的長詩，「是自己的手甘心放下世上的享受」，獻給奔赴邊疆的無名傳道人。半世紀間在華人教會傳抄朗誦不絕，中文奉獻詩的第一名篇。' },
          { title_zh: '白馬歌謠', title_orig: 'The Ballad of the White Horse', author: 'G.K.切斯特頓', era: '1911', place: '倫敦', language: '英文', intro: '切斯特頓以阿弗雷德大王抗丹麥的傳說寫成的敘事長詩，聖母對王說「不帶盼望的信心才是喜樂」。二戰時《泰晤士報》引其詩句振奮全國，英語基督教敘事詩的最後一部大歌謠。' },
          { title_zh: '默頓詩集', title_orig: 'The Collected Poems of Thomas Merton', author: '託馬斯‧默頓', era: '1944–1968', place: '革責瑪尼修道院', language: '英文', intro: '隱修士默頓自初期的禮儀詩到晚年反戰與禪意的實驗詩，千頁詩卷與其散文互為呼吸。〈為我兄弟陣亡而作〉諸篇尤見沉痛，二十世紀修道詩的最大結集。' },
          { title_zh: '聖誕詩篇', title_orig: 'Nativity Poems', author: '約瑟夫‧布羅茨基', era: '1962–1995', place: '列寧格勒／紐約', language: '俄文', intro: '布羅茨基自蘇聯時期起幾乎每年聖誕寫一首馬槽詩，流亡不輟，積成跨越卅年的聖誕組詩。猶太裔諾貝爾詩人向伯利恆之星的長年致意，現代詩與道成肉身的持續對話。' },
          { title_zh: '上帝的長號', title_orig: 'God\'s Trombones: Seven Negro Sermons in Verse', author: '詹姆斯‧韋爾登‧約翰遜', era: '1927', place: '紐約', language: '英文', intro: '約翰遜把黑人老派講道人的七篇講章寫成自由體詩，〈創世〉開篇「上帝說：我孤獨——我要造一個世界」。哈林文藝復興向黑人講壇傳統的致敬，非裔美國宗教詩的奠基文本。' }
        
        ]
      },
      {
        key: 'sacred-art-film',
        label: '宗教藝術與影像部',
        label_en: 'Sacred Art, Architecture and Film',
        desc: '二十世紀宗教建築、繪畫、聖像復興、電影與流行音樂——自廊香教堂與羅斯科禮拜堂至德萊葉、塔可夫斯基與基督搖滾。',
        works: [
          { title_zh: '旺斯禮拜堂', title_orig: 'Chapelle du Rosaire de Vence', author: '亨利‧馬蒂斯', era: '1948–1951', place: '法國旺斯', language: '建築與裝飾（法蘭西）', intro: '垂暮的馬蒂斯應曾照護他的道明會修女之請，包辦禮拜堂建築、彩窗、壁繪與祭衣，自稱畢生傑作。黃藍綠三色光洗滌白瓷磚上的簡筆聖像，現代藝術大師獻給信仰的完整空間。' },
          { title_zh: '廊香教堂', title_orig: 'Chapelle Notre-Dame-du-Haut, Ronchamp', author: '勒‧柯比意', era: '1950–1955', place: '法國廊香', language: '建築（法蘭西）', intro: '柯比意在朝聖山丘上以蟹殼屋頂與厚牆光孔造出的小聖堂，理性主義大師交出最神秘的作品。光自深窗斜落如恩典的物理學，二十世紀宗教建築最著名的一座，現代主義與神聖的和解。' },
          { title_zh: '光之教堂', title_orig: '茨木春日丘教会（光の教会）', author: '安藤忠雄', era: '1989', place: '大阪茨木', language: '建築（日本）', intro: '安藤忠雄以清水混凝土圍出黑暗，祭壇整面牆裂開十字形的光。極簡至無一物的會堂讓光本身成為聖像，日本建築對基督教空間最著名的貢獻，貧窮教會預算造出的世界名作。' },
          { title_zh: '巴西利亞主教座堂', title_orig: 'Catedral Metropolitana de Brasília', author: '奧斯卡‧尼邁耶', era: '1958–1970', place: '巴西利亞', language: '建築（巴西）', intro: '尼邁耶以十六根雙曲線混凝土肋骨束成荊冕般的圓冠，會眾自地下甬道升入滿頂藍光。共產黨員建築師為新首都造的天主教座堂，現代主義烏託邦與信仰空間的奇異合體。' },
          { title_zh: '亞穆蘇克羅和平之後大殿', title_orig: 'Basilique Notre-Dame de la Paix', author: '皮埃爾‧法克胡裡（烏弗埃-博瓦尼總統委建）', era: '1985–1989', place: '象牙海岸亞穆蘇克羅', language: '建築（西非）', intro: '象牙海岸總統在故鄉叢林邊緣建成超越聖彼得的世界最大教堂，穹頂彩窗中總統本人隨東方博士朝聖。後殖民非洲的信仰、權力與奢侈之辯全聚於此，二十世紀最具爭議的宗教建築。' },
          { title_zh: '米賽勒勒版畫集', title_orig: 'Miserere (Rouault)', author: '喬治‧魯奧', era: '1922–1927（1948 刊）', place: '巴黎', language: '版畫（法蘭西）', intro: '魯奧以五十八幅深黑銅版把一戰的屍骸、娼妓與小丑同釘於「憐憫」的標題下，基督的臉浮現於受苦者之間。彩窗學徒出身的畫家成為二十世紀最偉大的宗教藝術家，本集是其受難默想的總卷。' },
          { title_zh: '十字若望的基督', title_orig: 'Christ of Saint John of the Cross', author: '薩爾瓦多‧達利', era: '1951', place: '加泰隆尼亞（今藏格拉斯哥）', language: '油畫（西班牙）', intro: '達利據十字若望手繪草圖，自天父的俯角畫十字架懸於加利利湖上，無釘無血、唯有完全的俯身。超現實主義浪子重返信仰題材的代表作，格拉斯哥市民兩度投票把它留在美術館的鎮館之寶。' },
          { title_zh: '白色十字架', title_orig: 'White Crucifixion', author: '馬克‧夏卡爾', era: '1938', place: '巴黎', language: '油畫（俄／法）', intro: '水晶之夜同年，夏卡爾畫披猶太祈禱巾的基督釘於白光中，四周會堂焚燒、難民奔逃。猶太畫家以受難的拉比耶穌控訴迫害，方濟各教宗自言最愛此畫，二十世紀猶太-基督對話的圖像樞紐。' },
          { title_zh: '庫克姆的復活', title_orig: 'The Resurrection, Cookham', author: '斯坦利‧斯賓塞', era: '1924–1927', place: '英格蘭庫克姆', language: '油畫（英格蘭）', intro: '斯賓塞讓死人自故鄉泰晤士河畔教堂墓園紛紛坐起，村民面孔、慵懶陽光，審判如夏日午後。「天堂就在庫克姆」的地方性復活神學，英國現代宗教畫最深情的異象。' },
          { title_zh: '考文垂基督君王掛毯', title_orig: 'Christ in Glory in the Tetramorph', author: '格雷厄姆‧薩瑟蘭', era: '1962', place: '考文垂新座堂', language: '掛毯（英格蘭）', intro: '為戰火重生的考文垂座堂織造的巨幅基督君王掛毯，時為世界最大，與布瑞頓《戰爭安魂曲》同慶獻堂。廢墟十字與新堂榮光並置的和解神學，戰後英國宗教藝術復興的旗艦。' },
          { title_zh: '羅斯科禮拜堂', title_orig: 'Rothko Chapel', author: '馬克‧羅斯科（梅尼爾夫婦委建）', era: '1964–1971', place: '休士頓', language: '繪畫與空間（美國）', intro: '羅斯科為八角禮拜堂繪十四幅近黑巨畫，落成前自盡，空堂遂成無像時代的靜默聖所，開放予一切信仰。抽象表現主義的否定神學空間，當代靈性藝術朝聖的第一站。' },
          { title_zh: '渡邊禎雄聖經版畫', title_orig: '渡辺禎雄聖書版画', author: '渡邊禎雄', era: '1958–1996', place: '東京', language: '型染版畫（日本）', intro: '渡邊禎雄以沖繩紅型與民藝型染技法刻印聖經場景，最後晚餐上壽司、天使著和服。柳宗悅民藝運動結出的基督教果實，其作懸於世界各地教堂，日本本色聖藝的代表。' },
          { title_zh: '法努斯科普特聖像復興', title_orig: 'Neo-Coptic Icons of Isaac Fanous', author: '伊薩克‧法努斯', era: '1960 年代起', place: '開羅', language: '聖像（埃及）', intro: '法努斯融古科普特壁畫、法老正面律與現代設計，創「新科普特聖像」學派，執教神學院培育畫師遍佈僑居教會。千年科普特藝術的二十世紀再生，正教聖像復興的埃及支脈。' },
          { title_zh: '孔託格魯聖像復興', title_orig: 'Icons of Photis Kontoglou', author: '福蒂斯‧孔託格魯', era: '1930–1965', place: '雅典', language: '聖像（希臘）', intro: '小亞細亞難民作家畫家孔託格魯力斥西化甜膩聖像，重返拜占庭嚴格傳統，雅典諸堂壁畫與著述並行。希臘聖像復興之父，其門風隨僑民教會影響普世正教藝術的當代面貌。' },
          { title_zh: '聖女貞德受難記', title_orig: 'La Passion de Jeanne d\'Arc', author: '卡爾‧西奧多‧德萊葉', era: '1928', place: '巴黎', language: '默片（丹麥／法國）', intro: '德萊葉以審判紀錄為本、大特寫貞德臉龐的默片，法爾康涅蒂的面容成為影史受難的定像。膠卷兩度焚毀又奇蹟重現於精神病院儲藏室，宗教電影藝術的開山絕作。' },
          { title_zh: '詞語', title_orig: 'Ordet', author: '卡爾‧西奧多‧德萊葉', era: '1955', place: '丹麥', language: '電影（丹麥）', intro: '德萊葉據牧師劇作家蒙克之劇拍成：自認耶穌的瘋子約翰內斯在孩童的信心旁喚死者復活。影史罕見正面拍攝神蹟而成立的一部，威尼斯金獅加冕，信仰電影的最高峰。' },
          { title_zh: '馬太福音（帕索里尼）', title_orig: 'Il Vangelo secondo Matteo', author: '皮埃爾‧保羅‧帕索里尼', era: '1964', place: '義大利南部', language: '電影（義大利）', intro: '馬克思主義者帕索里尼以非職業演員、紀實鏡頭逐句拍攝馬太福音，題獻若望廿三世。教廷影評名列最佳宗教電影，無信者拍出最忠實的福音書，意識形態與聖言相遇的奇蹟。' },
          { title_zh: '鄉村牧師日記（佈列松）', title_orig: 'Journal d\'un curé de campagne (film)', author: '羅伯特‧佈列松', era: '1951', place: '法國', language: '電影（法蘭西）', intro: '佈列松以禁慾的「模特兒」表演法改編貝爾納諾斯小說，日記畫外音與空鏡承載恩典的不可見。「一切皆是恩典」的結尾黑幕十字，開創電影的超驗風格，宗教電影美學的教科書。' },
          { title_zh: '安德烈‧盧布廖夫（塔可夫斯基）', title_orig: 'Андрей Рублёв', author: '安德烈‧塔可夫斯基', era: '1966', place: '莫斯科', language: '電影（蘇聯）', intro: '塔可夫斯基以中世紀聖像畫家盧布廖夫的沉默與重拾畫筆，追問暴力世界中藝術與信仰何為。蘇聯當局封禁多年，結尾自黑白轉入聖三一像的彩色，影史最偉大的宗教史詩。' },
          { title_zh: '十誡（奇士勞斯基）', title_orig: 'Dekalog', author: '克里斯多夫‧奇士勞斯基', era: '1988', place: '華沙', language: '電視電影（波蘭）', intro: '奇士勞斯基以華沙一座公寓樓的十個故事對應十誡，誡命化為現代倫理的深水區。戒嚴後波蘭的道德焦慮盡入鏡中，電視電影而登影史殿堂，十誡傳統最深刻的當代詮釋。' },
          { title_zh: '冬之光', title_orig: 'Nattvardsgästerna', author: '英格瑪‧柏格曼', era: '1963', place: '瑞典', language: '電影（瑞典）', intro: '牧師之子柏格曼拍攝信仰失落的鄉村牧師在正午聖餐前的三小時，「上帝的沉默」三部曲的核心。教堂司事以受難的「被離棄」重釋十架一幕為神學名場面，懷疑年代的信仰電影經典。' },
          { title_zh: '第七封印', title_orig: 'Det sjunde inseglet', author: '英格瑪‧柏格曼', era: '1957', place: '瑞典', language: '電影（瑞典）', intro: '十字軍騎士與死神在瘟疫海岸對弈，向沉默的天空索求一個記號。柏格曼把中世紀壁畫的死亡之舞搬上銀幕，「與死神下棋」成為文化原型，存在主義宗教電影的座標原點。' },
          { title_zh: '生命樹', title_orig: 'The Tree of Life', author: '泰倫斯‧馬力克', era: '2011', place: '德州', language: '電影（美國）', intro: '馬力克以約伯記開篇，把五〇年代德州家庭的喪子之慟嵌入宇宙創生的巨觀蒙太奇，「自然之道與恩典之道」的低語貫穿。坎城金棕櫚之作，當代影壇最大膽的神學電影。' },
          { title_zh: '密陽', title_orig: '밀양 (Secret Sunshine)', author: '李滄東', era: '2007', place: '韓國密陽', language: '電影（韓國）', intro: '喪子的母親在教會找到安慰，卻在探監時聽兇手說「上帝已赦免我」而崩潰。李滄東把廉價恩典與饒恕的主權問題拍成利刃，全度妍摘坎城影后，亞洲電影對基督教最鋒利的提問。' },
          { title_zh: '人神之間', title_orig: 'Des hommes et des dieux', author: '札維耶‧波瓦', era: '2010', place: '法國（阿爾及利亞事件）', language: '電影（法蘭西）', intro: '重演一九九六年阿爾及利亞提比希林修道院七位熙篤會士面對恐怖威脅仍留守至殉道的抉擇，晚餐一場以天鵝湖配樂靜默告別。坎城評審團大獎，修道聖召與跨宗教友愛的當代聖像。' },
          { title_zh: '耶穌受難記', title_orig: 'The Passion of the Christ', author: '梅爾‧吉勃遜', era: '2004', place: '好萊塢／義大利', language: '電影（亞蘭語／拉丁語）', intro: '吉勃遜以亞蘭語拉丁語重現受難最後十二小時，血腥寫實引發神學與反猶爭議，全球票房逾六億美元。教會包場成現象，宗教電影市場力量的世紀證明，受難默想傳統的爭議性銀幕化。' },
          { title_zh: '耶穌傳電影', title_orig: 'The JESUS Film', author: '學園傳道會（約翰‧海曼製作）', era: '1979', place: '以色列實景', language: '電影（英文原版，逾二千語配音）', intro: '按路加福音逐節拍攝的耶穌生平電影，經學園傳道會譯配逾兩千種語言、放映於叢林村落與難民營，觀看人次號稱數十億，金氏紀錄的史上最多譯本電影。電影作為宣教工具的極致個案。' },
          { title_zh: '十誡（德米爾史詩片）', title_orig: 'The Ten Commandments (1956)', author: '塞西爾‧B‧德米爾', era: '1956', place: '好萊塢／埃及實景', language: '電影（美國）', intro: '德米爾以特藝彩色重拍出埃及史詩，紅海分開的特效成為影史奇觀，年年復活節電視重播成美國民俗。聖經史詩片類型的帝王之作，冷戰時代「自由對抗暴政」的銀幕聖經。' },
          { title_zh: '賓虛（1959 電影）', title_orig: 'Ben-Hur (1959)', author: '威廉‧惠勒', era: '1959', place: '好萊塢／羅馬影城', language: '電影（美國）', intro: '惠勒改編華萊士小說的巨製，戰車競技一場影史留名，基督始終只以背影與手勢出現。十一座奧斯卡的紀錄保持者之一，聖經史詩片黃金時代的頂點。' },
          { title_zh: '只是探訪這星球', title_orig: 'Only Visiting This Planet', author: '拉里‧諾曼', era: '1972', place: '倫敦／洛杉磯', language: '搖滾專輯（美國）', intro: '「基督搖滾之父」諾曼的代表專輯，「魔鬼憑什麼獨佔好音樂」的宣言開創耶穌運動的音樂革命。長髮抱電吉他唱末世與街頭，本作入選國會圖書館典藏，當代基督教音樂產業的創世記。' },
          { title_zh: '約書亞樹', title_orig: 'The Joshua Tree', author: 'U2', era: '1987', place: '都柏林', language: '搖滾專輯（愛爾蘭）', intro: 'U2 以詩篇語彙寫成的美國沙漠之旅，「我仍未尋見我所尋找的」被牧師與樂評同時講道。四位團員中三人的信仰貫穿詞曲，售逾兩千五百萬張，搖滾主流中最著名的靈性專輯。' },
          { title_zh: '萬世巨星', title_orig: 'Jesus Christ Superstar', author: '安德魯‧洛伊‧韋伯與提姆‧萊斯', era: '1970–1971', place: '倫敦／百老匯', language: '搖滾音樂劇（英國）', intro: '以猶大視角重唱受難週的搖滾歌劇，先出唱片後登舞臺，抗議與朝聖者同聚劇院門口。基督形象進入流行文化的引爆點，其詰問式的耶穌詮釋至今仍在神學課堂與劇場並演不衰。' },
          { title_zh: '瑪哈莉亞‧傑克森福音錄音', title_orig: 'Mahalia Jackson Gospel Recordings', author: '瑪哈莉亞‧傑克森', era: '1947–1971', place: '芝加哥', language: '福音音樂錄音（美國）', intro: '「福音歌后」傑克森堅拒演唱世俗音樂，〈Move On Up a Little Higher〉售逾百萬張，並在金恩「我有一個夢」演說前獻唱。黑人教會的聲音登上世界舞臺，福音演唱藝術的世紀典範。' }
        
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
          { title_zh: '每日研經叢書', title_orig: 'The Daily Study Bible', author: '巴克萊（William Barclay）', era: '一九五三–一九五九年', place: '英國格拉斯哥', language: '英文', intro: '巴克萊為平信徒撰寫的新約逐卷研經叢書，文字曉暢、廣納古典與文化背景，將深奧經文化為日用靈糧。全套涵蓋新約各卷，譯成多國語言、流通數千萬冊，是二十世紀普及解經最具影響力的著作之一，深刻塑造了現代信徒每日讀經的習慣。' },
          { title_zh: '鍾馬田羅馬書講道集', title_orig: 'Romans: An Exposition (D. Martyn Lloyd-Jones)', author: '鍾馬田', era: '1955–1968 講；1970 年代起刊行', place: '倫敦西敏教堂', language: '英文', intro: '鍾馬田在倫敦西敏教堂逐節講解羅馬書十三年，週五晚講道結集十四巨冊，把清教徒式的解經講道推向二十世紀高峰。他以醫生轉任傳道人的縝密論證聞名，此集是二十世紀講解式講道（expository preaching）的標竿之作，深刻影響全球福音派講壇。' },
          { title_zh: '講道與講道者', title_orig: 'Preaching and Preachers', author: '鍾馬田', era: '1971', place: '倫敦／費城', language: '英文', intro: '鍾馬田在西敏神學院的十六篇講座結集，開卷即言「講道是教會最迫切的需要」，力主講道是「邏輯著火」（logic on fire），反對以輔導與活動取代講壇。本書是二十世紀最具影響力的講道學著作之一，至今為各宗派傳道人的案頭書。' },
          { title_zh: '巴特監獄講道集', title_orig: 'Den Gefangenen Befreiung', author: '卡爾‧巴特', era: '1954–1959', place: '巴塞爾監獄', language: '德文', intro: '神學巨擘巴特晚年幾乎只在巴塞爾監獄向囚犯講道，這批講章語言平白、篇幅短小，把《教會教義學》的恩典神學化為對「真正會眾」的直接宣告。巴特自言在囚犯中才找到最誠實的聽眾，本集是辯證神學落地為牧養言說的最動人見證。' },
          { title_zh: '潘霍華講道選集', title_orig: 'Predigten Dietrich Bonhoeffers', author: '潘霍華', era: '1928–1944', place: '巴塞隆納／柏林／倫敦／芬肯瓦爾德', language: '德文', intro: '潘霍華自巴塞隆納副牧時期至認信教會地下神學院的講道存稿，貫穿其「廉價恩典」批判與抵抗神學的形成。芬肯瓦爾德時期對詩篇與受難經文的講章尤見深沉，講壇與刑場之間的一致性使這批講道成為二十世紀最有重量的宣講文本。' },
          { title_zh: '富司迪講道選', title_orig: 'Sermons of Harry Emerson Fosdick', author: '富司迪', era: '1922–1946', place: '紐約河濱教會', language: '英文', intro: '自由派講壇泰斗富司迪的講道選，一九二二年〈基要派能得勝嗎〉一講引爆美國基要派與現代派之爭，成為二十世紀最著名的單篇講道之一。他開創「以講道作群體輔導」的問題導向講法，執掌河濱教會講壇廿年，塑造了美國主流新教的宣講風格。' },
          { title_zh: '當代講道藝術', title_orig: 'Between Two Worlds: The Art of Preaching in the Twentieth Century', author: '斯托得', era: '1982', place: '倫敦', language: '英文', intro: '斯托得以「在聖經世界與現代世界之間搭橋」界定講道職分，綜論講道的神學根據、預備方法與講員操守。本書出自倫敦諸靈堂數十年講壇經驗，被譯成多種語言，是福音派講道學公認的當代經典，中譯本亦廣為華人神學院採用。' },
          { title_zh: '摩根西敏講壇講道集', title_orig: 'The Westminster Pulpit (G. Campbell Morgan)', author: '坎伯‧摩根', era: '1904–1917', place: '倫敦西敏教堂', language: '英文', intro: '「解經王子」坎伯‧摩根執掌西敏教堂時期的講道十卷本，逐卷聖經的講解式講道使無數平信徒重拾讀經熱忱。摩根不曾受正規神學訓練，全憑苦讀成家，其講章結構嚴整、綱目分明，成為二十世紀講解講道的範式，亦深刻影響其繼任者鍾馬田。' },
          { title_zh: '積極講道與現代心靈', title_orig: 'Positive Preaching and the Modern Mind', author: '福賽斯', era: '1907', place: '倫敦哈克尼學院', language: '英文', intro: '公理會神學家福賽斯的耶魯講道講座，斷言「講道若死，基督教亦死」，主張講道是福音自身的延續行動而非修辭表演。他以十字架的客觀救贖對抗當時的感傷自由主義，被譽為「英語世界的巴特先聲」，本書至今仍是講道神學的必讀文本。' },
          { title_zh: '加德納‧泰勒講道集', title_orig: 'The Words of Gardner Taylor', author: '加德納‧泰勒', era: '1948–1998 講；2000 結集', place: '紐約布魯克林', language: '英文', intro: '被《時代》稱為「美國講壇院長」的黑人浸信會牧師泰勒的講道全集六卷，融莎士比亞式修辭與黑人教會的節奏傳統於一爐。他執掌布魯克林協和浸信會四十二年，講壇聲望橫跨種族與宗派，本集是非裔美國講道藝術的最高紀念碑。' },
          { title_zh: '力量去愛', title_orig: 'Strength to Love', author: '馬丁‧路德‧金恩', era: '1963', place: '美國亞特蘭大／蒙哥馬利', language: '英文', intro: '金恩牧師親自編訂的講道集，收〈愛你的仇敵〉〈作個徹底的不隨波逐流者〉等名篇，把非暴力抗爭的神學根基以講壇語言鋪陳。本書出版於伯明翰運動之年，證明民權運動的引擎是黑人教會的講道傳統，是二十世紀講道與社會變革互證的第一文本。' },
          { title_zh: '呼喊正義：圖圖講道演說集', title_orig: 'Hope and Suffering: Sermons and Speeches', author: '戴斯蒙‧圖圖', era: '1983', place: '約翰尼斯堡', language: '英文', intro: '圖圖任約翰尼斯堡首位黑人聖公會主教前後的講道與演說集，於種族隔離高壓下宣講「上帝不是基督徒、但必然站在受壓者一邊」的盼望。這批講章使講壇成為南非唯一未被封殺的抗議空間，見證宣講如何承載一個民族的苦難與盼望。' },
          { title_zh: '講道人生', title_orig: 'The Preaching Life', author: '芭芭拉‧布朗‧泰勒', era: '1993', place: '美國喬治亞州', language: '英文', intro: '美國聖公會女司鐸芭芭拉‧布朗‧泰勒的講道自述與講章合集，以文學性的細膩觀照日常中的神聖。她被譽為英語世界最出色的在世講道者之一，本書是女性進入講壇傳統後的代表性文本，展示講道作為觀看世界之道的另一種可能。' },
          { title_zh: '如無權柄者講道', title_orig: 'As One Without Authority', author: '傅瑞德‧克拉多克', era: '1971', place: '美國奧克拉荷馬／亞特蘭大', language: '英文', intro: '克拉多克針對權威式三點講道的失效，提出「歸納式講道」：讓聽眾與講員一同經歷發現的旅程。本書掀起北美講道學的「新講道學」革命，重塑二十世紀後期的講壇形態，被評為百年來最重要的講道學著作之一。' },
          { title_zh: '講道的情節', title_orig: 'The Homiletical Plot', author: '尤金‧勞瑞', era: '1980', place: '美國堪薩斯', language: '英文', intro: '勞瑞主張講道是「時間中的事件」而非觀唸的堆疊，提出「翻轉—深化—轉折—經歷福音—預期後果」的敘事五環（勞瑞圈）。本書與克拉多克同為新講道學的雙璧，把敘事學引入講壇設計，影響遍及各宗派的講道教學。' },
          { title_zh: '宣講的傳承', title_orig: 'Heralds of God', author: '詹姆斯‧斯圖爾特', era: '1946', place: '愛丁堡', language: '英文', intro: '蘇格蘭長老會講道家斯圖爾特的沃拉克講座，戰後向疲憊的世代重申講道者為「上帝的傳令官」。其文字燃燒著蘇格蘭講壇的熱誠傳統，兼具學識與靈火，與其講道集《風隨意思而吹》同為二十世紀中葉英語講道的巔峰見證。' },
          { title_zh: '使徒宣講及其發展', title_orig: 'The Apostolic Preaching and its Developments', author: '陶德', era: '1936', place: '劍橋', language: '英文', intro: '新約學者陶德辨析新約中的「宣講」（kerygma）與「教導」（didache），重構使徒宣講的原始綱要，主張教會的講道當回到這一福音核心。本書的 kerygma 概念支配二十世紀中葉的新約研究與講道神學，是聖經學術直接重塑講壇的經典案例。' },
          { title_zh: '布特裡克講道學講座', title_orig: 'Homiletic: Moves and Structures', author: '大衛‧布特裡克', era: '1987', place: '納什維爾範德堡大學', language: '英文', intro: '布特裡克以「語言如何在群體意識中成形」為起點，將講道分解為連續的「語步」（moves），建構現象學取向的講道學體系。全書體大思精，是二十世紀末講道理論最具野心的綜合，與新講道學諸家共同改寫了講壇的文法。' },
          { title_zh: '黑人講道', title_orig: 'Black Preaching', author: '亨利‧米切爾', era: '1970', place: '美國羅徹斯特', language: '英文', intro: '米切爾首度以學術專著系統闡述黑人講道傳統：呼應唱和、音樂性語調（whooping）、敘事想像與群體參與。本書使長期被主流講道學忽視的黑人講壇獲得理論地位，開黑人講道學研究之先河，影響及於講道教學的多元轉向。' },
          { title_zh: '安東尼‧布魯姆講道集', title_orig: 'Sermons of Metropolitan Anthony of Sourozh', author: '安東尼‧布魯姆都主教', era: '1950–2003', place: '倫敦', language: '英文／俄文', intro: '俄國流亡醫生出身的索羅什都主教安東尼在倫敦牧養俄僑與英語會眾半世紀，其講道不用講稿，以臨在與靜默中的直言著稱。講章結集後風行東西方，把東正教的祈禱神學帶入現代都市講壇，是二十世紀正教宣講的代表聲音。' },
          { title_zh: '施梅曼廣播講道集', title_orig: 'Celebration of Faith: Radio Liberty Talks', author: '亞歷山大‧施梅曼', era: '1953–1983', place: '紐約（向蘇聯廣播）', language: '俄文', intro: '正教禮儀神學家施梅曼三十年間每週透過自由電臺向鐵幕內的蘇聯聽眾廣播短講，以無法公開信仰的億萬人為會眾。這批廣播講章平易而深邃，索忍尼辛亦自承受惠，是冷戰時代「向沉默教會宣講」的獨一無二文獻。' },
          { title_zh: '根基的動搖', title_orig: 'The Shaking of the Foundations', author: '保羅‧田立克', era: '1948', place: '紐約協和神學院', language: '英文', intro: '田立克的第一部講道集，〈你被接納了〉一篇以存在主義語言重述因信稱義，成為二十世紀最常被徵引的講章之一。他自言講道是其神學的試金石——若不能宣講便不是真神學，本集展示系統神學家如何向現代人的焦慮直接說話。' },
          { title_zh: '彼得‧馬歇爾講道與禱文集', title_orig: 'Mr. Jones, Meet the Master', author: '彼得‧馬歇爾', era: '1949', place: '華盛頓', language: '英文', intro: '蘇格蘭移民、美國參議院院牧彼得‧馬歇爾的講道與禱文集，在其猝逝後出版即成全國暢銷書。其講道以戲劇性的具象語言把福音講給政要與平民，參議院禱文短而鋒利，本集見證了戰後美國公共生活中講道聲音的黃金時刻。' }
        
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
          { title_zh: '阿蘇薩街復興記述', title_orig: 'The Azusa Street Revival Accounts', author: '西摩（William J. Seymour）等', era: '一九〇六–一九〇九年', place: '美國洛杉磯', language: '英文', intro: '一九〇六年起於洛杉磯阿蘇薩街使徒信心會的靈恩復興運動之講道與見證記述，以方言、醫治與跨種族敬拜為特徵。此復興被視為二十世紀全球五旬節運動的源頭，其佈道熱情與屬靈經驗論述深刻影響了往後遍及各洲的靈恩派宣教，故列入大型佈道與復興部。' },
          { title_zh: '託雷佈道講章集', title_orig: 'Revival Addresses (R. A. Torrey)', author: '託雷', era: '1902–1911', place: '芝加哥／世界巡迴', language: '英文', intro: '慕迪的接班人託雷率詩班環球佈道，足跡遍及澳洲、印度、中國與英倫，所到之處掀起決志浪潮。其佈道講章邏輯縝密、訴諸意志，代表福音佈道由營火式激情轉向法庭式論證的世代，本集是二十世紀初「環球佈道」時代的言語標本。' },
          { title_zh: '比利‧桑戴佈道講章', title_orig: 'Billy Sunday Sermons', author: '比利‧桑戴', era: '1896–1935', place: '美國各巡迴佈道城市', language: '英文', intro: '職棒球員出身的桑戴以俚語、肢體與烈火般的禁酒講道橫掃美國城市，一場佈道動輒數萬人，其〈酒吧講道〉助推禁酒令入憲。講章俗白潑辣，精英嗤之而百姓擁戴，是美國大眾佈道文化與進步時代社會運動交纏的代表文本。' },
          { title_zh: '麥艾梅四方福音講道集', title_orig: 'Sermons of Aimee Semple McPherson', author: '麥艾梅', era: '1923–1944', place: '洛杉磯安吉利斯堂', language: '英文', intro: '五旬節女佈道家麥艾梅在洛杉磯安吉利斯堂以戲劇化「圖解講道」與廣播電臺向大眾宣講「四方福音」——救主、醫治者、施浸者、再來王。她是美國第一批擁有廣播執照的女性，其講章集是女性主導大型佈道與媒體宣教的開創性見證。' },
          { title_zh: '威爾斯大復興信息與見證', title_orig: 'The Welsh Revival: Messages and Testimonies', author: '伊凡‧羅伯茨等', era: '1904–1905', place: '威爾斯', language: '威爾斯文／英文', intro: '一九〇四年威爾斯大復興中礦工青年伊凡‧羅伯茨的簡短信息、禱詞與當時報刊見證的輯錄。復興以詩歌與認罪代替講道技巧，一年內十萬人歸信，並成為阿蘇薩街等全球五旬節運動的直接火種，這批文獻是二十世紀復興浪潮的起點紀錄。' },
          { title_zh: '東非大復興見證與信息', title_orig: 'The East African Revival: Testimonies and Addresses', author: '巴洛柯雷弟兄會眾（盧安達／烏干達）', era: '1930 年代起', place: '盧安達／烏干達／肯亞', language: '盧干達語／史瓦希里語／英文', intro: '始於一九三〇年代盧安達差會醫院的東非大復興（巴洛柯雷，「得救的人」）以公開認罪、破除部族藩籬與「行在光中」的團契著稱，信息多出非洲信徒之口。其見證與講章輯錄是非洲人主導的復興運動最重要文獻，影響直達盧安達種族滅絕後的和解事工。' },
          { title_zh: '吉善宙講道集', title_orig: '길선주 설교집', author: '吉善宙', era: '1907–1935', place: '平壤章臺峴教會', language: '韓文', intro: '朝鮮首批按立牧師之一吉善宙為一九〇七年平壤大復興的靈魂人物，首倡黎明禱告會與通聲祈禱，其講道融儒道修養傳統與啟示錄的末世盼望。他亦是三一獨立運動民族代表，講道集見證韓國教會復興靈性與民族苦難的深度交織。' },
          { title_zh: '帕勞佈道信息集', title_orig: 'Mensajes de Luis Palau', author: '路易‧帕勞', era: '1966–2018', place: '阿根廷／拉丁美洲各城', language: '西班牙文', intro: '阿根廷佈道家帕勞承葛培理之風而以西語世界為場，城市佈道節橫跨拉美、伊比利與亞洲，聽眾累計數千萬。其信息集以家庭與盼望為軸，展示福音大眾佈道在拉丁美洲土壤的本色形態，標誌全球佈道領導權向南方轉移的先聲。' },
          { title_zh: '邦克非洲佈道信息集', title_orig: 'Evangelistic Messages of Reinhard Bonnke', author: '雷茵哈德‧邦克', era: '1975–2017', place: '奈及利亞等非洲諸國', language: '英文', intro: '德國佈道家邦克的「非洲當得救」運動在撒哈拉以南舉行露天佈道會，拉哥斯單場聚會逾百萬人，登記決志累計七千餘萬。其信息集以神蹟醫治與簡明福音為特色，是二十世紀末非洲五旬節化浪潮中大型佈道現象的核心文獻。' },
          { title_zh: '如疾風烈火：印尼復興紀實', title_orig: 'Like a Mighty Wind', author: '梅爾‧塔裡', era: '1971', place: '印尼帝汶', language: '英文（印尼見證）', intro: '印尼帝汶青年塔裡親歷一九六五年後印尼大復興的見證錄：赤足佈道隊深入村落，伴隨認罪、醫治與異象，數十萬穆斯林與泛靈信仰者歸信。本書風行世界而也引發查證爭論，是東南亞本土復興運動最廣為人知的第一身敘述。' },
          { title_zh: '山東大復興紀實', title_orig: 'The Shantung Revival', author: '庫爾佩珀', era: '1933', place: '山東', language: '英文', intro: '美南浸信會宣教士庫爾佩珀記述一九三〇年代山東煙臺、黃縣一帶的大復興：認罪、醫病與宣教士自身的更新，挪威女宣教士孟瑪麗的禱告事奉為其先導。山東復興被視為浸信會史上罕見的五旬節式經歷，本書是其最直接的一手紀錄。' },
          { title_zh: '孟瑪麗復興見證錄', title_orig: 'The Awakening: Revival in China (Marie Monsen)', author: '孟瑪麗', era: '1927–1932 事；1959 結集', place: '河南／山東', language: '挪威文／英文', intro: '挪威女宣教士孟瑪麗以「你重生了嗎」一問走遍華北教會，掀起認罪悔改的復興浪潮，被尊為山東復興的「點火者」。本見證錄自述其禱告、質問式佈道與海盜船上蒙保守的經歷，是女性宣教士塑造中國教會屬靈傳統的重要文獻。' },
          { title_zh: '西摩使徒信心會信條與講章', title_orig: 'The Doctrines and Discipline of the Azusa Street Apostolic Faith Mission', author: '威廉‧西摩', era: '1915', place: '洛杉磯阿蘇薩街', language: '英文', intro: '阿蘇薩街復興領袖、黑人聖潔會牧師西摩晚年編訂的信條與講章，重申復興的核心不在方言而在愛裡合一，並痛陳運動內的種族裂痕。本書長期湮沒後重刊，是全球五旬節運動創始人自己的神學聲音，於運動史具正本清源之義。' },
          { title_zh: '我信神蹟', title_orig: 'I Believe in Miracles', author: '凱瑟琳‧庫爾曼', era: '1962', place: '匹茲堡', language: '英文', intro: '醫治佈道家庫爾曼記述其聚會中醫治見證的成名作，她主持全美電視節目、坐滿卡內基音樂廳與洛杉磯神殿禮堂數十年。庫爾曼強調「我沒有醫治恩賜，只有聖靈」，本書是戰後美國醫治復興運動與女性佈道領袖的代表文獻。' },
          { title_zh: '奧羅‧羅伯茨醫治佈道信息', title_orig: 'Healing Messages of Oral Roberts', author: '奧羅‧羅伯茨', era: '1947–1985', place: '土爾沙／全美帳幕巡迴', language: '英文', intro: '羅伯茨以萬人帳幕與按手行列開創戰後醫治復興，率先把佈道會搬上電視，「期待神蹟」成為其標語。其信息集展示五旬節信仰如何經電子媒體進入美國主流，兼為「種子信心」教導的源頭，影響及於全球靈恩運動的形態。' },
          { title_zh: '生命值得活', title_orig: 'Life Is Worth Living', author: '富爾頓‧辛', era: '1952–1957', place: '紐約（全國電視）', language: '英文', intro: '天主教總主教富爾頓‧辛的全國電視講道節目講稿，以一襲紫袍、一塊黑板向三千萬觀眾講述信仰與現代生活，收視力壓同時段娛樂節目並獲艾美獎。本集證明大眾媒體佈道非新教專利，是天主教進入美國公共文化的里程碑。' },
          { title_zh: '標竿人生', title_orig: 'The Purpose Driven Life', author: '華理克', era: '2002', place: '加州馬鞍峰教會', language: '英文', intro: '馬鞍峰教會主任牧師華理克的四十天靈程書，以「你為何而活」發起全教會運動式研讀，銷逾三千萬冊、譯成百餘種語言，成為廿一世紀初最大規模的佈道出版現象。其小組動員模式重塑了福音派的佈道與教會增長實踐。' }
        
        ]
      },
      {
        key: 'chinese-preaching',
        label: '漢語宣道部',
        label_en: 'Chinese Preaching',
        desc: '華人教會自立講壇的講道、奮興佈道與講道學——自王明道、宋尚節至滕近輝、唐崇榮的漢語宣講傳統。',
        works: [
          { title_zh: '重生真義', title_orig: '重生真義', author: '王明道', era: '1933', place: '北平', language: '中文', intro: '王明道申論重生非入教儀文、乃生命更換的佈道名著，以直截的白話與嚴峻的聖潔要求，向掛名教徒發出當頭棒喝。他在北平自建基督徒會堂、自編《靈食季刊》，本書代表華北自立教會講壇的神學骨氣，影響中國家庭教會屬靈傳統至深。' },
          { title_zh: '宋尚節奮興佈道講章', title_orig: '宋尚節奮興佈道講章', author: '宋尚節', era: '1931–1940', place: '中國各省／南洋', language: '中文', intro: '「中國的衛斯理」宋尚節於伯特利佈道團及其後獨立奮興的講章紀錄，以醫病、認罪與十字架的血為軸，佈道足跡遍中國與南洋，帶起十萬計信徒與數千佈道隊。講章語言熾烈直指人心，是二十世紀華人奮興運動的核心文獻。' },
          { title_zh: '完全救法', title_orig: '完全救法', author: '賈玉銘', era: '1945 前後', place: '南京／上海', language: '中文', intro: '中國神學教育先驅賈玉銘的培靈講道系列，以「靈命神學」講解救恩的完全：稱義、成聖以至得榮，融奮興講壇與系統教義於一體。賈氏執教金陵、創靈修學院，此集代表中國教會自建講壇神學的成熟之作。' },
          { title_zh: '神的工人', title_orig: '神的工人', author: '楊紹唐', era: '1940 年代', place: '山西／南京', language: '中文', intro: '楊紹唐在靈修院訓練同工的講章結集，論工人的呼召、破碎與十字架道路，語調溫厚而剖析入骨。他創「靈工團」推動本土佈道，兼顧教會建造與工人靈命，本書為華人教會「工人先於工作」屬靈傳統的代表文本。' },
          { title_zh: '計志文佈道講章集', title_orig: '計志文佈道講章集', author: '計志文', era: '1931–1970 年代', place: '上海／南洋／美國', language: '中文', intro: '伯特利佈道團創始人之一計志文的佈道講章，其團五年間行程五萬裡、領人歸主數以萬計，戰後更創中國佈道會遍設孤兒院與教會於東南亞。講章以罪、血、悔改為綱，質樸有力，是華人自主跨國佈道事業的第一手言語遺產。' },
          { title_zh: '天國君王：馬太福音講義', title_orig: '天國君王——馬太福音講義', author: '陳終道', era: '1964 起', place: '香港／加拿大', language: '中文', intro: '陳終道《新約書信讀經講義》系列之馬太福音卷，以華人牧者的講壇實感逐段講解，重視上下文與生活應用。其讀經講義全套風行華人教會半世紀，為無數傳道人的解經案頭書，代表華人講解式講道的成熟傳統。' },
          { title_zh: '唐崇榮佈道神學講座集', title_orig: '唐崇榮神學講經講座信息', author: '唐崇榮', era: '1980 年代起', place: '雅加達／全球華人城市', language: '中文', intro: '印尼華僑佈道家唐崇榮以「歸正福音運動」為旗，數十年間於全球華人城市舉行神學講座式佈道，聽眾累計數千萬人次，講題自罪與救贖至文化哲學批判。其講座集把加爾文主義神學帶入大眾佈道現場，是華人世界獨樹一幟的宣講形態。' },
          { title_zh: '路標', title_orig: '路標（滕近輝講道集）', author: '滕近輝', era: '1970 年代', place: '香港宣道會北角堂', language: '中文', intro: '滕近輝牧養香港北角宣道會數十年間的講道結集，以清晰綱目與屬靈洞察指引信徒人生方向，故名「路標」。他兼任神學教育與宣教推動，是戰後香港教會講壇的標誌人物，此集流傳華人教會甚廣，培育了整代信徒領袖。' },
          { title_zh: '周聯華講道選集', title_orig: '周聯華講道選集', author: '周聯華', era: '1954–2016', place: '臺北凱歌堂／懷恩堂', language: '中文', intro: '臺灣浸信會牧師周聯華牧養懷恩堂逾半世紀，兼在凱歌堂為蔣氏家族證道，人稱「宮廷牧師」而自守平民本色。其講道選集融學術釋經與時代關懷，語多幽默而終歸懇切，是臺灣戰後教會講壇史的代表文獻。' },
          { title_zh: '講道法', title_orig: '講道法（陳崇桂）', author: '陳崇桂', era: '1934', place: '長沙／重慶', language: '中文', intro: '陳崇桂為中國教會早期自著講道學教本的代表，論講章結構、取材與講員操守，出自其創辦湖南聖經學校與重慶神學院的教學實踐。此書使講道學在華語神學教育中自成一科，見證中國教會由受教於宣教士轉向自訓工人的歷程。' },
          { title_zh: '趙世光佈道講章集', title_orig: '趙世光佈道講章集', author: '趙世光', era: '1940–1970 年代', place: '上海／香港／南洋', language: '中文', intro: '靈糧堂創辦人趙世光的佈道講章，戰亂中以「靈糧」為號在上海創堂，後建立遍及港臺與東南亞的靈糧堂體系，自任環球佈道。講章以靈奶餵養初信、以異象激勵教會，是華人自立宗派佈道傳統的重要文獻。' }
        
        ]
      },
      {
        key: 'mission-periodicals',
        label: '宣教刊物與調查部',
        label_en: 'Mission Periodicals and Surveys',
        desc: '差會機關報、教會報刊、宣教統計調查與年鑑——宣道運動的媒體與數據見證。',
        works: [
          { title_zh: '臺灣教會公報', title_orig: '台灣教會公報（Tâi-oân Kàu-hōe Kong-pò）', author: '臺灣基督長老教會', era: '1885 創刊，1900 年代起持續發行', place: '臺南', language: '台語白話字／中文', intro: '巴克禮創刊的《臺灣府城教會報》為臺灣史上第一份報紙，以臺語白話字印行，後易名《臺灣教會公報》發行至今。它承載教會消息、白話字教育與臺灣社會的百年記憶，戒嚴時期屢遭查禁仍持續發聲，是本土教會報刊的活化石。' },
          { title_zh: '教務雜誌', title_orig: 'The Chinese Recorder', author: '在華宣教士群體', era: '1867–1941', place: '福州／上海', language: '英文', intro: '在華新教宣教士的共同論壇，刊載宣教方法論戰、譯名之爭、教育醫療報告與中國社會觀察七十餘年。自本色化教會至反教運動皆留下第一手討論，是研究中國基督教史與中西文化交流無可替代的期刊檔案。' },
          { title_zh: '萬國公報', title_orig: 'A Review of the Times（萬國公報）', author: '林樂知主編', era: '1868–1907', place: '上海', language: '中文', intro: '美國監理會宣教士林樂知創辦主編的中文時務報刊，由教會新報轉型為紹介西學、時政與基督教義的綜合媒體，梁啟超、康有為皆受其啟迪。它是宣教出版介入晚清維新思潮的最著名個案，發行量冠絕當時中文報刊。' },
          { title_zh: '使徒信心報', title_orig: 'The Apostolic Faith (Azusa Street)', author: '阿蘇薩街使徒信心會', era: '1906–1908', place: '洛杉磯', language: '英文', intro: '阿蘇薩街復興的機關報，免費寄往全球最高達五萬份，報導方言、醫治與各地復興消息，讀者按報上見證尋來洛杉磯再把火帶回本國。這份簡陋小報是五旬節運動全球擴散的關鍵媒介，現存各期為運動起源的核心史料。' },
          { title_zh: '國際宣教評論', title_orig: 'International Review of Mission', author: '國際宣教協會／世界教協', era: '1912 創刊', place: '愛丁堡／日內瓦', language: '英文', intro: '愛丁堡會議的直接產物，百餘年來刊載宣教神學、各洲教會報告與年度宣教研究書目，自歐德姆至紐畢真皆曾主編。期刊名自「missions」改為單數「mission」的一字之變，正記錄了宣教觀念由西方差傳到上帝宣教的世紀轉向。' },
          { title_zh: '中華歸主', title_orig: 'The Christian Occupation of China', author: '中華續行委辦會調查特委會', era: '1922', place: '上海', language: '中文／英文', intro: '歷時四年、覆蓋全國的基督教事業統計調查，以地圖與圖表呈現各省教會、學校、醫院分佈，中文版題名《中華歸主》。它是二十世紀初最大規模的宣教普查，出版即逢非基運動衝擊，其數據至今為中國基督教史研究的基準線。' },
          { title_zh: '世界宣教地圖集', title_orig: 'World Missionary Atlas', author: '國際宣教協會（貝奇主編）', era: '1925', place: '紐約', language: '英文', intro: '國際宣教協會編纂的全球宣教統計地圖集，逐國羅列差會、宣教站、教育醫療機構與信徒數據，附大幅彩色地圖。它承接一九一〇年愛丁堡的普查傳統，是兩戰之間世界基督教版圖的權威快照，為宣教統計學的里程碑。' },
          { title_zh: '穆斯林世界期刊', title_orig: 'The Muslim World', author: '茲維默創刊', era: '1911 創刊', place: '哈特福', language: '英文', intro: '茲維默為穆斯林宣教創辦的學術季刊，兼載伊斯蘭研究與宣教通訊，逾百年不輟，今由哈特福神學院續刊為伊斯蘭與基督教關係研究重鎮。期刊自身的轉型——由宣教喉舌到對話平臺——濃縮了基督教面對伊斯蘭態度的百年演變。' },
          { title_zh: '億萬華民', title_orig: 'China\'s Millions', author: '中國內地會', era: '1875 創刊，1900 年代起續刊', place: '倫敦／上海', language: '英文', intro: '戴德生創辦的中國內地會機關月刊，以宣教士書信、內地見聞與代禱呼籲動員英語世界，義和團殉道報導尤震動人心。刊物首創「信心差會」的公開徵信模式，不募款而列需要，是宣教媒體史與中西認知史的重要文本。' },
          { title_zh: '倫敦傳道會宣教記事', title_orig: 'The Chronicle of the London Missionary Society', author: '倫敦傳道會', era: '1867–1966', place: '倫敦', language: '英文', intro: '倫敦傳道會的機關月刊，報導其在華南、印度、非洲與太平洋諸島的宣教事工，馬禮遜與利文斯敦傳統的後繼敘事俱在其中。百年刊史記錄了差會由帝國時代到去殖民時代的自我調整，是差會期刊文類的代表。' },
          { title_zh: '通問報', title_orig: '通問報（Chinese Christian Intelligencer）', author: '上海基督教會界', era: '1902–1949', place: '上海', language: '中文', intro: '上海發行的跨宗派中文教會週報，溝通各地華人教會消息、講道文字與教會評論近半世紀，發行遍及全國與南洋僑社。它是華人信徒自辦教會媒體的先聲之一，保存了本土教會網絡日常運作的珍貴剖面。' },
          { title_zh: '英行教會宣教情報', title_orig: 'Church Missionary Intelligencer / CM Review', author: '英行教會（CMS）', era: '1849–1927（1900 年代續刊）', place: '倫敦', language: '英文', intro: '英國聖公會差會的評論月刊，兼載宣教政策論辯、田野報告與語言學民族誌紀錄，東非、奈及利亞、波斯與華中教區的成長軌跡歷歷可尋。其論辯品質使之超越宣傳刊物，是聖公宗宣教思想史的主要檔案。' },
          { title_zh: '宣教先驅報', title_orig: 'The Missionary Herald', author: '美部會（ABCFM）', era: '1821–1934（1900 年代續刊）', place: '波士頓', language: '英文', intro: '美國公理會海外傳道部的機關月刊，百餘年間連載夏威夷、中東、印度與華北宣教站的書信報告，是美國最悠久的宣教期刊之一。其報導塑造了美國新教大眾對「異教世界」的想像，兼為諸多地區近代史的意外檔案庫。' },
          { title_zh: '福音新報', title_orig: '福音新報', author: '植村正久主編', era: '1891–1942', place: '東京', language: '日文', intro: '日本長老教會領袖植村正久主編的基督教週報，五十年間評論教會與國政，屢與國家主義交鋒，植村藉此培育日本教會的自立神學論壇。它是明治大正基督教言論史的中樞刊物，見證亞洲教會以報刊立言的傳統。' },
          { title_zh: '宣教研究國際公報', title_orig: 'International Bulletin of Missionary Research', author: '海外事工研究中心', era: '1950 創刊', place: '紐黑文', language: '英文', intro: '以宣教統計年表與「宣教遺產」人物研究著稱的季刊，巴雷特的全球基督教年度統計長期在此發布，成為引用最廣的宣教數據源。期刊嚴守研究品質而跨越宗派，是當代世界基督教研究的旗艦刊物之一。' },
          { title_zh: '收穫田野', title_orig: 'The Harvest Field', author: '印度衛理宗與跨差會編者', era: '1862–1926（1900 年代續刊）', place: '邁索爾／馬德拉斯', language: '英文', intro: '印度出版的跨差會宣教月刊，討論種姓與歸主運動、教育政策與本土教會自立，是在地宣教士與印度基督徒共同的論壇。其論戰預示了印度教會自治的進程，為南亞宣教史研究的一手期刊史料。' },
          { title_zh: '戰報', title_orig: 'The War Cry', author: '救世軍', era: '1879 創刊，1900 年代起全球版', place: '倫敦／各國', language: '英文等多語', intro: '救世軍機關報，以軍隊隱喻報導街頭佈道、貧民救濟與世界各地「戰況」，街頭義賣本身即是佈道行動。它隨救世軍擴展為多語全球報系，把宣教刊物由書齋帶到酒館與貧民窟門口，是大眾宣教媒體的獨特典型。' },
          { title_zh: '天風', title_orig: '天風（Tian Feng）', author: '中國基督教協進會／三自愛國運動委員會', era: '1945 創刊', place: '上海', language: '中文', intro: '吳耀宗等創辦的中文基督教刊物，一九四九年後成為三自愛國運動與中國基督教協進會機關刊物，是中國大陸公開教會唯一持續發行的全國性刊物。其歷年文字忠實折射政教關係的每一階段，為當代中國教會史的必讀檔案。' },
          { title_zh: '普世宣教手冊', title_orig: 'Operation World', author: '莊斯頓', era: '1974 初版', place: '英國', language: '英文', intro: '莊斯頓編纂的逐國代禱手冊，統計各國宗教人口、教會狀況與代禱需要，每隔數年增訂，累計發行數百萬冊。它把宣教統計轉化為草根代禱運動，被稱為「宣教者的年鑑」，是動員普通信徒關心普世宣教的第一工具書。' },
          { title_zh: '世界基督教手冊', title_orig: 'World Christian Handbook', author: '格拉布等主編', era: '1949–1968', place: '倫敦', language: '英文', intro: '世界宣教統計的戰後標準工具書，逐版彙整各國教會與差會數據，為後來《世界基督教百科全書》的先驅。它記錄了非西方教會信徒數首度超越西方的歷史轉折，是「世界基督教」概念成形期的數據見證。' }
        
        ]
      },
      {
        key: 'global-contextual-mission',
        label: '全球與處境宣教部',
        label_en: 'Global and Contextual Mission',
        desc: '普世宣教運動文獻、本色化神學與華人福音運動的宣教實踐。',
        works: [
          { title_zh: '本色化神學論集', title_orig: 'Essays on Contextual Theology', author: '宋泉盛等', era: '二十世紀後半', place: '亞洲', language: '中文‧英文', intro: '亞洲、非洲與拉美神學家探討福音如何在本土文化處境中生根的論述彙編，主張神學須回應在地的歷史、苦難與宗教經驗。此一處境化進路挑戰西方宣教的文化包袱，推動宣教由「移植」轉向「道成肉身」式的本色見證，是現代普世宣教思想的重要轉折。' },
          { title_zh: '中國福音化異象', title_orig: 'The China Evangelization Vision', author: '趙天恩', era: '一九七〇–二〇〇四年', place: '香港‧台灣', language: '中文', intro: '華人宣教學者趙天恩提出「三化異象」——中國福音化、教會國度化、文化基督化——的宣教論述與文獻彙編。其畢生致力於中國教會史研究與福音運動推展，將普世宣教關懷落實於華人處境，是二十世紀末華人本色宣教思想的代表，故收於全球與處境宣教部。' },
          { title_zh: '內村鑑三羅馬書講演', title_orig: 'ロマ書の研究', author: '內村鑑三', era: '1921–1922', place: '東京', language: '日文', intro: '無教會主義創始人內村鑑三晚年在東京連續六十講的羅馬書講演，聽者盈千，為日本基督教思想史的高峰事件。他以「無教會」的獨立精神直讀聖經，主張日本人當以武士道的土壤承接福音。本講演錄是亞洲本土化解經宣講的第一等文獻。' },
          { title_zh: '賀川豐彥佈道文集', title_orig: '賀川豊彦傳道文集', author: '賀川豐彥', era: '1920–1950 年代', place: '神戶／東京', language: '日文', intro: '賀川豐彥自神戶貧民窟起家，兼社會運動家與佈道家於一身，發起「百萬靈魂運動」與「天國運動」全國巡迴佈道。其佈道文集把十字架的愛與合作社運動、勞工權益相連，是二十世紀「社會福音的亞洲面孔」最著名的宣講遺產。' },
          { title_zh: '在主腳前', title_orig: 'At the Master\'s Feet', author: '孫大信', era: '1922', place: '北印度', language: '烏爾都文／英文', intro: '印度僧侶式佈道家孫大信身披橘黃僧袍徒步宣道，屢入西藏，其《在主腳前》以印度靈修對話體傳述與基督的交往。他主張福音之水須以「印度的碗」盛裝，本書風靡東西方，是亞洲本色化宣教靈性最傳奇的文本。' },
          { title_zh: '阿札理亞宣教講辭', title_orig: 'Addresses of V. S. Azariah', author: '阿札理亞', era: '1910–1945', place: '多內卡爾（南印度）', language: '英文／泰盧固文', intro: '英國聖公會首位印度主教阿札理亞在愛丁堡一九一〇年會議上直言「請給我們朋友，不只是恩主」，震動西方宣教界。其講辭集貫穿賤民群體歸主運動與印度教會自立的主張，是亞洲教會向宣教運動爭取平等夥伴地位的標誌聲音。' },
          { title_zh: '奈爾斯佈道神學文集', title_orig: 'That They May Have Life (D. T. Niles)', author: '奈爾斯', era: '1951–1968', place: '錫蘭（斯里蘭卡）', language: '英文', intro: '錫蘭衛理公會佈道家奈爾斯名言「佈道是一個乞丐告訴另一個乞丐哪裡有食物」，其文集申論見證式佈道與亞洲教會的普世責任。他為東亞基督教協會創建者、世界教協要角，是全球南方首批主導普世宣教神學的聲音。' },
          { title_zh: '門外的基督', title_orig: 'Christ Outside the Gate', author: '科斯塔斯', era: '1982', place: '波多黎各／費城', language: '英文／西班牙文', intro: '波多黎各宣教學家科斯塔斯以希伯來書「在營外」的意象，主張宣教的基督始終站在權力中心之外、與受苦者同在。本書把拉丁美洲的處境批判帶入宣教學主流，是「來自邊緣的宣教」典範文本，重塑了福音派的宣教想像。' },
          { title_zh: '整全宣教', title_orig: 'Misión Integral', author: '帕迪利亞', era: '1985', place: '布宜諾斯艾利斯', language: '西班牙文', intro: '阿根廷神學家帕迪利亞在洛桑會議力倡「整全宣教」：傳福音與社會責任如鳥之雙翼不可偏廢。本書結集其宣教神學論述，代表拉丁美洲福音派對北方「屬靈化」宣教觀的矯正，其概念已成為全球福音派宣教的共同語彙。' },
          { title_zh: '更新變化的宣教', title_orig: 'Transforming Mission', author: '博許', era: '1991', place: '南非普利托利亞', language: '英文', intro: '南非宣教學家博許的鉅著，以「宣教範式轉移」綜覽自新約至後現代的宣教神學史，提出「上帝的宣教」（missio Dei）的整全視野。作者身處種族隔離末期的南非而力行和解，本書被公認為二十世紀宣教學的集大成之作。' },
          { title_zh: '多元社會中的福音', title_orig: 'The Gospel in a Pluralist Society', author: '紐畢真', era: '1989', place: '伯明罕', language: '英文', intro: '在印度宣教四十年的紐畢真返英後，發現西方已成最艱難的宣教工場，本書遂以宣教士之眼剖析多元主義文化中福音的公共宣認。他提出「會眾是福音的釋經學」，開啟「向西方宣教」與宣教型教會運動，影響深遠。' },
          { title_zh: '重新發現基督教', title_orig: 'Christianity Rediscovered', author: '唐納文', era: '1978', place: '坦尚尼亞馬賽地區', language: '英文', intro: '美國聖靈會神父唐納文放下建制宣教模式，徒步向馬賽長者講述福音並讓部落整體自行決志，記錄成此書。他主張宣教士當把福音交給文化、然後退場，本書成為處境化宣教的經典案例，被譽為現代版的使徒行傳實驗。' },
          { title_zh: '教會增長的橋樑', title_orig: 'The Bridges of God', author: '馬蓋文', era: '1955', place: '印度／帕薩迪納', language: '英文', intro: '三代印度宣教士世家出身的馬蓋文觀察種姓群體的「集體歸主運動」，提出福音沿親屬網絡流動的「群體歸主」理論，本書被視為教會增長學派的創始文獻。其後他創辦富勒宣教學院，把宣教策略研究推成獨立學科。' },
          { title_zh: '世界基督教運動面面觀', title_orig: 'Perspectives on the World Christian Movement', author: '溫德（主編）', era: '1981', place: '帕薩迪納', language: '英文', intro: '溫德創辦的「面面觀」課程讀本，集聖經、歷史、文化、策略四視角的宣教文選，數十萬信徒藉此課程被動員投入未得之民事工。溫德在洛桑會議提出「隱藏的民族」概念，本書即其動員神學的教材化，形塑當代宣教動員運動。' },
          { title_zh: '第四度空間', title_orig: '4차원의 영적 세계', author: '趙鏞基', era: '1979', place: '首爾汝矣島', language: '韓文', intro: '汝矣島純福音教會創立者趙鏞基闡述異象、夢想、信心與禱告的「第四度空間」信仰操練，其教會以區家小組增長為全球最大會眾。本書代表韓國五旬節靈性的自我表述，兼為教會增長現象的內部視角，譯本流通全球。' },
          { title_zh: '拉瑪拜與穆克蒂復興文獻', title_orig: 'Pandita Ramabai and the Mukti Revival: Documents', author: '潘迪塔‧拉瑪拜', era: '1905–1907', place: '印度浦那穆克蒂之家', language: '馬拉提文／英文', intro: '梵學女學者出身的拉瑪拜收容寡婦孤女建立穆克蒂之家，一九〇五年院內爆發禱告復興，方言與認罪先於阿蘇薩街，被視為全球五旬節運動的印度源頭。其書信報告與院訊輯錄見證女性領導的復興與社會改革合流的獨特一頁。' },
          { title_zh: '本世代福音遍傳世界', title_orig: 'The Evangelization of the World in This Generation', author: '穆特', era: '1900', place: '紐約', language: '英文', intro: '學生志願運動領袖穆特以此書標舉「本世代把福音傳遍世界」的口號，動員兩萬餘名大學生投身海外宣教，並促成愛丁堡一九一〇年會議。本書是二十世紀宣教動員的綱領文本，其樂觀的世代使命感界定了一整個宣教世代。' },
          { title_zh: '宣教與文化人類學', title_orig: 'Anthropological Insights for Missionaries', author: '希伯特', era: '1985', place: '帕薩迪納', language: '英文', intro: '在印度長大的宣教學家希伯特把文化人類學系統引入宣教訓練，提出「批判性處境化」與「排中律的缺陷」等概念，防止福音的文化殖民與混合主義兩極。本書為宣教士文化訓練的標準教材，奠定宣教人類學的學科地位。' },
          { title_zh: '風俗與文化', title_orig: 'Customs and Cultures: Anthropology for Christian Missions', author: '尤金‧奈達', era: '1954', place: '紐約美國聖經公會', language: '英文', intro: '聖經翻譯理論家奈達為宣教士寫的文化人類學導論，主張福音傳播必須穿過文化的語法而非踐踏之。他以「功能對等」革新聖經翻譯，本書則把同一原則推及宣教溝通全域，是宣教學走向社會科學化的里程碑。' },
          { title_zh: '屬靈四律', title_orig: 'The Four Spiritual Laws', author: '白立德', era: '1952', place: '加州', language: '英文', intro: '學園傳道會創辦人白立德把福音濃縮為四條「屬靈定律」的小冊，印行數十億份、譯成兩百餘種語言，為史上流通最廣的佈道文宣。其標準化個人談道法界定了二十世紀後半的大眾佈道技術，毀譽之間自成一個宣教時代的符號。' },
          { title_zh: '未被佔領的宣教工場', title_orig: 'The Unoccupied Mission Fields of Africa and Asia', author: '茲維默', era: '1911', place: '開羅／紐約', language: '英文', intro: '「伊斯蘭使徒」茲維默盤點阿拉伯半島、中亞至北非尚無宣教據點的廣袤地帶，呼籲教會直面穆斯林世界。他創辦《穆斯林世界》期刊並終身致力於此工場，本書是「未得之民」概念的先驅文獻，界定了穆宣百年議程。' },
          { title_zh: '印度路上的基督', title_orig: 'The Christ of the Indian Road', author: '瓊斯', era: '1925', place: '印度', language: '英文', intro: '衛理公會宣教士瓊斯主張把基督而非西方基督教介紹給印度，記其與甘地及印度知識階層的對話，售逾百萬冊。他創立基督徒靜修院（Ashram）運動，使宣教士坐到印度的席子上，本書是宣教「去殖民化」意識的早期經典。' },
          { title_zh: '叢林醫生佈道故事集', title_orig: 'Jungle Doctor Series', author: '保羅‧懷特', era: '1942–1970 年代', place: '坦幹伊喀（坦尚尼亞）', language: '英文', intro: '澳洲醫療宣教士懷特以坦尚尼亞行醫經歷寫成的「叢林醫生」故事系列，藉非洲寓言與病房故事傳講福音，譯成百餘種語言並改編廣播。本系列展示醫療宣教與故事佈道的結合，是二十世紀宣教文學流通最廣的品牌之一。' },
          { title_zh: '韓景職講道集', title_orig: '한경직 설교전집', author: '韓景職', era: '1945–1992', place: '首爾永樂教會', language: '韓文', intro: '北韓流亡牧師韓景職創立首爾永樂教會，牧養戰爭孤兒與難民，使其成為長老宗全球最大會眾之一，一九九二年獲鄧普頓獎。其講道集以簡樸的愛與民族醫治為軸，見證韓國教會在分斷與戰禍中成長的講壇力量。' },
          { title_zh: '阿德博耶講道信息集', title_orig: 'Sermons of E. A. Adeboye', author: '以諾‧阿德博耶', era: '1981 起', place: '拉哥斯救贖營', language: '英文／約魯巴文', intro: '數學博士出身的阿德博耶領導奈及利亞救贖基督教會，每月聖靈之夜聚會動輒數十萬人，宗派植堂遍及百餘國。其講道信息集代表非洲主導的全球宣教新格局——非洲教會今日反向差派宣教士至歐美，本集是此浪潮的言語核心。' }
        
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
