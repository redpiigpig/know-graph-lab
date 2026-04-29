<template>
  <div class="min-h-screen bg-white text-gray-800" :style="{ fontFamily: lang==='en' ? 'Times New Roman,Times,serif' : 'DFKai-SB,標楷體,KaiTi,serif' }">
    <HcjbsHeader :lang="lang" @toggle="toggle" />

    <main style="width:75%; margin:0 auto; padding:28px 0 60px;">
      <nav class="text-sm mb-3" style="font-family: Arial, sans-serif;">
        <NuxtLink to="/Hsuan_Chuang_Studies" class="text-blue-700 hover:underline">{{ lang === 'zh' ? '玄奘佛學研究' : 'HCJBS' }}</NuxtLink>
        <span class="mx-1 text-gray-500">›</span>
        <span class="text-blue-700">{{ lang === 'zh' ? '學術倫理' : 'Academic Ethics' }}</span>
      </nav>
      <hr class="border-gray-300 mb-8" />

      <h2 class="text-2xl font-bold mb-1">{{ lang === 'zh' ? '學術倫理聲明' : 'Statement of Academic Ethics' }}</h2>
      <div class="flex items-center mb-8">
        <div class="h-1 w-28 bg-gray-900" />
        <div class="flex-1 border-t border-dashed border-gray-400" />
      </div>

      <!-- ZH -->
      <div v-if="lang === 'zh'" class="space-y-5 text-[17px] leading-relaxed">
        <p>《玄奘佛學研究》（Hsuan Chuang Journal of Buddhist Studies）致力於出版佛學學術性的研究論文，刊出之論文均匿名經嚴格審查。舉凡涉及剽竊、一稿多投（重複投稿）、杜撰（假造）資料、捉刀（槍手）著作、掛名與未揭露之利益衝突等任何不當行為之研究論文，本期刊一概不予接受。本期刊採用由 Elsevier 建議之《出版倫理》（Publishing Ethics）規定，摘錄並稍作修改如下：</p>

        <p class="font-bold text-lg" style="padding-left:0.5em">壹、編輯者義務</p>

        <p><span class="font-semibold">同儕審查</span>：基於「同儕評審」（peer review）的結果，依據研究議題本身或對其他研究者或讀者的重要性，編輯者可決定是否出版投稿文章。編輯者可授權審查者行使出版決定權。</p>

        <p><span class="font-semibold">公平競爭</span>：編輯者需按論文內容進行評審，不得以種族、性別、性傾向、宗教、國籍與政治信仰為評審標準。</p>

        <p><span class="font-semibold">機密原則</span>：編輯者與相關人員不得向相關作者、審查者、編輯顧問與出版商公開論文之任何訊息。</p>

        <p><span class="font-semibold">公開原則</span>：（1）未取得作者之同意，編輯者不得將論文中未發表資料作為個人研究之用。（2）由同儕審查者所提供之相關修改建議與訊息不得挪為私人使用。（3）當編輯者認為與投稿作者、企業與組織構成利益衝突時，必須迴避稿件審查。（4）編輯者需要求所有研究貢獻者公開相關利益衝突資訊。</p>

        <p class="font-bold text-lg" style="padding-left:0.5em">貳、審查者義務</p>

        <p><span class="font-semibold">審查能力</span>：被委任之審查者，若認為不適任或無法及時完成審查，必須通知編輯委員會，並主動要求撤銷審查委員資格。</p>

        <p><span class="font-semibold">保密原則</span>：審查者必須將審查的論文原稿視為機密文件，不得向編輯者以外之人透漏任何訊息。</p>

        <p><span class="font-semibold">客觀標準</span>：審查委員必須排除個人觀點，公正且客觀地執行評審工作，並提出具建設性的審查意見。</p>

        <p><span class="font-semibold">公開原則與利益衝突</span>：未取得作者之同意，審查者不得將論文中未發表資料挪為己用。當審查委員認為與其他作者、企業與組織構成利益衝突時，必須要求迴避審查工作。</p>

        <p class="font-bold text-lg" style="padding-left:0.5em">參、投稿者（作者）義務</p>

        <p><span class="font-semibold">論文標準</span>：作者需於論文中表達該著作相關研究數據之精確度與重要性，並且明白寫出基本研究資料。研究論文必須包含參考資料與重要細節，以利他人重複實驗。</p>

        <p><span class="font-semibold">原創性與剽竊</span>：作者應確保整篇論文均為原創，若有使用其他作者之論述，須明確引述。剽竊或抄襲等不道德行為是不被接受的。</p>

        <p><span class="font-semibold">重複出版</span>：作者不應同時發表本質上相同的研究論文於多個期刊或出版品，或將同一份原稿投稿至不同期刊。</p>

        <p><span class="font-semibold">論文作者之列名</span>：舉凡對於論文有構思、設計、執行或闡明等重要貢獻者均需列於共同作者之列。通訊作者需確認每位共同作者於投稿前都完成檢視文件，並同意投稿。</p>

        <p><span class="font-semibold">利益衝突</span>：作者需公開揭露任何可能被視為影響研究結果或結果闡釋的利益衝突事項，包含資金補助、計畫補助、僱傭關係、顧問等。</p>

        <p><span class="font-semibold">研究內容之錯誤</span>：當作者發現研究內容含有錯誤或不正確資訊，應迅速通知編輯者，並採取撤回論文或修改內容等相關措施。</p>

        <p class="text-base text-gray-600 border-t border-gray-200 pt-4">
          在評審與發表程序當中，主編、編輯委員會成員與出版者均需遵照
          <a href="https://publicationethics.org/" target="_blank" class="text-blue-700 hover:underline">Committee on Publication Ethics（COPE）</a>
          之指導方針，以確保沒有違反出版倫理與造成任何不當出版之行為。
        </p>
      </div>

      <!-- EN -->
      <div v-else class="space-y-5 text-[17px] leading-relaxed">
        <p>The <em>Hsuan Chuang Journal of Buddhism Studies</em> (HCJBS) is committed to publishing peer-reviewed scholarly articles on Buddhist studies. The journal does not accept manuscripts involving plagiarism, duplicate or simultaneous submission, data fabrication, ghost-writing, nominal authorship, or undisclosed conflicts of interest. HCJBS follows the Publishing Ethics guidelines recommended by Elsevier, as summarized below.</p>

        <p class="font-bold text-lg" style="padding-left:0.5em">I. Editor Obligations</p>

        <p><span class="font-semibold">Peer Review:</span> Based on peer review results, editors decide whether to publish submitted articles based on the scholarly merit and significance of the work to researchers and readers. Editors may delegate publication decisions to reviewers.</p>

        <p><span class="font-semibold">Fair Competition:</span> Editors shall evaluate manuscripts solely on their academic content, without discrimination based on race, gender, sexual orientation, religion, nationality, or political beliefs.</p>

        <p><span class="font-semibold">Confidentiality:</span> Editors and editorial staff shall not disclose any information about submitted manuscripts to unauthorized parties.</p>

        <p><span class="font-semibold">Disclosure:</span> (1) Unpublished data in submitted manuscripts shall not be used for personal research without the author's consent. (2) Information obtained through peer review shall not be used for private purposes. (3) Editors with competing interests must recuse themselves from reviewing related manuscripts. (4) Editors must require full disclosure of conflicts of interest from all contributors.</p>

        <p class="font-bold text-lg" style="padding-left:0.5em">II. Reviewer Obligations</p>

        <p><span class="font-semibold">Competence:</span> Reviewers who feel unqualified to evaluate a manuscript or unable to complete the review in a timely manner must notify the editorial board and request to be relieved of the assignment.</p>

        <p><span class="font-semibold">Confidentiality:</span> Reviewers must treat manuscripts as confidential documents and must not disclose any information to anyone other than the editors.</p>

        <p><span class="font-semibold">Objectivity:</span> Reviewers must set aside personal views and conduct evaluations objectively, providing constructive, evidence-based critiques.</p>

        <p><span class="font-semibold">Disclosure and Conflict of Interest:</span> Reviewers must not use unpublished data from manuscripts for personal use without the author's consent. Reviewers with competing interests must recuse themselves.</p>

        <p class="font-bold text-lg" style="padding-left:0.5em">III. Author Obligations</p>

        <p><span class="font-semibold">Manuscript Standards:</span> Authors must accurately represent the significance of their research data and clearly describe the basic research materials. Papers must include sufficient references and details to allow replication.</p>

        <p><span class="font-semibold">Originality and Plagiarism:</span> Authors must ensure that their manuscripts are original. All cited works must be properly attributed. Plagiarism in any form is unacceptable.</p>

        <p><span class="font-semibold">Duplicate Publication:</span> Authors must not submit manuscripts that are substantively the same to multiple journals or publish essentially the same research in more than one publication.</p>

        <p><span class="font-semibold">Authorship:</span> All individuals who have made significant contributions to conception, design, execution, or interpretation must be listed as co-authors. The corresponding author must confirm that all co-authors have reviewed and approved the final manuscript before submission.</p>

        <p><span class="font-semibold">Conflict of Interest:</span> Authors must disclose any financial or other conflicts of interest that could influence or be perceived to influence the results or interpretation of their research.</p>

        <p><span class="font-semibold">Errors:</span> If an author discovers a significant error or inaccuracy in their published work, they must promptly notify the editors and cooperate in issuing a correction or retraction.</p>

        <p class="text-base text-gray-600 border-t border-gray-200 pt-4">
          All parties involved in the editorial and publication process must adhere to the
          <a href="https://publicationethics.org/" target="_blank" class="text-blue-700 hover:underline">Committee on Publication Ethics (COPE)</a>
          Code of Conduct and Best Practice Guidelines to prevent violations of publication ethics.
        </p>
      </div>

      <!-- Download -->
      <div class="mt-10 pt-6 border-t border-gray-200" style="font-family: Arial, sans-serif;">
        <a href="/api/xuanzang/download?file=ethics" download
          class="inline-flex items-center gap-2 px-5 py-2.5 border border-gray-500 text-sm text-gray-700 hover:bg-gray-100 transition">
          ↓ {{ lang === 'zh' ? '下載學術倫理聲明（Word）' : 'Download Ethics Statement (Word)' }}
        </a>
      </div>
    </main>

    <HcjbsFooter />
  </div>
</template>

<script setup lang="ts">
useHead({ title: "玄奘大學 - 學術倫理", link: [{ rel: 'icon', type: 'image/png', href: '/xuanzang/logo.png' }] })
const lang = useState<'zh' | 'en'>('xuanzangLang', () => 'zh')
const toggle = () => { lang.value = lang.value === 'zh' ? 'en' : 'zh' }
</script>
