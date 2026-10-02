#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""天主教在線：把 z-lib/zlz 頂層已下載的檔，按站方分類分流 → trc_ingest（去重／Drive／ebooks）。

  python scripts/zlz_ingest.py [--run]      # 預設 dry-run

帳本 c:/tmp/zlz_downloaded.json 的 name 對到條目網址，網址帶分類。
站方分類 → Drive 落點（既有資料夾，不新開）：
  wenxian/shenxue/shengjing/yanjiu/lingxiu/qita → 神學/天主教文獻
  zhexue → 哲學　lishi/zhuanji → 歷史學　cidian → 神學/聖經與神學辭典
"""
from __future__ import annotations
import argparse, json, re, shutil, subprocess, sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
DROP = ROOT / "z-lib" / "zlz"
LEDGER = Path("c:/tmp/zlz_downloaded.json")
DEST = {
    "wenxian": ("神學", "天主教文獻"), "shenxue": ("神學", "天主教文獻"),
    "shengjing": ("神學", "天主教文獻"), "yanjiu": ("神學", "天主教文獻"),
    "lingxiu": ("神學", "天主教文獻"), "qita": ("神學", "天主教文獻"),
    "zhexue": ("哲學", ""), "lishi": ("歷史學", ""), "zhuanji": ("歷史學", ""),
    "cidian": ("神學", "聖經與神學辭典"),
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    a = ap.parse_args()
    led = json.loads(LEDGER.read_text(encoding="utf-8"))
    byname = {v["name"]: u for u, v in led.items()}
    groups: dict[str, list[Path]] = {}
    for p in DROP.iterdir():
        if not p.is_file() or p.name.endswith(".part"):
            continue
        u = byname.get(p.name)
        m = re.search(r"/pdf/([a-z]+)/", u or "")
        if not m:
            print(f"  ?? 帳本無此檔，略過：{p.name}")
            continue
        groups.setdefault(m.group(1), []).append(p)
    for cat, files in groups.items():
        dc, sub = DEST[cat]
        stage = DROP / "_stage" / cat
        stage.mkdir(parents=True, exist_ok=True)
        mp = {}
        for p in files:
            shutil.move(str(p), str(stage / p.name))
            mp[p.name] = f"/{cat}/{p.stem}"
        mf = stage.parent / f"{cat}_map.json"
        mf.write_text(json.dumps(mp, ensure_ascii=False), encoding="utf-8")
        cmd = [sys.executable, "-X", "utf8", str(ROOT / "scripts" / "trc_ingest.py"),
               "--src", str(stage), "--map", str(mf), "--category", dc,
               "--min-mb", "0.02"]
        if sub:
            cmd += ["--sub", sub]
        if a.run:
            cmd += ["--run", "--register"]
        print(f"=== {cat} → {dc}/{sub} ({len(files)} 檔)")
        subprocess.run(cmd, check=False)
        if a.run:
            for q in stage.iterdir():   # 殘留（低於門檻或失敗）留 stage，不丟回頂層
                if q.is_file():
                    print(f"  殘留 {q.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
