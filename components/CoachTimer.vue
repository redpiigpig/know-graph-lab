<!-- 語言教練各互動頁共用的「本次練習時間」計時器徽章。
     傳入 useActivityTracker() 的 activeSeconds（從開始互動累計、分頁隱藏會暫停）。 -->
<template>
  <span class="text-xs px-2 py-1 rounded-lg bg-indigo-50 text-indigo-600 tabular-nums whitespace-nowrap" title="本次練習時間（分頁切走會暫停）">⏱ {{ mmss }}</span>
</template>

<script setup lang="ts">
import { computed, unref } from "vue";
const props = defineProps<{ seconds: number }>();
const mmss = computed(() => {
  // 防呆：若不慎傳進 ref 物件或非數字，unref + Number.isFinite 仍給出 0:00 而非 NaN:NaN
  const n = Number(unref(props.seconds as any));
  const s = Number.isFinite(n) ? Math.max(0, Math.floor(n)) : 0;
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
});
</script>
