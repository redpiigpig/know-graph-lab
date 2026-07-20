"""重新分類「宗教學」中的 129 本書 — 用 title-regex 判斷每本應走 神學/世界宗教/宗教學。

執行：
  python scripts/_reclassify_religion_books.py            # 印提案
  python scripts/_reclassify_religion_books.py --apply    # 實跑：UPDATE DB + 移 Drive 檔案

規則：
- 教父／系統神學／基督教專題 → 神學
- 單一非基督教宗教 → 世界宗教/{宗教}
- 跨宗教比較／神話學／宗教社會學／宗教現象學／宗教心理／宗教哲學 → 保留 宗教學
- 模糊或人名專書 → 標 NEEDS_REVIEW 給人工看
"""
import os
import re
import shutil
import sys
from pathlib import Path
from collections import defaultdict

from dotenv import load_dotenv
load_dotenv()
import requests

sys.stdout.reconfigure(encoding="utf-8")

APPLY = "--apply" in sys.argv

SUPABASE_URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
DRIVE_ROOT = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\電子圖書館")

# Patterns — 順序很重要：先抓 神學 (基督教專題)，再抓單一非基督宗教，最後 fallback
CHRISTIAN_THEOLOGY_PATTERNS = [
    r"基督教史", r"基督教思想", r"基督教神學", r"基督教倫理", r"基督教教育",
    r"基督教文化", r"基督論", r"教父", r"教會史", r"教會歷史", r"教會教義",
    r"神學", r"信理", r"三一", r"福音", r"信仰", r"護教",
    r"奧古斯丁", r"阿奎那", r"Aquinas", r"Augustine", r"Anselm", r"安瑟", r"安波羅修",
    r"屈梭多模", r"金口若望", r"Chrysostom", r"亞他那修", r"Athanasius",
    r"巴特", r"Barth", r"Bonhoeffer", r"朋霍費爾", r"Rahner", r"拉內", r"拉納",
    r"Moltmann", r"莫爾特曼", r"Kierkegaard", r"克爾凱郭爾", r"Pelikan", r"帕利坎",
    r"Niebuhr", r"Wright", r"Pannenberg", r"Hauerwas", r"麥格拉思", r"McGrath",
    r"漢斯昆", r"Hans Küng", r"Kasper", r"卡斯培", r"Lessing", r"萊辛",
    r"Cyril of Alexandria", r"加利略", r"Nestorius", r"聶斯托留", r"Monophysite", r"一性論",
    r"Chalcedon", r"迦克墩", r"基督教傳統", r"Christian Tradition", r"Christian tradition",
    r"Babai", r"Ephrem", r"以法蓮", r"Sarug", r"Syriac", r"敘利亞", r"亞蘭",
    r"Heracleides", r"赫拉克利德", r"Council of", r"大公會議",
    r"上帝", r"天主", r"基督", r"耶穌", r"聖經", r"聖事", r"禮儀", r"教宗",
    r"靈修", r"神祕主義", r"修道", r"靈魂", r"懺悔", r"贖罪", r"成義", r"得救",
    r"Christ\s*in", r"NPNF", r"ANF", r"Schaff", r"教父集",
]

# 單一宗教 patterns (排除基督教 — 那些走 神學)
NON_CHRISTIAN_RELIGION_PATTERNS = {
    "佛教": [r"佛教", r"佛學", r"Buddhis", r"Zen", r"禪", r"密宗", r"藏傳", r"金剛經", r"法華", r"華嚴", r"淨土", r"觀音", r"菩薩"],
    "伊斯蘭教": [r"伊斯蘭", r"伊斯兰", r"穆斯林", r"Islam", r"Muslim", r"可蘭", r"古蘭", r"Qur"],
    "東亞宗教": [r"道教", r"道家", r"儒教", r"儒家", r"Taoism", r"Confucian", r"中國宗教", r"中國的靈魂"],
    "印度教": [r"印度教", r"Hindu", r"奧義書", r"吠陀", r"婆羅門", r"濕婆"],
    "猶太教": [r"猶太", r"Jewish", r"Judaism", r"Torah", r"Talmud", r"卡巴拉", r"Kabbalah"],
    "波斯宗教": [r"瑣羅亞斯德", r"祆教", r"Zoroastr", r"Avesta", r"阿維斯塔"],
    "巴哈伊": [r"巴哈伊", r"Baha"],
}

