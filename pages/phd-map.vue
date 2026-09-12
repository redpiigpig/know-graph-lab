<template>
  <div class="min-h-screen bg-slate-50">
    <AppHeader title="博班修業地圖" :back="{ to: '/', label: '返回主頁' }" container-class="max-w-4xl" />

    <div class="max-w-4xl mx-auto px-4 sm:px-6 py-8 sm:py-12">

      <!-- 抬頭 -->
      <header class="mb-8 pb-6 border-b-2 border-red-800/70">
        <p class="text-[11px] font-semibold tracking-[0.2em] text-red-800 mb-1.5">
          玄奘大學宗教與文化學系博士班　115 級
        </p>
        <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 leading-tight mb-1.5">博班修業地圖</h1>
        <p class="text-sm text-gray-500">以三年畢業為規劃　·　整理於 2026-09-12</p>
      </header>

      <!-- 基本資料 -->
      <dl class="mb-10 rounded-xl border border-gray-200 bg-white overflow-hidden divide-y divide-gray-100">
        <div v-for="row in identity" :key="row.k" class="grid grid-cols-1 sm:grid-cols-[6rem_1fr] gap-0.5 sm:gap-3 px-4 py-2.5">
          <dt class="text-[11px] tracking-wide text-gray-400 sm:pt-0.5">{{ row.k }}</dt>
          <dd class="text-sm text-gray-800 min-w-0 break-words" v-html="row.v" />
        </div>
      </dl>

      <!-- 目錄 -->
      <nav class="sticky top-0 z-20 -mx-4 sm:-mx-6 px-4 sm:px-6 py-2 mb-10 bg-slate-50/90 backdrop-blur border-b border-gray-200">
        <ul class="flex gap-1.5 overflow-x-auto no-scrollbar">
          <li v-for="s in sections" :key="s.id" class="flex-shrink-0">
            <a :href="`#${s.id}`"
               class="block text-xs text-gray-500 hover:text-red-800 border border-gray-200 hover:border-red-800 rounded px-2.5 py-1 no-underline whitespace-nowrap">
              {{ s.nav }}
            </a>
          </li>
        </ul>
      </nav>

      <!-- 壹 畢業六關 -->
      <section id="gates" class="mb-12 scroll-mt-16">
        <SectionHeading num="壹" title="畢業六關"
          lede="系《博士班修業辦法》第一條所列，取得學位須全數完成。" />
        <ol class="border-t border-gray-200">
          <li v-for="g in gates" :key="g.n"
              class="grid grid-cols-[2rem_1fr_auto] gap-x-3 gap-y-0.5 py-3 border-b border-gray-100">
            <span class="row-span-2 text-xs text-gray-400 tabular-nums pt-0.5">{{ g.n }}</span>
            <span class="text-sm font-semibold text-gray-900">{{ g.t }}</span>
            <span :class="['self-start text-[11px] px-2 py-0.5 rounded-full border whitespace-nowrap tabular-nums', pillClass(g.s)]">
              {{ g.p }}
            </span>
            <span class="col-start-2 text-xs text-gray-500 leading-relaxed break-words">{{ g.d }}</span>
          </li>
        </ol>
        <p class="mt-3 text-xs text-gray-500 leading-relaxed">
          另有兩項不在第一條、但同樣卡畢業：<b>學術活動場次</b>（第五條）與<b>學術研究倫理教育課程</b>（AREE 六小時，線上修習；未檢附修課證明不得申請學位口試。校《學術研究倫理教育課程實施要點》第二點規定<b>以入學第一學年結束前完成為原則</b>，即 115 學年度結束前）。
        </p>
      </section>

      <!-- 貳 三年時程 -->
      <section id="timeline" class="mb-12 scroll-mt-16">
        <SectionHeading num="貳" title="三年時程"
          lede="必修排到博二上 → 學分在博二下修滿 → 博三上資格考與計畫口試 → 博三下論文口試。" />
        <ol class="mt-4">
          <li v-for="(t, i) in timeline" :key="t.term"
              :class="['relative pl-6 pb-6', i === timeline.length - 1 ? '' : 'border-l border-gray-200']">
            <span :class="['absolute -left-[4.5px] top-2 w-2 h-2 rounded-full border-[1.5px]',
                           t.now ? 'bg-red-800 border-red-800' : 'bg-slate-50 border-gray-300']" />
            <div class="flex flex-wrap items-baseline gap-x-2.5 gap-y-1">
              <span class="font-mono text-sm font-bold text-gray-900 tracking-wide">{{ t.term }}</span>
              <span class="text-sm font-semibold text-gray-700">{{ t.who }}</span>
              <span v-if="t.now" class="text-[10px] tracking-widest text-red-800 border border-red-800 rounded px-1.5">現在</span>
              <span class="text-[11px] text-gray-400 sm:ml-auto">{{ t.when }}</span>
            </div>
            <ul class="mt-2 pl-4 list-disc marker:text-gray-300 space-y-1">
              <li v-for="(it, j) in t.items" :key="j" class="text-[13px] text-gray-700 leading-relaxed break-words" v-html="it" />
            </ul>
            <p class="mt-2.5 pl-2.5 border-l-2 border-gray-200 text-xs text-gray-500 leading-relaxed" v-html="t.tally" />
          </li>
        </ol>
        <div class="mt-2 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3.5">
          <h3 class="text-sm font-bold text-amber-800 mb-1">兩年半那條路：取決於兩個認定</h3>
          <p class="text-xs text-amber-900/85 leading-relaxed">
            若補修不佔修習額度、且希伯來文校際選課學分獲採計，116-1 結束時累計可達 25 學分 —— 資格考就能提前到 116-2 的四月中旬，論文口試落在 117-1，2/20 前離校，兩年半畢業。兩個認定任一不成立，就回到三年那條路。
          </p>
        </div>
      </section>

      <!-- 參 學分規則 -->
      <section id="credits" class="mb-12 scroll-mt-16">
        <SectionHeading num="參" title="學分規則" />

        <h3 class="sub-h">24 學分的組成</h3>
        <div class="tbl-wrap">
          <table class="tbl">
            <thead><tr><th>類別</th><th class="whitespace-nowrap">學分</th><th>內容</th></tr></thead>
            <tbody>
              <tr>
                <td class="whitespace-nowrap">專業必修</td><td class="tabular-nums">9</td>
                <td><code>BBJ001</code> 宗教研究基本問題與研究方法 3（一上）<br>
                    <code>BBJ002</code> 全球化與在地化宗教專題研討 3（一下）<br>
                    <code>BBJ003</code> 亞洲宗教比較研究 3（二上）</td>
              </tr>
              <tr>
                <td class="whitespace-nowrap">專業選修</td><td class="tabular-nums">15</td>
                <td>系上每學期兩個年級合計開出約 15 學分，可跨年級選修</td>
              </tr>
              <tr>
                <td class="whitespace-nowrap">補修</td><td class="tabular-nums">0</td>
                <td>宗教學理論與方法（一）（二）各 2 學分。非宗教相關系所碩士畢業者須補修，<b>不計入畢業學分，但佔當學期修習額度</b></td>
              </tr>
            </tbody>
          </table>
        </div>

        <h3 class="sub-h">每學期修習上限</h3>
        <blockquote class="my-3 pl-3.5 border-l-2 border-red-800 text-[13px] text-gray-600 leading-relaxed">
          研究生每學期所修研究所課程不得少於二學分，博士班最多以九學分為原則。
          <cite class="block mt-1 not-italic text-[11px] text-gray-400">— 校《學生選課辦法》第四條第二款</cite>
        </blockquote>
        <ul class="bullets">
          <li>算的是「<b>研究所課程</b>」總量，博班與碩班課一起算。<b>旁聽不佔額度，也不計學分。</b></li>
          <li>校際選課依《校際選課實施辦法》第五條第五款「比照本校學則及選課須知辦理」，條文上併入計算。</li>
          <li><b>超修</b>：前學期平均 90 分以上，或名次在該系班前 20% 以內，得超修 1–3 門（第五條第二款）。博一上沒有前學期成績，最快 115-2 起適用。</li>
        </ul>

        <h3 class="sub-h">抵免與校際選課</h3>
        <ul class="bullets">
          <li><b>抵免</b>：限過去<b>五年內</b>、<b>未曾計入任何學位</b>之<b>博士班課程</b>學分，由系主任與導師決定，最多 6 學分，<b>不含必修</b>，申請須於<b>入學第一學期開學前</b>完成（系辦法第二條第二款）。校《抵免辦法》第四條第二款另限「以本校開設之研究所學分班及修習研究所課程者為限」。<span class="text-gray-400">→ 已無可用空間。</span></li>
          <li><b>校際選課</b>：學分由<b>系主任與指導教授認可</b>後始得採計為畢業學分（系辦法第二條第三款）。須在學校公告期間內申請、以本校當學期未開設之科目為限、經系主任同意、且不得與校內課程衝堂（含往返時間）。</li>
        </ul>
      </section>

      <!-- 肆 語言要求 -->
      <section id="lang" class="mb-12 scroll-mt-16">
        <SectionHeading num="肆" title="語言要求"
          lede="系《博士班修業辦法》第三條。兩關都只規定「學位論文口試之前」完成 —— 不綁學期，也不綁學分。" />

        <h3 class="sub-h">第一關　中文或英文檢定</h3>
        <p class="para">凡未曾在以英語為唯一教學語言之高等教育體制下完成學士或碩士學位者皆須通過。符合下列任一項可抵免專業英語檢定考試：</p>
        <ol class="bullets list-decimal">
          <li>通過全民英檢（GEPT）中高級初試（含）以上，或 CEFR B2 以上英語檢定</li>
          <li><b>下修碩士班兩門「宗教學英文文獻選讀」</b>且及格 —— <code>BBA222</code> 初階（上學期）＋ <code>BBA223</code> 進階（下學期），倪杰老師 114 學年已連開過兩學期</li>
          <li>曾於英語系國家取得教育部認定之大學修習，取得 2 學分以上證明</li>
        </ol>

        <h3 class="sub-h">第二關　研究語言（中文與英文除外）</h3>
        <p class="para">完成一門與研究方向相關之研究語言，三選一：</p>
        <ol class="bullets list-decimal">
          <li>修畢本系或他系所開設之<b>同一語言連續兩學期</b>課程且成績及格</li>
          <li>通過相當於 <b>CEFR B1</b> 等級之語言檢定</li>
          <li>經<b>指導教授認定</b>其他語言能力或研究方法能力對該生研究更為必要，檢具書面說明，經<b>系主任核准</b>後替代之</li>
        </ol>

        <div class="mt-4 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3.5">
          <h3 class="text-sm font-bold text-emerald-800 mb-1.5">現行方案：走希伯來文</h3>
          <ul class="bullets !my-0 text-emerald-900/85">
            <li>希伯來文 I 已於 2026/8/3–8/27 在台神修畢（暑期密集）。</li>
            <li>希伯來文 II 自 9/16 起，<b>辦理校際選課</b>取得玄奘認可的成績紀錄（申請期限 9/7–9/18）。</li>
            <li>初階日文改為<b>旁聽</b>，不計學分、不佔額度，亦不再作為語言認定用途。</li>
          </ul>
          <p class="mt-2 text-xs text-emerald-900/75 leading-relaxed">
            風險：希伯來文 I 修於入學前且未辦校際選課，系辦法第一條「在此期間」可能將其排除，則湊不成「連續兩學期」。退路是走第三款，由昭慧法師以指導教授身分認定、再以系主任身分核准。
          </p>
        </div>
        <p class="mt-3 text-xs text-gray-400 leading-relaxed">
          系上博班科目表列的梵文／巴利語／藏文佛典導讀三門，114–115 兩學年一門都沒開；碩班基礎梵文僅 114-2 開過一次、無進階，湊不出連續兩學期。
        </p>
      </section>

      <!-- 伍 資格考 -->
      <section id="quals" class="mb-12 scroll-mt-16">
        <SectionHeading num="伍" title="資格考" />
        <div class="tbl-wrap">
          <table class="tbl">
            <tbody>
              <tr v-for="r in quals" :key="r.k">
                <th class="w-20 sm:w-24 bg-gray-50 font-normal text-gray-500 text-xs whitespace-nowrap align-top">{{ r.k }}</th>
                <td v-html="r.v" />
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- 陸 計畫口試 -->
      <section id="proposal" class="mb-12 scroll-mt-16">
        <SectionHeading num="陸" title="論文計畫口試"
          lede="系《博士班修業辦法》第六條。獨立一關，不是資格考的一部分。" />
        <ul class="bullets">
          <li>指導教授至少須有一位<b>現任專職教師</b>擔任 —— 昭慧法師滿足此款。</li>
          <li>須具<b>博士候選人</b>身分才能擬定計畫書，故順序上在資格考之後。</li>
          <li>計畫書<b>一萬字以上</b>，應含寫作動機、問題意識、文獻回顧、理論運用、研究方法、架構與章節安排、預定進度、參考書目。</li>
          <li>以<b>口試</b>審查。指導教授邀請 <b>3–5 位</b>專家學者組成委員會，<b>校外至少三分之一</b>。</li>
          <li>70 分及格，以出席委員評定分數平均決定；但<b>二分之一以上委員評不及格者，以不及格論</b>。</li>
          <li><b>審查通過後一學期，始得提學位論文口試。</b><span class="text-gray-400">這一條是整條時程的節奏器。</span></li>
        </ul>
      </section>

      <!-- 柒 論文口試 -->
      <section id="defense" class="mb-12 scroll-mt-16">
        <SectionHeading num="柒" title="論文口試與離校" />
        <ul class="bullets">
          <li><b>前置</b>：校內論文抄襲比對、AREE 六小時修課證明、指導教授同意，三者齊備才能提申請。</li>
          <li><b>申請窗口</b>：該學期註冊完成後至當學期休學截止日之間，隨時可提；須於學期結束日前完成口試。</li>
          <li><b>口試窗口</b>：第 1 學期 8/1 – 1/31；第 2 學期 2/1 – 7/31。當學期須完成註冊。</li>
          <li><b>委員會</b>：指導教授外另聘 <b>4–8 位</b>口試委員，校外至少三分之一。未具副教授以上資格者須系主任同意並簽請校方核可。</li>
          <li><b>成績</b>：70 分及格；二分之一以上委員評不及格即不及格，評定以一次為限。</li>
          <li><b>不及格</b>：至少隔一學期後、修業年限屆滿前得申請重考，一次為限。</li>
          <li><b>繳交離校</b>：第 1 學期 2/20、第 2 學期 8/31（遇假日順延次工作日）。逾期而未達修業年限者撤銷及格成績；修業年限屆滿仍未繳交者視為未通過畢業條件，應予退學。</li>
        </ul>
      </section>

      <!-- 捌 學術活動 -->
      <section id="activity" class="mb-12 scroll-mt-16">
        <SectionHeading num="捌" title="學術活動與論文發表" />
        <div class="rounded-xl border border-red-200 bg-red-50 px-4 py-4">
          <h3 class="text-sm font-bold text-red-800 mb-2">兩份文件的場次規定不一致</h3>
          <div class="tbl-wrap !bg-white">
            <table class="tbl">
              <thead><tr><th>項目</th><th>115 級修業規定</th><th>系辦法第五條</th></tr></thead>
              <tbody>
                <tr><td class="whitespace-nowrap">審稿論文</td><td>2 篇以上</td><td>2 篇以上</td></tr>
                <tr><td class="whitespace-nowrap">研討會</td><td>六<b>整天</b>（三場本系）</td><td>八<b>場</b>（三場本系）</td></tr>
                <tr><td class="whitespace-nowrap">演講</td><td>十場（五場本系）</td><td>二十場（五場本系）</td></tr>
              </tbody>
            </table>
          </div>
          <p class="mt-2.5 text-xs text-red-900/85 leading-relaxed">
            兩份都是 115 年 5 月 6 日第 84 次教務會議通過的，單位與數量卻不同。差距是十場演講，而演講只能一場一場累積 —— 愈晚確認愈難補。
          </p>
        </div>
      </section>

      <!-- 玖 研討會與演講紀錄 -->
      <section id="events" class="mb-12 scroll-mt-16">
        <SectionHeading num="玖" title="研討會與演講紀錄"
          lede="認列需取得主辦單位開立的參與證明；「本系舉辦」那幾場另計。" />

        <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5 mb-5">
          <div v-for="s in eventStats" :key="s.k" class="rounded-xl border border-gray-200 bg-white px-3 py-2.5">
            <div class="text-[11px] text-gray-400 mb-0.5">{{ s.k }}</div>
            <div class="text-lg font-bold text-gray-900 tabular-nums leading-none">{{ s.v }}</div>
            <div class="text-[10px] text-gray-400 mt-1">{{ s.note }}</div>
          </div>
        </div>

        <h3 class="sub-h">已參與</h3>
        <ol class="space-y-3">
          <li v-for="e in eventsDone" :key="e.name" class="rounded-xl border border-gray-200 bg-white px-4 py-3.5">
            <div class="flex flex-wrap items-baseline gap-x-2 gap-y-1 mb-1">
              <span class="font-mono text-xs font-bold text-gray-900 tabular-nums">{{ e.date }}</span>
              <span v-if="e.presented" class="text-[10px] font-semibold text-rose-700 bg-rose-50 border border-rose-200 rounded px-1.5">有發表</span>
              <span v-if="e.ownDept" class="text-[10px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 rounded px-1.5">本系主辦</span>
              <span class="text-[11px] text-gray-400 sm:ml-auto">{{ e.days }}</span>
            </div>
            <p class="text-[13px] font-semibold text-gray-900 leading-snug break-words">{{ e.name }}</p>
            <p v-if="e.place" class="mt-1 text-xs text-gray-500 break-words">{{ e.place }}</p>
            <p v-if="e.host" class="mt-0.5 text-xs text-gray-500 leading-relaxed break-words">
              <span class="text-gray-400">主辦　</span>{{ e.host }}
            </p>
            <a v-if="e.url" :href="e.url" target="_blank" rel="noopener"
               class="inline-block mt-1.5 text-xs text-red-800 hover:underline break-all">{{ e.url }}</a>
            <p v-if="e.cert" class="mt-1.5 text-xs text-emerald-700 break-words">✓ {{ e.cert }}</p>
            <p v-if="e.todo" class="mt-1 text-xs text-amber-700 break-words">⚠ {{ e.todo }}</p>
          </li>
        </ol>

        <h3 class="sub-h">預計參與</h3>
        <ol class="space-y-3">
          <li v-for="e in eventsPlanned" :key="e.name" class="rounded-xl border border-dashed border-gray-300 bg-white/60 px-4 py-3.5">
            <div class="flex flex-wrap items-baseline gap-x-2 gap-y-1 mb-1">
              <span class="font-mono text-xs font-bold text-gray-600 tabular-nums">{{ e.date }}</span>
              <span class="text-[11px] text-gray-400 sm:ml-auto">{{ e.days }}</span>
            </div>
            <p class="text-[13px] font-semibold text-gray-800 leading-snug break-words">{{ e.name }}</p>
            <p v-if="e.place" class="mt-1 text-xs text-gray-500 break-words">{{ e.place }}</p>
            <p v-if="e.host" class="mt-0.5 text-xs text-gray-500 break-words"><span class="text-gray-400">主辦　</span>{{ e.host }}</p>
            <a v-if="e.url" :href="e.url" target="_blank" rel="noopener"
               class="inline-block mt-1.5 text-xs text-red-800 hover:underline break-all">{{ e.url }}</a>
            <p v-if="e.todo" class="mt-1.5 text-xs text-amber-700 break-words">⚠ {{ e.todo }}</p>
          </li>
        </ol>

        <h3 class="sub-h">論文發表</h3>
        <div class="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3.5 mb-3">
          <h4 class="text-sm font-bold text-amber-800 mb-1">🚨 既有著作可能都不算</h4>
          <p class="text-xs text-amber-900/85 leading-relaxed">
            系辦法第五條的主詞是「本系博士生<b>在學期間</b>論文產出及學術活動之規定」。
            2026/8/28–29 印順學那一篇比開學日（9/7）早了十天，若嚴格照這四個字就不計。
            與希伯來文 I 卡在同一個字眼上，要一起問系辦。
            不過即使那一篇不算，10 月宗教學會年會與《玄奘佛學研究》兩篇也已達兩篇門檻。
          </p>
        </div>
        <div class="tbl-wrap">
          <table class="tbl">
            <thead><tr><th>發表</th><th>刊物／會議</th><th class="whitespace-nowrap">時間</th><th class="whitespace-nowrap">狀態</th><th class="whitespace-nowrap">計入門檻</th></tr></thead>
            <tbody>
              <tr v-for="pub in publications" :key="pub.title">
                <td class="break-words">{{ pub.title }}</td>
                <td class="text-gray-600 break-words">{{ pub.venue }}</td>
                <td class="text-gray-600 whitespace-nowrap">{{ pub.date }}</td>
                <td class="text-gray-600 whitespace-nowrap">{{ pub.state }}</td>
                <td :class="pub.inProgram ? 'text-emerald-700 font-semibold' : 'text-gray-400'">
                  {{ pub.inProgram ? '是' : '否' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <p class="text-xs text-gray-500 leading-relaxed">
          上表<b>只收博班期間</b>的發表。碩班時期的著作（期刊 3 篇、會議 11 篇、社論 3 篇）不列入畢業門檻，
          完整目錄見 <NuxtLink to="/papers" class="text-red-800 hover:underline">學術著作目錄</NuxtLink>。
        </p>

        <h3 class="sub-h">演講</h3>
        <div class="rounded-xl border border-gray-200 bg-white px-4 py-3.5">
          <p class="text-[13px] text-gray-700 leading-relaxed mb-2">
            門檻算的是<b>「參加」演講</b>（去聽），不是自己主講 —— 系辦法第五條第三款寫「至少參加二十場演講（每場 2 小時以上），其中需有五場為本系舉辦」。
          </p>
          <p class="text-[13px] text-gray-700 leading-relaxed mb-2">
            <b>目前尚無紀錄</b>，需要你提供已參加的場次（日期、講題、主講人、主辦單位、時數）才能建檔。
            本系場次請留意系網「最新消息」與助教轉知信。
          </p>
          <p class="text-xs text-gray-500 leading-relaxed">
            自己主講的演講另計，見 <NuxtLink to="/speech" class="text-red-800 hover:underline">演講紀錄</NuxtLink>
            （目前 1 場：2026/5/19〈台灣佛教具有「民主基因」嗎？〉，玄奘大學妙然樓 M401）。不列入此門檻。
          </p>
        </div>
      </section>

      <!-- 拾 投稿目標 -->
      <section id="journals" class="mb-12 scroll-mt-16">
        <SectionHeading num="拾" title="期刊投稿目標"
          lede="畢業門檻為兩篇以上具審稿制度之研討會或期刊論文。以下依與論文題目的相關度排序。" />

        <h3 class="sub-h">進行中</h3>
        <ul class="space-y-2.5 mb-5">
          <li v-for="j in journalsActive" :key="j.name" class="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3">
            <div class="flex flex-wrap items-baseline gap-x-2 gap-y-1">
              <span class="text-[13px] font-bold text-emerald-900">{{ j.name }}</span>
              <span class="text-[10px] font-semibold text-emerald-700 bg-white border border-emerald-200 rounded px-1.5">{{ j.status }}</span>
            </div>
            <p class="mt-1 text-xs text-emerald-900/80 leading-relaxed break-words">{{ j.note }}</p>
          </li>
        </ul>

        <h3 class="sub-h">候選名單</h3>
        <div class="tbl-wrap">
          <table class="tbl">
            <thead><tr><th>期刊</th><th>出版單位</th><th>相關度</th></tr></thead>
            <tbody>
              <tr v-for="j in journalsTargets" :key="j.name">
                <td class="font-semibold text-gray-900 break-words">{{ j.name }}</td>
                <td class="text-gray-600 break-words">{{ j.pub }}</td>
                <td class="text-gray-600 break-words">{{ j.fit }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p class="mt-2 text-xs text-gray-400 leading-relaxed">
          THCI 收錄狀態與各刊徵稿格式逐年變動，投稿前務必到該刊官網或華藝頁面重新查證。
        </p>
      </section>

      <!-- 拾壹 待確認 -->
      <section id="todo" class="mb-12 scroll-mt-16">
        <SectionHeading num="拾壹" title="待確認事項" />
        <div v-for="blk in todos" :key="blk.who" class="mb-4 rounded-xl border border-red-200 bg-red-50 px-4 py-4">
          <h3 class="text-sm font-bold text-red-800 mb-2">{{ blk.who }}</h3>
          <ol class="pl-5 list-decimal space-y-1.5 marker:text-red-800/50">
            <li v-for="(q, i) in blk.items" :key="i" class="text-[13px] text-red-900/90 leading-relaxed break-words" v-html="q" />
          </ol>
        </div>
      </section>

      <!-- 拾貳 法源 -->
      <section id="sources" class="mb-10 scroll-mt-16">
        <SectionHeading num="拾貳" title="法源出處" />
        <ul class="bullets">
          <li><b>系《宗教與文化學系博士班修業辦法》</b>（113.10.21 系務會議通過；115.4.13 修正；115.5.6 第 84 次教務會議通過）—— 未單獨公布，<b>全文夾在系網「本系課程 → 課程規劃 → 博士班 → 114／115 級博士班課程科目表、地圖」PDF 的後半段</b>。</li>
          <li>校《研究生學位考試辦法》（114.02.04 教育部核備）</li>
          <li>校《學生選課辦法》（114.4.30 第 80 次教務會議修正）</li>
          <li>校《學生抵免學分辦法》</li>
          <li>校《校際選課實施辦法》</li>
          <li>《玄奘大學 115 級日間學制博士班學生修業規定》（115.5.6 第 84 次教務會議）—— 教務處「各級別修業規定」頁</li>
        </ul>
      </section>

      <footer class="pt-4 border-t border-gray-200 text-xs text-gray-400 leading-relaxed">
        本文件依上述法規原文整理。第玖節的待確認事項在系辦或教務處回覆之前，不應據以行動；法規修訂時應重新核對。
      </footer>

    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
useHead({ title: '博班修業地圖' })

const identity = [
  { k: '姓名學號', v: '張辰瑋　<code>DB1153002</code>' },
  { k: '入學', v: '115 學年度第 1 學期（2026 秋）' },
  { k: '修業年限', v: '2 – 7 年' },
  { k: '指導教授', v: '釋昭慧（本系專任教授兼系主任）<br>鄭仰恩（濟南教會教育牧師，校外）' },
  { k: '論文題目', v: '從彼岸向此岸的轉向：台灣佛教與基督教公共性之宗教史比較研究（1920–2020）' },
]

const sections = [
  { id: 'gates', nav: '六關' },
  { id: 'timeline', nav: '三年時程' },
  { id: 'credits', nav: '學分' },
  { id: 'lang', nav: '語言' },
  { id: 'quals', nav: '資格考' },
  { id: 'proposal', nav: '計畫口試' },
  { id: 'defense', nav: '論文口試' },
  { id: 'activity', nav: '學術活動' },
  { id: 'events', nav: '研討會紀錄' },
  { id: 'journals', nav: '投稿目標' },
  { id: 'todo', nav: '待確認' },
  { id: 'sources', nav: '法源' },
]

const eventStats = [
  { k: '研討會日數', v: '5', note: '證明已備齊' },
  { k: '本系主辦', v: '2', note: '需 3 場' },
  { k: '演講場次', v: '0', note: '需 10 或 20' },
  { k: '審稿論文', v: '3', note: '門檻需 2 篇' },
]

const eventsDone = [
  {
    date: '2026/8/28–29',
    days: '2 天',
    presented: true,
    ownDept: true,
    name: '第二十四屆「印順導師思想之理論與實踐」國際學術會議——臺灣佛教組織永續治理',
    place: '慈濟臺中靜思堂（臺中市南屯區文心南路 113 號）',
    host: '佛教慈濟慈善基金會、玄奘大學臺灣佛教研究中心、玄奘大學宗教與文化學系、弘誓文教基金會（承辦：慈濟基金會；協辦：印證教育基金會、慈濟大學、玄奘文教基金會、嚴寬祜文教基金會）',
    url: 'https://infobackend.tzuchi-org.tw/index.php?view=article&id=4868',
    cert: '參與證明已開立（2 天）',
    todo: '本系為主辦單位之一，可認列「本系舉辦」。',
  },
  {
    date: '2026/9/3–4',
    days: '2 天',
    presented: false,
    ownDept: false,
    name: '臺灣藏傳佛教論壇（屆次待補）',
    place: '待補',
    host: '待查證 — 首屆（113.1.18–19）由玄奘大學藏傳佛教研究中心舉辦，與達賴喇嘛西藏宗教基金會合作',
    url: 'https://www.hcu.edu.tw/tbrc/',
    cert: '參與證明已開立（2 天）',
    todo: '官網查不到本屆公告，正式名稱與屆次待補。主辦是「藏傳佛教研究中心」而非本系，能否認列為「本系舉辦」要問系辦。',
  },
  {
    date: '2026/9/18',
    days: '1 天（會期 9/18–20）',
    presented: false,
    ownDept: true,
    name: '第三十七屆全國佛學論文聯合發表會',
    place: '玄奘大學圖書資訊大樓慈雲廳（新竹市香山區玄奘路 48 號）',
    host: '籌備處：玄奘大學宗教與文化學系',
    url: 'https://www.hcu.edu.tw/buddhism/buddhism/zh-tw/5D075C1C58314DF59F8D135D16C96486/B707A4FF0D684014AF742C1EE5DF935B',
    cert: '參與證明已開立（1 天）',
    todo: '本系為本屆籌備單位，可認列「本系舉辦」。',
  },
]

const eventsPlanned = [
  {
    date: '2026/10/23–24',
    days: '2 天',
    name: '台灣宗教學會 2026 年會「靈性運動、療癒與諮詢」學術研討會',
    place: '天主教輔仁大學濟時樓',
    host: '台灣宗教學會',
    url: 'https://sites.google.com/view/tjrsfortars/',
    todo: '本屆有發表論文。本系為台灣宗教學會團體會員，碩士班辦法明列其主辦研討會可認列，博班能否比照要問系辦。',
  },
  {
    date: '2027 年 8 月（待公布）',
    days: '2 天',
    name: '第二十五屆「印順導師思想之理論與實踐」國際學術會議',
    place: '待公布',
    host: '玄奘大學臺灣佛教研究中心、玄奘大學宗教與文化學系、慈濟慈善基金會、弘誓文教基金會',
    url: '',
    todo: '本系主辦系列，優先投稿。徵稿通常在前一年底至當年上半年公布。',
  },
  {
    date: '2027 年 9 月（待公布）',
    days: '1–3 天',
    name: '第三十八屆全國佛學論文聯合發表會',
    place: '輪流主辦，待公布',
    host: '全國佛學院所輪流主辦（本系為輪值單位之一）',
    url: 'https://sites.google.com/dila.edu.tw/conference/',
    todo: '若輪到本系主辦即可認列本系場次。',
  },
]

const publications = [
  { title: '（題目待補）', venue: '第二十四屆「印順導師思想之理論與實踐」國際學術會議', date: '2026/8/28–29', state: '已發表', inProgram: false },
  { title: '（題目待補）', venue: '台灣宗教學會 2026 年會「靈性運動、療癒與諮詢」', date: '2026/10/23–24', state: '預計發表', inProgram: true },
  { title: '信仰與學術的交互作用：近半世紀印順學與印順學派歷史發展回顧（1973–2023）', venue: '《玄奘佛學研究》', date: '2027 年該期', state: '已通過審查，確定刊登', inProgram: true },
]

const journalsActive = [
  {
    name: '《玄奘佛學研究》',
    status: '明年該期已確定刊登',
    note: '玄奘大學宗教與文化學系出版。本系刊物，為兩篇審稿論文門檻的第一篇。',
  },
  {
    name: '《法印學報》',
    status: '預計投稿',
    note: '已於第 14 期（2023）、第 15 期（2024）發表過兩篇印順學相關論文，題材與審稿流程都熟悉。',
  },
]

const journalsTargets = [
  { name: '《臺灣宗教研究》', pub: '台灣宗教學會', fit: '最對口 — 佛耶跨傳統比較與宗教公共性正是該刊守備範圍' },
  { name: '《華人宗教研究》', pub: '國立政治大學華人宗教研究中心', fit: '華人社會的宗教與公共領域，適合第五章的議題結盟材料' },
  { name: '《台灣神學論刊》', pub: '台灣神學研究學院', fit: '基督教那一線的本土神學系譜（黃彰輝—宋泉盛—王憲治—黃伯和）' },
  { name: '《神學與教會》', pub: '台南神學院', fit: '王憲治與台灣鄉土神學的核心場域，史料與人脈都在這裡' },
  { name: '《法鼓佛學學報》', pub: '法鼓文理學院', fit: '人間佛教思想史，明列歡迎博士生投稿' },
  { name: '《臺大佛學研究》', pub: '國立臺灣大學文學院佛學研究中心', fit: '佛教思想史，審查嚴謹、能見度高' },
  { name: '《新世紀宗教研究》', pub: '宗教文化研究中心', fit: '當代宗教現象與社會參與，接受跨傳統比較' },
  { name: '《輔仁宗教研究》', pub: '輔仁大學宗教學系', fit: '宗教對話與比較研究，天主教背景但收非基督宗教題材' },
  { name: '《臺灣史研究》', pub: '中央研究院臺灣史研究所', fit: '若把第二、三章的日治到戰後段落寫成史學論文，這是最高規格的出口' },
  { name: '《道風：基督教文化評論》', pub: '漢語基督教文化研究所（香港）', fit: '漢語神學與處境化神學，適合方法論那一章的理論部分' },
]

const gates = [
  { n: '01', t: '修滿 24 學分', p: '7 / 24', s: 'run', d: '專業必修 9 ＋ 專業選修 15　·　第二條' },
  { n: '02', t: '完成語言要求', p: '辦理中', s: 'run', d: '中／英文檢定 ＋ 一門研究語言　·　第三條' },
  { n: '03', t: '通過博士候選人資格考', p: '待修滿學分', s: 'todo', d: '兩科筆試，各 70 分及格　·　第四條' },
  { n: '04', t: '通過論文計畫口試', p: '未開始', s: 'todo', d: '一萬字以上計畫書，口試審查　·　第六條' },
  { n: '05', t: '發表兩篇審稿論文', p: '3 篇進行中', s: 'run', d: '具審稿制度之研討會或專業學術期刊　·　第五條「在學期間」' },
  { n: '06', t: '通過博士論文口試', p: '未開始', s: 'todo', d: '公開口試，70 分及格　·　第七條' },
]

function pillClass(s: string) {
  if (s === 'done') return 'text-emerald-700 border-emerald-300 bg-emerald-50'
  if (s === 'run') return 'text-amber-700 border-amber-300 bg-amber-50'
  return 'text-gray-500 border-gray-300 bg-white'
}

const timeline = [
  {
    term: '115-1', who: '博一上', when: '2026 秋', now: true,
    items: [
      '<code>BBJ001</code> 宗教研究基本問題與研究方法　<b>3　必修</b>　一 2-4 節',
      '<code>BBJ029</code> 唯識思想專題研討　<b>2　選修</b>　三 3-4 節',
      '<code>BBJ025</code> 宗教經濟學專題研討　<b>2　選修</b>　一 6-7 節　<span class="text-gray-400">賴建誠　已額滿，須加簽</span>',
      '<code>JJA051</code> 宗教學理論與方法（一）　2　單週六　<span class="text-gray-400">補修，不計畢業學分</span>',
      '台神希伯來文 II（9/16 起）　<span class="text-gray-400">辦理校際選課，學分待系主任與指導教授認可</span>',
      '<code>BBA224</code> 初階宗教學日文文獻選讀　<span class="text-gray-400">改為旁聽，不計學分、不佔額度</span>',
    ],
    tally: '計入 24 者 <b class="text-gray-700">7</b>（希伯來文獲採計則 9）。累計 <b class="text-gray-700">7</b>。',
  },
  {
    term: '115-2', who: '博一下', when: '2027 春', now: false,
    items: [
      '<code>BBJ002</code> 全球化與在地化宗教專題研討　<b>3　必修</b>',
      '博班專業選修 4 學分',
      '<code>JJA052</code> 宗教學理論與方法（二）　2　<span class="text-gray-400">補修，不計畢業學分</span>',
      '<b>完成 AREE 學術研究倫理課程六小時</b>　<span class="text-gray-400">要點第二點：入學第一學年結束前</span>',
    ],
    tally: '計入 <b class="text-gray-700">7</b>。累計 <b class="text-gray-700">14</b>。本學期起若前學期平均達 90 分可申請超修 1–3 門。',
  },
  {
    term: '116-1', who: '博二上', when: '2027 秋', now: false,
    items: [
      '<code>BBJ003</code> 亞洲宗教比較研究　<b>3　必修</b>　<span class="text-gray-400">必修 9 學分至此修畢</span>',
      '博班專業選修 6 學分',
      '投出第一篇審稿論文',
    ],
    tally: '兩門補修都已修完，額度全給博班課。計入 <b class="text-gray-700">9</b>。累計 <b class="text-gray-700">23</b>（希伯來文獲採計則 25，即可提前於 116-2 考資格考）。',
  },
  {
    term: '116-2', who: '博二下', when: '2028 春', now: false,
    items: [
      '補足專業選修，<b>24 學分修滿</b>',
      '完成語言兩關（檢定 ＋ 研究語言）',
      '撰寫論文計畫書，期末前完稿',
    ],
    tally: '累計 <b class="text-gray-700">24</b>。學分修滿是資格考的前提，這一步沒到，後面全部往後推。',
  },
  {
    term: '117-1', who: '博三上', when: '2028 秋　最擠的一學期', now: false,
    items: [
      '<b>開學後一週內</b>遞資格考申請',
      '<b>11 月下旬</b>資格考 → 通過即取得博士候選人資格',
      '<b>1/31 前</b>完成計畫口試（3–5 位委員，校外至少三分之一）',
      '第二篇審稿論文見刊或獲接受',
    ],
    tally: '資格考放榜到 1/31 只有約兩個月。<b class="text-gray-700">計畫書必須在資格考之前就寫完</b>，放榜當週即送件。',
  },
  {
    term: '117-2', who: '博三下', when: '2029 春', now: false,
    items: [
      '論文口試（第 2 學期窗口 2/1 – 7/31）',
      '前置：論文比對、AREE 證明、指導教授同意',
      '<b>8/31 前</b>繳交論文、辦離校',
    ],
    tally: '自入學起滿三年。修業年限下限為 2 年，此路徑合規。',
  },
]

const quals = [
  { k: '前提', v: '<b>修滿 24 學分後</b>方得提出申請（系辦法第四條）' },
  { k: '科目', v: '一、宗教學基本知識　二、研究主題相關知識（由指導教授命題）' },
  { k: '形式', v: '筆試（校《學位考試辦法》第三條）。每科 70 分及格' },
  { k: '申請', v: '每學期<b>開學後一週內</b>向系上提出，核准標準由系上自訂' },
  { k: '舉行', v: '上學期 <b>11 月下旬</b>／下學期 <b>4 月中旬</b>' },
  { k: '通過後', v: '完成應修課程 ＋ 通過資格考 ＝ <b>博士學位候選人</b>（校《學位考試辦法》第十條）' },
  { k: '不及格', v: '系辦法：至少隔一學期後重考，<b>三次</b>為限<br>校辦法第十六條：重考<b>一次</b>為限　<span class="text-gray-400">兩份衝突，待確認</span>' },
]

const todos = [
  {
    who: '教務處註冊課務組　分機 1227、1228',
    items: [
      '博士班每學期 9 學分上限，<b>補修課程</b>（<code>JJA051</code>／<code>JJA052</code>）算不算在內？',
      '<b>校際選課</b>學分算不算在內？',
      '資格考重考次數，以校辦法（一次）還是系辦法（三次）為準？',
    ],
  },
  {
    who: '系辦（助教 蔡惠君）／指導教授',
    items: [
      '研討會與演講場次，以修業規定還是系辦法為準？',
      '<b>入學前</b>修習的語言課程（希伯來文 I），算不算第三條的「完成語言要求」？',
      '第三條第四款第一目的「<b>他系所</b>」是否含校外學校？',
      '希伯來文 II 的校際選課學分能否採計入 24 畢業學分？',
      '資格考從舉行到成績確定約需多久？計畫口試能否在成績確定前先送件排程？',
      '兩位指導教授的「指導教授同意聲明」是共簽一張，還是各簽一份？',
      '昭慧法師同時為指導教授與系主任（表單末須系所長核章），是否有迴避程序？',
    ],
  },
]
</script>

<style scoped>
.sub-h { @apply text-sm font-bold text-gray-900 mt-6 mb-1.5; }
.para  { @apply text-[13px] text-gray-700 leading-relaxed my-1.5; }
.bullets { @apply my-2 pl-5 list-disc marker:text-gray-300 space-y-1.5 text-[13px] text-gray-700 leading-relaxed; }
.bullets :deep(b), .para :deep(b) { @apply font-semibold text-gray-900; }
.tbl-wrap { @apply my-3 overflow-x-auto rounded-xl border border-gray-200 bg-white; }
.tbl { @apply w-full border-collapse text-[13px] min-w-[340px]; }
.tbl :deep(th), .tbl :deep(td) { @apply px-3 py-2 text-left align-top border-b border-gray-100 text-gray-700; }
.tbl :deep(thead th) { @apply bg-gray-50 text-[11px] tracking-wide font-bold text-gray-600 whitespace-nowrap; }
.tbl :deep(tbody tr:last-child td), .tbl :deep(tbody tr:last-child th) { @apply border-b-0; }
.tbl :deep(b) { @apply font-semibold text-gray-900; }
:deep(code) { @apply font-mono text-[0.85em] text-gray-600 bg-gray-100 rounded px-1 py-px; }
.no-scrollbar { scrollbar-width: none; }
.no-scrollbar::-webkit-scrollbar { display: none; }
</style>
