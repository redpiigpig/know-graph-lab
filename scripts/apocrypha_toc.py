# -*- coding: utf-8 -*-
"""讀一冊書自己的**目錄**，得出「這一冊有哪幾部作品、各從第幾頁起」。

    python scripts/apocrypha_toc.py --vol cct-nt-1

這是定界的第三個錨，而且是最權威的一個——書自己列的篇目表，帶卷次與**印刷頁碼**。
另外兩個錨見 `apocrypha_map_volumes.py`（書眉、正文卷首）。三個錨互相對帳：

    目錄  說「第二部分 卷五 阿拉伯語耶穌嬰孩時期福音 從印刷頁 110 起」
    書眉  說「印刷頁 111–132 這些頁屬於第二部分卷五」
    卷首  說「某個實體頁上有 title『阿拉伯語…』＋title『簡介』」

三者要指向同一個地方。對不上就列出來，不要自己挑一個信。

🚨 目錄的頁碼是**印刷頁**，不是 PDF 的第幾張。兩者差一個不固定的位移（序、目錄用
另一套編號，還有插頁），所以一律拿印刷頁去對，不要換算成實體頁再比。
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

from apocrypha_map_volumes import block_text, cn_int, find_middle, read_volume  # noqa: E402

# 「卷一 獨立存留的耶穌語錄........9」——中間那串點是排版的引導點，長度不定，
# 而且 OCR 會把它認成 . … ． 。 等等各種東西，所以用「非數字的一串」去吃掉。
#
# 🚨 卷號與書名之間**常常沒有空白**，而書名本身又常以中文數字開頭，所以「把卷後面
#    那一串中文數字全部當成卷號」會靜默吃掉書名的第一個字：
#        卷四十二使徒福音   ＝ 卷四 ＋《十二使徒福音》  → 曾被讀成「卷42」
#        卷九七十長老福音   ＝ 卷九 ＋《七十長老福音》  → 曾被讀成「卷10」（與卷十撞號）
#    兩次都不會報錯，只會多出不存在的卷、或讓兩卷共用一個號。所以卷號改成
#    **按預期的下一卷去挑最短的前綴**（見 _juan_prefix），不貪心。
TOC_ITEM = re.compile(r"^卷([一二三四五六七八九十廿卅]+)\s*(.*?)[.．。…\s·､、]*(\d{1,3})\s*$")
TOC_PART = re.compile(r"^第([一二三四五六七八九十]+)部分\s*(.*)$")
# 目錄裡不帶卷號、但仍是獨立區段的條目（各部分的總簡介、序、附錄）。
# 🚨 「簡介」不一定自己成行：第四冊有一條「啟示文學與有關課題的簡介....... 100」，
#    只比對行首會漏掉它，而漏掉一條界線就讓前一部作品（彼得宣講集 81）從 99 頁
#    一路吃到 107 頁。所以改成**以簡介結尾**也算。
TOC_PLAIN = re.compile(r"^(序|.*簡介|.*對照)[.．。…\s]*(\d{1,3})?\s*$")
# 標題太長被折成兩行時，頁碼落在第二行。第一行長這樣：「卷七 阿倫德爾抄本404的」
TOC_CONT = re.compile(r"^卷([一二三四五六七八九十]+)\s*(.+?)[^\d]*$")


def _juan_prefix(run: str, want: int) -> tuple[int | None, str]:
    """「卷」後面那串中文數字 → (卷號, 其實屬於書名的那幾個字)。

    挑**最短且等於預期卷號**的前綴。挑不到就退回整串（並回報 None 讓上層看見），
    不要自己選一個看起來合理的——那正是「卷42」與重複「卷10」的來源。
    """
    for n in range(1, len(run) + 1):
        if cn_int(run[:n]) == want:
            return want, run[n:]
    return cn_int(run), ""


def parse_toc(pages: list[dict]) -> tuple[list[dict], list[str]]:
    """→ (條目, 沒認出來的行)。條目 = {kind, part, juan, title, printed}。

    🚨 各部分的「簡介」與卷首的總簡介、卷末的附錄**也要當條目收**，雖然它們不是
    作品。理由是下游要靠「下一個條目的起始頁」去定出每一部作品的**結束頁**：
    第二部分卷十《馬利亞的出生》從 173 起，而它結束在哪裡，只有「第三部分 簡介
    從 182 起」這一條講得出來。把它們當雜訊丟掉，每一部分的最後一部作品就會
    一路吃到下一部作品的開頭。
    """
    # 🚨 目錄只在冊首那幾頁，但 `index` 這個型別在書裡別處也會出現：第四冊的
    #    《基督教西卜神諭篇》是帶行號的長詩（「324而且，偉大神的兒子…」），
    #    MinerU 把整片詩行判成 index，於是那些行號被當成目錄頁碼讀進來，
    #    憑空長出幾十個「作品」。所以只吃**第一段連續的 index 頁**，
    #    一旦中斷就停——目錄本身是連著印的，不會中間隔幾十頁再出現。
    lines: list[str] = []
    started = False
    for p in pages:
        idx_blocks = [t for kind, t in p["blocks"] if kind == "index"]
        if idx_blocks:
            started = True
            for text in idx_blocks:
                lines += [ln.strip() for ln in text.split("\n") if ln.strip()]
        elif started:
            break
    items: list[dict] = []
    junk: list[str] = []
    # 🚨 第一個部分**不一定印「第一部分」**：第二冊開頭直接寫「諾斯底福音書」，
    #    第三冊整冊六部行傳根本沒有分部。留 None 的話下游得拿 None 當鍵，
    #    而那個 None 的意思是「解析器沒看到標題」，不是書的結構——很容易配錯。
    #    在第一個「第N部分」出現前的卷，一律算第一部分。
    part = 1
    want_juan = 1
    pending: tuple[int, str] | None = None      # 標題折行時暫存
    for ln in lines:
        mp = TOC_PART.match(ln)
        if mp:
            part = cn_int(mp.group(1))
            want_juan = 1                        # 卷號在每個部分底下重新編
            pending = None
            continue
        mi = TOC_ITEM.match(ln)
        if mi:
            juan, extra = _juan_prefix(mi.group(1), want_juan)
            # 卷號倒退回 1 卻沒看到「第N部分」那一行 → 那行 OCR 掉了。照樣進位，
            # 不然接下來整個部分都會掛在上一個部分底下（界線不受影響，但標錯）。
            if juan == 1 and want_juan > 1:
                part = (part or 0) + 1
            title, printed = (extra + mi.group(2)).strip(), int(mi.group(3))
            if pending:                          # 上一行是折行的開頭，這行才有頁碼
                juan, title = pending[0], (pending[1] + title).strip()
                pending = None
            items.append({"kind": "work", "part": part, "juan": juan,
                          "title": title, "printed": printed})
            if juan is not None:
                want_juan = juan + 1
            continue
        if pending:
            # 折行的下半：沒有卷號、結尾才是頁碼
            m = re.match(r"^(.*?)[.．。…\s]*(\d{1,3})\s*$", ln)
            if m:
                items.append({"kind": "work", "part": part, "juan": pending[0],
                              "title": (pending[1] + m.group(1)).strip(),
                              "printed": int(m.group(2))})
                pending = None
                continue
            pending = (pending[0], pending[1] + ln)
            continue
        mc = TOC_CONT.match(ln)
        if mc and not re.search(r"\d\s*$", ln):
            pending = (cn_int(mc.group(1)), mc.group(2).strip())
            continue
        mt = TOC_PLAIN.match(ln)
        if mt:
            title, printed = mt.group(1).strip(), mt.group(2)
            if printed is None:                  # 「序..」目錄上沒印頁碼
                junk.append(f"（沒有頁碼，無法當界線）{ln}")
                continue
            kind = "appendix" if "對照" in title else "intro"
            items.append({"kind": kind, "part": part, "juan": None,
                          "title": title, "printed": int(printed)})
            continue
        junk.append(ln)
    items.sort(key=lambda it: it["printed"])
    return items, junk


def load(slug: str) -> tuple[list[dict], list[str], list[dict]]:
    """目錄只在冊首幾頁，所以整冊還沒併好也能讀——直接吃第 0 批。"""
    vol_dir = REPO / "output" / "apocrypha-ocr" / slug
    merged = vol_dir / f"{slug}_middle.json"
    if merged.exists():
        pages = read_volume(slug)
    else:
        b0 = sorted(vol_dir.glob("b0000/**/*_middle.json"))
        if not b0:
            raise SystemExit(f"{slug} 連第 0 批都還沒好")
        mid = json.loads(b0[0].read_text(encoding="utf-8"))
        pages = []
        for page in mid.get("pdf_info") or []:
            blocks = [(b.get("type"), block_text(b)) for b in (page.get("preproc_blocks") or [])]
            pages.append({"idx": int(page.get("page_idx", len(pages))),
                          "blocks": [(k, t) for k, t in blocks if t]})
    items, junk = parse_toc(pages)
    return items, junk, pages


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--vol", required=True)
    ap.add_argument("--json", help="另存一份 JSON")
    a = ap.parse_args()

    items, junk, _ = load(a.vol)
    works = [it for it in items if it["kind"] == "work"]
    print(f"════ {a.vol} 目錄：{len(works)} 部作品"
          f"（另有 {len(items) - len(works)} 條簡介／附錄，當界線用）")
    cur = object()
    for it in items:
        if it["part"] != cur:
            cur = it["part"]
            print(f"\n  ── 第{cur}部分" if cur is not None else "\n  ── （卷首）")
        tag = f"卷{it['juan']:<3}" if it["juan"] is not None else f"{it['kind']:<5}"
        print(f"     {tag} 印刷頁 {it['printed']:>4}　{it['title']}")
    if junk:
        print(f"\n  ── 沒當成作品的 {len(junk)} 行")
        for j in junk:
            print(f"     {j}")
    if a.json:
        Path(a.json).write_text(json.dumps(items, ensure_ascii=False, indent=2),
                                encoding="utf-8")
        print(f"\n  → {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
