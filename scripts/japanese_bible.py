#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""日文聖經——內村、關根那一代人實際讀的版本收進經典區，並逐章直譯成繁中。

使用者 2026-09-23：「在經典的那一邊，新增一個當時他們使用的日文聖經，然後全部收錄，
再進行翻譯」。起因是內村全集的聖經引文：他引的是日文聖經的字句，套和合本修訂版
常會跟他接下來的解說對不上；有一份照日文直譯的中文本，引文就能照他讀到的字句譯。

## 收哪兩個版本

| 代碼 | 版本 | 誰在讀 |
|---|---|---|
| `jbungo` | 文語訳：明治元訳舊約（1887；語料是 1953 年版）＋大正改訳新約（1917） | 內村（新約 1917 以後）、矢內原、塚本 |
| `jkougo` | 口語訳（日本聖書協會 1955） | 關根那一代以後 |

🚨 `jkougo` **只 stage、沒有併進站上**：scrollmapper 那份有 473 節是空的（馬太福音
一卷就 207 節），是語料缺損不是經文鑑別的刪節。要收得先找完整來源。

內村 1917 年以前讀的是**明治元訳新約（1880）**，跟大正改訳新約字句不同，另收為 `jmeiji`
（日文維基文庫「明治元訳新約聖書 (明治37年)」，見下方 `meiji()`），同樣直譯成 `jmeiji_zh`。

語料：scrollmapper/bible_databases `formats/json/JapBungo.json`、`JapKougo.json`（MIT；
經文本身公版——文語訳早已公版，口語訳是團體名義著作、日本著作權五十年已過）。

## 中譯 `jbungo_zh`

照**文語訳**逐節直譯成白話繁中（不是和合本改寫）。人名地名照和合本修訂版寫法——
prompt 附上同章和修經文**只供對照專名**，並在產物上量「跟和修逐字重合率」，
太高代表模型抄了和修而不是譯日文，退回重譯。

## 資料流（同 repair_bible_versions.py）

經文正本是 R2 `bible-verses/{book}.json.gz`（Drive `_verses` 已不在），本機副本在
`output/source-cache/bible-verses/`。

    python scripts/japanese_bible.py pull              # R2 → 本機卷檔（先拉最新，別蓋掉別人的修補）
    python scripts/japanese_bible.py stage             # scrollmapper → STAGE/jbungo.json、jkougo.json，並比對節數
    python scripts/japanese_bible.py translate --ver jbungo_zh --shard 0/3   # 逐章譯，checkpoint 在 STAGE/<ver>/
    python scripts/japanese_bible.py translate --ver kjv_zh --shard 0/3      # 欽定本（含次經）
    python scripts/japanese_bible.py progress --ver kjv_zh
    python scripts/japanese_bible.py collect --ver jbungo_zh                 # checkpoint → STAGE/<ver>.json
    python scripts/repair_bible_versions.py merge jbungo   # 併進卷檔（jkougo、jbungo_zh 同）
    python scripts/repair_bible_versions.py upload         # 推回 R2
