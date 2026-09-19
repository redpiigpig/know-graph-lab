<template>
  <div class="min-h-screen bg-white text-gray-800" :style="{ fontFamily: 'Times New Roman,Times,DFKai-SB,標楷體,KaiTi,serif' }">
    <HcjbsHeader :lang="lang" @toggle="toggle" />

    <main style="width:75%; margin:0 auto; padding:28px 0 60px;">
      <nav class="text-sm mb-3" style="font-family: 'Times New Roman', Times, sans-serif;">
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

        <p class="text-base text-gray-600">下列指導方針依據 Elsevier 與 COPE 之 Best Practice Guidelines for Journal Editors 提供之原則。</p>

        <p><span class="font-semibold">同儕審查</span>：基於「同儕評審」（peer review）的結果，依據研究議題本身或對其他研究者或讀者的重要性，編輯者可決定是否出版投稿文章。編輯者需遵行相關期刊編輯指導原則與法律原則。編輯者可授權審查者行使出版決定權。</p>

        <p><span class="font-semibold">公平競爭</span>：編輯者需按論文內容進行評審，不得以種族、性別、性傾向、宗教、國籍與政治信仰為評審標準。</p>

        <p><span class="font-semibold">機密原則</span>：編輯者與相關人員不得向相關作者、審查者、編輯顧問與出版商公開論文之任何訊息。</p>

        <p><span class="font-semibold">公開原則</span>：（1）未取得作者之同意，編輯者不得將論文中未發表資料作為個人研究之用。（2）由同儕審查者所提供之相關修改建議與訊息不得挪為私人使用。（3）當編輯者認為與投稿作者、企業與組織構成競爭、合作或其他關聯等利益衝突時，必須迴避稿件審查。（4）編輯者需要求所有研究貢獻者公開相關利益衝突資訊。若利益衝突於出版後被揭露，需發表更正說明或發表撤銷出版或利害關係聲明等必要措施。</p>

        <p><span class="font-semibold">調查參與</span>：當投稿論文發生違反著作倫理事件之控訴，本編輯出版者需採取適度因應措施，包括聯繫作者或相關單位並告知其缺失。一旦確定違反學術倫理，必須立刻採取更正、撤回、釐清聲明等措施。即使是已刊登的論文，仍具追訴效力。</p>

        <p class="font-bold text-lg" style="padding-left:0.5em">貳、審查者義務</p>

        <p><span class="font-semibold">審查能力</span>：被委任之審查者，若認為不適任或無法及時完成審查，必須通知編輯委員會，並主動要求撤銷審查委員資格。</p>

        <p><span class="font-semibold">保密原則</span>：審查者必須將審查的論文原稿視為機密文件，不得向編輯者以外之人透漏任何訊息。</p>

        <p><span class="font-semibold">客觀標準</span>：審查委員必須排除個人觀點，公正且客觀地執行評審工作，並提出具建設性的審查意見，委婉地說明審查論文之不足，且需提出佐證。</p>

        <p><span class="font-semibold">來源告知</span>：審查者必須能辨識出作者沒有引註的相關資料，舉凡前人所進行之監測、調查或內容均須附在相關引註內。審查者也必須提醒編輯者留意論文中任何與其他作者可能相似或部分重疊之處。</p>

        <p><span class="font-semibold">公開原則與利益衝突</span>：未取得作者之同意，審查者不得將論文中未發表資料挪為己用。當審查委員認為與其他作者、企業與組織構成競爭、合作或其他關聯等利益衝突時，必須要求迴避審查工作。</p>

        <p class="font-bold text-lg" style="padding-left:0.5em">參、投稿者（作者）義務</p>

        <p><span class="font-semibold">論文標準</span>：作者需於論文中表達該著作相關研究數據之精確度與重要性，並且明白寫出基本研究資料。研究論文必須包含參考資料與重要細節，以利他人重複實驗。任何構成不道德行為之詐欺與不正確敘述，均不被接受。</p>

        <p><span class="font-semibold">資料使用與保留</span>：作者需保留原始數據，能於審查過程中提供給審查者進行審查，並於出版後供大眾使用。</p>

        <p><span class="font-semibold">原創性與剽竊</span>：作者應確保整篇論文均為原創，若有使用其他作者之論述，須明確引述。剽竊或抄襲等不道德行為是不被接受的，包含私自挪用他人結論為自己成果、複製或重新闡示其他作品之精華與仿冒他人作品為自己著作。</p>

        <p><span class="font-semibold">複合、重複或同時出版之出版品</span>：作者不應同時發表本質上相同的研究論文（報告）於多個期刊或出版品，或將同一份原稿投稿至不同期刊，此均不符出版倫理。一般而言，作者曾被發表的研究不能再投稿至另一期刊。但在特定的條件下，二次出版（secondary publication）可被允許，前提是作者與各（第一與二次）期刊編輯者均同意，且二次出版的資料與論述必須與原第一次出版論文相符，而第一次出版的相關資料，也必須列於二次出版品之參考文獻內。</p>

        <p><span class="font-semibold">資料來源之告知</span>：作者必須善盡引用他人作品的責任，並應列舉出影響研究本質的因素。私底下獲得之資訊，例如對話、書信、第三方之討論等，若無資料來源明確的書面授權函，即不應使用或發表。若為因審查他人論文而獲得之資訊，例如審閱他人稿件或計畫補助申請書，如無原作者的書面授權同意，不應使用或發表。</p>

        <p><span class="font-semibold">論文作者之列名</span>：舉凡對於論文有構思、設計、執行或闡明等重要貢獻者均需列於共同作者之列，若有參與相關研究計畫之人員也必須詳列清楚。通訊作者需確保所有具有貢獻的共同作者都列名於作者列，且對論文沒有貢獻者不應列名，並確認每位共同作者於投稿前都完成檢視文件，並同意投稿。</p>

        <p><span class="font-semibold">利益衝突</span>：作者需公開揭露任何可能被視為影響研究結果或結果闡釋的利益衝突事項，包含資金補助、計畫補助、僱傭關係、顧問、材料物品擁有權、報酬、專家證詞費用、專利申請／註冊或捐款授權。未來可能的利益衝突之資料必須儘早提供。</p>

        <p><span class="font-semibold">研究內容之錯誤</span>：當作者發現研究內容含有錯誤或不正確資訊，應迅速通知編輯者，並採取撤回論文或修改內容等相關措施。若編輯者經第三方得知研究論文包含重大錯誤，作者除需採取以上動作，尚需提供編輯者正確資訊。</p>

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

        <p><span class="font-semibold">Disclosure:</span> (1) Unpublished data in submitted manuscripts shall not be used for personal research without the author's consent. (2) Information obtained through peer review shall not be used for private purposes. (3) Editors who have a competing, collaborative, or other connected interest with an author, company, or institution must recuse themselves from handling the manuscript. (4) Editors must require full disclosure of conflicts of interest from all contributors; where a conflict of interest comes to light after publication, a correction, retraction, or statement of interest must be issued as appropriate.</p>

        <p><span class="font-semibold">Participation in Investigations:</span> Where an allegation of research misconduct is made concerning a submitted manuscript, the editors and publisher shall take appropriate measures, including contacting the author or the relevant institution and setting out the deficiency. Once misconduct is established, a correction, retraction, or clarifying statement must be issued at once. Articles already published remain subject to such action.</p>

        <p class="font-bold text-lg" style="padding-left:0.5em">II. Reviewer Obligations</p>

        <p><span class="font-semibold">Competence:</span> Reviewers who feel unqualified to evaluate a manuscript or unable to complete the review in a timely manner must notify the editorial board and request to be relieved of the assignment.</p>

        <p><span class="font-semibold">Confidentiality:</span> Reviewers must treat manuscripts as confidential documents and must not disclose any information to anyone other than the editors.</p>

        <p><span class="font-semibold">Objectivity:</span> Reviewers must set aside personal views and conduct evaluations objectively, providing constructive, evidence-based critiques and explaining the shortcomings of the manuscript with due courtesy.</p>

        <p><span class="font-semibold">Acknowledgement of Sources:</span> Reviewers should identify relevant published work that the author has not cited; any observation, derivation, or argument reported previously should be accompanied by the relevant citation. Reviewers should also call the editors' attention to any substantial similarity or overlap between the manuscript and other published work.</p>

        <p><span class="font-semibold">Disclosure and Conflict of Interest:</span> Reviewers must not use unpublished data from manuscripts for personal use without the author's consent. Reviewers who have a competing, collaborative, or other connected interest with any of the authors, companies, or institutions involved must ask to be excused from the review.</p>

        <p class="font-bold text-lg" style="padding-left:0.5em">III. Author Obligations</p>

        <p><span class="font-semibold">Manuscript Standards:</span> Authors must accurately represent the significance of their research data and clearly describe the basic research materials. Papers must include sufficient references and details to allow replication. Fraudulent or knowingly inaccurate statements constitute unethical behaviour and are unacceptable.</p>

        <p><span class="font-semibold">Data Access and Retention:</span> Authors should retain their raw data, make it available to reviewers during the review process, and keep it accessible after publication.</p>

        <p><span class="font-semibold">Originality and Plagiarism:</span> Authors must ensure that their manuscripts are original. All cited works must be properly attributed. Plagiarism in any form is unacceptable, including appropriating another's conclusions as one's own results, copying or paraphrasing substantial parts of another work, and passing off another's work as one's own.</p>

        <p><span class="font-semibold">Multiple, Redundant, or Concurrent Publication:</span> Authors must not submit manuscripts that are substantively the same to multiple journals or publish essentially the same research in more than one publication; to do so is unethical. As a rule, previously published research may not be submitted to another journal. Secondary publication is permissible under defined conditions: both the author and the editors of the first and second journals agree; the data and interpretation of the secondary publication correspond to the original; and the original publication is cited in the references of the secondary publication.</p>

        <p><span class="font-semibold">Acknowledgement of Sources:</span> Authors must properly cite the work of others and identify the factors that shaped the nature of the research. Information obtained privately — in conversation, correspondence, or discussion with third parties — must not be used or reported without explicit written permission from the source. Information obtained in the course of confidential services, such as reviewing manuscripts or grant applications, must not be used or reported without the written permission of the original author.</p>

        <p><span class="font-semibold">Authorship:</span> All individuals who have made significant contributions to conception, design, execution, or interpretation must be listed as co-authors, and other participants in the research project must be properly acknowledged. The corresponding author must ensure that all contributing co-authors, and no one who has not contributed, appear in the author list, and that all co-authors have reviewed and approved the manuscript before submission.</p>

        <p><span class="font-semibold">Conflict of Interest:</span> Authors must disclose any conflicts of interest that could influence or be perceived to influence the results or interpretation of their research, including funding, grants, employment, consultancies, ownership of materials, honoraria, expert-testimony fees, patent applications or registrations, and donations. Potential future conflicts should be disclosed as early as possible.</p>

        <p><span class="font-semibold">Errors:</span> If an author discovers a significant error or inaccuracy in their published work, they must promptly notify the editors and cooperate in issuing a correction or retraction. Where the editors learn of a significant error from a third party, the author must in addition supply the editors with the correct information.</p>

        <p class="text-base text-gray-600 border-t border-gray-200 pt-4">
          All parties involved in the editorial and publication process must adhere to the
          <a href="https://publicationethics.org/" target="_blank" class="text-blue-700 hover:underline">Committee on Publication Ethics (COPE)</a>
          Code of Conduct and Best Practice Guidelines to prevent violations of publication ethics.
        </p>
      </div>

      <!-- Download -->
      <div class="mt-10 pt-6 border-t border-gray-200" style="font-family: 'Times New Roman', Times, sans-serif;">
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
