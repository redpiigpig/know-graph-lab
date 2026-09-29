#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""已有中譯本的外文書 → 「一章一頁、章 ##／節 ###、逐段對照、段號 章-節-段」。

align_reference.py 的舊做法是「中文一節一塊、英文五頁一塊」再讓閱讀器按段落序號硬配，
英文那塊還是整片 OCR（書眉、斷字連字號、沒有段落），結果整本錯位（2026-09-29 民主妙法被使用者點名）。
這支改成：
  1. 英文逐頁 OCR（.jsonl.bak_chapters）清掉書眉頁碼、接回斷字、重建段落，全大寫行當節標題；
  2. 中文把各頁註釋抽出集中章末、接回被註釋切斷的段落、章節名補成 ##／###；
  3. 兩邊以「節」為硬錨點（小節數必須一致，不一致就停），節內用長度比＋數字／西文詞重疊做段落對齊；
  4. 每一對齊列兩欄都寫上同一個段號 {{s:章-節-段}}（沒有節就 章-段），閱讀器顯示成段首小灰字。

用法：
  python -X utf8 scripts/rebuild_reference_bilingual.py madsen            # 乾跑：印各章對齊摘要
  python -X utf8 scripts/rebuild_reference_bilingual.py madsen --show 2   # 印第 2 部分逐列對照
  python -X utf8 scripts/rebuild_reference_bilingual.py madsen --apply    # 寫回 JSONL＋R2＋DB（改前留 .bak_bilingual）
