<template>
  <div class="tfb-root" :class="{ 'tfb-root--fullscreen': fullscreen }">
    <!-- ── Topbar ─────────────────────────────────────────────── -->
    <div class="tfb-topbar">
      <div class="tfb-topbar-left">
        <button class="tfb-toc-btn" @click="tocOpen = !tocOpen" title="目錄">
          <svg viewBox="0 0 16 16" fill="none" aria-hidden="true">
            <line x1="2.5" y1="4"  x2="13.5" y2="4"  stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
            <line x1="2.5" y1="8"  x2="13.5" y2="8"  stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
            <line x1="2.5" y1="12" x2="13.5" y2="12" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
          </svg>
          目錄
        </button>
      </div>

      <div class="tfb-topbar-center">
        <button class="tfb-nav-btn" :disabled="state === 'cover'" @click="prev" title="上一頁 (←)">‹</button>
        <span class="tfb-page-label">
          <template v-if="state === 'cover'">封面</template>
          <template v-else-if="state === 'back'">封底</template>
          <template v-else>
            第
            <input
              v-model.number="jumpInput"
              class="tfb-page-input"
              type="number"
              :min="1"
              :max="totalPages"
              @keyup.enter="jump"
              @blur="jump"
            />
            / {{ totalPages }} 頁
          </template>
        </span>
        <button class="tfb-nav-btn" :disabled="state === 'back'" @click="next" title="下一頁 (→)">›</button>
      </div>

      <div class="tfb-topbar-right">
        <a :href="downloadUrl" download class="tfb-action-btn" title="下載原版 PDF">
          <svg viewBox="0 0 16 16" fill="none" aria-hidden="true">
            <path d="M8 2v8 M5 7l3 3 3-3 M2.5 13h11" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
          </svg>
          下載 PDF
        </a>
        <button class="tfb-action-btn" @click="fullscreen = !fullscreen" title="全螢幕">
          <svg viewBox="0 0 16 16" fill="none" aria-hidden="true">
            <path d="M2 6V2H6 M14 6V2H10 M2 10V14H6 M14 10V14H10"
              stroke="currentColor" stroke-width="1.3" stroke-linecap="round" fill="none"/>
          </svg>
          {{ fullscreen ? '退出' : '全螢幕' }}
        </button>
      </div>
    </div>

    <!-- ── Loading state ──────────────────────────────────────── -->
    <div v-if="loading" class="tfb-loading">載入中…</div>

    <!-- ── Reader body ────────────────────────────────────────── -->
    <div v-else class="tfb-body">

      <!-- TOC sidebar (only when reading) -->
      <aside v-show="tocOpen && state === 'reading'" class="tfb-toc">
        <div class="tfb-toc-title">章節目錄</div>
        <div v-if="!outline?.length" class="tfb-toc-empty">尚未自動偵測到章節</div>
        <ul v-else class="tfb-toc-list">
          <li
            v-for="(o, i) in outline"
            :key="i"
            :class="['tfb-toc-item', `tfb-toc-item--lvl${Math.min(o.level || 1, 4)}`,
                     { 'tfb-toc-item--active': isOutlineActive(o) }]"
            @click="goPage(o.page)"
          >
            <span class="tfb-toc-text">{{ o.text }}</span>
            <span class="tfb-toc-leader" aria-hidden="true"></span>
            <span class="tfb-toc-page">{{ o.page }}</span>
          </li>
        </ul>
      </aside>

      <!-- Book -->
      <div class="tfb-book-wrap">

        <!-- ── Front cover ─────────────────────────────────── -->
        <div v-if="state === 'cover'" class="tfb-book tfb-book--single" @click="openBook">
          <div class="tfb-cover tfb-cover--front">
            <div class="tfb-cover-frame">
              <div class="tfb-cover-eyebrow">{{ categoryLabel }}</div>
              <div class="tfb-cover-rule" />
              <h1 class="tfb-cover-title">{{ article.title }}</h1>
              <p v-if="article.title_en" class="tfb-cover-title-en">{{ article.title_en }}</p>
              <div class="tfb-cover-mid">
                <span class="tfb-cover-ornament">❦</span>
              </div>
              <p class="tfb-cover-author">{{ article.author || '龐君華' }}</p>
              <p v-if="article.supervisor" class="tfb-cover-supervisor">指導教授 ‧ {{ article.supervisor }}</p>
              <div class="tfb-cover-foot">
                <p v-if="article.publication" class="tfb-cover-school">{{ article.publication }}</p>
                <p v-if="article.published_date" class="tfb-cover-year">{{ formatYear(article.published_date) }}</p>
              </div>
            </div>
            <div class="tfb-cover-hint">點擊封面，開啟全書 →</div>
          </div>
        </div>

        <!-- ── Back cover ──────────────────────────────────── -->
        <div v-else-if="state === 'back'" class="tfb-book tfb-book--single" @click="prev">
          <div class="tfb-cover tfb-cover--back">
            <div class="tfb-cover-frame">
              <div class="tfb-back-mark">✝</div>
              <p class="tfb-back-archive">龐君華會督數位典藏</p>
              <p class="tfb-back-archive-en">Bishop Pong Kwan-wah Digital Archive</p>
              <div class="tfb-cover-rule" />
              <p v-if="article.provider" class="tfb-back-meta">原檔提供 ‧ {{ article.provider }}</p>
              <p class="tfb-back-meta">© {{ new Date().getFullYear() }}</p>
            </div>
            <div class="tfb-cover-hint">← 點擊回到最後一頁</div>
          </div>
        </div>

        <!-- ── Reading: 2-page spread ──────────────────────── -->
        <div v-else class="tfb-book" :class="{ 'tfb-book--flipping': flipping }">

          <!-- Left page -->
          <article class="tfb-page tfb-page--left" :class="overflowClass(leftOverflowLevel)">
            <div class="tfb-page-inner" ref="leftPageEl">
              <div class="tfb-content" v-if="leftBlocks">
                <template v-for="(b, i) in bodyBlocks(leftBlocks)" :key="`L${i}`">
                  <div v-if="b.type === '_toc_entry'" :class="['tfb-blk', 'tfb-blk--toc', `tfb-blk--toc-lvl${Math.min(b.level || 1, 4)}`]">
                    <span class="tfb-blk-toc-text">{{ b.text }}</span>
                    <span class="tfb-blk-toc-leader" aria-hidden="true"></span>
                    <span class="tfb-blk-toc-page">{{ b.page }}</span>
                  </div>
                  <component v-else :is="blockTag(b)" :class="blockClass(b)">{{ b.text }}</component>
                </template>
                <div v-if="leftFootnotes.length" class="tfb-footnotes">
                  <div v-for="(f, i) in leftFootnotes" :key="`LF${i}`" class="tfb-footnote">
                    <sup class="tfb-footnote-marker">{{ f.marker || (i + 1) }}</sup>
                    <span class="tfb-footnote-text">{{ f.text }}</span>
                  </div>
                </div>
              </div>
              <div v-else class="tfb-page-empty">（空白頁）</div>
            </div>
            <div class="tfb-page-num">{{ leftPage }}</div>
          </article>

          <!-- Right page -->
          <article class="tfb-page tfb-page--right" :class="overflowClass(rightOverflowLevel)">
            <div class="tfb-page-inner" ref="rightPageEl">
              <div class="tfb-content" v-if="rightBlocks">
                <template v-for="(b, i) in bodyBlocks(rightBlocks)" :key="`R${i}`">
                  <div v-if="b.type === '_toc_entry'" :class="['tfb-blk', 'tfb-blk--toc', `tfb-blk--toc-lvl${Math.min(b.level || 1, 4)}`]">
                    <span class="tfb-blk-toc-text">{{ b.text }}</span>
                    <span class="tfb-blk-toc-leader" aria-hidden="true"></span>
                    <span class="tfb-blk-toc-page">{{ b.page }}</span>
                  </div>
                  <component v-else :is="blockTag(b)" :class="blockClass(b)">{{ b.text }}</component>
                </template>
                <div v-if="rightFootnotes.length" class="tfb-footnotes">
                  <div v-for="(f, i) in rightFootnotes" :key="`RF${i}`" class="tfb-footnote">
                    <sup class="tfb-footnote-marker">{{ f.marker || (i + 1) }}</sup>
                    <span class="tfb-footnote-text">{{ f.text }}</span>
                  </div>
                </div>
              </div>
              <div v-else class="tfb-page-empty">（空白頁）</div>
            </div>
            <div class="tfb-page-num">{{ rightPage <= totalPages ? rightPage : '' }}</div>
          </article>

        </div>
      </div>
    </div>

    <!-- ── Edge hot zones for click-to-flip ─────────────────── -->
    <div class="tfb-edge tfb-edge--left"  @click="prev" :class="{ 'tfb-edge--disabled': leftPage <= 1 }"></div>
    <div class="tfb-edge tfb-edge--right" @click="next" :class="{ 'tfb-edge--disabled': rightPage >= totalPages }"></div>
  </div>
