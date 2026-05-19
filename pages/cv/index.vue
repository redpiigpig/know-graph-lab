<template>
  <div class="min-h-screen bg-slate-50 print:bg-white">
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-40 print:hidden">
      <div class="max-w-4xl mx-auto px-6 h-14 flex items-center justify-between">
        <div class="flex items-center gap-4">
          <NuxtLink to="/writing" class="text-gray-400 hover:text-gray-700 transition text-sm">← 學術活動紀錄</NuxtLink>
          <span class="text-gray-200">|</span>
          <span class="text-sm font-medium text-gray-700">學術履歷</span>
        </div>
        <button @click="print" class="text-xs text-amber-700 bg-amber-50 hover:bg-amber-100 border border-amber-200 px-3 py-1.5 rounded-md transition">列印 / 存為 PDF</button>
      </div>
    </nav>

    <main class="max-w-4xl mx-auto px-6 py-10 print:py-4">
      <article class="bg-white rounded-2xl border border-gray-100 px-10 py-10 print:px-0 print:py-0 print:rounded-none print:border-0 print:shadow-none">

        <!-- 抬頭 -->
        <header class="border-b border-gray-200 pb-5 mb-6">
          <div class="flex items-end justify-between flex-wrap gap-3">
            <div>
              <h1 class="text-3xl font-bold text-gray-900 tracking-wide">張辰瑋</h1>
              <p class="text-sm text-gray-500 mt-1 tracking-wider">Chang, Chen-Wei</p>
            </div>
            <div class="text-xs text-gray-500 leading-relaxed text-right">
              <div>📧 redpiigpig@gmail.com</div>
              <div>📞 0909-901-095</div>
              <div>📍 台北市北投區</div>
            </div>
          </div>
        </header>

        <!-- 現任 -->
        <section class="mb-6">
          <h2 class="cv-h2">現任</h2>
          <ul class="cv-list">
            <li><span class="cv-org">玄奘大學宗教與文化學系</span><span class="cv-role">兼任講師</span>（115 學年度，授課「基督教概論」）</li>
            <li><span class="cv-org">《無境界者》雜誌</span><span class="cv-role">創辦人 ‧ 主編</span>（2025 –）</li>
          </ul>
        </section>

        <!-- 學歷 -->
        <section class="mb-6">
          <h2 class="cv-h2">學歷</h2>
          <ul class="cv-list">
            <li>
              <span class="cv-school">國立臺北教育大學</span>
              <span class="cv-dept">台灣文化研究所 碩士</span>
              <span class="cv-date">2022.09 – 2025.06</span>
              <div class="cv-sub">論文：印順導師人間佛教思想的傳承與實踐：以昭慧法師、性廣法師為核心（指導：蘇瑞鏘教授、侯坤宏教授）</div>
            </li>
            <li>
              <span class="cv-school">國立臺灣大學</span>
              <span class="cv-dept">歷史學系 學士</span>
              <span class="cv-date">2014.09 – 2018.07</span>
              <div class="cv-sub">論文：福音派運動在台灣基督教中的起源與發展（指導：羅士傑教授）</div>
            </li>
          </ul>
        </section>

        <!-- 經歷 -->
        <section class="mb-6">
          <h2 class="cv-h2">經歷</h2>
          <ul class="cv-list">
            <li><span class="cv-org">中央研究院社會學研究所</span><span class="cv-role">兼任研究助理</span><span class="cv-date">2023.01 – 2023.08</span>（楊弘任教授研究計畫）</li>
            <li><span class="cv-org">新店向日葵文理補習班</span><span class="cv-role">國中小班導師</span><span class="cv-date">2022.08 – 2023.08</span></li>
            <li><span class="cv-org">新北市立橫山國民小學</span><span class="cv-role">代理教師</span><span class="cv-date">2020.08 – 2022.07</span></li>
            <li><span class="cv-org">中華基督教衛理公會城中教會</span><span class="cv-role">實習傳道</span><span class="cv-date">2019.08 – 2020.06</span></li>
            <li><span class="cv-org">北投育苗文理補習班</span><span class="cv-role">國中班導師</span><span class="cv-date">2019.01 – 2019.05</span></li>
            <li><span class="cv-org">國立臺灣大學圖書館</span><span class="cv-role">圖書館助理</span><span class="cv-date">2017.09 – 2018.06</span></li>
          </ul>
        </section>

        <!-- 學位論文 -->
        <section class="mb-6">
          <h2 class="cv-h2">學位論文 <span class="cv-h2-count">2</span></h2>
          <ol class="cv-pub-list">
            <li>張辰瑋（2025）。〈印順導師人間佛教思想的傳承與實踐：以昭慧法師、性廣法師為核心〉。國立臺北教育大學台灣文化研究所碩士論文。</li>
            <li>張辰瑋（2018）。〈福音派運動在台灣基督教中的起源與發展〉。國立臺灣大學歷史學系學士論文。</li>
          </ol>
        </section>

        <!-- 期刊論文 -->
        <section class="mb-6">
          <h2 class="cv-h2">期刊論文 <span class="cv-h2-count">3</span></h2>
          <ol class="cv-pub-list">
            <li>張辰瑋（刊登中）。〈信仰與學術的交互作用：近半世紀印順學與印順學派歷史發展回顧（1973–2023）〉。《玄奘佛學研究》。ISSN 1813-3649。玄奘大學。</li>
            <li>張辰瑋（2024.12）。〈從「青年佛教」之精神看印順學派的歷史發展〉。《法印學報》，第 15 期。ISSN 2224-1299。財團法人弘誓文教基金會。</li>
            <li>張辰瑋（2023.12）。〈昭慧法師與性廣法師對印順學的傳承與實踐──以經營佛教弘誓學院、參與社運、闡揚人間佛教禪法為例〉。《法印學報》，第 14 期。ISSN 2224-1299。財團法人弘誓文教基金會。</li>
          </ol>
        </section>

        <!-- 研討會論文 -->
        <section class="mb-6">
          <h2 class="cv-h2">研討會論文 <span class="cv-h2-count">11</span></h2>
          <ol class="cv-pub-list">
            <li>張辰瑋（2025.11）。〈昭慧法師的戒律學思想與實踐：以性別議題為核心〉。第六屆中華國際佛學會議，法鼓山中華佛學研究所。</li>
            <li>張辰瑋（2025.09）。〈從同理心到倫理秩序：主體性動物倫理的建構與社會實踐〉。第二十三屆印順導師思想之理論與實踐學術研討會，玄奘大學台灣佛教研究中心。</li>
            <li>張辰瑋（2024.12）。〈傳道法師與台南妙心寺對印順學派成立之貢獻〉。臺南府城佛影：人間菩薩傳道法師圓寂十週年學術研討會，國立台南大學人文學院。</li>
            <li>張辰瑋（2024.11）。〈信仰與學術的交互作用：近半世紀印順學與印順學派歷史發展回顧（1973–2023）〉。第三屆「臺灣佛教論壇」暨「臺灣佛教之傳承與展望」國際學術會議，玄奘大學台灣佛教研究中心。</li>
            <li>張辰瑋（2024.10）。〈耶佛之間的跨宗教友誼與跨宗教合作：以釋昭慧法師、盧俊義牧師、洪山川主教為例〉。台灣宗教學會 2024 年會「跨域與研修」，台灣宗教學會。</li>
            <li>張辰瑋（2024.09）。〈台灣佛教的宗教反抗傳統：以林秋梧、釋迦宗聖、釋傳道、釋昭慧為例〉。第三十五屆全國佛學論文聯合發表會，台灣大學佛學研究中心。</li>
            <li>張辰瑋（2024.08）。〈從「青年佛教」之精神看印順學派的歷史發展〉。第二十二屆印順導師思想之理論與實踐學術研討會，佛教慈濟慈善基金會。</li>
            <li>張辰瑋（2023.12）。〈台灣漢傳佛教的未來藍圖：以白聖、印順、星雲等長老的芻議為例〉。2023 年慧炬大學院校佛學論文及佛教文學創作獎學金，慧炬雜誌社。</li>
            <li>張辰瑋（2023.11）。〈臺灣師資培育制度的體質檢視：以校內師資培育制度多軌並行的某國立教育大學為例〉。「教育體質的檢視與再造：教改 30 面向未來」國際學術研討會，國立台灣師範大學教育學系。</li>
            <li>張辰瑋（2023.08）。〈昭慧法師與性廣法師對印順學的傳承與實踐：以經營佛教弘誓學院、參與社運、闡揚人間佛教禪法為例〉。第二十一屆印順導師思想之理論與實踐學術研討會，玄奘大學台灣佛教研究中心。</li>
            <li>張辰瑋（2023.06）。〈1960–70 年代福音派運動在台灣華語教會中的崛起〉。2023 第 16 屆「全國研究生歷史學論文研討會」，台灣歷史學會。</li>
          </ol>
        </section>

        <!-- 雜誌專文 -->
        <section class="mb-6">
          <h2 class="cv-h2">雜誌專文 <span class="cv-h2-count">7</span></h2>
          <ol class="cv-pub-list">
            <li>張辰瑋（2025.12）。〈陌生又親切的異鄉之神──簡評約納斯《諾斯替宗教》〉。《無境界者雜誌》，第 6 期。ISSN 3134-7576。</li>
            <li>張辰瑋（2025.10）。〈話語與肉身──簡評林貝克《教義的本質》〉。《無境界者雜誌》，第 5 期。ISSN 3134-7576。</li>
            <li>張辰瑋（2025.08）。〈我願作十方橋──宗教多元主義在當代的建構與田野實踐〉。《無境界者雜誌》，第 4 期。ISSN 3134-7576。</li>
            <li>張辰瑋（2025.06）。〈諸宗教當中的「獨身」與「婚姻」制度演化史〉。《無境界者雜誌》,第 3 期。ISSN 3134-7576。</li>
            <li>張辰瑋（2025.02）。〈基督教中的安那其份子──我心目中的無教會〉。《無境界者雜誌》，第 1 期。ISSN 3134-7576。</li>
            <li>張辰瑋（2024.12）。〈多元路途上的共願者──弘誓青年會成立紀事〉。《弘誓雙月刊》，第 192 期。ISSN 1729-2786。財團法人弘誓文教基金會。</li>
            <li>張辰瑋（2023.04）。〈流麻溝裡的神學〉。《校園雙月刊》，65 卷 2 期。校園書房出版社。</li>
          </ol>
        </section>

        <!-- 報紙社論 -->
        <section class="mb-2">
          <h2 class="cv-h2">報紙社論 <span class="cv-h2-count">3</span></h2>
          <ol class="cv-pub-list">
            <li>張辰瑋（2018.09.21）。〈自由派究竟是什麼？〉。《台灣教會公報》，第 3473 期。</li>
            <li>張辰瑋（2018.09.07）。〈中產階級的講台〉。《台灣教會公報》，第 3471 期。</li>
            <li>張辰瑋（2017.12.26）。〈盡智〉。《台灣教會公報》，第 3435 期。</li>
          </ol>
        </section>

      </article>
    </main>
  </div>
