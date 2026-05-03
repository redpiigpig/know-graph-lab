<template>
  <div class="pa-root">
    <header class="pa-header" :class="{ 'pa-header--editing': isEditing }">
      <div class="pa-header-inner">

        <!-- 中：典藏名稱 -->
        <div class="pa-title-group">
          <span class="pa-logo-cross" aria-hidden="true">✝</span>
          <span class="pa-header-zh">龐君華會督數位典藏</span>
          <span class="pa-header-divider">·</span>
          <span class="pa-header-en">Bishop Pong Kwan-wah Digital Archive</span>
        </div>

        <!-- 右：操作區 -->
        <div class="pa-header-actions">
          <Transition name="pa-save-fade">
            <span v-if="isEditing && saveStatus !== 'idle'" class="pa-save-indicator" :class="`pa-save--${saveStatus}`">
              <span v-if="saveStatus === 'saving' || saveStatus === 'pending'" class="pa-save-dot pa-save-dot--spin" />
              <span v-else-if="saveStatus === 'saved'" class="pa-save-dot pa-save-dot--ok" />
              <span v-else-if="saveStatus === 'error'" class="pa-save-dot pa-save-dot--err" />
              {{ saveStatusLabel }}
            </span>
          </Transition>

          <!-- 校對者管理（總編輯） -->
          <button
            v-if="isChief"
            class="pa-icon-btn"
            title="校對者管理"
            @click="openPanel"
          >
            <svg class="pa-icon-svg" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="6.5" cy="6" r="2.5" stroke="currentColor" stroke-width="1.2"/>
              <path d="M1 15c0-3 2.5-4.5 5.5-4.5S12 12 12 15" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
              <circle cx="13" cy="6" r="2" stroke="currentColor" stroke-width="1.2"/>
              <path d="M14.5 14.5c1.5-.5 2.5-1.5 2.5-3" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
            </svg>
          </button>

          <!-- 編輯按鈕 -->
          <button
            v-if="isLoggedIn"
            class="pa-edit-btn"
            :class="{ 'pa-edit-btn--active': isEditing }"
            :title="isEditing ? '完成編輯' : '編輯典藏內容'"
            @click="toggleEdit"
          >
            <svg v-if="!isEditing" class="pa-edit-icon" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12.5 2.5L15.5 5.5L6 15H3V12L12.5 2.5Z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round" fill="none"/>
              <line x1="10" y1="5" x2="13" y2="8" stroke="currentColor" stroke-width="1.3"/>
            </svg>
            <svg v-else class="pa-edit-icon" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
              <polyline points="3,9 7,13 15,5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span class="pa-edit-label">{{ isEditing ? '完成' : '編輯' }}</span>
          </button>

          <!-- 登入狀態 -->
          <div class="pa-auth">
            <template v-if="isLoggedIn">
              <span class="pa-user-name">{{ session?.name }}</span>
              <button class="pa-auth-link" @click="doLogout">登出</button>
            </template>
            <NuxtLink v-else to="/pong-archive/login" class="pa-auth-link pa-auth-link--login">登入</NuxtLink>
          </div>
        </div>

      </div>
    </header>

    <main class="pa-main">
      <slot />
    </main>

    <footer class="pa-footer">
      <p class="pa-footer-text">
        龐君華會督數位典藏 &copy; {{ new Date().getFullYear() }}
      </p>
    </footer>

    <!-- ── Chief Editor Panel ──────────────────────────── -->
    <Transition name="pa-panel-bg">
      <div v-if="panelOpen" class="pa-panel-backdrop" @click.self="panelOpen = false" />
    </Transition>
    <Transition name="pa-panel-slide">
      <div v-if="panelOpen" class="pa-panel">
        <div class="pa-panel-hd">
          <span class="pa-panel-title">校對者管理</span>
          <div class="pa-panel-hd-right">
            <button class="pa-panel-refresh" title="重新載入" @click="loadEditors">↻</button>
            <button class="pa-panel-close" @click="panelOpen = false">✕</button>
          </div>
        </div>

        <!-- Filter tabs -->
        <div class="pa-panel-tabs">
          <button
            v-for="tab in filterTabs"
            :key="tab.key"
            class="pa-tab"
            :class="{ 'pa-tab--active': editorFilter === tab.key }"
            @click="editorFilter = tab.key"
          >
            {{ tab.label }}
            <span class="pa-tab-count">{{ tabCount(tab.key) }}</span>
          </button>
        </div>

        <div class="pa-panel-body">
          <div v-if="panelLoading" class="pa-panel-loading">載入中…</div>
          <div v-else-if="filteredEditors.length === 0" class="pa-panel-empty">
            {{ editors.length === 0 ? '尚無申請記錄' : '此分類無資料' }}
          </div>
          <div
            v-else
            v-for="ed in filteredEditors"
            :key="ed.id"
            class="pa-ec"
            :class="`pa-ec--${ed.status}`"
          >
            <div class="pa-ec-top" @click="toggleExpand(ed.id)">
              <div class="pa-ec-info">
                <span class="pa-ec-name">{{ ed.name }}</span>
                <span class="pa-ec-email">{{ ed.email }}</span>
              </div>
              <div class="pa-ec-right">
                <span class="pa-ec-badge" :class="`pa-ec-badge--${ed.status}`">{{ statusLabel(ed.status) }}</span>
                <span class="pa-ec-chevron" :class="{ 'pa-ec-chevron--open': expanded.has(ed.id) }">▾</span>
              </div>
            </div>

            <Transition name="pa-expand">
              <div v-if="expanded.has(ed.id)" class="pa-ec-detail">
                <div class="pa-ec-grid">
                  <div v-if="ed.gender" class="pa-ec-kv"><span class="pa-ec-k">性別</span><span class="pa-ec-v">{{ ed.gender }}</span></div>
                  <div v-if="ed.age_group" class="pa-ec-kv"><span class="pa-ec-k">年齡層</span><span class="pa-ec-v">{{ ed.age_group }}</span></div>
                  <div v-if="ed.church" class="pa-ec-kv"><span class="pa-ec-k">所屬教會</span><span class="pa-ec-v">{{ ed.church }}</span></div>
                  <div class="pa-ec-kv"><span class="pa-ec-k">申請日期</span><span class="pa-ec-v">{{ fmtDate(ed.applied_at) }}</span></div>
                  <div v-if="ed.last_login" class="pa-ec-kv"><span class="pa-ec-k">最後登入</span><span class="pa-ec-v">{{ fmtDate(ed.last_login) }}</span></div>
                </div>
                <div v-if="ed.how_knew" class="pa-ec-section">
                  <span class="pa-ec-k">認識龐會督的經過</span>
                  <p class="pa-ec-p">{{ ed.how_knew }}</p>
                </div>
                <div v-if="ed.how_to_help" class="pa-ec-section">
                  <span class="pa-ec-k">希望協助的地方</span>
                  <p class="pa-ec-p">{{ ed.how_to_help }}</p>
                </div>
                <div class="pa-ec-actions">
                  <template v-if="ed.status === 'pending'">
                    <button class="pa-ec-btn pa-ec-btn--ok" @click="doApprove(ed, 'approve')">核准</button>
                    <button class="pa-ec-btn pa-ec-btn--no" @click="doApprove(ed, 'reject')">拒絕</button>
                  </template>
                  <button v-else-if="ed.status === 'rejected'" class="pa-ec-btn pa-ec-btn--ok" @click="doApprove(ed, 'approve')">改為核准</button>
                  <button v-else-if="ed.status === 'approved'" class="pa-ec-btn pa-ec-btn--no" @click="doApprove(ed, 'reject')">撤銷核准</button>
                </div>
              </div>
            </Transition>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useHead } from '#imports'
