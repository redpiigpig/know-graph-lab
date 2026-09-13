#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓《佛光大辭典》。使用者 2026-09-11 表示已取得佛光山授權。

🟢 **2026-09-13：這支大概不必再跑了——使用者拿到資料檔了。**

下載區的《佛光大辭典增訂版【阿彌陀佛】20230501》是三個分卷（`.zip.001/.002/.003`，
合計 54 MB）。那不是多卷 zip 而是**單一 ZIP 被逐位元組切三段**（`.001` 開頭就是
`PK\\x03\\x04`），`cat` 接起來即可解開。裡面是一套 **MDict 詞典**：

    .mdx  11.7 MB  釋義本體（MDict 2.0／UTF-8／Format=Html）
    .mdd  42.3 MB  資源
    .png  15 KB    圖示

MDX 標頭有 `Encrypted="2"`、`RegisterBy="EMail"`，但那是 MDict 標準的 record block
加擾（固定鹽值），**不是使用者綁定的 DRM**，`mdict_utils` 直接讀得出來。

實測數字（`--check` 等價的體檢見交接紀錄）：

    詞條          32,134 條，**零跳轉別名、零空白、最短 10 字**
    釋義          漢字 6,188,877；含標點數字 8,230,907 字元
    長度          中位數 141 字，最長 9,990 字
    原書頁碼      30,349 條（94.4%）結尾帶 `p8071` 這種頁碼——做註腳直接可用
    內嵌圖        4,066 個 <img>，分布在 2,766 條裡
    重複詞目      1 個（「於教二諦」）

🚨 **條數與 B2 交接文件寫的「約 22,600 條、360 餘萬字」對不上，但不是抓錯。**
那組數字是 1988 年**八冊初版**的；這個檔是**十冊增訂版**，它自己的說明頁寫
「總條目達三萬餘條，近三千幀圖表，近千萬言」——32,134 條／3,264 張圖／823 萬字元
三項都對得上。對帳前先確認自己比的是哪一版。

5.6% 沒有結尾頁碼的那批**不是缺陷**：它們是參見條（詞目以 `→` 結尾，共 1,751 條），
頁碼寫在內文的「（參閱「大乘同性經」1087）」裡，要另外用這個樣式抽。

⚠️ **這個檔的來歷要知道**：`.mdd` 裡除了 3,264 張 jpg，還有 `fgsdict.s3db`
（50.6 MB SQLite）、33 個 `fgsdict_bookN.xml`、以及 iOS 的
`archived-expanded-entitlements.xcent`——也就是說，這套 MDict 是有人把**佛光山官方
app 拆包**做出來的，不是佛光山交付的授權資料檔。使用者既已表示取得授權，是否用它、
以及要不要改向佛光山索取正式資料檔，由使用者決定；但入庫前這件事要記在 license 欄裡。

（下面是官網抓取那條路的紀錄，保留備查。）

🚨 **這個站沒有詞目索引頁**。`fgs_drlist/fgs_drindex/...` 全部 302，目錄列表 403，
新平台（etext.fgs.org.tw）也只有搜尋框。所以不能「照目錄抓」，只能用查詢去枚舉。

而「用查詢枚舉」最容易寫成一個**看起來成功的失敗**：隨便挑一批關鍵字去撈，撈回幾萬條
就宣告完成——漏掉的那些完全不會現形。這支改用**字集閉包**，讓完整性可以自我驗證：

  1. 觀察到的事實：搜尋是對**詞目**做子字串比對（查「般若」會回「二般若」「八千頌般若」
     「仁王護國般若波羅蜜經」），而每個詞目至少含一個漢字。
  2. 所以只要把「詞目用到的字」全查一遍，就必然涵蓋全部詞目。
  3. 種子不必用猜的：本站已有的十萬餘條佛學詞目（法鼓那批，見 dila_glossaries_fetch.py）
     抽出字集當起點；每抓回一批新詞目，再把其中的新字加進待查佇列。
  4. **跑到沒有新字、也沒有新詞目為止**——那就是不動點，可以宣告完整。

分頁：ASP.NET GridView，`__EVENTTARGET=ctl00$ContentPlaceHolder3$GridView2`、
`__EVENTARGUMENT=Page$N`，一頁 20 條，內文（名相／釋文）直接嵌在頁面上。

⚠️ 節流 1.5 秒是對佛光山伺服器的承諾，不是可調參數。整輪估計數千次請求。

