<template>
  <div class="sd-wrap">
    <div class="sdb-head">
      <div>
        <p class="sd-eyebrow">COMMAND · BARRACKS</p>
        <h1 class="sd-h sdb-title">營區指揮台</h1>
      </div>
      <div class="sdb-tabs">
        <button v-for="t in tabs" :key="t.k" class="sdb-tab" :class="{ 'sdb-tab--on': tab === t.k }" @click="tab = t.k">
          {{ t.label }}<span v-if="t.k === 'review' && pendingCount" class="sdb-tab-badge">{{ pendingCount }}</span>
        </button>
      </div>
    </div>

    <!-- 名冊 -->
    <section v-show="tab === 'roster'">
      <div v-if="loadingRoster" class="sdb-loading">整隊中…</div>
      <div v-else-if="!members.length" class="sd-panel sdb-empty">尚無兵員，切到「編成」新增第一名。</div>
      <div v-else class="sd-panel sdb-roster">
        <div class="sdb-row sdb-row--head">
          <span>軍階</span><span>代號 / 姓名</span><span>當前軍種</span><span>已破</span><span>XP</span><span>日記</span><span>最近回報</span>
        </div>
        <button v-for="m in members" :key="m.id" class="sdb-row" @click="openMember(m.id)">
          <span class="sdb-rank"><b>{{ m.rank.insignia }}</b>{{ m.rank.name }}</span>
          <span>
            <b class="sdb-cs">{{ m.callsign }}</b><span class="sdb-nm">{{ m.name }}</span>
            <span v-if="m.status === 'discharged'" class="sdb-discharged">退伍</span>
          </span>
          <span class="sdb-branch">
            <template v-if="m.graduated"><b class="sdb-grad">👑 結訓</b></template>
            <template v-else-if="m.currentBranch">{{ m.currentBranch.name }}<em>{{ qName(m.currentBranch.quality) }}</em></template>
            <template v-else>—</template>
          </span>
          <span class="sdb-conq">{{ m.conqueredCount }}/5</span>
          <span class="sdb-xp">{{ m.xp }}</span>
          <span>{{ m.logCount }}<span v-if="m.pendingCount" class="sdb-pending">{{ m.pendingCount }}待閱</span></span>
          <span class="sdb-last">{{ m.lastReport || '—' }}</span>
        </button>
      </div>
    </section>

    <!-- 待批閱 -->
    <section v-show="tab === 'review'">
      <div v-if="loadingReview" class="sdb-loading">載入中…</div>
      <div v-else-if="!pendingLogs.length" class="sd-panel sdb-empty">目前沒有待批閱的日記。</div>
      <div v-else class="sdb-review-list">
        <div v-for="l in pendingLogs" :key="l.id" class="sd-panel sdb-review">
          <div class="sdb-review-top">
            <b class="sdb-cs">{{ l.memberCallsign }}</b><span class="sdb-nm">{{ l.memberName }}</span>
            <span v-if="branchMap[l.type]" class="sdb-branch-tag" :style="{ color: branchMap[l.type].color }">{{ branchMap[l.type].name }}</span>
            <span class="sdb-review-date">{{ l.logDate }}</span>
            <span class="sdb-review-xp">+{{ l.xpAwarded }} XP</span>
            <span class="sdb-log-self">自評 {{ '★'.repeat(l.selfScore || 0) }}</span>
          </div>
          <div class="sdb-review-body">
            <span v-for="k in (l.payload?.trainingItems || [])" :key="k" class="sdd-log-tag">{{ itemName(k) }}</span>
            <span v-if="l.payload?.durationMin" class="sdb-dur">{{ l.payload.durationMin }}分</span>
          </div>
          <p v-if="l.payload?.note" class="sdb-review-note">「{{ l.payload.note }}」</p>
          <div class="sdb-review-actions">
            <div class="sdb-stars">
              <button v-for="n in 5" :key="n" type="button" class="sdd-star" :class="{ 'sdd-star--on': (reviewDraft[l.id]?.score || 0) >= n }" @click="setScore(l.id, n)">★</button>
            </div>
            <input v-model="reviewDraft[l.id].note" class="sd-input sdb-review-input" placeholder="評語（選填）" />
            <input v-model.number="reviewDraft[l.id].xpDelta" type="number" class="sd-input sdb-xp-input" placeholder="±XP" />
            <button class="sd-btn sd-btn--sm" :disabled="reviewing === l.id" @click="doReview(l)">批閱</button>
          </div>
        </div>
      </div>
    </section>

    <!-- 編成 -->
    <section v-show="tab === 'enlist'" class="sdb-enlist-wrap">
      <div class="sd-panel sd-panel--raised sdb-enlist">
        <p class="sd-eyebrow">新增兵員</p>
        <p class="sd-sub sdb-enlist-sub">帳號由教官建立配發；兵員以「代號＋通行碼」登入，從陸軍開始一一突破。</p>
        <div class="sdb-form-row">
          <div class="sdb-field"><label class="sd-label">姓名</label><input v-model="nf.name" class="sd-input" placeholder="真實姓名" /></div>
          <div class="sdb-field"><label class="sd-label">代號</label><input v-model="nf.callsign" class="sd-input" placeholder="登入用代號（唯一）" /></div>
        </div>
        <div class="sdb-form-row">
          <div class="sdb-field"><label class="sd-label">通行碼</label><input v-model="nf.code" class="sd-input" placeholder="登入密碼" /></div>
          <div class="sdb-field"><label class="sd-label">小隊（選填）</label><input v-model="nf.squad" class="sd-input" placeholder="如：第一小隊" /></div>
        </div>
        <div class="sdb-field"><label class="sd-label">備註（選填）</label><input v-model="nf.note" class="sd-input" placeholder="教官備註" /></div>
        <p v-if="enlistMsg" class="sd-ok">{{ enlistMsg }}</p>
        <p v-if="enlistErr" class="sd-error">{{ enlistErr }}</p>
        <button class="sd-btn" :disabled="enlisting" @click="enlist">{{ enlisting ? '建立中…' : '完成編成' }}</button>
      </div>
    </section>

    <!-- 兵員詳情 -->
    <div v-if="detail" class="sdb-modal" @click.self="detail = null">
      <div class="sd-panel sd-panel--raised sdb-detail">
        <button class="sdb-close" @click="detail = null">✕</button>
        <div class="sdb-detail-head">
          <div class="sdd-rank-badge">{{ detail.member.rankInfo.rank.insignia }}</div>
          <div>
            <h2 class="sd-h sdb-detail-name">{{ detail.member.rankInfo.rank.name }}　{{ detail.member.name }}</h2>
            <p class="sdd-id-meta"><b class="sdb-cs">{{ detail.member.callsign }}</b><span class="sdd-name">{{ detail.member.xp }} XP</span></p>
          </div>
        </div>

        <!-- 軍種進度 -->
        <div class="sdb-detail-branches">
          <span v-for="b in detail.member.branches" :key="b.branch.key" class="sdb-br-chip"
                :class="{ 'sdb-br-chip--done': b.conquered, 'sdb-br-chip--active': b.active, 'sdb-br-chip--lock': b.locked }"
                :style="{ '--bc': b.branch.color }">
            {{ b.branch.name }} {{ b.quality }}
          </span>
        </div>

        <div class="sdb-detail-cols">
          <div class="sdb-detail-panel">
            <p class="sd-eyebrow">調整品質與獎懲</p>
            <div v-for="q in QUALITIES" :key="q.key" class="sdb-attr-edit">
              <span class="sdb-attr-lbl"><b :style="{ color: q.color }">{{ q.short }}</b>{{ q.name }}</span>
              <input v-model.number="editQ[q.key]" type="number" min="0" max="100" class="sd-input sdb-attr-num" />
            </div>
            <div class="sdb-detail-row">
              <div class="sdb-field"><label class="sd-label">XP 增減</label><input v-model.number="editXpDelta" type="number" class="sd-input" placeholder="±XP" /></div>
              <div class="sdb-field"><label class="sd-label">重設通行碼</label><input v-model="editCode" class="sd-input" placeholder="留空不改" /></div>
            </div>
            <div class="sdb-field"><label class="sd-label">小隊</label><input v-model="editSquad" class="sd-input" /></div>
            <div class="sdb-field"><label class="sd-label">備註</label><input v-model="editNote" class="sd-input" /></div>
            <div class="sdb-detail-actions">
              <button class="sd-btn sd-btn--sm" :disabled="savingMember" @click="saveMember">儲存變更</button>
              <button class="sd-btn sd-btn--sm sd-btn--ghost" @click="toggleDischarge">
                {{ detail.member.status === 'discharged' ? '復役' : '辦理退伍' }}
              </button>
            </div>
            <p v-if="detailMsg" class="sd-ok sdb-detail-msg">{{ detailMsg }}</p>
          </div>

          <div class="sdb-detail-panel">
            <p class="sd-eyebrow">日記紀錄（{{ detail.logs.length }} 篇）</p>
            <div class="sdb-detail-logs">
              <div v-for="l in detail.logs" :key="l.id" class="sdb-detail-log">
                <div class="sdd-log-top">
                  <span class="sdd-log-date">{{ l.log_date }}</span>
                  <span v-if="branchMap[l.type]" class="sdb-branch-tag" :style="{ color: branchMap[l.type].color }">{{ branchMap[l.type].name }}</span>
                  <span class="sdd-log-xp">+{{ l.xp_awarded }}</span>
                  <span v-if="l.status === 'reviewed'" class="sdd-log-reviewed">已閱</span>
                </div>
                <div class="sdd-log-body">
                  <span v-for="k in (l.payload?.trainingItems || [])" :key="k" class="sdd-log-tag">{{ itemName(k) }}</span>
                </div>
                <p v-if="l.payload?.note" class="sdd-log-note">「{{ l.payload.note }}」</p>
              </div>
              <p v-if="!detail.logs.length" class="sd-sub">尚無日記。</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useSoldierSession } from '~/composables/useSoldierSession'
