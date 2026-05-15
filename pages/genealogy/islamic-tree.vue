<template>
  <div class="flex flex-col bg-slate-50" style="height: 100dvh;">
    <nav class="flex items-center gap-2 px-4 h-12 bg-white border-b border-gray-100 flex-shrink-0 z-30">
      <NuxtLink to="/genealogy" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">伊斯蘭族譜圖</span>
      <span v-if="peopleCount" class="text-xs text-gray-400 ml-1">{{ peopleCount }} 人</span>
      <div class="flex-1" />

      <div class="flex items-center gap-0.5 bg-gray-100 rounded-lg p-0.5">
        <NuxtLink
          to="/genealogy/islamic"
          class="text-xs px-2.5 py-1 rounded-md font-medium transition text-gray-500 hover:text-gray-700"
        >表格</NuxtLink>
        <span class="text-xs px-2.5 py-1 rounded-md font-medium bg-white shadow-sm text-gray-900">族譜圖</span>
      </div>
    </nav>

    <div class="flex-1 min-h-0 relative">
      <ClientOnly>
        <GenealogyIslamicSpineTree
          :nodes="graphNodes"
          :edges="graphEdges"
          :view="view"
          @select-person="onSelectPerson"
          @update:view="setView"
        />
        <template #fallback>
          <div class="absolute inset-0 flex items-center justify-center text-gray-300 text-sm">載入中…</div>
        </template>
      </ClientOnly>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
useHead({ title: '伊斯蘭族譜圖 — Know Graph Lab' })

const supabase = useSupabaseClient()
const router   = useRouter()
const route    = useRoute()

async function getToken() {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session) { router.push('/login'); return null }
  return session.access_token
}

type View = 'quranic' | 'sunni' | 'shia_twelver' | 'shia_ismaili' | 'shia_zaidi'
const ALLOWED: View[] = ['quranic', 'sunni', 'shia_twelver', 'shia_ismaili', 'shia_zaidi']
const view = ref<View>(
  (ALLOWED.includes(route.query.view as View) ? route.query.view : 'quranic') as View
)

function setView(v: View) {
  view.value = v
  router.replace({ query: { ...route.query, view: v === 'quranic' ? undefined : v } })
}

const graphNodes  = ref<any[]>([])
const graphEdges  = ref<any[]>([])
const peopleCount = computed(() => graphNodes.value.length)

async function loadGraph() {
  const token = await getToken()
  if (!token) return
  const qs = view.value !== 'quranic' ? `?view=${view.value}` : ''
  const { nodes, edges } = await $fetch<{ nodes: any[], edges: any[] }>('/api/genealogy/islamic-graph' + qs, {
    headers: { Authorization: `Bearer ${token}` },
  })
  graphNodes.value = nodes
  graphEdges.value = edges
}

watch(view, loadGraph)

function onSelectPerson(_id: string) {
  router.push({ path: '/genealogy/islamic' })
}

onMounted(loadGraph)
</script>
