<template>
  <div class="min-h-dvh bg-[#f4f0e7] text-stone-900">
    <AppHeader title="附錄對照表" :back="{ to: '/original-readers/hbo-lessons', label: '50課總覽' }" container-class="max-w-6xl" />

    <main class="mx-auto w-full max-w-6xl px-4 py-7 sm:px-8">
      <div v-if="pending" class="py-20 text-center text-sm text-stone-500">載入附錄對照表…</div>
      <div v-else-if="error" class="rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">{{ error }}</div>

      <template v-else-if="payload">
        <header class="overflow-hidden rounded-[2rem] border border-stone-300 bg-[#17231f] px-6 py-9 text-[#f7f0df] shadow-xl sm:px-10">
          <p class="text-xs font-semibold tracking-[0.26em] text-amber-300">PRIVATE APPENDIX · REFERENCE TABLES</p>
          <h1 class="mt-3 font-serif text-3xl font-semibold sm:text-5xl">附錄對照表</h1>
          <p class="mt-3 max-w-3xl text-sm leading-7 text-stone-300">{{ payload.note }}</p>
          <div class="mt-6 flex flex-wrap gap-2 text-xs">
            <span v-for="table in payload.tables" :key="table.id" class="rounded-full border border-stone-500 px-3 py-1.5">
              {{ table.titleZh }} · {{ table.entryCount }}條
            </span>
          </div>
        </header>

        <nav class="mt-6 rounded-3xl border border-stone-300 bg-[#fffdf7] p-5 shadow-sm" aria-label="附錄目錄">
          <p class="text-[11px] font-bold tracking-[0.2em] text-stone-400">CONTENTS</p>
          <ol class="mt-3 grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
            <li v-for="table in payload.tables" :key="table.id">
              <a :href="`#${table.id}`" class="flex h-full flex-col gap-1 rounded-xl border border-stone-200 bg-white px-3 py-2.5 transition hover:border-amber-300 hover:bg-amber-50">
                <strong class="text-xs leading-5 break-words">{{ table.titleZh }}</strong>
                <span class="hebrew-title text-sm text-stone-500" dir="rtl" lang="hbo">{{ table.titleHe }}</span>
              </a>
            </li>
          </ol>
        </nav>

        <article class="mt-6 space-y-6">
          <section v-for="table in payload.tables" :id="table.id" :key="table.id" class="scroll-mt-5 overflow-hidden rounded-3xl border border-stone-300 bg-[#fffdf7] shadow-sm">
            <header class="border-b border-stone-200 bg-stone-50 px-5 py-5 sm:px-7">
              <h2 class="font-serif text-2xl font-semibold">{{ table.titleZh }}</h2>
              <p class="hebrew-title mt-1 text-2xl text-stone-600" dir="rtl" lang="hbo">{{ table.titleHe }}</p>
              <p class="mt-3 text-xs leading-6 text-stone-600">{{ table.intro }}</p>
            </header>

            <div v-for="group in table.groups" :key="group.id" class="border-t border-stone-200 px-5 py-5 first:border-t-0 sm:px-7">
              <h3 class="text-sm font-semibold text-stone-900">{{ group.titleZh }}</h3>
              <p v-if="group.note" class="mt-1 text-xs leading-6 text-stone-500">{{ group.note }}</p>
              <p v-if="group.source" class="mt-1 text-xs leading-6 text-amber-800">{{ group.source }}</p>

              <div class="mt-3 overflow-x-auto">
                <table class="w-full min-w-[34rem] border-collapse text-left text-xs">
                  <thead>
                    <tr class="bg-stone-100 text-[11px] uppercase tracking-wide text-stone-500">
                      <th v-for="header in headersFor(group)" :key="header" class="whitespace-nowrap px-3 py-2 font-semibold">{{ header }}</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-stone-200">
                    <tr v-for="(entry, index) in group.entries" :key="`${group.id}-${index}`" class="align-top">
                      <template v-if="group.shape === 'gender_pair'">
                        <td class="px-3 py-2 font-mono text-stone-500">{{ entry.value }}</td>
                        <td class="hebrew-title px-3 py-2 text-lg" dir="rtl" lang="hbo">{{ entry.masculine?.pointed }}</td>
                        <td class="px-3 py-2 italic text-stone-500">{{ entry.masculine?.transliteration }}</td>
                        <td class="hebrew-title px-3 py-2 text-lg" dir="rtl" lang="hbo">{{ entry.feminine?.pointed }}</td>
                        <td class="px-3 py-2 italic text-stone-500">{{ entry.feminine?.transliteration }}</td>
                        <td class="px-3 py-2 break-words">{{ entry.glossZh }}</td>
                      </template>
                      <template v-else-if="group.shape === 'name'">
                        <td class="hebrew-title px-3 py-2 text-lg" dir="rtl" lang="hbo">{{ entry.pointed }}</td>
                        <td class="px-3 py-2 italic text-stone-500">{{ entry.transliteration }}</td>
                        <td class="px-3 py-2 break-words">{{ entry.glossZh }}</td>
                        <td class="whitespace-nowrap px-3 py-2 text-stone-500">{{ attestation(entry) }}</td>
                        <td class="whitespace-nowrap px-3 py-2 text-stone-500">{{ entry.lesson ? `第${entry.lesson}課` : "—" }}</td>
                      </template>
                      <template v-else>
                        <td class="whitespace-nowrap px-3 py-2 font-mono text-stone-500">{{ entry.value || entry.order || "" }}</td>
                        <td class="hebrew-title px-3 py-2 text-lg" dir="rtl" lang="hbo">{{ entry.pointed }}</td>
                        <td class="px-3 py-2 italic text-stone-500">{{ entry.transliteration }}</td>
                        <td class="px-3 py-2 break-words">{{ entry.glossZh }}</td>
                        <td class="whitespace-nowrap px-3 py-2 text-stone-500">{{ attestation(entry) }}</td>
                      </template>
                    </tr>
                  </tbody>
                </table>
              </div>

              <ul v-if="notesFor(group).length" class="mt-3 space-y-1 text-[11px] leading-6 text-stone-500">
                <li v-for="(entry, index) in notesFor(group)" :key="`note-${group.id}-${index}`">
                  <span class="hebrew-title text-sm text-stone-700" dir="rtl" lang="hbo">{{ entry.pointed || entry.masculine?.pointed }}</span>
                  <span class="ml-2">{{ entry.note }}</span>
                </li>
              </ul>
            </div>

            <a href="#top" class="block border-t border-stone-200 bg-stone-50 px-5 py-3 text-right text-[11px] font-semibold text-stone-500 hover:text-stone-900 sm:px-7">回附錄目錄 ↑</a>
          </section>
        </article>

        <footer class="mt-6 rounded-3xl border border-stone-300 bg-white p-5 text-xs leading-6 text-stone-600">
          <p class="font-semibold text-stone-900">本表來源</p>
          <p v-for="(value, key) in payload.sources" :key="key" class="mt-1">{{ value }}</p>
        </footer>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" });
