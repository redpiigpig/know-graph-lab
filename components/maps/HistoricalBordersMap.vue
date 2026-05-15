<template>
  <div ref="rootEl" class="relative w-full h-full bg-slate-50 rounded-xl overflow-hidden">
    <svg
      ref="svgEl"
      :width="width"
      :height="height"
      :viewBox="`0 0 ${width} ${height}`"
      class="block select-none cursor-default"
    >
      <!-- 海背景：白 -->
      <rect :width="width" :height="height" fill="#FFFFFF" />

      <g :transform="`translate(${transform.x},${transform.y}) scale(${transform.k})`">
        <!-- 陸地灰底 -->
        <path
          v-for="p in landPaths"
          :key="p.id"
          :d="p.d"
          fill="#D1D5DB"
          stroke="none"
        />

        <!-- 國家／帝國 polygon (彩色) -->
        <path
          v-for="p in statePaths"
          :key="p.id"
          :d="p.d"
          :fill="p.fill"
          :stroke="p.strokeColor"
          :stroke-width="1.2 / transform.k"
          stroke-opacity="0.9"
          :pointer-events="'auto'"
          class="cursor-pointer"
          @click.stop="onStateClick(p, $event)"
        />

        <!-- 海岸線：黑 -->
        <path
          v-for="p in coastPaths"
          :key="p.id"
          :d="p.d"
          fill="none"
          stroke="#000000"
          :stroke-width="0.6 / transform.k"
          stroke-opacity="0.8"
          pointer-events="none"
        />

        <!-- 國家名稱標籤 -->
        <g pointer-events="none">
          <g v-for="lbl in stateLabels" :key="lbl.id" :transform="`translate(${lbl.x},${lbl.y})`">
            <text
              text-anchor="middle"
              :font-size="lbl.fontSize / transform.k"
              font-weight="600"
              fill="#FFFFFF"
              stroke="rgba(0,0,0,0.7)"
              :stroke-width="(lbl.fontSize * 0.22) / transform.k"
              paint-order="stroke fill"
              style="font-family: ui-sans-serif, system-ui;"
            >{{ lbl.text }}</text>
          </g>
        </g>
      </g>
    </svg>

    <div v-if="loading" class="absolute inset-0 flex items-center justify-center text-gray-400 text-sm">
      載入地圖中…
    </div>

    <!-- Year badge -->
    <div
      class="absolute left-1/2 top-3 -translate-x-1/2 z-10 bg-amber-50/95 backdrop-blur border border-amber-300 rounded-lg shadow-md px-3 py-1.5 pointer-events-none"
    >
      <div class="flex items-baseline gap-2">
        <span class="text-sm font-bold text-amber-900 tabular-nums">{{ formatYearShort(props.currentYear) }}</span>
        <span class="text-xs text-amber-700">{{ activeStateCount }} 個政治體</span>
      </div>
      <div class="text-[10px] text-amber-600 mt-0.5">純政治／帝國國界，無文化圈著色</div>
    </div>

    <!-- Attribution -->
    <div
      class="absolute right-3 top-3 z-10 bg-white/90 backdrop-blur rounded-md border border-gray-200 px-2 py-0.5 text-[10px] text-gray-500 pointer-events-none"
    >
      © <a href="https://github.com/aourednik/historical-basemaps" target="_blank" class="hover:text-gray-700 pointer-events-auto" rel="noopener">historical-basemaps</a> · CC BY-NC-SA 4.0
    </div>

    <!-- Selected state info -->
    <div
      v-if="selectedState"
      class="absolute right-3 top-14 z-10 w-[260px] bg-white border border-gray-200 rounded-xl shadow-md p-3 text-xs"
    >
      <div class="flex items-start justify-between gap-2 mb-1.5">
        <div>
          <div class="font-semibold text-sm text-gray-900 leading-tight">{{ nameZhOf(selectedState.name) }}</div>
          <div v-if="nameZhOf(selectedState.name) !== selectedState.name" class="text-[10px] text-gray-400 mt-0.5">{{ selectedState.name }}</div>
        </div>
        <button
          @click="selectedState = null"
          class="text-gray-300 hover:text-gray-700 leading-none -mt-0.5 text-base"
          aria-label="關閉"
        >×</button>
      </div>
      <div class="text-gray-500">有效年代：{{ formatYearShort(selectedState.yearFrom) }} – {{ selectedState.yearTo >= 9999 ? '至今' : formatYearShort(selectedState.yearTo) }}</div>
    </div>

    <!-- Zoom controls -->
    <div class="absolute right-3 bottom-3 flex flex-col bg-white/95 backdrop-blur rounded-lg border border-gray-200 shadow-sm overflow-hidden">
      <button
        @click="zoomBy(1.5)"
        class="w-8 h-8 flex items-center justify-center text-gray-600 hover:bg-gray-100 hover:text-gray-900 text-lg leading-none border-b border-gray-200"
        aria-label="放大"
      >＋</button>
      <button
        @click="zoomBy(1/1.5)"
        class="w-8 h-8 flex items-center justify-center text-gray-600 hover:bg-gray-100 hover:text-gray-900 text-lg leading-none border-b border-gray-200"
        aria-label="縮小"
      >−</button>
      <button
        @click="resetZoom"
        class="w-8 h-8 flex items-center justify-center text-gray-500 hover:bg-gray-100 hover:text-gray-900 text-[10px]"
        aria-label="重置"
      >⟲</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { geoEqualEarth, geoPath, geoCentroid, type GeoProjection } from 'd3-geo'
