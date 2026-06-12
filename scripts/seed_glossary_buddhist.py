"""Seed Buddhist terms for /translation-glossary (「神祇與宗教名詞」tab) — HAND-CURATED.

填補 deities 表的佛教空白（既有 101 筆 0 佛教）。繁中 name_recommended 採漢傳佛教
標準譯名（《佛光大辭典》所載權威傳統譯法為據）；佛光特有 or 異體放 name_variants。
聚焦東方聖書佛教卷（法句經/經集/律藏/妙法蓮華/彌蘭陀王問經/大乘）會出現的高頻
名號、弟子、教義、經典、教派 — 供翻譯 prompt 鎖術語用。

name_english = 學界/SBE 英文常見轉寫（翻譯時的 lookup key）；梵巴二式並收。
name_original = 梵文羅馬轉寫（lang=sa）；巴利異式與異體中譯放 name_variants。
entity_type：佛號／佛／菩薩／弟子／天部／概念／經典／教派／宇宙。

Usage: python scripts/seed_glossary_buddhist.py [--dry]
"""
from __future__ import annotations
import os, sys, io, argparse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import requests
from dotenv import load_dotenv
load_dotenv(".env")
URL = os.environ["SUPABASE_URL"]; SVC = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": SVC, "Authorization": f"Bearer {SVC}"}
H_UPSERT = {**H, "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates,return=minimal"}
ROWS: list[dict] = []
_order = 0
R = "佛教"


def B(en, rec, *, o="", var="", reason="", root="", etype="概念", domain=""):
    global _order
    _order += 10
    ROWS.append({"name_english": en, "name_original": o or None,
        "name_original_lang": "sa" if o else None, "name_recommended": rec,
        "name_variants": var or None, "recommendation_reason": reason or None,
        "name_root": root or None, "religion": R,
        "entity_type": etype or None, "domain_of": domain or None,
        "sort_order": _order})


# ── 佛號與十號（佛陀的名號與尊稱）──────────────────────────────────────────────
_order = 6000
B("Buddha", "佛陀", o="buddha", var="佛；浮屠(古)；覺者", etype="佛號",
  reason="意為「覺者」；漢傳通稱佛、佛陀", root="佛")
B("Tathagata", "如來", o="tathāgata", var="多陀阿伽陀(音譯)", etype="佛號",
  reason="十號之一，乘真如而來；漢傳定譯如來")
B("Bhagavat", "世尊", o="bhagavat", var="薄伽梵(音譯)", etype="佛號",
  reason="十號之一，世所尊重；音譯薄伽梵")
B("Sugata", "善逝", o="sugata", etype="佛號", reason="十號之一，善巧入滅")
B("Arhat (Buddha epithet)", "應供", o="arhat", var="阿羅漢", etype="佛號",
  reason="十號之一，應受供養", root="羅漢")
B("Sakyamuni", "釋迦牟尼", o="śākyamuni", var="釋尊；釋迦牟尼佛", etype="佛",
  reason="釋迦族之聖者，歷史佛陀", root="釋迦")
B("Gautama", "喬達摩", o="gautama", var="瞿曇(古譯)", etype="佛",
  reason="佛陀俗姓；古譯瞿曇", root="喬達摩")
B("Siddhartha", "悉達多", o="siddhārtha", var="悉達", etype="佛",
  reason="佛陀本名，意為「成就一切義」")
B("Amitabha", "阿彌陀佛", o="amitābha", var="無量光佛；彌陀；阿彌陀婆", etype="佛",
  reason="西方極樂淨土教主；意譯無量光", root="彌陀")
B("Amitayus", "無量壽佛", o="amitāyus", var="阿彌陀佛", etype="佛",
  reason="阿彌陀佛之意譯（無量壽）", root="彌陀")
B("Vairocana", "毗盧遮那佛", o="vairocana", var="大日如來；盧舍那", etype="佛",
  reason="法身佛；密教大日如來")
B("Bhaisajyaguru", "藥師佛", o="bhaiṣajyaguru", var="藥師琉璃光如來", etype="佛",
  reason="東方淨琉璃世界教主")
B("Dipankara", "燃燈佛", o="dīpaṃkara", var="定光佛", etype="佛",
  reason="過去佛，授記釋迦成佛")

# ── 菩薩 ──────────────────────────────────────────────────────────────────────
_order = 6300
B("Bodhisattva", "菩薩", o="bodhisattva", var="菩提薩埵(全音譯)；覺有情", etype="概念",
  reason="求覺悟、度眾生者；漢傳通稱菩薩", root="菩薩")
