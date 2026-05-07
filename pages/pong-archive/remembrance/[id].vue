<template>
  <div class="rv-page">

    <div class="rv-topbar">
      <NuxtLink to="/pong-archive/remembrance" class="rv-back">← 回憶與緬懷</NuxtLink>
    </div>

    <div v-if="pending" class="rv-loading">載入中…</div>
    <div v-else-if="!item" class="rv-loading">找不到此文章。</div>

    <template v-else>

      <header class="rv-header">
        <div class="rv-header-inner">
          <div class="rv-meta">
            <span class="rv-cat-badge">{{ categoryLabel }}</span>
            <span v-if="item.source" class="rv-source">{{ item.source }}</span>
            <span v-if="item.published_at" class="rv-date">{{ formatDate(item.published_at) }}</span>
          </div>
          <h1 class="rv-title">{{ item.title }}</h1>
          <p v-if="item.author" class="rv-author">文／{{ item.author }}</p>
          <a
            v-if="item.source_url"
            :href="item.source_url"
            target="_blank"
            rel="noopener"
            class="rv-source-link"
          >前往原始出處 ↗</a>
        </div>
      </header>

      <article class="rv-body">
        <div class="rv-body-inner">
          <div class="rv-content" v-html="renderContent(item.content)" />
        </div>
      </article>

      <footer class="rv-footer">
        <div class="rv-footer-inner">
          <a v-if="item.source_url" :href="item.source_url" target="_blank" rel="noopener" class="rv-footer-link">
            原始出處：{{ item.source }} ↗
          </a>
          <NuxtLink to="/pong-archive/remembrance" class="rv-footer-back">← 返回列表</NuxtLink>
        </div>
      </footer>

    </template>

  </div>
</template>

<script setup>
definePageMeta({ layout: 'pong-archive' })

const route = useRoute()

const CATEGORY_LABELS = {
  tribute:   '緬懷文',
  interview: '訪談錄',
}

const item    = ref(null)
const pending = ref(true)

onMounted(async () => {
  try {
    item.value = await $fetch(`/api/pong-remembrance/${route.params.id}`)
  } catch (e) {
    console.error(e)
  } finally {
    pending.value = false
  }
})

const categoryLabel = computed(() => CATEGORY_LABELS[item.value?.category] || item.value?.category || '')

function formatDate(dateStr) {
  if (!dateStr) return ''
  const [y, m, d] = dateStr.split('-').map(Number)
  return `${y} 年 ${m} 月 ${d} 日`
}

function renderContent(text) {
  if (!text) return ''
  if (text.trimStart().startsWith('<')) return text
  return text
    .split('\n\n')
    .filter(p => p.trim())
    .map(p => `<p>${p.replace(/\n/g, '<br>')}</p>`)
    .join('')
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500&family=Noto+Serif+TC:wght@400;500;600&display=swap');

.rv-page { background-color: #F9F8F6; min-height: 100vh; font-family: 'Noto Sans TC', sans-serif; color: #2C2C2C; }

/* ── Topbar ─────────────────────────────────────────────── */
.rv-topbar { padding: 20px 48px; border-bottom: 1px solid #DDD8CF; }
.rv-back { font-size: 0.8rem; color: #8A8278; text-decoration: none; letter-spacing: 0.06em; transition: color 0.2s; }
.rv-back:hover { color: #3A3025; }

/* ── Loading ──────────────────────────────────────────────── */
.rv-loading { text-align: center; color: #A09280; font-size: 0.9rem; padding: 100px 40px; letter-spacing: 0.06em; }

/* ── Header ─────────────────────────────────────────────── */
.rv-header { background: #F2EFE9; border-bottom: 1px solid #E8E4DC; padding: 56px 40px 48px; }
.rv-header-inner { max-width: 800px; margin: 0 auto; }

.rv-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px 16px;
  margin-bottom: 20px;
}
.rv-cat-badge {
  font-size: 0.65rem;
  font-weight: 500;
  color: #FFF;
  background-color: #7A6E5A;
  padding: 3px 10px;
  border-radius: 2px;
  letter-spacing: 0.1em;
}
.rv-source {
  font-size: 0.68rem;
  font-weight: 500;
  color: #9A8E7E;
  letter-spacing: 0.14em;
  background: #EAE4D8;
  padding: 3px 10px;
  border-radius: 2px;
}
.rv-date {
  font-size: 0.78rem;
  font-weight: 300;
  color: #8A8278;
  letter-spacing: 0.06em;
}

.rv-title {
  font-family: 'Noto Serif TC', serif;
  font-size: clamp(1.4rem, 3vw, 1.9rem);
  font-weight: 500;
  color: #2C2C2C;
  letter-spacing: 0.06em;
  line-height: 1.7;
  margin: 0 0 12px;
}
.rv-author {
  font-size: 0.88rem;
  font-weight: 300;
  color: #7A7268;
  letter-spacing: 0.06em;
  font-style: italic;
  margin: 0 0 20px;
}
.rv-source-link {
  display: inline-block;
  font-size: 0.75rem;
  color: #9A8E7E;
  text-decoration: none;
  border-bottom: 1px solid #C4B99A;
  padding-bottom: 1px;
  letter-spacing: 0.08em;
  transition: color 0.2s;
}
.rv-source-link:hover { color: #3A3025; }

/* ── Body ────────────────────────────────────────────────── */
.rv-body { padding: 56px 40px 48px; }
.rv-body-inner { max-width: 800px; margin: 0 auto; }

.rv-content {
  font-family: 'Noto Serif TC', serif;
  font-size: 1rem;
  line-height: 2.15;
  color: #3A3025;
}
.rv-content :deep(p) {
  text-indent: 2em;
  margin-bottom: 1em;
}
.rv-content :deep(p:first-child) { text-indent: 0; }

/* ── Footer ──────────────────────────────────────────────── */
.rv-footer { border-top: 1px solid #E8E4DC; padding: 32px 40px 48px; }
.rv-footer-inner {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}
.rv-footer-link {
  font-size: 0.8rem;
  color: #7A6E5A;
  text-decoration: none;
  letter-spacing: 0.06em;
  border-bottom: 1px solid #C4B99A;
  padding-bottom: 1px;
  transition: color 0.2s;
}
.rv-footer-link:hover { color: #3A3025; }
.rv-footer-back {
  font-size: 0.78rem;
  color: #8A8278;
  text-decoration: none;
  letter-spacing: 0.06em;
  transition: color 0.2s;
}
.rv-footer-back:hover { color: #3A3025; }

/* ── Responsive ──────────────────────────────────────────── */
@media (max-width: 600px) {
  .rv-topbar { padding: 16px 20px; }
  .rv-header { padding: 40px 20px 36px; }
  .rv-body { padding: 36px 20px 40px; }
  .rv-footer { padding: 24px 20px 40px; }
  .rv-footer-inner { flex-direction: column-reverse; align-items: flex-start; }
}
</style>
