<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader title="AI 語言教練" :back="{ to: `/coach/${lang}`, label: '教練首頁' }" container-class="max-w-full" />
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink :to="`/coach/${lang}`" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-xl">{{ coach?.emoji }}</span>
      <span class="text-sm font-semibold text-gray-900">課程複習 · {{ coach?.langLabel }}</span>
      <div class="ml-auto"><CoachTimer :seconds="tracker.activeSeconds.value" /></div>
    </nav>

    <div class="flex-1 p-5 max-w-4xl mx-auto w-full space-y-4">
      <div v-if="loading" class="text-sm text-gray-400 py-10 text-center">載入中…</div>
      <div v-else-if="!spec" class="text-sm text-gray-500 py-10 text-center">這個語言還沒有課程複習內容。</div>

      <template v-else>
        <!-- 標題 + 課次選擇 -->
        <div class="bg-white rounded-2xl border border-gray-100 p-4">
          <h1 class="text-lg font-bold text-gray-900">{{ spec.title }}</h1>
          <p class="text-xs text-gray-500 mt-1 leading-relaxed">{{ spec.intro }}</p>
          <div class="flex flex-wrap gap-2 mt-3">
            <button v-for="(l, i) in spec.lessons" :key="l.id" @click="selectLesson(i)"
              class="text-xs px-3 py-1.5 rounded-lg border transition"
              :class="lessonIdx === i ? 'bg-indigo-600 border-indigo-600 text-white' : 'bg-white border-gray-200 text-gray-600 hover:border-indigo-300'">
              第 {{ l.no }} 課
            </button>
          </div>
          <div class="mt-2 text-sm font-semibold text-gray-800">{{ lesson.title }}</div>
          <div v-if="lesson.subtitle" class="text-[11px] text-gray-400">{{ lesson.subtitle }}</div>
        </div>

        <!-- 分頁 -->
        <div class="flex flex-wrap gap-2">
          <button @click="tab = 'phon'" :class="tabClass('phon')">🔡 母音子音</button>
          <button @click="tab = 'vocab'" :class="tabClass('vocab')">📇 單字</button>
          <button @click="tab = 'read'; resetRead()" :class="tabClass('read')">👁️ 認讀</button>
          <button @click="tab = 'dict'; resetDict()" :class="tabClass('dict')">✍️ 聽寫</button>
          <button @click="tab = 'say'; resetSay()" :class="tabClass('say')">🎤 發音跟讀</button>
        </div>

        <!-- ░░ 母音子音複習 ░░ -->
        <template v-if="tab === 'phon'">
          <div v-for="sec in phonSections" :key="sec.title" class="bg-white rounded-2xl border border-gray-100 p-4">
            <div class="flex items-baseline gap-2 mb-2">
              <h2 class="text-sm font-semibold text-gray-800">{{ sec.title }}</h2>
              <span v-if="sec.note" class="text-[11px] text-gray-400">{{ sec.note }}</span>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <div v-for="(l, i) in sec.items" :key="i"
                class="text-left bg-slate-50 border border-gray-100 rounded-xl p-2.5">
                <button type="button" @click="speakPhone(l)" :title="`朗讀 ${l.form} 的發音`"
                  class="flex items-baseline gap-2 rounded-lg -mx-1 px-1 hover:bg-indigo-50 transition group">
                  <span class="text-lg font-semibold text-gray-900 leading-none group-hover:text-indigo-700">{{ l.form }}</span>
                  <span class="text-sm text-indigo-600">{{ l.sound }}</span>
                  <span class="text-xs text-gray-300 group-hover:text-indigo-500" aria-hidden="true">🔊</span>
                </button>
                <div v-if="l.rule" class="text-[11px] text-gray-500 mt-1">{{ l.rule }}</div>
                <div v-if="l.examples" class="flex flex-wrap items-center gap-1.5 mt-2">
                  <span class="text-[11px] text-gray-400">例：</span>
                  <button v-for="word in splitExamples(l.examples)" :key="word"
                    type="button" @click="speakWord(word)"
                    class="px-2 py-1 rounded-md bg-white border border-gray-200 text-xs text-gray-700 hover:text-indigo-700 hover:border-indigo-300 hover:bg-indigo-50 transition"
                    :title="`朗讀 ${word}`">
                    {{ word }} <span aria-hidden="true">🔊</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </template>

        <!-- ░░ 單字（翻卡）░░ -->
        <template v-else-if="tab === 'vocab'">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            <button v-for="(v, i) in lesson.vocab" :key="i" @click="flip(i)"
              class="text-left bg-white hover:bg-indigo-50 border border-gray-100 hover:border-indigo-200 rounded-xl p-3 transition group">
              <div class="flex items-start gap-2">
                <div class="flex-1 min-w-0">
                  <div class="text-base font-semibold text-gray-900 break-words">{{ v.latin }}</div>
                  <div class="text-sm mt-1" :class="flipped.has(i) ? 'text-indigo-700' : 'text-transparent select-none'">
                    {{ flipped.has(i) ? v.zh : '點卡片看中文' }}
                  </div>
                  <div v-if="v.note && flipped.has(i)" class="text-[11px] text-gray-400 mt-0.5">{{ v.note }}</div>
                </div>
                <span @click.stop="speakWord(v.latin)" class="text-gray-300 group-hover:text-indigo-500 text-base shrink-0" title="朗讀">🔊</span>
              </div>
            </button>
          </div>
          <div class="text-center">
            <button @click="flipAll" class="text-xs text-gray-400 hover:text-indigo-600 underline">
              {{ flipped.size === lesson.vocab.length ? '全部蓋回' : '全部翻開' }}
            </button>
          </div>
        </template>

        <!-- ░░ 認讀（拼讀規則測驗）░░ -->
        <template v-else-if="tab === 'read'">
          <div v-if="!read.started" class="bg-white rounded-2xl border border-gray-100 p-5 space-y-4">
            <p class="text-xs text-gray-500 leading-relaxed">看拼讀情境（字母／字母組合）→ 選出正確讀音。專練教會拉丁的 c／g／sc 軟硬音、ti、gn、s／x 濁化等規則。</p>
            <div>
              <div class="text-xs font-semibold text-gray-400 mb-1.5">題數</div>
              <div class="flex flex-wrap gap-2">
                <button v-for="n in [10, 20, 0]" :key="n" @click="qCount = n" :class="countClass(n)">{{ n === 0 ? `全部 (${readPool.length})` : n }}</button>
              </div>
            </div>
            <button @click="startRead" :disabled="readPool.length < 4"
              class="w-full py-2.5 rounded-xl bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700 disabled:opacity-40 transition">開始認讀</button>
          </div>

          <div v-else-if="!read.done" class="bg-white rounded-2xl border border-gray-100 p-5">
            <div class="flex items-center justify-between mb-4">
              <span class="text-xs text-gray-400">第 {{ read.idx + 1 }} / {{ read.qs.length }} 題</span>
              <span class="text-xs text-gray-500">✅ {{ read.score }}　❌ {{ read.idx + (read.answered ? 1 : 0) - read.score }}</span>
            </div>
            <div class="text-center py-4">
              <div class="text-3xl font-bold text-gray-900">{{ readCur.item.form }}</div>
              <div class="text-[11px] text-gray-400 mt-2">這個讀音是？</div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5 mt-2">
              <button v-for="(opt, i) in readCur.options" :key="i" @click="pickRead(opt)" :disabled="read.answered"
                class="rounded-xl border-2 py-3 px-3 text-center transition disabled:cursor-default text-base font-medium"
                :class="readOptClass(opt)">{{ opt.sound }}</button>
            </div>
            <div v-if="read.answered" class="mt-4 text-center">
              <p class="text-sm" :class="read.correct ? 'text-emerald-600' : 'text-rose-600'">
                {{ read.correct ? '✅ 答對！' : '❌ 正解：' }}
                <span class="font-semibold">{{ readCur.item.form }} = {{ readCur.item.sound }}</span>
              </p>
              <p v-if="readCur.item.rule" class="text-xs text-gray-500 mt-1">{{ readCur.item.rule }}</p>
              <div v-if="readCur.item.examples" class="flex flex-wrap items-center justify-center gap-1.5 mt-2">
                <span class="text-xs text-gray-400">例：</span>
                <button v-for="word in splitExamples(readCur.item.examples)" :key="word"
                  type="button" @click="speakWord(word)"
                  class="px-2 py-1 rounded-md bg-slate-50 border border-gray-200 text-xs text-gray-700 hover:text-indigo-700 hover:border-indigo-300 transition"
                  :title="`朗讀 ${word}`">
                  {{ word }} <span aria-hidden="true">🔊</span>
                </button>
              </div>
              <button @click="nextRead" class="mt-3 px-6 py-2 rounded-xl bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700 transition">
                {{ read.idx + 1 < read.qs.length ? '下一題 →' : '看結果' }}
              </button>
            </div>
          </div>

          <div v-else class="bg-white rounded-2xl border border-gray-100 p-6 text-center space-y-4">
            <div class="text-4xl">{{ read.score === read.qs.length ? '🎉' : read.score / read.qs.length >= 0.7 ? '👍' : '💪' }}</div>
            <div>
              <div class="text-2xl font-bold text-gray-900">{{ read.score }} / {{ read.qs.length }}</div>
              <div class="text-xs text-gray-400 mt-1">正確率 {{ Math.round((read.score / read.qs.length) * 100) }}%</div>
            </div>
            <div v-if="read.wrong.length" class="text-left">
              <div class="text-xs font-semibold text-rose-400 mb-1.5">答錯的規則（再看一次）</div>
              <div class="space-y-1">
                <div v-for="(w, i) in read.wrong" :key="i" class="text-xs text-rose-700 bg-rose-50 rounded-lg px-2.5 py-1.5">
                  <b>{{ w.form }}</b> = {{ w.sound }}<span v-if="w.rule" class="text-rose-400"> · {{ w.rule }}</span>
                </div>
              </div>
            </div>
            <div class="flex gap-2 justify-center pt-1">
              <button @click="startRead" class="px-5 py-2 rounded-xl bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700 transition">再測一次</button>
              <button @click="resetRead" class="px-5 py-2 rounded-xl bg-white border border-gray-200 text-gray-600 text-sm hover:border-indigo-300 transition">改設定</button>
            </div>
          </div>
        </template>

        <!-- ░░ 聽寫 ░░ -->
        <template v-else-if="tab === 'dict'">
          <div v-if="!dict.started" class="bg-white rounded-2xl border border-gray-100 p-5 space-y-4">
            <p class="text-xs text-gray-500 leading-relaxed">聽教會式發音 → 把拉丁文打出來。逐字比對即時對錯（不計大小寫、長短音記號與標點），零 AI。</p>
            <div>
              <div class="text-xs font-semibold text-gray-400 mb-1.5">題型</div>
              <div class="flex flex-wrap gap-2">
                <button @click="dictScope = 'word'" :class="scopeClass('word')">單字（{{ dictWords.length }}）</button>
                <button @click="dictScope = 'phrase'" :class="scopeClass('phrase')">禮儀短語（{{ dictPhrases.length }}）</button>
              </div>
            </div>
            <div v-if="!speech.ttsSupported.value" class="text-[11px] text-amber-600 bg-amber-50 rounded-lg px-3 py-2">⚠️ 這個瀏覽器不支援語音朗讀，聽寫需要 TTS（建議 Chrome / Edge）。</div>
            <button @click="startDict" :disabled="dictPool.length < 1"
              class="w-full py-2.5 rounded-xl bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700 disabled:opacity-40 transition">開始聽寫</button>
          </div>

          <div v-else-if="!dict.done" class="bg-white rounded-2xl border border-gray-100 p-5">
            <div class="flex items-center justify-between mb-4">
              <span class="text-xs text-gray-400">第 {{ dict.idx + 1 }} / {{ dict.items.length }} 題</span>
              <span class="text-xs text-gray-500">✅ {{ dict.score }}　❌ {{ dict.idx + (dict.answered ? 1 : 0) - dict.score }}</span>
            </div>
            <div class="text-center py-3">
              <button @click="playDict()" class="text-4xl hover:scale-110 transition" title="再聽一次">🔊</button>
              <div class="mt-1 flex items-center justify-center gap-3 text-xs">
                <button @click="playDict()" class="text-indigo-500 hover:text-indigo-700">重播</button>
                <button @click="playDict(0.6)" class="text-indigo-500 hover:text-indigo-700">🐢 慢速</button>
              </div>
              <div class="text-[11px] text-gray-400 mt-1">{{ dictCur.zh }}<span v-if="dictScope === 'phrase'"> · 共 {{ dictWordCount }} 個字</span></div>
            </div>
            <input v-model="dict.input" :disabled="dict.answered" @keyup.enter="dict.answered ? nextDict() : submitDict()"
              type="text" autocomplete="off" autocapitalize="off" spellcheck="false"
              class="w-full border-2 border-gray-200 focus:border-indigo-400 rounded-xl px-4 py-3 text-lg text-center outline-none transition"
              placeholder="打出你聽到的拉丁文…" />
            <div v-if="!dict.answered" class="mt-3 text-center">
              <button @click="submitDict" :disabled="!dict.input.trim()"
                class="px-6 py-2 rounded-xl bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700 disabled:opacity-40 transition">對答案</button>
            </div>
            <div v-else class="mt-4 text-center">
              <p class="text-sm font-semibold" :class="dict.correct ? 'text-emerald-600' : 'text-rose-600'">{{ dict.correct ? '✅ 完全正確！' : '❌ 再看一次' }}</p>
              <p class="text-lg font-semibold text-gray-900 mt-1 break-words">{{ dictCur.latin }}</p>
              <p v-if="!dict.correct" class="text-sm text-gray-400 mt-0.5">你寫的：<span class="line-through">{{ dict.input || '（空白）' }}</span></p>
              <button @click="nextDict" class="mt-3 px-6 py-2 rounded-xl bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700 transition">
                {{ dict.idx + 1 < dict.items.length ? '下一題 →' : '看結果' }}
              </button>
            </div>
          </div>

          <div v-else class="bg-white rounded-2xl border border-gray-100 p-6 text-center space-y-4">
            <div class="text-4xl">{{ dict.score === dict.items.length ? '🎉' : dict.score / dict.items.length >= 0.7 ? '👍' : '💪' }}</div>
            <div>
              <div class="text-2xl font-bold text-gray-900">{{ dict.score }} / {{ dict.items.length }}</div>
              <div class="text-xs text-gray-400 mt-1">正確率 {{ Math.round((dict.score / dict.items.length) * 100) }}%</div>
            </div>
            <div v-if="dict.wrong.length" class="text-left">
              <div class="text-xs font-semibold text-rose-400 mb-1.5">拼錯的（再看一次）</div>
              <div class="flex flex-wrap gap-1.5">
                <button v-for="(w, i) in dict.wrong" :key="i" @click="speakWord(w.latin)"
                  class="text-xs px-2.5 py-1 rounded-lg bg-rose-50 text-rose-700 hover:bg-rose-100">{{ w.latin }} 🔊</button>
              </div>
            </div>
            <div class="flex gap-2 justify-center pt-1">
              <button @click="startDict" class="px-5 py-2 rounded-xl bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700 transition">再聽寫一次</button>
              <button @click="resetDict" class="px-5 py-2 rounded-xl bg-white border border-gray-200 text-gray-600 text-sm hover:border-indigo-300 transition">改題型</button>
            </div>
          </div>
        </template>

        <!-- ░░ 發音跟讀 ░░ -->
        <template v-else>
          <div class="bg-white rounded-2xl border border-gray-100 p-4">
            <p class="text-xs text-gray-500 leading-relaxed">
              挑一個單字／短語 → 🔊 聽教會式範讀（🐢 可慢速）→ 🎤 跟著唸 → 系統逐詞比對著色（✅唸對／🟡近似／❌漏錯），零 AI。
            </p>
            <div v-if="!speech.supported.value" class="mt-2 text-[11px] text-amber-600 bg-amber-50 rounded-lg px-3 py-2">
              ⚠️ 這個瀏覽器不支援語音辨識，仍可聽範讀跟著練，但沒有自動評分（建議 Chrome / Edge）。
            </div>
          </div>

          <div class="flex flex-wrap gap-1.5">
            <button v-for="(v, i) in lesson.vocab" :key="i" @click="pickSay(i)"
              class="text-xs px-2.5 py-1 rounded-lg border transition"
              :class="say.idx === i ? 'bg-indigo-600 border-indigo-600 text-white' : 'bg-white border-gray-200 text-gray-600 hover:border-indigo-300'">
              {{ v.latin.length > 22 ? v.latin.slice(0, 22) + '…' : v.latin }}
            </button>
          </div>

          <div class="bg-white rounded-2xl border border-gray-100 p-5 text-center">
            <div class="text-xl font-bold text-gray-900 break-words">{{ sayCur.latin }}</div>
            <div class="text-xs text-indigo-600 mt-0.5">{{ sayCur.zh }}</div>
            <div class="mt-3 flex items-center justify-center gap-2">
              <button @click="speakWord(sayCur.latin)" class="px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-sm">🔊 範讀</button>
              <button @click="speakWord(sayCur.latin, 0.6)" class="px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-sm">🐢 慢速</button>
              <button v-if="speech.supported.value" @click="toggleRec" class="px-3 py-1.5 rounded-lg text-sm text-white transition"
                :class="say.listening ? 'bg-rose-500 hover:bg-rose-600' : 'bg-indigo-600 hover:bg-indigo-700'">
                {{ say.listening ? '■ 停止' : '🎤 跟讀' }}
              </button>
            </div>
            <div v-if="say.listening" class="mt-2 text-xs text-gray-400">聆聽中…唸完會自動評分。聽到：「{{ speech.interim.value || say.heard }}」</div>

            <div v-if="say.result" class="mt-4">
              <div class="text-2xl font-bold" :class="say.result.score >= 80 ? 'text-emerald-600' : say.result.score >= 50 ? 'text-amber-600' : 'text-rose-600'">{{ say.result.score }} 分</div>
              <div class="mt-2 text-lg leading-relaxed">
                <span v-for="(t, i) in say.result.tokens" :key="i"
                  :class="!t.isWord ? 'text-gray-400' : t.status === 'hit' ? 'text-emerald-600' : t.status === 'near' ? 'text-amber-600' : 'text-rose-500'">{{ t.text }} </span>
              </div>
              <div class="mt-1 text-[11px] text-gray-400">✅ {{ say.result.hits }}　🟡 {{ say.result.near }}　❌ {{ say.result.miss }} · 你唸的：「{{ say.heard }}」</div>
            </div>
          </div>
        </template>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted, onUnmounted } from "vue";
