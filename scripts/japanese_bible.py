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

🚨 **缺一個**：內村 1917 年以前讀的是**明治元訳新約（1880）**，跟大正改訳新約字句不同。
這一版目前找不到數位全文（scrollmapper 只有 1953/1917 的組合），所以 `jbungo`
新約部分對內村早期文章只是近似。

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
    python scripts/japanese_bible.py translate --shard 0/3   # 逐章譯，checkpoint 在 STAGE/jbungo_zh/
    python scripts/japanese_bible.py progress
    python scripts/japanese_bible.py collect           # checkpoint → STAGE/jbungo_zh.json
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
ZH_DIR = STAGE / "jbungo_zh"
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
PROMPT = """你是聖經譯者。下面是日文《文語訳聖書》（明治元訳舊約／大正改訳新約）{book_zh}第 {ch} 章的經文。
請**照日文逐節直譯**成現代白話繁體中文。

規則：
1. 譯的是這份日文的字句與語氣，**不是**把和合本抄過來。日文怎麼說，中文就怎麼說；
   日文的用字若跟通行中文譯本不同（例如「愛」「義」「生命」「救」的講法），照日文。
2. 一律白話，不用文言句末虛詞（也／矣／乎／焉），不拿「之」當「的」。詩歌可稍保留韻文節奏。
3. 人名、地名、民族名、書卷名一律用下面附的《和合本修訂版》寫法（附文**只**供對照專名，
   不可照抄它的句子）。「神」照日文作「神」。
4. 日文的「」照用中文引號「」；不加註解、不加節外的說明。
   稱神的代名詞用「他」「你」，不用「祂」「祢」（與和合本修訂版一致）。
5. 詩歌體的日文用空格分隔詩行；譯文要照中文加上逗號、分號、句號，不可只留空格。
   詩篇開頭的標題（如「ダビデのうた」「伶長にうたはしめたる歌」）併在第 1 節裡，
   譯出來放在該節最前面、用〔〕括起來，例如「〔大衛的詩〕耶和華是我的牧者，……」。
6. 輸出格式：每節一行，「節號｜譯文」，節號與日文相同、一節都不能少、不能合併。

《和合本修訂版》同章（只看專名）：
{ref}

日文原文：
{src}
"""

OUT_FMT = "\n只輸出譯文：第一行寫 <<<譯文>>>，接著每節一行，最後一行寫 <<<完>>>。不要寫任何分析。"

BOOK_ZH = {}


def book_zh(code: str) -> str:
    if not BOOK_ZH:
        import course_quote_bible as cqb
        BOOK_ZH.update(cqb.BOOKS)
    return BOOK_ZH.get(code, code)


_KANA = re.compile(r"[\u3040-\u309f\u30a0-\u30fa\u30fc]")
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


