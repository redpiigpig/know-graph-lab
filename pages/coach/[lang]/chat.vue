<template>
  <div class="flex flex-col h-dvh bg-slate-50">
    <AppHeader title="AI 語言教練" :back="{ to: `/coach/${lang}`, label: '教練首頁' }" container-class="max-w-full" />
    <!-- 頂列 -->
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30 flex-shrink-0">
      <NuxtLink :to="`/coach/${lang}`" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-xl">{{ coach?.emoji }}</span>
      <div>
        <div class="text-sm font-semibold text-gray-900 leading-tight">
          {{ coach?.name }} <span class="text-xs text-gray-400 font-normal">{{ coach?.langLabel }}教練</span>
          <span v-if="persona" class="ml-1 text-[11px] px-1.5 py-0.5 rounded-full bg-violet-50 text-violet-700">{{ persona.emoji }} {{ persona.label }}</span>
        </div>
        <div class="text-[11px] text-gray-400 leading-tight">{{ coach?.accent }}</div>
      </div>

      <div class="ml-auto flex items-center gap-2">
        <span class="text-xs px-2 py-1 rounded-lg bg-gray-50 text-gray-500 tabular-nums" title="本次練習時間">⏱ {{ elapsed }}</span>
        <button
          v-if="!coach?.voiceless"
          @click="autoSpeak = !autoSpeak"
          class="text-xs px-2.5 py-1 rounded-lg border transition flex items-center gap-1"
          :class="autoSpeak ? 'bg-indigo-50 border-indigo-200 text-indigo-700' : 'bg-white border-gray-200 text-gray-400'"
          title="教練回覆自動語音播放"
        >
          🔊 自動朗讀
        </button>
        <button @click="newSession" class="text-xs px-2.5 py-1 rounded-lg bg-white border border-gray-200 text-gray-600 hover:border-indigo-300 transition">＋ 新對話</button>
      </div>
    </nav>

    <div class="flex-1 flex min-h-0">
      <!-- 左：對話清單 -->
      <aside class="hidden md:flex flex-col w-52 bg-white border-r border-gray-100 flex-shrink-0">
        <div class="px-3 py-2 text-[11px] font-semibold text-gray-400 uppercase tracking-wide">對話紀錄</div>
        <div class="flex-1 overflow-y-auto px-2 pb-2 space-y-1">
          <button
            v-for="s in sessions"
            :key="s.id"
            @click="loadSession(s.id)"
            class="w-full text-left px-2.5 py-2 rounded-lg text-xs transition truncate"
            :class="s.id === sessionId ? 'bg-indigo-50 text-indigo-700' : 'text-gray-600 hover:bg-gray-50'"
          >
            {{ s.title || '未命名對話' }}
            <span class="block text-[10px] text-gray-400">{{ s.message_count }} 則 · {{ fmtDate(s.updated_at) }}</span>
          </button>
          <div v-if="!sessions.length" class="text-[11px] text-gray-300 px-2 py-3">尚無對話，開始聊天吧</div>
        </div>
      </aside>

      <!-- 中：對話區 -->
      <section class="flex-1 flex flex-col min-w-0">
        <div ref="msgArea" class="flex-1 overflow-y-auto px-4 py-5 space-y-4">
          <!-- 歡迎 -->
          <div v-if="!messages.length && !sending" class="max-w-md mx-auto text-center mt-10">
            <div class="text-5xl mb-3">{{ coach?.emoji }}</div>
            <div class="font-semibold text-gray-800">{{ coach?.name }} <span class="text-xs font-normal text-violet-600">· {{ modeLabel }}</span></div>
            <p class="text-sm text-gray-500 mt-2">{{ coach?.blurb }}</p>

            <!-- 情境角色扮演：選一個情境 -->
            <div v-if="mode === 'scenario'" class="mt-4">
              <p class="text-xs text-gray-400 mb-2">選一個情境，教練扮演對方角色：</p>
              <div class="flex flex-wrap gap-1.5 justify-center">
                <button v-for="s in coach?.scenarios || []" :key="s" @click="startScenario(s)" class="text-xs px-2.5 py-1 rounded-full border border-violet-200 text-violet-700 bg-violet-50 hover:bg-violet-100 transition">{{ s }}</button>
              </div>
              <p class="text-[11px] text-gray-300 mt-2">或直接在下方輸入你想練的情境</p>
            </div>
            <p v-else-if="mode === 'qa'" class="text-xs text-gray-400 mt-3">問我任何問題（宗教／神話／宗教學／人文皆可），我用{{ coach?.langLabel }}講給你聽、附繁中對照。</p>
            <p v-else class="text-xs text-gray-400 mt-3">用{{ voiceMode ? '麥克風' : '文字' }}跟我打招呼，我會用{{ coach?.langLabel }}陪你練習、隨時改錯、記新單字、出作業。</p>
          </div>

          <div v-for="(m, i) in messages" :key="m.id || i" class="flex" :class="m.role === 'user' ? 'justify-end' : 'justify-start'">
            <div class="max-w-[80%]">
              <div
                dir="auto"
                class="px-3.5 py-2.5 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap"
                :class="m.role === 'user' ? 'bg-indigo-600 text-white rounded-br-md' : 'bg-white border border-gray-100 text-gray-800 rounded-bl-md shadow-sm'"
              >
                {{ m.content }}
                <button
                  v-if="m.role === 'coach' && !coach?.voiceless"
                  @click="replay(m.content)"
                  class="ml-1 text-gray-300 hover:text-indigo-500 transition align-middle"
                  title="再聽一次"
                >🔊</button>
              </div>
              <!-- 繁中對照 -->
              <div v-if="m.role === 'coach' && m.translation" class="text-[11px] text-gray-400 mt-1 px-1">{{ m.translation }}</div>
              <!-- 改錯卡 -->
              <div v-if="m.corrections && m.corrections.length" class="mt-1.5 space-y-1">
                <div v-for="(c, ci) in m.corrections" :key="ci" class="text-xs bg-rose-50 border border-rose-100 rounded-lg px-2.5 py-1.5">
                  <span class="line-through text-rose-400">{{ c.original }}</span>
                  <span class="mx-1 text-gray-300">→</span>
                  <span class="text-emerald-700 font-medium">{{ c.fixed }}</span>
                  <span v-if="c.note" class="block text-gray-500 mt-0.5">💡 {{ c.note }}</span>
                </div>
              </div>
            </div>
          </div>

          <div v-if="sending" class="flex justify-start">
            <div class="px-3.5 py-2.5 rounded-2xl bg-white border border-gray-100 shadow-sm text-gray-400 text-sm">{{ coach?.name }} 正在輸入…</div>
          </div>
        </div>

        <!-- 輸入列 -->
        <div class="border-t border-gray-100 bg-white px-3 py-2.5 flex-shrink-0">
          <div v-if="speechErr" class="text-[11px] text-rose-500 mb-1.5 px-1">{{ speechErr }}</div>

          <!-- 羅馬字系統切換（台語：教羅↔台羅；客語：白話字↔客拼） -->
          <div v-if="romanList.length" class="flex items-center flex-wrap gap-2 mb-2 px-0.5">
            <span class="text-[11px] text-gray-400">羅馬字：</span>
            <button
              v-for="r in romanList"
              :key="r.key"
              @click="setRoman(r.key)"
              class="text-xs px-2.5 py-1 rounded-lg border transition"
              :class="roman === r.key ? 'bg-teal-50 border-teal-300 text-teal-800' : 'bg-white border-gray-200 text-gray-500'"
            >{{ r.label }}</button>
          </div>

          <!-- 轉寫鍵盤工具列（希臘 / 假名 / 希伯來內建；其餘字母系走通用鍵盤） -->
          <div v-if="anyKb" class="flex items-center flex-wrap gap-2 mb-2 px-0.5">
            <button
              @click="kbOn = !kbOn"
              class="text-xs px-2.5 py-1 rounded-lg border transition flex items-center gap-1"
              :class="kbOn ? 'bg-amber-50 border-amber-300 text-amber-800' : 'bg-white border-gray-200 text-gray-400'"
              :title="'打英文/羅馬字即時轉成目標文字'"
            >⌨️ {{ greekKb ? '希臘鍵盤' : (kanaKb ? '假名鍵盤' : (hebrewKb ? '希伯來鍵盤' : (scriptKb ? scriptKb.label : '鍵盤'))) }} {{ kbOn ? '開' : '關' }}</button>

            <!-- 假名：平/片切換 -->
            <button
              v-if="kanaKb"
              @click="kana.kata.value = !kana.kata.value"
              class="text-xs px-2.5 py-1 rounded-lg border transition"
              :class="kana.kata.value ? 'bg-sky-50 border-sky-300 text-sky-700' : 'bg-white border-gray-200 text-gray-500'"
              title="平假名 / 片假名切換"
            >{{ kana.kata.value ? 'カ 片假名' : 'あ 平假名' }}</button>

            <button @click="showKbHelp = !showKbHelp" class="text-xs px-2 py-1 rounded-lg text-amber-700 hover:bg-amber-50 transition">
              對照表 {{ showKbHelp ? '▲' : '▼' }}
            </button>
            <span v-if="kbOn && greekKb" class="text-[11px] text-gray-400">打 a→α、h→η、q→θ、w→ω…；母音後按 ) ( / \ = | + 加符號</span>
            <span v-if="kbOn && kanaKb" class="text-[11px] text-gray-400">打羅馬字如 sakura→さくら；ん打 nn、っ打雙子音、' 分隔（kon'nichiwa）</span>
            <span v-if="kbOn && hebrewKb" class="text-[11px] text-gray-400">打 a→א、b→ב、w→ש、x→ח…（由右至左）；字尾自動 sofit；母音點在對照表點選</span>
            <span v-if="kbOn && scriptKb" class="text-[11px] text-gray-400">{{ scriptKb.hint }}</span>
          </div>

          <!-- 通用字母系對照表（西里爾/科普特/阿拉伯/敘利亞/亞美尼亞/喬治亞）+ 點選面板 -->
          <div v-if="scriptKb && showKbHelp" class="mb-2 p-2.5 rounded-xl bg-teal-50/60 border border-teal-100 space-y-2" :dir="scriptKb.rtl ? 'rtl' : 'ltr'">
            <div class="flex flex-wrap gap-1">
              <button
                v-for="(p, i) in scriptKb.palette"
                :key="i"
                @click="insertScript(p.ch)"
                class="px-2 py-1 rounded-lg bg-white border border-teal-200 text-base hover:bg-teal-100 transition"
                :title="p.label || (p.latin ? `鍵盤打 ${p.latin}` : '')"
              >
                <span class="text-gray-900">{{ p.ch }}</span>
                <span v-if="p.latin" class="text-[10px] text-gray-400 ml-0.5" dir="ltr">{{ p.latin }}</span>
              </button>
            </div>
            <div v-if="scriptKb.marks.length" class="flex flex-wrap gap-1 items-center" dir="ltr">
              <span class="text-[11px] text-teal-800/80">附加符號：</span>
              <button
                v-for="m in scriptKb.marks"
                :key="m.label"
                @click="insertScript(m.mark)"
                class="px-2 py-1 rounded-lg bg-white border border-teal-200 text-sm hover:bg-teal-100 transition"
                :title="m.label"
              >ا<span class="text-gray-900">{{ m.mark }}</span></button>
            </div>
          </div>

          <!-- 希臘文對照表 + 點選面板 -->
          <div v-if="greekKb && showKbHelp" class="mb-2 p-2.5 rounded-xl bg-amber-50/60 border border-amber-100 space-y-2">
            <div class="flex flex-wrap gap-1">
              <button
                v-for="p in gk.GREEK_PALETTE"
                :key="p.latin"
                @click="insertGreek(p.greek)"
                class="px-2 py-1 rounded-lg bg-white border border-amber-200 text-sm hover:bg-amber-100 transition"
                :title="`鍵盤打 ${p.latin}`"
              >
                <span class="text-gray-900">{{ p.greek }}</span>
                <span class="text-[10px] text-gray-400 ml-0.5">{{ p.latin }}</span>
              </button>
              <button @click="insertGreek('ς')" class="px-2 py-1 rounded-lg bg-white border border-amber-200 text-sm hover:bg-amber-100 transition" title="字尾 sigma（一般自動）">
                <span class="text-gray-900">ς</span><span class="text-[10px] text-gray-400 ml-0.5">字尾σ</span>
              </button>
            </div>
            <div class="text-[11px] text-amber-800/80">
              變音符號：母音後按
              <span v-for="d in gk.GREEK_DIACRITICS" :key="d.key" class="inline-block mx-0.5">
                <code class="px-1 rounded bg-white border border-amber-200">{{ d.key }}</code>={{ d.label }}
              </span>
            </div>
          </div>

          <!-- 假名五十音點選面板 -->
          <div v-if="kanaKb && showKbHelp" class="mb-2 p-2.5 rounded-xl bg-sky-50/60 border border-sky-100">
            <div class="grid grid-cols-5 gap-1 max-w-md">
              <template v-for="(row, ri) in kana.GOJUON" :key="ri">
                <button
                  v-for="(h, ci) in row"
                  :key="ri + '-' + ci"
                  :disabled="!h"
                  @click="insertKana(h)"
                  class="px-1 py-1.5 rounded-lg text-sm transition"
                  :class="h ? 'bg-white border border-sky-200 text-gray-800 hover:bg-sky-100' : 'opacity-0 pointer-events-none'"
                >{{ h ? (kana.kata.value ? kana.toKatakana(h) : h) : '·' }}</button>
              </template>
            </div>
            <p class="text-[11px] text-sky-800/70 mt-1.5">點選直接插入；或直接打羅馬字。濁音／拗音直接打（ga、kya、sha…），片假名長音打 -</p>
          </div>

          <!-- 希伯來文對照表 + 點選面板（含母音點 niqqud） -->
          <div v-if="hebrewKb && showKbHelp" class="mb-2 p-2.5 rounded-xl bg-emerald-50/60 border border-emerald-100 space-y-2" dir="rtl">
            <div class="flex flex-wrap gap-1">
              <button
                v-for="p in heb.HEBREW_PALETTE"
                :key="p.latin"
                @click="insertHebrew(p.heb)"
                class="px-2 py-1 rounded-lg bg-white border border-emerald-200 text-base hover:bg-emerald-100 transition"
                :title="`鍵盤打 ${p.latin}`"
              >
                <span class="text-gray-900">{{ p.heb }}</span>
                <span class="text-[10px] text-gray-400 mr-0.5" dir="ltr">{{ p.latin }}</span>
              </button>
            </div>
            <div class="flex flex-wrap gap-1 items-center" dir="ltr">
              <span class="text-[11px] text-emerald-800/80">母音點：</span>
              <button
                v-for="d in heb.HEBREW_NIQQUD"
                :key="d.label"
                @click="insertHebrew(d.mark)"
                class="px-2 py-1 rounded-lg bg-white border border-emerald-200 text-sm hover:bg-emerald-100 transition"
                :title="d.label"
              >א<span class="text-gray-900">{{ d.mark }}</span></button>
            </div>
          </div>

          <div class="flex items-end gap-2">
            <button
              v-if="!coach?.voiceless && sttSupported"
              @click="toggleMic"
              class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 transition"
              :class="listening ? 'bg-rose-500 text-white animate-pulse' : 'bg-gray-100 text-gray-500 hover:bg-gray-200'"
              :title="listening ? '停止錄音' : '按住說話'"
            >🎤</button>
            <textarea
              ref="inputEl"
              v-model="input"
              @keydown="onInputKeydown"
              :dir="kbOn && kbRtl ? 'rtl' : undefined"
              :placeholder="listening ? (interim || '聆聽中…') : (kbOn && greekKb ? '打英文字母 → 希臘字母（如 logos→λόγος）…' : (kbOn && kanaKb ? '打羅馬字 → 假名（如 sakura→さくら）…' : (kbOn && hebrewKb ? '打英文字母 → 希伯來字母（由右至左，如 wlvm→שלום）…' : (kbOn && scriptKb ? `打英文/羅馬字 → ${scriptKb.label.replace('鍵盤','')}（見對照表）…` : `用${coach?.langLabel}輸入…`))))"
              rows="1"
              class="flex-1 resize-none px-3.5 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-indigo-400 max-h-32"
            />
            <button
              @click="send"
              :disabled="sending || (!input.trim())"
              class="w-10 h-10 rounded-xl bg-indigo-600 text-white flex items-center justify-center flex-shrink-0 disabled:opacity-40 hover:bg-indigo-700 transition"
            >➤</button>
          </div>
        </div>
      </section>

      <!-- 右：單字庫 / 作業 -->
      <aside class="hidden lg:flex flex-col w-72 bg-white border-l border-gray-100 flex-shrink-0">
        <div class="flex border-b border-gray-100">
          <button @click="panel = 'vocab'" class="flex-1 py-2.5 text-xs font-medium transition" :class="panel === 'vocab' ? 'text-indigo-700 border-b-2 border-indigo-600' : 'text-gray-400'">📚 單字庫 ({{ vocab.length }})</button>
          <button @click="panel = 'homework'" class="flex-1 py-2.5 text-xs font-medium transition" :class="panel === 'homework' ? 'text-indigo-700 border-b-2 border-indigo-600' : 'text-gray-400'">✍️ 作業 ({{ homework.length }})</button>
        </div>

        <!-- 單字庫 -->
        <div v-if="panel === 'vocab'" class="flex-1 overflow-y-auto p-2.5 space-y-2">
          <div v-for="v in vocab" :key="v.id" class="border border-gray-100 rounded-xl p-2.5 group">
            <div class="flex items-start justify-between">
              <div>
                <span class="font-semibold text-gray-800 text-sm">{{ v.word }}</span>
                <span v-if="v.reading" class="text-[11px] text-gray-400 ml-1">{{ v.reading }}</span>
              </div>
              <button @click="delVocab(v)" class="text-gray-200 group-hover:text-rose-400 text-xs transition">✕</button>
            </div>
            <div class="text-xs text-gray-600 mt-0.5">{{ v.meaning }}</div>
            <div v-if="v.example" class="text-[11px] text-gray-400 mt-1 italic">{{ v.example }}</div>
            <div class="flex gap-0.5 mt-1.5">
              <button v-for="n in 5" :key="n" @click="setMastery(v, n)" class="text-xs" :title="`熟練度 ${n}`">
                <span :class="n <= v.mastery_level ? 'text-amber-400' : 'text-gray-200'">★</span>
              </button>
            </div>
          </div>
          <div v-if="!vocab.length" class="text-[11px] text-gray-300 text-center py-6">對話中學到的新單字會自動收進這裡</div>
        </div>

        <!-- 作業 -->
        <div v-if="panel === 'homework'" class="flex-1 overflow-y-auto p-2.5 space-y-2.5">
          <div v-for="h in homework" :key="h.id" class="border border-gray-100 rounded-xl p-3">
            <div class="flex items-center gap-2">
              <span class="text-xs font-semibold text-gray-800">{{ h.topic }}</span>
              <span class="text-[10px] px-1.5 py-0.5 rounded-full"
                :class="h.status === 'graded' ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'">
                {{ h.status === 'graded' ? `已批改 ${h.score ?? ''}` : '待繳交' }}
              </span>
            </div>
            <p class="text-xs text-gray-600 mt-1.5 whitespace-pre-wrap">{{ h.prompt }}</p>

            <template v-if="h.status !== 'graded'">
              <textarea v-model="h._draft" rows="3" placeholder="在此作答…" class="w-full mt-2 resize-none px-2.5 py-2 rounded-lg border border-gray-200 text-xs focus:outline-none focus:border-indigo-400" />
              <button @click="submitHw(h)" :disabled="h._grading || !h._draft?.trim()" class="mt-1.5 w-full py-1.5 rounded-lg bg-indigo-600 text-white text-xs disabled:opacity-40 hover:bg-indigo-700 transition">
                {{ h._grading ? '批改中…' : '繳交給' + (coach?.name || '教練') + '批改' }}
              </button>
            </template>

            <div v-else class="mt-2 space-y-1.5">
              <div class="text-[11px] text-gray-500 bg-gray-50 rounded-lg p-2 whitespace-pre-wrap">{{ h.feedback }}</div>
              <div v-for="(c, ci) in (h.corrections || [])" :key="ci" class="text-[11px] bg-rose-50 rounded-lg px-2 py-1">
                <span class="line-through text-rose-400">{{ c.original }}</span> → <span class="text-emerald-700">{{ c.fixed }}</span>
                <span v-if="c.note" class="block text-gray-500">{{ c.note }}</span>
              </div>
            </div>
          </div>
          <div v-if="!homework.length" class="text-[11px] text-gray-300 text-center py-6">請教練「出個作業」，題目會出現在這裡</div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from "vue";
import { useRoute } from "vue-router";
import { authedFetch } from "~/composables/useAuthedFetch";
import { useSpeech } from "~/composables/useSpeech";
import { useActivityTracker } from "~/composables/useActivityTracker";
import { useCoachAi } from "~/composables/useCoachAi";
import { useGreekKeyboard } from "~/composables/useGreekKeyboard";
import { useKanaKeyboard } from "~/composables/useKanaKeyboard";
import { useHebrewKeyboard } from "~/composables/useHebrewKeyboard";
import { getScriptKeyboard } from "~/composables/useScriptKeyboard";
import { getAbugidaKeyboard } from "~/composables/useAbugidaKeyboard";

definePageMeta({ middleware: "coach-auth" });

const tracker = useActivityTracker();
const { aiFetch } = useCoachAi();
const route = useRoute();
const lang = computed(() => route.params.lang as string);
const mode = computed(() => {
  const m = route.query.mode as string;
  return ["free", "qa", "scenario"].includes(m) ? m : "free";
});
const voiceMode = computed(() => route.query.voice === "1");
const modeLabel = computed(() => ({ free: "自由聊", qa: "問答・知識", scenario: "情境角色扮演" } as any)[mode.value] || "自由聊");

const persona = ref<any>(null);
const elapsed = computed(() => {
  const s = tracker.activeSeconds.value;
  const m = Math.floor(s / 60);
  return `${m}:${String(s % 60).padStart(2, "0")}`;
});

const coach = ref<any>(null);
const sessions = ref<any[]>([]);
const sessionId = ref<string | null>(null);
const messages = ref<any[]>([]);
const vocab = ref<any[]>([]);
const homework = ref<any[]>([]);
const input = ref("");
const sending = ref(false);
const panel = ref<"vocab" | "homework">("vocab");
const autoSpeak = ref(false);
const msgArea = ref<HTMLElement | null>(null);

// 轉寫鍵盤（打英文 → 目標文字）：依 coach.keyboard 啟用
//   greek = 希臘字母（Beta Code）；kana = 日文假名（romaji IME）；hebrew = 希伯來字母（RTL）
const gk = useGreekKeyboard();
const kana = useKanaKeyboard();
const heb = useHebrewKeyboard();
const inputEl = ref<HTMLTextAreaElement | null>(null);
const greekKb = computed(() => coach.value?.keyboard === "greek");
const kanaKb = computed(() => coach.value?.keyboard === "kana");
const hebrewKb = computed(() => coach.value?.keyboard === "hebrew");
// 其餘文字：字母系走無狀態通用鍵盤；abugida（天城體/吉茲/藏文）走有狀態重轉寫鍵盤
const scriptKb = computed(() => getScriptKeyboard(coach.value?.keyboard) || getAbugidaKeyboard(coach.value?.keyboard));
const anyKb = computed(() => greekKb.value || kanaKb.value || hebrewKb.value || !!scriptKb.value);
const kbRtl = computed(() => hebrewKb.value || !!scriptKb.value?.rtl);
const kbOn = ref(true); // 預設開啟（系統 IME 組字時 kana 會自動讓行）
const showKbHelp = ref(false);

// 羅馬字系統切換（台語：教羅 POJ ↔ 台羅；客語：白話字 ↔ 客拼）；存 localStorage
const romanList = computed<any[]>(() => coach.value?.romanizations || []);
const roman = ref<string>("");
function setRoman(key: string) {
  roman.value = key;
  localStorage.setItem(`coach-roman-${lang.value}`, key);
}

function setInput(v: string, cursor: number) {
  input.value = v;
  nextTick(() => inputEl.value?.setSelectionRange(cursor, cursor));
}

function onInputKeydown(e: KeyboardEvent) {
  // Enter（無 Shift、非組字中）送出；Shift+Enter 換行
  if (e.key === "Enter" && !e.shiftKey && !e.isComposing) {
    if (kanaKb.value && kbOn.value && inputEl.value) kana.finalize(inputEl.value, setInput); // 先收掉殘留 ん
    e.preventDefault();
    send();
    return;
  }
  if (!kbOn.value || !inputEl.value) return;
  if (greekKb.value) gk.onKeydown(e, inputEl.value, setInput);
  else if (kanaKb.value) kana.onKeydown(e, inputEl.value, setInput);
  else if (hebrewKb.value) heb.onKeydown(e, inputEl.value, setInput);
  else if (scriptKb.value) scriptKb.value.onKeydown(e, inputEl.value, setInput);
}

function insertGreek(ch: string) {
  if (inputEl.value) {
    gk.insert(inputEl.value, ch, setInput);
    inputEl.value.focus();
  }
}

function insertHebrew(ch: string) {
  if (inputEl.value) {
    heb.insert(inputEl.value, ch, setInput);
    inputEl.value.focus();
  }
}

function insertKana(ch: string) {
  if (ch && inputEl.value) {
    kana.insert(inputEl.value, kana.kata.value ? kana.toKatakana(ch) : ch, setInput);
    inputEl.value.focus();
  }
}

function insertScript(ch: string) {
  if (ch && inputEl.value && scriptKb.value) {
    scriptKb.value.insert(inputEl.value, ch, setInput);
    inputEl.value.focus();
  }
}

function startScenario(s: string) {
  input.value = `我想練習這個情境：「${s}」。請你扮演對方角色，先用${coach.value?.langLabel || ''}開場。`;
  send();
}

const speech = useSpeech();
const sttSupported = speech.supported;
const listening = speech.listening;
const interim = speech.interim;
const speechErr = speech.error;

function fmtDate(s: string) {
  if (!s) return "";
  return new Date(s).toLocaleDateString("zh-TW", { month: "numeric", day: "numeric" });
}

async function scrollDown() {
  await nextTick();
  if (msgArea.value) msgArea.value.scrollTop = msgArea.value.scrollHeight;
}

async function loadCoachMeta() {
  const { coaches } = await $fetch<{ coaches: any[] }>("/api/lang/coaches");
  coach.value = coaches.find((c) => c.language === lang.value);
  // 初始化羅馬字系統：localStorage 優先，否則用第一個（預設）
  if (romanList.value.length) {
    const saved = localStorage.getItem(`coach-roman-${lang.value}`);
    roman.value = saved && romanList.value.some((r) => r.key === saved) ? saved : romanList.value[0].key;
  }
}

async function loadSessions() {
  const { sessions: s } = await authedFetch<{ sessions: any[] }>(`/api/lang/sessions?language=${lang.value}`);
  sessions.value = s;
}

async function loadSession(id: string) {
  sessionId.value = id;
  const { messages: m } = await authedFetch<{ messages: any[] }>(`/api/lang/messages?sessionId=${id}`);
  messages.value = m;
  scrollDown();
}

function newSession() {
  sessionId.value = null;
  messages.value = [];
  persona.value = null;
  kana.reset();
}

async function loadVocab() {
  const { vocab: v } = await authedFetch<{ vocab: any[] }>(`/api/lang/vocab?language=${lang.value}`);
  vocab.value = v;
}

async function loadHomework() {
  const { homework: h } = await authedFetch<{ homework: any[] }>(`/api/lang/homework?language=${lang.value}`);
  homework.value = h.map((x) => ({ ...x, _draft: x.submission || "", _grading: false }));
}

async function send() {
  const text = input.value.trim();
  if (!text || sending.value) return;
  speech.stopListening();
  input.value = "";
  kana.reset();
  scriptKb.value?.reset?.(); // 清掉 abugida 的逐鍵緩衝（天城體/吉茲/藏文）
  messages.value.push({ role: "user", content: text, corrections: [] });
  scrollDown();
  sending.value = true;
  try {
    const res = await aiFetch<any>("/api/lang/chat", {
      method: "POST",
      body: { language: lang.value, sessionId: sessionId.value, message: text, mode: mode.value, romanization: roman.value || undefined },
    });
    sessionId.value = res.sessionId;
    if (res.persona) persona.value = res.persona;
    messages.value.push({
      role: "coach",
      content: res.reply,
      translation: res.translation,
      corrections: [],
    });
    // 把改錯掛到剛剛那則 user 訊息
    if (res.corrections?.length) {
      const lastUser = [...messages.value].reverse().find((m) => m.role === "user");
      if (lastUser) lastUser.corrections = res.corrections;
    }
    scrollDown();
    if (autoSpeak.value && !coach.value?.voiceless && res.reply) {
      speech.speak(res.reply, coach.value.ttsLang);
    }
    // 刷新側欄
    if (res.new_vocab?.length) loadVocab();
    if (res.homework) loadHomework();
    loadSessions();
  } catch (e: any) {
    messages.value.push({ role: "coach", content: `⚠️ ${e?.data?.message || e?.message || "對話失敗"}`, corrections: [] });
    scrollDown();
  } finally {
    sending.value = false;
  }
}

function toggleMic() {
  if (listening.value) {
    speech.stopListening();
  } else {
    speech.startListening(coach.value?.bcp47 || "en-US", (finalText) => {
      input.value = (input.value ? input.value + " " : "") + finalText;
    });
  }
}

function replay(text: string) {
  if (coach.value) speech.speak(text, coach.value.ttsLang);
}

async function setMastery(v: any, n: number) {
  const level = v.mastery_level === n ? n - 1 : n;
  v.mastery_level = level;
  await authedFetch(`/api/lang/vocab/${v.id}`, { method: "PATCH", body: { mastery_level: level } });
}

async function delVocab(v: any) {
  await authedFetch(`/api/lang/vocab/${v.id}`, { method: "DELETE" });
  vocab.value = vocab.value.filter((x) => x.id !== v.id);
}

async function submitHw(h: any) {
  if (!h._draft?.trim()) return;
  h._grading = true;
  try {
    const { homework: updated } = await authedFetch<any>(`/api/lang/homework/${h.id}/submit`, {
      method: "POST",
      body: { submission: h._draft },
    });
    Object.assign(h, updated, { _grading: false });
  } catch (e: any) {
    h._grading = false;
    alert(e?.data?.message || "批改失敗");
  }
}

watch(lang, async () => {
  newSession();
  await tracker.stop();
  tracker.start(lang.value, "speaking", "chat");
  await Promise.all([loadCoachMeta(), loadSessions(), loadVocab(), loadHomework()]);
});

onMounted(async () => {
  // 語音模式自動朗讀；對話練習時間記為「說」技能
  autoSpeak.value = voiceMode.value;
  tracker.start(lang.value, "speaking", "chat");
  await Promise.all([loadCoachMeta(), loadSessions(), loadVocab(), loadHomework()]);

  // 從首頁「今日推薦」帶進來的話題／情境 → 自動開場（新對話）
  const presetTopic = route.query.topic as string | undefined;
  const presetScenario = route.query.scenario as string | undefined;
  if (presetScenario) {
    startScenario(presetScenario);
  } else if (presetTopic) {
    input.value =
      mode.value === "qa"
        ? presetTopic
        : `我想用${coach.value?.langLabel || ""}聊聊這個話題：「${presetTopic}」`;
    send();
  }
});
</script>
