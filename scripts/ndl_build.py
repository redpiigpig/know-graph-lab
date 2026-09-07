# -*- coding: utf-8 -*-
"""國立國會圖書館デジタルコレクション → 全集卷（ja＋繁中）的取源模組。

無教會譜系裡戰前那批全是公有領域，卻不在青空文庫、也不在 libgen——只有 NDL 的
掃描本。2026-09-06 逐一探過公開範圍，共 **33 部可直接取用**（畔上賢造 16、
矢內原忠雄 9、藤井武 7、內村鑑三 1）；黒崎幸吉、塚本虎二、南原繁三位數位化了
28／35／23 部卻全是館內限定（卒後 70 年未過）。清單見
.claude/skills/ebook-collected-works/ndl_open_scans.md。

**判公開範圍只有一個可靠辦法**：抓 `https://dl.ndl.go.jp/api/iiif/{pid}/manifest.json`，
200＝インターネット公開、404＝館內限定／個人送信。目錄 metadata 不帶這個欄位。
「圖書館‧個人送信」看起來可用，但**居住在日本境外者不能用**，別把它算進來。

兩個 API 分工：
  * `lab.ndl.go.jp/dl/api/book/{pid}`  書誌＋**目次**（分章靠它），偶爾 page=0
  * `dl.ndl.go.jp/api/iiif/{pid}/...`  影像（也是公開範圍的探針）

流程：目次分章 → 逐頁取影像 → Gemini Vision OCR（直排舊字舊假名）→ 段落重建 →
交 uchimura_auto 那套 checkpoint／翻譯／上架。純函式鎖在
scripts/tests/test_ndl_build.py。

  python scripts/ndl_build.py --probe 1099766          # 看書誌與分章
  python scripts/ndl_build.py --fetch 1099766          # 下載影像到快取
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

CACHE_DIR = Path("c:/tmp/ndl_cache")
LAB_API = "https://lab.ndl.go.jp/dl/api/book/{pid}"
IIIF_MANIFEST = "https://dl.ndl.go.jp/api/iiif/{pid}/manifest.json"
IIIF_IMAGE = "https://dl.ndl.go.jp/api/iiif/{pid}/R{img:07d}/full/{size}/0/default.jpg"

# 目次一條的三種寫法：
#   第一　教派ではない/1  (0003.jp2)      章名/印刷頁 (影像)
#   舊新約の二大預言とその成就 / 1 (0006.jp2)
#   充さるべき預言 / (0006.jp2)           無印刷頁
#   標題  (0002.jp2)                      前付（無斜線）
_TOC_RE = re.compile(r"^\s*(?P<title>.*?)\s*(?:/\s*(?P<page>[0-9０-９]*)\s*)?\((?P<img>\d+)\.jp2\)\s*$")

# 前付／後付：不是正文，分章時丟掉
FRONT_MATTER = {"標題", "目次", "奥付", "奧付", "口絵", "口繪", "序", "凡例", "扉"}


def parse_toc_entry(line: str) -> dict | None:
    """NDL 目次的一行 → {title, printed_page, image}；解析不出來回 None。"""
    m = _TOC_RE.match(line or "")
    if not m:
        return None
    title = m.group("title").strip().rstrip("/").strip()
    if not title:
        return None
    return {"title": title, "printed_page": (m.group("page") or "").strip(), "image": int(m.group("img"))}


def sections_from_index(index: list[str], total_images: int, fallback_title: str = "全文") -> list[dict]:
    """目次 → [{title, start, end}]（影像編號，end 為 exclusive）。

    前付（標題／目次／奥付…）丟掉；每一節結束於下一節開始，最後一節到全書末頁。
    目次整個缺席時（NDL 對某些書沒建目次）退回「整本一節」，讓管線仍能跑。"""
    entries = [e for e in (parse_toc_entry(l) for l in index) if e]
    body = [e for e in entries if e["title"] not in FRONT_MATTER]
    if not body:
        return [{"title": fallback_title, "printed_page": "", "start": 1, "end": total_images + 1}]
    out = []
    for i, e in enumerate(body):
        end = body[i + 1]["image"] if i + 1 < len(body) else total_images + 1
        out.append({"title": e["title"], "printed_page": e["printed_page"],
                    "start": e["image"], "end": max(end, e["image"] + 1)})
    return out


def image_url(pid: str, img: int, width: int | None = None) -> str:
    return IIIF_IMAGE.format(pid=pid, img=img, size=f"{width}," if width else "full")


# ── OCR 後處理 ───────────────────────────────────────────────────────────────
# 直排舊書的振り仮名，OCR 常整段括進正文：基督教（キリストけう）は
_RUBY_RE = re.compile(r"[（(][ぁ-んァ-ヶー・]{1,12}[）)]")
# 只有數字（含漢數字與全形）的行＝頁碼
_PAGENUM_RE = re.compile(r"^[\s0-9０-９一二三四五六七八九十百]+$")
_TERMINAL = ("。", "！", "？", "」", "』", "）", "…")


def clean_ocr_text(text: str) -> str:
    """Vision OCR 的一頁文字 → 乾淨段落（以空行分段）。"""
    out = []
    for block in re.split(r"\n\s*\n", text or ""):
        lines = []
        for ln in block.split("\n"):
            s = ln.strip().strip("　").strip()
            if not s or _PAGENUM_RE.match(s):
                continue
            lines.append(_RUBY_RE.sub("", s))
        joined = "".join(lines).strip()
        if joined:
            out.append(joined)
    return "\n\n".join(out)


def paragraphs_from_pages(pages: list[str]) -> list[str]:
    """逐頁文字 → 段落。直排書換頁不換段是常態，所以上一段沒有句末標點就接下去。"""
    paras: list[str] = []
    for page in pages:
        for p in [x for x in re.split(r"\n\s*\n", (page or "").strip()) if x.strip()]:
            p = p.strip()
            if paras and not paras[-1].endswith(_TERMINAL):
                paras[-1] = paras[-1] + p
            else:
                paras.append(p)
    return paras


def section_payload(section: dict, pages: dict) -> dict:
    """一節＋該書的 {影像號: OCR 文字} → 與 uchimura／howes 同形的 section dict。

    形狀（heading／title_zh／src／zh）必須與其他作者一致，才接得上 uchimura_auto
    的 checkpoint／翻譯／上架。`zh` 一開始是空的，翻譯那一步才填。
    `title_zh` 先擺日文原題而不留空——留空的話 reader 目錄會出現空白項。
    """
    texts = [pages[i] for i in range(section["start"], section["end"])
             if pages.get(i) and pages[i].strip()]
    return {
        "heading": section["title"],
        "title_zh": section["title"],
        "src": paragraphs_from_pages(texts),
        "zh": [],
    }


def is_spread(width: int, height: int) -> bool:
    """橫幅＝兩頁合成一張（見開き）。NDL 的掃描幾乎都是這種。"""
    return width > height


def split_spread_boxes(width: int, height: int) -> list:
    """跨頁 → [右半頁 box, 左半頁 box]，PIL crop 用的 (l, t, r, b)。

    🚨 **右半頁先讀**：日文直書右起，右半頁是前一頁。順序反了整本的文意會倒著接，
    而且每一頁單獨看都很正常 —— 這種錯不會有任何東西報警。
    """
    mid = width // 2
    return [(mid, 0, width, height), (0, 0, mid, height)]


def toc_match_ratio(ocr_text: str, titles: list) -> float:
    """OCR 出來的目次頁，對得上幾成 NDL 目次 API 給的章名（0.0–1.0）。

    這是**幻覺偵測的錨**：這批直排舊字材料最危險的失敗不是讀不出來，而是
    部分錨定的編造 —— 模型讀到零星字詞，再用通順日文把中間補起來，整頁毫無異狀。
    唯一能自動抓的辦法，是我們剛好有一頁的內容是已知的（目次頁），
    拿它當 canary：連已知答案都對不上，其餘各頁的內容一個字都不能信。
    """
    if not titles:
        return 0.0
    squash = re.compile(r"[\s　.．・…‥]+")
    hay = squash.sub("", ocr_text or "")
    hit = sum(1 for t in titles if squash.sub("", t) in hay)
    return hit / len(titles)


def refuse_empty_build(sections: list, pages: dict) -> bool:
    """所有 section 都沒有正文＝OCR 根本沒跑（或全失敗），該擋下不要寫檔。

    不擋的話會產出一整套結構正確、目錄齊全、每章卻都沒有字的 secN.json——
    頁面看起來完全正常。見 [[feedback_reader_silent_failures]]。
    """
    return not any(section_payload(s, pages)["src"] for s in sections)


# ── 網路（非純函式，測試不碰） ────────────────────────────────────────────────
def is_open(pid: str) -> bool:
    """インターネット公開＝IIIF manifest 回 200。館內限定／個人送信回 404。"""
    import requests
    try:
        return requests.get(IIIF_MANIFEST.format(pid=pid), timeout=25).status_code == 200
    except Exception:
        return False


def fetch_book(pid: str) -> dict:
    """書誌＋目次＋頁數。Lab API 的 page 偶爾為 0，那時回頭數 IIIF canvas。"""
    import requests
    d = requests.get(LAB_API.format(pid=pid), timeout=40).json()
    pages = int(d.get("page") or 0)
    if not pages:
        m = requests.get(IIIF_MANIFEST.format(pid=pid), timeout=40).json()
        seq = m.get("sequences") or []
        pages = len(seq[0]["canvases"]) if seq else len(m.get("items", []))
    return {"pid": pid, "title": d.get("title", ""), "author": d.get("responsibility", ""),
            "publisher": d.get("publisher", ""), "year": d.get("published", ""),
            "pages": pages, "index": d.get("index") or []}


def fetch_images(pid: str, start: int, end: int, width: int = 1800,
                 cache_dir: Path = CACHE_DIR) -> list[Path]:
    """把 [start, end) 的影像抓下來（已存在就跳過）。回傳本機路徑。"""
    import time
    import requests
    d = cache_dir / pid
    d.mkdir(parents=True, exist_ok=True)
    out = []
    for i in range(start, end):
        p = d / f"{i:07d}.jpg"
        if not p.exists():
            r = requests.get(image_url(pid, i, width), timeout=90)
            r.raise_for_status()
            p.write_bytes(r.content)
            time.sleep(0.8)  # NDL 是公共資源，節流
        out.append(p)
    return out


OCR_PROMPT = """この画像は戦前日本の書籍を縦書きで印刷したページのスキャンです。
本文をそのまま文字に起こしてください。

