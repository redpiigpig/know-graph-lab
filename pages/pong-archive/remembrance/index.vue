<template>
  <div class="rm-page">

    <div class="rm-topbar">
      <NuxtLink to="/pong-archive" class="rm-back">← 返回典藏首頁</NuxtLink>
    </div>

    <header class="rm-header">
      <p class="rm-eyebrow">Remembrance</p>
      <h1 class="rm-title">回憶與緬懷</h1>
      <p class="rm-subtitle">各方友人、同工對龐君華牧師的訪談紀錄與追念文字</p>
    </header>

    <div v-if="pending" class="rm-loading">載入中…</div>

    <template v-else>

      <!-- ── 緬懷文 ─────────────────────────────────────── -->
      <section v-if="tributes.length" class="rm-section">
        <div class="rm-section-inner">
          <h2 class="rm-section-title">
            <span class="rm-section-line" />
            緬懷文
            <span class="rm-section-line" />
          </h2>
          <div class="rm-list">
            <article
              v-for="item in tributes"
              :key="item.id"
              class="rm-item"
            >
              <div class="rm-item-meta">
                <span v-if="item.source" class="rm-item-source">{{ item.source }}</span>
                <span v-if="item.published_at" class="rm-item-date">{{ formatDate(item.published_at) }}</span>
              </div>
              <h3 class="rm-item-title">
                <NuxtLink v-if="item.content" :to="`/pong-archive/remembrance/${item.id}`" class="rm-item-link">
                  {{ item.title }}
                </NuxtLink>
                <a v-else-if="item.source_url" :href="item.source_url" target="_blank" rel="noopener" class="rm-item-link rm-item-link--ext">
                  {{ item.title }} <span class="rm-ext-icon">↗</span>
                </a>
                <span v-else class="rm-item-link rm-item-link--plain">{{ item.title }}</span>
              </h3>
              <p v-if="item.author" class="rm-item-author">文／{{ item.author }}</p>
              <p v-if="item.summary" class="rm-item-summary">{{ item.summary }}</p>
              <div class="rm-item-footer">
                <NuxtLink v-if="item.content" :to="`/pong-archive/remembrance/${item.id}`" class="rm-item-read">
                  閱讀全文 →
                </NuxtLink>
                <a v-else-if="item.source_url" :href="item.source_url" target="_blank" rel="noopener" class="rm-item-read rm-item-read--ext">
                  前往原文 ↗
                </a>
              </div>
            </article>
          </div>
        </div>
      </section>

      <!-- ── 訪談錄 ─────────────────────────────────────── -->
      <section v-if="interviews.length" class="rm-section">
        <div class="rm-section-inner">
          <h2 class="rm-section-title">
            <span class="rm-section-line" />
            訪談錄
            <span class="rm-section-line" />
          </h2>
          <div class="rm-list">
            <article
              v-for="item in interviews"
              :key="item.id"
              class="rm-item"
            >
              <div class="rm-item-meta">
                <span v-if="item.source" class="rm-item-source">{{ item.source }}</span>
                <span v-if="item.published_at" class="rm-item-date">{{ formatDate(item.published_at) }}</span>
              </div>
              <h3 class="rm-item-title">
                <NuxtLink v-if="item.content" :to="`/pong-archive/remembrance/${item.id}`" class="rm-item-link">
                  {{ item.title }}
                </NuxtLink>
                <a v-else-if="item.source_url" :href="item.source_url" target="_blank" rel="noopener" class="rm-item-link rm-item-link--ext">
                  {{ item.title }} <span class="rm-ext-icon">↗</span>
                </a>
                <span v-else class="rm-item-link rm-item-link--plain">{{ item.title }}</span>
              </h3>
              <p v-if="item.author" class="rm-item-author">文／{{ item.author }}</p>
              <p v-if="item.summary" class="rm-item-summary">{{ item.summary }}</p>
              <div class="rm-item-footer">
                <NuxtLink v-if="item.content" :to="`/pong-archive/remembrance/${item.id}`" class="rm-item-read">
                  閱讀全文 →
                </NuxtLink>
                <a v-else-if="item.source_url" :href="item.source_url" target="_blank" rel="noopener" class="rm-item-read rm-item-read--ext">
                  前往原文 ↗
                </a>
              </div>
            </article>
          </div>
        </div>
      </section>

      <div v-if="!tributes.length && !interviews.length" class="rm-loading">
        尚無收錄文章。
      </div>

    </template>

  </div>
</template>

<script setup>
import { createClient } from '@supabase/supabase-js'

definePageMeta({ layout: 'pong-archive' })

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_KEY
)

const { data: items, pending } = await useAsyncData('pong-remembrances', async () => {
  const { data, error } = await supabase
    .from('pong_remembrance')
    .select('id, title, author, source, source_url, published_at, category, summary, content')
    .eq('is_published', true)
    .order('sort_order')
  if (error) return []
  return data
})

