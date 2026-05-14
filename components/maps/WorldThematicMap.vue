<template>
  <div ref="rootEl" class="relative w-full h-full bg-slate-50 rounded-xl overflow-hidden">
    <svg
      :width="width"
      :height="height"
      :viewBox="`0 0 ${width} ${height}`"
      class="block"
      @mouseleave="hovered = null"
    >
      <rect :width="width" :height="height" fill="#F1F5F9" />

      <!-- countries -->
      <g v-if="paths.length">
        <path
          v-for="p in paths"
          :key="p.id"
          :d="p.d"
          :fill="p.fill"
          :fill-opacity="p.opacity"
          stroke="#FFFFFF"
          :stroke-width="0.4"
          class="cursor-pointer"
          style="transition: fill 200ms, fill-opacity 200ms;"
          @click="onCountryClick(p)"
          @mousemove="onHover($event, p)"
          @mouseenter="onHover($event, p)"
        />
      </g>

      <!-- Realm labels (default view) -->
      <g v-if="!selectedRealm && realmLabels.length" pointer-events="none">
        <g
          v-for="lbl in realmLabels"
          :key="lbl.id"
          :transform="`translate(${lbl.x},${lbl.y})`"
        >
          <text
            text-anchor="middle"
            :font-size="lbl.fontSize"
            font-weight="700"
            fill="#FFFFFF"
            stroke="rgba(0,0,0,0.55)"
            :stroke-width="lbl.fontSize * 0.18"
            paint-order="stroke fill"
            style="font-family: ui-sans-serif, system-ui;"
          >{{ lbl.text }}</text>
        </g>
      </g>

      <!-- Sphere labels (drilled view) -->
      <g v-else-if="selectedRealm && sphereLabels.length" pointer-events="none">
        <g
          v-for="lbl in sphereLabels"
          :key="lbl.id"
          :transform="`translate(${lbl.x},${lbl.y})`"
        >
          <text
            text-anchor="middle"
            :font-size="lbl.fontSize"
            font-weight="600"
            fill="#FFFFFF"
            stroke="rgba(0,0,0,0.55)"
            :stroke-width="lbl.fontSize * 0.2"
            paint-order="stroke fill"
            style="font-family: ui-sans-serif, system-ui;"
          >{{ lbl.text }}</text>
        </g>
      </g>
    </svg>

    <div v-if="loading" class="absolute inset-0 flex items-center justify-center text-gray-400 text-sm">
      載入世界地圖中…
    </div>

    <!-- Tooltip -->
    <div
      v-if="hovered"
      class="pointer-events-none absolute z-10 px-3 py-2 bg-white border border-gray-200 rounded-lg shadow-md text-xs text-gray-800 max-w-[280px]"
      :style="{ left: tooltipPos.x + 'px', top: tooltipPos.y + 'px' }"
    >
      <div class="font-semibold text-sm mb-1">{{ hovered.nameZh || hovered.nameEn }}</div>
      <div v-if="hovered.realm" class="flex items-center gap-1.5 mb-1">
        <span class="inline-block w-2.5 h-2.5 rounded-sm" :style="{ background: hovered.realm.color }"></span>
        <span class="text-gray-600">{{ hovered.realm.index }}. {{ hovered.realm.name_zh }}</span>
      </div>
      <div v-if="hovered.spheres.length" class="text-gray-500 text-[11px] leading-relaxed mt-1">
        <div v-for="s in hovered.spheres" :key="s.sphere.id">
          · {{ s.sphere.name_zh }}<span v-if="s.member.note" class="text-gray-400"> — {{ s.member.note }}</span>
        </div>
      </div>
    </div>

    <!-- Legend (default: 8 realms) -->
    <div v-if="!selectedRealm" class="absolute left-3 bottom-3 bg-white/95 backdrop-blur rounded-lg border border-gray-200 px-3 py-2 shadow-sm">
      <div class="text-[11px] text-gray-500 mb-1.5 font-medium">八大界域<span class="text-gray-300 ml-1">— 點擊以下鑽</span></div>
      <div class="grid grid-cols-2 gap-x-3 gap-y-1">
        <button
          v-for="r in REALMS"
          :key="r.id"
          @click="selectedRealm = r.id"
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
          @click="selectedRealm = null"
          class="text-[11px] text-gray-500 hover:text-gray-900 px-1.5 py-0.5 rounded border border-gray-200 hover:border-gray-400"
        >← 返回</button>
        <span class="text-[11px] text-gray-400">界域 {{ selectedRealmInfo?.index }}</span>
        <span class="text-[12px] font-semibold text-gray-900">{{ selectedRealmInfo?.name_zh }}</span>
      </div>
      <div class="grid grid-cols-1 gap-y-1">
        <div
          v-for="s in sphereLegendItems"
          :key="s.id"
          class="flex items-start gap-1.5 text-[11px]"
        >
          <span class="inline-block w-3 h-3 rounded-sm flex-shrink-0 mt-0.5" :style="{ background: s.color }"></span>
          <span class="text-gray-700">{{ s.name_zh }}</span>
        </div>
      </div>
    </div>

    <!-- Top-right hint -->
    <div v-if="selectedRealm" class="absolute right-3 top-3 bg-white/95 backdrop-blur rounded-lg border border-gray-200 px-2.5 py-1 shadow-sm">
      <button
        @click="selectedRealm = null"
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
import {
  REALMS,
  SPHERES,
  COUNTRY_REALM,
  realmById,
  spheresByRealm,
  spheresForCountry,
  primarySphereForCountryInRealm,
  sphereColorsByRealm,
  type Realm,
  type RealmId,
  type CulturalSphere,
  type Member,
} from '~/data/maps/world-religions'

