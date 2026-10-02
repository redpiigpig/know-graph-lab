// 赫梯與胡里特藏 —— 安納托利亞
//
// 「赫梯」（user 2026-10-02 定，銜接聖經「赫人」；詞庫原作「西台」已改）。
//
// 赫梯人自稱「千神之國」：他們不消滅被征服者的神，而是把神連同祭司、語言、儀式一起搬回首都哈圖沙。
// 所以哈圖沙的泥板庫裡有八種語言——赫梯語、哈梯語、盧維語、帕萊語、胡里特語、阿卡德語、蘇美語，
// 以及印度—雅利安的神名。這一藏因此不能只叫「赫梯」：
//   · 哈梯人是赫梯人到來之前的安納托利亞土著，赫梯的本土神話（伊盧揚卡、泰利皮努）多源自哈梯
//   · 胡里特人的神話（庫瑪比組詩）與儀式（基茲瓦特納）在帝國後期取代了大半本土傳統
// 歸藏準則：出土於哈圖沙的胡里特語文本歸本藏；出土於烏加里特的胡里特讚歌也歸本藏（按宗教系統），
//   烏加里特藏以互見指回。
//
// 斷限：哈圖沙約前 1180 年被焚棄，楔形赫梯語隨之消失；但盧維語象形文字在敘利亞北部的
//   新赫梯諸邦續用到約前 700 年，本藏第九卷再收鐵器時代安納托利亞諸語至前 4 世紀。
//
// 編號：一律用 CTH（Catalogue des Textes Hittites，Laroche 1971，今由 Hethitologie-Portal Mainz 維護），
//   2026-10-02 逐條對過 hethport.net/CTH。🚨 未對到的不填。

import type { NeCanon } from './types'

const HIT = '赫梯語'
const HUR = '胡里特語'
const NH = '新赫梯時代抄本（約前 1300–1180）'