</template>

<script setup>
const props = defineProps({
  writingId:     { type: [Number, String], required: true },
  outline:       { type: Array, default: () => [] },
  totalPages:    { type: Number, default: 0 },
  pdfUrl:        { type: String, default: '' },
  article:       { type: Object, default: () => ({}) },
  categoryLabel: { type: String, default: '學位論文' },
})

// state machine: cover → reading → back
const state = ref('cover')
function openBook() { state.value = 'reading'; if (leftPage.value < 1) leftPage.value = 1 }
function closeFront() { state.value = 'cover' }
function closeBack()  { state.value = 'back' }

function formatYear(dateStr) {
  if (!dateStr) return ''
  const [y, m] = String(dateStr).split('-').map(Number)
  const cy = String(y).split('').map(d => '〇一二三四五六七八九'[+d]).join('')
  const cm = ['','一','二','三','四','五','六','七','八','九','十','十一','十二'][m] || ''
  return cm ? `${cy} 年 ${cm} 月` : `${cy} 年`
}

const pages = ref([])              // array of { page, blocks }
const pagesByNumber = ref(new Map())
const loading = ref(true)
const leftPage = ref(1)            // 1-based; left page is odd-numbered (1, 3, 5…)
const flipping = ref(false)
const tocOpen = ref(true)
const fullscreen = ref(false)
const jumpInput = ref(1)

