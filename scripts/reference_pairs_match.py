#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""把 output/untranslated_inventory/untranslated_v2.tsv 裡「狀態」＝
「已有中譯(館藏)」／「確認有中譯」的 134 本外文書，配對回館內「已有中譯本」
的 ebook_id，供 align_reference.py 逐段對齊使用。

三類：
  1. Schaff ANF/NPNF（`修正依據` 欄含 "/fathers"）—— 站上 /fathers 已有三欄
     對照，不必再對齊，標記 source="fathers_dup"，不解出 zh_id。
  2. 已有中譯(館藏)（`疑似比對到的館藏書名` 欄已經是先前模糊比對出的候選
     書名，相似度在 `比對相似度` 欄）—— 用候選書名回頭在 ebooks 表裡找
     對應的 id（同名或近似同名、且不是原文那筆自己）。
  3. 確認有中譯（非 fathers）—— `修正依據` 欄是自由文字附中譯書名（常見
     形式「同書（… =《書名》）」或「/works：…（uuid）」），用正則抽出書名
     候選字串，再回頭比對。

比對不到 / 相似度不夠高的一律標「待確認」，不臆測。

用法：
    python scripts/reference_pairs_match.py
輸出：output/reference_pairs/pairs_134.tsv
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_TSV = ROOT / "output/untranslated_inventory/untranslated_v2.tsv"
OUT_DIR = ROOT / "output/reference_pairs"
OUT_TSV = OUT_DIR / "pairs_134.tsv"

STATUS_LIBRARY = "已有中譯(館藏)"
STATUS_CONFIRMED = "確認有中譯"


# ---------------------------------------------------------------------------
# 純函式：書名正規化與相似度（可單獨測試，不必連 DB／讀 TSV）
# ---------------------------------------------------------------------------

_STRIP_CHARS_RE = re.compile(
    r"[\s　·・:：\-—－,，。.　]|"
    r"《|》|\(|\)|（|）|\[|\]|「|」|『|』")
_ROMAN_VOL_RE = re.compile(
    r"^vol\.?\s*[ivxlcdm0-9]+\s*", re.IGNORECASE)


def normalize_title(s: str) -> str:
    """書名正規化：去標點空白、轉小寫，供粗略比對用。"""
    if not s:
        return ""
    s = _ROMAN_VOL_RE.sub("", s.strip())
    s = _STRIP_CHARS_RE.sub("", s)
    return s.lower()


def title_similarity(a: str, b: str) -> float:
    """0~1 的字串相似度（SequenceMatcher，對書名這種短字串夠用）。

    候選書名整串（正規化後、至少 2 字）完整包含在目標字串裡時直接給高分：
    候選常常是從《書名》括注抽出來的短題，目標的 title 欄卻是「《書名》
    ＋作者＋英文檔名」一長串，逐字比對的 SequenceMatcher ratio 會被拉低
    到門檻以下（「愚人頌」對「愚人頌 [荷]伊拉斯謨」只有 0.545），但完整
    包含其實是比逐字比對更強的訊號，不該被短字串的分母拖累。"""
    na, nb = normalize_title(a), normalize_title(b)
    if not na or not nb:
        return 0.0
    ratio = SequenceMatcher(None, na, nb).ratio()
    if len(na) >= 2 and (na in nb or nb in na):
        ratio = max(ratio, 0.9)
    return ratio


_BRACKET_TITLE_RE = re.compile(r"《([^》]{2,60})》")
_EQUAL_TITLE_RE = re.compile(r"[＝=]\s*《?([^《》\s]{2,40})》?")


def extract_zh_title_candidates(note: str) -> list[str]:
    """從「修正依據」自由文字裡抽出可能的中譯書名候選（《…》優先）。"""
    if not note:
        return []
    out = list(dict.fromkeys(_BRACKET_TITLE_RE.findall(note)))
    if not out:
        out = list(dict.fromkeys(_EQUAL_TITLE_RE.findall(note)))
    return out


def is_fathers_dup(note: str) -> bool:
    return "/fathers" in (note or "") or "fathers" in (note or "").lower()


