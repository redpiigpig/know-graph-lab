# -*- coding: utf-8 -*-
"""R2 縮容：分三批刪除，每批都先過驗證閘，預設 dry-run。

  orphans   孤兒縮圖（index.json 已無對應原檔）      閘：cacheKey 不在 index
  thumbs    舊 _1600 燈箱圖                          閘：同 key 的 _1024 已存在
  research  研究資料大宗原檔                          閘：Drive 有同名同大小

用法： python scripts/r2_reclaim.py [orphans|thumbs|research|all] [--go]
"""
import os, sys, json, hashlib, collections
import boto3
from botocore.config import Config

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for line in open(os.path.join(ROOT, ".env"), encoding="utf-8"):
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
s3 = boto3.client("s3", endpoint_url=os.environ["R2_ENDPOINT"],
    aws_access_key_id=os.environ["R2_ACCESS_KEY"], aws_secret_access_key=os.environ["R2_SECRET_KEY"],
    config=Config(signature_version="s3v4", region_name="auto"))
B = os.environ["R2_BUCKET"]

# 仍留在雲端的研究資料子前綴（與 material.get.ts / works [slug] 頁同步）
KEEP = ("dadaodao-materials/碩士文稿/", "dadaodao-materials/研究回顧/")
DRIVE_ROOTS = {
    "dadaodao-materials/": r"G:\我的雲端硬碟\資料\知識圖工作室\研究資料\大愛道革命\論文資料",
    "yinshun-hongshi/":    r"G:\我的雲端硬碟\資料\知識圖工作室\研究資料\印順學派與弘誓",
}

def listing():
    out, tok = [], None
    while True:
        kw = dict(Bucket=B, MaxKeys=1000)
        if tok: kw["ContinuationToken"] = tok
        r = s3.list_objects_v2(**kw)
        out += [(o["Key"], o["Size"]) for o in r.get("Contents", [])]
        if not r.get("IsTruncated"): break
        tok = r.get("NextContinuationToken")
    return out

def ck(parts): return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:32]

def live_cachekeys():
    idx = json.loads(s3.get_object(Bucket=B, Key="photos/index.json")["Body"].read())
    keys = set()
    c = idx["libraries"].get("chenwei")
    if c:
        for year, yd in c["years"].items():
            for bucket, files in yd["buckets"].items():
                for f in files: keys.add(ck(["chenwei", year, bucket, f["name"]]))
    for slug in ("training", "hongshi"):
        lib = idx["libraries"].get(slug)
        if not lib: continue
        for subpath, node in lib.get("folders", {}).items():
            for f in node.get("files", []): keys.add(ck(["lib", slug, subpath, f["name"]]))
    return keys

def drive_sizes(root):
    d = {}
    for dp, _, fns in os.walk(root):
        for fn in fns:
            if fn.lower() == "desktop.ini": continue
            try: d.setdefault(fn, []).append(os.path.getsize(os.path.join(dp, fn)))
            except OSError: pass
    return d

def gate_orphans(objs):
    live = live_cachekeys()
    return [(k, s) for k, s in objs if k.startswith("photos/thumb/")
            and k.split("/")[-1].rsplit(".", 1)[0].rsplit("_", 1)[0] not in live]

def gate_thumbs(objs):
    have = {k for k, _ in objs if k.endswith("_1024.webp")}
    return [(k, s) for k, s in objs if k.endswith("_1600.webp")
            and k.replace("_1600.webp", "_1024.webp") in have]

def gate_research(objs):
    kill, skipped = [], 0
    for prefix, root in DRIVE_ROOTS.items():
        drive = drive_sizes(root)
        for k, s in objs:
            if not k.startswith(prefix) or k.startswith(KEEP): continue
            if s in drive.get(k.split("/")[-1], []): kill.append((k, s))
            else: skipped += 1
    if skipped: print(f"  ⚠ {skipped} 檔 Drive 無同名同大小備份 → 不刪")
    return kill

GATES = {"orphans": gate_orphans, "thumbs": gate_thumbs, "research": gate_research}

def main():
    which = [a for a in sys.argv[1:] if not a.startswith("--")] or ["all"]
    names = list(GATES) if which == ["all"] else which
    go = "--go" in sys.argv
    print("列出 bucket…", flush=True)
    objs = listing()
    print(f"目前 {len(objs):,} 物件 / {sum(s for _, s in objs)/1e9:.2f} GB\n")

    total = []
    for name in names:
        kill = GATES[name](objs)
        print(f"[{name}] 通過驗證閘可刪：{len(kill):,} 物件 / {sum(s for _, s in kill)/1e9:.3f} GB")
        total += kill
    print(f"\n合計 {len(total):,} 物件 / {sum(s for _, s in total)/1e9:.3f} GB")
    after = sum(s for _, s in objs) - sum(s for _, s in total)
    print(f"刪後總量 {after/1e9:.2f} GB（免費額度 10 GB）→ 月費 ${max(0,(after/1e9-10))*0.015:.2f}")

    if not go:
        print("\n(dry-run；加 --go 才真的刪)"); return
    seen, n = set(), 0
    uniq = [(k, s) for k, s in total if not (k in seen or seen.add(k))]
    for i in range(0, len(uniq), 1000):
        batch = [{"Key": k} for k, _ in uniq[i:i+1000]]
        r = s3.delete_objects(Bucket=B, Delete={"Objects": batch, "Quiet": True})
        if r.get("Errors"): print("  err:", r["Errors"][:3])
        n += len(batch)
        print(f"  已刪 {n:,}/{len(uniq):,}", flush=True)
    print("完成")

main()
