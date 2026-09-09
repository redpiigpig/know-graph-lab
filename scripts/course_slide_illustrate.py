# -*- coding: utf-8 -*-
"""替原本沒有圖的條列頁配圖。

課堂簡報一份三十幾張、只有三到十張有圖，投影出去一整節都是字。這一份是
「標題 → 圖片 key」的**指名對照表**：渲染時把對得上的 `bullets` 頁改成
`imgbullets`（左文右圖），不多生一張投影片。

🚨 **指名，不做模糊比對。** 讀本系列最貴的一課是「印出正常頁面卻配錯內容」；
   標題關鍵字比對一定會把「儀式」的圖配到「儀式」以外的頁上，而且看起來很正常。
   所以這裡只認**一字不差的標題**，對不上就不配。

🚨 配圖會把內文欄從 30.9 cm 縮到 17.0 cm。塞不下的頁**不配**（`fits()` 擋掉），
   否則不是字被縮成看不清，就是被拆成兩頁、整份超過張數上限。

圖片本身由 course_slide_images*.py 從維基共享資源抓下，授權寫進 manifest。
"""

# 課程代號 → {投影片標題: 圖片 key}
ILLUSTRATE = {
    'wr': {
        # 第 1 章 宗教是什麼
        '為什麼用「神聖」而不用「神」？': 'sacred-tree-shrine',
        '探詢：為什麼不用「相信」': 'tillich-paul',
        '組織與活動：探詢如何化為具體可見的形式': 'passover-seder',
        '那條著名的階梯': 'tylor-edward',
        '兩次轉折：歐洲「發現」佛教，以及儒教之爭': 'ricci-xuguangqi',
        '中國材料把歐洲人逼到了牆角': 'kang-youwei',
        '意外的後果：「宗教」一詞如何進入東亞': 'meiji-shrine-rite',
        # 第 2 章 八個向度
        '② 經驗：四種類型': 'teresa-avila',
        '④ 教義：神話被追問之後的結果': 'nicene-creed-ms',
        '⑤ 儀式：最外顯也最持久': 'bar-mitzvah',
        '⑤ 儀式（續）：曆法與潔淨': 'mikveh-bath',
        '⑧ 物質：多數人接觸宗教的方式': 'omamori-amulets',
        '八個向度': 'shinto-priest',
        # 第 5 章 泛靈論
        '泰勒的理論，以及它漏掉了什麼': 'frazer-james',
        '臺灣原住民族：神聖者與教義': 'amis-ilisin',
        '臺灣原住民族：聖行與體制': 'bunun-ritual',
        '約魯巴的離散形態': 'candomble',
        '易洛魁與美洲原住民教會': 'iroquois-longhouse',
        '印度部落民（ādivāsī）': 'santal-festival',
        # 第 6 章 哲學泛神論
        '新吠檀多：一個常被誤會的事': 'vivekananda',
        '基督宗教的默觀傳統：為什麼有人被譴責、有人被封聖': 'meister-eckhart',
        '室利毗濕奴派與限定不二論（印度教）': 'ramanuja',
        '過程神學：最完整的現代版本': 'whitehead-alfred',
        # 第 7 章 神話多神論
        '對照希伯來聖經': 'merneptah-stele',
        '密教：城邦宗教答不出的那個問題': 'eleusis-relief',
        '凱爾特、斯拉夫、波羅的': 'gundestrup-cauldron',
        # 第 8 章 現存的多神論
        '印度教：三大教派與聖行': 'shiva-nataraja',
        '神道最重要的歷史轉折': 'yasukuni-shrine',
        '東亞其他：巫俗、天道教、母道信仰、苯教': 'korean-mudang',
        '尤利安：最後一次嘗試': 'julian-emperor',
        # 第 9 章 一神論
        '早期以色列：不是一神論，是單一神崇拜': 'mesha-stele',
        '第二以賽亞的翻轉': 'cyrus-cylinder',
        '猶太教：八個欄位': 'synagogue-ark',
        '伊斯蘭：教義、聖行與體制': 'salat-prayer',
        # 第 10 章 二元神論與融合一神論
        '波斯統治期間，猶太教吸收了什麼': 'behistun',
        '諾斯底主義': 'nag-hammadi-codex',
        '摩尼教': 'manichaean-painting',
        '曼達教': 'mandaean-baptism',
        '越南與加勒比海的三支': 'caodai-temple',
        '中東的另外兩支與美洲的離散諸教': 'bahai-temple',
        # 第 11 章 實用神論
        '儒教：聖典與教義': 'four-books',
        '佛教：聖典的特殊處境': 'pali-palm-leaf',
        '佛教：當代的四件事': 'ambedkar',
        # 第 12 章 自然神論與無神論
        '自然神論與中國的一段因緣': 'voltaire',
        '不可知論': 'huxley-thomas',
        '無神論：這個詞的歷史與古代先例': 'lucretius',
        '二十世紀：以無神論為名的迫害': 'soviet-antireligious',
        # 第 13 章 世俗化
        '「世俗化」原本是個法律名詞': 'westphalia-treaty',
        '卡薩諾瓦的「公共宗教」': 'solidarity-poland',
        '「美國例外」還是「歐洲例外」？': 'american-megachurch',
        # 第 14 章 個人化與對話
        'SBNR：有靈性但沒有宗教': 'meditation-retreat',
        '對話的四種層次': 'assisi-prayer',
        # 第 15 章 臺灣宗教史
        '荷西時期：一次中斷的接觸（1624–1662）': 'fort-zeelandia',
        '神明作為族群的標誌': 'sanshan-guowang',
        '從厲到神：有應公、萬善爺、義民爺': 'yimin-temple',
    },
    'ch': {
        # 第 1 章
        '基督宗教共有的五項核心': 'apostles-creed',
        # 第 2 章 拿撒勒人耶穌
        '一個按常識應該被遺忘的人': 'sea-of-galilee',
        '史料一：四福音書是宣講文本': 'gospel-illumination',
        '對觀福音問題與 Q': 'codex-vaticanus',
        '歷史耶穌研究：三波': 'schweitzer-albert',
        '教導（二）比喻：讓聽的人自己判自己': 'good-samaritan',
        '死亡：釘十字架是史實': 'crucifix-vs-cross',
        # 第 3 章 初代教會
        '最早的宣講：內容不是教訓，是死與復活': 'empty-tomb-icon',
        '保羅：三重身份的橋樑': 'ephesus-theatre',
        '小普林尼的信（112 年）：外部見證': 'pliny-younger',
        '迫害的實情比通俗想像複雜': 'catacomb-tomb',
        '迫害留下的兩個結構後果': 'constantine',
        # 第 4 章 正典
        '「正典」是什麼': 'muratorian-fragment',
        '舊約：三層結構記錄了成典次序': 'aleppo-codex',
        '次經／第二正典之爭': 'codex-sinaiticus',
        '同一個技術問題，兩種答案': 'gutenberg-bible',
        '漢語與臺灣的譯本': 'chinese-union-version',
        # 第 5 章 兩千年的讀法
        '古代：預表與寓意': 'origen',
        '現代：歷史批判法': 'wellhausen',
        '處境化解經：沒有中立的閱讀': 'base-community',
        '奴隸制案例的三個推論': 'abolition-medallion',
        # 第 6 章 大公會議
        '君士坦丁堡（381）：三一論定型': 'cappadocian-fathers',
        '代價：第一次大分裂': 'armenian-church',
        '教義發展的四個機制': 'newman-john-henry',
        # 第 7 章 教父與東方基督教
        '護教士：與外部文化交涉的經典案例': 'justin-martyr',
        '東正教靈修：神化與耶穌禱文': 'christ-pantocrator-ch',
        '俄羅斯：靠禮儀的美感傳教': 'st-basil-cathedral',
        # 第 8 章 中世紀西方教會
        '西羅馬崩潰之後': 'gregory-great',
        '日耳曼各族的改宗：由上而下': 'clovis-baptism',
        '托缽修會回應的是一個真實的社會變化': 'francis-assisi',
        '教權與王權：一條上升與崩落的曲線': 'canossa',
        '第四次拉特朗（1215）：制度定型': 'innocent-iii',
        '修道運動為什麼在那個時候興起？': 'benedict-rule',
        '改革前就已存在的批判力量': 'erasmus',
        # 第 9 章 宗教改革
        '英國：一條政治先行的路線': 'henry-viii',
        '重洗派：被雙方共同迫害的第三條路': 'anabaptist-martyrs',
        '馬爾堡會談（1529）：卡在最後一項': 'marburg-colloquy',
        # 第 10 章 近代
        '啟蒙運動的四重挑戰': 'darwin-charles',
        '自由派：施萊爾馬赫的策略': 'schleiermacher',
        # 第 11 章 二十世紀
        '大屠殺之後的兩個問題': 'auschwitz-memorial',
        '五旬節派的三波': 'azusa-street',
        # 第 12 章 禮儀
        '聖事：清單本身就是神學立場': 'eucharist-elements',
        '時間：年曆與齋期': 'advent-wreath',
        '日常祈禱與生命禮儀': 'rosary-beads',
        '參訪時要看什麼（比記流程重要）': 'baroque-church',
        # 第 13 章 體制
        '會眾制：靈活，但沒有煞車': 'baptist-meeting-house',
        '獨身與女性按立': 'women-ordination',
        '教會的政治行為被組織形態決定': 'geneva-cathedral',
        # 第 14 章 看得見的神學
        '西方中世紀：教堂作為總體作品': 'chartres-cathedral',
        '毀像運動：各改革者立場並不相同': 'beeldenstorm',
        # 第 15 章 臺灣
        '日治時期：壓力造成的意外後果': 'taiwan-church-news',
        '原住民族的集體改宗': 'taiwan-indigenous-church',
        # 第 16 章 生死觀
        '這個區別有實際後果': 'last-judgment',
        '末世論的四種讀法': 'apocalypse-tapestry',
        '地獄：一個正在改變的教義': 'dante-inferno',
    },
    'sl': {
        # 第 2 章 漢字
        '六書：不是造字的歷史，是讀字的方法': 'seal-script',
        '文字作為宗教實踐的對象': 'xizi-pagoda',
        '《詩經》：從祭歌到考試範圍': 'shijing-manuscript',
        '屈原：作者問題與宗教身分': 'quyuan-portrait',
        '三個使用場所：詩社、廟宇、書房': 'tainan-confucius-temple',
        # 第 3 章 經典的成立
        '正典化的三個動作': 'confucius-temple-stele',
        '《老子》：從子書變成經書': 'laozi-riding-ox',
        '《儀禮》：一部只能被執行的書': 'confucian-wedding',
        # 第 6 章 六朝
        '玄學清談與佛教義理的交會': 'seven-sages',
        '志怪：作者的目的不是虛構，而是舉證': 'chinese-ghost-painting',
        '靈驗記：為了說服而設計的文體': 'water-moon-guanyin',
        '《文心雕龍》：一部懂佛教的文論': 'wenxin-diaolong',
        '僧傳：一種新的傳記文體': 'monk-portrait',
        '山水詩與佛教': 'chinese-landscape',
        # 第 7 章 唐代
        '《六祖壇經》：漢地撰述，稱「經」': 'platform-sutra',
        '燈錄：認祖歸宗的名單': 'bodhidharma',
        '唐詩裡的佛教': 'wangwei-painting',
        '道教文學：另一條線': 'daozang-volume',
        # 第 8 章 敦煌
        '變文：韻散交替是為耳朵設計的': 'bianwen-manuscript',
        '《大目乾連冥間救母變文》': 'mulian-rescue',
        # 第 9 章 戲曲
        '演出的場合決定劇目': 'temple-festival-opera',
        # 第 10 章 神魔小說
        '善書與功過格：用表格實踐倫理': 'taishang-ganying',
        '《西遊記》的丹道讀法': 'neijing-tu',
        '章回小說裡的說書遺跡': 'chinese-storyteller',
        # 第 11 章 日本
        '假名是怎麼長出來的': 'manyoshu',
        # 第 12 章 韓半島
        '科舉：漢文作為統治階層的門檻': 'imperial-exam-cells',
        '《東文選》與《朝鮮王朝實錄》': 'joseon-annals',
        # 第 13 章 越南
        '《禪苑集英》：越南有自己的法脈': 'vietnam-zen-temple',
        '越南的科舉與文廟': 'vietnam-pagoda-inscription',
        # 第 14 章 臺灣漢文學
        '鸞書：至今仍在生產的文言宗教文本': 'spirit-writing',
        '臺灣的方志與碑碣': 'taiwan-stone-tablet',
        '歌仔冊：另一種白話韻文': 'koa-a-chheh',
        # 第 15、16 章
        '原住民族語聖經': 'amis-bible',
        '白話文運動的標準': 'xin-qingnian',
    },
}


def apply(slides, course, has_image, fits):
    """把對得上的 bullets 頁換成 imgbullets。回傳 (新的 slides, 換掉幾張)。

    has_image(key) → 這張圖抓到了沒有；fits(item) → 換成窄欄之後還裝不裝得下。
    同一份簡報裡同一張圖不重複用。
    """
    table = ILLUSTRATE.get(course, {})
    used, out, n = set(), [], 0
    for item in slides:
        if item[0] != 'bullets':
            out.append(item)
            continue
        key = table.get(item[1])
        if not key or key in used or not has_image(key):
            out.append(item)
            continue
        # ('bullets', 標題, 條目, 副標?) → ('imgbullets', 標題, 條目, 圖, 副標?)
        rest = tuple(item[3:])
        cand = ('imgbullets', item[1], item[2], key) + rest
        if not fits(cand):
            out.append(item)
            continue
        used.add(key)
        out.append(cand)
        n += 1
    return out, n
