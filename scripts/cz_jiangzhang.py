# -*- coding: utf-8 -*-
"""城中講章（龐牧師親撰證道稿，2004-2006 + 講道/）→ pong_sermons.content。
把講章當逐字稿，依 gold-standard 格式（講者標籤＋【段落標題】＋全形標點）寫入。
Word COM 抽取 → 解析 主題/經課/日期 → 格式化 body → 對應日期的 row（fill-if-empty content）。
用法： python scripts/cz_jiangzhang.py            (dry-run + 印樣本)
       python scripts/cz_jiangzhang.py --apply
"""
import os, sys, re, json, glob, datetime, requests
sys.stdout.reconfigure(encoding="utf-8")

APPLY = "--apply" in sys.argv
ROOT = os.path.abspath(r"pong-archive/stores/城中週報")
with open(".env", encoding="utf-8") as f:
    for line in f:
        if line.strip() and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1); os.environ[k.strip()] = v.strip()
SB = os.environ["SUPABASE_URL"].rstrip("/") + "/rest/v1"
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

DATE6 = re.compile(r"(?<!\d)(\d{2})(\d{2})(\d{2})(?!\d)")   # 050102
DATE8 = re.compile(r"(?<!\d)(20\d{2})(\d{2})(\d{2})(?!\d)")  # 20070114
MMDD = re.compile(r"(?<!\d)(\d{2})(\d{2})(?!\d)")            # 0111 (2004, year from path)
TITLE_RE = re.compile(r"^(?:證道主題|講道主題|證道題目|講道題目|講題|主題|題目)\s*[：:]\s*(.+)$")
SCRIP_HDR = re.compile(r"^(?:經課|經文|讀經)\s*[：:]\s*(.+)$")
SKIP_HDR = re.compile(r"^(?:證道|主禮|司會|整理|司琴|讀經|招待|主後|主曆).{0,40}$|^主後|.*主日$|.*主日崇拜$|^[0-9０-９\s年月日]+$")
HEADING_WORDS = ("前言", "引言", "結論", "結語", "小結", "反省", "禱告", "結束")

def clean(t):
    return t.replace("\r", "").replace("\x07", " ").replace("\xa0", " ").replace("\x0b", " ").strip()

_word = None
def get_word():
    global _word
    if _word is None:
        import win32com.client as win32
        _word = win32.gencache.EnsureDispatch("Word.Application"); _word.Visible = False; _word.DisplayAlerts = False
    return _word

def read_doc(path):
    doc = get_word().Documents.Open(path, ReadOnly=True, AddToRecentFiles=False, Visible=False)
    try:
        return [clean(x) for x in re.split(r"[\r\n]", doc.Content.Text) if clean(x)]
    finally:
        doc.Close(False)

def _valid(y, mo, da):
    try:
        datetime.date(int(y), int(mo), int(da)); return 2003 <= int(y) <= 2026
    except ValueError:
        return False

def parse_date(path):
    base = os.path.basename(path); rel = os.path.relpath(path, ROOT).replace("\\", "/")
    m = DATE8.search(base)
    if m and _valid(*m.groups()): return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    # year from path segment: 講章/2005/... or 講章/2005講章/...
    ym = re.search(r"/(20\d{2})(?:講章)?/", rel) or re.search(r"(20\d{2})講章", rel)
    base_year = ym.group(1) if ym else None
    m = DATE6.search(base)            # YYMMDD
    if m and _valid("20" + m.group(1), m.group(2), m.group(3)):
        return f"20{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m = MMDD.match(base)              # MMDD prefix (year from path)
    if m and base_year and _valid(base_year, m.group(1), m.group(2)):
        return f"{base_year}-{m.group(1)}-{m.group(2)}"
    return None

FNAME_TITLE = re.compile(r"^\d{2,8}[\-－]?(.+?)(?:r\d)?\.docx?$")
def fname_title(path):
    """Extract title from a descriptive filename: 0108主受洗日－這是我的愛子 -> (主受洗日, 這是我的愛子)."""
    b = os.path.basename(path)
    m = FNAME_TITLE.match(b)
    if not m: return None, None
    rest = m.group(1).strip(" －-")
    if not rest or rest[0].isdigit(): return None, None
    parts = re.split(r"[－\-]", rest, 1)
    if len(parts) == 2 and ("主日" in parts[0] or "節" in parts[0] or "日" in parts[0]):
        return parts[0].strip(), parts[1].strip()
    return None, rest

