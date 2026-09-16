"""佛教大藏經 /tripitaka —— 目錄 rows 進 Supabase、逐段全文上 R2。

分工（遵守「新大內容表一律 file-backed」）：
  Supabase  只存目錄（2,554 列、約 1.5 MB）＋各部的對照語言旗標
  Drive     `_tripitaka/{id}.jsonl`（逐段正文）為 canonical
  R2        `tripitaka/{id}.jsonl.gz`（線上後備，單檔多在 100 KB 內）

9,700 萬字的正文絕不進 DB —— 2026-07 那次超量鎖站就是這樣來的。

  python scripts/tripitaka_db.py --schema          # 建表（冪等）
  python scripts/tripitaka_db.py --push            # catalog.json → tripitaka_works
  python scripts/tripitaka_db.py --push-dk         # DK.catalog.json（德格版甘珠爾）
  python scripts/tripitaka_db.py --sync-drive      # 本機 out/ → Drive _tripitaka/
  python scripts/tripitaka_db.py --push-r2 [--only T0262]
"""
from __future__ import annotations

import argparse
import gzip
import io
import json
import os
import re
import shutil
import sys
import time
import urllib.request
from pathlib import Path

# 主控台若是 cp950，印 ✓ 或藏文會炸 UnicodeEncodeError——而且是在工作
# 做完之後才炸，看起來像失敗其實已經寫進去了。
sys.stdout.reconfigure(encoding="utf-8")

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import tripitaka_cbeta as tc  # noqa: E402

REF = "vloqgautkahgmqcwgfuo"
MGMT = f"https://api.supabase.com/v1/projects/{REF}/database/query"
CATALOG = Path(os.environ.get("TRIPITAKA_CATALOG", "C:/tmp/cbeta/catalog.json"))
LOCAL_OUT = Path(os.environ.get("TRIPITAKA_LOCAL", "C:/tmp/cbeta/out"))
R2_PREFIX = "tripitaka/"


def _env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        raise RuntimeError(f"缺 {key}")
    return v


