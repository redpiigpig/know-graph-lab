<template>
  <div class="min-h-screen bg-slate-50">
    <AppHeader
      title="東方聖書"
      :back="{ to: '/collected-works/max-mueller', label: '← 穆勒全集' }"
      container-class="max-w-5xl"
      :editable="false"
    />

    <div class="max-w-5xl mx-auto px-6 py-12">
      <!-- hero -->
      <div class="mb-10">
        <div class="flex items-center gap-2 text-xs text-gray-400 font-mono mb-2">
          <span>{{ store.meta.span }}</span>
          <span>‧</span>
          <span>{{ store.meta.publisher }}</span>
        </div>
        <h1 class="text-2xl font-bold text-gray-900">{{ store.meta.title }}</h1>
        <p class="text-sm text-gray-400 italic mb-1">{{ store.meta.titleEn }}</p>
        <p class="text-sm text-gray-600">{{ store.meta.editor }}</p>

        <div class="mt-5 space-y-2.5">
          <p v-for="(p, i) in store.meta.intro" :key="i" class="text-sm text-gray-700 leading-relaxed">
            {{ p }}
          </p>
        </div>

        <div class="mt-5 flex items-center gap-3 text-xs">
          <span class="px-2.5 py-1 rounded-full bg-slate-100 text-slate-600 font-medium">
            {{ store.progress.done }}／{{ store.progress.total }} 卷已轉錄
          </span>
          <span class="text-gray-400">全套公有領域，逐卷收入原文／繁中對照</span>
        </div>
      </div>

      <!-- 傳統速覽 chips -->
      <div class="flex flex-wrap gap-2 mb-10">
        <a
          v-for="t in store.traditions"
          :key="t.key"
          :href="`#${t.key}`"
          class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium no-underline transition-colors"
          :class="`bg-${t.color}-50 text-${t.color}-700 hover:bg-${t.color}-100`"
        >
          <span>{{ t.emoji }}</span>{{ t.label }}
          <span class="opacity-60">{{ countOf(t.key) }}</span>
        </a>
      </div>

      <!-- 按傳統分組 -->
      <section v-for="g in store.groups" :key="g.tradition.key" :id="g.tradition.key" class="mb-12 scroll-mt-20">
        <div class="flex items-baseline gap-2 mb-1 pb-2 border-b-2" :class="`border-${g.tradition.color}-200`">
          <span class="text-lg">{{ g.tradition.emoji }}</span>
          <h2 class="text-base font-bold text-gray-800">{{ g.tradition.label }}</h2>
          <span class="text-xs text-gray-400 italic">{{ g.tradition.labelEn }}</span>
          <span class="ml-auto text-xs text-gray-400">{{ g.volumes.length }} 卷</span>
        </div>
        <p class="text-xs text-gray-500 mb-4 leading-relaxed">{{ g.tradition.blurb }}</p>

        <ul class="space-y-2">
          <li v-for="v in g.volumes" :key="v.vol">
            <component
              :is="isReadable(v) ? VolLink : 'div'"
              :to="isReadable(v) ? `/ebook/${v.ebookId}` : undefined"
              class="vol-row group"
              :class="isReadable(v)
                ? `bg-white border-${g.tradition.color}-100 hover:border-${g.tradition.color}-300 hover:shadow-sm cursor-pointer no-underline`
                : 'bg-gray-50/60 border-gray-100'"
            >
              <span
                class="text-[11px] font-mono w-12 flex-shrink-0 text-center self-start py-0.5 rounded"
                :class="`bg-${g.tradition.color}-50 text-${g.tradition.color}-600`"
              >卷 {{ v.vol }}</span>
              <div class="flex-1 min-w-0">
                <div class="text-sm text-gray-800 font-medium leading-snug">{{ v.titleZh }}</div>
                <div class="text-xs text-gray-400 italic truncate">{{ v.titleEn }}</div>
                <div class="text-[11px] text-gray-400 mt-0.5">
                  譯者：{{ v.translatorZh }}<span class="text-gray-300"> · {{ v.translatorEn }}</span> · {{ v.year }}
                </div>
              </div>
              <span
                class="text-[11px] px-2 py-0.5 rounded-full flex-shrink-0 self-start"
                :class="statusClass(v.status)"
              >{{ statusLabel(v.status) }}</span>
            </component>
          </li>
        </ul>
      </section>

      <p class="mt-4 text-center text-xs text-gray-400">
        卷目編號依穆勒原版（Oxford Clarendon, 1879–1910）；繁中卷名為本站擬定，譯者中英並列。
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { SbeVolume, SbeStatus } from '~/stores/sacredBooksEast'

definePageMeta({ middleware: 'auth' })
useHead({ title: '東方聖書 — Know Graph Lab' })

const store = useSacredBooksEastStore()

// Bind the resolved component object (not the string) to <component :is> — see
// the note in collected-works/[slug].vue. String resolution of an auto-imported
// component can render a dead element with no href.
const VolLink = resolveComponent('NuxtLink')

const countOf = (key: string) => store.volumes.filter((v) => v.tradition === key).length

function isReadable(v: SbeVolume): boolean {
  return !!v.ebookId && (v.status === 'done' || v.status === 'in-progress')
}

const STATUS: Record<SbeStatus, { label: string; cls: string }> = {
  done: { label: '已轉錄', cls: 'bg-emerald-50 text-emerald-700' },
  'in-progress': { label: '轉錄中', cls: 'bg-amber-50 text-amber-700' },
  planned: { label: '待轉錄', cls: 'bg-gray-100 text-gray-500' },
}
const statusLabel = (s: SbeStatus) => STATUS[s].label
const statusClass = (s: SbeStatus) => STATUS[s].cls
</script>

<style scoped>
.vol-row {
  @apply flex items-start gap-3 px-3 py-2.5 rounded-xl border transition-all duration-150;
}
</style>

<!-- Dynamic Tailwind colors (bg-${color}-*, text-${color}-*, border-${color}-*) are safelisted in tailwind.config.ts -->
