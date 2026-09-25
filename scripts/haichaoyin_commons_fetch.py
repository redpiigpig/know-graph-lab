"""《民國佛教期刊文獻集成》整冊 PDF 從 Wikimedia Commons 下載（正編 204 冊＋補編 28 冊＋補編目錄／作者索引）。

- 目標夾：Drive 研究資料\\民國與台灣佛教史\\民國佛教期刊文獻集成\\正編\\ 與 \\補編\\，檔名＝Commons 原檔名（去掉 File:）。
- 共用夾：另有 agent 也往這裡存。下載前檢查同名檔（空白／底線兩種寫法都認）是否已存在且大小一致，有就跳過。
- 寫入先寫 .part、驗大小＋SHA1 後才改名；.part 用 Range 續傳，筆電休眠或中斷後重跑即可接著下。
- Commons 的檔名有三種寫法（2026-09-25 查得 241 個檔）：
    「民國佛教期刊文獻集成 正編 第N卷 …」202 個；「民國佛教期刊文獻集成 第N卷」4 個（57、81 只有這種寫法；50、191 兩種都有）；
    「民國佛教期刊文獻集成·補編 第N卷」28 個，另有「補編 目錄」「補編 作者索引」。補編只有 28 冊在 Commons，其餘 55 冊沒有。
- 用法：
    python scripts/haichaoyin_commons_fetch.py                       # 正編 147–204（舊行為）
    python scripts/haichaoyin_commons_fetch.py --series all          # 全部 232 冊＋2 份索引
    python scripts/haichaoyin_commons_fetch.py --vols 正80 補53 正170  # 指定冊次
    python scripts/haichaoyin_commons_fetch.py --priority-tsv <太虛清單.tsv> --series all   # 清單涉及的冊次先下，其餘接著
    python scripts/haichaoyin_commons_fetch.py --list-only
"""
import argparse, csv, hashlib, json, os, re, sys, time
from collections import deque
from pathlib import Path
import requests

UA = "know-graph-lab research downloader (redpiigpig@gmail.com)"
API = "https://commons.wikimedia.org/w/api.php"
CAT = "Category:民國佛教期刊文獻集成"
ROOT = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\研究資料\民國與台灣佛教史\民國佛教期刊文獻集成")
DEST = {"正編": ROOT / "正編", "補編": ROOT / "補編"}
ALSO_CHECK = [Path(r"G:\我的雲端硬碟\資料\知識圖工作室\研究資料\民國與台灣佛教史\太虛研究\集成影印\_整冊")]
LOG = {"正編": DEST["正編"] / "_下載紀錄_海潮音.json",     # 名字沿用，2026-09-24 起就是這一份
       "補編": DEST["補編"] / "_下載紀錄.json"}
GAP = 5          # 檔與檔之間的間隔秒數
CHUNK = 1 << 20

s = requests.Session()
s.headers["User-Agent"] = UA


def api(params):
    for i in range(5):
        try:
            r = s.post(API, data={**params, "format": "json"}, timeout=60)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"  API 失敗 {e}，{10 * (i + 1)} 秒後重試", flush=True)
            time.sleep(10 * (i + 1))
    raise RuntimeError("Commons API 連續失敗")


def classify(title):
    """Commons 檔名 → (叢刊, 鍵)；鍵是冊號 int，或「目錄」「作者索引」。認不得回 None。"""
    if "補編" in title:
        m = re.search(r"補編 第(\d+)卷", title)
        if m:
            return "補編", int(m.group(1))
        for k in ("目錄", "作者索引"):
            if k in title:
                return "補編", k
        return None
    m = re.search(r"第(\d+)卷", title)
    return ("正編", int(m.group(1))) if m else None


def vol_key(s_):
    """'正80' / '補53' / '80'（＝正編）→ (叢刊, 冊)。"""
    m = re.match(r"(正編?|補編?)?(\d+)$", s_.strip())
    if not m:
        raise argparse.ArgumentTypeError(f"冊次寫法不對：{s_}（要像 正80、補53）")
    return ("補編" if (m.group(1) or "").startswith("補") else "正編"), int(m.group(2))