"""
from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import repair_bible_versions as rbv  # noqa: E402

CACHE, STAGE = rbv.CACHE, rbv.STAGE
SRC_URL = "https://raw.githubusercontent.com/scrollmapper/bible_databases/master/formats/json/{}.json"
VERSIONS = {"jbungo": "JapBungo", "jkougo": "JapKougo"}
BOOKS = list(rbv.RCUV_BOOKS)            # 66 卷，標準順序（與 scrollmapper 相同）

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


# ── 拉卷檔 ───────────────────────────────────────────────────────────────
def pull() -> None:
    cl = rbv.r2()
    CACHE.mkdir(parents=True, exist_ok=True)
    n = 0
    for obj in cl.list_objects_v2(Bucket=rbv.ENV["R2_BUCKET"], Prefix=rbv.R2_PREFIX)["Contents"]:
        key = obj["Key"]
        body = cl.get_object(Bucket=rbv.ENV["R2_BUCKET"], Key=key)["Body"].read()
        (CACHE / key[len(rbv.R2_PREFIX):]).write_bytes(body)
        n += 1
    print(f"從 R2 拉回 {n} 卷")


def load_book(code: str) -> dict:
    return json.loads(gzip.decompress((CACHE / f"{code}.json.gz").read_bytes()))


# ── 收錄 ─────────────────────────────────────────────────────────────────
def fetch_src(name: str) -> dict:
    f = Path("c:/tmp") / f"{name}.json"
    if not f.exists():
        import requests
        f.write_bytes(requests.get(SRC_URL.format(name), timeout=600).content)
    return json.loads(f.read_text(encoding="utf-8"))


def stage() -> None:
    STAGE.mkdir(parents=True, exist_ok=True)
    for code, name in VERSIONS.items():
        d = fetch_src(name)
        assert len(d["books"]) == 66, len(d["books"])
        out: dict[str, dict[str, dict[str, str]]] = {}
        empty = 0
        for bk, book in zip(BOOKS, d["books"]):
            for ch in book["chapters"]:
                for v in ch["verses"]:
                    t = (v["text"] or "").strip()
                    if not t:
                        empty += 1
                        continue
                    out.setdefault(bk, {}).setdefault(str(ch["chapter"]), {})[str(v["verse"])] = t
        (STAGE / f"{code}.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
        # 跟站上 kjva／cuv2010 比每章節數，抓對不上的版本分節差
        diff = []
        for bk in BOOKS:
            doc = load_book(bk)
            for ch, vs in out.get(bk, {}).items():
                ours = {r["v"] for r in doc["chapters"].get(ch, []) if r["t"].get("cuv2010") or r["t"].get("kjva")}
                theirs = {int(x) for x in vs}
                if theirs - ours:
                    diff.append(f"{bk} {ch}: 多出 {sorted(theirs - ours)[:5]}")
        n = sum(len(v) for b in out.values() for v in b.values())
        print(f"{code}: {n:,} 節（空節 {empty}）；站上沒有的節號 {len(diff)} 章")
        for x in diff[:15]:
            print("   ", x)


# ── 翻譯 ─────────────────────────────────────────────────────────────────
# 一支程式譯三個版本（使用者 2026-09-24）：內村日文著作引文照當年日文聖經、
# 英文著作引文照欽定本（實測 How I Became a Christian 欽定本獨有片語 138 處、
# 美國標準本 3 處），所以三個底本都各出一份中文直譯。
#   jbungo_zh  ← jbungo  文語訳（明治元訳舊約＋大正改訳新約）
#   kjv_zh     ← kjva    欽定本 1611（含次經，使用者要「整本」）
#   jmeiji_zh  ← jmeiji  明治元訳新約 1880（內村 1917 年以前引的新約；維基文庫，見 meiji()）
SPECS = {
    "jbungo_zh": {"src": "jbungo", "lang": "ja", "style": "classical",
                  "name": "日文《文語訳聖書》（明治元訳舊約／大正改訳新約）"},
    "kjv_zh": {"src": "kjva", "lang": "en", "style": "classical",
               "name": "英文《欽定本聖經》（King James Version, 1611）"},
    "asv_zh": {"src": "asv", "lang": "en", "style": "classical",
               "name": "英文《美國標準譯本》（American Standard Version, 1901）"},
    "niv_zh": {"src": "niv", "lang": "en", "style": "vernacular",
               "name": "英文《新國際譯本》（New International Version, 2011）"},
    "jmeiji_zh": {"src": "jmeiji", "lang": "ja", "style": "classical",
                  "name": "日文《明治元訳新約全書》（1880）"},
}
# 語域（使用者 2026-09-24）：「若是古英語就用古漢語對譯」、「thee/thou 翻譯作汝」。
# 欽定本、ASV 是古英語、文語訳是日文文語 → 淺近文言；NIV 是現代英語 → 白話。
# （文語訳原本照白話譯了 56 章，使用者同日決定一併改文言，已刪掉重譯。）
# 🚨 這條只管聖經譯本本身。內村等著作的正文仍一律白話（[[feedback_translation_register_and_titles]]）。
REGISTER = {
    "vernacular": "2. 一律白話，不用文言句末虛詞（也／矣／乎／焉），不拿「之」當「的」。詩歌可稍保留韻文節奏。\n",
    "classical": ("2. 原文是古語（古英語 thee／thou／-eth／-est，或日文文語），譯文用**淺近文言**對譯，"
                  "程度約如淺文理和合本：thou／thee 與日文「汝」作「汝」、thy／thine 作「汝之」、"
                  "ye 與複數 you、日文「爾曹」作「爾等」，古語動詞照文言語氣處理；"
                  "不要譯成現代白話，也不要艱深到讀不懂。標點用新式標點（，。；：「」），"
                  "「、」只用在並列的詞語之間，不可當逗號用。"
                  "文言裡不可夾「的」「了」「們」「這」「那」這類白話字。\n"),
}

PROMPT_HEAD = """你是聖經譯者。下面是{name}{book_zh}第 {ch} 章的經文。
請**照原文逐節直譯**成現代白話繁體中文。

