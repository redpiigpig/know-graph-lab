<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader title="編纂凡例與分類標準" :back="{ to: '/dazangjing', label: '基督教大藏經' }" container-class="max-w-4xl" />

    <div class="flex-1 max-w-4xl w-full mx-auto px-6 py-10">
      <header class="mb-10">
        <h1 class="text-2xl font-bold text-gray-900 mb-2">📖 編纂凡例與分類標準</h1>
        <p class="text-sm text-gray-600 leading-relaxed">
          《基督教大藏經》仿佛教《大藏經》的彙編體例，依「時代精神」分為五個時代，每代各立十藏，每藏再分「正藏／外藏」兩套平行目錄。
          本頁說明全書的編纂原則，以及每一藏在各時代的收入標準。
        </p>
        <p class="text-xs text-gray-500 leading-relaxed mt-3 border-l-2 border-stone-300 pl-3">
          三軌奠基於「隱密的上帝」與「社會學邊界」：<b>前藏</b>＝邊界劃分之前的原始啟示母體；
          <b>正藏</b>＝群體教會論與社會學邊界之內的家族記憶（非啟示壟斷、非絕對無誤）；
          <b>外藏</b>＝邊界之外、隱密上帝按其自由所開展的平行啟示與神聖見證（「外」無貶義）。
        </p>
      </header>

      <!-- 五時代與時代精神 -->
      <section class="mb-10">
        <h2 class="text-lg font-bold text-gray-900 mb-1">一、五時代與時代精神</h2>
        <p class="text-xs text-gray-500 mb-4 leading-relaxed">{{ ERA_ASSIGNMENT_PRINCIPLE }}</p>
        <div class="space-y-3">
          <div v-for="era in ERAS" :key="era.key" class="flex gap-3 bg-white border border-gray-200 rounded-xl p-4">
            <div class="shrink-0 w-9 h-9 rounded-lg bg-stone-900 text-white flex items-center justify-center text-lg font-serif">{{ era.glyph }}</div>
            <div class="min-w-0">
              <div class="font-semibold text-gray-900 text-sm">{{ era.name }}</div>
              <div v-if="era.boundary" class="text-xs text-gray-600 leading-relaxed mt-0.5">{{ era.boundary }}</div>
              <div v-if="derivedOf(era.key).length" class="text-[11px] text-gray-500 mt-1.5 leading-relaxed">
                <span class="text-gray-400">外藏交鋒對象：</span>{{ derivedOf(era.key).join('、') }}
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 十藏總覽 -->
      <section class="mb-10">
        <h2 class="text-lg font-bold text-gray-900 mb-1">二、十藏總覽</h2>
        <p class="text-xs text-gray-500 mb-4">定稿順序：經‧律‧論‧宣‧函‧儀‧詩‧譯‧史‧類。</p>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          <div v-for="(c, i) in canons" :key="c.key" class="flex gap-3 bg-white border border-gray-200 rounded-lg p-3">
            <div class="shrink-0 w-8 h-8 rounded-md bg-stone-100 text-stone-800 flex items-center justify-center text-base font-serif">{{ c.glyph }}</div>
            <div class="min-w-0">
              <div class="font-semibold text-gray-900 text-sm">{{ i + 1 }}. {{ c.name }}</div>
              <div class="text-xs text-gray-600 leading-relaxed mt-0.5">{{ c.goal }}</div>
            </div>
          </div>
        </div>
      </section>

      <!-- 編纂鐵則 -->
      <section class="mb-10">
        <h2 class="text-lg font-bold text-gray-900 mb-3">三、編纂鐵則</h2>
        <ol class="space-y-2">
          <li v-for="(r, i) in COMPILATION_RULES" :key="i" class="flex gap-2.5 text-sm text-gray-700 leading-relaxed">
            <span class="shrink-0 w-5 h-5 rounded-full bg-stone-800 text-white text-[11px] flex items-center justify-center mt-0.5">{{ i + 1 }}</span>
            <span>{{ r }}</span>
          </li>
        </ol>
      </section>

      <!-- 分類標準的結構原則 -->
      <section class="mb-10">
        <h2 class="text-lg font-bold text-gray-900 mb-3">四、分類標準的結構原則</h2>
        <ul class="space-y-2">
          <li v-for="(n, i) in CLASSIFICATION_NOTES" :key="i" class="flex gap-2.5 text-sm text-gray-700 leading-relaxed">
            <span class="shrink-0 text-stone-400 mt-0.5">▸</span>
            <span>{{ n }}</span>
          </li>
        </ul>
      </section>

      <!-- 各藏收錄標準詳目 -->
      <section>
        <h2 class="text-lg font-bold text-gray-900 mb-3">五、各藏收錄標準詳目</h2>
        <div class="space-y-4">
          <div v-for="c in canons" :key="c.key" class="bg-white border border-gray-200 rounded-2xl p-5">
            <div class="flex items-center gap-2.5 mb-2">
              <div class="shrink-0 w-9 h-9 rounded-lg bg-stone-900 text-white flex items-center justify-center text-lg font-serif">{{ c.glyph }}</div>
              <div class="font-bold text-gray-900">{{ c.name }}</div>
            </div>
            <p class="text-sm text-gray-700 leading-relaxed mb-3">{{ c.goal }}</p>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <div class="text-xs font-semibold text-emerald-700 mb-1.5">正藏收錄</div>
                <ul class="space-y-1">
                  <li v-for="(s, i) in c.zhengScope" :key="i" class="text-xs text-gray-600 leading-relaxed flex gap-1.5">
                    <span class="text-emerald-400">·</span><span>{{ s }}</span>
                  </li>
                </ul>
              </div>
              <div>
                <div class="text-xs font-semibold text-rose-700 mb-1.5">外藏收錄（對話‧衝突‧見證）</div>
                <ul class="space-y-1">
                  <li v-for="(s, i) in c.waiScope" :key="i" class="text-xs text-gray-600 leading-relaxed flex gap-1.5">
                    <span class="text-rose-400">·</span><span>{{ s }}</span>
                  </li>
                </ul>
              </div>
            </div>

            <div v-if="c.sources.length" class="mt-3 pt-3 border-t border-gray-100 text-[11px] text-gray-400 leading-relaxed">
              <span class="text-gray-500">權威來源：</span>{{ c.sources.join('‧') }}
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  ERAS,
  CANON_ORDER,
  COLLECTION_GOALS,
  DERIVED_RELIGIONS_BY_ERA,
  ERA_ASSIGNMENT_PRINCIPLE,
  COMPILATION_RULES,
  CLASSIFICATION_NOTES,
} from '~/data/dazangjing'

const canons = computed(() => CANON_ORDER.map((k) => COLLECTION_GOALS[k]).filter(Boolean))
const derivedOf = (key: string): string[] => DERIVED_RELIGIONS_BY_ERA[key] ?? []

definePageMeta({ middleware: 'auth' })
useHead({ title: '編纂凡例與分類標準 — 基督教大藏經' })
</script>
