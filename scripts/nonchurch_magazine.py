# -*- coding: utf-8 -*-
"""《無境界者》雜誌收錄 pipeline。

進「無教會主義研究資料」collection。這本是使用者自己在辦的線上雜誌，
2024 年創刊、雙數月發刊，主張「不以教會為本位的自由信仰論述平台」——
台灣無教會運動當代這一端最直接的一手語料，與廖本恩那本 1911–2011 的
百年運動史接續。

原稿是逐篇 .docx，依期別資料夾歸檔（`01-第一期/1-6縱貫一世紀的無教會史.docx`），
檔名前綴就是期別與篇序，不必解析內文即可歸期。目次、投稿資訊、編輯資訊這類
非文章的頁面照收但標成 front-matter，語料層可據以排除。

Drive canonical：G:\\…\\資料\\無境界者\\雜誌\\（原地不動，本流程只讀）
R2：mukyokai-fulltext/nonchurch/<期>-<序>-<篇名>.txt
index：public/content/research-data/mukyokai/nonchurch-index.json

  python -X utf8 scripts/nonchurch_magazine.py --process [--limit N]
  python -X utf8 scripts/nonchurch_magazine.py --publish
"""
import argparse
import glob
import hashlib
import html
import json
import os
import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dadaodao_fulltext as df  # noqa: E402

ROOT = Path(r"G:\我的雲端硬碟\資料\無境界者\雜誌")
R2_TXT = "mukyokai-fulltext/nonchurch"
INDEX_OUT = Path(__file__).resolve().parents[1] / "public/content/research-data/mukyokai/nonchurch-index.json"
MIN_CHARS = 200

# 目次／投稿資訊／編輯資訊不是文章，但仍收錄——它們記著每期主題與編輯方針
FRONT_MATTER = ("目次", "投稿資訊", "編輯資訊", "本期作者簡介")


def docx_text(path: Path) -> str:
    xml = zipfile.ZipFile(path).read("word/document.xml").decode("utf-8", "replace")
    txt = html.unescape(re.sub(r"<[^>]+>", "", re.sub(r"</w:p>", "\n", xml)))
    return re.sub(r"\n{3,}", "\n\n", txt).strip()


def parse_name(rel: str):
    """`01-第一期/1-6縱貫一世紀的無教會史.docx` → (1, 6, '縱貫一世紀的無教會史')。"""
    folder, name = rel.split(os.sep, 1) if os.sep in rel else ("", rel)
    issue = int(m.group(1)) if (m := re.match(r"(\d+)-", folder)) else 0
    stem = re.sub(r"\.docx$", "", name, flags=re.I)
    m2 = re.match(r"(\d+)-(\d+)\s*(.*)$", stem)
    if m2:
        return issue or int(m2.group(1)), int(m2.group(2)), m2.group(3).strip() or stem
    return issue, 0, stem


def slug_for(issue, seq, title):
    safe = re.sub(r'[\\/:*?"<>|\s]+', "-", title)[:48].strip("-")
    return f"{issue:02d}-{seq:02d}-{safe}-{hashlib.sha1(title.encode()).hexdigest()[:6]}"


def files():
    for p in sorted(glob.glob(str(ROOT / "**" / "*.docx"), recursive=True)):
        if "_已刪除孤兒檔" in p:
            continue
        yield Path(p), os.path.relpath(p, ROOT)


def process(limit=0):
    have = df.r2_existing_keys(R2_TXT)
    rows = []
    if INDEX_OUT.exists():
        rows = json.loads(INDEX_OUT.read_text(encoding="utf-8"))
    known = {r["textKey"]: r for r in rows}
    done = skip = fail = 0
    for path, rel in files():
        issue, seq, title = parse_name(rel)
        key = f"{R2_TXT}/{slug_for(issue, seq, title)}.txt"
        if key in have and key in known:
            skip += 1
            continue
        try:
            text = docx_text(path)
        except Exception as e:  # noqa: BLE001
            fail += 1
            print(f"  ! {rel}: {type(e).__name__}", flush=True)
            continue
        if len(text) < MIN_CHARS:
            skip += 1
            continue
        df.r2_put_text(key, text)
        known[key] = {
            "issue": issue, "seq": seq, "title": title,
            "kind": "front" if any(k in title for k in FRONT_MATTER) else "article",
            "chars": len(text), "textKey": key, "file": rel,
        }
        done += 1
        if limit and done >= limit:
            break
    out = sorted(known.values(), key=lambda r: (-r["issue"], r["seq"]))
    INDEX_OUT.parent.mkdir(parents=True, exist_ok=True)
    INDEX_OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    arts = sum(1 for r in out if r["kind"] == "article")
    print(f"新增 {done}、既有 {skip}、失敗 {fail}；索引 {len(out)} 篇（正文 {arts}）")


def publish():
    rows = json.loads(INDEX_OUT.read_text(encoding="utf-8"))
    issues = sorted({r["issue"] for r in rows})
    print(f"{len(issues)} 期 / {len(rows)} 篇 "
          f"（正文 {sum(1 for r in rows if r['kind'] == 'article')}）→ {INDEX_OUT}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--process", action="store_true")
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    if args.process:
        process(args.limit)
    if args.publish:
        publish()
    if not (args.process or args.publish):
        ap.print_help()


if __name__ == "__main__":
    main()
