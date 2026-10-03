#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""教父卷（Schaff 38 卷）中英對照的「重切＋重新對齊」。純函式核心＋可驗證的驅動。

## 為什麼要這支（2026-10-02 量出來的真相）

先前以為「中文只譯了 5–30%」，那是量尺錯：一個 CCEL 檔（title_en 相同的連續幾塊）被切成好幾個
中文塊，但**每一塊的英文欄都掛整個檔**（實測 2accee20 詩篇講解 23 塊同一份 388 列英文）。
逐塊算中英字數比，就會得到 0.02–0.2。改以「檔」為單位（同 title_en 的連續塊、取一份英文）算，
中文／英文字數比 0.32–0.41＝完整譯本的正常範圍，**全 38 卷只有極少數檔真的缺譯**。
所以真正的毛病是**英文欄沒有切到各塊自己的那一段**，加上 number_multilingual 用長度比硬配
（dup 群組上配出整欄錯位，例：詩篇第八篇的英文旁邊放著第九篇的中文）。

## 做法

  1. 以「檔群組」為單位：連續、title_en 相同的塊。英文取群組裡**最完整的一份**（整檔）。
  2. 英文正文列 E 與整組中文正文列 Z（依塊序串接）做 Gale–Church 式 DP 對齊
     （長度比＋段首節號＋[^N] 註號＋{{p:N}} 頁碼＋數字重疊）。註文另外按 (N) 號配。
  3. 每塊拿到自己中文列所對到的英文列（＋夾在兩塊之間、沒有中文的英文列＝缺譯，記入缺口表）。
  4. 逐列輸出（中英列數相等、對不到處放零寬字元），重編段號 {{s:章-節-段}}。
  5. 守恆：每塊中文去標記後字數不變；整組英文去重後每列恰好出現一次。

不動中文欄的文字（只重排列＋補佔位）。缺譯另由 fathers_fill_gaps.py 逐列翻譯寫回。
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field

EMPTY = "​"
FOOT_RULE = "—" * 15
FOOT_RULE_RE = re.compile(r"^[—－\-]{15,}$")
TAG_RE = re.compile(r"\{\{s:[^}]*\}\}")
PAGE_RE = re.compile(r"\{\{p:(\d+)\}\}")
ANYTAG_RE = re.compile(r"\{\{[ps]:[^}]*\}\}")
REF_RE = re.compile(r"\[\^(\d+)\]")
FN_RE = re.compile(r"^\((\d+)\)\s")
FNDEF_RE = re.compile(r"^\[\^\d+\]:")
LEAD_RE = re.compile(r"^(?:\{\{[^}]*\}\})*\s*(?:#+\s*)?(\d{1,3})\.\s")
CJK = re.compile(r"[一-鿿]")
LAT = re.compile(r"[A-Za-z]")


def split_rows(text: str | None) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text or "") if p.strip()]


def clean_rows(text: str | None) -> list[str]:
    """去掉 {{s:}} 段號與零寬佔位列（它們是 number_multilingual 加的，不是內容）。"""
    out = []
    for r in split_rows(text):
        r = TAG_RE.sub("", r).strip()
        r = r.replace(EMPTY, "").strip()
        if r:
            out.append(r)
    return out


def split_zone(rows: list[str]) -> tuple[list[str], list[str]]:
    """(正文列, 註文列)。註文＝第一條分隔線之後；沒有分隔線時，連續的 (N) 開頭列尾巴當註文。"""
    for i, r in enumerate(rows):
        if FOOT_RULE_RE.match(r):
            return rows[:i], [x for x in rows[i + 1:]]
    i = len(rows)
    while i > 0 and FN_RE.match(rows[i - 1]):
        i -= 1
    return rows[:i], rows[i:]


def fn_map(rows: list[str]) -> dict[int, str]:
    """註文列 → {號: 全列文字}。一號重複時留第一個。"""
    out: dict[int, str] = {}
    for r in rows:
        m = FN_RE.match(r)
        if m:
            out.setdefault(int(m.group(1)), r)
    return out


def mass(t: str | None) -> int:
    return len(re.findall(r"\w", ANYTAG_RE.sub("", (t or "").replace(EMPTY, ""))))


# ── 對齊 ────────────────────────────────────────────────────────────────────