// Overflow auto-shrink: 0 = fits, 1 = mild shrink, 2 = aggressive shrink.
// Pages with lots of footnotes need the deeper level so nothing gets clipped.
const leftPageEl = ref(null)
const rightPageEl = ref(null)
const leftOverflowLevel = ref(0)
const rightOverflowLevel = ref(0)
function overflowClass(level) {
  if (level >= 2) return 'is-overflow-2'
  if (level >= 1) return 'is-overflow-1'
  return ''
}
function measureOverflow(el) {
  if (!el) return 0
  // Try level 0 → 1 → 2 by applying classes and re-measuring
  el.classList.remove('measure-1', 'measure-2')
  if (el.scrollHeight <= el.clientHeight + 1) return 0
  el.classList.add('measure-1')
  if (el.scrollHeight <= el.clientHeight + 1) { el.classList.remove('measure-1'); return 1 }
  el.classList.remove('measure-1')
  el.classList.add('measure-2')
  const stillOver = el.scrollHeight > el.clientHeight + 1
  el.classList.remove('measure-2')
  return stillOver ? 2 : 2  // even if still overflowing at level 2, cap there
}
async function recheckOverflow() {
  await nextTick()
  // Two RAF: first lets browser apply fonts, second to settle
  requestAnimationFrame(() => requestAnimationFrame(() => {
    leftOverflowLevel.value  = measureOverflow(leftPageEl.value)
    rightOverflowLevel.value = measureOverflow(rightPageEl.value)
  }))
}

const totalPages = computed(() => Math.max(props.totalPages || pages.value.length, pages.value.length))
const rightPage = computed(() => leftPage.value + 1)
const downloadUrl = computed(() => {
  const base = props.pdfUrl || ''
  return base ? base + (base.includes('?') ? '&' : '?') + 'download=1' : ''
})

// Spread convention: left odd (1, 3, 5…), right even (2, 4, 6…).
// So a fresh book opens to page 1 on the right with a blank cover-left.
// We use the simpler "left=odd / right=even" model that thesis-style books
// use (book opens like 1+2, 3+4, 5+6, …).

const leftBlocks = computed(() => pagesByNumber.value.get(leftPage.value)?.blocks ?? null)
const rightBlocks = computed(() => pagesByNumber.value.get(rightPage.value)?.blocks ?? null)

// Detect OCR'd 目錄 pages: if a title block is followed by a paragraph that's
// just a number / page range, merge them into a virtual 'toc_entry' block so we
// can render dot-leader 「章節名 …… 頁碼」on one row.
function transformBlocks(blocks) {
  if (!blocks || !blocks.length) return blocks || []
  const out = []
  const isPageStr = s => /^[\d]{1,4}(\s*[-—–]\s*[\d]{1,4})?$/.test((s || '').trim())
  const titleTypes = new Set(['chapter_title','section_title','subsection_title'])
  for (let i = 0; i < blocks.length; i++) {
    const b = blocks[i]
    const next = blocks[i + 1]
    if (titleTypes.has(b.type) && next && next.type === 'paragraph' && isPageStr(next.text)) {
      out.push({
        type: '_toc_entry',
        _origType: b.type,
        level: b.level,
        text: (b.text || '').trim(),
        page: (next.text || '').trim(),
      })
      i++
      continue
    }
    out.push(b)
  }
  return out
}

function bodyBlocks(blocks) {
  return transformBlocks(blocks).filter(b => b.type !== 'footnote' && b.type !== 'page_number')
}

const leftFootnotes = computed(() =>
  (leftBlocks.value || []).filter(b => b.type === 'footnote')
)
const rightFootnotes = computed(() =>
  (rightBlocks.value || []).filter(b => b.type === 'footnote')
)

function blockTag(b) {
  switch (b.type) {
    case 'chapter_title':
    case 'section_title':
    case 'subsection_title':
      return 'h' + Math.min(Math.max(b.level || 2, 1), 6)
    case 'list_item':
      return 'li'
    default:
      return 'p'
  }
}

function blockClass(b) {
  const cls = ['tfb-blk']
  if (b.type === 'chapter_title')    cls.push('tfb-blk--ch')
  if (b.type === 'section_title')    cls.push('tfb-blk--sec')
  if (b.type === 'subsection_title') cls.push('tfb-blk--sub', `tfb-blk--sub${Math.min(b.level || 3, 4)}`)
  if (b.type === 'paragraph')        cls.push('tfb-blk--p')
  if (b.type === 'quote')            cls.push('tfb-blk--q')
  if (b.type === 'list_item')        cls.push('tfb-blk--li')
  return cls
}

