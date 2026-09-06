<template>
  <div class="min-h-screen bg-slate-50">

    <AppHeader title="一貫道研究資料" :back="{ to: '/research-data', label: '論文資料整理' }" container-class="max-w-5xl" />

    <div class="max-w-5xl mx-auto px-6 py-10">
      <div class="mb-6">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-purple-100 text-purple-700">研究資料</span>
          <span class="text-xs text-gray-400">政教關係史的對照案例</span>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 mb-1">一貫道研究資料</h1>
        <p class="text-sm text-gray-500 leading-relaxed">
          一貫道自 1930 年代起在中國被國民政府以「敵偽、附匪、邪教」取締，遷台後續遭查禁，
          直到 1987 年解嚴才合法化。它是「國家如何取締一個宗教」最完整的一條案例，
          與長老教會（被監控但未被查禁）恰成對照——兩者並置，政教關係的光譜才完整。
        </p>
      </div>

      <!-- 分頁 -->
      <div class="mb-8 flex flex-wrap gap-1.5 border-b border-gray-200 pb-px">
        <button v-for="t in TABS" :key="t.id" @click="tab = t.id"
          :class="['px-3.5 py-2 text-sm rounded-t-lg border-b-2 -mb-px transition whitespace-nowrap',
                   tab === t.id ? 'border-purple-600 text-purple-700 font-medium bg-white'
                                : 'border-transparent text-gray-500 hover:text-gray-700']">
          {{ t.label }}
          <span v-if="t.badge" class="ml-1 text-[11px] text-gray-400">{{ t.badge }}</span>
        </button>
      </div>

      <!-- ── 研究報告 ── -->
      <section v-show="tab === 'report'">
        <div v-if="!reportHtml" class="py-10 text-center text-sm text-gray-400">{{ loaded ? '尚未產出。' : '載入中⋯' }}</div>
        <article v-else class="md bg-white rounded-xl border border-gray-100 px-6 py-7 sm:px-8" v-html="reportHtml" />
      </section>

      <!-- ── 歷史與政教關係史年表 ── -->
      <section v-show="tab === 'timeline'">
        <div v-if="!timeline.events?.length" class="py-10 text-center text-sm text-gray-400">{{ loaded ? '尚未產出。' : '載入中⋯' }}</div>
        <template v-else>
          <p class="mb-3 text-xs text-gray-500 leading-relaxed bg-white border border-gray-100 rounded-lg px-3 py-2 break-words">
            {{ timeline.note }}
          </p>
          <p class="mb-5 text-xs text-amber-800 leading-relaxed bg-amber-50/70 border border-amber-100 rounded-lg px-3 py-2 break-words">
            {{ timeline.caution }}
          </p>

          <!-- 分期 -->
          <div class="mb-6 flex flex-wrap gap-1.5">
            <button @click="phase = ''"
              :class="['px-2.5 py-1 rounded-lg text-xs border transition',
                       phase === '' ? 'bg-purple-600 text-white border-purple-600' : 'bg-white text-gray-600 border-gray-200']">
              全部 {{ timeline.events.length }}
            </button>
            <button v-for="p in timeline.phases" :key="p.id" @click="phase = phase === p.id ? '' : p.id"
              :class="['px-2.5 py-1 rounded-lg text-xs border transition',
                       phase === p.id ? 'bg-purple-600 text-white border-purple-600' : 'bg-white text-gray-600 border-gray-200']">
              {{ p.range }}　{{ p.title }}
            </button>
          </div>

          <div v-if="activePhase" class="mb-6 bg-purple-50/60 border border-purple-100 rounded-xl px-4 py-3">
            <div class="text-sm font-semibold text-purple-900 mb-1">{{ activePhase.range }}　{{ activePhase.title }}</div>
            <p class="text-xs text-purple-900/80 leading-relaxed break-words">{{ activePhase.summary }}</p>
          </div>

          <ol class="relative border-l-2 border-gray-200 ml-2 space-y-5">
            <li v-for="(e, i) in shownEvents" :key="i" class="pl-5 relative">
              <span class="absolute -left-[7px] top-1.5 w-3 h-3 rounded-full ring-2 ring-slate-50"
                :class="phaseColor(e.phase)" />
              <div class="bg-white rounded-xl border border-gray-100 px-4 py-3">
                <div class="flex flex-wrap items-baseline gap-2 mb-1">
                  <span class="text-xs font-mono font-semibold text-purple-700">{{ e.year }}</span>
                  <span v-if="e.roc" class="text-[11px] text-gray-400">{{ e.roc }}</span>
                  <span class="ml-auto text-[11px] px-1.5 py-0.5 rounded bg-gray-100 text-gray-500">{{ e.src }}</span>
                </div>
                <h3 class="text-sm font-semibold text-gray-900 leading-snug break-words">{{ e.title }}</h3>
                <p v-if="e.detail" class="mt-1 text-xs text-gray-600 leading-relaxed break-words">{{ e.detail }}</p>
              </div>
            </li>
          </ol>
        </template>
      </section>

      <!-- ── 已取得檔案 ── -->
      <section v-show="tab === 'inventory'">
        <div v-if="!inventory.cases?.length" class="py-10 text-center text-sm text-gray-400">{{ loaded ? '尚未產出。' : '載入中⋯' }}</div>
        <template v-else>
          <div class="mb-4 grid grid-cols-3 gap-2">
            <div class="bg-white rounded-xl border border-gray-100 px-3 py-2.5 text-center">
              <div class="text-lg font-bold text-gray-900">{{ inventory.caseCount }}</div>
              <div class="text-[11px] text-gray-400">案卷</div>
            </div>
            <div class="bg-white rounded-xl border border-gray-100 px-3 py-2.5 text-center">
              <div class="text-lg font-bold text-gray-900">{{ inventory.pageCount?.toLocaleString() }}</div>
              <div class="text-[11px] text-gray-400">實得影像張數</div>
            </div>
            <div class="bg-white rounded-xl border border-gray-100 px-3 py-2.5 text-center">
              <div class="text-lg font-bold text-gray-900">{{ inventory.pendingPages?.toLocaleString() }}</div>
              <div class="text-[11px] text-gray-400">可線上閱覽待下載</div>
            </div>
          </div>
          <p class="mb-5 text-xs text-rose-700 bg-rose-50/70 border border-rose-100 rounded-lg px-3 py-2 leading-relaxed break-words">
            🚨 {{ inventory.note }}
          </p>

          <h2 class="text-base font-bold text-gray-900 mb-2">已下載</h2>
          <div class="bg-white rounded-xl border border-gray-100 divide-y divide-gray-50 mb-8">
            <div v-for="(c, i) in inventory.cases" :key="i" class="px-4 py-3">
              <div class="flex flex-wrap items-baseline gap-2">
                <span class="flex-shrink-0 text-[11px] px-1.5 py-0.5 rounded bg-purple-50 text-purple-700 font-mono">{{ c.totalPages }} 張</span>
                <span class="flex-1 text-sm text-gray-800 break-words">{{ c.title }}</span>
                <span v-if="c.files?.length" class="flex-shrink-0 text-[11px] text-gray-400">{{ c.files.length }} 件</span>
              </div>
              <div class="mt-0.5 text-[11px] text-gray-400 break-words font-mono">{{ c.archiveNo }}</div>
              <div class="text-[11px] text-gray-400 break-words">{{ c.fonds }}<template v-if="c.dateRange">　{{ c.dateRange }}</template></div>
              <p v-if="c.summary" class="mt-1 text-xs text-gray-600 leading-relaxed break-words line-clamp-3">{{ c.summary }}</p>
            </div>
          </div>

          <h2 class="text-base font-bold text-gray-900 mb-2">
            可線上閱覽、尚未下載
            <span class="ml-1 text-xs font-normal text-gray-400">{{ inventory.pending?.length }} 筆</span>
          </h2>
          <div class="bg-white rounded-xl border border-gray-100 divide-y divide-gray-50">
            <div v-for="(p, i) in inventory.pending" :key="i" class="px-4 py-2.5">
              <div class="flex flex-wrap items-baseline gap-2">
                <span class="flex-shrink-0 text-[11px] px-1.5 py-0.5 rounded bg-amber-50 text-amber-700 font-mono">{{ p.pages }} 頁</span>
                <span class="flex-1 text-sm text-gray-800 break-words">{{ p.title }}</span>
              </div>
              <div class="mt-0.5 text-[11px] text-gray-400 break-words font-mono">{{ p.archiveNo }}　{{ p.fonds }}</div>
            </div>
          </div>
        </template>
      </section>

      <!-- ── 檔案書目 ── -->
      <section v-show="tab === 'catalog'">
        <p class="mb-3 text-xs text-gray-500 bg-purple-50/60 border border-purple-100 rounded-lg px-3 py-2 leading-relaxed break-words">
          🚨 <strong>「已數位化」不等於「可以下載」</strong>。多數條目標示「須提出申請」，
          須向檔案局申請調閱；只有標「可線上閱覽」的那一批能直接看。本站只收書目與提供方式，不放影像。
        </p>

        <div v-if="!archive.items.length" class="py-10 text-center text-sm text-gray-400">
          {{ loaded ? '尚未產出。' : '載入中⋯' }}
        </div>
        <div v-else>
          <div class="mb-3 flex flex-wrap gap-2 items-center">
            <button @click="onlyOnline = !onlyOnline"
              :class="['px-3 py-1.5 rounded-lg text-xs border transition',
                       onlyOnline ? 'bg-purple-600 text-white border-purple-600' : 'bg-white text-gray-600 border-gray-200']">
              只看可線上閱覽
            </button>
            <input v-model="q" type="search" placeholder="在案由、全宗、摘要中搜尋（例：取締、邪教、考管、寧靜專案）"
              class="flex-1 min-w-[16rem] px-3 py-1.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:border-purple-400" />
            <span class="text-xs text-gray-400">{{ shown.length.toLocaleString() }} 筆</span>
          </div>

          <div class="bg-white rounded-xl border border-gray-100 divide-y divide-gray-50">
            <div v-for="(a, i) in paged" :key="i" class="px-4 py-3">
              <div class="flex flex-wrap items-baseline gap-2">
                <span class="flex-shrink-0 text-[11px] px-1.5 py-0.5 rounded"
                  :class="a.level === '案' ? 'bg-emerald-50 text-emerald-700' : 'bg-sky-50 text-sky-700'">{{ a.level || '—' }}</span>
                <span class="flex-1 text-sm text-gray-800 break-words">{{ a.title }}</span>
                <span v-if="a.online" class="flex-shrink-0 text-[11px] px-1.5 py-0.5 rounded bg-purple-50 text-purple-700">
                  可線上閱覽{{ a.pages ? ` ${a.pages} 頁` : '' }}
                </span>
                <span v-else class="flex-shrink-0 text-[11px] text-gray-400">須提出申請</span>
              </div>
              <div class="mt-0.5 text-[11px] text-gray-400 break-words">
                {{ a.fonds }}<template v-if="a.archiveNo">　檔號 {{ a.archiveNo }}</template>
              </div>
              <p v-if="a.summary" class="mt-1 text-xs text-gray-600 leading-relaxed break-words line-clamp-3">{{ a.summary }}</p>
            </div>
            <div v-if="paged.length < shown.length" class="px-4 py-3 text-center">
              <button @click="limit += 100" class="text-xs text-purple-600 hover:underline">
                顯示更多（已顯示 {{ paged.length }} / {{ shown.length }}）
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- ── 解密全文 ── -->
      <section v-show="tab === 'fulltext'">
        <template v-if="gsg.docs?.length">
          <div class="flex items-baseline gap-2 mb-3">
            <h2 class="text-base font-bold text-gray-900">{{ gsg.name }}</h2>
            <span class="text-xs text-gray-400">{{ gsg.access }}</span>
            <span class="ml-auto text-xs text-gray-500">{{ gsg.count }} 份 / {{ gsg.chars?.toLocaleString() }} 字</span>
          </div>
          <p class="mb-3 text-xs text-rose-700 bg-rose-50/70 border border-rose-100 rounded-lg px-3 py-2 leading-relaxed break-words">
            {{ gsg.notice }}
          </p>
          <div class="space-y-3">
            <div v-for="(d, i) in gsg.docs" :key="i" class="bg-white rounded-xl border border-gray-100 p-4">
              <div class="flex flex-wrap items-baseline gap-2 mb-1">
                <h3 class="text-sm font-semibold text-gray-900">{{ d.title }}</h3>
                <span class="text-[11px] px-1.5 py-0.5 rounded bg-gray-100 text-gray-500">{{ d.fonds }}</span>
                <span class="text-[11px] text-gray-400 font-mono">{{ d.dateRange }}</span>
                <span class="ml-auto text-xs text-gray-500">{{ d.chars.toLocaleString() }} 字</span>
              </div>
              <p class="text-[11px] text-gray-400 break-words">檔號 {{ d.archiveNo }}</p>
              <p class="text-[11px] text-gray-400 break-words">{{ d.declassified }}</p>
              <p class="mt-1 text-xs text-gray-600 leading-relaxed break-words">{{ d.note }}</p>
              <button @click="toggleDoc(i, d.archiveNo)" class="mt-2 text-xs text-purple-600 hover:underline">
                {{ openDoc === i ? '收合全文' : '展開全文' }}
              </button>
              <div v-if="openDoc === i" class="mt-2">
                <div v-if="docLoading" class="px-3 py-2 text-[11px] text-gray-400">載入全文⋯</div>
                <pre v-else-if="docText"
                  class="px-3 py-2 rounded-lg bg-gray-50/70 border border-gray-100 text-[11px] leading-relaxed text-gray-700 whitespace-pre-wrap font-sans max-h-[32rem] overflow-auto">{{ docText }}</pre>
                <div v-else class="px-3 py-2 text-[11px] text-gray-400">取不到全文（需登入）。</div>
              </div>
            </div>
          </div>
        </template>
        <div v-else class="py-10 text-center text-sm text-gray-400">{{ loaded ? '尚未產出。' : '載入中⋯' }}</div>
      </section>

      <!-- ── 研究文獻 ── -->
      <section v-show="tab === 'biblio'">
        <p v-if="biblio.source" class="mb-3 text-xs text-gray-500 leading-relaxed break-words">
          {{ biblio.source }}
          <span class="text-amber-700">標「待核」者為書頁照片判讀不確定的欄位，須核對原件。</span>
        </p>
        <div v-if="biblio.items?.length" class="bg-white rounded-xl border border-gray-100 divide-y divide-gray-50">
          <div v-for="(b, i) in biblio.items" :key="i" class="px-4 py-2.5">
            <div class="flex flex-wrap items-baseline gap-2 text-sm">
              <span class="flex-shrink-0 text-[11px] px-1.5 py-0.5 rounded bg-gray-100 text-gray-500">{{ b.kind }}</span>
              <span class="flex-shrink-0 text-xs text-gray-400 font-mono">{{ b.year }}</span>
              <span class="flex-1 text-gray-800 break-words">{{ b.title }}</span>
              <span v-if="b.verify" class="flex-shrink-0 text-[11px] px-1.5 py-0.5 rounded bg-amber-50 text-amber-700">待核</span>
            </div>
            <p v-if="b.titleEn" class="mt-0.5 text-[11px] text-gray-400 italic break-words">{{ b.titleEn }}</p>
            <div class="mt-0.5 text-[11px] text-gray-400 break-words">
              {{ b.author }}<template v-if="b.advisor">（指導教授：{{ b.advisor }}）</template><template
                v-if="b.container">　收於《{{ b.container }}》</template><template
                v-if="b.journal">　《{{ b.journal }}》{{ b.vol }}</template><template
                v-if="b.pub">　{{ b.pub }}</template><template v-if="b.pages">　{{ b.pages }}</template>
            </div>
            <p v-if="b.note" class="mt-0.5 text-[11px] text-amber-700 break-words">{{ b.note }}</p>
          </div>
        </div>
        <div v-else class="py-10 text-center text-sm text-gray-400">{{ loaded ? '尚未產出。' : '載入中⋯' }}</div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { authedFetch } from '~/composables/useAuthedFetch';
