"""唯讀稽核：原文與譯文長度比例異常（捏造擴寫／漏譯截斷）。2026-09-27。

英文→中文正常比例約 0.4–0.9 字／字元（中文字數 ÷ 英文字元數）。
- 捏造：原文 < 120 字元（章名、短標籤）但譯文 > 300 字，或比例 > 2.0 且譯文 > 600 字
- 截斷：原文 > 800 字元但比例 < 0.12（譯文只剩一小截）
只看拉丁字母為主的原文（日文、中文原文比例不同，另判）。
"""
import json, re, sys, glob, pathlib, collections

CHUNKS = pathlib.Path(r"G:\我的雲端硬碟\資料\知識圖工作室\_chunks")
CW = pathlib.Path(".claude/skills/ebook-collected-works")
HAN = re.compile(r"[\u4e00-\u9fff]")
LAT = re.compile(r"[A-Za-z]")
out = []
stat = collections.Counter()


def judge(en, zh):
    en, zh = (en or "").strip(), (zh or "").strip()
    if not en or not zh:
        return None
    lat = len(LAT.findall(en))
    if lat < 0.5 * len(en):          # 非拉丁字母原文（日文、中文、希臘文…）不判
        return None
    han = len(HAN.findall(zh))
    if han < 10:
        return None                   # 未譯段歸 translation_fix 管
    r = han / max(1, len(en))
    if len(en) < 120 and han > 300:
        return f"捏造?(原文{len(en)}字元→譯文{han}字)"
    if r > 2.0 and han > 600:
        return f"擴寫?(比例{r:.2f})"
    if len(en) > 800 and r < 0.12:
        return f"截斷?(比例{r:.2f}，原文{len(en)}→譯文{han})"
    return None


def emit(src, key, en, zh):
    stat[src] += 1
    why = judge(en, zh)
    if why:
        out.append((src, key, why, en[:100].replace("\n", " "), zh[:100].replace("\n", " ")))

# 1) Drive JSONL（一般譯書 source_text、教父 sources.en）
files = sorted(CHUNKS.glob("*.jsonl"))
for n, p in enumerate(files):
    try:
        for line in p.open(encoding="utf-8"):
            if '"source_text"' not in line and '"sources"' not in line:
                continue
            c = json.loads(line)
            en = c.get("source_text") or (c.get("sources") or {}).get("en") or ""
            if en and not c.get("zh_only"):
                emit("jsonl", f"{p.stem}#{c.get('chunk_index')}", en, c.get("content") or "")
    except Exception as e:  # noqa: BLE001
        print("ERR", p.name, type(e).__name__, file=sys.stderr)
    if n % 1000 == 0:
        print(f"jsonl {n}/{len(files)}", flush=True)

# 2) 全集／東方聖書 sec*.json
for p in sorted(CW.glob("*_data/*/sec*.json")):
    try:
        s = json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        continue
    en, zh = s.get("en") or s.get("src") or [], s.get("zh") or []   # 潘尼卡等 driver 用 src 鍵
    for j in range(min(len(en), len(zh))):
        emit("sec", f"{p.parent.name}/{p.name}#{j}", en[j] or "", zh[j] or "")
    if s.get("heading") and s.get("title_zh"):                        # 章名被擴寫成內文
        emit("sec", f"{p.parent.name}/{p.name}#title", s["heading"], s["title_zh"])

# 3) 研究回顧在 DB（lit_review_sections orig↔zh），另跑 output/translation_fix/ratio_litreview.py

rep = pathlib.Path("output/translation_fix/ratio_audit.tsv")
rep.write_text("\n".join("\t".join(map(str, r)) for r in out) + "\n", encoding="utf-8")
print("分母", dict(stat))
print("命中", collections.Counter((r[0], r[2].split("?")[0]) for r in out))
