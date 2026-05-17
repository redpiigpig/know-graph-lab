<template>
  <div class="flex flex-col bg-slate-50" style="height: 100dvh;">
    <nav class="flex items-center gap-2 px-4 h-12 bg-white border-b border-gray-100 flex-shrink-0 z-30">
      <NuxtLink to="/genealogy" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">主教按立樹</span>
      <span v-if="graph" class="text-xs text-gray-400 ml-1">
        以「按立鏈」為主軸的主教傳承
      </span>
      <div class="flex-1" />

      <div class="flex items-center gap-0.5 bg-gray-100 rounded-lg p-0.5">
        <NuxtLink
          to="/genealogy/episcopal-tree"
          class="text-xs px-2.5 py-1 rounded-md font-medium transition text-gray-500 hover:text-gray-700"
        >教座樹</NuxtLink>
        <span class="text-xs px-2.5 py-1 rounded-md font-medium bg-white shadow-sm text-gray-900">按立樹</span>
      </div>
    </nav>

    <div class="flex-1 min-h-0 relative">
      <ClientOnly>
        <GenealogyConsecrationTree :graph="graph" />
        <template #fallback>
          <div class="absolute inset-0 flex items-center justify-center text-gray-300 text-sm">載入中…</div>
        </template>
      </ClientOnly>
      <div v-if="loadError" class="absolute top-4 left-1/2 -translate-x-1/2 bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded-lg text-sm">
        載入失敗：{{ loadError }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
useHead({ title: '主教按立樹 — Know Graph Lab' })

const supabase = useSupabaseClient()
const router   = useRouter()

async function getToken() {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session) { router.push('/login'); return null }
  return session.access_token
}

const graph = ref<any>(null)
const loadError = ref<string | null>(null)

async function loadGraph() {
  const token = await getToken()
  if (!token) return
  try {
    graph.value = await $fetch('/api/genealogy/episcopal-graph', {
      headers: { Authorization: `Bearer ${token}` },
    })
  } catch (e: any) {
    loadError.value = e?.message ?? String(e)
  }
}

onMounted(loadGraph)
</script>
