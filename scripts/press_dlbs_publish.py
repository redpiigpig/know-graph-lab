# -*- coding: utf-8 -*-
"""臺大佛圖篇目：篇目清單移 R2，git 只留各刊統計索引。

為什麼不整批放 git：400 刊 33 萬筆＝129 MB，而其中一大半（日文與韓文的佛教學
期刊、敦煌學、宗派紀要）跟博論沒有直接關係，是掃全庫順手收下來的。
放進 git 等於每個 clone 都要付那個代價，而這一層的用途只是「查得到」。

分工照既有的 TCNN 那一套（全文 jsonl.gz 在 R2、index 在 git）：

  R2   research-private/dlbs/<slug>.jsonl.gz   逐筆篇目
  git  public/content/research-data/press/dlbs-index.json   400 刊的統計

🚨 **先上傳成功才刪本地檔**。反過來寫的話，R2 掛掉的那一刻資料就沒了，
   而腳本會照常印出「完成」。本檔的順序是 上傳 → 驗證 key 真的在 → 才 unlink。

  python -X utf8 scripts/press_dlbs_publish.py --dry-run
  python -X utf8 scripts/press_dlbs_publish.py --publish
  python -X utf8 scripts/press_dlbs_publish.py --publish --keep-local
"""
import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import dadaodao_fulltext as df  # noqa: E402

SRC = REPO / "public/content/research-data/press/dlbs"
INDEX = REPO / "public/content/research-data/press/dlbs-index.json"
PREFIX = "research-private/dlbs"


def rows():
    for f in sorted(SRC.glob("*.json")):
        yield f, json.loads(f.read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--keep-local", action="store_true",
                    help="上傳但不刪本地檔（想先自己看過再刪時用）")
    a = ap.parse_args()
    if not (a.dry_run or a.publish):
        ap.print_help()
        return

    have = set() if a.dry_run else df.r2_existing_keys(PREFIX)
    index, up, skipped, bytes_freed = [], 0, 0, 0
    for f, d in rows():
        key = f"{PREFIX}/{d['slug']}.jsonl.gz"
        c = d["counts"]
        index.append({
            "slug": d["slug"], "name": d["name"].strip(),
            "articles": c["篇目"], "fulltext": c["有全文"],
            "missingVol": c["缺卷期"], "missingPage": c["缺頁次"],
            "start": d["years"]["min"], "end": d["years"]["max"],
            "key": key,
        })
        if a.dry_run:
            continue
        if key not in have:
            body = "\n".join(json.dumps(x, ensure_ascii=False) for x in d["articles"])
            df.r2_put_text_gz(key, body)
            up += 1
        else:
            skipped += 1
        # 🚨 確認 R2 上真的有了才刪本地檔。上傳失敗多半不會拋例外，
        #    先刪再驗的話資料就沒了，而腳本照樣印「完成」。
        if not a.keep_local and df.r2_exists(key):
            bytes_freed += f.stat().st_size
            f.unlink()

    index.sort(key=lambda r: -r["articles"])
    INDEX.write_text(json.dumps(
        {"note": "臺大佛學數位圖書館的期刊篇目。逐筆資料在 R2 "
                 f"`{PREFIX}/<slug>.jsonl.gz`，本檔只留各刊統計——"
                 "33 萬筆放 git 會讓每個 clone 都付代價，而這一層的用途只是查得到。",
         "source": "https://dlbs.liberal.ntu.edu.tw/solr/mit/select",
         "counts": {"刊": len(index),
                    "篇目": sum(r["articles"] for r in index),
                    "有全文": sum(r["fulltext"] for r in index)},
         "journals": index}, ensure_ascii=False, indent=1), encoding="utf-8")

    tot = sum(r["articles"] for r in index)
    if a.dry_run:
        print(f"[試跑] {len(index)} 刊 / {tot:,} 篇目 → 會上傳 {len(index)} 個 R2 物件")
    else:
        print(f"{len(index)} 刊 / {tot:,} 篇目｜新上傳 {up}、既有 {skipped}、"
              f"本地釋出 {bytes_freed / 1024 / 1024:.0f} MB")
    print(f"→ {INDEX}")


if __name__ == "__main__":
    main()
