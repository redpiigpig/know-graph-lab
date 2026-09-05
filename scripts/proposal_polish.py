# -*- coding: utf-8 -*-
"""計畫書的稱謂統一、時程壓成三年、去掉條列符號。

稱謂規則（使用者定的）：
  太虛 → 太虛大師；印順 → 印順導師；其餘僧人一律「某某法師」。
  黃彰輝、宋泉盛 → 需要時寫「博士」；王憲治、黃伯和 → 需要時寫「牧師」。

🚨 僧人是**每一次都要**（使用者原話：「所有法師都要寫某某法師，不可以直接寫太虛、印順」），
   含系譜列舉；在家學者的「博士／牧師」才是「需要時」，只補前幾次免得整篇被稱謂淹沒。
🚨 書名與徵引書目一律不動——
   《太虛大師全書》再加一次會變成《太虛大師大師全書》，
   而書目的「釋太虛」「釋印順」是著者形式，本來就不加稱謂。

  python -X utf8 scripts/proposal_polish.py
"""
import re
from pathlib import Path

SRC = Path("G:/我的雲端硬碟/玄奘/博一上/獎學金/玄奘助學金/"
           "張辰瑋，博士論文計畫書（原始markdown）_國史館體例.md")

# 已經帶了稱謂、或屬於書名／專名的一律跳過
# 排除已帶稱謂，以及「印順學派」「太虛時代」「弘誓文教」這類專名
SUFFIX = r"(?!大師|導師|法師|牧師|博士|學派|學報|時代|學|之|文教)"
PREFIX = r"(?<!釋)(?<!《)"
MONASTIC = {"太虛": "大師", "印順": "導師", "傳道": "法師", "昭慧": "法師",
            "性廣": "法師", "聖嚴": "法師", "煮雲": "法師"}
LAY = {"黃彰輝": "博士", "宋泉盛": "博士", "王憲治": "牧師", "黃伯和": "牧師"}
TITLES = {**MONASTIC, **LAY}

# 三年時程（原為四年）
OLD_SCHEDULE = """本研究預定以四年完成，各年度工作重點如下。"""
NEW_SCHEDULE = """本研究預定以三年完成，各年度工作重點如下。"""
OLD_Y3 = ("**第三年（2028年8月–2029年7月）**：完成第五章的比較分析與第六章的"
          "「人間宗教」範式；補訪缺口，並就第五、六章各發表一篇學術論文。")
OLD_Y4 = ("**第四年（2029年8月–2030年7月）**：完成第七章結論，全稿統整修訂，"
          "通過學位考試。")
NEW_Y3 = ("**第三年（2028年8月–2029年7月）**：完成第五章的比較分析、第六章的"
          "「人間宗教」範式與第七章結論；補訪缺口，就第五、六章各發表一篇學術論文，"
          "全稿統整修訂後通過學位考試。")


def add_titles(text, lay_limit=6):
    """僧人全補；在家學者只補前 lay_limit 次。"""
    for name, suf in TITLES.items():
        pat = re.compile(PREFIX + re.escape(name) + SUFFIX)
        if name in MONASTIC:
            text = pat.sub(name + suf, text)
            continue
        n = 0

        def sub(m):
            nonlocal n
            n += 1
            return name + suf if n <= lay_limit else name
        text = pat.sub(sub, text)
    return text


def main():
    s = SRC.read_text(encoding="utf-8")
    head, sep, biblio = s.partition("## 徵引書目")
    assert sep, "找不到徵引書目，體例可能已經改過"

    before = {k: head.count(k) for k in TITLES}
    head = add_titles(head)

    # 這支要能重跑：時程若已改過就跳過，不要 assert 掉整輪
    if OLD_SCHEDULE in head:
        head = (head.replace(OLD_SCHEDULE, NEW_SCHEDULE)
                    .replace(OLD_Y3, NEW_Y3).replace(OLD_Y4 + "\n\n", ""))
        print("  時程：四年 → 三年")

    # 條列符號拿掉，改成句子（參考格式全篇沒有項目符號）
    head = re.sub(r"^- (.+)$", r"\1", head, flags=re.M)

    # 這是研究計畫不是論文，不用目錄；連同「無圖表」那一行一起拿掉
    head = re.sub(r"## 目錄\n(?:.*\n)*?(?=---\n)", "", head, count=1)

    SRC.write_text(head + sep + biblio, encoding="utf-8")
    for k, v in TITLES.items():
        got = head.count(k + v)
        print(f"  {k}{v}：{got} 處（原文出現 {before[k]} 次）")


if __name__ == "__main__":
    main()
