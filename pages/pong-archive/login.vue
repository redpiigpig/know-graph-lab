<template>
  <div class="pal-wrap">
    <div class="pal-card">
      <div class="pal-logo">
        <span class="pal-logo-zh">龐君華會督數位典藏</span>
        <span class="pal-logo-en">Bishop Pong Kwan-wah Digital Archive</span>
      </div>

      <h1 class="pal-title">校對者登入</h1>

      <form class="pal-form" @submit.prevent="submit">
        <div class="pal-field">
          <label class="pal-label">電子郵件</label>
          <input
            v-model="form.email"
            type="email"
            class="pal-input"
            placeholder="your@email.com"
            required
            autocomplete="email"
          />
        </div>
        <div class="pal-field">
          <label class="pal-label">登入密碼</label>
          <input
            v-model="form.password"
            type="password"
            class="pal-input"
            placeholder="輸入密碼"
            required
            autocomplete="current-password"
          />
        </div>

        <p v-if="error" class="pal-error">{{ error }}</p>

        <button type="submit" class="pal-btn" :disabled="loading">
          <span v-if="loading" class="pal-spin" />
          {{ loading ? '登入中…' : '登入' }}
        </button>
      </form>

      <div class="pal-links">
        <NuxtLink to="/pong-archive/register" class="pal-link">申請成為校對者 →</NuxtLink>
        <NuxtLink to="/pong-archive" class="pal-link">返回典藏首頁</NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup>
definePageMeta({ layout: 'pong-archive' })

import { reactive, ref } from 'vue'
import { usePongSession } from '~/composables/usePongSession'

const router = useRouter()
const { login, isLoggedIn } = usePongSession()

if (import.meta.client && isLoggedIn.value) {
  router.replace('/pong-archive')
}

const form = reactive({ email: '', password: '' })
const loading = ref(false)
const error = ref('')

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await login(form.email, form.password)
    router.push('/pong-archive')
  } catch (e) {
    error.value = e?.data?.message || e?.message || '登入失敗，請確認帳號密碼'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500&family=Noto+Serif+TC:wght@400;500;600&display=swap');

.pal-wrap {
  min-height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px 20px;
}

.pal-card {
  width: 100%;
  max-width: 420px;
  background-color: #F4F1EC;
  border: 1px solid #DDD8CF;
  border-radius: 6px;
  padding: 48px 40px 40px;
}

.pal-logo {
  text-align: center;
  margin-bottom: 32px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.pal-logo-zh {
  font-family: 'Noto Serif TC', serif;
  font-size: 0.95rem;
  font-weight: 500;
  color: #3A3025;
  letter-spacing: 0.1em;
}
.pal-logo-en {
  font-size: 0.62rem;
  font-weight: 300;
  color: #A09280;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.pal-title {
  font-family: 'Noto Serif TC', serif;
  font-size: 1.1rem;
  font-weight: 500;
  color: #2C2C2C;
  letter-spacing: 0.08em;
  margin: 0 0 28px;
  text-align: center;
}

.pal-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.pal-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.pal-label {
  font-size: 0.68rem;
  font-weight: 300;
  color: #8A8278;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.pal-input {
  background: #FDFCFA;
  border: 1px solid #C8BFB0;
  border-radius: 3px;
  padding: 10px 14px;
  font-family: 'Noto Sans TC', sans-serif;
  font-size: 0.88rem;
  font-weight: 300;
  color: #2C2C2C;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  width: 100%;
  box-sizing: border-box;
}
.pal-input:focus {
  border-color: #8A7E6E;
  box-shadow: 0 0 0 3px rgba(138,126,110,0.1);
}

.pal-error {
  font-size: 0.8rem;
  color: #8A3030;
  background-color: rgba(138,48,48,0.06);
  border: 1px solid rgba(138,48,48,0.2);
  border-radius: 3px;
  padding: 8px 12px;
  margin: 0;
  letter-spacing: 0.04em;
}

.pal-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 11px 20px;
  background-color: #5B3F2A;
  color: #fff;
  border: none;
  border-radius: 3px;
  font-family: 'Noto Sans TC', sans-serif;
  font-size: 0.85rem;
  font-weight: 400;
  letter-spacing: 0.1em;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-top: 4px;
}
.pal-btn:hover:not(:disabled) { background-color: #4A3020; }
.pal-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.pal-spin {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255,255,255,0.4);
  border-top-color: #fff;
  border-radius: 50%;
  animation: pal-spin 0.7s linear infinite;
  flex-shrink: 0;
}
@keyframes pal-spin { to { transform: rotate(360deg); } }

.pal-links {
  margin-top: 28px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}
.pal-link {
  font-size: 0.78rem;
  font-weight: 300;
  color: #8A8278;
  text-decoration: none;
  letter-spacing: 0.06em;
  transition: color 0.2s;
}
.pal-link:hover { color: #3A3025; }
</style>