def sql(query: str) -> list:
    req = urllib.request.Request(
        MGMT, data=json.dumps({"query": query}).encode(),
        headers={"Authorization": f"Bearer {_env('SUPABASE_ACCESS_TOKEN')}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        body = r.read().decode()
    return json.loads(body) if body.strip() else []


SCHEMA = """
create table if not exists tripitaka_works (
  id              text primary key,
  canon           text not null,
  vol             int  not null,
  work_no         int  not null,
  work_suffix     text default '',
  title_zh        text not null,
  series          text,
  byline          text,
  dynasty         text,
  translator      text,
  author          text,
  lost_translator boolean default false,
  extent          text,
  juan_count      int,
  division_key    text not null,
  japanese        boolean default false,
  xml_path        text,
  seg_count       int default 0,
  char_count      int default 0,
  toc_count       int default 0,
  -- equiv_count：大正藏原註標出的巴利對應條數
  -- term_count / term_langs：CBETA <cb:tt> 漢梵巴詞條（全藏 29,930 組、142 部）
  equiv_count     int default 0,
  term_count      int default 0,
  term_langs      text[] default '{}',
  parallel_langs  text[] default '{}',
  pali_ref        text,
  sanskrit_ref    text,
  tibetan_toh     text,
  parallel_count  int default 0,
  display_order   int
);
create index if not exists tripitaka_works_div_idx
  on tripitaka_works (division_key, display_order);
create index if not exists tripitaka_works_canon_idx
  on tripitaka_works (canon, work_no);
create index if not exists tripitaka_works_title_idx
  on tripitaka_works using gin (to_tsvector('simple', title_zh));

-- 藏文大藏經（德格版甘珠爾，canon='DK'）專用欄。
-- 🚨 甘珠爾是藏譯，`title_zh` 對它而言是「漢譯對照本的書名」而不是本名，
--    而且 661 部根本沒有漢譯對照 → 那一欄是空字串。顯示與搜尋都必須
--    退到 title_bo／title_en，不然目錄會列出一整片沒有標題的列。
alter table tripitaka_works add column if not exists toh            text;
alter table tripitaka_works add column if not exists title_bo       text;
alter table tripitaka_works add column if not exists title_bo_short text;
alter table tripitaka_works add column if not exists title_sa       text;
alter table tripitaka_works add column if not exists title_en       text;
alter table tripitaka_works add column if not exists translator_en  text;
alter table tripitaka_works add column if not exists folio_start    text;
alter table tripitaka_works add column if not exists folio_end      text;
-- 漢譯對照本清單 [{id,t,title,checked?}]，來源見 tripitaka_derge_zh.py
alter table tripitaka_works add column if not exists zh_parallels   jsonb;
create index if not exists tripitaka_works_toh_idx on tripitaka_works (canon, toh);

-- 逐段的跨語對照。段本身在檔案裡，這裡只記「哪一段對到什麼」。
-- src: taisho-equiv（大正藏原註）/ suttacentral / gretil / 84000 / manual
create table if not exists tripitaka_parallels (
  id       bigserial primary key,
  work_id  text not null references tripitaka_works(id) on delete cascade,
  -- 段的**唯一鍵**（T02n0099_p0001a06 或同行第二段的 …a06.2）。
  -- 純行號不唯一：全藏 6.5% 的段與別的段同行起頭，拿行號當鍵會讓
  -- 對照掛到同一行的其他段上。引用式仍是行號，顯示時去掉 .n 後綴。
  -- 整部層級的列用空字串而非 NULL：唯一索引若寫成 coalesce(seg_uid,'')
  -- 是運算式索引，PostgREST 的 on_conflict 認不得，寫入會回 42P10。
  seg_uid  text not null default '',
  lang     text not null,
  ref      text not null,
  src      text not null,
  note     text
);
create index if not exists tripitaka_parallels_work_idx on tripitaka_parallels (work_id);
create unique index if not exists tripitaka_parallels_uniq
  on tripitaka_parallels (work_id, seg_uid, lang, ref, src);

alter table tripitaka_works    enable row level security;
alter table tripitaka_parallels enable row level security;
drop policy if exists tripitaka_works_read on tripitaka_works;
create policy tripitaka_works_read on tripitaka_works for select to authenticated using (true);
drop policy if exists tripitaka_parallels_read on tripitaka_parallels;
create policy tripitaka_parallels_read on tripitaka_parallels for select to authenticated using (true);
"""


def series_of(row: dict) -> str:
    """南傳一部書常被切成數冊（『長部經典(第1卷-第14卷)』×3 冊），
    目錄要按書歸群而不是按冊平鋪。大正藏的 T0220a/b/c 同理。"""
    t = row["title_zh"]
    base = re.sub(r"[（(]第.*?[)）]\s*$", "", t).strip()
    return base or t


def cmd_schema():
    """DDL 走直連；直連不通就退回 Management API。

    🚨 兩條路都會壞，而且壞法不一樣，所以兩條都要留著：
       直連 `db.{ref}.supabase.co` 有時候連 DNS 都解不到
       （`could not translate host name`，換網路環境就會出現）；
       Management API 則是那把 personal access token 會過期。
    """
    try:
        pg_exec(SCHEMA)
        print("✓ tripitaka_works / tripitaka_parallels 已就緒（直連）")
        return
    except Exception as e:                      # noqa: BLE001
        print(f"直連不通（{type(e).__name__}: {str(e).strip().splitlines()[-1]}），"
              f"改走 Management API")
    sql(SCHEMA)
    print("✓ tripitaka_works / tripitaka_parallels 已就緒（Management API）")


COLS = ["id", "canon", "vol", "work_no", "work_suffix", "title_zh", "series", "byline",
        "dynasty", "translator", "author", "lost_translator", "extent", "juan_count",
        "division_key", "subdivision_key", "japanese", "xml_path", "seg_count", "char_count",
        "toc_count", "equiv_count", "term_count", "term_langs", "display_order"]


def pg_exec(sql_text: str, params=None):
    """直連 Postgres 跑 SQL。DDL 與「只更新部分欄位」的回填走這條。

    2026-08-29 更正：先前判定「直連 IPv6-only 無路由」是錯的 —— 當時只用
    `ping -6` 逾時就下結論，但 ICMP 被擋不代表 TCP 不通，而且當時沒裝驅動。
    裝上 psycopg2 後 db.{ref}.supabase.co:5432 直接連得上（密碼在 .env）。
    """
    import psycopg2
    conn = psycopg2.connect(
        host=_env("KGL_DB_HOST"), port=int(os.environ.get("KGL_DB_PORT", 5432)),
        user=os.environ.get("KGL_DB_USER", "postgres"), password=_env("KGL_DB_PASSWORD"),
        dbname=os.environ.get("KGL_DB_NAME", "postgres"),
        connect_timeout=15, sslmode="require")
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute(sql_text, params)
            return cur.fetchall() if cur.description else []
    finally:
        conn.close()


def postgrest(path: str, rows: list[dict] | None = None, method: str = "POST"):
    """走 PostgREST（service role key）。DDL 才需要 Management API，
    寫資料不用 —— 2026-08 那把 personal access token 過期時就是靠這條路繞過去的。"""
    url = _env("SUPABASE_URL").rstrip("/") + "/rest/v1/" + path
    key = _env("SUPABASE_SERVICE_ROLE_KEY")
    data = json.dumps(rows, ensure_ascii=False).encode() if rows is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "apikey": key, "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=minimal",
    })
    with urllib.request.urlopen(req, timeout=120) as r:
        body = r.read().decode()
    return json.loads(body) if body.strip() else []