def _len_zh(s: str) -> int:
    return len(CJK.findall(REF_RE.sub("", s))) or 1


def _len_en(s: str) -> int:
    return len(LAT.findall(REF_RE.sub("", s))) or 1


def kind_of(row: str) -> str:
    """S 分隔線／F 註文列「(N) …」／B 其餘（正文、標題）。"""
    if FOOT_RULE_RE.match(row):
        return "S"
    return "F" if (FN_RE.match(row) or FNDEF_RE.match(row)) else "B"


@dataclass
class Feat:
    kind: str
    n: int            # 長度（zh=漢字數、en=拉丁字母數）
    lead: int | None
    refs: frozenset
    page: int | None
    nums: frozenset


def _fn_no(row: str) -> int | None:
    m = FN_RE.match(row) or re.match(r"^\[\^(\d+)\]:", row)
    return int(m.group(1)) if m else None


def feat(s: str, zh: bool) -> Feat:
    m = LEAD_RE.match(s)
    p = PAGE_RE.search(s)
    k = kind_of(s)
    plain = ANYTAG_RE.sub("", REF_RE.sub("", FNDEF_RE.sub("", FN_RE.sub("", s)) if k == "F" else s))
    return Feat(k, _len_zh(s) if zh else _len_en(s),
                (int(m.group(1)) if (m and k == "B") else _fn_no(s) if k == "F" else None),
                frozenset(int(x) for x in REF_RE.findall(s)),
                int(p.group(1)) if p else None,
                frozenset(re.findall(r"\d+" if k == "F" else r"\d{2,}", plain)))


BEADS = {(1, 1): 0.0, (1, 2): 0.9, (2, 1): 0.9, (1, 3): 2.2, (3, 1): 2.2, (2, 2): 1.6,
         (1, 0): 4.0, (0, 1): 3.0}


_EMPTY_FS = frozenset()


def _pair_cost(zf: list[Feat], ef: list[Feat], i: int, j: int, a: int, b: int, r: float,
               zown: list[int] | None = None) -> float:
    pen = BEADS[(a, b)]
    if a > 1 and zown is not None and zown[i] != zown[i + a - 1]:
        return float("inf")      # 一個對齊列不可跨兩塊中文（塊序單調，比頭尾即可）
    if a == 1 and b == 1:
        z, e = zf[i], ef[j]
        if z.kind != e.kind:
            return float("inf")
        c = abs(math.log((z.n + 30) / (r * e.n + 30))) * 4
        if z.refs and e.refs:
            sr = z.refs & e.refs
            c += -4.0 * min(2, len(sr)) if sr else 3.0
        if z.page is not None and e.page is not None:
            c += -4.0 if z.page == e.page else 2.0
        if z.lead is not None and e.lead is not None:
            c += -3.0 if z.lead == e.lead else 4.0
        if z.nums and e.nums:
            c -= min(2.0, 0.6 * len(z.nums & e.nums))
        return c
    if a and b:
        ks = {f.kind for f in zf[i:i + a]} | {f.kind for f in ef[j:j + b]}
        if len(ks) > 1:
            return float("inf")
    lz = sum(f.n for f in zf[i:i + a])
    le = sum(f.n for f in ef[j:j + b])
    if not (a and b):
        return pen + 0.002 * (lz if a else r * le)
    c = abs(math.log((lz + 30) / (r * le + 30))) * 4 + pen
    zr = _EMPTY_FS.union(*(f.refs for f in zf[i:i + a]))
    er = _EMPTY_FS.union(*(f.refs for f in ef[j:j + b]))
    if zr and er:
        c += -4.0 * min(2, len(zr & er)) if zr & er else 3.0
    zp = {f.page for f in zf[i:i + a] if f.page is not None}
    ep = {f.page for f in ef[j:j + b] if f.page is not None}
    if zp and ep:
        c += -4.0 if zp & ep else 2.0
    zl = zf[i].lead
    el = ef[j].lead
    if zl is not None and el is not None:
        c += -3.0 if zl == el else 4.0
    sh = _EMPTY_FS.union(*(f.nums for f in zf[i:i + a])) & _EMPTY_FS.union(*(f.nums for f in ef[j:j + b]))
    c -= min(2.0, 0.6 * len(sh))
    return c