"""
from __future__ import annotations

import argparse
import html
import json
import math
import re
import shutil
import sys
from pathlib import Path

CHUNKS = Path("G:/我的雲端硬碟/資料/知識圖工作室/_chunks")
FOOT_RULE = "—" * 15
FOOT_RULE_RE = re.compile(r"^[—－\-]{15,}$")
PAGE_MARK_RE = re.compile(r"\{\{p:[^}]*\}\}")
REF_RE = re.compile(r"\[\^\d+\]")
EMPTY_CELL = "\u200b"          # 對不到的一側放零寬字元佔列（閱讀器 trim 不會吃掉），列數才對得齊
ZH_END = "。」』！？）)…—"


# ── 英文逐頁 OCR 清理 ──────────────────────────────────────────────────────

def is_caps_heading(line: str) -> bool:
    s = line.strip()
    letters = [ch for ch in s if ch.isalpha()]
    return (len(letters) >= 4 and len(s) < 70
            and sum(ch.isupper() for ch in letters) / len(letters) > 0.9)


SMALL_WORDS = {"a", "an", "and", "as", "at", "by", "for", "from", "in", "of", "on", "or", "the", "to"}


def title_case(s: str) -> str:
    words = s.lower().split()
    out = []
    for i, w in enumerate(words):
        if i and w in SMALL_WORDS:
            out.append(w)
        else:
            j = next((k for k, ch in enumerate(w) if ch.isalpha()), None)
            out.append(w if j is None else w[:j] + w[j].upper() + w[j + 1:])
    return " ".join(out)


def _norm_running(line: str) -> str:
    s = re.sub(r"^[\dIlOo|;:.,'’\s]+(?=[A-Z])", "", line.strip())
    return re.sub(r"[\s\d;:.,|]+$", "", s)


def strip_page_furniture(lines: list[str], running: set[str]) -> list[str]:
    """去掉頁首書眉／頁碼（前三行內）與頁尾頁碼。只在剩下的字是已知書眉時才丟，免得吃到正文。"""
    lines = [l.rstrip() for l in lines if l.strip()]
    for _ in range(3):
        if not lines:
            break
        s = lines[0].strip()
        n = _norm_running(s)
        if len(s) <= 4 or n in running or n.startswith("Notes to Pages"):
            lines.pop(0)
        else:
            break
    while lines and re.fullmatch(r"[\dIlOoxvi|.;:,'’ ]{1,6}", lines[-1].strip()):
        lines.pop()
    return lines


FN_IN_BODY = re.compile(r"(?<=[a-z.”’\")])(\d{1,2}|!)(?=\s|$)")
PARA_END = re.compile(r"[.?!”’\":)\]](\d{1,2}|!)?$")
FIGURE = re.compile(r"^(Figure|Table|Map)\s+\d+\.")


def pages_to_blocks(pages: list[tuple[int, str | None, str]], running: set[str],
                    skip_lines: set[str] = frozenset()) -> list[tuple[str, str]]:
    """[(pdf 頁, 印刷頁或 None, 該頁原文)] → [('h', 標題) | ('p', 段落)]。

    段落判準：行長明顯短於本頁中位數且以句末標點收尾 → 段落結束；跨頁照接。
    插圖說明（Figure N.）單獨成段，排在被它打斷的那一段之後。"""
    blocks: list[tuple[str, str]] = []
    cur: list[str] = []
    pending_figs: list[str] = []
    fig: list[str] | None = None
    heading: list[str] = []

    def flush_para():
        nonlocal cur
        if cur:
            blocks.append(("p", " ".join(cur).strip()))
            cur = []
        while pending_figs:
            blocks.append(("p", pending_figs.pop(0)))

    def add_line(buf: list[str], text: str):
        if buf and buf[-1].endswith("-") and text[:1].islower():
            buf[-1] = buf[-1][:-1] + text
        else:
            buf.append(text)

    for pdf_page, printed, raw in pages:
        lines = strip_page_furniture(raw.split("\n"), running)
        lines = [l for l in lines if l.strip() not in skip_lines]
        lens = sorted(len(l.strip()) for l in lines) or [60]
        median = lens[len(lens) // 2]
        marker = f"{{{{p:{printed}}}}}" if printed else ""
        first = True
        for line in lines:
            s = line.strip()
            if is_caps_heading(s) and fig is None:
                flush_para()
                heading.append(s)
                continue
            if heading:
                blocks.append(("h", title_case(" ".join(heading))))
                heading = []
            if FIGURE.match(s):
                fig = []
            target = fig if fig is not None else cur
            if first and marker:
                if target is cur and not cur:
                    s = marker + s
                elif target is cur:
                    cur.append(marker)
                else:
                    (cur.append(marker) if cur else None) if cur else None
                    if not cur:
                        s = marker + s
                first = False
            add_line(target, s)
            ends = len(s) < 0.8 * median and PARA_END.search(s)
            if fig is not None:
                if ends:
                    cap = " ".join(fig)
                    fig = None
                    if cur:
                        pending_figs.append(cap)
                    else:
                        blocks.append(("p", cap))
            elif ends:
                flush_para()
    if heading:
        blocks.append(("h", title_case(" ".join(heading))))
    flush_para()
    out = []
    for kind, text in blocks:
        text = re.sub(r"\s+", " ", text).replace(" -", "-").strip()
        text = re.sub(r"(\S)- (?=[a-z])", r"\1", text)      # 行尾斷字（跨頁或殘留）
        if kind == "p":
            text = FN_IN_BODY.sub(lambda m: f"[^{1 if m.group(1) == '!' else m.group(1)}]", text)
        if text:
            out.append((kind, text))
    return out


NOTE_START = re.compile(r"^([0-9IlOoSrZ|]{1,3})\.\s+(.*)$")
OCR_DIGIT = str.maketrans({"I": "1", "l": "1", "|": "1", "r": "1", "O": "0", "o": "0", "S": "5", "Z": "2"})


def _note_no(tok: str) -> int | None:
    t = tok.translate(OCR_DIGIT)
    return int(t) if t.isdigit() else None


def parse_notes(pages: list[tuple[int, str | None, str]], running: set[str]) -> dict[str, list[str]]:
    """書末 Notes（逐頁原文）→ {節名小寫（preface／chapter 1. …）: [第 1 條, 第 2 條…]}。

    逐行判：行首「N. 」且 N（OCR 錯字 ro→10、II→11 先換回數字）正好是下一個預期註號才算新的一條，
    否則是上一條的續行——書目裡常有「3. Aufl.」「vol. 2.」之類，只看格式會切錯。"""
    groups: dict[str, list[str]] = {}
    key = None
    for _, _, raw in pages:
        for line in strip_page_furniture(raw.split("\n"), running):
            s = line.strip()
            if is_caps_heading(s) and not NOTE_START.match(s):
                key = s.lower()
                groups[key] = []
                continue
            if key is None:
                continue
            notes = groups[key]
            m = NOTE_START.match(s) or (None if notes else re.match(r"^(\S{1,3})\.\s+(.*)$", s))
            n = _note_no(m.group(1)) if m else None
            if m and not notes and n is None:
                n = 1                               # 一組的第一條註號糊掉（如「rt.」）照樣當第 1 條
            if n and len(notes) < n <= len(notes) + 8:
                # 允許跳號：行首註號被 OCR 吃掉的那條補佔位，後面的號碼才不會整排錯位
                notes += ["（OCR 缺此註）"] * (n - len(notes) - 1)
                notes.append(s)
            elif m and _note_no(m.group(1)) is None and notes and PARA_END.search(notes[-1]):
                notes.append(s)                     # 註號糊到認不出，但上一條已收尾
            elif notes:
                if notes[-1].endswith("-") and s[:1].islower():
                    notes[-1] = notes[-1][:-1] + s
                else:
                    notes[-1] += " " + s
    return groups


ORIG_NOTE = re.compile(r"^\((\d+)\)\s*原註")
TR_NOTE = re.compile(r"^\((\d+)\)\s*譯註")


def _note_sim(zh: str, en: str) -> float:
    """兩條註的相似度：共同的數字（頁碼、年份）＋共同的西文詞（書名、人名）。"""
    zn, en_ = set(re.findall(r"\d{2,}", zh)), set(re.findall(r"\d{2,}", en))
    zw = {w.lower() for w in re.findall(r"[A-Za-z]{4,}", zh)}
    ew = {w.lower() for w in re.findall(r"[A-Za-z]{4,}", en)}
    return len(zn & en_) + 0.5 * len(zw & ew)


def pair_notes(zh_notes: list[str], en_notes: list[str]) -> tuple[str, dict[int, int], str]:
    """中譯本的註＝原註（翻原書的註）＋譯註混編一個號，而且有的原書註沒標「原註」二字，
    所以不能數「第 k 條原註」。改用內容做單調序列對齊（共同的頁碼、年份、西文詞；標了「原註」的加分），
    把英文註掛到配上的中文註號，閱讀器的註釋區按號碼並排。配不上的英文註不丟，接在前一條下面。
    回傳 (英文註釋區文字, {原書註號: 中文註號}, 警告)。"""
    zs = [(int(m.group(1)), n) for n in zh_notes if (m := re.match(r"^\((\d+)\)", n))]
    if not en_notes or not zs:
        return "", {}, ""
    n, m = len(zs), len(en_notes)
    sim = [[_note_sim(z, e) + (0.5 if ORIG_NOTE.match(z) else -0.5 if TR_NOTE.match(z) else 0.0) for e in en_notes] for _, z in zs]
    best = [[0.0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            take = best[i + 1][j + 1] + sim[i][j] if sim[i][j] >= 1.0 else -1.0
            best[i][j] = max(take, best[i + 1][j], best[i][j + 1])
    kmap: dict[int, int] = {}
    i = j = 0
    while i < n and j < m:
        if sim[i][j] >= 1.0 and best[i][j] == best[i + 1][j + 1] + sim[i][j]:
            kmap[j + 1] = zs[i][0]
            i, j = i + 1, j + 1
        elif best[i][j] == best[i + 1][j]:
            i += 1
        else:
            j += 1
    # 錨點之間補配：兩個已配上的註之間，英文剩 x 條、中文剩 x 條原註（或剛好 x 條任何註）就照順序配
    anchors = [(0, -1)] + sorted((k, next(i for i, (z, _) in enumerate(zs) if z == kmap[k])) for k in kmap)
    anchors.append((m + 1, n))
    for (k0, i0), (k1, i1) in zip(anchors, anchors[1:]):
        ek = list(range(k0 + 1, k1))
        if not ek:
            continue
        zi = [i for i in range(i0 + 1, i1) if ORIG_NOTE.match(zs[i][1])]
        if len(zi) != len(ek):
            zi = list(range(i0 + 1, i1))
        if len(zi) == len(ek):
            for k, i in zip(ek, zi):
                kmap[k] = zs[i][0]
    rows = []
    for k, t in enumerate(en_notes, 1):
        rows.append(f"({kmap[k]}) {t}" if k in kmap else t)
    if rows and not rows[0].startswith("("):
        rows[0] = f"({zs[0][0]}) {rows[0]}"
    miss = [k for k in range(1, m + 1) if k not in kmap and "OCR 缺此註" not in en_notes[k - 1]]
    warn = f"原書註 {m} 條配上 {len(kmap)} 條；沒配上：{miss[:12]}" if miss else ""
    return "\n\n".join(rows), kmap, warn


# ── 中文側 ──────────────────────────────────────────────────────────────────

def html_tables_to_md(text: str) -> str:
    """MinerU 的 <table>：單欄表拆成逐行段落，多欄表轉 markdown 表格（閱讀器只認後者）。"""
    def conv(m):
        rows = re.findall(r"<tr>(.*?)</tr>", m.group(0), flags=re.S)
        cells = [[html.unescape(re.sub(r"<[^>]+>", "", c)).strip()
                  for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, flags=re.S)] for r in rows]
        if all(len(r) <= 1 for r in cells):
            return "\n\n".join(r[0] for r in cells if r and r[0])
        w = max(len(r) for r in cells)
        lines = ["| " + " | ".join(r + [""] * (w - len(r))) + " |" for r in cells]
        return "\n".join([lines[0], "|" + " --- |" * w] + lines[1:])
    return re.sub(r"<table>.*?</table>", conv, text, flags=re.S)


def body_and_notes(texts: list[str]) -> tuple[str, list[str]]:
    """把各塊裡夾在分隔線之間的註釋抽出來，正文接回（被註釋切斷的段落不加段落分隔）。"""
    body = ""
    notes: list[str] = []
    for t in texts:
        in_notes = False
        pieces = []
        for para in re.split(r"\n{2,}", t):
            if FOOT_RULE_RE.match(para.strip()):
                in_notes = not in_notes
                continue
            if in_notes or re.match(r"^\(\d+\)\s", para.strip()):
                notes.append(para.strip())
            else:
                pieces.append(para)
        for para in pieces:
            para = para.strip()
            if not para:
                continue
            tail = PAGE_MARK_RE.sub("", REF_RE.sub("", body)).rstrip()
            glue = "" if body and tail and tail[-1] not in ZH_END and not para.startswith("#") else "\n\n"
            body = (body + glue + para) if body else para
    return body, notes


def _title_regex(title: str) -> str:
    chars = [c for c in title if not c.isspace() and c != "　"]
    return r"[\s　]*".join(re.escape(c) for c in chars)


def cut_prefix(body: str, title: str) -> str:
    """去掉正文開頭黏著的章名（前面可能有頁碼標記）。"""
    m = re.match(r"((?:\{\{p:[^}]*\}\}|\s)*)" + _title_regex(title) + r"\s*", body)
    return (m.group(1) + body[m.end():]) if m else body


def insert_headings(body: str, titles: list[str]) -> tuple[str, list[str]]:
    """依序在正文裡找節名（須位於段首／句末之後），插成獨立的 ### 段。回傳 (新正文, 找不到的節名)。"""
    missing = []
    pos = 0
    for t in titles:
        rx = re.compile(_title_regex(t) + r"((?:\[\^\d+\])*)")
        hit = None
        for m in rx.finditer(body, pos):
            before = PAGE_MARK_RE.sub("", body[max(0, m.start() - 40):m.start()]).rstrip(" ")
            if not before or before[-1] in "\n" + ZH_END:
                hit = m
                break
        if not hit:
            missing.append(t)
            continue
        new = f"\n\n### {t}{hit.group(1)}\n\n"
        body = body[:hit.start()].rstrip() + new + body[hit.end():].lstrip()
        pos = hit.start() + len(new)
    return body, missing


