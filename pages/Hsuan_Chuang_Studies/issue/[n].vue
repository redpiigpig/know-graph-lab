<template>
  <div :style="{ minHeight:'100vh', background:'#fff', fontFamily: lang==='en' ? 'Times New Roman,Times,serif' : 'DFKai-SB,標楷體,KaiTi,serif' }">
    <HcjbsHeader :lang="lang" @toggle="toggle" />

    <main id="main-content" style="width:75%; margin:0 auto; padding:28px 0 60px;">
      <!-- Breadcrumb -->
      <div style="font-size:13px; margin-bottom:12px; font-family:Arial,'Microsoft JhengHei',sans-serif;">
        <span style="color:#1a56db;">{{ lang === 'zh' ? '玄奘佛學研究' : 'HCJBS' }}</span>
        <span style="margin:0 4px; color:#666;">›</span>
        <NuxtLink to="/Hsuan_Chuang_Studies" style="color:#1a56db; text-decoration:none;">{{ lang === 'zh' ? '研究學報' : 'Journal Issues' }}</NuxtLink>
        <span style="margin:0 4px; color:#666;">›</span>
        <span style="color:#333;">{{ lang === 'zh' ? `第${toZh(n)}期` : `Vol. ${n}` }}</span>
      </div>
      <hr style="border:none; border-top:1px solid #ddd; margin-bottom:28px;" />

      <div v-if="issue" style="display:flex; gap:36px; align-items:flex-start;">
        <!-- Cover -->
        <div style="flex-shrink:0; width:220px;">
          <div style="aspect-ratio:400/560; border:1px solid #e2e2e2; border-radius:3px; overflow:hidden; background:#f7f7f7; box-shadow:0 2px 8px rgba(0,0,0,0.1);">
            <img v-if="issue.cover" :src="issue.cover" :alt="`第${n}期封面`" style="width:100%; height:100%; object-fit:cover; display:block;" />
          </div>
          <a v-if="issue.url" :href="issue.url" target="_blank" rel="noopener"
            style="display:block; text-align:center; margin-top:12px; font-size:13px; color:#888; text-decoration:none; font-family:Arial,'Microsoft JhengHei',sans-serif;"
            onmouseover="this.style.color='#c8860a'" onmouseout="this.style.color='#888'">
            {{ lang === 'zh' ? '玄奘大學原始頁 ↗' : 'Original page ↗' }}
          </a>
        </div>

        <!-- Articles -->
        <div style="flex:1; min-width:0;">
          <h2 style="font-size:22px; font-weight:bold; color:#111; margin:0 0 4px;">
            {{ lang === 'zh' ? `第${toZh(n)}期玄奘佛學研究學報` : `HCJBS Vol. ${n}` }}
          </h2>
          <div style="display:flex; align-items:center; margin-bottom:24px;">
            <div style="height:4px; width:96px; background:#111;"></div>
            <div style="flex:1; border-top:1px dashed #bbb;"></div>
          </div>

          <!-- Column header -->
          <div style="display:flex; align-items:center; padding:0 4px 8px; border-bottom:2px solid #333; font-family:Arial,'Microsoft JhengHei',sans-serif; font-size:13px; color:#666; font-weight:600;">
            <span style="flex:1;">{{ lang === 'zh' ? '篇名' : 'Title' }}</span>
            <span style="width:120px; flex-shrink:0;">{{ lang === 'zh' ? '作者' : 'Author' }}</span>
            <span style="width:52px; flex-shrink:0; text-align:center;">{{ lang === 'zh' ? '頁數' : 'Page' }}</span>
            <span style="width:88px; flex-shrink:0; text-align:center;">{{ lang === 'zh' ? '全文' : 'PDF' }}</span>
          </div>

          <div v-for="(a, i) in issue.articles" :key="i"
            style="display:flex; align-items:center; padding:14px 4px; border-bottom:1px solid #eee;">
            <span style="flex:1; font-size:16px; color:#222; line-height:1.5; padding-right:12px;">{{ a.title }}</span>
            <span style="width:120px; flex-shrink:0; font-size:14px; color:#555;">{{ a.author }}</span>
            <span style="width:52px; flex-shrink:0; text-align:center; font-size:14px; color:#777; font-family:Arial,sans-serif;">{{ a.page }}</span>
            <span style="width:88px; flex-shrink:0; text-align:center;">
              <a v-if="a.pdf" :href="a.pdf" target="_blank" rel="noopener"
                style="display:inline-block; padding:4px 12px; font-size:13px; color:#fff; background:#c8860a; border-radius:3px; text-decoration:none; font-family:Arial,'Microsoft JhengHei',sans-serif; white-space:nowrap;"
                onmouseover="this.style.background='#a86e05'" onmouseout="this.style.background='#c8860a'">
                {{ lang === 'zh' ? 'PDF' : 'PDF' }} ↓
              </a>
              <span v-else style="font-size:12px; color:#ccc;">—</span>
            </span>
          </div>
        </div>
      </div>

      <div v-else style="padding:80px 0; text-align:center; color:#aaa; font-size:14px;">
        {{ loaded ? (lang === 'zh' ? '查無此期。' : 'Issue not found.') : (lang === 'zh' ? '載入中⋯' : 'Loading…') }}
      </div>
    </main>

    <HcjbsFooter />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import issuesData from '~/public/content/Hsuan_Chuang_Studies/issues.json'

const lang = useState<'zh' | 'en'>('xuanzangLang', () => 'zh')
const toggle = () => { lang.value = lang.value === 'zh' ? 'en' : 'zh' }

const route = useRoute()
const n = computed(() => parseInt(String(route.params.n), 10))

interface Article { title: string; author: string; page: string; pdf: string }
interface Issue { issue: number; url: string; cover: string; articles: Article[] }
const allIssues = issuesData as Issue[]
const issue = computed<Issue | null>(() => allIssues.find(x => x.issue === n.value) ?? null)
const loaded = ref(true)

useHead(() => ({ title: `第${n.value}期 — 玄奘佛學研究`, link: [{ rel: 'icon', type: 'image/png', href: '/xuanzang/logo.png' }] }))

const zhNums = ['〇','一','二','三','四','五','六','七','八','九','十']
function toZh(v: number): string {
  if (!v) return ''
  if (v <= 10) return zhNums[v]
  if (v < 20) return '十' + (v % 10 ? zhNums[v % 10] : '')
  const t = Math.floor(v / 10), o = v % 10
  return zhNums[t] + '十' + (o ? zhNums[o] : '')
}
</script>
