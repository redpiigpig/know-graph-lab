<template>
  <div v-if="sermon" class="sd-page" :class="{ 'sd-page--editing': isEditing }">

    <!-- ── Topbar ──────────────────────────────────────────── -->
    <div class="sd-topbar">
      <NuxtLink to="/pong-archive/sermons" class="sd-back">← 講道集</NuxtLink>
    </div>

    <!-- ── Header ──────────────────────────────────────────── -->
    <header class="sd-header">
      <div class="sd-header-inner">
        <div class="sd-meta-line">
          <span class="sd-season" :style="{ color: seasonColor }">{{ sermon.liturgical_season }}</span>
          <span class="sd-dot" :style="{ color: seasonColor }">·</span>
          <span class="sd-date" :style="{ color: seasonColor }">{{ formatDate(sermon.sermon_date) }}</span>
        </div>

        <div class="sd-title-wrap">
          <textarea
            v-if="isEditing"
            v-model="local.title"
            class="sd-title sd-textarea"
            rows="1"
            placeholder="講道標題"
            @input="e => { autoResize(e.target); save('title', local.title) }"
            ref="titleRef"
          />
          <h1 v-else class="sd-title">{{ sermon.title }}</h1>

          <div class="sd-sub-line">
            <svg class="sd-loc-icon" viewBox="0 0 14 14" fill="none">
              <path d="M7 1C4.79 1 3 2.79 3 5c0 3.25 4 8 4 8s4-4.75 4-8c0-2.21-1.79-4-4-4z" stroke="currentColor" stroke-width="1.2" fill="none"/>
              <circle cx="7" cy="5" r="1.5" stroke="currentColor" stroke-width="1.2"/>
            </svg>
            <input v-if="isEditing" v-model="local.location" class="sd-location sd-input" placeholder="地點" @input="save('location', local.location)" />
            <span v-else class="sd-location">{{ sermon.location || '—' }}</span>
          </div>

          <!-- 一般禮拜 YouTube 按鈕：置中於 header -->
          <div v-if="!isEditing && !isMemorial && sermon.youtube_url" class="sd-yt-header-wrap">
            <a :href="sermon.youtube_url" target="_blank" rel="noopener noreferrer" class="sd-yt-btn">
              <svg class="sd-yt-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M23.8 7.2s-.2-1.7-.9-2.4c-.9-.9-1.9-.9-2.4-1C17.8 3.6 12 3.6 12 3.6s-5.8 0-8.5.2c-.5.1-1.5.1-2.4 1-.7.7-.9 2.4-.9 2.4S0 9.1 0 11v1.8c0 1.9.2 3.8.2 3.8s.2 1.7.9 2.4c.9.9 2.1.8 2.6.9C5.2 20 12 20 12 20s5.8 0 8.5-.2c.5-.1 1.5-.1 2.4-1 .7-.7.9-2.4.9-2.4s.2-1.9.2-3.8V11c0-1.9-.2-3.8-.2-3.8zM9.7 15.5V8.4l6.6 3.6-6.6 3.5z"/>
              </svg>
              觀看完整禮拜錄影
            </a>
          </div>

        </div>

        <div v-if="isEditing" class="sd-edit-hint">✦ 編輯模式</div>
      </div>
    </header>

    <!-- ── YouTube（追思禮拜 iframe / 編輯模式輸入）──────────── -->
    <section
      v-if="(isMemorial && sermon.youtube_url) || isEditing"
      class="sd-section sd-section--video"
    >
      <div class="sd-section-inner">
        <div v-if="!isEditing && isMemorial && youtubeEmbed" class="sd-video-wrap">
          <iframe
            :src="youtubeEmbed"
            title="禮拜影片記錄"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen
            class="sd-video-iframe"
          ></iframe>
        </div>
        <input
          v-if="isEditing"
          v-model="local.youtube_url"
          class="sd-input"
          placeholder="YouTube 連結（https://...）"
          style="width:100%;max-width:480px;"
          @input="save('youtube_url', local.youtube_url)"
        />
      </div>
    </section>

    <!-- ── Service Team ────────────────────────────────────── -->
    <section v-if="isEditing || hasAnyTeamField" class="sd-section sd-section--team">
      <div class="sd-section-inner">
        <h2 class="sd-section-title">服事團隊</h2>
        <div class="sd-team-grid">
          <!-- 城中教會：主禮 / 證道 / 司會 / 讀經 / 領唱 / 獻詩 -->
          <template v-if="isChengzhong">
            <div v-if="isEditing || sermon.officiant" class="sd-team-item">
              <span class="sd-team-label">主禮</span>
              <input v-if="isEditing" v-model="local.officiant" class="sd-team-value sd-input" placeholder="主禮" @input="save('officiant', local.officiant)" />
              <span v-else class="sd-team-value">{{ sermon.officiant }}</span>
            </div>
            <div v-if="isEditing || sermon.preacher" class="sd-team-item">
              <span class="sd-team-label">證道</span>
              <input v-if="isEditing" v-model="local.preacher" class="sd-team-value sd-input" placeholder="證道者" @input="save('preacher', local.preacher)" />
              <span v-else class="sd-team-value">{{ sermon.preacher }}</span>
            </div>
            <div v-if="isEditing || sermon.worship_leader" class="sd-team-item">
              <span class="sd-team-label">司會</span>
              <input v-if="isEditing" v-model="local.worship_leader" class="sd-team-value sd-input" placeholder="司會" @input="save('worship_leader', local.worship_leader)" />
              <span v-else class="sd-team-value">{{ sermon.worship_leader }}</span>
            </div>
            <div v-if="isEditing || sermon.scripture_reader" class="sd-team-item">
              <span class="sd-team-label">讀經</span>
              <input v-if="isEditing" v-model="local.scripture_reader" class="sd-team-value sd-input" placeholder="讀經" @input="save('scripture_reader', local.scripture_reader)" />
              <span v-else class="sd-team-value">{{ sermon.scripture_reader }}</span>
            </div>
            <div v-if="isEditing || sermon.song_leader" class="sd-team-item">
              <span class="sd-team-label">領唱</span>
              <input v-if="isEditing" v-model="local.song_leader" class="sd-team-value sd-input" placeholder="領唱" @input="save('song_leader', local.song_leader)" />
              <span v-else class="sd-team-value">{{ sermon.song_leader }}</span>
            </div>
            <div v-if="isEditing || sermon.choir" class="sd-team-item">
              <span class="sd-team-label">獻詩</span>
              <input v-if="isEditing" v-model="local.choir" class="sd-team-value sd-input" placeholder="獻詩" @input="save('choir', local.choir)" />
              <span v-else class="sd-team-value">{{ sermon.choir }}</span>
            </div>
          </template>
          <!-- 其他教會：證道 / 司會 / 敬拜 -->
          <template v-else>
            <div v-if="isEditing || sermon.preacher" class="sd-team-item">
              <span class="sd-team-label">證道</span>
              <input v-if="isEditing" v-model="local.preacher" class="sd-team-value sd-input" placeholder="證道者" @input="save('preacher', local.preacher)" />
              <span v-else class="sd-team-value">{{ sermon.preacher }}</span>
            </div>
            <div v-if="isEditing || sermon.worship_leader" class="sd-team-item">
              <span class="sd-team-label">司會</span>
              <input v-if="isEditing" v-model="local.worship_leader" class="sd-team-value sd-input" placeholder="司會" @input="save('worship_leader', local.worship_leader)" />
              <span v-else class="sd-team-value">{{ sermon.worship_leader }}</span>
            </div>
            <div v-if="isEditing || sermon.worship_team" class="sd-team-item">
              <span class="sd-team-label">敬拜</span>
              <input v-if="isEditing" v-model="local.worship_team" class="sd-team-value sd-input" placeholder="敬拜團隊" @input="save('worship_team', local.worship_team)" />
              <span v-else class="sd-team-value">{{ sermon.worship_team }}</span>
            </div>
          </template>
        </div>
      </div>
    </section>

    <!-- ── Scripture Readings ──────────────────────────────── -->
    <section v-if="scriptureReadings.length || simpleReadings.length || isEditing" class="sd-section sd-section--scripture">
      <div class="sd-section-inner">
        <h2 class="sd-section-title">經課</h2>
        <div v-if="!scriptureReadings.length && simpleReadings.length" class="sd-scripture-list">
          <div v-for="(r, i) in simpleReadings" :key="i" class="sd-reading sd-reading--static">
            <div class="sd-reading-hd sd-reading-hd--static">
              <div class="sd-reading-ref">
                <span v-if="r.label" class="sd-reading-label">{{ r.label }}</span>
                <span class="sd-reading-book">{{ r.body }}</span>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="sd-scripture-list">
          <div
            v-for="(reading, i) in scriptureReadings"
            :key="i"
            class="sd-reading"
            :class="{ 'sd-reading--open': openReadings.has(i) }"
          >
            <button class="sd-reading-hd" @click="toggleReading(i)">
              <div class="sd-reading-ref">
                <span class="sd-reading-label">{{ reading.display_label }}</span>
                <span class="sd-reading-book">{{ reading.book }} {{ reading.reference }}</span>
              </div>
              <span class="sd-reading-chevron">▾</span>
            </button>
            <Transition name="sd-reading-expand">
              <div v-if="openReadings.has(i)" class="sd-reading-body">
                <p
                  v-for="(line, j) in parseVerses(reading.text)"
                  :key="j"
                  class="sd-verse"
                >
                  <span class="sd-verse-num">{{ line.num }}</span>
                  <span class="sd-verse-text">{{ line.text }}</span>
                </p>
                <p class="sd-bible-version">和合本修訂版 2010（RCUVSS）</p>
              </div>
            </Transition>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Worship Songs ───────────────────────────────────── -->
    <section v-if="worshipSongs.length || isEditing" class="sd-section sd-section--songs">
      <div class="sd-section-inner">
        <h2 class="sd-section-title">禮拜詩歌</h2>
        <div v-if="!isEditing">
          <ul v-if="worshipSongs.length" class="sd-songs-list">
            <li v-for="(song, i) in worshipSongs" :key="i" class="sd-song">{{ song }}</li>
          </ul>
          <p v-else class="sd-songs-empty">—</p>
        </div>
        <textarea
          v-else
          :value="worshipSongsText"
          class="sd-songs-textarea sd-textarea-plain"
          rows="4"
          placeholder="每行一首詩歌名稱"
          @input="onSongsInput"
        />
      </div>
    </section>

    <!-- ── Sermon Content ──────────────────────────────────── -->
    <section class="sd-section sd-section--content">
      <div class="sd-section-inner">
        <h2 class="sd-section-title">講道內容</h2>
        <textarea
          v-if="isEditing"
          v-model="local.content"
          class="sd-content-textarea sd-textarea-plain"
          rows="30"
          placeholder="講道逐字稿或摘要…"
          @input="save('content', local.content)"
        />
        <div v-else class="sd-content-body">
          <template v-for="(item, i) in contentParagraphs" :key="i">
            <p v-if="item.type === 'section'" class="sd-content-section">{{ item.text }}</p>
            <p v-else-if="item.type === 'stage'"   class="sd-content-stage">{{ item.text }}</p>
            <p v-else-if="item.type === 'speaker'" class="sd-content-speaker">{{ item.text }}</p>
            <p v-else class="sd-content-para">{{ item.text }}</p>
          </template>
        </div>
      </div>
    </section>

  </div>

  <div v-else class="sd-notfound">
    <p>找不到此篇講道記錄。</p>
    <NuxtLink to="/pong-archive/sermons">← 返回講道集</NuxtLink>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { createClient } from '@supabase/supabase-js'
