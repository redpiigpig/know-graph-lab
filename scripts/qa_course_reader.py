# -*- coding: utf-8 -*-
"""課程讀本的成品稽核——排完一定要跑這支，不要等使用者一項一項挑錯。

    python -X utf8 scripts/qa_course_reader.py                 # 三本都查
    python -X utf8 scripts/qa_course_reader.py --book 初階日文讀本.pdf

每一條檢查都對應一次真的踩過的錯（2026-09-08 至 09-10），所以**不要因為
「看起來沒事」就拿掉**：這條線的錯幾乎都是「印出來很正常但內容是壞的」。

  A 目錄印的頁碼要指得到那一篇      舊版印的是 PDF 絕對頁次，每條差 4
  B 每篇要有閱讀導引且排在篇首      使用者翻了十九頁沒看到，以為沒做
  C 導引不可跨頁                    第三個問題老是掉到下一頁
  D 正文不可留頁眉頁腳              「STUDY OF RELIGION: AN OVERVIEW8766」
  E 不可有私用區豆腐格              來源字型把數字對到 PUA，印成「􀀀􀀀􀀀」
  F 不可有黏字                      抽取時漏補空白：「Christendom,but」
  G 篇末不可留參考書目              使用者要求省略
  H 不可留編者寫的作者簡介          選集導言不是要讀的正文
  I 每頁份量要接近                  貪心填滿會讓某頁只剩兩行
  J 頁腳只能有一個號碼              整頁搬運時舊頁碼沒清
  K 正文首行要空兩格
  L 每一篇要真的收尾                Alles 那篇停在句子中間，接著竄進隔壁條目
  M 不可竄進隔壁文章                〈… IN AUSTRALIA AND OCEANIA〉整段跑進來
  N 出處要印完整書目                印成「EoR 8761-8767」，查不到是哪一本書
  O 各個位置的檔要一致              只更新課程夾、送印那疊還是舊的（檔名一模一樣）
  P 附加符號要合進字母              來源把梵文轉寫的附標編成獨立字元：A´soka／bra¯hman:
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
import unicodedata
from pathlib import Path

import fitz

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(r"G:\我的雲端硬碟\玄奘\博一上\上課")
# 讀本的其他擺放位置，跟 build_course_reader.SHARED_OUTS 對齊。
SHARED = (
    Path(r"G:\我的雲端硬碟") / "115-1 課程讀本",                          # 送印那一疊
    Path(r"G:\我的雲端硬碟\資料\知識圖工作室\教學") / "115-1_修課讀本",     # 工作室歸檔
)
BOOKS = {
    "宗教研究方法讀本_上冊.pdf": BASE / "宗教研究基本問題與研究方法",
    "宗教研究方法讀本_下冊.pdf": BASE / "宗教研究基本問題與研究方法",
    "宗教學理論讀本.pdf": BASE / "宗教學理論與方法(一)",
    "初階日文讀本.pdf": BASE / "初階宗教學日文文獻選讀",
}
PUA = re.compile(r"[\ue000-\uf8ff\U000f0000-\U0010ffff]")
# 🚨 只認「標點後面直接接大寫」——HarperCollins、McCutcheon、MacIntyre 這種
# 小寫接大寫本來就合法，連進來就是一堆假警報（2026-09-11 踩過）。
GLUED = re.compile(r"[a-z][,.;:][A-Z][a-z]{2,}")      # 「Christendom,but」「mystery.Valuable」
BIBLIO = re.compile(r"^(bibliography|references|works cited|參考書目)\b", re.I)
BIO = re.compile(r"\bwas born (in|on)\b", re.I)
INDENT_X = 48.0 + 10.8 * 2


def norm(t: str) -> str:
    t = t.replace("\u00ad", "-").replace("\u00a0", " ").replace("\u3000", " ")
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", t)).strip()


def check(path: Path) -> int:
    doc = fitz.open(path)
    toc = doc.get_toc()
    if not toc:
        print(f"★ {path.name} 沒有書籤，無法稽核")
        return 1
    front = toc[0][2] - 1
    pieces = [(t, p) for lvl, t, p in toc if lvl == 1]
    bad: list[str] = []
    print("=" * 74)
    print(f"{path.name}　{doc.page_count} 頁／封面目錄 {front} 頁／篇 {len(pieces)}")

    # A 目錄
    printed = []
    for i in range(1, front):
        for line in doc[i].get_text().split("\n"):
            m = re.match(r"^(.+?)[·ꞏ.\s]{3,}(\d+)$", norm(line))
            if m:
                printed.append((norm(m.group(1)), int(m.group(2))))
    if len(printed) < len(pieces):
        bad.append(f"A 目錄只印了 {len(printed)} 條，篇數 {len(pieces)}")
    for (title, page), (label, shown) in zip(pieces, printed):
        if shown != page - front:
            bad.append(f"A 目錄頁碼 {norm(title)[:34]}：印 {shown}／實際 {page - front}")
        if norm(title)[:10] not in label:
            bad.append(f"A 目錄篇名對不上 {norm(title)[:34]}｜「{label[:34]}」")

    # B / C 導引
    for i, (title, page) in enumerate(pieces):
        end = pieces[i + 1][1] - 1 if i + 1 < len(pieces) else doc.page_count
        first = norm(doc[page - 1].get_text())
        if "閱讀導引" not in first[:60]:
            bad.append(f"B 導引不在篇首 {norm(title)[:34]}（p{page}）")
        n_guide = sum(1 for j in range(page - 1, min(end, doc.page_count))
                      if "閱讀導引" in norm(doc[j].get_text())[:60])
        if n_guide > 1:
            bad.append(f"C 導引跨了 {n_guide} 頁 {norm(title)[:34]}")
        if "可討論的問題" in first:
            bad.append(f"C 導引還印著可討論的問題 {norm(title)[:34]}")

    # D–H 逐頁內容
    heads = {}
    glued_hits, pua_hits, biblio_hits, bio_hits = [], [], [], []
    for i in range(front, doc.page_count):
        t = doc[i].get_text()
        if PUA.search(t):
            pua_hits.append(i + 1)
        body = norm(t)
        for m in GLUED.finditer(body):
            if not m.group(0).isupper():
                glued_hits.append((i + 1, m.group(0)))
        for line in t.split("\n"):
            ln = norm(line)
            # 書目標題是短標題（三個詞以內、不以句號收尾）；正文裡的
            # 「references apart. …」那種句子不算
            if (BIBLIO.match(ln) and len(ln) < 40
                    and len(ln.split()) <= 3 and not ln.endswith(".")):
                biblio_hits.append((i + 1, ln[:30]))
            if BIO.search(ln) and i - front < 3:
                bio_hits.append((i + 1, ln[:40]))
        # 頁眉重複字串混進內文：同一行在同一頁出現兩次以上
        for line in {norm(x) for x in t.split("\n") if 10 < len(norm(x)) < 70}:
            heads[line] = heads.get(line, 0) + 1
    if pua_hits:
        bad.append(f"E 私用區豆腐格 {len(pua_hits)} 頁：{pua_hits[:6]}")
    if glued_hits:
        bad.append(f"F 黏字 {len(glued_hits)} 處：{[g[1] for g in glued_hits[:6]]}")
    if biblio_hits:
        bad.append(f"G 還留著書目標題 {len(biblio_hits)} 處：{biblio_hits[:4]}")
    if bio_hits:
        bad.append(f"H 疑似編者作者簡介：{bio_hits[:3]}")

    # D 頁眉頁腳殘骸。🚨 舊版把 `heads` 數出來卻沒用它判——等於這條根本沒在查。
    #   來源書的頁眉一頁一條，混進正文就會在同一篇裡重複出現十幾次。
    for i, (title, page) in enumerate(pieces):
        end = pieces[i + 1][1] - 1 if i + 1 < len(pieces) else doc.page_count
        tally: dict[str, int] = {}
        for j in range(page - 1, min(end, doc.page_count)):
            for l in {norm(x) for x in doc[j].get_text().split("\n")[2:]}:
                # 短行與以句點收尾的行不算：正文裡「religion.」這種段尾本來就會
                # 在同一篇裡重複好幾次（2026-09-12 誤報過）。頁眉不會有句點。
                if (14 < len(l) < 70 and not l.endswith((".", "?", "!"))
                        and not re.fullmatch(r"[\d\s.]+", l)):
                    tally[l] = tally.get(l, 0) + 1
        dup = [k for k, v in tally.items() if v >= 3]
        if dup:
            bad.append(f"D 疑似頁眉殘骸 {norm(title)[:30]}：{dup[:3]}")

    # P 附加符號要合進字母，不能飄在旁邊。來源文字層把梵文轉寫的附標編成獨立
    #   字元（`A´soka`／`bra¯hman:`），印出來符號就散在字旁（使用者 2026-09-13
    #   指出上冊第 4、5 頁）。
    # 🚨 不要一併查 U+00AD（軟連字號）與 U+037E（希臘問號）：那兩個是 PyMuPDF
    #    產生 ToUnicode 時挑錯碼位，**印出來是正常的 `-` 與 `;`**（2026-09-13 把
    #    目錄那一行渲染成圖確認過），只有複製貼上會拿到怪字元。列進來只會每次
    #    報四千筆假警報。
    stray = [(i + 1, m.group()) for i in range(front, doc.page_count)
             for m in re.finditer(r"[A-Za-z][¯´˚˙˘ˇ¸]"
                                  r"|[¯´][A-Za-z]", doc[i].get_text())]
    if stray:
        bad.append(f"P 附加符號沒合進字母 {len(stray)} 處：{[s[1] for s in stray[:6]]}"
                   f"（頁 {[s[0] for s in stray[:6]]}）")

    # I 每頁份量
    counts = []
    thin_pages = []
    for i in range(front, doc.page_count):
        t = doc[i].get_text()
        if "閱讀導引" in norm(t)[:60]:
            continue
        counts.append((i + 1, len([l for l in t.split("\n") if norm(l)])))
    if counts:
        med = sorted(c for _, c in counts)[len(counts) // 2]
        # 🚨 門檻放在中位數的一半，不是 0.4——舊版 0.4 加上「超過 8% 才報」，
        #    讓「篇首那一頁只有標題」整批溜過去（使用者 2026-09-12 一頁一頁挑出來）。
        #    現在只要有一頁低於中位數一半就報，並且把頁碼印出來。
        thin_pages = [p for p, c in counts if c < max(5, med * 0.5)]
        if thin_pages:
            bad.append(f"I 太空的頁 {len(thin_pages)}／{len(counts)}"
                       f"（中位 {med} 行）：{thin_pages[:10]}")

    # L 每一篇要真的收尾。🚨「印出來很正常但半途沒了」是這條線最貴的錯：
    #   Alles 那篇因為雙欄讀序錯亂，正文停在句子中間，接著竄進隔壁條目
    #   〈… IN AUSTRALIA AND OCEANIA〉（使用者 2026-09-12 指出）。
    END_OK = ('.', '?', '!', '”', '’', '"', ')', ']', '。', '」', '』', '？', '！')
    for i, (title, page) in enumerate(pieces):
        end = pieces[i + 1][1] - 1 if i + 1 < len(pieces) else doc.page_count
        last = ""
        for j in range(end - 1, page - 2, -1):
            lines = [norm(l) for l in doc[j].get_text().split("\n") if norm(l)]
            body = [l for l in lines[2:] if not re.fullmatch(r"\d{1,4}", l)]
            if body:
                last = body[-1]
                break
        # 署名欄不是斷句：文語體的序以「明治三十二年十月三十日／東京角筈村において／
        # 内村鑑三」收尾，三行都沒有句點，但那就是原文的樣子。短行放過。
        # 句末的註號不算沒收句。🚨 只剝「接在句末標點後面」的數字：無條件剝
        # `\d{1,3}$` 會把「Königsberg, Prussia September 30, 1784」剝成
        # 「…September 30, 1」，然後報成斷句（2026-09-12 誤報過）。
        last = re.sub(r"(?<=[.?!])\d{1,3}$", "", last).rstrip()
        # 落款也不是斷句：康德那篇以「Königsberg, Prussia September 30, 1784」收尾，
        # 沒有句點但那就是原文的樣子。以四位數年份收尾的一律放過。
        if re.search(r"\b(1[5-9]|20)\d{2}\s*$", last):
            last = ""
        if last and not last.endswith(END_OK) and len(last) > 18:
            bad.append(f"L 篇尾斷在句子中間 {norm(title)[:34]}（p{end}）：…{last[-46:]}")

    # M 隔壁文章竄進來。
    # 🚨 不能只數「有幾個整行大寫」。Alles 那篇自己就有 THE EMERGENCE OF THE ACADEMIC
    #    STUDY OF RELIGION、DEVELOPMENT OF… 兩個大寫小標，數量判法會把正常的小標
    #    報成竄入（2026-09-12 誤報過）。竄進來的長相是**百科全書的條目名**：整行
    #    大寫又帶冒號，而且跟本篇篇名對不上。
    for i, (title, page) in enumerate(pieces):
        end = pieces[i + 1][1] - 1 if i + 1 < len(pieces) else doc.page_count
        own = re.sub(r"[^a-z]", "", norm(title).lower())
        shout = set()
        for j in range(page - 1, min(end, doc.page_count)):
            for l in [norm(x) for x in doc[j].get_text().split("\n")[2:]]:
                letters = [c for c in l if c.isalpha()]
                # SECTION／PART／CHAPTER 開頭的是書裡自己的分節標題（Segal 那篇
                # 就有「SECTION ONE: MYTH」「SECTION TWO: MYTH AND RITUAL」），
                # 不是竄進來的隔壁條目（2026-09-12 誤報過）。
                if (len(l) > 24 and ":" in l and letters
                        and not re.match(r"(SECTION|PART|CHAPTER|BOOK)\b", l)
                        and sum(c.isupper() for c in letters) / len(letters) > 0.85
                        and re.sub(r"[^a-z]", "", l.lower()) not in own):
                    shout.add(l[:56])
        if shout:
            bad.append(f"M 疑似竄進別篇 {norm(title)[:30]}：{sorted(shout)[:2]}")

    # N 出處要印完整書目，不是「EoR 8761-8767」這種檔名縮寫。
    # 只查英文那三本：日文讀本的出處走青空文庫圖書卡體例（「角川新書、角川書店、
    # 1952（昭和 27）年…／青空文庫　圖書卡 60192」），本來就完整，別誤報。
    for i, (title, page) in enumerate(pieces):
        head = norm(doc[page - 1].get_text() + " " + doc[min(page, doc.page_count - 1)].get_text())
        if re.search(r"[぀-ヿ一-鿿]", norm(title)):
            continue
        if "閱讀導引" in head[:60] and not re.search(r"\(\w[^)]*\d{4}\)", head):
            bad.append(f"N 出處沒有完整書目 {norm(title)[:34]}")

    # J 頁腳
    dupes = [i + 1 for i in range(front, doc.page_count)
             if len(re.findall(r"\d{1,4}", doc[i].get_text(
                 "text", clip=fitz.Rect(0, doc[i].rect.height - 60,
                                        doc[i].rect.width, doc[i].rect.height)))) > 1]
    if dupes:
        bad.append(f"J 頁腳重號 {len(dupes)} 頁：{dupes[:5]}")

    # K 首行縮排
    xs = [round(b[0]) for i in range(front, min(front + 80, doc.page_count))
          for b in doc[i].get_text("blocks") if b[4].strip()]
    if not any(abs(x - INDENT_X) <= 2 for x in xs):
        bad.append("K 找不到首行縮排")

    for b in bad:
        print("  ★", b)
    print("  →", "通過" if not bad else f"{len(bad)} 項要看")
    doc.close()
    return len(bad)


def check_copies(path: Path) -> int:
    """O 同一本書的各個位置要一致。

    🚨 讀本有三份：跟課的那份在課程資料夾、送印那疊在雲端硬碟根目錄的
    「115-1 課程讀本」、歸檔那份在知識圖工作室的「教學／115-1_修課讀本」。
    2026-09-12 我只更新課程資料夾，使用者翻的是送印那疊的舊檔，於是把**已經修好
    的錯又報了一次**——而各處檔名一模一樣，從檔名完全看不出哪份是新的。
    所以逐份比雜湊，缺了或不一致就報。
    """
    bad = 0
    for d in SHARED:
        other = d / path.name
        if not other.exists():
            print(f"  ★ O {d.name} 缺 {path.name}")
            bad += 1
            continue
        h1 = hashlib.sha1(path.read_bytes()).hexdigest()[:12]
        h2 = hashlib.sha1(other.read_bytes()).hexdigest()[:12]
        if h1 != h2:
            print(f"  ★ O {d.name} 不同步 {path.name}："
                  f"課程夾 {h1}（{path.stat().st_size // 1024} KB）／"
                  f"該處 {h2}（{other.stat().st_size // 1024} KB）")
            bad += 1
    return bad


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", help="只查這一本（檔名）")
    a = ap.parse_args()
    total = 0
    for name, folder in BOOKS.items():
        if a.book and a.book != name:
            continue
        path = folder / name
        if not path.exists():
            print(f"★ 找不到 {path}")
            total += 1
            continue
        total += check(path)
        total += check_copies(path)
    print("\n總結：", "全數通過" if total == 0 else f"{total} 項要看")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