_KIND = {"B": 0, "F": 1, "S": 2}
_BEAD_LIST = [(1, 1), (1, 0), (1, 2), (2, 1), (1, 3), (3, 1), (2, 2)]   # 碼 0..6；7 = (0,1)


def align(zh: list[str], en: list[str], r: float, band: float = 0.25, zown: list[int] | None = None):
    """→ [(zh 列索引 list, en 列索引 list)]，依序。Gale–Church 式全 DP（numpy 逐列向量化，無帶寬限制）。

    帶狀 DP 試過、不行：譯文不全時沿累計長度的對角線會漂，終點不可達就整段不對齊。
    """
    import numpy as np
    n, m = len(zh), len(en)
    if not n or not m:
        return [([i], []) for i in range(n)] + [([], [j]) for j in range(m)]
    zf = [feat(x, True) for x in zh]
    ef = [feat(x, False) for x in en]
    INF = np.inf
    zn = np.array([f.n for f in zf], dtype=float)
    en_n = np.array([f.n for f in ef], dtype=float)
    zk = np.array([_KIND[f.kind] for f in zf])
    ek = np.array([_KIND[f.kind] for f in ef])
    ZP = np.concatenate([[0.0], np.cumsum(zn)])
    EP = np.concatenate([[0.0], np.cumsum(en_n)])
    lead_e = np.array([(-1 if f.lead is None else f.lead) for f in ef])
    has_ref = np.array([bool(f.refs) for f in ef])
    has_page = np.array([f.page is not None for f in ef])
    ref_ix: dict[int, list[int]] = {}
    page_ix: dict[int, list[int]] = {}
    num_ix: dict[str, list[int]] = {}
    for j, f in enumerate(ef):
        for x in f.refs:
            ref_ix.setdefault(x, []).append(j)
        if f.page is not None:
            page_ix.setdefault(f.page, []).append(j)
        for x in f.nums:
            num_ix.setdefault(x, []).append(j)
    ekrun = {b: np.array([bool(j + b <= m and len(set(ek[j:j + b].tolist())) == 1) for j in range(m + 1)])
             for b in (2, 3)}

    def anchors(i: int):
        z = zf[i]
        v = np.zeros(m)
        if z.refs:
            v += 3.0 * has_ref
            cnt: dict[int, int] = {}
            for x in z.refs:
                for j in ref_ix.get(x, ()):
                    cnt[j] = cnt.get(j, 0) + 1
            for j, c in cnt.items():
                v[j] += -4.0 * min(2, c) - 3.0
        if z.page is not None:
            v += 2.0 * has_page
            for j in page_ix.get(z.page, ()):
                v[j] += -6.0
        if z.lead is not None:
            v += np.where(lead_e >= 0, np.where(lead_e == z.lead, -3.0, 4.0), 0.0)
        if z.nums:
            cnt2: dict[int, int] = {}
            for x in z.nums:
                for j in num_ix.get(x, ()):
                    cnt2[j] = cnt2.get(j, 0) + 1
            for j, c in cnt2.items():
                v[j] -= min(2.0, 0.6 * c)
        return v

    c01 = 3.0 + 0.002 * r * en_n
    P = np.concatenate([[0.0], np.cumsum(c01)])
    D = np.full((n + 1, m + 1), INF)
    bp = np.full((n + 1, m + 1), -1, dtype=np.int8)
    D[0] = P
    bp[0, 1:] = 7
    D[0][0] = 0.0
    anch_cache: dict[int, "np.ndarray"] = {}
    # 先把每個來源列 s 可用的各 bead 代價向量算好（j = 來源 en 位置）
    def src_costs(s: int):
        """→ list[(code, a, b, cost vector over j=0..m-b)]。"""
        out = []
        an = anchors(s)
        for code, (a, b) in enumerate(_BEAD_LIST):
            if s + a > n or b > m:
                continue
            if a == 1 and b == 0:
                out.append((code, a, b, np.full(m + 1, 4.0 + 0.002 * zn[s])))
                continue
            if a > 1 and zown is not None and zown[s] != zown[s + a - 1]:
                continue
            ks = zk[s:s + a]
            if len(set(ks.tolist())) > 1:
                continue
            L = m + 1 - b
            lz = ZP[s + a] - ZP[s]
            le = EP[b:m + 1] - EP[0:m + 1 - b]
            pen = {(1, 1): 0.0, (1, 2): 0.9, (2, 1): 0.9, (1, 3): 2.2, (3, 1): 2.2, (2, 2): 1.6}[(a, b)]
            c = np.abs(np.log((lz + 30.0) / (r * le + 30.0))) * 4.0 + pen
            c = c + np.concatenate([an, [0.0]])[:L] if b == 1 else c + np.concatenate([an, np.zeros(b)])[:L]
            ok = (ek[:L] == ks[0])
            if b > 1:
                ok = ok & ekrun[b][:L]
            c = np.where(ok, c, INF)
            out.append((code, a, b, c))
        return out

    cache: dict[int, list] = {}
    for i in range(1, n + 1):
        A = np.full(m + 1, INF)
        code_row = np.full(m + 1, -1, dtype=np.int8)
        for a in (1, 2, 3):
            s = i - a
            if s < 0:
                continue
            if s not in cache:
                cache[s] = src_costs(s)
            for code, aa, b, c in cache[s]:
                if aa != a:
                    continue
                if b == 0:
                    cand = D[s] + c
                    better = cand < A
                    A = np.where(better, cand, A)
                    code_row = np.where(better, code, code_row).astype(np.int8)
                else:
                    cand = D[s][:m + 1 - b] + c
                    seg = A[b:]
                    better = cand < seg
                    A[b:] = np.where(better, cand, seg)
                    code_row[b:] = np.where(better, code, code_row[b:]).astype(np.int8)
        # 釋放用不到的舊來源
        cache.pop(i - 4, None)
        # (0,1) 水平：D[j] = min(A[j], D[j-1]+c01[j-1])
        Ap = A - P
        cm = np.minimum.accumulate(Ap)
        Di = P + cm
        horiz = np.zeros(m + 1, dtype=bool)
        horiz[1:] = Di[1:] < A[1:] - 1e-9
        D[i] = Di
        bp[i] = np.where(horiz, 7, code_row)
    if not np.isfinite(D[n][m]):
        return [([i], []) for i in range(n)] + [([], [j]) for j in range(m)]
    rows = []
    i, j = n, m
    while i or j:
        code = int(bp[i][j])
        if code == 7:
            rows.append(([], [j - 1]))
            j -= 1
            continue
        a, b = _BEAD_LIST[code]
        rows.append((list(range(i - a, i)), list(range(j - b, j))))
        i, j = i - a, j - b
    return rows[::-1]


