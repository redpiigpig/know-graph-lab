<template>
  <div class="flex flex-col bg-white" style="height:100%; width:100%; border: 1px solid #e5e7eb;">

    <!-- ── 工具列 ────────────────────────────────────────── -->
    <div class="flex items-center flex-wrap gap-0.5 px-3 py-2 border-b border-gray-200 bg-gray-50" style="flex-shrink:0;">

      <!-- Undo / Redo -->
      <button title="復原" class="rte-btn" @click="editor?.chain().focus().undo().run()">↩</button>
      <button title="重做" class="rte-btn" @click="editor?.chain().focus().redo().run()">↪</button>
      <div class="rte-sep" />

      <!-- Headings -->
      <button title="H1" class="rte-btn" :class="{ 'rte-active': editor?.isActive('heading', { level: 1 }) }" @click="editor?.chain().focus().toggleHeading({ level: 1 }).run()"><strong>H1</strong></button>
      <button title="H2" class="rte-btn" :class="{ 'rte-active': editor?.isActive('heading', { level: 2 }) }" @click="editor?.chain().focus().toggleHeading({ level: 2 }).run()"><strong>H2</strong></button>
      <button title="H3" class="rte-btn" :class="{ 'rte-active': editor?.isActive('heading', { level: 3 }) }" @click="editor?.chain().focus().toggleHeading({ level: 3 }).run()"><strong>H3</strong></button>
      <div class="rte-sep" />

      <!-- Bold / Italic / Underline / Strike -->
      <button title="粗體" class="rte-btn" :class="{ 'rte-active': editor?.isActive('bold') }" @click="editor?.chain().focus().toggleBold().run()"><strong>B</strong></button>
      <button title="斜體" class="rte-btn" :class="{ 'rte-active': editor?.isActive('italic') }" @click="editor?.chain().focus().toggleItalic().run()"><em>I</em></button>
      <button title="底線" class="rte-btn" :class="{ 'rte-active': editor?.isActive('underline') }" @click="editor?.chain().focus().toggleUnderline().run()"><u>U</u></button>
      <button title="刪除線" class="rte-btn" :class="{ 'rte-active': editor?.isActive('strike') }" @click="editor?.chain().focus().toggleStrike().run()"><s>S</s></button>
      <div class="rte-sep" />

      <!-- 標楷體 -->
      <button title="標楷體" class="rte-btn" style="font-family:'BiauKai','DFKai-SB','標楷體','KaiTi',serif;" :class="{ 'rte-active': isKai }" @click="toggleKai">楷</button>
      <div class="rte-sep" />

      <!-- Lists / Blockquote -->
      <button title="項目清單" class="rte-btn" :class="{ 'rte-active': editor?.isActive('bulletList') }" @click="editor?.chain().focus().toggleBulletList().run()">≡</button>
      <button title="數字清單" class="rte-btn" :class="{ 'rte-active': editor?.isActive('orderedList') }" @click="editor?.chain().focus().toggleOrderedList().run()">①</button>
      <button title="引言" class="rte-btn" :class="{ 'rte-active': editor?.isActive('blockquote') }" @click="editor?.chain().focus().toggleBlockquote().run()">❝</button>
      <div class="rte-sep" />

      <!-- Alignment -->
      <button title="靠左" class="rte-btn" :class="{ 'rte-active': editor?.isActive({ textAlign: 'left' }) }" @click="editor?.chain().focus().setTextAlign('left').run()">
        <svg width="13" height="11" viewBox="0 0 13 11" fill="currentColor"><rect y="0" width="13" height="2" rx="1"/><rect y="4.5" width="9" height="2" rx="1"/><rect y="9" width="11" height="2" rx="1"/></svg>
      </button>
      <button title="置中" class="rte-btn" :class="{ 'rte-active': editor?.isActive({ textAlign: 'center' }) }" @click="editor?.chain().focus().setTextAlign('center').run()">
        <svg width="13" height="11" viewBox="0 0 13 11" fill="currentColor"><rect y="0" width="13" height="2" rx="1"/><rect x="2" y="4.5" width="9" height="2" rx="1"/><rect x="1" y="9" width="11" height="2" rx="1"/></svg>
      </button>
      <button title="靠右" class="rte-btn" :class="{ 'rte-active': editor?.isActive({ textAlign: 'right' }) }" @click="editor?.chain().focus().setTextAlign('right').run()">
        <svg width="13" height="11" viewBox="0 0 13 11" fill="currentColor"><rect y="0" width="13" height="2" rx="1"/><rect x="4" y="4.5" width="9" height="2" rx="1"/><rect x="2" y="9" width="11" height="2" rx="1"/></svg>
      </button>
      <div class="rte-sep" />

      <!-- Text Color -->
      <div class="relative" ref="colorRef">
        <button title="文字顏色" class="rte-btn" style="flex-direction:column; gap:2px; height:2rem;" @click="showColor = !showColor; showHL = false">
          <span style="font-size:11px; font-weight:700; line-height:1; color:#374151;">A</span>
          <div style="width:16px; height:3px; border-radius:9999px;" :style="{ background: activeColor }" />
        </button>
        <div v-if="showColor" style="position:absolute; top:calc(100% + 4px); left:0; z-index:100; background:#fff; border:1px solid #e5e7eb; border-radius:12px; box-shadow:0 10px 25px rgba(0,0,0,0.12); padding:12px; width:200px;">
          <p style="font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; color:#9ca3af; margin:0 0 8px;">文字顏色</p>
          <div style="display:grid; grid-template-columns:repeat(8,1fr); gap:4px; margin-bottom:8px;">
            <button v-for="c in TEXT_COLORS" :key="c"
              style="aspect-ratio:1; border-radius:4px; border:2px solid transparent; cursor:pointer; transition:transform 0.1s;"
              :style="{ background: c, borderColor: activeColor === c ? '#111' : 'transparent' }"
              @click="applyColor(c)" />
          </div>
          <button style="width:100%; padding:4px; font-size:11px; color:#9ca3af; border:1px solid #e5e7eb; border-radius:8px; cursor:pointer; background:#fff;"
            @click="applyColor('#374151')">重設</button>
        </div>
      </div>

      <!-- Highlight -->
      <div class="relative" ref="hlRef">
        <button title="螢光標記" class="rte-btn" style="flex-direction:column; gap:2px; height:2rem;" @click="showHL = !showHL; showColor = false">
          <span style="font-size:11px; line-height:1; color:#374151;">✦</span>
          <div style="width:16px; height:3px; border-radius:9999px; border:1px solid #e5e7eb;" :style="{ background: activeHL || '#fef08a' }" />
        </button>
        <div v-if="showHL" style="position:absolute; top:calc(100% + 4px); left:0; z-index:100; background:#fff; border:1px solid #e5e7eb; border-radius:12px; box-shadow:0 10px 25px rgba(0,0,0,0.12); padding:12px; width:200px;">
          <p style="font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; color:#9ca3af; margin:0 0 8px;">螢光標記</p>
          <div style="display:grid; grid-template-columns:repeat(8,1fr); gap:4px; margin-bottom:8px;">
            <button v-for="c in HL_COLORS" :key="c"
              style="aspect-ratio:1; border-radius:4px; border:2px solid transparent; cursor:pointer; transition:transform 0.1s;"
              :style="{ background: c, borderColor: activeHL === c ? '#111' : 'transparent' }"
              @click="applyHL(c)" />
          </div>
          <button style="width:100%; padding:4px; font-size:11px; color:#9ca3af; border:1px solid #e5e7eb; border-radius:8px; cursor:pointer; background:#fff;"
            @click="applyHL(null)">移除</button>
        </div>
      </div>
      <div class="rte-sep" />

      <!-- Clear formatting -->
      <button title="清除格式" class="rte-btn" @click="editor?.chain().focus().clearNodes().unsetAllMarks().run()">✕</button>
    </div>

    <!-- ── 打字區 ───────────────────────────────────────── -->
    <div style="flex:1; overflow-y:auto; padding:16px 24px; cursor:text;" @click="editor?.commands.focus()">
      <EditorContent :editor="editor" />
    </div>

  </div>
