<template>
  <div class="min-h-dvh bg-[#f4f0e7] text-stone-900">
    <AppHeader title="附錄參考表" :back="{ to: '/original-readers/lat-lessons', label: '拉丁文讀本' }" container-class="max-w-6xl" />

    <main class="mx-auto w-full max-w-6xl px-4 py-7 sm:px-8">
      <div v-if="pending" class="py-20 text-center text-sm text-stone-500">載入附錄參考表…</div>
      <div v-else-if="error" class="rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">{{ error }}</div>

      <template v-else-if="payload">
        <header class="overflow-hidden rounded-[2rem] border border-stone-300 bg-[#17231f] px-6 py-9 text-[#f7f0df] shadow-xl sm:px-10">
          <p class="text-xs font-semibold tracking-[0.26em] text-amber-300">PRIVATE APPENDIX · REFERENCE TABLES</p>
          <h1 class="mt-3 font-serif text-3xl font-semibold sm:text-5xl">附錄參考表</h1>
          <p class="mt-3 max-w-3xl text-sm leading-7 text-stone-300">{{ payload.note }}</p>
        </header>

        <section v-for="volume in payload.volumes" :key="volume.volume" class="mt-8">
          <h2 class="font-serif text-2xl font-semibold break-words">{{ volume.title }}</h2>

          <nav class="mt-4 rounded-3xl border border-stone-300 bg-[#fffdf7] p-5 shadow-sm" :aria-label="`${volume.title}附錄目錄`">
            <ol class="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
              <li v-for="table in volume.tables" :key="table.key">
                <a :href="`#${table.key}`" class="flex h-full flex-col gap-1 rounded-xl border border-stone-200 bg-white px-3 py-2.5 transition hover:border-amber-300 hover:bg-amber-50">
                  <strong class="text-xs leading-5 break-words">{{ table.title }}</strong>
                  <span class="text-[11px] text-stone-500">{{ table.entryCount }} 條 · {{ table.groups.length }} 節</span>
                </a>
              </li>
            </ol>
          </nav>

          <article class="mt-5 space-y-6">
            <section v-for="table in volume.tables" :id="table.key" :key="table.key" class="scroll-mt-5 overflow-hidden rounded-3xl border border-stone-300 bg-[#fffdf7] shadow-sm">
              <header class="border-b border-stone-200 bg-stone-50 px-5 py-5 sm:px-7">
                <h3 class="font-serif text-xl font-semibold break-words">{{ table.title }}</h3>
                <p class="mt-1 text-xs text-stone-500">{{ table.entryCount }} 條</p>
              </header>

              <div v-for="group in table.groups" :key="`${table.key}-${group.title}`" class="border-t border-stone-200 px-5 py-5 first:border-t-0 sm:px-7">
                <h4 v-if="group.title" class="text-sm font-semibold text-stone-900">
                  {{ group.title }}
                  <span class="ml-2 text-xs font-normal text-stone-500">{{ group.entries.length }} 條</span>
                </h4>

                <div class="mt-3 overflow-x-auto">
                  <table class="w-full min-w-[26rem] border-collapse text-left text-xs">
                    <thead>
                      <tr class="bg-stone-100 text-[11px] uppercase tracking-wide text-stone-500">
                        <th class="whitespace-nowrap px-3 py-2 font-semibold">拉丁文</th>
                        <th class="whitespace-nowrap px-3 py-2 font-semibold">繁體中文</th>
                        <th class="whitespace-nowrap px-3 py-2 font-semibold">出現次數</th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-stone-200">
                      <tr v-for="(entry, index) in group.entries" :key="`${group.title}-${index}`" class="align-top">
                        <td class="latin px-3 py-2 text-base break-words">
                          <button
                            v-if="audio.deviceSupported.value"
                            type="button"
                            class="mr-1 align-middle text-xs text-stone-400 transition hover:text-stone-800"
                            :aria-label="`朗讀 ${entry.headword}`"
                            @click="audio.speakOne('la', entry.headword)"
                          >🔊</button>{{ entry.headword }}
                        </td>
                        <!-- 中文缺就留白。缺就該看得出來缺，不用英文頂替。 -->
                        <td class="px-3 py-2 break-words" :class="entry.zh ? '' : 'text-stone-400'">{{ entry.zh || "（中文待補）" }}</td>
                        <td class="px-3 py-2 font-mono text-stone-500">{{ entry.frequency ?? "—" }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </section>
          </article>
        </section>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
// 附錄裡的月份、數字、親屬稱謂都是要唸出來記的，逐條給一個喇叭。
const audio = useOriginalReaderAudio();

interface Entry {
  headword: string;
  zh: string;
  frequency: number | null;
}

interface Payload {
  title: string;
  note: string;
  volumes: {
    volume: number;
    title: string;
    tables: {
      key: string;
      title: string;
      entryCount: number;
      groups: { title: string; entries: Entry[] }[];
    }[];
  }[];
}

const payload = ref<Payload | null>(null);
const pending = ref(true);
const error = ref("");

onMounted(async () => {
  try {
    payload.value = await $fetch<Payload>("/api/original-readers/lat-lessons/tables", {
      credentials: "include",
    });
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : "附錄參考表載入失敗";
  } finally {
    pending.value = false;
  }
});

useHead({ title: "附錄參考表 · 教會拉丁文原文讀本" });
</script>

<style scoped>
.latin {
  font-family: "Noto Serif", Georgia, serif;
}
</style>
