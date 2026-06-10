<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink :to="`/coach/${language}`" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">💬 情境實用句</span>
      <div class="ml-auto flex items-center gap-3">
        <CoachTimer :seconds="tracker.activeSeconds.value" />
      </div>
    </nav>

    <div class="flex-1 p-5 max-w-2xl mx-auto w-full space-y-4">
      <div v-if="!available && !loading" class="bg-white rounded-2xl border border-gray-100 p-8 text-center text-sm text-gray-500">情境實用句目前只有英文版。</div>

      <template v-else>
        <!-- 情境選擇 -->
        <div class="flex flex-wrap gap-1.5">
          <button @click="pick('all')" class="text-xs px-3 py-1.5 rounded-full border transition" :class="activeKey === 'all' ? 'bg-indigo-600 text-white border-indigo-600' : 'border-gray-200 text-gray-500'">🔀 綜合</button>
          <button v-for="s in scenarios" :key="s.key" @click="pick(s.key)" class="text-xs px-3 py-1.5 rounded-full border transition" :class="activeKey === s.key ? 'bg-indigo-600 text-white border-indigo-600' : 'border-gray-200 text-gray-500'">{{ s.icon }} {{ s.label.split(' ')[0] }}</button>
        </div>

        <!-- 模式 -->
        <div class="flex items-center gap-2">
          <button @click="mode = 'speak'" class="text-xs px-3 py-1.5 rounded-lg transition" :class="mode === 'speak' ? 'bg-violet-600 text-white' : 'bg-white border border-gray-200 text-gray-500'">🎙️ 口說</button>
          <button @click="mode = 'write'" class="text-xs px-3 py-1.5 rounded-lg transition" :class="mode === 'write' ? 'bg-violet-600 text-white' : 'bg-white border border-gray-200 text-gray-500'">✍️ 寫作</button>
          <span class="ml-auto text-xs text-gray-400">第 {{ idx + 1 }} 句 · 本回 {{ doneCount }} 句</span>
        </div>

        <!-- 練習卡 -->
        <div v-if="current" class="bg-white rounded-3xl border border-gray-100 shadow-sm p-6">
          <div class="text-[11px] text-gray-400 mb-1">{{ current._scenarioLabel }}</div>
          <div class="text-xs text-gray-400">情境 · 試著用英文{{ mode === 'speak' ? '說' : '寫' }}出來</div>
          <div class="text-lg font-bold text-gray-900 mt-1">{{ current.situation }}</div>

          <!-- 你的嘗試 -->
          <div class="mt-4">
            <div v-if="mode === 'speak'" class="flex items-center gap-2">
              <button v-if="sttSupported" @click="toggleMic" class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0" :class="listening ? 'bg-rose-500 text-white animate-pulse' : 'bg-violet-100 text-violet-600'">🎤</button>
              <div class="flex-1 text-sm text-gray-700 min-h-[2.5rem] px-3 py-2 rounded-lg bg-gray-50 border border-gray-100">{{ attempt || interim || '（按麥克風說說看，不會也沒關係，可直接看解答）' }}</div>
            </div>
            <textarea v-else v-model="attempt" rows="2" placeholder="試著用英文寫出來（不會也沒關係，可直接看解答）…" class="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm resize-none focus:outline-none focus:border-indigo-400" />
          </div>

          <!-- 建議解答 -->
          <button v-if="!revealed" @click="revealed = true" class="mt-4 w-full py-2.5 rounded-xl bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700 transition">💡 看建議解答</button>
          <div v-else class="mt-4 border-t border-gray-100 pt-4">
            <div class="bg-indigo-50/50 rounded-xl px-4 py-3">
              <div class="flex items-start gap-2">
                <div class="text-base text-gray-900 font-medium flex-1">{{ current.en }}</div>
                <button @click="speak(current.en)" class="text-gray-400 hover:text-indigo-600 flex-shrink-0">🔊</button>
              </div>
              <div class="text-sm text-gray-500 mt-1">{{ current.zh }}</div>
              <div v-if="current.note" class="text-[11px] text-indigo-500 mt-1.5">💡 {{ current.note }}</div>
            </div>

            <!-- 複述比對 -->
            <div v-if="repeatHeard" class="mt-2 text-xs px-3 py-2 rounded-lg" :class="repeatGood ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'">
              你說的：「{{ repeatHeard }}」{{ repeatGood ? ' ✓ 很接近！' : ' — 再聽一次模仿語調' }}
            </div>

            <div class="mt-3 flex flex-wrap gap-2">
              <button v-if="sttSupported" @click="repeat" class="text-xs px-3 py-1.5 rounded-lg bg-violet-600 text-white">🎙️ 複述一次</button>
              <button @click="similar" :disabled="loadingMore" class="text-xs px-3 py-1.5 rounded-lg bg-white border border-indigo-200 text-indigo-700 disabled:opacity-40">{{ loadingMore ? '生成中…' : '✨ 換類似句' }}</button>
              <button @click="next" class="ml-auto text-xs px-4 py-1.5 rounded-lg bg-indigo-600 text-white">下一句 →</button>
            </div>
          </div>
        </div>

        <div v-else-if="!loading" class="bg-white rounded-2xl border border-gray-100 p-8 text-center text-sm text-gray-500">選一個情境開始練習。</div>

        <p class="text-center text-[11px] text-gray-400">練到底會自動用 AI 補更多句子 · 與 <NuxtLink :to="`/coach/${language}/grammar`" class="text-indigo-500 hover:underline">文法課</NuxtLink>、<NuxtLink :to="`/coach/${language}/chat?mode=scenario`" class="text-indigo-500 hover:underline">情境角色</NuxtLink> 一起練更有效</p>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { authedFetch } from "~/composables/useAuthedFetch";
