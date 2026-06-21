#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""回填創生哲學叢書「每節級」對話編號引用（intro_schedule §6）。

為每個內容 <h3> 小節末加一行
  <p class="section-source">本節主要依據對話：C-00123、G-00045…</p>

來源鏈：
  1. notes_*.json 的 glossary 詞條帶 8 碼 id 前綴（term -> ids）。
  2. seq_label_map.json：8 碼前綴 -> seq_label（C-#####/G-#####），由
     ai_dialogues_{chatgpt,gemini} 全表抓 id+seq_label 建成（前綴全域唯一、0 碰撞）。
  3. 每個 <h3> 小節文字 → 命中哪些 glossary 詞 → 取其 id → 映 seq_label。

「本節主要依據」＝該節文字中出現頻次最高的幾個體系術語所對應的對話，
故不同主題的小節得到不同引用。章末摘要／論證分析圖（chapter-recap 內的 h3）不標。

純函式（無 IO）可被 pytest 匯入；冪等（重跑先清舊 section-source 再插）。

用法：
  python scripts/genesis_cite_backfill.py build-map        # 重建 seq_label_map.json
  python scripts/genesis_cite_backfill.py dry ethics A 4   # 乾跑單章印對照
  python scripts/genesis_cite_backfill.py tag ethics A 9 B 13 C 9   # 寫入 draft
