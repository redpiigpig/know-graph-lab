#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""逐「段」補譯 translation_fix scan 抓到的未譯／拒答段（JSONL 語料：教父、一般譯書）。2026-09-27。

為什麼另寫一支：`fathers_retranslate_untranslated.py` 是 chunk 層級（整個 chunk 的中文欄
都是英文才補），抓不到「chunk 裡其他段都譯好了、只有幾條編者註腳還是英文」這種情形。
2026-09-27 全站複查：教父語料有 960 段這種註腳，例如「(1041) Seest thou how he …」。
依註釋政策，敘述性的註要譯成繁中，純書目式的註（書名‧卷‧頁、經文出處）原樣保留。

做法：讀 scan 產生的 `*.clear.jsonl`，按書分組；每段先核對現值還是當初掃到的那段
（不是就跳過，避免蓋掉別人剛改的），純出處註略過，其餘每批最多 6 段、以 ⟦n⟧ 標記
一起送引擎（Gemini→NVIDIA→Haiku），逐段過 `unusable_reason` 關卡、註號要原樣保留，
合格才寫回；每本書寫完留一次 `.jsonl.bak_paras` 備份並推 R2。可重跑（已是中文的段自動略過）。

  python -X utf8 scripts/retranslate_flagged_paras.py --clear output/translation_fix/scan-XXXX-all.clear.jsonl --dry-run
  python -X utf8 scripts/retranslate_flagged_paras.py --clear ... --corpus fathers --apply
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

CHUNKS = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\_chunks")
HAN = re.compile(r"[\u4e00-\u9fff]")
WORD = re.compile(r"[A-Za-z]{3,}")
NOTE_NO = re.compile(r"^\s*(\(\d+\)|\[\^?\d+\]|\d+\.)\s*")
MARK = re.compile(r"⟦(\d+)⟧")
BATCH_N, BATCH_CHARS = 6, 3000

PROMPT = """你是{role}的專業譯者。下面有若干段編號為 ⟦1⟧ ⟦2⟧… 的英文段落（多半是編者註腳），逐段翻成**繁體中文**。

規則：
1. 每段開頭寫回同一個編號標記 ⟦n⟧，段數與順序不可增減，只輸出譯文，不要前言或說明。看不懂也照譯。
2. 註號（如「(1041)」「[^12]」）原樣保留在段首。
3. 書目與出處（作者、書名、卷、頁、版本、經文章節如 1 Thess. ii. 14）**原樣保留不譯**；敘述、論證、評語要譯。
4. 希臘文、拉丁文原詞原樣保留；人名地名依慣用譯名（{names}）。
5. 中間點用「‧」；嚴守繁體。
6. 聖經經文依和合本語體。

{body}"""

ROLES = {
    "fathers": ("教父學（Schaff 編《尼西亞前後教父全集》）",
                "Justin Martyr→猶斯定、Irenaeus→愛任紐、Clement of Alexandria→亞歷山卓的革利免、Tertullian→特土良、"
                "Origen→俄利根、Hermas→黑馬、Tatian→塔提安、Athenagoras→雅典那哥拉、Theophilus→提阿非羅、"
                "Cyprian→居普良、Hippolytus→希波呂圖、Athanasius→亞他那修、Basil→巴西流、Chrysostom→金口若望、"
                "Jerome→耶柔米、Augustine→奧古斯丁、Eusebius→優西比烏、Paul→保羅、Peter→彼得、Moses→摩西；"
                "其他教父與學者名若無把握，保留原文拼法"),
    "books": ("宗教學與人文學術書", "依書中通行譯名，無把握時保留原文"),
}


def is_citation_only(text: str) -> bool:
    """純出處註：去掉註號後英文字不到 8 個（如「(1049) Morel.」「(2175) John xx. 29.」）。"""
    body = NOTE_NO.sub("", text)
    return len(WORD.findall(body)) < 8


def split_marked(out: str, n: int) -> list[str] | None:
    parts = MARK.split(out.strip())
    if len(parts) != 2 * n + 1:
        return None
    if [int(x) for x in parts[1::2]] != list(range(1, n + 1)):
        return None
    return [p.strip() for p in parts[2::2]]


def piece_ok(src: str, zh: str, te) -> str:
    if len(HAN.findall(zh)) < 4:
        return "no-chinese"
    why = te.unusable_reason(zh, src)
    if why:
        return why
    m = NOTE_NO.match(src)
    if m and not zh.lstrip().startswith(m.group(1)):
        return "note-number-lost"
    return ""