規則：
1. 譯的是這份原文的字句與語氣，**不是**把和合本抄過來。原文怎麼說，中文就怎麼說；
   用字若跟通行中文譯本不同，照原文。
{register}3. 人名、地名、民族名、書卷名一律用《和合本修訂版》的通行寫法（亞伯拉罕、摩西、耶路撒冷、法利賽人……）。
4. 引號用中文「」；不加註解、不加節外的說明。
   稱神的代名詞不用「祂」「祢」。
   🚨 **代名詞照原文留代名詞**：原文寫 he／him／his，就譯「他／他的」（文言作「彼／其」），
   不可換成「主」「神」這類名詞；原文寫名詞才譯名詞。
   每節句尾照原文的標點（句點作「。」、逗號作「，」、分號作「；」、冒號作「：」）。
"""
PROMPT_LANG = {
    "ja": """5. 「神」照日文作「神」；「ヱホバ」作「耶和華」。
6. 詩歌體的日文用空格分隔詩行；譯文要照中文加上逗號、分號、句號，不可只留空格。
   詩篇開頭的標題（如「ダビデのうた」「伶長にうたはしめたる歌」）併在第 1 節裡，
   譯出來放在該節最前面、用〔〕括起來，例如「〔大衛的詩〕耶和華是我的牧者，……」。
""",
    "en": """5. God 譯「神」。**全大寫的 LORD（用來代替神名）譯「主」**，不要改成「耶和華」；
   一般的 Lord 也譯「主」。原文直接寫出神名 Jehovah（美國標準譯本）的，譯「耶和華」。
   Holy Ghost／Holy Spirit 譯「聖靈」。欽定本的斜體補字照譯進句子裡，不另標。
