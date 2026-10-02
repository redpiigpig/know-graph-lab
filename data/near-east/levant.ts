// 迦南與亞蘭藏 —— 鐵器時代黎凡特：腓尼基、布匿、亞蘭、摩押、亞捫、以色列與猶大
//
// 烏加里特亡後，迦南宗教在腓尼基諸城（推羅、西頓、比布魯斯）延續，又隨腓尼基人航遍地中海，
// 在迦太基成為布匿宗教，一直到羅馬時代。內陸的亞蘭諸國、摩押、亞捫各奉其國神。
//
// 🚨 以色列與猶大的**銘文**收在本藏，希伯來聖經不收：
//   聖經屬猶太教（/scripture-canon 的猶太教卡，規劃中），且已經過正典化的篩選與改寫；
//   銘文則是未經篩選的當時實物——它們顯示鐵器時代的以色列人寫「雅威與他的亞舍拉」，
//   正是先知所譴責的那種宗教。兩者是同一個民族的兩份證據，互見不合併。
//
// 斷限：止於羅馬時代。帕爾米拉約 273 年被奧勒良攻陷、哈特拉約 240 年被薩珊攻陷，
//   亞蘭語多神信仰的大型神廟銘文隨之終止；埃德薩的異教銘文止於 2 世紀末該城王室改宗。
//
// 編號：KAI＝Donner–Röllig《迦南與亞蘭銘文集》；TAD＝Porten–Yardeni《古埃及亞蘭文獻教本》。

import type { NeCanon } from './types'

const PHO = '腓尼基語'
const PUN = '布匿語'
const ARA = '亞蘭語'
const HEB = '古希伯來語'

