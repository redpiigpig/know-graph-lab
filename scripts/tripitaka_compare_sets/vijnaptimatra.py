# 唯識二論（世親《唯識三十頌》《唯識二十論》）異譯對讀 —— 由 scripts/tripitaka_compare.py 以其全域 exec（SETS 可直接用）。
#
# 三十頌（slug trimsika）：骨架＝梵本 GRETIL `sa_vasubandhu-triMzikAvijJaptikArikA`（頌號 Tvk_n）一頌一節，
#   另收安慧《唯識三十頌釋》梵本（GRETIL `-comm`，頌引文帶「1ab」「2cd」一類半頌標記，釋文隨頌）；
#   漢譯：玄奘《唯識三十論頌》T1586、真諦《轉識論》T1587（頌釋混合、無頌形）、《成唯識論》T1585（護法等釋，逐頌釋論）。
#   🚨 玄奘譯頌與梵本常差半頌（漢第 3 頌末「相應唯捨受」＝梵 4a，漢第 4 頌末「阿羅漢位捨」＝梵 5a，
#   漢第 12 頌後半起隨煩惱＝梵 12b…），兩本漢譯照玄奘頌號切、梵本照梵本頌號切，差的半頌寫進 intro。
#
# 二十論（slug vimsatika）：見下方。

_TV_UNITS = [
    ("m0", "造論緣起"),
    ("m01", "Tvk 1　我法假說，依識所變"), ("m02", "Tvk 2　三能變；初阿賴耶識"), ("m03", "Tvk 3　不可知執受處了，五遍行"),
    ("m04", "Tvk 4　捨受、無覆無記，恒轉如瀑流"), ("m05", "Tvk 5　第二能變末那"), ("m06", "Tvk 6　四煩惱常俱"),
    ("m07", "Tvk 7　隨所生所繫，三位無有"), ("m08", "Tvk 8　第三能變六識"), ("m09", "Tvk 9　六位心所"),
    ("m10", "Tvk 10　遍行、別境"), ("m11", "Tvk 11　善心所"), ("m12", "Tvk 12　煩惱與隨煩惱（一）"),
    ("m13", "Tvk 13　隨煩惱（二）"), ("m14", "Tvk 14　隨煩惱（三）與不定"), ("m15", "Tvk 15　五識依本識隨緣現"),
    ("m16", "Tvk 16　意識常現起，五位不起"), ("m17", "Tvk 17　一切唯識"), ("m18", "Tvk 18　一切種識展轉生分別"),
    ("m19", "Tvk 19　業習氣與二取習氣"), ("m20", "Tvk 20　遍計所執"), ("m21", "Tvk 21　依他起、圓成實"),
    ("m22", "Tvk 22　非異非不異"), ("m23", "Tvk 23　三無性"), ("m24", "Tvk 24　相、生、勝義無性"),
    ("m25", "Tvk 25　唯識實性"), ("m26", "Tvk 26　資糧位"), ("m27", "Tvk 27　加行位"), ("m28", "Tvk 28　通達位"),
    ("m29", "Tvk 29　修習位、轉依"), ("m30", "Tvk 30　究竟位"),
    ("x30", "（真諦本卷末追釋二執隨眠、二不顯現）"),
    ("m99", "結頌・尾題"),
]

