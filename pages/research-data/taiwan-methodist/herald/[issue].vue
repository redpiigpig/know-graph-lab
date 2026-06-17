<template>
  <div class="min-h-screen bg-slate-900">

    <AppHeader :title="`第 ${issue} 期`" :back="{ to: '/research-data/taiwan-methodist/herald', label: '衛報' }" container-class="max-w-7xl">
      <template #actions>
        <span class="text-xs text-gray-500">{{ meta.date_display }}<template v-if="meta.title"> · {{ meta.title }}</template></span>
        <a :href="`/api/herald/${issue}/pdf?download=1`"
           class="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-slate-100 text-slate-600 hover:bg-slate-200 transition no-underline text-xs"
           title="下載原始掃描 PDF">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5 5 5-5M12 15V3"/></svg>
          原始 PDF
        </a>
        <span class="hidden sm:inline text-xs text-gray-500">{{ currentLabel }}</span>
      </template>
    </AppHeader>

    <div class="px-4 py-8 flex flex-col items-center">

      <!-- Book frame (scrollable viewport so you can pan when zoomed in) -->
      <div class="book-viewport">
      <div class="book-stage" :style="bookSize">
        <div class="book-shadow" :style="bookSize"></div>

        <div class="book" :style="bookSize">
          <!-- LEFT PAGE -->
          <div class="page page-left" :class="{ 'is-blank': !leftItem }">
            <img v-if="leftItem?.type === 'scan'" :src="scanSrc(leftItem.idx)" class="scan-leaf" :alt="`第 ${issue} 期 第 ${leftItem.idx} 頁`" loading="lazy" />
            <component v-else-if="leftItem?.type === 'cover'" :is="CoverDesign" :issue="issue" />
            <component v-else-if="leftItem?.type === 'back'" :is="BackCoverDesign" />
            <component v-else-if="leftItem?.type === 'text'" :is="InsidePage" :issue="issue" :page-idx="leftItem.idx" side="left" />
            <div v-else class="blank-page"></div>
            <div class="page-shadow-right"></div>
          </div>

          <!-- RIGHT PAGE -->
          <div class="page page-right" :class="{ 'is-blank': !rightItem }">
            <img v-if="rightItem?.type === 'scan'" :src="scanSrc(rightItem.idx)" class="scan-leaf" :alt="`第 ${issue} 期 第 ${rightItem.idx} 頁`" loading="lazy" />
            <component v-else-if="rightItem?.type === 'cover'" :is="CoverDesign" :issue="issue" />
            <component v-else-if="rightItem?.type === 'back'" :is="BackCoverDesign" />
            <component v-else-if="rightItem?.type === 'text'" :is="InsidePage" :issue="issue" :page-idx="rightItem.idx" side="right" />
            <div v-else class="blank-page"></div>
            <div class="page-shadow-left"></div>
          </div>

          <!-- Spine -->
          <div class="book-spine"></div>

          <!-- Flip overlay (right page flipping to left when going forward) -->
          <div v-if="flip.active" class="flip-leaf" :class="flip.dir">
            <div class="flip-face flip-front">
              <img v-if="flip.front?.type === 'scan'" :src="scanSrc(flip.front.idx)" class="scan-leaf" alt="" />
              <component v-else-if="flip.front?.type === 'cover'" :is="CoverDesign" :issue="issue" />
              <component v-else-if="flip.front?.type === 'back'" :is="BackCoverDesign" />
              <component v-else-if="flip.front?.type === 'text'" :is="InsidePage" :issue="issue" :page-idx="flip.front.idx" />
            </div>
            <div class="flip-face flip-back">
              <img v-if="flip.back?.type === 'scan'" :src="scanSrc(flip.back.idx)" class="scan-leaf" alt="" />
              <component v-else-if="flip.back?.type === 'cover'" :is="CoverDesign" :issue="issue" />
              <component v-else-if="flip.back?.type === 'back'" :is="BackCoverDesign" />
              <component v-else-if="flip.back?.type === 'text'" :is="InsidePage" :issue="issue" :page-idx="flip.back.idx" />
            </div>
          </div>
        </div>

        <!-- Prev / next click zones overlaid -->
        <button class="nav-zone nav-zone-left" :disabled="spreadIdx === 0" @click="prev" aria-label="上一頁"></button>
        <button class="nav-zone nav-zone-right" :disabled="spreadIdx === lastSpread" @click="next" aria-label="下一頁"></button>
      </div>
      </div>

      <!-- Controls -->
      <div class="mt-6 flex items-center gap-3">
        <button @click="prev" :disabled="spreadIdx === 0" class="ctrl-btn">← 上一頁</button>

        <div class="px-3 py-2 rounded-lg bg-slate-800 text-gray-200 text-xs font-mono min-w-[80px] text-center">
          {{ spreadIdx + 1 }} / {{ totalSpreads }}
        </div>

        <button @click="next" :disabled="spreadIdx === lastSpread" class="ctrl-btn">下一頁 →</button>

        <div class="ml-4 hidden sm:flex items-center gap-2">
          <input type="range" min="0" :max="lastSpread" v-model.number="spreadIdx" class="range-slider" />
        </div>
      </div>

      <!-- Zoom controls -->
      <div class="mt-3 flex items-center gap-2">
        <button @click="zoomOut" :disabled="zoom <= ZOOM_MIN" class="ctrl-btn" title="縮小 (−)">－ 縮小</button>
        <div class="px-3 py-2 rounded-lg bg-slate-800 text-gray-200 text-xs font-mono min-w-[64px] text-center">
          {{ Math.round(zoom * 100) }}%
        </div>
        <button @click="zoomIn" :disabled="zoom >= ZOOM_MAX" class="ctrl-btn" title="放大 (+)">＋ 放大</button>
        <button @click="zoomReset" :disabled="zoom === 1" class="ctrl-btn" title="重設 (0)">重設</button>
      </div>

      <p class="mt-4 text-xs text-gray-500">點擊書本左右兩側可翻頁（← →）；放大縮小用下方按鈕或鍵盤 + − 0。放大後可拖動捲軸瀏覽</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onBeforeUnmount } from 'vue';
