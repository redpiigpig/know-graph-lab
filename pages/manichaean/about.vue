<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader title="摩尼教經典 · 凡例" :back="{ to: '/manichaean', label: '摩尼教經典' }" container-class="max-w-3xl" />

    <div class="flex-1 max-w-3xl w-full mx-auto px-6 py-10 space-y-8">
      <section>
        <h1 class="text-2xl font-bold text-gray-900 mb-2">凡例</h1>
        <p class="text-sm text-gray-600 leading-relaxed">
          本區收錄摩尼教現存的全部傳世文獻，分五藏：摩尼親撰的正典書目（正藏）、埃及與北非出土的
          科普特文與希臘文抄本、吐魯番出土的中古伊朗語與回鶻語寫本、敦煌與福建的漢文文獻，
          以及反對者所記（附錄，非經典）。以下是編纂時實際遵守的規矩，也是引用本區內容時該知道的限制。
        </p>
      </section>

      <section>
        <h2 class="text-lg font-bold text-gray-900 mb-2">一、為什麼正藏幾乎整個是空的</h2>
        <p class="text-sm text-gray-600 leading-relaxed mb-2">
          摩尼是宗教史上第一個親手寫下並封定正典的創教者。他在《凱法萊亞》裡明說：瑣羅亞斯德、佛陀與耶穌
          都沒有親筆寫下自己的教導，所以他們的教會在他們死後都走樣了，而他的不會。
          <b>結果恰好相反——他親撰的七部大經，今天沒有一部傳世。</b>
        </p>
        <p class="text-sm text-gray-600 leading-relaxed">
          本站仍照那份書目立卷，即使卷是空的。不列等於接受一個由勝利者寫下的假象，
          彷彿摩尼教本來就沒有正典、只是一堆異端囈語。每一卷底下列出的，是這部書今日僅存的痕跡：
          別的語言的殘葉、敵手的引文，或者只是一個書名。<b>空著要看得出來是空的</b>，
          所以存世狀態分「殘篇／佚存引文／佚存目」三級，一眼可辨。
        </p>
      </section>

      <section>
        <h2 class="text-lg font-bold text-gray-900 mb-2">二、續藏為什麼按語言分，不按主題分</h2>
        <p class="text-sm text-gray-600 leading-relaxed">
          摩尼教文獻的存世形態本來就是語言群。一部《巨人書》在科普特文、帕提亞語、回鶻文與漢文裡，
          是四份殘缺程度完全不同的殘卷，各自出土於不同的地方、被不同的人讀過。
          硬併成一條會抹掉「哪一群人在哪裡讀到什麼」這個最要緊的事實。
          所以本站按<b>出土語言與地點</b>立卷，同一部書的不同殘卷以「互見」相連——
          這裡的互見不是「參看」，而是「這是同一本書的另一塊碎片」。
        </p>
      </section>

      <section>
        <h2 class="text-lg font-bold text-gray-900 mb-2">三、敵證的三級，以及為什麼一定要分</h2>
        <p class="text-sm text-gray-600 leading-relaxed mb-3">
          第五藏裡沒有一個字是摩尼教徒寫的。收它有兩個理由：1904 年吐魯番殘卷出土之前，
          全世界對摩尼教的認識百分之百來自這一批；而且摩尼親撰七經今日僅存的若干段落，
          就夾在這些駁論的引文裡。但這批材料的可用程度差別極大，故分三級：
        </p>
        <dl class="space-y-2">
          <div v-for="(m, k) in HOSTILE_META" :key="k" class="flex items-start gap-3">
            <dt class="shrink-0 text-[11px] px-2 py-0.5 rounded" :class="m.cls">{{ m.zh }}</dt>
            <dd class="min-w-0 flex-1 text-xs text-gray-600 leading-relaxed break-words">{{ m.desc }}</dd>
          </div>
        </dl>
        <p class="text-sm text-gray-600 leading-relaxed mt-3">
          這個分級不是學術潔癖。奧古斯丁逐句抄錄《基要書信》再駁，那些抄錄句可以當摩尼的原話用；
          但他轉述教義時已經隔了一層敵意的選擇，而《阿基勞斯行傳》整本是一場虛構的辯論，
          連摩尼的出身都是編的。三者混用，就會寫出把敵人的嘲諷當教義引的論文。
        </p>
      </section>

      <section>
        <h2 class="text-lg font-bold text-gray-900 mb-2">四、段號照抄，不自編</h2>
        <p class="text-sm text-gray-600 leading-relaxed">
          摩尼教沒有統一的引用式——原書的章節結構早就隨著殘片斷了。學界的引用方式依材料而異：
          科普特抄本用抄本頁行號（<code class="text-[11px] bg-gray-100 px-1 rounded">1 Ke 89.18–24</code>）、
          吐魯番殘卷用館藏編號＋葉面＋行（<code class="text-[11px] bg-gray-100 px-1 rounded">M 470 R/ii/1–8</code>）、
          漢文寫卷用《大正藏》冊頁欄行（<code class="text-[11px] bg-gray-100 px-1 rounded">T54, 1270b12</code>）。
          <b>本站一律照抄，一個字都不自己發明。</b>自編段號會讓這裡的每一段都無法被外部引用，
          而版面看起來完全正常——那正是最難發現的一類錯。
        </p>
      </section>

      <section>
        <h2 class="text-lg font-bold text-gray-900 mb-2">五、漢文藏只出一欄</h2>
        <p class="text-sm text-gray-600 leading-relaxed">
          其餘各藏是「原文轉寫／英譯／繁中」三欄對照。漢文藏不是——那些文獻本來就是漢文寫的。
          正文原樣呈現，<b>不另譯成現代中文</b>（那不是對照，是改寫），需要幫助的地方以註解處理。
        </p>
      </section>

      <section>
        <h2 class="text-lg font-bold text-gray-900 mb-2">六、取源</h2>
        <p class="text-sm text-gray-600 leading-relaxed mb-3">
          三欄的取源狀態標的是「線上找不找得到可用來源」，<b>不是</b>「本站已經有了」。
          這是本區維護得最嚴格的一張表。摩尼教文獻的取源條件兩極：
        </p>
        <ul class="space-y-2 text-sm text-gray-600">
          <li class="flex gap-2">
            <span class="shrink-0 text-emerald-700">好</span>
            <span class="min-w-0 leading-relaxed break-words">
              <b>吐魯番各語言</b>——國際摩尼教研究學會（IAMS）開放取用的《東方摩尼教選輯》四冊
              （生平與教史／正典／沙卜爾干／讚詩與祈禱），原文轉寫與英譯逐行並排刊出，可直接取用。
              另有斯克耶爾沃《摩尼教文獻譯注》。
            </span>
          </li>
          <li class="flex gap-2">
            <span class="shrink-0 text-emerald-700">好</span>
            <span class="min-w-0 leading-relaxed break-words">
              <b>漢文三經</b>——《大正藏》第 54 冊（T2140《下部讚》、T2141A《儀略》、T2141B《殘經》），
              公有領域，維基文庫另有錄文。本站 /tripitaka 已有大正藏全文。
            </span>
          </li>
          <li class="flex gap-2">
            <span class="shrink-0 text-emerald-700">好</span>
            <span class="min-w-0 leading-relaxed break-words">
              <b>教父駁論</b>——奧古斯丁反摩尼教六種見《尼西亞前後期教父集》第一系列第四卷、
              《阿基勞斯行傳》見《尼西亞前教父集》第六卷、艾弗冷《駁謬論》有米契爾英譯、
              比魯尼《古代遺跡》有薩豪英譯，全部公有領域。本站 /fathers 已收 ANF／NPNF 全套。
            </span>
          </li>
          <li class="flex gap-2">
            <span class="shrink-0 text-amber-700">難</span>
            <span class="min-w-0 leading-relaxed break-words">
              <b>科普特文抄本</b>——校本與英譯幾乎全在版權內（波洛茨基、奧爾伯里、加德納諸家）。
              本站 /gnostic 另收有 gnosis.org 的英譯選段 75 篇並附繁中，但那是選本，
              沒有抄本編號與卷次結構，與本區分工不同，以互見相連，不重複翻譯。
            </span>
          </li>
          <li class="flex gap-2">
            <span class="shrink-0 text-amber-700">難</span>
            <span class="min-w-0 leading-relaxed break-words">
              <b>霞浦文書</b>——2008 年才發現，仍在整理刊布，校錄本多在版權內。
            </span>
          </li>
        </ul>
      </section>

      <section>
        <h2 class="text-lg font-bold text-gray-900 mb-2">七、與本站其他區的分工</h2>
        <ul class="space-y-1.5 text-sm text-gray-600">
          <li class="leading-relaxed break-words">
            <NuxtLink to="/research-data/sanyijiao" class="text-amber-800 hover:underline">/research-data/sanyijiao</NuxtLink>
            —— 三夷教（祆教／摩尼教／景教）的<b>二手研究</b>書目。那邊收研究，這邊收原典。
          </li>
          <li class="leading-relaxed break-words">
            <NuxtLink to="/gnostic" class="text-amber-800 hover:underline">/gnostic</NuxtLink>
            —— gnosis.org 的諾斯底文獻選本，其中「摩尼教文獻」一類 75 篇已有英中對照。以互見相連。
          </li>
          <li class="leading-relaxed break-words">
            <NuxtLink to="/fathers" class="text-amber-800 hover:underline">/fathers</NuxtLink>
            —— 教父著作全文。第五藏的奧古斯丁諸書與《阿基勞斯行傳》在那邊有完整譯本。
          </li>
          <li class="leading-relaxed break-words">
            <NuxtLink to="/dazangjing" class="text-amber-800 hover:underline">/dazangjing</NuxtLink>
            —— 基督教大藏經。摩尼教文獻在該藏以「外典」身分分類收錄（諾斯底與摩尼教部），
            那是分類目錄；本區是可讀的逐段對照，兩者性質不同。
          </li>
          <li class="leading-relaxed break-words">
            <NuxtLink to="/avesta" class="text-amber-800 hover:underline">/avesta</NuxtLink>
            —— 祆教經典。與本區為姊妹結構，但體例相反：祆教的正典還活著，照抄禮儀單位；
            摩尼教的正典死透了，照書目立卷。
          </li>
        </ul>
      </section>

      <section class="border-t border-gray-200 pt-6">
        <h2 class="text-lg font-bold text-gray-900 mb-2">八、斷限</h2>
        <p class="text-sm text-gray-600 leading-relaxed">
          <b>{{ TERMINUS.from }}</b> 起，止於 <b>{{ TERMINUS.to }}</b>。{{ TERMINUS.note }}
        </p>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { HOSTILE_META, TERMINUS } from '~/data/manichaean'

definePageMeta({ middleware: 'auth' })
useHead({ title: '凡例 — 摩尼教經典' })
</script>
