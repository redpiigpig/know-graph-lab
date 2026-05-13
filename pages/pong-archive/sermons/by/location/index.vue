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

    <PongSermonTabs />

    <section class="sl-grid-section">
      <div class="sl-cards-grid">
        <NuxtLink
          v-for="loc in locationGroups"
          :key="loc.name"
          :to="`/pong-archive/sermons/by/location/${encodeURIComponent(loc.name)}`"
          class="sl-card"
          :class="{ 'sl-card--empty': !loc.count }"
        >
          <span class="sl-card-label">{{ loc.name }}</span>
          <span class="sl-card-count">{{ loc.count }} 篇</span>
        </NuxtLink>
      </div>
    </section>
  </div>
</template>

<script setup>
import { createClient } from '@supabase/supabase-js'
import { computed } from 'vue'
import { locationCategory, LOCATION_ORDER, ALWAYS_SHOW_LOCATIONS } from '~/composables/usePongSermonTaxonomy'

definePageMeta({ layout: 'pong-archive' })

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_KEY,
)

const { data: rows } = await useAsyncData('pong-sermon-location-counts', async () => {
  const { data, error } = await supabase
    .from('pong_sermons')
    .select('location')
    .eq('is_published', true)
  if (error) return []
  return data || []
})

const locationGroups = computed(() => {
  const m = {}
  for (const r of (rows.value || [])) {
    const cat = locationCategory(r.location)
    m[cat] = (m[cat] || 0) + 1
  }
  // Follow the fixed display order. The 4 衛理 internal locations show even
  // with 0 sermons; the rest appear only when they have data.
  const ordered = LOCATION_ORDER
    .filter(name => ALWAYS_SHOW_LOCATIONS.includes(name) || m[name])
    .map(name => ({ name, count: m[name] || 0 }))
  // Anything that doesn't match a known category (e.g. a future denomination
  // we haven't added a rule for yet) gets appended at the end.
  const knownSet = new Set(LOCATION_ORDER)
  const unknown = Object.entries(m)
    .filter(([name]) => !knownSet.has(name))
    .map(([name, count]) => ({ name, count }))
  return [...ordered, ...unknown]
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500&family=Noto+Serif+TC:wght@400;500;600&display=swap');

.sl-page { background-color: #F9F8F6; min-height: 100vh; font-family: 'Noto Sans TC', sans-serif; color: #2C2C2C; }
.sl-topbar { padding: 20px 48px; border-bottom: 1px solid #DDD8CF; }
.sl-back { font-size: 0.8rem; color: #8A8278; text-decoration: none; letter-spacing: 0.06em; transition: color 0.2s; }
.sl-back:hover { color: #3A3025; }

.sl-header { text-align: center; padding: 56px 40px 32px; }
.sl-eyebrow { font-size: 0.72rem; font-weight: 300; color: #A09280; letter-spacing: 0.22em; text-transform: uppercase; margin: 0 0 10px; }
.sl-title { font-family: 'Noto Serif TC', serif; font-size: 2rem; font-weight: 500; color: #2C2C2C; letter-spacing: 0.12em; margin: 0 0 10px; }
.sl-subtitle { font-size: 0.85rem; font-weight: 300; color: #7A7268; letter-spacing: 0.06em; margin: 0; }

.sl-grid-section { max-width: 900px; margin: 0 auto; padding: 36px 24px 64px; }

.sl-cards-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
.sl-card {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 20px;
  background-color: #F2EFE9; border: 1px solid #DDD8CF; border-radius: 4px;
  text-decoration: none; color: inherit;
  transition: background-color 0.2s, border-color 0.2s;
}
.sl-card:hover { background-color: #EAE4D8; border-color: #C4B89A; }
.sl-card--empty { opacity: 0.45; }
.sl-card-label { font-family: 'Noto Serif TC', serif; font-size: 0.92rem; font-weight: 500; color: #3A3025; letter-spacing: 0.04em; }
.sl-card-count { font-size: 0.7rem; font-weight: 300; color: #9A9080; letter-spacing: 0.06em; }

@media (max-width: 640px) {
  .sl-topbar { padding: 16px 20px; }
  .sl-header { padding: 40px 20px 24px; }
  .sl-grid-section { padding: 28px 16px 56px; }
  .sl-cards-grid { grid-template-columns: 1fr; }
}
</style>
