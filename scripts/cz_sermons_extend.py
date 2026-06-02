# -*- coding: utf-8 -*-
"""城中週報 → pong_sermons：(A) 以週報官方經課覆蓋既有 scripture_ref（差異才覆蓋）；
(B) 為「龐牧師講道但無 DB 列」週次建 metadata-only row（無逐字稿，is_published）。
寫前先把整張 pong_sermons 備份到 c:/tmp。用法：
   python scripts/cz_sermons_extend.py            (dry-run)
   python scripts/cz_sermons_extend.py --apply
"""
import os, sys, re, json, datetime, requests, collections

APPLY = "--apply" in sys.argv
with open(".env", encoding="utf-8") as f:
    for line in f:
        if line.strip() and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1); os.environ[k.strip()] = v.strip()
SB = os.environ["SUPABASE_URL"].rstrip("/") + "/rest/v1"
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

EXTRA_ROLES = ["主理", "司琴", "司獻", "招待", "領唱", "領詩", "領會", "獻花", "獻刊",
               "兒童主日學", "青少年主日學", "愛筵庶務", "值週", "襄禮"]
SPECIAL_KW = ("復活", "受難", "聖誕", "將臨", "顯現節主日", "立約", "聖靈降臨主日",
              "基督君王", "感恩", "堂慶", "追思", "登山變", "聖灰", "棕枝", "濯足", "升天")

def easter(y):
    a=y%19;b=y//100;c=y%100;d=b//4;e=b%4;f=(b+8)//25;g=(b-f+1)//3
    h=(19*a+b-d-g+15)%30;i=c//4;k=c%4;l=(32+2*e+2*i-h-k)%7;m=(a+11*h+22*l)//451
    mo=(h+l-7*m+114)//31;da=((h+l-7*m+114)%31)+1
    return datetime.date(y,mo,da)

def advent1(year):
    xmas = datetime.date(year, 12, 25); wd = xmas.weekday()
    days = (wd + 1) % 7 or 7
    return xmas - datetime.timedelta(days=days) - datetime.timedelta(weeks=3)

def church_year(d):
    return d.year if d >= advent1(d.year) else d.year - 1

def fmt_hymns(hymns):
    out = []
    for h in hymns:
        s = f"{h['book']} {h['no']}首" + (f"「{h['title']}」" if h.get("title") else "")
        out.append(s)
    return out

def preacher_for(date_iso, bulletin_preacher):
    # era map: pre-2019-05 牧師, 2019-05+ 會督
    return "龐君華牧師" if date_iso < "2019-05-01" else "龐君華會督"

SCRIP_BOOKS_RE = re.compile(r"(創世記|出埃及記|利未記|民數記|申命記|約書亞記|士師記|路得記|撒母耳記[上下]|列王紀[上下]|歷代志[上下]|以斯拉記|尼希米記|以斯帖記|約伯記|詩篇|箴言|傳道書|雅歌|以賽亞書|耶利米書|耶利米哀歌|哀歌|以西結書|但以理書|何西阿書|約珥書|阿摩司書|俄巴底亞書|約拿書|彌迦書|那鴻書|哈巴谷書|西番雅書|哈該書|撒迦利亞書|瑪拉基書|瑪垃基書|馬太福音|馬可福音|路加福音|約翰福音|使徒行傳|羅馬書|哥林多[前後]書|加拉太書|以弗所書|腓立比書|歌羅西書|帖撒羅尼迦[前後]書|提摩太[前後]書|提多書|腓利門書|希伯來書|雅各書|彼得[前後]書|約翰[壹貳參一二三]書|猶大書|啟示錄)")

def book_set(s):
    return set(SCRIP_BOOKS_RE.findall(s or ""))

def fetch_all():
    rows, off = [], 0
    while True:
        r = requests.get(f"{SB}/pong_sermons", headers={**H, "Range": f"{off}-{off+999}"},
                         params={"select": "*", "order": "sermon_date"})
        b = r.json()
        if not b: break
        rows += b; off += 1000
        if len(b) < 1000: break
    return rows

