<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink to="/" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">裝置管理</span>
    </nav>

    <div class="flex-1 p-5 max-w-2xl mx-auto w-full">
      <p class="text-sm text-gray-500 mb-4">只有「已核准」的裝置能登入使用。新裝置登入後會列在這裡，需由已核准裝置核准。撤銷後該裝置會被擋下。</p>

      <div v-if="loading" class="text-gray-400 text-sm">載入中…</div>

      <div v-else class="space-y-2">
        <div v-for="d in devices" :key="d.device_id" class="bg-white rounded-2xl border border-gray-100 p-4 flex items-center gap-3">
          <div class="text-2xl">{{ icon(d) }}</div>
          <div class="flex-1 min-w-0">
            <div class="text-sm font-medium text-gray-800 flex items-center gap-2">
              {{ d.name || '未知裝置' }}
              <span v-if="d.device_id === myId" class="text-[10px] px-1.5 py-0.5 rounded-full bg-indigo-50 text-indigo-700">這台</span>
            </div>
            <div class="text-[11px] text-gray-400">最後使用 {{ fmt(d.last_seen) }}</div>
          </div>
          <span class="text-[11px] px-2 py-0.5 rounded-full" :class="badge(d.status)">{{ label(d.status) }}</span>
          <div class="flex gap-1">
            <button v-if="d.status !== 'approved'" @click="setStatus(d, 'approved')" class="text-xs px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-700 hover:bg-emerald-100 transition">核准</button>
            <button v-if="d.status === 'approved' && d.device_id !== myId" @click="setStatus(d, 'revoked')" class="text-xs px-2.5 py-1 rounded-lg bg-rose-50 text-rose-600 hover:bg-rose-100 transition">撤銷</button>
            <button v-if="d.status === 'revoked'" @click="setStatus(d, 'approved')" class="text-xs px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-700 hover:bg-emerald-100 transition">恢復</button>
          </div>
        </div>
        <p v-if="!devices.length" class="text-gray-300 text-sm text-center py-8">尚無裝置紀錄</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { authedFetch } from "~/composables/useAuthedFetch";
import { getDeviceId } from "~/composables/useDevice";

definePageMeta({ middleware: "auth" });

const devices = ref<any[]>([]);
const loading = ref(true);
const myId = ref("");

function icon(d: any) {
  const ua = (d.user_agent || "") + (d.name || "");
  if (/iPhone|Android|Mobile/i.test(ua)) return "📱";
  if (/iPad|Tablet/i.test(ua)) return "📲";
  return "💻";
}
function label(s: string) { return ({ approved: "已核准", pending: "待核准", revoked: "已撤銷" } as any)[s] || s; }
function badge(s: string) {
  return s === "approved" ? "bg-emerald-50 text-emerald-700" : s === "pending" ? "bg-amber-50 text-amber-700" : "bg-rose-50 text-rose-600";
}
function fmt(s: string) { return s ? new Date(s).toLocaleString("zh-TW", { month: "numeric", day: "numeric", hour: "2-digit", minute: "2-digit" }) : ""; }

async function load() {
  loading.value = true;
  try {
    const { devices: d } = await authedFetch<any>("/api/devices");
    devices.value = d;
  } finally {
    loading.value = false;
  }
}

async function setStatus(d: any, status: string) {
  if (status === "revoked" && !confirm(`撤銷「${d.name}」？該裝置將無法再登入使用。`)) return;
  try {
    await authedFetch(`/api/devices/${encodeURIComponent(d.device_id)}`, {
      method: "PATCH",
      body: { status, actingDeviceId: myId.value },
    });
    await load();
  } catch (e: any) {
    alert(e?.data?.message || "操作失敗");
  }
}

onMounted(() => {
  myId.value = getDeviceId();
  load();
});
</script>
