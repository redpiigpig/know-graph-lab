<template>
  <div class="min-h-screen bg-[#f4f5f7]">
    <AppHeader title="十六型宗教人格" :back="{ to: '/works', label: '寫作計畫' }" container-class="max-w-3xl" />

    <div class="max-w-3xl mx-auto px-5 py-10">

      <!-- ── 開始 ── -->
      <section v-if="stage === 'intro'">
        <p class="text-xs tracking-[0.3em] text-[#1f5673] mb-4">世界宗教文化導論・第一堂</p>
        <h1 class="font-serif text-3xl sm:text-4xl text-[#16181d] leading-snug mb-5">
          你最接近哪一種<br class="sm:hidden">宗教人格？
        </h1>
        <p class="text-[15px] leading-[1.95] text-gray-600 mb-4">
          二十個問題，一句都不會問你信什麼——問的是約會、森林、演唱會、中秋節烤肉。
          <span class="text-[#16181d]">但你答完會得到四個字。</span>
        </p>
        <p class="text-[15px] leading-[1.95] text-gray-600 mb-8">
          那四個字是人類幾千年來所有宗教都在回答的四個問題：神聖在哪裡、你怎麼認識它、
          你一個人還是跟大家一起、你想改變世界還是放過它。交叉起來十六型，
          等一下我們就用它分組——接下來四週的報告，你會研究跟自己最像的那一類。
        </p>

        <div class="grid grid-cols-2 gap-3 mb-9">
          <div v-for="ax in AXES" :key="ax.key" class="bg-white rounded-xl px-4 py-3.5 border border-gray-100">
            <div class="text-[11px] text-gray-400 mb-1.5">{{ ax.title }}</div>
            <div class="flex items-baseline gap-1.5 font-serif">
              <span class="text-lg text-[#1f5673]">{{ ax.pos }}</span>
              <span class="text-gray-300 text-xs">／</span>
              <span class="text-lg text-[#c03a2b]">{{ ax.neg }}</span>
            </div>
          </div>
        </div>

        <button @click="start"
          class="w-full sm:w-auto px-9 py-3.5 rounded-full bg-[#16181d] text-white text-[15px] hover:bg-[#1f5673] transition">
          開始，大約五分鐘
        </button>

        <button @click="stage = 'teacher'" class="block mt-10 text-xs text-gray-400 hover:text-gray-600 transition">
          教師分組工具
        </button>
      </section>

      <!-- ── 作答 ── -->
      <section v-else-if="stage === 'quiz'">
        <div class="flex items-center gap-1 mb-9">
          <span v-for="(q, i) in QUESTIONS" :key="i"
            class="h-1 flex-1 rounded-full transition-colors"
            :class="i < index ? 'bg-[#1f5673]' : i === index ? 'bg-[#c03a2b]' : 'bg-gray-200'"></span>
        </div>

        <p class="text-xs text-gray-400 mb-3">第 {{ index + 1 }} 題 ／ 共 {{ QUESTIONS.length }} 題</p>
        <h2 class="font-serif text-2xl text-[#16181d] leading-[1.6] mb-8">{{ current.text }}</h2>

        <div class="space-y-3">
          <button v-for="side in SIDES" :key="side" @click="answer(side)"
            class="w-full text-left bg-white rounded-2xl px-5 py-4 border border-gray-200 hover:border-[#1f5673] hover:shadow-sm transition group">
            <span class="text-[15px] leading-relaxed text-gray-800 group-hover:text-[#16181d]">{{ current[side] }}</span>
          </button>
        </div>

        <button v-if="index" @click="back" class="mt-8 text-xs text-gray-400 hover:text-gray-600 transition">← 上一題</button>
      </section>

      <!-- ── 結果 ── -->
      <section v-else-if="stage === 'result' && result">
        <p class="text-xs tracking-[0.3em] text-[#1f5673] mb-6">你的宗教人格</p>

        <div class="bg-white rounded-2xl border border-gray-100 px-6 sm:px-9 py-8 mb-6">
          <div class="flex items-start gap-7 mb-7">
            <div class="flex flex-col gap-2 pt-1.5 shrink-0">
              <div v-for="(ch, i) in result.code" :key="i" class="flex gap-1.5 w-[52px]">
                <template v-if="ch === AXES[i].pos">
                  <span class="h-[7px] flex-1 rounded-sm bg-[#16181d]"></span>
                </template>
                <template v-else>
                  <span class="h-[7px] flex-1 rounded-sm bg-[#c03a2b]"></span>
                  <span class="h-[7px] flex-1 rounded-sm bg-[#c03a2b]"></span>
                </template>
              </div>
            </div>
            <div class="min-w-0">
              <div class="font-serif text-4xl text-[#16181d] tracking-[0.15em] mb-2">{{ result.code }}</div>
              <div class="font-serif text-xl text-[#1f5673] mb-3">{{ result.type.name }}</div>
              <p class="text-[15px] leading-[1.9] text-gray-700">{{ result.type.line }}</p>
            </div>
          </div>

          <p class="text-[15px] leading-[1.95] text-gray-700 mb-6 break-words">{{ result.type.desc }}</p>

          <div class="border-t border-gray-100 pt-5">
            <div class="text-[11px] text-gray-400 mb-2.5">世界宗教裡跟你同一格的</div>
            <div class="flex flex-wrap gap-2">
              <span v-for="e in result.type.echoes" :key="e"
                class="text-[13px] px-3 py-1.5 rounded-full bg-[#f4f5f7] text-gray-600">{{ e }}</span>
            </div>
          </div>
        </div>

        <!-- 四軸強度 -->
        <div class="bg-white rounded-2xl border border-gray-100 px-6 sm:px-9 py-7 mb-6">
          <div v-for="ax in AXES" :key="ax.key" class="mb-5 last:mb-0">
            <div class="flex items-center justify-between text-[13px] mb-2 gap-3">
              <span class="truncate" :class="result.scores[ax.key] >= 3 ? 'text-[#16181d] font-medium' : 'text-gray-400'">
                {{ ax.pos }}・{{ ax.posLabel }}
              </span>
              <span class="truncate" :class="result.scores[ax.key] < 3 ? 'text-[#16181d] font-medium' : 'text-gray-400'">
                {{ ax.negLabel }}・{{ ax.neg }}
              </span>
            </div>
            <!-- 長條從贏的那一側長出來：靠左＝天文眾入，靠右＝地感獨出 -->
            <div class="h-1.5 rounded-full bg-gray-100 relative overflow-hidden">
              <span class="absolute inset-y-0 rounded-full"
                :class="result.scores[ax.key] >= 3 ? 'left-0 bg-[#1f5673]' : 'right-0 bg-[#c03a2b]'"
                :style="{ width: (Math.max(result.scores[ax.key], 5 - result.scores[ax.key]) / 5 * 100) + '%' }"></span>
            </div>
          </div>
        </div>

        <!-- 分組 -->
        <div class="bg-[#16181d] text-white rounded-2xl px-6 sm:px-9 py-7 mb-6">
          <div class="text-[11px] tracking-widest text-white/40 mb-2">你的報告小組</div>
          <div class="font-serif text-2xl mb-3">{{ result.family.title }}</div>
          <p class="text-[15px] leading-[1.9] text-white/70 mb-4">{{ result.family.topic }}</p>
          <ul class="space-y-1.5">
            <li v-for="h in result.family.hints" :key="h" class="text-[13px] text-white/50 leading-relaxed">— {{ h }}</li>
          </ul>
        </div>

        <div class="bg-white rounded-2xl border border-gray-100 px-6 sm:px-9 py-6 mb-8">
          <p class="text-[13px] text-gray-500 leading-relaxed mb-4">
            把下面這一行交給老師（貼進課堂的問答，或直接抄在紙上），我們用它來分組。
          </p>
          <div class="flex flex-col sm:flex-row gap-3">
            <input v-model="myName" placeholder="你的名字"
              class="flex-1 px-4 py-2.5 rounded-xl border border-gray-200 text-[15px] focus:outline-none focus:border-[#1f5673]" />
            <input v-model="myDept" placeholder="系級（例：宗教1A）"
              class="flex-1 px-4 py-2.5 rounded-xl border border-gray-200 text-[15px] focus:outline-none focus:border-[#1f5673]" />
          </div>
          <div class="mt-3 flex items-center gap-3">
            <code class="flex-1 text-[15px] bg-[#f4f5f7] rounded-xl px-4 py-2.5 text-gray-700 truncate">{{ submitLine }}</code>
            <button @click="copyLine"
              class="px-5 py-2.5 rounded-xl bg-[#1f5673] text-white text-sm hover:bg-[#16181d] transition shrink-0">
              {{ copied ? '已複製' : '複製' }}
            </button>
          </div>
        </div>

        <button @click="reset" class="text-xs text-gray-400 hover:text-gray-600 transition">重做一次</button>
      </section>

      <!-- ── 教師分組工具 ── -->
      <section v-else-if="stage === 'teacher'">
        <h1 class="font-serif text-2xl text-[#16181d] mb-3">教師分組工具</h1>
        <p class="text-[14px] leading-[1.9] text-gray-600 mb-5">
          一行一位學生，格式「姓名　系級　四字代碼」，順序不拘，只要那一行裡有四個字的代碼就抓得到。
          同一家族的人排在一起（十六型收成八組），再把系級打散，讓每組都有帶得動報告的宗教系學生。
        </p>
        <textarea v-model="rawInput" rows="10" placeholder="王小明 宗教1A 天文眾入"
          class="w-full px-4 py-3 rounded-xl border border-gray-200 text-[14px] leading-relaxed focus:outline-none focus:border-[#1f5673]"></textarea>

        <div class="flex items-center gap-4 mt-4 mb-8">
          <label class="text-[13px] text-gray-500">每組人數
            <input v-model.number="groupSize" type="number" min="2" max="10"
              class="w-16 ml-2 px-2 py-1.5 rounded-lg border border-gray-200 text-center" />
          </label>
          <span class="text-[13px] text-gray-400">共 {{ parsed.length }} 人 → {{ groups.length }} 組</span>
        </div>

        <div v-if="groups.length" class="space-y-4">
          <div v-for="(g, i) in groups" :key="i" class="bg-white rounded-2xl border border-gray-100 px-6 py-5">
            <div class="flex items-baseline justify-between mb-1 gap-3">
              <span class="font-serif text-lg text-[#16181d]">第 {{ i + 1 }} 組・{{ g.family.title }}</span>
              <span class="text-xs text-gray-400 shrink-0">{{ g.members.length }} 人</span>
            </div>
            <p class="text-[13px] text-gray-500 mb-3">{{ g.family.topic }}</p>
            <div class="flex flex-wrap gap-2">
              <span v-for="m in g.members" :key="m.name + m.code"
                class="text-[13px] px-3 py-1.5 rounded-full"
                :class="m.moved ? 'bg-amber-50 text-amber-700' : 'bg-[#f4f5f7] text-gray-700'">
                {{ m.name }}<span class="text-gray-400 ml-1.5">{{ m.dept }}</span><span class="text-gray-300 ml-1.5">{{ m.code }}</span>
              </span>
            </div>
          </div>
          <p class="text-xs text-gray-400 leading-relaxed pt-1">
            標黃的是為了湊人數或平衡系級被移過來的，他原本的家族跟這一組只差一個軸。
          </p>
        </div>

        <button @click="stage = 'intro'" class="mt-10 text-xs text-gray-400 hover:text-gray-600 transition">← 回測驗</button>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
