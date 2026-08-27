<template>
  <div class="min-h-dvh bg-[#f4f0e7] text-stone-900">
    <AppHeader title="線上翻卡" :back="{ to: '/original-readers', label: '原文讀本總覽' }" container-class="max-w-5xl" />

    <main class="mx-auto w-full max-w-5xl px-5 py-8 sm:px-8">
      <section class="rounded-[2rem] border border-stone-300 bg-[#17231f] px-6 py-7 text-[#f7f0df] shadow-xl sm:px-9">
        <p class="text-xs font-semibold tracking-[0.26em] text-amber-300">FLASHCARDS</p>
        <h1 class="mt-2 font-serif text-2xl font-semibold sm:text-4xl">原文單字卡</h1>
        <p class="mt-3 max-w-2xl text-sm leading-7 text-stone-300">
          與紙本同一份卡表：正面原文、背面圖與繁體中文詞義。認得的按「會了」，認不得的留在牌堆裡再抽。
          進度存在這台裝置的瀏覽器裡，不上傳。
        </p>
      </section>

      <!-- 牌組 -->
      <section class="mt-6">
        <div class="flex flex-wrap gap-2">
          <button
            v-for="item in decks"
            :key="item.deck"
            type="button"
            class="rounded-full border px-4 py-2 text-xs font-semibold transition"
            :class="item.deck === deck
              ? 'border-stone-900 bg-stone-900 text-white'
              : 'border-stone-300 bg-white text-stone-600 hover:border-stone-500'"
            @click="selectDeck(item.deck)"
          >{{ item.title }}<span class="ml-1 text-[10px] opacity-70">{{ item.cards }}</span></button>
        </div>
      </section>

      <div v-if="pending" class="py-20 text-center text-sm text-stone-500">載入卡表…</div>
      <div v-else-if="error" class="mt-6 rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">{{ error }}</div>

      <template v-else-if="current">
        <!-- 課次與模式 -->
        <section class="mt-4 flex flex-wrap items-center gap-2 text-xs">
          <label class="flex items-center gap-2 rounded-full border border-stone-300 bg-white px-3 py-1.5">
            <span class="text-stone-500">課次</span>
            <select v-model="lesson" class="bg-transparent font-semibold outline-none">
              <option value="">全部</option>
              <option v-for="value in lessons" :key="value" :value="value">{{ value }}</option>
            </select>
          </label>
          <button type="button" class="rounded-full border border-stone-300 bg-white px-3 py-1.5 font-semibold hover:border-stone-500" @click="shuffle">洗牌</button>
          <button type="button" class="rounded-full border border-stone-300 bg-white px-3 py-1.5 font-semibold hover:border-stone-500" @click="resetProgress">清除這副的進度</button>
          <span class="rounded-full bg-stone-200 px-3 py-1.5 font-semibold text-stone-700">
            剩 {{ queue.length }} 張 · 會了 {{ knownCount }}
          </span>
        </section>

        <!-- 卡片 -->
        <section v-if="card" class="mt-6">
          <div
            class="mx-auto flex min-h-[22rem] w-full max-w-xl cursor-pointer select-none flex-col items-center justify-center gap-5 rounded-[2rem] border border-stone-300 bg-white px-8 py-10 text-center shadow-lg transition hover:shadow-xl"
            role="button"
            tabindex="0"
            @click="flipped = !flipped"
            @keydown.space.prevent="flipped = !flipped"
            @keydown.enter.prevent="flipped = !flipped"
          >
            <template v-if="!flipped">
              <p class="text-[11px] font-semibold tracking-[0.24em] text-stone-400">正面</p>
              <p :class="frontClass">{{ card.front }}</p>
              <p class="text-xs text-stone-400">第 {{ card.lesson }} 課　·　點一下翻面</p>
            </template>
            <template v-else>
              <img
                v-if="card.art"
                :src="`/flashcards-art/${card.art}`"
                alt=""
                class="h-28 w-28 object-contain"
                loading="lazy"
              >
              <p class="font-serif text-2xl font-semibold leading-9 text-stone-900 sm:text-3xl">{{ card.zh }}</p>
              <p v-if="card.pos" class="text-sm text-stone-500">{{ card.pos }}</p>
              <p class="text-xs text-stone-400">第 {{ card.lesson }} 課</p>
            </template>
          </div>

          <div class="mx-auto mt-5 flex max-w-xl gap-3">
            <button
              type="button"
              class="flex-1 rounded-2xl border border-stone-300 bg-white px-4 py-3 text-sm font-semibold text-stone-700 transition hover:border-stone-500"
              @click="again"
            >再看一次</button>
            <button
              type="button"
              class="flex-1 rounded-2xl border border-emerald-300 bg-emerald-50 px-4 py-3 text-sm font-semibold text-emerald-900 transition hover:border-emerald-500"
              @click="markKnown"
            >會了</button>
          </div>
          <p class="mt-3 text-center text-xs text-stone-400">鍵盤：空白鍵翻面、← 再看一次、→ 會了</p>
        </section>

        <section v-else class="mt-8 rounded-3xl border border-emerald-200 bg-emerald-50 p-8 text-center">
          <p class="font-serif text-xl font-semibold text-emerald-900">這一疊都認得了</p>
          <p class="mt-2 text-sm text-emerald-800">換個課次或按「清除這副的進度」重來。</p>
        </section>

        <p class="mt-8 text-center text-[11px] leading-5 text-stone-400">
          卡面圖出自 OpenMoji 17.0.0，CC BY-SA 4.0。卡表與紙本 PDF 同一份資料。
        </p>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" });
