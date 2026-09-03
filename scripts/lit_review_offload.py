# -*- coding: utf-8 -*-
"""把 lit_review_sections.text 搬到 R2，DB 只留骨架。

為什麼是這張表（2026-09-03 逐張查證過，不是憑印象挑的）：
  ebook_chunks   158 MB 但 content 是列表要顯示的 100 字 preview，搬走每次列表
                 都要回 R2，反而更慢；而且全文早在 Drive，這裡本來就只是索引。
  ai_dialogues×2  71 MB 看起來很適合（少讀、73% 在 TOAST），但
                 🚨 `buildDialogueKeywordFilter` 對 prompt/response 做 ILIKE 全表搜尋
                 （server/utils/dialogue-search.ts），搬走 /ai-dialogues 的搜尋會整個失效。
  lit_review_sections 90 MB —— **唯一沒有任何地方對 text 做檢索或彙總的**，
                 而且讀取模式是「一次讀一篇」，正適合 file-backed。

順手解掉一個既有問題：兩支 API 現在都在做 1000 列一頁的分頁迴圈，
註解自己寫著「整本書的條目（中國禪宗史 ~1224 段）會超過 PostgREST 的 max-rows」。
改成一篇一個 R2 物件之後，單篇一次讀完，那段迴圈可以整段拿掉。

R2：lit-review/<entry_id>.jsonl.gz　一列一段 {order_index, version_code, text}

🚨 **分四步，最後一步才不可逆**：
    --dump    讀 DB 寫 R2
    --verify  從 R2 讀回來與 DB 逐字比對（不一致就中止，不往下走）
    --stats   產出「哪些 entry 有 zh 版」的清單，給列表 API 用（免得再掃 13.8 萬列）
    --drop    確認前三步都過了，才 ALTER TABLE DROP COLUMN

  python -X utf8 scripts/lit_review_offload.py --dump --verify --stats
  python -X utf8 scripts/lit_review_offload.py --drop        # 驗證通過後才跑
"""
import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dadaodao_fulltext as df  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
PREFIX = "lit-review"
STATS = REPO / "public/content/works/lit-review-fulltext-entries.json"
PAGE = 400           # 保守：Management API 按回應大小截斷，設小一點少踩


def _env():
    for line in (REPO / ".env").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def sql(query):
    """走 Management API 跑 SQL（psycopg2 直連是 IPv6-only 跑不通的）。"""
    _env()
    url = os.environ["SUPABASE_URL"]
    ref = url.replace("https://", "").split(".")[0]
    req = urllib.request.Request(
        f"https://api.supabase.com/v1/projects/{ref}/database/query",
        data=json.dumps({"query": query}).encode("utf-8"),
        # 🚨 一定要帶 User-Agent：Management API 對沒有 UA 的請求回 403（不是 401），
        #    很容易誤判成權杖沒權限。node 的 fetch 會自動帶，urllib 不會。
        headers={"Authorization": f"Bearer {os.environ['SUPABASE_ACCESS_TOKEN']}",
                 "Content-Type": "application/json",
                 "User-Agent": "know-graph-lab/1.0"},
        method="POST")
    # 🚨 Management API 會在連續請求時斷線（RemoteDisconnected，不是 HTTP 錯誤），
    #    520 篇跑到第 460 篇就斷過一次。要重試，否則整輪白跑。
    import time as _t
    for i in range(4):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception:
            if i == 3:
                raise
            _t.sleep(3 * (i + 1))


def entry_ids():
    return [r["entry_id"] for r in sql(
        "select distinct entry_id from lit_review_sections order by entry_id")]


