// 續藏一 —— 地中海文獻（埃及與北非）
//
// 1929 年，一批科普特文紙草抄本在開羅的古董市場出現，來源是法尤姆南緣的
// 梅迪奈特馬迪（Medinet Madi）。買主分頭買走，於是同一批書從此一半在柏林、
// 一半在都柏林。這批抄本是**摩尼教研究的分水嶺**：在此之前，全世界對摩尼教的
// 認識幾乎全來自反對者；在此之後，第一次有了摩尼教徒寫給摩尼教徒看的整本書。
//
// 🚨 **這一藏有一半已經不存在了。**
//    柏林那半的《教會史》與《書信集》兩部抄本在二戰末期失蹤，
//    一般認為是 1945 年被運往蘇聯後下落不明。它們在失蹤前只刊布過少量樣頁。
//    所以本藏的條目分成兩種：讀得到的，和「曾經有人讀過、現在誰也讀不到」的。
//    後者的 status 仍記 partial／fragment 而非 lost-listed——
//    因為書曾被著錄、被拍照、被抄錄過一部分，這與從未有人見過的佚書不是同一回事。
//
// ══════════ 與 /gnostic 的分工（重要，別重複收）══════════
//
//   本站 /gnostic 已從 gnosis.org 收了 75 篇「摩尼教文獻」，主要是科普特《詩篇集》
//   的英譯選段與《凱法萊亞》摘錄，已有繁中對照。那一批是**選本**，
//   按 gnosis.org 自己的編排走，沒有抄本編號、沒有卷次結構。
//   本藏做的是另一件事：按抄本與卷次立目，標明每一部的刊布狀態與可及性。
//   兩邊重疊的條目以 seealso 互指，不重複翻譯。

import type { ManiCanon } from './types'

const COPT = '科普特文（賽義德方言）'

