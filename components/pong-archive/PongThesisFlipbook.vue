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
        <button class="tfb-nav-btn" :disabled="leftPage <= 1" @click="prev" title="上一頁 (←)">‹</button>
        <span class="tfb-page-label">
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
        </span>
        <button class="tfb-nav-btn" :disabled="rightPage >= totalPages" @click="next" title="下一頁 (→)">›</button>
      </div>

      <div class="tfb-topbar-right">
        <a :href="pdfUrl" target="_blank" rel="noopener" class="tfb-action-btn" title="開啟原版 PDF">
          <svg viewBox="0 0 16 16" fill="none" aria-hidden="true">
            <rect x="2" y="1" width="12" height="14" rx="1.5" stroke="currentColor" stroke-width="1.2" fill="none"/>
            <line x1="4.5" y1="5.5" x2="11.5" y2="5.5" stroke="currentColor" stroke-width="1"/>
            <line x1="4.5" y1="8"   x2="11.5" y2="8"   stroke="currentColor" stroke-width="1"/>
            <line x1="4.5" y1="10.5" x2="9"   y2="10.5" stroke="currentColor" stroke-width="1"/>
          </svg>
          原版
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

      <!-- TOC sidebar -->
      <aside v-show="tocOpen" class="tfb-toc">
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
            <span class="tfb-toc-page">{{ o.page }}</span>
          </li>
        </ul>
      </aside>

      <!-- Book -->
      <div class="tfb-book-wrap">
        <div class="tfb-book" :class="{ 'tfb-book--flipping': flipping }">

          <!-- Left page -->
          <article class="tfb-page tfb-page--left">
            <div class="tfb-page-inner">
              <div class="tfb-content" v-if="leftBlocks">
                <template v-for="(b, i) in bodyBlocks(leftBlocks)" :key="`L${i}`">
                  <component :is="blockTag(b)" :class="blockClass(b)">{{ b.text }}</component>
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
          <article class="tfb-page tfb-page--right">
            <div class="tfb-page-inner">
              <div class="tfb-content" v-if="rightBlocks">
                <template v-for="(b, i) in bodyBlocks(rightBlocks)" :key="`R${i}`">
                  <component :is="blockTag(b)" :class="blockClass(b)">{{ b.text }}</component>
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
  writingId: { type: [Number, String], required: true },
  outline:   { type: Array, default: () => [] },
  totalPages: { type: Number, default: 0 },
  pdfUrl:    { type: String, default: '' },
})

const pages = ref([])              // array of { page, blocks }
const pagesByNumber = ref(new Map())
const loading = ref(true)
const leftPage = ref(1)            // 1-based; left page is odd-numbered (1, 3, 5…)
const flipping = ref(false)
const tocOpen = ref(true)
const fullscreen = ref(false)
const jumpInput = ref(1)

const totalPages = computed(() => Math.max(props.totalPages || pages.value.length, pages.value.length))
const rightPage = computed(() => leftPage.value + 1)

// Spread convention: left odd (1, 3, 5…), right even (2, 4, 6…).
// So a fresh book opens to page 1 on the right with a blank cover-left.
// We use the simpler "left=odd / right=even" model that thesis-style books
// use (book opens like 1+2, 3+4, 5+6, …).

const leftBlocks = computed(() => pagesByNumber.value.get(leftPage.value)?.blocks ?? null)
const rightBlocks = computed(() => pagesByNumber.value.get(rightPage.value)?.blocks ?? null)

function bodyBlocks(blocks) {
  return (blocks || []).filter(b => b.type !== 'footnote' && b.type !== 'page_number')
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
  const target = clampLeft(n % 2 === 0 ? n - 1 : n)
  if (target === leftPage.value) return
  flipping.value = true
  setTimeout(() => { flipping.value = false }, 380)
  leftPage.value = target
  jumpInput.value = target
}

function prev() { if (leftPage.value > 1) goPage(leftPage.value - 2) }
function next() { if (rightPage.value < totalPages.value) goPage(leftPage.value + 2) }

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

onMounted(async () => {
  window.addEventListener('keydown', onKey)
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
})
onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKey)
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;500;600;700&family=Noto+Sans+TC:wght@300;400;500&display=swap');

