# -*- coding: utf-8 -*-
"""初階宗教學日文文獻選讀：自訂十五週計畫與各週讀本。

這門課老師只排「依個人程度客製化自學」，讀什麼由學生自己定。owner 的目標是
**將來研究無教會主義**，起點是 N5，所以計畫走雙軌：

  主線（W03 起）現代日文：矢內原忠雄。戰後刊行，新字新假名，「である」體，
      是無教會第二代裡最接近現代日文的人。
  副線（W06 起）文語：文語訳聖書 → 內村鑑三。無教會的原始文獻與他們自己讀的
      聖經都是文語，繞不過去；但**先從附振假名的文語訳聖書入手**，漢字讀音
      不必查，剩下的難度只有文法。而且經文內容 owner 本來就熟，等於現成的
      comprehensible input。

W14 刻意讓同一位作者（內村）的文語與口語並排，看清兩種文體的分界。

## 讀量怎麼定

N5 精讀不是「讀完一篇」，是「讀懂一段」。所以每週給的是**實質字數目標**
（`TARGET`），腳本再回頭算該取到第幾段——不是先切一大塊再回頭找理由。

「實質字數」= 總字數扣掉振假名。文語訳聖書每個漢字都注了假名，
「幸福（さいはひ）なるかな」表面 12 字、實質只有 7 字，不扣就會把讀量高估一倍。

級距：W03–05 三百到四百字（剛起步，逐詞查）→ W06–08 四百到五百（文語有振假名，
內容又熟）→ W10–13 五百到七百（講演體長句）→ W14 兩篇合計約九百（文體對照）。
一週一節或幾段，不求讀完整篇；整篇字數另標，行有餘力再往下讀。

🚨 這支最容易犯的錯是「切出來看起來正常，其實切錯段」
（[[feedback_reader_silent_failures]]）。兩個具體陷阱，都踩過：

  1. **上下篇重疊**——用「湊到 N 字」配「跳過前 k 段」切上下篇，k 猜錯就重疊，
     而兩個檔案打開都正常。所以改用 `fit()` 回報實際段落區間，區間寫進檔案裡，
     肉眼一看就知道有沒有疊到。
  2. **文體切錯邊**——《後世への最大遺物》前面依序是「はしがき（文語）→ 再版に
     附する序言（文語）→ 改版に附する序（1925，已是口語）→ 講演本體（口語）」。
     靠字數切一定切錯，文體分界只能按段落索引人工指定。

語料一律取自本機既有快取（青空文庫 1,140 篇＋文語訳聖書 283 章），不另外上網抓：
    output/source-cache/original-readers/japanese-full/

    python -X utf8 scripts/japanese_self_study_plan.py
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from course_html import write_html  # noqa: E402

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "output", "source-cache", "original-readers", "japanese-full")
AOZORA = os.path.join(CACHE, "aozora", "texts")
SCRIPTURE = os.path.join(CACHE, "scripture")
DEST = r"G:\我的雲端硬碟\玄奘\博一上\上課\初階宗教學日文文獻選讀"

WEEK_DIRS = {
    1: "W01 課程介紹．目標設定", 2: "W02 個別化自學", 3: "W03 與老師個別討論課程目標",
    4: "W04 個別化自學", 5: "W05 個別化自學", 6: "W06 個別化自學", 7: "W07 個別化自學",
    8: "W08 個別化自學", 9: "W09 與老師個別討論課程目標進度", 10: "W10 個別化自學",
    11: "W11 個別化自學", 12: "W12 個別化自學", 13: "W13 個別化自學",
    14: "W14 個別化自學", 15: "W15 個別化自學",
}

# ── 出處（書目資料照青空文庫圖書卡與維基文庫原樣抄）────────────────────────
SRC = {
    "nyumon": {
        "作者": "矢內原忠雄（1893–1961）", "作品": "キリスト教入門",
        "初出": "「キリスト教入門」角川新書、角川書店、1952（昭和 27）年 11 月 11 日",
        "底本": "『キリスト教入門』",
        "電子文本": "青空文庫　圖書卡 60192",
        "網址": "https://www.aozora.gr.jp/cards/001538/card60192.html",
        "文字遣い": "新字新假名",
        "著作權": "作者 1961 年歿，日本已逾保護期間，青空文庫公開。",
    },
    "shukou": {
        "作者": "矢內原忠雄（1893–1961）", "作品": "帝大聖書研究会終講の辞",
        "初出": "「嘉信 第一巻第三号」1938（昭和 13）年 3 月",
        "底本": "『日本の名随筆 別巻 100 聖書』（親本：『民族と平和 キリスト者の信仰Ⅴ』）",
        "電子文本": "青空文庫　圖書卡 52208",
        "網址": "https://www.aozora.gr.jp/cards/001538/card52208.html",
        "文字遣い": "新字新假名",
        "著作權": "作者 1961 年歿，日本已逾保護期間，青空文庫公開。",
    },
    "denmark": {
        "作者": "內村鑑三（1861–1930）", "作品": "デンマルク国の話――信仰と樹木とをもって国を救いし話",
        "初出": "「聖書之研究 第一三六号」1911（明治 44）年",
        "底本": "『後世への最大遺物・デンマルク国の話』（親本：『內村鑑三全集』第一四卷）",
        "電子文本": "青空文庫　圖書卡 233",
        "網址": "https://www.aozora.gr.jp/cards/000034/card233.html",
        "文字遣い": "新字新假名",
        "著作權": "作者 1930 年歿，日本已逾保護期間，青空文庫公開。",
    },
    "isan": {
        "作者": "內村鑑三（1861–1930）", "作品": "後世への最大遺物",
        "初出": "「湖畔論集 第六回夏期学校編」十字屋書店、1894（明治 27）年 11 月",
        "底本": "『後世への最大遺物・デンマルク国の話』（親本：『內村鑑三全集』第一卷）",
        "電子文本": "青空文庫　圖書卡 519",
        "網址": "https://www.aozora.gr.jp/cards/000034/card519.html",
        "文字遣い": "新字新假名（惟序文本身即文語體，與假名遣無關）",
        "著作權": "作者 1930 年歿，日本已逾保護期間，青空文庫公開。",
    },
    "bungo": {
        "作者": "—（日本聖書協會譯定，譯者不具名）", "作品": "文語訳聖書　マタイ伝福音書",
        "初出": "新約：1917（大正 6）年「大正改訳」／舊約：1887（明治 20）年",
        "底本": "文語訳新約聖書（大正改訳）",
        "電子文本": "維基文庫（ja.wikisource.org）",
        "網址": "https://ja.wikisource.org/wiki/マタイ伝福音書(文語訳)",
        "文字遣い": "舊字舊假名．全文附振假名",
        "著作權": "公有領域。無教會諸人引用的即此譯本，不以口語訳或新共同訳頂替。",
    },
}

RUBY = re.compile(r"（[ぁ-ゖァ-ヺー、・]+）")


def net_len(text: str) -> int:
    """實質字數：扣掉振假名與 markdown 記號。文語訳不扣會高估一倍。"""
    t = RUBY.sub("", text)
    t = re.sub(r"[*#>\-\s]", "", t)
    return len(t)


def read_aozora(work_id: str) -> str:
    with open(os.path.join(AOZORA, f"{work_id}.txt"), encoding="utf-8", errors="replace") as f:
        return f.read()


def read_scripture(name: str) -> str:
    with open(os.path.join(SCRIPTURE, name), encoding="utf-8", errors="replace") as f:
        return f.read()


def between(text: str, start_pat: str, end_pat: str | None) -> str:
    i = re.search(start_pat, text, re.M)
    if not i:
        raise KeyError(f"找不到起點 {start_pat}")
    j = re.search(end_pat, text[i.end():], re.M) if end_pat else None
    return text[i.start(): i.end() + j.start()] if j else text[i.start():]


def paras(text: str) -> list[str]:
    return [p.strip() for p in text.splitlines() if p.strip()]


def fit(ps: list[str], lo: int, target: int) -> tuple[str, int, int]:
    """從第 lo 段起，取到實質字數達 target 為止。

    回傳 (內文, 結束段索引(不含), 實質字數)。段落區間會寫進讀本檔，
    上下篇有沒有疊到肉眼就看得出來。
    """
    i, run = lo, 0
    while i < len(ps) and run < target:
        run += net_len(ps[i])
        i += 1
    if i == lo:
        raise KeyError(f"從第 {lo} 段取不到東西")
    return "\n\n".join(ps[lo:i]), i, run


def verses(chapter_text: str, lo: int, hi: int) -> str:
    """文語訳快取是「1本文2本文3本文…」連寫，依節號切開再取範圍。"""
    body = chapter_text.split("\n", 2)[-1]
    parts = re.split(r"(?<![０-９0-9])(\d{1,3})(?=[^\d])", body)
    got, cur = [], None
    for k, seg in enumerate(parts):
        if k % 2 == 1:
            cur = int(seg)
        elif cur is not None and lo <= cur <= hi:
            got.append(f"**{cur}**　{seg.strip()}")
    if not got:
        raise KeyError(f"切不出第 {lo}-{hi} 節")
    return "\n\n".join(got)


# 每週實質字數目標。起步三百字，期末約七百，不是「讀完一篇」。
TARGET = {3: 300, 4: 350, 5: 400, 7: 450, 10: 500, 11: 700, 12: 550, 13: 650}


def build_readings() -> dict[int, list[dict]]:
    nyumon = read_aozora("060192")
    denmark = paras(read_aozora("000233"))
    isan = paras(read_aozora("000519"))
    shukou = paras(read_aozora("052208"))
    mt5 = read_scripture("マタイ伝福音書_第五章__文語訳_.txt")
    mt6 = read_scripture("マタイ伝福音書_第六章__文語訳_.txt")

    jo = paras(between(nyumon, r"^序$", r"^第一章"))
    ch1 = paras(between(nyumon, r"^第一章　人生と宗教", r"^第二章"))
    ch2 = paras(between(nyumon, r"^第二章　いかにしてキリスト教を学ぶか", r"^第三章"))

    def whole(ps):
        return sum(net_len(p) for p in ps)

    r: dict[int, list[dict]] = {}

    t, e, n = fit(jo, 0, TARGET[3])
    r[3] = [dict(stem="矢內原忠雄_キリスト教入門_序", title="矢內原忠雄《キリスト教入門》序",
                 src="nyumon", extent=f"全書序（共 {len(jo)} 段／約 {whole(jo)} 字）之第 1–{e} 段",
                 net=n, body=t)]

    t, e1, n = fit(ch1, 0, TARGET[4])
    r[4] = [dict(stem="矢內原忠雄_キリスト教入門_第一章上", title="矢內原忠雄《キリスト教入門》第一章　人生と宗教（上）",
                 src="nyumon", extent=f"第一章（共 {len(ch1)} 段／約 {whole(ch1)} 字）之第 1–{e1} 段",
                 net=n, body=t)]
    t, e2, n = fit(ch1, e1, TARGET[5])
    r[5] = [dict(stem="矢內原忠雄_キリスト教入門_第一章下", title="矢內原忠雄《キリスト教入門》第一章　人生と宗教（下）",
                 src="nyumon", extent=f"第一章之第 {e1 + 1}–{e2} 段（接續上週，不重疊）",
                 net=n, body=t)]

    body = verses(mt5, 1, 12)
    r[6] = [dict(stem="文語訳_マタイ伝五章_八福", title="文語訳聖書　マタイ伝福音書 第五章 1–12（八福）",
                 src="bungo", extent="第五章第 1–12 節（全章 48 節）", net=net_len(body), body=body)]

    t, _, n = fit(ch2, 0, TARGET[7])
    r[7] = [dict(stem="矢內原忠雄_キリスト教入門_第二章", title="矢內原忠雄《キリスト教入門》第二章　いかにしてキリスト教を学ぶか",
                 src="nyumon", extent=f"第二章（共 {len(ch2)} 段／約 {whole(ch2)} 字）開頭",
                 net=n, body=t)]

    body = verses(mt6, 5, 15)
    r[8] = [dict(stem="文語訳_マタイ伝六章_主の祈り", title="文語訳聖書　マタイ伝福音書 第六章 5–15（主の祈り）",
                 src="bungo", extent="第六章第 5–15 節（全章 34 節）", net=net_len(body), body=body)]

    # デンマルク：全篇 43 段約 9,000 字，N5 兩週讀不完。取「導入」與「結論三教訓」
    # 兩塊精讀；中間ダルガス植林敘事留作行有餘力再讀。
    t, e, n = fit(denmark, 12, TARGET[10])
    r[10] = [dict(stem="內村鑑三_デンマルク国の話_導入", title="內村鑑三《デンマルク国の話》導入",
                  src="denmark", extent=f"全篇 43 段（約 {whole(denmark)} 字）之第 13–{e} 段",
                  net=n, body=t)]
    t, e, n = fit(denmark, 34, TARGET[11])
    r[11] = [dict(stem="內村鑑三_デンマルク国の話_結論", title="內村鑑三《デンマルク国の話》結論——三つの教訓",
                  src="denmark", extent=f"全篇 43 段之第 35–{e} 段（中段植林敘事本週不列入精讀）",
                  net=n, body=t)]

    t, e1, n = fit(shukou, 2, TARGET[12])
    r[12] = [dict(stem="矢內原忠雄_帝大聖書研究会終講の辞_上", title="矢內原忠雄〈帝大聖書研究会終講の辞〉（上）",
                  src="shukou", extent=f"全篇 {len(shukou)} 段（約 {whole(shukou)} 字）之第 3–{e1} 段",
                  net=n, body=t)]
    t, e2, n = fit(shukou, e1, TARGET[13])
    r[13] = [dict(stem="矢內原忠雄_帝大聖書研究会終講の辞_下", title="矢內原忠雄〈帝大聖書研究会終講の辞〉（下）",
                  src="shukou", extent=f"全篇之第 {e1 + 1}–{e2} 段（接續上週，不重疊）",
                  net=n, body=t)]

    # 《後世への最大遺物》文體分界（段落索引，逐段核對過，不可用字數推）：
    #   2–7   はしがき（1897）                  → 文語體
    #   8–12  再版に附する序言（1899）          → 文語體
    #   13–17 改版に附する序（1925）＋標題      → 已是口語，本計畫不用
    #   18–   夏期演説 第一回                    → 口語講演體
    bungo_part = "\n\n".join(isan[2:8])
    kougo_part = "\n\n".join(isan[18:22])
    r[14] = [
        dict(stem="內村鑑三_後世への最大遺物_序_文語", title="內村鑑三《後世への最大遺物》はしがき〔文語體〕",
             src="isan", extent="全書第 3–8 段（1897 年序，全篇約 38,500 字）",
             net=net_len(bungo_part), body=bungo_part),
        dict(stem="內村鑑三_後世への最大遺物_講演冒頭_口語", title="內村鑑三《後世への最大遺物》夏期演説 第一回 冒頭〔口語體〕",
             src="isan", extent="全書第 19–22 段（1894 年講演本體開頭）",
             net=net_len(kougo_part), body=kougo_part),
    ]
    return r


def source_block(key: str, extent: str, net: int) -> str:
    s = SRC[key]
    return "\n".join([
        "## 出處", "",
        f"- **作者**：{s['作者']}",
        f"- **作品**：{s['作品']}",
        f"- **初出**：{s['初出']}",
        f"- **底本**：{s['底本']}",
        f"- **電子文本**：{s['電子文本']}",
        f"- **網址**：{s['網址']}",
        f"- **文字遣い**：{s['文字遣い']}",
        f"- **著作權狀態**：{s['著作權']}", "",
        "## 本週讀量", "",
        f"- **節錄範圍**：{extent}",
        f"- **實質字數**：約 {net} 字（已扣振假名）",
    ])


def plan_text(readings: dict[int, list[dict]]) -> str:
    rows = []
    labels = {
        1: ("目標設定、程度診斷", "—", "—", "—"),
        2: ("五十音鞏固；宗教學基本語彙 60 字", "—", "自製字表", "60 字"),
        9: ("**期中檢視**：口頭三分鐘說明「無教会とは何か」", "—", "—", "—"),
        15: ("**期末成果**：自選文獻逐詞注解＋繁中翻譯", "—", "自選", "約 500 字"),
    }
    track = {
        3: ("**繳交本計畫**；名詞句・指示詞・は/が/を/に", "—"),
        4: ("動詞ます形・て形", "—"),
        5: ("形容詞・過去形・否定", "—"),
        6: ("—", "**文語起步**：口語／文語對照；斷定「なり」"),
        7: ("授受・可能・意向", "打消「ず」・連體形"),
        8: ("—", "過去「き・けり」／完了「つ・ぬ・たり・り」"),
        10: ("講演體「〜であります」", "係り結び（ぞ・なむ・や・か・こそ）"),
        11: ("長句拆解・接續詞", "推量「む・べし」"),
        12: ("論說文讀法", "敬語（給ふ・侍り）基礎"),
        13: ("1937 年被迫辭去東大教職的脈絡", "形容詞ク／シク活用"),
        14: ("—", "**文語與口語並排**：同一作者兩種文體"),
    }
    for w in range(1, 16):
        if w in labels:
            a, b, c, d = labels[w]
            rows.append(f"| {w:02d} | {a} | {b} | {c} | {d} |")
            continue
        a, b = track[w]
        items = readings.get(w, [])
        c = "＋".join(i["title"].split("》")[-1] or i["title"] for i in items) if items else "—"
        c = "＋".join(i["title"] for i in items)
        total = sum(i["net"] for i in items)
        rows.append(f"| {w:02d} | {a} | {b} | {c} | 約 {total} 字 |")
    table = "\n".join(rows)

    return f"""# 個人課程目標與十五週自學計畫

