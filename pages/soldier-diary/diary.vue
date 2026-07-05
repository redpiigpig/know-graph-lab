<template>
  <div class="sd-wrap">
    <div v-if="loading" class="sdd-loading">整隊中…</div>

    <template v-else-if="member">
      <!-- 兵籍卡 -->
      <section class="sd-panel sd-panel--raised sdd-idcard">
        <div class="sdd-id-left">
          <div class="sdd-rank-badge">{{ member.rankInfo.rank.insignia }}</div>
          <div>
            <p class="sd-eyebrow">{{ member.rankInfo.rank.nameEn }}</p>
            <h1 class="sd-h sdd-rank-name">{{ member.rankInfo.rank.name }}</h1>
            <p class="sdd-id-meta">
              <span class="sdd-callsign">{{ member.callsign }}</span>
              <span class="sdd-name">{{ member.name }}</span>
              <span v-if="member.squad" class="sdd-squad">{{ member.squad }}</span>
            </p>
          </div>
        </div>
        <div class="sdd-id-right">
          <div class="sdd-xp-line"><span class="sdd-xp-num">{{ member.xp }}</span><span class="sdd-xp-unit">XP</span></div>
          <div class="sdd-xp-bar"><div class="sdd-xp-fill" :style="{ width: (member.rankInfo.progress * 100).toFixed(1) + '%' }" /></div>
          <p class="sdd-xp-next">
            <template v-if="member.rankInfo.next">距「{{ member.rankInfo.next.name }}」還需 {{ member.rankInfo.next.minXp - member.xp }} XP</template>
            <template v-else>已達最高軍階 上士 ❯❯❯</template>
          </p>
        </div>
      </section>

      <!-- 軍種突破進度 -->
      <section class="sd-panel sdd-block">
        <div class="sdd-branch-head">
          <p class="sd-eyebrow">五大軍種 · 一一突破</p>
          <span v-if="member.graduated" class="sdd-grad">👑 五軍結訓</span>
          <span v-else-if="activeBr" class="sdd-cur">當前：{{ activeBr.name }}（{{ qName(activeBr.quality) }}）</span>
        </div>
        <div class="sdd-branches">
          <div v-for="b in member.branches" :key="b.branch.key" class="sdd-branch"
               :class="{ 'sdd-branch--done': b.conquered, 'sdd-branch--active': b.active, 'sdd-branch--lock': b.locked }"
               :style="{ '--bc': b.branch.color }">
            <div class="sdd-branch-top">
              <span class="sdd-branch-name">{{ b.branch.name }}</span>
              <span class="sdd-branch-state">
                <template v-if="b.conquered">✓ 已突破</template>
                <template v-else-if="b.active">攻堅中</template>
                <template v-else>🔒</template>
              </span>
            </div>
            <div class="sdd-branch-q">{{ qName(b.branch.quality) }}</div>
            <div class="sdd-branch-bar"><div class="sdd-branch-fill" :style="{ width: (b.progress * 100) + '%' }" /></div>
            <div class="sdd-branch-val">{{ b.quality }}/100</div>
          </div>
        </div>
      </section>

      <!-- 狀態列 -->
      <section class="sdd-stats">
        <div class="sd-panel sdd-stat"><span class="sdd-stat-n">{{ stats.streak }}</span><span class="sdd-stat-l">連續回報天</span></div>
        <div class="sd-panel sdd-stat"><span class="sdd-stat-n">{{ stats.logCount }}</span><span class="sdd-stat-l">日記篇數</span></div>
        <div class="sd-panel sdd-stat"><span class="sdd-stat-n">{{ conqueredCount }}</span><span class="sdd-stat-l">已破軍種</span></div>
        <div class="sd-panel sdd-stat"><span class="sdd-stat-n">{{ earnedBadges.length }}</span><span class="sdd-stat-l">榮譽徽章</span></div>
      </section>

      <div class="sdd-cols">
        <!-- 左：品質 + 徽章 -->
        <div class="sdd-col">
          <section class="sd-panel sdd-block">
            <p class="sd-eyebrow">五大品質</p>
            <div v-for="q in QUALITIES" :key="q.key" class="sdd-attr">
              <span class="sdd-attr-name"><b :style="{ color: q.color }">{{ q.short }}</b>{{ q.name }}</span>
              <div class="sdd-attr-bar"><div class="sdd-attr-fill" :style="{ width: member.qualities[q.key] + '%', background: q.color }" /></div>
              <span class="sdd-attr-val">{{ member.qualities[q.key] }}</span>
            </div>
          </section>

          <section class="sd-panel sdd-block">
            <p class="sd-eyebrow">榮譽徽章</p>
            <div class="sdd-badges">
              <div v-for="b in badges" :key="b.key" class="sdd-badge" :class="{ 'sdd-badge--off': !b.earned }" :title="b.desc">
                <span class="sdd-badge-ic">{{ b.icon }}</span><span class="sdd-badge-nm">{{ b.name }}</span>
              </div>
            </div>
          </section>
        </div>

        <!-- 右：今日日記 -->
        <div class="sdd-col">
          <section class="sd-panel sd-panel--raised sdd-block">
            <div class="sdd-diary-head">
              <p class="sd-eyebrow">{{ todayLogged ? '今日日記（可修改）' : '今日日記' }}</p>
              <span class="sdd-date">{{ today }}</span>
            </div>

            <div class="sdd-focus" v-if="activeBr" :style="{ '--bc': activeBr.color }">
              當前軍種 <b>{{ activeBr.name }}</b>：{{ activeBr.motto }}
            </div>
            <div class="sdd-focus sdd-focus--grad" v-else>已五軍結訓，可自由操練任一項目維持狀態。</div>

            <label class="sd-label">{{ activeBr ? activeBr.name + ' 操練項目' : '操練項目' }}</label>
            <div class="sdd-checks">
              <label v-for="d in formItems" :key="d.key" class="sdd-check" :class="{ 'sdd-check--on': form.trainingItems.includes(d.key) }">
                <input type="checkbox" :value="d.key" v-model="form.trainingItems" />
                <span>{{ d.name }}</span>
              </label>
            </div>

            <div class="sdd-row">
              <div class="sdd-field">
                <label class="sd-label">操練時長（分）</label>
                <input v-model.number="form.durationMin" type="number" min="0" max="600" class="sd-input" />
              </div>
              <div class="sdd-field">
                <label class="sd-label">今日自評</label>
                <div class="sdd-stars">
                  <button v-for="n in 5" :key="n" type="button" class="sdd-star" :class="{ 'sdd-star--on': form.selfScore >= n }" @click="form.selfScore = n">★</button>
                </div>
              </div>
            </div>

            <label class="sd-label">每日紀律任務</label>
            <div class="sdd-checks">
              <label v-for="m in DAILY_MISSIONS" :key="m.key" class="sdd-check" :class="{ 'sdd-check--on': form.missions.includes(m.key) }">
                <input type="checkbox" :value="m.key" v-model="form.missions" />
                <span>{{ m.name }} <em>+{{ m.xp }}</em></span>
              </label>
            </div>

            <label class="sd-label">一句話心得</label>
            <textarea v-model="form.note" class="sd-textarea" rows="2" placeholder="今日訓練感想、遇到的困難、明日目標…" maxlength="500" />

            <div class="sdd-preview">
              <span>預計獲得</span>
              <b class="sdd-preview-xp">+{{ preview.xp }} XP</b>
              <span v-for="(v, k) in preview.qualityDelta" :key="k" class="sdd-preview-attr">{{ qName(k) }}+{{ v }}</span>
            </div>

            <p v-if="msg" class="sd-ok">{{ msg }}</p>
            <p v-if="err" class="sd-error">{{ err }}</p>

            <button class="sd-btn" :disabled="submitting || !canSubmit" @click="submit">
              {{ submitting ? '呈報中…' : (todayLogged ? '更新今日日記' : '呈報日記') }}
            </button>
          </section>
        </div>
      </div>

      <!-- 歷史日記 -->
      <section class="sd-panel sdd-block sdd-history">
        <p class="sd-eyebrow">日記紀錄</p>
        <p v-if="!logs.length" class="sd-sub">尚無日記，從今天開始記錄第一篇。</p>
        <div v-for="l in logs" :key="l.id" class="sdd-log">
          <div class="sdd-log-top">
            <span class="sdd-log-date">{{ l.log_date }}</span>
            <span v-if="branchMap[l.type]" class="sdd-log-branch" :style="{ color: branchMap[l.type].color }">{{ branchMap[l.type].name }}</span>
            <span class="sdd-log-xp">+{{ l.xp_awarded }} XP</span>
            <span class="sdd-log-self">自評 {{ '★'.repeat(l.self_score || 0) }}</span>
            <span v-if="l.status === 'reviewed'" class="sdd-log-reviewed">已批閱</span>
          </div>
          <div class="sdd-log-body">
            <span v-for="k in (l.payload?.trainingItems || [])" :key="k" class="sdd-log-tag">{{ itemName(k) }}</span>
            <span v-if="l.payload?.durationMin" class="sdd-log-dur">{{ l.payload.durationMin }}分</span>
          </div>
          <p v-if="l.payload?.note" class="sdd-log-note">「{{ l.payload.note }}」</p>
          <div v-if="l.officer_note || l.officer_score" class="sdd-log-officer">
            <span class="sdd-officer-tag">教官</span>
            <span v-if="l.officer_score">評分 {{ '★'.repeat(l.officer_score) }}</span>
            <span v-if="l.officer_note">{{ l.officer_note }}</span>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useSoldierSession } from '~/composables/useSoldierSession'
