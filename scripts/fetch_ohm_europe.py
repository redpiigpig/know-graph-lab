#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
從 OpenHistoricalMap Overpass API 抓歐洲帝國／王國的真實歷史邊界。

每個 OHM relation 含 type=boundary, admin_level=2 (國家層級), start_date, end_date,
以及多個 way members (role=outer/inner)。本腳本把 OSM relation 拼成 GeoJSON
Polygon/MultiPolygon，輸出 public/maps/ohm-polygons.geojson。

執行：
  PYTHONIOENCODING=utf-8 python scripts/fetch_ohm_europe.py
  PYTHONIOENCODING=utf-8 python scripts/fetch_ohm_europe.py --only "Imperium Romanum"
  PYTHONIOENCODING=utf-8 python scripts/fetch_ohm_europe.py --resume  # skip 已抓的

每個 relation 抓一個 query，避免單 query 超大。Overpass 每分鐘約限 2-3 query；
腳本內建 sleep 3 秒。約 30 個帝國 × 平均 15 polygons = 450 polygons，跑約 5 分鐘。
"""
import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = ROOT / "public/maps/ohm-polygons.geojson"
CACHE_DIR = Path("C:/tmp/ohm-cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# (OHM 原生名稱, 我的 polygon_name 對齊, 中文)
# OHM 名稱來自 admin_level=2 + 歐洲 bbox 掃描結果
EMPIRES = [
    # --- 古典／晚古 ---
    ("Imperium Romanum",            "Roman Empire",                       "羅馬"),
    ("Imperium Romanum Orientale",  "Byzantine Empire",                   "拜占庭"),
    ("Imperium Romanum Occidentale","Western Roman Empire",               "西羅馬"),
    ("Regnum Gothorum",             "Visigothic Kingdom",                 "西哥德王國"),
    ("Regnum Langobardorum",        "Lombard Kingdom",                    "倫巴底王國"),
    # --- 中世紀 ---
    ("Regnum Francorum",            "Frankish Kingdom",                   "法蘭克王國"),
    ("Sacrum Imperium Romanum",     "Holy Roman Empire",                  "神聖羅馬"),
    ("Status Ecclesiasticus",       "Papal States",                       "教皇國"),
    ("Iruñeko Erresuma",            "Kingdom of Navarre",                 "納瓦拉王國"),
    ("Reino de León",               "Kingdom of León",                    "萊昂王國"),
    ("Corona Castellae",            "Crown of Castile",                   "卡斯提爾"),
    ("Aragonum et Catalonie",       "Crown of Aragon",                    "阿拉貢"),
    ("Regnum Siciliae",             "Kingdom of Sicily",                  "西西里王國"),
    ("Konungariket Sverige",        "Kingdom of Sweden",                  "瑞典王國"),
    ("Republica de Venezia",        "Venetian Republic",                  "威尼斯共和國"),
    ("Magyar Királyság",            "Kingdom of Hungary",                 "匈牙利王國"),
    # --- 近世 ---
    ("España",                      "Spain",                              "西班牙"),
    ("Royaume de France",           "Kingdom of France",                  "法蘭西王國"),
    ("Russkoye tsarstvo",           "Russian Tsardom",                    "俄羅斯沙皇國"),
    ("Русское царство",             "Russian Tsardom",                    "俄羅斯沙皇國"),
    ("Rzeczpospolita Obojga Narodów","Polish-Lithuanian Commonwealth",    "波蘭立陶宛聯邦"),
    ("Danmark-Norge",               "Denmark-Norway",                     "丹麥-挪威"),
    # --- 19-20 世紀 ---
    ("Российская империя",          "Russian Empire",                     "俄羅斯帝國"),
    ("République Française",        "French Republic",                    "法蘭西共和國"),
    ("Kaiserthum Oesterreich",      "Austrian Empire",                    "奧地利帝國"),
    ("Königreich Preußen",          "Kingdom of Prussia",                 "普魯士王國"),
    ("Deutsches Reich",             "German Empire",                      "德意志帝國"),
    ("Italia",                      "Kingdom of Italy",                   "義大利王國"),
    ("Sverige",                     "Sweden",                             "瑞典"),
    ("Danmark",                     "Denmark",                            "丹麥"),
    ("Polska",                      "Poland",                             "波蘭"),
    ("Československá republika",    "Czechoslovakia",                     "捷克斯洛伐克"),
    ("Koninkrijk der Nederlanden",  "Kingdom of the Netherlands",         "荷蘭王國"),
    ("Soviet Union",                "Soviet Union",                       "蘇聯"),
    # --- 鄂圖曼（含部分歐洲領土）---
    ("دولتْ علیّه عثمانیّه",         "Ottoman Empire",                     "鄂圖曼"),
]

OVERPASS_URL = "https://overpass-api.openhistoricalmap.org/api/interpreter"


def overpass_query(query: str, retries: int = 3) -> dict:
    """POST query to OHM Overpass; retry on transient failure."""
    data = urllib.parse.urlencode({"data": query}).encode("utf-8")
    for attempt in range(retries):
        try:
            req = urllib.request.Request(OVERPASS_URL, data=data, method="POST",
                                         headers={"User-Agent": "know-graph-lab/1.0"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.load(resp)
        except (urllib.error.URLError, TimeoutError) as e:
            wait = 5 * (attempt + 1)
            print(f"  ⚠ Overpass error: {e}; retry in {wait}s")
            time.sleep(wait)
    raise RuntimeError("Overpass exhausted retries")


def fetch_empire_relations(ohm_name: str) -> list:
    """Fetch all admin_level=2 relations matching this OHM name with full geometry."""
    q = (
        '[out:json][timeout:120];'
        f'relation["type"="boundary"]["admin_level"="2"]["name"={json.dumps(ohm_name, ensure_ascii=False)}];'
        'out geom;'
    )
    cache = CACHE_DIR / f"{ohm_name.replace('/', '_')}.json"
    if cache.exists():
        try:
            with open(cache, "r", encoding="utf-8") as f:
                return json.load(f).get("elements", [])
        except Exception:
            pass
    print(f"  → fetching {ohm_name}…")
    data = overpass_query(q)
    with open(cache, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    return data.get("elements", [])


def stitch_ways_to_rings(way_geoms: list) -> list:
    """OSM relation way members → linked rings.

    Each way_geoms element is a list of {lat, lon} dicts.
    Two ways stitch if endpoint nodes match exactly.
    """
    # Convert to (lon, lat) coord lists
    segments = [[(g["lon"], g["lat"]) for g in geom] for geom in way_geoms if geom]
    rings = []
    remaining = list(segments)
    while remaining:
        cur = list(remaining.pop(0))
        if cur[0] == cur[-1]:
            rings.append(cur)
            continue
        changed = True
        while changed and cur[0] != cur[-1]:
            changed = False
            for i, seg in enumerate(remaining):
                if not seg:
                    continue
                if seg[0] == cur[-1]:
                    cur.extend(seg[1:]); remaining.pop(i); changed = True; break
                if seg[-1] == cur[-1]:
                    cur.extend(reversed(seg[:-1])); remaining.pop(i); changed = True; break
                if seg[0] == cur[0]:
                    cur = list(reversed(seg)) + cur[1:]; remaining.pop(i); changed = True; break
                if seg[-1] == cur[0]:
                    cur = seg[:-1] + cur; remaining.pop(i); changed = True; break
        if cur[0] != cur[-1]:
            # 無法閉合 — 強制閉合
            cur.append(cur[0])
        rings.append(cur)
    return rings


def signed_area(ring: list) -> float:
    """Shoelace area; >0 = CCW in math (y-up), <0 = CW."""
    return 0.5 * sum((ring[i+1][0] - ring[i][0]) * (ring[i+1][1] + ring[i][1])
                     for i in range(len(ring) - 1))


def _point_line_dist_sq(p, a, b):
    """Squared perpendicular distance from p to segment a-b."""
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return (px - ax) ** 2 + (py - ay) ** 2
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    qx, qy = ax + t * dx, ay + t * dy
    return (px - qx) ** 2 + (py - qy) ** 2


def simplify_ring(ring: list, epsilon: float) -> list:
    """Douglas-Peucker simplification (iterative). epsilon in degrees."""
    if len(ring) <= 4:
        return ring
    eps2 = epsilon * epsilon
    n = len(ring)
    keep = [False] * n
    keep[0] = keep[n - 1] = True
    stack = [(0, n - 1)]
    while stack:
        i, j = stack.pop()
        if j <= i + 1:
            continue
        max_d, max_k = 0.0, -1
        for k in range(i + 1, j):
            d = _point_line_dist_sq(ring[k], ring[i], ring[j])
            if d > max_d:
                max_d, max_k = d, k
        if max_d > eps2 and max_k > 0:
            keep[max_k] = True
            stack.append((i, max_k))
            stack.append((max_k, j))
    simplified = [ring[k] for k in range(n) if keep[k]]
    if simplified[0] != simplified[-1]:
        simplified.append(simplified[0])
    return simplified if len(simplified) >= 4 else ring


def ensure_cw(ring: list) -> list:
    """d3-geo 球面慣例：地理座標 CW = 內部小區域。確保所有 outer ring 是 CW。"""
    a = signed_area(ring)
    # In y-up math: a > 0 means CCW. d3-geo wants CW (math), so flip if a > 0.
    return ring if a > 0 else list(reversed(ring))


def parse_year(date_str: str) -> int | None:
    """OHM dates: '0395' / '-0027' / '1721-09-10' → year int."""
    if not date_str or date_str == "?":
        return None
    # Strip leading negative for BC
    neg = date_str.startswith("-")
    if neg:
        date_str = date_str[1:]
    parts = date_str.split("-")
    try:
        y = int(parts[0])
    except ValueError:
        return None
    return -y if neg else y


def relation_to_features(rel: dict, polygon_name: str, name_zh: str) -> list:
    """Convert one OSM boundary relation → GeoJSON Feature(s)."""
    tags = rel.get("tags", {})
    ohm_name = tags.get("name", "?")
    yf = parse_year(tags.get("start_date"))
    yt = parse_year(tags.get("end_date"))
    if yf is None:
        return []
    if yt is None:
        yt = 9999

    outer_ways = [m.get("geometry", []) for m in rel.get("members", [])
                  if m.get("type") == "way" and m.get("role") in ("outer", "")]
    inner_ways = [m.get("geometry", []) for m in rel.get("members", [])
                  if m.get("type") == "way" and m.get("role") == "inner"]
    if not outer_ways:
        return []

    outer_rings = stitch_ways_to_rings(outer_ways)
    inner_rings = stitch_ways_to_rings(inner_ways) if inner_ways else []

    # Drop tiny rings (numerical noise / failed stitching <3 vertices)
    outer_rings = [r for r in outer_rings if len(r) >= 4]
    if not outer_rings:
        return []

    # Simplify: Douglas-Peucker at ~0.1° tolerance (~11 km equator).
    # 帝國疆域層級夠細緻；不需要海岸線細節
    EPSILON = 0.1
    outer_rings = [simplify_ring(r, EPSILON) for r in outer_rings]
    inner_rings = [simplify_ring(r, EPSILON) for r in inner_rings]

    # Drop tiny rings (小島／拼接殘片，帝國尺度不可見）— abs area < 0.5 sq-deg
    outer_rings = [r for r in outer_rings if abs(signed_area(r)) > 0.5]
    inner_rings = [r for r in inner_rings if abs(signed_area(r)) > 0.5]
    if not outer_rings:
        return []

    # Apply CW winding for d3-geo spherical
    outer_rings = [ensure_cw(r) for r in outer_rings]
    # Inner (holes) should be CCW per d3-geo
    inner_rings = [list(reversed(r)) if signed_area(r) > 0 else r for r in inner_rings]
    inner_rings = [r for r in inner_rings if len(r) >= 4]

    # Single outer = Polygon, multi = MultiPolygon (one ring per polygon, holes inside the biggest)
    if len(outer_rings) == 1:
        coords = [outer_rings[0]] + inner_rings
        geom = {"type": "Polygon", "coordinates": coords}
    else:
        # Heuristic: put all inner rings inside the FIRST outer (good enough for most)
        polys = []
        for i, outer in enumerate(outer_rings):
            ring_polys = [outer]
            if i == 0:
                ring_polys.extend(inner_rings)
            polys.append(ring_polys)
        geom = {"type": "MultiPolygon", "coordinates": polys}

    return [{
        "type": "Feature",
        "geometry": geom,
        "properties": {
            "name": polygon_name,
            "name_zh": name_zh,
            "name_ohm": ohm_name,
            "year_from": yf,
            "year_to": yt,
            "source": "OHM",
            "ohm_id": rel.get("id"),
        },
    }]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--only", help="只跑指定 OHM 名稱（debug）")
    p.add_argument("--no-cache", action="store_true", help="忽略快取重新抓")
    args = p.parse_args()

    if args.no_cache:
        for f in CACHE_DIR.glob("*.json"):
            f.unlink()

    all_features = []
    for ohm_name, my_name, name_zh in EMPIRES:
        if args.only and args.only != ohm_name:
            continue
        try:
            rels = fetch_empire_relations(ohm_name)
            empire_features = []
            for r in rels:
                empire_features.extend(relation_to_features(r, my_name, name_zh))
            print(f"  ✅ {ohm_name:40s} → {my_name:40s} {len(rels):3d} relations → {len(empire_features):3d} features")
            all_features.extend(empire_features)
            time.sleep(3)
        except Exception as e:
            print(f"  ❌ {ohm_name}: {e}")

    out = {"type": "FeatureCollection", "features": all_features}
    OUT_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=None), encoding="utf-8")
    print(f"\n✅ {len(all_features)} polygons → {OUT_PATH}")
    print(f"   檔案大小：{OUT_PATH.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
