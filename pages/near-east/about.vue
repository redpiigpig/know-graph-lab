<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader title="古近東大藏經 · 凡例" :back="{ to: '/near-east', label: '古近東大藏經' }" container-class="max-w-3xl" />

    <div class="flex-1 max-w-3xl w-full mx-auto px-4 sm:px-6 py-10 space-y-8">
      <section>
        <h1 class="text-2xl font-bold text-gray-900 mb-2">凡例</h1>
        <p class="text-sm text-gray-600 leading-relaxed">
          本藏經收錄古代近東諸文明的宗教文獻，分八藏：埃及、蘇美、阿卡德（巴比倫與亞述）、赫梯與胡里特、烏加里特、
          迦南與亞蘭、阿拉伯、埃蘭與高地；另有附錄收外人的記述。以下是編纂時實際遵守的規矩，也是引用時該知道的限制。
        </p>
      </section>

      <section>
        <h2 class="text-lg font-bold text-gray-900 mb-2">一、這不是一個宗教，是七八個</h2>
        <p class="text-sm text-gray-600 leading-relaxed mb-2">
          希臘羅馬大藏經替一個沒有正典的宗教補做正典；本藏經面對的是一群宗教。它們彼此借神、借文類、借書吏學校——
          巴比倫的吉爾伽美什在赫梯首都有三種語言的版本，迦南的海神神話以埃及文寫在紙草上——但各有自己的神廟體系與神譜。
        </p>
        <p class="text-sm text-gray-600 leading-relaxed">
          所以本藏經<b>不調和、不比附</b>，不把巴力、馬杜克、特舒布編成同一位「近東風暴神」，
          也不編一套「近東神話」綜合版。相似之處以互見標出，由讀者自己比較。
        </p>
      </section>

      <section>
        <h2 class="text-lg font-bold text-gray-900 mb-2">二、分藏：先看文字，再看神廟</h2>
        <p class="text-sm text-gray-600 leading-relaxed mb-3">
          古近東宗教的載體是書吏與神廟：會寫神名的人都在神廟或宮廷的書吏學校受訓。所以分藏的第一判準是寫經的文字與語言，
          最終判準是這份材料屬於哪一套神廟體系。兩者衝突時以後者為準：
        </p>
        <div class="overflow-x-auto">
          <table class="w-full text-xs text-gray-600 border border-gray-200 bg-white rounded-lg">
            <thead class="bg-gray-50 text-gray-700">
              <tr><th class="text-left px-3 py-2">材料</th><th class="text-left px-3 py-2">語言</th><th class="text-left px-3 py-2">歸藏</th><th class="text-left px-3 py-2">理由</th></tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="row in RULE_ROWS" :key="row[0]">
                <td class="px-3 py-1.5 break-words">{{ row[0] }}</td>
                <td class="px-3 py-1.5 break-words">{{ row[1] }}</td>
                <td class="px-3 py-1.5 break-words font-medium text-gray-800">{{ row[2] }}</td>
                <td class="px-3 py-1.5 break-words">{{ row[3] }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 class="text-lg font-bold text-gray-900 mb-2">三、每一藏止於它的文字死亡</h2>
        <p class="text-sm text-gray-600 leading-relaxed mb-3">
          古代宗教沒有「改宗的那一天」，只有最後一個會寫神名的書吏死去的那一天。本藏經因此不定統一的下限：
        </p>
        <ul class="space-y-1.5">
          <li v-for="c in CANONS" :key="c.key" class="text-xs text-gray-600 leading-relaxed break-words">
            <b class="text-gray-800">{{ c.name }}</b>（{{ c.era }}）：{{ c.terminus }}
          </li>
        </ul>
      </section>

      <section>
        <h2 class="text-lg font-bold text-gray-900 mb-2">四、泥板不是書：綴合本與兩個年代</h2>
        <p class="text-sm text-gray-600 leading-relaxed mb-2">
          「吉爾伽美什史詩」不是一部古人手上拿得到的書，是現代學者從兩千年間幾百塊泥板綴合出來的學術物件，至今仍有約五分之一缺文。
          所以存世狀態分六級，其中<b>綴合本</b>是古近東大型文學作品的常態：
        </p>
        <dl class="space-y-1.5 mb-3">
          <div v-for="(m, k) in STATUS_META" :key="k" class="flex items-start gap-3">
            <dt class="shrink-0 flex items-center gap-1.5 w-20 text-xs" :class="m.titleCls">
              <span class="inline-block w-2.5 h-2.5 rounded-full" :class="m.dotCls" />{{ m.zh }}
            </dt>
            <dd class="min-w-0 flex-1 text-xs text-gray-600 leading-relaxed break-words">{{ m.desc }}</dd>
          </div>
        </dl>
        <p class="text-sm text-gray-600 leading-relaxed">
          每一條也分兩個年代：<b>成書</b>與<b>抄本</b>。蘇美文學多半成書於烏爾第三王朝，現存抄本卻幾乎全是兩三百年後
          古巴比倫書吏學校的習作——那時蘇美語早已不在街上說了。兩個年代混成一個，會讓人以為我們讀的是原件。
        </p>
      </section>

      <section>
        <h2 class="text-lg font-bold text-gray-900 mb-2">五、編號只用學界標準，查不到就留空</h2>
        <p class="text-sm text-gray-600 leading-relaxed mb-2">
          蘇美用牛津 ETCSL 分類號，赫梯用 CTH，烏加里特用 KTU，腓尼基與亞蘭銘文用 KAI，紙草與泥板用館藏號，
          新亞述文獻用 SAA，巴比倫智慧文學用 Lambert 的 BWL 頁碼。ETCSL 與 CTH 兩套已逐條對過線上目錄。
        </p>
        <p class="text-sm text-gray-600 leading-relaxed">
          <b>本站不自編編號。</b>卷頁左側的數字只是版面上的序號，方便定位，不能拿來引用。
          自編的號碼會讓一條書目無法被外部查證，而版面看起來完全正常。
        </p>
      </section>

      <section>
        <h2 class="text-lg font-bold text-gray-900 mb-2">六、聖經對位只是互見</h2>
        <p class="text-sm text-gray-600 leading-relaxed mb-2">
          許多條目標了「聖經對位」：阿蒙尼摩普訓言與箴言二十二至二十四章、阿頓大頌與詩篇一百零四篇、米沙碑與列王紀下三章。
          這是方便讀者比較，<b>不是收錄或排序的理由</b>。本藏經不把這些文本當作「聖經的背景」——
          它們是各自宗教的經典，有自己的讀者與用途。
        </p>
        <p class="text-sm text-gray-600 leading-relaxed">
          希伯來聖經本身屬猶太教（規劃中），不入本藏經。以色列與猶大出土的<b>銘文</b>則收在迦南與亞蘭藏：
          它們是未經正典篩選的當時實物，顯示先知所譴責的那種宗教確實存在過。兩者互見，不合併。
        </p>
      </section>

      <section>
        <h2 class="text-lg font-bold text-gray-900 mb-2">七、與站上其他典藏的分工</h2>
        <ul class="space-y-1.5 text-xs text-gray-600 leading-relaxed">
          <li class="break-words"><b class="text-gray-800">祆教經典</b>：波斯宗教一律歸那邊。阿契美尼德王室銘文、波斯波利斯泥板的祭祀記錄以互見相連。</li>
          <li class="break-words"><b class="text-gray-800">希臘羅馬大藏經</b>：普魯塔克《論伊西斯與奧西里斯》、琉善《論敘利亞女神》等在那邊是本經，在本藏經的附錄是外部證詞；同一部書在兩座圖書館各有位置。</li>
          <li class="break-words"><b class="text-gray-800">基督教大藏經‧前藏</b>：已收埃努瑪‧埃利什、吉爾伽美什、亡靈書等，定位是「前基督教啟示母體」。本藏經不動那邊的資料，以互見相連。</li>
          <li class="break-words"><b class="text-gray-800">摩尼教經典</b>：阿爾—納迪姆《群書類述》兩邊都用到。</li>
        </ul>
      </section>

      <section>
        <h2 class="text-lg font-bold text-gray-900 mb-2">八、譯名</h2>
        <p class="text-sm text-gray-600 leading-relaxed">
          人名、地名、神名先過站上的翻譯定名詞庫。古近東語境一律用一般學界譯名，不用聖經譯名：
          烏爾（非吾珥）、埃蘭（非以攔）、蘇薩（非書珊）、杜牧茲（非搭模斯）；赫梯取其能銜接聖經的「赫人」。
          音譯從短，省去只在譯子音尾的輕聲字：馬杜克（非馬爾杜克）；但需要區別同名時保留，亞述的主神作亞述爾，以別於國名亞述。
        </p>
      </section>

      <section>
        <h2 class="text-lg font-bold text-gray-900 mb-2">九、現況</h2>
        <p class="text-sm text-gray-600 leading-relaxed">
          目前完成的是<b>書目</b>：{{ CANONS.length }} 藏、{{ totalVolumes }} 卷、{{ allTexts().length }} 種，逐條標存世狀態、編號、年代、出土地與聖經對位。
          原文、英譯、繁中三欄逐段對照尚未上架；每一條的三欄色塊說的是「線上找不找得到可用來源」，不是「本站已經有了」。
        </p>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { CANONS, STATUS_META, allTexts } from '~/data/near-east'

definePageMeta({ middleware: 'auth' })
useHead({ title: '凡例 — 古近東大藏經' })

const totalVolumes = CANONS.reduce((n, c) => n + c.volumes.length, 0)

const RULE_ROWS: Array<[string, string, string, string]> = [
  ['恩赫杜安娜《神廟頌集》', '蘇美語', '蘇美藏', '作者是阿卡德王薩爾貢之女，但作品以蘇美語寫成'],
  ['盧伽—埃、烏都格惡魔咒', '蘇美語（附阿卡德語對譯）', '蘇美藏', '阿卡德語欄是後加的行間譯文'],
  ['庫瑪比組詩', '赫梯語譯本（胡里特原作）', '赫梯與胡里特藏', '出土於哈圖沙，屬赫梯國家所保存的胡里特神話'],
  ['胡里特尼卡讚歌', '胡里特語', '赫梯與胡里特藏', '出土於烏加里特，但屬胡里特宗教系統；烏加里特藏互見'],
  ['烏加里特三語神表', '烏加里特語、阿卡德語', '烏加里特藏', '阿卡德語本記的是烏加里特本地萬神殿'],
  ['阿斯塔特與海', '新埃及語', '埃及藏', '迦南神話在埃及的埃及文本，烏加里特藏互見'],
  ['卡拉特佩雙語銘文', '腓尼基語—盧維語', '赫梯與胡里特藏', '新赫梯邦國的王銘，腓尼基語是外交語言'],
  ['居魯士圓柱', '阿卡德語', '阿卡德藏', '寫的是馬杜克揀選居魯士，屬巴比倫宗教；祆教經典互見'],
  ['貝羅索斯、曼涅托', '古希臘文', '附錄', '作者是本地祭司，但以希臘文為希臘讀者而寫，原書已佚'],
]
</script>