import { ref, computed, onMounted, watch } from 'vue';

definePageMeta({ middleware: 'auth' });
useHead({ title: '一貫道研究資料 — 論文資料整理' });

interface ArchiveRow {
  level: string; title: string; fonds: string; archiveNo: string;
  access: string; online: boolean; pages: number; summary: string; subjects: string[];
}
interface BiblioRow {
  author: string; year: string; title: string; kind: string;
  container?: string; journal?: string; vol?: string; pub?: string;
  pages?: string; editor?: string; verify?: boolean; note?: string;
  titleEn?: string; authorEn?: string; advisor?: string; degree?: string;
}
interface GsgDoc {
  title: string; fonds: string; archiveNo: string; dateRange: string;
  declassified: string; note: string; lines: number; chars: number;
}
interface TimelineEvent { year: string; roc?: string; phase: string; title: string; detail?: string; src: string }
interface TimelinePhase { id: string; range: string; title: string; summary: string }
interface InventoryCase {
  archiveNo: string; title: string; fonds: string; dateRange: string;
  summary: string; pages: number; filePages: number; totalPages: number; files: InventoryCase[];
}

const TABS = [
  { id: 'report', label: '研究報告', badge: '' },
  { id: 'timeline', label: '歷史與政教關係史', badge: '' },
  { id: 'inventory', label: '已取得檔案', badge: '' },
  { id: 'catalog', label: '檔案書目', badge: '417' },
  { id: 'fulltext', label: '解密全文', badge: '12 萬字' },
  { id: 'biblio', label: '研究文獻', badge: '35' },
];
const tab = ref('report');