export const COPTIC_CANON: ManiCanon = {
  key: 'coptic',
  name: '地中海文獻',
  name_en: 'The Mediterranean Codices',
  glyph: '地',
  subtitle: '續藏 — 埃及與北非出土的教團典籍',
  scriptural: true,
  language: '科普特文（賽義德方言）與希臘文，譯自敘利亞語',
  era: '抄本約 4–5 世紀；所譯內容約 3 世紀',
  summary:
    '摩尼教傳入埃及後，教團把敘利亞語與希臘語的典籍譯成科普特文，'
    + '在四世紀抄成一批大部頭的紙草抄本。1929 年梅迪奈特馬迪出土的七部抄本，'
    + '以及 1990 年代起在達赫拉綠洲凱利斯村發掘出的文書，構成本藏。'
    + '這是摩尼教文獻中**唯一有整本書可讀**的一群：'
    + '《凱法萊亞》逐章記錄摩尼與門徒的問答，《詩篇集》保存了教團實際唱的詩，'
    + '《講道集》裡則有一篇當時人寫下的摩尼受難始末。'
    + '沒有這批抄本，摩尼教史只能從敵人的角度寫。',
  parts: [
    {
      key: 'p-medinet', label: '梅迪奈特馬迪抄本', label_en: 'The Medinet Madi Codices',
      desc:
        '1929 年出土的七部四世紀紙草抄本，分藏柏林與都柏林。'
        + '其中兩部於二戰末期失蹤，一部至今仍未全刊。',
      volumes: ['kephalaia', 'psalm-book', 'homilies', 'synaxeis', 'lost-codices'],
    },
    {
      key: 'p-greek', label: '希臘文抄本', label_en: 'The Greek Codices',
      desc:
        '埃及出土的希臘文摩尼教抄本。《科隆摩尼古卷》是其中最重要的一件，'
        + '也是**摩尼生平唯一的教內一手文獻**。',
      volumes: ['cmc'],
    },
    {
      key: 'p-kellis', label: '凱利斯文書', label_en: 'The Kellis Papyri',
      desc:
        '1991 年起在達赫拉綠洲凱利斯（今伊斯曼特—哈拉卜）發掘出的科普特文與希臘文文書。'
        + '與梅迪奈特馬迪的「典籍」不同，這一批是**活人的日常**：家書、帳目、禮儀抄本。',
      volumes: ['kellis'],
    },
  ],
  volumes: [
    {
      key: 'kephalaia',
      sigil: '凱',
      name: '凱法萊亞',
      name_orig: 'Kephalaia',
      name_en: 'The Kephalaia',
      provenance: '柏林國家博物館 P. 15996（教誨篇）；都柏林切斯特‧比替圖書館（智慧篇）',
      era: '抄本 4 世紀',
      extent: '教誨篇存 122 章中之大部；智慧篇存第 321–347 章等',
      summary:
        '希臘語 kephalaia 意為「章目」。全書是摩尼與門徒的問答集：'
        + '門徒問一個問題，摩尼作答，一問一答自成一章。'
        + '這個體裁讓它成為**今日所知最詳盡的摩尼教義文獻**——'
        + '從光明分子的下降、日月的運行、五種樹與五種身體，'
        + '到齋戒的理由、聽者與選民的分別，乃至占星與宗教心理學，無所不談。'
        + '分兩部：柏林的《導師的凱法萊亞》與都柏林的《我主摩尼智慧的凱法萊亞》。',
      divisions: [
        {
          key: 'd-keph',
          label: '凱法萊亞',
          columns: { orig: 'copyright', en: 'copyright', zh: 'none' },
          texts: [
            {
              slug: 'kephalaia-teacher',
              title_zh: '導師的凱法萊亞',
              title_orig: 'Kephalaia of the Teacher',
              title_en: 'The Kephalaia of the Teacher',
              siglum: '1 Ke',
              author: '摩尼門徒輯錄',
              era: '抄本 4 世紀；內容 3 世紀',
              language: COPT,
              provenance: '柏林國家博物館 P. 15996',
              status: 'partial',
              extent: '原 122 章，存大部但多有殘損',
              note: '今日所知最詳盡的摩尼教義文獻。',
              intro:
                '柏林抄本，一百二十二章的問答集。每章以「導師說」起頭，'
                + '回答門徒關於宇宙、身體、齋戒、教團規制乃至星象的問題。'
                + '它的價值在於**成系統**：其他材料給的是碎片與口號，'
                + '這部書給的是一個完整的世界圖景，而且是教內人為教內人寫的。'
                + '科普特文校本由波洛茨基與伯利希陸續刊布，'
                + '英譯本（加德納，1995）是目前唯一的完整英譯，仍在版權內。',
              seealso: ['kephalaia-wisdom'],
            },
            {
              slug: 'kephalaia-wisdom',
              title_zh: '我主摩尼智慧的凱法萊亞',
              title_orig: 'Kephalaia of the Wisdom of My Lord Mani',
              title_en: 'The Kephalaia of the Wisdom of My Lord Mani',
              siglum: '2 Ke',
              author: '摩尼門徒輯錄',
              era: '抄本 4 世紀',
              language: COPT,
              provenance: '都柏林切斯特‧比替圖書館',
              status: 'partial',
              extent: '存第 321 章以下數十章',
              note: '都柏林抄本。刊布遠晚於柏林那部，二十一世紀才陸續出版。',
              intro:
                '都柏林的另一部凱法萊亞，章次接在柏林本之後（自第 321 章起），'
                + '顯示兩部原屬同一套更大的問答集。內容更偏重摩尼晚年'
                + '在薩珊宮廷與波斯的活動，因此也是研究摩尼生平的重要材料。'
                + '這部抄本受損嚴重且刊布極慢，前半在二十世紀幾乎無人能用，'
                + '直到二〇〇〇年代才陸續有校訂本問世。',
              seealso: ['kephalaia-teacher'],
            },
          ],
        },
      ],
    },
    {
      key: 'psalm-book',
      sigil: '詩',
      name: '詩篇集',
      name_orig: 'Psalm-Book',
      name_en: 'The Manichaean Psalm-Book',
      provenance: '都柏林切斯特‧比替圖書館；部分在柏林',
      era: '抄本 4 世紀',
      extent: '第二部（Allberry 1938）已刊；第一部迄今未全刊',
      summary:
        '摩尼教團實際詠唱的詩集，是本藏**最接近宗教生活現場**的一部。'
        + '詩篇按用途與作者群分組：貝馬節（教曆最大的節日，紀念摩尼殉道）所唱的貝馬詩篇、'
        + '託名使徒托馬斯的托馬斯詩篇、赫拉克利德詩篇、流浪者詩篇等。'
        + '其中若干首與敘利亞基督教詩歌、與《多馬福音》的語彙關係密切，'
        + '是摩尼教與早期基督教關係的第一手證據。'
        + '奧爾伯里 1938 年刊布了第二部；第一部至今沒有完整校本。',
      divisions: [
        {
          key: 'd-psalms',
          label: '詩篇集',
          columns: { orig: 'copyright', en: 'available', zh: 'available' },
          texts: [
            {
              slug: 'psalm-book',
              title_zh: '詩篇集（第二部）',
              title_orig: 'Psalm-Book, Part II',
              title_en: 'A Manichaean Psalm-Book, Part II',
              siglum: '2 Ps',
              era: '抄本 4 世紀',
              language: COPT,
              provenance: '都柏林切斯特‧比替圖書館',
              status: 'partial',
              extent: '約 290 首，多有殘損',
              note: '奧爾伯里 1938 年校訂刊布，含科普特文與英譯對照。',
              intro:
                '摩尼教文獻中傳唱最廣的一部。奧爾伯里的校本把科普特文與英譯並排刊出，'
                + '使它成為少數西方學界之外也能使用的摩尼教原典。'
                + '詩中反覆出現的主題是靈魂受困於身體、渴望歸返光明國度，'
                + '以及對摩尼殉道的記念。本站 /gnostic 已收其中十八首的英中對照選段'
                + '（出自 gnosis.org），但那是選本；本條指的是整部校本。',
              seealso: ['bema-psalms', 'thomas-psalms'],
            },
            {
              slug: 'bema-psalms',
              title_zh: '貝馬詩篇',
              title_orig: 'Bema Psalms',
              title_en: 'The Bema Psalms',
              siglum: '2 Ps 218–241',
              era: '抄本 4 世紀',
              language: COPT,
              provenance: '都柏林切斯特‧比替圖書館',
              status: 'partial',
              extent: '第 218–241 首',
              note: '貝馬節（紀念摩尼殉道）所唱。摩尼教曆一年中最大的節日。',
              intro:
                '貝馬（希臘語 bēma，「座」）是摩尼教最重要的節日：'
                + '教團在節期擺設一個**空的座位**，象徵摩尼親臨審判與赦罪。'
                + '這一組詩篇就是那一天所唱的，內容集中在摩尼的受難、教會的傳承'
                + '與罪的赦免。一個以空座位為中心的節日，'
                + '把這個宗教如何處理「創教者已死」這件事說得很清楚。',
              seealso: ['psalm-book', 'homily-crucifixion'],
            },
            {
              slug: 'thomas-psalms',
              title_zh: '托馬斯詩篇',
              title_orig: 'Psalms of Thomas',
              title_en: 'The Psalms of Thomas',
              siglum: '2 Ps（托馬斯組）',
              era: '抄本 4 世紀',
              language: COPT,
              provenance: '都柏林切斯特‧比替圖書館',
              status: 'partial',
              extent: '二十餘首',
              note: '託名使徒托馬斯。與敘利亞基督教詩歌傳統關係密切。',
              intro:
                '託名多馬的一組詩，語彙與意象與《所羅門頌歌》'
                + '及敘利亞基督教的詩歌傳統高度重疊，'
                + '少數學者甚至主張其中某些首根本不是摩尼教作品，'
                + '而是摩尼教團收編的既有敘利亞詩歌。'
                + '無論如何，它們是「摩尼教究竟算不算一種基督教」'
                + '這個長年爭論中最常被搬出來的證據。',
              seealso: ['psalm-book'],
            },
          ],
        },
      ],
    },
    {
      key: 'homilies',
      sigil: '講',
      name: '講道集',
      name_orig: 'Homilies',
      name_en: 'The Homilies',
      provenance: '柏林國家博物館',
      era: '抄本 4 世紀',
      extent: '四篇，殘損嚴重',
      summary:
        '四篇講道，波洛茨基 1934 年刊布。其中《摩尼受難記》是'
        + '**教內所寫的摩尼死亡始末**，與後世反對者所記的版本可以對讀；'
        + '《大戰講道》則是一篇末世論講章，描述末日前的大戰與教會的勝利。'
        + '這一卷的重要性在於它記的是事件而非教義：'
        + '摩尼如何被沙普爾之子巴赫拉姆一世下獄、如何死在獄中、'
        + '教團如何處理這件事，都出自這裡。',
      divisions: [
        {
          key: 'd-hom',
          label: '講道集',
          columns: { orig: 'copyright', en: 'copyright', zh: 'none' },
          texts: [
            {
              slug: 'homily-crucifixion',
              title_zh: '摩尼受難記',
              title_orig: 'The Narrative about the Crucifixion',
              title_en: 'The Narrative about the Crucifixion of Mani',
              siglum: 'Hom.',
              era: '抄本 4 世紀',
              language: COPT,
              provenance: '柏林國家博物館',
              status: 'partial',
              extent: '殘損嚴重',
              note: '教內所記的摩尼死亡始末。標題用「受難」，刻意比附耶穌。',
              intro:
                '摩尼在巴赫拉姆一世治下被囚，二十六天後死於獄中（約 274／277 年）。'
                + '這篇講道是教團自己對這件事的敘述，而且刻意用了'
                + '「受難」(stauros，十字架) 這個字——摩尼並未被釘死，'
                + '用這個詞是要讀者把它讀成另一次耶穌之死。'
                + '這種比附是摩尼教自我定位的核心：摩尼是最後一位使徒，'
                + '他的死完成了前面每一位使徒未完成的事。',
              seealso: ['bema-psalms', 'acta-archelai'],
            },
            {
              slug: 'homily-great-war',
              title_zh: '大戰講道',
              title_orig: 'Sermon on the Great War',
              title_en: 'The Sermon on the Great War',
              siglum: 'Hom.',
              era: '抄本 4 世紀',
              language: COPT,
              provenance: '柏林國家博物館',
              status: 'partial',
              extent: '殘損嚴重',
              note: '末世論講章，描述末日前的大戰、教會受難與最終的勝利。',
              intro:
                '一篇末世講章：世界末了之前將有一場大戰，教會受盡逼迫，'
                + '而後義人得勝、光明與黑暗最終分離。'
                + '這類文字在受迫害的教團裡有明確的功能——'
                + '把眼前的苦難編進一個必然勝利的劇本裡。'
                + '摩尼教從三世紀末起在羅馬與薩珊兩邊同時遭禁，'
                + '這篇講道的處境感因此格外真實。',
            },
          ],
        },
      ],
    },
    {
      key: 'synaxeis',
      sigil: '聚',
      name: '聚會書',
      name_orig: 'Synaxeis',
      name_en: 'The Synaxeis of the Living Gospel',
      provenance: '都柏林切斯特‧比替圖書館',
      era: '抄本 4 世紀',
      extent: '殘損極嚴重，刊布中',
      summary:
        '對《活福音》的逐段講解與集會誦讀本。'
        + '這一部的意義非比尋常：七經之首的《活福音》原書全佚，'
        + '而這部書是**古代摩尼教徒為那部書做的註解**——'
        + '換句話說，它是我們僅有的、最接近《活福音》內容的東西。'
        + '可惜抄本殘損極嚴重，刊布緩慢，至今仍在整理之中。',
      divisions: [
        {
          key: 'd-syn',
          label: '聚會書',
          columns: { orig: 'copyright', en: 'copyright', zh: 'none' },
          texts: [
            {
              slug: 'synaxeis',
              title_zh: '活福音聚會書',
              title_orig: 'Synaxeis of the Living Gospel',
              title_en: 'The Synaxeis of the Living Gospel',
              siglum: 'Syn.',
              era: '抄本 4 世紀',
              language: COPT,
              provenance: '都柏林切斯特‧比替圖書館',
              status: 'fragment',
              extent: '殘損極嚴重',
              note: '《活福音》的集會誦讀與講解本——僅存最接近該書內容的材料。',
              intro:
                '摩尼教團在集會中誦讀《活福音》並逐段講解，講解的內容被抄成這一部書。'
                + '由於《活福音》本身全佚，這部註解成了間接的路徑：'
                + '透過古人講什麼，去推被講的是什麼。'
                + '但抄本碎成極小的片段，整理者必須先把紙草碎片按纖維走向拼回去，'
                + '再判斷哪一片接哪一片——這是整個摩尼教文獻學裡最慢的一項工作。',
              seealso: ['living-gospel'],
            },
          ],
        },
      ],
    },
    {
      key: 'lost-codices',
      sigil: '佚',
      name: '戰時失蹤的兩部',
      name_en: 'The Codices Lost in the War',
      provenance: '原藏柏林；1945 年後下落不明',
      era: '抄本 4 世紀',
      extent: '失蹤前僅刊布少量樣頁',
      summary:
        '🚨 梅迪奈特馬迪七部抄本中的兩部——《教會史》與《書信集》——'
        + '在二戰末期從柏林失蹤，一般認為 1945 年被運往蘇聯後下落不明。'
        + '它們在失蹤前只被拍照與刊布過少量樣頁。'
        + '這意味著摩尼教最早的教會史、以及摩尼本人書信的科普特文譯本，'
        + '**曾經在二十世紀被人讀過，而現在誰也讀不到**。'
        + '本卷把它們單獨立目，是要讓這個事實在版面上看得見：'
        + '一部文獻的失傳不只發生在古代。',
      divisions: [
        {
          key: 'd-lost',
          label: '失蹤抄本',
          columns: { orig: 'none', en: 'none', zh: 'none' },
          texts: [
            {
              slug: 'church-history-codex',
              title_zh: '教會史抄本',
              title_orig: 'Acta codex',
              title_en: 'The Church History (Acts) Codex',
              siglum: '佚 1',
              era: '抄本 4 世紀',
              language: COPT,
              provenance: '原藏柏林；1945 年後下落不明',
              status: 'fragment',
              via: '失蹤前刊布的樣頁與著錄',
              extent: '僅存少量樣頁與描述',
              note: '摩尼死後教團最早的自述史。二戰末期失蹤。',
              intro:
                '記摩尼死後教團如何在薩珊帝國的迫害下傳布、'
                + '第一代領袖如何繼承、各地教會如何建立——'
                + '相當於摩尼教的《使徒行傳》。'
                + '在 1930 年代被編目與部分拍攝後，這部抄本於二戰末期從柏林消失。'
                + '今日關於摩尼教早期組織的討論，'
                + '只能繞過這部本該是核心的材料進行。',
            },
            {
              slug: 'epistles-codex',
              title_zh: '書信集抄本',
              title_orig: 'Epistulae codex',
              title_en: 'The Epistles Codex',
              siglum: '佚 2',
              era: '抄本 4 世紀',
              language: COPT,
              provenance: '原藏柏林；1945 年後下落不明',
              status: 'fragment',
              via: '失蹤前刊布的樣頁；另有都柏林殘葉',
              extent: '僅存少量樣頁與描述',
              note: '摩尼書信的科普特文譯本。二戰末期失蹤。',
              intro:
                '七經之一《書信集》的科普特文譯本。'
                + '如果它還在，我們今天就能讀到摩尼書信的整批譯文，'
                + '而不必依賴奧古斯丁為了駁斥而抄錄的那幾段。'
                + '這是本藏經裡最令人扼腕的一條：'
                + '一部能夠改寫整個領域的書，在被真正讀懂之前就消失了。',
              seealso: ['epistles'],
            },
          ],
        },
      ],
    },
    {
      key: 'cmc',
      sigil: '科隆',
      name: '科隆摩尼古卷',
      name_orig: 'Codex Manichaicus Coloniensis',
      name_en: 'The Cologne Mani Codex',
      provenance: '埃及（確切出土地不明）；今藏科隆大學',
      era: '抄本 5 世紀；所記內容 3 世紀',
      extent: '192 頁，存 96 葉',
      summary:
        '全世界最小的古卷之一——每頁約 3.5×4.5 公分，比火柴盒大不了多少，'
        + '每頁只寫得下二十來行。1969 年辨認出來，1970 年起陸續刊布，'
        + '其重要性只有梅迪奈特馬迪抄本可比。'
        + '內容是摩尼的早年傳記：他生在一個受洗派（埃爾克塞派）團體裡，'
        + '自幼屢次見異象，二十四歲時與那個團體決裂而自立。'
        + '🚨 **這是摩尼生平唯一的教內一手記述**。'
        + '在它刊布之前，所有關於摩尼身世的說法都出自《阿基勞斯行傳》那一系的敵證，'
        + '而那些說法今天已知大半是編的。',
      divisions: [
        {
          key: 'd-cmc',
          label: '科隆摩尼古卷',
          columns: { orig: 'available', en: 'copyright', zh: 'none' },
          texts: [
            {
              slug: 'cologne-mani-codex',
              title_zh: '科隆摩尼古卷',
              title_orig: 'Περὶ τῆς γέννης τοῦ σώματος αὐτοῦ',
              title_en: 'The Cologne Mani Codex: On the Origin of His Body',
              siglum: 'CMC',
              author: '摩尼門徒輯錄',
              era: '抄本 5 世紀',
              language: '希臘文',
              provenance: '埃及；今藏科隆大學紙草學研究所',
              status: 'partial',
              extent: '存 96 葉（192 頁），末尾殘缺',
              note: '🚨 摩尼生平唯一的教內一手文獻。1970 年才刊布。',
              intro:
                '書題《論其身體的來歷》，由摩尼的門徒輯錄他自述的異象與早年經歷，'
                + '並引述多位早期門徒的見證。'
                + '最重大的發現是：摩尼成長於一個猶太基督教性質的受洗派團體，'
                + '他的教義是**從那個環境裡長出來的**，'
                + '而不是如敵證所說從波斯的祆教或某個騙子那裡偷來的。'
                + '這一點改寫了摩尼教的起源問題——'
                + '它從「一個東方混合宗教」變成「一個猶太基督教的分支」。'
                + '書中所引《活福音》開卷語，與吐魯番殘卷 M 17 互相印證。',
              seealso: ['living-gospel', 'm17-living-gospel', 'acta-archelai'],
            },
          ],
        },
      ],
    },
    {
      key: 'kellis',
      sigil: '凱利',
      name: '凱利斯文書',
      name_orig: 'P. Kellis',
      name_en: 'The Kellis Papyri',
      provenance: '埃及達赫拉綠洲伊斯曼特—哈拉卜（古凱利斯）；1991 年起發掘',
      era: '4 世紀',
      extent: '數百件文書，陸續刊布',
      summary:
        '與梅迪奈特馬迪的「典籍」完全不同的一批東西：這是**考古發掘出土**的'
        + '（不是古董市場買來的），而且大多是日常文書——家書、帳目、契約、'
        + '禮儀抄本、學童習字。'
        + '因為有明確的地層與年代，它第一次讓人看見摩尼教徒實際怎麼生活：'
        + '一個信摩尼教的商人寫信給母親談生意與禱告，'
        + '同一個家庭裡有人是選民、有人是聽者。'
        + '其中還發現了希臘文與科普特文的《大祈禱文》禮儀抄本。',
      divisions: [
        {
          key: 'd-kellis',
          label: '凱利斯文書',
          columns: { orig: 'copyright', en: 'copyright', zh: 'none' },
          texts: [
            {
              slug: 'kellis-letters',
              title_zh: '凱利斯書信',
              title_orig: 'P. Kellis Copt.',
              title_en: 'The Kellis Coptic Letters',
              siglum: 'P. Kellis',
              era: '4 世紀',
              language: '科普特文、希臘文',
              provenance: '達赫拉綠洲凱利斯，考古出土',
              status: 'partial',
              extent: '數十封，陸續刊布',
              note: '摩尼教徒的私人家書。有明確地層與年代的第一批摩尼教文獻。',
              intro:
                '一個四世紀埃及綠洲村落裡摩尼教家庭的往來書信。'
                + '談的是布匹買賣、家人健康、誰該寄錢回來——'
                + '中間夾著對「光明之父」的問安與對選民的供養安排。'
                + '這批材料的價值不在教義而在社會史：'
                + '它證明摩尼教不是躲在地下的祕密結社，'
                + '而是嵌在普通人親屬與生意網絡裡的一種日常信仰。',
            },
            {
              slug: 'kellis-prayer',
              title_zh: '大祈禱文',
              title_orig: 'The Prayer of the Emanations',
              title_en: 'The Prayer of the Emanations',
              siglum: 'P. Kellis Gr. 98',
              era: '4 世紀',
              language: '希臘文',
              provenance: '達赫拉綠洲凱利斯，考古出土',
              status: 'partial',
              extent: '一件較完整的禮儀抄本',
              note: '希臘文禮儀祈禱文，凱利斯所出最完整的宗教文本之一。',
              intro:
                '一篇逐層呼求光明諸神流出體的祈禱文，'
                + '結構與《詩篇集》中的讚詩相近，但用的是希臘文。'
                + '它證明埃及的摩尼教團在科普特文之外也用希臘文行禮，'
                + '而且這些禮文是**帶在身邊的**——'
                + '抄本出土於民居而非教堂或藏書室。',
            },
          ],
        },
      ],
    },
  ],
}
