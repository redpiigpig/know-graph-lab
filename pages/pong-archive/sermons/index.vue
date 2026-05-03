<template>
  <div class="sl-page">
    <div class="sl-topbar">
      <NuxtLink to="/pong-archive" class="sl-back">← 返回典藏首頁</NuxtLink>
    </div>

    <header class="sl-header">
      <p class="sl-eyebrow">Sermons</p>
      <h1 class="sl-title">講道集</h1>
      <p class="sl-subtitle">龐君華會督歷年主日講道及特別信息</p>
    </header>

    <section class="sl-years-section">
      <div class="sl-years-grid">
        <NuxtLink
          v-for="y in years"
          :key="y.year"
          :to="`/pong-archive/sermons/year/${y.year}`"
          class="sl-year-card"
          :class="{ 'sl-year-card--empty': !countMap[y.year] }"
        >
          <span class="sl-year-label">{{ y.year }}–{{ y.year + 1 }}</span>
          <span v-if="countMap[y.year]" class="sl-year-count">{{ countMap[y.year] }} 篇</span>
        </NuxtLink>
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

const years = Array.from({ length: 26 }, (_, i) => ({ year: 2000 + i }))

const { data: counts } = await useAsyncData('pong-sermon-counts', async () => {
  const { data, error } = await supabase
    .from('pong_sermons')
    .select('church_year')
    .eq('is_published', true)
  if (error) return []
  return data || []
})

const countMap = computed(() => {
  const map = {}
  for (const row of (counts.value || [])) {
    map[row.church_year] = (map[row.church_year] || 0) + 1
  }
  return map
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500&family=Noto+Serif+TC:wght@400;500;600&display=swap');

.sl-page {
  background-color: #F9F8F6;
  min-height: 100vh;
  font-family: 'Noto Sans TC', sans-serif;
  color: #2C2C2C;
}

.sl-topbar {
  padding: 20px 48px;
  border-bottom: 1px solid #DDD8CF;
}
.sl-back {
  font-size: 0.8rem;
  color: #8A8278;
  text-decoration: none;
  letter-spacing: 0.06em;
  transition: color 0.2s;
}
.sl-back:hover { color: #3A3025; }

.sl-header {
  text-align: center;
  padding: 56px 40px 40px;
  border-bottom: 1px solid #E8E4DC;
}
.sl-eyebrow {
  font-size: 0.72rem;
  font-weight: 300;
  color: #A09280;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  margin: 0 0 10px;
}
.sl-title {
  font-family: 'Noto Serif TC', serif;
  font-size: 2rem;
  font-weight: 500;
  color: #2C2C2C;
  letter-spacing: 0.12em;
  margin: 0 0 10px;
}
.sl-subtitle {
  font-size: 0.85rem;
  font-weight: 300;
  color: #7A7268;
  letter-spacing: 0.06em;
  margin: 0;
}

.sl-years-section {
  max-width: 900px;
  margin: 0 auto;
  padding: 48px 24px 64px;
}
.sl-years-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 8px;
}
.sl-year-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 12px 6px;
  background-color: #F2EFE9;
  border: 1px solid #DDD8CF;
  border-radius: 3px;
  text-decoration: none;
  color: inherit;
  transition: background-color 0.2s, border-color 0.2s;
  gap: 4px;
}
.sl-year-card:hover {
  background-color: #EAE4D8;
  border-color: #C4B89A;
}
.sl-year-card--empty {
  opacity: 0.45;
}
.sl-year-label {
  font-family: 'Noto Serif TC', serif;
  font-size: 0.78rem;
  font-weight: 500;
  color: #5A5048;
  letter-spacing: 0.03em;
  white-space: nowrap;
}
.sl-year-count {
  font-size: 0.65rem;
  font-weight: 300;
  color: #9A9080;
  letter-spacing: 0.06em;
}

@media (max-width: 640px) {
  .sl-topbar { padding: 16px 20px; }
  .sl-years-section { padding-left: 16px; padding-right: 16px; }
  .sl-years-grid { grid-template-columns: repeat(3, 1fr); }
  .sl-year-label { font-size: 0.7rem; }
}
</style>
