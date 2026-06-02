# -*- coding: utf-8 -*-
"""Parse raw.jsonl (城中週報) -> structured records. Regex/heuristic field extraction.
Outputs: index.json (light, for listing+search) and per-date detail JSON files."""
import sys, os, re, json, glob, collections, datetime
sys.stdout.reconfigure(encoding='utf-8')

def easter(y):
    """Western (Gregorian) Easter Sunday — Anonymous Gregorian algorithm."""
    a = y % 19; b = y // 100; c = y % 100; d = b // 4; e = b % 4
    f = (b + 8) // 25; g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30; i = c // 4; k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7; m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31; day = ((h + l - 7 * m + 114) % 31) + 1
    return datetime.date(y, month, day)

LOOSE_DATE = re.compile(r"(?<!\d)(\d{2})-(\d{1,2})-(\d{1,2})(?!\d)")
# (keyword in filename/season, days offset from Easter Sunday, service label)
SPECIAL_SERVICES = [
    ("復活節朝陽", 0, "復活節朝陽崇拜"), ("朝陽崇拜", 0, "復活節朝陽崇拜"),
    ("受難節", -2, "受難節禮拜"), ("受難日", -2, "受難節禮拜"), ("聖週五", -2, "受難節禮拜"),
    ("濯足", -3, "濯足節禮拜"), ("聖週四", -3, "濯足節禮拜"),
    ("棕枝", -7, "棕枝主日"), ("聖枝", -7, "棕枝主日"),
    ("大齋首", -46, "聖灰日禮拜"), ("聖灰", -46, "聖灰日禮拜"),
    ("復活", 0, "復活節崇拜"),
]

def resolve_special_date(source_file, season, head):
    """For bulletins whose filename has no clean date — derive from Easter-relative
    special-service name + the year embedded in the path. Returns (date, service) or (None, None)."""
    ym = re.search(r"(20\d{2})", source_file)
    if not ym:
        return None, None
    year = int(ym.group(1))
    hay = os.path.basename(source_file) + " " + (season or "") + " " + head[:60]
    for kw, off, label in SPECIAL_SERVICES:
        if kw in hay:
            d = easter(year) + datetime.timedelta(days=off)
            return d.isoformat(), label
    return None, None

RAW = r"c:/tmp/cz_bulletins/raw.jsonl"
OUT = os.path.abspath(r"public/content/chengzhong-bulletins")
os.makedirs(OUT, exist_ok=True)

# ---- role labels ----
ROLE_KEYS = ["主禮","主理","證道","講員","主席","司會","司獻","司奉","招待","司琴","領詩","領唱","領會",
             "讀經","獻詩","獻花","獻刊","愛筵庶務","愛筵","值週","值星","兒童主日學",
             "青少年主日學","襄禮","聖餐襄禮","傳道","領餐"]
ROLE_ALT = sorted(set(k for k in ROLE_KEYS if "/" not in k), key=len, reverse=True)
_R = "|".join(map(re.escape, ROLE_ALT))
# label only (value in next cell):  主禮/證道：
LABEL_ONLY = re.compile(r"^\s*(" + _R + r")\s*(?:[／/]\s*(" + _R + r"))?\s*[：:]\s*$")
# label with inline value:  主禮/證道：龐君華牧師
LABEL_VAL = re.compile(r"^\s*(" + _R + r")\s*(?:[／/]\s*(" + _R + r"))?\s*[：:]\s*(\S[^：:｜|\n]{0,23})\s*$")

COLOR_PAT = re.compile(r"(白|紫|綠|紅|藍|金|黑)色")
SEASON_KW = re.compile(r"(主日|節|期|齋|復活|聖誕|降臨|將臨|顯現|受難|五旬|聖靈|三一|受洗|變容|棕枝|預苦|"
                       r"基督君王|平安|感恩|母親|父親|教會|宗教改革|立約|追思|普世|聖徒)")
