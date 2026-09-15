#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""收臺大佛學數位圖書館（DLMBS）的書目資料庫。

約 51 萬筆佛學書目，欄位比華藝厚得多——除了做註腳必備的**卷期、起訖頁、正式作者
署名**之外，還有**摘要、目次、關鍵詞、研究時代、研究地點**。目次那一欄等於幾十萬
筆專書與論文的章節層索引，是這個庫最獨特的地方。

## 站與條款

  主機    `https://dlbs.liberal.ntu.edu.tw`
  🚨 舊網址 `buddhism.lib.ntu.edu.tw` 與 `ccbs.ntu.edu.tw` **都回 308 但不給
     Location**，curl 跟著跳會拿到 0 bytes。只能直接打 dlbs 那個。
  Cookie  `accept_copyright=yes; DLMBS_language=tw`（站上有一道著作權同意頁）
  條款    「在限於個人及非商業目的的情況下…可自由瀏覽及使用本網站」，
          並要求「如您引用本站資料作為您論文或研究的來源，請加註本站為
          您的參考資料來源」。本站為私人研究自用，符合；引用出處寫進索引。
  robots  沒有 robots.txt。節流 2 秒是自己給的規矩。

## 怎麼取

站方自己有批次匯出：`POST /exportbooks2016`，帶 `seqs`（逗號分隔的書目號）。
一次 300 個號沒問題，回傳是可直接解析的純文字，**比逐筆抓明細頁輕 20 倍**
（明細頁一筆 74 KB，匯出一筆約 1 KB）。

🚨 **兩種格式的欄位是互補的，必須都抓再合併：**

  `exportformat=txt`      有 資料類型／目次／附註項／研究時代／研究地點，
                          但**沒有書目號**——只有批次內的流水號。送 300 個號回
                          291 筆時，無從得知少的是哪 9 個，紀錄就沒有穩定 ID。
  `exportformat=endnote`  `%U` 欄帶 `…search_detail.jsp?seq=343626`，**書目號在裡面**，
                          但沒有資料類型與目次。

（另試過 ris／csv／xml／bibtex／html 全部回 0 bytes，`exporttype` 換值也沒用。）

🚨 **合併靠位置，而位置必須每批驗過。** 兩種格式回傳的順序一致，但
**那個順序不是送出去的 seq 順序**（實測送 343600–343699，endnote 回來的頭五個是
343690, 343644, 343610, 343680, 343601）。所以不能拿 seq 去對，只能靠位置；
而靠位置就必須每一批都比對題名，不符就整批丟掉重抓——否則做出來的是
「欄位齊全但張冠李戴」的資料，從結果完全看不出來。

## 存放

  紀錄  Drive `_corpus/ntu-dlmbs/records.jsonl`（一行一筆，不進 git）
  狀態  Drive `_corpus/ntu-dlmbs/state.json`（已完成的批次，可中斷續跑）
  索引  `public/content/research-data/buddhist-studies/dlmbs.json`（進版控）

## 用法

  python scripts/ntu_dlmbs_harvest.py --probe            # 探範圍與密度
  python scripts/ntu_dlmbs_harvest.py --harvest --limit 3  # 先跑三批看看
  python scripts/ntu_dlmbs_harvest.py --harvest          # 全量（可中斷續跑）
  python scripts/ntu_dlmbs_harvest.py --index            # 產網站索引
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DRIVE = Path("G:/我的雲端硬碟/資料/知識圖工作室/_corpus/ntu-dlmbs")
OUT = DRIVE / "records.jsonl"
STATE = DRIVE / "state.json"
INDEX = ROOT / "public" / "content" / "research-data" / "buddhist-studies" / "dlmbs.json"

HOST = "https://dlbs.liberal.ntu.edu.tw"
ENDPOINT = HOST + "/exportbooks2016"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (kglab-research; academic bibliography; non-commercial)",
    "Cookie": "accept_copyright=yes; DLMBS_language=tw",
    "Referer": HOST + "/search/export.jsp",
    "Content-Type": "application/x-www-form-urlencoded",
}

