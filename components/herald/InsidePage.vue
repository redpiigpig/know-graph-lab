<template>
  <div class="inside-page">
    <div class="paper">
      <div v-if="loading" class="loading">載入中…</div>

      <div v-else-if="error" class="error-fallback">
        <div class="error-hint">本頁文字尚未 OCR · 顯示原始掃描</div>
        <img :src="scanSrc" class="scan-img" :alt="`page ${pageNumber}`" />
      </div>

      <template v-else>
        <!-- Running header (top of every inside page) -->
        <div class="running-header">
          <span v-if="isLeftPage" class="rh-page">{{ pageNumber }}</span>
          <span class="rh-title" :class="isLeftPage ? 'rh-title-right' : 'rh-title-left'">{{ data.running_header || '文化取向的宣教 國度視野的牧養' }}</span>
          <span v-if="!isLeftPage" class="rh-page rh-page-right">{{ pageNumber }}</span>
        </div>

        <!-- Section marker e.g. 「四、衛理宗消息」 -->
        <div v-if="data.section_marker" class="section-marker">
          <div class="section-line"></div>
          {{ data.section_marker }}
          <div class="section-line"></div>
        </div>

        <!-- Article-level heading area: eyebrow / title / subtitle_en / author -->
        <div v-if="data.eyebrow || data.title || data.subtitle_en || data.author" class="article-head">
          <div v-if="data.eyebrow" class="art-eyebrow">{{ data.eyebrow }}</div>
          <div v-if="data.title" class="art-title">{{ data.title }}</div>
          <div v-if="data.subtitle_en" class="art-subtitle-en">{{ data.subtitle_en }}</div>
          <div v-if="data.author" class="art-author">{{ data.author }}</div>
        </div>

        <!-- Date / scripture-ref line if any -->
        <div v-if="data.date_line" class="date-line">{{ data.date_line }}</div>
        <div v-if="data.scripture_ref" class="scripture-ref">{{ data.scripture_ref }}</div>

        <!-- Body: rendered in 1 or 2 columns; font auto-shrinks if overflow -->
        <div ref="bodyEl" class="body" :class="`cols-${data.columns || 1}`" :style="{ fontSize: `${bodyFontCqw}cqw` }">
          <template v-for="(b, i) in data.blocks || []" :key="i">
            <h3 v-if="b.type === 'subsection'" class="sub">{{ b.text }}</h3>
            <div v-else-if="b.type === 'separator'" class="sep">＊＊＊＊＊＊＊＊＊＊</div>
            <blockquote v-else-if="b.type === 'blockquote'" class="bq">{{ b.text }}</blockquote>
            <div v-else-if="b.type === 'scripture_attribution'" class="attrib">{{ b.text }}</div>
            <p v-else>{{ b.text }}</p>
          </template>
        </div>

        <!-- Running footer -->
        <div class="running-footer">
          <span class="rf-page">{{ pageNumber }}</span>
          <span class="rf-date">2002-11-30</span>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick, onBeforeUnmount } from 'vue';

interface Block {
  type: 'paragraph' | 'subsection' | 'separator' | 'blockquote' | 'scripture_attribution';
  text?: string;
}
interface PageData {
  running_header?: string;
  section_marker?: string;
  eyebrow?: string;
  title?: string;
  subtitle_en?: string;
  author?: string;
  date_line?: string;
  scripture_ref?: string;
  columns?: 1 | 2;
  blocks?: Block[];
}

const props = defineProps<{
  issue: string;
  pageIdx: number; // 2..23
  side?: 'left' | 'right';
}>();

const isLeftPage = computed(() => props.side === 'left');
const pageNumber = computed(() => props.pageIdx - 1);
const scanSrc = computed(() => `/herald/${props.issue}/page-${String(props.pageIdx).padStart(2, '0')}.jpg`);

const data = ref<PageData>({});
const loading = ref(true);
const error = ref('');

const bodyEl = ref<HTMLElement | null>(null);
const MAX_BODY_FONT = 2.4;     // starts large to fill page
const MIN_BODY_FONT = 1.4;     // floor; below this is unreadable
const FONT_STEP = 0.05;
const bodyFontCqw = ref(MAX_BODY_FONT);

async function load() {
  loading.value = true;
  error.value = '';
  data.value = {};
  bodyFontCqw.value = MAX_BODY_FONT;
  try {
    const url = `/herald/${props.issue}/data/page-${String(props.pageIdx).padStart(2, '0')}.json`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`找不到資料 (${res.status})`);
    data.value = await res.json();
  } catch (e: any) {
    error.value = e?.message ?? '載入失敗';
  } finally {
    loading.value = false;
    await nextTick();
    fitFont();
    // Re-observe new body element if it changed
    if (ro && bodyEl.value) {
      ro.disconnect();
      ro.observe(bodyEl.value);
    }
  }
}

function fitFont() {
  const el = bodyEl.value;
  if (!el) return;
  // Reset to max and shrink until content fits
  let f = MAX_BODY_FONT;
  bodyFontCqw.value = f;
  // Force layout
  void el.offsetHeight;
  let guard = 30;
  while (el.scrollHeight > el.clientHeight + 1 && f > MIN_BODY_FONT && guard-- > 0) {
    f = Math.max(MIN_BODY_FONT, +(f - FONT_STEP).toFixed(2));
    bodyFontCqw.value = f;
    void el.offsetHeight;
  }
}