DATE_TXT = re.compile(r"主後[^\n]{2,40}?[日]")
HYMN_PAT = re.compile(r"(新普天頌讚|普天頌讚|世紀頌讚|新普頌|頌主新歌|聖徒詩歌|青年聖歌|讚美詩)\s*第?\s*(\d{1,3})\s*首?\s*[「『]?([^」』\n（(]{0,30})")
SCRIP_BOOKS = r"(創世記|出埃及記|利未記|民數記|申命記|約書亞記|士師記|路得記|撒母耳記[上下]|列王紀[上下]|歷代志[上下]|以斯拉記|尼希米記|以斯帖記|約伯記|詩篇|箴言|傳道書|雅歌|以賽亞書|耶利米書|耶利米哀歌|哀歌|以西結書|但以理書|何西阿書|約珥書|阿摩司書|俄巴底亞書|約拿書|彌迦書|那鴻書|哈巴谷書|西番雅書|哈該書|撒迦利亞書|瑪拉基書|瑪垃基書|馬太福音|馬可福音|路加福音|約翰福音|使徒行傳|羅馬書|哥林多[前後]書|加拉太書|以弗所書|腓立比書|歌羅西書|帖撒羅尼迦[前後]書|提摩太[前後]書|提多書|腓利門書|希伯來書|雅各書|彼得[前後]書|約翰[壹貳參一二三]書|猶大書|啟示錄)"
_R = r"[-–—~～－]"  # hyphen / en/em dash / ascii+fullwidth tilde / fullwidth hyphen
SCRIP_PAT = re.compile(SCRIP_BOOKS + r"\s*\d+(?:[:：]\d+(?:" + _R + r"\d+(?:[:：]\d+)?)?(?:[,，、]\s*\d+(?:[:：]\d+)?(?:" + _R + r"\d+(?:[:：]\d+)?)?)*)?")
SCRIP_LABELS = ["經課一", "經課二", "經課三", "經課四", "讀經一", "讀經二", "讀經三",
                "啟應文", "福音書", "書信", "舊約", "新約", "默想經文", "證道經文", "講道經文"]
SCRIP_LABEL_RE = re.compile(r"(" + "|".join(SCRIP_LABELS) + r")")
SERMON_LABEL = re.compile(r"(?:講道題目|證道題目|講道主題|證道主題|信息主題|講題)\s*[：:]\s*[「『]?([^」』\n｜|]{2,40})")
SERMON_LINE = re.compile(r"^\s*(?:證|講|宣)\s*道(?:信息|主題)?(?![：:])\s+(.+)$")
NAME_TAIL_RE = re.compile(r"\s*[一-鿿]{2,5}(?:牧師|弟兄|姊妹|傳道|會督|長老|教授|博士|先生|女士|同工|傳道師)\s*$")
SERVICE_PAT = re.compile(r"(午堂|晚堂|早堂|朝陽|聯合|除夕|跨年|燭光|安息|追思|洗禮|聖餐主日)")

NAME_TAIL = ("牧師","會督","傳道","弟兄","姊妹","女士","先生","長老","執事","同工","醫師","教授","老師")

def is_personish(s):
    s = s.strip().strip("、,，。.")
    if not s or len(s) > 24:
        return False
    return any(t in s for t in NAME_TAIL) or (1 <= len(s) <= 4)

def _assign(roles, k1, k2, val):
    val = val.strip().strip("、,，。.／/ ")
    if not val or not is_personish(val):
        return
    for k in (k1, k2):
        if k and k not in roles:
            roles[k] = val

def _parse_cells(cells, roles):
    cells = [c.strip() for c in cells]
    i = 0
    while i < len(cells):
        c = cells[i]
        m = LABEL_VAL.match(c)
        if m:
            _assign(roles, m.group(1), m.group(2), m.group(3)); i += 1; continue
        m = LABEL_ONLY.match(c)
        if m:
            val = ""
            j = i + 1
            while j < len(cells) and not cells[j]:
                j += 1
            if j < len(cells):
                val = cells[j]
            _assign(roles, m.group(1), m.group(2), val)
            i = j + 1; continue
        i += 1

def _is_worship_table(t):
    flat = " ".join(c for row in t for c in row)
    return (("司會" in flat or "司琴" in flat) and
            any(k in flat for k in ("主禮", "主理", "證道", "講員")) and
            "目前狀況" not in flat and "聚會名稱" not in flat and "需要人數" not in flat)

def parse_roles(paras, tables):
    roles = collections.OrderedDict()
    # 1) worship-roles table(s) — cell-pair aware
    for t in tables:
        if _is_worship_table(t):
            _parse_cells([c for row in t for c in row], roles)
    # 2) inline paragraphs (eras that list roles as text lines)
    _parse_cells(paras[:28], roles)
    return roles

