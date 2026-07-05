<template>
  <div class="sd-app">
    <header class="sd-topbar">
      <div class="sd-topbar-inner">
        <NuxtLink to="/experiments" class="sd-back">← 實驗網站</NuxtLink>

        <NuxtLink to="/soldier-diary" class="sd-brand">
          <span class="sd-brand-star" aria-hidden="true">★</span>
          <span class="sd-brand-zh">大兵日記</span>
          <span class="sd-brand-en">A SOLDIER'S DIARY</span>
        </NuxtLink>

        <div class="sd-topbar-actions">
          <template v-if="isLoggedIn">
            <span class="sd-role" :class="isChief ? 'sd-role--chief' : 'sd-role--recruit'">
              {{ isChief ? '教官' : session?.callsign }}
            </span>
            <button class="sd-logout" @click="doLogout">登出</button>
          </template>
          <NuxtLink v-else to="/soldier-diary/login" class="sd-login-link">登入</NuxtLink>
        </div>
      </div>
    </header>

    <main class="sd-main">
      <slot />
    </main>

    <footer class="sd-footer">
      <span>大兵日記 · 軍事化自律養成模擬系統</span>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { useSoldierSession } from '~/composables/useSoldierSession'

const { session, isLoggedIn, isChief, logout, loadSession } = useSoldierSession()

onMounted(() => loadSession())

async function doLogout() {
  logout()
  await navigateTo('/soldier-diary/login')
}
</script>

<style>
/* 非 scoped：命名空間全掛在 .sd-app 底下，供各頁共用 */
@import url('https://fonts.googleapis.com/css2?family=Stardos+Stencil:wght@400;700&family=Noto+Sans+TC:wght@400;500;700;900&display=swap');

.sd-app {
  --sd-field: #14160f;
  --sd-panel: #1e2216;
  --sd-panel-2: #262b1b;
  --sd-line: #3a4128;
  --sd-olive: #7a8b3f;
  --sd-olive-bright: #a6bd54;
  --sd-khaki: #c9c4a8;
  --sd-sand: #e9e4d1;
  --sd-brass: #cBA43a;
  --sd-muted: #8b886e;
  --sd-red: #c05236;

  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--sd-field);
  background-image:
    linear-gradient(0deg, rgba(0,0,0,0.35), rgba(0,0,0,0.35)),
    repeating-linear-gradient(45deg, #171a11 0 22px, #191c12 22px 44px);
  color: var(--sd-khaki);
  font-family: 'Noto Sans TC', system-ui, sans-serif;
  letter-spacing: 0.02em;
}