# ── 段落對齊（Gale–Church 式，加數字／西文詞重疊）───────────────────────────

def _clean_len(s: str) -> int:
    return len(re.sub(r"\s", "", PAGE_MARK_RE.sub("", REF_RE.sub("", s)))) or 1


def _tokens(s: str) -> set[str]:
    s = PAGE_MARK_RE.sub("", REF_RE.sub("", s))
    nums = set(re.findall(r"\d{2,}", s))
    words = {w.lower() for w in re.findall(r"[A-Za-z]{4,}", s)}
    return nums | words


BEADS = {(1, 1): 0.0, (1, 2): 0.9, (2, 1): 0.9, (1, 3): 2.2, (3, 1): 2.2, (2, 2): 1.6,
         (1, 0): 3.0, (0, 1): 3.0}


def align(zh: list[str], en: list[str]) -> list[tuple[list[str], list[str]]]:
    if not zh or not en:
        return [([z], []) for z in zh] + [([], [e]) for e in en]
    r = sum(map(_clean_len, zh)) / max(1, sum(map(_clean_len, en)))
    zt, et = [_tokens(z) for z in zh], [_tokens(e) for e in en]
    INF = float("inf")
    n, m = len(zh), len(en)
    cost = [[INF] * (m + 1) for _ in range(n + 1)]
    back = [[None] * (m + 1) for _ in range(n + 1)]
    cost[0][0] = 0.0
    for i in range(n + 1):
        for j in range(m + 1):
            if cost[i][j] == INF:
                continue
            for (a, b), pen in BEADS.items():
                if i + a > n or j + b > m:
                    continue
                lz = sum(_clean_len(x) for x in zh[i:i + a])
                le = sum(_clean_len(x) for x in en[j:j + b])
                if a and b:
                    c = abs(math.log((lz + 30) / (r * le + 30))) * 4 + pen
                    shared = set().union(*zt[i:i + a]) & set().union(*et[j:j + b])
                    c -= min(2.0, 0.6 * len(shared))
                else:
                    c = pen + 0.002 * (lz if a else r * le)
                if cost[i][j] + c < cost[i + a][j + b]:
                    cost[i + a][j + b] = cost[i][j] + c
                    back[i + a][j + b] = (a, b)
    rows = []
    i, j = n, m
    while i or j:
        a, b = back[i][j]
        rows.append((zh[i - a:i], en[j - b:j]))
        i, j = i - a, j - b
    return rows[::-1]


