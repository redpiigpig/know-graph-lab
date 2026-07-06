<template>
  <div class="sd-wrap sd-narrow">
    <div class="sd-panel sdl-card">
      <div class="sdl-head">
        <span class="sd-brand-star" aria-hidden="true">★</span>
        <p class="sd-eyebrow">REPORT FOR DUTY</p>
        <h1 class="sd-h sdl-title">登入報到</h1>
      </div>

      <div class="sdl-tabs">
        <button class="sdl-tab" :class="{ 'sdl-tab--on': mode === 'chief' }" @click="mode = 'chief'">教官（Email 驗證碼）</button>
        <button class="sdl-tab" :class="{ 'sdl-tab--on': mode === 'recruit' }" @click="mode = 'recruit'">兵員（代號登入）</button>
      </div>

      <!-- 教官：Email OTP -->
      <div v-if="mode === 'chief'" class="sdl-form">
        <template v-if="!codeSent">
          <div>
            <label class="sd-label">教官 Email</label>
            <input v-model="email" type="email" class="sd-input" placeholder="your@email.com" autocomplete="email" @keydown.enter="sendCode" />
          </div>
          <p v-if="error" class="sd-error">{{ error }}</p>
          <button class="sd-btn" :disabled="sending" @click="sendCode">{{ sending ? '寄送中…' : '✉️ 寄送驗證碼' }}</button>
        </template>
        <template v-else>
          <div>
            <label class="sd-label">Email 驗證碼</label>
            <input v-model="code" inputmode="numeric" maxlength="6" class="sd-input sdl-code" placeholder="000000" @keydown.enter="verifyChief" />
          </div>
          <p v-if="error" class="sd-error">{{ error }}</p>
          <button class="sd-btn" :disabled="verifying || code.length < 6" @click="verifyChief">{{ verifying ? '驗證中…' : '登入' }}</button>
          <div class="sdl-code-actions">
            <button class="sd-btn--link" @click="codeSent = false; code = ''; error = ''">← 改 Email</button>
            <button class="sd-btn--link" :disabled="sending" @click="sendCode">重新寄送</button>
          </div>
        </template>
        <p class="sdl-hint">登入一次後，這台裝置會長期保持登入，不必每次驗證。</p>
      </div>

      <!-- 兵員：代號 + 通行碼 -->
      <form v-else class="sdl-form" @submit.prevent="submitRecruit">
        <div>
          <label class="sd-label">代號 Callsign</label>
          <input v-model="callsign" class="sd-input" placeholder="兵員代號" autocomplete="username" />
        </div>
        <div>
          <label class="sd-label">通行碼 Access Code</label>
          <input v-model="rcode" type="password" class="sd-input" placeholder="通行碼" autocomplete="current-password" />
        </div>
        <p v-if="error" class="sd-error">{{ error }}</p>
        <button type="submit" class="sd-btn" :disabled="loading">{{ loading ? '驗證中…' : '登入' }}</button>
      </form>
    </div>

    <p class="sdl-note">兵員帳號一律由教官建立配發，請洽教官。</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useSoldierSession } from '~/composables/useSoldierSession'

definePageMeta({ layout: 'soldier-diary' })
useHead({ title: '登入 — 大兵日記' })

const supabase = useSupabaseClient()
const { login, loginChiefWithSupabaseToken } = useSoldierSession()

const mode = ref<'chief' | 'recruit'>('chief')
const error = ref('')

// 教官 Email OTP
const email = ref('redpiigpig@gmail.com')
const code = ref('')
const sending = ref(false)
const verifying = ref(false)
const codeSent = ref(false)

async function sendCode() {
  if (!email.value.trim()) { error.value = '請輸入 Email'; return }
  sending.value = true; error.value = ''
  const { error: e } = await supabase.auth.signInWithOtp({
    email: email.value.trim(),
    options: { shouldCreateUser: false },
  })
  sending.value = false
  if (e) {
    error.value = /signups? not allowed/i.test(e.message) ? '此 Email 不在授權名單，或拼錯了' : e.message
  } else {
    codeSent.value = true
  }
}

async function verifyChief() {
  if (code.value.length < 6) return
  verifying.value = true; error.value = ''
  const { error: e } = await supabase.auth.verifyOtp({
    email: email.value.trim(), token: code.value.trim(), type: 'email',
  })
  if (e) {
    verifying.value = false
    error.value = e.message === 'Token has expired or is invalid' ? '驗證碼錯誤或已過期' : e.message
    return
  }
  try {
    const { data } = await supabase.auth.getSession()
    const at = data.session?.access_token
    if (!at) throw new Error('取得登入憑證失敗')
    await loginChiefWithSupabaseToken(at)
    await navigateTo('/soldier-diary/barracks')
  } catch (err: any) {
    error.value = err?.data?.message || err?.message || '教官登入失敗'
  } finally {
    verifying.value = false
  }
}

// 兵員登入
const callsign = ref('')
const rcode = ref('')
const loading = ref(false)

async function submitRecruit() {
  error.value = ''
  if (!callsign.value.trim() || !rcode.value) { error.value = '請輸入代號與通行碼'; return }
  loading.value = true
  try {
    const s = await login(callsign.value.trim(), rcode.value)
    await navigateTo(s.role === 'chief' ? '/soldier-diary/barracks' : '/soldier-diary/diary')
  } catch (e: any) {
    error.value = e?.data?.message || e?.message || '登入失敗'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.sdl-card { max-width: 480px; margin: 40px auto 0; padding: 30px 32px 28px; }
.sdl-head { text-align: center; margin-bottom: 20px; }
.sdl-title { font-size: 1.4rem; margin: 8px 0 0; }
.sd-brand-star { color: var(--sd-brass); font-size: 1.1rem; }

.sdl-tabs { display: flex; gap: 6px; margin-bottom: 22px; }
.sdl-tab { flex: 1; padding: 9px 8px; background: #171a11; border: 1px solid var(--sd-line); border-radius: 3px; color: var(--sd-khaki); font-size: 0.8rem; font-weight: 700; letter-spacing: 0.04em; cursor: pointer; }
.sdl-tab--on { background: var(--sd-olive); color: #12140d; border-color: var(--sd-olive-bright); }

.sdl-form { display: flex; flex-direction: column; gap: 16px; }
.sdl-form .sd-btn { margin-top: 2px; }
.sdl-code { text-align: center; font-size: 1.6rem; letter-spacing: 0.5em; font-family: monospace; }
.sdl-code-actions { display: flex; justify-content: space-between; }
.sd-btn--link { background: none; border: none; color: var(--sd-muted); font-size: 0.76rem; cursor: pointer; }
.sd-btn--link:hover { color: var(--sd-olive-bright); }
.sd-btn--link:disabled { opacity: 0.5; cursor: not-allowed; }
.sdl-hint { color: var(--sd-muted); font-size: 0.72rem; letter-spacing: 0.03em; margin: 2px 0 0; text-align: center; }
.sdl-note { text-align: center; color: var(--sd-muted); font-size: 0.76rem; margin-top: 18px; letter-spacing: 0.04em; }
</style>
