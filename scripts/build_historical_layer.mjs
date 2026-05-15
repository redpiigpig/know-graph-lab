#!/usr/bin/env node
/**
 * v5 預處理腳本：geometric intersection
 *
 * 為了精準呈現古代文化圈（如埃及只在尼羅河、阿拉伯次大陸只在半島），
 * 同時保留多區帝國底層的 sphere（如阿巴斯哈里發底下伊拉克=兩河、埃及=埃及）：
 *
 * 對每個 historical-basemaps state polygon：
 *   - 與每個現代 admin_0 polygon 做幾何交集
 *   - 每個交集片段 = 該現代國家在該年的 sphere 顏色
 *   - 結果：古代邊界 ∩ 現代國家 → 細緻多片，按地理區分 sphere
 *
 * 輸出：
 *   - public/maps/historical-sphere-fills.geojson — split features for sphere fill
 *   - public/maps/historical-states.geojson — original 古國 polygons for outline
 *
 * 來源資料 CC BY-NC-SA 4.0 — Andrei Ourednik (aourednik/historical-basemaps)
 */

import { readFileSync, writeFileSync, existsSync } from 'node:fs'
import { join } from 'node:path'
import { intersect } from '@turf/intersect'
import { featureCollection } from '@turf/helpers'
import { rewind } from '@turf/rewind'

const HBM_DIR = 'C:\\tmp\\hbm-sample'
const ADM0_FILE = 'public/maps/ne_50m_admin_0_countries.geojson'
const OUT_FILLS = 'public/maps/historical-sphere-fills.geojson'
const OUT_STATES = 'public/maps/historical-states.geojson'

const SNAPSHOTS = [
  [-4000, 'world_bc4000.geojson'],
  [-2000, 'world_bc2000.geojson'],
  [-1500, 'world_bc1500.geojson'],
  [-1000, 'world_bc1000.geojson'],
  [-500,  'world_bc500.geojson'],
  [-322,  'world_bc323.geojson'],
  [-99,   'world_bc100.geojson'],
  [200,   'world_200.geojson'],
  [500,   'world_500.geojson'],
  [800,   'world_800.geojson'],
  [1000,  'world_1000.geojson'],
  [1100,  'world_1100.geojson'],
  [1279,  'world_1279.geojson'],
  [1500,  'world_1500.geojson'],
  [1815,  'world_1815.geojson'],
  [1914,  'world_1914.geojson'],
  [2000,  'world_2000.geojson'],
]

/**
 * COUNTRY_SPHERE_TIMELINE
 * 鏡像 data/maps/country-sphere-timeline.ts（保持同步）。
 */
