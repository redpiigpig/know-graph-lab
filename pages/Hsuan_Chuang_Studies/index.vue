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

      <!-- Issues grid -->
      <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:1px; background:#ccc; border:1px solid #ccc;">
        <a v-for="issue in issues" :key="issue.zh" href="#"
          style="display:block; padding:14px 10px; background:#fff; font-size:15px; color:#333; text-decoration:none; text-align:center; line-height:1.5;"
          onmouseover="this.style.background='#f5f5f5'" onmouseout="this.style.background='#fff'">
          {{ lang === 'zh' ? issue.zh : issue.en }}
        </a>
      </div>
    </main>

    <HcjbsFooter />
  </div>
</template>

<script setup lang="ts">
useHead({ title: "玄奘大學｜玄奘佛學研究", link: [{ rel: 'icon', type: 'image/png', href: '/xuanzang/header_logo.png' }] })
const lang = useState<'zh' | 'en'>('xuanzangLang', () => 'zh')
const toggle = () => { lang.value = lang.value === 'zh' ? 'en' : 'zh' }

const zhNums = ['一','二','三','四','五','六','七','八','九','十','十一','十二','十三','十四','十五','十六','十七','十八','十九','二十','二十一','二十二','二十三','二十四','二十五','二十六','二十七','二十八','二十九','三十','三十一','三十二','三十三','三十四','三十五','三十六','三十七','三十八','三十九','四十','四十一','四十二','四十三']
const issues = zhNums.map((zh, i) => ({
  zh: `第${zh}期玄奘佛學研究`,
  en: `HCJBS Vol. ${i + 1}`,
})).reverse()
</script>
