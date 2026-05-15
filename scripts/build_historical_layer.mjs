#!/usr/bin/env node
/**
 * Build a combined historical layer GeoJSON for /maps/world-religions.
 *
 * Reads aourednik/historical-basemaps snapshot files from C:\tmp\hbm-sample,
 * maps each state name → sphere_id, tags with valid_from/valid_to ranges,
 * outputs `public/maps/historical-spheres.geojson`.
 *
 * Unmapped names are dropped (rendered as oral-tribal gray base on map).
 *
 * Snapshot file → year_from mapping:
 *   bc4000.geojson → -4000  (valid -4000..-2001)
 *   bc2000.geojson → -2000  (valid -2000..-1501)
 *   ... etc
 *
 * License attribution required: CC BY-NC-SA 4.0,
 * Andrei Ourednik (https://github.com/aourednik/historical-basemaps).
 */

import { readFileSync, writeFileSync, existsSync } from 'node:fs'
import { join } from 'node:path'

const HBM_DIR = 'C:\\tmp\\hbm-sample'
const OUT_FILE = 'public/maps/historical-spheres.geojson'

// (snapshot_year, source_filename) ordered chronologically
const SNAPSHOTS = [
  [-4000, 'world_bc4000.geojson'],
  [-2000, 'world_bc2000.geojson'],
  [-1500, 'world_bc1500.geojson'],
  [-1000, 'world_bc1000.geojson'],
  [-500,  'world_bc500.geojson'],
  [-322,  'world_bc323.geojson'],   // file is bc323 (= 323 BCE)
  [-99,   'world_bc100.geojson'],   // file is bc100 (= 100 BCE)
  [200,   'world_200.geojson'],
  [500,   'world_500.geojson'],
  [800,   'world_800.geojson'],
  [1000,  'world_1000.geojson'],
  [1100,  'world_1100.geojson'],
  [1279,  'world_1279.geojson'],
  [1500,  'world_1500.geojson'],
  [1815,  'world_1815.geojson'],
  [1914,  'world_1914.geojson'],
  [2000,  'world_2000.geojson'],
]

