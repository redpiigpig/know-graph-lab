<template>
  <nav class="bg-white border-b border-gray-200 sticky top-0 z-40">
    <div :class="['mx-auto px-6 h-14 flex items-center gap-3', containerClass]">

      <NuxtLink to="/" class="flex items-center gap-2.5 hover:opacity-80 transition no-underline flex-shrink-0">
        <div class="w-7 h-7 bg-blue-600 rounded-lg flex items-center justify-center text-xs font-bold text-white">K</div>
        <span class="font-semibold text-gray-900 text-sm hidden sm:inline">Know Graph Lab</span>
      </NuxtLink>

      <slot name="breadcrumb">
        <template v-if="back">
          <span class="text-gray-200 hidden sm:inline">|</span>
          <NuxtLink :to="back.to" class="text-gray-400 hover:text-gray-700 transition text-sm flex-shrink-0">← {{ back.label }}</NuxtLink>
        </template>
        <template v-if="title">
          <span class="text-gray-200">|</span>
          <span class="text-sm font-medium text-gray-700 truncate">{{ title }}</span>
        </template>
      </slot>

      <div class="ml-auto flex items-center gap-2 sm:gap-3">
        <slot name="actions" />

        <!-- 編輯按鈕（除實驗網站之外的所有頁面） -->
        <button
          v-if="editable"
          @click="onEditClick"
          :title="user ? (editMode ? '退出編輯模式' : '進入編輯模式') : '登入後可編輯'"
          :class="[
            'text-xs px-2.5 sm:px-3 py-1.5 rounded-lg transition flex items-center gap-1.5 flex-shrink-0',
            editMode && user
              ? 'bg-amber-600 text-white hover:bg-amber-700 shadow-sm'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200',
          ]"
        >
          <span aria-hidden="true">{{ editMode && user ? '✓' : '✏️' }}</span>
          <span class="hidden sm:inline">{{ user ? (editMode ? '完成編輯' : '編輯') : '登入後編輯' }}</span>
          <span class="sm:hidden">{{ user ? (editMode ? '完成' : '編輯') : '登入' }}</span>
        </button>

        <span v-if="user" class="text-xs text-gray-400 hidden md:inline truncate max-w-[180px]">{{ user.email }}</span>
        <NuxtLink v-if="!user && !editable" to="/login" class="text-xs text-blue-600 hover:underline flex-shrink-0">登入</NuxtLink>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    title?: string
    back?: { to: string; label: string }
    editable?: boolean
    containerClass?: string
  }>(),
  {
    editable: true,
    containerClass: 'max-w-7xl',
  }
)

const user = useSupabaseUser()
const editMode = useEditMode()
const route = useRoute()

async function onEditClick() {
  if (!user.value) {
    // 把當前路徑帶到 /login，登入後可以回來（若 login 頁支援 redirect 參數）
    return navigateTo({ path: '/login', query: { redirect: route.fullPath } })
  }
  editMode.value = !editMode.value
}
</script>
