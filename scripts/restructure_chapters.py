#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""單語書 → 「一章一頁、章 ##／節 ###、段號 {{s:章-節-段}}」（2026-09-29 使用者定的全館規格）。

中外對照書走 rebuild_reference_bilingual.py；這支只處理沒有 source_text／sources 的圖書館藏書
（全集 collection=collected-works 另走全集閱讀器，不在這裡）。

只動章節結構可靠的書，其餘跳過並記原因（寧可不做也不要做壞）：
  - 用 audit_toc_accuracy.audit() 現場重判，帶 NO_TOC／BODY_AS_TITLE／RUNNING_HEADER／JUNK_TITLE／
    PRINTED_TOC_MISS／SEQ_BROKEN／THIN_TEXT 任一旗標就跳過；
  - 同一章名在書中不連續出現（切錯）、全書少於 2 章、合併後單章超過 MAX_CHAPTER 字 → 跳過；
  - 寫回前做「內容守恆」檢查：去掉標記、標題井號、註號後的字元數，改前改後差距超過 0.5% 就不寫。

每本做的事：
  1. 同一章（chapter_path 第一層）的連續各塊合成一塊；chapter_path 只留章名，chunk_type=chapter；
  2. 章名成 `## 章名`、節名（chapter_path 第二層）成 `### 節名`：先剝掉正文開頭黏著或重複的標題，
     節名在該塊內找段首位置插入，找不到才放在該塊開頭；塊內其他 `##` 降為 `###`；
  3. 各塊註釋抽出集中到章末，被註釋切斷的段落接回；合併後註號重複就逐塊重編；
  4. 段號只數正文段（標題、註釋、只有頁碼標記或分隔符號的段不數）；
  5. 封面／版權頁／目錄等前附頁原樣不動、不編號。

章的段號前綴（全書一致、不重複）：
  - 過半的正文章有編號（第N章／Chapter N／「3.」）→ 編號模式：有號的用號，其餘用短名（≤6 字）或章名前 4 字；
  - 否則序號模式：正文章依序 1、2、3…，序／導論／結論／附錄這類短名用自己的名稱。

用法：
  python -X utf8 scripts/restructure_chapters.py --dry-run [--limit N]    # 全館判讀，出報告
  python -X utf8 scripts/restructure_chapters.py --show <id>               # 印一本改後的樣子
  python -X utf8 scripts/restructure_chapters.py --apply --ids ids.txt     # 寫回（JSONL＋R2＋DB，留 .bak_restructure）
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rebuild_reference_bilingual as rb  # noqa: E402

CH = rb.CHUNKS
OUT = Path(__file__).resolve().parents[1] / "output" / "restructure"
MAX_CHAPTER = 150_000
BAD_FLAGS = {"NO_TOC", "BODY_AS_TITLE", "RUNNING_HEADER", "JUNK_TITLE", "PRINTED_TOC_MISS", "SEQ_BROKEN", "THIN_TEXT"}
FRONT = {"封面", "出版資訊", "出版說明", "版權頁", "版權資訊", "扉頁", "目錄", "目次", "目　錄", "目　次",
         "圖目次", "表目次", "Contents", "Table of Contents", "CONTENTS", "索引", "Index", "INDEX", "Copyright"}
HEAD_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.S)
FN_ITEM = re.compile(r"^\((\d+)\)\s")
CJK_NUM = {c: i for i, c in enumerate("〇一二三四五六七八九")} | {"零": 0, "兩": 2}


def cjk_int(s: str) -> int | None:
    if s.isdigit():
        return int(s)
    total, cur = 0, 0
    for ch in s:
        if ch in CJK_NUM:
            cur = CJK_NUM[ch]
        elif ch == "十":
            total += (cur or 1) * 10
            cur = 0
        elif ch == "百":
            total += (cur or 1) * 100
            cur = 0
        else:
            return None
    return total + cur