import { useRoute } from "vue-router";
import { authedFetch } from "~/composables/useAuthedFetch";
import { useSpeech } from "~/composables/useSpeech";
import { useActivityTracker } from "~/composables/useActivityTracker";
import { scorePronunciation, type PronScore } from "~/composables/usePronunciationScore";

definePageMeta({ middleware: "coach-auth" });

interface Phone { form: string; sound: string; rule?: string; examples: string; say?: string }
interface Vocab { latin: string; zh: string; note?: string }
interface Lesson { id: string; no: number; title: string; subtitle?: string; vowels: Phone[]; diphthongs: Phone[]; consonants: Phone[]; vocab: Vocab[] }
interface CourseSpec { language: string; title: string; intro: string; ttsLang: string; lessons: Lesson[] }

const route = useRoute();
const lang = computed(() => route.params.lang as string);
const speech = useSpeech();
const tracker = useActivityTracker();

const coach = ref<any>(null);
const spec = ref<CourseSpec | null>(null);
const loading = ref(true);
const lessonIdx = ref(0);
const tab = ref<"phon" | "vocab" | "read" | "dict" | "say">("phon");

const lesson = computed<Lesson>(() => spec.value?.lessons[lessonIdx.value] || { id: "", no: 0, title: "", vowels: [], diphthongs: [], consonants: [], vocab: [] });
const ttsLang = computed(() => coach.value?.ttsLang || spec.value?.ttsLang || "it-IT");

