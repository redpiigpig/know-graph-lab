# -*- coding: utf-8 -*-
"""把抓回的學團日誌 (C:/tmp/hongshi_dl/log/log-NNN.json) 發佈成站台內容。

輸出：
  public/content/research-data/yinshun-hongshi/log-index.json   [{n,range,chars}]
  public/content/research-data/yinshun-hongshi/log/<n>.json     {n,range,text}
canonical 備份：G:\\…\\印順學派與弘誓研究資料\\學團日誌\\log-NNN.txt

  python -X utf8 scripts/hongshi_publish_log.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(r"C:/tmp/hongshi_dl/log")
DRIVE = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\研究資料\印順學派與弘誓\學團日誌")
OUT = ROOT / "public/content/research-data/yinshun-hongshi"


def main():
    DRIVE.mkdir(parents=True, exist_ok=True)
    (OUT / "log").mkdir(parents=True, exist_ok=True)
    rows = []
    for f in sorted(SRC.glob("log-*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        n = d["n"]
        text = (d.get("text") or "").strip()
        if not text:
            continue
        rows.append({"n": n, "range": d.get("range", ""), "chars": len(text)})
        (OUT / "log" / f"{n}.json").write_text(
            json.dumps({"n": n, "range": d.get("range", ""), "text": text}, ensure_ascii=False, indent=2),
            encoding="utf-8")
        (DRIVE / f"log-{n:03d}.txt").write_text(
            f"學團日誌 第 {n} 期　{d.get('range','')}\n\n{text}\n", encoding="utf-8")
    rows.sort(key=lambda r: -r["n"])
    (OUT / "log-index.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"published {len(rows)} log entries → log-index.json + log/<n>.json + Drive backup")


if __name__ == "__main__":
    main()
