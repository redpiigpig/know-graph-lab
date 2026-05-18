"""掃描 1542 本書，找出可能誤分類的書。

策略：每本書用 title-regex 推斷「應該」的分類，跟現行 category 對比。

只列出「現行 cat 跟推斷 cat 不一致」的書 — 縮小人工檢查範圍。

執行：
  python scripts/_audit_all_categories.py            # 印疑似誤分提案
  python scripts/_audit_all_categories.py --apply    # 實跑：UPDATE + 移檔
"""
import json
import os
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()
import requests

sys.stdout.reconfigure(encoding="utf-8")

APPLY = "--apply" in sys.argv
SUPABASE_URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
DRIVE_ROOT = Path(r"G:\我的雲端硬碟\資料\電子書")

# Order matters — checked top-down，first match wins
# User 規則：基督教史/教會史/傳記 → 世界宗教/基督教；神學只收系統著作／教父原典／神學論述
RULES = [
    # 神學 — 只收「教父原典英譯／系統神學／信理／神學家本人著作（非傳記）」
    ("神學", [
        # 系統神學 / 信理 / 教義論述
        r"系統神學", r"信理神學", r"^神學概論", r"^神學大綱", r"^神學綱要",
        r"基督論(?!.*中國)", r"三一論", r"聖靈論", r"末世論", r"成義論", r"恩典論",
        r"基督教神學", r"基督教神學導論", r"基督教教義",
        # 教父原典（英譯／中譯）— 必須是「原典」標題，不是「教父歷史」
        r"^教父$", r"^使徒教父", r"^宗徒.*教父", r"教父集", r"NPNF", r"ANF", r"Schaff",
        r"Sarug.*Homilies", r"Bazaar of Heracleides", r"Babai.*Union",
        # 教父研究（學術 monograph）— 對 specific theological controversy
        r"Cyril of Alexandria.*Christological", r"Nestorius.*Teaching",
        r"Monophysite Movement", r"Christ in Christian Tradition", r"Council of Chalcedon",
        # 神學家著作（非傳記）— 中文書名通常含「論」、「教義學」、「神學」
        r"Aquinas.*Summa", r"^奧古斯丁論", r"奧古斯丁.*神學",
        r"教會教義學", r"Church Dogmatics",
    ]),
    # 世界宗教 — 各宗教自身原典／教義／祈禱書／講道集（學術研究除外）
    ("世界宗教", [
        # 基督教 / 基督教傳統（不是學術神學）
        r"^聖經", r"^新約.*譯本", r"^舊約.*譯本", r"祈禱書", r"信經(?!.*論)",
        r"中譯本.*聖經", r"和合本", r"思高本", r"呂振中譯本",
        # 佛教
        r"佛教(?!.*神學)", r"佛學", r"禪宗", r"密宗", r"金剛經", r"法華經", r"心經",
        r"華嚴經", r"淨土", r"觀音", r"菩薩", r"羅漢", r"Buddhism", r"Buddhis",
        # 伊斯蘭
        r"伊斯蘭(?!.*神學)", r"穆斯林", r"可蘭經", r"古蘭經", r"Qur", r"Islam(?!ic Theology)",
        r"蘇菲", r"什葉派", r"遜尼派",
        # 猶太
        r"猶太教", r"以色列宗教", r"Torah", r"Talmud", r"Kabbalah", r"卡巴拉", r"哈西迪",
        # 印度教
        r"印度教", r"Hindu", r"吠陀", r"奧義書", r"婆羅門", r"濕婆", r"梵天",
        # 道教 / 中國民間信仰
        r"道教", r"道家經典", r"中國民間信仰", r"五大宗教", r"中國的宗教",
        # 波斯 / 瑣羅亞斯德
        r"瑣羅亞斯德", r"祆教", r"Zoroastr", r"Avesta", r"阿維斯塔",
        # 巴哈伊
        r"巴哈伊", r"Baha[\'i]",
        # 摩門
        r"摩門", r"Mormon",
    ]),
    # 宗教學 — 跨宗教研究／神話學／宗教社會學
    ("宗教學", [
        r"宗教學", r"宗教社會學", r"宗教心理", r"宗教哲學", r"宗教比較", r"比較宗教",
        r"宗教現象", r"宗教對話", r"宗教交談", r"宗教史(?!.*基督|.*佛|.*伊斯|.*猶)",
        r"神話學", r"神話與", r"古典神話", r"Eliade", r"Frazer", r"Durkheim",
        r"涂爾幹", r"涂尔干", r"Berger.*神聖",
        r"神聖.*世俗", r"神聖.*帷幕", r"宇宙與歷史", r"金枝",
        r"宗教經驗(?!_)", r"宗教生活", r"宗教本質",
    ]),
    # 哲學 — 哲學家、流派、形上學、倫理學、邏輯
    ("哲學", [
        r"哲學(?!.*宗教)", r"形上學", r"形而上學", r"倫理學(?!.*基督|.*佛|.*伊斯)",
        r"邏輯學", r"認識論", r"知識論", r"美學",
        r"柏拉圖", r"亞里士多德", r"亞里斯多德", r"蘇格拉底", r"伊壁鳩魯", r"斯多葛",
        r"Plato", r"Aristotle", r"Socrates",
        r"笛卡兒", r"Descartes", r"康德", r"Kant", r"黑格爾", r"Hegel", r"叔本華",
        r"尼采(?!.*基督)", r"Nietzsche", r"海德格", r"Heidegger",
        r"沙特", r"沙特爾", r"Sartre", r"梅洛龐蒂", r"列維納斯", r"Levinas",
        r"福柯", r"Foucault", r"德希達", r"Derrida", r"德勒茲", r"Deleuze",
        r"維根斯坦", r"Wittgenstein", r"羅素", r"Russell", r"懷海德", r"Whitehead",
        r"士林哲學", r"經院辯證", r"中世紀哲學",
    ]),
    # 心理學 — 心理學、精神分析、認知科學
    ("心理學", [
        r"心理學(?!.*宗教)", r"精神分析", r"心理治療", r"認知科學", r"認知行為",
        r"佛洛伊德", r"佛洛依德", r"Freud", r"榮格", r"Jung", r"Adler", r"阿德勒",
        r"Frankl", r"弗蘭克爾", r"Yalom", r"亞隆", r"Skinner", r"Maslow",
        r"群眾心理", r"群体心理", r"創傷", r"PTSD", r"焦慮", r"憂鬱", r"depression",
        r"存在心理治療", r"完形治療", r"行為治療", r"家族治療",
    ]),
    # 自然科學 — 物理、化學、生物、地球科學、數學
    ("自然科學", [
        r"物理學", r"physics", r"量子", r"相對論", r"宇宙學", r"天文學", r"天文物理",
        r"化學(?!.*文化)", r"chemistry", r"分子", r"基因", r"DNA(?!.*文化)",
        r"生物學(?!.*人類)", r"biology", r"演化(?!.*社會|.*文化)", r"遺傳",
        r"地質學", r"地球科學", r"氣候(?!.*社會)",
        r"數學", r"mathematics", r"統計學", r"幾何", r"代數", r"微積分", r"拓樸",
        r"科學哲學", r"科學史(?!.*社會)", r"科學革命",
        r"愛因斯坦", r"Einstein", r"霍金", r"Hawking", r"費曼", r"Feynman", r"達爾文(?!.*社會)", r"Darwin(?!ism\s*and\s*society)",
    ]),
    # 人類生物學 — 人類學、生物人類學、演化、考古、體質、語言學
    ("人類生物學", [
        r"人類學", r"anthropology", r"民族誌", r"民族學",
        r"考古學", r"archaeology", r"舊石器", r"新石器", r"舊石器時代", r"史前",
        r"人類起源", r"人類演化", r"人類祖先", r"原始人", r"類人猿", r"靈長類",
        r"基因.*人類", r"語言學(?!.*哲學)", r"linguistics", r"語音學", r"句法",
        r"文化人類", r"體質人類", r"生物人類",
    ]),
    # 文學
    ("文學", [
        r"小說", r"novel", r"詩集", r"詩歌(?!.*聖)", r"散文集", r"文學評論",
        r"文學史", r"literature", r"莎士比亞", r"Shakespeare", r"杜思妥也夫斯基",
        r"托爾斯泰(?!.*基督|.*神學)", r"Tolstoy", r"Dostoevsky", r"卡夫卡", r"Kafka",
        r"加繆", r"Camus", r"歌德", r"Goethe", r"博爾赫斯", r"Borges",
        r"村上春樹", r"Murakami", r"米蘭昆德拉", r"Kundera",
    ]),
    # 歷史學 — 純地區／時代史，排除「思想史／政治史／教會史／人類進化史」等已歸他類
    ("歷史學", [
        r"^通史$", r"^斷代史$", r"^世界史$", r"全球史", r"世界文明史(?!.*人類)",
        r"古希臘(?!.*哲學|.*神話)", r"古羅馬(?!.*基督|.*哲學)", r"羅馬帝國", r"拜占庭(?!.*神學)",
        r"啟蒙運動(?!.*哲學)", r"工業革命", r"法國大革命", r"美國獨立",
        r"^中國史$", r"清史", r"明史", r"元史", r"宋史", r"唐史", r"漢史", r"魏晉",
        r"^日本史$", r"^朝鮮史$", r"^印度史$", r"波斯史", r"中亞史",
        r"^非洲史$", r"^美洲史$", r"^歐洲史$", r"二戰", r"一戰", r"冷戰", r"WWII", r"WWI",
        r"史學理論", r"史料原典",
    ]),
    # 社會政治學
    ("社會政治學", [
        r"政治學(?!.*哲學)", r"政治經濟", r"政治社會", r"國際關係", r"地緣政治",
        r"經濟學(?!.*哲學)", r"economics", r"資本主義", r"社會主義", r"共產主義",
        r"民主", r"民主化", r"威權主義", r"極權主義", r"自由主義",
        r"社會學(?!.*宗教)", r"sociology", r"階級", r"性別", r"女性主義(?!.*神學)",
        r"性學", r"婚姻(?!.*神學|.*基督|.*天主)",
        r"法律", r"法學", r"jurisprudence", r"憲法",
        r"知識社會學", r"科學社會學",
    ]),
]


