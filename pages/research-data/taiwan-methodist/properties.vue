<template>
  <div class="min-h-screen bg-slate-50">

    <nav class="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div class="max-w-6xl mx-auto px-6 h-14 flex items-center gap-4">
        <NuxtLink to="/research-data/taiwan-methodist" class="text-gray-400 hover:text-gray-700 transition text-sm">← 台灣衛理公會研究資料</NuxtLink>
        <span class="text-gray-200">|</span>
        <span class="text-sm font-medium text-gray-700">財團法人財產清冊</span>
      </div>
    </nav>

    <div class="max-w-6xl mx-auto px-6 py-8">

      <!-- 標題 -->
      <div class="mb-6">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-xs font-medium px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-700">研究資料</span>
          <span class="text-xs text-gray-400">財團法人中華基督教衛理公會</span>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 mb-1">財團法人中華基督教衛理公會財產清冊</h1>
        <p class="text-sm text-gray-500">
          全台堂會、牧宅、神學院、福音園等不動產，共 {{ properties.length }} 處，
          合計面積約 <span class="font-semibold text-gray-700">{{ totalArea.toLocaleString('zh-TW', { maximumFractionDigits: 2 }) }}</span> 平方公尺。
        </p>
      </div>

      <!-- 出處 -->
      <div class="mb-6 p-4 rounded-xl bg-white border border-gray-100 text-xs text-gray-600 leading-relaxed">
        <span class="text-gray-400 mr-1">出處</span>
        中華基督教衛理公會總會編，《中華基督教衛理公會第六十屆年議會大會會議紀錄》（台北市：中華基督教衛理公會總會，2023 年 5 月，發行人：黃寬裕），頁 246-247。
      </div>

      <!-- 篩選 -->
      <div class="bg-white rounded-2xl border border-gray-100 p-4 mb-4 flex flex-col sm:flex-row gap-3 flex-wrap">
        <div class="flex flex-wrap gap-2">
          <button
            v-for="r in regionFilters" :key="r.id"
            @click="activeRegion = r.id"
            :class="['px-3 py-1.5 text-xs font-medium rounded-full border transition', activeRegion === r.id ? 'bg-emerald-600 border-emerald-600 text-white' : 'bg-white border-gray-200 text-gray-600 hover:border-emerald-300']"
          >
            {{ r.label }}
            <span class="ml-1 opacity-70">{{ r.count }}</span>
          </button>
        </div>
        <input
          v-model="search"
          type="text"
          placeholder="搜尋堂會名稱／地址／地號…"
          class="flex-1 sm:max-w-xs px-3 py-2 border border-gray-200 rounded-xl text-sm outline-none focus:ring-2 focus:ring-emerald-400"
        />
      </div>

      <!-- 統計 -->
      <p class="mb-4 text-xs text-gray-500">
        顯示 {{ filtered.length }} / {{ properties.length }} 處 ·
        篩選後合計面積 <span class="font-semibold text-gray-700">{{ filteredArea.toLocaleString('zh-TW', { maximumFractionDigits: 2 }) }}</span> 平方公尺
      </p>

      <!-- 表格 -->
      <div class="bg-white rounded-2xl border border-gray-100 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full text-sm">
            <thead class="bg-slate-100 text-gray-600 text-xs uppercase tracking-wider">
              <tr>
                <th class="px-3 py-2.5 text-left font-medium whitespace-nowrap w-10">#</th>
                <th class="px-3 py-2.5 text-left font-medium whitespace-nowrap">堂會名稱</th>
                <th class="px-3 py-2.5 text-left font-medium">坐落門牌地址</th>
                <th class="px-3 py-2.5 text-left font-medium">地號</th>
                <th class="px-3 py-2.5 text-right font-medium whitespace-nowrap">面積<br><span class="text-[10px] normal-case opacity-70">(平方公尺)</span></th>
                <th class="px-3 py-2.5 text-left font-medium whitespace-nowrap">備註</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <template v-for="p in filtered" :key="p.id">
                <tr v-for="(g, gi) in p.parcels" :key="`${p.id}-${gi}`" class="hover:bg-emerald-50/40">
                  <td class="px-3 py-2.5 align-top text-gray-400 text-xs">{{ gi === 0 ? p.id : '' }}</td>
                  <td class="px-3 py-2.5 align-top whitespace-pre-line text-gray-900 font-medium">
                    {{ gi === 0 ? p.names.join('\n') : '' }}
                  </td>
                  <td class="px-3 py-2.5 align-top whitespace-pre-line text-gray-700 text-xs leading-relaxed">
                    {{ gi === 0 ? p.addresses.join('\n') : '' }}
                  </td>
                  <td class="px-3 py-2.5 align-top whitespace-pre-line text-gray-700 text-xs leading-relaxed">{{ g.parcel }}</td>
                  <td class="px-3 py-2.5 align-top text-right tabular-nums text-gray-900">{{ g.area.toLocaleString('zh-TW', { maximumFractionDigits: 3 }) }}</td>
                  <td class="px-3 py-2.5 align-top whitespace-nowrap text-gray-600 text-xs">{{ g.note }}</td>
                </tr>
              </template>
              <tr v-if="!filtered.length">
                <td colspan="6" class="px-3 py-10 text-center text-gray-400 text-sm">沒有符合條件的紀錄</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' });