**課程**：115-1 初階宗教學日文文獻選讀（BBA224，倪杰老師）
**學生**：張辰瑋（宗教與文化學系博士班一年級）
**起點**：日文 N5（五十音已識，基礎文法未成形）

## 一、為什麼選這個目標

我的博士研究以比較宗教史為方法，其中一條軸線是日本的**無教會主義**
（內村鑑三—矢內原忠雄—藤井武—塚本虎二一系）及其與台灣的關聯。
這批文獻至今絕大多數沒有中譯，研究者必須直接讀日文原典。

本課程既然採「依個人程度客製化自學」，我把個人目標定為：

> **在十五週內，從 N5 起步，做到能借助辭典逐句讀懂矢內原忠雄的現代日文散文，
> 並能辨認文語體的核心語法，讀懂附振假名的文語訳聖書。**

這不是「學會日文」，是**為讀特定一批文獻，把最短路徑走通**。

## 二、為什麼要分兩軌

盤點過這批文獻的實際文體之後，發現它不是單一難度：

| 文獻 | 年代 | 文體 | 難度 |
|---|---|---|---|
| 矢內原忠雄《キリスト教入門》 | 1952 | 現代日文．新字新假名．「である」體 | 可及 |
| 矢內原忠雄《イエス伝》 | 1940 | 現代日文 | 可及 |
| 矢內原忠雄〈帝大聖書研究会終講の辞〉 | 1938 初出 | 現代口語＋舊詞（「居り」「此の」） | 中 |
| 內村鑑三《デンマルク国の話》 | 1911 | 講演口語「〜であります」 | 中 |
| 內村鑑三《後世への最大遺物》 | 1894 | 序＝文語，講演本體＝口語 | 中／難 |
| 內村鑑三《聖書の読方》 | 講演 | 漢文訓讀調（「於て」「而して」） | 難 |
| 內村鑑三《基督信徒のなぐさめ》 | 1893 | **文語體** | 難 |
| 文語訳聖書（1887／1917） | — | **純文語** | 難 |

