<template>
  <!-- dev-only 截圖 harness：讓 scripts/shot.mjs 不經登入截世界宗教地圖（生產環境 404） -->
  <div id="shot" class="w-[1500px] h-[860px] bg-white">
    <WorldThematicMap :current-year="year" />
  </div>
</template>

<script setup lang="ts">
import WorldThematicMap from '~/components/maps/WorldThematicMap.vue'

if (!import.meta.dev) {
  throw createError({ statusCode: 404, statusMessage: 'Not Found' })
}

const route = useRoute()
const year = Number(route.query.year ?? 2026)
</script>
