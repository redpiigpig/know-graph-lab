"""從掃描書自己的「目次」頁解出章節骨架，零 LLM。

Workflow H 的 `fix_book_structure.py recover` 是拿 Gemini 去**推**章節，適用於
根本沒有目次頁的書；但很多掃描書的目次就印在書裡、OCR 也轉出來了，那份表比
模型推出來的準，而且不吃配額。差別在於要把「目次上印的頁碼」換算成「PDF 第幾張」。

換算靠 `printed_page`（MinerU 從 discarded_blocks 撿回來的原書頁碼）：

  🚨 **不能直接查表**。章首頁多半不印頁碼，於是最需要的那幾個進入點恰好查不到
  （《民主妙法》五章的起始頁 53/75/127/175/205 全部沒有）。改用**最近的有頁碼
  鄰居**推算：同一段落裡頁碼是連號的，所以 PDF 頁 = 鄰居的 PDF 頁 + (目標印刷頁
  − 鄰居的印刷頁)。

  🚨 **推算完一定要驗**。目次頁的 OCR 會把頁碼讀錯（實測「索引...300」被讀成
  「3003」），而錯掉的章節起點會讓整段內容掛到錯的章名底下 —— 側欄看起來正常、
  點進去卻是別章的內容，屬於「看起來成功的失敗」。閘是：**推算出來的那一頁，
  內容裡真的要找得到這個標題**，找不到就在附近幾頁挪；都找不到就丟掉這一條並印出來，
  不要猜。

用法：
    python scripts/toc_from_toc_pages.py --book <id> --toc-pages 4-6          # 只看
    python scripts/toc_from_toc_pages.py --book <id> --toc-pages 4-6 --apply  # 寫回
"""
import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
sys.stdout.reconfigure(encoding="utf-8")

# 目次行的尾巴是頁碼，中間夾著點線（. · … ． 空白）
_ENTRY = re.compile(r"^(?P<title>.*?)[\s.．·・…‥]*(?P<page>\d{1,4})\s*$")
# 章級條目：第N章，或這些固定名稱
_TOP_NAMES = ("導讀", "中文版序", "謝辭", "自序", "序論", "緒論", "結論",
              "註釋", "注釋", "參考書目", "參考文獻", "索引", "後記", "譯後記", "附錄")
_TOP_PREFIX = re.compile(r"^第[一二三四五六七八九十百]+[章卷編篇部]")
_STRIP = re.compile(r"[\s.．·・…‥、，,：:；;「」『』（）()〈〉《》〔〕\[\]—－\-]")


def norm(text: str) -> str:
    return _STRIP.sub("", text)


def parse_toc_lines(lines: list[str]) -> tuple[list[dict], list[str]]:
    """目次行 → [{title, printed_page, level}]，外加「看得懂但沒頁碼」的殘料。"""
    entries, orphans = [], []
    for raw in lines:
        line = raw.strip().lstrip("目次").strip()
        if not line:
            continue
        m = _ENTRY.match(line)
        if not m or not m.group("title").strip():
            if line:
                orphans.append(line)
            continue
        title = m.group("title").strip(" .．·・…‥")
        # 一行擠了兩個條目（「一、作者背景…二、本書內容…4」）：只有最後那個帶頁碼，
        # 前面那個沒有頁碼可對，記成殘料讓人看見，不要替它猜一個頁碼。
        parts = re.split(r"(?<=[^、])(?=[一二三四五六七八九十]+、)", title)
        if len(parts) > 1:
            orphans.extend(p.strip() for p in parts[:-1] if p.strip())
            title = parts[-1].strip()
        level = 1 if (_TOP_PREFIX.match(title) or title.startswith(_TOP_NAMES)) else 2
        entries.append({"title": title, "printed_page": int(m.group("page")), "level": level})
    return entries, orphans


def resolve_page(printed: int, anchors: list[tuple[int, int]]) -> int | None:
    """印刷頁 → PDF 頁。拿最近的 (pdf, printed) 錨點推算（同段落頁碼連號）。"""
    if not anchors:
        return None
    pdf, anchor_printed = min(anchors, key=lambda a: abs(a[1] - printed))
    return pdf + (printed - anchor_printed)


def verify(page: int, title: str, by_page: dict[int, dict], window: int = 3) -> int | None:
    """標題真的出現在那一頁嗎？在 ±window 內找，找不到回 None（寧可丟掉）。"""
    needle = norm(title)
    if len(needle) > 12:
        needle = needle[:12]
    if not needle:
        return None
    for delta in sorted(range(-window, window + 1), key=abs):
        c = by_page.get(page + delta)
        if c and needle in norm(c.get("content") or ""):
            return page + delta
    # 章名前綴（「第二章」）與章題之間常被 OCR 拆到不同行，退一步只比章題
    stripped = norm(_TOP_PREFIX.sub("", title))[:10]
    if stripped and stripped != needle:
        for delta in sorted(range(-window, window + 1), key=abs):
            c = by_page.get(page + delta)
            if c and stripped in norm(c.get("content") or ""):
                return page + delta
    return None


