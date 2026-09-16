# -*- coding: utf-8 -*-
r"""封面配圖 —— 每一份簡報的第一頁要有一張與該單元相關的圖。

使用者 2026-09-16：「每一張簡報第一頁就要有相關的圖片。」

以**章**為鍵（一個單元取它頭一章的圖），值是 `course_slide_images*.py` 已經抓下來、
授權已查核過的 key。全部取自既有圖庫，不另外下載——授權那一關已經過了。

🚨 **指名，不做關鍵字比對**（與配圖表、範文表同一條規矩）。
🚨 對不上就**出聲**：`check()` 會把「表上有、圖庫沒有」的 key 列出來。
   靜靜跳過的話，封面會退回無圖版，而那看起來完全正常——沒有人會發現少了圖。
"""

COVERS = {
    # ── 基督宗教概論 ────────────────────────────────────────────────────
    ('ch', 1): 'st-peters-square',        # 什麼是基督宗教
    ('ch', 2): 'christ-pantocrator-ch',   # 拿撒勒人耶穌
    ('ch', 3): 'catacomb-fresco',         # 初代教會的三百年
    ('ch', 4): 'codex-sinaiticus',        # 正典是怎麼形成的
    ('ch', 5): 'medieval-scriptorium',    # 兩千年的讀法
    ('ch', 6): 'nicaea-council',          # 信經與大公會議
    ('ch', 7): 'desert-monastery',        # 教父與東方基督教世界
    ('ch', 8): 'gothic-cathedral',        # 中世紀西方教會
    ('ch', 9): 'wittenberg-door',         # 宗教改革
    ('ch', 10): 'wesley-john',            # 近代基督教
    ('ch', 11): 'vatican-ii-ch',          # 二十世紀與當代
    ('ch', 12): 'eucharist-elements',     # 禮儀與聖事
    ('ch', 13): 'bishop-ordination',      # 四大宗派與教會體制
    ('ch', 14): 'sistine-chapel',         # 藝術與物質文化
    ('ch', 15): 'tainan-church',          # 臺灣的基督宗教
    ('ch', 16): 'last-judgment',          # 生死觀與終末盼望

    # ── 世界宗教文化導論 ────────────────────────────────────────────────
    ('wr', 1): 'kaaba-crowd',             # 什麼是宗教
    ('wr', 2): 'mazu-pilgrimage',         # 宗教裡有什麼：八個向度
    ('wr', 3): 'longshan-temple',         # 信仰、體制與範疇
    ('wr', 4): 'max-muller',              # 宗教怎麼分類
    ('wr', 5): 'amis-ilisin',             # 泛靈論與原住民族傳統宗教
    ('wr', 6): 'whirling-dervishes',      # 哲學泛神論與萬有在神論
    ('wr', 7): 'ziggurat-ur',             # 古代文明的諸神譜系
    ('wr', 8): 'shiva-nataraja',          # 現存的多神論
    ('wr', 9): 'western-wall',            # 一神論（上）
    ('wr', 10): 'fire-temple',            # 二元神論與融合一神論
    ('wr', 11): 'buddha-preaching',       # 實用神論（上）
    ('wr', 12): 'nietzsche',              # 實用神論（下）
    ('wr', 13): 'westphalia-treaty',      # 世俗化與政教關係
    ('wr', 14): 'vatican-ii',             # 個人化、基要主義、對話
    ('wr', 15): 'fort-zeelandia',         # 臺灣宗教（上）
    ('wr', 16): 'wangye-temple',          # 臺灣宗教（下）

    # ── 宗教系國文講義 ──────────────────────────────────────────────────
    ('sl', 1): 'sinographic-map',         # 導論：漢字書寫圈
    ('sl', 2): 'oracle-bone',             # 六書、字體與卜辭
    ('sl', 3): 'stone-classics',          # 經典的成立
    ('sl', 4): 'kumarajiva',              # 佛典漢譯
    ('sl', 5): 'tripitaka-printing-block',  # 大藏經的世界
    ('sl', 6): 'baopuzi',                 # 六朝
    ('sl', 7): 'huineng',                 # 唐代
    ('sl', 8): 'dunhuang-library-cave',   # 敦煌變文與講唱文學
    ('sl', 9): 'nuo-opera-mask',          # 戲曲與宗教演藝
    ('sl', 10): 'xiyouji-illustration',   # 明清神魔小說
    ('sl', 11): 'kukai',                  # 日本漢文學
    ('sl', 12): 'haeinsa-tripitaka',      # 韓半島漢文學
    ('sl', 13): 'vietnam-stele',          # 越南漢文學
    ('sl', 14): 'taiwan-poetry-society',  # 台灣漢文學
    ('sl', 15): 'nestorian-stele',        # 聖經漢譯與宗教經典的漢文翻譯
    ('sl', 16): 'hunminjeongeum',         # 去漢字化與漢文傳統
}


def cover_key(src, chapters):
    """一個單元的封面圖＝它頭一章的圖。查無就回 None（封面退回無圖版）。"""
    return COVERS.get((src, min(chapters))) if chapters else None


def check():
    """把「表上有、圖庫裡沒有」的 key 列出來。回傳 [(課程, 章, key), ...]。"""
    import json
    from pathlib import Path
    base = Path(r'G:\我的雲端硬碟\資料\知識圖工作室\教學')
    folders = {'wr': '115-1_世界宗教文化導論', 'sl': '115-1_宗教系國文講義',
               'ch': '115-1_基督宗教概論'}
    bad = []
    for src, folder in folders.items():
        d = base / folder / '簡報' / '圖片'
        f = d / '_manifest.json'
        man = json.loads(f.read_text(encoding='utf-8')) if f.exists() else {}
        for (c, ch), key in COVERS.items():
            if c != src:
                continue
            m = man.get(key)
            if not m or not (d / m['file']).exists():
                bad.append((c, ch, key))
    return bad


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    bad = check()
    print(f'封面圖 {len(COVERS)} 筆，缺 {len(bad)} 筆')
    for c, ch, key in bad:
        print(f'  ✖ {c} 第 {ch} 章 → {key}')
