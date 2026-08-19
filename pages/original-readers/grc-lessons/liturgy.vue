<template>
  <div class="min-h-dvh bg-[#f5f1ea] text-stone-900">
    <AppHeader
      title="金口聖若望事奉聖禮"
      :back="{ to: '/original-readers/grc-lessons', label: '50 課總覽' }"
      container-class="max-w-5xl"
    />

    <main class="mx-auto w-full max-w-5xl px-5 py-8 sm:px-8">
      <div v-if="pending" class="py-20 text-center text-sm text-stone-500">載入禮儀全文…</div>
      <div v-else-if="error" class="rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">{{ error }}</div>

      <template v-else-if="liturgy">
        <header class="rounded-[2rem] border border-stone-300 bg-[#20303a] px-6 py-8 text-[#f4efe2] shadow-xl sm:px-9">
          <p class="text-xs font-semibold tracking-[0.26em] text-sky-300">APPENDIX · DIVINE LITURGY</p>
          <h1 class="mt-3 font-serif text-2xl font-semibold leading-snug break-words sm:text-4xl">{{ liturgy.title }}</h1>
          <p class="greek mt-2 break-words text-base text-stone-300">{{ liturgy.titleGrc }}</p>
          <p class="mt-4 max-w-3xl text-sm leading-7 text-stone-300">{{ liturgy.placement }}</p>
          <dl class="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-3">
            <div class="rounded-2xl border border-stone-600 bg-white/5 px-4 py-3">
              <dt class="text-[11px] text-stone-400">禮儀段落</dt>
              <dd class="mt-1 text-xl font-semibold">{{ liturgy.summary.sectionCount }}</dd>
            </div>
            <div class="rounded-2xl border border-stone-600 bg-white/5 px-4 py-3">
              <dt class="text-[11px] text-stone-400">全文段數</dt>
              <dd class="mt-1 text-xl font-semibold">{{ liturgy.summary.stepCount }}</dd>
            </div>
            <div class="rounded-2xl border border-stone-600 bg-white/5 px-4 py-3">
              <dt class="text-[11px] text-stone-400">希臘文詞數</dt>
              <dd class="mt-1 text-xl font-semibold">{{ liturgy.summary.wordCount }}</dd>
            </div>
          </dl>
        </header>

        <section class="mt-6 space-y-3 text-xs leading-6 text-stone-600">
          <p class="rounded-2xl border border-stone-300 bg-white p-4 break-words">{{ liturgy.notes.roleDerivation }}</p>
          <p class="rounded-2xl border border-stone-300 bg-white p-4 break-words">{{ liturgy.notes.printedText }}</p>
          <p class="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-amber-900 break-words">{{ liturgy.notes.crossCheck }}</p>
        </section>

        <nav class="mt-7 rounded-2xl border border-stone-300 bg-white p-4">
          <h2 class="text-xs font-bold tracking-[0.2em] text-stone-400">流程</h2>
          <ol class="mt-3 flex flex-wrap gap-2">
            <li v-for="section in liturgy.sections" :key="section.key">
              <a :href="`#${section.key}`" class="inline-flex rounded-full border border-stone-300 px-3 py-1 text-xs hover:border-stone-500">
                {{ section.label }}
                <span class="ml-2 text-stone-400">{{ section.stepCount }}</span>
              </a>
            </li>
          </ol>
        </nav>

        <section v-for="section in liturgy.sections" :id="section.key" :key="section.key" class="mt-8 scroll-mt-20">
          <h2 class="font-serif text-xl font-semibold break-words">{{ section.label }}</h2>
          <p class="mt-1 text-[11px] text-stone-500">第 {{ section.firstStep }}–{{ section.lastStep }} 段・{{ section.wordCount }} 詞</p>
          <ol class="mt-3 space-y-2">
            <li
              v-for="step in stepsOf(section.key)"
              :key="step.ordinal"
              class="rounded-2xl border bg-white p-4"
              :class="roleClass(step.role)"
            >
              <div class="flex flex-wrap items-center gap-2 text-[11px] text-stone-500">
                <span class="rounded-full px-2 py-0.5 font-semibold" :class="roleBadgeClass(step.role)">{{ step.roleLabel }}</span>
                <span v-if="step.repeatCount">重複 {{ step.repeatCount }} 次</span>
                <span class="text-stone-400" :title="step.roleEvidence">角色由排版推定</span>
              </div>
              <p class="greek mt-2 text-lg leading-9 break-words">{{ step.displayText }}</p>
            </li>
          </ol>
        </section>

        <p class="mt-10 text-xs text-stone-500 break-words">
          底本：{{ liturgy.edition }}
          <a :href="liturgy.sourceUrl" target="_blank" rel="noopener noreferrer" class="underline underline-offset-4">來源 ↗</a>
        </p>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
interface Step {
  ordinal: number; section: string; sectionLabel: string;
  role: string; roleLabel: string; roleEvidence: string;
  kind: string; wordCount: number; displayText: string; repeatCount?: number;
}
interface Section {
  key: string; label: string; firstStep: number; lastStep: number; stepCount: number; wordCount: number;
}
interface Liturgy {
  title: string; titleGrc: string; placement: string; edition: string; sourceUrl: string;
  notes: { roleDerivation: string; printedText: string; crossCheck: string };
  summary: { stepCount: number; wordCount: number; sectionCount: number };
  sections: Section[];
  steps: Step[];
}

const supabase = useSupabaseClient();
const liturgy = ref<Liturgy | null>(null);
const pending = ref(true);
const error = ref("");

function stepsOf(sectionKey: string) {
  return (liturgy.value?.steps || []).filter((step) => step.section === sectionKey);
}

function roleClass(role: string) {
  if (role.startsWith("διάκονος")) return "border-sky-200";
  if (role.startsWith("χορὸς")) return "border-emerald-200";
  if (role.startsWith("κοινωνία")) return "border-orange-200";
  return "border-stone-200";
}
function roleBadgeClass(role: string) {
  if (role.startsWith("διάκονος")) return "bg-sky-100 text-sky-800";
  if (role.startsWith("χορὸς")) return "bg-emerald-100 text-emerald-800";
  if (role.startsWith("κοινωνία")) return "bg-orange-100 text-orange-800";
  return "bg-stone-100 text-stone-700";
}

async function load() {
  pending.value = true;
  error.value = "";
  try {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) return;
    liturgy.value = await $fetch<Liturgy>("/api/original-readers/grc-lessons/liturgy", {
      headers: { Authorization: `Bearer ${session.access_token}` },
    });
    useHead({ title: `${liturgy.value.title} — 希臘文讀本附錄` });
  } catch (cause: any) {
    error.value = cause?.data?.message || cause?.message || String(cause);
  } finally {
    pending.value = false;
  }
}

onMounted(load);
</script>

<style scoped>
.greek {
  font-family: "SBL Greek", "New Athena Unicode", "Gentium Plus", "Noto Serif", serif;
  text-wrap: pretty;
}
</style>