_HAN_RE = re.compile(r"[一-鿿]")


def has_han(s: str) -> bool:
    return bool(_HAN_RE.search(s or ""))


def best_match(candidate_titles: list[str], ebooks: list[dict], *,
                exclude_id: str, min_score: float = 0.55) -> tuple[dict | None, float, str]:
    """在 ebooks 清單裡找 candidate_titles 最像的一筆。

    這批書的英文原書常常同一本被重複上傳好幾筆（各自檔名不同），而且這些
    重複的英文原書筆記錄，`author` 欄常常被填成跟真正中譯本一模一樣的
    「中文短題 英文題名」字串（上傳當下複製過來的慣例，不是巧合）——直接
    拿這個字串去配 `author` 欄，很容易配到另一本英文重複記錄自己身上
    （2026-09-28 拿《討好人的罪》試跑時真的犯過：配到另一筆英文重複記錄，
    不是中譯本）。兩道防呆：

    1. **先只比對 `title` 欄，比不到夠分才退而比對 `author`／`original_title`**
       ——這批中譯本的慣例是把「《中文題》…英文檔名」整串放在 `title` 欄，
       `author` 欄才是那個容易重複的短題，所以 `title` 欄比對更可靠。
    2. **候選本身必須含漢字**——我們找的是中譯本，中譯本的書名一定有漢字；
       純英文（無漢字）的候選一律不算數，直接篩掉（會濾掉配到英文重複記錄
       或配到另一本英文原書的情況）。

    回傳 (row_or_None, score, matched_field)。"""
    def _search(fields: tuple[str, ...]) -> tuple[dict | None, float, str, int]:
        """回傳 (row, score, field, n_tied)：`n_tied` 是並列最高分的筆數
        （>1 代表分數是靠巧合的通用字串湊出來的，不是真的指到特定一本書）。"""
        best_row, best_score, best_field = None, 0.0, ""
        n_tied = 0
        for row in ebooks:
            if row["id"] == exclude_id:
                continue
            for field in fields:
                val = row.get(field) or ""
                if not val or not has_han(val):
                    continue
                for cand in candidate_titles:
                    score = title_similarity(cand, val)
                    if score > best_score:
                        best_row, best_score, best_field, n_tied = row, score, field, 1
                    elif score == best_score and best_row is not None and row["id"] != best_row["id"]:
                        n_tied += 1
        return best_row, best_score, best_field, n_tied

    row, score, field, tied = _search(("title",))
    if row is not None and score >= min_score and (tied <= 1 or score >= 0.9):
        return row, score, field
    # `author`／`original_title` 欄常常是同一作者旗下好幾本書共用的通用短題
    # （「馬丁路德 Martin Luther」這種），一旦有並列最高分（同一候選字串同時
    # 命中好幾本不同書），代表這個分數只是巧合湊出來的、指不到特定哪一本，
    # 寧可回「配不到」也不要賭一把（2026-09-28 拿《意志的捆綁》試跑真的
    # 賭錯過一次：配到同作者另一本不相干的書）。
    row2, score2, field2, tied2 = _search(("author", "original_title"))
    if row2 is not None and score2 >= min_score and score2 > score and tied2 <= 1:
        return row2, score2, field2
    if row is not None and score >= min_score and tied <= 1:
        return row, score, field
    return None, max(score, score2), field if score >= score2 else field2


# ---------------------------------------------------------------------------
# I/O 層
# ---------------------------------------------------------------------------

def load_ebooks_cache(path: Path) -> list[dict]:
    """讀本機快取的 ebooks 全表（id/title/author/original_title/...）。
    快取由本檔 `--refresh-cache` 或呼叫端另外從 Supabase 拉好存成 json。"""
    return json.loads(path.read_text(encoding="utf-8"))


