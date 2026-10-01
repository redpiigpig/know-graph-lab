"""批次跑 relink：python batch.py rule|llm ；每本前重讀 DNT、驗 bak_restructure、驗 G:。"""
import sys, subprocess, time, re
from pathlib import Path

ROOT = Path(r"C:\Users\user\Desktop\know-graph-lab")
CH = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\_chunks")
PY = sys.executable
mode = sys.argv[1]
PRI = {"神學", "宗教學", "世界宗教"}
rows = [l.split("\t") for l in (ROOT / "output/relink/booktypes.tsv").read_text(encoding="utf-8").splitlines()[1:]]
rows = [x for x in rows if x[-1][0] in "ABCD"]
rows.sort(key=lambda x: (0 if x[2] in PRI else 1, -int(x[4])))
quota_hits = 0
for x in rows:
    bid = x[0]
    if not Path(r"G:\我的雲端硬碟").exists():
        print("G: 不見了，停手", flush=True)
        sys.exit(3)
    dnt = set((ROOT / "output/restructure/DO_NOT_TOUCH_ids.txt").read_text(encoding="utf-8").split())
    if bid in dnt:
        print("SKIP DNT", bid, flush=True)
        continue
    if not (CH / f"{bid}.jsonl.bak_restructure").exists():
        print("SKIP no bak_restructure", bid, flush=True)
        continue
    args = [PY, "-X", "utf8", str(ROOT / "scripts/relink_missing_footnotes.py"), "--ids", bid, "--apply"]
    if mode == "llm":
        args.append("--llm")
    print(f"=== {bid} {x[1]} [{x[2]}] type={x[-1]} miss={x[4]}", flush=True)
    p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", cwd=str(ROOT))
    lines = (p.stdout or "").splitlines()
    for l in lines:
        if l.startswith(bid) or l.startswith("  已寫回") or "✗" in l and mode == "llm" and False:
            print(l, flush=True)
    tail = (p.stderr or "")[-300:]
    if p.returncode:
        print("ERR rc", p.returncode, tail, flush=True)
    if mode == "llm":
        errs = sum(1 for l in lines if "位置不唯一" in l)
        if re.search(r"429|quota|RESOURCE_EXHAUSTED", (p.stdout or "") + (p.stderr or ""), re.I):
            quota_hits += 1
            print("quota-ish hit", quota_hits, flush=True)
            if quota_hits >= 2:
                print("連續額度錯，停", flush=True)
                break
        else:
            quota_hits = 0
print("BATCH DONE", mode, flush=True)
