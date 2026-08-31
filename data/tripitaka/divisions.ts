// 佛教大藏經 /tripitaka —— 部類定義（顯示層）。
//
// 分類的權威在 scripts/tripitaka_cbeta.py 的 TAISHO_DIVISIONS / NANCHUAN_DIVISIONS
// （那裡按經號／冊號切，並由 pytest 鎖住區間不重疊不留縫）。本檔只補 UI 需要的
// 標籤、次序與配色，key 必須與 Python 端一致。

export interface Division {
  key: string
  label: string
  /** 梵／巴原名或英文對照，列表頁小字 */
  label_alt?: string
  /** 一句話說明這一部收什麼 */
  desc: string
  /** 大正藏冊次或南傳冊次區間，顯示用 */
  vols: string
  color: string
}

/** 大正藏第一區：印度傳來的經律論（漢譯佛典本體） */
export const TAISHO_TRANSLATED: Division[] = [
  { key: 'agama', label: '阿含部', label_alt: 'Āgama', vols: 'T01–02',
    desc: '四阿含與單經。與巴利五尼柯耶同源異流，是漢巴對照最密集的一部。', color: 'amber' },
  { key: 'benyuan', label: '本緣部', label_alt: 'Jātaka / Avadāna', vols: 'T03–04',
    desc: '佛傳、本生、譬喻。故事文學，與巴利《本生經》多有平行。', color: 'orange' },
  { key: 'prajna', label: '般若部', label_alt: 'Prajñāpāramitā', vols: 'T05–08',
    desc: '大般若六百卷、金剛經、心經。梵本與藏譯存世率高。', color: 'yellow' },
  { key: 'fahua', label: '法華部', label_alt: 'Saddharmapuṇḍarīka', vols: 'T09',
    desc: '法華經三譯與相關經。梵本完整（Kern–Nanjio 校本）。', color: 'rose' },
  { key: 'huayan', label: '華嚴部', label_alt: 'Avataṃsaka', vols: 'T09–10',
    desc: '華嚴經六十／八十／四十卷本。全本僅存藏譯，梵本只餘〈入法界品〉與〈十地品〉。', color: 'violet' },
  { key: 'baoji', label: '寶積部', label_alt: 'Ratnakūṭa', vols: 'T11–12',
    desc: '大寶積經四十九會與別譯。淨土三經在此。', color: 'indigo' },
  { key: 'niepan', label: '涅槃部', label_alt: 'Mahāparinirvāṇa', vols: 'T12',
    desc: '大乘涅槃經群。與阿含〈遊行經〉、巴利《大般涅槃經》同題異質。', color: 'slate' },
  { key: 'daji', label: '大集部', label_alt: 'Mahāsaṃnipāta', vols: 'T13',
    desc: '大集經與地藏十輪等。', color: 'teal' },
  { key: 'jingji', label: '經集部', label_alt: 'Sūtra miscellany', vols: 'T14–17',
    desc: '不入前列諸部的大乘經總彙，維摩詰、藥師、楞伽、解深密皆在此。', color: 'emerald' },
  { key: 'mijiao', label: '密教部', label_alt: 'Tantra', vols: 'T18–21',
    desc: '陀羅尼與儀軌，全藏最大一部。悉曇字梵咒集中於此。', color: 'purple' },
  { key: 'lu', label: '律部', label_alt: 'Vinaya', vols: 'T22–24',
    desc: '四分、五分、十誦、摩訶僧祇、根本說一切有部律。與巴利律藏平行。', color: 'stone' },
  { key: 'shijinglun', label: '釋經論部', label_alt: 'Sūtra commentary', vols: 'T25–26',
    desc: '大智度論、十住毘婆沙等解經之論。', color: 'lime' },
  { key: 'pitan', label: '毘曇部', label_alt: 'Abhidharma', vols: 'T26–29',
    desc: '說一切有部阿毘達磨。與巴利七論分屬兩系，不可互代。', color: 'cyan' },
  { key: 'zhongguan', label: '中觀部', label_alt: 'Madhyamaka', vols: 'T30',
    desc: '中論、百論、十二門論。頌文梵藏漢三本齊備，頌號可逐一對照。', color: 'sky' },
  { key: 'yuqie', label: '瑜伽部', label_alt: 'Yogācāra', vols: 'T30–31',
    desc: '瑜伽師地論、攝大乘論、唯識三十頌等。', color: 'blue' },
  { key: 'lunji', label: '論集部', label_alt: 'Śāstra miscellany', vols: 'T32',
    desc: '大乘起信論、成實論、因明入正理論等。', color: 'fuchsia' },
]