import { zoom as d3zoom, zoomIdentity, type ZoomBehavior } from 'd3-zoom'
import { select } from 'd3-selection'
import { formatYearShort } from '~/data/maps/historical-epochs'
import { STATE_DETAILS, type WikidataState } from '~/data/maps/historical-states-db'
import { COUNTRY_NAME_ZH } from '~/data/maps/world-religions'

// 從現代國家英文名找 ISO_A3 → 中文。NE admin_0 用的是國家英文全名。
const adm0NameToZh = new Map<string, string>()

// historical-basemaps 用的特殊國名（與 NE admin_0 NAME_EN 不一致）的手動補譯
const SUPPLEMENT_ZH: Record<string, string> = {
  'United States': '美國',
  'United Kingdom': '英國',
  'United Kingdom of Great Britain and Ireland': '大不列顛及愛爾蘭聯合王國',
  'British Empire': '大英帝國',
  'Empire of Japan': '大日本帝國',
  'Imperial Japan': '大日本帝國',
  'USSR': '蘇聯',
  'Soviet Union': '蘇聯',
  'Russian Empire': '俄羅斯帝國',
  'Ottoman Empire': '奧斯曼帝國',
  'German Empire': '德意志帝國',
  'East Germany': '東德',
  'West Germany': '西德',
  'Czechoslovakia': '捷克斯洛伐克',
  'Yugoslavia': '南斯拉夫',
  'British Raj': '英屬印度',
  'British India': '英屬印度',
  'Ceylon': '錫蘭',
  'Burma': '緬甸',
  'Persia': '波斯',
  'Manchuria': '滿洲國',
  'French Indo-China': '法屬印度支那',
  'Dutch East Indies': '荷屬東印度',
  'French West Africa': '法屬西非',
  'French Equatorial Africa': '法屬赤道非洲',
  'Italian Somaliland': '義屬索馬利蘭',
  'British Somaliland': '英屬索馬利蘭',
  'French Somaliland': '法屬索馬利蘭',
  'Spanish Sahara': '西屬撒哈拉',
  'Western Sahara': '西撒哈拉',
  'Mandatory Palestine (GB)': '英屬巴勒斯坦託管地',
  'Mesopotamia (GB)': '英屬美索不達米亞託管地',
  'Syria (France)': '法屬敘利亞託管地',
  'Madagascar (France)': '法屬馬達加斯加',
  'Rwanda (Belgium)': '比屬盧安達',
  'French Cameroons': '法屬喀麥隆',
  'Angola (Portugal)': '葡屬安哥拉',
  'Hejaz': '漢志',
  'Hail': '哈伊勒',
  'Trucial Oman': '特魯西阿曼',
  'Muscat and Oman': '馬斯喀特與阿曼',
  'Cochin China': '交趾支那',
  'Annam': '安南',
  'Tanzania, United Republic of': '坦尚尼亞',
  "Korea, Democratic People's Republic of": '北韓',
  'Korea, Republic of': '南韓',
  'Gambia, The': '甘比亞',
  'Korea': '韓國',
  'Swaziland': '史瓦帝尼',
  'Puerto Rico': '波多黎各',
  'Hong Kong': '香港',
  'Greenland': '格陵蘭',
  'French Guiana': '法屬圭亞那',
  'Wallis and Futuna Islands': '瓦利斯和富圖納群島',
  'American Samoa': '美屬薩摩亞',
  'Tonga': '東加',
  'Samoa': '薩摩亞',
  'Niue': '紐埃',
  'Antigua and Barbuda': '安地卡及巴布達',
  'Dominica': '多米尼克',
  'Montserrat': '蒙特塞拉特',
  'Anguilla': '安圭拉',
  'Saint Kitts and Nevis': '聖克里斯多福及尼維斯',
  'United States Virgin Islands': '美屬維京群島',
  'Guadeloupe': '瓜地洛普',
  'Netherlands Antilles': '荷屬安地列斯',
  'Saint Martin': '聖馬丁',
  'Saint Barthelemy': '聖巴瑟米',
  'Saint Lucia': '聖露西亞',
  'Saint Vincent and the Grenadines': '聖文森及格瑞那丁',
  'Bahamas': '巴哈馬',
  'Barbados': '巴貝多',
  'Grenada': '格瑞那達',
  'Trinidad': '千里達',
  'Andorra': '安道爾',
  'Martinique': '馬丁尼克',
  'Turks and Caicos Islands': '土克凱可群島',
  'Rapa Nui': '復活節島',
  'Xinjiang': '新疆',
  'Tibet': '西藏',
  'Italy': '義大利',
  'France': '法國',
  'Spain': '西班牙',
  'Germany': '德國',
  'Hong Kong': '香港',
}

