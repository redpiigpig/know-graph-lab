<template>
  <div class="sy-page">
    <div class="sy-topbar">
      <NuxtLink to="/pong-archive/sermons" class="sy-back">← 講道集</NuxtLink>
    </div>

    <header class="sy-header">
      <p class="sy-eyebrow">Church Year</p>
      <h1 class="sy-title">{{ year }}–{{ year + 1 }} 教會年</h1>
      <p class="sy-range">{{ churchYearRange }}</p>
    </header>

    <div v-if="!isValidYear" class="sy-error">
      年份超出典藏範圍（2000–2001 至 2025–2026）
    </div>

    <section v-else class="sy-body">
      <div
        v-for="group in groupedWeeks"
        :key="group.seasonKey + group.index"
        class="sy-season-group"
      >
        <div class="sy-season-header" :style="{ backgroundColor: group.color }">
          <span class="sy-season-name">{{ group.seasonName }}</span>
          <span class="sy-season-count">{{ group.sundayCount }} 主日</span>
        </div>

        <div class="sy-weeks">
          <template v-for="entry in group.entries" :key="entry.dateStr">

            <!-- 特殊日期行 -->
            <div
              v-if="entry.isSpecial"
              class="sy-week-row sy-week-row--special"
              :class="{ 'sy-week-row--funeral': entry.isFuneral }"
            >
              <span class="sy-bar" :style="{ backgroundColor: entry.specialColor }"></span>
              <span class="sy-week-label">{{ entry.specialName }}</span>
              <NuxtLink
                v-if="sermonFor(entry.date)"
                :to="`/pong-archive/sermons/${sermonFor(entry.date).sermon_date}`"
                class="sy-sermon-title"
              >{{ sermonFor(entry.date).title }}</NuxtLink>
              <span v-else class="sy-sermon-title"></span>
              <span class="sy-week-date">{{ entry.dateStr }}</span>
            </div>

            <!-- 主日行 -->
            <div v-else class="sy-week-row">
              <span class="sy-bar" :style="{ backgroundColor: entry.barColor || group.color }"></span>
              <span class="sy-week-label">{{ entry.weekLabel }}</span>
              <NuxtLink
                v-if="sermonFor(entry.date)"
                :to="`/pong-archive/sermons/${sermonFor(entry.date).sermon_date}`"
                class="sy-sermon-title"
              >{{ sermonFor(entry.date).title }}</NuxtLink>
              <span v-else class="sy-sermon-title"></span>
              <span class="sy-week-date">{{ entry.dateStr }}</span>
            </div>

          </template>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { createClient } from '@supabase/supabase-js'

definePageMeta({ layout: 'pong-archive' })

const route = useRoute()
const year = parseInt(route.params.year)
const isValidYear = year >= 2000 && year <= 2025

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_KEY,
)

// ── Sermon data ───────────────────────────────────────────
const sermons = ref([])

const sermonMap = computed(() => {
  const map = {}
  for (const s of sermons.value) {
    if (s.sermon_date) map[s.sermon_date] = s
  }
  return map
})

function sermonFor(date) {
  const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
  return sermonMap.value[key] || null
}

onMounted(async () => {
  if (!isValidYear) return
  const { data } = await supabase
    .from('pong_sermons')
    .select('id, title, sermon_date')
    .eq('church_year', year)
    .eq('is_published', true)
  sermons.value = data || []
})

// ── 典藏截止：2026年1月31日（六）────────────────────────────
const ARCHIVE_CUTOFF = new Date(2026, 0, 31)

// ── 曆算工具函式 ──────────────────────────────────────────
function getAdvent1(y) {
  const nov30 = new Date(y, 10, 30)
  const dow = nov30.getDay()
  const offset = dow === 0 ? 0 : dow <= 3 ? -dow : 7 - dow
  const d = new Date(nov30)
  d.setDate(nov30.getDate() + offset)
  return d
}