import { QUALITIES, branchMap, trainingItemMap, qualityMap } from '~/data/soldierDiaryConfig'

definePageMeta({ layout: 'soldier-diary' })
useHead({ title: '營區指揮台 — 大兵日記' })

const { session, isChief, loadSession, authedFetch } = useSoldierSession()

const tab = ref<'roster' | 'review' | 'enlist'>('roster')
const tabs = [
  { k: 'roster' as const, label: '名冊' },
  { k: 'review' as const, label: '待批閱' },
  { k: 'enlist' as const, label: '編成' },
]

const members = ref<any[]>([])
const loadingRoster = ref(true)
const pendingLogs = ref<any[]>([])
const loadingReview = ref(false)
const pendingCount = computed(() => members.value.reduce((s, m) => s + (m.pendingCount || 0), 0))

const itemName = (k: string) => trainingItemMap[k]?.name || k
const qName = (k: string) => qualityMap[k as keyof typeof qualityMap]?.name || k

async function loadRoster() {
  loadingRoster.value = true
  try {
    const r: any = await authedFetch('/api/soldier-diary/members')
    members.value = r.members
  } finally { loadingRoster.value = false }
}

async function loadReview() {
  loadingReview.value = true
  try {
    const r: any = await authedFetch('/api/soldier-diary/pending-logs?status=submitted')
    pendingLogs.value = r.logs
    for (const l of r.logs) if (!reviewDraft[l.id]) reviewDraft[l.id] = { score: l.selfScore || 0, note: '', xpDelta: null }
  } finally { loadingReview.value = false }
}

