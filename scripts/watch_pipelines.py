#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""三條長跑管線的一頁式對帳：全集轉錄／每日下載（華藝‧z-lib）／圖書館 OCR。

會做這支的原因：這三條都是排程在背景跑的，各自的徵狀藏在不同地方——排程的
LastTaskResult、c:/tmp 的 log 尾巴、Drive 的檔案數、DB 的 chunk_count。任何一條
「排程還 Ready、log 還在寫，但其實已經沒有產出」都不會有人通知
（[[feedback_disable_finished_schedules]]、[[feedback_build_not_equal_deployed]]）。
所以這支一律**看產出**，排程狀態只當佐證。

  python scripts/watch_pipelines.py              # 三條全看
  python scripts/watch_pipelines.py --author mircea-eliade   # 併看某位全集作家
  python scripts/watch_pipelines.py --quiet      # 只印警訊（給排程用）
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import pathlib
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
DRIVE = pathlib.Path("G:/我的雲端硬碟/資料/知識圖工作室")
AIRITI_DIR = DRIVE / "研究資料" / "華藝期刊全文"
CW_DIR = DRIVE / "全集"
ZLIB_LEDGER = ROOT / "scripts/state/zlib_ledger.jsonl"
ZLIB_WANTED = ROOT / "output/zlib_wanted_all.jsonl"
ZLIB_DROP = ROOT / "z-lib"
LOGS = ROOT / "scripts/logs"

TASKS = [
    "KGL_CW_Translation",
    "KGL_Translation_Supervisor",
    "KGL_Fleet_Keeper",
    "KGL_Airiti_Poll",
    "KGL_ZLib_Daily",
    "KGLab-OCR-Daily-10",
    "KGLab-OCR-Daily-14",
    "KGLab-OCR-Daily-18",
]

warnings: list[str] = []


def warn(msg: str) -> None:
    warnings.append(msg)


# ── Supabase（只讀）─────────────────────────────────────────────────────

def _env() -> dict[str, str]:
    out = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


_E = _env()
_URL = _E["SUPABASE_URL"].rstrip("/")
_KEY = _E.get("SUPABASE_SERVICE_ROLE_KEY") or _E["SUPABASE_KEY"]
_H = {"apikey": _KEY, "Authorization": f"Bearer {_KEY}"}


def q(path: str, count: bool = False, tries: int = 3):
    """PostgREST 查詢。count=True 走 Content-Range 拿總數。

    🚨 不帶 limit 的查詢會被靜默截在 1000 筆（[[feedback_postgrest_silent_1000_cap]]），
    所以要全量的地方一律用 page() 分頁，不要直接呼叫這支。

    🚨 會重試：這支是無人值守每 30 分鐘跑的監控，2026-09-08 因為一次
    `WinError 10054 遠端主機已強制關閉連線` 整個 traceback 死掉——監控自己被瞬斷
    打死，比它要監控的東西還脆弱。網路不穩正是最需要看到報告的時候。
    """
    h = dict(_H)
    if count:
        h["Prefer"] = "count=exact"
        h["Range"] = "0-0"
    last = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(f"{_URL}/rest/v1/{path}", headers=h)
            with urllib.request.urlopen(req, timeout=60) as r:
                body = r.read().decode("utf-8")
                cr = r.headers.get("Content-Range", "")
            if count:
                return int(cr.split("/")[-1]) if "/" in cr else 0
            return json.loads(body)
        except (urllib.error.URLError, OSError, ValueError) as e:
            last = e
            if attempt < tries - 1:
                time.sleep(2 * (attempt + 1))
    raise _Unreachable(str(last))


class _Unreachable(RuntimeError):
    """連不上 DB。呼叫端要接住並印「這一節看不到」，而不是讓整份報告消失。"""


def page(path: str, size: int = 1000) -> list[dict]:
    out, off = [], 0
    sep = "&" if "?" in path else "?"
    while True:
        rows = q(f"{path}{sep}limit={size}&offset={off}")
        out += rows
        if len(rows) < size:
            return out
        off += size


# ── 排程狀態（佐證用，不當判準）────────────────────────────────────────

