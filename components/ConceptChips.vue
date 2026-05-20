<template>
  <div class="flex flex-wrap items-center gap-1.5">
    <NuxtLink
      v-for="c in modelValue"
      :key="c.id"
      :to="`/concepts/${c.slug}`"
      class="group inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs border bg-white hover:shadow-sm transition"
      :style="c.color ? { borderColor: c.color, color: c.color } : { borderColor: '#06b6d4', color: '#0e7490' }"
    >
      <span>🕸 {{ c.name }}</span>
      <button v-if="editable" class="text-gray-300 group-hover:text-red-500 transition leading-none -mt-0.5"
              title="移除" @click.prevent.stop="unlink(c)">×</button>
    </NuxtLink>

    <template v-if="editable">
      <div v-if="adding" class="inline-flex items-center gap-1">
        <input
          ref="inputEl"
          v-model="newName"
          @keyup.enter="commit"
          @blur="onBlur"
          @keyup.esc="adding = false"
          placeholder="概念名稱"
          class="px-2 py-0.5 border border-cyan-300 rounded-full text-xs outline-none focus:ring-2 focus:ring-cyan-300 w-32"
        />
        <button class="text-cyan-700 text-xs" @click="commit">＋</button>
      </div>
      <button v-else class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs border border-dashed border-cyan-300 text-cyan-700 hover:bg-cyan-50 transition"
              @click="startAdd">+ 概念</button>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue';
import { authedFetch } from '~/composables/useAuthedFetch';

interface LinkedConcept { id: string; name: string; slug: string; color?: string | null }

const props = defineProps<{
  excerptId: string;
  modelValue: LinkedConcept[];
  editable?: boolean;
}>();
const emit = defineEmits<{
  (e: 'update:modelValue', v: LinkedConcept[]): void;
}>();

const adding = ref(false);
const newName = ref('');
const inputEl = ref<HTMLInputElement | null>(null);
let blurGuard = false;

async function startAdd() {
  adding.value = true;
  await nextTick();
  inputEl.value?.focus();
}

function onBlur() {
  // If user just hit Enter, commit() already fired; don't double-trigger.
  if (blurGuard) { blurGuard = false; return; }
  if (newName.value.trim()) commit();
  else adding.value = false;
}

async function commit() {
  const name = newName.value.trim();
  if (!name) { adding.value = false; return; }
  blurGuard = true;
  newName.value = '';
  try {
    const res: any = await authedFetch('/api/concepts/link-excerpt', {
      method: 'POST',
      body: { excerpt_id: props.excerptId, concept_name: name },
    });
    if (props.modelValue.some((c) => c.id === res.concept_id)) {
      adding.value = false;
      return;
    }
    // Fetch the (possibly new) concept's slug
    const list: any[] = await authedFetch('/api/concepts');
    const found = list.find((c: any) => c.id === res.concept_id);
    const concept: LinkedConcept = found
      ? { id: found.id, name: found.name, slug: found.slug, color: found.color }
      : { id: res.concept_id, name, slug: name, color: null };
    emit('update:modelValue', [...props.modelValue, concept]);
  } catch (e: any) {
    alert(e?.data?.message || '加入失敗');
  } finally {
    adding.value = false;
  }
}

async function unlink(c: LinkedConcept) {
  await authedFetch('/api/concepts/unlink-excerpt', {
    method: 'POST',
    body: { excerpt_id: props.excerptId, concept_id: c.id },
  });
  emit('update:modelValue', props.modelValue.filter((x) => x.id !== c.id));
}
</script>
