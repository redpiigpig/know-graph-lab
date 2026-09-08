# -*- coding: utf-8 -*-
"""《大家的日本語》1–50 課的自學索引：各課文型、單字數、免費中文講解。

只對課本，不牽讀本——讀本課次是另一件事，混在同一張表裡兩邊都看不清楚。

  單字數     來自 output/source-cache/original-readers/japanese-full/minna-lesson-order.json
             （u-biq 逐課頁重建的課本詞序，2,043 詞）。那是第三方對課本順序的整理、
             不是課本本身，數字當量感參考可以，當清點依據不行。

  文型       按標準大綱寫的，不是從課本 OCR 來的。初版與第二版的文型幾乎一致，但
             編者換過例句，所以這欄當索引用可以，當課本用不行。

  外部連結   一律「已驗證的目錄頁」或「決定性的搜尋網址」，不放猜出來的單篇網址。
             時雨の町的文法頁是 /learn-japanese/grammar/{n5,n4}/NN，但那個 NN 是
             時雨自己按品詞排的序號，跟課次沒有對應關係，硬編會全錯位。
             王可樂的文法那套標題格式固定（【改訂版】大家的日本語NN課文法解說），
             單字那套標題卻不統一（有「第N課單字」也有「初階1 第N課 單字」），
             所以單字欄用關鍵字搜、不用精確標題。逐支影片 id 猜不出來，兩邊都走搜尋。

    python -X utf8 scripts/build_japanese_study_crosswalk.py
"""
from __future__ import annotations

import collections
import html
import json
import os
import sys
import urllib.parse

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MINNA = os.path.join(ROOT, "output", "source-cache", "original-readers",
                     "japanese-full", "minna-lesson-order.json")
OUT_JSON = os.path.join(ROOT, "output", "japanese-study-crosswalk.json")

# Drive 上的個人日語學習夾（底下原本放《大家的日本語1》的 CD 音檔）。
# 成品照 repo-hygiene 規矩落 Drive、不進 git。
DRIVE_DEST = r"G:\我的雲端硬碟\資料\語言\日語"
DRIVE_NAME = "大家的日本語進度對照表.html"

SIGURE_HOME = "https://www.sigure.tw/"
KOLA_GRAMMAR_PLAYLIST = "https://www.youtube.com/playlist?list=PLynCeSdpMqxCW-AfMtmIlASAMUVq8wX6k"
VOCAB_PLAYLIST = "https://www.youtube.com/playlist?list=PLfj-oWcHWI3DNRMp5KkS0Bdkz0O2-K1gw"