import { useRoute } from 'vue-router';
import CoverDesign from '~/components/herald/CoverDesign.vue';
import BackCoverDesign from '~/components/herald/BackCoverDesign.vue';
import InsidePage from '~/components/herald/InsidePage.vue';

definePageMeta({ middleware: 'auth' });

const route = useRoute();
const issue = String(route.params.issue);

useHead({ title: `衛報 第 ${issue} 期 — 翻頁瀏覽` });

// Per-issue manifest (public/herald/{issue}/meta.json)
interface IssueMeta {
  issue: number;
  date_display: string;
  title: string;
  page_count: number;
  mode: 'scan' | 'text';
}
const meta = ref<IssueMeta>({ issue: Number(issue), date_display: '', title: '', page_count: 0, mode: 'scan' });

const scanSrc = (idx: number) => `/herald/${issue}/page-${String(idx).padStart(2, '0')}.jpg`;

// Items are built from the manifest:
//  - scan mode: every physical page is a scan leaf
//  - text mode (issue 55): cover + structured-text inside pages + designed back cover
interface Item { type: 'cover' | 'back' | 'text' | 'scan'; idx: number; }
const items = ref<Item[]>([]);

function buildItems() {
  const n = meta.value.page_count || 0;
  const out: Item[] = [];
  if (meta.value.mode === 'text') {
    out.push({ type: 'cover', idx: 1 });
    for (let i = 2; i <= n - 1; i++) out.push({ type: 'text', idx: i });
    if (n >= 2) out.push({ type: 'back', idx: n });
  } else {
    for (let i = 1; i <= n; i++) out.push({ type: 'scan', idx: i });
  }
  items.value = out;
  spreadIdx.value = 0;
}

onMounted(async () => {
  try {
    const res = await fetch(`/herald/${issue}/meta.json`);
    if (res.ok) meta.value = { ...meta.value, ...(await res.json()) };
  } catch { /* fall back to defaults */ }
  buildItems();
});

// Spreads: spread 0 = [blank | item1], spread 1 = [item2 | item3], ..., last = [itemN | blank]
const spreads = computed<Array<[Item | null, Item | null]>>(() => {
  const arr = items.value;
  if (!arr.length) return [[null, null]];
  const s: Array<[Item | null, Item | null]> = [];
  s.push([null, arr[0]]); // closed front
  for (let i = 1; i < arr.length - 1; i += 2) {
    s.push([arr[i] ?? null, arr[i + 1] ?? null]);
  }
  s.push([arr[arr.length - 1], null]); // closed back
  return s;
});

const spreadIdx = ref(0);
const lastSpread = computed(() => spreads.value.length - 1);
const totalSpreads = computed(() => spreads.value.length);