6. 詩篇標題若在第 1 節裡，譯出來放在該節最前面、用〔〕括起來。
""",
}
PROMPT_TAIL = """7. 輸出格式：每節一行，「節號｜譯文」，節號與原文相同、一節都不能少、不能合併。
{style_ref}
原文：
{src}
"""
OUT_FMT = "\n只輸出譯文：第一行寫 <<<譯文>>>，接著每節一行，最後一行寫 <<<完>>>。不要寫任何分析。"
DEBUG = STAGE / "_debug"

BOOK_ZH = {}


def book_zh(code: str) -> str:
    if not BOOK_ZH:
        import course_quote_bible as cqb
        BOOK_ZH.update(cqb.BOOKS)
    return BOOK_ZH.get(code, code)


_KANA = re.compile(r"[぀-ゟ゠-ヺー]")
_LATIN = re.compile(r"[A-Za-z]")
_LINE = re.compile(r"^\s*(\d+)\s*[｜|:：.．、]\s*(.+?)\s*$")
BATCH = 40                                   # 詩篇 119 篇 176 節要分批


def overlap(a: str, b: str) -> float:
    """譯文與和修的逐字重合率（最長共同子序列 / 譯文長度）——量是不是抄了和修。"""
    import difflib
    a = re.sub(r"\W", "", a)
    b = re.sub(r"\W", "", b)
    if not a or not b:
        return 0.0
    m = difflib.SequenceMatcher(None, a, b, autojunk=False)
    return sum(x.size for x in m.get_matching_blocks()) / len(a)


COPY_LIMIT = 0.9                             # 中文聖經語言本來就收斂，實測直譯也有 0.7–0.8


_END_PUNCT = {".": "。", ",": "，", ";": "；", ":": "：", "?": "？", "!": "！",
              "。": "。", "、": "，", "，": "，", "；": "；", "：": "：", "？": "？", "！": "！"}
_VERN = re.compile(r"[的了們這那]")


def fix_end(zh: str, src: str) -> str:
    """模型常漏掉句尾標點；照原文最後一個標點補上（原文沒標點就不補）。"""
    zh = zh.rstrip("、，") if zh.endswith(("、", "，")) and src.rstrip()[-1:] not in ",，、" else zh
    if not zh or zh[-1] in "。，；：？！」』）…—":
        return zh
    tail = src.rstrip().rstrip("'\"’”』」)）")
    return zh + _END_PUNCT.get(tail[-1:], "") if tail else zh


def translate_batch(ver: str, code: str, ch: str, verses: dict[str, str], ref: dict[int, str],
                    force_style: str | None = None) -> dict[str, str]:
    import translate_ebook_to_zh as te
    spec = dict(SPECS[ver], style=force_style or SPECS[ver].get("style", "vernacular"))
    classical = spec.get("style") == "classical"
    src = "\n".join(f"{v}｜{t}" for v, t in verses.items())
    # 🚨 不再把和修同章附進 prompt：關掉推理後，整節和修擺在眼前它就照抄（白話那一步
    #    ASV／NIV 創世記前幾章重合 92–100%、整章被退）。專名改在規則裡要求用和修寫法，
    #    ref 只留給下面的抄襲比對。
    style_ref = (f"\n文體範本（施約瑟淺文理譯本的別處經文，只學它的文言程度與句法）：\n{style_sample()}\n"
                 if classical else "")
    prompt = (PROMPT_HEAD + PROMPT_LANG[spec["lang"]] + PROMPT_TAIL).format(
        name=spec["name"], book_zh=book_zh(code), ch=ch, src=src, style_ref=style_ref,
        register=REGISTER[spec.get("style", "vernacular")])
    last = "?"
    tries = 4 if classical else 3
    for attempt in range(tries):
        try:
            # 關推理：開著的話規則一多它就先寫兩萬字推理、把 max_tokens 用完（見 nvidia_chat）。
            # 關掉後文言會往附給它的和修白話靠，所以文言版本另附淺文理範本（style_ref）。
            raw = te.nvidia_chat(prompt + OUT_FMT, max_tokens=8000, temperature=0.2, thinking=False)
        except Exception as e:  # noqa: BLE001
            last = f"engine {e}"
            time.sleep(20)
            continue
        # 🚨 nemotron 會先把推理寫成明文（沒有 <think> 標籤），裡面夾著原句與
        #    「1｜…」半成品；整份解析會把那些當譯文（第一輪五章全數缺節／假名外洩）。
        #    只收 <<<譯文>>>…<<<完>>> 區塊；推理裡偶爾也會複述出這種區塊，
        #    所以取解析得出最多節的那一塊，不取最後一塊。
        blocks = re.findall(r"<<<譯文>>>(.*?)<<<完>>>", raw, re.S)

        def parse(block: str) -> dict[str, str]:
            out = {}
            for ln in block.splitlines():
                m = _LINE.match(ln)
                if m and m.group(1) in verses:
                    t = te._to_traditional(m.group(2).strip())
                    if spec["lang"] == "ja":
                        # 文語訳一律作「神」；附給它對照專名的和修是上帝版，模型會抄進來
                        t = t.replace("上帝", "神")
                    out[m.group(1)] = fix_end(t, verses[m.group(1)])
            return out
        got = max((parse(b) for b in blocks), key=len) if blocks else {}
        missing = [v for v in verses if not got.get(v)]
        if spec["lang"] == "ja":
            leak = [v for v, t in got.items() if len(_KANA.findall(t)) > 2]
        else:
            leak = [v for v, t in got.items() if len(_LATIN.findall(t)) > max(6, len(t) * 0.2)]
        joined = "".join(got.get(v, "") for v in verses)
        copied = overlap(joined, "".join(ref.get(int(v), "") for v in verses))
        vern = len(_VERN.findall(joined))
        too_vern = classical and vern > max(2, len(joined) // 150)
        if not blocks:
            last = "沒有 <<<譯文>>> 區塊"
        elif missing:
            last = f"缺節 {len(missing)}/{len(verses)}：{missing[:5]}"
        elif leak:
            last = f"原文外洩 {leak[:5]}"
        elif too_vern and attempt < tries - 1:
            last = f"文言裡夾白話（的了們這那 {vern} 處）"
        elif copied > COPY_LIMIT:
            last = f"跟對照本重合 {copied:.0%}（抄了）"
        else:
            if too_vern:                          # 最後一次才放行：記下來之後重譯，不要靜默收下
                with open(STAGE / f"_weak_{ver}.txt", "a", encoding="utf-8") as f:
                    f.write(f"{code} {ch} {min(verses, key=int)}-{max(verses, key=int)} 白話 {vern} 處\n")
            return got
        DEBUG.mkdir(parents=True, exist_ok=True)
        (DEBUG / f"{ver}_{code}_{ch}_{attempt}.txt").write_text(raw, encoding="utf-8")
        print(f"   {code} {ch} 重試 {attempt + 1}：{last}", flush=True)
    raise RuntimeError(f"{code} {ch}: {last}")


CLASSICALIZE = """下面是聖經{book_zh}第 {ch} 章的白話中文直譯（譯自{name}）。原文是古語，
請把它**改寫成淺近文言**，程度約如淺文理和合本。