B("Avalokitesvara", "觀世音菩薩", o="avalokiteśvara", var="觀自在菩薩(玄奘)；觀音", etype="菩薩",
  reason="鳩摩羅什譯觀世音、玄奘譯觀自在，漢傳通稱觀音", root="觀音")
B("Manjusri", "文殊菩薩", o="mañjuśrī", var="文殊師利；妙吉祥", etype="菩薩",
  reason="智慧第一菩薩", root="文殊")
B("Samantabhadra", "普賢菩薩", o="samantabhadra", etype="菩薩",
  reason="行願第一菩薩")
B("Ksitigarbha", "地藏菩薩", o="kṣitigarbha", var="地藏王", etype="菩薩",
  reason="地獄不空誓不成佛")
B("Maitreya", "彌勒菩薩", o="maitreya", var="彌帝隸；慈氏", etype="菩薩",
  reason="未來佛，當來下生；意譯慈氏", root="彌勒")
B("Mahasthamaprapta", "大勢至菩薩", o="mahāsthāmaprāpta", var="勢至", etype="菩薩",
  reason="西方三聖之一")

# ── 弟子與聖眾（律藏/經藏常見人物）────────────────────────────────────────────
_order = 6600
B("Ananda", "阿難", o="ānanda", var="阿難陀", etype="弟子",
  reason="多聞第一，佛之侍者", root="阿難")
B("Mahakasyapa", "大迦葉", o="mahākāśyapa", var="摩訶迦葉；迦葉", etype="弟子",
  reason="頭陀第一，付法第一祖", root="迦葉")
B("Sariputra", "舍利弗", o="śāriputra", var="舍利子(玄奘)；鶖鷺子", etype="弟子",
  reason="智慧第一；玄奘譯舍利子", root="舍利")
B("Maudgalyayana", "目犍連", o="maudgalyāyana", var="大目犍連；目連", etype="弟子",
  reason="神通第一")
B("Subhuti", "須菩提", o="subhūti", var="善現；空生", etype="弟子",
  reason="解空第一；《金剛經》當機者")
B("Purna", "富樓那", o="pūrṇa", var="富樓那彌多羅尼子", etype="弟子",
  reason="說法第一")
B("Upali", "優波離", o="upāli", var="優婆離", etype="弟子",
  reason="持律第一；結集律藏")
B("Rahula", "羅睺羅", o="rāhula", var="羅云", etype="弟子",
  reason="密行第一；佛之子")
B("Aniruddha", "阿那律", o="aniruddha", var="阿㝹樓馱", etype="弟子",
  reason="天眼第一")
B("Katyayana", "迦旃延", o="kātyāyana", var="摩訶迦旃延", etype="弟子",
  reason="論議第一")
B("Devadatta", "提婆達多", o="devadatta", var="調達", etype="弟子",
  reason="佛之堂弟，破和合僧")
B("Mahaprajapati", "摩訶波闍波提", o="mahāprajāpatī", var="大愛道", etype="弟子",
  reason="佛之姨母，首位比丘尼")

# ── 三寶與僧團 ────────────────────────────────────────────────────────────────
_order = 6900
B("Dharma", "法", o="dharma", var="達磨；達摩；曇(音譯)", etype="概念",
  reason="佛陀教法／真理／一切存在；漢傳意譯法", root="法")
B("Sangha", "僧伽", o="saṃgha", var="僧；和合眾", etype="概念",
  reason="出家修行團體；略稱僧", root="僧")
B("Triratna", "三寶", o="triratna", var="佛法僧三寶", etype="概念",
  reason="佛、法、僧三者")
B("Bhikkhu", "比丘", o="bhikṣu", var="苾芻；乞士；(巴)bhikkhu", etype="概念",
  reason="受具足戒之男眾", root="比丘")
B("Bhikkhuni", "比丘尼", o="bhikṣuṇī", var="苾芻尼；(巴)bhikkhunī", etype="概念",
  reason="受具足戒之女眾", root="比丘")
B("Upasaka", "優婆塞", o="upāsaka", var="近事男；清信士", etype="概念",
  reason="在家男眾居士")
B("Upasika", "優婆夷", o="upāsikā", var="近事女；清信女", etype="概念",
  reason="在家女眾居士")
B("Arhat", "阿羅漢", o="arhat", var="羅漢；阿羅訶；(巴)arahant；應供", etype="概念",
  reason="斷盡煩惱、不再受生之聖者；聲聞極果", root="羅漢")
B("Pratyekabuddha", "辟支佛", o="pratyekabuddha", var="緣覺；獨覺；(巴)paccekabuddha",
  etype="概念", reason="無師自悟者；意譯緣覺")
