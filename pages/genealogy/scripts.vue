<template>
  <div class="flex flex-col bg-slate-50" style="height: 100dvh;">
    <AppHeader title="文字創造族譜" :back="{ to: '/genealogy', label: '圖譜工具' }" container-class="max-w-full">
      <template #actions>
        <span class="text-xs text-gray-400 hidden sm:inline">{{ SCRIPT_NODES.length }} 種書寫系統</span>
        <input
          v-model="q"
          placeholder="搜尋文字…"
          class="text-xs px-2.5 py-1 rounded-lg border border-gray-200 focus:border-indigo-300 outline-none w-28 sm:w-40"
        />
      </template>
    </AppHeader>

    <div class="flex-1 min-h-0 relative">
      <!-- 圖 -->
      <svg ref="svgEl" class="w-full h-full select-none" :viewBox="`0 0 ${size.w} ${size.h}`">
        <g ref="vpEl">
          <!-- 邊 -->
          <path
            v-for="(e, i) in layout.edges"
            :key="'e' + i"
            :d="e.d"
            fill="none"
            :stroke="e.color"
            :stroke-width="e.active ? 2.2 : 1.2"
            :stroke-dasharray="e.dashed ? '4 4' : undefined"
            :opacity="e.dim ? 0.12 : (e.active ? 0.9 : 0.4)"
          />
          <!-- 節點 -->
          <g
            v-for="n in layout.nodes"
            :key="n.id"
            :transform="`translate(${n.x},${n.y})`"
            class="cursor-pointer"
            :opacity="n.dim ? 0.18 : 1"
            @click="selectNode(n.id)"
          >
            <rect
              :width="NODE_W" :height="NODE_H" rx="9"
              :fill="n.id === selectedId ? n.color : '#fff'"
              :stroke="n.color" :stroke-width="n.id === selectedId ? 2.5 : 1.5"
            />
            <text :x="11" :y="20" font-size="15" :fill="n.id === selectedId ? '#fff' : '#111827'">{{ n.sample }}</text>
            <text :x="32" :y="20" font-size="12.5" font-weight="600" :fill="n.id === selectedId ? '#fff' : '#1f2937'">{{ clip(n.name, 9) }}</text>
            <text :x="11" :y="37" font-size="10" :fill="n.id === selectedId ? '#f1f5f9' : '#94a3b8'">{{ eraLabel(n.era) }} · {{ SCRIPT_TYPE_LABEL[n.type] }}</text>
          </g>
        </g>
      </svg>

      <!-- 圖例 / 篩選 -->
      <div class="absolute top-3 left-3 bg-white/90 backdrop-blur rounded-xl border border-gray-200 shadow-sm p-2.5 max-w-[180px]">
        <div class="text-[11px] font-semibold text-gray-500 mb-1.5">文字大族（點選篩選）</div>
        <button
          v-for="f in SCRIPT_FAMILIES"
          :key="f.key"
          @click="toggleFamily(f.key)"
          class="flex items-center gap-1.5 w-full text-left text-[11px] py-0.5 transition"
          :class="activeFamilies.size && !activeFamilies.has(f.key) ? 'opacity-35' : ''"
        >
          <span class="w-2.5 h-2.5 rounded-sm flex-shrink-0" :style="{ background: f.color }"></span>
          <span class="text-gray-700 truncate">{{ f.label }}</span>
        </button>
        <div class="text-[10px] text-gray-400 mt-1.5 leading-snug">實線＝演化／創製；虛線＝影響或有爭議</div>
      </div>

      <!-- 縮放控制 -->
      <div class="absolute bottom-3 left-3 flex flex-col gap-1">
        <button @click="zoomBy(1.3)" class="w-8 h-8 rounded-lg bg-white border border-gray-200 shadow-sm text-gray-600 hover:bg-gray-50">＋</button>
        <button @click="zoomBy(1/1.3)" class="w-8 h-8 rounded-lg bg-white border border-gray-200 shadow-sm text-gray-600 hover:bg-gray-50">－</button>
        <button @click="fit()" class="w-8 h-8 rounded-lg bg-white border border-gray-200 shadow-sm text-gray-600 hover:bg-gray-50 text-xs">⤢</button>
      </div>

      <!-- 詳情面板 -->
      <div
        v-if="selected"
        class="absolute top-3 right-3 bottom-3 w-72 bg-white rounded-xl border border-gray-200 shadow-lg p-4 overflow-y-auto"
      >
        <div class="flex items-start justify-between gap-2">
          <div>
            <div class="flex items-center gap-2">
              <span class="text-2xl">{{ selected.sample }}</span>
              <h2 class="text-base font-bold text-gray-900">{{ selected.name }}</h2>
            </div>
            <div class="text-xs mt-0.5" :style="{ color: familyColor(selected.family) }">{{ familyLabel(selected.family) }}</div>
          </div>
          <button @click="selectedId = null" class="text-gray-300 hover:text-gray-500 text-lg leading-none">✕</button>
        </div>

        <dl class="mt-3 space-y-1.5 text-xs">
          <div class="flex gap-2"><dt class="text-gray-400 w-12 flex-shrink-0">類型</dt><dd class="text-gray-700">{{ SCRIPT_TYPE_LABEL[selected.type] }}</dd></div>
          <div class="flex gap-2"><dt class="text-gray-400 w-12 flex-shrink-0">年代</dt><dd class="text-gray-700">{{ eraLabel(selected.era) }}</dd></div>
          <div class="flex gap-2"><dt class="text-gray-400 w-12 flex-shrink-0">地區</dt><dd class="text-gray-700">{{ selected.region }}</dd></div>
          <div class="flex gap-2"><dt class="text-gray-400 w-12 flex-shrink-0">狀態</dt><dd class="text-gray-700">{{ statusLabel(selected.status) }}</dd></div>
        </dl>
        <p class="mt-2.5 text-xs text-gray-600 leading-relaxed">{{ selected.note }}</p>

        <NuxtLink
          v-if="selected.coach"
          :to="`/coach/${selected.coach}`"
          class="mt-3 inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-lg bg-indigo-50 text-indigo-700 hover:bg-indigo-100 transition"
        >📚 用此文字的語言教練 →</NuxtLink>

        <div v-if="parentsOf(selected).length" class="mt-4">
          <div class="text-[11px] font-semibold text-gray-400 mb-1">源自</div>
          <button v-for="p in parentsOf(selected)" :key="p.node.id" @click="selectNode(p.node.id)"
            class="block text-left text-xs text-gray-700 hover:text-indigo-600 py-0.5">
            <span>{{ p.node.sample }} {{ p.node.name }}</span>
            <span class="text-[10px] text-gray-400 ml-1">（{{ EDGE_KIND_LABEL[p.kind] }}）</span>
          </button>
        </div>
        <div v-if="childrenOf(selected).length" class="mt-3">
          <div class="text-[11px] font-semibold text-gray-400 mb-1">衍生出</div>
          <button v-for="c in childrenOf(selected)" :key="c.node.id" @click="selectNode(c.node.id)"
            class="block text-left text-xs text-gray-700 hover:text-indigo-600 py-0.5">
            <span>{{ c.node.sample }} {{ c.node.name }}</span>
            <span class="text-[10px] text-gray-400 ml-1">（{{ EDGE_KIND_LABEL[c.kind] }}）</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { select } from "d3-selection";
