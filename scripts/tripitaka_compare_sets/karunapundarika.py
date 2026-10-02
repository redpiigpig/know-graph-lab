# 悲華經（Karuṇāpuṇḍarīka）異譯對讀 —— 由 scripts/tripitaka_compare.py 以其全域 exec（SETS、Path、json、re 可直接用）。
#
# 本子：梵本 GRETIL `sa_karuNApuNDarIkasUtra`（Yamada 1968 校訂本，全本六品，頁碼標記 (KpSū n)）
#       ＋藏譯 Toh 112（84000 TMX，六章；章首 0／83／325／724／2495／2998，迄 3222）＋英
#       ＋曇無讖《悲華經》T0157（六品）、失譯《大乘悲分陀利經》T0158（三十品）。
# 骨架＝梵本六品（藏譯六章與梵本同次第）。第四品〈授記品〉極長（曇無讖本 5.8 萬字），
# 依悲分陀利經的品界（離諍王授記、三王子授記…）分成 c04-1…c04-N 數組。
#
# 品次對照（依各本品名與內容逐一核對）：
#   梵 1 dharmacakrapravartana ＝ 藏 1 ＝ 曇〈轉法輪品〉＝ 悲分〈轉法輪品〉
#   梵 2 dhāraṇīmukha          ＝ 藏 2 ＝ 曇〈陀羅尼品〉＝ 悲分〈入陀羅尼門品〉＋〈入一切種智行陀羅尼品〉
#   梵 3 dānavisarga           ＝ 藏 3 ＝ 曇〈大施品〉  ＝ 悲分〈勸施品〉＋〈勸發品〉
#   梵 4 bodhisattvavyākaraṇa  ＝ 藏 4 ＝ 曇〈諸菩薩本授記品〉＝ 悲分〈離諍王授記品〉至〈莊嚴品〉
#   梵 5 dāna                  ＝ 藏 5 ＝ 曇〈檀波羅蜜品〉＝ 悲分〈眼施品〉至〈菩薩集品〉
#   梵 6（無品題）             ＝ 藏 6 ＝ 曇〈入定三昧門品〉＝ 悲分〈入三昧門品〉＋〈囑累品〉

_KP_TMX = [0, 83, 325, 724, 2495, 2998, 3222]
_KP_ZH = {"T0157": ("曇無讖本", "曇無讖譯《悲華經》十卷・北涼（五世紀初）"),
          "T0158": ("悲分陀利經", "失譯《大乘悲分陀利經》八卷・附秦錄")}


def _kp(slug, title, intro, units, sa, bo, zh):
    """sa＝(start, end, cuts) 或 None；bo＝(TMX 起, 迄, [(義段, TMX 絕對行號)])；
    zh＝[(work, nodes, cuts, 其他 src 欄)]，其他欄可含 end、anchor_nodes、reorder。"""
    a, b, en = bo
    vs = []
    if sa:
        st, ed, sc = sa
        vs.append({"id": "sa", "lang": "sa", "label": "梵本", "who": "Yamada 1968 校訂本・GRETIL",
                   "src": {"gretil": "sa_karuNApuNDarIkasUtra", "start": st} | ({"end": ed} if ed else {}), "cuts": sc})
    vs += [{"id": side, "lang": side, "label": lab, "who": who, "src": {"tmx": "toh112", "side": side, "from": a, "to": b},
            "lines": [(u, n - a) for u, n in en]}
           for side, lab, who in [("bo", "藏譯", "德格版 Toh 112・84000 翻譯記憶"), ("en", "84000 英譯", "譯自藏譯・與藏文逐句對齊")]]
    for w, nodes, cuts, extra in zh:
        extra = extra or {}
        vs.append({"id": w, "lang": "lzh", "label": _KP_ZH[w][0], "who": _KP_ZH[w][1],
                   "src": {"work": w, "nodes": nodes, "start": cuts[0][1]} | {x: y for x, y in extra.items() if x != "reorder"},
                   "cuts": cuts} | ({"reorder": True} if extra.get("reorder") else {}))
    SETS[slug] = {"title": f"悲華經・{title}", "family": "sa", "extra_works": [], "intro": intro, "units": units, "versions": vs}


_KP_INTRO0 = ("梵本 Karuṇāpuṇḍarīka（GRETIL，Yamada 1968 本，全本六品）＋藏譯 Toh 112《悲白蓮華》＋84000 英譯＋"
              "曇無讖《悲華經》T0157、失譯《大乘悲分陀利經》T0158。")

