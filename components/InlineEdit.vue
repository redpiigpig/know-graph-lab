<template>
  <span class="inline-edit-wrapper" @click="startEdit">
    <!-- View mode -->
    <component
      v-if="!editing"
      :is="multiline ? 'div' : 'span'"
      :class="[
        'cursor-text rounded px-0.5 -mx-0.5 transition hover:bg-yellow-50 hover:ring-1 hover:ring-yellow-300',
        multiline ? 'whitespace-pre-wrap break-words' : '',
        !modelValue && 'text-gray-300 italic',
        $attrs.class,
      ]"
      :title="'點擊編輯'"
    >{{ modelValue || placeholder }}</component>

    <!-- Edit mode: single line -->
    <input
      v-else-if="!multiline"
      ref="inputRef"
      v-model="draft"
      :placeholder="placeholder"
      class="border-none outline-none bg-yellow-50 ring-1 ring-yellow-400 rounded px-1 w-full"
      :class="$attrs.class"
      @blur="commit"
      @keydown.enter.prevent="commit"
      @keydown.esc="cancel"
    />

    <!-- Edit mode: multi-line -->
    <textarea
      v-else
      ref="inputRef"
      v-model="draft"
      :placeholder="placeholder"
      rows="4"
      class="border-none outline-none bg-yellow-50 ring-1 ring-yellow-400 rounded px-1 w-full resize-y leading-relaxed"
      :class="$attrs.class"
      @blur="commit"
      @keydown.esc="cancel"
    />
  </span>
</template>

<script setup lang="ts">
const props = defineProps<{
  value: string;
  placeholder?: string;
  multiline?: boolean;
}>();

const emit = defineEmits<{
  (e: "save", value: string): void;
}>();

defineOptions({ inheritAttrs: false });

const editing = ref(false);
const draft = ref("");
const inputRef = ref<HTMLInputElement | HTMLTextAreaElement | null>(null);

const modelValue = computed(() => props.value);

function startEdit() {
  draft.value = props.value ?? "";
  editing.value = true;
  nextTick(() => inputRef.value?.focus());
}

function commit() {
  editing.value = false;
  if (draft.value !== props.value) {
    emit("save", draft.value);
  }
}

function cancel() {
  editing.value = false;
  draft.value = props.value ?? "";
}
</script>
