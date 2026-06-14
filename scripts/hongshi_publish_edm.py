# -*- coding: utf-8 -*-
"""發佈弘誓電子報 (C:/tmp/hongshi_dl/edm/edm-N.json) 成站台內容。

輸出：
  public/content/research-data/yinshun-hongshi/edm-index.json   [{n,date,title,chars}]
  public/content/research-data/yinshun-hongshi/edm/<n>.json     {n,date,title,text}
canonical：G:\\…\\印順學派與弘誓研究資料\\電子報\\edm-N.txt

  python -X utf8 scripts/hongshi_publish_edm.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(r"C:/tmp/hongshi_dl/edm")
DRIVE = Path(r"G:\我的雲端硬碟\公事\印順學派與弘誓研究資料\電子報")
OUT = ROOT / "public/content/research-data/yinshun-hongshi"

_DATE = re.compile(r"(20\d{2})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日")


def parse(text: str):
    """→ (date_display, title). 期首通常有發行日期與『本期目錄』。"""
    date = ""
    m = _DATE.search(text[:400])
    if m:
        date = f"{m.group(1)}/{int(m.group(2)):02d}/{int(m.group(3)):02d}"
    # title = first 目錄 item or first meaningful line after 本期目錄
    title = ""
    mi = re.search(r"本\s*期\s*目\s*錄\s*[\n■、]*\s*([^\n■]{4,40})", text)
    if mi:
        title = mi.group(1).strip()
    return date, title


def main():
    DRIVE.mkdir(parents=True, exist_ok=True)
    (OUT / "edm").mkdir(parents=True, exist_ok=True)
    rows = []
    for f in sorted(SRC.glob("edm-*.json"), key=lambda p: int(re.search(r"(\d+)", p.stem).group(1))):
        d = json.loads(f.read_text(encoding="utf-8"))
        n = d["n"]
        text = (d.get("text") or "").strip()
        if not text:
            continue
        date, title = parse(text)
        rows.append({"n": n, "date": date, "title": title, "chars": len(text)})
        (OUT / "edm" / f"{n}.json").write_text(
            json.dumps({"n": n, "date": date, "title": title, "text": text}, ensure_ascii=False, indent=2),
            encoding="utf-8")
        (DRIVE / f"edm-{n}.txt").write_text(f"弘誓電子報 第 {n} 期　{date}\n\n{text}\n", encoding="utf-8")
    rows.sort(key=lambda r: -r["n"])
    (OUT / "edm-index.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"published {len(rows)} EDM issues → edm-index.json + edm/<n>.json + Drive backup")


if __name__ == "__main__":
    main()