import { usePongEditor } from '~/composables/usePongEditor'

definePageMeta({ layout: 'pong-archive' })

const route = useRoute()
const { isEditing, saveField } = usePongEditor()

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_KEY,
)

const { data: sermon } = await useAsyncData(`pong-sermon-${route.params.year}`, async () => {
  const { data, error } = await supabase
    .from('pong_sermons')
    .select('*')
    .eq('sermon_date', route.params.year)
    .eq('is_published', true)
    .single()
  return error ? null : data
})

const local = reactive({})
watch(sermon, (v) => { if (v) Object.assign(local, v) }, { immediate: true })
watch(isEditing, async (on) => {
  if (!on) return
  const { data } = await supabase.from('pong_sermons').select('*').eq('sermon_date', route.params.year).single()
  if (data) Object.assign(local, data)
})

const titleRef = ref(null)
watch(isEditing, async (on) => {
  if (on) { await nextTick(); if (titleRef.value) autoResize(titleRef.value) }
})

function save(field, value) {
  saveField('pong_sermons', sermon.value?.id, field, value)
}

function autoResize(el) {
  el.style.height = 'auto'
  el.style.height = el.scrollHeight + 'px'
}

// ── Location helpers ─────────────────────────────────────────
const isChengzhong = computed(() => (sermon.value?.location || '').includes('城中教會'))
const hasAnyTeamField = computed(() => {
  const s = sermon.value
  if (!s) return false
  return isChengzhong.value
    ? s.officiant || s.preacher || s.worship_leader || s.scripture_reader || s.song_leader || s.choir
    : s.preacher || s.worship_leader || s.worship_team
})

