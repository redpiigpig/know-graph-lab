<template>
  <div class="genealogy-page flex flex-col bg-slate-50" style="height: 100dvh;">
    <!-- Nav -->
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 flex-shrink-0 z-30">
      <NuxtLink to="/genealogy" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <input
        v-model="projectTitle"
        class="text-sm font-semibold text-gray-900 bg-transparent border-none outline-none hover:bg-gray-50 focus:bg-gray-50 px-2 py-0.5 rounded-lg w-48 transition"
        placeholder="族譜名稱…"
      />
      <span class="text-xs text-gray-300">族譜繪製</span>
      <div class="flex-1" />
      <span class="text-xs text-gray-300">{{ saveStatus }}</span>
    </nav>

    <!-- Toolbar -->
    <GenealogyToolbar
      :current-direction="currentDirection"
      :node-shape="nodeShape"
      :selected-node="selectedNode"
      :selected-edge="selectedEdge"
      :color-legend="colorLegend"
      :line-style-legend="lineStyleLegend"
      class="flex-shrink-0 z-20"
      @apply-layout="handleApplyLayout"
      @set-shape="handleSetShape"
      @add-person="canvasRef?.startPlacing('person')"
      @add-text-box="canvasRef?.startPlacing('textBox')"
      @add-group="canvasRef?.startPlacing('group')"
      @fit-view="canvasRef?.fitAll()"
      @open-ai="showAiPanel = true"
      @import-biblical="handleBiblicalImport"
      @export="handleExport"
      @update-node="selectedNode && canvasRef?.updateNode(selectedNode.id, $event)"
      @delete-node="() => { selectedNode && canvasRef?.removeNode(selectedNode.id); selectedNode = null }"
      @update-edge="onEdgeUpdate"
      @delete-edge="() => { selectedEdge && canvasRef?.removeEdge(selectedEdge.id); selectedEdge = null }"
      @update-color-legend="updateColorLegend"
      @update-line-style-legend="updateLineStyleLegend"
    />

    <!-- Canvas -->
    <div class="flex-1 min-h-0 overflow-hidden">
      <ClientOnly>
        <GenealogyCanvas
          ref="canvasRef"
          class="w-full h-full"
          @select-node="onSelectNode"
          @select-edge="onSelectEdge"
          @deselect-all="onDeselectAll"
        >
          <template #legend>
            <ColorLegend :color-legend="colorLegend" :line-style-legend="lineStyleLegend" />
          </template>
        </GenealogyCanvas>
      </ClientOnly>
    </div>

    <!-- Editor toggle bar / resize handle -->
    <div
      class="flex-shrink-0 h-9 bg-gray-50 border-t border-gray-200 flex items-center justify-between px-4 z-20 select-none"
      :class="editorOpen ? 'cursor-row-resize hover:bg-amber-50' : 'cursor-pointer hover:bg-gray-100'"
      @mousedown="editorOpen && startResize($event)"
      @click.self="!editorOpen && (editorOpen = true)"
    >
      <span class="text-xs text-gray-500 pointer-events-none flex items-center gap-1.5">
        <span>📝</span> 族譜說明文字
      </span>
      <button
        class="text-[10px] text-gray-400 hover:text-gray-600 px-2 py-0.5 rounded hover:bg-white transition z-10"
        @click.stop="editorOpen = !editorOpen"
      >{{ editorOpen ? '收起 ↓' : '展開 ↑' }}</button>
    </div>

    <!-- Rich text editor -->
    <div v-if="editorOpen"
      class="flex-shrink-0 bg-white border-t border-gray-200"
      :style="{ height: `${editorHeight}px` }"
    >
      <RichTextEditor v-model="noteContent" />
    </div>

    <!-- AI panel -->
    <AiParsePanel
      v-if="showAiPanel"
      @import="handleAiImport"
      @append="handleAiAppend"
      @close="showAiPanel = false"
    />
  </div>
</template>

<script setup lang="ts">
import type { Node, Edge } from '@vue-flow/core'
import { toPng } from 'html-to-image'
import { jsPDF } from 'jspdf'
import { Document, Packer, Paragraph, TextRun, ImageRun, HeadingLevel } from 'docx'