import { usePongEditor } from '~/composables/usePongEditor'
import { usePongSession } from '~/composables/usePongSession'

useHead({ title: '龐君華會督數位典藏' })

const { isEditing, saveStatus, toggleEdit } = usePongEditor()
const { session, isLoggedIn, isChief, logout, loadSession } = usePongSession()

const saveStatusLabel = computed(() => ({
  pending: '等待儲存…',
  saving:  '儲存中…',
  saved:   '已儲存',
  error:   '儲存失敗',
  idle:    '',
}[saveStatus.value] ?? ''))

function doLogout() {
  if (isEditing.value) toggleEdit()
  logout()
}

// ── Chief Panel ────────────────────────────────────────────────
const panelOpen    = ref(false)
const panelLoading = ref(false)
const editors      = ref([])
const editorFilter = ref('all')
const expanded     = ref(new Set())

const filterTabs = [
  { key: 'all',      label: '全部' },
  { key: 'pending',  label: '待審核' },
  { key: 'approved', label: '已核准' },
  { key: 'rejected', label: '已拒絕' },
]

function tabCount(key) {
  if (key === 'all') return editors.value.length
  return editors.value.filter(e => e.status === key).length
}

const filteredEditors = computed(() =>
  editorFilter.value === 'all'
    ? editors.value
    : editors.value.filter(e => e.status === editorFilter.value)
)