def translate_batch(code: str, ch: str, verses: dict[str, str], ref: dict[int, str]) -> dict[str, str]:
    import translate_ebook_to_zh as te
    src = "\n".join(f"{v}｜{t}" for v, t in verses.items())
    refs = "\n".join(f"{v}｜{ref.get(int(v), '')}" for v in verses)
    prompt = PROMPT.format(book_zh=book_zh(code), ch=ch, ref=refs, src=src)
    last = "?"
    for attempt in range(3):
        try:
            raw = te.nvidia_chat(prompt + OUT_FMT, max_tokens=8000, temperature=0.2, system="/no_think")
        except Exception as e:  # noqa: BLE001
            last = f"engine {e}"
            time.sleep(20)
            continue
        # 🚨 nemotron 會先把推理寫成明文（沒有 <think> 標籤），裡面夾著日文原句與
        #    「1｜…」半成品；整份解析會把那些當譯文（第一輪五章全數缺節／假名外洩）。
        #    只收最後一個 <<<譯文>>>…<<<完>>> 區塊，沒有區塊就當失敗。
        blocks = re.findall(r"<<<譯文>>>(.*?)<<<完>>>", raw, re.S)
        if not blocks:
            last = "沒有 <<<譯文>>> 區塊"
            print(f"   {code} {ch} 重試 {attempt + 1}：{last}", flush=True)
            continue
        # 推理裡偶爾也會寫出 <<<譯文>>>…<<<完>>>（在複述格式要求），所以不取「最後一塊」，
        # 取解析得出最多節的那一塊。
        def parse(block: str) -> dict[str, str]:
            out = {}
            for ln in block.splitlines():
                m = _LINE.match(ln)
                if m and m.group(1) in verses:
                    # 文語訳一律作「神」；附給它對照專名的和修是上帝版，模型會抄進來
                    out[m.group(1)] = te._to_traditional(m.group(2).strip()).replace("上帝", "神")
            return out
        got = max((parse(b) for b in blocks), key=len)
        missing = [v for v in verses if not got.get(v)]
        leak = [v for v, t in got.items() if len(_KANA.findall(t)) > 2]
        joined = "".join(got.get(v, "") for v in verses)
        copied = overlap(joined, "".join(ref.get(int(v), "") for v in verses))
        if missing:
            last = f"缺節 {missing[:5]}"
        elif leak:
            last = f"假名外洩 {leak[:5]}"
        elif copied > COPY_LIMIT:
            last = f"跟和修重合 {copied:.0%}（抄了和修）"
        else:
            return got
        print(f"   {code} {ch} 重試 {attempt + 1}：{last}", flush=True)
    raise RuntimeError(f"{code} {ch}: {last}")


def chapters() -> list[tuple[str, str]]:
    src = json.loads((STAGE / "jbungo.json").read_text(encoding="utf-8"))
    return [(bk, ch) for bk in BOOKS for ch in sorted(src.get(bk, {}), key=int)]


def translate(shard: str) -> None:
    i, n = (int(x) for x in shard.split("/"))
    src = json.loads((STAGE / "jbungo.json").read_text(encoding="utf-8"))
    todo = [c for k, c in enumerate(chapters()) if k % n == i]
    fails = 0
    for bk, ch in todo:
        out = ZH_DIR / bk / f"{ch}.json"
        if out.exists():
            continue
        verses = src[bk][ch]
        doc = load_book(bk)
        ref = {r["v"]: r["t"].get("cuv2010") or r["t"].get("cuv1919", "")
               for r in doc["chapters"].get(ch, [])}
        keys = sorted(verses, key=int)
        res: dict[str, str] = {}
        try:
            for k in range(0, len(keys), BATCH):
                part = {v: verses[v] for v in keys[k:k + BATCH]}
                res.update(translate_batch(bk, ch, part, ref))
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
    left = [c for c in todo if not (ZH_DIR / c[0] / f"{c[1]}.json").exists()]
    if left:
        print(f"本輪跑完，還有 {len(left)} 章失敗待重跑")
    else:
        print("QUEUE_COMPLETE")                    # fleet_keeper 的 EnsureUntil 認這個退場


def progress() -> None:
    allc = chapters()
    done = sum(1 for bk, ch in allc if (ZH_DIR / bk / f"{ch}.json").exists())
    print(f"jbungo_zh：{done}/{len(allc)} 章（{done / len(allc):.1%}）")


def collect() -> None:
    out: dict = {}
    for bk, ch in chapters():
        f = ZH_DIR / bk / f"{ch}.json"
        if f.exists():
            out.setdefault(bk, {})[ch] = json.loads(f.read_text(encoding="utf-8"))
    (STAGE / "jbungo_zh.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print(f"收進 {sum(len(v) for b in out.values() for v in b.values()):,} 節")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["pull", "stage", "translate", "progress", "collect"])
    ap.add_argument("--shard", default="0/1")
    a = ap.parse_args()
    {"pull": pull, "stage": stage, "progress": progress, "collect": collect}.get(
        a.cmd, lambda: translate(a.shard))()