# ── 組裝 ────────────────────────────────────────────────────────────────────

def paras(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]


def fold_empty(ps: list[str]) -> list[str]:
    """只剩頁碼標記的段併進下一個正文段；沒有任何字母數字漢字的 OCR 雜訊段（如「|」）丟掉。"""
    out: list[str] = []
    carry = ""
    for p in ps:
        if not re.search(r"\w", PAGE_MARK_RE.sub("", p)):
            carry += "".join(PAGE_MARK_RE.findall(p))
            continue
        if p.startswith("#"):
            out.append(p)
        else:
            out.append(carry + p)
            carry = ""
    if carry and out:
        out[-1] += carry
    return out


def split_sections(ps: list[str]) -> list[tuple[str | None, list[str]]]:
    secs: list[tuple[str | None, list[str]]] = [(None, [])]
    for p in ps:
        if p.startswith("### "):
            secs.append((p, []))
        else:
            secs[-1][1].append(p)
    return secs


def _join(ps: list[str]) -> str:
    return "\n".join(ps) if ps else EMPTY_CELL


def build_part(label: str, zh_body: str, en_blocks: list[tuple[str, str]] | None,
               en_heading: str | None) -> tuple[str, str | None, list[str]]:
    """一章：回傳 (中文正文含段號, 原文含段號或 None, 警告)。"""
    warns: list[str] = []
    zp = paras(zh_body)
    head = [p for p in zp if p.startswith("## ")]
    zsecs = split_sections(fold_empty([p for p in zp if not p.startswith("## ")]))
    if en_blocks is None:
        out, sec_no = [], 0
        for h, ps in zsecs:
            if h:
                sec_no += 1
                out.append(h)
            for k, p in enumerate(ps, 1):
                sid = f"{label}-{sec_no}-{k}" if len(zsecs) > 1 else f"{label}-{k}"
                out.append(f"{{{{s:{sid}}}}}{p}")
        return "\n\n".join(head + out), None, warns
    esecs: list[tuple[str | None, list[str]]] = [(None, [])]
    for kind, text in en_blocks:
        if kind == "h":
            esecs.append((f"### {text}", []))
        else:
            esecs[-1][1].append(text)
    esecs = [(h, fold_empty(ps)) for h, ps in esecs]
    if not zsecs[0][1] and not esecs[0][1]:
        zsecs, esecs = zsecs[1:], esecs[1:]
    if len(zsecs) != len(esecs):
        warns.append(f"{label}：節數不一致 中 {len(zsecs)}／英 {len(esecs)} → 整章不分節對齊")
        zsecs = [(None, [p for h, ps in zsecs for p in ([h] if h else []) + ps])]
        esecs = [(None, [p for h, ps in esecs for p in ([h] if h else []) + ps])]
    two_level = all(h is None for h, _ in zsecs)
    zo, eo = list(head), ([f"## {en_heading}"] if en_heading else [])
    if head and not en_heading:
        eo.append(EMPTY_CELL)
    has_intro = zsecs[0][0] is None and not two_level
    for si, ((zh_h, zps), (en_h, eps)) in enumerate(zip(zsecs, esecs)):
        sec_no = si if has_intro else si + 1
        if zh_h or en_h:
            zo.append(zh_h or EMPTY_CELL)
            eo.append(en_h or EMPTY_CELL)
        k, extra = 0, 0
        for zg, eg in align(zps, eps):
            # 段號只數原文段落（同一本原文不論配哪個譯本號碼都不變）：
            # 譯者併段寫 5–6，譯本多出原文沒有的段接前號加字母 5a
            if eg:
                n0, k, extra = k + 1, k + len(eg), 0
                num = f"{n0}" if n0 == k else f"{n0}–{k}"
            else:
                extra += 1
                num = f"{k}{chr(96 + extra)}"
            sid = f"{label}-{num}" if two_level else f"{label}-{sec_no}-{num}"
            mark = f"{{{{s:{sid}}}}}"
            zo.append(mark + _join(zg) if zg else EMPTY_CELL)
            eo.append(mark + _join(eg) if eg else EMPTY_CELL)
    return "\n\n".join(zo), "\n\n".join(eo), warns


