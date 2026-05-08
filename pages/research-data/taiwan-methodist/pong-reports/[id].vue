<template>
  <div v-if="report" class="min-h-screen bg-slate-50">

    <nav class="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div class="max-w-6xl mx-auto px-6 h-14 flex items-center gap-4">
        <NuxtLink to="/research-data/taiwan-methodist/pong-reports" class="text-gray-400 hover:text-gray-700 transition text-sm">← 龐君華牧師歷年事工報告</NuxtLink>
        <span class="text-gray-200">|</span>
        <span class="text-sm font-medium text-gray-700 truncate">第 {{ report.sessionNumber }} 屆 · {{ report.title }}</span>
      </div>
    </nav>

    <div class="max-w-6xl mx-auto px-6 py-8 grid grid-cols-1 lg:grid-cols-[200px_1fr] gap-8">

      <!-- TOC -->
      <aside class="hidden lg:block sticky top-20 self-start">
        <p class="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-2">目錄</p>
        <ul class="space-y-1 text-sm">
          <li v-for="s in tocItems" :key="s.id">
            <a
              :href="`#${s.id}`"
              :class="[
                'block py-0.5 transition no-underline hover:text-rose-600',
                s.level === 2 ? 'text-gray-700 font-medium' : 'text-gray-500 pl-3 text-xs',
              ]"
            >{{ s.title }}</a>
          </li>
        </ul>
      </aside>

      <!-- Main content -->
      <article class="min-w-0">
        <!-- Header -->
        <header class="mb-8 pb-6 border-b border-gray-200">
          <div class="flex flex-wrap items-center gap-2 mb-3 text-xs">
            <span class="font-medium px-2.5 py-1 rounded-full bg-rose-100 text-rose-700">第 {{ report.sessionNumber }} 屆</span>
            <span class="text-gray-500">{{ report.sessionYear }}</span>
            <span class="text-gray-300">·</span>
            <span class="text-gray-500">{{ report.sessionMeetingTitle }}</span>
            <span class="text-gray-300">·</span>
            <span class="text-gray-500">頁 {{ report.sourcePages }}</span>
          </div>
          <h1 class="text-2xl font-bold text-gray-900 mb-2 leading-tight">{{ report.title }}</h1>
          <p class="text-sm text-gray-600">
            <span class="font-medium text-gray-900">龐君華</span>
            <span class="text-gray-500 ml-1">{{ report.authorRole }}</span>
            <span v-if="report.unit" class="text-gray-400 ml-3">· {{ report.unit }}</span>
          </p>
        </header>

        <!-- Intro -->
        <section v-if="report.intro?.length" class="mb-10 space-y-3">
          <p v-for="(p, i) in report.intro" :key="i" class="text-[15px] leading-loose text-gray-800 indent-8">{{ p }}</p>
        </section>

        <!-- Sections -->
        <section
          v-for="s in report.sections" :key="s.id" :id="s.id"
          :class="[
            s.level === 2 ? 'mt-10 mb-4' : s.level === 3 ? 'mt-6 mb-3' : 'mt-4 mb-2 pl-4',
          ]"
        >
          <component
            :is="s.level === 2 ? 'h2' : s.level === 3 ? 'h3' : 'h4'"
            :class="[
              'text-gray-900 font-semibold flex items-baseline gap-2 scroll-mt-20',
              s.level === 2 ? 'text-lg pb-1.5 border-b border-rose-200' : s.level === 3 ? 'text-base' : 'text-sm',
            ]"
          >
            <span>{{ s.title }}</span>
            <span v-if="s.noteAfterTitle" class="text-[10px] font-normal text-gray-400">（編按：{{ s.noteAfterTitle }}）</span>
          </component>

          <!-- Blocks -->
          <div class="mt-2 space-y-3">
            <template v-for="(b, bi) in s.blocks" :key="bi">

              <p v-if="b.type === 'p'" class="text-[15px] leading-loose text-gray-800 indent-8">{{ b.text }}</p>

              <ol v-else-if="b.type === 'list' && b.ordered" class="list-decimal list-outside ml-8 space-y-1 text-[15px] leading-loose text-gray-800">
                <li v-for="(item, ii) in b.items" :key="ii">{{ item }}</li>
              </ol>

              <ul v-else-if="b.type === 'list'" class="list-disc list-outside ml-8 space-y-1 text-[15px] leading-loose text-gray-800">
                <li v-for="(item, ii) in b.items" :key="ii">{{ item }}</li>
              </ul>

              <div v-else-if="b.type === 'table'" class="overflow-x-auto rounded-xl border border-gray-200 bg-white">
                <table class="min-w-full text-sm">
                  <thead class="bg-slate-100 text-gray-600 text-xs uppercase tracking-wider">
                    <tr>
                      <th v-for="h in b.headers" :key="h" class="px-3 py-2 text-left font-medium whitespace-nowrap">{{ h }}</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-100">
                    <tr v-for="(row, ri) in b.rows" :key="ri">
                      <td v-for="(cell, ci) in row" :key="ci" class="px-3 py-2 align-top text-gray-800 leading-relaxed">{{ cell }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <p v-else-if="b.type === 'note'" class="text-xs text-gray-500 italic pl-4 border-l-2 border-gray-200">{{ b.text }}</p>

              <blockquote v-else-if="b.type === 'callout'" class="my-2 mx-2 sm:mx-6 p-4 sm:p-5 rounded-2xl bg-rose-50 border border-rose-200 text-[15px] leading-relaxed text-rose-900 font-medium">
                <span class="text-rose-300 mr-1">「</span>{{ b.text }}<span class="text-rose-300 ml-1">」</span>
              </blockquote>

              <figure v-else-if="b.type === 'tree'" class="my-3 p-4 sm:p-6 rounded-2xl border border-gray-200 bg-gradient-to-br from-slate-50 to-white overflow-x-auto">
                <figcaption v-if="b.caption" class="text-sm font-medium text-gray-700 mb-3 text-center">{{ b.caption }}</figcaption>
                <ul class="text-sm">
                  <OrgTree :node="b.root" :depth="0" />
                </ul>
              </figure>

              <WeiLanFlowchart v-else-if="b.type === 'flowchart' && b.chartId === 'wei-lan-metro'" />
              <MethodistGrowthFlowchart v-else-if="b.type === 'flowchart' && b.chartId === 'methodist-growth'" />

            </template>
          </div>
        </section>

      </article>
    </div>
  </div>

  <div v-else class="min-h-screen bg-slate-50 flex items-center justify-center text-gray-500">
    找不到該份報告。<NuxtLink to="/research-data/taiwan-methodist/pong-reports" class="text-rose-600 hover:underline ml-2">回列表</NuxtLink>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' });

const route = useRoute();
const { findById } = usePongReports();
const report = computed(() => findById(route.params.id as string));

useHead(() => ({
  title: report.value
    ? `${report.value.title} · 第 ${report.value.sessionNumber} 屆 — Know Graph Lab`
    : '報告未找到 — Know Graph Lab',
}));

const tocItems = computed(() =>
  report.value
    ? report.value.sections.filter(s => s.level !== 4).map(s => ({ id: s.id, title: s.title, level: s.level }))
    : []
);
</script>
