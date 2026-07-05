<template>
  <div class="sd-wrap sd-narrow">
    <div class="sd-panel sdl-card">
      <div class="sdl-head">
        <span class="sd-brand-star" aria-hidden="true">★</span>
        <p class="sd-eyebrow">REPORT FOR DUTY</p>
        <h1 class="sd-h sdl-title">登入報到</h1>
        <p class="sd-sub">兵員以代號與通行碼登入；教官以專屬代號進入營區。</p>
      </div>

      <form class="sdl-form" @submit.prevent="submit">
        <div>
          <label class="sd-label">代號 Callsign</label>
          <input v-model="callsign" class="sd-input" placeholder="兵員代號，或教官代號" autocomplete="username" />
        </div>
        <div>
          <label class="sd-label">通行碼 Access Code</label>
          <input v-model="code" type="password" class="sd-input" placeholder="通行碼" autocomplete="current-password" />
        </div>

        <p v-if="error" class="sd-error">{{ error }}</p>

        <button type="submit" class="sd-btn" :disabled="loading">
          {{ loading ? '驗證中…' : '登入' }}
        </button>
      </form>
    </div>

    <p class="sdl-note">
      沒有帳號？本系統採小隊制，帳號一律由教官建立配發，請洽教官。
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useSoldierSession } from '~/composables/useSoldierSession'

definePageMeta({ layout: 'soldier-diary' })
useHead({ title: '登入 — 大兵日記' })

const { login } = useSoldierSession()
const callsign = ref('')
const code = ref('')
const loading = ref(false)
const error = ref('')

async function submit() {
  error.value = ''
  if (!callsign.value.trim() || !code.value) { error.value = '請輸入代號與通行碼'; return }
  loading.value = true
  try {
    const s = await login(callsign.value.trim(), code.value)
    await navigateTo(s.role === 'chief' ? '/soldier-diary/barracks' : '/soldier-diary/diary')
  } catch (e: any) {
    error.value = e?.data?.message || e?.message || '登入失敗'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.sdl-card { max-width: 460px; margin: 40px auto 0; padding: 34px 34px 30px; }
.sdl-head { text-align: center; margin-bottom: 24px; }
.sdl-title { font-size: 1.4rem; margin: 8px 0 8px; }
.sdl-form { display: flex; flex-direction: column; gap: 16px; }
.sdl-form .sd-btn { margin-top: 4px; }
.sdl-note { text-align: center; color: var(--sd-muted); font-size: 0.76rem; margin-top: 18px; letter-spacing: 0.04em; }
.sd-brand-star { color: var(--sd-brass); font-size: 1.1rem; }
</style>
