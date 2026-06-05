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

        <!-- 帳號選單 -->
        <div v-if="user" class="relative flex-shrink-0">
          <button
            @click="accountOpen = !accountOpen"
            :title="user.email"
            class="w-7 h-7 rounded-full bg-gray-100 text-gray-600 text-xs font-semibold flex items-center justify-center hover:bg-gray-200 transition"
          >{{ userInitial }}</button>

          <div v-if="accountOpen">
            <!-- 點擊外部關閉 -->
            <div class="fixed inset-0 z-40" @click="accountOpen = false" />
            <div class="absolute right-0 mt-2 w-56 bg-white border border-gray-200 rounded-xl shadow-lg py-1 z-50">
              <div class="px-3 py-2 border-b border-gray-100">
                <div class="text-[11px] text-gray-400">已登入</div>
                <div class="text-sm text-gray-700 truncate">{{ user.email }}</div>
              </div>
              <NuxtLink to="/settings" @click="accountOpen = false" class="block px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 no-underline">設定</NuxtLink>
              <button @click="logout" class="w-full text-left px-3 py-2 text-sm text-red-600 hover:bg-red-50">登出</button>
            </div>
          </div>
        </div>
        <NuxtLink v-else to="/login" class="text-xs text-blue-600 hover:underline flex-shrink-0">登入</NuxtLink>
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
const supabase = useSupabaseClient()

const accountOpen = ref(false)
const userInitial = computed(() => user.value?.email?.[0]?.toUpperCase() ?? '?')

async function logout() {
  accountOpen.value = false
  await supabase.auth.signOut()
  navigateTo('/login')
}

async function onEditClick() {
  if (!user.value) {
    // 把當前路徑帶到 /login，登入後可以回來（若 login 頁支援 redirect 參數）
    return navigateTo({ path: '/login', query: { redirect: route.fullPath } })
  }
  editMode.value = !editMode.value
}
</script>