useHead({ title: '十六型宗教人格｜世界宗教文化導論' })

type AxisKey = 'a' | 'b' | 'c' | 'd'
type Side = 'pos' | 'neg'

const SIDES: Side[] = ['pos', 'neg']

const AXES = [
  { key: 'a' as AxisKey, title: '神聖在哪裡', pos: '天', neg: '地', posLabel: '在世界之上', negLabel: '在萬物之中' },
  { key: 'b' as AxisKey, title: '怎麼認識它', pos: '文', neg: '感', posLabel: '讀懂道理', negLabel: '親身體驗' },
  { key: 'c' as AxisKey, title: '在哪裡修', pos: '眾', neg: '獨', posLabel: '在人群中', negLabel: '一個人' },
  { key: 'd' as AxisKey, title: '怎麼看世界', pos: '入', neg: '出', posLabel: '改變它', negLabel: '放下它' },
]

// 二十題一句宗教都不提：問的是約會、森林、演唱會。答案落在哪一軸，答的人自己看不出來。
const QUESTIONS: { axis: AxisKey; text: string; pos: string; neg: string }[] = [
  { axis: 'a', text: '你走進一座森林，最希望遇見哪一種動物？', pos: '一隻在高處盤旋、幾乎不落地的鷹', neg: '一頭安靜走過你身邊的鹿' },
  { axis: 'b', text: '朋友帶來一套你沒玩過的桌遊，你會？', pos: '先把說明書從頭看完', neg: '先開始玩，邊玩邊問規則' },
  { axis: 'c', text: '一個沒有安排的週末，最理想的樣子是？', pos: '一群朋友吃飯聊到很晚', neg: '一個人在家，手機轉靜音' },
  { axis: 'd', text: '排隊的時候有人插到你前面，你會？', pos: '出聲說一下', neg: '算了，讓他去' },
  { axis: 'a', text: '第一次約會，你希望對方帶你去哪裡？', pos: '山頂上，看得到整座城市的夜景', neg: '他從小吃到大的那家巷口麵店' },
  { axis: 'b', text: '菜還沒上桌，這段時間你在做什麼？', pos: '讀菜單上那段介紹', neg: '聞味道，順便看隔壁桌點了什麼' },
  { axis: 'c', text: '去看演唱會，你想站在哪裡？', pos: '搖滾區，跟著所有人一起跳', neg: '後面一點的位子，看得清楚就好' },
  { axis: 'd', text: '突然中了一筆不小的錢，你第一件事是？', pos: '拿一部分去做一件一直想做的事，順便幫點人', neg: '辭掉工作，找個安靜的地方住下來' },
  { axis: 'a', text: '半夜開車經過一片很空曠的地方，你停下來看什麼？', pos: '抬頭那一整片星空', neg: '遠處還亮著燈的那一戶人家' },
  { axis: 'b', text: '有一首聽不懂歌詞的外語歌，你很喜歡。然後呢？', pos: '去查它到底在唱什麼', neg: '不用查，跟著哼就很爽' },
  { axis: 'c', text: '心情很差的那天，你會？', pos: '找個人講一講', neg: '自己出去走一走' },
  { axis: 'd', text: '滑到一則讓你很生氣的新聞，你通常？', pos: '轉發，或者留言講兩句', neg: '關掉不看，免得心情壞一整天' },
  { axis: 'a', text: '房間牆上只能掛一張圖，你選？', pos: '一張星系的照片', neg: '一張全家人的合照' },
  { axis: 'b', text: '出發旅行的前一晚，你在做什麼？', pos: '把行程排好、資料查清楚', neg: '行李收一收就睡，到了再說' },
  { axis: 'c', text: '分組報告，你希望怎麼進行？', pos: '大家坐下來一起討論到有共識', neg: '先分工，各自做完再合起來' },
  { axis: 'd', text: '如果可以許一個一定會實現的願望，你許？', pos: '這個世界少一點不公平', neg: '我心裡少一點煩惱' },
  { axis: 'a', text: '有人送你一張免費機票，你飛去哪？', pos: '去看世界上最大的那座教堂或清真寺', neg: '去朋友的老家，住一個禮拜' },
  { axis: 'b', text: '到了一個陌生的城市，你怎麼認路？', pos: '先看地圖，把街名記起來', neg: '憑感覺走，走過一次就記得了' },
  { axis: 'c', text: '中秋節烤肉，你多半在做什麼？', pos: '招呼大家、負責控場', neg: '顧火，默默把肉串好' },
  { axis: 'd', text: '十年後，你希望別人怎麼形容你？', pos: '「他改變了一些事。」', neg: '「他過得很自在。」' },
]

