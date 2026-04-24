<template>
  <div ref="containerRef" class="w-full h-full relative">
    <VueFlow
      id="genealogy-canvas"
      :node-types="nodeTypes"
      :default-edge-options="defaultEdgeOptions"
      fit-view-on-init
      class="genealogy-flow"
      @node-click="onNodeClick"
      @edge-click="onEdgeClick"
      @pane-click="onPaneClick"
      @connect="onConnect"
    >
      <Background :variant="BackgroundVariant.Dots" :gap="20" :size="1.5" color="#e5e7eb" />
      <Controls position="bottom-left" />

      <!-- Custom node slots -->
      <template #node-person="nodeProps">
        <PersonNode v-bind="nodeProps" @update-name="onNameUpdate" />
      </template>
      <template #node-textBox="nodeProps">
        <TextBoxNode v-bind="nodeProps" @update-text="onTextBoxUpdate" />
      </template>
      <template #node-group="nodeProps">
        <GroupNode v-bind="nodeProps" />
      </template>
    </VueFlow>

    <!-- "click to place" overlay -->
    <div
      v-if="placingType"
      class="absolute inset-0 z-50 cursor-crosshair flex items-center justify-center bg-amber-50/20"
      @click="onPlaceClick"
      @contextmenu.prevent="placingType = null"
    >
      <div class="bg-white border border-amber-300 rounded-xl px-4 py-2 text-sm text-amber-700 shadow-lg pointer-events-none">
        點擊畫布放置節點，右鍵取消
      </div>
    </div>

    <!-- Legend slot – rendered as absolute overlay -->
    <slot name="legend" />
  </div>
</template>

<script setup lang="ts">
import {
  VueFlow,
  useVueFlow,
  MarkerType,
  type Node,
  type Edge,
  type Connection,
  type NodeMouseEvent,
  type EdgeMouseEvent,
} from '@vue-flow/core'
import { Background, BackgroundVariant } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { markRaw } from 'vue'
import dagre from '@dagrejs/dagre'
import PersonNode from './PersonNode.vue'
import TextBoxNode from './TextBoxNode.vue'
import GroupNode from './GroupNode.vue'

defineProps<{ showMinimap?: boolean }>()  // showMinimap kept for API compat, not used

const emit = defineEmits<{
  selectNode: [node: Node | null]
  selectEdge: [edge: Edge | null]
  deselectAll: []
}>()

const containerRef = ref<HTMLElement>()
const placingType = ref<'person' | 'textBox' | 'group' | null>(null)

const nodeTypes = {
  person:  markRaw(PersonNode),
  textBox: markRaw(TextBoxNode),
  group:   markRaw(GroupNode),
}

const defaultEdgeOptions = {
  type: 'smoothstep',
  markerEnd: MarkerType.ArrowClosed,
  style: { stroke: '#6b7280', strokeWidth: 2 },
}

const { nodes, edges, addNodes, addEdges, setNodes, setEdges, fitView, getViewport, toObject } = useVueFlow('genealogy-canvas')

// ─── Events ────────────────────────────────────────────────
function onNodeClick({ node }: NodeMouseEvent) { emit('selectNode', node) }
function onEdgeClick({ edge }: EdgeMouseEvent) { emit('selectEdge', edge) }
function onPaneClick() { emit('deselectAll') }

function onConnect(conn: Connection) {
  addEdges([{
    id: `e_${Date.now()}`,
    source: conn.source,
    target: conn.target,
    sourceHandle: conn.sourceHandle ?? undefined,
    targetHandle: conn.targetHandle ?? undefined,
    type: 'smoothstep',
    markerEnd: MarkerType.ArrowClosed,
    style: { stroke: '#6b7280', strokeWidth: 2 },
    data: {
      relationshipType: 'parentChild',
      color: '#6b7280',
      strokeWidth: 2,
      strokeDasharray: '',
      lineType: 'smoothstep',
      dashStyleId: 'solid',
    },
  }])
}

function onNameUpdate(id: string, name: string) {
  setNodes(nodes.value.map(n => n.id === id ? { ...n, data: { ...n.data, name } } : n))
}

function onTextBoxUpdate(id: string, text: string) {
  setNodes(nodes.value.map(n => n.id === id ? { ...n, data: { ...n.data, text } } : n))
}