function getEaster(y) {
  const a = y % 19
  const b = Math.floor(y / 100)
  const c = y % 100
  const d = Math.floor(b / 4)
  const e = b % 4
  const f = Math.floor((b + 8) / 25)
  const g = Math.floor((b - f + 1) / 3)
  const h = (19 * a + b - d - g + 15) % 30
  const i = Math.floor(c / 4)
  const k = c % 4
  const l = (32 + 2 * e + 2 * i - h - k) % 7
  const m = Math.floor((a + 11 * h + 22 * l) / 451)
  const month = Math.floor((h + l - 7 * m + 114) / 31)
  const day = ((h + l - 7 * m + 114) % 31) + 1
  return new Date(y, month - 1, day)
}

function addDays(date, days) {
  const d = new Date(date)
  d.setDate(d.getDate() + days)
  return d
}

function dateEqual(a, b) {
  return a.getFullYear() === b.getFullYear()
    && a.getMonth() === b.getMonth()
    && a.getDate() === b.getDate()
}

function fmtDate(d) {
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`
}

const DOW_ZH = ['（日）', '（一）', '（二）', '（三）', '（四）', '（五）', '（六）']

const CH = ['○','一','二','三','四','五','六','七','八','九','十',
  '十一','十二','十三','十四','十五','十六','十七','十八','十九','二十',
  '二十一','二十二','二十三','二十四','二十五','二十六','二十七','二十八']
function cn(n) { return CH[n] ?? String(n) }

// ── 節期設定 ──────────────────────────────────────────────
const SEASONS = {
  advent:    { name: '將臨期',     color: '#5B3F8A' },
  christmas: { name: '聖誕期',     color: '#A07828' },
  epiphany:  { name: '顯現期',     color: '#2A6E3A' },
  lent:      { name: '大齋期',     color: '#7B2D6E' },
  easter:    { name: '復活期',     color: '#A07828' },
  pentecost: { name: '聖靈降臨期', color: '#2A6E3A' },
}

function sundayLabel(sk, n, isDec25, isPentecost, isChristKing) {
  switch (sk) {
    case 'advent':    return `將臨期第${cn(n)}主日`
    case 'christmas': return isDec25 ? '聖誕節主日' : `聖誕期第${cn(n)}主日`
    case 'epiphany':  return n === 1 ? '耶穌受洗主日' : `顯現期第${cn(n)}主日`
    case 'lent':      return n === 6 ? '棕枝主日' : `大齋期第${cn(n)}主日`
    case 'easter':
      if (n === 1) return '復活節主日'
      if (isPentecost) return '聖靈降臨節'
      return `復活期第${cn(n)}主日`
    case 'pentecost':
      if (n === 1) return '三一主日'
      if (isChristKing) return '基督君王主日'
      return `聖靈降臨後第${cn(n - 1)}主日`
    default: return ''
  }
}

// ── 建立教會年完整列表 ────────────────────────────────────
function buildChurchYear(y) {
  const ny          = y + 1
  const christmas   = new Date(y,  11, 25)
  const epiphanyDay = new Date(ny,  0,  6)
  const easter      = getEaster(ny)
  const ashWed      = addDays(easter, -46)
  const lent1       = addDays(ashWed,  4)
  const pentecost   = addDays(easter, 49)
  const goodFriday  = addDays(easter, -2)

  const advent1Next = getAdvent1(y + 1)
  const naturalEnd  = addDays(advent1Next, -1)
  const end         = naturalEnd < ARCHIVE_CUTOFF ? naturalEnd : ARCHIVE_CUTOFF

  const entries = []
  const skCounts = {}
  let cur = new Date(getAdvent1(y))

  while (cur <= end) {
    const t = cur.getTime()
    let sk
    if      (t < christmas.getTime())   sk = 'advent'
    else if (t < epiphanyDay.getTime()) sk = 'christmas'
    else if (t < lent1.getTime())       sk = 'epiphany'
    else if (t < easter.getTime())      sk = 'lent'
    else if (t <= pentecost.getTime())  sk = 'easter'
    else                                 sk = 'pentecost'

    skCounts[sk] = (skCounts[sk] ?? 0) + 1
    const n = skCounts[sk]

    const isDec25      = cur.getMonth() === 11 && cur.getDate() === 25
    const isPent       = dateEqual(cur, pentecost)
    const isChristKing = sk === 'pentecost' && dateEqual(addDays(cur, 7), advent1Next)

    let barColor = null
    if (sk === 'epiphany'  && n === 1) barColor = '#A07828'
    if (sk === 'lent'      && n === 6) barColor = '#B22020'
    if (sk === 'pentecost' && n === 1) barColor = '#A07828'
    if (isChristKing)                  barColor = '#A07828'

    entries.push({
      date:      new Date(cur),
      dateStr:   fmtDate(cur) + DOW_ZH[0],   // 主日固定加（日）
      isSpecial: false,
      seasonKey: sk,
      weekLabel: sundayLabel(sk, n, isDec25, isPent, isChristKing),
      barColor,
    })
    cur = addDays(cur, 7)
  }

  const specials = []

  const christmasEve = new Date(y, 11, 24)
  if (christmasEve.getDay() !== 0 && christmasEve <= end) {
    specials.push({
      date:        christmasEve,
      dateStr:     fmtDate(christmasEve) + DOW_ZH[christmasEve.getDay()],
      isSpecial:   true,
      seasonKey:   'christmas',
      specialName: '平安夜禮拜',
      specialColor:'#A07828',
    })
  }

  if (ashWed <= end) {
    specials.push({
      date:        ashWed,
      dateStr:     fmtDate(ashWed) + DOW_ZH[ashWed.getDay()],
      isSpecial:   true,
      seasonKey:   'lent',
      specialName: '聖灰日',
      specialColor:'#6B4A90',
    })
  }

  if (goodFriday <= end) {
    specials.push({
      date:        goodFriday,
      dateStr:     fmtDate(goodFriday) + DOW_ZH[goodFriday.getDay()],
      isSpecial:   true,
      seasonKey:   'lent',
      specialName: '受難日禮拜',
      specialColor:'#8B1818',
    })
  }

  if (y === 2018) {
    const installation = new Date(2019, 4, 25)
    if (installation <= end) {
      specials.push({
        date:        installation,
        dateStr:     fmtDate(installation) + DOW_ZH[installation.getDay()],
        isSpecial:   true,
        seasonKey:   'easter',
        specialName: '龐君華會督就任禮拜',
        specialColor:'#B22020',
      })
    }
  }

  if (y === 2025) {
    const funeral = new Date(2026, 0, 31)
    specials.push({
      date:        funeral,
      dateStr:     fmtDate(funeral) + DOW_ZH[funeral.getDay()],
      isSpecial:   true,
      isFuneral:   true,
      seasonKey:   'epiphany',
      specialName: '龐君華會督告別式',
      specialColor:'#3A3530',
    })
  }

  return [...entries, ...specials].sort((a, b) => a.date - b.date)
}

// ── Computed ──────────────────────────────────────────────
const allEntries = computed(() => isValidYear ? buildChurchYear(year) : [])

const groupedWeeks = computed(() => {
  const groups = []
  let curKey = null
  let curGroup = null
  let groupIndex = 0

  for (const entry of allEntries.value) {
    if (entry.seasonKey !== curKey) {
      curKey = entry.seasonKey
      const s = SEASONS[curKey]
      curGroup = {
        index:       groupIndex++,
        seasonKey:   curKey,
        seasonName:  s.name,
        color:       s.color,
        sundayCount: 0,
        entries:     [],
      }
      groups.push(curGroup)
    }
    curGroup.entries.push(entry)
    if (!entry.isSpecial) curGroup.sundayCount++
  }
  return groups
})

const churchYearRange = computed(() => {
  if (!isValidYear) return ''
  const start      = getAdvent1(year)
  const naturalEnd = addDays(getAdvent1(year + 1), -1)
  const end        = naturalEnd < ARCHIVE_CUTOFF ? naturalEnd : ARCHIVE_CUTOFF
  return `${fmtDate(start)} — ${fmtDate(end)}`
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500&family=Noto+Serif+TC:wght@400;500;600&display=swap');

.sy-page {
  background-color: #F9F8F6;
  min-height: 100vh;
  font-family: 'Noto Sans TC', sans-serif;
  color: #2C2C2C;
}

/* ── Top bar ───────────────────────────────────────────── */
.sy-topbar {
  padding: 20px 48px;
  border-bottom: 1px solid #DDD8CF;
}
.sy-back {
  font-size: 0.8rem;
  color: #8A8278;
  text-decoration: none;
  letter-spacing: 0.06em;
  transition: color 0.2s;
}
.sy-back:hover { color: #3A3025; }

/* ── Header ────────────────────────────────────────────── */
.sy-header {
  text-align: center;
  padding: 56px 40px 40px;
  border-bottom: 1px solid #E8E4DC;
}
.sy-eyebrow {
  font-size: 0.72rem;
  font-weight: 300;
  color: #A09280;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  margin: 0 0 10px;
}
.sy-title {
  font-family: 'Noto Serif TC', serif;
  font-size: 2rem;
  font-weight: 500;
  color: #2C2C2C;
  letter-spacing: 0.12em;
  margin: 0 0 10px;
}
.sy-range {
  font-size: 0.82rem;
  font-weight: 300;
  color: #8A8278;
  letter-spacing: 0.06em;
  margin: 0;
}

/* ── Error ─────────────────────────────────────────────── */
.sy-error {
  text-align: center;
  padding: 80px 40px;
  color: #8A8278;
  font-size: 0.9rem;
}

/* ── Body ──────────────────────────────────────────────── */
.sy-body {
  max-width: 860px;
  margin: 0 auto;
  padding: 48px 40px;
  display: flex;
  flex-direction: column;
  gap: 36px;
}

/* ── Season group ──────────────────────────────────────── */
.sy-season-group {
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid #DDD8CF;
}
.sy-season-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  color: #fff;
}
.sy-season-name {
  font-family: 'Noto Serif TC', serif;
  font-size: 1.05rem;
  font-weight: 500;
  letter-spacing: 0.1em;
}
.sy-season-count {
  font-size: 0.72rem;
  font-weight: 300;
  opacity: 0.85;
  letter-spacing: 0.08em;
}

/* ── Weeks wrapper ─────────────────────────────────────── */
.sy-weeks { background-color: #FAFAF8; }

/* ── Row: 4 columns → bar | label | title(center) | date ── */
.sy-week-row,
.sy-week-row--special {
  display: grid;
  grid-template-columns: 4px auto 1fr auto;
  align-items: center;
  gap: 0 16px;
  padding-right: 20px;
  border-bottom: 1px solid #EDEAE4;
  height: 48px;
  text-decoration: none;
  color: inherit;
  transition: background-color 0.15s;
}
.sy-week-row:last-child,
.sy-week-row--special:last-child { border-bottom: none; }

.sy-week-row:hover { background-color: #F2EFE9; }

.sy-week-row--special {
  height: 48px;
  background-color: #F4F1EC;
}
.sy-week-row--special:hover { background-color: #EDE8E0; }

/* ── Grid children ─────────────────────────────────────── */
.sy-bar {
  align-self: stretch;
  width: 4px;
}

.sy-week-label {
  font-family: 'Noto Serif TC', serif;
  font-size: 0.9rem;
  color: #2C2C2C;
  letter-spacing: 0.06em;
  padding-left: 14px;
  white-space: nowrap;
}


/* Sermon title: center column, link when has sermon */
.sy-sermon-title {
  font-family: 'Noto Serif TC', serif;
  font-size: 0.88rem;
  font-weight: 600;
  color: #5B3F2A;
  letter-spacing: 0.08em;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  text-decoration: none;
}
a.sy-sermon-title:hover {
  text-decoration: underline;
  text-underline-offset: 2px;
}

.sy-week-date {
  font-size: 0.78rem;
  color: #7A7268;
  letter-spacing: 0.04em;
  white-space: nowrap;
}

/* ── 告別式行 ──────────────────────────────────────────── */
.sy-week-row--funeral {
  background-color: #EFEBE4;
  border-top: 2px solid #8A8278;
}
.sy-week-row--funeral .sy-week-date { color: #5A5450; }

/* ── Responsive ────────────────────────────────────────── */
@media (max-width: 640px) {
  .sy-topbar { padding: 16px 20px; }
  .sy-body   { padding: 24px 16px; }
}
</style>
