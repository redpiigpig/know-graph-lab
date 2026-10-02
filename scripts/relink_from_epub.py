#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""F 型書（正文完全沒註號、註文都在）從原 EPUB 的註號錨點補回 [^N]（2026-10-02）。

F 型 4,163／4,700 則在 EPUB：原檔裡正文與註文是成對互指的 <a href="#…">(1)</a>／<sup>[1]</sup>，
解析時把錨點丟了。這支不用模型：
  1. 讀原 EPUB（先複製到本機），每個「正文側」錨點記下：錨點前的正文文字＋它指向的註文內容；
     正文側／註文側的分法：錨點在所屬段落最前面的是註文側（回指），其餘是正文側。
  2. 現行 JSONL 每塊缺連結的註 N：用註文內容（正規化後前 20 字）找 EPUB 的同一則註，
     再用錨點前的文字（正規化後最後 12 字）在該塊正文裡定位，剛好出現一次才插 [^N]。
正規化＝轉繁體、只留文字與數字（去標點、markdown、{{…}} 標記與既有 [^N]），所以簡體 EPUB 對繁體 JSONL 也對得上。

  python -X utf8 scripts/relink_from_epub.py --ids <id> [...]            # 乾跑，印每處
  python -X utf8 scripts/relink_from_epub.py --ids <id> [...] --apply    # 寫回（留 .bak_relink），推 R2＋更新 DB
