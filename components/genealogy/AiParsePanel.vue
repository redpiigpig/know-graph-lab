<template>
  <!-- Backdrop -->
  <div class="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/30 backdrop-blur-sm" @click.self="$emit('close')">
    <div class="w-full sm:w-[600px] max-h-[85vh] bg-white rounded-t-2xl sm:rounded-2xl shadow-2xl flex flex-col">
      <!-- Header -->
      <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100">
        <div>
          <h3 class="font-semibold text-gray-900">✨ AI 譜系解析</h3>
          <p class="text-xs text-gray-400 mt-0.5">貼入族譜文字，AI 自動整理成關係圖</p>
        </div>
        <button class="text-gray-400 hover:text-gray-600 text-xl leading-none" @click="$emit('close')">×</button>
      </div>

      <!-- Input -->
      <div class="flex-1 overflow-y-auto px-5 py-4">
        <textarea
          v-model="inputText"
          class="w-full h-52 border border-gray-200 rounded-xl px-3 py-2.5 text-sm text-gray-800 outline-none focus:border-amber-400 resize-none leading-relaxed placeholder-gray-300"
          placeholder="貼入族譜資料，例如：&#10;&#10;張氏族譜&#10;始祖：張大成（1850—1920）&#10;長子：張明德（1878—1945），配偶：李氏&#10;次子：張明義（1881—1960）&#10;張明德之子：張志遠（1905—1988）..."
        />

        <!-- Result preview -->
        <div v-if="result" class="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-xl">
          <p class="text-xs font-medium text-amber-700 mb-1">解析結果預覽</p>
          <p class="text-xs text-amber-600">
            找到 <strong>{{ result.nodes.length }}</strong> 位人物、
            <strong>{{ result.edges.length }}</strong> 條關係
          </p>
        </div>

        <div v-if="error" class="mt-3 p-3 bg-red-50 border border-red-200 rounded-xl">
          <p class="text-xs text-red-600">{{ error }}</p>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex items-center gap-2 px-5 py-4 border-t border-gray-100">
        <button
          class="flex-1 py-2.5 rounded-xl text-sm font-semibold bg-amber-500 hover:bg-amber-600 text-white transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          :disabled="!inputText.trim() || loading"
          @click="parse"
        >
          <span v-if="loading" class="animate-spin text-base">⟳</span>
          {{ loading ? '解析中…' : '解析並匯入' }}
        </button>

        <button
          v-if="result"
          class="flex-1 py-2.5 rounded-xl text-sm font-semibold border border-amber-300 text-amber-700 hover:bg-amber-50 transition"
          @click="appendResult"
        >追加到現有圖</button>

        <button
          class="px-4 py-2.5 rounded-xl text-sm text-gray-500 hover:bg-gray-50 transition border border-gray-200"
          @click="$emit('close')"
        >取消</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const emit = defineEmits<{
  import: [nodes: any[], edges: any[]]
  append: [nodes: any[], edges: any[]]
  close: []
}>()

const inputText = ref('')
const loading = ref(false)
const error = ref('')
const result = ref<{ nodes: any[]; edges: any[] } | null>(null)

async function parse() {
  if (!inputText.value.trim()) return
  loading.value = true
  error.value = ''
  result.value = null

  try {
    const data = await $fetch<{ nodes: any[]; edges: any[] }>('/api/genealogy/parse', {
      method: 'POST',
      body: { text: inputText.value },
    })
    result.value = data
    // Auto-import on first parse
    emit('import', data.nodes, data.edges)
  } catch (e: any) {
    error.value = e?.data?.message || e?.message || '解析失敗，請稍後再試'
  } finally {
    loading.value = false
  }
}

function appendResult() {
  if (!result.value) return
  emit('append', result.value.nodes, result.value.edges)
}
</script>
