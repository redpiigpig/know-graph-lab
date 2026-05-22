<template>
  <div class="inside-page">
    <div class="paper">
      <div v-if="loading" class="loading">載入中…</div>
      <div v-else-if="error" class="error-fallback">
        <div class="error-msg">{{ error }}</div>
        <div class="error-hint">本頁文字尚未完成 OCR · 顯示原始掃描</div>
        <img :src="scanSrc" class="scan-img" :alt="`page ${pageNumber}`" />
      </div>
      <div v-else class="content" v-html="rendered"></div>

      <!-- Footer with page number and date (hidden in scan fallback) -->
      <div v-if="!error" class="page-footer">
        <div class="footer-left">{{ pageNumber }}</div>
        <div class="footer-right">2002-11-30</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';

const props = defineProps<{
  issue: string;
  pageIdx: number; // 2..23, used to fetch page-02.txt..page-23.txt
}>();

// Magazine inner page number is pageIdx - 1 (page-02.jpg => 編者案頭 = p.1)
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

// Render text: lines beginning with 一、 二、 etc become headers; blank lines split paragraphs
const rendered = computed(() => {
  if (!text.value) return '';
  const lines = text.value.split(/\n+/);
  const out: string[] = [];
  for (const raw of lines) {
    const line = raw.trim();
    if (!line) continue;
    // Section header: 一、二、三、…  or Roman numerals or numbered like "1."
    const isCnHeader = /^[一二三四五六七八九十]+、/.test(line);
    const isMainTitle = isCnHeader && line.length <= 24;
    if (isMainTitle) {
      out.push(`<h2 class="sec">${escapeHtml(line)}</h2>`);
    } else {
      out.push(`<p>${escapeHtml(line)}</p>`);
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
}
.paper {
  position: absolute;
  inset: 0;
  padding: 7cqh 8cqw 6cqh 8cqw;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  font-family: 'Noto Serif TC', 'Source Han Serif TC', 'PMingLiU', 'Times New Roman', serif;
  color: #1a1a1a;
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
.error-msg {
  display: none;
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
.content {
  flex: 1;
  overflow: hidden;
  font-size: 2.3cqw;
  line-height: 1.95;
  letter-spacing: 0.02em;
  text-align: justify;
  text-justify: inter-ideograph;
}
.content :deep(.sec) {
  text-align: center;
  font-size: 3cqw;
  font-weight: 700;
  margin: 0 0 2.5cqw 0;
  letter-spacing: 0.3em;
  padding-left: 0.3em;
}
.content :deep(p) {
  margin: 0 0 1.2cqw 0;
  text-indent: 2em;
}
.page-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 1.6cqw;
  color: #555;
  padding-top: 2cqh;
  border-top: 0;
  font-family: 'Times New Roman', serif;
}
.footer-left {
  flex: 1;
  text-align: center;
}
.footer-right {
  position: absolute;
  right: 8cqw;
  bottom: 3cqh;
  font-size: 1.4cqw;
}
</style>