# 強跨宗教 / 宗教學專業詞（保留在 宗教學）
RELIGIOUS_STUDIES_PATTERNS = [
    r"宗教學", r"宗教社會學", r"宗教比較", r"比較宗教", r"宗教現象", r"宗教心理",
    r"宗教哲學", r"宗教對話", r"宗教交談", r"宗教史(?!.*基督|.*佛|.*伊斯|.*猶|.*印度|.*道)",
    r"神聖", r"神話學", r"神話與", r"古典神話", r"神話\s*與", r"神話", r"神祇",
    r"金枝", r"Frazer", r"Eliade", r"伊利亞德", r"Durkheim", r"涂爾幹", r"涂尔干",
    r"James.*宗教", r"宗教經驗", r"宗教生活", r"宗教本質", r"沒有上帝的宗教",
    r"宇宙與歷史", r"神聖的存在", r"神聖的帷幕", r"天使的傳言", r"Berger",
    r"信仰的彩虹", r"宗教\s*與.*文化", r"宗教\s*與.*社會", r"World Religions",
    r"萬有", r"靈異", r"巫術", r"獻祭", r"祭祀(?!.*基督)", r"五大宗教",
    r"性與宗教", r"死亡.*戰爭", r"自己的上帝", r"當代宗教",
]


CROSS_RELIGION_PATTERNS = [
    # 多宗教比較／對話／跨宗教史 — 優先級最高，避免被「聖經/福音/基督」單字綁架
    r"對話", r"交談", r"比較", r"Dialogue", r"Encounter", r"Interfaith", r"Inter-faith",
    r"Common\s*Word", r"Common Ground",
    # 多宗教並列題目：A,B,C 三個宗教都在標題裡
    r"(?:Christian|Christianity).*(?:Islam|Muslim|Jewish|Judaism|Buddhis|Hindu|Zoroastr)",
    r"(?:Islam|Muslim).*(?:Christian|Christianity|Jewish|Judaism|Buddhis|Hindu|Zoroastr)",
    r"(?:Jewish|Judaism).*(?:Christian|Christianity|Islam|Muslim|Buddhis|Hindu|Zoroastr)",
    r"基督.*伊斯", r"基督.*佛", r"基督.*猶太", r"儒.*基督", r"儒.*耶",
    r"聖經.*古蘭", r"古蘭.*聖經",
    r"Christian.*Zoroastrian", r"A state of mixture",
    # 個人化／淡神論／跨傳統的「上帝/信仰」哲學
    r"沒有上帝的宗教", r"自己的上帝", r"信仰的彩虹",
    # 北歐神話「福音」名字
    r"洛基.*福音", r"Loki",
]


def classify(title: str, current_sub: str | None) -> tuple[str, str | None, str]:
    """Returns (new_category, new_subcategory, reason)."""
    t = title

    # -1. Subcategory-based override — current_sub 已是明確 Christian-specific
    if current_sub == "教會史":
        return ("神學", "教會史", "subcategory promotion: 教會史")

    # -0.5. 「中國/東亞/亞洲 + 靈魂/信仰/宗教」→ 世界宗教/東亞宗教，不要被 christian theology 抓走
    if re.search(r"中國|東亞|亞洲|日本|韓國|越南", t) and re.search(r"靈魂|信仰|宗教|神靈|民間", t):
        return ("世界宗教", "東亞宗教", "matched: East Asia religion phrase")

    # 0. Cross-religion (highest priority — 跨宗教研究 / 對話 / 多宗教比較)
    for pat in CROSS_RELIGION_PATTERNS:
        if re.search(pat, t, re.IGNORECASE):
            return ("宗教學", current_sub if current_sub != "None" else "宗教對話", f"matched cross-religion: {pat}")

    # 1. Christian-specific theology (must not get caught by 宗教史 below)
    for pat in CHRISTIAN_THEOLOGY_PATTERNS:
        m = re.search(pat, t, re.IGNORECASE)
        if m:
            # 用既有 sub 如 "教會史" "Schaff -..." 維持
            sub = current_sub if current_sub and current_sub not in ("None", "宗教史") else None
            # 推斷 subcategory
            if not sub:
                if re.search(r"教父|patristic", t, re.IGNORECASE): sub = "教父學"
                elif re.search(r"教會史|教會歷史", t): sub = "教會史"
                elif re.search(r"系統神學|信理|大全|綱要|教義學", t): sub = "系統神學"
                elif re.search(r"基督論|三一|聖靈論|末世論|聖事|禮儀|教會論", t): sub = "神學專題"
                elif re.search(r"靈修|神祕|修道|沙漠", t): sub = "靈修神學"
                elif re.search(r"Bonhoeffer|Barth|Rahner|Moltmann|奧古斯丁|Aquinas|Augustine", t, re.IGNORECASE): sub = "神學家研究"
                elif re.search(r"Cyril|Athanasius|Chrysostom|Ephrem|Babai|Nestorius|Sarug|Heracleides|教父", t, re.IGNORECASE): sub = "教父研究"
                else: sub = "神學"
            return ("神學", sub, f"matched: {pat}")

    # 2. Single non-Christian religion
    for religion, pats in NON_CHRISTIAN_RELIGION_PATTERNS.items():
        for pat in pats:
            if re.search(pat, t, re.IGNORECASE):
                return ("世界宗教", religion, f"matched: {pat}")

    # 3. Cross-religion / 宗教學
    for pat in RELIGIOUS_STUDIES_PATTERNS:
        if re.search(pat, t, re.IGNORECASE):
            return ("宗教學", current_sub if current_sub != "None" else None, f"matched: {pat}")

    # 4. Fallback — NEEDS_REVIEW
    return ("宗教學", current_sub, "NEEDS_REVIEW (no pattern matched)")