def printed_map(chunks: list[dict]) -> dict[int, int]:
    """PDF 頁 → 印刷頁（逐頁對應的 page_numbers／printed_pages）。"""
    known = {}
    for c in chunks:
        for p, q in zip(c.get("page_numbers") or [], c.get("printed_pages") or []):
            if q:
                known[p] = q
    return known


def infer_printed(pdf: int, known: dict[int, int]) -> int | None:
    """章首頁常不印頁碼：用前後 3 頁內已知的頁碼推（差值要前後一致才用）。"""
    for d in (1, 2, 3):
        for q in (pdf + d, pdf - d):
            if q in known and known[q] - (q - pdf) >= 1:
                return known[q] - (q - pdf)
    return None


def fix_leading_marker(c: dict, known: dict[int, int]) -> str:
    """舊合併把每塊第一個頁碼標記寫成 PDF 頁；換成該頁的印刷頁（推不出就拿掉，不留假頁碼）。"""
    pp = known.get(c["page_number"]) or infer_printed(c["page_number"], known)
    return re.sub(r"^\{\{p:\d+\}\}", f"{{{{p:{pp}}}}}" if pp else "", c["content"])


# ── 書別設定 ───────────────────────────────────────────────────────────────

MADSEN = {
    "zh_id": "539068d3-b75a-4480-a1fd-3e9817b9886b",
    "en_id": "727d0835-ff32-4629-83af-9ae8185fbb8f",
    "offset": 28,                                       # 英文 PDF 頁 − 印刷頁（第 29 頁起）
    "running": {"Preface", "Acknowledgments", "Conclusions", "Notes", "The Taiwanese Religious Context",
                "Tzu Chi", "Buddha’s Light Mountain", "Buddha's Light Mountain", "Dharma Drum Mountain",
                "The Enacting Heaven Temple"},
    "notes_pages": (187, 202),
    "extra_subs": {"自序": ["主題"]},                    # 目錄沒列、正文裡有的小標
    "title_in_text": {"導讀宗教、民主政治與現代性危機蕭阿勤": "導讀宗教、民主政治與現代性危機"},  # 正文開頭實際的標題字樣
    # (段號前綴, 中文章名（chapter_path 頂層）, 顯示標題, 英文頁起訖或 None, 英文章名, 開頭要剝的行, Notes 節名)
    "parts": [
        ("導讀", "導讀宗教、民主政治與現代性危機蕭阿勤", "導讀　宗教、民主政治與現代性危機（蕭阿勤）", None, None, (), None),
        ("中譯序", "中文版序（中譯本獨有）", "中文版序", None, None, (), None),
        ("謝辭", "謝辭", "謝辭", (11, 12), "Acknowledgments", ("Acknowledgments",), None),
        ("序", "自序", "自序", (15, 28), "Preface", ("Preface",), "preface"),
        ("1", "第一章　臺灣的宗教情境", "第一章　臺灣的宗教情境", (29, 43),
         "Chapter 1. The Taiwanese Religious Context", ("CHAPTER", "I", "The Taiwanese Religious Context"),
         "chapter i. the taiwanese religious context"),
        ("2", "第二章　慈濟：佛教慈悲的現代化", "第二章　慈濟：佛教慈悲的現代化", (44, 78),
         "Chapter 2. Tzu Chi: The Modernization of Buddhist Compassion",
         ("CHAPTER", "2", "Tzu Chi", "The Modernization of Buddhist Compassion"), "chapter 2. tzu chi"),
        ("3", "第三章　佛光山：佛教對民主公民宗教的貢獻", "第三章　佛光山：佛教對民主公民宗教的貢獻", (79, 112),
         "Chapter 3. Buddha’s Light Mountain: The Buddhist Contribution to a Democratic Civil Religion",
         ("CHAPTER 3",), "chapter 3. buddha’s light mountain"),
        ("4", "第四章　法鼓山：「國土危脆」中的超越性意義", "第四章　法鼓山：「國土危脆」中的超越性意義", (113, 131),
         "Chapter 4. Dharma Drum Mountain: Transcendent Meaning in a Precarious World",
         ("CHAPTER 4",), "chapter 4. dharma drum mountain"),
        ("5", "第五章　行天宮：混合的現代性", "第五章　行天宮：混合的現代性", (132, 158),
         "Chapter 5. The Enacting Heaven Temple: Hybrid Modernity", ("CHAPTER 5",),
         "chapter 5. the enacting heaven temple"),
        ("結論", "結論", "結論", (159, 186), "Conclusions", ("Conclusions",), "conclusions"),
        ("譯後記", "譯後記（中譯本獨有）", "譯後記", None, None, (), None),
    ],
}
BOOKS = {"madsen": MADSEN}


