<template>
  <div class="min-h-screen bg-slate-900">

    <nav class="bg-slate-800 border-b border-slate-700 sticky top-0 z-40">
      <div class="max-w-7xl mx-auto px-6 h-14 flex items-center gap-4">
        <NuxtLink to="/research-data/taiwan-methodist/herald" class="text-gray-400 hover:text-white transition text-sm">← 衛理報</NuxtLink>
        <span class="text-gray-600">|</span>
        <span class="text-sm font-medium text-gray-200">第 {{ issue }} 期</span>
        <span class="text-xs text-gray-500">2002/11/30 · 將臨節第一主日</span>
        <div class="ml-auto flex items-center gap-3 text-xs text-gray-300">
          <span>{{ currentLabel }}</span>
        </div>
      </div>
    </nav>

    <div class="px-4 py-8 flex flex-col items-center">

      <!-- Book frame -->
      <div class="book-stage" :style="bookSize">
        <div class="book-shadow" :style="bookSize"></div>

        <div class="book" :style="bookSize">
          <!-- LEFT PAGE -->
          <div class="page page-left" :class="{ 'is-blank': !leftItem }">
            <component v-if="leftItem?.type === 'cover'" :is="CoverDesign" :issue="issue" />
            <component v-else-if="leftItem?.type === 'back'" :is="BackCoverDesign" />
            <img v-else-if="leftItem?.type === 'scan'" :src="leftItem.src" :alt="`page ${leftItem.idx}`" />
            <div v-else class="blank-page"></div>
            <div class="page-shadow-right"></div>
          </div>

          <!-- RIGHT PAGE -->
          <div class="page page-right" :class="{ 'is-blank': !rightItem }">
            <component v-if="rightItem?.type === 'cover'" :is="CoverDesign" :issue="issue" />
            <component v-else-if="rightItem?.type === 'back'" :is="BackCoverDesign" />
            <img v-else-if="rightItem?.type === 'scan'" :src="rightItem.src" :alt="`page ${rightItem.idx}`" />
            <div v-else class="blank-page"></div>
            <div class="page-shadow-left"></div>
          </div>

          <!-- Spine -->
          <div class="book-spine"></div>

          <!-- Flip overlay (right page flipping to left when going forward) -->
          <div v-if="flip.active" class="flip-leaf" :class="flip.dir">
            <div class="flip-face flip-front">
              <component v-if="flip.front?.type === 'cover'" :is="CoverDesign" :issue="issue" />
              <component v-else-if="flip.front?.type === 'back'" :is="BackCoverDesign" />
              <img v-else-if="flip.front?.type === 'scan'" :src="flip.front.src" />
            </div>
            <div class="flip-face flip-back">
              <component v-if="flip.back?.type === 'cover'" :is="CoverDesign" :issue="issue" />
              <component v-else-if="flip.back?.type === 'back'" :is="BackCoverDesign" />
              <img v-else-if="flip.back?.type === 'scan'" :src="flip.back.src" />
            </div>
          </div>
        </div>

        <!-- Prev / next click zones overlaid -->
        <button class="nav-zone nav-zone-left" :disabled="spreadIdx === 0" @click="prev" aria-label="上一頁"></button>
        <button class="nav-zone nav-zone-right" :disabled="spreadIdx === lastSpread" @click="next" aria-label="下一頁"></button>
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

      <p class="mt-4 text-xs text-gray-500">點擊書本左右兩側可翻頁，或使用鍵盤左右方向鍵</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onBeforeUnmount } from 'vue';
import { useRoute } from 'vue-router';
import CoverDesign from '~/components/herald/CoverDesign.vue';
import BackCoverDesign from '~/components/herald/BackCoverDesign.vue';

definePageMeta({ middleware: 'auth' });

const route = useRoute();
const issue = String(route.params.issue);

useHead({ title: `衛報 第 ${issue} 期 — 翻頁瀏覽` });

// Items: 1 cover + 22 inside + 1 back = 24
interface Item { type: 'cover' | 'back' | 'scan'; src?: string; idx: number; }
const items: Item[] = [];
items.push({ type: 'cover', idx: 1 });
for (let i = 2; i <= 23; i++) items.push({ type: 'scan', idx: i, src: `/herald/${issue}/page-${String(i).padStart(2, '0')}.jpg` });
items.push({ type: 'back', idx: 24 });

// Spreads: spread 0 = [blank | cover], spread 1 = [item2 | item3], ..., spread 12 = [item24 | blank]
const spreads = computed<Array<[Item | null, Item | null]>>(() => {
  const s: Array<[Item | null, Item | null]> = [];
  s.push([null, items[0]]); // closed front
  for (let i = 1; i < items.length - 1; i += 2) {
    s.push([items[i] ?? null, items[i + 1] ?? null]);
  }
  s.push([items[items.length - 1], null]); // closed back
  return s;
});

const spreadIdx = ref(0);
const lastSpread = computed(() => spreads.value.length - 1);
const totalSpreads = computed(() => spreads.value.length);

const leftItem = computed(() => spreads.value[spreadIdx.value][0]);
const rightItem = computed(() => spreads.value[spreadIdx.value][1]);

const currentLabel = computed(() => {
  const l = leftItem.value, r = rightItem.value;
  if (!l && r?.type === 'cover') return '封面';
  if (l?.type === 'back' && !r) return '封底';
  const parts = [l, r].filter(Boolean).map(i => `p.${i!.idx - 1}`);
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

function onKey(e: KeyboardEvent) {
  if (e.key === 'ArrowRight') next();
  else if (e.key === 'ArrowLeft') prev();
}
onMounted(() => window.addEventListener('keydown', onKey));
onBeforeUnmount(() => window.removeEventListener('keydown', onKey));

// Book sizing — 1:1.4 aspect ratio of a leaf, two leaves side by side
const bookWidth = ref(900);
const bookHeight = computed(() => Math.round(bookWidth.value / 2 * 1.4));

function resize() {
  const w = Math.min(window.innerWidth - 40, 1100);
  bookWidth.value = w;
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
.nav-zone {
  position: absolute;
  top: 0; bottom: 0;
  width: 50%;
  background: transparent;
  border: 0;
  cursor: pointer;
  z-index: 10;
}
.nav-zone:disabled { cursor: default; }
.nav-zone-left { left: 0; }
.nav-zone-right { right: 0; }

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