BATCH = 300           # 實測可行；再大沒測過，別隨手調
DELAY = 2.0           # 對站方的承諾，不是可調參數
SEQ_FROM, SEQ_TO = 1, 780_000   # 實測紀錄落在 ~128,125–712,500，兩頭各留餘裕

# endnote 欄位碼 → 我們的欄位名
ENW = {
    "A": "authors", "T": "title", "D": "date", "J": "source", "V": "volume",
    "N": "issue", "P": "pages", "I": "publisher", "C": "place", "@": "issn",
    "G": "lang", "K": "keywords", "X": "abstract", "U": "url", "B": "book",
    "S": "series", "9": "degree", "E": "editor",
}
# 純文字匯出的欄位標籤。站方用全形空格把標籤排成等寬（「題　　名」「出 版 者」），
# 所以比對前先把所有空白去掉。
#
# 🚨 **不要用正則去猜標籤。**第一版寫成
#     ^([^\s：]{1,6}(?:　*[^\s：]{0,6})*)：(.*)$
# 那是一個可匹配空字串的巢狀量詞，碰到目次那種沒有冒號的長行就**災難性回溯**，
# 整支程式卡死在第一批而且不報錯——看起來像網路慢或站方擋人，實際上是自己的正則。
# 而且就算不爆炸也會誤判：目次的內容行「一. 前言：概述」會被當成標籤「一.前言」。
# 現在改成「找第一個冒號 → 前綴去空白 → 比對已知標籤集」，線性且不會誤判。
TXT_LABELS = {
    "題名", "作者", "出處題名", "卷期", "頁次", "日期", "出版者", "出版地",
    "資料類型", "使用語文", "附註項", "ISBN/ISSN/ISRC", "關鍵字", "摘要",
    "目次", "研究時代", "研究地點", "叢書名", "版本項", "稽核項", "學位類別",
    "校院名稱", "系所名稱", "指導教授", "畢業年度", "點閱次數", "建檔日期",
    "更新日期", "出版者網址", "備註", "叢書號", "冊次", "集叢號", "版本",
}
# 長得像標籤但不在上表裡的，計次記下來，跑完印出現「出現很多次」的那些——
# 那才可能是真的新欄位。只出現一兩次的幾乎都是目次的內容行。
UNKNOWN_LABELS: dict[str, int] = {}


def txt_label(line: str) -> tuple[str, str] | None:
    """一行是不是「標籤：值」。

    回 `(label, value)`＝認得的欄位；回 `None`＝當成續行。

    🚨 `叢書號` 一開始不在清單裡，於是「叢 書 號：0」整行被當成題名的續行
    吞進去，題名變成「測試書目(請勿刪除)\n叢 書 號：0」，害合併閘擋掉整批。
    補進白名單就解決了。

    ⚠️ **但不可以因此改成「認不得就中止續接」**——實測那樣會把目次從第一個
    含冒號的條目（「第一章：空」「練習一：…」）處整個截斷，換來更大的資料損失，
    而且目次少一半在頁面上完全看不出來。認不得一律當續行，只把它計次記下來，
    跑完看哪些出現得夠頻繁——那才可能是真的新欄位。
    """
    i = line.find("：")
    if i <= 0 or i > 20:
        return None
    label = re.sub(r"\s", "", line[:i])
    if not label:
        return None
    if label not in TXT_LABELS:
        UNKNOWN_LABELS[label] = UNKNOWN_LABELS.get(label, 0) + 1
        return None
    return label, line[i + 1:].strip()


def die(msg: str) -> None:
    print(f"✗ {msg}")
    raise SystemExit(1)