import {
  QUALITIES, BRANCHES, DAILY_MISSIONS, branchMap, trainingItemMap, qualityMap,
  computeLogRewards,
} from '~/data/soldierDiaryConfig'

definePageMeta({ layout: 'soldier-diary' })
useHead({ title: '我的日記 — 大兵日記' })

const { session, isChief, loadSession, authedFetch } = useSoldierSession()

const loading = ref(true)
const submitting = ref(false)
const member = ref<any>(null)
const logs = ref<any[]>([])
const stats = ref<any>({ streak: 0, logCount: 0, totalTrainMin: 0, todayLogged: false })
const badges = ref<any[]>([])
const msg = ref('')
const err = ref('')

const form = reactive({
  trainingItems: [] as string[],
  durationMin: 30,
  missions: [] as string[],
  selfScore: 3,
  note: '',
})

const today = computed(() => new Date().toLocaleDateString('en-CA', { timeZone: 'Asia/Taipei' }))
const todayLogged = computed(() => stats.value.todayLogged)
const earnedBadges = computed(() => badges.value.filter((b) => b.earned))
const conqueredCount = computed(() => (member.value?.branches || []).filter((b: any) => b.conquered).length)
const activeBr = computed(() => (member.value?.currentBranch ? branchMap[member.value.currentBranch] : null))
const formItems = computed(() => (activeBr.value ? activeBr.value.items : BRANCHES.flatMap((b) => b.items)))
const preview = computed(() => computeLogRewards(
  { trainingItems: form.trainingItems, durationMin: form.durationMin, missions: form.missions, note: form.note },
  form.selfScore,
))
const canSubmit = computed(() => form.trainingItems.length > 0 || form.missions.length > 0)