const archive = ref<{ total: number; count: number; online: number; items: ArchiveRow[] }>(
  { total: 0, count: 0, online: 0, items: [] });
const biblio = ref<{ source?: string; count?: number; items?: BiblioRow[] }>({});
const gsg = ref<{ name?: string; access?: string; notice?: string; count?: number; chars?: number; docs?: GsgDoc[] }>({});
const timeline = ref<{ note?: string; caution?: string; phases?: TimelinePhase[]; events?: TimelineEvent[] }>({});
const inventory = ref<{
  note?: string; caseCount?: number; pageCount?: number; pendingPages?: number;
  cases?: InventoryCase[]; pending?: { archiveNo: string; title: string; fonds: string; pages: number }[];
}>({});
const reportHtml = ref('');
const loaded = ref(false);

// ── 年表 ──
const phase = ref('');
const activePhase = computed(() => timeline.value.phases?.find(p => p.id === phase.value) || null);
const shownEvents = computed(() =>
  (timeline.value.events || []).filter(e => !phase.value || e.phase === phase.value));
const PHASE_COLOR: Record<string, string> = {
  p1: 'bg-slate-400', p2: 'bg-rose-500', p3: 'bg-orange-500', p4: 'bg-amber-500',
  p5: 'bg-lime-600', p6: 'bg-sky-500', p7: 'bg-emerald-600',
};
const phaseColor = (id: string) => PHASE_COLOR[id] || 'bg-gray-300';

