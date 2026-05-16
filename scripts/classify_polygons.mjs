#!/usr/bin/env node
/**
 * Classify each historical-states.geojson polygon NAME as is_state (政權／酋邦／城邦) or not.
 *
 * 標準（user-defined）：
 *   - 至少達到「酋邦 (chiefdom)」、「城邦 (city-state)」或「建立王權的遊牧帝國」
 *   - 純部落 (band/tribe) / 語族 / 考古文化群 / 古人類學名 / 狩獵採集者群 → 排除
 *
 * Output: public/maps/polygon-classifications.json
 *   {
 *     "Han Empire": { is_state: true,  reason: "polity-suffix" },
 *     "Polynesians": { is_state: false, reason: "language-family" },
 *     ...
 *   }
 */
import { readFileSync, writeFileSync } from 'node:fs'

const STATES_FILE = 'public/maps/historical-states.geojson'
const OUT_FILE = 'public/maps/polygon-classifications.json'

const states = JSON.parse(readFileSync(STATES_FILE, 'utf8'))
const polyZh = (() => { try { return JSON.parse(readFileSync('public/maps/polygon-names-zh.json','utf8')) } catch { return {} } })()
const adm0 = JSON.parse(readFileSync('public/maps/ne_50m_admin_0_countries.geojson','utf8'))

