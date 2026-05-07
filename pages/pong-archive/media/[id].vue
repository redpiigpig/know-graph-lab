<template>
  <div v-if="item" class="md-page" :class="{ 'md-page--editing': isEditing }">

    <!-- ── Topbar ──────────────────────────────────────────── -->
    <div class="md-topbar">
      <NuxtLink to="/pong-archive/media" class="md-back">← 返回訪談與演講</NuxtLink>
    </div>

    <!-- ── Header ──────────────────────────────────────────── -->
    <header class="md-header">
      <div class="md-header-inner">

        <!-- 來源 / 節目名稱 row -->
        <div class="md-eyebrow-row">
          <template v-if="isEditing">
            <input v-model="local.source"       class="md-badge md-badge--source md-input" placeholder="來源機構" @input="save('source', local.source)" />
            <input v-model="local.source_en"    class="md-badge-en md-input" placeholder="Source EN" @input="save('source_en', local.source_en)" />
            <input v-model="local.program_name" class="md-program md-input" placeholder="節目名稱" @input="save('program_name', local.program_name)" />
            <input v-model="local.program_en"   class="md-program-en md-input" placeholder="Program EN" @input="save('program_en', local.program_en)" />
          </template>
          <template v-else>
            <span v-if="item.source"       class="md-badge md-badge--source">{{ item.source }}</span>
            <span v-if="item.source_en"    class="md-badge-en">{{ item.source_en }}</span>
            <span v-if="item.program_name" class="md-program">{{ item.program_name }}</span>
            <span v-if="item.program_en"   class="md-program-en">{{ item.program_en }}</span>
          </template>
        </div>

        <!-- 標題 -->
        <textarea
          v-if="isEditing"
          v-model="local.title"
          class="md-title md-textarea"
          rows="1"
          placeholder="標題"
          @input="e => { autoResize(e.target); save('title', local.title) }"
          ref="titleRef"
        />
        <h1 v-else class="md-title">{{ item.title }}</h1>

        <!-- 英文標題 -->
        <input
          v-if="isEditing"
          v-model="local.title_en"
          class="md-title-en md-input"
          placeholder="Title in English"
          @input="save('title_en', local.title_en)"
        />
        <p v-else-if="item.title_en" class="md-title-en">{{ item.title_en }}</p>

        <!-- Metadata row -->
        <div class="md-meta-row">
          <div class="md-meta-item">
            <span class="md-meta-label">播出日期</span>
            <input v-if="isEditing" v-model="local.broadcast_date" type="date" class="md-meta-value md-input md-input--date" @change="save('broadcast_date', local.broadcast_date)" />
            <span v-else class="md-meta-value">{{ item.broadcast_date ? formatDate(item.broadcast_date) : '—' }}</span>
          </div>
          <div class="md-meta-item">
            <span class="md-meta-label">主持人</span>
            <input v-if="isEditing" v-model="local.interviewer" class="md-meta-value md-input" placeholder="主持人" @input="save('interviewer', local.interviewer)" />
            <span v-else class="md-meta-value">{{ item.interviewer || '—' }}</span>
          </div>
          <div class="md-meta-item">
            <span class="md-meta-label">類型</span>
            <select v-if="isEditing" v-model="local.media_type" class="md-meta-value md-input md-input--select" @change="save('media_type', local.media_type)">
              <option value="interview">影音訪談</option>
              <option value="talk">演講</option>
              <option value="sermon_audio">講道錄音</option>
              <option value="documentary">紀錄片</option>
            </select>
            <span v-else class="md-meta-value">{{ mediaTypeLabel(item.media_type) }}</span>
          </div>
          <div class="md-meta-item">
            <span class="md-meta-label">YouTube ID</span>
            <input v-if="isEditing" v-model="local.youtube_id" class="md-meta-value md-input md-input--mono" placeholder="影片 ID" @input="save('youtube_id', local.youtube_id)" />
            <span v-else class="md-meta-value md-meta-value--mono">{{ item.youtube_id || '—' }}</span>
          </div>
        </div>

        <!-- 簡介 -->
        <textarea
          v-if="isEditing"
          v-model="local.description"
          class="md-description md-textarea"
          rows="3"
          placeholder="節目簡介…"
          @input="e => { autoResize(e.target); save('description', local.description) }"
        />
        <p v-else-if="item.description" class="md-description">{{ item.description }}</p>

        <!-- 編輯模式提示 -->
        <div v-if="isEditing" class="md-edit-hint">
          ✦ 編輯模式：點擊欄位直接修改，自動儲存至資料庫
        </div>
      </div>
    </header>

    <!-- ── Talk Image (no YouTube) ──────────────────────────── -->
    <section v-if="!youtubeId && item.thumbnail_url" class="md-image-section">
      <div class="md-image-inner">
        <img :src="item.thumbnail_url" :alt="item.title" class="md-talk-image" />
      </div>
    </section>

    <!-- ── YouTube Player ───────────────────────────────────── -->
    <section v-if="youtubeId" class="md-player-section">
      <div class="md-player-inner">
        <!-- 短影音：豎版 9:16 -->
        <div v-if="isShort" class="md-player-wrap md-player-wrap--short">
          <!-- facade：有自訂封面時，先顯示圖片，點擊才載入 YouTube -->
          <div
            v-if="!videoPlaying && item.thumbnail_url"
            class="md-short-facade"
            @click="videoPlaying = true"
          >
            <img :src="item.thumbnail_url" :alt="item.title" />
            <div class="md-facade-play">
              <svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
                <circle cx="40" cy="40" r="40" fill="rgba(0,0,0,0.52)"/>
                <polygon points="32,24 62,40 32,56" fill="white"/>
              </svg>
            </div>
          </div>
          <iframe
            v-else
            :src="videoPlaying ? youtubePlaySrc : youtubeEmbedSrc"
            title="YouTube Shorts player"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            allowfullscreen
          ></iframe>
        </div>
        <!-- 一般影片：橫版 16:9 -->
        <div v-else class="md-player-wrap">
          <iframe
            :src="youtubeEmbedSrc"
            title="YouTube video player"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            allowfullscreen
            loading="lazy"
          ></iframe>
        </div>
        <div class="md-yt-link">
          <a :href="item.url" target="_blank" rel="noopener noreferrer" class="md-yt-ext">
            在 YouTube 開啟 ↗
          </a>
        </div>
      </div>
    </section>

    <!-- ── Transcript ───────────────────────────────────────── -->
    <section class="md-transcript-section">
      <div class="md-transcript-inner">
        <div class="md-transcript-header">
          <h2 class="md-transcript-title">逐字稿</h2>
          <p class="md-transcript-note">以下為節目逐字稿，依原始語音紀錄整理，保留口語。</p>
        </div>

        <!-- 編輯模式：純文字編輯 textarea -->
        <textarea
          v-if="isEditing"
          v-model="local.transcript"
          class="md-transcript-raw"
          placeholder="逐字稿（格式：每行「講者：內容」，以空白行分段）"
          @input="save('transcript', local.transcript)"
        />

        <!-- 閱覽模式：格式化顯示 -->
        <div v-else class="md-transcript-body">
          <template v-for="(seg, i) in parsedTranscript" :key="i">
            <div v-if="seg.type === 'section'" class="md-ts-section">{{ seg.text }}</div>
            <div v-else-if="seg.type === 'speech'" class="md-ts-speech" :class="speakerClass(seg.speaker)">
              <div class="md-ts-speaker">{{ seg.speaker }}</div>
              <div class="md-ts-content">
                <p v-for="(para, j) in seg.paragraphs" :key="j">{{ para }}</p>
              </div>
            </div>
            <div v-else-if="seg.type === 'block'" class="md-ts-block">
              <p v-for="(para, j) in seg.paras" :key="j">{{ para }}</p>
            </div>
          </template>
        </div>
      </div>
    </section>

    <!-- ── Proofreader Sign-off ─────────────────────────────── -->
    <section v-if="isLoggedIn" class="md-pr-section">
      <div class="md-pr-inner">
        <div class="md-pr-hd">
          <h3 class="md-pr-title">校對簽名</h3>
          <p v-if="item.proofread_by" class="md-pr-status">
            <span class="md-pr-badge">已校對</span>
            上次由 <strong>{{ item.proofread_by }}</strong> 於 {{ formatDate(item.proofread_date) }} 簽署
            <span v-if="item.proofread_note"> · {{ item.proofread_note }}</span>
          </p>
        </div>

        <div class="md-pr-form">
          <div class="md-pr-row">
            <div class="md-pr-field">
              <label class="md-pr-label">校對者簽名</label>
              <input v-model="proofreadForm.name" class="md-pr-input" placeholder="輸入姓名以簽署" />
            </div>
            <div class="md-pr-field">
              <label class="md-pr-label">校對日期</label>
              <input v-model="proofreadForm.date" type="date" class="md-pr-input" />
            </div>
          </div>
          <div class="md-pr-field">
            <label class="md-pr-label">備註（選填）</label>
            <input v-model="proofreadForm.note" class="md-pr-input" placeholder="如有修正說明請填寫…" />
          </div>
          <div class="md-pr-footer">
            <button
              class="md-pr-btn"
              @click="submitProofread"
              :disabled="proofreadSaving || !proofreadForm.name || !proofreadForm.date"
            >
              <span v-if="proofreadSaving" class="md-pr-spin" />
              {{ proofreadSaving ? '儲存中…' : proofreadDone ? '✓ 已更新' : '提交簽名' }}
            </button>
            <span class="md-pr-hint">簽名後將覆蓋此記錄</span>
          </div>
        </div>
      </div>
    </section>

  </div>

  <div v-else class="md-notfound">
    <p>找不到此筆資料。</p>
    <NuxtLink to="/pong-archive/media">← 返回</NuxtLink>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick, onMounted } from 'vue'
