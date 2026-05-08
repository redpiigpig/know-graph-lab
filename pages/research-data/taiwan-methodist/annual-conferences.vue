<template>
  <div class="min-h-screen bg-slate-50">

    <nav class="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div class="max-w-6xl mx-auto px-6 h-14 flex items-center gap-4">
        <NuxtLink to="/research-data/taiwan-methodist" class="text-gray-400 hover:text-gray-700 transition text-sm">← 台灣衛理公會研究資料</NuxtLink>
        <span class="text-gray-200">|</span>
        <span class="text-sm font-medium text-gray-700">年議會歷屆大會名表</span>
      </div>
    </nav>

    <div class="max-w-6xl mx-auto px-6 py-8">

      <!-- 標題 -->
      <div class="mb-6">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-teal-100 text-teal-700">研究資料</span>
          <span class="text-xs text-gray-400">台灣衛理公會</span>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 mb-1">年議會歷屆大會日期、地點及主持人名表</h1>
        <p class="text-sm text-gray-500">自 1956 年臺港臨時年議會第一屆起，至 2023 年中華年議會第六十屆為止，共 {{ records.length }} 筆會議紀錄。</p>
      </div>

      <!-- 出處 -->
      <div class="mb-6 p-4 rounded-xl bg-white border border-gray-100 text-xs text-gray-600 leading-relaxed">
        <span class="text-gray-400 mr-1">出處</span>
        中華基督教衛理公會總會編，《中華基督教衛理公會第六十屆年議會大會會議紀錄》（台北市：中華基督教衛理公會總會，2023 年 5 月，發行人：黃寬裕），頁 242-245。
      </div>

      <!-- 篩選 -->
      <div class="bg-white rounded-2xl border border-gray-100 p-4 mb-4 flex flex-col sm:flex-row gap-3">
        <div class="flex flex-wrap gap-2">
          <button
            v-for="t in typeFilters" :key="t.id"
            @click="activeType = t.id"
            :class="['px-3 py-1.5 text-xs font-medium rounded-full border transition', activeType === t.id ? 'bg-teal-600 border-teal-600 text-white' : 'bg-white border-gray-200 text-gray-600 hover:border-teal-300']"
          >
            {{ t.label }}
            <span class="ml-1 opacity-70">{{ t.count }}</span>
          </button>
        </div>
        <input
          v-model="search"
          type="text"
          placeholder="搜尋屆次／地點／主席／書記…"
          class="flex-1 sm:max-w-xs px-3 py-2 border border-gray-200 rounded-xl text-sm outline-none focus:ring-2 focus:ring-teal-400"
        />
      </div>

      <!-- 表格 -->
      <div class="bg-white rounded-2xl border border-gray-100 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full text-sm">
            <thead class="bg-slate-100 text-gray-600 text-xs uppercase tracking-wider">
              <tr>
                <th class="px-3 py-2.5 text-left font-medium whitespace-nowrap">會別</th>
                <th class="px-3 py-2.5 text-left font-medium whitespace-nowrap">屆次</th>
                <th class="px-3 py-2.5 text-left font-medium whitespace-nowrap">地點</th>
                <th class="px-3 py-2.5 text-left font-medium whitespace-nowrap">會期</th>
                <th class="px-3 py-2.5 text-left font-medium whitespace-nowrap">主席</th>
                <th class="px-3 py-2.5 text-left font-medium whitespace-nowrap">書記</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="(r, i) in filtered" :key="i" class="hover:bg-teal-50/40">
                <td class="px-3 py-2.5 align-top whitespace-nowrap text-gray-500">{{ r.type }}</td>
                <td class="px-3 py-2.5 align-top whitespace-nowrap text-gray-900 font-medium">{{ r.session }}</td>
                <td class="px-3 py-2.5 align-top text-gray-700">{{ r.location }}</td>
                <td class="px-3 py-2.5 align-top text-gray-700">{{ r.date }}</td>
                <td class="px-3 py-2.5 align-top whitespace-nowrap text-gray-900">{{ r.chair }}</td>
                <td class="px-3 py-2.5 align-top text-gray-700">{{ r.secretary }}</td>
              </tr>
              <tr v-if="!filtered.length">
                <td colspan="6" class="px-3 py-10 text-center text-gray-400 text-sm">沒有符合條件的紀錄</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <p class="mt-4 text-xs text-gray-400">
        顯示 {{ filtered.length }} / {{ records.length }} 筆
      </p>

    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' });