def roman(s: str) -> int | None:
    vals = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}
    s = s.upper()
    if not s or any(c not in vals for c in s):
        return None
    n = 0
    for a, b in zip(s, s[1:] + " "):
        n += -vals[a] if b != " " and vals[a] < vals[b] else vals[a]
    return n


def chapter_number(title: str) -> int | None:
    t = re.sub(r"[*_<>/u]|\[\^\d+\]", "", title).strip()
    m = re.match(r"^第\s*([0-9〇零一二兩三四五六七八九十百]+)\s*[章講篇回課]", t)
    if m:
        return cjk_int(m.group(1))
    m = re.match(r"^(?:Chapter|CHAPTER|Lecture|LECTURE)\s+([0-9]+|[IVXLCivxlc]+)\b", t)
    if m:
        g = m.group(1)
        return int(g) if g.isdigit() else roman(g)
    m = re.match(r"^(\d{1,3})\s*[.、．:：]\s*\S", t)
    return int(m.group(1)) if m else None


PART_NAME = re.compile(
    r"^(總導讀|導讀|中譯本序|中譯序|中文版序|譯者序|推薦序|出版說明|自序|序言|代序|序|前言|導論|導言|緒論|引言|"
    r"結論|結語|後記|跋|譯後記|譯序|謝辭|致謝|"
    r"附錄[一二三四五六七八九十0-9A-Za-z]*|Preface|Foreword|Introduction|Conclusions?|Epilogue|Afterword|"
    r"Acknowledg(?:e)?ments?|Appendix(?:\s*[A-Z0-9]+)?)", re.I)


def short_name(title: str) -> str | None:
    """序／導論／結論／附錄這類非編號部分的名稱；一般章名不算（短篇集的篇名要用序號）。"""
    m = PART_NAME.match(re.sub(r"^[\s　*_#<>]+", "", title))
    return re.sub(r"\s", "", m.group(1)) if m else None


def chapter_labels(titles: list[str]) -> list[str]:
    """正文章的段號前綴：全書一致、不重複。"""
    nums = [chapter_number(t) for t in titles]
    numbered_mode = sum(n is not None for n in nums) * 2 > len(titles)
    labels, ordinal = [], 0
    for t, n in zip(titles, nums):
        if numbered_mode:
            lab = str(n) if n is not None else (short_name(t) or re.sub(r"\s", "", t)[:4])
        elif short_name(t) and n is None:
            lab = short_name(t)
        else:
            ordinal += 1
            lab = str(ordinal)
        labels.append(re.sub(r"[{}\s]", "", lab) or "章")
    seen: collections.Counter = collections.Counter()
    out = []
    for lab in labels:
        seen[lab] += 1
        out.append(lab if seen[lab] == 1 else f"{lab}({seen[lab]})")
    return out


def norm(s: str) -> str:
    return re.sub(r"[\s　*_#<>/|]|\[\^\d+\]|\{\{p:[^}]*\}\}|</?u>", "", s)


def strip_leading_titles(text: str, titles: list[str]) -> str:
    """剝掉塊首黏著或重複的標題（可能帶井號、可能連打兩次、可能黏著正文）。"""
    changed = True
    while changed:
        changed = False
        lead = re.match(r"((?:\{\{p:[^}]*\}\}|\s)*)", text).group(1)
        rest = text[len(lead):]
        m = HEAD_RE.match(rest.split("\n\n", 1)[0])
        if m and norm(m.group(2)) and any(norm(m.group(2)) == norm(t) for t in titles):
            text = lead + rest.split("\n\n", 1)[1] if "\n\n" in rest else lead
            changed = True
            continue
        first = rest.split("\n\n", 1)[0]
        for t in titles:
            if norm(t) and norm(first) == norm(t):
                text = lead + (rest.split("\n\n", 1)[1] if "\n\n" in rest else "")
                changed = True
                break
            if norm(t) and len(norm(t)) >= 2:
                cut = rb.cut_prefix(rest, t)
                if cut != rest:
                    text = lead + cut
                    changed = True
                    break
    return text