import { createClient } from '@supabase/supabase-js'
import { usePongEditor } from '~/composables/usePongEditor'
import { usePongSession } from '~/composables/usePongSession'

definePageMeta({ layout: 'pong-archive' })

const route = useRoute()
const { isEditing, saveField } = usePongEditor()
const { session, isLoggedIn, loadSession } = usePongSession()

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_KEY,
)

const { data: item } = await useAsyncData(`pong-media-${route.params.id}`, async () => {
  const { data, error } = await supabase
    .from('pong_media').select('*')
    .eq('id', route.params.id).eq('is_published', true).single()
  return error ? null : data
})

// ── Local editable copy ──────────────────────────────────────
const local = reactive({})
watch(item, (v) => { if (v) Object.assign(local, v) }, { immediate: true })
watch(isEditing, async (on) => {
  if (!on) return
  const { data } = await supabase.from('pong_media').select('*').eq('id', route.params.id).single()
  if (data) Object.assign(local, data)
})

const titleRef = ref(null)
watch(isEditing, async (on) => {
  if (on) { await nextTick(); if (titleRef.value) autoResize(titleRef.value) }
})

const youtubeId = computed(() => isEditing.value ? local.youtube_id : item.value?.youtube_id)
const isShort = computed(() => (isEditing.value ? local.media_type : item.value?.media_type) === 'short')
const youtubeEmbedSrc = computed(() => {
  const id = youtubeId.value
  if (!id) return null
  if (isShort.value) return `https://www.youtube.com/embed/${id}`
  const start = item.value?.youtube_start
  return `https://www.youtube.com/embed/${id}${start ? `?start=${start}` : ''}`
})