def cmd_push():
    rows = json.loads(CATALOG.read_text(encoding="utf-8"))
    # 藏經次序照目錄頁的群組：大正藏 → 卍續藏 → 漢譯南傳。
    # 原本寫成 `canon != "T"`（T=0、其餘都=1），N 與 X 會依冊號交錯排在一起。
    _CANON_ORDER = {"T": 0, "X": 1, "N": 2}
    rows.sort(key=lambda r: (_CANON_ORDER.get(r["canon"], 9), r["vol"],
                             r["work_no"], r.get("work_suffix", "")))
    payload = []
    for n, r in enumerate(rows, start=1):
        rec = {c: r.get(c) for c in COLS}
        rec["series"] = series_of(r)
        rec["display_order"] = n
        rec["work_suffix"] = r.get("work_suffix") or ""
        rec["term_langs"] = r.get("term_langs") or []
        payload.append(rec)

    for i in range(0, len(payload), 400):
        postgrest("tripitaka_works?on_conflict=id", payload[i:i + 400])
        print(f"  … {min(i + 400, len(payload))}/{len(payload)}", flush=True)
    print(f"✓ tripitaka_works 已寫入 {len(payload)} 列")


DK_CATALOG = Path(os.environ.get(
    "DK_CATALOG",
    "G:/我的雲端硬碟/資料/知識圖工作室/_tripitaka_tibetan/DK.catalog.json"))
# DK 的 display_order 從一萬起跳，與 CBETA 那 3,784 部錯開。
# 兩邊是分開推的，`--push` 只會把 CBETA 重編成 1…3,784；留出空檔，
# 重推任一邊都不會把另一邊的次序打亂。
DK_ORDER_BASE = 10_000


