// 阿卡德藏 —— 巴比倫與亞述（阿卡德語楔形文獻）
//
// 「阿卡德語」是一個語言的名字，不是一個王朝：薩爾貢在前 2334 年前後建阿卡德王朝，
// 王朝亡了，這個閃族語言繼續寫了兩千四百年，分出南方的巴比倫方言與北方的亞述方言。
// 本藏依語言立藏，所以阿卡德王朝、古巴比倫、亞述帝國、新巴比倫與塞琉古時代的巴比倫祭司
// 全在一藏；蘇美語寫的作品即使抄於巴比倫，歸蘇美藏。
//
// 斷限：楔形文字最後一塊可紀年的泥板，是烏魯克出土的一份天文曆書（W 22340a），
//   約公元 75–80 年。之後巴比倫的神廟沒有人能讀自己的經了。
//
// 編號：本藏學界沒有 ETCSL 那樣的統一編號。只標兩種查得到的：
//   館藏號（K＝大英博物館庫雍吉克藏品，即亞述巴尼拔圖書館）與叢刊號
//   （SAA＝新亞述國家檔案叢刊；ARM＝馬里王室檔案；BWL＝Lambert《巴比倫智慧文學》1960）。

import type { NeCanon } from './types'

const AKK = '阿卡德語'
const SB = '標準巴比倫語（文學用阿卡德語）'
const OB = '古巴比倫語'
const NA = '新亞述語'

