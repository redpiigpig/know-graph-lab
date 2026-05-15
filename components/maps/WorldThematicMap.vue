<template>
  <div ref="rootEl" class="relative w-full h-full bg-slate-50 rounded-xl overflow-hidden">
    <svg
      ref="svgEl"
      :width="width"
      :height="height"
      :viewBox="`0 0 ${width} ${height}`"
      class="block select-none"
      :class="addAnchorFor ? 'cursor-crosshair' : 'cursor-default'"
    >
      <rect
        :width="width"
        :height="height"
        fill="#F1F5F9"
        @click="onBackgroundClick($event)"
      />

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
        <g v-else-if="selectedRealm && sphereLabels.length">
          <!-- Leader lines (from anchor + every extra anchor → label) -->
          <g pointer-events="none">
            <template v-for="lbl in sphereLabels" :key="`leaders-${lbl.id}`">
              <line
                v-if="lbl.hasLeader"
                :x1="lbl.anchorX"
                :y1="lbl.anchorY"
                :x2="lbl.x"
                :y2="lbl.y"
                stroke="rgba(15,23,42,0.55)"
                :stroke-width="0.8 / transform.k"
              />
              <line
                v-for="(a, ai) in lbl.extraAnchors"
                :key="`extra-leader-${lbl.id}-${ai}`"
                :x1="a.x"
                :y1="a.y"
                :x2="lbl.x"
                :y2="lbl.y"
                stroke="rgba(15,23,42,0.55)"
                :stroke-width="0.8 / transform.k"
              />
              <circle
                v-if="lbl.hasLeader"
                :cx="lbl.anchorX"
                :cy="lbl.anchorY"
                :r="1.6 / transform.k"
                fill="rgba(15,23,42,0.7)"
              />
            </template>
          </g>

          <!-- Extra anchor dots — clickable to remove in editMode -->
          <g v-if="editMode">
            <circle
              v-for="dot in extraAnchorDots"
              :key="dot.key"
              :cx="dot.x"
              :cy="dot.y"
              :r="4 / transform.k"
              fill="#DC2626"
              stroke="#FFFFFF"
              :stroke-width="1 / transform.k"
              class="cursor-pointer"
              @click.stop="removeExtraAnchor(dot.sphereId, dot.idx)"
            />
          </g>

          <!-- Labels (text + drag handle) -->
          <g v-for="lbl in sphereLabels" :key="lbl.id" :transform="`translate(${lbl.x},${lbl.y})`">
            <!-- editMode: subtle dashed background as drag affordance -->
            <rect
              v-if="editMode"
              :x="-(lbl.text.length * lbl.fontSize * 0.55) / transform.k"
              :y="-(lbl.fontSize * 0.7) / transform.k"
              :width="(lbl.text.length * lbl.fontSize * 1.1) / transform.k"
              :height="(lbl.fontSize * 1.4) / transform.k"
              fill="rgba(255,255,255,0.001)"
              stroke="rgba(15,23,42,0.4)"
              stroke-dasharray="3 2"
              :stroke-width="0.6 / transform.k"
              class="cursor-move"
              @mousedown.stop="startDrag($event, lbl)"
            />
            <text
              text-anchor="middle"
              :font-size="lbl.fontSize / transform.k"
              font-weight="600"
              fill="#FFFFFF"
              stroke="rgba(0,0,0,0.6)"
              :stroke-width="(lbl.fontSize * 0.2) / transform.k"
              paint-order="stroke fill"
              :class="editMode ? 'cursor-move' : ''"
              style="font-family: ui-sans-serif, system-ui;"
              :pointer-events="editMode ? 'all' : 'none'"
              @mousedown.stop="editMode && startDrag($event, lbl)"
            >{{ lbl.text }}</text>
            <!-- "+" button to add another leader line in editMode -->
            <text
              v-if="editMode"
              :x="(lbl.text.length * lbl.fontSize * 0.6 + 6) / transform.k"
              y="0"
              text-anchor="start"
              :font-size="(lbl.fontSize * 0.95) / transform.k"
              fill="#0F172A"
              stroke="#FFFFFF"
              :stroke-width="(lbl.fontSize * 0.25) / transform.k"
              paint-order="stroke fill"
              class="cursor-pointer"
              :pointer-events="'all'"
              dominant-baseline="middle"
              @click.stop="enterAddAnchor(lbl.id)"
            >＋線</text>
          </g>
        </g>
      </g>
    </svg>

    <div v-if="loading" class="absolute inset-0 flex items-center justify-center text-gray-400 text-sm">
      載入世界地圖中…
    </div>

    <!-- Selected feature info -->
    <div
      v-if="selectedFeature && selectedRealm && !editMode"
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
        <div v-for="(s, i) in selectedFeature.spheres" :key="i">· {{ s.name }}</div>
      </div>
    </div>

    <!-- Add-anchor banner -->
    <div
      v-if="addAnchorFor && addAnchorTargetName"
      class="absolute left-1/2 top-3 -translate-x-1/2 z-10 bg-amber-50 border border-amber-300 rounded-lg shadow-md px-3 py-1.5 text-xs text-amber-900 flex items-center gap-2"
    >
      <span>點地圖任一處作為「{{ addAnchorTargetName }}」的新引線錨點</span>
      <button @click="addAnchorFor = null" class="text-amber-600 hover:text-amber-900 text-base leading-none">×</button>
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

    <!-- Legend (drilled) -->
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
      <div class="text-[10px] text-gray-400 mt-2 leading-relaxed">
        {{ editMode ? '拖標籤調位置；＋線可新增引線；點紅錨刪除' : '點國家／行政區看名稱；點海洋退回八大界域' }}
      </div>
    </div>

    <!-- Top-right toolbar (drilled view): edit toggle / reset / back -->
    <div v-if="selectedRealm" class="absolute right-3 top-3 flex items-center gap-2">
      <button
        v-if="editMode"
        @click="resetCurrentRealmOverrides"
        class="bg-white/95 backdrop-blur rounded-lg border border-gray-200 px-2.5 py-1 shadow-sm text-[11px] text-gray-500 hover:text-gray-900"
      >↺ 重置位置</button>
      <button
        @click="toggleEditMode"
        class="bg-white/95 backdrop-blur rounded-lg border px-2.5 py-1 shadow-sm text-[11px] flex items-center gap-1"
        :class="editMode ? 'border-amber-400 text-amber-700 bg-amber-50' : 'border-gray-200 text-gray-500 hover:text-gray-900'"
      >
        <span>{{ editMode ? '✓' : '✏️' }}</span> 編輯標籤
      </button>
      <button
        @click="exitRealm"
        class="bg-white/95 backdrop-blur rounded-lg border border-gray-200 px-2.5 py-1 shadow-sm text-[11px] text-gray-500 hover:text-gray-900 flex items-center gap-1"
      >
        <span>↩</span> 返回八大界域
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { geoNaturalEarth1, geoPath, geoCentroid, type GeoProjection } from 'd3-geo'
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
  anchorX: number
  anchorY: number
  text: string
  fontSize: number
  hasLeader: boolean
  /** Additional anchors (each draws its own leader line). User-added in editMode. */
  extraAnchors: { x: number; y: number }[]
  /** True if user manually moved the label position. Skip auto-collision relax. */
  isLockedByUser: boolean
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