</template>

<script setup lang="ts">
useHead({ title: '學術履歷 — 張辰瑋' })

function print() {
  if (typeof window !== 'undefined') window.print()
}
</script>

<style scoped>
.cv-h2 {
  @apply text-sm font-bold text-amber-800 border-b border-amber-200 pb-1 mb-3 tracking-wider;
}
.cv-h2-count {
  @apply ml-2 text-xs font-normal text-gray-400;
}
.cv-list {
  @apply space-y-1.5 text-sm text-gray-700;
}
.cv-pub-list {
  @apply list-decimal pl-6 space-y-1.5 text-sm text-gray-700 leading-relaxed;
}
.cv-org { @apply font-medium text-gray-900; }
.cv-role { @apply text-gray-600 ml-2; }
.cv-school { @apply font-medium text-gray-900; }
.cv-dept { @apply text-gray-700 ml-2; }
.cv-date { @apply text-xs text-gray-500 ml-2; }
.cv-sub { @apply text-xs text-gray-500 ml-0 mt-0.5 leading-snug; }

@media print {
  :global(body) { background: white; }
  .cv-pub-list { @apply text-xs leading-snug; }
  .cv-list { @apply text-xs leading-snug; }
  .cv-h2 { @apply text-xs mb-2; }
}
</style>