const itemName = (k: string) => trainingItemMap[k]?.name || k
const qName = (k: string) => qualityMap[k as keyof typeof qualityMap]?.name || k

async function load() {
  loading.value = true
  try {
    const r: any = await authedFetch('/api/soldier-diary/member')
    member.value = r.member
    logs.value = r.logs
    stats.value = r.stats
    badges.value = r.badges
    const todayLog = r.logs.find((l: any) => l.log_date === today.value)
    if (todayLog?.payload) {
      form.trainingItems = [...(todayLog.payload.trainingItems || [])]
      form.durationMin = todayLog.payload.durationMin ?? 30
      form.missions = [...(todayLog.payload.missions || [])]
      form.note = todayLog.payload.note || ''
      form.selfScore = todayLog.self_score || 3
    }
  } catch (e: any) {
    err.value = e?.data?.message || '載入失敗'
  } finally {
    loading.value = false
  }
}

async function submit() {
  msg.value = ''; err.value = ''
  submitting.value = true
  try {
    const r: any = await authedFetch('/api/soldier-diary/log-create', {
      method: 'POST',
      body: {
        trainingItems: form.trainingItems, durationMin: form.durationMin,
        missions: form.missions, selfScore: form.selfScore, note: form.note,
      },
    })
    if (r.conqueredBranch) msg.value = `🎉 突破「${r.conqueredBranch}」！${r.graduated ? '五軍全數結訓！' : '解鎖下一軍種。'}`
    else msg.value = r.updated ? '已更新今日日記。' : `呈報完成，獲得 ${r.xpAwarded} XP。`
    form.trainingItems = []
    await load()
  } catch (e: any) {
    err.value = e?.data?.message || '呈報失敗'
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  loadSession()
  if (!session.value) return navigateTo('/soldier-diary/login')
  if (isChief.value) return navigateTo('/soldier-diary/barracks')
  await load()
})
</script>

<style scoped>
.sdd-loading { text-align: center; color: var(--sd-muted); padding: 60px; letter-spacing: 0.1em; }