def digit_candidates(printed: int, max_printed: int) -> list[int]:
    """頁碼超出全書範圍時的救援候選。

    目次那幾頁的點線會讓 OCR 多吐或吃掉數字（實測「索引…300」讀成「3003」）。
    拿原字串的子字串當候選，落在合理範圍的才留，最後仍要過標題驗證閘。
    """
    if 0 < printed <= max_printed:
        return [printed]
    s = str(printed)
    out = []
    for size in (len(s) - 1, len(s) - 2):
        if size < 1:
            continue
        for i in range(len(s) - size + 1):
            n = int(s[i:i + size])
            if 0 < n <= max_printed and n not in out:
                out.append(n)
    return out


def find_by_title(title: str, by_page: dict[int, dict], skip: set[int]) -> int | None:
    """目次那行沒帶頁碼時，直接到內文裡找這個標題第一次出現在哪一頁。"""
    needle = norm(title)[:12]
    if len(needle) < 4:                       # 太短的字串到處都是，不要猜
        return None
    for page in sorted(by_page):
        if page in skip:                      # 目次頁自己不算
            continue
        if needle in norm(by_page[page].get("content") or ""):
            return page
    return None


def title_from_page(page: int, by_page: dict[int, dict]) -> str | None:
    """目次那行的標題被 OCR 吃掉時，改用那一頁自己的第一行當章名。"""
    c = by_page.get(page)
    if not c:
        return None
    for line in (c.get("content") or "").splitlines():
        line = line.strip(" .．·・…‥")
        if 1 < len(line) <= 20:
            return line
    return None


# 首條目之前那幾頁的身分，在它們自己的內容裡看得出來。認不出來就留 null，
# reader 會顯示「第 N 段」——那比掛一個猜的名字好。
_FRONT_MARKERS = (("出版品預行編目", "版權頁"), ("圖目次", "圖目次"),
                  ("目次", "目次"), ("表目次", "表目次"))


def front_matter_label(content: str) -> str | None:
    head = norm(content)[:120]
    for marker, label in _FRONT_MARKERS:
        if marker in head:
            return label
    return None


def tidy(title: str) -> str:
    """章名排版：目次的 OCR 不留空白，「第一章臺灣的宗教情境」讀起來黏成一團。"""
    title = _TOP_PREFIX.sub(lambda m: m.group(0) + "　", title, count=1)
    return title.replace(":", "：").replace("　　", "　").strip()