import { zoom, zoomIdentity, type ZoomBehavior } from "d3-zoom";
import {
  SCRIPT_NODES, SCRIPT_FAMILIES, SCRIPT_TYPE_LABEL, EDGE_KIND_LABEL, getScriptNode,
  type ScriptNode,
} from "~/data/scriptGenealogy";

definePageMeta({ middleware: "auth" });
useHead({ title: "文字創造族譜 — Know Graph Lab" });

const NODE_W = 150, NODE_H = 46, COL_W = 224, ROW_H = 60;

const q = ref("");
const selectedId = ref<string | null>(null);
const activeFamilies = ref<Set<string>>(new Set());

const idMap = new Map(SCRIPT_NODES.map((n) => [n.id, n]));
const familyColor = (key: string) => SCRIPT_FAMILIES.find((f) => f.key === key)?.color ?? "#475569";
const familyLabel = (key: string) => SCRIPT_FAMILIES.find((f) => f.key === key)?.label ?? key;
const clip = (s: string, n: number) => (s.length > n ? s.slice(0, n) + "…" : s);
const eraLabel = (y: number) => (y < 0 ? `前 ${-y}` : `${y}`);
const statusLabel = (s: string) => ({ living: "現用", extinct: "已死", undeciphered: "未解讀" } as Record<string, string>)[s] ?? s;
const selected = computed(() => (selectedId.value ? idMap.get(selectedId.value) ?? null : null));

