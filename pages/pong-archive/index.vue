<template>
  <div class="pa-page">

    <!-- ── Hero Section ──────────────────────────────────── -->
    <section class="pa-hero">
      <div class="pa-hero-inner">
        <h1 class="pa-hero-title">龐君華會督文集數位典藏</h1>
        <blockquote class="pa-hero-quote">
          <p class="pa-hero-quote-text">
            「我們所傳講的，不是我們自己，乃是基督耶穌為主；
            並且我們為耶穌的緣故，作你們的僕人。」
          </p>
          <cite class="pa-hero-quote-cite">哥林多後書 4:5</cite>
        </blockquote>
        <div class="pa-hero-rule" />
      </div>
    </section>

    <!-- ── Collection Grid ───────────────────────────────── -->
    <section class="pa-collections">
      <div class="pa-collections-inner">

        <!-- 1. 講道集 -->
        <NuxtLink to="/pong-archive/sermons" class="pa-card pa-card--sermons">
          <div class="pa-card-icon">
            <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
              <rect x="8" y="6" width="32" height="36" rx="3" stroke="currentColor" stroke-width="2" fill="none"/>
              <line x1="15" y1="16" x2="33" y2="16" stroke="currentColor" stroke-width="1.5"/>
              <line x1="15" y1="22" x2="33" y2="22" stroke="currentColor" stroke-width="1.5"/>
              <line x1="15" y1="28" x2="26" y2="28" stroke="currentColor" stroke-width="1.5"/>
              <circle cx="36" cy="34" r="8" fill="#F9F8F6" stroke="currentColor" stroke-width="1.5"/>
              <line x1="33" y1="34" x2="39" y2="34" stroke="currentColor" stroke-width="1.5"/>
              <line x1="36" y1="31" x2="36" y2="37" stroke="currentColor" stroke-width="1.5"/>
            </svg>
          </div>
          <div class="pa-card-body">
            <span class="pa-card-en">Sermons</span>
            <h2 class="pa-card-title">講道集</h2>
            <p class="pa-card-desc">
              收錄歷年主日講道、奮興會信息、退修會講章，依時序與主題分類整理。
            </p>
          </div>
          <span class="pa-card-arrow">→</span>
        </NuxtLink>

        <!-- 2. 著作與專文 -->
        <NuxtLink to="/pong-archive/writings" class="pa-card pa-card--writings">
          <div class="pa-card-icon">
            <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
              <path d="M12 42 C12 42, 10 36, 10 24 C10 12, 18 6, 24 6 C30 6, 38 12, 38 24 C38 36, 36 42, 36 42" stroke="currentColor" stroke-width="2" fill="none"/>
              <line x1="12" y1="42" x2="36" y2="42" stroke="currentColor" stroke-width="2"/>
              <line x1="14" y1="18" x2="34" y2="18" stroke="currentColor" stroke-width="1.5"/>
              <line x1="14" y1="25" x2="34" y2="25" stroke="currentColor" stroke-width="1.5"/>
              <line x1="14" y1="32" x2="28" y2="32" stroke="currentColor" stroke-width="1.5"/>
            </svg>
          </div>
          <div class="pa-card-body">
            <span class="pa-card-en">Writings</span>
            <h2 class="pa-card-title">著作與專文</h2>
            <p class="pa-card-desc">
              專書章節、神學論文、雜誌專欄及敬虔靈修文章，呈現其思想脈絡與神學關懷。
            </p>
          </div>
          <span class="pa-card-arrow">→</span>
        </NuxtLink>

        <!-- 3. 訪談與演講 -->
        <NuxtLink to="/pong-archive/media" class="pa-card pa-card--media">
          <div class="pa-card-icon">
            <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
              <rect x="6" y="12" width="36" height="26" rx="3" stroke="currentColor" stroke-width="2" fill="none"/>
              <polygon points="20,19 20,31 33,25" stroke="currentColor" stroke-width="1.5" fill="none"/>
              <line x1="6" y1="38" x2="14" y2="42" stroke="currentColor" stroke-width="1.5"/>
              <line x1="42" y1="38" x2="34" y2="42" stroke="currentColor" stroke-width="1.5"/>
            </svg>
          </div>
          <div class="pa-card-body">
            <span class="pa-card-en">Interviews &amp; Talks</span>
            <h2 class="pa-card-title">訪談與演講</h2>
            <p class="pa-card-desc">
              龐會督接受訪談的影音記錄、廣播節目、公開演講及相關媒體資料，聆聽其聲音與見證。
            </p>
          </div>
          <span class="pa-card-arrow">→</span>
        </NuxtLink>

        <!-- 4. 三讀三禱 -->
        <NuxtLink to="/pong-archive/daily-office" class="pa-card pa-card--daily-office">
          <div class="pa-card-icon">
            <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
              <circle cx="24" cy="24" r="16" stroke="currentColor" stroke-width="2" fill="none"/>
              <line x1="24" y1="10" x2="24" y2="24" stroke="currentColor" stroke-width="2"/>
              <line x1="24" y1="24" x2="32" y2="30" stroke="currentColor" stroke-width="1.5"/>
              <circle cx="24" cy="24" r="2" fill="currentColor"/>
              <line x1="24" y1="6" x2="24" y2="8" stroke="currentColor" stroke-width="2"/>
              <line x1="24" y1="40" x2="24" y2="42" stroke="currentColor" stroke-width="2"/>
              <line x1="6" y1="24" x2="8" y2="24" stroke="currentColor" stroke-width="2"/>
              <line x1="40" y1="24" x2="42" y2="24" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <div class="pa-card-body">
            <span class="pa-card-en">Daily Office</span>
            <h2 class="pa-card-title">三讀三禱</h2>
            <p class="pa-card-desc">
              龐會督按照日課表所寫的每日讀經靈修反省，以三段讀經配合三段禱文，記錄其與聖言同行的屬靈操練。
            </p>
          </div>
          <span class="pa-card-arrow">→</span>
        </NuxtLink>

        <!-- 5. 手稿與書信 -->
        <NuxtLink to="/pong-archive/manuscripts" class="pa-card pa-card--manuscripts">
          <div class="pa-card-icon">
            <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
              <rect x="10" y="8" width="28" height="34" rx="2" stroke="currentColor" stroke-width="2" fill="none" transform="rotate(-4 24 25)"/>
              <path d="M17 16 Q20 13 23 16 Q26 19 29 16" stroke="currentColor" stroke-width="1.5" fill="none"/>
              <path d="M16 23 Q19 20 22 23 Q25 26 28 23 Q31 20 34 23" stroke="currentColor" stroke-width="1.5" fill="none"/>
              <line x1="16" y1="31" x2="26" y2="31" stroke="currentColor" stroke-width="1.5"/>
            </svg>
          </div>
          <div class="pa-card-body">
            <span class="pa-card-en">Manuscripts</span>
            <h2 class="pa-card-title">手稿與書信</h2>
            <p class="pa-card-desc">
              親筆手稿、書信往來、批注筆記等原始文獻，保存其事奉生命中的私密記錄。
            </p>
          </div>
          <span class="pa-card-arrow">→</span>
        </NuxtLink>

        <!-- 6. 相關報導 -->
        <NuxtLink to="/pong-archive/reports" class="pa-card pa-card--reports">
          <div class="pa-card-icon">
            <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
              <rect x="6" y="8" width="36" height="32" rx="3" stroke="currentColor" stroke-width="2" fill="none"/>
              <rect x="12" y="14" width="10" height="10" rx="1" stroke="currentColor" stroke-width="1.5" fill="none"/>
              <line x1="26" y1="15" x2="36" y2="15" stroke="currentColor" stroke-width="1.5"/>
              <line x1="26" y1="20" x2="36" y2="20" stroke="currentColor" stroke-width="1.5"/>
              <line x1="12" y1="29" x2="36" y2="29" stroke="currentColor" stroke-width="1.5"/>
              <line x1="12" y1="34" x2="28" y2="34" stroke="currentColor" stroke-width="1.5"/>
            </svg>
          </div>
          <div class="pa-card-body">
            <span class="pa-card-en">Press &amp; Reports</span>
            <h2 class="pa-card-title">相關報導</h2>
            <p class="pa-card-desc">
              收錄各方媒體對龐會督事奉生涯的相關採訪、報導與評論，見證其影響廣及教會與社會。
            </p>
          </div>
          <span class="pa-card-arrow">→</span>
        </NuxtLink>

        <!-- 7. 照片錦集 -->
        <NuxtLink to="/pong-archive/photos" class="pa-card pa-card--photos">
          <div class="pa-card-icon">
            <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
              <rect x="6" y="12" width="36" height="28" rx="3" stroke="currentColor" stroke-width="2" fill="none"/>
              <circle cx="24" cy="26" r="7" stroke="currentColor" stroke-width="1.5" fill="none"/>
              <circle cx="24" cy="26" r="3" fill="currentColor" opacity="0.35"/>
              <rect x="18" y="7" width="12" height="5" rx="2" stroke="currentColor" stroke-width="1.5" fill="none"/>
              <circle cx="38" cy="18" r="2" fill="currentColor" opacity="0.5"/>
            </svg>
          </div>
          <div class="pa-card-body">
            <span class="pa-card-en">Photo Gallery</span>
            <h2 class="pa-card-title">照片錦集</h2>
            <p class="pa-card-desc">
              龐會督歷年事奉、按立、退修、教導與生活的影像紀錄，以圖像留存其生命風範。
            </p>
          </div>
          <span class="pa-card-arrow">→</span>
        </NuxtLink>

        <!-- 7. 回憶與緬懷 -->
        <NuxtLink to="/pong-archive/remembrance" class="pa-card pa-card--remembrance">
          <div class="pa-card-icon">
            <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
              <path d="M24 8 C14 8, 8 15, 8 22 C8 32, 24 42, 24 42 C24 42, 40 32, 40 22 C40 15, 34 8, 24 8Z" stroke="currentColor" stroke-width="2" fill="none"/>
              <path d="M24 16 L24 28" stroke="currentColor" stroke-width="1.5"/>
              <path d="M18 22 L30 22" stroke="currentColor" stroke-width="1.5"/>
            </svg>
          </div>
          <div class="pa-card-body">
            <span class="pa-card-en">Remembrance</span>
            <h2 class="pa-card-title">回憶與緬懷</h2>
            <p class="pa-card-desc">
              訪談錄、回憶錄、悼詞，以及他人對龐會督生平思想的研究文章，留存眾人對他的敬念。
            </p>
          </div>
          <span class="pa-card-arrow">→</span>
        </NuxtLink>

      </div>
    </section>

    <!-- ── About Section ─────────────────────────────────── -->
    <section class="pa-about">
      <div class="pa-about-inner">
        <h2 class="pa-about-heading">關於本典藏</h2>
        <p class="pa-about-text">
          龐君華會督畢生事奉於教會牧養、神學教育與合一對話。
          本典藏蒐集其歷年講道、著述與私人文件，以數位形式完整保存，
          盼望這些信仰遺產能繼續滋養後代的靈命與思考。
        </p>
      </div>
    </section>

  </div>