type TypeInfo = { name: string; line: string; desc: string; echoes: string[] }

const TYPES: Record<string, TypeInfo> = {
  天文眾入: { name: '先知型', line: '你相信有一個超過人的意志，而它對這個世界有話要說。', desc: '你透過經典與教導認識神聖，在群體裡實踐，而且不覺得信仰可以只停在心裡——看到不公平的事，你會覺得那正是信仰要處理的。宗教史上最會惹麻煩的一群人，多半是這一型。', echoes: ['希伯來先知阿摩司', '伊斯蘭改革運動', '天主教社會訓導', '太虛與人間佛教'] },
  天文眾出: { name: '聖禮型', line: '你在重複了千百年的儀式裡，感覺到那個不會改變的東西。', desc: '神在上，而人靠著禮儀、節期與經文一次次靠近祂。你不急著改變世界，因為你相信真正重要的事發生在另一個層次——把儀式做對、把傳統守住，本身就是回應。', echoes: ['東正教聖禮', '正統派猶太教安息日', '淨土宗共修', '聖公會日課'] },
  天文獨入: { name: '經師型', line: '你一個人把道理想通，然後把它帶回人間。', desc: '你信任文字與論證，習慣獨自鑽研，但你讀書不是為了躲起來——弄懂了之後，你想把它用在真實的問題上。傳統裡的法學家、神學家、講經的人，多半是這一型。', echoes: ['伊斯蘭教法學者', '經院哲學', '儒家士人', '拉比釋經傳統'] },
  天文獨出: { name: '隱修型', line: '你想弄懂的不是世界，是你跟那位超越者的關係。', desc: '你可以一個人讀很久的書、抄很久的經，而且不覺得無聊。世界的事情不是不重要，只是不在你這一格。宗教史上最安靜也最持久的力量，常常出自這一型。', echoes: ['沙漠教父', '本篤會修道院', '藏傳格魯派學僧', '天台止觀'] },
  天感眾入: { name: '復興型', line: '你相信那位超越者會現在、當場、在這群人中間動工。', desc: '你認識神聖的方式是強烈的體驗，而且那種體驗要在一群人裡才燒得起來。感受到了就要傳出去——這一型是宗教最有擴散力的形態，也最容易被主流批評。', echoes: ['五旬節運動', '非洲獨立教會', '日本新宗教', '大覺醒佈道'] },
  天感眾出: { name: '朝聖型', line: '你要用整個身體走過去，才算真的到過那裡。', desc: '你透過人群、行走、音樂與香火感覺神聖，而目的地永遠在此世之外。你不太相信只靠讀書能認識神，也不太在意這個世界的爭吵——重點是路上。', echoes: ['麥加朝覲', '印度大壺節', '大甲媽祖遶境', '聖雅各之路'] },
  天感獨入: { name: '異象型', line: '你一個人領受到了什麼，然後帶著它回到人群中。', desc: '你的信仰來自一次無法解釋的個人經驗，不是別人教你的。這一型的人往往被推到領導的位置，因為他們的權威不來自制度而來自那次經驗——這也是他們常跟制度衝突的原因。', echoes: ['貞德', '蘇非導師', '薩滿的召喚', '扶乩開壇'] },
  天感獨出: { name: '神祕型', line: '你要的不是知道祂，是消失在祂裡面。', desc: '你相信最深的那一層講不出來，也不必講。你一個人走，往世界之外走，語言在那裡會失效。所有宗教都出過這一型的人，而且他們彼此讀得懂對方。', echoes: ['十字若望', '蘇非密契', '大德蘭', '禪的默照'] },
  地文眾入: { name: '倫理型', line: '你覺得神聖不在天上，在人怎麼對待人。', desc: '你靠典籍與思辨認識世界，在群體中實踐，而你檢驗一個宗教好不好，看的是它讓人變成什麼樣子。這一型撐起了宗教裡最大的一塊：教育、醫療、賑災、社會運動。', echoes: ['儒家', '慈濟', '猶太人道主義', '入世佛教'] },
  地文眾出: { name: '傳承型', line: '你把上一代交下來的規矩，原樣交給下一代。', desc: '神聖在血脈、在節氣、在祖先牌位與家裡那個老規矩裡。你不覺得需要改造世界，也不追求神祕經驗——把該做的做對、該記得的記得，就是虔誠。', echoes: ['祖先祭祀', '台灣民間信仰', '日本神道', '越南家庭祭壇'] },
  地文獨入: { name: '哲思型', line: '你一個人想通了道理，然後用它來質問世界。', desc: '你不接受「因為傳統是這樣」，你要自己想過。而想通之後你不會沉默——這一型常常站在制度的外面批評制度，卻比很多在裡面的人更認真。', echoes: ['斯多噶學派', '莊子', '內村鑑三與無教會主義', '解放神學'] },
  地文獨出: { name: '無執型', line: '你讀了很多，最後讀到「沒有一個可以抓的東西」。', desc: '你靠思辨走，卻走到思辨的盡頭。你一個人，也不打算改變什麼，因為你懷疑那個要改變的「我」本身就是假的。這一型是宗教思想史上最鋒利的一群。', echoes: ['龍樹中觀', '老子', '禪宗公案', '否定神學'] },
  地感眾入: { name: '土地型', line: '神聖就在這塊土地、這條河、這群人的身體裡。', desc: '你用身體和一起生活的人感覺神聖，而神聖是要守護的——土地被破壞，就是神聖被破壞。這一型在原住民傳統與當代生態運動裡同時活著。', echoes: ['台灣原住民祭儀', '非洲傳統宗教', '安地斯大地母', '生態靈性'] },
  地感眾出: { name: '通靈型', line: '你相信身體會被借用，而另一個世界會借它說話。', desc: '你透過群體的身體感應——起乩、附身、舞蹈、擊鼓——接觸神聖，而那個世界不是這個世界。這一型是人類最古老的宗教形態，到今天都還活著。', echoes: ['台灣童乩', '韓國巫堂', '海地 Vodou', '西伯利亞薩滿'] },
  地感獨入: { name: '療癒型', line: '你從自己的身心出發，也想讓身邊的人好過一點。', desc: '你相信神聖不必上教堂才有，它在呼吸、在飲食、在照顧人的手上。這一型在當代最常見，也最容易被說「那不算宗教」——但它處理的正是宗教一直在處理的事。', echoes: ['正念與禪修', '瑜伽', '民俗療者', '當代身心靈'] },
  地感獨出: { name: '隱逸型', line: '你在山裡、在海邊，一個人的時候最靠近它。', desc: '你不靠經典也不靠群體，靠的是獨自置身自然時那種說不出來的東西。你也不想改變世界——你只想它安靜一點。東亞的隱逸傳統養了兩千年這一型的人。', echoes: ['道教養生', '日本山岳信仰', '梭羅式自然靈性', '陶淵明'] },
}