def post(seqs: list[int], fmt: str, tries: int = 4) -> str:
    body = urllib.parse.urlencode({
        "seqs": ",".join(map(str, seqs)),
        "exporttype": "bibliography",
        "exportformat": fmt,
        "language": "tw",
        "bibliographyexportmode": "1",
    }).encode()
    for attempt in range(tries):
        try:
            req = urllib.request.Request(ENDPOINT, data=body, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=300) as r:
                return r.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < tries - 1:
                time.sleep(10 * (attempt + 1))
                continue
            raise
        except Exception:
            if attempt < tries - 1:
                time.sleep(6 * (attempt + 1))
                continue
            raise
    return ""


# ── 解析 ────────────────────────────────────────────────────────────────
def parse_enw(t: str) -> list[dict]:
    """EndNote .enw → 逐筆。⚠️ %X（摘要）是多行的，不以 % 開頭的行要續接。"""
    recs, cur, last = [], {}, None
    for line in t.splitlines():
        m = re.match(r"^%(\S) ?(.*)$", line)
        if m:
            code, val = m.group(1), m.group(2).strip()
            if code == "A" and "authors" in cur and last == "A":
                cur["authors"] += "; " + val        # 多位作者各佔一行
            elif code in ENW:
                key = ENW[code]
                cur[key] = (cur.get(key) + "; " + val) if key in cur else val
            last = code
            # %W（資料庫名）固定是最後一欄，用它切紀錄
            if code == "W" and cur:
                recs.append(cur)
                cur, last = {}, None
        elif line.strip() and last and last in ENW:
            cur[ENW[last]] = cur.get(ENW[last], "") + "\n" + line.strip()
    if cur:
        recs.append(cur)
    return recs


def parse_txt(t: str) -> list[dict]:
    """站方的純文字匯出 → 逐筆。紀錄以「只有數字的一行」分隔。"""
    recs, cur, last = [], None, None
    seen = 0          # 已經看過幾個分隔號（＝目前正在讀第幾筆）
    for line in t.splitlines():
        # 🚨 紀錄分隔是「批次內的流水號」，但不能只判「整行都是數字」——
        #    目次或摘要裡出現單獨一行的數字（年份、頁碼）就會被誤判成分隔，
        #    多切出一筆空紀錄。實測 seq 270,001– 那批就是這樣：原始只有 254 個
        #    「題名：」，卻被切成 255 筆，害合併閘擋掉整批（27 批全是這個原因）。
        #    流水號嚴格遞增 1,2,3…，所以只在「剛好等於下一號」時才算分隔。
        #    ⚠️ 要用獨立計數器，不能用 len(recs)——看到「2」時第 1 筆還在 cur 裡
        #    沒進 recs，len(recs)+1 會算成 1 而永遠對不上。
        s = line.strip()
        if s.isdigit() and int(s) == seen + 1:
            seen += 1
            if cur:
                recs.append(cur)
            cur, last = {}, None
            continue
        if cur is None:
            continue
        kv = txt_label(line)
        if kv:
            label, val = kv
            cur[label] = val
            last = label
        elif line.strip() and last:
            cur[last] = (cur[last] + "\n" + line.strip()).strip()
    if cur:
        recs.append(cur)
    return recs


def norm(s: str) -> str:
    return re.sub(r"\s+", "", (s or "")).strip()


def merge(enw: list[dict], txt: list[dict]) -> tuple[list[dict], str]:
    """靠位置合併，並以題名逐筆驗證。不符就回錯誤訊息，由呼叫端整批丟掉。"""
    if len(enw) != len(txt):
        return [], f"筆數不同 endnote {len(enw)} / txt {len(txt)}"
    bad = 0
    out = []
    for e, x in zip(enw, txt):
        if norm(e.get("title")) != norm(x.get("題名")):
            bad += 1
            continue
        seq = None
        m = re.search(r"seq=(\d+)", e.get("url", ""))
        if m:
            seq = int(m.group(1))
        row = {"seq": seq}
        for k, v in e.items():
            if k not in ("url",) and v:
                row[k] = v
        for label, key in (("資料類型", "doctype"), ("目次", "toc"), ("附註項", "note"),
                           ("研究時代", "era"), ("研究地點", "region")):
            if x.get(label):
                row[key] = x[label]
        if seq:
            row["source_url"] = (
                f"https://dlbs.liberal.ntu.edu.tw/search/search_detail.jsp?seq={seq}")
        out.append(row)
    if bad:
        return [], f"題名對不上 {bad}/{len(enw)} 筆"
    return out, ""