// 從 data/maps/historical-states-db.ts 的 STATE_DETAILS 抽 keys（人工撰寫的詳細，必為政權）
const dbTs = readFileSync('data/maps/historical-states-db.ts','utf8')
const STATE_DETAILS_KEYS = new Set([...dbTs.matchAll(/^  '([^']+)': \{/gm)].map(m => m[1]))
const allNames = new Set()
for (const f of states.features) allNames.add(f.properties.name)

// 從 NE admin_0 抽英文國名 set — 在這裡的視為現代國家（政權）
const adm0NameSet = new Set()
for (const f of adm0.features) {
  for (const k of ['NAME','NAME_EN','NAME_LONG','ADMIN','SOVEREIGNT','BRK_NAME']) {
    const v = f.properties[k]
    if (v) adm0NameSet.add(v)
  }
}

// ---- Rule layer 1: STRONG WHITELIST (definite polities) ----
// 含有這些 keyword/suffix → 必為政權。
const POLITY_PATTERNS = [
  /\bEmpires?\b/i,
  /\bKingdoms?\b/i,
  /\bDynasty\b/i,
  /\bDynasties\b/i,
  /\bCaliphates?\b/i,
  /\bSultanates?\b/i,
  /\bKhanates?\b/i,
  /\bTsardom\b/i,
  /\bShogunate\b/i,
  /\bDespotate\b/i,
  /\bRepublic\b/i,
  /\bConfederation\b/i,
  /\bConfederacy\b/i,
  /\bFederation\b/i,
  /\bUnion\b/i,
  /\bDuchy\b/i,
  /\bGrand Duchy\b/i,
  /\bPrincipality\b/i,
  /\bEmirate\b/i,
  /\bBeylik\b/i,
  /\bCounty of\b/i,
  /\bMarch of\b/i,
  /\bMargrave/i,
  /\bLandgrave/i,
  /\bArchbishop/i,
  /\bBishopric\b/i,
  /\bImperial Abbey\b/i,
  /\bImperial Free City\b/i,
  /\bFree City\b/i,
  /\bCity-state/i,
  /\bcity-states\b/i,
  /\bcity states\b/i,
  /\bChiefdom/i,                          // 用戶明確：酋邦算
  /\bChieftaincy\b/i,
  /\bState\b/i,                           // "X State"
  /\bStates\b/i,                          // "Maya states", "Hindu kingdoms" 都算
  /\bLeague\b/i,                          // Hanseatic League 等
  /\bProtectorate\b/i,
  /\bDominion\b/i,
  /\bColony\b/i,
  /\bColonies\b/i,
  /\bMandate\b/i,
  /\bTerritory of\b/i,
  /\bGovernorate\b/i,
  /\bProvince of\b/i,
  /\bViceroyalty\b/i,
  /\bCrown of\b/i,
  /\bRealm of\b/i,
  /\bConfederated\b/i,                    // 但部分 Confederated Tribes 是現代美國保留地，後面再排
  /\bHordes?\b/i,                         // Golden Horde, White Horde
  /\bCalif\b/i,
  // 殖民地／屬地 prefix — Portuguese Brazil, Spanish Sahara, French West Africa 等
  /^(Portuguese|Spanish|French|British|Dutch|German|Italian|Russian|Belgian|Soviet|Japanese|Ottoman|Mughal|Habsburg|Austrian|Norwegian|Swedish|Danish|Polish|Finnish|Roman|Byzantine)\s+[A-Z]/i,
  /\b(Vice[\s-]?royalty|Viceroyalty)\b/i,
  /\bAdministration of\b/i,
  /\bGovernment of\b/i,
  /\bRegency of\b/i,
  /\bRegency\b/i,
  /\bRegent of\b/i,
  /\bPrincipal/i,
  /\bSan\s|^Saint\s/i,                    // 假設 San X / Saint X 是城邦／國家
]

// ---- Rule layer 2: STRONG BLACKLIST (definite non-state) ----
const NON_STATE_PATTERNS = [
  // 古人類學
  /\bHomo (erectus|sapiens|heidelbergensis|neanderthalensis|naledi|floresiensis|habilis)\b/i,
  /\bNeanderthal/i,
  /\bDenisovan/i,
  /\bPaleo[\s-]?(Inuit|Indian|Eskimo|American|Korean|Asian|African|Siberian)/i,
  /\bArchaic Humans?\b/i,
  /\bMesolithic Hunter/i,
  /\bNeolithic Farmer/i,
  /\bNeolithic Hunter/i,

  // 經濟形態描述
  /Hunter[\s-]?Forager/i,
  /Hunter[\s-]?gatherer/i,
  /\bForag(er|ing)\b/i,
  /\bGatherers?\b/i,
  /shellfish gather/i,
  /marine mammal hunter/i,
  /\b(bison|cereal|maize|manioc|rice) (hunter|farmer)/i,
  /\bfarmers?\b/i,
  /\bhunters?\b/i,
  /\bfisherm?(en|an|ing)\b/i,
  /\bpastoralis/i,
  /\bnomad(ic|s)?\b/i,                    // 純粹的 "nomadic tribes"

  // 部落／保留地（19-20 世紀美國印第安保留地）
  /\bTribes? of\b/i,                      // "Tribes of X"
  /Tribe \(.*\)/i,
  /Reservation\)/i,
  /\bReservations?\b/i,
  /\bConfederated Tribes?/i,              // "Confederated Tribes of Grand Ronde" 是保留地
  /\bSeminole Tribe/i,

  // 語族／考古文化常見後綴
  /\bculture\b/i,                         // "Beaker culture", "Andronovo culture"
  /\bcivili[sz]ation\b/i,                 // 有些算（Indus valley）有些不算（Cucuteni-Trypillia civilization）— 用 override
  /\bcomplex\b/i,                         // "Yangshao complex" 等考古學
  /\bphase\b/i,
  /\bperiod\b/i,
  /\bTradition\b/i,
  /\bHorizon\b/i,                         // 「文化期」
  /\bware\b/i,                            // "Linear Pottery ware", "combware"

  // 純語族／民族集合
  /\bspeakers?\b/i,
  /\blanguage family\b/i,
  /\bIndigenous peoples\b/i,
]