type Family = { title: string; topic: string; hints: string[] }

const FAMILIES: Record<string, Family> = {
  天文入: { title: '經典與正義', topic: '一個宗教怎麼從經典裡讀出「這件事不對」，又憑什麼要求整個社會改？', hints: ['選一個宗教的社會運動，找出它引用的經文', '同一段經文被正反兩方引用的例子', '為什麼有些傳統認為宗教不該碰政治'] },
  天文出: { title: '儀式、修道與神聖時間', topic: '重複做同一件事，為什麼會讓人覺得碰到了永恆？', hints: ['挑一個儀式，畫出它的完整流程與意義', '修道院／叢林的一日作息比較', '節期怎麼把一年切成「神聖的」與「平常的」'] },
  天感入: { title: '靈恩、復興與宗教權威', topic: '當一個人說「我親身經歷了」，制度該拿他怎麼辦？', hints: ['一場宗教復興運動的興起與被壓制', '個人經驗與制度權威衝突的案例', '為什麼復興運動特別容易在邊緣人群中發生'] },
  天感出: { title: '朝聖、節慶與神祕經驗', topic: '為什麼人要用身體走那麼遠，才覺得到得了？', hints: ['一條朝聖路線的實地資料與人數變化', '不同宗教的神祕經驗描述有多像', '觀光化之後，朝聖還是朝聖嗎'] },
  地文入: { title: '宗教倫理與公共生活', topic: '不談神也可以很虔誠嗎？宗教如何變成一套做人的道理。', hints: ['一個宗教慈善組織的實際運作', '宗教倫理與世俗倫理的差別在哪', '世俗化之後，宗教留下了什麼'] },
  地文出: { title: '祖先、傳承與「空」的智慧', topic: '一邊拜祖先、一邊講無我，這兩件事怎麼同時成立？', hints: ['台灣或越南家庭祭祀的實地觀察', '佛教的無我與民間的祖先崇拜如何共存', '傳統斷掉的時候，人失去了什麼'] },
  地感入: { title: '土地、身體與當代靈性', topic: '把神聖放回土地與身體，是回到最古老，還是最新潮？', hints: ['原住民祭儀與土地權的關係', '瑜伽／正念從宗教變成保健的過程', '生態運動裡的宗教語言'] },
  地感出: { title: '靈媒、附身與自然崇拜', topic: '人類最古老的宗教形態，為什麼到今天還沒消失？', hints: ['童乩或巫堂的實際田野紀錄', '附身現象在不同文化裡的解釋', '為什麼現代社會反而更需要它'] },
}