PREACHER_LINE = re.compile(r"^(?:證道|講員|講道|主禮[／/]證道|主禮[／/]講員)\s*[：:]\s*(\S{2,12})")
def detect_preacher(raw):
    for p in raw[:10]:
        m = PREACHER_LINE.match(p)
        if m:
            name = m.group(1)
            if "龐" in name: return "龐"
            if "邱" in name or "蕢" in name: return name  # 邱泰耀 / 蕢建華 etc.
            return name
    return None  # unknown

def is_heading(line):
    if any(line.startswith(w) or line == w for w in HEADING_WORDS):
        return True
    if len(line) <= 18 and not re.search(r"[。，、！？；：]$", line) and not line.startswith("「") \
       and not re.search(r"\d{1,3}[:：]\d", line) and "。" not in line:
        return True
    return False

def parse_from_raw(paras):
    title = scrip = None
    body_start = 0
    for i, p in enumerate(paras[:8]):
        mt = TITLE_RE.match(p)
        if mt and not title: title = mt.group(1).strip()
        ms = SCRIP_HDR.match(p)
        if ms and not scrip: scrip = ms.group(1).strip()
        if p.startswith("前言") or p.startswith("引言"):
            body_start = i; break
        if SKIP_HDR.match(p) or TITLE_RE.match(p) or SCRIP_HDR.match(p):
            body_start = i + 1
    body = paras[body_start:]
    return title, scrip, body

def format_content(body, date_iso):
    title_word = "龐君華牧師" if date_iso < "2019-05-01" else "龐君華會督"
    blocks = [f"{title_word}："]
    for p in body:
        if not p: continue
        blocks.append(f"【{p.strip('【】 ')}】" if is_heading(p) else p)
    return "\n\n".join(blocks)

def fetch_pang():
    rows, off = {}, 0
    while True:
        r = requests.get(f"{SB}/pong_sermons", headers={**H, "Range": f"{off}-{off+999}"},
                         params={"select": "id,sermon_date,title,scripture_ref,content,media_id", "order": "sermon_date"})
        b = r.json()
        if not b: break
        for x in b: rows[x["sermon_date"]] = x
        off += 1000
        if len(b) < 1000: break
    return rows

def collect():
    files = []
    for dp, dn, fn in os.walk(os.path.join(ROOT, "講章")):
        for f in fn:
            if f.lower().endswith((".doc", ".docx")) and not f.startswith("~$") \
               and "主日程序" not in f and "程序" not in f:
                files.append(os.path.join(dp, f))
    for f in glob.glob(os.path.join(ROOT, "講道", "*.doc*")):
        if not os.path.basename(f).startswith("~$"):
            files.append(f)
    return sorted(set(files))

def advent1(year):
    xmas = datetime.date(year, 12, 25); wd = xmas.weekday()
    days = (wd + 1) % 7 or 7
    return xmas - datetime.timedelta(days=days) - datetime.timedelta(weeks=3)

def church_year(d):
    dt = datetime.date.fromisoformat(d)
    return dt.year if dt >= advent1(dt.year) else dt.year - 1

def snap_sunday(d):
    dt = datetime.date.fromisoformat(d); wd = dt.weekday()
    if wd == 6: return d
    fwd, back = (6 - wd) % 7, (wd + 1) % 7
    if min(fwd, back) <= 3:
        return (dt + datetime.timedelta(days=(fwd if fwd <= back else -back))).isoformat()
    return d

SPECIAL_KW = ("復活", "受難", "聖誕", "將臨", "顯現節主日", "立約", "聖靈降臨主日",
              "基督君王", "感恩", "堂慶", "追思", "登山變", "聖灰", "棕枝", "濯足", "升天")
GENERIC = {"", "主日崇拜", "主日證道", "主日禮拜", None}