結論很清楚：**矢內原是現代日文，內村的著作是文語**。而無教會的原始文獻與
他們自己引用的聖經都在文語那一側，所以文語不能等到「日文學好了再說」，
必須從學期中段就開始練。

因此本計畫分兩軌並行：

- **主線（W03 起）現代日文**：矢內原忠雄。把基礎文法與宗教學詞彙一次到位。
- **副線（W06 起）文語入門**：**先讀附振假名的文語訳聖書**——漢字讀音不必查，
  剩下的難度只剩文法；而且經文內容我本來就熟，等於現成的可理解輸入。
  熟了之後再轉進內村的文語。

W14 刻意把內村同一本書的「文語序」與「口語講演」並排讀，看清兩種文體的分界線。

## 三、讀量怎麼定

N5 的精讀不是「讀完一篇」，是「讀懂一段」。所以每週給的是**實質字數**——
總字數扣掉振假名。文語訳聖書每個漢字都注了假名，「幸福（さいはひ）なるかな」
表面 12 字、實質只有 7 字，不扣就會把讀量高估一倍。

級距：W03–05 三百到四百字（剛起步，逐詞查）→ W06–08 四百到五百（文語但有振假名，
內容又熟）→ W10–13 五百到七百（講演體長句）→ W14 兩篇合計約九百（文體對照）。
**一週只讀一節或幾段，不求讀完整篇**；各篇全長另標在讀本檔裡，行有餘力再往下讀。

