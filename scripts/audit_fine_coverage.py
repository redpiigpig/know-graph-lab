#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
列出每 25 年哪些 polygons 仍是 fine (city-hull)，需要找真實邊界資料補。

渲染優先級：CHGIS > OHM > fine > source。
我們關心：active fine polygons 在那些年份壓不過 CHGIS/OHM／source。
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.stdout.reconfigure(encoding='utf-8')


def load(fp):
    with open(fp, 'r', encoding='utf-8') as f:
        return json.load(f)


source = load(ROOT / 'public/maps/historical-states.geojson')
fine = load(ROOT / 'public/maps/fine-polygons.geojson')
ohm = load(ROOT / 'public/maps/ohm-polygons.geojson')
chgis = load(ROOT / 'public/maps/chgis-polygons.geojson')
manual = load(ROOT / 'public/maps/manual-polygons.geojson')
overrides = load(ROOT / 'public/maps/polygon-year-overrides.json')['overrides']
cls = load(ROOT / 'public/maps/polygon-classifications.json')


def active_names_at(year, feats, with_overrides=False):
    out = set()
    for f in feats['features']:
        p = f['properties']
        name = p['name']
        if with_overrides and cls.get(name, {}).get('is_state') is False:
            continue
        yf = p['year_from']; yt = p['year_to']
        if with_overrides:
            ov = overrides.get(name, {})
            if 'min_year_from' in ov:
                yf = max(yf, ov['min_year_from'])
            if 'max_year_to' in ov:
                yt = min(yt, ov['max_year_to'])
        if yf <= year <= yt:
            out.add(name)
    return out


# Sample every 25 years from -500 to 1900
results = []  # (year, fine_only_names: list)
for year in range(-500, 1901, 25):
    chgis_names = active_names_at(year, chgis)
    ohm_names = active_names_at(year, ohm)
    manual_names = active_names_at(year, manual)
    fine_names = active_names_at(year, fine)
    source_names = active_names_at(year, source, with_overrides=True)
    # Fine polygons that aren't superseded by CHGIS / OHM / manual (same name)
    visible_fine = fine_names - chgis_names - ohm_names - manual_names
    if visible_fine:
        results.append((year, sorted(visible_fine)))

# Print compact
from collections import Counter
all_fine_persists = Counter()
print('Year-by-year city-hull (fine) polygons still rendering:')
print('=' * 100)
for year, names in results:
    for n in names:
        all_fine_persists[n] += 1
    if year % 100 == 0 or (year % 25 == 0 and len(names) <= 5):
        names_str = ', '.join(names[:8])
        if len(names) > 8:
            names_str += f' (+{len(names)-8})'
        print(f'  {year:5d}: {len(names):2d} polys  {names_str}')

print('\n=== Empires/polygons that are STILL city-hull (city-hull persists count across 25-year samples) ===')
for n, c in all_fine_persists.most_common(50):
    print(f'  {c:3d} samples  {n}')