let ro: ResizeObserver | null = null;
onMounted(() => {
  load();
  // Refit on container resize (e.g. window resize → bookWidth changes)
  if (typeof ResizeObserver !== 'undefined') {
    ro = new ResizeObserver(() => fitFont());
    if (bodyEl.value) ro.observe(bodyEl.value);
  }
});
onBeforeUnmount(() => ro?.disconnect());

watch(() => [props.issue, props.pageIdx], load);
</script>

<style scoped>
.inside-page {
  width: 100%;
  height: 100%;
  background: #ffffff;
  position: relative;
  container-type: size;
  user-select: text;
}
.paper {
  position: absolute;
  inset: 0;
  padding: 2.5cqh 5cqw 3cqh 5cqw;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  font-family: 'Noto Serif TC', 'Source Han Serif TC', 'PMingLiU', 'Times New Roman', serif;
  color: #1a1a1a;
  user-select: text;
}
.loading { margin: auto; color: #999; font-size: 2cqw; }

.error-fallback {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
}
.error-hint {
  padding: 1cqh 2cqw;
  font-size: 1.6cqw;
  color: #888;
  text-align: center;
  background: #fff8ed;
}
.scan-img { flex: 1; width: 100%; object-fit: contain; background: #f5f5f0; }

/* Running header */
.running-header {
  display: flex;
  align-items: baseline;
  font-size: 1.5cqw;
  color: #666;
  margin-bottom: 2cqh;
  letter-spacing: 0.05em;
}
.rh-page {
  font-family: 'Times New Roman', serif;
  font-size: 1.6cqw;
  color: #555;
  min-width: 2em;
}
.rh-page-right { text-align: right; margin-left: auto; }
.rh-title {
  flex: 1;
  color: #555;
}
.rh-title-right { text-align: right; }
.rh-title-left  { text-align: left; padding-left: 1em; }

/* Big section marker like 「四、衛理宗消息」 */
.section-marker {
  text-align: center;
  font-size: 3cqw;
  font-weight: 500;
  letter-spacing: 0.4em;
  padding-left: 0.4em;
  margin: 1cqh 0 2cqh 0;
  display: flex;
  align-items: center;
  gap: 2cqw;
  color: #1a1a1a;
}
.section-line {
  flex: 1;
  height: 0.15cqw;
  background: #333;
}

/* Article head */
.article-head {
  text-align: center;
  margin-bottom: 2cqh;
}
.art-eyebrow {
  font-size: 1.8cqw;
  color: #444;
  letter-spacing: 0.3em;
  margin-bottom: 1cqh;
}
.art-title {
  font-size: 2.8cqw;
  font-weight: 700;
  color: #1a1a1a;
  line-height: 1.4;
  margin-bottom: 0.6cqh;
  letter-spacing: 0.05em;
}
.art-subtitle-en {
  font-family: 'Georgia', 'Times New Roman', serif;
  font-style: italic;
  font-size: 1.9cqw;
  color: #333;
  margin-bottom: 0.8cqh;
  line-height: 1.4;
}
.art-author {
  font-family: 'Georgia', 'Times New Roman', 'Noto Serif TC', serif;
  font-style: italic;
  font-size: 1.7cqw;
  color: #555;
  margin-bottom: 1cqh;
}

/* Date / scripture refs */
.date-line {
  text-align: center;
  font-size: 2cqw;
  color: #333;
  margin-bottom: 1cqh;
}
.scripture-ref {
  text-align: center;
  font-size: 1.9cqw;
  color: #444;
  margin-bottom: 1.6cqh;
  letter-spacing: 0.02em;
}

/* Body: 1 or 2 column */
.body {
  flex: 1;
  overflow: hidden;
  /* font-size is set inline via :style for auto-fit */
  line-height: 1.6;
  letter-spacing: 0.02em;
  text-align: justify;
  text-justify: inter-ideograph;
  user-select: text;
}
.body.cols-2 {
  column-count: 2;
  column-gap: 4cqw;
  column-rule: 0.15cqw solid #d8d8d8;
}
.body p {
  margin: 0 0 0.3em 0;
  text-indent: 2em;
  break-inside: avoid-column;
}
.body .sub {
  font-size: 1.15em;
  font-weight: 700;
  text-indent: 0;
  margin: 0.6em 0 0.2em 0;
  letter-spacing: 0.05em;
}
.body .sep {
  text-align: center;
  letter-spacing: 0.4em;
  color: #888;
  margin: 0.4em 0;
  font-size: 0.85em;
  text-indent: 0;
}
.body .bq {
  padding-left: 2em;
  color: #333;
  font-size: 0.95em;
  text-indent: 0;
  margin: 0 0 0.4em 0;
}
.body .attrib {
  text-align: right;
  font-size: 0.95em;
  color: #444;
  text-indent: 0;
  margin: 0.4em 0 0 0;
}

/* Running footer */
.running-footer {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  font-size: 1.4cqw;
  color: #666;
  padding-top: 1cqh;
  margin-top: 1cqh;
  font-family: 'Times New Roman', serif;
}
.rf-page {
  flex: 1;
  text-align: center;
  font-size: 1.6cqw;
  color: #444;
}
.rf-date {
  position: absolute;
  right: 5cqw;
  bottom: 3cqh;
  font-size: 1.4cqw;
  color: #888;
}
</style>