export const ANATOLIA_CANON: NeCanon = {
  key: 'anatolia',
  name: '赫梯與胡里特藏',
  name_en: 'Hittite and Hurrian Canon',
  glyph: '赫',
  subtitle: '「千神之國」哈圖沙的泥板庫',
  scriptural: true,
  language: '赫梯語為主，兼哈梯語、胡里特語、盧維語、帕萊語；第八卷另收弗里吉亞語、呂底亞語、呂基亞語',
  era: '約前 1650 – 前 4 世紀',
  terminus: '哈圖沙約前 1180 年焚棄，楔形赫梯語隨之消失；盧維語象形文字續用至約前 700 年。',
  columns: { orig: 'available', en: 'copyright', zh: 'none' },
  summary:
    '赫梯人把被征服各地的神連同儀式搬回首都，自稱「千神之國」。這一藏的特色是：'
    + '幾乎沒有「文學」，大半是國家宗教的實務檔案——節期儀程、巫婆的治病儀式、國王為瘟疫向神認罪的禱文、'
    + '神廟清點神像的清冊。神話多半是儀式的一部分，在節慶中念給神聽。'
    + '胡里特人的天界王權神話（庫瑪比組詩）是赫西俄德《神譜》的近親，諸神世代以閹割與吞食相繼。',
  volumes: [
    {
      key: 'native-myths',
      sigil: '赫一',
      name: '本土神話',
      name_en: 'Anatolian (Hattic–Hittite) Myths',
      era: '古赫梯時代成書（約前 1650–1500），新赫梯抄本',
      summary:
        '源自哈梯土著的安納托利亞神話，多與儀式相連：神「失蹤」使大地凋敝，眾神尋回並平息其怒，萬物復甦。'
        + '這一類「消失之神」神話是赫梯宗教最有代表性的文類。',
      divisions: [
        {
          key: 'vanishing',
          label: '消失之神',
          label_en: 'Vanishing Gods',
          texts: [
            { slug: 'telipinu-myth', title_zh: '泰利皮努神話', title_orig: 'Telipinu Myth', siglum: 'CTH 324', copies: NH, language: HIT, note: '農神發怒離去，連鞋都穿反了；爐火熄滅、牛羊不生、穀不結實。蜜蜂找到熟睡的他，螫醒之後他更怒，最後以儀式把怒氣封進冥府的銅鍋裡。' },
            { slug: 'storm-god-vanishing', title_zh: '風暴神的消失與歸來', title_orig: 'Disappearance and return of the Storm-god', siglum: 'CTH 325', copies: NH, language: HIT, status: 'fragment', note: '同一型的神話套在風暴神身上——「消失之神」是一個可以換主角的儀式框架。' },
            { slug: 'telipinu-sea', title_zh: '泰利皮努與海神之女', title_orig: 'Telipinu and the Daughter of the Sea-god', siglum: 'CTH 322', copies: NH, language: HIT, status: 'fragment', note: '海神扣住太陽，泰利皮努前去，娶回海神之女。' },
          ],
        },
        {
          key: 'other-native',
          label: '其他本土神話',
          label_en: 'Other Native Myths',
          texts: [
            { slug: 'illuyanka', title_zh: '伊盧揚卡（風暴神屠蛇）', title_orig: 'Illuyanka Myth', siglum: 'CTH 321', copies: NH, language: HIT, note: '兩個版本並列：一說女神以酒宴灌醉巨蛇，一說風暴神之子娶蛇之女以取回父親的心與眼。在普魯利新年節中誦唸。', seealso: ['purulli'], bible: '賽 27:1 利維坦；詩 74:13–14' },
            { slug: 'moon-fell', title_zh: '月亮從天上掉下來', title_orig: 'The Moon that Fell from Heaven', siglum: 'CTH 727', language: '哈梯語—赫梯語雙語', status: 'fragment', note: '月神墜落在城門口，風暴神降雨打他、使他驚恐。哈梯神話少數留下雙語本的一篇。' },
            { slug: 'zalpa', title_zh: '扎爾帕的故事', title_orig: 'Tale of Zalpa', siglum: 'CTH 3', copies: '古赫梯', language: HIT, status: 'fragment', note: '卡內什的王后一年生了三十個兒子，放進塗了糞的籃子丟進河裡，眾神把他們救起養大。', bible: '出 2:3' },
            { slug: 'appu', title_zh: '阿普與他的兩個兒子', title_orig: 'Tale of Appu and his Two Sons', siglum: 'CTH 360', copies: NH, language: HIT, note: '富而無子的人求太陽神賜子，生了「惡」與「善」兩兄弟，分家時惡者佔盡便宜。胡里特色彩的寓言。' },
            { slug: 'sun-cow-fisherman', title_zh: '太陽神、母牛與漁夫', title_orig: 'The Sun-god, the Cow and the Fisherman', siglum: 'CTH 363', copies: NH, language: HIT, status: 'fragment', note: '太陽神與母牛所生的孩子被遺棄，漁夫撿回撫養。' },
          ],
        },
      ],
    },
    {
      key: 'kumarbi',
      sigil: '赫二',
      name: '庫瑪比組詩',
      name_en: 'The Kumarbi Cycle',
      era: '胡里特原作；赫梯語譯本為新赫梯抄本',
      summary:
        '胡里特神話的「天界王權」系列，赫梯人譯成赫梯語並保存。天神阿拉盧、安努、庫瑪比、特舒布四代相繼，'
        + '庫瑪比咬下安努的生殖器而懷了風暴神——這套閹割、吞食、以石代子的情節與赫西俄德的烏拉諾斯—克洛諾斯—宙斯幾乎一一對應，'
        + '是希臘神話近東來源最有力的證據。',
      divisions: [
        {
          key: 'kingship',
          label: '天界王權',
          label_en: 'Kingship in Heaven',
          texts: [
            { slug: 'kumarbi-kingship', title_zh: '起源之歌（天界王權）', title_orig: 'Song of Origins (Kingship in Heaven, Theogony)', siglum: 'CTH 344', copies: NH, language: HIT, status: 'fragment', note: '阿拉盧為王九年，安努推翻他；安努為王九年，庫瑪比咬下他的生殖器吞入腹中，懷上風暴神特舒布等三神。', xref: ['希臘羅馬大藏經 Α 神譜（赫西俄德）'], seealso: ['dunnu-theogony', 'philo-byblos'] },
            { slug: 'ullikummi', title_zh: '烏利庫米之歌', title_orig: 'Song of Ullikummi', siglum: 'CTH 345', copies: NH, language: `${HIT}（另有胡里特語殘本）`, extent: '三塊泥板', note: '庫瑪比與巨石交合生下石巨人，立在背負天地的巨人肩上，一天長一肘，直頂天庭。恩基（埃阿）以分開天地的古刀割斷它的腳。' },
            { slug: 'hedammu', title_zh: '赫達穆之歌', title_orig: 'Song of Hedammu', siglum: 'CTH 348', copies: NH, language: `${HIT}（另有胡里特語殘本）`, status: 'fragment', note: '庫瑪比娶海神之女生下吞噬一切的海蛇，伊絲塔以美色誘之。' },
            { slug: 'song-silver', title_zh: '銀之歌', title_orig: 'Song of Silver', siglum: 'CTH 364', copies: NH, language: HIT, status: 'fragment', note: '庫瑪比與凡間女子所生的「銀」，被人嘲笑沒有父親。' },
            { slug: 'kal-kingship', title_zh: '守護神 KAL 的王權', title_orig: 'Song of the Protective God (KAL)', siglum: 'CTH 343', copies: NH, language: HIT, status: 'fragment', note: '一位小神篡得天庭王位，因怠慢獻祭而被廢。' },
            { slug: 'kumarbi-fragments', title_zh: '庫瑪比神話殘篇', title_orig: 'Fragments of the Kumarbi myth', siglum: 'CTH 346', copies: NH, language: HIT, status: 'fragment' },
          ],
        },
        {
          key: 'hurrian-epics',
          label: '其他胡里特敘事',
          label_en: 'Other Hurrian Narratives',
          texts: [
            { slug: 'song-release', title_zh: '解放之歌', title_orig: 'Song of Release (Epic of Liberation)', siglum: 'CTH 789', era: '約前 1400', language: '胡里特語—赫梯語雙語', provenance: '哈圖沙', status: 'fragment', note: '冥府女神宴請風暴神；埃卜拉城因拒絕釋放奴隸而被毀。附一組寓言與釋義。迄今最長的胡里特語文本。', bible: '利 25 禧年釋奴；耶 34:8–22' },
            { slug: 'kessi', title_zh: '獵人凱什希', title_orig: 'Tale of the Hunter Kešši', siglum: 'CTH 361', copies: '赫梯語、胡里特語、阿卡德語三種殘本', language: HIT, status: 'fragment', note: '獵人迷戀新婚妻子而荒廢狩獵與獻祭，眾神懲罰他。' },
            { slug: 'gurparanzah', title_zh: '古帕蘭扎的英勇事蹟', title_orig: 'Heroic deeds of Gurparanzah', siglum: 'CTH 362', copies: NH, language: HIT, status: 'fragment' },
          ],
        },
      ],
    },
    {
      key: 'foreign-myths',
      sigil: '赫三',
      name: '外來神話譯本',
      name_en: 'Translated Foreign Myths',
      era: '新赫梯時代',
      summary: '赫梯書吏翻譯的美索不達米亞與迦南神話。這些譯本不是原作的忠實複製，而是改寫——吉伽美什在赫梯本裡多了安納托利亞的地名與神。',
      divisions: [
        {
          key: 'translations',
          label: '譯本',
          label_en: 'Translations',
          texts: [
            { slug: 'gilgamesh-hittite', title_zh: '赫梯語吉伽美什', title_orig: 'Gilgameš (Akkadian, Hurrian, Hittite versions)', siglum: 'CTH 341', copies: NH, language: '阿卡德語、胡里特語、赫梯語三種', status: 'fragment', note: '哈圖沙同時藏有三種語言的吉伽美什——同一部史詩在一座城裡以三種語言流通。', seealso: ['gilgamesh-sb'] },
            { slug: 'elkunirsa', title_zh: '埃勒庫尼薩與亞舍拉', title_orig: 'Elkunirša and Ašertu', siglum: 'CTH 342', copies: NH, language: HIT, status: 'fragment', note: '赫梯語寫的迦南神話：「伊勒，地的創造者」（ʾEl qōnē ʾarṣ）之妻亞舍拉勾引巴力不成，向丈夫反誣。', bible: '創 14:19「天地的主（創造者）」El ʿElyon qōnē šāmayim wāʾāreṣ；創 39', seealso: ['baal-cycle'] },
            { slug: 'atrahasis-hittite', title_zh: '赫梯語阿特拉哈西', title_orig: 'Atramḫasis', siglum: 'CTH 347', copies: NH, language: HIT, status: 'fragment', seealso: ['atrahasis'] },
          ],
        },
      ],
    },
    {
      key: 'prayers',
      sigil: '赫四',
      name: '祈禱',
      name_en: 'Prayers',
      era: '約前 1400 – 前 1200',
      summary:
        '赫梯王的禱文是古代近東最坦白的認罪文獻：瘟疫肆虐二十年，穆西利二世查問神諭，'
        + '查出是父王違背誓約之罪，便以第一人稱向眾神認罪、陳情、討價還價。「父親的罪落到兒子身上」——同一個問題以西結書第十八章也問過。',
      divisions: [
        {
          key: 'royal',
          label: '王室禱文',
          label_en: 'Royal Prayers',
          texts: [
            { slug: 'plague-prayers', title_zh: '穆西利二世瘟疫禱文', title_orig: 'Plague Prayers of Muršili II', siglum: 'CTH 378', era: '約前 1320', copies: NH, language: HIT, extent: '五篇', note: '「哈圖沙的眾神啊，瘟疫已經二十年……若是因為我父親的罪，我承認了。」王把神諭查出的罪因逐條列出，並辯稱：「人死光了，誰來給你們獻祭？」', bible: '撒下 21:1–14（掃羅違約，大衛時饑荒三年）；結 18' },
            { slug: 'kantuzzili', title_zh: '坎圖齊利向太陽神禱', title_orig: 'Prayer of Kantuzzili to the Sun-god', siglum: 'CTH 373', era: '約前 1400', copies: NH, language: HIT, note: '「我從來沒有向神發假誓……我的神，為什麼讓我生病？」最早的赫梯語個人禱文之一，承襲巴比倫向沙馬什禱告的格式。', seealso: ['shamash-hymn'] },
            { slug: 'prayer-mortal-sun', title_zh: '凡人向太陽神的頌禱', title_orig: 'Hymn and prayer of a mortal to the Sun-god', siglum: 'CTH 372', copies: NH, language: HIT },
            { slug: 'arnuwanda-asmunikal', title_zh: '阿努旺達一世與阿什穆尼卡向阿琳娜太陽女神禱', title_orig: 'Prayer of Arnuwanda I and Ašmunikal', siglum: 'CTH 375', era: '約前 1370', copies: NH, language: HIT, note: '王與王后哀訴北方卡什卡人攻掠神廟，「再沒有人為你們獻祭」。' },
            { slug: 'arinna-hymns', title_zh: '阿琳娜太陽女神頌禱', title_orig: 'Hymns and prayers to the Sun-goddess of Arinna', siglum: 'CTH 376', copies: NH, language: HIT },
            { slug: 'mursili-telipinu', title_zh: '穆西利二世向泰利皮努頌禱', title_orig: 'Hymn and prayer of Muršili II to Telipinu', siglum: 'CTH 377', copies: NH, language: HIT },
            { slug: 'muwatalli-assembly', title_zh: '穆瓦塔利二世向眾神禱', title_orig: 'Prayer of Muwatalli II to the assembly of gods', siglum: 'CTH 381', era: '約前 1290', copies: NH, language: HIT, note: '逐一點名百餘位神與其所在之城，一份禱文同時是帝國的宗教地圖。' },
            { slug: 'puduhepa-prayer', title_zh: '普杜赫帕王后禱文', title_orig: 'Prayer of Puduḫepa to the Sun-goddess of Arinna', siglum: 'CTH 384', era: '約前 1260', copies: NH, language: HIT, note: '王后為病重的丈夫哈圖西利三世向諸女神許願：若神延長他的壽命，她將獻上城鎮與金像。' },
            { slug: 'hattusili-puduhepa', title_zh: '哈圖西利三世與普杜赫帕向阿琳娜太陽女神禱', title_orig: 'Prayer of Ḫattušili III and Puduḫepa', siglum: 'CTH 383', copies: NH, language: HIT, status: 'fragment' },
          ],
        },
      ],
    },
    {
      key: 'hurrian-hymns',
      sigil: '赫五',
      name: '胡里特讚歌',
      name_en: 'Hurrian Hymns',
      era: '約前 1400 – 前 1200',
      summary: '胡里特語的祭儀詩歌。最著名的一首出土於烏加里特，附有樂譜——按宗教系統歸本藏，烏加里特藏以互見指回。',
      divisions: [
        {
          key: 'hymns',
          label: '讚歌',
          label_en: 'Hymns',
          texts: [
            { slug: 'hurrian-hymn-nikkal', title_zh: '胡里特尼卡讚歌（第六號）', title_orig: 'Hurrian Hymn no. 6 to Nikkal', siglum: 'RS 15.30 + 15.49 + 17.387（h.6）', era: '約前 1400', language: HUR, provenance: '烏加里特王宮', status: 'fragment', note: '向果園女神尼卡祈求生育的禱歌，泥板下半是以巴比倫音名寫成的豎琴指法——現存最古、大體完整的樂譜。', seealso: ['nikkal-yarikh'] },
          ],
        },
      ],
    },
    {
      key: 'festivals',
      sigil: '赫六',
      name: '國家節期',
      name_en: 'State Festivals',
      era: '古赫梯至新赫梯',
      summary:
        '國王是最高祭司，一年中大半時間在各城巡行主持節期。春季的「番紅花節」長達三十八天，秋季的「急行節」以神像出巡為主。'
        + '節期泥板記到極細：誰站哪裡、念什麼、喝哪一杯酒、樂師唱哈梯語還是盧維語。',
      divisions: [
        {
          key: 'great-festivals',
          label: '大節',
          label_en: 'Great Festivals',
          texts: [
            { slug: 'antahsum', title_zh: '番紅花節（AN.TAḪ.ŠUM）', title_orig: 'AN.DAḪ.ŠUM festival', siglum: 'CTH 604–625', copies: NH, language: HIT, extent: '春季三十八日', note: '國王與王后巡行哈圖沙周邊諸城，每日一神一廟。CTH 604 是全節的總覽泥板。' },
            { slug: 'nuntarriyashas', title_zh: '急行節', title_orig: 'Festival of Haste (EZEN₄ nuntarrijašḫaš)', siglum: 'CTH 626', copies: NH, language: HIT, note: '秋季節慶，國王從戰場趕回主持，故名「急行」。' },
            { slug: 'kilam', title_zh: '門樓節（KI.LAM）', title_orig: 'KI.LAM festival', siglum: 'CTH 627', copies: NH, language: HIT, note: '王在城門樓上檢閱神像、聖獸與各行會的遊行隊伍。' },
            { slug: 'hisuwa', title_zh: '希蘇瓦節', title_orig: '(ḫ)išuwa festival', siglum: 'CTH 628', copies: NH, language: `${HIT}（胡里特語祝詞）`, note: '基茲瓦特納的胡里特節慶，九日，為王室祈福——胡里特宗教進入赫梯國家祭典的標誌。' },
            { slug: 'purulli', title_zh: '普魯利節（涅里克）', title_orig: 'purulli festival of Nerik', siglum: 'CTH 674', copies: NH, language: HIT, status: 'fragment', note: '新年（春季）節慶，誦唸伊盧揚卡神話以重演風暴神的勝利、更新王權。', seealso: ['illuyanka', 'akitu'] },
            { slug: 'samuha-ishtar', title_zh: '沙穆哈伊絲塔節', title_orig: 'Festivals for Ištar of Šamuḫa', siglum: 'CTH 711–712', copies: NH, language: HIT, status: 'fragment', note: '哈圖西利三世的保護女神。' },
          ],
        },
      ],
    },
    {
      key: 'rituals',
      sigil: '赫七',
      name: '儀式',
      name_en: 'Rituals',
      era: '約前 1500 – 前 1200',
      summary:
        '赫梯泥板庫裡最大的一類。儀式常以「某地某人如此說」開頭——作者多是「老婦」（巫醫）、占卜師或外國祭司，'
        + '治的是陽痿、瘟疫、家庭失和、軍隊潰敗、王的口吃。替罪羊、替身、以線綁走病痛等技法反覆出現。',
      divisions: [
        {
          key: 'healing',
          label: '治病與淨化',
          label_en: 'Healing and Purification',
          texts: [
            { slug: 'tunnawiya', title_zh: '屯納維婭儀式', title_orig: 'Rituals of Tunnawiya', siglum: 'CTH 409', copies: NH, language: `${HIT}（盧維語咒語）`, note: '老婦屯納維婭的淨化儀式群，最常見的「老婦儀式」範本。' },
            { slug: 'paskuwatti', title_zh: '帕什庫瓦蒂儀式（治性無能）', title_orig: 'Ritual of Paškuwatti against impotence', siglum: 'CTH 406', copies: NH, language: HIT, note: '病人放下弓箭、拿起紡錘鏡子，再反轉過來——以性別象徵物的交換治病。' },
            { slug: 'mastigga', title_zh: '馬斯提加儀式（化解家庭紛爭）', title_orig: 'Rituals of Maštigga of Kizzuwatna', siglum: 'CTH 404', copies: NH, language: HIT, note: '父子或兄弟因咒罵失和，巫婆以羊與小像為替身吸走詛咒。' },
            { slug: 'ammihatna', title_zh: '阿米哈特納儀式（除不潔）', title_orig: 'Ritual of Ammiḫatna of Kizzuwatna', siglum: 'CTH 471', copies: NH, language: HIT, note: '基茲瓦特納的胡里特祭司為神廟除污，與利未記的潔淨條例類型相近。', bible: '利 11–15' },
            { slug: 'itkalzi', title_zh: '洗口儀式（伊特卡齊）', title_orig: 'Mouth-washing ritual (itkaḫi-, itkalzi-)', siglum: 'CTH 777', copies: NH, language: `${HUR}（赫梯語儀程）`, extent: '二十二塊泥板', note: '胡里特語的大型淨化儀式系列。' },
            { slug: 'mursili-aphasia', title_zh: '穆西利的失語症', title_orig: 'Muršili\'s Aphasia', siglum: 'CTH 486', copies: NH, language: HIT, note: '雷雨中王受驚口歪失語，占卜查出是風暴神所為，遂以牛為替身送往神廟。王的病歷與神諭並列。' },
          ],
        },
        {
          key: 'plague',
          label: '瘟疫與軍隊',
          label_en: 'Plague and Army',
          texts: [
            { slug: 'ashella', title_zh: '阿什赫拉儀式（軍中瘟疫）', title_orig: 'Ritual of Ašḫella against plague in the army', siglum: 'CTH 394', copies: NH, language: HIT, note: '公羊頭戴彩線、女人一同，被趕往敵境，把瘟疫帶走。', bible: '利 16:20–22 送往曠野的羊' },
            { slug: 'uhhamuwa', title_zh: '烏哈穆瓦儀式', title_orig: 'Ritual of Uḫḫamuwa of Arzawa against plague', siglum: 'CTH 410', copies: NH, language: HIT, note: '為公羊戴上冠冕送往敵國：「讓瘟疫之神跟著牠去。」', bible: '利 16' },
            { slug: 'pulisa', title_zh: '普利沙儀式', title_orig: 'Ritual of Puliša against imported plague', siglum: 'CTH 407', copies: NH, language: HIT, note: '王出征帶回的瘟疫，以俘虜的男女與公羊為替身送回原地。' },
          ],
        },
        {
          key: 'royal-rituals',
          label: '王室儀式',
          label_en: 'Royal Rituals',
          texts: [
            { slug: 'royal-funerary', title_zh: '王室喪禮（大死）', title_orig: 'Royal funerary ritual (šalliš waštaiš)', siglum: 'CTH 450', copies: NH, language: HIT, extent: '十四日', note: '「當哈圖沙發生大罪（王死）時」：火葬、以油酒澆熄骨灰、裝入銀盒、為亡王製作坐像，並象徵性地為他在冥府備好田地牛羊。' },
            { slug: 'old-hittite-royal', title_zh: '四篇古赫梯王室儀式', title_orig: 'Four Old Hittite rituals for the royal couple', siglum: 'CTH 416', copies: '古赫梯', language: HIT, status: 'fragment' },
            { slug: 'zuwi', title_zh: '祖維的儀式與神話', title_orig: 'Ritual and myth of Zuwi', siglum: 'CTH 412', copies: NH, language: HIT, status: 'fragment' },
            { slug: 'kursas', title_zh: '獵袋守護神儀式', title_orig: 'Rituals for the Protective God of the Hunting Bag (KUŠkuršaš)', siglum: 'CTH 433', copies: NH, language: HIT, note: '神不以人形而以一隻皮袋為象——赫梯宗教中物件即神的例子。' },
          ],
        },
      ],
    },
    {
      key: 'state-religion',
      sigil: '赫八',
      name: '神廟與國家宗教',
      name_en: 'Temple and State Religion',
      era: '約前 1650 – 前 1200',
      summary: '祭司守則、神像清冊、宗教改革、神諭裁決，以及把王權正當性寫成神意的幾篇大文。',
      divisions: [
        {
          key: 'administration',
          label: '神廟行政',
          label_en: 'Temple Administration',
          texts: [
            { slug: 'temple-instructions', title_zh: '祭司與神廟人員守則', title_orig: 'Instructions for Priests and Temple Personnel', siglum: 'CTH 264', copies: NH, language: HIT, note: '祭司夜間要守廟、要潔淨才可進廚房；「人和神的心一樣嗎？僕人在主人面前要潔淨，神也一樣。」偷吃祭肉者連同全家處死。', bible: '利 22；撒上 2:12–17 以利的兒子' },
            { slug: 'cult-inventories', title_zh: '神廟清冊', title_orig: 'Cult inventories (Tudḫaliya IV)', siglum: 'CTH 529–530', era: '約前 1230', copies: NH, language: HIT, status: 'fragment', note: '圖達利亞四世下令普查全國地方神廟：每城有幾尊神像、什麼材質、何時祭祀。王把千神納入中央管理。' },
            { slug: 'samuha-reform', title_zh: '穆西利二世改革沙穆哈夜之女神祭', title_orig: 'Reform of the cult of the Goddess of the Night of Šamuḫa', siglum: 'CTH 482', copies: NH, language: HIT, note: '「分神」儀式：把神從舊廟請到新廟，用紅毛線一路鋪路。' },
            { slug: 'samuha-ritual', title_zh: '沙穆哈儀式', title_orig: 'Ritual of Šamuḫa', siglum: 'CTH 480', copies: NH, language: HIT, status: 'fragment' },
            { slug: 'yazilikaya', title_zh: '亞茲勒卡亞岩廟眾神浮雕', title_orig: 'Yazılıkaya rock sanctuary', era: '約前 1250（圖達利亞四世）', language: '盧維語象形文字（神名題記）', provenance: '哈圖沙東北露天岩廟', status: 'inscription', extent: '六十餘位神', note: '男神從左、女神從右兩列遊行，在中央由特舒布與赫帕特相會。胡里特萬神殿的一張石刻全圖。' },
          ],
        },
        {
          key: 'kingship',
          label: '王權神學',
          label_en: 'Royal Ideology',
          texts: [
            { slug: 'anitta', title_zh: '阿尼塔文', title_orig: 'Anitta Text', siglum: 'CTH 1', copies: '古赫梯與新赫梯抄本', language: HIT, note: '最古的印歐語文本。王摧毀哈圖沙，在廢墟上撒下雜草種子，詛咒「誰在我之後為王重建此城，願風暴神擊殺他」——後來的赫梯人偏偏定都在這裡。' },
            { slug: 'telipinu-edict', title_zh: '鐵列皮努敕令', title_orig: 'Edict of Telipinu', siglum: 'CTH 19', era: '約前 1500', copies: '阿卡德語與赫梯語本', language: HIT, note: '王回顧前朝因手足相殘而衰亡，訂立王位繼承法，並規定殺人者由苦主家屬決定生死。' },
            { slug: 'hattusili-apology', title_zh: '哈圖西利三世自辯書', title_orig: 'Apology of Ḫattušili III', siglum: 'CTH 81', era: '約前 1265', copies: NH, language: HIT, note: '篡位的王自述：伊絲塔從小在夢中引導我、保護我，奪取王位是女神的旨意。', bible: '撒上 16–撒下 5「大衛登基史」的自辯體' },
          ],
        },
      ],
    },
    {
      key: 'iron-age',
      sigil: '赫九',
      name: '鐵器時代安納托利亞',
      name_en: 'Iron Age Anatolia',
      era: '約前 1100 – 前 4 世紀',
      summary:
        '哈圖沙亡後，赫梯的宗教在敘利亞北部的「新赫梯」諸邦以盧維語續存；安納托利亞西部則興起弗里吉亞、呂底亞、呂基亞，'
        + '它們的大母神後來以希臘名字「庫柏勒」進入希臘羅馬世界。',
      divisions: [
        {
          key: 'neo-hittite',
          label: '新赫梯（盧維語象形文字）',
          label_en: 'Neo-Hittite (Hieroglyphic Luwian)',
          texts: [
            { slug: 'karatepe', title_zh: '卡拉特佩雙語銘文', title_orig: 'Karatepe bilingual (Azatiwada)', siglum: 'KAI 26', era: '約前 700', language: '腓尼基語—盧維語象形文字雙語', provenance: '卡拉特佩（土耳其南部）', status: 'inscription', note: '城主自述蒙巴力與諸神揀選，使平原「婦人可獨自紡錘而行」。解讀盧維語象形文字的鑰匙。', seealso: ['ahiram'] },
            { slug: 'karkamis-katuwa', title_zh: '卡赫美士諸王銘文', title_orig: 'Hieroglyphic Luwian inscriptions of Karkamiš', era: '約前 1000 – 前 717', language: '盧維語象形文字', provenance: '卡赫美士（土敘邊境）', status: 'inscription', note: '向女神庫巴巴與風暴神塔浩恩塔奉獻的建築銘文。庫巴巴後來就是弗里吉亞—希臘的庫柏勒。' },
          ],
        },
        {
          key: 'western',
          label: '弗里吉亞、呂底亞、呂基亞',
          label_en: 'Phrygia, Lydia, Lycia',
          columns: { orig: 'available', en: 'copyright', zh: 'none' },
          texts: [
            { slug: 'matar-inscriptions', title_zh: '弗里吉亞母神銘文', title_orig: 'Old Phrygian Matar inscriptions (Midas City)', era: '約前 8–6 世紀', language: '古弗里吉亞語', provenance: '米達斯城岩壁聖所', status: 'inscription', note: '岩壁上鑿出神門，門中立著「母親」（matar）的像。希臘人稱她為「眾神之母」庫柏勒。', xref: ['希臘羅馬大藏經 Λ 祕儀書（眾神之母）'] },
            { slug: 'lydian-sardis', title_zh: '呂底亞語宗教銘文', title_orig: 'Lydian inscriptions from Sardis', era: '前 6–4 世紀', language: '呂底亞語', provenance: '薩第斯', status: 'inscription', note: '向阿爾忒彌斯（呂底亞語 Artimuś）奉獻與詛咒褻瀆者的墓銘。' },
            { slug: 'letoon-trilingual', title_zh: '萊托翁三語碑', title_orig: 'Letoon trilingual', era: '前 337', language: '呂基亞語、古希臘文、亞蘭語', provenance: '桑索斯萊托神廟', status: 'inscription', note: '桑索斯城設立「考諾斯之王」等神的祭祀與祭司俸給，三種語言各記一次——一位神如何在三種宗教語言裡被稱呼。' },
          ],
        },
      ],
    },
  ],
}