function clampLeft(n) {
  // Round to nearest odd, clamp to [1, lastOdd]
  let v = Math.max(1, Math.min(n, totalPages.value))
  if (v % 2 === 0) v -= 1
  if (v < 1) v = 1
  return v
}

function goPage(n) {
  state.value = 'reading'
  const target = clampLeft(n % 2 === 0 ? n - 1 : n)
  if (target === leftPage.value) return
  flipping.value = true
  setTimeout(() => { flipping.value = false }, 380)
  leftPage.value = target
  jumpInput.value = target
}

function prev() {
  if (state.value === 'back') { state.value = 'reading'; return }
  if (state.value === 'cover') return
  if (leftPage.value <= 1) { state.value = 'cover'; return }
  goPage(leftPage.value - 2)
}
function next() {
  if (state.value === 'cover') { openBook(); return }
  if (state.value === 'back')  return
  if (rightPage.value >= totalPages.value) { state.value = 'back'; return }
  goPage(leftPage.value + 2)
}

function jump() {
  const n = parseInt(jumpInput.value, 10)
  if (!Number.isFinite(n)) return
  goPage(n)
}

function isOutlineActive(o) {
  return o.page === leftPage.value || o.page === rightPage.value
}

function onKey(e) {
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return
  if (e.key === 'ArrowLeft' || e.key === 'PageUp')  { prev(); e.preventDefault() }
  if (e.key === 'ArrowRight'|| e.key === 'PageDown'){ next(); e.preventDefault() }
  if (e.key === 'Home') { goPage(1) }
  if (e.key === 'End')  { goPage(totalPages.value) }
}

const _onResize = () => recheckOverflow()

onMounted(async () => {
  window.addEventListener('keydown', onKey)
  window.addEventListener('resize', _onResize)
  try {
    const data = await $fetch(`/api/pong-writing/${props.writingId}/pages`)
    pages.value = Array.isArray(data) ? data : []
    const map = new Map()
    for (const p of pages.value) map.set(p.page, p)
    pagesByNumber.value = map
  } catch (e) {
    console.error('[thesis-flipbook]', e)
  } finally {
    loading.value = false
  }
  recheckOverflow()
})
watch([leftPage, () => pages.value.length], () => recheckOverflow())
onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKey)
  window.removeEventListener('resize', _onResize)
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;500;600;700&family=Noto+Sans+TC:wght@300;400;500&display=swap');

/* ── Root ─────────────────────────────────────────────────── */
.tfb-root {
  position: relative;
  background: linear-gradient(180deg, #3A2E20 0%, #2A2218 100%);
  /* Fill parent (which is layout's <main flex:1>, sized = viewport-header-footer).
     Falls back to a sensible min-height if parent doesn't size us. */
  height: 100%;
  min-height: 480px;
  display: flex;
  flex-direction: column;
  font-family: 'Noto Serif TC', serif;
  color: #2C2620;
  overflow: hidden;
}
.tfb-root--fullscreen {
  position: fixed;
  inset: 0;
  z-index: 1000;
}

/* ── Topbar ───────────────────────────────────────────────── */
.tfb-topbar {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  padding: 8px 20px;
  background: #1F1810;
  border-bottom: 1px solid #4A3E2C;
  color: #DBCBB0;
  flex-shrink: 0;
}
.tfb-topbar-left  { display: flex; }
.tfb-topbar-right { display: flex; justify-content: flex-end; gap: 10px; }
.tfb-topbar-center {
  display: flex;
  align-items: center;
  gap: 10px;
}

.tfb-toc-btn,
.tfb-action-btn,
.tfb-nav-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #2C2418;
  border: 1px solid #4A3E2C;
  border-radius: 4px;
  color: #DBCBB0;
  font-family: 'Noto Sans TC', sans-serif;
  font-size: 0.78rem;
  letter-spacing: 0.06em;
  cursor: pointer;
  text-decoration: none;
  transition: background 0.18s, color 0.18s, border-color 0.18s;
}
.tfb-toc-btn:hover,
.tfb-action-btn:hover,
.tfb-nav-btn:hover:not(:disabled) {
  background: #4A3E2C;
  color: #F0E2C8;
  border-color: #6A5840;
}
.tfb-nav-btn {
  width: 32px;
  height: 32px;
  justify-content: center;
  font-size: 1.2rem;
  padding: 0;
}
.tfb-nav-btn:disabled { opacity: 0.3; cursor: not-allowed; }
.tfb-toc-btn svg,
.tfb-action-btn svg { width: 13px; height: 13px; }

