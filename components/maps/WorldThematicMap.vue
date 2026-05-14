<template>
  <div ref="rootEl" class="relative w-full h-full bg-slate-50 rounded-xl overflow-hidden">
    <svg
      ref="svgEl"
      :width="width"
      :height="height"
      :viewBox="`0 0 ${width} ${height}`"
      class="block select-none"
      :class="selectedRealm ? 'cursor-default' : 'cursor-default'"
    >
      <!-- Background catches "click empty space" to deselect -->
      <rect
        :width="width"
        :height="height"
        fill="#F1F5F9"
        @click="onBackgroundClick"
      />

      <!-- Zoomable / pannable group -->
      <g :transform="`translate(${transform.x},${transform.y}) scale(${transform.k})`">
        <g v-if="paths.length">
          <path
            v-for="p in paths"
            :key="p.id"
            :d="p.d"
            :fill="p.fill"
            :fill-opacity="p.opacity"
            stroke="#FFFFFF"
            :stroke-width="p.strokeBase / transform.k"
            :stroke-opacity="p.opacity"
            class="cursor-pointer"
            style="transition: fill 200ms, fill-opacity 200ms;"
            @click.stop="onCountryClick(p, $event)"
          />
        </g>

        <!-- Selected feature outline (drawn above paths so it's visible) -->
        <path
          v-if="selectedFeature"
          :d="selectedFeature.d"
          fill="none"
          stroke="#0F172A"
          :stroke-width="2 / transform.k"
          pointer-events="none"
        />

        <!-- Realm labels (default view) -->
        <g v-if="!selectedRealm && realmLabels.length" pointer-events="none">
          <g v-for="lbl in realmLabels" :key="lbl.id" :transform="`translate(${lbl.x},${lbl.y})`">
            <text
              text-anchor="middle"
              :font-size="lbl.fontSize / transform.k"
              font-weight="700"
              fill="#FFFFFF"
              stroke="rgba(0,0,0,0.55)"
              :stroke-width="(lbl.fontSize * 0.18) / transform.k"
              paint-order="stroke fill"
              style="font-family: ui-sans-serif, system-ui;"
            >{{ lbl.text }}</text>
          </g>
        </g>

        <!-- Sphere labels (drilled view) -->
        <g v-else-if="selectedRealm && sphereLabels.length" pointer-events="none">
          <!-- Leader lines (drawn first so they're under text) -->
          <g>
            <line
              v-for="lbl in sphereLabels.filter(l => l.hasLeader)"
              :key="`leader-${lbl.id}`"
              :x1="lbl.anchorX"
              :y1="lbl.anchorY"
              :x2="lbl.x"
              :y2="lbl.y"
              stroke="rgba(15,23,42,0.55)"
              :stroke-width="0.8 / transform.k"
            />
            <circle
              v-for="lbl in sphereLabels.filter(l => l.hasLeader)"
              :key="`anchor-${lbl.id}`"
              :cx="lbl.anchorX"
              :cy="lbl.anchorY"
              :r="1.4 / transform.k"
              fill="rgba(15,23,42,0.7)"
            />
          </g>
          <g v-for="lbl in sphereLabels" :key="lbl.id" :transform="`translate(${lbl.x},${lbl.y})`">
            <text
              text-anchor="middle"
              :font-size="lbl.fontSize / transform.k"
              font-weight="600"
              fill="#FFFFFF"
              stroke="rgba(0,0,0,0.6)"
              :stroke-width="(lbl.fontSize * 0.2) / transform.k"
              paint-order="stroke fill"
              style="font-family: ui-sans-serif, system-ui;"
            >{{ lbl.text }}</text>
          </g>
        </g>
      </g>
    </svg>

    <div v-if="loading" class="absolute inset-0 flex items-center justify-center text-gray-400 text-sm">
      載入世界地圖中…
    </div>

    <!-- Selected feature info (only in drilled view) -->
    <div
      v-if="selectedFeature && selectedRealm"
      class="absolute right-3 top-14 z-10 w-[260px] bg-white border border-gray-200 rounded-xl shadow-md p-3 text-xs"
    >
      <div class="flex items-start justify-between gap-2 mb-1.5">
        <div class="font-semibold text-sm text-gray-900 leading-tight">{{ selectedFeature.title }}</div>
        <button
          @click="selectedFeature = null"
          class="text-gray-300 hover:text-gray-700 leading-none -mt-0.5 text-base"
          aria-label="關閉"
        >×</button>
      </div>
      <div v-if="selectedFeature.realm" class="flex items-center gap-1.5 mb-1">
        <span class="inline-block w-2.5 h-2.5 rounded-sm" :style="{ background: selectedFeature.realm.color }"></span>
        <span class="text-gray-600">{{ selectedFeature.realm.index }}. {{ selectedFeature.realm.name_zh }}</span>
      </div>
      <div v-if="selectedFeature.spheres.length" class="text-gray-500 text-[11px] leading-relaxed mt-1 space-y-0.5">
        <div v-for="(s, i) in selectedFeature.spheres" :key="i">
          · {{ s.name }}<span v-if="s.note" class="text-gray-400"> — {{ s.note }}</span>
        </div>
      </div>
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

    <!-- Legend (default: 8 realms) -->
    <div v-if="!selectedRealm" class="absolute left-3 bottom-3 bg-white/95 backdrop-blur rounded-lg border border-gray-200 px-3 py-2 shadow-sm">
      <div class="text-[11px] text-gray-500 mb-1.5 font-medium">八大界域<span class="text-gray-300 ml-1">— 點擊以下鑽</span></div>
      <div class="grid grid-cols-2 gap-x-3 gap-y-1">
        <button
          v-for="r in REALMS"
          :key="r.id"
          @click="enterRealm(r.id)"
          class="flex items-center gap-1.5 text-[11px] hover:text-gray-900 transition text-left"
        >
          <span class="inline-block w-3 h-3 rounded-sm flex-shrink-0" :style="{ background: r.color }"></span>
          <span class="text-gray-700">{{ r.index }}. {{ r.name_zh }}</span>
        </button>
      </div>
    </div>

    <!-- Legend (drilled: spheres of selected realm) -->
    <div v-else class="absolute left-3 bottom-3 bg-white/95 backdrop-blur rounded-lg border border-gray-200 px-3 py-2 shadow-sm max-w-[320px]">
      <div class="flex items-center gap-2 mb-2">
        <button
          @click="exitRealm"
          class="text-[11px] text-gray-500 hover:text-gray-900 px-1.5 py-0.5 rounded border border-gray-200 hover:border-gray-400"
        >← 返回</button>
        <span class="text-[11px] text-gray-400">界域 {{ selectedRealmInfo?.index }}</span>
        <span class="text-[12px] font-semibold text-gray-900">{{ selectedRealmInfo?.name_zh }}</span>
      </div>
      <div class="grid grid-cols-1 gap-y-1">
        <div v-for="s in sphereLegendItems" :key="s.id" class="flex items-start gap-1.5 text-[11px]">
          <span class="inline-block w-3 h-3 rounded-sm flex-shrink-0 mt-0.5" :style="{ background: s.color }"></span>
          <span class="text-gray-700">{{ s.name_zh }}</span>
        </div>
      </div>
      <div class="text-[10px] text-gray-400 mt-2 leading-relaxed">點國家／行政區看名稱；點海洋空白處退回八大界域</div>
    </div>

    <div v-if="selectedRealm" class="absolute right-14 top-3 bg-white/95 backdrop-blur rounded-lg border border-gray-200 px-2.5 py-1 shadow-sm">
      <button
        @click="exitRealm"
        class="text-[11px] text-gray-500 hover:text-gray-900 flex items-center gap-1"
      >
        <span>↩</span> 返回八大界域
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { geoNaturalEarth1, geoPath, geoCentroid } from 'd3-geo'
import { zoom as d3zoom, zoomIdentity, type ZoomBehavior } from 'd3-zoom'
import { select } from 'd3-selection'
import {
  REALMS,
  SPHERES,
  COUNTRY_REALM,
  COUNTRY_NAME_ZH,
  COUNTRIES_USING_ADMIN1,
  ADMIN1_SPHERE,
  ADMIN1_NAME_ZH,
  realmById,
  spheresByRealm,
  spheresForCountry,
  primarySphereForCountryInRealm,
  sphereForAdmin1,
  sphereColorsByRealm,
  type Realm,
  type RealmId,
  type CulturalSphere,
} from '~/data/maps/world-religions'

const rootEl = ref<HTMLElement | null>(null)
const svgEl = ref<SVGSVGElement | null>(null)
const width = ref(1200)
const height = ref(620)
const loading = ref(true)
const selectedRealm = ref<RealmId | null>(null)

const transform = ref({ k: 1, x: 0, y: 0 })
let zoomBehavior: ZoomBehavior<SVGSVGElement, unknown> | null = null

interface PathItem {
  id: string
  d: string
  fill: string
  opacity: number
  strokeBase: number
  isAdmin1: boolean
  realm?: Realm
  title: string
  spheres: { name: string; note?: string }[]
}

interface LabelItem {
  id: string
  x: number
  y: number
  /** original anchor (centroid) for drawing leader line if displaced */
  anchorX: number
  anchorY: number
  text: string
  fontSize: number
  /** true if label was pushed away from anchor (draw leader line) */
  hasLeader: boolean
}

interface FeatureEntry {
  feature: any
  isAdmin1: boolean
  key: string
  countryCode: string
}

const featureEntries = ref<FeatureEntry[]>([])
const paths = ref<PathItem[]>([])
const realmLabels = ref<LabelItem[]>([])
const sphereLabels = ref<LabelItem[]>([])

const selectedFeature = ref<PathItem | null>(null)

const selectedRealmInfo = computed<Realm | undefined>(() =>
  selectedRealm.value ? realmById(selectedRealm.value) : undefined
)

const sphereLegendItems = computed(() => {
  if (!selectedRealm.value) return []
  const colors = sphereColorsByRealm(selectedRealm.value)
  return spheresByRealm(selectedRealm.value).map(s => ({
    id: s.id,
    name_zh: s.name_zh,
    color: colors[s.id],
  }))
})

function getAdm0Code(props: any): string {
  const iso = props.ISO_A3
  if (iso && iso !== '-99') return iso
  return props.ADM0_A3 || ''
}

function describeEntry(entry: FeatureEntry, drilling: RealmId | null) {
  let realm: Realm | undefined
  let sphere: CulturalSphere | undefined
  let title = ''
  const spheresList: { name: string; note?: string }[] = []

  if (entry.isAdmin1) {
    sphere = sphereForAdmin1(entry.key, entry.countryCode)
    realm = sphere ? realmById(sphere.realm_id) : undefined
    const cn = COUNTRY_NAME_ZH[entry.countryCode] || entry.feature.properties.adm0_a3 || ''
    const adminName = ADMIN1_NAME_ZH[entry.key] || entry.feature.properties.name || entry.key
    title = cn ? `${cn}・${adminName}` : adminName
    if (sphere) {
      const m = sphere.members.find(mm => mm.iso_a3 === entry.countryCode && mm.admin1)
        || sphere.members.find(mm => mm.iso_a3 === entry.countryCode)
      spheresList.push({ name: sphere.name_zh, note: m?.note })
    }
  } else {
    const code = entry.key
    const realmId = COUNTRY_REALM[code]
    realm = realmId ? realmById(realmId) : undefined
    title = COUNTRY_NAME_ZH[code] || entry.feature.properties.NAME || code
    const ss = spheresForCountry(code)
    for (const { sphere: s, member: m } of ss) {
      spheresList.push({ name: s.name_zh, note: m.note })
    }
    if (drilling && realmId === drilling) {
      sphere = primarySphereForCountryInRealm(code, drilling)
    }
  }

  return { realm, sphere, title, spheres: spheresList }
}

function makeProjection() {
  return geoNaturalEarth1()
    .fitSize([width.value, height.value - 20], { type: 'Sphere' } as any)
    .translate([width.value / 2, (height.value - 20) / 2 + 10])
}

function rebuildAll() {
  if (!featureEntries.value.length) return
  const projection = makeProjection()
  const path = geoPath(projection)

  const drilling = selectedRealm.value
  const sphereColors = drilling ? sphereColorsByRealm(drilling) : null

  paths.value = featureEntries.value
    .map((entry, i) => {
      const { realm, sphere, title, spheres } = describeEntry(entry, drilling)

      let fill = '#E5E7EB'
      let opacity = 1
      if (drilling) {
        if (realm?.id === drilling) {
          fill = sphere && sphereColors ? sphereColors[sphere.id] : (realm.color)
          opacity = 1
        } else {
          fill = realm ? realm.color : '#E5E7EB'
          opacity = 0.12
        }
      } else {
        fill = realm ? realm.color : '#E5E7EB'
        opacity = 1
      }

      const d = path(entry.feature as any) || ''
      return {
        id: `${entry.isAdmin1 ? 'a1' : 'a0'}-${entry.key || 'x'}-${i}`,
        d,
        fill,
        opacity,
        strokeBase: entry.isAdmin1 ? 0.25 : 0.5,
        isAdmin1: entry.isAdmin1,
        realm,
        title,
        spheres,
      } as PathItem
    })
    .filter(p => p.d)

  realmLabels.value = REALMS.map(r => {
    const xy = projection(r.label_lnglat)
    if (!xy) return null
    return {
      id: r.id, x: xy[0], y: xy[1], anchorX: xy[0], anchorY: xy[1],
      text: r.name_zh, fontSize: 17, hasLeader: false,
    }
  }).filter(Boolean) as LabelItem[]

  if (drilling) {
    const realmSpheres = spheresByRealm(drilling)
    sphereLabels.value = realmSpheres.map(s => {
      const matches = featureEntries.value.filter(e => {
        if (e.isAdmin1) {
          // explicit ADMIN1_SPHERE override wins; otherwise fall back to country default
          const matched = sphereForAdmin1(e.key, e.countryCode)
          return matched?.id === s.id
        }
        if (COUNTRIES_USING_ADMIN1.has(e.key)) return false
        return s.members.some(m => m.iso_a3 === e.key && !m.is_extension && !m.admin1)
      }).map(e => e.feature)
      if (!matches.length) return null
      let lng = 0, lat = 0
      try {
        const c = geoCentroid({ type: 'FeatureCollection', features: matches } as any)
        lng = c[0]; lat = c[1]
      } catch { return null }
      const xy = projection([lng, lat])
      if (!xy || isNaN(xy[0]) || isNaN(xy[1])) return null
      return {
        id: s.id, x: xy[0], y: xy[1], anchorX: xy[0], anchorY: xy[1],
        text: s.name_zh, fontSize: 12, hasLeader: false,
      }
    }).filter(Boolean) as LabelItem[]
    relaxLabelCollisions(sphereLabels.value)
  } else {
    sphereLabels.value = []
  }
}

/**
 * Push overlapping labels apart with simple iterative repulsion.
 * If a label gets displaced significantly, mark hasLeader so a thin line is drawn
 * from its original anchor (centroid) to the displaced position.
 */
function relaxLabelCollisions(labels: LabelItem[]) {
  if (labels.length < 2) return
  const PADDING = 6
  const ITER = 40
  const widthOf = (l: LabelItem) => l.text.length * l.fontSize * 1.05
  const heightOf = (l: LabelItem) => l.fontSize * 1.25
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
  // mark leader if displaced more than a few pixels from anchor
  for (const l of labels) {
    const dist = Math.hypot(l.x - l.anchorX, l.y - l.anchorY)
    l.hasLeader = dist > 6
  }
}

function enterRealm(id: RealmId) {
  selectedRealm.value = id
  selectedFeature.value = null
}

function exitRealm() {
  selectedRealm.value = null
  selectedFeature.value = null
}

function onCountryClick(p: PathItem, _ev: MouseEvent) {
  if (!p.realm) return
  if (selectedRealm.value) {
    // drilled view → toggle selection (does NOT exit drill)
    if (selectedFeature.value && selectedFeature.value.id === p.id) {
      selectedFeature.value = null
    } else {
      selectedFeature.value = p
    }
  } else {
    // default view → click drills into the country's realm
    selectedRealm.value = p.realm.id
  }
}

function onBackgroundClick() {
  // Two-step ESC via background (ocean) click:
  //   if a feature is selected → only deselect it
  //   else if drilled into a realm → exit drill (back to 8-realm view)
  if (selectedFeature.value) {
    selectedFeature.value = null
  } else if (selectedRealm.value) {
    selectedRealm.value = null
  }
}

// ----- Zoom controls -----

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

  // Initialize zoom behavior
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
    const [adm0Res, adm1Res, adm1ExtraRes] = await Promise.all([
      fetch('/maps/ne_50m_admin_0_countries.geojson'),
      fetch('/maps/ne_50m_admin_1_subset.geojson'),
      fetch('/maps/ne_10m_admin_1_extra.geojson'),
    ])
    const [adm0, adm1, adm1Extra] = await Promise.all([
      adm0Res.json(), adm1Res.json(), adm1ExtraRes.json(),
    ])

    const entries: FeatureEntry[] = []
    for (const f of adm0.features) {
      if (f.properties.ADM0_A3 === 'ATA') continue
      const code = getAdm0Code(f.properties)
      if (COUNTRIES_USING_ADMIN1.has(code)) continue
      entries.push({ feature: f, isAdmin1: false, key: code, countryCode: code })
    }
    for (const f of adm1.features) {
      const key = f.properties.iso_3166_2
      const country = f.properties.adm0_a3
      entries.push({ feature: f, isAdmin1: true, key, countryCode: country })
    }
    for (const f of adm1Extra.features) {
      const key = f.properties.iso_3166_2
      const country = f.properties.adm0_a3
      entries.push({ feature: f, isAdmin1: true, key, countryCode: country })
    }
    featureEntries.value = entries
    rebuildAll()
  } catch (e) {
    console.error('地圖資料載入失敗', e)
  } finally {
    loading.value = false
  }
})

onBeforeUnmount(() => {
  ro?.disconnect()
})

watch(selectedRealm, () => {
  rebuildAll()
})
</script>
