<template>
  <div class="min-h-screen bg-white text-gray-800" :style="{ fontFamily: lang==='en' ? 'Times New Roman,Times,serif' : 'DFKai-SB,標楷體,KaiTi,serif' }">
    <HcjbsHeader :lang="lang" @toggle="toggle" />

    <main style="width:75%; margin:0 auto; padding:28px 0 60px;">
      <nav class="text-sm mb-3" style="font-family: Arial, sans-serif;">
        <NuxtLink to="/Hsuan_Chuang_Studies" class="text-blue-700 hover:underline">{{ lang === 'zh' ? '玄奘佛學研究' : 'HCJBS' }}</NuxtLink>
        <span class="mx-1 text-gray-500">›</span>
        <span class="text-blue-700">{{ lang === 'zh' ? 'AI 使用規範' : 'AI Use Policy' }}</span>
      </nav>
      <hr class="border-gray-300 mb-8" />

      <h2 class="text-2xl font-bold mb-1">
        {{ lang === 'zh' ? '生成式人工智慧（AI）使用規範' : 'Policy on the Use of Generative AI' }}
      </h2>
      <div class="flex items-center mb-8">
        <div class="h-1 w-32 bg-gray-900" />
        <div class="flex-1 border-t border-dashed border-gray-400" />
      </div>

      <!-- ZH -->
      <div v-if="lang === 'zh'" class="space-y-6 text-[17px] leading-relaxed">
        <p>因應生成式 AI 技術於學術領域之普及，為確保研究之真實性與自主思考，學生使用相關工具（如 ChatGPT、Claude 等）時，必須嚴格遵守以下三道防線：</p>

        <div>
          <p class="font-bold text-lg mb-2">一、透明揭露原則（Disclosure）</p>
          <p>作者於論文或研究紀要中，若有使用生成式 AI 工具進行輔助（如語句潤飾、結構建議、程式碼編寫或優化等），必須於論文之方法章節、附錄或致謝中，清楚且誠實地揭露「AI 工具名稱、版本、使用日期及具體使用方法（如核心提示詞 Prompt）」。</p>
        </div>

        <div>
          <p class="font-bold text-lg mb-2">二、人類須負最終全責原則</p>
          <p>生成式 AI 工具僅為研究與寫作之輔助手段，無法辨識資料之真實性，亦無法承擔學術、法律與道德責任。因此，絕對不可將 AI 工具列為論文或報告之「共同作者」。即使在有 AI 輔助之情況下，研究者（作者本人）仍須對論文或報告之正確性與原創性負擔 100% 的最終責任。</p>
        </div>

        <div>
          <p class="font-bold text-lg mb-2">三、機密與個資安全限制</p>
          <p>為防止智慧財產權與隱私外洩，嚴格禁止將具保密義務之研究數據、未經授權之實驗資料、他人個人資料（個資），或未公開之審查中稿件輸入至公開或雲端的 AI 模型中。</p>
        </div>
      </div>

      <!-- EN -->
      <div v-else class="space-y-6 text-[17px] leading-relaxed">
        <p>In response to the spread of generative AI in academic work, and in order to safeguard the authenticity of research and independent thinking, students using such tools (ChatGPT, Claude, and the like) must strictly observe the following three safeguards:</p>

        <div>
          <p class="font-bold text-lg mb-2">I. Disclosure</p>
          <p>Where generative AI tools have been used in an auxiliary capacity — for language polishing, structural suggestions, code writing or optimization, and so forth — the author must disclose clearly and honestly, in the methodology section, an appendix, or the acknowledgements, the name and version of the AI tool, the dates on which it was used, and the specific manner of use (including the core prompts).</p>
        </div>

        <div>
          <p class="font-bold text-lg mb-2">II. Final Responsibility Rests with the Human Author</p>
          <p>Generative AI tools are aids to research and writing only. They cannot ascertain the truth of the material they produce, and they cannot bear academic, legal, or moral responsibility. AI tools must therefore never be listed as “co-authors” of an article or report. Even where AI assistance has been used, the researcher (the author) remains 100% responsible for the accuracy and originality of the work.</p>
        </div>

        <div>
          <p class="font-bold text-lg mb-2">III. Confidentiality and Personal Data</p>
          <p>To prevent the leakage of intellectual property and private information, it is strictly forbidden to enter confidential research data, unauthorized experimental data, other people's personal data, or unpublished manuscripts under review into public or cloud-based AI models.</p>
        </div>
      </div>

      <!-- Download -->
      <div class="mt-10 pt-6 border-t border-gray-200" style="font-family: Arial, sans-serif;">
        <a href="/api/xuanzang/download?file=ai" download
          class="inline-flex items-center gap-2 px-5 py-2.5 border border-gray-500 text-sm text-gray-700 hover:bg-gray-100 transition">
          ↓ {{ lang === 'zh' ? '下載 AI 使用規範（Word）' : 'Download AI Use Policy (Word)' }}
        </a>
      </div>
    </main>

    <HcjbsFooter />
  </div>
</template>

<script setup lang="ts">
useHead({ title: "玄奘大學 - AI 使用規範", link: [{ rel: 'icon', type: 'image/png', href: '/xuanzang/logo.png' }] })
const lang = useState<'zh' | 'en'>('xuanzangLang', () => 'zh')
const toggle = () => { lang.value = lang.value === 'zh' ? 'en' : 'zh' }
</script>