def find_season(paras):
    for p in paras[:8]:
        if any(x in p for x in ("中華基督教", "衛理公會", "城中牧區", "城中教會")):
            continue
        if DATE_TXT.search(p):
            continue
        if len(p) <= 30 and SEASON_KW.search(p):
            return re.sub(r"(崇拜)?程序(單|表)?$", "", p).strip() or p
    return None

def find_color(paras):
    for p in paras[:25]:
        if ("象徵" in p or "禮儀" in p or "用於" in p) and COLOR_PAT.search(p):
            return COLOR_PAT.search(p).group(1)
    return None

def find_service(paras, file):
    head = "\n".join(paras[:6]) + " " + file
    m = SERVICE_PAT.search(head)
    if m:
        return m.group(1)
    return "主日崇拜"

def _clean_title(cand):
    cand = re.sub(r"[.…・·．•　]+", " ", cand)
    # cut at a following field label (講道：/證道：/司會：…) or stray colon
    cand = re.split(r"(?:講道|證道|信息|宣講|司會|司琴|讀經|主理|主禮|整理|司獻)\s*[：:]", cand)[0]
    cand = cand.split("：")[0].split(":")[0]
    cand = re.sub(r"\s+", " ", cand).strip(" 「」『』─-—　")
    cand = NAME_TAIL_RE.sub("", cand).strip(" .…「」『』─-—　")
    return cand

def find_sermon(paras, roles):
    # priority 1: explicit 證道主題/講道題目 label
    for p in paras:
        m = SERMON_LABEL.search(p)
        if m:
            cand = _clean_title(m.group(1))
            if 2 <= len(cand) <= 40 and not is_personish(cand):
                return cand
    # priority 2: worship-order line "證道 <title> <preacher>"
    for p in paras:
        m = SERMON_LINE.match(p)
        if m:
            cand = _clean_title(m.group(1))
            if 2 <= len(cand) <= 40 and not is_personish(cand) and "：" not in cand:
                return cand
    return None

def find_scriptures(paras):
    """Return (refs[list of str], labeled[list of {label, ref}]). refs = website display;
    labeled = DB scripture_ref source (經課一：X / 啟應文：Y / 福音書：Z)."""
    refs, seen, labeled, lseen = [], set(), [], set()
    for i, p in enumerate(paras):
        if not any(k in p for k in ("經課", "讀經", "啟應", "福音", "書信", "舊約", "新約", "默想", "證道經文", "講道經文")):
            continue
        lm = SCRIP_LABEL_RE.search(p)
        if lm:
            sm = SCRIP_PAT.search(p)
            if not sm:  # label and ref split across lines — look ahead one para
                nxt = paras[i + 1] if i + 1 < len(paras) else ""
                if not SCRIP_LABEL_RE.search(nxt):
                    sm = SCRIP_PAT.search(nxt)
            if sm:
                label = lm.group(1)
                if label not in lseen:
                    lseen.add(label); labeled.append({"label": label, "ref": sm.group(0).replace("：", ":")})
        for m in SCRIP_PAT.finditer(p):
            ref = m.group(0).replace("：", ":")
            if ref not in seen:
                seen.add(ref); refs.append(ref)
    # DB scripture_ref: prefer the precise labeled lectionary set (>=2 slots);
    # only fall back to the greedy unlabeled list when no real labeled set exists.
    if len(labeled) >= 2:
        ref_str = "；".join(f"{x['label']}：{x['ref']}" for x in labeled[:8]); is_labeled = True
    elif labeled and len(labeled) >= len(refs):
        ref_str = "；".join(f"{x['label']}：{x['ref']}" for x in labeled); is_labeled = True
    else:
        ref_str = "；".join(refs[:8]); is_labeled = False
    return refs[:12], ref_str, is_labeled

def _clean_hymn_title(t):
    t = t.strip(" 「」『』（）()　.…·•-").strip()
    # drop liturgical-rubric pollution that leaks past the hymn number
    if re.search(r"……|\.\.\.|眾立|眾坐|同頌|請參|司會|司琴|普頌\s*\d|週報第", t) or len(t) < 2:
        return ""
    return t

def find_hymns(paras):
    out = []
    for p in paras:
        for m in HYMN_PAT.finditer(p):
            book, num, title = m.group(1), m.group(2), _clean_hymn_title(m.group(3))
            out.append({"book": book, "no": num, "title": title})
    # dedupe
    seen = set(); ded = []
    for h in out:
        k = (h["book"], h["no"])
        if k not in seen:
            seen.add(k); ded.append(h)
    return ded[:12]

