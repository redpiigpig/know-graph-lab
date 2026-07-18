#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 archive.org 某 item 的所有 PDF 鏡像到 R2（僅存檔，不轉錄、不入庫）。

  python -X utf8 scripts/mirror_archive_pdfs_to_r2.py --identifier <id> --prefix accs-english/OT

每檔：archive.org 下載 → R2 put_object(prefix/<name>) → head 確認 → 刪本地暫存。
--resume：R2 已有同 key 且大小相符就跳過。冪等，可重跑。
"""
import argparse
import os
import sys
import tempfile
from pathlib import Path
from urllib.parse import quote

import boto3
import requests
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()
ENV = os.environ
s3 = boto3.client(
    "s3", region_name="auto", endpoint_url=ENV["R2_ENDPOINT"],
    aws_access_key_id=ENV["R2_ACCESS_KEY"], aws_secret_access_key=ENV["R2_SECRET_KEY"])
BUCKET = ENV["R2_BUCKET"]
UA = {"User-Agent": "Mozilla/5.0 (KGL archive mirror)"}


def r2_size(key: str):
    try:
        return s3.head_object(Bucket=BUCKET, Key=key)["ContentLength"]
    except ClientError:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--identifier", required=True, help="archive.org item id")
    ap.add_argument("--prefix", required=True, help="R2 key 前綴，如 accs-english/OT")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--dedupe-trailing-space", action="store_true",
                    help="跳過檔名去空白後與別檔重複者（archive 偶有重覆檔）")
    ap.add_argument("--name-contains", default="",
                    help="僅鏡像檔名含此子字串的 PDF（大雜燴 item 精準挑檔用）")
    args = ap.parse_args()

    # 大 item 的 /metadata 可能數 MB 且偶爾截斷 → 用 /metadata/{id}/files 專取檔案清單
    fr = requests.get(f"https://archive.org/metadata/{args.identifier}/files",
                      headers=UA, timeout=180)
    fr.raise_for_status()
    raw = fr.json()
    flist = raw.get("result", raw) if isinstance(raw, dict) else raw
    if isinstance(flist, dict):
        flist = flist.get("files", [])
    files = [f for f in flist
             if str(f.get("name", "")).lower().endswith(".pdf")
             and (not args.name_contains or args.name_contains in f.get("name", ""))]
    if not files:
        sys.exit("no matching PDF files in item")

    seen_norm = set()
    uploaded, skipped = 0, 0
    for f in sorted(files, key=lambda x: -int(x.get("size", 0))):  # 大檔優先（去重時留大的）
        name = f["name"]
        size = int(f.get("size", 0))
        norm = name.replace(" ", "").lower()
        if args.dedupe_trailing_space and norm in seen_norm:
            print(f"  ~ 跳過重覆檔 {name}", flush=True)
            continue
        seen_norm.add(norm)
        key = f"{args.prefix}/{name}"
        if args.resume and r2_size(key) == size:
            print(f"  = 已在 R2，跳過 {name}", flush=True)
            skipped += 1
            continue
        url = f"https://archive.org/download/{args.identifier}/{quote(name)}"
        print(f"  ↓ {name} ({size//1024//1024}MB) …", end="", flush=True)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp_path = Path(tmp.name)
        try:
            with requests.get(url, headers=UA, stream=True, timeout=300) as r:
                r.raise_for_status()
                with open(tmp_path, "wb") as out:
                    for chunk in r.iter_content(1 << 20):
                        out.write(chunk)
            s3.put_object(Bucket=BUCKET, Key=key, Body=tmp_path.read_bytes(),
                          ContentType="application/pdf")
            if r2_size(key) != tmp_path.stat().st_size:
                raise RuntimeError("R2 size mismatch after upload")
            print(f" ✓ R2 ← {key}", flush=True)
            uploaded += 1
        finally:
            tmp_path.unlink(missing_ok=True)
    print(f"\n完成：上傳 {uploaded}，跳過 {skipped}，item={args.identifier} → {args.prefix}")


if __name__ == "__main__":
    main()
