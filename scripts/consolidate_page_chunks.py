#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""OCR「一頁一塊」的書合併成「一節一塊」，註釋改成可上下互點（2026-09-27）。

使用者回報《民主妙法》：一頁六七百字就切一塊太碎；每頁頁尾的註釋是純文字、點不回正文。
reader（pages/ebook/[id].vue renderMarkdown）早就支援：
  - 正文 `[^N]` → 可點上標（id=fnref-…，連到 #fn-…）
  - 15 條以上破折號的分隔線之後、以 `(N)` 開頭的段落 → 註釋條目（帶 ↩ 回正文）
  - `{{p:N}}` → 行內原書頁碼標記（引用時取游標前最近的一個）
所以這支只做資料轉換，不動 reader：
  1. 同一 chapter_path 的連續頁合成一塊（上限 MAX_CHARS 字換塊）
  2. 每頁開頭插 `{{p:印刷頁碼}}`（沒有就用實體頁序）；頁碼清單存 page_numbers（PDF 對照用）
  3. 上一頁停在句中就直接接下一頁，不硬斷段；段內單一換行（MinerU 折行）接起來
  4. 每頁頁尾註釋（「50譯註：…」）轉成 `(50) 譯註：…` 一條一段，集中放在該塊末尾
  5. 正文註號：只轉「這一頁確實有這條註」的數字，且要緊接在中文字或標點之後、後面不是數字；
     OCR 把上標 50 認成「5°」也認得
content 以外的欄位不動；page_number 保留該塊第一頁（實體頁序），原逐頁資料留 .jsonl.bak_pages。

  python -X utf8 scripts/consolidate_page_chunks.py --ids <ebook_id> [--apply]
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

CH = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\_chunks")
RULE_RE = re.compile(r"^[—－\-]{15,}\s*$", re.M)
FN_LINE = re.compile(r"^(\d{1,4})\s*(?=\S)(?!\d)(.*)$")
FOOT_RULE = "—" * 15
MAX_CHARS = 15_000
_CJK = r"[\u4e00-\u9fff]"
_END = "。！？」』）…—：；"


def split_page(content: str) -> tuple[str, list[tuple[int, str]]]:
    """一頁 → (正文, [(註號, 註文)])。註釋在頁尾分隔線之後，每條以號碼開頭，沒號碼的行接上一條。"""
    parts = RULE_RE.split(content or "", maxsplit=1)
    body = parts[0].strip()
    notes: list[tuple[int, str]] = []
    if len(parts) > 1:
        for line in parts[1].splitlines():
            s = line.strip()
            if not s:
                continue
            m = FN_LINE.match(s)
            if m:
                notes.append((int(m.group(1)), m.group(2).strip()))
            elif notes:
                notes[-1] = (notes[-1][0], notes[-1][1] + s)
    return body, notes


def link_markers(body: str, numbers: list[int]) -> tuple[str, list[int]]:
    """把正文裡的註號換成 `[^N]`，依序找（每個號碼只換第一個合格位置）。回傳 (新正文, 找到的號碼)。"""
    found = []
    pos = 0
    for n in sorted(numbers):
        variants = [str(n)]
        if n % 10 == 0:
            variants.append(str(n)[:-1] + "°")   # OCR：上標 50 → 5°
        best = None
        for v in variants:
            rx = re.compile(r"(?<=" + _CJK + r"|[，。、；：！？」』）])" + re.escape(v) + r"(?![\d°年月日%％頁])")
            m = rx.search(body, pos)
            if m and (best is None or m.start() < best.start()):
                best = m
        if best:
            body = body[:best.start()] + f"[^{n}]" + body[best.end():]
            pos = best.start() + len(f"[^{n}]")
            found.append(n)
    return body, found


def join_lines(text: str) -> str:
    """段內單一換行（MinerU 折行）：兩邊是中文就直接接，其他補空格。段落（空行）保留。"""
    paras = re.split(r"\n\s*\n", text)
    out = []
    for p in paras:
        p = re.sub(r"(?<=" + _CJK + r"|[，。、；：！？「」『』（）])\n(?=" + _CJK + r"|[「『（])", "", p)
        out.append(re.sub(r"\s*\n\s*", " ", p).strip())
    return "\n\n".join(x for x in out if x)