# ═══ 驅動：卷 → 檔群組 → 對齊 → 逐塊輸出 ═════════════════════════════════════

import json
import os
import statistics
from pathlib import Path

HEAD_RE = re.compile(
    r"^(?:#+\s*)?(?:(?:Psalm|Homily|Chapter|Book|Letter|Epistle|Tractate|Sermon|Discourse|Oration|"
    r"Treatise|Part|Section|Canon|Question|Argument|Exhortation|Hymn|Lecture|Catechetical|Appendix|"
    r"Elucidation|Preface|Introduction|Prolegomena|Fragment|Chapters?)\b|[IVXLC]+\.$)", re.I)


def heading_like(row: str) -> bool:
    t = row.strip()
    return kind_of(t) == "B" and len(t) <= 110 and bool(HEAD_RE.match(t))


def _norm(s: str | None) -> str:
    return re.sub(r"\s+", "", TAG_RE.sub("", (s or "").replace(EMPTY, "")))


def chunk_en_text(c: dict) -> str:
    return ((c.get("sources") or {}).get("en")) or (c.get("source_text") if (c.get("source_lang") or "en") == "en" else "") or ""


def load_rows(chunks: list[dict], bak: list[dict] | None):
    """每塊 (zh列, en列)。優先用 number_multilingual 之前的備份（列界保持原樣），條件是去標記後文字相同。"""
    bmap = {b.get("chunk_index"): b for b in (bak or [])}
    out = []
    for c in chunks:
        b = bmap.get(c.get("chunk_index"))
        zsrc, esrc = c.get("content"), chunk_en_text(c)
        if b is not None:
            if _norm(b.get("content")) == _norm(zsrc):
                zsrc = b.get("content")
            be = chunk_en_text(b)
            if _norm(be) == _norm(esrc):
                esrc = be
        zr, er = clean_rows(zsrc), clean_rows(esrc)
        if untranslated(c):
            # 「中文欄其實是英文」的塊（從來沒翻）：content 搬到英文列，中文清空，整塊進缺口表
            er = file_en([zr, er])[0] if er else zr
            zr = []
        out.append((zr, er))
    return out