/** 大正藏第二區：中土（漢地）撰述 */
export const TAISHO_CHINESE: Division[] = [
  { key: 'jingshu', label: '經疏部', vols: 'T33–39', desc: '漢地祖師的經典注疏。', color: 'emerald' },
  { key: 'lushu', label: '律疏部', vols: 'T40', desc: '律典注疏。', color: 'stone' },
  { key: 'lunshu', label: '論疏部', vols: 'T40–44', desc: '論書注疏。', color: 'cyan' },
  { key: 'zhuzong', label: '諸宗部', vols: 'T44–48', desc: '天台、華嚴、禪、淨、律、密各宗自家著述。', color: 'purple' },
  { key: 'shizhuan', label: '史傳部', vols: 'T49–52', desc: '高僧傳、燈錄、王朝佛教史、求法行記。', color: 'amber' },
  { key: 'shihui', label: '事彙部', vols: 'T53–54', desc: '法苑珠林、經律異相、一切經音義等類書與音義。', color: 'orange' },
  { key: 'waijiao', label: '外教部', vols: 'T54', desc: '婆羅門、摩尼、景教等外道文獻的漢譯與記述。', color: 'rose' },
  { key: 'mulu', label: '目錄部', vols: 'T55', desc: '歷代經錄：出三藏記集、開元釋教錄等。', color: 'slate' },
  { key: 'guyi', label: '古逸部', vols: 'T85', desc: '敦煌等地出土的佚失文獻。', color: 'yellow' },
  { key: 'yisi', label: '疑似部', vols: 'T85', desc: '歷代經錄判為疑偽的經典。收錄不等於認可其真實性。', color: 'red' },
]

/** 漢譯南傳大藏經（元亨寺版）—— 巴利三藏的完整現代漢譯 */
export const NANCHUAN: Division[] = [
  { key: 'n-vinaya', label: '律藏', label_alt: 'Vinaya Piṭaka', vols: 'N01–05',
    desc: '經分別、犍度、附隨。', color: 'stone' },
  { key: 'n-digha', label: '長部', label_alt: 'Dīgha Nikāya', vols: 'N06–08',
    desc: '三十四經。與漢譯《長阿含經》同源。', color: 'amber' },
  { key: 'n-majjhima', label: '中部', label_alt: 'Majjhima Nikāya', vols: 'N09–12',
    desc: '一五二經。與漢譯《中阿含經》同源。', color: 'orange' },
  { key: 'n-samyutta', label: '相應部', label_alt: 'Saṃyutta Nikāya', vols: 'N13–18',
    desc: '五十六相應。與漢譯《雜阿含經》同源，大正藏原註已逐經標出對應編號。', color: 'yellow' },
  { key: 'n-anguttara', label: '增支部', label_alt: 'Aṅguttara Nikāya', vols: 'N19–25',
    desc: '十一集。與漢譯《增壹阿含經》同源。', color: 'lime' },
  { key: 'n-khuddaka', label: '小部', label_alt: 'Khuddaka Nikāya', vols: 'N26–47',
    desc: '法句、經集、本生、長老偈尼偈、無礙解道、大小義釋等十五種。', color: 'emerald' },
  { key: 'n-abhidhamma', label: '論藏', label_alt: 'Abhidhamma Piṭaka', vols: 'N48–62',
    desc: '南傳七論與《論事》。與漢譯毘曇部（有部系）分屬兩系。', color: 'cyan' },
  { key: 'n-outside', label: '藏外', label_alt: 'Extra-canonical', vols: 'N63–70',
    desc: '彌蘭王問經、島史、大史、小史、清淨道論、善見律註序、攝阿毘達磨義論、阿育王刻文。', color: 'violet' },
]