function tabClass(t: string) {
  return `text-sm px-3.5 py-1.5 rounded-lg font-medium transition ${tab.value === t ? "bg-indigo-600 text-white" : "bg-slate-100 text-gray-500 hover:bg-slate-200"}`;
}
function countClass(n: number) {
  return `text-xs px-3 py-1.5 rounded-lg border transition ${qCount.value === n ? "bg-indigo-600 border-indigo-600 text-white" : "bg-white border-gray-200 text-gray-600 hover:border-indigo-300"}`;
}
function scopeClass(s: string) {
  return `text-xs px-3 py-1.5 rounded-lg border transition ${dictScope.value === s ? "bg-indigo-600 border-indigo-600 text-white" : "bg-white border-gray-200 text-gray-600 hover:border-indigo-300"}`;
}

function speakWord(text: string, rate = 0.75) {
  speech.speak(text, ttsLang.value, rate);
}
// 按字母／音組本身：用資料層的 say 載體音節（it-IT TTS 才不會唸成字母名），缺省退回第一個例字
function speakPhone(p: Phone) {
  speakWord(p.say || splitExamples(p.examples)[0] || p.form);
}
function splitExamples(examples: string) {
  return (examples || "").trim().split(/\s+/).filter(Boolean);
}
function selectLesson(i: number) {
  lessonIdx.value = i;
  resetRead(); resetDict(); resetSay(); flipped.clear();
}

