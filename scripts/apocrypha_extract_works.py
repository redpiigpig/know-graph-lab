# -*- coding: utf-8 -*-
"""把一冊書拆成一部一部作品：目錄定界 → 書眉對帳 → 逐部切節。

    python scripts/apocrypha_extract_works.py --vol cct-nt-1
    python scripts/apocrypha_extract_works.py --vol cct-nt-1 --work 雅各原始福音 --show 5
    python scripts/apocrypha_extract_works.py --vol cct-nt-1 --json output/...json

三個零件各司其職，本檔只做組裝：
    apocrypha_toc.py         這一冊有哪幾部、各從印刷第幾頁起（權威來源）
    apocrypha_map_volumes.py 書眉說每一頁屬於哪一卷（拿來對帳）
    apocrypha_sectionize.py  一部作品的頁 → 節（純函式）

🚨 一部作品的**結束頁**來自「目錄裡下一個條目的起始頁」，所以目錄的簡介與附錄
   條目一定要一起收（見 apocrypha_toc.parse_toc 的說明）。
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

from apocrypha_map_volumes import (block_text, extract_blocks, head_juan,  # noqa: E402
                                   read_volume)
from apocrypha_sectionize import choose  # noqa: E402
from apocrypha_missing_numbers import for_work  # noqa: E402
from apocrypha_toc import load as load_toc  # noqa: E402

INTRO_TITLE = "簡介"
TEXT_TITLE = "文本"
CREDIT = re.compile(r"^(翻譯|審閱|譯者|審閱者)[：:]")


def load_pages(slug: str) -> tuple[list[dict], list[tuple[int, int]]]:
    """整冊的頁。併好就讀併好的；還沒併就把現有批次接起來並回報缺哪幾段。

    🚨 回傳第二個值是**還沒 OCR 的頁區間**。跑到一半就來看結果是常態（OCR 要幾個
    小時），但「這一部作品只切出三節」到底是切壞了還是頁還沒到，一定要分得出來。
    """
    merged = OUT_ROOT / slug / f"{slug}_middle.json"
    if merged.exists():
        return read_volume(slug), []
    from mineru_ocr import pages_from_middle
    pages: list[dict] = []
    have: set[int] = set()
    for bdir in sorted((OUT_ROOT / slug).glob("b[0-9]*")):
        mids = sorted(bdir.rglob("*_middle.json"))
        if not mids:
            continue
        start = int(bdir.name[1:])
        mid = json.loads(mids[0].read_text(encoding="utf-8"))
        carried: list[str] | None = None
        for page in mid.get("pdf_info") or []:
            idx = int(page.get("page_idx", 0)) + start
            heads, notes, printed = [], [], None
            for b in page.get("discarded_blocks") or []:
                t = block_text(b)
                if not t:
                    continue
                if b.get("type") == "header":
                    heads.append(" ".join(t.split()))
                elif b.get("type") == "page_footnote":
                    notes.append(" ".join(t.split()))
                elif b.get("type") == "page_number":
                    m = re.search(r"\d{1,4}", t)
                    if m and printed is None:
                        printed = int(m.group())
            raw, carried = extract_blocks(page.get("preproc_blocks") or [], carried)
            pages.append({"idx": idx, "printed": printed, "heads": heads, "notes": notes,
                          "blocks": [(k, t) for k, t, _ in raw],
                          "boxes": [bb for _, _, bb in raw],
                          "paras": [t for k, t, _ in raw]})
            have.add(idx)
    pages.sort(key=lambda p: p["idx"])
    gaps, run = [], None
    for i in range(0, (max(have) + 1) if have else 0):
        if i not in have:
            run = (i, i) if run is None else (run[0], i)
        elif run:
            gaps.append(run)
            run = None
    if run:
        gaps.append(run)
    return pages, gaps


def markers_of(page: dict) -> set[int]:
    """這一頁的註腳標記集合 —— 用來把註腳標記和節號分開。"""
    out = set()
    for n in page["notes"]:
        m = re.match(r"^(\d{1,3})", n)
        if m:
            out.add(int(m.group(1)))
    return out


def fill_printed(pages: list[dict]) -> None:
    """卷首頁與插頁不印頁碼，用前後頁的印刷頁碼推。推不出來就留 None。

    🚨 只在「前一頁有印刷頁碼」時 +1，不用全域位移去算——位移不是常數（序用羅馬
    數字、插頁不編號），拿一個 offset 推整本會產生**假頁碼**，比沒有更糟。
    """
    for i, p in enumerate(pages):
        if p["printed"] is not None:
            continue
        prev = pages[i - 1] if i else None
        if prev and prev["printed"] is not None:
            p["printed"] = prev["printed"] + 1
            p["printed_inferred"] = True


def slice_work(pages: list[dict], lo: int, hi: int) -> list[dict]:
    return [p for p in pages if p["printed"] is not None and lo <= p["printed"] <= hi]


def two_column_pages(work_pages: list[dict]) -> list[int]:
    """找出**雙欄並排**的頁。回傳那些頁的印刷頁碼。

    🚨 這套書會把同一段的兩種抄本並排印成兩欄（《雅各原始福音》第 18–21 章就是
    「伯默蒲草紙5」與「一些後期的抄卷」對照）。MinerU 是**照欄**吐區塊的（先整個
    左欄、再整個右欄），不是照 y 交錯，所以文字本身沒壞；壞的是把兩欄接成一條
    流之後**同一組章節號會出現兩次**，於是連號閘從第二欄開始就再也對不上，
    後面每一章都被併進同一節。症狀正是「一篇讀到一半沒了，接著冒出隔壁的條目」。

    這種頁要當成兩個**版本**（DB 的 version_code）分開收，不能串成一條。本函式
    只負責認出來並回報，不自己決定怎麼收。
    """
    hits = []
    for p in work_pages:
        pairs = [(bb, t) for bb, (_k, t) in zip(p.get("boxes") or [], p["blocks"])
                 if bb and bb[2] > bb[0]]
        if len(pairs) < 4:
            continue
        lo = min(bb[0] for bb, _ in pairs)
        hi = max(bb[2] for bb, _ in pairs)
        mid = (lo + hi) / 2
        left = [t for bb, t in pairs if bb[2] <= mid + 5]
        right = [t for bb, t in pairs if bb[0] >= mid - 5]
        # 🚨 只看「兩邊都有區塊」會誤判：單欄的教父摘錄把**出處**靠右排（《伊便尼
        #    派人福音》p43 的「——伊皮法紐《反異端》30：13：6」），右半邊自然就有
        #    區塊。真正的並排雙欄，兩欄各自都是**成段的正文**，所以要求兩邊都至少
        #    有一塊夠長的文字；靠右的出處行都很短，過不了這一關。
        if (sum(1 for t in left if len(t) >= 40) >= 1
                and sum(1 for t in right if len(t) >= 40) >= 1):
            hits.append(p["printed"])
    return hits


def classify_columns(page: dict) -> list[str]:
    """這一頁每個區塊落在哪一欄：'full'／'left'／'right'。單欄頁全部是 'full'。"""
    boxes = [bb for bb in page.get("boxes") or []]
    kinds = ["full"] * len(boxes)
    if page["printed"] not in set(two_column_pages([page])):
        return kinds
    good = [bb for bb in boxes if bb and bb[2] > bb[0]]
    lo, hi = min(b[0] for b in good), max(b[2] for b in good)
    mid = (lo + hi) / 2
    for i, bb in enumerate(boxes):
        if not bb or bb[2] <= bb[0]:
            continue
        if bb[2] <= mid + 5:
            kinds[i] = "left"
        elif bb[0] >= mid - 5:
            kinds[i] = "right"
    return kinds


def peel_columns(work_pages: list[dict]) -> tuple[dict[int, list[tuple[str, str]]], list[int]]:
    """把**右欄**從正文流裡摘出來，回傳 {右欄起始的區塊序號: [(標籤, 文字)]}。

    🚨 兩欄是同一組節號的兩種抄本讀法（見 two_column_pages）。左右接成一條流之後
    同一個 `201` 會出現兩次，連號閘從第二欄起就再也對不上，後面整卷併成一節。

    依使用者定案：**單一版本＋行內標籤**——左欄留在正文流裡（節號因此連得下去），
    右欄摘出來，之後以書上原本的欄標（「一些後期的抄卷」「(修訂版本二)」）為前綴，
    附在該處那一節後面。兩種讀法都留著，不動 schema、不開第二個 version_code。
    """
    secondary: dict[int, list[tuple[str, str]]] = {}
    labels: list[int] = []
    for p in work_pages:
        kinds = classify_columns(p)
        if "right" not in kinds:
            continue
        labels.append(p["printed"])
        # 欄標是該欄第一塊很短的字（「伯默蒲草紙5」「(修訂版本一)」）
        cur_label, run, anchor = "", [], None
        for i, ((_k, t), c) in enumerate(zip(p["blocks"], kinds)):
            if c != "right":
                if run:
                    secondary.setdefault(anchor, []).extend((cur_label, x) for x in run)
                    cur_label, run, anchor = "", [], None
                continue
            if anchor is None:
                anchor = (p["printed"], i)
            if not run and len(t.strip()) <= 14:
                cur_label = t.strip().strip("()（）")
                continue
            run.append(t)
        if run:
            secondary.setdefault(anchor, []).extend((cur_label, x) for x in run)
    return secondary, labels


def split_front(work_pages: list[dict]) -> tuple[list[str], list[dict], str | None, bool]:
    """把一部作品的頁切成（簡介, 正文段落, 作品名）。

    書上每一卷固定是：title「<作品名>」→ title「簡介」→ 簡介正文 → title「文本」
    → 文獻本身。「文本」之前、簡介之後的東西（例如阿拉伯語那篇的三一頌開場白）
    屬於文獻的序言，不是簡介。
    """
    name = None
    intro: list[str] = []
    body: list[dict] = []
    seen_intro = False
    seen_text = False
    for p in work_pages:
        kinds = classify_columns(p)
        col_label = ""
        for (kind, text), col in zip(p["blocks"], kinds):
            t = text.strip()
            if col == "right":
                continue            # 右欄另外收（peel_columns），不進正文流
            # 🚨 這兩個小標**認字面、不認區塊型別**，而且要容得下括號說明。踩過兩次：
            #    ①《希伯來人福音》印的是「文本（教父摘錄）」，用相等比就認不出來；
            #    ②《雅各原始福音》的「文本」被 MinerU 判成 text 不是 title。
            #    兩者的後果一樣：整卷認不出正文起點 → 退回「整卷都是正文」那條路 →
            #    **簡介被靜默丟掉**（它們不帶節號，在第一節出現前沒有歸屬）。
            #    長度限制是為了不要把正文裡剛好以「文本」開頭的句子誤當小標。
            if not seen_text and len(t) <= 12 and t.startswith(TEXT_TITLE):
                seen_text = True
                continue
            if not seen_intro and len(t) <= 12 and t.startswith(INTRO_TITLE):
                seen_intro = True
                continue
            if not seen_intro and kind == "title" and name is None:
                name = t
                continue
            # 🚨 欄標的判斷一定要排在「文本／簡介」之後。《巴多羅買福音》的「文本'」
            #    印得很窄（x43–72），會被歸進左欄；先判欄標就把正文起點吃掉了，
            #    於是整卷退回「都是正文」那條路、簡介又一次消失。
            if col == "left" and not col_label and len(t) <= 14:
                col_label = t.strip("()（）")   # 左欄的欄標，冠在該段前面
                continue
            if col == "full":
                col_label = ""
            if seen_text:
                body.append({"page": p["printed"], "text": text, "kind": kind,
                             "col_label": col_label})
            elif seen_intro:
                intro.append(text)
            elif name is not None:
                intro.append(text)          # 沒有「簡介」小標的卷，開頭仍算簡介
    if not seen_text:                        # 有些卷沒有「文本」小標
        # 這條退路也要濾掉右欄，否則雙欄頁的兩種讀法又會接成一條流。
        body = []
        for p in work_pages:
            for (k, t), col in zip(p["blocks"], classify_columns(p)):
                if col != "right":
                    body.append({"page": p["printed"], "text": t, "kind": k,
                                 "col_label": ""})
        intro = []
    return intro, body, name, seen_text


def run(slug: str, only: str | None, show: int, as_json: str | None) -> int:
    items, _junk, _ = load_toc(slug)
    pages, gaps = load_pages(slug)
    fill_printed(pages)
    printed_hi = max((p["printed"] for p in pages if p["printed"]), default=0)
    if gaps:
        print(f"⚠ 還沒 OCR 的實體頁區間：{gaps}（下面的結果只涵蓋已完成的部分）\n")

    works = [it for it in items if it["kind"] == "work"]
    out = []
    for i, it in enumerate(items):
        if it["kind"] != "work":
            continue
        lo = it["printed"]
        hi = (items[i + 1]["printed"] - 1) if i + 1 < len(items) else printed_hi
        if only and only not in it["title"]:
            continue
        wp = slice_work(pages, lo, hi)
        if not wp:
            print(f"  ── 第{it['part']}部分 卷{it['juan']}　{it['title']}"
                  f"　印刷 {lo}–{hi}　（頁還沒 OCR 到，跳過）")
            continue
        markers = {p["printed"]: markers_of(p) for p in wp}
        intro, body, name, _seen = split_front(wp)
        sp, msg = choose(body, markers, first=1, missing=for_work(it["title"]))
        # 逐段點名（交接單 §E）：字數不是好閘，差幾十字都能說成正常；要問的是
        # **每一個 preproc 段落是不是都有歸屬**。這裡不必事後比對字串——切節本身
        # 已經是完整分割（進某一節／進序言，沒有第三條路），見 Split.prologue。
        # 書眉對帳：這一段頁的書眉是不是都指向同一卷
        heads = {head_juan(p)[1] for p in wp if head_juan(p)[1] is not None}
        head_ok = heads in ({it["juan"]}, set())
        twocol = two_column_pages(wp)
        print(f"  ── 第{it['part']}部分 卷{it['juan']}　{it['title']}　印刷 {lo}–{hi}"
              f"（{len(wp)} 頁）")
        print(f"       卷首名 {name or '（沒抓到）'}　簡介 {len(intro)} 段　"
              f"註腳 {sum(len(p['notes']) for p in wp)} 條")
        if twocol:
            print(f"       🚨 雙欄並排 {len(twocol)} 頁（印刷 {twocol[0]}–{twocol[-1]}）"
                  f"：兩種抄本對照，要當兩個版本分開收，不能串成一條")
        print(f"       書眉 {'✓ 全指向本卷' if head_ok else f'⚠ 指向 {sorted(heads)}'}"
              f"　切節 {msg}"
              f"　{'✓ 點名 0 段落外　序言 %d 段' % len(sp.prologue) if sp else ''}")
        if sp and show:
            for s in sp.sections[:show]:
                print(f"         §{s.label} p{s.page} {s.paras[0][:44]}")
        out.append({"part": it["part"], "juan": it["juan"], "title": it["title"],
                    "printed_from": lo, "printed_to": hi, "pages": len(wp),
                    "scheme": sp.scheme if sp else None,
                    "sections": len(sp.sections) if sp else 0,
                    "note": msg, "head_ok": head_ok,
                    "prologue_paras": len(sp.prologue) if sp else 0,
                    "two_column_pages": twocol,
                    "intro_paras": len(intro)})
    done = sum(1 for o in out if o["sections"])
    print(f"\n═══ {slug}：目錄 {len(works)} 部；本次處理 {len(out)} 部，"
          f"切出節的 {done} 部")
    if as_json:
        Path(as_json).write_text(json.dumps(out, ensure_ascii=False, indent=2),
                                 encoding="utf-8")
        print(f"  → {as_json}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--vol", required=True)
    ap.add_argument("--work", help="只看標題含這個字的作品")
    ap.add_argument("--show", type=int, default=0, help="每部印前幾節")
    ap.add_argument("--json")
    a = ap.parse_args()
    return run(a.vol, a.work, a.show, a.json)


if __name__ == "__main__":
    raise SystemExit(main())
