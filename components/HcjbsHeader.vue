<template>
  <header style="background:#fff;">

    <!-- Row 1: Logo + university name / controls -->
    <div style="width:75%; margin:0 auto; padding:14px 0 10px; display:flex; align-items:center; justify-content:space-between;">
      <NuxtLink to="/Hsuan_Chuang_Studies" style="display:flex; align-items:center; text-decoration:none;">
        <img :src="logoUrl" alt="玄奘大學"
          style="height:64px; width:auto; display:block;" />
      </NuxtLink>
      <div style="display:flex; align-items:center; gap:16px;">
        <a href="#main-content" style="font-size:13px; color:#888; text-decoration:none; font-family:Arial,sans-serif;">Skip to content</a>
        <span style="width:1px; height:14px; background:#ccc; display:inline-block;"></span>
        <button @click="$emit('toggle')"
          style="font-size:13px; color:#555; border:none; padding:2px 10px; background:none; cursor:pointer; font-family:Arial,sans-serif;">
          {{ lang === 'zh' ? 'EN' : '中文' }}
        </button>
      </div>
    </div>

    <!-- Row 2: Journal name -->
    <div style="width:75%; margin:0 auto; padding:0 0 12px;">
      <NuxtLink to="/Hsuan_Chuang_Studies" style="text-decoration:none;">
        <p style="font-size:30px; font-weight:bold; color:#777; margin:0; font-family:Arial,'Microsoft JhengHei',sans-serif; letter-spacing:1px; transition:color 0.15s; cursor:pointer;"
          onmouseover="this.style.color='#111'" onmouseout="this.style.color='#777'">
          {{ lang === 'zh' ? '玄奘佛學研究' : 'Hsuan Chuang Journal of Buddhism Studies' }}
        </p>
      </NuxtLink>
    </div>

    <!-- Row 3: Nav -->
    <div>
      <div style="width:75%; margin:0 auto; padding:0; display:flex; align-items:center;">
        <NuxtLink
          v-for="item in nav" :key="item.to" :to="item.to"
          style="padding:10px 32px; text-align:center; text-decoration:none; font-size:14px; font-family:Arial,'Microsoft JhengHei',sans-serif; border-right:2px solid #ddd; white-space:nowrap; transition:color 0.15s;"
          :style="route.path === item.to ? 'color:#c8860a; font-weight:600;' : 'color:#444;'"
          @mouseenter="(e) => { if(route.path !== item.to) (e.target as HTMLElement).style.color='#c8860a' }"
          @mouseleave="(e) => { if(route.path !== item.to) (e.target as HTMLElement).style.color='#444' }">
          {{ lang === 'zh' ? item.zh : item.en }}
        </NuxtLink>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
defineProps<{ lang: 'zh' | 'en' }>()
defineEmits(['toggle'])

const logoUrl = '/api/xuanzang/logo'
const route = useRoute()

useHead({
  link: [{ rel: 'icon', type: 'image/png', href: '/api/xuanzang/logo-icon' }]
})

const nav = [
  { zh: '研究學報', en: 'Journal Issues',          to: '/Hsuan_Chuang_Studies' },
  { zh: '編輯委員', en: 'Editorial Board',          to: '/Hsuan_Chuang_Studies/editorial-team' },
  { zh: '投稿指引', en: 'Submission Guidelines',   to: '/Hsuan_Chuang_Studies/submission' },
  { zh: '審查流程', en: 'Review Process',           to: '/Hsuan_Chuang_Studies/review-process' },
  { zh: '學術倫理', en: 'Academic Ethics',          to: '/Hsuan_Chuang_Studies/ethics' },
]
</script>
