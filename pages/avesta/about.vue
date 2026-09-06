<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader title="編纂凡例" :back="{ to: '/avesta', label: '祆教經典' }" container-class="max-w-3xl" />

    <div class="flex-1 max-w-3xl w-full mx-auto px-6 py-10 space-y-8">
      <section>
        <h1 class="text-2xl font-bold text-gray-900 mb-3">📖 祆教經典 · 編纂凡例</h1>
        <p class="text-sm text-gray-600 leading-relaxed break-words">
          本區收錄祆教（瑣羅亞斯德教）現存的全部傳世文獻，分四藏，以原文轉寫／英譯／繁體中文三欄逐段對照。
          以下說明收錄準則、分部依據、存世狀態的定義，以及三欄各自的來源與缺口——
          尤其是缺口：一部藏經最該說清楚的，是它沒有什麼。
        </p>
      </section>

      <section>
        <h2 class="text-base font-bold text-gray-900 mb-2 border-b border-orange-200 pb-1.5">一、分部照祆教自己的禮儀單位，本站不另立卷次</h2>
        <p class="text-sm text-gray-600 leading-relaxed break-words">
          這是本區與姊妹區
          <NuxtLink to="/hellenika" class="text-orange-800 hover:underline">《希臘羅馬大藏經》</NuxtLink>
          最根本的差別。希臘宗教從來沒有正典，那部藏經的廿四卷是編者按文類光譜所立、可以辯論；
          祆教卻**自己有**一套分部——耶斯那 72 章、維斯佩拉德 24 章、祓魔法典 22 章、耶什特 21 首——
          那是薩珊祭司傳下來的禮儀單位，伊朗與印度的火廟今天仍照這個數目誦唸。
        </p>
        <p class="text-sm text-gray-600 leading-relaxed break-words mt-2">
          所以本區照抄，不重編。按主題把它拆散重組，等於把一套活的禮儀改成書架分類。
        </p>
      </section>

      <section>
        <h2 class="text-base font-bold text-gray-900 mb-2 border-b border-orange-200 pb-1.5">二、四藏的分界</h2>
        <div class="space-y-3">
          <div v-for="canon in CANONS" :key="canon.key" class="bg-white border border-gray-200 rounded-xl p-4">
            <div class="flex items-center gap-2 mb-1 flex-wrap">
              <span
                class="w-7 h-7 rounded-lg text-white flex items-center justify-center text-sm font-serif shrink-0"
                :class="canon.scriptural ? 'bg-orange-900' : 'bg-stone-500'"
              >{{ canon.glyph }}</span>
              <span class="font-semibold text-gray-900">{{ canon.name }}</span>
              <span class="text-[11px] text-gray-400">{{ canon.subtitle }}</span>
              <span
                v-if="!canon.scriptural"
                class="text-[10px] px-1.5 py-0.5 rounded bg-amber-100 text-amber-800"
              >非經典</span>
            </div>
            <p class="text-xs text-gray-500 leading-relaxed break-words">{{ canon.summary }}</p>
          </div>
        </div>
        <p class="text-xs text-gray-500 leading-relaxed break-words mt-3">
          <b class="text-gray-700">為什麼王室銘文列為附錄而不算經典。</b>
          阿契美尼德銘文是否屬於祆教文獻，學界至今無定論：支持者說大流士獨尊阿胡拉‧馬茲達、
          以「真理對謊言」構築秩序、行王權神授，這套語彙在阿維斯陀裡一一對得上；
          反對者說銘文從頭到尾沒有出現查拉圖斯特拉、沒有迦薩的專門術語、沒有不朽聖者，
          而且大流士是土葬的——那正好違反祆教最嚴格的潔淨法。本站的處理是收但不算經，
          理由只有一個而且很強：這是這個信仰世界最早的、有確切紀年與具名作者的文字證據，
          比現存最早的阿維斯陀寫本早了約兩千年。
        </p>
      </section>

      <section>
        <h2 class="text-base font-bold text-gray-900 mb-2 border-b border-orange-200 pb-1.5">三、五級存世狀態</h2>
        <p class="text-sm text-gray-600 leading-relaxed break-words mb-3">
          祆教的殘缺程度極高：薩珊時代的二十一部納斯克，今日僅《祓魔法典》完整傳世。
          殘缺不是元資料，是這些文本的處境本身，故一律在版面上標色標明。
        </p>
        <div class="divide-y divide-gray-100 border border-gray-200 rounded-xl overflow-hidden bg-white">
          <div v-for="(m, k) in STATUS_META" :key="k" class="flex items-start gap-3 px-4 py-2.5">
            <span class="shrink-0 inline-block w-2.5 h-2.5 rounded-full mt-1.5" :class="m.dotCls" />
            <span class="shrink-0 w-16 text-sm font-medium" :class="m.titleCls">{{ m.zh }}</span>
            <span class="min-w-0 flex-1 text-xs text-gray-500 leading-relaxed break-words">{{ m.desc }}</span>
          </div>
        </div>
      </section>

      <section>
        <h2 class="text-base font-bold text-gray-900 mb-2 border-b border-orange-200 pb-1.5">四、三欄的來源與缺口</h2>
        <div class="space-y-3">
          <div class="bg-white border border-gray-200 rounded-xl p-4">
            <div class="font-semibold text-gray-900 text-sm mb-1">原文轉寫</div>
            <p class="text-xs text-gray-500 leading-relaxed break-words">
              阿維斯陀語部分取自 avesta.org（蓋爾德納校本轉寫）與法蘭克福 TITUS 語料庫，
              傳世文本大致齊全。<b class="text-gray-700">缺口在巴列維文獻</b>——中古波斯語的轉寫線上零散，
              估計僅能取得六七成，其餘只有英譯。
            </p>
          </div>
          <div class="bg-white border border-gray-200 rounded-xl p-4">
            <div class="font-semibold text-gray-900 text-sm mb-1">英譯</div>
            <p class="text-xs text-gray-500 leading-relaxed break-words">
              以《東方聖書》的公有領域舊譯為主：阿維斯陀為達梅斯特（第 4、23 卷）與米爾斯（第 31 卷），
              巴列維文獻為韋斯特（第 5、18、24、37、47 卷）。這八卷同時收在本站的
              <NuxtLink to="/sacred-books-east" class="text-orange-800 hover:underline">《東方聖書》</NuxtLink> 專區。
              <b class="text-gray-700">缺口在《丹卡爾德》第 3、6 卷</b>——韋斯特未譯，
              通行的德梅納斯法譯（1958–73）與沙克德英譯（1979）仍在版權內，不能作為對照欄底本。
            </p>
          </div>
          <div class="bg-white border border-gray-200 rounded-xl p-4">
            <div class="font-semibold text-gray-900 text-sm mb-1">繁體中文</div>
            <p class="text-xs text-gray-500 leading-relaxed break-words">
              <b class="text-gray-700">這一欄在華語世界近乎空白，全部為本站自譯。</b>
              既有的中譯僅元文琪譯《阿維斯塔——瑣羅亞斯德教聖書》（商務印書館，2005／2024 新版），
              而它是伊朗學者杜斯特哈赫的選編本、簡體，且仍在版權內，故不採用。
              巴列維文獻則無成規模的中譯。本站以公有領域英譯為中介逐段翻譯，
              無英譯可依據而直接譯自原文轉寫者，會在該篇頁面上以警示色標明——
              那條路徑的可信度較低，讀者有權知道。
            </p>
          </div>
        </div>
      </section>

      <section>
        <h2 class="text-base font-bold text-gray-900 mb-2 border-b border-orange-200 pb-1.5">五、阿維斯陀字母與拉丁轉寫</h2>
        <p class="text-sm text-gray-600 leading-relaxed break-words mb-2">
          主欄一律是拉丁轉寫，因為學界的引用、檢索與比對都用轉寫。阿維斯陀字母欄是給眼睛看的，
          由轉寫程式轉換而得，<b class="text-gray-700">不是抄本影像</b>，引用請一律以轉寫為準。
        </p>
        <div class="px-3 py-2.5 bg-amber-50 border border-amber-200 rounded-lg mb-3">
          <div class="text-[11px] font-semibold text-amber-900 mb-0.5">為什麼有些篇章沒有字母切換</div>
          <p class="text-[11px] text-amber-800 leading-relaxed break-words">
            轉寫有兩套方案。霍夫曼式學術轉寫（<span class="italic">ahura mazdā</span>）一字一符，可安全轉成字母；
            avesta.org 用的蓋爾德納舊式羅馬轉寫（<span class="italic">ahurô mazdå</span>）以 sh／zh／kh／th／dh／gh／ng
            表 š／ž／x／θ／δ／γ／ŋ，在「ŋ 還是 n＋g」這類位置上需要語音學判斷才拆得開。
            機器硬轉會拼錯——而錯了以後畫面仍是一串漂亮的阿維斯陀字，沒有人看得出來。
            所以本站只對霍夫曼式轉寫開放字母切換，舊式一律不轉。
          </p>
        </div>
        <details class="bg-white border border-gray-200 rounded-xl overflow-hidden">
          <summary class="px-4 py-2.5 text-sm font-medium text-gray-800 cursor-pointer hover:bg-slate-50">
            字母對照表（{{ alphabet.length }} 字）
          </summary>
          <div class="px-4 py-3 border-t border-gray-100 grid grid-cols-3 sm:grid-cols-5 gap-x-3 gap-y-1.5">
            <div v-for="row in alphabet" :key="row.code" class="flex items-baseline gap-1.5 min-w-0">
              <span class="text-lg shrink-0">{{ row.glyph }}</span>
              <span class="text-xs text-gray-700 italic truncate">{{ row.translit }}</span>
              <span class="text-[10px] text-gray-300 font-mono truncate">{{ row.code }}</span>
            </div>
          </div>
        </details>
      </section>

      <section>
        <h2 class="text-base font-bold text-gray-900 mb-2 border-b border-orange-200 pb-1.5">六、段號與斷限</h2>
        <p class="text-sm text-gray-600 leading-relaxed break-words">
          <b class="text-gray-700">段號一律沿用經文自身的編號</b>（Y 28.1、Vd 3.24、Yt 10.4、Dk 8.44），
          不自編。轉寫依蓋爾德納校本分節、英譯依達梅斯特或米爾斯分節，兩者偶有出入；
          對不齊時各自入位、缺的一欄留空，<b class="text-gray-700">絕不按序號硬配對</b>——
          那會讓整章往下錯一格，而版面完全正常。蓋爾德納把數節合為一段時（如 Vd 12.3-4），
          該段涵蓋的英譯各節併入同一列，引用式亦標作區間。
        </p>
        <p class="text-sm text-gray-600 leading-relaxed break-words mt-2">
          <b class="text-gray-700">斷限</b>：{{ TERMINUS.from }} 起，{{ TERMINUS.to }}。{{ TERMINUS.note }}
        </p>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { CANONS, STATUS_META, TERMINUS } from '~/data/avesta'
import { avestanAlphabet } from '~/utils/avestanScript'

definePageMeta({ middleware: 'auth' })
useHead({ title: '編纂凡例 — 祆教經典' })

const alphabet = avestanAlphabet()
</script>