const props = withDefaults(defineProps<{ currentYear?: number }>(), { currentYear: -1500 })

const rootEl = ref<HTMLElement | null>(null)
const svgEl = ref<SVGSVGElement | null>(null)
const width = ref(1200)
const height = ref(620)
const loading = ref(true)

const transform = ref({ k: 1, x: 0, y: 0 })
let zoomBehavior: ZoomBehavior<SVGSVGElement, unknown> | null = null
let projectionCache: GeoProjection | null = null

// ===== 資料 =====
interface StateEntry {
  feature: any
  name: string
  yearFrom: number
  yearTo: number
}

const landFeatures = ref<any[]>([])
const stateEntries = ref<StateEntry[]>([])
const coastlineFeatures = ref<any[]>([])
const nameZhMap = ref<Map<string, string>>(new Map())
const polygonNameZh = ref<Record<string, string>>({})

function nameZhOf(en: string): string {
  return STATE_DETAILS[en]?.name_zh
    || SUPPLEMENT_ZH[en]
    || adm0NameToZh.get(en)
    || nameZhMap.value.get(en)
    || polygonNameZh.value[en]
    || en
}

interface PathItem { id: string; d: string; fill?: string; strokeColor?: string }
interface StatePathItem extends PathItem {
  name: string
  yearFrom: number
  yearTo: number
}
interface LabelItem { id: string; x: number; y: number; text: string; fontSize: number }

const landPaths = ref<PathItem[]>([])
const statePaths = ref<StatePathItem[]>([])
const coastPaths = ref<PathItem[]>([])
const stateLabels = ref<LabelItem[]>([])

const selectedState = ref<StatePathItem | null>(null)

const activeStateCount = computed(() =>
  stateEntries.value.filter(s => props.currentYear >= s.yearFrom && props.currentYear <= s.yearTo).length
)

