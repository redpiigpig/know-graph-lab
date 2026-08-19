import type { HellenCanon } from './types'

// 希臘卷 Α–Ω 廿四卷。
// 前十四卷（Α–Ξ）按文本權威位階與成書早晚排；後十卷（Ο–Ω）按成書年代排，卷內亦由早到晚。

export const GREEK_CANON: HellenCanon = {
  key: 'greek',
  name: '希臘卷',
  name_en: 'The Greek Canon',
  glyph: '希',
  subtitle: '廿四卷 Α–Ω — 希臘傳統宗教的正藏',
  summary:
    '以希臘字母 Α–Ω 立廿四卷，呼應荷馬兩部史詩的分卷制。前十四卷按文本在希臘宗教中的權威位階與成書早晚排——荷馬與赫西俄德是希臘人真正當經在讀的東西，故居首（希羅多德 2.53：「是荷馬與赫西俄德替希臘人造了神譜，給諸神定了名號、職司與形貌」）；後十卷按成書年代排，卷內亦由早到晚，數卷因此自成一部衰亡史。拉丁文獻在希臘原典已佚、或拉丁是後世唯一傳承管道時，以「續典」身分入卷對照。',
  enabled: true,
  parts: [
    { key: 'p-canon', label: '本經部', label_en: 'The Scriptures', desc: '荷馬與赫西俄德——希臘人實際當經在讀的四部書，加上與之同源而僅存殘篇的史詩循環。', volumes: ['A', 'B', 'G', 'D', 'E'] },
    { key: 'p-genealogy', label: '譜系部', label_en: 'Genealogies', desc: '列祖世系與族群的遷徙建城；相當於創世記後半與出埃及記。', volumes: ['Z', 'H'] },
    { key: 'p-hero', label: '英雄部', label_en: 'Heroes', desc: '單身英雄的功業循環與泛希臘的聯合遠征；相當於士師記與約書亞記。', volumes: ['Th', 'I'] },
    { key: 'p-cult', label: '祭儀部', label_en: 'Cult and Mystery', desc: '成文祭儀法與入教祕儀。刻意置於神話段落，仿聖經把晚出的祭司律法安置在西奈山下；兩卷材料實為前 6–2 世紀，須看時代標記。', volumes: ['K', 'L'] },
    { key: 'p-land', label: '土地部', label_en: 'Land and City', desc: '回歸得地、城邦成立，直到保薩尼亞斯走遍希臘、在土地上指認神話——神話時間在此交棒給歷史時間。', volumes: ['M', 'N', 'X'] },
    { key: 'p-wisdom', label: '詩智部', label_en: 'Song and Wisdom', desc: '詩篇、箴言、約伯記、傳道書的希臘對位。', volumes: ['O', 'P', 'R', 'S'] },
    { key: 'p-prophet', label: '先知部', label_en: 'Oracle and Revelation', desc: '神從外面說話（神諭）與神在裡面顯現（啟示）兩種傳統。', volumes: ['T', 'U'] },
    { key: 'p-doctrine', label: '道理部', label_en: 'Doctrine and Life', desc: '系統神學與聖徒行傳；異教在最後三百年才長出的兩種文類。', volumes: ['Ph', 'Ch'] },
    { key: 'p-end', label: '終末部', label_en: 'Contest and End', desc: '與基督教的正面交鋒，以及神廟關閉的編年。', volumes: ['Ps', 'W'] },
  ],
  volumes: [
    // ──────────────────────────── Α 神譜 ────────────────────────────
    {
      key: 'A', sigil: 'Α', name: '神譜', name_en: 'Theogony',
      parallel: '創世記 1–2', clock: 'mythic', span: '前 8 世紀 – 公元 5 世紀（異版）',
      summary: '赫西俄德《神譜》為正文，其餘三系神譜作對觀欄並置。四版互斥，不作調和——這正是本藏經勝過任何一本「希臘神話故事集」之處。',
      divisions: [
        {
          key: 'a-main', label: '本文', label_en: 'The Received Theogony',
          works: [
            {
              title_zh: '神譜', title_orig: 'Θεογονία / Theogonia', author: '赫西俄德',
              era: '約前 8 世紀末至前 7 世紀初', place: '希臘‧彼奧提亞‧阿斯克拉', language: '古希臘文（六步格）',
              extent: '約 1,022 行', status: 'whole',
              note: '自混沌開篇，敘三代神權交替至宙斯確立統治。',
              intro: '現存最早的希臘系統性宇宙起源與諸神譜系詩。自混沌（卡俄斯）、大地（蓋亞）開始，經烏拉諾斯遭閹、克羅諾斯吞子、提坦之戰與提豐之亂，敘諸神世代更迭直至宙斯確立統治並分定職司。全詩以繆斯在赫利孔山授予詩人歌權開篇，等於自陳其權威來自神的委任。希羅多德視之與荷馬同為希臘人神觀的立法者，本藏經因此以之為 Α 卷本文。',
              seealso: '基督教大藏經‧前藏經藏‧創世神話部',
            },
          ],
        },
        {
          key: 'a-variant', label: '異版對觀', label_en: 'Rival Theogonies',
          desc: '同一文類的四個互斥版本，作對觀欄並置，如對觀福音。',
          works: [
            {
              title_zh: '德爾維尼紙草', title_orig: 'Papyrus Derveni', author: '佚名（俄耳甫斯派註釋者）',
              era: '約前 340–320 年抄本（所註詩作更早）', place: '希臘‧馬其頓‧德爾維尼', language: '古希臘文',
              status: 'inscription',
              note: '現存最早的希臘文書卷；俄耳甫斯神譜原文＋逐行寓意註釋。',
              intro: '1962 年出土於德爾維尼墓葬火堆的半焦紙草卷，是歐洲現存最古老的書卷。內容為一部俄耳甫斯神譜的引文與逐行寓意解經：宙斯吞下先祖的陽物（一說吞下先神本身）而重生萬有，註釋者則把諸神一一還原為氣、心智與必然。它同時見證了兩件事——希臘另有一套與赫西俄德全然不同的創世說，以及公元前五世紀已存在成熟的寓意釋經法。',
            },
            {
              title_zh: '俄耳甫斯狂詩神譜', title_orig: 'Ἱεροὶ Λόγοι ἐν Ῥαψῳδίαις / Rhapsodic Theogony', author: '託名俄耳甫斯',
              era: '約公元 1–2 世紀定型（材料遠早）', language: '古希臘文', extent: '傳為 24 卷', status: 'fragment',
              via: '達馬斯基烏斯《論第一原理》、普羅克洛註疏',
              note: '時間之神克羅諾斯生宇宙卵，法涅斯破卵而出。',
              intro: '新柏拉圖學派所引用的俄耳甫斯神譜標準本，原書已佚，靠達馬斯基烏斯與普羅克洛的引述綴輯。以無齡的時間（Chronos）為始，生出宇宙卵，光輝雌雄同體的法涅斯（Phanes）破卵而出，為第一王；歷經夜、烏拉諾斯、克羅諾斯而至宙斯，宙斯吞法涅斯以總攝萬有，末生戴奧尼索斯而遭提坦分屍——人由提坦灰燼所造，故兼具神性與罪。此一「原罪—淨化—復歸」結構，是異教中最接近救恩論的一套神話。',
            },
            {
              title_zh: '七穴（諸神之穴）', title_orig: 'Ἑπτάμυχος / Heptamychos', author: '敘羅斯的費瑞居德',
              era: '約前 6 世紀中葉', place: '希臘‧敘羅斯島', language: '古希臘文（散文）', status: 'fragment',
              note: '現存最早的散文神譜；宙斯、時間、大地三永恆者並立。',
              intro: '傳為希臘第一部散文著作。以宙斯（Zas）、時間（Chronos）與大地（Chthonie）三者本來就在、無所自來開篇，時間以自己的種子造出七穴中的諸神，宙斯化身為愛神並織就繡有大地與海洋的婚袍贈予新婦。它既不從混沌起、也不敘神權更迭，是與赫西俄德平行的另一條古老思路，並被古人視為哲學宇宙論的先聲。',
            },
            {
              title_zh: '譜系', title_orig: 'Γενεαλογίαι / Genealogiai', author: '阿爾戈斯的阿庫西勞',
              era: '約前 6 世紀末至前 5 世紀初', place: '希臘‧阿爾戈斯', language: '古希臘文（散文）', status: 'fragment',
              note: '把赫西俄德神譜改寫成散文並加以理性化的最早嘗試。',
            },
            {
              title_zh: '斯多噶寓意神譜', title_orig: 'Stoic allegorical theogony',
              author: '克呂西波斯、科爾努圖斯等', era: '前 3 世紀 – 公元 1 世紀', language: '古希臘文', status: 'fragment',
              note: '諸神即自然力：宙斯＝理性、赫拉＝氣、波塞頓＝水。',
              intro: '斯多噶學派為救回被哲學批評的神話而發展的解經路線：把諸神一一等同於自然元素與宇宙理性，把神譜讀成物理學。科爾努圖斯《希臘神學要覽》是現存最完整的一份。此路線後來被基督教護教者反過來使用——既然你們自己承認神話不可照字面讀，便不必再守它。',
            },
            {
              title_zh: '變形記（卷一：創世與四代說）', title_orig: 'Metamorphoses I', author: '奧維德',
              era: '公元 8 年', place: '羅馬', language: '拉丁文', track: 'latin', status: 'whole',
              note: '四代說是赫西俄德五族說的拉丁變體；中世紀歐洲認識希臘創世全靠這條線。',
            },
          ],
        },
      ],
    },
    // ──────────────────────────── Β 人類世代記 ────────────────────────────
    {
      key: 'B', sigil: 'Β', name: '人類世代記', name_en: 'The Ages of Man',
      parallel: '創世記 3–9', clock: 'mythic', span: '前 7 世紀 – 公元 2 世紀',
      summary: '人如何被造、如何失去神的同席、如何一代不如一代，以及一場滅世的洪水。等於希臘的太古史。',
      divisions: [
        {
          key: 'b-main', label: '本文', label_en: 'The Ages',
          works: [
            {
              title_zh: '工作與時日（神話段）', title_orig: 'Ἔργα καὶ Ἡμέραι / Opera et Dies', author: '赫西俄德',
              era: '約前 700 年', place: '希臘‧彼奧提亞', language: '古希臘文（六步格）',
              extent: '全詩 828 行，本卷取 1–201 行', status: 'whole',
              note: '普羅米修斯盜火、潘朵拉開甕、黃金至鐵的五族說。',
              intro: '全詩後半的農時勸誡歸 Π 箴言卷，本卷只取前段神話。普羅米修斯代人盜火，宙斯以潘朵拉為報復——她揭開甕蓋放出一切疾苦，唯「期望」留在甕內；接著是黃金、白銀、青銅、英雄、黑鐵五族一代不如一代，詩人自陳生在鐵族而恨不得早生或晚生。這是希臘唯一一套完整的墮落論，與創世記三章的功能位置相同，但責任歸屬相反：人受苦不因人犯罪，而因神記恨。',
            },
            {
              title_zh: '丟卡利翁洪水', title_orig: 'The Deluge of Deukalion',
              author: '諸家傳述（品達、阿波羅多洛斯、奧維德等）', era: '前 5 世紀起見於文獻', language: '古希臘文', status: 'fragment',
              note: '宙斯滅銅族，丟卡利翁與皮拉造方舟得生，投石造人。',
              intro: '希臘的挪亞。宙斯決意滅絕青銅族，普羅米修斯示其子丟卡利翁造櫃，與妻皮拉漂流九日而止於帕爾納索斯山。二人求嗣，神諭令「拋擲大母的骨骸」，遂拾石回擲，男石成男、女石成女——希臘人由此得名「石民」。此說散見諸家而無專書，本卷綴輯。',
              seealso: '基督教大藏經‧前藏經藏‧洪水史詩部',
            },
            {
              title_zh: '普羅米修斯盜火諸傳', title_orig: 'The Prometheus tradition',
              author: '赫西俄德、埃斯庫羅斯、柏拉圖《普羅塔哥拉》等', era: '前 8–4 世紀', language: '古希臘文', status: 'fragment',
              note: '獻祭分份的欺瞞、火的竊取、人類技藝的來源三個母題。',
            },
          ],
        },
      ],
    },
    // ──────────────────────────── Γ 大戰記 ────────────────────────────
    {
      key: 'G', sigil: 'Γ', name: '大戰記', name_en: 'The Great War',
      parallel: '撒母耳記', clock: 'mythic', span: '約前 750–700 年',
      summary: '《伊利亞特》單卷。希臘人千年來的共同課本，也是諸神性格與神人關係最權威的紀錄。',
      divisions: [
        {
          key: 'g-main', label: '本文', label_en: 'The Iliad',
          works: [
            {
              title_zh: '伊利亞特', title_orig: 'Ἰλιάς / Ilias', author: '荷馬',
              era: '約前 750–700 年', place: '小亞細亞西岸（愛奧尼亞）', language: '古希臘文（六步格）',
              extent: '全 24 卷，15,693 行', status: 'whole',
              note: '阿基里斯之怒；戰爭第十年的五十一天。',
              intro: '西方最早的完整文學作品，也是希臘宗教最核心的文本。全詩只寫特洛伊戰爭第十年的五十一天，自阿基里斯與阿伽門農爭執起，至赫克托爾葬禮止。宗教上的分量在於：它決定了奧林匹亞諸神的形貌、名號、職司與相互關係，記錄了祈禱、獻祭、誓約、屍體處置的完整儀節，並提出了此後希臘一切神義論的原始問題——宙斯的意志與命運（moira）孰先，以及神為何偏袒。',
            },
          ],
        },
      ],
    },
    // ──────────────────────────── Δ 歸返記 ────────────────────────────
    {
      key: 'D', sigil: 'Δ', name: '歸返記', name_en: 'The Homecoming',
      parallel: '列王紀下', clock: 'mythic', span: '約前 720–670 年',
      summary: '《奧德賽》單卷。勝利之後的崩壞、漂流與返鄉；也是希臘文獻中最完整的招魂與冥府紀錄。',
      divisions: [
        {
          key: 'd-main', label: '本文', label_en: 'The Odyssey',
          works: [
            {
              title_zh: '奧德賽', title_orig: 'Ὀδύσσεια / Odysseia', author: '荷馬',
              era: '約前 720–670 年', place: '小亞細亞西岸（愛奧尼亞）', language: '古希臘文（六步格）',
              extent: '全 24 卷，12,110 行', status: 'whole',
              note: '奧德修斯十年歸途；卷十一為希臘最早的冥府之行。',
              intro: '與《伊利亞特》並列本經。宗教上最重的是卷十一「招魂」（Nekyia）——奧德修斯依女巫指示掘坑、以血引魂，與亡母、阿基里斯、阿伽門農對話，並見審判者米諾斯與受罰的坦塔洛斯、西緒福斯。這是希臘文獻中最早也最完整的來世圖景，此後一切冥府敘述（柏拉圖、維吉爾、乃至但丁）皆以之為原型。全詩另貫穿一條神學主線：宙斯在開篇即宣告人的災禍多半是自作，這是荷馬對神義論的正面答覆。',
            },
          ],
        },
      ],
    },
    // ──────────────────────────── Ε 循環補遺 ────────────────────────────
    {
      key: 'E', sigil: 'Ε', name: '循環補遺', name_en: 'The Cyclic Remains',
      parallel: '次經', clock: 'mythic', span: '前 8–6 世紀（僅存摘要與引文）',
      summary: '與荷馬同源、卻只剩內容摘要的史詩諸篇。與 Γ、Δ 分卷不合卷，是為了讓讀者一眼看出全本與殘篇地位不同。',
      divisions: [
        {
          key: 'e-troy', label: '特洛伊循環', label_en: 'The Trojan Cycle',
          desc: '主要靠普羅克洛《文選》的內容摘要傳世，另有零星引文與紙草。',
          works: [
            { title_zh: '賽普里亞', title_orig: 'Κύπρια / Cypria', author: '傳為賽普勒斯的斯塔西努斯', era: '約前 7 世紀', language: '古希臘文', extent: '傳為 11 卷', status: 'fragment', via: '普羅克洛《文選》摘要', parent: '史詩循環', note: '戰爭的起因：金蘋果、帕里斯的裁判、艦隊集結、伊菲革涅亞獻祭。' },
            { title_zh: '埃塞俄比斯', title_orig: 'Αἰθιοπίς / Aethiopis', author: '傳為米利都的阿克提努斯', era: '約前 7 世紀', language: '古希臘文', extent: '傳為 5 卷', status: 'fragment', via: '普羅克洛《文選》摘要', parent: '史詩循環', note: '亞馬遜女王與衣索比亞王門農之死；阿基里斯陣亡並被接往白島。' },
            { title_zh: '小伊利亞特', title_orig: 'Ἰλιὰς μικρά / Ilias Mikra', author: '傳為米蒂利尼的萊斯克斯', era: '約前 7 世紀', language: '古希臘文', extent: '傳為 4 卷', status: 'fragment', via: '普羅克洛《文選》摘要', parent: '史詩循環', note: '武器之爭、埃阿斯自殺、木馬的建造。' },
            { title_zh: '伊利昂陷落', title_orig: 'Ἰλίου πέρσις / Iliou Persis', author: '傳為米利都的阿克提努斯', era: '約前 7 世紀', language: '古希臘文', extent: '傳為 2 卷', status: 'fragment', via: '普羅克洛《文選》摘要', parent: '史詩循環', note: '木馬入城、祭壇前的屠殺、卡珊德拉受辱——希臘人褻瀆神聖的總帳，是其後歸途災禍的原因。' },
            { title_zh: '歸返', title_orig: 'Νόστοι / Nostoi', author: '傳為特羅曾的阿吉亞斯', era: '約前 7 世紀', language: '古希臘文', extent: '傳為 5 卷', status: 'fragment', via: '普羅克洛《文選》摘要', parent: '史詩循環', note: '各將領的歸途與敗亡；阿伽門農遇害。' },
            { title_zh: '特勒戈努斯', title_orig: 'Τηλεγόνεια / Telegonia', author: '傳為昔蘭尼的歐伽蒙', era: '約前 6 世紀', language: '古希臘文', extent: '傳為 2 卷', status: 'fragment', via: '普羅克洛《文選》摘要', parent: '史詩循環', note: '奧德修斯死於己子之手，全循環於此收束。' },
          ],
        },
        {
          key: 'e-thebes', label: '底比斯循環', label_en: 'The Theban Cycle',
          works: [
            { title_zh: '伊底帕斯記', title_orig: 'Οἰδιπόδεια / Oidipodeia', author: '傳為科林斯的基奈同', era: '約前 8–7 世紀', language: '古希臘文', status: 'fragment', parent: '史詩循環', note: '斯芬克斯之謎與伊底帕斯的罪；悲劇所本的原始敘事。' },
            { title_zh: '底比斯記（七雄攻底比斯）', title_orig: 'Θηβαΐς / Thebais', author: '佚名（古人或歸荷馬）', era: '約前 8–7 世紀', language: '古希臘文', status: 'fragment', parent: '史詩循環', note: '伊底帕斯的詛咒與七雄攻城；古代評價僅次於荷馬。' },
            { title_zh: '後繼者', title_orig: 'Ἐπίγονοι / Epigonoi', author: '佚名', era: '約前 7 世紀', language: '古希臘文', status: 'fragment', parent: '史詩循環', note: '七雄之子再攻底比斯而克之。' },
          ],
        },
        {
          key: 'e-latin', label: '拉丁續典', label_en: 'Latin Continuations',
          desc: '希臘本已佚而拉丁本完整者；本卷唯一能讀到全篇敘事的來源。',
          works: [
            { title_zh: '底比斯戰記', title_orig: 'Thebais', author: '斯塔提烏斯', era: '公元 80–92 年', place: '羅馬', language: '拉丁文', extent: '全 12 卷', track: 'latin', status: 'whole', note: '七雄攻底比斯最完整的古代敘事，底比斯循環希臘本已佚，全靠此書。' },
            { title_zh: '後荷馬記（特洛伊的陷落）', title_orig: 'Τὰ μεθ᾿ Ὅμηρον / Posthomerica', author: '斯米爾納的昆圖斯', era: '約公元 4 世紀', language: '古希臘文', extent: '全 14 卷', status: 'whole', note: '晚期補綴《伊利亞特》到城破之間的空白，可代讀已佚的循環諸篇。' },
          ],
        },
      ],
    },
    // ──────────────────────────── Ζ 列祖傳 ────────────────────────────
    {
      key: 'Z', sigil: 'Ζ', name: '列祖傳', name_en: 'The Patriarchs',
      parallel: '創世記 10–50', clock: 'mythic', span: '前 6 世紀 – 公元 2 世紀',
      summary: '開篇列國表，其後六大家系。與神交合而生族的譜系記述，是希臘族群自我定位的根據。',
      divisions: [
        {
          key: 'z-nations', label: '列國表', label_en: 'The Table of Nations',
          desc: '相當於創世記十章，材料實際只有一章之量，故不另立卷。',
          works: [
            { title_zh: '希倫三子分族', title_orig: 'The genealogy of Hellen', author: '赫西俄德傳統，見於《婦女名錄》與阿波羅多洛斯', era: '前 6 世紀起', language: '古希臘文', status: 'fragment', note: '多羅斯生多利安人、埃俄羅斯生伊奧利亞人、克蘇托斯之子伊翁與阿凱俄斯生愛奧尼亞與亞該亞人——全希臘由一祖分出四族。' },
          ],
        },
        {
          key: 'z-catalogue', label: '婦女名錄', label_en: 'The Catalogue of Women',
          works: [
            {
              title_zh: '婦女名錄（又名「或如是女子」）', title_orig: 'Γυναικῶν Κατάλογος / Ἠοῖαι', author: '託名赫西俄德',
              era: '約前 6 世紀', language: '古希臘文（六步格）', extent: '傳為 5 卷', status: 'fragment',
              via: '紙草殘葉與古注引文', note: '以「或如是女子……」起句，逐位列出與神交合而生英雄族的凡間女子。',
              intro: '《神譜》的續篇，把神譜接到人間：每一段以固定套語「或如是女子」開頭，敘一位凡間女子受某神眷顧而生下一族之祖，全希臘的貴族世系由此串成一張大表。它在功能上正是希臘的列祖傳——族群的合法性來自某位神親自介入的譜系。原書已佚，二十世紀以來靠俄克喜林庫斯紙草大量復原，是本卷的骨架。',
            },
          ],
        },
        {
          key: 'z-houses', label: '六大家系', label_en: 'The Six Houses',
          works: [
            { title_zh: '伊那科斯家系（阿爾戈斯）', title_orig: 'The house of Inachos', author: '綴輯', language: '古希臘文', status: 'fragment', note: '伊俄流亡埃及生埃帕福斯，衍出埃及、腓尼基、克里特三支——希臘人自陳其祖出於東方。' },
            { title_zh: '阿革諾耳家系（腓尼基與底比斯）', title_orig: 'The house of Agenor', author: '綴輯', language: '古希臘文', status: 'fragment', note: '歐羅巴被劫、卡德摩斯尋妹不獲而建底比斯。' },
            { title_zh: '刻克洛普斯家系（雅典）', title_orig: 'The house of Kekrops', author: '綴輯（含雅典地方史家）', language: '古希臘文', status: 'fragment', note: '土生王統與雅典娜、波塞頓爭城；雅典人「土著」意識的根據。' },
            { title_zh: '坦塔洛斯—珀羅普斯家系（邁錫尼）', title_orig: 'The house of Tantalos and Pelops', author: '綴輯', language: '古希臘文', status: 'fragment', note: '從觸怒諸神的坦塔洛斯到阿特柔斯兄弟的世仇，是三大悲劇家最愛的血脈詛咒。' },
            { title_zh: '埃俄羅斯家系', title_orig: 'The house of Aiolos', author: '綴輯', language: '古希臘文', status: 'fragment', note: '西緒福斯、阿塔瑪斯、克瑞透斯諸支，衍出伊奧爾科斯與科林斯王統。' },
            { title_zh: '阿爾卡斯與拉刻代蒙家系', title_orig: 'The Arcadian and Laconian houses', author: '綴輯', language: '古希臘文', status: 'fragment', note: '阿爾卡狄亞的呂卡翁與斯巴達王統。' },
          ],
        },
        {
          key: 'z-compend', label: '彙編本', label_en: 'The Handbooks',
          desc: '帝國期回頭把散佚譜系重新整編的著作——正典整理總在信仰動搖之後。',
          works: [
            {
              title_zh: '書庫（神話全編）', title_orig: 'Βιβλιοθήκη / Bibliotheca', author: '託名阿波羅多洛斯',
              era: '約公元 1–2 世紀', language: '古希臘文', extent: '全 3 卷（末段殘，有《節要》補）', status: 'whole',
              note: '唯一系統性的希臘神話全編，自神譜貫穿到特洛伊歸返。',
              intro: '古代唯一一部從創世一路寫到特洛伊歸返的希臘神話全編，體例乾淨、幾無文采，正因如此成為最可靠的譜系工具書。全書分三卷，末段在中世紀佚失，靠十四世紀發現的《節要》（Epitome）補足。要留意的是：希臘人自己並不讀它——它是羅馬時代的整理品，本藏經因此把它列在荷馬與赫西俄德之後，而非之前。',
            },
            { title_zh: '傳說集', title_orig: 'Fabulae', author: '希吉努斯', era: '公元 2 世紀', language: '拉丁文', extent: '約 300 則', track: 'latin', status: 'whole', note: '補阿波羅多洛斯佚失段落的唯一材料。' },
            { title_zh: '天文志（星座神話）', title_orig: 'De astronomia', author: '希吉努斯', era: '公元 2 世紀', language: '拉丁文', track: 'latin', status: 'whole', note: '星座的神話由來，保存大量他處不存的異說。' },
            { title_zh: '變形記', title_orig: 'Metamorphoses', author: '奧維德', era: '公元 8 年', language: '拉丁文', extent: '全 15 卷', track: 'latin', status: 'whole', note: '中世紀與文藝復興歐洲認識希臘神話的主要管道；作為並行證人與希臘諸本對讀。' },
          ],
        },
      ],
    },
    // ──────────────────────────── Η 遷徙與建城 ────────────────────────────
    {
      key: 'H', sigil: 'Η', name: '遷徙與建城', name_en: 'Migration and Foundation',
      parallel: '出埃及記', clock: 'mythic', span: '前 5 世紀 – 公元 2 世紀',
      summary: '族群如何離開舊地、渡海、得地、立城。希臘版的出埃及——但方向相反：他們是從東方回到希臘。',
      divisions: [
        {
          key: 'h-migration', label: '遷徙', label_en: 'Migrations',
          works: [
            {
              title_zh: '乞援女', title_orig: 'Ἱκέτιδες / Hiketides', author: '埃斯庫羅斯',
              era: '約前 463 年', place: '雅典', language: '古希臘文', status: 'whole',
              note: '達那俄斯五十女自埃及逃回阿爾戈斯求庇——現存最完整的「出埃及」敘事。',
              intro: '達那俄斯率五十女逃離埃及、渡海回到祖先伊俄的故鄉阿爾戈斯，向當地王求取庇護。全劇幾乎全由歌隊唱成，是現存最古老的悲劇形態之一。宗教上的分量在於它是希臘唯一一部以「族群出離埃及、求神庇護、獲准定居」為主軸的完整作品，與出埃及敘事的結構對位極近，而神學重心落在「求庇者神聖不可侵犯」這條古老的宙斯律法上。',
            },
            { title_zh: '卡德摩斯建底比斯', title_orig: 'The founding of Thebes', author: '綴輯（歐里庇得斯、阿波羅多洛斯、保薩尼亞斯）', language: '古希臘文', status: 'fragment', note: '腓尼基王子隨神諭跟牛而行、殺龍、播齒生武士；希臘人自承字母來自腓尼基的神話表述。' },
            { title_zh: '珀羅普斯自呂底亞西渡', title_orig: 'The coming of Pelops', author: '綴輯（品達《奧林匹亞頌》一為主）', language: '古希臘文', status: 'fragment', note: '伯羅奔尼撒（「珀羅普斯之島」）得名所自；奧林匹亞競技的建制傳說。' },
          ],
        },
        {
          key: 'h-ktisis', label: '建城詩', label_en: 'Foundation Poems',
          desc: '殖民建城必先請德爾菲神諭，故此類文獻同時是神諭史料。',
          works: [
            { title_zh: '皮托競技勝利頌 四、五（昔蘭尼建城）', title_orig: 'Pythian Odes 4–5', author: '品達', era: '前 462 年', language: '古希臘文', status: 'whole', note: '巴托斯奉德爾菲神諭赴利比亞建昔蘭尼——現存最完整的建城神諭敘事。' },
            { title_zh: '歷史‧卷四（昔蘭尼建城異說）', title_orig: 'Historiae IV', author: '希羅多德', era: '約前 440 年', language: '古希臘文', status: 'whole', note: '同一建城事件的兩個城邦版本並存，見證神諭傳說如何被各方改寫。' },
            { title_zh: '建城詩殘篇集', title_orig: 'Κτίσεις / Ktiseis', author: '諸家（阿波羅尼俄斯等）', era: '前 3 世紀', language: '古希臘文', status: 'fragment', note: '希臘化時期為各殖民城市編寫的建城起源詩，多僅存篇名與零句。' },
          ],
        },
      ],
    },
    // ──────────────────────────── Θ 英雄志 ────────────────────────────
    {
      key: 'Th', sigil: 'Θ', name: '英雄志', name_en: 'The Book of Heroes',
      parallel: '士師記', clock: 'mythic', span: '前 6 世紀 – 公元 2 世紀',
      summary: '單身英雄的功業循環。赫拉克勒斯的結構——受命、蒙難、力勝、女人、慘死——與參孫幾乎重疊。',
      divisions: [
        {
          key: 'th-herakles', label: '赫拉克勒斯', label_en: 'Herakles',
          works: [
            { title_zh: '赫拉克勒斯記', title_orig: 'Ἡράκλεια / Herakleia', author: '羅德島的佩珊德羅斯', era: '約前 6 世紀', language: '古希臘文', extent: '傳為 2 卷', status: 'fragment', note: '最早把十二功勞編成定數的史詩；獅皮與大棒的形象自此定型。' },
            { title_zh: '赫拉克勒斯記', title_orig: 'Ἡράκλεια / Herakleia', author: '哈利卡納索斯的帕尼亞西斯', era: '約前 5 世紀初', language: '古希臘文', extent: '傳為 14 卷', status: 'fragment', note: '古代所列九大抒情／史詩家之一，其書為後世十二功勞敘述之所本。' },
            { title_zh: '十二功勞', title_orig: 'The Twelve Labours', author: '綴輯（以阿波羅多洛斯《書庫》二卷為骨）', language: '古希臘文', status: 'whole', note: '受命於歐律斯透斯，自涅墨亞獅至取刻耳柏洛斯；本卷以《書庫》為底本綴各家異說。' },
            { title_zh: '特拉基斯少女', title_orig: 'Τραχίνιαι / Trachiniai', author: '索福克勒斯', era: '約前 450–425 年', language: '古希臘文', status: 'whole', note: '得伊阿妮拉誤用毒血袍害死丈夫，赫拉克勒斯自焚於俄塔山而升為神——英雄成神的關鍵文本。' },
            { title_zh: '赫拉克勒斯', title_orig: 'Ἡρακλῆς μαινόμενος', author: '歐里庇得斯', era: '約前 416 年', language: '古希臘文', status: 'whole', note: '功成歸家卻被降瘋而殺妻殺子；把「神為何如此」的問題推到極處。' },
          ],
        },
        {
          key: 'th-heroes', label: '諸英雄', label_en: 'The Other Heroes',
          works: [
            { title_zh: '忒修斯諸傳', title_orig: 'The Theseus tradition', author: '綴輯（巴克基利得斯、普魯塔克《忒修斯傳》、雅典地方史家）', language: '古希臘文', status: 'fragment', note: '六路除暴、迷宮殺牛、統一阿提卡；雅典的國族英雄，功業表刻意仿赫拉克勒斯。' },
            { title_zh: '珀爾修斯諸傳', title_orig: 'The Perseus tradition', author: '綴輯（費瑞居德、品達、阿波羅多洛斯）', language: '古希臘文', status: 'fragment', note: '金雨受孕、斬美杜莎、救安德羅美達；邁錫尼王統的開創者。' },
            { title_zh: '柏勒洛豐諸傳', title_orig: 'The Bellerophon tradition', author: '綴輯（《伊利亞特》六卷為最早）', language: '古希臘文', status: 'fragment', note: '馴飛馬、斬奇美拉，終因欲飛上天而墜——僭越的典型。' },
            { title_zh: '阿塔蘭忒諸傳', title_orig: 'The Atalanta tradition', author: '綴輯', language: '古希臘文', status: 'fragment', note: '獵豬、賽跑、金蘋果；女性英雄的少數個案，末以褻瀆聖域而變獅收場。' },
            { title_zh: '英雄崇拜銘文與英雄祠', title_orig: 'Hero cult inscriptions', author: '各城邦', era: '前 6 – 公元 3 世紀', language: '古希臘文', status: 'inscription', note: '英雄不只是故事——各地有墳、有祠、有定期血祭。此類銘文是英雄「信仰」而非「文學」的證據。' },
          ],
        },
      ],
    },
    // ──────────────────────────── Ι 遠征記 ────────────────────────────
    {
      key: 'I', sigil: 'Ι', name: '遠征記', name_en: 'The Expeditions',
      parallel: '約書亞記', clock: 'mythic', span: '前 3 世紀 – 公元 5 世紀',
      summary: '泛希臘的聯合行動：取金羊毛、獵卡呂冬野豬。特洛伊之戰的預演。',
      divisions: [
        {
          key: 'i-argo', label: '阿爾戈遠征', label_en: 'The Argonauts',
          works: [
            {
              title_zh: '阿爾戈英雄記', title_orig: 'Ἀργοναυτικά / Argonautica', author: '羅德島的阿波羅尼俄斯',
              era: '約前 3 世紀中葉', place: '亞歷山卓', language: '古希臘文', extent: '全 4 卷', status: 'whole',
              note: '希臘化時代唯一完整傳世的長篇史詩。',
              intro: '伊阿宋率五十英雄乘阿爾戈號赴科爾基斯取金羊毛。宗教上值得注意的有三處：一是全程由阿波羅神諭導引，等於一部航行中的神諭實錄；二是薩摩色雷斯入教一節，是現存最早提到該島祕儀的文獻；三是美狄亞的巫術描寫，為後世一切魔法文學定下模型。它同時是希臘化詩學的代表作——博學、細膩、對神明的態度已明顯疏遠。',
            },
            { title_zh: '俄耳甫斯阿爾戈英雄記', title_orig: 'Ὀρφέως Ἀργοναυτικά / Orphic Argonautica', author: '託名俄耳甫斯', era: '約公元 4–5 世紀', language: '古希臘文', extent: '1,376 行', status: 'whole', note: '改由俄耳甫斯第一人稱敘述，全程以歌與祕儀取勝而非武力；晚期俄耳甫斯派的自我表述。' },
            { title_zh: '阿爾戈英雄記', title_orig: 'Argonautica', author: '瓦勒里烏斯‧弗拉庫斯', era: '約公元 70–90 年', language: '拉丁文', extent: '8 卷（未完）', track: 'latin', status: 'whole', note: '阿波羅尼俄斯的拉丁對讀本。' },
          ],
        },
        {
          key: 'i-hunt', label: '卡呂冬狩獵', label_en: 'The Calydonian Hunt',
          works: [
            { title_zh: '卡呂冬野豬諸傳', title_orig: 'The Calydonian Boar', author: '綴輯（《伊利亞特》九卷、巴克基利得斯、阿波羅多洛斯）', language: '古希臘文', status: 'fragment', note: '因忘記獻祭阿爾忒彌斯而招來巨豬——漏祭必受罰的教訓文本。' },
          ],
        },
      ],
    },
    // ──────────────────────────── Κ 祭儀法 ────────────────────────────
    {
      key: 'K', sigil: 'Κ', name: '祭儀法', name_en: 'The Sacred Laws',
      parallel: '利未記', clock: 'historical', span: '前 6 世紀 – 公元 3 世紀',
      summary: '希臘宗教真正的「律法書」。全部出自石刻，不是書。這一卷在中文世界近乎空白，是本藏經原創性最高的部分。',
      divisions: [
        {
          key: 'k-purity', label: '淨罪法', label_en: 'Cathartic Laws',
          works: [
            {
              title_zh: '塞利農特淨罪法', title_orig: 'Lex sacra from Selinous', author: '塞利農特城邦',
              era: '約前 460 年', place: '西西里‧塞利農特', language: '古希臘文（多利安方言）', status: 'inscription', link: '/hellenika/text/cgrn-13',
              note: '鉛板兩面；規定祖靈祭與殺人者的淨化程序。',
              intro: '1981 年公開的一塊鉛板，兩面各刻一部法。A 面規定對「不潔的」與「純淨的」祖靈的獻祭時程與牲品，B 面則逐步指示殺人者如何自我淨化：向外邦人或本邦人求接待、獻豬、洗滌、然後方可與人同席。這是古希臘現存最詳盡的血污淨化程序，與利未記的贖罪條例可逐條對讀。',
            },
            { title_zh: '昔蘭尼淨罪法', title_orig: 'The Cyrene Cathartic Law', author: '昔蘭尼城邦（自稱奉阿波羅神諭）', era: '約前 4 世紀末', place: '利比亞‧昔蘭尼', language: '古希臘文', status: 'inscription', note: '什一奉獻、聖所進入資格、產婦與死屋的不潔期、對「來訪者」（幽靈）的處置。' },
            { title_zh: '進所條例集', title_orig: 'Entry regulations (leges sacrae)', author: '各聖所', era: '前 5 – 公元 3 世紀', language: '古希臘文', status: 'inscription', note: '誰可入、須隔多久、穿什麼、不得攜入何物；散在各地神廟門柱。' },
          ],
        },
        {
          key: 'k-calendar', label: '祭曆', label_en: 'Sacrificial Calendars',
          works: [
            { title_zh: '埃爾希亞祭曆', title_orig: 'The Erchia sacrificial calendar', author: '阿提卡‧埃爾希亞區', era: '約前 375–350 年', place: '雅典近郊', language: '古希臘文', status: 'inscription', link: '/hellenika/text/cgrn-52', note: '一個村落全年的獻祭表：日期、神名、牲品、價錢、由誰主持——古代最完整的地方祭曆。' },
            { title_zh: '科斯祭曆與祭司法', title_orig: 'The Coan sacred calendar', author: '科斯島', era: '約前 4 世紀', language: '古希臘文', status: 'inscription', link: '/hellenika/text/cgrn-86', note: '含祭司職位的拍賣與世襲規定，可見祭司職如何成為一種財產。' },
            { title_zh: '尼科馬科斯曆法修訂', title_orig: 'The Nikomachos recodification', author: '雅典（尼科馬科斯主持）', era: '前 410–399 年', place: '雅典', language: '古希臘文', status: 'inscription', note: '民主復辟後重新刊刻全城祭曆，並因此引發訴訟——古代唯一一場關於「祭儀該花多少錢」的公開審判。' },
            { title_zh: '安達尼亞祕儀規章', title_orig: 'The Andania mysteries regulation', author: '美塞尼亞‧安達尼亞', era: '前 92/91 年', place: '希臘‧美塞尼亞', language: '古希臘文', status: 'inscription', link: '/hellenika/text/cgrn-222', note: '現存最完整的一部祕儀施行細則：職司、服裝、經費、秩序維持、罰則，一應俱全。' },
          ],
        },
        {
          key: 'k-theory', label: '祭儀理論', label_en: 'Theory of Sacrifice',
          works: [
            { title_zh: '論虔敬', title_orig: 'Περὶ εὐσεβείας / De pietate', author: '泰奧弗拉斯托斯', era: '約前 4 世紀末', language: '古希臘文', status: 'fragment', via: '波菲利《論戒食》大段引錄', note: '主張獻祭原以穀果為始、血祭是墮落後的產物；古代唯一一部祭祀理論專著。' },
            { title_zh: '論戒食動物', title_orig: 'Περὶ ἀποχῆς ἐμψύχων / De abstinentia', author: '波菲利', era: '約公元 270 年', language: '古希臘文', extent: '全 4 卷', status: 'whole', note: '從哲學與宗教兩面反對血祭，並保存泰奧弗拉斯托斯的祭祀史；異教內部的祭儀改革宣言。' },
            { title_zh: '帝王崇拜祭儀銘文', title_orig: 'Imperial cult regulations', author: '希臘各城邦', era: '前 1 – 公元 3 世紀', language: '古希臘文', status: 'inscription', note: '希臘城邦以希臘文、依希臘儀節奉祀在世皇帝；執行者是希臘人，故列本卷而不列羅馬卷。' },
          ],
        },
      ],
    },
    // ──────────────────────────── Λ 祕儀書 ────────────────────────────
    {
      key: 'L', sigil: 'Λ', name: '祕儀書', name_en: 'The Book of Mysteries',
      parallel: '至聖所與贖罪日', clock: 'historical', span: '前 6 世紀 – 公元 4 世紀',
      summary: '入教、死而復生、來世的通行證。希臘宗教中唯一許諾個人救贖的一支，也是基督教最直接的競爭對手。',
      divisions: [
        {
          key: 'l-eleusis', label: '厄琉息斯', label_en: 'Eleusis',
          works: [
            { title_zh: '荷馬詩頌‧致得墨忒耳', title_orig: 'Ὁμηρικὸς Ὕμνος εἰς Δημήτραν', author: '託名荷馬', era: '約前 7 世紀末', language: '古希臘文', extent: '495 行', status: 'whole', note: '厄琉息斯祕儀的創教敘事：珀耳塞福涅被劫、母神哀行、祕儀由神親授。末句明言見過者有福、未見者死後不得同分。' },
            { title_zh: '厄琉息斯銘文與祭司法', title_orig: 'Eleusinian inscriptions', author: '雅典與厄琉息斯', era: '前 5 – 公元 3 世紀', language: '古希臘文', status: 'inscription', note: '聖休戰佈告、初穗奉獻令、祭司世家（歐摩爾波斯族與刻律克斯族）的職權劃分。' },
          ],
        },
        {
          key: 'l-orphic', label: '俄耳甫斯與酒神', label_en: 'Orphic-Bacchic',
          works: [
            {
              title_zh: '金葉片（死者通行證）', title_orig: 'The Orphic-Bacchic gold tablets / lamellae',
              author: '入教者（佚名）', era: '約前 5 世紀 – 公元 2 世紀',
              place: '南義大利、克里特、帖薩利亞等地墓葬', language: '古希臘文', status: 'inscription',
              extent: '現存約 40 餘片',
              note: '隨葬薄金片，刻著在冥府該說的話。',
              intro: '折疊塞入死者口中或置於胸前的薄金片，刻著幾行給亡魂的指示與口令：不要喝右邊那泓忘川，要走左邊記憶之泉，並向守衛者說「我是大地與星天之子，但我的族類屬天」。有些直接宣告「你已從人變成神」。這是古代世界唯一一批由信徒本人帶進墳墓的救贖文書，也是異教中最接近「因入教而得永生」的證據，分量極重。',
            },
            { title_zh: '奧爾比亞骨片', title_orig: 'The Olbia bone tablets', author: '俄耳甫斯派信徒', era: '約前 5 世紀', place: '黑海‧奧爾比亞', language: '古希臘文', status: 'inscription', note: '刻「生—死—生．真理．狄奧尼索斯．俄耳甫斯派」等字樣；現存最早的俄耳甫斯派自稱。' },
            { title_zh: '酒神祕儀入教規章', title_orig: 'Bacchic mystery regulations', author: '各地信團', era: '前 3 – 公元 2 世紀', language: '古希臘文', status: 'inscription', note: '入教者名冊、職司分工、聚會規約；可見祕教團體的組織形態。' },
          ],
        },
        {
          key: 'l-foreign', label: '外來密教', label_en: 'Imported Mysteries',
          works: [
            { title_zh: '薩摩色雷斯大神祕儀', title_orig: 'The Mysteries of the Great Gods of Samothrace', author: '綴輯（阿波羅尼俄斯、入教者名錄銘文）', era: '前 4 世紀 – 公元 4 世紀', language: '古希臘文', status: 'fragment', note: '航海者的保命祕儀；入教者名錄石刻是研究其社會構成的主要材料。' },
            { title_zh: '密特拉禮文', title_orig: 'The Mithras Liturgy (PGM IV.475–834)', author: '佚名', era: '約公元 4 世紀', language: '古希臘文', status: 'inscription', parent: '希臘魔法紙草', note: '第一人稱的升天儀軌：屏息、見火門、與太陽神面對面。是否真屬密特拉教有爭議，但作為升天啟示文本無可取代。' },
            { title_zh: '伊西斯自述文', title_orig: 'The Isis aretalogies (Kyme, Maroneia, Andros)', author: '伊西斯祭司傳統', era: '前 1 – 公元 2 世紀', language: '古希臘文', status: 'inscription', note: '「我是伊西斯，萬國之主……是我立定法律，人不能廢」——第一人稱神的自我宣告，句式與約翰福音的「我是」極近。' },
            { title_zh: '金驢記‧卷十一', title_orig: 'Metamorphoses XI', author: '阿普列尤斯', era: '約公元 170 年', language: '拉丁文', track: 'latin', status: 'whole', note: '全部古代文獻中唯一的第一人稱入教皈依敘事，希臘文沒有對應物。' },
          ],
        },
        {
          key: 'l-hostile', label: '敵證', label_en: 'Hostile Witnesses',
          desc: '為駁斥而抄錄，卻因此保存了口令與儀節。使用時須知敘述框架受敵手支配。',
          works: [
            { title_zh: '勸勉希臘人（祕儀章）', title_orig: 'Προτρεπτικὸς πρὸς Ἕλληνας', author: '亞歷山卓的克萊門', era: '約公元 195 年', language: '古希臘文', status: 'hostile', note: '為揭穿而複述厄琉息斯與酒神祕儀的口令與聖物，是該口令唯一的文獻來源。' },
            { title_zh: '論異教宗教之謬', title_orig: 'De errore profanarum religionum', author: '菲爾米庫斯‧馬特爾努斯', era: '約公元 346–350 年', language: '拉丁文', status: 'hostile', track: 'latin', note: '逐一詳述各密教的儀節與暗語以求皇帝取締；反成本卷最細的祕儀資料。羅馬卷六互見。' },
          ],
        },
      ],
    },
    // ──────────────────────────── Μ 分族記 ────────────────────────────
    {
      key: 'M', sigil: 'Μ', name: '分族記', name_en: 'The Return and the Dispersion',
      parallel: '王國分裂與被擄歸回', clock: 'mythic', span: '前 5 世紀起見於文獻',
      summary: '英雄時代結束之後：赫拉克勒斯子孫回歸得地、愛奧尼亞人東遷、以及三百年的大殖民。希臘世界的形狀在此定型。',
      divisions: [
        {
          key: 'm-return', label: '回歸', label_en: 'The Return of the Heracleidae',
          works: [
            { title_zh: '赫拉克勒斯子孫回歸', title_orig: 'The Return of the Heracleidae', author: '綴輯（品達、希羅多德、阿波羅多洛斯、保薩尼亞斯）', language: '古希臘文', status: 'fragment', note: '多利安人以「歸還祖產」為名南下取伯羅奔尼撒——征服被講成回歸，與約書亞得地的合法性論述同型。' },
            { title_zh: '愛奧尼亞東遷', title_orig: 'The Ionian Migration', author: '綴輯（希羅多德一卷、帕烏薩尼亞斯七卷）', language: '古希臘文', status: 'fragment', note: '雅典為母邦、十二城為聯盟，以泛愛奧尼亞祭為紐帶。' },
          ],
        },
        {
          key: 'm-colonies', label: '大殖民', label_en: 'The Great Colonisation',
          works: [
            { title_zh: '殖民神諭集', title_orig: 'Colonisation oracles', author: '德爾菲', era: '前 8–6 世紀', language: '古希臘文', status: 'fragment', note: '幾乎每一次建城都先問德爾菲；此一制度使德爾菲成為全希臘唯一的中央權威。' },
            { title_zh: '殖民城市祖神祭銘文', title_orig: 'Founder-cult inscriptions', author: '各殖民城市', era: '前 7 – 公元 2 世紀', language: '古希臘文', status: 'inscription', note: '建城者死後葬於市集中央、受英雄祭；政治權威由此取得宗教形式。' },
          ],
        },
      ],
    },
    // ──────────────────────────── Ν 城邦紀年 ────────────────────────────
    {
      key: 'N', sigil: 'Ν', name: '城邦紀年', name_en: 'Chronicles of the Cities',
      parallel: '歷代志', clock: 'historical', span: '前 7 – 前 3 世紀',
      summary: '立法者向神請法、城邦以神諭建制、波斯戰爭被讀成神意。歷史時間在此正式開始。',
      divisions: [
        {
          key: 'n-lawgivers', label: '立法者與神諭', label_en: 'Lawgivers and Oracles',
          works: [
            { title_zh: '呂庫古大諭令', title_orig: 'The Great Rhetra', author: '斯巴達（傳為呂庫古得自德爾菲）', era: '約前 7 世紀', language: '古希臘文', status: 'fragment', via: '普魯塔克《呂庫古傳》', note: '希臘唯一一部自稱直接得自神諭的憲法。' },
            { title_zh: '梭倫詩殘篇', title_orig: 'The poems of Solon', author: '梭倫', era: '約前 594 年', language: '古希臘文', status: 'fragment', note: '以詩自陳立法之義；「大地作證」一段以神明為社會契約的見證人。' },
            { title_zh: '埃庇米尼德淨化雅典', title_orig: 'Epimenides and the purification of Athens', author: '綴輯（亞里斯多德、第歐根尼‧拉爾修）', era: '約前 600 年', language: '古希臘文', status: 'fragment', note: '瘟疫中應召自克里特來，放羊隨處而祭「未識之神」——使徒行傳十七章的背景文本。' },
          ],
        },
        {
          key: 'n-chronicle', label: '編年', label_en: 'Chronicles',
          works: [
            { title_zh: '帕羅斯編年碑', title_orig: 'Marmor Parium', author: '佚名', era: '前 264/263 年', place: '希臘‧帕羅斯島', language: '古希臘文', status: 'inscription', note: '自刻克洛普斯（前 1582）逐條記到前 299 年的大事年表，神話與歷史同列一軸——古人自己的年代學。' },
            { title_zh: '雅典地方史', title_orig: 'Ἀτθίδες / Atthides', author: '赫拉尼科斯、菲洛科羅斯等', era: '前 5–3 世紀', language: '古希臘文', status: 'fragment', note: '按年編排雅典的節期、祭司、聖物與神諭；本卷最重要的城邦宗教史料。' },
          ],
        },
        {
          key: 'n-providence', label: '神意史', label_en: 'History as Providence',
          works: [
            {
              title_zh: '歷史', title_orig: 'Ἱστορίαι / Historiae', author: '希羅多德',
              era: '約前 430 年', language: '古希臘文', extent: '全 9 卷', status: 'whole',
              note: '以神嫉盈滿、神諭必應為史觀的希臘版列王紀。',
              intro: '表面寫波斯戰爭，骨子裡是一部神意史：神嫉恨過盛者、僭越必遭報、神諭終必應驗（只是人總誤解）。書中保存了大量他處不存的宗教材料——各地神諭原文、埃及與波斯宗教的比較觀察、祭儀與節期的實錄。就史觀而言，它與列王紀的「因行惡而失國」屬同一類寫作，只是希臘的神不立約、只維持平衡。',
            },
          ],
        },
      ],
    },
    // ──────────────────────────── Ξ 聖所志 ────────────────────────────
    {
      key: 'X', sigil: 'Ξ', name: '聖所志', name_en: 'The Book of Sanctuaries',
      parallel: '民數記營站與約書亞地界志', clock: 'historical', span: '公元 2 世紀為主',
      summary: '樞紐卷。保薩尼亞斯站在二世紀的土地上，逐處指認神話發生的地點——兩個時鐘在此交棒。',
      divisions: [
        {
          key: 'x-topography', label: '地誌', label_en: 'Topography',
          works: [
            {
              title_zh: '希臘志', title_orig: 'Ἑλλάδος Περιήγησις / Graeciae Descriptio', author: '保薩尼亞斯',
              era: '約公元 155–180 年', language: '古希臘文', extent: '全 10 卷', status: 'whole',
              note: '走遍希臘本土，逐座神廟記其神像、祭儀、傳說與禁忌。',
              intro: '古代唯一一部實地踏查的希臘宗教地誌，也是本藏經單一分量最大的來源。作者親歷阿提卡、伯羅奔尼撒、彼奧提亞與福基斯，凡聖所必記其創建傳說、神像形制、祭儀細節、司祭家族與地方異說，並常註明「當地人是這樣講的，但我不信」。許多祭儀與神話僅賴此書存世；十九世紀以來的希臘考古幾乎全以它為地圖。',
            },
            { title_zh: '歷史叢書‧卷一至六', title_orig: 'Βιβλιοθήκη Ἱστορική I–VI', author: '西西里的狄奧多羅斯', era: '約前 60–30 年', language: '古希臘文', status: 'whole', note: '神話部六卷，含歐赫美魯斯《聖史》的主要摘要與埃及、東方諸神的希臘化解釋。' },
          ],
        },
        {
          key: 'x-votive', label: '還願銘文', label_en: 'Votive Inscriptions',
          works: [
            { title_zh: '還願銘文集', title_orig: 'Votive inscriptions', author: '各地信眾', era: '前 7 – 公元 4 世紀', language: '古希臘文', status: 'inscription', note: '「某某還願獻上，因神垂聽」——最大宗、也最貼近實際信仰生活的一批文獻。' },
            { title_zh: '認罪碑（利底亞—弗里吉亞）', title_orig: 'The confession inscriptions of Lydia and Phrygia', author: '小亞細亞鄉間信眾', era: '公元 1–3 世紀', language: '古希臘文', status: 'inscription', note: '公開刻石承認自己犯了何罪、受神何種懲罰、如何贖回——異教中極罕見的認罪文獻。' },
          ],
        },
      ],
    },
    // ──────────────────────────── Ο 詩頌集 ────────────────────────────
    {
      key: 'O', sigil: 'Ο', name: '詩頌集', name_en: 'The Book of Hymns',
      parallel: '詩篇', clock: 'historical', span: '前 700 – 公元 450 年',
      summary: '一千兩百年的希臘人祈禱，按年代排。從對眾神的稱謝走到普羅克洛對著已關閉的神廟呼求一位近乎獨一的神——禱詞語言的變化本身就是全書最有力的論證。',
      divisions: [
        {
          key: 'o-archaic', label: '古風', label_en: 'Archaic',
          works: [
            {
              title_zh: '荷馬詩頌', title_orig: 'Ὁμηρικοὶ Ὕμνοι / Homerici Hymni', author: '託名荷馬（諸家）',
              era: '約前 7 – 前 5 世紀', language: '古希臘文（六步格）', extent: '33 首', status: 'whole',
              note: '各篇年代不一，須逐篇定位；長篇五首（得墨忒耳、阿波羅、赫爾墨斯、阿芙羅狄忒、狄奧尼索斯）自成敘事。',
              intro: '掛荷馬之名、實出諸家之手的一組頌詩，原為史詩吟誦前的開場。宗教上的價值在於它們是「神的簡介」——每首說明一位神的出生、權能之取得與聖所之建立。致得墨忒耳一首是厄琉息斯祕儀的創教敘事，致阿波羅一首記德爾菲神諭所的建立，兩篇分別是 Λ 卷與 Τ 卷的源頭文本。本卷雖屬詩頌，其年代與權威實與 Γ、Δ 同層，導言須點明。',
            },
            { title_zh: '致阿芙羅狄忒', title_orig: 'Ὕμνος εἰς Ἀφροδίτην', author: '莎孚', era: '約前 600 年', place: '萊斯博斯島', language: '古希臘文（伊奧利亞方言）', status: 'whole', note: '莎孚唯一完整傳世的詩，也是希臘個人祈禱詩的典範：呼名、追述前事、求告。' },
            { title_zh: '少女歌', title_orig: 'Παρθένειον / Partheneion', author: '阿爾克曼', era: '約前 7 世紀後半', place: '斯巴達', language: '古希臘文', status: 'fragment', note: '少女歌隊為女神獻唱的儀式歌，現存最早的希臘合唱抒情詩實例。' },
          ],
        },
        {
          key: 'o-classical', label: '古典', label_en: 'Classical',
          works: [
            { title_zh: '勝利頌', title_orig: 'Ἐπίνικοι / Epinikia', author: '品達', era: '前 498–446 年', language: '古希臘文', extent: '4 卷 45 首', status: 'whole', note: '為競技勝利者而作，實則每首都以神話與神意為主體；古代希臘宗教語言的最高成就。' },
            { title_zh: '祝祭歌與頌神詩殘篇', title_orig: 'Παιᾶνες, Διθύραμβοι, Παρθένεια', author: '品達', era: '前 5 世紀', language: '古希臘文', status: 'fragment', note: '真正用於祭典的品達作品，多賴紙草復原。' },
            { title_zh: '祝祭歌與酒神頌', title_orig: 'Παιᾶνες / Dithyrambs', author: '巴克基利得斯', era: '前 5 世紀', language: '古希臘文', status: 'fragment', note: '第十七首寫忒修斯下海見海神，是現存最完整的酒神頌之一。' },
            { title_zh: '伊敘洛斯祝祭歌', title_orig: 'The Paean of Isyllos', author: '埃庇道洛斯的伊敘洛斯', era: '約前 300 年', place: '埃庇道洛斯', language: '古希臘文', status: 'inscription', note: '刻在阿斯克勒庇俄斯聖所的頌歌並附作者自序，說明此歌如何由神諭核可入祭。' },
            { title_zh: '厄律特萊祝祭歌', title_orig: 'The Erythraean Paean to Asklepios', author: '厄律特萊', era: '約前 380–360 年', language: '古希臘文', status: 'inscription', note: '同一首醫神頌在小亞、雅典、埃及三地出土——古代少見的「通用禮文」。' },
          ],
        },
        {
          key: 'o-hellenistic', label: '希臘化', label_en: 'Hellenistic',
          works: [
            { title_zh: '頌詩六首', title_orig: 'Ὕμνοι / Hymni', author: '卡利馬科斯', era: '約前 270 年', place: '亞歷山卓', language: '古希臘文', status: 'whole', note: '致宙斯、阿波羅、阿爾忒彌斯、提洛島、雅典娜浴、得墨忒耳；文人化的祭儀詩，形式仍嚴守古制。' },
            { title_zh: '宙斯頌', title_orig: 'Ὕμνος εἰς Δία', author: '克萊安特斯', era: '約前 250 年', language: '古希臘文', extent: '39 行', status: 'whole', note: '斯多噶學派的信仰告白：宙斯即普遍理性與律法，萬物依之而行，惡人自違而自苦。異教中最接近一神論禱文者。' },
            { title_zh: '德爾菲阿波羅頌（附樂譜）', title_orig: 'The Delphic Hymns to Apollo', author: '雅典的阿特納伊俄斯、利梅尼俄斯', era: '前 128/127 年', place: '德爾菲', language: '古希臘文', status: 'inscription', note: '刻在雅典寶庫牆上並附古希臘記譜符號，是現存最早可實際演奏的西方樂譜。' },
          ],
        },
        {
          key: 'o-imperial', label: '帝國期', label_en: 'Imperial',
          works: [
            {
              title_zh: '俄耳甫斯詩頌', title_orig: 'Ὀρφικοὶ Ὕμνοι / Orphic Hymns', author: '託名俄耳甫斯（小亞細亞某信團）',
              era: '約公元 2–3 世紀', place: '小亞細亞（推測帕加馬一帶）', language: '古希臘文', extent: '87 首', status: 'whole',
              note: '一個信團實際使用的整套禮文，每首附焚香指示。',
              intro: '八十七首短頌，前有致穆賽俄斯的引詩，每首標明應焚何香（乳香、沒藥、番紅花、種子……）。這不是文學選集，而是某個小亞細亞信團從頭到尾的一套禮儀本——按聚會次序呼求諸神，先原初諸力，再奧林匹亞眾神，終以死亡收束。它是異教晚期唯一完整傳世的成套禮文，功能上等同於一本會眾詩歌本。',
            },
            { title_zh: '頌詩（附樂譜）', title_orig: 'Ὕμνοι / Hymni', author: '克里特的美索梅德斯', era: '公元 2 世紀（哈德良朝）', language: '古希臘文', status: 'whole', note: '致繆斯、致太陽、致復仇女神等，附古希臘記譜；與德爾菲頌並為現存僅有的古代宗教樂譜。' },
          ],
        },
        {
          key: 'o-late', label: '晚期古代', label_en: 'Late Antique',
          works: [
            { title_zh: '致太陽王', title_orig: 'Εἰς τὸν βασιλέα Ἥλιον', author: '尤利安', era: '公元 362 年 12 月', language: '古希臘文', status: 'whole', note: '皇帝親撰的太陽神學，以新柏拉圖三層結構統攝諸神——異教在制度上最後一次嘗試自我統一。' },
            { title_zh: '致眾神之母', title_orig: 'Εἰς τὴν Μητέρα τῶν θεῶν', author: '尤利安', era: '公元 362 年 3 月', language: '古希臘文', status: 'whole', note: '為庫柏勒祭儀作寓意辯護，寫成僅一夜。' },
            {
              title_zh: '頌詩七首', title_orig: 'Ὕμνοι / Hymni', author: '普羅克洛',
              era: '約公元 450–480 年', place: '雅典', language: '古希臘文', status: 'whole',
              note: '本卷終篇：神廟已閉，禱詞仍在。',
              intro: '致太陽、阿芙羅狄忒、繆斯、諸神、呂基亞的阿芙羅狄忒、赫卡忒與雅努斯、雅典娜七首。寫作時雅典的神廟已陸續關閉、公開獻祭已屬非法，詩中因此幾乎不再求現世福祉，只求「引我的魂脫離幽暗、賜我光明」。與 Ο 卷開篇的荷馬詩頌並讀，一千兩百年的距離一目了然——這也是本卷按年代排序的全部用意。',
            },
          ],
        },
      ],
    },
    // ──────────────────────────── Π 箴言 ────────────────────────────
    {
      key: 'P', sigil: 'Π', name: '箴言', name_en: 'The Book of Precepts',
      parallel: '箴言', clock: 'historical', span: '前 700 – 公元 300 年',
      summary: '不靠啟示、只靠世代經驗累積的處世智慧。希臘的智慧文學不歸神說，歸人說。',
      divisions: [
        {
          key: 'pi-hesiod', label: '農時勸誡', label_en: 'Works and Days',
          works: [
            { title_zh: '工作與時日（勸誡段）', title_orig: 'Ἔργα καὶ Ἡμέραι', author: '赫西俄德', era: '約前 700 年', language: '古希臘文', extent: '取 202–828 行', status: 'whole', note: '對兄弟佩爾塞斯的訓誨：勞動、公義、農事曆、航海禁忌與吉凶日。與箴言的父訓體例同型。' },
          ],
        },
        {
          key: 'pi-delphic', label: '德爾菲箴言與七賢', label_en: 'Delphic Maxims and the Seven Sages',
          works: [
            { title_zh: '德爾菲箴言', title_orig: 'Δελφικὰ παραγγέλματα / Delphic Maxims', author: '傳為七賢所獻', era: '前 6 世紀起', language: '古希臘文', extent: '147 條', status: 'inscription', note: '「認識你自己」「毋過度」刻於德爾菲廟門；阿伊哈努姆（今阿富汗）出土的石刻證明它傳到了希臘世界的最東端。' },
            { title_zh: '七賢言行錄', title_orig: 'The sayings of the Seven Sages', author: '綴輯（柏拉圖、第歐根尼‧拉爾修）', era: '前 6 世紀起', language: '古希臘文', status: 'fragment', note: '泰勒斯、梭倫、庇塔庫斯等人的格言；希臘最早的智者傳統，尚未與哲學分家。' },
          ],
        },
        {
          key: 'pi-gnomic', label: '格言詩', label_en: 'Gnomic Poetry',
          works: [
            { title_zh: '哀歌集', title_orig: 'Ἐλεγεῖαι / Elegiae', author: '墨伽拉的泰奧格尼斯', era: '約前 6 世紀後半', language: '古希臘文', extent: '約 1,400 行', status: 'whole', note: '對少年居爾諾斯的訓誨，貫穿貴族沒落的怨懟；希臘現存最大宗的格言詩。' },
            { title_zh: '金言', title_orig: 'Χρύσεα Ἔπη / Carmen Aureum', author: '託名畢達哥拉斯', era: '約前 3 – 公元 1 世紀定型', language: '古希臘文', extent: '71 行', status: 'whole', note: '每晚三省吾身、敬神、戒食、淨化；新柏拉圖學派拿它當入門必誦，希耶羅克勒斯為之作註。' },
            { title_zh: '訓誨詩', title_orig: 'Ποίημα Νουθετικόν', author: '託名福西利德斯', era: '約公元 1 世紀', language: '古希臘文', extent: '230 行', status: 'whole', note: '以希臘格言體重寫猶太律法倫理而不提摩西——希臘化猶太與異教倫理交會的關鍵文本。' },
            { title_zh: '單行格言集', title_orig: 'Μονόστιχοι / Monostichoi', author: '託名米南德', era: '公元 1–4 世紀彙編', language: '古希臘文', status: 'fragment', note: '一行一句的格言集，拜占庭學校的識字課本；靠它流傳的希臘倫理句子比任何哲學著作都廣。' },
          ],
        },
      ],
    },
    // ──────────────────────────── Ρ 受苦者之書 ────────────────────────────
    {
      key: 'R', sigil: 'Ρ', name: '受苦者之書', name_en: 'The Book of the Sufferer',
      parallel: '約伯記', clock: 'historical', span: '前 5 世紀為主',
      summary: '悲劇中的神義論選段。希臘沒有一部約伯記，但有一整個世紀的劇場在問同一個問題，而且沒有旋風中的答覆。',
      divisions: [
        {
          key: 'r-defiance', label: '抗辯', label_en: 'Defiance',
          works: [
            {
              title_zh: '受縛的普羅米修斯', title_orig: 'Προμηθεὺς Δεσμώτης', author: '託名埃斯庫羅斯',
              era: '約前 470–430 年', language: '古希臘文', status: 'whole',
              note: '因愛人類而受縛的義者，當面指控至高神不義。',
              intro: '普羅米修斯因把火與技藝給了人類而被釘在高加索絕壁，全劇他始終不肯屈服，公開指宙斯為新僭主、其統治靠暴力而非公義，並預言宙斯終將如其父祖一樣被推翻。這是古代世界最徹底的一次神義論抗辯——它與約伯的差別在於：約伯質問一位他仍信的神，普羅米修斯質問一位他準備熬過去的神。',
            },
          ],
        },
        {
          key: 'r-terror', label: '神的可畏', label_en: 'The Terror of the God',
          works: [
            { title_zh: '酒神的女信徒', title_orig: 'Βάκχαι / Bacchae', author: '歐里庇得斯', era: '前 405 年（身後上演）', language: '古希臘文', status: 'whole', note: '拒認新神的王被母親徒手撕碎；全劇不判是非，只呈現不信的代價。異教神學最深的一部戲。' },
            { title_zh: '希波呂托斯', title_orig: 'Ἱππόλυτος', author: '歐里庇得斯', era: '前 428 年', language: '古希臘文', status: 'whole', note: '獨敬一神而怠慢另一神，遂被毀滅——多神信仰中「不可偏廢」的鐵律。' },
            { title_zh: '特洛伊婦女', title_orig: 'Τρῳάδες / Troades', author: '歐里庇得斯', era: '前 415 年', language: '古希臘文', status: 'whole', note: '城破之後的婦女對神的控訴；赫卡柏那段祈禱把宙斯稱作「大地的支撐、無論你是誰」。' },
          ],
        },
        {
          key: 'r-submission', label: '順服', label_en: 'Submission',
          works: [
            { title_zh: '伊底帕斯在科隆諾斯', title_orig: 'Οἰδίπους ἐπὶ Κολωνῷ', author: '索福克勒斯', era: '前 401 年（身後上演）', language: '古希臘文', status: 'whole', note: '受盡神罰的瞎眼老人終被大地接納而成守護英雄；最接近「苦難得贖」的一部希臘戲。' },
            { title_zh: '阿伽門農（歌隊神學段）', title_orig: 'Ἀγαμέμνων', author: '埃斯庫羅斯', era: '前 458 年', language: '古希臘文', status: 'whole', note: '「宙斯教人受苦而後知」——希臘神義論最凝練的一句，本卷收其歌隊各段。' },
            { title_zh: '悲劇', title_orig: 'Tragoediae', author: '塞內卡', era: '公元 1 世紀中', language: '拉丁文', extent: '9 部', track: 'latin', status: 'whole', note: '斯多噶版神義論；也是中世紀歐洲唯一讀得到的「希臘悲劇」。' },
          ],
        },
      ],
    },
    // ──────────────────────────── Σ 虛空篇 ────────────────────────────
    {
      key: 'S', sigil: 'Σ', name: '虛空篇', name_en: 'The Book of Vanity',
      parallel: '傳道書', clock: 'historical', span: '前 5 – 公元 5 世紀',
      summary: '人生短促、諸事無常、死後無知。希臘的傳道書散在歌隊、墓誌與諷刺詩裡，本卷綴為一編。',
      divisions: [
        {
          key: 's-chorus', label: '歌隊詠嘆', label_en: 'Choral Laments',
          works: [
            { title_zh: '不出生最好', title_orig: 'μὴ φῦναι τὸν ἅπαντα νικᾷ λόγον', author: '索福克勒斯《伊底帕斯在科隆諾斯》1224 行起', era: '前 401 年', language: '古希臘文', status: 'whole', note: '「不出生是最好的；既已出生，速歸來處次之。」希臘悲觀主義的定音之句。' },
            { title_zh: '人如樹葉', title_orig: 'οἵη περ φύλλων γενεή', author: '《伊利亞特》六卷 146 行；西摩尼得斯、姆奈爾摩斯續之', era: '前 8–6 世紀', language: '古希臘文', status: 'whole', note: '一代人如一代樹葉——此喻自荷馬起被反覆重寫，成為希臘無常觀的母題。' },
          ],
        },
        {
          key: 's-epitaph', label: '墓誌', label_en: 'Epitaphs',
          works: [
            { title_zh: '希臘詩選‧卷七（墓誌銘）', title_orig: 'Anthologia Graeca VII', author: '諸家彙編', era: '前 5 – 公元 10 世紀彙編', language: '古希臘文', extent: '約 750 首', status: 'whole', note: '古代希臘人對死亡最誠實的話都在這裡；多數詩明言死後一無所有，與祕儀的來世許諾正相反。' },
            { title_zh: '墓碑銘文集', title_orig: 'Funerary inscriptions', author: '各地', era: '前 6 – 公元 5 世紀', language: '古希臘文', status: 'inscription', note: '「我不在，我曾在；我不在意」——刻在石上的通俗虛無主義套語，分布極廣。' },
          ],
        },
        {
          key: 's-satire', label: '諷刺', label_en: 'Satire',
          works: [
            { title_zh: '諷刺詩', title_orig: 'Epigrammata', author: '亞歷山卓的帕拉達斯', era: '約公元 4 世紀末', place: '亞歷山卓', language: '古希臘文', status: 'fragment', note: '眼見神廟被拆、神像被熔的異教文人，寫下希臘最苦的自嘲；異教末世的傳道書。' },
            { title_zh: '死者的對話', title_orig: 'Νεκρικοὶ Διάλογοι', author: '薩莫薩塔的琉善', era: '公元 2 世紀', language: '古希臘文', status: 'whole', note: '在冥府裡人人一樣是骨頭；以喜劇拆穿一切關於來世與名聲的說法。' },
          ],
        },
      ],
    },
    // ──────────────────────────── Τ 神諭書 ────────────────────────────
    {
      key: 'T', sigil: 'Τ', name: '神諭書', name_en: 'The Book of Oracles',
      parallel: '大先知書', clock: 'historical', span: '前 8 世紀 – 公元 2 世紀',
      summary: '神從外面說話。本卷按年代排到普魯塔克追問神諭為何沉默為止；最後一則神諭留在 Ω 卷。',
      divisions: [
        {
          key: 't-delphi', label: '德爾菲', label_en: 'Delphi',
          works: [
            { title_zh: '荷馬詩頌‧致阿波羅', title_orig: 'Ὕμνος εἰς Ἀπόλλωνα', author: '託名荷馬', era: '約前 7–6 世紀', language: '古希臘文', status: 'whole', note: '德爾菲神諭所的創建敘事：阿波羅殺巨蟒、擄克里特商人為祭司。' },
            { title_zh: '德爾菲神諭彙編', title_orig: 'The Delphic responses', author: '皮媞亞（德爾菲阿波羅祭司）', era: '前 8 – 公元 4 世紀', language: '古希臘文', status: 'fragment', via: '希羅多德、修昔底德、普魯塔克、狄奧多羅斯等轉引', extent: '傳世逾 600 則', note: '本卷主體，按年代編次；含「木牆」「呂庫古大諭令」「蘇格拉底最智慧」諸則。', seealso: '基督教大藏經‧前藏經藏‧希臘神諭部' },
          ],
        },
        {
          key: 't-dodona', label: '多多納', label_en: 'Dodona',
          works: [
            {
              title_zh: '多多納問卜鉛片', title_orig: 'The Dodona lead tablets', author: '各地問卜者',
              era: '前 6 – 前 2 世紀', place: '希臘‧伊庇魯斯‧多多納', language: '古希臘文（多種方言）',
              extent: '現存逾 4,000 片', status: 'inscription',
              note: '「我該不該娶她」「羊是誰偷的」——最大宗的民間問神實物。',
              intro: '希臘最古老的神諭所，以宙斯聖橡樹的葉聲為兆。信眾把問題刻在小鉛片上投入，鉛片因此大量留存：該不該遷居、該向哪位神獻祭才會有孩子、丟失的毯子是誰拿的。與德爾菲多為城邦大事不同，多多納留下的幾乎全是私人生活的憂慮，是古代宗教最貼近日常的一批文獻，也是希臘方言學的一座礦。',
            },
          ],
        },
        {
          key: 't-asia', label: '小亞神學神諭', label_en: 'The Theological Oracles',
          works: [
            { title_zh: '克拉羅斯神諭銘文', title_orig: 'The oracles of Claros', author: '克拉羅斯阿波羅神所', era: '公元 1–3 世紀', place: '小亞細亞‧克拉羅斯', language: '古希臘文', status: 'inscription', note: '晚期神諭不再指示吉凶，改答「至高神是誰」——神諭本身開始神學化。' },
            { title_zh: '狄杜瑪神諭', title_orig: 'The oracles of Didyma', author: '狄杜瑪阿波羅神所', era: '前 6 – 公元 3 世紀', language: '古希臘文', status: 'inscription', note: '含答覆基督徒問題的著名一則，後為戴克里先迫害所引。' },
            { title_zh: '神諭哲學（殘篇）', title_orig: 'Περὶ τῆς ἐκ λογίων φιλοσοφίας', author: '波菲利', era: '約公元 3 世紀末', language: '古希臘文', status: 'fragment', via: '優西比烏《福音的預備》', note: '以神諭本身為哲學依據的彙編，把神諭抬升為啟示文獻。' },
          ],
        },
        {
          key: 't-sibyl', label: '西比拉與遊方預言', label_en: 'Sibyls and Wandering Prophets',
          works: [
            { title_zh: '西比拉神諭（異教核心層）', title_orig: 'Oracula Sibyllina', author: '託名各地西比拉', era: '前 2 世紀 – 公元 4 世紀', language: '古希臘文', extent: '現存 12 卷', status: 'fragment', note: '現存本已被猶太與基督教徒大幅改寫，本卷僅收可辨識的異教殘核，並標明改寫層。' },
            { title_zh: '巴基斯與穆賽俄斯神諭殘篇', title_orig: 'The oracles of Bakis and Musaeus', author: '託名', era: '前 6–5 世紀', language: '古希臘文', status: 'fragment', via: '希羅多德、亞里斯多芬', note: '遊方神諭販子所售的成套預言集；雅典喜劇常拿來嘲諷。' },
          ],
        },
        {
          key: 't-silence', label: '沉默', label_en: 'The Silence',
          works: [
            { title_zh: '論神諭的衰微', title_orig: 'Περὶ τῶν ἐκλελοιπότων χρηστηρίων', author: '普魯塔克', era: '約公元 100 年', place: '德爾菲', language: '古希臘文', status: 'whole', note: '身為德爾菲祭司的作者追問：神諭為何一個接一個停了？書中「大潘已死」一則傳誦千年。本卷終篇。' },
          ],
        },
      ],
    },
    // ──────────────────────────── Υ 啟示書 ────────────────────────────
    {
      key: 'U', sigil: 'Υ', name: '啟示書', name_en: 'The Book of Revelations',
      parallel: '但以理、以西結、啟示錄', clock: 'historical', span: '前 5 – 公元 4 世紀',
      summary: '神在裡面顯現。第一人稱的異象、升天、來世圖景與個人啟示日記——異教中最接近啟示文學的一批文獻。',
      divisions: [
        {
          key: 'u-early', label: '早期異象', label_en: 'Early Visions',
          works: [
            { title_zh: '論自然（序詩）', title_orig: 'Περὶ φύσεως, proem', author: '埃利亞的巴門尼德', era: '約前 480 年', language: '古希臘文', status: 'fragment', note: '駕車越過晝夜之門、由女神親授真理——希臘哲學以一段啟示異象開篇。' },
            { title_zh: '淨化篇', title_orig: 'Καθαρμοί / Katharmoi', author: '阿克拉加斯的恩培多克勒', era: '約前 450 年', language: '古希臘文', status: 'fragment', note: '「我在你們中間行走，已不是人，而是不朽的神」——第一人稱的先知宣告與輪迴贖罪說。' },
          ],
        },
        {
          key: 'u-plato', label: '柏拉圖末世神話', label_en: 'The Platonic Eschatological Myths',
          works: [
            { title_zh: '厄爾神話（《理想國》卷十）', title_orig: 'The Myth of Er, Republic X', author: '柏拉圖', era: '約前 375 年', language: '古希臘文', status: 'whole', note: '陣亡者還魂，述審判、千年賞罰、抽籤擇來生、飲忘川而復生——西方來世觀的骨架。' },
            { title_zh: '斐多末段', title_orig: 'Phaedo 107c–115a', author: '柏拉圖', era: '約前 380 年', language: '古希臘文', status: 'whole', note: '真地與地下諸河；靈魂依其潔淨程度分往各處。' },
            { title_zh: '高爾吉亞末段', title_orig: 'Gorgias 523a–527e', author: '柏拉圖', era: '約前 380 年', language: '古希臘文', status: 'whole', note: '死後赤裸受審，罪痕顯於魂上；三判官的設置為後世末日審判圖像所本。' },
            { title_zh: '斐德羅（天馬車異象）', title_orig: 'Phaedrus 246a–257a', author: '柏拉圖', era: '約前 370 年', language: '古希臘文', status: 'whole', note: '靈魂隨神隊登天穹外緣觀「真實存有」；新柏拉圖與基督教神祕主義共同的源頭意象。' },
          ],
        },
        {
          key: 'u-imperial', label: '帝國期啟示文集', label_en: 'Imperial Revelation Corpora',
          works: [
            {
              title_zh: '赫爾墨斯文集', title_orig: 'Corpus Hermeticum', author: '託名三重偉大的赫爾墨斯',
              era: '約公元 1–3 世紀', place: '埃及‧亞歷山卓', language: '古希臘文', extent: '18 篇（另有《阿斯克勒庇俄斯》與斯托拜俄斯殘篇）',
              status: 'whole',
              note: '首篇《牧人書》即一部完整的創世—墮落—救贖啟示。',
              intro: '託名赫爾墨斯的一組師徒對話，內容為宇宙起源、人的墮落與藉知識（gnosis）上升復歸。首篇《牧人書》最重：至高心智以異象顯現，述光與暗分離、原人因愛自己的影像而墜入物質、以及靈魂穿越七重天脫去情慾而復歸於神。它與諾斯底文獻同源而不敵視物質，文藝復興以後被誤認為摩西同時代的埃及古智慧，深刻影響了整個歐洲祕學傳統。',
              link: '/gnostic',
            },
            {
              title_zh: '迦勒底神諭', title_orig: 'Λόγια Χαλδαϊκά / Oracula Chaldaica', author: '猶利安努斯父子（託名）',
              era: '約公元 2 世紀末', language: '古希臘文（六步格）', status: 'fragment',
              via: '普羅克洛、達馬斯基烏斯、普塞洛斯引錄',
              note: '新柏拉圖學派奉為聖經的啟示詩；召神術（theurgy）的根本典據。',
              intro: '以六步格寫成的神諭詩殘篇，自稱得自諸神。內容為父、力、心智的三一結構、靈魂下降與上升、以及藉儀式（而非僅靠思辨）促使神明降臨的召神術。揚布利科斯以下的新柏拉圖學派把它抬到與柏拉圖對話錄同等的地位，普羅克洛甚至說若能決定哪些書留存於世，他只留《蒂邁歐》與《迦勒底神諭》。異教最後三百年的教義核心即由此出。',
            },
            { title_zh: '密特拉禮文', title_orig: 'PGM IV.475–834', author: '佚名', era: '約公元 4 世紀', language: '古希臘文', status: 'inscription', parent: '希臘魔法紙草', note: '逐步指示如何屏息、見火門開啟、與太陽神面對面並索求不朽——現存最詳盡的升天儀軌。' },
            {
              title_zh: '聖言錄', title_orig: 'Ἱεροὶ Λόγοι / Sacred Tales', author: '埃利烏斯‧阿里斯提德斯',
              era: '約公元 170 年', place: '帕加馬', language: '古希臘文', extent: '6 卷', status: 'whole',
              note: '一部長達十餘年的個人啟示日記。',
              intro: '長年患病的雄辯家在帕加馬的醫神聖所住院求夢，把神每夜的指示逐一記錄：何時放血、何時在寒冬下河、該寫什麼講稿、該去哪裡演說。全書把生活的每一件小事都繫於神的親自指引，是整個古代唯一一部完整的個人宗教經驗紀錄，也是研究醫神信仰、夢占與宗教心理的第一手材料。',
            },
            { title_zh: '解夢書', title_orig: 'Ὀνειροκριτικά / Oneirocritica', author: '達爾狄斯的阿爾特米多羅斯', era: '公元 2 世紀', language: '古希臘文', extent: '全 5 卷', status: 'whole', note: '古代唯一完整傳世的解夢手冊，作者自陳走遍各地蒐羅夢例；通俗宗教生活的百科。' },
            { title_zh: '金驢記‧卷十一', title_orig: 'Metamorphoses XI', author: '阿普列尤斯', era: '約公元 170 年', language: '拉丁文', track: 'latin', status: 'whole', note: '女神夜半顯現、自陳萬名歸一——第一人稱皈依敘事，與 Λ 卷互見。' },
          ],
        },
        {
          key: 'u-theurgy', label: '召神術', label_en: 'Theurgy',
          works: [
            { title_zh: '論祕儀（答波菲利書）', title_orig: 'Περὶ μυστηρίων / De mysteriis', author: '揚布利科斯', era: '約公元 300 年', language: '古希臘文', status: 'whole', note: '主張人不能靠思辨上達於神，必須藉神所定的儀式；異教晚期由哲學轉回祭儀的分水嶺。' },
            { title_zh: '論召神術（殘篇）', title_orig: 'Περὶ τῆς καθ᾿ Ἕλληνας ἱερατικῆς τέχνης', author: '普羅克洛', era: '公元 5 世紀', language: '古希臘文', status: 'fragment', note: '論物質中的神性印記與交感原理，是理解晚期異教「聖物觀」的關鍵短篇。' },
          ],
        },
      ],
    },
    // ──────────────────────────── Φ 論神書 ────────────────────────────
    {
      key: 'Ph', sigil: 'Φ', name: '論神書', name_en: 'On the Gods',
      parallel: '書信與系統神學', clock: 'historical', span: '前 6 – 公元 6 世紀',
      summary: '異教的系統神學。薩盧斯提烏斯的要理抽出置於卷首作導覽，正文再從色諾芬尼按年代走——「小引置前、正文按序」的舊例。',
      divisions: [
        {
          key: 'ph-catechism', label: '要理提綱', label_en: 'The Catechism',
          desc: '本篇實為公元 4 世紀作品，因是全書唯一成體系的異教要理，抽置卷首作導覽。',
          works: [
            {
              title_zh: '論諸神與世界', title_orig: 'Περὶ θεῶν καὶ κόσμου / De diis et mundo', author: '薩盧斯提烏斯',
              era: '約公元 362 年', language: '古希臘文', extent: '21 章', status: 'whole',
              note: '異教唯一一份成體系的要理問答，出自尤利安的圈子。',
              intro: '短短二十一章，把整套異教信仰講得像一本要理問答：神的本性、神話該如何讀（「這些事從未發生，卻永遠如此」）、宇宙為何不滅、靈魂輪迴、惡從何來、為何要獻祭、不信者將如何。文字淺白、結構完整、刻意寫給一般人看——它出現在尤利安復興異教的那一年，用意昭然：異教也需要一本能發給民眾的教義手冊。這是本卷最好的入口。',
            },
          ],
        },
        {
          key: 'ph-early', label: '早期批判', label_en: 'Early Critique',
          works: [
            { title_zh: '殘篇', title_orig: 'Fragmenta', author: '科洛封的色諾芬尼', era: '約前 530 年', language: '古希臘文', status: 'fragment', note: '「牛馬若能作畫，畫出的神必像牛馬」——反神人同形的先知式批判，也是希臘一神傾向的最早聲音。' },
            { title_zh: '殘篇（宗教語句）', title_orig: 'Fragmenta', author: '以弗所的赫拉克利特', era: '約前 500 年', language: '古希臘文', status: 'fragment', note: '斥血祭如以泥洗泥、斥向偶像禱告如對房子說話；同時提出「邏各斯」——後世道成肉身神學的用語源頭。' },
          ],
        },
        {
          key: 'ph-classical', label: '古典神學', label_en: 'Classical Theology',
          works: [
            { title_zh: '蒂邁歐', title_orig: 'Τίμαιος / Timaeus', author: '柏拉圖', era: '約前 360 年', language: '古希臘文', status: 'whole', note: '工匠神依永恆典範造宇宙——古代影響最大的一部創世論，經卡爾奇迪烏斯拉丁譯註成為中世紀西方唯一讀得到的柏拉圖。' },
            { title_zh: '法律篇‧卷十', title_orig: 'Νόμοι Ι', author: '柏拉圖', era: '約前 350 年', language: '古希臘文', status: 'whole', note: '古代第一部有系統的「神存在論證」，並主張無神論應以法律論罪——異教版的異端法。' },
            { title_zh: '形上學‧卷十二', title_orig: 'Μετὰ τὰ φυσικά Λ', author: '亞里斯多德', era: '約前 340 年', language: '古希臘文', status: 'whole', note: '不動的推動者、思想自身的思想；經阿拉伯與經院哲學轉手，成為西方一神論的哲學骨幹。' },
          ],
        },
        {
          key: 'ph-schools', label: '學派神學', label_en: 'School Theologies',
          works: [
            { title_zh: '斯多噶神學殘篇', title_orig: 'Stoicorum Veterum Fragmenta (theologica)', author: '克呂西波斯等', era: '前 3–2 世紀', language: '古希臘文', status: 'fragment', note: '神即遍在的理性之火與命運本身；泛神論在古代的最完整形態。' },
            { title_zh: '希臘神學要覽', title_orig: 'Ἐπιδρομὴ τῶν κατὰ τὴν Ἑλληνικὴν θεολογίαν', author: '科爾努圖斯', era: '公元 1 世紀', language: '古希臘文', status: 'whole', note: '現存最完整的斯多噶寓意神學手冊，逐一解釋諸神名號的自然意義。' },
            { title_zh: '論神性', title_orig: 'De natura deorum', author: '西塞羅', era: '前 45 年', language: '拉丁文', extent: '全 3 卷', track: 'latin', status: 'whole', note: '伊比鳩魯、斯多噶、學園派三方辯論；克呂西波斯神學的最完整轉述，希臘原典已佚。' },
            { title_zh: '物性論', title_orig: 'De rerum natura', author: '盧克萊修', era: '約前 55 年', language: '拉丁文', extent: '全 6 卷', track: 'latin', status: 'whole', note: '伊比鳩魯派的反宗教長詩：神存在但不管人事，畏神才是一切苦難之源。異教內部最徹底的宗教批判。' },
          ],
        },
        {
          key: 'ph-middle', label: '中期柏拉圖', label_en: 'Middle Platonism',
          works: [
            { title_zh: '論伊西斯與奧西里斯', title_orig: 'Περὶ Ἴσιδος καὶ Ὀσίριδος', author: '普魯塔克', era: '約公元 120 年', language: '古希臘文', status: 'whole', note: '以希臘哲學解埃及神話，並提出善惡二原理說；古代比較宗教學的開山之作。' },
            { title_zh: '論德爾菲的 E 字', title_orig: 'Περὶ τοῦ Εἶ τοῦ ἐν Δελφοῖς', author: '普魯塔克', era: '約公元 100 年', language: '古希臘文', status: 'whole', note: '德爾菲廟門的神祕字母 E 何解；末段以「你是」為神之名，直逼一神論。' },
            { title_zh: '論神遲罰惡', title_orig: 'Περὶ τῶν ὑπὸ τοῦ θείου βραδέως τιμωρουμένων', author: '普魯塔克', era: '公元 2 世紀初', language: '古希臘文', status: 'whole', note: '正面處理「惡人為何不立刻遭報」，末附靈魂受審異象；異教神義論的代表作。' },
            { title_zh: '講演集', title_orig: 'Διαλέξεις / Orationes', author: '推羅的馬克西姆斯', era: '公元 2 世紀後半', language: '古希臘文', extent: '41 篇', status: 'whole', note: '面向大眾的哲學佈道：該不該立神像、該不該向神禱告、何謂神——古代少見的「講章集」。' },
            { title_zh: '教程（柏拉圖學說綱要）', title_orig: 'Διδασκαλικός / Didaskalikos', author: '阿爾基努斯', era: '公元 2 世紀', language: '古希臘文', status: 'whole', note: '中期柏拉圖主義的教科書，第一因、心智、質料三層結構於此定型。' },
            { title_zh: '論善（殘篇）', title_orig: 'Περὶ τἀγαθοῦ', author: '阿帕梅亞的努美尼烏斯', era: '公元 2 世紀後半', language: '古希臘文', status: 'fragment', note: '「柏拉圖不過是說阿提卡話的摩西」——把希臘哲學與東方啟示打通的關鍵人物。' },
          ],
        },
        {
          key: 'ph-neo', label: '新柏拉圖', label_en: 'Neoplatonism',
          works: [
            {
              title_zh: '九章集', title_orig: 'Ἐννεάδες / Enneades', author: '普羅提諾（波菲利編訂）',
              era: '公元 253–270 年撰，約 301 年編定', place: '羅馬', language: '古希臘文', extent: '6 集 54 篇', status: 'whole',
              note: '太一—心智—靈魂三層流出說；異教哲學神學的頂點。',
              intro: '五十四篇論文，由弟子波菲利按每集九篇編為六集。核心是流出說：不可名狀的「太一」滿溢而生心智，心智生靈魂，靈魂生可感世界；人可循原路內轉、超越思維而與太一合一——波菲利說老師一生有四次達到。全書幾乎不談祭儀與神話，卻為此後的異教神學、基督教神祕主義與伊斯蘭哲學共同奠基。',
            },
            { title_zh: '致馬爾克拉書', title_orig: 'Πρὸς Μαρκέλλαν / Ad Marcellam', author: '波菲利', era: '約公元 300 年', language: '古希臘文', status: 'whole', note: '寫給妻子的哲學勸勉書；「最好的敬神方式是心思潔淨」，異教靈修文學的代表。' },
            { title_zh: '神學要義', title_orig: 'Στοιχείωσις θεολογική / Elementatio theologica', author: '普羅克洛', era: '公元 5 世紀', language: '古希臘文', extent: '211 命題', status: 'whole', note: '仿歐幾里得體例、以命題與證明寫成的形上學；經阿拉伯轉譯為《原因之書》，深刻影響經院哲學。' },
            { title_zh: '柏拉圖神學', title_orig: 'Περὶ τῆς κατὰ Πλάτωνα θεολογίας', author: '普羅克洛', era: '公元 5 世紀', language: '古希臘文', extent: '全 6 卷', status: 'whole', note: '把希臘全部神名系統地編入形上學階序；異教神學的最終形態與集大成。' },
            { title_zh: '論第一原理', title_orig: 'Περὶ ἀρχῶν / De principiis', author: '達馬斯基烏斯', era: '約公元 520 年', place: '雅典', language: '古希臘文', status: 'whole', note: '雅典學園末代園長之作，論不可言說者何以不可言說；希臘哲學的最後一部原創巨著。' },
            { title_zh: '蒂邁歐譯註', title_orig: 'Timaeus a Calcidio translatus commentarioque instructus', author: '卡爾奇迪烏斯', era: '公元 4 世紀', language: '拉丁文', track: 'latin', status: 'whole', note: '十二世紀之前西方唯一能讀到的柏拉圖創世論，中世紀宇宙觀的實際來源。' },
            { title_zh: '西庇阿之夢註', title_orig: 'Commentarii in Somnium Scipionis', author: '馬克羅比烏斯', era: '約公元 430 年', language: '拉丁文', track: 'latin', status: 'whole', note: '把新柏拉圖宇宙論與靈魂上升說傳入拉丁世界的關鍵著作。' },
            { title_zh: '文獻學與墨丘利的婚禮', title_orig: 'De nuptiis Philologiae et Mercurii', author: '瑪爾提亞努斯‧卡佩拉', era: '約公元 420–490 年', language: '拉丁文', track: 'latin', status: 'whole', note: '以異教神話包裝的七藝教科書；中世紀學校由此在基督教框架內繼續誦讀諸神之名。' },
          ],
        },
      ],
    },
    // ──────────────────────────── Χ 聖徒傳與神蹟簿 ────────────────────────────
    {
      key: 'Ch', sigil: 'Χ', name: '聖徒傳與神蹟簿', name_en: 'Lives and Miracles',
      parallel: '福音書與使徒行傳', clock: 'historical', span: '前 4 – 公元 6 世紀',
      summary: '神人的行傳與神蹟的紀錄。異教在最後三百年才長出這一文類，時間點與基督教聖徒傳的興起完全重疊。',
      divisions: [
        {
          key: 'ch-miracle', label: '神蹟簿', label_en: 'Records of Healing',
          works: [
            {
              title_zh: '埃庇道洛斯治癒銘文', title_orig: 'Ἰάματα / The Epidaurian Iamata',
              author: '埃庇道洛斯醫神聖所', era: '約前 350–300 年', place: '希臘‧埃庇道洛斯',
              language: '古希臘文', extent: '現存 4 石逾 70 則', status: 'inscription',
              note: '古代最完整的神蹟集：某人得何病、夢見神做了什麼、醒來即癒。',
              intro: '刻在聖所大石板上的治癒紀錄，一則一案：盲人夢見神剖開眼球敷藥，醒來復明；懷胎五年的婦人夢中產子；不信的人被神當場治好並改名為「不信者」。文體固定、語氣自信，明顯是為招徠信眾而立。它與福音書的治病敘事屬同一文類，且年代早了三百年，是比較宗教研究無法迴避的一批材料。',
            },
            { title_zh: '朗吉努斯與各地醫神聖所紀錄', title_orig: 'Healing records from Lebena, Pergamon, Rome', author: '各醫神聖所', era: '前 3 – 公元 3 世紀', language: '古希臘文', status: 'inscription', note: '醫神信仰遍及地中海，各聖所皆有同型紀錄；可見此文類的制度化程度。' },
          ],
        },
        {
          key: 'ch-lives', label: '聖徒傳', label_en: 'Holy Lives',
          works: [
            {
              title_zh: '提亞納的阿波羅尼烏斯傳', title_orig: 'Τὰ ἐς τὸν Τυανέα Ἀπολλώνιον', author: '斐洛斯特拉托斯',
              era: '約公元 220–230 年', language: '古希臘文', extent: '全 8 卷', status: 'whole',
              note: '全部異教文獻中最接近福音書的一部。',
              intro: '受尤利亞‧多姆娜之託所寫的一位一世紀畢達哥拉斯派聖者傳：神異降生、周遊行教、醫病驅鬼、復活少女、遠赴印度求道、面斥暴君、受審時自行消失、死後顯現向弟子證明靈魂不朽。全書與福音書的敘事結構重疊之深，使它在三世紀末就被希耶羅克勒斯拿來與基督直接比較，也因此成為此後一千七百年比較宗教爭論的中心文本。',
            },
            { title_zh: '畢達哥拉斯傳（論畢達哥拉斯的生活方式）', title_orig: 'Περὶ τοῦ Πυθαγορείου βίου', author: '揚布利科斯', era: '約公元 300 年', language: '古希臘文', status: 'whole', note: '把畢達哥拉斯寫成教團創立者：入教考驗、緘默期、共財、戒律——異教修道生活的典範文本。' },
            { title_zh: '普羅提諾傳', title_orig: 'Περὶ τοῦ Πλωτίνου βίου', author: '波菲利', era: '約公元 301 年', language: '古希臘文', status: 'whole', note: '弟子為師作傳並附《九章集》編纂說明；記其一生四次與太一合一，及臨終遺言「把你們裡面的神帶回宇宙的神那裡」。' },
            { title_zh: '哲學家與辯士傳', title_orig: 'Βίοι φιλοσόφων καὶ σοφιστῶν', author: '薩爾迪斯的歐納庇烏斯', era: '約公元 396 年', language: '古希臘文', status: 'whole', note: '新柏拉圖師承的群像傳，並記塞拉皮雍神廟被毀、修士取代哲人的過程——異教知識人的悲憤實錄。' },
            { title_zh: '普羅克洛傳（論幸福）', title_orig: 'Πρόκλος ἢ Περὶ εὐδαιμονίας', author: '新普勒的馬里努斯', era: '公元 486 年', place: '雅典', language: '古希臘文', status: 'whole', note: '以德目階梯結構為師作傳，記其守齋、禱告、見神顯現與治病；異教聖徒傳的完成形態。' },
            { title_zh: '哲學史（伊西多爾傳）', title_orig: 'Φιλόσοφος Ἱστορία', author: '達馬斯基烏斯', era: '約公元 520 年', language: '古希臘文', status: 'fragment', via: '佛提烏《書目》與《蘇達辭書》', note: '最後一代異教哲人的群像與軼事，字裡行間是一個正在消失的世界的自我記錄。Ω 卷互見。' },
          ],
        },
      ],
    },
    // ──────────────────────────── Ψ 爭辯書 ────────────────────────────
    {
      key: 'Ps', sigil: 'Ψ', name: '爭辯書', name_en: 'The Book of Contention',
      parallel: '護教書信', clock: 'historical', span: '公元 178–386 年',
      summary: '按年代排，本卷自成一部節節敗退史：從「我來揭穿你們」到「請留我們一座神廟」。多數原書已被焚毀，僅存敵證。',
      divisions: [
        {
          key: 'ps-attack', label: '攻勢', label_en: 'The Offensive',
          works: [
            {
              title_zh: '真道', title_orig: 'Ἀληθὴς Λόγος / Alethes Logos', author: '塞爾蘇斯',
              era: '約公元 178 年', language: '古希臘文', status: 'hostile',
              via: '奧利金《駁塞爾蘇斯》（約公元 248 年）逐段引錄',
              note: '現存最早的反基督教論著，靠敵手的逐段引用而幾乎完整還原。',
              intro: '一位中期柏拉圖派學者對基督教的全面批判：耶穌是私生子與埃及術士、門徒是無知漁夫、復活只有歇斯底里的女人作證、基督徒拒服兵役與公職將使帝國崩解。奧利金七十年後為駁斥而逐段引錄，使原書得以幾乎完整還原——這是「敵證」層最典型的個案，也是本藏經必須另設此標記的原因。',
            },
            { title_zh: '駁基督徒', title_orig: 'Κατὰ Χριστιανῶν / Contra Christianos', author: '波菲利', era: '約公元 270–300 年', language: '古希臘文', extent: '原為 15 卷', status: 'hostile', via: '優西比烏、耶柔米、馬卡里烏斯等引錄', note: '古代最有學問的一部反基督教著作，開歷史考據式聖經批判之先；公元 448 年遭下令焚毀，僅存殘篇。' },
            { title_zh: '愛真理者', title_orig: 'Φιλαλήθης Λόγος', author: '希耶羅克勒斯', era: '公元 303 年', language: '古希臘文', status: 'hostile', via: '優西比烏《駁希耶羅克勒斯》', note: '大迫害發動之年所作，主張阿波羅尼烏斯的神蹟更可信而基督徒卻不奉之為神——首次以「比較宗教」為武器。' },
          ],
        },
        {
          key: 'ps-restoration', label: '復興', label_en: 'The Restoration',
          works: [
            {
              title_zh: '駁加利利人', title_orig: 'Κατὰ Γαλιλαίων / Contra Galilaeos', author: '尤利安',
              era: '公元 362–363 年冬', place: '安提阿', language: '古希臘文', status: 'hostile',
              via: '亞歷山卓的區利羅《駁尤利安》',
              note: '唯一一位以皇帝之尊親自撰文駁斥基督教者。',
              intro: '尤利安在對波斯用兵前的冬營中寫成，逐條比對摩西與柏拉圖、希伯來律法與希臘城邦，指基督徒既背離猶太人的律法、又不接受希臘人的智慧，兩頭落空。書中最刺痛的一擊是承認基督徒的濟貧與埋葬做得比異教徒好，並下令異教祭司必須照做。原書已佚，靠區利羅的駁論保存約前三分之一。',
            },
            { title_zh: '致祭司書信', title_orig: 'Ἐπιστολαί (πρὸς ἱερέας)', author: '尤利安', era: '公元 362–363 年', language: '古希臘文', status: 'whole', note: '要求祭司戒酒色、讀哲學、設立救濟院與客旅所——異教史上唯一一份「教牧書信」，內容幾乎全是向基督教學來的。' },
          ],
        },
        {
          key: 'ps-plea', label: '請命', label_en: 'The Plea',
          works: [
            { title_zh: '為神廟辯（第三十號演說）', title_orig: 'Ὑπὲρ τῶν ἱερῶν / Pro templis', author: '安提阿的利巴尼烏斯', era: '公元 386 年', place: '安提阿', language: '古希臘文', status: 'whole', note: '上書皇帝，控訴黑衣修士成群拆毀鄉間神廟；語氣已從辯論轉為哀求。本卷終篇。' },
            { title_zh: '第三號陳情', title_orig: 'Relatio III', author: '敘馬庫斯', era: '公元 384 年', language: '拉丁文', track: 'latin', status: 'whole', note: '「通往如此大奧祕的路不會只有一條」——羅馬卷六收正文，此處互見。' },
          ],
        },
      ],
    },
    // ──────────────────────────── Ω 終卷 ────────────────────────────
    {
      key: 'W', sigil: 'Ω', name: '終卷', name_en: 'The Last Book',
      parallel: '啟示錄', clock: 'historical', span: '公元 362–529 年',
      summary: '按年代排到 529 年為止。與羅馬卷六在同一年合攏：東邊雅典學園關閉，西邊卡西諾山的阿波羅聖林被伐倒。',
      divisions: [
        {
          key: 'w-oracle', label: '最後的神諭', label_en: 'The Last Oracle',
          works: [
            {
              title_zh: '德爾菲致尤利安的最後神諭', title_orig: 'The last Delphic oracle',
              author: '德爾菲（傳由御醫奧里巴西烏斯攜回）', era: '公元 362 年', language: '古希臘文',
              extent: '3 行', status: 'fragment', via: '菲洛斯托爾吉烏斯《教會史》、凱德倫努斯',
              note: '「告訴王，華美的殿宇已然傾倒；福波斯再無居所、無預言的月桂、無說話的泉。」',
              intro: '尤利安遣人往德爾菲問神，得此三行答覆。真偽自古有爭議——它可能出自基督徒之手，作為異教自認終結的宣告。但無論真偽，它都是這件事最好的紀錄：問的人是最後一位嘗試復興異教的皇帝，答的是希臘一千兩百年來的中央神諭所，而答覆是承認自己已經沒有話說。本藏經以之開啟終卷。',
            },
          ],
        },
        {
          key: 'w-chronicle', label: '神廟關閉編年', label_en: 'The Chronicle of Closure',
          works: [
            { title_zh: '塞拉皮雍神廟被毀（391）', title_orig: 'The destruction of the Serapeum', author: '綴輯（歐納庇烏斯、魯菲努斯、蘇格拉底‧斯科拉斯提庫斯）', era: '公元 391 年', place: '亞歷山卓', language: '古希臘文／拉丁文', status: 'fragment', note: '異教方（歐納庇烏斯）與基督教方（魯菲努斯）的兩份記述並置，是本卷體例的示範。' },
            { title_zh: '狄奧多西禁令', title_orig: 'Codex Theodosianus XVI.10', author: '狄奧多西一世', era: '公元 391–392 年', language: '拉丁文', status: 'whole', track: 'latin', note: '全面禁止獻祭、進廟、家中奉神像；異教自此在法律上成為犯罪。' },
            { title_zh: '末屆古代奧林匹亞競技（393）', title_orig: 'The last ancient Olympiad', author: '綴輯', era: '公元 393 年', status: 'fragment', note: '延續一千一百餘年的泛希臘祭典就此中止。' },
            { title_zh: '希帕提婭之死（415）', title_orig: 'The murder of Hypatia', author: '綴輯（蘇格拉底‧斯科拉斯提庫斯、達馬斯基烏斯、尼基烏的約翰）', era: '公元 415 年', place: '亞歷山卓', language: '古希臘文', status: 'fragment', note: '女數學家兼柏拉圖學派教師遭暴民殺害；異教與基督教兩方的記述差距極大，並收。' },
          ],
        },
        {
          key: 'w-lastworks', label: '最後的作品', label_en: 'The Last Works',
          works: [
            {
              title_zh: '戴奧尼索斯譚', title_orig: 'Διονυσιακά / Dionysiaca', author: '帕諾波利斯的諾努斯',
              era: '約公元 450–470 年', place: '埃及‧帕諾波利斯', language: '古希臘文', extent: '全 48 卷，21,286 行',
              status: 'whole',
              note: '現存最長的古代史詩，也是最後一部異教史詩——而作者同時寫了《約翰福音》詩體改寫。',
              intro: '四十八卷，卷數刻意等同《伊利亞特》加《奧德賽》，敘戴奧尼索斯的誕生、遠征印度與升入諸神之列。它是異教神話最後一次以史詩規模被完整重述，辭藻繁複到近乎目眩。最耐人尋味的是同一位作者另有一部《約翰福音》的六步格改寫本傳世——同一支筆，同一種格律，寫兩個彼此取代的宗教。這一事實本身就是本卷最好的註腳。',
            },
            { title_zh: '哲學史（伊西多爾傳）殘篇', title_orig: 'Φιλόσοφος Ἱστορία', author: '達馬斯基烏斯', era: '約公元 520 年', language: '古希臘文', status: 'fragment', note: '最後一代異教哲人的自我記錄；Χ 卷收正文，此處按年代互見。' },
            { title_zh: '亞里斯多德註疏', title_orig: 'Commentaria in Aristotelem', author: '西里西亞的辛普利丘', era: '公元 530 年代', language: '古希臘文', status: 'whole', note: '流亡途中或之後寫成的巨帙註疏，因大量引錄前蘇格拉底原文而成為早期希臘哲學的最大保存者。' },
          ],
        },
        {
          key: 'w-end', label: '五二九', label_en: 'The Year 529',
          works: [
            { title_zh: '查士丁尼關閉雅典學園', title_orig: 'The closing of the Athenian Academy', author: '綴輯（馬拉拉斯《編年史》、《查士丁尼法典》I.11.10）', era: '公元 529 年', place: '雅典', language: '古希臘文／拉丁文', status: 'fragment', note: '禁異教徒授課並沒收其財產；柏拉圖創立於前 387 年的學統至此中斷。' },
            { title_zh: '七哲東走波斯', title_orig: 'The seven philosophers at the Persian court', author: '阿伽提亞斯《歷史》二‧30–31', era: '公元 531–532 年（記事）', language: '古希臘文', status: 'whole', note: '達馬斯基烏斯、辛普利丘等七人赴庫思老一世宮廷，失望而歸；和約中特別載明他們可返鄉且不得被迫改宗。全書之跋。' },
            { title_zh: '哲學的慰藉', title_orig: 'De consolatione philosophiae', author: '波愛修斯', era: '公元 524 年', place: '帕維亞獄中', language: '拉丁文', extent: '全 5 卷', track: 'latin', status: 'whole', note: '作者是基督徒，全書卻是純粹的新柏拉圖式慰藉，從頭到尾未出現基督之名。希臘傳統在拉丁世界的最後一口氣——已經不能叫神的名字，只能叫哲學。' },
          ],
        },
      ],
    },
  ],
}