存放：Drive `知識圖工作室/_corpus/fgs-dictionary/entries.jsonl`
狀態：同目錄 `state.json`（已查過的字、已收詞目）——**可中斷續跑**

用法：
  python scripts/fgs_dictionary_fetch.py --pilot 8   # 先查八個字驗證
  python scripts/fgs_dictionary_fetch.py             # 全量（可重跑，會續傳）
  python scripts/fgs_dictionary_fetch.py --status    # 看進度
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import http.cookiejar
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
CORPUS = Path("G:/我的雲端硬碟/資料/知識圖工作室/_corpus")
OUT = CORPUS / "fgs-dictionary"
SEED_DIR = CORPUS / "dila-glossaries"

URL = "https://www.fgs.org.tw/fgs_book/fgs_drser.aspx"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
      "Accept-Language": "zh-TW,zh;q=0.9"}
DELAY = 1.5          # 對佛光山伺服器的承諾，別調小
GRID = "ctl00$ContentPlaceHolder3$GridView2"
CJK = re.compile(r"[\u4e00-\u9fff]")
HIDDEN = ("__VIEWSTATE", "__VIEWSTATEGENERATOR", "__EVENTVALIDATION")
# 一筆結果：名相 …… 釋文 ……（兩者都在表格列裡，標籤會夾雜高亮 span）
ROW = re.compile(r"名相[：:](.*?)釋文[：:](.*?)(?=名相[：:]|$)", re.S)
TAG = re.compile(r"<[^>]+>")


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(TAG.sub("", s))).strip()


class Session:
    def __init__(self) -> None:
        cj = http.cookiejar.CookieJar()
        self.op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    def get(self, url: str) -> str:
        return self.op.open(urllib.request.Request(url, headers=UA),
                            timeout=90).read().decode("utf-8", "replace")

    def post(self, url: str, data: dict) -> str:
        """POST，失敗就退避重試。

        ⚠️ 這個站禁不起連續猛打：一個「羅」字要翻三十九頁，跑完之後接連三個字都
        URLError。不是被永久擋，是短時間請求太密——退避幾秒就恢復。沒有重試的話，
        那三個字會被記成「查過了」而其實一條都沒拿到，最後總數少掉幾百條也看不出來。
        """
        body = urllib.parse.urlencode(data).encode()
        last: Exception | None = None
        for attempt in range(4):
            try:
                req = urllib.request.Request(url, data=body, headers={
                    **UA, "Referer": url,
                    "Content-Type": "application/x-www-form-urlencoded"})
                return self.op.open(req, timeout=90).read().decode("utf-8", "replace")
            except Exception as e:
                last = e
                time.sleep(4 * (attempt + 1))
        raise last if last else RuntimeError("post failed")


def hidden(page: str) -> dict:
    out = {}
    for n in HIDDEN:
        m = re.search(r'id="' + n + r'"[^>]*value="([^"]*)"', page)
        out[n] = html.unescape(m.group(1)) if m else ""
    return out


def parse_rows(page: str) -> list[dict]:
    # 結果區在頁尾，名相/釋文 成對出現；把導覽列那些雜訊排除靠「名相：」這個錨
    body = page[page.find("名相"):] if "名相" in page else ""
    rows = []
    for m in ROW.finditer(body):
        term, defi = clean(m.group(1)), clean(m.group(2))
        if not term or len(term) > 40:
            continue
        rows.append({"term": term, "definition": defi})
    return rows


TEXTBOX = "ctl00$ContentPlaceHolder2$TextBox2"


def search(s: Session, word: str, max_pages: int = 200) -> list[dict]:
    page = s.get(URL)
    d = hidden(page)
    d.update({"__EVENTTARGET": "", "__EVENTARGUMENT": "",
              TEXTBOX: word,
              "ctl00$ContentPlaceHolder2$Button2": "查詢"})
    page = s.post(URL, d)
    rows = parse_rows(page)
    seen_pages = 1
    while seen_pages < max_pages:
        # ⚠️ 分頁把頁碼放在 __EVENTARGUMENT，不是換 target。找不到下一頁就停——
        # GridView 只顯示一個頁碼視窗，不能靠「頁碼連結還在不在」判斷結束。
        nxt = f"Page${seen_pages + 1}"
        if f"'{GRID}','{nxt}'" not in page.replace("&#39;", "'"):
            break
        d = hidden(page)
        # 🚨 翻頁一定要把查詢字一起送回去。少了它伺服器會拿空字串重查、回 0 條，
        # 而第一頁明明有 20 條——於是每個字都剛好收到 20 條，看起來像
        # 「這個字只有 20 個詞目」，完全不像壞掉。試跑六個字全是 20 才露餡。
        d.update({"__EVENTTARGET": GRID, "__EVENTARGUMENT": nxt, TEXTBOX: word})
        time.sleep(DELAY)
        page = s.post(URL, d)
        got = parse_rows(page)
        if not got:
            break
        rows += got
        seen_pages += 1
    return rows