// ---- Rule layer 3: 已知政權／文明 override（white）— rules 抓不到的明確國家 ----
const KNOWN_STATES = new Set([
  // 古近東
  'Sumer','Sumero-Akkadian','Akkad','Babylonia','Assyria','Egypt','Hittites','Mitanni',
  'Mittani','Elam','Hurrian Kingdoms','Ur','Lagash','Mari','Ebla','Yamhad','Kizzuwatna',
  'Mira','Arzawa','Wilusa','Ahhiyawa','Alashiya','Phoenicia','Aram','Ammon','Moab','Edom',
  'Israel','Judah','Saba','Sheba','Hadramaut','Qataban','Awsan','Ma\'in','Himyar','Saba','Lihyan',
  'Nabateans','Nabatean Kingdom','Palmyra','Hatra','Osroene','Adiabene','Atropatene',
  'Commagene','Cilicia','Kingdom of Tyre','Tyre','Sidon','Byblos','Ugarit','Carchemish',
  'Urartu','Mannaea','Phrygia','Lydia','Caria','Lycia','Pamphylia','Pisidia','Cappadocia',
  'Pontus','Bithynia','Galatia','Paphlagonia','Mysia','Troas','Aeolis','Ionia','Doris',
  'Achaemenid Empire','Median Empire','Medes','Parthia','Sasanian Empire','Sassanid Empire',
  // 印度
  'Magadha','Kosala','Kasi','Avanti','Vatsa','Kuru','Pancala','Surasena','Malla','Vajji',
  'Gandhāra','Gandhara','Anga','Asmaka','Chedi','Matsya','Gandhāra','Kamboja','Kekaya',
  'Sindhu','Mahishaka','Pulinda','Andhra','Kalinga','Pandya','Chola','Chera','Pallava',
  'Vakataka','Cālukya','Chalukya','Pala','Sena','Rashtrakuta','Pratihara','Hindu kingdoms',
  'Sinhala','Simhala','Maldives','Sinhalese kingdoms','Bahmani Kingdom','Vijayanagara',
  'Bengal','Orissa','Rajastan','Bahmani Kingdom','Bahmani','Maurya','Mauryan Empire','Maurya Empire',
  'Sunga','Kanva','Gupta Empire','Harsha','Pala Empire','Solanki','Chahamana','Tomara',
  'Eastern Ganga','Sena','Kakatiya','Yadava','Hoysala','Reddi','Madurai',
  // 東亞
  'Xia','Shang','Zhou','Zhou states','Spring and Autumn','Warring States','Qin','Han',
  'Wei','Shu','Wu','Yue','Chu','Yan','Qi','Lu','Song','Zhao','Zhoa','Han Empire','Han Chinese Empire',
  'Cao Wei','Eastern Wu','Shu Han','Three Kingdoms','Western Jin','Eastern Jin',
  'Northern Wei','Toba Wei','Liu Song','Southern Qi','Liang','Chen','Sui','Sui Empire',
  'Tang','Tang Empire','Tang Chinese Empire','Five Dynasties','Northern Song','Southern Song',
  'Song Empire','Song Chinese Empire','Liao','Liao Empire','Western Xia','Tangut Empire',
  'Jin (Jurchen)','Jurchen Jin','Mongol Empire','Yuan','Yuan Empire','Yuan Chinese Empire',
  'Ming','Ming Empire','Ming Chinese Empire','Qing','Qing Empire','Qing Chinese Empire',
  'Sinic',                                // 華夏（早期中華）算
  'Tibet','Tibetan Empire','Zhangzhung','Zhangzhung Kingdom','Pyu','Mon',
  'Goguryeo','Koguryo','Baekje','Paekche','Silla','Gaya','Balhae','Goryeo','Joseon',
  'Korea','Gojoseon','Jin (Korea)','Mahan','Byeonhan','Jinhan',
  'Yamato','Japan','Empire of Japan','Imperial Japan','Tokugawa Shogunate','Ashikaga Shogunate',
  'Kamakura Shogunate','Heian Japan','Nara Japan','Asuka Japan','Kofun period',
  // 東南亞
  'Funan','Chenla','Khmer Empire','Khmer','Champa','Đại Việt','Dai Viet','Annam','Cochin China',
  'Lan Xang','Laos','Lavo','Sukhothai','Ayutthaya','Rattanakosin','Rattanakosin Kingdom',
  'Pagan','Bagan','Toungoo','Konbaung','Burma','Pegu','Arakan','Mon Kingdom','Hanthawaddy',
  'Srivijaya','Srivijaya Empire','Mataram','Majapahit','Singhasari','Aceh','Malacca','Brunei',
  'Sailendra','Demak','Pajang','Banten','Madura','Bali','Buton','Ternate','Tidore',
  // 中亞
  'Xiongnu','Wusun','Yuezhi','Kushan Empire','Kushan Principalities','Hephthalites','White Huns',
  'Rouran','Ruanruan','Göktürk','Göktürk Khaganate','Western Turkic Khaganate','Eastern Turkic Khaganate',
  'Uyghur Khaganate','Kyrgyz Khaganate','Karluk Yabghu','Kara-Khanid Khanate',
  'Khazar Khaganate','Volga Bulgaria','Pechenegs','Cumans','Kipchaks',
  'Khwarazmian Empire','Samanid Empire','Ghaznavid Empire','Ghurid Sultanate','Karakhanids',
  'Timurid Empire','Timurid Emirates','Mughal Empire','Bukhara','Khiva','Kokand',
  'Crimean Khanate','Khanate of Sibir','Khanate of Kazan','Khanate of Astrakhan','Nogai Horde',
  'White Horde','Golden Horde','Chagatai Khanate','Ilkhanate','Il-khanate','Oirat Confederation',
  'Dzungar Khanate','Kazakh Khanate','central Asian khanates',
  // 中東伊斯蘭
  'Rashidun Caliphate','Umayyad Caliphate','Abbasid Caliphate','Fatimid Caliphate',
  'Ayyubid Sultanate','Mamluk Sultanate','Mamluke Sultanate','Ottoman Empire','Seljuk Empire',
  'Seljuks','Sultanate of Rum','Anatolian Beyliks','Aq Qoyunlu','Kara Koyunlu',
  'Safavid Empire','Persia','Iran','Qajar','Pahlavi','Afsharid','Zand',
  'Sultanate of Delhi','Mughal Empire','Sokoto Caliphate','Adal Sultanate','Adal',
  'Hejaz','Hail','Asir','Najd','Trucial Oman','Muscat and Oman','Oman','Yemen',
  // 歐洲
  'Etrurians','Etruscans','Sabini','Sabines','Samnites','Latins','Volsci','Picentes','Lucani','Bruttii',
  'Greek city-states','Greek colonies','Macedonia','Macedonian Empire','Epirus','Thessaly',
  'Thrace','Dacia','Getae','Scordisci','Boii','Helvetii','Belgae','Aedui','Arverni',
  'Britania','Gaul','Iberia (Iberian)','Lusitania','Tartessos','Celtiberia',
  'Roman Republic','Rome','Roman Empire','Byzantine Empire','Eastern Roman Empire',
  'Western Roman Empire','Ostrogothic Kingdom','Visigothic Kingdom','Vandal Kingdom',
  'Suebic Kingdom','Burgundian Kingdom','Frankish Kingdom','Lombard Kingdom',
  'Anglo-Saxons','Mercia','Wessex','Northumbria','East Anglia','Sussex','Kent','Essex',
  'Kingdom of England','England','Scotland','Scottland','Ireland','Wales','Britany','Brittany',
  'Picts','Dál Riata','Strathclyde',
  'Carolingian Empire','Charlemagne Empire','Holy Roman Empire','East Francia','West Francia',
  'France','Kingdom of France','Aragon','Aragón','Castille','Castile','Navarre','León','Leon',
  'Portugal','Spain','Granada','Asturias','Galicia',
  'Italy','Venice','Genoa','Florence','Milan','Naples','Sicily','Papal States','Vatican',
  'Sardinia','Two Sicilies','Tuscany','Modena','Parma','Lucca','Mantua',
  'Hungary','Imperial Hungary','Bohemia','Moravia','Croatia','Serbia','Bosnia','Bulgaria',
  'Wallachia','Moldavia','Transylvania','Albania','Montenegro','Macedonia',
  'Poland','Poland-Lithuania','Lithuania','Teutonic Knights','Prussia','Kingdom of Prussia',
  'Livonia','Courland','Order of Livonia','Hanseatic League',
  'Kievan Rus','Kievan Rus\'','Kyivan Rus','Novgorod','Pskov','Ryazan','Vladimir-Suzdal',
  'Galicia-Volhynia','Grand Duchy of Moscow','Tsardom of Russia','Russian Empire','USSR','Soviet Union',
  'Denmark','Sweden','Norway','Denmark-Norway','Iceland','Kalmar Union','Finland',
  'Switzerland','Swiss Confederation','Belgium','Netherlands','Luxembourg',
  // 非洲
  'Aksum','Axum','Ethiopia','Damot','Zagwe','Solomonic Ethiopia','Adal','Hadiya','Bale',
  'Empire of Ghana','Mali','Songhai','Bornu-Kanem','Hausa States','Sokoto Caliphate',
  'Tukulor Empire','Toucouleur Empire','Wolof','Jolof','Cayor','Baol','Sine','Saloum',
  'Akan','Asante','Ashanti','Dahomey','Oyo','Benin','Mossi States','Dagbon','Mamprusi',
  'Nubia','Kush','Kingdom of Kush','Kerma','Kerma kingdom','Meroe','Meroë','Alodia','Alwa',
  'Makuria','Makkura','Nobatia','Funj','Sennar','Darfur',
  'Kongo','Congo','Loango','Ndongo','Matamba','Kasanje','Lunda','Luba','Bunyoro','Buganda',
  'Rwanda','Burundi','Karagwe','Bukoba','Mwenemutapa','Mutapa','Rozvi','Butua','Maravi',
  'Madagascar','Imerina','Merina','Expansionist Kingdom of Merina','Sakalava','Betsimisaraka','Boina','Antemoro',
  'Zulu Kingdom','Boer Republics','Orange Free State','Transvaal','Natal','Cape Colony',
  // 美洲
  'Olmec','Norte Chico','Caral','Chavin','Chavín','Moche','Nazca','Tiwanaku','Wari','Huari',
  'Inca Empire','Chimu','Chimú','Chachapoya','Lambayeque','Sicán','Cajamarca',
  'Maya states','Maya city-states','Maya chiefdoms and states','Maya civilization',
  'Teotihuacàn','Teotihuacán','Monte Albàn','Monte Albán','Toltec','Aztec Empire','Tarascan',
  'Mixtec Empire','Zapotec','Veracruz civilization','Huastec','Totonac',
  'Cahokia','Mississippian','Anasazi','Ancestral Puebloan','Hohokam','Mogollon',
  'Iroquois Confederacy','Powhatan Confederacy','Wabanaki Confederacy','Cherokee Nation',
  'Aztec Empire','Tarascan Empire','Purépecha',
  // 大洋洲
  "Tuʻi Tonga Empire","Tongan Empire","Tu'i Tonga Empire",'Hawaiian Kingdom','Tahitian Kingdom',
  // 殖民／現代簡稱
  'British Empire','French & Colonies','French Empire','Portuguese Empire','Spanish Empire',
  'Dutch East Indies','British India','British Raj','French Indo-China','German Empire',
  'Austria-Hungary','Habsburg Empire','Austrian Empire','Holy See','Jamaica (UK)','Germany (Soviet)',
  'East Germany','West Germany','Czechoslovakia','Yugoslavia','Manchuria','Tannu Tuva',
  'Mongolian People\'s Republic','Mongolia','Tibet','Xinjiang',
  // 早期文明（雖被歸 culture，但有酋邦／早期國家結構）
  'Indus valley civilization','Cucuteni-Trypillia civilization','Vinča civilization',
  'Harappa','Mohenjo-daro','Maya civilization',
  // 殖民／近世領地（rules 抓不到的）
  'Cayenne','Essequibo','Surinam','Ceylon','Malaya','Trinidad','Rapa Nui','Cherokee',
  'Cherokee Nation','Gambia, The','Swaziland','Zaire','Massachusetts Bay','New France',
  'Florida','Virginia','South Carolina','North Carolina','Georgia (US)','Maryland',
  'Pennsylvania','New York','Connecticut','New Hampshire','Rhode Island','Delaware','New Jersey',
  'Acadia','Acadian Peninsula (UK)','Newfoundland','Quebec','Hudson\'s Bay','Hudson Bay Company',
  'Oregon','Louisiana','Texas','Mexican Texas','California','Alaska',
  // 歐洲歷史小邦／地區
  'Lombardy','Sardinia-Piedmont','Franche-Comté','Massa','Fivizzano','Pontremoli','Modena','Parma',
  'Lucca','Urbino','Ferrara','Mantua','Genoa','Pisa','Siena','Ravenna','Spoleto','Aquileia',
  'Saxony','Bavaria','Hesse','Brandenburg','Mecklenburg','Pomerania','Württemberg','Baden',
  'Hanover','Westphalia','Hessen','Anhalt','Schleswig','Holstein','Trier','Cologne','Mainz',
  'Salzburg','Tyrol','Carinthia','Styria','Carniola',
  'Provence','Burgundy','Flanders','Hainault','Brabant','Holland','Zeeland','Friesland','Geldria',
  'Liège','Luxembourg','Liege','Limburg',
  'Catalonia','Valencia','Murcia','Asturias','Cantabria','Andalusia','Granada',
  'Wales','Cornwall','East Anglia','Mercia','Northumbria',
  // 非洲小國
  'Awsa','Wadai','Bagirmi','Borgu','Gobir','Katsina','Kano','Zaria','Nupe','Ilorin','Ibadan',
  'Bunyoro-Kitara','Karagwe','Bukoba','Kazembe','Lozi','Barotse','Yeke','Garenganze',
  // 東南亞小國／緬印
  'Ava','Toungoo','Chiang Mai','Lan Na','Vientiane','Luang Prabang','Champasak',
  'Cambodia','Cochin','Champa','Annam','Tonkin',
  'Hyderabad','Mysore','Travancore','Cochin (India)','Sikkim','Manipur','Assam','Tripura',
  'Cooch Behar','Junagadh','Bahawalpur','Kalat','Las Bela','Makran','Kharan',
  'Indore','Bhopal','Jaipur','Jodhpur','Udaipur','Bikaner','Jaisalmer','Mewar','Marwar',
  'Gwalior','Ahmadnagar','Bijapur','Golconda','Khandesh','Berar','Awadh','Oudh',
  // 中國分裂時期
  'Northern Yuan','Mongolia','Khalkha','Western Mongolia','Inner Mongolia',
  'Khorasan','Khorezm','Bukhara Emirate','Khiva Khanate','Kokand Khanate',
  'England and Ireland','Great Britain','United Kingdom','Kingdom of Great Britain',
  'Kingdom of Italy','Kingdom of Greece','Republic of Genoa','Republic of Venice',
  // 西班牙／葡萄牙殖民地時期 viceroyalties
  'New Spain','Vice Royalty of Peru','Vice-Royalty of New Spain','Viceroyalty of Peru',
  'Viceroyalty of New Spain','Viceroyalty of New Granada','Viceroyalty of Río de la Plata',
  'New Granada','Captaincy General of Venezuela','Captaincy General of Chile','Captaincy General of Cuba',
  'Captaincy General of Yucatan','Captaincy General of Guatemala','Captaincy General of the Philippines',
  'Brazil (Portugal)','Brazil','Kingdom of Brazil',
  'Delagoa Bay','Cape Colony','Cape of Good Hope','Mauritius','Réunion','Seychelles','Comoros',
  // 條頓 / 騎士團
  'Knights Hospitaller','Knights Templar','Order of Malta',
  // 美洲原住民「邦聯」（已達酋邦／國家）
  'Iroquois Confederacy','Powhatan Confederacy','Wabanaki Confederacy','Creek Confederacy',
  'Ojibwa Council','Wampanoag Confederacy','Three Fires Confederacy',
  // Polynesian chiefdom
  'Society Islands','Tahiti','Samoan Islands','Hawaii','Hawaiian Islands','Cook Islands',
  'Tonga (Kingdom)','Wallis and Futuna','Fiji (Kingdom)',
  // 1900 加入：奧匈別寫法、非洲小國、殖民地
  'Austria Hungary','Sweden–Norway','Sweden-Norway','Bosnia-Herzegovina','Arabia',
  'Basutoland','Bechuanaland','Nyasaland','Rhodesia','Northern Rhodesia','Southern Rhodesia',
  'Tanganyika','Uganda Protectorate','Kenya Colony','Anglo-Egyptian Sudan',
  'Calabar','Cotonou','Lagos','Accra','Algiers','Tunis','Tripoli','Tripolitania','Cyrenaica',
  'Futa Jalon','Futa Jallon','Futa Toro','Kanem-Bornu','Kanem','Bornu','Kong','Opobo',
  'Mbailundu','Yaka','Zululand','Griqualand West','Griqualand East','Transkei','Bechuanaland Protectorate',
  'Harer (Egypt)','Harar','Harar Sultanate','Sennar','Sinnar','Oromo Kingdoms','Kaffa','Janjero',
  'Guadeloupe','Martinique','Netherlands Antilles','Curaçao','Aruba','French Guiana',
  'Anguilla','Antigua and Barbuda','Bahamas','Barbados','Dominica','Grenada','Montserrat',
  'Saint Kitts and Nevis','Saint Lucia','Saint Vincent and the Grenadines','Trinidad and Tobago',
  'Turks and Caicos Islands','United States Virgin Islands','Saint Martin','Saint Barthelemy',
  // 1500 加入：原住民邦聯、印度蘇丹小邦、拼寫變體
  'Iroquois','Iroquoia','Mi\'kma\'ki','Wabanaki',
  'Bidar','Golconda','Golkonda','Bijapur','Berar','Khandesh','Vijayanagar',
  'Muscat','Cherookee','Cherokee','Novgorod-Seversky','Burmese kingdoms','Hindu kingdoms',
  'Sinhalese kingdoms','Maya states','Greek city-states','Greek colonies','Zhou states',
  'Maya chiefdoms and states','Polynesian chiefdoms','Hawaiian chiefdoms',
])