# ── 主流程 ──────────────────────────────────────────────────────────────
def load_state() -> dict:
    if STATE.exists():
        try:
            return json.loads(STATE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {"done": [], "records": 0, "failed": []}


def save_state(st: dict) -> None:
    tmp = STATE.with_suffix(".json.part")
    tmp.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(STATE)


def harvest(limit: int | None, start_at: int | None) -> None:
    DRIVE.mkdir(parents=True, exist_ok=True)
    st = load_state()
    done = set(st["done"])
    batches = list(range(start_at or SEQ_FROM, SEQ_TO, BATCH))
    todo = [b for b in batches if b not in done]
    if limit:
        todo = todo[:limit]
    print(f"全部 {len(batches):,} 批，已完成 {len(done):,} 批，這次要跑 {len(todo):,} 批")
    print(f"每批 {BATCH} 個號 × 2 種格式，節流 {DELAY} 秒 → 約 "
          f"{len(todo)*2*DELAY/3600:.1f} 小時")

    got = 0
    empty = 0
    for i, b in enumerate(todo, 1):
        seqs = list(range(b, min(b + BATCH, SEQ_TO)))
        try:
            enw_raw = post(seqs, "endnote")
            time.sleep(DELAY)
            enw = parse_enw(enw_raw)
            if not enw:
                empty += 1
                done.add(b)
                st["done"] = sorted(done)
                if i % 20 == 0 or i == len(todo):
                    save_state(st)
                    print(f"  [{i}/{len(todo)}] seq {b:,}– 空批（累計空 {empty}）")
                continue
            txt_raw = post(seqs, "txt")
            time.sleep(DELAY)
            rows, err = merge(enw, parse_txt(txt_raw))
        except Exception as e:
            print(f"  [{i}/{len(todo)}] seq {b:,}– 失敗 {type(e).__name__}，留待重跑")
            st.setdefault("failed", []).append(b)
            save_state(st)
            time.sleep(DELAY * 3)
            continue
        if err:
            # 🚨 寧可整批丟掉重抓，也不要寫進「欄位齊全但張冠李戴」的資料
            print(f"  [{i}/{len(todo)}] seq {b:,}– ⚠️ 合併閘擋下：{err}，整批不寫")
            st.setdefault("failed", []).append(b)
            save_state(st)
            continue
        with OUT.open("a", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        got += len(rows)
        done.add(b)
        st["done"] = sorted(done)
        st["records"] = st.get("records", 0) + len(rows)
        if i % 10 == 0 or i == len(todo):
            save_state(st)
            print(f"  [{i}/{len(todo)}] seq {b:,}–{b+BATCH-1:,}  本批 {len(rows)} 筆"
                  f"（本次累計 {got:,}／總計 {st['records']:,}）")
    save_state(st)
    print(f"\n本次新增 {got:,} 筆；空批 {empty}；待重跑 {len(st.get('failed', []))} 批")
    hot = sorted((v, k) for k, v in UNKNOWN_LABELS.items() if v >= 20)
    if hot:
        print(f"⚠️ 有 {len(hot)} 個沒見過、但出現 20 次以上的「標籤：」前綴，"
              f"可能是真的新欄位（目前當續行處理）：")
        for v, k in sorted(hot, reverse=True)[:15]:
            print(f"     {k}  ×{v}")
        print("   確認是欄位就補進 TXT_LABELS 再重跑相關批次")
    elif UNKNOWN_LABELS:
        print(f"（{len(UNKNOWN_LABELS)} 個一次性的「X：」前綴，都是目次內容行，已當續行）")


def probe() -> None:
    print("密度抽樣（每 50,000 取 60 個號）：")
    for at in range(100_000, 760_001, 50_000):
        try:
            n = len(parse_enw(post(list(range(at, at + 60)), "endnote")))
        except Exception as e:
            n = -1
            print(f"  {at:>8,} 失敗 {type(e).__name__}")
            continue
        print(f"  {at:>8,} → {n:>3}/60  ({n/60:.0%})")
        time.sleep(DELAY)


def build_index() -> None:
    if not OUT.exists():
        die("還沒有 records.jsonl，先跑 --harvest")
    n = dup = noseq = 0
    doctypes: dict[str, int] = {}
    years: dict[str, int] = {}
    with_toc = with_abs = 0
    sources: dict[str, int] = {}
    # ⚠️ records.jsonl 是逐批 append 的，同一個 seq 可能被寫兩次：
    # 試跑時用過 --start，那些批次不在對齊後的批次格線上，全量重跑會再撈一次。
    # 所以索引一律以 seq 去重，並把重複數印出來（靜默去重 = 看不出抓壞了沒有）。
    seen: set[int] = set()
    for line in OUT.open(encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        s = r.get("seq")
        if s is None:
            noseq += 1
            continue
        if s in seen:
            dup += 1
            continue
        seen.add(s)
        n += 1
        d = (r.get("doctype") or "未標").split("=")[0]
        doctypes[d] = doctypes.get(d, 0) + 1
        y = (r.get("date") or "")[:4]
        if y.isdigit():
            years[y] = years.get(y, 0) + 1
        if r.get("toc"):
            with_toc += 1
        if r.get("abstract"):
            with_abs += 1
        s = (r.get("source") or "").split("=")[0]
        if s:
            sources[s] = sources.get(s, 0) + 1
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    INDEX.write_text(json.dumps({
        "source": "臺大佛學數位圖書館 DLMBS（https://dlbs.liberal.ntu.edu.tw）",
        "cite": "引用本站資料請加註臺大佛學數位圖書館為來源，依其版權聲明要求。",
        "records": n,
        "with_toc": with_toc,
        "with_abstract": with_abs,
        "doctypes": dict(sorted(doctypes.items(), key=lambda x: -x[1])),
        "top_sources": dict(sorted(sources.items(), key=lambda x: -x[1])[:60]),
        "years": dict(sorted(years.items())),
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{n:,} 筆（去重後）→ {INDEX}")
    if dup:
        print(f"  ⚠️ 重複的 seq {dup:,} 筆已去除（試跑批次與全量格線不對齊所致）")
    if noseq:
        print(f"  ⚠️ 沒有 seq 的 {noseq:,} 筆已略過——這不該發生，要查 merge 那一段")
    print(f"  有目次 {with_toc:,}（{with_toc/max(n,1):.0%}）／"
          f"有摘要 {with_abs:,}（{with_abs/max(n,1):.0%}）")
    for d, c in sorted(doctypes.items(), key=lambda x: -x[1])[:8]:
        print(f"    {d:<16s} {c:>8,}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--harvest", action="store_true")
    ap.add_argument("--index", action="store_true")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--start", type=int)
    a = ap.parse_args()
    if not any((a.probe, a.harvest, a.index)):
        ap.print_help()
        return 0
    if not DRIVE.parent.parent.exists():
        die("G: 沒掛載——先修 Drive（見 CLAUDE.md），別寫進一個不存在的路徑")
    if a.probe:
        probe()
    if a.harvest:
        harvest(a.limit, a.start)
    if a.index:
        build_index()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