_TV_SA = [
    ("m0", "Atha Triṃśikāvijñaptikārikāḥ"),
    ("m01", "ātmadharmopacāro hi vividho"), ("m02", "vipāko mananākhyaśca"), ("m03", "asaṃviditakopādisthāna"),
    ("m04", "upekṣā vedanā tatrā"), ("m05", "tasya vyāvṛtirarhatve"), ("m06", "kleśaiścaturbhiḥ sahitaṃ"),
    ("m07", "yatrajastanmayairanyaiḥ"), ("m08", "dvitīyaḥ pariṇāmo 'yaṃ"), ("m09", "sarvatragairviniyataiḥ"),
    ("m10", "ādyāḥ sparśādayaś"), ("m11", "alobhādi trayaṃ"), ("m12", "mānadṛgvicikitsāśca"),
    ("m13", "śāṭhyaṃ mado"), ("m14", "vikṣepo 'samprajanyaṃ"), ("m15", "pañcānāṃ mūlavijñāne"),
    ("m16", "manovijñānasambhūtiḥ"), ("m17", "vijñānapariṇāmo 'yaṃ vikalpo"), ("m18", "sarvabījaṃ hi vijñānaṃ"),
    ("m19", "karmaṇo vāsanā"), ("m20", "yena yena vikalpena"), ("m21", "paratantrasvabhāvastu"),
    ("m22", "ata eva sa naivānyo"), ("m23", "trividhasya svabhāvasya"), ("m24", "prathamo lakṣaṇenaiva"),
    ("m25", "dharmāṇāṃ paramārthaśca"), ("m26", "yāvadvijñaptimātratve"), ("m27", "vijñaptimātramevedam"),
    ("m28", "yadālambanaṃ vijñānaṃ"), ("m29", "acitto 'nupalambho"), ("m30", "sa evānasravo"),
    ("m99", "triṃśikāvijñaptikārikāḥ samāptāḥ"),
]

# 安慧釋：頌前的「…ity ata āha」提問句歸下一頌
_TV_STH = [
    ("m0", "Vasubandhu: Triṃśikāvijñaptikārikā"),
    ("m01", "ātmadharmopacāro hi vividho yaḥ"), ("m02", "yo 'sau trividhaḥ pariṇāma ukto"),
    ("m03", "yadi pravṛttivijñānavyatiriktam ālayavijñānam asti"), ("m04", "tatrālayavijñāne vid iti sāmānyopadeśena"),
    ("m05", "tasyaivaṃ śrotasā pravṛttasya"), ("m06", "vijñānasvarūpatvād avaśyaṃ tac caittaiḥ"),
    ("m07", "ete hy ātmamohādayaḥ kleśā"), ("m08", "dvitīyaḥ pariṇāmo 'yam"), ("m09", "sā punaḥ kīdṛśaiś caitasikaiḥ"),
    ("m10", "ya ete sarvatragādaya uddiṣṭās"), ("m11", "tadanantaroddiṣṭās tv idānīṃ kuśalā"),
    ("m12", "tadanantaroddiṣṭās tu kleśā"), ("m13", "śāṭhyaṃ svadoṣapracchādanopāya"),
    ("m14", "vikṣepo rāgadveṣamohāṃśikaś"), ("m15", "idam idānīñ cintyate"), ("m16", "idam īdānīṃ vaktavyam"),
    ("m17", "yatra vijñānapariṇāme ātmadharmopacāraḥ sa punas"), ("m18", "yadi sarvaṃ vijñaptimātrakam eva na tato"),
    ("m19", "idānīṃ vijñaptimātre anāgataṃ"), ("m20", "yadi vijñaptimātram evedaṃ kathaṃ na sūtravirodhaḥ"),
    ("m21", "parikalpitānantaraṃ paratantrasvabhāvo"), ("m22", "ata eva sa naivānyo nānanyaḥ"),
    ("m23", "yadi dravyam eva paratantraḥ kathaṃ sūtre"), ("m24", "idānīṃ trividhasya svabhāvasya yā yasya"),
    ("m25", "dharmāṇāṃ paramārthaś ca sa yatas tathāpi"), ("m26", "yadi vijñaptimātram evedaṃ kasmāc"),
    ("m27", "idam idānīṃ vaktavyaṃ kim artharahita"), ("m28", "kadā punar vijñānagrāhasya"),
    ("m29", "yadaivaṃ vijñaptimātratāyāṃ cittam avasthitaṃ"), ("m30", "sa evānāsravo dhātur iti"),
    ("m99", "triṃśikāvijñaptibhāṣyaṃ samāptam"),
]

