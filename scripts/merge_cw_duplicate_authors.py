#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合併 /collected-works 上重複的作家 hub（2026-09-11 使用者指出）。

站上同一個人出現兩張卡：

  釋太虛 ／ 太虛大師   → 兩邊 slug 都是 `taixu`（**撞號**），內容也一樣的 21 卷
  釋昭慧 ／ 昭慧法師   → slug 不同（shih-chao-hwei ／ chao-hwei），所以真的各自成卡
  釋性廣               → 改名「性廣法師」（沒有重複，只是稱謂要一致）

使用者裁定「保留後者」＝保留法師稱謂那張。但**不能直接刪掉前者**：
`釋昭慧` 那張帶 40 筆書目，而 `昭慧法師` 只有 13 筆——照字面刪會把書目一起丟掉。
所以是「把書目併過去、再刪卡」，不是「刪卡」。

  python -X utf8 scripts/merge_cw_duplicate_authors.py            # dry-run
  python -X utf8 scripts/merge_cw_duplicate_authors.py --apply
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQ = ROOT / "data/requestedCollectedWorks.ts"
STORE = ROOT / "stores/collectedWorks.ts"


# ── 純函式（scripts/tests/test_merge_cw_duplicate_authors.py 鎖定）─────────

def title_key(title: str) -> str:
    """書名比對鍵：破折號、括號與空白寫法各家不一，統一掉才比得出重複。

    「心靈的交會——山間對話」與「心靈的交會：山間對話」是同一本；
    「佛教規範倫理學」與「佛教規範倫理學——從佛教倫理學到…」也是（前者是簡稱），
    所以長書名以**冒號／破折號之前**那一段為鍵。
    """
    t = (title or "").strip()
    t = re.split(r"[—–\-：:（(]", t)[0]
    return re.sub(r"[\s　]+", "", t)


def new_titles(existing: list[str], incoming: list[str]) -> list[str]:
    """incoming 裡不在 existing 的（依 title_key 去重，保序）。"""
    have = {title_key(t) for t in existing}
    out, seen = [], set()
    for t in incoming:
        k = title_key(t)
        if k in have or k in seen:
            continue
        seen.add(k)
        out.append(t)
    return out


def author_span(lines: list[str], slug: str) -> tuple[int, int]:
    """在 requestedCollectedWorks.ts 找某個作家物件的行範圍 [start, end)。

    start 指向物件開頭的 `  {`，end 指向下一個物件的 `  {`（或陣列結尾）。
    """
    idx = next(i for i, l in enumerate(lines) if l.strip() == f"slug: '{slug}',")
    start = idx
    while start > 0 and lines[start].strip() != "{":
        start -= 1
    end = idx + 1
    while end < len(lines) and lines[end].strip() != "{":
        end += 1
    return start, end


# ── I/O ────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    req_lines = REQ.read_text(encoding="utf-8").split("\n")
    store_text = STORE.read_text(encoding="utf-8")

    # 昭慧法師（store）現有書名
    i = store_text.index("slug: 'chao-hwei',")
    j = store_text.index("    },\n\n", i)
    chao_seg = store_text[i:j]
    existing = re.findall(r"title: '([^']+)'", chao_seg)

    # 釋昭慧（requested）的書名與原始 work(...) 行
    s0, s1 = author_span(req_lines, "shih-chao-hwei")
    chao_req = "\n".join(req_lines[s0:s1])
    incoming_lines = [l for l in req_lines[s0:s1] if l.strip().startswith("work(")]
    incoming = [re.search(r"work\('([^']+)'", l).group(1) for l in incoming_lines]

    add = new_titles(existing, incoming)
    print(f"昭慧法師現有 {len(existing)} 筆；釋昭慧 {len(incoming)} 筆")
    print(f"→ 要併入 {len(add)} 筆新書目：")
    for t in add:
        print("   ", t)
    dup = [t for t in incoming if t not in add]
    print(f"→ {len(dup)} 筆已存在，不重複加")

    t0, t1 = author_span(req_lines, "taixu")
    print(f"\n釋太虛：刪掉 requested 第 {t0 + 1}–{t1} 行"
          f"（與 store 的太虛大師 **slug 同為 taixu**，內容同樣 21 卷）")
    print(f"釋昭慧：刪掉 requested 第 {s0 + 1}–{s1} 行（書目已併入昭慧法師）")
    print("釋性廣：改名為「性廣法師」")

    if not a.apply:
        print("\n（dry-run，加 --apply 才會寫檔）")
        return 0

    # 1) 併書目進 store 的 chao-hwei：插在 works 陣列尾端
    add_set = set(add)
    keep_lines = [l for l in incoming_lines
                  if re.search(r"work\('([^']+)'", l).group(1) in add_set]
    rendered = []
    for l in keep_lines:
        m = re.search(r"work\('([^']+)',\s*'([^']*)'", l)
        title, year = m.group(1), m.group(2)
        ys = re.search(r"\d{4}", year)
        cat = re.search(r"',\s*'([^']+)'\s*[,)]", l[l.index(year) + len(year):])
        rendered.append(
            "        {\n"
            f"          title: '{title}',\n"
            f"          year: '{year}',\n"
            f"          yearSort: {ys.group(0) if ys else 0},\n"
            f"          category: '{cat.group(1) if cat else '專書'}',\n"
            "          languages: ['zh'],\n"
            "          status: 'planned',\n"
            "        },")
    anchor = store_text.index("      ],\n    },", store_text.index("slug: 'chao-hwei',"))
    store_text = store_text[:anchor] + "\n".join(rendered) + "\n" + store_text[anchor:]
    STORE.write_text(store_text, encoding="utf-8")
    print(f"✅ 併入 {len(rendered)} 筆 → stores/collectedWorks.ts")

    # 2) 刪 requested 的兩個重複物件（由後往前刪，行號才不會位移）
    for lo, hi, who in sorted([(t0, t1, "釋太虛"), (s0, s1, "釋昭慧")], reverse=True):
        del req_lines[lo:hi]
        print(f"✅ 已刪 {who}")
    # 3) 釋性廣 → 性廣法師
    out = "\n".join(req_lines).replace("name: '釋性廣',", "name: '性廣法師',")
    REQ.write_text(out, encoding="utf-8")
    print("✅ 釋性廣 → 性廣法師")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
