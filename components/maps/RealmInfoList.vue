<template>
  <div class="space-y-6">
    <section
      v-for="realm in REALMS"
      :key="realm.id"
      class="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm"
    >
      <header
        class="flex items-center gap-3 px-4 py-3 border-b border-gray-100"
        :style="{ background: realm.color + '14' }"
      >
        <div
          class="w-9 h-9 rounded-lg flex items-center justify-center text-white font-bold text-sm flex-shrink-0"
          :style="{ background: realm.color }"
        >
          {{ realm.index }}
        </div>
        <div class="flex-1 min-w-0">
          <div class="font-semibold text-gray-900 text-base">{{ realm.name_zh }} <span class="text-xs text-gray-400 font-normal ml-1">({{ realm.name_en }})</span></div>
        </div>
      </header>

      <div class="divide-y divide-gray-100">
        <article
          v-for="sphere in spheresByRealm(realm.id)"
          :key="sphere.id"
          class="px-4 py-3"
        >
          <div class="flex items-baseline gap-2 mb-2">
            <h3 class="text-sm font-semibold text-gray-900">{{ sphere.name_zh }}</h3>
            <span class="text-[11px] text-gray-400">{{ sphere.name_en }}</span>
          </div>
          <ol class="flex flex-wrap gap-x-1 gap-y-1.5 text-xs">
            <li
              v-for="(m, idx) in sphere.members"
              :key="`${sphere.id}-${m.iso_a3}-${m.admin1 || ''}-${idx}`"
              class="inline-flex items-center"
            >
              <span
                v-if="idx > 0"
                class="text-gray-300 mx-1 select-none"
              >→</span>
              <span
                class="inline-flex items-center px-2 py-0.5 rounded-md border"
                :class="m.is_extension
                  ? 'border-dashed border-gray-300 text-gray-500 bg-gray-50'
                  : 'border-gray-200 text-gray-800 bg-white'"
              >{{ m.label }}</span>
            </li>
          </ol>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { REALMS, spheresByRealm } from '~/data/maps/world-religions'
</script>