def main():
    # Get ALL 宗教學 books — use range pagination to avoid 1000 cap
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/ebooks?select=id,title,file_path,category,subcategory&category=eq.宗教學",
        headers={**H, "Range": "0-999"},
    )
    rows = r.json()
    print(f"Total 宗教學 books: {len(rows)}")
    print()

    by_dest = defaultdict(list)
    for row in rows:
        new_cat, new_sub, reason = classify(row["title"], row["subcategory"])
        key = f"{new_cat}/{new_sub or '(None)'}"
        by_dest[key].append((row, new_cat, new_sub, reason))

    # Output proposal grouped
    for key in sorted(by_dest.keys()):
        books = by_dest[key]
        # 只標示變動的
        changed = [b for b in books if b[1] != b[0]["category"] or b[2] != b[0]["subcategory"]]
        no_change = [b for b in books if b not in changed]
        print(f"=== → {key} ({len(books)} 本，{len(changed)} 變動) ===")
        for row, _, _, reason in changed:
            print(f"  ↻ {row['title'][:80]} (from {row.get('subcategory') or 'None'})  [{reason}]")
        if no_change:
            print(f"  ({len(no_change)} 本保持原樣 — 略)")
        print()

    if not APPLY:
        print()
        print("--- DRY RUN — 用 --apply 實跑 UPDATE DB + 移 Drive 檔案 ---")
        return

    # APPLY
    moved, dbpatch, fail = 0, 0, 0
    for row in rows:
        new_cat, new_sub, _ = classify(row["title"], row["subcategory"])
        if new_cat == row["category"] and new_sub == row["subcategory"]:
            continue
        old_path = Path(row["file_path"])
        # 新路徑：DRIVE_ROOT / new_cat / [new_sub if it's a folder-style sub like Schaff -...] / filename
        # 大多 subcategory 是邏輯標籤而非實體子資料夾。只有 Schaff/系列 才有子資料夾。
        # 為穩妥起見，這次只動 category；subcategory 在 DB 改即可。
        new_path = DRIVE_ROOT / new_cat / old_path.name
        if old_path.exists() and old_path != new_path:
            try:
                new_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(old_path), str(new_path))
                moved += 1
            except Exception as e:
                print(f"  ❌ move {row['title'][:50]}: {e}")
                fail += 1
                continue
        # UPDATE DB
        patch = requests.patch(
            f"{SUPABASE_URL}/rest/v1/ebooks?id=eq.{row['id']}",
            headers={**H, "Content-Type": "application/json"},
            json={"category": new_cat, "subcategory": new_sub, "file_path": str(new_path)},
        )
        if patch.status_code in (200, 204):
            dbpatch += 1
        else:
            print(f"  ❌ DB patch {row['title'][:50]}: {patch.status_code}")
            fail += 1

    print(f"\n=== Done: moved={moved}, db-patched={dbpatch}, fail={fail} ===")


if __name__ == "__main__":
    main()