def untranslated(c: dict) -> bool:
    from audit_fathers_coverage import zh_flags
    return bool(zh_flags(c.get("content") or "", 0)["untranslated"])


def group_chunks(chunks: list[dict]) -> list[list[int]]:
    groups: list[list[int]] = []
    for i, c in enumerate(chunks):
        if groups and c.get("title_en") and chunks[groups[-1][0]].get("title_en") == c.get("title_en"):
            groups[-1].append(i)
        else:
            groups.append([i])
    return groups


def file_en(rows_list: list[list[str]]) -> tuple[list[str], bool]:
    """群組的整檔英文列。依塊序合併各塊的英文：已在 E 裡的列當錨點，不在的列插在同塊前一個錨點之後
    （沒有前一個就插在後一個錨點之前，整塊都沒有錨點就接在最後）。
    ⇒ 整檔重複掛在每塊（dup）→ 得到那份整檔；各塊是不重疊的切片 → 依序串接；混合 → 也成立。
    判「已在 E 裡」用子字串（舊的重切會從列中間的頁碼標記切，切片頭尾是半列）。"""
    import bisect
    E: list[str] = []
    merged = False

    def index(E):
        keys = [_norm(x) for x in E]
        offs, acc = [], 0
        for k in keys:
            offs.append(acc)
            acc += len(k) + 1
        return keys, offs, "|".join(keys)

    for rows in rows_list:
        if not rows:
            continue
        keys, offs, big = index(E)
        hits: list[int | None] = []
        for x in rows:
            nx = _norm(x)
            h = None
            if nx in keys:
                h = keys.index(nx)
            elif len(nx) >= 24 and big:
                f = big.find(nx)
                if f >= 0:
                    h = bisect.bisect_right(offs, f) - 1
            hits.append(h)
        # 逐段處理：連續的缺列一起插
        n = len(rows)
        i = 0
        inserts: list[tuple[int, list[str]]] = []   # (插入位置, 列) 以舊 E 的索引為準
        while i < n:
            if hits[i] is not None:
                i += 1
                continue
            j = i
            while j < n and hits[j] is None:
                j += 1
            prev = next((hits[k] for k in range(i - 1, -1, -1) if hits[k] is not None), None)
            nxt = next((hits[k] for k in range(j, n) if hits[k] is not None), None)
            if prev is not None:
                pos = prev + 1
            elif nxt is not None:
                pos = nxt
            else:
                pos = len(E)
            inserts.append((pos, rows[i:j]))
            i = j
        for pos, rs in sorted(inserts, key=lambda t: -t[0]):
            E[pos:pos] = rs
            merged = True
    return E, merged


@dataclass
class GroupResult:
    chunk_ids: list[int]
    safe: bool
    ratio: float
    # 逐塊輸出：列 = (zh 文字或 None, en 文字或 None, kind)
    rows: dict[int, list[tuple[str | None, str | None]]] = field(default_factory=dict)
    gaps: list[tuple[int, int, str, str]] = field(default_factory=list)   # (chunk_idx, row_idx, kind, en)
    orphans: list[tuple[int, int, str, str]] = field(default_factory=list)  # (chunk_idx, row_idx, kind, zh)
    stats: dict = field(default_factory=dict)


