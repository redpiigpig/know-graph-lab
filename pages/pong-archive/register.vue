<template>
  <div class="par-wrap">
    <div class="par-card">
      <div class="par-logo">
        <span class="par-logo-zh">龐君華會督數位典藏</span>
        <span class="par-logo-en">Bishop Pong Kwan-wah Digital Archive</span>
      </div>

      <!-- Success state -->
      <div v-if="submitted" class="par-success">
        <div class="par-success-icon">✓</div>
        <h2 class="par-success-title">申請已提交</h2>
        <p class="par-success-body">
          感謝您申請加入龐君華會督數位典藏的校對團隊。<br>
          我們將在審核後通知您，請靜候總編輯核准。
        </p>
        <NuxtLink to="/pong-archive" class="par-btn par-btn--outline">返回典藏首頁</NuxtLink>
      </div>

      <!-- Form state -->
      <template v-else>
        <h1 class="par-title">申請成為校對者</h1>
        <p class="par-subtitle">填寫以下資料，提交後由總編輯審核，核准後即可登入參與校對工作。</p>

        <form class="par-form" @submit.prevent="submit">

          <div class="par-row">
            <div class="par-field par-field--required">
              <label class="par-label">姓名</label>
              <input v-model="form.name" class="par-input" placeholder="請填寫真實姓名" required />
            </div>
            <div class="par-field">
              <label class="par-label">性別</label>
              <select v-model="form.gender" class="par-input par-input--select">
                <option value="">不指定</option>
                <option value="男">男</option>
                <option value="女">女</option>
              </select>
            </div>
            <div class="par-field">
              <label class="par-label">年齡層</label>
              <select v-model="form.age_group" class="par-input par-input--select">
                <option value="">不指定</option>
                <option value="20以下">20 歲以下</option>
                <option value="20-30">20–30 歲</option>
                <option value="30-40">30–40 歲</option>
                <option value="40-50">40–50 歲</option>
                <option value="50-60">50–60 歲</option>
                <option value="60以上">60 歲以上</option>
              </select>
            </div>
          </div>

          <div class="par-row">
            <div class="par-field par-field--wide par-field--required">
              <label class="par-label">電子郵件（作為登入帳號）</label>
              <input v-model="form.email" type="email" class="par-input" placeholder="your@email.com" required autocomplete="email" />
            </div>
            <div class="par-field par-field--wide">
              <label class="par-label">所屬教會</label>
              <input v-model="form.church" class="par-input" placeholder="教會名稱（選填）" />
            </div>
          </div>

          <div class="par-field">
            <label class="par-label">認識龐會督的簡要經過</label>
            <textarea v-model="form.how_knew" class="par-textarea" rows="3" placeholder="請簡述您與龐君華會督的淵源或認識經過…" />
          </div>

          <div class="par-field">
            <label class="par-label">希望協助這個事工的地方</label>
            <textarea v-model="form.how_to_help" class="par-textarea" rows="3" placeholder="例如：逐字稿校對、資料整理、翻譯英文字幕…" />
          </div>

          <p v-if="error" class="par-error">{{ error }}</p>

          <div class="par-actions">
            <button type="submit" class="par-btn" :disabled="loading">
              <span v-if="loading" class="par-spin" />
              {{ loading ? '提交中…' : '提交申請' }}
            </button>
            <NuxtLink to="/pong-archive/login" class="par-link">已有帳號，登入 →</NuxtLink>
          </div>

        </form>
      </template>
    </div>
  </div>
</template>

<script setup>
definePageMeta({ layout: 'pong-archive' })

import { reactive, ref } from 'vue'

const form = reactive({
  name: '',
  gender: '',
  age_group: '',
  email: '',
  church: '',
  how_knew: '',
  how_to_help: '',
})

