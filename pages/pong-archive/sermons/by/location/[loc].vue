<template>
  <div class="bl-page">
    <div class="bl-topbar">
      <NuxtLink to="/pong-archive/sermons/by/location" class="bl-back">← 按地點瀏覽</NuxtLink>
    </div>

    <header class="bl-header">
      <p class="bl-eyebrow">By Location</p>
      <h1 class="bl-title">{{ category }}</h1>
      <p class="bl-meta">{{ sermons.length }} 篇</p>
    </header>

    <section class="bl-body">
      <div v-if="!sermons.length" class="bl-empty">此地點目前沒有講道記錄。</div>
      <ol v-else class="bl-list">
        <li v-for="s in sermons" :key="s.id" class="bl-item">
          <span class="bl-date">{{ s.sermon_date }}</span>
          <div class="bl-content">
            <NuxtLink :to="`/pong-archive/sermons/${s.sermon_date}`" class="bl-link">{{ s.title || '(未命名)' }}</NuxtLink>
            <div class="bl-sub">
              <span v-if="s.occasion" class="bl-occasion">{{ s.occasion }}</span>
              <span v-if="s.location" class="bl-loc">{{ s.location }}</span>
            </div>
          </div>
        </li>
      </ol>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { createClient } from '@supabase/supabase-js'
import { locationCategory } from '~/composables/usePongSermonTaxonomy'

definePageMeta({ layout: 'pong-archive' })

const route = useRoute()
const category = computed(() => decodeURIComponent(route.params.loc))

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_KEY,
)

const { data: allRows } = await useAsyncData(
  () => `pong-sermons-by-loc-${category.value}`,
  async () => {
    const { data, error } = await supabase
      .from('pong_sermons')
      .select('id, sermon_date, title, occasion, location')
      .eq('is_published', true)
      .order('sermon_date', { ascending: false })
    if (error) return []
    return data || []
  },
)

const sermons = computed(() => (allRows.value || []).filter(r => locationCategory(r.location) === category.value))
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500&family=Noto+Serif+TC:wght@400;500;600&display=swap');

.bl-page { background: #F9F8F6; min-height: 100vh; font-family: 'Noto Sans TC', sans-serif; color: #2C2C2C; }
.bl-topbar { padding: 20px 48px; border-bottom: 1px solid #DDD8CF; }
.bl-back { font-size: 0.8rem; color: #8A8278; text-decoration: none; letter-spacing: 0.06em; transition: color 0.2s; }
.bl-back:hover { color: #3A3025; }

.bl-header { text-align: center; padding: 48px 40px 32px; border-bottom: 1px solid #E8E4DC; }
.bl-eyebrow { font-size: 0.7rem; font-weight: 300; color: #A09280; letter-spacing: 0.22em; text-transform: uppercase; margin: 0 0 10px; }
.bl-title { font-family: 'Noto Serif TC', serif; font-size: 1.6rem; font-weight: 500; color: #2C2C2C; letter-spacing: 0.1em; margin: 0 0 8px; }
.bl-meta { font-size: 0.78rem; font-weight: 300; color: #7A7268; letter-spacing: 0.06em; margin: 0; }

.bl-body { max-width: 760px; margin: 0 auto; padding: 32px 24px 64px; }
.bl-empty { text-align: center; color: #B0A890; font-size: 0.85rem; padding: 48px 0; }

.bl-list { list-style: none; padding: 0; margin: 0; }
.bl-item {
  display: grid;
  grid-template-columns: 100px 1fr;
  gap: 16px;
  padding: 14px 0;
  border-bottom: 1px solid #ECE7DD;
  align-items: baseline;
}
.bl-item:last-child { border-bottom: none; }

.bl-date {
  font-family: 'Noto Serif TC', serif;
  font-size: 0.78rem;
  color: #9A9080;
  letter-spacing: 0.04em;
  white-space: nowrap;
}
.bl-content { min-width: 0; }
.bl-link {
  font-family: 'Noto Serif TC', serif;
  font-size: 0.95rem;
  font-weight: 500;
  color: #3A3025;
  letter-spacing: 0.03em;
  text-decoration: none;
  transition: color 0.2s;
}
.bl-link:hover { color: #8A6E40; }
.bl-sub { margin-top: 4px; display: flex; gap: 14px; flex-wrap: wrap; }
.bl-occasion { font-size: 0.7rem; color: #A09280; letter-spacing: 0.04em; }
.bl-loc { font-size: 0.7rem; color: #B0A890; letter-spacing: 0.04em; }

@media (max-width: 640px) {
  .bl-topbar { padding: 16px 20px; }
  .bl-header { padding: 36px 20px 24px; }
  .bl-body { padding: 24px 16px 56px; }
  .bl-item { grid-template-columns: 80px 1fr; gap: 12px; }
  .bl-date { font-size: 0.72rem; }
  .bl-link { font-size: 0.88rem; }
}
</style>