useHead({ title: '台灣衛理公會年議會歷屆大會 — Know Graph Lab' });

interface ConferenceRecord {
  type: '臺港臨時年議會' | '臺灣臨時年議會' | '中華年議會';
  session: string;
  location: string;
  date: string;
  chair: string;
  secretary: string;
}

const records: ConferenceRecord[] = [
  { type: '臺港臨時年議會', session: '第一屆', location: '香港北角衛理堂', date: '一九五六年十二月六日至九日', chair: '黃安素', secretary: '周福全 許可傾' },
  { type: '臺港臨時年議會', session: '第二屆', location: '台北衛理堂', date: '一九五七年十二月廿七日至卅一日', chair: '黃安素 (駐區會督)', secretary: '彭傳經 許可傾' },
  { type: '臺港臨時年議會', session: '第三屆', location: '香港北角衛理堂', date: '一九五八年十二月四日至七日', chair: '黃安素(主席職員) 周郁晞 聶樹德', secretary: '彭傳經 許可傾' },
  { type: '臺港臨時年議會', session: '第四屆', location: '台北衛理堂', date: '一九五九年十月廿一日至廿五日', chair: '基雅德', secretary: '彭傳經 許可傾' },
  { type: '臺港臨時年議會', session: '第五屆', location: '香港北角衛理堂', date: '一九六〇年十月廿三日至廿七日', chair: '施梅士', secretary: '李廷英 唐樂仁' },
  { type: '臺港臨時年議會', session: '第六屆', location: '台北衛理福音園', date: '一九六一年十月廿七日至廿九日', chair: '柯遜', secretary: '李廷英 唐樂仁' },
  { type: '臺港臨時年議會', session: '第七屆', location: '香港北角衛理堂', date: '一九六二年十一月廿一日至廿五日', chair: '柯遜', secretary: '梁林開 唐樂仁' },

  { type: '臺灣臨時年議會', session: '第一屆', location: '台北衛理福音園', date: '一九六三年十一月一日至三日', chair: '芮理查', secretary: '吳承禧 許可傾' },
  { type: '臺灣臨時年議會', session: '第二屆', location: '台北衛理福音園', date: '一九六四年九月廿四日至廿六日', chair: '華納', secretary: '吳承禧 許可傾' },
  { type: '臺灣臨時年議會', session: '第三屆', location: '台中東海大學', date: '一九六五年十月廿二日至廿四日', chair: '華納', secretary: '吳承禧 許可傾' },
  { type: '臺灣臨時年議會', session: '第四屆', location: '台北東吳大學', date: '一九六六年九月卅日至十月二日', chair: '華納', secretary: '吳承禧 許可傾' },
  { type: '臺灣臨時年議會', session: '第五屆', location: '台北衛理福音園', date: '一九六七年十月六日至十月八日', chair: '華納', secretary: '吳承禧 許可傾' },
  { type: '臺灣臨時年議會', session: '第六屆', location: '台北衛理福音園', date: '一九六八年十月十八日至廿日', chair: '羅愛徒', secretary: '魏元珪 鄧克禮' },
  { type: '臺灣臨時年議會', session: '第七屆', location: '台北衛理福音園', date: '一九六九年六月廿六日至廿九日', chair: '羅愛徒', secretary: '高雄 鄧克禮' },
  { type: '臺灣臨時年議會', session: '第七屆特別議會', location: '台北衛理堂', date: '一九六九年十二月五日至六日', chair: '羅愛徒', secretary: '高雄 鄧克禮' },
  { type: '臺灣臨時年議會', session: '第八屆', location: '台北東吳大學', date: '一九七〇年七月廿四日至廿六日', chair: '羅愛徒', secretary: '高雄 許可傾' },
  { type: '臺灣臨時年議會', session: '第九屆', location: '台北衛理福音園', date: '一九七一年七月八至十一日', chair: '羅愛徒', secretary: '吳承禧 吳劍秋' },
  { type: '臺灣臨時年議會', session: '第十屆', location: '台北衛理福音園', date: '一九七二年三月卅一日至四月二日', chair: '羅愛徒', secretary: '吳承禧 吳劍秋' },

  { type: '中華年議會', session: '第十一屆', location: '台北衛理福音園', date: '民國六十二年七月十九日至廿二日', chair: '劉子哲', secretary: '吳承禧' },
  { type: '中華年議會', session: '第十二屆', location: '台北衛理福音園', date: '民國六十三年六月廿八日至三十日', chair: '劉子哲', secretary: '周鴻章' },
  { type: '中華年議會', session: '第十三屆', location: '台北衛理福音園', date: '民國六十四年七月十日至十三日', chair: '劉子哲', secretary: '周鴻章' },
  { type: '中華年議會', session: '第十四屆', location: '台北衛理福音園', date: '民國六十五年七月十五日至十八日', chair: '劉子哲', secretary: '周鴻章' },
  { type: '中華年議會', session: '第十五屆', location: '台北衛理福音園', date: '民國六十六年七月十四日至十七日', chair: '劉子哲', secretary: '李棟臣' },
  { type: '中華年議會', session: '第十六屆', location: '台北衛理福音園', date: '民國六十七年七月廿一日至廿三日', chair: '吳承禧', secretary: '林述鼎' },
  { type: '中華年議會', session: '第十七屆', location: '淡水聖本篤修道院', date: '民國六十九年七月廿八日至卅一日', chair: '會務整理委員', secretary: '郝文章' },
  { type: '中華年議會', session: '第十八屆', location: '台北東吳大學', date: '民國七十年七月九至十二日', chair: '吳英武', secretary: '林述鼎' },
  { type: '中華年議會', session: '第十九屆', location: '台北衛理女中', date: '民國七十一年八月五日至八日', chair: '吳英武', secretary: '林述鼎' },
  { type: '中華年議會', session: '第二十屆', location: '台北東吳大學', date: '民國七十二年七月十九日至廿四日', chair: '吳英武', secretary: '黃建華 林拔高' },
  { type: '中華年議會', session: '第二十一屆', location: '台北衛理福音園', date: '民國七十三年七月十七日至廿日', chair: '吳英武', secretary: '廖紀榮 吳承禧' },
  { type: '中華年議會', session: '第二十二屆', location: '台北衛理福音園', date: '民國七十四年七月十六日至十八日', chair: '張保羅', secretary: '吳承禧 曾紀平' },
  { type: '中華年議會', session: '第二十三屆', location: '台北衛理福音園', date: '民國七十五年七月九日至十一日', chair: '張保羅', secretary: '吳承禧 林季博' },
  { type: '中華年議會', session: '第二十四屆', location: '台北衛理福音園', date: '民國七十六年七月十五日至十六日', chair: '黃建華', secretary: '郝文章 曾紀平' },
  { type: '中華年議會', session: '第二十五屆', location: '台北衛理福音園', date: '民國七十七年七月十八日至二十日', chair: '黃建華', secretary: '吳承禧 鍾思波' },
  { type: '中華年議會', session: '第二十六屆臨時年議會', location: '台北衛理福音園', date: '民國七十八年五月六日', chair: '黃建華', secretary: '郝文章 曾紀平' },
  { type: '中華年議會', session: '第二十六屆', location: '台北衛理福音園', date: '民國七十八年七月十七日至十八日', chair: '黃建華', secretary: '郝文章 曾紀平' },
  { type: '中華年議會', session: '第二十七屆', location: '台北衛理福音園', date: '民國七十九年七月五日至七日', chair: '黃建華', secretary: '曾紀鴻 許珂' },
  { type: '中華年議會', session: '第二十八屆', location: '台北衛理福音園', date: '民國八十年七月十五日至十六日', chair: '黃建華', secretary: '陳家厚 曾長森' },
  { type: '中華年議會', session: '第二十九屆臨時年議會', location: '台北衛理福音園', date: '民國八十一年四月二十日至廿一日', chair: '黃建華', secretary: '林長贈 蔡敏勝' },
  { type: '中華年議會', session: '第二十九屆', location: '台北衛理福音園', date: '民國八十一年七月十五日至十七日', chair: '黃建華', secretary: '林長贈 蔡敏勝' },
  { type: '中華年議會', session: '第三十屆', location: '台北衛理福音園', date: '民國八十二年七月十五日至十六日', chair: '伍秉衡', secretary: '陳家厚 汪鵬聰' },
  { type: '中華年議會', session: '第三十一屆', location: '台北衛理福音園', date: '民國八十三年七月十九日至二十日', chair: '伍秉衡', secretary: '謝榮生 林中立' },
  { type: '中華年議會', session: '第三十二屆臨時年議會', location: '台北衛理福音園', date: '民國八十四年四月二十日', chair: '伍秉衡', secretary: '王春安 蔡敏勝' },
  { type: '中華年議會', session: '第三十二屆', location: '台北衛理福音園', date: '民國八十四年七月二十日至二十一日', chair: '伍秉衡', secretary: '王春安 蔡敏勝' },
  { type: '中華年議會', session: '第三十三屆臨時年議會', location: '台北衛理福音園', date: '民國八十五年五月七日', chair: '伍秉衡', secretary: '鄭憲章 劉瑞河' },
  { type: '中華年議會', session: '第三十三屆', location: '台北衛理福音園', date: '民國八十五年七月二十二日至二十三日', chair: '景泰祥', secretary: '鄭憲章 蔡本源' },
  { type: '中華年議會', session: '第三十四屆臨時年議會', location: '台北衛理福音園', date: '民國八十五年十一月十八日', chair: '曾紀鴻', secretary: '鄭憲章 劉瑞河' },
  { type: '中華年議會', session: '第三十四屆', location: '台北衛理福音園', date: '民國八十六年七月十七日至十八日', chair: '曾紀鴻', secretary: '黃建華 謝毓駿' },
  { type: '中華年議會', session: '第三十五屆年議會第一次會議', location: '台北衛理福音園', date: '民國八十七年四月二十九日', chair: '曾紀鴻', secretary: '許長榮 林中立' },
  { type: '中華年議會', session: '第三十五屆年議會第二次會議', location: '台北衛理福音園', date: '民國八十七年七月十五日至十六日', chair: '曾紀鴻', secretary: '許長榮 盧聖邦' },
  { type: '中華年議會', session: '第三十六屆年議會第一次會議', location: '台北衛理福音園', date: '民國八十八年七月十三日', chair: '曾紀鴻', secretary: '侯協明 王國安' },
  { type: '中華年議會', session: '第三十七屆年議會第一次會議', location: '台北衛理福音園', date: '民國八十九年五月十七日', chair: '曾紀鴻', secretary: '林烽銓 梅翰生' },
  { type: '中華年議會', session: '第三十八屆年議會第一次會議', location: '台北衛理福音園', date: '民國九十年二月二十一日', chair: '曾紀鴻', secretary: '陳建中 鍾維信' },
  { type: '中華年議會', session: '第三十八屆年議會第二次會議', location: '台北衛理福音園', date: '民國九十年五月十六日至十七日', chair: '曾紀鴻', secretary: '陳建中 鍾維信' },
  { type: '中華年議會', session: '第三十九屆年議會第一次會議', location: '台北衛理福音園', date: '民國九十一年五月二十一日', chair: '曾紀鴻', secretary: '許世芬 曹穎' },
  { type: '中華年議會', session: '第四十屆年議會第一次會議', location: '台北衛理福音園', date: '民國九十二年六月二十七日', chair: '曾紀鴻', secretary: '蘇福全 金賽玉' },
  { type: '中華年議會', session: '第四十一屆年議會第一次會議', location: '台北衛理福音園', date: '民國九十三年二月十七日', chair: '曾紀鴻', secretary: '莊璧如 吳玉僑' },
  { type: '中華年議會', session: '第四十一屆年議會第二次會議', location: '台北衛理福音園', date: '民國九十三年五月二十八日至二十九日', chair: '曾紀鴻', secretary: '莊璧如 黃寬裕 歐陽讓 汪鵬聰' },
  { type: '中華年議會', session: '第四十二屆年議會第一次會議', location: '台北衛理福音園', date: '民國九十四年五月二十日', chair: '黃建華', secretary: '唐秋惠 高麗穗' },
  { type: '中華年議會', session: '第四十三屆年議會第一次會議', location: '台北衛理福音園', date: '民國九十五年五月二十五日至二十六日', chair: '黃建華', secretary: '嚴明華 唐基微' },
  { type: '中華年議會', session: '第四十四屆年議會第一次會議', location: '台北衛理福音園', date: '民國九十六年二月二十七日', chair: '黃建華', secretary: '黃寬裕 藍思琪' },
  { type: '中華年議會', session: '第四十四屆年議會第二次會議', location: '台北衛理福音園', date: '民國九十六年五月三十一日至六月一日', chair: '黃建華', secretary: '黃寬裕 藍思琪' },
  { type: '中華年議會', session: '第四十五屆年議會第一次會議', location: '台北衛理福音園', date: '民國九十七年五月廿三日至五月廿四日', chair: '黃建華', secretary: '林烽銓 李承譽' },
  { type: '中華年議會', session: '第四十六屆年議會第一次會議', location: '台北衛理福音園', date: '民國九十八年五月廿一日至五月廿二日', chair: '黃建華', secretary: '關鎮威 陳碧娥' },
  { type: '中華年議會', session: '第四十七屆年議會第一次會議', location: '台北衛理福音園', date: '民國九十九年二月廿六日至二月廿七日', chair: '黃建華', secretary: '徐雪坪 趙慧敏' },
  { type: '中華年議會', session: '第四十七屆年議會第二次會議', location: '台北衛理福音園', date: '民國九十九年五月廿八日至五月廿九日', chair: '黃建華', secretary: '徐雪坪 何家淑' },
  { type: '中華年議會', session: '第四十八屆年議會第一次會議', location: '台北衛理福音園', date: '民國一〇〇年五月二十日', chair: '林長贈', secretary: '徐秀蓉 谷筱雯' },
  { type: '中華年議會', session: '第四十九屆年議會第一次會議', location: '台北衛理堂', date: '民國一〇〇年十月十二日', chair: '林長贈', secretary: '徐秀蓉 胡瑠美 施小惠' },
  { type: '中華年議會', session: '第四十九屆年議會第二次會議', location: '衛理神學研究院', date: '民國一〇一年二月二十五日', chair: '林長贈', secretary: '徐秀蓉 胡瑠美' },
  { type: '中華年議會', session: '第五十屆年議會第一次會議', location: '台北衛理堂', date: '民國一〇一年十一月十六日', chair: '林長贈', secretary: '徐秀蓉 胡瑠美' },
  { type: '中華年議會', session: '第五十屆年議會第二次會議', location: '台北衛理福音園', date: '民國一〇二年二月二十二日', chair: '林長贈', secretary: '葉雅慧 鄭明芳' },
  { type: '中華年議會', session: '第五十屆年議會第三次會議', location: '台北衛理福音園', date: '民國一〇二年五月二十四日', chair: '林長贈', secretary: '葉雅慧 施小惠' },
  { type: '中華年議會', session: '第五十一屆年議會第一次會議', location: '台北衛理福音園', date: '民國一〇三年五月二十三日', chair: '林長贈', secretary: '戴祖聖 鄭明芳' },
  { type: '中華年議會', session: '第五十二屆年議會第一次會議', location: '台北衛理福音園', date: '民國一〇四年五月二十九日', chair: '林長贈', secretary: '葉雅慧 羅仲娟 葉純珍' },
  { type: '中華年議會', session: '第五十三屆年議會第一次會議', location: '台北衛理福音園', date: '民國一〇四年十二月十二日', chair: '林長贈', secretary: '葉雅慧 葉純珍' },
  { type: '中華年議會', session: '第五十三屆年議會第二次會議', location: '台北衛理福音園', date: '民國一〇五年二月二十六日', chair: '林長贈', secretary: '葉雅慧 葉純珍' },
  { type: '中華年議會', session: '第五十三屆年議會第三次會議', location: '台北衛理福音園', date: '民國一〇五年五月廿七日至五月廿八日', chair: '林長贈', secretary: '葉雅慧 龍寶珍' },
  { type: '中華年議會', session: '第五十四屆年議會第一次會議', location: '台北衛理福音園', date: '民國一〇六年五月十九日至五月二十日', chair: '陳建中', secretary: '陳信成 林恩寧' },
  { type: '中華年議會', session: '第五十五屆年議會第一次會議', location: '台北衛理福音園', date: '民國一〇七年五月二十五日', chair: '陳建中', secretary: '李信政 林恩寧' },
  { type: '中華年議會', session: '第五十六屆年議會第一次會議', location: '台北衛理福音園', date: '民國一〇八年二月二十二日', chair: '陳建中', secretary: '吳怡慧 龍寶珍' },
  { type: '中華年議會', session: '第五十六屆年議會第二次會議', location: '台北衛理福音園', date: '民國一〇八年五月廿四日至五月廿五日', chair: '陳建中', secretary: '吳怡慧 賴正中' },
  { type: '中華年議會', session: '第五十七屆年議會第一次會議', location: '台北衛理堂、台中衛理堂、高雄榮光堂、馬祖衛理堂', date: '民國一〇九年五月廿二日', chair: '龐君華', secretary: '高思凱 安慧婷' },
  { type: '中華年議會', session: '第五十八屆年議會第一次會議', location: 'ZOOM線上視訊會議', date: '民國一一〇年五月廿二日', chair: '龐君華', secretary: '吳怡慧 莊友銘' },
  { type: '中華年議會', session: '第五十九屆年議會第一次會議', location: '台北衛理福音園', date: '民國一一一年二月十八日', chair: '龐君華', secretary: '曾以勒 賴正中' },
  { type: '中華年議會', session: '第五十九屆年議會第二次會議', location: '台北衛理堂及ZOOM線上視訊會議', date: '民國一一一年五月廿日至五月廿一日', chair: '龐君華', secretary: '曾以勒 賴正中' },
  { type: '中華年議會', session: '第六十屆年議會第一次會議', location: '台北衛理福音園', date: '民國一一二年五月十九日', chair: '黃寬裕', secretary: '賴明貞 李永祺' },
];

const activeType = ref<'all' | ConferenceRecord['type']>('all');
const search = ref('');

const typeFilters = computed(() => {
  const counts = records.reduce<Record<string, number>>((acc, r) => {
    acc[r.type] = (acc[r.type] ?? 0) + 1;
    return acc;
  }, {});
  return [
    { id: 'all' as const, label: '全部', count: records.length },
    { id: '臺港臨時年議會' as const, label: '臺港臨時年議會', count: counts['臺港臨時年議會'] ?? 0 },
    { id: '臺灣臨時年議會' as const, label: '臺灣臨時年議會', count: counts['臺灣臨時年議會'] ?? 0 },
    { id: '中華年議會' as const, label: '中華年議會', count: counts['中華年議會'] ?? 0 },
  ];
});

const filtered = computed(() => {
  const q = search.value.trim();
  return records.filter(r => {
    if (activeType.value !== 'all' && r.type !== activeType.value) return false;
    if (!q) return true;
    return (
      r.session.includes(q) ||
      r.location.includes(q) ||
      r.date.includes(q) ||
      r.chair.includes(q) ||
      r.secretary.includes(q)
    );
  });
});
</script>
