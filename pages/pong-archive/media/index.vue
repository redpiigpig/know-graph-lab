<template>
  <div class="mi-page">

    <div class="mi-topbar">
      <NuxtLink to="/pong-archive" class="mi-back">← 返回典藏首頁</NuxtLink>
    </div>

    <header class="mi-header">
      <p class="mi-eyebrow">Interviews &amp; Talks</p>
      <h1 class="mi-title">訪談與演講</h1>
      <p class="mi-subtitle">龐君華會督歷年接受訪談、廣播節目及公開演講的影音紀錄</p>
    </header>

    <!-- ── 影音訪談 ─────────────────────────────────────────── -->
    <section class="mi-section">
      <h2 class="mi-section-heading">
        <span class="mi-section-zh">影音訪談</span>
        <span class="mi-section-en">Interviews</span>
      </h2>

      <div v-if="interviews.length" class="mi-list">
        <NuxtLink
          v-for="item in interviews"
          :key="item.id"
          :to="`/pong-archive/media/${item.id}`"
          class="mi-card"
        >
          <div class="mi-thumb">
            <img
              v-if="item.youtube_id"
              :src="`https://img.youtube.com/vi/${item.youtube_id}/mqdefault.jpg`"
              :alt="item.title"
              loading="lazy"
            />
            <div v-else class="mi-thumb-placeholder">
              <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="6" y="12" width="36" height="26" rx="3" stroke="currentColor" stroke-width="2" fill="none"/>
                <polygon points="20,19 20,31 33,25" fill="currentColor" opacity="0.5"/>
              </svg>
            </div>
            <div class="mi-play-badge">▶</div>
          </div>

          <div class="mi-card-body">
            <div class="mi-card-meta">
              <span v-if="item.source" class="mi-source">{{ item.source }}</span>
              <span v-if="item.broadcast_date" class="mi-date">{{ formatDate(item.broadcast_date) }}</span>
            </div>
            <h3 class="mi-card-title">{{ item.title }}</h3>
            <p v-if="item.description" class="mi-card-desc">{{ item.description }}</p>
            <div v-if="item.interviewer" class="mi-card-interviewer">
              主持：{{ item.interviewer }}
            </div>
          </div>

          <span class="mi-card-arrow">→</span>
        </NuxtLink>
      </div>

      <div v-else class="mi-empty">
        <p>尚無影音訪談資料。</p>
      </div>
    </section>

    <!-- ── 演講 ───────────────────────────────────────────────── -->
    <section class="mi-section">
      <h2 class="mi-section-heading">
        <span class="mi-section-zh">演講</span>
        <span class="mi-section-en">Talks &amp; Lectures</span>
      </h2>

      <div v-if="talks.length" class="mi-list">
        <NuxtLink
          v-for="item in talks"
          :key="item.id"
          :to="`/pong-archive/media/${item.id}`"
          class="mi-card"
        >
          <div class="mi-thumb">
            <img
              v-if="item.youtube_id || item.thumbnail_url"
              :src="item.thumbnail_url || `https://img.youtube.com/vi/${item.youtube_id}/mqdefault.jpg`"
              :alt="item.title"
              loading="lazy"
            />
            <div v-else class="mi-thumb-placeholder">
              <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="6" y="12" width="36" height="26" rx="3" stroke="currentColor" stroke-width="2" fill="none"/>
                <polygon points="20,19 20,31 33,25" fill="currentColor" opacity="0.5"/>
              </svg>
            </div>
            <div v-if="item.youtube_id" class="mi-play-badge">▶</div>
          </div>

          <div class="mi-card-body">
            <div class="mi-card-meta">
              <span v-if="item.source" class="mi-source">{{ item.source }}</span>
              <span v-if="item.broadcast_date" class="mi-date">{{ formatDate(item.broadcast_date) }}</span>
            </div>
            <h3 class="mi-card-title">{{ item.title }}</h3>
            <p v-if="item.description" class="mi-card-desc">{{ item.description }}</p>
          </div>

          <span class="mi-card-arrow">→</span>
        </NuxtLink>
      </div>

      <div v-else class="mi-empty">
        <p>尚無演講資料。</p>
      </div>
    </section>

    <!-- ── 短影音 ──────────────────────────────────────────────── -->
    <section class="mi-section">
      <h2 class="mi-section-heading">
        <span class="mi-section-zh">短影音</span>
        <span class="mi-section-en">Short Clips</span>
      </h2>

      <div v-if="shorts.length" class="mi-shorts-grid">
        <NuxtLink
          v-for="item in shorts"
          :key="item.id"
          :to="`/pong-archive/media/${item.id}`"
          class="mi-short-card"
        >
          <div
            class="mi-short-thumb"
            :style="(item.thumbnail_url || item.youtube_id)
              ? { '--thumb-src': `url('${item.thumbnail_url || `https://img.youtube.com/vi/${item.youtube_id}/mqdefault.jpg`}')` }
              : {}"
          >
            <img
              v-if="item.thumbnail_url || item.youtube_id"
              :src="item.thumbnail_url || `https://img.youtube.com/vi/${item.youtube_id}/mqdefault.jpg`"
              :alt="item.title"
              loading="lazy"
            />
            <div v-else class="mi-thumb-placeholder">
              <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="6" y="12" width="36" height="26" rx="3" stroke="currentColor" stroke-width="2" fill="none"/>
                <polygon points="20,19 20,31 33,25" fill="currentColor" opacity="0.5"/>
              </svg>
            </div>
            <div class="mi-play-badge">▶</div>
          </div>
          <div class="mi-short-body">
            <span v-if="item.broadcast_date" class="mi-date">{{ formatDate(item.broadcast_date) }}</span>
            <h3 class="mi-short-title">{{ item.title }}</h3>
            <p v-if="item.description" class="mi-card-desc">{{ item.description }}</p>
          </div>
        </NuxtLink>
      </div>

      <div v-else class="mi-empty">
        <p>尚無短影音資料。</p>
      </div>
    </section>

  </div>
</template>

<script setup>
import { createClient } from '@supabase/supabase-js'

definePageMeta({ layout: 'pong-archive' })

const config = useRuntimeConfig()
const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_KEY
)

