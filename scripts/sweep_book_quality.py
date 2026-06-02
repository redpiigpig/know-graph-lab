"""Rule-based sweep over a translated book JSONL to fix the LLM-quality
bugs the structural pipeline can't catch.

Pairs with `scan_translated_book.py`:
  - scan reports T1 (heading bleed) and T2 (h3 vs volume drift).
  - sweep applies in-place fixes plus T3 (quote chars) and T8 (term
    consistency from the per-book TERM_FIXES table).

T1 fix — heading bleed: split heading at the body-marker position, prepend
the trailing portion onto the next paragraph. Example:

  Before:
    #### 第一章—書信寫作的契機既然我看到你
    ，最為卓越的狄奧格尼圖，極其渴慕要學習...

  After:
    #### 第一章—書信寫作的契機

    既然我看到你，最為卓越的狄奧格尼圖，極其渴慕要學習...

T2 fix — first-h3 letter-title drift: when the chunk has a `volume` set
and its first h3 (### ...) doesn't match the volume, replace the h3 text
with the volume name (since the volume is what the sidebar / breadcrumb
shows; the LLM's literal H3 wording shouldn't override that). The fix is
SKIPPED when the chunk has multiple h3s — those are EPUB-packaging cross-
work bleed cases (next letter's intro got pulled into prev chunk) and
need a careful split that this sweep doesn't attempt.

T3 fix — straight quotes → CJK corner brackets. Toggle each chunk's
straight " between 「 and 」 (alternating), and ' between 『 and 』, so
all Chinese quote chars use the proper full-width CJK form. Chunks with
odd quote-count get reported but not changed (heuristically broken).
Only the `content` (Chinese) is swept; `source_text` (English original)
is left untouched.

T8 fix — term consistency. TERM_FIXES is the per-book table of
{ wrong_term: standard_term } pairs, applied longest-first so prefix
collisions don't bite. For ANF Vol 1 the table is built into the script;
other books override by editing TERM_FIXES_BY_BOOK below.

Usage:
    python scripts/sweep_book_quality.py <ebook_id> --dry-run
    python scripts/sweep_book_quality.py <ebook_id>
    python scripts/sweep_book_quality.py <ebook_id> --no-push
    python scripts/sweep_book_quality.py <ebook_id> --only-t1   # T1 only
    python scripts/sweep_book_quality.py <ebook_id> --only-t2   # T2 only
    python scripts/sweep_book_quality.py <ebook_id> --only-t3   # quotes only
    python scripts/sweep_book_quality.py <ebook_id> --only-t8   # terms only
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT / "scripts"))
import standardize_ebook as se  # noqa: E402

URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H_GET = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
H_JSON = {**H_GET, "Content-Type": "application/json", "Prefer": "return=minimal"}

CHUNKS_DIR = Path(os.environ.get("EBOOK_CHUNKS_DIR")
                  or r"G:\我的雲端硬碟\資料\電子書\_chunks")

# Reuse scan's body-marker set — keep in sync.
BODY_MARKERS = [
    # 書信／講道體常見開頭
    "既然", "誠然", "親愛的", "讓我們", "誠如",
    "若你", "若我", "蓋此", "蓋我", "蓋經上", "蓋誠",
    "雖然", "但關於", "但是我", "然而我",
    "因此我", "正如我", "我先前", "我所說", "只要前一",
    "亞伯拉罕被", "本書信", "在已過去", "從一開始",
    # 教父神學論述體（Hippolytus / Origen / Tertullian 常見）
    # 注意：避免「其後／其人／其乃」這類太通用 — 容易在 title 內已出現。
    "據說", "此人主張", "此哲", "此學派",
    "凡此", "凡有", "蓋因", "蓋自此", "蓋若",
    "於是", "於此", "故此", "故知", "故其",
    "今將", "今者", "今當", "我今",
    "彼等主張", "彼乃為",
]
TITLE_CLOSE_PUNCT = re.compile(r"[。！？」）]\s*$")
EM_DASH_SPLIT_RE = re.compile(r"^(第[一二三四五六七八九十百千零0-9]+章\s*[—\-－]+\s*)(.+)$")
# 用來切 heading 中間的標點邊界（；。！？）— title 通常以「；」分隔多 phrase，
# 內文則接續純文字。當 heading 長度 > 25 字且有 ; / 。等邊界時觸發。
PUNCT_BOUNDARY_RE = re.compile(r"[；。！？]")

# Per-book term consistency fixes — { wrong_term: standard_term }. The
# standards match the volume / NCX-derived names in consolidate_by_ncx.
# Longest patterns first to avoid prefix collision (科林斯 must be tried
# before 科林).
TERM_FIXES_ANF_VOL_1 = {
    # Corinth — volume name uses 哥林多 (Protestant)
    "科林多人": "哥林多人",
    "科林斯人": "哥林多人",
    "科林多教會": "哥林多教會",
    "科林斯教會": "哥林多教會",
    "科林多": "哥林多",
    "科林斯": "哥林多",
    "科林妥": "哥林多",
    "格林多前書": "哥林多前書",
    "格林多後書": "哥林多後書",
    "格林多": "哥林多",
    # Diognetus — addressee of Mathetes' letter. Volume = 致丟格那妥書.
    "狄奧格尼圖斯": "丟格那妥",
    "狄奧格尼特斯": "丟格那妥",
    "狄奧格尼圖": "丟格那妥",
    "狄奧格尼特": "丟格那妥",
    "狄奧格尼": "丟格那妥",
    # Paul — book uses 保羅 (Protestant)
    "聖保祿": "聖保羅",
    "保祿": "保羅",
    # Philippi — volume name uses 腓立比 (Protestant)
    "斐理伯人書": "腓立比人書",
    "斐理伯人": "腓立比人",
    "斐理伯": "腓立比",
    # Cephas / 磯法 — Catholic 革法 → Protestant 磯法
    "革法": "磯法",
    # Smyrna — volume uses 士每拿
    "士麥那": "士每拿",
    # Tarsus — volume uses 他爾索, but body shows variants
    "他爾蘇城": "他爾索",
    "他爾蘇": "他爾索",
    "塔爾蘇": "他爾索",
    # Aristion — Papias references this disciple of John
    "亞里斯頓": "亞里斯鐸",
    # Jupiter — sweep both ways could happen; prefer 朱庇特 (more common
    # in Latin transliteration tradition). Body uses both.
    "木星": "朱庇特",
    # Typos
    "平安安": "平安",
}

# ── ANF Vol 2 — Fathers of the Second Century ───────────────────────────
# Hermas / Tatian / Athenagoras / Theophilus / Clement of Alexandria
TERM_FIXES_ANF_VOL_2 = {
    # Corinth — Protestant 哥林多
    "科林多人": "哥林多人",
    "科林斯人": "哥林多人",
    "科林多": "哥林多",
    "科林斯": "哥林多",
    "科林妥": "哥林多",
    "格林多前書": "哥林多前書",
    "格林多後書": "哥林多後書",
    "格林多": "哥林多",
    # Paul — Protestant 保羅
    "聖保祿": "聖保羅",
    "保祿": "保羅",
    # Philippi — Protestant 腓立比
    "斐理伯人書": "腓立比人書",
    "斐理伯人": "腓立比人",
    "斐理伯": "腓立比",
    # Cephas — Protestant 磯法
    "革法": "磯法",
    "克法": "磯法",
    # Antioch
    "安條克": "安提阿",
    # Smyrna — Vol 1 standard 士每拿
    "士麥那": "士每拿",
    # Clement of Alexandria — volume uses 革利免 (亞歷山卓)
    # 革利免 是希臘文 Κλήμης (Klemēs) 的音譯，思高/和合本/教會傳統都用此譯名；
    # 不要被 LLM 校對誤導改成英文音譯「克雷門」。
    "克萊門": "革利免",
    "克雷門": "革利免",
    # Valentinus — Vol 1 standard 瓦倫廷
    "瓦倫提努": "瓦倫廷",
    "華倫提奴": "瓦倫廷",
    "華倫提努": "瓦倫廷",
    # Heraclitus
    "赫拉克里特": "赫拉克利特",
    # Thales — Protestant Greek philosophy convention
    "泰勒斯": "泰利斯",
    # Democritus
    "德謨克里特": "德謨克利特",
    # Protagoras
    "普羅泰哥拉": "普羅泰戈拉",
    # Caius (proper name in Hermas + Clement)
    "蓋猶": "該猶",
    # Epicurus
    "伊比鳩魯": "伊壁鳩魯",
    # Hera (Greek goddess) — 赫拉 is standard; 赫剌 is rare variant
    "赫剌": "赫拉",
    # Jupiter (Vol 1 convention)
    "木星": "朱庇特",
    # Aristion (Vol 1 convention from Papias)
    "亞里斯頓": "亞里斯鐸",
    # Typos seen — 違揹 (carry-on-back) is wrong for 違背 (violate)
    "違揹": "違背",
    "平安安": "平安",
    # Autolycus — addressee of Theophilus's letter; normalize to 奧托呂庫
    "奧託呂庫": "奧托呂庫",
    "歐多呂庫": "奧托呂庫",
    "奧多利古": "奧托呂庫",
    "歐多魯克": "奧托呂庫",
    # Cassian — proper transliteration is 卡西安 (Protestant); 格西安 is wrong
    "若望‧格西安": "卡西安",
    "格西安": "卡西安",
    # Sicyon — Greek city; standardize to 西錫翁
    "錫錫翁": "西錫翁",
}

# ── ANF Vol 3 — Tertullian (Apologetic + Anti-Marcion + Ethical) ────────
TERM_FIXES_ANF_VOL_3 = {
    # Corinth
    "科林多人": "哥林多人",
    "科林斯人": "哥林多人",
    "科林多": "哥林多",
    "科林斯": "哥林多",
    "格林多前書": "哥林多前書",
    "格林多後書": "哥林多後書",
    "格林多": "哥林多",
    # Paul — Protestant 保羅
    "聖保祿": "聖保羅",
    "保祿": "保羅",
    # Peter — Protestant 彼得 (Tertullian text leans Catholic 伯多祿 due to
    # Latin sources; standardize to Protestant for cross-volume consistency)
    "伯多祿": "彼得",
    # Philippi
    "斐理伯人書": "腓立比人書",
    "斐理伯人": "腓立比人",
    "斐理伯": "腓立比",
    # Cephas
    "革法": "磯法",
    "克法": "磯法",
    # Valentinus — Vol 1 standard 瓦倫廷
    "瓦倫提努": "瓦倫廷",
    "華倫提奴": "瓦倫廷",
    "華倫提努": "瓦倫廷",
    # Hermogenes — Tertullian's adversary in《駁黑摩根》; unify to 黑摩根
    "黑爾摩根尼斯": "黑摩根",
    "赫莫根尼斯": "黑摩根",
    "黑摩根尼斯": "黑摩根",
    "赫摩根": "黑摩根",
    "赫莫根": "黑摩根",
    "黑爾摩根": "黑摩根",
    # Thales / Democritus / Protagoras
    "泰勒斯": "泰利斯",
    "塔勒斯": "泰利斯",
    "德謨克里特": "德謨克利特",
    "普羅泰哥拉": "普羅泰戈拉",
    # Pliny
    "普林尼": "普利尼",
    # Heracles → 海格力斯 (Vol 1 latinate convention)
    "赫拉克勒斯": "海格力斯",
    # Jupiter (Vol 1 convention)
    "木星": "朱庇特",
    # Typo
    "違揹": "違背",
    "對峙巖": "對峙岩",
    # Perpetua/Felicitas — Vol 3 glossary 統一為 佩爾佩圖亞 / 費莉西塔斯
    "永卓": "佩爾佩圖亞",
    "費利西塔斯": "費莉西塔斯",  # 利 vs 莉
    "費利西塔": "費莉西塔斯",
    "菲莉西妲": "費莉西塔斯",
    # Saturus / Saturninus 是兩個不同人物，不要互相替換：
    # - Saturus (殉道者，跟 Perpetua 一起死於 203 AD) → 薩圖魯
    # - Saturninus (羅馬農業神 Saturnus，或 Toulouse 的殉道者) → 薩圖爾努斯
    # 早期版本曾把兩者合併為「薩圖爾努斯」是 bug，必須保持兩名分離
    # Jupiter — Vol 1 標準 朱庇特
    "奧林匹亞宙斯": "奧林匹斯的朱庇特",
    "盧米娜神": "魯米娜神",
}

TERM_FIXES_ANF_VOL_4 = {
    # 思高聖經書名 → 和合本（跨卷統一新教譯名）
    "瑪竇福音": "馬太福音",
    "若望福音": "約翰福音",
    "若望一書": "約翰一書",
    "若望二書": "約翰二書",
    "若望三書": "約翰三書",
    "格林多前書": "哥林多前書",
    "格林多後書": "哥林多後書",
    "格林多人前書": "哥林多人前書",
    "格林多人後書": "哥林多人後書",
    "格林多": "哥林多",
    "格言書": "箴言",
    "厄則克爾": "以西結",
    "厄則克耳": "以西結",
    "依撒意亞": "以賽亞",
    "厄弗所": "以弗所",
    "斐理伯": "腓立比",
    # 思高 vs 和合 人物
    "厄娃": "夏娃",                  # Eve
    "巴拉罕": "巴蘭",                # Balaam
    # Celsus typo (俄利根《駁塞爾蘇斯》主角)
    "蕭爾蘇斯": "塞爾蘇斯",
    "比克爾蘇斯": "塞爾蘇斯",
    # Valentinus — Vol 1/3 標準 瓦倫廷
    "瓦倫提努": "瓦倫廷",
    "瓦倫蒂努斯": "瓦倫廷",
    # Lucian (希臘諷刺作家)
    "露西安": "路西安",
    # Herennius Philo
    "海倫尼烏斯": "赫倫尼烏斯",
    # Greek statesmen / mythological figures
    "題斯提克利": "特米斯托克利",     # Themistocles
    "喬卡斯塔": "約卡斯塔",          # Jocasta
    # Oracles & places
    "特爾斐": "德爾斐",              # Delphi
    "米利圖": "米利都",              # Miletus
    # Translator's name (Rev. S. Thelwall)
    "瑟爾沃爾": "塞爾沃爾",
    "蘭‧瑟爾沃": "塞爾沃爾",
    # Typos & word fixes
    "遲晚": "遲早",
    "縞瑪瑙石": "縞瑪瑙",
    "逍遙派": "逍遙學派",            # Peripatetics
    # Origen of Alexandria — Vol 4 詞庫 俄利根
    "奧利金": "俄利根",
    "奧利根": "俄利根",
    # Africanus
    "亞非利加努斯": "阿弗里卡努",
    "阿非利加努斯": "阿弗里卡努",
}

# Cross-volume baseline (思高聖經書名 → 和合本 + 一般 typo) —
# Vol 5/6/7 起步用此 baseline；post-llm_proofread 再個別擴充
TERM_FIXES_ANF_COMMON = {
    # 思高聖經書名 → 和合本
    "瑪竇福音": "馬太福音",
    "若望福音": "約翰福音",
    "若望一書": "約翰一書",
    "若望二書": "約翰二書",
    "若望三書": "約翰三書",
    "格林多前書": "哥林多前書",
    "格林多後書": "哥林多後書",
    "格林多人前書": "哥林多人前書",
    "格林多人後書": "哥林多人後書",
    "格林多": "哥林多",
    "格言書": "箴言",
    "厄則克爾": "以西結",
    "厄則克耳": "以西結",
    "依撒意亞": "以賽亞",
    "厄弗所": "以弗所",
    "斐理伯": "腓立比",
    "厄娃": "夏娃",
    "巴拉罕": "巴蘭",
    "瓦倫提努": "瓦倫廷",
    "瓦倫蒂努斯": "瓦倫廷",
    # 跨卷詞庫名
    "奧利金": "俄利根",
    "奧利根": "俄利根",
    "亞非利加努斯": "阿弗里卡努",
    "阿非利加努斯": "阿弗里卡努",
}

TERM_FIXES_ANF_VOL_5 = dict(TERM_FIXES_ANF_COMMON, **{
    # ── proofread 2026-05-28 抽出 ──────────────────────────────────────
    # Seven Sages 七賢
    "庇達庫": "庇塔庫斯",          # Pittacus of Mitylene
    "基隆": "奇洛",                 # Chilo of Sparta
    "裴裡安德": "佩里安德",         # Periander of Corinth
    "克萊奧布盧斯": "克里奧布盧斯", # Cleobulus of Lindus
    # Hippolytus 駁諸異端 — 異端領袖名
    "尤斯提努": "猶斯定",           # Justinus (gnostic) — 跟 Justin Martyr 同名統一
    "塞蒂安人": "塞特人",           # Sethians
    "撒土爾尼努": "撒圖尼魯",       # Saturnilus
    # Cyprian 書信 — 人物
    "克魯斯神父": "克魯斯",         # Abbe Cruice (近代編者)
    # Cross-vol typos / variants
    "克林妥": "哥林多",             # Vol 2 標準 哥林多
    "希玻里圖": "希波呂圖",         # Hippolytus
    "希玻律陀": "希波呂圖",
    "希波律陀": "希波呂圖",
    "希玻律圖": "希波呂圖",
    "塞浦良": "居普良",             # Cyprian — Vol 5 詞庫定為「居普良」
    "西普里安": "居普良",
    "西彼連": "居普良",
    "賽普林": "居普良",
    "諾瓦圖斯": "諾瓦提安",         # Novatian
    "諾瓦提亞努斯": "諾瓦提安",
})
TERM_FIXES_ANF_VOL_6 = dict(TERM_FIXES_ANF_COMMON)
TERM_FIXES_ANF_VOL_7 = dict(TERM_FIXES_ANF_COMMON)

# ── NPNF1 Vol 1 (Augustine: Confessions + Letters) ──────────────────────────
# 譯名鎖定：奧古斯丁（of Hippo → 希波的奧古斯丁）。收斂思高/異體。
TERM_FIXES_NPNF1_VOL_1 = dict(TERM_FIXES_ANF_COMMON, **{
    "奧斯定": "奧古斯丁",          # 思高 → 新教標準
    "奧古斯汀": "奧古斯丁",
    "奧古斯廷": "奧古斯丁",
    "奧古斯定": "奧古斯丁",
    "盎博羅削": "安波羅修",        # Ambrose 思高 → 新教
    "安博羅修": "安波羅修",
    "盎博羅修": "安波羅修",
    "白拉奇": "伯拉糾",            # Pelagius
    "貝拉基": "伯拉糾",
    "摩尼加": "莫尼卡",            # Monica (mother) — 與摩尼教 Manichaean 區隔
    "莫尼加": "莫尼卡",
})

# ── NPNF2 Vol 4 (Athanasius) ────────────────────────────────────────────────
# 譯名鎖定：亞他那修（NOT 阿塔那修）；Arius → 亞流。
TERM_FIXES_NPNF2_VOL_4 = dict(TERM_FIXES_ANF_COMMON, **{
    "阿塔那修": "亞他那修",
    "亞塔那修": "亞他那修",
    "阿他那修": "亞他那修",
    "亞大納西": "亞他那修",
    "阿他拿修": "亞他那修",
    "阿里烏斯": "亞流",            # Arius
    "阿里烏": "亞流",
    "亞利烏": "亞流",
    "阿流": "亞流",
    "亞略": "亞流",
    "安多尼": "安東尼",            # Antony of Egypt
    "聖安當": "安東尼",
    "亞歷山卓的狄奧尼修斯": "亞歷山卓的狄奧尼修",  # 詞庫 name_recommended
})

# ── NPNF1 Chrysostom (Vol 9-14) ─────────────────────────────────────────────
# 譯名鎖定（user 2026-05-30）：John Chrysostom → 金口若望（詞庫 name_recommended）。
# 收斂新教音譯「屈梭多模」、東正「聖金口約安」、各式「金口約翰／克里索斯托」等變體。
TERM_FIXES_NPNF1_CHRYSOSTOM = dict(TERM_FIXES_ANF_COMMON, **{
    "聖若望‧屈梭多模": "金口若望", "約翰‧屈梭多模": "金口若望", "約翰·屈梭多模": "金口若望",
    "若望‧屈梭多模": "金口若望", "屈梭多模": "金口若望",
    "金口聖若望": "金口若望", "金口約翰": "金口若望", "聖金口約安": "金口若望",
    "約翰‧克里索斯通": "金口若望", "約翰·克里索斯通": "金口若望",
    "克里索斯托姆": "金口若望", "克里索斯托": "金口若望", "屈索斯敦": "金口若望",
    "狄奧多羅": "狄奧多若",          # Theodore (of Mopsuestia, addressee)
})

# ── NPNF2 教會史家（Vol 1-3：優西比烏／蘇格拉底／索佐門／狄奧多勒）────────────
# 譯名鎖定：Eusebius→優西比烏（該撒利亞的優西比烏）；Socrates Scholasticus→蘇格拉底；
# Sozomen→索佐門；Constantine→君士坦丁。收斂常見音譯變體。
TERM_FIXES_NPNF2_HISTORIANS = dict(TERM_FIXES_ANF_COMMON, **{
    "尤西比烏斯": "優西比烏", "優西比烏斯": "優西比烏", "尤西比烏": "優西比烏",
    "猶西比烏": "優西比烏", "攸西比烏": "優西比烏", "尤瑟比烏斯": "優西比烏",
    "索佐曼": "索佐門", "索左門": "索佐門", "蘇佐門": "索佐門", "索佐墨諾斯": "索佐門",
    "康斯坦丁": "君士坦丁", "君士坦汀": "君士坦丁",
    "蘇格拉底斯": "蘇格拉底",
})

# NPNF2 Vol 3 — Theodoret（史家，繼承 HISTORIANS）+ Jerome + Rufinus
TERM_FIXES_NPNF2_V3 = dict(TERM_FIXES_NPNF2_HISTORIANS, **{
    # Theodoret → 狄奧多勒（詞庫 居魯斯的狄奧多勒）；收斂其他變體
    "狄奧多雷特": "狄奧多勒", "狄奧多雷": "狄奧多勒", "狄奧多列": "狄奧多勒", "提阿多勒": "狄奧多勒",
    "傑羅姆": "耶柔米", "哲羅姆": "耶柔米", "耶羅米": "耶柔米", "熱羅尼莫": "耶柔米",
    "魯非努": "魯菲努斯", "魯芬努斯": "魯菲努斯", "魯非諾": "魯菲努斯", "魯弗納": "魯菲努斯",
})

# NPNF2 Vol 5 — Gregory of Nyssa（迦帕多家教父）
# 譯名鎖定（2026-05-29 決策）：Gregory → 格列高里（「里」非「理」/「利」）；Basil → 巴西流
TERM_FIXES_NPNF2_V5 = dict(TERM_FIXES_ANF_COMMON, **{
    "尼撒的格列高理": "尼撒的格列高里", "尼撒的格列高利": "尼撒的格列高里",
    "尼斯的格列高里": "尼撒的格列高里", "尼撒的格里高利": "尼撒的格列高里",
    "格列高理": "格列高里", "格列高利": "格列高里", "格里高利": "格列高里",
    "尤諾米烏斯": "歐諾米烏", "歐諾米烏斯": "歐諾米烏", "歐諾米": "歐諾米烏",  # Eunomius
    "巴西略": "巴西流",
})

# 所有 ANF vol 都吃 ANF_COMMON baseline；per-vol specific 覆蓋 baseline。
TERM_FIXES_BY_BOOK: dict[str, dict[str, str]] = {
    "c98d358d-7066-4691-a896-b7232707b0db": {**TERM_FIXES_ANF_COMMON, **TERM_FIXES_ANF_VOL_1},  # ANF Vol 1
    "4e3d16fc-ef4f-420f-a3ec-56e2e92d659f": {**TERM_FIXES_ANF_COMMON, **TERM_FIXES_ANF_VOL_2},  # ANF Vol 2
    "364dac2e-410f-4906-be63-8bb86b4865ee": {**TERM_FIXES_ANF_COMMON, **TERM_FIXES_ANF_VOL_3},  # ANF Vol 3
    "904661d3-16fc-4f37-bb04-f7c4aa7671e9": TERM_FIXES_ANF_VOL_4,  # ANF Vol 4 (already includes common)
    "0e08c662-540b-4186-b250-9bca0cfe1002": TERM_FIXES_ANF_VOL_5,  # ANF Vol 5
    "dffaae40-e088-41c1-ab7f-9b96f9249661": TERM_FIXES_ANF_VOL_6,  # ANF Vol 6
    "75d8aae0-7431-4be9-baee-c57d26599653": TERM_FIXES_ANF_VOL_7,  # ANF Vol 7
    "9edb7c37-4231-412b-83bd-78f3f793cc0a": TERM_FIXES_NPNF1_VOL_1,  # NPNF1 Vol 1 Augustine
    "e01917ab-7429-41a0-9859-eddad413ef60": TERM_FIXES_NPNF2_VOL_4,  # NPNF2 Vol 4 Athanasius
    "1eb50be9-34ac-4ce3-874d-1280975851fc": TERM_FIXES_NPNF1_VOL_1,  # NPNF1 Vol 2 Augustine (City of God)
    "d7f66759-3fa9-4633-abde-87003cdbcc06": TERM_FIXES_NPNF1_VOL_1,  # NPNF1 Vol 3 Augustine (Holy Trinity)
    "56ef3d65-c559-41f8-8d68-ba6c13e47876": TERM_FIXES_NPNF1_VOL_1,  # NPNF1 Vol 4 Augustine (Anti-Manich/Donatist)
    "df789501-5620-4833-a0a0-6e8f1a031bb1": TERM_FIXES_NPNF1_VOL_1,  # NPNF1 Vol 5 Augustine (Anti-Pelagian)
    "7bff8a13-3c35-43d4-9b4c-b7c3c9f81076": TERM_FIXES_NPNF1_VOL_1,  # NPNF1 Vol 6 Augustine (Sermon Mount + Gospel Harmony)
    "0069932a-7b27-4c06-9874-b74d51ad564e": TERM_FIXES_NPNF1_VOL_1,  # NPNF1 Vol 7 Augustine (Tractates on John + 1 John + Soliloquies)
    "2accee20-5f9d-4099-9ce9-3dda0726a74b": TERM_FIXES_NPNF1_VOL_1,  # NPNF1 Vol 8 Augustine (Expositions on the Psalms)
    "76df31fe-e732-4aa6-88c2-d650a09fb688": TERM_FIXES_NPNF1_CHRYSOSTOM,  # NPNF1 Vol 9 Chrysostom (On the Priesthood + Ascetic Treatises)
    "0d160c29-8d61-4dbc-8f8e-d47fee694eab": TERM_FIXES_NPNF1_CHRYSOSTOM,  # NPNF1 Vol 10 Chrysostom (Homilies on Matthew)
    "4d73c561-aa4e-46b2-8e29-d331c5b9d28d": TERM_FIXES_NPNF1_CHRYSOSTOM,  # NPNF1 Vol 11 Chrysostom (Acts + Romans)
    "bf2dd1b2-ae53-43c2-8fac-7ce10e137c10": TERM_FIXES_NPNF1_CHRYSOSTOM,  # NPNF1 Vol 12 Chrysostom (1 & 2 Corinthians)
    "9192cb77-3ce2-4adb-9d90-76200e452763": TERM_FIXES_NPNF1_CHRYSOSTOM,  # NPNF1 Vol 13 Chrysostom (Galatians..Philemon)
    "91c7023f-2e63-4b16-897a-43bdf7d5e290": TERM_FIXES_NPNF1_CHRYSOSTOM,  # NPNF1 Vol 14 Chrysostom (John + Hebrews)
    "91ff3a5e-cd1f-4ab4-acb7-70cb7a80c4b9": TERM_FIXES_NPNF2_HISTORIANS,  # NPNF2 Vol 1 Eusebius (Church History + Life of Constantine)
    "29782dd6-ece9-446a-83ed-9cc0892d7cc7": TERM_FIXES_NPNF2_HISTORIANS,  # NPNF2 Vol 2 Socrates + Sozomen
    "a7e5956e-8851-4d0f-b3d2-1f823d1bdc81": TERM_FIXES_NPNF2_V3,  # NPNF2 Vol 3 Theodoret + Jerome + Rufinus
    "9b94e7c1-fa82-4910-a31f-9db1e2e040bb": TERM_FIXES_NPNF2_V5,  # NPNF2 Vol 5 Gregory of Nyssa
}


def find_bleed_split(heading_text: str) -> tuple[str, str] | None:
    """If heading is a bleed, return (title_proper, body_bleed); else None.

    `heading_text` is the text AFTER the leading `#### ` markers. Strategies:
      A. If heading is SHORT (≤25) AND closes with 「。！？」」 → assume
         clean descriptive title, no split. Long headings that end with
        「。」are usually a body sentence appended to the title — keep
         processing.
      B. Match「第X章—」prefix; inspect the tail.
      C. (BODY_MARKERS) Find earliest body marker in the tail at pos > 1.
      D. (PUNCT_BOUNDARY, 2026-05-29) When B/C miss but heading is long
         (>25 chars), split at the last 「；。！？」 in the tail when the
         remainder after the punct is ≥ 6 chars — that's almost always
         a bled first sentence of the body.
    """
    if len(heading_text) <= 25 and TITLE_CLOSE_PUNCT.search(heading_text):
        return None
    m = EM_DASH_SPLIT_RE.match(heading_text)
    if not m:
        return None
    prefix, tail = m.group(1), m.group(2)
    # Strategy C — BODY_MARKERS (highest precision)
    best_pos = None
    for marker in BODY_MARKERS:
        pos = tail.find(marker)
        if pos >= 2 and (best_pos is None or pos < best_pos):
            best_pos = pos
    if best_pos is not None:
        return prefix + tail[:best_pos].rstrip(), tail[best_pos:].strip()
    # Strategy D — punctuation boundary, only for longer overflows.
    # Vol 2-7 reality: many bleeds have no body marker (e.g. proper-noun
    # subject「恩培多克勒乃其後…」), but the title still has 「；」phrase
    # separators. Pick the LAST 「；。！？」 such that the remainder is a
    # plausible body sentence (≥ 6 chars).
    if len(heading_text) > 25:
        positions = [m.start() for m in PUNCT_BOUNDARY_RE.finditer(tail) if m.start() >= 2]
        for p in reversed(positions):
            after = tail[p + 1:].strip()
            if len(after) >= 6:
                title_proper = prefix + tail[:p + 1].rstrip()
                return title_proper, after
    return None


def sweep_t1(content: str) -> tuple[str, int]:
    """Apply T1 (heading bleed) fix to a chunk's markdown content.
    Returns (new_content, num_fixes)."""
    lines = content.split("\n")
    out: list[str] = []
    fixes = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        h_match = re.match(r"^(#{1,4})\s+(.+?)\s*$", line)
        if not h_match:
            out.append(line)
            i += 1
            continue
        marks, heading_text = h_match.group(1), h_match.group(2)
        split = find_bleed_split(heading_text)
        if not split:
            out.append(line)
            i += 1
            continue
        title_proper, body_bleed = split
        out.append(f"{marks} {title_proper}")
        # Locate the next non-empty non-heading line — that's the body
        # paragraph the bleed escaped from. Prepend the bleed onto it.
        j = i + 1
        # Skip blank lines after the heading
        while j < len(lines) and not lines[j].strip():
            out.append(lines[j])
            j += 1
        if j < len(lines):
            next_line = lines[j]
            # If the next line starts with a heading marker, the bleed has
            # nowhere natural to go — emit it as its own paragraph rather
            # than mash it into another heading.
            if re.match(r"^#{1,4}\s", next_line):
                out.append("")
                out.append(body_bleed)
            else:
                # The body line often starts with 「，」(orphan comma left
                # over from the bleed cut). Stitch cleanly.
                stitched = (body_bleed + next_line).replace("  ", " ")
                out.append(stitched)
            i = j + 1
        else:
            out.append("")
            out.append(body_bleed)
            i = j
        fixes += 1
    return "\n".join(out), fixes


def sweep_t3(content: str) -> tuple[str, int, bool]:
    """Toggle straight ASCII quotes to CJK corner brackets.

    `"`→ alternates between 「 and 」 starting with 「.
    `'`→ alternates between 『 and 』 starting with 『.

    Returns (new_content, num_replaced, ok). ok=False when a column has
    an odd number of straight quotes (likely broken pairing) — we still
    apply the toggle but caller should report.
    """
    fixes = 0
    ok = True
    n_dq = content.count('"')
    n_sq = content.count("'")
    if n_dq % 2:
        ok = False
    if n_sq % 2:
        ok = False
    # Toggle double quotes
    if n_dq:
        toggle = [True]  # True → 「, False → 」
        def _dq(_m: re.Match) -> str:
            opening = toggle[0]
            toggle[0] = not toggle[0]
            return "「" if opening else "」"
        content = re.sub(r'"', _dq, content)
        fixes += n_dq
    # Toggle single quotes (only when chunk has them; rare)
    if n_sq:
        toggle = [True]
        def _sq(_m: re.Match) -> str:
            opening = toggle[0]
            toggle[0] = not toggle[0]
            return "『" if opening else "』"
        content = re.sub(r"'", _sq, content)
        fixes += n_sq
    return content, fixes, ok


def sweep_t12(content: str) -> tuple[str, int]:
    """Insert a blank line between any ##/###/#### heading and the
    immediately-following non-heading text.

    Background: renderMarkdown uses a multiline regex
    `^###[ \\t]+([\\s\\S]+?)(?=\\n[ \\t]*\\n|\\n#|\\Z)` to capture full h3
    headings (CCEL wraps long titles across lines, so single-line `.+$`
    misses the rest). The lookahead means the heading consumes everything
    UNTIL the next blank line. When a body paragraph follows a heading
    with only a single `\\n` separator, the whole paragraph gets absorbed
    into the heading and rendered as a giant H3 — destroying ZH↔EN
    paragraph alignment in bilingual mode (chunk 11 「致腓立比人的坡旅甲
    書信」 + greeting got fused into one heading block).

    Fix: insert `\\n` between heading + body so the lookahead fires.
    """
    fixed, n = re.subn(
        r"(^#{2,4}[ \t]+[^\n]+)\n(?!\n|#)",
        r"\1\n\n",
        content, flags=re.M,
    )
    return fixed, n


def sweep_t8(content: str, term_fixes: dict[str, str]) -> tuple[str, int]:
    """Apply term-consistency replacements, longest-first to avoid prefix
    collision."""
    if not term_fixes:
        return content, 0
    fixes = 0
    # Longest first
    for wrong in sorted(term_fixes, key=len, reverse=True):
        std = term_fixes[wrong]
        if wrong == std:
            continue
        n = content.count(wrong)
        if n == 0:
            continue
        content = content.replace(wrong, std)
        fixes += n
    return content, fixes


def sweep_t2(content: str, volume: str) -> tuple[str, int]:
    """If chunk has ONE h3 NEAR THE TOP and it differs from volume,
    replace it with the volume name.

    Skipped when:
    - chunk has multiple h3s (cross-work bleed needs a chunk-split, not
      a heading rename)
    - the lone h3 appears AFTER position threshold (default 30% of the
      chunk's length): a late-positioned h3 is almost certainly the
      bleeding intro of the NEXT letter (e.g. Justin Martyr intro stuck
      at the tail of the Papias fragments chunk), so renaming it to the
      current volume corrupts the meaning. Caught after a regression on
      ANF Vol 1 chunk 48.
    """
    if not volume:
        return content, 0
    h3_iter = list(re.finditer(r"^(### )(.+?)\s*$", content, re.M))
    letter_h3s = [m for m in h3_iter
                  if not re.match(r"第[一二三四五六七八九十百千零0-9]+章",
                                  m.group(2).strip())]
    if len(letter_h3s) != 1:
        return content, 0
    m = letter_h3s[0]
    # Position guard: only fix h3s that sit in the first 30% of content.
    # A letter title is naturally at the top; anything past 30% is almost
    # always a next-letter intro that got packaged into this chunk.
    if m.start() > len(content) * 0.30:
        return content, 0
    current = m.group(2).strip()
    current_clean = re.sub(r"\[\^\d+\]", "", current).strip()
    if current_clean == volume:
        return content, 0
    def _replace(m2: re.Match) -> str:
        body = m2.group(2).strip()
        body_clean = re.sub(r"\[\^\d+\]", "", body).strip()
        if body_clean == current_clean:
            return f"### {volume}"
        return m2.group(0)
    new_content, n = re.subn(r"^(### )(.+?)\s*$", _replace, content,
                             count=1, flags=re.M)
    return new_content, n


def fetch_book(ebook_id: str) -> dict:
    r = requests.get(f"{URL}/rest/v1/ebooks?id=eq.{ebook_id}&select=*",
                     headers=H_GET, timeout=30)
    r.raise_for_status()
    rows = r.json()
    if not rows:
        sys.exit(f"no ebooks row for {ebook_id}")
    return rows[0]


def sweep(ebook_id: str, dry_run: bool = False, push: bool = True,
          only_t1: bool = False, only_t2: bool = False,
          only_t3: bool = False, only_t8: bool = False,
          only_t12: bool = False) -> None:
    book = fetch_book(ebook_id)
    print(f"Book: {book['title']}")

    jsonl_path = CHUNKS_DIR / f"{ebook_id}.jsonl"
    chunks = [json.loads(l) for l in jsonl_path.read_text(encoding="utf-8").splitlines() if l]
    print(f"Loaded {len(chunks)} chunks")

    term_fixes = TERM_FIXES_BY_BOOK.get(ebook_id, {})

    # If any --only-X flag is set, run ONLY those steps. Else run all.
    any_only = only_t1 or only_t2 or only_t3 or only_t8 or only_t12
    run_t1 = (not any_only) or only_t1
    run_t2 = (not any_only) or only_t2
    run_t3 = (not any_only) or only_t3
    run_t8 = (not any_only) or only_t8
    run_t12 = (not any_only) or only_t12

    t1_total = t2_total = t3_total = t8_total = t12_total = 0
    t1_chunks = t2_chunks = t3_chunks = t8_chunks = t12_chunks = 0
    t3_odd_chunks: list[int] = []

    for c in chunks:
        content = c.get("content") or ""
        new_content = content
        if run_t1:
            new_content, n1 = sweep_t1(new_content)
            if n1:
                t1_total += n1
                t1_chunks += 1
        if run_t2:
            new_content, n2 = sweep_t2(new_content, c.get("volume") or "")
            if n2:
                t2_total += n2
                t2_chunks += 1
        if run_t3:
            new_content, n3, ok = sweep_t3(new_content)
            if n3:
                t3_total += n3
                t3_chunks += 1
            if not ok:
                t3_odd_chunks.append(c.get("chunk_index"))
        if run_t8 and term_fixes:
            new_content, n8 = sweep_t8(new_content, term_fixes)
            if n8:
                t8_total += n8
                t8_chunks += 1
        if run_t12:
            new_content, n12 = sweep_t12(new_content)
            if n12:
                t12_total += n12
                t12_chunks += 1
        if new_content != content:
            c["content"] = new_content

    print(f"\nT1 (heading bleed) fixes: {t1_total} in {t1_chunks} chunks")
    print(f"T2 (h3 letter-title) fixes: {t2_total} in {t2_chunks} chunks")
    print(f"T3 (quote chars) fixes:    {t3_total} in {t3_chunks} chunks")
    print(f"T12 (blank line after heading) fixes: {t12_total} in {t12_chunks} chunks")
    if t3_odd_chunks:
        print(f"  ⚠ odd-quote-count chunks (review manually): {t3_odd_chunks}")
    if term_fixes:
        print(f"T8 (term consistency) fixes: {t8_total} in {t8_chunks} chunks")
    else:
        print("T8 (term consistency): no TERM_FIXES table for this book")

    if dry_run:
        print("\n(dry-run; not writing)")
        return

    with open(jsonl_path, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"\n✓ wrote {jsonl_path.name} ({jsonl_path.stat().st_size // 1024} KB)")

    if push:
        try:
            se.push_to_r2(ebook_id, jsonl_path)
            print("✓ pushed R2")
        except Exception as e:
            print(f"⚠ R2 push: {e}", file=sys.stderr)

        # Refresh DB previews — content[:200] now reflects the fixed text.
        try:
            r = requests.delete(f"{URL}/rest/v1/ebook_chunks?ebook_id=eq.{ebook_id}",
                                headers=H_GET, timeout=30)
            if r.status_code not in (200, 204):
                print(f"⚠ preview DELETE: {r.status_code}", file=sys.stderr)
            rows = [{
                "ebook_id": ebook_id,
                "chunk_index": c["chunk_index"],
                "chunk_type": c.get("chunk_type", "chapter"),
                "page_number": c.get("page_number"),
                "chapter_path": c.get("chapter_path"),
                "content": (c.get("content") or "")[:200],
                "char_count": len(c.get("content") or ""),
            } for c in chunks]
            BATCH = 25
            for i in range(0, len(rows), BATCH):
                batch = rows[i:i + BATCH]
                rr = requests.post(f"{URL}/rest/v1/ebook_chunks",
                                   headers=H_JSON, json=batch, timeout=30)
                if rr.status_code not in (200, 201):
                    for row in batch:
                        requests.post(f"{URL}/rest/v1/ebook_chunks",
                                      headers=H_JSON, json=row, timeout=30)
            print(f"✓ refreshed previews ({len(rows)} rows)")
        except Exception as e:
            print(f"⚠ preview refresh: {e}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ebook_id")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-push", action="store_true")
    ap.add_argument("--only-t1", action="store_true")
    ap.add_argument("--only-t2", action="store_true")
    ap.add_argument("--only-t3", action="store_true")
    ap.add_argument("--only-t8", action="store_true")
    ap.add_argument("--only-t12", action="store_true")
    args = ap.parse_args()
    sweep(args.ebook_id, dry_run=args.dry_run, push=not args.no_push,
          only_t1=args.only_t1, only_t2=args.only_t2,
          only_t3=args.only_t3, only_t8=args.only_t8,
          only_t12=args.only_t12)


if __name__ == "__main__":
    main()
