# -*- coding: utf-8 -*-
"""把一貫道那批研究資料從 repo 搬到 R2（gzip），供需登入的端點讀取。

    python -X utf8 scripts/yiguandao_r2_sync.py            # 上傳
    python -X utf8 scripts/yiguandao_r2_sync.py --status   # 只看兩邊有什麼
    python -X utf8 scripts/yiguandao_r2_sync.py --dry-run

為什麼要搬：**repo 是公開的**（github.com/redpiigpig/know-graph-lab，visibility=public）。
這批東西帶著檔案局目錄裡的人名，還加上「此人被列管 21 年」這類分析——書目本身在
檔案局網站上是公開的，但把分析放進公開 repo 是另一回事。2026-09-06 使用者定調：
搬 R2、加需登入的端點，repo 只留程式碼；本機那份留著（`.gitignore` 擋住不追蹤）。

配套：`server/api/research-data/yiguandao-file.get.ts`（requireAdmin）＋頁面改 authedFetch。

🚨 **搬走之後本機那份就是唯一的可編輯正本**，git 不再保管。改了 report.md／
   timeline.json 一定要重跑這支上傳，否則線上還是舊的——而且頁面照樣顯示得好好的，
   看不出來是舊資料。

🚨 已經推上去的三個 commit 不會因此消失（歷史刪不掉，使用者選擇不改寫）。
   這支腳本處理的是「從現在起不再往公開 repo 放」。
"""
import argparse
import gzip
import sys
from pathlib import Path

try:
    import boto3
except ImportError:                                        # pragma: no cover
    sys.exit("缺 boto3：pip install boto3")

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "public/content/research-data/yiguandao"
PREFIX = "research-private/yiguandao/"

# 白名單，與端點那邊的 ALLOWED 必須一致。不用萬用字元掃目錄——多掃到一個檔就是
# 多公開一份東西，寧可新增檔案時手動加一行。
FILES = (
    "archives-index.json",
    "biblio-zhong.json",
    "guoshiguan.json",
    "inventory.json",
    "timeline.json",
    "report.md",
    "progress/2026-09.md",
)


def load_env() -> dict:
    env = {}
    path = ROOT / ".env"
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


ENV = load_env()


def client():
    return boto3.client(
        "s3", region_name="auto",
        endpoint_url=ENV["R2_ENDPOINT"],
        aws_access_key_id=ENV["R2_ACCESS_KEY"],
        aws_secret_access_key=ENV["R2_SECRET_KEY"],
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    s3, bucket = client(), ENV["R2_BUCKET"]

    if args.status:
        got = s3.list_objects_v2(Bucket=bucket, Prefix=PREFIX).get("Contents", [])
        print(f"R2 {PREFIX}（{len(got)} 個物件）")
        for o in sorted(got, key=lambda x: x["Key"]):
            print(f"  {o['Size']:>9,}  {o['Key']}")
        print(f"\n本機 {SRC}")
        for name in FILES:
            p = SRC / name
            print(f"  {p.stat().st_size:>9,}  {name}" if p.exists() else f"  {'缺':>9}  {name}")
        return

    total_raw = total_gz = 0
    for name in FILES:
        path = SRC / name
        if not path.exists():
            print(f"  跳過（本機沒有）{name}")
            continue
        raw = path.read_bytes()
        # mtime 固定成 0：同樣內容重跑要產生同樣的 gzip，否則每次都變更
        body = gzip.compress(raw, mtime=0)
        key = f"{PREFIX}{name}.gz"       # r2Text() 會先試 .gz
        total_raw += len(raw)
        total_gz += len(body)
        if args.dry_run:
            print(f"  [dry] {len(raw):>9,} → {len(body):>8,}  {key}")
            continue
        s3.put_object(Bucket=bucket, Key=key, Body=body,
                      ContentType="application/gzip")
        print(f"  {len(raw):>9,} → {len(body):>8,}  {key}")
    print(f"\n合計 {total_raw:,} → {total_gz:,} bytes"
          f"（{total_gz / total_raw:.0%}）" if total_raw else "\n沒有東西可傳")


if __name__ == "__main__":
    main()
