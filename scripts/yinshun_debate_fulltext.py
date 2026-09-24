"""人間佛教論爭：Drive 原檔（PDF／HTML／MD）→ 全文 .txt → Drive `_全文` ＋ R2 ＋ 站上索引。

    python -X utf8 scripts/yinshun_debate_fulltext.py            # 全部走一輪（可中斷，重跑接續）
    python -X utf8 scripts/yinshun_debate_fulltext.py --no-ocr   # 只做有文字層的，掃描檔先記在佇列
    python -X utf8 scripts/yinshun_debate_fulltext.py --status   # 印進度表（含分母）
    python -X utf8 scripts/yinshun_debate_fulltext.py --only <相對路徑> --force

來源夾：Drive `研究資料\\印順學派與弘誓\\人間佛教論爭\\`（含子夾 西方與中文學界、復原主義比較）。
輸出：
- Drive `_全文\\<相對路徑去副檔名>.txt`（成品正本，不進 git）
- R2 `yinshun-hongshi-fulltext/人間佛教論爭/<相對路徑去副檔名>.txt`（站上「全文」按鈕讀這裡）
- R2 `yinshun-hongshi/人間佛教論爭/<相對路徑>`：原檔 ≤30MB 才上（R2 只放小衍生物；大檔留 Drive，
  本機跑站時 yinshun-hongshi-file 端點會直接讀 Drive）
- 站上索引 public/content/research-data/yinshun-hongshi/debate-index.json（進 git）
- 進度檔 Drive `_全文\\_status.json`（每檔一筆，每做完一檔就寫回；筆電休眠中斷後重跑從缺口接）

頁碼：每頁前一行 `【頁 N】`＝頁面上**印出來的**頁碼（書眉／頁腳讀到、且與全篇的頁序位移一致才算）；
讀不到印刷頁碼的頁寫 `【PDF 頁 N】`（檔案裡的第幾張），**不推算、不流水重編**。
掃描檔（每頁字數過少，或只有掃描器附的隱形 OCR 層）走 OCR：英文走本機 MinerU（CPU，不搶夜班 GPU 鎖）；
中日文（多為直排）走 Gemini Vision。
🚨 日文不可過 OpenCC；中文來源若是簡體才轉繁（s2tw＋TRAD_FIXES），判準是簡體專用字密度＋無假名。
🚨 Gemini 連續兩次配額錯就整場停 OCR、放回佇列（下一輪再接），不要把各把 key 燒光。
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.stdout.reconfigure(encoding="utf-8")

import yinshun_japan_bilingual as yj  # noqa: E402  直排／雙欄切行、R2 client 共用

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\研究資料\印順學派與弘誓\人間佛教論爭")
OUT = SRC / "_全文"
STATUS = OUT / "_status.json"
OCR_SIDE = OUT / "_ocr"
INDEX_OUT = ROOT / "public" / "content" / "research-data" / "yinshun-hongshi" / "debate-index.json"
R2_TXT = "yinshun-hongshi-fulltext/人間佛教論爭/"
R2_SRC = "yinshun-hongshi/人間佛教論爭/"
MAX_R2_SRC = 30 * 1024 * 1024
EXTS = {".pdf", ".html", ".htm", ".md"}
ROOT_GROUP = "論爭核心文獻"
MINERU_PY = ROOT / "_mineru_venv" / "Scripts" / "python.exe"
QUOTA_SIGNS = ("exhausted", "429", "quota", "resource_exhausted", "rate limit")

# ── 共用 ─────────────────────────────────────────────────────────────────────
_KANA = re.compile(r"[぀-ヿ]")
_CJK = re.compile(r"[一-鿿]")
# 簡體專用字（繁體文本裡不會出現）——拿來判「這篇是簡體」，不用 OpenCC 轉換前後比對（會把「祢」判成簡體）
_SIMP_ONLY = set("这们说为国时个来对发会经过还进没与应实现学习关于种样问题认识从义说论难头听书记该车长门马鸟鱼东乐买卖见观规视亲讲证评译谈语读谁调谓传伟佛华历图团围园圆")
_SIMP_ONLY -= set("佛")


def is_japanese(text: str) -> bool:
    return len(_KANA.findall(text)) > max(20, len(text) * 0.02)


def is_simplified(text: str) -> bool:
    cjk = len(_CJK.findall(text))
    # 西文論文裡夾的漢字多是引用的書名與術語（Hsu 2022 夾日文書名「日本の社会参加仏教」）：整篇不轉
    if cjk < 50 or is_japanese(text) or len(re.findall(r"[A-Za-z]", text)) > cjk:
        return False
    return sum(1 for ch in text if ch in _SIMP_ONLY) / cjk > 0.015


def maybe_trad(text: str) -> tuple[str, bool]:
    if not is_simplified(text):
        return text, False
    from parse_drive_inventory import to_traditional
    return to_traditional(text), True


def parse_name(rel: str) -> dict:
    """`年_作者_題名…` → 年／作者／題名。年份不是四位數（如「年待核」）就留空。"""
    p = Path(rel)
    stem = p.stem
    parts = stem.split("_")
    year = parts[0] if re.fullmatch(r"\d{4}", parts[0]) else ""
    if len(parts) >= 3 and (year or parts[0].startswith("年")):
        author, title = parts[1], "　".join(parts[2:])
    else:
        author, title = "", stem.replace("_", "　")
    if re.fullmatch(r"[\x00-\x7f　]+", title):
        title = title.replace("-", " ").replace("　", "：", 1).replace("　", " ")
    group = p.parts[0] if len(p.parts) > 1 else ROOT_GROUP
    return {"year": year, "author": author, "title": title, "group": group}


def load_status() -> dict:
    if STATUS.exists():
        return json.loads(STATUS.read_text(encoding="utf-8"))
    return {}


def save_status(st: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = STATUS.with_suffix(".tmp")
    tmp.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(STATUS)


def fingerprint(p: Path) -> str:
    s = p.stat()
    return f"{s.st_size}-{int(s.st_mtime)}"


def txt_path(rel: str) -> Path:
    return OUT / Path(rel).with_suffix(".txt")


# ── HTML ─────────────────────────────────────────────────────────────────────
class _Text(HTMLParser):
    BLOCK = {"p", "br", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li", "tr", "table", "blockquote",
             "section", "article", "dd", "dt", "hr", "pre", "title"}
    SKIP = {"script", "style", "noscript", "head"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out: list[str] = []
        self.skip = 0
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self._in_title = True
        if tag in self.SKIP:
            self.skip += 1
        if tag in self.BLOCK:
            self.out.append("\n")

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag in self.SKIP and self.skip:
            self.skip -= 1
        if tag in self.BLOCK:
            self.out.append("\n")

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if not self.skip:
            self.out.append(data)


def decode_html(raw: bytes) -> str:
    head = raw[:4000].decode("ascii", "ignore").lower()
    m = re.search(r"charset\s*=\s*[\"']?([a-z0-9_\-]+)", head)
    cands = []
    if m:
        cands.append(m.group(1))
    cands += ["utf-8", "big5hkscs", "cp950", "gb18030"]
    for enc in cands:
        try:
            return raw.decode(enc)
        except (LookupError, UnicodeDecodeError):
            continue
    return raw.decode("cp950", errors="replace")


def html_to_text(raw: bytes) -> str:
    s = decode_html(raw)
    # Wayback 工具列整段拿掉
    s = re.sub(r"<!--\s*BEGIN WAYBACK TOOLBAR INSERT\s*-->.*?<!--\s*END WAYBACK TOOLBAR INSERT\s*-->", "", s, flags=re.S)
    p = _Text()
    p.feed(s)
    text = html.unescape("".join(p.out)).replace("\xa0", " ").replace("\u3000", "　")
    lines = [re.sub(r"[ \t\r\f\v]+", " ", ln).strip() for ln in text.split("\n")]
    lines = [ln for ln in lines if ln]
    cb = re.compile(r"[A-Z]{1,2}\d+n\d+_p(\d{4})[a-c]\d{2}")
    joined = "\n".join(lines)
    if len(cb.findall(joined)) > 10:
        # CBETA 行號（Y43n0041_p0221a01＝《印順法師佛學著作集》第 43 冊頁 221 上欄第 1 行），有的獨立成行、
        # 有的夾在字中間：換頁處轉成【頁 N】（這就是原書頁碼），其餘行號拿掉
        seen = [None]

        def sub(m):
            pg = int(m.group(1))
            if pg != seen[0]:
                seen[0] = pg
                return f"\n\n【頁 {pg}】\n\n"
            return ""
        joined = cb.sub(sub, joined)
        paras = [re.sub(r"\s*\n\s*", "", x).strip() for x in re.split(r"\n{2,}", joined)]
        return "\n\n".join(x for x in paras if x) + "\n"
    return "\n\n".join(lines) + "\n"


# ── PDF（有文字層） ───────────────────────────────────────────────────────────
_NUM_AT = re.compile(r"^\D{0,3}?(\d{1,4})(?!\d)|(?<!\d)(\d{1,4})\D{0,3}$")


def page_number_candidates(page) -> set[int]:
    """頁面上下緣（上 10%、下 10%）短行裡出現在行首或行尾的數字。"""
    H = page.rect.height
    cands: set[int] = set()
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            y0, y1 = l["bbox"][1], l["bbox"][3]
            if not (y1 < H * 0.1 or y0 > H * 0.9):
                continue
            t = re.sub(r"\s+", "", "".join(s["text"] for s in l["spans"]))
            if not t or len(t) > 60:
                continue
            for m in _NUM_AT.finditer(t):
                v = m.group(1) or m.group(2)
                if v:
                    cands.add(int(v))
    return cands


def printed_pages(doc) -> list[int | None]:
    """每頁的印刷頁碼：頁序與頁碼的位移（遞增或遞減）要有多數頁支持，且該頁真的印著那個數字才算。"""
    n = len(doc)
    cands = [page_number_candidates(p) for p in doc]
    from collections import Counter
    votes: Counter = Counter()
    for i, cs in enumerate(cands):
        for v in cs:
            votes[("+", v - i)] += 1
            votes[("-", v + i)] += 1
    if not votes:
        return [None] * n
    (sign, off), cnt = votes.most_common(1)[0]
    if cnt < max(2, int(n * 0.3)):
        return [None] * n
    out = []
    for i, cs in enumerate(cands):
        v = off + i if sign == "+" else off - i
        out.append(v if v in cs and v > 0 else None)
    return out


def column_clips(page):
    """中文雙欄欄距窄（林建德 2011《佛教圖書館館刊》約 3 字寬），逐行併基線會把左右兩欄同一高度的
    兩行接成一行。先用文字 block 找一條沒有 block 跨過的縱向欄縫，找到就回傳
    [通欄頂部, 左欄, 右欄, 通欄底部] 四塊 clip；找不到回 None（單欄，照舊整頁讀）。"""
    import fitz
    W, H = page.rect.width, page.rect.height
    blocks = [b for b in page.get_text("blocks") if b[6] == 0 and b[4].strip()
              and H * 0.06 < (b[1] + b[3]) / 2 < H * 0.94]
    tot = sum(len(b[4]) for b in blocks) or 1
    scores = {}
    for gx in range(int(W * 0.35), int(W * 0.65)):
        cross = [b for b in blocks if b[0] < gx - 1 and b[2] > gx + 1]
        left = sum(len(b[4]) for b in blocks if b[2] <= gx + 1)
        right = sum(len(b[4]) for b in blocks if b[0] >= gx - 1)
        if left / tot < 0.25 or right / tot < 0.25:
            continue
        scores[gx] = sum(len(b[4]) for b in cross)
    if not scores or min(scores.values()) / tot > 0.25:
        return None
    # 取最低跨越量那一段欄縫的正中間：貼著欄邊切，clip 會把相鄰那一欄行尾的字也收進來
    lo = min(scores.values())
    runs, cur = [], []
    for gx in sorted(scores):
        if scores[gx] == lo and (not cur or gx == cur[-1] + 1):
            cur.append(gx)
        else:
            if cur:
                runs.append(cur)
            cur = [gx] if scores[gx] == lo else []
    if cur:
        runs.append(cur)
    run = max(runs, key=len)
    gx = run[len(run) // 2]
    colb = [b for b in blocks if b[2] <= gx + 1 or b[0] >= gx - 1]
    ytop = min(b[1] for b in colb)
    ybot = max(b[3] for b in colb)
    return [fitz.Rect(0, 0, W, ytop), fitz.Rect(0, ytop, gx, ybot + 1),
            fitz.Rect(gx, ytop, W, ybot + 1), fitz.Rect(0, ybot + 1, W, H)]


def items_to_paras(items: list[dict]) -> list[str]:
    paras: list[str] = []
    for it in items:
        t = it["text"].strip()
        if not t:
            continue
        if paras and not it["start"]:
            paras[-1] = yj._join(paras[-1], t)
        else:
            paras.append(t)
    return paras


def pdf_text(pdf: Path) -> tuple[str, int, int]:
    """回傳 (全文, 頁數, 讀到印刷頁碼的頁數)。"""
    import fitz
    doc = fitz.open(pdf)
    heads = yj._running_heads(doc, 0)
    vheads = yj.vertical_running_heads(doc, 0)
    pnums = printed_pages(doc)
    out = []
    for i, page in enumerate(doc):
        pn = pnums[i]
        if yj.vertical_ratio(page) >= 0.5:
            items, _ = yj.vertical_page_items(page, vheads | heads, pn)
        else:
            clips = column_clips(page)
            if clips:
                items = []
                for c in clips:
                    items += yj.horizontal_page_items(page, heads, pn, clip=c)[0]
            else:
                items, _ = yj.horizontal_page_items(page, heads, pn)
        paras = items_to_paras(items)
        out.append((f"【頁 {pn}】" if pn else f"【PDF 頁 {i + 1}】") + "\n\n" + "\n\n".join(paras))
    return "\n\n".join(out) + "\n", len(doc), sum(1 for x in pnums if x)


def pdf_is_scanned(pdf: Path) -> tuple[bool, int, float]:
    import fitz
    doc = fitz.open(pdf)
    cs = [len(re.sub(r"\s", "", p.get_text())) for p in doc]
    low = sum(1 for c in cs if c < 100)
    # 掃描器附的隱形 OCR 層（HiddenHorzOCR／HiddenVertOCR）：字有，但直排讀序全亂、錯字多（林建德 2003
    # 香光莊嚴兩篇「印順法帥」「悲哀」拆散），當掃描檔重新 OCR
    hidden = any("HiddenHorzOCR" in f[3] or "HiddenVertOCR" in f[3] for pg in list(doc)[:3] for f in pg.get_fonts())
    return (low >= len(cs) * 0.6 or hidden), len(cs), (sum(cs) / max(len(cs), 1))


# ── OCR ─────────────────────────────────────────────────────────────────────
def ocr_mineru(pdf: Path, lang: str) -> tuple[str, int, int]:
    with tempfile.TemporaryDirectory(prefix="debate_mineru_") as td:
        out = Path(td) / "o.jsonl"
        r = subprocess.run([str(MINERU_PY), "-X", "utf8", str(ROOT / "scripts" / "mineru_ocr.py"), "run",
                            "--pdf", str(pdf), "--out", str(out), "--lang", lang, "--device", "cpu"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0 or not out.exists():
            raise RuntimeError(f"MinerU exit {r.returncode}：{((r.stdout or '') + (r.stderr or ''))[-300:]}")
        chunks = [json.loads(x) for x in out.read_text(encoding="utf-8").splitlines() if x.strip()]
    pages = []
    found = 0
    for c in sorted(chunks, key=lambda c: c["page_number"]):
        pn = c.get("printed_page")
        found += 1 if pn else 0
        body = c.get("content") or ""
        main, _, notes = body.partition("—" * 15)
        paras = []
        for blk in re.split(r"\n\s*\n", main):
            t = ""
            for ln in blk.splitlines():
                t = yj._join(t, ln.strip()) if t else ln.strip()
            if t:
                paras.append(t)
        if notes.strip():
            paras.append("—" * 10)
            paras += [ln.strip() for ln in notes.splitlines() if ln.strip()]
        pages.append((f"【頁 {pn}】" if pn else f"【PDF 頁 {c['page_number']}】") + "\n\n" + "\n\n".join(paras))
    return "\n\n".join(pages) + "\n", len(chunks), found


GEMINI_PROMPT = """這是{lang}文獻〈{title}〉的掃描 PDF 片段，共 {k} 個 PDF 頁。請逐頁完整轉錄原文，
輸出 JSON：{{"pages":[{{"page":1,"text":"..."}}]}}，"page" 是這份片段裡的 1-based 頁次。

