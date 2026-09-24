"""《民國佛教期刊文獻集成》正編 147–204 冊（《海潮音》1920–1949）從 Wikimedia Commons 整冊下載。

- 目標夾：Drive 研究資料\\民國與台灣佛教史\\民國佛教期刊文獻集成\\正編\\，檔名＝Commons 原檔名（去掉 File:）。
- 共用夾：另有 agent 也往這裡存。下載前檢查同名檔（空白／底線兩種寫法都認）是否已存在且大小一致，有就跳過。
- 寫入先寫 .part、驗大小＋SHA1 後才改名；.part 用 Range 續傳，筆電休眠或中斷後重跑即可接著下。
- 用法：python scripts/haichaoyin_commons_fetch.py [--from 147 --to 204] [--list-only]
"""
import argparse, hashlib, json, os, re, sys, time
from pathlib import Path
import requests

UA = "know-graph-lab research downloader (redpiigpig@gmail.com)"
API = "https://commons.wikimedia.org/w/api.php"
CAT = "Category:民國佛教期刊文獻集成"
DEST = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\研究資料\民國與台灣佛教史\民國佛教期刊文獻集成\正編")
ALSO_CHECK = [Path(r"G:\我的雲端硬碟\資料\知識圖工作室\研究資料\民國與台灣佛教史\太虛研究\集成影印\_整冊")]
LOG = DEST / "_下載紀錄_海潮音.json"
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


def list_volumes(lo, hi):
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
        m = re.search(r"正編 第(\d+)卷", t)
        if m and lo <= int(m.group(1)) <= hi:
            want[int(m.group(1))] = t
    out = {}
    keys = sorted(want)
    for i in range(0, len(keys), 20):
        r = api({"action": "query", "titles": "|".join(want[k] for k in keys[i:i + 20]),
                 "prop": "imageinfo", "iiprop": "url|size|sha1"})
        by_title = {pg["title"]: pg for pg in r["query"]["pages"].values()}
        for k in keys[i:i + 20]:
            ii = by_title[want[k]]["imageinfo"][0]
            out[k] = {"title": want[k], "name": want[k].split(":", 1)[1],
                      "url": ii["url"], "size": ii["size"], "sha1": ii["sha1"]}
    return out


def existing(name, size):
    for d in [DEST] + ALSO_CHECK:
        for n in {name, name.replace(" ", "_")}:
            f = d / n
            if f.exists() and f.stat().st_size == size:
                return f
    return None


def sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(CHUNK * 8), b""):
            h.update(b)
    return h.hexdigest()


def download(v):
    final = DEST / v["name"]
    part = DEST / (v["name"] + ".hcy.part")   # 自己的副檔名，不和對方 agent 的 .part 互相 append
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
        if existing(v["name"], v["size"]):
            part.unlink(); return "他方已完成"
        os.replace(part, final)
        return "ok"
    return "失敗"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="lo", type=int, default=147)
    ap.add_argument("--to", dest="hi", type=int, default=204)
    ap.add_argument("--list-only", action="store_true")
    a = ap.parse_args()
    if not Path(r"G:\我的雲端硬碟").exists():
        sys.exit("G: 不在（Drive 卡住），先照 CLAUDE.md 重掛再跑")
    DEST.mkdir(parents=True, exist_ok=True)
    vols = list_volumes(a.lo, a.hi)
    print(f"Commons 上 {a.lo}–{a.hi} 冊：{len(vols)} 個，合計 {sum(v['size'] for v in vols.values())/1e9:.2f} GB", flush=True)
    log = json.loads(LOG.read_text(encoding="utf-8")) if LOG.exists() else {}
    if a.list_only:
        return
    # 太虛研究那個 agent 要的冊次排最後，讓它先下，輪到時多半已存在可跳過
    TAIXU = set(range(170, 176)) | set(range(180, 183)) | set(range(186, 189)) | set(range(192, 196)) | set(range(202, 205))
    order = [k for k in sorted(vols) if k not in TAIXU] + [k for k in sorted(vols) if k in TAIXU]
    from collections import deque
    queue, streak = deque(order), 0
    while queue:
        k = queue.popleft()
        v = vols[k]
        foreign = DEST / (v["name"] + ".part")
        if foreign.exists() and time.time() - foreign.stat().st_mtime < 600 and not existing(v["name"], v["size"]):
            print(f"[{k}] 對方 agent 正在下（.part 10 分鐘內有更新），延後", flush=True)
            queue.append(k)
            streak += 1
            if streak >= len(queue):      # 剩下的全是對方在下的，等一下再看
                time.sleep(300); streak = 0
            continue
        streak = 0
        f = existing(v["name"], v["size"])
        if f:
            log[str(k)] = {**v, "status": "已存在", "path": str(f)}
            print(f"[{k}] 已存在，跳過（{f.parent.name}）", flush=True)
            continue
        print(f"[{k}] 下載 {v['size']/1e6:.0f} MB …", flush=True)
        t = time.time()
        st = download(v)
        log[str(k)] = {**v, "status": st, "path": str(DEST / v["name"]),
                       "at": time.strftime("%Y-%m-%d %H:%M:%S")}
        print(f"[{k}] {st}（{time.time()-t:.0f} 秒）", flush=True)
        tmp = LOG.with_suffix(".json.part")
        tmp.write_text(json.dumps(log, ensure_ascii=False, indent=1), encoding="utf-8")
        os.replace(tmp, LOG)
        time.sleep(GAP)
    bad = [k for k in sorted(vols) if log.get(str(k), {}).get("status") not in ("ok", "已存在", "他方已完成")]
    print("完成。失敗：", bad or "無", flush=True)


if __name__ == "__main__":
    main()