export const LEVANT_CANON: NeCanon = {
  key: 'levant',
  name: '迦南與亞蘭藏',
  name_en: 'Canaanite and Aramaic Canon',
  glyph: '迦',
  subtitle: '腓尼基、布匿、亞蘭、摩押與以色列的銘文',
  scriptural: true,
  language: '腓尼基語、布匿語、亞蘭語、摩押語、亞捫語、古希伯來語',
  era: '約前 1000 – 公元 3 世紀',
  terminus: '帕爾米拉 273 年陷落、哈特拉約 240 年陷落，亞蘭語多神信仰的神廟銘文隨之終止。',
  columns: { orig: 'available', en: 'available', zh: 'none' },
  summary:
    '這一藏幾乎全是刻在石頭、金屬、灰泥牆上的短銘文——沒有一部長篇神話傳世。'
    + '但它們是第一手的：摩押王為基抹把以色列人「盡行殺滅」、亞蘭先知巴蘭在灰泥牆上見異象、'
    + '以色列人在西奈旅站的陶甕上寫「願撒馬利亞的雅威與他的亞舍拉賜福你」、'
    + '耶路撒冷墓中的銀卷刻著民數記的祭司祝福。舊約的世界，從它的鄰居與它自己的地底下看。',
  volumes: [
    {
      key: 'phoenician',
      sigil: '迦一',
      name: '腓尼基與布匿',
      name_en: 'Phoenician and Punic',
      era: '約前 1000 – 公元 2 世紀',
      summary:
        '比布魯斯的女神「比布魯斯之女主」、西頓的醫神埃什蒙、推羅的城神麥勒卡特、迦太基的塔尼特與巴力‧哈蒙。'
        + '祭稅表列出每一種祭牲祭司可得多少，與利未記的祭祀條例逐項可比；迦太基「托斐特」的嬰孩獻祭碑則是本藏最具爭議的材料。',
      divisions: [
        {
          key: 'royal',
          label: '王室與墓葬銘文',
          label_en: 'Royal and Funerary Inscriptions',
          texts: [
            { slug: 'ahiram', title_zh: '阿希蘭石棺銘', title_orig: 'Ahiram sarcophagus', siglum: 'KAI 1', era: '約前 1000', language: PHO, provenance: '比布魯斯；貝魯特國家博物館藏', status: 'inscription', note: '現存最早的成篇腓尼基字母銘文：「若有王、總督或將軍上來攻比布魯斯、揭開此棺，願他的王杖折斷、王座傾覆。」' },
            { slug: 'yehimilk', title_zh: '耶希米勒克建廟銘', title_orig: 'Yehimilk inscription', siglum: 'KAI 4', era: '約前 950', language: PHO, provenance: '比布魯斯', status: 'inscription', note: '「願巴力沙門與比布魯斯之女主延長耶希米勒克的年日，因他是公義正直的王。」' },
            { slug: 'yehawmilk', title_zh: '耶哈米勒克碑', title_orig: 'Yehawmilk stela', siglum: 'KAI 10', era: '約前 450（波斯時代）', language: PHO, provenance: '比布魯斯；羅浮宮藏', status: 'inscription', note: '王向「比布魯斯之女主」獻銅祭壇與金門，碑頂浮雕女神作埃及哈索爾的樣子。' },
            { slug: 'tabnit', title_zh: '塔布尼特石棺銘', title_orig: 'Tabnit sarcophagus', siglum: 'KAI 13', era: '約前 5 世紀', language: PHO, provenance: '西頓；伊斯坦堡考古博物館藏', status: 'inscription', note: '西頓王兼「阿斯塔特的祭司」，躺在一具重新利用的埃及石棺裡。', bible: '耶 7:18；王上 11:5「西頓人的女神亞斯她錄」' },
            { slug: 'eshmunazar', title_zh: '埃什蒙納扎爾石棺銘', title_orig: 'Eshmunazar II sarcophagus', siglum: 'KAI 14', era: '約前 5 世紀', language: PHO, provenance: '西頓；羅浮宮藏', status: 'inscription', note: '「凡開此棺者，願他在陰魂（拉菲烏姆）中沒有安息之所，不得葬於墳墓。」並記王母為阿斯塔特與埃什蒙建廟。', seealso: ['rephaim'] },
            { slug: 'bodashtart', title_zh: '博達施塔特銘文', title_orig: 'Bodashtart inscriptions', siglum: 'KAI 15–16', era: '約前 4 世紀', language: PHO, provenance: '西頓埃什蒙神廟', status: 'inscription', note: '王為醫神埃什蒙建「聖山之廟」。' },
          ],
        },
        {
          key: 'temple',
          label: '神廟與祭儀',
          label_en: 'Temple and Cult',
          texts: [
            { slug: 'kition-tariff', title_zh: '基提翁阿斯塔特神廟帳目', title_orig: 'Kition temple tariff (Astarte temple accounts)', siglum: 'KAI 37', era: '約前 4 世紀', language: PHO, provenance: '賽普勒斯基提翁', status: 'inscription', note: '一個月的神廟開支：給石匠、理髮師、歌者，給「狗」與「少年」——後兩者的身分學界爭論不休。', bible: '申 23:17–18' },
            { slug: 'pyrgi', title_zh: '皮吉金板', title_orig: 'Pyrgi Gold Tablets', siglum: 'KAI 277', era: '約前 500', language: '腓尼基語—伊特魯里亞語雙語', provenance: '義大利皮吉（切爾韋泰里港）；羅馬朱利亞別墅博物館藏', status: 'inscription', note: '伊特魯里亞城主向阿斯塔特（伊特魯里亞語作烏妮）獻聖所。腓尼基女神在義大利的名字。', xref: ['希臘羅馬大藏經 羅馬卷（伊特魯里亞）'] },
            { slug: 'marseille-tariff', title_zh: '馬賽祭稅表', title_orig: 'Marseille Tariff', siglum: 'KAI 69', era: '約前 3 世紀（原立於迦太基）', language: PUN, provenance: '馬賽出土；原屬迦太基巴力‧札封神廟', status: 'inscription', note: '每種祭牲（牛、牛犢、公羊、山羊、羔羊、鳥）在「全燔祭」「平安祭」各應付祭司多少銀子、分得哪幾塊肉。', bible: '利 1–7；利 7:31–34 祭司的分' },
            { slug: 'carthage-tariff', title_zh: '迦太基祭稅表', title_orig: 'Carthage Tariff', siglum: 'KAI 74', era: '約前 4–3 世紀', language: PUN, provenance: '迦太基', status: 'fragment', note: '與馬賽祭稅表同類，殘缺較甚。', seealso: ['marseille-tariff'] },
            { slug: 'tophet-stelae', title_zh: '迦太基托斐特獻祭碑', title_orig: 'Tophet stelae of Carthage (molk offerings)', siglum: 'KAI 79 等', era: '約前 7 – 前 2 世紀', language: PUN, provenance: '迦太基薩朗博托斐特', status: 'inscription', extent: '數千件', note: '「獻給女主塔尼特、巴力之面，與主巴力‧哈蒙……某某所許的 mlk 祭，因神聽了他的聲音。」數萬甕嬰孩骨灰出土於同址；是否為活人獻祭，考古學界至今兩派對立。', bible: '王下 23:10；耶 7:31「陀斐特」；利 18:21「摩洛」' },
          ],
        },
      ],
    },
    {
      key: 'aramaic',
      sigil: '迦二',
      name: '亞蘭',
      name_en: 'Aramaic',
      era: '約前 850 – 前 4 世紀',
      summary:
        '亞蘭諸國的王銘、條約與先知文獻，加上波斯帝國時代埃及駐軍留下的亞蘭文紙草。亞蘭語後來成為整個近東的通用語，'
        + '但留下的多神信仰文獻並不多。',
      divisions: [
        {
          key: 'kingdoms',
          label: '亞蘭諸國',
          label_en: 'Aramaean Kingdoms',
          texts: [
            { slug: 'deir-alla', title_zh: '德伊爾‧阿拉巴蘭銘文', title_orig: 'Deir ʿAlla plaster texts (Balaam son of Beor)', era: '約前 800', language: '亞蘭語或南迦南方言（學界爭論）', provenance: '約旦河谷德伊爾‧阿拉，寫在灰泥牆上', status: 'fragment', note: '「比珥之子巴蘭，眾神的先見……神在夜間來到他那裡。」他醒來哭泣，說眾神會議要使天地黑暗。舊約以外唯一提到聖經先知的古代文獻。', bible: '民 22–24' },
            { slug: 'zakkur', title_zh: '扎庫爾碑', title_orig: 'Zakkur stela', siglum: 'KAI 202', era: '約前 785', language: ARA, provenance: '敘利亞阿菲斯；羅浮宮藏', status: 'inscription', note: '王被十六國聯軍圍困，向巴力沙明舉手，「巴力沙明藉先見與占卜者答覆我：不要怕，我立你為王，我必與你同在。」', bible: '王上 22；王下 6–7 先知在圍城中的神諭' },
            { slug: 'sefire', title_zh: '塞菲雷條約', title_orig: 'Sefire treaties', siglum: 'KAI 222–224', era: '約前 750', language: ARA, provenance: '敘利亞塞菲雷；大馬士革國家博物館藏', status: 'inscription', note: '以眾神為見證的附庸條約與咒詛：「如這蠟被火燒，願背約者也被燒；如這牛犢被劈開，願背約者也被劈開。」', bible: '創 15:9–18；耶 34:18–20 劈開牛犢立約' },
            { slug: 'tel-dan', title_zh: '但丘碑', title_orig: 'Tel Dan stela', siglum: 'KAI 310', era: '約前 840', language: ARA, provenance: '以色列北部但丘', status: 'fragment', note: '「哈達德立我為王，哈達德行在我前面」，並記擊殺「以色列王」與「大衛家」之王——聖經以外最早的「大衛家」字樣。', bible: '王下 8–9' },
            { slug: 'hadad-panamuwa', title_zh: '帕納穆瓦一世哈達德像銘', title_orig: 'Hadad statue of Panamuwa I', siglum: 'KAI 214', era: '約前 760', language: '撒瑪勒語（亞蘭語方言）', provenance: '撒瑪勒（土耳其津吉利）', status: 'inscription', note: '王的子孫獻祭時要說：「願帕納穆瓦的魂與哈達德同吃同喝。」' },
            { slug: 'kuttamuwa', title_zh: '庫塔穆瓦碑', title_orig: 'Kuttamuwa stela', era: '約前 735', language: '撒瑪勒語（亞蘭語方言）', provenance: '撒瑪勒，2008 年出土', status: 'inscription', note: '「我的魂（nbš）在這碑裡。」一位官員為自己預備的祭亡靈之所，每年獻牲。顯示魂可與屍身分離、住在石碑之中——對聖經「魂」（nepeš）觀念的研究影響極大。' },
          ],
        },
        {
          key: 'persian-egypt',
          label: '波斯時代埃及的亞蘭文',
          label_en: 'Aramaic in Persian Egypt',
          texts: [
            { slug: 'ahiqar', title_zh: '阿希卡爾', title_orig: 'Words of Ahiqar', siglum: 'TAD C1.1', era: '抄於約前 5 世紀', language: ARA, provenance: '埃及象島', status: 'fragment', note: '亞述王以撒哈頓的賢臣被養子誣陷、藏身得救的故事，後附格言百餘條。後來傳入敘利亞、阿拉伯、亞美尼亞、斯拉夫諸語。', bible: '多比傳 1:21–22、14:10 提到阿希卡爾', seealso: ['ahiqar-akkadian'] },
            { slug: 'amherst-63', title_zh: '阿默斯特紙草 63（世俗體字母寫的亞蘭文）', title_orig: 'Papyrus Amherst 63', era: '抄於約前 4 世紀', language: '亞蘭語（以世俗體埃及文字拼寫）', provenance: '埃及（底比斯一帶）；紐約摩根圖書館藏', status: 'composite', note: '一群亞蘭人移民的節慶禮儀與詩歌，向荷魯斯、伯特利諸神禱告；其中一首與詩篇第二十篇幾乎逐句相同。', bible: '詩 20' },
            { slug: 'elephantine-temple', title_zh: '象島神廟重建請願書', title_orig: 'Elephantine petition for the rebuilding of the temple of YHW', siglum: 'TAD A4.7–8', era: '前 407', language: ARA, provenance: '埃及象島', status: 'whole', note: '駐軍的猶大人寫信給耶路撒冷與撒馬利亞的波斯總督，請求重建被埃及祭司毀掉的「雅胡神廟」。同一社群的捐款名冊上，雅胡與「阿娜特—雅胡」「伯特利」並列受捐。', bible: '耶 44 在埃及的猶大人' },
          ],
        },
      ],
    },
    {
      key: 'transjordan-israel',
      sigil: '迦三',
      name: '摩押、亞捫與以色列銘文',
      name_en: 'Moab, Ammon, Israel and Judah',
      era: '約前 900 – 前 586',
      summary:
        '聖經裡「摩押人的可憎之神基抹」「亞捫人的可憎之神米勒公」在這裡有了他們自己子民的記述；'
        + '以色列與猶大出土的祝福銘文則顯示，在先知與申命記改革之前，民間宗教的實際樣貌。',
      divisions: [
        {
          key: 'neighbours',
          label: '摩押與亞捫',
          label_en: 'Moab and Ammon',
          texts: [
            { slug: 'mesha', title_zh: '米沙碑', title_orig: 'Mesha stela (Moabite Stone)', siglum: 'KAI 181', era: '約前 840', language: '摩押語', provenance: '約旦底本；羅浮宮藏', status: 'inscription', note: '「暗利為以色列王，多日欺壓摩押，因基抹向他的地發怒。」米沙奉基抹之命攻取尼波，殺七千人，「因我已將它當作禁物（ḥrm）獻給亞施塔—基抹」；並提到奪取「雅威的器皿」。', bible: '王下 3；書 6:17–21 禁物（ḥērem）' },
            { slug: 'amman-citadel', title_zh: '安曼城堡銘文', title_orig: 'Amman Citadel inscription', era: '約前 9 世紀', language: '亞捫語', provenance: '約旦安曼', status: 'fragment', note: '米勒公神對王說話的殘句。', bible: '王上 11:5' },
          ],
        },
        {
          key: 'israel-judah',
          label: '以色列與猶大',
          label_en: 'Israel and Judah',
          texts: [
            { slug: 'kuntillet-ajrud', title_zh: '昆提勒‧阿吉魯德銘文', title_orig: 'Kuntillet ʿAjrud inscriptions', era: '約前 800', language: HEB, provenance: '西奈半島東北的旅站', status: 'inscription', note: '大陶甕上寫著「我以撒馬利亞的雅威與他的亞舍拉祝福你」、「提幔的雅威與他的亞舍拉」，旁邊畫著兩個神像與一個彈琴的人。', bible: '申 16:21；王下 21:7；王下 23:4–7' },
            { slug: 'khirbet-el-qom', title_zh: '希伯特‧庫姆墓銘', title_orig: 'Khirbet el-Qom inscription', era: '約前 750', language: HEB, provenance: '猶大山地（希伯崙西）', status: 'inscription', note: '「烏利雅胡蒙雅威賜福，他藉祂的亞舍拉從仇敵手中被救。」墓壁上刻著一隻手。' },
            { slug: 'ketef-hinnom', title_zh: '欣嫩谷銀卷', title_orig: 'Ketef Hinnom silver amulets', era: '約前 600', language: HEB, provenance: '耶路撒冷欣嫩谷墓室；以色列博物館藏', status: 'inscription', note: '兩個捲起來掛在頸上的小銀卷，刻著「願雅威賜福你、保護你，願雅威使祂的臉光照你，賜你平安」——現存最古的聖經經文。', bible: '民 6:24–26' },
            { slug: 'arad-ostraca', title_zh: '亞拉得陶片', title_orig: 'Arad ostraca', era: '約前 600', language: HEB, provenance: '亞拉得要塞（內有一座帶祭壇與香壇的雅威聖所）', status: 'fragment', note: '軍需文書中提到「雅威的殿」。要塞內的聖所格局與耶路撒冷聖殿相同，後來被刻意廢棄。', bible: '王下 18:4、23:8 廢除丘壇' },
          ],
        },
      ],
    },
    {
      key: 'roman-syria',
      sigil: '迦四',
      name: '羅馬時代的亞蘭語神廟',
      name_en: 'Aramaic Temples of the Roman Era',
      era: '約前 1 世紀 – 公元 3 世紀',
      summary:
        '羅馬與帕提亞之間的沙漠商城：帕爾米拉的貝勒神廟、哈特拉的太陽神廟、埃德薩的月神高地。'
        + '這是古代近東多神信仰最後一次大規模的公共表達，也是本藏的終點。',
      divisions: [
        {
          key: 'caravan-cities',
          label: '商隊城市',
          label_en: 'Caravan Cities',
          texts: [
            { slug: 'palmyra-bel', title_zh: '帕爾米拉貝勒神廟奉獻銘', title_orig: 'Palmyrene dedications (Temple of Bel)', era: '公元 32 年起', language: '帕爾米拉亞蘭語（多附希臘文）', provenance: '帕爾米拉', status: 'inscription', note: '貝勒、亞希博勒（月）、雅希博勒（日）三神並坐。神廟主殿 2015 年被極端組織炸毀。' },
            { slug: 'palmyra-anonymous', title_zh: '帕爾米拉「名字受祝福者」奉獻銘', title_orig: 'Dedications to the "One whose name is blessed forever"', era: '公元 2–3 世紀', language: '帕爾米拉亞蘭語', provenance: '帕爾米拉', status: 'inscription', extent: '逾二百件', note: '不稱神名，只稱「名字永受祝福的那一位、良善慈悲者」——晚期近東多神信仰內部的一神傾向。' },
            { slug: 'palmyra-tesserae', title_zh: '帕爾米拉宴席籌牌', title_orig: 'Palmyrene banquet tesserae', era: '公元 1–3 世紀', language: '帕爾米拉亞蘭語', provenance: '帕爾米拉', status: 'inscription', extent: '逾千枚', note: '參加神廟祭宴（marzeaḥ）的入場陶籌，印著神像與宴主之名。', seealso: ['el-marzeah'] },
            { slug: 'hatra', title_zh: '哈特拉銘文', title_orig: 'Hatran inscriptions', era: '公元 1–3 世紀', language: '哈特拉亞蘭語', provenance: '伊拉克哈特拉', status: 'inscription', extent: '約四百件', note: '「我們的主、我們的女主、我們主的兒子」三神與太陽神沙馬什的大神廟。約 240 年城為薩珊所破。' },
            { slug: 'sumatar', title_zh: '蘇馬塔高地銘文', title_orig: 'Sumatar Harabesi inscriptions', era: '公元 165 年', language: '古敘利亞語', provenance: '埃德薩與哈蘭之間', status: 'inscription', note: '向「眾神之主」（Marilaha）與月神辛立碑——同一地區一兩代人之後就成了敘利亞基督教的中心。', seealso: ['harran-sabians'] },
          ],
        },
      ],
    },
  ],
}
