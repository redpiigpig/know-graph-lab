<template>
  <div class="sd-wrap sdr-wrap">
    <header class="sdr-head">
      <div>
        <p class="sd-eyebrow">BASIC CODE · 2024.12.30</p>
        <h1 class="sd-h sdr-title">禮兵調教基本守則</h1>
      </div>
      <button type="button" class="sd-btn sd-btn--ghost sd-btn--sm" :disabled="downloading" @click="downloadOriginal">
        {{ downloading ? '準備中…' : '下載原始 DOCX' }}
      </button>
    </header>

    <div v-if="loading" class="sd-panel sdr-state">守則調閱中…</div>
    <div v-else-if="error" class="sd-error sdr-state">{{ error }}</div>
    <article v-else class="sd-panel sd-panel--raised sdr-document">
      <div class="sdr-paper" v-html="html" />
    </article>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useSoldierSession } from '~/composables/useSoldierSession'

definePageMeta({ layout: 'soldier-diary' })
useHead({ title: '禮兵調教基本守則 — 大兵日記' })

const { session, loadSession, authedFetch } = useSoldierSession()
const loading = ref(true)
const downloading = ref(false)
const html = ref('')
const error = ref('')

async function loadRules() {
  try {
    const result = await authedFetch<{ html: string }>('/api/soldier-diary/basic-rules')
    html.value = result.html
  } catch (e: any) {
    error.value = e?.data?.message || '基本守則載入失敗'
  } finally {
    loading.value = false
  }
}

async function downloadOriginal() {
  downloading.value = true
  try {
    const result = await authedFetch<{ url: string }>('/api/soldier-diary/basic-rules-download')
    window.location.assign(result.url)
  } catch (e: any) {
    error.value = e?.data?.message || '下載連結建立失敗'
  } finally {
    downloading.value = false
  }
}

onMounted(async () => {
  loadSession()
  if (!session.value) return navigateTo('/soldier-diary/login')
  await loadRules()
})
</script>

<style scoped>
.sdr-wrap { max-width: 940px; }
.sdr-head { display: flex; justify-content: space-between; align-items: flex-end; gap: 18px; margin-bottom: 16px; }
.sdr-head .sd-eyebrow { margin: 0 0 6px; }
.sdr-title { font-size: clamp(1.4rem, 4vw, 2rem); }
.sdr-state { padding: 48px 24px; text-align: center; color: var(--sd-muted); }
.sdr-document { padding: 16px; }
.sdr-paper {
  max-width: 760px; margin: 0 auto; padding: 42px 52px;
  background: #eeeadc; color: #25271e; border-radius: 2px;
  box-shadow: 0 3px 14px rgba(0,0,0,0.35);
  font-family: 'Noto Sans TC', system-ui, sans-serif;
  line-height: 1.9; letter-spacing: 0.02em;
}
.sdr-paper :deep(h1) { margin: 0 0 1.5em; text-align: center; font-size: 1.8rem; letter-spacing: 0.12em; }
.sdr-paper :deep(h2) { margin: 2em 0 0.8em; padding-bottom: 0.35em; border-bottom: 2px solid #77745e; font-size: 1.3rem; }
.sdr-paper :deep(h3) { margin: 1.6em 0 0.6em; font-size: 1.08rem; }
.sdr-paper :deep(p) { margin: 0.85em 0; text-align: justify; }
.sdr-paper :deep(strong) { color: #3e4328; }
.sdr-paper :deep(ol), .sdr-paper :deep(ul) { padding-left: 1.6em; }
.sdr-paper :deep(img) { max-width: 100%; height: auto; }

@media (max-width: 680px) {
  .sdr-head { align-items: flex-start; flex-direction: column; }
  .sdr-paper { padding: 28px 20px; font-size: 0.9rem; }
  .sdr-document { padding: 8px; }
}
</style>
