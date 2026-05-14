<template>
  <div class="wa-page">

    <div class="wa-topbar">
      <NuxtLink to="/pong-archive/writings" class="wa-back">← 返回著作列表</NuxtLink>
    </div>

    <div v-if="pending" class="wa-loading">載入中…</div>

    <template v-else-if="article">
      <header class="wa-header">
        <div class="wa-header-meta">
          <span class="wa-cat-badge">{{ categoryLabel }}</span>
          <span v-if="article.publication" class="wa-pub">{{ article.publication }}</span>
          <span v-if="article.published_date" class="wa-date">{{ formatDate(article.published_date, article.date_approximate) }}</span>
          <span v-if="article.page_range" class="wa-pages">頁次：{{ article.page_range }}</span>
        </div>
        <h1 class="wa-title">{{ article.title }}</h1>
        <p v-if="article.title_en" class="wa-title-en">{{ article.title_en }}</p>
        <p class="wa-byline">龐君華 會督</p>

        <div class="wa-header-actions">
          <a
            v-if="article.cloudinary_urls && article.cloudinary_urls.length"
            :href="article.cloudinary_urls[0]"
            target="_blank"
            rel="noopener"
            class="wa-dl-btn"
          >
            <svg viewBox="0 0 16 16" fill="none" aria-hidden="true">
              <rect x="2" y="1" width="12" height="14" rx="1.5" stroke="currentColor" stroke-width="1.2" fill="none"/>
              <line x1="4.5" y1="5.5" x2="11.5" y2="5.5" stroke="currentColor" stroke-width="1"/>
              <line x1="4.5" y1="8"   x2="11.5" y2="8"   stroke="currentColor" stroke-width="1"/>
              <line x1="4.5" y1="10.5" x2="9"   y2="10.5" stroke="currentColor" stroke-width="1"/>
            </svg>
            下載原始 PDF
          </a>
        </div>

        <div v-if="article.tags && article.tags.length" class="wa-tags">
          <span v-for="tag in article.tags" :key="tag" class="wa-tag">{{ tag }}</span>
        </div>
      </header>

      <div class="wa-rule" />

      <!-- ── Full Text ─────────────────────────────────── -->
      <article class="wa-body">
        <div class="wa-content">
          <p
            v-for="(para, i) in paragraphs"
            :key="i"
            class="wa-para"
            :class="{ 'wa-para--heading': isHeading(para), 'wa-para--quote': isQuote(para), 'wa-para--empty': !para.trim() }"
          >{{ displayText(para) }}</p>
        </div>

        <!-- ── Colophon (版權頁) ─────────────────────────── -->
        <section v-if="article.colophon && article.colophon.lines && article.colophon.lines.length" class="wa-colophon">
          <h2 class="wa-colophon-title">出版資訊</h2>
          <dl class="wa-colophon-list">
            <div v-for="(line, i) in article.colophon.lines" :key="i" class="wa-colophon-row">
              <dt class="wa-colophon-label">{{ line.label }}</dt>
              <dd class="wa-colophon-value">{{ line.value }}</dd>
            </div>
          </dl>
        </section>
      </article>
    </template>

    <div v-else class="wa-loading">找不到此篇文章。</div>

  </div>
</template>

<script setup>
definePageMeta({ layout: 'pong-archive' })

const route = useRoute()

const CATEGORIES = {
  thesis:       '學位論文',
  book_chapter: '專書文章',
  journal:      '期刊文章',
  conference:   '會議文章',
  web:          '網站文章',
  periodical:   '刊物文章',
}

const article = ref(null)
const pending = ref(true)

onMounted(async () => {
  try {
    article.value = await $fetch(`/api/pong-writing/${route.params.id}`)
  } catch (e) {
    console.error(e)
  } finally {
    pending.value = false
  }
})

const categoryLabel = computed(() => CATEGORIES[article.value?.category] || article.value?.category || '')

const paragraphs = computed(() => {
  const text = article.value?.content || ''
  return text.split('\n').map(l => l.trimEnd())
})

function isHeading(para) {
  const t = para.trim()
  if (!t) return false
  return t.length <= 20 && !/[，。！？、；：]$/.test(t) && /[一-鿿]/.test(t)
}

function isQuote(para) {
  return para.trimStart().startsWith('> ')
}

function displayText(para) {
  return isQuote(para) ? para.trimStart().slice(2) : para
}

function formatDate(dateStr, approximate) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return approximate ? `${d.getFullYear()} 年` : `${d.getFullYear()} 年 ${d.getMonth() + 1} 月`
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500&family=Noto+Serif+TC:wght@400;500;600&display=swap');

.wa-page {
  background-color: #F9F8F6;
  min-height: 100vh;
  font-family: 'Noto Sans TC', sans-serif;
  color: #2C2C2C;
}