// ----- Edit mode + label overrides -----
type LabelOverride = { lnglat?: [number, number]; extraAnchors?: [number, number][] }
type Overrides = Record<string, Record<string, LabelOverride>>
const STORAGE_KEY = 'maps:wr:label-overrides:v1'
const overrides = ref<Overrides>({})
const editMode = ref(false)
const addAnchorFor = ref<string | null>(null)  // sphere id awaiting anchor click

let projectionCache: GeoProjection | null = null

function loadOverrides() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    overrides.value = raw ? JSON.parse(raw) : {}
  } catch { overrides.value = {} }
}
function saveOverrides() {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(overrides.value)) } catch {}
}
function getOverride(realmId: string, sphereId: string): LabelOverride {
  return overrides.value[realmId]?.[sphereId] || {}
}
function setOverridePosition(realmId: string, sphereId: string, lnglat: [number, number]) {
  if (!overrides.value[realmId]) overrides.value[realmId] = {}
  if (!overrides.value[realmId][sphereId]) overrides.value[realmId][sphereId] = {}
  overrides.value[realmId][sphereId].lnglat = lnglat
  saveOverrides()
  rebuildAll()
}
function addExtraAnchor(realmId: string, sphereId: string, lnglat: [number, number]) {
  if (!overrides.value[realmId]) overrides.value[realmId] = {}
  if (!overrides.value[realmId][sphereId]) overrides.value[realmId][sphereId] = {}
  const list = overrides.value[realmId][sphereId].extraAnchors || []
  list.push(lnglat)
  overrides.value[realmId][sphereId].extraAnchors = list
  saveOverrides()
  rebuildAll()
}
function removeExtraAnchor(sphereId: string, idx: number) {
  const realmId = selectedRealm.value
  if (!realmId) return
  const ovr = overrides.value[realmId]?.[sphereId]
  if (!ovr?.extraAnchors) return
  ovr.extraAnchors.splice(idx, 1)
  if (!ovr.extraAnchors.length) delete ovr.extraAnchors
  saveOverrides()
  rebuildAll()
}
function resetCurrentRealmOverrides() {
  const realmId = selectedRealm.value
  if (!realmId) return
  delete overrides.value[realmId]
  saveOverrides()
  rebuildAll()
}