def consolidate(chunks: list[dict]) -> list[dict]:
    """逐頁 chunks → 一節一塊。只合併 chunk_type=='page'；其他型別原樣保留。"""
    out: list[dict] = []
    cur = None

    def flush():
        nonlocal cur
        if cur:
            body = cur["body"].strip()
            notes = "\n\n".join(f"({n}) {t}" for n, t in cur["notes"])
            content = body + (f"\n\n{FOOT_RULE}\n\n{notes}" if notes else "")
            c = dict(cur["first"])
            c.update(content=content, page_numbers=cur["pages"], format="markdown",
                     printed_pages=cur["printed"])
            c.pop("printed_page", None)
            c["printed_page"] = next((p for p in cur["printed"] if p), None)
            out.append(c)
        cur = None

    for c in chunks:
        if c.get("chunk_type") != "page":
            flush()
            out.append(dict(c))
            continue
        body, notes = split_page(c.get("content") or "")
        body = join_lines(body)
        body, _ = link_markers(body, [n for n, _ in notes])
        label = c.get("printed_page") or c.get("page_number")
        marker = f"{{{{p:{label}}}}}" if label else ""
        cp = c.get("chapter_path")
        if cur is None or cur["cp"] != cp or len(cur["body"]) + len(body) > MAX_CHARS:
            flush()
            cur = {"cp": cp, "first": c, "body": marker + body, "notes": [], "pages": [],
                   "printed": []}
        else:
            prev = cur["body"].rstrip()
            glue = "" if prev and prev[-1] not in _END and not prev.endswith("]") else "\n\n"
            cur["body"] = prev + glue + marker + body
        cur["notes"].extend(notes)
        cur["pages"].append(c.get("page_number"))
        cur["printed"].append(c.get("printed_page"))
    flush()
    for i, c in enumerate(out):
        c["chunk_index"] = i
    return out


def eligible(chunks: list[dict]) -> str:
    """回傳空字串＝可合併；否則回原因。一頁一塊為主、多數頁有章節、沒有原文欄／譯文、沒合併過。"""
    pages = [c for c in chunks if c.get("chunk_type") == "page"]
    if len(pages) < 10 or len(pages) < 0.6 * len(chunks):
        return "not-page-book"
    if any(c.get("page_numbers") for c in chunks):
        return "already"
    if any("source_text" in c or "sources" in c for c in chunks):
        return "has-translation"
    with_cp = [c for c in pages if c.get("chapter_path")]
    if len(with_cp) < 0.5 * len(pages) or len({c["chapter_path"] for c in with_cp}) < 2:
        return "no-chapters"
    return ""


def main() -> int:
    ids = sys.argv[sys.argv.index("--ids") + 1:] if "--ids" in sys.argv else []
    ids = [i for i in ids if not i.startswith("--")]
    apply = "--apply" in sys.argv
    if "--all" in sys.argv:
        ids = sorted(p.stem for p in CH.glob("*.jsonl"))
    stat: dict[str, int] = {}
    for bid in ids:
        p = CH / f"{bid}.jsonl"
        try:
            chunks = [json.loads(l) for l in p.open(encoding="utf-8") if l.strip()]
        except Exception:  # noqa: BLE001
            continue
        why = eligible(chunks)
        if why:
            stat[why] = stat.get(why, 0) + 1
            if "--all" not in sys.argv:
                print(bid, "略過：", why)
            continue
        stat["merged"] = stat.get("merged", 0) + 1
        new = consolidate(chunks)
        fn_in = sum(len(split_page(c.get("content") or "")[1]) for c in chunks if c.get("chunk_type") == "page")
        linked = sum(c["content"].count("[^") for c in new)
        print(f"{bid}：{len(chunks)} 塊 → {len(new)} 塊；註釋 {fn_in} 條，正文註號連上 {linked} 個")
        if apply:
            bak = p.with_suffix(".jsonl.bak_pages")
            if not bak.exists():
                shutil.copy2(p, bak)
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            import standardize_ebook as se  # noqa: E402
            out = se.write_jsonl(bid, new)
            try:
                se.push_to_r2(bid, out)
                se.update_db(bid, new)
            except Exception as e:  # noqa: BLE001  網路失敗只記，本機已寫好
                print("  同步失敗", type(e).__name__, flush=True)
                stat["sync-failed"] = stat.get("sync-failed", 0) + 1
            print("  已寫入＋R2＋DB", flush=True)
    print("SUMMARY", stat, flush=True)
    print("CONSOLIDATE_DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