// ── 全文（不在 repo 裡，存 R2 由需驗證的端點供應）──
const openDoc = ref(-1);
const docText = ref('');
const docLoading = ref(false);
async function toggleDoc(i: number, archiveNo: string) {
  if (openDoc.value === i) { openDoc.value = -1; return; }
  openDoc.value = i; docText.value = ''; docLoading.value = true;
  try {
    const r = await authedFetch<{ available: boolean; doc?: { text: string } }>(
      '/api/research-data/guoshiguan-text', { query: { archiveNo } });
    docText.value = r.available ? (r.doc?.text ?? '') : '';
  } catch { docText.value = ''; } finally { docLoading.value = false; }
}

// ── 書目篩選 ──
const onlyOnline = ref(false);
const q = ref('');
const limit = ref(100);
const shown = computed(() => {
  let rows = archive.value.items;
  if (onlyOnline.value) rows = rows.filter(a => a.online);
  const term = q.value.trim();
  if (!term) return rows;
  return rows.filter(a =>
    a.title.includes(term) || a.fonds.includes(term) || (a.summary || '').includes(term));
});
const paged = computed(() => shown.value.slice(0, limit.value));
watch([onlyOnline, q], () => { limit.value = 100; });

// ── 迷你 markdown 渲染（標題／粗體／表格／清單／引用／分隔線；無外部依賴）──
function esc(s: string) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
function inlineMd(s: string) {
  return esc(s)
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code>$1</code>');
}
function renderMarkdown(md: string): string {
  // 封面那幾行只給 Word 版用，網頁上略過
  const marker = md.indexOf('<!-- 封面結束 -->');
  const body = marker >= 0 ? md.slice(marker + '<!-- 封面結束 -->'.length) : md;
  const lines = body.replace(/\r\n/g, '\n').split('\n');
  const out: string[] = [];
  let i = 0;
  let list: 'ul' | 'ol' | null = null;
  const closeList = () => { if (list) { out.push(`</${list}>`); list = null; } };
  while (i < lines.length) {
    const t = lines[i].trim();
    if (!t) { closeList(); i++; continue; }
    if (/^---+$/.test(t)) { closeList(); out.push('<hr>'); i++; continue; }
    if (t.startsWith('|') && i + 1 < lines.length && /^\|[\s:|-]+\|?\s*$/.test(lines[i + 1].trim())) {
      closeList();
      const cells = (s: string) => s.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map(c => c.trim());
      const head = cells(t); i += 2;
      const rows: string[][] = [];
      while (i < lines.length && lines[i].trim().startsWith('|')) { rows.push(cells(lines[i])); i++; }
      let tbl = '<div class="md-tw"><table><thead><tr>' + head.map(h => `<th>${inlineMd(h)}</th>`).join('') + '</tr></thead><tbody>';
      for (const r of rows) tbl += '<tr>' + r.map(c => `<td>${inlineMd(c)}</td>`).join('') + '</tr>';
      out.push(tbl + '</tbody></table></div>'); continue;
    }
    const h = t.match(/^(#{1,6})\s+(.*)$/);
    if (h) { closeList(); out.push(`<h${Math.min(h[1].length + 1, 6)}>${inlineMd(h[2])}</h${Math.min(h[1].length + 1, 6)}>`); i++; continue; }
    if (t.startsWith('>')) {
      closeList(); const buf: string[] = [];
      while (i < lines.length && lines[i].trim().startsWith('>')) { buf.push(lines[i].trim().replace(/^>\s?/, '')); i++; }
      out.push(`<blockquote>${inlineMd(buf.join(' '))}</blockquote>`); continue;
    }
    const ul = t.match(/^[-*]\s+(.*)$/);
    if (ul) { if (list !== 'ul') { closeList(); out.push('<ul>'); list = 'ul'; } out.push(`<li>${inlineMd(ul[1])}</li>`); i++; continue; }
    const ol = t.match(/^\d+[.)]\s+(.*)$/);
    if (ol) { if (list !== 'ol') { closeList(); out.push('<ol>'); list = 'ol'; } out.push(`<li>${inlineMd(ol[1])}</li>`); i++; continue; }
    closeList(); out.push(`<p>${inlineMd(t)}</p>`); i++;
  }
  closeList();
  return out.join('\n');
}

// 🚨 這批資料不在 public/ 裡，也不在 git 裡——它帶著檔案局目錄的人名與列管年數，
//    而 repo 是公開的。檔案放 R2 `research-private/yiguandao/`，由需登入的
//    `yiguandao-file` 端點供應（上傳走 scripts/yiguandao_r2_sync.py）。
async function loadFile<T>(name: string): Promise<T | null> {
  try {
    const r = await authedFetch<{ available: boolean; data?: T }>(
      '/api/research-data/yiguandao-file', { query: { name } });
    return r.available ? (r.data ?? null) : null;
  } catch { return null; }   // 一份讀不到不該讓其他五個分頁一起空掉
}

onMounted(async () => {
  const [a, b, g, t, v, r] = await Promise.all([
    loadFile<typeof archive.value>('archives-index.json'),
    loadFile<typeof biblio.value>('biblio-zhong.json'),
    loadFile<typeof gsg.value>('guoshiguan.json'),
    loadFile<typeof timeline.value>('timeline.json'),
    loadFile<typeof inventory.value>('inventory.json'),
    loadFile<string>('report.md'),
  ]);
  if (a) archive.value = a;
  if (b) biblio.value = b;
  if (g) gsg.value = g;
  if (t) timeline.value = t;
  if (v) inventory.value = v;
  if (r) reportHtml.value = renderMarkdown(r);
  loaded.value = true;
});
</script>

<style scoped>
.md { color: #374151; font-size: 0.9rem; line-height: 1.85; }
.md :deep(h2) { font-size: 1.15rem; font-weight: 700; color: #111827; margin: 2.2rem 0 0.8rem; padding-bottom: 0.4rem; border-bottom: 1px solid #f3f4f6; }
.md :deep(h2:first-child) { margin-top: 0; }
.md :deep(h3) { font-size: 1rem; font-weight: 700; color: #1f2937; margin: 1.6rem 0 0.6rem; }
.md :deep(h4) { font-size: 0.92rem; font-weight: 700; color: #374151; margin: 1.2rem 0 0.4rem; }
.md :deep(p) { margin: 0.7rem 0; overflow-wrap: anywhere; }
.md :deep(strong) { color: #111827; font-weight: 700; }
.md :deep(ul), .md :deep(ol) { margin: 0.7rem 0; padding-left: 1.4rem; }
.md :deep(li) { margin: 0.3rem 0; overflow-wrap: anywhere; }
.md :deep(ul) { list-style: disc; }
.md :deep(ol) { list-style: decimal; }
.md :deep(hr) { margin: 2rem 0; border: 0; border-top: 1px solid #f3f4f6; }
.md :deep(blockquote) { margin: 0.9rem 0; padding: 0.5rem 0.9rem; border-left: 3px solid #e9d5ff; background: #faf5ff; color: #4b5563; font-size: 0.86rem; }
/* 寬表格自己捲，頁面不橫向捲 */
.md :deep(.md-tw) { overflow-x: auto; margin: 1rem 0; }
.md :deep(table) { border-collapse: collapse; font-size: 0.78rem; min-width: 100%; }
.md :deep(th), .md :deep(td) { border: 1px solid #e5e7eb; padding: 0.35rem 0.55rem; text-align: left; vertical-align: top; }
.md :deep(th) { background: #f9fafb; font-weight: 600; color: #374151; white-space: nowrap; }
.md :deep(code) { background: #f3f4f6; padding: 0.05rem 0.3rem; border-radius: 0.2rem; font-size: 0.85em; }
</style>
