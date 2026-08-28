import type { HellenCanon } from './types'

// 羅馬卷 I–VI。續典而非本經，故用羅馬數字編號以示位階。
// 羅馬宗教自成一系（努瑪傳統、祭司團、卜筮、國家法），重心在儀式與國家法而非神話與神學，
// 文類分佈與希臘那套對不上，因此另立六卷而不打散進廿四卷——這樣兩套宗教的邊界還看得見。

export const ROMAN_CANON: HellenCanon = {
  key: 'roman',
  name: '羅馬卷',
  name_en: 'The Roman Canon',
  glyph: '羅',
  subtitle: '六卷 I–VI — 續典',
  summary:
    '羅馬傳統宗教不是希臘東西的拉丁版，是另一套宗教：它的核心是神事法（ius divinum）而非神學，是祭司團、曆法與卜筮而非神譜與救贖。故另立六卷為續典，以羅馬數字編號。歸卷準則同全書：按材料所屬的宗教系統歸卷，不按語言也不按作者——普魯塔克《努瑪傳》雖希臘文而歸此，西塞羅《論神性》雖拉丁文而留希臘卷 Φ。斷限同為公元 529 年。',
  enabled: true,
  parts: [
    { key: 'rp-origin', label: '建城部', label_en: 'Foundation', desc: '羅馬人的創世記與出埃及記：從特洛伊逃出、渡海、建城、立教。', volumes: ['RI', 'RII'] },
    { key: 'rp-order', label: '秩序部', label_en: 'Sacred Order', desc: '曆法與卜筮——羅馬宗教真正的日常運作方式。', volumes: ['RIII', 'RIV'] },
    { key: 'rp-state', label: '國教部', label_en: 'State and Empire', desc: '宗教如何成為帝國的制度，以及外來諸神如何被收編或鎮壓。', volumes: ['RV'] },
    { key: 'rp-end', label: '終末部', label_en: 'The End', desc: '西方的終結，與希臘卷 Ω 在同一年合攏。', volumes: ['RVI'] },
  ],
  volumes: [
    // ──────────────────────────── I 建城記 ────────────────────────────
    {
      key: 'RI', sigil: 'I', name: '建城記', name_en: 'The Founding',
      parallel: '創世記與出埃及記', clock: 'mythic', span: '前 2 世紀 – 公元 2 世紀',
      summary: '羅馬人自陳其血脈來自特洛伊敗方、其城建於神意。與希臘卷 Δ 歸返記對讀：一邊是勝方的歸鄉，一邊是敗方的流亡。',
      divisions: [
        {
          key: 'ri-aeneas', label: '埃涅阿斯', label_en: 'Aeneas',
          works: [
            {
              title_zh: '埃涅阿斯紀', title_orig: 'Aeneis', author: '維吉爾',
              era: '前 29–19 年', place: '羅馬', language: '拉丁文', extent: '全 12 卷（未定稿）', status: 'whole',
              note: '羅馬的民族史詩；前六卷漂流、後六卷得地立國。',
              intro: '特洛伊城破後，埃涅阿斯負父攜子出逃，歷經迦太基、西西里、冥府，終抵拉丁姆並以戰爭取得立國之地。全詩的宗教核心是 pietas——對神、對父、對國的責任先於個人願望，這是羅馬人自我理解的根本德目。卷六下冥府一段，把希臘的招魂傳統改造成一場關於羅馬未來的啟示：亡父指認尚未出生的歷代英雄，使建城成為神所預定的歷史計畫。與希臘卷 Δ、Ε 對讀。',
            },
            { title_zh: '家神與帕拉狄昂聖像的西遷', title_orig: 'The Penates and the Palladium', author: '綴輯（維吉爾、李維、狄奧尼修斯、奧維德《歲時記》）', language: '拉丁文／古希臘文', status: 'fragment', note: '特洛伊的家神與雅典娜聖像被帶到羅馬並藏於火神廟——羅馬宗教合法性的物質憑據。' },
          ],
        },
        {
          key: 'ri-romulus', label: '羅慕路斯', label_en: 'Romulus',
          works: [
            { title_zh: '羅馬史‧卷一', title_orig: 'Ab Urbe Condita I', author: '李維', era: '約前 27–25 年', language: '拉丁文', status: 'whole', note: '雙生子、母狼、鳥卜定城址、劫薩賓婦女、羅慕路斯升天為奎里努斯——建城傳說的標準本。' },
            { title_zh: '羅馬古事記', title_orig: 'Ῥωμαϊκὴ Ἀρχαιολογία', author: '哈利卡納索斯的狄奧尼修斯', era: '前 7 年', language: '古希臘文', extent: '原 20 卷（存前 11 卷）', status: 'whole', note: '以希臘文寫給希臘人看的羅馬古史，保存大量已佚的祭儀與制度細節；本卷最重的史料來源之一。' },
            { title_zh: '羅慕路斯傳', title_orig: 'Ῥωμύλος', author: '普魯塔克', era: '公元 2 世紀初', language: '古希臘文', status: 'whole', note: '希臘文著作而歸羅馬卷——本藏經歸卷準則的示範個案。' },
            { title_zh: '編年紀', title_orig: 'Annales', author: '恩尼烏斯', era: '約前 180–170 年', language: '拉丁文', extent: '原 18 卷', status: 'fragment', note: '最早的拉丁民族史詩，自埃涅阿斯寫到作者當代；羅馬人對自己歷史的第一次詩體整理。' },
          ],
        },
      ],
    },
    // ──────────────────────────── II 祭司法 ────────────────────────────
    {
      key: 'RII', sigil: 'II', name: '祭司法', name_en: 'The Sacred Law',
      parallel: '利未記', clock: 'historical', span: '前 5 世紀 – 公元 3 世紀',
      summary: '羅馬宗教的核心：神事法。不問神是誰、只問儀節有沒有做對——程序出錯則整套重來。本卷是全藏經最「律法書」的一卷。',
      divisions: [
        {
          key: 'rii-numa', label: '努瑪立教', label_en: 'The Institution of Numa',
          works: [
            { title_zh: '羅馬史 1.19–21（努瑪立教）', title_orig: 'Ab Urbe Condita I.19–21', author: '李維', era: '約前 27–25 年', language: '拉丁文', status: 'whole', note: '第二任王在女神埃格里亞指導下設曆、立祭司團、建雅努斯門——羅馬一切祭儀的傳說性起點。' },
            { title_zh: '努瑪傳', title_orig: 'Νουμᾶς', author: '普魯塔克', era: '公元 2 世紀初', language: '古希臘文', status: 'whole', note: '最完整的努瑪傳記，並比較其與呂庫古的立法；記其禁止神像、以為神不可摹狀。' },
          ],
        },
        {
          key: 'rii-colleges', label: '祭司團', label_en: 'The Priestly Colleges',
          works: [
            { title_zh: '大祭司團與祭司王', title_orig: 'Pontifices and the rex sacrorum', author: '綴輯（西塞羅、李維、瓦羅、銘文）', era: '前 5 世紀 – 公元 4 世紀', language: '拉丁文', status: 'fragment', note: '掌曆法、神事法解釋與祭司任免；共和末以後大祭司長由執政者兼任，帝國期歸皇帝。' },
            { title_zh: '火神女祭司', title_orig: 'Virgines Vestales', author: '綴輯（普魯塔克、奧盧斯‧革利烏斯、銘文）', era: '前 7 世紀 – 公元 394 年', language: '拉丁文／古希臘文', status: 'fragment', note: '六名處女守護城中聖火，任期三十年；失貞者活埋。羅馬國運與此火直接繫連。' },
            { title_zh: '三大婚祭司與跳祭司團', title_orig: 'Flamines maiores and the Salii', author: '綴輯', era: '前 7 世紀 – 公元 4 世紀', language: '拉丁文', status: 'fragment', note: '朱庇特婚祭司的禁忌多到近乎不能生活（不得騎馬、不得見軍隊、不得打結）；三月跳祭司持聖盾遊行歌舞。' },
            { title_zh: '宣戰祭司團', title_orig: 'Fetiales', author: '綴輯（李維 1.32 為最詳）', era: '前 7 世紀起', language: '拉丁文', status: 'fragment', note: '開戰須由祭司赴邊界擲矛並誦定式禱詞，戰爭方為「正義」——古代罕見的宗教化國際法。' },
            {
              title_zh: '阿爾瓦兄弟會會議紀錄', title_orig: 'Acta Fratrum Arvalium',
              author: '阿爾瓦兄弟會', era: '前 21 年 – 公元 241 年', place: '羅馬近郊聖林',
              language: '拉丁文', status: 'inscription',
              note: '橫跨兩個半世紀的祭儀逐年實錄，古代世界獨一無二。',
              intro: '十二人組成的古老祭司團，每年為豐產女神主持三日祭典，並把每一次集會的日期、與會者、牲品、禱詞、乃至儀節出錯後如何補贖，全部刻石存檔。現存殘石橫跨兩個半世紀，是全古代唯一一份連續的祭儀行政檔案——不是描述儀式應該怎麼做，而是記錄它實際上怎麼做了。研究羅馬宗教的第一手材料，其分量相當於一部逐年更新的利未記實錄。',
            },
            { title_zh: '阿爾瓦頌與跳祭司頌', title_orig: 'Carmen Arvale; Carmen Saliare', author: '佚名（古拉丁）', era: '約前 6 世紀或更早（存於帝國期抄刻）', language: '古拉丁文', status: 'fragment', note: '現存最古的拉丁禱詞，古到羅馬人自己已讀不懂——昆體良說連祭司都只是照音誦念。' },
          ],
        },
        {
          key: 'rii-formula', label: '程式與法典', label_en: 'Formulae and Codes',
          works: [
            { title_zh: '獻身、招神與贖罪諸式', title_orig: 'Devotio, evocatio, piaculum, lustratio', author: '綴輯（李維、加圖《農業志》、馬克羅比烏斯）', era: '前 3 世紀 – 公元 2 世紀', language: '拉丁文', status: 'fragment', note: '將軍以自身獻於地下諸神換取勝利（獻身）、圍城前先招敵城之神叛離（招神）；加圖書中保存了最完整的田產淨化禱詞原文。' },
            { title_zh: '鋪神席與公眾祈禱', title_orig: 'Lectisternium and supplicatio', author: '綴輯（李維為主）', era: '前 399 年起', language: '拉丁文', status: 'fragment', note: '國難時陳設神像臥榻宴請諸神，全民赴各廟祈禱；羅馬應對危機的標準宗教程序。' },
            { title_zh: '十二表法宗教條款', title_orig: 'Lex XII Tabularum (religious clauses)', author: '十人立法委員會', era: '約前 451–450 年', language: '古拉丁文', status: 'fragment', note: '喪葬限制、禁止城內火葬、禁咒術害人——羅馬成文法一開始就管宗教。' },
            { title_zh: '辭義彙纂', title_orig: 'De verborum significatu', author: '費斯圖斯（節錄維里烏斯‧弗拉庫斯，後由保魯斯‧狄阿科努斯再節錄）', era: '公元 2 世紀（原書前 1 世紀）', language: '拉丁文', status: 'fragment', note: '按詞條解釋古語與古制，祭司團職名、祭儀術語、已廢節期的釋義多半只存於此。羅馬宗教研究第一線的工具書，卻本身就是一部殘篇。' },
            { title_zh: '神人事物古事記（殘篇）', title_orig: 'Antiquitates rerum humanarum et divinarum', author: '瓦羅', era: '前 47 年', language: '拉丁文', extent: '原 41 卷（神事 16 卷）', status: 'hostile', via: '奧古斯丁《上帝之城》卷四至七', note: '羅馬宗教最完整的一部系統著作，全書已佚，靠敵手的駁斥保存綱目與大量引文。其「三種神學」（詩人的／哲人的／城邦的）之分至今仍是宗教學的基本框架。' },
          ],
        },
      ],
    },
    // ──────────────────────────── III 節期曆 ────────────────────────────
    {
      key: 'RIII', sigil: 'III', name: '節期曆', name_en: 'The Calendar',
      parallel: '節期條例', clock: 'historical', span: '前 1 世紀 – 公元 5 世紀',
      summary: '羅馬宗教靠曆法運作：哪天可以開庭、哪天必須獻祭、哪天不吉。曆就是教規。',
      divisions: [
        {
          key: 'riii-fasti', label: '曆銘', label_en: 'The Fasti',
          works: [
            {
              title_zh: '安提烏姆曆石', title_orig: 'Fasti Antiates Maiores', author: '佚名',
              era: '約前 84–55 年', place: '義大利‧安提烏姆', language: '拉丁文', status: 'inscription',
              note: '唯一存世的前儒略曆刻本。',
              intro: '一面壁畫式的曆表，逐日標記該日的法律性質（可開庭／不可／部分可）、節期名稱與紀念日。它是唯一一份儒略改曆之前的羅馬曆實物，保存了共和時代的原始節期序列與那個尚未整齊的閏月制度。羅馬人的宗教義務全部寫在這張表上，因此它同時是曆書、法典與教規。',
            },
            { title_zh: '各地曆銘集', title_orig: 'Fasti (Praenestini, Amiternini, Maffeiani, etc.)', author: '各城鎮', era: '前 1 – 公元 3 世紀', language: '拉丁文', status: 'inscription', note: '奧古斯都以後各地所刻曆表，部分附節期釋義（普萊涅斯特曆的註記傳為維里烏斯‧弗拉庫斯所撰）。' },
          ],
        },
        {
          key: 'riii-feasts', label: '節期釋義', label_en: 'The Feasts Explained',
          works: [
            {
              title_zh: '歲時記', title_orig: 'Fasti', author: '奧維德',
              era: '公元 8 年（流放後修訂）', language: '拉丁文', extent: '存 6 卷（一至六月）', status: 'whole',
              note: '逐日解說羅馬節期的起源，是羅馬宗教最豐富的單一文獻。',
              intro: '按曆日逐條解釋每個節期的由來，作者常自稱親自去問祭司或女神本人。全書原擬十二卷，因流放中止於六月。它保存了大量他處不存的儀節細節——牧神節的皮鞭、亡靈節的黑豆、羅比古節的紅狗——並且不憚並列數種互相矛盾的說法，因此成為羅馬節期研究的第一手材料。與同一作者的《變形記》分屬兩藏，正好示範本藏經按宗教系統而非作者歸卷。',
            },
            { title_zh: '農神節', title_orig: 'Saturnalia', author: '馬克羅比烏斯', era: '約公元 430 年', language: '拉丁文', extent: '全 7 卷', status: 'whole', note: '以節期宴談形式寫成的百科，保存共和時代祭儀、曆法與維吉爾詮釋；異教貴族最後的自我保存之作。' },
            { title_zh: '牧神節、亡靈節、幽靈節與農神節諸儀', title_orig: 'Lupercalia, Parentalia, Lemuria, Saturnalia', author: '綴輯', era: '前 3 – 公元 5 世紀', language: '拉丁文', status: 'fragment', note: '牧神節裸奔鞭女以求孕、幽靈節家主半夜擲黑豆逐鬼；羅馬最古老的一批儀式，多與死者和生育有關。' },
          ],
        },
        {
          key: 'riii-saecular', label: '世紀慶典', label_en: 'The Secular Games',
          works: [
            { title_zh: '世紀慶典法令銘文', title_orig: 'Acta ludorum saecularium', author: '十五人祭司團', era: '前 17 年（另有公元 204 年石）', place: '羅馬', language: '拉丁文', status: 'inscription', note: '完整刻錄一場國家級大祭的全部流程：占卜、通告、獻祭、歌隊排練、皇帝親禱的原文。' },
            { title_zh: '世紀之歌', title_orig: 'Carmen Saeculare', author: '賀拉斯', era: '前 17 年 6 月 3 日', language: '拉丁文', extent: '76 行', status: 'whole', note: '現存唯一一首確知演出日期、地點與歌隊編制（27 男童 27 女童）的古代祭典聖詩。' },
          ],
        },
      ],
    },
    // ──────────────────────────── IV 卜筮與異兆 ────────────────────────────
    {
      key: 'RIV', sigil: 'IV', name: '卜筮與異兆', name_en: 'Divination and Prodigies',
      parallel: '先知書', clock: 'historical', span: '前 1 世紀 – 公元 4 世紀',
      summary: '羅馬的「先知書」：神從不說話，只給徵兆。所有公務都必須先取得神的默許，取得的方式是觀察而非聆聽。',
      divisions: [
        {
          key: 'riv-augury', label: '鳥卜與內臟卜', label_en: 'Augury and Haruspicy',
          works: [
            { title_zh: '鳥卜術', title_orig: 'Augurium / auspicia', author: '綴輯（西塞羅《論法律》二、瓦羅、銘文）', era: '前 7 世紀 – 公元 4 世紀', language: '拉丁文', status: 'fragment', note: '劃定天空觀察區、看鳥的飛向與鳴聲、看聖雞是否進食；執政官出征前必行，不吉則整件事重來。' },
            { title_zh: '伊特魯里亞紀律（殘篇）', title_orig: 'Etrusca Disciplina', author: '伊特魯里亞祭司傳統', era: '前 7 世紀起，前 1 世紀譯為拉丁', language: '伊特魯里亞語／拉丁文', status: 'fragment', note: '羊肝卜、閃電卜與界域劃分三部分；羅馬向被征服者借來的一整套占卜技術，並始終承認其外來。' },
            { title_zh: '皮亞琴察肝模型', title_orig: 'The Piacenza Liver', author: '伊特魯里亞祭司', era: '約前 100 年', place: '義大利‧皮亞琴察', language: '伊特魯里亞語', status: 'inscription', note: '青銅羊肝模型，表面分格刻神名，是肝卜與伊特魯里亞天界分區觀的實物教具。' },
            { title_zh: '論卜筮', title_orig: 'De divinatione', author: '西塞羅', era: '前 44 年', language: '拉丁文', extent: '全 2 卷', status: 'whole', note: '兄弟二人一正一反辯論占卜是否有效；卷一是古代占卜學最完整的整理，卷二是最徹底的懷疑論駁斥。' },
            { title_zh: '論法律‧卷二（宗教法）', title_orig: 'De legibus II', author: '西塞羅', era: '約前 51 年', language: '拉丁文', status: 'whole', note: '為理想國家起草的一部宗教法典，逐條規定祭司職權與祭儀原則；羅馬人自己寫的神事法綱要。' },
          ],
        },
        {
          key: 'riv-prodigy', label: '異兆年報', label_en: 'The Annual Prodigies',
          works: [
            {
              title_zh: '羅馬史異兆年報', title_orig: 'Prodigia in Ab Urbe Condita', author: '李維',
              era: '約前 27 – 公元 17 年', language: '拉丁文', status: 'whole',
              note: '每年開頭列該年異象與贖罪儀式——羅馬版的先知書。',
              intro: '李維在每一年的敘事開頭固定列出當年通報的異象：天降石雨、牛開口說話、神像流汗、嬰兒生而有異，接著記元老院如何裁定、指派何種贖罪儀式。這套年報顯示羅馬宗教處理「神的訊息」的方式與希伯來先知截然不同——沒有人代神說話，只有一個制度負責判讀徵兆並回以正確的儀式。本卷據此把它列為羅馬的先知書。',
            },
            { title_zh: '異兆書', title_orig: 'Liber Prodigiorum', author: '尤利烏斯‧奧布塞昆斯', era: '約公元 4 世紀', language: '拉丁文', status: 'whole', note: '自前 249 至前 12 年的異兆彙編，多取自李維已佚諸卷，因此保存了失傳部分的內容。' },
          ],
        },
        {
          key: 'riv-sibyl', label: '西比拉書', label_en: 'The Sibylline Books',
          works: [
            { title_zh: '羅馬西比拉書與十五人祭司團', title_orig: 'Libri Sibyllini; quindecimviri sacris faciundis', author: '綴輯（李維、狄奧尼修斯、塔西佗）', era: '前 6 世紀 – 公元 408 年', language: '拉丁文', status: 'fragment', note: '國難時經元老院授權方可查閱，所得對策多為「引入某位新神」——羅馬吸納外來神祇的制度性管道。' },
            { title_zh: '西比拉書被焚（約 408）', title_orig: 'The burning of the Sibylline Books', author: '綴輯（魯提利烏斯‧納馬提亞努斯、佐西姆斯）', era: '約公元 408 年', language: '拉丁文／古希臘文', status: 'fragment', note: '傳為斯提里科下令焚毀；羅馬國家宗教最核心的一批文書就此消失。' },
          ],
        },
      ],
    },
    // ──────────────────────────── V 國教與帝王崇拜 ────────────────────────────
    {
      key: 'RV', sigil: 'V', name: '國教與帝王崇拜', name_en: 'State Cult and the Divine Emperor',
      parallel: '王國史', clock: 'historical', span: '前 2 世紀 – 公元 3 世紀',
      summary: '宗教如何成為帝國制度，以及外來諸神如何被收編、被管制、或被鎮壓。羅馬的宗教寬容有其邊界，而邊界由元老院劃定。',
      divisions: [
        {
          key: 'rv-emperor', label: '帝王崇拜', label_en: 'The Imperial Cult',
          works: [
            { title_zh: '奧古斯都功業錄', title_orig: 'Res Gestae Divi Augusti', author: '奧古斯都', era: '公元 14 年', place: '安卡拉等地銘刻', language: '拉丁文／古希臘文', status: 'inscription', note: '皇帝自撰的一生功業，逐條列出他修復了多少神廟、擔任哪些祭司職——政治權威以宗教職銜表述的範本。' },
            { title_zh: '神化制度', title_orig: 'Consecratio / divus', author: '綴輯（蘇埃托尼烏斯、狄奧、元老院決議）', era: '前 42 年 – 公元 4 世紀', language: '拉丁文／古希臘文', status: 'fragment', note: '皇帝死後由元老院表決是否成神；塞內卡《變瓜記》則以喜劇嘲弄此制。' },
            { title_zh: '十二凱撒傳', title_orig: 'De vita Caesarum', author: '蘇埃托尼烏斯', era: '約公元 121 年', language: '拉丁文', extent: '全 8 卷', status: 'whole', note: '逐帝記其出生異兆、星象、褻瀆之舉與死後神化表決；帝王崇拜最密集的一部史料。書中並有羅馬官方視角最早的兩條基督徒記載（《革老丟傳》二十五、《尼祿傳》十六）。' },
            { title_zh: '杜拉歐羅波斯軍團祭曆', title_orig: 'Feriale Duranum', author: '羅馬第二十帕爾提亞弓騎兵團', era: '約公元 225–235 年', place: '敘利亞‧杜拉歐羅波斯', language: '拉丁文', status: 'inscription', note: '一份紙草軍團年度祭曆，逐日列出軍中該向哪位神與哪位先帝獻祭——帝國宗教制度化最直接的證據。' },
          ],
        },
        {
          key: 'rv-foreign', label: '外來諸神', label_en: 'Foreign Gods in Rome',
          works: [
            { title_zh: '大母神引入羅馬（前 204）', title_orig: 'The arrival of Magna Mater', author: '綴輯（李維 29.10–14、奧維德《歲時記》四）', era: '前 204 年', language: '拉丁文', status: 'fragment', note: '依西比拉書指示自小亞細亞迎來黑隕石；羅馬第一次以國家名義引入東方神祇，卻同時禁止公民擔任其祭司。' },
            {
              title_zh: '鎮壓酒神祭元老院令', title_orig: 'Senatus consultum de Bacchanalibus',
              author: '羅馬元老院', era: '前 186 年', place: '義大利‧提里奧洛', language: '古拉丁文', status: 'inscription',
              note: '羅馬第一次宗教迫害的原始法令。',
              intro: '刻在青銅板上的元老院決議，全面取締義大利境內的酒神祕儀：解散信團、拆毀聚會處、非經元老院特許不得舉行，違者處死。李維記當時處決人數以千計。這是歐洲史上第一份針對特定宗教團體的鎮壓法令，其理由——祕密集會、夜間聚會、男女混雜、敗壞風俗——與三百年後羅馬對付基督徒的指控幾乎逐條相同。',
            },
            { title_zh: '伊西斯與薩拉皮斯在羅馬', title_orig: 'The cult of Isis and Sarapis at Rome', author: '綴輯（銘文、塔西佗、阿普列尤斯）', era: '前 1 – 公元 4 世紀', language: '拉丁文／古希臘文', status: 'fragment', note: '數度被逐出羅馬又數度復歸，終成帝國最盛的密教之一。' },
            { title_zh: '申辯（論巫術）', title_orig: 'Apologia / Pro se de magia', author: '阿普列尤斯', era: '約公元 158 年', place: '北非‧薩布拉塔', language: '拉丁文', status: 'whole', note: '被岳家控以巫術致富妻的法庭自辯詞，全篇逐條回應：買魚做什麼、為何家中藏一尊小神像、為何深夜行祕儀。古代唯一一份完整的巫術審判辯護，也是羅馬如何劃分「宗教」與「巫術」的實務界線。' },
            { title_zh: '密特拉教在軍中', title_orig: 'Mithraism in the Roman army', author: '各地密特拉窟銘文與浮雕', era: '公元 1–4 世紀', language: '拉丁文', status: 'inscription', note: '幾無經典傳世，全靠遺址與銘文重建；七階入教制與軍團分布是研究重點。與希臘卷 Λ 互見（該卷收禮文，此卷收制度）。' },
            { title_zh: '不敗太陽神國教化', title_orig: 'Sol Invictus', author: '綴輯（銘文、錢幣、《奧古斯都史》）', era: '公元 274 年起', language: '拉丁文', status: 'fragment', note: '奧勒良立為帝國主神；一神化傾向在異教內部的最後一次制度嘗試。' },
          ],
        },
        {
          key: 'rv-superstitio', label: '新迷信', label_en: 'The New Superstition',
          desc: '羅馬官府最早注意到基督徒時的兩份文件。兩份都不在論教義，只在論一件事：一個不肯向皇帝像獻香的社團該怎麼辦。希臘卷 Ψ 收異教作家的譏刺與駁論，此處收官方文書。',
          works: [
            { title_zh: '編年史 十五‧44（尼祿嫁禍）', title_orig: 'Annales XV.44', author: '塔西佗', era: '約公元 116 年', language: '拉丁文', status: 'whole', note: '為平息羅馬大火的流言，尼祿以基督徒頂罪，「其名出於提比略朝被總督本丟彼拉多處死的基利斯督」。非基督教文獻中最早、也最常被引用的耶穌之死旁證，並稱其教為「有害的迷信」。' },
            { title_zh: '書信 十‧96–97（與圖拉真論基督徒）', title_orig: 'Epistulae X.96–97', author: '小普林尼、圖拉真', era: '約公元 112 年', place: '比提尼亞', language: '拉丁文', status: 'whole', note: '總督請示如何審理：他令被告向皇帝像獻香、咒罵基督，肯做的即釋放。並記其人於天未亮時聚會、向基督唱詩如向神、共誓不偷不淫不背信。皇帝回覆定調：不主動搜捕、不受理匿名檢舉，被告不從則辦。羅馬對基督教的第一份成文政策。' },
          ],
        },
      ],
    },
    // ──────────────────────────── VI 終卷 ────────────────────────────
    {
      key: 'RVI', sigil: 'VI', name: '終卷', name_en: 'The Last Book',
      parallel: '啟示錄', clock: 'historical', span: '公元 382–529 年',
      summary: '西方的終結。與希臘卷 Ω 在同一年合攏——東邊查士丁尼關閉雅典學園，西邊本篤伐倒卡西諾山的阿波羅聖林。',
      divisions: [
        {
          key: 'rvi-altar', label: '勝利女神祭壇之爭', label_en: 'The Altar of Victory',
          works: [
            { title_zh: '撤除勝利女神祭壇與祭司經費（382）', title_orig: 'The removal of the Altar of Victory', author: '格拉提安', era: '公元 382 年', language: '拉丁文', status: 'fragment', note: '同時廢止火神女祭司與各祭司團的國家經費，並辭去大祭司長頭銜；羅馬國家宗教的財政基礎至此斷絕。' },
            {
              title_zh: '第三號陳情', title_orig: 'Relatio III', author: '敘馬庫斯',
              era: '公元 384 年', place: '羅馬', language: '拉丁文', status: 'whole',
              note: '「通往如此大奧祕的路不會只有一條。」',
              intro: '羅馬城長官上書皇帝，請求恢復元老院議事堂的勝利女神祭壇。他不辯教義，只訴諸傳統、饑荒與帝國的運祚，並借羅馬城本身之口發言。全文最有名的一句是「我們仰望同一片星空，共有同一個天，同一個宇宙環繞著我們；每個人以什麼方式尋求真理，這有什麼要緊？通往如此大奧祕的路不會只有一條。」安波羅修隨即上兩封書信駁斥，請求被拒。希臘卷 Ψ 互見。',
            },
            { title_zh: '駁敘馬庫斯二書', title_orig: 'Epistulae 17 et 18', author: '米蘭的安波羅修', era: '公元 384 年', language: '拉丁文', status: 'hostile', note: '主教方的答辯：真理不在傳統而在啟示，並以皇帝的信仰責任施壓。兩造並收，是本卷體例的示範。' },
          ],
        },
        {
          key: 'rvi-ban', label: '禁令與敗亡', label_en: 'Prohibition and Defeat',
          works: [
            { title_zh: '狄奧多西宗教禁令', title_orig: 'Codex Theodosianus XVI.10', author: '狄奧多西一世', era: '公元 391–392 年', language: '拉丁文', status: 'whole', note: '禁止一切獻祭、進廟與家中奉神像，違者以叛逆論；異教自此在法律上成為犯罪。' },
            { title_zh: '冷河之役（394）', title_orig: 'The Battle of the Frigidus', author: '綴輯（佐西姆斯、魯菲努斯、安波羅修）', era: '公元 394 年 9 月', language: '拉丁文／古希臘文', status: 'fragment', note: '歐根尼烏斯與阿爾波加斯特的軍隊打著朱庇特與赫拉克勒斯旗號迎戰狄奧多西——最後一支以異教旗號作戰的羅馬軍隊。' },
            { title_zh: '火神女祭司團解散', title_orig: 'The dissolution of the Vestals', author: '綴輯（普魯登提烏斯、佐西姆斯）', era: '約公元 394 年', language: '拉丁文', status: 'fragment', note: '守了一千一百年的城中聖火熄滅。' },
            { title_zh: '論異教宗教之謬', title_orig: 'De errore profanarum religionum', author: '菲爾米庫斯‧馬特爾努斯', era: '約公元 346–350 年', language: '拉丁文', status: 'hostile', note: '上書兩位皇帝要求以刀劍根除異教，並為此逐一詳述各密教的儀節與暗語。希臘卷 Λ 收正文，此處互見。' },
          ],
        },
        {
          key: 'rvi-end', label: '最後的節期與聖林', label_en: 'The Last Feast and the Last Grove',
          works: [
            { title_zh: '廢止牧神節（494）', title_orig: 'The abolition of the Lupercalia', author: '教宗格拉修一世《駁安德羅馬庫斯書》', era: '約公元 494 年', place: '羅馬', language: '拉丁文', status: 'whole', note: '羅馬最後一個仍在舉行的公共異教節期；教宗與元老貴族的往返書信顯示，此時仍有基督徒照舊參加。' },
            {
              title_zh: '本篤伐倒卡西諾山的阿波羅聖林（529）', title_orig: 'Gregorius Magnus, Dialogi II.8',
              author: '大額我略一世', era: '公元 593–594 年（記 529 年事）', place: '義大利‧卡西諾山',
              language: '拉丁文', status: 'whole',
              note: '全藏經之末：與雅典學園關閉同年。',
              intro: '大額我略記載：本篤抵達卡西諾山時，山頂仍有一座阿波羅神殿、一尊神像與一片供獻祭的聖林，附近農民照舊前往祭拜。本篤砸毀神像、推倒祭壇、伐倒聖林，就地建起兩座禮拜堂。傳統繫此事於公元 529 年——正是查士丁尼在雅典關閉柏拉圖學園的同一年。東西兩端在同一年合攏，希臘卷 Ω 與羅馬卷 VI 因此同止於此。這不是編者的安排，是史料本來就長這樣。',
            },
          ],
        },
      ],
    },
  ],
}
