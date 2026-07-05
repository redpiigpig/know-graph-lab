<template>
  <div :style="{ minHeight:'100vh', background:'#fff', fontFamily: lang==='en' ? 'Times New Roman,Times,serif' : 'DFKai-SB,標楷體,KaiTi,serif' }">
    <HcjbsHeader :lang="lang" @toggle="toggle" />

    <main id="main-content" style="width:75%; margin:0 auto; padding:28px 0 60px;">
      <!-- Breadcrumb -->
      <div style="font-size:13px; margin-bottom:12px; font-family:Arial,'Microsoft JhengHei',sans-serif;">
        <span style="color:#1a56db;">{{ lang === 'zh' ? '玄奘佛學研究' : 'HCJBS' }}</span>
        <span style="margin:0 4px; color:#666;">›</span>
        <span style="color:#1a56db;">{{ lang === 'zh' ? '研究學報' : 'Journal Issues' }}</span>
      </div>
      <hr style="border:none; border-top:1px solid #ddd; margin-bottom:28px;" />

      <!-- Section title -->
      <h2 style="font-size:22px; font-weight:bold; color:#111; margin:0 0 4px;">
        {{ lang === 'zh' ? '玄奘佛學研究' : 'Hsuan Chuang Journal of Buddhism Studies' }}
      </h2>
      <div style="display:flex; align-items:center; margin-bottom:28px;">
        <div style="height:4px; width:96px; background:#111;"></div>
        <div style="flex:1; border-top:1px dashed #bbb;"></div>
      </div>

      <!-- Issues grid: cover thumbnails -->
      <div style="display:grid; grid-template-columns:repeat(5,1fr); gap:28px 24px;">
        <NuxtLink v-for="issue in issues" :key="issue.issue" :to="`/Hsuan_Chuang_Studies/issue/${issue.issue}`"
          style="display:block; text-decoration:none; color:inherit;"
          @mouseenter="hover = issue.issue" @mouseleave="hover = 0">
          <div :style="{
            aspectRatio:'400 / 560', background:'#f7f7f7', borderRadius:'3px', overflow:'hidden',
            border:'1px solid #e2e2e2',
            boxShadow: hover === issue.issue ? '0 6px 18px rgba(0,0,0,0.16)' : '0 1px 3px rgba(0,0,0,0.08)',
            transform: hover === issue.issue ? 'translateY(-3px)' : 'none',
            transition:'box-shadow 0.18s, transform 0.18s'
          }">
            <img v-if="issue.cover" :src="issue.cover" :alt="`第${issue.issue}期封面`"
              style="width:100%; height:100%; object-fit:cover; display:block;" loading="lazy" />
            <div v-else style="width:100%; height:100%; display:flex; align-items:center; justify-content:center; color:#bbb; font-size:14px;">
              {{ lang === 'zh' ? '無封面' : 'No cover' }}
            </div>
          </div>
          <div :style="{
            textAlign:'center', marginTop:'10px', fontSize:'15px',
            fontFamily: 'Arial,\'Microsoft JhengHei\',sans-serif',
            color: hover === issue.issue ? '#c8860a' : '#333', transition:'color 0.18s'
          }">
            {{ lang === 'zh' ? `第${toZh(issue.issue)}期` : `Vol. ${issue.issue}` }}
          </div>
        </NuxtLink>
      </div>

      <div v-if="!issues.length" style="padding:80px 0; text-align:center; color:#aaa; font-size:14px;">
        {{ loaded ? (lang === 'zh' ? '尚未收錄。' : 'No issues yet.') : (lang === 'zh' ? '載入中⋯' : 'Loading…') }}
      </div>
    </main>

    <HcjbsFooter />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import issuesData from '~/public/content/Hsuan_Chuang_Studies/issues.json'

useHead({ title: "玄奘大學｜玄奘佛學研究", link: [{ rel: 'icon', type: 'image/png', href: '/xuanzang/logo.png' }] })
const lang = useState<'zh' | 'en'>('xuanzangLang', () => 'zh')
const toggle = () => { lang.value = lang.value === 'zh' ? 'en' : 'zh' }

interface Article { title: string; author: string; page: string; pdf: string }
interface Issue { issue: number; url: string; cover: string; articles: Article[] }
const issues = issuesData as Issue[]
const loaded = ref(true)
const hover = ref(0)

const zhNums = ['〇','一','二','三','四','五','六','七','八','九','十']
function toZh(n: number): string {
  if (n <= 10) return zhNums[n]
  if (n < 20) return '十' + (n % 10 ? zhNums[n % 10] : '')
  const t = Math.floor(n / 10), o = n % 10
  return zhNums[t] + '十' + (o ? zhNums[o] : '')
}
</script>