def seed_chars() -> list[str]:
    """從法鼓那十萬條詞目抽字集當種子。"""
    chars: dict[str, int] = {}
    for f in sorted(SEED_DIR.glob("*.jsonl")):
        for line in f.open(encoding="utf-8"):
            try:
                t = json.loads(line).get("term") or ""
            except Exception:
                continue
            for ch in CJK.findall(t):
                chars[ch] = chars.get(ch, 0) + 1
    # 常用的先查：早一點把高產的字掃完，新字才會盡早進佇列
    return [c for c, _ in sorted(chars.items(), key=lambda kv: -kv[1])]


def load_state() -> dict:
    f = OUT / "state.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    return {"done_chars": [], "queue": [], "terms": []}


def save(state: dict, entries: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    nl = chr(10)
    (OUT / "state.json").write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
    (OUT / "entries.jsonl").write_text(
        nl.join(json.dumps(v, ensure_ascii=False) for v in entries.values()) + nl,
        encoding="utf-8")


def load_entries() -> dict:
    f = OUT / "entries.jsonl"
    if not f.exists():
        return {}
    out = {}
    for line in f.open(encoding="utf-8"):
        try:
            r = json.loads(line)
            out[r["term"]] = r
        except Exception:
            continue
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", type=int, help="只查前 N 個字，驗證用")
    ap.add_argument("--status", action="store_true")
    args = ap.parse_args()

    state = load_state()
    entries = load_entries()

    if args.status:
        print(f"已查字 {len(state['done_chars'])}／待查 {len(state['queue'])}"
              f"／已收詞目 {len(entries):,}")
        return 0

    if not state["queue"] and not state["done_chars"]:
        state["queue"] = seed_chars()
        print(f"種子字集 {len(state['queue'])} 字（取自法鼓十萬條詞目）")

    done = set(state["done_chars"])
    queue = [c for c in state["queue"] if c not in done]
    limit = args.pilot or len(queue)
    s = Session()
    new_chars = 0

    for i, ch in enumerate(queue[:limit], 1):
        try:
            rows = search(s, ch)
        except Exception as e:
            print(f"[{i}/{limit}] 「{ch}」失敗 {type(e).__name__}，稍後重試")
            time.sleep(5)
            continue
        added = 0
        for r in rows:
            if r["term"] not in entries:
                entries[r["term"]] = r
                added += 1
                # 新詞目帶來的新字回頭進佇列——閉包就是靠這一步
                for c in CJK.findall(r["term"]):
                    if c not in done and c not in queue:
                        queue.append(c)
                        new_chars += 1
        done.add(ch)
        # ⚠️ 一定要 flush：重導向到檔案時 python 會緩衝到行程結束，
        # 長跑中 log 會一直是空的，看不出是在跑還是卡住（ocr_overnight 記過同一個坑）。
        print(f"[{i}/{limit}] 「{ch}」 命中 {len(rows):>4}　新增 {added:>4}　"
              f"累計 {len(entries):,}", flush=True)
        # 存檔要密：常用字（法、三、大…）一個字就要翻上百頁、耗好幾分鐘，
        # 而這台筆電會通勤休眠，二十個字才存一次可能整段白跑。
        if i % 5 == 0:
            state["done_chars"] = sorted(done)
            state["queue"] = queue
            save(state, entries)
        time.sleep(DELAY * 2)   # 翻頁多的字打得兇，字與字之間多喘一口

    state["done_chars"] = sorted(done)
    state["queue"] = queue
    save(state, entries)
    left = len([c for c in queue if c not in done])
    print(f"{chr(10)}已查 {len(done)} 字／待查 {left} 字（其中本輪新發現 {new_chars} 字）")
    print(f"詞目 {len(entries):,} 條 → {OUT / 'entries.jsonl'}")
    if left == 0:
        print("✅ 字集已閉包：沒有新字也沒有新詞目，可視為收錄完整")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