const videoPlaying = ref(false)
watch(() => item.value?.id, () => { videoPlaying.value = false })
const youtubePlaySrc = computed(() => {
  const src = youtubeEmbedSrc.value
  if (!src) return null
  return src + (src.includes('?') ? '&' : '?') + 'autoplay=1'
})

function save(field, value) {
  saveField('pong_media', item.value?.id, field, value)
}

function autoResize(el) {
  el.style.height = 'auto'
  el.style.height = el.scrollHeight + 'px'
}

// ── Transcript parser ────────────────────────────────────────
// Recognised speaker-name suffixes — used to gate speaker detection
// inside a running speech block (so "他告訴我：..." won't be misread).
const SPEAKER_SUFFIX = /(?:牧師|牧正|主席|主持人?|教授|長老|傳道人?|博士|執事|姊妹|弟兄|會友|主教|會督|師母|院長|司會|司琴|敬拜|傳道|同工|傳道師|老師)$/
// Function words that real Chinese names never contain — used to reject
// false-positive "speaker" lines like "這裡有個問題：xxx".
// 會 is intentionally excluded (legit names like 「龐君華會督」 contain it).
const FORBIDDEN_NAME_CHARS = /[這那有是了的就我你他她它把被很都也還已經要沒]/

const parsedTranscript = computed(() => {
  const text = item.value?.transcript
  if (!text) return []
  const lines = text.split('\n')
  const segments = []
  const knownSpeakers = new Set()
  let curSpeaker = null
  let pendingSpeaker = null   // speaker declared but no content yet (e.g. lone "龐牧師：" line)
  let curParas = []
  let blockParas = []
  let paraBuf = []

  // Pre-pass: scan the whole transcript and pre-register any name that
  // would already be accepted under the lenient block-mode rules
  // (suffix match, English, or short ≤6 chars without forbidden chars).
  // This way a name that first appears INSIDE another speaker's block
  // (like 「林立峯牧正：…」 mid-speech) is still recognised.
  for (const rawLine of lines) {
    const l = rawLine.trim()
    if (!l || /^【.+】$/.test(l)) continue
    const m = l.match(/^(.{1,12}?)(?:（[^）]*）)?\s*：\s*(.+)$/)
    if (!m) continue
    const candidate = m[1].trim()
    if (!candidate) continue
    if (!/^[一-龥A-Za-z·\s]+$/.test(candidate)) continue
    if (/[，。？！、；]/.test(candidate)) continue
    if (FORBIDDEN_NAME_CHARS.test(candidate)) continue
    const passes = SPEAKER_SUFFIX.test(candidate)
                || /^[A-Za-z][A-Za-z\s]*$/.test(candidate)
                || candidate.length <= 6
    if (passes) knownSpeakers.add(candidate)
  }

  const flushSpeech = () => {
    if (curSpeaker !== null && curParas.length)
      segments.push({ type: 'speech', speaker: curSpeaker, paragraphs: [...curParas] })
    curSpeaker = null; curParas = []
  }
  const flushPara = () => {
    if (paraBuf.length) { blockParas.push(paraBuf.join('')); paraBuf = [] }
  }
  const flushBlock = () => {
    flushPara()
    if (blockParas.length) {
      segments.push({ type: 'block', paras: [...blockParas] })
      blockParas = []
    }
  }

  // Returns { name, role, content } or null. role is the (xxx) suffix if present.
  const parseSpeakerLine = (line) => {
    const m = line.match(/^(.{1,12}?)(?:（([^）]*)）)?\s*：\s*(.*)$/)
    if (!m) return null
    const name = m[1].trim()
    if (!name) return null
    if (!/^[一-龥A-Za-z·\s]+$/.test(name)) return null
    if (/[，。？！、；]/.test(name)) return null
    if (FORBIDDEN_NAME_CHARS.test(name)) return null
    return { name, role: (m[2] || '').trim(), content: m[3].trim() }
  }

  // Whether this name is "definitely" a speaker (vs e.g. "結論：xxx").
  const looksLikeName = (name) =>
    knownSpeakers.has(name) || SPEAKER_SUFFIX.test(name) || /^[A-Za-z][A-Za-z\s]*$/.test(name)

  for (const line of lines) {
    const l = line.trim()

    // blank line
    if (!l) {
      if (curSpeaker === null) flushPara()
      continue
    }

    // section header 【xxx】
    if (/^【.+】$/.test(l)) {
      flushBlock(); flushSpeech()
      pendingSpeaker = null
      segments.push({ type: 'section', text: l.replace(/^【|】$/g, '') })
      continue
    }

    // Try to detect a speaker line.
    const sp = parseSpeakerLine(l)
    const acceptHere = sp && (
      curSpeaker === null
        // In block / fresh mode: accept if name looks reasonable
        ? (looksLikeName(sp.name) || sp.name.length <= 6)
        // In speech mode: only accept strong matches (avoids false positives)
        : looksLikeName(sp.name)
    )

    if (acceptHere) {
      flushBlock(); flushSpeech()
      knownSpeakers.add(sp.name)
      const display = sp.role ? `${sp.name}（${sp.role}）` : sp.name
      curSpeaker = display
      if (sp.content) {
        curParas.push(sp.content)
        pendingSpeaker = null
      } else {
        // Lone "龐牧師：" line — remember for the next non-section content.
        pendingSpeaker = display
        curSpeaker = null
      }
      continue
    }

    // pending speaker waiting → start a fresh speech block with this line
    if (pendingSpeaker !== null && curSpeaker === null) {
      flushBlock()
      curSpeaker = pendingSpeaker
      pendingSpeaker = null
      curParas.push(l)
      continue
    }

    // running speech: add to current speaker
    if (curSpeaker !== null) { curParas.push(l); continue }

    // plain narrative → block paragraph buffer
    paraBuf.push(l)
  }
  flushBlock(); flushSpeech()
  return segments
})