const reviewDraft = reactive<Record<number, { score: number; note: string; xpDelta: number | null }>>({})
const reviewing = ref<number | null>(null)
const setScore = (id: number, n: number) => { reviewDraft[id].score = n }
async function doReview(l: any) {
  reviewing.value = l.id
  try {
    await authedFetch('/api/soldier-diary/log-review', {
      method: 'POST',
      body: { id: l.id, score: reviewDraft[l.id].score || undefined, note: reviewDraft[l.id].note || undefined, xpDelta: reviewDraft[l.id].xpDelta || undefined },
    })
    await Promise.all([loadReview(), loadRoster()])
  } finally { reviewing.value = null }
}

const nf = reactive({ name: '', callsign: '', code: '', squad: '', note: '' })
const enlisting = ref(false)
const enlistMsg = ref(''); const enlistErr = ref('')
async function enlist() {
  enlistMsg.value = ''; enlistErr.value = ''
  if (!nf.name.trim() || !nf.callsign.trim() || !nf.code.trim()) { enlistErr.value = '姓名、代號、通行碼皆必填'; return }
  enlisting.value = true
  try {
    await authedFetch('/api/soldier-diary/member-create', { method: 'POST', body: { ...nf } })
    enlistMsg.value = `已完成編成：${nf.callsign}（${nf.name}）`
    nf.name = ''; nf.callsign = ''; nf.code = ''; nf.squad = ''; nf.note = ''
    await loadRoster()
  } catch (e: any) {
    enlistErr.value = e?.data?.message || '建立失敗'
  } finally { enlisting.value = false }
}

const detail = ref<any>(null)
const editQ = reactive<Record<string, number>>({ obedience: 0, strength: 0, endurance: 0, composure: 0, challenge: 0 })
const editXpDelta = ref<number | null>(null)
const editCode = ref(''); const editSquad = ref(''); const editNote = ref('')
const savingMember = ref(false)
const detailMsg = ref('')

