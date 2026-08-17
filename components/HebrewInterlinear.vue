<template>
  <div>
    <div v-if="tokens.length" dir="rtl" lang="hbo" class="flex flex-wrap items-end gap-x-4 gap-y-4">
      <span v-if="lead" class="mb-1 shrink-0 rounded-md bg-amber-100 px-2 py-0.5 font-mono text-xs font-bold text-amber-900">{{ lead }}</span>
      <span v-for="(token, index) in tokens" :key="index" class="inline-flex flex-col items-center">
        <span class="hebrew-word">{{ token.word }}{{ token.trailing }}</span>
        <span class="gloss">{{ token.glossZh }}</span>
      </span>
    </div>

    <!-- A unit that has not been glossed yet still reads as a complete text. -->
    <p v-else class="hebrew-line whitespace-pre-wrap" dir="rtl" lang="hbo">
      <span v-if="lead" class="mr-2 font-mono text-xs text-stone-400">{{ lead }}</span>{{ fallbackText }}
    </p>

    <p v-if="sense" class="mt-4 border-r-2 border-amber-300 pr-4 text-[15px] leading-8 text-stone-700">
      <span class="mr-2 text-xs font-bold tracking-wider text-amber-800">整句</span>{{ sense }}
    </p>
  </div>
</template>

<script setup lang="ts">
interface InterlinearToken { word: string; trailing: string; glossZh: string }

withDefaults(defineProps<{
  tokens?: InterlinearToken[];
  /** Whole-sentence meaning printed under the word blocks. */
  sense?: string;
  /** Shown when this unit has no gloss layer yet. */
  fallbackText?: string;
  /** Verse or segment number, riding at the start of the first row. */
  lead?: string | number;
}>(), {
  tokens: () => [],
  sense: "",
  fallbackText: "",
  lead: "",
});
</script>

<style scoped>
.hebrew-word,
.hebrew-line {
  font-family: "SBL Hebrew", "Noto Serif Hebrew", "Ezra SIL", serif;
}
.hebrew-word {
  font-size: clamp(1.3rem, 2.2vw, 1.65rem);
  line-height: 1.65;
}
.hebrew-line {
  font-size: clamp(1.35rem, 2.4vw, 1.75rem);
  line-height: 2.15;
  text-wrap: pretty;
}
.gloss {
  margin-top: 0.15rem;
  font-size: 0.8rem;
  line-height: 1.4;
  color: #78716c;
  white-space: nowrap;
}
</style>
