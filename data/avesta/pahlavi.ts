import type { ZoroCanon } from './types'

// 巴列維文獻（續典）— 中古波斯語
//
// 這一藏的處境與阿維斯陀完全不同，不可混為一談：
//
//   阿維斯陀是「經」——阿維斯陀語、口傳、在祭典裡誦唸；
//   巴列維文獻是「論」——中古波斯語、書面著述、寫給讀者不是誦者。
//
// 而且它們幾乎全部寫於**伊斯蘭征服之後**（9–10 世紀），是一個已經失去政權的
// 宗教在最後關頭把自己的知識整個寫下來的努力。這決定了它們的語氣：
// 焦慮、系統化、帶著護教的緊張。《破疑釋惑》直接逐條反駁伊斯蘭、基督宗教、
// 猶太教與摩尼教——那是被逼到牆角的人才會寫的書。
//
// 🚨 英文欄的缺口全在《丹卡爾德》。韋斯特的 SBE 只譯了第 7、8、9 卷；
//    第 3 卷（全書篇幅最大、教義最重）僅零星章節有公有領域英譯，主要依據是
//    德梅納斯的法譯（1958–73），第 6 卷是沙克德的英譯（1979）——兩者都在版權內。
//    這個缺口是真的補不上，不要假裝有。

const MP = '中古波斯語（巴列維）'