B("Sravaka", "聲聞", o="śrāvaka", var="(巴)sāvaka", etype="概念",
  reason="聞佛聲教而悟道者")

# ── 核心教義概念 ──────────────────────────────────────────────────────────────
_order = 7200
B("Nirvana", "涅槃", o="nirvāṇa", var="泥洹(古)；(巴)nibbāna 涅盤；圓寂；滅度", etype="概念",
  reason="煩惱寂滅之境；漢傳定譯涅槃", root="涅槃")
B("Samsara", "輪迴", o="saṃsāra", var="生死輪迴；流轉", etype="概念",
  reason="生死流轉不已")
B("Karma", "業", o="karman", var="(巴)kamma；羯磨(音,特指儀軌)；業力", etype="概念",
  reason="身口意造作及其果報；漢傳意譯業", root="業")
B("Pratityasamutpada", "緣起", o="pratītyasamutpāda", var="因緣生起；十二因緣；(巴)paṭiccasamuppāda",
  etype="概念", reason="此有故彼有的依存生起法則", root="緣")
B("Four Noble Truths", "四聖諦", o="catvāri āryasatyāni", var="四諦；苦集滅道", etype="概念",
  reason="苦、集、滅、道四真理")
B("Noble Eightfold Path", "八正道", o="āryāṣṭāṅgamārga", var="八聖道；(巴)aṭṭhaṅgika-magga",
  etype="概念", reason="正見乃至正定八支聖道", root="道")
B("Dukkha", "苦", o="duḥkha", var="(巴)dukkha；苦諦", etype="概念",
  reason="逼迫不安之性；四諦之苦", root="苦")
B("Skandha", "蘊", o="skandha", var="五蘊；陰(古譯)；(巴)khandha 五蘊", etype="概念",
  reason="色受想行識五蘊；古譯五陰", root="蘊")
B("Anatman", "無我", o="anātman", var="非我；(巴)anattā", etype="概念",
  reason="諸法無自性、無常一主宰之我", root="我")
B("Anitya", "無常", o="anitya", var="(巴)anicca", etype="概念",
  reason="諸行剎那生滅、不恆常")
B("Sunyata", "空", o="śūnyatā", var="空性", etype="概念",
  reason="諸法無自性；般若核心", root="空")
B("Bodhi", "菩提", o="bodhi", var="覺；道(古譯)", etype="概念",
  reason="覺悟、正覺；音譯菩提", root="菩提")
B("Prajna", "般若", o="prajñā", var="智慧；(巴)paññā", etype="概念",
  reason="證空之智；音譯般若", root="般若")
B("Madhyama", "中道", o="madhyamā pratipad", var="中觀", etype="概念",
  reason="離斷常二邊之中正之道", root="道")
B("Tathata", "真如", o="tathatā", var="如；如如", etype="概念",
  reason="諸法真實不變之本性")
B("Dharmakaya", "法身", o="dharmakāya", etype="概念",
  reason="佛三身之一，真理本體", root="法")
B("Sambhogakaya", "報身", o="saṃbhogakāya", var="受用身", etype="概念",
  reason="佛三身之一，福慧果報之身")
B("Nirmanakaya", "應身", o="nirmāṇakāya", var="化身；應化身", etype="概念",
  reason="佛三身之一，應機示現之身")
B("Tathagatagarbha", "如來藏", o="tathāgatagarbha", etype="概念",
  reason="眾生本具之佛性")
B("Alayavijnana", "阿賴耶識", o="ālayavijñāna", var="藏識；第八識", etype="概念",
  reason="唯識所立根本識")
B("Klesa", "煩惱", o="kleśa", var="惑；(巴)kilesa", etype="概念",
  reason="擾亂身心之染污")
B("Three Poisons", "三毒", o="triviṣa", var="貪瞋癡", etype="概念",
  reason="貪、瞋、癡三根本煩惱")
B("Sila", "戒", o="śīla", var="(巴)sīla；尸羅(音)", etype="概念",
  reason="三學之一，防非止惡", root="戒")
B("Samadhi", "定", o="samādhi", var="三昧(音譯)；三摩地", etype="概念",
  reason="三學之一，心一境性；音譯三昧", root="定")
B("Dhyana", "禪那", o="dhyāna", var="禪；(巴)jhāna 禪那；靜慮", etype="概念",
  reason="寂靜審慮之定境；音譯禪", root="禪")
B("Paramita", "波羅蜜", o="pāramitā", var="波羅蜜多；六度；到彼岸", etype="概念",
  reason="到彼岸之菩薩行；六波羅蜜", root="波羅蜜")
