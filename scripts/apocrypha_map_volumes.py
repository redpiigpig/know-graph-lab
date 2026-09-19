# -*- coding: utf-8 -*-
"""從重 OCR 的 middle.json 讀出一冊書的**作品邊界**（卷N ＝ 一部文獻）。

    python scripts/apocrypha_map_volumes.py --vol cct-nt-1
    python scripts/apocrypha_map_volumes.py --vol cct-nt-1 --pages 100-140
    python scripts/apocrypha_map_volumes.py --part nt --json output/...

🚨 為什麼不照 chapter 切（handoff §D）：舊資料的 chunk 邊界跟作品邊界對不齊 ——
`gthom` 的 ch.10 第 1 節還是拉丁語嬰孩福音的結尾，第 2 節已經是「卷二 多馬福音
簡介」。所以界線只能從正文本身認。

本檔用**兩個互相獨立的錨**，兩邊對不上就報出來讓人看，不要自己挑一邊信：

  錨一 · 書眉（`discarded_blocks` 型別 `header`）
      單數頁印「第二部分：卷五阿拉伯語耶穌嬰孩時期福音」，雙數頁印書名。
      書眉**每一頁都有**，所以它給的是「這一頁屬於哪一卷」——覆蓋率最好的訊號。

  錨二 · 正文裡的卷首（`preproc_blocks` 型別 `title`）
      一部作品的開頭固定是 title「<作品名>」＋ title「簡介」…＋ title「文本」。
      它給的是「哪一頁**開始**一部新作品」——精確到頁，但只在卷首出現一次。

兩者的分工：錨二定起點，錨一補中間與驗證。錨一說某頁屬於卷五、錨二卻說卷五從
下一頁才開始 —— 這種歧異一律列出來，不自動裁決。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
OUT_ROOT = REPO / "output" / "apocrypha-ocr"

CN_NUM = {c: i for i, c in enumerate("一二三四五六七八九", 1)}
CN_DIGITS = "十廿卅一二三四五六七八九"


def cn_int(s: str) -> int | None:
    """中文數字 → 阿拉伯數字。只需撐到「卷三十幾」，不做通用實作。

    🚨 要認得「廿」「卅」。第二冊目錄印的是「卷廿一夏娃福音」「卷廿五真理的福音」，
    少了這兩個字不會報錯，只會讓那五卷**從目錄裡整個消失**——而目錄是定界的權威
    來源，少一條就等於把後面那部作品的範圍一路吃到下一條。
    """
    s = s.strip()
    if not s or any(c not in CN_DIGITS for c in s):
        return None
    for tens_char, tens in (("廿", 20), ("卅", 30)):
        if s.startswith(tens_char):
            rest = s[1:]
            if not rest:
                return tens
            ones = CN_NUM.get(rest)
            return tens + ones if ones else None
    if "十" not in s:
        return CN_NUM.get(s)
    head, _, tail = s.partition("十")
    if head and head not in CN_NUM:
        return None
    if tail and tail not in CN_NUM:
        return None
    tens = CN_NUM.get(head, 1) if head else 1
    ones = CN_NUM.get(tail, 0) if tail else 0
    return tens * 10 + ones


# 書眉長相：「第二部分：卷五阿拉伯語耶穌嬰孩時期福音」「卷五」「基督教典外文獻新約篇 第一冊」
HEAD_PART = re.compile(r"第([一二三四五六七八九十]+)部分")
HEAD_JUAN = re.compile(r"卷([一二三四五六七八九十]+)")
BOOK_HEAD = re.compile(r"基督教典外文獻")
# 卷首的正文小標
INTRO_TITLE = "簡介"
TEXT_TITLE = "文本"


def block_text(b: dict) -> str:
    """一個區塊 → 純文字。

    🚨 表格的文字在 `span["html"]`，不在 `span["content"]`。只讀 content 會讓整頁
    回空字串——而且是**安靜地**回空：頁數照樣對、稽核照樣過、逐段點名照樣 0 段落外
    （因為分母就是 MinerU 給的那些段落）。2026-09-19 實測新約篇四冊共 **50 頁**
    就是這樣整頁不見，其中三頁是《多馬福音》語錄 1–7（於是整部書切不出章），
    另有連續 12 頁的《耶穌基督智慧書》。
    這套書凡是「兩種版本並排」的段落都排成有框線的表格，所以這不是罕見情形。
    """
    # 🚨 巢狀型別不要用白名單列舉。原本只對 table／image 往下鑽，結果 `code` 這一種
    #    （MinerU 把某些縮排段落判成 code）又整頁回空。判準改成「自己沒有 lines、
    #    但底下有 blocks」就往下鑽，才不會每遇到一種新型別就再掉一次資料。
    if not b.get("lines") and b.get("blocks"):
        return "\n".join(x for x in (block_text(sub) for sub in b["blocks"]) if x).strip()
    out = []
    for line in b.get("lines") or []:
        for s in line.get("spans") or []:
            if s.get("content"):
                out.append(s["content"])
            elif s.get("html"):
                out.append(table_html_to_text(s["html"]))
        out.append("\n")
    return "".join(out).strip()


_TAG = re.compile(r"<[^>]+>")


def table_rows(html: str, carried_head: list[str] | None = None
               ) -> tuple[list[str], list[str] | None]:
    """表格 HTML → (逐列文字, 這個表的欄標)。**一列一段**，不是整個表一段。

    🚨 整個表回成一段的話，列首的號（「1. 標題和第一句」）就不在段首，切節那一步
    一個也認不到——《多馬福音》114 則語錄整片變成一段。

    🚨 跨頁的表格**只有第一頁有欄標**，後面幾頁直接接著排。所以欄標要跨頁帶著走
    （`carried_head`），否則續頁的右欄就標不出來源。
    """
    rows: list[list[str]] = []
    for tr in re.findall(r"<tr>(.*?)</tr>", html, re.S):
        cells = [_TAG.sub("", td).replace("&lt;", "<").replace("&gt;", ">")
                 .replace("&amp;", "&").strip()
                 for td in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        if any(cells):
            rows.append(cells)
    if not rows:
        return [], carried_head
    head = carried_head
    if len(rows) > 1 and len(rows[0]) > 1 and all(
            len(c) <= 12 and "。" not in c for c in rows[0]):
        head = rows.pop(0)
    out: list[str] = []
    for cells in rows:
        if len(cells) == 1 or not head:
            out.append("　".join(c for c in cells if c))
            continue
        # 左欄是主要讀法，**不加標籤**（見下方 table_html_to_text 的說明）
        parts = [cells[0]] if cells[0] else []
        for i, c in enumerate(cells[1:], start=1):
            if not c:
                continue
            parts.append(f"〔{head[i]}〕{c}" if i < len(head) and head[i] else c)
        out.append("\n".join(parts))
    return out, head


def table_html_to_text(html: str) -> str:
    """MinerU 的表格 HTML → 逐列文字。

    這套書的表格幾乎都是「同一段的兩種版本並排」（科普替語版／希臘語版、
    伯默蒲草紙5／一些後期的抄卷）。依定案的作法——單一版本＋行內標籤——
    把表頭當標籤，每一列輸出成一段，兩欄各冠上自己的標籤。
    """
    rows: list[list[str]] = []
    for tr in re.findall(r"<tr>(.*?)</tr>", html, re.S):
        cells = [_TAG.sub("", td).replace("&lt;", "<").replace("&gt;", ">")
                 .replace("&amp;", "&").strip()
                 for td in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        if any(cells):
            rows.append(cells)
    if not rows:
        return ""
    # 第一列若兩欄都短、且不含句號，當表頭（欄標）
    head: list[str] = []
    if len(rows) > 1 and all(len(c) <= 12 and "。" not in c for c in rows[0]) and len(rows[0]) > 1:
        head = rows.pop(0)
    out = []
    if head:
        # 🚨 **左欄不要加標籤**。左欄是主要讀法，它開頭的那個號（「1. 標題和第一句」）
        #    是切節唯一的錨；在前面塞一個〔科普替語版〕就把號從段首推走，整部
        #    《多馬福音》的 114 則語錄就切不出來了。改成把欄名先講一次，之後每一列
        #    只在**右欄**冠標籤——主要讀法在原位、次要讀法有標示，與雙欄那邊一致。
        out.append("（以下兩欄對照：" + "／".join(c for c in head if c) + "）")
    for cells in rows:
        if len(cells) == 1 or not head:
            out.append("　".join(c for c in cells if c))
            continue
        parts = [cells[0]] if cells[0] else []
        for i, c in enumerate(cells[1:], start=1):
            if not c:
                continue
            parts.append(f"〔{head[i]}〕{c}" if i < len(head) and head[i] else c)
        out.append("\n".join(parts))
    return "\n".join(out)


def extract_blocks(preproc: list[dict], carried_head: list[str] | None = None
                   ) -> tuple[list[tuple[str, str, list]], list[str] | None]:
    """一頁的 `preproc_blocks` → [(型別, 文字, bbox)]，**表格一列一項**。

    🚨 這支是 `read_volume`（整冊併好）與 `apocrypha_extract_works.load_pages`
    （還在分批）**共用**的。先前 bbox 只加在其中一邊，結果 OCR 一跑完、改走併好的
    那條路，雙欄偵測就安靜地失效了。共用的東西就放一份。
    """
    out: list[tuple[str, str, list]] = []
    head = carried_head
    for b in preproc:
        bbox = b.get("bbox") or [0, 0, 0, 0]
        if b.get("type") == "table":
            html = ""
            for sub in (b.get("blocks") or [b]):
                for line in sub.get("lines") or []:
                    for s in line.get("spans") or []:
                        if s.get("html"):
                            html = s["html"]
            if html:
                before = head
                rows, head = table_rows(html, head)
                # 欄名只在**第一次看到**時講一次。跨頁的表格每頁都印一遍的話，
                # 讀起來每隔幾段就冒出一句「以下兩欄對照」。
                if head and head != before:
                    out.append(("text", "（以下兩欄對照："
                                + "／".join(c for c in head if c) + "）", bbox))
                out += [("text", r, bbox) for r in rows if r.strip()]
                continue
        t = block_text(b)
        if t:
            out.append((b.get("type") or "text", t, bbox))
    return out, head


def find_middle(slug: str) -> Path:
    """只認**併好的**那一份，不要隨便撿一個批次檔。

    🚨 OCR 是 40 頁一批跑的，每批各自留一個 `*_middle.json`。用 rglob 撿 `hits[0]`
    會拿到**第 0 批**——40 頁的東西冒充整冊，而報表照樣印得出頁數、書眉、卷次，
    看起來完全正常。所以併檔產物用固定檔名 `<slug>_middle.json`，找不到就明講
    「還沒併」，不要回退到批次檔。
    """
    merged = OUT_ROOT / slug / f"{slug}_middle.json"
    if merged.exists():
        return merged
    loose = sorted((OUT_ROOT / slug).rglob("*_middle.json"))
    if len(loose) == 1:
        return loose[0]          # 一次跑完、沒有分批的（兩篇嬰孩福音就是這樣）
    if loose:
        raise SystemExit(
            f"{slug} 只有 {len(loose)} 個批次檔、還沒併成 {merged.name} —— "
            f"OCR 還沒跑完（或跑完了但有批次失敗）。不要拿單批當整冊。")
    raise SystemExit(f"找不到 {slug} 的 middle.json —— 先跑 ocr_cct_apocrypha.py")


def read_volume(slug: str) -> list[dict]:
    """→ 逐頁 [{idx, printed, heads, notes, blocks:[(type,text)], paras:[...]}]"""
    mid = json.loads(find_middle(slug).read_text(encoding="utf-8"))
    pages = []
    carried: list[str] | None = None
    for page in mid.get("pdf_info") or []:
        heads, notes, printed = [], [], None
        for b in page.get("discarded_blocks") or []:
            t = block_text(b)
            if not t:
                continue
            kind = b.get("type")
            if kind == "header":
                heads.append(" ".join(t.split()))
            elif kind == "page_footnote":
                notes.append(" ".join(t.split()))
            elif kind == "page_number":
                m = re.search(r"\d{1,4}", t)
                if m and printed is None:
                    printed = int(m.group())
        # 🚨 bbox 一定要一起帶出來。雙欄偵測靠的就是它，而它是用 `p.get("boxes")`
        #    取的——少帶的話不會報錯，只會安靜地回「沒有雙欄頁」。本檔與
        #    `apocrypha_extract_works.load_pages` 是同一份資料的兩條讀法（整冊併好
        #    走這裡、還在分批走那裡），兩邊的欄位必須一樣，否則 OCR 跑完的那一刻
        #    偵測就自己失效了。
        raw, carried = extract_blocks(page.get("preproc_blocks") or [], carried)
        pages.append({
            "idx": int(page.get("page_idx", len(pages))),
            "printed": printed,
            "heads": heads,
            "notes": notes,
            "blocks": [(k, t) for k, t, _ in raw],
            "boxes": [bb for _, _, bb in raw],
            "paras": [t for k, t, _ in raw],
        })
    pages.sort(key=lambda p: p["idx"])
    return pages


def head_juan(page: dict) -> tuple[int | None, int | None, str]:
    """書眉 → (部分, 卷, 書眉裡的作品名)。認不出來回 (None, None, '')。"""
    for h in page["heads"]:
        if BOOK_HEAD.search(h):        # 雙數頁的書名眉，不帶卷號
            continue
        mj = HEAD_JUAN.search(h)
        if not mj:
            continue
        juan = cn_int(mj.group(1))
        mp = HEAD_PART.search(h)
        part = cn_int(mp.group(1)) if mp else None
        name = h[mj.end():].strip("：: 　")
        return part, juan, name
    return None, None, ""


def title_starts(pages: list[dict]) -> list[dict]:
    """錨二：正文 title 區塊裡的卷首。

    卷首的樣子是同一頁上先出現作品名的 title、緊接著 title「簡介」。只認這個
    組合——單獨一個 title 可能是作品內部的小標（例如〈第一部分〉），拿它當
    起點會把一部書切成好幾部。
    """
    starts = []
    for p in pages:
        titles = [(i, t) for i, (k, t) in enumerate(p["blocks"]) if k == "title"]
        for n, (i, t) in enumerate(titles):
            if t.strip() != INTRO_TITLE:
                continue
            # 「簡介」之前最近的一個 title 就是作品名
            prev = [tt for j, tt in titles[:n] if tt.strip() != INTRO_TITLE]
            starts.append({
                "idx": p["idx"], "printed": p["printed"],
                "title": prev[-1].strip() if prev else "（同頁沒有作品名 title）",
                "block_i": i,
            })
    return starts


def group_by_head(pages: list[dict]) -> list[dict]:
    """錨一：照書眉把連續頁分成段。回傳每一段 [{part, juan, name, pages:[idx]}]。

    🚨 書眉是**左右頁交替**的：單數頁印「第二部分：卷五 <作品名>」，雙數頁印書名
    「基督教典外文獻新約篇 第一冊」。所以「這一頁的書眉沒有卷號」≠「換卷了」，
    它只是那一面印的是書名。第一版把沒卷號的頁當成獨立一段，23 頁就切出 23 段，
    每一段一頁——看起來像資料很破，其實是判準錯了。

    正解：沒有卷號的頁**沿用上一頁的卷**，只有頁面明白說出**另一個**卷號時才換段。
    """
    runs: list[dict] = []
    cur: tuple[int | None, int | None] | None = None
    cur_part: int | None = None
    for p in pages:
        part, juan, name = head_juan(p)
        # 🚨 卷號在**每個部分底下重新編**（第一部分有卷一…卷二十，第二部分又從卷一
        #    開始），所以鍵一定要是 (部分, 卷)。而書眉有時只印「卷五」不印部分，
        #    那種頁沿用目前的部分——把它當成「部分不明」會憑空多切一段。
        if part is None:
            part = cur_part
        else:
            cur_part = part
        if juan is None:                        # 書名眉／書眉被裁掉 → 沿用
            if runs:
                runs[-1]["pages"].append(p["idx"])
            else:                               # 還沒遇過任何卷號（卷首頁常這樣）
                runs.append({"part": None, "juan": None,
                             "name": "", "pages": [p["idx"]]})
            continue
        last = runs[-1] if runs else None
        # 同一卷的條件：卷號相同，且部分不衝突（其中一邊還不知道就算相容，
        # 並把知道的那一邊補上去——卷首頁的書眉常只印「卷五」）。
        same = (last is not None and last["juan"] == juan
                and (last["part"] is None or part is None or last["part"] == part))
        if same:
            last["pages"].append(p["idx"])
            if last["part"] is None:
                last["part"] = part
            if name and len(name) > len(last["name"]):
                last["name"] = name             # 書眉偶爾被切掉半截，取最長的那次
        elif last is not None and last["juan"] is None:
            # 開頭那段「還沒遇過卷號」的頁其實屬於這一卷，補記回去
            last.update(part=part, juan=juan, name=name)
            last["pages"].append(p["idx"])
        else:
            runs.append({"part": part, "juan": juan,
                         "name": name, "pages": [p["idx"]]})
        cur = (part, juan)
    return runs


def report(slug: str, lo: int | None, hi: int | None) -> dict:
    pages = read_volume(slug)
    sel = [p for p in pages if (lo is None or p["idx"] >= lo) and (hi is None or p["idx"] <= hi)]
    runs = group_by_head(sel)
    starts = title_starts(sel)

    printed_ok = sum(1 for p in sel if p["printed"] is not None)
    notes = sum(len(p["notes"]) for p in sel)
    heads_ok = sum(1 for p in sel if p["heads"])
    print(f"════ {slug}　{len(sel)} 頁")
    print(f"  印刷頁碼 {printed_ok}/{len(sel)}　書眉 {heads_ok}/{len(sel)}　註腳 {notes} 條")
    pr = [p["printed"] for p in sel if p["printed"]]
    if pr:
        print(f"  印刷頁範圍 {min(pr)}–{max(pr)}")

    print(f"\n── 錨一 · 書眉分段（{len(runs)} 段，含認不出卷號的）")
    for r in runs:
        span = f"{r['pages'][0]}–{r['pages'][-1]}"
        pp = [p["printed"] for p in sel if p["idx"] in set(r["pages"]) and p["printed"]]
        tag = f"第{r['part']}部分 卷{r['juan']}" if r["juan"] else "（無卷號書眉）"
        print(f"  {tag:>18}　頁索引 {span:>9}（{len(r['pages']):>3} 頁）"
              f"　印刷 {min(pp) if pp else '?'}–{max(pp) if pp else '?'}　{r['name'][:30]}")

    print(f"\n── 錨二 · 正文卷首（title＋簡介，{len(starts)} 處）")
    for s in starts:
        print(f"  頁索引 {s['idx']:>4}　印刷 {str(s['printed']):>4}　{s['title'][:40]}")

    # ── 兩錨對帳 ──
    print("\n── 對帳")
    head_starts = {r["pages"][0] for r in runs if r["juan"]}
    title_idx = {s["idx"] for s in starts}
    only_head = sorted(head_starts - title_idx)
    only_title = sorted(title_idx - head_starts)
    if not only_head and not only_title:
        print("  ✓ 兩錨完全一致")
    else:
        if only_head:
            print(f"  ⚠ 書眉說換卷、正文沒有卷首的頁索引：{only_head}")
        if only_title:
            print(f"  ⚠ 正文有卷首、書眉沒換卷的頁索引：{only_title}")
        print("  （±1 頁多半是卷首頁不印書眉／書眉沿用上一卷，要逐一看過再定界）")
    return {"pages": pages, "runs": runs, "starts": starts}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--vol", help="例 cct-nt-1")
    ap.add_argument("--part", choices=["nt", "ot"], help="整個篇的四／六冊都跑")
    ap.add_argument("--pages", help="只看某段頁索引，例 100-140")
    a = ap.parse_args()
    if not (a.vol or a.part):
        ap.error("要 --vol 或 --part")

    lo = hi = None
    if a.pages:
        s, _, e = a.pages.partition("-")
        lo, hi = int(s), int(e or s)

    slugs = [a.vol] if a.vol else [
        f"cct-{a.part}-{i}" for i in range(1, 5 if a.part == "nt" else 7)]
    for slug in slugs:
        if not (OUT_ROOT / slug).exists():
            print(f"（{slug} 還沒 OCR，跳過）")
            continue
        report(slug, lo, hi)
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