# 玄奘頌本：頌號（全形數字）起切；頌前的問句（「已說初能變，第二能變其相云何？頌曰」）歸下一頌
_TV_T1586 = [
    ("m0", "護法等菩薩約此三十頌"), ("m01", "謂外問言"), ("m02", "２謂異熟"), ("m03", "３不可知執受"),
    ("m04", "４是無覆無記"), ("m05", "已說初能變"), ("m06", "６四煩惱"), ("m07", "７有覆無記"),
    ("m08", "如是已說第二能變"), ("m09", "９此心所"), ("m10", "１０初遍行"), ("m11", "１１善謂"),
    ("m12", "１２煩惱謂"), ("m13", "１３誑"), ("m14", "１４放逸"), ("m15", "已說六識心所相應"),
    ("m16", "１６意識常現起"), ("m17", "已廣分別三能變相"), ("m18", "若唯有識，都無外緣"),
    ("m19", "雖有內識而無外緣"), ("m20", "若唯有識，何故世尊"), ("m21", "２１依他起"), ("m22", "２２故此與依他"),
    ("m23", "若有三性"), ("m24", "２４初即相無性"), ("m25", "２５此諸法勝義"), ("m26", "後五行頌明唯識行位者"),
    ("m27", "二、加行位"), ("m28", "三、通達位"), ("m29", "四、修習位"), ("m30", "五、究竟位"),
]

# 真諦《轉識論》：無頌形，依內容對到梵本頌（小惑二十四種與梵本隨煩惱次第逐一相當，在「八諂曲」「十九散亂」下刀）
_TV_T1587 = [
    ("m01", "識轉有二種"), ("m02", "次明能緣有三種"), ("m03", "問：此識何相何境"), ("m04", "此識及心法，但是自性無記"),
    ("m05", "乃至得羅漢果"), ("m06", "與四惑相應"), ("m07", "亦有五種心法相應，名字同前"), ("m08", "第三塵識者"),
    ("m09", "與十種心法相應"), ("m10", "十種心法者"), ("m11", "十善者"), ("m12", "大惑有十種者"),
    ("m13", "八諂曲"), ("m14", "十九散亂"), ("m15", "五識於第六意識"), ("m16", "問：此意識於何處不起"),
    ("m17", "如此識轉不離兩義"), ("m18", "又說唯識義得成者"), ("m19", "記曰：由二種宿業"), ("m20", "記曰：如是如是分別"),
    ("m21", "此所顯體實無，此分別者"), ("m22", "是故前性於後性不一不異"), ("m23", "然一切諸法但有三性"),
    ("m24", "三無性者，即不離前三性"), ("m25", "此三無性，是一切法真實"), ("m26", "若人修道智慧未住"),
    ("m27", "若謂但唯有識"), ("m28", "若智者不更緣此境"), ("m29", "何以故？由修觀熟"), ("m30", "是名無流界"),
    ("x30", "釋曰：二執隨眠"),
]

# 《成唯識論》：每頌釋文起點（頌文成組引出：2b–4、5–7、12b–14a、15–16、20–22、23–25，組內各頌以釋文起處下刀）
_TV_T1585 = [
    ("m0", "稽首唯識性"), ("m01", "(壹) 明唯識相"), ("m02", "識所變相雖無量種"), ("m03", "此識行相、所緣云何"),
    ("m04", "法有四種：謂善、不善"), ("m05", "如是已說初能變相"), ("m06", "此意相應有幾心所"), ("m07", "末那心所，何性所攝"),
    ("m08", "如是已說第二能變"), ("m09", "六識與幾心所相應"), ("m10", "前所略摽六位心所"), ("m11", "已說遍行、別境二位"),
    ("m12", "如是已說善位心所"), ("m13", "云何為誑"), ("m14", "云何放逸"), ("m15", "已說六識心所相應"),
    ("m16", "由五轉識行相麁動"), ("m17", "已廣分別三能變相"), ("m18", "㊀釋違理"), ("m19", "雖有內識，而無外緣"),
    ("m20", "1 釋三自性不成難"), ("m21", "由斯理趣，眾緣所生"), ("m22", "由前理故，此圓成實"), ("m23", "若有三性，如何世尊"),
    ("m24", "云何依此而立彼三"), ("m25", "一、解第二十五頌"), ("m26", "如是所成唯識相、性，誰於幾位"),
    ("m27", "㊀問起> 次加行位"), ("m28", "㊀問起> 次通達位"), ("m29", "㊀問起> 次修習位"), ("m30", "㊀問起> 後究竟位"),
    ("m99", "(壹) 結釋示正名"),
]