"text" 的規則：
1. 原樣轉錄：舊字體、歷史假名遣照印（「佛敎」「云ふ」照舊），不可改成新字體或簡體、不可改寫、不可翻譯、不可摘要。
2. 每一個**印刷頁**以單獨一行 `【頁 N】` 開頭，N 是該頁上**印出來的頁碼**（漢數字也轉成阿拉伯數字）。
   一個 PDF 頁若是左右兩個印刷頁（跨頁掃描），就分成兩個 `【頁 N】` 區塊，按閱讀順序（直排書右頁在前）。
   頁面上看不到頁碼就寫 `【頁 ?】`——**絕對不要用前後頁推算**。
3. 閱讀順序：直排（縱書）每行由上而下、行序由右而左；頁面分上下段時先讀完上段再讀下段。
4. 不轉錄書眉（書名、章名與頁碼那一行）與圖書館浮水印。
5. 一個自然段寫成一行；章節標題自成一行；段與段之間用 `¶` 分隔（JSON 裡的換行會被吃掉）。
6. 註釋、表格照樣轉錄；圖只寫圖說；空白頁寫 `（空白）`。
只輸出 JSON，不要任何說明。"""


def ocr_gemini(pdf: Path, rel: str, lang_label: str, title: str, batch: int = 2) -> tuple[str | None, int, int, str]:
    """逐批 Gemini OCR，每批寫回 `_ocr/<名>.json`（可續跑）。回傳 (全文或 None, 頁數, 有頁碼的印刷頁數, 錯誤)。"""
    import fitz
    from ocr_pdf_to_text import ocr_pdf
    OCR_SIDE.mkdir(parents=True, exist_ok=True)
    side = OCR_SIDE / (hashlib.md5(rel.encode("utf-8")).hexdigest()[:12] + ".json")
    got: dict[str, str] = json.loads(side.read_text(encoding="utf-8")) if side.exists() else {}
    n = len(fitz.open(pdf))
    for s in range(1, n + 1, batch):
        rng = list(range(s, min(s + batch - 1, n) + 1))
        if all(str(i) in got for i in rng):
            continue
        prompt = GEMINI_PROMPT.format(lang=lang_label, title=title, k=len(rng))
        t0 = time.time()
        try:
            pages = ocr_pdf(pdf, model=yj.OCR_MODEL, pages=(rng[0], rng[-1]), prompt=prompt)
        except Exception as ex:  # noqa: BLE001
            return None, n, 0, str(ex)[-300:]
        texts = {int(p["page"]): (p.get("text") or "") for p in pages}
        if set(texts) != set(rng) and len(pages) == len(rng):
            texts = {i: (p.get("text") or "") for i, p in zip(rng, pages)}
        for i in rng:
            t = texts.get(i, "")
            if not t.strip():
                side.write_text(json.dumps(got, ensure_ascii=False, indent=1), encoding="utf-8")
                return None, n, 0, f"PDF 頁 {i} 回空"
            got[str(i)] = t
        side.write_text(json.dumps(got, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"    Gemini OCR pp{rng[0]}-{rng[-1]} ✓ {time.time() - t0:.0f}s（{len(got)}/{n}）", flush=True)
    out, found = [], 0
    for i in range(1, n + 1):
        t = got[str(i)].replace("¶", "\n\n").strip()
        # 【頁 N】/【頁 ?】 → 讀到頁碼的保留；? 換成 PDF 頁
        def sub(m):
            nonlocal found
            v = m.group(1).strip()
            if re.fullmatch(r"\d{1,4}", v):
                found += 1
                return f"\n\n【頁 {v}】\n\n"
            return f"\n\n【PDF 頁 {i}】\n\n"
        if not t.startswith("【頁"):
            t = f"【PDF 頁 {i}】\n\n" + t
        t = re.sub(r"【頁\s*([^】]*)】", sub, t)
        out.append(re.sub(r"\n{3,}", "\n\n", t).strip())
    return "\n\n".join(out) + "\n", n, found, ""


# ── R2 ──────────────────────────────────────────────────────────────────────
_s3 = [None, None]


def s3():
    if _s3[0] is None:
        _s3[0], _s3[1] = yj.r2_client()
    return _s3[0], _s3[1]


def put(key: str, body: bytes, ctype: str) -> None:
    c, b = s3()
    for i in range(4):
        try:
            c.put_object(Bucket=b, Key=key, Body=body, ContentType=ctype)
            return
        except Exception as ex:  # noqa: BLE001
            if i == 3:
                raise
            print(f"    R2 重試（{type(ex).__name__}）", flush=True)
            time.sleep(5 * (i + 1))


CTYPE = {".pdf": "application/pdf", ".html": "text/html; charset=utf-8", ".htm": "text/html; charset=utf-8",
         ".md": "text/markdown; charset=utf-8"}


# ── 主流程 ───────────────────────────────────────────────────────────────────
def walk() -> list[str]:
    rels = []
    for p in sorted(SRC.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in EXTS:
            continue
        rel = p.relative_to(SRC).as_posix()
        if rel.startswith("_全文/") or rel.split("/")[0].startswith("_"):
            continue
        rels.append(rel)
    stems = [str(Path(r).with_suffix("")) for r in rels]
    dup = {s for s in stems if stems.count(s) > 1}
    if dup:
        raise SystemExit(f"同名不同副檔名會撞全文 key：{sorted(dup)}")
    return rels


def lang_of(rel: str) -> str:
    stem = Path(rel).stem
    if _KANA.search(stem):
        return "ja"
    if re.fullmatch(r"[\x00-\x7f]+", stem.split("_", 2)[-1] if "_" in stem else stem):
        return "en"
    return "zh"


def finish(rel: str, st: dict, text: str, method: str, pages: int, printed: int) -> None:
    text, conv = maybe_trad(text) if lang_of(rel) != "ja" and not is_japanese(text) else (text, False)
    tp = txt_path(rel)
    tp.parent.mkdir(parents=True, exist_ok=True)
    tp.write_text(text, encoding="utf-8")
    body_chars = len(re.sub(r"\s|【(PDF )?頁 [^】]*】", "", text))
    put(R2_TXT + str(Path(rel).with_suffix(".txt").as_posix()), text.encode("utf-8"), "text/plain; charset=utf-8")
    src = SRC / rel
    r2src = False
    if src.stat().st_size <= MAX_R2_SRC:
        put(R2_SRC + rel, src.read_bytes(), CTYPE.get(src.suffix.lower(), "application/octet-stream"))
        r2src = True
    st[rel] = {"state": "done", "method": method, "pages": pages, "printedPages": printed,
               "chars": body_chars, "s2t": conv, "r2Source": r2src, "fp": fingerprint(src),
               "at": time.strftime("%Y-%m-%d %H:%M")}
    print(f"  ✓ {rel}：{method} {pages or ''}頁 {body_chars} 字" + (f"（印刷頁碼 {printed}/{pages}）" if pages else "")
          + ("（簡→繁）" if conv else "") + ("" if r2src else "（原檔 >30MB 留 Drive）"), flush=True)


def process(rel: str, st: dict, do_ocr: bool, force: bool, gem: dict) -> None:
    src = SRC / rel
    old = st.get(rel, {})
    if not force and old.get("state") == "done" and old.get("fp") == fingerprint(src) and txt_path(rel).exists():
        return
    ext = src.suffix.lower()
    try:
        if ext in (".html", ".htm"):
            finish(rel, st, html_to_text(src.read_bytes()), "html", 0, 0)
        elif ext == ".md":
            finish(rel, st, src.read_text(encoding="utf-8"), "md", 0, 0)
        else:
            scanned, n, cpp = pdf_is_scanned(src)
            if not scanned:
                text, n, found = pdf_text(src)
                finish(rel, st, text, "text", n, found)
                return
            lang = lang_of(rel)
            engine = "mineru" if lang == "en" else "gemini"      # 英文橫排走 MinerU；中日文（多直排）走 Gemini
            st[rel] = {**old, "state": "ocr_pending", "method": engine, "pages": n, "fp": fingerprint(src),
                       "note": f"掃描檔（每頁平均 {cpp:.0f} 字）"}
            if not do_ocr:
                print(f"  … {rel}：掃描 {n} 頁，排入 OCR（{engine}）", flush=True)
                return
            if engine == "mineru":
                print(f"● MinerU OCR {rel}（{n} 頁，CPU）", flush=True)
                text, n2, found = ocr_mineru(src, "en" if lang == "en" else "ch")
                finish(rel, st, text, "ocr-mineru", n2, found)
            else:
                if gem["blocked"]:
                    print(f"  … {rel}：待 Gemini OCR（本輪配額已停）", flush=True)
                    return
                print(f"● Gemini OCR {rel}（{n} 頁）", flush=True)
                meta = parse_name(rel)
                text, n2, found, err = ocr_gemini(src, rel, "日文" if lang == "ja" else "中文", meta["title"])
                if text is None:
                    st[rel]["error"] = err
                    print(f"    ✗ Gemini OCR 中斷：{err[-160:]}", flush=True)
                    if any(k in err.lower() for k in QUOTA_SIGNS):
                        gem["streak"] += 1
                        if gem["streak"] >= 2:
                            gem["blocked"] = True
                            yj.block_gemini()
                            print("⛔ Gemini 連續兩次配額錯：本輪停止 OCR，放回佇列", flush=True)
                    return
                gem["streak"] = 0
                finish(rel, st, text, "ocr-gemini", n2, found)
    except Exception as ex:  # noqa: BLE001
        st[rel] = {**old, "state": "error", "error": str(ex)[-300:], "fp": fingerprint(src)}
        print(f"  ✗ {rel}：{str(ex)[-200:]}", flush=True)
    finally:
        save_status(st)


def write_index(rels: list[str], st: dict) -> None:
    rows = []
    for rel in rels:
        s = st.get(rel, {})
        meta = parse_name(rel)
        rows.append({
            "key": R2_SRC + rel,
            "title": meta["title"], "author": meta["author"], "year": meta["year"], "group": meta["group"],
            "format": {".htm": "html"}.get(Path(rel).suffix.lower(), Path(rel).suffix.lower().lstrip(".")),
            "pages": s.get("pages", 0), "chars": s.get("chars", 0),
            "status": s.get("state", "pending"), "method": s.get("method", ""),
            "printedPages": s.get("printedPages", 0), "r2Source": s.get("r2Source", False),
        })
    INDEX_OUT.parent.mkdir(parents=True, exist_ok=True)
    INDEX_OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"索引 {len(rows)} 筆 → {INDEX_OUT.relative_to(ROOT)}", flush=True)


def print_status(rels: list[str], st: dict) -> None:
    from collections import Counter
    c = Counter(st.get(r, {}).get("state", "pending") for r in rels)
    fmt = Counter(Path(r).suffix.lower() for r in rels)
    print(f"分母 {len(rels)} 檔（" + "、".join(f"{k} {v}" for k, v in sorted(fmt.items())) + "）")
    print("狀態：" + "、".join(f"{k} {v}" for k, v in c.items()))
    for r in rels:
        s = st.get(r, {})
        if s.get("state") != "done":
            print(f"  {s.get('state', 'pending'):12} {s.get('method', ''):7} {r}  {s.get('error', s.get('note', ''))[:100]}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-ocr", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--only")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    if not Path(r"G:\我的雲端硬碟").exists():
        raise SystemExit("⛔ G: 不見了（Drive 卡住），先重啟 GoogleDriveFS")
    rels = walk()
    st = load_status()
    if a.status:
        print_status(rels, st)
        return
    try:
        from keep_awake import keep_awake
        keep_awake()
    except Exception:  # noqa: BLE001
        pass
    gem = {"streak": 0, "blocked": yj.gemini_blocked()}
    todo = [r for r in rels if not a.only or r == a.only]
    # 先做有文字層／HTML／MD（快），掃描檔 OCR 壓後
    for rel in todo:
        process(rel, st, do_ocr=False, force=a.force, gem=gem)
    if not a.no_ocr:
        for rel in todo:
            if st.get(rel, {}).get("state") == "ocr_pending":
                process(rel, st, do_ocr=True, force=a.force, gem=gem)
    write_index(rels, st)
    left = [r for r in rels if st.get(r, {}).get("state") != "done"]
    print(f"本輪結束：分母 {len(rels)}，完成 {len(rels) - len(left)}，未完成 {len(left)}", flush=True)
    if not left:
        print("ALL_DONE", flush=True)


if __name__ == "__main__":
    main()
