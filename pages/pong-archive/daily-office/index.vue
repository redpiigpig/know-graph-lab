<template>
  <div class="do-page">

    <div class="do-topbar">
      <NuxtLink to="/pong-archive" class="do-back">← 返回典藏首頁</NuxtLink>
    </div>

    <header class="do-header">
      <p class="do-eyebrow">Daily Office</p>
      <h1 class="do-title">三讀三禱</h1>
      <p class="do-subtitle">每日經課與祈禱文</p>
    </header>

    <!-- ── 今日經課 banner ────────────────────────────────── -->
    <section class="do-today" :style="{ backgroundColor: todayColor.bg }">
      <div class="do-today-inner">
        <div class="do-today-meta">
          <span class="do-today-cycle">{{ todayCycleLabel }}</span>
          <span class="do-today-sep">·</span>
          <span class="do-today-season">{{ todaySlot?.seasonZh || '—' }}</span>
        </div>
        <div class="do-today-date">{{ todayDateLabel }}</div>
        <div class="do-today-label">{{ todaySlot?.label || '計算中…' }}</div>
        <NuxtLink
          v-if="todaySlot"
          :to="`/pong-archive/daily-office/${todayCycleEn}/${todaySlot.season}/${todaySlot.week}`"
          class="do-today-btn"
        >
          今日經課 →
        </NuxtLink>
      </div>
    </section>

    <!-- ── 三個圓餅圖 ──────────────────────────────────────── -->
    <section class="do-wheels-section">
      <div class="do-wheels-grid">
        <div v-for="yi in YEAR_INFO" :key="yi.yearEn" class="do-wheel-wrap">
          <div class="do-wheel-label">
            <span class="do-wheel-cycle">{{ yi.cycle }}年</span>
            <span class="do-wheel-en">Year {{ yi.yearEn }}</span>
            <span class="do-wheel-gospel">{{ yi.gospel }}</span>
          </div>

          <div class="do-wheel-container">
            <svg
              viewBox="-1 -1 2 2"
              class="do-wheel-svg"
              @mouseleave="tooltip = null"
            >
              <path
                v-for="(slot, i) in baseSlices"
                :key="i"
                :d="slot.path"
                :fill="slot.color"
                stroke="#F9F8F6"
                stroke-opacity="0.35"
                stroke-width="0.005"
                class="do-slice do-slice--active"
                style="cursor: pointer"
                @mouseenter="onSliceHover($event, slot, yi.yearEn)"
                @click="onSliceClick(slot, yi.yearEn)"
              />
              <!-- 中心圓 -->
              <circle cx="0" cy="0" r="0.38" fill="#F9F8F6" />
              <text x="0" y="0.05" text-anchor="middle" class="do-center-text-main">{{ yi.cycle }}年</text>
            </svg>

            <!-- Tooltip -->
            <div
              v-if="tooltip && tooltip.yearEn === yi.yearEn"
              class="do-tooltip"
              :style="{ top: tooltip.y + 'px', left: tooltip.x + 'px' }"
            >
              <span class="do-tooltip-label">{{ tooltip.label }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 色票說明 -->
    <section class="do-legend">
      <div class="do-legend-inner">
        <div v-for="(v, k) in SEASON_COLORS" :key="k" class="do-legend-item">
          <span class="do-legend-dot" :style="{ backgroundColor: v.bg }"></span>
          <span class="do-legend-name">{{ v.name }}</span>
        </div>
      </div>
    </section>

    <!-- Team credits -->
    <footer class="do-credits">
      <div class="do-credits-inner">
        <div class="do-credits-grid">
          <div v-for="c in TEAM_CREDITS" :key="c.role" class="do-credit-row">
            <span class="do-credit-role">{{ c.role }}</span>
            <span class="do-credit-names">{{ c.names }}</span>
          </div>
        </div>
        <p class="do-credits-site-label">官方網站</p>
        <a href="https://www.1day3read3pray.com/" target="_blank" rel="noopener" class="do-credits-link">www.1day3read3pray.com</a>
      </div>
    </footer>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  getLectionaryYear,
  getLectionaryYearEn,
  getCurrentChurchYear,
  findTodaySlot,
  getFixedLectionarySlots,
  SEASON_COLORS,
} from '~/composables/useChurchCalendar.js'

definePageMeta({ layout: 'pong-archive' })

// 典藏總覽頁顯示最新版工作團隊（逐週精確版見各週頁面 weekData.team_credits）
const TEAM_CREDITS = [
  { role: '內容原稿', names: '龐君華' },
  { role: '文字工作', names: '邱泰耀、褚秀玲、鄭沂珊' },
  { role: '影音工作', names: '蕭曉玲、呂華光、褚秀玲' },
  { role: '後勤協作', names: '蕭毓蓉' },
  { role: '封面設計', names: '王柏欽' },
  { role: '整合執行', names: '陳繼賢、張芝嘉' },
]

