import type { DazangEra } from './types'

// ─────────────────────────────────────────────────────────────────────────
// 古代基督教大藏經
//
// 年代結界（「八百／四百」雙軌死線）：
//   基督教文獻收錄至 800 年（前七次大公會議終結；查理曼加冕、第二次尼西亞 787）。
//   猶太教文獻收錄至 400 年（第二聖殿至耶柔米時代，基督教與猶太學術最後交集）。
//
// 每藏分「正藏／外藏」兩套平行目錄：
//   正藏 = 尼西亞教會（大公傳統）接受者。經藏正藏 = 92 卷「普世新舊約正典與次經」，
//          入選準則：有尼西亞教會使用 + 兩位以上教父推薦 + 重要古抄本收錄。
//   外藏 = 分類與正藏對照、但不被尼西亞教會接受者（偽典／異端／猶太教／外教見證）。
// ─────────────────────────────────────────────────────────────────────────

export const ANCIENT_ERA: DazangEra = {
  key: 'ancient',
  name: '古代基督教大藏經',
  name_en: 'Ancient Christian Canon (to 800 CE)',
  glyph: '古',
  subtitle: '經‧律‧論‧史傳‧譯校‧書信‧禮儀‧詩文‧宣道‧類書（每藏分正藏／外藏）',
  boundary: '基督教文獻收錄至 800 年（前七次大公會議終結）；猶太教文獻收錄至 400 年（耶柔米與拉比學術最後交集）。',
  enabled: true,
  collections: [
    // ═══════════════════════════════════════════════════════ 1. 經藏
    {
      key: 'jing',
      name: '經藏',
      name_en: 'Scriptures',
      glyph: '經',
      genres: '經‧傳‧錄‧訓‧篇',
      summary: '神聖啟示的源頭。正藏為 92 卷「普世新舊約正典與次經」（尼西亞教會使用＋兩位以上教父推薦＋重要古抄本收錄）；外藏為分類對照的「影子聖經」——偽托先祖使徒之名、模仿正典文體而未獲大公教會接納者。',
      portal: { to: '/scripture', label: '聖經多版本對照' },
      zheng: {
        summary: '92 卷普世大正典：舊約 59 卷 + 新約 33 卷。含希伯來正典、七十士第二正典，以及達標的次經（禧年書、以諾書、巴拿巴書、克勉書、黑馬牧人書、彼得啟示錄等）。',
        divisions: [
          {
            key: 'law', label: '律法書', label_en: 'Law', desc: '信仰的絕對基石與神聖啟示（6 卷）。',
            works: [
              { title_zh: '創世經', title_orig: 'Genesis', link: '/scripture' },
              { title_zh: '出埃及經', title_orig: 'Exodus', link: '/scripture' },
              { title_zh: '利未經', title_orig: 'Leviticus', link: '/scripture' },
              { title_zh: '民數經', title_orig: 'Numbers', link: '/scripture' },
              { title_zh: '申命經', title_orig: 'Deuteronomy', link: '/scripture' },
              { title_zh: '禧年經', tier: 'eastern', title_orig: 'Jubilees', note: '奠基神聖曆法的小妥拉；衣索匹亞正典', link: '/apocrypha' },
            ],
          },
          {
            key: 'history', label: '歷史書', label_en: 'Histories', desc: '從應許之地到第二聖殿被毀的民族興衰（24 卷）。',
            works: [
              { title_zh: '約書亞記', title_orig: 'Joshua', link: '/scripture' },
              { title_zh: '士師記', title_orig: 'Judges', link: '/scripture' },
              { title_zh: '路得傳', title_orig: 'Ruth', link: '/scripture' },
              { title_zh: '撒母耳記上', title_orig: '1 Samuel', link: '/scripture' },
              { title_zh: '撒母耳記下', title_orig: '2 Samuel', link: '/scripture' },
              { title_zh: '列王紀上', title_orig: '1 Kings', link: '/scripture' },
              { title_zh: '列王紀下', title_orig: '2 Kings', link: '/scripture' },
              { title_zh: '歷代志上', title_orig: '1 Chronicles', link: '/scripture' },
              { title_zh: '歷代志下', title_orig: '2 Chronicles', link: '/scripture' },
              { title_zh: '以斯拉記', title_orig: 'Ezra', link: '/scripture' },
              { title_zh: '尼希米記', title_orig: 'Nehemiah', link: '/scripture' },
              { title_zh: '以斯拉記三', tier: 'lxx', title_orig: '3 Esdras (1 Esdras)', note: '希臘文以斯拉記', link: '/apocrypha' },
              { title_zh: '以斯拉記四', tier: 'eastern', title_orig: '4 Esdras (2 Esdras)', note: '衣索比亞以斯拉續篇', link: '/apocrypha' },
              { title_zh: '多比傳', tier: 'lxx', title_orig: 'Tobit', link: '/apocrypha' },
              { title_zh: '猶滴傳', tier: 'lxx', title_orig: 'Judith', link: '/apocrypha' },
              { title_zh: '以斯帖傳', title_orig: 'Esther', note: '內含七十士譯本補編', link: '/scripture' },
              { title_zh: '馬加比記一', tier: 'lxx', title_orig: '1 Maccabees', link: '/apocrypha' },
              { title_zh: '馬加比記二', tier: 'lxx', title_orig: '2 Maccabees', link: '/apocrypha' },
              { title_zh: '馬加比記三', tier: 'lxx', title_orig: '3 Maccabees', note: '東正教正典', link: '/apocrypha' },
              { title_zh: '馬加比記四', tier: 'lxx', title_orig: '4 Maccabees', link: '/apocrypha' },
              { title_zh: '衣索比亞馬加比記一', tier: 'eastern', title_orig: '1 Meqabyan' },
              { title_zh: '衣索比亞馬加比記二', tier: 'eastern', title_orig: '2 Meqabyan' },
              { title_zh: '衣索比亞馬加比記三', tier: 'eastern', title_orig: '3 Meqabyan' },
              { title_zh: '約瑟夫斯歷代志', tier: 'eastern', title_orig: 'Josippon', note: '第二聖殿興衰史（希伯來文）' },
            ],
          },
          {
            key: 'wisdom', label: '詩歌智慧書', label_en: 'Poetry & Wisdom', desc: '匯集篇、辭、箴、錄、歌、傳、訓的東方文學矩陣（9 卷）。',
            works: [
              { title_zh: '詩篇', title_orig: 'Psalms', note: '內含第 151–155 篇補編', link: '/scripture' },
              { title_zh: '所羅門詩篇', tier: 'patristic', title_orig: 'Psalms of Solomon', note: '法利賽獨立詩集', link: '/apocrypha' },
              { title_zh: '瑪拿西禱辭', tier: 'lxx', title_orig: 'Prayer of Manasseh', link: '/apocrypha' },
              { title_zh: '箴言', title_orig: 'Proverbs', link: '/scripture' },
              { title_zh: '傳道錄', title_orig: 'Ecclesiastes', link: '/scripture' },
              { title_zh: '雅歌', title_orig: 'Song of Songs', link: '/scripture' },
              { title_zh: '約伯傳', title_orig: 'Job', link: '/scripture' },
              { title_zh: '所羅門智訓', tier: 'lxx', title_orig: 'Wisdom of Solomon', link: '/apocrypha' },
              { title_zh: '便西拉德訓', tier: 'lxx', title_orig: 'Sirach / Ecclesiasticus', link: '/apocrypha' },
            ],
          },
          {
            key: 'minor-prophets', label: '十二先知書', label_en: 'Twelve Prophets', desc: '東正教傳統，排於大先知之前（12 卷）。',
            works: [
              { title_zh: '何西阿書', title_orig: 'Hosea', link: '/scripture' },
              { title_zh: '阿摩司書', title_orig: 'Amos', link: '/scripture' },
              { title_zh: '彌迦書', title_orig: 'Micah', link: '/scripture' },
              { title_zh: '約珥書', title_orig: 'Joel', link: '/scripture' },
              { title_zh: '俄巴底亞書', title_orig: 'Obadiah', link: '/scripture' },
              { title_zh: '約拿書', title_orig: 'Jonah', link: '/scripture' },
              { title_zh: '那鴻書', title_orig: 'Nahum', link: '/scripture' },
              { title_zh: '哈巴谷書', title_orig: 'Habakkuk', link: '/scripture' },
              { title_zh: '西番雅書', title_orig: 'Zephaniah', link: '/scripture' },
              { title_zh: '哈該書', title_orig: 'Haggai', link: '/scripture' },
              { title_zh: '撒迦利亞書', title_orig: 'Zechariah', link: '/scripture' },
              { title_zh: '瑪拉基書', title_orig: 'Malachi', link: '/scripture' },
            ],
          },
          {
            key: 'major-prophets', label: '大先知書', label_en: 'Major Prophets', desc: '古典先知的宣告、悔改與哀歌（4 卷）。',
            works: [
              { title_zh: '以賽亞書', title_orig: 'Isaiah', link: '/scripture' },
              { title_zh: '耶利米書', title_orig: 'Jeremiah', link: '/scripture' },
              { title_zh: '巴錄書', tier: 'lxx', title_orig: 'Baruch', note: '內含耶利米書信', link: '/apocrypha' },
              { title_zh: '耶利米哀歌', title_orig: 'Lamentations', link: '/scripture' },
            ],
          },
          {
            key: 'apocalyptic-prophets', label: '天啟先知書', label_en: 'Apocalyptic Prophets', desc: '異象、天使啟示與末世神義論（4 卷）。',
            works: [
              { title_zh: '以諾書', tier: 'eastern', title_orig: '1 Enoch', note: '天啟文學傳統之父；衣索匹亞正典', link: '/apocrypha' },
              { title_zh: '以西結書', title_orig: 'Ezekiel', note: '被擄初期的戰車與聖殿異象', link: '/scripture' },
              { title_zh: '巴錄二書', tier: 'eastern', title_orig: '2 Baruch', note: '耶路撒冷陷落當下的末日啟示', link: '/apocrypha' },
              { title_zh: '但以理書', title_orig: 'Daniel', note: '內含蘇撒拿、彼勒與大龍等補編', link: '/scripture' },
            ],
          },
          {
            key: 'gospels', label: '福音書', label_en: 'Gospels', desc: '基督的降世與歷史生平（4 卷）。',
            works: [
              { title_zh: '馬太福音', title_orig: 'Matthew', link: '/scripture' },
              { title_zh: '馬可福音', title_orig: 'Mark', link: '/scripture' },
              { title_zh: '路加福音', title_orig: 'Luke', link: '/scripture' },
              { title_zh: '約翰福音', title_orig: 'John', link: '/scripture' },
            ],
          },
          {
            key: 'acts', label: '行傳', label_en: 'Acts', desc: '基督升天後的教會奠基行動（1 卷；十二使徒遺訓與使徒教訓已移入律藏）。',
            works: [
              { title_zh: '使徒行傳', title_orig: 'Acts', link: '/scripture' },
            ],
          },
          {
            key: 'catholic-1', label: '第一大公書信', label_en: 'First Catholic Epistles', desc: '初代核心使徒的普世教導，東正教傳統置於保羅之前（7 卷）。',
            works: [
              { title_zh: '雅各書', title_orig: 'James', link: '/scripture' },
              { title_zh: '彼得前書', title_orig: '1 Peter', link: '/scripture' },
              { title_zh: '彼得後書', title_orig: '2 Peter', link: '/scripture' },
              { title_zh: '約翰一書', title_orig: '1 John', link: '/scripture' },
              { title_zh: '約翰二書', title_orig: '2 John', link: '/scripture' },
              { title_zh: '約翰三書', title_orig: '3 John', link: '/scripture' },
              { title_zh: '猶大書', title_orig: 'Jude', link: '/scripture' },
            ],
          },
          {
            key: 'pauline', label: '保羅書信', label_en: 'Pauline Epistles', desc: '外邦人使徒向各地教會的系統神學與糾正（10 卷）。',
            works: [
              { title_zh: '羅馬書', title_orig: 'Romans', link: '/scripture' },
              { title_zh: '哥林多前書', title_orig: '1 Corinthians', link: '/scripture' },
              { title_zh: '哥林多後書', title_orig: '2 Corinthians', link: '/scripture' },
              { title_zh: '哥林多三書', tier: 'eastern', title_orig: '3 Corinthians', note: '亞美尼亞反異端傳統', link: '/apocrypha' },
              { title_zh: '加拉太書', title_orig: 'Galatians', link: '/scripture' },
              { title_zh: '以弗所書', title_orig: 'Ephesians', link: '/scripture' },
              { title_zh: '腓立比書', title_orig: 'Philippians', link: '/scripture' },
              { title_zh: '歌羅西書', title_orig: 'Colossians', link: '/scripture' },
              { title_zh: '帖撒羅尼迦前書', title_orig: '1 Thessalonians', link: '/scripture' },
              { title_zh: '帖撒羅尼迦後書', title_orig: '2 Thessalonians', link: '/scripture' },
            ],
          },
          {
            key: 'pastoral', label: '教牧書信', label_en: 'Pastoral Epistles', desc: '對教會領袖的個人指導與信仰傳承（4 卷）。',
            works: [
              { title_zh: '提摩太前書', title_orig: '1 Timothy', link: '/scripture' },
              { title_zh: '提摩太後書', title_orig: '2 Timothy', link: '/scripture' },
              { title_zh: '提多書', title_orig: 'Titus', link: '/scripture' },
              { title_zh: '腓利門書', title_orig: 'Philemon', link: '/scripture' },
            ],
          },
          {
            key: 'catholic-2', label: '第二大公書信', label_en: 'Second Catholic Epistles', desc: '希伯來書與廣泛流傳的亞使徒時代次經書信（4 卷）。',
            works: [
              { title_zh: '希伯來書', title_orig: 'Hebrews', note: '大祭司神學的總結', link: '/scripture' },
              { title_zh: '巴拿巴書', tier: 'patristic', title_orig: 'Epistle of Barnabas', note: '寓意解經；西乃抄本收錄', link: '/apocrypha' },
              { title_zh: '克勉書', tier: 'patristic', title_orig: '1 Clement', note: '羅馬主教的平亂與教誨；亞歷山大抄本收錄', link: '/apocrypha' },
              { title_zh: '黑馬牧人書', tier: 'patristic', title_orig: 'Shepherd of Hermas', note: '先知性的牧養與悔改；西乃抄本收錄', link: '/apocrypha' },
            ],
          },
          {
            key: 'apocalypse', label: '啟示錄', label_en: 'Apocalypse', desc: '末世異象與宇宙奧祕揭示（3 卷）。',
            works: [
              { title_zh: '約翰啟示錄', title_orig: 'Revelation to John', link: '/scripture' },
              { title_zh: '彼得啟示錄', tier: 'patristic', title_orig: 'Apocalypse of Peter', note: '天堂與地獄異象；穆拉多利殘篇收錄', link: '/apocrypha' },
              { title_zh: '克勉啟示錄', tier: 'eastern', title_orig: 'Apocalypse of Clement', note: '衣索比亞天啟（阿拉伯語彼得啟示錄）' },
            ],
          },
        ],
      },
      wai: {
        summary: '與正藏 92 卷分類對照的「影子聖經」：未進正藏的偽典、諾斯底經卷、重述聖經與啟示文獻——凡未達「尼西亞教會使用＋兩位教父＋古抄本」門檻者盡收於此（對齊討論記錄的 85 卷外典經藏）。各部按文獻所述時代排序（舊約按託名先祖／先知時代、新約按使徒順序：基督→雅各、主弟猶大→十二使徒→巴拿巴→保羅→福傳者腓力等非使徒）；正藏所無者另設「史傳」「遺訓」「使徒密訓與神論」三部。',
        divisions: [
          {
            key: 'law', label: '律法書', label_en: 'Law', desc: '託名摩西傳統的律法擴充與重寫。',
            works: [
              { title_zh: '創世記外傳', title_orig: 'Genesis Apocryphon', era: '前 1 世紀', note: '亞蘭文重寫創世記', link: '/apocrypha' },
              { title_zh: '聖殿卷', title_orig: 'Temple Scroll (11QT)', era: '前 2 世紀', note: '死海社群的律法擴充', link: '/apocrypha' },
              { title_zh: '古訓法度殘篇（四篇）', title_orig: 'Apocryphal Laws Fragments I–IV', note: '摩西五經的另類律法與契約擴充殘篇' },
            ],
          },
          {
            key: 'history', label: '歷史書', label_en: 'Histories', desc: '假借歷史之名對古以色列的另類重寫與別傳。',
            works: [
              { title_zh: '偽斐洛《聖經古史》', title_orig: 'Pseudo-Philo, Liber Antiquitatum Biblicarum', era: '1 世紀', note: '亞當至大衛的另類以色列史' },
              { title_zh: '利甲族傳', title_orig: 'History of the Rechabites', note: '曠野純潔隱士的神祕歷史' },
              { title_zh: '約瑟史傳', title_orig: 'History of Joseph', era: '約瑟', note: '擴寫約瑟在埃及的宮廷統治史' },
              { title_zh: '以西結悲劇辭', title_orig: 'Ezekiel the Tragedian', note: '用古希臘悲劇劇本改寫的《出埃及記》' },
              { title_zh: '亞里斯體亞書信', title_orig: 'Letter of Aristeas', era: '前 2 世紀', note: '七十士譯本起源傳說' },
              { title_zh: '雅尼與楊布雷', title_orig: 'Jannes and Jambres', note: '與摩西鬥法的兩位埃及術士下場' },
            ],
          },
          {
            key: 'legend', label: '史傳', label_en: 'Legends', desc: '正藏所無——託名古人的傳奇敘事，按人物時代排序。',
            works: [
              { title_zh: '亞當與夏娃生平', title_orig: 'Life of Adam and Eve', era: '亞當', note: '被逐出伊甸園後的懊悔生活', link: '/apocrypha' },
              { title_zh: '巨怪傳', title_orig: 'Book of Giants', era: '洪水前', note: '死海古卷中墮落天使與巨人神話', link: '/apocrypha' },
              { title_zh: '麥基洗德別傳', title_orig: 'Melchizedek Tractate', era: '亞伯拉罕時代', note: '將麥基洗德描繪為末日審判天使' },
              { title_zh: '約瑟與亞西納', title_orig: 'Joseph and Aseneth', era: '約瑟', note: '埃及祭司之女改宗嫁約瑟的浪漫小說' },
              { title_zh: '雅煞珥史記', title_orig: 'Book of Jasher', note: '失落的古以色列英雄戰紀' },
              { title_zh: '亞希夸書', title_orig: 'Story of Ahiqar', era: '亞述（前 7 世紀）', note: '古代近東宮廷智慧傳奇' },
              { title_zh: '先知傳', title_orig: 'Lives of the Prophets', era: '列代先知', note: '眾先知行誼與葬地' },
            ],
          },
          {
            key: 'testament', label: '遺訓', label_en: 'Testaments', desc: '正藏所無——託名先祖的臨終遺言，按先祖時代排序。',
            works: [
              { title_zh: '亞當遺訓', title_orig: 'Testament of Adam', era: '亞當' },
              { title_zh: '亞伯拉罕遺訓', title_orig: 'Testament of Abraham', era: '亞伯拉罕', link: '/apocrypha' },
              { title_zh: '以撒遺訓‧雅各遺訓', title_orig: 'Testaments of Isaac & Jacob', era: '以撒、雅各' },
              { title_zh: '約伯遺訓', title_orig: 'Testament of Job', era: '約伯', link: '/apocrypha' },
              { title_zh: '十二族長遺訓', title_orig: 'Testaments of the Twelve Patriarchs', era: '雅各十二子', link: '/apocrypha' },
              { title_zh: '摩西遺訓（升天記）', title_orig: 'Testament/Assumption of Moses', era: '摩西', link: '/apocrypha' },
              { title_zh: '所羅門遺訓', title_orig: 'Testament of Solomon', era: '所羅門', note: '以神戒驅使惡魔建聖殿的驅魔傳統' },
            ],
          },
          {
            key: 'wisdom', label: '詩歌智慧書', label_en: 'Poetry & Wisdom', desc: '未入正典的會堂非官方智慧與個人頌讚。',
            works: [
              { title_zh: '雅各禱辭', title_orig: 'Prayer of Jacob', era: '雅各' },
              { title_zh: '約瑟禱辭', title_orig: 'Prayer of Joseph', era: '約瑟' },
              { title_zh: '敘利亞詩篇（第 152–155 篇）', title_orig: 'Syriac Psalms 152–155', era: '大衛傳統' },
              { title_zh: '所羅門頌歌', title_orig: 'Odes of Solomon', era: '2 世紀', note: '早期神祕主義混合聖詩集' },
              { title_zh: '偽福西里德智訓', title_orig: 'Pseudo-Phocylides', note: '假借希臘詩人之名的猶太勸世文' },
              { title_zh: '敘利亞米南德箴言', title_orig: 'Sentences of Syriac Menander' },
              { title_zh: '銅卷藏寶錄', title_orig: 'Copper Scroll (3Q15)', note: '記載聖殿財寶藏地的非典型死海文獻', link: '/apocrypha' },
            ],
          },
          {
            key: 'minor-prophets', label: '十二先知書', label_en: 'Twelve Prophets',
            works: [
              { title_zh: '伊勒達與米達預言書', title_orig: 'Letter of Eldad and Modad', note: '民數記十一章二先知的失佚預言' },
            ],
          },
          {
            key: 'major-prophets', label: '大先知書', label_en: 'Major Prophets',
            works: [
              { title_zh: '耶利米餘事（巴錄四書）', title_orig: '4 Baruch / Paraleipomena Jeremiou', era: '耶利米（前 6 世紀）', link: '/apocrypha' },
              { title_zh: '巴錄續篇信札', title_orig: 'Epistle of Baruch', era: '巴錄' },
            ],
          },
          {
            key: 'apocalyptic-prophets', label: '天啟先知書', label_en: 'Apocalyptic Prophets', desc: '舊約天啟偽典——按託名先知的時代排序。',
            works: [
              { title_zh: '亞當啟示錄', title_orig: 'Apocalypse of Adam', era: '亞當', note: '拿戈瑪第塞特派天啟', link: '/gnostic' },
              { title_zh: '以諾二書（斯拉夫以諾）', title_orig: '2 Enoch', era: '以諾', note: '詳述七層天構造', link: '/apocrypha' },
              { title_zh: '以諾三書（希伯來以諾）', title_orig: '3 Enoch', era: '以諾', note: '以諾化身梅丹佐天使長', link: '/apocrypha' },
              { title_zh: '閃之異象錄', title_orig: 'Treatise of Shem', era: '閃（挪亞之子）', note: '結合十二星座的占星天啟' },
              { title_zh: '亞伯拉罕啟示錄', title_orig: 'Apocalypse of Abraham', era: '亞伯拉罕', link: '/apocrypha' },
              { title_zh: '以利亞啟示錄', title_orig: 'Apocalypse of Elijah', era: '以利亞（前 9 世紀）', link: '/apocrypha' },
              { title_zh: '以賽亞殉道與升天記', title_orig: 'Martyrdom and Ascension of Isaiah', era: '以賽亞（前 8 世紀）', link: '/apocrypha' },
              { title_zh: '西番雅啟示錄', title_orig: 'Apocalypse of Zephaniah', era: '西番雅（前 7 世紀）', link: '/apocrypha' },
              { title_zh: '巴錄三書（希臘巴錄啟示錄）', title_orig: '3 Baruch', era: '巴錄（前 6 世紀）', link: '/apocrypha' },
              { title_zh: '希臘以斯拉啟示錄', title_orig: 'Greek Apocalypse of Ezra', era: '以斯拉（前 5 世紀）', link: '/apocrypha' },
              { title_zh: '以斯拉異象書', title_orig: 'Vision of Ezra', era: '以斯拉', link: '/apocrypha' },
              { title_zh: '沙得拉啟示錄', title_orig: 'Apocalypse of Sedrach', era: '託名以斯拉', note: '與上帝爭辯人類犯罪的神義論異象' },
              { title_zh: '西比拉神諭', title_orig: 'Sibylline Oracles', era: '貫穿歷史', note: '借羅馬女祭司之口的末日預言詩', link: '/apocrypha' },
            ],
          },
          {
            key: 'gospels', label: '福音書', label_en: 'Gospels', desc: '按所述時代——童年福音在前，續以言行、受難、復活後對話。',
            works: [
              { title_zh: '雅各原始福音（雅各童年福音）', title_orig: 'Protoevangelium / Infancy Gospel of James', era: '聖誕前後', note: '瑪利亞身世與耶穌誕生', link: '/apocrypha' },
              { title_zh: '多馬童年福音', title_orig: 'Infancy Gospel of Thomas', era: '童年', note: '少年耶穌展示神力的故事', link: '/apocrypha' },
              { title_zh: '偽馬太童年福音', title_orig: 'Gospel of Pseudo-Matthew', era: '童年' },
              { title_zh: '阿拉伯童年福音', title_orig: 'Arabic Infancy Gospel', era: '童年' },
              { title_zh: '希伯來人福音', title_orig: 'Gospel of the Hebrews', era: '傳道', link: '/apocrypha' },
              { title_zh: '拿撒勒人福音', title_orig: 'Gospel of the Nazoreans', era: '傳道' },
              { title_zh: '伊便尼派福音', title_orig: 'Gospel of the Ebionites', era: '傳道', note: '早期素食教派專用' },
              { title_zh: '埃及人福音', title_orig: 'Gospel of the Egyptians', era: '傳道', link: '/gnostic' },
              { title_zh: '多馬密傳福音', title_orig: 'Gospel of Thomas', era: '語錄', note: '114 條耶穌隱密語錄', link: '/gnostic' },
              { title_zh: '腓力福音', title_orig: 'Gospel of Philip', era: '教導', note: '探討「新娘房」聖事', link: '/gnostic' },
              { title_zh: '真理福音', title_orig: 'Gospel of Truth', era: '教導', note: '華倫泰派神學講章', link: '/gnostic' },
              { title_zh: '彼得福音', title_orig: 'Gospel of Peter', era: '受難', note: '會說話的十字架受難奇譚', link: '/apocrypha' },
              { title_zh: '猶大密傳福音', title_orig: 'Gospel of Judas', era: '受難前夕', note: '宣稱猶大是唯一懂耶穌的門徒', link: '/gnostic' },
              { title_zh: '尼哥底母福音（彼拉多行傳）', title_orig: 'Gospel of Nicodemus', era: '受難與下陰府', note: '耶穌下陰間拯救先祖', link: '/apocrypha' },
              { title_zh: '馬利亞密傳福音', title_orig: 'Gospel of Mary', era: '復活後', note: '凸顯抹大拉馬利亞的使徒領袖地位', link: '/gnostic' },
              { title_zh: '救主福音', title_orig: 'Gospel of the Savior', era: '復活後對話' },
            ],
          },
          {
            key: 'acts', label: '行傳', label_en: 'Acts', desc: '揉合希臘冒險小說與禁慾主義的使徒傳奇，按使徒順序排列。',
            works: [
              { title_zh: '彼得行傳', title_orig: 'Acts of Peter', era: '彼得', note: '與行邪術的西門鬥法、倒釘十字架', link: '/apocrypha' },
              { title_zh: '彼得與十二使徒行傳', title_orig: 'Acts of Peter and the Twelve', era: '彼得與十二使徒', link: '/gnostic' },
              { title_zh: '安得烈行傳', title_orig: 'Acts of Andrew', era: '安得烈', link: '/apocrypha' },
              { title_zh: '約翰行傳', title_orig: 'Acts of John', era: '約翰', note: '含幻影說與十字架起舞場景', link: '/apocrypha' },
              { title_zh: '多馬行傳', title_orig: 'Acts of Thomas', era: '多馬', note: '赴印度傳教；含〈珍珠之歌〉', link: '/apocrypha' },
              { title_zh: '達太行傳', title_orig: 'Acts of Thaddaeus', era: '達太（十二使徒）' },
              { title_zh: '腓力行傳', title_orig: 'Acts of Philip', era: '使徒腓力' },
              { title_zh: '巴拿巴行傳', title_orig: 'Acts of Barnabas', era: '巴拿巴' },
              { title_zh: '保羅與底克拉行傳', title_orig: 'Acts of Paul and Thecla', era: '保羅', note: '女傳道者受洗與馴獅傳奇', link: '/apocrypha' },
            ],
          },
          {
            key: 'catholic-1', label: '第一大公書信', label_en: 'First Catholic Epistles', desc: '按使徒順序：基督→雅各、主弟猶大→十二使徒。',
            works: [
              { title_zh: '基督與阿布加爾王往來書', title_orig: 'Letter of Christ and Abgar', era: '基督', note: '耶穌親筆回信給埃德薩國王' },
              { title_zh: '蘭圖盧斯書信', title_orig: 'Letter of Lentulus', era: '基督', note: '古代唯一詳述耶穌長相的偽造公文' },
              { title_zh: '使徒書信（宗徒總函）', title_orig: 'Epistula Apostolorum', era: '十一使徒（集體）', note: '披著書信外衣的復活基督啟示對話' },
              { title_zh: '彼得致雅各書', title_orig: 'Epistle of Peter to James', era: '彼得', note: '偽克勉文集前言' },
            ],
          },
          {
            key: 'pauline', label: '保羅書信', label_en: 'Pauline Epistles',
            works: [
              { title_zh: '致老底嘉人書', title_orig: 'Epistle to the Laodiceans', era: '保羅', link: '/apocrypha' },
              { title_zh: '保羅與塞內加往來書信', title_orig: 'Correspondence of Paul and Seneca', era: '保羅', note: '試圖連結保羅與斯多葛哲學' },
            ],
          },
          {
            key: 'pastoral', label: '教牧書信', label_en: 'Pastoral Epistles',
            works: [
              { title_zh: '偽提多書', title_orig: 'Pseudo-Titus Epistle', era: '提多', note: '論貞潔的勸誡書' },
            ],
          },
          {
            key: 'catholic-2', label: '第二大公書信', label_en: 'Second Catholic Epistles', desc: '教父推薦但未入正藏的非使徒書信。',
            works: [
              { title_zh: '克勉二書', title_orig: '2 Clement', era: '克勉（羅馬）', note: '古代最早的講道辭，教父推薦不足', link: '/apocrypha' },
              { title_zh: '偽克勉致雅各書', title_orig: 'Pseudo-Clementine Epistles', era: '克勉（羅馬）' },
              { title_zh: '克勉論童貞二書', title_orig: 'Two Epistles on Virginity', era: '克勉（羅馬）' },
            ],
          },
          {
            key: 'apocalypse', label: '啟示錄', label_en: 'Apocalypse', desc: '新約天啟偽典——按使徒順序排列。',
            works: [
              { title_zh: '雅各啟示錄上卷', title_orig: 'First Apocalypse of James', era: '主的兄弟雅各', link: '/gnostic' },
              { title_zh: '雅各啟示錄下卷', title_orig: 'Second Apocalypse of James', era: '主的兄弟雅各', link: '/gnostic' },
              { title_zh: '科普特彼得啟示錄', title_orig: 'Coptic Apocalypse of Peter', era: '彼得', link: '/gnostic' },
              { title_zh: '神學家約翰啟示錄外傳', title_orig: 'Apocryphal Apocalypse of John', era: '約翰' },
              { title_zh: '保羅啟示錄', title_orig: 'Apocalypse of Paul (Visio Pauli)', era: '保羅', note: '靈魂秤重與地獄酷刑，影響但丁《神曲》', link: '/apocrypha' },
              { title_zh: '科普特保羅啟示錄', title_orig: 'Coptic Apocalypse of Paul', era: '保羅', link: '/gnostic' },
              { title_zh: '多馬啟示錄', title_orig: 'Apocalypse of Thomas', era: '多馬', note: '末日降臨前七天的宇宙異象' },
              { title_zh: '司提反啟示錄', title_orig: 'Apocalypse of Stephen', era: '司提反（非使徒）' },
            ],
          },
          {
            key: 'gnostic-treatise', label: '使徒密訓與神論', label_en: 'Gnostic Treatises', desc: '正藏所無——拿戈瑪第出土、披著使徒外衣的諾斯底宇宙論與神學。',
            works: [
              { title_zh: '約翰密傳', title_orig: 'Apocryphon of John', note: '諾斯底神話百科，詳解造物主的墮落', link: '/gnostic' },
              { title_zh: '執政官本源論', title_orig: 'Hypostasis of the Archons', note: '顛覆創世記，舊約神為瞎眼邪神', link: '/gnostic' },
              { title_zh: '創世起源論', title_orig: 'On the Origin of the World', link: '/gnostic' },
              { title_zh: '三形初思錄', title_orig: 'Trimorphic Protennoia', note: '神聖女性智慧流出神話', link: '/gnostic' },
              { title_zh: '耶穌智言', title_orig: 'Sophia of Jesus Christ', link: '/gnostic' },
              { title_zh: '救主對話錄', title_orig: 'Dialogue of the Savior', link: '/gnostic' },
              { title_zh: '靈魂釋義論', title_orig: 'Exegesis on the Soul', link: '/gnostic' },
              { title_zh: '雷：完美理智辭', title_orig: 'The Thunder, Perfect Mind', note: '女性神格第一人稱矛盾詩', link: '/gnostic' },
              { title_zh: '畢斯提斯‧索菲亞', title_orig: 'Pistis Sophia', note: '龐大的諾斯底悔改詩歌與咒語集', link: '/gnostic' },
            ],
          },
        ],
      },
    },
        // ═══════════════════════════════════════════════════════ 2. 律藏
    {
      key: 'lu',
      name: '律藏',
      name_en: 'Canons & Ecclesiastical Law',
      glyph: '律',
      genres: '信經‧教令‧教規‧會規',
      summary: '教會運作的骨架。正藏為大公會議信經教令、使徒教規與教會憲典、使徒法典（由經藏移入的教會秩序書）與修道規則；外藏為異端與分裂派的教規，以及 400 年前的猶太律法。',
      portal: { to: '/creeds', label: '信條與大公會議' },
      zheng: {
        divisions: [
          {
            key: 'councils', label: '大公會議部', label_en: 'Ecumenical & Local Councils',
            works: [
              { title_zh: '前七次大公會議信經與教令', title_orig: 'Seven Ecumenical Councils (325–787)', note: '尼西亞 325 至第二次尼西亞 787', link: '/creeds' },
              { title_zh: '地方會議教令', title_orig: 'Local Synods', note: '安提阿‧迦太基‧老底嘉‧艾爾維拉‧特路羅 692', link: '/canon-law' },
            ],
          },
          {
            key: 'apostolic-canons', label: '教令與教規部', label_en: 'Apostolic Canons',
            works: [
              { title_zh: '使徒教規（八十五條）', title_orig: 'Apostolic Canons', link: '/canon-law' },
              { title_zh: '使徒憲典', title_orig: 'Apostolic Constitutions', era: '4 世紀' },
              { title_zh: '希波律陀《使徒傳統》', title_orig: 'Hippolytus, Apostolic Tradition', era: '3 世紀' },
              { title_zh: '查士丁尼／狄奧多西法典（宗教部分）', title_orig: 'Codex Justinianus / Theodosianus', era: '5–6 世紀' },
            ],
          },
          {
            key: 'apostolic-order', label: '使徒法典部', label_en: 'Church Orders', desc: '由經藏壓軸移入——性質為法規的教會秩序書。',
            works: [
              { title_zh: '十二使徒遺訓', title_orig: 'Didache', era: '1–2 世紀', link: '/apocrypha' },
              { title_zh: '使徒教訓', title_orig: 'Didascalia Apostolorum', note: '原譯宗徒規範' },
              { title_zh: '衣索比亞教會秩序六典', title_orig: 'Sirate Tsion / Tizaz / Gitsew / Abtilis / Covenant I–II', note: '秩序典‧訓令典‧戒律典‧規章典‧聖約前後典' },
            ],
          },
          {
            key: 'monastic', label: '修道規則部', label_en: 'Monastic Rules',
            works: [
              { title_zh: '帕科繆規章', title_orig: 'Rule of Pachomius', era: '4 世紀' },
              { title_zh: '大巴西流規章', title_orig: 'Basil, Asketikon', era: '4 世紀' },
              { title_zh: '聖本篤會規', title_orig: 'Rule of St. Benedict', era: '6 世紀' },
              { title_zh: '該撒留會規', title_orig: 'Rule of Caesarius', era: '6 世紀' },
            ],
          },
        ],
      },
      wai: {
        divisions: [
          {
            key: 'heretic-councils', label: '異端與分裂派教規部', label_en: 'Heretical Synods',
            works: [
              { title_zh: '亞流派與聶斯多留派會議文件', title_orig: 'Arian & Nestorian Synods' },
              { title_zh: '以弗所強盜會議', title_orig: 'Latrocinium of Ephesus', era: '449', note: '被迦克墩否定的會議' },
              { title_zh: '孟他努派教規', title_orig: 'Montanist Canons' },
            ],
          },
          {
            key: 'jewish-law', label: '猶太律部', label_en: 'Jewish Law (to 400 CE)',
            works: [
              { title_zh: '米書拿', title_orig: 'Mishnah', era: '約 200', note: '口傳律法核心' },
              { title_zh: '陀塞他', title_orig: 'Tosefta', era: '約 300' },
              { title_zh: '耶路撒冷塔木德（早期地層）', title_orig: 'Jerusalem Talmud', era: '約 350–400' },
            ],
          },
        ],
      },
    },
    // ═══════════════════════════════════════════════════════ 3. 論藏
    {
      key: 'lun',
      name: '論藏',
      name_en: 'Treatises & Exegesis',
      glyph: '論',
      genres: '論‧辯（護教詞）‧駁‧註‧疏‧釋',
      summary: '教父用血淚與智慧為信仰披上的「重裝鎧甲」。正藏為正統的護教、反異端、系統教義、釋經與神祕主義；外藏為作為「對手與底色」的異端論述、猶太哲學與外教批判。',
      portal: { to: '/fathers', label: '教父著作' },
      zheng: {
        divisions: [
          {
            key: 'apologia', label: '護教詞部', label_en: 'Apologetics',
            works: [
              { title_zh: '游斯丁《第一、第二護教詞》《駁特里風護教詞》', title_orig: 'Justin Martyr', era: '2 世紀', link: '/fathers' },
              { title_zh: '特土良《護教辯》', title_orig: 'Tertullian, Apologeticus', link: '/fathers' },
              { title_zh: '致丟格那妥書‧亞他那哥拉《請願》‧提阿非羅《致奧托呂古》', title_orig: 'Diognetus / Athenagoras / Theophilus', link: '/apocrypha' },
              { title_zh: '拉克坦提烏《神聖原理》‧亞挪比烏《駁異教》', title_orig: 'Lactantius / Arnobius', link: '/fathers' },
              { title_zh: '奧古斯丁《上帝之城》', title_orig: 'Augustine, De Civitate Dei', era: '5 世紀', link: '/fathers' },
            ],
          },
          {
            key: 'adversus', label: '反異端部', label_en: 'Against Heresies',
            works: [
              { title_zh: '愛任紐《駁異端論》', title_orig: 'Irenaeus, Adversus Haereses', link: '/fathers' },
              { title_zh: '特土良《規誡異端》《駁馬吉安》《駁普拉克西亞》', title_orig: 'Tertullian', link: '/fathers' },
              { title_zh: '希波律陀《駁諸異端》', title_orig: 'Hippolytus, Refutatio', link: '/fathers' },
              { title_zh: '亞他那修《駁亞流辭》', title_orig: 'Athanasius, Contra Arianos', link: '/fathers' },
              { title_zh: '愛比法紐《破百異端駁（藥箱）》', title_orig: 'Epiphanius, Panarion', link: '/fathers' },
            ],
          },
          {
            key: 'dogmatics', label: '系統與教義部', label_en: 'Systematic Dogmatics',
            works: [
              { title_zh: '俄利根《基要原理論》', title_orig: 'Origen, De Principiis', note: '史上第一部系統神學', link: '/fathers' },
              { title_zh: '亞他那修《論道成肉身》', title_orig: 'Athanasius, De Incarnatione', link: '/fathers' },
              { title_zh: '巴西流《論聖靈》‧尼撒貴格利《大要理問答》', title_orig: 'Basil / Gregory of Nyssa', link: '/fathers' },
              { title_zh: '奧古斯丁《論三位一體》《信望愛手冊》', title_orig: 'Augustine, De Trinitate / Enchiridion', link: '/fathers' },
              { title_zh: '大馬士革約翰《正統信仰闡述》', title_orig: 'John of Damascus, De Fide Orthodoxa', era: '8 世紀', link: '/fathers' },
            ],
          },
          {
            key: 'exegesis', label: '釋經與釋祕部', label_en: 'Exegesis',
            works: [
              { title_zh: '俄利根《雅歌疏》《約翰福音註》', title_orig: 'Origen, Commentaries', link: '/fathers' },
              { title_zh: '屈梭多模《創世記／馬太／約翰講疏》', title_orig: 'Chrysostom, Homilies', link: '/fathers' },
              { title_zh: '奧古斯丁《創世記字義解》《詩篇詮釋》', title_orig: 'Augustine, Commentaries', link: '/fathers' },
              { title_zh: '耶柔米聖經註釋全集', title_orig: 'Jerome, Commentaries', link: '/fathers' },
            ],
          },
          {
            key: 'mystical', label: '神祕主義部', label_en: 'Mystical Theology',
            works: [
              { title_zh: '偽丟尼修《天階序列》《神祕神學》', title_orig: 'Pseudo-Dionysius', link: '/fathers' },
              { title_zh: '階梯約翰《神聖攀登天階》', title_orig: 'John Climacus, The Ladder', link: '/fathers' },
              { title_zh: '馬克西母《愛德四百則》《論神化》', title_orig: 'Maximus the Confessor', link: '/fathers' },
              { title_zh: '尼尼微的以撒《靈修講道》', title_orig: 'Isaac of Nineveh', era: '7 世紀' },
            ],
          },
        ],
      },
      wai: {
        divisions: [
          {
            key: 'heretic', label: '異端論述部', label_en: 'Heterodox Treatises',
            works: [
              { title_zh: '諾斯底論述（瓦倫廷派／塞特派）', title_orig: 'Valentinian & Sethian Gnosis', link: '/gnostic' },
              { title_zh: '摩尼教文獻', title_orig: 'Manichaean Texts', note: '科普特科里斯文書‧《摩尼光佛教法儀略》' },
              { title_zh: '亞流《晚宴》殘篇', title_orig: 'Arius, Thalia (fragments)' },
              { title_zh: '聶斯多留《赫拉克利德斯之書》', title_orig: 'Nestorius, Bazaar of Heracleides' },
              { title_zh: '伯拉糾論述殘篇', title_orig: 'Pelagius (fragments)' },
            ],
          },
          {
            key: 'jewish-philo', label: '猶太哲學部', label_en: 'Jewish Philosophy',
            works: [
              { title_zh: '斐洛全集', title_orig: 'Philo of Alexandria', era: '1 世紀', note: '教父神學術語的「原始碼」' },
              { title_zh: '猶太教法理疏（早期拉比釋經）', title_orig: 'Early Rabbinic Exegesis' },
            ],
          },
          {
            key: 'pagan-critique', label: '外教批判部', label_en: 'Pagan Critiques',
            works: [
              { title_zh: '塞爾蘇斯《真道》', title_orig: 'Celsus, On the True Doctrine', note: '經俄利根《駁瑟蘇斯》保存' },
              { title_zh: '波菲利《駁基督徒》殘篇', title_orig: 'Porphyry, Against the Christians' },
              { title_zh: '皇帝尤利安《駁加利利人》', title_orig: 'Julian, Against the Galileans' },
            ],
          },
        ],
      },
    },
    // ═══════════════════════════════════════════════════════ 4. 史傳藏
    {
      key: 'shizhuan',
      name: '史傳藏',
      name_en: 'History & Hagiography',
      glyph: '史',
      genres: '紀（史）‧傳‧世家（宗統）‧表（編年）‧志',
      summary: '基督宗教的真實人間史。正藏為教會通史、聖徒本傳、宗統記、編年表與典志；外藏為猶太背景史料、外教見證選（Testimonia）與帶奇幻情節的偽史傳。',
      portal: { to: '/fathers', label: '教父著作' },
      zheng: {
        divisions: [
          {
            key: 'general-history', label: '通史部（史）', label_en: 'General Histories',
            works: [
              { title_zh: '優西比烏《教會史》', title_orig: 'Eusebius, Ecclesiastical History', link: '/fathers' },
              { title_zh: '蘇格拉底／索佐門／提阿多勒《教會史》', title_orig: 'Socrates / Sozomen / Theodoret', link: '/fathers' },
              { title_zh: '比德《英吉利教會史》', title_orig: 'Bede, Historia Ecclesiastica', era: '731' },
              { title_zh: '都爾的貴格利《法蘭克人史》', title_orig: 'Gregory of Tours' },
            ],
          },
          {
            key: 'lives', label: '本傳與殉道錄部（傳）', label_en: 'Saints & Martyrs',
            works: [
              { title_zh: '亞他那修《安東尼傳》', title_orig: 'Athanasius, Life of Antony', link: '/fathers' },
              { title_zh: '波西丟《奧古斯丁傳》‧耶柔米隱士傳', title_orig: 'Possidius / Jerome, Lives', link: '/fathers' },
              { title_zh: '《波利卡普殉道記》《佩珮圖亞殉道記》', title_orig: 'Martyrdom accounts', link: '/apocrypha' },
              { title_zh: '帕拉迪烏《樂園（隱修史）》', title_orig: 'Palladius, Lausiac History' },
            ],
          },
          {
            key: 'succession', label: '宗統記部（世家）', label_en: 'Episcopal Succession',
            works: [
              { title_zh: '《教宗世家記》', title_orig: 'Liber Pontificalis' },
            ],
          },
          {
            key: 'chronicle', label: '編年表部（表）', label_en: 'Chronicles',
            works: [
              { title_zh: '優西比烏—耶柔米《編年史》', title_orig: 'Eusebius–Jerome, Chronicon' },
              { title_zh: '《復活節編年史》', title_orig: 'Chronicon Paschale' },
            ],
          },
          {
            key: 'topography', label: '典志部（志）', label_en: 'Pilgrimage & Topography',
            works: [
              { title_zh: '《埃格里亞朝聖記》《波爾多朝聖者行記》', title_orig: 'Egeria / Itinerarium Burdigalense', era: '4 世紀' },
            ],
          },
        ],
      },
      wai: {
        divisions: [
          {
            key: 'jewish-history', label: '猶太背景史料部', label_en: 'Jewish Background (to 400)',
            works: [
              { title_zh: '約瑟夫斯《猶太古史》《猶太戰記》《駁亞皮溫》', title_orig: 'Josephus', era: '1 世紀' },
              { title_zh: '巴爾科赫巴戰地手札', title_orig: 'Bar Kokhba Letters', era: '2 世紀' },
            ],
          },
          {
            key: 'pagan-testimonia', label: '外史志部（外教見證）', label_en: 'Pagan Testimonia',
            works: [
              { title_zh: '塔西佗《編年史》論尼祿焚城段', title_orig: 'Tacitus, Annals 15.44' },
              { title_zh: '蘇埃托尼烏斯《革老丟傳》「基斯督」段', title_orig: 'Suetonius, Claudius 25' },
              { title_zh: '琉善《佩雷格里努斯之死》', title_orig: 'Lucian, De Morte Peregrini' },
            ],
          },
        ],
      },
    },
    // ═══════════════════════════════════════════════════════ 5. 譯校藏
    {
      key: 'yijiao',
      name: '譯校藏',
      name_en: 'Translation & Textual Criticism',
      glyph: '譯',
      genres: '寶抄‧譯本‧校勘‧考異',
      summary: '人類傳遞啟示的「歷史肉身」。正藏為大公教會接受的古卷寶抄、多語大譯本與正統校勘；外藏為猶太修訂譯本與異端經本。',
      portal: { to: '/scripture', label: '聖經多版本對照' },
      zheng: {
        divisions: [
          {
            key: 'manuscripts', label: '古卷寶抄部', label_en: 'Great Codices',
            works: [
              { title_zh: '西乃抄本', title_orig: 'Codex Sinaiticus', era: '4 世紀' },
              { title_zh: '梵蒂岡抄本‧亞歷山大抄本', title_orig: 'Vaticanus / Alexandrinus' },
              { title_zh: '以法蓮重寫寶抄‧伯撒抄本', title_orig: 'Ephraemi Rescriptus / Bezae' },
            ],
          },
          {
            key: 'versions', label: '多語大譯本部', label_en: 'Multilingual Versions', desc: '止於 7 世紀大秦景教殘卷（不含 9 世紀斯拉夫文）。',
            works: [
              { title_zh: '七十士譯本', title_orig: 'Septuagint (LXX)', link: '/scripture' },
              { title_zh: '武加大拉丁譯本（耶柔米）', title_orig: 'Vulgate', link: '/scripture' },
              { title_zh: '古拉丁譯本', title_orig: 'Vetus Latina', link: '/scripture' },
              { title_zh: '別西大敘利亞譯本', title_orig: 'Peshitta', link: '/scripture' },
              { title_zh: '科普特譯本（撒希地／波海里）', title_orig: 'Coptic', link: '/scripture' },
              { title_zh: '哥德文／亞美尼亞文／喬治亞文／吉茲文譯本', title_orig: 'Gothic / Armenian / Georgian / Geʿez', link: '/scripture' },
              { title_zh: '大秦景教殘卷', title_orig: 'Jingjiao Chinese Fragments', era: '7–8 世紀' },
            ],
          },
          {
            key: 'critical', label: '校勘考異部', label_en: 'Textual Criticism',
            works: [
              { title_zh: '俄利根《六文本合參》', title_orig: 'Origen, Hexapla' },
              { title_zh: '耶柔米《武加大序言》', title_orig: 'Jerome, Prefaces', note: '「希伯來真理」翻譯理論' },
            ],
          },
        ],
      },
      wai: {
        divisions: [
          {
            key: 'jewish-versions', label: '猶太修訂譯本部', label_en: 'Jewish Recensions',
            works: [
              { title_zh: '亞居拉／辛馬庫／狄奧多田譯本', title_orig: 'Aquila / Symmachus / Theodotion', era: '2 世紀' },
              { title_zh: '塔古姆（翁克羅斯／約拿單）', title_orig: 'Targum Onkelos / Jonathan' },
            ],
          },
          {
            key: 'heretic-versions', label: '異端經本部', label_en: 'Heretical Recensions',
            works: [
              { title_zh: '馬吉安經典（刪節版路加與保羅書信）', title_orig: 'Marcionite Apostolikon & Evangelion' },
              { title_zh: '摩尼教經卷', title_orig: 'Manichaean Scriptures' },
            ],
          },
        ],
      },
    },
    // ═══════════════════════════════════════════════════════ 6. 書信藏
    {
      key: 'shuxin',
      name: '書信藏',
      name_en: 'Epistles',
      glyph: '信',
      genres: '函（牧函／教令）‧札（尺牘）',
      summary: '為冷峻的法典與神學大山注入真實的人間血肉。正藏為使徒教父牧函與教父書信集；外藏為偽使徒書信與外教公函。',
      portal: { to: '/fathers', label: '教父著作' },
      zheng: {
        divisions: [
          {
            key: 'apostolic-letters', label: '使徒教父牧函部（函）', label_en: 'Apostolic Fathers',
            works: [
              { title_zh: '伊格那丟七書', title_orig: 'Ignatius, Seven Epistles', era: '2 世紀', link: '/apocrypha' },
              { title_zh: '波利卡普《致腓立比人書》', title_orig: 'Polycarp', link: '/apocrypha' },
            ],
          },
          {
            key: 'father-letters', label: '教父書信集部', label_en: 'Patristic Letters',
            works: [
              { title_zh: '居普良書信集', title_orig: 'Cyprian, Letters', link: '/fathers' },
              { title_zh: '巴西流／納西盎貴格利書信', title_orig: 'Basil / Gregory Nazianzen', link: '/fathers' },
              { title_zh: '安波羅修／耶柔米／奧古斯丁書信集', title_orig: 'Ambrose / Jerome / Augustine', link: '/fathers' },
              { title_zh: '利奧書信集‧大貴格利《登記書》', title_orig: 'Leo / Gregory the Great', link: '/encyclicals' },
            ],
          },
          {
            key: 'spiritual-letters', label: '神學交鋒與靈修尺牘部（札）', label_en: 'Theological & Spiritual Letters',
            works: [
              { title_zh: '奧古斯丁與耶柔米論戰信', title_orig: 'Augustine–Jerome Correspondence', link: '/fathers' },
              { title_zh: '沙漠父老巴撒努菲與約翰答問札', title_orig: 'Barsanuphius and John', era: '6 世紀' },
              { title_zh: '傑拉修《雙劍論》致阿納斯塔修', title_orig: 'Gelasius, Letter to Anastasius', link: '/encyclicals' },
            ],
          },
        ],
      },
      wai: {
        divisions: [
          {
            key: 'pseudo-letters', label: '偽使徒書信部', label_en: 'Pseudo-Apostolic Letters',
            works: [
              { title_zh: '老底嘉書‧哥林多三書', title_orig: 'Laodiceans / 3 Corinthians', link: '/apocrypha' },
              { title_zh: '保羅與塞內加書信', title_orig: 'Paul and Seneca' },
            ],
          },
          {
            key: 'pagan-letters', label: '外教公函部', label_en: 'Pagan Correspondence',
            works: [
              { title_zh: '小普林尼致圖拉真書（及回信）', title_orig: 'Pliny–Trajan', era: '約 112' },
            ],
          },
        ],
      },
    },
    // ═══════════════════════════════════════════════════════ 7. 禮儀藏
    {
      key: 'liyi',
      name: '禮儀藏',
      name_en: 'Liturgy',
      glyph: '儀',
      genres: '事奉聖禮‧聖事書‧日課‧祈禱',
      summary: '最具動態感與神聖感的空間。正藏為正統的事奉聖禮、聖事日課與奧祕教理；外藏為異端禮儀與 400 年前的猶太敬拜。',
      zheng: {
        divisions: [
          {
            key: 'eucharist', label: '聖禮事奉部', label_en: 'Eucharistic Liturgies',
            works: [
              { title_zh: '金口約翰／巴西流事奉聖禮', title_orig: 'Liturgy of Chrysostom / Basil' },
              { title_zh: '雅各／馬可事奉聖禮', title_orig: 'Liturgy of James / Mark' },
              { title_zh: '阿迪與馬利聖頌', title_orig: 'Anaphora of Addai and Mari', note: '東敘利亞最古老感恩經' },
              { title_zh: '羅馬彌撒正典', title_orig: 'Canon Romanus' },
            ],
          },
          {
            key: 'sacramentary', label: '聖事書與日課部', label_en: 'Sacramentaries & Hours',
            works: [
              { title_zh: '傑拉修／大貴格利聖事書', title_orig: 'Gelasian / Gregorian Sacramentary' },
              { title_zh: '拜占庭時辰經', title_orig: 'Horologion' },
            ],
          },
          {
            key: 'mystagogy', label: '奧祕教理與洗禮部', label_en: 'Mystagogy & Baptism',
            works: [
              { title_zh: '耶路撒冷區利羅《奧祕教理講授》', title_orig: 'Cyril of Jerusalem, Mystagogical Catecheses', link: '/fathers' },
            ],
          },
        ],
      },
      wai: {
        divisions: [
          {
            key: 'heretic-liturgy', label: '異端禮儀部', label_en: 'Heterodox Liturgies',
            works: [
              { title_zh: '諾斯底洗禮與新娘室禮儀', title_orig: 'Gnostic Baptism & Bridal Chamber', link: '/gnostic' },
              { title_zh: '馬可斯派聖餐儀軌', title_orig: 'Marcosian Eucharist' },
            ],
          },
          {
            key: 'jewish-liturgy', label: '猶太禮儀部', label_en: 'Jewish Liturgy (to 400)',
            works: [
              { title_zh: '安息日獻祭之歌（天使禮儀）‧感恩聖詩卷', title_orig: 'Songs of the Sabbath Sacrifice / Hodayot', link: '/apocrypha' },
              { title_zh: '希臘化會堂祈禱辭', title_orig: 'Hellenistic Synagogal Prayers' },
            ],
          },
        ],
      },
    },
    // ═══════════════════════════════════════════════════════ 8. 詩文藏
    {
      key: 'shiwen',
      name: '詩文藏',
      name_en: 'Poetry & Literature',
      glyph: '詩',
      genres: '聖詠‧讚歌‧哲理‧傳奇',
      summary: '最具美感、最能觸動靈魂的藝術聖殿。正藏為正統聖詠、哲理與敘事傳奇；外藏為諾斯底與摩尼教的讚歌。',
      zheng: {
        divisions: [
          {
            key: 'hymns', label: '聖詠讚美部', label_en: 'Hymns & Chants',
            works: [
              { title_zh: '以法蓮《讚美詩集／教導詩》', title_orig: 'Ephrem the Syrian, Hymns', era: '4 世紀' },
              { title_zh: '羅曼努斯《孔塔基昂讚歌》', title_orig: 'Romanos, Kontakia', era: '6 世紀' },
              { title_zh: '安波羅修聖詩‧普魯登修斯《殉道冠冕》', title_orig: 'Ambrosian Hymns / Prudentius', link: '/fathers' },
            ],
          },
          {
            key: 'philosophical', label: '哲理與自傳文學部', label_en: 'Philosophical & Autobiographical',
            works: [
              { title_zh: '波愛修斯《哲學的慰藉》', title_orig: 'Boethius, Consolation of Philosophy', link: '/fathers' },
              { title_zh: '奧古斯丁《懺悔錄》', title_orig: 'Augustine, Confessions', link: '/fathers' },
              { title_zh: '普魯登修斯《靈魂爭戰》', title_orig: 'Prudentius, Psychomachia' },
            ],
          },
          {
            key: 'romance', label: '敘事傳奇部', label_en: 'Christian Romance',
            works: [
              { title_zh: '《巴拉姆與約沙法傳奇》', title_orig: 'Barlaam and Josaphat', note: '釋迦牟尼生平的基督教化' },
              { title_zh: '《克勉遊記》', title_orig: 'Clementine Recognitions / Homilies' },
            ],
          },
        ],
      },
      wai: {
        divisions: [
          {
            key: 'gnostic-hymns', label: '諾斯底讚歌部', label_en: 'Gnostic Hymns',
            works: [
              { title_zh: '〈珍珠之歌〉', title_orig: 'Hymn of the Pearl', note: '《多馬行傳》中的靈魂寓言詩', link: '/apocrypha' },
              { title_zh: '〈三重普羅諾亞〉等諾斯底讚詩', title_orig: 'Trimorphic Protennoia etc.', link: '/gnostic' },
            ],
          },
          {
            key: 'manichaean-hymns', label: '摩尼教讚美詩部', label_en: 'Manichaean Psalms',
            works: [
              { title_zh: '科普特摩尼教讚美詩集', title_orig: 'Coptic Manichaean Psalm-Book' },
            ],
          },
        ],
      },
    },
    // ═══════════════════════════════════════════════════════ 9. 宣道藏
    {
      key: 'xuandao',
      name: '宣道藏',
      name_en: 'Sermons & Sayings',
      glyph: '宣',
      genres: '講‧疏‧語錄',
      summary: '唯一能聽到「群眾回音」的迴音壁。正藏為正統釋經講疏、節期講道與沙漠語錄；外藏為異端講道與 400 年前的拉比講疏（米德拉什）。',
      portal: { to: '/fathers', label: '教父著作' },
      zheng: {
        divisions: [
          {
            key: 'expository', label: '釋經講疏部', label_en: 'Expository Homilies',
            works: [
              { title_zh: '金口約翰《創世記／馬太／約翰福音講疏》《雕像講道》', title_orig: 'Chrysostom, Homilies', link: '/fathers' },
              { title_zh: '奧古斯丁《講道集》《約翰福音講解》', title_orig: 'Augustine, Sermones', link: '/fathers' },
              { title_zh: '俄利根講道集‧大貴格利《福音書講道》', title_orig: 'Origen / Gregory the Great', link: '/fathers' },
            ],
          },
          {
            key: 'festal', label: '節期與教理講道部', label_en: 'Festal & Catechetical',
            works: [
              { title_zh: '納西盎貴格利《神學演講》', title_orig: 'Gregory Nazianzen, Theological Orations', link: '/fathers' },
              { title_zh: '耶路撒冷區利羅《教理講授》', title_orig: 'Cyril of Jerusalem, Catechetical Lectures', link: '/fathers' },
            ],
          },
          {
            key: 'desert-sayings', label: '沙漠語錄部', label_en: 'Sayings of the Desert Fathers',
            works: [
              { title_zh: '《沙漠教父言行錄》', title_orig: 'Apophthegmata Patrum', era: '4–5 世紀' },
              { title_zh: '艾瓦格留《實踐論格言》', title_orig: 'Evagrius, Praktikos' },
            ],
          },
        ],
      },
      wai: {
        divisions: [
          {
            key: 'rabbinic-homily', label: '拉比講疏部', label_en: 'Rabbinic Midrash (to 400)',
            works: [
              { title_zh: '《創世記大注釋》《利未記大注釋》', title_orig: 'Genesis / Leviticus Rabbah' },
              { title_zh: '《米基塔》《西弗瑞》', title_orig: 'Mekhilta / Sifre' },
            ],
          },
          {
            key: 'heretic-homily', label: '異端講道部', label_en: 'Heterodox Homilies',
            works: [
              { title_zh: '諾斯底與摩尼教講道殘篇', title_orig: 'Gnostic & Manichaean Homilies' },
            ],
          },
        ],
      },
    },
    // ═══════════════════════════════════════════════════════ 10. 類書藏
    {
      key: 'leishu',
      name: '類書藏',
      name_en: 'Encyclopedic Reference',
      glyph: '類',
      genres: '類書‧法要‧工具‧曆算',
      summary: '修院認識世界的百科全書，每一種分類都指向造物主。正藏為基督教百科類書、修學法要、哲學工具與曆算自然；外藏為外教百科與占驗祕學。',
      zheng: {
        divisions: [
          {
            key: 'encyclopedia', label: '百科類書部', label_en: 'Encyclopedias',
            works: [
              { title_zh: '塞維亞的伊西多爾《詞源（百科志）》', title_orig: 'Isidore of Seville, Etymologiae', era: '7 世紀', note: '全書 20 卷的「中世紀維基百科」' },
            ],
          },
          {
            key: 'curriculum', label: '修學法要部', label_en: 'Educational Manuals',
            works: [
              { title_zh: '卡西奧多羅斯《聖俗文獻指南》', title_orig: 'Cassiodorus, Institutiones', era: '6 世紀' },
              { title_zh: '奧古斯丁《論基督教教義》', title_orig: 'Augustine, De Doctrina Christiana', link: '/fathers' },
              { title_zh: '馬爾蒂亞努斯《文獻學與墨丘利的聯姻》', title_orig: 'Martianus Capella, De Nuptiis' },
            ],
          },
          {
            key: 'philosophy-tools', label: '哲學工具部', label_en: 'Philosophical Tools',
            works: [
              { title_zh: '波愛修斯譯註《波菲利引論》', title_orig: 'Boethius, Porphyry Isagoge', note: '基督二性辯論的邏輯學武器' },
            ],
          },
          {
            key: 'computus', label: '曆算與自然部', label_en: 'Computus & Nature',
            works: [
              { title_zh: '比德《論時間計算》《論萬物本性》', title_orig: 'Bede, De Temporum Ratione', era: '8 世紀' },
              { title_zh: '科斯馬斯《基督教地形志》', title_orig: 'Cosmas, Christian Topography', era: '6 世紀' },
            ],
          },
        ],
      },
      wai: {
        divisions: [
          {
            key: 'pagan-encyclopedia', label: '外教百科部', label_en: 'Pagan Reference',
            works: [
              { title_zh: '老普林尼《博物志》（基督教摘要）', title_orig: 'Pliny the Elder, Natural History (excerpts)' },
            ],
          },
          {
            key: 'occult', label: '占驗祕學部', label_en: 'Occult & Magic',
            works: [
              { title_zh: '《所羅門遺訓》魔法傳統', title_orig: 'Testament of Solomon', note: '被基督教引用／駁斥的驅魔與占星傳統' },
            ],
          },
        ],
      },
    },
  ],
}