useHead({
  title: "線上翻卡 — 原文單字卡",
  meta: [{ name: "robots", content: "noindex,nofollow,noarchive" }],
});

interface Card { front: string; zh: string; pos: string; lesson: string; art: string }
interface Deck {
  deck: string; title: string; language: "hbo" | "grc" | "la";
  lessons: string[]; cards: Card[];
}

const decks = ref<{ deck: string; title: string; cards: number }[]>([]);
const current = ref<Deck | null>(null);
const deck = ref("hbo");
const lesson = ref("");
const queue = ref<number[]>([]);
const known = ref<Set<string>>(new Set());
const flipped = ref(false);
const pending = ref(true);
const error = ref("");

const card = computed(() => (current.value && queue.value.length
  ? current.value.cards[queue.value[0]]
  : null));
const lessons = computed(() => current.value?.lessons ?? []);
const knownCount = computed(() => known.value.size);

// 三種文字的字級不一樣：希伯來與希臘的字母比漢字小得多，同一個級數印出來
// 希伯來那面幾乎看不清楚。這與紙本卡片的級數階梯是同一個道理。
const frontClass = computed(() => {
  const language = current.value?.language;
  if (language === "hbo") return "hebrew-title text-5xl leading-tight sm:text-6xl";
  if (language === "grc") return "greek text-4xl leading-tight sm:text-5xl";
  return "font-serif text-3xl leading-snug sm:text-4xl";
});

function storageKey(name: string) {
  return `flashcards:known:${name}`;
}

function loadKnown(name: string) {
  // 進度只存在這台裝置。讀不到（無痕視窗、清過資料）就當作全新開始。
  try {
    const raw = localStorage.getItem(storageKey(name));
    known.value = new Set(raw ? (JSON.parse(raw) as string[]) : []);
  } catch {
    known.value = new Set();
  }
}

function saveKnown() {
  try {
    localStorage.setItem(storageKey(deck.value), JSON.stringify([...known.value]));
  } catch {
    // 存不了就算了，翻卡本身照常。
  }
}

function rebuildQueue() {
  if (!current.value) return;
  const indexes = current.value.cards
    .map((item, index) => ({ item, index }))
    .filter(({ item }) => !lesson.value || item.lesson === lesson.value)
    .filter(({ item }) => !known.value.has(item.front))
    .map(({ index }) => index);
  queue.value = indexes;
  shuffle();
}

function shuffle() {
  const list = [...queue.value];
  for (let i = list.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [list[i], list[j]] = [list[j], list[i]];
  }
  queue.value = list;
  flipped.value = false;
}

function again() {
  if (queue.value.length < 2) { flipped.value = false; return; }
  const [head, ...rest] = queue.value;
  // 沒記住的排到後面，但不是最後——隔幾張再遇到才是複習。
  const at = Math.min(rest.length, 4);
  queue.value = [...rest.slice(0, at), head, ...rest.slice(at)];
  flipped.value = false;
}

function markKnown() {
  if (!card.value) return;
  known.value.add(card.value.front);
  known.value = new Set(known.value);
  saveKnown();
  queue.value = queue.value.slice(1);
  flipped.value = false;
}

function resetProgress() {
  known.value = new Set();
  saveKnown();
  rebuildQueue();
}

async function loadDeck(name: string) {
  pending.value = true;
  error.value = "";
  try {
    current.value = await $fetch<Deck>(`/content/flashcards/${name}.json`);
    loadKnown(name);
    rebuildQueue();
  } catch (cause: any) {
    error.value = cause?.message || "卡表載入失敗";
  } finally {
    pending.value = false;
  }
}

function selectDeck(name: string) {
  deck.value = name;
  lesson.value = "";
  loadDeck(name);
}

function onKey(event: KeyboardEvent) {
  if (event.key === " ") { event.preventDefault(); flipped.value = !flipped.value; }
  if (event.key === "ArrowLeft") again();
  if (event.key === "ArrowRight") markKnown();
}

watch(lesson, rebuildQueue);

onMounted(async () => {
  try {
    const index = await $fetch<{ decks: { deck: string; title: string; cards: number }[] }>(
      "/content/flashcards/index.json",
    );
    decks.value = index.decks;
  } catch {
    decks.value = [];
  }
  await loadDeck(deck.value);
  window.addEventListener("keydown", onKey);
});

onBeforeUnmount(() => window.removeEventListener("keydown", onKey));
</script>
