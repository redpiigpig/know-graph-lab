<template>
  <nav class="psmt-tabs">
    <NuxtLink
      v-for="t in tabs"
      :key="t.path"
      :to="t.path"
      class="psmt-tab"
      :class="{ 'psmt-tab--active': isActive(t.path) }"
    >{{ t.label }}</NuxtLink>
  </nav>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()

const tabs = [
  { path: '/pong-archive/sermons',             label: '年份', match: /^\/pong-archive\/sermons(?:\/year(?:\/|$)|\/?$)/ },
  { path: '/pong-archive/sermons/by/location', label: '地點', match: /^\/pong-archive\/sermons\/by\/location/ },
  { path: '/pong-archive/sermons/by/type',     label: '類型', match: /^\/pong-archive\/sermons\/by\/type/ },
]

function isActive(path) {
  const t = tabs.find(x => x.path === path)
  return t ? t.match.test(route.path) : false
}
</script>

<style scoped>
.psmt-tabs {
  display: flex;
  justify-content: center;
  gap: 4px;
  padding: 0 24px 28px;
  border-bottom: 1px solid #E8E4DC;
}
.psmt-tab {
  background: transparent;
  border: none;
  padding: 8px 22px 10px;
  font-family: 'Noto Sans TC', sans-serif;
  font-size: 0.85rem;
  font-weight: 400;
  color: #8A8278;
  letter-spacing: 0.12em;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: color 0.15s, border-color 0.15s;
  text-decoration: none;
}
.psmt-tab:hover { color: #3A3025; }
.psmt-tab--active { color: #3A3025; border-bottom-color: #C4B89A; }

@media (max-width: 640px) {
  .psmt-tabs { padding: 0 16px 20px; gap: 0; }
  .psmt-tab { padding: 8px 14px 10px; font-size: 0.8rem; letter-spacing: 0.08em; }
}
</style>