// ── 今日資訊 ──────────────────────────────────────────────
const today = new Date()
const { churchYear: todayChurchYear, slot: todaySlot } = findTodaySlot(today)
const todayCycle = getLectionaryYear(todayChurchYear)
const todayCycleEn = getLectionaryYearEn(todayChurchYear)
const todayCycleLabel = `${todayCycle}年（Year ${todayCycleEn}）`
const todayColor = computed(() =>
  todaySlot ? (SEASON_COLORS[todaySlot.season] || SEASON_COLORS.pentecost) : SEASON_COLORS.advent
)
const weekdays = ['週日', '週一', '週二', '週三', '週四', '週五', '週六']
const todayDateLabel = `${today.getFullYear()} 年 ${today.getMonth() + 1} 月 ${today.getDate()} 日　${weekdays[today.getDay()]}`

// ── 固定 57 週圓餅圖（三個圓餅結構相同，只有年份標籤不同） ──
const rawSlots = getFixedLectionarySlots()
const TOTAL = rawSlots.length // 57
const anglePerSlice = (2 * Math.PI) / TOTAL
const startAngle = -Math.PI / 2
const r = 0.95

const baseSlices = rawSlots.map((slot, i) => {
  const a1 = startAngle + i * anglePerSlice
  const a2 = a1 + anglePerSlice
  const x1 = Math.cos(a1) * r, y1 = Math.sin(a1) * r
  const x2 = Math.cos(a2) * r, y2 = Math.sin(a2) * r
  return {
    ...slot,
    path: `M 0 0 L ${x1} ${y1} A ${r} ${r} 0 0 1 ${x2} ${y2} Z`,
    color: SEASON_COLORS[slot.season]?.bg || '#888',
  }
})

const YEAR_INFO = [
  { yearEn: 'A', cycle: '甲', gospel: '馬太年' },
  { yearEn: 'B', cycle: '乙', gospel: '馬可年' },
  { yearEn: 'C', cycle: '丙', gospel: '路加年' },
]

// ── Tooltip ───────────────────────────────────────────────
const tooltip = ref(null)

function onSliceHover(event, slot, yearEn) {
  const svgRect = event.currentTarget.closest('svg').getBoundingClientRect()
  tooltip.value = {
    yearEn,
    label: slot.label,
    x: event.clientX - svgRect.left + 12,
    y: event.clientY - svgRect.top - 8,
  }
}