useHead({
  title: "附錄對照表 — 希伯來文私人讀本",
  meta: [{ name: "robots", content: "noindex,nofollow,noarchive" }],
  bodyAttrs: { id: "top" },
});

interface Entry {
  glossZh: string;
  value?: string;
  order?: string;
  note?: string;
  pointed?: string;
  transliteration?: string;
  attestation?: string;
  formSource?: string;
  frequency?: number;
  firstOccurrence?: string;
  lesson?: number;
  masculine?: { pointed: string; transliteration: string };
  feminine?: { pointed: string; transliteration: string };
}
interface Group { id: string; titleZh: string; shape: string; note?: string; source?: string; entries: Entry[] }
interface Table { id: string; titleZh: string; titleHe: string; intro: string; groups: Group[]; entryCount: number }
interface Payload { titleZh: string; note: string; sources: Record<string, string>; tables: Table[] }

const HEADERS: Record<string, string[]> = {
  gender_pair: ["數", "陽性形", "音標", "陰性形", "音標", "繁中"],
  name: ["附點形", "音標", "繁中", "首見（次數）", "課"],
  month: ["序位", "附點形", "音標", "繁中月名", "首見（次數）"],
  single: ["項", "附點形", "音標", "繁中", "首見（次數）"],
};

function headersFor(group: Group): string[] {
  return HEADERS[group.shape] || HEADERS.single;
}

function notesFor(group: Group): Entry[] {
  return group.entries.filter((entry) => entry.note);
}

function attestation(entry: Entry): string {
  if (entry.attestation === "post_biblical") return "後期文獻";
  if (entry.formSource === "lexicon") return "詞典引用形";
  if (!entry.firstOccurrence) return "—";
  return `${entry.firstOccurrence}（${entry.frequency}）`;
}

const supabase = useSupabaseClient();
const payload = ref<Payload | null>(null);
const pending = ref(true);
const error = ref("");

onMounted(async () => {
  try {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) return;
    payload.value = await $fetch<Payload>("/api/original-readers/hbo-lessons/tables", {
      headers: { Authorization: `Bearer ${session.access_token}` },
    });
  } catch (cause: any) {
    error.value = cause?.data?.message || cause?.message || String(cause);
  } finally {
    pending.value = false;
  }
});
</script>

<style scoped>
.hebrew-title {
  font-family: "SBL Hebrew", "Noto Serif Hebrew", "Ezra SIL", serif;
  line-height: 1.9;
}
</style>