// Name → { sphere, name_zh }. Sphere = sphere_id or '__skip__' to ignore.
// '__tribal__' = explicitly oral-tribal (don't render as polygon; let gray base show).
const MAP = {
  // ===== bc4000-era civilizations =====
  // 2026-05 重構：中央界域早期 spheres 拆分 — Ur/Hurrian/Semites → sumerian
  'Egypt':                            { sphere: 'egyptian',                name_zh: '埃及' },
  'Kerma':                            { sphere: 'egyptian',                name_zh: '克爾瑪（努比亞）' },
  'Ur':                               { sphere: 'sumerian',                name_zh: '烏爾' },
  'Hurrian Kingdoms':                 { sphere: 'sumerian',                name_zh: '胡里安諸邦' },
  'Elam':                             { sphere: 'persian',                 name_zh: '埃蘭' },
  'Indus valley civilization':        { sphere: 'indian',                  name_zh: '印度河文明' },
  'Minoan':                           { sphere: 'aegean-asia-minor',       name_zh: '米諾斯' },
  'Cycladic':                         { sphere: 'aegean-asia-minor',       name_zh: '基克拉迪' },
  'Norte Chico':                      { sphere: 'andean',                  name_zh: '小北文明' },
  'Valdivia':                         { sphere: 'andean',                  name_zh: '瓦爾迪維亞' },
  'Namazga':                          { sphere: 'persian',                 name_zh: '那馬茲加（中亞）' },
  'Semites':                          { sphere: 'sumerian',                name_zh: '閃族（古近東早期）' },
  'Dravidians':                       { sphere: 'indian',                  name_zh: '達羅毗荼' },
  'Dapenkeng culture':                { sphere: 'banua',                   name_zh: '大坌坑文化（台灣）' },
  'Dakapeng culture':                 { sphere: 'banua',                   name_zh: '大坌坑文化' },

  // ===== bc2000-era additions =====
  // 2026-05：Hittites → anatolia; Canaan → canaan
  'Hittites':                         { sphere: 'anatolia',                name_zh: '赫梯' },
  'Canaan':                           { sphere: 'canaan',                  name_zh: '迦南' },
  'Xia':                              { sphere: 'han',                     name_zh: '夏' },
  'Oxus':                             { sphere: 'persian',                 name_zh: '巴克特里亞-馬爾吉亞那（奧克蘇斯）' },
  'Únětice':                          { sphere: 'central-european',        name_zh: '奧涅蒂采（中歐青銅）' },
  'Beaker':                           { sphere: 'central-european',        name_zh: '鐘形杯文化' },

  // ===== bc1500-bc1000 (鐵器時代列國) =====
  'Assyria':                          { sphere: 'assyrian',                name_zh: '亞述' },
  'Babylonia':                        { sphere: 'babylonian',              name_zh: '巴比倫' },
  'Phrygians':                        { sphere: 'anatolia',                name_zh: '弗里吉亞' },
  'Arameans':                         { sphere: 'levant',                  name_zh: '亞蘭' },
  'state societies and Aramaean kingdoms': { sphere: 'levant',             name_zh: '亞蘭諸邦' },
  'Urartu':                           { sphere: 'caucasus',                name_zh: '烏拉爾圖' },
  'Iron Age megalith cultures':       { sphere: '__tribal__',              name_zh: '鐵器時代巨石文化' },

  // ===== bc323/bc100 (希臘化／早期帝國) =====
  // 此期間愛琴-小亞細亞已合，Cappadocia 等小亞細亞諸邦歸 aegean-asia-minor
  'Cappadocia':                       { sphere: 'aegean-asia-minor',       name_zh: '卡帕多西亞' },
  'Nabatean Kingdom':                 { sphere: 'mesopotamian-levantine',  name_zh: '納巴泰王國' },

  // ===== bc1500/bc1000/bc500 axial =====
  'Achaemenid Empire':                { sphere: 'persian',                 name_zh: '阿契美尼德波斯' },
  'Greek city-states':                { sphere: 'aegean-asia-minor',       name_zh: '希臘城邦' },
  'Rome':                             { sphere: 'latin-cultural',          name_zh: '羅馬' },
  'Etrurians':                        { sphere: 'latin-cultural',          name_zh: '伊特魯里亞' },
  'Sabini':                           { sphere: 'latin-cultural',          name_zh: '薩賓人' },
  'Samnites':                         { sphere: 'latin-cultural',          name_zh: '薩姆奈人' },
  'Carthaginian Empire':              { sphere: 'carthaginian-maghreb',    name_zh: '迦太基帝國' },
  'Magadha':                          { sphere: 'indian',                  name_zh: '摩揭陀' },
  'Kosala':                           { sphere: 'indian',                  name_zh: '憍薩羅' },
  'Kasi':                             { sphere: 'indian',                  name_zh: '迦尸' },
  'Avanti':                           { sphere: 'indian',                  name_zh: '阿槃提' },
  'Gandhāra':                         { sphere: 'indian',                  name_zh: '犍陀羅' },
  'Kuru':                             { sphere: 'indian',                  name_zh: '俱盧' },
  'Pancala':                          { sphere: 'indian',                  name_zh: '般遮羅' },
  'Surasena':                         { sphere: 'indian',                  name_zh: '蘇羅薩那' },
  'Vatsa':                            { sphere: 'indian',                  name_zh: '跋蹉' },
  'Malla':                            { sphere: 'indian',                  name_zh: '末羅' },
  'Simhala':                          { sphere: 'indian',                  name_zh: '楞伽（錫蘭）' },
  'Hindu kingdoms':                   { sphere: 'indian',                  name_zh: '印度教諸邦' },
  'Zhou states':                      { sphere: 'han',                     name_zh: '周諸國（春秋戰國）' },
  'Saba':                             { sphere: 'arabian',                 name_zh: '示巴' },
  'Meroe':                            { sphere: 'egyptian',                name_zh: '麥羅埃（庫施）' },
  'Blemmyes':                         { sphere: 'egyptian',                name_zh: '布雷米耶斯' },
  'Olmec':                            { sphere: 'mesoamerican',            name_zh: '奧爾梅克' },
  'Chavin':                           { sphere: 'andean',                  name_zh: '查文' },
  'Chorrera':                         { sphere: 'andean',                  name_zh: '喬雷拉' },
  'El Paraiso':                       { sphere: 'andean',                  name_zh: '帕拉伊索' },
  'Adena Culture':                    { sphere: '__tribal__',              name_zh: '阿迪納（北美林地）' },
  'Illyrians':                        { sphere: 'balkan',                  name_zh: '伊利里亞' },
  'Boii':                             { sphere: 'central-european',        name_zh: '波伊人' },
  'Ethiopian highland farmers':       { sphere: 'ethiopian',               name_zh: '衣索比亞高地' },

  // ===== bc323 / bc100 (Hellenistic + Han) =====
  'Macedonia':                        { sphere: 'aegean-asia-minor',       name_zh: '馬其頓' },
  'Macedonian Empire':                { sphere: 'aegean-asia-minor',       name_zh: '亞歷山大帝國' },
  'Seleucid Empire':                  { sphere: 'mesopotamian-levantine',  name_zh: '塞琉古帝國' },
  'Ptolemaic Kingdom':                { sphere: 'egyptian',                name_zh: '托勒密埃及' },
  'Antigonid Kingdom':                { sphere: 'aegean-asia-minor',       name_zh: '安提柯王朝' },
  'Maurya Empire':                    { sphere: 'indian',                  name_zh: '孔雀王朝' },
  'Maurya':                           { sphere: 'indian',                  name_zh: '孔雀王朝' },
  'Mauryan Empire':                   { sphere: 'indian',                  name_zh: '孔雀王朝' },
  'Han Empire':                       { sphere: 'han',                     name_zh: '漢' },
  'Han':                              { sphere: 'han',                     name_zh: '漢' },
  'Xiongnu':                          { sphere: 'mongolic-tungusic',       name_zh: '匈奴' },
  'Roman Republic':                   { sphere: 'latin-cultural',          name_zh: '羅馬共和' },
  'Roman Empire':                     { sphere: 'latin-cultural',          name_zh: '羅馬帝國' },
  'Parthian Empire':                  { sphere: 'persian',                 name_zh: '帕提亞（安息）' },
  'Parthians':                        { sphere: 'persian',                 name_zh: '帕提亞' },
  'Armenia':                          { sphere: 'caucasus',                name_zh: '亞美尼亞' },
  'Iberia':                           { sphere: 'caucasus',                name_zh: '伊比利亞（高加索）' },
  'Colchis':                          { sphere: 'caucasus',                name_zh: '科爾基斯' },
  'Aksum':                            { sphere: 'ethiopian',               name_zh: '阿克蘇姆' },
  'Axum':                             { sphere: 'ethiopian',               name_zh: '阿克蘇姆' },
  'Hadramaut':                        { sphere: 'arabian',                 name_zh: '哈德拉毛' },
  'Himyarite Kingdom':                { sphere: 'arabian',                 name_zh: '希木葉爾' },
  'Nabateans':                        { sphere: 'mesopotamian-levantine',  name_zh: '納巴泰' },

  // ===== 200/500/800 Late Antiquity → Early Medieval =====
  'Eastern Roman Empire':             { sphere: 'aegean-asia-minor',       name_zh: '東羅馬（拜占庭）' },
  'Western Roman Empire':             { sphere: 'latin-cultural',          name_zh: '西羅馬' },
  'Byzantine Empire':                 { sphere: 'aegean-asia-minor',       name_zh: '拜占庭帝國' },
  'Sasanian Empire':                  { sphere: 'persian',                 name_zh: '薩珊波斯' },
  'Sassanid Empire':                  { sphere: 'persian',                 name_zh: '薩珊波斯' },
  'Gupta Empire':                     { sphere: 'indian',                  name_zh: '笈多帝國' },
  'Vakataka':                         { sphere: 'indian',                  name_zh: '伐迦陀迦' },
  'Pallavas':                         { sphere: 'indian',                  name_zh: '帕拉瓦' },
  'Cholas':                           { sphere: 'indian',                  name_zh: '注輦' },
  'Cheras':                           { sphere: 'indian',                  name_zh: '哲羅' },
  'Pandyas':                          { sphere: 'indian',                  name_zh: '潘地亞' },
  'Kadambas':                         { sphere: 'indian',                  name_zh: '卡丹巴' },
  'Western Gangas':                   { sphere: 'indian',                  name_zh: '西恆伽' },
  'Vishnu-Kundins':                   { sphere: 'indian',                  name_zh: '毗濕奴坤丁' },
  'Kushan Principalities':            { sphere: 'indian',                  name_zh: '貴霜公國' },
  'Kushan Empire':                    { sphere: 'indian',                  name_zh: '貴霜帝國' },
  'Yamato':                           { sphere: 'kuroshio',                name_zh: '大和' },
  'Toba Wei':                         { sphere: 'han',                     name_zh: '北魏（拓跋）' },
  'Jin Empire':                       { sphere: 'han',                     name_zh: '晉' },
  'Tang Empire':                      { sphere: 'han',                     name_zh: '唐' },
  'Tang Chinese Empire':              { sphere: 'han',                     name_zh: '唐' },
  'Sui Empire':                       { sphere: 'han',                     name_zh: '隋' },
  'Koguryo':                          { sphere: 'kuroshio',                name_zh: '高句麗' },
  'Paekche':                          { sphere: 'kuroshio',                name_zh: '百濟' },
  'Silla':                            { sphere: 'kuroshio',                name_zh: '新羅' },
  'Ruanruan':                         { sphere: 'mongolic-tungusic',       name_zh: '柔然' },
  'Champa':                           { sphere: 'mekong',                  name_zh: '占婆' },
  'Funan':                            { sphere: 'mekong',                  name_zh: '扶南' },
  'Lavo':                             { sphere: 'mekong',                  name_zh: '羅渦（陀羅缽地）' },
  'Anglo-Saxons':                     { sphere: 'british-celtic',          name_zh: '盎格魯-撒克遜' },
  'Franks':                           { sphere: 'gallic-french',           name_zh: '法蘭克' },
  'Visigoths':                        { sphere: 'latin-cultural',          name_zh: '西哥德' },
  'Ostrogoths':                       { sphere: 'latin-cultural',          name_zh: '東哥德' },
  'Vandals':                          { sphere: 'carthaginian-maghreb',    name_zh: '汪達爾' },
  'Burgunds':                         { sphere: 'gallic-french',           name_zh: '勃艮第' },
  'Sveves':                           { sphere: 'latin-cultural',          name_zh: '蘇維匯' },
  'Saxons':                           { sphere: 'central-european',        name_zh: '撒克遜' },
  'Turingians':                       { sphere: 'central-european',        name_zh: '圖林根' },
  'Basks':                            { sphere: 'latin-cultural',          name_zh: '巴斯克' },
  'Empire of Ghana':                  { sphere: 'west-african-sahel',      name_zh: '加納帝國' },
  'Maya states':                      { sphere: 'mesoamerican',            name_zh: '馬雅諸邦' },
  'Maya city-states':                 { sphere: 'mesoamerican',            name_zh: '馬雅城邦' },
  'Teotihuacàn':                      { sphere: 'mesoamerican',            name_zh: '特奧蒂瓦坎' },
  'Teotihuacán':                      { sphere: 'mesoamerican',            name_zh: '特奧蒂瓦坎' },
  'Monte Albàn':                      { sphere: 'mesoamerican',            name_zh: '蒙特阿爾班' },
  'Monte Albán':                      { sphere: 'mesoamerican',            name_zh: '蒙特阿爾班' },
  'Moche':                            { sphere: 'andean',                  name_zh: '莫切' },
  'Nazca':                            { sphere: 'andean',                  name_zh: '納斯卡' },
  'Veracruz civilization':            { sphere: 'mesoamerican',            name_zh: '維拉克魯斯' },
  'Mixtec Empire':                    { sphere: 'mesoamerican',            name_zh: '米斯特克' },
  'Swedes':                           { sphere: 'nordic-livonian',         name_zh: '瑞典人' },
  'Saami':                            { sphere: 'nordic-livonian',         name_zh: '薩米人' },
  'Sámi':                             { sphere: 'nordic-livonian',         name_zh: '薩米人' },
  'Caliphate':                        { sphere: 'arabian',                 name_zh: '哈里發' },
  'Umayyad Caliphate':                { sphere: 'arabian',                 name_zh: '伍麥亞哈里發' },
  'Abbasid Caliphate':                { sphere: 'arabian',                 name_zh: '阿巴斯哈里發' },
  'Rashidun Caliphate':               { sphere: 'arabian',                 name_zh: '正統哈里發' },
  'Charlemagne Empire':               { sphere: 'gallic-french',           name_zh: '查理曼帝國' },
  'Carolingian Empire':               { sphere: 'gallic-french',           name_zh: '加洛林帝國' },
  'Holy Roman Empire':                { sphere: 'central-european',        name_zh: '神聖羅馬帝國' },

  // ===== 1000/1100/1279 Medieval =====
  'Song Empire':                      { sphere: 'han',                     name_zh: '宋' },
  'Song Chinese Empire':              { sphere: 'han',                     name_zh: '宋' },
  'Jin (Jurchen)':                    { sphere: 'mongolic-tungusic',       name_zh: '金（女真）' },
  'Liao Empire':                      { sphere: 'mongolic-tungusic',       name_zh: '遼' },
  'Tangut Empire':                    { sphere: 'tibetan',                 name_zh: '西夏' },
  'Western Xia':                      { sphere: 'tibetan',                 name_zh: '西夏' },
  'Tibet':                            { sphere: 'tibetan',                 name_zh: '吐蕃／西藏' },
  'Tibetan Empire':                   { sphere: 'tibetan',                 name_zh: '吐蕃' },
  'Khmer Empire':                     { sphere: 'mekong',                  name_zh: '高棉帝國' },
  'Pagan':                            { sphere: 'mekong',                  name_zh: '蒲甘' },
  'Sukhothai':                        { sphere: 'mekong',                  name_zh: '素可泰' },
  'Đại Việt':                         { sphere: 'mekong',                  name_zh: '大越' },
  'Dai Viet':                         { sphere: 'mekong',                  name_zh: '大越' },
  'Cambodia':                         { sphere: 'mekong',                  name_zh: '柬埔寨' },
  'Srivijaya':                        { sphere: 'banua',                   name_zh: '室利佛逝' },
  'Majapahit':                        { sphere: 'banua',                   name_zh: '滿者伯夷' },
  'Mongol Empire':                    { sphere: 'mongolic-tungusic',       name_zh: '蒙古帝國' },
  'Yuan Empire':                      { sphere: 'han',                     name_zh: '元（蒙古入主漢地）' },
  'Yuan Chinese Empire':              { sphere: 'han',                     name_zh: '元' },
  'Golden Horde':                     { sphere: 'turanian-turkic',         name_zh: '金帳汗國' },
  'Chagatai Khanate':                 { sphere: 'turanian-turkic',         name_zh: '察合台汗國' },
  'Ilkhanate':                        { sphere: 'persian',                 name_zh: '伊兒汗國' },
  'Il-khanate':                       { sphere: 'persian',                 name_zh: '伊兒汗國' },
  'Mamluke Sultanate':                { sphere: 'arabian',                 name_zh: '馬木留克' },
  'Mamluk Sultanate':                 { sphere: 'arabian',                 name_zh: '馬木留克' },
  'Sultanate of Delhi':               { sphere: 'indian',                  name_zh: '德里蘇丹國' },
  'Seljuk Empire':                    { sphere: 'anatolia',                name_zh: '塞爾柱帝國' },
  'Seljuks':                          { sphere: 'anatolia',                name_zh: '塞爾柱' },
  'Sultanate of Rum':                 { sphere: 'anatolia',                name_zh: '羅姆蘇丹國' },
  'Anatolian Beyliks':                { sphere: 'anatolia',                name_zh: '安納托利亞諸貝伊國' },
  'Seljuk Caliphate':                 { sphere: 'anatolia',                name_zh: '塞爾柱「哈里發」（羅姆蘇丹國）' },
  'Emirate of the White Sheep Turks': { sphere: 'anatolia',                name_zh: '白羊王朝（土庫曼-安納托利亞）' },
  'Kievan Rus':                       { sphere: 'russian-tatar',           name_zh: '基輔羅斯' },
  "Kievan Rus'":                      { sphere: 'russian-tatar',           name_zh: '基輔羅斯' },
  'Kingdom of England':               { sphere: 'british-celtic',          name_zh: '英格蘭王國' },
  'England':                          { sphere: 'british-celtic',          name_zh: '英格蘭' },
  'Scotland':                         { sphere: 'british-celtic',          name_zh: '蘇格蘭' },
  'Scottland':                        { sphere: 'british-celtic',          name_zh: '蘇格蘭' },
  'Ireland':                          { sphere: 'british-celtic',          name_zh: '愛爾蘭' },
  'France':                           { sphere: 'gallic-french',           name_zh: '法蘭西' },
  'Kingdom of France':                { sphere: 'gallic-french',           name_zh: '法蘭西王國' },
  'Hungary':                          { sphere: 'central-european',        name_zh: '匈牙利' },
  'Imperial Hungary':                 { sphere: 'central-european',        name_zh: '匈牙利王國' },
  'Poland':                           { sphere: 'lublin',                  name_zh: '波蘭' },
  'Poland-Lithuania':                 { sphere: 'lublin',                  name_zh: '波立聯邦' },
  'Lithuania':                        { sphere: 'lublin',                  name_zh: '立陶宛' },
  'Grand Duchy of Moscow':            { sphere: 'russian-tatar',           name_zh: '莫斯科大公國' },
  'Novgorod':                         { sphere: 'russian-tatar',           name_zh: '諾夫哥羅德' },
  'Novgorod-Seversky':                { sphere: 'russian-tatar',           name_zh: '諾夫哥羅德-謝韋爾斯基' },
  'Pskov':                            { sphere: 'russian-tatar',           name_zh: '普斯科夫' },
  'Ryazan':                           { sphere: 'russian-tatar',           name_zh: '梁贊' },
  'Castille':                         { sphere: 'latin-cultural',          name_zh: '卡斯提爾' },
  'Aragón':                           { sphere: 'latin-cultural',          name_zh: '阿拉貢' },
  'Aragon':                           { sphere: 'latin-cultural',          name_zh: '阿拉貢' },
  'Portugal':                         { sphere: 'latin-cultural',          name_zh: '葡萄牙' },
  'Navarre':                          { sphere: 'latin-cultural',          name_zh: '納瓦拉' },
  'Venice':                           { sphere: 'latin-cultural',          name_zh: '威尼斯' },
  'Papal States':                     { sphere: 'latin-cultural',          name_zh: '教皇國' },
  'Denmark':                          { sphere: 'nordic-livonian',         name_zh: '丹麥' },
  'Denmark-Norway':                   { sphere: 'nordic-livonian',         name_zh: '丹麥-挪威' },
  'Norway':                           { sphere: 'nordic-livonian',         name_zh: '挪威' },
  'Sweden':                           { sphere: 'nordic-livonian',         name_zh: '瑞典' },
  'Kalmar Union':                     { sphere: 'nordic-livonian',         name_zh: '卡爾馬聯盟' },
  'Iceland':                          { sphere: 'nordic-livonian',         name_zh: '冰島' },
  'Teutonic Knights':                 { sphere: 'lublin',                  name_zh: '條頓騎士團' },

  // ===== 1500 Age of Exploration =====
  'Ming Empire':                      { sphere: 'han',                     name_zh: '明' },
  'Ming Chinese Empire':              { sphere: 'han',                     name_zh: '明' },
  // 奧斯曼歸 anatolia（1071 後小亞細亞分立；雖然奧斯曼版圖含巴爾幹/黎凡特/埃及，
  // 但其核心與身分是安納托利亞-突厥，本期他地仍以邊界顯示）
  'Ottoman Empire':                   { sphere: 'anatolia',                name_zh: '奧斯曼帝國' },
  'Aztec Empire':                     { sphere: 'mesoamerican',            name_zh: '阿茲特克' },
  'Inca Empire':                      { sphere: 'andean',                  name_zh: '印加帝國' },
  'Mali':                             { sphere: 'west-african-sahel',      name_zh: '馬利帝國' },
  'Songhai':                          { sphere: 'west-african-sahel',      name_zh: '桑海帝國' },
  'Mwenemutapa':                      { sphere: 'southern-african-bantu',  name_zh: '穆塔帕' },
  'Congo':                            { sphere: 'central-african-congolese', name_zh: '剛果王國' },
  'Korea':                            { sphere: 'kuroshio',                name_zh: '朝鮮' },
  'Japan':                            { sphere: 'kuroshio',                name_zh: '日本' },
  'Vijayanagara':                     { sphere: 'indian',                  name_zh: '毗奢耶那伽羅' },
  'Bahmani Kingdom':                  { sphere: 'indian',                  name_zh: '巴赫曼尼' },
  'Bengal':                           { sphere: 'indian',                  name_zh: '孟加拉' },
  'Orissa':                           { sphere: 'indian',                  name_zh: '奧里薩' },
  'Rajastan':                         { sphere: 'indian',                  name_zh: '拉賈斯坦' },
  'Crimean Khanate':                  { sphere: 'turanian-turkic',         name_zh: '克里米亞汗國' },
  'White Horde':                      { sphere: 'turanian-turkic',         name_zh: '白帳汗國' },
  'Khanate of Sibir':                 { sphere: 'turanian-turkic',         name_zh: '失必兒汗國' },
  'Timurid Emirates':                 { sphere: 'turanian-turkic',         name_zh: '帖木兒諸邦' },
  'Timurid Empire':                   { sphere: 'turanian-turkic',         name_zh: '帖木兒帝國' },
  'Oirat Confederation':              { sphere: 'mongolic-tungusic',       name_zh: '瓦剌（衛拉特）' },
  'Ethiopia':                         { sphere: 'ethiopian',               name_zh: '衣索比亞' },
  'Adal':                             { sphere: 'east-african-swahili',    name_zh: '阿達爾' },
  'Funj':                             { sphere: 'east-african-swahili',    name_zh: '芬吉蘇丹國' },
  'Yemen':                            { sphere: 'arabian',                 name_zh: '葉門' },
  'Muscat':                           { sphere: 'arabian',                 name_zh: '馬斯喀特（阿曼）' },
  'Bornu-Kanem':                      { sphere: 'west-african-sahel',      name_zh: '加涅姆-博爾努' },
  'Hausa States':                     { sphere: 'west-african-sahel',      name_zh: '豪薩諸邦' },
  'Hafsid Caliphate':                 { sphere: 'carthaginian-maghreb',    name_zh: '哈夫斯哈里發' },
  'Zayyanid Caliphate':               { sphere: 'carthaginian-maghreb',    name_zh: '扎延王朝' },
  'Wattasid Caliphate':               { sphere: 'carthaginian-maghreb',    name_zh: '瓦塔斯王朝' },
  'Akan':                             { sphere: 'gulf-of-guinea',          name_zh: '阿坎' },
  'Oyo':                              { sphere: 'gulf-of-guinea',          name_zh: '奧約' },
  'Benin':                            { sphere: 'gulf-of-guinea',          name_zh: '貝寧（古王國）' },
  'Mossi States':                     { sphere: 'west-african-sahel',      name_zh: '莫西諸邦' },
  'Alwa':                             { sphere: 'east-african-swahili',    name_zh: '阿洛迪亞' },
  'Makkura':                          { sphere: 'east-african-swahili',    name_zh: '馬庫里亞' },
  'Madagascar':                       { sphere: 'east-african-swahili',    name_zh: '馬達加斯加' },
  'Ndongo':                           { sphere: 'central-african-congolese', name_zh: '恩東戈' },
  'Britany':                          { sphere: 'gallic-french',           name_zh: '布列塔尼' },
  'Brittany':                         { sphere: 'gallic-french',           name_zh: '布列塔尼' },
  'Swiss Confederation':              { sphere: 'central-european',        name_zh: '瑞士聯邦' },
  'Cyprus':                           { sphere: 'aegean-asia-minor',       name_zh: '賽普勒斯' },
  'Georgia':                          { sphere: 'caucasus',                name_zh: '喬治亞' },
  'Aceh':                             { sphere: 'banua',                   name_zh: '亞齊' },
  'Malacca':                          { sphere: 'banua',                   name_zh: '馬六甲' },
  'Brunei':                           { sphere: 'banua',                   name_zh: '汶萊' },
  'Ayutthaya':                        { sphere: 'mekong',                  name_zh: '大城王朝' },
  'Burmese kingdoms':                 { sphere: 'mekong',                  name_zh: '緬甸諸邦' },
  'Pegu':                             { sphere: 'mekong',                  name_zh: '勃固' },
  'Laos':                             { sphere: 'mekong',                  name_zh: '寮國' },
  'Arakan':                           { sphere: 'mekong',                  name_zh: '阿拉幹' },
  'Sinhalese kingdoms':               { sphere: 'indian',                  name_zh: '錫蘭諸邦' },
  'Maldives':                         { sphere: 'indian',                  name_zh: '馬爾地夫' },
  'Taiwan':                           { sphere: 'banua',                   name_zh: '台灣（南島）' },
  'Philippines':                      { sphere: 'banua',                   name_zh: '菲律賓' },
  'Maori':                            { sphere: 'australasian',            name_zh: '毛利' },
  'Polynesians':                      { sphere: 'pacific',                 name_zh: '玻里尼西亞' },
  'Maldivians':                       { sphere: 'indian',                  name_zh: '馬爾地夫人' },

  // ===== 1815 Post-Napoleonic =====
  'Russian Empire':                   { sphere: 'russian-tatar',           name_zh: '俄羅斯帝國' },
  'Habsburg Empire':                  { sphere: 'central-european',        name_zh: '哈布斯堡' },
  'Austrian Empire':                  { sphere: 'central-european',        name_zh: '奧地利帝國' },
  'Prussia':                          { sphere: 'central-european',        name_zh: '普魯士' },
  'Kingdom of Prussia':               { sphere: 'central-european',        name_zh: '普魯士王國' },
  'Spain':                            { sphere: 'latin-cultural',          name_zh: '西班牙' },
  'United Kingdom':                   { sphere: 'british-celtic',          name_zh: '英國' },
  'Qing Empire':                      { sphere: 'han',                     name_zh: '清' },
  'Qing Chinese Empire':              { sphere: 'han',                     name_zh: '清' },
  'Mughal Empire':                    { sphere: 'indian',                  name_zh: '蒙兀兒帝國' },
  'British India':                    { sphere: 'indian',                  name_zh: '英屬印度' },
  'Burma':                            { sphere: 'mekong',                  name_zh: '緬甸' },
  'Iran':                             { sphere: 'persian',                 name_zh: '伊朗（卡扎爾）' },
  'Persia':                           { sphere: 'persian',                 name_zh: '波斯' },
  'Egypt under Ottoman':              { sphere: 'egyptian',                name_zh: '奧斯曼治下埃及' },
  'United States':                    { sphere: 'anglo-american',          name_zh: '美國' },
  'Brazil':                           { sphere: 'amazonian-brazilian',     name_zh: '巴西' },
  'Mexico':                           { sphere: 'mesoamerican',            name_zh: '墨西哥' },
  'Gran Colombia':                    { sphere: 'andean',                  name_zh: '大哥倫比亞' },
  'Provinces of the Río de la Plata': { sphere: 'southern-cone',           name_zh: '拉布拉他' },
  'Sokoto Caliphate':                 { sphere: 'west-african-sahel',      name_zh: '索科托哈里發' },
  'Tukulor Empire':                   { sphere: 'west-african-sahel',      name_zh: '杜庫魯帝國' },
  'Toucouleur Empire':                { sphere: 'west-african-sahel',      name_zh: '杜庫魯帝國' },
  'Buganda':                          { sphere: 'east-african-swahili',    name_zh: '布干達' },
  'Zulu Kingdom':                     { sphere: 'southern-african-bantu',  name_zh: '祖魯王國' },
  'Boer Republics':                   { sphere: 'southern-african-bantu',  name_zh: '波耳共和國' },

  // ===== 1914 / 2000 modern (large catch-all below) =====
  'France & Colonies':                { sphere: 'gallic-french',           name_zh: '法蘭西及殖民地' },
  'British Empire':                   { sphere: 'british-celtic',          name_zh: '大英帝國' },
  'Portuguese Empire':                { sphere: 'latin-cultural',          name_zh: '葡萄牙帝國' },
  'Spanish Empire':                   { sphere: 'latin-cultural',          name_zh: '西班牙帝國' },
  'German Empire':                    { sphere: 'central-european',        name_zh: '德意志帝國' },
  'Austria-Hungary':                  { sphere: 'central-european',        name_zh: '奧匈帝國' },
  'Italy':                            { sphere: 'latin-cultural',          name_zh: '義大利' },
  'Belgium':                          { sphere: 'low-countries',           name_zh: '比利時' },
  'Netherlands':                      { sphere: 'low-countries',           name_zh: '荷蘭' },
  'Switzerland':                      { sphere: 'central-european',        name_zh: '瑞士' },
  'Greece':                           { sphere: 'aegean-asia-minor',       name_zh: '希臘' },
  'Bulgaria':                         { sphere: 'balkan',                  name_zh: '保加利亞' },
  'Romania':                          { sphere: 'balkan',                  name_zh: '羅馬尼亞' },
  'Serbia':                           { sphere: 'balkan',                  name_zh: '塞爾維亞' },
  'Albania':                          { sphere: 'balkan',                  name_zh: '阿爾巴尼亞' },
  'Montenegro':                       { sphere: 'balkan',                  name_zh: '蒙特內哥羅' },

  // ===== 2000 modern country mapping (from existing COUNTRY_REALM) =====
  // -- 中央 --
  'Iraq':                             { sphere: 'mesopotamian-levantine',  name_zh: '伊拉克' },
  'Syria':                            { sphere: 'mesopotamian-levantine',  name_zh: '敘利亞' },
  'Lebanon':                          { sphere: 'mesopotamian-levantine',  name_zh: '黎巴嫩' },
  'Israel':                           { sphere: 'mesopotamian-levantine',  name_zh: '以色列' },
  'Jordan':                           { sphere: 'mesopotamian-levantine',  name_zh: '約旦' },
  'Palestine':                        { sphere: 'mesopotamian-levantine',  name_zh: '巴勒斯坦' },
  'Sudan':                            { sphere: 'egyptian',                name_zh: '蘇丹' },
  'Libya':                            { sphere: 'carthaginian-maghreb',    name_zh: '利比亞' },
  'Tunisia':                          { sphere: 'carthaginian-maghreb',    name_zh: '突尼西亞' },
  'Algeria':                          { sphere: 'carthaginian-maghreb',    name_zh: '阿爾及利亞' },
  'Morocco':                          { sphere: 'carthaginian-maghreb',    name_zh: '摩洛哥' },
  'Turkey':                           { sphere: 'anatolia',                name_zh: '土耳其' },
  'Afghanistan':                      { sphere: 'persian',                 name_zh: '阿富汗' },
  'Tajikistan':                       { sphere: 'persian',                 name_zh: '塔吉克' },
  'Armenia':                          { sphere: 'caucasus',                name_zh: '亞美尼亞' },
  'Azerbaijan':                       { sphere: 'caucasus',                name_zh: '亞塞拜然' },
  'Saudi Arabia':                     { sphere: 'arabian',                 name_zh: '沙烏地阿拉伯' },
  'Oman':                             { sphere: 'arabian',                 name_zh: '阿曼' },
  'Bahrain':                          { sphere: 'arabian',                 name_zh: '巴林' },
  'Qatar':                            { sphere: 'arabian',                 name_zh: '卡達' },
  'United Arab Emirates':             { sphere: 'arabian',                 name_zh: '阿聯酋' },
  'Kuwait':                           { sphere: 'arabian',                 name_zh: '科威特' },
  // -- 東方 --
  'Pakistan':                         { sphere: 'indian',                  name_zh: '巴基斯坦' },
  'India':                            { sphere: 'indian',                  name_zh: '印度' },
  'Nepal':                            { sphere: 'indian',                  name_zh: '尼泊爾' },
  'Sri Lanka':                        { sphere: 'indian',                  name_zh: '斯里蘭卡' },
  'Bangladesh':                       { sphere: 'indian',                  name_zh: '孟加拉' },
  'China':                            { sphere: 'han',                     name_zh: '中國' },
  'Bhutan':                           { sphere: 'tibetan',                 name_zh: '不丹' },
  // -- 拉美 --
  'Guatemala':                        { sphere: 'mesoamerican',            name_zh: '瓜地馬拉' },
  'Belize':                           { sphere: 'mesoamerican',            name_zh: '貝里斯' },
  'Honduras':                         { sphere: 'mesoamerican',            name_zh: '宏都拉斯' },
  'El Salvador':                      { sphere: 'mesoamerican',            name_zh: '薩爾瓦多' },
  'Nicaragua':                        { sphere: 'mesoamerican',            name_zh: '尼加拉瓜' },
  'Costa Rica':                       { sphere: 'mesoamerican',            name_zh: '哥斯大黎加' },
  'Panama':                           { sphere: 'mesoamerican',            name_zh: '巴拿馬' },
  'Peru':                             { sphere: 'andean',                  name_zh: '秘魯' },
  'Bolivia':                          { sphere: 'andean',                  name_zh: '玻利維亞' },
  'Ecuador':                          { sphere: 'andean',                  name_zh: '厄瓜多' },
  'Colombia':                         { sphere: 'andean',                  name_zh: '哥倫比亞' },
  'Cuba':                             { sphere: 'caribbean',               name_zh: '古巴' },
  'Dominican Republic':               { sphere: 'caribbean',               name_zh: '多明尼加' },
  'Haiti':                            { sphere: 'caribbean',               name_zh: '海地' },
  'Jamaica':                          { sphere: 'caribbean',               name_zh: '牙買加' },
  'Venezuela':                        { sphere: 'caribbean',               name_zh: '委內瑞拉' },
  'Guyana':                           { sphere: 'caribbean',               name_zh: '蓋亞那' },
  'Suriname':                         { sphere: 'caribbean',               name_zh: '蘇利南' },
  'Chile':                            { sphere: 'southern-cone',           name_zh: '智利' },
  'Argentina':                        { sphere: 'southern-cone',           name_zh: '阿根廷' },
  'Paraguay':                         { sphere: 'southern-cone',           name_zh: '巴拉圭' },
  'Uruguay':                          { sphere: 'southern-cone',           name_zh: '烏拉圭' },
  // -- 西方 --
  'Vatican':                          { sphere: 'latin-cultural',          name_zh: '梵蒂岡' },
  'Malta':                            { sphere: 'latin-cultural',          name_zh: '馬爾他' },
  'Macedonia':                        { sphere: 'balkan',                  name_zh: '北馬其頓' },
  'Croatia':                          { sphere: 'balkan',                  name_zh: '克羅埃西亞' },
  'Bosnia and Herzegovina':           { sphere: 'balkan',                  name_zh: '波士尼亞' },
  'Slovenia':                         { sphere: 'balkan',                  name_zh: '斯洛維尼亞' },
  'Moldova':                          { sphere: 'balkan',                  name_zh: '摩爾多瓦' },
  'Germany':                          { sphere: 'central-european',        name_zh: '德國' },
  'Austria':                          { sphere: 'central-european',        name_zh: '奧地利' },
  'Czech Republic':                   { sphere: 'central-european',        name_zh: '捷克' },
  'Slovakia':                         { sphere: 'central-european',        name_zh: '斯洛伐克' },
  'Luxembourg':                       { sphere: 'low-countries',           name_zh: '盧森堡' },
  'Latvia':                           { sphere: 'lublin',                  name_zh: '拉脫維亞' },
  'Estonia':                          { sphere: 'nordic-livonian',         name_zh: '愛沙尼亞' },
  'Finland':                          { sphere: 'nordic-livonian',         name_zh: '芬蘭' },
  // -- 亞太 --
  'Cambodia':                         { sphere: 'mekong',                  name_zh: '柬埔寨' },
  'Vietnam':                          { sphere: 'mekong',                  name_zh: '越南' },
  'Thailand':                         { sphere: 'mekong',                  name_zh: '泰國' },
  'Korea, Democratic People\'s Republic of': { sphere: 'kuroshio',         name_zh: '北韓' },
  'Korea, Republic of':               { sphere: 'kuroshio',                name_zh: '南韓' },
  'Indonesia':                        { sphere: 'banua',                   name_zh: '印尼' },
  'Malaysia':                         { sphere: 'banua',                   name_zh: '馬來西亞' },
  'Singapore':                        { sphere: 'banua',                   name_zh: '新加坡' },
  'Fiji':                             { sphere: 'pacific',                 name_zh: '斐濟' },
  'Papua New Guinea':                 { sphere: 'pacific',                 name_zh: '巴布亞紐幾內亞' },
  'Australia':                        { sphere: 'australasian',            name_zh: '澳大利亞' },
  'New Zealand':                      { sphere: 'australasian',            name_zh: '紐西蘭' },
  // -- 南方 --
  'Eritrea':                          { sphere: 'ethiopian',               name_zh: '厄利垂亞' },
  'Senegal':                          { sphere: 'west-african-sahel',      name_zh: '塞內加爾' },
  'Niger':                            { sphere: 'west-african-sahel',      name_zh: '尼日' },
  'Chad':                             { sphere: 'west-african-sahel',      name_zh: '查德' },
  'Burkina Faso':                     { sphere: 'west-african-sahel',      name_zh: '布吉納法索' },
  'Mauritania':                       { sphere: 'west-african-sahel',      name_zh: '茅利塔尼亞' },
  'Gambia, The':                      { sphere: 'west-african-sahel',      name_zh: '甘比亞' },
  'Guinea':                           { sphere: 'west-african-sahel',      name_zh: '幾內亞' },
  'Guinea-Bissau':                    { sphere: 'west-african-sahel',      name_zh: '幾內亞比索' },
  'Cape Verde':                       { sphere: 'west-african-sahel',      name_zh: '維德角' },
  'Somalia':                          { sphere: 'east-african-swahili',    name_zh: '索馬利亞' },
  'Kenya':                            { sphere: 'east-african-swahili',    name_zh: '肯亞' },
  'Tanzania, United Republic of':     { sphere: 'east-african-swahili',    name_zh: '坦尚尼亞' },
  'Uganda':                           { sphere: 'east-african-swahili',    name_zh: '烏干達' },
  'Rwanda':                           { sphere: 'east-african-swahili',    name_zh: '盧安達' },
  'Burundi':                          { sphere: 'east-african-swahili',    name_zh: '蒲隆地' },
  'Djibouti':                         { sphere: 'east-african-swahili',    name_zh: '吉布地' },
  'Liberia':                          { sphere: 'gulf-of-guinea',          name_zh: '賴比瑞亞' },
  'Sierra Leone':                     { sphere: 'gulf-of-guinea',          name_zh: '獅子山' },
  'Ivory Coast':                      { sphere: 'gulf-of-guinea',          name_zh: '象牙海岸' },
  'Ghana':                            { sphere: 'gulf-of-guinea',          name_zh: '迦納' },
  'Togo':                             { sphere: 'gulf-of-guinea',          name_zh: '多哥' },
  'Nigeria':                          { sphere: 'gulf-of-guinea',          name_zh: '奈及利亞' },
  'Cameroon':                         { sphere: 'central-african-congolese', name_zh: '喀麥隆' },
  'Gabon':                            { sphere: 'central-african-congolese', name_zh: '加彭' },
  'Equatorial Guinea':                { sphere: 'central-african-congolese', name_zh: '赤道幾內亞' },
  'Central African Republic':         { sphere: 'central-african-congolese', name_zh: '中非共和國' },
  'Zaire':                            { sphere: 'central-african-congolese', name_zh: '剛果民主共和國' },
  'Zimbabwe':                         { sphere: 'southern-african-bantu',  name_zh: '辛巴威' },
  'Mozambique':                       { sphere: 'southern-african-bantu',  name_zh: '莫三比克' },
  'South Africa':                     { sphere: 'southern-african-bantu',  name_zh: '南非' },
  'Angola':                           { sphere: 'southern-african-bantu',  name_zh: '安哥拉' },
  'Namibia':                          { sphere: 'southern-african-bantu',  name_zh: '納米比亞' },
  'Botswana':                         { sphere: 'southern-african-bantu',  name_zh: '波札那' },
  'Zambia':                           { sphere: 'southern-african-bantu',  name_zh: '尚比亞' },
  'Malawi':                           { sphere: 'southern-african-bantu',  name_zh: '馬拉威' },
  'Lesotho':                          { sphere: 'southern-african-bantu',  name_zh: '賴索托' },
  'Swaziland':                        { sphere: 'southern-african-bantu',  name_zh: '史瓦帝尼' },
  // -- 北方 --
  'Uzbekistan':                       { sphere: 'turanian-turkic',         name_zh: '烏茲別克' },
  'Turkmenistan':                     { sphere: 'turanian-turkic',         name_zh: '土庫曼' },
  'Kyrgyzstan':                       { sphere: 'turanian-turkic',         name_zh: '吉爾吉斯' },
  'Kazakhstan':                       { sphere: 'turanian-turkic',         name_zh: '哈薩克' },
  'Ukraine':                          { sphere: 'lublin',                  name_zh: '烏克蘭（西部）' },  // simplified, 1815-2000
  'Byelarus':                         { sphere: 'russian-tatar',           name_zh: '白俄羅斯' },
  'Belarus':                          { sphere: 'russian-tatar',           name_zh: '白俄羅斯' },
  'Russia':                           { sphere: 'russian-tatar',           name_zh: '俄羅斯' },
  'Mongolia':                         { sphere: 'mongolic-tungusic',       name_zh: '蒙古' },
  // -- 北美 --
  'Canada':                           { sphere: 'anglo-american',          name_zh: '加拿大' },
  'Greenland':                        { sphere: 'arctic',                  name_zh: '格陵蘭' },
}

