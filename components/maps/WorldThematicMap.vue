<template>
  <div ref="rootEl" class="relative w-full h-full bg-slate-50 rounded-xl overflow-hidden">
    <svg
      :width="width"
      :height="height"
      :viewBox="`0 0 ${width} ${height}`"
      class="block"
      @mouseleave="hovered = null"
    >
      <!-- ocean / background -->
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
          class="cursor-pointer transition-opacity duration-150"
          @mousemove="onHover($event, p)"
          @mouseenter="onHover($event, p)"
        />
      </g>

      <!-- graticule (optional subtle) -->
    </svg>

    <!-- Loading -->
    <div v-if="loading" class="absolute inset-0 flex items-center justify-center text-gray-400 text-sm">
      載入世界地圖中…
    </div>

    <!-- Tooltip -->
    <div
      v-if="hovered"
      class="pointer-events-none absolute z-10 px-3 py-2 bg-white border border-gray-200 rounded-lg shadow-md text-xs text-gray-800"
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

    <!-- Legend -->
    <div class="absolute left-3 bottom-3 bg-white/95 backdrop-blur rounded-lg border border-gray-200 px-3 py-2 shadow-sm">
      <div class="text-[11px] text-gray-500 mb-1.5 font-medium">八大界域</div>
      <div class="grid grid-cols-2 gap-x-3 gap-y-1">
        <button
          v-for="r in REALMS"
          :key="r.id"
          @click="toggleRealm(r.id)"
          class="flex items-center gap-1.5 text-[11px] hover:text-gray-900 transition"
          :class="activeRealm && activeRealm !== r.id ? 'opacity-40' : 'text-gray-700'"
        >
          <span class="inline-block w-3 h-3 rounded-sm" :style="{ background: r.color }"></span>
          <span>{{ r.index }}. {{ r.name_zh }}</span>
        </button>
      </div>
      <button
        v-if="activeRealm"
        @click="activeRealm = null"
        class="mt-1.5 text-[10px] text-gray-400 hover:text-gray-700"
      >
        清除篩選
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { geoNaturalEarth1, geoPath } from 'd3-geo'
import {
  REALMS,
  COUNTRY_REALM,
  realmById,
  spheresForCountry,
  type Realm,
  type RealmId,
  type CulturalSphere,
  type Member,
} from '~/data/maps/world-religions'

const rootEl = ref<HTMLElement | null>(null)
const width = ref(1200)
const height = ref(620)
const loading = ref(true)
const activeRealm = ref<RealmId | null>(null)

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

const features = ref<any[]>([])
const paths = ref<PathItem[]>([])

const hovered = ref<PathItem | null>(null)
const tooltipPos = ref({ x: 0, y: 0 })

function onHover(ev: MouseEvent, p: PathItem) {
  hovered.value = p
  const rect = rootEl.value?.getBoundingClientRect()
  if (!rect) return
  let x = ev.clientX - rect.left + 12
  let y = ev.clientY - rect.top + 12
  // keep tooltip inside container
  if (x + 280 > width.value) x = ev.clientX - rect.left - 290
  if (y + 120 > height.value) y = ev.clientY - rect.top - 130
  tooltipPos.value = { x, y }
}

function toggleRealm(id: RealmId) {
  activeRealm.value = activeRealm.value === id ? null : id
}

function getCode(props: any): string {
  // ISO_A3 takes precedence unless invalid (-99), then fall back to ADM0_A3
  const iso = props.ISO_A3
  if (iso && iso !== '-99') return iso
  return props.ADM0_A3 || ''
}

function rebuildPaths() {
  if (!features.value.length) return
  const projection = geoNaturalEarth1()
    .fitSize([width.value, height.value - 20], { type: 'Sphere' } as any)
    .translate([width.value / 2, (height.value - 20) / 2 + 10])
  const path = geoPath(projection)

  paths.value = features.value
    .map((f, i) => {
      const code = getCode(f.properties)
      const realmId = COUNTRY_REALM[code]
      const realm = realmId ? realmById(realmId) : undefined
      const spheres = spheresForCountry(code)
      const isMuted = activeRealm.value && realmId !== activeRealm.value
      return {
        id: `${code || 'x'}-${i}`,
        d: path(f as any) || '',
        fill: realm ? realm.color : '#E5E7EB',
        opacity: isMuted ? 0.18 : 1,
        code,
        nameZh: f.properties.NAME_ZH || f.properties.NAME || '',
        nameEn: f.properties.NAME || '',
        realm,
        spheres,
      } as PathItem
    })
    .filter(p => p.d)
}

let ro: ResizeObserver | null = null

onMounted(async () => {
  // size
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
      rebuildPaths()
    }
  })
  ro.observe(rootEl.value!)

  try {
    const res = await fetch('/maps/ne_50m_admin_0_countries.geojson')
    const gj = await res.json()
    // skip Antarctica for tighter framing
    features.value = gj.features.filter((f: any) => f.properties.ADM0_A3 !== 'ATA')
    rebuildPaths()
  } catch (e) {
    console.error('地圖資料載入失敗', e)
  } finally {
    loading.value = false
  }
})

onBeforeUnmount(() => {
  ro?.disconnect()
})

watch(activeRealm, () => rebuildPaths())
</script>
