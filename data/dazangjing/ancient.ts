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
              { title_zh: '託名斐洛《聖經古史》', title_orig: 'Pseudo-Philo, Liber Antiquitatum Biblicarum', era: '1 世紀', note: '亞當至大衛的另類以色列史' },
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
              { title_zh: '託名福西里德智訓', title_orig: 'Pseudo-Phocylides', note: '假借希臘詩人之名的猶太勸世文' },
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
              { title_zh: '託名馬太童年福音', title_orig: 'Gospel of Pseudo-Matthew', era: '童年' },
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
              { title_zh: '彼得致雅各書', title_orig: 'Epistle of Peter to James', era: '彼得', note: '託名克勉文集前言' },
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
              { title_zh: '託名提多書', title_orig: 'Pseudo-Titus Epistle', era: '提多', note: '論貞潔的勸誡書' },
            ],
          },
          {
            key: 'catholic-2', label: '第二大公書信', label_en: 'Second Catholic Epistles', desc: '教父推薦但未入正藏的非使徒書信。',
            works: [
              { title_zh: '克勉二書', title_orig: '2 Clement', era: '克勉（羅馬）', note: '古代最早的講道辭，教父推薦不足', link: '/apocrypha' },
              { title_zh: '託名克勉致雅各書', title_orig: 'Pseudo-Clementine Epistles', era: '克勉（羅馬）' },
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
      summary: '教會運作的骨架。正藏為使徒律、大公會議律、地方會議律與修道會規（含由經藏移入的教會秩序書、各信經作卷首總綱）；外藏為異端／分裂派的宗派律，以及作為舊約根源的猶太律法（米書拿、死海社群規章等）。',
      portal: { to: '/creeds', label: '信條與大公會議' },
      zheng: {
        divisions: [
          {
            key: 'apostolic', label: '使徒律部', label_en: 'Apostolic & Early Church Orders',
            works: [
              { title_zh: '十二使徒遺訓', title_orig: 'Didache', era: '1 世紀末', note: '最古老的教會實踐手冊', link: '/apocrypha' },
              { title_zh: '使徒教訓', title_orig: 'Didascalia Apostolorum', era: '3 世紀', note: '敘利亞教會生活法度', link: '/canon-law' },
              { title_zh: '使徒憲章', title_orig: 'Apostolic Constitutions', era: '4 世紀', note: '古代大公教會法規集大成', link: '/canon-law' },
              { title_zh: '衣索比亞教會秩序六典', title_orig: 'Sirate Tsion / Tizaz / Gitsew / Abtilis / Covenant I–II', note: '秩序典‧訓令典‧戒律典‧規章典‧聖約前後典', link: '/canon-law' },
            ],
          },
          {
            key: 'ecumenical', label: '大公律部', label_en: 'Ecumenical Councils & Creeds',
            works: [
              { title_zh: '尼西亞信經', title_orig: 'Nicene Creed', era: '325', note: '卷首總綱，不佔卷數', link: '/creeds' },
              { title_zh: '尼西亞—君士坦丁堡信經', title_orig: 'Niceno-Constantinopolitan Creed', era: '381', note: '卷首總綱，不佔卷數', link: '/creeds' },
              { title_zh: '迦克墩信仰定義', title_orig: 'Chalcedonian Definition', era: '451', note: '卷首總綱，不佔卷數', link: '/creeds' },
              { title_zh: '尼西亞大公會議錄', title_orig: 'Canons of Nicaea I', era: '325', note: '解決亞流派危機，20 條教規', link: '/creeds' },
              { title_zh: '君士坦丁堡大公會議錄', title_orig: 'Canons of Constantinople I', era: '381', note: '確立聖靈神性，7 條教規', link: '/creeds' },
              { title_zh: '以弗所大公會議錄', title_orig: 'Canons of Ephesus', era: '431', note: '解決涅斯多留爭議', link: '/creeds' },
              { title_zh: '迦克墩大公會議錄', title_orig: 'Canons of Chalcedon', era: '451', note: '確立神人二性與四大教區，30 條教規', link: '/creeds' },
              { title_zh: '第二屆君士坦丁堡大公會議錄', title_orig: 'Acts of Constantinople II', era: '553', note: '譴責三章', link: '/creeds' },
              { title_zh: '第三屆君士坦丁堡大公會議錄', title_orig: 'Acts of Constantinople III', era: '680–681', note: '解決基督一志論危機', link: '/creeds' },
              { title_zh: '特魯洛五六屆會議錄', title_orig: 'Canons of the Quinisext Council', era: '692', note: '東正教 102 條紀律法典', link: '/creeds' },
              { title_zh: '第二屆尼西亞大公會議錄', title_orig: 'Acts of Nicaea II', era: '787', note: '頒布尊崇聖像教令與 22 條教規', link: '/creeds' },
            ],
          },
          {
            key: 'local', label: '地方律部', label_en: 'Local Synods & Western Creeds',
            works: [
              { title_zh: '使徒信經', title_orig: 'Apostles’ Creed', note: '西方本土洗禮信經，卷首總綱', link: '/creeds' },
              { title_zh: '亞他那修信經', title_orig: 'Athanasian Creed', era: '5–6 世紀', note: '含和子句的拉丁神學總結，卷首總綱', link: '/creeds' },
              { title_zh: '埃爾維拉教規', title_orig: 'Canons of Elvira', era: '約 305', note: '西班牙性道德與反聖像法', link: '/canon-law' },
              { title_zh: '安居拉教規', title_orig: 'Canons of Ancyra', era: '314', note: '叛教者補贖問題', link: '/canon-law' },
              { title_zh: '甘格拉教規', title_orig: 'Canons of Gangra', era: '約 340', note: '捍衛婚姻神聖、反極端禁慾', link: '/canon-law' },
              { title_zh: '老底嘉教規', title_orig: 'Canons of Laodicea', era: '約 363', note: '早期正典名單與禮儀規範', link: '/canon-law' },
              { title_zh: '迦太基教規', title_orig: 'Canons of the African Church', era: '397 & 419', note: '北非法典與西方正典確立', link: '/canon-law' },
              { title_zh: '奧朗日會議錄', title_orig: 'Council of Orange', era: '529', note: '調和恩典論、譴責半伯拉糾主義', link: '/canon-law' },
              { title_zh: '第三屆托雷多會議錄', title_orig: 'Third Council of Toledo', era: '589', note: '首次正式宣讀和子句', link: '/canon-law' },
              { title_zh: '亞琛一般詔令', title_orig: 'Admonitio Generalis', era: '789', note: '查理曼宗教整頓令', link: '/canon-law' },
              { title_zh: '法蘭克福會議錄', title_orig: 'Council of Frankfurt', era: '794', note: '拒絕東方聖像教令', link: '/canon-law' },
            ],
          },
          {
            key: 'monastic', label: '修道律部', label_en: 'Monastic Rules',
            works: [
              { title_zh: '帕科米烏斯規', title_orig: 'Rule of Pachomius', era: '4 世紀', note: '史上第一部團體修道法規（埃及）', link: '/canon-law' },
              { title_zh: '大巴西略會規', title_orig: 'Rule of St. Basil', era: '4 世紀', note: '東方修道主義核心', link: '/canon-law' },
              { title_zh: '奧斯定會規', title_orig: 'Rule of St. Augustine', era: '5 世紀', note: '教士群體生活綱領', link: '/canon-law' },
              { title_zh: '哥倫巴努斯會規', title_orig: 'Rule of St. Columbanus', era: '6 世紀', note: '凱爾特嚴修傳統', link: '/canon-law' },
              { title_zh: '本篤會規', title_orig: 'Rule of St. Benedict', era: '6 世紀', note: '奠定西方中世紀修道文明', link: '/canon-law' },
            ],
          },
        ],
      },
      wai: {
        divisions: [
          {
            key: 'jewish', label: '猶太律部', label_en: 'Old Covenant & Second Temple Codes',
            works: [
              { title_zh: '聖約律', title_orig: 'Book of the Covenant', note: '出埃及記核心律法' },
              { title_zh: '聖潔律', title_orig: 'Holiness Code', note: '利未記祭司與純潔法' },
              { title_zh: '申命律', title_orig: 'Deuteronomic Code', note: '申命記重申之法' },
              { title_zh: '聖殿法典', title_orig: 'Temple Scroll (11QT)', era: '前 2 世紀', note: '艾瑟尼曠野終極聖殿藍圖', link: '/apocrypha' },
              { title_zh: '大馬士革盟約', title_orig: 'Damascus Document (CD)', note: '艾瑟尼社群盟約與行為法規', link: '/apocrypha' },
              { title_zh: '社群規章', title_orig: 'Community Rule (1QS)', note: '昆蘭曠野修道生活準則', link: '/apocrypha' },
              { title_zh: '判律辭', title_orig: 'Halakhic Letter (4QMMT)', note: '與主流教派決裂的法律裁定書', link: '/apocrypha' },
              { title_zh: '光明戰卷', title_orig: 'War Scroll (1QM)', note: '末日決戰軍事指令', link: '/apocrypha' },
              { title_zh: '斐洛特殊律', title_orig: 'De Specialibus Legibus', era: '1 世紀', note: '將律法歸入十誡的系統化專著' },
              { title_zh: '米書拿法典', title_orig: 'Mishnah', era: '約 200', note: '法利賽口傳律法大成' },
              { title_zh: '陀瑟他補典', title_orig: 'Tosefta', era: '約 300', note: '與米書拿平行的拉比補充判例' },
              { title_zh: '禁食規', title_orig: 'Megillat Taanit', era: '1 世紀', note: '節慶與禁食的實務守則' },
            ],
          },
          {
            key: 'sectarian', label: '宗派律部', label_en: 'Sectarian & Independent Church Canons',
            works: [
              { title_zh: '亞美尼亞正統信經', title_orig: 'Armenian Creed', note: '宗派信經卷首總綱', link: '/creeds' },
              { title_zh: '阿弗拉哈特信仰告白', title_orig: 'Creed of Aphrahat', era: '4 世紀', note: '波斯景教母會古老閃族宣告', link: '/creeds' },
              { title_zh: '伊薩克會議錄', title_orig: 'Synod of Isaac', era: '410', note: '東方亞述教會（景教）建制根本法典', link: '/canon-law' },
              { title_zh: '達迪修會議錄', title_orig: 'Synod of Dadisho', era: '424', note: '脫離羅馬安提阿管轄的獨立宣言', link: '/canon-law' },
              { title_zh: '阿卡修會議錄', title_orig: 'Synod of Acacius', era: '486', note: '接納安提阿學派、允許神職結婚', link: '/canon-law' },
              { title_zh: '阿什蒂沙特會議錄', title_orig: 'Synod of Ashtishat', era: '364', note: '亞美尼亞本土教會奠基', link: '/canon-law' },
              { title_zh: '德溫會議錄', title_orig: 'First Council of Dvin', era: '506', note: '正式拒絕迦克墩定讞', link: '/canon-law' },
              { title_zh: '安提阿奉獻會議教規', title_orig: 'Canons of Antioch in Encaeniis', era: '341', note: '亞流派主導的嚴密行政教規', link: '/canon-law' },
              { title_zh: '迦太基多納徒會議錄', title_orig: 'Donatist Council of Carthage', era: '311/312', note: '多納徒派極端聖潔紀律', link: '/canon-law' },
              { title_zh: '耶烏密規', title_orig: 'Books of Jeu', note: '諾斯底靈魂穿越諸天密碼法規', link: '/gnostic' },
              { title_zh: '摩尼十戒與聽者規', title_orig: 'Manichaean Precepts', note: '劃分選民與聽者的階級禁慾法度' },
              { title_zh: '特土良嚴行規', title_orig: 'Tertullian’s Montanist Tracts', era: '約 200', note: '孟他努派禁慾底線' },
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
      summary: '教父用血淚與智慧為信仰披上的「重裝鎧甲」。正藏為正統的護教、反異端、系統教義、釋經與神祕主義；外藏為作為「對手與底色」的猶太哲學、諾斯底與摩尼教異端論述，以及外教批判。',
      portal: { to: '/fathers', label: '教父著作' },
      zheng: {
        divisions: [
          {
            key: 'apologia', label: '護教詞部', label_en: 'Apologetics',
            works: [
              { title_zh: '第一護教詞', title_orig: 'First Apology', author: '猶斯定', era: '2 世紀', note: '寫給羅馬皇帝的正式申訴書', link: '/fathers' },
              { title_zh: '第二護教詞', title_orig: 'Second Apology', author: '猶斯定', era: '2 世紀', link: '/fathers' },
              { title_zh: '駁特里風護教詞', title_orig: 'Dialogue with Trypho', author: '猶斯定', era: '2 世紀', note: '針對猶太教義的學術辯論', link: '/fathers' },
              { title_zh: '護教辯', title_orig: 'Apologeticus', author: '特土良', era: '2 世紀', link: '/fathers' },
              { title_zh: '駁塞爾修斯', title_orig: 'Contra Celsum', author: '俄利根', era: '3 世紀', note: '古代最龐大的基督教對希臘哲學筆戰', link: '/fathers' },
            ],
          },
          {
            key: 'refutations', label: '反異端部', label_en: 'Refutations',
            works: [
              { title_zh: '駁異端論', title_orig: 'Adversus Haereses', author: '愛任紐', era: '2 世紀', note: '拆解諾斯底宇宙觀的巨著', link: '/fathers' },
              { title_zh: '駁亞流論', title_orig: 'Orationes contra Arianos', author: '亞他那修', era: '4 世紀', note: '奠定尼西亞正統的純神學論證', link: '/fathers' },
              { title_zh: '破百異端駁', title_orig: 'Panarion', author: '愛比法紐', era: '4 世紀', note: '原名《百草藥箱》，如異端百科全書', link: '/fathers' },
            ],
          },
          {
            key: 'dogmatics', label: '系統與教義部', label_en: 'Systematic Dogmatics',
            works: [
              { title_zh: '基要原理論', title_orig: 'De Principiis', author: '俄利根', era: '3 世紀', note: '史上第一部系統神學專著', link: '/fathers' },
              { title_zh: '論道成肉身', title_orig: 'De Incarnatione', author: '亞他那修', era: '4 世紀', link: '/fathers' },
              { title_zh: '論聖靈', title_orig: 'De Spiritu Sancto', author: '大巴西略', era: '4 世紀', link: '/fathers' },
              { title_zh: '三位一體論', title_orig: 'De Trinitate', author: '奧古斯丁', era: '4 世紀', note: '花二十年寫成的學術天花板', link: '/fathers' },
              { title_zh: '上帝之城', title_orig: 'De Civitate Dei', author: '奧古斯丁', era: '5 世紀', note: '回應羅馬傾覆的歷史哲學鉅作', link: '/fathers' },
              { title_zh: '論本性與恩典', title_orig: 'De Natura et Gratia', author: '奧古斯丁', era: '5 世紀', note: '反伯拉糾派專著', link: '/fathers' },
              { title_zh: '正統信仰闡述論', title_orig: 'De Fide Orthodoxa', author: '大馬士革的約翰', era: '8 世紀', note: '東方教會教義的集大成', link: '/fathers' },
            ],
          },
          {
            key: 'exegesis', label: '釋經與釋祕部', label_en: 'Exegesis',
            works: [
              { title_zh: '約翰福音註', title_orig: 'Commentary on John', author: '俄利根', era: '3 世紀', note: '逐字哲學分析的案頭註釋', link: '/fathers' },
              { title_zh: '雅歌疏', title_orig: 'Commentary on the Song of Songs', author: '俄利根', era: '3 世紀', note: '靈意解經的代表', link: '/fathers' },
              { title_zh: '馬太福音註', title_orig: 'Homilies on Matthew', author: '金口若望', era: '4 世紀', link: '/fathers' },
              { title_zh: '詩篇註', title_orig: 'Commentary on the Psalms', author: '狄奧多若', era: '4 世紀', link: '/fathers' },
              { title_zh: '先知書註', title_orig: 'Commentaries on the Prophets', author: '耶柔米', era: '4 世紀', note: '據希伯來原文逐字詞源分析', link: '/fathers' },
              { title_zh: '創世記字義註解', title_orig: 'De Genesi ad Litteram', author: '奧古斯丁', era: '5 世紀', link: '/fathers' },
            ],
          },
          {
            key: 'mystical', label: '神祕主義部', label_en: 'Mystical Theology',
            works: [
              { title_zh: '天階序列', title_orig: 'De Caelesti Hierarchia', author: '託名狄奧尼修斯', era: '5 世紀', note: '結合新柏拉圖主義的神聖秩序', link: '/fathers' },
              { title_zh: '神祕神學', title_orig: 'De Mystica Theologia', author: '託名狄奧尼修斯', era: '5 世紀', link: '/fathers' },
              { title_zh: '神聖攀登天階', title_orig: 'The Ladder of Divine Ascent', author: '階梯約翰', era: '7 世紀', note: '隱修士的靈魂攀登指南', link: '/fathers' },
              { title_zh: '摩西生平', title_orig: 'De Vita Moysis', author: '尼撒的格列高理', era: '4 世紀', note: '探討靈魂上升的靈修專論', link: '/fathers' },
            ],
          },
        ],
      },
      wai: {
        divisions: [
          {
            key: 'jewish-philosophy', label: '猶太哲學與法理部', label_en: 'Jewish Philosophy & Halakhah',
            works: [
              { title_zh: '斐洛真理論', title_orig: 'Works of Philo', author: '斐洛', era: '1 世紀', note: '教父神學術語的先驅——希臘化猶太哲學' },
              { title_zh: '猶太教法理疏', title_orig: 'Early Rabbinic Tractates', author: '早期拉比', era: '3 世紀', note: '早期拉比釋經與法理疏解精華' },
            ],
          },
          {
            key: 'gnostic-manichaean', label: '諾斯底與摩尼教部', label_en: 'Gnostic & Manichaean Heresies',
            works: [
              { title_zh: '瓦倫廷神話論', title_orig: 'Valentinian Cosmogony', author: '瓦倫廷學派', era: '2 世紀', note: '諾斯底派宇宙起源的異端體系', link: '/gnostic' },
              { title_zh: '摩尼教義論', title_orig: 'Manichaean Treatises', author: '摩尼教', era: '3 世紀', note: '極端二元論的光明王國神話' },
            ],
          },
          {
            key: 'pagan-critique', label: '外教批判部', label_en: 'Pagan Critiques',
            works: [
              { title_zh: '塞爾蘇斯《真道》', title_orig: 'Celsus, On the True Doctrine', era: '2 世紀', note: '經俄利根《駁塞爾修斯》保存' },
              { title_zh: '波菲利《駁基督徒》殘篇', title_orig: 'Porphyry, Against the Christians', era: '3 世紀' },
              { title_zh: '皇帝尤利安《駁加利利人》', title_orig: 'Julian, Against the Galileans', era: '4 世紀' },
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
      summary: '基督宗教的真實人間史。正藏為教會通史、殉道受難錄、聖徒本傳、自傳告白、宗統記、編年表與典志；外藏為猶太正史、殉道、拉比傳燈與編年史料。',
      portal: { to: '/fathers', label: '教父著作' },
      zheng: {
        divisions: [
          {
            key: 'general-history', label: '通史部（史）', label_en: 'Ecclesiastical Histories',
            works: [
              { title_zh: '教會史', title_orig: 'Historia Ecclesiastica', author: '優西比烏', era: '4 世紀', note: '史上第一部教會總史', link: '/fathers' },
              { title_zh: '教會史續編', title_orig: 'Historia Ecclesiastica (continuators)', author: '索克拉底／索佐門／提奧多勒', era: '5 世紀', note: '續寫優西比烏的古典史學三傑', link: '/fathers' },
              { title_zh: '敘利亞教會史', title_orig: 'Historia Ecclesiastica', author: '約翰‧以弗所', era: '6 世紀', note: '東方敘利亞語教會視角', link: '/fathers' },
              { title_zh: '亞美尼亞史', title_orig: 'History of the Armenians', author: '莫夫塞斯', era: '5 世紀', note: '民族教會建立史', link: '/fathers' },
              { title_zh: '法蘭克人歷史', title_orig: 'Historia Francorum', author: '都爾的格列高利', era: '6 世紀', note: '蠻族改宗與帝國興衰紀實', link: '/fathers' },
              { title_zh: '英國人教會史', title_orig: 'Historia Ecclesiastica Gentis Anglorum', author: '比德', era: '8 世紀', note: '凱爾特與羅馬傳統融合的巔峰', link: '/fathers' },
            ],
          },
          {
            key: 'martyr-acts', label: '殉道受難錄（錄）', label_en: 'Acts of the Martyrs',
            works: [
              { title_zh: '波利卡殉道錄', title_orig: 'Martyrdom of Polycarp', era: '2 世紀', note: '最古老的真實受難紀錄', link: '/apocrypha' },
              { title_zh: '里昂殉道錄', title_orig: 'Letter of the Churches of Vienne and Lyons', era: '2 世紀', note: '早期教會集體受難紀錄', link: '/fathers' },
              { title_zh: '佩蓓圖與斐麗西達受難錄', title_orig: 'Passion of Perpetua and Felicity', era: '3 世紀', note: '佩蓓圖在獄中親記的日記', link: '/apocrypha' },
              { title_zh: '巴勒斯坦殉道者', title_orig: 'Martyrs of Palestine', author: '優西比烏', era: '4 世紀', note: '優西比烏親歷的教難現場', link: '/fathers' },
            ],
          },
          {
            key: 'hagiography', label: '聖徒本傳（傳）', label_en: 'Hagiographies',
            works: [
              { title_zh: '塞浦路斯傳', title_orig: 'Vita Cypriani', author: '龐提烏斯', era: '3 世紀', note: '主教在瘟疫中的慈悲與管理', link: '/fathers' },
              { title_zh: '安東尼傳', title_orig: 'Vita Antonii', author: '亞他那修', era: '4 世紀', note: '確立修道主義與沙漠隱士標準', link: '/fathers' },
              { title_zh: '馬丁傳', title_orig: 'Vita Sancti Martini', author: '蘇爾皮基烏‧塞維魯', era: '4 世紀', note: '西方苦修與巡牧的典範', link: '/fathers' },
              { title_zh: '沙漠父老傳燈錄', title_orig: 'Apophthegmata Patrum', era: '4–5 世紀', note: '沙漠隱修士師徒智慧的傳遞', link: '/fathers' },
            ],
          },
          {
            key: 'autobiography', label: '自傳告白（記）', label_en: 'Autobiography & Confessions',
            works: [
              { title_zh: '懺悔錄', title_orig: 'Confessiones', author: '奧古斯丁', era: '4 世紀', note: '古代最深刻的個人生命轉折紀錄', link: '/fathers' },
              { title_zh: '我罪論記', title_orig: 'De Vita Sua', author: '拿先斯的格列高理', era: '4 世紀', note: '以詩歌寫下的自傳', link: '/fathers' },
            ],
          },
          {
            key: 'succession', label: '宗統記（世家）', label_en: 'Episcopal Successions',
            works: [
              { title_zh: '羅馬主教世家', title_orig: 'Liber Pontificalis', era: '6 世紀', note: '歷任教宗的生平與政績', link: '/fathers' },
              { title_zh: '亞歷山大宗統記', title_orig: 'Patriarchs of Alexandria', note: '亞歷山大城主教傳承' },
            ],
          },
          {
            key: 'chronicle', label: '編年表（表／通鑒）', label_en: 'Chronicles & Annals',
            works: [
              { title_zh: '編年史', title_orig: 'Chronicon', author: '優西比烏', era: '4 世紀', note: '連結世俗帝國與聖經時間線', link: '/fathers' },
              { title_zh: '編年史（拉丁擴編）', title_orig: 'Chronicon', author: '耶柔米', era: '4 世紀', note: '定義中世紀時間基準', link: '/fathers' },
              { title_zh: '西班牙編年史', title_orig: 'Chronica / Historia Gothorum', author: '依西多祿', era: '7 世紀', note: '西哥德王國與本土教史的對齊', link: '/fathers' },
              { title_zh: '愛爾蘭編年史', title_orig: 'Irish Annals', note: '早期凱爾特教派的時序紀錄' },
            ],
          },
          {
            key: 'gazetteers', label: '典志部（志）', label_en: 'Travelogues & Gazetteers',
            works: [
              { title_zh: '波爾多朝聖志', title_orig: 'Itinerarium Burdigalense', era: '333', note: '第一份詳盡記錄聖地路徑的檔案', link: '/fathers' },
              { title_zh: '艾格莉亞朝聖志', title_orig: 'Itinerarium Egeriae', author: '艾格莉亞', era: '4 世紀', note: '修女對耶路撒冷禮儀的詳實手記', link: '/fathers' },
              { title_zh: '聖地景觀志', title_orig: 'De Situ Hierusalem', author: '歐歇利烏斯', era: '5 世紀', note: '早期基督徒的地理與建築紀錄', link: '/fathers' },
            ],
          },
        ],
      },
      wai: {
        divisions: [
          {
            key: 'jewish-chronicles', label: '猶太正史記（記）', label_en: 'Jewish Histories',
            works: [
              { title_zh: '猶太戰記', title_orig: 'The Jewish War', author: '約瑟夫斯', era: '1 世紀', note: '反羅馬起義現場，初代教會最關鍵史料' },
              { title_zh: '猶太古史', title_orig: 'Antiquities of the Jews', author: '約瑟夫斯', era: '1 世紀', note: '創世至羅馬統治的猶太通史' },
              { title_zh: '猶太王國志', title_orig: 'Josippon', note: '希伯來文版猶太歷史集大成' },
            ],
          },
          {
            key: 'jewish-martyr', label: '猶太殉道傳（傳）', label_en: 'Jewish Martyrologies',
            works: [
              { title_zh: '馬加比殉道傳', title_orig: 'The Maccabean Martyrdoms', note: '母親帶領七子為律法而死，殉道文學雛形', link: '/apocrypha' },
            ],
          },
          {
            key: 'rabbinic-succession', label: '拉比與大祭司傳燈（傳燈錄）', label_en: 'Rabbinic & Priestly Successions',
            works: [
              { title_zh: '拉比傳燈錄', title_orig: 'Pirkei Avot', era: '2–3 世紀', note: '又稱「先賢訓辭」，律法自摩西經拉比傳承' },
              { title_zh: '大祭司世系記', title_orig: 'High-Priestly Successions', note: '第二聖殿時期大祭司更迭' },
            ],
          },
          {
            key: 'jewish-chronology', label: '猶太編年表（編年）', label_en: 'Jewish Chronologies',
            works: [
              { title_zh: '猶太編年史', title_orig: 'Seder Olam Rabbah', era: '2 世紀', note: '猶太傳統最古老的年代學' },
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
      summary: '人類傳遞啟示的「歷史肉身」。正藏為大公教會接受的古卷寶抄、東方與西方多語大譯本、譯經序論與校勘考異；外藏為猶太修訂譯本與意譯塔古姆。',
      portal: { to: '/scripture', label: '聖經多版本對照' },
      zheng: {
        divisions: [
          {
            key: 'codices', label: '古卷寶抄部', label_en: 'The Great Codices',
            works: [
              { title_zh: '西乃山大卷', title_orig: 'Codex Sinaiticus', era: '4 世紀', note: '現存最完整最古老的新約與希臘文舊約，含外典', link: '/scripture' },
              { title_zh: '梵蒂岡大卷', title_orig: 'Codex Vaticanus', era: '4 世紀', note: '最純淨的亞歷山大文本代表', link: '/scripture' },
              { title_zh: '亞歷山大巨卷', title_orig: 'Codex Alexandrinus', era: '5 世紀', note: '拜占庭文本體系的早期基石', link: '/scripture' },
              { title_zh: '伯撒雙語大卷', title_orig: 'Codex Bezae', era: '5 世紀', note: '希臘拉丁雙語，含大量西方變體', link: '/scripture' },
              { title_zh: '艾弗冷重寫寶抄', title_orig: 'Codex Ephraemi Rescriptus', era: '5 世紀', note: '教父講章底下覆蓋著被刮掉的古老經文', link: '/scripture' },
              { title_zh: '華盛頓四福音大卷', title_orig: 'Codex Washingtonianus', era: '4–5 世紀', note: '含獨家「弗里爾補編」', link: '/scripture' },
            ],
          },
          {
            key: 'eastern-versions', label: '東方與希臘譯經部', label_en: 'Eastern & Greek Versions',
            works: [
              { title_zh: '七十士希臘文大譯本', title_orig: 'Septuagint', era: '前 3–2 世紀', note: '初代教會的唯一舊約聖經', link: '/scripture' },
              { title_zh: '四福音合參', title_orig: 'Diatessaron', author: '塔提安', era: '2 世紀', note: '四福音融合本，統治敘利亞教會數百年' },
              { title_zh: '別西大敘利亞文大譯本', title_orig: 'Peshitta', era: '2–5 世紀', note: '東方亞蘭語系的「武加大」', link: '/scripture' },
              { title_zh: '科普特文南北大譯本', title_orig: 'Coptic (Sahidic & Bohairic)', era: '3–4 世紀', note: '埃及修道士專用，保存古老變體', link: '/scripture' },
              { title_zh: '吉茲文衣索比亞大譯本', title_orig: 'Geʿez Version', era: '4–5 世紀', note: '含《以諾書》與《禧年書》的巨型譯本', link: '/scripture' },
              { title_zh: '亞美尼亞文大譯本', title_orig: 'Armenian Version', era: '5 世紀', note: '譯本之后，翻譯精美', link: '/scripture' },
            ],
          },
          {
            key: 'western-versions', label: '西方與邊區譯經部', label_en: 'Western & Marginal Versions',
            works: [
              { title_zh: '古拉丁文譯本', title_orig: 'Vetus Latina', era: '2–4 世紀', note: '耶柔米統一前的草根拉丁譯本', link: '/scripture' },
              { title_zh: '武加大拉丁文大譯本', title_orig: 'Vulgate', author: '耶柔米', era: '4 世紀', note: '統治西方中世紀一千年', link: '/scripture' },
              { title_zh: '哥德文烏爾菲拉譯本', title_orig: 'Gothic Bible', author: '烏爾菲拉', era: '4 世紀', note: '為日耳曼蠻族造字翻譯，現存「銀色大卷」' },
              { title_zh: '大秦景教譯經殘卷', title_orig: 'Jingjiao Chinese Fragments', era: '7–8 世紀', note: '唐代景教中文聖經殘篇（《尊經》《一神論》）' },
            ],
          },
          {
            key: 'criticism', label: '校勘考異部', label_en: 'Prefaces & Textual Criticism',
            works: [
              { title_zh: '武加大譯本大序', title_orig: 'Prologus Galeatus', author: '耶柔米', era: '4 世紀', note: '西方確立正典與次經界線的最重要文獻', link: '/fathers' },
              { title_zh: '六文本合參殘卷', title_orig: 'Hexapla', author: '俄利根', era: '3 世紀', note: '六版本舊約並列，古代版本學最高峰', link: '/fathers' },
              { title_zh: '新約古卷異讀考異', title_orig: 'Apparatus Criticus', note: '馬可福音長短結尾、約壹三位一體逗號、行淫婦女段落真偽', link: '/scripture' },
            ],
          },
        ],
      },
      wai: {
        divisions: [
          {
            key: 'jewish-versions', label: '猶太譯本部', label_en: 'Jewish Versions & Targums',
            works: [
              { title_zh: '七十士譯本傳奇', title_orig: 'Letter of Aristeas', era: '前 2 世紀', note: '譯經神話的源頭' },
              { title_zh: '亞居拉希臘文譯本', title_orig: 'Aquila’s Version', author: '亞居拉', era: '2 世紀', note: '猶太人反擊基督教而重譯的極度直譯本' },
              { title_zh: '狄奧多田與辛馬庫譯本', title_orig: 'Theodotion & Symmachus', era: '2–3 世紀', note: '另兩部重要希臘文重譯本' },
              { title_zh: '亞蘭文塔古姆譯註', title_orig: 'Targums', note: '將「上帝的道（Memra）」啟發約翰福音道成肉身' },
              { title_zh: '撒馬利亞五經異讀考', title_orig: 'Samaritan Pentateuch', note: '撒馬利亞人修改的摩西五經關鍵段落' },
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
      summary: '為冷峻的法典與神學大山注入真實的人間血肉。正藏為大公通諭與牧函、神學交鋒與靈修尺牘、政教博弈奏表；外藏為猶太教戰地手札。',
      portal: { to: '/fathers', label: '教父著作' },
      zheng: {
        divisions: [
          {
            key: 'pastoral', label: '大公通諭與牧函部', label_en: 'Encyclicals & Pastoral Letters',
            works: [
              { title_zh: '羅馬克勉一書', title_orig: '1 Clement', author: '羅馬的克勉', era: '1 世紀末', note: '新約之外最古老的基督教文獻', link: '/apocrypha' },
              { title_zh: '伊格那丟七函', title_orig: 'Epistles of Ignatius', author: '安提阿的伊格那丟', era: '2 世紀', note: '殉道途中的絕筆牧函，確立主教制權威', link: '/apocrypha' },
              { title_zh: '坡旅甲致腓立比人書', title_orig: 'Polycarp to the Philippians', author: '坡旅甲', era: '2 世紀', link: '/apocrypha' },
              { title_zh: '居普良牧函集', title_orig: 'Letters of Cyprian', author: '居普良', era: '3 世紀', note: '大逼迫中指揮信徒面對死亡的戰時通信', link: '/fathers' },
              { title_zh: '大良獅王之諭', title_orig: 'Tome of Leo', author: '大良', era: '5 世紀', note: '終結迦克墩基督論爭議', link: '/encyclicals' },
            ],
          },
          {
            key: 'spiritual', label: '神學交鋒與靈修尺牘部', label_en: 'Personal & Spiritual Epistles',
            works: [
              { title_zh: '奧古斯丁與耶柔米往來尺牘', title_orig: 'Augustine–Jerome Correspondence', era: '4–5 世紀', note: '古代最精彩的學術筆戰', link: '/fathers' },
              { title_zh: '加帕多家三傑尺牘集', title_orig: 'Letters of the Cappadocian Fathers', era: '4 世紀', note: '私信中建構三位一體神學名詞', link: '/fathers' },
              { title_zh: '金口若望流放家書', title_orig: 'Letters of Chrysostom from Exile', author: '金口若望', era: '5 世紀', note: '流放至死前寫給女執事奧林匹亞的絕筆', link: '/fathers' },
              { title_zh: '沙漠父老巴撒努菲答問札', title_orig: 'Letters of Barsanuphius and John', era: '6 世紀', note: '隱修士以書信回答靈修難題', link: '/fathers' },
            ],
          },
          {
            key: 'diplomatic', label: '政教博弈奏表部', label_en: 'Diplomatic & State Letters',
            works: [
              { title_zh: '安波羅修致皇帝奏表', title_orig: 'Letters of Ambrose to Emperors', author: '安波羅修', era: '4 世紀', note: '逼狄奧多西皇帝在教會門口公開悔改', link: '/fathers' },
              { title_zh: '傑拉修雙劍論公文', title_orig: 'Letter of Gelasius to Anastasius', author: '教宗傑拉修一世', era: '5 世紀末', note: '首次提出神權高於王權的雙劍理論', link: '/encyclicals' },
              { title_zh: '大額我略外交尺牘', title_orig: 'Register of Gregory the Great', author: '教宗大額我略', era: '6 世紀末', note: '寫給法蘭克女王、倫巴底國王的政治信件', link: '/encyclicals' },
            ],
          },
        ],
      },
      wai: {
        divisions: [
          {
            key: 'jewish-letters', label: '猶太教手札部', label_en: 'Jewish Field Letters',
            works: [
              { title_zh: '巴爾‧科赫巴戰地手札', title_orig: 'Letters of Bar Kokhba', author: '巴爾‧科赫巴', era: '2 世紀', note: '死海山洞出土的起義軍令木簡真跡' },
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
      summary: '最具動態感與神聖感的空間。正藏為大公聖祭（事奉聖儀）、聖事密典與教規、日課與經課；外藏為 400 年前的猶太祈禱與節令禮文。',
      zheng: {
        divisions: [
          {
            key: 'liturgies', label: '大公聖祭部', label_en: 'Divine Liturgies',
            works: [
              { title_zh: '雅各事奉聖儀', title_orig: 'Liturgy of St. James', note: '耶路撒冷與安提阿最古老的聖餐禮', link: '/fathers' },
              { title_zh: '馬可事奉聖儀', title_orig: 'Liturgy of St. Mark', note: '亞歷山大與科普特教會專用', link: '/fathers' },
              { title_zh: '大巴西略事奉聖儀', title_orig: 'Liturgy of St. Basil', author: '大巴西略', note: '拜占庭重大節日的超長版聖儀', link: '/fathers' },
              { title_zh: '金口若望事奉聖儀', title_orig: 'Liturgy of St. John Chrysostom', author: '金口若望', note: '東方教會至今每日使用的標準敬拜', link: '/fathers' },
              { title_zh: '羅馬彌撒正典', title_orig: 'Roman Canon', era: '4 世紀核心定型', note: '西方拉丁教會最古老的聖餐祈禱文' },
            ],
          },
          {
            key: 'sacramentaries', label: '聖事密典與教規部', label_en: 'Sacramentaries & Ordines',
            works: [
              { title_zh: '希波律陀聖事軌', title_orig: 'Apostolic Tradition', author: '希波律陀', era: '3 世紀初', note: '保留羅馬最古老的洗禮問答與按手禮', link: '/fathers' },
              { title_zh: '傑拉修聖事密典', title_orig: 'Gelasian Sacramentary', era: '8 世紀', note: '法蘭克與羅馬混合的官方聖事手冊' },
              { title_zh: '大額我略聖事密典', title_orig: 'Gregorian Sacramentary', author: '教宗大額我略', era: '8–9 世紀', note: '寄給查理曼大帝的官方標準版' },
              { title_zh: '羅馬禮儀軌', title_orig: 'Ordines Romani', note: '教宗大彌撒的神職走位動線指南' },
            ],
          },
          {
            key: 'office', label: '日課與經課部', label_en: 'Divine Office & Lectionaries',
            works: [
              { title_zh: '拜占庭時辰經', title_orig: 'Horologion', note: '東方修士每日八個祈禱時辰規程', link: '/fathers' },
              { title_zh: '耶路撒冷大經課表', title_orig: 'Jerusalem Lectionary', era: '5 世紀', note: '規定聖誕到復活節每日讀經與堂所' },
            ],
          },
          {
            key: 'mystagogy', label: '奧祕教理部', label_en: 'Mystagogy',
            works: [
              { title_zh: '耶路撒冷區利羅《奧祕教理講授》', title_orig: 'Mystagogical Catecheses', author: '耶路撒冷的區利羅', era: '4 世紀', link: '/fathers' },
            ],
          },
        ],
      },
      wai: {
        divisions: [
          {
            key: 'jewish-liturgy', label: '猶太祈禱與節令部', label_en: 'Jewish Liturgy (to 400 CE)',
            works: [
              { title_zh: '巴勒斯坦三年期經課表', title_orig: 'Palestinian Triennial Cycle', note: '早期會堂三年讀完摩西五經的進度表' },
              { title_zh: '古本逾越節哈加達', title_orig: 'Early Passover Haggadah', note: '逾越節家宴講述出埃及的古老儀式文本' },
              { title_zh: '安息日獻祭之歌（天使禮儀）', title_orig: 'Songs of the Sabbath Sacrifice', note: '死海社群的敬拜詩歌', link: '/apocrypha' },
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
      genres: '聖詠‧讚歌‧史詩‧寓言',
      summary: '最具美感、最能觸動靈魂的藝術聖殿。正藏為聖詠與頌辭、靈戰與敘事史詩、勸世寓言與教化文學；外藏為諾斯底與摩尼教讚歌。',
      zheng: {
        divisions: [
          {
            key: 'hymns', label: '聖詠與頌辭部', label_en: 'Hymns & Canticles',
            works: [
              { title_zh: '敘利亞聖詠集', title_orig: 'Hymns of Ephrem', author: '敘利亞的艾弗冷', era: '4 世紀', note: '被譽為「聖靈的豎琴」', link: '/fathers' },
              { title_zh: '安波羅修晨光頌', title_orig: 'Hymns of Ambrose', author: '安波羅修', era: '4 世紀', note: '為西方教會奠定格律詩傳統', link: '/fathers' },
              { title_zh: '拜占庭聖頌（孔塔基昂）', title_orig: 'Kontakia of Romanos', author: '歌詠者羅曼努斯', era: '6 世紀', note: '拜占庭最偉大的聖詠詩人', link: '/fathers' },
              { title_zh: '阿卡菲斯托斯讚美神頌', title_orig: 'Akathist Hymn', era: '6 世紀', note: '讚美道成肉身與聖母的站立詠唱長詩', link: '/fathers' },
            ],
          },
          {
            key: 'epics', label: '靈戰與敘事史詩部', label_en: 'Christian Epics',
            works: [
              { title_zh: '靈戰記', title_orig: 'Psychomachia', author: '普魯登修斯', era: '4 世紀', note: '西方第一部偉大寓言史詩，美德與邪惡擬人搏殺', link: '/fathers' },
              { title_zh: '福音史詩', title_orig: 'Evangeliorum libri IV', author: '尤文庫斯', era: '4 世紀', note: '以羅馬六步格詩體改寫四福音', link: '/fathers' },
              { title_zh: '創世記韻文史詩', title_orig: 'Metrical Genesis', note: '盎格魯-撒克遜古英語宗教長詩' },
            ],
          },
          {
            key: 'fables', label: '勸世寓言與教化文學部', label_en: 'Fables & Didactic Literature',
            works: [
              { title_zh: '黑馬牧人書', title_orig: 'Shepherd of Hermas', author: '黑馬', era: '2 世紀', note: '曾被部分早期教會視為正典的道德勸世小說', link: '/apocrypha' },
              { title_zh: '巴拉姆與約沙法傳奇', title_orig: 'Barlaam and Josaphat', era: '8 世紀', note: '釋迦牟尼生平基督教化的傳奇小說' },
            ],
          },
        ],
      },
      wai: {
        divisions: [
          {
            key: 'gnostic-hymns', label: '諾斯底讚歌部', label_en: 'Gnostic Hymns',
            works: [
              { title_zh: '〈珍珠之歌〉', title_orig: 'Hymn of the Pearl', era: '2–3 世紀', note: '《多馬行傳》中的靈魂寓言詩', link: '/apocrypha' },
              { title_zh: '〈雷：完美理智辭〉', title_orig: 'The Thunder, Perfect Mind', era: '2–3 世紀', note: '女性神格第一人稱矛盾詩', link: '/gnostic' },
            ],
          },
          {
            key: 'manichaean-hymns', label: '摩尼教讚美詩部', label_en: 'Manichaean Psalms',
            works: [
              { title_zh: '科普特摩尼教讚美詩集', title_orig: 'Coptic Manichaean Psalm-Book', era: '3–4 世紀', note: '光明王國的讚歌' },
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
      summary: '唯一能聽到「群眾回音」的迴音壁。正藏為解經講疏、節令與倫理講章、啟蒙與教理講訓、沙漠語錄與箴言；外藏為 400 年前的會堂米德拉什（拉比講疏）。',
      portal: { to: '/fathers', label: '教父著作' },
      zheng: {
        divisions: [
          {
            key: 'expository', label: '解經講疏部', label_en: 'Exegetical Homilies',
            works: [
              { title_zh: '路加福音演講錄', title_orig: 'Homilies on Luke', author: '俄利根', era: '3 世紀', note: '講道稿異常溫柔，充滿牧養關懷', link: '/fathers' },
              { title_zh: '創世記講台疏', title_orig: 'Homilies on Genesis', author: '金口若望', era: '4 世紀', note: '研究古代安提阿平民生活的寶庫', link: '/fathers' },
              { title_zh: '約翰福音講疏', title_orig: 'Tractates on the Gospel of John', author: '奧古斯丁', era: '5 世紀', note: '124 篇以淺白拉丁向北非平民解釋道成肉身', link: '/fathers' },
            ],
          },
          {
            key: 'thematic', label: '節令與倫理講章部', label_en: 'Thematic & Festal Sermons',
            works: [
              { title_zh: '創世六日講', title_orig: 'Hexaemeron', author: '大巴西略', era: '4 世紀', note: '對工匠農夫口語講述創造，古代大自然百科', link: '/fathers' },
              { title_zh: '斥富人篇', title_orig: 'Sermon to the Rich', author: '大巴西略／金口若望', era: '4 世紀', note: '古代最激進的社會正義演說', link: '/fathers' },
              { title_zh: '大眾講章集', title_orig: 'Sermones ad Populum', author: '奧古斯丁', era: '5 世紀', note: '近 400 篇即興演說，可見群眾掌聲與抱怨', link: '/fathers' },
              { title_zh: '大良節期講章', title_orig: 'Sermons of Leo the Great', author: '大良', era: '5 世紀', note: '奠定西方聖誕與復活節神學基調', link: '/fathers' },
            ],
          },
          {
            key: 'catechetical', label: '啟蒙與教理講訓部', label_en: 'Catechetical Lectures',
            works: [
              { title_zh: '慕道友啟蒙講訓', title_orig: 'Catechetical Lectures', author: '耶路撒冷的區利羅', era: '4 世紀', note: '23 篇在復活堂親口教導受洗者', link: '/fathers' },
              { title_zh: '要理講授', title_orig: 'Catechetical Homilies', author: '摩普綏提亞的提奧多若', era: '4 世紀', note: '東方教會洗禮與聖餐的口頭指導', link: '/fathers' },
            ],
          },
          {
            key: 'desert-sayings', label: '沙漠語錄與箴言部', label_en: 'Sayings of the Desert',
            works: [
              { title_zh: '沙漠父老語錄', title_orig: 'Apophthegmata Patrum', era: '4–5 世紀', note: '長老與弟子間如禪宗公案的短小對話', link: '/fathers' },
              { title_zh: '沙漠靈母箴言', title_orig: 'Sayings of the Desert Mothers', era: '4–5 世紀', note: '古代女性隱修大師的屬靈棒喝', link: '/fathers' },
            ],
          },
        ],
      },
      wai: {
        divisions: [
          {
            key: 'midrash', label: '會堂米德拉什部', label_en: 'Synagogue Midrash (to ~400 CE)',
            works: [
              { title_zh: '出埃及記法理講疏', title_orig: 'Mekhilta de-Rabbi Ishmael', era: '3–4 世紀', note: '以實瑪利學派的早期米德拉什' },
              { title_zh: '西弗雷講疏（民數記／申命記）', title_orig: 'Sifre', era: '3–4 世紀', note: '坦拿傳統的米德拉什講疏' },
              { title_zh: '大米德拉什：創世記講疏', title_orig: 'Genesis Rabbah', era: '5 世紀', note: '巴勒斯坦拉比與教父同講創世記的口頭交鋒' },
              { title_zh: '大米德拉什：利未記講疏', title_orig: 'Leviticus Rabbah', era: '5 世紀' },
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
      summary: '修院認識世界的百科全書，每一種分類都指向造物主。正藏為類書與博物志、曆算與象緯、理學與通識、哲學玄思；外藏為外教百科與占驗祕學。',
      zheng: {
        divisions: [
          {
            key: 'encyclopedia', label: '類書與博物志部', label_en: 'Encyclopedias & Bestiaries',
            works: [
              { title_zh: '自然物相志', title_orig: 'Physiologus', era: '2–4 世紀', note: '基督教動物學，將世俗動物知識神聖化，影響歐洲藝術千年' },
              { title_zh: '詞源百科志', title_orig: 'Etymologiae', author: '塞維亞的依西多祿', era: '7 世紀', note: '中世紀的維基百科', link: '/fathers' },
            ],
          },
          {
            key: 'computus', label: '曆算與象緯部', label_en: 'Computus & Cosmology',
            works: [
              { title_zh: '基督教寰宇地理志', title_orig: 'Christian Topography', author: '科斯馬斯', era: '6 世紀', note: '據會幕形狀畫平頂長方形宇宙圖' },
              { title_zh: '時間計算理法', title_orig: 'De Temporum Ratione', author: '可敬者比德', era: '8 世紀', note: '古代最偉大的復活節曆算法', link: '/fathers' },
            ],
          },
          {
            key: 'liberal-arts', label: '理學與通識部', label_en: 'Liberal Arts & Logic',
            works: [
              { title_zh: '神聖與世俗修學法要', title_orig: 'Institutiones', author: '卡西奧多羅斯', era: '6 世紀', note: '規定後世修道院必學七藝，中世紀大學制度的源頭', link: '/fathers' },
              { title_zh: '波菲利引論（基督教釋本）', title_orig: 'Isagoge (trans. Boethius)', author: '波菲利著，波愛修譯', era: '3／6 世紀', note: '基督二性辯論的邏輯學武器' },
            ],
          },
          {
            key: 'philosophy', label: '哲學玄思部', label_en: 'Christianized Philosophy',
            works: [
              { title_zh: '哲學的慰藉', title_orig: 'De Consolatione Philosophiae', author: '波愛修', era: '6 世紀', note: '純用希臘哲學探討命運苦難與上帝主權，中世紀修士最愛' },
            ],
          },
        ],
      },
      wai: {
        divisions: [
          {
            key: 'pagan-encyclopedia', label: '外教百科部', label_en: 'Pagan Encyclopedias',
            works: [
              { title_zh: '博物志', title_orig: 'Naturalis Historia', author: '老普林尼', era: '1 世紀', note: '羅馬世俗百科全書，精華選集被教會吸收' },
            ],
          },
          {
            key: 'occult', label: '占驗祕學部', label_en: 'Divination & Occult Lore',
            works: [
              { title_zh: '所羅門遺訓', title_orig: 'Testament of Solomon', era: '1–3 世紀', note: '以神戒驅使惡魔建聖殿的驅魔與召喚祕錄' },
            ],
          },
        ],
      },
    },
  ],
}