"""
from __future__ import annotations

import json
import posixpath
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import relink_missing_footnotes as rl  # noqa: E402

NUM = re.compile(r"^\W{0,2}\d{1,4}\W{0,2}$")
LEAD = re.compile(r"^\s*[\[(（〔]?\s*\d{1,4}\s*[\])）〕]?\s*[.、．:：]?\s*")
BLOCKS = ["p", "li", "div", "aside", "dd", "td", "section", "blockquote"]
MARK = re.compile(r"\{\{[^}]*\}\}|\[\^\d+\]|[\W_]")   # 只留文字與數字：標點、引號形式、markdown 都不比
CTX = 12
KEY = 20


def _t(s: str) -> str:
    import standardize_ebook as se
    return se.to_traditional(s)


def norm(s: str) -> str:
    return _t(MARK.sub("", s or ""))


def norm_map(s: str) -> tuple[str, list[int]]:
    """純函式：去掉標記與空白後的字串，以及每個字在原字串的位置。"""
    out, pos, i = [], [], 0
    for m in MARK.finditer(s):
        for k in range(i, m.start()):
            out.append(s[k])
            pos.append(k)
        i = m.end()
    for k in range(i, len(s)):
        out.append(s[k])
        pos.append(k)
    return "".join(out), pos


def note_key(text: str) -> str:
    return norm(LEAD.sub("", text or ""))[:KEY]


def epub_refs(path: str) -> list[tuple[str, str]]:
    """原 EPUB → [(錨點前正文, 註文)]（正文側錨點，依檔案內順序）。"""
    from bs4 import BeautifulSoup
    loc = Path(tempfile.gettempdir()) / "relink_from_epub.epub"
    shutil.copyfile(path, loc)                  # PyMuPDF／zip 零碎讀 Drive 會卡
    z = zipfile.ZipFile(loc)
    docs = {}
    for n in z.namelist():
        if re.search(r"\.x?html?$", n, re.I):
            docs[n] = BeautifulSoup(z.read(n).decode("utf-8", "ignore"), "html.parser")
    ids = {}
    for n, d in docs.items():
        for el in d.find_all(id=True):
            ids[(n, el["id"])] = el

    def block_of(el):
        return el.find_parent(BLOCKS) or el.parent

    def note_text(tgt) -> str:
        """錨點所在段落；段落太大（加爾文整頁包一個 div）就取錨點之後緊接的文字。"""
        nb = block_of(tgt) or tgt
        t = nb.get_text(" ", strip=True)
        if len(t) <= 1500:
            return t
        buf = []
        for el in tgt.next_elements:
            if isinstance(el, str):
                buf.append(el)
                if sum(map(len, buf)) > 200:
                    break
        return (tgt.get_text(" ", strip=True) + " " + "".join(buf)).strip()

    out = []
    for n, d in docs.items():
        refs = []
        for a in d.find_all("a", href=True):
            if "#" not in a["href"] or not NUM.match(a.get_text(strip=True)):
                continue
            blk = block_of(a)
            if blk is None:
                continue
            if blk.get_text().lstrip().startswith(a.get_text().strip()):
                continue                         # 錨點在段首＝註文側的回指
            f, frag = a["href"].split("#", 1)
            tgt = ids.get((posixpath.normpath(posixpath.join(posixpath.dirname(n), f)) if f else n, frag))
            if tgt is None:
                continue
            refs.append((a, blk, note_text(tgt)))
        for i, (a, blk, _) in enumerate(refs):
            a.replace_with(f"{i}")
        for i, (a, blk, note) in enumerate(refs):
            txt = blk.get_text()
            k = txt.find(f"{i}")
            before = re.sub("\\d+", "", txt[:k])
            out.append((before, note))
    return out


def place(body: str, before: str, n: int) -> str | None:
    """純函式：錨點前文字（正規化後最後 CTX 字）在 body 剛好出現一次 → 插 [^n]。"""
    ctx = norm(before)[-CTX:]
    if len(ctx) < 6:
        return None
    nb, pos = norm_map(body)
    if nb.count(ctx) != 1:
        return None
    at = pos[nb.index(ctx) + len(ctx) - 1] + 1
    if body[at:at + 2] == "[^":
        return None
    return body[:at] + f"[^{n}]" + body[at:]


MASS = re.compile(r"(?m)^\(\d+\)(?:\s|$)|\[\^@?\w+\]|[\W_]")
# (1)＋空白／不換行空白／換行（暗網、荷馬那本號碼自成一行）；註釋區最尾巴光禿禿的「(1)」也算一則（加爾文塊 150）
NOTE_LINE = re.compile(r"(?m)^\((\d+)\)(?:\s+|$)")
RULE_TXT = "\n" + "—" * 20 + "\n"


def split_notes(notes: str) -> list[tuple[int, str]]:
    """純函式：註釋區 → [(N, 整則文字含續行)]，保留原順序；第一則之前的雜文併進第一則前面不處理（回傳時丟棄）。"""
    ms = list(NOTE_LINE.finditer(notes))
    return [(int(m.group(1)), notes[m.end():(ms[i + 1].start() if i + 1 < len(ms) else len(notes))].rstrip("\n"))
            for i, m in enumerate(ms)]


def renumber(body: str, notes: list[tuple[str, str]]) -> tuple[str, str]:
    """純函式：notes＝[(標籤, 註文)]，標籤是正文裡的 [^標籤]（原號或 @暫號）。
    依正文出現順序重編 1..；正文沒引用的註排在最後。回傳 (新正文, 新註釋區)。"""
    # 🚨 同一塊會有重號（加爾文書尾各章各自從 1 編）：按「哪一則」配，不可用 dict（曾少 48,779 字，守恆擋下）
    used: set[int] = set()
    seq: list[int] = []
    last: dict[str, int] = {}

    def sub(m):
        tag = m.group(1)
        i = next((i for i, (t, _) in enumerate(notes) if t == tag and i not in used), None)
        if i is None:
            return f"[^{last[tag]}]" if tag in last else m.group(0)
        used.add(i)
        seq.append(i)
        last[tag] = len(seq)
        return f"[^{len(seq)}]"

    body = re.sub(r"\[\^(@?\w+)\]", sub, body)
    order = seq + [i for i in range(len(notes)) if i not in used]
    return body, "\n".join(f"({k + 1}) {notes[i][1]}" for k, i in enumerate(order)) + "\n"


def note_total(chunks: list[dict]) -> int:
    return sum(len(split_notes(parts[2])) for c in chunks if (parts := rl.split_body(c.get("content") or "")))


def mass(chunks: list[dict]) -> int:
    return sum(len(MASS.sub("", c.get("content") or "")) for c in chunks)


def relink_book(bid: str, epub: str, apply: bool) -> tuple[int, int]:
    """跨塊：錨點前文字在全書正文找，剛好一處才採用；註文搬到引用所在那一塊（註釋跟著引用頁走），兩塊都依出現順序重編。"""
    p = rl.CH / f"{bid}.jsonl"
    chunks = [json.loads(l) for l in p.open(encoding="utf-8") if l.strip()]
    refs = epub_refs(epub)
    by_key: dict[str, list[str]] = {}
    for before, note in refs:
        by_key.setdefault(note_key(note), []).append(before)
    before_gap = rl.gap_count(chunks)
    mass0, notes0 = mass(chunks), note_total(chunks)
    # 各塊：正文、註釋 [(標籤, 文)]；沒有註釋區的塊 notes=[]
    body, notes, pre = [], [], []
    for c in chunks:
        parts = rl.split_body(c.get("content") or "")
        if parts:
            body.append(parts[0])
            notes.append([(str(n), t) for n, t in split_notes(parts[2])])
            m0 = NOTE_LINE.search(parts[2])
            pre.append((parts[2][:m0.start()] if m0 else parts[2]).strip())   # 第一則 (N) 之前的雜文原樣留著
        else:
            body.append(c.get("content") or "")
            notes.append([])
            pre.append("")
    nmap = [norm_map(b) for b in body]
    touched, done, uid = set(), 0, 0
    for k in range(len(chunks)):
        for item in list(notes[k]):
            tag, text = item
            if not tag.isdigit() or f"[^{tag}]" in body[k]:
                continue
            key = note_key(text)
            if len(key) < 8:
                continue                         # 「同上」「Ibid.」這種短註文對不準
            hits = set()
            for b in by_key.get(key, []):
                ctx = norm(b)[-CTX:]
                if len(ctx) < 6:
                    continue
                for j, (nb, _) in enumerate(nmap):
                    c = nb.count(ctx)
                    if c:
                        hits.add((j, nb.index(ctx) + len(ctx) - 1) if c == 1 else (j, -1))
            if len(hits) != 1 or next(iter(hits))[1] < 0:
                continue
            j, idx = next(iter(hits))
            at = nmap[j][1][idx] + 1
            if body[j][at:at + 2] == "[^":
                continue
            uid += 1
            new_tag = f"@{uid}"
            body[j] = body[j][:at] + f"[^{new_tag}]" + body[j][at:]
            nmap[j] = norm_map(body[j])
            notes[k] = [x for x in notes[k] if x is not item]   # 按「哪一則」刪，重號的另一則留著
            notes[j].append((new_tag, text))
            touched |= {j, k}
            done += 1
            print(f"塊{k}→塊{j} ✓ 註{tag} …{body[j][max(0, at - 20):at]}【^】｜{text[:30]}", flush=True)
    for j in touched:
        if notes[j] or pre[j]:
            b, ns = renumber(body[j], notes[j]) if notes[j] else (body[j], "")
            chunks[j]["content"] = b.rstrip("\n") + RULE_TXT + (pre[j] + "\n" if pre[j] else "") + ns
        else:
            chunks[j]["content"] = body[j]
    after_gap = rl.gap_count(chunks)
    print(f"{bid}：EPUB 錨點 {len(refs)}；缺連結 {before_gap[1]} → {after_gap[1]}（補 {done}）", flush=True)
    if mass(chunks) != mass0:
        print("  ✗ 字數不守恆（註釋區有非 (N) 開頭的雜文被丟？），不寫回", flush=True)
        return before_gap[1], 0
    if note_total(chunks) != notes0:            # gap_count 不認 (N)+不換行空白，不能拿它當守恆量尺
        print(f"  ✗ 註文總數 {notes0} → {note_total(chunks)} 不守恆，不寫回", flush=True)
        return before_gap[1], 0
    if apply and done:
        shutil.copy2(p, p.with_suffix(".jsonl.bak_relink"))
        import standardize_ebook as se
        o = se.write_jsonl(bid, chunks)
        se.push_to_r2(bid, o)
        se.update_db(bid, chunks)
        print("  已寫回 Drive、推 R2、更新 DB", flush=True)
    return before_gap[1], done


def main() -> int:
    import requests
    import translate_ebook_to_zh as te
    ids = [a for a in sys.argv if re.fullmatch(r"[0-9a-f-]{36}", a)]
    h = {"apikey": te.KEY, "Authorization": "Bearer " + te.KEY}
    for bid in ids:
        m = requests.get(te.URL + "/rest/v1/ebooks", headers=h, timeout=60,
                         params={"select": "file_type,file_path", "id": "eq." + bid, "limit": "1"}).json()
        if not m or m[0]["file_type"] != "epub" or not Path(m[0]["file_path"] or "").exists():
            print(f"{bid}：不是 EPUB 或找不到原檔，略過")
            continue
        relink_book(bid, m[0]["file_path"], "--apply" in sys.argv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