def translate_batch(items: list[str], corpus: str, te) -> list[str | None]:
    role, names = ROLES[corpus]
    body = "\n\n".join(f"⟦{i + 1}⟧\n{t}" for i, t in enumerate(items))
    te.PROMPT_TMPL = PROMPT.replace("{role}", role).replace("{names}", names).replace("{body}", "{source}")
    try:
        out = te.gemini_with_nvidia_fallback(body)
    except Exception as e:  # noqa: BLE001  引擎鏈全數失敗（含 Haiku 關卡 raise）
        print(f"    ! 引擎失敗：{str(e)[:100]}", flush=True)
        return [None] * len(items)
    pieces = split_marked(out or "", len(items))
    if pieces is None:
        if len(items) == 1:
            pieces = [MARK.sub("", out or "").strip()]
        else:
            print(f"    · 標記對不上 → 拆單段", flush=True)
            return [translate_batch([t], corpus, te)[0] for t in items]
    res = []
    for src, zh in zip(items, pieces):
        why = piece_ok(src, zh, te)
        if why:
            print(f"    ✗ 關卡 {why}：{zh[:40]!r}", flush=True)
            res.append(None)
        else:
            res.append(zh)
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--clear", required=True)
    ap.add_argument("--corpus", default="fathers,books")
    ap.add_argument("--reasons", default="untranslated,meta")
    ap.add_argument("--ids", nargs="*")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    corpora = set(a.corpus.split(","))
    reasons = set(a.reasons.split(","))
    recs = [json.loads(l) for l in open(a.clear, encoding="utf-8") if l.strip()]
    recs = [r for r in recs if r["corpus"] in corpora and r["reason"] in reasons
            and (not a.ids or r["id"] in a.ids)]
    by_book = collections.defaultdict(list)
    for r in recs:
        by_book[(r["corpus"], r["id"])].append(r)
    te = None
    if a.apply:
        import translate_ebook_to_zh as te  # noqa: E402
        import standardize_ebook as se  # noqa: E402
    stat = collections.Counter()
    for (corpus, bid), rs in sorted(by_book.items(), key=lambda kv: len(kv[1])):
        p = CHUNKS / f"{bid}.jsonl"
        if not p.exists():
            stat["no-file"] += len(rs)
            continue
        chunks = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
        by_ci = {c.get("chunk_index"): c for c in chunks}
        todo = []  # (chunk, para_index, source_text)
        for r in rs:
            c = by_ci.get(r["chunk_index"])
            if c is None:
                stat["gone"] += 1
                continue
            paras = (c.get("content") or "").split("\n\n")
            j = r["para"]
            cur = paras[j] if j < len(paras) else ""
            if not cur.strip() or not cur.strip().startswith((r.get("zh_excerpt") or "")[:30].strip()):
                stat["changed-since-scan"] += 1
                continue
            if r["reason"] == "untranslated":
                src = cur
            else:  # meta：譯文是拒答，要拿對齊的原文段
                src = (r.get("src_excerpt") or "").strip()
                sp = ((c.get("sources") or {}).get("en") or c.get("source_text") or "").split("\n\n")
                if len(sp) == len(paras) and sp[j].strip():
                    src = sp[j]
                elif not src or len(src) < 20:
                    stat["meta-no-source"] += 1
                    continue
            if len(HAN.findall(cur)) > 0.3 * len(cur) and r["reason"] == "untranslated":
                stat["already-chinese"] += 1
                continue
            if r["reason"] == "untranslated" and is_citation_only(src):
                stat["citation-kept"] += 1
                continue
            todo.append((c, j, src))
        stat["todo"] += len(todo)
        print(f"[{corpus}] {bid} 標記 {len(rs)}、待譯 {len(todo)}", flush=True)
        if not a.apply or not todo:
            continue
        batches, cur_b, cur_len = [], [], 0
        for t in todo:
            if cur_b and (cur_len + len(t[2]) > BATCH_CHARS or len(cur_b) >= BATCH_N):
                batches.append(cur_b)
                cur_b, cur_len = [], 0
            cur_b.append(t)
            cur_len += len(t[2])
        if cur_b:
            batches.append(cur_b)
        done = 0
        for b in batches:
            outs = translate_batch([t[2] for t in b], corpus, te)
            for (c, j, _), zh in zip(b, outs):
                if zh is None:
                    stat["failed"] += 1
                    continue
                paras = c["content"].split("\n\n")
                paras[j] = zh
                c["content"] = "\n\n".join(paras)
                done += 1
        stat["translated"] += done
        if done:
            bak = p.with_suffix(".jsonl.bak_paras")
            if not bak.exists():
                shutil.copy2(p, bak)
            tmp = p.with_suffix(".jsonl.tmp")
            tmp.write_text("\n".join(json.dumps(c, ensure_ascii=False) for c in chunks) + "\n", encoding="utf-8")
            tmp.replace(p)
            se.push_to_r2(bid, p)
            print(f"  ✓ 寫回 {done} 段並推 R2", flush=True)
    print("SUMMARY", dict(stat), flush=True)
    print("RETRANS_PARAS_DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
