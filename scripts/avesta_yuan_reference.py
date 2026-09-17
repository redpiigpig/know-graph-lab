#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
元文琪譯《阿維斯塔》→ /avesta 的「既有中譯」對照欄。

    python scripts/avesta_yuan_reference.py --build
    python scripts/avesta_yuan_reference.py --build --only yasna-30
    python scripts/avesta_yuan_reference.py --coverage

═══════════ 這份譯本是什麼、不是什麼 ═══════════

🚨 **它是選編本，不是全譯本。**（2026-09-17 翻目次核對）
   杜斯特哈赫選編的波斯文本 → 元文琪譯，商務印書館。收的是：
     伽薩全 17 章（＝亞斯納 28–34、43–51、53）
     亞斯納 9、10、12 三章（共 72 章）
     亞什特 5、8、10、13、14、19 六首（共 21 首）
     萬迪達德 5、7 兩章（共 22 章）／維斯帕拉德 7、15 兩章（共 24 章）
     小阿維斯陀：大西魯澤、阿法林甘四篇
   所以本欄**只在這 30 篇出現**，其餘各篇仍是空的，不是漏抓。

🚨 **它的專名是波斯語形式，不是阿維斯陀語形式。**
   巴赫曼（Bahman）＝沃胡‧馬納、奧爾迪貝赫什特（Ordibehesht）＝阿沙‧瓦希什塔、
   索魯什＝斯魯沙、塞潘達爾馬茲＝斯彭塔‧阿爾邁提。
   本站正文用的是阿維斯陀語形式（詞庫定名），兩套不可混用——
   拿巴赫曼去譯阿維斯陀語原文是把中古波斯的用語套回一千多年前。
   故本欄**原樣呈現、不改字**，並在版面上標明它是另一套譯名系統。

═══════════ 節號怎麼來的（這是本支最脆弱的地方）═══════════

本書的節號印成置中獨立一行的中文數字。**MinerU 會丟掉「一二三十」**
（純橫豎筆畫，版面分析判成分隔線），詳見 scripts/avesta_yuan_lines.py。
故節號有兩個來源：

  四以上　MinerU 讀得到，直接用（獨立成行的中文數字）
  一二三十 由 avesta_yuan_lines 幾何還原（數橫劃：一條＝一、兩條＝二、三條＝三）

🚨 **幾何還原要求該頁的行數與 MinerU 完全一致**（341 頁中 238 頁符合）。
   不一致就表示有行被併掉或多切，插入位置會差一格，於是某一節的頭一行
   會被算進上一節——版面完全正常，只有對照的人會發現接不上。
   所以不一致的頁**不補節號**，那一章的前幾節合成一塊並標明「第 1–N 節（未逐節切分）」。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

OUT_DIR = ROOT / "data" / "avesta" / "sources" / "yuan"
JSONL = r"G:/我的雲端硬碟/資料/知識圖工作室/_chunks/6d731f04-664d-4459-826e-0dba1dbefc4b.jsonl"
MARKERS = ROOT / "output" / "yuan_markers.json"

BODY_FROM, BODY_TO = 36, 376  # 正文；377 起是導讀，那裡的章次是學術引用不是譯文

CN = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}