// ── Scripture readings ───────────────────────────────────────
const scriptureReadings = computed(() => {
  const r = sermon.value?.scripture_readings
  if (!r) return []
  return Array.isArray(r) ? r : []
})

// Fallback: parse scripture_ref string ("經課一：使徒行傳 2；啟應文：詩篇 116；…")
// into {label, body} pairs for display-only rendering. No verse text, no expand.
const simpleReadings = computed(() => {
  const ref = sermon.value?.scripture_ref
  if (!ref) return []
  return ref.split(/[；;]/).map(s => s.trim()).filter(Boolean).map(seg => {
    const m = seg.match(/^(經課[一二三四]?|啟應文|福音書|信息經文|詩篇經課)\s*[：:]\s*(.+)$/)
    return m ? { label: m[1], body: m[2].trim() } : { label: '', body: seg }
  })
})

const openReadings = ref(new Set())
function toggleReading(i) {
  const s = new Set(openReadings.value)
  if (s.has(i)) s.delete(i)
  else s.add(i)
  openReadings.value = s
}

function parseVerses(text) {
  if (!text) return []
  return text.split('\n').filter(Boolean).map(line => {
    const m = line.match(/^(\d+)\s+(.*)$/)
    return m ? { num: m[1], text: m[2] } : { num: '', text: line }
  })
}