SETS["trimsika"] = {
    "title": "唯識三十頌", "family": "sa", "extra_works": [],
    "intro": ("世親《唯識三十頌》（Triṃśikāvijñaptikārikā）。骨架＝梵本 GRETIL 頌號 Tvk 1–30，一頌一節；"
              "另收安慧《唯識三十頌釋》梵本（Triṃśikāvijñaptibhāṣya），釋文隨頌，頌前的提問句歸下一頌。"
              "漢譯三本：玄奘《唯識三十論頌》（附唐人科文，照漢譯頌號切，頌前問句歸下一頌）；"
              "真諦《轉識論》（頌釋混合、無頌形，依內容對到梵本各頌；卷末「釋曰」追釋第二十六、二十八頌，另列一節）；"
              "《成唯識論》（護法等釋、玄奘糅譯，CBETA 本夾有現代科判標題）——頌文成組引出，各頌從其釋文起處下刀，"
              "故第四頌一節含阿賴耶識的教證理證、第七頌一節含末那的教證理證，篇幅特長。"
              "🚨 玄奘譯頌與梵本常差半頌：漢第三頌末「相應唯捨受」＝梵 4a；漢第四頌末「阿羅漢位捨」＝梵 5a；"
              "漢第六頌末「及餘觸等俱」＝梵 7a，第七頌首「有覆無記攝」＝梵 6a；漢第十二頌首「貪瞋癡」＝梵 11d，第十三頌首「誑」＝梵 12 末；"
              "漢第十四頌首「放逸及失念」＝梵 13 末。漢譯欄照玄奘頌號，梵本欄照梵本頌號，所以這幾節兩邊差半頌。"
              "安慧釋的善心所、煩惱兩段照漢譯分（梵 10d 信慚愧的釋文歸第 11 節、11d 貪瞋癡的釋文歸第 12 節）。"),
    "units": _TV_UNITS,
    "versions": [
        {"id": "sa", "lang": "sa", "label": "梵本", "who": "《唯識三十頌》Triṃśikāvijñaptikārikā・GRETIL",
         "src": {"gretil": "sa_vasubandhu-triMzikAvijJaptikArikA"}, "cuts": _TV_SA},
        {"id": "sa-sthiramati", "lang": "sa", "label": "安慧釋（梵）", "who": "安慧 Sthiramati《唯識三十頌釋》Triṃśikāvijñaptibhāṣya・GRETIL",
         "src": {"gretil": "sa_vasubandhu-triMzikAvijJaptikArikA-comm"}, "cuts": _TV_STH},
        {"id": "T1586", "lang": "lzh", "label": "玄奘頌本", "who": "玄奘譯《唯識三十論頌》・唐",
         "src": {"work": "T1586", "start": _TV_T1586[0][1]}, "cuts": _TV_T1586},
        {"id": "T1587", "lang": "lzh", "label": "轉識論", "who": "真諦譯《轉識論》・陳",
         "src": {"work": "T1587", "start": _TV_T1587[0][1]}, "cuts": _TV_T1587},
        {"id": "T1585", "lang": "lzh", "label": "成唯識論", "who": "護法等造・玄奘譯《成唯識論》・唐",
         "src": {"work": "T1585", "start": _TV_T1585[0][1], "end": "成唯識論後序"}, "cuts": _TV_T1585},
    ],
}