規則：
1. **旧字体・旧仮名遣いはそのまま残す**（教會→教会 のような新字体への変換は禁止）。
2. 振り仮名（ルビ）は出力しない。
3. ページ番号・柱（ノンブル、書名や章名の繰り返し）は出力しない。
4. 段落は空行で区切る。原文の改行は段落の区切りではないので、
   文が続いている限り一つの段落にまとめる。
5. 説明・注釈・markdown（``` など）は一切付けない。本文だけを出力する。

本文が無いページ（扉、目次、奥付、白紙など）は、次の一行だけを出力：
# NO_TEXT
"""


_CLIENTS: dict = {}


def _client_for(key: str, genai):
    """一把 key 一個 client，跨頁重用（也確保它不會被 GC 掉）。"""
    if key not in _CLIENTS:
        _CLIENTS[key] = genai.Client(api_key=key)
    return _CLIENTS[key]


def ocr_page(jpg_bytes: bytes, model: str = "gemini-2.5-flash") -> str:
    """一頁影像 → 文字。連 2 次 429 就退（[[feedback_ocr_two_strike_quota]]）。"""
    import time
    sys.path.insert(0, str(SCRIPT_DIR))
    from ocr_with_gemini import _find_gemini_keys  # type: ignore
    from google import genai
    from google.genai import types

    keys = _find_gemini_keys()
    if not keys:
        raise RuntimeError("無 GEMINI_API_KEY")

    last_err = None
    quota_hits = 0
    for key in keys:
        try:
            # client 一定要綁在變數上：寫成 genai.Client(...).models.generate_content(...)
            # 那個 client 是暫時物件，請求還沒回來就可能被 GC 關掉，
            # 報 "Cannot send a request, as the client has been closed."
            client = _client_for(key, genai)
            resp = client.models.generate_content(
                model=model,
                contents=[types.Part.from_bytes(data=jpg_bytes, mime_type="image/jpeg"),
                          OCR_PROMPT],
                config=types.GenerateContentConfig(temperature=0.1),
            )
            text = (resp.text or "").strip()
            if text == "# NO_TEXT":
                return ""
            text = re.sub(r"^```[a-z]*\n", "", text)
            text = re.sub(r"\n```$", "", text)
            return clean_ocr_text(text.strip())
        except Exception as e:
            msg = str(e)
            last_err = e
            if "429" in msg or "RESOURCE_EXHAUSTED" in msg or "quota" in msg.lower():
                quota_hits += 1
                if quota_hits >= 2:
                    raise RuntimeError("連 2 次 429 quota，依規範退出") from e
                continue
            if "503" in msg or "UNAVAILABLE" in msg:
                time.sleep(3)
                continue
            raise
    raise RuntimeError("全 key 失敗: %s" % last_err)


