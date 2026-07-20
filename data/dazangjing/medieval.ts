import type { DazangEra } from './types'

// 中世紀基督教大藏經（三軌斷代，按時代精神：伊斯蘭交鋒與政教權之爭）
export const MEDIEVAL_ERA: DazangEra = {
  key: 'medieval',
  name: '中世紀基督教大藏經',
  name_en: 'Medieval Christian Canon',
  glyph: '中',
  subtitle: '經院哲學‧拜占庭靜修‧伊斯蘭交鋒‧政教博弈（三軌斷代）',
  boundary: '按時代精神斷代——伊斯蘭文明交鋒與政教權之爭即中世紀：拉丁西方 800–1500（卡爾大帝加冕）、拜占庭 787/843–1453（正統的勝利至君士坦丁堡陷落）、伊斯蘭交鋒區 622–1500。',
  enabled: true,
  collections: [
    {
  key: 'jing',
  name: '經藏',
  name_en: 'Scripture Pitaka',
  glyph: '經',
  genres: '聖經‧標準本‧註釋聖經',
  summary: '中世紀基督教世界的聖經與並立的他宗教啟示經典。依正典封閉法則，正經藏留白（武加大標準本、巴黎聖經與《通用註釋》等已歸譯校藏）；外經藏收伊斯蘭《古蘭經》與猶太馬所拉聖經兩大並立啟示傳統。',
  portal: { to: '/scripture', label: '聖經閱讀器' },
  zheng: {
    summary: '正典封閉法則：使徒時代新約正典封閉後，基督教不再有新「正經」。中世紀的武加大標準本、巴黎聖經與《通用註釋》等聖經文本與註釋傳承一律歸入譯校藏；此處正經藏留白。外經藏則收與基督教並立交鋒的伊斯蘭與猶太啟示經典。',
    divisions: [],
  },
  wai: {
    summary: '與基督教啟示並立的他宗教根本經典。中世紀拉丁西方與拜占庭在伊比利、西西里、近東與伊斯蘭、猶太兩大啟示傳統長期交鋒、論辯與翻譯，古蘭經與希伯來聖經是其神學對話與駁斥的核心文本。摩尼教與諾斯底經典已歸古代藏，不在此重複。',
    divisions: [
      {
        key: 'quran',
        label: '外經部‧伊斯蘭啟示',
        label_en: 'The Islamic Revelation',
        desc: '伊斯蘭教的根本啟示經典，中世紀基督教世界外藏之重頭。',
        works: [
          { title_zh: '古蘭經', title_orig: 'al-Qurʾān', author: '穆罕默德傳述', era: '610–632 結集‧奧斯曼定本約 650', place: '麥加‧麥地那', language: '阿拉伯文', intro: '《古蘭經》為伊斯蘭教根本經典，穆斯林信為真主於 610 至 632 年間經天使逐次降示穆罕默德之言，由先知口傳，第三任哈里發奧斯曼時期結集為定本。全書一百一十四章，以阿拉伯韻文寫成，涵蓋信仰、律法、敘事與訓誡。中世紀基督教世界視之為外藏之重頭：克呂尼院長尊者彼得於 1143 年主持首部拉丁譯本，使西方學者得以研讀並展開長期的護教論辯。它是與基督教聖經並立的另一啟示傳統的核心文本。' }
        ]
      },
      {
        key: 'masoretic',
        label: '外經部‧猶太啟示',
        label_en: 'The Jewish Revelation',
        desc: '猶太教的根本經典，中世紀基督徒希伯來文研究與護教論辯之對象。',
        works: [
          { title_zh: '馬所拉希伯來聖經', title_orig: 'Tanakh / Masoretic Text', author: '馬所拉學者(提比哩亞 Ben Asher 等)', era: '經文定型約 7–10 世紀', place: '提比哩亞(Tiberias)', language: '希伯來文(含少量亞蘭文)', intro: '馬所拉希伯來聖經是猶太教權威的希伯來正典文本，由七至十世紀提比哩亞的馬所拉學者（以 Ben Asher 家族最著）為輔音經文加注元音符號、誦讀記號與旁註，使口傳讀法固定化。它分律法、先知、聖卷三部，是猶太信仰與律法的根本。中世紀基督徒（如十二世紀聖維克托學派與後來的修士希伯來學者）藉研讀此文本核校武加大、展開與拉比的釋經論辯，亦是基督教希伯來文研究的源頭。' }
        ]
      }
    ]
  }
},
    {
  key: 'lu',
  name: '律藏',
  name_en: 'Discipline Pitaka',
  glyph: '律',
  genres: '會議‧教令‧教規‧會規',
  summary: '中世紀基督教世界的法規傳統：大公會議的信理與紀律裁定、教宗與法學家彙編的教會法、各修會的會規會憲，以及異端裁判的實踐手冊。外藏並陳伊斯蘭教法與猶太律法兩大平行法系，以及異端團體自身的紀律。',
  zheng: {
    summary: '拉丁西方 800–1500 的教會法規體系。由大公會議的權威裁定、教宗詔書與法學家的教令彙編（《教會法大全》之核心）、各修會的會規會憲，以及異端裁判的程序手冊構成，是中世紀教會治理與紀律的根本。',
    divisions: [
      {
        key: 'councils',
        label: '大公會議部',
        label_en: 'Ecumenical Councils',
        desc: '羅馬公教所數第 8 至 18 次大公會議（869–1517），其信理與紀律法規。',
        works: [
          { title_zh: '第四次君士坦丁堡會議(第八次大公會議)', title_orig: 'Concilium Constantinopolitanum IV', author: '教宗哈德良二世‧皇帝巴西爾一世', era: '869–870', place: '君士坦丁堡', language: '拉丁文‧希臘文', intro: '第四次君士坦丁堡會議為羅馬公教所數的第八次大公會議，由教宗哈德良二世與皇帝巴西爾一世共同召開，主要裁定罷黜牧首佛提烏、譴責其反對羅馬的立場，並重申聖像崇敬。其法規確立了此一時期教宗對東方教會的權威主張。然東正教不承認此會為大公會議，反以 879 年復佛提烏之會為正，故此會成為東西方教會分歧的早期標誌，在中世紀教會法中具重要地位。', link: '/creeds' },
          { title_zh: '第一次拉特朗會議(第九次大公會議)', title_orig: 'Concilium Lateranense I', author: '教宗卡利克斯特二世', era: '1123', place: '羅馬‧拉特朗', language: '拉丁文', intro: '第一次拉特朗會議是西方拉丁教會召開的首次大公會議，由教宗卡利克斯特二世主持，旨在確認結束敘任權之爭的《沃爾姆斯協約》。會議頒布多條教規，禁止買賣聖職、重申神職獨身、規範教產與教會選舉。它標誌教宗改革（格里高利改革）成果的鞏固，確立教會在屬靈職務任命上的自主，是中世紀教會法的重要里程碑。', link: '/creeds' },
          { title_zh: '第二次拉特朗會議(第十次大公會議)', title_orig: 'Concilium Lateranense II', author: '教宗英諾森二世', era: '1139', place: '羅馬‧拉特朗', language: '拉丁文', intro: '第二次拉特朗會議由教宗英諾森二世召開，旨在終結阿納克萊圖斯二世對立教宗造成的分裂，恢復教會統一。會議頒布近三十條教規，重申禁止買賣聖職、強化神職獨身（宣告已婚神職的婚姻無效）、譴責放高利貸與比武，並懲處布雷西亞的阿諾德等改革派。它鞏固了教宗權威，是中世紀盛期教會紀律立法的重要成果。', link: '/creeds' },
          { title_zh: '第三次拉特朗會議(第十一次大公會議)', title_orig: 'Concilium Lateranense III', author: '教宗亞歷山大三世', era: '1179', place: '羅馬‧拉特朗', language: '拉丁文', intro: '第三次拉特朗會議由教宗亞歷山大三世召開，於結束與皇帝腓特烈一世的分裂後重建秩序。其最著名法規規定教宗須由樞機團三分之二多數選出，奠定此後教宗選舉的基本制度。會議亦規範主教年齡、設立教座學校、譴責瓦勒度派與卡特里派異端。它在教會選舉法與反異端立法上影響深遠，是中世紀教會法發展的關鍵會議。', link: '/creeds' },
          { title_zh: '第四次拉特朗會議(第十二次大公會議)', title_orig: 'Concilium Lateranense IV', author: '教宗英諾森三世', era: '1215', place: '羅馬‧拉特朗', language: '拉丁文', intro: '第四次拉特朗會議由教宗英諾森三世召開，是中世紀規模最大、影響最深的會議。其七十條教令首次以官方術語界定「變體」(transubstantiation)、規定信徒每年至少告解領聖體一次、譴責卡特里與瓦勒度異端、規範猶太人與穆斯林服飾標識，並推動新一輪十字軍。它系統地確立中世紀盛期的信理與紀律，是教宗權力與教會法的巔峰之作。', link: '/creeds' },
          { title_zh: '第一次里昂會議(第十三次大公會議)', title_orig: 'Concilium Lugdunense I', author: '教宗英諾森四世', era: '1245', place: '里昂', language: '拉丁文', intro: '第一次里昂會議由教宗英諾森四世於與皇帝腓特烈二世激烈衝突之際召開，會議正式宣布廢黜腓特烈二世的皇位，譴責其侵犯教會。會議亦討論應對蒙古入侵與聖地危機，並頒布若干教會紀律法規。它是教宗以大公會議行使對世俗君主最高裁判權的鮮明案例，反映中世紀教俗權力鬥爭的高峰。', link: '/creeds' },
          { title_zh: '第二次里昂會議(第十四次大公會議)', title_orig: 'Concilium Lugdunense II', author: '教宗額我略十世', era: '1274', place: '里昂', language: '拉丁文', intro: '第二次里昂會議由教宗額我略十世召開，最重要成果是與拜占庭使節達成東西方教會的暫時合一（雖未能持久）。會議制定教宗選舉「閉門會議」(conclave)制度以防選位空懸過久，規範托缽修會，並籌劃新十字軍。波那文圖拉出席並逝於會中，多瑪斯·阿奎那則卒於赴會途中。它在教會合一與選舉制度上影響深遠。', link: '/creeds' },
          { title_zh: '維埃納會議(第十五次大公會議)', title_orig: 'Concilium Viennense', author: '教宗克勉五世', era: '1311–1312', place: '維埃納', language: '拉丁文', intro: '維埃納會議由身處亞維農的教宗克勉五世召開，在法王腓力四世施壓下解散聖殿騎士團，沒收其財產轉予醫院騎士團。會議亦譴責方濟會內部「屬靈派」對使徒貧窮的激進主張、處理自由靈異端，並頒布有關教會改革與東方語言教席的法規。它深刻反映亞維農時期教宗受法國王權左右的處境。', link: '/creeds' },
          { title_zh: '康斯坦茨會議(第十六次大公會議)', title_orig: 'Concilium Constantiense', author: '教宗額我略十二世退位‧馬丁五世當選', era: '1414–1418', place: '康斯坦茨', language: '拉丁文', intro: '康斯坦茨會議召開以終結西方大分裂，當時羅馬、亞維農、比薩三位教宗並立。會議罷黜並安排退位，選出馬丁五世重歸統一。其法令《神聖》(Haec Sancta)宣告大公會議權力高於教宗（會議至上論），並判處胡斯為異端火刑、譴責威克里夫。它是中世紀晚期教會危機與會議運動的核心事件，影響後世教會憲政之爭。', link: '/creeds' },
          { title_zh: '巴塞爾—費拉拉—佛羅倫斯會議(第十七次大公會議)', title_orig: 'Concilium Basiliense-Ferrariense-Florentinum', author: '教宗尤金四世', era: '1431–1445', place: '巴塞爾‧費拉拉‧佛羅倫斯', language: '拉丁文‧希臘文', intro: '此會先於巴塞爾召開以延續改革與會議至上主張，後因與教宗尤金四世衝突而遷至費拉拉、佛羅倫斯。其在佛羅倫斯階段達成與東正教、亞美尼亞、科普特等教會的合一協議（雖多未能持久），並界定煉獄、聖靈雙發等教義。會議至上派則在巴塞爾另立對立教宗。它是教會合一努力與教宗對抗會議運動的關鍵戰場。', link: '/creeds' },
          { title_zh: '第五次拉特朗會議(第十八次大公會議)', title_orig: 'Concilium Lateranense V', author: '教宗儒略二世‧良十世', era: '1512–1517', place: '羅馬‧拉特朗', language: '拉丁文', intro: '第五次拉特朗會議由教宗儒略二世召開、良十世續行，旨在反制法王支持的比薩分裂會議並推動教會改革。會議重申教宗權高於大公會議、譴責靈魂可朽論、規範印刷出版審查，並通過與法國的《波隆那教務專約》。然其改革法令多流於空文，會議閉幕僅數月後馬丁·路德即發起九十五條論綱，宗教改革旋即爆發。', link: '/creeds' },
          { title_zh: '亞琛會議法令', title_orig: 'Institutio canonicorum Aquisgranensis', author: '亞琛改革會議（虔誠者路易召集）', era: '816–817', place: '亞琛', language: '拉丁文', intro: '虔誠者路易召集的亞琛會議為座堂教士與修女團體制定的生活規章。加洛林教會改革的立法高峰，「詠禮司鐸」制度的奠基文件。' },
          { title_zh: '上帝的和平與休戰法令', title_orig: 'Pax et Treuga Dei', author: '沙魯／圖盧日等地方會議', era: '989 起', place: '亞奎丹', language: '拉丁文', intro: '法蘭西主教會議宣告保護非武裝者、限定徵戰日期的和平法令，違者絕罰。教會以屬靈制裁馴化封建暴力的運動文本，中世紀和平理念的制度嘗試。' },
          { title_zh: '克萊蒙會議法令', title_orig: 'Concilium Claromontanum', author: '教宗烏爾班二世主持', era: '1095', place: '克萊蒙', language: '拉丁文', intro: '烏爾班二世宣講收復聖地並頒赦罪之恩的會議，「上帝所願」呼聲由此而起。第一次十字軍的發動文件，贖罪制度與聖戰觀念交會的法律時刻。' },
          { title_zh: '倫敦會議法令（1102）', title_orig: 'Concilium Londoniense (1102)', author: '坎特伯裡總主教安瑟倫主持', era: '1102', place: '倫敦西敏', language: '拉丁文', intro: '安瑟倫主持的倫敦會議法令，首度明文譴責販賣英格蘭人為奴的貿易。中世紀教會反奴隸買賣的先聲條文，改革派主教立法的代表案例。' },
          { title_zh: '神聖會議法令', title_orig: 'Haec sancta synodus', author: '康斯坦茨大公會議', era: '1415', place: '康斯坦茨', language: '拉丁文', parent: '康斯坦茨會議(第十六次大公會議)', intro: '康斯坦茨會議宣告大公會議權柄直接來自基督、教宗亦當服從的法令。公會議主義的憲章文本，其效力之爭至今仍是教會學的活問題。' },
          { title_zh: '頻仍法令', title_orig: 'Frequens', author: '康斯坦茨大公會議', era: '1417', place: '康斯坦茨', language: '拉丁文', parent: '康斯坦茨會議(第十六次大公會議)', intro: '康斯坦茨會議規定大公會議須定期召開的法令，欲使會議成為教會常設憲政機制。公會議主義的制度設計，後為教宗復權運動束之高閣。' },
          { title_zh: '比薩會議法令', title_orig: 'Concilium Pisanum', author: '兩系樞機聯合召集', era: '1409', place: '比薩', language: '拉丁文', intro: '兩系樞機為終結大分裂聯合召開的會議，廢黜兩教宗另立其一，反致三宗鼎立。公會議路線的初次實驗，康斯坦茨最終解決的失敗序章。' },
          { title_zh: '布拉格四條款', title_orig: 'Čtyři artikuly pražské', author: '胡斯派聯合綱領', era: '1420', place: '布拉格', language: '捷克文／拉丁文', intro: '胡斯派各翼共同的四條綱領：自由講道、平信徒領杯、教產充公與公罪公罰。捷克宗教革命的憲章，聖杯派身分的信仰旗幟。' },
          { title_zh: '巴塞爾公約', title_orig: 'Compactata Basileensia', author: '巴塞爾會議與胡斯派代表', era: '1436', place: '巴塞爾／伊赫拉瓦', language: '拉丁文／捷克文', intro: '巴塞爾會議與溫和胡斯派達成的和解公約，允波希米亞平信徒領杯。大公會議與「異端」談判成約的孤例，中歐宗教和平的先驅文件。' },
          { title_zh: '一二七七年巴黎譴責', title_orig: 'Condemnatio Parisiensis (1277)', author: '巴黎主教唐皮耶', era: '1277', place: '巴黎', language: '拉丁文', intro: '唐皮耶主教譴責二百一十九條亞里斯多德主義命題的法令，波及阿奎那部分論題。信仰與哲學邊界的著名劃線，中世紀科學思想史的爭議轉折點。' },
          { title_zh: '黑衣修士會議譴責法令', title_orig: 'Blackfriars Council (1382)', author: '坎特伯裡總主教考特尼主持', era: '1382', place: '倫敦黑衣修士院', language: '拉丁文', intro: '考特尼主持譴責威克里夫二十四條命題的會議，地震適至而得「地震會議」之名。羅拉德運動遭壓制的法律開端，宗教改革前史的英格蘭一頁。' },
          { title_zh: '巴黎大學章程', title_orig: 'Statuta Universitatis Parisiensis (Robertus de Courçon)', author: '教廷使節羅貝爾‧德‧庫爾松', era: '1215', place: '巴黎', language: '拉丁文', intro: '教廷使節為巴黎大學頒定的章程，課程、學位與教師資格成文。中世紀大學建制的代表文件，教會孕育大學體制的法律見證。' }
        
        ]
      },
      {
        key: 'eastern-synods',
        label: '東方教會會議與會憲部',
        label_en: 'Oriental Church Synods and Canons',
        desc: '科普特、敘利亞、亞美尼亞、衣索比亞與東方亞述等非迦克墩／東方教會在伊斯蘭與蒙古治下召開的宗主教會議，及其彙編的教會法憲。',
        works: [
          { title_zh: '提摩太一世東方教會會議', title_orig: 'Synods under Patriarch Timothy I', author: '東方亞述教會大公牧首提摩太一世', era: '約 790–823', place: '巴格達', language: '敘利亞文', intro: '提摩太一世為阿巴斯王朝治下東方教會（景教）的大公牧首，駐節巴格達。他召開多次宗主教會議，整頓教會法、規範主教選立與修道紀律，並大力推動向中亞、印度與中國的宣教。其會議決議與書信續補了《東方會議集》，鞏固了東方教會在伊斯蘭帝國中的組織與自治。提摩太一世任內是東方教會傳教擴張與制度成熟的高峰。' },
          { title_zh: '科普特教會法大全', title_orig: 'al-Majmūʿ al-Ṣafawī', author: '薩菲‧伊本‧阿薩爾(al-Ṣafī ibn al-ʿAssāl)', era: '約 1238', place: '埃及開羅', language: '阿拉伯文', intro: '科普特學者薩菲‧伊本‧阿薩爾彙編的教會法大全，將歷代大公會議與地方會議教規、使徒教規、宗主教裁決及拜占庭民法整理為體系化的阿拉伯文法典。它成為科普特正教會官方的教會法準繩，並為衣索比亞教會所採用（即吉茲文《王法 Fetha Nagast》的根源）。此書是中世紀科普特教會在伊斯蘭治下整理自身律法傳統的集大成之作。' },
          { title_zh: '巴爾‧赫布雷烏斯教會法典(指南書)', title_orig: 'Ktābā d-Hudāyē (Nomocanon)', author: '巴爾‧赫布雷烏斯(Bar Hebraeus)', era: '13 世紀', place: '美索不達米亞', language: '敘利亞文', intro: '敘利亞正教會東方瑪弗里安巴爾‧赫布雷烏斯編纂的教會法典，敘利亞文名《指南書》。全書分四十章，系統整理敘利亞正教（雅各派）的教會法規與世俗法，涵蓋教會體制、聖職、婚姻、繼承與訴訟。它是西敘利亞傳統最完整、最具權威的法典，長期作為敘利亞正教會的法律準據。巴爾‧赫布雷烏斯學識淵博，兼長神學、史學與科學，此書是其法學代表作。' },
          { title_zh: '西斯會議與亞達納會議', title_orig: 'Councils of Sis (1307) and Adana (1316)', author: '奇里乞亞亞美尼亞使徒教會', era: '1307／1316', place: '奇里乞亞西斯', language: '亞美尼亞文', intro: '奇里乞亞亞美尼亞王國晚期，為換取拉丁西方對抗馬穆魯克的奧援，亞美尼亞使徒教會於西斯（1307）與亞達納（1316）兩度召開宗主教會議，議決在禮儀與教義上向羅馬教會靠攏。決議引發本土教會與大亞美尼亞神職的強烈反彈，合一終未持久。兩會議是中世紀東方教會在政治壓力下尋求與西方合一的代表性事件，深刻牽動亞美尼亞教會的認同之爭。' },
          { title_zh: '德布雷米特馬克會議', title_orig: 'Council of Debre Mitmaq', author: '衣索比亞正教（札拉‧雅各布皇帝召開）', era: '1450', place: '衣索比亞德布雷米特馬克', language: '吉茲文', intro: '衣索比亞皇帝札拉‧雅各布召開的全國教會會議，旨在平息困擾衣索比亞教會逾一世紀的「安息日之爭」。會議裁定基督徒當同守猶太安息日（週六）與主日（週日），調和了亞歷山卓科普特母會所反對的本土守安息傳統。此會議鞏固了王權對教會的主導，是中世紀衣索比亞正教制度與禮儀整合的關鍵，反映其獨特的猶太—基督教綜合特色。' },
          { title_zh: '佛提烏十四題法典', title_orig: 'Nomocanon XIV titulorum (recensio Photiana)', author: '君士坦丁堡牧首佛提烏（修訂本）', era: '883', place: '君士坦丁堡', language: '希臘文', intro: '教會法規與帝國法令按十四主題合編的法典，佛提烏修訂本成為拜占庭教會的標準法源。「法典-教規合編」體例的定型之作，東正教法制的千年骨架。' },
          { title_zh: '首次二次會議法規', title_orig: 'Synodus Prima-Secunda (861)', author: '君士坦丁堡會議（佛提烏主持）', era: '861', place: '君士坦丁堡聖使徒教堂', language: '希臘文', intro: '佛提烏首任內召開的大會議，十七條法規嚴整修道建院與主教紀律。拜占庭修道法制的重要立法，佛提烏與羅馬爭端的序幕場景。' },
          { title_zh: '聖索菲亞會議法令', title_orig: 'Synodus Sanctae Sophiae (879–880)', author: '君士坦丁堡會議', era: '879–880', place: '君士坦丁堡聖索菲亞', language: '希臘文', intro: '恢復佛提烏職位並獲羅馬使節與會確認的大會議，兼申信經不得增添。東方視之為第八次大公會議的候選，東西方共融最後的和解時刻之一。' },
          { title_zh: '靜修派會議法令', title_orig: 'Synodi Palamiticae (1341, 1347, 1351)', author: '君士坦丁堡歷次會議', era: '1341–1351', place: '君士坦丁堡', language: '希臘文', intro: '裁定帕拉瑪斯靜修神學為正統、確立神之本質與能量之分的歷次會議法令。晚期拜占庭神學的定調立法，正統禮儀年「帕拉瑪斯主日」的法源。' },
          { title_zh: '佐納拉斯教會法注釋', title_orig: 'Commentarii in canones (Ioannes Zonaras)', author: '約翰‧佐納拉斯', era: '約 1130', place: '君士坦丁堡', language: '希臘文', intro: '史家佐納拉斯遍注歷代會議法規的注釋全集，考訂立法本意而直言時弊。拜占庭教會法學三大家之首，正教法規詮釋的基準著作。' },
          { title_zh: '巴爾薩蒙教會法注釋', title_orig: 'Commentarii in Nomocanonem (Theodorus Balsamon)', author: '安提阿牧首巴爾薩蒙', era: '約 1170–1195', place: '君士坦丁堡', language: '希臘文', intro: '巴爾薩蒙奉敕注釋法典與教規全帙，兼答各方教律疑問。拜占庭法學的集大成者，帝國法與教會法關係的權威裁量。' },
          { title_zh: '布拉斯塔雷斯字母法規大全', title_orig: 'Syntagma alphabeticum (Matthaeus Blastares)', author: '馬太‧布拉斯塔雷斯', era: '1335', place: '帖撒羅尼迦', language: '希臘文', intro: '按希臘字母排列主題的教會法便覽，僧侶布拉斯塔雷斯為實務檢索而編。拜占庭法學的普及化定本，旋譯入斯拉夫世界沿用數百年。' },
          { title_zh: '弗拉基米爾與雅羅斯拉夫教會規章', title_orig: 'Церковные уставы Владимира и Ярослава', author: '基輔大公弗拉基米爾與雅羅斯拉夫', era: '11 世紀', place: '基輔', language: '教會斯拉夫文', intro: '基輔羅斯兩代大公劃定教會法庭管轄與什一奉獻的規章。斯拉夫政教關係的奠基文件，羅斯受洗後教會建制的法律見證。' },
          { title_zh: '掌舵書', title_orig: 'Кормчая книга', author: '斯拉夫教會（譯編自拜占庭法典）', era: '13 世紀（1274 弗拉基米爾會議採行）', place: '塞爾維亞／羅斯', language: '教會斯拉夫文', intro: '拜占庭教會法典的斯拉夫譯編本，以「掌舵」喻導引教會之船。羅斯與巴爾幹教會數百年的法律聖書，斯拉夫法制史的源頭文獻。' },
          { title_zh: '薩瓦法典', title_orig: 'Законоправило светог Саве (Zakonopravilo)', author: '塞爾維亞首任總主教聖薩瓦', era: '1219', place: '塞爾維亞', language: '教會斯拉夫文', intro: '聖薩瓦為新獲自主的塞爾維亞教會編譯的教會-民事法典。塞爾維亞教會自立的法律基石，斯拉夫掌舵書系的權威定本。' },
          { title_zh: '亞美尼亞法典', title_orig: 'Datastanagirk\' (Mkhitar Gosh)', author: '姆希塔爾‧戈什', era: '約 1184', place: '亞美尼亞', language: '亞美尼亞文', intro: '修士戈什編纂的亞美尼亞教會-民事法典，教規與習慣法熔於一爐。無主權時代亞美尼亞人的自治法源，後隨僑社行用至波蘭與印度。' },
          { title_zh: '引導之書', title_orig: 'Kitāb al-Hudā', author: '馬龍派教會（阿拉伯文法典彙編）', era: '1059', place: '黎巴嫩山', language: '阿拉伯文', intro: '馬龍派彙譯教規與教義訓示的阿拉伯文法典。伊斯蘭統治下山地教會的自治法本，馬龍派中世紀法制僅存的重要見證。' },
          { title_zh: '普雷斯拉夫會議決議', title_orig: 'Преславски събор (893)', author: '保加利亞會議（鮑里斯與西美昂治下）', era: '893', place: '普雷斯拉夫', language: '教會斯拉夫文', intro: '保加利亞遷都普雷斯拉夫並定斯拉夫語為教會與國家用語的大會議。斯拉夫禮儀文明的立國決議，古教會斯拉夫文黃金時代的制度起點。' },
          { title_zh: '魯伊斯-烏爾布尼西會議法規', title_orig: 'რუის-ურბნისის კრება', author: '喬治亞教會會議（建設者大衛召集）', era: '1103', place: '喬治亞魯伊斯', language: '喬治亞文', intro: '建設者大衛召集整頓喬治亞教會的大會議，罷黜失格主教並嚴訂敘任紀律。喬治亞黃金時代的教會憲章，高加索基督教法制的代表文獻。' },
          { title_zh: '奎隆銅板特許狀', title_orig: 'Tharisāppaḷḷi Copper Plates', author: '文奈杜王阿雅安（頒予敘利亞教會）', era: '849', place: '印度奎隆', language: '古馬拉雅拉姆文／波斯文簽署', intro: '南印度王室頒予聖多馬基督徒教會土地與特權的銅板文書，附波斯、阿拉伯與猶太商人簽署見證。印度教會最古的法律實物，馬拉巴海岸多元共處的第一手見證。' }
        
        ]
      },
      {
        key: 'decretals',
        label: '教令部',
        label_en: 'Decretals and Canon Law',
        desc: '法學家彙編的教會法與教宗詔書，構成《教會法大全》。',
        works: [
          { title_zh: '格拉提安教令集(歧異教規之調和)', title_orig: 'Decretum Gratiani / Concordia Discordantium Canonum', author: '格拉提安(Gratianus)', era: '約 1140', place: '波隆那', language: '拉丁文', intro: '《教令集》是法學家格拉提安在波隆那編纂的教會法巨著，原名《歧異教規之調和》，蒐羅歷代會議教規、教父言論、教宗裁決與羅馬法，並以辯證方法調和其中的矛盾。它將散亂的教會法整理成體系化教本，開創教會法學為獨立學科，成為大學講授的基礎教材。雖非官方法典，卻是《教會法大全》的核心首部，奠定整個中世紀教會法的根基。' },
          { title_zh: '額我略九世教令集', title_orig: 'Decretales Gregorii IX / Liber Extra', author: '教宗額我略九世命雷蒙·德·佩尼亞福特編', era: '1234', place: '羅馬', language: '拉丁文', intro: '《額我略九世教令集》（又稱《集外篇》）由教宗額我略九世委任道明會法學家雷蒙·德·佩尼亞福特彙編，收錄格拉提安《教令集》之後的教宗教令與會議法規，刪汰過時、整理成五卷（審判、聖職、婚姻等主題）。它是首部由教宗權威頒布、具普遍約束力的官方教會法典，取代此前的私人彙編，成為中世紀教會法的標準法源，地位至為崇高。' },
          { title_zh: '卜尼法八世教令第六書', title_orig: 'Liber Sextus', author: '教宗卜尼法八世', era: '1298', place: '羅馬', language: '拉丁文', intro: '《第六書》由教宗卜尼法八世頒布，續補《額我略九世教令集》五卷之後的新教令，故稱「第六書」。它整理了里昂會議以來的法規與教宗裁決，並附著名的法律格言彙編。此書是《教會法大全》的重要組成，反映中世紀盛期教宗立法的成熟，卜尼法八世亦藉以強化教宗至上的主張，後與法王腓力四世的衝突即與此相關。' },
              { title_zh: '列王律法', title_orig: 'Fetḥa Nagast (Law of the Kings)', author: '輯自伊本‧阿薩爾教會法（Ibn al-ʿAssāl）等', era: '約 13 世紀彙編、15 世紀傳入衣索匹亞', place: '埃及→衣索匹亞', language: '阿拉伯文→吉茲文', intro: '衣索匹亞教會與帝國長期奉行的教會兼民事法典，源出十三世紀科普特學者伊本‧阿薩爾以阿拉伯文編纂的教會法總集，後譯為吉茲文傳入衣索匹亞，兼採使徒憲章、大公會議教規與羅馬—拜占庭民法。內容含教會聖統、聖事、婚姻、繼承、契約與刑罰諸法，作為帝國根本法直行至二十世紀，是研究東方教會法與衣索匹亞政教制度的核心文獻。' },
          { title_zh: '偽伊西多爾教令集', title_orig: 'Decretales Pseudo-Isidorianae', author: '佚名（法蘭克教士群，託名塞維亞的伊西多爾）', era: '約 850', place: '蘭斯一帶', language: '拉丁文', intro: '法蘭克教士假託古教宗名義偽造的大型教令集，維護主教免受都主教與世俗權侵奪。中世紀最成功的偽文書工程，君士坦丁贈禮亦廁身其中，教宗權理論意外的助產士。' },
          { title_zh: '雷吉諾教會紀律二書', title_orig: 'De synodalibus causis et disciplinis ecclesiasticis', author: '普呂姆的雷吉諾', era: '約 906', place: '特里爾', language: '拉丁文', intro: '雷吉諾為主教巡察教區編纂的法規問答手冊，兼收著名的「夜騎婦人」條目。加洛林之後教會法整編的先驅，主教視察制度的操作指南。' },
          { title_zh: '布爾夏德教令集', title_orig: 'Decretum Burchardi', author: '沃姆斯主教布爾夏德', era: '約 1012–1023', place: '沃姆斯', language: '拉丁文', intro: '布爾夏德輯錄兩千餘條教規的二十卷教令集，第十九卷「糾正者」為著名的懺悔則例。格拉提安之前最通行的教會法典，中世紀民間信仰研究的意外寶庫。' },
          { title_zh: '伊沃教令集', title_orig: 'Decretum et Panormia Ivonis', author: '沙特爾主教伊沃', era: '約 1094', place: '沙特爾', language: '拉丁文', intro: '伊沃輯纂的教令集及其通行縮編本，序言提出寬嚴互濟的法律解釋原則。敘任權之爭中調和路線的法學基礎，格拉提安方法論的直接先驅。' },
          { title_zh: '克萊孟教令集', title_orig: 'Constitutiones Clementinae', author: '教宗克萊孟五世（若望二十二世頒行）', era: '1317', place: '亞維儂', language: '拉丁文', intro: '克萊孟五世彙整維埃納會議法令與本朝教令的法典，身後由若望二十二世頒行。教會法大全的第四部件，亞維儂教廷立法的代表成果。' },
          { title_zh: '若望二十二世常行教令', title_orig: 'Extravagantes Johannis XXII', author: '教宗若望二十二世', era: '1325 輯', place: '亞維儂', language: '拉丁文', intro: '若望二十二世流通教令的彙編，因行於法典之外得名「常行教令」。與《共通常行教令》同補教會法大全的末篇，中世紀教宗立法的收尾卷帙。' },
          { title_zh: '林德伍德教省法規彙編', title_orig: 'Provinciale (seu Constitutiones Angliae)', author: '威廉‧林德伍德', era: '1433', place: '倫敦', language: '拉丁文', intro: '林德伍德輯注坎特伯裡教省歷代法規的彙編，逐條附學理注釋。中世紀英格蘭教會法的總集，英國教會法學的奠基文本。' },
          { title_zh: '喬巴姆聽告解大全', title_orig: 'Summa confessorum (Thomas de Chobham)', author: '託馬斯‧喬巴姆', era: '約 1216', place: '索爾茲伯裡', language: '拉丁文', intro: '喬巴姆為聽告解司鐸編寫的實務大全，職業倫理逐行業剖析。拉特朗四世年度告解制的配套手冊，中世紀日常道德生活的透視鏡。' },
          { title_zh: '雷蒙德判例大全', title_orig: 'Summa de casibus poenitentiae', author: '佩尼亞福特的雷蒙德', era: '約 1224–1234', place: '巴塞隆納', language: '拉丁文', intro: '《額我略九世教令集》總編纂雷蒙德為告解實務撰寫的判例大全。教會法與良心法庭的接榫之作，道明會法學傳統的代表手冊。' },
          { title_zh: '霍斯蒂恩西斯金言大全', title_orig: 'Summa aurea (Hostiensis)', author: '蘇薩的亨利（霍斯蒂恩西斯樞機）', era: '約 1253', place: '巴黎／羅馬', language: '拉丁文', intro: '教會法學巨擘霍斯蒂恩西斯系統疏解教令法的大全，以文筆金聲玉振得名。中世紀教會法學的頂峰著作，「教宗權充盈」理論的經典表述。' }
        
        ]
      },
      {
        key: 'monastic-rules',
        label: '修會會規部',
        label_en: 'Monastic and Mendicant Rules',
        desc: '中世紀各修會、托缽會的會規與會憲。',
        works: [
          { title_zh: '熙篤會憲章(愛德憲章)', title_orig: 'Carta Caritatis', author: '熙篤會創立者(傳斯蒂芬·哈丁 Stephen Harding)', era: '約 1114–1119', place: '熙篤(Cîteaux)', language: '拉丁文', intro: '《愛德憲章》是熙篤會的根本會憲，在遵行本篤會規之外，確立熙篤各院之間的聯合架構：母院對子院的視察、年度全體院長大會、以及以「愛德」而非財產隸屬維繫的聯合。它主張回歸本篤精神，強調勞動、簡樸與隱修。此憲章創設了跨院的修會聯邦治理模式，影響後世眾多修會組織，是中世紀修道改革的制度典範。' },
          { title_zh: '方濟會規(定型會規)', title_orig: 'Regula Bullata', author: '亞西西的方濟各(Franciscus Assisiensis)', era: '1223', place: '亞西西‧羅馬', language: '拉丁文', intro: '《定型會規》是方濟各於 1223 年定稿、經教宗何諾三世以詔書批准的方濟會正式會規。它規定弟兄們效法基督的貧窮，不擁有任何財產、托缽行乞、巡迴宣道，並服從教會與會內長上。相較早期較長的會規，此本更簡要而具法律效力。它界定了托缽修會的全新生活形態，使「使徒貧窮」制度化，後因詮釋分歧引發會內「屬靈派」與「住院派」的長期爭論。' },
          { title_zh: '道明會憲章', title_orig: 'Constitutiones Ordinis Praedicatorum', author: '道明(Dominicus)及早期總會', era: '約 1216–1228', place: '土魯斯‧波隆那', language: '拉丁文', intro: '道明會憲章是宣道兄弟會（道明會）的根本法規，在採用奧斯定會規之外另立會憲，規定以宣道與救靈為宗旨、重視神學研讀、實行托缽貧窮，並建立以總會、省會、各院議會逐級代議與選舉的治理制度。其代議式架構被譽為中世紀最先進的修會憲政之一。它使學術研究與宣道使命制度化，深刻影響經院神學的興盛（阿奎那、大阿爾伯特皆出此會）。' },
          { title_zh: '加爾都西會規(慣例集)', title_orig: 'Consuetudines Cartusiae', author: '加爾都西會圭格一世(Guigo I)', era: '約 1127', place: '大沙特勒斯(Grande Chartreuse)', language: '拉丁文', intro: '《慣例集》是加爾都西會第五任院長圭格一世彙編成文的會規，記錄此前隱修慣例，確立加爾都西獨特的「半隱修」生活：會士各居獨立小室、多數時間於室內獨自祈禱勞作研讀，僅部分時刻共聚禮儀。它將嚴格的緘默、獨居與本篤式團體生活相結合，會規以從不改革著稱（其銘言謂「從未改革，因從未敗壞」），是中世紀最嚴苦的隱修傳統之根本文獻。' },
          { title_zh: '克呂尼慣例集', title_orig: 'Consuetudines Cluniacenses', author: '克呂尼修士伯爾納與烏爾裡希（輯錄）', era: '11 世紀', place: '克呂尼', language: '拉丁文', intro: '克呂尼修院日課、禮儀與院務慣例的成文輯錄，詳至燭火與手勢暗語。本篤會規的克呂尼實施細則，中世紀修道日常最細密的白描。' },
          { title_zh: '阿尼安改革法令', title_orig: 'Capitulare monasticum (817)', author: '阿尼安的本篤主導、亞琛會議頒', era: '817', place: '亞琛', language: '拉丁文', intro: '阿尼安的本篤推動帝國全境修院一體遵行本篤會規的法令。「一規一慣例」的加洛林修道統一工程，本篤會規獨尊地位的法律確立。' },
          { title_zh: '熙篤會總會議法規集', title_orig: 'Statuta capitulorum generalium Ordinis Cisterciensis', author: '熙篤會歷年總會議', era: '1134 起輯錄', place: '熙篤', language: '拉丁文', intro: '熙篤會年度總會議決議的累積法規集，農莊經營至抄書規範鉅細靡遺。愛德憲章之下的動態立法，中世紀跨國組織治理的檔案標本。' },
          { title_zh: '普雷蒙特雷會規章', title_orig: 'Statuta Ordinis Praemonstratensis', author: '普雷蒙特雷會（聖諾伯特創始）', era: '約 1140 成文', place: '普雷蒙特雷', language: '拉丁文', intro: '諾伯特所創詠禮司鐸會的規章，奧斯定會規之上疊加熙篤式總會議制。修道嚴規與牧靈使命結合的體制設計，白衣詠禮司鐸的生活法度。' },
          { title_zh: '聖殿騎士團會規', title_orig: 'Regula pauperum commilitonum Christi Templique Salomonici', author: '特魯瓦會議頒（伯爾納鐸襄贊）', era: '1129', place: '特魯瓦', language: '拉丁文／古法文', intro: '特魯瓦會議為聖殿騎士團頒定的會規，修道三願與軍事紀律熔鑄一體。「新騎士制度」的法律文本，修士武人這一中世紀悖論的章程化。' },
          { title_zh: '醫院騎士團會規', title_orig: 'Regula Hospitalariorum (Raymond du Puy)', author: '雷蒙‧杜‧皮伊', era: '約 1153', place: '耶路撒冷', language: '拉丁文', intro: '醫院騎士團首任總團長杜‧皮伊訂立的會規，「以病者為主」的服侍條文先於軍事職能。醫護修會法制的源頭文件，馬爾他騎士團傳統的根本章程。' },
          { title_zh: '條頓騎士團規章', title_orig: 'Statuten des Deutschen Ordens', author: '條頓騎士團', era: '約 1264 成文', place: '阿卡／普魯士', language: '中古德文／拉丁文', intro: '條頓騎士團的會規與慣例彙編，聖殿與醫院兩團法制的德語綜合。騎士修會治理波羅的海領邦的制度文本，德意志東向拓殖的規章側影。' },
          { title_zh: '克拉拉會規', title_orig: 'Regula Sanctae Clarae', author: '亞西西的克拉拉', era: '1253', place: '亞西西聖達彌盎', language: '拉丁文', intro: '克拉拉臨終前兩日獲教宗批准的會規，堅守徹底神貧不容產業。史上首部由女性為女修會撰寫並獲準的會規，方濟神貧理想的女性法典。' },
          { title_zh: '方濟非定型會規', title_orig: 'Regula non bullata', author: '亞西西的方濟', era: '1221', place: '亞西西', language: '拉丁文', intro: '方濟未經教宗璽印批准的早期會規，福音語句與勸勉交織近乎靈修文本。定型會規之前的原初理想文件，方濟精神最少修剪的法度形態。' },
          { title_zh: '方濟第三會規章', title_orig: 'Memoriale propositi (Regula Tertii Ordinis)', author: '方濟會第三會（尼各老四世 1289 定版）', era: '1221／1289', place: '義大利', language: '拉丁文', intro: '在俗信徒不離家庭職業而行悔改生活的第三會規章。平信徒修道理想的制度化容器，中世紀城市敬虔運動的法律外衣。' },
          { title_zh: '加爾默羅原始會規', title_orig: 'Regula Sancti Alberti', author: '耶路撒冷宗主教阿爾伯特', era: '約 1209', place: '迦密山', language: '拉丁文', intro: '阿爾伯特為迦密山隱士撰寫的簡短會規，獨居靜默晝夜默想主法。加爾默羅傳統的根本法度，大德蘭改革所回歸的「原始會規」本文。' },
          { title_zh: '布里吉特會規', title_orig: 'Regula Sancti Salvatoris', author: '瑞典的布里吉特（自述基督啟示）', era: '1370 獲准', place: '瓦茨泰納／羅馬', language: '拉丁文', intro: '布里吉特自陳得自基督啟示的救主會規，男女雙修院同屬女院長治理。北歐女先知的立法文本，中世紀晚期女性宗教權威的制度高峰。' },
          { title_zh: '共同生活弟兄會章程', title_orig: 'Consuetudines Fratrum Vitae Communis', author: '共同生活弟兄會（格羅特傳統）', era: '約 1380–1400', place: '德文特', language: '拉丁文', intro: '不發聖願而共財共住的平信徒團體章程，以抄書與辦學自養。新虔敬運動的制度容器，《效法基督》所出土壤的生活法度。' },
          { title_zh: '斯圖狄奧斯修院典章', title_orig: 'Typikon monasterii Studii', author: '斯圖狄奧斯的狄奧多若傳統', era: '9 世紀', place: '君士坦丁堡', language: '希臘文', intro: '狄奧多若整頓斯圖狄奧斯修院的典章傳統，日課勞動與抄書坊制度並詳。拜占庭修道復興的章程原型，東方典章文類的源頭之一。' },
          { title_zh: '聖山典章', title_orig: 'Typikon Athonis (Tragos)', author: '阿託斯修道長老會議（皇帝約翰一世確認）', era: '972', place: '阿託斯聖山', language: '希臘文', intro: '皇帝確認的阿託斯聖山首部典章，羊皮原件「山羊皮卷」猶存。修道共和國的建國憲法，千年聖山自治的法律起點。' },
          { title_zh: '艾弗格提斯修院典章', title_orig: 'Typikon Euergetidis', author: '艾弗格提斯修院（提摩太院長編）', era: '11 世紀末', place: '君士坦丁堡郊', language: '希臘文', intro: '君士坦丁堡艾弗格提斯修院的典章，禮儀與治理條文後為各地新院廣泛抄用。拜占庭修道法制的樣板文本，典章傳抄網絡的樞紐文件。' }
        
        ]
      },
      {
        key: 'inquisition',
        label: '裁判與實踐部',
        label_en: 'Inquisition and Practice',
        desc: '異端裁判的程序手冊與司法實踐文獻。',
        works: [
          { title_zh: '異端裁判實踐手冊', title_orig: 'Practica Inquisitionis Heretice Pravitatis', author: '伯爾納德·桂(Bernard Gui)', era: '約 1323–1324', place: '土魯斯', language: '拉丁文', intro: '《異端裁判實踐手冊》是道明會裁判官伯爾納德·桂依其多年審理經驗編成的程序指南，分述各異端派別（卡特里、瓦勒度、貝甘會、猶太改宗者等）的信仰特徵、審訊問答範例、判決與懲罰程式，以及裁判所的檔案與行政實務。它是研究中世紀異端裁判運作最重要的第一手文獻，系統呈現裁判程序如何制度化，在法制史與宗教史上均具核心價值。' },
          { title_zh: '艾梅里克裁判官指南', title_orig: 'Directorium Inquisitorum', author: '尼古拉‧艾梅里克', era: '1376', place: '亞維儂', language: '拉丁文', intro: '亞拉岡總裁判官艾梅里克集程序、法理與異端名錄於一書的指南，十六世紀經佩尼亞增注再版通行。裁判法學的系統化頂點，近代宗教審判的操作藍本。' },
          { title_zh: '女巫之槌', title_orig: 'Malleus Maleficarum', author: '海因裡希‧克拉馬（署名併斯普倫格）', era: '1486', place: '斯派爾', language: '拉丁文', intro: '克拉馬論證巫術實在、教示偵訊定罪之法的手冊，挾教宗詔書與神學院背書行世。獵巫時代最惡名昭彰的文本，性別偏見與司法暴力交織的黑暗經典。' },
          { title_zh: '富尼耶審訊登記簿', title_orig: 'Registre d\'Inquisition de Jacques Fournier', author: '帕米耶主教雅克‧富尼耶（後為本篤十二世）', era: '1318–1325', place: '帕米耶', language: '拉丁文（歐克語口供）', intro: '富尼耶主教審訊卡特里派殘餘的完整登記簿，村民口供鉅細靡遺。《蒙塔尤》所據的著名史料，中世紀庶民心態史的第一礦脈。' },
          { title_zh: '西班牙裁判所訓令', title_orig: 'Instrucciones del Santo Oficio (Torquemada)', author: '託爾克馬達', era: '1484', place: '塞維亞', language: '西班牙文', intro: '首任大裁判官託爾克馬達為新設西班牙裁判所頒定的程序訓令。王權裁判體制的組織法，近代國家宗教審查機器的第一份章程。' },
          { title_zh: '里昂窮人宣誓書', title_orig: 'Professio fidei Valdesii', author: '里昂的瓦勒度（宣誓文本）', era: '1180', place: '里昂', language: '拉丁文', intro: '商人瓦勒度在教廷使節前宣認正統信仰的誓文，隨後其運動仍遭絕罰。瓦勒度派歷史的第一份法律文件，貧窮運動與教制衝突的起點見證。' }
        
        ]
      },
      {
        key: 'papal-bulls',
        label: '教宗詔書與特許部',
        label_en: 'Papal Bulls and Privileges',
        desc: '中世紀教宗詔書、協約與特許狀，教宗權運作的法律文書。',
        works: [
          { title_zh: '主的名義法令', title_orig: 'In nomine Domini', author: '教宗尼各老二世', era: '1059', place: '拉特朗', language: '拉丁文', intro: '尼各老二世將教宗選舉權收歸樞機團的法令，排除皇帝與羅馬貴族幹預。教宗選舉制度的奠基文件，額我略改革的第一聲號角。' },
          { title_zh: '沃姆斯協約', title_orig: 'Concordatum Wormatiense', author: '教宗加里斯都二世與皇帝亨利五世', era: '1122', place: '沃姆斯', language: '拉丁文', intro: '教宗與皇帝就主教敘任權達成的協約，屬靈授職與世俗封授分離。半世紀敘任權之爭的和解文件，近代政教二元論的中世紀根源。' },
          { title_zh: '克呂尼創建特許狀', title_orig: 'Charta fundationis Cluniacensis', author: '亞奎丹公爵虔誠者威廉', era: '910', place: '克呂尼', language: '拉丁文', intro: '威廉公爵捐建克呂尼修院並宣告其僅屬聖彼得、免受一切俗權與主教管轄的特許狀。修道自由的憲章文本，兩百年克呂尼改革帝國的出生證書。' },
          { title_zh: '遇險之際憲章', title_orig: 'Ubi periculum', author: '教宗額我略十世（第二次里昂會議頒）', era: '1274', place: '里昂', language: '拉丁文', intro: '額我略十世制定教宗選舉閉門會議制的憲章，樞機遲不決者遞減飲食。三年空位危機催生的制度發明，「conclave」一詞與制度的法律起點。' },
          { title_zh: '廢除異端詔書', title_orig: 'Ad abolendam', author: '教宗路爵三世', era: '1184', place: '維羅納', language: '拉丁文', intro: '路爵三世與皇帝腓特烈一世協同頒布的反異端教令，令主教定期巡查並開列必究教派名單。主教裁判制度的奠基文件，中世紀壓制異端法制的起點。' },
          { title_zh: '剷除詔書', title_orig: 'Ad extirpanda', author: '教宗依諾增爵四世', era: '1252', place: '佩魯賈', language: '拉丁文', intro: '依諾增爵四世授權裁判所對異端嫌疑人施用刑訊的詔書，並命城邦政權配合執行。裁判制度最黑暗的法律授權，中世紀司法與信仰強制交纏的標記。' },
          { title_zh: '猶太人保護詔書', title_orig: 'Sicut Judaeis', author: '歷代教宗（加里斯都二世起反覆重頒）', era: '1120 起', place: '羅馬', language: '拉丁文', intro: '歷代教宗重頒的猶太人保護詔書，禁止強迫受洗、傷害人身與侵奪財產。中世紀反猶暴潮中的法律堤防，教會對猶太政策雙面性的正面一頁。' },
          { title_zh: '最深切願望詔書', title_orig: 'Summis desiderantes affectibus', author: '教宗依諾增爵八世', era: '1484', place: '羅馬', language: '拉丁文', intro: '依諾增爵八世授權克拉馬與斯普倫格在德意志追訴行巫者的詔書。獵巫運動的教廷背書文件，兩年後《女巫之槌》即挾之而行。' },
          { title_zh: '可憎之事詔書', title_orig: 'Execrabilis', author: '教宗庇護二世', era: '1460', place: '曼圖亞', language: '拉丁文', intro: '庇護二世宣告凡越過教宗上訴大公會議者絕罰的詔書，昔日的公會議派健將親手封殺公會議主義。十五世紀教宗復權的法律句點，立場逆轉的著名個案。' },
          { title_zh: '奧斯定隱修會聯合詔書', title_orig: 'Licet ecclesiae catholicae', author: '教宗亞歷山大四世', era: '1256', place: '羅馬', language: '拉丁文', intro: '亞歷山大四世將義大利諸隱修團體合併為奧斯定隱修會的詔書。託缽修會第四支的誕生文件，日後路德所出修會的法律起點。' },
          { title_zh: '藉可敬弟兄詔書', title_orig: 'Per venerabilem', author: '教宗依諾增爵三世', era: '1202', place: '羅馬', language: '拉丁文', intro: '依諾增爵三世致蒙彼利埃伯爵、闡發教宗於世俗事務「因罪介入」權的教令。中世紀教宗權法理的關鍵條文，後入額我略九世教令集成為經典判例。' },
          { title_zh: '祂知曉詔書', title_orig: 'Novit ille', author: '教宗依諾增爵三世', era: '1204', place: '羅馬', language: '拉丁文', intro: '依諾增爵三世介入英法戰爭、主張教宗有權審斷君王涉罪之爭的教令。教宗仲裁世俗政爭的理論宣言，中世紀教會主權論的代表文本。' },
          { title_zh: '傾向異端詔書', title_orig: 'Vergentis in senium', author: '教宗依諾增爵三世', era: '1199', place: '羅馬', language: '拉丁文', intro: '依諾增爵三世將異端比附羅馬法叛國罪、沒收其財產並累及子嗣的教令。異端罪重刑化的法律里程碑，後世裁判制度的嚴酷源頭。' },
          { title_zh: '古人記述詔書', title_orig: 'Antiquorum habet fida relatio', author: '教宗卜尼法八世', era: '1300', place: '羅馬', language: '拉丁文', intro: '卜尼法八世宣告首個聖年、頒赴羅馬朝聖者全大赦的詔書。天主教禧年制度的創始文件，中世紀朝聖與赦罪經濟的法律起點。' }
        
        ]
      },
      {
        key: 'national-law',
        label: '各國教會法部',
        label_en: 'National Church Laws',
        desc: '各王國規範教會事務的法典與憲章，政教關係的在地法制。',
        works: [
          { title_zh: '克拉倫登憲章', title_orig: 'Constitutions of Clarendon', author: '英王亨利二世', era: '1164', place: '克拉倫登', language: '拉丁文', intro: '亨利二世申明王權對教士審判與教會上訴管轄的十六條憲章，貝克特拒署而流亡。坎特伯裡血案的法律導火線，英格蘭政教管轄之爭的核心文本。' },
          { title_zh: '焚燒異端法', title_orig: 'De heretico comburendo', author: '英格蘭國會（亨利四世治下）', era: '1401', place: '倫敦', language: '拉丁文', intro: '英格蘭國會授權以火刑處死頑抗異端的法律，矛頭直指羅拉德派。英國史上首部焚燒異端的成文法，日後殉道世紀的法律工具。' },
          { title_zh: '聖史蒂芬教會法令', title_orig: 'Decreta Sancti Stephani regis', author: '匈牙利國王史蒂芬一世', era: '約 1000–1038', place: '艾斯特根', language: '拉丁文', intro: '匈牙利開國聖王史蒂芬的法令集，建堂什一與主日守禮入法。馬扎爾人基督教化的立法工程，中歐新王國「以法立教」的樣板。' },
          { title_zh: '冰島基督教法', title_orig: 'Kristinréttr (Grágás)', author: '冰島全體大會（灰雁法典教會編）', era: '約 1122–1133 成文', place: '冰島辛格韋德利', language: '古諾斯文', intro: '冰島自由邦灰雁法典中的基督教法編，洗禮葬儀與主教職權按本地議會傳統成文。無王之國的教會法奇例，北歐邊陲基督教化的法律化石。' },
          { title_zh: '古拉廷教會法', title_orig: 'Gulaþingslǫg (kristinn réttr)', author: '挪威古拉廷議會', era: '11–12 世紀成文', place: '挪威古拉廷', language: '古諾斯文', intro: '挪威西部古拉廷議會法典中的教會法章，聖俗條文同卷並存。維京社會接納基督教的立法切片，挪威法制史的最古地層之一。' }
        
        ]
      }
    ]
  },
  wai: {
      "summary": "與基督教教會法並立的他宗教法系與異端紀律。伊斯蘭以聖訓律、遜尼四大教法學派、法源學、公法與什葉派法典構成沙里亞；猶太以巴比倫塔木德、Geonic 律典、邁蒙尼德法典與卡拉派律法集其大成；卡特里、瓦勒度等異端與德魯茲衍生宗教亦有自身紀律，皆為中世紀法規版圖的並行體系。",
      "divisions": [
        {
          "key": "r-hadith-law",
          "label": "伊斯蘭聖訓律部",
          "label_en": "Islamic Hadith Law",
          "desc": "六大聖訓集中關乎買賣、婚姻、刑罰、司法、繼承的律法篇章，沙里亞的原始傳述法源。",
          "works": [
            {
              "title_zh": "《布哈里聖訓實錄‧買賣經》",
              "title_orig": "صحيح البخاري — كتاب البيوع (Kitāb al-Buyūʿ)",
              "author": "穆罕默德‧伊本‧伊斯瑪儀‧布哈里（Muḥammad ibn Ismāʿīl al-Bukhārī）",
              "era": "約西元 846 年（伊曆 232 年）成書",
              "place": "中亞布哈拉／呼羅珊一帶輯錄，後流傳於巴格達、奈薩布爾",
              "language": "阿拉伯文",
              "parent": "布哈里聖訓實錄（Ṣaḥīḥ al-Bukhārī）",
              "extent": "全書第 34 卷（kitāb），下分多門",
              "intro": "《布哈里聖訓實錄》六大聖訓集之首，被順尼派視為僅次於古蘭經的權威。〈買賣經〉收錄關於商業交易、買賣合法與禁戒、利息（riba）、抵押與賒購等先知言行，是伊斯蘭契約與商法的核心傳述來源，與中世紀教會教會法的買賣、放貸規範形成並立交鋒的他宗教法系。"
            },
            {
              "title_zh": "《布哈里聖訓實錄‧結婚經》",
              "title_orig": "صحيح البخاري — كتاب النكاح (Kitāb al-Nikāḥ)",
              "author": "穆罕默德‧伊本‧伊斯瑪儀‧布哈里（Muḥammad ibn Ismāʿīl al-Bukhārī）",
              "era": "約西元 846 年（伊曆 232 年）成書",
              "place": "中亞布哈拉／呼羅珊一帶輯錄",
              "language": "阿拉伯文",
              "parent": "布哈里聖訓實錄（Ṣaḥīḥ al-Bukhārī）",
              "extent": "全書第 67 卷（kitāb）",
              "intro": "〈結婚經〉收錄先知關於婚姻締結、聘禮、許可條件、婚配對象與夫妻倫常的言行，是伊斯蘭家庭法（婚姻法）的根本傳述依據。其婚姻效力與禁婚親等規範，與中世紀拉丁教會婚姻聖事法、拜占庭婚姻法構成跨宗教法系對照。"
            },
            {
              "title_zh": "《布哈里聖訓實錄‧律例經》",
              "title_orig": "صحيح البخاري — كتاب الأحكام (Kitāb al-Aḥkām)",
              "author": "穆罕默德‧伊本‧伊斯瑪儀‧布哈里（Muḥammad ibn Ismāʿīl al-Bukhārī）",
              "era": "約西元 846 年（伊曆 232 年）成書",
              "place": "中亞布哈拉／呼羅珊一帶輯錄",
              "language": "阿拉伯文",
              "parent": "布哈里聖訓實錄（Ṣaḥīḥ al-Bukhārī）",
              "extent": "全書第 93 卷（kitāb）",
              "intro": "〈律例經〉（Aḥkām，意為「裁斷／判例」）收錄先知與哈里發關於統治者職權、法官審判、效忠（bayʿa）與行政裁斷的言行，是伊斯蘭公法與司法制度的傳述基礎。其裁判倫理與政教權柄論，正對應中世紀政教權之爭的他宗教法系視角。"
            },
            {
              "title_zh": "《布哈里聖訓實錄‧法度刑罰經》",
              "title_orig": "صحيح البخاري — كتاب الحدود (Kitāb al-Ḥudūd)",
              "author": "穆罕默德‧伊本‧伊斯瑪儀‧布哈里（Muḥammad ibn Ismāʿīl al-Bukhārī）",
              "era": "約西元 846 年（伊曆 232 年）成書",
              "place": "中亞布哈拉／呼羅珊一帶輯錄",
              "language": "阿拉伯文",
              "parent": "布哈里聖訓實錄（Ṣaḥīḥ al-Bukhārī）",
              "extent": "全書第 86 卷（kitāb）",
              "intro": "〈法度刑罰經〉（Ḥudūd，意為「真主所定界限之刑」）收錄先知關於盜竊、通姦、誣告、飲酒等罪的法定刑罰傳述，是伊斯蘭刑法的核心。其「真主所定不可增減之刑」觀，與中世紀教會法的教會懲戒與世俗刑罰之分構成鮮明對照。"
            },
            {
              "title_zh": "《布哈里聖訓實錄‧繼承法經》",
              "title_orig": "صحيح البخاري — كتاب الفرائض (Kitāb al-Farāʾiḍ)",
              "author": "穆罕默德‧伊本‧伊斯瑪儀‧布哈里（Muḥammad ibn Ismāʿīl al-Bukhārī）",
              "era": "約西元 846 年（伊曆 232 年）成書",
              "place": "中亞布哈拉／呼羅珊一帶輯錄",
              "language": "阿拉伯文",
              "parent": "布哈里聖訓實錄（Ṣaḥīḥ al-Bukhārī）",
              "extent": "全書第 85 卷（kitāb）",
              "intro": "〈繼承法經〉（Farāʾiḍ，意為「法定份額」）收錄先知關於遺產分配、繼承人份額與親等順位的言行，奠定伊斯蘭繼承法精密的份額制度。此法以古蘭明文份額為骨幹，是伊斯蘭法中數理化最強的部門，與中世紀羅馬—教會繼承法傳統並立。"
            },
            {
              "title_zh": "《穆斯林聖訓實錄‧買賣交易經》",
              "title_orig": "صحيح مسلم — كتاب البيوع (Kitāb al-Buyūʿ)",
              "author": "穆斯林‧伊本‧哈賈吉‧奈薩布里（Muslim ibn al-Ḥajjāj al-Naysābūrī）",
              "era": "約西元 875 年（伊曆 261 年，輯者卒年）前成書",
              "place": "波斯奈薩布爾（Nīshāpūr）輯錄",
              "language": "阿拉伯文",
              "parent": "穆斯林聖訓實錄（Ṣaḥīḥ Muslim）",
              "extent": "全書第 21 卷（kitāb）",
              "intro": "《穆斯林聖訓實錄》六大集中地位僅次於布哈里，以傳述鏈嚴整、編排精細著稱。〈買賣交易經〉專輯先知關於買賣、利息禁令、預售（salam）、欺詐買賣禁戒的言行，與布哈里同類卷互補，是伊斯蘭商法與契約法的權威傳述。"
            },
            {
              "title_zh": "《穆斯林聖訓實錄‧離婚經》",
              "title_orig": "صحيح مسلم — كتاب الطلاق (Kitāb al-Ṭalāq)",
              "author": "穆斯林‧伊本‧哈賈吉‧奈薩布里（Muslim ibn al-Ḥajjāj al-Naysābūrī）",
              "era": "約西元 875 年（伊曆 261 年）前成書",
              "place": "波斯奈薩布爾（Nīshāpūr）輯錄",
              "language": "阿拉伯文",
              "parent": "穆斯林聖訓實錄（Ṣaḥīḥ Muslim）",
              "extent": "全書第 18 卷（kitāb）",
              "intro": "〈離婚經〉收錄先知關於休妻（ṭalāq）、待婚期（ʿidda）、撤回與不可撤回離婚等言行，是伊斯蘭婚姻解消法的核心傳述。其離婚程序與婦女權益規範，與中世紀拉丁教會堅持婚姻不可解的聖事觀形成最尖銳的跨宗教法系對立。"
            },
            {
              "title_zh": "《穆斯林聖訓實錄‧司法裁判經》",
              "title_orig": "صحيح مسلم — كتاب الأقضية (Kitāb al-Aqḍiya)",
              "author": "穆斯林‧伊本‧哈賈吉‧奈薩布里（Muslim ibn al-Ḥajjāj al-Naysābūrī）",
              "era": "約西元 875 年（伊曆 261 年）前成書",
              "place": "波斯奈薩布爾（Nīshāpūr）輯錄",
              "language": "阿拉伯文",
              "parent": "穆斯林聖訓實錄（Ṣaḥīḥ Muslim）",
              "extent": "全書第 30 卷（kitāb）",
              "intro": "〈司法裁判經〉（Aqḍiya，意為「判決」）收錄先知關於審判程序、舉證責任、誓證與法官裁斷原則的言行，是伊斯蘭訴訟法與司法倫理的根本依據。其「原告舉證、被告具誓」原則與中世紀教會法庭證據制度可相互對照。"
            },
            {
              "title_zh": "《提爾米吉聖訓集‧律例篇》",
              "title_orig": "جامع الترمذي — كتاب الأحكام (Kitāb al-Aḥkām)",
              "author": "穆罕默德‧伊本‧伊薩‧提爾米吉（Muḥammad ibn ʿĪsā al-Tirmidhī）",
              "era": "約西元 884 年（伊曆 270 年）前成書",
              "place": "中亞河中地區提爾米茲（Tirmidh）輯錄",
              "language": "阿拉伯文",
              "parent": "提爾米吉聖訓集（Jāmiʿ al-Tirmidhī）",
              "extent": "全書第 15 卷（kitāb）",
              "intro": "《提爾米吉聖訓集》為六大集之一，特色在每段聖訓後評斷其真偽等級並附法學派分歧。〈律例篇〉收錄關於審判、爭訟裁斷、法官資格與賄賂禁戒的傳述，並標註各教法學派立場，是研究伊斯蘭司法與比較法學的重要橋樑。"
            },
            {
              "title_zh": "《提爾米吉聖訓集‧血金篇》",
              "title_orig": "جامع الترمذي — كتاب الديات (Kitāb al-Diyāt)",
              "author": "穆罕默德‧伊本‧伊薩‧提爾米吉（Muḥammad ibn ʿĪsā al-Tirmidhī）",
              "era": "約西元 884 年（伊曆 270 年）前成書",
              "place": "中亞河中地區提爾米茲（Tirmidh）輯錄",
              "language": "阿拉伯文",
              "parent": "提爾米吉聖訓集（Jāmiʿ al-Tirmidhī）",
              "extent": "全書第 16 卷（kitāb）",
              "intro": "〈血金篇〉（Diyāt，意為「命價賠償」）收錄先知關於殺傷、過失致死之賠償金與同態報復（qiṣāṣ）的言行傳述，是伊斯蘭侵權與刑事賠償法的核心。其以血金替代血仇的制度，與中世紀日耳曼贖罪金（wergild）及教會調解傳統可作跨法系比較。"
            },
            {
              "title_zh": "《艾布達伍德聖訓集‧法官職守經》",
              "title_orig": "سنن أبي داود — كتاب الأقضية (Kitāb al-Aqḍiya)",
              "author": "艾布達伍德‧蘇萊曼‧西吉斯坦尼（Abū Dāwūd Sulaymān al-Sijistānī）",
              "era": "約西元 888 年（伊曆 275 年，輯者卒年）前成書",
              "place": "主要於塔爾蘇斯（Ṭarsūs，安納托利亞邊塞）輯錄，晚年於巴斯拉（Baṣra）講授／卒葬",
              "language": "阿拉伯文",
              "parent": "艾布達伍德聖訓集（Sunan Abī Dāwūd）",
              "extent": "全書第 25 卷（kitāb）",
              "intro": "《艾布達伍德聖訓集》以專收法律相關聖訓著稱，為法學家最倚重的聖訓集之一。〈法官職守經〉收錄關於法官任命、審理職責、判決公正與迴避的傳述，是伊斯蘭司法制度與法官倫理的根本文獻，與中世紀教會法庭與主教審判職權形成跨宗教法系對照。"
            },
            {
              "title_zh": "《艾布達伍德聖訓集‧貢賦戰利與治權經》",
              "title_orig": "سنن أبي داود — كتاب الخراج والإمارة والفىء (Kitāb al-Kharāj wa al-Imāra wa al-Fayʾ)",
              "author": "艾布達伍德‧蘇萊曼‧西吉斯坦尼（Abū Dāwūd Sulaymān al-Sijistānī）",
              "era": "約西元 888 年（伊曆 275 年）前成書",
              "place": "伊拉克巴斯拉（Baṣra）輯錄",
              "language": "阿拉伯文",
              "parent": "艾布達伍德聖訓集（Sunan Abī Dāwūd）",
              "extent": "全書第 20 卷（kitāb）",
              "intro": "〈貢賦戰利與治權經〉收錄關於土地稅（kharāj）、戰利品分配（fayʾ）與統治者職權（imāra）的先知與哈里發言行，是伊斯蘭財政法與公法的核心傳述。其對非穆斯林屬民賦稅（jizya/kharāj）的規範，正對應中世紀伊斯蘭區與基督教世界的交鋒場域。"
            },
            {
              "title_zh": "《奈薩儀聖訓集‧斷血復仇與血金經》",
              "title_orig": "سنن النسائي — كتاب القسامة (Kitāb al-Qasāma)",
              "author": "艾哈邁德‧伊本‧舒艾卜‧奈薩儀（Aḥmad ibn Shuʿayb al-Nasāʾī）",
              "era": "約西元 915 年（伊曆 303 年，輯者卒年）前成書",
              "place": "呼羅珊奈薩（Nasā）出身，於埃及、敘利亞一帶輯錄",
              "language": "阿拉伯文",
              "parent": "奈薩儀聖訓集（Sunan al-Nasāʾī）",
              "extent": "全書第 45 卷（kitāb）",
              "intro": "《奈薩儀聖訓集》六大集中以傳述審查最嚴格著稱。〈斷血復仇與血金經〉（Qasāma，指命案中以五十人具誓裁定責任的特殊程序）收錄關於命案具誓、同態報復與血金的傳述，是伊斯蘭刑事程序法中最具特色的部門，與中世紀日耳曼共誓制度（compurgation）堪作對照。"
            },
            {
              "title_zh": "《奈薩儀聖訓集‧法官禮儀經》",
              "title_orig": "سنن النسائي — كتاب آداب القضاة (Kitāb Ādāb al-Quḍāt)",
              "author": "艾哈邁德‧伊本‧舒艾卜‧奈薩儀（Aḥmad ibn Shuʿayb al-Nasāʾī）",
              "era": "約西元 915 年（伊曆 303 年）前成書",
              "place": "呼羅珊奈薩（Nasā）出身，於埃及、敘利亞一帶輯錄",
              "language": "阿拉伯文",
              "parent": "奈薩儀聖訓集（Sunan al-Nasāʾī）",
              "extent": "全書第 49 卷（kitāb）",
              "intro": "〈法官禮儀經〉（Ādāb al-Quḍāt，意為「法官的規範與品德」）收錄關於法官操守、審判時的中立態度、不在憤怒下判決、不受賄等先知言行，是伊斯蘭司法倫理的專門文獻，與中世紀教會法對教會法官（judex ecclesiasticus）品德要求互可參照。"
            },
            {
              "title_zh": "《伊本馬哲聖訓集‧律例篇》",
              "title_orig": "سنن ابن ماجه — كتاب الأحكام (Kitāb al-Aḥkām)",
              "author": "穆罕默德‧伊本‧馬哲‧蓋茲維尼（Muḥammad ibn Mājah al-Qazwīnī）",
              "era": "約西元 887 年（伊曆 273 年，輯者卒年）前成書",
              "place": "波斯蓋茲溫（Qazwīn）輯錄",
              "language": "阿拉伯文",
              "parent": "伊本馬哲聖訓集（Sunan Ibn Mājah）",
              "extent": "全書第 13 卷（kitāb），第 2308–2374 段",
              "intro": "《伊本馬哲聖訓集》為六大集中最後納入者，補收前五集所缺傳述。〈律例篇〉收錄關於裁判、爭訟、賄賂禁戒與權責歸屬的先知言行，是研究伊斯蘭司法的補充來源，其與其他五集的異同正可顯示聖訓律法傳述的層累與互校。"
            },
            {
              "title_zh": "布哈里聖訓實錄",
              "title_orig": "Ṣaḥīḥ al-Bukhārī",
              "author": "布哈里(al-Bukhārī)",
              "era": "約 846 成書",
              "place": "中亞布哈拉‧編於各地",
              "language": "阿拉伯文",
              "intro": "《布哈里聖訓實錄》是順尼派六大聖訓集之首，由布哈里歷時十餘年自數十萬則傳述中嚴格甄選約七千餘則先知言行彙編而成，依教法主題分卷。它被順尼派奉為僅次於古蘭經的權威經典，是伊斯蘭教法（沙里亞）的根本法源之一。其嚴謹的傳述鏈考訂方法樹立了聖訓學標準，深刻塑造伊斯蘭法學與信仰實踐，在中世紀伊斯蘭世界具至高地位。"
            },
            {
              "title_zh": "穆斯林聖訓實錄",
              "title_orig": "Ṣaḥīḥ Muslim",
              "author": "穆斯林·本·哈查吉(Muslim ibn al-Ḥajjāj)",
              "era": "約 875 成書",
              "place": "內沙布爾(Nishapur)",
              "language": "阿拉伯文",
              "intro": "《穆斯林聖訓實錄》是順尼派六大聖訓集中與《布哈里聖訓實錄》並列最權威的兩部之一，由穆斯林·本·哈查吉精選約四千則先知傳述編成，以傳述鏈完整、編排嚴整著稱。它與布哈里集合稱「兩真本」，是伊斯蘭教法與信仰的核心依據。其體例側重將同一主題的不同傳述匯聚對照，在聖訓學方法上自成一格，為中世紀法學家廣泛徵引。"
            }
          ]
        },
        {
          "key": "sunni-fiqh",
          "label": "伊斯蘭教法部‧遜尼四大學派",
          "label_en": "Sunni Fiqh (Four Schools)",
          "desc": "哈乃斐、馬立克、沙斐儀、罕百里四大遜尼教法學派的奠基法典。",
          "works": [
            {
              "title_zh": "指南（希達亞）",
              "title_orig": "al-Hidāya fī sharḥ Bidāyat al-mubtadī",
              "author": "馬爾吉納尼(Burhān al-Dīn al-Marghīnānī，卒 593 AH/1197)",
              "era": "約 1170–1197",
              "place": "河中地區‧馬爾吉納(Transoxania / Marghinan)",
              "language": "阿拉伯文",
              "intro": "《指南》是哈乃斐派最負盛名的法典，中亞法學家馬爾吉納尼為初學者所編律例綱要的自注本，體例嚴整、說理清暢，數百年間為哈乃斐學派的標準教本。它隨鄂圖曼與蒙兀兒帝國通行於巴爾幹至印度，十八世紀更由英國殖民當局譯為英文(The Hedaya)作為印度穆斯林民法的準據，是流傳最廣的伊斯蘭法典之一。"
            },
            {
              "title_zh": "古杜里要略",
              "title_orig": "Mukhtaṣar al-Qudūrī",
              "author": "艾哈邁德‧本‧穆罕默德‧庫杜里（Aḥmad ibn Muḥammad al-Qudūrī）",
              "era": "11世紀初",
              "place": "巴格達",
              "language": "阿拉伯文",
              "intro": "哈乃斐派最精簡的入門法典，僅列學派通行定見而略去論證，體例緊湊、便於誦記，被稱作「al-Kitāb（那部書）」。千年來為初學費格赫者必修的第一部教材，後世大量註疏（如《明珠註》《精華註》）皆以之為骨幹，影響遍及中亞、印度、鄂圖曼與中國經堂教育。"
            },
            {
              "title_zh": "詳解大典（馬布蘇特）",
              "title_orig": "Kitāb al-Mabsūṭ / المبسوط",
              "author": "沙姆斯丁‧薩拉赫西（Shams al-Aʾimma Muḥammad ibn Aḥmad al-Sarakhsī）",
              "era": "約 11 世紀末（作者卒約 1090）",
              "place": "中亞河中烏茲堅（獄中口授）",
              "language": "阿拉伯文",
              "extent": "全書三十卷",
              "intro": "三十卷的哈乃斐派教法巨帙，據傳薩拉赫西被囚井中憑記憶口授門徒筆錄而成。體例宏富、論證細密，逐門疏理伊斯蘭全部律例，是哈乃斐學派集大成的百科式法典，中世紀伊斯蘭法學思辨深度的極致標本，與拉丁西方經院法學遙相呼應。"
            },
            {
              "title_zh": "大彙編（穆達瓦納）",
              "title_orig": "al-Mudawwana al-Kubrā",
              "author": "薩赫農(Saḥnūn ibn Saʿīd，卒 240 AH/854)口述輯錄，依馬立克學說",
              "era": "約 800–854",
              "place": "凱魯萬(Qayrawān)",
              "language": "阿拉伯文",
              "intro": "《大彙編》是馬立克派最權威的法典彙編，由北非凱魯萬法官薩赫農將伊本‧卡西姆轉述的馬立克教法整理成問答體巨帙，逐案記錄疑難與裁斷。它把馬立克的口傳學說系統化，成為西方伊斯蘭世界(馬格里布、安達魯斯)千年遵行的實務法典，是中世紀基督徒在收復失地運動中所面對的穆斯林法制的核心依據。"
            },
            {
              "title_zh": "坦途（穆瓦塔）",
              "title_orig": "al-Muwaṭṭaʾ",
              "author": "馬立克‧伊本‧阿納斯(Mālik ibn Anas，卒 179 AH/795)",
              "era": "約 760–795",
              "place": "麥地那(Medina)",
              "language": "阿拉伯文",
              "intro": "《坦途》是現存最早的伊斯蘭法律著作之一，馬立克‧伊本‧阿納斯依麥地那城的傳承慣行編成，兼收先知聖訓、聖伴裁斷與麥地那共識，逐門立律。它既是聖訓集也是法典，奠定遜尼四大教法學派之馬立克派的根本，流通於北非與安達魯斯。中世紀基督教西班牙與西西里治下的穆斯林即以此律自治，是拉丁世界最先接觸的伊斯蘭法源。"
            },
            {
              "title_zh": "教法論綱（凱魯萬里薩拉）",
              "title_orig": "al-Risāla fī al-fiqh al-Mālikī",
              "author": "伊本‧阿比‧宰德‧凱魯萬尼(Ibn Abī Zayd al-Qayrawānī，卒 386 AH/996)",
              "era": "約 970–996",
              "place": "凱魯萬(Qayrawān)",
              "language": "阿拉伯文",
              "intro": "《教法論綱》是馬立克派最流行的入門法典，凱魯萬法學家伊本‧阿比‧宰德以簡練文體概述信仰要義與各門律例，被譽為「馬立克派的小母法」，數百年來為馬格里布與西非清真學塾的必讀啟蒙教本。它把繁複的馬立克法制濃縮成可誦習的綱要，是中世紀北非伊斯蘭法教育普及的關鍵文本。"
            },
            {
              "title_zh": "哈利勒簡明教法",
              "title_orig": "Mukhtaṣar Khalīl",
              "author": "哈利勒‧本‧易斯哈格‧金迪（Khalīl ibn Isḥāq al-Jundī）",
              "era": "14世紀",
              "place": "開羅",
              "language": "阿拉伯文",
              "intro": "馬立克學派後期最權威的定本節略，以極度濃縮的術語體系裁定學派通行判斷，被視為馬立克派實質法的「終極簡本」。自成書以來即為北非、西非馬立克法官與穆夫提裁決的第一依據，衍生註疏汗牛充棟，法屬殖民地伊斯蘭民法亦多以其法譯為據。"
            },
            {
              "title_zh": "母法（烏姆）",
              "title_orig": "Kitāb al-Umm",
              "author": "沙斐儀(Muḥammad ibn Idrīs al-Shāfiʿī，卒 204 AH/820)",
              "era": "約 810–820",
              "place": "埃及‧福斯塔特(Fusṭāṭ, Egypt)",
              "language": "阿拉伯文",
              "intro": "《母法》是沙斐儀派的奠基法典，由該派創始人沙斐儀晚年在埃及口授弟子而成，逐門論列具體律例並詳述其法源推理，兼具實體法與方法論。沙斐儀首倡以古蘭、聖訓、公議、類比四源立法，此書即其教法體系的完整展開，為遜尼四大學派之沙斐儀派根本，中世紀盛行於埃及、敘利亞與東方，影響橫貫地中海東岸。"
            },
            {
              "title_zh": "求道者津梁",
              "title_orig": "Minhāj al-Ṭālibīn wa ʿUmdat al-Muftīn / منهاج الطالبين",
              "author": "葉哈雅‧奈瓦維（Yaḥyā al-Nawawī）",
              "era": "約 1260 年代（作者卒於 1277）",
              "place": "大馬士革",
              "language": "阿拉伯文",
              "extent": "一卷",
              "intro": "奈瓦維在拉菲儀《穆哈拉爾》基礎上校訂而成的沙斐儀派標準法典，以精確條文標定學派定論，是後世沙斐儀法官與教法諮詢者最倚重的權威簡編。其衍生《穆哈塔智津梁》《瓦哈吉之燈》等重要注疏，自中世紀迄今為東南亞、也門、埃及沙斐儀教學的核心文本。"
            },
            {
              "title_zh": "豐足（穆格尼）",
              "title_orig": "al-Mughnī",
              "author": "伊本‧古達馬(Muwaffaq al-Dīn Ibn Qudāma，卒 620 AH/1223)",
              "era": "約 1190–1220",
              "place": "大馬士革(Damascus)",
              "language": "阿拉伯文",
              "intro": "《豐足》是罕百里派最宏富的法典，敘利亞法學家伊本‧古達馬以比較法方式逐案陳列各派主張再申罕百里立場，卷帙逾萬頁，兼容並蓄而論證縝密，被公認為伊斯蘭比較法學的巔峰之一。它奠定遜尼四大學派中罕百里派的權威體系，是中世紀十字軍治下敘利亞穆斯林法制的重要典籍。"
            }
          ]
        },
        {
          "key": "usul-fiqh",
          "label": "伊斯蘭法源學部",
          "label_en": "Islamic Legal Theory (Uṣūl al-Fiqh)",
          "desc": "推衍教法的法源與方法論——經、訓、公議、類比之學。",
          "works": [
            {
              "title_zh": "法源論（沙斐儀里薩拉）",
              "title_orig": "al-Risāla (fī uṣūl al-fiqh) / الرسالة",
              "author": "穆罕默德‧伊本‧伊德里斯‧沙斐儀（Muḥammad ibn Idrīs al-Shāfiʿī）",
              "era": "約 9 世紀初（作者卒 820）",
              "place": "埃及福斯塔特",
              "language": "阿拉伯文",
              "intro": "伊斯蘭法學原理（usul al-fiqh）的開山之作，沙斐儀首次系統論定古蘭、聖訓、公議、類比四大法源的位階與運用規則，確立聖訓對古蘭的詮釋權威。它為伊斯蘭教法從零散判例升為嚴整法學體系奠定方法論根基，是理解整個沙里亞推理架構的鑰匙文本。"
            },
            {
              "title_zh": "明證（法源學明證論）",
              "title_orig": "al-Burhān fī uṣūl al-fiqh",
              "author": "朱瓦伊尼（Imām al-Ḥaramayn al-Juwaynī）",
              "era": "11世紀",
              "place": "尼沙普爾",
              "language": "阿拉伯文",
              "intro": "沙斐儀—艾什爾里傳統法學原理的成熟鉅構，作者「兩聖地伊瑪目」以縝密思辨重建法源理論，於類比、公議、目的論證多有創發，並為弟子安薩里之學鋪路。是古典 uṣūl al-fiqh 由早期向鼎盛過渡的關鍵著作，論理之嚴為後世推重。"
            },
            {
              "title_zh": "法學精義（澄澈之源）",
              "title_orig": "al-Mustaṣfā min ʿilm al-uṣūl / المستصفى من علم الأصول",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "11世紀末至12世紀初（安薩里卒於1111）",
              "place": "巴格達／波斯呼羅珊",
              "language": "阿拉伯文",
              "intro": "伊斯蘭法學原理（uṣūl al-fiqh）的巔峰之作，安薩里以其邏輯訓練重整法源學，先立論理與知識論導言，再論經、訓、公議、類比四源及公益（maṣlaḥa）等推理法。此書架構嚴謹、論證縝密，被視為沙斐儀派法源學的定本，深遠影響後世一切法理著述。"
            },
            {
              "title_zh": "法理精斷",
              "title_orig": "al-Iḥkām fī uṣūl al-aḥkām / الإحكام في أصول الأحكام",
              "author": "賽福丁‧阿米迪（Sayf al-Dīn al-Āmidī）",
              "era": "約 13 世紀初（作者卒於 1233）",
              "place": "開羅／大馬士革",
              "language": "阿拉伯文",
              "extent": "多卷",
              "intro": "阿米迪以神學家兼邏輯學家的思辨力寫就的法源學鉅著，綜攝前代各派學說並以嚴密論證權衡是非，體例精嚴、辨析入微，與安薩里《法學精義》並列法源學經典。後由伊本‧哈吉卜濃縮為《綱要》廣為流傳，是中世紀伊斯蘭法理思辨的高峰。"
            }
          ]
        },
        {
          "key": "siyasa-law",
          "label": "伊斯蘭公法部",
          "label_en": "Islamic Public Law",
          "desc": "治權、賦稅、齊米稅法與聖戰／國際法，伊斯蘭政權治理與宗教交鋒區的法律框架。",
          "works": [
            {
              "title_zh": "賦稅書",
              "title_orig": "Kitāb al-Kharāj",
              "author": "艾布‧優素福（Abū Yūsuf Yaʻqūb）",
              "era": "約780年代（8世紀）",
              "place": "巴格達",
              "language": "阿拉伯文",
              "intro": "應阿拔斯哈里發哈倫‧拉施德之請而撰的財政與行政法專論，系統規定土地稅（kharāj）、人丁稅（jizya）、戰利品分配、齊米（受保護非穆斯林）待遇與官吏職守。是伊斯蘭公法與稅法最早的權威文獻，兼具法學與治國諫言性質，為理解早期哈里發國家治理的第一手綱領。"
            },
            {
              "title_zh": "治權律例",
              "title_orig": "al-Aḥkām al-Sulṭāniyya",
              "author": "馬瓦爾迪（al-Māwardī）",
              "era": "11世紀",
              "place": "巴格達",
              "language": "阿拉伯文",
              "intro": "伊斯蘭憲政與公法的經典專論，系統論述哈里發（伊瑪目）之選立與職權、大臣、省督、司法官、軍政、稅收、齊米民與市政監察等制度。撰於阿拔斯哈里發權威衰微之際，旨在重申教法對政權的規範，是後世伊斯蘭政治法理與國家理論反覆援引的奠基文本。"
            },
            {
              "title_zh": "大聖戰律（希亞爾）",
              "title_orig": "Kitāb al-Siyar / كتاب السير",
              "author": "穆罕默德‧伊本‧哈桑‧謝巴尼（Muḥammad ibn al-Ḥasan al-Shaybānī）",
              "era": "約 790 年代（作者卒於 805）",
              "place": "庫法／巴格達",
              "language": "阿拉伯文",
              "extent": "一卷",
              "intro": "哈乃斐派謝巴尼所撰的「征略」（siyar）法典，界定伊斯蘭政權與非穆斯林勢力間的戰爭、締約、停戰、外交使節、戰俘與戰利品分配之法，被譽為伊斯蘭「萬國法」（國際法）的奠基之作。其對戰時倫理與異教徒待遇的規範，是中世紀伊斯蘭與基督教世界交鋒的法理依據。"
            }
          ]
        },
        {
          "key": "shia-law",
          "label": "什葉派教法部",
          "label_en": "Shia Jurisprudence",
          "desc": "十二伊瑪目派四大法典及伊斯瑪儀派、栽德派的教法典籍。",
          "works": [
            {
              "title_zh": "卡菲‧教法卷（分支篇）",
              "title_orig": "Furūʿ al-Kāfī (al-Kāfī)",
              "author": "庫萊尼(Muḥammad ibn Yaʿqūb al-Kulaynī，卒 329 AH/941)",
              "era": "約 900–940 編纂",
              "place": "賴伊‧巴格達(Rayy / Baghdad)",
              "language": "阿拉伯文",
              "parent": "卡菲（al-Kāfī）",
              "extent": "《卡菲》三部之一(法規部)",
              "intro": "《卡菲》是什葉十二伊瑪目派「四大法典」之首，由庫萊尼歷二十年輯成，分教義卷、教法卷與雜錄。此處收其教法卷(Furūʿ)，逐門編排潔淨、禮拜、齋戒、婚姻、買賣、刑罰等實務律例，全依歷代伊瑪目傳述立法。它與遜尼派聖訓集並立，是中世紀伊斯蘭世界另一支法統的根本，基督徒學者與什葉法學交鋒時所面對的權威文本。"
            },
            {
              "title_zh": "法基赫不臨者",
              "title_orig": "Man lā yaḥḍuruhu al-Faqīh",
              "author": "伊本‧巴巴瓦伊赫(謝赫‧薩杜格，Ibn Bābawayh al-Ṣadūq，卒 381 AH/991)",
              "era": "約 970–990",
              "place": "賴伊‧庫姆(Rayy / Qom)",
              "language": "阿拉伯文",
              "extent": "四大法典之一",
              "intro": "《法基赫不臨者》(意為「身邊無法學家可問者之書」)是什葉十二伊瑪目派四大法典之二，薩杜格為使無師可請的信徒能自行查律而編。全書按律法門類收錄可據以行事的可靠傳述，是一部面向平信徒的實用法典。與庫萊尼《卡菲》互補，構成中世紀什葉派教法的骨幹，是伊斯瑪儀‧十二伊瑪目分野後遜尼以外最重要的律典之一。"
            },
            {
              "title_zh": "教法修訂（塔赫濟卜）",
              "title_orig": "Tahdhīb al-Aḥkām",
              "author": "圖西(謝赫‧圖西，Muḥammad ibn al-Ḥasan al-Ṭūsī，卒 460 AH/1067)",
              "era": "約 1030–1050",
              "place": "巴格達‧納傑夫(Baghdad / Najaf)",
              "language": "阿拉伯文",
              "extent": "四大法典之一",
              "intro": "《教法修訂》是「教派宗師」圖西所著什葉四大法典之三，體例上為對其師穆菲德《教誨篇》的律法注疏，逐條匯集傳述、調和矛盾、判定取捨，涵蓋全部教法門類，卷帙浩繁。它奠定了什葉派法源學與傳述批判的方法，與其姊妹作《明察》同為中世紀什葉法學的支柱，直到近代仍是教法院引據的根本典籍。"
            },
            {
              "title_zh": "明察（傳述歧異審辨）",
              "title_orig": "al-Istibṣār fīmā ikhtalafa min al-akhbār",
              "author": "圖西(謝赫‧圖西，al-Ṭūsī，卒 460 AH/1067)",
              "era": "約 1040–1050",
              "place": "巴格達‧納傑夫(Baghdad / Najaf)",
              "language": "阿拉伯文",
              "extent": "四大法典之一",
              "intro": "《明察》是圖西編纂的什葉四大法典之四，專門處理律法傳述之間的歧異，逐一列出彼此矛盾的傳述並給出裁斷準則，可視為《教法修訂》的精要與方法論姊妹篇。它示範了如何在相衝突的伊瑪目傳述間辨明立法依據，是十二伊瑪目派教法定讞的關鍵工具書，構成中世紀什葉律學四柱之末柱。"
            },
            {
              "title_zh": "伊斯蘭支柱（法蒂瑪官定法典）",
              "title_orig": "Daʿāʾim al-Islām / دعائم الإسلام",
              "author": "卡迪‧努爾曼（al-Qāḍī al-Nuʿmān ibn Muḥammad）",
              "era": "10世紀（努爾曼卒於974）",
              "place": "北非（法蒂瑪王朝，凱魯萬／馬赫迪耶）",
              "language": "阿拉伯文",
              "intro": "伊斯瑪儀派（法蒂瑪王朝）的官定法典，卡迪‧努爾曼奉哈里發之命編纂，上部論信仰與敬拜「七支柱」，下部詳陳民商刑諸律，全依伊瑪目家族傳述立說。此書是伊斯瑪儀派實體法的權威根本，至今仍為波赫拉等社群所奉行。"
            },
            {
              "title_zh": "洶湧之海（栽德派法典）",
              "title_orig": "Kitāb al-Baḥr al-Zakhkhār al-jāmiʿ li-madhāhib ʿulamāʾ al-amṣār",
              "author": "伊本‧穆爾塔達(Aḥmad ibn Yaḥyā Ibn al-Murtaḍā，卒 840 AH/1437)",
              "era": "約 1400–1437",
              "place": "葉門‧薩那(Yemen / Ṣanʿāʾ)",
              "language": "阿拉伯文",
              "intro": "《洶湧之海》是栽德派(第五伊瑪目派)最重要的比較法典，由葉門栽德伊瑪目伊本‧穆爾塔達所撰，博採各城學者諸說而以栽德教法為歸，體系完備、影響深遠，其精華《花冠》(al-Azhār)後世注疏不絕。栽德派介於遜尼與十二伊瑪目派之間，此書代表中世紀什葉第三支流的法學高峰，是葉門千年教法的基石。"
            }
          ]
        },
        {
          "key": "talmud",
          "label": "巴比倫塔木德部",
          "label_en": "Babylonian Talmud",
          "desc": "巴比倫塔木德關乎律法實質的論篇（masekhtot），猶太口傳律法的根本。",
          "works": [
            {
              "title_zh": "巴比倫塔木德‧祝禱篇",
              "title_orig": "Talmud Bavli — Masekhet Berakhot / ברכות",
              "author": "巴比倫諸拉比學院（阿摩拉學者）",
              "era": "約 500–600 編定",
              "place": "巴比倫（蘇拉‧蓬貝迪塔學院）",
              "language": "希伯來文‧巴比倫亞蘭文",
              "parent": "巴比倫塔木德",
              "extent": "單篇（masekhet）",
              "intro": "塔木德「種子部」唯一入《革馬拉》辯論的一篇，論每日誦禱示瑪、十八禱文、飯前後謝恩與各式祝福的時序與規範。它奠定猶太日常禮儀與祈禱法（halakha）的根本框架，居巴比倫塔木德全書之首，是研究猶太禮拜生活的核心律典。"
            },
            {
              "title_zh": "巴比倫塔木德‧安息日篇",
              "title_orig": "Talmud Bavli — Masekhet Shabbat / שבת",
              "author": "巴比倫諸拉比學院（阿摩拉學者）",
              "era": "約 500–600 編定",
              "place": "巴比倫（蘇拉‧蓬貝迪塔學院）",
              "language": "希伯來文‧巴比倫亞蘭文",
              "parent": "巴比倫塔木德",
              "extent": "單篇（masekhet）",
              "intro": "塔木德「節期部」篇幅最巨的一篇，詳論安息日三十九類禁作之工、界域限制、燈火與飲食之預備等，是猶太安息日律法（hilkhot Shabbat）的根本淵藪。其對「工作」的精密界定深刻塑造正統猶太生活，並在中世紀與基督徒的守日之爭中屢成論辯焦點。"
            },
            {
              "title_zh": "巴比倫塔木德‧逾越節篇",
              "title_orig": "Pesaḥim (פסחים)",
              "author": "巴比倫塔木德（阿摩拉眾拉比編纂）",
              "era": "約200–600（成典約500）",
              "place": "巴比倫（蘇拉、彭貝迪塔學院）",
              "language": "巴比倫亞蘭文／希伯來文",
              "parent": "巴比倫塔木德",
              "extent": "巴比倫塔木德三十七篇之一（《節期部》）",
              "intro": "塔木德《節期部》論逾越節之篇，規範除酵、逾越羔羊獻祭與逾越夜「四杯酒」筵席（seder）程序。它為家庭逾越禮儀提供律法架構，兼論節前除麵酵的潔淨規條，是猶太節期律法的樞紐。"
            },
            {
              "title_zh": "巴比倫塔木德‧婚書篇",
              "title_orig": "Talmud Bavli — Masekhet Ketubot / כתובות",
              "author": "巴比倫諸拉比學院（阿摩拉學者）",
              "era": "約 500–600 編定",
              "place": "巴比倫（蘇拉‧蓬貝迪塔學院）",
              "language": "希伯來文‧巴比倫亞蘭文",
              "parent": "巴比倫塔木德",
              "extent": "單篇（masekhet）",
              "intro": "塔木德「婦女部」核心篇章，論婚約婚書（ketubah）所定聘金、夫妻互負之權利義務、嫁妝、寡婦贍養與離婚財產分配，是猶太婚姻與家庭財產法的根本。其對婦女經濟保障的規範，與中世紀拉丁教會婚姻聖事法構成鮮明的跨宗教法系對照。"
            },
            {
              "title_zh": "巴比倫塔木德‧離婚書篇",
              "title_orig": "Giṭṭin (גיטין)",
              "author": "巴比倫塔木德（阿摩拉眾拉比編纂）",
              "era": "約200–600（成典約500）",
              "place": "巴比倫（蘇拉、彭貝迪塔學院）",
              "language": "巴比倫亞蘭文／希伯來文",
              "parent": "巴比倫塔木德",
              "extent": "巴比倫塔木德三十七篇之一（《婦女部》）",
              "intro": "塔木德《婦女部》論休書（get）之篇，規範離婚文書的書寫、見證、遞交程序與生效條件。猶太離婚須由丈夫親付合法休書，本篇的形式要件至今仍規範正統派離婚，兼論「為世界安寧」的社會立法原則。"
            },
            {
              "title_zh": "巴比倫塔木德‧成聘篇",
              "title_orig": "Qiddushin (קידושין)",
              "author": "巴比倫塔木德（阿摩拉眾拉比編纂）",
              "era": "約200–600（成典約500）",
              "place": "巴比倫（蘇拉、彭貝迪塔學院）",
              "language": "巴比倫亞蘭文／希伯來文",
              "parent": "巴比倫塔木德",
              "extent": "巴比倫塔木德三十七篇之一（《婦女部》）",
              "intro": "塔木德《婦女部》論訂婚（成聘）之篇，界定締結婚約的三途——財、契、同房——及其法律效力，並廣論猶太身分世系與各類法律行為的能力。它是猶太婚姻締結與人身分法的基礎文本。"
            },
            {
              "title_zh": "巴比倫塔木德‧損害首門篇",
              "title_orig": "Talmud Bavli — Masekhet Bava Kamma / בבא קמא",
              "author": "巴比倫諸拉比學院（阿摩拉學者）",
              "era": "約 500–600 編定",
              "place": "巴比倫（蘇拉‧蓬貝迪塔學院）",
              "language": "希伯來文‧巴比倫亞蘭文",
              "parent": "巴比倫塔木德",
              "extent": "單篇（masekhet）",
              "intro": "「損害三門」之首，論牲畜致害、坑陷、火災、盜竊與傷害之侵權賠償責任，界定損害的類別與賠償計算，是猶太侵權法（tort）的根本篇章。其精密的責任歸屬體系可與伊斯蘭血金法及中世紀日耳曼贖罪金傳統作跨法系比較。"
            },
            {
              "title_zh": "巴比倫塔木德‧損害中門篇",
              "title_orig": "Talmud Bavli — Massekhet Bava Metzia / מסכת בבא מציעא",
              "author": "巴比倫諸拉比學院（阿摩拉學者）",
              "era": "約 500–600 編定",
              "place": "巴比倫（蘇拉‧蓬貝迪塔學院）",
              "language": "希伯來文‧巴比倫亞蘭文",
              "parent": "巴比倫塔木德",
              "extent": "塔木德三十七篇之一",
              "intro": "損害三篇（Bava Kamma/Metzia/Batra）之中門，專論民事財產法：拾遺、寄託、借貸、雇傭、租賃與利息禁令。它是猶太民商法的核心文本，規範中世紀猶太社群的日常交易與債務關係，其利息與契約規範恰與同期教會法的高利貸禁令、伊斯蘭商法並立交鋒。"
            },
            {
              "title_zh": "巴比倫塔木德‧損害末門篇",
              "title_orig": "Talmud Bavli — Masekhet Bava Batra / בבא בתרא",
              "author": "巴比倫諸拉比學院（阿摩拉學者）",
              "era": "約 500–600 編定",
              "place": "巴比倫（蘇拉‧蓬貝迪塔學院）",
              "language": "希伯來文‧巴比倫亞蘭文",
              "parent": "巴比倫塔木德",
              "extent": "單篇（masekhet）",
              "intro": "「損害三門」之末門，論不動產所有權、相鄰關係、地界、買賣、繼承與文書憑證之效力，是猶太物權法、繼承法與證據法的根本篇章。其對契據與見證的規範奠定猶太商業社群的法律秩序，是中世紀猶太民法實務的支柱。"
            },
            {
              "title_zh": "巴比倫塔木德‧公會篇",
              "title_orig": "Talmud Bavli — Masekhet Sanhedrin / סנהדרין",
              "author": "巴比倫諸拉比學院（阿摩拉學者）",
              "era": "約 500–600 編定",
              "place": "巴比倫（蘇拉‧蓬貝迪塔學院）",
              "language": "希伯來文‧巴比倫亞蘭文",
              "parent": "巴比倫塔木德",
              "extent": "單篇（masekhet）",
              "intro": "論猶太公會（Sanhedrin）的組成、審判程序、死刑四種執行方式與刑事訴訟法，並含關於復活、彌賽亞與「來世有份者」的著名神學章。它是猶太刑法與司法制度的根本篇章，其審判與死刑規範既屬律法核心，亦在中世紀基督徒論辯中被反覆援引。"
            },
            {
              "title_zh": "巴比倫塔木德‧經漏篇",
              "title_orig": "Niddah (נדה)",
              "author": "巴比倫塔木德（阿摩拉眾拉比編纂）",
              "era": "約200–600（成典約500）",
              "place": "巴比倫（蘇拉、彭貝迪塔學院）",
              "language": "巴比倫亞蘭文／希伯來文",
              "parent": "巴比倫塔木德",
              "extent": "巴比倫塔木德三十七篇之一（《潔淨部》唯一具革馬拉者）",
              "intro": "塔木德《潔淨部》唯一具革馬拉之篇，論婦女經期與產後的儀式潔淨、家庭潔淨律（niddah）及沐禮（mikveh）規範。它是猶太家庭潔淨法的律法核心，規範夫妻分合的時序，至今仍為正統派家庭生活所遵行。"
            },
            {
              "title_zh": "巴比倫塔木德‧偶像崇拜篇",
              "title_orig": "Talmud Bavli, Masekhet ʻAvodah Zarah",
              "author": "巴比倫諸拉比（阿摩拉學者）編定",
              "era": "約500–600年（塔木德編定期）",
              "place": "巴比倫（蘇拉與蓬貝迪塔學院）",
              "language": "巴比倫阿拉米文與希伯來文",
              "parent": "巴比倫塔木德",
              "intro": "塔木德「損害門」中的一篇，專論猶太人與偶像崇拜者（外邦人）交往的律法界限：禁與其節慶貿易、禁涉偶像祭物與酒、界定通商與雜居的分際。是理解猶太律法如何在多神與異教環境中劃定社群邊界的核心文本，中世紀在基督教審查下屢遭刪削。"
            },
            {
              "title_zh": "巴比倫塔木德‧界域篇",
              "title_orig": "Talmud Bavli — Masekhet Eruvin / עירובין",
              "author": "巴比倫諸拉比學院（阿摩拉世代眾拉比）",
              "era": "約 3–6 世紀纂輯（革馬拉），承米書拿（約 200）",
              "place": "巴比倫蘇拉與彭貝迪塔諸拉比學院",
              "language": "巴比倫亞蘭文與希伯來文",
              "parent": "巴比倫塔木德",
              "intro": "《界域篇》屬節期部，承接《安息日篇》，專論安息日與節期的「界域」（eruv）法度：如何以象徵性的合成界域擴展安息日可行走與搬運的範圍，涵蓋私域公域之界、庭院共域、城郊二千肘界限等。它是拉比法對安息日禁令作精細空間規範的核心論篇，中世紀猶太社群的安息日實踐皆據此而行。"
            },
            {
              "title_zh": "巴比倫塔木德‧贖罪日篇",
              "title_orig": "Talmud Bavli — Masekhet Yoma / יומא",
              "author": "巴比倫諸拉比學院（阿摩拉世代眾拉比）",
              "era": "約 3–6 世紀纂輯（革馬拉），承米書拿（約 200）",
              "place": "巴比倫蘇拉與彭貝迪塔諸拉比學院",
              "language": "巴比倫亞蘭文與希伯來文",
              "parent": "巴比倫塔木德",
              "intro": "《贖罪日篇》詳論贖罪日（Yom Kippur）大祭司在聖殿中的事奉禮儀、代罪羊之禮與潔淨規程，並及禁食、認罪、悔改的律法。它兼具聖殿祭儀與贖罪神學，是猶太律法中最莊嚴的節期論篇，中世紀會堂的贖罪日禮儀多本於此。"
            },
            {
              "title_zh": "巴比倫塔木德‧住棚篇",
              "title_orig": "Talmud Bavli — Masekhet Sukkah / סוכה",
              "author": "巴比倫諸拉比學院（阿摩拉世代眾拉比）",
              "era": "約 3–6 世紀纂輯（革馬拉），承米書拿（約 200）",
              "place": "巴比倫蘇拉與彭貝迪塔諸拉比學院",
              "language": "巴比倫亞蘭文與希伯來文",
              "parent": "巴比倫塔木德",
              "intro": "《住棚篇》規範住棚節（Sukkot）之律：棚（sukkah）的合法結構與尺寸、四種植物（lulav 與 etrog 等）的執取禮，以及節期奠水禮與歡慶。它是拉比對利未記所命節期作具體實踐規範的論篇，塑造了中世紀至今的住棚節習俗。"
            },
            {
              "title_zh": "巴比倫塔木德‧節慶篇",
              "title_orig": "Talmud Bavli — Masekhet Beitzah / ביצה",
              "author": "巴比倫諸拉比學院（阿摩拉世代眾拉比）",
              "era": "約 3–6 世紀纂輯（革馬拉），承米書拿（約 200）",
              "place": "巴比倫蘇拉與彭貝迪塔諸拉比學院",
              "language": "巴比倫亞蘭文與希伯來文",
              "parent": "巴比倫塔木德",
              "intro": "《節慶篇》（俗稱「蛋篇」，以首字得名）論節慶日（Yom Tov）與安息日禁令之異同，特別是節慶日為預備飲食所容許的勞作範圍。它界定了節期日與安息日在勞動禁令上的分野，是猶太節期法的重要論篇。"
            },
            {
              "title_zh": "巴比倫塔木德‧歲首篇",
              "title_orig": "Talmud Bavli — Masekhet Rosh Hashanah / ראש השנה",
              "author": "巴比倫諸拉比學院（阿摩拉世代眾拉比）",
              "era": "約 3–6 世紀纂輯（革馬拉），承米書拿（約 200）",
              "place": "巴比倫蘇拉與彭貝迪塔諸拉比學院",
              "language": "巴比倫亞蘭文與希伯來文",
              "parent": "巴比倫塔木德",
              "intro": "《歲首篇》論猶太曆法與新年（Rosh Hashanah）之律：新月的判定與作證、曆法的訂定、吹角禮（shofar）的規範，以及該日作為審判之日的神學。它是拉比掌理曆法與節期的關鍵論篇，中世紀猶太曆制的權威依據。"
            },
            {
              "title_zh": "巴比倫塔木德‧禁食篇",
              "title_orig": "Talmud Bavli — Masekhet Taanit / תענית",
              "author": "巴比倫諸拉比學院（阿摩拉世代眾拉比）",
              "era": "約 3–6 世紀纂輯（革馬拉），承米書拿（約 200）",
              "place": "巴比倫蘇拉與彭貝迪塔諸拉比學院",
              "language": "巴比倫亞蘭文與希伯來文",
              "parent": "巴比倫塔木德",
              "intro": "《禁食篇》規範公眾禁食日之律，尤其因乾旱等災厄而宣告的禁食與祈雨禮，並記述聖殿被毀諸紀念禁食。它兼含律法與大量敬虔傳說（aggadah），是猶太社群面對災難時集體悔罪祈求的法度依據。"
            },
            {
              "title_zh": "巴比倫塔木德‧卷軸篇",
              "title_orig": "Talmud Bavli — Masekhet Megillah / מגילה",
              "author": "巴比倫諸拉比學院（阿摩拉世代眾拉比）",
              "era": "約 3–6 世紀纂輯（革馬拉），承米書拿（約 200）",
              "place": "巴比倫蘇拉與彭貝迪塔諸拉比學院",
              "language": "巴比倫亞蘭文與希伯來文",
              "parent": "巴比倫塔木德",
              "intro": "《卷軸篇》論普珥節誦讀《以斯帖記》書卷（megillah）之律，兼及會堂中妥拉與先知書的公開誦讀規程、聖物之神聖等級與譯經規範。它是猶太會堂讀經禮儀的核心論篇，影響中世紀會堂儀軌甚深。"
            },
            {
              "title_zh": "巴比倫塔木德‧中節篇",
              "title_orig": "Talmud Bavli — Masekhet Moed Katan / מועד קטן",
              "author": "巴比倫諸拉比學院（阿摩拉世代眾拉比）",
              "era": "約 3–6 世紀纂輯（革馬拉），承米書拿（約 200）",
              "place": "巴比倫蘇拉與彭貝迪塔諸拉比學院",
              "language": "巴比倫亞蘭文與希伯來文",
              "parent": "巴比倫塔木德",
              "intro": "《中節篇》論逾越節與住棚節「中間日」（Chol ha-Moed）所容許與禁止的勞作，並詳述服喪（avelut）之律：守喪期、居喪禮儀與慰問之規。它是猶太喪葬法與中間節期法的主要依據。"
            },
            {
              "title_zh": "巴比倫塔木德‧朝節篇",
              "title_orig": "Talmud Bavli — Masekhet Chagigah / חגיגה",
              "author": "巴比倫諸拉比學院（阿摩拉世代眾拉比）",
              "era": "約 3–6 世紀纂輯（革馬拉），承米書拿（約 200）",
              "place": "巴比倫蘇拉與彭貝迪塔諸拉比學院",
              "language": "巴比倫亞蘭文與希伯來文",
              "parent": "巴比倫塔木德",
              "intro": "《朝節篇》論三大朝聖節（逾越、七七、住棚）上耶路撒冷朝覲獻祭之律，並及潔淨等級規範；其末章亦含著名的默卡巴（神秘上升）敬虔傳述。它是聖殿朝聖法與潔淨法的重要論篇。"
            },
            {
              "title_zh": "巴比倫塔木德‧娶寡篇",
              "title_orig": "Talmud Bavli — Masekhet Yevamot / יבמות",
              "author": "巴比倫諸拉比學院（阿摩拉世代眾拉比）",
              "era": "約 3–6 世紀纂輯（革馬拉），承米書拿（約 200）",
              "place": "巴比倫蘇拉與彭貝迪塔諸拉比學院",
              "language": "巴比倫亞蘭文與希伯來文",
              "parent": "巴比倫塔木德",
              "intro": "《娶寡篇》論利未拉特婚（yibbum）與脫履禮（chalitzah）之律：兄弟無嗣而亡時，其寡嫂的再婚義務與豁免程序，並廣及婚姻的禁例與合法性。它是猶太婚姻法婦女部的首篇，法理最為繁複。"
            },
            {
              "title_zh": "巴比倫塔木德‧願誓篇",
              "title_orig": "Talmud Bavli — Masekhet Nedarim / נדרים",
              "author": "巴比倫諸拉比學院（阿摩拉世代眾拉比）",
              "era": "約 3–6 世紀纂輯（革馬拉），承米書拿（約 200）",
              "place": "巴比倫蘇拉與彭貝迪塔諸拉比學院",
              "language": "巴比倫亞蘭文與希伯來文",
              "parent": "巴比倫塔木德",
              "intro": "《願誓篇》論許願（neder）與禁戒之律：如何立願、願的效力與範圍、以及由智者解除誓願（hatarat nedarim）之程序。它是猶太誓願法的核心論篇，深刻影響中世紀猶太人的宗教承諾實踐。"
            },
            {
              "title_zh": "巴比倫塔木德‧拿細耳篇",
              "title_orig": "Talmud Bavli — Masekhet Nazir / נזיר",
              "author": "巴比倫諸拉比學院（阿摩拉世代眾拉比）",
              "era": "約 3–6 世紀纂輯（革馬拉），承米書拿（約 200）",
              "place": "巴比倫蘇拉與彭貝迪塔諸拉比學院",
              "language": "巴比倫亞蘭文與希伯來文",
              "parent": "巴比倫塔木德",
              "intro": "《拿細耳篇》論拿細耳願（nazir）之律：離俗歸神者禁酒、不剃髮、不觸屍的規範，願期屆滿的獻祭與剃髮禮，以及誤觸不潔的補救。它承續《願誓篇》，是離俗歸獻法的專篇。"
            },
            {
              "title_zh": "巴比倫塔木德‧疑妻篇",
              "title_orig": "Talmud Bavli — Masekhet Sotah / סוטה",
              "author": "巴比倫諸拉比學院（阿摩拉世代眾拉比）",
              "era": "約 3–6 世紀纂輯（革馬拉），承米書拿（約 200）",
              "place": "巴比倫蘇拉與彭貝迪塔諸拉比學院",
              "language": "巴比倫亞蘭文與希伯來文",
              "parent": "巴比倫塔木德",
              "intro": "《疑妻篇》論被疑不貞之妻（sotah）的苦水試驗之律（民數記所載），並廣及以希伯來文宣讀的各種禮儀程式（如破頸母牛、塗油君王）。它兼含婚姻法與禮儀法，是婦女部的重要論篇。"
            },
            {
              "title_zh": "巴比倫塔木德‧笞刑篇",
              "title_orig": "Talmud Bavli — Masekhet Makkot / מכות",
              "author": "巴比倫諸拉比學院（阿摩拉世代眾拉比）",
              "era": "約 3–6 世紀纂輯（革馬拉），承米書拿（約 200）",
              "place": "巴比倫蘇拉與彭貝迪塔諸拉比學院",
              "language": "巴比倫亞蘭文與希伯來文",
              "parent": "巴比倫塔木德",
              "intro": "《笞刑篇》論刑律：可處笞刑之罪、逃城（庇護城）對誤殺者的保護、以及作偽證者的反坐之罰。它承續《公會篇》而專論刑罰執行，是猶太刑法的核心論篇。"
            },
            {
              "title_zh": "巴比倫塔木德‧誓言篇",
              "title_orig": "Talmud Bavli — Masekhet Shevuot / שבועות",
              "author": "巴比倫諸拉比學院（阿摩拉世代眾拉比）",
              "era": "約 3–6 世紀纂輯（革馬拉），承米書拿（約 200）",
              "place": "巴比倫蘇拉與彭貝迪塔諸拉比學院",
              "language": "巴比倫亞蘭文與希伯來文",
              "parent": "巴比倫塔木德",
              "intro": "《誓言篇》論各種法律誓言之律：法庭上證人與被告的具誓、保管人與債務糾紛中的誓言、以及妄誓與潔淨相關的誓約。它是猶太民事訴訟法中誓證制度的根本論篇。"
            },
            {
              "title_zh": "巴比倫塔木德‧誤裁篇",
              "title_orig": "Talmud Bavli — Masekhet Horayot / הוריות",
              "author": "巴比倫諸拉比學院（阿摩拉世代眾拉比）",
              "era": "約 3–6 世紀纂輯（革馬拉），承米書拿（約 200）",
              "place": "巴比倫蘇拉與彭貝迪塔諸拉比學院",
              "language": "巴比倫亞蘭文與希伯來文",
              "parent": "巴比倫塔木德",
              "intro": "《誤裁篇》論公會（Sanhedrin）、大祭司或君王因錯誤裁決而致眾人犯罪時的贖罪之律與責任歸屬。它是拉比論司法權威誤判責任的專篇，關乎律法權威的界限。"
            },
            {
              "title_zh": "巴比倫塔木德‧常食篇",
              "title_orig": "Talmud Bavli — Masekhet Chullin / חולין",
              "author": "巴比倫諸拉比學院（阿摩拉世代眾拉比）",
              "era": "約 3–6 世紀纂輯（革馬拉），承米書拿（約 200）",
              "place": "巴比倫蘇拉與彭貝迪塔諸拉比學院",
              "language": "巴比倫亞蘭文與希伯來文",
              "parent": "巴比倫塔木德",
              "intro": "《常食篇》論非聖物（chullin）之潔食律：合法宰牲（shechitah）的規範、禁食之肉、乳肉相分、以及各種潔與不潔動物的辨識。它是猶太日常飲食潔淨法（kashrut）最核心的論篇，中世紀猶太食律皆本於此。"
            },
            {
              "title_zh": "巴比倫塔木德‧頭生篇",
              "title_orig": "Talmud Bavli — Masekhet Bekhorot / בכורות",
              "author": "巴比倫諸拉比學院（阿摩拉世代眾拉比）",
              "era": "約 3–6 世紀纂輯（革馬拉），承米書拿（約 200）",
              "place": "巴比倫蘇拉與彭貝迪塔諸拉比學院",
              "language": "巴比倫亞蘭文與希伯來文",
              "parent": "巴比倫塔木德",
              "intro": "《頭生篇》論頭生者之律：頭生牲畜歸祭司、頭生子的贖銀，以及有殘疾牲畜不得獻祭的辨識規範。它屬聖物部，是奉獻與祭司權益法的專篇。"
            },
            {
              "title_zh": "巴比倫塔木德‧估價篇",
              "title_orig": "Talmud Bavli — Masekhet Arakhin / ערכין",
              "author": "巴比倫諸拉比學院（阿摩拉世代眾拉比）",
              "era": "約 3–6 世紀纂輯（革馬拉），承米書拿（約 200）",
              "place": "巴比倫蘇拉與彭貝迪塔諸拉比學院",
              "language": "巴比倫亞蘭文與希伯來文",
              "parent": "巴比倫塔木德",
              "intro": "《估價篇》論將人身或財物「估價」奉獻聖殿之律（利未記所載的等值奉獻），並及禧年田產的回贖與估值。它是聖物奉獻估值法的專篇。"
            },
            {
              "title_zh": "巴比倫塔木德‧剪除篇",
              "title_orig": "Talmud Bavli — Masekhet Keritot / כריתות",
              "author": "巴比倫諸拉比學院（阿摩拉世代眾拉比）",
              "era": "約 3–6 世紀纂輯（革馬拉），承米書拿（約 200）",
              "place": "巴比倫蘇拉與彭貝迪塔諸拉比學院",
              "language": "巴比倫亞蘭文與希伯來文",
              "parent": "巴比倫塔木德",
              "intro": "《剪除篇》論當受「剪除」（karet，天罰滅絕）之重罪及其誤犯時所需的贖罪祭。它繫聖物部，系統整理了故意與過失重罪的贖罪律法。"
            },
            {
              "title_zh": "巴比倫塔木德‧替換篇",
              "title_orig": "Talmud Bavli — Masekhet Temurah / תמורה",
              "author": "巴比倫諸拉比學院（阿摩拉世代眾拉比）",
              "era": "約 3–6 世紀纂輯（革馬拉），承米書拿（約 200）",
              "place": "巴比倫蘇拉與彭貝迪塔諸拉比學院",
              "language": "巴比倫亞蘭文與希伯來文",
              "parent": "巴比倫塔木德",
              "intro": "《替換篇》論以他牲替換已奉獻聖牲之律（利未記所禁）：替換的行為雖屬違誡且無效，然被替之牲與替換之牲皆成聖，須依例處置。它繫聖物部，系統整理了奉獻聖物的替換、轉讓與贖回規範，是猶太聖殿祭儀法的專篇。"
            }
          ]
        },
        {
          "key": "jewish-codes",
          "label": "猶太律典部",
          "label_en": "Jewish Legal Codes",
          "desc": "Geonic 時代至中世紀後期的猶太律法彙編——大律例、里夫、羅什、圖爾四部。",
          "works": [
            {
              "title_zh": "大律例（哈拉哈大典）",
              "title_orig": "Halakhot Gedolot",
              "author": "傳為西門‧凱雅拉/耶胡代‧高翁(Shimon Kayyara / Yehudai Gaon)",
              "era": "約 825(高翁時代)",
              "place": "巴比倫‧蘇拉(Babylonia / Sura)",
              "language": "希伯來文‧亞蘭文",
              "intro": "《大律例》是高翁時代(Geonim)巴比倫學院最重要的律法彙編之一，將塔木德的律法內容按誡命與主題系統整理成可行的法典，並首開列舉「六百一十三誡」之先河。它是塔木德成書後、邁蒙尼德之前律法法典化的奠基階段成果，代表巴比倫高翁律學的權威，深刻塑造了此後整個猶太律法傳統的體例。"
            },
            {
              "title_zh": "問答律義（舍以爾托特）",
              "title_orig": "Sheʾiltot de-Rav Aḥai Gaʾon / שאילתות דרב אחאי גאון",
              "author": "阿海‧迦翁（Aḥa of Shabḥa／Rav Aḥai Gaon）",
              "era": "約8世紀中葉（c. 750）",
              "place": "巴比倫（蘇拉附近沙布哈，後遷巴勒斯坦）",
              "language": "巴比倫亞蘭文／希伯來文",
              "intro": "迦翁時期最早成書的律法著作之一，依每週安息日讀經段落編排一百餘篇「問義」（sheʾilta），每篇提出律法問題、援引塔木德論證並勸勉遵行，兼具講道與教法功能。體裁獨特，開後世按週分講律法之先河，是研究早期迦翁律學與講壇傳統的重要文本。"
            },
            {
              "title_zh": "律例書（里夫律典）",
              "title_orig": "Sefer ha-Halakhot",
              "author": "以撒‧阿爾法西(里夫，Isaac ben Jacob Alfasi，卒 1103)",
              "era": "約 1070–1100",
              "place": "非斯‧盧塞納(Fez / Lucena, 北非‧安達魯斯)",
              "language": "希伯來文‧亞蘭文",
              "intro": "《律例書》是中世紀猶太律法史上承先啟後的巨著，北非法學家阿爾法西(尊稱里夫)將浩瀚的巴比倫塔木德删繁就簡，僅保留與實際律法(哈拉哈)相關的辯論並附以裁斷，成為一部可據以行事的精要法典。它是邁蒙尼德《密西拿妥拉》之前最權威的律法彙編，深刻影響後世《四部律典》與《舖設的餐桌》，是塞法迪猶太律學的基石。"
            },
            {
              "title_zh": "阿舍爾律斷（羅什判例）",
              "title_orig": "Piske ha-Rosh / Hilkhot ha-Rosh / פסקי הרא\"ש",
              "author": "阿舍爾‧本‧耶希爾（Asher ben Jehiel，Rosh）",
              "era": "約 13 世紀末至 14 世紀初（作者卒 1327）",
              "place": "德意志→西班牙托雷多",
              "language": "希伯來文",
              "intro": "阿舍爾承阿爾法西體例、融會德法（阿什肯納茲）與西班牙（塞法迪）兩大傳統而成的律法判例集。作者由德意志遷居托雷多，使兩地律法傳統交會，其判斷成為後世律法定說的三大支柱之一，是中世紀猶太律法跨地域整合的關鍵文本。"
            },
            {
              "title_zh": "圖爾‧生活之道部",
              "title_orig": "Ṭur Oraḥ Ḥayyim / טור אורח חיים",
              "author": "雅各‧本‧阿舍爾（Jacob ben Asher，Baʿal ha-Turim）",
              "era": "約 1300–1340 編成",
              "place": "西班牙托萊多（原籍德意志科隆）",
              "language": "希伯來文",
              "parent": "四部律典（圖爾）",
              "intro": "《圖爾》第一柱「生活之道」（Oraḥ Ḥayyim）彙整猶太人日常宗教生活之律：晨起禱告、經匣與流蘇、會堂禮儀、安息日與節期規程。它只錄實務裁定、略去塔木德辯證，是中世紀後期最實用的猶太日常律典，後為《舖設之席》同名部之藍本。"
            },
            {
              "title_zh": "圖爾‧教誨部",
              "title_orig": "Ṭur Yoreh Deʿah / טור יורה דעה",
              "author": "雅各‧本‧阿舍爾（Jacob ben Asher，Baʿal ha-Turim）",
              "era": "約 1300–1340 編成",
              "place": "西班牙托萊多（原籍德意志科隆）",
              "language": "希伯來文",
              "parent": "四部律典（圖爾）",
              "intro": "《圖爾》第二柱「教誨」（Yoreh Deʿah）彙整潔食（宰牲、乳肉相分、禁食）、誓願、割禮、皈依、喪葬與哀悼、放貸與偶像崇拜諸律。它是猶太潔淨與禮俗法最廣涵的一柱，中世紀拉比裁決的常用依據。"
            },
            {
              "title_zh": "圖爾‧幫助之石部",
              "title_orig": "Ṭur Even ha-ʿEzer / טור אבן העזר",
              "author": "雅各‧本‧阿舍爾（Jacob ben Asher，Baʿal ha-Turim）",
              "era": "約 1300–1340 編成",
              "place": "西班牙托萊多（原籍德意志科隆）",
              "language": "希伯來文",
              "parent": "四部律典（圖爾）",
              "intro": "《圖爾》第三柱「幫助之石」（Even ha-ʿEzer）彙整婚姻家庭之律：訂婚與結婚、婚書（ketubah）、離婚（get）、利未拉特婚與脫履禮。它是中世紀後期猶太婚姻法的權威編纂，規範了社群的家庭秩序。"
            },
            {
              "title_zh": "圖爾‧公斷胸牌部",
              "title_orig": "Ṭur Ḥoshen Mishpaṭ / טור חושן משפט",
              "author": "雅各‧本‧阿舍爾（Jacob ben Asher，Baʿal ha-Turim）",
              "era": "約 1300–1340 編成",
              "place": "西班牙托萊多（原籍德意志科隆）",
              "language": "希伯來文",
              "parent": "四部律典（圖爾）",
              "intro": "《圖爾》第四柱「公斷胸牌」（Ḥoshen Mishpaṭ）彙整民事與刑事法：法庭程序、借貸與擔保、買賣與契約、損害賠償、繼承與遺產。它是猶太民法最完整的一柱，中世紀猶太自治法庭的實務依據。"
            }
          ]
        },
        {
          "key": "maimonides-law",
          "label": "邁蒙尼德律法部",
          "label_en": "Maimonidean Law",
          "desc": "邁蒙尼德《密西拿妥拉》十四卷與《誡命之書》，中世紀最系統的猶太律法法典。",
          "works": [
            {
              "title_zh": "誡命之書（邁蒙尼德六一三誡）",
              "title_orig": "Sefer ha-Mitzvot / كتاب الفرائض · ספר המצוות",
              "author": "邁蒙尼德（Maimonides / Rambam）",
              "era": "約 1170 年",
              "place": "埃及福斯塔特",
              "language": "猶太–阿拉伯文（後譯希伯來文）",
              "extent": "一卷",
              "intro": "邁蒙尼德以猶太–阿拉伯文寫成的誡命枚舉專著，系統羅列妥拉六百一十三條誡命（二百四十八正誡、三百六十五禁誡），並先立十四條甄別原則辨明何者當計。它是《密西拿妥拉》大法典的先導綱目，其誡命清單與納曼尼德的異議辯難成為中世紀猶太律法學的重要公案。"
            },
            {
              "title_zh": "密西拿妥拉‧知識之書",
              "title_orig": "Mishneh Torah — Sefer ha-Madda (ספר המדע)",
              "author": "邁蒙尼德（Moses Maimonides, Rambam）",
              "era": "約1170–1180年",
              "place": "埃及福斯塔特（開羅舊城）",
              "language": "希伯來文",
              "parent": "密西拿妥拉",
              "extent": "全書十四卷之第一卷",
              "intro": "邁蒙尼德十四卷猶太律法大典的首卷，奠定信仰根基篇（Yesodei ha-Torah）、品德篇、悔改篇與偶像崇拜律。以清晰希伯來文將塔木德浩瀚判例系統化為可檢索律典，開篇即論神之唯一、先知與自由意志，為全書神學與倫理總綱。"
            },
            {
              "title_zh": "密西拿妥拉‧敬愛之書",
              "title_orig": "Sefer Ahavah — The Book of Love",
              "author": "邁蒙尼德",
              "era": "約1170–1180年",
              "place": "埃及福斯塔特",
              "language": "希伯來文",
              "parent": "密西拿妥拉",
              "extent": "第二卷",
              "intro": "匯集信徒須恆常履行、以表達對神敬愛的誡命：誦讀「聽命篇」（Shema）、祈禱、經匣（tefillin）、門柱經卷、割禮、祭司祝福與飯後謝恩等，規範日常敬拜的次第與儀節。"
            },
            {
              "title_zh": "密西拿妥拉‧節期之書",
              "title_orig": "Sefer Zemanim — The Book of Seasons",
              "author": "邁蒙尼德",
              "era": "約1170–1180年",
              "place": "埃及福斯塔特",
              "language": "希伯來文",
              "parent": "密西拿妥拉",
              "extent": "第三卷",
              "intro": "論安息日、逾越節除酵、贖罪日、住棚節等節期與禁食日之律，含曆法推算與節慶儀典，將分散於塔木德「節期部」（Moed）的判例整編成可依循的年度禮儀規程。"
            },
            {
              "title_zh": "密西拿妥拉‧婦女之書",
              "title_orig": "Sefer Nashim — The Book of Women",
              "author": "邁蒙尼德",
              "era": "約1170–1180年",
              "place": "埃及福斯塔特",
              "language": "希伯來文",
              "parent": "密西拿妥拉",
              "extent": "第四卷",
              "intro": "婚姻與家庭法卷：訂婚、婚書（ketubah）、夫妻義務、離婚與寡婦叔娶（levirate）之律，規範猶太社群的親屬與財產關係，是中世紀猶太婚姻裁判的權威依據。"
            },
            {
              "title_zh": "密西拿妥拉‧聖潔之書",
              "title_orig": "Sefer Kedushah — The Book of Holiness",
              "author": "邁蒙尼德",
              "era": "約1170–1180年",
              "place": "埃及福斯塔特",
              "language": "希伯來文",
              "parent": "密西拿妥拉",
              "extent": "第五卷",
              "intro": "以「聖潔」統攝禁忌之律：禁止的性關係、潔淨與不潔之飲食（kashrut）與合禮屠宰（shechitah）。透過飲食與身體的規範，界定以色列作為聖潔子民的界線。"
            },
            {
              "title_zh": "密西拿妥拉‧誓願之書",
              "title_orig": "Sefer Hafla'ah — The Book of Asseverations",
              "author": "邁蒙尼德",
              "era": "約1170–1180年",
              "place": "埃及福斯塔特",
              "language": "希伯來文",
              "parent": "密西拿妥拉",
              "extent": "第六卷",
              "intro": "論誓言、許願、拿細耳願（nazirite）與聖殿估價奉獻之律，處理人向神所立言辭承諾的效力、解除與違誓之罰，屬言語約束的專卷。"
            },
            {
              "title_zh": "密西拿妥拉‧農作之書",
              "title_orig": "Sefer Zeraim — The Book of Agriculture",
              "author": "邁蒙尼德",
              "era": "約1170–1180年",
              "place": "埃及福斯塔特",
              "language": "希伯來文",
              "parent": "密西拿妥拉",
              "extent": "第七卷",
              "intro": "農事與土產律卷：田角留予窮人、什一奉獻、安息年與禧年、祭司與利未人所得之份，將與應許之地相繫的農業誡命整編，兼顧慈善與聖殿供養。"
            },
            {
              "title_zh": "密西拿妥拉‧聖殿事奉之書",
              "title_orig": "Sefer Avodah — The Book of Temple Service",
              "author": "邁蒙尼德",
              "era": "約1170–1180年",
              "place": "埃及福斯塔特",
              "language": "希伯來文",
              "parent": "密西拿妥拉",
              "extent": "第八卷",
              "intro": "詳述聖殿建築、祭司職與常獻祭之律。聖殿雖已不存，邁蒙尼德仍系統保存其事奉規制，寄託彌賽亞時代重建的盼望，體現律法的完備與末世期待。"
            },
            {
              "title_zh": "密西拿妥拉‧祭獻之書",
              "title_orig": "Sefer Korbanot — The Book of Offerings",
              "author": "邁蒙尼德",
              "era": "約1170–1180年",
              "place": "埃及福斯塔特",
              "language": "希伯來文",
              "parent": "密西拿妥拉",
              "extent": "第九卷",
              "intro": "論個人所獻之祭：逾越節羔羊、贖罪祭、還願祭與各類個別供物之律，補聖殿事奉卷之常獻，聚焦信徒因事因願而獻的特定祭儀。"
            },
            {
              "title_zh": "密西拿妥拉‧潔淨之書",
              "title_orig": "Sefer Taharah — The Book of Cleanness",
              "author": "邁蒙尼德",
              "era": "約1170–1180年",
              "place": "埃及福斯塔特",
              "language": "希伯來文",
              "parent": "密西拿妥拉",
              "extent": "第十卷",
              "intro": "儀式潔淨與不潔之律：屍體、痲瘋、經血與各種不潔之源，以及浸禮池（mikveh）潔淨之法，整編塔木德「潔淨部」最艱深的判例體系。"
            },
            {
              "title_zh": "密西拿妥拉‧損害之書",
              "title_orig": "Sefer Nezikin — The Book of Torts",
              "author": "邁蒙尼德",
              "era": "約1170–1180年",
              "place": "埃及福斯塔特",
              "language": "希伯來文",
              "parent": "密西拿妥拉",
              "extent": "第十一卷",
              "intro": "侵權與刑事律卷：牲畜與財物致損之賠償、盜竊、搶奪、傷害與殺人之罰，確立損害責任與量刑原則，為猶太民刑事裁判核心。"
            },
            {
              "title_zh": "密西拿妥拉‧取得之書",
              "title_orig": "Sefer Kinyan — The Book of Acquisition",
              "author": "邁蒙尼德",
              "era": "約1170–1180年",
              "place": "埃及福斯塔特",
              "language": "希伯來文",
              "parent": "密西拿妥拉",
              "extent": "第十二卷",
              "intro": "論所有權取得之律：買賣、贈與、鄰產優先權與奴僕之制，界定財產轉移的法律行為與生效要件，是猶太契約法的基礎卷。"
            },
            {
              "title_zh": "密西拿妥拉‧民事律之書",
              "title_orig": "Sefer Mishpatim — The Book of Civil Laws",
              "author": "邁蒙尼德",
              "era": "約1170–1180年",
              "place": "埃及福斯塔特",
              "language": "希伯來文",
              "parent": "密西拿妥拉",
              "extent": "第十三卷",
              "intro": "民事債法卷：雇傭、租賃、借貸、寄託、繼承與債權之律，處理日常經濟往來的權利義務，與「取得之書」共構猶太財產與契約法全貌。"
            },
            {
              "title_zh": "密西拿妥拉‧審判官之書",
              "title_orig": "Mishneh Torah — Sefer Shofetim (Book of Judges) / ספר שופטים",
              "author": "邁蒙尼德（Moses Maimonides，Rambam）",
              "era": "約 1170–1180",
              "place": "埃及福斯塔特",
              "language": "希伯來文",
              "parent": "密西拿妥拉",
              "extent": "第十四卷（Sefer Shofetim）",
              "intro": "《密西拿妥拉》十四卷之末卷，統論司法與政制律法：公會（Sanhedrin）、證據、叛逆長老、悼亡、君王與戰爭，並以彌賽亞時代的律法圖景作結。它是邁蒙尼德律法體系中最具政治神學意味的一卷，其君王與戰爭律例是中世紀猶太政制思想的權威文本。"
            }
          ]
        },
        {
          "key": "karaite-law",
          "label": "卡拉派猶太律法部",
          "label_en": "Karaite Jewish Law",
          "desc": "拒斥拉比口傳、獨尊成文妥拉的卡拉派律法典籍。",
          "works": [
            {
              "title_zh": "光明與瞭望塔之書",
              "title_orig": "Kitāb al-Anwār wa-l-Marāqib / كتاب الأنوار والمراقب",
              "author": "雅各布‧蓋爾基薩尼（Yaʿqūb al-Qirqisānī）",
              "era": "約 937 年",
              "place": "伊拉克（巴格達一帶）",
              "language": "猶太–阿拉伯文",
              "extent": "多卷",
              "intro": "卡拉派（Karaites，只認成文妥拉、拒斥拉比口傳律法）最重要的律法與教義鉅著，蓋爾基薩尼以猶太–阿拉伯文論卡拉派律法的推導原則、節期曆算、潔淨與婚姻諸法，並記述當時猶太各教派與基督教。它是研究中世紀卡拉派法學及其與拉比猶太教之爭的核心文獻。"
            },
            {
              "title_zh": "誡命之書（阿南派）",
              "title_orig": "Sefer ha-Mitzvot de-Anan",
              "author": "阿南‧本‧大衛（Anan ben David）",
              "era": "約770年（8世紀）",
              "place": "巴比倫／巴格達",
              "language": "阿拉米文",
              "intro": "卡拉派（早期稱阿南派）奠基者阿南‧本‧大衛的律法綱領，以阿拉米文立法，主張直探聖經明文、拒斥拉比口傳律法，另立齋戒、婚姻、潔淨等異於拉比傳統的嚴格律例。原書僅存殘篇，由哈爾卡維自開羅藏經庫抄本輯校刊布，是卡拉派律法傳統的源頭文獻。"
            }
          ]
        },
        {
          "key": "heretic-discipline",
          "label": "異端與衍生宗教教規部",
          "label_en": "Heterodox & Derived-Religion Discipline",
          "desc": "卡特里派、瓦勒度派等基督教異端紀律，及德魯茲教衍生宗教的法度。",
          "works": [
            {
              "title_zh": "卡特里派禮儀書（奧克語慰勉禮）",
              "title_orig": "Rituel cathare (occitan)",
              "author": "卡特里派（純潔派，佚名）",
              "era": "13世紀",
              "place": "朗格多克（法國南部）",
              "language": "奧克語（普羅旺斯方言，附拉丁）",
              "intro": "中世紀朗格多克卡特里派（純潔派）以普羅旺斯方言留存的教規禮儀書，載其唯一聖禮「慰勉禮」（consolamentum）的按手施行程序、認信與紀律規條。它是這支被十字軍與宗教裁判所剿滅的二元論教派罕存的第一手紀律文獻，附於同抄本的方言新約之後。"
            },
            {
              "title_zh": "瓦勒度派紀律",
              "title_orig": "Disciplina Valdensium",
              "author": "里昂的瓦勒度(Valdès)及其追隨者",
              "era": "12 世紀末起",
              "place": "里昂‧阿爾卑斯山區",
              "language": "拉丁文‧方言",
              "intro": "瓦勒度派源於里昂富商瓦勒度散盡家財、誓守使徒貧窮並巡迴傳道，因未經許可講道而被逐出教會。其紀律強調自願清貧、以方言誦讀傳講聖經、拒絕起誓與謊言，並有巡迴傳道者(barbes)的派遣制度。被定為異端後轉入山區秘密傳承，是中世紀流傳最久的異端團體之一。其平信徒讀經與清貧理想，被後世視為宗教改革的先聲。"
            }
          ]
        }
      ]
    }
},
    {
  key: 'lun',
  name: '論藏',
  name_en: 'Treatises and Scholastic Disputations',
  glyph: '論',
  genres: '論‧辯‧駁‧註疏‧大全‧神祕',
  summary: '收中世紀（約 800–1500）拉丁西方、拜占庭與伊斯蘭交鋒區的論述性著作：經院哲學的思辨大全、東方教會的神學辯護、跨宗教護教與駁論，以及密契神祕傳統。正藏為基督宗教自身的論述主流，外藏收與之交鋒、對話或衍生的伊斯蘭哲學、猶太哲學、前改教異議與衍生宗教文獻。',
  zheng: {
    summary: '基督宗教（拉丁西方與拜占庭）自身的論述傳統，從經院思辨到密契神祕。',
    divisions: [
      {
        key: 'scholastic',
        label: '經院哲學部',
        label_en: 'Scholastic Philosophy',
        desc: '以辯證法與三段論建構信仰之理性架構的拉丁西方學院傳統，從安瑟莫到奧坎。',
        works: [
          { title_zh: '證道', title_orig: 'Proslogion', author: '坎特伯里的安瑟莫', era: '約 1078', place: '諾曼第貝克修道院／坎特伯里', language: '拉丁文', intro: '安瑟莫在此書中提出著名的「本體論論證」，主張上帝即「無法設想比之更偉大者」，既然如此者必然存在於實在而非僅存於理智之中。全書以向上帝祈禱的第一人稱獨白展開，將嚴密的邏輯推演融入虔敬的默觀，開啟「信仰尋求理解（fides quaerens intellectum）」的經院方法。後世由高尼羅與阿奎那不斷回應辯難，影響直達笛卡兒與近代形上學。', note: '原題一度名《信仰尋求理解》', link: '/fathers' },
          { title_zh: '信仰尋求理解（宣講）', title_orig: 'Monologion', author: '坎特伯里的安瑟莫', era: '約 1076', place: '諾曼第貝克修道院', language: '拉丁文', intro: '此書是安瑟莫應修士之請而作的「宣講」式默想，不訴諸聖經權威，純以理性推論上帝之存在、本質與三位一體。由受造物的善與存在層級，逐步上溯至至高的善與最高存有，論證神性的單一與位格的區分。全書奠定其後《證道》的思路，展現安瑟莫「信仰先行、理解隨後」的根本立場，是拉丁經院神學以理性闡釋信理的早期典範。', link: '/fathers' },
          { title_zh: '是與否', title_orig: 'Sic et Non', author: '彼得‧阿伯拉爾', era: '約 1120', place: '巴黎', language: '拉丁文', intro: '阿伯拉爾蒐集教父與聖經中表面互相矛盾的一百五十八個命題，並列正反論據而不逕下結論，意在訓練學生以辯證方法調和權威、辨明語詞歧義與歷史脈絡。其序言提出考察文本真偽、用語與情境的批判原則，為經院「問題（quaestio）」教學法奠基。此書因其大膽質疑而受爭議，卻深刻塑造了十二世紀以降大學的論辯文化。', link: '/fathers' },
          { title_zh: '四部語錄', title_orig: 'Sententiarum libri quatuor', author: '彼得‧隆巴德', era: '約 1150', place: '巴黎', language: '拉丁文', intro: '隆巴德系統蒐輯教父（尤其奧古斯丁）論述，按「上帝、受造、救贖（道成肉身與德行）、聖事與末世」四卷編排，成為中世紀神學的標準教科書。自十三世紀起，攻讀神學者皆須講授此書，托馬斯、董思高、奧坎等大師的學術生涯多以《語錄註》起步。其條理分明的問題編排，使之成為西方神學教育延續四百年的骨幹文本。', link: '/fathers' },
          { title_zh: '論造物六日', title_orig: 'De natura et origine rerum', author: '大阿爾伯特', era: '約 1250', place: '科隆／巴黎', language: '拉丁文', intro: '大阿爾伯特學識淵博，被尊為「全能博士」，廣註亞里斯多德全集並融會自然哲學、礦物、植物與動物之學。其著作將希臘與阿拉伯的科學知識引入拉丁學界，主張理性探究自然與信仰並行不悖。身為托馬斯‧阿奎那之師，他為亞里斯多德主義在基督教神學中的接納鋪路，是經院全盛期百科全書式的學術巨人。', note: '泛指其亞里斯多德註疏與自然哲學著作群', link: '/fathers' },
          { title_zh: '神學大全', title_orig: 'Summa Theologiae', author: '托馬斯‧阿奎那', era: '1265–1274', place: '羅馬／巴黎／那不勒斯', language: '拉丁文', intro: '阿奎那畢生神學的總綱，分三大部論上帝、人的德行與道德生活、基督與聖事。採「問題—異議—反之—我說—答辯」的辯證體例，融合亞里斯多德哲學與奧古斯丁傳統，建構出條理嚴密的天主教神學體系。其「五路」論證上帝存在、自然法理論與恩典與本性的關係，影響後世至深，至今仍是天主教神哲學的根本經典，惜作者臨終前擱筆未竟。', link: '/fathers' },
          { title_zh: '哲學大全（駁異教大全）', title_orig: 'Summa contra Gentiles', author: '托馬斯‧阿奎那', era: '約 1259–1265', place: '巴黎／義大利', language: '拉丁文', intro: '此書旨在面向不接受聖經權威的對象（尤指穆斯林與猶太哲人）以純理性辯護基督信仰，分四卷論上帝、受造、天意與信仰奧祕。前三卷盡力以哲學論證可由理性企及之真理，第四卷則處理三一、道成肉身等須靠啟示方知的信理。其護教進路與當時拉丁學界面對阿拉伯亞里斯多德主義的挑戰密切相關，是中世紀理性神學的代表作。', link: '/fathers' },
          { title_zh: '心向上帝的旅程', title_orig: 'Itinerarium Mentis in Deum', author: '波那文圖拉', era: '1259', place: '亞西西／拉維爾納山', language: '拉丁文', intro: '波那文圖拉於聖方濟各領受五傷的拉維爾納山默想時所作，描繪心靈藉六個階段上升至與上帝合一的旅程：由外在受造物中見上帝的痕跡，到內省靈魂中的上帝形像，終至超越理智的密契默觀。全書融合方濟靈修、奧古斯丁傳統與新柏拉圖主義，將經院思辨導向神祕默觀，是中世紀靈修神學與哲學交融的典範之作。', link: '/fathers' },
          { title_zh: '任意辯論集', title_orig: 'Quaestiones Quodlibetales / Ordinatio', author: '董思高', era: '約 1300–1308', place: '牛津／巴黎／科隆', language: '拉丁文', intro: '董思高被尊為「精微博士」，其思辨以細密著稱。他主張普遍者具「形式上的區分」、提出個體化原理「此性（haecceitas）」，並力倡意志優先於理智，與托馬斯主義分庭抗禮。其論證聖母無染原罪的進路後為天主教接納為教義。方濟會神學自此以董思高為宗，與道明會的托馬斯主義並列為經院兩大學派。', note: '其著作多由門生整理為《巴黎講錄》與《牛津講錄》', link: '/fathers' },
          { title_zh: '邏輯大全', title_orig: 'Summa Logicae', author: '奧坎的威廉', era: '約 1323', place: '牛津', language: '拉丁文', intro: '奧坎在此書中系統重構亞里斯多德邏輯，主張共相僅為心靈中的概念與語詞，外界唯有個別事物存在，是中世紀唯名論的奠基之作。其「如無必要，勿增實體」的簡約原則（奧坎剃刀）成為後世方法論利器。他將形上學負擔減至最低、嚴格區分信仰與理性的疆界，動搖了經院綜合的根基，預示了近代哲學與經驗主義的轉向。', link: '/fathers' }
        ,
          { title_zh: '上帝何以化身為人', title_orig: 'Cur Deus Homo', author: '坎特伯里的安瑟莫（Anselmus Cantuariensis）', era: '約 1094–1098', place: '英格蘭坎特伯里／義大利（流亡期間）', language: '拉丁文', intro: '西方教會救贖論的奠基之作，以「滿足說／補償說」（satisfaction theory）系統論證神為何必須道成肉身：人因罪虧欠上帝無限的榮耀，唯有兼具神人二性者方能償還此債。全書為安瑟莫與弟子波索（Boso）的對話體，純以「必然理由」（rationes necessariae）撇開基督權威而推演，開經院神學方法之先河。此說取代早期教父「贖價付予魔鬼」之觀點，奠定西方救贖論主流框架，影響直達阿奎那、宗教改革與近代神學。', extent: '二卷' },
          { title_zh: '論真理（辯論問題集）', title_orig: 'Quaestiones disputatae de veritate', author: '托馬斯‧阿奎那', era: '約 1256–1259', place: '巴黎', language: '拉丁文', intro: '阿奎那首次任教巴黎期間主持公開辯論的記錄，凡二十九題二百餘條，前半論真理、知識、上帝之知、天意、預定（知識論與神的全知），後半論善、意志、自由、良知與信望愛諸德及恩寵。以「異議—反之—我說—答辯」的完整辯論體例深入剖析，展現經院「爭議問題（quaestio disputata）」體例的成熟，為《神學大全》諸題奠基，是研究阿奎那思想形成的關鍵文本。', extent: '二十九問' },
          { title_zh: '論存有與本質', title_orig: 'De Ente et Essentia', author: '托馬斯‧阿奎那', era: '約 1252–1256', place: '巴黎', language: '拉丁文', intro: '阿奎那青年時期所作的形上學短論，篇幅雖小而為其哲學奠基。書中釐清「存有（esse）」與「本質（essentia）」之分，主張除上帝外一切受造物的本質與其存在皆為實在的區分，唯獨上帝的本質即其存在；並闡述本質在實體、偶性、純靈與上帝中的不同存在方式。是理解托馬斯式形上學「存在優先」核心洞見的入門經典。', extent: '短論一篇' },
          { title_zh: '神學綱要', title_orig: 'Compendium theologiae', author: '托馬斯‧阿奎那', era: '約 1272–1273', place: '那不勒斯', language: '拉丁文', intro: '阿奎那晚年應其摯友兼祕書雷吉納德之請而作的簡明神學總綱，原擬依「信、望、愛」三德架構統攝全部信理，惜未竟而止於信、望兩部。相較《神學大全》的鉅細靡遺，此書以精煉條理直陳要義，是理解阿奎那思想體系的入門綱領，亦見其臨終前對神學整體的最後綜觀。' },
          { title_zh: '黃金鎖鏈（四福音教父註疏輯）', title_orig: 'Catena aurea', author: '托馬斯‧阿奎那', era: '約 1262–1268（馬太卷 1262–1264 於奧爾維耶托；馬可／路加／約翰三卷在烏爾班四世 1264 年逝後於羅馬完成）', place: '奧爾維耶托（馬太卷）／羅馬（其餘三卷）', language: '拉丁文', intro: '阿奎那應教宗烏爾班四世之請編纂的四福音逐節註釋，輯錄逾八十位希臘與拉丁教父之語，環環相扣如金鏈，故名。此書首度大量引入東方教父（如金口若望、區利羅）的拉丁譯文，補西方註經傳統之闕，既是經院釋經的典範，亦保存了若干今已散佚之教父殘篇，兼具神學與文獻雙重價值。', extent: '四卷（按四福音）' },
          { title_zh: '論真理（早期對話）', title_orig: 'De Veritate', author: '坎特伯里的安瑟莫', era: '約 1080–1086', place: '諾曼第貝克修道院', language: '拉丁文', intro: '安瑟莫在貝克修院所作四篇對話之一，探討真理的本質，主張真理即「正當性（rectitudo）」——事物合於其當然之分。他層層分析陳述、思想、意志、行為、感官與事物存在中的真理，最終上溯至作為一切真理根源與標準的至高真理即上帝本身。展現「信仰尋求理解」方法在認識論上的運用，是安瑟莫早期理性神學的代表。', extent: '對話一篇' },
          { title_zh: '論基督信仰的聖事', title_orig: 'De Sacramentis Christianae Fidei', author: '聖維克托的雨果（Hugo de Sancto Victore）', era: '約 1134', place: '巴黎聖維克托修道院', language: '拉丁文', intro: '雨果以「創造之工（opus conditionis）」與「救贖之工（opus restaurationis）」二編統攝全部信理，被公認為中世紀第一部神學「大全」。從三一、創世、墮落，到道成肉身、聖事與末世，按救恩歷史鋪陳，視聖事為藉可見形質傳遞不可見恩寵的媒介。本書承奧古斯丁傳統而開經院綜合之先河，直接啟發波那文圖拉《簡論》的架構，亦深刻影響彼得‧倫巴《四部語錄》的編排。', extent: '二卷' },
          { title_zh: '論三位一體', title_orig: 'De Trinitate', author: '聖維克托的理查', era: '約 1162–1173', place: '巴黎聖維克托修道院', language: '拉丁文', intro: '理查承雨果之緒，於此六卷鉅著中以理性深入探究三一奧祕，提出以「愛」論證位格之三：至善的愛必須有對象、有共享，故神性的圓滿之愛要求三個彼此相愛、共融的位格。他將奧古斯丁的心理類比推進為「人際之愛」的類比，對位格（persona）概念作出原創性界定，影響後世波那文圖拉與董思高的三一神學，是聖維克托學派密契與思辨交融的高峰。', extent: '六卷' },
          { title_zh: '簡論（神學綱要）', title_orig: 'Breviloquium', author: '波那文圖拉（Bonaventura）', era: '約 1257', place: '巴黎', language: '拉丁文', intro: '波那文圖拉任方濟各會總會長前夕為初學者所撰的神學綱要，分七部（三一、創造、罪、道成肉身、恩寵、聖事、末世），以「上帝即萬物之源、模範與終向」「創造—復原」的新柏拉圖式流出與回歸架構統攝全部教義，承聖維克托的雨果而下。全書文字凝練、結構嚴整，與其《心向上帝的旅程》一升一降相對應，是方濟會經院神學的系統綱領，與阿奎那《神學大全》並峙。', extent: '七部' },
          { title_zh: '論技藝歸於神學', title_orig: 'De Reductione Artium ad Theologiam', author: '波那文都拉', era: '十三世紀中葉', place: '巴黎', language: '拉丁文', intro: '波那文都拉短論，主張一切人類知識與技藝（機械技藝、感官知識、哲學）皆以聖經之光為源、以神學為歸，呈現方濟會「萬學朝向上帝」的知識總綱。' },
          { title_zh: '六日創世講論', title_orig: 'Collationes in Hexaemeron', author: '波那文都拉', era: '1273', place: '巴黎', language: '拉丁文', intro: '波那文都拉晚年於巴黎方濟會院所作的系列講論（未竟），借創世六日喻基督中心的智慧層級，批判亞里斯多德主義之偏失，被視為其神學思想的總結與對拉丁亞維羅伊主義的回應。' },
          { title_zh: '巴黎講義（牛津定本《語錄註》）', title_orig: 'Ordinatio (Opus Oxoniense)', author: '若望‧董思高（Johannes Duns Scotus）', era: '約 1300–1308', place: '英格蘭牛津／法國巴黎', language: '拉丁文', intro: '「精微博士」董思高親自校訂、至死猶在修訂的《彼得‧倫巴語錄》註釋定本，為其哲學神學的權威表述：主張存有的單義性（univocatio entis）、形式區分（distinctio formalis）、個體化原理「此性」（haecceitas）、意志對理智的優位，並倡聖母無染原罪論。十七世紀沃丁刊本題為《牛津大著》，是蘇格徒學派（Scotism）的根本文獻，批判性 edition 至 2013 年方告完成。' },
          { title_zh: '論第一原理（論首要原理）', title_orig: 'Tractatus de Primo Principio', author: '董思高（若望‧鄧斯‧司各脫）', era: '約 1305–1308', place: '巴黎／科隆', language: '拉丁文', intro: '董思高簡明而嚴密的自然神學專論，大量取材於《牛津定本》，以形上學步驟逐層論證至高首因（上帝）之存在、唯一與無限完美，並發展其「存有單義性」思想。結構嚴密如禱詞兼論證，集中呈現理性所能證知於上帝者，為晚期經院主義對神之屬性最縝密的哲學推演之一。' },
          { title_zh: '隨意問答集（自由辯論集）', title_orig: 'Quodlibeta septem', author: '奧坎的威廉（Guillelmus de Ockham）', era: '約 1322–1325（亞維儂完成）', place: '倫敦／亞維儂', language: '拉丁文', intro: '奧坎七組「隨意辯論」之彙集，就神學與哲學各題即席應辯，涵蓋神之全能與絕對權能（potentia absoluta／ordinata）、認識論、倫理與形上問題。為理解其唯名論神學與意志主義倫理的關鍵文本。' },
          { title_zh: '創世六日論', title_orig: 'Hexaemeron', author: '林肯的羅伯特‧格羅斯泰斯特', era: '約 1232–1235', place: '英格蘭牛津／林肯', language: '拉丁文', intro: '牛津方濟會學派的奠基者、林肯主教格羅斯泰斯特對〈創世記〉首章「創世六日」的註釋。他以強烈的奧古斯丁式「光照論」貫穿全書——上帝是至高的真理與光，光為一切物體形式之始（光之形上學）；並融會其對光學與自然哲學的研究。其譯註亞里斯多德《尼各馬可倫理學》與偽狄奧尼修斯，為十三世紀拉丁學界引入希臘—阿拉伯科學居功厥偉，是英格蘭經院科學傳統的奠基者。', extent: '釋經一卷' },
          { title_zh: '論自然的怨訴', title_orig: 'De planctu naturae', author: '里爾的阿蘭（亞蘭努斯）', era: '約 1160–1170', place: '巴黎／里爾', language: '拉丁文', intro: '阿蘭以散文與韻文交錯的寓言體，藉「自然女神」哀嘆人類違背造物秩序、敗壞德行。表面是道德與宇宙論的詩篇，實為以新柏拉圖主義闡釋受造界和諧與人之墮落的神哲學著作。此書與其《反異端論》《神學規則》同屬十二世紀「文藝復興」思辨傳統，影響但丁與中世紀寓言文學。' },
          { title_zh: '神聖教導（神學大系）', title_orig: 'Magisterium Divinale et Sapientiale', author: '奧維涅的威廉（巴黎的威廉）', era: '約 1223–1240', place: '巴黎', language: '拉丁文', intro: '巴黎主教奧維涅的威廉所撰的龐大神學哲學叢書總稱，含《論三一》《論宇宙》《論靈魂》等多部，是十三世紀初拉丁學界最早正面消化亞里斯多德與阿維森納的系統嘗試之一。他既援引又批判阿拉伯哲學，於存在與本質、靈魂不朽、創世等議題上力辯信仰立場，為大阿爾伯特與阿奎那的綜合鋪路。其著作標誌經院神學由聖維克托傳統向亞里斯多德主義過渡的關鍵階段。', extent: '多部叢書' },
          { title_zh: '論造物（受造界大全）', title_orig: 'Summa de creaturis', author: '大阿爾伯特（艾爾伯圖斯‧馬格努斯）', era: '約 1240–1243', place: '巴黎／科隆', language: '拉丁文', intro: '大阿爾伯特早期的鉅著，系統論述受造世界——四元素、天體、時空、人之靈魂與感官等自然哲學課題，廣納亞里斯多德與阿拉伯註釋家之說並與信仰會通。作為阿奎那之師、中世紀百科全書式的學者，他在此奠定以亞里斯多德自然學為基礎的經院科學進路，是十三世紀基督教吸納希臘—阿拉伯哲學的關鍵文獻。' },
          { title_zh: '神學大全（哈雷斯的亞歷山大大全）', title_orig: 'Summa Universae Theologiae (Summa Halensis / Summa fratris Alexandri)', author: '哈雷斯的亞歷山大（Alexander Halensis）及方濟會編纂群', era: '約 1236–1245', place: '巴黎', language: '拉丁文', intro: '哈雷斯的亞歷山大是首位以隆巴德《語錄》為神學講授基礎、並率先吸收新譯亞里斯多德著作的學者。此部以其名行世的大全由方濟會學者集體編成，是十三世紀規模最大的系統神學嘗試之一，奠定方濟會經院傳統的基礎，深刻影響其學生波那文圖拉，標誌神學從經文註釋轉向系統化問題討論的關鍵。', extent: '四卷' },
          { title_zh: '認識你自己（倫理學）', title_orig: 'Scito te ipsum (Ethica)', author: '彼得‧阿伯拉爾', era: '約 1138–1139', place: '巴黎', language: '拉丁文', intro: '阿伯拉爾以理性分析道德責任，主張罪的本質不在外在行為而在「對上帝的輕蔑」——即明知故犯的內在同意。善惡繫於意向（intentio）而非結果，無知或被迫者不構成罪。此書是十二世紀倫理思想的重要里程碑，將良心與意圖置於道德判斷的核心，深刻影響後世天主教道德神學與良心論。' },
          { title_zh: '論君王之治', title_orig: 'De regimine principum', author: '羅馬的吉爾斯（埃吉迪烏斯‧羅馬努斯，Aegidius Romanus / Giles of Rome）', era: '約 1277–1279', place: '巴黎', language: '拉丁文', intro: '羅馬的吉爾斯為法王腓力四世（時為王儲）所撰的「君鑒」式政治神學論著，依倫理、家政、政治三部，本亞里斯多德《政治學》《倫理學》闡述君主自治、治家與治國之道，主張君主制為最佳政體。此書是中世紀流傳最廣的政治論著之一，存世抄本與譯本數百種，深刻塑造了中世紀晚期的政治思想與君權觀。', extent: '三卷' },
          { title_zh: '任意辯論集（根特的亨利）', title_orig: 'Quodlibeta', author: '根特的亨利', era: '約 1276–1292', place: '巴黎', language: '拉丁文', intro: '根特的亨利人稱「莊嚴博士」，是十三世紀末巴黎最具影響力的世俗神學家，介於托馬斯與董思高之間。其十五部《任意辯論集》與《尋常辯論集大全》探討上帝認識、類比、本質與存在之分、形上學與光照論，力主奧古斯丁式的神聖光照說。其思想為董思高所批判性吸收，是理解十三、十四世紀之交經院論爭的樞紐文獻。', extent: '十五部' },
          { title_zh: '語錄註（里米尼的格里高利）', title_orig: 'Lectura super Sententias', author: '里米尼的格里高利', era: '約 1343–1346', place: '巴黎', language: '拉丁文', intro: '奧斯定會神學家里米尼的格里高利在巴黎講授《四部語錄》的註釋，以嚴格的奧古斯丁恩寵論著稱，力斥半伯拉糾主義，強調人得救全賴神恩、無功自誇，因其嚴峻立場而被稱「孩童折磨者（tortor infantium）」。他兼採奧坎唯名論的邏輯工具，於無限、連續與認識論諸題亦有原創貢獻。是中世紀晚期奧古斯丁學派的代表，預示宗教改革對恩典與預定的強調。', extent: '《語錄》前二卷註' },
          { title_zh: '自然神學（受造物之書）', title_orig: 'Theologia Naturalis sive Liber Creaturarum', author: '塞邦德的雷蒙', era: '約 1434–1436', place: '圖盧茲', language: '拉丁文', intro: '圖盧茲大學教授塞邦德的雷蒙之唯一傳世著作，主張上帝賜人兩部「書」——聖經與受造的自然界，後者人人可讀，足以由受造之階梯上推造物主與信理。全書以理性論證上帝存在、三一、人之尊嚴與救贖，是中世紀晚期自然神學的集大成之作。蒙田曾將其譯為法文並為之辯護，使本書在文藝復興與近代思想中影響廣泛。', extent: '三百三十章' },
          { title_zh: '論有學識的無知', title_orig: 'De docta ignorantia', author: '庫薩的尼古拉（Nicolaus Cusanus）', era: '1440', place: '德意志／義大利', language: '拉丁文', intro: '庫薩的尼古拉晚期中世紀神祕形上學經典，主張真正的智者乃自知其無知者：人之有限理智無法正面把握無限的上帝，唯能藉「對立之巧合（coincidentia oppositorum）」趨近。他以數學類比論上帝為無限的極大與極小之合一，融新柏拉圖主義、否定神學與數學思辨於一爐，跨越中世紀經院與近代哲學，預示近代思想，影響布魯諾、萊布尼茲乃至近代形上學。' },
          { title_zh: '論神的預定與恩典（駁戈特沙爾克雙重預定論）', title_orig: 'De divina praedestinatione liber', author: '厄里根那（Johannes Scotus Eriugena）', era: '約 851', place: '西法蘭克王國宮廷學校', language: '拉丁文', intro: '加洛林時期厄里根那受蘭斯大主教辛克瑪（Hincmar）與拉昂主教帕杜路斯（Pardulus）委託，駁斥戈特沙爾克（Gottschalk）的「雙重預定論」（gemina praedestinatio）。主張神只預定一種、指向人之救恩，神不預定惡與罰，惡乃善之闕如、無實體，並以辯證法（dialectica）論神之單純超越時間。其過度理性化引發爭議，部分命題後遭瓦倫斯（855）與蘭斯（859）等會議定罪，仍為加洛林神學重要文獻。' },
          { title_zh: '自然的區分（論自然／論宇宙萬有）', title_orig: 'Periphyseon (De divisione naturae)', author: '厄里根那（Johannes Scotus Eriugena）', era: '約 862–866', place: '西法蘭克王國', language: '拉丁文', intro: '加洛林時期最宏大的哲學神學體系著作，以師生對話將「自然（natura）」分為四：創造而不受造（神為始）、受造而能創造（理型）、受造而不創造（萬物）、不創造亦不受造（萬物歸神為終），建構一套萬物由神流出又復歸於神的宏大體系。深受希臘教父與偽狄奧尼修斯影響，融神祕主義與新柏拉圖主義，其大膽精微的思辨後因泛神論嫌疑於 1225 年遭教宗譴責焚毀，卻是中世紀早期最具原創性的哲學神學鉅著。', extent: '五卷' },
          { title_zh: '默示錄詮解', title_orig: 'Expositio in Apocalypsim', author: '弗洛雷的約阿希姆', era: '約 1196–1199', place: '卡拉布里亞弗洛雷修道院', language: '拉丁文', intro: '熙篤會隱修院長約阿希姆以三一論詮釋歷史，將之分為聖父（律法）、聖子（恩典）、聖靈（自由與默觀）三時代，主張第三時代即將來臨。此《默示錄詮解》是其歷史神學的集大成，雖部分思想後遭教會審查，卻深刻影響方濟靈修派與後世千禧年運動，是中世紀末世論與聖經詮釋史上極具爭議與影響力的著作。' },
          { title_zh: '詩篇十弦琴（三一神學三部曲）', title_orig: 'Psalterium decem chordarum', author: '弗洛雷的約阿希姆（Ioachim de Fiore）', era: '約 1184–1186', place: '卡拉布里亞科拉佐修道院（Corazzo，南義）；始作於卡薩馬里（Casamari）', language: '拉丁文', intro: '約阿希姆神學三部曲之一（與《和諧之書》Liber Concordiae、《啟示錄詮解》Expositio in Apocalypsim 並列），以「十弦琴」之異象喻三位一體的奧祕，闡發其三一神學。他以聖父、聖子、聖神三個世代劃分救恩史，主張將臨的「聖神時代」屬靈而自由；其歷史神學深刻影響中世紀晚期的末世與靈修思潮（尤其方濟會屬靈派）。本書反對其歸於彼得‧倫巴德的「四位說」（quaternity）；其相關三一論述（連同所附論文）於第四次拉特朗會議（1215）遭譴責。思想史地位極為重要。' },
          { title_zh: '論聖體聖事（駁伯倫加爾）', title_orig: 'De corpore et sanguine Domini', author: '貝克的蘭弗朗克', era: '約 1063–1070', place: '諾曼第貝克修道院／坎特伯里', language: '拉丁文', intro: '貝克院長、後任坎特伯里總主教的蘭弗朗克，撰此書駁斥圖爾的伯倫加爾對聖體真實臨在的否定，以辯證法論證餅酒「實質變化（後稱 transubstantiatio）」而存留外形。此辯論是十一世紀理性運用於聖事神學的關鍵案例，為日後第四次拉特朗會議確立變體論奠基，亦標誌經院方法的興起。' }
        ]
      },
      {
        key: 'byzantine',
        label: '拜占庭神學部',
        label_en: 'Byzantine Theology',
        desc: '787／843 破除聖像之爭以降至 1453 君士坦丁堡陷落的東方希臘教會神學，以靜修主義為高峰。',
        works: [
          { title_zh: '知識百章', title_orig: 'Kephalaia Gnostika（後續編纂）', author: '大馬士革約翰（傳統續編）', era: '8–9 世紀', place: '聖薩巴斯修道院（巴勒斯坦）', language: '希臘文', intro: '大馬士革約翰《知識泉源》集教父神學之大成，其後拜占庭學者承其格言體與系統編纂的傳統，續輯神學百章與信理綱要，為東方正教教義作總結性整理。這些後續編纂保存了希臘教父對三一、道成肉身與聖像的精要論述，並維護了破除聖像爭議後對敬奉聖像的神學辯護，是東方教義傳承不可或缺的橋樑文本。', link: '/fathers' },
          { title_zh: '群書摘記', title_orig: 'Bibliotheca / Myriobiblos', author: '佛提烏（君士坦丁堡牧首）', era: '約 845', place: '君士坦丁堡', language: '希臘文', intro: '佛提烏匯讀並摘記二百八十餘部古典與基督教著作，每部評其內容、文體與作者，許多原書今已失傳，賴此書得窺梗概，是古代文獻學的瑰寶。佛提烏學養博洽，於聖神「和子（Filioque）」之爭中力辯西方教會增訂信經之非，其神學立場深刻形塑了東西方教會分裂的論述。此書既是書目巨著，也是拜占庭文藝復興的標誌。', link: '/fathers' },
          { title_zh: '為靜修者辯護', title_orig: 'Triades pro sanctis hesychastis', author: '額我略‧帕拉馬斯', era: '約 1338–1341', place: '阿索斯聖山／塞薩洛尼基', language: '希臘文', intro: '帕拉馬斯為阿索斯山靜修士的祈禱經驗辯護，回應加拉布里亞的巴爾拉姆之攻擊，闡發上帝「本質」與「能量（energeiai）」之分：人雖無法企及不可知的神性本質，卻能真實分享其非受造的能量（如他泊山之光）而與神合一。此論於 1351 年君士坦丁堡公會議獲確認為正教信理，奠定東方神化（theosis）神學的根基，是拜占庭晚期最重要的神學成就。', link: '/fathers' },
          { title_zh: '靜修派文獻', title_orig: 'Hesychasm（合集）', author: '阿索斯山靜修傳統諸師', era: '14 世紀', place: '阿索斯聖山', language: '希臘文', intro: '靜修主義是拜占庭晚期的內在祈禱運動，以不斷誦念「耶穌禱文」、調節呼吸與內斂心神，追求心靈寧靜（hesychia）與默觀神光。其修行傳統上溯沙漠教父與西奈的格里高利，經帕拉馬斯神學辯護而臻成熟。這批文獻記錄了修行法門與靈修指導，深刻塑造東方正教的靈修面貌，後世匯為《愛神集（Philokalia）》流傳至斯拉夫世界。', link: '/fathers' },
          { title_zh: '神學講論（神聖之愛之歌）', title_orig: 'Hymns of Divine Love / Catecheses', author: '新神學家西默盎', era: '約 1000', place: '君士坦丁堡', language: '希臘文', intro: '西默盎被尊為繼使徒約翰與拿先斯的格里高利後唯一稱「神學家」者，其講論與聖歌以熱烈的第一人稱見證神光的親身經驗，強調聖靈臨在的具體可感與意識可知。他主張真正的神學出自與上帝的直接相遇而非單純學問，為日後靜修主義鋪路。其著作將早期沙漠靈修的密契傳統帶入拜占庭中期，是東方神祕神學承先啟後的關鍵。', link: '/fathers' }
        ,
          { title_zh: '一百五十章（自然·神學·倫理·靜修篇）', title_orig: 'Capita CL physica, theologica, moralia et practica', author: '額我略‧帕拉瑪斯（Gregorios Palamas）', era: '約 1349–1350', place: '希臘塞薩洛尼基（帖撒羅尼迦）', language: '希臘文', intro: '帕拉瑪斯於 1347 年靜修派神學在君士坦丁堡公會議獲勝後所撰的格言體神學精要，凡一百五十章，自人類知識的本性與自然哲學論起，及於上帝的形象、三一、本質（οὐσία）與能量（ἐνέργειαι）之分、聖靈論及靜修之道。以簡明條目濃縮《三聯論》的核心思想，奠定東正教「神之能量可被人領受、本質不可知」的帕拉瑪斯神學，後經 1351 年會議定為正統教義，是繼《三聯論》之後其神學體系最凝練的表述。', extent: '一百五十章' },
          { title_zh: '為神聖靜修者辯護（三聯論）', title_orig: 'Ὑπὲρ τῶν ἱερῶς ἡσυχαζόντων (Triads in Defense of the Holy Hesychasts)', author: '額我略‧帕拉瑪斯（Gregorios Palamas）', era: '約 1338–1341', place: '希臘亞陀斯聖山／帖撒羅尼迦', language: '希臘文', intro: '回應卡拉布里亞哲人巴爾拉姆對亞陀斯靜修士（hesychasts）「耶穌禱文」與見「他泊之光」攻擊而作的三組各三篇論文。帕拉瑪斯區分上帝不可知的「本質」與可被受造者分享的「能量」（energeiai），主張靜修者在禱中所見之光即神的非受造能量，人可分受上帝的非受造能力而真實神化，奠定東正教神祕神學「帕拉瑪主義」的根基，後經 1341、1351 年大公會議確認。' },
          { title_zh: '基督裡的生命', title_orig: 'Peri tēs en Christō zōēs / De vita in Christo', author: '尼古拉‧卡巴西拉斯（Nicholas Kabasilas）', era: '約 1350–1363', place: '帖撒羅尼迦／君士坦丁堡', language: '希臘文', intro: '卡巴西拉斯為拜占庭末期的密契神學家與在俗信徒，此書七卷闡述人與基督的合一藉聖洗、傅油（堅振）與聖體三大入門奧蹟而成，並在現世即可開始「基督裡的生命」漸臻神化（theosis）。他將靜修派的內在祈禱傳統與聖事神學熔於一爐，主張神化生命並非脫離世俗的隱修專利，而是每位信徒可達之境。文辭優美、神學深邃，是東方正教論聖事與成聖的經典。', extent: '七卷' },
          { title_zh: '教座答辯（聖父為唯一根源論）', title_orig: 'De processione Spiritus Sancti / Περὶ τῆς ἐκπορεύσεως τοῦ Ἁγίου Πνεύματος', author: '尼魯斯‧卡巴西拉斯', era: '約 1355–1363', place: '帖撒羅尼迦', language: '希臘文', intro: '尼魯斯‧卡巴西拉斯繼帕拉瑪斯任帖撒羅尼迦總主教，並參與起草 1351 年會議定案。此書系統反駁拉丁「和子說」與教宗首席權，主張聖父為三一中唯一根源，是拜占庭晚期反拉丁護教與三一神學的代表作，亦為佛羅倫斯合一會議前東方立場的權威表述。' },
          { title_zh: '教義全副武裝（教義甲冑）', title_orig: 'Πανοπλία Δογματική (Panoplia Dogmatica)', author: '尤西米烏斯‧齊加貝努斯（Euthymios Zigabenos）', era: '約 1110–1118', place: '拜占庭君士坦丁堡', language: '希臘文', intro: '修士齊加貝努斯奉皇帝阿萊克修斯一世之命所編的反異端百科鉅著，前七篇正面闡述神義論與基督論，其後二十一篇逐一駁斥自猶太教、亞美尼亞派、保羅派、彌賽亞派、波各米勒派以至穆斯林等各派異端。其論波各米勒派一節為今人研究該派的首要史料，書中並保存大量今已失傳的異端文獻與正統反駁，是拜占庭官方護教與異端學的集大成之作，傳世希臘抄本逾一百四十部，影響及於斯拉夫世界。', extent: '二十八篇' },
          { title_zh: '論聖靈之奧導（駁和子，聖靈由父發出論）', title_orig: 'Περὶ τῆς τοῦ ἁγίου Πνεύματος μυσταγωγίας (Mystagogia Spiritus Sancti)', author: '君士坦丁堡牧首佛提烏（Photius I）', era: '約 885–886', place: '君士坦丁堡', language: '希臘文', intro: '拜占庭反對「和子句」（Filioque）的奠基性論著，佛提烏針對拉丁教會在信經中增添「和子」，系統論證聖神僅由聖父發出（ἐκ μόνου τοῦ Πατρός）、而非由父「和子」共發。他廣引金口若望、大馬士革約翰等教父，以聖經、教父與邏輯三方面論證，奠定東方教會反和子論的標準框架。此書與其相關書信奠定東西方千年聖神論之爭的論題框架，是東西教會分裂前夕最重要的三一神學論戰文獻，影響後世帕拉瑪斯等拜占庭神學家。' },
          { title_zh: '群書摘記（書目集成‧萬卷書）', title_orig: 'Bibliotheca (Μυριόβιβλος)', author: '君士坦丁堡的佛提烏（Photius）', era: '約 845–858', place: '君士坦丁堡', language: '希臘文', intro: '佛提烏出使阿拉伯前後為其弟編纂的讀書摘要，評介所讀約二百八十部古典與基督教著作，涵蓋神學、護教、史學、哲學、醫學與小說，逐部撮述大意並評其文體優劣。許多今已散佚的教父與古典作品賴此書得存梗概，是拜占庭學術復興的標誌，兼具教義評斷與目錄學意義，亦為研究古代文獻流傳不可或缺的瑰寶。', extent: '二百八十部摘述' },
          { title_zh: '教座答辯文書（聖神由聖子永恆顯現論）', title_orig: 'Tomus fidei / De processione Spiritus Sancti（1285 年大公會議文書）', author: '塞浦路斯的格里高利二世（Gregorios II Kyprios，君士坦丁堡牧首）', era: '1285（君士坦丁堡會議）', place: '君士坦丁堡', language: '希臘文', intro: '塞浦路斯的格里高利二世為回應里昂合一（1274）後的和子論爭而作的聖神論文書，獲 1285 年君士坦丁堡會議認可。他提出聖神「由聖子永恆顯現」（aïdios ekphansis）之說，作為介於佛提烏式嚴格立場與拉丁和子論之間的正教方案，深刻影響後來帕拉瑪斯的本質—能量神學，是拜占庭晚期聖神論發展的重要環節。' },
          { title_zh: '為己改宗辯（護教書）', title_orig: 'Apologia (pro sua fide / pro conversione sua)', author: '德米特里‧基多尼斯（Dēmētrios Kydōnēs）', era: '約 1363–1365', place: '君士坦丁堡', language: '希臘文', intro: '拜占庭政治家兼神學家基多尼斯曾三任帝國首相（Mesazon），精通拉丁文並將阿奎那《神學大全》《駁異教大全》譯為希臘文。此《護教書》為其皈依天主教辯護，闡述他經由研讀拉丁經院神學而改變立場的歷程，並論教會合一與羅馬權威。它是拜占庭晚期「拉丁親善派」神學思潮的代表文獻，見證東西方思想在帝國末世的交會。' },
          { title_zh: '駁帕拉馬斯論著（阿金迪諾斯）', title_orig: 'Antirrhetic Treatises against Palamas', author: '格里高利‧阿金迪諾斯', era: '約 1342–1347', place: '君士坦丁堡', language: '希臘文', intro: '阿金迪諾斯原為帕拉馬斯友人，後成為靜修主義神學最堅決的反對者，撰多篇駁論抨擊帕拉馬斯「神性本質與能量實有區別」之說，主張此分將危及神的單一性、近乎多神。其論著保存了反靜修陣營的核心論點，是理解十四世紀靜修之爭兩造交鋒的必讀文獻；雖其立場於 1351 年公會議被定為謬誤，文本史料價值極高。', extent: '駁論多篇' },
          { title_zh: '駁拉丁人論聖神發出（佛羅倫斯辯論文集）', title_orig: 'Opera anti-Latina (De Spiritus Sancti processione)', author: '以弗所的馬可（馬爾谷‧歐根尼科斯）', era: '約 1438–1444（佛羅倫斯辯論主要在 1438–1439，相關駁論成於其後至 1444 年去世）', place: '佛羅倫斯／君士坦丁堡', language: '希臘文', intro: '以弗所總主教馬可是帕拉馬斯的門徒，於佛羅倫斯大公會議（1438–39）中力辯反對西方「和子（Filioque）」增訂與東西合一，是唯一拒簽合一決議的東方主教，後被東正教尊為信仰的捍衛者與聖人。其多篇論文逐點反駁拉丁方對聖神發出、煉獄與聖體餅的主張，重申聖神僅由父發出與本質／能量之分。這批著作是東方教會抗拒合一、捍衛正教傳統的綱領性文獻。', extent: '論文數篇' },
          { title_zh: '知識泉源（正統信仰詳解）', title_orig: 'Pēgē gnōseōs / Ekdosis akribēs tēs orthodoxou pisteōs', author: '大馬士革的約翰（Joannes Damascenus）', era: '約 743', place: '聖薩巴斯修道院（巴勒斯坦）', language: '希臘文', intro: '大馬士革約翰《知識泉源》三部曲（哲學篇、論異端、正統信仰詳解）是希臘教父神學的集大成總綱。第三部《正統信仰詳解》系統整理三一、道成肉身、聖像敬奉、聖事與末世諸信理，成為東方正教的標準教義手冊，並經拉丁譯本（Burgundio 譯）深刻影響倫巴與阿奎那的西方經院神學。其格言體與百科式編纂，是承先啟後、貫通東西的神學橋樑。', extent: '三部' }
        ]
      },
      {
        key: 'anti-islam-jewish',
        label: '反伊斯蘭／猶太護教部',
        label_en: 'Anti-Islamic and Anti-Jewish Apologetics',
        desc: '基督教面對伊斯蘭與猶太教挑戰所發展的論辯與護教文獻，從大馬士革約翰到中世紀晚期的傳教辯論。',
        works: [
          { title_zh: '論以實瑪利人異端', title_orig: 'De Haeresibus, c. 100（Peri haireseon）', author: '大馬士革約翰', era: '約 743', place: '聖薩巴斯修道院（巴勒斯坦）', language: '希臘文', intro: '此章是基督教對伊斯蘭最早的系統性論述之一，大馬士革約翰將伊斯蘭列為一種基督教異端（「以實瑪利人」或「撒拉森人」之異端），轉述穆罕默德的教導並逐點駁斥其對基督神性與三一的否認。作者生於伍麥亞王朝治下的大馬士革，曾任穆斯林政權官職，對伊斯蘭有第一手認識。此文奠定了拜占庭與後世西方反伊斯蘭護教的基本論點與框架。', link: '/fathers' },
          { title_zh: '基督徒與撒拉森人辯論', title_orig: 'Disputatio Christiani et Saraceni (Disputation Between a Christian and a Saracen)', author: '傳大馬士革的約翰（歸屬有爭議）', era: '約 8–9 世紀', place: '敘利亞／巴勒斯坦', language: '希臘文', intro: '以穆斯林問、基督徒答的短篇對話，圍繞善惡的成因、自由意志、基督作為上帝之道、聖母與受造界等問題展開，是拜占庭基督徒早期回應伊斯蘭神學詰問的代表文本。傳統收入大馬士革約翰著作，現代研究對確切作者仍有爭議；無論歸屬如何，它保存了八、九世紀基督教—伊斯蘭論辯的早期形態，應與《論以實瑪利人異端》並讀。' },
          { title_zh: '與撒拉森人對話', title_orig: 'Opuscula de haeresibus et synodis', author: '提阿多‧阿布‧庫拉', era: '約 800', place: '哈蘭（埃德薩近郊）', language: '希臘文／阿拉伯文', intro: '提阿多是迦克墩派的哈蘭主教，活躍於阿巴斯王朝治下，是最早以阿拉伯文寫作護教的基督徒之一。他承大馬士革約翰之緒，以對話與論辯體裁，運用伊斯蘭自身的詞彙與邏輯，向穆斯林與猶太人辯護三一、道成肉身與敬奉聖像之合理。其著作見證了東方基督徒在伊斯蘭環境中以本地語言為信仰申辯的努力，是早期跨宗教論辯的珍貴史料。', link: '/fathers' },
          { title_zh: '信仰之匕首', title_orig: 'Pugio Fidei adversus Mauros et Judaeos', author: '雷蒙‧馬丁', era: '約 1278', place: '加泰隆尼亞（道明會）', language: '拉丁文（夾希伯來文與阿拉伯文）', intro: '道明會士雷蒙‧馬丁精通希伯來文與阿拉伯文，此書廣引塔木德、米大示與拉比文獻，意在以猶太人自身的典籍證明基督信仰之真，是中世紀基督教反猶論辯最博學的著作。書中保存大量今已散佚的拉比文本，學術價值極高。其方法影響後世傳教辯論甚鉅，亦反映十三世紀道明會於伊比利半島向穆斯林與猶太人傳教的策略。', note: '書中部分拉比引文的真偽後世有爭議' },
          { title_zh: '大藝術（傳教辯論著作）', title_orig: 'Ars Magna / Llibre del gentil e dels tres savis', author: '拉蒙‧柳利', era: '約 1275–1305', place: '馬約卡／突尼斯', language: '加泰隆尼亞文／拉丁文／阿拉伯文', intro: '柳利是馬約卡的方濟在俗會士、哲學家與傳教士，發明「大藝術」——一套以基本概念組合推演真理的邏輯機械，盼藉理性的共同基礎說服穆斯林與猶太人歸信。其《異教徒與三智者之書》以一異教徒聽猶太、基督、穆斯林三賢辯道為框架，呈現三教對話。他多次親赴北非傳教，相傳最終殉道，是中世紀少見主張以理性對話而非武力傳教的先驅。', note: '一說殉道於布日伊' },
          { title_zh: '駁古蘭經', title_orig: 'Contra legem Sarracenorum / Reprobatio Alcorani', author: '里科爾多‧達‧蒙特克羅切', era: '約 1300', place: '佛羅倫斯／巴格達', language: '拉丁文', intro: '道明會士里科爾多曾長居巴格達傳教並研讀阿拉伯文古蘭經，此書逐點批駁古蘭經的內容、來源與一致性，是中世紀最具影響力的反伊斯蘭論著之一。其論點扎根於對伊斯蘭典籍的直接閱讀，較前人更為具體。此書後經希臘文與多種譯本流傳，馬丁‧路德晚年亦曾將其譯為德文，可見其論辯框架在宗教改革時代仍被援引。' }
        ,
          { title_zh: '論信仰的理據——駁撒拉森人、希臘人與亞美尼亞人（致安提阿詠經長）', title_orig: 'De rationibus fidei contra Saracenos, Graecos et Armenos ad Cantorem Antiochenum', author: '托馬斯‧阿奎那（Thomas Aquinas）', era: '約 1264', place: '義大利', language: '拉丁文', intro: '應安提阿詠經長之請而作的短篇護教書，回應東方基督徒在伊斯蘭環境中所遭的詰難：撒拉森人嘲笑三一與基督為神子之說，故前六章理性辯護三一、道成肉身、十字架與救贖；另設專章論聖體（駁亞美尼亞人）與煉獄（駁希臘人）。為阿奎那直接面對伊斯蘭挑戰的代表性護教文獻。' },
          { title_zh: '駁異端論天主教信仰', title_orig: 'De fide catholica contra haereticos', author: '里爾的阿蘭（亞蘭努斯）', era: '約 1185–1200', place: '法國南部／蒙佩利耶／巴黎', language: '拉丁文', intro: '被尊為「全能博士」的里爾的阿蘭以辯證之筆系統駁斥當時的異端，分四卷分別反駁卡特里派（純潔派／清潔派）、瓦勒度派、猶太人與穆斯林，是最早全面回應卡特里二元論、面對十二世紀末多元異議的綜合護教著作。他力圖以理性與權威並用為天主教信理辯護，回應南法蓬勃的異端風潮，反映異端裁判興起前以說理勸化為主的時代精神。與其《神學規則》同為早期經院系統神學的範例。', extent: '四卷' },
          { title_zh: '論信仰的和平', title_orig: 'De Pace Fidei', author: '庫薩的尼古拉（Nicolaus Cusanus）', era: '1453', place: '庫埃斯（神聖羅馬帝國）', language: '拉丁文', intro: '樞機尼古拉於君士坦丁堡陷落（1453）之年震動之餘所撰，以天上一場理想對話為框架：神前由十七位代表各民族與宗教者（含穆斯林、猶太人、印度人等）議論，最終發現眾教雖儀軌各異，卻同歸於「諸宗教中的一信（una religio in rituum varietate）」與獨一上帝。是中世紀少見以對話而非駁斥追求宗教合一的著作，展現庫薩「對立之巧合」哲學在宗教多元問題上的應用。', extent: '對話一篇' },
          { title_zh: '古蘭經之篩辨', title_orig: 'Cribratio Alkorani', author: '庫薩的尼古拉（Nicolaus Cusanus）', era: '約 1460–1461', place: '羅馬／義大利', language: '拉丁文', intro: '庫薩的尼古拉晚年（君士坦丁堡陷落後、應教宗庇護二世之請）研讀里科爾多與拉丁譯古蘭經後所撰的批判性著作，以「虔敬詮釋（pia interpretatio）」逐卷篩辨古蘭經，主張其中凡為真者皆暗合福音、凡背福音者皆出於訛傳或穆罕默德私意，意在引穆斯林由古蘭經自身導向基督真理。承《論信仰的和平》尋求共通基礎的精神，採較前人溫和的進路，是文藝復興前夕基督教伊斯蘭研究由純駁斥轉向理性詮釋的代表作。', extent: '三卷' },
          { title_zh: '論異端‧伊斯瑪儀人之異端（《知識之泉》第二部選卷）', title_orig: 'De haeresibus c. 100: Haeresis Ishmaelitarum', author: '大馬士革的聖若望（Joannes Damascenus）', era: '八世紀中葉（約 743–749）', place: '巴勒斯坦聖撒巴隱修院', language: '希臘文', intro: '出自大馬士革若望神學總綱《知識之泉》第二部《論異端》，將伊斯蘭列為第一百項異端「伊斯瑪儀人之異端」，是基督教世界第一篇針對伊斯蘭的護教與駁論文字。作者身處倭馬亞哈里發治下，對古蘭經與穆斯林論點知之甚詳，所立論題（三一、基督神性、偶像爭議）長為後世東西方護教之張本，是整個中世紀基督教—伊斯蘭交鋒論述的源頭。', extent: '選卷（《論異端》第100章）' },
          { title_zh: '駁古蘭經（古蘭經駁正）', title_orig: 'Ἀνατροπὴ τοῦ Κορανίου (Refutatio Corani) / Confutatio falsi libri', author: '拜占庭的尼基塔斯（Nicetas Byzantius）', era: '九世紀（約 855–870）', place: '君士坦丁堡', language: '希臘文', intro: '拜占庭「馬其頓文藝復興」時期最早大規模直接以古蘭經文本逐節駁斥伊斯蘭信仰的護教論著之一，首部系統引用《古蘭經》希臘譯文逐章批判其論神、論基督之說。尼基塔斯廣引、轉述並評議古蘭經段落，其文保存了八至九世紀古蘭經希臘文早期譯本（Coranus Graecus）的珍貴殘片，對其後拜占庭乃至西歐反伊斯蘭護教傳統影響深遠。' },
          { title_zh: '提摩太一世與哈里發馬赫迪辯道錄', title_orig: 'Apology of Timothy I before Caliph al-Mahdi', author: '東方教會大公牧首提摩太一世', era: '約 781（成書約 9 世紀初）', place: '巴格達', language: '敘利亞文', intro: '景教（東方亞述教會）牧首提摩太一世在巴格達阿拔斯朝廷與哈里發馬赫迪展開兩日辯論，從容答覆三一、基督神性、十字架、穆罕默德是否先知等詰問。其語氣謙和而立論堅實，以「尋珠者各執一隅」喻諸教，是現存最早、最具份量的基督徒—穆斯林對話文獻之一，反映東方教會在伊斯蘭治下的護教智慧。' },
          { title_zh: '造物主存在與真宗教論', title_orig: 'Maymar fī wujūd al-Khāliq wa-l-dīn al-qawīm', author: '哈蘭的狄奧多‧阿布‧古拉', era: '約八世紀末至九世紀初', place: '哈蘭（今土耳其東南）', language: '阿拉伯文', intro: '最早以阿拉伯文寫作的東方正統護教家阿布‧古拉之論著，借「自幼長於荒山者下山求道」的思想實驗，以理性比較諸宗教而論定基督宗教為真宗教，為阿拔斯時期基督教阿拉伯護教（kalām）之典範。' },
          { title_zh: '金迪辯教書信', title_orig: 'Risālat al-Kindī (Apology of al-Kindī)', author: '託名阿卜杜‧馬西‧伊本‧伊斯哈格‧金迪', era: '約九至十世紀', place: '阿拔斯哈里發朝（巴格達）', language: '阿拉伯文', intro: '以基督徒金迪答覆穆斯林哈希米書信之形式寫成的長篇護教論辯，駁斥伊斯蘭對三一與道成肉身的指責、為聖經之可信辯護並批評古蘭經。後經可敬者彼得院長團隊譯為拉丁文，深刻影響拉丁西方對伊斯蘭的認識。' },
          { title_zh: '致一位穆斯林友人書', title_orig: 'Risāla ilā aḥad al-muslimīn', author: '安提阿的保羅（西頓主教保羅）', era: '約 1140–1200', place: '西頓', language: '阿拉伯文', intro: '默基特派西頓主教保羅以阿拉伯文寫給一位穆斯林友人，溫和陳述拜占庭學者對穆罕默德與伊斯蘭的看法。其論辯風格平和，甚至引古蘭經文句反證基督教真理，主張古蘭並非為基督徒而降。此書是基督教—伊斯蘭護教文獻中罕見的和緩之作，流傳廣泛，後引發伊本‧泰米葉等穆斯林學者的鄭重駁斥。' },
          { title_zh: '駁穆罕默德四辯護辭與四講辭', title_orig: 'Apologiae et Orationes contra Mahometem', author: '約翰六世‧坎塔庫澤努斯', era: '約 1370', place: '君士坦丁堡（退隱為修士後）', language: '希臘文', intro: '退位為修士的拜占庭皇帝坎塔庫澤努斯所撰四篇護教辭與四篇駁斥辭，主要取材於基多尼斯所譯里科爾多之作，系統批駁伊斯蘭教義、為基督宗教三一與救贖辯護，為帕拉約洛格王朝晚期反伊斯蘭神學要籍。' },
          { title_zh: '駁撒拉森派系或異端之書', title_orig: 'Liber contra sectam sive haeresim Saracenorum', author: '可敬者彼得（Petrus Venerabilis，克呂尼隱修院院長）', era: '約 1143–1156', place: '勃艮第克呂尼隱修院（Cluny）', language: '拉丁文', intro: '克呂尼隱修院長可敬者彼得在主持拉丁世界首部古蘭經譯本（《托雷多文集》Collectio Toletana，1142–43）後，據新譯材料親撰的反伊斯蘭論戰主著，一反武力進路，主張以理性與文本向穆斯林申辯，逐點駁斥伊斯蘭對基督神性與聖經的否認。與其《撒拉森全部異端綱要》合為「克呂尼文集」，開拉丁西方以文本研究為基礎之反伊斯蘭論辯先河，影響達四世紀之久。', extent: '二卷（附序信）' },
          { title_zh: '撒拉森人全部異端綱要', title_orig: 'Summa totius haeresis Saracenorum', author: '可敬者彼得（Petrus Venerabilis，克呂尼院長）', era: '約 1142–1143', place: '西班牙／克呂尼修道院', language: '拉丁文', intro: '克呂尼隱修院長可敬者彼得訪西班牙期間，委託肯頓的羅伯特完成首部古蘭經拉丁譯本，並親撰此綱要向拉丁基督徒「啟蒙」伊斯蘭。他將伊斯蘭定位為一種基督教異端而非獨立宗教，概述其源流與教義謬誤，與其《駁撒拉森派》合為「克呂尼文集」，開拉丁西方以文本研究為基礎之反伊斯蘭論辯先河。' },
          { title_zh: '駁撒拉森人之律（古蘭經駁斥）', title_orig: 'Contra legem Sarracenorum (Confutatio Alcorani)', author: '蒙特克羅切的里科爾多（Riccoldo da Monte di Croce）', era: '約 1300–1301', place: '巴格達／佛羅倫斯', language: '拉丁文', intro: '道明會傳教士里科爾多曾長居巴格達習阿拉伯文、研讀古蘭經原典，歸後撰此書逐項論證古蘭經非神聖默示，從《古蘭經》自身文本與聖經、理性的矛盾駁其神聖性，並評穆罕默德其人，論證之精細遠超前人。中世紀流傳最廣、影響最深，1500 年於塞維利亞首刊（題《駁古蘭》），經希臘文（Demetrios Kydones 譯）與斯拉夫文轉譯，馬丁路德 1542 年譯為德文，左右西方對伊斯蘭的認知達數世紀。' },
          { title_zh: '論穆罕默德教派', title_orig: 'De seta Machometi / Explanatio symboli apostolorum', author: '雷蒙‧馬丁（Ramon Martí）', era: '約 1257', place: '加泰隆尼亞（道明會）', language: '拉丁文（引阿拉伯文）', intro: '道明會士雷蒙‧馬丁早於其名著《信仰之匕首》的反伊斯蘭專論，運用阿拉伯文獻（或引阿拉伯文的拉丁來源）逐點駁斥伊斯蘭教義與穆罕默德的先知地位。馬丁是十三世紀道明會於伊比利向穆斯林與猶太人傳教的學術核心人物，此書反映其以對手典籍為據的論辯方法，是中世紀反伊斯蘭護教的重要一環。' },
          { title_zh: '駁猶太人對話錄', title_orig: 'Dialogi contra Iudaeos', author: '佩特魯斯‧阿方西', era: '約 1108–1110', place: '亞拉岡（西班牙）', language: '拉丁文', intro: '作者原為西班牙猶太拉比摩西‧塞法迪，1106 年受洗改宗取名佩特魯斯‧阿方西，此書以皈依前的自己「摩西」與皈依後的「彼得」對話為框架，逐節駁斥猶太教並兼及伊斯蘭，論證基督信仰之真。因作者通曉希伯來文與阿拉伯文及拉比文獻，書中援引塔木德等內部典籍之深廣前所未見，被譽為拉丁中世紀最重要的反猶論著，深刻形塑後世基督教對猶太教的論辯方法。', extent: '十二篇對話' },
              { title_zh: '論聖像敬禮', title_orig: 'Treatise on the Veneration of the Holy Icons', author: '哈蘭的狄奧多若‧阿布‧古拉（Theodore Abū Qurrah）', era: '約 9 世紀初', place: '哈蘭／埃德薩（默基特派）', language: '阿拉伯文', intro: '默基特派哈蘭主教阿布‧古拉是已知最早以阿拉伯文寫作的基督教神學家。本論為回應伊斯蘭與猶太教對「拜偶像」的指控、並勸勉因之卻步的基督徒而作，從神學與聖經論證敬禮聖像之正當，區分敬禮與崇拜。其著作見證八、九世紀東方基督徒在伊斯蘭環境中以對方語言進行的護教與對話，是阿拉伯基督教神學的開端。' },
        ]
      },
      {
        key: 'mystical',
        label: '密契神學部',
        label_en: 'Mystical Theology',
        desc: '追求心靈與上帝直接合一的靈修密契傳統，從熙篤會到萊茵河與英格蘭的神祕主義。',
        works: [
          { title_zh: '論愛上帝', title_orig: 'De diligendo Deo', author: '明谷的伯爾納鐸', era: '約 1126', place: '明谷修道院（熙篤會）', language: '拉丁文', intro: '伯爾納鐸是熙篤會改革的靈魂人物與十二世紀最具影響力的神學家。此書論人當如何並為何愛上帝，描繪愛的四個階段：由為己而愛己、為己而愛神、為神而愛神，終至為神而愛己的忘我境界。全書文辭優美、情感熾烈，將神學思辨與靈修體驗熔於一爐，是西方靈修神學的經典，深刻影響後世熙篤會與整個拉丁密契傳統。', link: '/fathers' },
          { title_zh: '德意志講道集', title_orig: 'Predigten / Deutsche Werke', author: '埃克哈特大師', era: '約 1300–1327', place: '科隆／埃爾福特／巴黎', language: '中古高地德語／拉丁文', intro: '道明會士埃克哈特以德語向修女與在俗信眾講道，闡發靈魂深處的「靈光（Seelenfünklein）」、神性的「無底深淵」與靈魂中「上帝之誕生」等密契主題，主張人當捨離一切、空乏自我以與神性合一。其大膽思辨與否定神學的語言招致異端指控，部分命題於 1329 年被定罪，然其影響深遠，啟發陶勒、蘇索及萊茵—弗蘭德密契學派，並激盪近代哲學與靈修。', link: '/fathers' },
          { title_zh: '不知之雲', title_orig: 'The Cloud of Unknowing', author: '佚名（英格蘭密契作者）', era: '約 1375', place: '英格蘭東米德蘭', language: '中古英語', intro: '此書以靈修導師致弟子書信的口吻寫成，教導默觀者放下一切思辨與形象，立於「不知之雲」中，唯以赤裸的愛之意向「叩擊」隱於「遺忘之雲」後的上帝。其進路深受偽狄奧尼修斯否定神學影響，主張上帝不可由理智企及，唯能由愛觸及。全書文字樸實親切，是英格蘭中世紀密契文學的瑰寶，至今仍為默觀祈禱的經典指南。' },
          { title_zh: '神聖之愛的啟示', title_orig: 'Revelations of Divine Love', author: '諾里奇的朱利安', era: '約 1393', place: '諾里奇（英格蘭）', language: '中古英語', intro: '朱利安是英格蘭的隱修女，於重病中得見基督受難的十六次「異象」，事後長年默想其義而成此書，是已知最早以英文寫作的女性著作。她以「一切都將安好（all shall be well）」的盼望、上帝如母親般的慈愛、以及「萬物如榛果般微小卻被上帝懷抱」等意象，闡發神聖之愛超越罪與苦的奧祕。其溫柔而深邃的神學，使之成為英語靈修傳統中歷久彌新的聲音。' },
          { title_zh: '效法基督', title_orig: 'De Imitatione Christi', author: '托馬斯‧厄‧肯培（金碧斯）', era: '約 1418–1427', place: '低地國（共同生活弟兄會）', language: '拉丁文', intro: '此書出自「新虔敬（Devotio Moderna）」運動，以簡樸親切的格言勸人輕看世俗、效法基督的謙卑與十架，並親近聖體聖事。全書分四卷，論靈修生活、內在修養、內在安慰與領聖體，文字平易卻深契人心。自問世以來譯本與印行數量僅次於聖經，跨越宗派界線，影響無數信徒，是西方基督教靈修文學流傳最廣、最受愛戴的經典。' }
        ,
          { title_zh: '論教會聖統制與天階體系註（偽狄奧尼修斯著作評註）', title_orig: 'Expositiones in Ierarchiam coelestem', author: '厄里根那（Johannes Scotus Eriugena）', era: '約 865–870（譯本 c. 860–862，評註本身稍晚）', place: '西法蘭克王國', language: '拉丁文', intro: '厄里根那將偽狄奧尼修斯《天階體系》譯為拉丁文並作評註，把東方否定神學（apophatic）與天使等級論引入拉丁西方，成為中世紀神祕神學的重要源頭。其譯注影響聖維克多學派、波那文都拉乃至埃克哈特一系的默觀傳統。' },
          { title_zh: '教理講話（要理講論）', title_orig: 'Κατηχήσεις (Catecheses)', author: '新神學家西默盎（敘默盎）', era: '約 949–1022', place: '君士坦丁堡聖瑪瑪斯修道院', language: '希臘文', intro: '新神學家西默盎為其修士在晨禱（Matins）時所講的系列訓誨（Catecheses），是其畢生核心著作之一。他大膽宣講人能在今生親身體驗聖靈之光與神化（theosis），強調有意識的聖神經驗而非僅形式聖禮，為日後靜修派（hesychasm）奠定先聲，是拜占庭密契傳統承先啟後的關鍵人物。' },
          { title_zh: '論默想（致教宗書）', title_orig: 'De Consideratione', author: '明谷的伯爾納鐸（Bernardus Claraevallensis）', era: '約 1148–1153', place: '明谷修道院（熙篤會，Clairvaux）', language: '拉丁文', intro: '伯爾納鐸晚年寫給其門生、教宗恩仁三世的五卷勸誡書，借「默想／省思（consideratio）」之鏡勸這位繁忙的教宗於治理教會之餘，務必保留自省與默觀上帝的時間，否則靈魂將枯竭。書中既論教宗職權的本質與界限（屬靈與屬世兩刃之說）、教會治理之弊，又上升至對上帝的默觀。全書兼具靈修勸勉、教會論與政治神學，是中世紀論教宗職分最深刻的著作之一，亦為「君鑒」體裁與教會改革思想的名篇。', extent: '五卷' },
          { title_zh: '論謙卑與驕傲的階梯', title_orig: 'De Gradibus Humilitatis et Superbiae', author: '明谷的伯爾納鐸', era: '約 1120（學界多繫於 1119–1124）', place: '明谷熙篤會院', language: '拉丁文', intro: '伯爾納鐸首部著作，敷陳《聖本篤會規》論謙卑之教導，詳列謙卑十二級與相對之驕傲十二級，為熙篤靈修與修道倫理奠基之作。' },
          { title_zh: '慈愛之鏡（論愛德）', title_orig: 'Speculum Caritatis', author: '里沃的艾爾雷德（Aelredus Rievallensis）', era: '約 1142–1143', place: '英格蘭里沃修道院（熙篤會）', language: '拉丁文', intro: '熙篤會院長艾爾雷德應明谷的伯爾納鐸之請而作的首部靈修論著，分三卷論愛德（caritas）為修道生活的根本。他剖析愛的本質、秩序與失序，主張一切德行皆以愛上帝為歸宿，並以細膩的心理洞察描繪靈魂在愛中的安息與紛擾。此書文辭優美、情理交融，與其《論屬靈友誼》並為英格蘭熙篤靈修的代表，深刻影響中世紀的愛德神學。', extent: '三卷' },
          { title_zh: '黃金書信（致蒙迪厄弟兄書）', title_orig: 'Epistola ad fratres de Monte Dei (Epistola aurea)', author: '聖蒂埃里的威廉（Guillelmus de Sancto Theodorico）', era: '約 1144–1145', place: '西尼修道院（熙篤會，法國北部）', language: '拉丁文', intro: '聖蒂埃里的威廉致蒙迪厄山加爾都西會弟兄的靈修長信，描繪靈魂由「動物人—理性人—屬靈人」三階段上升至與上帝合一之愛的圓滿，闡發人按神的形像受造、藉聖靈而與三一相通的密契神學。其神學深受希臘教父影響，將東方神化思想引入拉丁靈修。全書因辭采與深度被譽為「黃金書信」，中世紀一度誤歸於伯爾納鐸名下，是十二世紀熙篤密契神學的高峰之作。' },
          { title_zh: '愛之烈火（愛火）', title_orig: 'Incendium Amoris (The Fire of Love)', author: '哈姆波爾的理查‧羅爾（Richardus Rolle de Hampole）', era: '約 1343', place: '英格蘭約克郡（隱修）', language: '拉丁文', intro: '英格蘭最早、最受歡迎的隱修密契作家理查‧羅爾的名著，以第一人稱熱烈見證其默觀中親身體驗的「熾熱（calor）」、「甘甜（dulcor）」與「歌詠（canor）」三重屬靈感受，主張對基督熾熱之愛使靈魂如被烈火焚燒而生屬天的喜樂，並力主獨居默觀生活的優越。文字熱情奔放、富感官意象，廣為傳抄並引發後世（如希爾頓）對其情感主義的審慎回應，與《不知之雲》《神聖之愛的啟示》並為十四世紀英格蘭密契文學的代表。' },
          { title_zh: '成全之梯（完全之階梯）', title_orig: 'The Scale of Perfection (Scala Perfectionis)', author: '沃爾特‧希爾頓（Walter Hilton）', era: '約 1380–1396', place: '英格蘭索羅頓（奧斯定會修道院）', language: '中古英語', intro: '奧斯定詠禮會士希爾頓以英文寫給一位隱修女的靈修指南，分兩卷循序教導默觀生活：由改造罪人受損的「上帝形像」、潔淨罪垢，經黑暗與虛己，至重新成形於耶穌、在恩寵中與祂以愛與光契合。其文穩健平實、心理觀察細膩，避開過度激越的密契語言，調和行動與默觀、信德與經驗。是中世紀英格蘭密契文學與《不知之雲》《神聖之愛的啟示》並列的瑰寶，影響後世英語靈修甚深。', extent: '二卷' },
          { title_zh: '神性的流光（神性流溢之光）', title_orig: 'Das fließende Licht der Gottheit (The Flowing Light of the Godhead)', author: '馬格德堡的梅希蒂爾德（Mechthild von Magdeburg）', era: '約 1250–1282', place: '馬格德堡／黑爾夫塔修道院（德意志）', language: '中古低地德語', intro: '貝居因會修女梅希蒂爾德記述其與上帝相愛的神祕經驗，融異象、對話、禱詞、聖歌、抒情情詩、書信與寓言於一書，以新郎新婦之愛喻靈魂與神的結合。是最早以德語方言（而非拉丁文）獨立寫成的重要密契著作之一，開創「新娘神祕主義」的女性靈修傳統，影響艾克哈特等萊茵密契學派與後世德語靈修文學。' },
          { title_zh: '靈性婚配（靈性的婚配）', title_orig: 'Die geestelike brulocht (The Spiritual Espousals)', author: '揚‧範‧呂斯布魯克（John Ruusbroec）', era: '約 1335–1340', place: '布魯塞爾／格倫達爾', language: '中古荷蘭文', intro: '被尊為「可敬博士」的呂斯布魯克以福音「新郎來了，你們出來迎接他」為綱，論靈修生活由「行動—內在—默觀」三重層次上升，終達與三一上帝合一而又不失位格之別。被譽為其代表作與低地國家密契傳統的巔峰，思想深邃而結構嚴整，精微的密契心理分析與三一神學基礎深刻影響「新虔敬運動（Devotio Moderna）」、十字若望與後世萊茵—弗拉芒靈修。', extent: '三部' },
          { title_zh: '永恆智慧之書（智慧時計）', title_orig: 'Büchlein der ewigen Weisheit / Horologium Sapientiae', author: '亨利‧蘇索（Heinrich Seuse / Henricus Suso）', era: '約 1328–1334', place: '康斯坦茨／烏爾姆（道明會，德意志）', language: '中古高地德語／拉丁文', intro: '道明會士、艾克哈特門人蘇索的靈修名著，以靈魂與化身為「永恆智慧」（即基督）的對話展開，引領讀者默想基督苦難、捨離自我、預備善終而臻於與神合一。相較艾克哈特抽象的思辨，蘇索更重情感與基督受難的具體默想，文字溫柔而富詩意。其拉丁文增訂本《智慧時計》風行全歐，為中世紀晚期傳抄最廣的靈修書之一，是「萊茵蘭三大師」中最富情感者。' },
          { title_zh: '陶勒講道集', title_orig: 'Predigten (Sermons of Johannes Tauler)', author: '約翰‧陶勒（Johannes Tauler）', era: '約 1330–1361', place: '史特拉斯堡／科隆（道明會，萊茵河區）', language: '中古高地德語', intro: '道明會士、艾克哈特門人、萊茵密契學派核心人物陶勒的德語講道集，面向修女與在俗信眾，闡發靈魂深處的「根基（Grund）」與上帝相遇、捨棄自我以順服神意、在日常生活中實踐密契合一。相較艾克哈特，陶勒更務實、節制而重靈修牧養，避開異端指控。其平易懇切的牧養語調使密契神學落實於日常虔敬，深刻影響「上帝之友」運動與馬丁路德（路德親自注釋出版），是德意志密契傳統承先啟後的關鍵。' },
          { title_zh: '三部之工（三部曲鉅著／Opus tripartitum）', title_orig: 'Opus tripartitum', author: '邁斯特‧艾克哈特', era: '約 1305 起（未竟）', place: '巴黎／史特拉斯堡／科隆', language: '拉丁文', intro: '艾克哈特規劃中的拉丁神學鉅著，原擬三部：命題之工（逾千條神學命題）、問題之工與闡釋之工（聖經逐卷註疏），惜大半未成。今存《創世記註》《出谷紀註》《若望福音註》等，闡發「存有即上帝」「靈魂火花」「神性的虛空」等密契思想。其思辨將新柏拉圖主義推至極致，雖部分命題後遭判責，仍為萊茵蘭密契神學的源頭。', extent: '三部（多未竟）' },
          { title_zh: '異象集（哈德維希）', title_orig: 'Visioenen / Brieven (Hadewijch)', author: '哈德維希（安特衛普的哈德維希）', era: '約 1240', place: '布拉班特（低地國）', language: '中古荷蘭文', intro: '哈德維希是十三世紀貝居安（beguine）運動的密契女作家，以中古荷蘭文寫成異象集、書信與詩歌，以宮廷愛（minne）的語彙描繪靈魂對上帝之愛的渴慕、苦難與合一。其神學深邃、文學成就極高，將世俗愛情詩的修辭轉化為與神相愛的密契表達，是荷語文學與女性密契傳統的奠基者，並深刻影響其後的呂斯布魯克。', extent: '異象、書信與詩歌合集' },
          { title_zh: '德意志神學', title_orig: 'Theologia Germanica (Theologia Deutsch)', author: '佚名（法蘭克福一日耳曼騎士團司鐸）', era: '約十四世紀晚期', place: '法蘭克福', language: '中古高地德語', intro: '萊茵蘭神祕主義傳統的匿名論著，承艾克哈特、陶勒之緒，論捨棄自我意志、與上帝合一而臻於「完全生命」。馬丁路德於 1516、1518 年兩度刊行，視為其神學先聲，影響深遠。' },
          { title_zh: '對話錄（天主上智之書）', title_orig: 'Il Dialogo della Divina Provvidenza', author: '西恩納的加大利納（錫耶納的加大利納）', era: '約 1377–1378', place: '義大利西恩納（錫耶納）', language: '中古義大利文（托斯卡尼方言）', intro: '道明會第三會的女密契家加大利納於神魂超拔中口述、由祕書筆錄成書的靈修鉅著，以她的靈魂向天父祈求、天父逐一垂答的對話展開，論真理之橋（基督）、眼淚與識辨、自我認識、天命、教會改革與祈禱諸題。全書以強烈的個人體驗承載深厚的神學，呼籲教會與信徒回歸聖德，被譽為基督教神祕主義散文中的《神曲》。加大利納後被立為教會聖師，本書是中世紀女性神學書寫的高峰，亦是義大利語靈修文學的奠基之作。' }
        ]
      },
      {
        key: 'syriac-eastern',
        label: '敘利亞與東方教會神學部',
        label_en: 'Syriac and Eastern Church Theology',
        desc: '迦克墩會議後與拜占庭分流的敘利亞正教（合性論）與東方教會（聶斯托留傳統）系統神學，於伊斯蘭治下匯通希臘教父、亞里斯多德與阿拉伯哲學。',
        works: [
          { title_zh: '聖所明燈（神學大全）', title_orig: 'Mnārath qudšē / Candelabrum Sanctuarii', author: '巴爾‧赫布雷烏斯', era: '約 1267', place: '美索不達米亞（敘利亞正教）', language: '敘利亞文', intro: '敘利亞正教大主教巴爾‧赫布雷烏斯被譽為中世紀敘利亞學界最博通者。此《聖所明燈》分十二「基礎」系統論知識、宇宙、神學、道成肉身、天使、教會與末世，匯通希臘教父、亞里斯多德與阿拉伯哲學，是敘利亞「文藝復興」最完整的神學大全。其與《光輝之書》（教義摘要）並為東方教會系統神學的高峰。', extent: '十二基礎' },
          { title_zh: '光輝之書（教義摘要）', title_orig: 'Kethabha dhe-Zalge / Book of Rays', author: '巴爾‧赫布雷烏斯', era: '約 1270–1280', place: '美索不達米亞（敘利亞正教）', language: '敘利亞文', intro: '巴爾‧赫布雷烏斯（敘利亞正教瑪弗里安）為其神學大全《聖所明燈》（Menarath Qudhshe）所作的精簡本，名為《光輝之書》（Kethabha dhe-Zalge），分若干「光輝（zalge）」綱目，扼要陳述創造、道成肉身、天使論、教會論、聖事論、末世論等信理，廣引教父。與《明燈》互為詳略，是中世紀敘利亞正教（合性論）系統神學的代表性綱要。原典迄未刊行，僅存於巴黎、柏林、倫敦、牛津、羅馬等地之敘利亞文抄本。' },
          { title_zh: '精粹之珠', title_orig: 'Ad-Durr ath-Thamīn fī Īḍāḥ ad-Dīn (The Precious Pearl)', author: '塞維魯‧伊本‧穆卡法（Sāwīrus ibn al-Muqaffaʿ）', era: '10 世紀', place: '埃及（科普特正教）', language: '阿拉伯文', intro: '科普特正教阿什穆奈因主教塞維魯‧伊本‧穆卡法以阿拉伯文撰寫的系統神學總綱，闡述三位一體、道成肉身、聖事、末世等教義，並回應伊斯蘭與其他教派的質難。作為最早以阿拉伯文系統陳述科普特正教信仰的著作之一，它兼具教理問答與護教功能，是了解伊斯蘭治下科普特教會如何以阿拉伯語保存並辯護其信仰的關鍵神學文獻。' },
          { title_zh: '智識之燈', title_orig: 'Kitāb Miṣbāḥ al-ʿAql (The Lamp of the Intellect)', author: '塞維魯‧伊本‧穆卡法', era: '10 世紀', place: '埃及阿什穆奈因', language: '阿拉伯文', intro: '科普特主教塞維魯以阿拉伯文撰成的神學論著，從理性、受造秩序與啟示的關係說明基督信仰，並在伊斯蘭思想居主流的語境中為三一與道成肉身辯護。它與《精粹之珠》相互補充，見證科普特神學由科普特語轉入阿拉伯語後，如何吸收論辯術語而保持自身教義傳統。' },
        ]
      }
    ]
  },
  wai: {
      "summary": "與中世紀基督教並立交鋒的他宗教哲學與神學。伊斯蘭以法爾薩法（希臘哲學的承繼）、凱拉姆（辯證神學）、蘇菲形上學與什葉／伊斯瑪儀神學構成龐大思想體系，安薩里《宗教學的復興》四十卷尤為靈修神學巨帙；猶太自薩阿底亞至阿爾博建立理性神學傳統；伊斯蘭與猶太學者亦留下駁斥基督宗教的護教論著。並收基督教內部的異端與前改教論述。",
      "divisions": [
        {
          "key": "falsafa",
          "label": "伊斯蘭哲學部（法爾薩法）",
          "label_en": "Islamic Philosophy (Falsafa)",
          "desc": "希臘哲學傳統在伊斯蘭世界的承繼與轉化——金迪至伊本魯世德的形上學、政治哲學與靈魂論。",
          "works": [
            {
              "title_zh": "第一哲學",
              "title_orig": "Fī al-Falsafa al-Ūlā",
              "author": "金迪（al-Kindī, Abū Yūsuf Yaʻqūb ibn Isḥāq）",
              "era": "約830年代",
              "place": "巴格達（阿拔斯朝智慧宮）",
              "language": "阿拉伯文",
              "intro": "「阿拉伯人的哲學家」金迪的形上學代表作，首度以希臘哲學語彙論證真一的獨一與世界受造。他調和新柏拉圖與亞里斯多德傳統，主張哲學與啟示同源不悖，開伊斯蘭理性神學先河。此書亦透過拉丁譯本影響中世紀西歐，是falsafa運動的奠基文獻。"
            },
            {
              "title_zh": "德性之城",
              "title_orig": "Mabādiʼ Ārāʼ Ahl al-Madīna al-Fāḍila",
              "author": "法拉比（al-Fārābī, Abū Naṣr）",
              "era": "約940年代",
              "place": "巴格達／大馬士革",
              "language": "阿拉伯文",
              "intro": "「第二導師」法拉比的政治哲學名著，融柏拉圖《理想國》與伊斯蘭先知論，描繪由哲人先知領導、諸能力如身體器官般協作的德性之城，並列舉無知之城、墮落之城等對照。奠定伊斯蘭政治形上學典範，深刻影響伊本西那與邁蒙尼德。"
            },
            {
              "title_zh": "政治體制",
              "title_orig": "Kitāb al-Siyāsa al-Madaniyya",
              "author": "法拉比（al-Fārābī, Abū Naṣr）",
              "era": "約940年代",
              "place": "巴格達",
              "language": "阿拉伯文",
              "intro": "法拉比另一部政治哲學要籍，又名《存在諸原理》。自第一因流溢的宇宙秩序談起，遞降至天體、質料與人的社群，論證理想政體須以理性與啟示合一的元首統攝。與《德性之城》互補，為中世紀伊斯蘭與猶太政治思想提供形上根據。"
            },
            {
              "title_zh": "法拉比論著集",
              "title_orig": "Rasāʾil al-Fārābī",
              "author": "法拉比（al-Fārābī, Abū Naṣr）",
              "era": "公元十世紀",
              "place": "巴格達",
              "language": "阿拉伯文",
              "extent": "多篇短論合輯（含《論理智》《智慧珠璣》《問題精粹》等）",
              "intro": "法拉比短篇哲學論著結集，涵蓋知識論、宇宙生成、邏輯與形上學。其「主動理智」與流溢階層說經阿拉伯—拉丁譯介，成為中世紀論靈魂與啟示之共同語彙，猶太與基督教士林哲學多所援引，是研究早期伊斯蘭哲學不可或缺的一手文獻。"
            },
            {
              "title_zh": "指示與提醒",
              "title_orig": "al-Ishārāt wa-al-Tanbīhāt",
              "author": "伊本西那（Ibn Sīnā / Avicenna）",
              "era": "約1030年",
              "place": "伊斯法罕／哈馬丹",
              "language": "阿拉伯文",
              "intro": "伊本西那晚年的哲學總綱，以簡練「指示」與「提醒」凝縮邏輯、物理、形上與神秘知識，末篇論蘇菲的靈知階位尤負盛名。全書開放式行文引後世註疏蜂起（圖西、拉齊皆有註），成為伊斯蘭東方學派最核心的教學文本之一。"
            },
            {
              "title_zh": "救贖之書",
              "title_orig": "Kitāb al-Najāt（The Book of Salvation）",
              "author": "伊本西那（Ibn Sīnā / Avicenna）",
              "era": "約1027年",
              "place": "波斯",
              "language": "阿拉伯文（存中世紀希伯來譯本）",
              "intro": "伊本西那自其巨著《治療論》摘要精編的哲學綱要，涵蓋邏輯、自然哲學、數學與形上學，旨在闡明使靈魂得救、脫離無知的知識體系。書中靈魂論（含著名的「飛人」論證）經希伯來文轉譯後流入中世紀猶太哲學，影響深遠。"
            },
            {
              "title_zh": "哈義‧本‧葉格贊",
              "title_orig": "Risālat Ḥayy ibn Yaqẓān",
              "author": "伊本圖菲勒（Ibn Ṭufayl, Abū Bakr）",
              "era": "約1160年代",
              "place": "安達魯斯（格拉納達／馬拉喀什）",
              "language": "阿拉伯文",
              "intro": "史上首部哲理小說：孤島自生的哈義憑理性獨力攀升，由觀察自然到體證真一，最終印證哲學與啟示殊途同歸。伊本圖菲勒藉此調和falsafa與蘇菲神秘主義，質疑律法宗教的字面外殼。經拉丁與英譯（如《自學的哲學家》）廣傳，影響近代歐洲啟蒙。"
            },
            {
              "title_zh": "照明哲學",
              "title_orig": "Ḥikmat al-Ishrāq",
              "author": "蘇赫拉瓦爾迪（Shihāb al-Dīn al-Suhrawardī）",
              "era": "約1186年",
              "place": "阿勒頗",
              "language": "阿拉伯文",
              "intro": "照明學派創始經典，以「光」的等級取代亞里斯多德的形質論，建構由眾光之光層層流溢的存有秩序，融古波斯智慧、柏拉圖理型與蘇菲直觀。作者被稱「殉道的謝赫」，此書成為後世伊朗學派（如穆拉‧薩德拉）的活水源頭。"
            },
            {
              "title_zh": "決疑論",
              "title_orig": "Faṣl al-Maqāl fīmā bayna al-Ḥikma wa-al-Sharīʿa min al-Ittiṣāl",
              "author": "伊本魯世德（Ibn Rushd / Averroes）",
              "era": "約1180年",
              "place": "科爾多瓦（安達魯斯）",
              "language": "阿拉伯文",
              "intro": "伊本魯世德的法學—哲學宣言，以馬立克派法理論證：哲學思辨不僅合乎教法、對有能力者甚屬義務。他區分大眾、辯證者與明證者三種理解層次，主張啟示與哲學真理不相牴觸，為理性思辨在伊斯蘭中的正當性辯護，深刻影響拉丁阿威羅伊主義。"
            },
            {
              "title_zh": "孤獨者的治理",
              "title_orig": "Tadbīr al-Mutawaḥḥid",
              "author": "伊本巴哲（Ibn Bājja / Avempace）",
              "era": "約 12 世紀初（作者卒 1138）",
              "place": "安達魯斯薩拉戈薩‧非斯",
              "language": "阿拉伯文",
              "intro": "安達魯斯哲學家伊本巴哲的代表作，論在不完善的城邦中，追求真理的哲人如何以「孤獨者」之姿自我治理、憑理性上升與主動理智結合。它把法拉比的德性之城理想轉為個人靈性自足的方案，直接啟發伊本圖菲勒《哈義‧本‧葉格贊》與伊本魯世德。"
            },
            {
              "title_zh": "治療論（形上學）",
              "title_orig": "Kitab al-Shifa / Al-Ilahiyyat",
              "author": "伊本‧西那（阿維森納）",
              "era": "約 1020",
              "place": "波斯（哈馬丹／伊斯法罕）",
              "language": "阿拉伯文",
              "intro": "阿維森納是中世紀伊斯蘭最偉大的哲學家與醫學家，《治療論》是其哲學百科全書，《形上學》卷融會亞里斯多德與新柏拉圖主義，提出「本質與存在之區分」、「必然存有與可能存有」的著名論證，由「必然存有者」推證唯一真主。其思想經拉丁譯本傳入西方，深刻影響大阿爾伯特、阿奎那與董思高的形上學，是溝通希臘、伊斯蘭與基督教三大思想傳統的樞紐。"
            },
            {
              "title_zh": "哲學家的不一致",
              "title_orig": "Tahafut al-Falasifa",
              "author": "安薩里",
              "era": "約 1095",
              "place": "巴格達／圖斯（波斯）",
              "language": "阿拉伯文",
              "intro": "安薩里是伊斯蘭最具影響力的神學家與蘇菲導師，此書批判阿維森納、法拉比等哲學家在二十個論題上背離正統信仰，尤其駁斥「世界永恆」、「真主不知個別事物」與「無肉身復活」三說，斥之為悖逆教義。他主張因果關係非必然而出於真主直接意志，動搖了亞里斯多德式的自然哲學。此書扭轉了伊斯蘭思想的走向，使神學重新凌駕於希臘哲學之上。"
            },
            {
              "title_zh": "不一致的不一致",
              "title_orig": "Tahafut al-Tahafut",
              "author": "伊本‧魯世德（阿維羅伊）",
              "era": "約 1180",
              "place": "安達盧斯（哥多華）",
              "language": "阿拉伯文",
              "intro": "阿維羅伊為回應安薩里《哲學家的不一致》對哲學的攻擊而作此書，逐點為亞里斯多德哲學辯護，主張哲學與啟示殊途同歸、各有其真理層次。他是亞里斯多德最權威的註釋家，拉丁學界尊稱其為「註釋家（the Commentator）」。其著作經希伯來文與拉丁文譯本傳入西方，激起「拉丁阿維羅伊主義」之爭，論及理智單一、世界永恆等議題，深刻挑戰並激盪了基督教經院神學。"
            },
            {
              "title_zh": "靈魂論註（論靈魂大註釋）",
              "title_orig": "Long Commentary on De Anima",
              "author": "伊本‧魯世德（阿維羅伊）",
              "era": "約 1186",
              "place": "安達盧斯（哥多華）",
              "language": "阿拉伯文（傳世為拉丁譯本）",
              "intro": "阿維羅伊為亞里斯多德《論靈魂》所作的長篇註釋，提出爭議極大的「理智單一論」：主動理智與質料理智為全人類所共有的單一實體，個人死後並無個別的不朽靈魂。此說經拉丁譯本傳入巴黎大學，引發劇烈爭論，阿奎那特撰《駁阿維羅伊主義者論理智單一》予以反駁，相關命題並於 1277 年遭巴黎主教譴責。此註釋是中世紀心靈哲學論戰的核心文本。"
            }
          ]
        },
        {
          "key": "kalam",
          "label": "伊斯蘭辯證神學部（凱拉姆）",
          "label_en": "Islamic Dialectical Theology (Kalām)",
          "desc": "艾什爾里派、馬圖里迪派與穆爾太齊賴派的信理辯證，及其對基督宗教的批判。",
          "works": [
            {
              "title_zh": "辨明宗教根本",
              "title_orig": "al-Ibāna ʻan Uṣūl al-Diyāna",
              "author": "艾什爾里（Abū al-Ḥasan al-Ashʻarī）",
              "era": "約930年代",
              "place": "巴格達",
              "language": "阿拉伯文",
              "intro": "艾什爾里派奠基之作。作者早年為穆爾太齊賴健將，後倒戈，以此書折衷傳統派與理性派：既守經文字面（如真主諸屬性、可見於後世），又用辯證方法回擊過度理性化。奠定順尼派主流神學路線，英譯題作《伊斯蘭根基之闡明》。"
            },
            {
              "title_zh": "精光集（辯證神學綱要）",
              "title_orig": "Kitāb al-Lumaʿ",
              "author": "艾什爾里（Abū al-Ḥasan al-Ashʻarī）",
              "era": "十世紀前半",
              "place": "巴格達",
              "language": "阿拉伯文",
              "intro": "艾什爾里的辯證神學綱要，以理性論證真主存在、屬性、意志與人之行為（獲得說 kasb），確立信仰與理性並用的中道方法，是艾什爾里派 kalām 最重要的簡明教程。"
            },
            {
              "title_zh": "伊斯蘭教派學說彙錄",
              "title_orig": "Maqālāt al-Islāmiyyīn wa-Ikhtilāf al-Muṣallīn",
              "author": "艾什爾里（Abū al-Ḥasan al-Ashʻarī）",
              "era": "十世紀前半",
              "place": "巴格達",
              "language": "阿拉伯文",
              "intro": "艾什爾里編纂的伊斯蘭教派學說彙錄，系統臚列各派（穆爾太齊賴、什葉、哈瓦利吉等）在神學諸議題的主張與分歧，是研究早期伊斯蘭思想與教義史的第一手百科式資料。"
            },
            {
              "title_zh": "導論（駁異端辯證神學總集）",
              "title_orig": "Kitāb al-Tamhīd fī al-Radd ʻalā al-Mulḥida",
              "author": "巴基拉尼（al-Bāqillānī, Abū Bakr）",
              "era": "約十世紀末至十一世紀初",
              "place": "巴格達／巴斯拉",
              "language": "阿拉伯文",
              "intro": "巴基拉尼為艾什爾里派承先啟後的大師，本書系統駁斥無神論者、二元論者、婆羅門、猶太、基督徒及穆爾太齊賴與什葉，建立以原子論宇宙觀為基礎的遜尼辯證神學體系，是中世紀伊斯蘭 kalām 護教學的里程碑。"
            },
            {
              "title_zh": "認主學（一神論之書）",
              "title_orig": "Kitāb al-Tawḥīd",
              "author": "馬圖里迪（Abū Manṣūr al-Māturīdī）",
              "era": "約940年代",
              "place": "撒馬爾罕",
              "language": "阿拉伯文",
              "intro": "馬圖里迪學派開山巨著，與艾什爾里派並列順尼兩大神學傳統。作者強調理性在認識真主與辨別善惡上的獨立效力，較艾什爾里更重人的自由抉擇，並駁斥二元論、摩尼教與部分穆爾太齊賴觀點。中亞哈乃斐派神學的權威文本。"
            },
            {
              "title_zh": "思辨要義（諸學總匯）",
              "title_orig": "Muḥaṣṣal Afkār al-Mutaqaddimīn wa-al-Mutaʼakhkhirīn",
              "author": "法赫爾丁‧拉齊（Fakhr al-Dīn al-Rāzī）",
              "era": "約1200年",
              "place": "赫拉特／賴伊",
              "language": "阿拉伯文",
              "intro": "法赫爾丁‧拉齊集古今哲人與神學家見解的辯證總綱，涵蓋知識論、存有論、真主屬性與末世論，以哲學工具重構艾什爾里派神學。其批判性辨析引圖西作專註回應，成為後古典伊斯蘭哲學神學融合的樞紐文本。"
            },
            {
              "title_zh": "先知證言之確立（駁基督宗教起源）",
              "title_orig": "Tathbīt Dalāʼil al-Nubuwwa",
              "author": "阿卜杜勒賈巴爾（ʻAbd al-Jabbār al-Hamadhānī）",
              "era": "約995年",
              "place": "賴伊（Rayy）",
              "language": "阿拉伯文",
              "intro": "晚期穆爾太齊賴領袖阿卜杜勒賈巴爾的護教鉅著，收入對基督宗教起源的獨特批判：主張保羅與君士坦丁扭曲了原初「猶太—基督徒」的耶穌之道。所存早期猶太—基督教傳承的片段極具史料價值，經雷諾茲（Reynolds）校譯研究重見於世。"
            },
            {
              "title_zh": "總集（論認主與公義諸門）",
              "title_orig": "al-Mughnī fī Abwāb al-Tawḥīd wa-al-ʿAdl",
              "author": "卡迪‧阿卜杜勒‧賈巴爾（ʿAbd al-Jabbār al-Hamadhānī）",
              "era": "約980年代",
              "place": "賴伊（Rayy）",
              "language": "阿拉伯文",
              "extent": "原著約20卷",
              "intro": "穆爾太齊賴派晚期集大成者阿卜杜勒‧賈巴爾的巨帙，逐門辯證真主獨一、公義、諸屬性與人的自由意志，系統捍衛唯理神學。原著約二十卷，是研究穆爾太齊賴思想與其對基督教批判的首要一手文獻。"
            }
          ]
        },
        {
          "key": "sufi-metaphysics",
          "label": "蘇菲形上學部",
          "label_en": "Sufi Metaphysics",
          "desc": "安薩里的靈知轉向、古沙伊里的道統輯錄與伊本阿拉比的存在單一論。",
          "works": [
            {
              "title_zh": "迷途知返（脫離迷誤者）",
              "title_orig": "al-Munqidh min al-Ḍalāl",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約1108年",
              "place": "圖斯",
              "language": "阿拉伯文",
              "intro": "安薩里的思想自傳，記述他遍歷凱拉姆、falsafa、伊斯瑪儀教誨派與蘇菲四途，遭遇徹底懷疑後終在蘇菲的親證之光中重獲確信。因其對確定性的內省剖析，常被與奧古斯丁《懺悔錄》、笛卡兒《方法論》並舉。"
            },
            {
              "title_zh": "光龕",
              "title_orig": "Mishkāt al-Anwār",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約1106年",
              "place": "圖斯／內沙布爾",
              "language": "阿拉伯文",
              "intro": "安薩里以《古蘭》「光節」與「帳幕聖訓」為軸的神秘神學短論，闡發真主為「諸天與地之光」的形上學，層層剖析遮蔽人心的光暗帷幕，直指唯一實在。融新柏拉圖流溢說與蘇菲靈知，是理解其晚期形上學的關鍵文本。"
            },
            {
              "title_zh": "古沙伊里論書",
              "title_orig": "al-Risāla al-Qushayriyya fī ʻIlm al-Taṣawwuf",
              "author": "古沙伊里（Abū al-Qāsim al-Qushayrī）",
              "era": "約1045年",
              "place": "內沙布爾",
              "language": "阿拉伯文",
              "intro": "古典蘇菲主義最權威的教本，作者致書各地蘇菲道團，力證正統蘇菲與順尼教義相合。書分蘇菲聖傳、術語辨析與修道階位（悔改、托靠、知足、愛慕等），系統定型了蘇菲的靈修語彙，為後世道乘（tariqa）奠定理論框架。"
            },
            {
              "title_zh": "揭開帷幕",
              "title_orig": "Kashf al-Maḥjūb",
              "author": "胡吉維里（al-Hujwīrī）",
              "era": "約1070年代",
              "place": "加茲尼／拉合爾",
              "language": "波斯文",
              "intro": "現存最早的波斯文蘇菲論著，胡吉維里於印度次大陸（拉合爾）傳道時所撰。全書系統闡述蘇菲的知識論、貧與清修、諸家道統與教義分歧，並逐一評述早期蘇菲師表言行，兼具教義綱要與傳記史料價值，對南亞伊斯蘭神秘主義的傳布影響至鉅，作者陵寢至今為拉合爾聖地。"
            },
            {
              "title_zh": "智慧的珍寶（智慧之戒面）",
              "title_orig": "Fuṣūṣ al-Ḥikam",
              "author": "伊本阿拉比（Ibn ʻArabī, Muḥyī al-Dīn）",
              "era": "約1229年",
              "place": "大馬士革",
              "language": "阿拉伯文",
              "extent": "二十七章（先知珠璣）",
              "intro": "「最偉大的謝赫」伊本阿拉比的形上學精華，藉二十七位先知各自體現的一種「智慧珠璣」，闡發「存在單一性」（waḥdat al-wujūd）：萬有皆真主自我顯現的鏡像。文字晦奧、註疏浩繁，是伊斯蘭神秘哲學影響最深遠、也最具爭議的著作。"
            },
            {
              "title_zh": "麥加的啟示",
              "title_orig": "al-Futūḥāt al-Makkiyya",
              "author": "伊本阿拉比（Ibn ʻArabī, Muḥyī al-Dīn）",
              "era": "約1203–1240年",
              "place": "麥加／大馬士革",
              "language": "阿拉伯文",
              "extent": "五百六十章",
              "intro": "伊本阿拉比篇幅浩瀚的蘇菲百科全書，據稱源於他在麥加克爾白旁所得的靈啟。全書逾五百章，遍論宇宙論、宇宙人（完人）、字母神秘學、修道階位與末世論，是「存在單一性」思想最完整的展開，堪稱伊斯蘭神秘主義的集大成之作。"
            }
          ]
        },
        {
          "key": "ihya",
          "label": "宗教學的復興部（安薩里四十卷）",
          "label_en": "Iḥyāʾ ʿUlūm al-Dīn (40 Books)",
          "desc": "安薩里《宗教學的復興》四篇四十卷全帙——崇拜、常行、致毀、致救，中世紀伊斯蘭最具影響的靈修神學總集。",
          "works": [
            {
              "title_zh": "宗教學的復興‧知識之書",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — Kitāb al-ʿIlm",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 1 卷",
              "intro": "《復興》開卷之作，界定何為有益之學：分辨義務之知與可嘉之知、譴責徒炫辯才的偽學者，並論師生之禮與求知的內在條件。它為全書四十卷立下方法論綱領——學問須導向敬畏與實踐，否則反成障蔽。"
            },
            {
              "title_zh": "宗教學的復興‧信條基礎之書",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — Qawāʿid al-ʿAqāʾid",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 2 卷",
              "intro": "闡述遜尼派信仰綱要：真主的獨一與屬性、先知的使命、末日與復生，並按信眾的領受能力分層施教。安薩里在此以簡明信條取代繁瑣辯證，主張信仰當先立於心而後求理解。"
            },
            {
              "title_zh": "宗教學的復興‧潔淨之奧義",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — Asrār al-Ṭahāra",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 3 卷",
              "intro": "論外在潔淨（小淨、大淨、除穢）的教法規範，並層層轉入內在潔淨——潔身之外更須潔心，去除污穢的念頭與習性。體現全書「由外禮入內修」的核心手法。"
            },
            {
              "title_zh": "宗教學的復興‧禮拜之奧義",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — Asrār al-Ṣalāt",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 4 卷",
              "intro": "論五番拜功的形式規範與其靈性內涵：專注（khushūʿ）、臨在感、誦讀的體味與叩首的謙卑。安薩里力斥有形無心的禮拜，主張禮拜的實質是心對真主的臨在。"
            },
            {
              "title_zh": "宗教學的復興‧天課之奧義",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — Asrār al-Zakāt",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 5 卷",
              "intro": "論法定施捨的規範、受施者的資格與施予的內在條件——去除吝嗇、不求名譽、不傷受者尊嚴。並論自願施捨的德行，是伊斯蘭社會倫理的核心卷。"
            },
            {
              "title_zh": "宗教學的復興‧齋戒之奧義",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — Asrār al-Ṣawm",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 6 卷",
              "intro": "論齋月封齋的規範與層級：常人之齋止於飲食，特選者之齋兼戒耳目口舌，至高者之齋則心不繫於真主以外。是安薩里靈修分層法的典型示範。"
            },
            {
              "title_zh": "宗教學的復興‧朝覲之奧義",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — Asrār al-Ḥajj",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 7 卷",
              "intro": "論朝覲的儀節規範與其象徵意涵：受戒衣如殮衣、環行如天使繞主、駐阿拉法特如末日集合。將外在行旅詮釋為靈魂歸向真主的完整象徵。"
            },
            {
              "title_zh": "宗教學的復興‧誦讀古蘭經之禮",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — Ādāb Tilāwat al-Qurʾān",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 8 卷",
              "intro": "論誦讀經文的外在禮節與內在條件：敬畏、體味、以心印證、勿以誦讀求名。並論釋經的界限與危險，是伊斯蘭讀經靈修學的代表文獻。"
            },
            {
              "title_zh": "宗教學的復興‧祈念與祈禱",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — al-Adhkār wa-al-Daʿawāt",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 9 卷",
              "intro": "論頌念真主之名（dhikr）與祈禱的規範、時機與心態，並輯錄先知傳下的禱詞。強調祈念的功效在於心的持續臨在，而非口舌的重複。"
            },
            {
              "title_zh": "宗教學的復興‧定時課誦之序",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — Tartīb al-Awrād",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 10 卷",
              "intro": "論將晝夜劃分為定時課誦（awrād）的靈修時間表：夜間禮拜的價值、晨昏的功課與時間的善用。為求道者提供具體可行的日常靈修架構，收束崇拜篇。"
            },
            {
              "title_zh": "宗教學的復興‧飲食之禮",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — Ādāb al-Akl",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 11 卷",
              "intro": "論飲食的禮節與節制：進食的儀節、與人共食之禮、少食的德行與貪食之害。將最日常的行為納入靈修，體現「常行亦是宗教」的主張。"
            },
            {
              "title_zh": "宗教學的復興‧婚姻之禮",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — Ādāb al-Nikāḥ",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 12 卷",
              "intro": "論婚姻的益處與危險、擇偶的條件、夫妻相處之道與家庭倫理，並衡量獨身與成家的利弊。是伊斯蘭家庭倫理最具影響力的靈修論述。"
            },
            {
              "title_zh": "宗教學的復興‧營生與謀業之禮",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — Ādāb al-Kasb wa-al-Maʿāsh",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 13 卷",
              "intro": "論買賣經營的道德規範：誠實、不欺、不囤積、公道交易，並論工作作為敬拜的一環。將商業倫理置於宗教實踐的框架中。"
            },
            {
              "title_zh": "宗教學的復興‧合法與可疑之辨",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — al-Ḥalāl wa-al-Ḥarām",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 14 卷",
              "intro": "論合法（ḥalāl）、禁戒（ḥarām）與可疑（shubha）三者的分辨，主張虔敬者當避可疑以自保。是伊斯蘭良心倫理與敬慎（waraʿ）之學的核心卷。"
            },
            {
              "title_zh": "宗教學的復興‧交往與相處之禮",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — Ādāb al-Ṣuḥba",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 15 卷",
              "intro": "論與人相處之道：友誼的條件、弟兄的權利、寬容與勸誡的分寸，並及與家人、鄰人、統治者的往來。是伊斯蘭社群倫理的實踐指南。"
            },
            {
              "title_zh": "宗教學的復興‧隱居獨處",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — Ādāb al-ʿUzla",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 16 卷",
              "intro": "衡量獨處與群居的利弊：獨處免於是非卻失於互助，群居得益於社群卻易染塵俗。安薩里主張依人的靈性狀態擇取，反映其中道立場。"
            },
            {
              "title_zh": "宗教學的復興‧旅行之禮",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — Ādāb al-Safar",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 17 卷",
              "intro": "論旅行的規範與靈性意義：為求學、朝覲或修行而行的正當性、旅途中的教法通融，並以外在旅程喻靈魂歸主的內在行旅。"
            },
            {
              "title_zh": "宗教學的復興‧聽覺與心醉",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — al-Samāʿ wa-al-Wajd",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 18 卷",
              "intro": "論蘇菲聽誦詩歌與音樂（samāʿ）引發心醉（wajd）的合法性爭議，細辨其條件、危險與流弊。是伊斯蘭音樂與靈修爭議最權威的中世紀論述。"
            },
            {
              "title_zh": "宗教學的復興‧勸善戒惡",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — al-Amr bi-al-Maʿrūf wa-al-Nahy ʿan al-Munkar",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 19 卷",
              "intro": "論穆斯林勸善戒惡的義務、層級與界限：何時當以心、以言、以手，並論對統治者進諫的分寸與風險。是伊斯蘭公共倫理的關鍵文獻。"
            },
            {
              "title_zh": "宗教學的復興‧先知的品格與生平",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — Ādāb al-Maʿīsha wa-Akhlāq al-Nubuwwa",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 20 卷",
              "intro": "輯述先知穆罕默德的日常舉止、待人接物與品格，作為信徒效法的具體典範，收束常行篇。是伊斯蘭「效法先知」倫理的集中呈現。"
            },
            {
              "title_zh": "宗教學的復興‧心之奇妙",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — ʿAjāʾib al-Qalb",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 21 卷",
              "intro": "致毀篇開卷，剖析心（qalb）的結構與功能：心、靈、魂、智四名的分辨，心如君王而諸官如兵，及撒但與天使對心的爭奪。是安薩里靈魂論與心理學的總綱。"
            },
            {
              "title_zh": "宗教學的復興‧靈魂的修煉",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — Riyāḍat al-Nafs",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 22 卷",
              "intro": "論品格的陶冶：品格可否改變、如何以刻意的反向操練矯治惡習、辨識自身缺點的方法（藉師友與敵人之口）。是伊斯蘭道德修養學最系統的論述。"
            },
            {
              "title_zh": "宗教學的復興‧兩慾之害",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — Kasr al-Shahwatayn",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 23 卷",
              "intro": "論口腹之慾與情慾這兩大根本慾望的危害與節制之道，主張以齋戒與紀律折服之，卻不主張全然禁絕。體現安薩里節制而非苦行的立場。"
            },
            {
              "title_zh": "宗教學的復興‧舌之害",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — Āfāt al-Lisān",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 24 卷",
              "intro": "細數舌頭的二十種災害：妄言、搬弄是非、背談、諂媚、爭辯、謊言、譏諷等，並論沉默的德行。是伊斯蘭言語倫理最詳盡的經典論述。"
            },
            {
              "title_zh": "宗教學的復興‧憤怒憎恨與嫉妒",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — Dhamm al-Ghaḍab wa-al-Ḥiqd wa-al-Ḥasad",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 25 卷",
              "intro": "論憤怒、記恨與嫉妒三種心病的根源、危害與療治：以寬恕折服憤怒、以善願化解嫉妒。是伊斯蘭心靈醫治學的核心卷。"
            },
            {
              "title_zh": "宗教學的復興‧今世之譴責",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — Dhamm al-Dunyā",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 26 卷",
              "intro": "論今世的虛幻與危險：其歡愉短暫、其追逐無盡，並辨明何為當棄之今世、何為可用之今世。奠定全書禁慾主義的世界觀基調。"
            },
            {
              "title_zh": "宗教學的復興‧財富與吝嗇之譴責",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — Dhamm al-Bukhl wa-Dhamm Ḥubb al-Māl",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 27 卷",
              "intro": "論貪財與吝嗇之害、財富的正當用途與危險，並論慷慨與知足的德行。與天課篇相呼應，構成伊斯蘭財富倫理的兩面。"
            },
            {
              "title_zh": "宗教學的復興‧名位與虛偽之譴責",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — Dhamm al-Jāh wa-al-Riyāʾ",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 28 卷",
              "intro": "論好名與作秀（riyāʾ，為人而修行）的隱微危害——虛偽是隱藏的偶像崇拜，最能腐蝕宗教行為。是伊斯蘭誠意論的關鍵卷。"
            },
            {
              "title_zh": "宗教學的復興‧驕傲與自滿之譴責",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — Dhamm al-Kibr wa-al-ʿUjb",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 29 卷",
              "intro": "論驕傲與自滿的根源與療治：驕傲對人、自滿對己，皆源於忘卻自身的受造性。並論謙卑的操練之法。"
            },
            {
              "title_zh": "宗教學的復興‧自欺之譴責",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — Dhamm al-Ghurūr",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 30 卷",
              "intro": "論各類人（學者、修士、富人、統治者）自欺的具體形態——以宗教之名行自欺之實，是致毀篇的總收束，警示靈修最深的陷阱。"
            },
            {
              "title_zh": "宗教學的復興‧悔改",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — al-Tawba",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 31 卷",
              "intro": "致救篇開卷，論悔改的定義、條件與持續性：悔改非一次事件而是終身的回轉，並論如何償還對人與對主的虧欠。是伊斯蘭悔改神學的經典論述。"
            },
            {
              "title_zh": "宗教學的復興‧忍耐與感恩",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — al-Ṣabr wa-al-Shukr",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 32 卷",
              "intro": "論忍耐與感恩為信仰的兩半：忍耐面對苦難、感恩面對恩典，二者實為一體的兩面。並細分忍耐的層級與感恩的實踐。"
            },
            {
              "title_zh": "宗教學的復興‧恐懼與盼望",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — al-Khawf wa-al-Rajāʾ",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 33 卷",
              "intro": "論敬畏與盼望的平衡：偏於恐懼則絕望，偏於盼望則怠惰，信徒當如鳥之雙翼並用。是伊斯蘭靈修心理平衡論的代表。"
            },
            {
              "title_zh": "宗教學的復興‧清貧與禁慾",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — al-Faqr wa-al-Zuhd",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 34 卷",
              "intro": "論清貧的德行與禁慾（zuhd）的真義——禁慾在於心不繫於物，而非必然無物。辨析安貧、知足與依賴他人的界線。"
            },
            {
              "title_zh": "宗教學的復興‧認主獨一與託靠",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — al-Tawḥīd wa-al-Tawakkul",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 35 卷",
              "intro": "論認主獨一如何導向對真主的全然託靠（tawakkul），並細辨託靠與棄絕人事努力的分別——託靠不廢因果，而是心繫於賜因者。"
            },
            {
              "title_zh": "宗教學的復興‧愛慕與親暱",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — al-Maḥabba wa-al-Shawq wa-al-Uns wa-al-Riḍā",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 36 卷",
              "intro": "論愛主、渴慕、親暱與知足四階：愛是一切德行的頂點，知識愈深則愛愈切。是安薩里神秘神學最高峰的一卷。"
            },
            {
              "title_zh": "宗教學的復興‧舉意與真誠",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — al-Niyya wa-al-Ikhlāṣ wa-al-Ṣidq",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 37 卷",
              "intro": "論意念（niyya）決定行為的價值、誠意（ikhlāṣ）使行為純為真主，及真誠（ṣidq）貫通言行與內心。是伊斯蘭行為倫理的樞紐。"
            },
            {
              "title_zh": "宗教學的復興‧自省與省察",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — al-Murāqaba wa-al-Muḥāsaba",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 38 卷",
              "intro": "論靈修的自我管理：如商人記帳般定時省察己行、時時警醒於真主的鑒察，並設定功課與自罰。是伊斯蘭靈修紀律的實務卷。"
            },
            {
              "title_zh": "宗教學的復興‧冥思",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — al-Tafakkur",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 39 卷",
              "intro": "論冥思受造界以認識造物主：由天地萬象的秩序思及真主的智慧與大能，並論冥思自身過犯以促悔改。是伊斯蘭自然神學與默觀的結合。"
            },
            {
              "title_zh": "宗教學的復興‧死亡與後世的追念",
              "title_orig": "Iḥyāʾ ʿUlūm al-Dīn — Dhikr al-Mawt wa-mā Baʿdahu",
              "author": "安薩里（Abū Ḥāmid al-Ghazālī）",
              "era": "約 1095–1105（棄職隱修期間著成）",
              "place": "大馬士革‧耶路撒冷‧圖斯",
              "language": "阿拉伯文",
              "parent": "宗教學的復興",
              "extent": "全書第 40 卷",
              "intro": "全書終卷，論追念死亡的功效、臨終的景況、墳中的境遇、復生、審判、火獄與樂園，終於見主之樂。以末世異象總收四十卷的靈修歷程。"
            }
          ]
        },
        {
          "key": "shia-ismaili-theology",
          "label": "伊斯瑪儀與什葉派神學部",
          "label_en": "Shia & Ismaili Theology",
          "desc": "精誠兄弟會百科書信、伊斯瑪儀派宇宙論與十二伊瑪目派的信理、倫理與伊瑪目論。",
          "works": [
            {
              "title_zh": "知識與解脫",
              "title_orig": "Gushāyish va Rahāyish",
              "author": "納西爾‧胡斯魯（Nāṣir-i Khusraw）",
              "era": "約1070年",
              "place": "雲甘（巴達赫尚）",
              "language": "波斯文",
              "intro": "波斯詩人兼伊斯瑪儀派傳道師納西爾‧胡斯魯的哲學問答集，以三十問回應信眾對創造、靈魂、善惡與知識的疑難，融新柏拉圖流溢說與法蒂瑪朝伊斯瑪儀神智學。以優美波斯散文闡述深奧教義，是什葉派哲學神學的珍貴文獻。"
            },
            {
              "title_zh": "兩種智慧的調和",
              "title_orig": "Kitāb-i Jāmiʿ al-ḥikmatayn",
              "author": "納西爾‧胡斯魯（Nāṣir-i Khusraw）",
              "era": "約1070年",
              "place": "巴達赫尚／呼羅珊（波斯東部）",
              "language": "波斯文",
              "intro": "納西爾胡斯魯晚年應巴達赫尚一位埃米爾之請，以波斯文逐節詮解一首哲理長詩，調和希臘哲學（法爾沙法）與伊斯瑪儀啟示教義兩種智慧。全書展現法蒂瑪王朝伊斯瑪儀思想的流溢宇宙論與靈知學，是中世紀什葉哲學神學的代表作，英譯題為《理性與啟示之間》。"
            },
            {
              "title_zh": "信仰的淨化（教義提綱）",
              "title_orig": "Tajrīd al-Iʻtiqād",
              "author": "納西爾丁‧圖西（Naṣīr al-Dīn al-Ṭūsī）",
              "era": "約1250–1265年",
              "place": "馬拉蓋（Maragha）",
              "language": "阿拉伯文",
              "parent": "傳世多藉希里《明意》（Kashf al-murād）註本合刊",
              "intro": "十二伊瑪目派哲學神學的奠基綱要，圖西以哲學方法系統論證存有、真主獨一、先知與伊瑪目統緒、末世諸題。文極精簡，後世註疏（以希立《明求》為最著）汗牛充棟，成為什葉派神學院（hawza）數百年的核心教材。"
            },
            {
              "title_zh": "納西爾倫理學",
              "title_orig": "Akhlāq-i Nāṣirī",
              "author": "納西爾丁‧圖西（Naṣīr al-Dīn al-Ṭūsī）",
              "era": "約1235年",
              "place": "波斯（庫希斯坦／阿拉穆特）",
              "language": "波斯文",
              "intro": "圖西以波斯文寫成的倫理—政治哲學名著，承米斯卡瓦伊《品性精煉》並融亞里斯多德與柏拉圖，分倫理、家政、政治三卷，論靈魂德性、家庭治理與理想城邦，是波斯世界最具影響的倫理教本，展現什葉哲人對古典德性論的接受與轉化。"
            },
            {
              "title_zh": "指引之書（十二伊瑪目傳）",
              "title_orig": "Kitāb al-Irshād",
              "author": "謝赫穆菲德（al-Shaykh al-Mufīd，卒 1022）",
              "era": "約十一世紀初",
              "place": "巴格達",
              "language": "阿拉伯文",
              "intro": "謝赫穆菲德為巴格達十二伊瑪目派奠基神學家，本書逐一敘述十二位伊瑪目的生平、德行、神蹟與明文指定（納斯），論證伊瑪目統緒的正當性，是什葉派伊瑪目學（imamate）的經典史傳兼教義著作，對什葉神學體系化影響深遠。"
            },
            {
              "title_zh": "先知的無罪辯",
              "title_orig": "Tanzīh al-anbiyāʾ",
              "author": "謝里夫穆爾塔達（al-Sharīf al-Murtaḍā，卒 1044）",
              "era": "十一世紀上半",
              "place": "巴格達",
              "language": "阿拉伯文",
              "intro": "謝里夫穆爾塔達為穆菲德門生、巴格達什葉派領袖，本書系統論證眾先知與伊瑪目的無罪與無謬（ʿiṣma），駁斥聖經與傳述中歸諸先知的過失記載，是十二伊瑪目派理性主義神學（近穆爾太齊賴）的護教代表作。"
            },
            {
              "title_zh": "精誠兄弟會書信‧數理篇",
              "title_orig": "Rasāʾil Ikhwān al-Ṣafāʾ — al-Riyāḍiyyāt (書信 1–14)",
              "author": "精誠兄弟會（Ikhwān al-Ṣafāʾ，巴斯拉祕密結社）",
              "era": "約 10 世紀（伊斯瑪儀派思想圈）",
              "place": "伊拉克巴斯拉",
              "language": "阿拉伯文",
              "parent": "精誠兄弟會書信集",
              "extent": "第 1–14 封",
              "intro": "書信集第一部，凡十四封，論算術、幾何、天文、音樂、地理、邏輯與工藝技術。以畢達哥拉斯式的數論為萬有和諧的鑰匙，主張數的秩序即靈魂上升的階梯，為全集奠定百科體系的方法論基礎。"
            },
            {
              "title_zh": "精誠兄弟會書信‧自然篇",
              "title_orig": "Rasāʾil Ikhwān al-Ṣafāʾ — al-Jismāniyyāt al-Ṭabīʿiyyāt (書信 15–31)",
              "author": "精誠兄弟會（Ikhwān al-Ṣafāʾ，巴斯拉祕密結社）",
              "era": "約 10 世紀（伊斯瑪儀派思想圈）",
              "place": "伊拉克巴斯拉",
              "language": "阿拉伯文",
              "parent": "精誠兄弟會書信集",
              "extent": "第 15–31 封",
              "intro": "第二部凡十七封，論物質、天地生成、礦物、植物、動物與人體。其中〈人與動物在精靈王前的訴訟〉一封以動物控訴人類的寓言著稱，是中世紀最早的生態倫理文本之一。"
            },
            {
              "title_zh": "精誠兄弟會書信‧心靈理性篇",
              "title_orig": "Rasāʾil Ikhwān al-Ṣafāʾ — al-Nafsāniyya al-ʿAqliyya (書信 32–40)",
              "author": "精誠兄弟會（Ikhwān al-Ṣafāʾ，巴斯拉祕密結社）",
              "era": "約 10 世紀（伊斯瑪儀派思想圈）",
              "place": "伊拉克巴斯拉",
              "language": "阿拉伯文",
              "parent": "精誠兄弟會書信集",
              "extent": "第 32–40 封",
              "intro": "第三部凡九封，論宇宙理智、普遍靈魂、人的靈魂與其上升復歸之道，融新柏拉圖流溢說與伊斯蘭啟示。是全集形上學的核心，深刻影響伊斯瑪儀派宇宙論與後世蘇菲思想。"
            },
            {
              "title_zh": "精誠兄弟會書信‧律法神學篇",
              "title_orig": "Rasāʾil Ikhwān al-Ṣafāʾ — al-Nāmūsiyya al-Ilāhiyya (書信 41–52)",
              "author": "精誠兄弟會（Ikhwān al-Ṣafāʾ，巴斯拉祕密結社）",
              "era": "約 10 世紀（伊斯瑪儀派思想圈）",
              "place": "伊拉克巴斯拉",
              "language": "阿拉伯文",
              "parent": "精誠兄弟會書信集",
              "extent": "第 41–52 封",
              "intro": "第四部凡十二封，論信仰、律法、先知使命、教團生活與魔法星象。主張各宗教律法皆為同一真理的象徵表述，倡導超越教派的普世和諧觀，是全集宗教哲學的總結。"
            }
          ]
        },
        {
          "key": "jewish-philosophy",
          "label": "猶太哲學部",
          "label_en": "Medieval Jewish Philosophy",
          "desc": "薩阿底亞至阿爾博的猶太理性神學——信仰與理性、神的屬性、先知論與信條之爭。",
          "works": [
            {
              "title_zh": "信仰與意見之書",
              "title_orig": "Kitāb al-Amānāt wa-al-Iʻtiqādāt / Emunot ve-Deʻot",
              "author": "薩阿底亞‧迦昂（Saʻadia Gaon）",
              "era": "933年",
              "place": "蘇拉學院（巴格達近郊）",
              "language": "猶太阿拉伯文",
              "intro": "中世紀猶太哲學開山之作。薩阿底亞借鑑穆爾太齊賴凱拉姆方法，系統論證創世、神的獨一與正義、自由意志、靈魂與復活、彌賽亞與救贖，力證理性與《妥拉》啟示相輔相成。奠定猶太理性神學傳統，回應卡拉派與伊斯蘭的挑戰。"
            },
            {
              "title_zh": "生命之泉",
              "title_orig": "Fons Vitae / Meqor Ḥayyim",
              "author": "伊本蓋比魯勒（Solomon ibn Gabirol / Avicebron）",
              "era": "約1050年",
              "place": "薩拉戈薩（安達魯斯）",
              "language": "阿拉伯文（原文佚，存拉丁譯本）",
              "intro": "猶太詩人哲學家伊本蓋比魯勒的新柏拉圖形上學對話，主張除真主外一切存有（含靈性實體）皆由普遍質料與形式構成。原阿拉伯文佚失，經拉丁譯本《生命之泉》廣傳，作者被經院學者誤認為穆斯林「阿維斯布隆」，深刻影響方濟會學派的質料論。"
            },
            {
              "title_zh": "心的義務",
              "title_orig": "al-Hidāya ilā Farāʼiḍ al-Qulūb / Ḥovot ha-Levavot",
              "author": "巴希亞‧伊本帕庫達（Baḥya ibn Paqūda）",
              "era": "約1080年",
              "place": "薩拉戈薩",
              "language": "猶太阿拉伯文",
              "extent": "共十門（章）",
              "intro": "中世紀猶太倫理靈修最受愛戴的經典，區分外在「肢體的義務」與內在「心的義務」，循獨一、省察、托靠、謙卑、悔改、自省、離世至愛神十門，引領靈魂由敬畏臻於愛主。深受蘇菲主義薰染，被譽為猶太的內修寶典。"
            },
            {
              "title_zh": "崇高的信仰",
              "title_orig": "al-ʻAqīda al-Rafīʻa / ha-Emunah ha-Ramah",
              "author": "亞伯拉罕‧伊本達伍德（Abraham ibn Daud）",
              "era": "約1160年",
              "place": "托雷多",
              "language": "猶太阿拉伯文",
              "intro": "首部系統引亞里斯多德哲學入猶太神學的著作，早於邁蒙尼德。伊本達伍德以物理學與形上學論證神的存在與獨一，調和自由意志與神的預知，力斥伊本蓋比魯勒的新柏拉圖質料論。為猶太亞里斯多德主義開路，惜為《迷途指津》光芒所掩。"
            },
            {
              "title_zh": "上主的戰爭",
              "title_orig": "Milḥamot ha-Shem",
              "author": "格爾松尼德（Levi ben Gershom / Gersonides）",
              "era": "約1329年",
              "place": "普羅旺斯（奧朗日）",
              "language": "希伯來文",
              "extent": "全六卷（論靈魂不朽、預言、神之知識、神意、天體、創造與神蹟）",
              "intro": "格爾松尼德歷時十二年寫就的哲學鉅著，以六卷論靈魂不朽、預言、神的知識、天命、天體與創世。他大膽主張神不預知未來的偶然事件、世界由無形質料受造，比邁蒙尼德更徹底地推進亞里斯多德主義，是中世紀猶太理性哲學的高峰與爭議焦點。"
            },
            {
              "title_zh": "主之光",
              "title_orig": "Or Adonai",
              "author": "哈斯代‧克雷斯卡斯（Ḥasdai Crescas）",
              "era": "約1410年",
              "place": "薩拉戈薩",
              "language": "希伯來文",
              "intro": "克雷斯卡斯對猶太亞里斯多德主義的系統反攻，逐一批判亞氏物理學前提（否定其無限與虛空不可能之說），重立以愛與意志為核心的神觀，並質疑邁蒙尼德將哲學等同信仰。其對無限空間、決定論的思辨預示了近代物理與斯賓諾莎哲學。"
            },
            {
              "title_zh": "信條書（信理之書）",
              "title_orig": "Sefer ha-ʻIqqarim",
              "author": "約瑟夫‧阿爾博（Joseph Albo）",
              "era": "約1425年",
              "place": "索里亞（卡斯提爾）",
              "language": "希伯來文",
              "extent": "共四卷",
              "intro": "經歷1413–14年托爾托薩宗教辯論後，阿爾博撰此書為猶太教義辯護。他將信仰根本歸為三大原則——神存在、妥拉自天啟、賞罰報應，其下再衍支條，簡化了邁蒙尼德的十三信條。兼具護教與教義學意義，廣受後世猶太社群傳誦。"
            },
            {
              "title_zh": "品格的修善",
              "title_orig": "Iṣlāḥ al-Akhlāq（Tikkun Middot ha-Nefesh）",
              "author": "伊本蓋比魯勒（Solomon ibn Gabirol）",
              "era": "約1045年",
              "place": "薩拉戈薩（安達魯斯）",
              "language": "阿拉伯文",
              "intro": "伊本蓋比魯勒的倫理小品，別出心裁地將靈魂諸德惡繫於五官感覺與體液氣質，以自然哲學為道德修養立論，不倚宗教誡命而訴諸理性與人性。此書為中世紀猶太倫理學的獨特嘗試，體現安達魯斯猶太—伊斯蘭思想交融的世俗化傾向。"
            },
            {
              "title_zh": "珠璣選",
              "title_orig": "Mukhtār al-Jawāhir（Mivḥar ha-Peninim）",
              "author": "傳伊本蓋比魯勒（attrib. Solomon ibn Gabirol）",
              "era": "公元十一世紀",
              "place": "安達魯斯",
              "language": "阿拉伯文（存希伯來譯本）",
              "extent": "約六百則格言",
              "intro": "傳為伊本蓋比魯勒輯錄的阿拉伯格言集《珠璣選》，收謙遜、知足、緘默、克己諸倫理箴言六百餘則，經希伯來譯本《珠璣精選》廣傳猶太社群。此書融伊斯蘭 adab 智慧文學與猶太道德教誨，為中世紀跨宗教格言傳統的代表，長為猶太倫理啟蒙讀本。"
            },
            {
              "title_zh": "迷途指津",
              "title_orig": "Dalalat al-Hairin / Moreh Nevukhim",
              "author": "邁蒙尼德",
              "era": "約 1190",
              "place": "埃及（福斯塔特）",
              "language": "阿拉伯文（希伯來字母書寫）",
              "intro": "邁蒙尼德是中世紀最偉大的猶太哲學家、法學家與醫師，此書為調和亞里斯多德哲學與猶太信仰而作，引導因哲學而困惑的信徒。書中以否定神學詮釋神之屬性、寓意解讀聖經擬人語、論證創世與先知預言，並闡釋誡命的理性根據。其思想深刻影響後世猶太哲學，並經拉丁譯本為阿奎那等基督教經院學者所引用，是三大一神教哲學對話的重要橋樑。"
            },
            {
              "title_zh": "庫薩里",
              "title_orig": "Kitab al-Khazari",
              "author": "猶大‧哈列維",
              "era": "約 1140",
              "place": "安達盧斯（托萊多／哥多華）",
              "language": "阿拉伯文（希伯來字母書寫）",
              "intro": "哈列維是安達盧斯的希伯來詩人與哲學家，此書以可薩王尋求真道、依次召見哲學家及基督、伊斯蘭、猶太教代表的故事為框架，最終由猶太拉比折服可薩王。書中為猶太信仰辯護，強調以色列民族的歷史啟示與神聖揀選高於抽象的哲學思辨，對亞里斯多德主義持批判立場。此書文采斐然、論辯有力，是中世紀猶太護教與宗教哲學的代表作。"
            }
          ]
        },
        {
          "key": "anti-christian-polemic",
          "label": "伊斯蘭與猶太駁基督教護教部",
          "label_en": "Islamic & Jewish Anti-Christian Polemics",
          "desc": "伊本哈茲姆、伊本泰米葉、嘎拉菲與猶太辯駁文獻對三位一體、道成肉身與經文可靠性的批判。",
          "works": [
            {
              "title_zh": "宗教與教派之判別",
              "title_orig": "Kitāb al-Fiṣal fī al-Milal wa-al-Ahwāʼ wa-al-Niḥal",
              "author": "伊本哈茲姆（Ibn Ḥazm al-Andalusī）",
              "era": "約1030年",
              "place": "科爾多瓦（安達魯斯）",
              "language": "阿拉伯文",
              "intro": "世界宗教史與比較宗教學的早期鉅著，札希里派學者伊本哈茲姆逐一評述各哲學派、婆羅門、祆教、猶太教、基督宗教與伊斯蘭諸派。以嚴苛的文本批評指摘《舊約》《福音》的矛盾與竄改，是中世紀最系統的伊斯蘭反基督教與反猶論戰文獻之一。"
            },
            {
              "title_zh": "正答——駁篡改基督宗教者",
              "title_orig": "al-Jawāb al-Ṣaḥīḥ li-man Baddala Dīn al-Masīḥ",
              "author": "伊本泰米葉（Ibn Taymiyya, Taqī al-Dīn）",
              "era": "約1316–1321年",
              "place": "大馬士革",
              "language": "阿拉伯文",
              "intro": "漢巴里派學者伊本泰米葉針對賽普勒斯基督徒護教書所作的巨幅回應，系統反駁三位一體、道成肉身與《福音》的可靠性，並論證穆罕默德先知身分見於聖經預言。是伊斯蘭反基督教論戰最完整、影響最深的中世紀文本，米謝爾（Michel）節譯為英文。"
            },
            {
              "title_zh": "光輝答辯",
              "title_orig": "al-Ajwiba al-Fākhira ʿan al-Asʾila al-Fājira",
              "author": "嘎拉菲（al-Qarāfī，卒 1285）",
              "era": "十三世紀",
              "place": "開羅",
              "language": "阿拉伯文",
              "intro": "嘎拉菲（開羅馬立基派法學家）回應一封基督徒護教信而作的系統駁論，逐條反駁三位一體、道成肉身與福音書論據，並論證穆罕默德的先知身分，是馬木路克時期伊斯蘭駁斥基督教護教學的代表作。"
            },
            {
              "title_zh": "盟約之書",
              "title_orig": "Sefer ha-Berit",
              "author": "約瑟夫‧基米希（Joseph Kimḥi）",
              "era": "約1170年",
              "place": "納博訥（普羅旺斯）",
              "language": "希伯來文",
              "intro": "中世紀猶太反基督宗教辯論文獻的早期代表，基米希以「忠信者」與「叛教者」對話體，系統回應基督徒依《舊約》經文對猶太教的攻擊，逐條重釋彌賽亞預言，並反過來質疑三位一體、道成肉身與童貞受孕的合理性。本書為普羅旺斯—西班牙猶太護教傳統奠定論辯範式，影響其子大衛‧基米希及後世辯論家。"
            },
            {
              "title_zh": "古辯駁書（尼扎宏‧維圖斯）",
              "title_orig": "Sefer Niṣṣaḥon Yashan（Nizzahon Vetus）",
              "author": "佚名（阿什肯納茲猶太編者；David Berger 校勘）",
              "era": "約13世紀末",
              "place": "德意志地區（阿什肯納茲）",
              "language": "希伯來文",
              "intro": "十三世紀末阿什肯納茲匿名編纂的希伯來文反基督教辯論手冊，逐節駁斥基督徒對希伯來聖經與新約的釋經，並反擊三位一體、童貞受孕、彌賽亞論等教義。柏格（David Berger）之校勘英譯本《中世紀盛期的猶太—基督徒辯論》為權威版本，是研究中世紀猶太護教與兩教論戰的核心文獻。"
            }
          ]
        },
        {
          "key": "heterodox-prereform",
          "label": "異端與前改教論述部",
          "label_en": "Heterodox & Pre-Reformation Treatises",
          "desc": "純潔派二元論、泛神論異端、自由靈派，及威克里夫與胡斯的教會論。",
          "works": [
            {
              "title_zh": "純潔派二元論述",
              "title_orig": "Liber de duobus principiis（合集）",
              "author": "純潔派（卡特里派）論者",
              "era": "12–13 世紀",
              "place": "朗格多克（法國南部）／義大利北部",
              "language": "拉丁文／奧克語",
              "intro": "純潔派是流行於法國南部與義大利北部的二元論運動，主張善的靈界上帝與惡的物質世界造物主兩元對立，視肉身與物質為惡，追求脫離肉體輪迴的純潔境界。其論述（如《二元論之書》）系統闡發二元神學與嚴格禁慾的「完人」修行。此運動因威脅羅馬教會而招致阿爾比十字軍征討與宗教裁判所的設立，是中世紀規模最大的異端事件之一。"
            },
            {
              "title_zh": "阿馬里克派泛神論述",
              "title_orig": "Doctrina Amalriciana（殘篇）",
              "author": "貝訥的阿馬里克及其門徒",
              "era": "約 1200–1210",
              "place": "巴黎",
              "language": "拉丁文",
              "intro": "阿馬里克是巴黎的神學教師，倡導泛神論式的主張：上帝即一切、萬物皆神，故信者一旦領悟自身與神合一便無罪可言。其思想受愛留根納影響，並被門徒推展為否定聖事、主張聖靈時代來臨的激進教說。此派於 1210 年巴黎公會議遭定罪，多名信徒被處火刑，阿馬里克遺骸亦遭掘出焚毀。其殘存論述反映中世紀盛期民間泛神與靈性自由思潮的暗流。"
            },
            {
              "title_zh": "自由靈派論述（明鏡）",
              "title_orig": "Le Mirouer des simples ames（自由靈思想）",
              "author": "自由靈派（瑪格麗特‧波雷特等）",
              "era": "約 1290–1310",
              "place": "低地國／法國北部",
              "language": "古法語",
              "intro": "自由靈派主張靈魂藉愛全然消融於上帝、達到「無欲無求」的境界後，便超越教會體制、聖事與道德律的約束。瑪格麗特‧波雷特的《單純靈魂之鏡》以靈魂與愛、理性的對話，描繪靈魂逐級上升至與神性合一而「自由」的歷程。此書因其激進的密契主張被判為異端，波雷特於 1310 年在巴黎被處火刑，然其著作仍秘密流傳，是女性密契書寫的重要見證。"
            },
            {
              "title_zh": "論教會",
              "title_orig": "De Ecclesia",
              "author": "約翰‧威克里夫",
              "era": "約 1378",
              "place": "牛津／盧特沃斯（英格蘭）",
              "language": "拉丁文",
              "intro": "威克里夫被稱為「宗教改革的晨星」，此書主張真正的教會是上帝預定得救者的無形團體，而非以教宗為首的羅馬體制；唯有聖經是信仰最高權威，神職人員的權柄繫於其德行而非職位。他並否定化質說、抨擊教會的財富與腐敗，主張將聖經譯為本地語言。其思想啟發了羅拉德派與胡斯運動，雖遭康斯坦茨公會議定罪，卻深刻預示了一個半世紀後的宗教改革。"
            },
            {
              "title_zh": "論教會",
              "title_orig": "De Ecclesia",
              "author": "揚‧胡斯",
              "era": "約 1413",
              "place": "布拉格（波希米亞）",
              "language": "拉丁文",
              "intro": "胡斯是布拉格的神學教師與改革者，深受威克里夫影響，此書主張基督而非教宗才是教會的元首，得救者組成的預定團體才是真教會，並嚴厲批判教會的腐敗、贖罪券與神職人員的不義。他堅持聖經與良心高於教會權威。胡斯雖獲安全通行許諾赴康斯坦茨公會議申辯，卻於 1415 年被定罪火刑，激起波希米亞的胡斯戰爭，其犧牲成為後世宗教改革的精神先導。"
            }
          ]
        },
        {
          "key": "derived-religion",
          "label": "衍生宗教部",
          "label_en": "Derived Religions",
          "desc": "中世紀自伊斯蘭衍生的新宗教教義文獻。",
          "works": [
            {
              "title_zh": "智慧書信",
              "title_orig": "Rasail al-Hikma / Epistles of Wisdom",
              "author": "哈姆扎‧伊本‧阿里及德魯茲早期傳道者",
              "era": "約 1017–1043",
              "place": "開羅（法蒂瑪王朝）／黎凡特",
              "language": "阿拉伯文",
              "intro": "德魯茲信仰由法蒂瑪王朝哈里發哈基姆治下的伊斯瑪儀派分支發展而成，《智慧書信》是其根本聖典，共一百一十一封書信，闡述其神論、靈魂輪迴、宇宙等級與隱祕教義。德魯茲尊哈基姆為神聖的化身，並發展出與主流伊斯蘭迥異的封閉信仰體系，僅向入門者傳授經文。此典籍長期祕不外傳，是研究中世紀近東宗教多元與伊斯瑪儀派衍生運動的珍貴文獻。"
            }
          ]
        }
      ]
    }
},
    {
  key: 'shizhuan',
  name: '史傳藏',
  name_en: 'Histories and Biographies',
  glyph: '史',
  genres: '紀‧傳‧編年‧遊記',
  summary: '收中世紀（約 800–1500）三軌史傳之作：拉丁西方的通史、編年、教宗修會史與聖徒傳，十字軍與東方遊記；旁及伊斯蘭區與猶太社群的史傳。以「敘事記事」為體，與信條法規之「論斷」、書信之「往來」分流，呈現中古基督教世界如何書寫自身與他者的歷史。',
  zheng: {
    summary: '拉丁西方與拜占庭的正統史傳，自加洛林編年至中古晚期，含通史、教宗修會史、聖徒傳、十字軍編年與東方遊記五部。',
    divisions: [
      {
        key: 'tongshi-biannian',
        label: '通史與編年部',
        label_en: 'Universal Histories and Chronicles',
        desc: '承接古代教會史傳統的世界編年與民族史，兼收拉丁與拜占庭兩脈。',
        works: [
          { title_zh: '英格蘭教會史續編', title_orig: 'Continuatio Historiae Ecclesiasticae Gentis Anglorum', author: '比德後續諸家', era: '8–9 世紀', place: '英格蘭諾森布里亞', language: '拉丁文', intro: '比德「英格蘭教會史」收筆於 731 年後，後世修士於賈羅與其他修院接續其編年，記諾森布里亞與英格蘭諸國教會與王權的後續發展。這批續編承襲比德「以救恩史為綱、以年份為骨」的書寫法，是研究加洛林時代前後不列顛島教會脈動的重要環節，雖多佚散，仍透過後世編年家的轉引而存其梗概。', link: '/fathers' },
          { title_zh: '兩座城的歷史', title_orig: 'Historia de Duabus Civitatibus', author: '弗賴辛的奧托', era: '約 1143–1146 年', place: '神聖羅馬帝國弗賴辛', language: '拉丁文', intro: '霍亨斯陶芬皇室出身的主教奧托，以奧古斯丁「上帝之城／世俗之城」二城論為架構，從創世寫到自身時代的世界通史。他將人類歷史視為兩座城此消彼長的場域，賦予編年以神學縱深，是中世紀史學思辨的高峰之一，亦反映十二世紀文藝復興對歷史哲學的重新探問。', link: '/fathers' },
          { title_zh: '腓特烈皇帝編年史', title_orig: 'Gesta Friderici I Imperatoris', author: '弗賴辛的奧托', era: '約 1157–1158 年', place: '神聖羅馬帝國弗賴辛', language: '拉丁文', intro: '奧托晚年受外甥皇帝紅鬍子腓特烈一世之託，記述其事功的當代編年，未竟而卒，由其書記拉黑文續成。較之「兩座城」的悲觀末世感，本書語調轉趨樂觀，視腓特烈為帶來和平的明君，是研究斯陶芬王朝與十二世紀帝國政治、城市興起與倫巴底紛爭的一手史料。', link: '/fathers' },
          { title_zh: '英格蘭諸王事蹟', title_orig: 'Gesta Regum Anglorum', author: '馬姆斯伯里的威廉', era: '約 1125 年', place: '英格蘭馬姆斯伯里修院', language: '拉丁文', intro: '威廉繼比德之後，自承擔起書寫英格蘭民族通史的志業，從盎格魯撒克遜諸王寫到諾曼征服後的時代。他廣徵文獻、留意史料來源，文筆典雅而富批判意識，兼有「英格蘭主教事蹟」一書並行，被視為中世紀英格蘭史學承先啟後的關鍵人物，所記諾曼征服前後的轉折尤為珍貴。', link: '/fathers' },
          { title_zh: '卡洛林編年史', title_orig: 'Annales Regni Francorum', author: '加洛林宮廷編年家', era: '8 世紀末–9 世紀', place: '法蘭克王國', language: '拉丁文', intro: '又稱「法蘭克王國編年史」，由查理曼及其後裔宮廷與修院逐年編纂，記法蘭克王國自八世紀中葉的征戰、教廷往來與帝國加冕等大事。文字簡質而連續，是復原加洛林帝國政治軍事年表的骨幹史料，後世埃因哈德「查理大帝傳」等亦多有取資，奠定加洛林史學的基礎。' },
          { title_zh: '編年史', title_orig: 'Chronographia', author: '米海爾‧普塞洛斯', era: '11 世紀', place: '拜占庭君士坦丁堡', language: '希臘文', intro: '博學的廷臣與哲學家普塞洛斯，以親歷者之筆記述馬其頓王朝晚期至十一世紀諸帝的興替。他不重戰役年表而重人物性格與宮廷心理，筆觸細膩近於文學，對皇帝的褒貶寓於描摹之中，是拜占庭中期政治文化與知識分子處境的絕佳寫照，史學價值與文采兼具。' },
          { title_zh: '阿萊克修斯傳', title_orig: 'Alexias', author: '安娜‧科穆寧娜', era: '約 1148 年', place: '拜占庭君士坦丁堡', language: '希臘文', intro: '皇帝阿萊克修斯一世之女安娜，以希臘古典文體為其父立傳，記科穆寧王朝中興、與諾曼人及突厥人的征戰，以及第一次十字軍過境君士坦丁堡的見聞。本書是中世紀少見出自女性史家之手的鉅著，從拜占庭視角審視西歐十字軍的記述尤為獨特，文中對拉丁人的觀感折射出東西教會的隔閡。' },
          { title_zh: '懺悔者狄奧法尼斯編年史', title_orig: 'Χρονογραφία / Chronographia', author: '懺悔者狄奧法尼斯（Theophanes the Confessor）', era: '約810–814年', place: '君士坦丁堡近郊修道院', language: '中古希臘文', intro: '拜占庭隱修士、聖像崇敬捍衛者狄奧法尼斯所撰世界編年史，接續喬治‧辛克盧斯之作，自戴克里先（284年）逐年記述至813年。保存大量已佚史料，是研究七至九世紀拜占庭、波斯與初興伊斯蘭擴張及聖像之爭最重要的希臘史源；作者因護持聖像受難封聖，後經教廷圖書館員阿納斯塔修斯譯成拉丁文西傳。' },
          { title_zh: '編年史（修士喬治／罪人喬治）', title_orig: 'Χρονικόν σύντομον / Georgius Monachus, Chronicon', author: '修士喬治（George the Monk／Hamartolos）', era: '約9世紀中（約842–867年）', place: '君士坦丁堡', language: '拜占庭希臘文', intro: '由一位謙稱「罪人」的修士所撰世界編年史，自亞當記至842年。重神學與教會立場，廣徵教父與聖經，對聖像派立場鮮明，影響斯拉夫世界甚鉅，後譯為古教會斯拉夫文，是基輔羅斯史學的重要源頭。' },
          { title_zh: '拜占庭史綱（811–1057）', title_orig: 'Σύνοψις Ἱστοριῶν / Synopsis Historion', author: '約翰‧斯基利澤斯（John Skylitzes）', era: '約11世紀末', place: '君士坦丁堡', language: '中古希臘文', intro: '拜占庭官員斯基利澤斯所撰歷史撮要，接續狄奧法尼斯，記述811至1057年諸帝興替、教會事務與帝國邊疆爭戰，補足拜占庭九至十一世紀史事斷層。馬德里抄本附大量微型彩繪插圖，是現存唯一帶插圖的拜占庭編年抄本，史料與藝術價值兼具，Wortley 英譯為現行標準本。' },
          { title_zh: '歷史（尼基塔斯‧侯尼亞提斯）', title_orig: 'Χρονικὴ Διήγησις / O City of Byzantium (Historia)', author: '尼基塔斯‧侯尼亞提斯（Niketas Choniates）', era: '約1204–1217年', place: '君士坦丁堡／尼西亞', language: '中古希臘文', intro: '拜占庭高官侯尼亞提斯所撰編年，記1118至1207年科穆寧、安格洛斯王朝興亡，高潮為作者親歷的1204年第四次十字軍攻陷君士坦丁堡。以沉痛典雅之筆痛陳拉丁人對聖城的劫掠與褻瀆，是拜占庭由盛轉衰的第一手見證，與威阿杜安的西方記述構成同一事件的雙面史證。' },
          { title_zh: '歷史（喬治‧帕希梅雷斯）', title_orig: 'Συγγραφικαὶ Ἱστορίαι / Relations Historiques', author: '喬治‧帕希梅雷斯（George Pachymeres）', era: '約1308年前後', place: '君士坦丁堡', language: '拜占庭希臘文', intro: '記述米海爾八世與安德洛尼卡二世兩朝（1255–1308），即帕列奧洛戈斯王朝光復君士坦丁堡後的政教風波。詳載里昂教會合一爭議與東方教會內部分裂，作者身兼教士與官員，立場審慎，是晚期拜占庭教會史的核心文獻。' },
          { title_zh: '羅馬史（尼基弗魯斯‧格雷戈拉斯）', title_orig: 'Ῥωμαϊκὴ Ἱστορία / Byzantina Historia', author: '尼基弗魯斯‧格雷戈拉斯（Nikephoros Gregoras）', era: '14世紀中（約1359年止）', place: '君士坦丁堡', language: '拜占庭希臘文', intro: '記1204至1359年帕列奧洛戈斯朝史事，篇幅宏大。作者為反靜修主義（反帕拉瑪斯）健將，後半部詳載靜修論爭，是研究14世紀拜占庭神學辯論與內戰最重要的當事人記述之一。' },
          { title_zh: '歷史四書（約翰六世‧坎塔庫澤努斯回憶錄）', title_orig: 'Ἱστοριῶν βιβλία δ\' / Historiarum libri IV', author: '約翰六世‧坎塔庫澤努斯（John VI Kantakouzenos）', era: '約1354–1383年（1354 退位出家為僧後撰寫，至 1383 年逝世前）', place: '曼加納修道院，君士坦丁堡', language: '拜占庭希臘文', intro: '退位為僧的皇帝親撰回憶錄，記1320至1356年內戰與其執政始末，採第三人稱自辯。兼為帕拉瑪斯靜修神學的有力護教者，是極罕見由君主本人書寫、兼具政治史與神學辯護雙重身分的史傳。' },
          { title_zh: '歷史（杜卡斯）', title_orig: 'Ἱστορία Τουρκοβυζαντινή / Historia Turco-Byzantina', author: '杜卡斯（Doukas）', era: '15世紀中（約1462年止）', place: '萊斯沃斯島／熱那亞屬地', language: '拜占庭希臘文', intro: '記1341至1462年鄂圖曼崛起與拜占庭覆亡，含1453年君士坦丁堡陷落的生動記述。作者親拉丁、傾向教會合一，立場有別於反合一史家，為陷落史提供關鍵互校視角。亦有同時代古義大利文譯本傳世。' },
          { title_zh: '編年史（喬治‧斯弗朗澤斯）', title_orig: 'Χρονικόν / Geōrgiou Sphrantzē Chronikon', author: '喬治‧斯弗朗澤斯（George Sphrantzes／Phrantzes）', era: '1413–1477年（晚年於修院撰成）', place: '伯羅奔尼撒／科孚島', language: '拜占庭希臘文', intro: '末代皇帝近臣的私人日記體編年，記1413至1477年，是1453年陷落的第一手在場見證。作者於城破後被擄、家破人亡，晚年出家撰此，記述冷峻沉痛，為亡國平民與被擄者的聲音留下罕見記錄。' },
          { title_zh: '穆罕默德二世傳（伊姆夫羅斯的克里托布洛斯）', title_orig: 'Ξυγγραφὴ Ἱστοριῶν / History of Mehmed the Conqueror', author: '伊姆夫羅斯的克里托布洛斯（Kritoboulos）', era: '約1467年', place: '伊姆夫羅斯島', language: '拜占庭希臘文', intro: '由歸順鄂圖曼的希臘士紳撰寫，記1451至1467年穆罕默德二世征服史，含征服者視角下的君士坦丁堡陷落。雖頌揚蘇丹，卻為基督徒所書、獻給蘇丹，是亡國後基督徒在伊斯蘭治下書寫立場的特殊見證。' },
          { title_zh: '歷史（喬治‧阿克羅波利特斯）', title_orig: 'Χρονικὴ Συγγραφή / The History', author: '喬治‧阿克羅波利特斯（George Akropolites）', era: '13世紀後半（約1261年後）', place: '尼西亞／君士坦丁堡', language: '拜占庭希臘文', intro: '記1203至1261年，即第四次十字軍後拜占庭流亡尼西亞帝國至光復君士坦丁堡。作者為尼西亞朝重臣、外交家，曾親與里昂使團交涉教會合一，是流亡時期政教史最權威的當事人記述。' },
          { title_zh: '歷史述證十書（拉奧尼科斯‧哈爾科孔狄萊斯）', title_orig: 'Ἀποδείξεις Ἱστοριῶν / Historiarum demonstrationes', author: '拉奧尼科斯‧哈爾科孔狄萊斯（Laonikos Chalkokondyles）', era: '15世紀後半', place: '雅典／伯羅奔尼撒', language: '拜占庭希臘文', intro: '末代拜占庭史家，仿希羅多德筆法記1298至1463年，以鄂圖曼崛起為主軸，旁及西歐諸國，兼具民族誌廣度。為從希臘人視角理解拜占庭覆亡與鄂圖曼世界體系形成的重要文獻。' },
          { title_zh: '歷史概覽（約安尼斯‧佐納拉斯）', title_orig: 'Ἐπιτομὴ Ἱστοριῶν / Epitome Historiarum', author: '約安尼斯‧佐納拉斯（John Zonaras）', era: '12世紀上半', place: '君士坦丁堡（後隱修於聖格利凱里亞島）', language: '拜占庭希臘文', intro: '由曾任御前要職、後出家的教會法學者所撰世界通史，自創世記至1118年阿萊克修斯一世逝世。引用今已佚失的羅馬與拜占庭史料（如卡西烏斯‧狄奧前卷），是復原古典史源的關鍵中介，兼具教會法權威。' },
          { title_zh: '西默盎‧梅塔弗拉斯特斯與洛戈忒特斯編年史', title_orig: 'Symeonis Magistri et Logothetae Chronicon', author: '西默盎‧梅塔弗拉斯特斯（洛戈忒特斯，Symeon Logothetes）', era: '約10世紀', place: '君士坦丁堡', language: '古希臘文', intro: '託名與西默盎相關的拜占庭世界編年史，自創世記述至十世紀中葉，是研究九至十世紀拜占庭政教史的重要史源，尤詳於聖像之爭後的正統重整。Wahlgren 校勘本（CFHB 系列）為現代學界標準版。' },
          { title_zh: '敘利亞人米海爾編年史', title_orig: 'Maktbānūt zabnē / Chronicle of Michael the Syrian', author: '敘利亞人米海爾一世（Michael the Syrian，安提阿敘利亞正教教長，1126–1199）', era: '12世紀末（約1195年）', place: '安提阿／梅利泰內（敘利亞正教教長轄區）', language: '古典敘利亞文', extent: '全十一卷（Gorgias 版）／全四卷（Chabot 版）', intro: '敘利亞正教（米亞腓索）安提阿牧首米海爾大帝所撰自創世至1195年的浩瀚世界與教會通史，是現存規模最大的敘利亞語史著，採多欄並陳體例分述教會史、世俗史與雜記，保存大量今已散佚的更早敘利亞與希臘史源。是研究十字軍時代近東、敘利亞正教自我認同與東方諸教會關係的核心文獻，沙博四卷法譯本與 Gorgias 十一卷敘英對照本為標準整理。' },
          { title_zh: '巴爾‧赫布拉烏斯編年史（世界政治史）', title_orig: 'Maktbānūt zabnē / The Chronography of Bar Hebraeus (secular part)', author: '格里高利‧巴爾‧赫布拉烏斯（Gregory Bar Hebraeus，阿布勒‧法拉吉，1226–1286）', era: '約1285年（卒前完成）', place: '波斯馬拉蓋（伊兒汗國治下）', language: '古典敘利亞文', extent: '政治史第一部（Chronicon Syriacum）', intro: '敘利亞正教大主教（瑪夫良）巴爾‧赫布拉烏斯世界通史的世俗政治史部分，自創世（亞當）敘至蒙古伊兒汗時代，以基督徒視角記述波斯、阿拉伯、塞爾柱、蒙古諸朝興替。學貫敘、阿、希、波多語，融匯東西史源，是十三世紀近東基督徒史學的高峰，巴吉英譯本附敘利亞原文，流傳甚廣。' },
          { title_zh: '祖克寧編年史（提爾‧瑪赫雷的偽狄奧尼修斯）', title_orig: 'Chronicle of Zuqnīn (Pseudo-Dionysius of Tel-Maḥrē)', author: '佚名（祖克寧隱修院修士，託名提爾‧瑪赫雷的狄奧尼修斯）', era: '約775年', place: '祖克寧隱修院（阿米達／今土耳其迪亞巴克爾附近）', language: '古典敘利亞文', extent: '全四部', intro: '敘利亞正教祖克寧隱修院所出、記事下迄約775年的世界與教會編年，第四部對早期阿拔斯王朝治下美索不達米亞百姓苦難、瘟疫與賦稅有罕見的平民視角記載，舊誤歸教長狄奧尼修斯，今稱偽狄奧尼修斯。' },
          { title_zh: '佚名作者編年史‧迄主後1234年', title_orig: 'Anonymi auctoris Chronicon ad annum Christi 1234 pertinens', author: '佚名（埃德薩一帶的敘利亞正教史家）', era: '約1237年前後', place: '埃德薩／敘利亞正教轄區', language: '古典敘利亞文', extent: '全二卷（CSCO 版）', intro: '一部記事下迄1234年的匿名敘利亞正教世界與教會編年，世俗與教會兩編並行，對十字軍諸國、贊吉王朝與蒙古來襲有當代見聞，是與米海爾編年並列的十三世紀敘利亞史源，沙博（Chabot）校注本為標準版。' },
          { title_zh: '列王的榮耀', title_orig: 'Kebra Nagast (ክብረ ነገሥት)', author: '阿克蘇姆的雅各（Yəsḥaq）等編', era: '約 1314–1322 年（吉茲文定本）', place: '衣索匹亞阿克蘇姆', language: '吉茲文（古衣索匹亞文）', extent: '全 117 章', intro: '衣索匹亞正教（泰瓦希多）的民族與王朝奠基聖典，敘示巴女王往訪所羅門、誕下梅內利克一世，並將約櫃自耶路撒冷迎入阿克蘇姆，藉此論證衣索匹亞君主乃所羅門─大衛王統的合法繼承、衣索匹亞乃新的揀選之民。十四世紀由阿克蘇姆教士自阿拉伯文與更早素材編譯為吉茲文定本，長期被奉為帝國的「神聖憲章」。是研究衣索匹亞教會自我認同、聖王神學與東方基督教民族史的核心文獻。' },
          { title_zh: '珠串編年', title_orig: 'Naẓm al-Jawhar (Annals of Eutychius)', author: '亞歷山卓的歐提基烏斯（賽義德‧伊本‧巴特里克，Saʿīd ibn Baṭrīq）', era: '約 935–940 年', place: '埃及亞歷山卓（默基特派）', language: '阿拉伯文', intro: '默基特派（與大公教會共融的希臘正教）亞歷山卓宗主教歐提基烏斯所撰阿拉伯文世界編年史，自創世亞當敘至作者所處的十世紀。以基督徒視角貫通聖經史、希羅史與伊斯蘭初興，是最早以阿拉伯文書寫的基督教通史之一，兼具教會史與普世史價值，反映阿拉伯化的東方基督徒如何在伊斯蘭世界中保存並重述其歷史記憶。' },
          { title_zh: '大公會議史', title_orig: 'Tārīkh al-Majāmiʿ (History of the Councils)', author: '塞維魯‧伊本‧穆卡法', era: '10 世紀', place: '埃及阿什穆奈因', language: '阿拉伯文', intro: '塞維魯自科普特教會立場敘述歷代大公會議及其基督論爭議，尤重尼西亞、以弗所與迦克墩會議的歷史和後果。作品不只是會議事件的編年，也保存非迦克墩埃及教會對分裂成因與自身正統性的記憶，是阿拉伯語科普特史學與教義史的重要原典。' },
              { title_zh: '喬治亞編年（卡特利編年）', title_orig: 'Kʻartʻlis Cʻxovreba (The Georgian Chronicles)', author: '歷代喬治亞編者輯', era: '約 11–14 世紀彙編', place: '喬治亞', language: '古典喬治亞文', intro: '喬治亞王國的官方民族與王朝編年總集，又稱「卡特利編年」，自傳說始祖敘至中世紀盛期，匯集歷代編者之作。內容貫串喬治亞歸信基督、教會建立、與拜占庭及波斯的周旋，及大衛建設者、塔瑪爾女王的黃金時代。為喬治亞史學與民族認同的核心文本，兼存高加索地區教會史與政治史的關鍵史料。' },
          { title_zh: '歷史書', title_orig: 'Kitāb al-Tawārīkh', author: '阿布‧沙基爾‧伊本‧拉希卜（Abū Shākir ibn al-Rāhib）', era: '1257–1271', place: '埃及開羅', language: '阿拉伯文', intro: '科普特學者所撰百科式編年，前部論曆法與年代學，後部述世界史、伊斯蘭史、亞歷山卓宗主教與會議。它呈現十三世紀科普特阿拉伯學術如何以精密紀年重建基督教歷史秩序，也反映開羅教會菁英的跨學科史學。亦可補入科普特編年傳統。' },
          { title_zh: '蒙福彙編', title_orig: 'Kitāb al-Taʾrīkh / al-Majmūʿ al-Mubārak', author: '吉爾吉斯‧馬金‧伊本‧阿米德（Jirjis al-Makīn ibn al-ʿAmīd）', era: '13世紀中葉', place: '埃及開羅、敘利亞大馬士革', language: '阿拉伯文', intro: '科普特官員兼史家所編世界史，自亞當至希拉克略，再續述伊斯蘭史至拜巴爾即位。此書跨用聖經、基督教阿拉伯與穆斯林史源，代表馬穆魯克初期埃及基督徒的普世史視野，並為後來穆斯林史家與衣索匹亞譯本所吸收。適合列入中世紀埃及通史脈絡。' },
          { title_zh: '阿姆達‧塞雍光榮勝利記', title_orig: 'The Glorious Victories of ʿAmda Ṣǝyon', author: '不詳（所羅門王朝宮廷史官）', era: '14世紀', place: '衣索匹亞宮廷', language: '吉茲文', intro: '記述阿姆達‧塞雍一世對伊法特與東南穆斯林諸邦的戰役，將君王塑為護教征服者。它是衣索匹亞王家傳記體史書的早期高峰，保存十四世紀政教擴張語言，並展現基督王國與伊斯蘭邊疆的軍事敘事。可列王朝戰史核心文本之一。' },
          { title_zh: '札拉‧雅各布王紀', title_orig: 'Chronicle of Emperor Zärʾa Yaʿǝqob', author: '不詳（所羅門王朝宮廷史官）', era: '15世紀', place: '衣索匹亞德布雷伯罕與宮廷', language: '吉茲文', intro: '記述札拉‧雅各布的登位、教會改革、鎮壓異端、對阿達爾與北方邊疆的軍事行動。其史傳價值在於呈現十五世紀衣索匹亞王權如何重塑正統、禮儀與國家秩序，並記錄佛羅倫斯會議時代的外交視野。可補十五世紀王家編年序列。' },
          { title_zh: '阿爾茨魯尼家史', title_orig: 'Պատմութիւն տանն Արծրունեաց (Patmutʻiwn tann Artsruneatsʻ)', author: '托夫馬‧阿爾茨魯尼', era: '9世紀末至10世紀初', place: '瓦斯普拉坎、凡湖地區', language: '古典亞美尼亞語', intro: '托夫馬以阿爾茨魯尼王族為主軸，追述亞美尼亞古史、阿拉伯統治與瓦斯普拉坎興起。其對九世紀南亞美尼亞政治、貴族與阿赫塔馬爾宮廷的記錄，是地方王朝史與全國史交會的重要中世紀證詞。' },
          { title_zh: '塔倫的斯捷帕諾斯普世史', title_orig: 'Տիեզերական պատմութիւն (Tiezerakan patmutʻiwn)', author: '斯捷帕諾斯‧塔羅內齊，又稱阿索吉克', era: '1004或1005年完成', place: '塔倫、阿尼與亞美尼亞修院圈', language: '古典亞美尼亞語', intro: '全書三卷，自創世敘至作者當代，第三卷詳記十世紀亞美尼亞、拜占庭與教會爭議。其按政治、宗教、學者分欄組織材料，顯示中世紀亞美尼亞通史書寫走向編年化與資料化。' },
          { title_zh: '拉斯蒂韋爾特的阿里斯塔克斯災難史', title_orig: 'Պատմութիւն Արիստակիսի Լաստիվերտցւոյ (Patmutʻiwn Aristakisi Lastiverttsʻwoy)', author: '阿里斯塔克斯‧拉斯蒂韋爾齊', era: '1072至1079年', place: '大亞美尼亞、阿尼與東安納托利亞', language: '古典亞美尼亞語', intro: '此書記述十一世紀阿尼王國衰亡、拜占庭吞併、塞爾柱入侵與曼齊刻爾特前後局勢。作者具神學詮釋，卻保留大量近當代見聞，是理解中世紀亞美尼亞失國記憶的核心史源。' },
          { title_zh: '瓦爾丹歷史彙編', title_orig: 'Հաւաքումն պատմութեան (Havakʻumn patmutʻean)', author: '瓦爾丹‧阿雷韋爾齊', era: '1267年前後完成', place: '東亞美尼亞、基利家與蒙古伊兒汗國境內', language: '古典亞美尼亞語', intro: '瓦爾丹以普世史框架統攝聖經、古代與亞美尼亞歷史，敘事延至十三世紀蒙古時代。其作者兼具教師、外交與教會身份，對蒙古統治下亞美尼亞社會及史學自覺尤具定位價值。' },
          { title_zh: '弓箭民族史', title_orig: 'Պատմութիւն ազգին նետողաց (Patmutʻiwn azgin netoghatsʻ)', author: '格里戈爾‧阿克內爾齊', era: '1273年', place: '基利家亞美尼亞阿克內爾修院', language: '古典亞美尼亞語', intro: '本書專記成吉思汗以降蒙古人進入近東及其對亞美尼亞的影響，題名以弓箭民族稱蒙古。它不是普世史，而是十三世紀危機記錄，保存失傳師承材料，是蒙古統治史的珍貴亞美尼亞文本。' },
          { title_zh: '帖木兒及其繼承者史', title_orig: 'Պատմութիւն Լանկ-Թամուրայ եւ յաջորդաց իւրոց (Patmutʻiwn Lank-Tʻamuray ew yajordatsʻ iwrotsʻ)', author: '托夫馬‧梅措佩齊', era: '15世紀上半葉', place: '梅措普、瓦斯普拉坎、埃奇米阿津', language: '古典亞美尼亞語', intro: '托夫馬記述一三八六至一四四零年前後帖木兒、沙哈魯與黑羊王朝對高加索的戰爭。多數內容帶有親歷或近聞性質，並關聯宗主教座遷回埃奇米阿津，是晚中世紀亞美尼亞政教史要源。' },
          { title_zh: '卡爾特明編年史', title_orig: 'Chronicle of 819 / Chronicle of Qarṭmin', author: '佚名卡爾特明修士', era: '約819年', place: '圖爾阿卜丁卡爾特明修院', language: '敘利亞語', intro: '此編年以耶穌誕生至819年的年代表記錄教會與政局，特重卡爾特明修院、敘利亞正教宗主教與阿拔斯哈里發。它保存圖爾阿卜丁在伊斯蘭早期至中世紀初的地方記憶，是後來846年編年史的重要來源。' },
          { title_zh: '八一三年編年史', title_orig: 'Chronicle of 813', author: '佚名敘利亞正教作者', era: '約813年', place: '上美索不達米亞或哈蘭一帶', language: '敘利亞語', intro: '此殘篇記述754至813年間敘利亞正教宗主教、阿拔斯內亂、饑荒與地震等事。它雖僅存數葉，仍是哈倫拉希德死後敘利亞秩序崩解與哈蘭基督徒社群發展的早期見證，補足大型後世編年之空白。' },
          { title_zh: '八四六年編年史', title_orig: 'Chronicle of 846', author: '佚名敘利亞正教作者', era: '846至873年間定稿', place: '哈蘭或圖爾阿卜丁', language: '敘利亞語', intro: '此殘存通史原自創世敘起，現存部分以教會史與679至846年間政事最有價值。它從敘利亞正教立場保存拜占庭、阿拔斯與地方主教資料，並與祖克寧、米海爾等傳統相互參照，可作中世紀早期小編年代表。' },
          { title_zh: '尼西比斯的以利亞年表', title_orig: 'Chronography / Opus Chronologicum', author: '尼西比斯的以利亞', era: '11世紀前半，記至1018年', place: '尼西比斯', language: '敘利亞語與阿拉伯語', intro: '以利亞的年表兼具通史、曆法與王朝表，從羅馬帝國至11世紀初並列教會與政權紀年。它保存薩珊、東方教會宗主教和伊斯蘭時代資料，且常註明失傳來源，是東敘利亞史學由敘利亞語轉向阿拉伯語環境的標誌。' }
        ],
      },
      {
        key: 'jiaozong-xiuhui',
        label: '教宗與修會史部',
        label_en: 'Histories of Popes and Religious Orders',
        desc: '羅馬教宗世系名錄之續編，及各修會創建與發展的記述。',
        works: [
          { title_zh: '教宗名錄續編', title_orig: 'Liber Pontificalis (Continuatio)', author: '羅馬教廷編纂者', era: '9 世紀及其後', place: '羅馬', language: '拉丁文', intro: '「教宗名錄」自古代起逐位記述歷任羅馬主教的出身、任內事功、營建與敕令，中世紀續編延伸至加洛林乃至更晚時代。每位教宗一傳，兼具傳記與檔案性質，保存大量教廷財產、禮儀與建築資料，是研究中古教廷制度史不可或缺的連續性史源，雖部分條目雜有傳說，仍為一手骨幹。' },
          { title_zh: '熙篤會創建史', title_orig: 'Exordium Cistercii / Carta Caritatis', author: '熙篤會早期諸長', era: '12 世紀', place: '勃艮第熙篤修院', language: '拉丁文', intro: '記熙篤會自一○九八年於熙篤荒野立院、追求嚴守本篤會規與勞動清貧理想的創建緣起，並收錄規範各院關係的「愛德憲章」。此類修會創建史既是制度文獻也是靈修自述，呈現十二世紀修道改革運動如何透過組織創新而席捲西歐，為日後托缽修會的興起作了鋪墊。', link: '/fathers' },
          { title_zh: '道明會創建史', title_orig: 'Libellus de Principiis Ordinis Praedicatorum', author: '薩克森的若爾當', era: '約 1233 年', place: '波隆那', language: '拉丁文', intro: '道明會第二任總會長若爾當追述創會者古茲曼的道明如何因駁斥阿爾比異端而立宣道修會，記其早期組織、巡迴宣講與大學據點的建立。本書兼為會史與創始人行誼，是理解十三世紀托缽修會以講道與學術回應時代挑戰的關鍵內部文獻，語調虔敬而力圖存信史。', link: '/fathers' },
          { title_zh: '巴爾‧赫布拉烏斯教會編年史', title_orig: 'Chronicon Ecclesiasticum (Maktbānūt zabnē, ecclesiastical part)', author: '格里高利‧巴爾‧赫布拉烏斯（Gregory Bar Hebraeus，1226–1286）', era: '約1280年代', place: '波斯馬拉蓋／敘利亞', language: '古典敘利亞文（附英譯）', extent: '上下兩篇（西敘利亞教會＋東方教會）', intro: '巴爾‧赫布拉烏斯世界通史的教會史部分，上篇述安提阿西敘利亞教會主教序列暨東方總主教（瑪夫良）統緒，下篇專述東方（景教）宗主教與東方都主教，是兼跨米亞腓索與東方教會兩傳統最完整的中世紀教會通史，蒙古時代教會史不可或缺。' },
          { title_zh: '院長之書（馬爾加的多馬隱修史）', title_orig: 'The Book of Governors (Historia Monastica of Thomas of Marga)', author: '馬爾加的多馬（Thomas of Marga，景教東方教會主教）', era: '約840年', place: '馬爾加／貝特‧阿貝隱修院（今伊拉克北部）', language: '古典敘利亞文（附英譯）', extent: '全二冊（敘利亞原文＋英譯）', intro: '景教東方教會主教多馬所撰貝特‧阿貝大隱修院歷代院長（「統領」）與修士行誼，兼為東方教會修道制度與聖徒傳的寶庫，記述伊斯蘭治下美索不達米亞修道生活、傳教遠及中亞，是東敘利亞隱修史與東向宣教網絡最重要的早中世紀史料。' },
              { title_zh: '亞歷山卓教長史', title_orig: 'History of the Patriarchs of Alexandria (Siyar al-Bīʿa)', author: '塞維魯‧伊本‧穆卡法（Sāwīrus ibn al-Muqaffaʿ）等', era: '10 世紀起（後世續編）', place: '埃及（科普特正教）', language: '阿拉伯文（譯自科普特文素材）', intro: '科普特正教歷任亞歷山卓宗主教的傳記彙編，傳統歸於十世紀主教塞維魯‧伊本‧穆卡法集纂，後世續補至晚近。每位教長一傳，記述其任內教會事務、與伊斯蘭統治者的交涉及埃及基督徒處境。為科普特教會最重要的連續性史源，保存大量已佚的科普特文史料，是研究伊斯蘭治下埃及基督教史不可或缺的一手文獻。' },
          { title_zh: '埃及諸教堂與修院史', title_orig: 'Tārīkh al-kanāʾis wa-l-adyira / Akhbār nawāḥī Miṣr', author: '阿布‧馬卡里姆（Abū al-Makārim Saʿdallāh ibn Jirjis）', era: '約1200', place: '埃及', language: '阿拉伯文', intro: '記述埃及、努比亞及鄰近地區教堂、修院、聖物與地方傳承，是阿尤布時期科普特教會地誌。其材料兼具旅行見聞、檔案記憶與修院史價值，可補足教長史以外的基層教會圖像，並標示十二、十三世紀尼羅河流域基督教網絡。可列入非洲教會史核心文本。' },
          { title_zh: '西薩坎省史', title_orig: 'Պատմութիւն նահանգին Սիսական (Patmutʻiwn nahangin Sisakan)', author: '斯捷帕諾斯‧奧爾別良', era: '1297至1299年', place: '休尼克、西薩坎與塔特夫', language: '古典亞美尼亞語', intro: '作者為休尼克都主教，以碑銘、文書、家族記憶與舊史編成地方史。全書保存教區、貴族、修院與塔特夫傳統，兼具省志和教會史功能，是蒙古時代東亞美尼亞地方身份的代表作。' },
          { title_zh: '約翰與尤西米烏斯諸父傳', title_orig: 'ცხოვრება ნეტარისა მამისა ჩუენისა იოანესი და ეფთჳმესი და უწყებაჲ ღირსისა მის მოქალაქობისა მათისაჲ', author: '喬治‧聖山者', era: '1040年後', place: '阿索斯山伊維龍修院', language: '古喬治亞語', intro: '喬治為伊維龍修院領袖，記述約翰與尤西米烏斯生平及喬治亞阿索斯社群功業。文本結合聖徒傳、修院史與文化辯護，見證喬治亞僑居修院在拜占庭世界中的中世紀角色。' },
          { title_zh: '教會消息摘要', title_orig: 'Mukhtaṣar al-akhbār al-bīʿīya', author: '佚名東方教會作者', era: '1007/1008年', place: '東方教會巴格達宗主教區', language: '阿拉伯語', intro: '此阿拉伯語摘要教會史保存東方教會都主教省與教區資料，並與塞爾特傳統平行。其成書於11世紀初，反映阿拔斯時代東敘利亞教會以阿拉伯語整理本身制度記憶，對重建主教區、修院與族群分布尤有用。' },
          { title_zh: '東方教會諸宗主教史', title_orig: 'Akhbār baṭārikat Kanīsat al-Mashriq / De Patriarchis Nestorianorum Commentaria', author: '馬里‧本蘇萊曼', era: '12世紀後半，止於阿卜迪紹三世', place: '巴格達與摩蘇爾文化圈', language: '阿拉伯語', intro: '馬里在塔樓之書傳統中保存自東方教會起源至12世紀的宗主教敘事，兼記選立、主教按立、宮廷關係與教區變動。其阿拉伯語史傳部分為後來阿姆爾與斯利巴續修依據，是中世紀景教自我書寫的骨幹資料。' }
        ],
      },
      {
        key: 'shengtu-zhuan',
        label: '聖徒傳部',
        label_en: 'Lives of the Saints',
        desc: '聖人行誼與殉道事蹟的彙編與單傳，兼收聖傳總集與會祖傳記。',
        works: [
          { title_zh: '黃金傳說', title_orig: 'Legenda Aurea', author: '雅各‧德‧佛拉金', era: '約 1260 年', place: '熱那亞', language: '拉丁文', intro: '道明會士、後任熱那亞總主教的雅各，按禮儀年序彙編約一百八十位聖人的事蹟與相關節期釋義，成為中世紀流傳最廣的聖傳總集。書中糅合史實、傳說與神蹟敘事，雖不以信史自限，卻深刻形塑了西歐的聖人崇拜、藝術圖像與民間虔敬，是理解中古宗教想像與通俗神學的一把鑰匙。', link: '/fathers' },
          { title_zh: '亞西西方濟各大傳', title_orig: 'Legenda Maior Sancti Francisci', author: '波那文圖拉', era: '約 1263 年', place: '巴黎／義大利', language: '拉丁文', intro: '方濟各會總會長、神學家波那文圖拉受命為會祖方濟各撰寫的官方傳記，後被定為唯一正式聖傳。書中以神學家的眼光詮釋方濟各的清貧、傳道、聖痕與愛受造物之德，將其塑造為效法基督的典範。本書既是聖傳也是靈修神學文本，對方濟各形象的後世定型影響至深。', link: '/fathers' },
          { title_zh: '坎特伯雷的多默殉道記', title_orig: 'Vita et Passio Sancti Thomae', author: '索爾茲伯里的若望等', era: '12 世紀末', place: '英格蘭坎特伯雷', language: '拉丁文', intro: '坎特伯雷總主教多默‧貝克特因與英王亨利二世爭教權，於一一七○年在主教座堂遇刺殉道，事後群傳並出。諸傳記述其與王權衝突、流亡與慘死的經過，迅速催生其封聖與朝聖熱潮。這批聖傳是十二世紀政教博弈與殉道崇拜交織的鮮明見證，亦為中古英格蘭教會史一手材料。', link: '/fathers' },
          { title_zh: '聖徒傳全集（默諾洛吉昂）', title_orig: 'Menologion (Christian Novels from the Menologion of Symeon Metaphrastes)', author: '西默盎‧梅塔弗拉斯特斯（Symeon Metaphrastes）', era: '約10世紀（約980年代編纂）', place: '君士坦丁堡', language: '古希臘文', extent: '全集；現代選譯本', parent: '西默盎《聖徒傳全集》', intro: '拜占庭官員西默盎奉命將數百篇散在各處的聖徒行傳依教會年曆（默諾洛吉昂）重編潤飾，文體統一典雅，成為東正教聖徒傳的標準範本。收錄殉道者、隱修士、女聖人事蹟，影響後世希臘、斯拉夫各教會聖傳傳統至深。' },
          { title_zh: '新神學家西默盎傳', title_orig: 'The Life of Saint Symeon the New Theologian', author: '尼基塔斯‧斯提塔托斯（Niketas Stethatos）', era: '11世紀（約1050年代）', place: '君士坦丁堡', language: '古希臘文', intro: '新神學家西默盎的門徒尼基塔斯為其師所撰傳記，記述這位拜占庭神祕主義大師的生平、靈修經驗與身後爭議。兼具聖徒傳與靈修見證雙重性質，是理解東正教「心禱」與光照神學傳統源流的關鍵文本，後世靜修主義（赫西卡主義）多溯源於此。' },
          { title_zh: '拜占庭聖女傳輯', title_orig: 'Holy Women of Byzantium: Ten Saints\' Lives in English Translation', author: '佚名諸家（Alice-Mary Talbot 編）', era: '5–13世紀（拜占庭中後期，聖傳成文於五至十三世紀）', place: '拜占庭帝國', language: '中古希臘文', extent: '合集（十篇聖女傳）', intro: '彙集十篇拜占庭中後期女聖人原傳，含聖像之爭時代的捍衛者、皇后、修女院長、隱修女與裝扮男裝入修道院者，呈現希臘東方傳統中與拉丁西方平行而獨立的女性聖德書寫，補正以主教王侯為中心的史傳之偏，是研究拜占庭性別、社會階層與民間信仰的重要文本群。' },
          { title_zh: '科普特聖人曆', title_orig: 'Synaxarium Alexandrinum (Coptic Synaxarium)', author: '科普特正教輯（傳歸米海爾‧馬利古，Mīkhāʾīl of Malīj 等）', era: '約 13–14 世紀定型', place: '埃及（科普特正教）', language: '阿拉伯文（部分譯自科普特文）', intro: '科普特正教按教會曆逐日編排的聖人與殉道者紀念總集，每日列出當日所紀念聖徒的簡傳與事蹟，於日課中誦讀。它彙整了埃及自使徒時代以降的殉道者、隱修士、宗主教與聖母節期傳統，是科普特教會禮儀生活與歷史記憶的核心文獻，也是研究埃及基督教聖徒崇拜、隱修運動與民間信仰最豐富的一手彙編。' },
          { title_zh: '衣索匹亞聖人曆', title_orig: 'Mashafa Sǝnkǝssar (Ethiopian Synaxarium / Book of the Saints)', author: '衣索匹亞正教輯（譯自阿拉伯科普特本並增補本土聖徒）', era: '約 14–15 世紀譯入並增補', place: '衣索匹亞（泰瓦希多正教）', language: '吉茲文', intro: '衣索匹亞正教按教會曆編排的聖人紀念總集，源出科普特聖人曆的吉茲文譯本，並大量增補衣索匹亞本土聖徒、君王與隱修士。每日誦念當日聖徒簡傳，兼收頌讚聖詩（sälam）。它既是衣索匹亞教會禮儀年的骨幹，也保存了大量本土聖傳與民族記憶，是研究衣索匹亞基督教獨特聖統與信仰生活不可或缺的彙編。' },
          { title_zh: '塔克拉‧海馬諾特傳', title_orig: 'Gädlä Täklä Hāymānot (Acts of Takla Haymanot)', author: '衣索匹亞德布雷‧利巴諾斯修院輯', era: '約 14–15 世紀', place: '衣索匹亞紹阿', language: '吉茲文', intro: '衣索匹亞最受敬仰的本土聖人、德布雷‧利巴諾斯修院創立者塔克拉‧海馬諾特（約1215–1313）的聖傳（gädl）。記述其傳道、行神蹟、苦修（傳說曾立禱至斷腿）與重整衣索匹亞修道制度的事蹟。作為衣索匹亞民族聖傳文學（gädl）的代表作，它呈現本土隱修傳統與王權、教權的交涉，是研究衣索匹亞教會自我形塑的核心聖傳。' },
          { title_zh: '聖母瑪利亞奇蹟集', title_orig: 'Täʾammǝra Maryam (Miracles of Mary)', author: '衣索匹亞正教輯（譯自歐洲—阿拉伯傳統並本土增補）', era: '約 14–15 世紀傳入並增補', place: '衣索匹亞', language: '吉茲文', intro: '衣索匹亞正教廣為傳誦的聖母瑪利亞顯靈施恩故事集，源自中世紀歐洲與阿拉伯的瑪利亞奇蹟傳統，傳入後大幅增補衣索匹亞本土情節。皇帝扎拉‧雅各布更下令於禮儀中誦讀。書中瑪利亞屢屢救助、醫治、赦免向她祈求的信眾，是研究衣索匹亞聖母敬禮、民間信仰與宗教藝術（其插圖傳統尤負盛名）的珍貴文獻。' },
          { title_zh: '法尼約特的約翰殉道記', title_orig: 'Martyrdom of John of Phanijōit', author: '不詳（科普特傳統）', era: '1211', place: '埃及開羅', language: '科普特文', intro: '記述改宗伊斯蘭後復歸基督信仰的科普特人約翰在開羅受審、被處死的經過。文本直面十三世紀埃及的同化、叛教與見證問題，是中世紀科普特新殉道文學的核心個案，亦反映穆斯林政權下基督徒身分邊界。可作信仰邊界史料。' },
          { title_zh: '巴爾蘇瑪裸體者傳與奇蹟', title_orig: 'Life and Miracles of Barsawma al-ʿUryān', author: '不詳（科普特阿拉伯傳統）', era: '14世紀', place: '埃及開羅、代爾沙赫蘭', language: '阿拉伯文', intro: '記述巴爾蘇瑪由宮廷書吏轉為赤貧苦修者，在舊開羅與修院中行神蹟、受迫害並成聖。它反映馬穆魯克時代科普特都市苦修、穆斯林互動與聖徒崇敬的形成，也保存十三、十四世紀開羅社會的宗教緊張。可補都市聖人傳統研究。' },
          { title_zh: '伊亞蘇斯‧莫阿傳', title_orig: 'Gädlä Iyäsus Moʾa', author: '海克湖司提法諾斯修院傳統', era: '14–15世紀', place: '衣索匹亞海克湖', language: '吉茲文', intro: '記述海克湖修院院長伊亞蘇斯‧莫阿的修道、教學與扶助耶庫諾‧阿姆拉克事蹟。文本對所羅門王朝興起、修院學校與王權合法化提供早期本土敘事，是十三世紀後衣索匹亞政教轉型的重要聖傳史料。可列修院與王朝交會史料。' },
          { title_zh: '厄沃斯塔特沃斯傳', title_orig: 'Gädlä ʾEwosṭatewos', author: '不詳（厄沃斯塔特沃斯門徒傳統）', era: '15世紀傳統、現存本較晚', place: '衣索匹亞提格雷、厄立特里亞、埃及與亞美尼亞', language: '吉茲文', intro: '敘述厄沃斯塔特沃斯倡守雙安息日、流亡努比亞與埃及、朝聖耶路撒冷並卒於亞美尼亞。作品連結衣索匹亞修道改革、跨紅海交通與十五世紀安息日爭議的根源，並保存北非與近東教會互動的聖傳記憶。適合補入跨境聖徒傳序列。' },
          { title_zh: '拉利貝拉傳', title_orig: 'Gädlä Lalibäla', author: '不詳（札格維王朝聖王傳統）', era: '約15世紀定型', place: '衣索匹亞拉斯塔、拉利貝拉', language: '吉茲文', intro: '以聖王傳形式敘述拉利貝拉的出生預兆、流亡耶路撒冷、即位與鑿建岩石教堂。此書把札格維王權、非洲耶路撒冷想像與建築記憶結合，是中世紀衣索匹亞王聖傳代表，並為拉利貝拉聖城傳統提供敘事框架。可補聖王與聖地史傳。' },
          { title_zh: '瓦爾德巴的撒母耳傳', title_orig: 'Gädlä Samuʾel za-Waldǝbba', author: '不詳（瓦爾德巴修院傳統）', era: '15世紀', place: '衣索匹亞提格雷、瓦爾德巴', language: '吉茲文', intro: '記述撒母耳的離俗、苦修、馴獅、朝聖與創建瓦爾德巴修院傳統。它以神蹟敘事保存北衣索匹亞荒野修道理想，並反映十五世紀聖徒圖像與修院認同，對理解提格雷隱修網絡尤具價值。可補衣索匹亞北部修院聖傳與朝聖序列研究。' },
          { title_zh: '加布拉‧曼法斯‧基杜斯傳', title_orig: 'Gädlä Gäbrä Mänfäs Qǝddus', author: '不詳（衣索匹亞隱修傳統）', era: '1382–1411年間成書傳統', place: '上埃及、衣索匹亞紹阿', language: '吉茲文', intro: '敘述出身埃及的隱士加布拉‧曼法斯‧基杜斯遷往衣索匹亞，在荒野與野獸同居、行奇蹟並受民眾敬奉。作品呈現埃及科普特聖性在中世紀紹阿的在地化，也凸顯十四、十五世紀衣索匹亞苦修想像。可補衣索匹亞聖者在地傳統研究。' },
          { title_zh: '格里戈爾‧漢茲特利傳', title_orig: 'ცხოვრება გრიგოლ ხანძთელისა (Tskhovreba Grigol Khandztelisa)', author: '喬治‧梅爾丘列', era: '951年，後於958至966年間增補', place: '陶－克拉爾傑蒂與漢茲塔修院', language: '古喬治亞語', intro: '本傳描寫格里戈爾推動陶－克拉爾傑蒂修院復興，並連結巴格拉季王權與教會自立。作品以聖徒傳形式保存十世紀喬治亞統一理念、修院網絡與語言身份，史傳價值甚高。' },
          { title_zh: '貞潔之書', title_orig: 'Ktābā d-nakputā / Liber castitatis', author: '巴士拉的伊紹德納赫', era: '約860年', place: '巴士拉與邁尚', language: '敘利亞語', intro: '此書收約140則東方教會修士、隱修者與修院創建者小傳，重心在北美索不達米亞、波斯與阿拉伯治下修院。它以簡短傳記保存4至9世紀聖徒網絡、地名與修道傳統，是中世紀東敘利亞聖徒傳彙編的重要標本。' },
          { title_zh: '拉班約瑟夫布斯納亞傳', title_orig: 'Life of Rabban Joseph Busnaya', author: '約翰‧巴爾卡爾敦', era: '10世紀末至11世紀初', place: '摩蘇爾以北薩普納谷與阿馬迪亞地區', language: '敘利亞語', intro: '此傳由弟子約翰記述東方教會隱修士約瑟夫布斯納亞的生平、修院遷徙與靈修教誨。文本提供10世紀北伊拉克基督教地理、庫爾德襲擾、抄經與口誦文化的細節，可作聖徒傳與地方史雙重資料。' },
          { title_zh: '拉班斯利巴殉道錄', title_orig: 'Martyrology of Rabban Sliba', author: '哈赫的拉班斯利巴', era: '13世紀末至14世紀初', place: '圖爾阿卜丁與敘利亞正教修院圈', language: '敘利亞語', intro: '此殉道錄彙列敘利亞正教多位殉道者與聖人的紀念日，成書於蒙古時代前後。雖非連續敘事，卻保存地方聖徒崇敬、禮曆分類與人名傳承，是研究中世紀西敘利亞聖徒傳統與社群記憶的基礎文本。' },
          { title_zh: '帖撒羅尼迦的聖德奧多拉傳', title_orig: 'Βίος καὶ πολιτεία τῆς ὁσίας Θεοδώρας τῆς ἐν Θεσσαλονίκῃ', author: '額我略司鐸', era: '9世紀末至10世紀初成書', place: '帖撒羅尼迦', language: '希臘文', intro: '此傳敘述艾基納女子德奧多拉因海患遷至帖撒羅尼迦、入聖斯德望女院及死後聖油奇蹟。篇幅宏大，兼保存破壞聖像爭議記憶，是中期拜占庭女性修道、城市聖徒崇敬與地方史的重要史料。' },
          { title_zh: '艾基納的聖阿塔納西亞傳', title_orig: 'Βίος καὶ πολιτεία τῆς ὁσίας μητρὸς ἡμῶν Ἀθανασίας καὶ διήγησις μερικὴ τῶν θαυμάτων αὐτῆς', author: '佚名', era: '10世紀初成書', place: '艾基納與君士坦丁堡', language: '希臘文', intro: '作品記述阿塔納西亞由婚姻轉入修道、建立女院、施濟貧弱並以遺骸顯奇蹟。文本成於聖徒卒後不久，反映阿拉伯襲擾下愛琴海島嶼社會，也是中期拜占庭女院領袖形象的代表。' },
          { title_zh: '年輕的聖瑪利亞傳', title_orig: 'Βίος τῆς ὁσίας Μαρίας τῆς Νέας', author: '佚名', era: '11世紀前期成書', place: '比齊耶與色雷斯', language: '希臘文', intro: '此傳以亞美尼亞出身的已婚女子瑪利亞為主角，敘述家內衝突、受虐而死與墓前醫治奇蹟。它把殉道語彙移入家庭倫理，呈現拜占庭邊境貴族、婚姻權力與女性聖德的中世紀化。' },
          { title_zh: '克里索巴蘭頓女院長伊琳娜傳', title_orig: 'Βίος καὶ πολιτεία τῆς ὁσίας μητρὸς ἡμῶν Εἰρήνης τῆς Χρυσοβαλάντου', author: '佚名', era: '10世紀成書', place: '君士坦丁堡', language: '希臘文', intro: '傳記描繪卡帕多基亞貴女伊琳娜放棄宮廷婚配，成為克里索巴蘭頓女院長，並以預知、樂園果實與護院奇蹟聞名。它連結正統勝利後的宮廷想像與都城女修道，具鮮明拜占庭定位。' },
          { title_zh: '阿爾塔的聖德奧多拉傳', title_orig: 'Βίος τῆς ὁσίας Θεοδώρας τῆς βασιλίσσης Ἄρτης', author: '約伯修士', era: '13世紀後期成書', place: '伊庇魯斯阿爾塔', language: '希臘文', intro: '短傳敘述伊庇魯斯統治者之妻德奧多拉遭逐、忍受貧困、復歸宮廷並創建阿爾塔聖喬治女院。文本把王室婚姻、地方政治與修道退隱結合，是拉丁占領後希臘地方聖女崇敬的證據。' },
          { title_zh: '奧尼的瑪利亞傳', title_orig: 'Vita Mariae Oigniacensis', author: '雅各伯‧德‧維特里', era: '約1215年成書', place: '列日教區與奧尼', language: '拉丁文', intro: '雅各伯以親見與聽聞寫成奧尼瑪利亞傳，記述她由婚姻轉向貞潔、照護痲瘋者、引導神職人員與靈視哭泣。作品對十三世紀貝居安運動的合法化極有影響，是西歐女靈修傳記範本。' },
          { title_zh: '艾維耶爾的盧特加德傳', title_orig: 'Vita Piae Lutgardiae', author: '康廷普雷的多瑪斯', era: '1248年初稿，1254至1255年修訂', place: '列日教區與艾維耶爾', language: '拉丁文', intro: '多瑪斯為熙篤會修女盧特加德作傳，敘述她從修院少女成為靈視者，經歷與基督換心、失明、預知與治病。作品塑造封閉女院中的神秘權威，是十三世紀低地女性聖傳的重要文本。' },
          { title_zh: '納匝肋的貝雅特麗斯傳', title_orig: 'Vita Beatricis', author: '佚名熙篤會作者', era: '13世紀後期成書', place: '布拉班特納匝肋修院', language: '拉丁文', intro: '此傳據貝雅特麗斯的中荷蘭語札記與見證改寫，敘述她在熙篤會女院中的教育、苦修、聖三靈視與愛德階梯。它保存女性自述被拉丁聖傳化的過程，是低地修女書寫的關鍵證據。' },
          { title_zh: '聖杜斯琳傳', title_orig: 'La vida de la benaurada sancta Doucelina', author: '菲莉帕‧德‧波爾瑟萊，傳統歸名', era: '約1297年成書', place: '普羅旺斯、耶爾與馬賽', language: '奧克語', intro: '奧克語聖傳敘述杜斯琳創立普羅旺斯貝居安團體、照護貧病、禁欲苦修與公開出神。由女性團體內部記憶編成，呈現方濟各靈修、南法城市虔敬與女領袖權威的交會。' },
          { title_zh: '錫耶納的聖加大利納大傳', title_orig: 'Legenda maior sanctae Catharinae Senensis', author: '卡普亞的雷孟', era: '1385至1395年間成書', place: '錫耶納、羅馬與多明我會網絡', language: '拉丁文', intro: '雷孟以告解者與同行者身分撰寫加大利納大傳，敘述她的禁欲、神婚、教會調停、瘟疫服務與支持羅馬教宗。文本把女靈視者置於西方大分裂政治中，是晚中世紀聖女公共性史料。' }
        ],
      },
      {
        key: 'shizijun-biannian',
        label: '十字軍編年部',
        label_en: 'Chronicles of the Crusades',
        desc: '東征聖地與拉丁諸國之創建與征服的當代編年。',
        works: [
          { title_zh: '海外史', title_orig: 'Historia Rerum in Partibus Transmarinis Gestarum', author: '提爾的威廉', era: '約 1170–1184 年', place: '十字軍耶路撒冷王國', language: '拉丁文', intro: '生於耶路撒冷拉丁王國、官至提爾總主教的威廉，撰寫自第一次十字軍至其時代的東方拉丁諸國通史。他通曉阿拉伯語、態度相對持平，既頌揚十字軍偉業，亦批評其內部傾軋與失策。本書文采與史識俱佳，是研究十字軍國家政治、社會與東西交涉最權威的當代敘事。', link: '/fathers' },
          { title_zh: '法蘭克人事蹟', title_orig: 'Gesta Francorum et Aliorum Hierosolimitanorum', author: '佚名南義騎士', era: '約 1100–1101 年', place: '南義大利／聖地', language: '拉丁文', intro: '出自一位隨諾曼公爵博希蒙德東征的無名騎士之手，以樸質直白的拉丁文記述第一次十字軍自出發至攻陷耶路撒冷的全程。作為親歷者的一手見聞，本書視角貼近普通戰士，敘事生動而少修飾，成為後世諸多十字軍史改寫潤色的底本，史料價值極高。' },
          { title_zh: '征服君士坦丁堡記', title_orig: 'De la Conquête de Constantinople', author: '若弗魯瓦‧德‧維爾阿杜安', era: '約 1207–1213 年', place: '法蘭西香檳', language: '古法文', intro: '香檳元帥維爾阿杜安以法文散文記述第四次十字軍如何在威尼斯操弄下偏離聖地、轉而攻陷拜占庭都城君士坦丁堡並建立拉丁帝國。作為決策圈中人，他的敘述既是史料也是辯解，為這場改變東西關係的事件留下當事人視角，是中世紀法文歷史散文的開山之作。' },
          { title_zh: '埃德薩的馬太編年', title_orig: 'Ժամանակագրութիւն (Zhamanakagrutʻiwn)', author: '馬太‧烏爾海耶齊，通稱埃德薩的馬太', era: '約1113至1140年', place: '埃德薩、基利家與北敘利亞', language: '古典亞美尼亞語', intro: '編年涵蓋十至十二世紀亞美尼亞、拜占庭、塞爾柱與早期十字軍諸國。作者身處埃德薩亞美尼亞社群，對法蘭克統治與東方基督徒處境多有批評，是十字軍時代的地方一手視角。' },
          { title_zh: '基利家小亞美尼亞王國編年', title_orig: 'Տարեգիրք Սմբատայ Սպարապետի (Taregirkʻ Smbatay Sparapeti)', author: '斯姆巴特‧斯帕拉佩特，或君士坦布爾斯姆巴特', era: '13世紀中後期', place: '基利家亞美尼亞王國', language: '中古亞美尼亞語', intro: '斯姆巴特為基利家王室重臣與統帥，編年敘及九五一至十三世紀事件，並保存王國外交資料。文本對亞美尼亞、十字軍、蒙古與近東諸勢力互動有高史料價值，宜列入十字軍編年脈絡。' },
          { title_zh: '攻取耶路撒冷法蘭克人史', title_orig: 'Historia Francorum qui ceperunt Iherusalem', author: '阿吉勒的雷蒙；巴拉宗的龐斯', era: '約1098–1105', place: '第一次十字軍行營、耶路撒冷', language: '拉丁文', intro: '普羅旺斯軍隨軍教士雷蒙所撰，記述安條克、聖槍發現與耶路撒冷陷落等事。其親歷性強，偏向圖盧茲伯爵陣營，能呈現第一次十字軍內部政治、末世想像與拉丁朝聖軍的自我理解。' },
          { title_zh: '耶路撒冷遠征史', title_orig: 'Historia Ierosolimitana', author: '亞琛的阿爾伯特', era: '約1100–1120年代', place: '亞琛、萊茵地區', language: '拉丁文', intro: '亞琛的阿爾伯特未親赴東方，卻蒐集歸來者口述，寫成十二卷第一次十字軍與早期耶路撒冷王國史。其材料保存洛林、下萊茵與民眾十字軍傳聞，補足南法與諾曼敘事之外的拉丁記憶。' },
          { title_zh: '坦克雷德事蹟', title_orig: 'Gesta Tancredi in expeditione Hierosolymitana', author: '卡昂的拉爾夫', era: '約1112–1118', place: '安條克、敘利亞北部', language: '拉丁文', intro: '卡昂的拉爾夫為博希蒙與坦克雷德陣營書寫的韻散混合史，聚焦基利家、安條克與諾曼領袖形象。作品雖具頌揚色彩，仍是研究拉丁東方初期安條克政權、拜占庭關係與騎士英雄敘事的重要文本。' },
          { title_zh: '安條克戰記', title_orig: 'Bella Antiochena', author: '書記官瓦爾特', era: '約1119–1122', place: '安條克公國', language: '拉丁文', intro: '安條克公國書記官瓦爾特記述1114至1122年間北敘利亞戰事，尤以血田之戰與羅傑之死最著名。其職官身分使文本接近拉丁東方行政核心，保存安條克在穆斯林諸政權夾擊下的危機經驗。' },
          { title_zh: '聖戰史', title_orig: 'L’Estoire de la guerre sainte', author: '安布魯瓦', era: '約1195年前後', place: '英格蘭、法語圈十字軍環境', language: '盎格魯-諾曼法語', intro: '安布魯瓦以盎格魯-諾曼詩體記述第三次十字軍，與理查王行程關係密切但可獨立成卷。作品保留從阿卡圍城到雅法和約的細節，展現隨軍文學、騎士忠誠與拉丁東方戰場的敘事節奏。' }
        ],
      },
      {
        key: 'dongfang-youji',
        label: '東方遊記部',
        label_en: 'Travels to the East',
        desc: '十三、十四世紀教廷與商旅出使蒙古與東方的報告與遊記。',
        works: [
          { title_zh: '蒙古史', title_orig: 'Historia Mongalorum', author: '柏郎嘉賓', era: '約 1247 年', place: '蒙古／教廷', language: '拉丁文', intro: '方濟各會士柏郎嘉賓奉教宗英諾森四世之命出使蒙古，行抵和林參加貴由汗即位大典，歸而撰成西歐第一份關於蒙古帝國的系統報告。書中詳述蒙古人的習俗、軍制與政教情形，意在為西方提供應對之策，是中古東西首次正式外交接觸的珍貴記錄。' },
          { title_zh: '東方行紀', title_orig: 'Itinerarium', author: '魯布魯克的威廉', era: '約 1255 年', place: '蒙古／聖地', language: '拉丁文', intro: '方濟各會士魯布魯克受法王路易九世遣往蒙古傳教與探查，覲見蒙哥汗，並在和林與聶斯托里派、伊斯蘭及佛教人士辯論。其行紀觀察細膩、態度誠實，記載漢字、佛教與東方地理多有卓識，被視為中世紀最出色的旅行報告之一，史地與宗教價值兼備。' },
          { title_zh: '馬可波羅遊記', title_orig: 'Il Milione / Le Devisement du Monde', author: '馬可‧波羅口述、魯斯蒂謙筆錄', era: '約 1298 年', place: '威尼斯／熱那亞獄中', language: '古法文', intro: '威尼斯商人馬可波羅自述其隨父叔東行、長居元朝忽必烈治下並遍歷亞洲的見聞，於熱那亞獄中由作家魯斯蒂謙筆錄成書。書中對東方財富、城市與物產的描述雖時有誇飾，卻極大激發了西歐對東方的想像與探索熱情，是中世紀東西交流史最著名的文本。' },
          { title_zh: '孟高維諾書信', title_orig: 'Epistolae Iohannis de Monte Corvino', author: '孟高維諾的若望', era: '約 1305–1306 年', place: '元朝大都', language: '拉丁文', intro: '方濟各會士孟高維諾奉教廷之命東來，於元大都建立天主教傳教據點並受任首位汗八里總主教，其自大都寄回的書信報告傳教成果、受洗人數與在華處境。這幾封信是天主教在中國最早的一手傳教記錄，雖屬書信體，因其史傳性的見聞報導價值而收入此部。' },
          { title_zh: '朝聖者行程與理查王事蹟', title_orig: 'Itinerarium Peregrinorum et Gesta Regis Ricardi', author: '聖殿的理查（傳歸）', era: '約1194–1220年代', place: '英格蘭、阿卡與巴勒斯坦材料', language: '拉丁文', intro: '第三次十字軍拉丁散文敘事，敘述薩拉丁攻勢、腓特烈遠征與英王理查在阿卡、阿爾蘇夫及海岸戰線的行動。它兼具行程錄與王業史性格，是研究1190年代聖地戰爭與英格蘭十字軍記憶的核心文本。' },
          { title_zh: '瑪爾雅巴拉哈與拉班掃馬行傳', title_orig: 'History of Mar Yahballaha III and Rabban Sauma', author: '佚名東方教會作者', era: '14世紀初，1317年後不久', place: '馬拉蓋、巴格達與伊兒汗國', language: '敘利亞語，含波斯語遊記材料', intro: '此傳敘述元代中國出身的馬可斯與拉班掃馬西行，並記掃馬出使拜占庭、羅馬、法國與英格蘭。它連接景教中國、伊兒汗蒙古與拉丁歐洲，是十字軍末期以東方教會視角觀察歐亞外交與旅行的罕見文本。' }
        ],
      },
    ],
  },
  wai: {
    summary: '基督教世界以外、與之共處或交鋒的史傳：伊斯蘭區的先知傳與通史、猶太社群的殉道與反傳記敘事，及異端領袖的傳記材料。',
    divisions: [
      {
        key: 'yisilan-shizhuan',
        label: '伊斯蘭史傳部',
        label_en: 'Islamic Histories and Biographies',
        desc: '伊斯蘭區的先知傳記、回憶錄與世界通史。',
        works: [
          { title_zh: '先知傳', title_orig: 'Sīrat Rasūl Allāh', author: '伊本‧伊斯哈格', era: '8 世紀', place: '阿拔斯王朝麥地那／巴格達', language: '阿拉伯文', intro: '伊本‧伊斯哈格所撰穆罕默德傳記，是伊斯蘭最早的系統先知傳，原本雖佚，經伊本‧希沙姆刪訂的版本流傳至今。書中按時序記述先知的家世、啟示、麥加受迫、遷徙麥地那與諸戰役，是穆斯林理解先知生平的根本文本，亦為研究伊斯蘭初興與七世紀阿拉伯社會的核心史料。' },
          { title_zh: '沉思錄', title_orig: 'Kitāb al-Iʿtibār', author: '烏薩瑪‧伊本‧蒙基德', era: '12 世紀', place: '敘利亞謝薩爾', language: '阿拉伯文', intro: '敘利亞貴族戰士烏薩瑪晚年所寫的回憶錄，記其一生征戰、狩獵與宮廷見聞，尤以與十字軍法蘭克人交往的軼事著稱。他以穆斯林眼光打量這些「外來蠻夷」的醫術、司法與習俗，語帶調侃而饒富人情，為十字軍時代東西方日常接觸提供了難得的對面視角，史料與文學趣味兼具。' },
          { title_zh: '歷代先知與帝王史', title_orig: 'Taʾrīkh al-Rusul wa-l-Mulūk', author: '塔巴里', era: '9–10 世紀', place: '阿拔斯王朝巴格達', language: '阿拉伯文', intro: '波斯裔學者塔巴里所撰自創世至其時代（約九一五年）的編年世界通史，卷帙浩繁。書中以「傳述鏈」逐條徵引史料，記先知、波斯薩珊諸王與伊斯蘭哈里發歷代，兼收歧異說法而並陳，是中古伊斯蘭史學的集大成之作，也是復原早期伊斯蘭史與前伊斯蘭近東史的首要文獻。' },
        ],
      },
      {
        key: 'youtai-shizhuan',
        label: '猶太史傳部',
        label_en: 'Jewish Histories and Counter-Narratives',
        desc: '中世紀猶太社群的殉道編年與民間反傳記敘事。',
        works: [
          { title_zh: '萊茵蘭殉道編年史', title_orig: 'Hebrew First Crusade Chronicles', author: '索羅門‧巴爾‧西孟等', era: '12 世紀', place: '萊茵蘭沃姆斯、美因茨', language: '希伯來文', intro: '第一次十字軍途經萊茵蘭時，沃姆斯、美因茨等地猶太社群慘遭屠戮，倖存者群體以希伯來文撰成數種殉道編年，記述受難經過與「為聖名而死」的集體自我犧牲。這些文本既是悲愴的歷史見證，也建構了猶太殉道神學的範式，從受害者一方為十字軍暴力留下控訴性的一手記錄。' },
          { title_zh: '耶穌生平傳奇', title_orig: 'Toledot Yeshu', author: '佚名（猶太民間傳述）', era: '中世紀（早期素材更古）', place: '近東與歐洲猶太社群', language: '希伯來文／阿拉米文', intro: '中世紀猶太社群間流傳的耶穌生平民間敘事，以戲謔顛覆的筆調反寫福音書情節，回應基督徒的傳教與論爭壓力。文本版本繁多、出自集體口傳而無定本，並非信史而屬論戰性的反傳記。它折射出中世紀猶太基督兩教在敵意環境中的角力，是宗教論戰史與民間文學研究的特殊材料。' },
        ],
      },
      {
        key: 'yiduan-lingxiu',
        label: '異端領袖傳部',
        label_en: 'Lives of Heresiarchs',
        desc: '被正統教會判為異端之運動及其領袖的傳記性記述（多出自反方之手）。',
        works: [
          { title_zh: '里昂窮人華爾多事蹟', title_orig: 'Acta de Valdesio et Pauperibus de Lugduno', author: '反華爾多派論者轉述', era: '12 世紀末–13 世紀', place: '里昂', language: '拉丁文', intro: '里昂富商華爾多約於一一七○年代散盡家財、追求使徒清貧並擅自宣講，興起「里昂窮人」運動，後被判異端。其生平與運動的記述多保存於教會審訊文書與反方編年中，史料立場敵對而需審辨。這些材料記錄了一場以平信徒宣道與貧窮理想挑戰教階體制的運動，是中古異端史的關鍵案例。' },
          { title_zh: '阿爾比派與其首領事蹟', title_orig: 'Historia Albigensis', author: '彼得‧德‧沃克塞納', era: '約 1213–1218 年', place: '法蘭西南部朗格多克', language: '拉丁文', intro: '熙篤會士彼得隨阿爾比十字軍南下，記述純潔派（卡特里派）異端在朗格多克的蔓延與征討此派的軍事行動。書中對純潔派領袖及其二元論教義的描述出自鎮壓一方，敵意鮮明，卻是了解這場異端運動及其首領、以及十字軍轉向基督教內部討伐的重要當代敘事，史料價值與偏見並存。' },
        ],
      },
    ],
  },
},
    {
  key: 'yijiao',
  name: '譯校藏',
  name_en: 'Translations and Textual Scholarship',
  glyph: '譯',
  genres: '譯本‧註疏‧考勘',
  summary: '收中世紀（約 800–1500）拉丁西方的聖經修訂與標準註釋、跨宗教的經典翻譯工程，以及他宗教經本在基督教世界的翻譯與流傳。正藏為基督宗教自身的聖經文本整理與其主持的跨宗教翻譯，外藏收猶太與其他傳統的經本及其中世紀傳本。此藏聚焦於文本的翻譯、校勘與註釋傳承，是中世紀知識跨語言、跨信仰流動的見證。',
  zheng: {
    summary: '基督宗教自身的拉丁聖經文本整理，以及由教會主持的跨宗教經典翻譯。',
    divisions: [
      {
        key: 'latin-bible-revision',
        label: '拉丁聖經修訂部',
        label_en: 'Latin Bible Revision',
        desc: '中世紀對通俗拉丁文聖經的校訂、標準註釋與章節劃分等文本工程。',
        works: [
          { title_zh: '巴黎聖經', title_orig: 'Biblia Parisiensia', author: '巴黎大學書坊（編訂群）', era: '約 1230', place: '巴黎', language: '拉丁文', intro: '巴黎聖經是十三世紀巴黎大學周邊書坊量產的通俗拉丁文聖經標準版，確立了沿用至今的聖經書卷次序、單卷一冊的便攜開本與統一的卷首語。它應大學師生與托缽修會傳教之需而生，使聖經文本趨於規格化與普及，是中世紀盛期書籍生產與經文標準化的里程碑。雖文本校勘未臻嚴謹，卻奠定了後世印刷聖經的基本面貌。' },
          { title_zh: '聖經章節劃分', title_orig: 'Capitula / Chapter Divisions of the Bible', author: '蘭頓的斯蒂芬（坎特伯里）', era: '約 1205', place: '巴黎／坎特伯里', language: '拉丁文', intro: '坎特伯里大主教蘭頓的斯蒂芬於巴黎執教時，為通俗拉丁文聖經制定了一套系統的章節劃分，便於教學、引證與檢索。此劃分隨巴黎聖經廣為流傳，成為西方各語言聖經沿用至今的標準章次（節的劃分則待十六世紀方告完備）。這項看似技術性的工程，深刻改變了聖經的閱讀、查考與註釋方式，是中世紀文本工具發展的關鍵成就。' },
          { title_zh: '武加大標準本聖經', title_orig: 'Biblia Sacra Vulgata', author: '耶柔米(Hieronymus)譯，阿爾琴(Alcuin)校訂', era: '原譯 4 世紀末‧加洛林校訂約 800', place: '伯利恆(原譯)‧圖爾(Tours，校訂)', language: '拉丁文', intro: '武加大為耶柔米於四世紀末自希伯來文與希臘文重譯校訂的拉丁聖經，至中世紀成為拉丁西方唯一通行的正典文本。卡爾大帝時代由阿爾琴在圖爾主導大規模校勘，清除抄本訛誤，形成加洛林標準本，奠定其後七百年西歐聖經的文字基礎。它不僅是禮儀、講道與神學論證的依據，其拉丁措辭更深刻塑造了中世紀的宗教語彙與思維，是整個拉丁基督教世界的根本經典。', link: '/scripture' },
          { title_zh: '通用註釋', title_orig: 'Glossa Ordinaria', author: '拉昂的安瑟莫(Anselm of Laon)學派', era: '約 1100–1130', place: '拉昂', language: '拉丁文', intro: '《通用註釋》是十二世紀以拉昂的安瑟莫學派為核心彙編而成的標準聖經註釋，將教父與前代權威的釋義摘錄編排於聖經正文的行間（行間註）與頁邊（邊註）。它成為中世紀經院課堂研讀聖經的基本範本，凡講授聖經必以此註為據。其版面形式——正文居中、註釋環繞——亦定義了中世紀註釋聖經的視覺傳統，是連結教父釋經與經院神學的關鍵橋梁。', link: '/fathers' },
          { title_zh: '彼得·隆巴德詩篇與保羅書信大註', title_orig: 'Magna Glosatura', author: '隆巴德(Petrus Lombardus)', era: '約 1140', place: '巴黎', language: '拉丁文', intro: '《大註》是隆巴德在《通用註釋》基礎上對詩篇與保羅書信所作的擴充註釋，廣納教父與當代見解並加以整理辨析，註文篇幅遠超舊註，故稱「大註」。它與其《四部語錄》同為十二世紀巴黎神學的奠基之作，使隆巴德被尊為「大師」(Magister)。此書是經院釋經由摘錄彙編走向系統思辨的代表，深刻影響後世對詩篇與保羅神學的理解。', link: '/fathers' },
          { title_zh: '狄奧多夫校訂本聖經', title_orig: 'Biblia Theodulfiana', author: '奧爾良的狄奧多夫', era: '約 800–818', place: '奧爾良／弗勒裡', language: '拉丁文', intro: '西哥德出身的奧爾良主教狄奧多夫與阿爾琴同時，主持另一系統的武加大校訂。他以學者手法在頁邊標注異文來源（西班牙本、阿爾昆本等），近乎近代校勘記的先聲；其袖珍細字的「狄奧多夫聖經」現存數部，是加洛林文藝復興聖經文本工程的雙璧之一，惜其批判方法後世未獲承續。' },
          { title_zh: '卡瓦聖經', title_orig: 'Codex Cavensis', author: '繕寫者但尼拉', era: '約 850', place: '西班牙（後藏南義卡瓦修道院）', language: '拉丁文', intro: '九世紀西班牙武加大名抄，由繕寫者但尼拉以西哥德小寫體繕成，後歸南義卡瓦修道院而得名。全帙保存西班牙型武加大文本傳統，並以藍染羊皮紙與十字形排版的裝飾頁著稱，是研究伊比利聖經文本與書藝的第一等見證，與阿米亞提努斯抄本並列武加大兩大權威抄本。' },
          { title_zh: '吉加斯抄本（魔鬼聖經）', title_orig: 'Codex Gigas', author: '波希米亞本篤會繕寫僧（佚名）', era: '約 1224–1230', place: '波希米亞波德拉日採修道院', language: '拉丁文', intro: '現存中世紀最巨大的抄本，高近一公尺，內含全部武加大聖經，另收約瑟夫斯、依西多祿《語源學》、編年史與醫學文獻，儼然一部單冊圖書館。因書中整頁魔鬼像而俗稱「魔鬼聖經」，傳說為一僧一夜繕成。三十年戰爭中被瑞典軍擄走，今藏斯德哥爾摩皇家圖書館。' },
          { title_zh: '多明我會聖經修正錄', title_orig: 'Correctorium Bibliae', author: '聖謝爾的休主持（道明會團隊）', era: '約 1236–1240', place: '巴黎聖雅各修道院', language: '拉丁文', intro: '十三世紀巴黎聖經文字訛誤氾濫，道明會士聖謝爾的休率聖雅各修道院團隊比對古抄本與希伯來、希臘原文，編成系統的「修正錄」，逐卷列出當讀異文。此為中世紀最早的大規模聖經校勘工程之一，雖以修正巴黎通行本為務，其方法已開近代經文考據之先河。' },
          { title_zh: '方濟會聖經修正錄', title_orig: 'Correctorium Vaticanum', author: '威廉‧德‧拉‧馬雷', era: '約 1266–1290', place: '巴黎／牛津', language: '拉丁文', intro: '方濟會士威廉‧德‧拉‧馬雷精研希伯來文與希臘文，所編修正錄（今稱「梵蒂岡修正錄」）以原文權衡拉丁異文，校勘水準冠絕當代諸家。羅傑‧培根雖痛詆巴黎修正諸家「敗壞聖經」，獨於此係評價較高，足見其嚴謹，是中世紀語文學臻於高峰的見證。' },
          { title_zh: '古騰堡四十二行聖經', title_orig: 'Biblia Latina (42-line Bible)', author: '約翰內斯‧古騰堡', era: '約 1454–1455', place: '美因茲', language: '拉丁文', intro: '西方第一部以活字印刷的大書，每頁四十二行，印行約一百八十部，文本承巴黎型武加大。它終結了千年手抄聖經的時代，使經文得以標準化大量複製，直接預備了人文主義校勘與宗教改革民族語聖經的浪潮。現存完帙不足五十部，被譽為印刷史與聖經傳播史的分水嶺。' },
          { title_zh: '三十六行聖經', title_orig: 'Biblia Latina (36-line Bible)', author: '古騰堡圈印工（或阿爾布雷希特‧菲斯特）', era: '約 1458–1460', place: '班貝格', language: '拉丁文', intro: '繼四十二行聖經之後印成的第二部活字拉丁聖經，每頁三十六行，用字為古騰堡早期字體，多認為在班貝格印竣。其文本抄自四十二行本的印本而非抄本，見證印刷文本自我繁衍的開端。存世僅十餘部，是搖籃本時代聖經印刷的重要環節。' }
        
        ]
      },
      {
        key: 'illuminated-bibles',
        label: '泥金聖經名抄部',
        label_en: 'Illuminated Bibles and Gospel Books',
        desc: '島嶼、加洛林、奧托、拜占庭、羅曼式與哥德式的聖經與福音名抄——中世紀聖經文本以書藝傳世的見證。',
        works: [
          { title_zh: '凱爾斯書', title_orig: 'Book of Kells', author: '愛奧那／凱爾斯修道院繕寫僧', era: '約 800', place: '愛奧那島／凱爾斯', language: '拉丁文', intro: '島嶼藝術的極致之作，四福音泥金抄本，飾以無窮迴旋的凱爾特結飾與人獸交纏的首字母，「基羅頁」尤稱絕唱。維京劫掠中自愛奧那轉移至愛爾蘭凱爾斯，今為都柏林三一學院鎮館之寶，其文本屬愛爾蘭型武加大，混有古拉丁讀法。' },
          { title_zh: '阿爾馬書', title_orig: 'Book of Armagh', author: '繕寫者費爾多姆納赫', era: '807–808', place: '阿爾馬', language: '拉丁文', intro: '愛爾蘭阿爾馬繕寫室所出的袖珍新約全書，兼收聖派翠克文獻與蘇爾比修的聖馬丁傳，是愛爾蘭現存最早近乎完整的新約文本。繕寫者費爾多姆納赫題記可考，其派翠克文獻為愛爾蘭教會史的根本史料，中世紀時被奉為聖髑般的權威。' },
          { title_zh: '麥克雷戈福音書', title_orig: 'MacRegol (Rushworth) Gospels', author: '繕寫者麥克雷戈', era: '約 800（古英語行間註約 950）', place: '伯爾（愛爾蘭）', language: '拉丁文（附古英語行間註）', intro: '愛爾蘭伯爾修道院院長麥克雷戈繕飾的四福音抄本，十世紀時由法爾曼與奧文兩位司鐸加註古英語行間直譯，成為古英語聖經翻譯的珍貴見證。抄本兼具島嶼裝飾藝術與雙語文本價值，今藏牛津博德利圖書館。' },
          { title_zh: '洛爾施福音書', title_orig: 'Lorsch Gospels', author: '亞琛宮廷書坊', era: '約 810', place: '亞琛', language: '拉丁文', intro: '卡爾大帝宮廷書坊所出的泥金福音書，以金墨書寫，附著名的象牙雕封面。其福音史家像承襲古典晚期風格，見證加洛林文藝復興「復興羅馬」的雄心。後藏洛爾施修道院，今分藏梵蒂岡與羅馬尼亞阿爾巴尤利亞，象牙封面別藏倫敦與梵蒂岡。' },
          { title_zh: '埃博福音書', title_orig: 'Ebbo Gospels', author: '蘭斯奧維萊爾修道院書坊', era: '約 816–835', place: '蘭斯', language: '拉丁文', intro: '蘭斯大主教埃博委製的福音書，其福音史家像以顫動的速寫式筆觸畫成，人物如受靈感震撼，一反古典靜穆，是加洛林「蘭斯畫派」表現風格的代表作，直接影響《烏得勒支詩篇》。今藏埃佩爾奈市立圖書館。' },
          { title_zh: '烏得勒支詩篇', title_orig: 'Utrecht Psalter', author: '蘭斯奧維萊爾修道院書坊', era: '約 820–835', place: '蘭斯', language: '拉丁文', intro: '以速寫鋼筆畫逐篇圖解全部詩篇的曠世抄本，每篇詩配一幅字面義的敘事群像，想像力縱橫。它在中世紀被三度臨摹於英格蘭，塑造盎格魯-撒克遜線描傳統；其「以圖釋經」的徹底性空前絕後，今藏烏得勒支大學圖書館，入選世界記憶名錄。' },
          { title_zh: '聖埃默拉姆金抄本', title_orig: 'Codex Aureus of St. Emmeram', author: '禿頭查理宮廷書坊', era: '870', place: '法蘭西西部（宮廷書坊）', language: '拉丁文', intro: '禿頭查理委製的純金墨福音書，鑲金浮雕寶石封面完好傳世，為加洛林金工與書藝合璧的極品。書中「查理坐像」與羔羊崇拜整頁畫氣象堂皇，後歸雷根斯堡聖埃默拉姆修道院，今藏慕尼黑巴伐利亞國家圖書館。' },
          { title_zh: '維維安聖經（禿頭查理第一聖經）', title_orig: 'Vivian Bible', author: '圖爾聖馬丁修道院書坊', era: '845–846', place: '圖爾', language: '拉丁文', intro: '圖爾聖馬丁修道院俗院長維維安伯爵獻給禿頭查理的單帙全本聖經，屬阿爾琴校訂系統的豪華本。卷首「獻書圖」為中世紀最早的當代事件敘事畫之一，另有耶柔米譯經事蹟整頁畫，把聖經文本工程本身入畫，堪稱武加大傳統的自我紀念碑。' },
          { title_zh: '穆捷-格朗瓦爾聖經', title_orig: 'Moutier-Grandval Bible', author: '圖爾聖馬丁修道院書坊', era: '約 830–840', place: '圖爾', language: '拉丁文', intro: '圖爾書坊為穆捷-格朗瓦爾修道院製作的全本聖經，四幅整頁敘事畫（創世、出埃及、威嚴基督、啟示錄）開創中世紀聖經卷首畫傳統。全帙四百餘葉大開本，體現阿爾琴校訂本的標準面貌，今藏大英圖書館。' },
          { title_zh: '聖保祿門外聖經', title_orig: 'Bible of San Paolo fuori le Mura', author: '蘭斯宮廷書坊', era: '約 870–875', place: '蘭斯', language: '拉丁文', intro: '禿頭查理委製、後贈羅馬的巨帙全本聖經，二十四幅整頁畫綜合圖爾與蘭斯畫派之長，敘事繁複華麗，是加洛林聖經插畫的集大成。千年來藏於羅馬城外聖保祿大殿，故名，是加洛林王權與教廷聯盟的圖像見證。' },
          { title_zh: '萊昂九六〇年聖經', title_orig: 'León Bible of 960', author: '繕寫者弗洛倫西奧與桑喬', era: '960', place: '萊昂王國瓦萊蘭尼卡修道院', language: '拉丁文', intro: '伊比利莫札拉布書藝的代表作，由師徒繕寫者弗洛倫西奧與桑喬完成，飾繪帶伊斯蘭裝飾母題的鮮明色塊人物，卷末師徒對酌的「奧米茄自畫像」尤為著名。其文本屬西班牙型武加大，今藏萊昂聖依西多祿皇家學院圖書館。' },
          { title_zh: '奧託三世福音書', title_orig: 'Gospels of Otto III', author: '賴興瑙修道院書坊', era: '約 998–1001', place: '賴興瑙島', language: '拉丁文', intro: '奧託王朝宮廷藝術的巔峰，皇帝奧託三世委製，四方民族向皇帝進貢的整頁畫與金地福音像莊嚴逼人。賴興瑙畫派以簡練金地與巨眼人物營造超越時空的神聖感，此本為其極致，今藏慕尼黑巴伐利亞國家圖書館，賴興瑙抄本群已入世界記憶名錄。' },
          { title_zh: '埃格伯特抄本', title_orig: 'Codex Egberti', author: '賴興瑙修道院書坊（格里高利大師等）', era: '約 980–993', place: '賴興瑙島', language: '拉丁文', intro: '特里爾大主教埃格伯特委製的福音經課本，五十餘幅基督生平敘事畫為現存最早成套的福音圖傳之一，「格里高利大師」的古典風格與賴興瑙書坊合作其間。它把經課文本與圖像敘事熔於一爐，今藏特里爾市立圖書館。' },
          { title_zh: '亨利二世經課福音選', title_orig: 'Pericopes of Henry II', author: '賴興瑙修道院書坊', era: '約 1007–1012', place: '賴興瑙島', language: '拉丁文', intro: '皇帝亨利二世獻給班貝格座堂的福音經課本，金地畫面剔除一切背景，人物姿態如禮儀般凝定，是奧託藝術「神聖抽象」的極致。鑲寶石象牙封面完好，今藏慕尼黑巴伐利亞國家圖書館，與帝國新設的班貝格主教座互為紀念。' },
          { title_zh: '班貝格啟示錄', title_orig: 'Bamberg Apocalypse', author: '賴興瑙修道院書坊', era: '約 1000–1020', place: '賴興瑙島', language: '拉丁文', intro: '現存唯一的奧託時代整頁畫啟示錄抄本，五十七幅金地畫面把約翰異象化為凝重的末世劇場，成於千禧年前後的末世氛圍中。附福音經課，為亨利二世所贈班貝格座堂舊藏，今藏班貝格國家圖書館，入選世界記憶名錄。' },
          { title_zh: '赫盧多夫詩篇', title_orig: 'Khludov Psalter', author: '君士坦丁堡繕寫室', era: '約 850', place: '君士坦丁堡', language: '希臘文', intro: '破像爭議甫息後成書的拜占庭「邊註詩篇」，頁邊小畫屢以塗抹聖像者影射破像派，將時事論戰畫入經卷，是聖像神學勝利的圖像宣言。此類九世紀邊註詩篇存世僅三部，赫盧多夫本最著，今藏莫斯科國家歷史博物館。' },
          { title_zh: '巴黎詩篇（拜占庭泥金抄本）', title_orig: 'Paris Psalter (BnF gr. 139)', author: '君士坦丁堡宮廷書坊', era: '10 世紀中', place: '君士坦丁堡', language: '希臘文', intro: '馬其頓文藝復興的代表作，十四幅整頁畫古典氣息濃鬱，大衛彈琴圖中擬人化的「旋律」女神儼然古希臘壁畫再世。它證明拜占庭宮廷藝術對古典傳統的自覺回歸，與同期文人復興互相呼應，今藏法國國家圖書館。' },
          { title_zh: '狄奧多爾詩篇', title_orig: 'Theodore Psalter', author: '修士狄奧多爾（斯圖狄奧斯修道院）', era: '1066', place: '君士坦丁堡', language: '希臘文', intro: '斯圖狄奧斯修道院修士狄奧多爾為院長繕飾的邊註詩篇，四百餘幅邊畫承赫盧多夫傳統而益加繁密，兼含修道生活與聖徒圖像，是拜占庭中期修道文化的圖像百科，今藏大英圖書館。' },
          { title_zh: '斯塔沃洛聖經', title_orig: 'Stavelot Bible', author: '斯塔沃洛修道院書坊', era: '1093–1097', place: '斯塔沃洛（默茲河谷）', language: '拉丁文', intro: '默茲羅曼式書藝的奠基之作，兩卷本巨帙聖經，「威嚴基督」整頁畫融合拜占庭莊嚴與默茲金工的立體感。題記留下繕寫僧四年勞作的自述，為中世紀書籍生產的珍貴自證，今藏大英圖書館。' },
          { title_zh: '伯裡聖經', title_orig: 'Bury Bible', author: '畫師胡戈', era: '約 1135', place: '伯裡聖埃德蒙茲修道院', language: '拉丁文', intro: '英格蘭羅曼式聖經的開山之作，職業畫師胡戈受僱為修道院繪製，濕潤厚重的「拜占庭化」人物開十二世紀英格蘭大聖經傳統之先。胡戈為文獻可考的最早英格蘭職業書畫師之一，此本今藏劍橋基督聖體學院帕克圖書館。' },
          { title_zh: '溫徹斯特聖經', title_orig: 'Winchester Bible', author: '溫徹斯特座堂繕寫室（多位畫師）', era: '約 1150–1175', place: '溫徹斯特', language: '拉丁文', intro: '英格蘭最大的羅曼式泥金聖經，六位風格可辨的畫師先後參與，歷數十年未竟全功，首字母畫自「跳躍人物大師」至「拜占庭化大師」的風格演變一目瞭然，是十二世紀英格蘭繪畫的活教科書，至今仍藏溫徹斯特座堂。' },
          { title_zh: '梅利桑德詩篇', title_orig: 'Melisende Psalter', author: '耶路撒冷聖墓繕寫室', era: '約 1131–1143', place: '耶路撒冷', language: '拉丁文', intro: '耶路撒冷王后梅利桑德的私人詩篇，拜占庭風格畫師與拉丁繕寫者合作，象牙雕封面出東方工匠之手，是十字軍東方「文化混血」藝術的最佳標本。王后為亞美尼亞裔母親所出，抄本本身即跨傳統聯姻的縮影，今藏大英圖書館。' },
          { title_zh: '摩根十字軍聖經', title_orig: 'Morgan (Maciejowski) Bible', author: '巴黎宮廷畫坊', era: '約 1240–1250', place: '巴黎', language: '拉丁文（後加波斯文與猶太-波斯文題記）', intro: '路易九世宮廷所出的舊約圖傳聖經，以十三世紀騎士裝束重演舊約戰陣，寫實而血腥，冠絕中世紀敘事畫。後由教廷使團贈波斯沙阿，遞經波斯文、猶太-波斯文題記層層累積，一部抄本身歷三大宗教世界，今藏紐約摩根圖書館。' },
          { title_zh: '道德化聖經', title_orig: 'Bible moralisée', author: '巴黎宮廷畫坊', era: '約 1220–1240', place: '巴黎', language: '拉丁文／古法文', intro: '法蘭西王室委製的圖解聖經，每頁八枚圓形畫對照經文與道德寓意，全帙動輒五千幅，造價驚人，僅王室能致。其寓意畫兼涉時政，反猶圖像亦多，是十三世紀王權神學與社會心態的圖像總集，存世數部分藏維也納、巴黎、託萊多等地。' },
          { title_zh: '貧民聖經', title_orig: 'Biblia pauperum', author: '尼德蘭／德意志木版印坊', era: '15 世紀中', place: '尼德蘭／萊茵蘭', language: '拉丁文', intro: '以「預表法」編排的圖解聖經：每幅新約場景左右各配舊約預表與先知半身像，先以抄本流傳，十五世紀中葉改以整頁木版印行，成為最流行的木版書。它把救恩史的類型學壓縮為圖表，是中世紀晚期平信徒虔敬與印刷革命交會的標本。' },
          { title_zh: '霍克漢圖畫聖經', title_orig: 'Holkham Bible Picture Book', author: '倫敦畫坊', era: '約 1327–1335', place: '倫敦', language: '盎格魯-諾曼法文', intro: '以二百三十餘幅圖畫敘述創世至末日的圖畫書，附盎格魯-諾曼法文解說，開卷即繪道明會士囑畫師「為富貴人好生作畫」，自道其受眾。它見證中世紀晚期以圖像與俗語向平信徒傳達聖經的潮流，今藏大英圖書館。' }
        
        ]
      },
      {
        key: 'eastern-versions',
        label: '東方譯本與抄本部',
        label_en: 'Eastern Versions and Manuscripts',
        desc: '敘利亞、阿拉伯、亞美尼亞、喬治亞、衣索比亞、波斯與中亞絲路諸語的中世紀聖經譯本、修訂與名抄。',
        works: [
          { title_zh: '敘利亞馬所拉抄本', title_orig: 'Syriac Masora (Qarqaphta tradition)', author: '卡爾卡夫塔修道院傳統', era: '9–11 世紀', place: '敘利亞西部', language: '敘利亞文', intro: '敘利亞正教會卡爾卡夫塔修道院傳統所編的「馬所拉」式抄本，逐卷輯錄聖經難詞的標音、讀法與註記，規範別西大及哈爾克版的誦讀。它與猶太馬所拉平行發展，是敘利亞語文學自覺整理聖經文本的見證，存世抄本以大英圖書館與巴黎所藏最著。' },
          { title_zh: '布坎南聖經', title_orig: 'Buchanan Bible', author: '敘利亞正教繕寫僧', era: '12 世紀', place: '美索不達米亞（後傳南印度馬拉巴）', language: '敘利亞文', intro: '十二世紀繕成的別西大舊約全帙，後世流入南印度馬拉巴的聖多馬基督徒社群，一八〇六年由克勞狄烏斯‧布坎南攜歸劍橋，故名。它兼證別西大文本的中世紀傳承與敘利亞基督教沿印度洋的傳播網絡，今藏劍橋大學圖書館。' },
          { title_zh: '西奈阿拉伯抄本一五一號', title_orig: 'Mt. Sinai Arabic Codex 151', author: '比什爾‧伊本‧西里（譯註）', era: '867', place: '大馬士革', language: '阿拉伯文', intro: '現存最早有紀年的阿拉伯文聖經譯本之一，八六七年比什爾‧伊本‧西里於大馬士革自敘利亞文譯出保羅書信並附註釋，後續補行傳與大公書信。譯者為東方基督徒，行文已用伊斯蘭化的宗教語彙，見證阿拉伯化進程中的教會如何以新語言承載聖經，抄本藏西奈聖凱瑟琳修道院。' },
          { title_zh: '哈夫斯‧伊本‧阿爾巴爾阿拉伯韻文詩篇', title_orig: 'Kitāb al-Zubūr (urjūza Psalter)', author: '哈夫斯‧伊本‧阿爾巴爾', era: '889', place: '哥多華', language: '阿拉伯文', intro: '哥多華莫札拉布法官哈夫斯把拉丁詩篇譯成阿拉伯「拉賈茲」韻文，序言申明譯經之法，兼顧達意與可誦。此譯本是安達魯斯基督徒阿拉伯化的里程碑，連穆斯林學者亦見徵引，存世孤本藏米蘭盎博羅削圖書館。' },
          { title_zh: '伊本‧巴拉斯克福音譯本', title_orig: 'Evangelia (Isḥāq ibn Balashk al-Qurṭubī)', author: '伊斯哈格‧伊本‧巴拉斯克', era: '946', place: '哥多華', language: '阿拉伯文', intro: '哥多華基督徒伊斯哈格‧伊本‧巴拉斯克自拉丁文譯出的四福音，是安達魯斯阿拉伯語福音書的主流版本，存世抄本自成一系。其譯文按拉丁教會經課劃分段落，兼採伊斯蘭語彙，為研究莫札拉布社群語言轉換與禮儀生活的第一手文獻。' },
          { title_zh: '伊本‧阿薩爾福音校譯本', title_orig: 'al-As\'ad ibn al-\'Assāl, Gospel recension', author: '阿薩德‧伊本‧阿薩爾', era: '1253', place: '開羅', language: '阿拉伯文', intro: '科普特教會阿薩爾家族三傑之一阿薩德據科普特、希臘、敘利亞諸本互校，重譯四福音為阿拉伯文並附校勘記，標明異文出處，方法之嚴謹為中世紀東方所僅見。此「校勘譯本」雖後世流通不敵通俗本，卻是阿拉伯聖經文本學的高峰。' },
          { title_zh: '姆爾凱王后福音書', title_orig: 'Queen Mlk\'e Gospels', author: '亞美尼亞繕寫僧', era: '862', place: '亞美尼亞', language: '亞美尼亞文', intro: '現存最古有紀年的亞美尼亞福音抄本，因後歸瓦斯普拉坎王后姆爾凱而得名。卷首泥金頁承晚期古典風格，文本屬亞美尼亞譯本古層，為五世紀梅斯羅布譯經傳統的最早完整見證之一，今藏威尼斯聖拉撒路島梅希塔爾修道院。' },
          { title_zh: '埃奇米阿津福音書', title_orig: 'Etchmiadzin Gospels', author: '亞美尼亞繕寫僧', era: '989', place: '亞美尼亞', language: '亞美尼亞文', intro: '九八九年繕成的亞美尼亞福音書，卷末附四葉六至七世紀的古畫頁，六世紀象牙雕封面尤為國寶。其文本與插畫保存亞美尼亞譯經傳統的最古面貌，「埃奇米阿津式」構圖成為後世範本，今藏葉裡溫馬泰納達蘭古抄本館。' },
          { title_zh: '託羅斯‧羅斯林福音書群', title_orig: 'T\'oros Roslin Gospels', author: '託羅斯‧羅斯林', era: '1256–1268', place: '基利家赫羅姆克拉', language: '亞美尼亞文', intro: '基利家亞美尼亞王國宮廷畫師託羅斯‧羅斯林署名的七部福音抄本，把拜占庭古典人體、西方哥德式敘事與亞美尼亞裝飾傳統熔於一爐，敘事場景空前豐富。羅斯林為中世紀東方少數留名的畫師，作品今分藏耶路撒冷亞美尼亞宗主教區與華府弗利爾美術館等地。' },
          { title_zh: '基利家亞美尼亞聖經修訂本', title_orig: 'Cilician recension of the Armenian Bible', author: '蘭布倫的聶爾謝斯等', era: '12–13 世紀', place: '基利家', language: '亞美尼亞文', intro: '基利家王國時代學者（以蘭布倫的聶爾謝斯為著）對亞美尼亞聖經的系統修訂，據希臘本補正舊譯、增補章節劃分，形成後世通行的「基利家型」文本。十三世紀後的多數亞美尼亞聖經抄本皆承此係，是亞美尼亞文本史的分水嶺。' },
          { title_zh: '阿迪希福音書', title_orig: 'Adishi Gospels', author: '修士米卡埃爾', era: '897', place: '沙特貝爾迪修道院（塔奧-克拉爾傑季）', language: '喬治亞文', intro: '現存最古的喬治亞福音全帙，八九七年於沙特貝爾迪修道院繕成，後藏斯瓦內季亞的阿迪希村而得名。其文本保存喬治亞古譯層次，為喬治亞語聖經文本史的基準點，今藏梅斯蒂亞博物館。' },
          { title_zh: '吉魯奇第一福音書', title_orig: 'First Jruchi Gospels', author: '沙特貝爾迪書坊', era: '936–940', place: '塔奧-克拉爾傑季', language: '喬治亞文', intro: '十世紀喬治亞書藝黃金期的福音抄本，出沙特貝爾迪書坊，泥金頁融拜占庭與本土母題於一體。與阿迪希本同為喬治亞舊譯文本的柱石，今藏第比利斯喬治亞國家古抄本中心。' },
          { title_zh: '阿索斯喬治亞校訂本', title_orig: 'Athonite Georgian recension', author: '聖山的猶特米與喬治', era: '10 世紀末–11 世紀中', place: '阿索斯伊維隆修道院', language: '喬治亞文', intro: '阿索斯聖山伊維隆修道院的猶特米與「聖山人」喬治兩代學僧，據希臘標準本系統重譯校訂喬治亞新約與詩篇，形成沿用至今的「阿索斯定本」。喬治並自道其校勘原則，是喬治亞教會文本統一的完成者，譯業兼及大量教父著作。' },
          { title_zh: '澤爾‧加內拉福音書', title_orig: 'Zir Ganela Gospels', author: '衣索比亞繕寫僧（澤爾‧加內拉公主委製）', era: '1400–1401', place: '衣索比亞', language: '吉茲文', intro: '皇孫女澤爾‧加內拉為其出任院長的修道院委製的吉茲文四福音，附二十六幅整頁畫與飾框對觀表，卷末紀年題記完整。委製者為出家的皇室女性，抄本兼證所羅門王朝的宮廷虔敬與女性修道領導，今藏紐約摩根圖書館。' },
          { title_zh: '克布蘭福音書', title_orig: 'Kebran Gospels', author: '克布蘭加百列修道院繕寫僧', era: '約 1375–1400', place: '塔納湖克布蘭島', language: '吉茲文', intro: '塔納湖克布蘭加百列修道院珍藏的泥金福音書，成於所羅門王朝復興期，插畫以熱烈色彩重述基督生平，是衣索比亞高原修道書藝的代表。塔納湖諸島修道院於戰亂中守護帝國典籍，此本即其書庫之冠。' },
          { title_zh: '波斯語四福音合參', title_orig: 'Persian Diatessaron', author: '佚名東方教會譯者', era: '13–14 世紀', place: '大不里士一帶', language: '波斯文', intro: '中世紀波斯語的四福音合參譯本，序言自稱譯自敘利亞文，十六世紀抄本傳世，今藏佛羅倫斯勞倫斯圖書館。它是塔提安合參傳統在伊利汗國時代的迴響，兼為新波斯語基督教文獻的少數大部頭之一，見證蒙古治下東方教會的短暫復興。' },
          { title_zh: '粟特語福音經課殘卷', title_orig: 'Sogdian Gospel Lectionary (Bulayïq)', author: '東方教會布拉伊克修道院', era: '9–11 世紀', place: '吐魯番布拉伊克', language: '粟特文', intro: '德國吐魯番探險隊於布拉伊克修道院遺址所獲的粟特語福音經課殘卷，以敘利亞字母書寫，自別西大譯出，按東方教會禮儀年編排。它證明粟特語曾是絲路教會的禮儀與研讀語言，今藏柏林吐魯番特藏。' },
          { title_zh: '粟特語詩篇殘卷', title_orig: 'Sogdian Psalter', author: '東方教會布拉伊克修道院', era: '9–11 世紀', place: '吐魯番布拉伊克', language: '粟特文', intro: '布拉伊克出土的粟特語詩篇殘葉，部分附敘利亞語首行對照，顯示雙語誦讀之制。詩篇為修道日課核心，此殘卷與敘利亞語、中古波斯語詩篇同出一寺，並證吐魯番教團的多語靈修生活，今藏柏林。' },
          { title_zh: '回鶻語景教文獻殘卷', title_orig: 'Old Uyghur Christian fragments', author: '東方教會回鶻信眾', era: '9–14 世紀', place: '吐魯番／敦煌', language: '回鶻文', intro: '吐魯番與敦煌所出的回鶻語基督教殘卷，內容含聖喬治受難記、婚禮祝文與禮儀殘篇，多以敘利亞字母或回鶻字母書寫。它們見證突厥語族皈依東方教會的縱深，是景教在中亞最後數世紀的直接遺存，今分藏柏林等地。' }
        
        ]
      },
      {
        key: 'slavonic-versions',
        label: '斯拉夫譯經部',
        label_en: 'Slavonic Bible Tradition',
        desc: '西里爾與美多德以降的教會斯拉夫語譯經傳統：格拉哥里與西里爾字母諸抄本，迄於根納季全本聖經。',
        works: [
          { title_zh: '西里爾與美多德斯拉夫譯經', title_orig: 'Versio Palaeoslavica', author: '西里爾與美多德兄弟', era: '863–885', place: '大摩拉維亞／潘諾尼亞', language: '教會斯拉夫文', intro: '帖撒羅尼迦兄弟西里爾與美多德應大摩拉維亞之請，創制格拉哥里字母，把福音書、詩篇、使徒經課與禮儀譯成古教會斯拉夫語，奠定斯拉夫文字與文學的開端；美多德晚年續譯聖經大部。此譯業使斯拉夫諸族以母語領受聖道，兄弟倆被尊為「斯拉夫人的宗徒」，其譯文傳統至今仍活在正教會禮儀中。' },
          { title_zh: '佐格拉福福音抄本', title_orig: 'Codex Zographensis', author: '佚名抄經僧', era: '10 世紀末–11 世紀初', place: '保加利亞（後藏阿索斯佐格拉福修道院）', language: '教會斯拉夫文', intro: '以格拉哥里字母繕寫的四福音抄本，因藏於阿索斯聖山佐格拉福修道院而得名，今存聖彼得堡。其文本忠實保存西里爾與美多德譯文的古貌，是古教會斯拉夫語正典文獻的核心見證之一，於斯拉夫語文學與聖經文本史均屬第一等史料。' },
          { title_zh: '馬利亞福音抄本', title_orig: 'Codex Marianus', author: '佚名抄經僧', era: '11 世紀初', place: '馬其頓地區（後藏阿索斯聖母修道院）', language: '教會斯拉夫文', intro: '格拉哥里字母四福音抄本，得名於阿索斯聖山「聖母」修道院。文本屬古教會斯拉夫語最古層，兼帶塞爾維亞語音特徵，為斯拉夫聖經文本譜系的關鍵環節，今主體藏莫斯科俄羅斯國家圖書館，部分葉片藏維也納。' },
          { title_zh: '阿塞馬尼福音抄本', title_orig: 'Codex Assemanius', author: '佚名抄經僧', era: '11 世紀', place: '奧赫裡德文書圈', language: '教會斯拉夫文', intro: '格拉哥里字母的節選福音經課本，十八世紀由東方學家阿塞馬尼購自耶路撒冷而得名，今藏梵蒂岡圖書館。除經文外並附斯拉夫最早的曆書聖人紀念，兼具文本史與禮儀史價值，是奧赫裡德書寫傳統的代表作。' },
          { title_zh: '薩瓦之書', title_orig: 'Savvina Kniga', author: '修士薩瓦（署名）', era: '11 世紀', place: '保加利亞東部', language: '教會斯拉夫文', intro: '以西里爾字母繕寫的福音經課本，因書中兩處「修士薩瓦」題記而得名，今藏莫斯科。其語言保存古保加利亞語古態，是最早的西里爾字母聖經抄本之一，與格拉哥里諸抄本互證西里爾與美多德譯文的原貌。' },
          { title_zh: '西奈斯拉夫詩篇', title_orig: 'Psalterium Sinaiticum', author: '佚名抄經僧', era: '11 世紀', place: '保加利亞／馬其頓（藏西奈聖凱瑟琳修道院）', language: '教會斯拉夫文', intro: '現存最古的教會斯拉夫語詩篇抄本，以格拉哥里字母繕寫，藏於西奈聖凱瑟琳修道院。詩篇為斯拉夫初譯的核心經卷，此抄本保存美多德團隊譯文的最古層次，兼含禱文附錄，是斯拉夫語文學與禮儀史的無價之寶。' },
          { title_zh: '奧斯特羅米爾福音書', title_orig: 'Ostromir Gospels', author: '執事格里高利（繕寫）', era: '1056–1057', place: '諾夫哥羅德', language: '教會斯拉夫文', intro: '現存最古有明確紀年的東斯拉夫書籍，由執事格里高利為諾夫哥羅德總督奧斯特羅米爾繕成，屬節選福音經課本，泥金裝飾華美。其題記明確繫年，成為俄語文獻學的起點座標；文本兼證西里爾與美多德譯文在羅斯的承傳，今藏聖彼得堡俄羅斯國家圖書館。' },
          { title_zh: '阿爾漢格爾斯克福音書', title_orig: 'Arkhangelsk Gospel', author: '佚名抄經僧', era: '1092', place: '基輔羅斯', language: '教會斯拉夫文', intro: '基輔羅斯時期的福音經課本，一〇九二年繕成，因十九世紀發現於阿爾漢格爾斯克附近而得名。其樸素的書寫與奧斯特羅米爾本的華麗形成對照，見證聖經抄本在羅斯的日常流通層面，一九九七年入選聯合國教科文組織世界記憶名錄。' },
          { title_zh: '姆斯季斯拉夫福音書', title_orig: 'Mstislav Gospels', author: '繕寫者阿列克薩', era: '約 1103–1117', place: '諾夫哥羅德', language: '教會斯拉夫文', intro: '諾夫哥羅德王公姆斯季斯拉夫委製的節選福音經課本，由阿列克薩繕寫，飾以拜占庭風格泥金與珠寶封面。它是羅斯王室虔敬與書藝的頂峰之作，文本上與奧斯特羅米爾本同屬經課系統，為東斯拉夫聖經傳統的權威見證。' },
          { title_zh: '米羅斯拉夫福音書', title_orig: 'Miroslav Gospels', author: '繕寫者格里高利等', era: '約 1180', place: '塞爾維亞扎胡姆列', language: '教會斯拉夫文', intro: '塞爾維亞王公米羅斯拉夫委製的福音經課本，融合拜占庭泥金與羅曼式裝飾母題，是塞爾維亞語書寫傳統現存最古的代表作。其三百餘幅飾繪為巴爾幹書藝之冠，二〇〇五年入選世界記憶名錄，今藏貝爾格勒國家博物館。' },
          { title_zh: '伊凡‧亞歷山大沙皇四福音書', title_orig: 'Tetraevangelia of Ivan Alexander', author: '修士西蒙（繕寫）', era: '1355–1356', place: '大特爾諾沃', language: '教會斯拉夫文', intro: '保加利亞沙皇伊凡‧亞歷山大委製的四福音抄本，附三百六十六幅細密畫，含沙皇全家肖像，是第二保加利亞帝國藝術的巔峰。鄂圖曼征服後輾轉至阿索斯、摩爾達維亞，終入大英圖書館。其文本代表特爾諾沃書派修訂的斯拉夫福音定本。' },
          { title_zh: '根納季聖經', title_orig: 'Gennady Bible', author: '諾夫哥羅德大主教根納季主持', era: '1499', place: '諾夫哥羅德', language: '教會斯拉夫文', intro: '東斯拉夫世界第一部集為單帙的全本聖經，由大主教根納季為對抗「猶太化派」異端而主持編成；缺卷自武加大補譯，譯者含通曉拉丁文的修士。它總結中世紀斯拉夫譯經傳統，直接成為一五八一年奧斯特羅格印本聖經的底本，影響及於今日俄語正教會經文。' }
        
        ]
      },
      {
        key: 'vernacular-versions',
        label: '民族語譯本部',
        label_en: 'Vernacular Versions',
        desc: '日耳曼、英語、羅曼、斯拉夫西支、匈牙利與北歐諸民族語的中世紀聖經翻譯，兼及最早的俗語印刷聖經。',
        works: [
          { title_zh: '古高地德語塔提安合參', title_orig: 'Althochdeutscher Tatian', author: '富爾達修道院譯者群', era: '約 830', place: '富爾達', language: '古高地德語', intro: '富爾達修道院據拉丁文四福音合參譯成的古高地德語對照本，拉丁、德語左右並列，是古高地德語散文最重要的紀念碑。譯業出於拉巴努斯‧毛魯斯時代的教育雄心，為日耳曼語聖經翻譯的開端，主要抄本今藏聖加侖修道院圖書館。' },
          { title_zh: '威塞克斯福音書', title_orig: 'Wessex Gospels', author: '佚名西撒克遜譯者', era: '約 990', place: '英格蘭西南部', language: '古英語', intro: '四福音的完整古英語翻譯，不依附拉丁行間註而獨立成篇，是英語史上第一部完整福音譯本。存世七部抄本顯示其流通之廣，諾曼征服後仍被抄寫，至宗教改革時代被援為「英人自古有英語聖經」之證。' },
          { title_zh: '古英語六經', title_orig: 'Old English Hexateuch', author: '艾爾弗裡克等', era: '約 1000', place: '英格蘭', language: '古英語', intro: '修道院長艾爾弗裡克與佚名譯者合力把摩西五經與約書亞記譯為古英語，倫敦藏彩繪本附四百餘幅插畫，為英語舊約翻譯之始。艾爾弗裡克於序言坦陳對俗人誤讀律法的疑慮，此序成為中世紀翻譯理論的名篇。' },
          { title_zh: '古英語詩篇（阿爾弗雷德王譯）', title_orig: 'Old English (Paris) Psalter', author: '傳阿爾弗雷德大王（前五十篇散文）', era: '9 世紀末–11 世紀', place: '威塞克斯', language: '古英語', intro: '前五十篇散文譯文傳出阿爾弗雷德大王之手，餘篇以古英語韻文補足，合帙存於今稱「巴黎詩篇」的十一世紀抄本。它是英語詩篇翻譯的源頭，散文部分平易而重意譯，見證阿爾弗雷德「以英語興學」的王政理想。' },
          { title_zh: '威克里夫聖經（前期本）', title_orig: 'Wycliffite Bible, Early Version', author: '威克里夫學圈（赫裡福德的尼古拉等）', era: '約 1382–1384', place: '牛津', language: '中古英語', intro: '威克里夫倡議、其牛津門人執譯的第一部完整英語聖經，逐字直譯武加大，拉丁語序斑斑可見。它把「聖經置於凡人之手」的主張化為文本實踐，遭教會禁絕而抄傳不輟，是宗教改革前英語世界最大規模的地下書籍運動。' },
          { title_zh: '威克里夫聖經（後期修訂本）', title_orig: 'Wycliffite Bible, Later Version', author: '約翰‧珀維（主修）', era: '約 1388–1395', place: '英格蘭', language: '中古英語', intro: '威克里夫門人珀維主持的全面修訂本，改逐字直譯為順暢英語，並冠以申論翻譯原則的「總序」。存世抄本逾二百五十部，遠超任何中世紀英語作品，雖經一四〇九年禁令仍廣傳，直接滋養了廷代爾以降的英譯傳統。' },
          { title_zh: '十三世紀古法語聖經', title_orig: 'Bible du XIIIe siècle', author: '巴黎大學圈譯者群', era: '約 1220–1260', place: '巴黎', language: '古法語', intro: '第一部完整的法語散文聖經，出十三世紀巴黎，據巴黎型武加大譯成並雜採《通用註釋》。它突破教會對俗語聖經的疑慮，成為後世法語聖經（含與《歷史聖經》的合流本）的母本，見證法語作為神學俗語的崛起。' },
          { title_zh: '歷史聖經', title_orig: 'Bible historiale', author: '吉亞爾‧德‧穆蘭', era: '1291–1295', place: '法蘭西北部埃爾', language: '古法語', intro: '司鐸吉亞爾‧德‧穆蘭把科梅斯托的《經院史》與聖經敘事熔鑄為法語「歷史聖經」，經文與史釋相間，後與十三世紀聖經合流為「大歷史聖經」，成為中世紀晚期法語世界最流行的聖經形態，王室貴族藏本動輒泥金巨帙。' },
          { title_zh: '瓦勒度派羅曼語譯本', title_orig: 'Waldensian Romance New Testament', author: '瓦勒度派巴爾伯（遊方師傅）', era: '13–15 世紀', place: '皮德蒙阿爾卑斯山谷', language: '古奧克語（瓦勒度方言）', intro: '瓦勒度派以奧克語系方言傳抄的新約與訓道文本，袖珍抄本便於遊方師傅藏於衣襟。里昂的華爾多倡俗語聖經而遭絕罰，其派山谷社群卻把譯本傳承三百年，直至宗教改革時代獻藏本於改革宗，是俗語聖經運動最堅韌的血脈。' },
          { title_zh: '阿方索聖經（總史聖經）', title_orig: 'General estoria (Biblia alfonsina)', author: '阿方索十世宮廷編譯團', era: '約 1270–1284', place: '託萊多／塞維亞', language: '卡斯提爾語', intro: '「智者」阿方索十世宮廷把聖經敘事譯入其未竟的世界通史《總史》，據武加大並參猶太譯註譯成，是卡斯提爾語散文聖經的開端。王廷以俗語治學的雄心使聖經進入伊比利王室史學，孕育後世西班牙語聖經傳統。' },
          { title_zh: '阿爾巴聖經', title_orig: 'Alba Bible', author: '拉比摩西‧阿拉格爾', era: '1422–1430', place: '卡斯提爾馬克達', language: '卡斯提爾語', intro: '卡拉特拉瓦騎士團長委託拉比摩西‧阿拉格爾自希伯來原文譯出的卡斯提爾語舊約，附拉比與基督教雙重註釋及三百餘幅插畫，成書過程的往來書信俱存。猶太學者為基督徒貴族譯經，是驅逐前夕伊比利跨信仰合作的絕響。' },
          { title_zh: '瓦倫西亞聖經', title_orig: 'Bíblia Valenciana', author: '博尼法奇‧費雷爾', era: '1478 印行（譯於 15 世紀初）', place: '瓦倫西亞', language: '加泰隆尼亞語（瓦倫西亞語）', intro: '加爾都西會士博尼法奇‧費雷爾（聖文生‧費雷爾之兄）所譯聖經，一四七八年於瓦倫西亞印行，為伊比利半島第一部印刷俗語全本聖經。宗教裁判所旋即查禁焚毀，今僅存末葉孤紙，成為西班牙俗語聖經受難史的象徵。' },
          { title_zh: '德勒斯登聖經', title_orig: 'Dresden (Leskovec) Bible', author: '佚名波希米亞譯者群', era: '約 1360', place: '布拉格', language: '捷克語', intro: '最古的完整捷克語聖經，約一三六〇年譯成，證明捷克語為歐洲最早擁有全本聖經的俗語之一。原抄本一九一四年毀於大戰戰火，僅存照片與部分轉錄，其譯文為胡斯運動前捷克聖經文化深厚的鐵證。' },
          { title_zh: '布拉格聖經', title_orig: 'Prague Bible', author: '布拉格印坊', era: '1488', place: '布拉格', language: '捷克語', intro: '一四八八年於布拉格印行的捷克語全本聖經，為斯拉夫語世界第一部印刷聖經。它承襲胡斯運動整理的第四修訂型捷克譯文，由市民集資刊行，見證波希米亞平信徒讀經文化在十五世紀的成熟。' },
          { title_zh: '胡斯派匈牙利聖經', title_orig: 'Hussite Bible', author: '塔馬什與巴林特（兩位司鐸）', era: '約 1416–1435', place: '匈牙利南部／摩爾達維亞', language: '匈牙利語', intro: '兩位受胡斯思想影響的司鐸塔馬什與巴林特所譯的第一部匈牙利語聖經，因宗教裁判追索而攜稿流亡摩爾達維亞。譯文存於三部抄本，兼創匈牙利語標音正字法，是匈牙利語文學與異議宗教運動交織的開端。' },
          { title_zh: '王后索菲亞聖經', title_orig: 'Queen Sophia\'s Bible (Biblia królowej Zofii)', author: '安傑伊‧茲‧雅舒維茨等', era: '約 1453–1455', place: '克拉科夫宮廷', language: '波蘭語', intro: '波蘭最古的聖經翻譯，為雅蓋沃王朝王后索菲亞委製，宮廷懺悔師安傑伊等自捷克語本轉譯舊約。存世僅殘卷（原藏匈牙利沙羅什帕塔克），是古波蘭語散文的最大紀念碑，亦見證王室女性在俗語聖經運動中的贊助角色。' },
          { title_zh: '門特林聖經', title_orig: 'Mentelin Bible', author: '約翰內斯‧門特林（印行）', era: '1466', place: '斯特拉斯堡', language: '德語', intro: '第一部印刷的德語聖經，亦是拉丁文以外任何俗語的第一部印刷聖經。所用譯文為十四世紀紐倫堡一帶的舊譯，直譯生硬，然印行後五十年間德語聖經連出十八版，證明宗教改革前德語讀經需求之盛，徹底動搖「俗人不得讀經」的成見。' },
          { title_zh: '科隆聖經', title_orig: 'Cologne Bible', author: '科隆印坊（海因裡希‧昆特爾等）', era: '1478–1479', place: '科隆', language: '低地德語', intro: '一四七八至七九年科隆印行的兩種低地德語聖經（下萊茵與下薩克森語），附一百餘幅大型木刻插畫，構圖為後世德語聖經插畫（含路德聖經）沿用。它把泥金抄本的圖像傳統移植入印刷，是插畫印刷聖經的奠基之作。' },
          { title_zh: '德利夫特聖經', title_orig: 'Delft Bible', author: '德利夫特印坊', era: '1477', place: '德利夫特', language: '中古荷蘭語', intro: '一四七七年印行的第一部荷蘭語印刷聖經，收舊約而缺詩篇，譯文承十四世紀南尼德蘭修道譯經傳統。它是荷蘭語印刷書籍的開端之一，見證低地國家「現代虔敬運動」滋養的平信徒讀經風氣。' },
          { title_zh: '馬勒米聖經', title_orig: 'Malermi Bible', author: '尼科洛‧馬勒米', era: '1471', place: '威尼斯', language: '義大利語', intro: '卡馬爾多利會士馬勒米據武加大並整編舊有俗譯而成的義大利語全本聖經，一四七一年於威尼斯印行，為第一部印刷的義大利語聖經。至十六世紀中葉凡印三十餘版，附木刻插畫諸版尤為流行，是義大利文藝復興時代平信徒聖經文化的主脈。' },
          { title_zh: '斯蒂約恩聖史譯述', title_orig: 'Stjórn', author: '挪威宮廷譯者群', era: '約 1300（部分更早）', place: '挪威／冰島', language: '古挪威-冰島語', intro: '「治理」（Stjórn）為古挪威-冰島語的舊約譯述彙編，部分成於哈康五世宮廷，融聖經正文與《經院史》式的百科註解為一體。它是北歐中世紀最大的散文譯經工程，證明聖經俗語化的浪潮遠及斯堪的納維亞，主要抄本藏哥本哈根與雷克雅維克。' }
        
        ]
      },
      {
        key: 'philology-tools',
        label: '語文與檢索工具部',
        label_en: 'Philology and Reference Tools',
        desc: '經文彙編、希伯來與希臘語文研究等中世紀聖經語文學與檢索工具。',
        works: [
          { title_zh: '聖雅各經文彙編', title_orig: 'Concordantiae Sancti Jacobi', author: '聖謝爾的休主持（道明會團隊）', era: '約 1230–1235', place: '巴黎聖雅各修道院', language: '拉丁文', intro: '史上第一部聖經逐詞索引，由聖謝爾的休率數百名道明會士以朗頓章次為座標編成，把全本武加大的字詞按字母排序標明出處。它使講道者與神學家能瞬時檢得經文，帶動引證文化的革命；其後兩度增修為「英吉利彙編」，成為一切經文彙編的鼻祖。' },
          { title_zh: '博舍姆詩篇希伯來本註', title_orig: 'Psalterium cum commento', author: '赫伯特‧德‧博舍姆', era: '約 1190', place: '英格蘭／法蘭西', language: '拉丁文', intro: '貝克特的門生博舍姆晚年據耶柔米「希伯來本詩篇」撰成逐字註釋，直接徵引希伯來原文與拉希的猶太釋經，是中世紀唯一針對希伯來本詩篇字面義的註疏。其希伯來學造詣為十二世紀基督徒罕見，湮沒七百年後方由斯莫利與洛伊重新發現，被譽為中世紀基督教希伯來學的最高峰。' },
          { title_zh: '羅傑‧培根希臘文法', title_orig: 'Grammatica Graeca', author: '羅傑‧培根', era: '約 1270', place: '牛津', language: '拉丁文', intro: '方濟會士培根痛感巴黎修正諸家不諳原文而妄改聖經，力倡語言之學，撰成西方中世紀第一部希臘文法，另有希伯來文法殘篇。書中兼論經文校勘之法，主張回到希臘、希伯來原文以正拉丁訛誤，是中世紀語文學自覺的先聲，直接預告了人文主義的回歸原典。' }
        
        ]
      },
      {
        key: 'cross-religion-translation',
        label: '跨宗教翻譯部',
        label_en: 'Cross-Religious Translation',
        desc: '由基督教世界主持、將伊斯蘭與阿拉伯—希臘學術譯入拉丁文的翻譯工程。',
        works: [
          { title_zh: '拉丁文古蘭經（穆罕默德偽先知之法）', title_orig: 'Lex Mahumet pseudoprophete', author: '克頓的羅伯特（可敬的彼得主持）', era: '1143', place: '托萊多／克呂尼', language: '拉丁文（譯自阿拉伯文）', intro: '此為史上第一部完整的拉丁文古蘭經譯本，由克呂尼隱修院長可敬的彼得贊助、英格蘭學者克頓的羅伯特主譯，連同其他文獻合成「托萊多文集（Collectio Toletana）」。彼得意在使拉丁學界了解伊斯蘭以利論辯而非武力對抗。譯本雖採意譯且帶論戰色彩、序言斥穆罕默德為偽先知，卻是西方認識古蘭經的首要門徑，流傳近四百年，至文藝復興與宗教改革時代仍被印行援引。', note: '序與選章；屬論戰性意譯' },
          { title_zh: '托萊多翻譯院譯本集', title_orig: 'Translationes Toletanae（阿拉伯哲學與科學拉丁譯本）', author: '托萊多翻譯院（克雷莫納的傑拉德等）', era: '12–13 世紀', place: '托萊多（西班牙）', language: '拉丁文（譯自阿拉伯文，部分經希伯來文）', intro: '托萊多在收復後成為基督徒、穆斯林與猶太學者協作的翻譯重鎮，將大量阿拉伯文的哲學與科學典籍——亞里斯多德全集及阿拉伯註釋、阿維森納、阿維羅伊、托勒密《天文學大成》、歐幾里得、花拉子米的代數等——譯為拉丁文。克雷莫納的傑拉德一人即譯逾七十部。這場翻譯運動把希臘—阿拉伯的學術寶庫注入拉丁西方，直接催生了十三世紀經院哲學的興盛與大學的學術繁榮。' },
          { title_zh: '馬克‧德‧託萊多古蘭經直譯本', title_orig: 'Liber Alchorani', author: '託萊多的馬可', era: '1210–1211', place: '託萊多', language: '拉丁文（譯自阿拉伯文）', intro: '託萊多座堂法政牧師馬可應大主教羅德里戈之請重譯古蘭經，較克頓的羅伯特意譯本遠為直質，貼近阿拉伯原文語序。此譯本流傳雖不及前者，卻代表中世紀拉丁世界對伊斯蘭經典更嚴謹的語文學進路，並附譯穆斯林信仰綱要，服務於收復失地運動下的辯道與宣教。' },
          { title_zh: '赫爾曼‧德‧卡林西亞伊斯蘭文獻譯集', title_orig: 'De generatione Mahumet; Doctrina Mahumet', author: '卡林西亞的赫爾曼', era: '1142–1143', place: '西班牙埃布羅河谷', language: '拉丁文（譯自阿拉伯文）', intro: '斯拉夫出身的學者赫爾曼受可敬的彼得延攬，與克頓的羅伯特分工翻譯「託萊多文集」中的穆罕默德傳說與問答文獻，如《穆罕默德的世系》《穆罕默德的教導》。這批譯文使拉丁讀者首次得窺伊斯蘭傳統的內部敘事，雖帶論戰目的，仍是十二世紀跨宗教知識轉移的里程碑。' },
          { title_zh: '布爾貢迪奧希臘教父拉丁譯集', title_orig: 'Translationes Burgundionis Pisani', author: '比薩的布爾貢迪奧', era: '約 1150–1193', place: '比薩／君士坦丁堡', language: '拉丁文（譯自希臘文）', intro: '比薩法學家布爾貢迪奧屢任駐君士坦丁堡使節，通曉希臘文，將大馬士革的約翰《正統信仰詳解》、金口若望福音講道集、尼撒的格列高理《論人的造成》等譯為拉丁文，並譯蓋倫醫書。其譯業使拉丁經院得以直接徵引希臘教父體系，隆巴德與阿奎那皆受其惠。' },
          { title_zh: '格羅斯泰斯特希臘譯業', title_orig: 'Translationes Roberti Grosseteste', author: '羅伯特‧格羅斯泰斯特', era: '約 1235–1253', place: '林肯', language: '拉丁文（譯自希臘文）', intro: '林肯主教格羅斯泰斯特晚年延聘希臘助手，重譯託名狄奧尼修斯全集並附詳注，又譯大馬士革的約翰、《十二族長遺訓》與亞里斯多德《尼各馬可倫理學》。其譯風逐字精確，兼附語文學評註，把牛津的希臘學推上巔峰，為中世紀英格蘭最重要的希臘—拉丁譯者。' },
          { title_zh: '莫爾貝克的威廉希臘哲學譯集', title_orig: 'Translationes Guillelmi de Morbeka', author: '莫爾貝克的威廉', era: '約 1260–1286', place: '尼西亞／維泰博／科林斯', language: '拉丁文（譯自希臘文）', intro: '道明會士威廉晚年出任科林斯總主教，應阿奎那等之請自希臘原文系統重譯亞里斯多德全集，並首譯普羅克洛《神學要義》，逐字直譯而力求可考。經院哲學自此擺脫轉譯自阿拉伯文的隔閡，阿奎那識破《原因之書》實出普羅克洛即賴其譯本，堪稱十三世紀學術翻譯的定音之錘。' }
        
        ]
      }
    ]
  },
  wai: {
    summary: '猶太及其他傳統的經本，及其在中世紀基督教世界的翻譯與傳本流傳。',
    divisions: [
      {
        key: 'other-scriptures-translation',
        label: '他宗教經本與翻譯部',
        label_en: 'Other Religious Scriptures and Their Transmission',
        desc: '猶太傳統經本的中世紀傳本，及基督教世界對其的翻譯與摘譯。',
        works: [
          { title_zh: '塔木德拉丁文摘錄', title_orig: 'Extractiones de Talmud', author: '巴黎審查譯者群（道明會主導）', era: '約 1245', place: '巴黎', language: '拉丁文（譯自希伯來文與亞蘭文）', intro: '此為現存最早、規模最大的塔木德拉丁文摘譯，緣於 1240 年巴黎塔木德審判：教會指控塔木德含褻瀆與反基督內容，遂令學者摘譯其文以供審查，終致 1242 年巴黎當眾焚毀大批塔木德抄本。譯本初按塔木德篇目編排，後改按主題重整。它雖出於論戰與審查之惡意，卻保存了十三世紀塔木德文本的珍貴面貌，是猶太—基督教關係史與文本傳承的重要史料。', note: '出於審查論戰背景' },
          { title_zh: '伊本‧提本家族希伯來譯本', title_orig: 'Tibbonide Hebrew Translations', author: '伊本‧提本家族（猶大、撒母耳等）', era: '12–13 世紀', place: '普羅旺斯（呂內爾／馬賽）', language: '希伯來文（譯自阿拉伯文）', intro: '伊本‧提本家族是普羅旺斯的猶太翻譯世家，將安達盧斯猶太學者以阿拉伯文寫成的哲學、語法與宗教經典譯為希伯來文，使不諳阿拉伯文的歐洲猶太社群得以承繼。撒母耳‧伊本‧提本譯邁蒙尼德《迷途指津》尤為經典，並與作者通信商榷譯法。此譯業確立了希伯來哲學術語，使阿拉伯—猶太的思想遺產轉入希伯來文傳統，深刻影響後世猶太思想與基督教希伯來學。' },
          { title_zh: '亞蘭塔古姆中世紀傳本', title_orig: 'Targumim（medieval recensions）', author: '猶太抄經與馬所拉傳統', era: '中世紀傳本（文本上溯更早）', place: '巴比倫／提比哩亞／歐洲猶太社群', language: '亞蘭文', intro: '塔古姆是希伯來聖經的亞蘭文翻譯與意譯，原為會堂誦經時供不通希伯來文者理解之用，如《翁克羅斯塔古姆》（妥拉）與《約拿單塔古姆》（先知書）。其文本雖源遠流長，現存抄本多為中世紀猶太抄經傳統所傳寫、加注母音與馬所拉符號者。這些傳本不僅是猶太釋經與禮儀的活水，其釋義傳統亦為中世紀基督教希伯來學者所參照，是聖經文本與詮釋史的重要環節。' }
        ]
      }
    ]
  }
},
    {
  key: 'shuxin',
  name: '書函藏',
  name_en: 'Letters and Decretals',
  glyph: '函',
  genres: '牧函‧詔書‧尺牘',
  summary: '收中世紀（約 800–1500）三軌往來文書：拉丁西方教宗的牧函與詔書、修院靈修尺牘、政教博弈書信，旁及伊斯蘭哈里發與猶太社群的書簡。以「往來相寄」為體，與史傳之「記事」、信條法規之「論斷」分流，呈現中古基督教世界藉書信經營權力、靈修與外交的活絡網絡。',
  zheng: {
    summary: '拉丁西方教宗、修院與政教場域的正統書信，含教宗牧函詔書、修院靈修尺牘、政教博弈書信三部。',
    divisions: [
      {
        key: 'jiaozong-mahan',
        label: '教宗牧函與詔書部',
        label_en: 'Papal Letters and Decretals',
        desc: '羅馬教宗訓令、書信與通諭，行使教導與治權的核心文書。',
        works: [
          { title_zh: '教宗訓令', title_orig: 'Dictatus Papae', author: '額我略七世', era: '1075 年', place: '羅馬', language: '拉丁文', intro: '教宗額我略七世登錄於書信集中的二十七條格言式宣言，逐條主張羅馬教宗的至高權柄：唯教宗可廢立主教、可解除臣民對君主的效忠誓約、教宗永不謬誤等。此文是格里高利改革與敘任權之爭的綱領，將教權凌駕王權的主張推至頂點，深刻形塑了中世紀政教關係的走向。', link: '/encyclicals' },
          { title_zh: '英諾森三世書信集', title_orig: 'Registrum Innocentii III', author: '英諾森三世', era: '1198–1216 年', place: '羅馬', language: '拉丁文', intro: '教宗權勢登峰造極的英諾森三世，任內書信經官方登錄成卷，內容涵蓋裁決王位繼承、加冕與廢黜君主、發動十字軍、處置異端與召開拉特朗大公會議等。這批書信既是教廷檔案，也展現一位教宗如何以書信為工具仲裁全歐事務，是研究中世紀盛期教廷至上論與實際治理的第一手寶庫。', link: '/encyclicals' },
          { title_zh: '一聖通諭', title_orig: 'Unam Sanctam', author: '卜尼法八世', era: '1302 年', place: '羅馬', language: '拉丁文', intro: '教宗卜尼法八世在與法王腓力四世激烈衝突中頒布的通諭，宣告教會唯一、得救必須服從羅馬教宗，並以「兩把劍」之喻主張屬靈權柄高於世俗權柄。此文是中世紀教權至上論最強硬的表述，卻適逢王權崛起，反成教宗權勢由盛轉衰的轉捩，隨後即有亞維農「教廷之囚」。', link: '/encyclicals' },
          { title_zh: '尼古拉一世書信集', title_orig: 'Epistolae Nicolai I', author: '教宗尼古拉一世', era: '858–867', place: '羅馬', language: '拉丁文', intro: '九世紀最強勢教宗尼古拉一世的書信集，涉洛泰爾二世離婚案、佛提烏之爭與教宗首席權的申張，行文剛烈，屢以「教宗高於君王」立論。這批書信是加洛林晚期政教關係與東西方教會摩擦的第一手文獻，收入《日耳曼歷史文獻集成》書信部。' },
          { title_zh: '答保加利亞人問', title_orig: 'Responsa Nicolai ad consulta Bulgarorum', author: '教宗尼古拉一世', era: '866', place: '羅馬', language: '拉丁文', intro: '保加利亞可汗鮑里斯一世皈依後遣使就婚俗、齋期、刑罰等一百餘項疑難請示羅馬，尼古拉一世逐條作答成此長函。答問語氣體貼入微，兼顧福音原則與民族習俗，是中世紀宣教適應策略的經典文本，亦為拜占庭與羅馬爭奪保加利亞的關鍵一著。' },
          { title_zh: '哈德良二世書信集', title_orig: 'Epistolae Hadriani II', author: '教宗哈德良二世', era: '867–872', place: '羅馬', language: '拉丁文', intro: '哈德良二世在位雖短，其書信正值君士坦丁堡第四次大公會議與斯拉夫宣教的關口：他批准西里爾與美多德的斯拉夫禮儀並祝聖美多德為主教，相關函件保存了教廷對斯拉夫譯經最初的正式認可，為斯拉夫基督教的合法性奠基，收入《日耳曼歷史文獻集成》。' },
          { title_zh: '若望八世書信登記冊', title_orig: 'Registrum Iohannis VIII', author: '教宗若望八世', era: '872–882', place: '羅馬', language: '拉丁文', intro: '九世紀教廷書信登記冊中罕見近乎完整傳世者，三百餘函涉薩拉森人侵義大利、美多德在摩拉維亞的護持與東西方修好。若望八世重申斯拉夫語禮儀之許可，其登記冊是研究九世紀教廷行政與地中海危機的核心史料。' },
          { title_zh: '額我略七世書信登記冊', title_orig: 'Registrum Gregorii VII', author: '教宗額我略七世', era: '1073–1085', place: '羅馬', language: '拉丁文', intro: '額我略七世改革教廷的官方書信登記冊，原冊奇蹟般傳世，三百六十餘函貫穿敘任權之爭全程，致亨利四世、諸侯與主教的函件火氣逼人，著名的《教宗訓令》亦錄於其中。它是十一世紀教會改革運動最核心的文獻整體，被譽為中世紀教廷檔案之王。' },
          { title_zh: '良九世與賽魯拉留斯往來文書', title_orig: 'Leo IX–Michael Cerularius correspondence', author: '良九世／米海爾一世賽魯拉留斯', era: '1053–1054', place: '羅馬／君士坦丁堡', language: '拉丁文／希臘文', intro: '一〇五四年東西方教會決裂前夕，教宗良九世與君士坦丁堡宗主教賽魯拉留斯就無酵餅、教宗首席權等針鋒相對的往來文書。良九世函中首度大段援引《君士坦丁獻土》申張教權，談判終以互相絕罰收場。這批文書是大分裂的直接見證，千年後兩教會撤銷絕罰時仍須回到它們。' },
          { title_zh: '烏爾班二世十字軍文告書信', title_orig: 'Epistolae Urbani II de cruce', author: '教宗烏爾班二世', era: '1095–1099', place: '克萊蒙／羅馬', language: '拉丁文', intro: '烏爾班二世於克萊蒙會議號召十字軍後發往佛蘭德斯、波隆那等地的正式書信，申明赦罪允諾與出征規範，是十字軍運動最早的官方文本。與後世編纂的演說詞不同，這批書信出自教宗府第一手，為考訂克萊蒙原始訊息的基準文獻。' },
          { title_zh: '亞歷山大三世書信集', title_orig: 'Epistolae Alexandri III', author: '教宗亞歷山大三世', era: '1159–1181', place: '羅馬／流亡諸地', language: '拉丁文', intro: '亞歷山大三世在位廿二年與腓特烈一世巴巴羅薩纏鬥、處理貝克特案，存世書信與教令逾七百件，大量進入後世《教令集》。其函件展示流亡教宗如何以文書維繫普世網絡，是十二世紀教廷司法權成形的文獻主脈。' },
          { title_zh: '洪諾留三世書信登記冊', title_orig: 'Regesta Honorii III', author: '教宗洪諾留三世', era: '1216–1227', place: '羅馬', language: '拉丁文', intro: '洪諾留三世的官方登記冊近乎完整傳世，錄函件近萬，批准道明會與方濟會會規、籌劃第五次十字軍、協調幼主腓特烈二世的監護。它是十三世紀教廷「文書治理」規模的第一手見證，為託缽修會創建史的根本檔案。' },
          { title_zh: '英諾森四世書信登記冊', title_orig: 'Registrum Innocentii IV', author: '教宗英諾森四世', era: '1243–1254', place: '里昂／羅馬', language: '拉丁文', intro: '英諾森四世與腓特烈二世決戰時期的教廷登記冊，含里昂第一次會議廢黜皇帝的文書與遣使蒙古的國書。教宗致貴由汗的兩函以神學勸化草原霸主，開啟教廷的歐亞外交，登記冊全帙是十三世紀政教衝突與蒙古交涉的檔案核心。' },
          { title_zh: '尼各老四世致東方諸王書信', title_orig: 'Epistolae Nicolai IV ad reges Orientis', author: '教宗尼各老四世', era: '1288–1292', place: '羅馬', language: '拉丁文', intro: '首位方濟會出身的教宗尼各老四世致伊利汗阿魯渾、元世祖忽必烈與衣索比亞君主的宣教國書，並派遣孟高維諾東行。這批書信首次把教廷視野正式延伸至中國與非洲之角，是中世紀天主教全球宣教藍圖的開端文獻。' },
          { title_zh: '教士俸祿諭', title_orig: 'Clericis laicos', author: '教宗卜尼法八世', era: '1296', place: '羅馬', language: '拉丁文', intro: '卜尼法八世禁止世俗君主未經教廷同意向教士徵稅的通諭，直指英法兩王籌措戰費之舉，凡違者絕罰。法王腓力四世以禁運金銀出境反制，揭開教權與新興主權國家的決戰序幕，本諭與其後《一聖通諭》同為中世紀教權主張的絕唱。' },
          { title_zh: '克萊孟五世書信登記冊', title_orig: 'Regestum Clementis papae V', author: '教宗克萊孟五世', era: '1305–1314', place: '亞維儂', language: '拉丁文', intro: '首位駐蹕亞維儂的教宗克萊孟五世的登記冊，貫穿聖殿騎士團審判、維埃納會議與教廷遷徙的全程。函件顯示教宗在腓力四世壓力下的迂迴周旋，本篤會刊本九巨冊，是「亞維儂之囚」開端的檔案總匯。' },
          { title_zh: '若望二十二世詔書與書信', title_orig: 'Epistolae Iohannis XXII', author: '教宗若望二十二世', era: '1316–1334', place: '亞維儂', language: '拉丁文', intro: '亞維儂教廷全盛期教宗若望二十二世的詔書與書信，涉方濟會神貧之爭、譴責埃克哈特命題、與巴伐利亞的路易帝位之爭，並設立蘇丹尼耶總教區經略波斯。其文書產量空前，展示十四世紀教廷財政與司法機器的巔峰運作。' },
          { title_zh: '克萊孟六世護猶詔書', title_orig: 'Quamvis perfidiam (Sicut Judaeis renewals)', author: '教宗克萊孟六世', era: '1348', place: '亞維儂', language: '拉丁文', intro: '黑死病肆虐、屠猶謠言四起之際，克萊孟六世兩度頒詔駁斥「猶太人投毒」之誣，指出猶太社群同罹瘟疫，嚴禁未經審判加害，並在亞維儂庇護逃難猶太人。此詔是中世紀教廷保護猶太人傳統最擲地有聲的一章，於反猶狂潮中尤顯孤勇。' },
          { title_zh: '庇護二世致穆罕默德二世書', title_orig: 'Epistola ad Mahomatem II', author: '教宗庇護二世', era: '1461', place: '羅馬', language: '拉丁文', intro: '君士坦丁堡陷落後，人文主義教宗庇護二世致函征服者穆罕默德二世，勸其受洗以換取「東羅馬皇帝」之承認，全文縱論兩教異同，兼具護教論與外交奇想。此書似未實際送達，卻是文藝復興教廷面對鄂圖曼霸權的思想標本，流傳刊本極廣。' }
        
        ],
      },
      {
        key: 'xiuyuan-chidu',
        label: '修院靈修尺牘部',
        label_en: 'Monastic and Spiritual Letters',
        desc: '修道院與靈修傳統中往來的書信，論靈修、神學與情誼。',
        works: [
          { title_zh: '伯爾納鐸書信集', title_orig: 'Epistolae Sancti Bernardi', author: '克萊爾沃的伯爾納鐸', era: '12 世紀', place: '勃艮第克萊爾沃修院', language: '拉丁文', intro: '熙篤會精神領袖伯爾納鐸一生致書教宗、君主、主教與修士，數以百計，內容遍及修道改革、神學爭辯、勸退與調解、鼓吹第二次十字軍等。其書信文采斐然、辭鋒銳利而靈修深厚，使他成為十二世紀西歐最具影響力的人物之一。這批尺牘是研究中古修道靈修與教會政治交織的典範文本。', link: '/fathers' },
          { title_zh: '阿伯拉爾與哀綠綺思往來書信', title_orig: 'Epistolae Abaelardi et Heloisae', author: '彼得‧阿伯拉爾、哀綠綺思', era: '12 世紀', place: '巴黎／帕拉克萊修院', language: '拉丁文', intro: '神學家阿伯拉爾與其弟子哀綠綺思的悲劇戀情舉世皆知，二人各自出家後仍互通書信。信中阿伯拉爾自述苦難（「劫餘錄」），哀綠綺思則坦露未泯的愛戀與對修道生活的掙扎，往返辯難愛欲、悔罪與修道倫理。這組書信兼具自傳、靈修與情感文學的多重深度，是中世紀最動人的私人通信。', link: '/fathers' },
          { title_zh: '希爾德加德書信集', title_orig: 'Epistolarium Hildegardis Bingensis', author: '賓根的希爾德加德', era: '12 世紀', place: '萊茵蘭賓根魯佩茨貝格修院', language: '拉丁文', intro: '本篤會女院長、神視家希爾德加德致教宗、皇帝、主教與各方求問者的大量書信，常以「天主之言」的先知口吻發出告誡、安慰與屬靈指引。身為女性而能以神視權威向當世權貴進言，她的書信展現中世紀女性靈修聲音的罕見高度，內容兼及神學、教會改革與靈修勸勉，是修院書信文化的奇葩。', link: '/fathers' },
          { title_zh: '彼得‧達米安書信集', title_orig: 'Epistolae Petri Damiani', author: '彼得‧達米安', era: '約 1040–1072', place: '豐泰阿韋拉納', language: '拉丁文', intro: '隱修改革家、樞機彼得‧達米安的一百八十封書信，兼具隱修勸勉與教會改革檄文，痛斥買賣聖職與教士敗德，致教宗與皇后的函件尤見鋒芒。其書信集是十一世紀改革運動的靈魂文獻，修辭峻烈如火，被譽為「改革的良心」。' },
          { title_zh: '安瑟莫書信集', title_orig: 'Epistolae Anselmi', author: '坎特伯裡的安瑟莫', era: '約 1070–1109', place: '貝克／坎特伯裡', language: '拉丁文', intro: '安瑟莫存世書信四百七十餘封，自貝克修道院師友情誼到坎特伯裡大主教任上與英王的敘任權抗爭，靈修懇切與原則堅定並見。其致修士的友愛書簡展現中世紀修道友誼神學的典範，是理解這位經院之父人格的第一門徑。' },
          { title_zh: '可敬的彼得書信集', title_orig: 'Epistolae Petri Venerabilis', author: '可敬的彼得', era: '約 1122–1156', place: '克呂尼', language: '拉丁文', intro: '克呂尼隱修院長可敬的彼得的書信集，與聖伯爾納論辯修道理想、庇護落難的阿伯拉爾、主持古蘭經翻譯的往還俱在其中。文風溫厚寬和，與伯爾納的鋒銳相映成趣，是十二世紀修道文化與跨宗教視野交會的樞紐文獻。' },
          { title_zh: '亞西西方濟各書信集', title_orig: 'Epistolae S. Francisci', author: '亞西西的方濟各', era: '約 1215–1226', place: '亞西西', language: '拉丁文', intro: '方濟各存世書信含《致眾信友書》《致全會書》《致某長上書》與致安東尼的短簡等，語極質樸而句句見其神魂：敬禮聖體、服從教會、以貧窮為淨配。這批書信與遺囑同為方濟各親筆心聲的最直接見證，是方濟靈修的源頭活水。' },
          { title_zh: '加辣致布拉格依搦斯書信', title_orig: 'Epistolae S. Clarae ad Agnetem de Praga', author: '亞西西的加辣', era: '1234–1253', place: '亞西西聖達勉', language: '拉丁文', intro: '加辣致波希米亞公主、後入方濟第二會的布拉格依搦斯的四封書信，以「貧窮夫人」的婚姻密契語言勸勉持守赤貧特恩，是中世紀女性間靈修指導的珍稀文獻。兩位女性一在義大利一在波希米亞，以書信共構跨國的女性修道網絡。' },
          { title_zh: '哈德維希書信集', title_orig: 'Brieven van Hadewijch', author: '哈德維希', era: '13 世紀中', place: '布拉班特', language: '中古荷蘭文', intro: '布拉班特貝居因女靈修導師哈德維希致同道姊妹的三十一封書信，以「愛」（Minne）的宮廷語彙鍛造密契神學，為中古荷蘭語散文的巔峰。書信對象是無會規束縛的平信徒女性群體，見證中世紀低地國家女性靈修運動的自主與深度。' },
          { title_zh: '蘇索小書信集', title_orig: 'Briefbüchlein (Heinrich Seuse)', author: '亨利‧蘇索', era: '約 1350', place: '康斯坦茨／烏爾姆', language: '德文', intro: '道明會密契者蘇索晚年由其靈修女弟子施塔格爾輯錄的德語靈修書信選，勸慰修女以基督受苦為鏡，柔腸與詩情兼備。與其《智慧書》同為「萊茵密契」德語散文的珠玉，見證男性靈修導師與女修道群體的書信牧養。' },
          { title_zh: '諾德林根與埃布納往來書信', title_orig: 'Briefwechsel Heinrichs von Nördlingen und Margaretha Ebner', author: '亨利‧馮‧諾德林根／瑪格麗特‧埃布納', era: '1332–1350', place: '巴伐利亞梅丁根', language: '德文', intro: '世俗司鐸亨利與道明會修女密契者埃布納的往來書信，為德語史上第一批完整傳世的私人通信。信中交流靈視經驗、代禱與「上帝之友」網絡的消息，兼證帝國禁令時期平信徒靈修圈的地下聯繫，是十四世紀德語密契運動的活檔案。' },
          { title_zh: '錫耶納的加大利納書信集', title_orig: 'Epistole di S. Caterina da Siena', author: '錫耶納的加大利納', era: '1370–1380', place: '錫耶納／亞維儂／羅馬', language: '義大利文', intro: '平信徒道明第三會女子加大利納口述的三百八十一封書信，上至教宗（促額我略十一世返羅馬）、君王，下至獄囚、妓女，以「血與火」的密契語言直言不諱。這批書信是十四世紀義大利語散文的高峰，也是女性以靈性權威介入教會政治的空前見證。' },
          { title_zh: '圭戈二世隱修者之梯', title_orig: 'Scala claustralium (Epistola ad Gervasium)', author: '加爾都西的圭戈二世', era: '約 1150–1180', place: '大沙特勒斯', language: '拉丁文', intro: '加爾都西會第九任總院長圭戈二世致熱爾維修士的書信體小品，首度把靈修進程定式為讀經、默想、祈禱、默觀四階，「修士之梯」自此成為聖言誦讀（lectio divina）的經典綱領。全文僅數千言，影響貫穿至今的靈修傳統，是書信體靈修文學的絕品。' },
          { title_zh: '洪貝爾致全會書信', title_orig: 'Epistolae encyclicae Humberti de Romanis', author: '羅曼斯的洪貝爾', era: '1254–1263', place: '巴黎／里昂', language: '拉丁文', intro: '道明會第五任總會長洪貝爾每年致全會的通函，申論修會紀律、學業與宣道使命，兼及與方濟會的和睦。這批通函開創託缽修會「總會長書信」的治理文類，是十三世紀修會制度化管理的第一手文獻。' },
          { title_zh: '波納文圖拉致全會書信', title_orig: 'Epistolae officiales S. Bonaventurae', author: '波納文圖拉', era: '1257–1266', place: '巴黎', language: '拉丁文', intro: '波納文圖拉出任方濟會總會長之初與其後致全會的通函，直陳會內怠惰、乞討浮濫等積弊，籲回歸方濟本意而兼顧學術使命。這兩封通函是「第二會祖」重整方濟會的施政綱領，與其《大傳》同為方濟會身分之爭的關鍵文獻。' },
          { title_zh: '傑拉德‧格魯特書信集', title_orig: 'Epistolae Gerardi Magni', author: '傑拉德‧格魯特', era: '約 1379–1384', place: '德文特', language: '拉丁文', intro: '「現代虔敬運動」創始人格魯特的書信集，勸勉初創的共同生活弟兄會眾以內修、勞作與抄書自養，並批評教會積弊。其書信奠定德文特圈的靈修基調，此運動終結出《效法基督》之果，書信集是運動起源的直接文獻。' },
          { title_zh: '託馬斯‧肯皮斯書信集', title_orig: 'Epistolae Thomae a Kempis', author: '託馬斯‧肯皮斯', era: '約 1420–1470', place: '茲沃勒聖阿格尼斯山', language: '拉丁文', intro: '《效法基督》作者肯皮斯致修士與在俗友人的靈修書信，主題一如其書：退隱、安靜、棄絕虛榮。書信平實溫熙，展現現代虔敬運動晚期的日常牧養面貌，為理解這位隱修文豪生平交遊的少數第一手材料。' }
        
        ],
      },
      {
        key: 'scholar-letters',
        label: '學者教牧尺牘部',
        label_en: 'Letters of Scholars and Pastors',
        desc: '加洛林學者、主教學校、經院學人與教牧領袖的書信集——中世紀「書信共和國」的主脈。',
        works: [
          { title_zh: '阿爾昆書信集', title_orig: 'Epistolae Alcuini', author: '阿爾琴（約克的阿爾昆）', era: '約 790–804', place: '亞琛／圖爾', language: '拉丁文', intro: '卡爾大帝首席學術顧問阿爾琴存世書信三百餘封，致君王論教育與治道、致弟子論學業、致各地主教論禮儀與正統，是加洛林文藝復興的神經網絡。其函屢勸皇帝以勸化代刀劍對待薩克森人，展現宮廷學者的良知，收入《日耳曼歷史文獻集成》。' },
          { title_zh: '埃甘哈德書信集', title_orig: 'Epistolae Einhardi', author: '埃甘哈德', era: '約 823–840', place: '塞利根施塔特', language: '拉丁文', intro: '卡爾大帝傳記作者埃甘哈德晚年的書信集，為屬民請命、為修院產業奔走、與宮廷故舊寒暄，兼及喪妻之慟的私語。這批信函展示加洛林俗人廷臣的日常世界，與其《卡爾大帝傳》互補，是九世紀社會史的難得側寫。' },
          { title_zh: '費裡耶爾的盧普斯書信集', title_orig: 'Epistolae Lupi Ferrariensis', author: '費裡耶爾的盧普斯', era: '約 840–862', place: '費裡耶爾', language: '拉丁文', intro: '加洛林院長盧普斯的一百三十餘封書信，四處借閱、校勘、追討古典與教父抄本，堪稱第一位「文獻學家」的工作日誌。信中兼涉預定論之爭與王國政局，其求書若渴的形象成為加洛林人文主義最鮮活的見證。' },
          { title_zh: '拉巴努斯‧毛魯斯書信集', title_orig: 'Epistolae Hrabani Mauri', author: '拉巴努斯‧毛魯斯', era: '約 820–856', place: '富爾達／美因茲', language: '拉丁文', intro: '「日耳曼之師」拉巴努斯的書信集，多為進呈註釋著作的獻書函與答疑之作，兼涉戈特沙爾克預定論案的處置。書信勾勒富爾達學術帝國的運作與師承網絡，是加洛林經院教育體制的第一手文獻。' },
          { title_zh: '欣克馬爾書信集', title_orig: 'Epistolae Hincmari Remensis', author: '蘭斯的欣克馬爾', era: '845–882', place: '蘭斯', language: '拉丁文', intro: '蘭斯大主教欣克馬爾的龐大書信檔案，縱橫王位繼承、洛泰爾離婚案、預定論之爭與教省司法，動輒萬言，法理與權謀並用。他是九世紀西法蘭克教會實際的操盤手，其書信集是加洛林晚期政教運作最深的檔案礦脈。' },
          { title_zh: '拉瑟‧德‧維羅納書信集', title_orig: 'Epistolae Ratherii Veronensis', author: '維羅納的拉瑟', era: '約 930–974', place: '維羅納／列日', language: '拉丁文', intro: '十世紀最尖刻的文人主教拉瑟三度出掌維羅納三度被逐，其書信自嘲自辯、痛罵教士無知與貴族擅權，文風扭曲奇崛，人稱「維羅納的怪傑」。這批信函是所謂「黑暗世紀」裡知識分子孤憤的罕見自白。' },
          { title_zh: '阿博‧德‧弗勒裡書信集', title_orig: 'Epistolae Abbonis Floriacensis', author: '弗勒裡的阿博', era: '約 985–1004', place: '弗勒裡', language: '拉丁文', intro: '弗勒裡院長阿博的書信集，為修道院豁免權據理力爭、調停英法教會爭端、兼論曆算與正典法彙。阿博終在加斯科尼平亂中殉身，其書信是千年之交修道自由與王權角力的見證，亦見證弗勒裡作為學術中心的地位。' },
          { title_zh: '熱爾貝書信集', title_orig: 'Epistolae Gerberti', author: '歐裡亞克的熱爾貝（西爾維斯特二世）', era: '983–997', place: '蘭斯／拉文納', language: '拉丁文', intro: '日後成為千禧年教宗西爾維斯特二世的數學家熱爾貝任蘭斯學監時期的二百二十封書信，借書、論學、為帝國與法蘭西王位斡旋，字裡行間可見算盤與星盤的行家。這批書信是十世紀晚期政學交織的絕佳標本，被譽為當代最精緻的拉丁文。' },
          { title_zh: '富爾貝爾‧德‧沙特爾書信集', title_orig: 'Epistolae Fulberti Carnotensis', author: '沙特爾的富爾貝爾', era: '約 1004–1028', place: '沙特爾', language: '拉丁文', intro: '沙特爾主教學校奠基人富爾貝爾的書信集，其致阿基坦公爵威廉論封臣義務的一函，成為中世紀封建關係最常被徵引的定義文本。書信兼涉聖母敬禮與教會產業，展示十一世紀初主教學校崛起的氣象。' },
          { title_zh: '蘭弗朗克書信集', title_orig: 'Epistolae Lanfranci', author: '帕維亞的蘭弗朗克', era: '1070–1089', place: '坎特伯裡', language: '拉丁文', intro: '諾曼征服後首任坎特伯裡大主教蘭弗朗克的書信集，重整英格蘭教會、確立坎特伯裡對約克的首席權、輔佐威廉一世攝政，函件簡峻務實。它是諾曼教會改革的檔案主幹，兼見這位貝克名師由學者轉為政治家的身影。' },
          { title_zh: '伊沃‧德‧沙特爾書信集', title_orig: 'Epistolae Ivonis Carnotensis', author: '沙特爾的伊沃', era: '1090–1115', place: '沙特爾', language: '拉丁文', intro: '教會法學家伊沃的二百八十八封書信，以法理調處敘任權之爭，提出「屬靈授職與世俗封授分離」的折衷原則，直接預備了沃姆斯協約。其書信被當作教會法諮詢判例傳抄，是中世紀「以書信立法理」的典範。' },
          { title_zh: '希爾德貝爾‧德‧拉瓦爾丹書信集', title_orig: 'Epistolae Hildeberti Cenomanensis', author: '拉瓦爾丹的希爾德貝爾', era: '約 1100–1133', place: '勒芒／圖爾', language: '拉丁文', intro: '勒芒主教、後任圖爾總主教的希爾德貝爾以西塞羅式文筆馳名，其書信集在中世紀被當作書信術範本傳抄逾百部。函件慰問流亡者、規勸君王、詠嘆羅馬廢墟，古典人文情懷躍然，是十二世紀文藝復興前奏的代表文獻。' },
          { title_zh: '維博爾德‧德‧斯塔沃洛書信集', title_orig: 'Epistolae Wibaldi Stabulensis', author: '斯塔沃洛的維博爾德', era: '1146–1157', place: '斯塔沃洛／科爾維', language: '拉丁文', intro: '帝國首席修道院長維博爾德輔佐康拉德三世與腓特烈一世的書信檔案四百餘件，涉第二次十字軍、羅馬公社與拜占庭聯姻談判，兼及默茲金工藝術的訂製函。這批檔案近乎完整傳世，是霍亨斯陶芬初期帝國政治的核心史料。' },
          { title_zh: '蘇熱書信集', title_orig: 'Epistolae Sugerii', author: '聖但尼的蘇熱', era: '約 1122–1151', place: '聖但尼', language: '拉丁文', intro: '聖但尼院長、法王路易六世與七世的股肱蘇熱的書信集，第二次十字軍期間攝政法蘭西的政務函電俱在。與其《路易六世傳》及聖但尼重建錄互參，可見這位「哥德式建築之父」如何以修院為樞紐運轉王國。' },
          { title_zh: '索爾茲伯裡的約翰書信集', title_orig: 'Epistolae Iohannis Saresberiensis', author: '索爾茲伯裡的約翰', era: '1153–1180', place: '坎特伯裡／沙特爾', language: '拉丁文', intro: '十二世紀最優雅的人文學者約翰的三百二十五封書信，前期代坎特伯裡大主教起草教廷文書，後期見證貝克特案全程並在血案現場。書信集古典徵引信手拈來，兼具史料與文學雙重極品之譽。' },
          { title_zh: '吉爾伯特‧福利奧特書信集', title_orig: 'Epistolae Gilberti Foliot', author: '吉爾伯特‧福利奧特', era: '1139–1187', place: '格洛斯特／倫敦', language: '拉丁文', intro: '倫敦主教福利奧特為貝克特案中王權一方的教會領袖，其書信集與貝克特陣營針鋒相對，名函《不可多讓》系統駁斥大主教的殉道姿態。與貝克特往來書信集對讀，方能見這場政教衝突的完整光譜。' },
          { title_zh: '彼得‧德‧布盧瓦書信集', title_orig: 'Epistolae Petri Blesensis', author: '布盧瓦的彼得', era: '約 1170–1204', place: '坎特伯裡／倫敦', language: '拉丁文', intro: '宮廷文人彼得‧德‧布盧瓦自編的書信集，描摹亨利二世宮廷的奔波苦況、申論教士操守，文采斐然，中世紀傳抄逾二百部，為書信文學之最。其「宮廷病」書簡開創對權力生活的諷刺文類，影響直至人文主義。' },
          { title_zh: '彼得‧德‧塞勒書信集', title_orig: 'Epistolae Petri Cellensis', author: '塞勒的彼得', era: '約 1145–1183', place: '塞勒／沙特爾', language: '拉丁文', intro: '塞勒院長、後任沙特爾主教的彼得與索爾茲伯裡的約翰等一代文士的往來書信，靈修沉思與時局評騭交織，文風凝鍊如箴言。其書信網絡橫跨英法修道與主教圈，是十二世紀「書信共和國」的典型標本。' },
          { title_zh: '斯蒂芬‧德‧圖爾奈書信集', title_orig: 'Epistolae Stephani Tornacensis', author: '圖爾奈的斯蒂芬', era: '約 1160–1203', place: '奧爾良／巴黎／圖爾奈', language: '拉丁文', intro: '教會法學家、後任圖爾奈主教的斯蒂芬書信集，名函痛陳巴黎新式經院辯證氾濫、神學淪為技藝，為保守派對早期大學最經典的批評文本。函件兼涉修院治理與王室斡旋，見證法學訓練的行政菁英崛起。' },
          { title_zh: '阿爾努爾夫‧德‧利雪書信集', title_orig: 'Epistolae Arnulfi Lexoviensis', author: '利雪的阿爾努爾夫', era: '1141–1181', place: '利雪（諾曼第）', language: '拉丁文', intro: '諾曼第利雪主教阿爾努爾夫周旋於英法王室、教廷分裂與貝克特案之間的書信集，晚年失勢退隱的自辯函尤見蒼涼。其信精於修辭而工於算計，是十二世紀「政治主教」生涯的完整案卷。' },
          { title_zh: '埃洛伊絲問題集', title_orig: 'Problemata Heloissae', author: '埃洛伊絲', era: '約 1132–1135', place: '聖靈修道院（帕拉克萊特）', language: '拉丁文', intro: '帕拉克萊特女修院長埃洛伊絲致阿伯拉爾的四十二道聖經釋義問題與其答覆，展現這位以博學聞名的女性學者主導的釋經對話。問題屢及女性處境與倫理困境，與兩人情書合觀，可見埃洛伊絲由戀人而學問對話者的完整面貌。' },
          { title_zh: '格羅斯泰斯特書信集', title_orig: 'Epistolae Roberti Grosseteste', author: '羅伯特‧格羅斯泰斯特', era: '1235–1253', place: '林肯', language: '拉丁文', intro: '林肯主教格羅斯泰斯特的百餘封書信，以牧靈改革為軸，最著名者為一二五三年拒絕教宗任命外甥領英格蘭聖俸的抗命函，申言「服從教廷但不服從敗壞」。這批書信是中世紀主教良知與教廷集權張力的最強文本。' },
          { title_zh: '亞當‧馬什書信集', title_orig: 'Epistolae Adae de Marisco', author: '亞當‧馬什', era: '約 1241–1259', place: '牛津', language: '拉丁文', intro: '英格蘭首位方濟會神學教授亞當‧馬什的書信集，與格羅斯泰斯特、西蒙‧德‧蒙福爾及王后往還，以靈修之筆議政事之非。其信是十三世紀牛津方濟學派與貴族改革運動聯結的獨家檔案。' },
          { title_zh: '熱爾松書信集', title_orig: 'Epistolae Iohannis Gerson', author: '讓‧熱爾松', era: '約 1395–1429', place: '巴黎／康斯坦茨／里昂', language: '拉丁文／法文', intro: '巴黎大學校長熱爾松的書信集，貫穿西方大分裂的調解、康斯坦茨會議與晚年流亡，兼致其妹論在俗靈修的法文家書。書信展示「最後的經院公共知識分子」如何以筆維繫崩解中的基督教世界。' },
          { title_zh: '皮桑玫瑰論戰書信', title_orig: 'Le Débat sur le Roman de la Rose', author: '克莉絲蒂娜‧德‧皮桑', era: '1401–1403', place: '巴黎', language: '中古法文', intro: '職業女作家皮桑就《玫瑰傳奇》貶抑女性發起的公開論戰書信，與巴黎人文士子往復交鋒，熱爾松亦執筆聲援。這是歐洲文學史第一場由女性主導的筆戰，書信集開「女性之城」先聲，為中世紀性別論述的分水嶺。' },
          { title_zh: '伊什特萬王訓誡書', title_orig: 'Libellus de institutione morum (Admonitiones)', author: '匈牙利王聖伊什特萬（託名起草）', era: '約 1015–1027', place: '匈牙利艾斯特根', language: '拉丁文', intro: '匈牙利開國聖王伊什特萬致儲君埃默裡克的十章訓誡，以書信體傳授護持教會、禮遇外人、聽取諫言的治國之道。它是匈牙利文學的第一頁與「君王鑑」文類的東歐代表，見證新皈依王國如何以基督教倫理立國。' },
          { title_zh: '弗拉基米爾‧莫諾馬赫訓子書', title_orig: 'Pouchenie (Instruction of Vladimir Monomakh)', author: '弗拉基米爾‧莫諾馬赫', era: '約 1117', place: '基輔', language: '古東斯拉夫文', intro: '基輔大公莫諾馬赫晚年寫給諸子的訓誡書，自述徵戰與獵險的一生，勸子敬畏上帝、勤政恤民、莫恃武力。全文收於《往年紀事》勞倫抄本，是古羅斯文學最動人的自白，東斯拉夫「君王家訓」的孤峰之作。' },
          { title_zh: '阿納斯塔修斯圖書館長書信集', title_orig: 'Epistolae Anastasii Bibliothecarii', author: '圖書館長阿納斯塔修斯', era: '約 858–879', place: '羅馬', language: '拉丁文', intro: '教廷圖書館長阿納斯塔修斯身兼譯者與外交家，其書信涉君士坦丁堡第四次大公會議談判、為西里爾與美多德事業辯護，並附其希臘文獻拉丁譯序。他是九世紀羅馬僅存的希臘學橋樑，書信集兼具外交檔案與翻譯史料雙重價值。' }
        
        ]
      },
      {
        key: 'byzantine-eastern-letters',
        label: '拜占庭與東方書函部',
        label_en: 'Byzantine and Eastern Letters',
        desc: '拜占庭宗主教、文人與皇帝，及東方教會、亞美尼亞傳統的書信集。',
        works: [
          { title_zh: '狄奧多爾‧斯圖狄特書信集', title_orig: 'Epistolae Theodori Studitae', author: '斯圖狄奧斯的狄奧多爾', era: '約 795–826', place: '君士坦丁堡', language: '希臘文', intro: '斯圖狄奧斯修道院長狄奧多爾存世書信五百六十餘封，多成於三度流放中：抗辯皇帝干政、力挺聖像敬禮、遙領修道網絡。書信申言「皇帝無權定教義」，是拜占庭教會自由傳統最鏗鏘的文本，兼為破像爭議第二期的核心史料。' },
          { title_zh: '佛提烏書信集', title_orig: 'Epistolae Photii', author: '君士坦丁堡宗主教佛提烏', era: '約 858–886', place: '君士坦丁堡', language: '希臘文', intro: '大學者宗主教佛提烏的書信近三百封，致新皈依的保加利亞君主鮑里斯的「君王鑑」長函與駁「和子句」的東方宗主教通函最為著名，後者揭開東西方神學論戰的序幕。書信集兼具帝國外交、教義論辯與古典書話，是九世紀拜占庭人文復興的縮影。' },
          { title_zh: '尼古拉‧密斯提科斯書信集', title_orig: 'Epistolae Nicolai Mystici', author: '宗主教尼古拉一世密斯提科斯', era: '901–925', place: '君士坦丁堡', language: '希臘文', intro: '君士坦丁堡宗主教尼古拉的百餘封書信，以攝政身分致保加利亞沙皇西美昂的乞和與訓斥諸函絕妙，致阿拔斯哈里發為賽普勒斯基督徒請命的信更展示跨宗教外交的身段。皇帝四婚案中他寧遭放逐不肯通融，書信集是拜占庭政教角力的一等文獻。' },
          { title_zh: '米海爾‧普塞洛斯書信集', title_orig: 'Epistolae Michaelis Pselli', author: '米海爾‧普塞洛斯', era: '約 1040–1078', place: '君士坦丁堡', language: '希臘文', intro: '十一世紀首席文人普塞洛斯的五百餘封書信，周旋七朝宮廷，為友人求官、與修士論學、向皇帝獻策，修辭機巧百變。書信與其《編年史》互為表裡，是拜占庭官僚文人生態與「哲學復興」的活體標本。' },
          { title_zh: '奧赫裡德的狄奧菲拉克特書信集', title_orig: 'Epistolae Theophylacti Achridensis', author: '奧赫裡德的狄奧菲拉克特', era: '約 1090–1108', place: '奧赫裡德', language: '希臘文', intro: '出任保加利亞奧赫裡德總主教的拜占庭學者狄奧菲拉克特的書信集，自嘲流放蠻鄉卻為斯拉夫信眾抵擋帝國稅吏，兼與都城故舊論學問政。書信呈現拜占庭菁英與斯拉夫教會的複雜共生，為巴爾幹教會史的珍稀內部視角。' },
          { title_zh: '米海爾‧霍尼亞特斯書信集', title_orig: 'Epistolae Michaelis Choniatae', author: '米海爾‧霍尼亞特斯', era: '約 1182–1222', place: '雅典', language: '希臘文', intro: '雅典都主教米海爾‧霍尼亞特斯（史家尼基塔斯之兄）的書信集，哀嘆古城雅典的凋敝、第四次十字軍後流亡基亞島仍遙牧信眾。其信文筆典雅而情辭悲愴，是拉丁人統治希臘時代東方教會處境的第一手見證。' },
          { title_zh: '宗主教阿塔納修一世書信集', title_orig: 'Epistolae Athanasii I patriarchae', author: '君士坦丁堡宗主教阿塔納修一世', era: '1289–1309', place: '君士坦丁堡', language: '希臘文', intro: '苦行僧出身的宗主教阿塔納修一世致皇帝安德洛尼卡二世的書信近二百封，為飢民請命、斥責權貴囤糧、要求驅逐腐敗教士，凡俗政務無所不諫。這批信是拜占庭衰世社會史的獨家檔案，展現宗主教作為「窮人喉舌」的一面。' },
          { title_zh: '普拉努德斯書信集', title_orig: 'Epistolae Maximi Planudis', author: '馬克西姆‧普拉努德斯', era: '約 1292–1305', place: '君士坦丁堡', language: '希臘文', intro: '精通拉丁文的拜占庭學僧普拉努德斯的百餘封書信，論及其翻譯奧古斯丁與波愛修的譯業、蒐書校書之勞與出使威尼斯之行。他是帕列奧洛格文藝復興的樞紐人物，書信集見證東西學術於決裂後的罕見雙向流動。' },
          { title_zh: '迪米特里‧基多尼斯書信集', title_orig: 'Epistolae Demetrii Cydonis', author: '迪米特里‧基多尼斯', era: '約 1345–1391', place: '君士坦丁堡', language: '希臘文', intro: '三朝首相基多尼斯的四百五十封書信，記其翻譯阿奎那、皈依天主教、力主聯西抗突的一生。書信兼具政局密報與人文書話，是拜占庭末世「拉丁派」知識分子的心靈檔案，帕列奧洛格時代書信文學之冠。' },
          { title_zh: '曼努埃爾二世皇帝書信集', title_orig: 'Epistolae Manuelis II Palaeologi', author: '皇帝曼努埃爾二世', era: '約 1383–1417', place: '君士坦丁堡／西歐', language: '希臘文', intro: '末代雄主曼努埃爾二世的六十八封書信，自鄂圖曼軍營中論學、遍訪巴黎倫敦乞援時報聞，皇帝而兼文人，筆下盡是帝國黃昏。與其《與波斯人對話》同為拜占庭絕響，書信集是「歐洲最後的希臘皇帝」的自畫像。' },
          { title_zh: '尼基弗魯斯‧格雷戈拉斯書信集', title_orig: 'Epistolae Nicephori Gregorae', author: '尼基弗魯斯‧格雷戈拉斯', era: '約 1330–1358', place: '君士坦丁堡', language: '希臘文', intro: '史家格雷戈拉斯的百餘封書信，前期論天文曆法與古典學問，後期自軟禁的修道院中痛斥帕拉馬斯派得勢。書信與其《羅馬史》互補，呈現靜修論戰失敗一方的處境，是十四世紀拜占庭思想鬥爭的私檔。' },
          { title_zh: '狄奧多爾二世皇帝書信集', title_orig: 'Epistolae Theodori II Lascaris', author: '皇帝狄奧多爾二世‧拉斯卡里斯', era: '約 1254–1258', place: '尼西亞', language: '希臘文', intro: '尼西亞流亡帝國的哲學家皇帝狄奧多爾二世的書信集，與師友論亞里斯多德、談帝國復興藍圖，兼涉與教廷的合一試探。皇帝短壽而文名長存，書信展現流亡宮廷以學術自持的精神世界，為尼西亞時期文化史要籍。' },
          { title_zh: '提摩太一世書信集', title_orig: 'Epistolae Timothei I', author: '東方教會大公牧首提摩太一世', era: '約 780–823', place: '巴格達', language: '敘利亞文', intro: '東方亞述教會牧首提摩太一世存世書信五十九封，坐鎮阿拔斯都城巴格達，調度自美索不達米亞至中亞、印度的教省，派遣宣教士越蔥嶺，並記與哈里發的神學對談。這批書信是景教全盛期「巴格達治世界」的行政與宣教總檔。' },
          { title_zh: '內爾謝斯‧施諾爾哈利大公書信', title_orig: 'T\'ught\' Endhanrakan (General Epistle)', author: '內爾謝斯四世‧施諾爾哈利', era: '1166–1173', place: '赫羅姆克拉', language: '亞美尼亞文', intro: '亞美尼亞卡託利科斯「恩典者」內爾謝斯四世就任時致全民族的大公書信，訓誨各階層信德與操守；其與拜占庭皇帝曼努埃爾一世的教會合一往來書信亦傳世。文辭出自民族大詩人之手，是亞美尼亞教會牧函文類的巔峰與普世對話的先驅。' },
          { title_zh: '格里高利‧馬吉斯特羅斯書信集', title_orig: 'T\'ght\'er (Letters of Grigor Magistros)', author: '格里高利‧馬吉斯特羅斯', era: '約 1045–1058', place: '亞美尼亞／美索不達米亞', language: '亞美尼亞文', intro: '亞美尼亞貴族學者馬吉斯特羅斯的八十八封書信，為亞美尼亞文學首部俗人書信集，論希臘哲學、駁湯德拉克派異端、記拜占庭治下的宦遊。其文炫學好僻典，開亞美尼亞「希臘化文風」極致，是十一世紀亞美尼亞知識史的獨家資料。' },
          { title_zh: '雅巴拉哈三世與教廷往來書信', title_orig: 'Correspondence of Yahballaha III with the Papacy', author: '東方教會牧首雅巴拉哈三世', era: '1287–1304', place: '馬拉蓋／巴格達', language: '敘利亞文／拉丁文', intro: '畏兀兒出身的東方教會牧首雅巴拉哈三世與教宗尼各老四世、卜尼法八世的往來書信，隨拉班掃馬出使歐洲而啟，函中自陳信仰以釋西方之疑。這批書信是蒙古時代景教與羅馬空前的直接對話，見證基督教世界曾經的歐亞全幅圖景。' }
        
        ]
      },
      {
        key: 'zhengjiao-boyi',
        label: '政教博弈書信部',
        label_en: 'Letters of Church-State Contest',
        desc: '教權與王權角力、跨國外交往來的文書與國書。',
        works: [
          { title_zh: '敘任權之爭文書', title_orig: 'Documenta Controversiae de Investitura', author: '額我略七世、亨利四世等', era: '11 世紀末', place: '神聖羅馬帝國／羅馬', language: '拉丁文', intro: '圍繞主教敘任權，教宗額我略七世與皇帝亨利四世互相廢黜的往來文書與聲明：亨利致信宣告廢黜教宗，教宗則開除其教籍並解除臣民效忠，終致卡諾莎雪地請罪。這批針鋒相對的書信與宣告，是中世紀政教二權正面交鋒的核心檔案，奠定此後數百年敘任權與教俗權界之爭的基調。' },
          { title_zh: '卡爾大帝與哈倫‧拉希德外交國書', title_orig: 'Litterae inter Carolum Magnum et Hārūn al-Rašīd', author: '查理曼、哈倫‧拉希德（朝廷代擬）', era: '約 797–807 年', place: '亞琛／巴格達', language: '拉丁文／阿拉伯文', intro: '法蘭克皇帝查理曼與阿拔斯哈里發哈倫‧拉希德之間透過使節往來的外交接觸，留下饋贈與通好的記載，相傳哈里發贈以大象「阿布阿巴斯」與報時水鐘。雖正式國書原件多不存、細節雜有傳說，這段橫跨地中海的東西通使仍是加洛林帝國與伊斯蘭世界外交往來最著名的一頁，反映兩大政權的相互承認與務實聯絡。' },
          { title_zh: '阿萊克修斯一世致佛蘭德斯伯爵書', title_orig: 'Epistula Alexii I ad Robertum Flandrensem', author: '託名皇帝阿萊克修斯一世', era: '約 1091（傳本或經潤飾）', place: '君士坦丁堡', language: '拉丁文', intro: '以拜占庭皇帝阿萊克修斯一世名義致佛蘭德斯伯爵羅貝爾的求援書，歷數突厥人蹂躪東方教會之狀，籲西方騎士馳援。學界多認為現存拉丁文本經西方潤飾增衍，然其流傳直接催化第一次十字軍的輿論，是政教宣傳史的經典文本。' },
          { title_zh: '第一次十字軍諸侯書信', title_orig: 'Epistulae et chartae primae cruciatae', author: '布洛瓦的斯蒂芬、安條克諸侯等', era: '1097–1099', place: '小亞細亞／安條克／耶路撒冷', language: '拉丁文', intro: '第一次十字軍途中諸侯與教士發回西方的書信集：斯蒂芬伯爵致妻阿黛拉的家書、安條克圍城中致烏爾班二世的聯名求援、克萊芒致教會的捷報。這批當時書信未經後世潤飾，是十字軍史料中最接近現場的聲音。' },
          { title_zh: '哈德良四世貝桑松文書', title_orig: 'Litterae Besontinae Hadriani IV', author: '教宗哈德良四世／腓特烈一世廷臣', era: '1157–1158', place: '貝桑松／羅馬', language: '拉丁文', intro: '教宗哈德良四世致腓特烈一世的函件以「beneficia」一詞暗示帝位受於教宗，帝國宮廷解作「封地」而譁然，宰相雷納德當眾宣讀引爆衝突。往來澄清文書構成「貝桑松事件」全案，是中世紀政教語義戰的最著名個案。' },
          { title_zh: '亨利四世書信集', title_orig: 'Epistolae Heinrici IV', author: '皇帝亨利四世', era: '1073–1106', place: '帝國諸地', language: '拉丁文', intro: '亨利四世存世書信四十餘封，一〇七六年致額我略七世「下臺，下臺，你這永受詛咒者」的絕罪書震動歐洲，晚年致法王與諸侯自辯遭子逼宮的家國之痛尤為動人。這批書信是敘任權之爭皇帝一方的自我陳述，與教宗登記冊互為攻防。' },
          { title_zh: '貝克特往來書信集', title_orig: 'Correspondence of Thomas Becket', author: '託馬斯‧貝克特及其書記圈', era: '1162–1170', place: '坎特伯裡／法蘭西流亡地', language: '拉丁文', intro: '坎特伯裡大主教貝克特與亨利二世、教廷及英格蘭主教團的往來書信七百餘件，由其書記圈於殉道後彙編。書信逐日記錄教會自由與王權的攤牌至血濺聖壇，規模與密度為十二世紀之最，是中世紀政教衝突的完整卷宗。' },
          { title_zh: '坎特伯雷基督堂書信集', title_orig: 'Epistolae Cantuarienses', author: '坎特伯裡基督堂修士團', era: '1187–1199', place: '坎特伯裡', language: '拉丁文', intro: '坎特伯裡座堂修士團為抵制大主教另建教士團而與教廷、王室往來的五百餘封書信，修士遭圍困斷糧仍籲告不絕。這批檔案完整呈現一場中世紀教會內部訴訟的攻防全程，為修道團體法權意識的獨特見證。' },
          { title_zh: '祭司王約翰書信', title_orig: 'Epistola presbyteri Iohannis', author: '佚名西方作者（託名祭司王約翰）', era: '約 1165', place: '西歐（託稱印度）', language: '拉丁文', intro: '託名東方基督徒大君「祭司王約翰」致拜占庭皇帝的奇書，自誇其國七十二王來朝、遍地奇珍無罪惡。書信實出西方之手，卻風靡數百年、譯成諸語，驅動歐洲人東尋盟友直至衣索比亞與亞洲深處，是中世紀地理想像與十字軍心態的鑰匙文本。' },
          { title_zh: '彼得‧德‧維內亞書信集', title_orig: 'Epistolae Petri de Vinea', author: '彼得‧德‧維內亞', era: '約 1220–1249', place: '西西里宮廷', language: '拉丁文', intro: '腓特烈二世首席文膽維內亞的書信集，帝國與教廷筆戰的檄文多出其手，修辭華贍成「書信術」典範，中世紀晚期各國文書競相傳抄為公文範本。維內亞終遭猜忌自盡、入但丁地獄篇，其書信集是帝國文書藝術的最高峰。' },
          { title_zh: '腓特烈二世與額我略九世論戰文書', title_orig: 'Encyclicae Friderici II et Gregorii IX', author: '腓特烈二世／額我略九世', era: '1227–1241', place: '西西里／羅馬', language: '拉丁文', intro: '皇帝與教宗互相絕罰、互指對方為「敵基督」的通函戰：教宗斥皇帝為海中巨獸，皇帝籲諸王共抗教廷貪權。雙方文膽把末世意象投入政治宣傳，開近代輿論戰先河，這批文書是中世紀政教決裂最壯觀的言語交鋒。' },
          { title_zh: '利烏特普蘭德出使報告書', title_orig: 'Relatio de legatione Constantinopolitana', author: '克雷莫納的利烏特普蘭德', era: '968–969', place: '君士坦丁堡／克雷莫納', language: '拉丁文', intro: '奧託一世遣克雷莫納主教利烏特普蘭德使拜占庭求婚聯姻，遭冷遇而歸，憤而以書信體報告痛詆拜占庭宮廷的傲慢與希臘酒食。全文毒舌淋漓，是中世紀東西方相互認知（與誤解）最生動的外交文獻。' },
          { title_zh: '雅各‧德‧維特里東方書信集', title_orig: 'Epistolae Iacobi de Vitriaco', author: '雅各‧德‧維特里', era: '1216–1221', place: '阿卡／達米埃塔', language: '拉丁文', intro: '阿卡主教維特里自聖地與第五次十字軍達米埃塔前線發回歐洲的七封長信，實錄十字軍營中的罪惡、東方諸教派的樣貌與成吉思汗崛起的最早西傳情報。書信兼具佈道家之眼與記者之筆，是拉丁東方社會史的一級史料。' },
          { title_zh: '但丁書信集', title_orig: 'Epistolae Dantis', author: '但丁‧阿利吉耶裡', era: '約 1304–1320', place: '流亡義大利諸地', language: '拉丁文', intro: '但丁流亡期間的十三封拉丁書信，籲亨利七世南下重整義大利、斥佛羅倫斯同胞、致樞機團哀教廷遷亞維儂，致斯卡拉大公函並自解《神曲》寓意。書信是詩人政治神學的直接陳述，與《帝制論》互為表裡。' },
          { title_zh: '腓力四世與卜尼法八世論戰文書', title_orig: 'Acta controversiae Bonifatii VIII et Philippi IV', author: '法蘭西王廷／教廷文膽', era: '1296–1303', place: '巴黎／羅馬', language: '拉丁文', intro: '美男子腓力四世與卜尼法八世決裂全程的往來文書：偽造的「聽著，兒子」譏諷函、王廷散佈的指控書、阿納尼之辱前後的檄文。這場文書戰以教宗蒙羞告終，宣告主權國家壓倒普世教權，是中世紀政教關係的轉捩檔案。' },
          { title_zh: '西方大分裂文書', title_orig: 'Acta Schismatis Occidentalis', author: '羅馬與亞維儂兩系教廷／巴黎大學', era: '1378–1417', place: '羅馬／亞維儂／巴黎', language: '拉丁文', intro: '西方大分裂期間兩位乃至三位教宗互相絕罰的詔書、各國表態文書與巴黎大學徵集的合一方案書信。這批文書呈現基督教世界權威崩解與「會議至上論」興起的全過程，終結於康斯坦茨會議，是教會憲政思想的孵化檔案。' },
          { title_zh: '奧坎致小兄弟會書信', title_orig: 'Epistola ad Fratres Minores', author: '奧坎的威廉', era: '1334', place: '慕尼黑', language: '拉丁文', intro: '奧坎自亞維儂出奔投靠巴伐利亞的路易後，致方濟會全會的公開信，宣告若望二十二世因神貧問題與真福直觀謬說已自陷異端，籲全會抗命。此信是中世紀「以良知抗教宗」的radical宣言，開其晚年政教論戰著作的先聲。' },
          { title_zh: '聖女貞德口述書信', title_orig: 'Lettres de Jeanne d\'Arc', author: '聖女貞德（口述）', era: '1429–1431', place: '奧爾良／貢比涅', language: '中古法文', intro: '不識字的貞德口述、由書記代筆的書信，致英格蘭王「奉天上君王之命離開法蘭西」的最後通牒、致胡斯派的討伐書與致蘭斯市民的安撫函，三封留有其親筆簽名。這批書信是這位農家女以神啟號令王侯的直接物證，審判時反成罪狀。' },
          { title_zh: '揚‧胡斯獄中書信集', title_orig: 'Listy Jana Husa / Epistolae Iohannis Hus', author: '揚‧胡斯', era: '1414–1415', place: '康斯坦茨', language: '捷克文／拉丁文', intro: '胡斯赴康斯坦茨會議繫獄至就刑前的書信，以捷克文致布拉格全體信眾、以拉丁文致師友，自陳寧死不背真理的心跡，臨刑前夕之函尤為淒切。這批獄中書信使胡斯之死化為波希米亞民族與改革運動的精神原點。' },
          { title_zh: '聖文生‧費雷爾論敵基督書信', title_orig: 'Epistola de Antichristo (ad Benedictum XIII)', author: '文生‧費雷爾', era: '1412', place: '亞拉岡', language: '拉丁文', intro: '道明會佈道家文生‧費雷爾致亞維儂教宗本篤十三世的長信，申論大分裂亂象即敵基督將臨之兆，自述其巡迴佈道所見的悔改浪潮。此信是中世紀晚期末世佈道運動的綱領文本，兼證分裂如何撕裂一代人的教會忠誠。' },
          { title_zh: '教廷與蒙古往來國書', title_orig: 'Correspondence between the Papacy and the Mongol Khans', author: '英諾森四世／貴由汗等', era: '1245–1248', place: '里昂／哈拉和林', language: '拉丁文／波斯文', intro: '英諾森四世遣柏朗嘉賓齎書勸蒙古大汗止殺受洗，貴由汗以波斯文回書反令教宗率諸王來朝臣服，原件今存梵蒂岡檔案館。這組國書是歐洲與草原帝國最早的正式外交對話，雙方各以天命自居，錯身而過的姿態意味深長。' }
        
        ],
      },
    ],
  },
  wai: {
    summary: '基督教世界以外的書簡往來：伊斯蘭哈里發致基督教君主的外交國書，及猶太社群的書簡與經師回覆。',
    divisions: [
      {
        key: 'yisilan-shujian',
        label: '伊斯蘭書簡部',
        label_en: 'Islamic Correspondence',
        desc: '阿拔斯哈里發致拜占庭與法蘭克的外交國書。',
        works: [
          { title_zh: '阿拔斯哈里發致拜占庭國書', title_orig: 'Risālat al-Khalīfa ilā Imbarāṭūr al-Rūm', author: '阿拔斯朝廷', era: '9 世紀', place: '巴格達', language: '阿拉伯文', intro: '阿拔斯哈里發與拜占庭皇帝之間，圍繞邊境戰和、俘虜交換與貢賦而往來的外交書信。書信常以伊斯蘭與基督教兩大政權對峙的辭令交鋒，間或夾帶宗教論辯與威嚇。這類國書是研究九世紀地中海東部兩強角力與外交辭令藝術的材料，從伊斯蘭一方呈現其對「羅馬」基督教帝國的觀感與交涉策略。' },
          { title_zh: '阿拔斯哈里發致法蘭克通好書', title_orig: 'Risālat al-Khalīfa ilā Mulūk al-Faranja', author: '阿拔斯朝廷', era: '8–9 世紀', place: '巴格達', language: '阿拉伯文', intro: '配合查理曼與哈倫‧拉希德通使之事，阿拔斯朝廷致法蘭克君主的通好與饋贈文書。哈里發視這支地中海西端的基督教強權為可資聯絡、共制拜占庭與後伍麥亞的力量，書信遂帶務實結好之意。雖傳世細節多賴拉丁編年轉述，這條跨越歐亞的外交線索仍是早期伊斯蘭世界主動經營對歐關係的見證。' },
        ],
      },
      {
        key: 'youtai-shujian',
        label: '猶太書簡部',
        label_en: 'Jewish Correspondence',
        desc: '猶太社群的日常與商貿書信檔案，及經師對信眾的牧函回覆。',
        works: [
          { title_zh: '開羅貯藏室文獻', title_orig: 'Cairo Geniza Documents', author: '中世紀地中海猶太社群', era: '約 10–13 世紀', place: '埃及福斯塔特', language: '猶太阿拉伯文／希伯來文', intro: '開羅本以斯拉會堂的「貯藏室」依猶太習俗存放不可隨意丟棄的帶神聖之名文書，意外保存了數十萬件中世紀文獻，含私人書信、商業契約、婚書與經師回覆。這批檔案如時光膠囊，重現地中海猶太社群橫跨埃及、北非、西西里與印度洋的商貿與家庭生活，是中世紀社會經濟史與猶太日常書信文化的無價寶藏。' },
          { title_zh: '致葉門猶太人書', title_orig: 'Iggeret Teiman', author: '邁蒙尼德', era: '約 1172 年', place: '埃及福斯塔特', language: '猶太阿拉伯文', intro: '葉門猶太社群在伊斯蘭強制改宗壓力與冒牌彌賽亞的雙重衝擊下，去信求教於大經師邁蒙尼德，他以這封公開牧函作答，安慰受迫害的同胞、駁斥假彌賽亞、勸勉堅守信仰。書信語調沉痛而堅定，兼具神學論證與牧靈關懷，是邁蒙尼德回應流散猶太人苦難處境的名篇，廣為傳抄而影響深遠。' },
        ],
      },
    ],
  },
},
    {
  key: 'liyi',
  name: '禮儀藏',
  name_en: 'Liturgy Treasury',
  glyph: '儀',
  genres: '彌撒‧日課‧聖事',
  summary: '中世紀基督宗教與其周邊一神信仰傳統的禮儀典籍總集，涵蓋拉丁西方的彌撒經書與聖事神學、東方拜占庭的事奉聖禮、各修會的日課經，並收伊斯蘭與猶太兩大鄰近傳統的祈念與祈禱儀軌，呈現「公共敬拜如何被文字定型」這一中世紀宗教生活的核心面向。',
  zheng: {
    summary: '基督宗教自身的禮儀典籍：羅馬與地方禮的彌撒、東方事奉聖禮、聖事神學論著，以及日課與聖頌傳統，構成西方與東方教會敬拜的文獻骨幹。',
    divisions: [
      {
        key: 'mass-sacraments',
        label: '彌撒與聖事部',
        label_en: 'Mass and Sacraments',
        desc: '羅馬彌撒經書的定型、英格蘭薩倫禮，以及隆巴德與阿奎那奠定的聖事與聖體神學。',
        works: [
          { title_zh: '羅馬彌撒經書', title_orig: 'Missale Romanum', author: '羅馬教會（歷代編訂）', era: '11–13 世紀定型', place: '羅馬', language: '拉丁文', intro: '中世紀盛期將原本分散於聖事禮典（Sacramentarium）、讀經目錄與唱經本的彌撒各部，整合為單一「全備彌撒經書」，包含禮儀年通用與專用經文、進堂詠、集禱經、奉獻經、感恩經（Canon Missae）與領聖體經。隨方濟各會等托缽修會攜帶傳布，逐步取代地方差異，奠定日後特倫多公會議統一版本的基礎，是拉丁西方彌撒文本標準化的關鍵里程碑。' },
          { title_zh: '薩倫禮', title_orig: 'Use of Sarum', author: '索爾茲伯里座堂（傳歸聖奧斯蒙德）', era: '11 世紀後期起', place: '英格蘭索爾茲伯里', language: '拉丁文', intro: '英格蘭索爾茲伯里座堂發展的羅馬禮地方用法，詳訂遊行、執事與輔禮人員的繁複動作、唱經與禮儀色彩，禮儀美學華麗而井然。中世紀晚期通行於英格蘭、威爾斯與愛爾蘭大部分地區，並影響蘇格蘭與北歐。其彌撒序文、聖母小日課與遊行經本廣為抄傳，是宗教改革前英倫禮儀的主流，後世聖公會公禱書多有承襲。' },
          { title_zh: '四部語錄論七件聖事', title_orig: 'Sententiarum libri quattuor (lib. IV)', author: '彼得‧隆巴德', era: '約 1150 年', place: '巴黎', language: '拉丁文', intro: '隆巴德在語錄第四卷系統論述聖事，首次明確將聖事定為七件（聖洗、堅振、聖體、告解、終傅、聖秩、婚配），界定聖事為「恩寵的有形標記」，既象徵又施予所指之恩。此書成為中世紀大學神學教學的標準教材，歷代神學家競相注釋，七聖事之數自此成為西方教會定論，奠定整個經院聖事神學的框架。' },
          { title_zh: '神學大全論聖體聖事', title_orig: 'Summa Theologiae III, qq. 73–83', author: '多瑪斯‧阿奎那', era: '約 1273 年', place: '巴黎—那不勒斯', language: '拉丁文', intro: '阿奎那在神學大全第三部詳論聖體聖事，運用亞里斯多德的實體與依附體範疇闡明「變體說」（transsubstantiatio）：餅酒之實體全然轉變為基督的體血，而其依附體（顏色、形狀、味道）依舊存留。同時論基督在聖體中的真實臨在、彌撒作為祭獻的意義與領聖體的果效，為西方聖體神學提供最縝密的哲學表述，影響深遠。', link: '/fathers' },
          { title_zh: '哈德良聖事書', title_orig: 'Sacramentarium Hadrianum (Gregorianum)', author: '羅馬教廷（哈德良一世贈本）', era: '約 784–791', place: '羅馬／亞琛', language: '拉丁文', intro: '教宗哈德良一世應卡爾大帝之請送往法蘭克宮廷的額我略型聖事書，經本篤‧阿尼安增補附錄以敷北方之用。此書欽定為帝國彌撒標準本，羅馬禮由此覆蓋西歐，是中世紀禮儀「羅馬化」工程的基石文獻。' },
          { title_zh: '德羅戈聖事書', title_orig: 'Drogo-Sakramentar', author: '梅斯主教德羅戈委製', era: '約 845–855', place: '梅斯', language: '拉丁文', intro: '卡爾大帝私生子、梅斯主教德羅戈委製的泥金聖事書，歷史化首字母內繪滿禮儀場景，主教行禮的圖像為禮儀史提供了罕見的「現場照片」。書藝與禮文互證，是加洛林禮儀文化最精美的實物。' },
          { title_zh: '羅馬-日耳曼主教禮書', title_orig: 'Pontificale Romano-Germanicum', author: '美因茲聖阿爾班修道院編', era: '約 950–963', place: '美因茲', language: '拉丁文', intro: '奧託王朝美因茲編成的大型主教禮書，網羅祝聖、加冕、驅魔與神判諸儀，隨帝國影響迴流羅馬，反成教廷禮儀的底本。「日耳曼禮反哺羅馬」為禮儀史著名的迴流案例，本書即其載體。' },
          { title_zh: '羅馬儀注書彙', title_orig: 'Ordines Romani', author: '羅馬教廷與法蘭克編者群', era: '8–10 世紀彙傳', place: '羅馬／法蘭克王國', language: '拉丁文', intro: '記述教宗彌撒、洗禮、葬禮等儀式進行程序的「儀注」文獻群，五十篇彙傳於加洛林抄本。聖事書載禱文而儀注載動作，二者互補方見禮儀全貌，本彙是重建早期中世紀羅馬禮實況的第一史料。' },
          { title_zh: '約克禮', title_orig: 'Use of York', author: '約克座堂傳統', era: '13–15 世紀定型', place: '約克', language: '拉丁文', intro: '英格蘭北部約克教省的地方禮儀傳統，彌撒與日課於羅馬禮框架內自具經文曆法，與南方薩倫禮並立。宗教改革前英格蘭「各地各禮」的多樣生態，即以約克禮為北方代表，其禮書印本存世可考。' },
          { title_zh: '安博禮彌撒書', title_orig: 'Missale Ambrosianum', author: '米蘭教會傳統', era: '中世紀定型（9–13 世紀抄本）', place: '米蘭', language: '拉丁文', intro: '米蘭教會獨立於羅馬禮的安博禮彌撒書，經課、聖歌與齋期制度自成一系，相傳溯自安博。它是西方唯一存活至今的非羅馬拉丁禮，中世紀抄本傳統為其千年延續的檔案，禮儀多樣性的活見證。' },
          { title_zh: '莫札拉布儀典書', title_orig: 'Liber Ordinum', author: '西哥德-莫札拉布教會傳統', era: '11 世紀抄本（傳統上溯 7 世紀）', place: '西班牙北部', language: '拉丁文', intro: '伊比利莫札拉布禮的主教與司鐸儀典書，收聖事、祝福與國王出征禮諸文，賴十一世紀silos等抄本傳世。羅馬禮席捲半島前的西班牙禮儀全貌俱在此中，是研究西哥德禮儀傳統的核心文獻。' },
          { title_zh: '斯托伊彌撒書', title_orig: 'Stowe Missal', author: '愛爾蘭修道教會', era: '約 792–812', place: '愛爾蘭（塔拉赫特一帶）', language: '拉丁文（附古愛爾蘭語）', intro: '現存最古的愛爾蘭彌撒書，袖珍一冊供行旅司鐸隨身，附古愛爾蘭語的彌撒釋義與三篇咒禱。它是凱爾特禮儀傳統碩果僅存的完整標本，兼為古愛爾蘭語文獻的珍品，愛爾蘭教會自主時代的遺珠。' },
          { title_zh: '杜蘭德主教禮書', title_orig: 'Pontificale Guillelmi Durandi', author: '威廉‧杜蘭德', era: '約 1292–1295', place: '芒德', language: '拉丁文', intro: '芒德主教杜蘭德重編的主教禮書，結構井然、儀文完備，迅速取代前代諸本，一五九五年欽定羅馬主教禮書即以此為底。一部地方主教的私修禮書終成普世範本，是中世紀禮儀編纂學的巔峰成就。' },
          { title_zh: '埃塞爾沃爾德祝福禮書', title_orig: 'Benedictional of St Æthelwold', author: '溫徹斯特畫坊（戈德曼繕寫）', era: '約 971–984', place: '溫徹斯特', language: '拉丁文', intro: '溫徹斯特主教埃塞爾沃爾德委製的主教祝福文集，「溫徹斯特畫派」金彩繁花的整頁畫為盎格魯-撒克遜書藝之冠。祝福禮文按禮儀年編排，兼證十世紀英格蘭修道復興的禮儀雄心，今藏大英圖書館。' },
          { title_zh: '論祭壇聖奧', title_orig: 'De sacro altaris mysterio', author: '英諾森三世', era: '約 1195–1197', place: '羅馬', language: '拉丁文', intro: '日後的教宗英諾森三世任樞機時所著的彌撒詮釋，逐段解說儀文的寓意與神學，兼記當時教廷禮儀實況。出自最有權勢教宗之手的禮儀學著作，流傳極廣，是中世紀彌撒理解的權威指南。' },
          { title_zh: '神聖禮儀提要', title_orig: 'Rationale divinorum officiorum', author: '威廉‧杜蘭德', era: '1286–1291', place: '芒德', language: '拉丁文', intro: '杜蘭德集中世紀禮儀寓意學大成的八卷鉅著，自教堂建築、祭衣顏色至彌撒每一動作皆釋其奧義。本書為中世紀最流行的禮儀百科，一四五九年印本為史上最早活字書之一，禮儀象徵神學的總匯。' },
          { title_zh: '論教會職務', title_orig: 'Liber officialis', author: '梅斯的阿馬拉里烏斯', era: '約 823', place: '梅斯', language: '拉丁文', intro: '加洛林禮儀學家阿馬拉里烏斯以寓意法詮釋彌撒與日課的鉅著，視儀式每一動作為基督生平的重演。其說雖遭里昂教會指為謬妄，卻風行中世紀而塑造整個禮儀觀看傳統，是禮儀寓意學的開山之作。' },
          { title_zh: '論教會禮儀之起源與增長', title_orig: 'Libellus de exordiis et incrementis rerum ecclesiasticarum', author: '瓦拉弗裡德‧斯特拉波', era: '約 841', place: '賴興瑙', language: '拉丁文', intro: '賴興瑙院長瓦拉弗裡德考述教堂、祭器、禱文與什一稅諸制度源流的小書，以歷史眼光代替寓意解釋，被譽為史上第一部禮儀史著作。其冷靜的發展觀在中世紀獨樹一幟，近代禮儀學的遠祖。' },
          { title_zh: '論神聖職務', title_orig: 'De divinis officiis (Rupertus Tuitiensis)', author: '多伊茨的魯珀特', era: '約 1111', place: '列日', language: '拉丁文', intro: '本篤會神學家魯珀特以救恩史神學重釋全年禮儀的十二卷著作，把禮儀年讀作聖言在時間中的展開。它超越瑣碎寓意而賦禮儀以神學整體，是中世紀禮儀神學最深沉的作品之一。' },
          { title_zh: '神聖職務大全', title_orig: 'Summa de ecclesiasticis officiis', author: '讓‧貝萊特', era: '約 1160–1164', place: '巴黎', language: '拉丁文', intro: '巴黎教師貝萊特為神學生編寫的禮儀教本，按禮儀年與儀式類別條分縷析，兼記民俗如愚人節之濫。本書為大學禮儀教學的標準讀物，抄本近二百部，杜蘭德《提要》的直接前驅。' },
          { title_zh: '彌撒鏡鑑', title_orig: 'Mitrale seu de officiis ecclesiasticis summa', author: '克雷莫納的西卡爾德', era: '約 1200', place: '克雷莫納', language: '拉丁文', intro: '克雷莫納主教、法學家兼史家西卡爾德的禮儀大全，融教會法學識於禮儀詮釋，體例嚴整。與貝萊特、杜蘭德同構成中世紀禮儀學的三部曲，展示倫巴底主教的博學傳統。' },
          { title_zh: '靈魂寶石', title_orig: 'Gemma animae', author: '奧頓的霍諾留', era: '約 1120', place: '雷根斯堡一帶', language: '拉丁文', intro: '霍諾留的禮儀詮釋書，以「彌撒為屬靈的戰役」等鮮活比喻解說儀文，視教堂為宇宙縮影。本書承阿馬拉里烏斯而更趨大眾化，為堂區教士講解禮儀的常備手冊，中世紀禮儀想像的普及媒介。' },
          { title_zh: '論主的身體與寶血（帕斯卡修斯）', title_orig: 'De corpore et sanguine Domini (Paschasius)', author: '帕斯卡修斯‧拉德貝爾圖斯', era: '831–833', place: '科爾比', language: '拉丁文', intro: '科爾比院長帕斯卡修斯撰寫的西方第一部聖體專論，主張祭壇上的即是童貞女所生、釘於十架的那真實身體。本書開聖體神學千年論辯之端，其實在論路線終成中世紀主流，聖體敬禮文化的理論奠基。' },
          { title_zh: '論主的身體與寶血（拉特拉姆努斯）', title_orig: 'De corpore et sanguine Domini (Ratramnus)', author: '拉特拉姆努斯', era: '約 843–850', place: '科爾比', language: '拉丁文', intro: '同院修士拉特拉姆努斯應禿頭查理之問而作的答辯，主張聖體乃「奧蹟中的真實」而非血肉可驗之變。本書於宗教改革時代重刊而成新教聖餐論的中世紀證人，一座修院的兩部同名書分執千年論辯的兩端。' },
          { title_zh: '聖體節禮文', title_orig: 'Officium de festo Corporis Christi', author: '託馬斯‧阿奎那（教宗烏爾班四世委任）', era: '1264', place: '奧爾維耶託', language: '拉丁文', intro: '烏爾班四世應列日的朱莉安娜畢生推動而立聖體節，委阿奎那編纂全套日課與彌撒禮文，〈皇皇聖體〉〈錫安讚美救主〉諸歌皆出其手。神學家親撰的禮文字字精嚴，是教義化為頌禱的完美範例。' },
          { title_zh: '平信徒彌撒書', title_orig: 'The Lay Folks\' Mass Book', author: '佚名（英格蘭北部）', era: '約 1300（源出 12 世紀法文本）', place: '英格蘭北部', language: '中古英語', intro: '以英語韻文教導平信徒望彌撒時逐段默禱的手冊，司鐸行禮於前、信眾按韻文私禱於後。它揭示中世紀會眾「平行參與」彌撒的實態，是禮儀社會史與英語敬虔文學交會的珍貴文本。' },
          { title_zh: '米爾克堂區司鐸指南', title_orig: 'Instructions for Parish Priests', author: '約翰‧米爾克', era: '約 1400', place: '什羅普郡', language: '中古英語', intro: '米爾克以英語韻文教導堂區司鐸施行聖事、聽告解與教導教理的實務手冊，連緊急為嬰孩施洗的用語都逐句拼出。本書是中世紀晚期英格蘭基層聖事牧養的操作寫真，堂區宗教生活史的一級史料。' },
          { title_zh: '王室加冕禮書', title_orig: 'Liber Regalis', author: '西敏寺繕寫室', era: '約 1382', place: '西敏寺', language: '拉丁文', intro: '西敏寺編定的英格蘭國王與王后加冕禮書，膏立、授器與誓詞的完整儀注沿用至今——一九五三年伊莉莎白二世加冕仍循其骨架。它是政治神學化為儀式的最長壽文本，君權聖化傳統的活化石。' },
          { title_zh: '尼達羅斯禮儀書', title_orig: 'Ordo Nidrosiensis Ecclesiae', author: '尼達羅斯總教省', era: '約 1200–1250', place: '特隆赫姆', language: '拉丁文', intro: '挪威尼達羅斯（特隆赫姆）總教省的禮儀規程，涵蓋聖奧拉夫崇敬與北國曆法的調適，管轄遠及冰島格陵蘭。它是斯堪的納維亞中世紀禮儀的核心文獻，見證羅馬禮在極北的本地化。' },
          { title_zh: '克呂尼諸靈節禮儀', title_orig: 'Statutum de defunctorum commemoratione (Odilo)', author: '克呂尼的奧迪洛', era: '998', place: '克呂尼', language: '拉丁文', intro: '克呂尼院長奧迪洛下令全體屬院於十一月二日為所有亡者舉行紀唸的規令，諸靈節由此誕生並漸行普世。一紙修院法令化為全教會的節日，是中世紀亡者代禱文化與克呂尼影響力的紀念碑。' },
          { title_zh: '三鐘經敬禮的成形', title_orig: 'Angelus (medieval formation)', author: '方濟會與歷代教宗推廣', era: '13–15 世紀', place: '義大利／全西歐', language: '拉丁文', intro: '晚鐘誦念聖母領報經文的習俗自十三世紀方濟會晚禱鐘推廣，經教宗屢頒大赦而定為晨午晚三次的三鐘經。教堂鐘聲把全村的時間織入救恩奧蹟，是中世紀日常生活禮儀化最深入的個案。' }
        
        ]
      },
      {
        key: 'byzantine-liturgy',
        label: '拜占庭事奉禮部',
        label_en: 'Byzantine Divine Liturgy',
        desc: '東方教會兩大事奉聖禮的中世紀定型，以及聖山阿索斯的隱修禮儀傳統。',
        works: [
          { title_zh: '金口約翰事奉聖禮', title_orig: 'Θεία Λειτουργία τοῦ ἁγίου Ἰωάννου τοῦ Χρυσοστόμου', author: '託名金口約翰（中世紀編訂）', era: '中世紀定型（8–14 世紀）', place: '君士坦丁堡', language: '希臘文', intro: '東正教平日與主日最常用的感恩事奉禮，雖冠以金口約翰之名，實為君士坦丁堡禮歷代增飾而成。中世紀經由《典範手冊》（Diataxis）與大牧首傳統逐步定型，包含序禮（preparation）、聖言事奉與聖祭事奉三大段，連禱、進堂與奉獻遊行、感恩經（anaphora）與領聖體經次第井然，是拜占庭禮儀文本的核心。' },
          { title_zh: '巴西流事奉聖禮', title_orig: 'Θεία Λειτουργία τοῦ Μεγάλου Βασιλείου', author: '託名大巴西流（中世紀編訂）', era: '中世紀定型', place: '凱撒利亞—君士坦丁堡', language: '希臘文', intro: '感恩經較長、神學內涵豐富的事奉聖禮，東正教於大齋期諸主日、若干大節前夕及聖巴西流瞻禮日舉行。其感恩經以宏大的救恩史敘事貫穿造化、墮落與救贖，被視為拜占庭禮儀文學的高峰。中世紀與金口約翰禮並行於同一套禮典手冊中，僅替換感恩經部分，餘者大體相同。' },
          { title_zh: '聖山阿索斯禮儀典章', title_orig: 'Τυπικὸν τοῦ Ἁγίου Ὄρους', author: '阿索斯諸隱修院（歷代）', era: '10–14 世紀', place: '希臘聖山阿索斯', language: '希臘文', intro: '阿索斯隱修共和國各院所遵行的禮儀章程（Typikon），規範通宵祈禱（Agrypnia）、晚課、晨課與時辰祈禱的次序、唱經調式與齋戒規矩。其禮儀深受靜修主義（Hesychasm）影響，強調連續不斷的禱告與耶穌禱文。聖山典章經薩瓦的耶路撒冷典章融合後，成為日後東正教世界通行的隱修與堂區禮儀標準。' },
          { title_zh: '預先祝聖事奉聖禮', title_orig: 'Λειτουργία τῶν Προηγιασμένων Δώρων', author: '拜占庭傳統（傳額我略對話者）', era: '7 世紀成制，中世紀定型', place: '君士坦丁堡', language: '希臘文', intro: '大齋平日不行感恩祭，而以先期祝聖的聖體行領聖體晚禱，是為預先祝聖禮儀。其肅穆的黃昏氛圍為拜占庭齋期靈修的核心體驗，中世紀禮書定其文本，至今正教會大齋週三週五仍行之。' },
          { title_zh: '大教堂典章', title_orig: 'Typikon of the Great Church', author: '聖索菲亞大教堂傳統', era: '9–10 世紀', place: '君士坦丁堡', language: '希臘文', intro: '君士坦丁堡聖索菲亞大教堂的禮儀典章，載「歌詠禮儀」的盛大程序：遊行貫穿全城、聖詠隊與會眾對答，皇帝與宗主教同臺演出帝國的神聖秩序。它是「城市禮儀」傳統的總譜，拜占庭禮儀史的基準文獻。' },
          { title_zh: '斯圖狄奧斯典章', title_orig: 'Studite Typikon', author: '斯圖狄奧斯修道院傳統（阿列克西斯宗主教編訂本）', era: '9–11 世紀', place: '君士坦丁堡', language: '希臘文', intro: '斯圖狄奧斯修道院的禮儀與生活典章，融大教堂禮儀與修道日課為中道，經阿列克西斯宗主教編訂本傳入基輔羅斯，為斯拉夫修道禮儀的第一個範本。拜占庭禮儀「修道化」進程的關鍵環節。' },
          { title_zh: '聖薩巴斯典章', title_orig: 'Typikon of St Sabas (Jerusalem Typikon)', author: '聖薩巴斯修道院傳統', era: '中世紀定型（12–14 世紀抄本）', place: '耶路撒冷曠野', language: '希臘文', intro: '耶路撒冷聖薩巴斯大修道院的禮儀典章，以徹夜守夜禮著稱，十四世紀起漸取代斯圖狄奧斯系而成拜占庭與斯拉夫正教的通行典章至今。一座曠野修院的作息表終規範半個基督教世界的敬拜時間。' },
          { title_zh: '菲洛塞奧斯禮規', title_orig: 'Diataxis tēs Theias Leitourgias', author: '宗主教菲洛塞奧斯‧科基諾斯', era: '約 1350–1370', place: '君士坦丁堡／阿索斯', language: '希臘文', intro: '靜修派宗主教菲洛塞奧斯編訂的事奉聖禮儀注，逐一規定司祭與輔祭的動作經文，終結各地行禮的紛歧。此禮規隨其權威傳遍正教世界，今日拜占庭禮的樣貌大體由它定格，是禮儀標準化的東方典範。' },
          { title_zh: '神聖禮儀詮釋', title_orig: 'Hermēneia tēs Theias Leitourgias', author: '尼古拉‧卡巴西拉斯', era: '約 1350', place: '帖撒羅尼迦', language: '希臘文', intro: '平信徒神學家卡巴西拉斯逐段默觀事奉聖禮的詮釋，視全禮為基督奧蹟的漸次顯現，深靜而不流於瑣碎寓意。本書與其《基督裡的生命》同為拜占庭禮儀靈修的雙璧，梵二禮儀神學亦屢引為源。' },
          { title_zh: '論聖殿與禮儀', title_orig: 'De sacro templo et liturgia (Symeon Thessalonicensis)', author: '帖撒羅尼迦的西默盎', era: '約 1420–1429', place: '帖撒羅尼迦', language: '希臘文', intro: '帖撒羅尼迦都主教西默盎以問答詳解聖殿空間、聖職祝聖與諸聖事的鉅著，成於城破前夕，儼然拜占庭禮儀傳統的總遺囑。其書至今為正教禮儀學的權威徵引，帝國黃昏最完整的禮儀百科。' },
          { title_zh: '八音頌唱集', title_orig: 'Oktōēchos', author: '拜占庭聖詩傳統（傳大馬士革的約翰奠基）', era: '中世紀定型', place: '耶路撒冷／君士坦丁堡', language: '希臘文', intro: '按八個調式循環編排每週日課聖頌的禮書，傳統歸功大馬士革的約翰而實經數百年層累。八音體系規範了拜占庭與斯拉夫教會的全部歌唱生活，是東方教會「以音階組織時間」的偉大發明。' },
          { title_zh: '三歌齋期禮典', title_orig: 'Triōdion', author: '斯圖狄奧斯詩人群（狄奧多爾兄弟等）', era: '9–10 世紀編成', place: '君士坦丁堡', language: '希臘文', intro: '大齋期前後十週的專用禮書，因平日晨禱聖頌僅三歌而得名，收懺悔聖頌與受難週全部禮文。斯圖狄奧斯詩人為其主要作者，安德烈的大懺悔聖頌亦在其中，是正教齋期靈性的文本總庫。' },
          { title_zh: '五旬節禮典', title_orig: 'Pentēkostarion', author: '拜占庭聖詩傳統', era: '中世紀編成', place: '君士坦丁堡', language: '希臘文', intro: '自復活夜至諸聖主日五十餘日的節期禮書，貫穿「基督復活」頌的凱旋基調，收帕斯卡聖頌與昇天、五旬節諸禮文。與三歌禮典互為悲喜兩極，合構正教禮儀年的心臟地帶。' },
          { title_zh: '每月禮典', title_orig: 'Mēnaia', author: '拜占庭聖詩傳統', era: '9–12 世紀編成', place: '君士坦丁堡', language: '希臘文', intro: '按十二個月每日聖人與節慶編排聖頌的十二巨冊禮書，收錄拜占庭聖詩傳統的主體，作者自羅曼諾斯以降數百家。它是東方教會聖人崇敬與詩歌神學的總集成，正教日課不可一日或缺的書架。' },
          { title_zh: '時課經', title_orig: 'Hōrologion', author: '拜占庭修道傳統', era: '中世紀定型', place: '巴勒斯坦／君士坦丁堡', language: '希臘文', intro: '載每日時辰祈禱固定框架的禮書，自夜半課至晚禱九個時辰的詩篇與禱文俱備，為誦經員與信眾的隨身基本書。其結構承巴勒斯坦修道傳統，是東方日課體系的骨架文獻。' },
          { title_zh: '正統勝利節禮文', title_orig: 'Synodikon of Orthodoxy', author: '君士坦丁堡教會', era: '843（後世增補）', place: '君士坦丁堡', language: '希臘文', intro: '八四三年聖像敬禮最終恢復，教會定大齋首主日為「正統勝利節」，誦讀宣認正統、絕罰異端的《宣言書》。此禮文隨世增補（後收帕拉馬斯論題），成為以禮儀宣告教義的獨特文獻，至今每年誦讀。' },
          { title_zh: '歐可洛吉翁大禮書', title_orig: 'Euchologion', author: '拜占庭教會傳統', era: '中世紀諸抄本定型', place: '君士坦丁堡', language: '希臘文', intro: '司祭與主教用的總禮書，收三種事奉聖禮與洗禮、婚冠、傅油、葬禮及各式祝福禱文，相當於西方聖事書與主教禮書之合。中世紀抄本譜系是重建拜占庭聖事史的基礎，東方禮儀文獻的母船。' },
          { title_zh: '斯提凱拉里翁與伊爾莫洛吉翁', title_orig: 'Stichērarion / Heirmologion', author: '拜占庭聖樂傳統', era: '10–14 世紀譜本', place: '君士坦丁堡／阿索斯', language: '希臘文', intro: '拜占庭記譜法寫定的兩大聖歌譜集：前者收節慶自成調聖頌，後者收典範旋律「伊爾莫斯」。這批紐姆譜本使千年拜占庭旋律得以破譯重唱，是東方教會音樂考古的羅塞塔石。' },
          { title_zh: '薩瓦聖山典章', title_orig: 'Karyes Typikon (St Sava)', author: '聖薩瓦（塞爾維亞）', era: '1199', place: '阿索斯卡里埃斯', language: '教會斯拉夫文', intro: '塞爾維亞王子出家的聖薩瓦為阿索斯隱修室手訂的典章，羊皮原件存希蘭達爾修道院，後其希蘭達爾與斯圖德尼察典章奠定塞爾維亞教會禮儀生活。一紙典章開啟一個民族教會，斯拉夫修道立法的原點。' }
        
        ]
      },
      {
        key: 'eastern-rites',
        label: '東方諸禮部',
        label_en: 'Oriental Rites',
        desc: '亞美尼亞、敘利亞東西兩支、科普特、衣索比亞、喬治亞與斯拉夫傳統的中世紀禮典。',
        works: [
          { title_zh: '亞美尼亞聖祭禮', title_orig: 'Patarag (Badarak)', author: '亞美尼亞使徒教會傳統', era: '中世紀定型', place: '亞美尼亞', language: '古典亞美尼亞文', intro: '亞美尼亞教會的感恩祭禮文，融耶路撒冷、卡帕多細亞源流而自成一格：無酵餅、不摻水之酒與垂簾行禮為其特徵。中世紀教父的詮釋與增訂定其今貌，是亞美尼亞民族信仰認同的禮儀核心。' },
          { title_zh: '亞美尼亞時課經', title_orig: 'Zhamagirk', author: '亞美尼亞教會傳統', era: '中世紀編成', place: '亞美尼亞', language: '古典亞美尼亞文', intro: '亞美尼亞教會的日課經書，九個時辰的詩篇、聖頌與禱文按古老的耶路撒冷架構編排，施諾爾哈利等詩人之作累世增益。它是亞美尼亞語詩歌與靈修的活水庫，民族苦難中維繫共同祈禱的紐帶。' },
          { title_zh: '馬什託茨禮書', title_orig: 'Mashtots (Armenian Ritual)', author: '亞美尼亞教會傳統（託名馬什託茨卡託利科斯）', era: '9 世紀編定', place: '亞美尼亞', language: '古典亞美尼亞文', intro: '亞美尼亞的聖事禮典，洗禮、婚配、葬禮與家宅祝福諸文俱備，以九世紀編訂者馬什託茨卡託利科斯為名。其葬禮與祝福文保存大量古東方禮素材，是亞美尼亞聖事生活的總本。' },
          { title_zh: '侯德拉禮典', title_orig: 'Ḥudra', author: '東方教會（伊修雅布三世主持編訂）', era: '7 世紀編定，中世紀增補', place: '美索不達米亞', language: '敘利亞文', intro: '東方亞述教會全年主日與節期的禮文總集，牧首伊修雅布三世主持編定，「侯德拉」意為「循環」。其禮儀年以「教會奉獻節」收尾自成一格，是東敘利亞傳統千年敬拜的母本，景教禮儀的總源。' },
          { title_zh: '芬基託節期頌集', title_orig: 'Fenqitho', author: '敘利亞正教傳統', era: '中世紀編成', place: '敘利亞／美索不達米亞', language: '敘利亞文', intro: '敘利亞正教會的節期聖頌總集，收以法蓮、雅各‧德‧塞魯格傳統的詩體禮文，按全年節慶編排達七巨冊。它是敘利亞詩歌神學的禮儀化總匯，米亞菲西傳統敬拜生活的文本主體。' },
          { title_zh: '科普特聖週禮典', title_orig: 'Book of the Holy Pascha', author: '科普特教會傳統', era: '中世紀編定', place: '埃及', language: '科普特文／阿拉伯文', intro: '科普特教會受難週的專用禮典，自聖枝主日至復活夜逐時辰誦讀經課與哀歌，「上帝之力」古調徹夜迴盪。其編排保存早期耶路撒冷聖週禮的古層，是埃及教會苦難靈修的年度高峰文本。' },
          { title_zh: '讚美瑪利亞', title_orig: 'Weddāsē Māryām', author: '衣索比亞教會傳統', era: '14–15 世紀定型', place: '衣索比亞', language: '吉茲文', intro: '衣索比亞教會按週日循環讚美聖母的日課詩集，與《衣索比亞讚美詩》並用，會眾配鼓與叉鈴詠唱。它是衣索比亞獨特聖母敬禮的核心文本，非洲基督教禮儀詩歌自主發展的代表。' },
          { title_zh: '伊亞德加里聖頌禮書', title_orig: 'Iadgari', author: '喬治亞教會傳統', era: '9–10 世紀抄本', place: '耶路撒冷／喬治亞', language: '喬治亞文', intro: '喬治亞語的古聖頌禮書，因保存已佚的耶路撒冷希臘禮儀年全貌而為禮儀學至寶——聖城之禮竟賴高加索譯本傳世。新舊兩種《伊亞德加里》是重建五至八世紀耶路撒冷敬拜的鑰匙文獻。' },
          { title_zh: '基輔禮書殘葉', title_orig: 'Kiev Missal (Kyivski hlaholychni lystky)', author: '斯拉夫宣教傳統（美多德圈）', era: '約 900', place: '大摩拉維亞／潘諾尼亞', language: '教會斯拉夫文', intro: '七葉格拉哥里字母的彌撒禮文殘卷，內容為羅馬禮聖事書的斯拉夫語譯本，被視為現存最古的教會斯拉夫語抄本。它證明西里爾-美多德傳統曾以斯拉夫語行羅馬禮，東西禮儀交會的獨一無二物證。' }
        
        ]
      },
      {
        key: 'office-hymnody',
        label: '日課與聖頌部',
        label_en: 'Divine Office and Hymnody',
        desc: '中世紀時辰祈禱的日課經，以及本篤、熙篤、道明等各修會的禮儀規制。',
        works: [
          { title_zh: '日課經', title_orig: 'Breviarium', author: '羅馬教會與各修會（歷代）', era: '11–13 世紀定型', place: '羅馬與各修院', language: '拉丁文', intro: '將時辰祈禱（晨禱、讚禱、各時辰小禱、晚禱、夜禱）所需的聖詠、對經、讀經、應答詠與聖人傳記濃縮為一冊的綜合禮典，便於個人或行旅誦念。原為隱修院唱詠用書的合編，方濟各會將其攜帶傳布後通行於全教會。其聖詠週循環與聖人曆構成西方教會每日公共祈禱的骨架，為日後羅馬日課經的前身。' },
          { title_zh: '本篤會規論神工', title_orig: 'Regula Benedicti (de Opere Dei)', author: '努西亞的本篤', era: '6 世紀（中世紀通行）', place: '義大利卡西諾山', language: '拉丁文', intro: '本篤會規以「神工」（Opus Dei，即時辰祈禱）為隱修生活的中心，詳定每日七次日間祈禱與一次夜禱的時刻、所誦聖詠的分配，要求一週內誦完全部一百五十篇聖詠。此一安排成為西方隱修日課的母型，中世紀本篤系各院皆奉行之，深刻塑造了拉丁教會禮儀時間的節律與聖詠誦念傳統。' },
          { title_zh: '熙篤會日課與遊行禮典', title_orig: 'Ecclesiastica Officia Cisterciensia', author: '熙篤會總會', era: '12 世紀', place: '法國熙篤', language: '拉丁文', intro: '熙篤會為追求本篤會規的純樸本義，刪除中世紀累積的繁飾，制定簡素清明的日課與遊行章程，強調素歌（plainchant）的純淨與禮儀的節制。其禮典規範彌撒、日課、遊行與一年禮儀年的細節，反映熙篤改革「返本歸源」的精神，與克呂尼系的華麗禮儀形成鮮明對比，影響中世紀盛期的隱修禮儀風尚。' },
          { title_zh: '道明會禮儀規制', title_orig: 'Ordinarium Ordinis Praedicatorum', author: '道明會（胡姆伯特編訂）', era: '13 世紀', place: '巴黎', language: '拉丁文', intro: '道明會第五任總會長薩克森的胡姆伯特統整全會分歧的禮儀用法，編成統一的彌撒、日課、唱經與遊行規制，史稱「胡姆伯特法典」。此舉使分散各地、以講道與遊學為務的道明會弟兄無論身在何處皆能依同一禮本祈禱，是托缽修會禮儀統一化的典範，也保存了一套有別於羅馬與薩倫的獨特中世紀禮儀傳統。' },
          { title_zh: '方濟會改訂羅馬日課', title_orig: 'Breviarium Romanae Curiae (recensio Haymonis)', author: '法弗舍姆的海莫主持', era: '1243–1244', place: '羅馬／巴黎', language: '拉丁文', intro: '方濟會總會長海莫應教廷之託改訂羅馬教廷日課，簡編合冊便於託缽會士隨身攜行。此「攜帶型日課」隨方濟會傳遍歐洲而成羅馬日課主流，breviarium 一詞的近代意義由此確立，日課史的轉捩工程。' },
          { title_zh: '英格蘭修道禮儀協約', title_orig: 'Regularis Concordia', author: '埃塞爾沃爾德主持（溫徹斯特會議）', era: '約 973', place: '溫徹斯特', language: '拉丁文', intro: '英格蘭修道復興運動為統一全國修院禮儀而訂的協約，日課、遊行與君王代禱的儀節俱備，其復活節晨禱的「你們找誰」對答為西方禮儀劇的最早記載。禮儀統一與戲劇起源共冶一爐的奇特文獻。' },
          { title_zh: '舍努特沙漠節遊行禮', title_orig: 'The Feast of the Desert of Apa Shenoute: A Liturgical Procession from the White Monastery', author: '上埃及白修道院傳統', era: '中世紀禮儀傳本', place: '上埃及白修道院', language: '科普特文／阿拉伯文／希臘文', intro: '白修道院為紀念修院領袖舍努特而行的沙漠節遊行禮儀，以三語抄本保存遊行次序、誦讀與歌詠。禮文把舍努特墓地、修院教堂與周邊聖地串成一條敬拜路徑，使修院歷史、建築空間與聖徒記憶在群體步行中重現。現代校本證實它是中世紀科普特公共禮儀的一手文本，補足正文中偏重拜占庭與拉丁禮的部分。' },
          { title_zh: '諾特克繼抒詠集', title_orig: 'Liber hymnorum (Notker Balbulus)', author: '「結巴」諾特克', era: '約 884', place: '聖加侖', language: '拉丁文', intro: '聖加侖修士諾特克為記誦哈利路亞長旋律而配詞，編成史上第一部繼抒詠集，自序記其創作因緣。繼抒詠自此成為中世紀彌撒詩歌最富創造力的文類，本集是禮儀音樂「文本化革命」的起點。' },
          { title_zh: '溫徹斯特附加段譜集', title_orig: 'Winchester Troper', author: '溫徹斯特舊座堂歌者', era: '約 1000', place: '溫徹斯特', language: '拉丁文', intro: '溫徹斯特座堂的附加段與聖歌譜集，內含一百七十餘首二聲部奧爾加農，為現存最大的早期複音音樂集。西方和聲傳統的第一批書面見證竟出禮儀實用譜本，音樂史的黎明文獻。' },
          { title_zh: '聖馬歇爾修道院聖歌譜集', title_orig: 'Codices Sancti Martialis Lemovicensis', author: '利摩日聖馬歇爾修道院', era: '10–12 世紀', place: '利摩日', language: '拉丁文', intro: '利摩日聖馬歇爾修道院累積的附加段、繼抒詠與早期複音譜集群，「阿基坦複音」以流麗的花唱聲部聞名。這批抄本是聖詠創作與複音實驗的南方重鎮檔案，巴黎聖母院樂派的先聲。' },
          { title_zh: '萊昂對經聖歌抄本', title_orig: 'Antifonario de León', author: '萊昂座堂傳統', era: '10 世紀（藍本上溯 7 世紀）', place: '萊昂', language: '拉丁文', intro: '莫札拉布禮聖歌的最完整譜本，紐姆記譜迄今無法完全破譯，成為「唱不出來的聖歌全集」。羅馬禮取代舊禮後西班牙古調失傳，本抄本遂為伊比利千年聖音的無聲方舟，聖歌學最著名的謎題。' },
          { title_zh: '古羅馬聖詠抄本', title_orig: 'Old Roman Chant Manuscripts', author: '羅馬城教會歌者', era: '11–13 世紀抄本', place: '羅馬', language: '拉丁文', intro: '羅馬城本地聖詠傳統的五部譜本，旋律與通行的「額我略」聖詠同源異流、更趨迴旋裝飾。其存在揭示所謂額我略聖詠實為羅馬與法蘭克交融之產，改寫聖歌起源史的關鍵物證。' },
          { title_zh: '貝內文託聖詠抄本', title_orig: 'Beneventan Chant Manuscripts', author: '貝內文託與蒙特卡西諾歌者', era: '10–11 世紀抄本', place: '義大利南部', language: '拉丁文', intro: '倫巴底南部自成一系的古聖詠，教廷推行額我略聖詠後遭明令禁唱，賴貝內文託字體抄本殘存。與莫札拉布聖歌同為被「標準化」淹沒的地方傳統，中世紀禮儀一統化代價的音樂見證。' },
          { title_zh: '哈特克對經集', title_orig: 'Hartker-Antiphonar', author: '聖加侖修士哈特克', era: '約 990–1000', place: '聖加侖', language: '拉丁文', intro: '隱居修士哈特克手繕的日課對經全集，聖加侖紐姆譜精緻入微，為日課聖詠現存最權威的早期譜本。今日校訂額我略對經旋律仍以此為基準，一人斗室之功成千年聖歌之尺。' },
          { title_zh: '艾因西德倫聖詠譜本', title_orig: 'Codex Einsidlensis 121', author: '艾因西德倫修道院', era: '約 960–970', place: '艾因西德倫', language: '拉丁文', intro: '艾因西德倫修道院的彌撒聖詠全年譜本，紐姆附加的表情字母細如呼吸標記，為聖詠古譜學的核心證人。二十世紀索雷姆復原運動倚為柱石，中世紀歌者精微聽覺的直接遺存。' },
          { title_zh: '熙篤聖詠改革文獻', title_orig: 'Cistercian Chant Reform Documents', author: '熙篤會（伯爾納主持）', era: '約 1134–1147', place: '克萊爾沃／熙篤', language: '拉丁文', intro: '熙篤會以「回歸純正」為名兩度改訂聖詠，伯爾納主持的委員會依理論削齊旋律音域，序言申其原則。這批文獻是中世紀罕見的自覺音樂改革檔案，苦修美學施於聖歌的完整個案。' },
          { title_zh: '奧爾加農大全', title_orig: 'Magnus liber organi', author: '雷奧南與佩羅坦（巴黎聖母院樂派）', era: '約 1160–1250', place: '巴黎聖母院', language: '拉丁文', intro: '巴黎聖母院為大節日聖詠配寫的複音曲總集，雷奧南首創、佩羅坦擴為三四聲部，節奏模式由此成文。西方音樂自此有了「作品」與「作曲家」，本集是複音藝術大廈的奠基石。' },
          { title_zh: '拉斯烏埃爾加斯抄本', title_orig: 'Codex Las Huelgas', author: '拉斯烏埃爾加斯王家女修道院', era: '約 1300–1325', place: '布爾戈斯', language: '拉丁文', intro: '卡斯提爾王家女修道院的複音音樂抄本，收經文歌、孔杜克圖斯與繼抒詠近兩百首，專供修女詩班之用。女性團體演唱前衛複音的直接證據，中世紀音樂史中最珍貴的女聲檔案。' },
          { title_zh: '老霍爾抄本', title_orig: 'Old Hall Manuscript', author: '英格蘭王家禮拜堂作曲家群', era: '約 1410–1420', place: '英格蘭', language: '拉丁文', intro: '英格蘭現存最大的中世紀複音禮儀音樂集，收彌撒樂章與經文歌百餘首，作者含王弟克拉倫斯公爵的禮拜堂樂師。其甜美的三度和聲「英格蘭風」旋即風靡歐陸，改變十五世紀音樂的聽覺。' },
          { title_zh: '馬肖聖母彌撒', title_orig: 'Messe de Nostre Dame', author: '紀堯姆‧德‧馬肖', era: '約 1360–1365', place: '蘭斯', language: '拉丁文', intro: '詩人作曲家馬肖為蘭斯座堂聖母祭壇譜寫的四聲部彌撒，為單一作曲家所作首部完整複音彌撒常規曲。他親立基金確保身後每週演唱，作品與紀念合一，中世紀音樂最高的個人紀念碑。' },
          { title_zh: '蒙特塞拉特朱紅書', title_orig: 'Llibre Vermell de Montserrat', author: '蒙特塞拉特修道院', era: '約 1399', place: '加泰隆尼亞蒙特塞拉特', language: '拉丁文／加泰隆尼亞文', intro: '蒙特塞拉特聖母朝聖地為朝聖者編集的歌舞集，序言明言供守夜者「唱誦端莊之歌代替俗謠」，含輪唱與圓舞。朝聖群眾的敬虔娛樂得此書而傳，中世紀大眾宗教音樂的鮮活孤本。' },
          { title_zh: '聖母頌歌集', title_orig: 'Cantigas de Santa Maria', author: '阿方索十世宮廷（國王主持）', era: '約 1270–1284', place: '託萊多／塞維亞', language: '加利西亞-葡萄牙文', intro: '智者阿方索十世主持編纂的聖母奇蹟頌歌四百餘首，附全部樂譜與細密畫，每十首插一讚美詩。它是中世紀單旋律歌曲最大的寶庫，兼為伊比利三教共存社會的圖像檔案，王室聖母敬禮的極致。' },
          { title_zh: '科爾託納勞德讚歌集', title_orig: 'Laudario di Cortona', author: '科爾託納平信徒讚歌會', era: '約 1270–1297', place: '科爾託納', language: '義大利文', intro: '義大利平信徒讚歌會的俗語靈歌集，為現存最古的義大利語宗教歌曲譜集，方濟各《太陽歌》開創的俗語讚美傳統賴此成體。城市兄弟會自組歌詠的見證，宗教音樂平民化的第一手文獻。' },
          { title_zh: '阿伯拉爾帕拉克萊聖詩集', title_orig: 'Hymnarius Paraclitensis', author: '彼得‧阿伯拉爾', era: '約 1130–1140', place: '帕拉克萊女修道院', language: '拉丁文', intro: '阿伯拉爾應埃洛伊絲之請為帕拉克萊女修院譜寫的全年聖詩百餘首，「安息日已何其榮美」至今傳唱。哲學家為摯愛的修院量身打造整套日課詩歌，是中世紀聖詩史上最私密動人的一章。' },
          { title_zh: '又聖母經', title_orig: 'Salve Regina', author: '傳賴興瑙的赫爾曼努斯', era: '11 世紀', place: '賴興瑙／勒皮', language: '拉丁文', intro: '「萬福母后」對經傳為殘疾天才赫爾曼努斯所作，熙篤與道明兩會定為晚課壓軸，日暮群僧列隊向聖母唱別遂成中世紀修院最深入人心的一幕。短短數行流傳千年，聖母敬禮音樂的第一名篇。' },
          { title_zh: '來，聖神', title_orig: 'Veni Sancte Spiritus', author: '傳坎特伯裡的斯蒂芬‧朗頓', era: '約 1200', place: '巴黎／坎特伯裡', language: '拉丁文', intro: '五旬節金色繼抒詠「來，聖神」，傳出朗頓之手，十行對句字字懇切，被譽為中世紀拉丁詩的完璧。特倫託刪汰繼抒詠時倖存的四首之一，至今聖神降臨節仍詠唱不輟。' },
          { title_zh: '來，創造之神', title_orig: 'Veni Creator Spiritus', author: '傳拉巴努斯‧毛魯斯', era: '9 世紀', place: '富爾達／美因茲', language: '拉丁文', intro: '祈求聖神的晚課聖詩，傳為拉巴努斯所作，自中世紀起凡按立、加冕、大公會議開幕必唱，馬勒第八交響曲亦以之開篇。一首加洛林聖詩成為西方一切「開始」的聲音，禮儀詩歌影響力之最。' },
          { title_zh: '讚美逾越犧牲', title_orig: 'Victimae paschali laudes', author: '傳勃艮第的維波', era: '約 1040', place: '帝國宮廷', language: '拉丁文', intro: '復活節繼抒詠，傳為皇帝康拉德二世的宮廷司鐸維波所作，與馬利亞的對話問答成為復活節劇的種子。特倫託倖存四繼抒詠之一，其旋律亦為路德〈基督躺臥死亡枷鎖〉所本，跨越宗派的復活之歌。' },
          { title_zh: '耶穌，甘甜的記憶', title_orig: 'Jesu dulcis memoria', author: '佚名熙篤會詩人（傳聖伯爾納）', era: '12 世紀末', place: '英格蘭（熙篤圈）', language: '拉丁文', intro: '詠耶穌聖名甘甜的長篇靈修詩，中世紀託名伯爾納而尊為「甜蜜博士之歌」，選節入耶穌聖名節日課。其溫柔的內在化虔敬預示近代靈修的轉向，拉丁讚美詩中最常被翻譯傳唱的名作之一。' },
          { title_zh: '亡者日課', title_orig: 'Officium defunctorum', author: '西方教會傳統', era: '9 世紀成形', place: '羅馬／法蘭克王國', language: '拉丁文', intro: '為亡者誦唸的特別日課，晚課、夜課與讚課以約伯記哀音貫穿，自加洛林時代附入日常祈禱。它是中世紀死亡文化的日常配樂，時辰書必收其文，後世奧克岡至維多利亞的安魂音樂皆其枝葉。' },
          { title_zh: '玫瑰經敬禮的成形', title_orig: 'Rosarium (medieval formation)', author: '道明會與加爾都西會推廣', era: '13–15 世紀', place: '萊茵蘭／全西歐', language: '拉丁文', intro: '以一百五十遍聖母經對應詩篇的「聖母詩篇」敬禮，經加爾都西會的多明尼克析為默想奧蹟、道明會的阿蘭立會推廣，十五世紀末定型為玫瑰經。平信徒的「窮人日課」由此誕生，天主教敬禮史的分水嶺。' },
          { title_zh: '苦路敬禮禮文', title_orig: 'Via Crucis (Franciscan tradition)', author: '方濟會聖地監護傳統', era: '14–15 世紀成形', place: '耶路撒冷／西歐', language: '拉丁文', intro: '方濟會受託監護聖地後，把耶路撒冷苦路巡禮移植為歐洲教堂內的十四處默想行禮。無力朝聖者得以在本堂「行走耶路撒冷」，是中世紀晚期受難敬虔最成功的禮儀發明，至今普世遵行。' },
          { title_zh: '貝裡公爵豪華時辰書', title_orig: 'Très Riches Heures du duc de Berry', author: '林堡兄弟（貝裡公爵委製）', era: '約 1412–1416', place: '布爾日', language: '拉丁文', intro: '貝裡公爵委託林堡兄弟繪製的時辰書，十二月令圖把貴族與農民的四季生活繪入祈禱書，為國際哥德式繪畫的最高峰。時辰書為中世紀晚期最流行的私人祈禱書，此本即其王者，「中世紀最美的書」。' },
          { title_zh: '讓娜‧德‧埃夫勒時辰書', title_orig: 'Heures de Jeanne d\'Évreux', author: '讓‧皮塞勒（王后委製）', era: '約 1324–1328', place: '巴黎', language: '拉丁文', intro: '法蘭西王后讓娜的袖珍時辰書，皮塞勒以灰色單彩畫出七百餘幅精微圖像，頁緣戲謔小像與虔敬正圖並存。王后掌中方寸即一座祈禱的大教堂，哥德書藝與女性虔敬文化的絕品。' },
          { title_zh: '克萊沃的凱瑟琳時辰書', title_orig: 'Hours of Catherine of Cleves', author: '克萊沃畫師（公爵夫人委製）', era: '約 1440', place: '烏得勒支', language: '拉丁文', intro: '克萊沃公爵夫人凱瑟琳的時辰書，頁緣以魚籠、椒鹽卷餅與錢幣等日常物象環繞聖像，寫實奇想為尼德蘭繪畫先聲。委製者身陷婚姻與政爭，其祈禱書的私密圖像自成一部女性生命史。' },
          { title_zh: '瑪麗‧德‧勃艮第時辰書', title_orig: 'Stundenbuch der Maria von Burgund', author: '維也納畫師（勃艮第女公爵用書）', era: '約 1477', place: '根特／布魯日', language: '拉丁文', intro: '歐洲最富有的女繼承人瑪麗的時辰書，名頁繪其臨窗讀此書、窗外即聖母顯現的教堂——祈禱者、書與異象疊為一景。「畫中畫」的視覺神學總結了時辰書文化的本質：私禱即親臨。' },
          { title_zh: '貝德福德時辰書', title_orig: 'Bedford Hours', author: '貝德福德畫坊（公爵婚禮委製）', era: '約 1423–1430', place: '巴黎', language: '拉丁文', intro: '英格蘭攝政貝德福德公爵與勃艮第安妮婚禮委製的豪華時辰書，千餘幅邊飾圓畫連環鋪陳聖經史。成於英法百年戰爭佔領下的巴黎，兼為政治聯姻的禮物，祈禱書而載王朝雄圖的代表作。' },
          { title_zh: '羅昂大時辰書', title_orig: 'Grandes Heures de Rohan', author: '羅昂大師', era: '約 1430–1435', place: '巴黎／安茹', language: '拉丁文', intro: '佚名「羅昂大師」繪製的時辰書，亡者日課一頁繪垂死者仰對持劍上帝、靈魂被天使魔鬼爭奪，慘烈直逼表現主義。百年戰爭世代的死亡焦慮盡入祈禱書，中世紀圖像最震撼的臨終場景。' },
          { title_zh: '聖奧爾本斯詩篇', title_orig: 'St Albans Psalter', author: '聖奧爾本斯修道院（為隱修女克莉絲蒂娜）', era: '約 1120–1145', place: '聖奧爾本斯', language: '拉丁文', intro: '聖奧爾本斯修道院為隱修女瑪基雅特的克莉絲蒂娜備製的詩篇集，四十餘幅整頁畫開英格蘭羅曼式書繪之先，並收最早的法語聖亞歷克西斯歌。一位女隱士的祈禱書成為藝術史坐標，女性靈修與書藝的交點。' },
          { title_zh: '呂特雷爾詩篇', title_orig: 'Luttrell Psalter', author: '林肯郡畫坊（呂特雷爾爵士委製）', era: '約 1325–1340', place: '林肯郡', language: '拉丁文', intro: '鄉紳呂特雷爾委製的詩篇集，頁緣繪耕田、車載、烤爐與奇形怪獸，為中世紀英格蘭農村生活最完整的圖像檔案。祈禱文本與日常百態同頁共存，是禮儀書籍兼作社會史料的極致個案。' },
          { title_zh: '達勒姆禮書', title_orig: 'Durham Collectar (Ritual)', author: '達勒姆教會（阿爾德雷德加註）', era: '10 世紀（註約 970）', place: '切斯特勒街／達勒姆', language: '拉丁文（古英語行間註）', intro: '諾森布里亞的禱文與祝福禮書，司鐸阿爾德雷德以古英語行間直譯全文，與其林迪斯法恩福音書註同手。禮儀拉丁文首度全面「翻譯」為英語的實物，古英語與禮儀史的雙重珍寶。' },
          { title_zh: '聖加侖唱經本', title_orig: 'Cantatorium Sancti Galli (Codex 359)', author: '聖加侖修道院', era: '約 922–925', place: '聖加侖', language: '拉丁文', intro: '聖加侖修道院供獨唱者使用的彌撒聖詠唱經本，紐姆記譜精確為現存聖詠譜本之最，象牙封板完好如初。與艾因西德倫本、哈特克本鼎足而三，是額我略聖詠文本批判的第一級證人。' }
        
        ]
      }
    ]
  },
  wai: {
    summary: '基督宗教以外、與中世紀基督教世界比鄰並互動的一神信仰禮儀：伊斯蘭的禮拜與蘇菲祈念，以及猶太教的標準祈禱書與逾越節家宴儀軌。',
    divisions: [
      {
        key: 'islamic-liturgy',
        label: '伊斯蘭禮儀部',
        label_en: 'Islamic Liturgy',
        desc: '伊斯蘭每日五番禮拜的儀程，以及蘇菲道團的齊克爾祈念儀軌。',
        works: [
          { title_zh: '禮拜儀程', title_orig: 'Ṣalāt / الصلاة', author: '伊斯蘭傳統（聖訓與教法學派傳承）', era: '中世紀定型（8–13 世紀）', place: '麥地那—巴格達—開羅', language: '阿拉伯文', intro: '伊斯蘭五功之一的每日五番禮拜，其完整儀程經中世紀四大遜尼教法學派與聖訓彙編逐步定型：包含淨禮（wuḍū）、面向麥加的舉意、起拜大讚（takbīr）、誦念開端章與古蘭經文、鞠躬（rukūʿ）、叩首（sujūd）與作證辭，按晨、晌、晡、昏、宵五時定數施行。儀程中阿拉伯經文的誦念與身體動作緊密結合，是伊斯蘭公共與個人敬拜的根本框架。' },
          { title_zh: '蘇菲齊克爾祈念儀軌', title_orig: 'Dhikr / الذِّكْر', author: '蘇菲各道團（卡迪里耶、里法耶等）', era: '12–15 世紀', place: '巴格達—呼羅珊—安那托利亞', language: '阿拉伯文', intro: '齊克爾意為「記念真主」，是蘇菲修行的核心儀軌：信眾於導師帶領下反覆吟誦真主尊名與信仰作證辭，或單獨默念，或眾人圍坐齊聲高誦，常配合呼吸節奏與身體律動，部分道團更發展出迴旋、搖擺等形式以臻於忘我與心靈澄明之境。中世紀各道團（ṭarīqa）皆有專屬的祈念串珠、誦詞次序與連禱（wird），構成蘇菲團體日常與聚會敬拜的禮儀骨幹。' }
        ]
      },
      {
        key: 'jewish-liturgy',
        label: '猶太禮儀部',
        label_en: 'Jewish Liturgy',
        desc: '中世紀猶太教的標準祈禱書傳本，以及逾越節家宴的哈加達禮儀。',
        works: [
          { title_zh: '阿姆蘭‧加翁祈禱書', title_orig: 'Seder Rav Amram Gaon', author: '阿姆蘭‧加翁', era: '9 世紀（中世紀傳本）', place: '巴比倫蘇拉學院', language: '希伯來文‧亞蘭文', intro: '巴比倫蘇拉學院院長（Gaon）阿姆蘭應西班牙猶太社團之請，編成史上首部完整有序的祈禱書（Siddur），按年週循環羅列日常、安息日與節期的祈禱辭，並附簡明的禮儀規矩與律法說明。此書經中世紀各地社團抄傳增補，成為猶太祈禱定型的基石，後世薩阿迪亞祈禱書與西班牙、阿什肯納茲諸禮本皆以之為母本。' },
          { title_zh: '逾越節哈加達', title_orig: 'Haggadah shel Pesaḥ', author: '猶太傳統（中世紀編訂）', era: '中世紀本（13–15 世紀繁盛）', place: '西班牙—德意志（萊茵蘭）', language: '希伯來文‧亞蘭文', intro: '逾越節家宴（Seder）誦讀的禮儀文本，按四杯酒的次序敘述以色列出埃及的救恩故事，含「四問」、十災、讚美詩篇（Hallel）與餐後祝謝。中世紀哈加達從祈禱書中獨立成冊，並發展出華美的插圖抄本傳統（如「金色哈加達」、「薩拉耶佛哈加達」），既是家庭教育下一代的敘事腳本，也是猶太禮儀藝術的瑰寶，傳本繁多而流傳至今。' }
        ]
      }
    ]
  }
},
    {
  key: 'shiwen',
  name: '詩藝藏',
  name_en: 'Poetry and Arts Treasury',
  glyph: '詩',
  genres: '聖詠‧史詩‧戲劇‧藝術',
  summary: '中世紀宗教詩歌、神學史詩、神蹟戲劇與宗教藝術典籍的總集。涵蓋拉丁聖頌與續抒詠、但丁與聖方濟的神學詩篇、神蹟劇與道德劇的舞台文本、建築與圖像象徵手冊，並收伊斯蘭蘇菲詩與猶太希伯來宗教詩，呈現中世紀信仰如何以詩、樂、劇與造型藝術的形式表達超越的嚮往。',
  zheng: {
    summary: '基督宗教的詩文與藝術：拉丁與拜占庭的聖頌、但丁與聖方濟的神學詩篇，以及神蹟劇、道德劇與建築圖像的象徵傳統。',
    divisions: [
      {
        key: 'psalmody-hymnody',
        label: '聖詠與聖頌部',
        label_en: 'Psalmody and Hymnody',
        desc: '拉丁聖體頌與彌撒續抒詠、拜占庭聖頌續編，以及希爾德加德的靈視聖樂。',
        works: [
          { title_zh: '舌兮歌詠', title_orig: 'Pange Lingua Gloriosi', author: '多瑪斯‧阿奎那', era: '約 1264 年', place: '奧爾維耶托', language: '拉丁文', intro: '阿奎那應教宗烏爾班四世之命為新設的基督聖體聖血節（Corpus Christi）所作的聖體讚美詩，以六節格律頌讚聖體聖事的奧蹟，末二節「Tantum Ergo」尤為著名，至今仍於聖體降福禮中詠唱。全詩將深奧的變體神學凝鍊為優美的拉丁詩律，兼具教義精準與抒情之美，被譽為中世紀拉丁聖詩的巔峰之一。', link: '/fathers' },
          { title_zh: '熙雍讚主', title_orig: 'Lauda Sion Salvatorem', author: '多瑪斯‧阿奎那', era: '約 1264 年', place: '奧爾維耶托', language: '拉丁文', intro: '阿奎那為基督聖體節彌撒所作的續抒詠（Sequentia），呼籲熙雍（耶路撒冷）讚頌賜下生命之糧的救主。全詩以教理問答般的層次闡明聖體神學：基督整全地臨在於每一份餅酒之中，掰開不分其體。詩律工整、神學嚴密而頌讚熱切，是中世紀少數保留於羅馬彌撒中的續抒詠之一，與舌兮歌詠並為聖體節禮儀的雙璧。', link: '/fathers' },
          { title_zh: '聖母悼歌', title_orig: 'Stabat Mater Dolorosa', author: '託名雅各伯內‧達托迪', era: '13 世紀', place: '義大利', language: '拉丁文', intro: '描繪聖母瑪利亞站立十字架下、目睹聖子受難而肝腸寸斷的哀傷聖詩，傳為方濟各會士雅各伯內‧達托迪所作。全詩以強烈的情感邀請信眾與聖母同悲、共擔基督的苦難，體現方濟各靈修對基督人性與受苦的深切默想。中世紀廣傳於苦路與聖母痛苦瞻禮，後世無數作曲家為之譜曲，成為西方宗教音樂史上最常被詠唱的文本之一。' },
          { title_zh: '震怒之日', title_orig: 'Dies Irae', author: '託名切拉諾的多默', era: '13 世紀', place: '義大利', language: '拉丁文', intro: '中世紀最著名的末日審判續抒詠，以震慄的筆觸描繪世界末日大火、號角召喚萬民、生死簿展開、義人蒙救而惡人遭棄的景象，繼而轉為罪人向慈悲審判者的懇切哀求。傳為方濟各會士切拉諾的多默所作，長期用於追思安魂彌撒（Requiem）。其陰鬱莊嚴的格律與旋律深植西方文化，成為「末日」意象的音樂代名詞。' },
          { title_zh: '拜占庭聖頌續編', title_orig: 'Kontakia kai Kanones', author: '大馬士革的約翰、邁烏馬的科斯馬斯等', era: '8–11 世紀', place: '耶路撒冷—君士坦丁堡', language: '希臘文', intro: '繼六世紀羅曼努斯的長篇講道體聖頌（kontakion）之後，中世紀拜占庭聖樂發展出以九段歌頌（ode）構成的「聖頌典」（kanon）形式，大馬士革的約翰與其義兄邁烏馬的科斯馬斯為集大成者。其作品依附於晨課九首聖經頌歌，按八種調式（Octoechos）譜成，神學深邃而韻律繁複，構成東正教節期與主日晨課聖樂的主體，至今傳唱。' },
          { title_zh: '希爾德加德靈視聖頌', title_orig: 'Symphonia armonie celestium revelationum', author: '賓根的希爾德加德', era: '12 世紀', place: '德意志賓根', language: '拉丁文', intro: '本篤會女隱修院長希爾德加德所譜的靈視聖樂集，含對經、應答詠、聖頌與一齣音樂道德劇，獻給聖母、聖靈、諸聖與童貞女。其旋律音域寬廣、樂句綿長飛揚，突破當時聖詠的常規，歌詞則充滿她特有的鮮活意象（青翠生機 viriditas、寶石、光）。作為中世紀少數有名可考的女性作曲家，其作品融合神祕靈視、神學與音樂創造，獨樹一幟。' },
          { title_zh: '哀歌之書', title_orig: 'Matʻean Ołbergutʻean (Մատեան ողբերգութեան, Book of Lamentations)', author: '納雷克的聖額我略（Grigor Narekatsʻi）', era: '約 1002–1003 年', place: '亞美尼亞凡湖納雷克修道院', language: '古典亞美尼亞文（grabar）', extent: '全 95 篇', note: '亞美尼亞人暱稱「納雷克」，奉為僅次於聖經的靈修經典', intro: '亞美尼亞使徒教會隱修士、神祕主義詩人納雷克的額我略晚年所撰的長篇祈禱詩集，由九十五篇「與神由心底傾訴」的哀禱組成。全書以罪人向上帝痛切自陳、懇求憐憫為主軸，意象繁複、語言瑰麗而情感熾烈，世代被亞美尼亞人抄誦、暱稱「納雷克」，信其有醫治之效，尊為僅次於聖經的靈修經典。二〇一五年作者獲天主教會冊封為教會聖師，本書亦為東方基督教密契傳統的巔峰之作。' },
              { title_zh: '以信告白', title_orig: 'Hawatov Khostovanim (I Confess with Faith)', author: '雅愛者聖納雷斯（Nersēs Šnorhali）', era: '12 世紀', place: '亞美尼亞奇里乞亞', language: '古典亞美尼亞文', extent: '二十四節', intro: '亞美尼亞使徒教會大公牧首、被尊為「雅愛者（Šnorhali，蒙恩者）」的納雷斯所作二十四節祈禱詩，對應晝夜二十四時，逐節向三位一體痛悔祈禱、求賜信德與救恩。文辭優美虔敬，世代為亞美尼亞信徒誦念，並譯成多國語言，是亞美尼亞教會最受愛戴的祈禱文之一，也是中世紀亞美尼亞靈修詩的代表作。' },
          { title_zh: '阿伯拉爾哀歌六首', title_orig: 'Planctus (Abaelardus)', author: '彼得‧阿伯拉爾', era: '約 1130–1140', place: '巴黎／帕拉克萊', language: '拉丁文', intro: '阿伯拉爾以舊約悲劇人物——耶弗他之女、掃羅與約拿單——寫成六首哀歌，古調存譜，哀音中自照其身世之慟。中世紀拉丁抒情詩的異數，邏輯大師以哀歌自懺的絕美文本。' },
          { title_zh: '卡西婭聖頌', title_orig: 'Hymns of Kassia', author: '卡西婭', era: '約 840–865', place: '君士坦丁堡', language: '希臘文', intro: '拜占庭女修道院長卡西婭為教會年譜寫聖頌數十首，聖週三的「墮落婦人頌」至今誦唱，傳說她因應對過於聰慧而落選皇后。教會音樂史上最早有署名作品傳世的女作曲家，拜占庭女性創作的孤峰。' },
          { title_zh: '約瑟夫聖詩家聖頌集', title_orig: 'Canons of Joseph the Hymnographer', author: '聖詩家約瑟夫', era: '約 840–886', place: '君士坦丁堡', language: '希臘文', intro: '西西里出身的約瑟夫為聖人曆譜寫聖頌經典數百部，正教日課《每月禮典》的主體出其手筆。他因護聖像被擄為奴而不輟歌詠，量產與虔誠兼具，拜占庭聖詩工業的化身。' },
          { title_zh: '神聖愛情讚歌', title_orig: 'Hymns of Divine Eros', author: '新神學家西默盎', era: '約 1000–1022', place: '君士坦丁堡', language: '希臘文', intro: '拜占庭密契者西默盎自述神光經驗的讚歌集，敢言「我的手是基督、我的腳是基督」，狂喜的第一人稱在拜占庭傳統中石破天驚。正教密契詩的最高峰，千年後仍炙熱如初。' },
          { title_zh: '雅各波內勞德詩集', title_orig: 'Laude di Jacopone da Todi', author: '雅各波內‧達‧託迪', era: '約 1278–1306', place: '託迪／獄中', language: '義大利文（翁布里亞方言）', intro: '喪妻棄業的律師雅各波內入方濟會屬靈派，以粗礪的俗語勞德詩詠神聖之愛的瘋狂，因諷卜尼法八世繫獄仍歌唱不絕。義大利宗教抒情詩的火山，聖母悼歌亦傳其手筆。' },
          { title_zh: '聖維克託的亞當繼抒詠集', title_orig: 'Sequentiae Adami a Sancto Victore', author: '聖維克託的亞當', era: '約 1130–1146', place: '巴黎聖維克託修道院', language: '拉丁文', intro: '聖維克託修道院詩人亞當把繼抒詠推向格律與神學的雙重完美，韻節如鐘錶而意象如彩窗。中世紀拉丁詩藝的最高工匠，其詠聖母與聖靈諸篇為巴黎禮儀增色近百年。' },
          { title_zh: '論輕世', title_orig: 'De contemptu mundi (Bernardus Cluniacensis)', author: '克呂尼的伯爾納', era: '約 1140', place: '克呂尼', language: '拉丁文', intro: '克呂尼修士伯爾納以三千行罕見的三重韻律痛斥時世腐敗、遙詠天上耶路撒冷。十九世紀尼爾自其中譯出「金色耶路撒冷」聖詩而家喻戶曉，諷世詩與天鄉頌合一的奇作。' },
          { title_zh: '甜蜜的歡欣', title_orig: 'In dulci jubilo', author: '傳亨利希‧蘇索（記其天使之歌）', era: '約 1328', place: '萊茵蘭', language: '拉丁文／德文混合', intro: '傳說密契者蘇索聞天使歌舞而記下的聖誕歌，拉丁文與德語逐句交織的「混合詩體」為其獨創。自中世紀狂喜傳統流入普世聖誕曲目，巴哈亦為之作管風琴聖詠曲。' },
          { title_zh: '中古英語頌歌集', title_orig: 'Middle English Carols', author: '英格蘭方濟會圈與民間歌者', era: '15 世紀', place: '英格蘭', language: '中古英語', intro: '十五世紀英格蘭傳抄的頌歌數百首，聖誕、聖母與道德題材配以疊句舞歌形式，「科芬特里頌歌」等至今傳唱。教會節期與民間歌舞交融的產物，英語聖誕音樂傳統的中世紀根系。' },
          { title_zh: '派翠克胸甲禱歌', title_orig: 'Faeth Fiada (St Patrick\'s Breastplate)', author: '託名聖派翠克（中世紀傳本）', era: '11 世紀抄本（傳統上溯更早）', place: '愛爾蘭', language: '古愛爾蘭文', intro: '託名派翠克的「鹿鳴」護身禱歌，「基督在我前、基督在我後」的迴環結構承凱爾特咒禱傳統而全然歸主。愛爾蘭靈修的招牌文本，十九世紀譯為聖詩後風行普世教會。' },
          { title_zh: '弗裡克詩集', title_orig: 'Poems of Frik', author: '弗裡克', era: '約 1230–1310', place: '大亞美尼亞', language: '亞美尼亞文', intro: '蒙古統治下的亞美尼亞平信徒詩人弗裡克，以直白的俗語向上帝申冤：義人受苦、稅吏橫行，天理何在。中世紀罕見的「抗辯詩」聲音，亞美尼亞文學自教會語轉向民間語的標誌。' }
        
        ]
      },
      {
        key: 'theological-epic',
        label: '神學史詩部',
        label_en: 'Theological Epic',
        desc: '但丁縱貫地獄、煉獄與天堂的神曲，以及聖方濟讚頌受造萬物的太陽歌。',
        works: [
          { title_zh: '神曲', title_orig: 'La Divina Commedia', author: '但丁‧阿利吉耶里', era: '約 1308–1320 年', place: '義大利（流亡中）', language: '托斯卡納俗語（義大利文）', intro: '但丁以第一人稱敘述自己在維吉爾與貝雅特麗采引領下，依次遊歷地獄、煉獄與天堂三界的長篇史詩，共一百歌、以三韻句（terza rima）寫成。全詩既是個人靈魂從迷失走向天主之愛的朝聖，也是一部囊括經院神學、政治、倫理與宇宙論的百科全書。它確立了義大利俗語的文學地位，被尊為中世紀基督教文明的詩學總結與西方文學的不朽豐碑。' },
          { title_zh: '太陽歌（造物讚）', title_orig: 'Cantico di Frate Sole / Laudes Creaturarum', author: '亞西西的方濟各', era: '約 1224–1225 年', place: '義大利亞西西', language: '翁布里亞俗語（義大利文）', intro: '聖方濟在病痛與近乎失明的晚年所作的讚美詩，被視為義大利文學最早的文獻之一。詩中以「太陽兄弟」、「月亮姊妹」、「風兄弟」、「水姊妹」、「火兄弟」與「我們的母親大地」相稱，邀請一切受造之物同頌造物主，末段更接納「死亡姊妹」。全詩洋溢方濟各對受造界的手足之情與單純喜樂，是中世紀生態靈修與受造讚頌的典範之作。' },
              { title_zh: '耶穌之子', title_orig: 'Yisus Ordi (Jesus the Son)', author: '雅愛者聖納雷斯（Nersēs Šnorhali）', era: '約 1152 年', place: '亞美尼亞奇里乞亞', language: '古典亞美尼亞文', extent: '逾八千行', intro: '納雷斯以單一韻腳貫穿全篇的長篇敘事神學詩，自創世與救恩計畫敘至基督的生平、受難、復活與末世審判，並以勸勉與祈禱作結。全詩既是聖經救恩史的詩體總覽，也是默想基督的靈修長卷，展現亞美尼亞詩體神學的恢宏氣度，與但丁《神曲》同為中世紀各民族以母語譜寫的基督教史詩巨構。' },
              { title_zh: '救主篇', title_orig: 'Heliand (The Saviour)', author: '佚名古薩克森詩人', era: '約 830 年', place: '東法蘭克／薩克森', language: '古薩克森文（古低地德文）', extent: '近 6000 行頭韻詩', intro: '加洛林時期受命為新歸信的薩克森人寫成的古薩克森文頭韻體福音敘事詩，將四福音合參為一，把基督描繪成日耳曼式的「民眾君主」、門徒為其忠誠扈從，背景亦轉化為北方的山川村落。它以日耳曼英雄詩傳統承載福音，是中世紀早期福音「在地化」宣教的傑作，與《神曲》《耶穌之子》並列各民族母語基督教史詩之林。' },
          { title_zh: '以德薩輓歌', title_orig: 'Oghb Edesioy (Lament for Edessa)', author: '雅愛者聖納雷斯（Nersēs Šnorhali）', era: '約 1145–1146 年', place: '亞美尼亞奇里乞亞', language: '古典亞美尼亞文', intro: '亞美尼亞大公牧首納雷斯為一一四四年埃德薩城陷於贊吉王朝、基督徒慘遭屠戮一事所作的長篇哀歌。全詩以擬人化的埃德薩城自述其昔日榮光與今日傾覆，哀悼東方基督教重鎮的淪亡，亦反思罪與審判。它是亞美尼亞詩體文學的名篇，也是十字軍時代近東基督徒創傷記憶的動人見證，與其《耶穌之子》《以信告白》並為納雷斯詩藝的代表。' },
          { title_zh: '以信告白（二十四禱文）', title_orig: 'Havatov Khosṭovanim / Preces Sancti Nersetis Clajensis', author: '雅愛者聖納雷斯（Nersēs Šnorhali）', era: '12 世紀', place: '亞美尼亞奇里乞亞', language: '古典亞美尼亞文', extent: '二十四節', intro: '亞美尼亞大公牧首納雷斯所作二十四節個人禱文，每節對應一日的一個時辰，以「我以信仰告白」起首，依次祈求三一上帝的憐憫、悔改、守護與聖潔生活。短句兼具信經、懺悔與靈修指引，長期為亞美尼亞信徒日常誦念，並譯成多種語言，是亞美尼亞教會跨越禮儀與私人祈禱的代表文本。' },
          { title_zh: '新生', title_orig: 'Vita Nuova', author: '但丁‧阿利吉耶裡', era: '約 1294', place: '佛羅倫斯', language: '義大利文', intro: '但丁以詩文交織自述對貝雅特麗齊的愛，自初遇、喪亡至誓言「要為她寫前人未寫之語」。塵世之愛升華為神學之愛的自傳性宣言，《神曲》的青春序章，俗語抒情的奠基之書。' },
          { title_zh: '珍珠', title_orig: 'Pearl', author: '珍珠詩人（高文詩人）', era: '約 1380', place: '英格蘭西北中部', language: '中古英語', intro: '喪女的父親夢中與化為天國新婦的「珍珠」隔河對話，環環相扣的詩節如珠鏈首尾相銜。喪慟、恩典與天啟異象熔於精工格律，中古英語詩藝最完美的single作品。' },
          { title_zh: '高文爵士與綠騎士', title_orig: 'Sir Gawain and the Green Knight', author: '珍珠詩人（高文詩人）', era: '約 1375–1400', place: '英格蘭西北中部', language: '中古英語', intro: '綠騎士的斬首之約試煉高文的忠信與貞潔，五角星盾徽鐫刻騎士的五重德性。亞瑟傳奇被鍛成一場關於誠實與悔罪的道德探測，中世紀騎士文學與基督教倫理合金的極品。' },
          { title_zh: '農夫皮爾斯', title_orig: 'Piers Plowman', author: '威廉‧朗格蘭', era: '約 1370–1390', place: '倫敦／莫爾文丘陵', language: '中古英語', intro: '朗格蘭以連串夢境求索「行善、行更善、行至善」，農夫皮爾斯漸與基督身影疊合，教會積弊盡入諷刺。中世紀英格蘭的良心之詩，一三八一年起義者亦引其句，社會異象文學的高峰。' },
          { title_zh: '坎特伯雷故事集', title_orig: 'The Canterbury Tales', author: '傑弗裡‧喬叟', era: '約 1387–1400', place: '倫敦', language: '中古英語', intro: '三十位朝聖者赴坎特伯雷途中輪流講述的故事集，自騎士傳奇至磨坊主葷笑話，赦罪僧與召喚師的醜態並陳，終以堂區神父講道與作者懺悔收卷。朝聖框架盛載全幅人間，英語文學的奠基巨構。' },
          { title_zh: '貝奧武夫', title_orig: 'Beowulf', author: '佚名（基督徒詩人）', era: '約 8–11 世紀（抄本約 1000）', place: '盎格魯-撒克遜英格蘭', language: '古英語', intro: '日耳曼英雄屠魔搏龍的古英語史詩，經基督徒詩人之手，怪物成為該隱後裔、命運歸於上主掌理。異教英雄倫理與新信仰的深層對話，英語文學的創世紀文本。' },
          { title_zh: '十字架之夢', title_orig: 'The Dream of the Rood', author: '佚名（諾森布里亞詩人）', era: '8–10 世紀（韋爾切利抄本）', place: '諾森布里亞', language: '古英語', intro: '十字架親口向夢者述說釘刑：「我不敢彎折，唯與勇士同戰慄」。基督被寫成主動登架的年輕英雄，日耳曼武士倫理與受難神學的天才融合，古英語宗教詩的絕頂之作。' },
          { title_zh: '基涅武甫宗教詩組', title_orig: 'Poems of Cynewulf', author: '基涅武甫', era: '9 世紀', place: '諾森布里亞／麥西亞', language: '古英語', intro: '以盧恩字母藏名的詩人基涅武甫存詩四篇——《海倫娜》尋獲真十架、《基督二》詠昇天等，懇求讀者為其靈魂代禱。古英語詩少數留名的作者，殉道敘事與末日默想的行家。' },
          { title_zh: '奧特弗裡德福音詩書', title_orig: 'Evangelienbuch (Otfrid von Weißenburg)', author: '魏森堡的奧特弗裡德', era: '約 863–871', place: '魏森堡修道院', language: '古高地德語', intro: '修士奧特弗裡德以尾韻詩體重述福音生平，自序申明日耳曼語何以堪載聖史，為德語詩開創韻腳傳統。首位留名的德語詩人，福音史詩本地化的加洛林代表作。' },
          { title_zh: '穆斯皮利', title_orig: 'Muspilli', author: '佚名（巴伐利亞教士）', era: '約 870', place: '巴伐利亞', language: '古高地德語', intro: '殘存百餘行的古高地德語末日詩：以利亞與敵基督決鬥、血滴燃世、靈魂受審。日耳曼頭韻古調吟詠基督教末世論，異教想像與新信仰交疊的珍稀化石。' },
          { title_zh: '小園詩', title_orig: 'Hortulus (De cultura hortorum)', author: '瓦拉弗裡德‧斯特拉波', era: '約 840', place: '賴興瑙島', language: '拉丁文', intro: '賴興瑙院長瓦拉弗裡德詠修道院藥草園的四百行詩，鼠尾草、玫瑰與百合的栽培與靈意娓娓道來，末以園藝獻師長。修道勞動靈修的田園詩化，中世紀植物文學的可愛珍品。' },
          { title_zh: '巴勒斯坦之歌', title_orig: 'Palästinalied', author: '瓦爾特‧馮‧德‧福格爾魏德', era: '約 1228', place: '神聖羅馬帝國', language: '中古高地德語', intro: '德語最偉大抒情詩人瓦爾特為十字軍所作的朝聖歌，「此地我罪身初得榮光」，旋律完整傳世為其唯一。宮廷戀歌大師轉詠聖地的名作，中世紀德語宗教抒情與音樂合璧的代表。' },
          { title_zh: '帕西法爾', title_orig: 'Parzival', author: '沃爾夫拉姆‧馮‧埃申巴赫', era: '約 1200–1210', place: '德意志', language: '中古高地德語', intro: '愚騃少年帕西法爾歷罪、絕望而至同情之問，終成聖杯之王，穆斯林異母兄弟亦得榮席。恩典與騎士道的成長史詩，德語中世紀文學的最高峰，華格納歌劇的遠源。' },
          { title_zh: '可憐的海因裡希', title_orig: 'Der arme Heinrich', author: '哈特曼‧馮‧奧埃', era: '約 1195', place: '士瓦本', language: '中古高地德語', intro: '痲瘋騎士唯處女心血可癒，農家少女甘願捨命，騎士臨刀鋒而悔拒，二人皆得醫治成婚。捨己之愛與天恩逆轉的中篇詩傳奇，德語文學最溫柔的救贖敘事。' },
          { title_zh: '聖杯探求', title_orig: 'La Queste del Saint Graal', author: '佚名（熙篤會背景作者）', era: '約 1220–1230', place: '法蘭西', language: '古法文', intro: '亞瑟騎士傾巢而出尋覓聖杯，唯童貞的加拉哈德得見奧蹟，蘭斯洛特因私情半途折戟。熙篤靈修把騎士傳奇改寫為聖餐默觀的寓言，世俗文類被徹底神學化的經典案例。' },
          { title_zh: '維永遺言詩集', title_orig: 'Le Testament (Villon)', author: '弗朗索瓦‧維永', era: '1461', place: '巴黎', language: '中古法文', intro: '竊盜詩人維永於絞架陰影下以戲謔遺囑體回望殘生，為老母所作的聖母謠曲質樸如燭光，「昔日之雪今安在」的詠嘆千古迴響。罪人的懺悔與嘲世交織，中世紀末法語詩的絕唱。' },
          { title_zh: '悼父輓歌', title_orig: 'Coplas por la muerte de su padre', author: '豪爾赫‧曼裡克', era: '約 1476', place: '卡斯提爾', language: '卡斯提爾文', intro: '騎士詩人曼裡克悼亡父的四十節輓歌，「我們的生命是河，流入死亡之海」，以三重生命觀安頓死亡。西班牙語最被傳誦的哀歌，中世紀死亡默想詩的完美收束。' },
          { title_zh: '聖亞歷克西斯之歌', title_orig: 'La Vie de saint Alexis', author: '佚名（諾曼教士）', era: '約 1050', place: '諾曼第', language: '古法文', intro: '羅馬貴公子亞歷克西斯新婚之夜棄家苦修，歸來隱於父家樓梯下十七年，死後方被認出。古法語文學現存最早的傑作，棄世聖徒理想的詩化原型，存於聖奧爾本斯詩篇抄本。' },
          { title_zh: '羅蘭之歌', title_orig: 'La Chanson de Roland', author: '佚名（傳圖羅爾德）', era: '約 1100', place: '諾曼第／法蘭西', language: '古法文', intro: '羅蘭殿後戰死龍塞斯瓦耶斯，吹角泣血、獻手套於上帝，天使迎其靈魂。武功歌之首以殉道語法書寫封臣之忠，十字軍時代「基督教騎士」意識形態的詩體憲章。' },
          { title_zh: '聖母奇蹟詩', title_orig: 'Milagros de Nuestra Señora', author: '貢薩洛‧德‧貝爾塞奧', era: '約 1246–1252', place: '聖米揚修道院', language: '卡斯提爾文', intro: '西班牙首位留名詩人貝爾塞奧以「僧侶技藝」詩體敷演聖母奇蹟廿五則，自稱只值一杯好酒的酬勞。草地與泉水的序詩為卡斯提爾文學的第一景，伊比利聖母文化的詩泉。' },
          { title_zh: '虎皮武士', title_orig: 'ვეფხისტყაოსანი (Vepkhistqaosani)', author: '紹塔‧魯斯塔維利', era: '約 1189–1207', place: '喬治亞（塔瑪爾女王朝）', language: '喬治亞文', intro: '喬治亞黃金時代的民族史詩，異邦武士結義尋覓被囚的愛人，友誼與天意貫穿波斯風的傳奇。基督教新柏拉圖主義的騎士詩學，喬治亞人奉為第二聖經的文學聖典。' },
          { title_zh: '伊戈爾遠徵記', title_orig: 'Слово о полку Игореве', author: '佚名（基輔羅斯宮廷詩人）', era: '約 1185–1187', place: '基輔羅斯', language: '古東斯拉夫文', intro: '詠伊戈爾王公伐波洛夫齊兵敗被俘的散文詩，雅羅斯拉夫娜城頭喚風喚河的哀歌絕美，異教自然神格與基督教救援交響。古羅斯文學的孤篇傑作，斯拉夫民族詩學的源頭活水。' },
          { title_zh: '太陽之歌（冰島）', title_orig: 'Sólarljóð', author: '佚名（冰島教士詩人）', era: '約 1200', place: '冰島', language: '古諾斯文', intro: '亡父之靈以埃達詩體向兒子述說死亡經歷與天堂地獄之見，「太陽」疊句迴環如鐘。異教《高人箴言》的形式盛載基督教末世異象，北歐信仰轉換期最深邃的詩篇。' },
          { title_zh: '百合詩', title_orig: 'Lilja', author: '埃斯泰因‧奧斯格里姆松', era: '約 1350', place: '冰島', language: '古諾斯文', intro: '冰島修士埃斯泰因以百節詩詠救恩史全幅，格律清麗使古奧的吟唱詩體黯然，諺雲「人人願曾作百合」。北歐中世紀宗教詩的皇冠，冰島文學由薩迦轉向聖詩的標誌。' },
          { title_zh: '情人的告解', title_orig: 'Confessio Amantis', author: '約翰‧高爾', era: '約 1390', place: '倫敦', language: '中古英語', intro: '戀人向維納斯的神父逐一告解七宗罪，每罪以故事訓誨，三萬三千行的框架敘事與喬叟並世爭輝。以告解聖事結構整編古今故事的道德詩庫，中世紀英語的說故事大全。' }
        
        ]
      },
      {
        key: 'sacred-art',
        label: '宗教藝術部',
        label_en: 'Sacred Art and Architecture',
        desc: '中世紀教堂建築、鑲嵌壁畫、聖像、雕刻與織品——自亞琛禮拜堂與夏特爾至盧布廖夫三一聖像與根特祭壇畫。',
        works: [
          { title_zh: '亞琛王家禮拜堂', title_orig: 'Aachener Pfalzkapelle', author: '梅斯的奧多（建築師）', era: '約 792–805', place: '亞琛', language: '建築（法蘭克王國）', intro: '卡爾大帝仿拉溫納聖維塔萊建造的八角宮廷禮拜堂，青銅欄杆與古羅馬石柱宣告「新羅馬」的雄心。加洛林文藝復興的建築宣言，此後六百年德意志諸王加冕於斯。' },
          { title_zh: '聖但尼修道院教堂', title_orig: 'Basilique de Saint-Denis', author: '敘熱主持重建', era: '1135–1144', place: '聖但尼', language: '建築（法蘭西）', intro: '敘熱以「光即神顯」的狄奧尼修斯神學重建王家修道院，尖拱、肋拱與彩窗牆首次合為一體。哥德式建築的誕生地，神學直接催生新建築語言的最著名案例。' },
          { title_zh: '夏特爾主教座堂', title_orig: 'Cathédrale Notre-Dame de Chartres', author: '夏特爾建築工坊', era: '1194–1220', place: '夏特爾', language: '建築（法蘭西）', intro: '火災後一代人建成的哥德盛期典範，一百七十餘扇原裝彩窗的「夏特爾藍」與王者之門雕像群完整傳世。石與光的神學大全，中世紀朝聖與聖母敬禮的空間結晶。' },
          { title_zh: '巴黎聖母院', title_orig: 'Cathédrale Notre-Dame de Paris', author: '巴黎建築工坊（敘利的莫里斯發起）', era: '1163–1345', place: '巴黎', language: '建築（法蘭西）', intro: '塞納河心的哥德座堂，飛扶壁的成熟運用與雙塔立面成為此後座堂的原型。八百年間加冕、革命、焚毀與重生，法蘭西信仰與民族記憶的第一地標。' },
          { title_zh: '威尼斯聖馬可大教堂', title_orig: 'Basilica di San Marco', author: '威尼斯共和國（拜占庭工匠）', era: '1063–1094（鑲嵌歷代增修）', place: '威尼斯', language: '建築（義大利-拜占庭）', intro: '威尼斯仿君士坦丁堡聖使徒教堂建造的五穹頂國家教堂，金底鑲嵌畫積累八千平方公尺。拜占庭藝術在西方的最大殖民地，海洋共和國以聖髑與黃金自我加冕的聖所。' },
          { title_zh: '帕拉多羅黃金祭壇', title_orig: 'Pala d\'Oro', author: '君士坦丁堡與威尼斯金匠', era: '1105（1345 定裝）', place: '威尼斯聖馬可', language: '金工琺瑯（拜占庭）', intro: '聖馬可主祭壇的黃金屏，二百五十餘枚拜占庭掐絲琺瑯嵌於哥德金框，部分掠自第四次十字軍。拜占庭琺瑯藝術的最大寶庫，威尼斯與君士坦丁堡愛恨交纏的物證。' },
          { title_zh: '聖禮拜堂', title_orig: 'Sainte-Chapelle', author: '路易九世敕建', era: '1242–1248', place: '巴黎西堤島', language: '建築（法蘭西）', intro: '聖路易為安奉荊冕聖髑建造的宮廷禮拜堂，上堂四壁幾全為彩窗，千餘幅聖經場景懸浮於光中。哥德「輻射式」的極致，被譽為通往天國的玻璃聖髑匣。' },
          { title_zh: '蒙雷阿萊主教座堂鑲嵌畫', title_orig: 'Duomo di Monreale', author: '威廉二世敕建（拜占庭工匠）', era: '1174–1189', place: '西西里蒙雷阿萊', language: '鑲嵌畫（諾曼西西里）', intro: '諾曼王威廉二世的王家座堂，六千餘平方公尺金底鑲嵌鋪陳新舊約全史，迴廊雙柱雕飾窮極變化。諾曼、拜占庭與阿拉伯工藝共冶的西西里奇蹟，中世紀鑲嵌藝術的最大單一工程。' },
          { title_zh: '切法盧全能者基督鑲嵌畫', title_orig: 'Cristo Pantocratore di Cefalù', author: '拜占庭鑲嵌工匠（羅傑二世敕建）', era: '1148', place: '西西里切法盧', language: '鑲嵌畫（諾曼西西里）', intro: '切法盧座堂半穹的全能者基督，巨掌撫卷而目光悲憫，被譽為所有 Pantocrator 像中最人性的一尊。諾曼王權借拜占庭聖像自證天命，地中海文化交融的臉龐。' },
          { title_zh: '達夫尼修道院鑲嵌畫', title_orig: 'Μονή Δαφνίου', author: '拜占庭鑲嵌工坊', era: '約 1100', place: '雅典近郊達夫尼', language: '鑲嵌畫（拜占庭）', intro: '科穆寧古典主義的鑲嵌傑作，穹頂全能者基督嚴峻如審判之日，敘事鑲嵌優雅如古典浮雕。拜占庭中期藝術「莊嚴與優美並臻」的代表，世界遺產的希臘三大修道院之一。' },
          { title_zh: '科拉教堂鑲嵌與壁畫', title_orig: 'Chora (Kariye) Mosaics and Frescoes', author: '狄奧多爾‧梅託希特斯捐建', era: '1315–1321', place: '君士坦丁堡', language: '鑲嵌畫與壁畫（拜占庭）', intro: '大臣梅託希特斯重修科拉修道院，鑲嵌敘聖母生平，葬堂壁畫《下臨陰府》中基督拽起亞當夏娃如旋風。帕列奧洛格文藝復興的巔峰，拜占庭藝術臨終前最燦爛的迸發。' },
          { title_zh: '基輔聖索菲亞大教堂', title_orig: 'Собор святої Софії (Київ)', author: '智者雅羅斯拉夫敕建（拜占庭工匠）', era: '1037 起', place: '基輔', language: '建築與鑲嵌（基輔羅斯）', intro: '雅羅斯拉夫仿君士坦丁堡聖索菲亞建造的十三穹頂大教堂，祈禱聖母「不可摧毀之牆」鑲嵌鎮守後殿千年。羅斯受洗一代的信仰紀念碑，東斯拉夫文明的奠基聖所。' },
          { title_zh: '拉利貝拉巖鑿教堂群', title_orig: 'Lalibela Rock-Hewn Churches', author: '拉利貝拉王敕鑿', era: '約 1181–1221', place: '衣索比亞拉利貝拉', language: '岩鑿建築（衣索比亞）', intro: '扎格維王朝自火山岩整體下鑿的十一座教堂，聖喬治堂十字平面自岩床浮出如天啟。耶路撒冷失陷後的「新耶路撒冷」工程，非洲基督教建築的世界奇觀，至今禮儀不輟。' },
          { title_zh: '阿赫塔瑪爾聖十字教堂', title_orig: 'Աղթամարի Սուրբ Խաչ եկեղեցի', author: '建築師曼努埃爾（加吉克王敕建）', era: '915–921', place: '凡湖阿赫塔瑪爾島', language: '建築浮雕（亞美尼亞）', intro: '瓦斯普拉坎王加吉克在凡湖島上建造的聖十字教堂，外牆浮雕自約拿到大衛環帶鋪陳，為亞美尼亞雕刻的最高成就。湖光中的石刻聖經，亞美尼亞建築黃金時代的孤島明珠。' },
          { title_zh: '米萊舍瓦白天使壁畫', title_orig: 'Бели анђео (Милешева)', author: '塞爾維亞宮廷畫師', era: '約 1235', place: '塞爾維亞米萊舍瓦修道院', language: '壁畫（塞爾維亞）', intro: '米萊舍瓦修道院空墓天使壁畫，白袍天使回眸指向復活的空穴，靜穆超逸為拜占庭圈壁畫的絕品。塞爾維亞中世紀藝術的代表作，其形象已成塞爾維亞文化的象徵。' },
          { title_zh: '博雅納教堂壁畫', title_orig: 'Боянска църква', author: '博雅納畫師（佚名）', era: '1259', place: '索菲亞近郊博雅納', language: '壁畫（保加利亞）', intro: '保加利亞博雅納教堂的壁畫層，捐建者卡洛揚夫婦肖像寫實入微，基督與聖徒面容個性宛然。早於義大利文藝復興的「人性覺醒」筆觸，巴爾幹中世紀繪畫的世界遺產。' },
          { title_zh: '塔烏爾全能者壁畫', title_orig: 'Sant Climent de Taüll', author: '塔烏爾大師', era: '1123', place: '加泰隆尼亞博伊谷地', language: '壁畫（加泰隆尼亞）', intro: '庇里牛斯山村教堂後殿的全能者基督，剛硬輪廓與礦物原色迸發拜占庭圖式的野性力量。羅曼式壁畫的第一名作，二十世紀移藏巴塞隆納後成為加泰隆尼亞藝術的圖騰。' },
          { title_zh: '榮耀門廊', title_orig: 'Pórtico da Gloria', author: '馬特奧師傅', era: '1168–1188', place: '聖地牙哥‧德‧孔波斯特拉', language: '雕刻（加利西亞）', intro: '孔波斯特拉朝聖終點的三連門廊，啟示錄長老各持樂器環拱榮耀基督，笑容初綻於先知但以理的唇邊。羅曼式雕刻向哥德式人性化過渡的傑作，百萬朝聖者的天堂之門。' },
          { title_zh: '韋茲萊聖靈降臨山牆', title_orig: 'Tympan de Vézelay', author: '勃艮第雕刻工坊', era: '約 1120–1132', place: '韋茲萊聖瑪德蓮修道院', language: '雕刻（勃艮第）', intro: '韋茲萊前廊山牆刻聖靈自基督雙手放射於萬邦使徒，環帶上犬首人與巨耳族候於福音邊陲。宣教神學的石刻宣言，第二次十字軍即在此門前佈道啟程。' },
          { title_zh: '莫瓦薩克門廊雕刻', title_orig: 'Portail de Moissac', author: '朗格多克雕刻工坊', era: '約 1115–1130', place: '莫瓦薩克聖伯多祿修道院', language: '雕刻（朗格多克）', intro: '莫瓦薩克山牆刻啟示錄異象，廿四長老仰首如聞號角，門柱先知耶利米身軀如火焰扭動。羅曼式雕刻表現主義的極致，但丁式的石頭幻視。' },
          { title_zh: '歐坦最後審判山牆', title_orig: 'Tympan d\'Autun (Gislebertus)', author: '吉斯勒貝爾圖斯', era: '約 1130–1145', place: '歐坦聖拉撒路座堂', language: '雕刻（勃艮第）', intro: '「吉斯勒貝爾圖斯作此」署名於基督腳下，靈魂稱重的天平旁魔鬼作弊、亡者驚恐如漫畫。中世紀雕刻家署名的破天荒之舉，最後審判圖像最富戲劇性的石刻版本。' },
          { title_zh: '比薩洗禮堂講道壇', title_orig: 'Pulpito del Battistero di Pisa', author: '尼古拉‧皮薩諾', era: '1260', place: '比薩', language: '雕刻（義大利）', intro: '尼古拉‧皮薩諾借古羅馬石棺的人體語彙刻福音場景，聖母如朱諾、力士如赫拉克勒斯。古典雕刻精神七百年後的甦醒，義大利文藝復興雕塑的直接先聲。' },
          { title_zh: '摩西之井', title_orig: 'Puits de Moïse', author: '克勞斯‧斯呂特', era: '1395–1403', place: '第戎香莫爾加爾都西修道院', language: '雕刻（勃艮第）', intro: '斯呂特為勃艮第公爵墓園刻六位環井先知，摩西鬚髮如活、大衛憂鬱如真人臨場。哥德雕刻寫實主義的最高峰，北方文藝復興雕塑的黎明之作。' },
          { title_zh: '傑羅十字架', title_orig: 'Gero-Kreuz', author: '科隆奧託工坊', era: '約 965–970', place: '科隆主教座堂', language: '木雕（奧托德意志）', intro: '科隆大主教傑羅捐獻的真人大木雕苦像，基督垂首弛肌，為現存最早的紀念性受難雕像。自凱旋基督轉向受苦基督的圖像轉捩點，西方受難敬虔的雕刻元祖。' },
          { title_zh: '克洛斯特新堡琺瑯祭壇', title_orig: 'Verduner Altar', author: '維爾登的尼古拉', era: '1181', place: '克洛斯特新堡修道院', language: '金工琺瑯（默茲）', intro: '金工大師維爾登的尼古拉以五十一枚鎏金琺瑯板構築「律法前—律法下—恩典下」的預表神學圖系。默茲藝術的巔峰，古典人體語彙復甦的先兆，神學圖像程式設計的傑作。' },
          { title_zh: '昂熱天啟掛毯', title_orig: 'Tenture de l\'Apocalypse d\'Angers', author: '尼古拉‧巴塔耶織坊（讓‧德‧布呂日繪稿）', era: '1377–1382', place: '巴黎（今藏昂熱）', language: '掛毯（法蘭西）', intro: '安茹公爵委製的啟示錄掛毯，原長逾百米、七十餘景，巴比倫傾覆與新耶路撒冷織入經緯。中世紀織品藝術的最大傑作，百年戰爭亂世中的末世默想長卷。' },
          { title_zh: '威爾頓雙聯畫', title_orig: 'The Wilton Diptych', author: '佚名（法蘭西或英格蘭宮廷畫師）', era: '約 1395–1399', place: '倫敦', language: '蛋彩板繪（國際哥德）', intro: '理查二世的隨行祭壇雙聯畫，少年王由三聖者引見於聖母與天使群，天使皆佩白鹿王徽。國際哥德式的精緻極品，王權自獻於天后的圖像神學，今藏倫敦國家美術館。' },
          { title_zh: '弗拉基米爾聖母聖像', title_orig: 'Владимирская икона Божией Матери', author: '君士坦丁堡聖像師', era: '約 1131', place: '君士坦丁堡（傳入基輔／弗拉基米爾／莫斯科）', language: '聖像（拜占庭-羅斯）', intro: '「慈憐型」聖母的原典之作：聖子貼頰、聖母預見受難的憂目。自君士坦丁堡北傳為羅斯的守護聖像，遷城莫斯科屢繫國運，俄羅斯宗教情感的第一聖物。' },
          { title_zh: '三位一體聖像', title_orig: 'Троица (Андрей Рублёв)', author: '安德烈‧盧布廖夫', era: '約 1411–1425', place: '謝爾蓋聖三一修道院', language: '聖像（莫斯科羅斯）', intro: '盧布廖夫以幔利橡樹三天使寫三一奧蹟，三位一體的環形凝視向觀者留出第四席。一五五一年百章會議定其為聖像典範，「盧布廖夫的三一」自此即正教聖像神學的代名詞。' },
          { title_zh: '西奈聖像群（中世紀）', title_orig: 'Sinai Icons (Medieval Collection)', author: '西奈與君士坦丁堡聖像師', era: '9–15 世紀', place: '西奈聖凱瑟琳修道院', language: '聖像（拜占庭）', intro: '聖凱瑟琳修道院因地處帝國之外而躲過破像浩劫，庋藏聖像逾兩千幀，梯子聖像與十二大節組像為中世紀部分的名品。拜占庭聖像史連續無缺的唯一寶庫，聖像研究的麥加。' },
          { title_zh: '斯克羅威尼禮拜堂壁畫', title_orig: 'Cappella degli Scrovegni', author: '喬託‧迪‧邦多內', era: '約 1303–1305', place: '帕多瓦', language: '壁畫（義大利）', intro: '高利貸者之子為贖父罪建堂，喬託以卅八景鋪陳聖母與基督生平，猶大之吻的對視與哀悼基督的慟哭開繪畫的人性紀元。西方繪畫「空間與情感」革命的第一現場。' },
          { title_zh: '寶座聖母大祭壇畫', title_orig: 'Maestà (Duccio)', author: '杜喬‧迪‧博尼塞尼亞', era: '1308–1311', place: '錫耶納', language: '蛋彩板繪（義大利）', intro: '錫耶納主教座堂的雙面大祭壇畫，正面聖母升座受千聖朝賀，背面廿六景受難敘事。完工之日全城列隊鐘鼓迎畫入堂，拜占庭優雅與哥德敘事交融的錫耶納畫派巔峰。' },
          { title_zh: '聖馬可修道院壁畫', title_orig: 'Affreschi di San Marco (Beato Angelico)', author: '弗拉‧安傑利科', era: '約 1438–1445', place: '佛羅倫斯', language: '壁畫（義大利）', intro: '道明會士安傑利科為本院每間修室繪一幅默想壁畫，樓梯轉角的天使報喜靜如屏息。繪畫即祈禱的最純粹案例，「畫基督者必先與基督同活」的修道藝術總綱。' },
          { title_zh: '根特祭壇畫', title_orig: 'Het Lam Gods', author: '胡伯特與揚‧範艾克', era: '1432', place: '根特聖巴夫座堂', language: '油彩板繪（法蘭德斯）', intro: '範艾克兄弟的十二翼大祭壇畫，神秘羔羊的崇拜將啟示錄禮儀鋪展於發光的油彩風景，亞當夏娃逼真如立於壁龕。油畫技法成熟的宣言，北方文藝復興的第一鉅作。' },
          { title_zh: '下十字架（羅希爾）', title_orig: 'De kruisafneming (Rogier van der Weyden)', author: '羅希爾‧範德魏登', era: '約 1435', place: '魯汶（今藏普拉多）', language: '油彩板繪（法蘭德斯）', intro: '羅希爾把下架群像壓入淺金龕如活人雕刻，昏厥的聖母與垂落的基督身形互為迴文。悲慟的幾何學登峰造極，北方繪畫最常被臨摹的受難構圖。' },
          { title_zh: '死亡的勝利（比薩公墓壁畫）', title_orig: 'Trionfo della Morte (Camposanto)', author: '布法馬可（傳）', era: '約 1336–1341', place: '比薩公墓', language: '壁畫（義大利）', intro: '比薩公墓長牆壁畫：獵遊貴族撞見三具敞棺，死神鐮刀掠過宴樂人群，隱士獨得安穩。黑死病前夕的死亡默想巨構，李斯特觀此而作《死之舞》，中世紀生死觀的圖像總綱。' }
        
        ]
      },
      {
        key: 'drama-sacred-art',
        label: '神蹟劇與宗教藝術部',
        label_en: 'Sacred Drama and Religious Art',
        desc: '中世紀神蹟劇與道德劇的舞台文本，以及建築圖稿與圖像象徵手冊。',
        works: [
          { title_zh: '凡人', title_orig: 'Everyman / Elckerlijc', author: '佚名', era: '15 世紀後期', place: '低地國—英格蘭', language: '中古英文（源出中古荷蘭文）', intro: '中世紀道德劇（morality play）的代表作，以擬人化的角色搬演一則關於死亡與救贖的寓言：「凡人」突遭「死亡」召喚去面見天主交帳，沿途求「財富」、「美貌」、「親朋」、「知識」相伴皆遭拒，唯有「善行」願與他同入墳墓。全劇以舞台寓言訓誨觀眾省察生命終向、看輕世俗而注重善功與懺悔，是中世紀宗教戲劇道德教化功能的最佳範例。' },
          { title_zh: '英格蘭神蹟劇連環套', title_orig: 'Mystery Cycles (York, Wakefield, Chester)', author: '各城同業公會（佚名劇作者）', era: '14–15 世紀', place: '英格蘭約克、韋克菲爾德、切斯特', language: '中古英文', intro: '中世紀英格蘭各城在基督聖體節等慶典演出的成套聖經劇，由各同業公會分擔不同劇目，從創世、墮落、洪水、基督降生、受難一路演到末日審判，於街頭活動花車（pageant wagon）上巡迴搬演。劇本以方言寫成，兼具虔敬與市井詼諧（如韋克菲爾德的牧羊人鬧劇）。它將救恩史搬上市民舞台，是中世紀群眾宗教教育與戲劇傳統的核心。' },
          { title_zh: '建築圖稿', title_orig: 'Livre de portraiture / Album', author: '奧內庫爾的維拉爾', era: '約 1230 年代', place: '法國皮卡第', language: '古法文', intro: '十三世紀一位遊歷各地的匠師所留下的圖稿冊，現存三十三葉羊皮，繪有教堂建築立面與平面、機械裝置、人物與動物比例、幾何作圖法及雕像草圖，並附親筆說明。它是中世紀盛期哥德建築與工坊技藝的罕見第一手見證，透露出當時匠人如何以幾何法則構築神聖空間，被視為理解哥德主教座堂營造思維與宗教造型藝術的珍貴文獻。' },
          { title_zh: '圖像象徵手冊（明鏡叢書）', title_orig: 'Speculum / Bestiarium', author: '博韋的文森等（佚名彙編）', era: '12–13 世紀', place: '法國—英格蘭', language: '拉丁文', intro: '中世紀「明鏡」（Speculum）類百科與動物寓言集（Bestiarium）的彙編傳統，將自然萬物、聖經事蹟與歷史人物逐一賦予屬靈寓意：鵜鶘以血哺雛喻基督捨身，鳳凰焚而復生喻復活。這套象徵體系是中世紀讀解世界的鑰匙，深刻塑造主教座堂的雕刻、彩窗與抄本插圖。它指引藝術家如何以可見之物表達不可見之道，是宗教圖像學的根本依據。' },
          { title_zh: '羅斯維塔戲劇集', title_orig: 'Dramata Hrotsvithae', author: '甘德斯海姆的羅斯維塔', era: '約 960–973', place: '甘德斯海姆女修道院', language: '拉丁文', intro: '薩克森女修道院修女羅斯維塔仿泰倫提烏斯體裁寫成六部殉道貞女劇，自言「以同一形式頌揚聖女的貞勇」。古典戲劇沉寂五百年後的第一位劇作家，且是女性，戲劇史與女性書寫史的雙重驚奇。' },
          { title_zh: '德行序列劇', title_orig: 'Ordo Virtutum', author: '賓根的希爾德加德', era: '約 1151', place: '賓根魯佩茨貝格', language: '拉丁文', intro: '希爾德加德為修女們譜寫的音樂道德劇，十六位德行擬人與魔鬼爭奪靈魂，魔鬼是全劇唯一不得歌唱的角色。現存最早有完整音樂的道德劇，比同類劇早兩百年，女修院藝術的巔峰創造。' },
          { title_zh: '亞當劇', title_orig: 'Le Jeu d\'Adam (Ordo representacionis Ade)', author: '佚名（盎格魯-諾曼教士）', era: '約 1150–1170', place: '英格蘭／諾曼第', language: '盎格魯-諾曼法文', intro: '以俗語演出墮落、該隱與先知行列的三段劇，舞臺指示詳盡：樂園設於教堂門前高臺，魔鬼竄入觀眾之間。宗教劇自禮儀走向廣場的第一步，法語戲劇現存最早的傑作。' },
          { title_zh: '忒奧菲勒的奇蹟', title_orig: 'Le Miracle de Théophile', author: '呂特博夫', era: '約 1261', place: '巴黎', language: '古法文', intro: '巴黎詩人呂特博夫把「賣身魔鬼的副主教蒙聖母搭救」的古老傳說搬上舞臺，忒奧菲勒的絕望獨白如浮士德先聲。聖母奇蹟劇的代表作，中世紀「契約與救贖」想像的戲劇結晶。' },
          { title_zh: '聖尼古拉劇', title_orig: 'Le Jeu de saint Nicolas', author: '阿拉斯的讓‧博岱爾', era: '約 1200', place: '阿拉斯', language: '古法文', intro: '阿拉斯市民詩人博岱爾把聖尼古拉護寶奇蹟嵌入十字軍與酒館嬉鬧，聖徒劇與市井喜劇並冶一爐。城市戲劇文化興起的標本，法語戲劇由教堂走入市集的里程碑。' },
          { title_zh: '但以理劇', title_orig: 'Ludus Danielis', author: '博韋座堂學子', era: '約 1230', place: '博韋', language: '拉丁文', intro: '博韋座堂青年學子為新年節慶編演的但以理音樂劇，伯沙撒盛宴與獅坑獲救配以華麗遊行音樂，樂譜完整傳世。中世紀音樂劇場的最高成就，二十世紀復排後成為古樂劇目的常青樹。' },
          { title_zh: '第二牧人劇', title_orig: 'The Second Shepherds\' Play', author: '威克菲爾德大師', era: '約 1425–1450', place: '威克菲爾德', language: '中古英語', intro: '威克菲爾德連環劇中的牧人劇：偷羊賊把羊藏入搖籃冒充嬰兒，鬧劇急轉為伯利恆馬槽的朝拜。世俗滑稽與道成肉身互為鏡像，中世紀英語戲劇最傑出的一折。' },
          { title_zh: '格雷邦受難奧蹟劇', title_orig: 'Le Mystère de la Passion (Arnoul Gréban)', author: '阿爾努‧格雷邦', era: '約 1450', place: '巴黎', language: '中古法文', intro: '巴黎聖母院樂長格雷邦寫成的三萬五千行受難大劇，四日連演自創世至復活，動員市民數百人。中世紀城市的全民劇場總體藝術，法語受難劇傳統的最高峰。' },
          { title_zh: '東方三王劇', title_orig: 'Auto de los Reyes Magos', author: '佚名（託萊多教士）', era: '約 1150–1200', place: '託萊多', language: '古卡斯提爾文', intro: '殘存一百四十七行的三王朝聖劇，為西班牙語現存最早的戲劇文本，三王仰觀新星的獨白已見性格刻畫。收復失地時代多元託萊多的產物，西語戲劇史的第一頁。' },
          { title_zh: '基督受難劇（拜占庭）', title_orig: 'Christos Paschon', author: '託名拿先斯的格列高利（拜占庭編者）', era: '11–12 世紀（傳統歸 4 世紀）', place: '君士坦丁堡', language: '希臘文', intro: '以歐裡庇得斯詩行拼綴而成的受難悲劇，聖母如希臘悲劇女主角慟哭於十字架下。「引詩成劇」（cento）技法的極致，拜占庭對古典悲劇遺產最奇特的基督教挪用。' },
          { title_zh: '奧爾良解圍奧蹟劇', title_orig: 'Le Mistère du siège d\'Orléans', author: '佚名（奧爾良市民圈）', era: '約 1435–1470', place: '奧爾良', language: '中古法文', intro: '貞德解圍後數十年間奧爾良搬演的兩萬行紀念大劇，聖女生前事蹟首度登上舞臺，兼具戲劇與集體記憶儀式。以奧蹟劇形式演「當代聖徒」的孤例，貞德崇敬的最早文藝見證。' }
        
        ]
      }
    ]
  },
  wai: {
    summary: '基督宗教以外的中世紀宗教詩文：伊斯蘭蘇菲的神祕主義詩與安達魯斯抒情詩，以及猶太教黃金時代的希伯來宗教詩（piyyutim）。',
    divisions: [
      {
        key: 'islamic-poetry',
        label: '伊斯蘭詩文部',
        label_en: 'Islamic Poetry',
        desc: '魯米的蘇菲長篇詩、安達魯斯的抒情詩傳統，以及波斯蘇菲神祕詩。',
        works: [
          { title_zh: '瑪斯納維', title_orig: 'Mathnawī-yi Maʿnawī / مثنوی معنوی', author: '賈拉勒丁‧魯米', era: '13 世紀', place: '安那托利亞科尼亞', language: '波斯文', intro: '蘇菲大師魯米歷時多年口授、由弟子記錄的六卷長篇敘事詩，逾兩萬六千聯句，被後世尊為「波斯文的古蘭經」。全詩以雙行押韻（mathnawī）體裁，穿插寓言、軼事、聖訓與古蘭經典故，引人由表象的故事深入靈性的奧義，主題環繞靈魂對神聖之愛的渴慕、自我的消融與重歸本源。它是伊斯蘭神祕主義文學的最高成就，影響跨越波斯、土耳其與南亞諸文化。' },
          { title_zh: '安達魯斯摩爾人抒情詩', title_orig: 'Muwashshaḥ wa-Zajal', author: '伊本‧古茲曼、伊本‧宰敦等', era: '11–13 世紀', place: '安達魯斯（西班牙南部）', language: '阿拉伯文（俗語結尾雜羅曼語）', intro: '中世紀伊斯蘭西班牙發展出的兩種富於音樂性的抒情詩體：穆瓦沙赫（muwashshaḥ）為多節環韻的雅言詩，末尾常綴以羅曼俗語的「下闋」（kharja）；扎吉勒（zajal）則通篇用安達魯斯方言寫成。兩者題材兼及愛情、美酒、自然與蘇菲神祕之愛，旋律優美而雅俗交融，是伊比利半島跨文化的詩樂結晶，並對歐洲遊唱詩人的抒情傳統有所啟發。' },
          { title_zh: '波斯蘇菲神祕詩', title_orig: 'Dīwān-i Ṣūfiyāna', author: '阿塔爾、薩納伊、伊拉基等', era: '12–14 世紀', place: '波斯（呼羅珊、設拉子）', language: '波斯文', intro: '哈菲茲之前的波斯蘇菲詩傳統，以薩納伊、阿塔爾、伊拉基等為代表。他們以抒情短詩（ghazal）與長篇譬喻詩（如阿塔爾的鳥語會議）表達對神聖之愛的追尋，將美酒、佳人、夜鶯與玫瑰等世俗意象轉化為靈性象徵：醉非醉於酒，乃醉於神。此一象徵體系與曖昧多義的詩語，奠定了後世哈菲茲集大成的波斯神祕抒情詩典範。' }
        ]
      },
      {
        key: 'jewish-poetry',
        label: '猶太詩文部',
        label_en: 'Jewish Poetry',
        desc: '西班牙黃金時代的希伯來宗教詩，含伊本‧蓋比魯勒與猶大‧哈列維的代表詩篇。',
        works: [
          { title_zh: '王冠', title_orig: 'Keter Malkhut / כתר מלכות', author: '所羅門‧伊本‧蓋比魯勒', era: '11 世紀', place: '安達魯斯（薩拉戈薩、馬拉加）', language: '希伯來文', intro: '猶太哲學家兼詩人伊本‧蓋比魯勒的長篇宗教頌詩，分為頌讚、宇宙論與懺悔三大部分：先以新柏拉圖哲思頌揚造物主的獨一與超越，繼而沿天界諸層描繪受造宇宙的宏偉秩序，終以人靈在造物主前的卑微懺悔作結。全詩思想深邃、語言莊嚴，融哲學與虔敬於一爐，被收入贖罪日（Yom Kippur）禮儀誦讀，是希伯來宗教詩的不朽傑作。' },
          { title_zh: '錫安之歌', title_orig: 'Shirei Tziyyon / שירי ציון', author: '猶大‧哈列維', era: '12 世紀', place: '安達魯斯—埃及（赴聖地途中）', language: '希伯來文', intro: '黃金時代詩人兼哲人猶大‧哈列維的一組思慕聖地之詩，以「我心在東方，我身卻在西陲」的名句傾訴對錫安與耶路撒冷的深切渴慕。詩人晚年毅然離開安達魯斯的安逸，啟程朝向聖地，這組詩即此心路的見證。其情感真摯熾烈、意象壯麗，被收入聖殿被毀紀念日（Tisha be-Av）的哀歌誦讀，是中世紀希伯來愛國與宗教抒情詩的頂峰。' },
          { title_zh: '希伯來禮儀詩', title_orig: 'Piyyutim / פיוטים', author: '伊本‧蓋比魯勒、伊本‧厄茲拉兄弟、猶大‧哈列維等', era: '10–13 世紀', place: '安達魯斯與普羅旺斯', language: '希伯來文', intro: '中世紀西班牙黃金時代繁盛的猶太禮儀詩傳統（piyyut），詩人們借鑑阿拉伯詩的格律與修辭，創作大量插入會堂祈禱的讚詩、懺悔詩（seliḥot）與節期詩歌。題材涵蓋頌神、求赦、流亡之痛與救贖之盼，語言精煉、典故密集，融希伯來經典與阿拉伯詩藝於一體。這批禮儀詩大量進入塞法迪與阿什肯納茲的祈禱書，至今仍於會堂節期中誦唱。' }
        ]
      }
    ]
  }
},
    {
  key: 'xuandao',
  name: '宣道藏',
  name_en: 'Canon of Preaching & Mission',
  glyph: '宣',
  genres: '講疏‧宣教‧解經',
  summary: '宣道藏收中世紀（約 800–1500）「對內宣道」與「對外宣教」兩面的文獻：一面是修道院與托缽會向信眾講解福音、闡釋雅歌與聖言的講疏傳統，一面是道明會、方濟會向異教徒、猶太人、穆斯林傳揚信仰的宣教手冊與護教論著，外加貫通中世紀的拉丁解經學與伊斯蘭、猶太兩大傳統的經注。',
  zheng: {
    summary: '正藏錄基督宗教內部的講道、宣教與解經三部：講疏部承奧古斯丁、大額我略以降的證道傳統，由熙篤會與托缽會發揚；宣教部記托缽修會向「外教人」傳道的方法與護教論述；解經部立中世紀拉丁聖經注釋的兩大骨幹。',
    divisions: [
      {
        key: 'inner-sermon',
        label: '對內講疏部',
        label_en: 'Sermons to the Faithful',
        desc: '修道院與托缽會向信眾、會士講解聖言的證道傳統，自拉丁神祕釋經至德語民間講道。',
        works: [
          { title_zh: '雅歌講疏', title_orig: 'Sermones super Cantica Canticorum', author: '克萊爾沃的伯爾納鐸', era: '約 1135–1153', place: '法蘭西‧克萊爾沃修道院', language: '拉丁文', intro: '熙篤會大師伯爾納鐸晚年向會士講授的雅歌系列，共八十六篇，僅及雅歌第三章便因講者離世而中止。伯爾納鐸把新娘與良人之愛讀作靈魂與聖言、教會與基督的婚配，層層推進「親吻」三階——吻足、吻手、吻口——對應悔改、進德與默觀的合一。文字熱烈而精微，奠定中世紀新娘神祕主義（Brautmystik）的典範，影響遍及後世默觀傳統。', note: '後由其門人續講補足全卷', link: '' },
          { title_zh: '福音講道四十篇（中世紀傳本）', title_orig: 'Homiliae in Evangelia', author: '大額我略（教宗額我略一世）', era: '590–604 原講；中世紀廣傳', place: '羅馬', language: '拉丁文', intro: '教宗大額我略在羅馬諸聖殿向會眾講解主日及瞻禮福音的四十篇講道集，雖成於六世紀末，卻在整個中世紀被反覆抄寫、誦讀、引用，成為西方講道學的基石教本。內容平實懇切，善以譬喻牧養庶民，兼顧字面與寓意兩層，並大量保存當時羅馬城的軼事與神蹟傳聞。中世紀講道集與《標準註釋》皆奉之為權威來源。', note: '雖屬教父時代，因中世紀奉為證道範本而收入', link: '/fathers' },
          { title_zh: '主日講道集（道明會與方濟會編本）', title_orig: 'Sermones Dominicales', author: '托缽修會講道師（道明會、方濟會佚名群編）', era: '十三至十四世紀', place: '巴黎‧波隆那‧亞西西等大學與會院', language: '拉丁文', intro: '十三世紀托缽修會興起後大量編纂的主日及瞻禮講道範本，供巡迴會士隨身取用。此類集子以教會年曆編排，每篇先列經題（thema），再以分段（divisio）逐層展開，附譬喻、聖人故事與神學要點，是「經院式講道」（sermo modernus）成熟的標誌。道明會重教義析理，方濟會重悔改感召，二會講道集流傳極廣，奠定後世佈道體例。', note: '託名與佚名集子甚多，此為傳統匯編', link: '' },
          { title_zh: '德語講道集', title_orig: 'Deutsche Predigten', author: '埃克哈特大師', era: '約 1300–1327', place: '神聖羅馬帝國‧科隆‧史特拉斯堡', language: '中古高地德語', intro: '道明會神學家埃克哈特大師以母語向修女與平信徒所作的講道，是中世紀少見的高水準德語神祕思想文獻。他講「靈魂的火花」（Seelenfünklein）、「神性的虛無」（Gottheit）與「離捨」（Abgeschiedenheit），主張靈魂須空盡自我，方能讓上帝在其中「誕生」。語言鋒利弔詭，部分命題身後遭教廷審查，卻深刻塑造了陶勒、蘇索與萊茵蘭神祕主義一脈。', note: '部分命題於 1329 年《主在田間》詔書中受譴', link: '' },
          { title_zh: '保羅執事欽定講道集', title_orig: 'Homiliarium Pauli Diaconi', author: '保羅執事（卡爾大帝敕編）', era: '約 797', place: '蒙特卡西諾／亞琛', language: '拉丁文', intro: '卡爾大帝命倫巴底學者保羅執事自教父講章精選編成的官定講道集，按禮儀年編排，敕令全國教堂日課誦讀。它統一了加洛林帝國的講壇文本，此後數百年西方夜課誦讀的教父講章大體出此，是中世紀講道標準化的奠基工程。' },
          { title_zh: '海默講道集', title_orig: 'Homiliae Haimonis Autissiodorensis', author: '奧塞爾的海默', era: '約 840–865', place: '奧塞爾聖日耳曼修道院', language: '拉丁文', intro: '加洛林奧塞爾學派宗師海默的禮儀年講道集，融釋經與教義於平易講章，供修士與堂區司鐸取用。其講章長期混入教父名下流傳而影響倍增，是九世紀「學校講道」的代表，中世紀講道文本層累傳統的典型個案。' },
          { title_zh: '斯馬拉格杜斯書信福音講解集', title_orig: 'Collectiones in epistolas et evangelia', author: '聖米耶勒的斯馬拉格杜斯', era: '約 810–820', place: '凡爾登聖米耶勒修道院', language: '拉丁文', intro: '斯馬拉格杜斯按禮儀年逐主日輯解書信與福音經課的講解集，取材教父而剪裁為實用講章底本。本書流傳抄本逾百部，供中世紀司鐸備道數百年，見證加洛林改革把「有講道可用」列為堂區牧養的基本建設。' },
          { title_zh: '艾爾弗裡克天主教講道集', title_orig: 'Sermones catholici (Catholic Homilies)', author: '艾爾弗裡克', era: '約 990–995', place: '塞恩／恩舍姆', language: '古英語', intro: '修道院長艾爾弗裡克以古英語寫成的兩輯各四十篇講道，供司鐸向不諳拉丁文的會眾宣講，文體節奏鏗鏘近乎韻文。他自陳為免「無知者曲解」而譯講並重，是歐洲俗語講道文學最早的高峰，古英語散文的典範。' },
          { title_zh: '布里克林講道集', title_orig: 'Blickling Homilies', author: '佚名（英格蘭堂區編者）', era: '10 世紀（971 年題記）', place: '英格蘭', language: '古英語', intro: '存於布里克林府邸抄本的十八篇古英語講道，成於艾爾弗裡克之前，雜採偽經傳說與末世警語，反映千禧年前夕民間講壇的實態。其保存的聖米迦勒山異象等母題為研究盎格魯-撒克遜大眾信仰的珍貴材料。' },
          { title_zh: '韋爾切利講道集', title_orig: 'Vercelli Homilies', author: '佚名（英格蘭編者）', era: '10 世紀後期', place: '英格蘭（抄本存義大利韋爾切利）', language: '古英語', intro: '與古英語宗教詩同存於韋爾切利抄本的廿三篇講道，主題偏重悔改、審判與靈魂對肉身的控訴，語氣沉鬱。抄本因朝聖路線流落義大利反得保全，是古英語講道文學與朝聖文化交會的獨特見證。' },
          { title_zh: '沃夫斯坦講道集', title_orig: 'Homiliae Wulfstani (Sermo Lupi ad Anglos)', author: '約克大主教沃夫斯坦', era: '約 1002–1023', place: '約克／伍斯特', language: '古英語', intro: '約克大主教沃夫斯坦以「狼」為筆名的講道集，名篇〈狼致英吉利人講道〉把丹麥人入侵解作民族罪惡的天譴，句式如鼓點擂心。他兼為兩朝立法者，講道與法典同筆，是講壇語言介入國難的千年名文。' },
          { title_zh: '明燈問答', title_orig: 'Elucidarium', author: '奧頓的霍諾留', era: '約 1098–1101', place: '坎特伯裡／雷根斯堡', language: '拉丁文', intro: '霍諾留以師徒問答總括基督教義的教理手冊，自三一、救贖至末世逐條作答，語簡而斷然。本書為中世紀最流行的平信徒教理書，譯成法、德、古諾斯諸語，堂區司鐸賴以答問講授，塑造數百年大眾信仰的常識框架。' },
          { title_zh: '聖伯爾納禮儀年講道集', title_orig: 'Sermones per annum', author: '克萊爾沃的伯爾納', era: '約 1128–1153', place: '克萊爾沃', language: '拉丁文', intro: '伯爾納按禮儀年向修士宣講的講道集，自將臨期至諸聖節凡百餘篇，蜜般的文采使他得號「蜜口博士」。這批講章與其雅歌講疏同為熙篤靈修的雙峰，中世紀修道講道藝術的最高典範。' },
          { title_zh: '莫里斯‧德‧蘇利講道集', title_orig: 'Sermons de Maurice de Sully', author: '巴黎主教莫里斯‧德‧蘇利', era: '約 1160–1196', place: '巴黎', language: '古法文／拉丁文', intro: '興建巴黎聖母院的主教蘇利為堂區司鐸編寫的主日講道範本，並以古法語散文流傳，是法語最早的散文講道集之一。其講章平白切用，專為牧養市井會眾而設，見證十二世紀主教對堂區講道品質的制度性關懷。' },
          { title_zh: '英諾森三世講道集', title_orig: 'Sermones Innocentii III', author: '教宗英諾森三世', era: '約 1198–1216', place: '羅馬', language: '拉丁文', intro: '中世紀權勢最盛的教宗英諾森三世親撰的講道集，按節期與共通主題編排，自序稱講道為主教首務。其講章神學縝密而意象華麗，第四次拉特朗會議責成各地設置講道職，教宗以身作則的這批講道即其註腳。' },
          { title_zh: '聖安東尼主日講道集', title_orig: 'Sermones dominicales et festivi', author: '帕多瓦的安東尼', era: '約 1227–1231', place: '帕多瓦', language: '拉丁文', intro: '方濟會首位神學教師帕多瓦的安東尼為講道者編寫的主日與節期講道底本，經文對觀與寓意繁富如織。生前佈道萬人空巷、傳說向魚群宣講的安東尼，其存世講章實為供人取材的「講道百科」，一九四六年因此獲宣為教會聖師。' },
          { title_zh: '波納文圖拉主日講道集', title_orig: 'Sermones de tempore (Bonaventura)', author: '波納文圖拉', era: '約 1250–1273', place: '巴黎', language: '拉丁文', intro: '「熾愛博士」波納文圖拉存世講道數百篇，於巴黎向大學師生與王室宣講，經聽者筆錄傳世。講章以嚴整的經院分段承載密契的上升動勢，是十三世紀「大學講道」文類的最高標本，與其神學著作互為表裡。' },
          { title_zh: '貝爾託德講道集', title_orig: 'Predigten Bertholds von Regensburg', author: '雷根斯堡的貝爾託德', era: '約 1240–1272', place: '德意志南部巡迴', language: '德文／拉丁文', intro: '方濟會巡迴佈道家貝爾託德足跡遍及德語區，野外聽眾動輒數萬，需以旗幟示風向使眾人聞聲。其德語講道集鮮活如市集現場，痛斥高利貸與虛榮服飾，是中世紀德語散文與大眾佈道的第一座高峰。' },
          { title_zh: '沃拉金講道集', title_orig: 'Sermones Iacobi de Voragine', author: '雅各‧德‧沃拉金', era: '約 1270–1298', place: '熱那亞', language: '拉丁文', intro: '《黃金傳說》作者、熱那亞總主教沃拉金的講道範本集，分主日、聖徒與聖母三系數百篇，供講道者按曆取用。其流傳之廣僅次於其聖傳，二者共構中世紀晚期講壇的材料庫，見證道明會「講道工業」的規模。' },
          { title_zh: '喬爾達諾俗語講道集', title_orig: 'Prediche di Giordano da Pisa', author: '喬爾達諾‧達‧比薩', era: '1303–1309', place: '佛羅倫斯／比薩', language: '義大利文', intro: '道明會士喬爾達諾在佛羅倫斯的托斯卡納語講道七百餘篇由聽眾當場筆錄，開俗語講道實錄之先。講章雜記城市生活，其一三〇六年講道更留下眼鏡發明的最早文字記載，兼為語言史與社會史的活檔案。' },
          { title_zh: '奎德林堡的約旦講道集', title_orig: 'Opus postillarum et sermonum Iordani', author: '奎德林堡的約旦', era: '約 1365–1380', place: '埃爾福特', language: '拉丁文', intro: '奧斯定隱修會士約旦的講道與後注大全，按禮儀年集成數百篇，兼收其會祖傳統的靈修教導，流傳中歐抄本極多。他是十四世紀「講道彙編」文化的代表，其書為晚期中世紀司鐸的標準參考，亦預示奧斯定會的改革土壤。' },
          { title_zh: '米爾克節期講道集', title_orig: 'Festial (John Mirk)', author: '約翰‧米爾克', era: '約 1380–1390', place: '什羅普郡利勒斯霍爾修道院', language: '中古英語', intro: '奧斯定會律修士米爾克為粗通文墨的堂區司鐸編寫的英語節期講道集，逐節配聖徒故事與奇蹟例話，語極平白。本書為中世紀晚期英格蘭最流行的講道書，印刷時代再版逾二十次，正統堂區講壇對羅拉德挑戰的回應。' },
          { title_zh: '布林頓主教講道集', title_orig: 'Sermones Thomae Brinton', author: '羅徹斯特主教託馬斯‧布林頓', era: '1373–1389', place: '羅徹斯特／倫敦', language: '拉丁文', intro: '羅徹斯特主教布林頓存世百餘篇講道，於農民起義與教會分裂之際直斥朝政腐敗與貴族欺壓，名句「鐘上之舌」自況主教職分。其講章是十四世紀英格蘭社會批判講道的代表，史家重建瓦特‧泰勒起義背景的要籍。' },
          { title_zh: '帕薩萬蒂真悔改之鏡', title_orig: 'Lo specchio di vera penitenza', author: '雅各布‧帕薩萬蒂', era: '1354', place: '佛羅倫斯', language: '義大利文', intro: '道明會士帕薩萬蒂把大瘟疫翌年的四旬期講道整理為悔改論述，穿插地獄異象與例話，托斯卡納語文溫潤典雅。本書為黑死病世代懺悔心態的文學結晶，義大利語散文史的名著，講道與文學合流的典型。' },
          { title_zh: '文生‧費雷爾講道集', title_orig: 'Sermones sancti Vincentii Ferrerii', author: '文生‧費雷爾', era: '約 1399–1419', place: '伊比利／法蘭西／義大利巡迴', language: '加泰隆尼亞文／拉丁文', intro: '道明會佈道家費雷爾率悔罪行列巡迴西歐二十年，以末世將臨呼喚悔改，聽眾常逾萬人，講道由隨行筆錄者存記數百篇。其加泰隆尼亞語講章尤為母語散文瑰寶，是中世紀晚期巡迴佈道現象的第一手言語紀錄。' },
          { title_zh: '卡皮斯特拉諾講道文獻', title_orig: 'Sermones Iohannis de Capistrano', author: '卡皮斯特拉諾的約翰', era: '約 1417–1456', place: '義大利／中歐巡迴', language: '拉丁文', intro: '方濟會嚴規派佈道家卡皮斯特拉諾巡迴義大利與中歐，講道動員之力終匯為一四五六年貝爾格勒解圍——七旬老僧親執十字督軍。其存世講章與宣講文獻見證講道如何轉為軍事動員，是中世紀末講壇權能的極端個案。' },
          { title_zh: '卡拉喬洛講道集', title_orig: 'Sermones Roberti Caracciolo', author: '羅貝託‧卡拉喬洛', era: '約 1450–1495', place: '那不勒斯／萊切', language: '義大利文／拉丁文', intro: '方濟會佈道家卡拉喬洛被譽為「第二保羅」，其四旬期講道集於印刷初期刊行數十版，為十五世紀最暢銷的講道書。他戲劇化的講臺身段與市場化的印本流通，標誌中世紀講道向印刷文化過渡的臨界點。' },
          { title_zh: '維特里通俗講道集', title_orig: 'Sermones vulgares', author: '雅各‧德‧維特里', era: '約 1226–1240', place: '阿卡／羅馬', language: '拉丁文', intro: '維特里按聽眾身分——騎士、商賈、農夫、寡婦、痲瘋者——分別撰寫的「按階層講道」範本集，開 ad status 講道文類之典範。講章正文與例話交織，把福音話語精準投向中世紀社會的每一格棚架，是講道社會學的第一文獻。' },
          { title_zh: '胡斯伯利恆講道集', title_orig: 'Betlémská kázání (Jan Hus)', author: '揚‧胡斯', era: '1402–1412', place: '布拉格伯利恆禮拜堂', language: '捷克文', intro: '胡斯任布拉格伯利恆禮拜堂講道者十年，以捷克語向三千聽眾日日宣講，直斥贖罪券與教士積弊，講章由其親訂與聽錄並存。伯利恆講壇是捷克宗教改革的搖籃，這批講道使俗語宣講成為民族運動的火種。' },
          { title_zh: '米利奇講道集', title_orig: 'Sermones Milicii de Chremsir', author: '克羅梅日什的米利奇', era: '約 1364–1374', place: '布拉格', language: '捷克文／拉丁文', intro: '米利奇棄高俸投身講道，日講數場，感化布拉格妓院街區改建為「新耶路撒冷」悔改者之家，被尊為捷克改革運動之父。其講道集《贖罪者》等以末世迫切呼喚悔改，是胡斯運動的直接精神先驅。' },
          { title_zh: '薩佛納羅拉講道集', title_orig: 'Prediche di Girolamo Savonarola', author: '薩佛納羅拉', era: '1490–1498', place: '佛羅倫斯', language: '義大利文', intro: '道明會士薩佛納羅拉在佛羅倫斯以哈該書、詩篇與出埃及記系列講道震動全城，宣告教會刑罰將至、力主政教更新，終被絞焚於市政廣場。講道由速記者存錄，是講壇撼動共和國政治的極致案例，宗教改革前夜最悲壯的聲音。' },
          { title_zh: '冰島古講道書', title_orig: 'Íslensk hómilíubók', author: '佚名冰島編者', era: '約 1200', place: '冰島', language: '古諾斯語', intro: '冰島現存最古的書籍之一，輯五十餘篇古諾斯語講道與教理文字，供新植教會的司鐸宣講。它證明皈依僅二百年的冰島已建立母語講壇傳統，與挪威講道書同為北歐俗語宗教散文的源頭文獻。' },
          { title_zh: '論律法與恩典', title_orig: 'Слово о законе и благодати', author: '基輔都主教伊拉里翁', era: '約 1049', place: '基輔', language: '教會斯拉夫文', intro: '首位羅斯本土出身的基輔都主教伊拉里翁的節慶講道，以律法與恩典對比舊約與福音，進而頌讚受洗的羅斯民族「後來者居上」。全篇修辭承拜占庭而氣象自立，是東斯拉夫文學的開山名篇與民族神學的第一聲。' },
          { title_zh: '圖羅夫的西里爾講道集', title_orig: 'Слова Кирилла Туровского', author: '圖羅夫的西里爾', era: '約 1160–1182', place: '圖羅夫（今白俄羅斯）', language: '教會斯拉夫文', intro: '羅斯隱修主教西里爾以節慶講道馳名，復活節諸講以春回大地喻救恩更新，意象豐美，人稱「羅斯的金口」。其講章收入斯拉夫講道選集流傳數百年，是基輔羅斯講道藝術的最高成就。' },
          { title_zh: '塞拉皮翁講道集', title_orig: 'Слова Серапиона Владимирского', author: '弗拉基米爾的塞拉皮翁', era: '約 1274–1275', place: '弗拉基米爾', language: '教會斯拉夫文', intro: '蒙古蹂躪後出任弗拉基米爾主教的塞拉皮翁存世五篇講道，以震裂的悲愴追問「上帝為何以韃靼鞭笞我們」，召喚全民悔改。這批講章是羅斯淪亡世代的精神實錄，中世紀講道文學中罕見的國殤之聲。' },
          { title_zh: '奧赫裡德的克萊門特講道集', title_orig: 'Поучения на Климент Охридски', author: '奧赫裡德的克萊門特', era: '約 886–916', place: '奧赫裡德', language: '教會斯拉夫文', intro: '西里爾與美多德高弟克萊門特被逐出摩拉維亞後於奧赫裡德建校興學，為新受洗的保加利亞信眾撰寫節慶講道與聖徒頌讚數十篇，語淺情深。他是斯拉夫語講道文學的實際奠基者，七聖師傳統的核心人物。' },
          { title_zh: '教誨福音', title_orig: 'Учително евангелие', author: '普雷斯拉夫的康斯坦丁', era: '約 893–894', place: '普雷斯拉夫', language: '教會斯拉夫文', intro: '保加利亞黃金時代學者康斯坦丁按主日經課編譯的斯拉夫語講解福音集，附字母序詩與世界簡史，為斯拉夫語最早的系統講道書。它把拜占庭講章轉為新信民族的母語教材，是斯拉夫基督教文教工程的里程碑。' },
          { title_zh: '斯圖狄特要理講話集', title_orig: 'Catecheses (Theodorus Studita)', author: '斯圖狄奧斯的狄奧多爾', era: '約 795–826', place: '君士坦丁堡', language: '希臘文', intro: '斯圖狄奧斯修道院長狄奧多爾對修士的大小兩輯要理講話，短講平實如家常，論勞動、服從與弟兄之愛，至今仍為正教修道院例行誦讀。與其書信互補，這批講話是拜占庭修道講道傳統千年不輟的活水源頭。' },
          { title_zh: '佛提烏講道集', title_orig: 'Homiliae Photii', author: '君士坦丁堡宗主教佛提烏', era: '858–886', place: '君士坦丁堡', language: '希臘文', intro: '大學者宗主教佛提烏的講道集，最著名者為羅斯艦隊八六〇年突襲君士坦丁堡時的兩篇臨危講道，兼有聖母大殿落成讚辭。講章修辭宏麗而報導翔實，是拜占庭講壇藝術與帝都危機史的雙重見證。' },
          { title_zh: '利奧六世皇帝講道集', title_orig: 'Homiliae Leonis VI Sapientis', author: '皇帝利奧六世', era: '886–912', place: '君士坦丁堡', language: '希臘文', intro: '「智者」利奧六世親撰節慶講道數十篇，於宮廷與大殿親自宣讀，帝王執講道職為拜占庭政教合一的獨特風景。講章神學嚴謹兼具帝國修辭，是研究拜占庭皇帝神學角色與馬其頓文藝復興的一級文獻。' },
          { title_zh: '帕拉馬斯講道集', title_orig: 'Homiliae Gregorii Palamae', author: '帖撒羅尼迦的格列高利‧帕拉馬斯', era: '1347–1359', place: '帖撒羅尼迦', language: '希臘文', intro: '靜修論戰主將帕拉馬斯出任帖撒羅尼迦都主教後的六十三篇講道，把「非受造之光」的高峰神學化為對城市會眾的牧養言說，兼斥社會不義。這批講章證明奧秘神學與講壇實踐可為一體，是晚期拜占庭講道的巔峰。' },
          { title_zh: '摩西‧巴爾‧凱法講道集', title_orig: 'Homiliae Mosis bar Kepha', author: '摩西‧巴爾‧凱法', era: '約 863–903', place: '摩蘇爾一帶', language: '敘利亞文', intro: '敘利亞正教主教巴爾‧凱法著述宏富，其禮儀年講道集逐節闡發經課與聖事奧義，兼存其樂園論與禮儀註釋的神學體系。他是阿拔斯治下敘利亞教會學術復興的代表，講道集為東方講壇傳統的重要環節。' },
          { title_zh: '希爾德加德福音講解集', title_orig: 'Expositiones evangeliorum', author: '賓根的希爾德加德', era: '約 1150–1170', place: '賓根魯佩茨貝格', language: '拉丁文', intro: '希爾德加德為修女團體逐段講解主日福音的五十八篇講章，以靈視者的寓意讀法自成一格，並曾應邀赴科隆、特里爾向教士公開宣講——中世紀女性公開講道的絕例。本集是女性講道聲音在拉丁教會的罕見正式文本。' },
          { title_zh: '熱爾松法語講道集', title_orig: 'Sermons français de Jean Gerson', author: '讓‧熱爾松', era: '約 1389–1418', place: '巴黎', language: '中古法文', intro: '巴黎大學校長熱爾松以法語向宮廷與市民宣講的講道集，痛陳內戰之罪、為亡王祈安、教平信徒祈禱之道，開法語神學言說之先河。他主張以母語餵養「單純者」，這批講章是晚期中世紀法蘭西公共講壇的最強音。' },
          { title_zh: '北方講道集', title_orig: 'Northern Homily Cycle', author: '佚名（英格蘭北部奧斯定會圈）', era: '約 1315–1350', place: '英格蘭北部', language: '中古英語', intro: '以中古英語韻文按主日福音編排的講道詩集，每篇譯經、釋義、附例話，供司鐸誦講亦供平信徒自讀。全集傳抄本眾多並兩度擴編，是英格蘭俗語講道與通俗詩歌合流的大型紀念碑。' },
          { title_zh: '奧姆魯姆', title_orig: 'Ormulum', author: '奧姆', era: '約 1150–1180', place: '英格蘭東中部', language: '中古英語', intro: '奧斯定會律修士奧姆以自創嚴格音節體與獨特拼寫法寫成的英語福音講解詩，自序願「英吉利人以英語明白福音」。其拼寫系統精確標記音長，意外成為英語語音史的無價化石，講道文學與語言學雙重奇珍。' },
          { title_zh: '彼得‧達米安講道集', title_orig: 'Sermones Petri Damiani', author: '彼得‧達米安', era: '約 1040–1072', place: '豐泰阿韋拉納', language: '拉丁文', intro: '隱修改革家達米安存世講道七十餘篇，多為聖徒瞻禮與修院集會而作，以嚴峻的悔改呼召與熾烈的十字架默想著稱。講章與其書信互為表裡，同屬十一世紀改革運動的言語武庫，展示隱修講道由靜默中迸發的力度。' },
          { title_zh: '伊尼的圭裡克講道集', title_orig: 'Sermones Guerrici Igniacensis', author: '伊尼的圭裡克', era: '約 1138–1157', place: '伊尼熙篤會修道院', language: '拉丁文', intro: '聖伯爾納弟子、伊尼院長圭裡克的禮儀年講道五十餘篇，以「基督在我們裡面成形」為軸，靜穆深醇，與伯爾納、艾爾雷德並稱熙篤講道四家。其將臨期與聖母講道尤為傳誦，是熙篤靈修講壇的珠玉之作。' }
        
        
        ]
      },
      {
        key: 'ars-praedicandi',
        label: '講道術部',
        label_en: 'Arts of Preaching',
        desc: '中世紀講道方法論——自諾讓的吉貝爾至巴斯沃恩的「講道術」教本與講道者培育文獻。',
        works: [
          { title_zh: '諾讓的吉貝爾論講道之序', title_orig: 'Liber quo ordine sermo fieri debeat', author: '諾讓的吉貝爾', era: '約 1084', place: '諾讓修道院', language: '拉丁文', intro: '本篤會院長吉貝爾論講道預備的小書，主張講道者先修內心、按聽眾靈況剪裁道理，兼授四重釋經法。它是中世紀第一部自覺的講道方法論，開其後三百年「講道術」文類的先聲。' },
          { title_zh: '講道藝術大全', title_orig: 'Summa de arte praedicatoria', author: '裡爾的亞蘭', era: '約 1199', place: '熙篤', language: '拉丁文', intro: '「全能博士」亞蘭定義講道為「出於理性大道、源於權威泉源的公開明白教導」，按德目惡行分章示範講章骨架。本書為十二世紀末講道理論的集成，其定義為後世講道術著作反覆徵引的起點。' },
          { title_zh: '論講道者的培育', title_orig: 'De eruditione praedicatorum', author: '羅曼斯的洪貝爾', era: '約 1266–1277', place: '里昂', language: '拉丁文', intro: '道明會前總會長洪貝爾論講道職分的全書：講道者的資格、材料的蒐集、對各色聽眾的分寸，兼附範例。出自「講道兄弟會」掌門之手，本書是中世紀講道專業化的制度性總結，講道者職業倫理的元典。' },
          { title_zh: '講道形式', title_orig: 'Forma praedicandi', author: '羅伯特‧德‧巴斯沃恩', era: '1322', place: '牛津', language: '拉丁文', intro: '巴斯沃恩系統定式「主題講道法」的教本：取主題經文、立三分、引權威、聲韻收束，並品評英法講道風尚。本書為「大學式講道」結構的標準說明書，中世紀晚期講章千篇一律的三分骨架即其定型。' },
          { title_zh: '沃利斯講道編撰法', title_orig: 'De modo componendi sermones', author: '託馬斯‧沃利斯', era: '約 1336–1340', place: '牛津／亞維儂', language: '拉丁文', intro: '道明會士沃利斯的講道編撰教本，自選題、分段至臺風語速面面俱到，兼誡講道者勿炫學賣弄。作者曾因觸怒教宗論真福直觀而繫獄，其書實務精到，是十四世紀講道職人手藝的完整紀錄。' },
          { title_zh: '通言集', title_orig: 'Communiloquium sive summa collationum', author: '威爾斯的約翰', era: '約 1265–1270', place: '牛津／巴黎', language: '拉丁文', intro: '方濟會士威爾斯的約翰為講道與談道編纂的材料大全，按社會身分與德目分類輯錄古典與教父權威，儼然「與各色人等談道指南」。本書抄本逾百部，是託缽修會知識工程服務宣講的代表作。' }
        
        ]
      },
      {
        key: 'outer-mission',
        label: '對外宣教部',
        label_en: 'Mission to Non-Christians',
        desc: '托缽修會向異教徒、猶太人、穆斯林與東方諸族傳福音的方法手冊、護教論著與宣教實錄。',
        works: [
          { title_zh: '駁異教大全', title_orig: 'Summa contra Gentiles', author: '托馬斯‧阿奎那', era: '約 1259–1265', place: '義大利‧奧爾維耶托', language: '拉丁文', intro: '相傳應道明會宣教需要而作的護教巨著，旨在向不接受聖經權威的「外教人」——尤指穆斯林與猶太智者——僅憑理性論證基督信仰。全書四卷，前三卷依自然理性論上帝存在、本性與受造界的歸向，末卷方論唯憑啟示可知的奧理如三位一體、降生與聖事。結構嚴密，是中世紀理性護教與宣教神學的最高範本。', note: '一說為宣教手冊，學界對其用途有爭議', link: '/fathers' },
          { title_zh: '異教徒與三智者之書', title_orig: 'Llibre del gentil e dels tres savis', author: '拉蒙‧柳利', era: '約 1274–1276', place: '馬約卡', language: '加泰隆尼亞文', intro: '加泰隆尼亞傳教士柳利的對話體護教名著：一位陷於絕望的異教徒先後請教猶太、基督與穆斯林三位智者，三人各依柳利的「大術」（Ars）以理性樹本花葉之喻闡述己信。全書終卻不明寫異教徒最終皈依何教，留白以彰理性對話之誠。柳利畢生倡以語言學習與理性說服而非武力傳教，並推動設立東方語文學校，是中世紀宗教對話的先驅。', note: '', link: '' },
          { title_zh: '赴蒙古宣教行紀', title_orig: 'Itinerarium / Historia Mongalorum', author: '魯不魯乞的威廉、柏郎嘉賓的若望', era: '1245–1255', place: '蒙古帝國‧哈剌和林', language: '拉丁文', intro: '方濟會士奉教宗與法王之命東赴蒙古宮廷的宣教與外交實錄。柏郎嘉賓的若望（1245–47）首抵貴由汗即位大典，魯不魯乞的威廉（1253–55）則深入蒙哥汗廷，並在哈剌和林與聶斯脫里派、佛教徒、穆斯林當面辯道。二人記下沿途地理、風俗與宗教實況，既是宣教文獻，也是歐洲認識內亞與遠東的早期一手報導。', note: '為兩部行紀之合錄', link: '' },
          { title_zh: '向穆斯林證三位一體傳教指南', title_orig: 'Pugio Fidei / De rationibus fidei', author: '雷蒙‧馬蒂尼、托馬斯‧阿奎那', era: '十三世紀中後期', place: '伊比利亞‧北非', language: '拉丁文（雜希伯來、阿拉伯文）', intro: '收伊比利亞道明會為向穆斯林與猶太人傳道而編的論辯手冊。馬蒂尼的「信仰之匕首」廣徵塔木德、古蘭與阿拉伯哲人原文，逐條駁斥並引以證基督；阿奎那的「論信仰之理」則應安提阿傳教士之請，教人如何向否認三位一體與降生的穆斯林作理性辯護而不訴諸聖經權威。二者反映托缽會「以彼之典攻彼之說」的宣教策略。', note: '為同類傳教手冊之合錄', link: '/fathers' },
          { title_zh: '十字軍講道論', title_orig: 'De praedicatione sanctae crucis', author: '羅曼斯的洪貝爾', era: '約 1266–1268', place: '里昂', language: '拉丁文', intro: '道明會前總會長洪貝爾為十字軍招募講道編寫的專門手冊，備妥講題、經文、駁詞與應對聽眾冷場之法。它是中世紀「動員講道」唯一的系統教範，兼露拉丁教會對聖戰宣傳的自我技術化，十字軍研究的必讀文獻。' },
          { title_zh: '夏託魯十字軍講道集', title_orig: 'Sermones de cruce (Odo de Castro Radulphi)', author: '夏託魯的歐德', era: '約 1245–1270', place: '巴黎／教廷', language: '拉丁文', intro: '巴黎校長出身的樞機歐德隨路易九世東徵，其十字軍講道存世數十篇，向騎士、水手與悔罪者分別勸誓出征。這批講章是十字軍講道實務現存最完整的樣本，重建聖戰宣傳現場的第一手材料。' },
          { title_zh: '論撒拉森人的狀況', title_orig: 'De statu Saracenorum', author: '特里波利的威廉', era: '約 1273', place: '阿卡', language: '拉丁文', intro: '道明會士威廉久居聖地，本書平實記述伊斯蘭的信仰與國勢，斷言穆斯林近於基督教真理、宜以言語而非刀劍歸化之，自稱曾為千餘人授洗。在十字軍狂熱中主張和平宣教，是十三世紀對伊斯蘭最不敵意的拉丁文本。' },
          { title_zh: '巴黎塔木德大辯論記錄', title_orig: 'Disputatio Parisiensis (1240)', author: '尼古拉‧多寧與巴黎審查團', era: '1240–1248', place: '巴黎', language: '拉丁文／希伯來文', intro: '改宗者多寧指控塔木德褻瀆，法王路易九世召集辯論，猶太方由拉比耶希爾應訊，終致塔木德焚毀。拉丁控詞與希伯來語記錄兩造並存，是中世紀基督教世界審判他教典籍的第一大案，猶太-基督關係史的轉捩文獻。' },
          { title_zh: '巴塞隆納大辯論記錄', title_orig: 'Disputatio Barcinonensis (1263)', author: '保羅‧克里斯蒂亞尼與亞拉岡王廷', era: '1263', place: '巴塞隆納', language: '拉丁文／希伯來文', intro: '改宗道明會士保羅與納曼尼德御前四日辯論彌賽亞已臨與否，拉丁官方記錄與納曼尼德的希伯來自述並傳，立場相反如羅生門。此辯是中世紀猶太-基督辯道最著名的一役，兩造文本對觀為思想史的經典功課。' },
          { title_zh: '託爾託薩大辯論記錄', title_orig: 'Disputatio Dertosensis (1413–1414)', author: '傑羅姆‧德‧聖菲與亞拉岡教廷', era: '1413–1414', place: '託爾託薩', language: '拉丁文', intro: '亞維儂教宗本篤十三世主持、改宗醫師聖菲主辯的馬拉松辯道，歷六十九場逾年餘，亞拉岡各地拉比被迫與會。會後猶太社群大批受洗，是中世紀最大規模也最具壓迫性的宗教辯論，伊比利猶太史的黑色里程碑。' },
          { title_zh: '尤洛吉烏斯護教勸殉書', title_orig: 'Documentum martyriale / Liber apologeticus martyrum', author: '哥多華的尤洛吉烏斯', era: '851–859', place: '哥多華', language: '拉丁文', intro: '哥多華司鐸尤洛吉烏斯為自願殉道運動辯護並勸勉繫獄女信徒的著作，記錄基督徒在伊斯蘭治下公開宣信取死的浪潮，自身終亦殉道。這批文本是安達魯斯教會精神抵抗的核心文獻，殉道神學在中世紀的激烈重演。' },
          { title_zh: '光明錄', title_orig: 'Indiculus luminosus', author: '保羅‧阿爾瓦魯斯', era: '854', place: '哥多華', language: '拉丁文', intro: '哥多華平信徒學者阿爾瓦魯斯為殉道運動辯護的檄文，痛心疾呼基督徒青年競習阿拉伯文而忘拉丁經典。書中對穆斯林社會的描述與那句「千人中難覓一人能以拉丁文寫信」的哀嘆，是文化同化研究最常徵引的中世紀文本。' },
          { title_zh: '科茲馬駁鮑格米勒講道', title_orig: 'Беседа против богомилите', author: '科茲馬長老', era: '約 969–972', place: '保加利亞', language: '教會斯拉夫文', intro: '保加利亞司鐸科茲馬駁斥新興鮑格米勒二元論異端的長篇講道，逐條批其棄聖禮、拒舊約、詆教會之說，兼責教會自身積弊給異端可乘之機。本篇是斯拉夫語最早的原創駁異端文獻，鮑格米勒運動研究的第一史料。' },
          { title_zh: '阿布庫拉宮廷辯道錄', title_orig: 'Mayāmir Theodori Abu Qurrah', author: '狄奧多爾‧阿布庫拉', era: '約 795–829', place: '哈蘭／巴格達', language: '阿拉伯文／敘利亞文', intro: '哈蘭主教阿布庫拉為最早以阿拉伯文著述的基督教神學家，傳世辯道篇章記其在哈里發馬蒙御前與穆斯林學者論道，兼撰論聖像與自由意志諸篇。他把教父神學譯入伊斯蘭的語言世界，是阿拉伯基督教護教學的開山。' },
          { title_zh: '以利亞與維齊爾會談錄', title_orig: 'Kitāb al-Majālis', author: '尼西比斯的以利亞', era: '1026–1027', place: '尼西比斯', language: '阿拉伯文', intro: '東方教會都主教以利亞與穆斯林維齊爾七次會談的記錄，論三一、道成肉身與基督徒的阿拉伯文化貢獻，語氣互敬如學社。附致維齊爾書信，本書是伊斯蘭治下基督徒以理性與友誼辯道的最溫和典範。' },
          { title_zh: '曼努埃爾二世與波斯人辯道錄', title_orig: 'Dialoge mit einem Perser', author: '皇帝曼努埃爾二世‧帕列奧洛戈斯', era: '約 1391', place: '安卡拉冬營', language: '希臘文', intro: '拜占庭皇帝曼努埃爾二世隨鄂圖曼軍出征安納託利亞時，與一位波斯穆斯林學者的廿六場辯道自錄，論先知、律法與聖戰。六百年後教宗本篤十六世雷根斯堡演講引其一語而震動世界，本書自身則是文明對話的深沉標本。' },
          { title_zh: '匈牙利的格奧爾格土耳其風俗論', title_orig: 'Tractatus de moribus, condictionibus et nequicia Turcorum', author: '匈牙利的格奧爾格', era: '1481', place: '羅馬', language: '拉丁文', intro: '少年被擄為奴、居鄂圖曼二十年的格奧爾格獲釋後寫成的見聞論，既詳述土耳其人的紀律虔敬令歐洲自愧，又警告其信仰的誘惑力。本書刊行極廣、路德親為德譯本作序，是歐洲認識鄂圖曼的第一手經典。' },
          { title_zh: '塞戈維亞的約翰古蘭經對譯計畫文獻', title_orig: 'Iohannes de Segovia: praefatio in translationem Alcorani', author: '塞戈維亞的約翰', era: '1454–1458', place: '薩伏依艾通修道院', language: '拉丁文', intro: '君士坦丁堡陷落後，前巴塞爾會議神學家塞戈維亞的約翰延聘穆斯林法學家同譯古蘭經為卡斯提爾語與拉丁語，遺序言與方法論書信傳世，力主以「和平與講理之道」代替十字軍。其三語對照構想是宗教對話史的先知性文獻。' },
          { title_zh: '論收復聖地', title_orig: 'Liber recuperationis Terrae Sanctae', author: '帕多瓦的菲登齊奧', era: '約 1290–1291', place: '阿卡／帕多瓦', language: '拉丁文', intro: '方濟會聖地省會長菲登齊奧應教宗之請撰寫的收復聖地方略，綜論伊斯蘭興起、軍事地理與海陸進兵之策，成書於阿卡陷落前夕。本書是「收復計畫書」文類的代表，宣教與地緣戰略在中世紀末的交纏標本。' }
        
        ]
      },
      {
        key: 'exegesis',
        label: '中世紀解經部',
        label_en: 'Medieval Latin Exegesis',
        desc: '中世紀拉丁聖經注釋的兩大骨幹：標準頁邊行間注釋與依字面義系統重注的後世通注。',
        works: [
          { title_zh: '聖經通注', title_orig: 'Postilla Litteralis super totam Bibliam', author: '尼古拉‧德‧利拉', era: '約 1322–1331', place: '巴黎', language: '拉丁文', intro: '方濟會學者利拉遍注全本聖經的逐卷注釋，特重「字面義」（sensus litteralis），主張寓意解必須建基於字面方為穩固。他通曉希伯來文，大量參酌拉希等猶太注釋家以求經文本意，開拉丁解經兼採猶太傳統之先河。此書於中世紀晚期流傳極廣，據傳對路德的釋經影響甚深，後世遂有「若無利拉執筆，路德不會起舞」之諺。', note: '', link: '' },
          { title_zh: '標準註釋聖經', title_orig: 'Glossa Ordinaria', author: '拉昂的安瑟莫學派（中世紀經院群編）', era: '十二世紀成形', place: '法蘭西‧拉昂', language: '拉丁文', intro: '中世紀大學最權威的聖經注釋彙編：每頁中央排聖經正文，行間（interlinear）與頁邊（marginal）密布輯自教父與前代注釋家的注語，使讀者一覽即得歷代權威之解。主要由拉昂的安瑟莫一脈於十二世紀整理成形，遂成神學課堂的標準教本與經院辯論的共同底本。其體例本身即代表中世紀「以傳統累積讀經」的釋經精神。', note: '為學派群編，非一人之作', link: '' },
          { title_zh: '約翰福音序講', title_orig: 'Homilia super prologum Iohannis (Vox spiritualis aquilae)', author: '約翰‧斯科特斯‧愛留根納', era: '約 870', place: '西法蘭克宮廷', language: '拉丁文', intro: '愛留根納講解約翰福音序言的名篇「屬靈之鷹的鳴聲」，以新柏拉圖的高翔筆勢闡述道成肉身，為加洛林釋經最深邃的一頁。此講長期託名金口若望流傳，其真貌重光後被譽為中世紀最美的講章之一。' },
          { title_zh: '塞杜利烏斯保羅書信集註', title_orig: 'Collectaneum in epistolas Pauli', author: '塞杜利烏斯‧斯科圖斯', era: '約 840–860', place: '列日', language: '拉丁文', intro: '愛爾蘭流寓學者塞杜利烏斯輯教父諸說註解保羅書信的集註，兼採佩拉糾舊注而加以正統化剪裁，展示加洛林學者處理疑難遺產的手腕。他兼為宮廷詩人與希臘學先驅，本書是愛爾蘭學術移植歐陸的代表成果。' },
          { title_zh: '弗洛魯斯保羅書信奧古斯丁輯注', title_orig: 'Expositio in epistolas Pauli ex operibus Augustini', author: '里昂的弗洛魯斯', era: '約 850–860', place: '里昂', language: '拉丁文', intro: '里昂執事弗洛魯斯自奧古斯丁全部著作中輯出保羅書信相關段落，按經文順序織成巨型輯注，考訂精嚴近乎現代輯佚學。本書是加洛林「以教父注教父」方法的極致，中世紀奧古斯丁接受史的樞紐文獻。' },
          { title_zh: '雷米吉烏斯詩篇注', title_orig: 'Enarrationes in Psalmos (Remigius Autissiodorensis)', author: '奧塞爾的雷米吉烏斯', era: '約 880–908', place: '奧塞爾／蘭斯／巴黎', language: '拉丁文', intro: '奧塞爾學派殿軍雷米吉烏斯的詩篇全注，融文法分析與屬靈釋義，供學校講授之用，流傳極廣。他先後執教蘭斯與巴黎，被視為巴黎學校傳統的遠祖，本注是加洛林釋經學校化的收官之作。' },
          { title_zh: '科隆的布魯諾詩篇注', title_orig: 'Expositio in Psalmos (Bruno Carthusianorum)', author: '科隆的布魯諾', era: '約 1080–1090', place: '蘭斯／大沙特勒斯', language: '拉丁文', intro: '加爾都西會創始人布魯諾任蘭斯學監時期的詩篇注，逐節簡釋文義而歸於基督奧義，文風洗鍊如其隱修理想。本注流傳既廣，亦見證十一世紀主教學校釋經與新興隱修運動的人事相承。' },
          { title_zh: '魯珀特約翰福音注', title_orig: 'Commentaria in evangelium Iohannis', author: '多伊茨的魯珀特', era: '約 1115–1116', place: '列日／多伊茨', language: '拉丁文', intro: '本篤會神學家魯珀特的約翰福音大注，以救恩史的宏觀敘事貫穿全書，篇幅與想像力俱冠當代。他是十二世紀「修道釋經」對抗新興經院辯證的主將，本注展示默觀傳統釋經的最後盛放。' },
          { title_zh: '研讀論', title_orig: 'Didascalicon de studio legendi', author: '聖維克託的休', era: '約 1127', place: '巴黎聖維克託修道院', language: '拉丁文', intro: '聖維克託的休為初學者規劃全部學問的讀書法：七藝為基、機械之藝並列、終歸聖經三重義的研讀。本書是中世紀最重要的教育與釋經方法論，「先識字面、後求奧義」的原則重整了十二世紀的讀經文化。' },
          { title_zh: '安德魯舊約字面義注', title_orig: 'Expositiones historicae in Vetus Testamentum', author: '聖維克託的安德魯', era: '約 1140–1175', place: '巴黎／威格莫爾', language: '拉丁文', intro: '聖維克託的安德魯專注舊約字面義，屢訪猶太學者請教希伯來原文與拉比釋義，先知書注尤見大膽。他被史家譽為「十二世紀的耶柔米」，其字面義綱領直接哺育後世的利拉與宗教改革釋經。' },
          { title_zh: '經院史', title_orig: 'Historia scholastica', author: '彼得‧科梅斯托', era: '約 1169–1173', place: '巴黎', language: '拉丁文', intro: '「吞書者」科梅斯托把全部聖經敘事連綴為一部通貫的聖史教本，補以史地掌故與猶太傳說，成為大學與修院的聖經入門必讀。各俗語「歷史聖經」皆其苗裔，抄本數以千計，是中世紀讀經文化最成功的教科書。' },
          { title_zh: '言詞簡編', title_orig: 'Verbum abbreviatum', author: '彼得‧尚託', era: '約 1191–1192', place: '巴黎', language: '拉丁文', intro: '巴黎聖母院總鐸尚託的道德釋經大全，以聖經權威裁斷聖職買賣、司法酷刑與奢華排場，倡「讀經、辯難、講道」三部曲的神學實踐。本書是巴黎道德學派的綱領，把釋經之學直接推向社會批判。' },
          { title_zh: '朗頓聖經講疏集', title_orig: 'Commentarii in Scripturam (Stephanus Langton)', author: '斯蒂芬‧朗頓', era: '約 1180–1206', place: '巴黎', language: '拉丁文', intro: '朗頓在巴黎講授聖經幾乎逐捲成疏，兼顧字面與道德義，聽錄稿傳世極多，其章節劃分即講學副產品。這批講疏呈現大學釋經課堂的原生態，是「聖經博士」職業成形期的核心文獻。' },
          { title_zh: '聖謝爾的休聖經後注', title_orig: 'Postillae in totam Bibliam (Hugo de Sancto Charo)', author: '聖謝爾的休', era: '約 1230–1236', place: '巴黎聖雅各修道院', language: '拉丁文', intro: '道明會團隊在聖謝爾的休主持下完成的全本聖經後注，四重義並陳而檢索便利，與其經文彙編同出一坊。本書為十三世紀大學與修會的標準聖經參考，印刷時代仍再版不輟，集體釋經工程的典範。' },
          { title_zh: '阿奎那約伯記釋義', title_orig: 'Expositio super Iob ad litteram', author: '託馬斯‧阿奎那', era: '1261–1265', place: '奧爾維耶託', language: '拉丁文', intro: '阿奎那按字面義逐節講解約伯記，把全書讀作一場關於天意的哲學辯論，苦難問題由此獲得經院式的澄明。本注展示「天使博士」作為聖經教授的日常工作，字面義釋經與神學思辨合一的傑作。' },
          { title_zh: '聖瑪利亞的保羅利拉補注', title_orig: 'Additiones ad Postillam Nicolai de Lyra', author: '聖瑪利亞的保羅（布爾戈斯的保羅）', era: '約 1429–1431', place: '布爾戈斯', language: '拉丁文', intro: '猶太拉比出身、皈依後官至布爾戈斯主教的保羅為利拉《文字後注》所作千餘條補注，以其希伯來學養與拉比文獻修正前人。補注隨利拉注合刊流傳全歐，是中世紀猶太-基督釋經學交融最深的文本。' },
          { title_zh: '託斯塔多聖經釋義集', title_orig: 'Commentaria in Sacram Scripturam (Tostatus)', author: '阿方索‧託斯塔多', era: '約 1436–1455', place: '薩拉曼卡／亞維拉', language: '拉丁文', intro: '薩拉曼卡神學家、亞維拉主教託斯塔多的聖經釋義卷帙浩繁，刊本達廿餘巨冊，西班牙諺語至今以「寫得比託斯塔多還多」形容多產。其注博採字面義與史地考證，是中世紀晚期伊比利釋經學術的百科式頂峰。' },
          { title_zh: '加爾特會士丹尼斯聖經注', title_orig: 'Enarrationes in Sacram Scripturam (Dionysius Cartusianus)', author: '加爾特會士丹尼斯', era: '約 1434–1457', place: '魯爾蒙德加爾都西修道院', language: '拉丁文', intro: '「狂喜博士」丹尼斯在斗室中注畢全本聖經，兼撰神學靈修著作近二百種，全集印行四十二巨冊。其注總攬教父與經院諸說而歸於默觀，被稱為「最後一位經院大全式作者」，中世紀釋經傳統的閉幕總卷。' },
          { title_zh: '狄奧菲拉克特四福音注', title_orig: 'Hermeneia eis ta tessara euangelia', author: '奧赫裡德的狄奧菲拉克特', era: '約 1090–1108', place: '奧赫裡德', language: '希臘文', intro: '狄奧菲拉克特承金口若望釋經傳統寫成的四福音簡注，文義清通，拜占庭與斯拉夫世界奉為標準福音注，阿奎那《黃金鎖鏈》與伊拉斯謨新約注皆大量取資。本注是教父釋經中世紀傳承的最大中繼站。' },
          { title_zh: '齊加貝努斯詩篇注', title_orig: 'Commentarius in Psalterium (Euthymius Zigabenus)', author: '歐帝米烏斯‧齊加貝努斯', era: '約 1100–1120', place: '君士坦丁堡', language: '希臘文', intro: '科穆寧宮廷學僧齊加貝努斯的詩篇注，精擇金口若望以降諸家而斷以己意，條理明淨，拜占庭後期傳抄極盛並早經拉丁譯介。與其《教義甲冑》互補，本注代表科穆寧文藝復興的釋經水準。' },
          { title_zh: '阿雷塔斯啟示錄注', title_orig: 'Commentarius in Apocalypsim (Arethas)', author: '凱撒利亞的阿雷塔斯', era: '約 900–913', place: '凱撒利亞（卡帕多細亞）', language: '希臘文', intro: '拜占庭大藏書家、凱撒利亞都主教阿雷塔斯增訂前人而成的啟示錄注，為希臘教會少數完整的啟示錄釋義傳統立下中世紀定本。其人主持古籍轉抄工程澤及後世，本注兼具釋經史與文獻傳承史的雙重地位。' },
          { title_zh: '伊修達德聖經注釋', title_orig: 'Commentaries of Isho\'dad of Merv', author: '梅爾夫的伊修達德', era: '約 850', place: '哈達塔（美索不達米亞）', language: '敘利亞文', intro: '東方教會主教伊修達德的新舊約全注，總匯狄奧多爾以降的安提阿學派釋經並存錄諸家異說，為東敘利亞釋經傳統的集大成。其注保存大量已佚前人注釋，是研究敘利亞語釋經史無可替代的寶庫。' },
          { title_zh: '巴爾‧科尼釋疑注', title_orig: 'Scholion (Theodorus bar Koni)', author: '狄奧多爾‧巴爾‧科尼', era: '792', place: '卡什卡爾（美索不達米亞）', language: '敘利亞文', intro: '東方教會學者巴爾‧科尼以問答體註解全本聖經的《釋疑》，末卷附駁異端與伊斯蘭的辯道，兼存摩尼教與諸諾斯底教派的珍貴記述。本書是阿拔斯初期東敘利亞學校神學的總覽，宗教史研究的意外富礦。' },
          { title_zh: '奧秘倉庫', title_orig: 'Awṣar Rāzē (Storehouse of Mysteries)', author: '巴爾‧赫布拉烏斯', era: '約 1277–1286', place: '馬拉蓋', language: '敘利亞文', intro: '敘利亞正教大公巴爾‧赫布拉烏斯的全本聖經注，兼採敘利亞諸本異文與希臘本對勘，並融文法、瑪索拉與神學於一爐。成書於伊利汗國治下的馬拉蓋天文臺之城，是敘利亞釋經與文本學的最後高峰。' },
          { title_zh: '巴爾‧薩利比福音注', title_orig: 'Commentary on the Gospels (Dionysius bar Salibi)', author: '迪奧尼修斯‧巴爾‧薩利比', era: '約 1150–1171', place: '阿米達（迪亞巴克爾）', language: '敘利亞文', intro: '敘利亞正教主教巴爾‧薩利比的四福音大注，分「物質義」與「屬靈義」雙軌並陳，總匯以法蓮以降的敘利亞釋經遺產。他著述遍及聖經、禮儀與駁論，本注是十二世紀敘利亞文藝復興的釋經代表作。' },
          { title_zh: '施諾爾哈利馬太福音注', title_orig: 'Commentary on Matthew (Nerses Shnorhali)', author: '內爾謝斯四世‧施諾爾哈利', era: '約 1170–1173', place: '赫羅姆克拉', language: '亞美尼亞文', intro: '亞美尼亞大公「恩典者」內爾謝斯晚年注馬太福音，僅成前五章而由後人續竟，註文詩情與神學交融如其聖詩。此注開基利家時代亞美尼亞釋經復興之端，是民族教會釋經傳統的珍貴環節。' },
          { title_zh: '瓦爾丹聖經釋義', title_orig: 'Biblical Commentaries of Vardan Areveltsi', author: '瓦爾丹‧阿雷維爾齊', era: '約 1240–1271', place: '大亞美尼亞', language: '亞美尼亞文', intro: '亞美尼亞史家瓦爾丹兼治釋經，撰五經與詩篇等注釋並編《釋疑問答》，以母語普及聖經知識。他親歷蒙古統治並曾謁見旭烈兀，其釋經著作見證亞美尼亞教會在蒙古時代堅持文教的韌性。' }
        
        ]
      }
    ]
  },
  wai: {
    summary: '外藏錄基督宗教以外、中世紀兩大一神傳統的聖典注釋：伊斯蘭的古蘭經注（tafsir）與猶太教的聖經、塔木德註釋，二者皆於此時期臻於高度體系化，與拉丁解經遙相呼應。',
    divisions: [
      {
        key: 'islamic-tafsir',
        label: '伊斯蘭解經部',
        label_en: 'Islamic Qur\'anic Exegesis',
        desc: '中世紀伊斯蘭古蘭經注的兩大典範：以傳述匯纂見長的歷史派與以語言修辭析理見長的理性派。',
        works: [
          { title_zh: '古蘭經注大全', title_orig: 'Jāmiʿ al-bayān ʿan taʾwīl āy al-Qurʾān (Tafsīr al-Ṭabarī)', author: '塔巴里', era: '約 883–923', place: '巴格達', language: '阿拉伯文', intro: '波斯裔學者塔巴里逐節注釋整本古蘭經的鉅著，是現存最早、最完整的傳述派經注典範。他每解一節，必廣引先知聖訓、門弟子與再傳者的解說，並標明傳述系譜（isnād），再加以權衡取捨。其方法兼顧語言、歷史與律法，網羅前代幾乎全部解經傳統，遂成後世一切古蘭經注必先稽考的源頭活水，地位之於伊斯蘭釋經學猶如標準註釋之於拉丁世界。', note: '', link: '' },
          { title_zh: '古蘭經明義', title_orig: 'al-Kashshāf ʿan ḥaqāʾiq al-tanzīl', author: '查麥赫沙里', era: '約 1134', place: '花剌子模', language: '阿拉伯文', intro: '花剌子模學者查麥赫沙里的古蘭經注，以精湛的阿拉伯語言學與修辭分析著稱，專揭經文遣詞造句之妙與其「不可摹擬」（iʿjāz）的雄辯之美。作者持穆爾太齊賴派理性神學立場，注中時見其義理發揮，雖屢遭正統派批評，後世遜尼學者仍因其語文造詣之高而不能不讀，並編訂校刪本以「去其義理、存其文辭」，足見其在解經學上的份量。', note: '作者屬穆爾太齊賴理性派', link: '' }
        ]
      },
      {
        key: 'jewish-exegesis',
        label: '猶太解經部',
        label_en: 'Jewish Biblical Exegesis',
        desc: '中世紀猶太聖經與塔木德註釋的兩座高峰：北法的逐字平易注與西班牙的文法考據注。',
        works: [
          { title_zh: '托拉與塔木德註釋', title_orig: 'Perush Rashi ʿal ha-Torah ve-ha-Talmud', author: '拉希（所羅門‧本‧以撒）', era: '約 1075–1105', place: '法蘭西‧特魯瓦', language: '希伯來文（雜古法語）', intro: '北法學者拉希為整部托拉、塔納赫多卷及幾乎全部巴比倫塔木德所作的逐句註釋，是猶太傳統中最受尊崇、流傳最廣的注本。其文簡明扼要，務求疏通字面（peshat）與必要的拉比傳統（midrash），遇難解之希伯來語常以當時法語對音（laʿaz）標注。後世印行希伯來聖經與塔木德幾乎必附拉希注於旁，連基督教解經家利拉亦深受其惠。', note: '', link: '' },
          { title_zh: '聖經註釋', title_orig: 'Perushei ha-Miqra', author: '亞伯拉罕‧伊本‧以斯拉', era: '十二世紀', place: '西班牙‧義大利‧法蘭西（遊歷）', language: '希伯來文', intro: '西班牙猶太學者伊本‧以斯拉的聖經註釋，以嚴謹的希伯來文法、詞源與天文曆算考據見長，力主依字面與語言實證解經，對寓意附會與後加傳說每每存疑甚至婉諷。他周遊基督教歐洲各地，把西班牙黃金時代的語文學成果傳入北方猶太社群。其注以理性審慎著稱，後世學者讀拉希之餘必參伊本‧以斯拉，以補其文法之精。', note: '', link: '' }
        ]
      }
    ]
  }
},
    {
  key: 'leishu',
  name: '類書藏',
  name_en: 'Canon of Encyclopaedia & Liberal Arts',
  glyph: '類',
  genres: '類書‧百科‧七藝‧自然',
  summary: '類書藏收中世紀（約 800–1500）宗教藝術以外的知識彙編：上溯古典、總攬萬有的百科全書，觀察自然界動植礦與天體的科學論著，大學課程奠基的七藝與邏輯教本，以及伊斯蘭世界的科學百科與猶太傳統的祕學典籍。此藏體例近於漢語藏經的「類書」，務求把當時可知的天地人之學分門別類，匯為一爐。',
  zheng: {
    summary: '正藏錄拉丁基督教世界的三類知識彙編：總攬萬有的百科全書部，觀測自然與天體的自然科學部，及大學文科基礎的七藝與邏輯部。',
    divisions: [
      {
        key: 'encyclopaedia',
        label: '百科全書部',
        label_en: 'Encyclopaedias',
        desc: '總攬天地人萬有、分門別類的中世紀拉丁百科全書傳統，上承古典晚期而集其大成。',
        works: [
          { title_zh: '大鏡', title_orig: 'Speculum Maius', author: '博韋的文森', era: '約 1244–1259', place: '法蘭西‧博韋', language: '拉丁文', intro: '道明會士文森奉法王路易九世之助編成的中世紀最大百科全書，分「自然之鏡」「教理之鏡」「歷史之鏡」三部（後人補入「道德之鏡」成四部），逾八十卷、近萬章，幾乎囊括當時拉丁世界可知的一切學問。它以摘錄前代權威原文為法，從上帝創世、自然萬物、人類技藝一路寫到當代史事，是一座以引文砌成的知識總庫，中世紀晚期讀書人取材的淵藪。', note: '「道德之鏡」一部為後人增補', link: '' },
          { title_zh: '物性論', title_orig: 'De proprietatibus rerum', author: '英格蘭的巴多羅買', era: '約 1240', place: '巴黎‧馬德堡', language: '拉丁文', intro: '方濟會士巴多羅買所編、共十九卷的自然百科，從上帝與天使論起，依序及於靈魂、人體、疾病、天體、四元素、鳥獸、草木、寶石、度量與聲色等萬物之性。它把神學、醫學與自然知識通俗匯整，文字平易而條理井然，中世紀晚期被譯成法、英、西等多種俗語，流傳極廣，成為平信徒與學生認識自然世界最常用的入門讀本之一。', note: '', link: '' },
          { title_zh: '語源學續傳', title_orig: 'Etymologiae (traditio medievalis)', author: '塞維亞的依西多祿', era: '約 625–636 原著；中世紀廣傳', place: '西班牙‧塞維亞', language: '拉丁文', intro: '西哥德主教依西多祿總結古典晚期一切學問的二十卷百科，借「語源」（etymologia）為線索，從七藝、醫學、法律、神學一路寫到地理、礦物、農事、戰具與日用器物。雖成於七世紀，卻在整個中世紀被當作百科知識的標準藍本，抄本數以千計，後世幾乎所有百科全書皆以之為骨架而續寫增補，故列為類書傳統之祖。', note: '雖屬古典晚期，因中世紀奉為百科之祖而收入', link: '' },
              { title_zh: '蜜蜂之書', title_orig: 'Ktābā d-Dabbōrītā (The Book of the Bee)', author: '巴士拉的所羅門（Solomon of Basra）', era: '約 13 世紀', place: '巴士拉（東方教會）', language: '古典敘利亞文', intro: '東方教會主教巴士拉的所羅門編纂的神學百科，採問答與敘事體，自創造、墮落、救恩史貫述至末世與來生，並廣納聖經外傳、聖徒名錄與民間傳說。作者自喻如蜜蜂採集群芳釀蜜，匯整前代敘利亞傳統菁華成一冊，是了解中世紀東方教會宇宙觀、救恩史架構與民間信仰的便覽式文獻。' },
          { title_zh: '萬物論', title_orig: 'De rerum naturis (De universo)', author: '拉巴努斯‧毛魯斯', era: '約 842–846', place: '富爾達', language: '拉丁文', intro: '「日耳曼之師」拉巴努斯以依西多祿《語源學》為底本重編的廿二卷百科，逐項增補聖經寓意解釋，使萬物知識皆指向救恩奧義。它是加洛林時代最大的知識總匯，中世紀修道院圖書館的基本藏書，代表「百科即釋經」的早期類書型態。' },
          { title_zh: '自然萬物論', title_orig: 'Liber de natura rerum', author: '康蒂姆普雷的託馬斯', era: '約 1237–1244', place: '布拉班特', language: '拉丁文', intro: '道明會士託馬斯歷時十五年編成的自然百科，凡人體、獸禽魚蟲、草木寶石、天象無所不收，屢引親身見聞。本書為大阿爾伯特《論動物》的重要材料源，亦經德語改編流傳，是十三世紀「百科世紀」的代表作之一。' },
          { title_zh: '萬物本性論', title_orig: 'De naturis rerum', author: '亞歷山大‧內卡姆', era: '約 1190–1204', place: '倫敦／西倫塞斯特', language: '拉丁文', intro: '英格蘭學者內卡姆的自然百科兼道德省思，於歐洲文獻中最早記載指南針用於航海，兼述十二世紀新入西方的科學新知。內卡姆為獅心王理查的乳兄弟、牛津早期教師，本書見證經院興起前夜英格蘭的博物之學。' },
          { title_zh: '世界圖像', title_orig: 'Imago mundi', author: '奧頓的霍諾留', era: '約 1110–1139', place: '雷根斯堡一帶', language: '拉丁文', intro: '霍諾留以問答簡明體例綜述宇宙、地理、時間與世界史的小百科，因便於記誦而風行全歐，抄本數以百計並譯成多種俗語。它把奧古斯丁式的世界觀濃縮為教學手冊，是十二世紀知識普及化的代表文本。' },
          { title_zh: '喜樂之園', title_orig: 'Hortus deliciarum', author: '蘭茨貝格的赫拉德', era: '1167–1185', place: '亞爾薩斯霍恩堡女修道院', language: '拉丁文', intro: '霍恩堡女院長赫拉德為修女教育編纂的圖文百科，三百餘幅細密畫貫穿哲學七藝、救恩史與德行惡行之戰，為史上第一部確知由女性編纂的百科全書。原本毀於一八七〇年史特拉斯堡大火，賴摹本傳世，是女性知識傳承的豐碑。' },
          { title_zh: '百花之書', title_orig: 'Liber floridus', author: '聖奧梅爾的蘭伯特', era: '約 1090–1120', place: '聖奧梅爾', language: '拉丁文', intro: '法蘭德斯教士蘭伯特自輯的圖解百科，雜纂世界史、地理、天文、聖經與奇獸異聞，親筆原稿今存根特大學。其編排隨興如花圃採擷，故名「百花」，保存多幅重要的中世紀世界地圖與末世圖像，是個人式類書的奇品。' },
          { title_zh: '珍寶之書', title_orig: 'Li livres dou tresor', author: '布魯內託‧拉蒂尼', era: '約 1260–1266', place: '巴黎（佛羅倫斯人流亡中）', language: '古法文', intro: '但丁之師、佛羅倫斯公證人拉蒂尼流亡法國時以法語編成的百科，分博物、倫理、修辭政治三部，自詡為市民治事的「珍寶」。以俗語寫百科並以政治學收尾，展現義大利城邦公民文化的知識需求，流傳抄本近百部。' },
          { title_zh: '世界之像', title_orig: 'L\'image du monde', author: '戈蘇安‧德‧梅斯', era: '約 1245', place: '梅斯', language: '古法文', intro: '以法語韻文寫成的通俗宇宙誌，述天地形狀、四元素與諸邦風土，明言大地為圓球並以插圖示意。本書後有散文改寫本並經卡克斯頓譯成英語印行，是中世紀俗語科普最成功的作品之一。' },
          { title_zh: '自然之書', title_orig: 'Buch der Natur', author: '康拉德‧馮‧梅根貝格', era: '約 1349–1350', place: '雷根斯堡', language: '德文', intro: '雷根斯堡教士康拉德據康蒂姆普雷的託馬斯改編增訂的德語自然百科，為第一部德語博物全書，兼記黑死病時代的天災省思。印刷術興起後屢刊附木刻插圖，是德語世界自然知識普及的奠基之作。' }
        
        ]
      },
      {
        key: 'natural-science',
        label: '自然與科學部',
        label_en: 'Natural Philosophy & Science',
        desc: '中世紀觀察自然界動植礦、天體運行並倡導實驗方法的科學論著。',
        works: [
          { title_zh: '論動物‧論礦物', title_orig: 'De animalibus / De mineralibus', author: '大阿爾伯特', era: '約 1250–1270', place: '科隆‧帕多瓦', language: '拉丁文', intro: '道明會學者大阿爾伯特承亞里斯多德自然學而作的兩部自然誌：「論動物」凡二十六卷，在註解亞氏之餘大量加入自身對昆蟲、鳥獸、魚類的實地觀察與解剖記述；「論礦物」則論金屬、寶石的生成、性質與所謂效力。他主張自然之事須以經驗親驗而非僅靠權威，是中世紀經驗自然研究的先行者，亦為阿奎那之師。', note: '為兩部自然誌之合錄', link: '/fathers' },
          { title_zh: '天球論', title_orig: 'Tractatus de Sphaera', author: '薩克羅博斯科（霍利伍德的約翰）', era: '約 1230', place: '巴黎', language: '拉丁文', intro: '英格蘭天文學者薩克羅博斯科在巴黎大學寫成的天文入門教本，簡明講解托勒密體系的地心宇宙：分天球結構、日月星辰運行、晝夜與四季成因、氣候帶劃分及日月食原理。全書篇幅不大卻條理清晰，自十三世紀起即列為歐洲各大學的標準天文教材，反覆抄印、評註長達四百餘年，是中世紀至文藝復興初期最普及的宇宙論課本。', note: '', link: '' },
          { title_zh: '大著作', title_orig: 'Opus Maius', author: '羅吉爾‧培根', era: '約 1267', place: '牛津‧巴黎', language: '拉丁文', intro: '方濟會士培根應教宗克勉四世之請而呈的學術改革綱領巨著，分論神學與哲學之關係、語言研究、數學、光學、實驗科學與道德哲學六大部。他力倡以數學為一切科學之鑰、以實驗（scientia experimentalis）驗證真理，並重視原文語言之精研，在光學與曆法上更有具體論證。書中超前的方法論主張，使他被後世譽為近代實驗科學的遠祖之一。', note: '', link: '' },
          { title_zh: '論光', title_orig: 'De luce', author: '羅伯特‧格羅斯泰斯特', era: '約 1225', place: '牛津', language: '拉丁文', intro: '格羅斯泰斯特以「光」為第一形式推演宇宙生成：光自一點自我繁殖成球，凝為諸天與四元素。短短數頁融合創世記、新柏拉圖主義與幾何學，被譽為中世紀的「大霹靂」雛型，是把數學引入自然哲學的開創文本。' },
          { title_zh: '通用透視學', title_orig: 'Perspectiva communis', author: '約翰‧佩坎', era: '約 1277–1279', place: '牛津／坎特伯裡', language: '拉丁文', intro: '方濟會士、坎特伯裡大主教佩坎綜合阿爾哈曾光學傳統寫成的透視學教本，論視覺、反射與折射，簡明適教。本書作為大學光學標準教材沿用至十七世紀，刊本迭出，是中世紀科學課程建制化的代表。' },
          { title_zh: '透視學十卷', title_orig: 'Perspectiva (Witelo)', author: '維特羅', era: '約 1270–1278', place: '維泰博', language: '拉丁文', intro: '西里西亞學者維特羅在教廷駐地寫成的光學鉅著十卷，系統整合阿爾哈曾的實驗光學與幾何方法，兼論視錯覺與彩虹。克卜勒日後即以「對維特羅的補充」為題著書，足見其為近代光學革命的直接跳板。' },
          { title_zh: '論虹', title_orig: 'De iride et radialibus impressionibus', author: '弗萊貝格的狄奧多里克', era: '約 1304–1310', place: '弗萊貝格／巴黎', language: '拉丁文', intro: '道明會士狄奧多里克以注水玻璃球模擬雨滴，實驗推得虹乃陽光在單一水滴內兩折射一反射所成，並解釋副虹倒色。此為中世紀實驗方法最漂亮的成果，與三百年後笛卡兒的解釋僅一步之遙，科學史家譽為經院科學的巔峰。' },
          { title_zh: '論磁石書信', title_orig: 'Epistola de magnete', author: '馬裡古的彼得（佩雷格林努斯）', era: '1269', place: '義大利南部圍城軍中', language: '拉丁文', intro: '工程師彼得在圍城軍旅中寫成的磁學書信，首度定義磁極、記述極性相斥相吸與斷磁再生兩極，並設計浮針與樞軸羅盤。這是歐洲第一部實驗磁學專著，吉爾伯特《論磁》承其餘緒，羅盤航海的理論起點。' },
          { title_zh: '論運動比例', title_orig: 'Tractatus de proportionibus', author: '託馬斯‧布拉德沃丁', era: '1328', place: '牛津默頓學院', language: '拉丁文', intro: '「深邃博士」布拉德沃丁以複比例函數重構亞里斯多德的運動定律，使力、阻與速度的關係首度數學化。本書開默頓學派運動學之先，其「布拉德沃丁函數」流行歐陸大學三百年，是數學物理學的中世紀源頭。' },
          { title_zh: '論天與世界', title_orig: 'Le Livre du ciel et du monde', author: '尼科爾‧奧雷姆', era: '1377', place: '巴黎', language: '中古法文', intro: '奧雷姆應查理五世之命以法語註譯亞里斯多德《論天》，附論中詳辯「大地自轉而天不動」在物理與聖經上皆無不可，終以信仰存而不論。其論證預演哥白尼問題的全部關節，兼為法語科學散文的奠基之作。' },
          { title_zh: '論貨幣', title_orig: 'De moneta', author: '尼科爾‧奧雷姆', era: '約 1355–1360', place: '巴黎／盧昂', language: '拉丁文', intro: '奧雷姆針對法王濫貶幣值而作的貨幣論，申言貨幣屬於共同體而非君主私產，貶值即隱形課稅、террän暴政。此為西方第一部貨幣專論，經濟思想史尊為貨幣理論的開山，展現經院學術介入公共財政的鋒芒。' },
          { title_zh: '計算之書', title_orig: 'Liber abaci', author: '比薩的李奧納多（斐波那契）', era: '1202（1228 修訂）', place: '比薩', language: '拉丁文', intro: '斐波那契引進印度—阿拉伯數字與位值計算法的劃時代教本，兼授商業算術、比例與代數，兔子數列即出其中。本書使拉丁世界的計算脫離籌算盤，商業革命的帳房與後世數學皆奠基於此。' },
          { title_zh: '默頓計算者', title_orig: 'Liber calculationum', author: '理查‧斯萬斯赫德', era: '約 1340–1350', place: '牛津默頓學院', language: '拉丁文', intro: '默頓學院「計算者」斯萬斯赫德把質變、運動與強度的量化推至極致的論集，均勻加速的「默頓中速定理」即此學圈之功。萊布尼茲曾嘆其才堪比阿基米德，本書代表中世紀數理分析的最高水位。' },
          { title_zh: '算法書', title_orig: 'Algorismus (De arte numerandi)', author: '薩克羅博斯科', era: '約 1225–1230', place: '巴黎', language: '拉丁文', intro: '薩克羅博斯科為大學編寫的印度—阿拉伯數字算術教本，與其《天球論》同為藝學院標準教材，抄本印本歷四百年不衰。「algorismus」一詞經此書而定於一尊，是「演算法」概念進入西方教育的正式戶籍。' },
          { title_zh: '論植物', title_orig: 'De vegetabilibus et plantis', author: '大阿爾伯特', era: '約 1250–1260', place: '科隆', language: '拉丁文', intro: '大阿爾伯特以親身觀察增補亞里斯多德傳統的植物學七卷，逐種描述形態、habitat 與栽培，兼論嫁接改變物性。其觀察之精使近代植物學家譽為林奈之前最偉大的植物學者，是中世紀經驗博物學的代表作。' },
          { title_zh: '狩獵鳥類之術', title_orig: 'De arte venandi cum avibus', author: '腓特烈二世', era: '約 1241–1248', place: '西西里宮廷', language: '拉丁文', intro: '皇帝腓特烈二世親撰的鷹獵與鳥類學專著，宣稱「只寫親眼驗證之事」，糾正亞里斯多德多處錯誤，附數百幅寫生插圖。它是中世紀經驗主義的異數，鳥類學史的第一座豐碑，梵蒂岡藏彩繪本尤為國寶。' },
          { title_zh: '醫學全書', title_orig: 'Pantegni', author: '非洲人康斯坦丁（譯編）', era: '約 1080–1087', place: '薩勒諾／蒙特卡西諾', language: '拉丁文', intro: '突尼斯出身的修士康斯坦丁在蒙特卡西諾把阿里‧阿拔斯的醫學大全譯編為拉丁文，理論實務各十卷，使希臘—阿拉伯醫學重返西方。本書催生薩勒諾醫學校的課程體系，是歐洲學院醫學的奠基文獻。' },
          { title_zh: '薩勒諾養生訓', title_orig: 'Regimen sanitatis Salernitanum', author: '薩勒諾醫學校（託名彙編）', era: '12–13 世紀', place: '薩勒諾', language: '拉丁文', intro: '以拉丁韻文寫成的養生格言集，託名薩勒諾醫學校致英格蘭王，論飲食起居四體液調攝，朗朗可誦。後世增衍至數千行、譯成諸語刊行數百版，是流傳最廣的中世紀醫學通俗文本，民間衛生觀唸的千年底稿。' },
          { title_zh: '自然學', title_orig: 'Physica', author: '賓根的希爾德加德', era: '約 1150–1158', place: '賓根魯佩茨貝格女修道院', language: '拉丁文', intro: '女院長希爾德加德的博物誌九卷，逐條記述草木、元素、魚鳥獸石的性質與療效，兼採萊茵民間藥草知識與德語俗名。它是中世紀女性署名的最大自然學著作，修道院醫藥實踐的直接紀錄，今日草藥學仍屢屢回訪。' },
          { title_zh: '病因與療治', title_orig: 'Causae et curae', author: '賓根的希爾德加德', era: '約 1150–1158', place: '賓根', language: '拉丁文', intro: '希爾德加德的醫學專著，自宇宙論與體液說推演疾病成因，詳述婦科、心疾與體質差異的療法，對女性身體的觀察尤為史上罕見。與《自然學》合為其醫學雙璧，展現女修道院作為醫療知識中心的實態。' },
          { title_zh: '英吉利醫學綱要', title_orig: 'Compendium medicinae', author: '吉爾伯特‧安格利庫斯', era: '約 1230–1250', place: '英格蘭', language: '拉丁文', intro: '英格蘭醫師吉爾伯特綜合薩勒諾與阿拉伯醫學的臨床全書七卷，自頭疾至足病按部位條列診治，兼載痲瘋判定與外科法。它是英格蘭最早的系統醫學全書，喬叟筆下醫生的書單即有其名，流通歐陸數百年。' },
          { title_zh: '解剖學', title_orig: 'Anathomia corporis humani', author: '蒙迪諾‧德‧盧齊', era: '1316', place: '波隆那', language: '拉丁文', intro: '波隆那醫學教授蒙迪諾據公開解剖實作寫成的解剖教本，按解剖順序敘述臟器，恢復了中斷千餘年的人體解剖教學。此後兩百年歐洲解剖課皆誦其書，直至維薩裡起而修正，是解剖學復興的正式起點。' },
          { title_zh: '曆法校正論', title_orig: 'Compotus correctorius', author: '羅伯特‧格羅斯泰斯特', era: '約 1220–1230', place: '牛津', language: '拉丁文', intro: '格羅斯泰斯特精算儒略曆的累積誤差，指出春分與月相漸離教會曆法，提出校正方案以正復活節之期。其後培根、庫薩諸家相繼論此，至一五八二年格里高利改曆方告實現，本書是三百年改曆運動的先聲。' },
          { title_zh: '天文鐘論', title_orig: 'Tractatus horologii astronomici', author: '理查‧德‧沃林福德', era: '約 1327–1336', place: '聖阿爾班斯修道院', language: '拉丁文', intro: '聖阿爾班斯院長沃林福德記述其自製巨型天文鐘的設計專著，齒輪比例、日月行度與潮汐指示俱有圖說，為機械鐘錶史最早的完整技術文獻。院長身患痲瘋仍手不停鑿，其鐘領先歐洲工藝近兩百年。' },
          { title_zh: '阿方索天文表', title_orig: 'Tabulae Alphonsinae', author: '託萊多猶太天文家團隊（阿方索十世敕修）', era: '約 1272', place: '託萊多', language: '拉丁文（原卡斯提爾語）', intro: '智者阿方索十世召集猶太天文學家依觀測修訂托勒密體系的行星表，後經巴黎學圈整理為拉丁標準本，支配歐洲天文計算近三百年。哥白尼案頭即置此表，其誤差正是新體系的催生劑，是跨信仰協作科學的豐碑。' },
          { title_zh: '田事利益書', title_orig: 'Ruralia commoda', author: '皮埃特羅‧德‧克雷申齊', era: '約 1304–1309', place: '波隆那', language: '拉丁文', intro: '波隆那法學家克雷申齊退休後綜合古典農書與親身經營寫成的農學全書十二卷，自選址、五穀、園圃至獵漁畜牧皆備。它是中世紀最完整的農學著作，印刷時代譯成諸語刊行數十版，歐洲莊園經營的標準指南。' },
          { title_zh: '亨利農書', title_orig: 'Husbandry (Walter of Henley)', author: '亨利的沃爾特', era: '約 1280', place: '英格蘭', language: '盎格魯-諾曼法文', intro: '曾為騎士後入道明會的沃爾特以法語寫成的莊園經營手冊，教導領主查帳、輪作、養畜與防弊，語多精明市儈之趣。本書為英格蘭莊園管理的標準教本，經濟史家賴以重建中世紀農業的實際運作。' },
          { title_zh: '阿伯丁動物寓言集', title_orig: 'Aberdeen Bestiary', author: '英格蘭繕寫畫坊', era: '約 1200', place: '英格蘭北部', language: '拉丁文', intro: '承《博物學者》傳統的豪華動物寓言抄本，逐獸配泥金插圖與靈意教訓：獅子拂跡喻基督、鵜鶘刺血喻救贖。動物寓言集為中世紀英格蘭最流行的圖書類型，此本裝飾未竟反而保留製作工序，是書籍考古的名品。' },
          { title_zh: '赫裡福德世界地圖', title_orig: 'Hereford Mappa Mundi', author: '霍爾丁厄姆的理查', era: '約 1300', place: '林肯／赫裡福德', language: '拉丁文', intro: '現存最大的中世紀世界地圖，繪於整張牛皮，以耶路撒冷居中，伊甸園、巴別塔與奇風異族環列，地理與救恩史疊合為一。它與其說是導航圖不如說是「時間中的世界」總覽，中世紀宇宙觀最壯麗的視覺總結。' },
          { title_zh: '埃布斯托夫世界地圖', title_orig: 'Ebstorf Mappa Mundi', author: '埃布斯托夫本篤會女修道院（傳蒂爾伯裡的傑瓦斯）', era: '約 1300', place: '下薩克森埃布斯托夫', language: '拉丁文', intro: '出自本篤會女修道院的巨幅世界地圖，將全圖疊畫於基督身軀之上——頭在東方樂園、雙手攬世界兩極，地理即基督身體。原圖毀於一九四三年空襲，賴摹本傳世，是「神學地圖學」最極致的作品。' },
          { title_zh: '宇宙圖誌', title_orig: 'Imago mundi (Petrus de Alliaco)', author: '皮埃爾‧達伊', era: '1410', place: '康佈雷', language: '拉丁文', intro: '樞機達伊綜述天文地理的宇宙誌，力主大西洋東西兩岸相距不遠、順風數日可達。哥倫布藏本眉批密佈，即憑此書向王廷力陳西航印度之可行。本書遂成地理大發現的思想觸媒，中世紀宇宙誌意外的歷史轉轍器。' },
          { title_zh: '養生書', title_orig: 'Regimen sanitatis ad regem Aragonum', author: '阿爾諾‧德‧維拉諾瓦', era: '約 1305–1308', place: '巴塞隆納', language: '拉丁文', intro: '蒙彼利埃名醫維拉諾瓦為亞拉岡王詹姆斯二世撰寫的個人養生指南，按空氣、飲食、睡眠、運動諸「非自然因素」逐項調攝。本書為中世紀養生文類的典範，旋譯成加泰隆尼亞語與希伯來語，宮廷醫學的代表文獻。' },
          { title_zh: '特羅圖拉', title_orig: 'Trotula', author: '薩勒諾的特羅塔等', era: '12 世紀', place: '薩勒諾', language: '拉丁文', intro: '以薩勒諾女醫特羅塔為名的婦科醫學三篇合集，論月事、生產、不孕與婦容調護，為中世紀流通最廣的女性醫學文本。特羅塔為文獻可考的女性醫學作者，本書譯本遍及諸俗語，是婦女醫療史的核心文獻。' },
          { title_zh: '外科學', title_orig: 'Chirurgia (Rogerius)', author: '羅傑‧弗魯加德', era: '約 1180', place: '帕爾馬／薩勒諾', language: '拉丁文', intro: '薩勒諾傳統第一部系統外科教本，按頭至足序列論創傷、骨折與手術，文字簡切可據。本書確立外科為可教之學，衍生註疏學派並譯成俗語，支配歐洲外科教學逾百年，是中世紀外科的奠基石。' },
          { title_zh: '大外科', title_orig: 'Chirurgia magna', author: '居伊‧德‧肖利亞克', era: '1363', place: '亞維儂', language: '拉丁文', intro: '教宗御醫肖利亞克總結古今的外科全書，徵引前人逾三千處，並留下黑死病兩度襲擊亞維儂的第一手臨床記述——自身染疫而痊。本書為此後兩百年歐洲外科的聖經，「大外科」之名即成外科全書的代稱。' },
          { title_zh: '健康花園', title_orig: 'Gart der Gesundheit', author: '美因茲編者群（舍費爾刊）', era: '1485', place: '美因茲', language: '德文', intro: '印刷初期最重要的德語本草書，收草木蟲石藥物四百餘條，附寫生木刻，部分插圖出自實地採繪。它把中世紀修道院藥草知識轉入印刷市場，開近代本草圖譜之先，是醫藥出版史的關鍵環節。' },
          { title_zh: '健康全書', title_orig: 'Tacuinum sanitatis', author: '伊本‧布特蘭原著（拉丁譯編）', era: '13–14 世紀（拉丁本）', place: '西西里／倫巴底', language: '拉丁文', intro: '巴格達基督徒醫師伊本‧布特蘭的養生表格經西西里宮廷譯為拉丁文，倫巴底畫坊更製成滿幅彩繪的圖鑑本，逐頁繪四季食材與起居。它是阿拉伯醫學融入西方生活文化的美麗見證，兼為中世紀日常圖像的寶庫。' },
          { title_zh: '加泰隆尼亞地圖集', title_orig: 'Atles català', author: '克雷斯克斯‧亞伯拉罕', era: '1375', place: '馬約卡', language: '加泰隆尼亞文', intro: '馬約卡猶太製圖師克雷斯克斯為亞拉岡王室繪製、獻予法王的世界地圖集，八幅羊皮上羅盤線縱橫，馬裡帝國曼薩‧穆薩與馬可波羅商隊皆入畫。它代表波特蘭實測製圖與世界圖像的合流，中世紀製圖學的最高傑作。' },
          { title_zh: '牧羊人曆', title_orig: 'Kalendrier et compost des bergiers', author: '巴黎印坊編者（居伊‧馬爾尚刊）', era: '1491', place: '巴黎', language: '中古法文', intro: '為平民編印的曆書百科：教會曆節期、放血養生、天文圖解與地獄異象木刻並陳，託名牧羊人的自然智慧。刊行後百年間法英諸語翻印不輟，是中世紀天文曆算知識下滲民間的暢銷標本。' }
        
        ]
      },
      {
        key: 'exempla-handbooks',
        label: '訓例與實用手冊部',
        label_en: 'Exempla, Florilegia and Practical Handbooks',
        desc: '講道例話集、名句彙編、家政朝聖商旅工藝手冊——中世紀實用知識與教化文獻的總匯。',
        works: [
          { title_zh: '哲學家格言集', title_orig: 'Auctoritates Aristotelis', author: '佚名編者（巴黎學圈）', era: '13 世紀末', place: '巴黎', language: '拉丁文', intro: '輯錄亞里斯多德、波愛修、塞內加等權威名句的袖珍引語手冊，供學生與講道者隨手徵引，存世抄本與印本數以百計。它把經院學問壓縮為可攜格言，是中世紀大學「引證文化」最流行的工具書之一。' },
          { title_zh: '花束彙編', title_orig: 'Manipulus florum', author: '愛爾蘭的託馬斯', era: '1306', place: '巴黎索邦', language: '拉丁文', intro: '索邦學者愛爾蘭的託馬斯把教父與古典作家名句六千則按主題字母排序，並附出處與交叉索引，開現代引語辭典之先河。本書七百年間抄本印本不絕，是檢索技術史上的里程碑，講道者的隨身武庫。' },
          { title_zh: '道德教訓集', title_orig: 'Moralium dogma philosophorum', author: '傳孔什的威廉', era: '12 世紀中', place: '沙特爾學圈', language: '拉丁文', intro: '以西塞羅《論義務》為骨架的倫理格言彙編，傳為沙特爾學派孔什的威廉所輯，流傳極廣並譯成法、德諸語。它把古典道德哲學裝訂為基督徒的處世手冊，見證十二世紀人文主義對西塞羅倫理的復興。' },
          { title_zh: '訓道例話集', title_orig: 'Exempla (Sermones vulgares 附錄)', author: '雅各‧德‧維特里', era: '約 1226–1240', place: '阿卡／羅馬', language: '拉丁文', intro: '維特里把佈道中使用的生動故事——商人、農婦、酒徒、朝聖者的日常軼事——輯為例話庫，供講道者取用。他是例話佈道法的開山宗師，這批故事兼為中世紀社會生活的意外檔案，後世例話集皆祖述之。' },
          { title_zh: '聖靈七恩例話大全', title_orig: 'Tractatus de diversis materiis praedicabilibus', author: '波旁的埃蒂安', era: '約 1250–1261', place: '里昂', language: '拉丁文', intro: '道明會審判官埃蒂安按聖靈七恩架構編纂的例話大全，近三千則故事網羅民間傳說、異端見聞與聖徒奇蹟，為中世紀最大的例話庫。其中對民間「聖犬」崇拜等記載成為民俗學珍籍，是講道文化與大眾信仰的交會檔案。' },
          { title_zh: '奇蹟對話錄', title_orig: 'Dialogus miraculorum', author: '海斯特巴赫的凱撒裡烏斯', era: '約 1219–1223', place: '海斯特巴赫熙篤會修道院', language: '拉丁文', intro: '熙篤會見習導師凱撒裡烏斯以師徒問答輯錄七百餘則奇蹟故事，分論皈依、聖體、魔鬼、臨終等十二題，供初學者靈修教育。故事多採萊茵地區近事，鮮活如小說，是中世紀盛期民間宗教心態最豐富的單一文本。' },
          { title_zh: '神學詞義區分辭典', title_orig: 'Distinctiones dictionum theologicalium', author: '裡爾的亞蘭', era: '約 1179–1195', place: '巴黎／熙篤', language: '拉丁文', intro: '「全能博士」裡爾的亞蘭按字母編排聖經詞彙的多重屬靈義：一詞之下歷數其字面、寓意、道德與末世諸義並引經為證。此類「區分辭典」是經院講道的檢索引擎，本書為其奠基之作，見證釋經學的工具化轉向。' },
          { title_zh: '羅馬人事蹟', title_orig: 'Gesta Romanorum', author: '佚名編者（英格蘭或德意志）', era: '約 1300–1342', place: '英格蘭／萊茵蘭', language: '拉丁文', intro: '託名羅馬史事的道德故事集，每則附靈意解釋，實雜東方寓言、傳奇與民間故事，為中世紀晚期最流行的故事類書。喬叟與莎士比亞皆自此取材（《威尼斯商人》三匣故事即出於此），是歐洲敘事文學的隱形水庫。' },
          { title_zh: '拉圖爾騎士教女書', title_orig: 'Livre du Chevalier de la Tour Landry', author: '拉圖爾‧朗德里騎士', era: '1371–1372', place: '安茹', language: '中古法文', intro: '安茹騎士拉圖爾為教育喪母之女編纂的例話教本，雜引聖經、聖傳與貴族社會見聞以訓婦德，兼露中世紀貴族家庭的日常肌理。本書風行三百年並經卡克斯頓英譯印行，是俗人家庭教育文獻的代表。' },
          { title_zh: '巴黎主婦書', title_orig: 'Le Ménagier de Paris', author: '佚名巴黎市民（老夫為少妻作）', era: '約 1393', place: '巴黎', language: '中古法文', intro: '年邁巴黎市民為十五歲新婦編寫的治家全書：靈修德行、園藝食譜、僱僕馭馬無所不包，附三百餘道菜譜。它是中世紀城市家政知識的完整標本，兼為飲食史與婦女生活史的第一手文獻，今為中世紀日常生活研究的必引之書。' },
          { title_zh: '聖雅各朝聖指南', title_orig: 'Liber Sancti Jacobi‧Liber peregrinationis', author: '傳普瓦捷的艾梅里‧皮科', era: '約 1140', place: '孔波斯特拉／克呂尼圈', language: '拉丁文', intro: '《加里斯都抄本》第五卷，為赴聖地牙哥朝聖者逐段指點路線、食水、民風與聖髑，兼吐槽各地飲食與言語，被稱為歐洲第一部旅行指南。它見證朝聖如何催生跨國的實用知識文類，是中世紀道路文明的活地圖。' },
          { title_zh: '通商實務', title_orig: 'La pratica della mercatura', author: '佩戈洛蒂', era: '約 1335–1343', place: '佛羅倫斯', language: '義大利文', intro: '佛羅倫斯巴爾迪商行職員佩戈洛蒂編纂的商人手冊，詳列自黑海至中國的商路、度量衡、匯兌與貨品，稱往契丹之路「日夜皆安」。本書是蒙古和平時代歐亞貿易網的商業百科，經濟史家視為中世紀商業文明的第一文獻。' },
          { title_zh: '死亡藝術', title_orig: 'Ars moriendi', author: '佚名（康斯坦茨會議圈道明會士）', era: '約 1415–1450', place: '德意志南部', language: '拉丁文', intro: '教導臨終者抵禦五重試探、善終歸主的手冊，黑死病後應運而生，有長短二版，短版配十一幅木版畫流通尤廣。它把善終化為可學的技藝，是中世紀晚期死亡文化的核心文本，印刷初期最暢銷的書種之一。' },
          { title_zh: '棋弈道德化', title_orig: 'Liber de moribus hominum et officiis nobilium super ludo scacchorum', author: '雅各‧德‧塞索利斯', era: '約 1300', place: '倫巴底', language: '拉丁文', intro: '道明會士塞索利斯以棋盤喻社會：王后主教騎士與八枚小卒各配職分訓誨，藉棋道講授各階層的倫理。本書風行程度一度僅次於聖經，卡克斯頓印行的英譯本為英格蘭最早印刷書籍之一，是遊戲與道德教化結合的奇著。' },
          { title_zh: '英格蘭修道院聯合目錄', title_orig: 'Registrum Anglie de libris doctorum et auctorum veterum', author: '牛津方濟會士編者群', era: '約 1250–1320', place: '牛津', language: '拉丁文', intro: '方濟會士普查英格蘭與蘇格蘭近二百所修道院藏書編成的聯合書目，逐一標記教父與古代作家著作的收藏地點。它是歐洲最早的聯合圖書目錄，圖書館學史的開山文獻，見證託缽修會治學對文獻檢索的系統需求。' },
          { title_zh: '諸藝清單', title_orig: 'De diversis artibus (Schedula diversarum artium)', author: '泰奧菲盧斯（傳赫爾馬斯豪森的羅傑）', era: '約 1100–1120', place: '帕德博恩一帶', language: '拉丁文', intro: '本篤會士泰奧菲盧斯記錄繪畫顏料、彩色玻璃與金工鑄造全套工藝的手冊，序言以神學申明手藝乃聖靈恩賜。它是中世紀最完整的工藝技術文獻，教堂彩窗與聖器製作的第一手配方，藝術史與技術史共尊的經典。' },
          { title_zh: '藝匠手冊', title_orig: 'Il libro dell\'arte', author: '琴尼諾‧琴尼尼', era: '約 1390–1400', place: '帕多瓦', language: '義大利文', intro: '喬託畫派傳人琴尼尼記錄蛋彩、濕壁畫、鍍金與調色工序的畫室手冊，自稱「為敬禮上帝與聖母」而傳藝。本書是中世紀晚期畫坊知識的總結與文藝復興技法的前奏，至今仍為壁畫修復者案頭的實用指南。' }
        
        ]
      },
      {
        key: 'byzantine-eastern-reference',
        label: '拜占庭與東方類書部',
        label_en: 'Byzantine and Eastern Reference Works',
        desc: '拜占庭百科主義（蘇達、君士坦丁七世工程）與敘利亞東方傳統的辭書、摘錄與彙編。',
        works: [
          { title_zh: '蘇達辭書', title_orig: 'Suda (Suidae Lexicon)', author: '拜占庭佚名編者群', era: '約 970–1000', place: '君士坦丁堡', language: '希臘文', intro: '拜占庭十世紀末的巨型辭書百科，三萬餘條目兼收詞義訓詁與人物書目，保存大量佚失古籍的引文與古代作家生平。它是通往古希臘文獻的最大單一孔道，古典學至今日日檢用，為拜占庭「百科主義」時代的最高成就。' },
          { title_zh: '帝國行政論', title_orig: 'De administrando imperio', author: '君士坦丁七世‧波菲羅格尼圖斯', era: '約 948–952', place: '君士坦丁堡', language: '希臘文', intro: '「生於紫室者」君士坦丁七世為皇子編纂的治國手冊，逐族剖析佩切涅格、羅斯、斯拉夫、亞美尼亞等鄰邦的虛實與馭之之術。書中保存諸民族起源的獨家記載，是拜占庭外交智慧的內廷機密本，東歐早期史的第一等史料。' },
          { title_zh: '典儀論', title_orig: 'De ceremoniis aulae Byzantinae', author: '君士坦丁七世（主持彙編）', era: '約 956–959', place: '君士坦丁堡', language: '希臘文', intro: '詳載拜占庭宮廷典禮的官方彙編：皇帝加冕、迎使、節慶巡行、賽車場儀節，鉅細靡遺。君士坦丁七世自序稱典儀使帝權「如宇宙運行般有序」，本書是理解拜占庭政治神學與宮廷文化的鑰匙，兼存大量已佚前代禮制。' },
          { title_zh: '農事集成', title_orig: 'Geoponika', author: '拜占庭佚名編者（獻君士坦丁七世）', era: '約 950', place: '君士坦丁堡', language: '希臘文', intro: '拜占庭百科運動下的農學總匯二十卷，輯錄古代至晚期的農藝、園藝、釀酒、畜牧文獻，所引諸家原書多已亡佚。它是希臘羅馬農學傳統的中世紀總結，後譯入敘利亞文、阿拉伯文與亞美尼亞文，流澤及於東方農書。' },
          { title_zh: '君士坦丁摘錄', title_orig: 'Excerpta Constantiniana', author: '君士坦丁七世（主持）', era: '約 945–959', place: '君士坦丁堡', language: '希臘文', intro: '君士坦丁七世命學士把古代以降史家著作按五十三個主題（使節、德行、陰謀等）分類摘錄的大型史料類書，今存使節篇等四部。波利比烏斯等史家泰半佚文賴此保存，是拜占庭「摘錄文化」最宏大的工程。' },
          { title_zh: '雜學總覽', title_orig: 'De omnifaria doctrina', author: '米海爾‧普塞洛斯', era: '約 1060–1075', place: '君士坦丁堡', language: '希臘文', intro: '普塞洛斯為皇帝編寫的問答體小百科，二百則短章綜述神學、靈魂論、自然學與氣象，融新柏拉圖哲學於正統框架。它展示拜占庭宮廷「哲學皇帝之師」如何將全部知識裝進袖珍手冊，是中期拜占庭學術的縮影。' },
          { title_zh: '解頤故事集', title_orig: 'Ktābā d-Tunnāyē Mgaḥḥkānē (Laughable Stories)', author: '巴爾‧赫布拉烏斯', era: '約 1280', place: '馬拉蓋（伊利汗國）', language: '敘利亞文', intro: '敘利亞正教大學者巴爾‧赫布拉烏斯晚年輯錄的趣話集，七百餘則笑談分採希臘哲人、波斯智者、阿拉伯格言與基督教修士軼事，序言自道「使憂傷的心得舒暢」。它是東方基督教罕見的幽默類書，見證伊利汗國治下多元文化的交融。' }
        
        ]
      },
      {
        key: 'liberal-arts',
        label: '七藝與邏輯部',
        label_en: 'Liberal Arts & Logic',
        desc: '中世紀大學文學院的基礎課程教本：三藝四術合稱的七藝與經院邏輯訓練讀本。',
        works: [
          { title_zh: '七藝教本', title_orig: 'Artes Liberales (manualia)', author: '中世紀大學文學院（傳統教本群編）', era: '九至十三世紀', place: '巴黎‧波隆那‧牛津等', language: '拉丁文', intro: '中世紀大學文學院教授「七種自由技藝」的標準教本總稱：前三藝（trivium）為文法、修辭、辯證，後四術（quadrivium）為算術、幾何、天文、音樂。這些教本上承馬爾蒂亞努斯‧卡佩拉、波愛修斯與卡西奧多魯斯的古典整理，是進入神學、法學、醫學高等學院前必修的共同底子，奠定了整個拉丁知識界的學術語言與思維框架。', note: '為傳統教本之匯編，非一人一書', link: '' },
          { title_zh: '邏輯綱要', title_orig: 'Summulae Logicales (Tractatus)', author: '西班牙的彼得（後傳為教宗若望二十一世）', era: '約 1230', place: '巴黎‧西班牙', language: '拉丁文', intro: '中世紀流傳最廣的邏輯教科書，系統整理亞里斯多德與波愛修斯以降的辭項邏輯：論命題、謂詞、三段論、論辯謬誤，並發展出獨特的「指代理論」（suppositio）分析詞語在命題中的指涉。全書條理分明、便於記誦，自十三世紀起即為歐洲各大學辯證課的標準入門，評註與改編本層出不窮，影響邏輯教學達三百年之久。', note: '作者身份與後世同名教宗的對應有爭議', link: '' },
          { title_zh: '辯證法', title_orig: 'Dialectica (Abaelardus)', author: '彼得‧阿伯拉爾', era: '約 1117–1121', place: '巴黎', language: '拉丁文', intro: '阿伯拉爾最大的邏輯著作，全面重構亞里斯多德舊邏輯，於共相問題提出「概念論」中道，以言語分析拆解形上難題。他把辯證法奉為「一切學問的裁判」，本書是十二世紀邏輯復興的代表作，經院方法的鍛造爐。' },
          { title_zh: '邏輯導論', title_orig: 'Introductiones in logicam', author: '舍伍德的威廉', era: '約 1240–1250', place: '巴黎', language: '拉丁文', intro: '英格蘭邏輯家舍伍德的威廉在巴黎講授的邏輯教本，首創以「Barbara, Celarent」記憶詩背誦三段論式，並發展詞項指代理論。西班牙的彼得與後世教本皆承其法，是「詞項邏輯」傳統的開山教材。' },
          { title_zh: '辯證法綱要', title_orig: 'Summulae de dialectica', author: '讓‧布里丹', era: '約 1340–1355', place: '巴黎', language: '拉丁文', intro: '巴黎藝學院大師布里丹以唯名論立場全面改寫邏輯課程的綱要書，兼論指代、推論與詭辯，「布里丹之驢」的悖論意象即與其學相連。本書支配中歐大學邏輯教學至十六世紀，是晚期經院邏輯的集大成教本。' },
          { title_zh: '論語法方式', title_orig: 'De modis significandi (Grammatica speculativa)', author: '埃爾福特的託馬斯', era: '約 1300–1310', place: '埃爾福特', language: '拉丁文', intro: '思辨語法學派的代表作，主張語法範疇映照存有與思維的普遍結構，故可建立凌駕各語言的普遍語法。本書長期誤傳為董思高著作，海德格的教授資格論文即研究之，是中世紀語言哲學的高峰文本。' },
          { title_zh: '教義韻文法', title_orig: 'Doctrinale puerorum', author: '維勒迪厄的亞歷山大', era: '1199', place: '巴黎／諾曼第', language: '拉丁文', intro: '以兩千六百餘行六步格韻文寫成的拉丁文法教本，供學童記誦，取代普里西安成為中世紀晚期全歐學校的標準課本，抄本印本逾四百版。人文主義者痛詆其野蠻正足證其無所不在，是中世紀教育史的第一暢銷書。' },
          { title_zh: '希臘風文法', title_orig: 'Graecismus', author: '貝蒂訥的埃伯哈德', era: '約 1212', place: '法蘭德斯', language: '拉丁文', intro: '以韻文講授拉丁文法兼詞源的教本，因首章論希臘語源而得名「希臘風」。與《教義韻文法》並列中世紀晚期兩大文法課本，大學章程明定必讀，其詞源解釋雖多穿鑿，卻是理解中世紀語文教育的必經之門。' },
          { title_zh: '巴黎詩藝', title_orig: 'Parisiana poetria', author: '約翰‧德‧加蘭', era: '約 1220–1235', place: '巴黎', language: '拉丁文', intro: '巴黎教師加蘭綜論散文、韻文與書信寫作之藝的修辭教本，兼授講道體與公文體，附範例習作。它把古典修辭改裝為中世紀學堂的實用寫作課，是「詩藝」文類建制化的代表教材。' },
          { title_zh: '新詩學', title_orig: 'Poetria nova', author: '傑弗裡‧德‧文索夫', era: '約 1208–1213', place: '英格蘭', language: '拉丁文', intro: '以兩千行韻文自身示範修辭技法的寫作教本，論佈局、放大縮小與文采諸法，題獻英諾森三世。全歐傳抄逾二百部，喬叟亦戲仿其句，是中世紀修辭學最成功的教科書，「新詩學」遂成文類之名。' },
          { title_zh: '修辭古術', title_orig: 'Rhetorica antiqua (Boncompagnus)', author: '博納孔帕紐‧達‧西尼亞', era: '1215', place: '波隆那', language: '拉丁文', intro: '波隆那書信術大師博納孔帕紐的修辭書信大全，按情境羅列公文私函範式，自嘲自誇兼備，於波隆那大學公開宣讀時加冕桂冠。書信術（ars dictaminis）為中世紀官署文書的核心技藝，本書是其最恢弘的紀念碑。' },
          { title_zh: '小論', title_orig: 'Micrologus', author: '圭多‧達雷佐', era: '約 1026–1032', place: '阿雷佐', language: '拉丁文', intro: '本篤會士圭多的音樂教本，創四線譜記音高、以「ut re mi」唱名法教視唱，使歌者不賴口傳即能識譜，自詡「一年成就十年之功」。本書是西方記譜法與音樂教育的奠基文獻，音樂史上影響最深遠的著作之一。' },
          { title_zh: '音樂手冊', title_orig: 'Musica enchiriadis', author: '佚名（法蘭克修道學圈）', era: '約 850–900', place: '東法蘭克', language: '拉丁文', intro: '加洛林晚期的音樂理論教本，首度系統記述平行奧爾加農的複音唱法並附記譜示例，是西方複音音樂最早的理論見證。與姊妹篇《手冊註解》同傳，開啟了從聖詠單音走向和聲織體的千年航程。' },
          { title_zh: '七藝之戰', title_orig: 'La Bataille des VII ars', author: '亨利‧德‧安德利', era: '約 1230', place: '巴黎', language: '古法文', intro: '以寓言詩描寫奧爾良的文法與巴黎的邏輯兩軍交戰：荷馬維吉爾列陣於前，三段論式衝鋒於後，終以邏輯得勝而文學敗走。此詩活畫十三世紀課程之爭——人文教育讓位於辯證法，是教育史最生動的諷喻文獻。' },
          { title_zh: '詞彙大全', title_orig: 'Elementarium doctrinae rudimentum', author: '帕皮亞斯', era: '約 1040–1050', place: '倫巴底', language: '拉丁文', intro: '倫巴底學者帕皮亞斯編纂的字母序拉丁辭典，兼收詞義、詞源與百科說明，首創嚴格按前三字母排序並於序言說明檢索法。它被稱為第一部現代意義的辭典，中世紀語文工具書的分水嶺。' },
          { title_zh: '詞源大典', title_orig: 'Liber derivationum (Magnae derivationes)', author: '比薩的胡古喬', era: '約 1190', place: '波隆那', language: '拉丁文', intro: '教會法學家胡古喬以詞根衍生法組織的大型拉丁詞典，一詞根下輯盡孳乳諸詞，兼發詞源議論。但丁屢引其說，全歐法學與神學課堂皆備此書，是中世紀盛期最權威的語文工具書。' },
          { title_zh: '大詞典', title_orig: 'Catholicon', author: '約翰內斯‧巴布斯（熱那亞的約翰）', era: '1286', place: '熱那亞', language: '拉丁文', intro: '道明會士巴布斯集文法與辭典於一書的「大全詞典」，按字母全序編排，檢索之便冠絕當代，一四六〇年於美因茲印行，為最早的大型印刷辭書之一。自抄本到印本流通四百年，是中世紀詞典學的總結之作。' },
          { title_zh: '聖經難詞典', title_orig: 'Expositiones vocabulorum Biblie', author: '威廉‧布里託', era: '約 1250–1270', place: '巴黎', language: '拉丁文', intro: '方濟會士布里託解釋聖經難詞二千五百餘條的專門辭典，逐條考訂希伯來、希臘詞源並引文法家為證。它是中世紀讀經者案頭的標準工具，抄本逾百部，代表語文學服務釋經的成熟形態。' },
          { title_zh: '大邏輯', title_orig: 'Logica magna', author: '威尼斯的保羅', era: '約 1396–1399', place: '帕多瓦', language: '拉丁文', intro: '奧斯定會士威尼斯的保羅集十四世紀英國邏輯之大成的巨帙，論詞項、命題、推論與詭辯無所不包，篇幅為中世紀邏輯書之最。它把牛津的邏輯精微移植義大利，支配帕多瓦學風，是晚期經院邏輯的百科式總匯。' },
          { title_zh: '解決詭辯的規則', title_orig: 'Regulae solvendi sophismata', author: '威廉‧海特斯伯裡', era: '1335', place: '牛津默頓學院', language: '拉丁文', intro: '默頓學者海特斯伯裡以詭辯題材訓練分析技巧的教本，論說謊者悖論、極大極小與瞬時速度，將邏輯推向數學物理的邊界。本書為義大利大學邏輯課指定用書百餘年，展示中世紀「詭辯練習」的智性鋒芒。' },
          { title_zh: '定量歌樂藝術', title_orig: 'Ars cantus mensurabilis', author: '科隆的弗朗科', era: '約 1280', place: '科隆／巴黎', language: '拉丁文', intro: '科隆教士弗朗科確立以音符形狀本身標示時值的記譜原則，使節奏脫離語境約定而可精確書寫。「弗朗科記譜法」為其後一切節奏記譜的基礎，本書是西方音樂邁向精密書寫文化的關鍵一步。' },
          { title_zh: '新藝術', title_orig: 'Ars nova', author: '菲利普‧德‧維特里（託名傳本）', era: '約 1322', place: '巴黎', language: '拉丁文', intro: '以「新藝術」為名的音樂理論文獻，倡二分節拍與微細音值，解放了十四世紀法國音樂的節奏想像，馬肖的複調彌撒即其果實。教宗若望二十二世曾頒詔斥其浮巧，反證其顛覆之力，「新藝術」遂成整個時代的名字。' },
          { title_zh: '音樂術語定義集', title_orig: 'Terminorum musicae diffinitorium', author: '約翰內斯‧廷克托里斯', era: '約 1472–1495 刊', place: '那不勒斯', language: '拉丁文', intro: '法蘭德斯樂師廷克托里斯編纂的音樂術語辭典，收詞近三百條，為史上第一部印行的音樂辭書。成於複音音樂鼎盛的那不勒斯宮廷，它標誌音樂學術語的自覺整理，音樂辭典學的起點。' },
          { title_zh: '俗語論', title_orig: 'De vulgari eloquentia', author: '但丁‧阿利吉耶裡', era: '約 1303–1305', place: '流亡義大利', language: '拉丁文', intro: '但丁以拉丁文為俗語辯護的語言學論著，考察語言變遷、分類義大利十四種方言，尋求足堪高詩的「光輝俗語」。書雖未竟，其歷史語言學眼光超前數百年，是俗語文學自覺的理論宣言，語言學史的先知之作。' }
        
        ]
      }
    ]
  },
  wai: {
    summary: '外藏錄基督教世界以外的知識傳統：伊斯蘭世界融貫哲學、數學、天文與醫學的科學百科，及猶太傳統中以喀巴拉為核心的祕學典籍。',
    divisions: [
      {
        key: 'islamic-science',
        label: '伊斯蘭科學百科部',
        label_en: 'Islamic Science & Encyclopaedia',
        desc: '伊斯蘭黃金時代融貫哲學、數學、天文與醫學的百科論文集與專科鉅著。',
        works: [
          { title_zh: '純潔兄弟會論文集', title_orig: 'Rasāʾil Ikhwān al-Ṣafāʾ', author: '純潔兄弟會（巴斯拉祕密學社）', era: '約十世紀', place: '巴斯拉', language: '阿拉伯文', intro: '巴斯拉一個帶伊斯瑪儀派色彩的祕密學社所編、共五十二篇的百科全書，分數學、自然學、心理與理智學、神學形上學四大門類，內容涵蓋算術、音樂、地理、礦植動物、靈魂、邏輯與宇宙論。它以新柏拉圖主義與畢達哥拉斯數論為框架，試圖把希臘哲學、科學與伊斯蘭信仰熔於一爐，是中世紀伊斯蘭世界知識綜合的代表作，影響後世蘇菲與哲學傳統甚深。', note: '作者為匿名學社群體', link: '' },
          { title_zh: '代數學', title_orig: 'al-Kitāb al-mukhtaṣar fī ḥisāb al-jabr wa-l-muqābala', author: '花拉子米', era: '約 820', place: '巴格達‧智慧宮', language: '阿拉伯文', intro: '花剌子模裔學者花拉子米在巴格達智慧宮寫成的數學奠基之作，系統處理一次與二次方程的解法，分「還原」（al-jabr，移項）與「對消」（al-muqābala，合併同類項）兩大運算。書名中的 al-jabr 即後世「代數」（algebra）一詞之源，作者拉丁化的名字則衍生出「算法」（algorithm）。此書奠定代數成為獨立學科，是伊斯蘭數學西傳歐洲的關鍵橋梁。', note: '', link: '' },
          { title_zh: '醫典', title_orig: 'al-Qānūn fī al-Ṭibb', author: '阿維森納（伊本‧西那）', era: '約 1025', place: '波斯‧哈馬丹', language: '阿拉伯文', intro: '波斯哲人兼醫家阿維森納總集希臘、波斯、印度與阿拉伯醫學傳統的五卷醫學鉅著，從醫學總論、單味藥、各系統疾病、全身性病症到複方藥物，體系恢宏、論理嚴整。它把蓋倫醫學與亞里斯多德自然哲學整合為一完備系統，自十二世紀經拉丁譯本傳入歐洲後，數百年間被奉為各大學醫學院的標準教本，影響東西方醫學至文藝復興之後。', note: '', link: '' }
        ]
      },
      {
        key: 'jewish-mysticism',
        label: '猶太祕學部',
        label_en: 'Jewish Mysticism (Kabbalah)',
        desc: '中世紀猶太傳統中以神聖流溢、字母奧義與十質點（sefirot）為核心的喀巴拉祕學典籍。',
        works: [
          { title_zh: '光輝之書', title_orig: 'Sefer ha-Zohar', author: '摩西‧德‧萊昂（託西緬‧巴‧約海之名）', era: '約 1280–1290', place: '西班牙‧卡斯提爾', language: '亞蘭文（雜希伯來文）', intro: '喀巴拉傳統的核心經典，以對托拉的神祕釋經為體，借古亞蘭文寫成，假託二世紀拉比西緬‧巴‧約海及其門徒漫遊論道之口。書中展開「十質點」（sefirot）為神聖流溢的結構，以光明與奧義層層詮解經文，論神性內在生命、善惡之源與靈魂之命運。學界多認為實出十三世紀西班牙的摩西‧德‧萊昂之手，是中世紀晚期猶太神祕主義最具影響力的著作。', note: '託名古代拉比，實為中世紀晚期之作', link: '' },
          { title_zh: '創造之書（中世紀傳本）', title_orig: 'Sefer Yetzirah', author: '佚名（古代傳本，中世紀廣注）', era: '成書年代不詳；中世紀廣傳並評註', place: '近東猶太世界', language: '希伯來文', intro: '猶太祕學中最古老而簡短的宇宙生成論文獻，講上帝藉「三十二條智慧之路」——即十個質點（sefirot）與希伯來字母表二十二個字母——創造萬有，把宇宙、時間與人體三層對應於語言的奧祕結構。其成書年代古遠難考，卻在中世紀被薩阿底亞、阿布拉菲亞等學者反覆評註闡發，遂成喀巴拉與字母神祕主義的理論源頭，與「光輝之書」並為猶太祕學兩大柱石。', note: '原典年代古遠，此收中世紀評註傳本', link: '' }
        ]
      }
    ]
  }
}
  ],
}
