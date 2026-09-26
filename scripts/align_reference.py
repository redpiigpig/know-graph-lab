#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""把館裡「已有的原文書」逐段對齊進「已有的中譯本」，讓 reader 能中／中英對照／英切換。

沿用既有對齊程式，不另起爐灶：
- 章節錨點解析仿 `align_editions.parse_chapter_number`（本檔擴充：多章節合併標題
  如 "Lectures IV and V"、CJK「講／回」關鍵字）。
- 段落層按長度比例分配沿用 `merge_original_column.distribute` / `split_paras`
  （原是泰勒《原始文化》／弗雷澤《金枝》那次「把英文原著併進既有中譯」的做法）。
- 寫回 JSONL＋推 R2 沿用 `standardize_ebook.push_to_r2`。

兩本書各自的切分粒度常常不同（英文一章一段、中文一頁一段甚至是 OCR 雜訊），
所以流程是兩層：

  1. 章節錨點對齊 —— 把兩邊的 chunk 序列各自「帶著走」分組成一串 block
     （見 `build_blocks`），block 的 key 是章節編號（可能不只一個，例如英文原著
     把「第四講、第五講」併成一個 chunk）。章節編號比對得上的兩邊 block 配對，
     配不上的另外處理（前後扉頁靠標題關鍵字配對／完全對不上就留白＋計入報告）。
  2. block 內段落層按累計字數比例分配英文段落給中譯的各個既有 chunk
     （不重寫中文、不改變中文 chunk 數）。

🚨 中譯的 `content` 一字不改。對不上的段落寧可留空，不可以硬配錯。

用法：

    python scripts/align_reference.py --orig-id <原文ebook_id> --zh-id <中譯ebook_id> --dry-run
    python scripts/align_reference.py --orig-id <原文ebook_id> --zh-id <中譯ebook_id> --apply
