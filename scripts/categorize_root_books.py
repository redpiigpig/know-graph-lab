#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classify the 181 root-level ebooks into main categories using keyword rules.

Usage:
  python scripts/categorize_root_books.py dryrun    # show classification
  python scripts/categorize_root_books.py apply     # move files + update DB
"""
import json
import os
import re
import shutil
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    os.system("pip install requests -q")
    import requests

DRIVE_ROOT = Path('G:/我的雲端硬碟/資料/電子書')

# Order matters — first match wins. More specific patterns first.
# Each rule: (regex, category)
RULES = [
    # 自然科學 (specific science topics, before more general categories that may match)
    (r'空間簡史|物理學|數學|鍊金術|化學|天文|科學作為天職|科學的價值|科學的反革命|地球上最偉大的表演|生命3\.0|宇宙|相對論|量子', '自然科學'),

    # 人類生物學 (biology/anthropology specific)
    (r'道金斯|自私的基因|道德動物|大歷史|人類|薩滿|原始活態文化|理性與本能|大尺度|被人類改變和改變人類的10萬年|大躍進|人類起源|生物進化', '人類生物學'),

    # 心理學
    (r'精神分析|心理學|意識|大腦|齊澤克|認知|榮格|弗洛伊德', '心理學'),

    # 世界宗教 — specific religion keywords
    (r'佛教|佛經|佛性|佛王|佛學|佛像|禪|藏族宗教|蔣維喬|印度宗教|印度教|博伽梵歌|摩訶婆羅多|道家|道教|基督教|基督徒|耶穌|主教|教宗|聖約|聖經|聖典|教父|教義|福音|默觀|神學|新教|猶太|塔木德|希伯來|伊斯蘭|穆斯林|可蘭|蘇菲|巴哈伊|印度哲學|藏傳|靜觀|神鬼祖先|神諭|宗教思想|宗教哲學|宗教學|追尋一己之福|追求靈性|阿維斯塔|瑣羅亞斯德|祆教', '世界宗教'),

    # 宗教學 (study OF religion, broader)
    (r'神話學|宗教史|神話|宗教社會學|宗教研究|宗教比較|神諭|世界宗教史|赫耳墨斯|秘籍', '宗教學'),

    # 文學
    (r'文學|小說|詩|散文|戲劇|全集$|卡謬|韓松|楊絳|三毛|斐多|神性的溫柔|查拉圖斯特拉如是說|柏拉圖對話|泰戈爾|赫塞|卡夫卡|湯姆歷險|神話傳說|莎士比亞|流浪者之歌', '文學'),

    # 哲學 (broad — various philosophers)
    (r'哲學|思想|形上|本體|存在主義|現象學|倫理|康德|黑格爾|尼采|海德格|胡塞爾|維特根斯坦|笛卡爾|柏拉圖|亞里士多德|蘇格拉底|斯多亞|伊比鳩魯|伊壁鳩魯|馬基維利|霍布斯|休謨|羅素|福柯|傅柯|阿倫特|阿甘本|列維-斯特勞斯|薩特|沙特|齊澤克|批判|理性|認識論|邏輯|莊子|王陽明|新儒家|儒家|儒學|新政治科學', '哲學'),

    # 社會政治學
    (r'政治|社會學|社會科學|社會主義|資本主義|資本論|新自由主義|意識型態|國家|帝國主義|民主|極權|主義|福利|貧富|階級|韋伯|涂爾幹|塗爾幹|馬克思|福山|國家理論|憲法|法哲學|懲罰|犯罪|觀念|穿透|現代性|現代社會|沃格林|不被統治|開放社會|齊澤克|阿倫特', '社會政治學'),

    # 歷史學 — country/region/general history (catch-all for 史 keyword)
    (r'史$|史 |史，|史$|史·|史:|歷史|帝國|王朝|戰爭|革命|編年|文明史|世界史|古代|中世紀|中古|近代|現代|当代|當代|二十世紀|20世紀|十九世紀|遊牧|蒙古|游牧|歐洲|拜占庭|羅馬|希臘|波斯|埃及|巴比倫|印度史|中國|日本|韓國|泰國|柬埔寨|越南|新加坡|斯里蘭卡|錫蘭|瑞士|葡萄牙|西班牙|奧地利|意大利|義大利|俄羅斯|俄國|蘇聯|捷克|斯洛伐克|南斯拉夫|新西蘭|紐西蘭|埃塞俄比亞|塞俄比亞|英國|法國|德國|奧斯曼|十字軍|諾曼|維京|諾曼征服|中亞|西亞|東亞|南亞|拉丁美洲|加勒比|海洋|大歷史|世界文明|敦煌|王明珂|余英時|史景遷|商務印書館漢譯歷史|劍橋插圖|牛津|企鵝|花卉|貿易|金融|外交|軍事|戰役|大決戰|藝術|繪畫|考古|甲骨|金石|出土|畫像|墓葬|文化史|思想史|草原帝國|海權|海洋帝國|閩南|台灣|台海|香港|西藏|新疆|蒙古|韓松', '歷史學'),
]


# Manual overrides for tricky books
MANUAL_OVERRIDES = {
    '儒學復興與神話重述，儒學復興與神話重述.pdf': '宗教學',
    '從_佛般泥洹經_線索探討漢譯佛經中轉輪王觀念.pdf': '世界宗教',
    '教會拉丁文(一) 暑密A_課堂講義_1-2_修1.pdf': '世界宗教',
    '商務印書館，商務印書館漢譯歷史套裝（24冊）.epub': '歷史學',
    '理想國譯叢系列 套裝32冊（MIRROR系列）.epub': '社會政治學',
    '理想譯叢045 滔天洪水.epub': '社會政治學',
    '李猛 【德】馬克斯·韋伯，科學作為天職.azw3': '社會政治學',  # 韋伯 sociology
    '李映洲  主編，敦煌壁畫藝術論.pdf': '歷史學',
    '神諭與預言在古希臘社會中的地位及作用，神諭與預言在古希臘社會中的地位及作用.pdf': '宗教學',
    '新版宗教史叢書（4卷本）.pdf': '宗教學',
    '饒宗頤二十世紀學術文集 卷5 宗教學_12430091，饒宗頤二十世紀學術文集 卷5 宗教學_12430091.pdf': '宗教學',
    '楊絳，斐多.epub': '文學',
    '李安宅，藏族宗教史之實地研究.pdf': '世界宗教',
    '焦大衛，神·鬼·祖先 一個臺灣鄉村的民間信仰.pdf': '世界宗教',
    '蒲慕州，追尋一己之福 中國古代的信仰世界.pdf': '世界宗教',
    '吳根友，道家思想及其現代詮釋.epub': '世界宗教',
    'admin，顧頡剛的疑古思想漢儒、孔子與經典.pdf': '哲學',
    '韓松，韓松作品.azw3': '文學',
    '張光直，美術、神話與祭祀.pdf': '宗教學',
    '泰戈爾，神性的溫柔.epub': '文學',
    '伊利亞德，神聖的存在 比較宗教的範型.pdf': '宗教學',
    '【英】唐·庫比特，神學的奇異迴歸.epub': '世界宗教',
    'Carlo Maria Martini，楊成斌，從靜觀到基督徒的美德（上冊）.pdf': '世界宗教',
    'Carlo Maria Martini，楊成斌，從靜觀到基督徒的美德（下冊）.pdf': '世界宗教',
    '塔木德智慧全書.mobi': '世界宗教',
    '甘懷真，皇權、禮儀與經典詮釋 中國古代政治史研究.pdf': '社會政治學',
    '王明珂，遊牧者的抉擇.epub': '歷史學',
    '王明珂，遊牧者的抉擇：面對漢帝國的北亞遊牧部族.epub': '歷史學',
    '王明珂，羌在漢藏之間  川西羌族的歷史人類學研究.pdf': '人類生物學',
    '王明珂，華夏邊緣--歷史記憶與族群認同.pdf': '歷史學',
    '李碩，翦商  殷周之變與華夏新生.epub': '歷史學',
    '蔣維喬，蔣維喬中國佛教史.pdf': '世界宗教',
    '古正美，從天王傳統到佛王傳統.pdf': '世界宗教',
    '夏金華，緣起佛性成佛.pdf': '世界宗教',
    '霍韜晦，絕對與圓融 佛教思想論集 (2nd ed).pdf': '世界宗教',
    '陳迎年，感應與心物 牟宗三哲學批判.pdf': '哲學',
    '海德格爾 奧特劉小楓，海德格爾與神學.pdf': '世界宗教',
    '朱利安・鮑爾迪，黑色上帝 猶太教、基督教和伊斯蘭教的起源.pdf': '世界宗教',
    '羅曉穎，吳小鋒等編譯，菜園哲人伊壁鳩魯.pdf': '哲學',
    '威廉．伯恩斯坦，貿易大歷史.epub': '歷史學',
    '《物理學之道》的根據F.卡普拉.pdf': '自然科學',
    '阿爾貝‧卡謬，卡謬全集（6卷）.epub': '文學',
    # Additional uncategorized cleanups
    '[英] 亞當·圖茲，理想譯叢045 滔天洪水.epub': '社會政治學',
    '[英] 奧蘭多·費吉斯，娜塔莎之舞.mobi': '歷史學',
    '剑桥插图中国史（The Cambridge Illustrated History of China） by author 伊佩霞（Patricia Buckley Ebrey）, translator赵世瑜     赵世玲      张红艳 (z-lib.org).pdf': '歷史學',
    '劉小楓，經典與解釋的張力.pdf': '哲學',
    '古育安，戰國時代的古史記憶──虞夏之際篇.pdf': '歷史學',
    '孫向晨，面對他者.pdf': '哲學',
    '安東尼·艾福瑞特，雅典的勝利.epub': '歷史學',
    '寺田隆信，鄭和.pdf': '歷史學',
    '德国观念论与惩罚的概念 by [德]梅尔 J.-C. Merle 考明凯维奇(英译) 梅尔(英译) 布朗(英译) 邱帅萍(中译) (z-lib.org).pdf': '哲學',
    '曹新宇 編，新史學（第十卷） 激辯儒教.pdf': '歷史學',
    '瑪喬麗·謝弗，胡椒的全球史.epub': '歷史學',
    '約翰·高德特，法老的寶藏.epub': '歷史學',
    '納斯鮑姆，善的脆弱性.pdf': '哲學',
    '詹姆斯·希恩，暴力的衰落.azw3': '歷史學',
    '譯文紀實，彼得·沃森（Peter Watson） [Watson）, 彼得·沃森（Peter]，虛無時代.epub': '歷史學',
    '賈雷德·戴蒙德(Jared Diamond)，崩潰社會如何選擇成敗興亡 (世紀人文系列叢書·開放人文).epub': '歷史學',
    '馬丁·湯姆·迪克 延斯·巴爾策，德勒茲歸來 不可思議的俄耳甫斯之新歷險.pdf': '哲學',
    '魯思·本尼迪克特，菊與刀(增訂版) (漢譯世界學術名著叢書).azw3': '人類生物學',
    # User-confirmed adjustments
    'Ma, Yue Foucault, Michel Fu, Ke Xie, Qiang，知識考古學 Zhi shi kao gu xue.pdf': '哲學',
    'admin，顧頡剛的疑古思想漢儒、孔子與經典.pdf': '歷史學',
    '劉易斯·A·科瑟，社會學思想名家  歷史背景和社會背景下的思想.pdf': '社會政治學',
}


def classify(filename):
    if filename in MANUAL_OVERRIDES:
        return MANUAL_OVERRIDES[filename]
    for pattern, category in RULES:
        if re.search(pattern, filename):
            return category
    return None  # uncategorized


def load_env():
    env = {}
    with open('.env', 'r', encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'): continue
            if '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env


def get_root_files():
    """Return list of (filename, full_path) for root-level ebooks."""
    files = []
    for f in DRIVE_ROOT.iterdir():
        if f.is_file() and f.suffix.lower() in {'.pdf', '.epub', '.mobi', '.azw3', '.azw'}:
            files.append(f)
    return sorted(files)


def cmd_dryrun():
    files = get_root_files()
    print(f"Total root-level books: {len(files)}\n")

    by_cat = {}
    uncategorized = []
    for f in files:
        cat = classify(f.name)
        if cat:
            by_cat.setdefault(cat, []).append(f.name)
        else:
            uncategorized.append(f.name)

    with open('_classification.txt', 'w', encoding='utf-8') as out:
        for cat, items in sorted(by_cat.items(), key=lambda x: -len(x[1])):
            out.write(f"\n=== {cat} ({len(items)}) ===\n")
            for n in items:
                out.write(f"  {n}\n")
        if uncategorized:
            out.write(f"\n=== UNCATEGORIZED ({len(uncategorized)}) ===\n")
            for n in uncategorized:
                out.write(f"  {n}\n")

    # Summary to stderr
    for cat, items in sorted(by_cat.items(), key=lambda x: -len(x[1])):
        print(f"  {cat}: {len(items)}", file=sys.stderr)
    if uncategorized:
        print(f"  UNCATEGORIZED: {len(uncategorized)}", file=sys.stderr)

    print(f"\nFull list: _classification.txt", file=sys.stderr)


def cmd_apply():
    env = load_env()
    URL = env['SUPABASE_URL']
    KEY = env['SUPABASE_SERVICE_ROLE_KEY']
    H = {'apikey': KEY, 'Authorization': f'Bearer {KEY}', 'Content-Type': 'application/json'}

    files = get_root_files()
    moved = 0
    skipped = 0
    failed = 0
    for f in files:
        cat = classify(f.name)
        if not cat:
            print(f"  SKIP (uncategorized): {f.name}", file=sys.stderr)
            skipped += 1
            continue
        target_dir = DRIVE_ROOT / cat
        target_dir.mkdir(exist_ok=True)
        target = target_dir / f.name
        if target.exists():
            print(f"  SKIP (target exists): {f.name}", file=sys.stderr)
            skipped += 1
            continue
        try:
            shutil.move(str(f), str(target))
            # Update DB
            old_path = str(f).replace('/', '\\')  # match Windows-style stored path
            new_path = str(target).replace('/', '\\')
            r = requests.patch(
                f"{URL}/rest/v1/ebooks?file_path=eq.{old_path}",
                headers=H,
                json={'file_path': new_path, 'category': cat, 'subcategory': None},
                timeout=30
            )
            if r.status_code not in (200, 204):
                print(f"  WARN: DB update failed for {f.name}: HTTP {r.status_code}", file=sys.stderr)
            moved += 1
            if moved % 20 == 0:
                print(f"  moved {moved}...", file=sys.stderr)
        except Exception as e:
            print(f"  FAIL: {f.name}: {e}", file=sys.stderr)
            failed += 1

    print(f"\nMoved: {moved}", file=sys.stderr)
    print(f"Skipped: {skipped}", file=sys.stderr)
    print(f"Failed: {failed}", file=sys.stderr)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'dryrun'
    if cmd == 'dryrun':
        cmd_dryrun()
    elif cmd == 'apply':
        cmd_apply()
    else:
        print(__doc__, file=sys.stderr)
        sys.exit(1)
