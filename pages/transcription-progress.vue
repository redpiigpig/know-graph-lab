<template>
  <div class="min-h-screen bg-gray-50">
    <AppHeader title="轉錄與翻譯進度" :back="{ to: '/', label: '返回主頁' }" />

    <div class="max-w-5xl mx-auto px-4 py-8 space-y-8">
      <div v-if="pending" class="space-y-3 animate-pulse">
        <div v-for="i in 6" :key="i" class="h-16 bg-gray-200 rounded-xl"></div>
      </div>

      <div v-else-if="error" class="bg-amber-50 border border-amber-200 rounded-xl p-6 text-sm text-amber-800">
        進度資料尚未產生。夜間排程（02:30）或每日 OCR 排程跑過後會自動更新；
        也可手動跑 <code class="bg-amber-100 px-1 rounded">python scripts/push_transcription_progress.py</code>。
      </div>

      <template v-else-if="data">
        <p class="text-xs text-gray-400">
          資料時間：{{ fmtTime(data.generated_at) }}（由每日排程與夜間品質任務自動更新）
        </p>

        <!-- ── 重轉錄佇列 ─────────────────────────────── -->
        <section class="bg-white border border-gray-200 rounded-2xl p-6 space-y-4">
          <div class="flex items-center justify-between gap-3 flex-wrap">
            <h2 class="text-lg font-semibold text-gray-900">🔁 電子書重轉錄佇列</h2>
            <NuxtLink to="/ebook" class="text-xs text-blue-600 hover:underline">→ 電子圖書館</NuxtLink>
          </div>

          <!-- 全館品質 tier 分佈 -->
          <div class="grid grid-cols-2 sm:grid-cols-5 gap-3">
            <div v-for="t in tierCards" :key="t.key"
              :class="['rounded-xl border p-3 text-center', t.cls]">
              <div class="text-2xl font-bold">{{ data.reocr.tier_counts[t.key] ?? 0 }}</div>
              <div class="text-xs mt-0.5 truncate">{{ t.label }}</div>
            </div>
          </div>

          <!-- 重轉狀態機 -->
          <div>
            <h3 class="text-sm font-medium text-gray-700 mb-2">重轉錄狀態（夜間每晚最多 5 本）</h3>
            <div v-if="!Object.keys(data.reocr.ledger_states || {}).length"
              class="text-sm text-gray-400">
              尚未開始重轉——等 Gemini 額度補上後由 02:30 排程自動消化 REOCR 佇列。
            </div>
            <div v-else class="flex flex-wrap gap-2">
              <span v-for="(n, st) in data.reocr.ledger_states" :key="st"
                :class="['text-xs px-2 py-1 rounded border',
                  st === 'done' ? 'bg-emerald-50 border-emerald-200 text-emerald-700'
                  : st === 'rejected' || st === 'ocr_failed' ? 'bg-red-50 border-red-200 text-red-700'
                  : 'bg-blue-50 border-blue-200 text-blue-700']">
                {{ stateLabel(st as string) }}：{{ n }}
              </span>
            </div>
            <ul v-if="data.reocr.recent?.length" class="mt-3 space-y-1">
              <li v-for="(r, i) in data.reocr.recent" :key="i"
                class="text-xs text-gray-500 flex items-center gap-2">
                <span :class="['w-1.5 h-1.5 rounded-full flex-shrink-0',
                  r.state === 'done' ? 'bg-emerald-500'
                  : r.state === 'rejected' ? 'bg-red-500' : 'bg-blue-400']"></span>
                <span class="truncate">{{ r.title }}</span>
                <span class="text-gray-400 flex-shrink-0">{{ stateLabel(r.state) }}‧{{ fmtTime(r.updated_at) }}</span>
              </li>
            </ul>
          </div>
        </section>

        <!-- ── 全集翻譯 ──────────────────────────────── -->
        <section v-for="corpus in data.translation" :key="corpus.name"
          class="bg-white border border-gray-200 rounded-2xl p-6 space-y-4">
          <div class="flex items-center justify-between gap-3 flex-wrap">
            <h2 class="text-lg font-semibold text-gray-900">
              📚 {{ corpus.name }}
              <span class="text-sm font-normal text-gray-400 ml-2">{{ corpus.works_done }}/{{ corpus.works_total }} 部完成</span>
            </h2>
            <NuxtLink to="/collected-works" class="text-xs text-blue-600 hover:underline">→ 全集</NuxtLink>
          </div>

          <div class="space-y-2">
            <div v-for="w in corpus.works" :key="w.slug" class="flex items-center gap-3">
              <span class="text-sm text-gray-700 w-48 sm:w-64 truncate flex-shrink-0" :title="w.title">
                {{ w.done ? '✅' : w.paras_zh > 0 ? '⏳' : '⬜' }} {{ w.title }}
              </span>
              <div class="flex-1 h-2.5 bg-gray-100 rounded-full overflow-hidden">
                <div :class="['h-full rounded-full transition-all',
                    w.done ? 'bg-emerald-500' : w.paras_zh > 0 ? 'bg-blue-500' : 'bg-gray-200']"
                  :style="{ width: pct(w) + '%' }"></div>
              </div>
              <span class="text-xs text-gray-400 w-24 text-right flex-shrink-0">
                {{ w.paras_total ? `${w.paras_zh}/${w.paras_total} 段` : '未開始' }}
              </span>
            </div>
          </div>
        </section>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" });
useHead({ title: "轉錄與翻譯進度" });

interface WorkRow { slug: string; title: string; done: boolean; sections: number; paras_total: number; paras_zh: number }
interface Corpus { name: string; works_total: number; works_done: number; works: WorkRow[] }
interface Progress {
  generated_at: string;
  reocr: {
    tier_counts: Record<string, number>;
    tiers_generated_at?: string;
    ledger_states: Record<string, number>;
    recent: { title: string; state: string; updated_at?: string }[];
  };
  translation: Corpus[];
}

const { data, pending, error } = useFetch<Progress>("/api/transcription-progress");

const tierCards = [
  { key: "GOOD", label: "良好", cls: "bg-emerald-50 border-emerald-200 text-emerald-700" },
  { key: "FAIR", label: "普通", cls: "bg-gray-50 border-gray-200 text-gray-600" },
  { key: "FIX_TOC", label: "待補目錄", cls: "bg-sky-50 border-sky-200 text-sky-700" },
  { key: "RESTANDARDIZE", label: "待重標準化", cls: "bg-amber-50 border-amber-200 text-amber-700" },
  { key: "REOCR", label: "待重轉錄", cls: "bg-red-50 border-red-200 text-red-700" },
];

const STATE_ZH: Record<string, string> = {
  pending: "排隊中", ocr_staged: "已轉錄待驗", validated: "已過品質閘",
  swapped: "已上線", restandardized: "已重排版", done: "完成",
  rejected: "品質未過", ocr_failed: "轉錄失敗",
};
const stateLabel = (s: string) => STATE_ZH[s] ?? s;

function pct(w: WorkRow): number {
  if (w.done) return 100;
  if (!w.paras_total) return 0;
  return Math.round((w.paras_zh / w.paras_total) * 100);
}
function fmtTime(iso?: string): string {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString("zh-TW", { hour12: false, month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit" });
  } catch { return iso; }
}
</script>