export const PAHLAVI_CANON: ZoroCanon = {
  key: 'pahlavi',
  name: '巴列維文獻',
  name_en: 'Zoroastrian Middle Persian Literature',
  glyph: '巴',
  subtitle: '續典 — 中古波斯語著述',
  scriptural: true,
  language: '中古波斯語（巴列維文字）',
  era: '公元 9–10 世紀為主（材料可上溯薩珊）',
  summary:
    '伊斯蘭征服兩百年後，僅存的祆教學者用中古波斯語把整個傳統寫了下來——教義、宇宙論、法規、護教、末世、傳記無所不包。這批著述之所以珍貴，正因為它們晚：阿維斯陀只剩四分之一，而巴列維文獻的作者手上還有完整的二十一納斯克，他們的引述與撮要因此成了失傳正典的唯一通路。《丹卡爾德》第八九卷逐部撮述二十一納斯克，等於一份佚書總目；《本達希什》則保存了已佚的《創造書》納斯克的宇宙論。**沒有這一藏，祆教研究就只剩一堆讚歌。**',
  parts: [
    {
      key: 'p-summa', label: '大典部', label_en: 'The Great Compendia',
      desc: '篇幅最大、涵蓋最廣的三部，是整個中古波斯語祆教知識體系的骨幹。',
      volumes: ['denkard', 'bundahishn'],
    },
    {
      key: 'p-law', label: '法規部', label_en: 'Religious Law and Rulings',
      desc: '祭司對信眾疑問的判答與行為規範。法類納斯克佚失之後，薩珊法制只能靠這一部間接推知。',
      volumes: ['dadestan'],
    },
    {
      key: 'p-apol', label: '論辯部', label_en: 'Apologetics and Wisdom',
      desc: '對外的護教論辯與對內的智慧訓誡。',
      volumes: ['apologetic', 'andarz'],
    },
    {
      key: 'p-vision', label: '末世部', label_en: 'Vision and Apocalypse',
      desc: '異象、預言與世界終局。祆教末世論對猶太教與基督宗教的影響，材料主要在這一部。',
      volumes: ['apocalypse'],
    },
    {
      key: 'p-narrative', label: '史傳部', label_en: 'Narrative and Epigraphy',
      desc: '王朝傳奇、故事與祭司銘文。宗教性較弱，但語言與史料價值高。',
      volumes: ['narrative'],
    },
  ],
  volumes: [
    // ───────────────────────── 丹卡爾德 ─────────────────────────
    {
      key: 'denkard', sigil: '丹', name: '丹卡爾德', name_orig: 'Dēnkard', name_en: 'Dēnkard',
      era: '9–10 世紀（阿杜爾法恩巴格與阿杜爾巴德‧埃梅丹先後編纂）', extent: '原 9 卷，存 3–9 卷',
      summary:
        '名稱意為「宗教之作為」，中古波斯語祆教文獻的最大部頭，被稱作「馬茲達教的百科全書」。第一、二卷已佚。現存七卷性質差異極大：第三卷是全書篇幅之最，逐條論辯教義並駁斥異教；第七卷是查拉圖斯特拉的完整傳記；第八、九兩卷逐部撮述二十一納斯克——**那是失傳正典的目錄，本站佚失納斯克一卷的全部依據**。',
      divisions: [
        {
          key: 'dk-doctrine', label: '教義諸卷（3–6）', label_en: 'Books 3–6',
          columns: { orig: 'available', en: 'copyright', zh: 'none' },
          texts: [
            { slug: 'denkard-03', title_zh: '丹卡爾德 第三卷', title_orig: 'Dēnkard III', siglum: 'Dk 3', language: MP, extent: '約 420 章', status: 'whole', note: '全書篇幅之最，逐章論辯教義並駁斥摩尼教、猶太教、基督宗教與伊斯蘭。', intro: '《丹卡爾德》體量最大也最艱深的一卷，凡四百二十餘章，由九世紀祭司長阿杜爾法恩巴格與其後繼者陸續編成。內容為逐條的教義論證：善惡二元的形上根據、身體與靈魂的構成、律法的理性基礎、對摩尼教「物質即惡」的反駁、對一神論者「惡從何來」的反問。它的論證方式已深受亞里斯多德式邏輯與同時代伊斯蘭「凱拉姆」神學影響——這本身就是史料。🚨 韋斯特的 SBE 未收本卷，通行的完整譯本是德梅納斯的法譯（1958–73），仍在版權內。' },
            { slug: 'denkard-04', title_zh: '丹卡爾德 第四卷', title_orig: 'Dēnkard IV', siglum: 'Dk 4', language: MP, status: 'partial', note: '論知識的分類與王室蒐書；記載阿爾達希爾與沙普爾廣蒐希臘、印度典籍歸入阿維斯陀的著名段落。' },
            { slug: 'denkard-05', title_zh: '丹卡爾德 第五卷', title_orig: 'Dēnkard V', siglum: 'Dk 5', language: MP, status: 'whole', note: '答一位基督徒與一位猶太人所提的問題；宗教對話的實錄體。' },
            { slug: 'denkard-06', title_zh: '丹卡爾德 第六卷', title_orig: 'Dēnkard VI', siglum: 'Dk 6', language: MP, status: 'whole', note: '「先賢所言」格言集，祆教倫理最集中的一卷。🚨 通行英譯為沙克德（1979），版權內。' },
          ],
        },
        {
          key: 'dk-prophet', label: '先知傳（7）', label_en: 'Book 7',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: [
            { slug: 'denkard-07', title_zh: '丹卡爾德 第七卷', title_orig: 'Dēnkard VII', siglum: 'Dk 7', language: MP, extent: '11 章', status: 'whole', note: '查拉圖斯特拉自太初的神光下降、降生、蒙召、傳教到末世救主降臨的完整傳記。', intro: '祆教唯一一部結構完整的先知傳。自「神光」（赫瓦雷納）在太初分授、經歷代先賢傳遞而降於查拉圖斯特拉之母開始，敘其誕生時大笑而非啼哭、幼年屢遭巫者謀害、三十歲於河畔蒙召見善念之靈、七次天啟、勸化維什塔斯帕王，直到書末預告三位末世救主相繼降臨。材料多出於已佚的《聖行書》納斯克。韋斯特譯本收於 SBE 第 47 卷，公有領域。' },
          ],
        },
        {
          key: 'dk-nask', label: '納斯克撮要（8–9）', label_en: 'Books 8–9',
          desc: '祆教研究裡使用頻率最高的兩卷——因為除此之外沒有別的路可以走到那十九部佚書。',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: [
            { slug: 'denkard-08', title_zh: '丹卡爾德 第八卷', title_orig: 'Dēnkard VIII', siglum: 'Dk 8', language: MP, extent: '46 章', status: 'whole', seealso: '阿維斯陀‧二十一納斯克', note: '逐部撮述二十一納斯克的內容與章數；失傳正典的總目。韋斯特譯本收於 SBE 第 37 卷。' },
            { slug: 'denkard-09', title_zh: '丹卡爾德 第九卷', title_orig: 'Dēnkard IX', siglum: 'Dk 9', language: MP, extent: '69 章', status: 'whole', seealso: '阿維斯陀‧二十一納斯克', note: '詳解迦薩類三部納斯克（益世書、聖言功效書、分授書），逐章逐節撮要。' },
          ],
        },
      ],
    },

    // ───────────────────────── 本達希什 ─────────────────────────
    {
      key: 'bundahishn', sigil: '創', name: '本達希什', name_orig: 'Bundahišn', name_en: 'Bundahišn',
      era: '9 世紀成書（材料出自已佚的《創造書》納斯克）', extent: '大本 36 章／印度本 34 章',
      summary:
        '名稱意為「太初的造作」，祆教的創世書。自阿胡拉‧馬茲達與安格拉‧曼紐在無限光明與無限黑暗中各自存在講起，經三千年一期的四期世界史，到善惡決戰、烈火熔山、萬物復原（弗拉紹‧克雷提）為止。傳世有兩系：伊朗傳的「大本」較完整，印度帕西傳的「印度本」較短。**祆教宇宙論、地理、曆法、世系的知識幾乎全部出於此書**——它保存了已佚的《創造書》納斯克。',
      divisions: [
        {
          key: 'bd-all', label: '兩系傳本', label_en: 'The Two Recensions',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: [
            { slug: 'bundahishn-greater', title_zh: '大本達希什（伊朗本）', title_orig: 'Iranian Bundahišn', siglum: 'GBd', language: MP, extent: '36 章', status: 'whole', note: '較完整的一系，多出宇宙地理與世系數章。安克萊薩里亞英譯。' },
            { slug: 'bundahishn-indian', title_zh: '印度本達希什', title_orig: 'Indian Bundahišn', siglum: 'Bd', language: MP, extent: '34 章', status: 'whole', note: '帕西社群所傳的較短一系。韋斯特譯本收於 SBE 第 5 卷。' },
            { slug: 'zadspram', title_zh: '扎德斯普拉姆選集', title_orig: 'Wizīdagīhā ī Zādspram', siglum: 'WZ', language: MP, extent: '35 章', status: 'whole', author: '扎德斯普拉姆（9 世紀祭司）', note: '與《本達希什》同源而自成一書：創世、查拉圖斯特拉生平、人體構造與靈魂、末世復原。韋斯特譯本收於 SBE 第 47 卷。' },
            { slug: 'pahlavi-rivayat', title_zh: '巴列維利瓦亞特', title_orig: 'Pahlavi Rivāyat', siglum: 'PRDd', language: MP, extent: '65 章', status: 'whole', note: '附於《宗教判例》之後流傳的雜纂，教義、法規、末世、神話兼收。' },
          ],
        },
      ],
    },

    // ───────────────────────── 法規 ─────────────────────────
    {
      key: 'dadestan', sigil: '判', name: '判例與法規', name_en: 'Rulings and Religious Law',
      era: '9–10 世紀', extent: '約 8 種',
      summary:
        '祭司對信眾具體疑問的書面判答，以及行為規範的彙編。與基督宗教的教會法規、伊斯蘭的教法答問（法特瓦）性質相近。這一部最能看見祆教徒在伊斯蘭統治下的實際處境——問題往往是「與異教徒同席可不可以」「改宗者的財產怎麼辦」這一類。',
      divisions: [
        {
          key: 'dd-all', label: '判例與規範', label_en: 'Rulings',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: [
            { slug: 'dadestan-i-denig', title_zh: '宗教判例', title_orig: 'Dādestān ī Dēnīg', siglum: 'Dd', language: MP, extent: '92 問', status: 'whole', author: '曼努什奇赫爾（9 世紀祭司長）', note: '九十二則問答；祆教法律思想最完整的傳世文本。韋斯特譯本收於 SBE 第 18 卷。' },
            { slug: 'epistles-manushchihr', title_zh: '曼努什奇赫爾書信', title_orig: 'Nāmagīhā ī Manuščihr', siglum: 'Ep', language: MP, era: '公元 881 年', status: 'whole', author: '曼努什奇赫爾', note: '三封信，斥其弟扎德斯普拉姆擅改大淨禮的儀式。**有明確年份的祆教文獻極少，這是其一。**' },
            { slug: 'shayest-ne-shayest', title_zh: '宜與不宜', title_orig: 'Šāyest nē Šāyest', siglum: 'SnS', language: MP, extent: '23 章', status: 'whole', note: '罪與潔淨的細目彙編，體例零散。韋斯特譯本收於 SBE 第 5 卷。' },
            { slug: 'rivayat-adur-farnbag', title_zh: '阿杜爾法恩巴格判例', title_orig: 'Rivāyat ī Ādur-Farnbag', siglum: 'RAF', language: MP, extent: '147 問', status: 'whole' },
            { slug: 'rivayat-farnbag-srosh', title_zh: '法恩巴格‧斯勞什判例', title_orig: 'Rivāyat ī Farnbag-Srōš', siglum: 'RFS', language: MP, status: 'fragment' },
            { slug: 'nirangistan-pahlavi', title_zh: '儀軌書巴列維註', title_orig: 'Nīrangistān (Zand)', siglum: 'N(Z)', language: MP, status: 'fragment', seealso: '阿維斯陀‧殘篇‧儀軌書', note: '阿維斯陀語《儀軌書》的逐句中古波斯語註解，篇幅遠大於被註的原文。' },
          ],
        },
      ],
    },

    // ───────────────────────── 護教論辯 ─────────────────────────
    {
      key: 'apologetic', sigil: '辯', name: '護教與論辯', name_en: 'Apologetics',
      era: '9–10 世紀', extent: '約 3 種',
      summary:
        '祆教被四面包圍時寫下的辯護。這一卷的文獻價值超出祆教本身——《破疑釋惑》是中古時期少見的、由一個非亞伯拉罕傳統的作者對三大一神教與摩尼教同時提出的系統批判，其「惡的問題」論證至今仍被宗教哲學引用。',
      divisions: [
        {
          key: 'ap-all', label: '論辯諸書', label_en: 'Polemical Works',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: [
            { slug: 'shkand-gumanig-vizar', title_zh: '破疑釋惑', title_orig: 'Škand-gumānīg Wizār', siglum: 'ŠGW', language: '帕贊德／中古波斯語', extent: '16 章', status: 'whole', author: '馬爾丹法魯赫（9 世紀）', note: '逐章反駁伊斯蘭、猶太教、基督宗教與摩尼教。', intro: '書名意為「解疑之釋」。作者馬爾丹法魯赫自陳曾遍訪各教、讀其經書而後歸信祆教，故全書採比較宗教的論證體例。前半正面陳述二元論：若神全善全能，惡必來自另一獨立本原，否則神即為惡之作者——他以此逼問一神論者，反問基督宗教的三位一體與道成肉身如何自洽，質疑猶太教的神為何後悔、發怒、與人角力，並斥摩尼教視物質本身為惡。**這是前現代少數由非亞伯拉罕傳統寫出的系統性一神教批判。**韋斯特譯本收於 SBE 第 24 卷。' },
            { slug: 'ulema-i-islam', title_zh: '伊斯蘭學者問答', title_orig: 'Ulamā ī Islām', siglum: 'UI', language: '新波斯語', status: 'whole', era: '13 世紀以後', note: '託為伊斯蘭學者向祆教祭司問道的對話體；實為祆教徒所作的護教文。' },
            { slug: 'drayishn-i-ahriman', title_zh: '阿里曼對眾魔之言', title_orig: 'Draxt ī Ahreman ō Dēwān', siglum: 'DA', language: MP, status: 'fragment', note: '短篇，惡靈訓示群魔如何敗壞人類。' },
          ],
        },
      ],
    },

    // ───────────────────────── 智慧訓誡 ─────────────────────────
    {
      key: 'andarz', sigil: '訓', name: '智慧與訓誡', name_orig: 'Andarz', name_en: 'Wisdom Literature',
      era: '薩珊至 10 世紀', extent: '約 8 種',
      summary:
        '「安達爾茲」是波斯特有的訓誡文類，形式為長者對子弟的格言式教導，內容從宗教義務到理財、擇友、飲食無所不包。它與希伯來的箴言、佛教的法句經同屬一類，但更世俗、更務實。這一卷最能看出祆教倫理的實際樣貌——不是二元論的形上思辨，而是「量入為出、不與愚人爭辯、每日三省」這種東西。',
      divisions: [
        {
          key: 'an-all', label: '訓誡諸篇', label_en: 'Andarz Texts',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: [
            { slug: 'menog-i-khrad', title_zh: '智慧精神', title_orig: 'Dādestān ī Mēnōg ī Xrad', siglum: 'MX', language: MP, extent: '63 問', status: 'whole', note: '智者向「智慧之靈」發問六十三則的對話體；祆教入門最常被引用的一書。韋斯特譯本收於 SBE 第 24 卷。' },
            { slug: 'chidag-andarz', title_zh: '古聖精選訓誡', title_orig: 'Čīdag Andarz ī Pōryōtkēšān', siglum: 'ČAP', language: MP, status: 'whole', note: '祆教的要理問答：十五歲當知者為何？答曰知我是誰、屬誰、從何而來、往何處去。' },
            { slug: 'andarz-adurbad-1', title_zh: '阿杜爾巴德訓誡', title_orig: 'Andarz ī Ādurbād ī Mahraspandān', siglum: 'AAM', language: MP, status: 'whole', author: '阿杜爾巴德‧馬赫拉斯潘丹（4 世紀祭司長）', note: '傳為受熔銅神判而不傷的那位祭司長所留；祆教格言的最大宗。' },
            { slug: 'andarz-adurbad-2', title_zh: '阿杜爾巴德箴言', title_orig: 'Wāzag ī Ādurbād', siglum: 'WA', language: MP, status: 'whole' },
            { slug: 'khweshkarih-i-redagan', title_zh: '幼者的本分', title_orig: 'Xwēškārīh ī Rēdagān', siglum: 'XR', language: MP, status: 'whole' },
            { slug: 'nature-fortunate-man', title_zh: '有福之人的性情與智慧', title_orig: 'Xēm ud Xrad ī Farrox Mard', siglum: 'XXFM', language: MP, status: 'whole' },
            { slug: 'style-of-letters', title_zh: '書信體例', title_orig: 'Abar Ēwēnag ī Nāmag Nibēsišnīh', siglum: 'ENN', language: MP, status: 'whole', note: '公文書寫格式手冊；宗教性極低，但保存了薩珊官制詞彙。' },
            { slug: 'gasanawa', title_zh: '亡者迦薩誦', title_orig: 'Gāsānawā', siglum: 'Gw', language: MP, status: 'fragment' },
          ],
        },
      ],
    },

    // ───────────────────────── 末世異象 ─────────────────────────
    {
      key: 'apocalypse', sigil: '末', name: '異象與末世', name_en: 'Vision and Apocalypse',
      era: '薩珊至 11 世紀', extent: '約 4 種',
      summary:
        '祆教末世論的主要文本。世界四期三千年、末代的敗壞徵兆、救主薩奧希揚特由處女受孕而生、死者復活、烈火熔盡群山成河、萬物復原——這一整套敘事對第二聖殿時期猶太教與早期基督宗教的影響是宗教史上爭論最久的題目之一，而爭論所用的材料主要就在這一卷。**須注意年代問題**：這些寫本晚至九世紀以後，其中的末世細節有多少可上溯到前基督教時代，是每一次引用都必須交代的前提。',
      divisions: [
        {
          key: 'ap-all', label: '末世諸書', label_en: 'Apocalyptic Works',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: [
            { slug: 'arda-wiraz-namag', title_zh: '阿爾達‧維拉茲書', title_orig: 'Ardā Wīrāz Nāmag', siglum: 'AWN', language: MP, extent: '101 章', status: 'whole', note: '義人維拉茲飲藥入定七日，魂遊天堂與地獄，逐一目睹各罪的刑罰。', intro: '祆教的天地遊記。祭司會議選出最義的維拉茲，飲下曼陀羅與酒調的藥而神魂出竅七日；他先過裁判之橋，見義人的靈魂由化身少女的「自己的宗教」相迎，再上三重天到無限光明之境，然後下入地獄，逐一目睹背約者、苛待牲畜者、毀壞水火者所受的刑罰。歸來後口述，書記錄之。**與但丁《神曲》的結構相似度極高**，兩者有無傳承關係聚訟未決。文本最晚不遲於十世紀，但材料可能早得多。' },
            { slug: 'zand-i-wahman-yasn', title_zh: '巴赫曼耶什特', title_orig: 'Zand ī Wahman Yasn', siglum: 'ZWY', language: MP, extent: '9 章', status: 'whole', note: '四枝（或七枝）金銀鐵鉛之樹的異象，預言各時代的敗壞與外族入侵；祆教啟示文學的代表。韋斯特譯本收於 SBE 第 5 卷。' },
            { slug: 'ayadgar-i-jamaspig', title_zh: '賈馬斯普紀念書', title_orig: 'Ayādgār ī Jāmāspīg', siglum: 'AJ', language: '帕贊德／中古波斯語', extent: '17 章', status: 'partial', note: '智者賈馬斯普答維什塔斯帕王問未來之事；含千年周期與救主降臨。' },
            { slug: 'saddar-bundahesh', title_zh: '百門本達希什', title_orig: 'Saddar Bundahiš', siglum: 'SdB', language: '新波斯語', status: 'whole', era: '15 世紀', note: '晚期彙編，末世材料豐富但年代甚晚，引用須格外謹慎。' },
          ],
        },
      ],
    },

    // ───────────────────────── 史傳敘事 ─────────────────────────
    {
      key: 'narrative', sigil: '傳', name: '史傳與銘文', name_en: 'Narrative and Priestly Epigraphy',
      era: '3 世紀（銘文）至 10 世紀', extent: '約 8 種',
      summary:
        '王朝傳奇、故事與薩珊祭司的自述銘文。宗教教義成分低，但語言與史料價值高——尤其卡爾提爾的四處銘文，是**祆教史上唯一一份由當事祭司親自刻下的、關於他如何鎮壓其他宗教的紀錄**，其史料性質與任何後世的教內敘述都不同。',
      divisions: [
        {
          key: 'nr-story', label: '傳奇與故事', label_en: 'Legend and Tale',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: [
            { slug: 'karnamag-ardashir', title_zh: '阿爾達希爾功業記', title_orig: 'Kārnāmag ī Ardaxšīr ī Pābagān', siglum: 'KAP', language: MP, extent: '18 章', status: 'whole', note: '薩珊開國君主的傳奇；《列王紀》相關段落的直接來源。' },
            { slug: 'ayadgar-i-zareran', title_zh: '扎雷爾紀念書', title_orig: 'Ayādgār ī Zarērān', siglum: 'AZ', language: MP, status: 'whole', note: '現存最古的伊朗語敘事詩之一，敘維什塔斯帕王為護新教而戰、其弟扎雷爾陣亡。原為安息時期的口傳吟唱。' },
            { slug: 'yavisht-i-friyan', title_zh: '雅維什特‧弗里揚故事', title_orig: 'Mādayān ī Yōšt ī Friyān', siglum: 'YF', language: MP, status: 'whole', note: '少年以智慧解答惡巫三十三則謎題。謎語文學的伊朗代表作。' },
            { slug: 'chatrang-namag', title_zh: '棋弈書', title_orig: 'Wizārišn ī Čatrang', siglum: 'WČ', language: MP, status: 'whole', note: '印度使者獻西洋棋、波斯智者回贈雙陸棋；世界棋史最早的文獻之一。' },
            { slug: 'shahrestaniha-i-eranshahr', title_zh: '伊朗諸城志', title_orig: 'Šahrestānīhā ī Ērānšahr', siglum: 'ŠĒ', language: MP, status: 'whole', note: '逐城記其建者與傳說；歷史地理材料。' },
          ],
        },
        {
          key: 'nr-inscription', label: '祭司銘文', label_en: 'Priestly Inscriptions',
          desc: '三世紀祭司長卡爾提爾的自述。四處銘文內容大同小異，互相補足殘缺。',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: [
            { slug: 'kartir-kz', title_zh: '卡爾提爾‧瑣羅亞斯德立方體銘文', title_orig: 'KKZ', siglum: 'KKZ', language: MP, era: '約公元 280 年', status: 'inscription', note: '最完整的一處。卡爾提爾歷數其在各省設立火廟、整肅祭司，並列舉遭其打擊的宗教：猶太教、佛教、婆羅門教、拿撒勒派、基督徒、洗禮派與摩尼教。' },
            { slug: 'kartir-naqsh-i-rajab', title_zh: '卡爾提爾‧納克什伊拉賈布銘文', title_orig: 'KNRb', siglum: 'KNRb', language: MP, era: '3 世紀', status: 'inscription' },
            { slug: 'kartir-naqsh-i-rustam', title_zh: '卡爾提爾‧納克什伊魯斯塔姆銘文', title_orig: 'KNRm', siglum: 'KNRm', language: MP, era: '3 世紀', status: 'inscription', note: '含卡爾提爾自述的靈魂出竅異象，是《阿爾達‧維拉茲書》的遠祖。' },
            { slug: 'kartir-sar-mashhad', title_zh: '卡爾提爾‧薩爾馬什哈德銘文', title_orig: 'KSM', siglum: 'KSM', language: MP, era: '3 世紀', status: 'inscription' },
          ],
        },
      ],
    },
  ],
}
