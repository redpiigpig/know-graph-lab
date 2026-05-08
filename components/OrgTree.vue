<template>
  <li class="relative pl-5">
    <span
      class="absolute left-0 top-2.5 w-3 h-px bg-gray-300"
      aria-hidden="true"
    />
    <div
      :class="[
        'inline-block px-3 py-1 rounded-md text-sm',
        depth === 0
          ? 'bg-rose-100 text-rose-900 font-semibold border border-rose-200'
          : depth === 1
            ? 'bg-amber-50 text-amber-900 font-medium border border-amber-200'
            : depth === 2
              ? 'bg-slate-100 text-slate-800 border border-slate-200'
              : 'text-gray-700',
      ]"
    >{{ node.label }}</div>
    <ul v-if="node.children?.length" class="mt-1 ml-2 border-l border-gray-200 space-y-1">
      <OrgTree
        v-for="(c, i) in node.children" :key="i"
        :node="c"
        :depth="depth + 1"
      />
    </ul>
  </li>
</template>

<script setup lang="ts">
import type { TreeNode } from '~/composables/usePongReports';

defineProps<{ node: TreeNode; depth?: number }>();
</script>
