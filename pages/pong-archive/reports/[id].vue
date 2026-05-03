<template>
  <div class="rd-page">

    <div class="rd-topbar">
      <NuxtLink to="/pong-archive/reports" class="rd-back">← 相關報導</NuxtLink>
    </div>

    <div v-if="pending" class="rd-loading">載入中…</div>

    <div v-else-if="!report" class="rd-empty">找不到此報導</div>

    <template v-else>

      <header class="rd-header">
        <div class="rd-header-inner">
          <div class="rd-meta">
            <span class="rd-source">{{ report.source }}</span>
            <span v-if="report.published_at" class="rd-date">{{ formatDate(report.published_at) }}</span>
            <span v-if="report.author" class="rd-author">{{ report.author }}</span>
          </div>
          <h1 class="rd-title">{{ report.title }}</h1>
          <a
            v-if="report.source_url"
            :href="report.source_url"
            target="_blank"
            rel="noopener"
            class="rd-source-link"
          >
            前往原始報導 ↗
          </a>
        </div>
      </header>

      <article class="rd-body">
        <div class="rd-body-inner">
          <div class="rd-content" v-html="renderContent(report.content)"></div>
        </div>
      </article>

      <footer class="rd-footer">
        <div class="rd-footer-inner">
          <a v-if="report.source_url" :href="report.source_url" target="_blank" rel="noopener" class="rd-footer-link">
            原始報導：{{ report.source }} ↗
          </a>
          <NuxtLink to="/pong-archive/reports" class="rd-footer-back">← 返回報導列表</NuxtLink>
        </div>
      </footer>

    </template>

  </div>
</template>

<script setup>
import { createClient } from '@supabase/supabase-js'

definePageMeta({ layout: 'pong-archive' })

const route = useRoute()
const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_KEY
)

const { data: report, pending } = await useAsyncData(
  `pong-report-${route.params.id}`,
  async () => {
    const { data, error } = await supabase
      .from('pong_reports')
      .select('*')
      .eq('id', route.params.id)
      .eq('is_published', true)
      .single()
    if (error) return null
    return data
  }
)

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()} 年 ${d.getMonth() + 1} 月 ${d.getDate()} 日`
}

function renderContent(text) {
  if (!text) return ''
  if (text.trimStart().startsWith('<')) return text
  return text
    .split('\n\n')
    .filter(p => p.trim())
    .map(p => `<p>${p.replace(/\n/g, '')}</p>`)
    .join('')
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500&family=Noto+Serif+TC:wght@400;500;600&display=swap');

.rd-page { background-color: #F9F8F6; min-height: 100vh; font-family: 'Noto Sans TC', sans-serif; color: #2C2C2C; }

/* ── Topbar ─────────────────────────────────────────────── */
.rd-topbar { padding: 20px 48px; border-bottom: 1px solid #DDD8CF; }
.rd-back { font-size: 0.8rem; color: #8A8278; text-decoration: none; letter-spacing: 0.06em; transition: color 0.2s; }
.rd-back:hover { color: #3A3025; }

/* ── Loading / Empty ──────────────────────────────────── */
.rd-loading, .rd-empty { max-width: 720px; margin: 80px auto; text-align: center; font-size: 0.9rem; color: #A09280; letter-spacing: 0.06em; }

/* ── Header ─────────────────────────────────────────────── */
.rd-header { background: #F2EFE9; border-bottom: 1px solid #E8E4DC; padding: 56px 40px 48px; }
.rd-header-inner { max-width: 800px; margin: 0 auto; }

.rd-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px 16px;
  margin-bottom: 20px;
}
.rd-source {
  font-size: 0.68rem;
  font-weight: 500;
  color: #9A8E7E;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  background: #EAE4D8;
  padding: 3px 10px;
  border-radius: 2px;
}
.rd-date, .rd-author {
  font-size: 0.78rem;
  font-weight: 300;
  color: #8A8278;
  letter-spacing: 0.06em;
}
.rd-date::before { content: ''; }
.rd-author::before { content: ''; }

.rd-title {
  font-family: 'Noto Serif TC', serif;
  font-size: clamp(1.3rem, 3vw, 1.7rem);
  font-weight: 500;
  color: #2C2C2C;
  letter-spacing: 0.06em;
  line-height: 1.7;
  margin: 0 0 24px;
}

.rd-source-link {
  display: inline-block;
  font-size: 0.75rem;
  color: #9A8E7E;
  text-decoration: none;
  border-bottom: 1px solid #C4B99A;
  padding-bottom: 1px;
  letter-spacing: 0.08em;
  transition: color 0.2s;
}
.rd-source-link:hover { color: #3A3025; }

/* ── Body ────────────────────────────────────────────────── */
.rd-body { padding: 56px 40px 48px; }
.rd-body-inner { max-width: 800px; margin: 0 auto; }

.rd-content {
  font-family: 'Noto Serif TC', serif;
  font-size: 1rem;
  line-height: 2.15;
  color: #3A3025;
}
.rd-content :deep(p) {
  text-indent: 2em;
  margin-bottom: 1em;
}
.rd-content :deep(p:first-child) { text-indent: 0; }

/* ── Footer ──────────────────────────────────────────────── */
.rd-footer { border-top: 1px solid #E8E4DC; padding: 32px 40px 48px; }
.rd-footer-inner {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}
.rd-footer-link {
  font-size: 0.8rem;
  color: #7A6E5A;
  text-decoration: none;
  letter-spacing: 0.06em;
  border-bottom: 1px solid #C4B99A;
  padding-bottom: 1px;
  transition: color 0.2s;
}
.rd-footer-link:hover { color: #3A3025; }
.rd-footer-back {
  font-size: 0.78rem;
  color: #8A8278;
  text-decoration: none;
  letter-spacing: 0.06em;
  transition: color 0.2s;
}
.rd-footer-back:hover { color: #3A3025; }

/* ── Responsive ──────────────────────────────────────────── */
@media (max-width: 600px) {
  .rd-topbar { padding: 16px 20px; }
  .rd-header { padding: 40px 20px 36px; }
  .rd-body { padding: 36px 20px 40px; }
  .rd-footer { padding: 24px 20px 40px; }
  .rd-footer-inner { flex-direction: column-reverse; align-items: flex-start; }
}
</style>