// ── Worship songs ────────────────────────────────────────────
const worshipSongs = computed(() => {
  const s = sermon.value?.worship_songs
  if (!s) return []
  return Array.isArray(s) ? s.filter(Boolean) : []
})

const worshipSongsText = computed(() => (local.worship_songs || []).join('\n'))

function onSongsInput(e) {
  const arr = e.target.value.split('\n').map(s => s.trim()).filter(Boolean)
  local.worship_songs = arr
  saveField('pong_sermons', sermon.value?.id, 'worship_songs', arr)
}

// ── Content paragraphs ───────────────────────────────────────
// Any line starting with 1-8 chars then ： is treated as a speaker label
const SPEAKER_RE = /^(.{1,8})：(.*)/

function normalizeSpeakerName(name) {
  return name.replace(/^李牧師$/, '李信政牧師')
}

const contentParagraphs = computed(() => {
  const t = sermon.value?.content
  if (!t) return []
  return t.split(/\n+/).filter(Boolean).flatMap(line => {
    if (/^【.+】/.test(line)) return [{ type: 'section', text: line }]
    if (/^[（(]/.test(line))  return [{ type: 'stage',   text: line }]
    const m = line.match(SPEAKER_RE)
    if (m) {
      const results = [{ type: 'speaker', text: normalizeSpeakerName(m[1]) + '：' }]
      if (m[2].trim()) results.push({ type: 'para', text: m[2].trim() })
      return results
    }
    return [{ type: 'para', text: line }]
  })
})

function formatDate(d) {
  if (!d) return '—'
  const dt = new Date(d)
  return `${dt.getFullYear()} 年 ${dt.getMonth() + 1} 月 ${dt.getDate()} 日`
}

const SEASON_COLORS = {
  advent:    '#5B3F8A',
  christmas: '#A07828',
  epiphany:  '#2A6E3A',
  lent:      '#7B2D6E',
  easter:    '#A07828',
  pentecost: '#2A6E3A',
}

const isMemorial = computed(() => /追思|安息/.test(sermon.value?.occasion || ''))

const youtubeEmbed = computed(() => {
  const url = sermon.value?.youtube_url
  if (!url) return null
  const v = url.match(/[?&]v=([^&]+)/)
  const t = url.match(/[?&]t=(\d+)/)
  if (!v) return null
  return `https://www.youtube.com/embed/${v[1]}${t ? `?start=${t[1]}` : ''}`
})

const seasonColor = computed(() => {
  const s = sermon.value?.liturgical_season || ''
  if (/將臨/.test(s))                              return SEASON_COLORS.advent
  if (/聖誕/.test(s))                              return SEASON_COLORS.christmas
  if (/顯現|主顯|耶穌受洗/.test(s))               return SEASON_COLORS.epiphany
  if (/大齋|受難|棕枝|聖灰/.test(s))              return SEASON_COLORS.lent
  if (/復活|聖靈降臨節/.test(s))                  return SEASON_COLORS.easter
  if (/聖靈降臨後|三一|常年/.test(s))             return SEASON_COLORS.pentecost
  return '#8A7E6E'
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500&family=Noto+Serif+TC:wght@400;500;600&display=swap');

.sd-page {
  background-color: #F9F8F6;
  min-height: 100vh;
  font-family: 'Noto Sans TC', sans-serif;
  color: #2C2C2C;
}

/* ── Topbar ─────────────────────────────────────────────── */
.sd-topbar { padding: 20px 48px; border-bottom: 1px solid #DDD8CF; }
.sd-back { font-size: 0.8rem; color: #8A8278; text-decoration: none; letter-spacing: 0.06em; transition: color 0.2s; }
.sd-back:hover { color: #3A3025; }

/* ── Header ─────────────────────────────────────────────── */
.sd-header {
  background-color: #F4F1EC;
  border-bottom: 1px solid #E0DAD0;
  padding: 56px 40px 48px;
  text-align: center;
  transition: background-color 0.3s;
}
.sd-page--editing .sd-header { background-color: #EDE8DF; }
.sd-header-inner { max-width: 720px; margin: 0 auto; }

.sd-meta-line {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 20px;
}
.sd-season { font-size: 0.75rem; font-weight: 500; letter-spacing: 0.12em; }
.sd-dot    { font-size: 0.7rem; opacity: 0.6; }
.sd-date   { font-size: 0.75rem; font-weight: 300; letter-spacing: 0.08em; opacity: 0.9; }

.sd-title {
  font-family: 'Noto Serif TC', serif;
  font-size: clamp(1.6rem, 4vw, 2.4rem);
  font-weight: 500;
  color: #2C2C2C;
  letter-spacing: 0.12em;
  line-height: 1.5;
  margin: 0 0 20px;
}

.sd-sub-line {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
.sd-loc-icon { width: 13px; height: 13px; color: #A09280; flex-shrink: 0; }
.sd-location { font-size: 0.82rem; font-weight: 300; color: #7A7268; letter-spacing: 0.06em; }

/* Edit mode inputs */
.sd-textarea {
  background: transparent;
  border: none;
  border-bottom: 1.5px dashed #C4B89A;
  outline: none;
  font-family: inherit; font-size: inherit; font-weight: inherit; color: inherit;
  letter-spacing: inherit; line-height: inherit;
  width: 100%; resize: none; overflow: hidden;
  padding: 2px 0; text-align: center;
  transition: border-color 0.2s;
}
.sd-textarea:focus { border-bottom-color: #8A7E6E; }
.sd-input {
  background: transparent;
  border: none;
  border-bottom: 1.5px dashed #C4B89A;
  outline: none;
  font-family: inherit; font-size: inherit; font-weight: inherit; color: inherit;
  letter-spacing: inherit; padding: 1px 0; text-align: center;
  transition: border-color 0.2s; width: auto;
}
.sd-input:focus { border-bottom-color: #8A7E6E; }
.sd-edit-hint { margin-top: 16px; font-size: 0.68rem; color: #A09280; letter-spacing: 0.06em; }

/* ── Sections ────────────────────────────────────────────── */
.sd-section { padding: 40px 40px; border-bottom: 1px solid #E8E4DC; }
.sd-section--content { padding-bottom: 80px; border-bottom: none; }
.sd-section-inner { max-width: 720px; margin: 0 auto; }

.sd-section-title {
  font-family: 'Noto Serif TC', serif;
  font-size: 0.88rem;
  font-weight: 500;
  color: #8A7E6E;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  margin: 0 0 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #DDD8CF;
}

/* ── Service Team ─────────────────────────────────────────── */
.sd-section--team { background-color: #F4F1EC; }
.sd-team-grid { display: flex; flex-wrap: wrap; gap: 28px; }
.sd-team-item { display: flex; flex-direction: column; gap: 4px; }
.sd-team-label { font-size: 0.62rem; font-weight: 300; color: #A09280; letter-spacing: 0.12em; text-transform: uppercase; }
.sd-team-value { font-size: 0.92rem; font-weight: 400; color: #2C2C2C; letter-spacing: 0.04em; }

/* ── Title wrap ───────────────────────────────────────────── */
.sd-title-wrap { margin-bottom: 20px; }
.sd-title-wrap .sd-title { margin-bottom: 0; }

/* ── YouTube button in header (一般禮拜) ───────────────────── */
.sd-yt-header-wrap {
  margin-top: 2rem;
  text-align: center;
}

/* ── YouTube embed section (追思禮拜) ──────────────────────── */
.sd-section--video { background-color: #F9F8F6; padding: 48px 40px; border-bottom: 1px solid #E8E4DC; }
.sd-section--video .sd-section-inner { max-width: 720px; margin: 0 auto; }

.sd-yt-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 18px;
  background: #CC0000;
  color: #fff;
  text-decoration: none;
  border-radius: 3px;
  font-family: 'Noto Sans TC', sans-serif;
  font-size: 0.8rem;
  font-weight: 400;
  letter-spacing: 0.08em;
  transition: background 0.2s;
}
.sd-yt-btn:hover { background: #AA0000; }
.sd-yt-icon { width: 15px; height: 15px; flex-shrink: 0; }
.sd-video-wrap {
  position: relative;
  width: 100%;
  padding-top: 56.25%;
  border-radius: 4px;
  overflow: hidden;
  background-color: #000;
  box-shadow: 0 8px 32px rgba(40,30,20,0.18);
}
.sd-video-iframe {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  border: none;
}

/* ── Scripture ────────────────────────────────────────────── */
.sd-scripture-list { display: flex; flex-direction: column; gap: 0; border: 1px solid #DDD8CF; border-radius: 4px; overflow: hidden; }

/* Static (non-clickable) variant for scripture_ref fallback rows — borderless, plain inline */
.sd-scripture-list:has(.sd-reading--static) { border: none; border-radius: 0; }
.sd-reading--static { border-bottom: none; }
.sd-reading--static .sd-reading-hd--static { cursor: default; background: transparent; padding: 4px 0; }
.sd-reading--static .sd-reading-hd--static:hover { background: transparent; }

.sd-reading { border-bottom: 1px solid #DDD8CF; }
.sd-reading:last-child { border-bottom: none; }

.sd-reading-hd {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  background: #FDFCFA;
  border: none;
  cursor: pointer;
  text-align: left;
  transition: background-color 0.15s;
  gap: 12px;
}
.sd-reading-hd:hover { background-color: #F4F1EC; }
.sd-reading--open .sd-reading-hd { background-color: #F0EDE6; }

.sd-reading-ref { display: flex; align-items: center; gap: 12px; min-width: 0; }
.sd-reading-label { font-size: 0.65rem; font-weight: 400; color: #A09280; letter-spacing: 0.12em; text-transform: uppercase; white-space: nowrap; }
.sd-reading-book { font-family: 'Noto Serif TC', serif; font-size: 0.92rem; font-weight: 500; color: #3A3025; letter-spacing: 0.06em; }
.sd-reading-chevron { color: #A09280; font-size: 0.75rem; transition: transform 0.2s; flex-shrink: 0; }
.sd-reading--open .sd-reading-chevron { transform: rotate(180deg); }

.sd-reading-body { padding: 20px 20px 24px; background-color: #FDFCFA; border-top: 1px solid #EDE8DF; }
.sd-reading-expand-enter-active, .sd-reading-expand-leave-active { transition: opacity 0.2s; }
.sd-reading-expand-enter-from, .sd-reading-expand-leave-to { opacity: 0; }

.sd-verse { display: grid; grid-template-columns: 28px 1fr; gap: 0 8px; margin: 0 0 6px; }
.sd-verse-num { font-size: 0.68rem; color: #B0A890; font-weight: 400; padding-top: 3px; text-align: right; }
.sd-verse-text { font-family: 'Noto Serif TC', serif; font-size: 0.9rem; font-weight: 400; color: #2C2C2C; line-height: 1.9; letter-spacing: 0.04em; }
.sd-bible-version { margin: 16px 0 0; font-size: 0.68rem; font-weight: 300; color: #B0A890; letter-spacing: 0.1em; text-align: right; }

/* ── Worship songs ────────────────────────────────────────── */
.sd-songs-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px; }
.sd-song { font-size: 0.9rem; font-weight: 300; color: #3A3530; letter-spacing: 0.04em; padding-left: 16px; position: relative; }
.sd-song::before { content: '♩'; position: absolute; left: 0; color: #C4B89A; font-size: 0.75rem; }
.sd-songs-empty { font-size: 0.85rem; color: #B0A890; letter-spacing: 0.04em; }

.sd-textarea-plain {
  width: 100%;
  background-color: #FDFCFA;
  border: 1.5px dashed #C4B89A;
  border-radius: 3px;
  padding: 12px 16px;
  font-family: 'Noto Sans TC', sans-serif;
  font-size: 0.88rem;
  font-weight: 300;
  color: #2C2C2C;
  line-height: 1.9;
  letter-spacing: 0.04em;
  resize: vertical;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}
.sd-textarea-plain:focus { border-color: #8A7E6E; }

/* ── Sermon content ───────────────────────────────────────── */
.sd-content-body { display: flex; flex-direction: column; gap: 1.2em; }
.sd-content-para {
  font-family: 'Noto Serif TC', serif;
  font-size: 1rem;
  font-weight: 400;
  color: #2C2C2C;
  line-height: 2.1;
  letter-spacing: 0.06em;
  text-align: justify;
  text-indent: 2em;
  margin: 0;
}
.sd-content-speaker {
  font-family: 'Noto Serif TC', serif;
  font-size: 1rem;
  font-weight: 700;
  color: #2C2C2C;
  line-height: 2.1;
  letter-spacing: 0.06em;
  text-indent: 0;
  margin: 0.4em 0 0;
}
.sd-content-section {
  font-family: 'Noto Serif TC', serif;
  font-size: 0.82rem;
  font-weight: 500;
  color: #8A7E6E;
  letter-spacing: 0.18em;
  text-indent: 0;
  text-align: center;
  margin: 0.8em 0 0.2em;
  padding: 0.5em 0;
  border-top: 1px solid #DDD8CF;
  border-bottom: 1px solid #DDD8CF;
}
.sd-content-stage {
  font-family: 'Noto Serif TC', serif;
  font-size: 0.9rem;
  font-weight: 300;
  color: #A09280;
  letter-spacing: 0.06em;
  text-indent: 0;
  text-align: center;
  margin: 0;
  font-style: normal;
}
.sd-content-textarea { min-height: 50vh; }

/* ── Not found ────────────────────────────────────────────── */
.sd-notfound { min-height: 60vh; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 16px; font-size: 0.9rem; color: #9A9080; }
.sd-notfound a { color: #8A7E6E; text-decoration: none; }

/* ── Responsive ───────────────────────────────────────────── */
@media (max-width: 640px) {
  .sd-topbar { padding: 16px 20px; }
  .sd-header { padding: 40px 20px 36px; }
  .sd-section { padding: 32px 20px; }
  .sd-reading-hd { padding: 12px 16px; }
  .sd-reading-body { padding: 16px 16px 20px; }
}
</style>