## 四、十五週進度

| 週 | 主線（現代日文） | 副線（文語） | 讀本 | 讀量 |
|---|---|---|---|---|
{table}

## 五、每週固定作業

1. **讀本**：當週指定範圍，逐句標注不懂的詞，查完寫進個人詞表。
2. **討論區貼文**：用日文寫 3–5 句心得（W03 起；容許大量錯誤，重點是產出）。
3. **口說**：每日 10 分鐘與 AI 語言教練對話，題材限宗教學／宗教史。
4. **單字**：每週 40 字，用印刷字卡複習。

## 六、成果檢核（W15 自評用）

- [ ] 能在不看中譯的情況下，讀懂矢內原《キリスト教入門》任一節的大意。
- [ ] 能辨認並說出文語的十二個核心形態（なり・たり・ず・き・けり・つ・ぬ・
      たり・り・む・べし・係り結び）。
- [ ] 能讀懂附振假名的文語訳聖書一章。
- [ ] 個人詞表累積 500 條以上，其中宗教學專門語彙不少於 150 條。
- [ ] 能用日文寫出 300 字的「無教会主義とは何か」短文。

## 七、讀本出處

各週讀本檔案皆附完整出處欄（作者、初出、底本、電子文本、網址、文字遣い、
節錄範圍、實質字數、著作權狀態）。總表如下：