// 家族＝收掉「眾／獨」那一軸：十六型剛好收成八組
const familyKey = (code: string) => code[0] + code[1] + code[3]

const stage = ref<'intro' | 'quiz' | 'result' | 'teacher'>('intro')
const index = ref(0)
const picks = ref<Side[]>([])
const myName = ref('')
const myDept = ref('')
const copied = ref(false)

const current = computed(() => QUESTIONS[index.value])

const result = computed(() => {
  if (picks.value.length < QUESTIONS.length) return null
  const scores: Record<AxisKey, number> = { a: 0, b: 0, c: 0, d: 0 }
  QUESTIONS.forEach((q, i) => { if (picks.value[i] === 'pos') scores[q.axis]++ })
  const code = AXES.map((ax) => (scores[ax.key] >= 3 ? ax.pos : ax.neg)).join('')
  return { code, scores, type: TYPES[code], family: FAMILIES[familyKey(code)] }
})

const submitLine = computed(() =>
  [myName.value || '（姓名）', myDept.value || '（系級）', result.value?.code ?? ''].join(' '))

function start() { picks.value = []; index.value = 0; stage.value = 'quiz' }
function back() { index.value--; picks.value = picks.value.slice(0, index.value) }
function reset() { stage.value = 'intro' }

function answer(side: Side) {
  picks.value[index.value] = side
  if (index.value + 1 < QUESTIONS.length) index.value++
  else stage.value = 'result'
}