const leftItem = computed(() => spreads.value[spreadIdx.value]?.[0] ?? null);
const rightItem = computed(() => spreads.value[spreadIdx.value]?.[1] ?? null);

const currentLabel = computed(() => {
  const l = leftItem.value, r = rightItem.value;
  if (!l && r?.type === 'cover') return '封面';
  if (l?.type === 'back' && !r) return '封底';
  if (!l && r?.type === 'scan') return '封面';
  if (l?.type === 'scan' && !r) return '封底';
  // text mode page numbering is offset by 1 (cover = leaf 1); scan mode uses raw idx
  const pageOf = (i: Item) => (i.type === 'text' ? i.idx - 1 : i.idx);
  const parts = [l, r].filter(Boolean).map(i => `p.${pageOf(i!)}`);
  return parts.join(' · ');
});

// Flip animation state
interface FlipState { active: boolean; dir: 'forward' | 'back' | ''; front: Item | null; back: Item | null; }
const flip = ref<FlipState>({ active: false, dir: '', front: null, back: null });

function next() {
  if (spreadIdx.value >= lastSpread.value || flip.value.active) return;
  const cur = spreads.value[spreadIdx.value];
  const nxt = spreads.value[spreadIdx.value + 1];
  flip.value = { active: true, dir: 'forward', front: cur[1], back: nxt[0] };
  setTimeout(() => {
    spreadIdx.value += 1;
    flip.value = { active: false, dir: '', front: null, back: null };
  }, 700);
}

function prev() {
  if (spreadIdx.value === 0 || flip.value.active) return;
  const cur = spreads.value[spreadIdx.value];
  const prv = spreads.value[spreadIdx.value - 1];
  flip.value = { active: true, dir: 'back', front: cur[0], back: prv[1] };
  setTimeout(() => {
    spreadIdx.value -= 1;
    flip.value = { active: false, dir: '', front: null, back: null };
  }, 700);
}

// Zoom
const ZOOM_MIN = 0.5;
const ZOOM_MAX = 3;
const ZOOM_STEP = 0.25;
const zoom = ref(1);
function zoomIn() { zoom.value = Math.min(ZOOM_MAX, +(zoom.value + ZOOM_STEP).toFixed(2)); }
function zoomOut() { zoom.value = Math.max(ZOOM_MIN, +(zoom.value - ZOOM_STEP).toFixed(2)); }
function zoomReset() { zoom.value = 1; }

function onKey(e: KeyboardEvent) {
  if (e.key === 'ArrowRight') next();
  else if (e.key === 'ArrowLeft') prev();
  else if (e.key === '+' || e.key === '=') zoomIn();
  else if (e.key === '-' || e.key === '_') zoomOut();
  else if (e.key === '0') zoomReset();
}
onMounted(() => window.addEventListener('keydown', onKey));
onBeforeUnmount(() => window.removeEventListener('keydown', onKey));

// Book sizing — 1:1.4 aspect ratio of a leaf, two leaves side by side.
// baseWidth fits the viewport; the displayed book is baseWidth × zoom.
const baseWidth = ref(900);
const bookWidth = computed(() => Math.round(baseWidth.value * zoom.value));
const bookHeight = computed(() => Math.round(bookWidth.value / 2 * 1.4));

function resize() {
  baseWidth.value = Math.min(window.innerWidth - 40, 1100);
}
onMounted(() => {
  resize();
  window.addEventListener('resize', resize);
});
onBeforeUnmount(() => window.removeEventListener('resize', resize));

const bookSize = computed(() => ({
  width: bookWidth.value + 'px',
  height: bookHeight.value + 'px',
}));
</script>

<style scoped>
/* Scrollable viewport: when zoomed beyond the screen, pan via scrollbars.
   Block-level container + margin:auto child centres when it fits and
   overflows to the right (not clipped on the left) when it doesn't. */
