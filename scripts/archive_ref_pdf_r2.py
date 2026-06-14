#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""研究回顧用過的 PDF → 上傳 R2 保留連結，再刪本地（使用者政策）。

- 上傳到 R2 key `dadaodao-materials/研究回顧/<檔名>`（沿用既有簽名下載前綴，
  server/api/works/material.get.ts 可下載）。
- 把該 lit_review_entries 的 fulltext_url 設成簽名下載路徑 `/api/works/material?key=…`
  （「保留連結」，原始 PDF 仍可取得）。
- --delete：上傳成功後刪本地 PDF。

  python -X utf8 scripts/archive_ref_pdf_r2.py --pdf "<x.pdf>" --ref <ref_key> [--delete]
"""
import argparse
import os
import sys
from pathlib import Path
from urllib.parse import quote

import boto3
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv()
SLUG = "mahaprajapati-revolution"
PREFIX = "dadaodao-materials/研究回顧"

# R2 client (same env as dadaodao pipeline)
ENV = os.environ
s3 = boto3.client(
    "s3", region_name="auto", endpoint_url=ENV["R2_ENDPOINT"],
    aws_access_key_id=ENV["R2_ACCESS_KEY"], aws_secret_access_key=ENV["R2_SECRET_KEY"])
BUCKET = ENV["R2_BUCKET"]
U = ENV["SUPABASE_URL"]
K = ENV["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": K, "Authorization": f"Bearer {K}", "Content-Type": "application/json"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--delete", action="store_true")
    args = ap.parse_args()

    pdf = Path(args.pdf)
    if not pdf.exists():
        sys.exit(f"no such file: {pdf}")
    key = f"{PREFIX}/{pdf.name}"
    s3.put_object(Bucket=BUCKET, Key=key, Body=pdf.read_bytes(),
                  ContentType="application/pdf")
    # head to confirm
    s3.head_object(Bucket=BUCKET, Key=key)
    link = f"/api/works/material?key={quote(key)}"
    r = requests.patch(f"{U}/rest/v1/lit_review_entries?project_slug=eq.{SLUG}&ref_key=eq.{args.ref}",
                       headers={**H, "Prefer": "return=minimal"},
                       data=f'{{"fulltext_url": "{link}"}}'.encode("utf-8"), timeout=30)
    if r.status_code not in (200, 204):
        sys.exit(f"patch error {r.status_code}: {r.text[:200]}")
    print(f"✓ R2 ← {key}  ({pdf.stat().st_size} bytes); fulltext_url set for {args.ref}")
    if args.delete:
        pdf.unlink()
        print(f"  🗑 deleted local {pdf.name}")


if __name__ == "__main__":
    main()