function shuffle<T>(arr: T[]): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; }
  return a;
}
// 聽寫比對正規化：小寫、去長短音記號、去標點、收斂空白
function normLatin(s: string): string {
  return (s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "")
    .replace(/[.,!?;:'"()’]/g, "").replace(/\s+/g, " ").trim();
}

// ── 單字翻卡 ─────────────────────────────────────────────────────────────────
const flipped = reactive(new Set<number>());
function flip(i: number) { flipped.has(i) ? flipped.delete(i) : flipped.add(i); }
function flipAll() {
  if (flipped.size === lesson.value.vocab.length) flipped.clear();
  else lesson.value.vocab.forEach((_, i) => flipped.add(i));
}

// ── 認讀（拼讀規則測驗）─────────────────────────────────────────────────────
const qCount = ref(20);
const readPool = computed<Phone[]>(() => [...lesson.value.vowels, ...lesson.value.diphthongs, ...lesson.value.consonants].filter((p) => p.form && p.sound));
interface ReadQ { item: Phone; options: Phone[] }
const read = reactive<{ started: boolean; done: boolean; idx: number; score: number; qs: ReadQ[]; wrong: Phone[]; answered: boolean; correct: boolean; picked: Phone | null }>(
  { started: false, done: false, idx: 0, score: 0, qs: [], wrong: [], answered: false, correct: false, picked: null }
);
const readCur = computed(() => read.qs[read.idx] || { item: { form: "", sound: "", examples: "" }, options: [] } as ReadQ);

function buildReadQ(item: Phone): ReadQ {
  const used = new Set([item.sound]);
  const distractors: Phone[] = [];
  for (const d of shuffle(readPool.value)) {
    if (distractors.length >= 3) break;
    if (used.has(d.sound)) continue;
    used.add(d.sound); distractors.push(d);
  }
  return { item, options: shuffle([item, ...distractors]) };
}
function startRead() {
  const n = qCount.value === 0 ? readPool.value.length : Math.min(qCount.value, readPool.value.length);
  read.qs = shuffle(readPool.value).slice(0, n).map(buildReadQ);
  read.idx = 0; read.score = 0; read.wrong = []; read.started = true; read.done = false; read.answered = false; read.picked = null;
}
function resetRead() {
  Object.assign(read, { started: false, done: false, idx: 0, score: 0, qs: [], wrong: [], answered: false, correct: false, picked: null });
}
function pickRead(opt: Phone) {
  if (read.answered) return;
  read.answered = true; read.picked = opt;
  read.correct = opt.sound === readCur.value.item.sound && opt.form === readCur.value.item.form;
  if (read.correct) read.score++; else read.wrong.push(readCur.value.item);
}
function nextRead() {
  if (read.idx + 1 < read.qs.length) { read.idx++; read.answered = false; read.picked = null; }
  else read.done = true;
}
function readOptClass(opt: Phone) {
  if (!read.answered) return "border-gray-200 bg-white hover:border-indigo-300 hover:bg-indigo-50 text-gray-800";
  const isCorrect = opt.form === readCur.value.item.form;
  if (isCorrect) return "border-emerald-400 bg-emerald-50 text-emerald-700";
  if (opt === read.picked) return "border-rose-400 bg-rose-50 text-rose-700";
  return "border-gray-200 bg-white text-gray-400 opacity-60";
}

// ── 聽寫 ─────────────────────────────────────────────────────────────────────
const dictScope = ref<"word" | "phrase">("word");
const dictWords = computed<Vocab[]>(() => {
  const seen = new Set<string>();
  const out: Vocab[] = [];
  // 單字：詞庫中不含空白者 + 例字裡的個別單字
  for (const v of lesson.value.vocab) if (!/\s/.test(v.latin)) { const k = normLatin(v.latin); if (!seen.has(k)) { seen.add(k); out.push(v); } }
  for (const p of [...lesson.value.vowels, ...lesson.value.diphthongs, ...lesson.value.consonants]) {
    for (const w of (p.examples || "").split(/\s+/)) {
      const k = normLatin(w);
      if (w && k.length >= 2 && !seen.has(k)) { seen.add(k); out.push({ latin: w, zh: "（例字）" }); }
    }
  }
  return out;
});
const dictPhrases = computed<Vocab[]>(() => lesson.value.vocab.filter((v) => /\s/.test(v.latin)));
const dictPool = computed<Vocab[]>(() => (dictScope.value === "word" ? dictWords.value : dictPhrases.value));
const dict = reactive<{ started: boolean; done: boolean; idx: number; score: number; items: Vocab[]; wrong: Vocab[]; answered: boolean; correct: boolean; input: string }>(
  { started: false, done: false, idx: 0, score: 0, items: [], wrong: [], answered: false, correct: false, input: "" }
);
const dictCur = computed(() => dict.items[dict.idx] || { latin: "", zh: "" } as Vocab);
const dictWordCount = computed(() => dictCur.value.latin.trim().split(/\s+/).length);

function startDict() {
  const n = Math.min(dictScope.value === "word" ? 15 : dictPool.value.length, dictPool.value.length);
  dict.items = shuffle(dictPool.value).slice(0, n);
  dict.idx = 0; dict.score = 0; dict.wrong = []; dict.started = true; dict.done = false; dict.answered = false; dict.input = "";
  setTimeout(() => playDict(), 300);
}
function resetDict() {
  Object.assign(dict, { started: false, done: false, idx: 0, score: 0, items: [], wrong: [], answered: false, correct: false, input: "" });
}
function playDict(rate = 0.75) { speakWord(dictCur.value.latin, rate); }
function submitDict() {
  if (dict.answered || !dict.input.trim()) return;
  dict.answered = true;
  dict.correct = normLatin(dict.input) === normLatin(dictCur.value.latin);
  if (dict.correct) dict.score++; else dict.wrong.push(dictCur.value);
}
function nextDict() {
  if (dict.idx + 1 < dict.items.length) { dict.idx++; dict.answered = false; dict.input = ""; setTimeout(() => playDict(), 250); }
  else dict.done = true;
}

// ── 發音跟讀 ─────────────────────────────────────────────────────────────────
const say = reactive<{ idx: number; listening: boolean; heard: string; result: PronScore | null }>({ idx: 0, listening: false, heard: "", result: null });
const sayCur = computed(() => lesson.value.vocab[say.idx] || { latin: "", zh: "" } as Vocab);
function pickSay(i: number) { say.idx = i; say.heard = ""; say.result = null; if (say.listening) stopRec(); }
function toggleRec() { say.listening ? stopRec() : startRec(); }
function startRec() {
  if (!speech.supported.value) return;
  say.heard = ""; say.result = null; say.listening = true;
  speech.startListening(ttsLang.value, (text: string) => {
    say.heard = text;
    say.result = scorePronunciation(sayCur.value.latin, text);
    stopRec();
  });
}
function stopRec() { speech.stopListening(); say.listening = false; }
function resetSay() { stopRec(); say.idx = 0; say.heard = ""; say.result = null; }

const phonSections = computed(() => [
  { title: "單母音 · Vocales", note: "", items: lesson.value.vowels },
  { title: "雙母音 · Diphthongi", note: "", items: lesson.value.diphthongs },
  { title: "子音與拼讀規則 · Consonantes", note: "教會式發音；c／g／sc 在 e、i 前軟化是誦讀最關鍵處。", items: lesson.value.consonants },
]);

onMounted(async () => {
  try {
    const [{ coaches }, r] = await Promise.all([
      $fetch<{ coaches: any[] }>("/api/lang/coaches"),
      authedFetch<{ available: boolean; course: CourseSpec | null }>(`/api/lang/course?language=${lang.value}`),
    ]);
    coach.value = coaches.find((c) => c.language === lang.value);
    if (r.available && r.course) spec.value = r.course;
  } finally {
    loading.value = false;
  }
  tracker.start(lang.value, "reading", "course");
});
onUnmounted(() => { speech.stopListening(); speech.stopSpeaking(); });
</script>
