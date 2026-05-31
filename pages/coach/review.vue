<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink to="/coach/dashboard" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">單字複習</span>
      <select v-model="language" @change="reload" class="ml-auto text-xs border border-gray-200 rounded-lg px-2 py-1">
        <option value="en">英文</option>
        <option value="ja">日文</option>
      </select>
    </nav>

    <div class="flex-1 p-5 max-w-2xl mx-auto w-full">
      <!-- 複習卡 -->
      <div v-if="current" class="bg-white rounded-3xl border border-gray-100 shadow-sm p-8 text-center">
        <div class="text-xs text-gray-400 mb-4">剩餘 {{ queue.length }} 張 · 今日已複習 {{ reviewed }}</div>
        <div class="text-3xl font-bold text-gray-900">{{ current.word }}</div>
        <div v-if="current.reading" class="text-sm text-gray-400 mt-1">{{ current.reading }}</div>
        <button v-if="speech.ttsSupported.value" @click="speak" class="mt-2 text-gray-300 hover:text-indigo-500 transition">🔊 發音</button>

        <Transition name="fade">
          <div v-if="revealed" class="mt-5 pt-5 border-t border-gray-100">
            <div class="text-lg text-gray-800">{{ current.meaning }}</div>
            <div v-if="current.example" class="text-sm text-gray-400 mt-2 italic">{{ current.example }}</div>
          </div>
        </Transition>

        <div class="mt-7">
          <button v-if="!revealed" @click="revealed = true" class="px-8 py-3 rounded-2xl bg-indigo-600 text-white font-semibold hover:bg-indigo-700 transition">顯示答案</button>
          <div v-else class="grid grid-cols-4 gap-2">
            <button @click="grade(2)" class="py-3 rounded-xl bg-rose-50 text-rose-700 text-sm font-medium hover:bg-rose-100 transition">再來一次<span class="block text-[10px] opacity-60">1天</span></button>
            <button @click="grade(3)" class="py-3 rounded-xl bg-amber-50 text-amber-700 text-sm font-medium hover:bg-amber-100 transition">困難</button>
            <button @click="grade(4)" class="py-3 rounded-xl bg-sky-50 text-sky-700 text-sm font-medium hover:bg-sky-100 transition">良好</button>
            <button @click="grade(5)" class="py-3 rounded-xl bg-emerald-50 text-emerald-700 text-sm font-medium hover:bg-emerald-100 transition">簡單</button>
          </div>
        </div>
      </div>

      <!-- 沒有到期單字 -->
      <div v-else-if="!loading" class="bg-white rounded-3xl border border-gray-100 p-10 text-center">
        <div class="text-4xl mb-3">🎉</div>
        <div class="font-semibold text-gray-800">今日複習完成！</div>
        <p class="text-sm text-gray-400 mt-1">沒有到期的單字了。可以生成新的學術單字組繼續學。</p>
      </div>

      <!-- 生成新單字組 -->
      <div class="mt-6 bg-white rounded-2xl border border-gray-100 p-5">
        <h2 class="text-sm font-semibold text-gray-800 mb-1">生成學術單字組</h2>
        <p class="text-xs text-gray-400 mb-3">依你的程度與人文興趣生成；自動加入複習排程。</p>
        <div class="flex flex-wrap gap-1.5 mb-3">
          <button v-for="p in PRESETS" :key="p" @click="theme = p" class="text-xs px-2.5 py-1 rounded-full border transition" :class="theme === p ? 'bg-indigo-50 border-indigo-300 text-indigo-700' : 'border-gray-200 text-gray-500'">{{ p }}</button>
        </div>
        <div class="flex gap-2">
          <input v-model="theme" placeholder="主題，如：GRE 哲學高頻字 / AWL Sublist 1 / 歷史學術用語" class="flex-1 px-3 py-2 rounded-lg border border-gray-200 text-sm focus:outline-none focus:border-indigo-400" />
          <button @click="generate" :disabled="generating || !theme.trim()" class="px-4 py-2 rounded-lg bg-indigo-600 text-white text-sm disabled:opacity-40 hover:bg-indigo-700 transition whitespace-nowrap">{{ generating ? '生成中…' : '生成' }}</button>
        </div>
        <p v-if="genMsg" class="text-xs text-emerald-600 mt-2">{{ genMsg }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { authedFetch } from "~/composables/useAuthedFetch";
import { useSpeech } from "~/composables/useSpeech";
import { useCoachAi } from "~/composables/useCoachAi";

definePageMeta({ middleware: "coach-auth" });

const { aiFetch } = useCoachAi();

const PRESETS = ["AWL Sublist 1", "GRE 高頻字", "哲學學術用語", "歷史學術用語", "神學術語", "文學批評術語", "學術寫作連接詞"];
const TTS_LANG: Record<string, string> = { en: "en-US", ja: "ja-JP" };

const language = ref("en");
const queue = ref<any[]>([]);
const revealed = ref(false);
const reviewed = ref(0);
const loading = ref(true);
const theme = ref("");
const generating = ref(false);
const genMsg = ref("");
const speech = useSpeech();

const current = computed(() => queue.value[0] || null);

async function reload() {
  loading.value = true;
  revealed.value = false;
  reviewed.value = 0;
  const { due } = await authedFetch<{ due: any[] }>(`/api/lang/vocab/review?language=${language.value}&limit=40`);
  queue.value = due;
  loading.value = false;
}

async function grade(q: number) {
  const card = current.value;
  if (!card) return;
  queue.value.shift();
  revealed.value = false;
  reviewed.value++;
  try {
    await authedFetch("/api/lang/vocab/review", { method: "POST", body: { id: card.id, quality: q } });
  } catch {
    /* 失敗就算了，下次到期再複習 */
  }
}

function speak() {
  if (current.value) speech.speak(current.value.word, TTS_LANG[language.value] || "en-US");
}

async function generate() {
  generating.value = true;
  genMsg.value = "";
  try {
    const res = await aiFetch<any>("/api/lang/vocab/generate", {
      method: "POST",
      body: { language: language.value, theme: theme.value, count: 15 },
    });
    genMsg.value = `已加入 ${res.added} 個新單字（${res.theme}），開始複習吧！`;
    await reload();
  } catch (e: any) {
    genMsg.value = e?.data?.message || "生成失敗";
  } finally {
    generating.value = false;
  }
}

onMounted(reload);
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from,
.fade-leave-to { opacity: 0; }
</style>