"""
from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import merge_original_column as moc  # noqa: E402  (distribute/split_paras 沿用)
# 注意：`standardize_ebook`（push_to_r2/ENV）只在 CLI I/O 函式內延遲 import，
# 讓本檔的純函式核心（extract_anchor_keys/build_blocks/align_book…）在沒有
# .env／沒有網路的測試環境下也能單獨載入、單獨測試。

STUDIO = Path(r"G:\我的雲端硬碟\資料\知識圖工作室")
CHUNKS_DIR = STUDIO / "_chunks"

# ============================================================================
# 1. 數字解析（羅馬數字／中文數字）
# ============================================================================

_ROMAN = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100, "d": 500, "m": 1000}
_CJK_DIGIT = {"零": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
              "六": 6, "七": 7, "八": 8, "九": 9}


def roman_to_int(s: str) -> int | None:
    """'IV' -> 4；不是合法羅馬數字回 None。"""
    s = s.lower().strip()
    if not s or any(c not in _ROMAN for c in s):
        return None
    total, prev = 0, 0
    for c in reversed(s):
        v = _ROMAN[c]
        total += -v if v < prev else v
        prev = max(prev, v)
    return total or None


def cjk_num_to_int(s: str) -> int | None:
    """'十二' -> 12；'二十一' -> 21。只管章節號會出現的範圍（1–999）。

    🚨 中文合章標題常把幾個章節編號直接串在一起、不加分隔（「第十六十七講」＝
    第十六講與第十七講合併，不是「第七十七講」）。單一合法的中文數字裡最多
    只會出現一個「十」（三百六十五也只有一個），出現兩個以上代表這其實是
    好幾個數字被串接，交給 `split_cjk_number_run` 拆開，這裡直接回 None
    （回傳一個看似合法但語意錯誤的大數字，比老實說『解析不出單一數字』更糟）。
    """
    s = s.strip()
    if not s:
        return None
    if s.isdigit():
        return int(s)
    if s.count("十") > 1:
        return None
    total, section, last_digit = 0, 0, 0
    for ch in s:
        if ch in _CJK_DIGIT:
            last_digit = _CJK_DIGIT[ch]
            section += last_digit
        elif ch == "十":
            section = section - last_digit + (last_digit or 1) * 10
            last_digit = 0
        elif ch == "百":
            section = (section or 1) * 100
            last_digit = 0
        else:
            return None
    total += section
    return total or None


_CJK_TOKEN_RE = re.compile(r"[一二三四五六七八九]?十[一二三四五六七八九]?|[一二三四五六七八九]")


def split_cjk_number_run(s: str) -> list[int]:
    """把『十六十七』『十一十二十三』這種沒有分隔符、其實是好幾個章節編號
    串接在一起的中文數字，拆回獨立整數列表。單一合法數字原樣包一層 list。"""
    n = cjk_num_to_int(s)
    if n is not None:
        return [n]
    out = []
    for m in _CJK_TOKEN_RE.finditer(s):
        v = cjk_num_to_int(m.group())
        if v is not None:
            out.append(v)
    return out


def parse_number_token(tok: str) -> int | None:
    tok = tok.strip()
    if not tok:
        return None
    if tok.isdigit():
        return int(tok)
    if all(c.lower() in _ROMAN for c in tok):
        return roman_to_int(tok)
    return cjk_num_to_int(tok)


# ============================================================================
# 2. 章節錨點抽取（可能不只一個 —— 「Lectures IV and V」要拆成兩把鑰匙）
# ============================================================================

_KIND_KEYWORDS = {
    "chapter": ("chapter", "chap", "lecture", "lect"),
    "part": ("part",),
    "book": ("book",),
    "section": ("section", "sec"),
}
_KEYWORD_TO_KIND = {kw: kind for kind, kws in _KIND_KEYWORDS.items() for kw in kws}
# 關鍵字後可以接（可選 s／句點）再接一串「羅馬數字或阿拉伯數字」，中間可用
# 逗號／and／&／to／- 串接多個（"Lectures IV and V" / "Lectures XI, XII and XIII"）。
_KEYWORD_RE = re.compile(
    r"\b(" + "|".join(sorted(_KEYWORD_TO_KIND, key=len, reverse=True)) + r")s?\.?\s+"
    r"((?:[IVXLCDM]+|\d+)(?:\s*(?:,|and|&|to|-)\s*(?:[IVXLCDM]+|\d+))*)\b",
    re.IGNORECASE,
)
_NUM_TOKEN_RE = re.compile(r"[IVXLCDM]+|\d+", re.IGNORECASE)

_CJK_KIND = {"章": "chapter", "講": "chapter", "回": "chapter",
             "節": "section", "篇": "part", "部": "part", "卷": "book"}
_CJK_RE = re.compile(r"第\s*([一二三四五六七八九十百零0-9]+)\s*([章節篇部卷講回])")
_SECTION_SIGN_RE = re.compile(r"§\s*(\d+)")
# 一個 chunk 就是一章、標題乾脆用「1. Religion and World-Construction」這種
# 「純數字＋句點」寫法（沒有 Chapter/Section 之類的關鍵字）。這個模式太容易
# 在正文／書目裡誤觸發（"3. xyz" 常常只是一條列舉），所以只在 chapter_path
# 這個「已經是乾淨標題欄位」時才啟用（見 `allow_bare`），不對內文開頭掃描。
_BARE_NUM_RE = re.compile(r"^\(?\s*([IVXLCDM]+|\d+)\s*[\.\)、]\s+\S")


def extract_anchor_keys(text: str, *, allow_bare: bool = False) -> list[tuple[str, int]]:
    """從一段文字（chapter_path 或 content 開頭）抽出章節錨點鍵，可能不只一個。

    'Chapter III. On Memory' -> [('chapter', 3)]
    'Lectures IV and V'      -> [('chapter', 4), ('chapter', 5)]
    '第一講 宗教與神經病學'   -> [('chapter', 1)]
    '§ 12'                   -> [('section', 12)]
    `allow_bare=True` 時額外接受 '1. Religion and World-Construction' 這種
    沒有關鍵字的純編號標題（只該對乾淨的標題欄位開，不要對內文開）。
    找不到 -> []
    """
    if not text:
        return []
    keys: list[tuple[str, int]] = []
    seen: set[tuple[str, int]] = set()

    for m in _CJK_RE.finditer(text):
        kind = _CJK_KIND.get(m.group(2), "chapter")
        for n in split_cjk_number_run(m.group(1)):
            k = (kind, n)
            if k not in seen:
                seen.add(k)
                keys.append(k)

    for m in _SECTION_SIGN_RE.finditer(text):
        k = ("section", int(m.group(1)))
        if k not in seen:
            seen.add(k)
            keys.append(k)

    for m in _KEYWORD_RE.finditer(text):
        kind = _KEYWORD_TO_KIND[m.group(1).lower()]
        # 拆解 "IV and V" / "XI, XII and XIII" 之類的多值串——先把連接詞換成
        # 逗號再切，逐個 token 要求「整串」都是合法羅馬數字或阿拉伯數字
        # （不能對子字串 findall，"and" 裡的 'd' 單獨看是合法羅馬數字 D=500）。
        seg = re.sub(r"(?i)\band\b|\bto\b", ",", m.group(2))
        for tok in re.split(r"[,&\-]+", seg):
            tok = tok.strip()
            if not tok:
                continue
            n = parse_number_token(tok)
            if n is None:
                continue
            k = (kind, n)
            if k not in seen:
                seen.add(k)
                keys.append(k)

    if not keys and allow_bare:
        m = _BARE_NUM_RE.match(text.strip())
        if m:
            n = parse_number_token(m.group(1))
            if n is not None:
                keys.append(("chapter", n))

    return keys


def anchor_text_for_chunk(chunk: dict, window: int = 250) -> str:
    """chunk 的『可能藏著章節錨點』的那一段文字：metadata 標題 + 內文開頭一小截。

    OCR 掃描書常把章節標題印成每頁書眉，混在內文最前面（不是獨立欄位），
    所以要看 content 的開頭，不能只看 chapter_path。只取開頭一截是為了不要在
    整本書裡隨機命中「提到第三章」這種正文敘述。
    """
    cp = (chunk.get("chapter_path") or "").strip()
    body = (chunk.get("content") or "")[:window]
    return f"{cp}\n{body}"


def anchor_keys_for_chunk(chunk: dict, window: int = 250) -> list[tuple[str, int]]:
    """一個 chunk 的章節錨點鍵：先看 chapter_path 這個乾淨欄位本身（允許純數字
    標題），找不到再退而掃 metadata+內文開頭那一小截（不允許純數字，避免正文
    裡的列舉句「3. xyz」被誤判成章節）。"""
    raw_title = (chunk.get("chapter_path") or "").strip()
    if raw_title:
        keys = extract_anchor_keys(raw_title, allow_bare=True)
        if keys:
            return keys
    return extract_anchor_keys(anchor_text_for_chunk(chunk, window))


# ============================================================================
# 3. Block：把 chunk 序列按「帶著走」規則分組
# ============================================================================

def build_blocks(chunks: list[dict], *, window: int = 250) -> list[dict]:
    """把 chunk 序列分成連續 block；同一個 block 內的 chunk 共用同一組錨點鍵。

    兩種各自獨立的「換新 block」訊號（互不取代，任一成立就換）：
    1. **編號錨點**：chunk 自己偵得到的章節鍵（見 `extract_anchor_keys`），且跟
       目前 block 的鍵不同 -> 開新 block。同一把鍵重複出現（OCR 書眉每頁都印
       一次同樣章名）不會被拆散，照樣併入目前 block。
    2. **原始標題換了**：chunk 自己的 `chapter_path` 欄位非空，且跟目前 block
       的標題不同——用來抓「沒有編號、但本來就是獨立一節」的段落，例如
       Endnotes／Bibliography／Appendix／Index 這種只有標題、沒有章節數字的
       扉頁或書後附件（它們在 `extract_anchor_keys` 底下不會出現任何鍵）。

    最前面兩者都偵不到的 chunk 會自成一個 keys=()／title="" 的 block（前扉頁）。

    回傳：[{"keys": tuple[(kind,num),...], "title": str, "chunks": [chunk,...]}, ...]
    """
    blocks: list[dict] = []
    cur_keys: tuple = ()
    cur_title: str = ""
    cur_chunks: list[dict] = []

    def flush():
        if cur_chunks:
            blocks.append({"keys": cur_keys, "title": cur_title, "chunks": list(cur_chunks)})

    for c in chunks:
        raw_title = (c.get("chapter_path") or "").strip()
        own = tuple(anchor_keys_for_chunk(c, window))
        new_block = bool(cur_chunks) and (
            (own and own != cur_keys)
            or (not own and raw_title and raw_title != cur_title)
        )
        if new_block:
            flush()
            cur_keys, cur_title, cur_chunks = own, raw_title, [c]
        else:
            if not cur_chunks:
                cur_keys, cur_title = own, raw_title
            cur_chunks.append(c)
    flush()
    return blocks


def chapter_zone(blocks: list[dict]) -> tuple[int, int]:
    """回傳 (第一個有章節鍵 block 的 index, 最後一個有章節鍵 block 的 index)。

    全部都沒有鍵時回 (-1, -1)。"""
    idxs = [i for i, b in enumerate(blocks) if b["keys"]]
    if not idxs:
        return (-1, -1)
    return (idxs[0], idxs[-1])


# ============================================================================
# 4. 前後扉頁分類（標題關鍵字 -> 種類），用來配對「序」「附錄」「參考書目」…
# ============================================================================

_ZONE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "cover": ("cover", "title page", "imprint", "colophon", "uncopyright",
              "封面", "版權", "出版資訊", "扉頁"),
    "toc": ("contents", "目錄", "目录"),
    "preface": ("preface", "foreword", "introduction", "dedication",
                "前言", "序言", "導讀", "导读", "獻詞", "献词"),
    "translator_note": ("译者序", "譯者序", "译后记", "譯後記",
                         "出版說明", "出版说明", "编者序", "編者序", "译者按", "譯者按"),
    "postscript": ("postscript", "conclusion", "後記", "后记", "跋", "結語", "结语"),
    "notes": ("notes", "endnotes", "footnotes", "尾註", "尾注",
              "注釋", "注释", "附註", "附注"),
    "bibliography": ("bibliography", "references", "works cited",
                      "參考書目", "参考书目", "引用文獻", "引用文献", "書目", "书目"),
    "appendix": ("appendix", "附錄", "附录"),
    "index": ("index", "索引"),
}


def classify_zone(title: str) -> str | None:
    """標題／chapter_path -> 種類（cover/toc/preface/...），對不上回 None。"""
    if not title:
        return None
    t = title.strip().lower()
    if re.fullmatch(r"[a-z]", t):
        # 書後索引常按字母分組，各節標題只是單一字母（A/B/C/…），沒有
        # 「Index」字樣可以配 _ZONE_KEYWORDS，靠這條單一大寫字母的形狀認出來。
        return "index"
    for zone, kws in _ZONE_KEYWORDS.items():
        for kw in kws:
            if kw.lower() in t:
                return zone
    return None


def block_title(block: dict) -> str:
    if block.get("title"):
        return block["title"]
    for c in block["chunks"]:
        cp = (c.get("chapter_path") or "").strip()
        if cp:
            return cp
    # 沒有 chapter_path 就退而求其次看內文開頭一小段
    if block["chunks"]:
        return (block["chunks"][0].get("content") or "")[:40]
    return ""


# ============================================================================
# 5. 譯者註標記統一
# ============================================================================

_TRANSLATOR_NOTE_RE = re.compile(
    r"(?:^|(?<=[。\n]))\s*[〔(（]?\s*(?:译者按|譯者按|译者注|譯者注|译注|譯注|译按|譯按)\s*[:：)）〕]?\s*"
)


def normalize_translator_notes(text: str) -> tuple[str, int]:
    """把 (译者注：/譯者按：/译按 …) 各種寫法統一成「〔譯注〕」。回傳 (新文字, 取代次數)。

    只認位於句首／行首的譯者註起手式，避免誤殺正文裡「作者提到譯者」這類敘述
    （那些不會出現在 `(?:^|(?<=[。\n]))` 這個邊界之後）。"""
    count = 0

    def _sub(m: re.Match) -> str:
        nonlocal count
        count += 1
        return "〔譯注〕"

    new_text = _TRANSLATOR_NOTE_RE.sub(_sub, text)
    return new_text, count


# ============================================================================
# 6. 註腳：逐條配對（找得到編號標記時）／否則交給長度比例分配
# ============================================================================

_FOOTNOTE_ENTRY_RE = re.compile(r"^\s*(\d{1,4})[\.\)、]\s+", re.M)
_FOOTNOTE_REF_RE = re.compile(r"\[\^(\d+)\]|〔(\d+)〕|\((\d+)\)")


def extract_footnote_entries(text: str) -> dict[int, str]:
    """把一大塊『N. 註文…』的尾註/註釋文字切成 {編號: 內容}。"""
    matches = list(_FOOTNOTE_ENTRY_RE.finditer(text))
    out: dict[int, str] = {}
    for i, m in enumerate(matches):
        n = int(m.group(1))
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out[n] = text[start:end].strip()
    return out


def find_footnote_refs(text: str) -> set[int]:
    """在中譯 chunk 內文裡找『[^N]』/『〔N〕』/『(N)』這類註腳參照標記。"""
    refs: set[int] = set()
    for m in _FOOTNOTE_REF_RE.finditer(text or ""):
        for g in m.groups():
            if g:
                refs.add(int(g))
                break
    return refs


# ============================================================================
# 7. Block 級對齊主流程
# ============================================================================

def _flat_len(chunks: list[dict]) -> int:
    return sum(len(c.get("content") or "") for c in chunks) or 1


def align_chapter_blocks(en_blocks: list[dict], zh_blocks: list[dict]) -> dict:
    """章節區的核心：把有章節鍵的 en block 對到 zh 的對應章節 chunk 群，
    段落層按累計字數比例分配。回傳 {"filled": [...更新後的 zh chunk...],
    "matched_chapters": int, "gap_chapters": [(keys, n_zh_chunks), ...]}。
    """
    zh_by_key: dict[tuple, list[dict]] = {}
    zh_key_order: list[tuple] = []
    for b in zh_blocks:
        if not b["keys"]:
            continue
        for k in b["keys"]:
            if k not in zh_by_key:
                zh_by_key[k] = []
                zh_key_order.append(k)
            zh_by_key[k].extend(b["chunks"])

    used_keys: set[tuple] = set()
    matched = 0
    gaps: list[tuple] = []

    for b in en_blocks:
        if not b["keys"]:
            continue
        members: list[dict] = []
        seen_ids = set()
        for k in b["keys"]:
            for c in zh_by_key.get(k, []):
                if id(c) not in seen_ids:
                    seen_ids.add(id(c))
                    members.append(c)
        if not members:
            gaps.append((b["keys"], 0))
            continue
        if any(k in used_keys for k in b["keys"]):
            continue  # 這組鍵已經被前一個 en block 用掉，避免重複覆寫
        used_keys.update(b["keys"])

        en_text = "\n\n".join(c.get("content") or "" for c in b["chunks"])
        title_words = set(re.findall(r"[A-Za-z]{3,}", en_text[:400]))
        cleaned = moc.strip_running_heads(en_text, title_words) if title_words else en_text
        paras = moc.split_paras(cleaned)
        weights = [len(m.get("content") or "") or 1 for m in members]
        parts = moc.distribute(paras, weights)
        for m, p in zip(members, parts):
            m["source_text"] = p
            m["source_lang"] = "en"
        matched += 1

    return {"matched_chapters": matched, "gap_chapters": gaps,
            "zh_key_order": zh_key_order, "zh_by_key": zh_by_key,
            "used_keys": used_keys}


def align_front_back(en_blocks: list[dict], zh_blocks: list[dict],
                      en_lo: int, en_hi: int, zh_lo: int, zh_hi: int) -> dict:
    """扉頁／書末（前於第一章或後於最後一章的 block）配對。

    先照 `classify_zone` 關鍵字配對（序⇆preface、附錄⇆appendix…），
    同種類配不上的再照位置順序配對；剩下的：
    - en 有、zh 沒有 -> 記一筆「刪節／未收錄」（index 除外，直接略過）
    - zh 有、en 沒有 -> 標 zh_only
    """
    def outside(blocks, lo, hi):
        if lo < 0:
            return list(range(len(blocks)))
        return [i for i in range(len(blocks)) if i < lo or i > hi]

    en_idx = outside(en_blocks, en_lo, en_hi)
    zh_idx = outside(zh_blocks, zh_lo, zh_hi)

    en_by_zone: dict[str | None, list[int]] = {}
    for i in en_idx:
        en_by_zone.setdefault(classify_zone(block_title(en_blocks[i])), []).append(i)
    zh_by_zone: dict[str | None, list[int]] = {}
    for i in zh_idx:
        zh_by_zone.setdefault(classify_zone(block_title(zh_blocks[i])), []).append(i)

    paired: list[tuple[int, int]] = []
    used_en, used_zh = set(), set()
    for zone, en_list in en_by_zone.items():
        if zone is None:
            continue
        zh_list = zh_by_zone.get(zone, [])
        for a, b in zip(en_list, zh_list):
            paired.append((a, b))
            used_en.add(a)
            used_zh.add(b)

    # 剩下的按原順序位置配對（同樣種類都是 None 或種類數目不對等時的兜底）
    remain_en = [i for i in en_idx if i not in used_en]
    remain_zh = [i for i in zh_idx if i not in used_zh]
    for a, b in zip(remain_en, remain_zh):
        paired.append((a, b))
        used_en.add(a)
        used_zh.add(b)

    omitted: list[dict] = []  # en-only：中譯本沒收錄
    zh_only: list[dict] = []  # zh-only：中譯本獨有

    for a, b in paired:
        en_block, zh_block = en_blocks[a], zh_blocks[b]
        en_text = "\n\n".join(c.get("content") or "" for c in en_block["chunks"])
        paras = moc.split_paras(en_text)
        members = zh_block["chunks"]
        weights = [len(m.get("content") or "") or 1 for m in members]
        parts = moc.distribute(paras, weights)
        for m, p in zip(members, parts):
            m["source_text"] = p
            m["source_lang"] = "en"

    for i in en_idx:
        if i in used_en:
            continue
        zone = classify_zone(block_title(en_blocks[i]))
        if zone == "index":
            continue  # 索引可以略過，不計刪節
        omitted.append({"title": block_title(en_blocks[i])[:80], "zone": zone,
                         "chars": _flat_len(en_blocks[i]["chunks"])})

    for i in zh_idx:
        if i in used_zh:
            continue
        for c in zh_blocks[i]["chunks"]:
            c["zh_only"] = True
            cp = (c.get("chapter_path") or "").strip()
            if cp and "（中譯本獨有）" not in cp:
                c["chapter_path"] = f"{cp}（中譯本獨有）"
        zh_only.append({"title": block_title(zh_blocks[i])[:80],
                         "n_chunks": len(zh_blocks[i]["chunks"])})

    return {"omitted": omitted, "zh_only": zh_only}


def align_notes(en_blocks: list[dict], zh_blocks: list[dict]) -> dict:
    """章節錨點對完之後，另外找『notes/尾註』種類的 block 做逐條配對。

    註腳的「參照標記」([^N]／〔N〕／(N)) 可能出現在正文任何一個既有 chunk 裡
    （superscript 就地標號，註文另外集中在書後），所以找標記要掃**全書**的中譯
    chunk，不能只掃被分類成 notes 種類的那幾個 block。找得到標記時按編號精確
    配對；找不到任何標記就交給 `align_front_back` 的長度比例兜底（那邊已經
    處理過了，這裡只回報統計數字，不重複寫入）。
    """
    en_notes_blocks = [b for b in en_blocks if classify_zone(block_title(b)) == "notes"]
    if not en_notes_blocks:
        return {"original_footnotes": 0, "retained_in_translation": 0,
                "numbered_pairing": False}

    en_text = "\n\n".join(
        c.get("content") or "" for b in en_notes_blocks for c in b["chunks"])
    entries = extract_footnote_entries(en_text)
    original_n = len(entries)

    zh_chunks = [c for b in zh_blocks for c in b["chunks"]]
    all_refs: set[int] = set()
    for c in zh_chunks:
        all_refs |= find_footnote_refs(c.get("content") or "")

    if not all_refs:
        return {"original_footnotes": original_n,
                "retained_in_translation": None,  # 無法判定，長度比例已兜底
                "numbered_pairing": False}

    matched_refs = all_refs & set(entries)
    for c in zh_chunks:
        refs = find_footnote_refs(c.get("content") or "")
        hit = refs & set(entries)
        if hit:
            note_text = "\n\n".join(entries[n] for n in sorted(hit))
            existing = (c.get("source_text") or "").strip()
            c["source_text"] = f"{existing}\n\n{note_text}".strip() if existing else note_text
            c["source_lang"] = "en"

    return {"original_footnotes": original_n,
            "retained_in_translation": len(matched_refs),
            "numbered_pairing": True}


def align_book(en_chunks: list[dict], zh_chunks: list[dict], *,
               window: int = 250, apply_translator_notes: bool = True) -> dict:
    """全書對齊主流程。回傳 {"zh_chunks": [...], "report": {...}}。

    `zh_chunks` 是深拷貝過的（不動呼叫端傳進來的原始 list），只有這裡回傳的
    才帶 source_text/zh_only 等新欄位。"""
    zh = [dict(c) for c in zh_chunks]  # 淺拷貝每個 chunk dict，不動呼叫端
    en = [dict(c) for c in en_chunks]

    tn_count = 0
    if apply_translator_notes:
        for c in zh:
            new_content, n = normalize_translator_notes(c.get("content") or "")
            if n:
                c["content"] = new_content
                tn_count += n

    en_blocks = build_blocks(en, window=window)
    zh_blocks = build_blocks(zh, window=window)

    en_lo, en_hi = chapter_zone(en_blocks)
    zh_lo, zh_hi = chapter_zone(zh_blocks)

    ch_result = align_chapter_blocks(en_blocks, zh_blocks)
    fb_result = align_front_back(en_blocks, zh_blocks, en_lo, en_hi, zh_lo, zh_hi)
    notes_result = align_notes(en_blocks, zh_blocks)

    n_zh = len(zh)
    n_filled = sum(1 for c in zh if (c.get("source_text") or "").strip())
    n_zh_only = sum(1 for c in zh if c.get("zh_only"))

    en_chapter_blocks = [b for b in en_blocks if b["keys"]]
    zh_chapter_keys = {k for b in zh_blocks for k in b["keys"]}
    en_keys_flat = {k for b in en_chapter_blocks for k in b["keys"]}
    chapter_hit = len(en_keys_flat & zh_chapter_keys)
    chapter_total = len(en_keys_flat) or 1

    report = {
        "zh_total_chunks": n_zh,
        "zh_filled_chunks": n_filled,
        "zh_paragraph_coverage": round(n_filled / n_zh, 4) if n_zh else 0.0,
        "zh_only_chunks": n_zh_only,
        "chapter_anchor_hit": chapter_hit,
        "chapter_anchor_total": chapter_total,
        "chapter_coverage": round(chapter_hit / chapter_total, 4),
        "gap_chapters": ch_result["gap_chapters"],
        "omitted_in_translation": fb_result["omitted"],
        "zh_only_sections": fb_result["zh_only"],
        "translator_notes_normalized": tn_count,
        "footnotes": notes_result,
    }
    return {"zh_chunks": zh, "report": report}


# ============================================================================
# 8. CLI I/O 層（讀 Drive／R2、寫回＋備份＋推 R2、dry-run 報告）
# ============================================================================

def load_jsonl(ebook_id: str, *, timeout: int = 30) -> list[dict]:
    """優先讀 Drive `_chunks/{id}.jsonl`；沒有就退而讀 R2。"""
    p = CHUNKS_DIR / f"{ebook_id}.jsonl"
    if p.exists():
        return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    import boto3
    se_mod = _load_se()
    c = boto3.client("s3", region_name="auto", endpoint_url=se_mod.ENV["R2_ENDPOINT"],
                      aws_access_key_id=se_mod.ENV["R2_ACCESS_KEY"],
                      aws_secret_access_key=se_mod.ENV["R2_SECRET_KEY"],
                      config=__import__("botocore").config.Config(
                          connect_timeout=timeout, read_timeout=timeout))
    key = f"ebook-chunks/{ebook_id}.jsonl.gz"
    raw = c.get_object(Bucket=se_mod.ENV["R2_BUCKET"], Key=key)["Body"].read()
    text = gzip.decompress(raw).decode("utf-8")
    return [json.loads(l) for l in text.splitlines() if l.strip()]


def _load_se():
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    import standardize_ebook as se  # noqa: WPS433
    return se


def fetch_ebook_meta(ebook_id: str, *, timeout: int = 15) -> dict:
    import requests
    se_mod = _load_se()
    url = se_mod.ENV["SUPABASE_URL"].rstrip("/")
    key = se_mod.ENV["SUPABASE_SERVICE_ROLE_KEY"]
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    r = requests.get(f"{url}/rest/v1/ebooks", params={
        "id": f"eq.{ebook_id}", "select": "id,title,author,original_title",
        "limit": "1"}, headers=headers, timeout=timeout)
    r.raise_for_status()
    rows = r.json()
    return rows[0] if rows else {}


def write_jsonl_with_backup(ebook_id: str, rows: list[dict]) -> Path:
    """寫回 Drive，寫入前留 `.jsonl.align.bak` 備份（已有備份就不再覆蓋，
    避免多次重跑把最早的原始版本蓋掉）。"""
    out_path = CHUNKS_DIR / f"{ebook_id}.jsonl"
    bak_path = CHUNKS_DIR / f"{ebook_id}.jsonl.align.bak"
    if out_path.exists() and not bak_path.exists():
        bak_path.write_bytes(out_path.read_bytes())
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
        encoding="utf-8")
    return out_path


def push_and_patch(ebook_id: str, out_path: Path, rows: list[dict], *, timeout: int = 30) -> None:
    se_mod = _load_se()
    se_mod.push_to_r2(ebook_id, out_path)
    import requests
    url = se_mod.ENV["SUPABASE_URL"].rstrip("/")
    key = se_mod.ENV["SUPABASE_SERVICE_ROLE_KEY"]
    headers = {"apikey": key, "Authorization": f"Bearer {key}",
               "Content-Type": "application/json"}
    total_chars = sum(len(r.get("content") or "") for r in rows)
    from datetime import datetime, timezone
    patch = {"total_chars": total_chars,
              "standardized_at": datetime.now(timezone.utc).isoformat()}
    requests.patch(f"{url}/rest/v1/ebooks", params={"id": f"eq.{ebook_id}"},
                    headers=headers, json=patch, timeout=timeout).raise_for_status()


def _sample_pairs(zh_chunks: list[dict], n: int = 5, cap: int = 80) -> list[dict]:
    """抽樣（預設 5 對）給人核對，每段截 `cap` 字，避免把整本書內容灌進報告。"""
    candidates = [c for c in zh_chunks if (c.get("source_text") or "").strip()
                  and not c.get("zh_only")]
    if not candidates:
        return []
    step = max(1, len(candidates) // n)
    picks = candidates[::step][:n]
    out = []
    for c in picks:
        out.append({
            "chunk_index": c.get("chunk_index"),
            "chapter_path": (c.get("chapter_path") or "")[:60],
            "zh": (c.get("content") or "")[:cap],
            "en": (c.get("source_text") or "")[:cap],
        })
    return out


def print_report(orig_id: str, zh_id: str, report: dict, samples: list[dict]) -> None:
    print(f"\n=== 對齊報告：原文 {orig_id} → 中譯 {zh_id} ===")
    print(f"中譯 chunk 總數：{report['zh_total_chunks']}")
    print(f"章節錨點對上：{report['chapter_anchor_hit']}/{report['chapter_anchor_total']}"
          f"（{report['chapter_coverage']*100:.1f}%）")
    print(f"段落配到原文：{report['zh_filled_chunks']}/{report['zh_total_chunks']}"
          f"（{report['zh_paragraph_coverage']*100:.1f}%）")
    print(f"中譯本獨有段落：{report['zh_only_chunks']}")
    if report["gap_chapters"]:
        print(f"對不上的章節（原文有、中譯本找不到對應）：{len(report['gap_chapters'])}")
        for keys, _ in report["gap_chapters"][:10]:
            print(f"    缺：{keys}")
    if report["omitted_in_translation"]:
        print(f"中譯本整段刪節（原文有，中譯本沒收）：{len(report['omitted_in_translation'])}")
        for o in report["omitted_in_translation"]:
            print(f"    刪節：[{o['zone']}] {o['title']}（原文約 {o['chars']} 字）")
    if report["zh_only_sections"]:
        print(f"中譯本獨有小節：{len(report['zh_only_sections'])}")
        for z in report["zh_only_sections"]:
            print(f"    獨有：{z['title']}（{z['n_chunks']} 段）")
    if report["translator_notes_normalized"]:
        print(f"譯者註標記統一：{report['translator_notes_normalized']} 處 → 〔譯注〕")
    fn = report["footnotes"]
    if fn["original_footnotes"]:
        print(f"原文註腳／尾註共 {fn['original_footnotes']} 條；"
              f"中譯本逐條配對{'可行' if fn['numbered_pairing'] else '不可行（無編號標記，已用長度比例兜底）'}"
              + (f"，保留 {fn['retained_in_translation']} 條"
                 if fn["retained_in_translation"] not in (None,) else ""))
    print(f"\n抽樣 {len(samples)} 對（各截 80 字）：")
    for i, s in enumerate(samples, 1):
        print(f"  [{i}] {s['chapter_path']}")
        print(f"      中：{s['zh']}")
        print(f"      英：{s['en']}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--orig-id", required=True, help="原文書 ebook_id")
    ap.add_argument("--zh-id", required=True, help="中譯書 ebook_id")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--window", type=int, default=250)
    ap.add_argument("--samples", type=int, default=5)
    ap.add_argument("--engine", default="auto",
                    help="保留給日後低覆蓋率時的 LLM 輔助錨定（目前兩本 pilot 用純規則已足夠）")
    args = ap.parse_args()

    print(f"讀取原文 {args.orig_id} …")
    en = load_jsonl(args.orig_id)
    print(f"讀取中譯 {args.zh_id} …")
    zh = load_jsonl(args.zh_id)
    print(f"原文 {len(en)} chunks／中譯 {len(zh)} chunks")

    result = align_book(en, zh, window=args.window)
    samples = _sample_pairs(result["zh_chunks"], n=args.samples)
    print_report(args.orig_id, args.zh_id, result["report"], samples)

    if args.apply:
        rows = result["zh_chunks"]
        out_path = write_jsonl_with_backup(args.zh_id, rows)
        print(f"\n寫回 Drive：{out_path}（備份：{out_path}.align.bak）")
        push_and_patch(args.zh_id, out_path, rows)
        print("已推 R2 並更新 ebooks.total_chars/standardized_at")
    elif not args.dry_run:
        print("\n（未指定 --apply，僅印報告；加 --apply 才寫回）")


if __name__ == "__main__":
    main()
