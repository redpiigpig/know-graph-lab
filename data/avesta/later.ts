import type { ZoroCanon } from './types'

// 後期文獻（外典）— 新波斯語與古吉拉特語
//
// 收錄理由：祆教沒有在薩珊滅亡時停止書寫。這一藏是社群自己在流散中寫的東西——
// 遷徙史、與伊朗本部通信的教法答問、給不再讀得懂巴列維文的信眾的白話宗教書。
//
// 🚨 定位要說清楚：這些不是「經」，作者自己也不當它們是經。
//    《百門》開宗明義說它是為「不通巴列維文者」摘述前人之說。
//    列為外典是體例上的老實，不是貶低——沒有這一藏，
//    祆教的故事會在公元 1000 年斷掉，而它其實一直延續到今天。
//
//    但 scriptural 仍為 true：那一欄問的是「是不是本教的宗教文獻」，
//    不是「是不是正典」。這一藏是祆教徒寫給祆教徒的宗教書，答案是肯定的。
//    四藏裡只有王室銘文為 false。

export const LATER_CANON: ZoroCanon = {
  key: 'later',
  name: '後期文獻',
  name_en: 'Later Persian and Gujarati Literature',
  glyph: '後',
  subtitle: '外典 — 新波斯語與古吉拉特語',
  scriptural: true,
  language: '新波斯語、古吉拉特語',
  era: '公元 12–19 世紀',
  summary:
    '巴列維文成為死語言之後，祆教社群改用新波斯語與（在印度）古吉拉特語繼續書寫。這一藏包含三類：給一般信眾的白話宗教綱要（《百門》）、印度帕西社群與伊朗本部祭司之間長達三百年的教法通信（《波斯利瓦亞特》），以及社群自己的遷徙史與詩體聖傳。**它們的價值不在教義原創，而在於這是一個少數族群在流散中維持自我認同的完整紀錄**——這一點對比較宗教研究的意義，不下於任何一部經。',
  parts: [
    {
      key: 'p-manual', label: '綱要部', label_en: 'Manuals of the Faith',
      desc: '為不再通曉巴列維文的信眾所寫的白話宗教綱要。',
      volumes: ['manual'],
    },
    {
      key: 'p-rivayat', label: '通信部', label_en: 'The Rivāyats',
      desc: '印度帕西社群遣使赴伊朗求問教法、伊朗祭司書面答覆的往來紀錄。',
      volumes: ['rivayat'],
    },
    {
      key: 'p-community', label: '族史部', label_en: 'Community History and Hagiography',
      desc: '遷徙史、聖傳與宗教志。',
      volumes: ['community'],
    },
  ],
  volumes: [
    {
      key: 'manual', sigil: '綱', name: '白話綱要', name_en: 'Vernacular Manuals',
      era: '14–16 世紀', extent: '約 3 種',
      summary:
        '巴列維文獻對十四世紀的祆教徒已經難讀，於是有人把要點譯述為當時通行的新波斯語。這批書在帕西社群流通極廣，實際塑造了近代祆教徒對自己宗教的理解——**近代祆教的樣貌是由這一層決定的，不是由阿維斯陀決定的**。',
      divisions: [
        {
          key: 'mn-all', label: '綱要諸書', label_en: 'Manuals',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: [
            { slug: 'sad-dar-nasr', title_zh: '百門（散文本）', title_orig: 'Sad Dar Nasr', siglum: 'SdN', language: '新波斯語', extent: '100 章', status: 'whole', era: '約 15 世紀', note: '一百則宗教義務的白話摘述，每則一「門」。韋斯特譯本收於 SBE 第 24 卷。' },
            { slug: 'sad-dar-nazm', title_zh: '百門（韻文本）', title_orig: 'Sad Dar Naẓm', siglum: 'SdNz', language: '新波斯語', extent: '100 章', status: 'whole', note: '同一內容的詩體改寫本。' },
            { slug: 'zaratusht-nama', title_zh: '查拉圖斯特拉傳（詩體）', title_orig: 'Zarātušt-nāma', siglum: 'ZN', language: '新波斯語', status: 'whole', era: '約 1278 年', author: '扎爾圖什特‧巴赫拉姆', note: '仿《列王紀》體例的先知生平長詩；材料本於《丹卡爾德》第七卷。' },
          ],
        },
      ],
    },
    {
      key: 'rivayat', sigil: '問', name: '波斯利瓦亞特', name_orig: 'Persian Rivāyats', name_en: 'The Persian Rivāyats',
      era: '1478–1773 年', extent: '約 22 通',
      summary:
        '印度帕西社群自十五世紀末起，屢次派人攜書信橫渡阿拉伯海赴伊朗亞茲德、克爾曼，向當地祆教祭司請教儀式與教法疑難，祭司書面作答，使者再攜回。前後近三百年、二十餘通往返。**這是宗教史上罕見的、跨海分隔的兩個社群逐條協商如何維持同一個傳統的實錄**——問題從「新火廟該如何開光」到「與異教徒通婚的子女算不算教徒」，答案有時彼此矛盾，那些矛盾本身就是材料。',
      divisions: [
        {
          key: 'rv-all', label: '往返書信', label_en: 'The Correspondence',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: [
            { slug: 'rivayat-nariman-hoshang', title_zh: '納里曼‧霍尚書', title_orig: 'Rivāyat of Nariman Hoshang', siglum: 'RvNH', language: '新波斯語', era: '1478 年', status: 'whole', note: '現存最早的一通，開啟三百年往返。' },
            { slug: 'rivayat-kama-bohra', title_zh: '卡瑪‧波赫拉書', title_orig: 'Rivāyat of Kama Bohra', siglum: 'RvKB', language: '新波斯語', era: '1527 年', status: 'whole' },
            { slug: 'rivayat-shapur-bharuchi', title_zh: '沙普爾‧巴魯奇書', title_orig: 'Rivāyat of Shapur Bharuchi', siglum: 'RvSB', language: '新波斯語', era: '1627 年', status: 'whole' },
            { slug: 'rivayat-barzu-qiyamuddin', title_zh: '巴爾祖‧齊亞穆丁書', title_orig: 'Rivāyat of Barzu Qiyamuddin', siglum: 'RvBQ', language: '新波斯語', era: '1636 年', status: 'whole' },
            { slug: 'rivayat-collection', title_zh: '利瓦亞特彙編（其餘各通）', title_orig: 'Persian Rivāyats (collected)', siglum: 'Rv', language: '新波斯語', era: '1478–1773 年', status: 'whole', note: '其餘十餘通，以主題彙編傳世；杜拉英譯本（1932）為通行本。' },
          ],
        },
      ],
    },
    {
      key: 'community', sigil: '族', name: '族史與宗教志', name_en: 'Community History',
      era: '16–19 世紀', extent: '約 4 種',
      summary:
        '帕西社群關於自身來歷的敘述，以及外部觀察者所留的紀錄。《桑賈恩紀事》是帕西人自述遷徙的唯一傳統文本——它成書於事件之後六百餘年，史實性一直有爭議，但它是這個社群的自我起源敘事，其功能與史實性是兩回事。',
      divisions: [
        {
          key: 'cm-all', label: '族史諸書', label_en: 'Histories',
          columns: { orig: 'available', en: 'available', zh: 'none' },
          texts: [
            { slug: 'qissa-i-sanjan', title_zh: '桑賈恩紀事', title_orig: 'Qissa-i Sanjān', siglum: 'QS', language: '新波斯語', era: '1600 年', status: 'whole', author: '巴赫曼‧凱庫巴德', note: '帕西人自伊朗渡海抵印度古吉拉特、獲王許居留、建阿塔什‧巴赫拉姆聖火的詩體敘事。**帕西族群認同的奠基文本**，但成書晚於所敘事件六百年，史實性須另行評估。' },
            { slug: 'dabestan-e-mazaheb', title_zh: '諸教志', title_orig: 'Dabestān-e Mazāheb', siglum: 'DM', language: '新波斯語', era: '17 世紀中', status: 'whole', note: '蒙兀兒時代印度所編的比較宗教志，含篇幅可觀的祆教一章。作者身分不明，一說為阿扎爾‧凱萬教團中人，其祆教敘述夾雜該派自創的說法，使用須謹慎。' },
            { slug: 'meherjirana-genealogy', title_zh: '納夫薩里祭司世系', title_orig: 'Genealogy of the Navsari Parsi Priests', siglum: 'MG', language: '古吉拉特語', era: '19 世紀', status: 'whole', note: '印度祆教祭司家系的譜牒紀錄。' },
            { slug: 'mushkil-asan', title_zh: '解難記', title_orig: 'Mushkil Āsān', siglum: 'MA', language: '新波斯語／古吉拉特語', status: 'whole', note: '樵夫遇困得助的民間故事，附於祈願儀式誦唸；今日帕西家庭仍在使用的活文本。' },
          ],
        },
      ],
    },
  ],
}