definePageMeta({ ssr: false, middleware: 'auth' })
useHead({ title: '族譜繪製 — Know Graph Lab' })

const supabase = useSupabaseClient()
const router   = useRouter()

async function getToken() {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session) { router.push('/login'); return null }
  return session.access_token
}

const canvasRef = ref()
const projectTitle    = ref('我的族譜')
const currentDirection = ref<'TB'|'BT'|'LR'|'RL'>('TB')
const nodeShape       = ref<'circle'|'rectangle'>('rectangle')
const showAiPanel     = ref(false)
const selectedNode    = ref<Node | null>(null)
const selectedEdge    = ref<Edge | null>(null)
const noteContent     = ref('<p>在此輸入族譜說明文字…</p>')
const saveStatus      = ref('')

const colorLegend     = ref<Record<string, string>>({})
const lineStyleLegend = ref<Record<string, string>>({})

function updateColorLegend(hex: string, name: string) {
  colorLegend.value = { ...colorLegend.value, [hex]: name }
  debouncedSave()
}
function updateLineStyleLegend(id: string, name: string) {
  lineStyleLegend.value = { ...lineStyleLegend.value, [id]: name }
  debouncedSave()
}

const editorOpen   = ref(false)
const editorHeight = ref(260)

onMounted(() => { loadFromStorage() })

function startResize(e: MouseEvent) {
  if (!editorOpen.value) return
  const startY = e.clientY
  const startH = editorHeight.value
  const onMove = (ev: MouseEvent) => {
    editorHeight.value = Math.max(160, Math.min(600, startH + (startY - ev.clientY)))
  }
  const onUp = () => {
    window.removeEventListener('mousemove', onMove)
    window.removeEventListener('mouseup', onUp)
  }
  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup', onUp)
}

function onSelectNode(node: Node) { selectedNode.value = node; selectedEdge.value = null }
function onSelectEdge(edge: Edge) { selectedEdge.value = edge; selectedNode.value = null }
function onDeselectAll() { selectedNode.value = null; selectedEdge.value = null }

function onEdgeUpdate(data: Record<string, any>) {
  if (!selectedEdge.value) return
  canvasRef.value?.updateEdge(selectedEdge.value.id, data)
}

function handleApplyLayout(dir: string) {
  currentDirection.value = dir as any
  canvasRef.value?.applyLayout(dir)
}
function handleSetShape(shape: 'circle'|'rectangle') {
  nodeShape.value = shape
  canvasRef.value?.setGlobalShape(shape)
}

async function handleBiblicalImport() {
  if (!confirm('匯入聖經族譜將覆蓋目前畫布內容，確定繼續？')) return
  const token = await getToken()
  if (!token) return
  const { nodes, edges } = await $fetch<{ nodes: Node[], edges: Edge[] }>('/api/genealogy/biblical-graph', {
    headers: { Authorization: `Bearer ${token}` },
  })
  canvasRef.value?.importData(nodes, edges)
  nextTick(() => canvasRef.value?.applyLayout(currentDirection.value))
}

function handleAiImport(nodes: Node[], edges: Edge[]) {
  canvasRef.value?.importData(nodes, edges)
  showAiPanel.value = false
  nextTick(() => canvasRef.value?.applyLayout(currentDirection.value))
}
function handleAiAppend(nodes: Node[], edges: Edge[]) {
  canvasRef.value?.appendData(nodes, edges)
  showAiPanel.value = false
  nextTick(() => canvasRef.value?.applyLayout(currentDirection.value))
}

const debouncedSave = useDebounceFn(saveToStorage, 1500)
watch([projectTitle, noteContent, colorLegend, lineStyleLegend], debouncedSave)

function saveToStorage() {
  if (!canvasRef.value) return
  const snap = canvasRef.value.getSnapshot()
  localStorage.setItem('genealogy_project', JSON.stringify({
    title: projectTitle.value,
    direction: currentDirection.value,
    nodeShape: nodeShape.value,
    notes: noteContent.value,
    nodes: snap.nodes,
    edges: snap.edges,
    colorLegend: colorLegend.value,
    lineStyleLegend: lineStyleLegend.value,
  }))
  saveStatus.value = '已儲存'
  setTimeout(() => { saveStatus.value = '' }, 2000)
}