export const AKKAD_CANON: NeCanon = {
  key: 'akkad',
  name: '阿卡德藏',
  name_en: 'Akkadian Canon (Babylonia and Assyria)',
  glyph: '巴',
  subtitle: '巴比倫與亞述——兩千四百年的楔形經典',
  scriptural: true,
  language: '阿卡德語（古阿卡德、巴比倫、亞述各方言；文學作品多用標準巴比倫語）',
  era: '約前 2350 – 公元 80',
  terminus: '止於楔形文字的最後一塊泥板：烏魯克出土的天文曆書，約公元 75–80 年。',
  columns: { orig: 'available', en: 'available', zh: 'none' },
  summary:
    '美索不達米亞宗教的主體。創世史詩在新年節對著馬杜克神像誦唸；吉爾伽美什史詩在書吏學校傳抄了一千五百年；'
    + '驅魔師的咒文、占卜師的肝卜手冊與天象兆書，則是神廟每天實際在用的「經」。'
    + '亞述巴尼拔在尼尼微收集的王家圖書館（前 7 世紀）保存了其中大半——圖書館在前 612 年焚毀，大火把泥板燒得更硬。',
  volumes: [
    {
      key: 'epics',
      sigil: '巴一',
      name: '史詩與神話',
      name_en: 'Epics and Myths',
      era: '約前 1900 – 前 700',
      summary:
        '創世、洪水、冥府、王權與文明的來歷。這些作品大多有古巴比倫版與第一千紀的「標準版」兩層，'
        + '中間經過改寫、增刪甚至換掉主角（亞述版創世史詩把馬杜克換成亞述爾）。',
      divisions: [
        {
          key: 'creation-flood',
          label: '創世與洪水',
          label_en: 'Creation and Flood',
          texts: [
            { slug: 'enuma-elish', title_zh: '埃努瑪‧埃利什（天之高兮）', title_orig: 'Enūma eliš', era: '約前 1100（尼布甲尼撒一世迎回馬杜克神像前後，爭議）', copies: '新亞述與新巴比倫抄本為主', language: SB, extent: '七塊泥板，約 1,100 行', note: '「天之上未名、地之下未喚」。馬杜克殺原水之母提阿瑪特、剖屍為天地，以叛神金古之血造人，眾神為他建巴比倫，頌其五十個名號。', bible: '創 1（深淵 təhôm 與提阿瑪特同源）', xref: ['基督教大藏經‧前藏（埃努瑪‧埃利什）'], seealso: ['akitu', 'damascius-principles'] },
            { slug: 'enuma-elish-assyrian', title_zh: '亞述版創世史詩', title_orig: 'Assyrian recension of Enūma eliš', era: '前 8–7 世紀', copies: '亞述城出土抄本', language: SB, status: 'fragment', note: '把馬杜克的名字換成亞述爾——帝國換了，創世主就換了。' },
            { slug: 'atrahasis', title_zh: '阿特拉哈西斯', title_orig: 'Atra-ḫasīs', era: '約前 1700（古巴比倫）', copies: '古巴比倫本（伊皮可—阿雅抄，約前 1635）與新亞述本', language: OB, extent: '三塊泥板，約 1,245 行', note: '低階神祇罷工，眾神殺一神以其血肉和泥造人；人太吵，神先降瘟疫、旱災，終降洪水。智者阿特拉哈西斯得恩基暗示造船。創世—洪水連成一線的「太古史」。', bible: '創 1–9', xref: ['基督教大藏經‧前藏（阿特拉哈西斯史詩）'], seealso: ['sumerian-flood', 'gilgamesh-sb'] },
            { slug: 'eridu-founding', title_zh: '馬杜克創世（埃利都的奠立）', title_orig: 'The Founding of Eridu / Creation of the World by Marduk', era: '新巴比倫抄本', language: '蘇美—阿卡德雙語', status: 'whole', note: '「萬地皆海」之時，馬杜克在水面上鋪蘆葦、填土而造陸地。一段插在驅魔咒文開頭的創世記。', bible: '創 1:2' },
            { slug: 'dunnu-theogony', title_zh: '敦努神譜', title_orig: 'Theogony of Dunnu', siglum: 'BM 74329', era: '新巴比倫抄本', language: AKK, status: 'fragment', note: '神祇世代相弒、娶母娶姊而繼位——與赫梯的天界王權神話、希臘的赫西俄德神譜同一類型。', seealso: ['kumarbi-kingship'] },
          ],
        },
        {
          key: 'gilgamesh',
          label: '吉爾伽美什',
          label_en: 'Gilgamesh',
          texts: [
            { slug: 'gilgamesh-ob', title_zh: '吉爾伽美什史詩（古巴比倫版）', title_orig: 'Old Babylonian Gilgamesh (Šūtur eli šarrī)', era: '約前 1800', language: OB, status: 'fragment', note: '首行「超越諸王者」。賓館女主人西杜莉勸吉爾伽美什：「你所求的永生你找不到……讓你的妻子在你懷中歡喜。」此段標準版刪去。', bible: '傳 9:7–9' },
            { slug: 'gilgamesh-sb', title_zh: '吉爾伽美什史詩（標準版）', title_orig: 'Ša naqba īmuru ("He who saw the Deep")', author: '傳為辛—勒克—烏寧尼編', era: '約前 1200', copies: '以亞述巴尼拔圖書館抄本為主，今仍有約五分之一缺文', language: SB, extent: '十二塊泥板，約 3,000 行', note: '「那見過深淵的人」。友誼、死亡與求永生；第十一塊泥板烏納皮什提親述洪水，放出鴿子、燕子、烏鴉探水。1872 年喬治‧史密斯在大英博物館讀出此段，震動英國。', bible: '創 6–9（放鳥探水）', xref: ['基督教大藏經‧前藏（吉爾伽美什史詩）'], seealso: ['gilgamesh-netherworld'] },
          ],
        },
        {
          key: 'netherworld',
          label: '冥府',
          label_en: 'Netherworld',
          texts: [
            { slug: 'ishtar-descent', title_zh: '伊絲塔下冥府', title_orig: 'Ištar\'s Descent to the Netherworld', era: '中巴比倫成書', copies: '新亞述（尼尼微、亞述城）抄本', language: SB, extent: '約 140 行', note: '蘇美〈伊南娜入冥府〉的阿卡德語短本。女神下到「無返之地」，地上萬物停止交配；結尾提到杜牧茲節的哀哭與歸來。', seealso: ['inana-descent'] },
            { slug: 'nergal-ereshkigal', title_zh: '涅伽爾與埃列什基伽爾', title_orig: 'Nergal and Ereškigal', copies: '阿瑪納抄本（前 14 世紀）與蘇丹特佩抄本（前 7 世紀）', language: AKK, note: '天神之子下到冥府，與冥界女王成婚而成為冥府之主。兩個版本相隔七百年，情節差異極大。' },
            { slug: 'underworld-vision', title_zh: '亞述王子冥府夢', title_orig: 'The Underworld Vision of an Assyrian Prince', siglum: 'SAA 3 32', era: '前 7 世紀', language: NA, status: 'fragment', note: '王子庫瑪在夢中被帶到冥府，見到十五個怪異的冥界之神與涅伽爾的審判。古代近東唯一一份第一人稱的「遊地獄」。' },
          ],
        },
        {
          key: 'heroes',
          label: '英雄與智者',
          label_en: 'Heroes and Sages',
          texts: [
            { slug: 'anzu', title_zh: '安祖神話', title_orig: 'Anzû', copies: '古巴比倫本與標準版', language: SB, extent: '三塊泥板', note: '獅首巨鳥盜走恩利爾的天命泥板，宇宙失序；尼努爾塔奉命奪回。', seealso: ['lugalbanda-anzud'] },
            { slug: 'etana', title_zh: '埃塔納', title_orig: 'Etana', copies: '古巴比倫、中亞述、新亞述三版', language: AKK, status: 'fragment', note: '無子的王乘鷹升天求「生子之草」。結局佚失。' },
            { slug: 'adapa', title_zh: '阿達帕', title_orig: 'Adapa', copies: '阿瑪納抄本與新亞述抄本', language: AKK, status: 'fragment', note: '埃利都的智者被召上天庭，聽了恩基的話拒食天神給的「生命之餅」與「生命之水」，錯失了永生。', bible: '創 3:22 生命樹' },
            { slug: 'erra', title_zh: '埃拉史詩', title_orig: 'Erra and Išum', author: '卡卜提—伊拉尼—馬杜克（自署，稱受夢中啟示一字不改）', era: '約前 8 世紀', language: SB, extent: '五塊泥板', note: '瘟疫與戰禍之神趁馬杜克離開寶座而肆虐巴比倫。作者聲稱全文是夜間所見異象——近東極少數由作者自稱啟示的文本，泥板本身被當護身符掛在屋裡。' },
            { slug: 'sargon-birth', title_zh: '薩爾貢出生傳說', title_orig: 'The Sargon Birth Legend', era: '新亞述抄本（前 8–7 世紀）', language: NA, status: 'fragment', note: '「我母親是女祭司，懷了我暗中生下，把我放在蘆葦箱裡、以瀝青封口，丟進河中。」', bible: '出 2:1–10 摩西' },
            { slug: 'cuthean-legend', title_zh: '納拉姆辛的庫塔傳說', title_orig: 'The Cuthean Legend of Naram-Sîn', copies: '古巴比倫至新亞述', language: SB, note: '王不聽占卜而出戰，三次全軍覆沒。教訓：不要違逆神兆。', seealso: ['curse-agade'] },
          ],
        },
      ],
    },
    {
      key: 'prayers',
      sigil: '巴二',
      name: '頌詩與禱文',
      name_en: 'Hymns and Prayers',
      era: '約前 1800 – 前 3 世紀',
      summary:
        '「舉手禱」（šuila）是巴比倫最常見的禱文體：讚美神名、陳述苦況、求赦求醫、許願讚美，與詩篇的悲歌體結構相同。'
        + '本卷另收神殿大頌與晚期把眾神視為馬杜克各個面向的「準一神論」頌詩。',
      divisions: [
        {
          key: 'hymns',
          label: '大頌',
          label_en: 'Great Hymns',
          texts: [
            { slug: 'shamash-hymn', title_zh: '沙馬什大頌', title_orig: 'The Great Hymn to Šamaš', siglum: 'BWL pp. 121–138', copies: '新亞述與新巴比倫抄本', language: SB, extent: '約 200 行', note: '太陽神照見萬邦，連異族、旅人、海上的人都在他看顧之下；收賄的法官、改秤的商人逃不過他。', bible: '詩 19；詩 139' },
            { slug: 'gula-hymn', title_zh: '布盧薩—拉比的古拉頌', title_orig: 'Gula Hymn of Bulluṭsa-rabi', copies: '新亞述', language: SB, note: '醫療女神第一人稱自述，輪流以十位女神之名出現。' },
            { slug: 'marduk-syncretistic', title_zh: '眾神即馬杜克', title_orig: 'Syncretistic hymn: the gods as aspects of Marduk', siglum: 'CT 24 50（BM 47406）', era: '新巴比倫', language: SB, status: 'fragment', note: '「尼努爾塔是耕作的馬杜克，涅伽爾是戰爭的馬杜克，沙馬什是公義的馬杜克……」一張把眾神逐一化約為一神屬性的對照表。' },
            { slug: 'ishtar-prayer', title_zh: '伊絲塔大禱', title_orig: 'Great Prayer to Ištar (šuila Ištar 2)', copies: '新巴比倫抄本', language: SB, extent: '約 110 行', note: '「我向你祈求，眾女主之主……我的神與女神向我發怒，求你看顧我。」' },
            { slug: 'prayers-gods-night', title_zh: '夜間諸神禱', title_orig: 'Prayer to the Gods of the Night', copies: '古巴比倫', language: OB, note: '占卜師在夜裡向星辰禱告：「大人們入睡了，門閂上了……求你們在我所獻的羊羔上顯示真實。」' },
          ],
        },
        {
          key: 'shuila',
          label: '舉手禱與悔罪禱',
          label_en: 'Šuila and Penitential Prayers',
          texts: [
            { slug: 'shuila-corpus', title_zh: '舉手禱集', title_orig: 'Šu-ila prayers', copies: '中巴比倫至塞琉古', language: SB, extent: '逾百篇', note: '向各神的個人禱文，常配合驅魔儀式一起使用。', bible: '詩篇的悲歌體' },
            { slug: 'dingirsadabba', title_zh: '平息神怒禱', title_orig: 'Dingir-šà-dib-ba incantations', copies: '新亞述', language: SB, note: '「我不知道我犯了什麼罪，我吃了不該吃的、踏了不該踏的……」為不知名之罪求赦。', bible: '詩 19:12「誰能知道自己的錯失？」' },
          ],
        },
      ],
    },
    {
      key: 'wisdom',
      sigil: '巴三',
      name: '智慧書與神義論',
      name_en: 'Wisdom and Theodicy',
      era: '約前 1700 – 前 7 世紀',
      summary: '為什麼義人受苦？神的心意能不能知道？巴比倫智慧文學的大問題與約伯記、傳道書完全相同，答案卻不一樣。',
      divisions: [
        {
          key: 'sufferer',
          label: '受苦的義人',
          label_en: 'The Righteous Sufferer',
          texts: [
            { slug: 'ludlul', title_zh: '我要讚美智慧之主（盧德魯）', title_orig: 'Ludlul bēl nēmeqi', siglum: 'BWL pp. 21–62', era: '約前 1300–1100（加喜特時代）', copies: '新亞述與新巴比倫', language: SB, extent: '四塊泥板，約 480 行', note: '貴族舒比—梅希—沙坎無故失勢、病重、被眾人唾棄，終得馬杜克垂憐痊癒。「誰能明白天上諸神的旨意？」', bible: '約伯記' },
            { slug: 'babylonian-theodicy', title_zh: '巴比倫神義論', title_orig: 'The Babylonian Theodicy', siglum: 'BWL pp. 63–91', author: '薩吉勒—基納姆—烏比布（藏頭詩自署）', era: '約前 1000', language: SB, extent: '27 節，每節 11 行', note: '受苦者與友人輪番對話——每節首字連起來是作者的名字與「驅魔師、敬拜神與王」。結構與約伯記的對話最接近。', bible: '約伯記 3–31' },
            { slug: 'dialogue-pessimism', title_zh: '主僕對話（悲觀對話）', title_orig: 'Dialogue of Pessimism', siglum: 'BWL pp. 139–149', era: '約前 1000', language: SB, note: '主人每提一個主意僕人都附和，主人改主意僕人也附和。最後主人問什麼才是好，僕人說：「扭斷我的脖子和你的脖子，丟進河裡。」', bible: '傳道書' },
          ],
        },
        {
          key: 'counsels',
          label: '訓言',
          label_en: 'Counsels',
          texts: [
            { slug: 'counsels-wisdom', title_zh: '智慧箴言', title_orig: 'Counsels of Wisdom', siglum: 'BWL pp. 96–107', copies: '新亞述', language: SB, note: '「不要以惡報惡，向行惡的人行善。」', bible: '箴 25:21–22；羅 12:17–21' },
            { slug: 'shupe-ameli', title_zh: '舒佩—阿美里訓言', title_orig: 'Instructions of Šūpê-amēli', copies: '烏加里特、埃馬爾、哈圖沙出土', language: '阿卡德語（另有赫梯語譯本）', note: '父親教子的訓言，在敘利亞與安納托利亞流通——書吏學校的國際教材。' },
            { slug: 'advice-prince', title_zh: '王者之鑑', title_orig: 'Advice to a Prince', siglum: 'BWL pp. 110–115', era: '約前 8 世紀', language: SB, note: '以占卜兆辭體寫成：「若王不聽公義，他的國將亂……」' },
            { slug: 'ahiqar-akkadian', title_zh: '阿希卡爾的原型（阿哈—烏卡）', title_orig: 'Aba-Enlil-dari (Aḫu\'aqar) in the Uruk apkallu list', siglum: 'W 20030,7', era: '塞琉古時代泥板', language: AKK, status: 'fragment', note: '烏魯克的「智者表」記載以撒哈頓的大臣「亞蘭人稱之為阿希卡爾」——證實亞蘭文《阿希卡爾》的主角在楔形傳統裡有據。', seealso: ['ahiqar'] },
          ],
        },
      ],
    },
    {
      key: 'exorcism',
      sigil: '巴四',
      name: '驅魔與儀式',
      name_en: 'Exorcism and Ritual',
      era: '約前 1800 – 前 1 世紀',
      summary:
        '驅魔師（āšipu）是巴比倫神廟的大宗職業，他們的「經」是成系列的咒文與儀式手冊：焚燒巫師人像、'
        + '解除不明之罪、以水淨口使新神像「活過來」。宗教與醫療在此是同一門學問。',
      divisions: [
        {
          key: 'series',
          label: '咒文系列',
          label_en: 'Incantation Series',
          texts: [
            { slug: 'maqlu', title_zh: '焚燒（馬克盧）', title_orig: 'Maqlû', era: '第一千紀定型', copies: '新亞述與新巴比倫', language: SB, extent: '八塊咒文泥板＋一塊儀式泥板', note: '一整夜的反巫術儀式：做出巫師的蠟像與泥像逐一焚燒，到黎明時把灰燼倒掉。', seealso: ['udug-hul'] },
            { slug: 'shurpu', title_zh: '焚燒（舒爾普）', title_orig: 'Šurpu', era: '第一千紀定型', copies: '新亞述與新巴比倫', language: SB, extent: '九塊泥板', note: '將病人的罪過「剝」在洋蔥、椰棗、羊毛上投火燒掉。第二塊泥板列出上百條可能犯下的罪——巴比倫的罪的清單。', bible: '利 16 贖罪日' },
            { slug: 'lamashtu', title_zh: '拉瑪什圖咒', title_orig: 'Lamaštu series', copies: '古巴比倫至新巴比倫；另有大量護身銅牌', language: AKK, note: '驅逐專害產婦與嬰兒的女魔。' },
            { slug: 'namburbi', title_zh: '消兆儀式（南布比）', title_orig: 'Namburbi rituals', copies: '新亞述與新巴比倫', language: SB, note: '遇到凶兆時用來「解除」它的儀式——徵兆不是命定，可以化解。', seealso: ['shumma-alu'] },
          ],
        },
        {
          key: 'temple-rituals',
          label: '神廟儀式',
          label_en: 'Temple Rituals',
          texts: [
            { slug: 'mis-pi', title_zh: '洗口儀式', title_orig: 'Mīs pî (Mouth-washing ritual)', era: '第一千紀定型', copies: '尼尼微與巴比倫抄本', language: '蘇美—阿卡德雙語咒文＋阿卡德語儀程', note: '新雕好的神像經河邊、果園、神廟三處儀式，工匠斬斷自己的手（象徵性）宣告「我沒有造它」，神像才成為神。', bible: '賽 44:9–20 譏刺造像', seealso: ['opening-of-mouth'] },
            { slug: 'akitu', title_zh: '巴比倫新年節（阿基圖）儀程', title_orig: 'Akītu Festival ritual of Babylon', era: '塞琉古時代抄本，節期可溯至前三千紀', language: AKK, provenance: '巴比倫埃薩吉拉神廟', status: 'fragment', note: '第四日誦唸《埃努瑪‧埃利什》全文；第五日大祭司掌摑國王，王流淚才算神喜悅。', xref: ['基督教大藏經‧前藏（巴比倫新年節神廟儀程；天之高兮）'], seealso: ['enuma-elish'] },
            { slug: 'uruk-rituals', title_zh: '烏魯克塞琉古時代儀式文', title_orig: 'Seleucid ritual texts from Uruk', era: '前 3–2 世紀', language: AKK, provenance: '烏魯克', status: 'fragment', note: '天神安努的每日四餐菜單、夜間火炬儀式、神廟重建時拆舊牆的哀歌程序——楔形宗教最晚期的實錄。' },
            { slug: 'substitute-king', title_zh: '代身王儀式', title_orig: 'Šar pūḫi (Substitute King ritual)', copies: '新亞述書信與儀式文', language: NA, status: 'fragment', note: '月食預示國王將死時，立一個平民為王百日，期滿處死，真王得免。以撒哈頓在位時舉行過數次。' },
          ],
        },
      ],
    },
    {
      key: 'divination',
      sigil: '巴五',
      name: '占卜',
      name_en: 'Divination',
      era: '約前 1900 – 公元 80',
      summary:
        '神不說話，神「寫」——寫在羊的肝臟上、天空中、畸形的胎兒上、城裡的日常瑣事裡。'
        + '巴比倫占卜是一套龐大的「若……則……」條文系統，形式與漢摩拉比法典完全相同。最後一塊楔形泥板是天文書。',
      divisions: [
        {
          key: 'omen-series',
          label: '兆書',
          label_en: 'Omen Series',
          texts: [
            { slug: 'barutu', title_zh: '肝卜書（巴魯圖）', title_orig: 'Bārûtu', copies: '古巴比倫泥板肝模型；新亞述系列約百塊泥板', language: AKK, note: '綿羊肝臟各部位的形狀所示之兆。占卜師（bārû）是國家大事必諮的專業。', xref: ['希臘羅馬大藏經 羅馬卷 IV（皮亞琴察肝模型）'] },
            { slug: 'enuma-anu-enlil', title_zh: '天兆書（埃努瑪‧阿努‧恩利爾）', title_orig: 'Enūma Anu Enlil', copies: '新亞述', language: SB, extent: '約 70 塊泥板，七千條兆', note: '月、日、氣象、星辰之兆。金星泥板記錄了阿米薩杜卡王二十一年間金星的出沒。', xref: ['基督教大藏經‧前藏（埃努瑪‧阿努‧恩利爾徵兆系列）'] },
            { slug: 'shumma-alu', title_zh: '城中兆書（舒馬‧阿盧）', title_orig: 'Šumma ālu', copies: '新亞述', language: SB, extent: '逾百塊泥板', note: '「若城建在高處……」「若蛇落在人身上……」日常生活的一切都可能是神的訊息。' },
            { slug: 'shumma-izbu', title_zh: '異胎兆書', title_orig: 'Šumma izbu', copies: '新亞述', language: SB, extent: '24 塊泥板', note: '人與牲畜畸形胎兒之兆。' },
            { slug: 'sakikku', title_zh: '診斷兆書（薩基庫）', title_orig: 'Sakikkû (Diagnostic Handbook)', author: '博爾西帕的以撒基—金—阿皮（編）', era: '約前 11 世紀', copies: '新亞述與新巴比倫', language: SB, extent: '40 塊泥板', note: '「若驅魔師往病人家去的路上看見黑狗……」從路上所見到病人症狀，一步步推出是哪位神降的病。' },
            { slug: 'dream-book-akk', title_zh: '解夢書（夢之神）', title_orig: 'Iškar Zaqīqu (Assyrian Dream Book)', copies: '新亞述', language: SB, note: '「若人夢見自己飛……」' },
          ],
        },
        {
          key: 'astronomy',
          label: '天文',
          label_en: 'Astronomy',
          texts: [
            { slug: 'mul-apin', title_zh: '犁星（星辰總表）', title_orig: 'MUL.APIN', era: '約前 1000 前後彙編', copies: '新亞述至新巴比倫', language: SB, extent: '兩塊泥板', note: '全天星表、各星升起日期、閏月規則。以星為神，天文即神學。' },
            { slug: 'astronomical-diaries', title_zh: '天文日誌', title_orig: 'Astronomical Diaries', era: '前 652 – 前 61', language: AKK, provenance: '巴比倫', status: 'fragment', extent: '殘存數百塊', note: '巴比倫天文祭司連續六百年每夜記錄天象、物價、河水、大事——亞歷山大進城、高加米拉之戰都在其中。' },
            { slug: 'last-cuneiform', title_zh: '最後一塊楔形泥板', title_orig: 'Astronomical almanac W 22340a', siglum: 'W 22340a', era: '約公元 75–80 年', language: AKK, provenance: '烏魯克', status: 'fragment', note: '一份預告行星位置的曆書。此後再也沒有人用楔形文字寫過任何東西。' },
          ],
        },
      ],
    },
    {
      key: 'prophecy',
      sigil: '巴六',
      name: '先知與預言',
      name_en: 'Prophecy',
      era: '約前 1780 – 前 3 世紀',
      summary:
        '近東也有先知：馬里與亞述的「出神者」「呼喊者」在神廟中被神附身，把神的話帶給國王。'
        + '另有一類阿卡德語「預言」是事後寫成、預告諸王善惡的文書，文體上接近但以理書。',
      divisions: [
        {
          key: 'prophets',
          label: '先知神諭',
          label_en: 'Prophetic Oracles',
          texts: [
            { slug: 'mari-prophecies', title_zh: '馬里先知書信', title_orig: 'Prophetic texts from Mari', siglum: 'ARM 26 191–240 等', era: '約前 1780（辛里—利姆王）', language: OB, provenance: '馬里（敘利亞特爾哈里里）', status: 'fragment', extent: '約五十則', note: '官員向國王轉報：某神廟的「出神者」被達干神附身說話。並附上先知的一綹頭髮和衣角，供國王另行占卜查驗真偽。', bible: '申 18:21–22 先知的驗證' },
            { slug: 'assyrian-prophecies', title_zh: '亞述先知書', title_orig: 'Assyrian Prophecies', siglum: 'SAA 9', era: '前 681 – 前 668（以撒哈頓、亞述巴尼拔）', language: NA, provenance: '尼尼微', status: 'fragment', note: '阿貝拉的伊絲塔藉女先知說：「不要怕，以撒哈頓！我是阿貝拉的伊絲塔……」與以賽亞書「不要懼怕」神諭體幾乎同式。', bible: '賽 41:10–14；賽 43–44' },
          ],
        },
        {
          key: 'literary',
          label: '文學預言',
          label_en: 'Literary Predictive Texts',
          texts: [
            { slug: 'marduk-prophecy', title_zh: '馬杜克預言', title_orig: 'Marduk Prophecy', copies: '新亞述抄本', language: SB, status: 'fragment', note: '馬杜克神像三次離開巴比倫（往赫梯、亞述、埃蘭），以神的第一人稱自述流亡，並預言一位王將迎他回來。', bible: '結 10–11 神的榮耀離城' },
            { slug: 'uruk-prophecy', title_zh: '烏魯克預言', title_orig: 'Uruk Prophecy', siglum: 'W 22307,7', copies: '塞琉古時代（烏魯克）', language: SB, status: 'fragment', note: '一連串壞王之後將出一位王，他的王朝「如神一樣永遠」。' },
            { slug: 'dynastic-prophecy', title_zh: '王朝預言', title_orig: 'Dynastic Prophecy', siglum: 'BM 40623', copies: '塞琉古時代', language: SB, status: 'fragment', note: '以預言體寫亞述亡、波斯興、亞歷山大勝——成書於希臘化時代，體例與但以理書 11 章同類。', bible: '但 11' },
          ],
        },
      ],
    },
    {
      key: 'royal',
      sigil: '巴七',
      name: '王室銘文與神權',
      name_en: 'Royal Inscriptions and Divine Kingship',
      era: '約前 2300 – 前 539',
      summary:
        '王的碑文開口就是神學：神揀選王、神授法律、神因王的罪而棄城、神因王的虔敬而回心轉意。'
        + '本卷只收宗教意義明確者；純軍事年鑑不收。',
      divisions: [
        {
          key: 'law',
          label: '神授律法',
          label_en: 'Divinely Given Law',
          texts: [
            { slug: 'hammurabi', title_zh: '漢摩拉比法典（序與跋）', title_orig: 'Laws of Hammurabi, prologue and epilogue', siglum: 'Louvre Sb 8', era: '約前 1754', language: OB, provenance: '蘇薩出土（埃蘭人戰利品）；羅浮宮藏', status: 'inscription', extent: '282 條', note: '碑頂浮雕是沙馬什授王權杖；序言說眾神召漢摩拉比「使公義顯於全地，滅除惡人，使強者不欺凌弱者」。收其序跋的神學，不收法條本身。', bible: '出 21–23 約書（同態復仇、牛觸人等條文平行）' },
          ],
        },
        {
          key: 'gods-cities',
          label: '神與城',
          label_en: 'Gods and Cities',
          texts: [
            { slug: 'esarhaddon-babylon', title_zh: '以撒哈頓巴比倫重建銘', title_orig: 'Esarhaddon\'s Babylon Inscriptions', era: '約前 680', language: SB, status: 'inscription', note: '馬杜克發怒，定巴比倫荒廢七十年；後回心轉意，把楔形數字「70」翻轉成「11」，十一年後便命以撒哈頓重建。', bible: '耶 25:11–12；29:10 七十年' },
            { slug: 'nabonidus-harran', title_zh: '那波尼度哈蘭碑', title_orig: 'Harran Stelae of Nabonidus', era: '約前 545', language: SB, provenance: '哈蘭', status: 'inscription', note: '巴比倫末代王獨尊哈蘭的月神辛，冷落馬杜克，十年不回巴比倫過新年節。' },
            { slug: 'adad-guppi', title_zh: '阿達德—古比自傳碑', title_orig: 'Adad-guppi Stela', era: '約前 547', language: SB, provenance: '哈蘭', status: 'inscription', note: '那波尼度之母自述活到一百零四歲，一生事奉月神。古代近東罕見的女性自傳。' },
            { slug: 'verse-account', title_zh: '那波尼度詩體控訴文', title_orig: 'Verse Account of Nabonidus', siglum: 'BM 38299', era: '前 539 之後', language: SB, status: 'fragment', note: '巴比倫祭司在波斯征服後攻擊前王褻瀆馬杜克。', bible: '但 4–5' },
            { slug: 'cyrus-cylinder', title_zh: '居魯士圓柱', title_orig: 'Cyrus Cylinder', siglum: 'BM 90920', era: '前 539 之後', language: SB, provenance: '巴比倫；大英博物館藏', status: 'inscription', note: '馬杜克尋找一位公義的王，揀選了居魯士，讓他兵不血刃進入巴比倫，並把各地神像送回原處。', bible: '賽 44:28–45:1；拉 1:1–4', xref: ['祆教經典‧王室銘文附錄（阿契美尼德銘文互見）'] },
          ],
        },
        {
          key: 'chronicles',
          label: '宗教編年',
          label_en: 'Religious Chronicles',
          texts: [
            { slug: 'weidner-chronicle', title_zh: '魏德納編年（埃薩吉拉編年）', title_orig: 'Weidner Chronicle', copies: '新巴比倫', language: SB, status: 'fragment', note: '把歷代王朝的興亡一律解釋為是否敬奉巴比倫馬杜克神廟的魚供——以祭儀為準繩的申命記式史觀。', bible: '列王紀的申命記史觀' },
          ],
        },
      ],
    },
    {
      key: 'scholarship',
      sigil: '巴八',
      name: '神表與神學註釋',
      name_en: 'God Lists and Theological Commentary',
      era: '約前 2600 – 前 3 世紀',
      summary: '書吏把眾神編成清單、把神名拆字解經——巴比倫的神學不寫成論文，寫成詞表與註釋。',
      divisions: [
        {
          key: 'god-lists',
          label: '神表',
          label_en: 'God Lists',
          texts: [
            { slug: 'an-anum', title_zh: '安＝阿努姆神表', title_orig: 'An = Anum', era: '中巴比倫成形', copies: '新亞述與新巴比倫', language: '蘇美—阿卡德', extent: '七塊泥板，約兩千個神名', note: '依神族與神廟的等級排列全部神祇——萬神殿的官方編制表。' },
            { slug: 'marduk-50-names', title_zh: '馬杜克五十名註', title_orig: 'Commentary on the Fifty Names of Marduk', copies: '新亞述', language: AKK, status: 'fragment', note: '把《埃努瑪‧埃利什》第六、七塊泥板的五十個名號逐字拆解成神學意義——拆字解經法。', seealso: ['enuma-elish'] },
            { slug: 'mystical-commentaries', title_zh: '祕傳神學註釋', title_orig: 'Mystical and cultic commentaries', copies: '新亞述至塞琉古', language: AKK, status: 'fragment', note: '「此為祕密，識者可示識者，不識者不可見」——儀式動作逐一對應神話事件的註解。' },
          ],
        },
      ],
    },
    {
      key: 'early-semitic',
      sigil: '巴九',
      name: '早期閃族文獻',
      name_en: 'Early Semitic Texts',
      era: '約前 2500 – 前 2000',
      summary: '阿卡德語成為帝國語言之前，敘利亞的埃卜拉與兩河流域北部已用楔形文字寫閃族語。最早的閃族讚歌在此。',
      divisions: [
        {
          key: 'ebla',
          label: '埃卜拉與早期阿卡德',
          label_en: 'Ebla and Old Akkadian',
          columns: { orig: 'available', en: 'copyright', zh: 'none' },
          texts: [
            { slug: 'ebla-shamash-hymn', title_zh: '埃卜拉與阿布薩拉比赫的沙馬什頌', title_orig: 'Hymn to Šamaš from Ebla and Abū Ṣalābīḫ', era: '約前 2500', language: '早期閃族語（埃卜拉語／古阿卡德語）', provenance: '埃卜拉（敘利亞）與阿布薩拉比赫（伊拉克）', status: 'fragment', note: '相距一千公里的兩地出土同一首讚歌——現存最古的閃族語文學作品。' },
            { slug: 'ebla-archive', title_zh: '埃卜拉王室檔案中的祭祀紀錄', title_orig: 'Ebla cultic and offering texts', era: '約前 2400 – 前 2300', language: '埃卜拉語', provenance: '埃卜拉', status: 'fragment', extent: '檔案共約 17,000 件殘片', note: '向達干、哈達德、庫拉等神的獻祭紀錄。曾被誤傳提到「雅威」與所多瑪，學界已否定。' },
          ],
        },
      ],
    },
  ],
}
