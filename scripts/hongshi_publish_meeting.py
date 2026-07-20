# -*- coding: utf-8 -*-
"""發佈弘誓/玄奘 歷屆學術活動 (C:/tmp/hongshi_dl/meeting/meet-N.json) 成站台內容。

輸出：
  public/content/research-data/yinshun-hongshi/meeting-index.json   [{n,title,year,chars}]
  public/content/research-data/yinshun-hongshi/meeting/<n>.json     {n,title,text}
canonical：G:\\…\\印順學派與弘誓研究資料\\學術活動\\meet-N.txt（best-effort）

  python -X utf8 scripts/hongshi_publish_meeting.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(r"C:/tmp/hongshi_dl/meeting")
DRIVE = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\研究資料\印順學派與弘誓\學術活動")
OUT = ROOT / "public/content/research-data/yinshun-hongshi"

_YEAR = re.compile(r"(20\d{2})\s*年")


def drive_write(name: str, text: str) -> None:
    try:
        DRIVE.mkdir(parents=True, exist_ok=True)
        (DRIVE / name).write_text(text, encoding="utf-8")
    except Exception:  # noqa: BLE001  G: not mounted → skip
        pass


def main():
    (OUT / "meeting").mkdir(parents=True, exist_ok=True)
    rows = []
    for f in sorted(SRC.glob("meet-*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        n = d["n"]
        text = (d.get("text") or "").strip()
        title = (d.get("title") or "").strip()
        if not text:
            continue
        my = _YEAR.search(title) or _YEAR.search(text[:200])
        year = int(my.group(1)) if my else 0
        rows.append({"n": n, "title": title, "year": year, "chars": len(text)})
        (OUT / "meeting" / f"{n}.json").write_text(
            json.dumps({"n": n, "title": title, "year": year, "text": text}, ensure_ascii=False, indent=2),
            encoding="utf-8")
        drive_write(f"meet-{n}.txt", f"{title}\n\n{text}\n")
    # newest first: by year then n
    rows.sort(key=lambda r: (-(r["year"] or 0), -r["n"]))
    (OUT / "meeting-index.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"published {len(rows)} activities → meeting-index.json + meeting/<n>.json")


if __name__ == "__main__":
    main()
