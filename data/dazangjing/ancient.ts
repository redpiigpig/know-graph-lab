import type { DazangEra } from './types'

// ─────────────────────────────────────────────────────────────────────────
// 古代基督教大藏經
//
// 年代結界（「八百／四百」雙軌死線）：
//   基督教文獻收錄至 公元 800 年（涵蓋前七次大公會議與東西方教父時代終結；
//                                查理曼加冕、第二次尼西亞 787 為界）。
//   猶太教文獻收錄至 公元 400 年（涵蓋第二聖殿時期至耶柔米時代，此為基督教
//                                與猶太學術交流的最後斷層點；耶路撒冷塔木德、
//                                米書拿、早期米德拉什入藏，巴比倫塔木德擋於門外）。
//
// 範圍：800 年前基督教文獻、400 年前猶太教文獻、古代異端文獻、外教提及基督教
//       的見證／批判文獻。書目為策展骨架，多數跨連到站內既有對照工具。
// ─────────────────────────────────────────────────────────────────────────

export const ANCIENT_ERA: DazangEra = {
  key: 'ancient',
  name: '古代基督教大藏經',
  name_en: 'Ancient Christian Canon (to 800 CE)',
  glyph: '古',
  subtitle: '經‧律‧論‧史傳‧譯校‧書信‧禮儀‧詩文‧宣道‧類書',
  boundary: '基督教文獻收錄至 800 年（前七次大公會議終結）；猶太教文獻收錄至 400 年（耶柔米與拉比學術最後交集）。',
  enabled: true,
  collections: [
    // ═══════════════════════════════════════════════════════ 1. 經藏
    {
      key: 'jing',
      name: '經藏',
      name_en: 'Scriptures',
      glyph: '經',
      genres: '正典‧第二正典‧次經‧偽典',
      summary: '神聖啟示的源頭。大公教會確立的正典聖經（各教會聯集約「百卷大正典」），以及附編「外典經藏」——意圖被當作聖經閱讀、卻被大公教會或歷史淘汰的「影子聖經」。',
      portal: { to: '/scripture', label: '聖經多版本對照' },
      divisions: [
        {
          key: 'canon',
          label: '正典經藏部',
          label_en: 'Canonical Scriptures',
          desc: '舊約（律法書‧歷史書‧智慧詩歌書‧大小先知書）與新約（四福音‧使徒行傳‧保羅書信‧大公書信‧啟示錄）；含各教會次經與第二正典。',
          works: [
            { title_zh: '摩西五經', title_orig: 'Pentateuch / Torah', note: '創世記‧出埃及記‧利未記‧民數記‧申命記', link: '/scripture' },
            { title_zh: '歷史書與智慧詩歌書', title_orig: 'Historical & Wisdom Books', note: '約書亞記至以斯帖記；約伯記‧詩篇‧箴言‧傳道書‧雅歌', link: '/scripture' },
            { title_zh: '大小先知書', title_orig: 'Prophets', note: '以賽亞至瑪拉基', link: '/scripture' },
            { title_zh: '四福音與使徒行傳', title_orig: 'Gospels & Acts', link: '/scripture' },
            { title_zh: '保羅書信與大公書信', title_orig: 'Pauline & Catholic Epistles', link: '/scripture' },
            { title_zh: '啟示錄', title_orig: 'Revelation / Apocalypse', link: '/scripture' },
            { title_zh: '第二正典與次經', title_orig: 'Deuterocanon & Apocrypha', note: '多比傳‧猶滴傳‧智慧篇‧便西拉智訓‧巴錄書‧瑪加伯上下‧厄斯德拉一二書‧瑪拿西禱詞‧詩篇 151 等（各教會 canon 範圍不一）', link: '/apocrypha' },
          ],
        },
        {
          key: 'extracanon',
          label: '外典經藏附編（影子聖經）',
          label_en: 'Extra-Canonical Scriptures',
          desc: '與百卷正典鏡像對齊的影子圖書館：偽托先祖使徒之名、模仿正典文體、曾遊走正典邊緣的書卷。',
          works: [
            { title_zh: '以諾一書', title_orig: '1 Enoch', era: '前 3–1 世紀', note: '猶大書引用；衣索匹亞教會列為正典', link: '/apocrypha' },
            { title_zh: '禧年書', title_orig: 'Jubilees', era: '前 2 世紀', note: '重寫創世記與出埃及；昆蘭發現希伯來殘卷', link: '/apocrypha' },
            { title_zh: '以諾二書‧十二族長遺訓‧摩西升天記', title_orig: '2 Enoch / Testaments of the Twelve Patriarchs / Assumption of Moses', link: '/apocrypha' },
            { title_zh: '以賽亞升天記‧亞當夏娃生平‧巴錄二三書', title_orig: 'Ascension of Isaiah / Life of Adam and Eve / 2–3 Baruch', link: '/apocrypha' },
            { title_zh: '以斯拉續篇（以斯拉四書）‧所羅門詩篇‧西比拉神諭', title_orig: '4 Ezra / Psalms of Solomon / Sibylline Oracles', link: '/apocrypha' },
            { title_zh: '新約偽福音群', title_orig: 'Apocryphal Gospels', note: '多馬福音‧彼得福音‧雅各原始福音‧尼哥德慕福音（彼拉多行傳）‧多馬嬰孩福音', link: '/apocrypha' },
            { title_zh: '新約偽行傳與偽啟示', title_orig: 'Apocryphal Acts & Apocalypses', note: '彼得行傳‧保羅與底克拉行傳‧約翰行傳‧彼得啟示錄‧保羅啟示錄', link: '/apocrypha' },
            { title_zh: '諾斯底經卷（拿戈瑪第文庫）', title_orig: 'Nag Hammadi Library', note: '真理福音‧腓力福音‧約翰密傳‧埃及人福音‧猶大福音‧抹大拉瑪利亞福音', link: '/gnostic' },
            { title_zh: '黑馬牧人書', title_orig: 'Shepherd of Hermas', era: '2 世紀', note: '末世異象與靈修寓言；西乃抄本收錄，列為經藏附錄', link: '/apocrypha' },
          ],
        },
      ],
    },
    // ═══════════════════════════════════════════════════════ 2. 律藏
    {
      key: 'lu',
      name: '律藏',
      name_en: 'Canons & Ecclesiastical Law',
      glyph: '律',
      genres: '信經‧教令‧教規‧會規',
      summary: '教會運作的骨架。大公會議與地方會議的信經與教令、使徒教規與教會憲典、修道規則，以及 400 年前猶太口傳律法的核心。',
      portal: { to: '/creeds', label: '信條與大公會議' },
      divisions: [
        {
          key: 'councils',
          label: '大公會議部',
          label_en: 'Ecumenical & Local Councils',
          desc: '前七次大公會議信經與教令（尼西亞 325 至第二次尼西亞 787）及重要地方會議。',
          works: [
            { title_zh: '第一次尼西亞會議', title_orig: 'Council of Nicaea', era: '325', note: '尼西亞信經；反亞流主義', link: '/creeds' },
            { title_zh: '第一次君士坦丁堡會議', title_orig: 'Council of Constantinople I', era: '381', note: '尼西亞-君士坦丁堡信經；聖靈論', link: '/creeds' },
            { title_zh: '以弗所會議', title_orig: 'Council of Ephesus', era: '431', note: 'Theotokos；居利羅十二章', link: '/creeds' },
            { title_zh: '迦克墩會議', title_orig: 'Council of Chalcedon', era: '451', note: '一位格兩本性；引發東方分裂', link: '/creeds' },
            { title_zh: '第二、三次君士坦丁堡與第二次尼西亞', title_orig: 'Constantinople II–III / Nicaea II', era: '553 / 680–81 / 787', note: '三章案‧一志論‧聖像敬禮', link: '/creeds' },
            { title_zh: '地方會議教令', title_orig: 'Local Synods', note: '安提阿‧迦太基‧老底嘉‧艾爾維拉‧君士坦丁堡 692（特路羅）等', link: '/canon-law' },
          ],
        },
        {
          key: 'canons',
          label: '教令與教規部',
          label_en: 'Apostolic Canons & Decretals',
          works: [
            { title_zh: '十二使徒遺訓', title_orig: 'Didache', era: '1–2 世紀', note: '最早的洗禮、聖餐與教會秩序手冊', link: '/apocrypha' },
            { title_zh: '使徒教規（八十五條）', title_orig: 'Apostolic Canons', link: '/canon-law' },
            { title_zh: '使徒憲典', title_orig: 'Apostolic Constitutions', era: '4 世紀', note: '敘利亞編成的教會法律與禮儀大全' },
            { title_zh: '希波律陀《使徒傳統》', title_orig: 'Hippolytus, Apostolic Tradition', era: '3 世紀' },
            { title_zh: '查士丁尼法典（宗教部分）', title_orig: 'Codex Justinianus / Novellae', era: '6 世紀', note: '帝國立法中的教會法' },
            { title_zh: '狄奧多西法典（宗教部分）', title_orig: 'Codex Theodosianus', era: '438' },
          ],
        },
        {
          key: 'monastic',
          label: '修道規則部',
          label_en: 'Monastic Rules',
          works: [
            { title_zh: '帕科繆規章', title_orig: 'Rule of Pachomius', era: '4 世紀', note: '最早的集體隱修會規（埃及）' },
            { title_zh: '大巴西流規章', title_orig: 'Basil, Asketikon / Rules', era: '4 世紀', note: '東方修道制度根基' },
            { title_zh: '聖本篤會規', title_orig: 'Rule of St. Benedict', era: '6 世紀', note: '西方隱修制度的典範' },
            { title_zh: '大師規章‧該撒留會規', title_orig: 'Regula Magistri / Rule of Caesarius', era: '6 世紀' },
          ],
        },
        {
          key: 'jewish-law',
          label: '猶太律部',
          label_en: 'Jewish Law (to 400 CE)',
          desc: '口傳律法的核心——與初代教父釋經平行對話的猶太法典（400 年死線內）。',
          works: [
            { title_zh: '米書拿', title_orig: 'Mishnah', era: '約 200', note: '口傳律法核心，拉比猶大編定' },
            { title_zh: '陀塞他', title_orig: 'Tosefta', era: '約 300', note: '米書拿的補編' },
            { title_zh: '耶路撒冷塔木德（早期地層）', title_orig: 'Jerusalem Talmud', era: '約 350–400', note: '與俄利根、耶柔米同時空的巴勒斯坦拉比論辯' },
          ],
        },
      ],
    },
    // ═══════════════════════════════════════════════════════ 3. 論藏
    {
      key: 'lun',
      name: '論藏',
      name_en: 'Treatises & Exegesis',
      glyph: '論',
      genres: '論‧辯（護教詞）‧駁‧註‧疏‧釋',
      summary: '教父用血淚與智慧為信仰披上的「重裝鎧甲」。護教、反異端、系統教義、釋經、神祕主義，以及作為「底色與對手」的猶太哲學與異端思想。',
      portal: { to: '/fathers', label: '教父著作' },
      divisions: [
        {
          key: 'apologia',
          label: '護教詞部',
          label_en: 'Apologetics',
          desc: '面對帝國與異教的防禦著作。',
          works: [
            { title_zh: '游斯丁《第一、第二護教詞》《駁特里風護教詞》', title_orig: 'Justin Martyr, Apologies / Dialogue with Trypho', era: '2 世紀', link: '/fathers' },
            { title_zh: '特土良《護教辯》', title_orig: 'Tertullian, Apologeticus', era: '約 197', link: '/fathers' },
            { title_zh: '致丟格那妥書', title_orig: 'Epistle to Diognetus', era: '2 世紀', note: '護教文學名篇', link: '/apocrypha' },
            { title_zh: '亞他那哥拉《為基督徒請願》‧提阿非羅《致奧托呂古》', title_orig: 'Athenagoras / Theophilus, To Autolycus', link: '/fathers' },
            { title_zh: '塔提安《致希臘人書》‧米努修《屋大維》', title_orig: 'Tatian, Oratio / Minucius Felix, Octavius', link: '/fathers' },
            { title_zh: '拉克坦提烏《神聖原理》‧亞挪比烏《駁異教》', title_orig: 'Lactantius, Institutes / Arnobius, Adversus Nationes', era: '3–4 世紀', link: '/fathers' },
            { title_zh: '奧古斯丁《上帝之城》', title_orig: 'Augustine, De Civitate Dei', era: '5 世紀', note: '護教兼歷史神學巨著', link: '/fathers' },
          ],
        },
        {
          key: 'adversus',
          label: '反異端部',
          label_en: 'Against Heresies',
          desc: '對抗內部分裂與異端的清洗戰。',
          works: [
            { title_zh: '愛任紐《駁異端論》', title_orig: 'Irenaeus, Adversus Haereses', era: '約 180', note: '駁諾斯底主義的奠基之作', link: '/fathers' },
            { title_zh: '特土良《規誡異端》《駁馬吉安》《駁普拉克西亞》', title_orig: 'Tertullian, De Praescriptione / Adversus Marcionem / Adversus Praxean', link: '/fathers' },
            { title_zh: '希波律陀《駁諸異端》', title_orig: 'Hippolytus, Refutatio Omnium Haeresium', link: '/fathers' },
            { title_zh: '亞他那修《駁亞流辭》', title_orig: 'Athanasius, Orationes contra Arianos', era: '4 世紀', link: '/fathers' },
            { title_zh: '愛比法紐《破百異端駁（藥箱）》', title_orig: 'Epiphanius, Panarion', era: '4 世紀', note: '古代異端百科全書', link: '/fathers' },
            { title_zh: '奧古斯丁《駁摩尼教》《駁多納徒派》《駁伯拉糾》', title_orig: 'Augustine, Anti-Manichaean / Anti-Donatist / Anti-Pelagian', link: '/fathers' },
          ],
        },
        {
          key: 'dogmatics',
          label: '系統與教義部',
          label_en: 'Systematic Dogmatics',
          works: [
            { title_zh: '俄利根《基要原理論》', title_orig: 'Origen, De Principiis', era: '3 世紀', note: '史上第一部系統神學', link: '/fathers' },
            { title_zh: '亞他那修《論道成肉身》', title_orig: 'Athanasius, De Incarnatione', link: '/fathers' },
            { title_zh: '巴西流《論聖靈》‧尼撒的貴格利《大要理問答》', title_orig: 'Basil, On the Holy Spirit / Gregory of Nyssa, Catechetical Oration', link: '/fathers' },
            { title_zh: '奧古斯丁《論三位一體》《信望愛手冊》《論基督教教義》', title_orig: 'Augustine, De Trinitate / Enchiridion / De Doctrina Christiana', link: '/fathers' },
            { title_zh: '利奧《大卷》', title_orig: 'Leo the Great, Tome', era: '449', link: '/creeds' },
            { title_zh: '波愛修斯《神學短論》', title_orig: 'Boethius, Opuscula Sacra', era: '6 世紀', link: '/fathers' },
            { title_zh: '大馬士革約翰《正統信仰闡述》《知識泉源》', title_orig: 'John of Damascus, De Fide Orthodoxa / Fount of Knowledge', era: '8 世紀', note: '東方教父的系統總結', link: '/fathers' },
          ],
        },
        {
          key: 'exegesis',
          label: '釋經與釋祕部',
          label_en: 'Exegesis & Pesher',
          desc: '「註」（逐句）與「疏」（靈意）並重；附死海社群的「釋祕」解經。',
          works: [
            { title_zh: '俄利根《雅歌疏》《約翰福音註》《論詩篇》', title_orig: 'Origen, Commentaries', link: '/fathers' },
            { title_zh: '屈梭多模《創世記／馬太／約翰／羅馬書講疏》', title_orig: 'Chrysostom, Homilies (as commentary)', link: '/fathers' },
            { title_zh: '奧古斯丁《創世記字義解》《詩篇詮釋》', title_orig: 'Augustine, De Genesi ad Litteram / Enarrationes in Psalmos', link: '/fathers' },
            { title_zh: '安波羅修《六日創造論》‧希拉流《詩篇註》', title_orig: 'Ambrose, Hexaemeron / Hilary, Tractatus super Psalmos', link: '/fathers' },
            { title_zh: '耶柔米聖經註釋全集', title_orig: 'Jerome, Commentaries', link: '/fathers' },
            { title_zh: '死海古卷釋祕與創世記外傳', title_orig: 'Qumran Pesharim / Genesis Apocryphon', note: '哈巴谷‧那鴻‧詩篇釋祕（社群末世解經）', link: '/apocrypha' },
          ],
        },
        {
          key: 'mystical',
          label: '神祕主義部',
          label_en: 'Mystical Theology',
          works: [
            { title_zh: '偽丟尼修《天階序列》《神祕神學》《神名論》', title_orig: 'Pseudo-Dionysius, Corpus', era: '約 5–6 世紀', link: '/fathers' },
            { title_zh: '階梯約翰《神聖攀登天階》', title_orig: 'John Climacus, The Ladder', era: '7 世紀', link: '/fathers' },
            { title_zh: '艾瓦格留《修行論》《論禱告》', title_orig: 'Evagrius Ponticus, Praktikos / On Prayer', link: '/fathers' },
            { title_zh: '馬克西母《愛德四百則》《論神化》', title_orig: 'Maximus the Confessor', era: '7 世紀', link: '/fathers' },
            { title_zh: '尼尼微的以撒《靈修講道》', title_orig: 'Isaac of Nineveh', era: '7 世紀', note: '東敘利亞神祕主義' },
          ],
        },
        {
          key: 'jewish-heresy',
          label: '猶太哲學與異端思想部',
          label_en: 'Jewish & Heterodox Thought',
          desc: '作為論藏「基因、對手與工具」的猶太希臘化哲學、早期拉比釋經，以及諾斯底、摩尼教等異端思想原典。',
          works: [
            { title_zh: '斐洛全集', title_orig: 'Philo of Alexandria', era: '1 世紀', note: '教父神學術語的「原始碼」——希臘化猶太哲學' },
            { title_zh: '猶太教法理疏（早期拉比釋經）', title_orig: 'Early Rabbinic Exegesis', note: '針對米書拿的早期法理疏解' },
            { title_zh: '諾斯底論述（瓦倫廷派／塞特派）', title_orig: 'Valentinian & Sethian Gnosis', link: '/gnostic' },
            { title_zh: '摩尼教文獻', title_orig: 'Manichaean Texts', note: '科普特科里斯文書‧讚美詩集‧《摩尼光佛教法儀略》（吐魯番／敦煌出土）' },
          ],
        },
      ],
    },
    // ═══════════════════════════════════════════════════════ 4. 史傳藏
    {
      key: 'shizhuan',
      name: '史傳藏',
      name_en: 'History & Hagiography',
      glyph: '史',
      genres: '紀（史）‧傳‧世家（宗統）‧表（編年）‧志',
      summary: '基督宗教的真實人間史。剝離神話奇幻、追求史實與聖徒見證的通史、本傳、宗統記、編年表、典志，以及外教史家對基督教的見證。',
      portal: { to: '/fathers', label: '教父著作' },
      divisions: [
        {
          key: 'general-history',
          label: '通史部（史）',
          label_en: 'General Histories',
          works: [
            { title_zh: '優西比烏《教會史》', title_orig: 'Eusebius, Ecclesiastical History', era: '4 世紀', note: '教會史學的奠基之作', link: '/fathers' },
            { title_zh: '蘇格拉底／索佐門／提阿多勒／以瓦格留《教會史》', title_orig: 'Socrates / Sozomen / Theodoret / Evagrius Scholasticus', era: '5–6 世紀', link: '/fathers' },
            { title_zh: '比德《英吉利教會史》', title_orig: 'Bede, Historia Ecclesiastica Gentis Anglorum', era: '731' },
            { title_zh: '都爾的貴格利《法蘭克人史》‧奧羅修《駁異教史》', title_orig: 'Gregory of Tours / Orosius', era: '5–6 世紀' },
          ],
        },
        {
          key: 'lives',
          label: '本傳與殉道錄部（傳）',
          label_en: 'Saints & Martyrs',
          desc: '排除後期奇幻加工，僅收法庭筆錄或同時代目擊者紀錄。',
          works: [
            { title_zh: '亞他那修《安東尼傳》', title_orig: 'Athanasius, Life of Antony', era: '4 世紀', note: '隱修運動的範本傳記', link: '/fathers' },
            { title_zh: '耶柔米隱士傳（保羅／希拉里翁／馬爾庫斯）‧波西丟《奧古斯丁傳》', title_orig: 'Jerome, Lives / Possidius, Vita Augustini', link: '/fathers' },
            { title_zh: '《波利卡普殉道記》《佩珮圖亞與菲莉琪殉道記》《史基利殉道者行傳》', title_orig: 'Martyrdom accounts', link: '/apocrypha' },
            { title_zh: '帕拉迪烏《樂園（隱修史）》', title_orig: 'Palladius, Lausiac History', era: '約 420' },
          ],
        },
        {
          key: 'succession',
          label: '宗統記部（世家）',
          label_en: 'Episcopal Succession',
          works: [
            { title_zh: '《教宗世家記》', title_orig: 'Liber Pontificalis', note: '羅馬主教代際交替' },
            { title_zh: '優西比烏《使徒繼承名錄》', title_orig: 'Eusebius, Apostolic Succession Lists' },
          ],
        },
        {
          key: 'chronicle',
          label: '編年表部（表）',
          label_en: 'Chronicles',
          works: [
            { title_zh: '優西比烏—耶柔米《編年史》', title_orig: 'Eusebius–Jerome, Chronicon', note: '帝國年號與主教傳承對齊的時間軸' },
            { title_zh: '《復活節編年史》《亞歷山大編年史》', title_orig: 'Chronicon Paschale / Chronicon Alexandrinum' },
          ],
        },
        {
          key: 'topography',
          label: '典志部（志）',
          label_en: 'Pilgrimage & Topography',
          works: [
            { title_zh: '《波爾多朝聖者行記》《埃格里亞朝聖記》', title_orig: 'Itinerarium Burdigalense / Egeria, Itinerarium', era: '4 世紀' },
            { title_zh: '《聖地景觀志》《君士坦丁堡古蹟志》', title_orig: 'De Situ Terrae Sanctae / Notitia Urbis' },
          ],
        },
        {
          key: 'jewish-history',
          label: '猶太背景史料部',
          label_en: 'Jewish Background (to 400 CE)',
          works: [
            { title_zh: '約瑟夫斯《猶太古史》《猶太戰記》《駁亞皮溫》《自傳》', title_orig: 'Josephus, Complete Works', era: '1 世紀', note: '初代教會的必讀歷史背景' },
            { title_zh: '巴爾科赫巴戰地手札', title_orig: 'Bar Kokhba Letters', era: '2 世紀' },
          ],
        },
        {
          key: 'pagan-testimonia',
          label: '外史志部（外教見證）',
          label_en: 'Pagan Testimonia',
          desc: '羅馬史家與作家對基督教的第一手見證選集（Testimonia de Christianis）。',
          works: [
            { title_zh: '塔西佗《編年史》論尼祿焚城段', title_orig: 'Tacitus, Annals 15.44', era: '約 116' },
            { title_zh: '蘇埃托尼烏斯《革老丟傳》「基斯督」段', title_orig: 'Suetonius, Claudius 25' },
            { title_zh: '琉善《佩雷格里努斯之死》', title_orig: 'Lucian, De Morte Peregrini' },
            { title_zh: '約瑟夫斯「弗拉維約瑟夫斯見證」', title_orig: 'Testimonium Flavianum', note: '《猶太古史》18.63 論耶穌的爭議段落' },
          ],
        },
      ],
    },
    // ═══════════════════════════════════════════════════════ 5. 譯校藏
    {
      key: 'yijiao',
      name: '譯校藏',
      name_en: 'Translation & Textual Criticism',
      glyph: '譯',
      genres: '寶抄‧譯本‧校勘‧考異',
      summary: '人類傳遞啟示的「歷史肉身」。古卷寶抄、多語大譯本、校勘考異——讀者在此看的不是經文講什麼，而是經文如何在幾千年的戰火、語言轉換與神學角力中生存下來。',
      portal: { to: '/scripture', label: '聖經多版本對照' },
      divisions: [
        {
          key: 'manuscripts',
          label: '古卷寶抄部',
          label_en: 'Great Codices & Papyri',
          works: [
            { title_zh: '西乃抄本', title_orig: 'Codex Sinaiticus', era: '4 世紀', note: '含舊約、新約與外典的巨型抄本' },
            { title_zh: '梵蒂岡抄本‧亞歷山大抄本', title_orig: 'Codex Vaticanus / Alexandrinus', era: '4–5 世紀' },
            { title_zh: '以法蓮重寫寶抄', title_orig: 'Codex Ephraemi Rescriptus', era: '5 世紀', note: '教父講章底下覆蓋著被刮掉的古老聖經' },
            { title_zh: '伯撒抄本‧徹斯特貝蒂與波得美蒲草紙', title_orig: 'Codex Bezae / Chester Beatty & Bodmer Papyri' },
            { title_zh: '死海古卷聖經殘卷', title_orig: 'Dead Sea Biblical Scrolls', link: '/apocrypha' },
          ],
        },
        {
          key: 'versions',
          label: '多語大譯本部',
          label_en: 'Multilingual Versions',
          desc: '止於 4 世紀哥德文、5 世紀亞美尼亞文、7 世紀大秦景教殘卷（不含 9 世紀斯拉夫文，已屬中世紀）。',
          works: [
            { title_zh: '七十士譯本', title_orig: 'Septuagint (LXX)', era: '前 3–2 世紀', note: '希臘文舊約，初代教會的聖經', link: '/scripture' },
            { title_zh: '亞居拉／狄奧多田／辛馬庫譯本', title_orig: 'Aquila / Theodotion / Symmachus', era: '2 世紀', note: '猶太希臘文修訂譯本' },
            { title_zh: '武加大拉丁譯本（耶柔米）', title_orig: 'Vulgate', era: '4 世紀末', note: '統治西方中世紀一千年', link: '/scripture' },
            { title_zh: '古拉丁譯本', title_orig: 'Vetus Latina', link: '/scripture' },
            { title_zh: '別西大敘利亞譯本', title_orig: 'Peshitta', era: '5 世紀', link: '/scripture' },
            { title_zh: '科普特譯本（撒希地／波海里）', title_orig: 'Coptic (Sahidic / Bohairic)', link: '/scripture' },
            { title_zh: '哥德文譯本（烏斐拉）', title_orig: 'Gothic Bible (Ulfilas)', era: '4 世紀' },
            { title_zh: '亞美尼亞文‧喬治亞文‧衣索匹亞吉茲文譯本', title_orig: 'Armenian / Georgian / Geʿez', era: '5–6 世紀', link: '/scripture' },
            { title_zh: '大秦景教殘卷', title_orig: 'Jingjiao (Nestorian) Chinese Fragments', era: '7–8 世紀', note: '東方亞述教會傳入長安的漢文文獻' },
          ],
        },
        {
          key: 'critical',
          label: '校勘考異部',
          label_en: 'Textual Criticism',
          works: [
            { title_zh: '俄利根《六文本合參》', title_orig: 'Origen, Hexapla', era: '3 世紀', note: '六欄並列的舊約版本對校（近 50 卷羊皮紙）' },
            { title_zh: '耶柔米《武加大序言》《聖經問題》', title_orig: 'Jerome, Prefaces / Quaestiones', note: '「希伯來真理」（Hebraica Veritas）翻譯理論' },
            { title_zh: '塔古姆（翁克羅斯／約拿單）', title_orig: 'Targum Onkelos / Jonathan', note: '猶太會堂的亞蘭文意譯本' },
          ],
        },
      ],
    },
    // ═══════════════════════════════════════════════════════ 6. 書信藏
    {
      key: 'shuxin',
      name: '書信藏',
      name_en: 'Epistles',
      glyph: '信',
      genres: '函（牧函／教令）‧札（尺牘）',
      summary: '為冷峻的法典與神學大山注入真實的人間血肉與呼吸。古代的書信不只是問候，而是「未成冊的神學、帶血的教令、與跨國的外交博弈」。',
      portal: { to: '/fathers', label: '教父著作' },
      divisions: [
        {
          key: 'apostolic-letters',
          label: '使徒教父牧函部（函）',
          label_en: 'Apostolic Fathers',
          works: [
            { title_zh: '羅馬的革利免《致哥林多人書》', title_orig: '1 Clement', era: '約 96', link: '/apocrypha' },
            { title_zh: '伊格那丟七書', title_orig: 'Ignatius, Seven Epistles', era: '2 世紀', note: '巡迴殉道途中所寫的牧函', link: '/apocrypha' },
            { title_zh: '波利卡普《致腓立比人書》‧巴拿巴書', title_orig: 'Polycarp / Epistle of Barnabas', link: '/apocrypha' },
          ],
        },
        {
          key: 'father-letters',
          label: '教父書信集部',
          label_en: 'Patristic Letter Collections',
          works: [
            { title_zh: '居普良書信集', title_orig: 'Cyprian, Letters', era: '3 世紀', link: '/fathers' },
            { title_zh: '巴西流／納西盎貴格利書信', title_orig: 'Basil / Gregory of Nazianzus, Letters', link: '/fathers' },
            { title_zh: '安波羅修／耶柔米／奧古斯丁書信集', title_orig: 'Ambrose / Jerome / Augustine, Letters', link: '/fathers' },
            { title_zh: '利奧書信集‧大貴格利《登記書》', title_orig: 'Leo, Letters / Gregory the Great, Registrum', link: '/encyclicals' },
          ],
        },
        {
          key: 'spiritual-letters',
          label: '神學交鋒與靈修尺牘部（札）',
          label_en: 'Theological & Spiritual Letters',
          works: [
            { title_zh: '奧古斯丁與耶柔米論戰信', title_orig: 'Augustine–Jerome Correspondence', link: '/fathers' },
            { title_zh: '沙漠父老巴撒努菲與約翰答問札', title_orig: 'Letters of Barsanuphius and John', era: '6 世紀', note: '隱修士以書信回答靈修難題' },
            { title_zh: '亞他那修《節期書》', title_orig: 'Athanasius, Festal Letters', note: '第 39 封首列 27 卷新約正典' },
          ],
        },
        {
          key: 'church-state',
          label: '政教博弈部',
          label_en: 'Church & State',
          works: [
            { title_zh: '傑拉修《雙劍論》致阿納斯塔修', title_orig: 'Gelasius, Letter to Anastasius', era: '5 世紀末', note: '神權高於王權的「雙劍理論」', link: '/encyclicals' },
            { title_zh: '小普林尼致圖拉真書（及皇帝回信）', title_orig: 'Pliny–Trajan Correspondence', era: '約 112', note: '羅馬官僚的基督教對策公函' },
            { title_zh: '君士坦丁致教會與主教書', title_orig: 'Constantine, Letters to the Church' },
          ],
        },
      ],
    },
    // ═══════════════════════════════════════════════════════ 7. 禮儀藏
    {
      key: 'liyi',
      name: '禮儀藏',
      name_en: 'Liturgy',
      glyph: '儀',
      genres: '事奉聖禮‧聖事書‧日課‧祈禱',
      summary: '整座大藏經中最具「動態感」與「神聖感」的空間。規範信徒與祭司的敬拜、聖禮程序、日課時辰與祈禱文。',
      divisions: [
        {
          key: 'eucharist',
          label: '聖禮事奉部',
          label_en: 'Eucharistic Liturgies',
          works: [
            { title_zh: '金口約翰事奉聖禮‧巴西流事奉聖禮', title_orig: 'Liturgy of St. John Chrysostom / St. Basil', note: '拜占庭傳統兩大事奉聖禮' },
            { title_zh: '雅各事奉聖禮‧馬可事奉聖禮', title_orig: 'Liturgy of St. James / St. Mark', note: '耶路撒冷與亞歷山大傳統' },
            { title_zh: '阿迪與馬利聖頌', title_orig: 'Anaphora of Addai and Mari', note: '東敘利亞最古老的感恩經' },
            { title_zh: '羅馬彌撒正典', title_orig: 'Canon Romanus / Roman Mass' },
          ],
        },
        {
          key: 'sacramentary',
          label: '聖事書與日課部',
          label_en: 'Sacramentaries & Hours',
          works: [
            { title_zh: '傑拉修聖事書', title_orig: 'Gelasian Sacramentary', era: '7–8 世紀' },
            { title_zh: '大貴格利聖事密典', title_orig: 'Gregorian Sacramentary', era: '8–9 世紀', note: '教宗寄給查理曼大帝的官方標準版' },
            { title_zh: '拜占庭時辰經', title_orig: 'Horologion', note: '東方修士每日八個祈禱時辰規程' },
          ],
        },
        {
          key: 'mystagogy',
          label: '奧祕教理與洗禮部',
          label_en: 'Mystagogy & Baptism',
          works: [
            { title_zh: '耶路撒冷區利羅《奧祕教理講授》', title_orig: 'Cyril of Jerusalem, Mystagogical Catecheses', era: '4 世紀', link: '/fathers' },
            { title_zh: '《十二使徒遺訓》洗禮與聖餐規條', title_orig: 'Didache (Baptism & Eucharist)', link: '/apocrypha' },
          ],
        },
        {
          key: 'jewish-liturgy',
          label: '猶太禮儀部',
          label_en: 'Jewish Liturgy (to 400 CE)',
          works: [
            { title_zh: '希臘化會堂祈禱辭', title_orig: 'Hellenistic Synagogal Prayers' },
            { title_zh: '安息日獻祭之歌（天使禮儀）‧感恩聖詩卷', title_orig: 'Songs of the Sabbath Sacrifice / Hodayot', note: '死海社群的敬拜詩歌', link: '/apocrypha' },
          ],
        },
      ],
    },
    // ═══════════════════════════════════════════════════════ 8. 詩文藏
    {
      key: 'shiwen',
      name: '詩文藏',
      name_en: 'Poetry & Literature',
      glyph: '詩',
      genres: '聖詠‧讚歌‧哲理‧傳奇',
      summary: '整部大藏經中最具美感、最能觸動靈魂的藝術聖殿。神學在星空下被吟唱、在壁爐旁被當作故事講述——聖詠、哲理文學與敘事傳奇。',
      divisions: [
        {
          key: 'hymns',
          label: '聖詠讚美部',
          label_en: 'Hymns & Chants',
          works: [
            { title_zh: '以法蓮《讚美詩集／教導詩》', title_orig: 'Ephrem the Syrian, Hymns', era: '4 世紀', note: '敘利亞聖詩的高峰' },
            { title_zh: '羅曼努斯《孔塔基昂讚歌》', title_orig: 'Romanos the Melodist, Kontakia', era: '6 世紀' },
            { title_zh: '安波羅修聖詩‧普魯登修斯《日課詩集／殉道冠冕》', title_orig: 'Ambrosian Hymns / Prudentius, Cathemerinon / Peristephanon', link: '/fathers' },
            { title_zh: '塞多流斯《逾越節之歌》‧《阿卡提斯讚歌》', title_orig: 'Sedulius, Carmen Paschale / Akathist Hymn' },
          ],
        },
        {
          key: 'philosophical',
          label: '哲理與自傳文學部',
          label_en: 'Philosophical & Autobiographical',
          works: [
            { title_zh: '波愛修斯《哲學的慰藉》', title_orig: 'Boethius, Consolation of Philosophy', era: '6 世紀', note: '通篇用希臘哲學探討命運與上帝主權', link: '/fathers' },
            { title_zh: '奧古斯丁《懺悔錄》', title_orig: 'Augustine, Confessions', note: '西方第一部心靈自傳', link: '/fathers' },
            { title_zh: '普魯登修斯《靈魂爭戰（靈戰記）》', title_orig: 'Prudentius, Psychomachia', note: '寓意敘事詩的開端' },
          ],
        },
        {
          key: 'romance',
          label: '敘事傳奇部',
          label_en: 'Christian Romance',
          works: [
            { title_zh: '《巴拉姆與約沙法傳奇》', title_orig: 'Barlaam and Josaphat', era: '8 世紀前', note: '釋迦牟尼生平被基督教化的跨文化傳奇' },
            { title_zh: '《革利免遊記》', title_orig: 'Clementine Recognitions / Homilies', note: '偽托革利免的早期基督教小說' },
            { title_zh: '《七聖童傳說》', title_orig: 'Seven Sleepers of Ephesus' },
          ],
        },
      ],
    },
    // ═══════════════════════════════════════════════════════ 9. 宣道藏
    {
      key: 'xuandao',
      name: '宣道藏',
      name_en: 'Sermons & Sayings',
      glyph: '宣',
      genres: '講‧疏‧語錄',
      summary: '整部大藏經中唯一能聽到「群眾回音」的迴音壁。主教站在講台上對平民講道、沙漠長老的棒喝語錄——由速記員逐字抄錄而流傳。',
      portal: { to: '/fathers', label: '教父著作' },
      divisions: [
        {
          key: 'expository',
          label: '釋經講疏部',
          label_en: 'Expository Homilies',
          works: [
            { title_zh: '金口約翰《創世記／馬太／約翰福音講疏》《雕像講道》', title_orig: 'Chrysostom, Homilies', era: '4 世紀', note: '單《希臘教父全集》即佔 18 卷', link: '/fathers' },
            { title_zh: '奧古斯丁《講道集》《約翰福音講解》', title_orig: 'Augustine, Sermones / Tractates on John', link: '/fathers' },
            { title_zh: '俄利根講道集（路加／耶利米／約書亞）', title_orig: 'Origen, Homilies', link: '/fathers' },
            { title_zh: '大貴格利《福音書講道》《以西結書講道》', title_orig: 'Gregory the Great, Homilies', link: '/fathers' },
          ],
        },
        {
          key: 'festal',
          label: '節期與教理講道部',
          label_en: 'Festal & Catechetical Orations',
          works: [
            { title_zh: '納西盎貴格利《神學演講》', title_orig: 'Gregory of Nazianzus, Theological Orations', link: '/fathers' },
            { title_zh: '耶路撒冷區利羅《教理講授》', title_orig: 'Cyril of Jerusalem, Catechetical Lectures', link: '/fathers' },
            { title_zh: '尼撒貴格利／瑟琉古巴西流節期講道', title_orig: 'Festal Homilies', link: '/fathers' },
          ],
        },
        {
          key: 'desert-sayings',
          label: '沙漠語錄部',
          label_en: 'Sayings of the Desert Fathers',
          works: [
            { title_zh: '《沙漠教父言行錄》', title_orig: 'Apophthegmata Patrum', era: '4–5 世紀', note: '師徒問答體的隱修智慧語錄' },
            { title_zh: '艾瓦格留《實踐論格言》‧《教父金言集》', title_orig: 'Evagrius / Patristic Maxims' },
          ],
        },
        {
          key: 'rabbinic-homily',
          label: '拉比講疏部',
          label_en: 'Rabbinic Midrash (to 400 CE)',
          works: [
            { title_zh: '《創世記大注釋》《利未記大注釋》', title_orig: 'Genesis Rabbah / Leviticus Rabbah', era: '5 世紀前', note: '巴勒斯坦拉比的講道精華' },
            { title_zh: '《米基塔》《西弗瑞》', title_orig: 'Mekhilta / Sifre', note: '早期釋經米德拉什' },
          ],
        },
      ],
    },
    // ═══════════════════════════════════════════════════════ 10. 類書藏
    {
      key: 'leishu',
      name: '類書藏',
      name_en: 'Encyclopedic Reference',
      glyph: '類',
      genres: '類書‧法要‧工具‧曆算',
      summary: '修院認識世界的百科全書。把世俗知識重新分類、每一種分類都指向造物主——百科類書、修學法要、哲學工具與曆算自然之學。',
      divisions: [
        {
          key: 'encyclopedia',
          label: '百科類書部',
          label_en: 'Encyclopedias',
          works: [
            { title_zh: '塞維亞的伊西多爾《詞源（百科志）》《論萬物本性》', title_orig: 'Isidore of Seville, Etymologiae / De Natura Rerum', era: '7 世紀', note: '中世紀的「維基百科」，全書 20 卷' },
          ],
        },
        {
          key: 'curriculum',
          label: '修學法要部',
          label_en: 'Educational Manuals',
          works: [
            { title_zh: '卡西奧多羅斯《聖俗文獻指南（修學法要）》《論靈魂》', title_orig: 'Cassiodorus, Institutiones / De Anima', era: '6 世紀', note: '規定後世修道院必學「七藝」' },
            { title_zh: '奧古斯丁《論基督教教義》', title_orig: 'Augustine, De Doctrina Christiana', note: '基督教學術詮釋方法論', link: '/fathers' },
            { title_zh: '馬爾蒂亞努斯《文獻學與墨丘利的聯姻》', title_orig: 'Martianus Capella, De Nuptiis', note: '七藝的寓言教科書' },
          ],
        },
        {
          key: 'philosophy-tools',
          label: '哲學工具部',
          label_en: 'Philosophical Tools',
          desc: '不收柏拉圖、亞里斯多德原典，僅收「被教父改裝過」的邏輯學與哲學工具書。',
          works: [
            { title_zh: '波愛修斯譯註《波菲利引論》', title_orig: 'Boethius, trans. Porphyry Isagoge', era: '6 世紀', note: '教父與異端辯論「基督二性」時的邏輯學武器' },
            { title_zh: '波愛修斯《亞里斯多德範疇篇譯註》', title_orig: 'Boethius, Aristotelian Logic' },
          ],
        },
        {
          key: 'computus',
          label: '曆算與自然部',
          label_en: 'Computus & Natural Science',
          works: [
            { title_zh: '比德《論時間計算》《論萬物本性》', title_orig: 'Bede, De Temporum Ratione / De Natura Rerum', era: '8 世紀', note: '復活節曆算與自然知識' },
            { title_zh: '科斯馬斯《基督教地形志》', title_orig: 'Cosmas Indicopleustes, Christian Topography', era: '6 世紀' },
          ],
        },
      ],
    },
  ],
}
