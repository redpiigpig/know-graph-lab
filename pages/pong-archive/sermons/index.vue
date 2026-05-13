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

    <nav class="sl-tabs">
      <button
        v-for="t in tabs"
        :key="t.key"
        class="sl-tab"
        :class="{ 'sl-tab--active': activeTab === t.key }"
        @click="activeTab = t.key"
      >{{ t.label }}</button>
    </nav>

    <!-- Year tab -->
    <section v-if="activeTab === 'year'" class="sl-grid-section">
      <div class="sl-years-grid">
        <NuxtLink
          v-for="y in years"
          :key="y.year"
          :to="`/pong-archive/sermons/year/${y.year}`"
          class="sl-year-card"
          :class="{ 'sl-year-card--empty': !yearCounts[y.year] }"
        >
          <span class="sl-year-label">{{ y.year }}–{{ y.year + 1 }}</span>
          <span v-if="yearCounts[y.year]" class="sl-year-count">{{ yearCounts[y.year] }} 篇</span>
        </NuxtLink>
      </div>
    </section>

    <!-- Location tab -->
    <section v-if="activeTab === 'location'" class="sl-grid-section">
      <div class="sl-cards-grid">
        <NuxtLink
          v-for="loc in locationGroups"
          :key="loc.name"
          :to="`/pong-archive/sermons/by/location/${encodeURIComponent(loc.name)}`"
          class="sl-card"
        >
          <span class="sl-card-label">{{ loc.name }}</span>
          <span class="sl-card-count">{{ loc.count }} 篇</span>
        </NuxtLink>
      </div>
    </section>

    <!-- Type tab -->
    <section v-if="activeTab === 'type'" class="sl-grid-section">
      <div class="sl-cards-grid">
        <NuxtLink
          v-for="t in typeGroups"
          :key="t.name"
          :to="`/pong-archive/sermons/by/type/${encodeURIComponent(t.name)}`"
          class="sl-card"
        >
          <span class="sl-card-label">{{ t.name }}</span>
          <span class="sl-card-count">{{ t.count }} 篇</span>
        </NuxtLink>
      </div>
    </section>
  </div>
</template>

<script setup>
import { createClient } from '@supabase/supabase-js'
import { ref, computed } from 'vue'
import { locationCategory, SERMON_TYPE_ORDER } from '~/composables/usePongSermonTaxonomy'

definePageMeta({ layout: 'pong-archive' })

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_KEY,
)

const tabs = [
  { key: 'year',     label: '年份' },
  { key: 'location', label: '地點' },
  { key: 'type',     label: '類型' },
]
const activeTab = ref('year')

const years = Array.from({ length: 26 }, (_, i) => ({ year: 2000 + i }))

const { data: rows } = await useAsyncData('pong-sermon-counts', async () => {
  const { data, error } = await supabase
    .from('pong_sermons')
    .select('church_year, location, sermon_type')
    .eq('is_published', true)
  if (error) return []
  return data || []
})

const yearCounts = computed(() => {
  const m = {}
  for (const r of (rows.value || [])) m[r.church_year] = (m[r.church_year] || 0) + 1
  return m
})

const locationGroups = computed(() => {
  const m = {}
  for (const r of (rows.value || [])) {
    const cat = locationCategory(r.location)
    m[cat] = (m[cat] || 0) + 1
  }
  return Object.entries(m)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
})

const typeGroups = computed(() => {
  const m = {}
  for (const r of (rows.value || [])) {
    const t = r.sermon_type || '主日講道'
    m[t] = (m[t] || 0) + 1
  }
  return SERMON_TYPE_ORDER
    .filter(name => m[name])
    .map(name => ({ name, count: m[name] }))
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
.sl-back { font-size: 0.8rem; color: #8A8278; text-decoration: none; letter-spacing: 0.06em; transition: color 0.2s; }
.sl-back:hover { color: #3A3025; }

.sl-header {
  text-align: center;
  padding: 56px 40px 32px;
}
.sl-eyebrow { font-size: 0.72rem; font-weight: 300; color: #A09280; letter-spacing: 0.22em; text-transform: uppercase; margin: 0 0 10px; }
.sl-title { font-family: 'Noto Serif TC', serif; font-size: 2rem; font-weight: 500; color: #2C2C2C; letter-spacing: 0.12em; margin: 0 0 10px; }
.sl-subtitle { font-size: 0.85rem; font-weight: 300; color: #7A7268; letter-spacing: 0.06em; margin: 0; }

.sl-tabs {
  display: flex;
  justify-content: center;
  gap: 4px;
  padding: 0 24px 28px;
  border-bottom: 1px solid #E8E4DC;
}
.sl-tab {
  background: transparent;
  border: none;
  padding: 8px 22px 10px;
  font-family: 'Noto Sans TC', sans-serif;
  font-size: 0.85rem;
  font-weight: 400;
  color: #8A8278;
  letter-spacing: 0.12em;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: color 0.15s, border-color 0.15s;
}
.sl-tab:hover { color: #3A3025; }
.sl-tab--active { color: #3A3025; border-bottom-color: #C4B89A; }

.sl-grid-section { max-width: 900px; margin: 0 auto; padding: 36px 24px 64px; }

.sl-years-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 8px; }
.sl-year-card { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 12px 6px; background-color: #F2EFE9; border: 1px solid #DDD8CF; border-radius: 3px; text-decoration: none; color: inherit; transition: background-color 0.2s, border-color 0.2s; gap: 4px; }
.sl-year-card:hover { background-color: #EAE4D8; border-color: #C4B89A; }
.sl-year-card--empty { opacity: 0.45; }
.sl-year-label { font-family: 'Noto Serif TC', serif; font-size: 0.78rem; font-weight: 500; color: #5A5048; letter-spacing: 0.03em; white-space: nowrap; }
.sl-year-count { font-size: 0.65rem; font-weight: 300; color: #9A9080; letter-spacing: 0.06em; }

.sl-cards-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
.sl-card {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 20px;
  background-color: #F2EFE9; border: 1px solid #DDD8CF; border-radius: 4px;
  text-decoration: none; color: inherit;
  transition: background-color 0.2s, border-color 0.2s;
}
.sl-card:hover { background-color: #EAE4D8; border-color: #C4B89A; }
.sl-card-label { font-family: 'Noto Serif TC', serif; font-size: 0.92rem; font-weight: 500; color: #3A3025; letter-spacing: 0.04em; }
.sl-card-count { font-size: 0.7rem; font-weight: 300; color: #9A9080; letter-spacing: 0.06em; }

@media (max-width: 640px) {
  .sl-topbar { padding: 16px 20px; }
  .sl-header { padding: 40px 20px 24px; }
  .sl-tabs { padding: 0 16px 20px; gap: 0; }
  .sl-tab { padding: 8px 14px 10px; font-size: 0.8rem; letter-spacing: 0.08em; }
  .sl-grid-section { padding: 28px 16px 56px; }
  .sl-years-grid { grid-template-columns: repeat(3, 1fr); }
  .sl-year-label { font-size: 0.7rem; }
  .sl-cards-grid { grid-template-columns: 1fr; }
}
</style>