規則：
1. 只改語體，**意思一字不增減**；原譯的用字若是在反映原文的特殊講法，保留那個講法。
2. 人名、地名、專名一字不動；「神」「耶和華」「主」照原譯。
3. 你→汝、你的→汝之、你們→爾等；他→彼、他的→其；不可夾「的」「了」「們」「這」「那」。
4. 代名詞照原譯留代名詞，不換成名詞。〔〕裡的詩篇標題照樣留在該節最前面。
5. 標點用新式標點（，。；：「」），「、」只用在並列詞語之間。
6. 輸出格式：每節一行，「節號｜譯文」，一節都不能少。
{style_ref}
白話直譯：
{src}
"""


def classicalize(ver: str, code: str, ch: str, vern: dict[str, str], ref: dict[int, str]) -> dict[str, str]:
    """文言版本的第二步（白話直譯 → 淺近文言）。
    文語訳：模型直接從日文文語譯文言，會把半句日文原封抄進來（「彼によりて永遠の生命を得ん爲なり」），
    重試又改抄施約瑟淺文理——日文文語本身就半像文言，關掉推理後它分不清。
    欽定本／ASV：關推理後一步到位會滑回和修式白話（約 3 章四次重試都「的」字十處上下）。
    所以先照白話直譯（這一步忠於原文字句、品質穩），再中文轉中文改寫成文言。"""
    import translate_ebook_to_zh as te
    src = "\n".join(f"{v}｜{t}" for v, t in vern.items())
    style_ref = f"\n文體範本（施約瑟淺文理譯本的別處經文，只學文言程度與句法）：\n{style_sample()}\n"
    prompt = CLASSICALIZE.format(book_zh=book_zh(code), ch=ch, name=SPECS[ver]["name"], src=src, style_ref=style_ref)
    last = "?"
    for attempt in range(4):
        try:
            raw = te.nvidia_chat(prompt + OUT_FMT, max_tokens=8000, temperature=0.2, thinking=False)
        except Exception as e:  # noqa: BLE001
            last = f"engine {e}"
            time.sleep(20)
            continue
        got = {}
        for b in re.findall(r"<<<譯文>>>(.*?)<<<完>>>", raw, re.S):
            cur = {}
            for ln in b.splitlines():
                m = _LINE.match(ln)
                if m and m.group(1) in vern:
                    cur[m.group(1)] = fix_end(te._to_traditional(m.group(2).strip()).replace("上帝", "神"), vern[m.group(1)])
            got = max(got, cur, key=len)
        joined = "".join(got.values())
        vcount = len(_VERN.findall(joined))
        missing = [v for v in vern if not got.get(v)]
        # 跟施約瑟淺文理同章比：範本雖然不給同一章，模型仍可能憑記憶寫出淺文理原句
        cl = {r["v"]: re.sub(r"\s+", "", r["t"].get("cuv1919e", "")) for r in load_book(code)["chapters"].get(ch, [])}
        copied = overlap(joined, "".join(cl.get(int(v), "") for v in vern))
        if missing:
            last = f"文言化缺節 {len(missing)}/{len(vern)}"
        elif any(_KANA.search(t) for t in got.values()):
            last = "文言化帶假名"
        elif vcount > max(2, len(joined) // 150) and attempt < 3:
            last = f"文言化後仍夾白話 {vcount} 處"
        elif copied > COPY_LIMIT:
            last = f"跟施約瑟淺文理重合 {copied:.0%}（抄了）"
        else:
            if vcount > max(2, len(joined) // 150):
                with open(STAGE / f"_weak_{ver}.txt", "a", encoding="utf-8") as f:
                    f.write(f"{code} {ch} 文言化 白話 {vcount} 處\n")
            return got
        DEBUG.mkdir(parents=True, exist_ok=True)
        (DEBUG / f"{ver}_{code}_{ch}_cl{attempt}.txt").write_text(raw, encoding="utf-8")
        print(f"   {code} {ch} 文言化重試 {attempt + 1}：{last}", flush=True)
    raise RuntimeError(f"{code} {ch}: {last}")


def source_chapters(ver: str) -> list[tuple[str, str, dict[str, str]]]:
    """(書卷, 章, {節: 原文})，原文一律從經文卷檔讀（jbungo 已併進卷檔）。
    書卷順序：正典 66 卷在前，其餘（次經）照檔名。"""
    srcv = SPECS[ver]["src"]
    codes = BOOKS + sorted(f.name.split(".")[0] for f in CACHE.glob("*.json.gz")
                           if f.name.split(".")[0] not in BOOKS)
    out = []
    for bk in codes:
        doc = load_book(bk)
        for ch in sorted(doc["chapters"], key=int):
            vs = {str(r["v"]): r["t"][srcv].strip() for r in doc["chapters"][ch]
                  if (r["t"].get(srcv) or "").strip()}
            if vs:
                out.append((bk, ch, vs))
    return out


_STYLE: list[str] = []


def style_sample() -> str:
    """文言版本的文體範本：施約瑟淺文理（1902）的詩篇 1:1–3 與馬太 5:3–8。
    🚨 固定用這兩段、不給同一章：給同一章的淺文理，模型會整段照抄
    （文言化那一步實測跟範本重合 100%，四次重試都一樣）。
    語料在專名兩邊留了空格（「主諭 亞伯蘭 曰」），拿掉；淺文理的「、」逗號改新式標點。"""
    if not _STYLE:
        for bk, ch, vs in (("psa", "1", range(1, 4)), ("mat", "5", range(3, 9))):
            rows = {r["v"]: r["t"].get("cuv1919e", "") for r in load_book(bk)["chapters"][ch]}
            for v in vs:
                t = re.sub(r"\s+", "", rows.get(v, "")).replace("○", "").replace("、", "，")
                t = re.sub(r"[(（][^()（）]*[)）]", "", t)                 # 夾註「(虛心者原文作貧於心者)」.rstrip("，")
                _STYLE.append(f"{book_zh(bk)} {ch}:{v}　{t}。")
    return "\n".join(_STYLE)


def chapter_ref(bk: str, ch: str) -> dict[int, str]:
    """給模型對照專名的中文本：和修；次經和修沒有，用思高。"""
    doc = load_book(bk)
    return {r["v"]: r["t"].get("cuv2010") or r["t"].get("sigao") or r["t"].get("cuv1919", "")
            for r in doc["chapters"].get(ch, [])}


def translate(ver: str, shard: str) -> None:
    i, n = (int(x) for x in shard.split("/"))
    out_dir = STAGE / ver
    todo = [c for k, c in enumerate(source_chapters(ver)) if k % n == i]
    fails = 0
    for bk, ch, verses in todo:
        out = out_dir / bk / f"{ch}.json"
        if out.exists():
            continue
        ref = chapter_ref(bk, ch)
        keys = sorted(verses, key=int)
        res: dict[str, str] = {}
        try:
            for k in range(0, len(keys), BATCH):
                part = {v: verses[v] for v in keys[k:k + BATCH]}
                # 文言版本一律兩步：一步到位時日文會漏假名、英文會滑回和修白話（見 classicalize）
                if SPECS[ver].get("style") == "classical":
                    vern = translate_batch(ver, bk, ch, part, ref, force_style="vernacular")
                    res.update(classicalize(ver, bk, ch, vern, ref))
                else:
                    res.update(translate_batch(ver, bk, ch, part, ref))
        except RuntimeError as e:
            fails += 1
            print(f"✗ {e}", flush=True)
            if fails >= 3:
                raise SystemExit("連續三章失敗，整條線停（引擎多半出事了）")
            continue
        fails = 0
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(res, ensure_ascii=False, indent=0), encoding="utf-8")
        print(f"✓ {bk} {ch}（{len(res)} 節）", flush=True)
    left = [c for c in todo if not (out_dir / c[0] / f"{c[1]}.json").exists()]
    if left:
        print(f"本輪跑完，還有 {len(left)} 章失敗待重跑")
    else:
        print("QUEUE_COMPLETE")                    # fleet_keeper 的 EnsureUntil 認這個退場


def progress(ver: str) -> None:
    allc = source_chapters(ver)
    done = sum(1 for bk, ch, _ in allc if (STAGE / ver / bk / f"{ch}.json").exists())
    print(f"{ver}：{done}/{len(allc)} 章（{done / max(len(allc), 1):.1%}）")


def collect(ver: str) -> None:
    out: dict = {}
    for bk, ch, _ in source_chapters(ver):
        f = STAGE / ver / bk / f"{ch}.json"
        if f.exists():
            out.setdefault(bk, {})[ch] = json.loads(f.read_text(encoding="utf-8"))
    (STAGE / f"{ver}.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print(f"{ver}：收進 {sum(len(v) for b in out.values() for v in b.values()):,} 節")



# ── 明治元訳新約（1880）─────────────────────────────────────────────────────
# 內村 1917 年以前引的新約是這一版：《求安錄》（1893）引太 5:48「天に在す爾曹の父の完全が如く
# 爾曹も完全すべし」逐字相同，大正改訳作「汝らの天の父の全きが如く、汝らも全かれ」。
# 來源：日文維基文庫「明治元訳新約聖書 (明治37年)」——底本 NDL『新約全書』米國聖書會社 1904，
# 缺頁以同年大英國北英國聖書會社本補；逐章與明治14年（1881）版對校，異文記在章末 ※ 註。
# 公有領域（PD-old）。頁面說明：已修正假名錯誤與明顯誤植、不用變體假名與踊り字（々除外）、
# 拿掉專名旁線、ルビ依 1881 年版補齊——所以是「校訂本」，不是逐字影印。
WS_API = "https://ja.wikisource.org/w/api.php"
WS_UA = {"User-Agent": "know-graph-lab private research (contact: redpiigpig)"}
MEIJI_BOOKS = {
    "馬太傳福音書": "mat", "馬可傳福音書": "mrk", "路加傳福音書": "luk", "約翰傳福音書": "jhn",
    "使徒行傳": "act", "羅馬書": "rom", "哥林多前書": "1co", "哥林多後書": "2co",
    "加拉太書": "gal", "以弗所書": "eph", "腓立比書": "php", "哥羅西書": "col",
    "帖撒羅尼迦前書": "1th", "帖撒羅尼迦後書": "2th", "提摩太前書": "1ti", "提摩太後書": "2ti",
    "提多書": "tit", "腓利門書": "phm", "希伯來書": "heb", "雅各書": "jas",
    "彼得前書": "1pe", "彼得後書": "2pe", "約翰第一書": "1jn", "約翰第二書": "2jn",
    "約翰第三書": "3jn", "猶太書": "jud", "約翰默示録": "rev",
}
MEIJI_ONE_CHAPTER = {"腓利門書", "猶太書", "約翰第二書", "約翰第三書"}   # 只有一章，經文直接在卷頁上
MEIJI_RAW = STAGE / "jmeiji_raw"


def _ws_get(params: dict) -> dict:
    import requests
    for attempt in range(6):
        r = requests.get(WS_API, params={**params, "format": "json"}, headers=WS_UA, timeout=60)
        if r.status_code == 429:                   # 維基文庫連打幾次就 429；退避
            time.sleep(15 * (attempt + 1))
            continue
        r.raise_for_status()
        return r.json()
    raise RuntimeError(f"wikisource 429 不停：{params}")


def meiji_titles() -> list[tuple[str, str, int]]:
    """(頁名, 書卷代碼, 章)。章頁從分類拿；單章書用卷頁。"""
    import bible_quote_ref as bqr
    d = _ws_get({"action": "query", "list": "categorymembers", "cmlimit": 500,
                 "cmtitle": "Category:明治元訳新約聖書 (明治37年)"})
    out = []
    for m in d["query"]["categorymembers"]:
        t = m["title"]
        g = re.match(r"^(.+?)\(明治元訳\)(?: 第(.+)章)?$", t)
        if not g or g.group(1) not in MEIJI_BOOKS:
            continue
        book, chk = g.group(1), g.group(2)
        if chk:
            out.append((t, MEIJI_BOOKS[book], bqr.cn_num(chk)))
        elif book in MEIJI_ONE_CHAPTER:
            out.append((t, MEIJI_BOOKS[book], 1))
    return out


_RUBY = re.compile(r"\{\{ruby\|([^|}]*)\|[^}]*\}\}")
_VLINE = re.compile(r"^(\d+)\s+(.+?)(?:<br\s*/?>)?\s*$")


def parse_meiji(wikitext: str) -> tuple[dict[str, str], list[str]]:
    """wikitext → ({節: 經文（只留漢字，讀音拿掉）}, [章末 1881 年版異文註])。"""
    verses: dict[str, str] = {}
    notes: list[str] = []
    for ln in wikitext.splitlines():
        ln = ln.strip()
        if ln.startswith("※"):
            notes.append(_RUBY.sub(r"\1", re.sub(r"<br\s*/?>", "", ln)).strip())
            continue
        m = _VLINE.match(ln)
        if not m:
            continue
        t = _RUBY.sub(r"\1", m.group(2))
        t = re.sub(r"※\d*|<[^>]+>|\{\{[^}]*\}\}|'''?", "", t).strip()
        if t:
            verses[m.group(1)] = t
    return verses, notes


def meiji() -> None:
    """抓明治元訳新約 → STAGE/jmeiji.json（格式同 jbungo），異文註 → STAGE/jmeiji_notes.json。
    逐頁快取在 STAGE/jmeiji_raw/，可重跑。之後 `repair_bible_versions.py merge jmeiji`。"""
    MEIJI_RAW.mkdir(parents=True, exist_ok=True)
    titles = meiji_titles()
    print(f"章頁 {len(titles)}（新約應為 260）")
    out: dict = {}
    notes: dict = {}
    for k, (t, bk, ch) in enumerate(titles, 1):
        f = MEIJI_RAW / f"{bk}_{ch}.txt"
        if not f.exists():
            d = _ws_get({"action": "query", "prop": "revisions", "rvprop": "content",
                         "rvslots": "main", "titles": t})
            page = next(iter(d["query"]["pages"].values()))
            f.write_text(page["revisions"][0]["slots"]["main"]["*"], encoding="utf-8")
            time.sleep(2.5)
            if k % 20 == 0:
                print(f"  {k}/{len(titles)}", flush=True)
        vs, ns = parse_meiji(f.read_text(encoding="utf-8"))
        out.setdefault(bk, {})[str(ch)] = vs
        if ns:
            notes.setdefault(bk, {})[str(ch)] = ns
    (STAGE / "jmeiji.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    (STAGE / "jmeiji_notes.json").write_text(json.dumps(notes, ensure_ascii=False, indent=1), encoding="utf-8")
    # 跟大正改訳（jbungo 新約）逐章比節數：少的節逐條列出來看，不要只看總數
    bungo = json.loads((STAGE / "jbungo.json").read_text(encoding="utf-8"))
    n = sum(len(v) for b in out.values() for v in b.values())
    diffs = []
    for bk, chs in bungo.items():
        if bk not in MEIJI_BOOKS.values():
            continue
        for ch, vs in chs.items():
            mine = set(out.get(bk, {}).get(ch, {}))
            if set(vs) - mine:
                diffs.append(f"{bk} {ch}: 明治本缺 {sorted(set(vs) - mine, key=int)}")
            if mine - set(vs):
                diffs.append(f"{bk} {ch}: 明治本多 {sorted(mine - set(vs), key=int)}")
    print(f"jmeiji：{len(out)} 卷、{n:,} 節；異文註 {sum(len(v) for b in notes.values() for v in b.values())} 條；"
          f"節號跟大正改訳對不上 {len(diffs)} 章")
    for x in diffs[:40]:
        print("   ", x)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["pull", "stage", "meiji", "translate", "progress", "collect"])
    ap.add_argument("--ver", default="jbungo_zh", choices=list(SPECS))
    ap.add_argument("--shard", default="0/1")
    a = ap.parse_args()
    if a.cmd == "pull":
        pull()
    elif a.cmd == "stage":
        stage()
    elif a.cmd == "meiji":
        meiji()
    elif a.cmd == "translate":
        translate(a.ver, a.shard)
    elif a.cmd == "progress":
        progress(a.ver)
    else:
        collect(a.ver)