def list_volumes(series="正編", lo=1, hi=10 ** 6, keys=None):
    titles, p = [], {"action": "query", "list": "categorymembers", "cmtitle": CAT,
                     "cmlimit": "500", "cmtype": "file"}
    while True:
        r = api(p)
        titles += [m["title"] for m in r["query"]["categorymembers"]]
        if "continue" not in r:
            break
        p.update(r["continue"])
    want = {}
    for t in titles:
        c = classify(t)
        if not c:
            continue
        ser, k = c
        if series != "all" and ser != series:
            continue
        if isinstance(k, int) and not (lo <= k <= hi):
            continue
        if keys is not None and (ser, k) not in keys:
            continue
        # 同一冊兩種寫法（50、191）時取有「正編」字樣的那個
        if (ser, k) in want and "正編" not in t:
            continue
        want[(ser, k)] = t
    out = {}
    ks = sorted(want, key=lambda x: (x[0], str(x[1]).zfill(4)))
    for i in range(0, len(ks), 20):
        r = api({"action": "query", "titles": "|".join(want[k] for k in ks[i:i + 20]),
                 "prop": "imageinfo", "iiprop": "url|size|sha1"})
        by_title = {pg["title"]: pg for pg in r["query"]["pages"].values()}
        for k in ks[i:i + 20]:
            pg = by_title.get(want[k]) or next((pg for pg in by_title.values()
                                                if pg["title"].replace("_", " ") == want[k]), None)
            if not pg or "imageinfo" not in pg:
                print(f"  ⚠ Commons 查不到 imageinfo：{want[k]}", flush=True)
                continue
            ii = pg["imageinfo"][0]
            out[k] = {"series": k[0], "vol": k[1], "title": want[k], "name": want[k].split(":", 1)[1],
                      "url": ii["url"], "size": ii["size"], "sha1": ii["sha1"]}
    return out


def existing(v):
    for d in [DEST[v["series"]]] + ALSO_CHECK:
        for n in {v["name"], v["name"].replace(" ", "_")}:
            f = d / n
            if f.exists() and f.stat().st_size == v["size"]:
                return f
    return None


def sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(CHUNK * 8), b""):
            h.update(b)
    return h.hexdigest()


def download(v):
    dest = DEST[v["series"]]
    final = dest / v["name"]
    part = dest / (v["name"] + ".hcy.part")   # 自己的副檔名，不和對方 agent 的 .part 互相 append
    for attempt in range(1, 7):
        have = part.stat().st_size if part.exists() else 0
        if have > v["size"]:
            part.unlink(); have = 0
        if have < v["size"]:
            hdr = {"Range": f"bytes={have}-"} if have else {}
            try:
                with s.get(v["url"], headers=hdr, stream=True, timeout=(30, 120)) as r:
                    if r.status_code == 429:
                        wait = int(r.headers.get("Retry-After", 60))
                        print(f"  429，等 {wait} 秒", flush=True); time.sleep(wait); continue
                    if have and r.status_code != 206:
                        print(f"  伺服器不接受續傳（{r.status_code}），從頭下", flush=True)
                        part.unlink(); continue
                    r.raise_for_status()
                    with open(part, "ab") as f:
                        for b in r.iter_content(CHUNK):
                            f.write(b)
            except Exception as e:
                print(f"  第 {attempt} 次中斷：{e}", flush=True)
                time.sleep(15 * attempt)
                continue
        got = part.stat().st_size
        if got != v["size"]:
            print(f"  大小不符 {got}/{v['size']}，續傳", flush=True)
            continue
        h = sha1(part)
        if h != v["sha1"]:
            print(f"  SHA1 不符，刪掉重下", flush=True)
            part.unlink(); continue
        # 對方 agent 可能同時下完同一冊：已存在且大小一致就丟掉自己的
        if existing(v):
            part.unlink(); return "他方已完成"
        os.replace(part, final)
        return "ok"
    return "失敗"