// ---- Rule layer 4: 已知非政權 override（black）— 補 blacklist 漏的 ----
const KNOWN_NON_STATES = new Set([
  // 純語族／民族集合
  'Polynesians','Bantu','Dravidians','Semites','Berbers','Khoisan','Khoiasan','Vedic Aryans',
  'Aryans','Indo-Europeans','Austroasiatics','Austronesians','Sino-Tibetans',
  'Celts','Germans (Germanic)','Slavs','Balts','Finno-Ugrians','Tibeto-Burmanese',
  'Bantu','Nilotic','Cushitic','Iroquoians','Algonquians',
  'Burmese','Koreans','Thai','Tibetans','Mongols','Manchus','Han Chinese','Japanese',
  'Paleo-Inuit','Paleo-Koreans',
  // 古考古「文化」（band/tribe 階段，非酋邦）
  'Cycladic','Beaker','Funnel-Beaker','Únětice','Unetice','Andronovo','Sintashta',
  'Afanasevo','Kelteminar','Namazga','Naquada I','Naquada II','Ubaid','Halaf','Hassuna','Samarra',
  'Yarmukian','Ghassul','Dimini','Sesklo','Vinča','Karanovo','Tisza','Lengyel','Tripolye',
  'Yangshao','Longshan','Hongshan','Liangzhu','Majiayao','Dawenkou','Hemudu','Peiligang',
  'Dapenkeng culture','Dakapeng culture','Jōmon','Yayoi',
  'Catal Huyuk','Çatalhöyük','Jericho (Neolithic)',
  'Lapita','Toalean','Hoabinhian','Bacsonian','Sa Huỳnh','Đông Sơn',
  'Comb Ceramic','Pit-Comb','Early combware','Linear Pottery',
  'Wankarani','Paracas','Chavin de Huantar (pre-state)','Chinchoros','Valdivia',
  'Cotton Preceramic',
  // 部落／民族（非政權）
  'Saami','Sámi','Sami','Ainu','Maori','Māori','M?ori','Inuit','Yupik','Aleuts',
  'Wiradjuri','Yolngu','Wurundjeri','Kaurna','Larrakia','Noongar','Bundjalung',
  'Iroquoians','Algonquians','Athabaskan','Athabascan','Tlingit','Haida','Tsimshian',
  'Pueblo','Hopi','Zuni','Apache','Navajo','Comanche','Kiowa','Sioux','Cheyenne','Arapaho',
  'Crow','Blackfoot','Ojibwe','Cree','Mi\'kmaq','Innu',
  'Tupis','Tupinamba','Guarani','Mapuche','Tehuelche','Selk\'nam','Yamana',
  'Pygmies','San','Hottentots','Bushmen','Zaghawa',
  'Guanches','Berbers','Tuareg',
  // Polynesians 等已含 -人 結尾
])