/* ── Topbar ── */
.sd-topbar {
  position: sticky; top: 0; z-index: 40;
  background: linear-gradient(180deg, #23281a, #1a1e13);
  border-bottom: 2px solid var(--sd-olive);
  box-shadow: 0 2px 0 #0d0f09, 0 6px 18px rgba(0,0,0,0.4);
}
.sd-topbar-inner {
  max-width: 1120px; margin: 0 auto; height: 58px; padding: 0 20px;
  display: flex; align-items: center; justify-content: space-between; gap: 16px;
}
.sd-back {
  font-size: 0.8rem; color: var(--sd-muted); text-decoration: none;
  white-space: nowrap; transition: color 0.15s;
}
.sd-back:hover { color: var(--sd-olive-bright); }
.sd-brand {
  display: flex; align-items: baseline; gap: 8px; text-decoration: none;
  position: absolute; left: 50%; transform: translateX(-50%);
}
.sd-brand-star { color: var(--sd-brass); font-size: 0.9rem; }
.sd-brand-zh {
  font-weight: 900; font-size: 1.12rem; color: var(--sd-sand);
  letter-spacing: 0.16em;
}
.sd-brand-en {
  font-family: 'Stardos Stencil', sans-serif; font-size: 0.62rem;
  color: var(--sd-olive); letter-spacing: 0.18em;
}
.sd-topbar-actions { display: flex; align-items: center; gap: 12px; margin-left: auto; }
.sd-role {
  font-size: 0.72rem; font-weight: 700; letter-spacing: 0.08em;
  padding: 3px 10px; border-radius: 2px; border: 1px solid;
}
.sd-role--chief { color: var(--sd-brass); border-color: var(--sd-brass); background: rgba(203,164,58,0.08); }
.sd-role--recruit { color: var(--sd-olive-bright); border-color: var(--sd-olive); background: rgba(122,139,63,0.1); }
.sd-logout, .sd-login-link {
  font-size: 0.76rem; color: var(--sd-khaki); background: none; border: none;
  cursor: pointer; text-decoration: none; transition: color 0.15s;
}
.sd-logout:hover, .sd-login-link:hover { color: var(--sd-red); }

.sd-main { flex: 1; width: 100%; }
.sd-footer {
  text-align: center; padding: 22px; font-size: 0.68rem; color: var(--sd-muted);
  letter-spacing: 0.12em; border-top: 1px solid var(--sd-line);
}

/* ── 共用元件 ── */
.sd-app .sd-wrap { max-width: 1120px; margin: 0 auto; padding: 28px 20px 48px; }
.sd-app .sd-narrow { max-width: 720px; }

.sd-app .sd-panel {
  background: var(--sd-panel);
  border: 1px solid var(--sd-line);
  border-radius: 4px;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
}
.sd-app .sd-panel--raised { background: var(--sd-panel-2); }

.sd-app .sd-eyebrow {
  font-family: 'Stardos Stencil', sans-serif;
  font-size: 0.66rem; letter-spacing: 0.24em; text-transform: uppercase;
  color: var(--sd-olive);
}
.sd-app .sd-h {
  font-weight: 900; color: var(--sd-sand); letter-spacing: 0.1em; margin: 0;
}
.sd-app .sd-sub { color: var(--sd-muted); font-size: 0.82rem; letter-spacing: 0.04em; }

.sd-app .sd-btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  padding: 10px 22px; border-radius: 3px; cursor: pointer;
  font-family: 'Noto Sans TC', sans-serif; font-size: 0.86rem; font-weight: 700;
  letter-spacing: 0.1em; text-decoration: none;
  background: var(--sd-olive); color: #12140d; border: 1px solid var(--sd-olive-bright);
  transition: filter 0.15s, transform 0.05s;
}
.sd-app .sd-btn:hover:not(:disabled) { filter: brightness(1.12); }
.sd-app .sd-btn:active:not(:disabled) { transform: translateY(1px); }
.sd-app .sd-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.sd-app .sd-btn--ghost {
  background: transparent; color: var(--sd-khaki); border: 1px solid var(--sd-line);
}
.sd-app .sd-btn--ghost:hover { border-color: var(--sd-olive); color: var(--sd-sand); }
.sd-app .sd-btn--danger { background: var(--sd-red); border-color: #d5654a; color: #fff; }
.sd-app .sd-btn--sm { padding: 6px 14px; font-size: 0.76rem; }

.sd-app .sd-label {
  display: block; font-size: 0.68rem; font-weight: 700; letter-spacing: 0.12em;
  text-transform: uppercase; color: var(--sd-muted); margin-bottom: 6px;
}
.sd-app .sd-input, .sd-app .sd-textarea, .sd-app .sd-select {
  width: 100%; box-sizing: border-box;
  background: #12140d; border: 1px solid var(--sd-line); border-radius: 3px;
  padding: 10px 12px; color: var(--sd-sand); font-family: inherit; font-size: 0.9rem;
  outline: none; transition: border-color 0.15s, box-shadow 0.15s;
}
.sd-app .sd-input:focus, .sd-app .sd-textarea:focus, .sd-app .sd-select:focus {
  border-color: var(--sd-olive); box-shadow: 0 0 0 3px rgba(122,139,63,0.15);
}
.sd-app .sd-textarea { resize: vertical; min-height: 70px; line-height: 1.7; }

.sd-app .sd-error {
  font-size: 0.82rem; color: #f0b8a8; background: rgba(192,82,54,0.12);
  border: 1px solid rgba(192,82,54,0.35); border-radius: 3px; padding: 8px 12px;
}
.sd-app .sd-ok {
  font-size: 0.82rem; color: #cbe08a; background: rgba(122,139,63,0.14);
  border: 1px solid rgba(122,139,63,0.4); border-radius: 3px; padding: 8px 12px;
}
</style>
