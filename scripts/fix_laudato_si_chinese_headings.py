"""
Replace the malformed Chinese section headings in
data/encyclicals/21c-francis/laudato-si-2015-chinese.txt with hand-written
translations matching the English structure exactly.

Strategy:
  1. Scan English .txt to learn (heading_text, next_paragraph_num) pairs.
  2. Look up each English heading in HEADING_ZH table.
  3. Strip all existing `## ` lines from Chinese .txt (except `## Footnotes`).
  4. Re-insert `## {zh}` right before the matching `N. ` paragraph in Chinese.

Run from project root:
  python scripts/fix_laudato_si_chinese_headings.py
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EN_PATH = ROOT / "data" / "encyclicals" / "21c-francis" / "laudato-si-2015-english.txt"
ZH_PATH = ROOT / "data" / "encyclicals" / "21c-francis" / "laudato-si-2015-chinese.txt"

# 英文標題 → 中譯（依台灣主教團《願祢受讚頌》譯本章節結構）
HEADING_ZH: dict[str, str] = {
    # 第一章
    "WHAT IS HAPPENING TO OUR COMMON HOME": "第一章 我們共同家園的境況",
    "I. POLLUTION AND CLIMATE CHANGE": "一、污染與氣候變化",
    "II. THE ISSUE OF WATER": "二、水的問題",
    "III. LOSS OF BIODIVERSITY": "三、生物多樣性的消失",
    "IV. DECLINE IN THE QUALITY OF HUMAN LIFE AND THE BREAKDOWN OF SOCIETY": "四、人類生活品質的下降與社會的分崩離析",
    "V. GLOBAL INEQUALITY": "五、全球的不平等",
    "VI. WEAK RESPONSES": "六、微弱的回應",
    "VII. A VARIETY OF OPINIONS": "七、不同意見的多元",
    # 第二章
    "THE GOSPEL OF CREATION": "第二章 創造的福音",
    "I. THE LIGHT OFFERED BY FAITH": "一、信仰提供的光明",
    "II. THE WISDOM OF THE BIBLICAL ACCOUNTS": "二、聖經記載的智慧",
    "III. THE MYSTERY OF THE UNIVERSE": "三、宇宙的奧秘",
    "IV. THE MESSAGE OF EACH CREATURE IN THE HARMONY OF CREATION": "四、在創造的和諧中每個受造物的訊息",
    "V. A UNIVERSAL COMMUNION": "五、普世共融",
    "VI. THE COMMON DESTINATION OF GOODS": "六、財物的共同歸屬",
    "VII. THE GAZE OF JESUS": "七、耶穌的凝視",
    # 第三章
    "THE HUMAN ROOTS OF THE ECOLOGICAL CRISIS": "第三章 生態危機的人性根源",
    "I. TECHNOLOGY: CREATIVITY AND POWER": "一、科技：創造力與權力",
    "II. THE GLOBALIZATION OF THE TECHNOCRATIC PARADIGM": "二、科技至上主義典範的全球化",
    "III. THE CRISIS AND EFFECTS OF MODERN ANTHROPOCENTRISM": "三、現代人類中心主義的危機與影響",
    # 第四章
    "INTEGRAL ECOLOGY": "第四章 整體生態學",
    "I. ENVIRONMENTAL, ECONOMIC AND SOCIAL ECOLOGY": "一、環境、經濟與社會生態學",
    "II. CULTURAL ECOLOGY": "二、文化生態學",
    "III. ECOLOGY OF DAILY LIFE": "三、日常生活的生態學",
    "IV. THE PRINCIPLE OF THE COMMON GOOD": "四、共同善的原則",
    "V. JUSTICE BETWEEN THE GENERATIONS": "五、世代之間的正義",
    # 第五章
    "LINES OF APPROACH AND ACTION": "第五章 對話與行動方針",
    "I. DIALOGUE ON THE ENVIRONMENT IN THE INTERNATIONAL COMMUNITY": "一、國際社群中對環境議題的對話",
    "II. DIALOGUE FOR NEW NATIONAL AND LOCAL POLICIES": "二、新的國家與地方政策的對話",
    "III. DIALOGUE AND TRANSPARENCY IN DECISION-MAKING": "三、對話與決策的透明度",
    "IV. POLITICS AND ECONOMY IN DIALOGUE FOR HUMAN FULFILMENT": "四、為人類成全進行政治與經濟的對話",
    "V. RELIGIONS IN DIALOGUE WITH SCIENCE": "五、宗教與科學的對話",
    # 第六章
    "ECOLOGICAL EDUCATION AND SPIRITUALITY": "第六章 生態教育與靈修",
    "I. TOWARDS A NEW LIFESTYLE": "一、邁向新的生活方式",
    "II. EDUCATING FOR THE COVENANT BETWEEN HUMANITY AND THE ENVIRONMENT": "二、為人類與環境之約教育",
    "III. ECOLOGICAL CONVERSION": "三、生態皈依",
    "IV. JOY AND PEACE": "四、喜樂與平安",
    "V. CIVIC AND POLITICAL LOVE": "五、公民與政治的愛",
    "VI. SACRAMENTAL SIGNS AND THE CELEBRATION OF REST": "六、聖事標記與安息日慶祝",
    "VII. THE TRINITY AND THE RELATIONSHIP BETWEEN CREATURES": "七、聖三與受造物之間的關係",
    "VIII. QUEEN OF ALL CREATION": "八、萬物之后",
    "IX. BEYOND THE SUN": "九、超越太陽",
    # Footer
    "Footnotes": "註腳",
}


def scan_english_anchors() -> list[tuple[str, str]]:
    """Return [(en_heading, next_para_num)] in document order."""
    text = EN_PATH.read_text(encoding="utf-8")
    blocks = re.split(r"\n{2,}", text)
    anchors: list[tuple[str, str]] = []
    pending_heading: str | None = None
    for raw in blocks:
        block = raw.strip()
        if block.startswith("## "):
            pending_heading = block[3:].strip()
            continue
        m = re.match(r"^(\d{1,3})\s*\.\s+", block)
        if m and pending_heading is not None:
            anchors.append((pending_heading, m.group(1)))
            pending_heading = None
    return anchors


def rewrite_chinese(anchors: list[tuple[str, str]]) -> None:
    text = ZH_PATH.read_text(encoding="utf-8")
    blocks = re.split(r"\n{2,}", text)

    # First pass: drop all `## ` heading blocks except the Footnotes section divider
    cleaned: list[str] = []
    inside_footnotes = False
    for raw in blocks:
        b = raw.strip()
        if not b:
            continue
        if b.startswith("## "):
            heading_text = b[3:].strip()
            # Keep only the Footnotes section divider — everything else is a
            # misextracted body fragment or title-page noise.
            if heading_text.lower() in ("footnotes", "footnote", "註腳"):
                inside_footnotes = True
                cleaned.append("---")
                cleaned.append("## 註腳")
                continue
            # drop
            continue
        cleaned.append(b)

    # Second pass: insert ## {zh} headings right before the matching paragraph
    para_to_heading: dict[str, str] = {}
    for en_heading, para_num in anchors:
        zh = HEADING_ZH.get(en_heading)
        if not zh:
            print(f"  ⚠ no zh translation for: {en_heading!r}")
            continue
        para_to_heading[para_num] = zh

    out: list[str] = []
    for block in cleaned:
        m = re.match(r"^(\d{1,3})\s*\.\s+", block)
        if m:
            n = m.group(1)
            if n in para_to_heading:
                out.append(f"## {para_to_heading[n]}")
        out.append(block)

    ZH_PATH.write_text("\n\n".join(out).rstrip() + "\n", encoding="utf-8")
    inserted = sum(1 for b in out if b.startswith("## ") and b != "## 註腳")
    print(f"  Wrote {ZH_PATH.name}: {inserted} section headings + 註腳 inserted")


def main() -> None:
    anchors = scan_english_anchors()
    print(f"Found {len(anchors)} (heading, next-para) anchors in English")
    rewrite_chinese(anchors)


if __name__ == "__main__":
    main()
