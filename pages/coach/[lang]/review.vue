<template>
  <div class="flex flex-col bg-slate-50 min-h-dvh">
    <AppHeader title="AI 語言教練" :back="{ to: `/coach/${language}`, label: '教練首頁' }" container-class="max-w-full" />
    <nav class="flex items-center gap-3 px-4 h-12 bg-white border-b border-gray-100 z-30">
      <NuxtLink :to="`/coach/${language}`" class="text-gray-400 hover:text-gray-700 transition text-lg leading-none">←</NuxtLink>
      <div class="w-px h-5 bg-gray-200" />
      <span class="text-sm font-semibold text-gray-900">單字複習</span>
      <div class="ml-auto flex items-center gap-1">
        <CoachTimer :seconds="tracker.activeSeconds.value" />
        <button @click="endless = !endless" class="text-xs px-2.5 py-1 rounded-lg transition mr-1" :class="endless ? 'bg-violet-600 text-white' : 'bg-gray-50 text-gray-500'" title="刷完到期單字後自動生成新學術單字，永不停">♾️ 無限</button>
        <button @click="mode = 'flip'" class="text-xs px-2.5 py-1 rounded-lg transition" :class="mode === 'flip' ? 'bg-indigo-600 text-white' : 'bg-gray-50 text-gray-500'">翻卡</button>
        <button @click="mode = 'quiz'" class="text-xs px-2.5 py-1 rounded-lg transition" :class="mode === 'quiz' ? 'bg-indigo-600 text-white' : 'bg-gray-50 text-gray-500'">選擇題</button>
        <button @click="mode = 'cloze'" class="text-xs px-2.5 py-1 rounded-lg transition" :class="mode === 'cloze' ? 'bg-indigo-600 text-white' : 'bg-gray-50 text-gray-500'">克漏字</button>
      </div>
    </nav>

    <div class="flex-1 p-5 max-w-2xl mx-auto w-full">
      <!-- 複習卡 -->
      <div v-if="current" class="bg-white rounded-3xl border border-gray-100 shadow-sm p-8 text-center">
        <div class="text-xs text-gray-400 mb-4">剩餘 {{ queue.length }} 張 · 今日已複習 {{ reviewed }}</div>
        <div v-if="mode !== 'cloze'" class="text-3xl font-bold text-gray-900">{{ current.word }}</div>
        <div v-if="mode !== 'cloze' && current.reading" class="text-sm text-gray-400 mt-1">{{ current.reading }}</div>
        <button v-if="mode !== 'cloze' && speech.ttsSupported.value" @click="speak" class="mt-2 text-gray-300 hover:text-indigo-500 transition">🔊 發音</button>

        <!-- 克漏字模式：看中文＋挖空例句，打出單字 -->
        <template v-if="mode === 'cloze'">
          <div class="text-base text-gray-700 mt-1">{{ current.meaning }}</div>
          <div v-if="clozeSentence" class="text-sm text-gray-500 mt-3 italic">{{ clozeSentence }}</div>
          <input v-model="clozeInput" :disabled="clozeChecked" @keydown.enter="checkCloze" placeholder="打出這個單字…" class="mt-4 w-full text-center px-4 py-3 rounded-xl border text-lg focus:outline-none" :class="clozeChecked ? (clozeCorrect ? 'border-emerald-300 bg-emerald-50' : 'border-rose-300 bg-rose-50') : 'border-gray-200 focus:border-indigo-400'" />
          <button v-if="!clozeChecked" @click="checkCloze" :disabled="!clozeInput.trim()" class="mt-3 px-8 py-2.5 rounded-2xl bg-indigo-600 text-white font-semibold disabled:opacity-40 hover:bg-indigo-700 transition">檢查</button>
          <div v-else class="mt-4">
            <p v-if="clozeCorrect" class="text-sm text-emerald-600 font-medium">✓ 答對了！</p>
            <p v-else class="text-sm text-rose-600 font-medium">✗ 正解：{{ current.word }}</p>
            <div v-if="current.example" class="text-xs text-gray-400 mt-1 italic">{{ current.example }}</div>
            <button @click="next()" class="mt-3 px-8 py-2.5 rounded-2xl bg-indigo-600 text-white font-semibold hover:bg-indigo-700 transition">下一張 →</button>
          </div>
        </template>

        <!-- 選擇題模式：選意思 -->
        <template v-else-if="mode === 'quiz'">
          <div class="mt-5 space-y-2">
            <button v-for="(opt, oi) in current.options" :key="oi" @click="answer(opt)" :disabled="picked !== null"
              class="w-full text-left px-4 py-3 rounded-xl border text-sm transition"
              :class="optionClass(opt)">
              {{ opt }}
            </button>
          </div>
          <div v-if="picked !== null" class="mt-4">
            <p v-if="picked === current.meaning" class="text-sm text-emerald-600 font-medium">✓ 答對了！</p>
            <p v-else class="text-sm text-rose-600 font-medium">✗ 答錯了，已排進複習。正解：{{ current.meaning }}</p>
            <div v-if="current.example" class="text-xs text-gray-400 mt-1 italic">{{ current.example }}</div>
            <button @click="next()" class="mt-3 px-8 py-2.5 rounded-2xl bg-indigo-600 text-white font-semibold hover:bg-indigo-700 transition">下一張 →</button>
          </div>
        </template>

        <!-- 翻卡模式 -->
        <template v-else>
          <Transition name="fade">
            <div v-if="revealed" class="mt-5 pt-5 border-t border-gray-100">
              <div class="text-lg text-gray-800">{{ current.meaning }}</div>
              <div v-if="current.example" class="text-sm text-gray-400 mt-2 italic">{{ current.example }}</div>
            </div>
          </Transition>
          <div class="mt-7">
            <button v-if="!revealed" @click="revealed = true" class="px-8 py-3 rounded-2xl bg-indigo-600 text-white font-semibold hover:bg-indigo-700 transition">顯示答案</button>
            <div v-else class="grid grid-cols-4 gap-2">
              <button @click="grade(2)" class="py-3 rounded-xl bg-rose-50 text-rose-700 text-sm font-medium hover:bg-rose-100 transition">再來一次<span class="block text-[10px] opacity-60">1天</span></button>
              <button @click="grade(3)" class="py-3 rounded-xl bg-amber-50 text-amber-700 text-sm font-medium hover:bg-amber-100 transition">困難</button>
              <button @click="grade(4)" class="py-3 rounded-xl bg-sky-50 text-sky-700 text-sm font-medium hover:bg-sky-100 transition">良好</button>
              <button @click="grade(5)" class="py-3 rounded-xl bg-emerald-50 text-emerald-700 text-sm font-medium hover:bg-emerald-100 transition">簡單</button>
            </div>
          </div>
        </template>
      </div>

      <!-- 無限模式：正在生成新題 -->
      <div v-else-if="topping" class="bg-white rounded-3xl border border-gray-100 p-10 text-center">
        <div class="text-4xl mb-3 animate-pulse">♾️</div>
        <div class="font-semibold text-gray-800">正在生成新的學術單字…</div>
        <p class="text-sm text-gray-400 mt-1">教練在幫你出新題，馬上回來。</p>
      </div>

      <!-- 沒有到期單字（非無限模式，或生成失敗）-->
      <div v-else-if="!loading" class="bg-white rounded-3xl border border-gray-100 p-10 text-center">
        <div class="text-4xl mb-3">🎉</div>
        <div class="font-semibold text-gray-800">今日複習完成！</div>
        <p class="text-sm text-gray-400 mt-1">沒有到期的單字了。{{ endless ? "（無限模式找不到新題，可手動指定主題生成）" : "可以生成新的學術單字組繼續學，或開啟右上「♾️ 無限」自動出題。" }}</p>
      </div>

      <!-- 生成新單字組 -->
      <div class="mt-6 bg-white rounded-2xl border border-gray-100 p-5">
        <h2 class="text-sm font-semibold text-gray-800 mb-1">生成學術單字組</h2>
        <p class="text-xs text-gray-400 mb-3">依你的程度與人文興趣生成；自動加入複習排程。</p>
        <div class="flex flex-wrap gap-1.5 mb-3">
          <button v-for="p in PRESETS" :key="p" @click="theme = p" class="text-xs px-2.5 py-1 rounded-full border transition" :class="theme === p ? 'bg-indigo-50 border-indigo-300 text-indigo-700' : 'border-gray-200 text-gray-500'">{{ p }}</button>
        </div>
        <div class="flex gap-2">
          <input v-model="theme" placeholder="主題，如：GRE 哲學高頻字 / AWL Sublist 1 / 歷史學術用語" class="flex-1 px-3 py-2 rounded-lg border border-gray-200 text-sm focus:outline-none focus:border-indigo-400" />
          <button @click="generate" :disabled="generating || !theme.trim()" class="px-4 py-2 rounded-lg bg-indigo-600 text-white text-sm disabled:opacity-40 hover:bg-indigo-700 transition whitespace-nowrap">{{ generating ? '生成中…' : '生成' }}</button>
        </div>
        <p v-if="genMsg" class="text-xs text-emerald-600 mt-2">{{ genMsg }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import { useRoute } from "vue-router";
import { authedFetch } from "~/composables/useAuthedFetch";
import { useSpeech } from "~/composables/useSpeech";
import { useCoachAi } from "~/composables/useCoachAi";
import { useActivityTracker } from "~/composables/useActivityTracker";

definePageMeta({ middleware: "coach-auth" });

const { aiFetch } = useCoachAi();
const tracker = useActivityTracker();

// 主題池依語言不同：英文走學術/考試；日文走 N5→N4 初學（簡單、文化/宗教淺白）
const THEME_POOLS: Record<string, { presets: string[]; auto: string[] }> = {
  en: {
    presets: ["AWL Sublist 1", "GRE 高頻字", "哲學學術用語", "歷史學術用語", "神學術語", "文學批評術語", "學術寫作連接詞"],
    // 無限模式用：全為「手工策展」主題（後端直接插策展單字、不走 AI）→ 永遠秒出題、不卡頓
    auto: [
      "AWL Sublist 1", "GRE 高頻字", "哲學學術用語", "歷史學術用語",
      "神學術語", "文學批評術語", "學術寫作連接詞",
    ],
  },
  ja: {
    presets: ["N5 基礎單字", "N4 常用單字", "日常生活單字", "神社・お寺の基礎語", "祭りと行事", "食べ物と飲み物"],
    auto: [
      "N5 基礎單字", "N4 常用單字", "日常生活の動詞", "形容詞（い・な形）", "家族と人",
      "食べ物と飲み物", "時間と日付", "場所と方向", "体と健康", "天気と季節",
      "あいさつと丁寧表現", "神社・お寺の基礎語", "日本の祭りと行事", "数と助数詞", "学校と仕事",
    ],
  },
  // 德文（A1 初學）：A1 高頻字＋日常生活，隨程度再帶宗教／神話題材
  de: {
    presets: ["A1 高頻字", "日常生活名詞", "規則動詞現在式", "der/die/das 常見名詞", "數字與時間", "家庭與人"],
    auto: [
      "A1 高頻字（前 100）", "常用規則動詞", "sein／haben 與情態動詞", "家庭與人",
      "食物與飲料", "數字・時間・日期", "城市與方向", "身體與健康", "天氣與季節",
      "問候與禮貌用語", "der/die/das 常見名詞（含複數）", "形容詞與顏色",
      "教堂與節慶基礎字", "宗教改革與神學基礎詞", "旅遊與交通",
    ],
  },
  // 法文（A1 初學）：A1 高頻字＋日常生活，隨程度再帶宗教／神話題材
  fr: {
    presets: ["A1 高頻字", "日常生活名詞", "-er 動詞現在式", "le/la/un/une 常見名詞", "數字與時間", "家庭與人"],
    auto: [
      "A1 高頻字（前 100）", "常用 -er 動詞", "être／avoir 與基本動詞", "家庭與人",
      "食物與飲料", "數字・時間・日期", "城市與方向", "身體與健康", "天氣與季節",
      "問候與禮貌用語", "陰陽性常見名詞（含冠詞）", "形容詞與顏色",
      "大教堂與節慶基礎字", "天主教與神學基礎詞", "旅遊與交通",
    ],
  },
  // 通用希臘文（Koine，入門）：題材＝新約／LXX／教父／信經／希臘化猶太／哲學家／拜占庭
  grc: {
    presets: ["新約高頻字", "約翰福音核心字", "希臘文冠詞與代名詞", "信經關鍵詞", "七十士譯本基礎字", "教父文獻常用字"],
    auto: [
      "新約高頻字（前 100）", "新約高頻動詞", "希臘文冠詞・代名詞・連接詞", "介系詞與小品詞",
      "約翰福音核心字彙", "馬可福音核心字彙", "七十士譯本（LXX）創世記基礎字", "詩篇（LXX）常用字",
      "使徒教父常用字", "尼西亞信經關鍵詞", "大公會議神學術語（οὐσία／ὑπόστασις…）",
      "斐羅與希臘化猶太文獻常用字", "希臘化哲學常用字（斯多噶／柏拉圖）", "拜占庭教會與官方文獻常用字",
      "基督教禮儀與敬拜詞彙",
    ],
  },
  // 教會拉丁文（Ecclesiastical，入門）：武加大／拉丁教父 → 經院神哲學 → 中世紀各學科
  la: {
    presets: ["武加大高頻字", "福音書常用字", "拉丁文代名詞與介系詞", "信經與禮儀關鍵詞", "拉丁教父常用字", "經院神學術語"],
    auto: [
      "武加大（Vulgata）高頻字", "武加大高頻動詞", "拉丁文代名詞・連接詞・介系詞",
      "福音書核心字彙", "詩篇（武加大）常用字", "使徒信經與尼西亞信經關鍵詞",
      "拉丁教父常用字（奧古斯丁／耶柔米）", "禮儀與彌撒常用字", "大公會議與教令術語",
      "經院神學術語（ens／esse／essentia／substantia…）", "阿奎那《神學大全》常見詞",
      "經院哲學邏輯術語（quaestio／ratio／accidens…）", "教會法（canon law）常用字",
      "中世紀大學與七藝常用字", "聖徒傳與編年史常用字",
    ],
  },
  // 聖經希伯來文（Biblical，入門）：以舊約為起點，擴及昆蘭／拉比／中世紀註釋
  hbo: {
    presets: ["創世記常用字", "舊約高頻字", "希伯來文代名詞與介係詞", "詩篇常用字", "動詞 binyanim 入門", "聖經人名與地名"],
    auto: [
      "舊約（Tanakh）高頻字（前 100）", "創世記核心字彙", "出埃及記核心字彙", "詩篇常用字",
      "希伯來文代名詞・介係詞・冠詞", "連接詞 vav 與敘述式", "常用三母音字根",
      "動詞詞幹 binyanim（Qal／Niphal／Piel…）入門", "先知書常用字", "智慧文學（箴言／約伯）常用字",
      "聖殿與禮儀詞彙", "死海古卷（昆蘭）常用字", "米示拿／拉比希伯來文入門字",
      "中世紀希伯來文聖經註釋常用字", "聖經人名與地名",
    ],
  },
  // ── 新增語言（2026-06-20）：宗教研究取向主題 ──
  es: { presets: ["A1 高頻字", "日常生活名詞", "ser／estar 與動詞", "陰陽性常見名詞", "天主教與聖週基礎詞", "數字與時間"],
    auto: ["A1 高頻字（前 100）", "常用 -ar 動詞", "ser／estar 與基本動詞", "家庭與人", "食物與飲料", "城市與方向", "天主教與聖週詞彙", "聖經西譯基礎詞", "拉美宗教詞彙", "旅遊與交通"] },
  att: { presets: ["荷馬高頻字", "古典希臘冠詞與代名詞", "希臘神話神名", "柏拉圖哲學術語", "悲劇常用字", "祕儀宗教詞彙"],
    auto: ["荷馬史詩高頻字", "古典散文高頻字", "冠詞・代名詞・小品詞", "希臘神話神名與譜系", "柏拉圖哲學術語（ἀρετή／ψυχή／εἶδος）", "前蘇格拉底哲人術語", "悲劇與抒情詩常用字", "厄琉息斯/奧菲斯祕儀詞彙", "願望語氣與條件句動詞", "荷馬式形容詞"] },
  chu: { presets: ["禮儀高頻字", "福音書常用字", "詩篇常用字", "信經關鍵詞", "教會西里爾字母詞", "東正教神學詞"],
    auto: ["福音書核心字彙", "詩篇（Псалтырь）常用字", "事奉聖禮常用字", "主禱文與信經關鍵詞", "教父譯文常用字", "名詞七格與雙數", "動詞 aorist／imperfect", "titlo 縮寫詞", "東正教節期詞彙", "繫詞 быти 與基本動詞"] },
  arc: { presets: ["但以理書常用字", "亞蘭文代名詞與介係詞", "塔古姆常用字", "emphatic state 名詞", "動詞詞幹入門", "聖經亞蘭文高頻字"],
    auto: ["但以理書 2–7 章字彙", "以斯拉記亞蘭文段落", "Onkelos 塔古姆常用字", "亞蘭文代名詞・介係詞", "動詞詞幹 peal／pael／haphel", "emphatic state（-א）名詞", "與希伯來同源字對照", "象島蒲草常用字", "巴比倫塔木德亞蘭文入門", "亞蘭文數字與時間"] },
  mid: { presets: ["曼達字母詞", "《金茲拉巴》常用字", "諾斯底宇宙論詞彙", "洗禮禮儀詞", "亞蘭同源詞", "曼達神名"],
    auto: ["曼達字母與母音字母", "《金茲拉巴》核心字彙", "《約翰書》常用字", "光明界／黑暗界二元詞彙", "洗禮（masbuta）禮儀詞", "救贖者神話詞彙", "與亞蘭文同源詞", "曼達教祭司術語", "覺知（gnosis）相關詞", "曼達神祇與精靈名"] },
  syr: { presets: ["Peshitta 高頻字", "Estrangela 字母詞", "聖以法蓮常用字", "敘利亞文代名詞", "動詞詞幹入門", "景教文獻常用字"],
    auto: ["Peshitta 福音書核心字", "Estrangela 字母與母音", "聖以法蓮教義詩常用字", "敘利亞文代名詞・介係詞", "動詞詞幹 pʿal／paʿʿel／aphʿel", "emphatic state 名詞", "東/西兩傳統發音對照", "東方教會（景教）文獻字彙", "禮儀與神學術語", "與亞蘭文同源字"] },
  cop: { presets: ["科普特字母詞", "薩希德聖經常用字", "《多馬福音》常用字", "動詞時態前綴", "沙漠教父語彙", "諾斯底術語"],
    auto: ["科普特字母（含世俗體字母）", "薩希德福音書核心字", "《多馬福音》與納戈瑪第字彙", "動詞時態前綴系統", "定/不定冠詞與屬格", "沙漠教父修道語彙", "諾斯底神學術語", "聖薛努特講道常用字", "與希臘借詞", "科普特數字"] },
  gez: { presets: ["fidäl 音節文字詞", "吉茲聖經常用字", "《以諾書》字彙", "三母音字根", "衣索比亞正教詞", "詩篇常用字"],
    auto: ["fidäl 音節文字（基本階）", "吉茲文聖經福音書核心字", "《以諾一書》常用字", "《禧年書》字彙", "三母音字根（對照閃語）", "動詞詞型 G／D／L", "Kebra Nagast 字彙", "衣索比亞正教禮儀詞", "構造狀態名詞", "吉茲數字"] },
  hy: { presets: ["Mesrop 字母詞", "亞美尼亞聖經常用字", "名詞七格", "教父譯文字彙", "史著常用字", "教會術語"],
    auto: ["Mesrop 字母與發音", "亞美尼亞文聖經福音書核心字", "名詞七格與冠詞後綴", "動詞變位常用字", "教父譯文（僅存亞美尼亞譯）字彙", "Movses Khorenatsi 史著字彙", "亞美尼亞使徒教會術語", "Agathangelos 常用字", "與希臘借詞", "亞美尼亞數字"] },
  ka: { presets: ["Asomtavruli 字母詞", "古喬治亞聖經常用字", "多人稱動詞", "名詞格位", "聖徒傳字彙", "教會術語"],
    auto: ["Asomtavruli／Nuskhuri 字母", "古喬治亞文聖經福音書核心字", "多人稱記號動詞（主＋賓）", "名詞七格", "時態系列 screeves", "《Shushanik 殉道記》字彙", "喬治亞正教禮儀詞", "苦修文獻譯本字彙", "前綴與後綴標記", "喬治亞數字"] },
  akk: { presets: ["楔形轉寫高頻字", "《吉爾伽美什》字彙", "《埃努瑪埃利什》字彙", "動詞詞幹 G/D/Š/N", "名詞格位", "美索神名"],
    auto: ["阿卡德轉寫高頻字", "《埃努瑪‧埃利什》創世史詩字彙", "《吉爾伽美什》史詩字彙", "《阿特拉哈西斯》洪水字彙", "動詞詞幹 G／D／Š／N", "名詞格位與狀態", "決定符（determinatives）", "巴比倫／亞述方言差異詞", "《漢摩拉比法典》術語", "美索不達米亞神名"] },
  uga: { presets: ["烏加列字母詞", "《巴力史詩》字彙", "迦南神名", "三母音字根", "詩歌對句詞", "獻祭術語"],
    auto: ["烏加列 30 符字母", "《巴力史詩》核心字彙", "《Kirta》《Aqhat》史詩字彙", "迦南神名（El／Baal／Anat／Asherah）", "三母音字根（對照希伯來）", "西北閃語平行詩體詞", "獻祭與神名表字彙", "動詞詞幹與時態", "與希伯來同源字", "烏加列名詞格位"] },
  egy: { presets: ["聖書體轉寫詞", "《亡靈書》字彙", "埃及神名", "sḏm.f 動詞句", "來世觀詞彙", "瑪阿特相關詞"],
    auto: ["中古埃及語轉寫高頻字", "《亡靈書》核心字彙", "金字塔文／棺槨文字彙", "《阿吞讚歌》字彙", "埃及神名（Ra／Osiris／Isis／Amun）", "sḏm.f 動詞句型詞", "來世觀與審判詞彙", "瑪阿特（Maat）相關詞", "決定符類別", "神廟與祭儀術語"] },
  phn: { presets: ["腓尼基字母詞", "腓尼基銘文常用字", "迦南神名", "三母音字根", "獻祭術語", "布匿宗教詞"],
    auto: ["腓尼基 22 字母", "Aḥiram／Kilamuwa 銘文字彙", "迦南神名（Baal／Astarte／Melqart／Tanit）", "三母音字根（對照希伯來）", "獻祭碑套語", "布匿（迦太基）宗教詞彙", "字母演化對照（希臘/希伯來）", "名詞性數狀態", "與希伯來同源字", "腓尼基數字"] },
  peo: { presets: ["古波斯楔形轉寫詞", "貝希斯敦銘文字彙", "王室宗教詞", "名詞格位", "阿胡拉馬茲達相關詞", "王權術語"],
    auto: ["古波斯楔形轉寫高頻字", "貝希斯敦銘文核心字", "王室銘文套語（adam…xšāyaθiya）", "阿胡拉‧馬茲達與宗教詞彙", "名詞格位與性數", "動詞變位常用字", "與阿維斯陀同源字", "與梵文同源字", "王權神授（xšaça）詞", "阿契美尼德地名人名"] },
  ae: { presets: ["阿維斯陀字母詞", "《迦薩》核心字", "祆教神學術語", "禱文常用字", "名詞八格", "與梵文同源字"],
    auto: ["阿維斯陀字母與轉寫", "《迦薩》(Gathas) 核心字彙", "Ahuna Vairya／Ashem Vohu 禱文字", "祆教神學（Ahura Mazdā／Aṣ̌a／Aməṣ̌a Spəṇta）", "《亞斯納》《耶斯特》禮儀字彙", "名詞八格與性數", "與梵文同源字（連音對照）", "巴列維 Zand 註釋詞", "二元論（善惡靈）詞彙", "祆教祭儀術語"] },
  ar: { presets: ["古蘭高頻字", "阿拉伯字母詞", "三母音字根", "動詞 I–X 型", "伊斯蘭神學術語", "古蘭短章字彙"],
    auto: ["古蘭經高頻字", "阿拉伯字母與連寫變形", "三母音字根與詞型（awzān）", "動詞 I–X 型", "名詞 i‘rāb 三格", "開端章與短章字彙", "聖訓（ḥadīth）常用字", "kalām 神學術語", "falsafa 哲學術語（金迪/伊本西那）", "基督教阿拉伯文獻字彙"] },
  sa: { presets: ["天城體與 IAST", "《薄伽梵歌》字彙", "佛教梵語術語", "名詞八格", "連音 sandhi", "奧義書術語"],
    auto: ["梵文高頻字（天城體＋IAST）", "《薄伽梵歌》核心字彙", "《心經》《金剛經》梵本字彙", "佛教術語（dharma／śūnyatā／bodhi）", "名詞八格三數三性", "連音 sandhi 規則詞", "動詞十類現在系統", "奧義書哲學術語", "複合詞（samāsa）詞例", "吠陀梵語特有詞"] },
  pi: { presets: ["巴利轉寫高頻字", "《法句經》字彙", "佛教術語", "名詞格位", "尼柯耶常用字", "與梵文對照"],
    auto: ["巴利文高頻字（羅馬轉寫）", "《法句經》核心字彙", "四部尼柯耶常用字", "佛教術語（dhamma／dukkha／anattā／nibbāna）", "名詞格位與性數", "動詞變位常用字", "《經集》字彙", "護衛經（paritta）字彙", "與梵文同源對照", "《清淨道論》術語"] },
  bo: { presets: ["藏文字母與 Wylie", "《心經》藏文字彙", "佛教術語", "格助詞", "甘珠爾常用字", "作格句法詞"],
    auto: ["藏文字母與 Wylie 轉寫", "《心經》《入菩薩行論》藏文字彙", "佛教術語（梵—藏—漢對照）", "格助詞（屬/具/位/離格）", "作格（ergative）句法詞", "甘珠爾（佛說部）常用字", "丹珠爾（論疏部）術語", "敬語與佛典套語", "中觀／唯識術語", "藏文數字"] },
  pra: { presets: ["俗語轉寫詞", "耆那《阿含經》字彙", "耆那教術語", "梵→俗音變詞", "名詞格位", "與梵巴對照"],
    auto: ["半摩揭陀俗語高頻字", "《行為經》(Ācārāṅga) 核心字", "耆那教術語（jīva／ahiṃsā／kevala-jñāna）", "梵→俗音變規則詞", "名詞格位與性數", "動詞變位常用字", "與梵文／巴利對照詞", "白衣派聖典字彙", "偈頌格律詞", "耆那宇宙論詞彙"] },
  lzh: { presets: ["文言虛詞", "漢譯佛典術語", "道家經典字", "儒家經典字", "通假字辨析", "句讀斷句詞"],
    auto: ["文言虛詞（之乎者也而以於其）", "漢譯佛典譯經體語彙", "《心經》《金剛經》術語", "《六祖壇經》禪宗術語", "道家《老子》《莊子》字彙", "儒家《論語》《孟子》字彙", "通假字與古今字", "文言句法（判斷/被動/使動意動）", "《道藏》專詞", "訓詁常用詞"] },
  nan: { presets: ["台語高頻詞", "聲調與變調", "文白異讀字", "廟宇民間信仰詞", "白話字聖經詞", "日常生活詞"],
    auto: ["台語高頻詞（漢字＋羅馬字）", "聲調與變調規則詞", "文白異讀字例", "日常生活與家庭", "食物與市場", "廟宇與民間信仰詞彙", "媽祖遶境節慶詞", "巴克禮台語聖經詞", "白話字文獻常用字", "俗諺與慣用語"] },
  hak: { presets: ["客語高頻詞", "四縣腔聲調", "民間信仰詞", "白話字聖經詞", "日常生活詞", "俗諺"],
    auto: ["客語高頻詞（漢字＋羅馬字）", "四縣腔聲調詞", "日常生活與家庭", "食物與市場", "伯公與民間信仰詞彙", "義民祭節慶詞", "客語聖經詞", "白話字文獻常用字", "四縣/海陸腔差異詞", "俗諺與慣用語"] },
  ami: { presets: ["阿美語高頻詞", "族語書寫字母", "焦點系統詞", "豐年祭詞彙", "口傳神話詞", "親屬稱謂"],
    auto: ["阿美語高頻詞（族語書寫）", "族語書寫系統字母與拼讀", "焦點系統（主事/受事…）詞", "代名詞與格位標記", "海洋與採集生活詞", "豐年祭（Ilisin）詞彙", "口傳神話與創世故事詞", "阿美語聖經詞", "親屬稱謂", "傳統信仰（kawas）詞彙"] },
  tay: { presets: ["泰雅語高頻詞", "族語書寫字母", "焦點系統詞", "gaga 規範詞", "祖靈信仰詞", "親屬稱謂"],
    auto: ["泰雅語高頻詞（族語書寫）", "族語書寫系統字母與拼讀", "焦點系統與語序詞", "代名詞與格位標記", "山林狩獵織布生活詞", "gaga／gaya 傳統規範詞", "祖靈 utux 與彩虹橋傳說詞", "泰雅語聖經詞", "親屬稱謂", "賽考利克/澤敖利方言差異詞"] },
};
const pool = computed(() => THEME_POOLS[language.value] || THEME_POOLS.en);

// 共用預備字庫的真實分類（每語言）；有就用、每天輪替一批顯示，沒有則 fallback 到內建 presets。
const bankCats = ref<string[]>([]);
async function loadBankCats() {
  try {
    const { categories } = await authedFetch<{ categories: { category: string; count: number }[] }>(
      `/api/lang/vocab/categories?language=${language.value}`,
    );
    bankCats.value = (categories || []).map((c) => c.category);
  } catch {
    bankCats.value = [];
  }
}
// 每日輪替（台北本地日期種子；同天穩定、隔天換一批標籤）
function daySeed() {
  return parseInt(new Date().toLocaleDateString("en-CA").replace(/-/g, ""), 10) || 0;
}
function rotateDaily(arr: string[], take: number) {
  if (!arr.length) return arr;
  const start = daySeed() % arr.length;
  const out: string[] = [];
  for (let i = 0; i < Math.min(take, arr.length); i++) out.push(arr[(start + i) % arr.length]);
  return out;
}
const PRESETS = computed(() => (bankCats.value.length ? rotateDaily(bankCats.value, 8) : pool.value.presets));
const TTS_LANG: Record<string, string> = { en: "en-US", de: "de-DE", fr: "fr-FR", es: "es-ES", ja: "ja-JP", grc: "el-GR", att: "el-GR", la: "it-IT", hbo: "he-IL", arc: "he-IL", chu: "ru-RU", syr: "ar-SY", cop: "ar-EG", gez: "am-ET", hy: "hy-AM", ka: "ka-GE", ar: "ar-SA", akk: "ar-IQ", uga: "ar-SY", egy: "ar-EG", phn: "ar-LB", peo: "fa-IR", ae: "fa-IR", mid: "ar-IQ", sa: "hi-IN", pi: "hi-IN", pra: "hi-IN", bo: "bo", lzh: "zh-TW", nan: "zh-TW", hak: "zh-TW", ami: "zh-TW", tay: "zh-TW" };

const route = useRoute();
const language = computed(() => route.params.lang as string);
const queue = ref<any[]>([]);
const revealed = ref(false);
const reviewed = ref(0);
const loading = ref(true);
const theme = ref("");
const generating = ref(false);
const genMsg = ref("");
const speech = useSpeech();
const mode = ref<"quiz" | "flip" | "cloze">("quiz"); // 預設選擇題
const picked = ref<string | null>(null);

// ── 克漏字模式 ──
const clozeInput = ref("");
const clozeChecked = ref(false);
const clozeCorrect = ref(false);
const normWord = (s: string) => (s || "").toLowerCase().trim().replace(/[^\p{L}\p{N}'’\- ]/gu, "");
// 例句中把目標字挖空（不分大小寫、整詞）
const clozeSentence = computed(() => {
  const c = current.value;
  if (!c?.example || !c?.word) return "";
  const re = new RegExp(`\\b${c.word.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\b`, "gi");
  return c.example.replace(re, "_____");
});
async function checkCloze() {
  if (clozeChecked.value || !clozeInput.value.trim()) return;
  const c = current.value;
  clozeChecked.value = true;
  clozeCorrect.value = normWord(clozeInput.value) === normWord(c.word);
  try {
    await authedFetch("/api/lang/vocab/review", { method: "POST", body: { id: c.id, quality: clozeCorrect.value ? 4 : 2 } });
  } catch { /* ignore */ }
}
function resetCloze() {
  clozeInput.value = "";
  clozeChecked.value = false;
  clozeCorrect.value = false;
}

// ── 無限刷題模式 ──
const endless = ref(true);          // 預設開：刷完自動生成新單字
const topping = ref(false);         // 正在背景補題
const seen = new Set<string>();     // 本次 session 已出現過的卡片 id（避免馬上重複）
let themeIdx = 0;
const LOW_WATER = 4;                 // 佇列剩這麼少就先補題（預抓，藏延遲）

const current = computed(() => queue.value[0] || null);

function optionClass(opt: string) {
  if (picked.value === null) return "border-gray-200 text-gray-700 hover:border-indigo-300";
  if (opt === current.value.meaning) return "border-emerald-300 bg-emerald-50 text-emerald-700";
  if (opt === picked.value) return "border-rose-300 bg-rose-50 text-rose-600";
  return "border-gray-100 text-gray-400";
}

// 選擇題作答：對→good(4)、錯→again(2，排進複習)
async function answer(opt: string) {
  if (picked.value !== null) return;
  picked.value = opt;
  const card = current.value;
  const q = opt === card.meaning ? 4 : 2;
  try {
    await authedFetch("/api/lang/vocab/review", { method: "POST", body: { id: card.id, quality: q } });
  } catch { /* ignore */ }
}

function next() {
  queue.value.shift();
  picked.value = null;
  resetCloze();
  reviewed.value++;
  maybeTopUp();
}

// 抓佇列；append=true 只把「沒出現過的」新卡接到尾端（無限模式用），保留進度
async function loadQueue(append = false) {
  const { due } = await authedFetch<{ due: any[] }>(`/api/lang/vocab/review?language=${language.value}&limit=40`);
  const fresh = (due || []).filter((c) => !seen.has(c.id));
  for (const c of fresh) seen.add(c.id);
  if (append) queue.value.push(...fresh);
  else queue.value = fresh;
  return fresh.length;
}

async function reload() {
  loading.value = true;
  revealed.value = false;
  picked.value = null;
  reviewed.value = 0;
  seen.clear();
  await loadQueue(false);
  loading.value = false;
}

// 無限模式核心：佇列見底就自動生成一批新學術單字（走 NVIDIA，免費）接上去
async function replenish() {
  if (!endless.value || topping.value) return;
  topping.value = true;
  try {
    const themes = bankCats.value.length ? bankCats.value : pool.value.auto;
    const theme = themes[themeIdx % themes.length];
    themeIdx++;
    await aiFetch("/api/lang/vocab/generate", {
      method: "POST",
      body: { language: language.value, theme, count: 15 },
    });
    await loadQueue(true); // 把新生成的（未出現過的）接到佇列尾
  } catch {
    /* 生成失敗就算了，next 次再試 */
  } finally {
    topping.value = false;
  }
}

// 佇列偏低就預先補題（藏住生成延遲，讓刷題不中斷）
function maybeTopUp() {
  if (endless.value && !topping.value && queue.value.length <= LOW_WATER) replenish();
}

async function grade(q: number) {
  const card = current.value;
  if (!card) return;
  queue.value.shift();
  revealed.value = false;
  resetCloze();
  reviewed.value++;
  maybeTopUp();
  try {
    await authedFetch("/api/lang/vocab/review", { method: "POST", body: { id: card.id, quality: q } });
  } catch {
    /* 失敗就算了，下次到期再複習 */
  }
}

function speak() {
  if (current.value) speech.speak(current.value.word, TTS_LANG[language.value] || "en-US");
}

async function generate() {
  generating.value = true;
  genMsg.value = "";
  try {
    const res = await aiFetch<any>("/api/lang/vocab/generate", {
      method: "POST",
      body: { language: language.value, theme: theme.value, count: 15 },
    });
    genMsg.value = `已加入 ${res.added} 個新單字（${res.theme}），開始複習吧！`;
    await reload();
  } catch (e: any) {
    genMsg.value = e?.data?.message || "生成失敗";
  } finally {
    generating.value = false;
  }
}

// 佇列被刷空時（預抓沒跟上）→ 立刻補題；開啟無限開關時若正好空了也補
watch([current, endless], ([cur, on]) => {
  if (on && !cur && !loading.value && !topping.value) replenish();
});

// 進到新單字卡 → 自動念一次（翻卡＋選擇題都套用；瀏覽器不支援 TTS 則略過）
// 只在卡片真的「換成另一張」時觸發（比對 id），翻卡顯示答案不會重念。
watch(current, (cur, prev) => {
  if (mode.value === "cloze") return; // 克漏字不自動念（會洩漏答案）
  if (cur?.word && cur.id !== prev?.id && speech.ttsSupported.value) speak();
});

onMounted(() => {
  tracker.start(language.value, "reading", "vocab"); // 複習計入「讀」時間，從進頁開始算
  loadBankCats();
  reload();
});
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from,
.fade-leave-to { opacity: 0; }
</style>