const tributes   = computed(() => (items.value || []).filter(i => i.category === 'tribute'))
const interviews = computed(() => (items.value || []).filter(i => i.category === 'interview'))

function formatDate(dateStr) {
  if (!dateStr) return ''
  const [y, m, d] = dateStr.split('-').map(Number)
  return `${y} 年 ${m} 月 ${d} 日`
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500&family=Noto+Serif+TC:wght@400;500;600&display=swap');

.rm-page { background-color: #F9F8F6; min-height: 100vh; font-family: 'Noto Sans TC', sans-serif; color: #2C2C2C; }

/* ── Topbar ─────────────────────────────────────────────── */
.rm-topbar { padding: 20px 48px; border-bottom: 1px solid #DDD8CF; }
.rm-back { font-size: 0.8rem; color: #8A8278; text-decoration: none; letter-spacing: 0.06em; transition: color 0.2s; }
.rm-back:hover { color: #3A3025; }

/* ── Header ─────────────────────────────────────────────── */
.rm-header { text-align: center; padding: 56px 40px 40px; border-bottom: 1px solid #E8E4DC; }
.rm-eyebrow { font-size: 0.72rem; font-weight: 300; color: #A09280; letter-spacing: 0.22em; text-transform: uppercase; margin: 0 0 10px; }
.rm-title { font-family: 'Noto Serif TC', serif; font-size: 2rem; font-weight: 500; color: #2C2C2C; letter-spacing: 0.12em; margin: 0 0 10px; }
.rm-subtitle { font-size: 0.85rem; font-weight: 300; color: #7A7268; letter-spacing: 0.06em; margin: 0; }

.rm-loading { text-align: center; color: #A09280; font-size: 0.9rem; padding: 80px 40px; letter-spacing: 0.06em; }

/* ── Section ─────────────────────────────────────────────── */
.rm-section { padding: 56px 40px 0; }
.rm-section:last-of-type { padding-bottom: 80px; }
.rm-section-inner { max-width: 800px; margin: 0 auto; }

.rm-section-title {
  display: flex;
  align-items: center;
  gap: 16px;
  font-family: 'Noto Serif TC', serif;
  font-size: 1.05rem;
  font-weight: 500;
  color: #6A5E4A;
  letter-spacing: 0.18em;
  margin: 0 0 36px;
}
.rm-section-line {
  flex: 1;
  height: 1px;
  background-color: #DDD8CF;
}

/* ── List ────────────────────────────────────────────────── */
.rm-list { display: flex; flex-direction: column; gap: 0; }

/* ── Article item ─────────────────────────────────────────── */
.rm-item {
  padding: 32px 0;
  border-bottom: 1px solid #EAE6DF;
}
.rm-item:first-child { border-top: 1px solid #EAE6DF; }

.rm-item-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}
.rm-item-source {
  font-size: 0.68rem;
  font-weight: 500;
  color: #9A8E7E;
  letter-spacing: 0.14em;
  background: #EEE8DC;
  padding: 3px 10px;
  border-radius: 2px;
}
.rm-item-date {
  font-size: 0.72rem;
  font-weight: 300;
  color: #A09280;
  letter-spacing: 0.06em;
}

.rm-item-title { margin: 0 0 6px; line-height: 1.6; }
.rm-item-link {
  font-family: 'Noto Serif TC', serif;
  font-size: 1.15rem;
  font-weight: 500;
  color: #2C2C2C;
  text-decoration: none;
  letter-spacing: 0.04em;
  transition: color 0.2s;
}
.rm-item-link:hover { color: #7A6E5A; }
.rm-item-link--plain { cursor: default; }
.rm-ext-icon { font-size: 0.8em; margin-left: 4px; opacity: 0.6; }

.rm-item-author {
  font-size: 0.8rem;
  font-weight: 300;
  color: #8A8278;
  letter-spacing: 0.05em;
  margin: 0 0 10px;
  font-style: italic;
}

.rm-item-summary {
  font-size: 0.88rem;
  font-weight: 300;
  color: #5A5550;
  line-height: 1.9;
  letter-spacing: 0.04em;
  margin: 0 0 18px;
}

.rm-item-footer { display: flex; align-items: center; gap: 16px; }
.rm-item-read {
  font-size: 0.78rem;
  color: #7A6E5A;
  text-decoration: none;
  letter-spacing: 0.08em;
  font-weight: 500;
  transition: color 0.2s;
}
.rm-item-read:hover { color: #3A3025; }

/* ── Responsive ──────────────────────────────────────────── */
@media (max-width: 600px) {
  .rm-topbar { padding: 16px 20px; }
  .rm-header { padding: 40px 20px 32px; }
  .rm-section { padding: 40px 20px 0; }
  .rm-section:last-of-type { padding-bottom: 60px; }
  .rm-item-link { font-size: 1.05rem; }
}
</style>