# 課本各課文型。key = 課本課次；jp 是文型本身，zh 是一句話說明，terms 是拿去查
# 時雨の町的關鍵字（用日文文法術語查中文站，命中率比查中文說法高）。
SYLLABUS: dict[int, dict] = {
    1: dict(jp="〜は〜です／〜じゃありません／〜も／〜の", zh="名詞判斷句。自我介紹、國籍、職業。", terms=["は です", "名詞 主題"]),
    2: dict(jp="これ／それ／あれ、この／その／あの＋N", zh="指示詞（物）與所有格の。", terms=["これ それ あれ", "指示詞"]),
    3: dict(jp="ここ／そこ／あそこ、〜はどこですか、いくら", zh="指示詞（場所）、問價錢。", terms=["ここ そこ あそこ", "場所 指示"]),
    4: dict(jp="〜時〜分、動詞ます形の時制、〜から〜まで", zh="時間表達與動詞四種時制。**動詞第一次登場**。", terms=["ます形", "動詞 時制"]),
    5: dict(jp="〜へ行きます、〜で（交通手段）、〜と（同行）", zh="移動動詞與助詞へ／で／と。", terms=["へ 助詞", "で 手段"]),
    6: dict(jp="〜を＋他動詞、〜で（動作場所）、〜ませんか／〜ましょう", zh="受格を、邀約與提議。", terms=["を 助詞", "ませんか ましょう"]),
    7: dict(jp="〜で（道具）、あげます／もらいます、もう〜ました", zh="工具格與授受動詞初階。", terms=["あげます もらいます", "授受動詞"]),
    8: dict(jp="い形容詞・な形容詞", zh="兩類形容詞的述語與修飾用法。**中文母語者第一個大坑**。", terms=["い形容詞 な形容詞", "形容詞 修飾"]),
    9: dict(jp="〜がわかります／すきです、〜から（原因）", zh="好惡與能力用が，原因用から。", terms=["が 助詞 好き", "から 原因"]),
    10: dict(jp="あります／います、〜に〜があります", zh="存在句與位置名詞。有生／無生分兩個動詞。", terms=["あります います", "存在文"]),
    11: dict(jp="助数詞、数量詞の位置、〜に〜回", zh="量詞系統與數量詞在句中的位置。", terms=["助数詞", "数量詞"]),
    12: dict(jp="名詞・形容詞の過去形、比較（より／のほうが／いちばん）", zh="形容詞過去式與三種比較句。", terms=["形容詞 過去形", "より のほうが"]),
    13: dict(jp="〜がほしいです、〜たいです、〜に行きます（目的）", zh="欲求表達。ほしい接名詞、たい接動詞。", terms=["たい ほしい", "に行きます 目的"]),
    14: dict(jp="て形、〜てください、〜ています（進行）", zh="**て形**。全書最重要的一課，後面一半的句型都靠它。", terms=["て形", "て形 変化"]),
    15: dict(jp="〜てもいいです、〜てはいけません、〜ています（狀態）", zh="許可與禁止；ています的第二個用法。", terms=["てもいい てはいけない", "ている 状態"]),
    16: dict(jp="て形接續、〜てから、〜は〜が〜", zh="用て形串句子；大主題小主語雙重主語句。", terms=["てから", "は が 二重主語"]),
    17: dict(jp="ない形、〜ないでください、〜なければなりません", zh="**ない形**。義務與不必要。", terms=["ない形", "なければならない"]),
    18: dict(jp="辞書形、〜ことができます、〜まえに", zh="**辞書形**。名詞化こと的第一步。", terms=["辞書形", "ことができる"]),
    19: dict(jp="た形、〜たことがあります、〜たり〜たり", zh="**た形**。經驗與列舉。四大變形到此收齊。", terms=["た形", "たことがある"]),
    20: dict(jp="普通形（常体）", zh="敬體↔常體轉換。**讀書面文獻的分水嶺**——書上寫的全是常體。", terms=["普通形", "常体 敬体"]),
    21: dict(jp="〜と思います、〜と言いました、〜でしょう？", zh="引用節。意見與轉述。", terms=["と思う", "と言う 引用"]),
    22: dict(jp="名詞修飾節（連体修飾）", zh="**用整個句子修飾名詞**。中文沒有對應結構，讀長句非過不可。", terms=["連体修飾", "名詞修飾節"]),
    23: dict(jp="〜とき、〜と（條件）、〜を（通過）", zh="時間從句與自然條件。", terms=["とき", "と 条件"]),
    24: dict(jp="くれます、〜てあげます／〜てもらいます／〜てくれます", zh="授受動詞全系統。日語的「視點」概念在此。", terms=["てあげる てもらう てくれる", "授受表現"]),
    25: dict(jp="〜たら、〜ても", zh="條件與逆接。初級 I 收尾。", terms=["たら", "ても 逆接"]),
    26: dict(jp="〜んです（説明）、〜ていただけませんか", zh="說明語氣んです。初級 II 開始。", terms=["んです のです", "ていただけませんか"]),
    27: dict(jp="可能動詞、見えます／聞こえます、しか〜ません", zh="可能形與自發感知動詞。", terms=["可能動詞", "見える 聞こえる"]),
    28: dict(jp="〜ながら、〜し（並列）、〜ています（習慣）", zh="同時動作與並列理由。", terms=["ながら", "し 並列"]),
    29: dict(jp="自動詞＋ています、〜てしまいます", zh="**自他動詞對立**。結果狀態與完了／遺憾。", terms=["自動詞 他動詞", "てしまう"]),
    30: dict(jp="〜てあります、〜ておきます", zh="有意圖的結果狀態與事前準備。", terms=["てある", "ておく"]),
    31: dict(jp="意向形、〜ようと思っています、〜つもりです", zh="意志形與計畫表達。", terms=["意向形", "つもり 予定"]),
    32: dict(jp="〜たほうがいいです、〜でしょう、〜かもしれません", zh="建議與推測。確信度階梯。", terms=["ほうがいい", "かもしれない"]),
    33: dict(jp="命令形・禁止形、〜と書いてあります", zh="命令與禁止形。**讀告示、標語、引文用**。", terms=["命令形", "禁止形"]),
    34: dict(jp="〜とおりに、〜あとで、〜ないで", zh="依照、順序、附帶狀況。", terms=["とおりに", "ないで"]),
    35: dict(jp="条件形ば、〜なら、〜ば〜ほど", zh="ば條件形。**文語條件句的近親，讀舊文獻會遇到**。", terms=["ば 条件形", "なら"]),
    36: dict(jp="〜ように（目的）、〜ようになります", zh="目的與能力／習慣的變化。", terms=["ように 目的", "ようになる"]),
    37: dict(jp="受身形（被動）、〜によって", zh="**被動態**。學術文章的骨幹句型，出現率極高。", terms=["受身形", "受動態"]),
    38: dict(jp="〜のが好きです、〜のは〜です", zh="形式名詞の的名詞化。抽象論述必備。", terms=["の 名詞化", "のは のが"]),
    39: dict(jp="〜て（原因）、〜ので、〜のに", zh="三種因果與逆接。ので比から書面。", terms=["ので から 違い", "のに 逆接"]),
    40: dict(jp="〜かどうか、〜てみます、疑問詞＋か", zh="嵌入疑問句。", terms=["かどうか", "てみる"]),
    41: dict(jp="授受の敬語（いただきます／くださいます／やります）", zh="授受動詞的敬語層。**敬語系統起點**。", terms=["いただく くださる", "授受 敬語"]),
    42: dict(jp="〜ために（目的）、〜のに（用途）", zh="目的與用途。ために在論文裡到處都是。", terms=["ために 目的", "のに 用途"]),
    43: dict(jp="〜そうです（樣態）、〜てきます", zh="外觀推測與方向補助動詞。", terms=["そうです 様態", "ていく てくる"]),
    44: dict(jp="〜すぎます、〜やすい／〜にくい、〜くします", zh="程度過度與難易度。", terms=["すぎる", "やすい にくい"]),
    45: dict(jp="〜場合は、〜のに（逆接）", zh="場合假設與強逆接。法規、條文常見。", terms=["場合は", "のに 逆接"]),
    46: dict(jp="〜ところです、〜たばかり、〜はずです", zh="時間點的細緻區分與理應如此。", terms=["ところです", "はず"]),
    47: dict(jp="〜そうです（傳聞）、〜ようです（推量）", zh="**傳聞與推量**。學術寫作區分資訊來源靠這組。", terms=["そうです 伝聞", "ようです 推量"]),
    48: dict(jp="使役形、〜させてください", zh="使役態。與被動合成使役被動是下一階。", terms=["使役形", "させてください"]),
    49: dict(jp="尊敬語（〜れます、お〜になります）", zh="**尊敬語**。抬高對方。", terms=["尊敬語", "お になる"]),
    50: dict(jp="謙譲語（お〜します）、丁寧語（〜でございます）", zh="**謙譲語・丁寧語**。敬語三層到此完整。全書終。", terms=["謙譲語", "丁寧語"]),
}

