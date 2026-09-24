"""臺大佛學數位圖書館（DLBS）標「有全文」的《海潮音》篇章 PDF 下載。

篇目明細：R2 research-private/dlbs/haichaoyin.jsonl.gz（press_dlbs.py 產生；本腳本只讀）。
2026-09-24 盤點：1,141 篇全部是戰後台灣《海潮音》（1998、2002、2007–2025），不是民國原刊，
所以與集成正編 147–204 冊不重複，要抓。

- FULLTEXTPATH 三種：https://buddhism.lib.ntu.edu.tw/FT/JA/<seq>.pdf（1,138）、
  http://…/FULLTEXT/JR-MISC/misc<seq>.pdf（2，上下篇共用同一檔）、fjdh.cn 網頁（1）。
  buddhism.lib.ntu.edu.tw 會 308 轉到 dlbs.liberal.ntu.edu.tw，要跟轉址。
- 檔名「年_卷期_篇名.pdf」；同一路徑被兩篇共用時只抓一次，對照表記兩列。
- 驗內容開頭是 %PDF（抓到 HTML 錯誤頁也會 200）。先寫 .part 再改名；已存在且非空就跳過，可中斷續跑。
- 用法：python scripts/haichaoyin_dlbs_fetch.py
"""
import csv, gzip, io, json, os, re, sys, time
from pathlib import Path
import boto3, requests

ROOT = Path(__file__).resolve().parents[1]
DEST = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\研究資料\民國與台灣佛教史\海潮音\DLBS全文")
UA = "know-graph-lab research downloader (redpiigpig@gmail.com)"
GAP = 1.5


def env():
    e = {}
    for l in open(ROOT / ".env", encoding="utf-8"):
        if "=" in l and not l.lstrip().startswith("#"):
            k, v = l.strip().split("=", 1)
            e[k] = v.strip().strip('"').strip("'")
    return e


def rows():
    e = env()
    s3 = boto3.client("s3", region_name="auto", endpoint_url=e["R2_ENDPOINT"],
                      aws_access_key_id=e["R2_ACCESS_KEY"], aws_secret_access_key=e["R2_SECRET_KEY"])
    b = s3.get_object(Bucket=e["R2_BUCKET"], Key="research-private/dlbs/haichaoyin.jsonl.gz")["Body"].read()
    return [json.loads(l) for l in gzip.decompress(b).decode("utf-8").splitlines() if l.strip()]


def vol_issue(archive):
    m = re.match(r"v\.\s*(\d+)\s*n\.\s*([\d/\-]+)", archive or "")
    return f"v{m.group(1)}n{m.group(2).replace('/', '-')}" if m else re.sub(r"[^\w]+", "", archive or "") or "無卷期"


def safe(t, n=60):
    t = re.sub(r'[\\/:*?"<>|\r\n\t]+', "_", t).strip(" ._")
    return t[:n] or "無題"


def main():
    if not Path(r"G:\我的雲端硬碟").exists():
        sys.exit("G: 不在（Drive 卡住），先照 CLAUDE.md 重掛再跑")
    DEST.mkdir(parents=True, exist_ok=True)
    arts = [r for r in rows() if r.get("fulltext")]
    print(f"有全文 {len(arts)} 篇", flush=True)
    s = requests.Session(); s.headers["User-Agent"] = UA
    by_path, table = {}, []
    for r in sorted(arts, key=lambda r: (r.get("presstime", ""), int(r["seq"]))):
        path = r["path"]
        ext = ".html" if not path.lower().endswith(".pdf") else ".pdf"
        if path in by_path:
            fn = by_path[path]
        else:
            fn = f"{r.get('year') or '無年'}_{vol_issue(r.get('archive'))}_{safe(r['title'])}{ext}"
            # 檔名撞名（同期同題的連載）時加 seq
            if fn in by_path.values():
                fn = fn[:-len(ext)] + f"_{r['seq']}{ext}"
            by_path[path] = fn
        table.append((r, fn))
    ok = fail = skip = 0
    failed = []
    done_paths = set()
    for r, fn in table:
        path = r["path"]
        if path in done_paths:
            continue
        done_paths.add(path)
        f = DEST / fn
        if f.exists() and f.stat().st_size > 0:
            skip += 1; continue
        part = f.with_name(f.name + ".part")
        err = None
        for attempt in range(1, 5):
            try:
                resp = s.get(path, timeout=(30, 180), allow_redirects=True)
                if resp.status_code == 404:
                    err = "404"; break
                resp.raise_for_status()
                body = resp.content
                if fn.endswith(".pdf") and not body.startswith(b"%PDF"):
                    err = f"不是 PDF（{resp.headers.get('Content-Type')}，{len(body)} bytes）"; break
                part.write_bytes(body)
                os.replace(part, f)
                err = None; break
            except Exception as e:
                err = str(e)[-200:]
                time.sleep(10 * attempt)
        if err:
            fail += 1; failed.append((r["seq"], path, err))
            print(f"  ✗ {r['seq']} {err}", flush=True)
        else:
            ok += 1
        if (ok + fail) % 50 == 0:
            print(f"進度 下載 {ok}／失敗 {fail}／已有 {skip}", flush=True)
        time.sleep(GAP)
    # 對照表（每篇一列，含共用檔）
    failed_paths = {p for _, p, _ in failed}
    with open(DEST / "_篇目對照.tsv", "w", encoding="utf-8-sig", newline="") as fo:
        w = csv.writer(fo, delimiter="\t")
        w.writerow(["seq", "年", "出版年月", "卷期", "頁", "篇名", "作者", "檔名", "原始路徑", "狀態"])
        for r, fn in table:
            st = "失敗" if r["path"] in failed_paths else "有"
            w.writerow([r["seq"], r.get("year"), r.get("presstime"), r.get("archive"), r.get("page"),
                        r["title"], r.get("author"), fn, r["path"], st])
    if failed:
        with open(DEST / "_失敗清單.tsv", "w", encoding="utf-8-sig", newline="") as fo:
            w = csv.writer(fo, delimiter="\t")
            w.writerow(["seq", "路徑", "錯誤"]); w.writerows(failed)
    print(f"完成：篇目 {len(table)}、不重複檔 {len(done_paths)}、本次下載 {ok}、已有 {skip}、失敗 {fail}", flush=True)


if __name__ == "__main__":
    main()