def ocr_page_haiku(jpg_bytes: bytes, model: str = "claude-haiku-4-5-20251001") -> str:
    """一頁影像 → 文字（Haiku Vision）。

    依 [[feedback_ocr_strategy]]，Haiku **只在使用者明確下令時**啟用、嚴格一次一本。
    這條路是 Gemini 免費層額度用盡時的救急，不是預設。
    """
    import base64
    import time
    # 🚨 不要自己 Anthropic()：本機沒有 ANTHROPIC_API_KEY，走的是 Claude Code 的
    # OAuth 憑證（~/.claude/.credentials.json）。翻譯那邊已經有處理好的建構式
    # （含 401 時重讀憑證），直接重用，別再寫第二套。
    sys.path.insert(0, str(SCRIPT_DIR))
    from translate_ebook_to_zh import _make_anthropic_client  # type: ignore

    client = _make_anthropic_client()
    b64 = base64.standard_b64encode(jpg_bytes).decode("utf-8")

    quota_hits = 0
    for _ in range(3):
        try:
            resp = client.messages.create(
                model=model,
                max_tokens=4000,
                system=OCR_PROMPT,
                messages=[{"role": "user", "content": [
                    {"type": "image", "source": {"type": "base64",
                                                 "media_type": "image/jpeg", "data": b64}},
                    {"type": "text", "text": "このページの本文を文字起こししてください。"},
                ]}],
            )
        except Exception as e:
            msg = str(e).lower()
            if "429" in msg or "quota" in msg or "rate" in msg:
                quota_hits += 1
                if quota_hits >= 2:
                    raise RuntimeError("連 2 次 429 quota，依規範退出") from e
                time.sleep(5)
                continue
            if "overload" in msg or "529" in msg or "500" in msg:
                time.sleep(5)
                continue
            raise
        text = (resp.content[0].text if resp.content else "").strip()
        if text == "# NO_TEXT":
            return ""
        text = re.sub(r"^```[a-z]*\n", "", text)
        text = re.sub(r"\n```$", "", text)
        return clean_ocr_text(text.strip())
    raise RuntimeError("Haiku 連續失敗")


