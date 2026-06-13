#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把碩士論文「論文資料」archive 全數上傳到 R2，key = dadaodao-materials/<相對路徑>。
冪等：已存在且大小相同則跳過；可重跑接續。檔案清單讀 C:\\tmp\\dadaodao_files.json。
  python -X utf8 scripts/upload_dadaodao_r2.py
網站經 /api/works/material?key=... 簽名下載。
"""
import json
import os
import sys
import mimetypes
from pathlib import Path

import boto3
from botocore.config import Config

ROOT_ENV = Path(__file__).resolve().parents[1] / ".env"
env = {}
for line in ROOT_ENV.read_text(encoding="utf-8").splitlines():
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")

BUCKET = env["R2_BUCKET"]
PREFIX = "dadaodao-materials"
LIST = Path(r"C:\tmp\dadaodao_files.json")

CT = {
    ".pdf": "application/pdf", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".png": "image/png", ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}

s3 = boto3.client(
    "s3", region_name="auto", endpoint_url=env["R2_ENDPOINT"],
    aws_access_key_id=env["R2_ACCESS_KEY"], aws_secret_access_key=env["R2_SECRET_KEY"],
    config=Config(retries={"max_attempts": 5, "mode": "standard"}),
)

data = json.loads(LIST.read_text(encoding="utf-8-sig"))
root = Path(data["root"])
files = data["files"]

def exists_same(key, size):
    try:
        h = s3.head_object(Bucket=BUCKET, Key=key)
        return h["ContentLength"] == size
    except Exception:
        return False

done = skipped = failed = 0
sent_bytes = 0
total = len(files)
for i, f in enumerate(files, 1):
    rel = f["rel"]
    size = f["size"]
    key = f"{PREFIX}/{rel}"
    src = root / rel.replace("/", os.sep)
    if exists_same(key, size):
        skipped += 1
        continue
    if not src.exists():
        print(f"  ✗ missing local: {rel}", flush=True)
        failed += 1
        continue
    ct = CT.get(src.suffix.lower(), "application/octet-stream")
    try:
        s3.upload_file(str(src), BUCKET, key, ExtraArgs={"ContentType": ct})
        done += 1
        sent_bytes += size
        print(f"  [{i}/{total}] ↑ {rel}  ({size/1024/1024:.1f} MB)", flush=True)
    except Exception as e:
        failed += 1
        print(f"  ✗ {rel}: {e}", flush=True)

print(f"\nDONE — uploaded {done}, skipped {skipped}, failed {failed}; "
      f"sent {sent_bytes/1024/1024:.0f} MB of {total} files", flush=True)
sys.exit(1 if failed else 0)
