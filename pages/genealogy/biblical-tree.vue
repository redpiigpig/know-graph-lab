<template>
  <div class="flex flex-col bg-slate-50" style="height: 100dvh;">
    <!-- Nav -->
    <nav class="flex items-center gap-2 px-4 h-12 bg-white border-b border-gray-100 flex-shrink-0 z-30">
      <NuxtLink to="/genealogy" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">聖經人物族譜圖</span>
      <span v-if="peopleCount" class="text-xs text-gray-400 ml-1">{{ peopleCount }} 人</span>
      <div class="flex-1" />

      <!-- 耶穌弟兄詮釋 toggle 已移至族譜圖內浮動 widget（局部按鈕） -->

      <!-- View link -->
      <div class="flex items-center gap-0.5 bg-gray-100 rounded-lg p-0.5">
        <NuxtLink
          to="/genealogy/biblical"
          class="text-xs px-2.5 py-1 rounded-md font-medium transition text-gray-500 hover:text-gray-700"
        >表格</NuxtLink>
        <span class="text-xs px-2.5 py-1 rounded-md font-medium bg-white shadow-sm text-gray-900">族譜圖</span>
      </div>
    </nav>

    <!-- 族譜圖（含浮動耶穌弟兄詮釋 toggle） -->
    <div class="flex-1 min-h-0 relative">
      <ClientOnly>
        <GenealogyBiblicalSpineTree
          :nodes="graphNodes"
          :edges="graphEdges"
          :brothers-view="brothersView"
          @select-person="onSelectPerson"
          @update:brothers-view="setBrothersView"
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

// 耶穌弟兄詮釋（馬可 6:3）— 4 個選項：
//   protestant（字面）/ early_consensus（前妻說早期版）/ orthodox（前妻說）/ catholic（表親說）
// 局部按鈕在族譜圖 widget 內；URL 同步 ?view=
type BrothersView = 'protestant' | 'early_consensus' | 'orthodox' | 'catholic' | 'apocrypha' | 'rabbinic'
const ALLOWED = ['protestant', 'early_consensus', 'orthodox', 'catholic', 'apocrypha', 'rabbinic']
const brothersView = ref<BrothersView>(
  (ALLOWED.includes(route.query.view as string) ? route.query.view : 'protestant') as BrothersView
)

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