function statusLabel(s) {
  return { pending: '待審核', approved: '已核准', rejected: '已拒絕' }[s] || s
}

function fmtDate(d) {
  if (!d) return '—'
  const dt = new Date(d)
  return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}-${String(dt.getDate()).padStart(2, '0')}`
}

function toggleExpand(id) {
  const s = new Set(expanded.value)
  if (s.has(id)) s.delete(id)
  else s.add(id)
  expanded.value = s
}

async function loadEditors() {
  panelLoading.value = true
  try {
    editors.value = await $fetch('/api/pong-auth/editors')
  } catch (e) {
    console.error('[panel]', e)
  } finally {
    panelLoading.value = false
  }
}

async function doApprove(ed, action) {
  try {
    await $fetch('/api/pong-auth/approve', {
      method: 'POST',
      body: { id: ed.id, action, approver: session.value?.name },
    })
    ed.status = action === 'approve' ? 'approved' : 'rejected'
  } catch (e) {
    alert('操作失敗：' + (e?.data?.message || e.message))
  }
}

function openPanel() {
  panelOpen.value = true
  if (!editors.value.length) loadEditors()
}

watch(panelOpen, (open) => {
  document.body.style.overflow = open ? 'hidden' : ''
})

onMounted(() => {
  loadSession()
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500&family=Noto+Serif+TC:wght@400;500;600&display=swap');

/* ── Root ──────────────────────────────────────────────────── */
.pa-root {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #F9F8F6;
  color: #2C2C2C;
  font-family: 'Noto Sans TC', 'PingFang TC', 'Microsoft JhengHei', sans-serif;
  font-size: 16px;
  line-height: 1.8;
  letter-spacing: 0.04em;
}

/* ── Header ────────────────────────────────────────────────── */
.pa-header {
  background-color: #F2EFE9;
  border-bottom: 1px solid #DDD8CF;
  padding: 0 40px;
  transition: border-color 0.3s, background-color 0.3s;
}
.pa-header--editing {
  background-color: #EDE8DF;
  border-bottom-color: #C4B89A;
}

.pa-header-inner {
  position: relative;
  max-width: 1100px;
  margin: 0 auto;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.pa-title-group {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 10px;
  white-space: nowrap;
  pointer-events: none;
}
.pa-logo-cross {
  font-size: 1rem;
  color: #8A7A68;
  line-height: 1;
  flex-shrink: 0;
  letter-spacing: 0;
}

.pa-header-zh {
  font-family: 'Noto Serif TC', 'SimSun', serif;
  font-size: 1rem;
  font-weight: 500;
  color: #3A3530;
  letter-spacing: 0.1em;
}
.pa-header-divider { color: #B0A89A; font-size: 0.85rem; }
.pa-header-en {
  font-family: 'Noto Sans TC', sans-serif;
  font-size: 0.72rem;
  font-weight: 300;
  color: #8C8278;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

/* ── Header Actions ─────────────────────────────────────────── */
.pa-header-actions {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
}

/* ── Save Indicator ─────────────────────────────────────────── */
.pa-save-indicator {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.68rem;
  font-weight: 300;
  letter-spacing: 0.08em;
  white-space: nowrap;
}
.pa-save--pending, .pa-save--saving { color: #8A7E6E; }
.pa-save--saved  { color: #4A7A5A; }
.pa-save--error  { color: #8A3030; }

.pa-save-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}
.pa-save-dot--spin {
  border: 1.5px solid currentColor;
  border-top-color: transparent;
  animation: pa-spin 0.7s linear infinite;
}
.pa-save-dot--ok  { background-color: #4A7A5A; }
.pa-save-dot--err { background-color: #8A3030; }
@keyframes pa-spin { to { transform: rotate(360deg); } }

.pa-save-fade-enter-active, .pa-save-fade-leave-active { transition: opacity 0.25s; }
.pa-save-fade-enter-from, .pa-save-fade-leave-to { opacity: 0; }

/* ── Icon Button (chief panel) ──────────────────────────────── */
.pa-icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: 1px solid #C8BFB0;
  border-radius: 50%;
  background: transparent;
  color: #7A7268;
  cursor: pointer;
  transition: color 0.2s, border-color 0.2s, background-color 0.2s;
}
.pa-icon-btn:hover { color: #3A3025; border-color: #A09080; background-color: #F2EDE4; }
.pa-icon-svg { width: 15px; height: 15px; flex-shrink: 0; }

/* ── Edit Button ────────────────────────────────────────────── */
.pa-edit-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 12px 5px 10px;
  border: 1px solid #C8BFB0;
  border-radius: 20px;
  background: transparent;
  color: #7A7268;
  font-family: 'Noto Sans TC', sans-serif;
  font-size: 0.72rem;
  font-weight: 300;
  letter-spacing: 0.1em;
  cursor: pointer;
  transition: color 0.2s, border-color 0.2s, background-color 0.2s, box-shadow 0.2s;
  white-space: nowrap;
}
.pa-edit-btn:hover {
  color: #3A3025;
  border-color: #A09080;
  background-color: #F2EDE4;
}
.pa-edit-btn--active {
  color: #fff;
  background-color: #5B3F2A;
  border-color: #5B3F2A;
  box-shadow: 0 2px 8px rgba(91,63,42,0.25);
}
.pa-edit-btn--active:hover {
  background-color: #4A3020;
  border-color: #4A3020;
}
.pa-edit-icon {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
  transition: transform 0.2s;
}
.pa-edit-btn:hover .pa-edit-icon { transform: rotate(-5deg); }
.pa-edit-btn--active:hover .pa-edit-icon { transform: none; }
.pa-edit-label { line-height: 1; }

/* ── Auth ───────────────────────────────────────────────────── */
.pa-auth {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-left: 4px;
  border-left: 1px solid #DDD8CF;
  margin-left: 2px;
}
.pa-user-name {
  font-size: 0.7rem;
  font-weight: 300;
  color: #7A7268;
  letter-spacing: 0.06em;
  white-space: nowrap;
  max-width: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
}
.pa-auth-link {
  font-size: 0.7rem;
  font-weight: 300;
  color: #8A8278;
  letter-spacing: 0.08em;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  text-decoration: none;
  transition: color 0.2s;
  white-space: nowrap;
}
.pa-auth-link:hover { color: #3A3025; }
.pa-auth-link--login { color: #5B3F2A; font-weight: 400; }

/* ── Main ──────────────────────────────────────────────────── */
.pa-main { flex: 1; }

/* ── Footer ────────────────────────────────────────────── */
.pa-footer { border-top: 1px solid #DDD8CF; padding: 28px 40px; text-align: center; }
.pa-footer-text { font-size: 0.75rem; color: #A09890; letter-spacing: 0.08em; margin: 0; }

/* ── Panel Backdrop ─────────────────────────────────────────── */
.pa-panel-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgba(40, 32, 24, 0.35);
  z-index: 900;
}
.pa-panel-bg-enter-active, .pa-panel-bg-leave-active { transition: opacity 0.25s; }
.pa-panel-bg-enter-from, .pa-panel-bg-leave-to { opacity: 0; }

/* ── Panel Drawer ───────────────────────────────────────────── */
.pa-panel {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  width: 400px;
  max-width: 100vw;
  background-color: #F4F1EC;
  border-left: 1px solid #DDD8CF;
  z-index: 910;
  display: flex;
  flex-direction: column;
  box-shadow: -8px 0 32px rgba(40,30,20,0.12);
  overflow: hidden;
}
.pa-panel-slide-enter-active, .pa-panel-slide-leave-active { transition: transform 0.28s cubic-bezier(0.4,0,0.2,1); }
.pa-panel-slide-enter-from, .pa-panel-slide-leave-to { transform: translateX(100%); }

/* Panel header */
.pa-panel-hd {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid #DDD8CF;
  flex-shrink: 0;
}
.pa-panel-title {
  font-family: 'Noto Serif TC', serif;
  font-size: 0.95rem;
  font-weight: 500;
  color: #3A3025;
  letter-spacing: 0.08em;
}
.pa-panel-hd-right { display: flex; gap: 8px; align-items: center; }
.pa-panel-refresh, .pa-panel-close {
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  color: #8A8278;
  font-size: 0.9rem;
  cursor: pointer;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s, color 0.2s;
}
.pa-panel-refresh:hover, .pa-panel-close:hover { background-color: #E8E4DC; color: #3A3025; }

/* Filter tabs */
.pa-panel-tabs {
  display: flex;
  gap: 0;
  padding: 12px 24px 0;
  flex-shrink: 0;
  border-bottom: 1px solid #DDD8CF;
}
.pa-tab {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 8px 12px;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  font-family: 'Noto Sans TC', sans-serif;
  font-size: 0.72rem;
  font-weight: 300;
  color: #8A8278;
  letter-spacing: 0.06em;
  cursor: pointer;
  transition: color 0.2s, border-color 0.2s;
  white-space: nowrap;
  margin-bottom: -1px;
}
.pa-tab:hover { color: #3A3025; }
.pa-tab--active { color: #3A3025; border-bottom-color: #5B3F2A; font-weight: 400; }
.pa-tab-count {
  background-color: #DDD8CF;
  color: #7A7268;
  border-radius: 10px;
  font-size: 0.65rem;
  padding: 1px 6px;
  font-weight: 400;
}
.pa-tab--active .pa-tab-count { background-color: #C4B89A; color: #3A3025; }

/* Panel body */
.pa-panel-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.pa-panel-loading, .pa-panel-empty {
  text-align: center;
  font-size: 0.8rem;
  font-weight: 300;
  color: #A09280;
  letter-spacing: 0.06em;
  padding: 40px 20px;
}

/* Editor cards */
.pa-ec {
  border: 1px solid #DDD8CF;
  border-radius: 4px;
  background-color: #FDFCFA;
  overflow: hidden;
  transition: border-color 0.2s;
}
.pa-ec--pending { border-left: 3px solid #C4A860; }
.pa-ec--approved { border-left: 3px solid #4A7A5A; }
.pa-ec--rejected { border-left: 3px solid #B07070; }

.pa-ec-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  cursor: pointer;
  user-select: none;
  transition: background-color 0.15s;
}
.pa-ec-top:hover { background-color: #F4F1EC; }

.pa-ec-info { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.pa-ec-name { font-size: 0.88rem; font-weight: 500; color: #2C2C2C; letter-spacing: 0.04em; }
.pa-ec-email { font-size: 0.72rem; font-weight: 300; color: #8A8278; letter-spacing: 0.04em; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.pa-ec-right { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
.pa-ec-badge {
  font-size: 0.62rem;
  font-weight: 400;
  padding: 2px 8px;
  border-radius: 10px;
  letter-spacing: 0.06em;
  white-space: nowrap;
}
.pa-ec-badge--pending  { background-color: rgba(196,168,96,0.15); color: #8A7230; }
.pa-ec-badge--approved { background-color: rgba(74,122,90,0.12); color: #2A5A3A; }
.pa-ec-badge--rejected { background-color: rgba(176,112,112,0.12); color: #7A3030; }

.pa-ec-chevron { font-size: 0.75rem; color: #A09280; transition: transform 0.2s; display: inline-block; }
.pa-ec-chevron--open { transform: rotate(180deg); }

/* Editor detail */
.pa-ec-detail {
  padding: 0 14px 14px;
  border-top: 1px solid #EDE8DF;
}
.pa-expand-enter-active, .pa-expand-leave-active { transition: opacity 0.2s; }
.pa-expand-enter-from, .pa-expand-leave-to { opacity: 0; }

.pa-ec-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px 16px;
  padding: 12px 0 10px;
}
.pa-ec-kv { display: flex; flex-direction: column; gap: 2px; }
.pa-ec-k { font-size: 0.6rem; font-weight: 300; color: #A09280; letter-spacing: 0.1em; text-transform: uppercase; }
.pa-ec-v { font-size: 0.8rem; color: #3A3530; letter-spacing: 0.04em; }

.pa-ec-section { margin-top: 10px; }
.pa-ec-section .pa-ec-k { display: block; margin-bottom: 4px; }
.pa-ec-p { font-size: 0.8rem; font-weight: 300; color: #5A5550; line-height: 1.8; letter-spacing: 0.04em; margin: 0; }

.pa-ec-actions {
  display: flex;
  gap: 8px;
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid #EDE8DF;
}
.pa-ec-btn {
  padding: 6px 18px;
  border: none;
  border-radius: 3px;
  font-family: 'Noto Sans TC', sans-serif;
  font-size: 0.75rem;
  font-weight: 400;
  letter-spacing: 0.08em;
  cursor: pointer;
  transition: background-color 0.2s;
}
.pa-ec-btn--ok { background-color: #4A7A5A; color: #fff; }
.pa-ec-btn--ok:hover { background-color: #3A6A4A; }
.pa-ec-btn--no { background-color: #B07070; color: #fff; }
.pa-ec-btn--no:hover { background-color: #9A5858; }

/* ── Responsive ────────────────────────────────────────────── */
@media (max-width: 640px) {
  .pa-header { padding: 0 20px; }
  .pa-header-en, .pa-header-divider { display: none; }
  .pa-edit-label { display: none; }
  .pa-edit-btn { padding: 5px 8px; }
  .pa-save-indicator { display: none; }
  .pa-user-name { display: none; }
  .pa-panel { width: 100vw; }
}
</style>
