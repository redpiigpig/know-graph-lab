#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""把英文原著併進既有中譯本的來源欄，讓那一卷從單欄變成中英對照。

緣起（2026-09-11）：泰勒《原始文化（英繁對照）》與弗雷澤《金枝（英繁對照）》站上
都已經有完整中譯（683／650 段），可是 `source_text` 全空——**標題寫著「英繁對照」，
實際上只有中文**。而同一天從 archive.org 抓回了兩部的英文原著全文，正好補得上。

不能直接新增一筆英文版了事：站上會出現兩個《原始文化》兩個《金枝》，讀者分不出
哪個是哪個。正解是把英文塞進既有那一筆的來源欄。

## 對齊策略（[[ebook-collected-works]] §B1-3 的第一級：章節錨點）

中譯側每一段的 `chapter_path` 形如 `原始文化 · 卷一 · CHAPTER III.`。
🚨 那個欄位有雜訊——腳註文字（`Niebuhr, 'Römische Geschichte,' part i. p. 88`）
也被當成章名，658 段裡有 141 個不同值。所以**不能逐段解析章名，要「帶著走」**：
每一段沿用最後看到的有效 `CHAPTER N` 標記。實測這樣 658 段全部分到 19 章、零未分配。

英文側從純文字切：`^CHAPTER [IVXL]+\.?$` 單獨成行。🚨 前半是目錄後半才是正文，
要取**編號重新從 I（或卷二的 XII）開始的那一輪**。

章對上之後，章內按**累計字數比例**把英文段落分給中譯的各段。這是 §B1-3 的第二級，
不是精確對齊——所以本腳本會逐章報覆蓋率，對不上的章寧可留白也不硬塞。

## 全文正本在哪裡

🚨 不是 DB。DB 的 `content` 只有 200 字 preview（[[feedback_ocr_truncation_jsonl_source]]）。
正本是 `_chunks/{id}.jsonl`，Drive 為 canonical、R2 為後備。
這兩本的 **Drive 副本已經不見了，只剩 R2**——所以本腳本從 R2 取、寫回 Drive 與 R2 兩邊，
順便把 canonical 補回去。

  python scripts/merge_original_column.py --book tylor            # 預演
  python scripts/merge_original_column.py --book tylor --apply
