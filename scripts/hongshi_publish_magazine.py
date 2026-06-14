# -*- coding: utf-8 -*-
"""把已下載的弘誓雙月刊 PDF 搬到 canonical Drive + 上傳 R2 + 建 index.json。

來源：C:/tmp/hongshi_dl/magazine/弘誓雙月刊-NNN[-pK].pdf（hongshi_download_magazine.mjs 產出）
canonical：G:\\我的雲端硬碟\\公事\\印順學派與弘誓研究資料\\弘誓雙月刊\\
R2：yinshun-hongshi/弘誓雙月刊/<檔名>（bucket 私有，仿 dadaodao 簽名下載）
index：public/content/research-data/yinshun-hongshi/magazine-index.json

冪等：R2 已存在（同 size）跳過。
  python -X utf8 scripts/hongshi_publish_magazine.py
"""
import json
import re
import shutil
from pathlib import Path

import boto3

ROOT = Path(__file__).resolve().parents[1]
ENV = {}
for _l in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if _l and not _l.startswith("#") and "=" in _l:
        _k, _v = _l.split("=", 1)
        ENV[_k.strip()] = _v.strip().strip('"').strip("'")

STAGE = Path(r"C:/tmp/hongshi_dl/magazine")
DRIVE = Path(r"G:\我的雲端硬碟\公事\印順學派與弘誓研究資料\弘誓雙月刊")
HARVEST = Path(r"C:/tmp/hongshi_magazine_index.json")
R2_PREFIX = "yinshun-hongshi/弘誓雙月刊"
INDEX_OUT = ROOT / "public/content/research-data/yinshun-hongshi/magazine-index.json"

s3 = boto3.client("s3", region_name="auto", endpoint_url=ENV["R2_ENDPOINT"],
                  aws_access_key_id=ENV["R2_ACCESS_KEY"], aws_secret_access_key=ENV["R2_SECRET_KEY"])
B = ENV["R2_BUCKET"]


def r2_size(key):
    try:
        return s3.head_object(Bucket=B, Key=key)["ContentLength"]
    except Exception:
        return None


def main():
    meta = {x["issue"]: x for x in json.loads(HARVEST.read_text(encoding="utf-8"))}
    DRIVE.mkdir(parents=True, exist_ok=True)
    issues = {}
    up = skip = 0
    for pdf in sorted(STAGE.glob("*.pdf")):
        m = re.match(r"弘誓雙月刊-(\d+)(?:-p(\d))?\.pdf", pdf.name)
        if not m:
            continue
        issue = int(m.group(1))
        part = int(m.group(2)) if m.group(2) else 1
        # canonical copy to Drive
        dst = DRIVE / pdf.name
        if not dst.exists() or dst.stat().st_size != pdf.stat().st_size:
            shutil.copy2(pdf, dst)
        # upload R2
        key = f"{R2_PREFIX}/{pdf.name}"
        sz = pdf.stat().st_size
        if r2_size(key) == sz:
            skip += 1
        else:
            s3.upload_file(str(pdf), B, key, ExtraArgs={"ContentType": "application/pdf"})
            up += 1
            print(f"  ↑ {pdf.name} {sz/1024/1024:.1f}MB", flush=True)
        e = issues.setdefault(issue, {
            "issue": issue,
            "date": (meta.get(issue) or {}).get("date", ""),
            "title": (meta.get(issue) or {}).get("title", "").strip(),
            "parts": [],
        })
        e["parts"].append({"part": part, "key": key, "size": sz})

    out = sorted(issues.values(), key=lambda x: -x["issue"])
    for e in out:
        e["parts"].sort(key=lambda p: p["part"])
    INDEX_OUT.parent.mkdir(parents=True, exist_ok=True)
    INDEX_OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nuploaded {up}, skipped {skip}; {len(out)} issues → {INDEX_OUT.relative_to(ROOT)}", flush=True)


if __name__ == "__main__":
    main()