def scheduled_tasks() -> dict[str, dict]:
    ps = (
        "$ErrorActionPreference='SilentlyContinue';"
        "Get-ScheduledTask | Where-Object { $_.TaskName -in @(" +
        ",".join(f"'{t}'" for t in TASKS) +
        ") } | ForEach-Object { $i=$_ | Get-ScheduledTaskInfo;"
        " [pscustomobject]@{name=$_.TaskName;state=[string]$_.State;"
        " last=[string]$i.LastRunTime;result=$i.LastTaskResult;next=[string]$i.NextRunTime} }"
        " | ConvertTo-Json -Compress"
    )
    try:
        raw = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", ps],
            capture_output=True, text=True, timeout=90, encoding="utf-8",
        ).stdout.strip()
        data = json.loads(raw) if raw else []
    except Exception:
        return {}
    if isinstance(data, dict):
        data = [data]
    return {d["name"]: d for d in data}


def fmt_result(code: int | None) -> str:
    """LastTaskResult 的人話。267009 是「正在跑」不是錯誤，最容易誤讀。

    🚨 2147946720（0x800710E0）不要讀成憑證問題。排程器拿它表示「這一輪沒有執行」，
    最常見的成因是**觸發時機器在睡、而該工作沒勾 StartWhenAvailable**——事件記錄
    id=153 會明說「missed its schedule」。2026-09-08 的 OCR-Daily-18 就是這樣整輪
    蒸發，連 log 都沒寫，而我一開始把它讀成憑證掉了、差點去查錯方向。
    """
    return {
        0: "ok",
        267009: "執行中",
        267011: "尚未跑過",
        None: "?",
        3221225786: "被中止 (睡眠/Ctrl+C/登出)",
        2147946720: "未執行 (多半是錯過排程，看事件 id=153)",
    }.get(code, f"exit={code}")


# ── 一、全集轉錄 ────────────────────────────────────────────────────────