def sections_of(entry_id):
    """一篇的全部段落。

    🚨 **不可以用 `len(rows) < PAGE` 當結束條件。** Management API 是按
       **回應大小**截斷而不是按列數：段落文字長的時候，`limit 1000` 只回得了
       幾百列，那個判斷就會當成「讀完了」而提早跳出——無聲截斷，不報錯。
       實測同一筆 entry 兩次讀出 33,061 字與 46,771 字，數字還會變。
       所以先問 count(*)，湊滿才停；湊不滿就丟例外，寧可失敗也不要少資料。
    """
    want = sql(f"select count(*) c from lit_review_sections where entry_id = {entry_id}")[0]["c"]
    out, off = [], 0
    while len(out) < want:
        rows = sql(f"""select order_index, version_code, text
                       from lit_review_sections where entry_id = {entry_id}
                       order by order_index, version_code
                       limit {PAGE} offset {off}""")
        if not rows:                      # 還沒湊滿卻回空 → 真的有問題
            raise RuntimeError(f"entry {entry_id}：讀到 {len(out)}/{want} 段就回空")
        out += rows
        off += len(rows)                  # 用實收列數推進，不是用 PAGE
    return out


def body_of(rows):
    return "\n".join(json.dumps(r, ensure_ascii=False) for r in rows)


def dump():
    ids = entry_ids()
    print(f"{len(ids)} 篇要搬", flush=True)
    total = 0
    have = df.r2_existing_keys(PREFIX)
    for i, eid in enumerate(ids, 1):
        if f"{PREFIX}/{eid}.jsonl.gz" in have:      # 續跑：已寫過的跳過
            continue
        rows = sections_of(eid)
        df.r2_put_text_gz(f"{PREFIX}/{eid}.jsonl.gz", body_of(rows))
        total += len(rows)
        if i % 50 == 0:
            print(f"  …{i}/{len(ids)} 篇、{total:,} 段", flush=True)
    print(f"寫出 {len(ids)} 篇 / {total:,} 段", flush=True)


def verify():
    """🚨 逐字比對。不一致就回 False，呼叫端一定要中止，不可以往下 drop。"""
    ids = entry_ids()
    bad = 0
    for i, eid in enumerate(ids, 1):
        want = body_of(sections_of(eid))
        try:
            got = df.r2_get_text(f"{PREFIX}/{eid}.jsonl.gz")
        except Exception as e:  # noqa: BLE001
            print(f"  ✗ entry {eid}：R2 讀不到（{str(e)[:50]}）", flush=True)
            bad += 1
            continue
        if got != want:
            print(f"  ✗ entry {eid}：內容不一致（DB {len(want):,} vs R2 {len(got):,} 字）", flush=True)
            bad += 1
        if i % 100 == 0:
            print(f"  …已驗 {i}/{len(ids)}", flush=True)
    print(f"驗證：{len(ids) - bad}/{len(ids)} 篇一致" + ("" if not bad else f"，{bad} 篇不一致"), flush=True)
    return bad == 0


def stats():
    """哪些 entry 有 zh 版——列表 API 原本要掃 13.8 萬列才知道，改讀這份。"""
    rows = sql("""select entry_id, version_code, count(*) n
                  from lit_review_sections group by 1,2 order by 1""")
    by = {}
    for r in rows:
        by.setdefault(r["entry_id"], {})[r["version_code"]] = r["n"]
    out = [{"entryId": k, "versions": v, "hasFulltext": "zh" in v} for k, v in sorted(by.items())]
    STATS.parent.mkdir(parents=True, exist_ok=True)
    STATS.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(out)} 篇（有中譯 {sum(1 for x in out if x['hasFulltext'])}）→ {STATS}")


def drop():
    before = sql("select pg_size_pretty(pg_database_size(current_database())) t")[0]["t"]
    sql("ALTER TABLE lit_review_sections DROP COLUMN text")
    sql("VACUUM FULL lit_review_sections")
    after = sql("select pg_size_pretty(pg_database_size(current_database())) t")[0]["t"]
    print(f"資料庫：{before} → {after}")


def main():
    ap = argparse.ArgumentParser()
    for f in ("dump", "verify", "stats", "drop"):
        ap.add_argument(f"--{f}", action="store_true")
    a = ap.parse_args()
    if a.dump:
        dump()
    if a.verify and not verify():
        print("🚨 驗證未通過，中止。DB 的 text 欄原封不動。", file=sys.stderr)
        sys.exit(1)
    if a.stats:
        stats()
    if a.drop:
        drop()
    if not any([a.dump, a.verify, a.stats, a.drop]):
        ap.print_help()


if __name__ == "__main__":
    main()
