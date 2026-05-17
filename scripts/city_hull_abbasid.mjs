#!/usr/bin/env node
/**
 * Stage 1 POC — City Hull Polygon Generator
 *
 * SKILL.md proposes filling snapshot gaps with city-hull polygons:
 *   1. List cities under empire control at year Y
 *   2. Lookup each city's lat/lon
 *   3. Convex hull → GeoJSON Polygon
 *
 * This POC bypasses Gemini Vision and uses hard-coded city lists +
 * embedded lat/lon (no network), targeting Abbasid Caliphate at 6 years:
 *   750, 800, 900, 1000, 1100, 1200
 *
 * Output: public/maps/abbasid-fine-polygons.geojson
 *
 * Run: node scripts/city_hull_abbasid.mjs
 *
 * Accuracy: ±100 km. Limited to convex hull (no concavity around hostile zones).
 * Future: expand to other empires + Gemini Vision auto-extract from Wikipedia
 * 「Territorial evolution of X」 maps.
 */

import { writeFileSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const ROOT = resolve(__dirname, '..')

// ===== City lat/lon (lon, lat for GeoJSON) =====
const CITIES = {
  'Baghdad':        [44.42, 33.34],
  'Kufa':           [44.40, 32.03],
  'Basra':          [47.78, 30.50],
  'Mosul':          [43.13, 36.34],
  'Tikrit':         [43.69, 34.61],
  'Hilla':          [44.43, 32.46],
  'Samarra':        [43.88, 34.20],
  'Damascus':       [36.30, 33.51],
  'Aleppo':         [37.16, 36.20],
  'Homs':           [36.71, 34.73],
  'Jerusalem':      [35.23, 31.78],
  'Tyre':           [35.20, 33.27],
  'Antioch':        [36.16, 36.20],
  'Edessa':         [38.80, 37.16],
  'Cairo':          [31.24, 30.04],
  'Fustat':         [31.23, 30.01],
  'Alexandria':     [29.92, 31.20],
  'Aswan':          [32.90, 24.09],
  'Mecca':          [39.83, 21.43],
  'Medina':         [39.61, 24.47],
  "Sana'a":         [44.21, 15.37],
  'Aden':           [45.03, 12.79],
  'Muscat':         [58.59, 23.59],
  'Tripoli (Libya)':[13.18, 32.89],
  'Kairouan':       [10.10, 35.68],
  'Tunis':          [10.18, 36.81],
  'Fez':            [-5.00, 34.03],
  'Marrakesh':      [-7.99, 31.63],
  'Cordoba':        [-4.78, 37.89],   // Only Umayyad post-750
  'Granada':        [-3.60, 37.18],
  'Seville':        [-5.99, 37.39],
  'Toledo':         [-4.02, 39.86],
  'Nishapur':       [58.81, 36.21],
  'Merv':           [61.83, 37.60],
  'Bukhara':        [64.43, 39.77],
  'Samarkand':      [66.97, 39.65],
  'Tashkent':       [69.27, 41.32],
  'Ghazni':         [68.42, 33.55],
  'Kabul':          [69.21, 34.53],
  'Balkh':          [66.90, 36.76],
  'Herat':          [62.20, 34.34],
  'Multan':         [71.51, 30.20],
  'Lahore':         [74.36, 31.55],
  'Rayy':           [51.43, 35.59],   // Tehran area
  'Isfahan':        [51.67, 32.65],
  'Shiraz':         [52.53, 29.59],
  'Hamadan':        [48.51, 34.80],
  'Tabriz':         [46.27, 38.07],
  'Yerevan':        [44.51, 40.18],
  'Tbilisi':        [44.83, 41.72],
}

// ===== Abbasid territorial control by year =====
// Based on standard historiography of Abbasid extent.
// 750 — Revolution: inherited near-all Umayyad except al-Andalus
// 800 — Harun al-Rashid: peak, Aghlabids 800 take Ifriqiya soon after
// 900 — Tulunid (Egypt) detached, Saffarid in east, but caliph nominally
//        recognized; here we shade only direct rule (Iraq + western Iran + parts Levant)
// 1000 — Buyid de-facto rule in Iraq, Abbasid limited to Baghdad area
// 1100 — Seljuk era: Abbasid caliph in Baghdad with surroundings
// 1200 — al-Nasir reasserted: Baghdad + central Iraq

const CONTROL_BY_YEAR = {
  750: [
    'Baghdad', 'Kufa', 'Basra', 'Mosul', 'Tikrit', 'Hilla',
    'Damascus', 'Aleppo', 'Homs', 'Jerusalem', 'Tyre', 'Antioch', 'Edessa',
    'Cairo', 'Fustat', 'Alexandria', 'Aswan',
    'Mecca', 'Medina', "Sana'a", 'Aden',
    'Tripoli (Libya)', 'Kairouan', 'Tunis',
    'Nishapur', 'Merv', 'Bukhara', 'Samarkand',
    'Ghazni', 'Kabul', 'Balkh', 'Herat', 'Multan',
    'Rayy', 'Isfahan', 'Shiraz', 'Hamadan', 'Tabriz',
    'Yerevan', 'Tbilisi',
  ],
  800: [
    'Baghdad', 'Kufa', 'Basra', 'Mosul', 'Tikrit', 'Hilla', 'Samarra',
    'Damascus', 'Aleppo', 'Homs', 'Jerusalem', 'Tyre', 'Antioch', 'Edessa',
    'Cairo', 'Fustat', 'Alexandria', 'Aswan',
    'Mecca', 'Medina', "Sana'a", 'Aden',
    'Tripoli (Libya)', 'Kairouan',
    'Nishapur', 'Merv', 'Bukhara', 'Samarkand', 'Tashkent',
    'Ghazni', 'Kabul', 'Balkh', 'Herat', 'Multan',
    'Rayy', 'Isfahan', 'Shiraz', 'Hamadan', 'Tabriz',
    'Yerevan', 'Tbilisi',
  ],
  900: [
    'Baghdad', 'Kufa', 'Basra', 'Mosul', 'Tikrit', 'Hilla', 'Samarra',
    'Damascus', 'Aleppo', 'Homs', 'Jerusalem', 'Edessa',
    'Mecca', 'Medina',
    'Rayy', 'Isfahan', 'Hamadan',
    'Tabriz', 'Yerevan',
  ],
  1000: [
    'Baghdad', 'Kufa', 'Basra', 'Mosul', 'Tikrit', 'Hilla', 'Samarra',
    'Hamadan',
  ],
  1100: [
    'Baghdad', 'Kufa', 'Hilla', 'Samarra', 'Tikrit',
  ],
  1200: [
    'Baghdad', 'Kufa', 'Basra', 'Hilla', 'Samarra', 'Tikrit', 'Mosul',
  ],
}

// ===== Convex hull (Graham scan) =====
function cross(o, a, b) {
  return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
}
function convexHull(points) {
  const sorted = [...points].sort((a, b) => a[0] - b[0] || a[1] - b[1])
  const n = sorted.length
  if (n < 3) return sorted
  const lower = []
  for (const p of sorted) {
    while (lower.length >= 2 && cross(lower[lower.length - 2], lower[lower.length - 1], p) <= 0) {
      lower.pop()
    }
    lower.push(p)
  }
  const upper = []
  for (let i = n - 1; i >= 0; i--) {
    const p = sorted[i]
    while (upper.length >= 2 && cross(upper[upper.length - 2], upper[upper.length - 1], p) <= 0) {
      upper.pop()
    }
    upper.push(p)
  }
  upper.pop(); lower.pop()
  return lower.concat(upper)
}

// ===== Build GeoJSON =====
const features = []
const yearList = Object.keys(CONTROL_BY_YEAR).map(Number).sort((a, b) => a - b)

for (let i = 0; i < yearList.length; i++) {
  const year = yearList[i]
  const nextYear = yearList[i + 1] ?? 1260   // Abbasid fell 1258, end at 1260
  const cityNames = CONTROL_BY_YEAR[year]
  const coords = cityNames.map(n => {
    if (!CITIES[n]) {
      console.error('Missing city coords:', n)
      return null
    }
    return CITIES[n]
  }).filter(Boolean)

  if (coords.length < 3) {
    console.warn(`Year ${year}: only ${coords.length} cities — skipping (need ≥3 for hull)`)
    continue
  }

  const hull = convexHull(coords)
  // Close ring
  const ring = [...hull, hull[0]]
  features.push({
    type: 'Feature',
    geometry: { type: 'Polygon', coordinates: [ring] },
    properties: {
      name: 'Abbasid Caliphate',
      name_zh: '阿巴斯哈里發',
      year_from: year,
      year_to: nextYear - 1,
      cities: cityNames,
      source: 'city-hull POC (manual city list)',
    },
  })
  console.log(`Year ${year}: ${cityNames.length} cities → ${hull.length}-vertex hull`)
}

const geojson = { type: 'FeatureCollection', features }
const out = resolve(ROOT, 'public/maps/abbasid-fine-polygons.geojson')
writeFileSync(out, JSON.stringify(geojson, null, 2))
console.log(`\n✅ ${features.length} polygons → ${out}`)
console.log(`Total bytes: ${JSON.stringify(geojson).length}`)