/**
 * 卍新纂大日本續藏經（X）—— 大正藏的補遺。
 *
 * 大正藏偏重印度傳來的經律論與唐以前的中土著述；卍續藏補的正是它略掉的那一半：
 * 宋元明清的疏鈔、各宗語錄、禮懺儀軌與寺志僧傳。兩藏合看，漢傳佛教才是全的。
 *
 * 部類與經號區間抓自 CBETA 站方原書目錄（見 tripitaka_cbeta.XUZANG_DIVISIONS），
 * 不是自訂的。每部底下另有第二層子類（宗派／經疏類目）共 60 個；
 * 禮懺部站方未再分子類，那 42 部沒有子類是預期。
 */
export const XUZANG: Division[] = [
  { key: 'x-india', label: '印度撰述', label_alt: 'Indian works', vols: 'X01–02',
    desc: '大正藏未收的印度經律論譯本與密教儀軌。全 X 部唯一非中土撰述的一區。', color: 'amber' },
  { key: 'x-jingshu', label: '大小乘釋經部', label_alt: 'Sūtra commentaries', vols: 'X03–37',
    desc: '華嚴、方等、般若、法華、涅槃各部的疏鈔，佔全藏三分之一。歷代講經的實錄。', color: 'emerald' },
  { key: 'x-lushu', label: '大小乘釋律部', label_alt: 'Vinaya commentaries', vols: 'X38–44',
    desc: '梵網、四分律的疏記。南山律宗的核心文獻多在此。', color: 'stone' },
  { key: 'x-lunshu', label: '大小乘釋論部', label_alt: 'Śāstra commentaries', vols: 'X45–53',
    desc: '起信、唯識、俱舍、因明各論的注疏。明末唯識學復興的著作集中於此。', color: 'cyan' },
  { key: 'x-zhuzong', label: '諸宗著述部', label_alt: 'Sectarian works', vols: 'X54–73',
    desc: '三論、法相、天台、華嚴、真言、戒律、淨土各宗著述，及禪宗語錄通集與別集。全藏最大一部。', color: 'purple' },
  { key: 'x-lichan', label: '禮懺部', label_alt: 'Liturgy & repentance', vols: 'X74',
    desc: '水陸、梁皇、藥師、地藏各種懺儀與道場儀軌。漢傳佛教實際怎麼做法事，看這一部。', color: 'rose' },
  { key: 'x-shizhuan', label: '史傳部', label_alt: 'Histories & biographies', vols: 'X75–88',
    desc: '燈錄、僧傳、編年史、寺志、居士傳、感應記。禪宗燈史的主體在此不在大正藏。', color: 'orange' },
]

export const ALL_DIVISIONS = [
  ...TAISHO_TRANSLATED, ...TAISHO_CHINESE, ...NANCHUAN, ...XUZANG,
]

export function divisionByKey(key: string): Division | undefined {
  return ALL_DIVISIONS.find(d => d.key === key)
}