"""
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ── 純函式區（可被 pytest 匯入，無 IO）──────────────────────────────

_CJK = re.compile(r"[一-鿿]{3,}")


def term_match_keys(term):
    """從 glossary 詞條抽出比對鍵：所有長度≥3 的中文連續片段。

    例「倫理能見度（EVI）」→ ['倫理能見度']；「愛的萬物論（The Theory…）」→ ['愛的萬物論']。
    ≥3 的門檻是關鍵：把「行善≠誠實」這類複合詞拆出的通用 2 字詞（誠實/倫理/主體）排除，
    它們是滿篇皆有的常用字、會污染每節排名；體系核心詞（主體性倫理學/誠實度/愛的公式…）皆 ≥3。
    純拉丁鍵（hi/EVI…）易誤命中英文，亦不採用。
    """
    return [k for k in _CJK.findall(term) if len(k) >= 3]


def split_content_recap(html):
    """回傳 (content_region, recap_region)；recap = chapter-recap 起以後（不標引用）。"""
    m = re.search(r'<section\s+class="chapter-recap"', html)
    if m:
        return html[: m.start()], html[m.start():]
    return html, ""


_SRC_LINE = re.compile(r'\n\n<p class="section-source[^"]*">.*?</p>', re.S)


def strip_existing(html):
    """移除既有的 section-source 行（冪等重跑用）。"""
    return _SRC_LINE.sub("", html)


def plain_text(seg):
    """去標籤取純文字（供詞頻比對）。"""
    return re.sub(r"<[^>]+>", "", seg)


def section_seq_labels(body_text, term_keys, term_ids, prefix_map,
                       max_terms=4, cap=12):
    """依小節文字回傳排序後的 seq_label 清單。

    term_keys: {term: [中文比對鍵…]}；term_ids: {term: [8碼id…]}。
    取本節出現頻次最高的前 max_terms 個術語，聯集其 id → seq_label，去重排序，截斷 cap。
    """
    scored = []
    for term, keys in term_keys.items():
        cnt = sum(body_text.count(k) for k in keys)
        if cnt:
            # 分數：頻次優先；同頻偏好較長（較具體）的術語
            scored.append((cnt, max(len(k) for k in keys), term))
    if not scored:
        return []
    scored.sort(key=lambda x: (-x[0], -x[1]))
    labels = []
    seen = set()
    for _, _, term in scored[:max_terms]:
        for i in term_ids.get(term, []):
            lab = prefix_map.get(i)
            if lab and lab not in seen:
                seen.add(lab)
                labels.append(lab)
    labels.sort(key=lambda s: (s[0], int(s.split("-")[1])))
    return labels[:cap]


def tag_html(html, term_keys, term_ids, prefix_map, **kw):
    """為每個內容 <h3> 小節插入 section-source，章末再加一行 chapter-source 彙整全章；
    冪等。回傳 (new_html, n_tagged)。

    純史述／無體系術語的小節（如 B6/B7 社會史）得不到每節引用是忠實的，
    但章末彙整（依全章主導術語）保證該章的對話依據仍被標出（intro_schedule §6「章末可再彙整」）。
    """
    html = strip_existing(html)
    content, recap = split_content_recap(html)

    # 找出內容區所有 <h3 …> 起點，切成小節
    h3s = [m.start() for m in re.finditer(r"<h3[ >]", content)]
    if not h3s:
        return html, 0
    bounds = h3s + [len(content)]
    out = []
    n = 0
    prev_end = 0
    for idx in range(len(h3s)):
        s, e = h3s[idx], bounds[idx + 1]
        body = plain_text(content[s:e])
        labels = section_seq_labels(body, term_keys, term_ids, prefix_map, **kw)
        out.append(content[prev_end:e])
        if labels:
            out.append(
                f'\n\n<p class="section-source">本節主要依據對話：{"、".join(labels)}</p>'
            )
            n += 1
        prev_end = e
    out.append(content[prev_end:])

    # 章末彙整：全章主導術語，較寬（more terms / higher cap）
    chap = section_seq_labels(plain_text(content), term_keys, term_ids,
                              prefix_map, max_terms=8, cap=18)
    chap_line = ""
    if chap:
        chap_line = (
            f'\n\n<p class="section-source chapter-source">本章主要依據對話：'
            f'{"、".join(chap)}</p>'
        )
    return "".join(out) + chap_line + recap, n


# ── IO 區 ─────────────────────────────────────────────────────────

def _tmp(series):
    return Path("c:/tmp") / f"genesis_{series}"


def build_map():
    import requests
    from dotenv import load_dotenv
    load_dotenv()
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    h = {"apikey": key, "Authorization": f"Bearer {key}"}
    pref = {}
    coll = 0
    for tbl in ["ai_dialogues_chatgpt", "ai_dialogues_gemini"]:
        off = 0
        while True:
            r = requests.get(
                f"{url}/rest/v1/{tbl}",
                headers={**h, "Range-Unit": "items", "Range": f"{off}-{off+999}"},
                params={"select": "id,seq_label"},
            )
            rows = r.json()
            if not rows:
                break
            for row in rows:
                s = row.get("seq_label")
                if not s:
                    continue
                p = row["id"].replace("-", "")[:8]
                if p in pref and pref[p] != s:
                    coll += 1
                pref[p] = s
            off += len(rows)
            if len(rows) < 1000:
                break
    out = _tmp("ethics") / "seq_label_map.json"
    json.dump(pref, open(out, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"  {len(pref)} 前綴 → seq_label（碰撞 {coll}），寫出 {out}")


def load_terms(series):
    tmp = _tmp(series)
    term_ids = defaultdict(set)
    for f in sorted(tmp.glob("notes_*.json")):
        d = json.load(open(f, encoding="utf-8"))
        for g in d.get("glossary", []):
            for i in g.get("ids", []):
                term_ids[g["term"]].add(i)
    term_ids = {k: sorted(v) for k, v in term_ids.items()}
    term_keys = {k: term_match_keys(k) for k in term_ids}
    term_keys = {k: v for k, v in term_keys.items() if v}  # 丟無中文骨幹的
    term_ids = {k: term_ids[k] for k in term_keys}
    prefix_map = json.load(open(_tmp("ethics") / "seq_label_map.json", encoding="utf-8"))
    return term_keys, term_ids, prefix_map


def cmd_dry(series, book, ch):
    term_keys, term_ids, pm = load_terms(series)
    f = _tmp(series) / "draft" / book / f"{int(ch):02d}.html"
    html = strip_existing(f.read_text(encoding="utf-8"))
    content, _ = split_content_recap(html)
    for m in re.finditer(r"<h3[^>]*>(.*?)</h3>", content):
        s = m.start()
        nxt = re.search(r"<h3[ >]", content[m.end():])
        e = m.end() + (nxt.start() if nxt else len(content) - m.end())
        body = plain_text(content[s:e])
        labels = section_seq_labels(body, term_keys, term_ids, pm)
        # 印命中術語
        scored = sorted(
            ((sum(body.count(k) for k in keys), t) for t, keys in term_keys.items()
             if sum(body.count(k) for k in keys)),
            key=lambda x: -x[0])[:4]
        print(f"\n【{m.group(1)}】")
        print("  術語:", "，".join(f"{t}×{c}" for c, t in scored))
        print("  引用:", "、".join(labels) or "(無)")


def cmd_tag(series, pairs):
    term_keys, term_ids, pm = load_terms(series)
    for book, n in pairs:
        d = _tmp(series) / "draft" / book
        tot = 0
        for ch in range(1, n + 1):
            f = d / f"{ch:02d}.html"
            html = f.read_text(encoding="utf-8")
            new, k = tag_html(html, term_keys, term_ids, pm)
            f.write_text(new, encoding="utf-8")
            tot += k
        print(f"  {book}: {n} 章，標了 {tot} 個小節")


def main():
    a = sys.argv[1:]
    if not a:
        raise SystemExit(__doc__)
    if a[0] == "build-map":
        build_map()
    elif a[0] == "dry":
        cmd_dry(a[1], a[2], a[3])
    elif a[0] == "tag":
        series = a[1]
        rest = a[2:]
        pairs = [(rest[i], int(rest[i + 1])) for i in range(0, len(rest), 2)]
        cmd_tag(series, pairs)
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