def cmd_push_dk():
    """德格版甘珠爾目錄 → tripitaka_works（canon='DK'）。

    🚨 `title_zh` 在這裡的意思與漢文藏經不同：它是**漢譯對照本**的書名，
       不是這部經自己的名字（甘珠爾是藏譯，沒有漢文本名）。661 部沒有
       對照本，那一欄就是空字串。`series` 一律填得出東西（漢譯對照 →
       英譯題名 → 藏文題名），列表與搜尋要靠它，不要靠 title_zh。
    """
    if not DK_CATALOG.exists():
        raise SystemExit(f"✗ 找不到 {DK_CATALOG}（先跑 tripitaka_derge.py --build）")
    doc = json.loads(DK_CATALOG.read_text(encoding="utf-8"))
    works = doc["works"]

    payload = []
    for n, w in enumerate(works, start=1):
        zh = w.get("title_zh") or ""
        folio = f'{w.get("folio_start") or ""}–{w.get("folio_end") or ""}'.strip("–")
        payload.append({
            "id": w["id"],
            "canon": "DK",
            "vol": w["vol"],
            # 目錄冊沒有 Toh 號，但 work_no 是 not null；排最後。
            "work_no": w["toh_no"] if w["toh_no"] is not None else 9999,
            "work_suffix": w.get("toh_suffix") or "",
            "title_zh": zh,
            "series": zh or w.get("title_en") or w.get("title_bo") or w["id"],
            # 🚨 `translator_en` 是 **84000 的現代英譯者**（Gareth Sparham、
            #    Gyurme Dorje…），不是九世紀把它譯成藏文的譯師。塞進
            #    byline／translator 的話，頁面會在一部藏文經旁邊寫
            #    「譯者：Gareth Sparham」，看起來完全正常而且沒人會察覺。
            #    這兩欄對甘珠爾留空，英譯者只放在自己的欄位、由 UI 標明來歷。
            "byline": "",
            "translator": "",
            # 藏文大藏經的單位是「函」（帙）不是「冊」
            "extent": f"{folio}（第 {w['vol']} 函）" if folio else f"第 {w['vol']} 函",
            "division_key": w["division_key"],
            "japanese": False,
            "seg_count": w.get("seg_count") or 0,
            "char_count": w.get("char_count") or 0,
            "toc_count": w.get("sub_count") or 0,
            "term_langs": [],
            "parallel_langs": ["zh"] if zh else [],
            "parallel_count": len(w.get("zh_parallels") or []),
            "display_order": DK_ORDER_BASE + n,
            "toh": w.get("toh") or None,
            "tibetan_toh": w.get("toh") or None,
            "title_bo": w.get("title_bo") or None,
            "title_bo_short": w.get("title_bo_short") or None,
            "title_sa": w.get("title_sa") or None,
            "title_en": w.get("title_en") or None,
            "translator_en": w.get("translator_en") or None,
            "folio_start": w.get("folio_start") or None,
            "folio_end": w.get("folio_end") or None,
            "zh_parallels": w.get("zh_parallels") or [],
        })

    for i in range(0, len(payload), 300):
        postgrest("tripitaka_works?on_conflict=id", payload[i:i + 300])
        print(f"  … {min(i + 300, len(payload))}/{len(payload)}", flush=True)
    withzh = sum(1 for r in payload if r["title_zh"])
    print(f"✓ tripitaka_works 寫入 DK {len(payload)} 列"
          f"（{withzh} 部有漢譯對照、{len(payload) - withzh} 部只有藏文）")


def cmd_sync_drive():
    dst = tc.OUT_DIR
    dst.mkdir(parents=True, exist_ok=True)
    files = sorted(LOCAL_OUT.glob("*"))
    print(f"{len(files)} 檔 → {dst}")
    for i, f in enumerate(files, 1):
        t = dst / f.name
        if t.exists() and t.stat().st_size == f.stat().st_size:
            continue
        shutil.copy2(f, t)
        if i % 200 == 0:
            print(f"  … {i}/{len(files)}", flush=True)
    print("✓ Drive 同步完成")


def _r2():
    import boto3  # noqa: F401
    from botocore.config import Config
    import boto3 as b3
    return b3.client("s3", endpoint_url=_env("R2_ENDPOINT"),
                     aws_access_key_id=_env("R2_ACCESS_KEY"),
                     aws_secret_access_key=_env("R2_SECRET_KEY"),
                     region_name="auto", config=Config(signature_version="s3v4"))


def _r2_existing(s3, bucket: str) -> set[str]:
    """已在 R2 上的 key。全藏 5,295 檔重傳一次要十幾分鐘，
    補幾個新檔不該把整批再推一遍。"""
    keys: set[str] = set()
    token = None
    while True:
        kw = {"Bucket": bucket, "Prefix": R2_PREFIX, "MaxKeys": 1000}
        if token:
            kw["ContinuationToken"] = token
        r = s3.list_objects_v2(**kw)
        keys.update(o["Key"] for o in r.get("Contents", []))
        if not r.get("IsTruncated"):
            return keys
        token = r["NextContinuationToken"]


