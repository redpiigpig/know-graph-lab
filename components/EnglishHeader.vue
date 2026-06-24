<template>
  <nav class="bg-white/90 backdrop-blur border-b-2 border-amber-200 sticky top-0 z-40">
    <div class="max-w-5xl mx-auto px-4 h-14 flex items-center gap-3">
      <NuxtLink to="/english" class="flex items-center gap-2 no-underline flex-shrink-0 hover:opacity-80 transition">
        <span class="text-2xl">🌈</span>
        <span class="font-extrabold text-lg bg-gradient-to-r from-rose-500 via-amber-500 to-emerald-500 bg-clip-text text-transparent">
          Happy English
        </span>
      </NuxtLink>

      <template v-if="back">
        <span class="text-amber-200 hidden sm:inline">|</span>
        <NuxtLink :to="back.to" class="text-gray-500 hover:text-gray-800 transition text-sm flex-shrink-0">
          ← {{ back.label }}
        </NuxtLink>
      </template>

      <div class="ml-auto flex items-center gap-2">
        <slot name="actions" />
        <button
          @click="logout"
          class="text-xs px-3 py-1.5 rounded-full bg-gray-100 text-gray-600 hover:bg-gray-200 transition flex-shrink-0"
        >
          登出
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
defineProps<{ back?: { to: string; label: string } }>();
const supabase = useSupabaseClient();
async function logout() {
  await supabase.auth.signOut();
  await navigateTo("/login");
}
</script>