def assign(chunks: list[dict], resolved: list[dict], toc_pages: range | None = None) -> int:
    """把 chapter_path 掛到每一頁：章級給「章」，節級給「章 / 節」。"""
    resolved = sorted(resolved, key=lambda e: e["pdf_page"])
    touched = 0
    for c in chunks:
        # 目次自己那幾頁是呼叫者指定的，不必從內容猜（續頁看不到「目次」兩個字）。
        # reader 會把同名的連續條目收成一條，所以三頁只會出現一個「目次」。
        if toc_pages and c["page_number"] in toc_pages:
            if c.get("chapter_path") != "目次":
                c["chapter_path"] = "目次"
                touched += 1
            continue
        current = [e for e in resolved if e["pdf_page"] <= c["page_number"]]
        if not current:
            # 🚨 首條目之前的頁（封面／版權頁／目次）要把舊值清掉，不能放著不管。
            #    standardize 會從目次頁的內文推出「第三章…」這種 chapter_path，
            #    留著就是目次頁掛著別章的名字 —— 側欄看起來有東西，點進去是目次。
            label = front_matter_label(c.get("content") or "")
            if c.get("chapter_path") != label:
                c["chapter_path"] = label
                touched += 1
            continue
        entry = current[-1]
        if entry["level"] == 1:
            path = tidy(entry["title"])
        else:
            tops = [e for e in current if e["level"] == 1]
            path = (f"{tidy(tops[-1]['title'])} / {tidy(entry['title'])}"
                    if tops else tidy(entry["title"]))
        if c.get("chapter_path") != path:
            touched += 1
        c["chapter_path"] = path
    return touched


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", required=True)
    ap.add_argument("--toc-pages", required=True, help="目次在 PDF 的第幾頁，例 4-6")
    ap.add_argument("--apply", action="store_true", help="寫回 JSONL＋R2（預設只看）")
    ap.add_argument("--extra", action="append", default=[], metavar="PDF頁=標題",
                    help="人工補一條（標題跟內文黏成一段、機器切不出來時）。"
                         "照樣要過驗證閘：那一頁的內容裡找不到這個標題就不收。")
    args = ap.parse_args()

    from dotenv import load_dotenv
    load_dotenv(REPO / ".env")
    import ocr_with_gemini as og

    src = og.CHUNKS_DIR / f"{args.book}.jsonl"
    chunks = [json.loads(l) for l in src.read_text(encoding="utf-8").splitlines() if l.strip()]
    by_page = {c["page_number"]: c for c in chunks}
    lo, _, hi = args.toc_pages.partition("-")
    toc_pages = range(int(lo), int(hi or lo) + 1)

    lines: list[str] = []
    for p in toc_pages:
        lines += (by_page[p].get("content") or "").splitlines()
    entries, orphans = parse_toc_lines(lines)
    anchors = [(c["page_number"], c["printed_page"]) for c in chunks if c.get("printed_page")]
    print(f"目次頁 {list(toc_pages)}：解出 {len(entries)} 條，錨點 {len(anchors)} 個")

    max_printed = max((p for _, p in anchors), default=0)
    resolved, dropped = [], []
    for e in entries:
        hit = None
        for cand in digit_candidates(e["printed_page"], max_printed):
            guess = resolve_page(cand, anchors)
            hit = verify(guess, e["title"], by_page) if guess else None
            if hit is not None:
                e = {**e, "printed_page": cand}
                break
        if hit is None:
            dropped.append(e)
            continue
        resolved.append({**e, "pdf_page": hit})

    # 殘料救援：目次行壞掉的兩種長相，都還是要過「那一頁真的有這個東西」的閘。
    rescued = []
    for line in list(orphans):
        m = _ENTRY.match(line)
        if m and not m.group("title").strip(" .．·・…‥"):
            # 有頁碼、標題被吃掉 → 用那一頁自己的第一行當章名
            for cand in digit_candidates(int(m.group("page")), max_printed):
                page = resolve_page(cand, anchors)
                title = title_from_page(page, by_page) if page else None
                if title:
                    rescued.append({"title": title, "printed_page": cand,
                                    "level": 1, "pdf_page": page, "how": "標題取自該頁首行"})
                    orphans.remove(line)
                    break
            continue
        # 有標題、沒頁碼 → 到內文裡找它第一次出現在哪
        title = line.strip(" .．·・…‥")
        page = find_by_title(title, by_page, skip=set(toc_pages))
        if page:
            level = 1 if (_TOP_PREFIX.match(title) or title.startswith(_TOP_NAMES)) else 2
            rescued.append({"title": title, "printed_page": by_page[page].get("printed_page"),
                            "level": level, "pdf_page": page, "how": "目次無頁碼，內文比對"})
            orphans.remove(line)
    resolved += rescued

    for spec in args.extra:
        page_s, _, title = spec.partition("=")
        page = int(page_s)
        if verify(page, title, by_page, window=0) is None:
            print(f"🚨 --extra {spec}：PDF {page} 的內容裡找不到「{title}」，不收")
            continue
        level = 1 if (_TOP_PREFIX.match(title) or title.startswith(_TOP_NAMES)) else 2
        resolved.append({"title": title, "printed_page": by_page[page].get("printed_page"),
                         "level": level, "pdf_page": page, "how": "人工指定（已驗證）"})

    print(f"\n對上 {len(resolved)} 條：")
    for e in sorted(resolved, key=lambda x: x["pdf_page"]):
        mark = "  " if e["level"] == 1 else "    ・"
        note = f"　←{e['how']}" if e.get("how") else ""
        print(f"{mark}{e['title']}　印刷 {e['printed_page']} → PDF {e['pdf_page']}{note}")
    if dropped:
        print(f"\n🚨 對不上、已丟棄 {len(dropped)} 條（寧可少，不要掛錯章）：")
        for e in dropped:
            print(f"  {e['title']}（印刷 {e['printed_page']}，推算 PDF "
                  f"{resolve_page(e['printed_page'], anchors)}）")
    if orphans:
        print(f"\n殘料 {len(orphans)} 條（目次上沒有可用頁碼）：{orphans}")

    if not args.apply:
        print("\n（預設不寫檔。要寫加 --apply）")
        return 0

    touched = assign(chunks, resolved, toc_pages)
    tmp = src.with_suffix(".jsonl.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for i, c in enumerate(chunks):
            c["chunk_index"] = i
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    tmp.replace(src)
    og.push_to_r2(args.book, src)
    print(f"\n✓ {touched} 段掛上 chapter_path，已寫回並推 R2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
