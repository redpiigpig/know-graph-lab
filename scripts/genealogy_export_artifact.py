"""把 web-summary.json 壓成 artifact 用的 gdata.js（〈使徒軌跡歸屬表〉那一頁的資料檔）。

    python scripts/genealogy_export_web.py      # 先更新 web-summary.json
    python scripts/genealogy_export_artifact.py # 再產 gdata.js

為什麼要有這支：gdata.js 第一版是手工湊出來的，代號改號（O2–O8 往前挪成 O1–O7）之後
整張表就停在舊代號，而網站那邊早就對了——同一份成品放兩處、只更新一處的老毛病。
從今以後 artifact 那份一律由本腳本重生，不手改。

陣列的欄位順序要與 artifact HTML 裡的解構式對齊，改這裡就要一起改那邊：
    books   [code,name,ed,edn,date,place,div,tdate,tplace,segs,vs,own,sup,rat]
    apoc    [slug,title,grp,nta,d1,d2,place,pk,attr,act,secs,own,beyond,rat]
    tally   [code,name,verses,pct]
    gnostic [key,n,actual,excluded,note]
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data/christian-genealogy/web-summary.json"
OUT = ROOT / "data/christian-genealogy/gdata.js"

d = json.loads(SRC.read_text(encoding="utf-8"))

# tally 的 name 欄在 web-summary 裡是靠代號樹回查的，子碼之下的子碼（U5a／U5b）
# 查不到會留 "?"——那是舊 gdata.js 裡「U5a ?」的來源。這裡補上。
EXTRA_NAMES = {
    "U5a": "路加群體 · L 特有材料",
    "U5b": "路加群體 ·「我們」旅行來源",
}

payload = {
    "tally": [[t["code"], EXTRA_NAMES.get(t["code"], t["name"]), t["verses"], t["pct"]]
              for t in d["tally"]],
    "books": [[b["code"], b["name"], b["editor"], b["editorName"], b["date"], b["place"],
               b["divergence"], b.get("dateTraditional") or "", b.get("placeTraditional") or "",
               b["segments"], b["verses"], b["own"], b["support"], b["rationale"]]
              for b in d["books"]],
    "apoc": [[a["slug"], a["title"], a["group"], a["nta"], a["date"][0], a["date"][1],
              a["place"], a["placeKind"], a["attributed"], a["actual"], a["sections"],
              a["own"], a["beyond"], a["rationale"]]
             for a in d["apocrypha"]],
    "gnostic_rules": [[g["key"], g["n"], g["actual"], g["excluded"], g["note"]]
                      for g in d["gnosticRules"]],
    "counts": d["counts"],
}

OUT.write_text("window.G=" + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";",
               encoding="utf-8")
unnamed = [t[0] for t in payload["tally"] if t[1] == "?"]
print(f"tally {len(payload['tally'])} · 書卷 {len(payload['books'])} · "
      f"典外 {len(payload['apoc'])} · 諾斯底規則 {len(payload['gnostic_rules'])}")
print(f"🚨 仍無名稱的代號：{unnamed}" if unnamed else "代號名稱全數對得上")
print(f"寫出 → {OUT.relative_to(ROOT)}（{len(OUT.read_text(encoding='utf-8'))/1024:.0f} KB）")
