<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader title="希臘羅馬大藏經" :back="{ to: '/scripture-canon/greco-roman', label: '希臘羅馬宗教' }" container-class="max-w-5xl">
      <template #actions>
        <span class="text-xs text-gray-400">{{ totalVolumes }} 卷 · {{ totalWorks }} 種</span>
      </template>
    </AppHeader>

    <div class="flex-1 max-w-5xl w-full mx-auto px-6 py-10">
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">🏛️ 希臘羅馬大藏經</h1>
        <p class="text-sm text-gray-500 leading-relaxed">
          為希臘傳統宗教建立一部它從未擁有過的正典。以希臘字母 Α–Ω 立廿四卷，仿聖經的文類光譜編次——神譜、列祖、律法、詩頌、智慧、神諭、啟示、論議、爭辯；
          羅馬宗教自成一系，另立六卷為續典，以羅馬數字 I–VI 編號。
        </p>
        <p class="text-xs text-gray-400 leading-relaxed mt-2">
          <b>斷限</b>：{{ TERMINUS.from }} 起，止於 <b>{{ TERMINUS.to }}</b>。{{ TERMINUS.note }}
        </p>
        <p class="text-xs text-gray-400 leading-relaxed mt-1">
          <b>編次原則</b>：希臘卷前十四卷按文本在希臘宗教中的權威位階與成書早晚排，不按所敘事件先後——荷馬與赫西奧德是希臘人真正當經在讀的東西，故居首；後十卷按成書年代排，卷內亦由早到晚。
        </p>

        <div class="flex items-center gap-2 mt-4">
          <input
            v-model="q"
            type="search"
            placeholder="🔍 搜尋書卷、作者或卷名（中／原文）…"
            class="flex-1 px-3.5 py-2 text-sm bg-white border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-stone-400 focus:border-stone-400"
            @keyup.enter="goSearch"
          />
          <button
            class="shrink-0 text-sm font-medium text-white bg-stone-900 hover:bg-stone-700 rounded-xl px-4 py-2 transition"
            @click="goSearch"
          >搜尋</button>
        </div>
        <NuxtLink
          to="/hellenika/about"
          class="inline-flex items-center gap-1.5 mt-3 text-xs font-medium text-stone-700 hover:text-stone-900 border border-stone-300 hover:border-stone-400 rounded-full px-3 py-1.5 transition"
        >📖 編纂凡例與分類標準 →</NuxtLink>
      </div>

      <!-- 存世狀態圖例 -->
      <div class="flex flex-wrap items-center gap-x-4 gap-y-1.5 mb-8 px-3 py-2 bg-white border border-gray-200 rounded-lg text-[11px]">
        <span class="text-gray-500">存世狀態：</span>
        <span v-for="(m, k) in STATUS_META" :key="k" class="flex items-center gap-1.5">
          <span class="inline-block w-2.5 h-2.5 rounded-full" :class="m.dotCls" />
          <span :class="m.titleCls">{{ m.zh }}</span>
        </span>
        <span class="text-gray-400 ml-auto">本藏經大量文獻僅存殘篇或敵證，狀態一律標明。</span>
      </div>

      <!-- 兩藏 -->
      <section v-for="canon in CANONS" :key="canon.key" class="mb-12">
        <div class="flex items-center gap-3 mb-2">
          <div class="shrink-0 w-11 h-11 rounded-xl bg-stone-900 text-white flex items-center justify-center text-2xl font-serif">{{ canon.glyph }}</div>
          <div class="min-w-0">
            <h2 class="text-lg font-bold text-gray-900 leading-tight">{{ canon.name }}</h2>
            <div class="text-[11px] text-gray-400">{{ canon.name_en }} · {{ canon.subtitle }}</div>
          </div>
          <span class="ml-auto shrink-0 text-[11px] px-2 py-0.5 rounded bg-emerald-50 text-emerald-700">
            {{ canon.volumes.length }} 卷 · {{ canonWorkCount(canon) }} 種
          </span>
        </div>
        <p class="text-xs text-gray-500 leading-relaxed mb-5">{{ canon.summary }}</p>

        <!-- 各部 -->
        <div v-for="part in canon.parts" :key="part.key" class="mb-5">
          <div class="flex items-baseline gap-2 mb-1 border-b border-stone-300 pb-1.5">
            <h3 class="text-sm font-bold text-stone-800">{{ part.label }}</h3>
            <span v-if="part.label_en" class="text-[11px] text-gray-400">{{ part.label_en }}</span>
          </div>
          <p v-if="part.desc" class="text-[11px] text-gray-500 leading-relaxed mb-2">{{ part.desc }}</p>

          <div class="divide-y divide-gray-100 border border-gray-200 rounded-xl overflow-hidden bg-white">
            <NuxtLink
              v-for="v in volumesOf(canon, part)"
              :key="v.key"
              :to="`/hellenika/${canon.key}/${v.key}`"
              class="flex items-center gap-3.5 px-4 py-3 hover:bg-slate-50 transition group"
            >
              <div class="shrink-0 w-9 h-9 rounded-lg bg-stone-800 text-white flex items-center justify-center text-base font-serif">{{ v.sigil }}</div>
              <div class="min-w-0 flex-1">
                <div class="flex items-baseline gap-2 flex-wrap">
                  <span class="font-semibold text-gray-900 group-hover:text-stone-700 transition">{{ v.name }}</span>
                  <span class="text-[11px] text-gray-400">{{ v.name_en }}</span>
                  <span v-if="v.parallel" class="text-[10px] text-stone-500 font-serif">〔對位 {{ v.parallel }}〕</span>
                </div>
                <p class="text-xs text-gray-500 leading-relaxed mt-0.5 line-clamp-2 break-words">{{ v.summary }}</p>
              </div>
              <div class="shrink-0 text-right">
                <div class="text-[11px] text-gray-400 whitespace-nowrap">{{ v.span }}</div>
                <div class="text-[10px] mt-0.5" :class="v.clock === 'mythic' ? 'text-amber-600' : 'text-sky-600'">
                  {{ v.clock === 'mythic' ? '神話時間' : '成書年代' }}
                </div>
              </div>
              <span class="shrink-0 text-[11px] text-gray-400 tabular-nums w-10 text-right">{{ volumeWorkCount(v) }}</span>
            </NuxtLink>
          </div>
        </div>
      </section>

      <div class="mt-4 text-xs text-gray-400 leading-relaxed border-t border-gray-200 pt-4">
        <p>與《基督教大藏經》（/dazangjing）平行的第二部藏經，體例刻意不同：該部為「時代 × 十藏 × 正藏／外藏」，本部為「兩藏 × 部 × 卷」。</p>
        <p class="mt-1">兩部有少數重疊條目（如赫西奧德《神譜》、德爾菲神諭），在該部列為「前藏」的啟示母體前驅，在本部則是本經；同一部書在兩座圖書館各有其位置，以互見標記串連，不作合併。</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  CANONS, TERMINUS, STATUS_META, canonWorkCount, volumeWorkCount,
  type HellenCanon, type HellenPart,
} from '~/data/hellenika'

definePageMeta({ middleware: 'auth' })
useHead({ title: '希臘羅馬大藏經 — Know Graph Lab' })

const q = ref('')
const goSearch = () => {
  const k = q.value.trim()
  navigateTo(k ? `/hellenika/search?q=${encodeURIComponent(k)}` : '/hellenika/search')
}

const totalVolumes = computed(() => CANONS.reduce((n, c) => n + c.volumes.length, 0))
const totalWorks = computed(() => CANONS.reduce((n, c) => n + canonWorkCount(c), 0))

function volumesOf(canon: HellenCanon, part: HellenPart) {
  return part.volumes.map(k => canon.volumes.find(v => v.key === k)).filter(Boolean) as HellenCanon['volumes']
}
</script>