def split_notes_keep_order(text: str) -> tuple[list[str], list[str]]:
    """一塊 → (正文段落, 註釋條目)。分隔線之間的、以及以 (N) 起頭的段都算註。"""
    body, notes, in_notes = [], [], False
    for p in rb.paras(text):
        if rb.FOOT_RULE_RE.match(p):
            in_notes = not in_notes
            continue
        if HEAD_RE.match(p):
            in_notes = False
            body.append(p)
        elif in_notes or FN_ITEM.match(p):
            if FN_ITEM.match(p) or not notes:
                notes.append(p)
            else:
                notes[-1] += "\n\n" + p
        else:
            body.append(p)
    return body, notes


def renumber(body: list[str], notes: list[str], offset: int) -> tuple[list[str], list[str], int]:
    """把一塊內的註號整體平移 offset（合併後註號才不會重複）。回傳新的 offset。"""
    nums = [int(FN_ITEM.match(n).group(1)) for n in notes if FN_ITEM.match(n)]
    if not offset or not nums:
        return body, notes, offset + (max(nums) if nums else 0)
    sub = lambda m: f"[^{int(m.group(1)) + offset}]"  # noqa: E731
    body = [re.sub(r"\[\^(\d+)\]", sub, p) for p in body]
    notes = [FN_ITEM.sub(lambda m: f"({int(m.group(1)) + offset}) ", n, count=1) for n in notes]
    return body, notes, offset + max(nums)


def is_countable(p: str) -> bool:
    """要編段號的正文段：不是標題、分隔線、章末 [N] 註、只剩頁碼標記的段、或「一」「上篇」這類小段標記。"""
    bare = rb.PAGE_MARK_RE.sub("", p).strip()
    if HEAD_RE.match(p) or rb.FOOT_RULE_RE.match(p) or not re.search(r"\w", bare):
        return False
    if re.match(r"^\[\d+\]", bare):
        return False
    return not (len(bare) <= 6 and not re.search(r"[。，、；：！？.,;:!?「」“”\"']", bare))


def clean_title(t: str) -> str:
    """章名去掉 markdown 殘渣：開頭井號、粗體星號、<u> 標籤。"""
    t = re.sub(r"</?u>|\*\*|__", "", t or "")
    return re.sub(r"^#+\s*", "", t).strip()


JUNK_TITLE = re.compile(r"[Ͱ-ϿЀ-ӿ]|[一-鿿][A-Za-z](?![A-Za-z])|(?<![A-Za-z])[A-Za-z][一-鿿]")


def build_chapter(label: str, top: str, cs: list[dict], known: dict) -> str:
    out: list[str] = [f"## {top}"]
    all_notes: list[str] = []
    offset = 0
    need_renumber = False
    seen_nums: set[int] = set()
    for c in cs:
        for n in split_notes_keep_order(c.get("content") or "")[1]:
            m = FN_ITEM.match(n)
            if m and int(m.group(1)) in seen_nums:
                need_renumber = True
            if m:
                seen_nums.add(int(m.group(1)))
    cur_sec = None
    for c in cs:
        text = rb.html_tables_to_md(fix_marker(c, known))
        parts = [clean_title(x) for x in (c.get("chapter_path") or "").split(" / ")]
        sec = " / ".join(parts[1:]) if len(parts) > 1 and norm(parts[-1]) != norm(top) else None
        titles = [top] + ([sec, parts[-1]] if sec else [])
        text = strip_leading_titles(text, titles)
        body, notes = split_notes_keep_order(text)
        if need_renumber:
            body, notes, offset = renumber(body, notes, offset)
        all_notes += notes
        body = [("### " + HEAD_RE.match(p).group(2)) if HEAD_RE.match(p) and HEAD_RE.match(p).group(1) in ("#", "##")
                else p for p in body]
        if sec and sec != cur_sec:
            joined = "\n\n".join(body)
            new, missing = rb.insert_headings(joined, [parts[-1]])
            if missing:
                body = [f"### {parts[-1]}"] + body
            else:
                body = rb.paras(new)
            cur_sec = sec
        # 被頁界或註釋切斷的段落接回（上一段沒有句末標點、這段不是標題）
        if out and body and is_countable(out[-1]) and is_countable(body[0]):
            tail = rb.PAGE_MARK_RE.sub("", rb.REF_RE.sub("", out[-1])).rstrip()
            if tail and tail[-1] not in rb.ZH_END + ".?!:;\"'”’":
                out[-1] += body.pop(0)
        out += body
    # 段號
    numbered, sec_no, k, has_sec = [], 0, 0, any(p.startswith("### ") for p in out)
    for p in out:
        if p.startswith("### "):
            sec_no, k = sec_no + 1, 0
            numbered.append(p)
        elif is_countable(p):
            k += 1
            sid = f"{label}-{sec_no}-{k}" if has_sec else f"{label}-{k}"
            numbered.append(f"{{{{s:{sid}}}}}{p}")
        else:
            numbered.append(p)
    text = "\n\n".join(numbered)
    if all_notes:
        text += f"\n\n{rb.FOOT_RULE}\n\n" + "\n\n".join(all_notes)
    return text