# 階段分組：起訖課本課次、標題、這一段在幹嘛。
STAGES = [
    (1, 3, "名詞句", "還沒碰動詞。純粹是「這是什麼、在哪裡、多少錢」。走得很快。"),
    (4, 13, "動詞 ます 形與助詞", "動詞以 ます 形整塊出現，不變形。真正要花時間的是**助詞**（は・が・を・に・で・へ・と），中文母語者的主要失分區。"),
    (14, 19, "動詞四大變形", "て形・ない形・辞書形・た形。**全書最陡的一段**，六課學完四種變形，後面 30 課全部建在上面。慢下來，寧可多花一倍時間。"),
    (20, 25, "常體與複句", "第 20 課的普通形是讀寫的分水嶺——書上不寫 ます。第 22 課的連體修飾是讀長句的鑰匙。"),
    (26, 38, "表達擴張", "可能・被動・使役・名詞化。第 37 課被動態和第 38 課の名詞化，是學術日文出現頻率最高的兩個結構。"),
    (39, 50, "論述與敬語", "ので／のに／ために 這組連接詞，加上敬語三層。**做無教會文獻研究真正要用的就在這一段**。"),
]


def load_word_counts() -> dict[int, int]:
    """u-biq 重建的課本逐課詞數。缺課就停，不要靜默出半張表。"""
    with open(MINNA, encoding="utf-8") as f:
        data = json.load(f)
    counts = collections.Counter(w["lesson"] for w in data["words"])
    missing = [n for n in range(1, 51) if n not in counts]
    if missing:
        raise SystemExit(f"課本第 {missing} 課在 {os.path.basename(MINNA)} 裡沒有詞，先補來源再出表")
    return dict(counts)


