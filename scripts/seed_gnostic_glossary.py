"""Seed authoritative Chinese Gnostic terminology into the glossary `deities`
table (religion='諾斯底'). Renderings follow 張新樟譯漢斯‧約納斯《諾斯替宗教》+
中文維基百科 諾斯底主義 + 黃根春《基督教典外文獻》. name_recommended = ★主譯,
name_variants = ；-separated 其他通行譯法. These feed the /gnostic translation
prompt so future translations stay term-consistent."""
import os, json
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.getcwd(), ".env"))
URL = os.environ["SUPABASE_URL"]
SK = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": SK, "Authorization": f"Bearer {SK}", "Content-Type": "application/json",
     "Prefer": "resolution=merge-duplicates,return=minimal"}

# (en, original_grc, romanized, ★recommended, variants, entity_type, domain_of, reason)
TERMS = [
    # ── 核心概念 ──
    ("Gnosticism", "γνωστικισμός", "gnostikismos", "諾斯底主義", "諾斯替主義；諾斯蒂主義", "concept", "", "源自希臘文 gnōsis「知識」；學界另作諾斯替主義"),
    ("Gnosis", "γνῶσις", "gnosis", "靈知", "諾斯；知識；靈智", "concept", "超越性的得救知識", "希臘文「知識」；學界譯靈知，強調超凡得救之知"),
    ("Pleroma", "πλήρωμα", "pleroma", "普累若麻", "佩雷若瑪；豐盈；圓滿；完滿", "concept", "神性完滿之境", "張新樟《諾斯替宗教》標準音譯；意為神性的完滿"),
    ("Aeon", "αἰών", "aion", "移涌", "艾翁；伊涌；永世；世代", "deity", "由太一流溢的神性存在", "張新樟學界標準「移涌」；自太一流溢之神性實體"),
    ("Emanation", "ἀπόρροια", "aporrhoia", "流溢", "流出", "concept", "", "神性層層流出"),
    ("Demiurge", "δημιουργός", "demiourgos", "巨匠造物主", "德謬革；德謬哥；造匠；工匠造物者", "deity", "物質世界的低等造物者", "中文維基標準；柏拉圖借詞，諾斯底指低等造物神"),
    ("Archon", "ἄρχων", "archon", "執政者", "執政；阿爾孔；阿爾康", "deity", "星界統治者、巨匠之僕役", "巨匠造物主的僕役，掌管物質界與星辰"),
    ("Monad", "μονάς", "monas", "太一", "一元；單子", "concept", "至高本源、光之領域", "至高獨一者，普累若麻之源"),
    ("Bythos", "βυθός", "bythos", "深淵", "彼托斯；本源", "deity", "至高無名之父", "瓦倫廷派中至高無名的本源"),
    ("Sige", "σιγή", "sige", "沉默", "西格", "deity", "深淵的配偶", "Bythos 的陰性配偶"),
    ("Nous", "νοῦς", "nous", "努斯", "心智；理智", "concept", "神聖心智", "希臘哲學「心智」，諾斯底為流溢之一"),
    ("Logos", "λόγος", "logos", "邏各斯", "道；言", "concept", "", "神聖之道／言"),
    ("Syzygy", "συζυγία", "syzygia", "配偶", "同軛；相偶；配對", "concept", "移涌的陰陽配對", "移涌成對流溢（陰陽配偶）"),
    ("Horos", "ὅρος", "horos", "界限", "界標；限界", "deity", "普累若麻的界限（Limit）", "分隔普累若麻與外界的界限"),
    ("Hebdomad", "ἑβδομάς", "hebdomas", "七重天", "", "concept", "七執政之領域", "七行星執政的星界"),
    ("Ogdoad", "ὀγδοάς", "ogdoas", "八重天", "", "concept", "", "第八重天，超乎七執政之上"),
    ("Kenoma", "κένωμα", "kenoma", "虛空", "", "concept", "普累若麻之外的匱乏", "與普累若麻（圓滿）相對的虛空"),
    # ── 神祇／神話人物 ──
    ("Sophia", "Σοφία", "sophia", "索菲亞", "蘇菲亞；智慧", "deity", "智慧；墮落的移涌", "希臘文「智慧」；其墮落引發物質世界生成"),
    ("Achamoth", "Ἀχαμώθ", "achamoth", "阿卡摩特", "", "deity", "下層智慧", "瓦倫廷派中墮落的下層索菲亞"),
    ("Yaldabaoth", "Ιαλδαβαώθ", "Ialdabaoth", "雅達巴沃", "亞大伯斯；雅爾達巴沃；伊勒達巴俄特", "deity", "= 巨匠造物主", "獅面蛇身的低等造物神，即巨匠造物主"),
    ("Samael", "Σαμαήλ", "samael", "薩邁爾", "薩麥爾", "deity", "「盲目之神」", "亞蘭文「盲目的神」，巨匠別名"),
    ("Saklas", "Σακλάς", "saklas", "薩克拉斯", "薩迦拉", "deity", "「愚者」", "敘利亞文「愚蠢」，巨匠別名"),
    ("Barbelo", "Βαρβηλώ", "barbelo", "巴貝洛", "巴爾貝洛", "deity", "至高之母、初思", "塞特派中由太一流溢的至高陰性神格"),
    ("Abraxas", "Ἀβραξάς", "abraxas", "阿布拉克薩斯", "阿伯拉薩斯；阿布拉薩斯", "deity", "", "巴西里德派中統攝諸天的至高存在（名數值 365）"),
    ("Autogenes", "αὐτογενής", "autogenes", "自生者", "奧托革涅斯", "deity", "自生的神聖之子", "「自生者」，由巴貝洛流溢"),
    ("Adamas", "Ἀδάμας", "adamas", "亞達瑪", "天上的亞當", "deity", "完美的天上原人", "塞特派中天上完美的原型亞當"),
    ("Norea", "Ὡραία", "norea", "諾蕾亞", "", "deity", "塞特之妹／妻", "塞特派傳統中的女性救贖人物"),
    ("Seth", "Σήθ", "seth", "塞特", "舍特", "deity", "屬靈族類之祖", "亞當之子，塞特派視為屬靈後裔之祖"),
    ("Protennoia", "πρωτέννοια", "protennoia", "初思", "普羅頓諾亞", "deity", "最初的思想", "「最初之思」，至高神的首發意念"),
    ("Pronoia", "πρόνοια", "pronoia", "先見", "普羅諾亞；天意", "deity", "神的先見", "神的先見／護佑"),
    # ── 教派 ──
    ("Sethian", "", "Sethian", "塞特派", "賽特派", "term", "諾斯底教派", "以塞特為屬靈始祖的諾斯底支派"),
    ("Valentinian", "", "Valentinian", "瓦倫廷派", "華倫提努派；范倫提努派", "term", "諾斯底教派", "瓦倫廷創立，最具系統的諾斯底學派"),
    ("Ophite", "", "Ophite", "俄斐特派", "蛇派；奧斐特派", "term", "諾斯底教派", "崇蛇（智慧象徵）的諾斯底支派"),
    ("Basilidean", "", "Basilidean", "巴西里德派", "巴西利德派", "term", "諾斯底教派", "巴西里德創立的亞歷山卓諾斯底學派"),
]


def main():
    rows = []
    for i, (en, orig, rom, rec, var, etype, dom, reason) in enumerate(TERMS):
        rows.append({
            "name_english": en, "name_original": orig or None, "name_original_lang": "grc" if orig else None,
            "name_romanized": rom, "name_recommended": rec, "name_variants": var or None,
            "recommendation_reason": reason, "religion": "諾斯底", "entity_type": etype,
            "domain_of": dom or None, "sort_order": 100 + i,
        })
    r = requests.post(f"{URL}/rest/v1/deities", headers=H, data=json.dumps(rows), timeout=60)
    print("insert:", r.status_code, r.text[:200])
    r.raise_for_status()
    print(f"seeded {len(rows)} Gnostic terms into deities (religion=諾斯底)")


if __name__ == "__main__":
    main()