// ----- run -----
function main() {
  const allFeatures = []
  const unmappedCounts = {}

  for (let i = 0; i < SNAPSHOTS.length; i++) {
    const [yearFrom, fname] = SNAPSHOTS[i]
    const yearTo = i + 1 < SNAPSHOTS.length ? SNAPSHOTS[i + 1][0] - 1 : 9999

    const path = join(HBM_DIR, fname)
    if (!existsSync(path)) {
      console.warn(`SKIP ${fname} (not found)`)
      continue
    }
    const raw = readFileSync(path, 'utf8')
    const gj = JSON.parse(raw)

    let kept = 0
    for (const f of gj.features) {
      const nm = f.properties?.NAME?.trim()
      if (!nm) continue
      const m = MAP[nm]
      if (!m) {
        if (!unmappedCounts[nm]) unmappedCounts[nm] = 0
        unmappedCounts[nm] += 1
        continue
      }
      if (m.sphere === '__tribal__' || m.sphere === '__skip__') continue
      // Tag feature
      allFeatures.push({
        type: 'Feature',
        properties: {
          sphere_id: m.sphere,
          name_zh: m.name_zh,
          name_en: nm,
          year_from: yearFrom,
          year_to: yearTo,
          snapshot: yearFrom,  // for debugging
        },
        geometry: f.geometry,
      })
      kept += 1
    }
    console.log(`${fname.padEnd(28)} y=${String(yearFrom).padStart(5)}..${String(yearTo).padStart(5)}  total=${gj.features.length}  kept=${kept}`)
  }

  // Output
  const out = {
    type: 'FeatureCollection',
    name: 'historical-spheres',
    crs: { type: 'name', properties: { name: 'urn:ogc:def:crs:OGC:1.3:CRS84' } },
    attribution: 'CC BY-NC-SA 4.0 — Andrei Ourednik (aourednik/historical-basemaps)',
    features: allFeatures,
  }
  writeFileSync(OUT_FILE, JSON.stringify(out))
  const sz = Math.round(JSON.stringify(out).length / 1024)
  console.log(`\n→ wrote ${OUT_FILE} (${allFeatures.length} features, ${sz} KB)`)

  // Top unmapped
  const top = Object.entries(unmappedCounts).sort((a, b) => b[1] - a[1]).slice(0, 60)
  console.log(`\nTop unmapped names (consider adding to MAP):`)
  for (const [nm, cnt] of top) console.log(`  ${nm}  (×${cnt})`)
}

main()
