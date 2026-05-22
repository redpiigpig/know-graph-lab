<template>
  <div class="inside-page">
    <div class="paper">
      <div v-if="loading" class="loading">載入中…</div>
      <div v-else-if="error" class="error-fallback">
        <div class="error-hint">本頁文字尚未完成 OCR · 顯示原始掃描</div>
        <img :src="scanSrc" class="scan-img" :alt="`page ${pageNumber}`" />
      </div>
      <template v-else>
        <!-- Running header (top): magazine page header on every inside page -->
        <div class="running-header">
          <span class="rh-page" :class="isLeftPage ? 'rh-left' : 'rh-right'">
            <template v-if="isLeftPage">{{ pageNumber }}</template>
          </span>
          <span class="rh-title" :class="isLeftPage ? 'rh-title-right' : 'rh-title-left'">{{ runningHeader }}</span>
          <span class="rh-page" :class="isLeftPage ? 'rh-right' : 'rh-left'" v-if="!isLeftPage">{{ pageNumber }}</span>
        </div>

        <!-- Body content -->
        <div class="content" v-html="rendered"></div>

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
import { ref, computed, watch, onMounted } from 'vue';

const props = defineProps<{
  issue: string;
  pageIdx: number; // 2..23, used to fetch page-02.txt..page-23.txt
  side?: 'left' | 'right';
}>();

const isLeftPage = computed(() => props.side === 'left');

const pageNumber = computed(() => props.pageIdx - 1);
const scanSrc = computed(() => `/herald/${props.issue}/page-${String(props.pageIdx).padStart(2, '0')}.jpg`);

const text = ref('');
const loading = ref(true);
const error = ref('');

async function load() {
  loading.value = true;
  error.value = '';
  try {
    const url = `/herald/${props.issue}/text/page-${String(props.pageIdx).padStart(2, '0')}.txt`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`找不到文字檔 (${res.status})`);
    text.value = (await res.text()).trim();
  } catch (e: any) {
    error.value = e?.message ?? '載入失敗';
  } finally {
    loading.value = false;
  }
}

onMounted(load);
watch(() => [props.issue, props.pageIdx], load);

const RUNNING_HEADER_PATTERNS = [
  /^文化取向/,  // matches "文化取向的宣教 ..." running header
];

function isRunningHeaderLine(line: string): boolean {
  return RUNNING_HEADER_PATTERNS.some(re => re.test(line));
}

function isAsterisks(line: string): boolean {
  return /^[*＊]{3,}$/.test(line);
}

function joinLines(lines: string[]): string {
  // Join visually-broken lines within a Chinese paragraph.
  // Insert a space between lines only when both sides are ASCII letters/digits
  // (to keep English/page-number readable). Otherwise concatenate directly.
  let out = '';
  for (let i = 0; i < lines.length; i++) {
    const cur = lines[i].trim();
    if (!cur) continue;
    if (!out) {
      out = cur;
      continue;
    }
    const prevEnd = out[out.length - 1];
    const curStart = cur[0];
    const needsSpace = /[A-Za-z0-9]/.test(prevEnd) && /[A-Za-z0-9]/.test(curStart);
    out += (needsSpace ? ' ' : '') + cur;
  }
  return out;
}

// Extract running header from first line(s), group blank-separated chunks into paragraphs
const parsed = computed(() => {
  const raw = text.value.replace(/\r\n?/g, '\n');
  // Split into paragraphs by blank lines (one or more empty lines)
  const chunks = raw.split(/\n\s*\n+/).map(c => c.split(/\n/).map(s => s.trim()).filter(Boolean));

  let header = '';
  const paragraphs: string[] = [];

  for (const chunk of chunks) {
    if (!chunk.length) continue;

    // Strip running header if present at chunk start
    const filtered = chunk.filter((line, idx) => {
      if (idx === 0 && !header && isRunningHeaderLine(line)) {
        header = line;
        return false;
      }
      return true;
    });
    if (!filtered.length) continue;

    // Asterisk separator chunk → keep as separator paragraph
    if (filtered.length === 1 && isAsterisks(filtered[0])) {
      paragraphs.push('___SEP___');
      continue;
    }

    paragraphs.push(joinLines(filtered));
  }
  return { header, paragraphs };
});

const runningHeader = computed(() => parsed.value.header || '文化取向的宣教 國度視野的牧養');

const rendered = computed(() => {
  const paras = parsed.value.paragraphs;
  if (!paras.length) return '';
  const out: string[] = [];
  for (const p of paras) {
    if (p === '___SEP___') {
      out.push(`<div class="sep">＊＊＊＊＊＊＊＊＊＊</div>`);
      continue;
    }
    const isCnHeader = /^[一二三四五六七八九十]+、/.test(p);
    const isMainTitle = isCnHeader && p.length <= 24;
    if (isMainTitle) {
      out.push(`<h2 class="sec">${escapeHtml(p)}</h2>`);
    } else {
      out.push(`<p>${escapeHtml(p)}</p>`);
    }
  }
  return out.join('\n');
});

function escapeHtml(s: string): string {
  return s.replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]!));
}
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
  padding: 3cqh 6cqw 3cqh 6cqw;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  font-family: 'Noto Serif TC', 'Source Han Serif TC', 'PMingLiU', 'Times New Roman', serif;
  color: #1a1a1a;
  user-select: text;
}
.loading {
  margin: auto;
  color: #999;
  font-size: 2cqw;
}
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
  border-bottom: 1px solid #f0e7d3;
}
.scan-img {
  flex: 1;
  width: 100%;
  object-fit: contain;
  background: #f5f5f0;
}

/* Running header bar (top of every inside page) */
.running-header {
  display: flex;
  align-items: baseline;
  font-size: 1.5cqw;
  color: #666;
  padding-bottom: 1cqh;
  margin-bottom: 2cqh;
  letter-spacing: 0.05em;
  user-select: text;
}
.rh-page {
  flex: 0 0 auto;
  font-family: 'Times New Roman', serif;
  font-size: 1.6cqw;
  color: #555;
  min-width: 2em;
}
.rh-left { text-align: left; }
.rh-right { text-align: right; }
.rh-title {
  flex: 1;
  color: #555;
}
.rh-title-right { text-align: right; }
.rh-title-left  { text-align: left; padding-left: 1em; }

.content {
  flex: 1;
  overflow: hidden;
  font-size: 1.95cqw;
  line-height: 1.7;
  letter-spacing: 0.02em;
  text-align: justify;
  text-justify: inter-ideograph;
  user-select: text;
}
.content :deep(.sec) {
  text-align: center;
  font-size: 2.6cqw;
  font-weight: 700;
  margin: 0 0 1.6cqw 0;
  letter-spacing: 0.3em;
  padding-left: 0.3em;
}
.content :deep(p) {
  margin: 0 0 0.8cqw 0;
  text-indent: 2em;
}
.content :deep(.sep) {
  text-align: center;
  letter-spacing: 0.4em;
  color: #888;
  margin: 1cqw 0;
  font-size: 1.7cqw;
  text-indent: 0;
}

/* Running footer (bottom) */
.running-footer {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  font-size: 1.4cqw;
  color: #666;
  padding-top: 1cqh;
  margin-top: 1cqh;
  font-family: 'Times New Roman', serif;
  letter-spacing: 0.05em;
}
.rf-page {
  flex: 1;
  text-align: center;
  font-size: 1.6cqw;
  color: #444;
}
.rf-date {
  position: absolute;
  right: 7cqw;
  bottom: 3cqh;
  font-size: 1.4cqw;
  color: #888;
}
</style>
