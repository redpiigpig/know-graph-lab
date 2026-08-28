<template>
  <span class="inline">
    <template v-for="(word, index) in words" :key="index">
      <span
        class="relative inline-block cursor-help rounded px-0.5 transition hover:bg-amber-100"
        tabindex="0"
        @mouseenter="open = index"
        @mouseleave="open = null"
        @focus="open = index"
        @blur="open = null"
        @click="open = open === index ? null : index"
      >{{ word.text }}<span
          v-if="open === index"
          class="absolute left-1/2 top-full z-30 mt-1 w-72 -translate-x-1/2 rounded-xl border border-stone-300 bg-white px-3 py-2 text-left text-sm leading-6 text-stone-700 shadow-xl"
          dir="ltr"
        >
          <span class="block font-semibold text-stone-900" :class="[scriptClass, language === 'hbo' ? 'text-2xl leading-relaxed' : 'text-lg']">{{ word.lemma }}</span>
          <span v-if="word.features?.length" class="mt-1.5 grid grid-cols-[3.5rem_1fr] gap-x-2 gap-y-0.5 text-xs">
            <template v-for="(item, position) in word.features" :key="position">
              <span class="text-stone-400">{{ item.label }}</span>
              <span class="font-medium text-stone-700">{{ item.value }}</span>
            </template>
          </span>
          <span v-else class="mt-0.5 block text-xs text-stone-500">
            {{ word.pos }}<template v-if="word.parsing"> · {{ word.parsing }}</template>
          </span>
          <span v-if="word.strong" class="mt-1 block text-[11px] text-stone-400">{{ word.strong }}</span>
          <span v-if="word.zh" class="mt-1 block break-words text-stone-800">{{ word.zh }}</span>
          <span v-else class="mt-1 block text-stone-400">（本站尚未收錄此字的中文詞義）</span>
          <span v-if="word.en" class="mt-0.5 block break-words text-xs text-stone-500">{{ word.en }}</span>
        </span></span><span v-if="index < words.length - 1"> </span>
    </template>
  </span>
</template>

<script setup lang="ts">
// 逐詞詞形分析的顯示層。詞形分析一律有（MorphGNT／OSHB 標的），中文詞義只在
// 本站覆核過的詞表裡有；沒有就明說沒有，不要留一個看起來像沒查到的空白。
interface MorphWord {
  text: string;
  lemma: string;
  strong?: string;
  pos: string;
  parsing: string;
  features?: { label: string; value: string }[];
  zh?: string;
  en?: string;
}

const props = defineProps<{ words: MorphWord[]; language: "grc" | "hbo" }>();
const open = ref<number | null>(null);
const scriptClass = computed(() => (props.language === "hbo" ? "hebrew-title" : "greek"));
</script>