def fix_marker(c: dict, known: dict) -> str:
    """塊首頁碼標記若是 PDF 頁（等於 page_number）且推得出印刷頁，換成印刷頁；推不出就維持原樣。"""
    t = c.get("content") or ""
    m = re.match(r"^\{\{p:(\d+)\}\}", t)
    if not m or not known or int(m.group(1)) != c.get("page_number"):
        return t
    pp = known.get(c["page_number"]) or rb.infer_printed(c["page_number"], known)
    return t if not pp else f"{{{{p:{pp}}}}}" + t[m.end():]


def mass(chunks: list[dict]) -> int:
    """內容守恆用：去掉所有標記、井號、註號後的字元數。"""
    n = 0
    for c in chunks:
        t = c.get("content") or ""
        t = re.sub(r"\{\{[ps]:[^}]*\}\}|\[\^\d+\]|^\(\d+\)\s|#|</?(?:table|tr|td|th|thead|tbody)\b[^<>\n]{0,80}>", "", t, flags=re.M)
        # ↑ 只去 HTML 表格標籤。寫成 <[^>]+> 會從正文裡落單的「<」一路刪到很遠的「>」，合併跨塊後誤報大量缺字
        n += len(re.findall(r"\w", t))
    return n


def is_front(title: str) -> bool:
    return title in FRONT or bool(re.match(r"^(Copyright|版權|©)", title, re.I))


def promote_flat_sections(chunks: list[dict]) -> list[dict]:
    """章節資料是扁平的（「第一章」與它底下各節同一層）時，把夾在兩個「章」之間的無編號標題
    改成前一章的節：chapter_path「第一章 X / 節名」。「章」＝有章號的，或序／導言／結語這類部分名。
    只在全書至少 2 個有章號的標題、且章號標題之間夾著無編號標題時才動。"""
    tops = [clean_title((c.get("chapter_path") or "").split(" / ")[0]) for c in chunks]
    if any(" / " in (c.get("chapter_path") or "") for c in chunks):
        return chunks
    is_head = [bool(t) and (chapter_number(t) is not None or bool(short_name(t))) for t in tops]
    if sum(1 for t in tops if t and chapter_number(t) is not None) < 2:
        return chunks
    out, parent = [], None
    for c, t, h in zip(chunks, tops, is_head):
        c = dict(c)
        if not t or is_front(t):
            parent = None if is_front(t) else parent
        elif h:
            parent = t
        elif parent:
            c["chapter_path"] = f"{parent} / {t}"
        out.append(c)
    return out


