# -*- coding: utf-8 -*-
"""把國家檔案「可線上閱覽」的影像下載到 Drive。

只抓 access 標示「可線上閱覽」的那批——標「須提出申請」者要走檔案局的申請書流程，
不繞過（見 archives_gov.py）。

授權（檔案局〈本網站之電子影音檔案使用說明〉，2026-05-13）：
  一、公文（法律、命令、公務員撰擬之講稿新聞稿及其他公文）依著作權法第 9 條
      **不得為著作權標的**——情治單位的簽呈、函文、偵訊筆錄、專案報告都屬此類。
  二、可自由利用，但須①標示來源「國家發展委員會檔案管理局，國家檔案資訊網
      (https://aa.archives.gov.tw/)」②非商業性。學術論文引用符合。
  三、檔案中夾附的受著作權保護物（如《方向雙月刊》這類刊物本身）另需授權。
  🚨 五、「請注意有無侵害公共利益、第三人隱私或正當權益…應自負一切法律責任」。
      政治檔案含大量第三人姓名（被監控者、線民、承辦人、信徒名冊），
      **所以影像只落地 Drive 供研究，不上 R2 也不上網站**；站上只放書目與摘要。

取得路徑（三步，缺一不可）：
  1. 搜尋結果頁的「可線上閱覽」鈕帶 GoToMoreImage('<base64 SystemID>', '<fullpath>')
  2. 開 /ELK/SearchImageDetailed?SystemID=..&fullpath=.. 讀出 .hFullPath 與 .hImgCount
     🚨 hFullPath 是**加密過的**（96 位十六進位），構造不出來，一定要從檢視頁讀
  3. /ELK/LoadImages?encPath=<hFullPath>&page=N&type=9&ck=false
     回傳是 `檔名|data:image/jpeg;base64,...` 的純文字，不是二進位影像

  python -X utf8 scripts/archives_images.py --section yiguandao [--limit N]
"""
import argparse
import base64
import json
import re
import subprocess
import sys
import time
from pathlib import Path

from bs4 import BeautifulSoup

BASE = "https://aa.archives.gov.tw"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"
SRC = Path(r"C:/tmp/archives_gov.json")
DRIVE = Path(r"G:/我的雲端硬碟/資料/知識圖工作室/研究資料/國家檔案調閱/影像")
LEDGER = Path(r"C:/tmp/archives_images_done.json")
DELAY = 1.5

SECTIONS = {
    "yiguandao": ("一貫道", ["一貫道"]),
    "pct": ("台灣基督長老教會", ["長老教會", "台南神學院", "台灣神學院", "玉山神學院", "神學院",
                            "黃彰輝", "宋泉盛", "王憲治", "黃伯和", "高俊明", "鄭仰恩",
                            "董芳苑", "陳主顯", "清寧專案", "一二一O專案", "二二二專案"]),
    "buddhist": ("佛教", ["佛教", "印順", "佛法概論", "太虛", "傳道", "妙心寺", "昭慧"]),
    "methodist": ("衛理公會", ["衛理公會", "周聯華"]),
}


def curl(url, binary=False):
    r = subprocess.run(["curl", "-s", "--max-time", "180", "-A", UA,
                        "-H", "Accept-Language: zh-TW,zh;q=0.9", url],
                       capture_output=True, timeout=200)
    return r.stdout if binary else r.stdout.decode("utf-8", "replace")


def safe(s, n=80):
    """檔名用：去掉 Windows 不接受的字元，並截短。"""
    return re.sub(r'[\\/:*?"<>|]', "_", s).strip()[:n] or "untitled"


def viewer_info(system_id, fullpath):
    """→ (加密後的 encPath, 影像張數)。拿不到就回 (None, 0)。"""
    h = curl(f"{BASE}/ELK/SearchImageDetailed?SystemID={system_id}&fullpath={fullpath}")
    s = BeautifulSoup(h, "html.parser")
    fp = s.select_one(".hFullPath")
    cnt = s.select_one(".hImgCount")
    if not fp or not fp.get("value"):
        return None, 0
    return fp["value"], int((cnt.get("value") if cnt else "0") or 0)


def fetch_page(enc, page):
    """→ (檔名, bytes)。回傳格式是 `檔名|data:image/jpeg;base64,...`。"""
    t = curl(f"{BASE}/ELK/LoadImages?encPath={enc}&page={page}&type=9&ck=false")
    if "|" not in t or "base64," not in t:
        return None, None
    name, data = t.split("|", 1)
    return safe(name.split("=")[-1] or f"{page:04d}.jpg", 60), base64.b64decode(data.split("base64,", 1)[1])


def run(section, limit=0):
    name, keys = SECTIONS[section]
    src = json.loads(SRC.read_text(encoding="utf-8"))
    ledger = json.loads(LEDGER.read_text(encoding="utf-8")) if LEDGER.exists() else {}
    todo = []
    for k in keys:
        for r in src.get(k, {}).get("items", []):
            if r["online"] and r.get("systemId") and r["archiveNo"] not in ledger:
                todo.append(r)
    seen, uniq = set(), []
    for r in todo:                       # 同一件可能在多組裡出現
        if r["archiveNo"] in seen:
            continue
        seen.add(r["archiveNo"])
        uniq.append(r)
    print(f"{name}：待抓 {len(uniq)} 件（已完成 {len(ledger)} 件）", flush=True)

    for i, r in enumerate(uniq, 1):
        if limit and i > limit:
            break
        enc, cnt = viewer_info(r["systemId"], r["fullpath"])
        if not enc:
            print(f"  ! {r['archiveNo']}：檢視頁拿不到 encPath，跳過", flush=True)
            continue
        out = DRIVE / section / f"{safe(r['archiveNo'].replace('/', '_'), 60)}_{safe(r['title'], 40)}"
        out.mkdir(parents=True, exist_ok=True)
        got = 0
        for p in range(1, cnt + 1):
            fn, blob = fetch_page(enc, p)
            if not blob:
                continue
            (out / f"{p:04d}_{fn}").write_bytes(blob)
            got += 1
            time.sleep(DELAY)
        # 一併留下書目，日後看圖才知道這是什麼
        (out / "_書目.txt").write_text(
            "\n".join([f"案由：{r['title']}", f"檔號：{r['archiveNo']}",
                       f"全宗：{r['fonds']}", f"起訖：{r.get('dateRange','')}",
                       f"提供方式：{r['access']}", f"內容摘要：{r.get('summary','')}", "",
                       "來源：國家發展委員會檔案管理局，國家檔案資訊網",
                       "      https://aa.archives.gov.tw/",
                       "利用限制：非商業性；引用須標示上列來源；含第三人姓名，再公開前須自行評估。"]),
            encoding="utf-8")
        ledger[r["archiveNo"]] = {"title": r["title"], "pages": got, "dir": str(out)}
        LEDGER.write_text(json.dumps(ledger, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"  [{i}/{len(uniq)}] {r['title'][:34]} → {got}/{cnt} 張", flush=True)
    print(f"\n完成 {len(ledger)} 件 → {DRIVE / section}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--section", choices=list(SECTIONS), required=True)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    run(a.section, a.limit)


if __name__ == "__main__":
    main()