def section_collected_works(author: str | None) -> None:
    print("━━ 一、全集轉錄 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    rows = page("ebooks?select=title,author,chunk_count,total_chars,parse_error&collection=eq.collected-works")
    empty = [r for r in rows if not (r.get("chunk_count") or 0)]
    thin = [r for r in rows if 0 < (r.get("chunk_count") or 0) <= 5]
    print(f"  DB collection=collected-works：{len(rows)} 本"
          f"（有內容 {len(rows) - len(empty)}、空 {len(empty)}、疑似殘缺 {len(thin)}）")
    if empty:
        warn(f"全集有 {len(empty)} 本掛在 collected-works 卻沒有任何 chunk")
        for r in empty[:5]:
            print(f"    ⚠ 空：{r.get('author')}《{r['title'][:36]}》 {str(r.get('parse_error'))[:40]}")
    if thin:
        print(f"    ⓘ 疑似殘缺（≤5 段，多半是只吃到目錄）前 5：")
        for r in thin[:5]:
            print(f"      {r.get('author')}《{r['title'][:32]}》 {r['chunk_count']} 段／{r.get('total_chars')} 字")

    # Drive 側：全集各學科實際有幾個檔（沒有檔＝這位作家根本還沒開工）
    if CW_DIR.exists():
        parts = []
        for d in sorted(CW_DIR.iterdir()):
            if d.is_dir():
                parts.append(f"{d.name} {sum(1 for _ in d.rglob('*') if _.is_file())}")
        print(f"  Drive 全集/：{'、'.join(parts)}")

    if author:
        section_author(author)


def section_author(slug: str) -> None:
    """某位全集作家的三方對帳：hub works[] ／ DB ／ z-lib 獵表。"""
    store = (ROOT / "stores/collectedWorks.ts").read_text(encoding="utf-8")
    i = store.find(f'"slug": "{slug}"')
    if i < 0:
        i = store.find(f"slug: '{slug}'")
    if i < 0:
        print(f"  （hub 找不到 {slug}）")
        return
    seg = store[i:i + 20000]
    nxt = seg.find('"slug": "', 10)
    if nxt > 0:
        seg = seg[:nxt]
    name = name_en = ""
    for line in seg.splitlines():
        if '"name"' in line and not name:
            name = line.split('"')[3]
        if '"nameEn"' in line and not name_en:
            name_en = line.split('"')[3]
    works = []
    cur = {}
    # 這個 store 一半手寫 TS 一半 JSON dump，key 有的帶引號有的不帶，值也是單雙引號混用。
    # 🚨 ebookId 特別要吃不帶引號那種——backfill regex（isolation.spec 驗的那條）要求
    # 寫成 `ebookId: 'xxx'`，只認 `"ebookId":` 會把剛接好的書report成「沒有 ebookId」。
    field_re = re.compile(
        r"""["']?(title|status|ebookId|note)["']?\s*:\s*["']([^"']*)["']"""
    )
    for line in seg.splitlines():
        m = field_re.search(line)
        if m:
            cur[m.group(1)] = m.group(2)
        if line.strip().startswith("}") and cur.get("title"):
            works.append(cur)
            cur = {}
    print(f"\n  ▸ {name}（{slug}） hub works[]：{len(works)} 部")
    for w in works:
        eb = w.get("ebookId") or "—"
        print(f"      {w['title'][:28]:<30} status={w.get('status'):<12} ebookId={eb}")
    if works and not any(w.get("ebookId") for w in works):
        warn(f"{name} hub 的 {len(works)} 部書全都沒有 ebookId，/collected-works 上一本都點不開")

    # DB 側：這個人的書在庫裡是什麼狀態（不限 collection，圖書館那份也要看到）。
    # 🚨 姓氏要取完整那一段，不能截字：「伊利亞」會把《伊利亞特》(Iliad) 一起撈進來。
    surname = name.split("‧")[-1] if "‧" in name else name
    terms = {surname, name_en.split()[-1] if name_en else ""} - {""}
    ors = ",".join(
        f"{col}.ilike.*{urllib.parse.quote(t)}*"
        for t in terms for col in ("title", "author", "file_path")
    )
    hits = q(f"ebooks?select=title,collection,chunk_count,total_chars,parse_error"
             f"&or=({ors})&limit=50")
    print(f"    DB 現有 {len(hits)} 本：")
    for h in hits:
        c = h.get("chunk_count") or 0
        mark = "✓" if c > 5 else ("△" if c else "✗")
        where = h.get("collection") or "圖書館"
        print(f"      {mark} {h['title'][:30]:<32} {where:<16} {c} 段／{h.get('total_chars') or 0} 字"
              f" {str(h.get('parse_error') or '')[:28]}")
        if 0 < c <= 5:
            warn(f"{name}《{h['title'][:20]}》只有 {c} 段——像是抽到文字層空的掃描本（假成功）")
        if not c:
            warn(f"{name}《{h['title'][:20]}》0 段，待 OCR：{str(h.get('parse_error'))[:30]}")
    if hits and all((h.get("collection") or "") != "collected-works" for h in hits):
        warn(f"{name} 的書全在圖書館、沒有一本標 collected-works"
             f"（[[feedback_collected_works_not_in_library]] 要搬）")

    # z-lib 獵表：排在第幾、輪不輪得到
    if ZLIB_WANTED.exists() and ZLIB_LEDGER.exists():
        wanted = [json.loads(l) for l in ZLIB_WANTED.read_text(encoding="utf-8").splitlines() if l.strip()]
        # 🚨 要跟 zlib_fetch.doneKeys() 同一套語意：status='dry' 是「只查沒下載」，
        # 那邊明確不算已處理。這裡要是照單全收，跑一輪 --dry-run 就會讓獵表進度
        # 假性前進（2026-09-08 一輪 11 筆 dry 讓「未處理」從 22 掉到 11）。
        done = {r["key"] for r in
                (json.loads(l) for l in ZLIB_LEDGER.read_text(encoding="utf-8").splitlines() if l.strip())
                if r.get("status") != "dry"}
        mine = [(n, w) for n, w in enumerate(wanted)
                if any(t.lower() in json.dumps(w, ensure_ascii=False).lower() for t in terms)]
        todo = [(n, w) for n, w in mine if w["key"] not in done]
        if mine:
            print(f"    z-lib 獵表：{len(mine)} 筆，未處理 {len(todo)}"
                  f"（整張表 {len(wanted)} 筆已處理 {len(done)}）")
            if todo:
                first = min(n for n, _ in todo)
                # 只有「排在射程外」才算警訊。已經插到隊首的（見 zlib_wanted.FOCUS_AUTHORS）
                # 每輪都喊一次就成了狼來了，反而蓋掉真的警訊。
                reach = len(done) + 200
                if first + 1 > reach:
                    warn(f"{name} 在 z-lib 獵表最早排在第 {first + 1}/{len(wanted)} 筆，"
                         f"目前才處理到 {len(done)} 筆——不插隊輪不到")
                else:
                    print(f"      ↳ 最早排在第 {first + 1} 筆，在射程內")


# ── 二、每日下載（華藝 ‧ z-lib）───────────────────────────────────────

def section_downloads(tasks: dict) -> None:
    print("\n━━ 二、每日下載 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    today = dt.date.today().isoformat()

    # 華藝：看 Drive 上的 PDF 數，不看 log 說下了幾篇
    if AIRITI_DIR.exists():
        pdfs = list(AIRITI_DIR.rglob("*.pdf"))
        n_today = sum(1 for p in pdfs
                      if dt.date.fromtimestamp(p.stat().st_mtime).isoformat() == today)
        by = collections.Counter(p.relative_to(AIRITI_DIR).parts[0] for p in pdfs)
        print(f"  華藝：Drive 累計 {len(pdfs)} 篇 PDF，今天 {n_today} 篇；"
              f"{len(by)} 種刊，最大宗 {by.most_common(1)[0][0]} {by.most_common(1)[0][1]}")
        if n_today == 0:
            warn(f"華藝今天（{today}）一篇都沒落地")
    t = tasks.get("KGL_Airiti_Poll")
    if t:
        print(f"    排程 {t['state']}／{fmt_result(t.get('result'))}／上次 {t.get('last')}")

    # z-lib：帳本＋ drop 夾
    if ZLIB_LEDGER.exists():
        recs = [json.loads(l) for l in ZLIB_LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()]
        wanted_n = sum(1 for _ in ZLIB_WANTED.open(encoding="utf-8")) if ZLIB_WANTED.exists() else 0
        c = collections.Counter(r.get("status", "?") for r in recs)
        last = recs[-1]["at"][:10] if recs else "—"
        n_today = sum(1 for r in recs if r["at"][:10] == today)
        # 帳本會有重試，同一 key 出現多次；進度要看去重後的 key 數，不是行數。
        # 🚨 而且要排除 status='dry'——那是「只查沒下載」，zlib_fetch 下一輪還會再做，
        # 算進去會讓一輪 --dry-run 看起來像推進了獵表。
        uniq = len({r["key"] for r in recs if r.get("status") != "dry"})
        n_dry = sum(1 for r in recs if r.get("status") == "dry")
        print(f"  z-lib：獵表 {wanted_n} 筆，已處理 {uniq} 筆／{len(recs)} 次嘗試"
              f"（{uniq / wanted_n * 100:.1f}%；另有 {n_dry} 次只查不算數）"
              f"；今天 {n_today} 次，最後動作 {last}")
        print(f"    {dict(c)}")
        if n_today == 0:
            warn(f"z-lib 今天（{today}）沒有任何新處理，最後動作停在 {last}")
    drop = list(ZLIB_DROP.glob("*")) if ZLIB_DROP.exists() else []
    print(f"    drop 夾待 ingest：{len([p for p in drop if p.is_file()])} 檔")
    t = tasks.get("KGL_ZLib_Daily")
    if t:
        print(f"    排程 {t['state']}／{fmt_result(t.get('result'))}／上次 {t.get('last')}／下次 {t.get('next')}")
        if t.get("result") not in (0, 267009):
            warn(f"KGL_ZLib_Daily 上次收在 {fmt_result(t.get('result'))}")
    # 抓瀏覽器層的失敗。
    # 🚨 2026-09-08 實測釐清：站沒掛、DiamWall 過得去、登入與搜尋都正常。
    # zlib_fetch.mjs 是 headless:false + channel:'chrome'，開的是**看得見的 Chrome 視窗**；
    # 那個視窗一被關掉（登出、關視窗、工作階段結束）整輪就斷在半路，噴的就是這兩句。
    # 所以看到它別再去查網路或 cookie——查的是「那一輪跑的時候視窗還在不在」。
    zl = LOGS / "zlib_daily.log"
    if zl.exists():
        tail = zl.read_text(encoding="utf-8", errors="replace")[-6000:]
        if "browser has been closed" in tail:
            warn("z-lib 上一輪斷在『瀏覽器被關』——headless:false 的實體 Chrome 視窗中途消失，非網路問題")
        elif "TimeoutError" in tail:
            warn("z-lib 上一輪有 Playwright 逾時（單筆逾時可容忍，整輪都是才要查站況）")


# ── 三、圖書館 OCR ─────────────────────────────────────────────────────

def section_ocr(tasks: dict) -> None:
    print("\n━━ 三、電子圖書館 OCR／解析 ━━━━━━━━━━━━━━━━━━━━━━")
    tot = q("ebooks?select=id", count=True)
    parsed = q("ebooks?select=id&parsed_at=not.is.null", count=True)
    err = q("ebooks?select=id&parse_error=not.is.null", count=True)
    nul = q("ebooks?select=id&chunk_count=is.null", count=True)
    zero = q("ebooks?select=id&chunk_count=eq.0", count=True)
    print(f"  ebooks {tot} 本：已 parsed {parsed}、有 parse_error {err}")
    print(f"  待轉錄 {nul + zero} 本（chunk_count 為 null {nul}、為 0 {zero}）"
          f" → 完成率 {(tot - nul - zero) / tot * 100:.1f}%")

    logs = sorted(LOGS.glob("ocr_*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    if logs:
        newest = logs[0]
        txt = newest.read_text(encoding="utf-8", errors="replace")
        ok = txt.count("✓")
        bad = txt.count("❌")
        quota = txt.count("RESOURCE_EXHAUSTED")
        net = txt.count("getaddrinfo failed") + txt.count("WinError 10053")
        age = dt.datetime.now() - dt.datetime.fromtimestamp(newest.stat().st_mtime)
        print(f"  最新 OCR 日誌 {newest.name}（{age.days} 天 {age.seconds // 3600} 小時前）："
              f"成功 {ok}、失敗 {bad}、額度 {quota}、斷網 {net}")
        if bad > ok:
            warn(f"{newest.name} 失敗數（{bad}）多於成功數（{ok}）")
        if net:
            warn(f"{newest.name} 有 {net} 次連不上 Supabase／Gemini——那批 parse_error 沒被記錄，會重跑")
    for n in ("KGLab-OCR-Daily-10", "KGLab-OCR-Daily-14", "KGLab-OCR-Daily-18"):
        t = tasks.get(n)
        if t:
            print(f"    {n}：{t['state']}／{fmt_result(t.get('result'))}／上次 {t.get('last')}")

    # 翻譯艦隊：keeper 每輪重拉的那幾條線還活著沒
    fk = LOGS / "fleet_keeper.log"
    if fk.exists():
        tail = fk.read_text(encoding="utf-8", errors="replace").splitlines()[-40:]
        started = [l.split("started ")[1].split(" pid=")[0] for l in tail if "started " in l]
        if started:
            print(f"  艦隊最後一輪重拉：{'、'.join(dict.fromkeys(started))}")
        age = dt.datetime.now() - dt.datetime.fromtimestamp(fk.stat().st_mtime)
        if age.total_seconds() > 3 * 3600:
            warn(f"fleet_keeper 已 {age.total_seconds() / 3600:.1f} 小時沒動作")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--author", help="併看某位全集作家（hub slug，如 mircea-eliade）")
    ap.add_argument("--quiet", action="store_true", help="只印警訊")
    a = ap.parse_args()

    tasks = scheduled_tasks()
    if a.quiet:
        buf = []
        import io, contextlib
        with contextlib.redirect_stdout(io.StringIO()):
            section_collected_works(a.author)
            section_downloads(tasks)
            section_ocr(tasks)
    else:
        print(f"◆ 管線對帳 {dt.datetime.now():%Y-%m-%d %H:%M}\n")
        section_collected_works(a.author)
        section_downloads(tasks)
        section_ocr(tasks)

    print("\n━━ 警訊 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    if warnings:
        for w in warnings:
            print(f"  🚨 {w}")
    else:
        print("  （無）")
    return 1 if warnings else 0


if __name__ == "__main__":
    sys.exit(main())
