"""佛學辭典 JSONL（Drive 正本）→ R2 `glossaries/<代號>.jsonl.gz` 服務副本。

正式站（Zeabur）讀不到 G:，server/utils/glossaries.ts 的 ensureGlossaries()
讀不到 Drive 時改讀這裡。重跑會覆蓋；上傳後讀回來比對條數，對不上就報錯。

  python -X utf8 scripts/glossaries_to_r2.py
"""
import gzip
import re
import sys
from pathlib import Path

import boto3

ROOT = Path(__file__).resolve().parent.parent
CORPUS = Path("G:/我的雲端硬碟/資料/知識圖工作室/_corpus")
DIRS = ["dila-glossaries", "fgs-dictionary"]
PREFIX = "glossaries/"


def codes() -> list[str]:
    """跟 server 端同一份名單：只上 GLOSSARY_NAMES 登記過的（排除 entries.jsonl 之類）。"""
    ts = (ROOT / "server/utils/glossaries.ts").read_text(encoding="utf-8")
    block = ts.split("GLOSSARY_NAMES", 1)[1].split("};", 1)[0]
    return re.findall(r"^\s*([A-Z]+):", block, re.M)


def main() -> None:
    env = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8-sig").splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    s3 = boto3.client("s3", region_name="auto", endpoint_url=env["R2_ENDPOINT"],
                      aws_access_key_id=env["R2_ACCESS_KEY"],
                      aws_secret_access_key=env["R2_SECRET_KEY"])
    bucket = env["R2_BUCKET"]

    want = codes()
    print(f"登記 {len(want)} 部：{' '.join(want)}")
    done, total_rows, total_bytes = 0, 0, 0
    for code in want:
        src = next((CORPUS / d / f"{code}.jsonl" for d in DIRS
                    if (CORPUS / d / f"{code}.jsonl").exists()), None)
        if not src:
            print(f"  ✗ {code}: Drive 上找不到")
            continue
        raw = src.read_bytes()
        n = sum(1 for l in raw.decode("utf-8").split("\n") if l.strip())
        gz = gzip.compress(raw, 9)
        key = f"{PREFIX}{code}.jsonl.gz"
        s3.put_object(Bucket=bucket, Key=key, Body=gz, ContentType="application/gzip")
        back = gzip.decompress(s3.get_object(Bucket=bucket, Key=key)["Body"].read())
        m = sum(1 for l in back.decode("utf-8").split("\n") if l.strip())
        if m != n:
            sys.exit(f"  ✗ {code}: 讀回 {m} 條 ≠ 原檔 {n} 條")
        print(f"  ✓ {code}: {n:,} 條  {len(raw)/1e6:.1f} → {len(gz)/1e6:.1f} MB")
        done += 1
        total_rows += n
        total_bytes += len(gz)
    print(f"完成 {done}/{len(want)} 部、{total_rows:,} 條、R2 {total_bytes/1e6:.1f} MB")
    if done != len(want):
        sys.exit(1)


if __name__ == "__main__":
    main()
