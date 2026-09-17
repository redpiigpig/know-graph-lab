"""把譜系資料層壓成一份給網站用的摘要：data/christian-genealogy/web-summary.json

    python scripts/genealogy_export_web.py

/works/christian-genealogy 的「譜系歸屬」分頁直接 import 這一份。
完整資料（逐段 sources、逐份 rationale）留在各原始檔，不進 client bundle。
"""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data/christian-genealogy"
OUT = D / "web-summary.json"

tree = json.loads((D / "traditions.json").read_text(encoding="utf-8"))
peri = json.loads((D / "nt-pericopes.json").read_text(encoding="utf-8"))["books"]
defs = json.loads((D / "nt-book-defaults.json").read_text(encoding="utf-8"))["books"]
bib = json.loads((D / "bibliography.json").read_text(encoding="utf-8"))["entries"]

names = {}
def walk(arr):
    for n in arr:
        names[n["code"]] = n["name"]
        for s in n.get("sub", []) or []:
            names[s["code"]] = s["name"]
            for t in s.get("sub", []) or []:
                names[t["code"]] = t["name"]
for k in ("layer1", "layer2", "layer3"):
    walk(tree[k])

# ── 逐節來源分佈 ──
tally, total = Counter(), 0
for f in sorted((D / "segments").glob("*.json")):
    code = f.stem
    vs = {f"{s['from'][0]}:{s['from'][1]}-{s['to'][0]}:{s['to'][1]}": s["verses"] for s in peri[code]}
    for ref, seg in json.loads(f.read_text(encoding="utf-8"))["segments"].items():
        v = vs[ref]
        total += v
        for src in seg["sources"]:
            tally[src] += v / len(seg["sources"])

# ── 代號樹 ──
def node(n):
    out = {"code": n["code"], "name": n["name"]}
    for k in ("etymon", "region", "keeps", "character", "authority", "note"):
        if n.get(k):
            out[k] = n[k]
    if n.get("sub"):
        out["sub"] = [{"code": s["code"], "name": s["name"], **({"note": s["note"]} if s.get("note") else {})}
                      for s in n["sub"]]
    return out

# ── 典外 ──
apoc = []
for fn, grp in (("apocryphal-gospels.json", "福音書"), ("nt-apocrypha.json", "非福音")):
    for slug, d in json.loads((D / fn).read_text(encoding="utf-8"))["documents"].items():
        apoc.append({
            "slug": slug, "title": d["title"], "group": grp, "nta": d.get("NTA", ""),
            "date": d["date"], "place": d.get("place", ""), "placeKind": d.get("place_kind", ""),
            "attributed": d.get("attributed", []), "actual": d.get("actual", []),
            "sections": d.get("sections", 0), "own": bool(d.get("own_judgment")),
            "beyond": bool(d.get("beyond_scope")), "rationale": d.get("rationale", ""),
            "support": d.get("support", []),
        })
apoc.sort(key=lambda x: (x["date"][0], x["date"][1]))

gc = json.loads((D / "gnostic-corpus.json").read_text(encoding="utf-8"))

payload = {
    "generatedBy": "scripts/genealogy_export_web.py",
    "counts": {
        "verses": total, "segments": sum(len(v) for v in peri.values()), "books": len(defs),
        "apocrypha": len(apoc), "gnostic": 287, "bibliography": len(bib),
    },
    "tree": {
        "layer1": [node(n) for n in tree["layer1"]],
        "layer2": [node(n) for n in tree["layer2"]],
        "layer3": [node(n) for n in tree["layer3"]],
        "cities": [{"key": c["key"], "name": c["name"], "from": c["from"],
                    "figures": len(c["figures"]), "note": c.get("note", "")}
                   for c in tree["city_traditions"]["cities"]],
        "inclusionRule": tree["meta"]["inclusion_rule"],
        "modelClaims": tree["meta"]["model_claims"],
    },
    "tally": [{"code": c, "name": names.get(c, "?"), "verses": round(v, 1),
               "pct": round(v / total * 100, 1)} for c, v in tally.most_common()],
    "books": [{"code": k, "name": b["name"], "editor": b["editor"], "editorName": b["editor_name"],
               "date": b["date"], "place": b["place"],
               "dateTraditional": b.get("date_traditional"), "placeTraditional": b.get("place_traditional"),
               "divergence": bool(b.get("dating_divergence")),
               "segments": len(peri[k]), "verses": sum(s["verses"] for s in peri[k]),
               "own": bool(b["own_judgment"]), "support": b["support"], "rationale": b["rationale"]}
              for k, b in defs.items()],
    "apocrypha": apoc,
    "gnosticRules": [{"key": k, "n": v.get("n"), "actual": v.get("actual", []),
                      "excluded": bool(v.get("excluded")),
                      "note": v.get("reason") or v.get("note", "")}
                     for k, v in gc["category_rules"].items()],
    "gnosticWarning": gc["meta"]["data_quality_warning"],
    "bibliography": [{"key": k, "ref": v["ref"], "provenance": v["provenance"], "supports": v["supports"]}
                     for k, v in bib.items()],
}

OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
size = len(OUT.read_text(encoding="utf-8"))
print(f"逐節 {total} 節 · 段落 {payload['counts']['segments']} · 典外 {len(apoc)} · 書目 {len(bib)}")
print(f"寫出 → {OUT.relative_to(ROOT)}（{size/1024:.0f} KB）")