| 讀本 | 初出 | 底本 | 電子文本 |
|---|---|---|---|
| 矢內原忠雄《キリスト教入門》 | 角川新書，1952 年 11 月 11 日 | 『キリスト教入門』 | 青空文庫 60192 |
| 矢內原忠雄〈帝大聖書研究会終講の辞〉 | 《嘉信》第一卷第三號，1938 年 3 月 | 『日本の名随筆 別巻100 聖書』（親本《民族と平和》） | 青空文庫 52208 |
| 內村鑑三《デンマルク国の話》 | 《聖書之研究》第一三六號，1911 年 | 『後世への最大遺物・デンマルク国の話』（親本《內村鑑三全集》一四卷） | 青空文庫 233 |
| 內村鑑三《後世への最大遺物》 | 《湖畔論集 第六回夏期学校編》十字屋書店，1894 年 11 月 | 同上（親本《內村鑑三全集》一卷） | 青空文庫 519 |
| 文語訳聖書 マタイ伝福音書 | 大正改訳新約，1917 年 | 文語訳新約聖書 | 維基文庫 |

著作權：內村鑑三 1930 年歿、矢內原忠雄 1961 年歿，日本均已逾保護期間；
文語訳聖書為公有領域。全部取自公開電子文本，未使用任何仍受保護的譯本。