</template>

<script setup lang="ts">
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import { TextStyle } from '@tiptap/extension-text-style'
import { Color } from '@tiptap/extension-color'
import Highlight from '@tiptap/extension-highlight'
import TextAlign from '@tiptap/extension-text-align'
import Underline from '@tiptap/extension-underline'

const props = defineProps<{ modelValue: string }>()
const emit  = defineEmits<{ 'update:modelValue': [string] }>()

const KAI_FONT = "'BiauKai','DFKai-SB','標楷體','KaiTi',serif"

const TEXT_COLORS = [
  '#111827','#374151','#6b7280','#9ca3af',
  '#ef4444','#f97316','#f59e0b','#22c55e',
  '#14b8a6','#3b82f6','#6366f1','#8b5cf6',
  '#ec4899','#f43f5e','#0ea5e9','#84cc16',
]
const HL_COLORS = [
  '#fef08a','#fed7aa','#fecaca','#bbf7d0',
  '#a5f3fc','#bfdbfe','#e9d5ff','#fbcfe8',
  '#fde68a','#d1fae5','#cffafe','#dbeafe',
  '#f3e8ff','#fce7f3','#e0f2fe','#dcfce7',
]

const editor = useEditor({
  content: props.modelValue || '<p></p>',
  extensions: [
    StarterKit,
    TextStyle,
    Color,
    Highlight.configure({ multicolor: true }),
    TextAlign.configure({ types: ['heading', 'paragraph'] }),
    Underline,
  ],
  editorProps: { attributes: { class: 'rte-body' } },
  onUpdate: ({ editor }) => emit('update:modelValue', editor.getHTML()),
})

