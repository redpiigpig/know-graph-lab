# -*- coding: utf-8 -*-
"""內村鑑三：只存在於岩波《內村鑑三全集》（1932–33）裡的單行著作 → ja＋繁中。

青空文庫沒有的作品（《求安錄》至今仍是「作業中」）只能從全集的轉錄文字取。
全集 20 卷已由 MinerU 轉錄入庫（`d0000001-…-0001`～`0020`，一頁一 chunk，
page_number＝PDF 頁序），本模組從中切出單一作品、清理、重建段落，交給
`uchimura_auto.py --author uchimura-zenshu` 翻譯與上架。

🚨 **MinerU 讀這套直排書的四種毛病**（2026-09-23 逐頁對原圖查過《求安錄》124 頁）：
  1. 直排裡**橫躺的英文詩句**整段丟掉，換成一大串 LaTeX（`\\begin{array}…`）。
  2. **章標題漏讀**——16 章裡有 6 章的標題不在文字裡。
  3. **同頁段落順序顛倒**（第 157、208 頁四段整個倒過來；202、224 頁兩段對調）。
  4. 行間的注音假名（ruby）被讀成獨立的一行（「まったう」「あらか」），著重點讀成「o o0」。
1 與 4 可以自動清；2 與 3 只能人工——這裡的 CHAPTERS 與 PAGE_FIX 就是對過原圖的結果。
頁碼換算成岩波版**印刷頁碼**（PDF 頁序 − 34，第一卷此段一致），引用時對得上紙本。

另一個來源試過不行：NDL 的 1893 年初版（pid 824178）官方 OCR 字錯得多（明治活字），
而且一張影像兩頁、章界落在影像中間，切出來章首夾前章、字數只剩岩波版七成。
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

SOURCE_LANG = "ja"
AUTHOR_ZH = "內村鑑三"
AUTHOR_EN = "Uchimura Kanzō"
CATEGORY = "神學"
DATA_DIRNAME = "uchimura_data"

ZENSHU_VOL1 = "d0000001-0000-4000-8000-000000000001"
PRINTED_OFFSET = 34          # 岩波全集第一卷：印刷頁 = PDF 頁序 − 34

REGISTRY: dict[str, dict] = {
    "kyuanroku": {
        "ebook_id": "d0000000-0000-4000-8000-000000000011",
        "title": "求安錄",
        "original_title": "求安録",
        "subtitle": "內村鑑三 1893（底本：岩波《內村鑑三全集》第一卷 1932，日文原文＋繁中對照）",
        "year": 1893,
        "parent_volume": "信仰三部作",
        "pages": (113, 236),   # PDF 頁序（含）
    },
}
QUEUE = ["kyuanroku"]
# 2026-09-23 NVIDIA 斷線時 run_queue 照樣印 QUEUE_COMPLETE，lane 退場、求安錄空著好幾段。
# 開嚴格判定：只有每段都有譯文（或零進展且引擎沒出錯）才算完成。
STRICT_COMPLETE = True

# (PDF 頁, 日文章名, 中譯章名, 切點)。切點：'top'＝該頁頁首；('find', 前綴)＝在以此前綴
# 開頭的段落之前；('drop', 前綴)＝該段就是 MinerU 讀到的章名行，丟掉並從下一段起算。
CHAPTERS = [
    (114, "卷頭", "卷首題詞", "top"),
    (117, "悲嘆", "悲嘆", ("drop", "悲嘆")),
    (119, "內心の分離", "內心的分裂", "top"),
    (129, "脫罪術其一　リバイバル", "脫罪術之一：奮興會", ("drop", "脫罪術其一")),
    (134, "脫罪術其二　學問", "脫罪術之二：學問", ("drop", "脫罪術其二")),
    (136, "脫罪術其三　自然の研究", "脫罪術之三：研究自然", ("drop", "脫罪術其三")),
    (138, "脫罪術其四　慈善事業", "脫罪術之四：慈善事業", ("drop", "脫罪術其四")),
    (146, "脫罪術其五　神學研究", "脫罪術之五：神學研究", ("find", "平安を慈善事業に於て")),
    (154, "忘罪術其一　「ホーム」", "忘罪術之一：「家庭」", "top"),
    (156, "忘罪術其二　利慾主義", "忘罪術之二：利慾主義", ("drop", "忘罪術其二")),
    (161, "忘罪術其三　オプチミスム（樂天教）附ユニテリヤン教並に「新神學」",
     "忘罪術之三：樂天教（附：一位論派與「新神學」）", "top"),
    (169, "罪の原理", "罪的原理", ("drop", "罪の原理")),
    (181, "喜の音", "喜訊", ("find", "失望暗夜")),
    (186, "信仰の解", "信仰之解", ("drop", "信仰の解")),
    (197, "樂園の回復", "樂園的回復", ("drop", "樂園の回復")),
    (214, "贖罪の哲理", "贖罪的哲理", "top"),
    (235, "最終問題", "最終問題", "top"),
]
PART_MARK = {117: "上の部", 169: "下の部"}   # 印在章名之前的部別（只作分隔，不成節）

# 逐頁人工校正（對過原圖）。項目：('find', 前綴)＝沿用清理後以此開頭的段落；
# ('lit', 文字)＝原圖轉錄。未列的頁照 MinerU 清理結果。
PAGE_FIX: dict[int, list] = {
    118: [("find", "我がルシラス"),
          ("lit", "と、人生を以て快樂と言ふものは誰ぞ、我に一日の虛日あるなし、關ケ原、ウオータルーは日々我わが心中に目撃する處なり。"),
          ("find", "會て聞く"),
          ("lit", "\"The unrest of this weary world is its unvoiced cry after God.\"—Munger."),
          ("lit", "我等神を得て始めて安し、世は最大幸福を求めつゝありて未だその最大幸福なるものは何たるを知らず、我等をして再びウェスレーの言を重復せしめよ、何物よりも善き事は神我等と共に在す事なり。")],
    143: [("find", "を學べり"),
          ("lit", "汝一度試みて成功せずんば二度試みよ、二度にて足らずんば百度試みよ、而して尙ほ汝の目的を達するを得ずんば二百度三百度四百度五百度試みよ、夫でだめなら一千度試みよ。"),
          ("find", "基督の言はる"), ("find", "慈善は天使の職")],
    145: [("find", "汝等人に見せん"), ("find", "鳴呼之れ今日"), ("find", "余は安心術"),
          ("lit", "Where wouldst thou fly? To works—to empty forms\nWith thy dove wings?\n"
                  "Will these give shelter from eternal storms—\nThese poor dead things?\n"
                  "And \"working\" answers with a voice severe,\n\"Turn back, mistaken soul! Rest is not here.\"\n"
                  "Henry Burton, in Sunday Magazine.")],
    146: [("lit", "羽翼あらば何處に飛ばんわが魂よ、\n事業へ乎、心よりせぬ事業へ乎。\n永久のあらしはこゝに吹かぬかや、\n"
                  "事業には、死せるうはべの事業には。\n恐るべき聲もて事業答へける、\nこゝになし、まどへる魂よこゝを去れ。"),
          ("lit", "ヘンリー、バートンの歌"),
          ("find", "平安を慈善事業に於て"), ("find", "凡そ世に嫌ふべき")],
    157: [("find", "ものなり、此理を"), ("find", "而して之れ理論"), ("find", "如斯"), ("find", "然り若し我をして")],
    160: [("find", "なし、ジェームス"), ("find", "ギボンは自身"),
          ("lit", "弄滑稽的の文字を以てせり、"), ("find", "と、哲學海に")],
    166: [("find", "以て徴すべきなり"), ("find", "神の慈悲のみに"),
          ("lit", "\"There is wideness in God's mercy\nLike the wideness of the sea.\""),
          ("lit", "神のなさけ　はかりなや\n海のひろきが　ごとくなり"),
          ("find", "とは宇宙神教主義"), ("find", "チャールス")],
    168: [("lit", "め最大希望を我等に充たすべしと宣言するものなり、われ基督教に由て未だ此完全に達する道を得ざればわれは未だ"
                  "基督教を解せざるものなり、基督信徒は大慾を抱かざる可らず、印度宣教師ウヰリヤム＝ケリー曰く、"
                  "Attempt great things for God, expect great things from God.（神の爲めに大事を計畫し、神より大事を望め）と、"
                  "我は人力の及ばざる大變動を我身に來たさんと欲するものなり。")],
    183: [("lit", "此救主とは誰ぞ"),
          ("lit", "\"The Lord who all our foes o'ercame,\nWorld, sin and death, and hell o'erthrew,\n"
                  "And Jesus is the Conqueror's name.\"—C. Wesley."),
          ("lit", "諸ての我等の敵に勝ち、\n陰府と世と死と罪とをば\nきり從へしものにして\nその名を耶穌と稱ふなり。"),
          ("lit", "彼は如何なる生涯に依て此世と我を救ひしや、"),
          ("lit", "われらが宣るところを信ぜしものは誰ぞや、エホバの手はたれにあらはれしや。\n"
                  "かれは主のまへに芽の如く、燥きたる土よりいづる樹株の如くそだちたり、\n"
                  "われらが見るべきうるはしき容なくうつくしき貌はなく、われらがしたふべき艷色なし。\n"
                  "かれは侮られて人にすてられ、悲哀の人にして病患を知れり、\n"
                  "また面をおほひて避くることをせらるゝ者のごとく侮られたり、われらも彼をたふとまざりき。")],
    199: [("find", "是ぞ天路歷程"), ("find", "我れ更に何を言はんや"),
          ("lit", "Just as I am without one plea,\nBut that thy blood was shed for me……"),
          ("lit", "われをばたのまじ　十字架にのぼりし\n耶蘇よびたまへば　我キリストにゆく"),
          ("find", "の歌を以て"), ("find", "罪人の長なる余も")],
    181: [("find", "他を愛するの念慮"), ("find", "失望暗夜"), ("find", "なんぢらの神")],
    202: [("find", "にまし"), ("find", "時に聲あり")],
    204: [("lit", "して曰く「汝憶病者よ、汝は汝の義務を果す能はざるか、神が汝に道德上の律を與へしは汝が之を實行するの力を有すればなり」西鄉隆盛言はずや、"),
          ("lit", "聖賢にならんと欲する志想古人の事蹟を見て迚も及ばぬと云ふ樣なる心は戰に臨んで逃ぐるより卑怯"),
          ("find", "と、基督教の贖罪論"),
          ("lit", "是を思ひ彼を思ひて余は尙ほ數年間神より獨立を維持せり、余は尙ほ余の領土を保ち應分の貢を納めて余の君主たるの權力を保存せり、"
                  "然れども窮迫は終に余をして此土奉還の策を講ぜざるを得ざるに至らしめたり、余の自負心に逆ひ、道義學者の嘲弄を省みず、"
                  "余は余一人の決心を以て余の身も靈も慾も望も愛も意志も悉く神に引渡せり、而して見よ余は始めて富めるものとなれり、"
                  "生命は得んと欲して失ひ失ひて而して得らる、余は余を捨てて始めて余を得たり、全身奉還の結果は領土十分の一の下賜に"
                  "あらずして神と宇宙と永遠とはその報として余に與へられたり。"),
          ("find", "奉還後の余の生涯")],
    208: [("find", "と、英國を改造し"), ("find", "基督の救に與かりてより"), ("find", "我の罪は免されたり"), ("find", "此主義に反對して")],
    224: [("find", "を踏まざらしむ"), ("find", "或人曰はむ")],
}

# ── 清理 ─────────────────────────────────────────────────────────────────
_LATEX = re.compile(r"\\begin\{array\}.*?\\end\{array\}|\$[^$\n]{0,400}\$", re.S)
_KANA_ONLY = re.compile(r"^[\u3040-\u30ffー・]{1,6}$")
_DOTS = re.compile(r"(?:(?<=\s)|^)[o0O°](?:\s+[o0O°\d(]{1,3})+[C)]*|[o0O]{2,}\d*")
_CJK = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff]")


def clean_page(text: str) -> list[str]:
    """一頁 MinerU 文字 → 段落（已去 LaTeX／ruby 行／著重點／孤立雜符）。"""
    text = _LATEX.sub("", text or "")
    blocks = []
    for raw in re.split(r"\n\s*\n", text):
        lines = []
        for ln in raw.split("\n"):
            s = _DOTS.sub("", ln).strip()
            # 注音假名自成一行（「まったう」「あらか」）要丟；但以助詞開頭的短行是接續上一頁的
            # 正文（第 202 頁「にまし」＝詩篇引文的行尾），不可當注音刪掉。
            if not s or (_KANA_ONLY.match(s) and s[0] not in "にをはがのでとへもやか"):
                continue
            if not _CJK.search(s) and len(re.findall(r"[A-Za-z]", s)) < 4:
                continue                     # 「201) –」「0 0 6」之類
            lines.append(s)
        if not lines:
            continue
        poem = len(lines) >= 2 and all(len(l) <= 24 for l in lines)
        if poem:
            blocks.append("\n".join(lines))
        else:
            out = lines[0]
            for l in lines[1:]:
                sep = " " if re.search(r"[A-Za-z,.;:!?]$", out) and re.match(r"[A-Za-z\"']", l) else ""
                out += sep + l
            blocks.append(out)
    return blocks


# ── 段落順序：拿 NDL 初版（824178）的版面 OCR 當對照 ─────────────────────
# MinerU 常把直排一頁的段落整個倒過來（第 142 頁六段完全逆序），光看文字抓不全
# （以助詞開頭的段才抓得到）。NDL 的 layouttext 照 ORDER 排、順序可靠但錯字多，
# 所以只拿它**定位**：每段取開頭 40 個漢字切成 6 字片段，在 NDL 全文裡找唯一命中，
# 取中位數當該段位置；同頁各段位置不遞增就照位置重排。
NDL_PID = "824178"
_NDL_TEXT: str | None = None


def _han(t: str) -> str:
    return re.sub(r"[^一-鿿]", "", t)      # 只比漢字：兩版假名 OCR 差最多


def _ndl_pos(block: str) -> float | None:
    global _NDL_TEXT
    if _NDL_TEXT is None:
        import ndl_build as nb
        d = nb.CACHE_DIR / NDL_PID / "ocr-ndl"
        files = sorted(d.glob("*.txt")) if d.exists() else []
        if not files:
            raise RuntimeError(f"{d} 不在——先跑 ndl_official_text.py {NDL_PID} --refs ''（段落排序要用它對照）")
        _NDL_TEXT = _han("".join(f.read_text(encoding="utf-8") for f in files))
    k = _han(block)[:40]
    hits = []
    for i in range(0, max(1, len(k) - 5), 3):
        sh = k[i:i + 6]
        if len(sh) < 6:
            break
        j = _NDL_TEXT.find(sh)
        if j >= 0 and _NDL_TEXT.find(sh, j + 1) < 0:
            hits.append(j - i)
    if not hits:
        return None
    hits.sort()
    return hits[len(hits) // 2]


def reorder_by_ndl(blocks: list[str]) -> list[str]:
    import statistics
    pos = [(_ndl_pos(b) if len(_han(b)) >= 12 else None) for b in blocks]
    known = [p for p in pos if p is not None]
    if len(known) < 2:
        return blocks
    med = statistics.median(known)
    pos = [p if p is not None and abs(p - med) < 3000 else None for p in pos]   # 誤配的離群值不算
    known = [p for p in pos if p is not None]
    if len(known) < 2 or all(b >= a - 30 for a, b in zip(known, known[1:])):
        return blocks
    # 沒有位置的段落跟著原本的前一段走
    keyed, last = [], min(known) - 1
    for i, (b, p) in enumerate(zip(blocks, pos)):
        if p is None:
            p = last + 0.001 * (i + 1)
        keyed.append((p, i, b))
        last = p
    return [b for _, _, b in sorted(keyed)]


def apply_fix(pg: int, blocks: list[str]) -> list[str]:
    fix = PAGE_FIX.get(pg)
    if not fix:
        return reorder_by_ndl(blocks)
    out = []
    for kind, val in fix:
        if kind == "lit":
            out.append(val)
        else:
            i = _find(blocks, val)
            if i is None:
                raise RuntimeError(f"PAGE_FIX p{pg}: 找不到以「{val}」開頭的段落")
            out.append(blocks[i])
    return out


def _find(blocks: list[str], prefix: str) -> int | None:
    """以 prefix 開頭的段落。完整前綴對不上時退回前三字（OCR 字形常與人工錨點不同：
    歴／歷），但只接受唯一命中——兩段都以同樣三字開頭就寧可報錯。"""
    for i, b in enumerate(blocks):
        if b.startswith(prefix):
            return i
    short = [i for i, b in enumerate(blocks) if b.startswith(prefix[:3])]
    return short[0] if len(short) == 1 else None


_TERMINAL = ("。", "」", "』", "）", ")", "！", "？", ".", "\"", "”")


def _pages() -> dict[int, str]:
    import translate_ebook_to_zh as te
    p = Path(str(te.CHUNKS_DIR)) / f"{ZENSHU_VOL1}.jsonl"
    rows = [json.loads(l) for l in p.read_text(encoding="utf-8").split("\n") if l.strip()]
    return {r["page_number"]: r.get("content") or "" for r in rows}


def load_work_sections(slug: str) -> list[dict]:
    w = REGISTRY[slug]
    start, end = w["pages"]
    pages = _pages()
    chap_at = {c[0]: c for c in CHAPTERS}
    secs: list[dict] = []
    cur = None
    for pg in range(start, end + 1):
        blocks = apply_fix(pg, clean_page(pages.get(pg, "")))
        # 前付：書名頁與作者署名頁不進正文
        blocks = [b for b in blocks if b not in ("求安錄", "內村鑑三", "求安錄上の部", "求安錄下の部")]
        ch = chap_at.get(pg)
        split_at = None
        if ch:
            how = ch[3]
            if how == "top":
                split_at = 0
            else:
                kind, pre = how
                idx = _find(blocks, pre)
                if idx is None:
                    raise RuntimeError(f"p{pg}: 找不到章 {ch[1]} 的切點「{pre}」")
                if kind == "drop":
                    blocks.pop(idx)
                # 章名在頁中間時，MinerU 常把章名連注音讀成一段（「喜よろこび／音」），
                # 落在切點前面、被當成上一章的結尾。漢字與章名相同就丟掉。
                elif idx > 0 and re.sub(r"[^一-鿿]", "", blocks[idx - 1]) == re.sub(r"[^一-鿿]", "", ch[1]):
                    blocks.pop(idx - 1)
                    idx -= 1
                split_at = idx
        for i, b in enumerate(blocks):
            if split_at is not None and i == split_at:
                cur = {"heading": ch[1], "title_zh": ch[2], "paras": [], "pages": []}
                secs.append(cur)
            if cur is None:
                continue
            printed = pg - PRINTED_OFFSET
            prev = cur["paras"][-1] if cur["paras"] else None
            # 換頁不換段：上一段沒有句末標點就接下去（詩行、引文不接）
            if prev is not None and i == 0 and not prev.endswith(_TERMINAL) and "\n" not in prev and "\n" not in b:
                cur["paras"][-1] = prev + b
            else:
                cur["paras"].append(b)
                cur["pages"].append(printed)
        if split_at is not None and split_at >= len(blocks):
            cur = {"heading": ch[1], "title_zh": ch[2], "paras": [], "pages": []}
            secs.append(cur)
    return secs


def make_engine(backend: str = "auto"):
    import uchimura_build as ub
    return ub.make_engine(backend)


def needs_translation(src: str) -> bool:
    import uchimura_build as ub
    return ub.needs_translation(src)