def cn_to_int(s: str) -> int | None:
    """中文數字 → 阿拉伯數字。認不得回 None。

    🚨 **這本書一百以上用位值寫法**：一〇七＝107、一二〇＝120、一四〇＝140，
       不寫「一百零七」。只認「百／十」那一套的話，長亞什特每首會靜靜少掉
       三四十節（亞什特 5、10、13、19 的節號都超過 100），
       而 --coverage 只會顯示「最大節號 99」——看起來像譯本收到這裡為止。

    >>> [cn_to_int(x) for x in ('一', '十', '十二', '二十', '二十四')]
    [1, 10, 12, 20, 24]
    >>> [cn_to_int(x) for x in ('一〇七', '一二〇', '一四〇', '一一五')]
    [107, 120, 140, 115]
    >>> cn_to_int('第三章') is None
    True
    """
    if not s or not all(c in "一二三四五六七八九十百零〇" for c in s):
        return None
    # 位值寫法：三位以上且不含「十／百」，或含「〇」——逐字當阿拉伯數字讀。
    digits = {"〇": 0, "零": 0, **CN}
    if ("〇" in s or len(s) >= 3) and "十" not in s and "百" not in s:
        if all(c in digits for c in s):
            n = 0
            for c in s:
                n = n * 10 + digits[c]
            return n
        return None
    if s == "十":
        return 10
    if "百" in s:
        h, rest = s.split("百", 1)
        n = CN.get(h, 0) * 100
        rest = rest.lstrip("零")
        return n + (cn_to_int(rest) or 0) if rest else n
    if "十" in s:
        t, o = s.split("十", 1)
        return (CN.get(t, 1) if t else 1) * 10 + (CN.get(o, 0) if o else 0)
    return CN.get(s)


VERSE_LINE = re.compile(r"^[一二三四五六七八九十百零〇]{1,5}$")
CHAPTER_CN = re.compile(r"^《(亞斯納|亞什特|萬迪達德|維斯帕拉德)》第([一二三四五六七八九十百]+)章")
SECTION_CN = re.compile(r"^第([一二三四五六七八九十]+)(章|篇)\s*(\S{0,16})$")
VOLUME_CN = re.compile(r"^第([一二三四五六])卷\s*(\S{2,10})$")


VERSE_RANGE = re.compile(r"^([一二三四五六七八九十百零〇]{1,5})\s*[—–\-~]\s*([一二三四五六七八九十百零〇]{1,5})$")


def is_verse_marker(line: str) -> int | None:
    """這一行是不是節號？是就回節號的值。

    >>> is_verse_marker('四')
    4
    >>> is_verse_marker('二十四')
    24
    >>> is_verse_marker('第三章') is None
    True
    >>> is_verse_marker('呵，馬茲達！') is None
    True
    """
    t = line.strip()
    if VERSE_LINE.fullmatch(t):
        n = cn_to_int(t)
        # 🚨 破折號會被 OCR 讀成「一」：「八—九」變成「八一九」，
        #    位值解析就把它讀成第 819 節。本書最長的一首（亞什特 10）也只到 145 節，
        #    所以位值解析一旦超過 199 就一定是這種情形——改當成區間讀，取起始節。
        #    （測試釘住：元譯的節號必須全部落在本站該篇實際有的節次裡。）
        if n is not None and n > 199 and len(t) == 3 and t[1] == "一":
            return cn_to_int(t[0])
        if n is not None and n > 199:
            return None
        return n
    # 🚨 節號可以是區間。萬迪達德那兩章把數節合印成一條「一—七」「八—九」，
    #    只認單一數字的話那幾節全部落到上一節裡，而版面完全正常。
    #    區間一律以**起始節號**為鍵，區間資訊寫進 range_note。
    m = VERSE_RANGE.fullmatch(t)
    return cn_to_int(m.group(1)) if m else None


# 元文琪的卷／篇 → 本站 slug。
# 🚨 卷三（亞什特）的「第 N 篇」是**亞什特的編號**，篇底下的「第 N 章」是 karda，
#    而節號是跨 karda 連續編的。所以 karda 標題要略過，只認節號。
YASHT_PIAN = {5: "yasht-05", 8: "yasht-08", 10: "yasht-10",
              13: "yasht-13", 14: "yasht-14", 19: "yasht-19"}