// ===== 色彩：依國家名稱 hash 算出穩定 HSL =====
function colorForState(name: string): { fill: string; stroke: string } {
  let h = 0
  for (let i = 0; i < name.length; i++) {
    h = ((h << 5) - h + name.charCodeAt(i)) | 0
  }
  const hue = ((h % 360) + 360) % 360
  // 連續色相分群，避免相同 hue 連續出現
  const sat = 55 + ((h >> 8) & 0x1f)  // 55-86%
  const lit = 60 + ((h >> 13) & 0x0f)  // 60-75%
  const fill = `hsl(${hue}, ${sat}%, ${lit}%)`
  const stroke = `hsl(${hue}, ${Math.min(sat + 10, 90)}%, ${Math.max(lit - 25, 25)}%)`
  return { fill, stroke }
}

function getAdm0Code(props: any): string {
  const iso = props.ISO_A3
  if (iso && iso !== '-99') return iso
  return props.ADM0_A3 || ''
}

function makeProjection(): GeoProjection {
  const p = geoEqualEarth()
    .fitSize([width.value, height.value - 20], { type: 'Sphere' } as any)
    .translate([width.value / 2, (height.value - 20) / 2 + 10])
  projectionCache = p
  return p
}

function rebuildAll() {
  if (!landFeatures.value.length) return
  const projection = makeProjection()
  const path = geoPath(projection)
  const year = props.currentYear

  // Land base
  landPaths.value = landFeatures.value.map((f, i) => ({
    id: `land-${i}`, d: path(f) || '',
  })).filter(p => p.d)

  // States active at year
  const activeStates = stateEntries.value.filter(s =>
    year >= s.yearFrom && year <= s.yearTo
  )
  statePaths.value = activeStates.map((s, i) => {
    const { fill, stroke } = colorForState(s.name)
    return {
      id: `state-${i}-${s.name}`,
      d: path(s.feature) || '',
      fill, strokeColor: stroke,
      name: s.name,
      yearFrom: s.yearFrom,
      yearTo: s.yearTo,
    }
  }).filter(p => p.d)

  // Coastline
  coastPaths.value = coastlineFeatures.value.map((f, i) => ({
    id: `coast-${i}`, d: path(f) || '',
  })).filter(p => p.d)

  // Labels — compute centroid per state
  const labels: LabelItem[] = []
  for (const s of activeStates) {
    let c: [number, number]
    try {
      c = geoCentroid(s.feature)
      if (isNaN(c[0]) || isNaN(c[1])) continue
    } catch { continue }
    const xy = projection(c)
    if (!xy || isNaN(xy[0]) || isNaN(xy[1])) continue
    labels.push({
      id: `lbl-${s.name}-${labels.length}`,
      x: xy[0], y: xy[1],
      text: nameZhOf(s.name),
      fontSize: 10,
    })
  }
  relaxLabelCollisions(labels)
  stateLabels.value = labels
}

function relaxLabelCollisions(labels: LabelItem[]) {
  if (labels.length < 2) return
  const PADDING = 4
  const ITER = 30
  const widthOf = (l: LabelItem) => l.text.length * l.fontSize * 0.6
  const heightOf = (l: LabelItem) => l.fontSize * 1.2
  for (let iter = 0; iter < ITER; iter++) {
    let moved = false
    for (let i = 0; i < labels.length; i++) {
      for (let j = i + 1; j < labels.length; j++) {
        const a = labels[i], b = labels[j]
        const dx = a.x - b.x
        const dy = a.y - b.y
        const minDx = (widthOf(a) + widthOf(b)) / 2 + PADDING
        const minDy = (heightOf(a) + heightOf(b)) / 2 + PADDING
        const overlapX = minDx - Math.abs(dx)
        const overlapY = minDy - Math.abs(dy)
        if (overlapX > 0 && overlapY > 0) {
          if (overlapX < overlapY) {
            const push = overlapX / 2 * (dx >= 0 ? 1 : -1)
            a.x += push; b.x -= push
          } else {
            const push = overlapY / 2 * (dy >= 0 ? 1 : -1)
            a.y += push; b.y -= push
          }
          moved = true
        }
      }
    }
    if (!moved) break
  }
}

function onStateClick(p: StatePathItem, _ev: MouseEvent) {
  selectedState.value = selectedState.value?.id === p.id ? null : p
}