---

由 `scripts/japanese_self_study_plan.py` 產生；改計畫後重跑。
"""


def main() -> None:
    readings = build_readings()
    plan = plan_text(readings)

    os.makedirs(DEST, exist_ok=True)
    write_html(os.path.join(DEST, "個人課程目標_十五週計畫.html"),
               "個人課程目標與十五週自學計畫", plan)
    print("✓ 個人課程目標_十五週計畫.html")

    w3 = os.path.join(DEST, WEEK_DIRS[3])          # W03 的作業就是繳交這份計畫
    os.makedirs(w3, exist_ok=True)
    write_html(os.path.join(w3, "個人課程目標_十五週計畫.html"),
               "個人課程目標與十五週自學計畫", plan)

    n = 0
    for week, items in sorted(readings.items()):
        d = os.path.join(DEST, WEEK_DIRS[week])
        os.makedirs(d, exist_ok=True)
        for it in items:
            dst = os.path.join(d, f"W{week:02d}_自訂_{it['stem']}.html")
            write_html(dst, it["title"],
                       f"# {it['title']}\n\n"
                       f"> 自訂讀本——本課程為個別化自學，讀本由學生依個人目標自選。\n\n"
                       f"{source_block(it['src'], it['extent'], it['net'])}\n\n"
                       f"---\n\n## 本文\n\n{it['body']}\n")
            n += 1
            print(f"  ✓ W{week:02d} {it['title'][:40]}　實質 {it['net']} 字")
    print(f"\n讀本 {n} 篇")


if __name__ == "__main__":
    main()