VOL2_CHAPTER = {9: "yasna-09", 10: "yasna-10", 12: "yasna-12"}
VOL4_CHAPTER = {5: "vendidad-05", 7: "vendidad-07"}
# 🚨 卷四的章標題在 OCR 裡變成「第章」——章號整個被吃掉（與節號「一二三」同因）。
#    目次寫明卷四只收第五、第七兩章，且內容可核對（前者是屍體與鷹隼＝Vd 5、
#    後者是行醫者先醫誰＝Vd 7），故依**出現順序**指派。
#    這是推定不是讀出來的，所以寫死在這裡、註明理由，不藏在程式邏輯裡。
VOL4_ORDER = ["vendidad-05", "vendidad-07"]
HEADING_NO_NUMBER = re.compile(r"^第\s*章")
VOL5_CHAPTER = {7: "visperad-07", 15: "visperad-15"}


def slug_for(vol: int, num: int) -> str | None:
    """依所在卷次把「第 N 篇／章」換成本站 slug。對不到回 None。

    >>> slug_for(2, 9), slug_for(3, 10), slug_for(4, 5), slug_for(5, 15)
    ('yasna-09', 'yasht-10', 'vendidad-05', 'visperad-15')
    >>> slug_for(3, 99) is None
    True
    """
    return {2: VOL2_CHAPTER, 3: YASHT_PIAN, 4: VOL4_CHAPTER, 5: VOL5_CHAPTER}.get(vol, {}).get(num)


def lines_with_markers(page: dict, geo: dict | None) -> list[tuple[str, int | None]]:
    """把一頁的 MinerU 行與幾何還原的節號合成一串 [(文字, 節號或 None), …]。

    幾何節號只有在該頁行數與 MinerU 完全一致時才插入（geo['match']）；
    否則整頁只用 MinerU 自己讀到的節號，寧可少切也不錯位。
    """
    text_lines = [t for t in page["content"].split("\n") if t.strip()]
    out: list[tuple[str, int | None]] = []
    if not geo or not geo.get("match") or not geo.get("markers_at"):
        return [(t, None) for t in text_lines]

    # markers_at 是節號行在「全部幾何行」裡的位置；換算成「插在第幾個正文行之前」。
    inserts: dict[int, int] = {}
    seen_text = 0
    strokes: list[int] = []
    for i in range(geo["geo_text"] + len(geo["markers_at"])):
        if i in geo["markers_at"]:
            strokes.append(seen_text)
        else:
            seen_text += 1
    # 連續的筆畫屬於同一個字：位置相同的併成一個，筆畫數就是數值。
    for pos in strokes:
        inserts[pos] = inserts.get(pos, 0) + 1

    for idx, t in enumerate(text_lines):
        if idx in inserts:
            out.append(("", inserts[idx]))
        out.append((t, None))
    return out