function parentsOf(n: ScriptNode) {
  return n.parents.map((p) => ({ node: idMap.get(p.id)!, kind: p.kind })).filter((x) => x.node);
}
function childrenOf(n: ScriptNode) {
  const out: { node: ScriptNode; kind: any }[] = [];
  for (const m of SCRIPT_NODES) for (const p of m.parents) if (p.id === n.id) out.push({ node: m, kind: p.kind });
  return out;
}

// ── 版面：longest-path 分層（col）＋ barycenter 排列（row）──
const positions = computed(() => {
  // Kahn 拓撲排序 → col = max(parent.col)+1
  const indeg = new Map<string, number>();
  const childAdj = new Map<string, string[]>();
  for (const n of SCRIPT_NODES) { indeg.set(n.id, 0); childAdj.set(n.id, []); }
  for (const n of SCRIPT_NODES) for (const p of n.parents) {
    if (!idMap.has(p.id)) continue;
    indeg.set(n.id, (indeg.get(n.id) ?? 0) + 1);
    childAdj.get(p.id)!.push(n.id);
  }
  const col = new Map<string, number>();
  const queue = SCRIPT_NODES.filter((n) => (indeg.get(n.id) ?? 0) === 0).map((n) => n.id);
  queue.forEach((id) => col.set(id, 0));
  const ind = new Map(indeg);
  while (queue.length) {
    const id = queue.shift()!;
    for (const c of childAdj.get(id)!) {
      col.set(c, Math.max(col.get(c) ?? 0, (col.get(id) ?? 0) + 1));
      ind.set(c, (ind.get(c) ?? 0) - 1);
      if ((ind.get(c) ?? 0) === 0) queue.push(c);
    }
  }
  // 分欄
  const cols: string[][] = [];
  for (const n of SCRIPT_NODES) {
    const c = col.get(n.id) ?? 0;
    (cols[c] ||= []).push(n.id);
  }
  // 初始排序：同欄按 family 順序＋年代
  const famOrder = new Map(SCRIPT_FAMILIES.map((f, i) => [f.key, i]));
  for (const c of cols) c?.sort((a, b) => {
    const na = idMap.get(a)!, nb = idMap.get(b)!;
    return (famOrder.get(na.family)! - famOrder.get(nb.family)!) || (na.era - nb.era);
  });
  // barycenter 迭代：用前一欄父節點的平均 row 排序，減少交叉
  const row = new Map<string, number>();
  const setRows = () => { for (const c of cols) c?.forEach((id, i) => row.set(id, i)); };
  setRows();
  for (let iter = 0; iter < 3; iter++) {
    for (let ci = 1; ci < cols.length; ci++) {
      const c = cols[ci]; if (!c) continue;
      const bary = (id: string) => {
        const ps = idMap.get(id)!.parents.filter((p) => idMap.has(p.id));
        if (!ps.length) return row.get(id) ?? 0;
        return ps.reduce((s, p) => s + (row.get(p.id) ?? 0), 0) / ps.length;
      };
      c.sort((a, b) => bary(a) - bary(b) || (row.get(a)! - row.get(b)!));
      c.forEach((id, i) => row.set(id, i));
    }
  }
  const pos = new Map<string, { x: number; y: number }>();
  for (let ci = 0; ci < cols.length; ci++) {
    const c = cols[ci]; if (!c) continue;
    c.forEach((id, ri) => pos.set(id, { x: ci * COL_W + 20, y: ri * ROW_H + 16 }));
  }
  const maxRows = Math.max(...cols.map((c) => (c ? c.length : 0)));
  return { pos, w: cols.length * COL_W + 40, h: maxRows * ROW_H + 40 };
});
const size = computed(() => ({ w: positions.value.w, h: positions.value.h }));

