"""多瑪斯‧阿奎那《神學大全》（中華道明會譯本）→ /collected-works 經院問答（quaestio）全集。

REFERENCE / 單一語言案例，但**文體特殊（quaestio 經院問答）**：圖書館已有 19 冊 OCR 中譯
掃描本（collection=null）；本 skill 把每「節（Articulus）」重切為一個 chunk，注入
〔異議〕〔反之〕〔正解〕〔答覆〕四段角色標記 → collected-works reader `[work].vue` 的
genre='quaestio' 版面自動四段配色（異議 rose／反之 amber／正解 emerald／答覆 blue）。

來源＝圖書館既有 ebook 的 Drive 原始 OCR JSONL（**唯讀，不覆蓋**，保留給後續 NVIDIA
逐字清理）。輸出寫到新的 collected-works ebook id（a9051225 命名空間；a9≈aquinas、1225＝生年）。
中華道明會譯本每節固定格式：
    有關第N節，我們討論如下：→〔異議〕質疑＋編號難題 →〔反之〕…卻說 →〔正解〕正解我解答如下 →〔答覆〕釋疑編號

⚠️ OCR 雜訊（督貴/啞益/範圓/跑版頁眉字散落）本腳本只做**輕量規則清理**（頁碼行、空白、
明顯頁眉 bleed）；**逐字級 OCR 錯字**留給 `--clean nvidia` 批次（走 NVIDIA 文字模型，
不吃 ACCS 的 Gemini Vision 量能）。

純函式（chinese_to_int / clean_ocr_light / split_articles / mark_zones）零 network/DB，
由 scripts/tests/test_aquinas_build.py 鎖定。

  python scripts/aquinas_build.py --inspect --vol 1        # 印第一冊 題/節/四段統計 + 樣本
  python scripts/aquinas_build.py --vol 1 --upload         # 第一冊 → quaestio chunks → R2 + DB
  python scripts/aquinas_build.py --all --upload           # 17 冊
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

PARENT_VOLUME = "神學大全（多瑪斯‧阿奎那‧中華道明會譯本）"
NEW_EBID = "a9051225-0000-4000-8000-{:012d}"  # a9≈aquinas 1225=生年；末 12 位＝冊號

# 17 冊 registry：冊號 → (來源圖書館 ebook_id, 冊名, 集‧題範圍副標)。
# 集/題範圍取自各冊首 chunk chapter_path（缺者依《神學大全》標準結構補）。
REGISTRY = {
    1:  ("eb6f9426-5636-44b7-bd0a-11c5838f9357", "論天主一體三位", "第一集‧第1–43題"),
    2:  ("f40d95eb-a82b-4731-8d50-3b663697d97a", "論天主創造萬物", "第一集‧第44–74題"),
    3:  ("b1d1c090-47b1-4e27-a0c5-9a421d7065ac", "論人", "第一集‧第75–119題"),
    4:  ("d2c4f95a-9f66-4c69-9fed-ae524e02e2b3", "論人的道德行為與情", "第二集第一部‧第1–48題"),
    5:  ("9948f776-cecd-4fd2-a58a-b7da87d05229", "論德性與惡習及罪", "第二集第一部‧第49–89題"),
    6:  ("c82f299f-0a56-41c1-b17f-db152a9f2892", "論法律與恩寵", "第二集第一部‧第90–114題"),
    7:  ("58e9f9ea-5885-4e67-8daa-9e574ddeb324", "論信德與望德", "第二集第二部‧第1–22題"),
    8:  ("7e8209d6-6c0c-4e1d-a25a-2f83ab9a007a", "論愛德", "第二集第二部‧第23–46題"),
    9:  ("da118696-1588-46b7-8331-eb1e29b06af8", "論智德與義德", "第二集第二部‧第47–79題"),
    10: ("d76c3b3c-5d00-4f55-8071-140861156e48", "論義德之諸部分", "第二集第二部‧第80–100題"),
    11: ("365f47f5-2de0-4c9b-ad59-bc0b252f447d", "論勇德與節德", "第二集第二部‧第101–140題"),
    12: ("0d41cf82-c1c3-4b8d-9e59-12b326070536", "論特殊恩寵、生活和身分", "第二集第二部‧第141–189題"),
    13: ("42fc24cf-41a3-46e4-b7d2-b2a061672cdf", "論天主聖言之降生成人", "第三集‧第1–26題"),
    14: ("0251c9bb-ec2b-4dd8-a34d-7ff367473444", "論基督的生平與救贖", "第三集‧第27–59題"),
    15: ("2351b657-a2c8-4072-a26c-620d471a320d", "論聖事總論與聖洗堅振", "第三集‧第60–90題"),
    16: ("8b3ac46c-26b8-43f4-87a5-848a8c2e1abc", "論聖體聖事與懺悔", "補編‧第1–68題"),
    17: ("966bd071-5119-4d9e-8c50-8682825cb29e", "論肉身復活的問題", "補編‧第69–99題／附設1–2題"),
}

_CN = {c: i for i, c in enumerate("零一二三四五六七八九", 0)}
OPENER = re.compile(r"有關第([一二三四五六七八九十百]+)節[，,]?\s*我們討論如下[：:]")
_QNUM = re.compile(r"第([一二三四五六七八九十百]+)題[：:]?\s*(論[^>\n，。]{2,25})")


def chinese_to_int(s: str) -> int:
    """中文數字（含十/百，≤999）→ int。'四十三'→43、'十'→10、'一一四'→114（逐字亦可）。"""
    s = s.strip()
    if not s:
        return 0
    if "十" not in s and "百" not in s:  # 逐字式：一一四 → 114
        if all(c in _CN for c in s):
            return int("".join(str(_CN[c]) for c in s)) if len(s) > 1 else _CN[s]
    total, section, num = 0, 0, 0
    for c in s:
        if c == "百":
            section += (num or 1) * 100
            num = 0
        elif c == "十":
            section += (num or 1) * 10
            num = 0
        elif c in _CN:
            num = _CN[c]
    return total + section + num


# ── 純函式：清理 / 切段 / 標記 ─────────────────────────────────────────

def clean_ocr_light(text: str) -> str:
    """輕量規則清理：純頁碼行、行首散落單數字、多餘空白。**不動逐字錯字**。"""
    out = []
    for ln in text.split("\n"):
        s = ln.strip()
        if not s:
            continue
        if re.fullmatch(r"[-–—\s]*\d{1,4}[-–—\s]*", s):  # 純頁碼行
            continue
        out.append(s)
    joined = "\n".join(out)
    joined = re.sub(r"[ \t　]+", "", joined)  # CJK 間去空白
    return joined


def split_articles(full: str):
    """全書文字 → [{'sec': 節號int, 'body': 該節內文}]，以「有關第N節，我們討論如下」為界。"""
    ops = list(OPENER.finditer(full))
    arts = []
    for i, m in enumerate(ops):
        body = full[m.end(): ops[i + 1].start() if i + 1 < len(ops) else len(full)]
        arts.append({"sec": chinese_to_int(m.group(1)), "body": body})
    return arts


def mark_zones(body: str):
    """一節內文 → [(label|None, para)] 段落序列，四段各注入 〔異議/反之/正解/答覆〕。

    〔異議〕逐條難題各一段、〔反之〕整段、〔正解〕首段帶標其餘續接、〔答覆〕逐條各一段。
    偵測不到正解＝非標準節（回傳單段無標，維持可讀）。"""
    r = re.search(r"正解\s*我解答如下[：:]?", body)
    if not r:
        return [(None, p.strip()) for p in re.split(r"\n{2,}", body.strip()) if p.strip()]
    resp = r.start()
    sc = body.rfind("反之", 0, resp)
    rp = body.find("釋疑", resp)
    obj_raw = body[: sc if sc > 0 else resp]
    sed_raw = body[sc:resp] if sc > 0 else ""
    sol_raw = body[resp: rp if rp > 0 else len(body)]
    rep_raw = body[rp:] if rp > 0 else ""

    rows = []
    # 異議：去開頭「質疑」，依編號 1. 2. 3. 拆條
    obj = re.sub(r"^\s*質疑", "", obj_raw.strip())
    for para in _split_numbered(obj):
        rows.append(("異議", para))
    # 反之：去 bleed 前綴至「反之」
    if sed_raw:
        sed = re.sub(r"^.*?反之", "", sed_raw, count=1, flags=re.S).strip()
        if sed:
            rows.append(("反之", sed))
    # 正解：去「正解我解答如下」；首段帶標、其餘續接
    sol = re.sub(r"^正解\s*我解答如下[：:]?", "", sol_raw).strip()
    sol_paras = [p.strip() for p in re.split(r"\n{2,}", sol) if p.strip()]
    for j, p in enumerate(sol_paras):
        rows.append(("正解" if j == 0 else None, p))
    # 答覆：去 bleed 至「釋疑」，依編號拆條
    if rep_raw:
        rep = re.sub(r"^.*?釋疑", "", rep_raw, count=1, flags=re.S).strip()
        for para in _split_numbered(rep):
            rows.append(("答覆", para))
    return rows


def _split_numbered(text: str):
    """依行首/句首編號『1. 2. 3.』拆條；無編號則整段一條。回傳非空段 list。"""
    text = text.strip()
    if not text:
        return []
    parts = re.split(r"(?:^|\n)\s*([0-9１-９]{1,2})[.．、]?[ \t　]*\n?", "\n" + text)
    # parts: ['', '1', body1, '2', body2, ...] 或無編號時 ['\n<text>']
    if len(parts) <= 1:
        return [re.sub(r"\s*\n\s*", "", text)]
    out = []
    it = iter(parts[1:])
    for num, body in zip(it, it):
        body = re.sub(r"\s*\n\s*", "", body).strip()
        if body:
            out.append(f"{num}. {body}")
    return out or [re.sub(r"\s*\n\s*", "", text)]


def build_qtitles(rows: list[dict]) -> dict[int, str]:
    """從 chunk chapter_path + 正文題目標題，建 題號→題名 對照。"""
    titles: dict[int, str] = {}
    for r in rows:
        cp = r.get("chapter_path", "") or ""
        for m in re.finditer(r"第([一二三四五六七八九十百]+)題[：:]([^>\n]{2,25})", cp):
            titles.setdefault(chinese_to_int(m.group(1)), m.group(2).strip())
    return titles


# ── 組冊（I/O）───────────────────────────────────────────────────────

def _load_source(src_ebid: str) -> list[dict]:
    import translate_ebook_to_zh as te
    p = te.CHUNKS_DIR / f"{src_ebid}.jsonl"
    if not p.exists():
        raise SystemExit(f"找不到來源 OCR JSONL：{p}")
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def build_volume(vol: int):
    """一冊 → quaestio chunks（cover + 每節一 chunk）。"""
    src_ebid, vol_title, vol_sub = REGISTRY[vol]
    rows = _load_source(src_ebid)
    qtitles = build_qtitles(rows)
    full = clean_ocr_light("\n".join(r.get("content", "") for r in rows))
    # 從第一個 article opener 起（之前皆前付/目次）
    first = OPENER.search(full)
    body_text = full[first.start():] if first else full
    arts = split_articles(body_text)

    book = f"神學大全‧第{vol}冊 {vol_title}"
    cover = {
        "chunk_index": 0, "chunk_type": "cover", "page_number": 0,
        "chapter_path": book, "volume": book, "parent_volume": PARENT_VOLUME,
        "format": "markdown",
        "content": f"# {book}\n\n{PARENT_VOLUME}\n\n{vol_sub}",
    }
    chunks = [cover]
    qnum, prev_sec = 0, 0
    for a in arts:
        sec = a["sec"]
        if sec <= 1 or sec < prev_sec:  # 節號重置 → 新題
            qnum += 1
        prev_sec = sec
        qtitle = qtitles.get(qnum, f"第{qnum}題")
        zone_rows = mark_zones(a["body"])
        if not zone_rows:
            continue
        heading = f"## 第{qnum}題 {qtitle} · 第{sec}節"
        paras = [heading] + [(f"〔{lab}〕{p}" if lab else p) for lab, p in zone_rows]
        idx = len(chunks)
        chunks.append({
            "chunk_index": idx, "chunk_type": "chapter", "page_number": idx,
            "chapter_path": f"{book} · 第{qnum}題 {qtitle} · 第{sec}節",
            "volume": book, "parent_volume": PARENT_VOLUME, "format": "markdown",
            "content": "\n\n".join(paras),
            "anchors": [f"I q{qnum} a{sec}"] + [""] * (len(paras) - 1),
        })
    return chunks


def _upload(vol: int, chunks: list[dict]):
    import datetime
    import requests
    import translate_ebook_to_zh as te

    ebid = NEW_EBID.format(vol)
    _, vol_title, vol_sub = REGISTRY[vol]
    out = te.CHUNKS_DIR / f"{ebid}.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    try:
        te.se.push_to_r2(ebid, out)
        print("    ✓ R2", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"    ⚠ R2 失敗: {e}", flush=True)
    total = sum(len(c["content"]) for c in chunks)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    row = {
        "id": ebid, "title": f"神學大全 第{vol}冊 {vol_title}", "author": "多瑪斯‧阿奎那",
        "author_en": "Thomas Aquinas", "original_title": "Summa Theologiae",
        "file_type": "epub", "translator": "中華道明會",
        "file_path": f"全集/神學/阿奎那/{PARENT_VOLUME}/第{vol}冊",
        "category": "神學", "subcategory": "經院哲學", "display_mode": "standard",
        "collection": "collected-works", "publication_year": 1274,
        "chunk_count": len(chunks), "total_pages": len(chunks), "total_chars": total,
        "parsed_at": now, "standardized_at": now,
    }
    H = {**te.H_JSON, "Prefer": "resolution=merge-duplicates"}
    requests.post(f"{te.URL}/rest/v1/ebooks?on_conflict=id", headers=H, json=row, timeout=30)
    requests.delete(f"{te.URL}/rest/v1/ebook_chunks?ebook_id=eq.{ebid}", headers=te.H_GET, timeout=30)
    prows = [{
        "ebook_id": ebid, "chunk_index": c["chunk_index"], "chunk_type": c["chunk_type"],
        "page_number": c["page_number"], "chapter_path": c["chapter_path"],
        "content": c["content"][:200], "char_count": len(c["content"]),
    } for c in chunks]
    for i in range(0, len(prows), 25):
        requests.post(f"{te.URL}/rest/v1/ebook_chunks", headers=te.H_JSON, json=prows[i:i + 25], timeout=60)
    print(f"    ✓ DB ebooks+previews  chunk_count={len(chunks)}  {ebid}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vol", type=int)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--inspect", action="store_true")
    ap.add_argument("--upload", action="store_true")
    a = ap.parse_args()

    vols = list(REGISTRY) if a.all else [a.vol] if a.vol else []
    if not vols:
        ap.error("需 --inspect --vol N / --vol N / --all")
    for v in vols:
        chunks = build_volume(v)
        arts = len(chunks) - 1
        chars = sum(len(c["content"]) for c in chunks)
        print(f"[冊{v}] {REGISTRY[v][1]}: {arts} 節 chunk | {chars:,} 字 | {NEW_EBID.format(v)}", flush=True)
        if a.inspect:
            for c in chunks[1:3]:
                print("   ", c["chapter_path"])
                print("   ", c["content"][:220].replace("\n", " ⏎ "))
        if a.upload:
            _upload(v, chunks)


if __name__ == "__main__":
    main()