function speakerClass(name) {
  if (!name) return ''
  if (name.includes('龐') || name.includes('Bishop') || name.includes('Pong')) return 'md-ts-speech--bishop'
  return 'md-ts-speech--host'
}

function formatDate(d) {
  if (!d) return '—'
  const dt = new Date(d)
  return `${dt.getFullYear()} 年 ${dt.getMonth() + 1} 月 ${dt.getDate()} 日`
}

function mediaTypeLabel(t) {
  return { interview: '影音訪談', talk: '演講', sermon_audio: '講道錄音', documentary: '紀錄片' }[t] || t
}

// ── Proofreader sign-off ─────────────────────────────────────
const proofreadForm = reactive({
  name: '',
  date: new Date().toISOString().split('T')[0],
  note: '',
})

watch(
  [session, item],
  ([s, it]) => {
    if (it?.proofread_by) {
      proofreadForm.name = it.proofread_by
      if (it.proofread_date) proofreadForm.date = it.proofread_date
      proofreadForm.note = it.proofread_note || ''
    } else if (s?.name && !proofreadForm.name) {
      proofreadForm.name = s.name
    }
  },
  { immediate: true },
)

const proofreadSaving = ref(false)
const proofreadDone   = ref(false)

async function submitProofread() {
  if (!proofreadForm.name || !proofreadForm.date) return
  proofreadSaving.value = true
  try {
    await $fetch('/api/pong-save', {
      method: 'POST',
      body: {
        table: 'pong_media',
        id: route.params.id,
        fields: {
          proofread_by: proofreadForm.name,
          proofread_date: proofreadForm.date,
          proofread_note: proofreadForm.note || null,
        },
      },
    })
    if (item.value) {
      item.value.proofread_by   = proofreadForm.name
      item.value.proofread_date = proofreadForm.date
      item.value.proofread_note = proofreadForm.note || null
    }
    proofreadDone.value = true
    setTimeout(() => { proofreadDone.value = false }, 3000)
  } catch (e) {
    console.error('[proofread]', e)
  } finally {
    proofreadSaving.value = false
  }
}