def predict(title: str) -> tuple[str, str | None]:
    """Returns (predicted_category, matched_pattern). None if no match."""
    for cat, pats in RULES:
        for pat in pats:
            if re.search(pat, title, re.IGNORECASE):
                return (cat, pat)
    return (None, None)


def main():
    with open("scripts/_all_books_snapshot.json", "r", encoding="utf-8") as f:
        rows = json.load(f)

    # 過濾出疑似誤分（current != predicted，且 predicted 不是 None）
    proposals = defaultdict(list)
    for row in rows:
        cur = row["category"]
        pred, pat = predict(row["title"])
        if not pred or pred == cur:
            continue
        proposals[(cur, pred)].append((row, pat))

    print(f"Total books scanned: {len(rows)}")
    print(f"Suspect mismatches: {sum(len(v) for v in proposals.values())} 本")
    print()

    # 印出每個 (cur → pred) 群組
    for (cur, pred), items in sorted(proposals.items(), key=lambda x: -len(x[1])):
        print(f"=== {cur} → {pred} ({len(items)} 本) ===")
        for row, pat in items[:30]:
            print(f"  ↻ {row['title'][:75]} (sub={row.get('subcategory')}) [{pat}]")
        if len(items) > 30:
            print(f"  ... 還有 {len(items)-30} 本")
        print()

    if not APPLY:
        print()
        print("--- DRY RUN — 用 --apply 實跑 UPDATE DB + 移 Drive 檔案 ---")
        return

    # APPLY — fetch fresh file_paths
    moved, dbpatch, fail = 0, 0, 0
    for (cur, pred), items in proposals.items():
        for row, _ in items:
            # Refetch latest file_path
            r = requests.get(
                f"{SUPABASE_URL}/rest/v1/ebooks?id=eq.{row['id']}&select=file_path",
                headers=H,
            )
            fp = r.json()[0].get("file_path") if r.json() else None
            if not fp:
                continue
            old_path = Path(fp)
            new_path = DRIVE_ROOT / pred / old_path.name
            if old_path.exists() and old_path != new_path:
                try:
                    new_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(old_path), str(new_path))
                    moved += 1
                except Exception as e:
                    print(f"  ❌ move {row['title'][:50]}: {e}")
                    fail += 1
                    continue
            patch = requests.patch(
                f"{SUPABASE_URL}/rest/v1/ebooks?id=eq.{row['id']}",
                headers={**H, "Content-Type": "application/json"},
                json={"category": pred, "file_path": str(new_path)},
            )
            if patch.status_code in (200, 204):
                dbpatch += 1
            else:
                print(f"  ❌ DB patch {row['title'][:50]}: {patch.status_code}")
                fail += 1

    print(f"\n=== Done: moved={moved}, db-patched={dbpatch}, fail={fail} ===")


if __name__ == "__main__":
    main()