def restructure(chunks: list[dict], meta: dict) -> tuple[list[dict] | None, str, dict]:
    """回傳 (新 chunks 或 None, 原因／OK, 統計)。"""
    import audit_toc_accuracy as at
    if meta.get("collection"):
        return None, f"collection={meta['collection']}", {}
    if any(c.get("source_text") or c.get("sources") for c in chunks):
        return None, "有對照欄（走 rebuild_reference_bilingual）", {}
    if any("{{s:" in (c.get("content") or "") for c in chunks):
        return None, "已有段號", {}
    flags = set(at.audit(chunks, meta)["flags"]) & BAD_FLAGS
    if flags:
        return None, "稽核旗標 " + ",".join(sorted(flags)), {}
    work = promote_flat_sections(chunks)
    if meta.get("file_type") in ("docx", "txt"):
        # docx／txt 的段落只隔一個換行；閱讀器把單一換行當空白，整章會連成一段。改成空行分段（表格列不動）
        work = [dict(c, content="\n\n".join(
            ln for p in rb.paras(c.get("content") or "")
            for ln in ([p] if p.lstrip().startswith("|") else p.split("\n")) if ln.strip()))
            for c in work]
    total = sum(len(c.get("content") or "") for c in work)
    orphan = sum(len(c.get("content") or "") for c in work[3:] if not (c.get("chapter_path") or "").strip())
    if total and orphan / total > 0.3:
        return None, f"章節覆蓋不足（{orphan * 100 // total}% 的內容沒有章名）", {}
    runs: list[tuple[str, list[dict]]] = []
    for c in work:
        top = clean_title((c.get("chapter_path") or "").split(" / ")[0])
        key = (c.get("volume"), top)
        if runs and runs[-1][0] == key:
            runs[-1][1].append(c)
        else:
            runs.append((key, [c]))
    keys = [k for k, _ in runs]
    dup = [k[1] for k, n in collections.Counter(keys).items() if n > 1 and not is_front(k[1]) and k[1]]
    if dup:
        return None, f"章名不連續出現：{dup[:3]}", {}
    body_runs = [(k, cs) for k, cs in runs if k[1] and not is_front(k[1])]
    if len(body_runs) < 2:
        return None, "少於 2 章", {}
    junk = [k[1] for k, _ in body_runs if JUNK_TITLE.search(k[1])]
    if junk:
        return None, f"章名疑似OCR亂碼：{junk[:2]}", {}
    glued = [k[1] for k, _ in body_runs if len(k[1]) > 12 and re.search(r"[，。；！？]", k[1])]
    if glued:
        return None, f"章名黏正文：{glued[:2]}", {}
    lens = sorted(len(p) for _, cs in body_runs for c in cs for p in rb.paras(c.get("content") or ""))
    if lens and lens[len(lens) // 2] > 2500:
        return None, f"段落沒切開（段長中位數 {lens[len(lens) // 2]:,} 字）", {}
    per_ch = sorted(sum(1 for c in cs for p in rb.paras(c.get("content") or "") if is_countable(p))
                    for _, cs in body_runs)
    if per_ch[len(per_ch) // 2] < 3:
        return None, f"章內段落過少（每章段數中位數 {per_ch[len(per_ch) // 2]}）", {}
    labels = dict(zip([k for k, _ in body_runs], chapter_labels([k[1] for k, _ in body_runs])))
    known = rb.printed_map(chunks)
    out: list[dict] = []
    for key, cs in runs:
        if key not in labels:                      # 封面／目錄等前附頁、無章名塊：原樣
            out += [dict(c) for c in cs]
            continue
        text = build_chapter(labels[key], key[1], cs, known)
        if len(text) > MAX_CHAPTER:
            return None, f"合併後單章 {len(text):,} 字超過上限", {}
        first = dict(cs[0])
        pages = [p for c in cs for p in (c.get("page_numbers") or ([c["page_number"]] if c.get("page_number") else []))]
        if pages:
            first["page_numbers"] = pages
            if any(c.get("printed_pages") for c in cs):
                first["printed_pages"] = [known.get(p) or rb.infer_printed(p, known) for p in pages]
                first["printed_page"] = first["printed_pages"][0]
        first.update(content=text, chapter_path=key[1], chunk_type="chapter", format="markdown")
        if "\n### " in text:
            first["section_anchors"] = True
        out.append(first)
    for i, c in enumerate(out):
        c["chunk_index"] = i
    # 合併後再驗一次段落：一頁一段的書，跨頁斷句接回去之後會整章變一段（Taiwan's Buddhist Nuns）
    chs = [c for c in out if c.get("chunk_type") == "chapter" and "{{s:" in c["content"]]
    lumpy = [c for c in chs if len(c["content"]) > 5000 and c["content"].count("{{s:") <= 3]
    if chs and len(lumpy) * 4 > len(chs):
        return None, f"合併後段落沒切開（{len(lumpy)}/{len(chs)} 章字多但不到 4 段）", {}
    before, after = mass(chunks), mass(out)
    # 只有標題字可以增減（剝掉正文裡重打的章名、補上節名）：容許量＝各塊標題字數兩倍＋100，正文不能少
    title_w = sum(len(re.findall(r"\w", c.get("chapter_path") or "")) for c in chunks)
    if abs(after - before) > 100 + 2 * title_w:
        return None, f"內容守恆失敗 {before:,}→{after:,}", {}
    return out, "OK", {"before": len(chunks), "after": len(out), "chapters": len(body_runs),
                       "mass": (before, after)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--show")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--ids", help="要寫回的書 id 清單檔（一行一個）")
    a = ap.parse_args()
    import audit_toc_accuracy as at
    meta = at.load_meta()
    print("ebooks", len(meta), flush=True)
    if a.show:
        cs = [json.loads(l) for l in (CH / f"{a.show}.jsonl").open(encoding="utf-8") if l.strip()]
        out, why, st = restructure(cs, meta.get(a.show, {}))
        print(why, st)
        for c in out or []:
            print(f"\n=== [{c['chunk_index']}] {c.get('chapter_path')!r} {len(c['content']):,} 字")
            print(c["content"][:700])
        return 0
    if a.apply:
        ids = [l.strip() for l in Path(a.ids).read_text(encoding="utf-8").splitlines() if l.strip()]
        import standardize_ebook as se
        for bid in ids:
            src = CH / f"{bid}.jsonl"
            cs = [json.loads(l) for l in src.open(encoding="utf-8") if l.strip()]
            out, why, st = restructure(cs, meta.get(bid, {}))
            if out is None:
                print("SKIP", bid, why, flush=True)
                continue
            bak = src.with_name(src.name + ".bak_restructure")
            if not bak.exists():
                shutil.copy2(src, bak)
            o = se.write_jsonl(bid, out)
            se.push_to_r2(bid, o)
            se.update_db(bid, out)
            print("OK", bid, st, flush=True)
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in CH.glob("*.jsonl") if p.stem in meta)
    if a.limit:
        files = files[:a.limit]
    rows, reasons = [], collections.Counter()
    for i, p in enumerate(files):
        try:
            cs = [json.loads(l) for l in p.open(encoding="utf-8") if l.strip()]
            cs.sort(key=lambda c: c.get("chunk_index") or 0)
            out, why, st = restructure(cs, meta[p.stem])
        except Exception as e:  # noqa: BLE001
            out, why, st = None, f"錯誤 {type(e).__name__}: {str(e)[:60]}", {}
        reasons[why if why == "OK" else why.split(" ")[0].split("：")[0]] += 1
        m = meta[p.stem]
        rows.append([p.stem, (m.get("title") or "")[:40], m.get("file_type") or "", why,
                     st.get("before", ""), st.get("after", ""), st.get("chapters", "")])
        if i % 250 == 0:
            print(f"{i}/{len(files)} {dict(reasons)}", flush=True)
    (OUT / "dryrun.tsv").write_text("\n".join("\t".join(map(str, r)) for r in
                                              [["id", "title", "type", "result", "chunks_before", "chunks_after",
                                                "chapters"]] + rows) + "\n", encoding="utf-8")
    (OUT / "ok_ids.txt").write_text("\n".join(r[0] for r in rows if r[3] == "OK") + "\n", encoding="utf-8")
    print(f"分母 {len(rows)} 本：{dict(reasons.most_common())}", flush=True)
    print("RESTRUCTURE_DRYRUN_DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