/* ── Topbar ──────────────────────────────────────────────── */
.wa-topbar {
  padding: 20px 48px;
  border-bottom: 1px solid #DDD8CF;
}
.wa-back {
  font-size: 0.8rem;
  color: #8A8278;
  text-decoration: none;
  letter-spacing: 0.06em;
  transition: color 0.2s;
}
.wa-back:hover { color: #3A3025; }

.wa-loading {
  text-align: center;
  color: #A09280;
  font-size: 0.9rem;
  padding: 100px 40px;
  letter-spacing: 0.06em;
}

/* ── Header ──────────────────────────────────────────────── */
.wa-header {
  max-width: 760px;
  margin: 0 auto;
  padding: 56px 40px 40px;
}

.wa-header-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
}
.wa-cat-badge {
  font-size: 0.65rem;
  font-weight: 500;
  color: #FFF;
  background-color: #9A8060;
  padding: 3px 10px;
  border-radius: 2px;
  letter-spacing: 0.1em;
}
.wa-pub {
  font-size: 0.72rem;
  font-weight: 300;
  color: #8A8278;
  letter-spacing: 0.08em;
  background: #EEE8DC;
  padding: 3px 10px;
  border-radius: 2px;
}
.wa-date {
  font-size: 0.72rem;
  font-weight: 300;
  color: #A09280;
  letter-spacing: 0.06em;
}
.wa-pages {
  font-size: 0.72rem;
  font-weight: 300;
  color: #8A8278;
  letter-spacing: 0.06em;
}
/* ── Colophon (版權頁) ───────────────────────────────────── */
.wa-colophon {
  margin-top: 64px;
  padding: 28px 32px;
  border: 1px solid #DDD8CF;
  background-color: #F5F1E8;
  border-radius: 3px;
  font-family: 'Noto Sans TC', sans-serif;
}
.wa-colophon-title {
  font-family: 'Noto Serif TC', serif;
  font-size: 0.9rem;
  font-weight: 500;
  color: #6A5E4A;
  letter-spacing: 0.22em;
  margin: 0 0 18px;
  padding-bottom: 10px;
  border-bottom: 1px solid #DDD8CF;
  text-align: center;
}
.wa-colophon-list {
  margin: 0;
  display: grid;
  grid-template-columns: max-content 1fr;
  column-gap: 18px;
  row-gap: 6px;
  font-size: 0.82rem;
  line-height: 1.7;
}
.wa-colophon-row {
  display: contents;
}
.wa-colophon-label {
  color: #8A8278;
  font-weight: 400;
  letter-spacing: 0.1em;
  text-align: right;
  white-space: nowrap;
}
.wa-colophon-label::after {
  content: '｜';
  margin-left: 6px;
  color: #C4B89A;
}
.wa-colophon-value {
  color: #3A3025;
  margin: 0;
  letter-spacing: 0.04em;
}

.wa-title {
  font-family: 'Noto Serif TC', serif;
  font-size: clamp(1.5rem, 3vw, 2rem);
  font-weight: 500;
  color: #2C2C2C;
  letter-spacing: 0.08em;
  line-height: 1.6;
  margin: 0 0 12px;
}
.wa-title-en {
  font-size: 0.9rem;
  font-weight: 300;
  color: #8A8278;
  font-style: italic;
  letter-spacing: 0.04em;
  line-height: 1.6;
  margin: 0 0 24px;
}
.wa-byline {
  font-family: 'Noto Serif TC', serif;
  font-size: 0.95rem;
  font-weight: 400;
  color: #6A5E4A;
  letter-spacing: 0.18em;
  margin: 0 0 24px;
}

.wa-header-actions {
  margin-bottom: 20px;
}
.wa-dl-btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 9px 18px;
  background-color: #F2EFE9;
  border: 1px solid #DDD8CF;
  border-radius: 3px;
  font-size: 0.78rem;
  font-weight: 500;
  color: #6A6050;
  letter-spacing: 0.07em;
  text-decoration: none;
  transition: background-color 0.18s, border-color 0.18s, color 0.18s;
}
.wa-dl-btn:hover { background-color: #EAE4D8; border-color: #C4B89A; color: #3A3025; }
.wa-dl-btn svg { width: 14px; height: 14px; flex-shrink: 0; color: #9A8060; }

.wa-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.wa-tag {
  font-size: 0.62rem;
  color: #9A9080;
  background: #F0EDE8;
  border: 1px solid #E0DBD4;
  border-radius: 2px;
  padding: 2px 8px;
  letter-spacing: 0.05em;
}

/* ── Rule ────────────────────────────────────────────────── */
.wa-rule {
  max-width: 760px;
  margin: 0 auto;
  border: none;
  border-top: 1px solid #E0DAD2;
  margin-left: 40px;
  margin-right: 40px;
}

/* ── Body / Content ──────────────────────────────────────── */
.wa-body {
  max-width: 760px;
  margin: 0 auto;
  padding: 40px 40px 100px;
}

.wa-content {
  font-family: 'Noto Serif TC', 'SimSun', serif;
}

.wa-para {
  font-size: 1rem;
  line-height: 2.1;
  letter-spacing: 0.06em;
  color: #2C2C2C;
  margin: 0 0 0.4em;
  text-align: justify;
  text-indent: 2em;
}

.wa-para--heading {
  font-family: 'Noto Serif TC', serif;
  font-size: 1.05rem;
  font-weight: 600;
  color: #3A3025;
  margin-top: 1.8em;
  margin-bottom: 0.4em;
  letter-spacing: 0.1em;
  text-indent: 0;
}

.wa-para--quote {
  font-family: 'Noto Serif TC', 'DFKai-SB', 'BiauKai', serif;
  font-style: italic;
  margin-left: 2em;
  margin-right: 1em;
  padding-left: 1em;
  border-left: 3px solid #C4B89A;
  color: #5A5040;
  text-indent: 0;
}

.wa-para--empty {
  height: 0.6em;
  margin: 0;
}

/* ── Responsive ───────────────────────────────────────────── */
@media (max-width: 640px) {
  .wa-topbar { padding: 16px 20px; }
  .wa-header { padding: 36px 20px 28px; }
  .wa-rule   { margin-left: 20px; margin-right: 20px; }
  .wa-body   { padding: 28px 20px 60px; }
  .wa-title  { font-size: 1.4rem; }
  .wa-colophon { padding: 22px 18px; margin-top: 48px; }
  .wa-colophon-list { column-gap: 12px; font-size: 0.78rem; }
}
</style>
