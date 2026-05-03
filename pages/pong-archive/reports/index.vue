<template>
  <div class="rp-page">

    <div class="rp-topbar">
      <NuxtLink to="/pong-archive" class="rp-back">← 返回典藏首頁</NuxtLink>
    </div>

    <header class="rp-header">
      <p class="rp-eyebrow">Press &amp; Reports</p>
      <h1 class="rp-title">相關報導</h1>
      <p class="rp-subtitle">各方媒體對龐君華會督事奉生涯的採訪與報導</p>
    </header>

    <section class="rp-list">
      <div class="rp-list-inner">

        <div v-if="pending" class="rp-loading">載入中…</div>

        <template v-else>
          <article
            v-for="item in reports"
            :key="item.id"
            class="rp-item"
          >
            <div class="rp-item-meta">
              <span class="rp-item-source">{{ item.source }}</span>
              <span v-if="item.published_at" class="rp-item-date">{{ formatDate(item.published_at) }}</span>
            </div>
            <h2 class="rp-item-title">
              <NuxtLink v-if="item.content" :to="`/pong-archive/reports/${item.id}`" class="rp-item-link">
                {{ item.title }}
              </NuxtLink>
              <a v-else :href="item.source_url" target="_blank" rel="noopener" class="rp-item-link rp-item-link--ext">
                {{ item.title }}
                <span class="rp-ext-icon">↗</span>
              </a>
            </h2>
            <p v-if="item.summary" class="rp-item-summary">{{ item.summary }}</p>
            <div class="rp-item-footer">
              <NuxtLink v-if="item.content" :to="`/pong-archive/reports/${item.id}`" class="rp-item-read">
                閱讀全文 →
              </NuxtLink>
              <a v-else :href="item.source_url" target="_blank" rel="noopener" class="rp-item-read rp-item-read--ext">
                前往原始報導 ↗
              </a>
              <a v-if="item.source_url" :href="item.source_url" target="_blank" rel="noopener" class="rp-item-source-link">
                {{ item.source }}
              </a>
            </div>
          </article>
        </template>

      </div>
    </section>

  </div>
</template>

<script setup>
import { createClient } from '@supabase/supabase-js'

definePageMeta({ layout: 'pong-archive' })

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_KEY
)

const { data: reports, pending } = await useAsyncData('pong-reports-list', async () => {
  const { data, error } = await supabase
    .from('pong_reports')
    .select('id, title, source, source_url, author, published_at, summary, content')
    .eq('is_published', true)
    .order('sort_order')
  if (error) return []
  return data
})

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()} 年 ${d.getMonth() + 1} 月`
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500&family=Noto+Serif+TC:wght@400;500;600&display=swap');

.rp-page { background-color: #F9F8F6; min-height: 100vh; font-family: 'Noto Sans TC', sans-serif; color: #2C2C2C; }

/* ── Topbar ─────────────────────────────────────────────── */
.rp-topbar { padding: 20px 48px; border-bottom: 1px solid #DDD8CF; }
.rp-back { font-size: 0.8rem; color: #8A8278; text-decoration: none; letter-spacing: 0.06em; transition: color 0.2s; }
.rp-back:hover { color: #3A3025; }

/* ── Header ─────────────────────────────────────────────── */
.rp-header { text-align: center; padding: 56px 40px 40px; border-bottom: 1px solid #E8E4DC; }
.rp-eyebrow { font-size: 0.72rem; font-weight: 300; color: #A09280; letter-spacing: 0.22em; text-transform: uppercase; margin: 0 0 10px; }
.rp-title { font-family: 'Noto Serif TC', serif; font-size: 2rem; font-weight: 500; color: #2C2C2C; letter-spacing: 0.12em; margin: 0 0 10px; }
.rp-subtitle { font-size: 0.85rem; font-weight: 300; color: #7A7268; letter-spacing: 0.06em; margin: 0; }

/* ── List ────────────────────────────────────────────────── */
.rp-list { padding: 48px 40px 80px; }
.rp-list-inner { max-width: 800px; margin: 0 auto; display: flex; flex-direction: column; gap: 0; }
.rp-loading { text-align: center; color: #A09280; font-size: 0.9rem; padding: 80px 0; letter-spacing: 0.06em; }

/* ── Article item ─────────────────────────────────────────── */
.rp-item {
  padding: 36px 0;
  border-bottom: 1px solid #E8E4DC;
}
.rp-item:first-child { border-top: 1px solid #E8E4DC; }

.rp-item-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.rp-item-source {
  font-size: 0.68rem;
  font-weight: 500;
  color: #9A8E7E;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  background: #EEE8DC;
  padding: 3px 10px;
  border-radius: 2px;
}
.rp-item-date {
  font-size: 0.72rem;
  font-weight: 300;
  color: #A09280;
  letter-spacing: 0.06em;
}

.rp-item-title { margin: 0 0 12px; line-height: 1.6; }
.rp-item-link {
  font-family: 'Noto Serif TC', serif;
  font-size: 1.1rem;
  font-weight: 500;
  color: #2C2C2C;
  text-decoration: none;
  letter-spacing: 0.04em;
  transition: color 0.2s;
}
.rp-item-link:hover { color: #7A6E5A; }
.rp-ext-icon { font-size: 0.8em; margin-left: 4px; opacity: 0.6; }

.rp-item-summary {
  font-size: 0.88rem;
  font-weight: 300;
  color: #5A5550;
  line-height: 1.9;
  letter-spacing: 0.04em;
  margin: 0 0 20px;
}

.rp-item-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.rp-item-read {
  font-size: 0.78rem;
  color: #7A6E5A;
  text-decoration: none;
  letter-spacing: 0.08em;
  font-weight: 500;
  transition: color 0.2s;
}
.rp-item-read:hover { color: #3A3025; }
.rp-item-source-link {
  font-size: 0.68rem;
  color: #B0A690;
  text-decoration: none;
  letter-spacing: 0.06em;
  border-bottom: 1px solid #DDD8CF;
  padding-bottom: 1px;
  transition: color 0.2s;
}
.rp-item-source-link:hover { color: #7A6E5A; }

/* ── Responsive ──────────────────────────────────────────── */
@media (max-width: 600px) {
  .rp-topbar { padding: 16px 20px; }
  .rp-header { padding: 40px 20px 32px; }
  .rp-list { padding: 32px 20px 60px; }
  .rp-item-link { font-size: 1rem; }
  .rp-item-footer { flex-direction: column; align-items: flex-start; gap: 10px; }
}
</style>