useHead({ title: '財團法人衛理公會財產清冊 — Know Graph Lab' });

interface ParcelGroup {
  parcel: string;
  area: number;
  note: string;
}

interface Property {
  id: number;
  region: '台北' | '新北' | '台中' | '南投' | '嘉義' | '台南' | '高雄' | '馬祖';
  names: string[];
  addresses: string[];
  parcels: ParcelGroup[];
}

const properties: Property[] = [
  { id: 1, region: '台北', names: ['台北衛理堂'], addresses: ['台北市大安區新生南路1段113號'],
    parcels: [{ parcel: '台北市大安區懷生段三小段586.590.591.593地號', area: 3029, note: '四筆' }] },
  { id: 2, region: '台北', names: ['恩友堂'], addresses: ['台北市松山區寶清街123號'],
    parcels: [{ parcel: '台北市松山區寶清段一小段273.273-1.273-2.274.274-1.275.276.276-6.277地號', area: 1269.35, note: '九筆' }] },
  { id: 3, region: '台北', names: ['雅各大樓', '雅各堂', '總會'],
    addresses: ['台北市大安區光復南路438號', '台北市大安區光復南路438號2樓', '台北市大安區光復南路438號1樓'],
    parcels: [{ parcel: '台北市大安區仁愛段一小段640.641.647地號', area: 993, note: '三筆' }] },
  { id: 4, region: '台北', names: ['城中教會'], addresses: ['台北市中正區寧波東街9巷4號6號'],
    parcels: [{ parcel: '台北市中正區南海段一小段681地號', area: 559, note: '一筆' }] },
  { id: 5, region: '台北', names: ['城中牧宅'], addresses: ['台北市中正區南昌路2段31號4樓之3'],
    parcels: [{ parcel: '台北市中正區南海段二小段244.263地號', area: 100.47, note: '二筆' }] },
  { id: 6, region: '台北', names: ['沛恩堂'], addresses: ['台北市松山區民生東路5段36號8弄30號'],
    parcels: [{ parcel: '台北市松山區民生段82-9地號', area: 270, note: '持分: 1/4' }] },
  { id: 7, region: '台北', names: ['沛恩堂牧宅'], addresses: ['台北市松山區新東街12巷37號2樓'],
    parcels: [{ parcel: '台北市松山區民生段47-9地號', area: 102.87, note: '一筆' }] },
  { id: 8, region: '台北', names: ['平安堂'], addresses: ['台北市文山區仙岩路16巷35弄2號、2-1號1~4樓'],
    parcels: [{ parcel: '台北市文山區興安段二小段482地號', area: 603, note: '一筆' }] },
  { id: 9, region: '台北', names: ['平安公寓'],
    addresses: ['台北市仙岩路16巷35弄6號1樓4樓', '台北市仙岩路16巷35弄8號1樓4樓', '台北市仙岩路16巷39弄9號1樓~4樓'],
    parcels: [{ parcel: '台北市文山區興安段二小段477地號\n(道路)興安段二小段344.483.485-1地號', area: 808, note: '四筆' }] },
  { id: 10, region: '台北', names: ['王者鄉', '衛理神學院', '平安堂牧宅', '會督館'],
    addresses: ['台北市文山區仙岩路22巷9-31號', '台北市文山區仙岩路22巷31號1-4樓', '台北市文山區仙岩路22巷31號4樓之3', '台北市文山區仙岩路22巷31號17樓之3'],
    parcels: [{ parcel: '台北市文山區興安段二小段546地號\n(道路)292地號', area: 9607, note: '持分：15796/100000' }] },
  { id: 11, region: '台北', names: ['夏卡爾'], addresses: ['台北市文山區仙岩路22巷2號等'],
    parcels: [
      { parcel: '興安段二小段514地號', area: 1187, note: '持分：20283/100000' },
      { parcel: '興安段二小段514-1.514-2.541-1地號', area: 123, note: '三筆' },
    ] },
  { id: 12, region: '台北', names: ['福音園'], addresses: ['台北市士林區仰德大道2段200號'],
    parcels: [{ parcel: '台北市士林區至善段四小段39.52.53.54.55.146.148.151地號', area: 2421, note: '八筆' }] },
  { id: 13, region: '台北', names: ['衛理大廈', '華恩堂'],
    addresses: ['台北市大安區濟南路3段9號', '台北市大安區濟南路3段9號4樓'],
    parcels: [{ parcel: '台北市大安區懷生段三小段476地號', area: 298, note: '一筆' }] },
  { id: 14, region: '新北', names: ['天恩堂'], addresses: ['新北市永和區信義路23號'],
    parcels: [{ parcel: '永和市信義段313地號', area: 334, note: '一筆' }] },
  { id: 15, region: '新北', names: ['聖保羅堂'], addresses: ['新北市新店區建國路33巷10號'],
    parcels: [{ parcel: '新店市建國段664(1/4). 662(1/4).\n663(1/2). 661(1/2). 660(1/2)地號', area: 104.26, note: '五筆' }] },
  { id: 16, region: '台北', names: ['木柵衛理堂'], addresses: ['台北市文山區木柵路3段102巷14之2號'],
    parcels: [{ parcel: '台北市文山區木柵段三小段0248地號', area: 949, note: '一筆' }] },
  { id: 17, region: '新北', names: ['榮恩堂'], addresses: ['新北市板橋區文聖街144號、146號、148號2樓'],
    parcels: [{ parcel: '板橋市江子翠段第一崁小段24-0002地號', area: 1105, note: '持分 757/10000' }] },
  { id: 18, region: '新北', names: ['榮恩堂牧宅'], addresses: ['新北市板橋區文聖街149巷15號4樓'],
    parcels: [{ parcel: '板橋市江子翠段第二崁小段113.114地號', area: 27.98, note: '二筆' }] },
  { id: 19, region: '新北', names: ['約翰堂'], addresses: ['新北市樹林區中山路1段148號'],
    parcels: [{ parcel: '台北縣樹林市復興段823地號', area: 1891, note: '一筆' }] },
  { id: 20, region: '新北', names: ['三峽衛理堂'], addresses: ['新北市三峽區大同路134號'],
    parcels: [{ parcel: '三峽區永安段1863-0000地號', area: 110.85, note: '一筆' }] },
  { id: 21, region: '台中', names: ['台中衛理堂'], addresses: ['台中市西區民生路137號、137-1號'],
    parcels: [{ parcel: '西區平和段6-0006.6-0009.6-0010.6-0131.6-0146地號', area: 3534, note: '五筆' }] },
  { id: 22, region: '台中', names: ['台中衛道堂'], addresses: ['台中市東區力行路69號'],
    parcels: [{ parcel: '台中市東區東勢子段44-0027地號', area: 1818, note: '一筆' }] },
  { id: 23, region: '台中', names: ['台中衛道堂牧宅'], addresses: ['台中市東區自強街5巷18號'],
    parcels: [{ parcel: '台中市東區東勢子段44-0189, 44-0190', area: 238.5, note: '二筆' }] },
  { id: 24, region: '台中', names: ['台中信正教會'], addresses: ['台中市北區西屯路一段391巷1號'],
    parcels: [{ parcel: '台中市北區乾溝子段0088-0032、33、34、35、36、37地號', area: 387, note: '六筆' }] },
  { id: 25, region: '南投', names: ['南投竹山衛理堂'], addresses: ['南投縣竹山鎮公所路117號'],
    parcels: [{ parcel: '南投縣竹山鎮雲林段1687-0000地號', area: 121.303, note: '一筆' }] },
  { id: 26, region: '台中', names: ['台中大里衛理堂'], addresses: ['台中市大里區大里二街161號'],
    parcels: [{ parcel: '台中縣大里市大忠段0307-0002地號', area: 140.61, note: '一筆' }] },
  { id: 27, region: '嘉義', names: ['嘉義衛理堂'], addresses: ['嘉義市維新路66號'],
    parcels: [{ parcel: '嘉義市中山段四小段33-1地號', area: 139, note: '一筆' }] },
  { id: 28, region: '台南', names: ['台南衛理堂'], addresses: ['台南市中西區健康路1段368號，370,370-1,370-2號'],
    parcels: [{ parcel: '台南市南寧段 6024-1.6025-2. 6025-4\n6028-9地號', area: 2063, note: '四筆' }] },
  { id: 29, region: '台南', names: ['台南安平堂'], addresses: ['台南市安平區平豐路141號'],
    parcels: [{ parcel: '台南市金城段0050-0027地號', area: 99, note: '一筆' }] },
  { id: 30, region: '台南', names: ['台南永康衛理堂'], addresses: ['台南市永康區永興路351號'],
    parcels: [{ parcel: '台南縣永康市永二段0664地號', area: 681.39, note: '一筆' }] },
  { id: 31, region: '台南', names: ['南工衛理中心'], addresses: ['台南縣永康市南工街135巷8號'],
    parcels: [{ parcel: '台南縣永康市忠孝段212.213地號', area: 89.5, note: '二筆' }] },
  { id: 32, region: '高雄', names: ['高雄衛理堂'], addresses: ['高雄市新興區中山二路564號'],
    parcels: [{ parcel: '高雄市前金段493-0008. 493-0009地號', area: 852, note: '二筆' }] },
  { id: 33, region: '高雄', names: ['高雄榮光堂牧宅'], addresses: ['高雄市前鎮區桂林街32巷1號2樓'],
    parcels: [{ parcel: '高雄市前鎮區盛興段1142地號', area: 175, note: '持分:1/4' }] },
  { id: 34, region: '高雄', names: ['高雄榮光堂'], addresses: ['高雄市前鎮區廣西路155號'],
    parcels: [{ parcel: '前鎮區盛興段1089,1090-1,地號', area: 48, note: '二筆' }] },
  { id: 35, region: '高雄', names: ['高雄榮光堂'], addresses: ['高雄市苓雅區和平二路437號'],
    parcels: [{ parcel: '苓雅區林興段0170,0172地號', area: 1019, note: '二筆' }] },
  { id: 36, region: '馬祖', names: ['馬祖衛理堂'], addresses: ['馬祖連江縣南竿鄉清水村117之5號'],
    parcels: [{ parcel: '福建省連江縣南竿鄉清水段266地號', area: 492.41, note: '一筆' }] },
  { id: 37, region: '馬祖', names: ['北竿佈道所'], addresses: ['馬祖北竿鄉塘岐村241號'],
    parcels: [{ parcel: '福建省連江縣北竿鄉塘其段0844-0008地號', area: 139.12, note: '一筆' }] },
  { id: 38, region: '台南', names: ['南衛幼兒園'], addresses: ['台南市中西區健康路一段366號'],
    parcels: [{ parcel: '台南市中西區南門段2060地號', area: 97.88, note: '一筆' }] },
  { id: 39, region: '台南', names: ['南衛幼兒園'], addresses: ['台南市中西區健康路一段364號'],
    parcels: [{ parcel: '台南市中西區南門段2060地號', area: 92.61, note: '一筆' }] },
  { id: 40, region: '台南', names: ['南衛幼兒園'], addresses: ['台南市仁德區全福路80巷13弄16號'],
    parcels: [{ parcel: '台南市仁德區和愛段1035地號', area: 74.85, note: '一筆' }] },
];

const regions = ['台北', '新北', '台中', '南投', '嘉義', '台南', '高雄', '馬祖'] as const;

const activeRegion = ref<'all' | typeof regions[number]>('all');
const search = ref('');

const sumArea = (list: Property[]) => list.reduce((s, p) => s + p.parcels.reduce((a, g) => a + g.area, 0), 0);

const totalArea = computed(() => sumArea(properties));

const regionFilters = computed(() => {
  const counts = properties.reduce<Record<string, number>>((acc, p) => {
    acc[p.region] = (acc[p.region] ?? 0) + 1;
    return acc;
  }, {});
  return [
    { id: 'all' as const, label: '全部', count: properties.length },
    ...regions.map(r => ({ id: r, label: r, count: counts[r] ?? 0 })),
  ];
});

const filtered = computed(() => {
  const q = search.value.trim();
  return properties.filter(p => {
    if (activeRegion.value !== 'all' && p.region !== activeRegion.value) return false;
    if (!q) return true;
    return (
      p.names.some(n => n.includes(q)) ||
      p.addresses.some(a => a.includes(q)) ||
      p.parcels.some(g => g.parcel.includes(q) || g.note.includes(q))
    );
  });
});

const filteredArea = computed(() => sumArea(filtered.value));
</script>
