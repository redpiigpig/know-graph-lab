# -*- coding: utf-8 -*-
"""千面上帝：把寫好的章稿放到網站讀得到的地方。

output/qianmian/chapters/chNN.md（中繼，不進版控）
        │
        ▼
public/content/million-masks-book/chNN.md ＋ index.json（網站內容，進版控）

index.json 供 /works/million-masks 的「書稿」分頁列目次用，
每章記卷次、標題、副標、字數與註數，前端不必自己讀全文去算。
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "output" / "qianmian" / "sources"
CH = ROOT / "output" / "qianmian" / "chapters"
DEST = ROOT / "public" / "content" / "million-masks-book"

FN_DEF = re.compile(r"^\[\^(\d+)\]:", re.M)
FN_REF = re.compile(r"\[\^\d+\]")


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    index = []
    for f in sorted(SRC.glob("ch*.json")):
        meta = json.loads(f.read_text(encoding="utf-8"))
        no = meta["no"]
        md = CH / f"ch{no:02d}.md"
        if not md.exists():
            print(f"  · 第{no}章 尚未寫完，略過")
            continue
        text = md.read_text(encoding="utf-8")
        (DEST / f"ch{no:02d}.md").write_text(text, encoding="utf-8")

        body = FN_DEF.split(text)[0]
        index.append({
            "no": no,
            "volume": meta["volume"],
            "title": meta["title"],
            "span": meta["span"],
            "period": meta["period"],
            "chars": len(FN_REF.sub("", re.sub(r"[#>\-*\n]", "", body))),
            "notes": len(FN_DEF.findall(text)),
        })
        print(f"  ✓ 第{no}章 {meta['title']}：{index[-1]['chars']} 字、{index[-1]['notes']} 註")

    (DEST / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n上架 {len(index)}/28 章，共 {sum(x['chars'] for x in index):,} 字、"
          f"{sum(x['notes'] for x in index):,} 個註")


if __name__ == "__main__":
    main()