def load(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.open(encoding="utf-8")]


def build(cfg: dict) -> tuple[list[dict], list[str]]:
    # 一律從第一次重建前的備份讀，重跑才會得到同樣結果（讀已重建的檔會找不到原本黏在正文裡的節名）
    orig = CHUNKS / f"{cfg['zh_id']}.jsonl.bak_bilingual"
    zh = load(orig if orig.exists() else CHUNKS / f"{cfg['zh_id']}.jsonl")
    en_pages = load(CHUNKS / f"{cfg['en_id']}.jsonl.bak_chapters")
    off = cfg["offset"]

    def en_range(a, b):
        return [(c["page_number"], (c["page_number"] - off) if c["page_number"] > off else None, c["content"])
                for c in en_pages if a <= c["page_number"] <= b]

    na, nb = cfg["notes_pages"]
    notes = parse_notes(en_range(na, nb), cfg["running"] | {"Notes"})
    warns: list[str] = []
    by_top: dict[str, list[dict]] = {}
    order: list[str] = []
    for c in zh:
        top = (c.get("chapter_path") or "").split(" / ")[0]
        if top not in by_top:
            order.append(top)
            by_top[top] = []
        by_top[top].append(c)
    parts = {p[1]: p for p in cfg["parts"]}
    known = printed_map(zh)
    out: list[dict] = []
    for top in order:
        cs = by_top[top]
        first = dict(cs[0])
        first.pop("source_text", None)
        first.pop("source_lang", None)
        pages = sorted({p for c in cs for p in (c.get("page_numbers") or [c["page_number"]])})
        first["page_numbers"] = pages
        first["printed_pages"] = [known.get(p) or infer_printed(p, known) for p in pages]
        first["printed_page"] = first["printed_pages"][0]
        texts = [html_tables_to_md(fix_leading_marker(c, known)) for c in cs]
        if top not in parts:                 # 封面／版權頁／目次／參考書目／索引：合併、不配原文
            first["content"] = "\n\n".join(texts)
            out.append(first)
            continue
        label, _, display, en_pp, en_title, skip, notes_key = parts[top]
        body, zh_notes = body_and_notes(texts)
        body = cut_prefix(body, cfg.get("title_in_text", {}).get(top, top.replace("（中譯本獨有）", "")))
        subs = [(c.get("chapter_path") or "").split(" / ", 1)[1].replace("（中譯本獨有）", "")
                for c in cs if " / " in (c.get("chapter_path") or "")]
        subs = list(dict.fromkeys(subs + cfg.get("extra_subs", {}).get(top, [])))
        body, missing = insert_headings(body, subs)
        if missing:
            warns.append(f"{label}：中文正文找不到節名 {missing}")
        body = f"## {display}\n\n{body}"
        en_blocks = None
        if en_pp:
            en_blocks = pages_to_blocks(en_range(*en_pp), cfg["running"], set(skip))
            if label == "1" and en_blocks and en_blocks[0] == ("h", "I"):
                en_blocks = en_blocks[1:]
        zc, ec, w = build_part(label, body, en_blocks, en_title)
        warns += w
        if ec is not None:
            ns = notes.get(notes_key) if notes_key else None
            if notes_key and not ns:
                warns.append(f"{label}：書末 Notes 找不到「{notes_key}」（有 {list(notes)}）")
            block, kmap, w = pair_notes(zh_notes, ns or [])
            if w:
                warns.append(f"{label}：{w}")
            # 英文正文殘存的上標註號：OCR 幾乎全丟、殘存的又常是「!」「2:00」誤判，連過去會跳錯條，一律拿掉；
            # 英文註改由章末註釋區按中文註號逐條並排
            ec = REF_RE.sub("", ec)
            if block:
                ec += f"\n\n{FOOT_RULE}\n\n{block}"
        if zh_notes:
            zc += f"\n\n{FOOT_RULE}\n\n" + "\n\n".join(zh_notes)
        first["chapter_path"] = display
        first["chunk_type"] = "chapter"
        if "\n### " in zc:
            first["section_anchors"] = True        # 章內 ### 小節要進側欄目錄（ebook-chunks.ts loadToc）
        first["content"] = zc
        if ec is not None:
            first["source_text"] = ec
            first["source_lang"] = "en"
        out.append(first)
    for i, c in enumerate(out):
        c["chunk_index"] = i
        c["format"] = "markdown"
    return out, warns