import { useCoachAi } from "~/composables/useCoachAi";
import { useSpeech } from "~/composables/useSpeech";
import { useActivityTracker } from "~/composables/useActivityTracker";

definePageMeta({ middleware: "coach-auth" });

const route = useRoute();
const language = computed(() => route.params.lang as string);
const { aiFetch } = useCoachAi();
const speech = useSpeech();
const tracker = useActivityTracker();
const sttSupported = speech.supported;
const listening = speech.listening;
const interim = speech.interim;

const loading = ref(true);
const available = ref(false);
const scenarios = ref<any[]>([]);
const activeKey = ref("all");
const queue = ref<any[]>([]);
const idx = ref(0);
const doneCount = ref(0);
const mode = ref<"speak" | "write">("speak");
const attempt = ref("");
const revealed = ref(false);
const loadingMore = ref(false);
const repeatHeard = ref("");
const repeatGood = ref(false);

const current = computed(() => queue.value[idx.value] || null);

function shuffle<T>(a: T[]): T[] { return [...a].sort(() => Math.random() - 0.5); }

function buildQueue(key: string) {
  let items: any[] = [];
  if (key === "all") {
    items = scenarios.value.flatMap((s) => s.items.map((it: any) => ({ ...it, _scenarioLabel: s.label, _key: s.key })));
    items = shuffle(items);
  } else {
    const s = scenarios.value.find((x) => x.key === key);
    items = s ? shuffle(s.items.map((it: any) => ({ ...it, _scenarioLabel: s.label, _key: s.key }))) : [];
  }
  queue.value = items;
  idx.value = 0;
  resetCard();
}

function resetCard() {
  attempt.value = "";
  revealed.value = false;
  repeatHeard.value = "";
  repeatGood.value = false;
  speech.stopListening();
}

function pick(key: string) {
  activeKey.value = key;
  doneCount.value = 0;
  buildQueue(key);
}

function speak(t: string) { speech.speak(t, "en-US"); }

function toggleMic() {
  if (listening.value) speech.stopListening();
  else speech.startListening("en-US", (t) => { attempt.value = (attempt.value ? attempt.value + " " : "") + t; });
}

// 複述：播放範例 → 聽使用者複述 → 簡單比對
function repeat() {
  if (!current.value) return;
  repeatHeard.value = "";
  speech.speak(current.value.en, "en-US");
  // 播完後開始聽（簡單延遲；使用者也可直接說）
  setTimeout(() => {
    speech.startListening("en-US", (t) => {
      repeatHeard.value = (repeatHeard.value ? repeatHeard.value + " " : "") + t;
      repeatGood.value = similarity(repeatHeard.value, current.value.en) >= 0.6;
    });
  }, Math.min(4000, (current.value.en.length / 12) * 1000 + 800));
}

// 粗略相似度（去標點小寫，共同字比例）
function similarity(a: string, b: string): number {
  const norm = (s: string) => s.toLowerCase().replace(/[^a-z\s]/g, "").split(/\s+/).filter(Boolean);
  const wa = norm(a), wb = new Set(norm(b));
  if (!wa.length) return 0;
  const hit = wa.filter((w) => wb.has(w)).length;
  return hit / Math.max(wa.length, wb.size);
}

async function next() {
  doneCount.value++;
  idx.value++;
  resetCard();
  // 練到接近底 → AI 補更多
  if (idx.value >= queue.value.length - 1) await loadMore();
}

async function loadMore() {
  if (loadingMore.value || activeKey.value === "all") {
    // 綜合模式練完就重洗
    if (activeKey.value === "all" && idx.value >= queue.value.length) buildQueue("all");
    return;
  }
  loadingMore.value = true;
  try {
    const seen = queue.value.map((q) => q.en);
    const { items } = await aiFetch<any>("/api/lang/sentences/more", {
      method: "POST",
      body: { language: language.value, scenario: activeKey.value, seen, count: 5 },
    });
    const s = scenarios.value.find((x) => x.key === activeKey.value);
    queue.value.push(...items.map((it: any) => ({ ...it, _scenarioLabel: s?.label || "", _key: activeKey.value })));
  } catch { /* 失敗就重洗既有 */ if (idx.value >= queue.value.length) buildQueue(activeKey.value); }
  finally { loadingMore.value = false; }
}

// 換類似句：在當前位置插入一句 AI 生成的同情境句
async function similar() {
  if (loadingMore.value) return;
  loadingMore.value = true;
  try {
    const { items } = await aiFetch<any>("/api/lang/sentences/more", {
      method: "POST",
      body: { language: language.value, scenario: activeKey.value === "all" ? current.value?._key : activeKey.value, seen: [current.value?.en], count: 1 },
    });
    if (items?.[0]) {
      queue.value.splice(idx.value + 1, 0, { ...items[0], _scenarioLabel: current.value?._scenarioLabel || "", _key: current.value?._key });
      idx.value++;
      resetCard();
    }
  } catch { /* ignore */ }
  finally { loadingMore.value = false; }
}

onMounted(async () => {
  tracker.start(language.value, mode.value === "speak" ? "speaking" : "writing", "sentences");
  try {
    const r = await authedFetch<any>(`/api/lang/sentences?language=${language.value}`);
    available.value = !!r.available;
    scenarios.value = r.scenarios || [];
    if (available.value) buildQueue("all");
  } finally {
    loading.value = false;
  }
});
</script>