def ocr_book(pid: str, model: str = "gemini-2.5-flash",
             cache_dir: Path = CACHE_DIR, backend: str = "gemini") -> dict:
    """快取裡的影像逐頁 OCR，一頁一個 checkpoint 檔；已有的跳過。回傳 {影像號: 文字}。"""
    import io as _io
    from PIL import Image

    src_dir = cache_dir / pid
    # 🚨 checkpoint 依引擎分目錄：不分的話換引擎重跑會沿用上一個引擎的結果，
    #    Haiku 編造出來的那批會被 Gemini 那輪當成「已完成」直接跳過。
    out_dir = src_dir / ("ocr-" + backend)
    out_dir.mkdir(parents=True, exist_ok=True)

    def _one(img_bytes: bytes) -> str:
        if backend == "haiku":
            return ocr_page_haiku(img_bytes)
        return ocr_page(img_bytes, model=model)

    pages: dict = {}
    for jpg in sorted(src_dir.glob("*.jpg")):
        idx = int(jpg.stem)
        txt = out_dir / ("%07d.txt" % idx)
        if txt.exists():
            pages[idx] = txt.read_text(encoding="utf-8")
            continue
        raw = jpg.read_bytes()
        im = Image.open(_io.BytesIO(raw))
        if is_spread(*im.size):
            # 跨頁分兩半各自 OCR，右半頁先（日文直書右起）
            parts = []
            for box in split_spread_boxes(*im.size):
                buf = _io.BytesIO()
                im.crop(box).save(buf, format="JPEG", quality=92)
                parts.append(_one(buf.getvalue()))
            text = (chr(10) * 2).join(p for p in parts if p.strip())
        else:
            text = _one(raw)
        txt.write_text(text, encoding="utf-8")
        pages[idx] = text
        print("  OCR %07d  %d 字%s" % (idx, len(text), "（跨頁分兩半）" if is_spread(*im.size) else ""))
    return pages