function toggleEditMode() {
  editMode.value = !editMode.value
  if (!editMode.value) addAnchorFor.value = null
  if (editMode.value) selectedFeature.value = null
}

const addAnchorTargetName = computed(() => {
  if (!addAnchorFor.value) return ''
  const sp = SPHERES.find(s => s.id === addAnchorFor.value)
  return sp?.name_zh || ''
})

const extraAnchorDots = computed(() => {
  const out: { key: string; x: number; y: number; sphereId: string; idx: number }[] = []
  for (const lbl of sphereLabels.value) {
    lbl.extraAnchors.forEach((a, i) => {
      out.push({ key: `${lbl.id}-${i}`, x: a.x, y: a.y, sphereId: lbl.id, idx: i })
    })
  }
  return out
})

function enterAddAnchor(sphereId: string) {
  addAnchorFor.value = sphereId
}

const selectedRealmInfo = computed<Realm | undefined>(() =>
  selectedRealm.value ? realmById(selectedRealm.value) : undefined
)

const sphereLegendItems = computed(() => {
  if (!selectedRealm.value) return []
  const colors = sphereColorsByRealm(selectedRealm.value)
  return spheresByRealm(selectedRealm.value).map(s => ({
    id: s.id, name_zh: s.name_zh, color: colors[s.id],
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

function makeProjection(): GeoProjection {
  const p = geoNaturalEarth1()
    .fitSize([width.value, height.value - 20], { type: 'Sphere' } as any)
    .translate([width.value / 2, (height.value - 20) / 2 + 10])
  projectionCache = p
  return p
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
      const isOverlayOnAdmin0 = entry.isAdmin1 && !COUNTRIES_USING_ADMIN1.has(entry.countryCode)
      let fill = '#E5E7EB'
      let opacity = 1
      if (drilling) {
        if (realm?.id === drilling) {
          fill = sphere && sphereColors ? sphereColors[sphere.id] : (realm.color)
          opacity = 1
        } else {
          fill = realm ? realm.color : '#E5E7EB'
          opacity = isOverlayOnAdmin0 ? 1 : 0.12
        }
      } else {
        fill = realm ? realm.color : '#E5E7EB'
        opacity = 1
      }
      const d = path(entry.feature as any) || ''
      return {
        id: `${entry.isAdmin1 ? 'a1' : 'a0'}-${entry.key || 'x'}-${i}`,
        d, fill, opacity,
        strokeBase: entry.isAdmin1 ? 0.25 : 0.5,
        isAdmin1: entry.isAdmin1,
        realm, title, spheres,
      } as PathItem
    })
    .filter(p => p.d)

  realmLabels.value = REALMS.map(r => {
    const xy = projection(r.label_lnglat)
    if (!xy) return null
    return {
      id: r.id, x: xy[0], y: xy[1], anchorX: xy[0], anchorY: xy[1],
      text: r.name_zh, fontSize: 17, hasLeader: false,
      extraAnchors: [], isLockedByUser: false,
    }
  }).filter(Boolean) as LabelItem[]

  if (drilling) {
    const realmSpheres = spheresByRealm(drilling)
    sphereLabels.value = realmSpheres.map(s => {
      const matches = featureEntries.value.filter(e => {
        if (e.isAdmin1) {
          const matched = sphereForAdmin1(e.key, e.countryCode)
          return matched?.id === s.id
        }
        if (COUNTRIES_USING_ADMIN1.has(e.key)) return false
        return s.members.some(m => m.iso_a3 === e.key && !m.is_extension && !m.admin1)
      }).map(e => e.feature)
      if (!matches.length) return null
      let anchorLng = 0, anchorLat = 0
      try {
        const c = geoCentroid({ type: 'FeatureCollection', features: matches } as any)
        anchorLng = c[0]; anchorLat = c[1]
      } catch { return null }
      const anchorXy = projection([anchorLng, anchorLat])
      if (!anchorXy || isNaN(anchorXy[0]) || isNaN(anchorXy[1])) return null

      // Display position priority: user override > sphere.label_lnglat hardcode > centroid
      const ovr = getOverride(drilling, s.id)
      let displayXy = anchorXy
      let userLocked = false
      if (ovr.lnglat) {
        const p = projection(ovr.lnglat)
        if (p && !isNaN(p[0]) && !isNaN(p[1])) { displayXy = p; userLocked = true }
      } else if (s.label_lnglat) {
        const p = projection(s.label_lnglat)
        if (p && !isNaN(p[0]) && !isNaN(p[1])) displayXy = p
      }

      // Project user-added extra anchors
      const extraAnchors: { x: number; y: number }[] = []
      if (ovr.extraAnchors) {
        for (const ll of ovr.extraAnchors) {
          const p = projection(ll)
          if (p && !isNaN(p[0]) && !isNaN(p[1])) extraAnchors.push({ x: p[0], y: p[1] })
        }
      }

      return {
        id: s.id, x: displayXy[0], y: displayXy[1],
        anchorX: anchorXy[0], anchorY: anchorXy[1],
        text: s.name_zh, fontSize: 12, hasLeader: false,
        extraAnchors, isLockedByUser: userLocked,
      } as LabelItem
    }).filter(Boolean) as LabelItem[]

    // Mark hardcoded/user displaced labels as having leaders
    for (const l of sphereLabels.value) {
      if (Math.hypot(l.x - l.anchorX, l.y - l.anchorY) > 6) l.hasLeader = true
    }
    // Auto-relax overlapping (skip user-locked labels)
    relaxLabelCollisions(sphereLabels.value)
  } else {
    sphereLabels.value = []
  }
}

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
            if (!a.isLockedByUser) a.x += push
            if (!b.isLockedByUser) b.x -= push
          } else {
            const push = overlapY / 2 * (dy >= 0 ? 1 : -1)
            if (!a.isLockedByUser) a.y += push
            if (!b.isLockedByUser) b.y -= push
          }
          moved = true
        }
      }
    }
    if (!moved) break
  }
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
  editMode.value = false
  addAnchorFor.value = null
}