def sigure_url(terms: list[str], lesson: int) -> str:
    level = "N5" if lesson <= 25 else "N4"
    return "https://www.google.com/search?q=" + urllib.parse.quote(f"site:sigure.tw {level} {terms[0]}")


def grammar_video_url(lesson: int) -> str:
    """王可樂那套標題格式固定，用精確標題搜必中。"""
    return "https://www.youtube.com/results?search_query=" + urllib.parse.quote(
        f"【改訂版】大家的日本語{lesson:02d}課文法解說"
    )


def vocab_video_url(lesson: int) -> str:
    """單字那套標題不統一（「第N課單字」／「初階1 第N課 單字」），所以用關鍵字搜。"""
    return "https://www.youtube.com/results?search_query=" + urllib.parse.quote(
        f"大家的日本語 第{lesson}課 單字 みんなの日本語 単語"
    )


def build_rows(counts: dict[int, int]) -> list[dict]:
    rows = []
    for n in range(1, 51):
        s = SYLLABUS[n]
        rows.append(
            dict(
                lesson=n,
                level="N5" if n <= 25 else "N4",
                volume="初級 I" if n <= 25 else "初級 II",
                grammarJp=s["jp"],
                grammarZh=s["zh"],
                wordCount=counts[n],
                vocabVideo=vocab_video_url(n),
                grammarVideo=grammar_video_url(n),
                sigure=sigure_url(s["terms"], n),
            )
        )
    return rows


def stage_of(n: int) -> tuple:
    for st in STAGES:
        if st[0] <= n <= st[1]:
            return st
    raise KeyError(n)


def emphasise(text: str) -> str:
    """把 **…** 轉成 <strong>，其餘一律 escape。"""
    parts = text.split("**")
    out = []
    for i, p in enumerate(parts):
        p = html.escape(p)
        out.append(f"<strong>{p}</strong>" if i % 2 else p)
    return "".join(out)


