#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把《佛光大辭典增訂版》的 MDict 檔解析成站上可查的詞條，並收它的插圖與缺字圖。

來源是使用者 2026-09-13 放在下載區的三個分卷
`佛光大辭典增訂版【阿彌陀佛】20230501.zip.001/.002/.003`（合計 54 MB）。
⚠️ 那不是多卷 zip，是**單一 ZIP 被逐位元組切三段**（`.001` 開頭就是 `PK\\x03\\x04`），
所以用 `cat` 接起來即可，不要去找 7z 的多卷模式。

裡面是 MDict：`.mdx` 11.7 MB（釋義）＋ `.mdd` 42.3 MB（資源）。標頭雖然寫
`Encrypted="2"`、`RegisterBy="EMail"`，但那是 MDict 標準的固定鹽值加擾，
不是使用者綁定的 DRM，`mdict_utils` 讀得出來。

檔案來歷：`.mdd` 裡除了 3,264 張 jpg，還有 `fgsdict.s3db`（50 MB SQLite）、
33 個 `fgsdict_bookN.xml` 與 iOS 的 `.xcent`——這套 MDict 是由佛光山官方 app 的資料
轉製的。使用者表示已取得授權（2026-09-11），站台不對外開放、僅研究自用。

## 🚨 三個會靜默毀損內容的地方

1. **有些 `<img>` 不是插圖，是「缺字圖」。**罕用字無法編碼時，這部辭典直接嵌一張
   小圖當一個字用（例如 `䞋` 條裡的 `w3-944.jpg` 夾在「又作嚫、▢、襯」中間）。
   直接 strip 標籤轉純文字會把那個字**整個吃掉**，而句子讀起來依然通順——
   這是最難發現的一種錯。本支一律把缺字圖換成 `▢` 佔位，並把檔名記進 `glyphs`。
2. **頁碼不要用「結尾抓 p\\d+」的正則。**原書頁碼包在
   `<span style="color: #942923">p8653</span>` 裡，有明確標記就用標記；
   而且 1,751 條「參見條」（詞目以 `→` 結尾）**沒有自己的頁碼**，
   它們的頁碼寫在內文「（參閱「大乘同性經」1087）」中，指的是別條的頁。
   混在一起會得到一批張冠李戴的頁碼。
3. **條數別拿 1988 年初版的「約 22,600 條」對帳。**這個檔是十冊增訂版，
   自報「總條目達三萬餘條，近三千幀圖表，近千萬言」——32,134 條／3,264 張圖／
   823 萬字元，三項都對得上。拿錯版本對帳會以為漏抓了三分之一。

## 存放

  正本    Drive `_corpus/fgs-dictionary/`（src/ 原始 mdx+mdd、images/ 全部圖）
  詞條    Drive `_corpus/fgs-dictionary/FGS.jsonl`（server/utils/glossaries.ts 直接讀）
  服務    R2 `fgs-dictionary/<檔名>`，由 server/api/glossary/image/[name] 串流
  索引    `data/research-data/dila-glossaries.json` 追加一列（進版控）

## 用法

  python scripts/fgs_dictionary_ingest.py --unpack    # 分卷 → ZIP → 解出 mdx/mdd
  python scripts/fgs_dictionary_ingest.py --parse     # MDX → FGS.jsonl
  python scripts/fgs_dictionary_ingest.py --images    # MDD → images/（Drive 正本）
  python scripts/fgs_dictionary_ingest.py --r2        # images/ → R2（可重跑，會略過已上傳）
  python scripts/fgs_dictionary_ingest.py --index     # 更新索引 JSON
  python scripts/fgs_dictionary_ingest.py --all