// 高亮譜系（選中節點的祖先＋後裔）
const lineage = computed(() => {
  if (!selectedId.value) return null;
  const anc = new Set<string>(), desc = new Set<string>();
  const up = (id: string) => { for (const p of idMap.get(id)?.parents ?? []) if (idMap.has(p.id) && !anc.has(p.id)) { anc.add(p.id); up(p.id); } };
  const down = (id: string) => { for (const c of childrenOf(idMap.get(id)!)) if (!desc.has(c.node.id)) { desc.add(c.node.id); down(c.node.id); } };
  up(selectedId.value); down(selectedId.value);
  const all = new Set<string>([selectedId.value, ...anc, ...desc]);
  return all;
});

function nodeDim(id: string) {
  if (activeFamilies.value.size && !activeFamilies.value.has(idMap.get(id)!.family)) return true;
  if (q.value.trim() && !idMap.get(id)!.name.includes(q.value.trim())) return true;
  if (lineage.value && !lineage.value.has(id)) return true;
  return false;
}

const layout = computed(() => {
  const nodes = SCRIPT_NODES.map((n) => ({
    ...n, ...positions.value.pos.get(n.id)!, color: familyColor(n.family), dim: nodeDim(n.id),
  }));
  const edges: { d: string; color: string; dashed: boolean; dim: boolean; active: boolean }[] = [];
  for (const n of SCRIPT_NODES) {
    const cp = positions.value.pos.get(n.id)!;
    for (const p of n.parents) {
      const pp = positions.value.pos.get(p.id); if (!pp) continue;
      const x1 = pp.x + NODE_W, y1 = pp.y + NODE_H / 2, x2 = cp.x, y2 = cp.y + NODE_H / 2;
      const dx = Math.max(40, (x2 - x1) / 2);
      const active = !!lineage.value && lineage.value.has(n.id) && lineage.value.has(p.id);
      edges.push({
        d: `M${x1},${y1} C${x1 + dx},${y1} ${x2 - dx},${y2} ${x2},${y2}`,
        color: familyColor(idMap.get(p.id)!.family),
        dashed: p.kind === "influenced",
        dim: nodeDim(n.id) || nodeDim(p.id),
        active,
      });
    }
  }
  return { nodes, edges };
});

function selectNode(id: string) { selectedId.value = selectedId.value === id ? null : id; }
function toggleFamily(key: string) {
  const s = new Set(activeFamilies.value);
  s.has(key) ? s.delete(key) : s.add(key);
  activeFamilies.value = s;
}

// ── d3-zoom 平移縮放 ──
const svgEl = ref<SVGSVGElement | null>(null);
const vpEl = ref<SVGGElement | null>(null);
let zb: ZoomBehavior<SVGSVGElement, unknown> | null = null;
function zoomBy(k: number) { if (zb && svgEl.value) select(svgEl.value).transition().duration(200).call(zb.scaleBy, k); }
function fit() {
  if (!zb || !svgEl.value) return;
  const r = svgEl.value.getBoundingClientRect();
  const s = Math.min(r.width / size.value.w, r.height / size.value.h) * 0.95;
  const t = zoomIdentity.translate((r.width - size.value.w * s) / 2, 16).scale(s);
  select(svgEl.value).transition().duration(300).call(zb.transform, t);
}
onMounted(() => {
  if (!svgEl.value || !vpEl.value) return;
  zb = zoom<SVGSVGElement, unknown>().scaleExtent([0.15, 3]).on("zoom", (ev) => {
    select(vpEl.value!).attr("transform", ev.transform.toString());
  });
  select(svgEl.value).call(zb);
  fit();
});

// 深連 ?id=hangul
const route = useRoute();
onMounted(() => { if (typeof route.query.id === "string" && idMap.has(route.query.id)) selectedId.value = route.query.id; });
</script>