def render_html(rows: list[dict], total_words: int) -> str:
    trs = []
    seen_stages = set()
    for r in rows:
        st = stage_of(r["lesson"])
        if st[0] not in seen_stages:
            seen_stages.add(st[0])
            trs.append(
                '<tr class="stage"><td colspan="6">'
                f'<span class="stage-range">第 {st[0]}–{st[1]} 課</span>'
                f'<span class="stage-title">{html.escape(st[2])}</span>'
                f'<span class="stage-note">{emphasise(st[3])}</span>'
                "</td></tr>"
            )
        trs.append(
            "<tr>"
            f'<td class="num"><span class="lesson">{r["lesson"]}</span>'
            f'<span class="level">{r["level"]}</span></td>'
            f'<td class="gram"><span class="jp">{html.escape(r["grammarJp"])}</span>'
            f'<span class="zh">{emphasise(r["grammarZh"])}</span></td>'
            f'<td class="wc">{r["wordCount"]}</td>'
            f'<td class="link"><a href="{r["vocabVideo"]}" target="_blank" rel="noopener">單字</a></td>'
            f'<td class="link"><a href="{r["grammarVideo"]}" target="_blank" rel="noopener">文法</a></td>'
            f'<td class="link"><a href="{r["sigure"]}" target="_blank" rel="noopener">時雨</a></td>'
            "</tr>"
        )
    body = "\n".join(trs)

    return f"""<title>大家的日本語進度表</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&family=Noto+Serif+JP:wght@500;600&display=swap">
<style>
  /* 配色取自原稿用紙：綠罫線的印刷綠、藁半紙的微綠白、老師批改用的朱筆紅。 */
  :root {{
    --bg:#f4f6f1; --card:#fdfdfb; --ink:#1b1e1a; --dim:#6a7264; --line:#dce3d5;
    --rule:#c3d2bb; --accent:#2e6b4d; --accent-soft:#e8efe6; --band:#eaf0e5; --shu:#a8452c;
  }}
  @media (prefers-color-scheme: dark) {{
    :root:not([data-theme="light"]) {{
      --bg:#141712; --card:#1c201b; --ink:#e7eae1; --dim:#959d8d; --line:#2e352b;
      --rule:#3d4738; --accent:#87c09a; --accent-soft:#222a23; --band:#232a21; --shu:#e0906f;
    }}
  }}
  :root[data-theme="dark"] {{
    --bg:#141712; --card:#1c201b; --ink:#e7eae1; --dim:#959d8d; --line:#2e352b;
    --rule:#3d4738; --accent:#87c09a; --accent-soft:#222a23; --band:#232a21; --shu:#e0906f;
  }}
  body {{ background:var(--bg); color:var(--ink);
    font:15px/1.7 "Noto Sans TC","PingFang TC","Microsoft JhengHei",system-ui,sans-serif; }}
  .wrap {{ max-width:960px; margin:0 auto; padding:44px 20px 88px; }}
  header {{ border-bottom:2px solid var(--rule); padding-bottom:18px; margin-bottom:26px; }}
  h1 {{ font-family:"Noto Serif JP","Noto Serif TC",serif; font-weight:600;
    font-size:28px; margin:0 0 8px; letter-spacing:.02em; text-wrap:balance; }}
  .sub {{ color:var(--dim); margin:0; font-size:14px; max-width:62ch; }}
  .legend {{ display:grid; gap:9px; background:var(--card); border:1px solid var(--line);
    border-left:3px solid var(--accent); padding:16px 18px; margin-bottom:28px; }}
  .legend p {{ margin:0; font-size:13.5px; color:var(--dim); }}
  .legend b {{ color:var(--ink); font-weight:700; }}
  .scroll {{ overflow-x:auto; -webkit-overflow-scrolling:touch;
    border:1px solid var(--line); background:var(--card); }}
  table {{ border-collapse:collapse; width:100%; min-width:640px; }}
  td, th {{ padding:12px 14px; border-bottom:1px solid var(--line); vertical-align:top; }}
  thead th {{ font-size:11px; font-weight:700; color:var(--dim); letter-spacing:.1em;
    text-align:left; border-bottom:1px solid var(--rule); padding-top:14px; padding-bottom:10px; }}
  thead th.c {{ text-align:center; }}
  tbody tr:last-child td {{ border-bottom:0; }}
  tr.stage td {{ background:var(--band); padding:15px 14px;
    border-top:1px solid var(--rule); border-bottom:1px solid var(--rule); }}
  .stage-range {{ font-family:"Noto Serif JP",serif; font-weight:600; font-size:12.5px;
    color:var(--accent); margin-right:11px; font-variant-numeric:tabular-nums; }}
  .stage-title {{ font-family:"Noto Serif JP","Noto Serif TC",serif;
    font-weight:600; font-size:16px; }}
  .stage-note {{ display:block; margin-top:6px; font-size:13px; color:var(--dim); line-height:1.65; }}
  /* 課次放進方框，取原稿用紙一字一格的マス。 */
  td.num {{ width:58px; text-align:center; }}
  .lesson {{ display:flex; align-items:center; justify-content:center;
    width:34px; height:34px; margin:0 auto; border:1px solid var(--rule);
    font-family:"Noto Serif JP",serif; font-size:17px; font-weight:600;
    font-variant-numeric:tabular-nums; }}
  .level {{ display:block; font-size:10px; color:var(--dim); letter-spacing:.1em; margin-top:5px; }}
  td.gram {{ min-width:300px; }}
  .jp {{ display:block; font-family:"Noto Serif JP",serif; font-weight:500;
    font-size:14.5px; line-height:1.55; }}
  .zh {{ display:block; color:var(--dim); font-size:13px; margin-top:4px; line-height:1.6; }}
  .zh strong, .stage-note strong {{ color:var(--shu); font-weight:700; }}
  td.wc {{ width:56px; text-align:center; color:var(--dim); font-size:13.5px;
    font-variant-numeric:tabular-nums; }}
  td.link {{ width:62px; text-align:center; }}
  td.link a {{ display:inline-block; padding:4px 10px; font-size:12px; text-decoration:none;
    color:var(--accent); border:1px solid var(--rule); background:transparent; }}
  td.link a:hover, td.link a:focus-visible {{ background:var(--accent-soft); border-color:var(--accent); }}
  a:focus-visible {{ outline:2px solid var(--accent); outline-offset:2px; }}
  .foot {{ margin-top:30px; font-size:13.5px; color:var(--dim); line-height:1.75; max-width:64ch; }}
  .foot a {{ color:var(--accent); }}
  .foot b {{ color:var(--ink); font-weight:700; }}
  .foot h2 {{ font-family:"Noto Serif JP","Noto Serif TC",serif; font-size:15px;
    font-weight:600; color:var(--ink); margin:24px 0 8px;
    padding-left:10px; border-left:3px solid var(--rule); }}
</style>
<div class="wrap">
  <header>
    <h1>《大家的日本語》1–50 課自學索引</h1>
    <p class="sub">各課文型、單字數，以及三個免費中文講解的直達入口。初級 I 是第 1–25 課（約 N5），初級 II 是第 26–50 課（約 N4）。</p>
  </header>

  <div class="legend">
    <p><b>單字</b>　<a href="{VOCAB_PLAYLIST}" target="_blank" rel="noopener">「大家的日本語【單字】／みんなの日本語【単語】」</a>逐課單字唸讀。該套標題格式不統一，所以用關鍵字搜。</p>
    <p><b>文法</b>　<a href="{KOLA_GRAMMAR_PLAYLIST}" target="_blank" rel="noopener">王可樂「【改訂版】大家的日本語文法解說」</a>該課影片。標題格式固定，必中。</p>
    <p><b>時雨</b>　<a href="{SIGURE_HOME}" target="_blank" rel="noopener">時雨の町</a>的站內搜尋（該課文法術語）。時雨按品詞編號、不按課次排，所以走搜尋而不是直接對號。</p>
  </div>

  <div class="scroll">
    <table>
      <thead><tr>
        <th class="c">課</th><th>文型</th><th class="c">單字</th>
        <th class="c" colspan="3">免費中文講解</th>
      </tr></thead>
      <tbody>{body}</tbody>
    </table>
  </div>

  <div class="foot">
    <h2>怎麼配速</h2>
    <p>一週一課 ≈ 一年走完 50 課；一週兩課 ≈ 半年，但<b>第 14–19 課那六課例外</b>，那是四大動詞變形，該慢就慢。真正的檢查點是第 20 課（常體）和第 22 課（連體修飾）——過了這兩課，日文書面文獻才開始「看得下去」。</p>

    <h2>文型這欄是索引，不是課本</h2>
    <p>文型按標準大綱整理，初版與第二版的<b>例句換過</b>。拿來定位「這課在講什麼」沒問題，實際句型還是以你手上那本為準。</p>

    <h2>單字數的來源</h2>
    <p>共 {total_words} 詞，來自 u-biq 逐課頁重建的課本詞序。那是<b>第三方對課本順序的整理，不是課本本身</b>；當量感參考可以，當清點依據不行。</p>
  </div>
</div>
"""