function onSliceClick(slot, yearEn) {
  navigateTo(`/pong-archive/daily-office/${yearEn}/${slot.season}/${slot.week}`)
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500&family=Noto+Serif+TC:wght@400;500;600&display=swap');

.do-page {
  background-color: #F9F8F6;
  min-height: 100vh;
  font-family: 'Noto Sans TC', sans-serif;
  color: #2C2C2C;
}

/* ── Topbar ─────────────────────────────────────────────── */
.do-topbar { padding: 20px 48px; border-bottom: 1px solid #DDD8CF; }
.do-back { font-size: 0.8rem; color: #8A8278; text-decoration: none; letter-spacing: 0.06em; transition: color 0.2s; }
.do-back:hover { color: #3A3025; }

/* ── Header ─────────────────────────────────────────────── */
.do-header { text-align: center; padding: 56px 40px 40px; border-bottom: 1px solid #E8E4DC; }
.do-eyebrow { font-size: 0.72rem; font-weight: 300; color: #A09280; letter-spacing: 0.22em; text-transform: uppercase; margin: 0 0 10px; }
.do-title { font-family: 'Noto Serif TC', serif; font-size: 2rem; font-weight: 500; color: #2C2C2C; letter-spacing: 0.12em; margin: 0 0 10px; }
.do-subtitle { font-size: 0.85rem; font-weight: 300; color: #7A7268; letter-spacing: 0.06em; margin: 0; }

/* ── Today Banner ───────────────────────────────────────── */
.do-today {
  transition: background-color 0.4s;
}
.do-today-inner {
  max-width: 720px;
  margin: 0 auto;
  padding: 40px 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  text-align: center;
}
.do-today-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.72rem;
  font-weight: 300;
  color: rgba(255,255,255,0.75);
  letter-spacing: 0.14em;
  text-transform: uppercase;
}
.do-today-sep { opacity: 0.5; }
.do-today-date {
  font-size: 0.82rem;
  font-weight: 300;
  color: rgba(255,255,255,0.85);
  letter-spacing: 0.1em;
}
.do-today-label {
  font-family: 'Noto Serif TC', serif;
  font-size: 1.5rem;
  font-weight: 500;
  color: #fff;
  letter-spacing: 0.12em;
  margin: 4px 0 8px;
}
.do-today-btn {
  display: inline-block;
  padding: 8px 24px;
  border: 1.5px solid rgba(255,255,255,0.6);
  color: #fff;
  text-decoration: none;
  font-size: 0.78rem;
  font-weight: 300;
  letter-spacing: 0.12em;
  border-radius: 2px;
  transition: background-color 0.2s, border-color 0.2s;
}
.do-today-btn:hover { background-color: rgba(255,255,255,0.15); border-color: #fff; }

/* ── Wheels ─────────────────────────────────────────────── */
.do-wheels-section {
  padding: 56px 24px 40px;
  max-width: 1100px;
  margin: 0 auto;
}
.do-wheels-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 32px;
  align-items: start;
}
.do-wheel-wrap { display: flex; flex-direction: column; align-items: center; gap: 16px; }
.do-wheel-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
}
.do-wheel-cycle {
  font-family: 'Noto Serif TC', serif;
  font-size: 1.1rem;
  font-weight: 500;
  color: #3A3025;
  letter-spacing: 0.1em;
}
.do-wheel-en { font-size: 0.68rem; font-weight: 300; color: #A09280; letter-spacing: 0.16em; text-transform: uppercase; }
.do-wheel-gospel { font-family: 'Noto Serif TC', serif; font-size: 1.1rem; font-weight: 500; color: #3A3025; letter-spacing: 0.1em; }

.do-wheel-container {
  position: relative;
  width: 100%;
  max-width: 300px;
}
.do-wheel-svg {
  width: 100%;
  height: auto;
  display: block;
  overflow: visible;
}

.do-slice { transition: opacity 0.15s; }
.do-slice--active:hover { opacity: 0.82 !important; }

.do-center-text-main {
  font-family: 'Noto Serif TC', serif;
  font-size: 0.14px;
  font-weight: 500;
  fill: #3A3025;
  letter-spacing: 0.01em;
}

/* ── Tooltip ─────────────────────────────────────────────── */
.do-tooltip {
  position: absolute;
  pointer-events: none;
  background: rgba(40, 30, 20, 0.92);
  color: #fff;
  padding: 8px 12px;
  border-radius: 3px;
  font-size: 0.75rem;
  line-height: 1.6;
  white-space: nowrap;
  z-index: 10;
  display: flex;
  flex-direction: column;
  gap: 2px;
  backdrop-filter: blur(4px);
}
.do-tooltip-label { font-weight: 500; letter-spacing: 0.06em; }

/* ── Legend ─────────────────────────────────────────────── */
.do-legend {
  padding: 24px 40px 48px;
  border-top: 1px solid #E8E4DC;
}
.do-legend-inner {
  max-width: 720px;
  margin: 0 auto;
  display: flex;
  flex-wrap: wrap;
  gap: 16px 28px;
  justify-content: center;
}
.do-legend-item { display: flex; align-items: center; gap: 8px; }
.do-legend-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.do-legend-name { font-size: 0.75rem; font-weight: 300; color: #7A7268; letter-spacing: 0.06em; }

/* ── Team credits ─────────────────────────────────────────── */
.do-credits { border-top: 1px solid #E8E4DC; background: #F2EFE9; }
.do-credits-inner { max-width: 720px; margin: 0 auto; padding: 40px 40px 48px; text-align: center; }
.do-credits-grid { display: grid; grid-template-columns: auto auto; gap: 6px 20px; width: fit-content; margin: 0 auto 24px; text-align: left; }
.do-credit-row { display: contents; }
.do-credit-role { font-size: 0.7rem; font-weight: 500; color: #9A9080; letter-spacing: 0.12em; padding-top: 2px; white-space: nowrap; }
.do-credit-names { font-family: 'Noto Serif TC', serif; font-size: 0.85rem; color: #5A5040; letter-spacing: 0.04em; line-height: 1.8; }
.do-credits-site-label { font-size: 0.65rem; font-weight: 500; color: #9A9080; letter-spacing: 0.18em; text-transform: uppercase; margin: 0 0 6px; }
.do-credits-link {
  display: inline-block;
  font-size: 0.78rem;
  color: #7A7268;
  letter-spacing: 0.1em;
  text-decoration: none;
  border-bottom: 1px solid #C8C0B0;
  padding-bottom: 1px;
  transition: color 0.2s, border-color 0.2s;
}
.do-credits-link:hover { color: #3A3025; border-color: #3A3025; }

/* ── Responsive ─────────────────────────────────────────── */
@media (max-width: 768px) {
  .do-wheels-grid { grid-template-columns: 1fr; gap: 40px; }
  .do-wheel-container { max-width: 280px; }
  .do-topbar { padding: 16px 20px; }
  .do-today-inner { padding: 32px 20px; }
  .do-credits-inner { padding: 32px 20px 40px; }
  .do-credits-grid { gap: 4px 14px; }
}
</style>