.tfb-page-label {
  color: #C4B89A;
  font-family: 'Noto Sans TC', sans-serif;
  font-size: 0.82rem;
  letter-spacing: 0.05em;
}
.tfb-page-input {
  width: 50px;
  text-align: center;
  background: #2C2418;
  border: 1px solid #4A3E2C;
  color: #F0E2C8;
  padding: 4px 6px;
  border-radius: 3px;
  font-size: 0.82rem;
  font-family: 'Noto Sans TC', sans-serif;
  margin: 0 4px;
}
.tfb-page-input:focus { outline: 1px solid #9A8060; }

/* ── Loading ──────────────────────────────────────────────── */
.tfb-loading {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #DBCBB0;
  font-family: 'Noto Sans TC', sans-serif;
  letter-spacing: 0.12em;
}

/* ── Body ─────────────────────────────────────────────────── */
.tfb-body {
  flex: 1;
  display: flex;
  overflow: hidden;
  min-height: 0;
}

/* ── TOC ──────────────────────────────────────────────────── */
.tfb-toc {
  width: 220px;
  flex-shrink: 0;
  background: #251E14;
  border-right: 1px solid #4A3E2C;
  overflow-y: auto;
  padding: 14px 0;
  font-family: 'Noto Sans TC', sans-serif;
}
.tfb-toc-title {
  font-size: 0.62rem;
  color: #A09280;
  letter-spacing: 0.22em;
  padding: 0 14px 8px;
  border-bottom: 1px solid #3A3025;
  margin-bottom: 6px;
}
.tfb-toc-empty {
  padding: 20px 14px;
  color: #6A6050;
  font-size: 0.7rem;
  text-align: center;
  letter-spacing: 0.06em;
}
.tfb-toc-list {
  list-style: none;
  margin: 0;
  padding: 0;
}
.tfb-toc-item {
  display: flex;
  align-items: baseline;
  gap: 5px;
  padding: 4px 14px;
  font-size: 0.74rem;
  line-height: 1.5;
  color: #C4B89A;
  cursor: pointer;
  letter-spacing: 0.03em;
  transition: background 0.15s, color 0.15s;
}
.tfb-toc-item:hover { background: #2F2618; color: #F0E2C8; }
.tfb-toc-item--active { background: #3A3025; color: #F0E2C8; font-weight: 500; }
.tfb-toc-item--lvl1 { font-weight: 600; color: #DBCBB0; font-size: 0.78rem; }
.tfb-toc-item--lvl2 { padding-left: 24px; }
.tfb-toc-item--lvl3 { padding-left: 36px; font-size: 0.7rem; }
.tfb-toc-item--lvl4 { padding-left: 48px; font-size: 0.68rem; color: #A09280; }
.tfb-toc-text {
  flex: 0 1 auto;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.tfb-toc-leader {
  flex: 1 1 auto;
  min-width: 10px;
  border-bottom: 1px dotted rgba(196, 184, 154, 0.32);
  transform: translateY(-3px);
  align-self: end;
  margin-bottom: 0.35em;
}
.tfb-toc-item--active .tfb-toc-leader { border-bottom-color: rgba(240, 226, 200, 0.5); }
.tfb-toc-page {
  flex-shrink: 0;
  font-family: 'Noto Sans TC', monospace;
  font-size: 0.66rem;
  color: #6A6050;
}
.tfb-toc-item--active .tfb-toc-page { color: #DBCBB0; }

/* ── Book ─────────────────────────────────────────────────── */
.tfb-book-wrap {
  flex: 1;
  display: grid;
  place-items: center;
  padding: 14px 20px;
  overflow: hidden;
  min-height: 0;
}
.tfb-book {
  display: grid;
  grid-template-columns: 1fr 1fr;
  aspect-ratio: 1.414 / 1;       /* A4 spread (210×2 : 297) */
  height: 100%;
  max-height: 100%;
  max-width: 100%;
  width: auto;
  background: #1A130C;
  border-radius: 4px;
  box-shadow:
    0 0 0 1px rgba(0,0,0,0.5),
    0 20px 60px rgba(0,0,0,0.5),
    inset 0 0 0 6px #2A2218,
    inset 0 0 30px rgba(0,0,0,0.4);
  position: relative;
  perspective: 1800px;
}
/* Single-page mode for cover / back cover — A4 portrait shape */
.tfb-book--single {
  grid-template-columns: 1fr;
  aspect-ratio: 0.707 / 1;
  cursor: pointer;
  background: linear-gradient(135deg, #3F2E1E 0%, #2A1E12 100%);
}
.tfb-book--single::before { display: none; }

/* ── Cover ─────────────────────────────────────────────── */
.tfb-cover {
  position: relative;
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  background:
    radial-gradient(ellipse at top, rgba(220, 195, 150, 0.08), transparent 70%),
    linear-gradient(170deg, #F4E8CE 0%, #E8D9B6 50%, #D9C698 100%);
  color: #2C2218;
  padding: 6% 8%;
  border-radius: 3px;
  box-shadow:
    inset 0 0 0 1px rgba(120, 90, 50, 0.25),
    inset 0 0 80px rgba(80, 50, 20, 0.15);
  transition: transform 0.35s ease, box-shadow 0.35s ease;
}
.tfb-cover:hover { transform: translateY(-2px); }

.tfb-cover-frame {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 8% 4%;
  border: 1px double rgba(120, 90, 50, 0.4);
  border-radius: 2px;
  background: rgba(252, 244, 224, 0.25);
}
.tfb-cover-eyebrow {
  font-family: 'Noto Sans TC', sans-serif;
  font-size: 0.75rem;
  font-weight: 400;
  color: #6A5538;
  letter-spacing: 0.5em;
  padding-left: 0.5em;
  text-transform: uppercase;
  margin-bottom: 14px;
}
.tfb-cover-rule {
  width: 60px;
  height: 1px;
  background: linear-gradient(90deg, transparent, #8A6E48, transparent);
  margin: 0 0 28px;
}
.tfb-cover-title {
  font-family: 'Noto Serif TC', 'SimSun', serif;
  font-size: clamp(1.3rem, 2.6vw, 2.1rem);
  font-weight: 700;
  letter-spacing: 0.2em;
  line-height: 1.55;
  color: #1F1610;
  margin: 0 0 14px;
  text-shadow: 0 1px 0 rgba(255,255,255,0.4);
}
.tfb-cover-title-en {
  font-family: 'Noto Serif TC', serif;
  font-size: clamp(0.78rem, 1.1vw, 0.95rem);
  font-style: italic;
  font-weight: 400;
  letter-spacing: 0.04em;
  line-height: 1.5;
  color: #5A4530;
  margin: 0 0 24px;
}
.tfb-cover-mid {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px 0;
}
.tfb-cover-ornament {
  font-size: 1.4rem;
  color: #8A6E48;
  opacity: 0.5;
}
.tfb-cover-author {
  font-family: 'Noto Serif TC', serif;
  font-size: clamp(1rem, 1.5vw, 1.2rem);
  font-weight: 500;
  letter-spacing: 0.85em;
  padding-left: 0.85em;
  color: #2C2218;
  margin: 0 0 8px;
}
.tfb-cover-supervisor {
  font-family: 'Noto Sans TC', sans-serif;
  font-size: clamp(0.72rem, 0.9vw, 0.82rem);
  font-weight: 300;
  letter-spacing: 0.18em;
  color: #5A4530;
  margin: 0 0 28px;
}
.tfb-cover-foot {
  font-family: 'Noto Serif TC', serif;
  margin-top: auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}
.tfb-cover-school {
  font-size: clamp(0.78rem, 1vw, 0.92rem);
  font-weight: 500;
  letter-spacing: 0.16em;
  color: #3A2A18;
  margin: 0;
}
.tfb-cover-year {
  font-size: clamp(0.72rem, 0.9vw, 0.82rem);
  font-weight: 400;
  letter-spacing: 0.22em;
  color: #5A4530;
  margin: 0;
}
.tfb-cover-hint {
  text-align: center;
  font-family: 'Noto Sans TC', sans-serif;
  font-size: 0.66rem;
  letter-spacing: 0.18em;
  color: rgba(106, 85, 56, 0.55);
  padding-top: 12px;
}

/* Back cover variant */
.tfb-cover--back {
  background:
    radial-gradient(ellipse at center, rgba(180, 150, 110, 0.1), transparent 70%),
    linear-gradient(170deg, #E8D9B6 0%, #D9C698 50%, #C4B080 100%);
}
.tfb-back-mark {
  font-size: 2.4rem;
  color: #6A5538;
  margin: 8% 0 4%;
  opacity: 0.6;
}
.tfb-back-archive {
  font-family: 'Noto Serif TC', serif;
  font-size: clamp(0.95rem, 1.4vw, 1.15rem);
  font-weight: 500;
  letter-spacing: 0.28em;
  padding-left: 0.28em;
  color: #2C2218;
  margin: 0 0 6px;
}
.tfb-back-archive-en {
  font-family: 'Noto Sans TC', sans-serif;
  font-size: 0.7rem;
  font-weight: 300;
  letter-spacing: 0.18em;
  color: #5A4530;
  text-transform: uppercase;
  margin: 0 0 20px;
}
.tfb-back-meta {
  font-family: 'Noto Sans TC', sans-serif;
  font-size: 0.74rem;
  font-weight: 300;
  letter-spacing: 0.14em;
  color: #3A2A18;
  margin: 0 0 6px;
}

/* ── In-page TOC entry (dot leader) ───────────────────────── */
.tfb-blk--toc {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin: 0.18em 0;
  font-family: 'Noto Serif TC', serif;
  text-indent: 0;
  line-height: 1.7;
}
.tfb-blk-toc-text {
  flex: 0 1 auto;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.tfb-blk-toc-leader {
  flex: 1 1 auto;
  min-width: 16px;
  border-bottom: 1px dotted rgba(80, 60, 30, 0.4);
  transform: translateY(-4px);
  margin-bottom: 0.45em;
}
.tfb-blk-toc-page {
  flex-shrink: 0;
  font-family: 'Noto Sans TC', 'Times New Roman', serif;
  color: #4A3A24;
}
.tfb-blk--toc-lvl1 { font-size: 1.05rem; font-weight: 600; color: #1F1A14; margin: 0.6em 0 0.25em; }
.tfb-blk--toc-lvl2 { font-size: 0.96rem; padding-left: 1.5em; }
.tfb-blk--toc-lvl3 { font-size: 0.9rem;  padding-left: 3em; color: #3A3025; }
.tfb-blk--toc-lvl4 { font-size: 0.86rem; padding-left: 4.5em; color: #4A4030; }
.tfb-book::before {
  content: '';
  position: absolute;
  left: 50%;
  top: 2%;
  bottom: 2%;
  width: 1px;
  background: linear-gradient(180deg, transparent, rgba(0,0,0,0.6), transparent);
  pointer-events: none;
}
.tfb-book--flipping .tfb-page {
  animation: tfb-flip 0.4s ease;
}
@keyframes tfb-flip {
  from { opacity: 0.6; transform: scale(0.995); }
  to   { opacity: 1;   transform: scale(1); }
}

/* ── Page ─────────────────────────────────────────────────── */
.tfb-page {
  background: linear-gradient(180deg, #FDFAF1 0%, #F8F2E2 100%);
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.tfb-page--left  {
  margin: 6px 0 6px 6px;
  box-shadow: inset -8px 0 12px -8px rgba(60, 40, 20, 0.4);
}
.tfb-page--right {
  margin: 6px 6px 6px 0;
  box-shadow: inset 8px 0 12px -8px rgba(60, 40, 20, 0.4);
}

.tfb-page-inner {
  flex: 1;
  padding: 36px 42px 18px;
  overflow: hidden;                 /* desktop: A4 fit, no scroll */
  min-height: 0;
}

.tfb-page-empty {
  text-align: center;
  color: #B8AC92;
  font-size: 0.8rem;
  margin-top: 40%;
  letter-spacing: 0.18em;
  font-style: italic;
}

.tfb-page-num {
  text-align: center;
  font-size: 0.68rem;
  color: #9A8E72;
  padding: 4px 0 10px;
  font-family: 'Noto Sans TC', sans-serif;
  letter-spacing: 0.08em;
  flex-shrink: 0;
}

/* ── Content blocks (default — fits comfortably) ──────────── */
.tfb-content {
  font-family: 'Noto Serif TC', 'SimSun', serif;
  color: #2C2620;
  line-height: 1.85;
  font-size: 0.96rem;
}

/* Chapter title */
.tfb-blk--ch {
  font-size: 1.45rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-align: center;
  margin: 0.3em 0 0.85em;
  padding-bottom: 0.35em;
  border-bottom: 1px solid #C4B89A;
  color: #1F1A14;
  line-height: 1.4;
}
/* Section title */
.tfb-blk--sec {
  font-size: 1.15rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  margin: 1.1em 0 0.45em;
  color: #2A2418;
  line-height: 1.4;
}
/* Subsection */
.tfb-blk--sub { font-weight: 600; color: #3A3025; line-height: 1.4; }
.tfb-blk--sub3 {
  font-size: 1.02rem;
  letter-spacing: 0.05em;
  margin: 0.8em 0 0.3em;
}
.tfb-blk--sub4 {
  font-size: 0.95rem;
  letter-spacing: 0.04em;
  margin: 0.65em 0 0.25em;
  font-weight: 500;
}

/* Paragraph */
.tfb-blk--p {
  text-indent: 2em;
  text-align: justify;
  margin: 0 0 0.3em;
  line-height: 1.95;
}
/* Block quote */
.tfb-blk--q {
  margin: 0.5em 0 0.5em 1.4em;
  padding: 0.35em 0 0.35em 0.9em;
  border-left: 2px solid #C4B89A;
  font-family: 'Noto Serif TC', 'DFKai-SB', 'BiauKai', serif;
  color: #4A4030;
  line-height: 1.75;
  font-size: 0.9rem;
  text-indent: 0;
}
/* List item */
.tfb-blk--li {
  margin: 0.15em 0 0.15em 1.8em;
  text-indent: 0;
  list-style: none;
  line-height: 1.75;
}

/* ── Footnotes ────────────────────────────────────────────── */
.tfb-footnotes {
  margin-top: 1.1em;
  padding-top: 0.45em;
  border-top: 1px solid #C4B89A;
  font-family: 'Noto Sans TC', sans-serif;
}
.tfb-footnote {
  font-size: 0.74rem;
  line-height: 1.55;
  color: #4A4030;
  margin: 0 0 0.25em;
  display: flex;
  gap: 6px;
  text-indent: 0;
}
.tfb-footnote-marker {
  font-size: 0.62rem;
  color: #8A7860;
  font-weight: 500;
  flex-shrink: 0;
  min-width: 1.3em;
  text-align: right;
}
.tfb-footnote-text { flex: 1; }

/* ── Overflow auto-shrink ─────────────────────────────────── */
/* level 1 — mild squeeze; level 2 — aggressive. JS picks whichever fits.
   .measure-1 / .measure-2 classes are temporarily applied by JS during
   measurement; they share the same rules so measurement matches render. */
.tfb-page.is-overflow-1 .tfb-page-inner,
.tfb-page-inner.measure-1 { padding: 28px 36px 14px; }
.tfb-page.is-overflow-1 .tfb-content,
.tfb-page-inner.measure-1 .tfb-content { font-size: 0.86rem; line-height: 1.7; }
.tfb-page.is-overflow-1 .tfb-blk--ch,
.tfb-page-inner.measure-1 .tfb-blk--ch { font-size: 1.28rem; margin: 0.2em 0 0.55em; }
.tfb-page.is-overflow-1 .tfb-blk--sec,
.tfb-page-inner.measure-1 .tfb-blk--sec { font-size: 1.05rem; margin: 0.85em 0 0.3em; }
.tfb-page.is-overflow-1 .tfb-blk--sub3,
.tfb-page-inner.measure-1 .tfb-blk--sub3 { font-size: 0.94rem; }
.tfb-page.is-overflow-1 .tfb-blk--sub4,
.tfb-page-inner.measure-1 .tfb-blk--sub4 { font-size: 0.88rem; }
.tfb-page.is-overflow-1 .tfb-blk--p,
.tfb-page-inner.measure-1 .tfb-blk--p { line-height: 1.78; margin-bottom: 0.22em; }
.tfb-page.is-overflow-1 .tfb-blk--q,
.tfb-page-inner.measure-1 .tfb-blk--q { font-size: 0.82rem; line-height: 1.6; }
.tfb-page.is-overflow-1 .tfb-footnote,
.tfb-page-inner.measure-1 .tfb-footnote { font-size: 0.66rem; line-height: 1.42; }

.tfb-page.is-overflow-2 .tfb-page-inner,
.tfb-page-inner.measure-2 { padding: 22px 28px 12px; }
.tfb-page.is-overflow-2 .tfb-content,
.tfb-page-inner.measure-2 .tfb-content { font-size: 0.76rem; line-height: 1.55; }
.tfb-page.is-overflow-2 .tfb-blk--ch,
.tfb-page-inner.measure-2 .tfb-blk--ch { font-size: 1.12rem; margin: 0.15em 0 0.42em; padding-bottom: 0.25em; }
.tfb-page.is-overflow-2 .tfb-blk--sec,
.tfb-page-inner.measure-2 .tfb-blk--sec { font-size: 0.94rem; margin: 0.6em 0 0.22em; }
.tfb-page.is-overflow-2 .tfb-blk--sub3,
.tfb-page-inner.measure-2 .tfb-blk--sub3 { font-size: 0.85rem; margin: 0.45em 0 0.15em; }
.tfb-page.is-overflow-2 .tfb-blk--sub4,
.tfb-page-inner.measure-2 .tfb-blk--sub4 { font-size: 0.8rem; margin: 0.35em 0 0.12em; }
.tfb-page.is-overflow-2 .tfb-blk--p,
.tfb-page-inner.measure-2 .tfb-blk--p { line-height: 1.6; margin-bottom: 0.14em; }
.tfb-page.is-overflow-2 .tfb-blk--q,
.tfb-page-inner.measure-2 .tfb-blk--q { font-size: 0.74rem; line-height: 1.5; margin: 0.3em 0 0.3em 1em; padding: 0.2em 0 0.2em 0.7em; }
.tfb-page.is-overflow-2 .tfb-footnote,
.tfb-page-inner.measure-2 .tfb-footnote { font-size: 0.6rem; line-height: 1.3; }
.tfb-page.is-overflow-2 .tfb-footnotes,
.tfb-page-inner.measure-2 .tfb-footnotes { margin-top: 0.6em; padding-top: 0.3em; }

/* ── Edge click zones ─────────────────────────────────────── */
.tfb-edge {
  position: absolute;
  top: 70px;
  bottom: 30px;
  width: 32px;
  cursor: pointer;
  z-index: 5;
  opacity: 0;
  transition: opacity 0.2s;
}
.tfb-edge--left  { left:  0; background: linear-gradient(90deg, rgba(200,180,140,0.18), transparent); }
.tfb-edge--right { right: 0; background: linear-gradient(270deg, rgba(200,180,140,0.18), transparent); }
.tfb-edge:hover  { opacity: 1; }
.tfb-edge--disabled { cursor: default; opacity: 0 !important; pointer-events: none; }

/* ── Responsive: mobile = single page + scroll allowed ────── */
@media (max-width: 920px) {
  .tfb-root { height: auto; min-height: 100vh; overflow: visible; }
  .tfb-body { overflow: visible; }
  .tfb-toc  { display: none; }
  .tfb-book-wrap { padding: 12px; overflow: visible; min-height: 0; }
  .tfb-book {
    grid-template-columns: 1fr;        /* single page */
    aspect-ratio: 0.707 / 1;           /* A4 portrait */
    height: auto;
    min-height: calc(100vh - 80px);
  }
  .tfb-book::before { display: none; }
  .tfb-page--right { display: none; }  /* hide right page on mobile, only left visible */
  .tfb-page-inner  { overflow-y: auto; padding: 22px 18px 14px; }
  .tfb-content  { font-size: 0.88rem; line-height: 1.75; }
  .tfb-blk--ch  { font-size: 1.15rem; }
  .tfb-blk--sec { font-size: 0.98rem; }
  .tfb-topbar   { padding: 8px 12px; }
  .tfb-action-btn span,
  .tfb-toc-btn  { font-size: 0.72rem; }
}
</style>