def wrap_standalone(doc: str) -> str:
    """包成可直接雙擊開啟的完整 HTML。

    artifact 版沒有 <!doctype>／<head>／<body>——那是發布時外面才包上去的。
    落到 Drive 當獨立檔就得自己補，尤其 charset：少了它中日文全變亂碼。
    """
    head, sep, body = doc.partition("</style>")
    if not sep:
        raise SystemExit("render_html 的結構變了（找不到 </style>），standalone 包裝要跟著改")
    return (
        '<!doctype html>\n<html lang="zh-Hant">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"{head}</style>\n"
        "<style>body{margin:0}img{max-width:100%}</style>\n"
        f"</head>\n<body>\n{body.strip()}\n</body>\n</html>\n"
    )


def main() -> None:
    counts = load_word_counts()
    rows = build_rows(counts)
    total_words = sum(r["wordCount"] for r in rows)
    doc = render_html(rows, total_words)

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(
            dict(
                note="《大家的日本語》1–50 課的文型、單字數與免費中文資源索引。文型欄為標準大綱整理，非課本原文。",
                source=dict(wordCounts="output/source-cache/original-readers/japanese-full/minna-lesson-order.json"),
                counts=dict(lessons=len(rows), words=total_words),
                rows=rows,
            ),
            f,
            ensure_ascii=False,
            indent=2,
        )

    html_path = os.path.join(os.environ.get("CROSSWALK_HTML_DIR", os.path.dirname(OUT_JSON)),
                             "japanese-study-crosswalk.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(doc)

    print(f"課本 {len(rows)} 課，單字合計 {total_words} 詞")
    print(f"JSON -> {OUT_JSON}")
    print(f"HTML（artifact 用，無 head）-> {html_path}")

    if os.path.isdir(DRIVE_DEST):
        drive_path = os.path.join(DRIVE_DEST, DRIVE_NAME)
        with open(drive_path, "w", encoding="utf-8") as f:
            f.write(wrap_standalone(doc))
        print(f"HTML（獨立檔，可雙擊）-> {drive_path}")
    else:
        print(f"！Drive 沒掛上（{DRIVE_DEST} 不存在），這輪沒出獨立檔")


if __name__ == "__main__":
    main()
