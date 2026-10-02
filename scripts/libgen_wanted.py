"""z-lib 獵表改走 LibGen 直接抓——不必排 z-lib 一天十本的隊。

使用者 2026-10-01：「如果抓得到 z-lib 的書也去查，這樣就不用排隊排那麼長了」。
Anna's Archive 有 DDOS-GUARD 要人點、而且常 504；LibGen（libgen.li）不擋程式、很穩，
所以把獵表裡還沒處理的書拿去 LibGen 搜，對得上就下載進 z-lib/ drop 夾（交給
ingest_new_books.py 照常分類），並在 z-lib 帳本記一列 downloaded，讓 z-lib 排程跳過它。

    python -X utf8 scripts/libgen_wanted.py --sources genealogy-sources,cw30-zh            # 只查不下
    python -X utf8 scripts/libgen_wanted.py --sources genealogy-sources,cw30-zh --apply    # 下載

對得上的判準（寧缺勿濫，對不上就留給 z-lib 排程）：
- 書名：獵表的 `expect` 去標點後要是 LibGen 書名的子字串（中文兩邊都轉繁比）。
- 作者：西文書要 `who` 的姓出現在作者欄；中文書要 `who` 裡的中文名或英文姓出現在作者欄，
  中文書名夠長（≥5 字）時可免。
- 多筆對得上時挑：pdf > epub > djvu、≤30MB 優先（[[feedback_download_prefer_small_files]]）、年份新的。
🚨 LibGen 常回 HTTP 500，每步重試；下載後驗檔頭，不是書檔就丟。
🚨 帳本只在**真的下載成功**時寫；查不到不寫，否則 z-lib 排程會以為處理過了。
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import time
import unicodedata
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WANTED = ROOT / "data" / "zlib-wanted"
LEDGER = ROOT / "scripts" / "state" / "zlib_ledger.jsonl"
DROP = ROOT / "z-lib"
UA = {"User-Agent": "Mozilla/5.0"}

try:
    from opencc import OpenCC
    _s2t = OpenCC("s2t").convert
except Exception:  # pragma: no cover
    _s2t = lambda s: s  # noqa: E731


def norm(s: str) -> str:
    s = _s2t(s or "")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[\W_]+", "", s.lower())


def has_cjk(s: str) -> bool:
    return bool(re.search(r"[一-鿿]", s or ""))


def get(url: str, timeout: int = 120) -> bytes:
    last = None
    for a in range(4):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(8 * (a + 1))
    raise last  # type: ignore[misc]


def search(query: str) -> list[dict]:
    s = get("https://libgen.li/index.php?" + urllib.parse.urlencode({"req": query, "res": "50", "topics[]": "l"})).decode("utf-8", "ignore")
    out = []
    for r in re.findall(r"<tr[^>]*>(.*?)</tr>", s, re.S):
        if "edition.php" not in r:
            continue
        tds = [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t))).strip() for t in re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)]
        if len(tds) < 8:
            continue
        eid = re.search(r"edition\.php\?id=(\d+)", r).group(1)
        # 第 0 欄是「叢書名＋書名＋檔名雜訊」，書名取 edition 連結的文字
        tmatch = re.findall(r'edition\.php\?id=\d+"[^>]*>([^<]{2,300})<', r)
        title = html.unescape(tmatch[-1]).strip() if tmatch else tds[0]
        m = re.match(r"([\d.]+)\s*([kMG])B", tds[6])
        mb = float(m.group(1)) * {"k": 1 / 1024, "M": 1, "G": 1024}[m.group(2)] if m else 999
        out.append({"edition": eid, "title": title, "col0": tds[0], "author": tds[1], "publisher": tds[2],
                    "year": tds[3][:4], "lang": tds[4], "mb": mb, "ext": tds[7].lower()})
    return out


def surname(who: str) -> str:
    latin = re.sub(r"[一-鿿‧·．]+", " ", who).split()
    latin = [w for w in latin if w[0].isalpha() and w.lower() not in {"ed.", "eds.", "&", "and"}]
    return latin[-1] if latin else ""


def matches(it: dict, row: dict) -> bool:
    exp = norm(it.get("expect", ""))
    if len(exp) < 3:
        return False
    hay_t = norm(row["title"] + " " + row["col0"])
    if exp not in hay_t:
        return False
    who = it.get("who", "")
    auth = norm(row["author"])
    sur = norm(surname(who))
    zh_names = [norm(x) for x in re.findall(r"[一-鿿‧·．]{2,}", who)]
    if has_cjk(it.get("expect", "")):
        if len(exp) >= 5:
            return True
        return bool((sur and sur in auth) or any(z and (z in auth or z[-2:] in auth) for z in zh_names))
    return bool(sur) and sur in auth


def pick(rows: list[dict]) -> dict | None:
    if not rows:
        return None
    pref = {"pdf": 0, "epub": 1, "djvu": 2}
    rows = [r for r in rows if r["ext"] in pref]
    if not rows:
        return None
    return sorted(rows, key=lambda r: (pref[r["ext"]], 0 if r["mb"] <= 30 else 1 if r["mb"] <= 100 else 2,
                                       -int(r["year"]) if r["year"].isdigit() else 0))[0]


def check_complete(path: Path, ext: str, expect: int) -> None:
    """下載完整才放行，否則丟例外讓外層重試。

    🚨 只驗檔頭是不夠的：LibGen 的伺服器會在半途切斷連線，copyfileobj 照樣正常結束，
    於是存下一個「檔頭正確、只有前 9／11／13 MB」的殘檔。10-01～02 那一輪 566 本裡有
    54 本是這樣（結尾都沒有 %%EOF），入庫時才被當壞檔隔離。
    """
    size = path.stat().st_size
    if expect and size != expect:
        raise ValueError(f"只下載到 {size:,}／{expect:,} bytes")
    head = path.read_bytes()[:8]
    ok = {"pdf": head.startswith(b"%PDF"), "epub": head.startswith(b"PK"), "djvu": head.startswith(b"AT&TFORM")}[ext]
    if not ok:
        raise ValueError(f"檔頭不對 {head!r}")
    if ext == "pdf":
        try:
            import fitz
            with fitz.open(str(path)) as d:
                if d.page_count < 1:
                    raise ValueError("PDF 0 頁")
        except ImportError:
            with open(path, "rb") as f:
                f.seek(max(0, size - 2048))
                if b"%%EOF" not in f.read():
                    raise ValueError("PDF 結尾沒有 %%EOF（可能被截斷）")
        except ValueError:
            raise
        except Exception as e:  # noqa: BLE001  頁面樹壞掉：page_count 會丟 RuntimeError
            raise ValueError(f"PDF 打不開：{e}")
    if ext == "epub":
        import zipfile
        if not zipfile.is_zipfile(path):
            raise ValueError("EPUB 不是完整的 zip")


def download(row: dict, name: str) -> Path:
    ed = get(f"https://libgen.li/edition.php?id={row['edition']}").decode("utf-8", "ignore")
    md5 = re.search(r"ads\.php\?md5=([0-9a-f]{32})", ed).group(1)
    ads = get(f"https://libgen.li/ads.php?md5={md5}").decode("utf-8", "ignore")
    g = re.search(r"get\.php\?md5=[0-9a-f]{32}&(?:amp;)?key=\w+", ads).group(0).replace("&amp;", "&")
    safe = re.sub(r'[\\/:*?"<>|]', "", name)[:180]
    dst = DROP / f"{safe}.{row['ext']}"
    tmp = dst.with_suffix(dst.suffix + ".part")
    # 正反兩支會合時會同時抓同一本，兩邊搶同一個 .part 互鎖（WinError 32，10-02 齊澤烏拉斯那本）。
    if dst.exists() or tmp.exists():
        raise FileExistsError(f"另一支已在下載或已下載：{dst.name}")
    for a in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request("https://libgen.li/" + g, headers=UA), timeout=1800) as r, open(tmp, "wb") as f:
                expect = int(r.headers.get("Content-Length") or 0)
                shutil.copyfileobj(r, f, 1 << 20)
            check_complete(tmp, row["ext"], expect)
            tmp.replace(dst)
            return djvu_to_pdf(dst) if row["ext"] == "djvu" else dst
        except Exception as e:  # noqa: BLE001
            print("   重試", a, e)
            time.sleep(15)
    tmp.unlink(missing_ok=True)
    raise RuntimeError("下載失敗")


DDJVU = Path(r"C:\Program Files (x86)\DjVuLibre\ddjvu.exe")


def djvu_to_pdf(src: Path) -> Path:
    """ingest_new_books.py 不收 djvu（會列在 non-ebook files 略過），抓到就轉成 PDF，
    原檔移到 z-lib/_converted/。轉不成就原樣留著（交人處理），不丟例外。"""
    import subprocess
    dst = src.with_suffix(".pdf")
    if not DDJVU.exists() or dst.exists():
        return src
    r = subprocess.run([str(DDJVU), "-format=pdf", "-quality=85", str(src), str(dst)], capture_output=True, timeout=3600)
    if r.returncode != 0 or not dst.exists() or dst.stat().st_size < 50000:
        dst.unlink(missing_ok=True)
        print("   djvu 轉檔失敗，原檔留著：", r.stderr[:200])
        return src
    conv = src.parent / "_converted"
    conv.mkdir(exist_ok=True)
    src.replace(conv / src.name)
    return dst


def done_keys() -> set[str]:
    out = set()
    if LEDGER.exists():
        for line in LEDGER.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("key") and r.get("status") != "dry":
                out.add(r["key"])
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", default="", help="逗號分隔的 source 名（比對獵表每筆的 source 欄）")
    ap.add_argument("--queue", action="store_true",
                    help="改讀 zlib_wanted.py 產生的整份排隊清單 output/zlib_wanted_all.jsonl（已排序、已濾黑名單與期刊單篇）")
    ap.add_argument("--shard", default="", help="k/n：只做清單第 k 份（共 n 份，依序號取餘），多支並跑用")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--reverse", action="store_true", help="從清單尾端往前查；同一份清單可另開一支倒著跑，在中間會合")
    a = ap.parse_args()
    srcs = set(filter(None, a.sources.split(",")))
    done = done_keys()
    items = []
    files = [ROOT / "output" / "zlib_wanted_all.jsonl"] if a.queue else sorted(WANTED.glob("*.jsonl"))
    for f in files:
        for line in f.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                it = json.loads(line)
            except json.JSONDecodeError:
                continue
            if "key" not in it or it["key"] in done:   # 缺 key 的不是獵書格式（見 zlib_wanted.load_curated）
                continue
            if a.queue or it.get("source") in srcs:
                items.append(it)
    if a.shard:
        k, n = map(int, a.shard.split("/"))
        items = [it for i, it in enumerate(items) if i % n == k]
    if a.reverse:
        items.reverse()
    if a.limit:
        items = items[: a.limit]
    print(f"分母：{len(items)} 筆未處理（{'整份排隊清單' if a.queue else '來源 ' + ', '.join(sorted(srcs))}{' 分片 ' + a.shard if a.shard else ''}）")
    hit = got = 0
    for i, it in enumerate(items, 1):
        if a.reverse and it["key"] in done_keys():   # 正向那支可能已經抓過（兩支會合時）
            print(f"[{i}] ＝ 已由另一支處理 {it['query']}")
            break
        try:
            rows = [r for r in search(it["query"]) if matches(it, r)]
            if not rows and has_cjk(it["query"]):
                rows = [r for r in search(it.get("expect", "")) if matches(it, r)]
        except Exception as e:  # noqa: BLE001
            print(f"[{i}] 查詢失敗 {it['query']}：{e}")
            continue
        best = pick(rows)
        if not best:
            print(f"[{i}] ✗ {it['query']}")
            time.sleep(1.5)
            continue
        hit += 1
        print(f"[{i}] ✓ {it['query']}  →  {best['title'][:70]} | {best['author'][:40]} | {best['year']} {best['ext']} {best['mb']:.1f}MB")
        if a.apply:
            try:
                p = download(best, f"{best['title'][:120]} ({best['author'][:60]})")
                got += 1
                with LEDGER.open("a", encoding="utf-8") as f:
                    f.write(json.dumps({"key": it["key"], "query": it["query"], "status": "downloaded", "file": p.name,
                                        "pick": {"via": "libgen", "edition": best["edition"], "title": best["title"],
                                                 "author": best["author"], "year": best["year"], "extension": best["ext"]},
                                        "at": datetime.now(timezone.utc).isoformat()}, ensure_ascii=False) + "\n")
                print(f"     已下載 {p.name}")
            except Exception as e:  # noqa: BLE001
                print(f"     下載失敗：{e}")
        time.sleep(2)
    print(f"\n分母 {len(items)}｜對得上 {hit}｜已下載 {got}")
    return 0


def retry_corrupt() -> None:
    """帳本記為 LibGen 下載、但檔案被 ingest 隔離到 z-lib/_corrupt/ 的，照原 edition 重抓（完整才算）。"""
    corrupt = DROP / "_corrupt"
    rows = []
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if (r.get("pick") or {}).get("via") == "libgen" and r.get("file") and (corrupt / r["file"]).exists():
            rows.append(r)
    print(f"分母：{len(rows)} 本殘檔要重抓")
    ok = 0
    for i, r in enumerate(rows, 1):
        p = Path(r["file"])
        row = {"edition": r["pick"]["edition"], "ext": r["pick"].get("extension") or p.suffix.lstrip(".")}
        try:
            got = download(row, p.stem)
            (corrupt / r["file"]).unlink(missing_ok=True)
            ok += 1
            print(f"[{i}] ✓ {got.name}")
        except Exception as e:  # noqa: BLE001
            print(f"[{i}] ✗ {p.name}：{e}")
        time.sleep(2)
    print(f"\n分母 {len(rows)}｜重抓成功 {ok}")


if __name__ == "__main__" and len(__import__("sys").argv) > 1 and __import__("sys").argv[1] == "--retry-corrupt":
    retry_corrupt()
    raise SystemExit(0)

if __name__ == "__main__" and len(__import__("sys").argv) > 1 and __import__("sys").argv[1] == "--convert-djvu":
    for f in sorted(DROP.glob("*.djvu")):
        print(f.name, "→", djvu_to_pdf(f).name)
    raise SystemExit(0)

if __name__ == "__main__":
    raise SystemExit(main())