function applyZoomTransform(t: { k: number; x: number; y: number }) {
  transform.value = t
}
function zoomBy(factor: number) {
  if (!svgEl.value || !zoomBehavior) return
  select(svgEl.value).transition().duration(200).call(zoomBehavior.scaleBy as any, factor)
}
function resetZoom() {
  if (!svgEl.value || !zoomBehavior) return
  select(svgEl.value).transition().duration(250).call(zoomBehavior.transform as any, zoomIdentity)
}

let ro: ResizeObserver | null = null

onMounted(async () => {
  if (rootEl.value) {
    const rect = rootEl.value.getBoundingClientRect()
    width.value = Math.max(640, Math.floor(rect.width))
    height.value = Math.max(360, Math.round(width.value * 0.5))
  }
  ro = new ResizeObserver(() => {
    if (!rootEl.value) return
    const rect = rootEl.value.getBoundingClientRect()
    const newW = Math.max(640, Math.floor(rect.width))
    if (Math.abs(newW - width.value) > 4) {
      width.value = newW
      height.value = Math.round(newW * 0.5)
      rebuildAll()
    }
  })
  ro.observe(rootEl.value!)

  zoomBehavior = d3zoom<SVGSVGElement, unknown>()
    .scaleExtent([1, 16])
    .translateExtent([[-200, -200], [width.value + 200, height.value + 200]])
    .on('zoom', (event: any) => {
      applyZoomTransform({ k: event.transform.k, x: event.transform.x, y: event.transform.y })
    })
  if (svgEl.value) {
    select(svgEl.value).call(zoomBehavior as any)
  }

  try {
    const [adm0Res, statesRes, coastRes, wdRes, polyZhRes] = await Promise.all([
      fetch('/maps/ne_50m_admin_0_countries.geojson'),
      fetch('/maps/historical-states.geojson'),
      fetch('/maps/ne_50m_coastline.geojson'),
      fetch('/maps/wikidata-states.json'),
      fetch('/maps/polygon-names-zh.json').catch(() => ({ ok: false } as any)),
    ])
    const [adm0, states, coast, wd] = await Promise.all([
      adm0Res.json(), statesRes.json(), coastRes.json(), wdRes.json(),
    ])
    if (polyZhRes && (polyZhRes as Response).ok) {
      try { polygonNameZh.value = await (polyZhRes as Response).json() } catch {}
    }
    landFeatures.value = adm0.features.filter((f: any) => f.properties.ADM0_A3 !== 'ATA')
    coastlineFeatures.value = coast.features || []
    const m = new Map<string, string>()
    for (const w of wd as WikidataState[]) {
      if (w.name_zh) m.set(w.name_en, w.name_zh)
    }
    nameZhMap.value = m
    // 從 NE admin_0 抽各種 NAME 變體 → 中文。優先 NAME_ZHT (繁中)，再 NAME_ZH (簡中)，
    // 退而求其次用 ISO → COUNTRY_NAME_ZH
    adm0NameToZh.clear()
    for (const f of adm0.features) {
      const iso = f.properties.ISO_A3 || f.properties.ADM0_A3
      const zh = f.properties.NAME_ZHT || f.properties.NAME_ZH || COUNTRY_NAME_ZH[iso]
      if (!zh) continue
      // 一個 admin_0 可能在不同 NAME 欄位有不同英文寫法 — 全收
      for (const k of ['NAME', 'NAME_EN', 'NAME_LONG', 'ADMIN', 'SOVEREIGNT', 'BRK_NAME']) {
        const en = f.properties[k]
        if (en && !adm0NameToZh.has(en)) adm0NameToZh.set(en, zh)
      }
    }
    stateEntries.value = (states.features || []).map((f: any) => ({
      feature: f,
      name: f.properties.name,
      yearFrom: f.properties.year_from,
      yearTo: f.properties.year_to,
    }))
    rebuildAll()
  } catch (e) {
    console.error('歷史國界地圖載入失敗', e)
  } finally {
    loading.value = false
  }
})

onBeforeUnmount(() => {
  ro?.disconnect()
})

watch(() => props.currentYear, () => {
  selectedState.value = null
  rebuildAll()
})
</script>
