<template>
  <div class="min-h-screen bg-gradient-to-br from-amber-50 to-rose-50 flex items-center justify-center p-4">
    <div class="max-w-sm w-full bg-white rounded-2xl shadow-xl p-8 text-center space-y-4">
      <div class="text-5xl">🔒</div>
      <h1 class="text-lg font-bold text-gray-900">這台裝置尚未核准</h1>
      <p class="text-sm text-gray-600">
        為了安全，新裝置需要由你<b>已核准的管理裝置</b>（通常是你的電腦）核准後才能使用。
      </p>
      <div class="bg-gray-50 rounded-xl p-3 text-xs text-gray-500">
        本機：{{ deviceName }}
      </div>
      <p class="text-xs text-gray-400">
        請到你的電腦開啟「裝置管理」核准這台；核准後此頁會自動進入。
      </p>
      <div class="flex gap-2 pt-1">
        <button @click="recheck" :disabled="checking" class="flex-1 py-2 rounded-xl bg-indigo-600 text-white text-sm disabled:opacity-50">{{ checking ? '檢查中…' : '我已核准，重新檢查' }}</button>
        <button @click="logout" class="px-4 py-2 rounded-xl bg-white border border-gray-200 text-gray-500 text-sm">登出</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import { authedFetch } from "~/composables/useAuthedFetch";
import { getDeviceId, getDeviceName } from "~/composables/useDevice";

const supabase = useSupabaseClient();
const router = useRouter();
const deviceName = ref("");
const checking = ref(false);
let poll: any = null;

async function recheck() {
  checking.value = true;
  try {
    const r = await authedFetch<{ status: string }>("/api/devices/check", {
      method: "POST",
      body: { deviceId: getDeviceId(), name: getDeviceName(), userAgent: navigator.userAgent },
    });
    const status = useState<string>("deviceStatus", () => "");
    status.value = r.status;
    if (r.status === "approved") router.push("/");
  } finally {
    checking.value = false;
  }
}

async function logout() {
  await supabase.auth.signOut();
  router.push("/login");
}

onMounted(() => {
  deviceName.value = getDeviceName();
  poll = setInterval(recheck, 5000); // 每 5 秒自動檢查是否已被核准
});
onUnmounted(() => { if (poll) clearInterval(poll); });
</script>
