"""把 Drive「_待審分類」裡的書重新分類、搬到正確類別夾，並同步 ebooks.category／file_path。

緣起（2026-10-02）：ingest 的 Gemini 分類寫死已下架的 gemini-2.5-flash，一整輪 511 本每本都退回
本地評分器，信心不足就全進了 _待審分類。模型修好後（gemini-flash-latest），用同一套
`ingest_new_books.classify()` 重跑這批。

    python scripts/reclassify_review_queue.py            # 只列出會怎麼分（dry run）
    python scripts/reclassify_review_queue.py --apply    # 搬檔＋改 DB

- 仍判不出來（classify 回 _待審分類）的留在原處，不硬分。
- 目標夾已有同名檔就跳過並列出（交人處理），不覆蓋。
- 🚨 搬了 Drive 檔一定要同步 ebooks.file_path（[[feedback_set_books_split]]），否則閱讀器找不到檔。
- 🚨 PostgREST 不帶 limit 會靜默截在 1000 筆，分頁撈。
- Gemini 免費層每 key 每天額度很小；額度用完 classify 會退回本地評分器，判不出就留著，隔天再跑即可。
"""
from __future__ import annotations

import argparse
import shutil
import sys
import urllib.parse
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
import ingest_new_books as ing  # noqa: E402

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


_gemini_dead = False


def _parse_cls(text: str) -> dict:
    """LLM 回的 JSON → {category, subcategory, confidence}；類別名稱的常見誤寫照 ingest 的對照表收斂。"""
    import json
    import re
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S)
    m = re.search(r"\{.*\}", text, flags=re.S)
    parsed = json.loads(m.group(0) if m else text)
    cat = (parsed.get("category") or "").strip()
    if cat not in ing.CATEGORIES:
        if cat in {"聖經研究", "教父學", "系統神學", "信理神學", "基督論", "三一論"}:
            cat = "神學"
        elif cat in {"基督教", "伊斯蘭教", "佛教", "印度教", "瑣羅亞斯德教", "猶太教", "巴哈伊"}:
            cat = "世界宗教"
        elif cat in {"教會史", "宗教史", "神話學", "宗教比較", "宗教社會學", "宗教對話"}:
            cat = "宗教學"
        else:
            raise ValueError(f"非類別名稱：{cat!r}")
    return {"category": cat, "subcategory": parsed.get("subcategory") or None,
            "confidence": float(parsed.get("confidence", 0.5))}


def classify(title: str, author: str, filename: str) -> dict:
    """同 ingest_new_books.classify，但 Gemini 額度用完就改走 NVIDIA（模型鏈 Gemini→NVIDIA），
    而且一旦 Gemini 七把 key 都 429 就整輪不再試——否則每本都要白等三分多鐘的重試。"""
    global _gemini_dead
    fb = ing.fallback_category(title, author, filename)
    if fb:
        return {"category": fb, "subcategory": None, "confidence": 0.9, "source": "fallback"}
    g = None
    if not _gemini_dead:
        try:
            g = ing.gemini_classify(title, author)
            g["source"] = "gemini"
        except Exception as e:  # noqa: BLE001
            if "exhausted" in str(e) or "429" in str(e):
                _gemini_dead = True
                print("  （Gemini 額度用完，本輪改用 NVIDIA）")
    if g is None:
        try:
            import translate_ebook_to_zh as te
            prompt = ing.CATEGORIZE_PROMPT.format(title=title, author=author or "(unknown)")
            g = _parse_cls(te.nvidia_chat(prompt + "\n只回 JSON。", max_tokens=400, temperature=0.1, thinking=False))
            g["source"] = "nvidia"
        except Exception as e:  # noqa: BLE001
            print(f"  ⚠ NVIDIA 也失敗：{str(e)[:80]}")
            return ing._local_or_review(title, author, filename)
    if g.get("confidence", 0) < ing.REVIEW_CONFIDENCE:
        return ing._local_or_review(title, author, filename, conf_floor=g.get("confidence", 0))
    return g


def fetch_review_rows() -> list[dict]:
    rows, off = [], 0
    cat = urllib.parse.quote(ing.REVIEW_CATEGORY)
    while True:
        r = requests.get(f"{ing.URL}/rest/v1/ebooks?select=id,title,author,file_path,category&category=eq.{cat}"
                         f"&order=id&offset={off}&limit=1000", headers=ing.SB_HEADERS, timeout=120)
        r.raise_for_status()
        chunk = r.json()
        rows += chunk
        if len(chunk) < 1000:
            return rows
        off += 1000


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--no-gemini", action="store_true", help="今天 Gemini 額度已用完時直接走 NVIDIA，省掉七把 key 各三分鐘的重試")
    a = ap.parse_args()
    global _gemini_dead
    _gemini_dead = a.no_gemini
    rows = fetch_review_rows()
    if a.limit:
        rows = rows[: a.limit]
    print(f"分母：_待審分類 {len(rows)} 本")
    moved = kept = clash = missing = 0
    for i, r in enumerate(rows, 1):
        src = Path(r["file_path"] or "")
        if not src.exists():
            print(f"[{i}] ⚠ 檔案不在 {src}")
            missing += 1
            continue
        cls = classify(r["title"] or src.stem, r.get("author") or "", src.name)
        cat = cls["category"]
        if cat == ing.REVIEW_CATEGORY:
            print(f"[{i}] ＝ 仍判不出（{cls['source']}）{src.name[:70]}")
            kept += 1
            continue
        dst = ing.DRIVE_ROOT / cat / src.name
        print(f"[{i}] → {cat}{' / ' + cls['subcategory'] if cls.get('subcategory') else ''}"
              f"  ({cls['source']}, {cls['confidence']:.2f})  {src.name[:70]}")
        if not a.apply:
            continue
        if dst.exists():
            print("     ✗ 目標夾已有同名檔，跳過")
            clash += 1
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        p = requests.patch(f"{ing.URL}/rest/v1/ebooks?id=eq.{r['id']}",
                           headers={**ing.SB_HEADERS, "Prefer": "return=minimal"},
                           json={"category": cat, "subcategory": cls.get("subcategory"),
                                 "file_path": str(dst).replace("/", "\\")}, timeout=30)
        if p.status_code not in (200, 204):
            # DB 沒改成功就把檔搬回去，兩邊保持一致
            shutil.move(str(dst), str(src))
            print(f"     ✗ DB 更新失敗 HTTP {p.status_code}，檔案已搬回：{p.text[:120]}")
            continue
        moved += 1
    print(f"\n分母 {len(rows)}｜已分類搬移 {moved}｜仍待審 {kept}｜同名衝突 {clash}｜找不到檔 {missing}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