def summarize(chunks: list[dict]) -> None:
    for c in chunks:
        z = paras(c["content"])
        e = paras(c.get("source_text") or "")
        zb = [p for p in z if not re.match(r"^\(\d+\)\s", p) and not FOOT_RULE_RE.match(p)]
        empt_z = sum(1 for p in zb if p == EMPTY_CELL)
        empt_e = sum(1 for p in e if p == EMPTY_CELL)
        h3 = sum(1 for p in z if p.startswith("### "))
        print(f"  [{c['chunk_index']:2}] {(c['chapter_path'] or '')[:28]:28} 中 {len(zb):3} 段（空 {empt_z}）"
              f" 英 {len(e):3} 段（空 {empt_e}） ### {h3}  {len(c['content']):6,}／{len(c.get('source_text') or ''):6,} 字")


def show(c: dict, n: int = 400) -> None:
    z = [p for p in paras(c["content"]) if not re.match(r"^\(\d+\)\s", p) and not FOOT_RULE_RE.match(p)]
    e = paras(c.get("source_text") or "")
    for k in range(max(len(z), len(e))):
        zz = z[k] if k < len(z) else ""
        ee = e[k] if k < len(e) else ""
        print(f"--- {k}\n中 {zz[:120]!r}\n英 {ee[:200]!r}")
        if k >= n:
            break


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("book", choices=BOOKS)
    ap.add_argument("--show", type=int, help="印第 N 塊逐列對照")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    cfg = BOOKS[a.book]
    chunks, warns = build(cfg)
    summarize(chunks)
    for w in warns:
        print("⚠", w)
    if a.show is not None:
        show(chunks[a.show])
    if a.apply:
        sys.path.insert(0, str(Path(__file__).parent))
        import standardize_ebook as se
        src = CHUNKS / f"{cfg['zh_id']}.jsonl"
        bak = src.with_name(src.name + ".bak_bilingual")
        if not bak.exists():                       # 只留第一次的原貌，重跑不可覆蓋
            shutil.copy2(src, bak)
        o = se.write_jsonl(cfg["zh_id"], chunks)
        print("R2", se.push_to_r2(cfg["zh_id"], o), "bytes")
        se.update_db(cfg["zh_id"], chunks)
        print("✓ 已寫回", o)


if __name__ == "__main__":
    main()