B("Metta", "慈", o="maitrī", var="(巴)mettā；慈心", etype="概念",
  reason="與樂之心；四無量心之一")
B("Karuna", "悲", o="karuṇā", var="悲心", etype="概念",
  reason="拔苦之心；四無量心之一")
B("Bodhicitta", "菩提心", o="bodhicitta", etype="概念",
  reason="上求佛道、下化眾生之心", root="菩提")
B("Mara", "魔", o="māra", var="魔羅(音)；波旬", etype="天部",
  reason="障道之惡魔；音譯魔羅")
B("Kalpa", "劫", o="kalpa", var="劫波(音)；(巴)kappa", etype="概念",
  reason="極長時間單位；音譯劫")
B("Merit (punya)", "功德", o="puṇya", var="福德；(巴)puñña", etype="概念",
  reason="善行所感之福報")
B("Mantra", "真言", o="mantra", var="咒；曼怛羅(音)", etype="概念",
  reason="密教持誦之神聖語句")
B("Mudra", "手印", o="mudrā", var="印契；母陀羅(音)", etype="概念",
  reason="象徵性手勢")
B("Stupa", "塔", o="stūpa", var="窣堵波(音)；浮屠；塔婆", etype="概念",
  reason="安奉舍利之建築；音譯窣堵波")
B("Dharani", "陀羅尼", o="dhāraṇī", var="總持", etype="概念",
  reason="長咒；意譯總持")

# ── 天部與六道眾生（與既有 deities 印度教神系區隔，標佛教脈絡）──────────────────
_order = 7700
B("Deva", "天", o="deva", var="提婆(音)；天人", etype="天部",
  reason="六道之天界眾生；音譯提婆", root="提婆")
B("Asura", "阿修羅", o="asura", var="修羅；非天", etype="天部",
  reason="六道之一，好鬥之神")
B("Preta", "餓鬼", o="preta", var="薜荔多(音)", etype="天部",
  reason="六道之一，飢渴之鬼")
B("Naga", "龍", o="nāga", var="那伽(音)", etype="天部",
  reason="護法龍眾；音譯那伽")
B("Yaksa", "夜叉", o="yakṣa", var="藥叉", etype="天部",
  reason="護法鬼神之一")
B("Gandharva", "乾闥婆", o="gandharva", var="香神；尋香", etype="天部",
  reason="天龍八部之樂神")
B("Kinnara", "緊那羅", o="kiṃnara", var="歌神；疑神", etype="天部",
  reason="天龍八部之歌神")
B("Garuda", "迦樓羅", o="garuḍa", var="金翅鳥", etype="天部",
  reason="天龍八部之金翅鳥")
B("Brahma (Buddhist)", "梵天", o="brahmā", var="大梵天", etype="天部",
  reason="色界初禪天主；佛教護法")
B("Sakra / Indra (Buddhist)", "帝釋天", o="śakra", var="釋提桓因；因陀羅(印度教為因陀羅)", etype="天部",
  reason="忉利天主；即印度教因陀羅，佛教護法", root="帝釋")
B("Four Heavenly Kings", "四天王", o="caturmahārāja", var="四大天王", etype="天部",
  reason="守護四方之護法天王")
B("Sumeru", "須彌山", o="sumeru", var="妙高山；蘇迷盧(音)", etype="宇宙",
  reason="佛教宇宙觀之世界中心")
B("Trichiliocosm", "三千大千世界", o="trisāhasra-mahāsāhasra-lokadhātu", var="大千世界",
  etype="宇宙", reason="佛教宇宙的廣大世界系統")
B("Six Realms", "六道", o="ṣaḍgati", var="六趣；天人阿修羅畜生餓鬼地獄", etype="宇宙",
  reason="輪迴流轉之六種界趣")
B("Pure Land", "淨土", o="sukhāvatī", var="極樂世界；安樂國", etype="宇宙",
  reason="阿彌陀佛之西方極樂世界")

# ── 經典與三藏（SBE 佛教卷相關）──────────────────────────────────────────────
_order = 8200
B("Tripitaka", "三藏", o="tripiṭaka", var="(巴)tipiṭaka；大藏經", etype="經典",
  reason="經、律、論三藏聖典")
B("Sutra", "經", o="sūtra", var="(巴)sutta 經；修多羅(音)", etype="經典",
  reason="佛所說法之經典；音譯修多羅", root="經")
B("Vinaya", "律", o="vinaya", var="律藏；毗奈耶(音)", etype="經典",
  reason="僧團戒律典籍")