function eventToLngLat(e: MouseEvent): [number, number] | null {
  if (!svgEl.value || !projectionCache) return null
  const rect = svgEl.value.getBoundingClientRect()
  const sx = e.clientX - rect.left
  const sy = e.clientY - rect.top
  const ux = (sx - transform.value.x) / transform.value.k
  const uy = (sy - transform.value.y) / transform.value.k
  const ll = projectionCache.invert?.([ux, uy])
  if (!ll || isNaN(ll[0]) || isNaN(ll[1])) return null
  return [ll[0], ll[1]]
}

function onCountryClick(p: PathItem, ev: MouseEvent) {
  if (addAnchorFor.value && selectedRealm.value) {
    const ll = eventToLngLat(ev)
    if (ll) addExtraAnchor(selectedRealm.value, addAnchorFor.value, ll)
    addAnchorFor.value = null
    return
  }
  if (!p.realm) return
  if (selectedRealm.value) {
    if (editMode.value) return  // ignore feature select while editing
    if (selectedFeature.value && selectedFeature.value.id === p.id) {
      selectedFeature.value = null
    } else {
      selectedFeature.value = p
    }
  } else {
    selectedRealm.value = p.realm.id
  }
}

function onBackgroundClick(ev: MouseEvent) {
  if (addAnchorFor.value && selectedRealm.value) {
    const ll = eventToLngLat(ev)
    if (ll) addExtraAnchor(selectedRealm.value, addAnchorFor.value, ll)
    addAnchorFor.value = null
    return
  }
  if (selectedFeature.value) {
    selectedFeature.value = null
  } else if (selectedRealm.value) {
    selectedRealm.value = null
    editMode.value = false
  }
}