/** 卡片／標籤配色。Tailwind 需要靜態類名，故列成表而非字串拼接。 */
export const COLOR_CLASS: Record<string, { chip: string; bar: string; hover: string }> = {
  amber:   { chip: 'bg-amber-50 text-amber-800 border-amber-200',     bar: 'bg-amber-400',   hover: 'hover:border-amber-300' },
  orange:  { chip: 'bg-orange-50 text-orange-800 border-orange-200',  bar: 'bg-orange-400',  hover: 'hover:border-orange-300' },
  yellow:  { chip: 'bg-yellow-50 text-yellow-800 border-yellow-200',  bar: 'bg-yellow-400',  hover: 'hover:border-yellow-300' },
  lime:    { chip: 'bg-lime-50 text-lime-800 border-lime-200',        bar: 'bg-lime-400',    hover: 'hover:border-lime-300' },
  emerald: { chip: 'bg-emerald-50 text-emerald-800 border-emerald-200', bar: 'bg-emerald-400', hover: 'hover:border-emerald-300' },
  teal:    { chip: 'bg-teal-50 text-teal-800 border-teal-200',        bar: 'bg-teal-400',    hover: 'hover:border-teal-300' },
  cyan:    { chip: 'bg-cyan-50 text-cyan-800 border-cyan-200',        bar: 'bg-cyan-400',    hover: 'hover:border-cyan-300' },
  sky:     { chip: 'bg-sky-50 text-sky-800 border-sky-200',           bar: 'bg-sky-400',     hover: 'hover:border-sky-300' },
  blue:    { chip: 'bg-blue-50 text-blue-800 border-blue-200',        bar: 'bg-blue-400',    hover: 'hover:border-blue-300' },
  indigo:  { chip: 'bg-indigo-50 text-indigo-800 border-indigo-200',  bar: 'bg-indigo-400',  hover: 'hover:border-indigo-300' },
  violet:  { chip: 'bg-violet-50 text-violet-800 border-violet-200',  bar: 'bg-violet-400',  hover: 'hover:border-violet-300' },
  purple:  { chip: 'bg-purple-50 text-purple-800 border-purple-200',  bar: 'bg-purple-400',  hover: 'hover:border-purple-300' },
  fuchsia: { chip: 'bg-fuchsia-50 text-fuchsia-800 border-fuchsia-200', bar: 'bg-fuchsia-400', hover: 'hover:border-fuchsia-300' },
  rose:    { chip: 'bg-rose-50 text-rose-800 border-rose-200',        bar: 'bg-rose-400',    hover: 'hover:border-rose-300' },
  red:     { chip: 'bg-red-50 text-red-800 border-red-200',           bar: 'bg-red-400',     hover: 'hover:border-red-300' },
  slate:   { chip: 'bg-slate-100 text-slate-700 border-slate-200',    bar: 'bg-slate-400',   hover: 'hover:border-slate-300' },
  stone:   { chip: 'bg-stone-100 text-stone-700 border-stone-200',    bar: 'bg-stone-400',   hover: 'hover:border-stone-300' },
}

/** 對照欄的語言。漢文永遠是基準欄，其餘按有無資料出現。 */
export const PARALLEL_LANGS: Record<string, { label: string; short: string; note?: string }> = {
  lzh:     { label: '漢文（大正藏）', short: '漢' },
  'zh-nan': { label: '漢譯南傳（元亨寺版）', short: '南傳' },
  'zh-mod': { label: '繁中白話', short: '白話', note: '本站自譯' },
  pi:      { label: '巴利', short: 'Pāli' },
  sa:      { label: '梵文', short: 'Skt' },
  pra:     { label: '中期印度語', short: 'Prakrit', note: '犍陀羅語／波特那法句經等，既非梵文也非巴利' },
  bo:      { label: '藏文', short: 'Tib' },
  en:      { label: '英譯', short: 'En' },
}

/** 對照資料的來源分級 —— UI 必須把三者分色，不可混為一談。 */
export const PARALLEL_SOURCES: Record<string, { label: string; desc: string; cls: string }> = {
  'taisho-equiv': {
    label: '大正藏原註',
    desc: '大正藏編者（1924–34）在經文腳註標出的巴利對應，權威度最高。',
    cls: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  },
  'cbeta-term': {
    label: 'CBETA 詞條',
    desc: 'CBETA 在專名旁附註的梵／巴原語形，逐詞而非逐段。',
    cls: 'bg-sky-50 text-sky-700 border-sky-200',
  },
  suttacentral: {
    label: 'SuttaCentral',
    desc: 'SuttaCentral 的跨語系平行經目資料庫，涵蓋巴利、漢譯、梵文殘卷與藏譯。',
    cls: 'bg-indigo-50 text-indigo-700 border-indigo-200',
  },
  site: {
    label: '本站對齊',
    desc: '無現成對照資料時由本站自行切分對齊，屬編輯判斷，非學術定論。',
    cls: 'bg-amber-50 text-amber-700 border-amber-200',
  },
}
