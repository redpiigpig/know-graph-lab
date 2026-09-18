"""/apocrypha 的兩道資料品質閘：複合檔與壞文字層。

    python scripts/apocrypha_audit_quality.py

🚨 這支是 2026-09-18 查《多馬福音》時撞出來的。當時 doc_slug=gthom 掛著 574 節，
   其中只有 213 節真的是多馬福音，其餘 361 節橫跨雅各原始福音、嬰孩多馬、
   拉丁語嬰孩福音、彼拉多文獻、腓力福音、摩尼派殘片——**整冊書被倒進一個 slug**。
   後果是「站上有全文」的統計灌水，而且那幾部書都引不出節號。

兩道閘：
  ① 複合檔：一份文獻的正文裡若出現多個「卷N…簡介」標頭，它就不是一部文獻。
  ② 壞文字層：那四冊 PDF 有文字層但那層是壞的。用字形訛誤當指標——
     「耶蕻」「約慈」「耶蘇」這些字只會出現在壞 OCR 裡，正常排版不可能有。
     🚨 這個指標只驗得出**這一套書**的壞法，不是通用的 OCR 品質分數；
     換一套書要另外找它自己的訛誤指紋。
"""
import re
import sys
from collections import Counter
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent

# 字形訛誤指紋：錯字 → 應為
BAD_GLYPHS = {
    "耶蕻": "耶穌", "耶蘇": "耶穌", "約慈": "約瑟", "豐孜": "嬰孩",
    "該斯底": "諾斯底", "偽音書": "福音書", "撤迦利亞": "撒迦利亞",
    "驛亂": "騷亂", "唉騙": "欺騙", "宮員": "官員", "間安": "問安",
    "誰各": "雅各", "木祭福": "為祝福",
}
VOL_HEAD = re.compile(r"卷[一二三四五六七八九十]+\s*(?:[IVX]+\.)?\s*.{0,30}(簡介|福音)")

DENSITY_LIMIT = 5.0      # 每萬字訛誤上限
PAGE = 1000


def env():
    return dict(l.strip().split("=", 1)
                for l in (ROOT / ".env").read_text(encoding="utf-8-sig").splitlines()
                if "=" in l and not l.startswith("#"))


def fetch_all(url, headers, path, params):
    """🚨 伺服器端 db-max-rows=1000，limit 給再大都沒用，一定要分頁。"""
    out, off = [], 0
    while True:
        p = dict(params, limit=str(PAGE), offset=str(off))
        r = requests.get(f"{url}/rest/v1/{path}", headers=headers, params=p, timeout=120)
        if r.status_code >= 400:
            raise SystemExit(f"{r.status_code} {r.text[:200]}")
        j = r.json()
        if not isinstance(j, list):
            raise SystemExit(f"PostgREST 回的不是 list：{j}")
        out += j
        if len(j) < PAGE:
            return out
        off += PAGE


def main() -> int:
    e = env()
    url = e["SUPABASE_URL"].rstrip("/")
    h = {"apikey": e["SUPABASE_SERVICE_ROLE_KEY"],
         "Authorization": "Bearer " + e["SUPABASE_SERVICE_ROLE_KEY"]}

    secs = fetch_all(url, h, "apocrypha_sections",
                     {"select": "doc_slug,text", "order": "doc_slug.asc,order_index.asc"})
    by = {}
    for s in secs:
        by.setdefault(s["doc_slug"], []).append(s["text"] or "")
    print(f"apocrypha_sections {len(secs)} 列、{len(by)} 份文獻（分頁抓完）\n")

    composite, dirty = [], []
    for slug, texts in by.items():
        blob = " ".join(texts)
        heads = sum(1 for t in texts if VOL_HEAD.search(t[:90]))
        if heads >= 2:
            composite.append((slug, len(texts), heads))
        n = sum(blob.count(b) for b in BAD_GLYPHS)
        if blob and n / len(blob) * 10000 > DENSITY_LIMIT:
            dirty.append((slug, len(texts), n, n / len(blob) * 10000))

    print(f"① 複合檔（正文含 ≥2 個「卷N…簡介」標頭）　{len(composite)} / {len(by)}")
    for slug, n, heads in sorted(composite, key=lambda x: -x[2]):
        print(f"     ✗ {slug:28} {n:>4} 節　標頭 {heads}")
    if not composite:
        print("     ✓ 無")

    print(f"\n② 壞文字層（字形訛誤 > {DENSITY_LIMIT}／萬字）　{len(dirty)} / {len(by)}")
    for slug, n, cnt, den in sorted(dirty, key=lambda x: -x[3]):
        print(f"     ✗ {slug:28} {n:>4} 節　訛誤 {cnt:>4} 次　{den:>5.1f}／萬")
    if not dirty:
        print("     ✓ 無")

    bad = len(composite) + len(dirty)
    print(f"\n{'✗ 有未解項，見上' if bad else '✓ 兩道閘皆過'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