def priority_keys_from_tsv(path):
    """太虛優先清單（欄位 叢刊、冊）→ 冊次集合。"""
    keys = set()
    with open(path, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            if (r.get("冊") or "").isdigit():
                keys.add((r["叢刊"], int(r["冊"])))
    return keys


def load_log(series):
    p = LOG[series]
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def save_log(series, log):
    p = LOG[series]
    tmp = p.with_suffix(".json.part")
    tmp.write_text(json.dumps(log, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", choices=["正編", "補編", "all"], default="正編")
    ap.add_argument("--from", dest="lo", type=int, default=None)
    ap.add_argument("--to", dest="hi", type=int, default=None)
    ap.add_argument("--vols", nargs="*", type=vol_key, help="指定冊次，如 正80 補53")
    ap.add_argument("--priority-tsv", help="太虛優先清單 TSV；涉及的冊次先下，其餘接著下")
    ap.add_argument("--list-only", action="store_true")
    ap.add_argument("--max-files", type=int, default=0,
                    help="這一次最多實際下載幾冊（0＝不限）；排程班用來補下，不要一班佔太久")
    a = ap.parse_args()
    if not Path(r"G:\我的雲端硬碟").exists():
        sys.exit("G: 不在（Drive 卡住），先照 CLAUDE.md 重掛再跑")
    for d in DEST.values():
        d.mkdir(parents=True, exist_ok=True)
    keys = set(a.vols) if a.vols else None
    lo, hi = a.lo, a.hi
    if keys is None and a.series == "正編" and lo is None and hi is None:
        lo, hi = 147, 204                      # 舊行為：海潮音那 58 冊
    vols = list_volumes("all" if keys else a.series, lo or 1, hi or 10 ** 6, keys)
    print(f"Commons 上符合的：{len(vols)} 個檔，合計 {sum(v['size'] for v in vols.values())/1e9:.2f} GB", flush=True)
    if a.list_only:
        for k in sorted(vols, key=lambda x: (x[0], str(x[1]).zfill(4))):
            v = vols[k]
            print(f"  {k[0]}{k[1]}  {v['size']/1e6:.0f} MB  {'已有' if existing(v) else '缺'}  {v['name']}")
        return
    prio = priority_keys_from_tsv(a.priority_tsv) if a.priority_tsv else set()
    order = sorted(vols, key=lambda k: (0 if k in prio else 1, k[0], str(k[1]).zfill(4)))
    if prio:
        print(f"優先冊次 {len([k for k in order if k in prio])} 個先下", flush=True)
    logs = {ser: load_log(ser) for ser in DEST}
    queue, streak, fetched = deque(order), 0, 0
    while queue:
        if a.max_files and fetched >= a.max_files:
            print(f"本次已下 {fetched} 冊（--max-files），其餘下次再補", flush=True)
            break
        k = queue.popleft()
        v = vols[k]
        label = f"{k[0]}{k[1]}"
        # 別人正在下：對方 agent 的 .part 10 分鐘內有更新，或本腳本另一個實例（排程班＋手動）的
        # .hcy.part 2 分鐘內有更新。兩個實例同時 append 同一個 .hcy.part 會交錯寫壞（SHA1 不符重下）。
        foreign = DEST[v["series"]] / (v["name"] + ".part")
        mine = DEST[v["series"]] / (v["name"] + ".hcy.part")
        busy = (foreign.exists() and time.time() - foreign.stat().st_mtime < 600) or \
               (mine.exists() and time.time() - mine.stat().st_mtime < 120)
        if busy and not existing(v):
            print(f"[{label}] 另一個下載程序正在下（.part 最近有更新），延後", flush=True)
            queue.append(k)
            streak += 1
            if streak >= len(queue):      # 剩下的全是對方在下的，等一下再看
                time.sleep(300); streak = 0
            continue
        streak = 0
        f = existing(v)
        if f:
            logs[v["series"]][str(k[1])] = {**v, "status": "已存在", "path": str(f)}
            print(f"[{label}] 已存在，跳過（{f.parent.name}）", flush=True)
            continue
        print(f"[{label}] 下載 {v['size']/1e6:.0f} MB …", flush=True)
        t = time.time()
        st = download(v)
        logs[v["series"]][str(k[1])] = {**v, "status": st, "path": str(DEST[v["series"]] / v["name"]),
                                        "at": time.strftime("%Y-%m-%d %H:%M:%S")}
        print(f"[{label}] {st}（{time.time()-t:.0f} 秒）", flush=True)
        fetched += 1
        save_log(v["series"], logs[v["series"]])
        time.sleep(GAP)
    for ser in DEST:
        save_log(ser, logs[ser])
    bad = [f"{k[0]}{k[1]}" for k in order
           if logs[k[0]].get(str(k[1]), {}).get("status") not in ("ok", "已存在", "他方已完成")]
    print("完成。失敗：", bad or "無", flush=True)


if __name__ == "__main__":
    main()
