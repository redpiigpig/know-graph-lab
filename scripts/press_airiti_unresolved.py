# -*- coding: utf-8 -*-
"""診斷書目點名卻對不上 docID 的那些篇。

    python -X utf8 scripts/press_airiti_unresolved.py

`resolve_wanted()` 會把對不上的留在 `airiti-wanted.json` 的 `unresolved` 裡並附
`why`，但只寫了「為什麼沒對上」，沒說「那該怎麼辦」。這支補上後半段：對
「篇名對不上」那一類，回頭在該刊篇目裡做模糊比對，把最接近的候選印出來，
好人工判斷是**寫法差異**（改書目就好）還是**華藝真的沒有**（要另找來源）。

分類直接沿用 `why`，不自己重新分桶——那會跟腳本本身的判斷打架。

🚨 **`articles` 是 TOC JSON 的頂層平坦清單，不是掛在 `issues` 底下。**
   照 `issues → articles` 去找會拿到空清單，而症狀是「每一筆都是篇目還沒抓」——
   整齊得可疑的分佈就是這個 bug 的長相。

🚨 **相似度 100% 不代表腳本漏抓。** 那多半是「華藝沒有這一篇的電子全文」：
   篇名對得上、docID 也有，只是沒有 PDF 可下載，所以照樣進 unresolved。
   看 `why` 才知道是哪一種。
"""
import json
import sys
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from press_airiti import OUT, TOC_DIR, norm_title  # noqa: E402

WANTED = OUT / "airiti-wanted.json"
NEAR = 0.75          # 相似度到這裡就當「多半是同一篇，只是寫法不同」


def toc_rows(slug):
    """該刊全部篇目 → [(正規化篇名, 原篇名, 卷期, 有無電子全文)]。"""
    p = TOC_DIR / f"{slug}.json"
    if not p.exists():
        return []
    d = json.loads(p.read_text(encoding="utf-8"))
    return [(norm_title(a.get("title", "")), a.get("title", ""),
             a.get("issueLabel", ""), bool(a.get("fulltext")))
            for a in d.get("articles", [])]


def main():
    w = json.loads(WANTED.read_text(encoding="utf-8"))
    cache, groups = {}, {}
    for it in w["unresolved"]:
        why = it.get("why", "").split("：", 1)[-1] or "（未註明）"
        groups.setdefault(why, []).append(it)

    for why, items in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        print(f"\n{'=' * 76}\n{why}　{len(items)} 筆\n{'=' * 76}")
        rows = []
        for it in items:
            slug = it.get("slug") or ""
            if slug not in cache:
                cache[slug] = toc_rows(slug)
            best, ratio = None, 0.0
            key = norm_title(it["title"])
            for nt, orig, label, has in cache[slug]:
                r = SequenceMatcher(None, key, nt).ratio()
                if r > ratio:
                    best, ratio = (orig, label, has), r
            rows.append((it, best, ratio))
        for it, best, ratio in sorted(rows, key=lambda x: -x[2]):
            tag = "★可補" if ratio >= NEAR else "  待查"
            print(f"\n{tag}　〈{it['title']}〉")
            print(f"      {it.get('author', '?')}／{it['venue']}"
                  f"{'／' + it['year'] if it.get('year') else ''}"
                  f"　書目來源={it.get('source', '?')}")
            if best:
                print(f"      華藝最接近：〈{best[0]}〉{best[1]}"
                      f"（{'有全文' if best[2] else '無全文'}）　相似度 {ratio:.0%}")
            else:
                print(f"      該刊篇目尚未抓（--toc {it.get('slug') or '?'}）")

    total = len(w["unresolved"])
    near = sum(1 for items in groups.values() for it in items)
    print(f"\n{'=' * 76}\n合計 {total} 筆；已對到 docID 的有 {w['counts']['對到 docID']} 篇。"
          f"（{near} 筆逐條列於上）")


if __name__ == "__main__":
    main()