def cmd_push_r2(only: str | None, force: bool = False, suffix: str | None = None,
                dk: bool = False):
    s3, bucket = _r2(), _env("R2_BUCKET")
    # 🚨 來源必須是 Drive（正本），不是本機 out/。
    # 原本寫成「本機目錄存在就用本機」，但 tripitaka_cbeta 是**建到 Drive** 的，
    # 而 tripitaka_sanskrit／vernacular 建到本機 —— 兩邊內容不一樣。
    # 於是推 X 那 2,480 個檔時，它去掃本機（沒有 X）、發現本機的檔 R2 都已有，
    # 印出「✓ R2 0 檔」當作成功，X 一個都沒上去。見 SKILL 踩坑 25。
    # 藏文大藏經在另一個 Drive 夾（_tripitaka_tibetan），R2 的 key 前綴共用。
    # 檔名 DKtoh0113.jsonl 與漢文那批不會撞。
    src = DK_CATALOG.parent if dk else (tc.OUT_DIR if tc.OUT_DIR.exists() else LOCAL_OUT)
    files = sorted(f for f in src.glob(f"{only}.*" if only else "*")
                   if f.is_file() and f.name != "DK.catalog.json")
    print(f"來源 {src}（{len(files)} 檔）", flush=True)
    if suffix:
        # 只重推某一類檔（例：對照層重建後只有 *.orig.json 變了，
        # 不必把 108 MB 的正文再推一遍）
        files = [f for f in files if f.name.endswith(suffix)]
    have = set() if force else _r2_existing(s3, bucket)
    if have:
        skip = sum(1 for f in files if f"{R2_PREFIX}{f.name}.gz" in have)
        print(f"R2 已有 {len(have)} 物件，本批跳過 {skip} 檔")
        files = [f for f in files if f"{R2_PREFIX}{f.name}.gz" not in have]
    big, failed = [], []
    for i, f in enumerate(files, 1):
        # 🚨 讀檔要自己擋。來源在 Drive，DriveFS 抖一下就回 OSError 22，
        #    而這一行原本在重試圈外——2,248 檔推到 1,200 檔時整批 traceback 中止。
        #    上傳失敗只記一筆繼續跑，讀檔失敗卻會炸掉整支，不合理。
        try:
            raw = f.read_bytes()
        except OSError as e:
            failed.append((f.name, f"讀檔 {type(e).__name__}"))
            continue
        buf = io.BytesIO()
        with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0) as g:
            g.write(raw)
        data = buf.getvalue()
        # R2 政策：單檔 >10 MB 一律不上（見 docs/r2-policy.md）
        if len(data) > 10 * 1024 * 1024:
            big.append((f.name, len(data)))
            continue
        # 5,295 檔的上傳不該被一次網路抖動整個打掉 —— 退避重試三次，
        # 三次都失敗才記下來繼續推下一檔（結尾列出未成功者）。
        for attempt in range(3):
            try:
                s3.put_object(Bucket=bucket, Key=f"{R2_PREFIX}{f.name}.gz",
                              Body=data, ContentType="application/json",
                              ContentEncoding="gzip")
                break
            except Exception as e:  # noqa: BLE001
                if attempt == 2:
                    failed.append((f.name, type(e).__name__))
                else:
                    time.sleep(2 ** attempt)
        if i % 200 == 0:
            print(f"  … {i}/{len(files)}", flush=True)
    print(f"✓ R2 {len(files) - len(big) - len(failed)} 檔")
    for name, n in big:
        print(f"  ⚠ 超過 10 MB 未上傳（Drive 仍有正本）: {name} {n/1048576:.1f} MB")
    for name, err in failed:
        print(f"  ⚠ 三次重試仍失敗（Drive 仍有正本，可重跑本指令補）: {name} {err}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--schema", action="store_true")
    ap.add_argument("--push", action="store_true")
    ap.add_argument("--push-dk", action="store_true",
                    help="德格版甘珠爾目錄 → tripitaka_works")
    ap.add_argument("--sync-drive", action="store_true")
    ap.add_argument("--push-r2", action="store_true")
    ap.add_argument("--dk", action="store_true",
                    help="--push-r2 改推藏文大藏經那一夾")
    ap.add_argument("--only", type=str)
    ap.add_argument("--force", action="store_true", help="不管 R2 已有，全部重傳")
    ap.add_argument("--suffix", type=str, help="只推指定後綴的檔，如 .orig.json")
    a = ap.parse_args()
    if a.schema:
        cmd_schema()
    if a.push:
        cmd_push()
    if a.push_dk:
        cmd_push_dk()
    if a.sync_drive:
        cmd_sync_drive()
    if a.push_r2:
        cmd_push_r2(a.only, a.force, a.suffix, a.dk)
    if not any([a.schema, a.push, a.push_dk, a.sync_drive, a.push_r2]):
        ap.print_help()


if __name__ == "__main__":
    main()
