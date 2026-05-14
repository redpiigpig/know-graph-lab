<template>
  <div class="flex flex-col bg-slate-50" style="height: 100dvh;">
    <!-- Nav -->
    <nav class="flex items-center gap-2 px-4 h-12 bg-white border-b border-gray-100 flex-shrink-0 z-30">
      <NuxtLink to="/genealogy" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">聖經人物族譜圖</span>
      <span v-if="peopleCount" class="text-xs text-gray-400 ml-1">{{ peopleCount }} 人</span>
      <div class="flex-1" />

      <!-- 耶穌弟兄解 toggle -->
      <div class="flex items-center gap-0.5 bg-gray-100 rounded-lg p-0.5 mr-1">
        <span class="text-[10px] text-gray-400 px-1.5 select-none">耶穌弟兄</span>
        <button
          v-for="t in viewOptions"
          :key="t.value"
          class="text-xs px-2.5 py-1 rounded-md font-medium transition"
          :class="brothersView === t.value
            ? `bg-white shadow-sm ${t.activeColor}`
            : 'text-gray-500 hover:text-gray-700'"
          @click="setBrothersView(t.value)"
        >{{ t.label }}</button>
      </div>

      <!-- View link -->
      <div class="flex items-center gap-0.5 bg-gray-100 rounded-lg p-0.5">
        <NuxtLink
          to="/genealogy/biblical"
          class="text-xs px-2.5 py-1 rounded-md font-medium transition text-gray-500 hover:text-gray-700"
        >表格</NuxtLink>
        <span class="text-xs px-2.5 py-1 rounded-md font-medium bg-white shadow-sm text-gray-900">族譜圖</span>
      </div>
    </nav>

    <!-- 族譜圖 -->
    <div class="flex-1 min-h-0 relative">
      <ClientOnly>
        <GenealogyBiblicalSpineTree
          :nodes="graphNodes"
          :edges="graphEdges"
          @select-person="onSelectPerson"
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
useHead({ title: '聖經人物族譜圖 — Know Graph Lab' })

const supabase = useSupabaseClient()
const router   = useRouter()
const route    = useRoute()

async function getToken() {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session) { router.push('/login'); return null }
  return session.access_token
}

// 耶穌弟兄解（馬可 6:3 三派解）— protestant 預設。
type BrothersView = 'protestant' | 'catholic' | 'orthodox'
const brothersView = ref<BrothersView>(
  (['protestant', 'catholic', 'orthodox'].includes(route.query.view as string)
    ? route.query.view
    : 'protestant') as BrothersView
)

const viewOptions: Array<{ value: BrothersView; label: string; activeColor: string }> = [
  { value: 'protestant', label: '新教',   activeColor: 'text-gray-900' },
  { value: 'catholic',   label: '天主教', activeColor: 'text-purple-600' },
  { value: 'orthodox',   label: '東方',   activeColor: 'text-emerald-600' },
]

function setBrothersView(v: BrothersView) {
  brothersView.value = v
  router.replace({ query: { ...route.query, view: v === 'protestant' ? undefined : v } })
}

const graphNodes  = ref<any[]>([])
const graphEdges  = ref<any[]>([])
const peopleCount = computed(() => graphNodes.value.length)

async function loadGraph() {
  const token = await getToken()
  if (!token) return
  const qs = brothersView.value !== 'protestant' ? `?view=${brothersView.value}` : ''
  const { nodes, edges } = await $fetch<{ nodes: any[], edges: any[] }>('/api/genealogy/biblical-graph' + qs, {
    headers: { Authorization: `Bearer ${token}` },
  })
  graphNodes.value = nodes
  graphEdges.value = edges
}

watch(brothersView, loadGraph)

function onSelectPerson(id: string) {
  // Jump to table view for editing
  router.push({ path: '/genealogy/biblical', query: { edit: id } })
}

onMounted(loadGraph)
</script>
