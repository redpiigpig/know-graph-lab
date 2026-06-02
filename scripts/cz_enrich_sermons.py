# -*- coding: utf-8 -*-
"""用城中週報資料 enrich pong_sermons（龐牧師講道週次）。
Fill-if-empty 政策：只填 DB 空欄，不覆蓋既有人工/Phase-4 資料。
欄位：title / scripture_ref / worship_leader(司會) / scripture_reader(讀經) /
      choir(獻詩) / officiant(主禮) / worship_team(其餘角色) / worship_songs(詩歌)。
用法： python scripts/cz_enrich_sermons.py            (dry-run)
       python scripts/cz_enrich_sermons.py --apply
"""
import os, sys, re, json, requests, collections

APPLY = "--apply" in sys.argv
with open(".env", encoding="utf-8") as f:
    for line in f:
        if line.strip() and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1); os.environ[k.strip()] = v.strip()
SB = os.environ["SUPABASE_URL"].rstrip("/") + "/rest/v1"
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

GENERIC_TITLE = {"", "主日崇拜", "主日證道", "主日禮拜", "主日聚會", None}
EXTRA_ROLES = ["主理", "司琴", "司獻", "招待", "領唱", "領詩", "領會", "獻花", "獻刊",
               "兒童主日學", "青少年主日學", "愛筵庶務", "值週", "襄禮"]

def fmt_scrip(refs):
    out = []
    for r in refs:
        out.append(re.sub(r"([一-鿿])(\d)", r"\1 \2", r).replace("：", ":"))
    return "；".join(out)

def fmt_hymns(hymns):
    out = []
    for h in hymns:
        s = f"{h['book']} {h['no']}首"
        if h.get("title"):
            s += f"「{h['title']}」"
        out.append(s)
    return out

def empty(v):
    if v is None:
        return True
    if isinstance(v, str):
        return not v.strip()
    if isinstance(v, (list, dict)):
        return len(v) == 0
    return False

def main():
    idx = json.load(open("public/content/chengzhong-bulletins/index.json", encoding="utf-8"))["items"]
    sermons = json.load(open("c:/tmp/cz_bulletins/pong_sermons_all.json", encoding="utf-8"))
    sb_by_date = {s["sermon_date"]: s for s in sermons}
    # 龐 bulletins, dedupe by date preferring 主日崇拜
    pang = {}
    for b in idx:
        if b.get("preacher") and "龐" in b["preacher"]:
            d = b["date"]
            if d not in pang or b["service"] == "主日崇拜":
                pang[d] = b

    field_fills = collections.Counter()
    field_skips = collections.Counter()
    n_updated = 0
    changelog = []
    for d, b in sorted(pang.items()):
        s = sb_by_date.get(d)
        if s is None:
            continue  # no row -> belongs to the "no transcript" report, not enrichment
        det = json.load(open(f"public/content/chengzhong-bulletins/{b['year']}/{b['slug']}.json", encoding="utf-8"))
        roles = det.get("roles") or {}
        payload, filled = {}, []

        def put(col, val):
            if val and empty(s.get(col)):
                payload[col] = val; filled.append(col); field_fills[col] += 1
            elif val and not empty(s.get(col)):
                field_skips[col] += 1

        if det.get("sermon_title") and s.get("title") in GENERIC_TITLE:
            payload["title"] = det["sermon_title"]; filled.append("title"); field_fills["title"] += 1
        elif det.get("sermon_title"):
            field_skips["title"] += 1
        if det.get("scriptures"):
            put("scripture_ref", fmt_scrip(det["scriptures"]))
        put("worship_leader", roles.get("司會"))
        put("scripture_reader", roles.get("讀經"))
        put("choir", roles.get("獻詩"))
        put("officiant", roles.get("主禮") or roles.get("主理"))
        wt = {k: roles[k] for k in EXTRA_ROLES if roles.get(k)}
        if wt and empty(s.get("worship_team")):
            payload["worship_team"] = json.dumps(wt, ensure_ascii=False); filled.append("worship_team"); field_fills["worship_team"] += 1
        elif wt:
            field_skips["worship_team"] += 1
        songs = fmt_hymns(det.get("hymns") or [])
        if songs and empty(s.get("worship_songs")):
            payload["worship_songs"] = songs; filled.append("worship_songs"); field_fills["worship_songs"] += 1
        elif songs:
            field_skips["worship_songs"] += 1

        if not payload:
            continue
        n_updated += 1
        changelog.append({"date": d, "id": s["id"], "filled": filled})
        if APPLY:
            r = requests.patch(f"{SB}/pong_sermons?id=eq.{s['id']}", headers={**H, "Prefer": "return=minimal"}, json=payload)
            if r.status_code >= 300:
                print("  ! PATCH fail", d, r.status_code, r.text[:120])

    print(f"=== {'APPLY' if APPLY else 'DRY-RUN'} ===")
    print(f"龐 週次有DB列: {sum(1 for d in pang if d in sb_by_date)} | 會更新: {n_updated}")
    print("\n各欄位填入數（fill-if-empty）:")
    for c in ["title", "scripture_ref", "worship_leader", "scripture_reader", "choir", "officiant", "worship_team", "worship_songs"]:
        print(f"  {c:18} 填 {field_fills[c]:3}  (已有跳過 {field_skips[c]})")
    json.dump(changelog, open("c:/tmp/cz_bulletins/enrich_changelog.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\nchangelog -> c:/tmp/cz_bulletins/enrich_changelog.json ({len(changelog)} rows)")
    if not APPLY:
        print("（dry-run，未寫入。加 --apply 執行）")

if __name__ == "__main__":
    main()