# ── 第一品 轉法輪 ─────────────────────────────────────────────────────────────
_kp("karunapundarika-c01", "轉法輪品",
    _KP_INTRO0 + "梵本〈dharmacakrapravartana〉＝藏譯第一章＝兩漢譯〈轉法輪品〉。釋迦於耆闍崛山，彌勒等萬菩薩向東南禮蓮華尊（蓮華上）佛，"
    "寶日光明（寶照明）問其因緣，佛說蓮華世界莊嚴與蓮華尊佛昨夜成道、現神變、轉不退法輪。"
    "梵本會眾次第不同（先比丘尼、再文殊等八萬菩薩、再帝釋諸天），且無彌勒等禮佛一段，改作釋迦放光照十方、大地六種震動（c1-04x，他本無）。",
    [("c1-00", "經題・歸敬"), ("c1-01", "如是我聞・比丘眾"), ("c1-02", "菩薩眾"), ("c1-03", "諸天、龍王眾"),
     ("c1-04", "世尊為四眾說法"), ("c1-04x", "梵本：世尊放光遍照・六種震動"), ("c1-05", "彌勒等萬菩薩向東南禮蓮華尊佛"),
     ("c1-06", "寶日光明問其因緣"), ("c1-07", "佛讚善問・誡聽"), ("c1-08", "蓮華世界：琉璃地・寶樹"),
     ("c1-09", "樓觀・寶池・華中化生菩薩"), ("c1-10", "金山・佛光寶光・無晝夜"), ("c1-11", "菩提樹・蓮華座・昨夜成道"),
     ("c1-12", "問神變：肉髻放光照上方・諸菩薩來集"), ("c1-13", "廣長舌相"), ("c1-14", "毛孔放光・十方菩薩來集"),
     ("c1-15", "轉不退轉法輪"), ("c1-16", "品尾題")],
    ("Karuṇāpuṇḍarīka-sūtram", "dvitīyo dhāraṇīmukhaparivartaḥ",
     [("c1-00", "Karuṇāpuṇḍarīka-sūtram"), ("c1-01", "evaṃ mayā śrutam"), ("c1-02", "aśītibhiśca bodhisattvasahasraiḥ"),
      ("c1-03", "śakreṇa ca devānāmindreṇa"), ("c1-04", "tena khalu punaḥ samayena bhagavāṃś"),
      ("c1-04x", "tadā nānāvarṇaraśmayo niścaritā"), ("c1-06", "atha ratnavairocano nāma"),
      ("c1-07", "atha khalu bhagavān ratnavairocanaṃ bodhisattvaṃ mahāsattvametadavocat"), ("c1-08", "\"asti kulaputra pūrvadakṣiṇasyāṃ"),
      ("c1-09", "teṣu ca vṛkṣāntareṣu"), ("c1-10", "teṣu ca vṛkṣakūṭāgārāntariteṣu"), ("c1-11", "padmāyāṃ kulaputra lokadhātau indro"),
      ("c1-12", "evamukte, ratnavairocano bodhisattvo"), ("c1-13", "sa ca kulaputra padmottarastathāgato jihvendriyaṃ"),
      ("c1-14", "atha kulaputra padmottarastathāgato jihvendriyam"), ("c1-15", "atha khalu kulaputra padmottarastathāgato 'rhan"),
      ("c1-16", "iti śrīkaruṇāpuṇḍarīke mahāyānasūtre dharmacakra")]),
    (0, 83, [("c1-00", 0), ("c1-01", 4), ("c1-02", 5), ("c1-03", 6), ("c1-04", 17), ("c1-05", 18), ("c1-06", 19), ("c1-07", 26),
             ("c1-08", 30), ("c1-09", 42), ("c1-10", 53), ("c1-11", 60), ("c1-12", 67), ("c1-13", 76), ("c1-14", 78),
             ("c1-15", 81), ("c1-16", 82)]),
    [("T0157", ["轉法輪品第一"], [("c1-01", "如是我聞"), ("c1-02", "菩薩摩訶薩四百四十萬人"), ("c1-03", "是時，復有大梵天王"),
                               ("c1-04", "爾時世尊，眷屬圍繞"), ("c1-05", "爾時，彌勒菩薩"), ("c1-06", "爾時，會中有菩薩摩訶薩，名寶日光明"),
                               ("c1-07", "爾時，佛告寶日光明菩薩"), ("c1-08", "爾時，世尊告寶日光明：「善男子！東南方"),
                               ("c1-09", "有七寶樓觀"), ("c1-10", "其園觀外周匝"), ("c1-11", "「善男子！其佛世界有菩提樹"),
                               ("c1-12", "爾時，世尊釋迦牟尼說是事已"), ("c1-13", "「善男子！爾時，彼佛見諸菩薩出其舌相"),
                               ("c1-14", "「善男子！蓮華尊佛復放身毛孔光"), ("c1-15", "善男子！爾時，彼佛作此變化")], None),
     ("T0158", ["轉法輪品第一"], [("c1-01", "如是我聞"), ("c1-02", "菩薩摩訶薩眾八十四百千人俱"), ("c1-03", "娑訶世界主梵天"),
                               ("c1-04", "爾時世尊，與如是等上首"), ("c1-05", "爾時彌勒菩薩摩訶薩"), ("c1-06", "爾時寶照明菩薩即從座起"),
                               ("c1-07", "爾時世尊告寶照明菩薩言：「善哉"), ("c1-08", "爾時世尊告寶照明菩薩言：「善男子！東南方"),
                               ("c1-09", "一一樹間有七寶臺"), ("c1-10", "諸樹寶臺周匝四面"), ("c1-11", "「善男子！蓮華世界菩提之樹"),
                               ("c1-12", "是時寶照明菩薩白佛言"), ("c1-13", "「善男子！蓮華上如來見大眾集"),
                               ("c1-14", "「善男子！蓮華上如來還攝舌相"), ("c1-15", "「善男子！爾時蓮華上如來，還攝神通")], None)])