/* ── Root ─────────────────────────────────────────────────── */
.tfb-root {
  position: relative;
  background: linear-gradient(180deg, #3A2E20 0%, #2A2218 100%);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  font-family: 'Noto Serif TC', serif;
  color: #2C2620;
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
  padding: 12px 24px;
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
}

/* ── TOC ──────────────────────────────────────────────────── */
.tfb-toc {
  width: 280px;
  flex-shrink: 0;
  background: #251E14;
  border-right: 1px solid #4A3E2C;
  overflow-y: auto;
  padding: 18px 0;
  font-family: 'Noto Sans TC', sans-serif;
}
.tfb-toc-title {
  font-size: 0.7rem;
  color: #A09280;
  letter-spacing: 0.22em;
  padding: 0 18px 12px;
  border-bottom: 1px solid #3A3025;
  margin-bottom: 10px;
}
.tfb-toc-empty {
  padding: 30px 18px;
  color: #6A6050;
  font-size: 0.78rem;
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
  justify-content: space-between;
  align-items: baseline;
  gap: 10px;
  padding: 6px 18px;
  font-size: 0.82rem;
  color: #C4B89A;
  cursor: pointer;
  letter-spacing: 0.04em;
  transition: background 0.15s, color 0.15s;
}
.tfb-toc-item:hover { background: #2F2618; color: #F0E2C8; }
.tfb-toc-item--active { background: #3A3025; color: #F0E2C8; font-weight: 500; }
.tfb-toc-item--lvl1 { font-weight: 600; color: #DBCBB0; }
.tfb-toc-item--lvl2 { padding-left: 32px; }
.tfb-toc-item--lvl3 { padding-left: 46px; font-size: 0.76rem; }
.tfb-toc-item--lvl4 { padding-left: 60px; font-size: 0.74rem; color: #A09280; }
.tfb-toc-text { flex: 1; }
.tfb-toc-page {
  font-family: 'Noto Sans TC', monospace;
  font-size: 0.7rem;
  color: #6A6050;
}

/* ── Book ─────────────────────────────────────────────────── */
.tfb-book-wrap {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 28px 40px;
  overflow: auto;
}
.tfb-book {
  display: grid;
  grid-template-columns: 1fr 1fr;
  width: min(100%, 1100px);
  aspect-ratio: 1.45 / 1;
  background: #1A130C;
  border-radius: 4px;
  box-shadow:
    0 0 0 1px rgba(0,0,0,0.5),
    0 20px 60px rgba(0,0,0,0.5),
    inset 0 0 0 8px #2A2218,
    inset 0 0 30px rgba(0,0,0,0.4);
  position: relative;
  perspective: 1800px;
}
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
  padding: 56px 56px 36px;
  overflow-y: auto;
  scrollbar-gutter: stable;
}
.tfb-page-inner::-webkit-scrollbar { width: 6px; }
.tfb-page-inner::-webkit-scrollbar-thumb { background: rgba(120, 100, 70, 0.25); border-radius: 3px; }

.tfb-page-empty {
  text-align: center;
  color: #B8AC92;
  font-size: 0.82rem;
  margin-top: 40%;
  letter-spacing: 0.18em;
  font-style: italic;
}

.tfb-page-num {
  text-align: center;
  font-size: 0.72rem;
  color: #9A8E72;
  padding: 8px 0 12px;
  font-family: 'Noto Sans TC', sans-serif;
  letter-spacing: 0.08em;
}

/* ── Content blocks ───────────────────────────────────────── */
.tfb-content {
  font-family: 'Noto Serif TC', 'SimSun', serif;
  color: #2C2620;
  line-height: 1.9;
  font-size: 1rem;
}

/* Chapter title */
.tfb-blk--ch {
  font-size: 1.6rem;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-align: center;
  margin: 0.4em 0 1em;
  padding-bottom: 0.4em;
  border-bottom: 1px solid #C4B89A;
  color: #1F1A14;
}
/* Section title */
.tfb-blk--sec {
  font-size: 1.25rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  margin: 1.4em 0 0.6em;
  color: #2A2418;
}
/* Subsection */
.tfb-blk--sub { font-weight: 600; color: #3A3025; }
.tfb-blk--sub3 {
  font-size: 1.08rem;
  letter-spacing: 0.06em;
  margin: 1em 0 0.4em;
}
.tfb-blk--sub4 {
  font-size: 1rem;
  letter-spacing: 0.04em;
  margin: 0.8em 0 0.3em;
  font-weight: 500;
}

/* Paragraph */
.tfb-blk--p {
  text-indent: 2em;
  text-align: justify;
  margin: 0 0 0.35em;
  line-height: 2;
}
/* Block quote */
.tfb-blk--q {
  margin: 0.6em 0 0.6em 1.5em;
  padding: 0.4em 0 0.4em 1em;
  border-left: 3px solid #C4B89A;
  font-family: 'Noto Serif TC', 'DFKai-SB', 'BiauKai', serif;
  color: #4A4030;
  line-height: 1.85;
  font-size: 0.96rem;
  text-indent: 0;
}
/* List item */
.tfb-blk--li {
  margin: 0.2em 0 0.2em 2em;
  text-indent: 0;
  list-style: none;
  line-height: 1.85;
}

/* ── Footnotes ────────────────────────────────────────────── */
.tfb-footnotes {
  margin-top: 2em;
  padding-top: 0.6em;
  border-top: 1px solid #C4B89A;
  font-family: 'Noto Sans TC', sans-serif;
}
.tfb-footnote {
  font-size: 0.74rem;
  line-height: 1.7;
  color: #4A4030;
  margin: 0 0 0.35em;
  display: flex;
  gap: 6px;
  text-indent: 0;
}
.tfb-footnote-marker {
  font-size: 0.62rem;
  color: #8A7860;
  font-weight: 500;
  flex-shrink: 0;
  min-width: 1.4em;
  text-align: right;
}
.tfb-footnote-text { flex: 1; }

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

/* ── Responsive ───────────────────────────────────────────── */
@media (max-width: 920px) {
  .tfb-toc { display: none; }
  .tfb-book-wrap { padding: 16px; }
  .tfb-page-inner { padding: 32px 24px 20px; }
  .tfb-blk--ch  { font-size: 1.3rem; }
  .tfb-blk--sec { font-size: 1.1rem; }
  .tfb-content  { font-size: 0.94rem; }
  .tfb-topbar   { padding: 10px 14px; }
}
</style>