function loadFromStorage() {
  try {
    const raw = localStorage.getItem('genealogy_project')
    if (!raw) return
    const d = JSON.parse(raw)
    projectTitle.value      = d.title      || '我的族譜'
    currentDirection.value  = d.direction  || 'TB'
    nodeShape.value         = d.nodeShape  || 'rectangle'
    noteContent.value       = d.notes      || ''
    colorLegend.value       = d.colorLegend      || {}
    lineStyleLegend.value   = d.lineStyleLegend  || {}
    if (d.nodes?.length) {
      nextTick(() => canvasRef.value?.importData(d.nodes, d.edges || []))
    }
  } catch {}
}

let saveTimer: ReturnType<typeof setInterval>
onMounted(() => { saveTimer = setInterval(saveToStorage, 5000) })
onBeforeUnmount(() => clearInterval(saveTimer))

async function handleExport(format: string) {
  const container = canvasRef.value?.getContainer() as HTMLElement | undefined
  if (!container) return

  const dataUrl = await toPng(container, { pixelRatio: 2, backgroundColor: '#f8fafc' })

  if (format === 'png') {
    const a = document.createElement('a')
    a.href = dataUrl; a.download = `${projectTitle.value}.png`; a.click()
    return
  }

  if (format === 'pdf-diagram') {
    const img = new Image(); img.src = dataUrl
    await new Promise(r => { img.onload = r })
    const pdf = new jsPDF({
      orientation: img.width > img.height ? 'landscape' : 'portrait',
      unit: 'px', format: [img.width, img.height],
    })
    pdf.addImage(dataUrl, 'PNG', 0, 0, img.width, img.height)
    pdf.save(`${projectTitle.value}.pdf`); return
  }

  if (format === 'pdf-full') {
    const img = new Image(); img.src = dataUrl
    await new Promise(r => { img.onload = r })
    const pageW = 794
    const imgH = Math.round((img.height / img.width) * pageW)
    const pdf = new jsPDF({ unit: 'px', format: 'a4' })
    pdf.addImage(dataUrl, 'PNG', 0, 0, pageW, imgH)
    const plain = noteContent.value.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim()
    if (plain) {
      pdf.setFontSize(11); pdf.setTextColor(60)
      const lines = pdf.splitTextToSize(plain, pageW - 40)
      pdf.text(lines, 20, imgH + 20)
    }
    pdf.save(`${projectTitle.value}.pdf`); return
  }

  if (format === 'word') {
    const base64 = dataUrl.split(',')[1]
    const binary = atob(base64)
    const bytes = new Uint8Array(binary.length)
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i)

    const img = new Image(); img.src = dataUrl
    await new Promise(r => { img.onload = r })
    const maxW = 600, scale = maxW / img.width
    const docW = Math.round(img.width * scale)
    const docH = Math.round(img.height * scale)

    const tempDiv = document.createElement('div')
    tempDiv.innerHTML = noteContent.value
    const textLines = Array.from(
      tempDiv.querySelectorAll('p,h1,h2,h3,li')
    ).map(el => el.textContent?.trim() || '').filter(Boolean)

    const doc = new Document({
      sections: [{
        properties: {},
        children: [
          new Paragraph({ text: projectTitle.value, heading: HeadingLevel.HEADING_1 }),
          new Paragraph({
            children: [new ImageRun({ data: bytes.buffer, transformation: { width: docW, height: docH }, type: 'png' })],
          }),
          new Paragraph({ text: '' }),
          ...textLines.map(line => new Paragraph({ children: [new TextRun({ text: line, size: 22 })] })),
        ],
      }],
    })

    const blob = await Packer.toBlob(doc)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = `${projectTitle.value}.docx`; a.click()
    URL.revokeObjectURL(url)
  }
}
</script>

<style scoped>
.genealogy-page { user-select: none; }
</style>
