#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
從 CHGIS V6 prefecture polygons 建中國朝代邊界 GeoJSON。

每個朝代選代表性 key years，將該年所有 active prefecture polygons
shapely.unary_union → 朝代總邊界。輸出 public/maps/chgis-polygons.geojson。

執行：
  python scripts/build_chgis_polygons.py
（需 shapely + pyshp）

CHGIS V6 Time Series Prefecture Polygons (Harvard Dataverse DOI:10.7910/DVN/I0Q7SM)
免費學術用，© Fairbank Center (Harvard) + 復旦歷史地理研究中心 2016。
"""
import json
import sys
from pathlib import Path

import shapefile
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
from shapely.geometry.base import BaseGeometry

ROOT = Path(__file__).resolve().parent.parent
SHP_PATH = Path("C:/tmp/chgis/v6_time_pref_pgn_utf_wgs84")
OUT_PATH = ROOT / "public/maps/chgis-polygons.geojson"

# 朝代 key years（事件級採樣，與我 fine city-hull 對齊但用 CHGIS 真實邊界）
# 格式: (dynasty_polygon_name, dynasty_zh, [(key_year, label_zh), ...])
DYNASTIES = [
    ("Qin", "秦", [
        (-221, "秦始皇統一"),
        (-210, "秦始皇崩"),
    ]),
    ("Han Empire", "西漢", [
        (-200, "高祖建漢"),
        (-150, "文景之治"),
        (-110, "武帝極盛"),
        (-60, "西域都護府"),
        (-7, "哀帝末"),
    ]),
    ("Han", "東漢", [
        (50, "光武中興"),
        (100, "永元盛世"),
        (160, "桓帝末"),
        (200, "官渡"),
    ]),
    ("Cao Wei", "曹魏", [(240, "三國鼎立")]),
    ("Shu Han", "蜀漢", [(240, "蜀漢")]),
    ("Eastern Wu", "東吳", [(240, "東吳")]),
    ("Jin", "西晉", [
        (270, "司馬炎"),
        (300, "八王之亂前"),
    ]),
    ("Jin", "東晉", [
        (350, "東晉中期"),
        (400, "東晉末"),
    ]),
    ("Toba Wei", "北魏", [(500, "孝文帝改革")]),
    ("Southern Dynasties (Liu Song)", "劉宋", [(450, "元嘉之治")]),
    ("Southern Dynasties (Liang)", "梁", [(540, "梁武帝")]),
    ("Sui Empire", "隋", [
        (590, "隋文帝統一"),
        (610, "煬帝極盛"),
    ]),
    ("Tang Empire", "唐", [
        (640, "貞觀之治"),
        (700, "武則天"),
        (750, "開元盛世"),
        (800, "中唐"),
        (860, "晚唐"),
    ]),
    ("Song Empire", "北宋", [
        (980, "太宗"),
        (1050, "仁宗"),
        (1120, "徽宗"),
    ]),
    ("Southern Song", "南宋", [
        (1150, "紹興和議"),
        (1250, "蒙古入侵前"),
    ]),
    ("Liao", "遼", [
        (1000, "聖宗極盛"),
        (1100, "天祚末"),
    ]),
    ("Jin Empire", "金", [
        (1150, "海陵王"),
        (1200, "章宗"),
    ]),
    ("Western Xia", "西夏", [
        (1100, "西夏中期"),
        (1200, "西夏末"),
    ]),
    ("Yuan Empire", "元", [
        (1280, "忽必烈"),
        (1330, "元朝中期"),
        (1360, "紅巾起義"),
    ]),
    ("Ming Chinese Empire", "明", [
        (1400, "永樂初"),
        (1500, "弘治中興"),
        (1600, "萬曆末"),
        (1640, "崇禎末"),
    ]),
    ("Manchu Empire", "清", [
        (1700, "康熙"),
        (1760, "乾隆極盛"),
        (1820, "嘉道之際"),
        (1880, "晚清"),
        (1911, "辛亥"),
    ]),
]


def signed_area(ring):
    return 0.5 * sum((ring[i+1][0] - ring[i][0]) * (ring[i+1][1] + ring[i][1])
                     for i in range(len(ring) - 1))


def _pld_sq(p, a, b):
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return (px - ax) ** 2 + (py - ay) ** 2
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    qx, qy = ax + t * dx, ay + t * dy
    return (px - qx) ** 2 + (py - qy) ** 2


def simplify_ring(ring, epsilon):
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
            d = _pld_sq(ring[k], ring[i], ring[j])
            if d > max_d:
                max_d, max_k = d, k
        if max_d > eps2 and max_k > 0:
            keep[max_k] = True
            stack.append((i, max_k))
            stack.append((max_k, j))
    out = [ring[k] for k in range(n) if keep[k]]
    if out[0] != out[-1]:
        out.append(out[0])
    return out if len(out) >= 4 else ring


def ensure_cw(ring):
    """d3-geo 球面：地理座標 CW = 內部小區域。我的 shoelace 正值 = CW。"""
    a = signed_area(ring)
    return ring if a > 0 else list(reversed(ring))


def shapely_to_geojson_geom(geom: BaseGeometry, epsilon=0.1, min_ring_area=0.05):
    """shapely Polygon/MultiPolygon → GeoJSON geometry with DP simplify + CW winding."""
    g = geom.simplify(epsilon, preserve_topology=True)
    raw = mapping(g)

    def process_poly(poly_coords):
        out_rings = []
        for i, ring in enumerate(poly_coords):
            ring = list(ring)
            # Drop tiny rings (numerical noise)
            if abs(signed_area(ring)) < min_ring_area:
                continue
            if i == 0:
                # Outer ring: CW (positive area in my shoelace)
                ring = ensure_cw(ring)
            else:
                # Inner ring (hole): CCW (negative area)
                ring = ring if signed_area(ring) < 0 else list(reversed(ring))
            out_rings.append(ring)
        return out_rings if out_rings else None

    if raw['type'] == 'Polygon':
        rings = process_poly(raw['coordinates'])
        if not rings:
            return None
        return {'type': 'Polygon', 'coordinates': rings}
    elif raw['type'] == 'MultiPolygon':
        polys = []
        for p in raw['coordinates']:
            rings = process_poly(p)
            if rings:
                polys.append(rings)
        if not polys:
            return None
        return {'type': 'MultiPolygon', 'coordinates': polys}
    return None


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    print(f'Reading {SHP_PATH}...')
    sf = shapefile.Reader(str(SHP_PATH))
    records = sf.records()
    shapes = sf.shapes()
    print(f'  {len(records)} prefecture records')

    features = []
    for poly_name, dyn_zh, keyframes in DYNASTIES:
        sorted_kfs = sorted(keyframes)
        for idx, (year, label) in enumerate(sorted_kfs):
            # year_from = current key year; year_to = next key year - 1 (or end of dynasty)
            next_year = sorted_kfs[idx + 1][0] if idx + 1 < len(sorted_kfs) else year
            year_to = next_year - 1 if next_year > year else year

            # Collect active prefecture polygons at this year
            active_geoms = []
            for r, s in zip(records, shapes):
                by, ey = r['BEG_YR'], r['END_YR']
                if by <= year <= ey:
                    # 過濾「非政区国土」之類非實際領土的記錄
                    if r['TYPE_CH'] in ('非政区国土',):
                        continue
                    try:
                        gj = s.__geo_interface__
                        g = shape(gj)
                        # 修無效 geometry (self-intersection 等) 才能 union
                        if not g.is_valid:
                            g = g.buffer(0)
                        if g.is_valid and not g.is_empty:
                            active_geoms.append(g)
                    except Exception:
                        pass

            if not active_geoms:
                print(f'  [{poly_name}] year {year}: no active prefectures, skipping')
                continue

            try:
                merged = unary_union(active_geoms)
            except Exception as e:
                print(f'  [{poly_name}] year {year}: union failed: {e}')
                continue

            geom = shapely_to_geojson_geom(merged, epsilon=0.1, min_ring_area=0.05)
            if not geom:
                continue

            features.append({
                'type': 'Feature',
                'geometry': geom,
                'properties': {
                    'name': poly_name,
                    'name_zh': dyn_zh,
                    'name_event': label,
                    'year_from': year,
                    'year_to': year_to,
                    'source': 'CHGIS',
                    'prefecture_count': len(active_geoms),
                },
            })
            print(f'  ✅ {poly_name:35s} {year:5d}-{year_to:5d}  {len(active_geoms):3d} prefectures → {label}')

    out = {'type': 'FeatureCollection', 'features': features}
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, ensure_ascii=False), encoding='utf-8')
    size_kb = OUT_PATH.stat().st_size / 1024
    print(f'\n✅ {len(features)} dynasty-year polygons → {OUT_PATH}')
    print(f'   檔案大小：{size_kb:.1f} KB')


if __name__ == '__main__':
    main()