onMounted(() => { loadSession() })
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500&family=Noto+Serif+TC:wght@400;500;600&display=swap');

.md-page {
  background-color: #F9F8F6;
  min-height: 100vh;
  font-family: 'Noto Sans TC', sans-serif;
  color: #2C2C2C;
}

/* ── Topbar ─────────────────────────────────────────────── */
.md-topbar { padding: 20px 48px; border-bottom: 1px solid #DDD8CF; }
.md-back { font-size: 0.8rem; color: #8A8278; text-decoration: none; letter-spacing: 0.06em; transition: color 0.2s; }
.md-back:hover { color: #3A3025; }

/* ── Header ─────────────────────────────────────────────── */
.md-header {
  background-color: #F4F1EC;
  border-bottom: 1px solid #E0DAD0;
  padding: 48px 40px 40px;
  transition: background-color 0.3s;
}
.md-page--editing .md-header { background-color: #EDE8DF; }
.md-header-inner { max-width: 800px; margin: 0 auto; }

.md-eyebrow-row { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin-bottom: 20px; }
.md-badge { font-size: 0.7rem; font-weight: 400; color: #fff; background-color: #7A6E5E; padding: 3px 10px; border-radius: 2px; letter-spacing: 0.06em; }
.md-badge-en, .md-program-en { font-size: 0.68rem; font-weight: 300; color: #9A9080; letter-spacing: 0.1em; }
.md-program { font-size: 0.72rem; font-weight: 300; color: #6A6058; letter-spacing: 0.06em; padding: 3px 10px; border: 1px solid #C4B89A; border-radius: 2px; }

.md-title {
  font-family: 'Noto Serif TC', serif;
  font-size: clamp(1.4rem, 3vw, 1.9rem);
  font-weight: 500;
  color: #2C2C2C;
  letter-spacing: 0.1em;
  line-height: 1.5;
  margin: 0 0 6px;
}
.md-title-en { font-size: 0.88rem; font-weight: 300; color: #8A8278; letter-spacing: 0.1em; margin: 0 0 24px; }

.md-meta-row { display: flex; flex-wrap: wrap; gap: 20px 32px; margin-bottom: 20px; padding: 18px 0; border-top: 1px solid #DDD8CF; border-bottom: 1px solid #DDD8CF; }
.md-meta-item { display: flex; flex-direction: column; gap: 3px; }
.md-meta-label { font-size: 0.65rem; font-weight: 300; color: #A09280; letter-spacing: 0.12em; text-transform: uppercase; }
.md-meta-value { font-size: 0.88rem; font-weight: 400; color: #3A3530; letter-spacing: 0.04em; }
.md-meta-value--mono { font-family: monospace; font-size: 0.82rem; }

.md-description { font-size: 0.9rem; font-weight: 300; color: #5A5550; line-height: 1.9; letter-spacing: 0.04em; margin: 0; }

/* ── Edit mode inputs ───────────────────────────────────── */
.md-input, .md-textarea {
  background: transparent;
  border: none;
  border-bottom: 1.5px dashed #C4B89A;
  border-radius: 0;
  outline: none;
  font-family: inherit;
  font-size: inherit;
  font-weight: inherit;
  color: inherit;
  letter-spacing: inherit;
  line-height: inherit;
  padding: 2px 0;
  width: 100%;
  resize: none;
  transition: border-color 0.2s, background-color 0.15s;
  -webkit-appearance: none;
}
.md-input:focus, .md-textarea:focus {
  border-bottom-color: #8A7E6E;
  background-color: rgba(196,184,154,0.07);
  border-radius: 2px;
}
.md-textarea { overflow: hidden; }
.md-input--date { cursor: pointer; }
.md-input--select { cursor: pointer; appearance: auto; }
.md-input--mono { font-family: monospace; font-size: 0.82rem; }

.md-badge.md-input {
  color: #fff;
  background-color: #7A6E5E;
  border-bottom: none;
  border: 1.5px dashed rgba(255,255,255,0.5);
  padding: 3px 10px;
  border-radius: 2px;
  width: auto;
}
.md-badge.md-input:focus { background-color: #5A5048; border-color: #fff; }
.md-program.md-input { border: 1.5px dashed #C4B89A; width: auto; padding: 3px 10px; }

.md-edit-hint { margin-top: 16px; font-size: 0.7rem; font-weight: 300; color: #A09280; letter-spacing: 0.06em; }

/* ── Talk Image ─────────────────────────────────────────── */
.md-image-section { padding: 48px 40px; background-color: #F9F8F6; border-bottom: 1px solid #E8E4DC; }
.md-image-inner { max-width: 800px; margin: 0 auto; }
.md-talk-image {
  display: block;
  max-width: 100%;
  max-height: 560px;
  margin: 0 auto;
  border-radius: 4px;
  box-shadow: 0 8px 32px rgba(40,30,20,0.14);
  object-fit: contain;
}

/* ── Player ─────────────────────────────────────────────── */
.md-player-section { padding: 48px 40px; background-color: #F9F8F6; border-bottom: 1px solid #E8E4DC; }
.md-player-inner { max-width: 800px; margin: 0 auto; }
.md-player-wrap {
  position: relative; width: 100%; padding-top: 56.25%;
  border-radius: 4px; overflow: hidden; background-color: #000;
  box-shadow: 0 8px 32px rgba(40,30,20,0.18);
}
.md-player-wrap--short {
  max-width: 360px;
  padding-top: calc(360px * 16 / 9);
  margin: 0 auto;
}
.md-player-wrap iframe { position: absolute; inset: 0; width: 100%; height: 100%; border: none; }

.md-short-facade {
  position: absolute;
  inset: 0;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.md-short-facade img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.md-facade-play {
  position: relative;
  z-index: 1;
  width: 72px;
  height: 72px;
  transition: transform 0.15s;
  filter: drop-shadow(0 2px 8px rgba(0,0,0,0.4));
}
.md-short-facade:hover .md-facade-play { transform: scale(1.12); }
.md-yt-link { margin-top: 12px; text-align: right; }
.md-yt-ext { font-size: 0.75rem; font-weight: 300; color: #9A9080; text-decoration: none; letter-spacing: 0.06em; transition: color 0.2s; }
.md-yt-ext:hover { color: #5A5040; }

/* ── Transcript ─────────────────────────────────────────── */
.md-transcript-section { padding: 56px 40px 80px; }
.md-transcript-inner { max-width: 800px; margin: 0 auto; }
.md-transcript-header { margin-bottom: 40px; padding-bottom: 20px; border-bottom: 2px solid #C4B89A; }
.md-transcript-title { font-family: 'Noto Serif TC', serif; font-size: 1.2rem; font-weight: 500; color: #3A3025; letter-spacing: 0.1em; margin: 0 0 8px; }
.md-transcript-note { font-size: 0.78rem; font-weight: 300; color: #A09280; letter-spacing: 0.04em; margin: 0; }

.md-transcript-raw {
  width: 100%;
  min-height: 60vh;
  background-color: #FDFCFA;
  border: 1.5px dashed #C4B89A;
  border-radius: 4px;
  padding: 20px;
  font-family: 'Noto Sans TC', monospace;
  font-size: 0.88rem;
  font-weight: 300;
  color: #3A3530;
  line-height: 2;
  letter-spacing: 0.04em;
  resize: vertical;
  outline: none;
  transition: border-color 0.2s;
}
.md-transcript-raw:focus { border-color: #8A7E6E; }

.md-transcript-body { display: flex; flex-direction: column; }
.md-ts-section {
  font-family: 'Noto Serif TC', serif;
  font-size: 0.9rem; font-weight: 500; color: #8A7E6E;
  letter-spacing: 0.12em; text-align: center;
  padding: 28px 0 20px; position: relative;
}
.md-ts-section::before, .md-ts-section::after { content: '—'; margin: 0 12px; color: #C4B89A; }

/* 發言人凸排：標籤獨立一行在內容上方，內容保留原本的 2rem 首行縮排 */
.md-ts-speech {
  padding: 18px 0 16px;
  border-bottom: 1px solid #EAE6DE;
}
.md-ts-speech:last-child { border-bottom: none; }
.md-ts-speaker {
  font-size: 0.82rem;
  font-weight: 500;
  letter-spacing: 0.08em;
  margin: 0 0 8px;
  line-height: 1.5;
}
.md-ts-speech--bishop .md-ts-speaker { color: #5B3F2A; }
.md-ts-speech--host .md-ts-speaker { color: #3A5A4A; }
.md-ts-content {
  font-size: 0.92rem;
  font-weight: 300;
  color: #3A3530;
  line-height: 2;
  letter-spacing: 0.04em;
}
/* 每段都要有 2rem 首行縮排（含換段後的後續段落） */
.md-ts-content p,
.md-ts-block p {
  text-indent: 2rem;
  margin: 0 0 0.6em;
}
.md-ts-content p:last-child,
.md-ts-block p:last-child { margin-bottom: 0; }

.md-ts-block {
  font-size: 0.92rem;
  font-weight: 300;
  color: #3A3530;
  line-height: 2;
  letter-spacing: 0.04em;
  padding: 18px 0 16px;
  border-bottom: 1px solid #EAE6DE;
}
.md-ts-block:last-child { border-bottom: none; }
/* 章節標題接在 hr 之後時，把多餘的線吃掉 */
.md-ts-speech:has(+ .md-ts-section),
.md-ts-block:has(+ .md-ts-section) { border-bottom: none; }

/* ── Proofreader Sign-off ────────────────────────────────── */
.md-pr-section {
  background-color: #F4F1EC;
  border-top: 1px solid #DDD8CF;
  padding: 40px 40px 48px;
}
.md-pr-inner { max-width: 800px; margin: 0 auto; }

.md-pr-hd {
  display: flex;
  align-items: baseline;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #DDD8CF;
}
.md-pr-title {
  font-family: 'Noto Serif TC', serif;
  font-size: 1rem;
  font-weight: 500;
  color: #3A3025;
  letter-spacing: 0.1em;
  margin: 0;
}
.md-pr-status {
  font-size: 0.78rem;
  font-weight: 300;
  color: #6A6460;
  letter-spacing: 0.04em;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.md-pr-badge {
  font-size: 0.62rem;
  background-color: rgba(74,122,90,0.12);
  color: #2A5A3A;
  border-radius: 10px;
  padding: 2px 8px;
  letter-spacing: 0.06em;
  white-space: nowrap;
}

.md-pr-form { display: flex; flex-direction: column; gap: 14px; }
.md-pr-row { display: flex; gap: 16px; flex-wrap: wrap; }
.md-pr-field { display: flex; flex-direction: column; gap: 5px; flex: 1; min-width: 160px; }

.md-pr-label {
  font-size: 0.62rem;
  font-weight: 300;
  color: #A09280;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.md-pr-input {
  background: #FDFCFA;
  border: 1px solid #C8BFB0;
  border-radius: 3px;
  padding: 8px 12px;
  font-family: 'Noto Sans TC', sans-serif;
  font-size: 0.85rem;
  font-weight: 300;
  color: #2C2C2C;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  width: 100%;
  box-sizing: border-box;
}
.md-pr-input:focus { border-color: #8A7E6E; box-shadow: 0 0 0 3px rgba(138,126,110,0.1); }

.md-pr-footer {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 4px;
}
.md-pr-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 22px;
  background-color: #5B3F2A;
  color: #fff;
  border: none;
  border-radius: 3px;
  font-family: 'Noto Sans TC', sans-serif;
  font-size: 0.8rem;
  font-weight: 400;
  letter-spacing: 0.1em;
  cursor: pointer;
  transition: background-color 0.2s;
  white-space: nowrap;
}
.md-pr-btn:hover:not(:disabled) { background-color: #4A3020; }
.md-pr-btn:disabled { opacity: 0.55; cursor: not-allowed; }

.md-pr-spin {
  width: 12px;
  height: 12px;
  border: 1.5px solid rgba(255,255,255,0.4);
  border-top-color: #fff;
  border-radius: 50%;
  animation: md-pr-spin 0.7s linear infinite;
  flex-shrink: 0;
}
@keyframes md-pr-spin { to { transform: rotate(360deg); } }

.md-pr-hint { font-size: 0.7rem; font-weight: 300; color: #A09280; letter-spacing: 0.06em; margin: 0; }

/* ── Not found ──────────────────────────────────────────── */
.md-notfound { min-height: 60vh; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 16px; font-size: 0.9rem; color: #9A9080; }
.md-notfound a { color: #8A7E6E; text-decoration: none; }

/* ── Responsive ─────────────────────────────────────────── */
@media (max-width: 640px) {
  .md-topbar { padding: 16px 20px; }
  .md-header { padding: 32px 20px 28px; }
  .md-player-section { padding: 28px 20px; }
  .md-transcript-section { padding: 36px 20px 60px; }
  .md-pr-section { padding: 32px 20px 40px; }
  .md-pr-row { flex-direction: column; }
}
</style>