def build() -> dict[str, dict[int, str]]:
    """走過正文各頁，切出 {slug: {節號: 中譯}}。"""
    pages = {json.loads(l)["page_number"]: json.loads(l)
             for l in open(JSONL, encoding="utf-8") if l.strip()}
    geo = json.loads(MARKERS.read_text(encoding="utf-8")) if MARKERS.exists() else {}

    texts: dict[str, dict[int, list[str]]] = {}
    vol = 1
    slug: str | None = None
    verse: int | None = None
    unnumbered: list[str] = []

    for pg in range(BODY_FROM, BODY_TO + 1):
        page = pages.get(pg)
        if not page:
            continue
        for line, marker in lines_with_markers(page, geo.get(str(pg))):
            if marker is not None:
                verse = marker
                continue
            t = line.strip()
            if not t:
                continue

            # 🚨 MinerU 自己讀到的節號（四以上）也要認。第一版漏了這一句，
            #    於是每一章都只剩幾何補回來的一、二、三 三節，
            #    而 --coverage 印出來的「2 節／3 節」看起來像是譯本收得少。
            v = is_verse_marker(t)
            if v is not None:
                verse = v
                continue

            m = VOLUME_CN.match(t)
            if m:
                vol, slug, verse = cn_to_int(m.group(1)) or vol, None, None
                continue

            m = CHAPTER_CN.match(t)
            if m:  # 《亞斯納》第二十八章（伽薩）、《萬迪達德》第五章…
                n = cn_to_int(m.group(2))
                # 🚨 四種書名都要映射。第一版只認「亞斯納」，於是卷四的
                #    《萬迪達德》第五章、第七章整整兩章靜靜地沒有產出，
                #    而 --build 印出來的 28 篇看起來像是全部都做完了。
                prefix = {"亞斯納": "yasna", "亞什特": "yasht",
                          "萬迪達德": "vendidad", "維斯帕拉德": "visperad"}[m.group(1)]
                slug = f"{prefix}-{n:02d}" if n else None
                verse, unnumbered = None, []
                continue

            if vol == 4 and HEADING_NO_NUMBER.match(t):
                nth = sum(1 for x in texts if x.startswith("vendidad-"))
                slug = VOL4_ORDER[nth] if nth < len(VOL4_ORDER) else None
                verse = None
                continue

            m = SECTION_CN.match(t)
            if m:
                n = cn_to_int(m.group(1))
                if vol == 3 and m.group(2) == "篇" and n in YASHT_PIAN:
                    slug, verse = YASHT_PIAN[n], None
                elif vol == 3 and m.group(2) == "章":
                    pass  # karda 標題，略過；節號跨 karda 連續
                elif n is not None:
                    got = slug_for(vol, n)
                    if got:
                        slug, verse = got, None
                continue

            if slug is None:
                continue
            if verse is None:
                # 章首還沒遇到任何節號：先收著，最後併成「第 1–N 節」。
                unnumbered.append(t)
                texts.setdefault(slug, {}).setdefault(0, []).append(t)
                continue
            texts.setdefault(slug, {}).setdefault(verse, []).append(t)

    return {s: {n: "".join(v) for n, v in sorted(d.items())} for s, d in texts.items()}


def cmd_build(only: list[str] | None) -> int:
    data = build()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = 0
    for slug, verses in sorted(data.items()):
        if only and slug not in only:
            continue
        head = verses.pop(0, "")
        doc = {
            "slug": slug,
            "translator": "元文琪",
            "source": "杜斯特哈赫（Jalil Doustkhah）選編；元文琪譯，"
                      "《阿維斯塔——瑣羅亞斯德教聖書》，商務印書館（2011 年版）",
            "note": "本譯本譯自波斯文選編本，專名採波斯語形式（巴赫曼＝沃胡‧馬納、"
                    "奧爾迪貝赫什特＝阿沙‧瓦希什塔），與本站正文所用的阿維斯陀語形式不同，"
                    "原樣呈現不改字。簡體原文已轉繁體。",
            "head": head,
            "head_label": "第 1 節之前（未逐節切分）" if head else "",
            "verses": {str(k): v for k, v in verses.items()},
        }
        (OUT_DIR / f"{slug}.json").write_text(
            json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
        written += 1
        chars = sum(len(v) for v in verses.values()) + len(head)
        print(f"✓ {slug:14s} {len(verses):3d} 節　{chars:6,} 字"
              + (f"　（另有 {len(head)} 字未編號）" if head else ""))
    print(f"完成，寫出 {written} 篇 → {OUT_DIR.relative_to(ROOT)}")
    return 0


def cmd_coverage() -> int:
    data = build()
    print(f"元文琪譯本涵蓋 {len(data)} 篇：")
    for slug, verses in sorted(data.items()):
        n = len([k for k in verses if k])
        head = len(verses.get(0, ""))
        print(f"  {slug:14s} {n:3d} 節" + (f"（另 {head} 字未編號）" if head else ""))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="元文琪譯本 → /avesta 對照欄")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--coverage", action="store_true")
    a = ap.parse_args()
    if a.coverage:
        return cmd_coverage()
    if a.build:
        return cmd_build(a.only)
    ap.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