</template>

<script setup>
definePageMeta({
  layout: 'pong-archive',
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500&family=Noto+Serif+TC:wght@400;500;600&display=swap');

/* ── Base ──────────────────────────────────────────────── */
.pa-page {
  font-family: 'Noto Sans TC', 'PingFang TC', 'Microsoft JhengHei', sans-serif;
  color: #2C2C2C;
  background-color: #F9F8F6;
}

/* ── Hero ──────────────────────────────────────────────── */
.pa-hero {
  padding: 80px 40px 60px;
  text-align: center;
  background-color: #F9F8F6;
}

.pa-hero-inner {
  max-width: 720px;
  margin: 0 auto;
}

.pa-hero-eyebrow {
  font-family: 'Noto Sans TC', sans-serif;
  font-size: 0.8rem;
  font-weight: 300;
  color: #9A9188;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  margin: 0 0 20px;
}

.pa-hero-title {
  font-family: 'Noto Serif TC', 'SimSun', serif;
  font-size: clamp(1.8rem, 4vw, 2.6rem);
  font-weight: 500;
  color: #2C2C2C;
  letter-spacing: 0.12em;
  line-height: 1.4;
  margin: 0 0 48px;
}

.pa-hero-quote {
  margin: 0 0 40px;
  padding: 28px 36px;
  background-color: #F2EFE9;
  border-left: 3px solid #C4B99A;
  text-align: left;
  border-radius: 2px;
}

.pa-hero-quote-text {
  font-family: 'Noto Serif TC', serif;
  font-size: 1rem;
  line-height: 2;
  letter-spacing: 0.06em;
  color: #3E3A35;
  margin: 0 0 12px;
}

.pa-hero-quote-cite {
  display: block;
  font-family: 'Noto Sans TC', sans-serif;
  font-size: 0.78rem;
  font-weight: 300;
  color: #9A9188;
  letter-spacing: 0.1em;
  font-style: normal;
}

.pa-hero-rule {
  width: 48px;
  height: 1px;
  background-color: #C4B99A;
  margin: 0 auto;
}

/* ── Collections Grid ──────────────────────────────────── */
.pa-collections {
  padding: 64px 40px;
  background-color: #F4F1EC;
}

.pa-collections-inner {
  max-width: 1100px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 28px;
}

.pa-collections-inner .pa-card:last-child:nth-child(3n+1) {
  grid-column: 2;
}

/* ── Card ──────────────────────────────────────────────── */
.pa-card {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 36px 32px;
  background-color: #F9F8F6;
  border: 1px solid #DDD8CF;
  border-radius: 4px;
  text-decoration: none;
  color: inherit;
  position: relative;
  transition: border-color 0.25s ease, box-shadow 0.25s ease, transform 0.25s ease;
}

.pa-card:hover {
  border-color: #C4B99A;
  box-shadow: 0 6px 24px rgba(60, 50, 40, 0.08);
  transform: translateY(-3px);
}

.pa-card-icon {
  width: 48px;
  height: 48px;
  color: #9A8E7E;
  flex-shrink: 0;
}

.pa-card-icon svg {
  width: 100%;
  height: 100%;
}

.pa-card-body {
  flex: 1;
}

.pa-card-en {
  display: block;
  min-height: 1.6em;
  font-family: 'Noto Sans TC', sans-serif;
  font-size: 0.7rem;
  font-weight: 300;
  color: #B0A690;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  margin-bottom: 6px;
}

.pa-card-title {
  font-family: 'Noto Serif TC', serif;
  font-size: 1.3rem;
  font-weight: 500;
  color: #2C2C2C;
  letter-spacing: 0.1em;
  margin: 0 0 14px;
  line-height: 1.4;
}

.pa-card-desc {
  font-family: 'Noto Sans TC', sans-serif;
  font-size: 0.85rem;
  font-weight: 300;
  color: #6A6460;
  line-height: 1.9;
  letter-spacing: 0.04em;
  margin: 0;
}

.pa-card-arrow {
  align-self: flex-end;
  font-size: 1rem;
  color: #B0A690;
  transition: color 0.2s ease, transform 0.2s ease;
}

.pa-card:hover .pa-card-arrow {
  color: #7A6E5E;
  transform: translateX(4px);
}

/* ── About ─────────────────────────────────────────────── */
.pa-about {
  padding: 72px 40px;
  background-color: #F9F8F6;
  border-top: 1px solid #DDD8CF;
}

.pa-about-inner {
  max-width: 680px;
  margin: 0 auto;
  text-align: center;
}

.pa-about-heading {
  font-family: 'Noto Serif TC', serif;
  font-size: 1.1rem;
  font-weight: 500;
  color: #3A3530;
  letter-spacing: 0.14em;
  margin: 0 0 24px;
}

.pa-about-text {
  font-family: 'Noto Sans TC', sans-serif;
  font-size: 0.9rem;
  font-weight: 300;
  color: #5A5550;
  line-height: 2;
  letter-spacing: 0.05em;
  margin: 0;
}

/* ── Responsive ────────────────────────────────────────── */
@media (max-width: 900px) {
  .pa-collections-inner {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .pa-hero {
    padding: 56px 24px 48px;
  }

  .pa-hero-quote {
    padding: 20px 24px;
  }

  .pa-collections {
    padding: 48px 24px;
  }

  .pa-collections-inner {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .pa-about {
    padding: 56px 24px;
  }
}
</style>
