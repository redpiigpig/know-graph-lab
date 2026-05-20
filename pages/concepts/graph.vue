<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-14">
          <div class="flex items-center gap-2 text-sm text-gray-500">
            <NuxtLink to="/" class="hover:text-blue-600 flex items-center gap-1.5">
              <img src="/logo_image.jpg" alt="logo" class="w-5 h-5 rounded object-cover" />
              <span>知識圖工作室</span>
            </NuxtLink>
            <span>›</span>
            <NuxtLink to="/concepts" class="hover:text-cyan-600">概念筆記</NuxtLink>
            <span>›</span>
            <span class="font-medium text-gray-900">概念圖</span>
          </div>
          <span class="text-xs text-gray-400">{{ data.nodes.length }} 概念 · {{ data.edges.length }} 連結</span>
        </div>
      </div>
    </nav>

    <div class="max-w-7xl mx-auto px-4 py-6">
      <div v-if="loading" class="text-center text-gray-400 py-20">載入中…</div>
      <div v-else-if="!data.nodes.length" class="text-center text-gray-400 py-20">
        尚無概念，<NuxtLink to="/concepts" class="text-cyan-600 underline">回到列表</NuxtLink>建立第一個
      </div>
      <div v-else class="bg-white border border-gray-200 rounded-2xl overflow-hidden">
        <svg ref="svgRef" class="w-full" :viewBox="`0 0 ${W} ${H}`" :style="{ height: `${H}px` }">
          <g>
            <line v-for="(e, i) in renderedEdges" :key="'e'+i"
              :x1="e.x1" :y1="e.y1" :x2="e.x2" :y2="e.y2"
              stroke="#cbd5e1" stroke-width="1" />
          </g>
          <g>
            <g v-for="n in renderedNodes" :key="n.id" :transform="`translate(${n.x},${n.y})`"
               class="cursor-pointer" @click="go(n.slug)">
              <circle :r="n.r" :fill="n.color || '#06b6d4'" fill-opacity="0.85" stroke="#fff" stroke-width="1.5" />
              <text :y="n.r + 12" text-anchor="middle" class="text-[11px] fill-gray-700 select-none pointer-events-none">{{ n.name }}</text>
            </g>
          </g>
        </svg>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { authedFetch } from '~/composables/useAuthedFetch';

definePageMeta({ middleware: 'auth' });

interface Node { id: string; name: string; slug: string; color?: string | null; degree: number; }
interface Edge { source: string; target: string; }

const W = 1100;
const H = 720;
const router = useRouter();

const data = ref<{ nodes: Node[]; edges: Edge[] }>({ nodes: [], edges: [] });
const loading = ref(true);

// Force-directed layout state.
type P = { id: string; x: number; y: number; vx: number; vy: number; n: Node };
const positions = ref<P[]>([]);
const tick = ref(0);                    // bump to trigger recompute
let raf = 0;

const renderedNodes = computed(() => {
  void tick.value;
  return positions.value.map((p) => ({
    ...p.n,
    x: p.x, y: p.y,
    r: 6 + Math.sqrt(p.n.degree) * 3,
    color: p.n.color,
  }));
});

const renderedEdges = computed(() => {
  void tick.value;
  const byId = new Map(positions.value.map((p) => [p.id, p]));
  return data.value.edges
    .map((e) => {
      const s = byId.get(e.source); const t = byId.get(e.target);
      if (!s || !t) return null;
      return { x1: s.x, y1: s.y, x2: t.x, y2: t.y };
    })
    .filter(Boolean) as { x1: number; y1: number; x2: number; y2: number }[];
});

function initLayout() {
  const cx = W / 2, cy = H / 2;
  positions.value = data.value.nodes.map((n, i) => {
    const angle = (i / Math.max(1, data.value.nodes.length)) * Math.PI * 2;
    const r = Math.min(W, H) * 0.35;
    return {
      id: n.id,
      x: cx + Math.cos(angle) * r * (0.4 + Math.random() * 0.6),
      y: cy + Math.sin(angle) * r * (0.4 + Math.random() * 0.6),
      vx: 0, vy: 0,
      n,
    };
  });
}

function step() {
  const cx = W / 2, cy = H / 2;
  const REPEL = 1800;     // node-node repulsion
  const SPRING = 0.02;    // edge spring constant
  const REST = 110;       // edge ideal length
  const CENTER = 0.005;   // pull toward center
  const DAMP = 0.85;

  const ps = positions.value;
  const byId = new Map(ps.map((p) => [p.id, p]));

  // Reset forces
  const fx = new Array(ps.length).fill(0);
  const fy = new Array(ps.length).fill(0);

  // Repulsion between every pair (O(n²) is fine for <300 nodes)
  for (let i = 0; i < ps.length; i++) {
    for (let j = i + 1; j < ps.length; j++) {
      let dx = ps[i].x - ps[j].x;
      let dy = ps[i].y - ps[j].y;
      let d2 = dx * dx + dy * dy + 0.01;
      const f = REPEL / d2;
      const d = Math.sqrt(d2);
      const fxi = (dx / d) * f, fyi = (dy / d) * f;
      fx[i] += fxi; fy[i] += fyi;
      fx[j] -= fxi; fy[j] -= fyi;
    }
  }

  // Edge spring
  for (const e of data.value.edges) {
    const s = byId.get(e.source); const t = byId.get(e.target);
    if (!s || !t) continue;
    const si = ps.indexOf(s), ti = ps.indexOf(t);
    const dx = t.x - s.x, dy = t.y - s.y;
    const d = Math.sqrt(dx * dx + dy * dy) || 0.01;
    const force = (d - REST) * SPRING;
    fx[si] += (dx / d) * force;
    fy[si] += (dy / d) * force;
    fx[ti] -= (dx / d) * force;
    fy[ti] -= (dy / d) * force;
  }

  // Centering + integrate
  let totalKE = 0;
  for (let i = 0; i < ps.length; i++) {
    fx[i] += (cx - ps[i].x) * CENTER;
    fy[i] += (cy - ps[i].y) * CENTER;
    ps[i].vx = (ps[i].vx + fx[i]) * DAMP;
    ps[i].vy = (ps[i].vy + fy[i]) * DAMP;
    ps[i].x += ps[i].vx;
    ps[i].y += ps[i].vy;
    // clamp
    ps[i].x = Math.max(20, Math.min(W - 20, ps[i].x));
    ps[i].y = Math.max(20, Math.min(H - 20, ps[i].y));
    totalKE += ps[i].vx * ps[i].vx + ps[i].vy * ps[i].vy;
  }

  tick.value++;
  if (totalKE > 0.05) {
    raf = requestAnimationFrame(step);
  }
}

async function load() {
  loading.value = true;
  try {
    data.value = await authedFetch('/api/concepts/graph');
    initLayout();
    cancelAnimationFrame(raf);
    raf = requestAnimationFrame(step);
  } finally { loading.value = false; }
}

function go(slug: string) { router.push(`/concepts/${slug}`); }

onMounted(load);
onBeforeUnmount(() => cancelAnimationFrame(raf));
</script>
