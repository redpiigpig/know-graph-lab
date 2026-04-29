<template>
  <div class="min-h-screen bg-white text-gray-800" :style="{ fontFamily: lang==='en' ? 'Times New Roman,Times,serif' : 'DFKai-SB,標楷體,KaiTi,serif' }">
    <HcjbsHeader :lang="lang" @toggle="toggle" />

    <main style="width:75%; margin:0 auto; padding:28px 0 60px;">
      <nav class="text-sm mb-3" style="font-family: Arial, sans-serif;">
        <NuxtLink to="/Hsuan_Chuang_Studies" class="text-blue-700 hover:underline">{{ lang === 'zh' ? '玄奘佛學研究' : 'HCJBS' }}</NuxtLink>
        <span class="mx-1 text-gray-500">›</span>
        <span class="text-blue-700">{{ lang === 'zh' ? '審查流程' : 'Review Process' }}</span>
      </nav>
      <hr class="border-gray-300 mb-8" />

      <h2 class="text-2xl font-bold mb-1">{{ lang === 'zh' ? '審查流程' : 'Manuscript Review Process' }}</h2>
      <div class="flex items-center mb-8">
        <div class="h-1 w-24 bg-gray-900" />
        <div class="flex-1 border-t border-dashed border-gray-400" />
      </div>

      <!-- ZH -->
      <div v-if="lang === 'zh'" class="space-y-6 text-[17px] leading-relaxed">
        <p class="font-bold text-lg">壹、審稿流程</p>

        <div>
          <p class="font-semibold mb-2">一、內審</p>
          <ol class="list-none space-y-2 ml-4 text-base">
            <li>1. 執行編輯先就來稿進行初步檢查：
              <ul class="list-none ml-4 mt-1 space-y-1 text-gray-700">
                <li>（1）檢查有無中、英文題目、摘要與關鍵詞。</li>
                <li>（2）檢查是否為頁下注。</li>
                <li>（3）檢查是否符合學術規格，不符合者退件請作者修改後再投稿。</li>
                <li>（4）進行論文比對，超過 15% 由委員網路會議討論。</li>
                <li>（5）確認以上條件符合，再傳送論文摘要於編輯委員網路社群平台，進行內審，討論是否送外審。</li>
              </ul>
            </li>
            <li>2. 編輯委員就來稿摘要與關鍵詞進行內審。若符合本刊之性質與主題領域，即由編委會提供審查名單，進行外審。</li>
            <li>3. 若不全符合本刊性質，而編輯委員有不同意見者，由主編決定是否請作者修改後再投，或逕予退稿。</li>
          </ol>
        </div>

        <div>
          <p class="font-semibold mb-2">二、外審</p>
          <ol class="list-none space-y-2 ml-4 text-base">
            <li>1. 由編輯委員依該文所屬領域提供審查者建議名單，由執行編輯彙總後，交由主編依建議名單排序，執行編輯依排序名單送交匿名審查。審查意見分為四類：
              <ul class="list-none ml-4 mt-1 space-y-1 text-gray-700">
                <li>（1）推薦刊登</li>
                <li>（2）修改後刊登</li>
                <li>（3）修改後再審（原審者複審）</li>
                <li>（4）不推薦刊登</li>
              </ul>
            </li>
            <li>2. 外審稿件審查時間以一個月為原則。</li>
            <li>3. 稿件依外審推薦狀況處理方式如下：</li>
          </ol>

          <!-- Decision matrix -->
          <div class="mt-4 overflow-x-auto">
            <table class="w-full border-collapse text-sm text-center" style="font-family: Arial, '新細明體', sans-serif;">
              <thead>
                <tr class="bg-gray-100">
                  <th class="border border-gray-400 px-2 py-2"></th>
                  <th class="border border-gray-400 px-2 py-2">第二位：推薦刊登</th>
                  <th class="border border-gray-400 px-2 py-2">第二位：修改後刊登</th>
                  <th class="border border-gray-400 px-2 py-2">第二位：修改後再審</th>
                  <th class="border border-gray-400 px-2 py-2">第二位：不推薦刊登</th>
                </tr>
              </thead>
              <tbody>
                <tr class="odd:bg-white even:bg-gray-50">
                  <td class="border border-gray-300 px-2 py-2 font-semibold bg-gray-100">第一位：推薦刊登</td>
                  <td class="border border-gray-300 px-2 py-2">推薦刊登</td>
                  <td class="border border-gray-300 px-2 py-2">修改後刊登</td>
                  <td class="border border-gray-300 px-2 py-2">修正後再送原審者複審</td>
                  <td class="border border-gray-300 px-2 py-2">第三位審查</td>
                </tr>
                <tr class="odd:bg-white even:bg-gray-50">
                  <td class="border border-gray-300 px-2 py-2 font-semibold bg-gray-100">第一位：修改後刊登</td>
                  <td class="border border-gray-300 px-2 py-2">修改後刊登</td>
                  <td class="border border-gray-300 px-2 py-2">修改後刊登</td>
                  <td class="border border-gray-300 px-2 py-2">修正後再送原審者複審</td>
                  <td class="border border-gray-300 px-2 py-2">第三位審查</td>
                </tr>
                <tr class="odd:bg-white even:bg-gray-50">
                  <td class="border border-gray-300 px-2 py-2 font-semibold bg-gray-100">第一位：修改後再審</td>
                  <td class="border border-gray-300 px-2 py-2">修正後再送原審者複審</td>
                  <td class="border border-gray-300 px-2 py-2">修正後再送原審者複審</td>
                  <td class="border border-gray-300 px-2 py-2">修正後再送原審者複審</td>
                  <td class="border border-gray-300 px-2 py-2">第三位審查</td>
                </tr>
                <tr class="odd:bg-white even:bg-gray-50">
                  <td class="border border-gray-300 px-2 py-2 font-semibold bg-gray-100">第一位：不推薦刊登</td>
                  <td class="border border-gray-300 px-2 py-2">不推薦刊登</td>
                  <td class="border border-gray-300 px-2 py-2">第三位審查</td>
                  <td class="border border-gray-300 px-2 py-2">第三位審查</td>
                  <td class="border border-gray-300 px-2 py-2">不推薦刊登</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div>
          <p class="font-semibold mb-2">三、後續處理</p>
          <ol class="list-none space-y-2 ml-4 text-base">
            <li>1. 「同意刊登」之文稿，送編委會認可後，進入刊登程序。</li>
            <li>2. 「修正後刊登」之文稿，作者應於接獲通知後 7–14 天內完成修訂並連同「修訂回應表」寄回編委會，由主編確認後進入刊登程序。</li>
            <li>3. 「修正後再送原審者複審」之文稿，作者應於接獲通知後 7–14 天內完成修訂，並連同「修訂回應表」寄回編委會，由原審者進行複審。</li>
            <li>4. 凡審查結果為「一推薦刊登、一不推薦刊登」，或兩位審查意見落差太大之文稿，由主編或編委會議決是否送第三位審查。三審後若有二通過即予通過；若二不通過則不予通過。</li>
            <li>5. 「不推薦刊登」之文稿，不予刊登。</li>
            <li>6. 複審稿件審查時間以 2 週為限，複審之審查意見只分「推薦刊登」、「修正後刊登」、「不推薦刊登」三級。</li>
          </ol>
        </div>
      </div>

      <!-- EN -->
      <div v-else class="space-y-6 text-[17px] leading-relaxed">
        <p class="font-bold text-lg">I. Review Process</p>

        <div>
          <p class="font-semibold mb-2">1. Internal Review</p>
          <ol class="list-none space-y-2 ml-4 text-base">
            <li>a. The Executive Editor performs an initial screening:
              <ul class="list-none ml-4 mt-1 space-y-1 text-gray-700">
                <li>(1) Verify that Chinese and English titles, abstracts, and keywords are provided.</li>
                <li>(2) Check that notes are formatted as footnotes.</li>
                <li>(3) Verify compliance with academic formatting; non-conforming manuscripts are returned for revision.</li>
                <li>(4) Run a similarity check; manuscripts exceeding 15% are reviewed by the editorial committee online.</li>
                <li>(5) Forward the abstract to the editorial board for internal review to determine whether external review is warranted.</li>
              </ul>
            </li>
            <li>b. The editorial board reviews the abstract and keywords. If the manuscript falls within the journal's scope, the editorial committee proposes a list of external reviewers.</li>
            <li>c. If the manuscript only partially meets the journal's scope and editorial opinions differ, the Editor-in-Chief decides whether to request revision or to reject outright.</li>
          </ol>
        </div>

        <div>
          <p class="font-semibold mb-2">2. External Review</p>
          <ol class="list-none space-y-2 ml-4 text-base">
            <li>a. External reviewers are selected by the editorial board based on field expertise. Manuscripts are sent for anonymous double-blind peer review. Review decisions fall into four categories:
              <ul class="list-none ml-4 mt-1 space-y-1 text-gray-700">
                <li>(1) Accept</li>
                <li>(2) Accept with minor revisions</li>
                <li>(3) Major revisions required (returned to original reviewer)</li>
                <li>(4) Reject</li>
              </ul>
            </li>
            <li>b. The external review period is approximately one month.</li>
            <li>c. Decision matrix based on two reviewers' recommendations:</li>
          </ol>

          <div class="mt-4 overflow-x-auto">
            <table class="w-full border-collapse text-sm text-center" style="font-family: Arial, sans-serif;">
              <thead>
                <tr class="bg-gray-100">
                  <th class="border border-gray-400 px-2 py-2"></th>
                  <th class="border border-gray-400 px-2 py-2">Reviewer 2: Accept</th>
                  <th class="border border-gray-400 px-2 py-2">Reviewer 2: Minor Revision</th>
                  <th class="border border-gray-400 px-2 py-2">Reviewer 2: Major Revision</th>
                  <th class="border border-gray-400 px-2 py-2">Reviewer 2: Reject</th>
                </tr>
              </thead>
              <tbody>
                <tr class="odd:bg-white even:bg-gray-50">
                  <td class="border border-gray-300 px-2 py-2 font-semibold bg-gray-100">Reviewer 1: Accept</td>
                  <td class="border border-gray-300 px-2 py-2">Accept</td>
                  <td class="border border-gray-300 px-2 py-2">Minor Revision</td>
                  <td class="border border-gray-300 px-2 py-2">Major Revision → Re-review</td>
                  <td class="border border-gray-300 px-2 py-2">3rd Reviewer</td>
                </tr>
                <tr class="odd:bg-white even:bg-gray-50">
                  <td class="border border-gray-300 px-2 py-2 font-semibold bg-gray-100">Reviewer 1: Minor Revision</td>
                  <td class="border border-gray-300 px-2 py-2">Minor Revision</td>
                  <td class="border border-gray-300 px-2 py-2">Minor Revision</td>
                  <td class="border border-gray-300 px-2 py-2">Major Revision → Re-review</td>
                  <td class="border border-gray-300 px-2 py-2">3rd Reviewer</td>
                </tr>
                <tr class="odd:bg-white even:bg-gray-50">
                  <td class="border border-gray-300 px-2 py-2 font-semibold bg-gray-100">Reviewer 1: Major Revision</td>
                  <td class="border border-gray-300 px-2 py-2">Major Revision → Re-review</td>
                  <td class="border border-gray-300 px-2 py-2">Major Revision → Re-review</td>
                  <td class="border border-gray-300 px-2 py-2">Major Revision → Re-review</td>
                  <td class="border border-gray-300 px-2 py-2">3rd Reviewer</td>
                </tr>
                <tr class="odd:bg-white even:bg-gray-50">
                  <td class="border border-gray-300 px-2 py-2 font-semibold bg-gray-100">Reviewer 1: Reject</td>
                  <td class="border border-gray-300 px-2 py-2">Reject</td>
                  <td class="border border-gray-300 px-2 py-2">3rd Reviewer</td>
                  <td class="border border-gray-300 px-2 py-2">3rd Reviewer</td>
                  <td class="border border-gray-300 px-2 py-2">Reject</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div>
          <p class="font-semibold mb-2">3. Follow-up Procedures</p>
          <ol class="list-none space-y-2 ml-4 text-base">
            <li>a. Manuscripts accepted for publication are forwarded to the editorial board for final approval before entering the publication process.</li>
            <li>b. Manuscripts requiring minor revisions must be revised and returned with a response letter within 7–14 days of notification.</li>
            <li>c. Manuscripts requiring major revisions must also be returned with a response letter within 7–14 days for re-review by the original reviewer.</li>
            <li>d. Manuscripts where one reviewer accepts and one rejects, or where reviewer opinions diverge significantly, are sent to a third reviewer. If two of three reviewers accept, the manuscript is accepted; if two reject, it is rejected.</li>
            <li>e. Manuscripts rejected by external reviewers will not be published.</li>
            <li>f. The re-review period is limited to two weeks. Re-review decisions are limited to three categories: Accept, Accept with Minor Revisions, or Reject.</li>
          </ol>
        </div>
      </div>

      <!-- Download -->
      <div class="mt-10 pt-6 border-t border-gray-200" style="font-family: Arial, sans-serif;">
        <a href="/api/xuanzang/download?file=review" download
          class="inline-flex items-center gap-2 px-5 py-2.5 border border-gray-500 text-sm text-gray-700 hover:bg-gray-100 transition">
          ↓ {{ lang === 'zh' ? '下載審查流程說明（Word）' : 'Download Review Process Document (Word)' }}
        </a>
      </div>
    </main>

    <HcjbsFooter />
  </div>
</template>

<script setup lang="ts">
useHead({ title: "玄奘大學 - 審查流程", link: [{ rel: 'icon', type: 'image/png', href: '/xuanzang/header_logo.png' }] })
const lang = useState<'zh' | 'en'>('xuanzangLang', () => 'zh')
const toggle = () => { lang.value = lang.value === 'zh' ? 'en' : 'zh' }
</script>