def build_sections(pid: str, slug: str, cache_dir: Path = CACHE_DIR,
                   backend: str = "gemini") -> Path:
    """目次分章＋OCR 文字 → secN.json（與其他作者同形），回傳輸出目錄。"""
    import json
    book = fetch_book(pid)
    secs = sections_from_index(book["index"], book["pages"], book["title"])
    pages = {}
    for txt in sorted((cache_dir / pid / ("ocr-" + backend)).glob("*.txt")):
        pages[int(txt.stem)] = txt.read_text(encoding="utf-8")
    # 幻覺閘：目次頁的內容我們已經從 NDL API 知道了，拿它驗 OCR 有沒有在讀圖
    toc_imgs = [e["image"] for e in
                (parse_toc_entry(l) for l in book["index"]) if e and e["title"] in ("目次", "目 次")]
    if toc_imgs and pages.get(toc_imgs[0]):
        ratio = toc_match_ratio(pages[toc_imgs[0]], [s0["title"] for s0 in secs])
        print("  目次 canary：影像 %d 對上 %.0f%% 章名" % (toc_imgs[0], ratio * 100))
        if ratio < 0.5:
            raise RuntimeError(
                "目次頁只對上 %.0f%% 的已知章名 —— OCR 在編造內容，拒絕產出。"
                "  這一頁的答案我們本來就知道（NDL 目次 API），連它都對不上，"
                "其餘各頁一個字都不能信。" % (ratio * 100))
    if refuse_empty_build(secs, pages):
        raise RuntimeError(
            "每一章都沒有正文——OCR 沒跑或全失敗，拒絕寫出空的 secN.json。"
            "先跑 --ocr %s。" % pid)
    out_dir = (SCRIPT_DIR.parent / ".claude" / "skills" / "ebook-collected-works"
               / "ndl_data" / slug)
    out_dir.mkdir(parents=True, exist_ok=True)
    for i, sec in enumerate(secs):
        payload = section_payload(sec, pages)
        (out_dir / ("sec%d.json" % i)).write_text(
            json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        print("  sec%-2d %-28s %d 段" % (i, sec["title"][:26], len(payload["src"])))
    return out_dir


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", type=str, help="pid：印書誌與分章")
    ap.add_argument("--fetch", type=str, help="pid：下載全部影像到快取")
    ap.add_argument("--ocr", type=str, help="pid：快取影像逐頁 Gemini Vision OCR")
    ap.add_argument("--build", type=str, help="pid：OCR 文字 → secN.json（需 --slug）")
    ap.add_argument("--slug", type=str, help="--build 的輸出目錄名")
    ap.add_argument("--model", type=str, default="gemini-2.5-flash")
    ap.add_argument("--backend", choices=["gemini", "haiku"], default="gemini",
                    help="OCR 引擎。haiku 需使用者明確下令（feedback_ocr_strategy）")
    ap.add_argument("--width", type=int, default=0,
                    help="0＝全解析度。🚨 跨頁掃描降尺寸會讓 OCR 開始編造內容")
    args = ap.parse_args()
    pid = args.probe or args.fetch or args.ocr or args.build
    if not pid:
        ap.error("--probe／--fetch／--ocr／--build 擇一")
    if args.build and not args.slug:
        ap.error("--build 需要 --slug")
    if not is_open(pid):
        print(f"pid={pid} 不是インターネット公開（館內限定／個人送信），不可取用")
        return
    b = fetch_book(pid)
    secs = sections_from_index(b["index"], b["pages"], fallback_title=b["title"])
    print(f"《{b['title']}》{b['author']} {b['publisher']} {b['year']}  影像 {b['pages']} 頁")
    for s in secs:
        print(f"   {s['start']:>4}–{s['end'] - 1:<4} {s['title'][:44]}")
    if args.fetch:
        got = fetch_images(pid, 1, b["pages"] + 1, width=(args.width or None))
        print(f"下載完成 {len(got)} 張 → {CACHE_DIR / pid}")
    if args.ocr:
        pages = ocr_book(pid, model=args.model, backend=args.backend)
        chars = sum(len(v) for v in pages.values())
        empty = [k for k, v in pages.items() if not v.strip()]
        print(f"OCR 完成 {len(pages)} 頁／{chars} 字；無正文 {len(empty)} 頁 {empty}")
    if args.build:
        out = build_sections(pid, args.slug, backend=args.backend)
        print(f"→ {out}")


if __name__ == "__main__":
    main()