watch(() => props.modelValue, val => {
  if (editor.value && val !== editor.value.getHTML())
    editor.value.commands.setContent(val || '', false)
})
onBeforeUnmount(() => editor.value?.destroy())

const isKai = computed(() => {
  const ff = (editor.value?.getAttributes('textStyle') as any)?.fontFamily ?? ''
  return ff.includes('BiauKai') || ff.includes('DFKai') || ff.includes('標楷體')
})
function toggleKai() {
  if (isKai.value) editor.value?.chain().focus().unsetMark('textStyle').run()
  else editor.value?.chain().focus().setMark('textStyle', { fontFamily: KAI_FONT }).run()
}

const showColor  = ref(false)
const showHL     = ref(false)
const colorRef   = ref<HTMLElement>()
const hlRef      = ref<HTMLElement>()
const activeColor = computed(() => (editor.value?.getAttributes('textStyle') as any)?.color ?? '#374151')
const activeHL    = computed(() => (editor.value?.getAttributes('highlight') as any)?.color ?? null)

onClickOutside(colorRef, () => { showColor.value = false })
onClickOutside(hlRef,    () => { showHL.value    = false })

function applyColor(c: string) {
  editor.value?.chain().focus().setColor(c).run()
  showColor.value = false
}
function applyHL(c: string | null) {
  if (c) editor.value?.chain().focus().toggleHighlight({ color: c }).run()
  else   editor.value?.chain().focus().unsetHighlight().run()
  showHL.value = false
}
</script>

<style>
.rte-body {
  outline: none;
  min-height: 80px;
  line-height: 1.75;
  color: #374151;
  font-size: 14px;
}
.rte-body p   { margin: 0 0 0.4em; }
.rte-body h1  { font-size: 1.5rem;  font-weight: 700; margin: 0.6em 0 0.3em; color: #111827; }
.rte-body h2  { font-size: 1.2rem;  font-weight: 600; margin: 0.5em 0 0.25em; color: #1f2937; }
.rte-body h3  { font-size: 1.05rem; font-weight: 600; margin: 0.4em 0 0.2em; color: #374151; }
.rte-body ul  { list-style: disc;    padding-left: 1.4em; margin: 0.3em 0; }
.rte-body ol  { list-style: decimal; padding-left: 1.4em; margin: 0.3em 0; }
.rte-body blockquote { border-left: 3px solid #f59e0b; padding-left: 0.8em; color: #6b7280; margin: 0.4em 0; }
</style>

<style scoped>
.rte-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.15s;
  color: #4b5563;
  background: transparent;
  border: none;
  flex-shrink: 0;
}
.rte-btn:hover { background: #e5e7eb; }
.rte-active { background: #fef3c7 !important; color: #b45309 !important; }
.rte-sep {
  display: inline-block;
  width: 1px;
  height: 16px;
  background: #d1d5db;
  margin: 0 4px;
  flex-shrink: 0;
}
</style>
