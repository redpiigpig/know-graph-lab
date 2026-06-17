<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader title="AI 語言教練" :back="{ to: `/coach/${language}`, label: '教練首頁' }" container-class="max-w-full" />
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink :to="`/coach/${language}`" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">✍️ 寫作批改</span>
      <div class="ml-auto"><CoachTimer :seconds="tracker.activeSeconds.value" /></div>
    </nav>

    <div class="flex-1 p-5 max-w-2xl mx-auto w-full space-y-4">
      <!-- 輸入 -->
      <div class="bg-white rounded-2xl border border-gray-100 p-5 space-y-3">
        <input v-model="prompt" placeholder="（可選）題目/情境，例：論述你對某議題的看法" class="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm focus:outline-none focus:border-indigo-400" />
        <textarea v-model="text" rows="7" placeholder="用英文寫一段（句子、段落、email、論述皆可）…" class="w-full px-3 py-2.5 rounded-lg border border-gray-200 text-sm resize-none focus:outline-none focus:border-indigo-400" />
        <div class="flex items-center gap-2 flex-wrap">
          <button v-if="ltSupported" @click="checkGrammar" :disabled="gtChecking || !text.trim()" class="px-4 py-2 rounded-xl bg-white border border-emerald-300 text-emerald-700 text-sm font-semibold disabled:opacity-40 hover:bg-emerald-50 transition">{{ gtChecking ? '檢查中…' : '🔍 文法檢查（零 AI）' }}</button>
          <button @click="correct" :disabled="correcting || !text.trim()" class="px-5 py-2 rounded-xl bg-indigo-600 text-white text-sm font-semibold disabled:opacity-40 hover:bg-indigo-700 transition">{{ correcting ? '批改中…' : '🧑‍🏫 AI 逐句批改' }}</button>
          <span v-if="res?.score !== null && res" class="ml-auto text-sm font-bold" :class="res.score >= 80 ? 'text-emerald-600' : res.score >= 60 ? 'text-amber-600' : 'text-rose-600'">{{ res.score }} 分</span>
        </div>
        <p v-if="err" class="text-xs text-rose-500">{{ err }}</p>
      </div>

      <!-- LanguageTool 規則式文法檢查（零 AI）-->
      <div v-if="gt" class="bg-white rounded-2xl border border-gray-100 p-5 space-y-3">
        <div class="flex items-center gap-2">
          <h2 class="text-xs font-semibold text-gray-400 uppercase">文法檢查 · LanguageTool（規則式，不用 AI）</h2>
          <span v-if="gt.available" class="ml-auto text-xs font-semibold" :class="gt.matches.length ? 'text-amber-600' : 'text-emerald-600'">{{ gt.matches.length ? gt.matches.length + ' 處建議' : '✓ 沒發現問題' }}</span>
        </div>
        <p v-if="!gt.available" class="text-xs text-gray-400">{{ gt.reason }}</p>
        <div v-for="(m, i) in gt.matches" :key="i" class="border-l-2 border-amber-300 pl-3 py-0.5">
          <div class="text-sm text-gray-700">
            <span class="text-rose-600 bg-rose-50 rounded px-1 line-through decoration-rose-300">{{ m.bad }}</span>
            <span v-if="m.replacements.length" class="text-emerald-700"> → {{ m.replacements.join(' / ') }}</span>
          </div>
          <div class="text-[11px] text-gray-500 mt-0.5">{{ m.message }}<span v-if="m.rule" class="text-gray-300"> · {{ m.rule }}</span></div>
        </div>
      </div>

      <!-- 批改結果 -->
      <template v-if="res">
        <div v-if="res.overall" class="bg-indigo-50/50 rounded-2xl border border-indigo-100 p-4 text-sm text-gray-700">{{ res.overall }}</div>

        <div v-if="res.sentences?.length" class="bg-white rounded-2xl border border-gray-100 p-5 space-y-3">
          <h2 class="text-xs font-semibold text-gray-400 uppercase">逐句</h2>
          <div v-for="(s, i) in res.sentences" :key="i" class="border-l-2 pl-3" :class="s.ok ? 'border-emerald-300' : 'border-rose-300'">
            <div v-if="!s.ok" class="text-sm text-rose-500 line-through decoration-rose-300">{{ s.original }}</div>
            <div class="text-sm" :class="s.ok ? 'text-gray-700' : 'text-emerald-700 font-medium'">{{ s.corrected }}</div>
            <div v-if="s.issue" class="text-[11px] text-gray-500 mt-0.5">💡 {{ s.issue }}</div>
          </div>
        </div>

        <div v-if="res.polished" class="bg-white rounded-2xl border border-gray-100 p-5">
          <div class="flex items-center gap-2 mb-1.5">
            <h2 class="text-xs font-semibold text-gray-400 uppercase">潤飾版</h2>
            <button v-if="ttsSupported" @click="speak(res.polished)" class="text-gray-300 hover:text-indigo-600 text-xs">🔊</button>
          </div>
          <div class="text-sm text-gray-800 leading-relaxed whitespace-pre-wrap">{{ res.polished }}</div>
        </div>
      </template>

      <p class="text-center text-[11px] text-gray-400">與 <NuxtLink :to="`/coach/${language}/sentences`" class="text-indigo-500 hover:underline">情境實用句／範文</NuxtLink>、<NuxtLink :to="`/coach/${language}/grammar`" class="text-indigo-500 hover:underline">文法課</NuxtLink> 一起練</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { useCoachAi } from "~/composables/useCoachAi";
import { useSpeech } from "~/composables/useSpeech";
import { useActivityTracker } from "~/composables/useActivityTracker";
import { authedFetch } from "~/composables/useAuthedFetch";

definePageMeta({ middleware: "coach-auth" });

const route = useRoute();
const language = computed(() => route.params.lang as string);
const { aiFetch } = useCoachAi();
const speech = useSpeech();
const tracker = useActivityTracker();
const ttsSupported = speech.ttsSupported;
const TTS: Record<string, string> = { en: "en-US", de: "de-DE", fr: "fr-FR", ja: "ja-JP", grc: "el-GR", la: "it-IT", hbo: "he-IL" };

const prompt = ref("");
const text = ref("");
const correcting = ref(false);
const res = ref<any>(null);
const err = ref("");
const gtChecking = ref(false);
const gt = ref<any>(null);
const LT_LANGS = ["en", "de", "fr", "es", "pt", "nl", "it", "ru", "pl", "ja", "zh"];
const ltSupported = computed(() => LT_LANGS.includes(language.value));

function speak(t: string) { speech.speak(t, TTS[language.value] || "en-US"); }

async function checkGrammar() {
  if (!text.value.trim() || gtChecking.value) return;
  gtChecking.value = true;
  gt.value = null;
  err.value = "";
  try {
    gt.value = await authedFetch<any>("/api/lang/grammar-check", { method: "POST", body: { language: language.value, text: text.value } });
  } catch (e: any) { err.value = e?.data?.message || "文法檢查失敗"; }
  finally { gtChecking.value = false; }
}

async function correct() {
  if (!text.value.trim() || correcting.value) return;
  correcting.value = true;
  err.value = "";
  res.value = null;
  try {
    res.value = await aiFetch<any>("/api/lang/writing/correct", { method: "POST", body: { language: language.value, text: text.value, prompt: prompt.value } });
  } catch (e: any) { err.value = e?.data?.message || "批改失敗，請重試"; }
  finally { correcting.value = false; }
}

onMounted(() => { tracker.start(language.value, "writing", "writing"); });
</script>