def main():
    idx = json.load(open("public/content/chengzhong-bulletins/index.json", encoding="utf-8"))["items"]
    pang = {}
    for b in idx:
        if b.get("preacher") and "龐" in b["preacher"]:
            d = b["date"]
            if d not in pang or b["service"] == "主日崇拜":
                pang[d] = b

    sermons = fetch_all()
    json.dump(sermons, open("c:/tmp/cz_bulletins/pong_sermons_backup.json", "w", encoding="utf-8"), ensure_ascii=False)
    sb = {s["sermon_date"]: s for s in sermons}
    print(f"備份 {len(sermons)} 列 -> c:/tmp/cz_bulletins/pong_sermons_backup.json")

    # ---------- Part A: REPORT ONLY — 經課真衝突（書卷層級雙向不符）。
    # 不自動覆蓋：週報抽取對舊年（全形標點/～範圍）不如 DB 轉錄完整，盲蓋會降級。
    # 只標出「DB 有別卷、週報也有別卷」的雙向矛盾（如 2024-06-09），供人工確認。----------
    conflicts = []
    for d, b in sorted(pang.items()):
        s = sb.get(d)
        if not s: continue
        det = json.load(open(f"public/content/chengzhong-bulletins/{b['year']}/{b['slug']}.json", encoding="utf-8"))
        if not det.get("scripture_labeled"):
            continue
        bb, db = book_set(det.get("scripture_ref")), book_set(s.get("scripture_ref"))
        only_b, only_db = bb - db, db - bb
        if only_b and only_db:  # genuine two-way disagreement
            conflicts.append({"date": d, "id": s["id"], "db": s.get("scripture_ref"),
                              "bulletin": det.get("scripture_ref")})
    print(f"\n[A] 經課『真衝突』候選（DB↔週報雙向書卷不符，需人工確認，不自動覆蓋）: {len(conflicts)} 筆")
    for c in conflicts[:6]:
        print(f"   {c['date']}\n     DB  : {c['db']}\n     週報: {c['bulletin']}")

    # ---------- Part B: create metadata-only rows for 龐 dates without a row ----------
    to_create = []
    for d, b in sorted(pang.items()):
        if d in sb: continue
        det = json.load(open(f"public/content/chengzhong-bulletins/{b['year']}/{b['slug']}.json", encoding="utf-8"))
        roles = det.get("roles") or {}
        dt = datetime.date.fromisoformat(d)
        season = det.get("season")
        is_special = (b["service"] not in ("主日崇拜", "午堂")) or (season and any(k in season for k in SPECIAL_KW))
        wt = {k: roles[k] for k in EXTRA_ROLES if roles.get(k)}
        row = {
            "id": int(d.replace("-", "")),
            "sermon_date": d,
            "title": det.get("sermon_title") or "主日崇拜",
            "preacher": preacher_for(d, det.get("preacher")),
            "officiant": roles.get("主禮") or roles.get("主理") or preacher_for(d, det.get("preacher")),
            "occasion": season,
            "liturgical_season": season,
            "scripture_ref": det.get("scripture_ref") or None,
            "worship_leader": roles.get("司會"),
            "scripture_reader": roles.get("讀經"),
            "choir": roles.get("獻詩"),
            "worship_team": json.dumps(wt, ensure_ascii=False) if wt else None,
            "worship_songs": fmt_hymns(det.get("hymns") or []) or None,
            "church_year": church_year(dt),
            "location": "衛理公會城中教會",
            "sermon_type": "特殊節日" if is_special else "主日講道",
            "has_recording": False,
            "is_published": True,
            "content": None,
            "sort_order": 0,
            "description": "（本場目前無逐字稿；資料取自城中教會主日崇拜週報）",
        }
        to_create.append(row)
    print(f"\n[B] 將新建 metadata-only row: {len(to_create)} 列")
    byyear = collections.Counter(r["sermon_date"][:4] for r in to_create)
    print("   by year:", dict(sorted(byyear.items())))
    if to_create:
        print("   sample:", json.dumps({k: to_create[0][k] for k in ("id","title","preacher","occasion","scripture_ref","sermon_type","church_year")}, ensure_ascii=False))

    if APPLY and to_create:
        for i in range(0, len(to_create), 100):
            batch = to_create[i:i+100]
            r = requests.post(f"{SB}/pong_sermons", headers={**H, "Prefer": "return=minimal"}, json=batch)
            if r.status_code >= 300:
                print("   ! INSERT batch fail", r.status_code, r.text[:200]); break
        print(f"   已新建 {len(to_create)} 列")

    json.dump({"scrip_conflicts": conflicts, "created": [r["id"] for r in to_create]},
              open("c:/tmp/cz_bulletins/extend_log.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if not APPLY:
        print("\n（dry-run，未寫入。加 --apply 執行）")

if __name__ == "__main__":
    main()