def refresh_ebooks_cache(path: Path) -> list[dict]:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    import requests
    url = os.environ["SUPABASE_URL"].rstrip("/")
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    rows: list[dict] = []
    offset = 0
    while True:
        r = requests.get(f"{url}/rest/v1/ebooks", params={
            "select": "id,title,author,original_title,original_author,"
                      "category,subcategory,collection,total_chars",
            "order": "id", "offset": str(offset), "limit": "1000"},
            headers=headers, timeout=30)
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        rows.extend(batch)
        offset += 1000
        if len(batch) < 1000:
            break
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    return rows


def build_pairs(src_tsv: Path, ebooks: list[dict]) -> list[dict]:
    out: list[dict] = []
    with src_tsv.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            status = row.get("狀態", "")
            if status not in (STATUS_LIBRARY, STATUS_CONFIRMED):
                continue
            orig_id = row["id"]
            title = row.get("書名", "")
            author = row.get("作者", "")
            note = row.get("修正依據", "")

            rec = {
                "orig_id": orig_id, "orig_title": title, "orig_author": author,
                "zh_id": "", "zh_title": "", "match_score": "",
                "match_field": "", "source": "", "note": note,
            }

            if is_fathers_dup(note):
                rec["source"] = "fathers_dup"
                rec["note"] = "站上 /fathers 已有三欄對照，不必再對齊"
                out.append(rec)
                continue

            if status == STATUS_LIBRARY:
                candidate = row.get("疑似比對到的館藏書名", "")
                candidates = [candidate] if candidate else []
                rec["source"] = "library_fuzzy"
            else:
                candidates = extract_zh_title_candidates(note)
                # 這批書常把「中文短題＋英文原題」擠在「作者」欄（資料本身
                # title/author 常錯位——見 Ark of the Covenant 那筆），而館內
                # 對應的中譯本 ebook 的 title 欄常常原樣包含同一串英文檔名，
                # 所以額外拿 `作者` 欄當候選，往往比 `修正依據` 的自由文字
                # 更準（2026-09-28 靠這個多配到 12 組：討好人的罪／愚人頌／
                # 衛斯理約翰日記／使徒信經簡釋／真正皈依的本質…）。
                if author and author not in candidates:
                    candidates = candidates + [author]
                rec["source"] = "confirmed_note"

            if not candidates:
                rec["source"] += "_no_candidate"
                out.append(rec)
                continue

            match, score, field = best_match(candidates, ebooks, exclude_id=orig_id)
            rec["match_score"] = f"{score:.3f}"
            if match:
                rec["zh_id"] = match["id"]
                rec["zh_title"] = (match.get("title") or "")[:80]
                rec["match_field"] = field
            else:
                rec["source"] += "_unmatched"
                rec["zh_title"] = (candidates[0] or "")[:80]
            out.append(rec)
    return out


def write_pairs_tsv(pairs: list[dict], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["orig_id", "orig_title", "orig_author", "zh_id", "zh_title",
              "match_score", "match_field", "source", "note"]
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        w.writeheader()
        for r in pairs:
            w.writerow(r)


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cache", default=str(ROOT / "output/reference_pairs/ebooks_cache.json"))
    ap.add_argument("--refresh-cache", action="store_true")
    ap.add_argument("--src", default=str(SRC_TSV))
    ap.add_argument("--out", default=str(OUT_TSV))
    args = ap.parse_args()

    cache_path = Path(args.cache)
    if args.refresh_cache or not cache_path.exists():
        print(f"從 Supabase 拉 ebooks 全表 -> {cache_path}")
        ebooks = refresh_ebooks_cache(cache_path)
    else:
        ebooks = load_ebooks_cache(cache_path)
    print(f"ebooks 全表 {len(ebooks)} 筆")

    pairs = build_pairs(Path(args.src), ebooks)
    write_pairs_tsv(pairs, Path(args.out))

    from collections import Counter
    cnt = Counter(p["source"] for p in pairs)
    print(f"共 {len(pairs)} 組，寫入 {args.out}")
    for k, v in cnt.most_common():
        print(f"  {k}: {v}")
    matched = sum(1 for p in pairs if p["zh_id"])
    print(f"配到 zh_id：{matched}/{len(pairs)}（不含 fathers_dup）")


if __name__ == "__main__":
    main()