const COUNTRY_SPHERE_TIMELINE = {
  // 中央界域：詳細時序
  IRQ: [
    { from: -4000, sphere: 'sumerian' },
    { from: -2334, sphere: 'sumero-akkadian' },
    { from: -1200, sphere: 'assyrian' },
    { from: -626, sphere: 'babylonian' },
    { from: -539, sphere: 'mesopotamian-levantine' },
  ],
  SYR: [
    { from: -3000, sphere: 'canaan' },
    { from: -2334, sphere: 'sumero-akkadian' },
    { from: -1200, sphere: 'levant' },
    { from: -539, sphere: 'mesopotamian-levantine' },
  ],
  LBN: [
    { from: -3000, sphere: 'canaan' },
    { from: -1200, sphere: 'levant' },
    { from: -539, sphere: 'mesopotamian-levantine' },
  ],
  ISR: [
    { from: -3000, sphere: 'canaan' },
    { from: -1200, sphere: 'levant' },
    { from: -539, sphere: 'mesopotamian-levantine' },
  ],
  PSE: [
    { from: -3000, sphere: 'canaan' },
    { from: -1200, sphere: 'levant' },
    { from: -539, sphere: 'mesopotamian-levantine' },
  ],
  JOR: [
    { from: -3000, sphere: 'canaan' },
    { from: -1200, sphere: 'levant' },
    { from: -539, sphere: 'mesopotamian-levantine' },
  ],
  EGY: [{ from: -3500, sphere: 'egyptian' }],
  SDN: [{ from: -2500, sphere: 'egyptian' }],
  LBY: [{ from: -1100, sphere: 'carthaginian-maghreb' }],
  TUN: [{ from: -1100, sphere: 'carthaginian-maghreb' }],
  DZA: [{ from: -1100, sphere: 'carthaginian-maghreb' }],
  MAR: [{ from: -1100, sphere: 'carthaginian-maghreb' }],
  TUR: [
    { from: -2334, sphere: 'anatolia' },
    { from: -547, sphere: 'aegean-asia-minor' },
    { from: 1071, sphere: 'anatolia' },
  ],
  GRC: [{ from: -2700, sphere: 'aegean-asia-minor' }],
  CYP: [{ from: -2700, sphere: 'aegean-asia-minor' }],
  IRN: [{ from: -3200, sphere: 'persian' }],
  AFG: [{ from: -2000, sphere: 'persian' }],
  TJK: [{ from: -2000, sphere: 'persian' }],
  ARM: [{ from: -3400, sphere: 'caucasus' }],
  GEO: [{ from: -3400, sphere: 'caucasus' }],
  AZE: [{ from: -3400, sphere: 'caucasus' }],
  YEM: [{ from: -1200, sphere: 'arabian' }],
  SAU: [{ from: 622, sphere: 'arabian' }],
  OMN: [{ from: 622, sphere: 'arabian' }],
  BHR: [{ from: 622, sphere: 'arabian' }],
  QAT: [{ from: 622, sphere: 'arabian' }],
  ARE: [{ from: 622, sphere: 'arabian' }],
  KWT: [{ from: 622, sphere: 'arabian' }],
  // 東方
  CHN: [{ from: -2070, sphere: 'han' }],
  PAK: [{ from: -2600, sphere: 'indian' }],
  IND: [{ from: -2600, sphere: 'indian' }],
  NPL: [{ from: -1500, sphere: 'indian' }],
  BGD: [{ from: -1500, sphere: 'indian' }],
  LKA: [{ from: -500, sphere: 'indian' }],
  MDV: [{ from: -500, sphere: 'indian' }],
  BTN: [{ from: -1000, sphere: 'tibetan' }],
  // 亞太
  TWN: [{ from: -3000, sphere: 'banua' }],
  IDN: [{ from: -3000, sphere: 'banua' }],
  MYS: [{ from: -2000, sphere: 'banua' }],
  SGP: [{ from: -2000, sphere: 'banua' }],
  BRN: [{ from: -2000, sphere: 'banua' }],
  PHL: [{ from: -3000, sphere: 'banua' }],
  TLS: [{ from: -3000, sphere: 'banua' }],
  KHM: [{ from: -200, sphere: 'mekong' }],
  VNM: [{ from: -200, sphere: 'mekong' }],
  THA: [{ from: -200, sphere: 'mekong' }],
  LAO: [{ from: -200, sphere: 'mekong' }],
  MMR: [{ from: -200, sphere: 'mekong' }],
  KOR: [{ from: -1000, sphere: 'kuroshio' }],
  PRK: [{ from: -1000, sphere: 'kuroshio' }],
  JPN: [{ from: -1000, sphere: 'kuroshio' }],
  AUS: [{ from: -50000, sphere: 'australasian' }],
  NZL: [{ from: 1280, sphere: 'australasian' }],
  PNG: [{ from: -1500, sphere: 'pacific' }],
  FJI: [{ from: -1500, sphere: 'pacific' }],
  WSM: [{ from: -1500, sphere: 'pacific' }],
  TON: [{ from: -1500, sphere: 'pacific' }],
  VUT: [{ from: -1500, sphere: 'pacific' }],
  SLB: [{ from: -1500, sphere: 'pacific' }],
  PLW: [{ from: -1500, sphere: 'pacific' }],
  FSM: [{ from: -1500, sphere: 'pacific' }],
  MHL: [{ from: -1500, sphere: 'pacific' }],
  KIR: [{ from: 0, sphere: 'pacific' }],
  NRU: [{ from: 0, sphere: 'pacific' }],
  TUV: [{ from: 0, sphere: 'pacific' }],
  // 拉美
  MEX: [{ from: -1500, sphere: 'mesoamerican' }],
  GTM: [{ from: -1500, sphere: 'mesoamerican' }],
  BLZ: [{ from: -1500, sphere: 'mesoamerican' }],
  HND: [{ from: -1500, sphere: 'mesoamerican' }],
  SLV: [{ from: -1500, sphere: 'mesoamerican' }],
  NIC: [{ from: -1500, sphere: 'mesoamerican' }],
  CRI: [{ from: -1500, sphere: 'mesoamerican' }],
  PAN: [{ from: -1500, sphere: 'mesoamerican' }],
  PER: [{ from: -3000, sphere: 'andean' }],
  BOL: [{ from: -3000, sphere: 'andean' }],
  ECU: [{ from: -3000, sphere: 'andean' }],
  COL: [{ from: -3000, sphere: 'andean' }],
  CUB: [{ from: -2000, sphere: 'caribbean' }],
  DOM: [{ from: -2000, sphere: 'caribbean' }],
  HTI: [{ from: -2000, sphere: 'caribbean' }],
  JAM: [{ from: -2000, sphere: 'caribbean' }],
  BHS: [{ from: -2000, sphere: 'caribbean' }],
  VEN: [{ from: -2000, sphere: 'caribbean' }],
  GUY: [{ from: -2000, sphere: 'caribbean' }],
  SUR: [{ from: -2000, sphere: 'caribbean' }],
  CHL: [{ from: -2000, sphere: 'southern-cone' }],
  ARG: [{ from: -2000, sphere: 'southern-cone' }],
  PRY: [{ from: -2000, sphere: 'southern-cone' }],
  URY: [{ from: -2000, sphere: 'southern-cone' }],
  BRA: [{ from: -3000, sphere: 'amazonian-brazilian' }],
  // 西方
  ITA: [{ from: -1000, sphere: 'latin-cultural' }],
  VAT: [{ from: 754, sphere: 'latin-cultural' }],
  SMR: [{ from: 301, sphere: 'latin-cultural' }],
  ESP: [{ from: -1100, sphere: 'latin-cultural' }],
  PRT: [{ from: -1100, sphere: 'latin-cultural' }],
  MLT: [{ from: -800, sphere: 'latin-cultural' }],
  MCO: [{ from: -700, sphere: 'latin-cultural' }],
  AND: [{ from: 800, sphere: 'latin-cultural' }],
  MKD: [{ from: -1500, sphere: 'balkan' }],
  BGR: [{ from: -1500, sphere: 'balkan' }],
  SRB: [{ from: -1500, sphere: 'balkan' }],
  ROU: [{ from: -1500, sphere: 'balkan' }],
  ALB: [{ from: -1500, sphere: 'balkan' }],
  HRV: [{ from: 600, sphere: 'balkan' }],
  BIH: [{ from: 600, sphere: 'balkan' }],
  SVN: [{ from: 600, sphere: 'balkan' }],
  MNE: [{ from: 600, sphere: 'balkan' }],
  KOS: [{ from: 600, sphere: 'balkan' }],
  MDA: [{ from: 600, sphere: 'balkan' }],
  FRA: [{ from: -800, sphere: 'gallic-french' }],
  GBR: [{ from: -800, sphere: 'british-celtic' }],
  IRL: [{ from: -800, sphere: 'british-celtic' }],
  DEU: [{ from: -500, sphere: 'central-european' }],
  AUT: [{ from: -500, sphere: 'central-european' }],
  CHE: [{ from: -500, sphere: 'central-european' }],
  CZE: [{ from: -500, sphere: 'central-european' }],
  HUN: [{ from: -500, sphere: 'central-european' }],
  SVK: [{ from: -500, sphere: 'central-european' }],
  LIE: [{ from: 100, sphere: 'central-european' }],
  BEL: [{ from: -500, sphere: 'low-countries' }],
  NLD: [{ from: -500, sphere: 'low-countries' }],
  LUX: [{ from: -500, sphere: 'low-countries' }],
  POL: [{ from: 500, sphere: 'lublin' }],
  LTU: [{ from: 500, sphere: 'lublin' }],
  LVA: [{ from: 500, sphere: 'lublin' }],
  DNK: [{ from: -1000, sphere: 'nordic-livonian' }],
  SWE: [{ from: -1000, sphere: 'nordic-livonian' }],
  NOR: [{ from: -1000, sphere: 'nordic-livonian' }],
  FIN: [{ from: -1000, sphere: 'nordic-livonian' }],
  ISL: [{ from: 874, sphere: 'nordic-livonian' }],
  EST: [{ from: -1000, sphere: 'nordic-livonian' }],
  // 南方
  ETH: [{ from: -1000, sphere: 'ethiopian' }],
  ERI: [{ from: -1000, sphere: 'ethiopian' }],
  MLI: [{ from: -1000, sphere: 'west-african-sahel' }],
  SEN: [{ from: -1000, sphere: 'west-african-sahel' }],
  NER: [{ from: -1000, sphere: 'west-african-sahel' }],
  CPV: [{ from: 1500, sphere: 'west-african-sahel' }],
  BFA: [{ from: -1000, sphere: 'west-african-sahel' }],
  GIN: [{ from: -1000, sphere: 'west-african-sahel' }],
  GMB: [{ from: -1000, sphere: 'west-african-sahel' }],
  GNB: [{ from: -1000, sphere: 'west-african-sahel' }],
  MRT: [{ from: -1000, sphere: 'west-african-sahel' }],
  TCD: [{ from: -1000, sphere: 'west-african-sahel' }],
  NGA: [{ from: 500, sphere: 'gulf-of-guinea' }],
  GHA: [{ from: 500, sphere: 'gulf-of-guinea' }],
  CIV: [{ from: 500, sphere: 'gulf-of-guinea' }],
  TGO: [{ from: 500, sphere: 'gulf-of-guinea' }],
  BEN: [{ from: 500, sphere: 'gulf-of-guinea' }],
  LBR: [{ from: 500, sphere: 'gulf-of-guinea' }],
  SLE: [{ from: 500, sphere: 'gulf-of-guinea' }],
  KEN: [{ from: 800, sphere: 'east-african-swahili' }],
  TZA: [{ from: 800, sphere: 'east-african-swahili' }],
  UGA: [{ from: 800, sphere: 'east-african-swahili' }],
  RWA: [{ from: 800, sphere: 'east-african-swahili' }],
  BDI: [{ from: 800, sphere: 'east-african-swahili' }],
  SOM: [{ from: 800, sphere: 'east-african-swahili' }],
  DJI: [{ from: 800, sphere: 'east-african-swahili' }],
  COM: [{ from: 800, sphere: 'east-african-swahili' }],
  MDG: [{ from: 500, sphere: 'east-african-swahili' }],
  SSD: [{ from: 800, sphere: 'east-african-swahili' }],
  COD: [{ from: 500, sphere: 'central-african-congolese' }],
  COG: [{ from: 500, sphere: 'central-african-congolese' }],
  CMR: [{ from: 500, sphere: 'central-african-congolese' }],
  CAF: [{ from: 500, sphere: 'central-african-congolese' }],
  GAB: [{ from: 500, sphere: 'central-african-congolese' }],
  GNQ: [{ from: 500, sphere: 'central-african-congolese' }],
  STP: [{ from: 1500, sphere: 'central-african-congolese' }],
  ZWE: [{ from: 500, sphere: 'southern-african-bantu' }],
  MOZ: [{ from: 500, sphere: 'southern-african-bantu' }],
  ZAF: [{ from: 500, sphere: 'southern-african-bantu' }],
  AGO: [{ from: 500, sphere: 'southern-african-bantu' }],
  NAM: [{ from: 500, sphere: 'southern-african-bantu' }],
  BWA: [{ from: 500, sphere: 'southern-african-bantu' }],
  ZMB: [{ from: 500, sphere: 'southern-african-bantu' }],
  MWI: [{ from: 500, sphere: 'southern-african-bantu' }],
  LSO: [{ from: 500, sphere: 'southern-african-bantu' }],
  SWZ: [{ from: 500, sphere: 'southern-african-bantu' }],
  // 北方
  UZB: [{ from: -700, sphere: 'turanian-turkic' }],
  TKM: [{ from: -700, sphere: 'turanian-turkic' }],
  KGZ: [{ from: -700, sphere: 'turanian-turkic' }],
  KAZ: [{ from: -700, sphere: 'turanian-turkic' }],
  UKR: [{ from: 862, sphere: 'russian-tatar' }],
  BLR: [{ from: 862, sphere: 'russian-tatar' }],
  RUS: [{ from: 862, sphere: 'russian-tatar' }],
  MNG: [{ from: -200, sphere: 'mongolic-tungusic' }],
  // 北美
  USA: [{ from: 1607, sphere: 'anglo-american' }],
  CAN: [{ from: 1534, sphere: 'franco-american' }],
  GRL: [{ from: -2500, sphere: 'arctic' }],
}