// ─── Place mode ────────────────────────────────────────────
function onPlaceClick(e: MouseEvent) {
  if (!placingType.value || !containerRef.value) return
  const rect = containerRef.value.getBoundingClientRect()
  const vp = getViewport()
  const x = (e.clientX - rect.left - vp.x) / vp.zoom
  const y = (e.clientY - rect.top  - vp.y) / vp.zoom
  const type = placingType.value
  placingType.value = null

  const id = `${type}_${Date.now()}`
  if (type === 'person') {
    addNodes([{
      id, type: 'person', position: { x, y },
      data: {
        name: '新人物', gender: 'unknown', generation: '', birthYear: '', deathYear: '',
        notes: '', shape: 'rectangle', borderStyleId: 'solid-md', borderColor: '#d1d5db',
      },
    }])
  } else if (type === 'textBox') {
    addNodes([{ id, type: 'textBox', position: { x, y }, data: { text: '文字備注', fontSize: 13 } }])
  } else {
    addNodes([{
      id, type: 'group', position: { x, y },
      style: { width: 280, height: 180, zIndex: -10 },
      data: { label: '群組', color: 'rgba(245,158,11,0.07)' },
    }])
  }
}

// ─── Public API ────────────────────────────────────────────
function startPlacing(type: 'person' | 'textBox' | 'group') { placingType.value = type }

function applyLayout(direction: 'TB' | 'BT' | 'LR' | 'RL') {
  const personNodes = nodes.value.filter(n => n.type === 'person')
  if (!personNodes.length) return
  const personIds = new Set(personNodes.map(n => n.id))
  const relevantEdges = edges.value.filter(e => personIds.has(e.source) && personIds.has(e.target))

  const g = new dagre.graphlib.Graph()
  g.setGraph({ rankdir: direction, nodesep: 60, ranksep: 80, marginx: 40, marginy: 40 })
  g.setDefaultEdgeLabel(() => ({}))
  personNodes.forEach(n => g.setNode(n.id, { width: 130, height: 70 }))
  relevantEdges.forEach(e => { try { g.setEdge(e.source, e.target) } catch {} })
  dagre.layout(g)

  setNodes(nodes.value.map(n => {
    if (!personIds.has(n.id)) return n
    const pos = g.node(n.id)
    return pos ? { ...n, position: { x: pos.x - 65, y: pos.y - 35 } } : n
  }))
  nextTick(() => fitView({ padding: 0.15, duration: 400 }))
}

function updateNode(id: string, data: Record<string, any>) {
  setNodes(nodes.value.map(n => n.id === id ? { ...n, data: { ...n.data, ...data } } : n))
}

function updateEdge(id: string, updates: Record<string, any>) {
  setEdges(edges.value.map(e => {
    if (e.id !== id) return e
    const color = updates.color ?? e.data?.color ?? '#6b7280'
    const width = updates.strokeWidth ?? e.data?.strokeWidth ?? 2
    const dash  = updates.strokeDasharray ?? e.data?.strokeDasharray ?? ''
    const ltype = updates.lineType ?? e.data?.lineType ?? 'smoothstep'
    return {
      ...e,
      type: ltype,
      label: updates.label ?? e.label,
      animated: updates.animated ?? e.animated,
      markerEnd: MarkerType.ArrowClosed,
      style: { stroke: color, strokeWidth: width, strokeDasharray: dash },
      data: { ...(e.data || {}), ...updates },
    }
  }))
}

function removeNode(id: string) {
  setNodes(nodes.value.filter(n => n.id !== id))
  setEdges(edges.value.filter(e => e.source !== id && e.target !== id))
}
function removeEdge(id: string) {
  setEdges(edges.value.filter(e => e.id !== id))
}
function importData(newNodes: Node[], newEdges: Edge[]) {
  setNodes(newNodes); setEdges(newEdges)
  nextTick(() => fitView({ padding: 0.2, duration: 500 }))
}
function appendData(newNodes: Node[], newEdges: Edge[]) {
  const existing = new Set(nodes.value.map(n => n.id))
  addNodes(newNodes.filter(n => !existing.has(n.id)))
  addEdges(newEdges.filter(e => !edges.value.find(ex => ex.id === e.id)))
  nextTick(() => fitView({ padding: 0.2, duration: 500 }))
}
function getSnapshot() { return toObject() }
function getContainer() { return containerRef.value }
function fitAll() { fitView({ padding: 0.15, duration: 400 }) }
function setGlobalShape(shape: 'circle' | 'rectangle') {
  setNodes(nodes.value.map(n => n.type === 'person' ? { ...n, data: { ...n.data, shape } } : n))
}

defineExpose({
  startPlacing, applyLayout, updateNode, updateEdge,
  removeNode, removeEdge, importData, appendData,
  getSnapshot, getContainer, fitAll, setGlobalShape,
})
</script>

<style>
@import '@vue-flow/core/dist/style.css';
@import '@vue-flow/core/dist/theme-default.css';
@import '@vue-flow/controls/dist/style.css';

.genealogy-flow { background: #f8fafc; }
.vue-flow__edge-path { transition: stroke 0.15s; }
</style>