async function openMember(id: number) {
  detailMsg.value = ''
  const r: any = await authedFetch(`/api/soldier-diary/member?id=${id}`)
  detail.value = r
  for (const q of QUALITIES) editQ[q.key] = r.member.qualities[q.key]
  editXpDelta.value = null; editCode.value = ''
  editSquad.value = r.member.squad || ''; editNote.value = r.member.note || ''
}

async function saveMember() {
  if (!detail.value) return
  savingMember.value = true
  try {
    await authedFetch('/api/soldier-diary/member-update', {
      method: 'POST',
      body: {
        id: detail.value.member.id, qualities: { ...editQ },
        xpDelta: editXpDelta.value || undefined, code: editCode.value || undefined,
        squad: editSquad.value, note: editNote.value,
      },
    })
    detailMsg.value = '已儲存。'
    await Promise.all([openMember(detail.value.member.id), loadRoster()])
  } finally { savingMember.value = false }
}

async function toggleDischarge() {
  if (!detail.value) return
  const next = detail.value.member.status === 'discharged' ? 'active' : 'discharged'
  await authedFetch('/api/soldier-diary/member-update', { method: 'POST', body: { id: detail.value.member.id, status: next } })
  await Promise.all([openMember(detail.value.member.id), loadRoster()])
}

onMounted(async () => {
  loadSession()
  if (!session.value) return navigateTo('/soldier-diary/login')
  if (!isChief.value) return navigateTo('/soldier-diary/diary')
  await Promise.all([loadRoster(), loadReview()])
})
</script>