const rootEl = ref<HTMLElement | null>(null)
const width = ref(1200)
const height = ref(620)
const loading = ref(true)
const selectedRealm = ref<RealmId | null>(null)

interface PathItem {
  id: string
  d: string
  fill: string
  opacity: number
  code: string
  nameZh: string
  nameEn: string
  realm?: Realm
  spheres: { sphere: CulturalSphere; member: Member }[]
}

interface LabelItem {
  id: string
  x: number
  y: number
  text: string
  fontSize: number
}

const features = ref<any[]>([])
const paths = ref<PathItem[]>([])
const realmLabels = ref<LabelItem[]>([])
const sphereLabels = ref<LabelItem[]>([])

const hovered = ref<PathItem | null>(null)
const tooltipPos = ref({ x: 0, y: 0 })

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

function getCode(props: any): string {
  const iso = props.ISO_A3
  if (iso && iso !== '-99') return iso
  return props.ADM0_A3 || ''
}

function makeProjection() {
  return geoNaturalEarth1()
    .fitSize([width.value, height.value - 20], { type: 'Sphere' } as any)
    .translate([width.value / 2, (height.value - 20) / 2 + 10])
}

function rebuildAll() {
  if (!features.value.length) return
  const projection = makeProjection()
  const path = geoPath(projection)

  // ----- Paths -----
  const drilling = selectedRealm.value
  const sphereColors = drilling ? sphereColorsByRealm(drilling) : null

  paths.value = features.value
    .map((f, i) => {
      const code = getCode(f.properties)
      const realmId = COUNTRY_REALM[code]
      const realm = realmId ? realmById(realmId) : undefined
      const spheres = spheresForCountry(code)

      let fill = '#E5E7EB'
      let opacity = 1
      if (drilling) {
        if (realmId === drilling) {
          const sphere = primarySphereForCountryInRealm(code, drilling)
          fill = sphere && sphereColors ? sphereColors[sphere.id] : (realm?.color ?? '#9CA3AF')
          opacity = 1
        } else {
          fill = realm ? realm.color : '#E5E7EB'
          opacity = 0.12
        }
      } else {
        fill = realm ? realm.color : '#E5E7EB'
        opacity = 1
      }

      return {
        id: `${code || 'x'}-${i}`,
        d: path(f as any) || '',
        fill,
        opacity,
        code,
        nameZh: f.properties.NAME_ZH || f.properties.NAME || '',
        nameEn: f.properties.NAME || '',
        realm,
        spheres,
      } as PathItem
    })
    .filter(p => p.d)

  // ----- Realm labels (default view) -----
  realmLabels.value = REALMS.map(r => {
    const xy = projection(r.label_lnglat)
    if (!xy) return null
    return { id: r.id, x: xy[0], y: xy[1], text: r.name_zh, fontSize: 17 }
  }).filter(Boolean) as LabelItem[]

  // ----- Sphere labels (drilled view) -----
  if (drilling) {
    const realmSpheres = spheresByRealm(drilling)
    sphereLabels.value = realmSpheres.map(s => {
      // collect features whose code matches a member of this sphere
      const memberCodes = new Set(s.members.map(m => m.iso_a3))
      const matches = features.value.filter(f => memberCodes.has(getCode(f.properties)))
      if (!matches.length) return null
      let lng = 0, lat = 0
      try {
        const c = geoCentroid({ type: 'FeatureCollection', features: matches } as any)
        lng = c[0]
        lat = c[1]
      } catch {
        return null
      }
      const xy = projection([lng, lat])
      if (!xy || isNaN(xy[0]) || isNaN(xy[1])) return null
      return { id: s.id, x: xy[0], y: xy[1], text: s.name_zh, fontSize: 12 }
    }).filter(Boolean) as LabelItem[]
  } else {
    sphereLabels.value = []
  }
}

function onHover(ev: MouseEvent, p: PathItem) {
  hovered.value = p
  const rect = rootEl.value?.getBoundingClientRect()
  if (!rect) return
  let x = ev.clientX - rect.left + 12
  let y = ev.clientY - rect.top + 12
  if (x + 280 > width.value) x = ev.clientX - rect.left - 290
  if (y + 120 > height.value) y = ev.clientY - rect.top - 130
  tooltipPos.value = { x, y }
}

function onCountryClick(p: PathItem) {
  if (!p.realm) return
  // toggle: clicking a country in selected realm exits drill; else drill into its realm
  if (selectedRealm.value === p.realm.id) {
    selectedRealm.value = null
  } else {
    selectedRealm.value = p.realm.id
  }
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

  try {
    const res = await fetch('/maps/ne_50m_admin_0_countries.geojson')
    const gj = await res.json()
    features.value = gj.features.filter((f: any) => f.properties.ADM0_A3 !== 'ATA')
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

watch(selectedRealm, () => rebuildAll())
</script>