async function copyLine() {
  try {
    await navigator.clipboard.writeText(submitLine.value)
    copied.value = true
    setTimeout(() => (copied.value = false), 1600)
  } catch { /* 手機瀏覽器擋剪貼簿時，讓他自己照著抄 */ }
}

/* ── 教師分組 ── */
type Student = { name: string; dept: string; code: string; moved?: boolean }

const rawInput = ref('')
const groupSize = ref(5)

const parsed = computed<Student[]>(() =>
  rawInput.value.split('\n').map((line) => {
    const code = line.match(/[天地][文感][眾獨][入出]/)?.[0]
    if (!code) return null
    const rest = line.replace(code, '').trim().split(/[\s,，\t]+/).filter(Boolean)
    return { name: rest[0] ?? '（無名）', dept: rest.slice(1).join(' '), code }
  }).filter((s): s is Student => !!s))

// 每組至少兩位宗教系學生，報告才帶得動
const isMajor = (s: Student) => /宗教/.test(s.dept)

const groups = computed(() => {
  const people = parsed.value
  if (!people.length) return []
  const size = Math.max(2, groupSize.value)
  const count = Math.ceil(people.length / size)

  // 先照家族分堆，人多的家族優先佔位
  const byFamily = new Map<string, Student[]>()
  for (const s of people) {
    const k = familyKey(s.code)
    if (!byFamily.has(k)) byFamily.set(k, [])
    byFamily.get(k)!.push(s)
  }
  const seats = [...byFamily.entries()]
    .sort((x, y) => y[1].length - x[1].length)
    .slice(0, count)
    .map(([key, members]) => ({ key, members: members.slice(0, size) }))
  if (!seats.length) return []

  // 沒排上的（家族太小、或那一組滿了）補進最像的一組
  const placed = new Set(seats.flatMap((g) => g.members))
  const distance = (x: string, y: string) => [...x].filter((ch, i) => ch !== y[i]).length
  for (const s of people.filter((p) => !placed.has(p))) {
    const open = seats.filter((g) => g.members.length < size)
    const pool = open.length ? open : seats
    const target = [...pool].sort((p, q) =>
      distance(familyKey(s.code), p.key) - distance(familyKey(s.code), q.key)
      || p.members.length - q.members.length)[0]
    target.members.push({ ...s, moved: true })
  }

  // 系級平衡：宗教系多的組跟一位都沒有的組換人
  for (let pass = 0; pass < 3; pass++) {
    const poor = seats.filter((g) => g.members.filter(isMajor).length < 2)
    if (!poor.length) break
    let swapped = false
    for (const p of poor) {
      const donor = seats.find((g) => g !== p && g.members.filter(isMajor).length > 2)
      if (!donor) break
      const give = donor.members.findIndex(isMajor)
      const take = p.members.findIndex((m) => !isMajor(m))
      if (give < 0 || take < 0) continue
      const a = donor.members[give], b = p.members[take]
      donor.members[give] = { ...b, moved: true }
      p.members[take] = { ...a, moved: true }
      swapped = true
    }
    if (!swapped) break
  }

  return seats.map((g) => ({ family: FAMILIES[g.key], members: g.members }))
})
</script>

<style scoped>
.font-serif {
  font-family: 'Noto Serif TC', 'Source Han Serif TC', 'Songti TC', 'PMingLiU', serif;
}
</style>