<style scoped>
.sdb-head { display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; flex-wrap: wrap; margin-bottom: 18px; }
.sdb-title { font-size: 1.5rem; margin-top: 6px; }
.sdb-tabs { display: flex; gap: 6px; }
.sdb-tab { position: relative; padding: 8px 18px; background: #171a11; border: 1px solid var(--sd-line); border-radius: 3px; color: var(--sd-khaki); font-size: 0.84rem; font-weight: 700; letter-spacing: 0.06em; cursor: pointer; }
.sdb-tab--on { background: var(--sd-olive); color: #12140d; border-color: var(--sd-olive-bright); }
.sdb-tab-badge { position: absolute; top: -7px; right: -7px; background: var(--sd-red); color: #fff; font-size: 0.64rem; padding: 1px 6px; border-radius: 8px; }

.sdb-loading, .sdb-empty { text-align: center; color: var(--sd-muted); padding: 40px; letter-spacing: 0.08em; }
.sdb-empty { padding: 32px; }

.sdb-roster { overflow-x: auto; }
.sdb-row { display: grid; grid-template-columns: 118px 1.4fr 1.2fr 56px 60px 88px 100px; align-items: center; gap: 10px; width: 100%; padding: 11px 16px; border: none; background: none; border-bottom: 1px solid var(--sd-line); color: var(--sd-khaki); font-size: 0.82rem; text-align: left; cursor: pointer; }
.sdb-row--head { color: var(--sd-muted); font-size: 0.68rem; letter-spacing: 0.1em; text-transform: uppercase; cursor: default; background: #171a11; }
button.sdb-row:hover:not(.sdb-row--head) { background: rgba(122,139,63,0.08); }
.sdb-rank b { color: var(--sd-brass); margin-right: 6px; }
.sdb-cs { color: var(--sd-olive-bright); font-weight: 700; margin-right: 8px; }
.sdb-nm { color: var(--sd-khaki); }
.sdb-discharged { color: var(--sd-red); font-size: 0.68rem; border: 1px solid var(--sd-red); padding: 0 5px; border-radius: 2px; margin-left: 6px; }
.sdb-branch em { color: var(--sd-muted); font-style: normal; font-size: 0.72rem; margin-left: 6px; }
.sdb-grad { color: var(--sd-brass); }
.sdb-conq { color: var(--sd-khaki); font-variant-numeric: tabular-nums; }
.sdb-xp { color: var(--sd-sand); font-weight: 700; }
.sdb-pending { color: var(--sd-red); font-size: 0.68rem; margin-left: 6px; }
.sdb-last { color: var(--sd-muted); font-size: 0.76rem; }

.sdb-review-list { display: flex; flex-direction: column; gap: 12px; }
.sdb-review { padding: 16px 18px; }
.sdb-review-top { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
.sdb-branch-tag { font-size: 0.74rem; font-weight: 700; }
.sdb-review-date { color: var(--sd-muted); font-size: 0.8rem; }
.sdb-review-xp { color: var(--sd-brass); font-size: 0.8rem; }
.sdb-log-self { color: var(--sd-muted); font-size: 0.78rem; }
.sdb-review-body { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 8px; }
.sdd-log-tag { font-size: 0.72rem; color: var(--sd-khaki); background: #171a11; border: 1px solid var(--sd-line); padding: 1px 7px; border-radius: 2px; }
.sdb-dur { color: var(--sd-muted); font-size: 0.72rem; }
.sdb-review-note { color: var(--sd-khaki); font-style: italic; font-size: 0.84rem; margin: 8px 0; }
.sdb-review-actions { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin-top: 8px; }
.sdb-stars { display: flex; gap: 2px; }
.sdd-star { background: none; border: none; cursor: pointer; font-size: 1.2rem; color: #3a4128; padding: 0; }
.sdd-star--on { color: var(--sd-brass); }
.sdb-review-input { flex: 1; min-width: 160px; }
.sdb-xp-input { width: 80px; }

.sdb-enlist-wrap { display: flex; justify-content: center; }
.sdb-enlist { width: 100%; max-width: 560px; padding: 24px 26px; }
.sdb-enlist-sub { margin: 4px 0 16px; }
.sdb-form-row { display: flex; gap: 14px; }
.sdb-field { flex: 1; margin-bottom: 12px; }
.sdb-enlist .sd-btn { margin-top: 6px; }

.sdb-modal { position: fixed; inset: 0; background: rgba(0,0,0,0.7); display: flex; align-items: flex-start; justify-content: center; padding: 40px 16px; z-index: 60; overflow-y: auto; }
.sdb-detail { width: 100%; max-width: 820px; padding: 26px 28px; position: relative; }
.sdb-close { position: absolute; top: 14px; right: 16px; background: none; border: none; color: var(--sd-muted); font-size: 1rem; cursor: pointer; }
.sdb-close:hover { color: var(--sd-red); }
.sdb-detail-head { display: flex; gap: 14px; align-items: center; margin-bottom: 16px; }
.sdd-rank-badge { width: 52px; height: 52px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; border: 2px solid var(--sd-brass); border-radius: 4px; color: var(--sd-brass); font-size: 1.1rem; font-weight: 700; background: rgba(203,164,58,0.08); }
.sdb-detail-name { font-size: 1.2rem; margin: 0 0 4px; }
.sdd-id-meta { display: flex; gap: 10px; align-items: center; margin: 0; }
.sdd-name { color: var(--sd-khaki); font-size: 0.84rem; }
.sdb-detail-branches { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 18px; }
.sdb-br-chip { font-size: 0.72rem; padding: 3px 9px; border-radius: 2px; border: 1px solid var(--sd-line); color: var(--sd-muted); background: #171a11; }
.sdb-br-chip--done { border-color: var(--bc); color: var(--bc); }
.sdb-br-chip--active { border-color: var(--sd-brass); color: var(--sd-brass); font-weight: 700; }
.sdb-br-chip--lock { opacity: 0.4; }
.sdb-detail-cols { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.sdb-attr-edit { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin: 8px 0; }
.sdb-attr-lbl { font-size: 0.82rem; color: var(--sd-khaki); }
.sdb-attr-lbl b { display: inline-block; width: 18px; font-weight: 900; }
.sdb-attr-num { width: 84px; }
.sdb-detail-row { display: flex; gap: 12px; margin-top: 8px; }
.sdb-detail-actions { display: flex; gap: 8px; margin-top: 12px; flex-wrap: wrap; }
.sdb-detail-msg { margin-top: 10px; }
.sdb-detail-logs { max-height: 360px; overflow-y: auto; }
.sdb-detail-log { padding: 9px 0; border-bottom: 1px solid var(--sd-line); }
.sdd-log-top { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
.sdd-log-date { font-weight: 700; color: var(--sd-sand); font-size: 0.82rem; }
.sdd-log-xp { color: var(--sd-brass); font-size: 0.78rem; }
.sdd-log-reviewed { color: var(--sd-olive-bright); font-size: 0.68rem; border: 1px solid var(--sd-olive); padding: 0 5px; border-radius: 2px; }
.sdd-log-body { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 5px; }
.sdd-log-note { color: var(--sd-khaki); font-size: 0.8rem; font-style: italic; margin: 5px 0 0; }

@media (max-width: 720px) {
  .sdb-detail-cols { grid-template-columns: 1fr; }
  .sdb-form-row { flex-direction: column; gap: 0; }
  .sdb-row { grid-template-columns: 100px 1.3fr 1fr 50px; }
  .sdb-row > span:nth-child(5), .sdb-row > span:nth-child(6), .sdb-row > span:nth-child(7) { display: none; }
}
</style>