def main():
    files = collect()
    rows = fetch_pang()
    bull = {b["date"]: b for b in json.load(open("public/content/chengzhong-bulletins/index.json", encoding="utf-8"))["items"]}
    print(f"講章/講道 docs: {len(files)} | pong_sermons rows: {len(rows)}")
    nodate = 0
    cand = {}
    for path in files:
        d = parse_date(path)
        if not d:
            nodate += 1; continue
        d = snap_sunday(d)
        try:
            raw = read_doc(path)
        except Exception as e:
            print("  ! read err", os.path.basename(path), e); continue
        preacher = detect_preacher(raw)
        title, scrip, body = parse_from_raw(raw)
        occ_fn, title_fn = fname_title(path)
        rec = {"date": d, "preacher": preacher, "title": title or title_fn, "occasion": occ_fn,
               "scrip": scrip, "content": format_content(body, d), "file": os.path.relpath(path, ROOT)}
        rec["len"] = len(rec["content"])
        cur = cand.get(d)
        # prefer 龐 > unknown > other; tie-break richest
        def rank(r): return ((2 if r["preacher"] == "龐" else 0 if r["preacher"] else 1), r["len"])
        if not cur or rank(rec) > rank(cur):
            cand[d] = rec

    filled = backfilled = created = skipped = 0
    samples = []
    for d, rec in sorted(cand.items()):
        b = bull.get(d)
        bull_pang = bool(b and b.get("preacher") and "龐" in b["preacher"])
        is_pang = (rec["preacher"] == "龐") or (rec["preacher"] is None and bull_pang)
        if not is_pang:                       # 邱泰耀/其他/無法確認 → 不動
            skipped += 1; continue
        if rec["len"] < 300:
            continue
        era = "龐君華牧師" if d < "2019-05-01" else "龐君華會督"
        occasion = rec["occasion"] or (b.get("season") if b else None)
        row = rows.get(d)
        if not row:                            # 無 row → 建新列（含講章全文）
            dt = datetime.date.fromisoformat(d)
            is_special = occasion and any(k in occasion for k in SPECIAL_KW)
            payload = {"id": int(d.replace("-", "")), "sermon_date": d, "title": rec["title"] or "主日崇拜",
                       "preacher": era, "officiant": era, "occasion": occasion, "liturgical_season": occasion,
                       "scripture_ref": rec["scrip"], "content": rec["content"], "church_year": church_year(d),
                       "location": "衛理公會城中教會", "sermon_type": "特殊節日" if is_special else "主日講道",
                       "has_recording": False, "is_published": True, "sort_order": 0}
            created += 1; samples.append(("建列", d, rec["title"], rec["len"], rec["file"]))
            if APPLY:
                r = requests.post(f"{SB}/pong_sermons", headers={**H, "Prefer": "return=minimal"}, json=payload)
                if r.status_code >= 300: print("  ! INSERT fail", d, r.status_code, r.text[:120])
            continue
        has_content = row.get("content") and len(row["content"].strip()) > 200
        payload = {}
        if has_content:
            # 已有逐字稿/講章 → 只補空的 preacher/officiant（明確是龐），不動 title/content（避免日期偏移誤植）
            if not row.get("preacher"): payload["preacher"] = era
            if not row.get("officiant"): payload["officiant"] = era
            if not payload:
                continue
            backfilled += 1; samples.append(("補preacher", d, row.get("title"), len(row["content"]), rec["file"]))
        else:
            # 空 row → 灌入講章全文，title/occasion/scripture 以講章為準（彼此一致）
            payload = {"content": rec["content"], "has_recording": False, "preacher": era}
            if not row.get("officiant"): payload["officiant"] = era
            if rec["title"]: payload["title"] = rec["title"]
            if occasion and not row.get("occasion"): payload["occasion"] = occasion
            if rec["scrip"] and not row.get("scripture_ref"): payload["scripture_ref"] = rec["scrip"]
            filled += 1; samples.append(("灌稿", d, rec["title"], rec["len"], rec["file"]))
        if APPLY and payload:
            r = requests.patch(f"{SB}/pong_sermons?id=eq.{row['id']}", headers={**H, "Prefer": "return=minimal"}, json=payload)
            if r.status_code >= 300: print("  ! PATCH fail", d, r.status_code, r.text[:120])
    if _word: _word.Quit()
    print(f"\n去重講章: {len(cand)} 日期 | 無日期檔: {nodate} | 非龐/無法確認跳過: {skipped}")
    print(f"灌入講章全文(空row): {filled} | 補 metadata(已有稿): {backfilled} | 新建列: {created}")
    print("\n樣本:")
    for tag, d, t, n, f in samples[:18]:
        print(f"  [{tag}] {d}  {t!s:22} {n}字  ←{f}")
    if not APPLY:
        print("\n（dry-run。加 --apply 寫入）")

if __name__ == "__main__":
    main()
