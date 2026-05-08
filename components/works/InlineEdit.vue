<template>
  <component
    :is="tag"
    v-if="!editable"
    :class="displayClass"
  >{{ modelValue || placeholder }}</component>

  <component
    v-else-if="!editing"
    :is="tag"
    :class="[displayClass, 'cursor-text hover:bg-amber-50/60 rounded px-1 -mx-1 transition']"
    :title="`點擊編輯`"
    @click="enter"
  >{{ modelValue || placeholderHint }}</component>

  <textarea
    v-else-if="multiline"
    ref="inputRef"
    v-model="draft"
    :class="[displayClass, 'block w-full px-1 -mx-1 bg-white border border-amber-300 rounded outline-none resize-none focus:ring-1 focus:ring-amber-300']"
    :rows="rows"
    :placeholder="placeholder"
    @blur="commit"
    @keydown.esc.prevent="cancel"
    @keydown.meta.enter.prevent="commit"
    @keydown.ctrl.enter.prevent="commit"
  ></textarea>

  <input
    v-else
    ref="inputRef"
    v-model="draft"
    type="text"
    :class="[displayClass, 'px-1 -mx-1 bg-white border border-amber-300 rounded outline-none focus:ring-1 focus:ring-amber-300']"
    :placeholder="placeholder"
    @blur="commit"
    @keydown.esc.prevent="cancel"
    @keydown.enter.prevent="commit"
  />
</template>

<script setup lang="ts">
const props = withDefaults(defineProps<{
  modelValue: string | null
  editable: boolean
  tag?: string
  multiline?: boolean
  rows?: number
  placeholder?: string
  placeholderHint?: string
  displayClass?: string
}>(), {
  tag: 'span',
  multiline: false,
  rows: 3,
  placeholder: '',
  placeholderHint: '（點擊編輯）',
  displayClass: '',
})

const emit = defineEmits<{
  'update:modelValue': [string]
  'save': [string]
}>()

const editing = ref(false)
const draft = ref(props.modelValue ?? '')
const inputRef = ref<HTMLInputElement | HTMLTextAreaElement>()

watch(() => props.modelValue, val => { if (!editing.value) draft.value = val ?? '' })

async function enter() {
  if (!props.editable) return
  draft.value = props.modelValue ?? ''
  editing.value = true
  await nextTick()
  inputRef.value?.focus()
  if (inputRef.value && 'select' in inputRef.value) inputRef.value.select()
}

function commit() {
  if (!editing.value) return
  editing.value = false
  const val = draft.value
  if (val !== (props.modelValue ?? '')) {
    emit('update:modelValue', val)
    emit('save', val)
  }
}

function cancel() {
  editing.value = false
  draft.value = props.modelValue ?? ''
}
</script>