const loading = ref(false)
const error = ref('')
const submitted = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await $fetch('/api/pong-auth/register', {
      method: 'POST',
      body: { ...form },
    })
    submitted.value = true
  } catch (e) {
    error.value = e?.data?.message || e?.message || '提交失敗，請稍後再試'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500&family=Noto+Serif+TC:wght@400;500;600&display=swap');

.par-wrap {
  min-height: 70vh;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 56px 20px 80px;
}

.par-card {
  width: 100%;
  max-width: 680px;
  background-color: #F4F1EC;
  border: 1px solid #DDD8CF;
  border-radius: 6px;
  padding: 48px 48px 44px;
}

.par-logo {
  text-align: center;
  margin-bottom: 28px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.par-logo-zh {
  font-family: 'Noto Serif TC', serif;
  font-size: 0.95rem;
  font-weight: 500;
  color: #3A3025;
  letter-spacing: 0.1em;
}
.par-logo-en {
  font-size: 0.62rem;
  font-weight: 300;
  color: #A09280;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.par-title {
  font-family: 'Noto Serif TC', serif;
  font-size: 1.2rem;
  font-weight: 500;
  color: #2C2C2C;
  letter-spacing: 0.08em;
  margin: 0 0 8px;
  text-align: center;
}
.par-subtitle {
  font-size: 0.8rem;
  font-weight: 300;
  color: #8A8278;
  letter-spacing: 0.04em;
  text-align: center;
  margin: 0 0 32px;
  line-height: 1.8;
}

.par-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.par-row {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.par-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
  min-width: 120px;
}
.par-field--wide { flex: 2; min-width: 200px; }

.par-label {
  font-size: 0.65rem;
  font-weight: 300;
  color: #8A8278;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.par-field--required .par-label::after {
  content: ' *';
  color: #8A3030;
}

.par-input,
.par-textarea {
  background: #FDFCFA;
  border: 1px solid #C8BFB0;
  border-radius: 3px;
  padding: 9px 12px;
  font-family: 'Noto Sans TC', sans-serif;
  font-size: 0.88rem;
  font-weight: 300;
  color: #2C2C2C;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  width: 100%;
  box-sizing: border-box;
  letter-spacing: 0.02em;
}
.par-input:focus,
.par-textarea:focus {
  border-color: #8A7E6E;
  box-shadow: 0 0 0 3px rgba(138,126,110,0.1);
}
.par-input--select { cursor: pointer; appearance: auto; }
.par-textarea { resize: vertical; line-height: 1.8; min-height: 80px; }

.par-error {
  font-size: 0.8rem;
  color: #8A3030;
  background-color: rgba(138,48,48,0.06);
  border: 1px solid rgba(138,48,48,0.2);
  border-radius: 3px;
  padding: 8px 12px;
  margin: 0;
  letter-spacing: 0.04em;
}

.par-actions {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-top: 4px;
  flex-wrap: wrap;
}

.par-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 11px 28px;
  background-color: #5B3F2A;
  color: #fff;
  border: none;
  border-radius: 3px;
  font-family: 'Noto Sans TC', sans-serif;
  font-size: 0.85rem;
  font-weight: 400;
  letter-spacing: 0.1em;
  cursor: pointer;
  text-decoration: none;
  transition: background-color 0.2s;
}
.par-btn:hover:not(:disabled) { background-color: #4A3020; }
.par-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.par-btn--outline {
  background-color: transparent;
  color: #5B3F2A;
  border: 1px solid #5B3F2A;
}
.par-btn--outline:hover { background-color: rgba(91,63,42,0.06); }

.par-link {
  font-size: 0.78rem;
  font-weight: 300;
  color: #8A8278;
  text-decoration: none;
  letter-spacing: 0.06em;
  transition: color 0.2s;
}
.par-link:hover { color: #3A3025; }

.par-spin {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255,255,255,0.4);
  border-top-color: #fff;
  border-radius: 50%;
  animation: par-spin 0.7s linear infinite;
  flex-shrink: 0;
}
@keyframes par-spin { to { transform: rotate(360deg); } }

/* Success state */
.par-success {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 16px 0;
  gap: 16px;
}
.par-success-icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background-color: rgba(74,122,90,0.12);
  color: #4A7A5A;
  font-size: 1.6rem;
  display: flex;
  align-items: center;
  justify-content: center;
}
.par-success-title {
  font-family: 'Noto Serif TC', serif;
  font-size: 1.2rem;
  font-weight: 500;
  color: #2C2C2C;
  margin: 0;
  letter-spacing: 0.08em;
}
.par-success-body {
  font-size: 0.88rem;
  font-weight: 300;
  color: #6A6460;
  line-height: 1.9;
  letter-spacing: 0.04em;
  margin: 0;
}

@media (max-width: 640px) {
  .par-card { padding: 36px 24px 32px; }
  .par-row { flex-direction: column; }
  .par-field--wide { min-width: unset; }
}
</style>