def realign_group(zh_by_chunk: dict[int, list[str]], en_by_chunk: dict[int, list[str]],
                  cids: list[int], vol_r: float, E: list[str] | None = None) -> GroupResult:
    """一個檔群組：正文列與註文列**分開**各做一次對齊。

    為什麼分開：中文塊裡「註文塊」常夾在正文中間（正文、分隔線、註文、又一段正文），英文整檔卻是
    「全部正文、全部註文」或另一種夾法。單調 DP 吃不下這種列序不同，整段被當成「中文孤列＋英文缺口」
    （Matthew 講道集 #18：第 8、9 節中文就躺在註文塊後面，英文在前面）。分開之後各自單調，
    每塊輸出正文列在前、註文列在後（tidy_rows 再補一條分隔線）。"""
    if E is None:
        E = file_en([en_by_chunk[i] for i in cids])[0]
    EB = [e for e in E if kind_of(e) == "B"]
    EF = [e for e in E if kind_of(e) == "F"]
    ZB, ownB, ZF, ownF = [], [], [], []
    for i in cids:
        for z in zh_by_chunk[i]:
            k = kind_of(z)
            if k == "B":
                ZB.append(z)
                ownB.append(i)
            elif k == "F":
                ZF.append(z)
                ownF.append(i)
    zl = sum(_len_zh(z) for z in ZB)
    el = sum(_len_en(e) for e in EB)
    r = zl / el if el else vol_r
    if not (0.22 <= r <= 0.6):
        r = vol_r
    res = GroupResult(cids, True, r)
    alB = demote_bad(align(ZB, EB, r, zown=ownB), ZB, EB) if (ZB and EB) else (
        [([x], []) for x in range(len(ZB))] + [([], [x]) for x in range(len(EB))])
    zfl = sum(_len_zh(z) for z in ZF)
    efl = sum(_len_en(e) for e in EF)
    rf = zfl / efl if efl and zfl else 0.3
    rf = min(max(rf, 0.12), 0.9)
    alF = align(ZF, EF, rf, zown=ownF) if (ZF and EF) else (
        [([x], []) for x in range(len(ZF))] + [([], [x]) for x in range(len(EF))])

    rows: dict[int, list] = {i: [] for i in cids}

    def distribute(al, Z, Ez, own, head_rule: bool):
        seq = [(own[a[0]] if a else None, a, b) for a, b in al]
        prev = None
        to_next = False
        for k, (o, a, b) in enumerate(seq):
            if o is not None:
                prev = o
                to_next = False
                tgt = o
            else:
                nxt = next((x for x, _, _ in seq[k + 1:] if x is not None), None)
                if head_rule and heading_like(Ez[b[0]]):
                    to_next = True
                if prev is None:
                    tgt = nxt if nxt is not None else cids[0]
                elif nxt is not None and to_next:
                    tgt = nxt
                else:
                    tgt = prev
            zt = chr(10).join(Z[x] for x in a) if a else None
            et = chr(10).join(Ez[x] for x in b) if b else None
            rows[tgt].append((zt, et, len(b)))
        return seq

    seqB = distribute(alB, ZB, EB, ownB, True)
    seqF = distribute(alF, ZF, EF, ownF, False)
    res.rows = rows
    for i in cids:
        for ri, (zt, et, _n) in enumerate(rows[i]):
            if zt is None and et is not None:
                res.gaps.append((i, ri, kind_of(et.split(chr(10))[0]), et))
            elif et is None and zt is not None:
                res.orphans.append((i, ri, kind_of(zt.split(chr(10))[0]), zt))
    res.stats = {
        "beads": len(alB) + len(alF),
        "en_only_rows": sum(1 for _, a, b in seqB + seqF if not a),
        "zh_orphan_rows": sum(len(a) for _, a, b in seqB + seqF if not b),
        "zh_orphan_chars": sum(_len_zh(ZB[x]) for _, a, b in seqB if not b for x in a),
        "odd_pairs": sum(1 for _, a, b in seqB if a and b
                         and sum(_len_en(EB[x]) for x in b) > 200
                         and not (0.15 < sum(_len_zh(ZB[x]) for x in a) / sum(_len_en(EB[x]) for x in b) < 0.8)),
    }
    return res


# ═══ 錯位搶救：群組內單調對齊之後，卷內剩下的「沒配到英文的中文列」與「沒配到中文的英文列」
#     可能其實是同一段（中文被排在別處）。把兩串各自依卷序拉出來，再做一次對齊。

LAST_PAIRS: list[tuple[str, str]] = []