// ----- Drag label -----
let dragState: { lbl: LabelItem; startCx: number; startCy: number; startLx: number; startLy: number } | null = null

function startDrag(e: MouseEvent, lbl: LabelItem) {
  if (!editMode.value) return
  e.preventDefault()
  e.stopPropagation()
  dragState = { lbl, startCx: e.clientX, startCy: e.clientY, startLx: lbl.x, startLy: lbl.y }
  window.addEventListener('mousemove', onDragMove)
  window.addEventListener('mouseup', endDrag)
}
function onDragMove(e: MouseEvent) {
  if (!dragState) return
  const dx = (e.clientX - dragState.startCx) / transform.value.k
  const dy = (e.clientY - dragState.startCy) / transform.value.k
  dragState.lbl.x = dragState.startLx + dx
  dragState.lbl.y = dragState.startLy + dy
  dragState.lbl.isLockedByUser = true
  dragState.lbl.hasLeader = Math.hypot(dragState.lbl.x - dragState.lbl.anchorX, dragState.lbl.y - dragState.lbl.anchorY) > 6
}
function endDrag() {
  window.removeEventListener('mousemove', onDragMove)
  window.removeEventListener('mouseup', endDrag)
  if (!dragState || !projectionCache || !selectedRealm.value) { dragState = null; return }
  const ll = projectionCache.invert?.([dragState.lbl.x, dragState.lbl.y])
  if (ll && !isNaN(ll[0]) && !isNaN(ll[1])) {
    setOverridePosition(selectedRealm.value, dragState.lbl.id, [ll[0], ll[1]])
  }
  dragState = null
}

// ----- Zoom -----
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
  loadOverrides()
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
    .filter((event: any) => {
      // Disable d3-zoom drag while in editMode (so label drag works without conflict)
      // Always allow wheel zoom
      if (event.type === 'wheel') return true
      if (editMode.value) return false
      return !event.ctrlKey && !event.button
    })
    .on('zoom', (event: any) => {
      applyZoomTransform({ k: event.transform.k, x: event.transform.x, y: event.transform.y })
    })
  if (svgEl.value) {
    select(svgEl.value).call(zoomBehavior as any)
  }

  try {
    const [adm0Res, adm1Res, adm1ExtraRes, prefRes] = await Promise.all([
      fetch('/maps/ne_50m_admin_0_countries.geojson'),
      fetch('/maps/ne_50m_admin_1_subset.geojson'),
      fetch('/maps/ne_10m_admin_1_extra.geojson'),
      fetch('/maps/cn_tibetan_prefectures.geojson'),
    ])
    const [adm0, adm1, adm1Extra, pref] = await Promise.all([
      adm0Res.json(), adm1Res.json(), adm1ExtraRes.json(), prefRes.json(),
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
    for (const f of pref.features) {
      const key = `gadm:${f.properties.GID_2}`
      const country = f.properties.GID_0
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
  window.removeEventListener('mousemove', onDragMove)
  window.removeEventListener('mouseup', endDrag)
})

watch(selectedRealm, () => rebuildAll())
watch(editMode, () => {
  // No need to rebuild paths but template re-renders due to reactive changes.
})
</script>