function sphereForCountryAtYear(iso, year) {
  const tl = COUNTRY_SPHERE_TIMELINE[iso]
  if (!tl) return null
  let active = null
  for (const entry of tl) {
    if (entry.from <= year) active = entry.sphere
    else break
  }
  return active
}

function getAdm0Code(props) {
  const iso = props.ISO_A3
  if (iso && iso !== '-99') return iso
  return props.ADM0_A3 || ''
}

// ---------- Main ----------
function main() {
  console.log('Loading modern admin_0…')
  const adm0 = JSON.parse(readFileSync(ADM0_FILE, 'utf8'))
  const adm0Features = adm0.features
    .filter(f => f.properties?.ADM0_A3 !== 'ATA')
    .map(f => ({ feature: f, iso: getAdm0Code(f.properties) }))
  console.log(`  ${adm0Features.length} modern countries loaded`)

  const fillFeatures = []
  const stateFeatures = []  // original (unsplit) state polygons for outline overlay

  for (let si = 0; si < SNAPSHOTS.length; si++) {
    const [yearFrom, fname] = SNAPSHOTS[si]
    const yearTo = si + 1 < SNAPSHOTS.length ? SNAPSHOTS[si + 1][0] - 1 : 9999
    const path = join(HBM_DIR, fname)
    if (!existsSync(path)) {
      console.warn(`SKIP ${fname}`)
      continue
    }
    const gj = JSON.parse(readFileSync(path, 'utf8'))
    let kept = 0
    let splits = 0

    for (const hf of gj.features) {
      const nm = hf.properties?.NAME?.trim()
      if (!nm) continue
      // Skip pure tribal/hunter-gatherer labels
      if (/hunter[- ]gatherer|tribal|culture$|cultures$| culture[s]?$/i.test(nm) && !/civiliz/i.test(nm)) continue

      stateFeatures.push({
        type: 'Feature',
        properties: { name: nm, year_from: yearFrom, year_to: yearTo },
        geometry: hf.geometry,
      })

      // Intersect with each modern admin_0
      for (const { feature: af, iso } of adm0Features) {
        const sphereId = sphereForCountryAtYear(iso, yearFrom)
        if (!sphereId) continue
        let inter
        try {
          inter = intersect(featureCollection([hf, af]))
        } catch (e) {
          // skip topology errors
          continue
        }
        if (!inter || !inter.geometry) continue
        // skip near-empty intersections
        const coords = inter.geometry.coordinates
        if (!coords || (Array.isArray(coords) && coords.length === 0)) continue
        // Ensure proper GeoJSON winding (counter-clockwise exterior, clockwise holes)
        // turf intersect can produce reversed winding which makes d3-geo render the
        // polygon as covering the antipodal hemisphere — appearing as a giant blob.
        try {
          inter = rewind(inter, { reverse: true })
        } catch {}
        fillFeatures.push({
          type: 'Feature',
          properties: {
            sphere_id: sphereId,
            iso_a3: iso,
            state_name: nm,
            year_from: yearFrom,
            year_to: yearTo,
          },
          geometry: inter.geometry,
        })
        splits += 1
      }
      kept += 1
    }
    console.log(`${fname.padEnd(28)} y=${String(yearFrom).padStart(5)}..${String(yearTo).padStart(5)}  states=${kept}  fills=${splits}`)
  }

  // Output sphere fills
  const fillsOut = {
    type: 'FeatureCollection',
    name: 'historical-sphere-fills',
    crs: { type: 'name', properties: { name: 'urn:ogc:def:crs:OGC:1.3:CRS84' } },
    attribution: 'CC BY-NC-SA 4.0 — Andrei Ourednik (aourednik/historical-basemaps), intersected with NE 50m admin_0',
    features: fillFeatures,
  }
  writeFileSync(OUT_FILLS, JSON.stringify(fillsOut))
  console.log(`\n→ ${OUT_FILLS} (${fillFeatures.length} fill features, ${Math.round(JSON.stringify(fillsOut).length / 1024)} KB)`)

  // Output state outlines
  const statesOut = {
    type: 'FeatureCollection',
    name: 'historical-states',
    crs: { type: 'name', properties: { name: 'urn:ogc:def:crs:OGC:1.3:CRS84' } },
    attribution: 'CC BY-NC-SA 4.0 — Andrei Ourednik (aourednik/historical-basemaps)',
    features: stateFeatures,
  }
  writeFileSync(OUT_STATES, JSON.stringify(statesOut))
  console.log(`→ ${OUT_STATES} (${stateFeatures.length} state features, ${Math.round(JSON.stringify(statesOut).length / 1024)} KB)`)
}

main()