.book-viewport {
  width: 100%;
  max-width: 100%;
  overflow: auto;
  padding: 8px 60px; /* room for the off-page nav zones */
}
.book-stage {
  position: relative;
  perspective: 2000px;
  margin: 0 auto;
}
.book-shadow {
  position: absolute;
  inset: 0;
  border-radius: 6px;
  box-shadow: 0 30px 80px rgba(0, 0, 0, 0.55), 0 10px 30px rgba(0, 0, 0, 0.35);
  z-index: 0;
}
.book {
  position: relative;
  display: grid;
  grid-template-columns: 1fr 1fr;
  background: #1a1a1a;
  transform-style: preserve-3d;
  z-index: 1;
}
.page {
  position: relative;
  background: #fff;
  overflow: hidden;
  display: flex;
  align-items: stretch;
  justify-content: center;
}
.page.is-blank {
  background: #2a2a2a;
}
.blank-page {
  width: 100%;
  height: 100%;
  background: #2a2a2a;
}
.page img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  display: block;
  background: #fff;
}
/* Scanned-page leaves: show the whole page, never crop */
.scan-leaf {
  width: 100%;
  height: 100%;
  object-fit: contain !important;
  background: #fff;
  display: block;
}
.page-shadow-right {
  position: absolute;
  top: 0; right: 0; bottom: 0;
  width: 24px;
  background: linear-gradient(to right, rgba(0, 0, 0, 0) 0%, rgba(0, 0, 0, 0.18) 100%);
  pointer-events: none;
}
.page-shadow-left {
  position: absolute;
  top: 0; left: 0; bottom: 0;
  width: 24px;
  background: linear-gradient(to left, rgba(0, 0, 0, 0) 0%, rgba(0, 0, 0, 0.18) 100%);
  pointer-events: none;
}
.book-spine {
  position: absolute;
  top: 0; bottom: 0;
  left: 50%;
  width: 6px;
  transform: translateX(-50%);
  background: linear-gradient(to right, rgba(0, 0, 0, 0.25), rgba(0, 0, 0, 0.55), rgba(0, 0, 0, 0.25));
  z-index: 5;
  pointer-events: none;
}
/* Side click zones only — leave middle selectable */
.nav-zone {
  position: absolute;
  top: 0; bottom: 0;
  width: 60px;
  background: transparent;
  border: 0;
  cursor: pointer;
  z-index: 10;
  transition: background 0.15s;
}
.nav-zone:hover:not(:disabled) {
  background: linear-gradient(to right, rgba(255,255,255,0.05), transparent);
}
.nav-zone:disabled { cursor: default; }
.nav-zone-left { left: -60px; }
.nav-zone-right { right: -60px;
  background: linear-gradient(to left, rgba(255,255,255,0.0), transparent);
}
.nav-zone::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 24px;
  height: 24px;
  transform: translate(-50%, -50%);
  border-top: 3px solid rgba(255,255,255,0.5);
  border-right: 3px solid rgba(255,255,255,0.5);
  border-radius: 2px;
}
.nav-zone-left::after  { transform: translate(-50%, -50%) rotate(225deg); }
.nav-zone-right::after { transform: translate(-50%, -50%) rotate(45deg); }
.nav-zone:hover:not(:disabled)::after { border-color: rgba(255,255,255,0.95); }
.nav-zone:disabled::after { opacity: 0.15; }

/* Flip leaf */
.flip-leaf {
  position: absolute;
  top: 0;
  width: 50%;
  height: 100%;
  transform-style: preserve-3d;
  z-index: 20;
  transition: transform 0.7s cubic-bezier(0.4, 0.0, 0.2, 1);
  pointer-events: none;
}
.flip-leaf.forward {
  left: 50%;
  transform-origin: left center;
  animation: flipForward 0.7s cubic-bezier(0.4, 0.0, 0.2, 1) forwards;
}
.flip-leaf.back {
  left: 0;
  transform-origin: right center;
  animation: flipBack 0.7s cubic-bezier(0.4, 0.0, 0.2, 1) forwards;
}
@keyframes flipForward {
  0% { transform: rotateY(0deg); }
  100% { transform: rotateY(-180deg); }
}
@keyframes flipBack {
  0% { transform: rotateY(0deg); }
  100% { transform: rotateY(180deg); }
}
.flip-face {
  position: absolute;
  inset: 0;
  backface-visibility: hidden;
  background: #fff;
  overflow: hidden;
}
.flip-face img {
  width: 100%; height: 100%;
  object-fit: cover;
}
.flip-back {
  transform: rotateY(180deg);
}

.ctrl-btn {
  @apply px-4 py-2 rounded-lg bg-slate-700 text-gray-200 text-xs font-medium hover:bg-slate-600 transition disabled:opacity-30 disabled:cursor-not-allowed;
}
.range-slider {
  width: 200px;
  accent-color: #a78bd9;
}
</style>