const { data: items } = await useAsyncData('pong-media-list', async () => {
  const { data, error } = await supabase
    .from('pong_media')
    .select('id, title, title_en, source, program_name, interviewer, media_type, platform, youtube_id, broadcast_date, description, thumbnail_url, tags')
    .eq('is_published', true)
    .order('broadcast_date', { ascending: false })
  if (error) { console.error(error); return [] }
  return data || []
})

const interviews = computed(() =>
  (items.value || []).filter(i => i.media_type === 'interview')
)
const talks = computed(() =>
  (items.value || []).filter(i => i.media_type === 'talk')
)
const shorts = computed(() =>
  (items.value || []).filter(i => i.media_type === 'short')
)

function formatDate(d) {
  if (!d) return ''
  const dt = new Date(d)
  return `${dt.getFullYear()} 年 ${dt.getMonth() + 1} 月 ${dt.getDate()} 日`
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500&family=Noto+Serif+TC:wght@400;500;600&display=swap');

.mi-page {
  background-color: #F9F8F6;
  min-height: 100vh;
  font-family: 'Noto Sans TC', sans-serif;
  color: #2C2C2C;
}

/* ── Topbar ─────────────────────────────────────────────── */
.mi-topbar {
  padding: 20px 48px;
  border-bottom: 1px solid #DDD8CF;
}
.mi-back {
  font-size: 0.8rem;
  color: #8A8278;
  text-decoration: none;
  letter-spacing: 0.06em;
  transition: color 0.2s;
}
.mi-back:hover { color: #3A3025; }

/* ── Header ─────────────────────────────────────────────── */
.mi-header {
  text-align: center;
  padding: 56px 40px 40px;
  border-bottom: 1px solid #E8E4DC;
}
.mi-eyebrow {
  font-size: 0.72rem;
  font-weight: 300;
  color: #A09280;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  margin: 0 0 10px;
}
.mi-title {
  font-family: 'Noto Serif TC', serif;
  font-size: 2rem;
  font-weight: 500;
  color: #2C2C2C;
  letter-spacing: 0.12em;
  margin: 0 0 10px;
}
.mi-subtitle {
  font-size: 0.85rem;
  font-weight: 300;
  color: #7A7268;
  letter-spacing: 0.06em;
  margin: 0;
}

/* ── Section ────────────────────────────────────────────── */
.mi-section {
  max-width: 860px;
  margin: 0 auto;
  padding: 48px 40px;
  border-bottom: 1px solid #EAE6DE;
}
.mi-section:last-child { border-bottom: none; }

.mi-section-heading {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin: 0 0 32px;
  padding-bottom: 14px;
  border-bottom: 2px solid #C4B89A;
}
.mi-section-zh {
  font-family: 'Noto Serif TC', serif;
  font-size: 1.2rem;
  font-weight: 500;
  color: #3A3025;
  letter-spacing: 0.1em;
}
.mi-section-en {
  font-size: 0.72rem;
  font-weight: 300;
  color: #A09280;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

/* ── Card List ──────────────────────────────────────────── */
.mi-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.mi-card {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  padding: 20px;
  background-color: #F2EFE9;
  border: 1px solid #DDD8CF;
  border-radius: 4px;
  text-decoration: none;
  color: inherit;
  transition: border-color 0.2s, box-shadow 0.2s, transform 0.2s;
}
.mi-card:hover {
  border-color: #C4B89A;
  box-shadow: 0 4px 16px rgba(60,50,40,0.08);
  transform: translateY(-2px);
}

/* ── Thumbnail ──────────────────────────────────────────── */
.mi-thumb {
  position: relative;
  flex-shrink: 0;
  width: 160px;
  height: 90px;
  border-radius: 3px;
  overflow: hidden;
  background-color: #E0DBD1;
}
.mi-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.mi-thumb-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #A09280;
}
.mi-thumb-placeholder svg {
  width: 40px;
  height: 40px;
}
.mi-play-badge {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(40,30,20,0.28);
  color: #fff;
  font-size: 1.1rem;
  opacity: 0;
  transition: opacity 0.2s;
}
.mi-card:hover .mi-play-badge { opacity: 1; }

/* ── Card Body ──────────────────────────────────────────── */
.mi-card-body {
  flex: 1;
  min-width: 0;
}
.mi-card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}
.mi-source, .mi-program {
  font-size: 0.7rem;
  font-weight: 300;
  color: #fff;
  background-color: #8A7E6E;
  padding: 2px 8px;
  border-radius: 2px;
  letter-spacing: 0.06em;
}
.mi-program { background-color: #A09280; }
.mi-date {
  font-size: 0.72rem;
  color: #9A9080;
  letter-spacing: 0.04em;
  align-self: center;
}
.mi-card-title {
  font-family: 'Noto Serif TC', serif;
  font-size: 1.05rem;
  font-weight: 500;
  color: #3A3025;
  letter-spacing: 0.06em;
  margin: 0 0 8px;
  line-height: 1.5;
}
.mi-card-desc {
  font-size: 0.82rem;
  font-weight: 300;
  color: #6A6460;
  line-height: 1.8;
  letter-spacing: 0.04em;
  margin: 0 0 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.mi-card-interviewer {
  font-size: 0.75rem;
  color: #9A9080;
  letter-spacing: 0.04em;
}

.mi-card-arrow {
  align-self: center;
  flex-shrink: 0;
  font-size: 1rem;
  color: #B0A690;
  transition: color 0.2s, transform 0.2s;
}
.mi-card:hover .mi-card-arrow {
  color: #7A6E5E;
  transform: translateX(4px);
}

/* ── Empty ──────────────────────────────────────────────── */
.mi-empty {
  padding: 40px 0;
  text-align: center;
  font-size: 0.85rem;
  color: #A09280;
  letter-spacing: 0.06em;
}

/* ── Shorts Grid ─────────────────────────────────────────── */
.mi-shorts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
}

.mi-short-card {
  display: flex;
  flex-direction: column;
  background-color: #F2EFE9;
  border: 1px solid #DDD8CF;
  border-radius: 4px;
  text-decoration: none;
  color: inherit;
  overflow: hidden;
  transition: border-color 0.2s, box-shadow 0.2s, transform 0.2s;
}
.mi-short-card:hover {
  border-color: #C4B89A;
  box-shadow: 0 4px 16px rgba(60,50,40,0.08);
  transform: translateY(-2px);
}

.mi-short-thumb {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  background-color: #1a1410;
  overflow: hidden;
}
.mi-short-thumb::before {
  content: '';
  position: absolute;
  inset: -8%;
  background-image: var(--thumb-src);
  background-size: cover;
  background-position: center;
  filter: blur(18px) brightness(0.45);
}
.mi-short-thumb img {
  position: relative;
  z-index: 1;
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.mi-short-body {
  padding: 12px 14px 14px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.mi-short-title {
  font-family: 'Noto Serif TC', serif;
  font-size: 0.88rem;
  font-weight: 500;
  color: #3A3025;
  letter-spacing: 0.05em;
  margin: 0;
  line-height: 1.5;
}

/* ── Responsive ─────────────────────────────────────────── */
@media (max-width: 640px) {
  .mi-topbar, .mi-section { padding: 16px 20px; }
  .mi-header { padding: 40px 20px 28px; }
  .mi-thumb { width: 100px; height: 56px; }
  .mi-card { gap: 14px; }
  .mi-shorts-grid { grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); }
}
</style>