B("Abhidharma", "論", o="abhidharma", var="阿毗達磨(音)；對法；論藏；(巴)abhidhamma",
  etype="經典", reason="論議分別法相之典籍")
B("Agama", "阿含經", o="āgama", var="阿含；阿笈摩", etype="經典",
  reason="早期結集之根本經典")
B("Dhammapada", "法句經", o="dharmapada", var="(巴)dhammapada；曇缽偈", etype="經典",
  reason="偈頌體法要；SBE 第10卷", root="法")
B("Sutta-Nipata", "經集", o="sūtranipāta", var="(巴)suttanipāta", etype="經典",
  reason="巴利經藏小部之古層經集；SBE 第10卷")
B("Jataka", "本生經", o="jātaka", var="闍多伽(音)；本生譚", etype="經典",
  reason="佛陀前生故事")
B("Saddharmapundarika", "妙法蓮華經", o="saddharmapuṇḍarīka", var="法華經", etype="經典",
  reason="大乘要典；SBE 第21卷", root="法")
B("Prajnaparamita Sutra", "般若經", o="prajñāpāramitā-sūtra", var="般若波羅蜜多經", etype="經典",
  reason="闡空之大乘經系", root="般若")
B("Avatamsaka Sutra", "華嚴經", o="avataṃsaka-sūtra", var="大方廣佛華嚴經", etype="經典",
  reason="華嚴宗根本經")
B("Lankavatara Sutra", "楞伽經", o="laṅkāvatāra-sūtra", etype="經典",
  reason="如來藏與唯識要典")
B("Milindapanha", "彌蘭陀王問經", o="milindapañha", var="那先比丘經；彌蘭王問經", etype="經典",
  reason="希臘王彌蘭陀與那先論道；SBE 第35-36卷")

# ── 教派／部派 ────────────────────────────────────────────────────────────────
_order = 8700
B("Theravada", "上座部", o="sthaviravāda", var="(巴)theravāda；南傳佛教", etype="教派",
  reason="現存南傳部派；長老之教")
B("Mahayana", "大乘", o="mahāyāna", var="大乘佛教", etype="教派",
  reason="自利利他之菩薩乘")
B("Hinayana", "小乘", o="hīnayāna", var="聲聞乘", etype="教派",
  reason="相對大乘之稱（含貶義，學界多改稱部派／聲聞乘）")
B("Madhyamaka", "中觀派", o="madhyamaka", var="中觀學派", etype="教派",
  reason="龍樹所創，明空義", root="中觀")
B("Yogacara", "瑜伽行派", o="yogācāra", var="唯識宗；法相宗", etype="教派",
  reason="無著世親所傳，明唯識")
B("Chan / Zen", "禪宗", o="dhyāna", var="禪", etype="教派",
  reason="以心傳心之宗派；日傳作 Zen", root="禪")
B("Pure Land school", "淨土宗", o="sukhāvatī", var="蓮宗", etype="教派",
  reason="專修念佛求生淨土")
B("Tiantai", "天台宗", var="法華宗", etype="教派",
  reason="智顗所創，依法華經")
B("Huayan", "華嚴宗", var="賢首宗", etype="教派",
  reason="依華嚴經，明法界緣起")
B("Vajrayana", "金剛乘", o="vajrayāna", var="密宗；密教；真言乘", etype="教派",
  reason="以真言密法修持之乘")
B("Nagarjuna", "龍樹", o="nāgārjuna", var="龍猛", etype="弟子",
  reason="中觀派祖師，大乘八宗共祖", root="龍樹")
B("Asanga", "無著", o="asaṅga", etype="弟子",
  reason="瑜伽行派創立者")
B("Vasubandhu", "世親", o="vasubandhu", var="天親", etype="弟子",
  reason="無著之弟，唯識集大成者")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()
    # duplicate-key guard
    seen = {}
    for r in ROWS:
        k = r["name_english"]
        if k in seen:
            print(f"  ⚠ DUP name_english: {k}")
        seen[k] = r
    print(f"{len(ROWS)} Buddhist rows ({len(seen)} unique name_english)")
    if args.dry:
        for r in ROWS:
            print(f"  [{r['entity_type']:4s}] {r['name_recommended']:12s} ← {r['name_english']:30s} {r['name_variants'] or ''}")
        return
    for i in range(0, len(ROWS), 50):
        resp = requests.post(f"{URL}/rest/v1/deities?on_conflict=name_english",
                             headers=H_UPSERT, json=ROWS[i:i + 50], timeout=60)
        resp.raise_for_status()
        print(f"  upserted {i}..{i + len(ROWS[i:i+50])}")
    print("done")


if __name__ == "__main__":
    main()