"""
from __future__ import annotations

import argparse
import glob
import html as htmllib
import json
import os
import re
import shutil
import sys
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DRIVE = Path("G:/我的雲端硬碟/資料/知識圖工作室/_corpus/fgs-dictionary")
SRC = DRIVE / "src"
IMAGES = DRIVE / "images"
OUT_JSONL = DRIVE / "FGS.jsonl"
INDEX = ROOT / "data" / "research-data" / "dila-glossaries.json"
DOWNLOADS = Path.home() / "Downloads"
PARTS = "佛光大辭典增訂版【阿彌陀佛】20230501.zip"
R2_PREFIX = "fgs-dictionary/"
CODE = "FGS"

# 原書頁碼有 **兩種** 寫法，只認一種會靜默漏掉約 800 條：
#   ① <span style="color: #942923">p8653</span>   （29,574 條，主要樣式）
#   ② 直接寫在正文尾巴的純文字 p1／p47／p66       （約 800 條，如【一】【一休和尚】）
# 先抓 ①，沒有再退回 ② 去看純文字的尾巴。
PAGE_SPAN = re.compile(r'<span[^>]*color:\s*#942923[^>]*>\s*p\s*(\d{1,5})\s*</span>', re.I)
PAGE_TAIL = re.compile(r"p\s?(\d{1,5})\s*$")
IMG = re.compile(r'<img[^>]*?src\s*=\s*["\']?([^"\'>\s]+)[^>]*>', re.I)
TAG = re.compile(r"<[^>]+>")
# 缺字圖 vs 插圖：缺字圖檔名是 w3-944 / s1-22 這種，插圖是 31129_1-p93 這種
GLYPH_NAME = re.compile(r"^[a-z]+\d*-\d+[a-z]?$", re.I)


def die(msg: str) -> None:
    print(f"✗ {msg}")
    raise SystemExit(1)


# ── 分卷 → ZIP → 解出 ────────────────────────────────────────────────────
def unpack() -> None:
    parts = sorted(DOWNLOADS.glob(PARTS + ".0*"))
    if not parts:
        die(f"下載區找不到 {PARTS}.001 等分卷")
    SRC.mkdir(parents=True, exist_ok=True)
    zpath = SRC / "fgs.zip"
    with zpath.open("wb") as out:
        for p in parts:
            print(f"  併入 {p.name}  {p.stat().st_size:,} bytes")
            with p.open("rb") as f:
                shutil.copyfileobj(f, out)
    head = zpath.open("rb").read(4)
    if head != b"PK\x03\x04":
        die(f"接起來不是 ZIP（開頭 {head!r}）——分卷順序或檔案本身有問題")
    with zipfile.ZipFile(zpath) as z:
        for info in z.infolist():
            print(f"  解出 {info.filename}  {info.file_size:,} bytes")
            z.extract(info, SRC)
    print(f"✓ 已解出到 {SRC}")


def mdx_path() -> str:
    hits = glob.glob(str(SRC / "*.mdx"))
    if not hits:
        die("找不到 .mdx，先跑 --unpack")
    return hits[0]


def mdd_path() -> str:
    hits = glob.glob(str(SRC / "*.mdd"))
    if not hits:
        die("找不到 .mdd，先跑 --unpack")
    return hits[0]


# ── MDX → JSONL ─────────────────────────────────────────────────────────
def to_text(h: str) -> tuple[str, list[str], list[str]]:
    """HTML → (純文字, 插圖檔名, 缺字圖檔名)。

    缺字圖換成 ▢ 而不是刪掉——刪掉句子照樣通順，但少了一個字（見檔頭第 1 條）。
    """
    figs: list[str] = []
    glyphs: list[str] = []

    def sub_img(m: re.Match) -> str:
        name = os.path.basename(m.group(1))
        stem = os.path.splitext(name)[0]
        if GLYPH_NAME.match(stem):
            glyphs.append(name)
            return "▢"
        figs.append(name)
        return ""

    h = IMG.sub(sub_img, h)
    h = re.sub(r"<br\s*/?>", "\n", h, flags=re.I)
    t = htmllib.unescape(TAG.sub("", h))
    t = t.replace("\ufeff", "").replace("\xa0", " ")
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n", t)
    return t.strip(), figs, glyphs


def parse() -> None:
    from mdict_utils.reader import MDX

    mdx = MDX(mdx_path())
    DRIVE.mkdir(parents=True, exist_ok=True)
    rows, seen = [], set()
    n_page = n_fig = n_glyph = 0
    dup = 0
    for k, v in mdx.items():
        term = k.decode("utf-8", "replace").strip()
        if term.startswith("0000說明"):
            continue  # 詞典自己的說明頁，不是詞條
        raw = v.decode("utf-8", "replace")
        pm = PAGE_SPAN.search(raw)
        page = int(pm.group(1)) if pm else None
        body = PAGE_SPAN.sub("", raw)
        text, figs, glyphs = to_text(body)
        if page is None:
            # 樣式② 的回退：頁碼直接寫在正文尾巴
            tm = PAGE_TAIL.search(text)
            if tm:
                page = int(tm.group(1))
                text = text[: tm.start()].rstrip()
        # 釋義開頭會把詞目再寫一次，去掉以免與 term 重複
        if text.startswith(term):
            text = text[len(term):].lstrip()
        if not text:
            continue
        key = (term, text[:40])
        if key in seen:
            dup += 1
            continue
        seen.add(key)
        row = {"term": term, "variants": [], "domain": [], "definition": text}
        if page:
            row["page"] = page
            n_page += 1
        if figs:
            row["images"] = sorted(set(figs))
            n_fig += len(row["images"])
        if glyphs:
            row["glyphs"] = sorted(set(glyphs))
            n_glyph += len(row["glyphs"])
        rows.append(row)

    nl = chr(10)
    tmp = OUT_JSONL.with_suffix(".jsonl.part")
    tmp.write_text(nl.join(json.dumps(r, ensure_ascii=False) for r in rows) + nl,
                   encoding="utf-8")
    tmp.replace(OUT_JSONL)
    cjk = sum(len(re.findall(r"[\u4e00-\u9fff\u3400-\u4dbf]", r["definition"])) for r in rows)
    arrow = sum(1 for r in rows if r["term"].endswith("→"))
    print(f"✓ {len(rows):,} 條 → {OUT_JSONL}")
    print(f"  釋義漢字 {cjk:,}；帶原書頁碼 {n_page:,}（{n_page/len(rows):.1%}）")
    print(f"  插圖引用 {n_fig:,}；缺字圖引用 {n_glyph:,}（已換成 ▢ 不是刪掉）")
    print(f"  參見條（詞目以 → 結尾，本來就沒有自己的頁碼）{arrow:,}")
    if dup:
        print(f"  重複條目略過 {dup}")
    short = [r for r in rows if len(r["definition"]) < 8]
    print(f"  釋義短於 8 字 {len(short)} 條" + (f"（例：{short[0]['term']}）" if short else ""))


# ── MDD → images/ ───────────────────────────────────────────────────────
def referenced_images() -> set[str]:
    """FGS.jsonl 裡真的被引用到的圖檔名。"""
    if not OUT_JSONL.exists():
        die("先跑 --parse：要先知道哪些圖被引用，才知道哪些該收")
    ref: set[str] = set()
    for line in OUT_JSONL.open(encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        ref.update(r.get("images") or [])
        ref.update(r.get("glyphs") or [])
    return ref


def extract_images() -> None:
    """只抽「詞條真的引用到的」圖。

    ⚠️ 不要照單全收 .mdd 裡的圖：那裡面混著 iOS app 的啟動畫面與圖示
    （Default-512h@2x.png、Default-Landscape@2x~ipad.png…共 38 張、4.1 MB），
    那是 app 外殼不是辭典內容。以引用清單為準，順便讓「引用了卻沒抽到」
    這種破圖在這一步就現形。
    """
    from mdict_utils.reader import MDD

    ref = referenced_images()
    IMAGES.mkdir(parents=True, exist_ok=True)
    mdd = MDD(mdd_path())
    n = skipped = other = chrome = 0
    got: set[str] = set()
    for k, v in mdd.items():
        name = k.decode("utf-8", "replace").replace("\\", "/").lstrip("/")
        base = os.path.basename(name)
        if not base.lower().endswith((".jpg", ".jpeg", ".png", ".gif")):
            other += 1
            continue
        if base not in ref:
            chrome += 1
            continue
        got.add(base)
        dest = IMAGES / base
        if dest.exists() and dest.stat().st_size == len(v):
            skipped += 1
            continue
        dest.write_bytes(v)
        n += 1
    # 先前版本收過 app 外殼，重跑時清掉
    for f in list(IMAGES.glob("*")):
        if f.name not in ref:
            f.unlink()
            chrome += 1
    total = sum(f.stat().st_size for f in IMAGES.glob("*"))
    print(f"✓ 圖片 {n:,} 張新寫入／{skipped:,} 張已存在 → {IMAGES}")
    print(f"  目錄合計 {total/1024/1024:.1f} MB；引用 {len(ref):,} 張")
    print(f"  略過 app 外殼與未引用資源 {chrome} 張、非圖片資源 {other} 個"
          f"（s3db／xml／ttf 等，不收）")
    missing = sorted(ref - got)
    if missing:
        print(f"  ❌ 引用了卻在 .mdd 裡找不到 {len(missing)} 張（例：{missing[:5]}）")
    else:
        print("  ✅ 引用到的圖一張不缺")


# ── images/ → R2 ────────────────────────────────────────────────────────
def to_r2() -> None:
    import boto3

    env = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8-sig").splitlines():
        if "=" in line and not line.startswith("#"):
            k, val = line.split("=", 1)
            env[k.strip()] = val.strip().strip('"').strip("'")
    s3 = boto3.client("s3", region_name="auto", endpoint_url=env["R2_ENDPOINT"],
                      aws_access_key_id=env["R2_ACCESS_KEY"],
                      aws_secret_access_key=env["R2_SECRET_KEY"])
    bucket = env["R2_BUCKET"]

    have = {}
    token = None
    while True:
        kw = {"Bucket": bucket, "Prefix": R2_PREFIX}
        if token:
            kw["ContinuationToken"] = token
        r = s3.list_objects_v2(**kw)
        for o in r.get("Contents") or []:
            have[o["Key"]] = o["Size"]
        if not r.get("IsTruncated"):
            break
        token = r.get("NextContinuationToken")
    print(f"  R2 上已有 {len(have):,} 個 {R2_PREFIX} 物件")

    files = sorted(IMAGES.glob("*"))
    up = skip = 0
    for f in files:
        key = R2_PREFIX + f.name
        if have.get(key) == f.stat().st_size:
            skip += 1
            continue
        ct = "image/png" if f.suffix.lower() == ".png" else "image/jpeg"
        s3.upload_file(str(f), bucket, key, ExtraArgs={"ContentType": ct})
        up += 1
        if up % 250 == 0:
            print(f"    上傳 {up:,}／{len(files):,}")
    print(f"✓ 上傳 {up:,} 張／略過 {skip:,} 張（已存在且大小相同）")


# ── 索引 ────────────────────────────────────────────────────────────────
def write_index() -> None:
    d = json.loads(INDEX.read_text(encoding="utf-8"))
    rows = [r for r in d["rows"] if r.get("code") != CODE]
    n = sum(1 for _ in OUT_JSONL.open(encoding="utf-8")) if OUT_JSONL.exists() else 0
    imgs = len(list(IMAGES.glob("*"))) if IMAGES.exists() else 0
    rows.append({
        "code": CODE,
        "title": "佛光大辭典增訂版",
        "blurb": "佛光山《佛光大辭典》增訂版（全十冊）。三萬餘條、近千萬言、近三千幀圖表，"
                 "收典籍語彙、古則公案、偈語、寺塔、人氏、事件、宗派團體、藝術與器物。"
                 "本站所收版本每條末尾保留原書頁碼，可直接作註腳。",
        "license": "⚠️ 使用者 2026-09-11 表示已取得佛光山授權。"
                   "但本站所據檔案為網路流傳的 MDict 版（其 .mdd 內含 fgsdict.s3db 與 "
                   "iOS entitlements，係由佛光山官方 app 拆包製成），"
                   "並非佛光山交付的授權資料檔。對外開放前須向佛光山確認授權範圍。",
        "rights": "by-permission",
        "files": [],
        "listed_name": "佛光大辭典增訂版【阿彌陀佛】20230501（MDict）",
        "downloaded": PARTS + ".001/.002/.003",
        "bytes": 54025659,
        "entries": n,
        "images": imgs,
        "source_kind": "mdict",
    })
    d["rows"] = rows
    d["count"] = len(rows)
    d["note"] = (d.get("note") or "").split("⚠️ FGS")[0].rstrip() + \
        "　⚠️ FGS（佛光大辭典）不是法鼓那批，正本在 _corpus/fgs-dictionary/，授權另計。"
    INDEX.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✓ 索引已更新：{len(rows)} 部，FGS {n:,} 條／{imgs:,} 張圖 → {INDEX}")


def main() -> int:
    ap = argparse.ArgumentParser()
    for flag in ("unpack", "parse", "images", "r2", "index", "all"):
        ap.add_argument(f"--{flag}", action="store_true")
    a = ap.parse_args()
    if not any(vars(a).values()):
        ap.print_help()
        return 0
    if not DRIVE.parent.parent.exists():
        die("G: 沒掛載——先修 Drive（見 CLAUDE.md），別寫進一個不存在的路徑")
    if a.unpack or a.all:
        unpack()
    if a.parse or a.all:
        parse()
    if a.images or a.all:
        extract_images()
    if a.r2 or a.all:
        to_r2()
    if a.index or a.all:
        write_index()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