def rescue_orphans(results: list["GroupResult"], r: float):
    """原地修改 results[*].rows；回傳搬移紀錄 [(from_chunk, to_chunk, 中文字數)]。"""
    O: list[tuple[int, int]] = []
    G: list[tuple[int, int]] = []
    for res in results:
        for i in res.chunk_ids:
            for k, (zt, et, ne) in enumerate(res.rows.get(i, [])):
                if et is None and zt and kind_of(zt.split("\n")[0]) == "B":
                    O.append((id(res), i, k))
                elif zt is None and et and kind_of(et.split("\n")[0]) == "B":
                    G.append((id(res), i, k))
    if not O or not G:
        return []
    by_res = {id(res): res for res in results}
    Zt = [by_res[a].rows[b][c][0] for a, b, c in O]
    Et = [by_res[a].rows[b][c][1] for a, b, c in G]
    al = align(Zt, Et, r)
    moves = []
    drop: set[tuple[int, int, int]] = set()

    def lead_pair(bead):
        a, b = bead
        if not a or len(b) != 1:
            return None
        zl = feat(Zt[a[0]].split(chr(10))[0], True).lead
        el = feat(Et[b[0]].split(chr(10))[0], False).lead
        return (zl, el) if zl is not None and el is not None else None

    for k, (a, b) in enumerate(al):
        if not a or len(b) != 1:
            continue
        zt = chr(10).join(Zt[x] for x in a)
        et = Et[b[0]]
        lz, le = _len_zh(zt), _len_en(et)
        zf, ef = feat(zt.split(chr(10))[0], True), feat(et.split(chr(10))[0], False)
        ratio_ok = le < 120 or (0.2 <= lz / le <= 0.7)
        tight = le >= 120 and 0.27 <= lz / le <= 0.5
        if not ratio_ok:
            continue
        refs_ok = bool(zf.refs & ef.refs) or (zf.page is not None and zf.page == ef.page)
        lead_ok = zf.lead is not None and zf.lead == ef.lead
        # 段號相同還不夠（不同論著都有「45.」）：前後鄰居也得是同一對號（差 1）才信
        neigh = False
        if lead_ok:
            for nb in (k - 1, k + 1):
                if 0 <= nb < len(al):
                    lp = lead_pair(al[nb])
                    if lp and lp[0] == lp[1] and abs(lp[0] - zf.lead) == 1:
                        neigh = True
        if not (refs_ok or (neigh and tight)):
            continue
        gres, gi, gk = G[b[0]]
        by_res[gres].rows[gi][gk] = (zt, et, 1)
        LAST_PAIRS.append((zt, et))
        for x in a:
            drop.add(O[x])
            moves.append((O[x][1], gi, _len_zh(Zt[x])))
    # 刪掉被搬走的原列
    for res in results:
        for i in res.chunk_ids:
            rows = res.rows.get(i)
            if not rows:
                continue
            res.rows[i] = [row for k, row in enumerate(rows) if (id(res), i, k) not in drop]
    return moves


def demote_bad(al, Z: list[str], E: list[str]):
    """DP 為了「每列都要有去處」會硬配長度差太多或段號對不上的列。這種配對比留白更糟
    （畫面上看起來像對應）→ 拆回「中文孤列＋英文缺口」。"""
    out = []
    for a, b in al:
        if not a or not b:
            out.append((a, b))
            continue
        kz = kind_of(Z[a[0]])
        if kz != "B":
            out.append((a, b))
            continue
        lz = sum(_len_zh(Z[x]) for x in a)
        le = sum(_len_en(E[x]) for x in b)
        zl = feat(Z[a[0]], True).lead
        el = feat(E[b[0]], False).lead
        bad = False
        if le >= 150:
            r_ = lz / le
            if not (0.12 <= r_ <= 0.9):
                bad = True
            elif zl is not None and el is not None and zl != el and not (0.2 <= r_ <= 0.6):
                bad = True
        if not bad and len(b) > 1 and len(a) == 1 and le >= 150 and lz / le < 0.2:
            # 一段中文配兩三段英文、字數卻只夠其中一段：多半是相鄰那段根本沒譯，被合併吃掉了
            # → 只留長度最像的那一列，其餘放回缺口
            r0 = 0.34
            k = min(b, key=lambda x: abs(math.log((lz + 30) / (r0 * _len_en(E[x]) + 30))))
            lead_hit = [x for x in b if zl is not None and feat(E[x], False).lead == zl]
            if lead_hit:
                k = lead_hit[0]
            for x in b:
                out.append((a, [x]) if x == k else ([], [x]))
            continue
        if bad:
            out.append((a, []))
            out.append(([], b))
        else:
            out.append((a, b))
    return out