def parse_record(rec):
    paras = rec.get("paras") or []
    tables = rec.get("tables") or []
    roles = parse_roles(paras, tables)
    season = find_season(paras)
    color = find_color(paras)
    service = find_service(paras, rec["file"])
    sermon = find_sermon(paras, roles)
    scriptures, scripture_ref, scripture_labeled = find_scriptures(paras)
    hymns = find_hymns(paras)
    dt = None
    for p in paras[:6]:
        m = DATE_TXT.search(p)
        if m:
            dt = m.group(0).strip(); break
    preacher = roles.get("證道") or roles.get("講員") or roles.get("主禮")
    presider = roles.get("主禮") or roles.get("主理")
    # resolve missing date: loose YY-M-D filename, then Easter-relative special service
    date = rec.get("date")
    if date:
        date = date.translate(str.maketrans("０１２３４５６７８９", "0123456789"))
    if not date:
        m = LOOSE_DATE.search(rec["fname"])
        if m:
            yy, mm, dd = m.groups()
            date = f"20{yy}-{int(mm):02d}-{int(dd):02d}"
        else:
            sd, slabel = resolve_special_date(rec["file"], season, "\n".join(paras[:4]))
            if sd:
                date, service = sd, slabel
    return {
        "date": date,
        "service": service,
        "season": season,
        "date_text": dt,
        "color": color,
        "preacher": preacher,
        "presider": presider,
        "sermon_title": sermon,
        "roles": roles,
        "scriptures": scriptures,
        "scripture_ref": scripture_ref,
        "scripture_labeled": scripture_labeled,
        "hymns": hymns,
        "full_text": "\n".join(paras),
        "nchars": rec.get("nchars", 0),
        "source_file": rec["file"],
        "ext": rec.get("ext"),
    }

def main():
    rows = [json.loads(l) for l in open(RAW, encoding="utf-8") if l.strip()]
    rows = [r for r in rows if not r.get("error")]
    parsed = [parse_record(r) for r in rows]
    # dedupe by (date, service): keep richest (most nchars)
    best = {}
    nodate = []
    for p in parsed:
        if not p["date"]:
            nodate.append(p); continue
        key = (p["date"], p["service"])
        if key not in best or p["nchars"] > best[key]["nchars"]:
            best[key] = p
    records = sorted(best.values(), key=lambda x: (x["date"], x["service"]))
    print(f"raw={len(rows)} parsed={len(parsed)} deduped={len(records)} nodate={len(nodate)}")
    # coverage stats
    def cov(field):
        return sum(1 for r in records if r.get(field))
    n = len(records)
    for f in ("season","color","preacher","presider","sermon_title"):
        print(f"  {f:14} {cov(f)}/{n}  ({100*cov(f)//max(n,1)}%)")
    print("  scriptures>0", sum(1 for r in records if r['scriptures']), " hymns>0", sum(1 for r in records if r['hymns']))
    # write index (light) + per-year detail folders
    index = []
    for r in records:
        slug = r["date"] + ("" if r["service"] in ("主日崇拜",) else "_" + r["service"])
        year = r["date"][:4]
        ydir = os.path.join(OUT, year); os.makedirs(ydir, exist_ok=True)
        index.append({k: r[k] for k in ("date","service","season","color","preacher","presider","sermon_title")}
                     | {"slug": slug, "year": year, "n_scrip": len(r["scriptures"]), "n_hymn": len(r["hymns"])})
        json.dump(r, open(os.path.join(ydir, slug + ".json"), "w", encoding="utf-8"), ensure_ascii=False)
    index.sort(key=lambda x: (x["date"], x["service"]))
    years = sorted({x["year"] for x in index})
    meta = {"total": len(index), "years": years,
            "preachers": sorted({x["preacher"] for x in index if x["preacher"]}),
            "coverage": {f: sum(1 for x in index if x.get(f)) for f in ("season","preacher","sermon_title","color")}}
    json.dump({"meta": meta, "items": index}, open(os.path.join(OUT, "index.json"), "w", encoding="utf-8"), ensure_ascii=False)
    json.dump([p["source_file"] for p in nodate], open(os.path.join(OUT, "_nodate.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("wrote", os.path.join(OUT, "index.json"), "years=", years)

if __name__ == "__main__":
    main()