.sdd-idcard { display: flex; justify-content: space-between; gap: 20px; padding: 22px 24px; flex-wrap: wrap; }
.sdd-id-left { display: flex; gap: 16px; align-items: center; }
.sdd-rank-badge { width: 56px; height: 56px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; border: 2px solid var(--sd-brass); border-radius: 4px; color: var(--sd-brass); font-size: 1.2rem; font-weight: 700; background: rgba(203,164,58,0.08); }
.sdd-rank-name { font-size: 1.5rem; margin: 2px 0 6px; }
.sdd-id-meta { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; margin: 0; }
.sdd-callsign { color: var(--sd-olive-bright); font-weight: 700; letter-spacing: 0.08em; }
.sdd-name { color: var(--sd-khaki); font-size: 0.86rem; }
.sdd-squad { color: var(--sd-muted); font-size: 0.74rem; border: 1px solid var(--sd-line); padding: 1px 7px; border-radius: 2px; }
.sdd-id-right { min-width: 220px; flex: 1; max-width: 320px; }
.sdd-xp-line { text-align: right; }
.sdd-xp-num { font-size: 1.7rem; font-weight: 900; color: var(--sd-sand); }
.sdd-xp-unit { color: var(--sd-olive); font-size: 0.8rem; margin-left: 4px; }
.sdd-xp-bar { height: 9px; background: #12140d; border: 1px solid var(--sd-line); border-radius: 5px; overflow: hidden; margin: 6px 0; }
.sdd-xp-fill { height: 100%; background: linear-gradient(90deg, var(--sd-olive), var(--sd-brass)); transition: width 0.4s; }
.sdd-xp-next { text-align: right; color: var(--sd-muted); font-size: 0.74rem; margin: 0; }

.sdd-block { padding: 18px 20px; margin-top: 14px; }
.sdd-branch-head { display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 12px; }
.sdd-cur { color: var(--sd-olive-bright); font-size: 0.82rem; font-weight: 700; }
.sdd-grad { color: var(--sd-brass); font-size: 0.86rem; font-weight: 700; }
.sdd-branches { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; }
.sdd-branch { border: 1px solid var(--sd-line); border-radius: 4px; padding: 12px 12px 10px; background: #171a11; position: relative; }
.sdd-branch--done { border-color: var(--bc); background: color-mix(in srgb, var(--bc) 14%, #171a11); }
.sdd-branch--active { border-color: var(--sd-brass); box-shadow: 0 0 0 1px var(--sd-brass) inset; }
.sdd-branch--lock { opacity: 0.45; }
.sdd-branch-top { display: flex; justify-content: space-between; align-items: baseline; }
.sdd-branch-name { font-weight: 700; color: var(--sd-sand); font-size: 0.88rem; }
.sdd-branch-state { font-size: 0.66rem; color: var(--sd-muted); }
.sdd-branch--done .sdd-branch-state { color: var(--bc); font-weight: 700; }
.sdd-branch--active .sdd-branch-state { color: var(--sd-brass); font-weight: 700; }
.sdd-branch-q { font-size: 0.72rem; color: var(--sd-muted); margin: 3px 0 8px; }
.sdd-branch-bar { height: 7px; background: #0f110a; border: 1px solid var(--sd-line); border-radius: 4px; overflow: hidden; }
.sdd-branch-fill { height: 100%; background: var(--bc); transition: width 0.4s; }
.sdd-branch-val { text-align: right; font-size: 0.68rem; color: var(--sd-khaki); margin-top: 3px; font-variant-numeric: tabular-nums; }

.sdd-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 14px 0; }
.sdd-stat { text-align: center; padding: 14px 8px; }
.sdd-stat-n { display: block; font-size: 1.5rem; font-weight: 900; color: var(--sd-olive-bright); }
.sdd-stat-l { font-size: 0.7rem; color: var(--sd-muted); letter-spacing: 0.06em; }

.sdd-cols { display: grid; grid-template-columns: 340px 1fr; gap: 14px; }
.sdd-col { display: flex; flex-direction: column; }
.sdd-col > .sdd-block:first-child { margin-top: 0; }

.sdd-attr { display: grid; grid-template-columns: 74px 1fr 34px; align-items: center; gap: 10px; margin: 10px 0; }
.sdd-attr-name { font-size: 0.82rem; color: var(--sd-khaki); }
.sdd-attr-name b { display: inline-block; width: 18px; margin-right: 5px; font-weight: 900; }
.sdd-attr-bar { height: 8px; background: #12140d; border: 1px solid var(--sd-line); border-radius: 4px; overflow: hidden; }
.sdd-attr-fill { height: 100%; transition: width 0.4s; }
.sdd-attr-val { text-align: right; font-weight: 700; color: var(--sd-sand); font-size: 0.86rem; }

.sdd-badges { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin-top: 10px; }
.sdd-badge { display: flex; align-items: center; gap: 8px; padding: 8px 10px; border: 1px solid var(--sd-line); border-radius: 3px; background: #171a11; }
.sdd-badge--off { opacity: 0.32; filter: grayscale(1); }
.sdd-badge-ic { font-size: 1.1rem; }
.sdd-badge-nm { font-size: 0.76rem; color: var(--sd-khaki); }

.sdd-diary-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.sdd-date { color: var(--sd-muted); font-size: 0.78rem; }
.sdd-focus { font-size: 0.8rem; color: var(--sd-khaki); background: color-mix(in srgb, var(--bc, #7a8b3f) 12%, transparent); border-left: 3px solid var(--bc, #7a8b3f); padding: 8px 12px; border-radius: 3px; margin-bottom: 14px; }
.sdd-focus b { color: var(--sd-sand); }
.sdd-focus--grad { border-color: var(--sd-brass); background: rgba(203,164,58,0.1); }
.sdd-checks { display: flex; flex-wrap: wrap; gap: 7px; margin-bottom: 14px; }
.sdd-check { display: inline-flex; align-items: center; gap: 6px; cursor: pointer; padding: 6px 11px; border: 1px solid var(--sd-line); border-radius: 3px; font-size: 0.8rem; color: var(--sd-khaki); background: #171a11; transition: all 0.12s; }
.sdd-check--on { border-color: var(--sd-olive); background: rgba(122,139,63,0.16); color: var(--sd-sand); }
.sdd-check input { accent-color: var(--sd-olive); }
.sdd-check em { color: var(--sd-olive); font-style: normal; font-size: 0.72rem; }
.sdd-row { display: flex; gap: 14px; margin-bottom: 14px; }
.sdd-field { flex: 1; }
.sdd-stars { display: flex; gap: 3px; }
.sdd-star { background: none; border: none; cursor: pointer; font-size: 1.3rem; color: #3a4128; padding: 0; }
.sdd-star--on { color: var(--sd-brass); }
.sdd-preview { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin: 4px 0 12px; font-size: 0.78rem; color: var(--sd-muted); }
.sdd-preview-xp { color: var(--sd-brass); font-size: 0.92rem; }
.sdd-preview-attr { color: var(--sd-olive-bright); }
.sdd-block .sd-ok, .sdd-block .sd-error { margin-bottom: 10px; }

.sdd-history { margin-top: 14px; }
.sdd-log { padding: 12px 0; border-bottom: 1px solid var(--sd-line); }
.sdd-log:last-child { border-bottom: none; }
.sdd-log-top { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
.sdd-log-date { font-weight: 700; color: var(--sd-sand); font-size: 0.86rem; }
.sdd-log-branch { font-size: 0.76rem; font-weight: 700; }
.sdd-log-xp { color: var(--sd-brass); font-size: 0.8rem; }
.sdd-log-self { color: var(--sd-muted); font-size: 0.78rem; }
.sdd-log-reviewed { color: var(--sd-olive-bright); font-size: 0.72rem; border: 1px solid var(--sd-olive); padding: 0 6px; border-radius: 2px; }
.sdd-log-body { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 6px; }
.sdd-log-tag { font-size: 0.72rem; color: var(--sd-khaki); background: #171a11; border: 1px solid var(--sd-line); padding: 1px 7px; border-radius: 2px; }
.sdd-log-dur { font-size: 0.72rem; color: var(--sd-muted); }
.sdd-log-note { color: var(--sd-khaki); font-size: 0.82rem; margin: 6px 0 0; font-style: italic; }
.sdd-log-officer { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin-top: 8px; padding: 7px 10px; background: rgba(203,164,58,0.06); border-left: 2px solid var(--sd-brass); font-size: 0.8rem; color: var(--sd-khaki); }
.sdd-officer-tag { color: var(--sd-brass); font-weight: 700; font-size: 0.72rem; }

@media (max-width: 760px) {
  .sdd-cols { grid-template-columns: 1fr; }
  .sdd-stats { grid-template-columns: repeat(2, 1fr); }
  .sdd-branches { grid-template-columns: repeat(2, 1fr); }
}
</style>