// 中文翻譯後綴 — 高信心信號
const ZH_POLITY_RE = /(王國|帝國|汗國|王朝|公國|親王國|哈里發|蘇丹國|酋長國|大公國|聯邦|聯盟|城邦|沙皇國|專制國|貝伊國|帕夏轄區|主教區|諸侯|共和國|自由邦|自由市|託管地|殖民地|保護國|占領區|蘇維埃|帝國自由市|親王主教區|大主教區|文明|王冠|總督|總督轄區|州$)/
const ZH_POLITY_PREFIX_RE = /^(葡屬|英屬|法屬|荷屬|西屬|德屬|義屬|俄屬|奧屬|比屬|日屬|蘇屬|新法蘭西)/
const ZH_NONSTATE_RE = /(人|族|文化|語族|語系)$/      // 結尾 -人/-族/文化/語族

// 殖民地／占領區後綴格式：X (UK), X (FR), X (Portugal), X (Soviet), X (USA) etc.
const COLONY_FORMAT_RE = /\((UK|GB|FR|France|US|USA|Portugal|Spain|Spanish|Belgium|Netherlands|Dutch|Italy|Italian|German|Germany|Soviet|Russian|Japanese|Japan)\)\s*$/i

// ---- Rule application ----
function classify(name) {
  // Layer 1: explicit overrides
  if (KNOWN_NON_STATES.has(name)) return { is_state: false, reason: 'known-non-state' }
  if (KNOWN_STATES.has(name)) return { is_state: true,  reason: 'known-state' }
  if (STATE_DETAILS_KEYS.has(name)) return { is_state: true, reason: 'state-details-key' }

  // Layer 2: name patterns (high confidence)
  for (const re of NON_STATE_PATTERNS) if (re.test(name)) return { is_state: false, reason: `non-state-pattern: ${re}` }
  for (const re of POLITY_PATTERNS) if (re.test(name)) return { is_state: true, reason: `polity-pattern: ${re}` }

  // Layer 3: 殖民地格式 X (UK) etc. → 政權
  if (COLONY_FORMAT_RE.test(name)) return { is_state: true, reason: 'colony-format' }

  // Layer 4: 出現在現代 NE admin_0 (現代國家名) → 政權
  if (adm0NameSet.has(name)) return { is_state: true, reason: 'modern-country' }

  // Layer 5: 看 Gemini 的中文翻譯後綴
  const zh = polyZh[name]
  if (zh) {
    if (ZH_POLITY_RE.test(zh)) return { is_state: true, reason: `zh-polity-suffix (${zh})` }
    if (ZH_POLITY_PREFIX_RE.test(zh)) return { is_state: true, reason: `zh-polity-prefix (${zh})` }
    if (ZH_NONSTATE_RE.test(zh)) return { is_state: false, reason: `zh-nonstate-suffix (${zh})` }
  }

  // 預設：保守 = false（不算）
  return { is_state: false, reason: 'unmatched-default-false' }
}

const result = {}
let nState = 0, nNonState = 0, nDefaultFalse = 0
for (const n of [...allNames].sort()) {
  const c = classify(n)
  result[n] = c
  if (c.is_state) nState++
  else { nNonState++; if (c.reason === 'unmatched-default-false') nDefaultFalse++ }
}

writeFileSync(OUT_FILE, JSON.stringify(result, null, 2))
console.log(`Wrote ${OUT_FILE} (${Object.keys(result).length} entries)`)
console.log(`  is_state = true:  ${nState}`)
console.log(`  is_state = false: ${nNonState}  (of which unmatched-default: ${nDefaultFalse})`)
console.log(`\n=== "unmatched-default-false" sample (first 80) ===`)
const def = Object.entries(result).filter(([_, v]) => v.reason === 'unmatched-default-false')
def.slice(0, 80).forEach(([n]) => console.log(` ${n.padEnd(40)} → ${polyZh[n] || ''}`))