"""
from __future__ import annotations

import argparse
import gzip
import io
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDIO = Path(r"G:\我的雲端硬碟\資料\知識圖工作室")
CHUNKS = STUDIO / "_chunks"

JOBS = {
    "tylor": {
        "ebook_id": "80000000-0000-4000-8000-000000000012",
        "label": "泰勒《原始文化（英繁對照）》",
        # (中譯側的卷字, 英文原文檔, 該卷第一章的羅馬數字)
        "volumes": [
            ("一", STUDIO / "全集" / "宗教學" / "泰勒" /
             "Edward B. Tylor，Primitive Culture Vol.1 (1871).txt", "I"),
            ("二", STUDIO / "全集" / "宗教學" / "泰勒" /
             "Edward B. Tylor，Primitive Culture Vol.2 (4th ed.).txt", "XII"),
        ],
        "vol_re": r"卷([一二])\s*·\s*CHAPTER\s+([IVXL]+)",
        # 🚨 OCR 把卷一的 `CHAPTER V.` 那一行吃掉了，正文從 IV 直接跳到 VI。
        # 靠書眉定位補回來：第五章標題是 EMOTIONAL AND IMITATIVE LANGUAGE，
        # 在行 6110 第一次出現（其後兩行是該章章旨）。
        # 格式 {(卷, 章): 起始行號}——行號是 0-based，取標題行前一行。
        "manual_starts": {("一", "V"): 6108},
    },
}

CH_LINE = re.compile(r"^\s*CHAPTER\s+([IVXL]+)\.?\s*$")


def english_chapters(path: Path, first: str,
                     manual: dict | None = None, vol: str = "") -> dict[str, str]:
    """純文字 → {羅馬數字: 該章全文}。只取正文那一輪，不取目錄。

    manual 是人工補的章首行號——OCR 偶爾會把 `CHAPTER N.` 那一行吃掉，
    自動切就會把兩章併成一章而毫無徵兆。"""
    lines = path.read_text(encoding="utf-8").splitlines()
    marks = [(i, m.group(1)) for i, l in enumerate(lines) if (m := CH_LINE.match(l))]
    if not marks:
        return {}
    # 正文起點＝最後一次出現 first 的位置（前面那些是目錄）
    starts = [k for k, (_, num) in enumerate(marks) if num == first]
    body = marks[starts[-1]:] if starts else marks
    for (v, num), ln in (manual or {}).items():
        if v == vol:
            body.append((ln, num))
    body.sort()
    out = {}
    for k, (ln, num) in enumerate(body):
        end = body[k + 1][0] if k + 1 < len(body) else len(lines)
        out[num] = "\n".join(lines[ln:end]).strip()
    return out



# 每頁重複的書眉。它們不是內容，卻會被當成獨立段落，把英文側的段數撐大而造成漂移。
# 🚨 腳註不刪——使用者定調註釋一律要收（[[feedback_transcribe_notes_and_bibliography]]），
# 它們雖然也會干擾對齊，但那是可接受的代價，刪掉則是不可回復的損失。
RUNNING_HEAD = re.compile(r"^[A-Z][A-Z \.,'\-—()]{4,60}\.?$")


def strip_running_heads(text: str, title_words: set[str]) -> str:
    """刪掉與章名重疊的全大寫單行（書眉）。只刪重複出現三次以上的，避免誤殺小標。"""
    lines = text.splitlines()
    counts = {}
    for l in lines:
        t = l.strip()
        if RUNNING_HEAD.match(t):
            counts[t] = counts.get(t, 0) + 1
    heads = {t for t, n in counts.items()
             if n >= 3 and (title_words & set(re.findall(r"[A-Z]{3,}", t)))}
    if not heads:
        heads = {t for t, n in counts.items() if n >= 5}
    return "\n".join(l for l in lines if l.strip() not in heads)


def split_paras(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def distribute(paras: list[str], weights: list[int]) -> list[str]:
    """按累計字數比例把段落分給 n 個目標格。回傳長度＝len(weights) 的字串串列。"""
    if not paras or not weights:
        return ["" for _ in weights]
    total_w = sum(weights) or 1
    total_p = sum(len(p) for p in paras) or 1
    out, i, acc_w = [], 0, 0
    for w in weights:
        acc_w += w
        target = total_p * acc_w / total_w
        got, acc_p = [], sum(len(p) for p in paras[:i])
        while i < len(paras) and (acc_p < target or not got):
            got.append(paras[i])
            acc_p += len(paras[i])
            i += 1
        out.append("\n\n".join(got))
    if i < len(paras) and out:                       # 尾巴全掛最後一格
        out[-1] = (out[-1] + "\n\n" + "\n\n".join(paras[i:])).strip()
    return out


def env() -> dict:
    out = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip().strip("\"'")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", required=True, choices=sorted(JOBS))
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    job = JOBS[a.book]
    E = env()

    import boto3
    c = boto3.client("s3", region_name="auto", endpoint_url=E["R2_ENDPOINT"],
                     aws_access_key_id=E["R2_ACCESS_KEY"], aws_secret_access_key=E["R2_SECRET_KEY"])
    key = f"ebook-chunks/{job['ebook_id']}.jsonl.gz"
    raw = c.get_object(Bucket=E["R2_BUCKET"], Key=key)["Body"].read()
    rows = [json.loads(l) for l in gzip.decompress(raw).decode("utf-8").splitlines() if l.strip()]
    print(f"{job['label']}：從 R2 取得 {len(rows)} 段")

    # 🚨 動手之前先確認這本**真的**沒有原文欄。
    #
    # 2026-09-11 我在這裡做錯過一次：查 DB 的 ebook_chunks 看到 source_text 是空的，
    # 就判定「這本有中譯沒原文」，用章級比例分配把英文塞進去，蓋掉了 675 段**原本
    # 就逐段對齊好的**英文。**DB 從來不存 source_text**——它只存 content 的 200 字
    # preview，正本一律在 _chunks/{id}.jsonl。
    # 所幸多語 schema 把各語言另存在 sources[lang]，原文完好才救得回來。
    has = sum(1 for r in rows if (r.get("source_text") or "").strip()
              or (r.get("sources") or {}))
    if has:
        print(f"  ⛔ 這本已經有原文欄（{has}/{len(rows)} 段），不覆蓋。")
        print("     要重做對齊請先確認現有的哪裡不好，並備份 sources 欄。")
        raise SystemExit(1)

    # 中譯側：帶著走分章
    vr = re.compile(job["vol_re"])
    cur = None
    for r in rows:
        m = vr.search(r.get("chapter_path") or "")
        if m:
            cur = (m.group(1), m.group(2))
        r["_ch"] = cur
    unassigned = sum(1 for r in rows if not r["_ch"])
    print(f"  帶著走分章：未分配 {unassigned} 段")

    # 英文側
    eng: dict[tuple, str] = {}
    for vol, path, first in job["volumes"]:
        if not path.exists():
            print(f"  ✗ 英文原文不在：{path}")
            continue
        chs = english_chapters(path, first, job.get("manual_starts", {}), vol)
        print(f"  英文卷{vol}：正文 {len(chs)} 章 {sorted(chs, key=len)[:14]}")
        for num, txt in chs.items():
            eng[(vol, num)] = txt

    # 逐章分配
    groups: dict[tuple, list] = {}
    for r in rows:
        if r["_ch"]:
            groups.setdefault(r["_ch"], []).append(r)

    filled = blank = 0
    for ch, members in sorted(groups.items()):
        src = eng.get(ch)
        if not src:
            blank += len(members)
            print(f"    ⚠ 卷{ch[0]} CHAPTER {ch[1]:5s} {len(members):3d} 段 → 英文缺這一章，留白")
            continue
        # 章名的大寫詞拿來認書眉
        head_words = set(re.findall(r"[A-Z]{3,}", src[:400]))
        paras = split_paras(strip_running_heads(src, head_words))
        weights = [len(m.get("content") or "") or 1 for m in members]
        parts = distribute(paras, weights)
        for m, p in zip(members, parts):
            m["source_text"] = p
            m["source_lang"] = "en"
        filled += len(members)
        print(f"    ✓ 卷{ch[0]} CHAPTER {ch[1]:5s} {len(members):3d} 段 ← 英文 {len(paras):4d} 段")

    for r in rows:
        r.pop("_ch", None)
    print(f"\n  補上英文 {filled} 段／留白 {blank} 段（覆蓋率 {filled/len(rows)*100:.1f}%）")

    if not a.apply:
        print("（預演，加 --apply 才寫回 Drive 與 R2）")
        return

    CHUNKS.mkdir(parents=True, exist_ok=True)
    out_path = CHUNKS / f"{job['ebook_id']}.jsonl"
    out_path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
                        encoding="utf-8")
    print(f"  寫回 Drive：{out_path}")

    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
        gz.write(("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n").encode("utf-8"))
    c.put_object(Bucket=E["R2_BUCKET"], Key=key, Body=buf.getvalue())
    print(f"  推回 R2：{key}（{len(buf.getvalue())/1e6:.2f} MB）")


if __name__ == "__main__":
    main()
