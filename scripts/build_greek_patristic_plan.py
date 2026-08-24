#!/usr/bin/env python3
"""Build 下冊's fifty readings — one for each lesson of the second volume.

上冊 reads fifty complete Scripture chapters; 下冊 reads these.  Lessons 1-25 are
patristic, weighted towards the Apostolic Fathers, whose Greek sits closest to
the New Testament the learner has just finished, and only then moving out to the
fourth-century theologians.  Lessons 26-50 are the Greek church's own documents:
the conciliar definitions, the canonical corpus that the Greek church actually
governs itself by, and the hymnody it sings.  The volume's Chrysostom liturgy is
a separate appendix and is not one of these fifty.

Every reading declares whether it is a complete short work or an authorised
excerpt, and an excerpt always names the sections it covers.  Nothing is ever
labelled complete because it looked long enough.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import greek_church_documents as church
import greek_patristic_sources as src


ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "greek-full"
CREEDS_GREEK = CACHE / "creeds-greek.json"
OUTPUT = CACHE / "patristic-plan.json"

VOLUME = 2
READING_COUNT = 50
FIRST_LESSON = 1
# Where the volume turns from the fathers to the church's own documents.
PATRISTIC_COUNT = 25

APOSTOLIC = "apostolic-father"
GREEK_FATHER = "greek-father"
CREED = "creed-or-decree"
CANON = "canon-collection"
HYMN = "liturgical-hymn"

CATEGORY_LABELS = {
    APOSTOLIC: "使徒教父",
    GREEK_FATHER: "希臘教父",
    CREED: "信經與信仰定義",
    CANON: "教規彙編",
    HYMN: "禮儀文本與頌歌",
}

PATRISTIC_CATEGORIES = {APOSTOLIC, GREEK_FATHER}

READINGS: list[dict] = [
    # --- Apostolic Fathers: closest Greek to the New Testament -------------
    {"category": APOSTOLIC, "titleZh": "十二使徒遺訓", "titleGrc": "Διδαχὴ τῶν δώδεκα ἀποστόλων",
     "author": "無名（一世紀末至二世紀初）", "completeness": "complete",
     "loader": ("af", "011-didache"), "difficulty": 2,
     "goals": ["讀最早的教會手冊", "辨認兩道教訓的命令語氣鏈"]},
    {"category": APOSTOLIC, "titleZh": "依納爵致以弗所人書", "titleGrc": "Ἰγνάτιος πρὸς Ἐφεσίους",
     "author": "安提阿的依納爵", "completeness": "complete",
     "loader": ("af", "003-ignatius-ephesians"), "difficulty": 3,
     "goals": ["處理書信體的問安套語", "辨認早期主教制語彙"]},
    {"category": APOSTOLIC, "titleZh": "依納爵致馬內夏人書", "titleGrc": "Ἰγνάτιος πρὸς Μαγνησιεῖς",
     "author": "安提阿的依納爵", "completeness": "complete",
     "loader": ("af", "004-ignatius-magnesians"), "difficulty": 3,
     "goals": ["比較同一作者不同書信的用語", "辨認守安息日與主日的對比段"]},
    {"category": APOSTOLIC, "titleZh": "依納爵致特拉勒人書", "titleGrc": "Ἰγνάτιος πρὸς Τραλλιανούς",
     "author": "安提阿的依納爵", "completeness": "complete",
     "loader": ("af", "005-ignatius-trallians"), "difficulty": 3,
     "goals": ["讀勸戒與警告並行的書信結構", "辨認早期反異端語彙"]},
    {"category": APOSTOLIC, "titleZh": "依納爵致費拉德非人書", "titleGrc": "Ἰγνάτιος πρὸς Φιλαδελφεῖς",
     "author": "安提阿的依納爵", "completeness": "complete",
     "loader": ("af", "007-ignatius-philadelphians"), "difficulty": 3,
     "goals": ["讀論教會合一與分裂的段落", "辨認引用舊約時的爭辯句式"]},
    {"category": APOSTOLIC, "titleZh": "依納爵致羅馬人書", "titleGrc": "Ἰγνάτιος πρὸς Ῥωμαίους",
     "author": "安提阿的依納爵", "completeness": "complete",
     "loader": ("af", "006-ignatius-romans"), "difficulty": 3,
     "goals": ["讀殉道意願的修辭高潮", "辨認第一人稱未來式的連續使用"]},
    {"category": APOSTOLIC, "titleZh": "依納爵致士每拿人書", "titleGrc": "Ἰγνάτιος πρὸς Σμυρναίους",
     "author": "安提阿的依納爵", "completeness": "complete",
     "loader": ("af", "008-ignatius-smyrnaeans"), "difficulty": 3,
     "goals": ["辨認反幻影說的論證", "認識「大公教會」一詞最早出處"]},
    {"category": APOSTOLIC, "titleZh": "依納爵致坡旅甲書", "titleGrc": "Ἰγνάτιος πρὸς Πολύκαρπον",
     "author": "安提阿的依納爵", "completeness": "complete",
     "loader": ("af", "009-ignatius-polycarp"), "difficulty": 3,
     "goals": ["讀寫給個人的牧養勸勉", "辨認連續命令語氣的節奏"]},
    {"category": APOSTOLIC, "titleZh": "坡旅甲致腓立比人書", "titleGrc": "Πολυκάρπου πρὸς Φιλιππησίους",
     "author": "士每拿的坡旅甲", "completeness": "complete",
     "loader": ("af", "010-polycarp-philippians"), "difficulty": 3,
     "goals": ["追蹤書中密集的新約引用", "比較與保羅書信的句法"]},
    {"category": APOSTOLIC, "titleZh": "坡旅甲殉道記", "titleGrc": "Μαρτύριον Πολυκάρπου",
     "author": "士每拿教會致腓羅美良教會", "completeness": "complete",
     "loader": ("af", "014-martyrdom"), "difficulty": 3,
     "goals": ["讀最早的殉道記敘事", "辨認敘事與祈禱段落的語域轉換"]},
    {"category": APOSTOLIC, "titleZh": "革利免二書", "titleGrc": "Κλήμεντος Βʹ πρὸς Κορινθίους",
     "author": "無名（二世紀中葉，託名革利免）", "completeness": "complete",
     "loader": ("af", "002-ii_clement"), "difficulty": 3,
     "goals": ["讀現存最早的基督教講道", "辨認勸勉體的第一人稱複數"]},
    {"category": APOSTOLIC, "titleZh": "致丟格那妥書", "titleGrc": "Πρὸς Διόγνητον",
     "author": "無名護教者（二世紀）", "completeness": "complete",
     "loader": ("af", "015-diognetus"), "difficulty": 4,
     "goals": ["讀古典修辭訓練下的護教散文", "辨認長排比句的結構"]},
    {"category": APOSTOLIC, "titleZh": "革利免一書 59–61：大祈禱文",
     "titleGrc": "Κλήμεντος Αʹ πρὸς Κορινθίους 59–61",
     "author": "羅馬的革利免", "completeness": "excerpt", "extent": "第 59–61 章",
     "loader": ("af-slice", "001-i_clement", 59, 61), "difficulty": 4,
     "goals": ["讀最早的教會公禱文", "辨認七十士譯本式的祈禱語彙"]},
    {"category": APOSTOLIC, "titleZh": "巴拿巴書 18–21：兩道",
     "titleGrc": "Βαρναβᾶ ἐπιστολή 18–21",
     "author": "託名巴拿巴", "completeness": "excerpt", "extent": "第 18–21 章",
     "loader": ("af-slice", "012-barnabas", 18, 21), "difficulty": 3,
     "goals": ["與十二使徒遺訓的兩道對讀", "辨認光明與黑暗的對比詞彙"]},
    {"category": APOSTOLIC, "titleZh": "黑馬牧人書：第一異象",
     "titleGrc": "Ποιμὴν τοῦ Ἑρμᾶ, Ὅρασις Αʹ",
     "author": "黑馬", "completeness": "excerpt", "extent": "第一異象（Vis. I）",
     "loader": ("af-slice", "013-shepherd", 1, 1), "difficulty": 3,
     "wordRange": (700, 1400),
     "goals": ["讀啟示體敘事的第一人稱", "辨認口語化的希臘文"]},
    {"category": APOSTOLIC, "titleZh": "黑馬牧人書：誡命一至四",
     "titleGrc": "Ποιμὴν τοῦ Ἑρμᾶ, Ἐντολαὶ Αʹ–Δʹ",
     "author": "黑馬", "completeness": "excerpt", "extent": "第一至第四誡命（Mand. I–IV）",
     # The Shepherd numbers 5 visions + 12 mandates + 10 similitudes as 27
     # consecutive top-level units, so the mandates start at unit 6, not at 1.
     "loader": ("af-slice", "013-shepherd", 6, 9), "difficulty": 3,
     "goals": ["讀命令語氣的倫理教導", "與十二使徒遺訓的兩道對讀"]},
    {"category": APOSTOLIC, "titleZh": "巴拿巴書 1–5：新約與舊約的關係",
     "titleGrc": "Βαρναβᾶ ἐπιστολή 1–5",
     "author": "託名巴拿巴", "completeness": "excerpt", "extent": "第 1–5 章",
     "loader": ("af-slice", "012-barnabas", 1, 5), "difficulty": 4,
     "goals": ["讀二世紀的預表解經", "辨認引用先知書時的論證推進"]},
    {"category": APOSTOLIC, "titleZh": "革利免一書 42–44：使徒統緒與教會職分",
     "titleGrc": "Κλήμεντος Αʹ πρὸς Κορινθίους 42–44",
     "author": "羅馬的革利免", "completeness": "excerpt", "extent": "第 42–44 章",
     "loader": ("af-slice", "001-i_clement", 42, 44), "difficulty": 4,
     "goals": ["讀主教與執事制度最早的論述", "辨認 ἐπίσκοπος 與 πρεσβύτερος 的早期用法"]},

    # --- Greek Fathers -----------------------------------------------------
    {"category": GREEK_FATHER, "titleZh": "猶斯定《第一護教辭》1–8：向皇帝陳情",
     "titleGrc": "Ἰουστίνου Ἀπολογία Αʹ 1–8",
     "author": "殉道者猶斯定", "completeness": "excerpt", "extent": "第 1–8 章",
     "loader": ("first1k", "tlg0645.tlg001.1st1K-grc1.xml", 1, 8), "difficulty": 4,
     "goals": ["讀上書體的稱謂與陳情句式", "辨認護教者借用的哲學語彙"]},
    {"category": GREEK_FATHER, "titleZh": "猶斯定《第一護教辭》61–67：洗禮與感恩祭",
     "titleGrc": "Ἰουστίνου Ἀπολογία Αʹ 61–67",
     "author": "殉道者猶斯定", "completeness": "excerpt", "extent": "第 61–67 章",
     "loader": ("first1k", "tlg0645.tlg001.1st1K-grc1.xml", 61, 67), "difficulty": 4,
     "goals": ["讀二世紀主日聚會的最早描述", "辨認禮儀術語的形成期用法"]},
    {"category": GREEK_FATHER, "titleZh": "亞他那修《論道成肉身》1–4：創造與敗壞",
     "titleGrc": "Ἀθανασίου Περὶ τῆς ἐνανθρωπήσεως τοῦ Λόγου 1–4",
     "author": "亞歷山大的亞他那修", "completeness": "excerpt", "extent": "第 1–4 章",
     "loader": ("first1k", "tlg2035.tlg002.1st1K-grc1.xml", 1, 4), "difficulty": 4,
     "goals": ["辨認神學論述的長句結構", "追蹤 Λόγος 一詞的論證功能"]},
    {"category": GREEK_FATHER, "titleZh": "亞他那修《論道成肉身》54：他成為人，使我們成為神",
     "titleGrc": "Ἀθανασίου Περὶ τῆς ἐνανθρωπήσεως τοῦ Λόγου 54",
     "author": "亞歷山大的亞他那修", "completeness": "excerpt", "extent": "第 54 章",
     "loader": ("first1k", "tlg2035.tlg002.1st1K-grc1.xml", 54, 54), "difficulty": 4,
     "goals": ["精讀神化教義的關鍵句", "比較與尼西亞信經的用語"]},
    {"category": GREEK_FATHER, "titleZh": "額我略‧納祥《神學講辭》第廿七篇：論神學該由誰、何時、如何講",
     "titleGrc": "Γρηγορίου τοῦ Ναζιανζηνοῦ Λόγος ΚΖʹ",
     "author": "納祥的額我略", "completeness": "complete",
     "loader": ("first1k", "tlg2022.tlg007.1st1K-grc1.xml", 0, 0), "difficulty": 5,
     "goals": ["讀第二代詭辯術訓練下的教父散文", "辨認修辭問句與反諷"]},
    {"category": GREEK_FATHER, "titleZh": "額我略‧納祥《神學講辭》第廿八篇 1–10：論神",
     "titleGrc": "Γρηγορίου τοῦ Ναζιανζηνοῦ Λόγος ΚΗʹ 1–10",
     "author": "納祥的額我略", "completeness": "excerpt", "extent": "第 1–10 節",
     "loader": ("first1k", "tlg2022.tlg008.1st1K-grc1.xml", 1, 10), "difficulty": 5,
     "goals": ["讀否定神學的論證推進", "辨認哲學語彙進入神學的痕跡"]},
    {"category": GREEK_FATHER, "titleZh": "金口若望《復活節教理講道》",
     "titleGrc": "Ἰωάννου τοῦ Χρυσοστόμου Λόγος Κατηχητικὸς εἰς τὸ ἅγιον Πάσχα",
     "author": "金口若望", "completeness": "complete",
     "loader": ("paschal",), "difficulty": 3, "wordRange": (300, 450),
     "goals": ["讀拜占庭禮復活節必誦的講道", "辨認排比與呼告的節奏"]},

    # --- Creeds and conciliar decrees --------------------------------------
    {"category": CREED, "titleZh": "尼西亞信經（325 原版）", "titleGrc": "Σύμβολον τῆς ἐν Νικαίᾳ Αʹ Οἰκουμενικῆς Συνόδου",
     "author": "第一次大公會議", "completeness": "complete",
     "loader": ("creed-file", "ecumenical-councils/01-nicaea-325.ts"), "difficulty": 3,
     "goals": ["精讀 ὁμοούσιος 一詞的語境", "辨認信經末尾的絕罰條款句型"]},
    {"category": CREED, "titleZh": "尼西亞—君士坦丁堡信經（381，大公會議原文）",
     "titleGrc": "Σύμβολον Νικαίας–Κωνσταντινουπόλεως",
     "author": "第二次大公會議", "completeness": "complete",
     "loader": ("creed-json", "constantinople-381"), "difficulty": 3,
     "goals": ["比較 325 與 381 兩版的差異", "區分會議複數形與禮儀單數形"]},
    {"category": CREED, "titleZh": "迦克墩信仰定義（451）", "titleGrc": "Ὅρος τῆς ἐν Χαλκηδόνι Δʹ Οἰκουμενικῆς Συνόδου",
     "author": "第四次大公會議", "completeness": "complete",
     "loader": ("creed-json", "chalcedon-451"), "difficulty": 4,
     "goals": ["精讀迦克墩四副詞", "辨認 πρόσωπον 與 ὑπόστασις 的分工"]},
    {"category": CREED, "titleZh": "君士坦丁堡第三次大公會議信仰定義（681，駁一志論）",
     "titleGrc": "Ὅρος τῆς ΣΤʹ Οἰκουμενικῆς Συνόδου",
     "author": "第六次大公會議", "completeness": "complete",
     "loader": ("creed-json", "constantinople-681"), "difficulty": 4,
     "goals": ["讀兩個意志的定義句", "比較與迦克墩定義的續接關係"]},
    {"category": CANON, "titleZh": "以弗所大公會議教規（431）", "titleGrc": "Κανόνες τῆς ἐν Ἐφέσῳ Γʹ Οἰκουμενικῆς Συνόδου",
     "author": "第三次大公會議", "completeness": "excerpt", "extent": "教規本文",
     "loader": ("creed-file", "ecumenical-councils/early-03-ephesus.ts"), "difficulty": 4,
     "goals": ["讀會議法規的公文體", "辨認判決與懲戒用語"]},
    {"category": CANON, "titleZh": "第二次尼西亞大公會議教規（787）", "titleGrc": "Κανόνες τῆς ἐν Νικαίᾳ Ζʹ Οἰκουμενικῆς Συνόδου",
     "author": "第七次大公會議", "completeness": "excerpt", "extent": "教規本文",
     "loader": ("creed-file", "ecumenical-councils/early-07-nicaea-ii.ts"), "difficulty": 4,
     "goals": ["讀敬像爭論的法規語言", "辨認拜占庭教會法的句型"]},

    # --- Canonical corpus --------------------------------------------------
    # The canons are the Greek church's working law, and they are read here in
    # the order the canonical collections themselves put them in: the apostolic
    # canons, then the ecumenical councils, then the local synods whose canons
    # the councils ratified.
    {"category": CANON, "titleZh": "使徒教規（85 條）", "titleGrc": "Κανόνες τῶν ἁγίων Ἀποστόλων",
     "author": "託名使徒（四世紀彙編）", "completeness": "complete",
     "loader": ("canons", "canons-apostolic", 0, 0), "difficulty": 3,
     "goals": ["讀教會法最基本的一套條文", "辨認 καθαιρείσθω／ἀφοριζέσθω 的處分句式"]},
    {"category": CANON, "titleZh": "尼西亞第一次大公會議教規（325，20 條）",
     "titleGrc": "Κανόνες τῆς Αʹ Οἰκουμενικῆς Συνόδου",
     "author": "第一次大公會議", "completeness": "complete",
     "loader": ("canons", "canons-nicaea-i", 0, 0), "difficulty": 4,
     "goals": ["讀最早的大公會議法規", "辨認教區與教省的用語"]},
    {"category": CANON, "titleZh": "君士坦丁堡第一次大公會議教規（381，7 條）",
     "titleGrc": "Κανόνες τῆς Βʹ Οἰκουμενικῆς Συνόδου",
     "author": "第二次大公會議", "completeness": "complete",
     "loader": ("canons", "canons-constantinople-i", 0, 0), "difficulty": 4,
     "goals": ["讀君士坦丁堡教座地位的條文", "辨認接納異端歸正者的程序用語"]},
    {"category": CANON, "titleZh": "迦克墩大公會議教規（451，30 條）",
     "titleGrc": "Κανόνες τῆς Δʹ Οἰκουμενικῆς Συνόδου",
     "author": "第四次大公會議", "completeness": "complete",
     "loader": ("canons", "canons-chalcedon", 0, 0), "difficulty": 4,
     "goals": ["讀教會行政與修道制度的規範", "辨認聖職買賣與轉調的禁令句型"]},
    {"category": CANON, "titleZh": "特魯洛（五六）大公會議教規 1–20",
     "titleGrc": "Κανόνες τῆς ἐν Τρούλλῳ Πενθέκτης Συνόδου 1–20",
     "author": "五六會議（692）", "completeness": "excerpt", "extent": "第 1–20 條（全 102 條）",
     "loader": ("canons", "canons-trullo", 1, 20), "difficulty": 4,
     "goals": ["讀拜占庭教會法的成熟文體", "辨認引述前代教規時的指涉方式"]},
    {"category": CANON, "titleZh": "安基拉會議教規（314）", "titleGrc": "Κανόνες τῆς ἐν Ἀγκύρᾳ Συνόδου",
     "author": "安基拉地方會議", "completeness": "complete",
     "loader": ("canons", "canons-ancyra", 0, 0), "difficulty": 4,
     "goals": ["讀迫害後如何接納背教者的條文", "辨認補贖年限的表述方式"]},
    {"category": CANON, "titleZh": "新凱撒利亞會議教規（約 315）",
     "titleGrc": "Κανόνες τῆς ἐν Νεοκαισαρείᾳ Συνόδου",
     "author": "新凱撒利亞地方會議", "completeness": "complete",
     "loader": ("canons", "canons-neocaesarea", 0, 0), "difficulty": 3,
     "goals": ["讀最短的一部教規彙編", "辨認條件句與處分句的固定配對"]},
    {"category": CANON, "titleZh": "甘格拉會議教規（約 340）", "titleGrc": "Κανόνες τῆς ἐν Γάγγρᾳ Συνόδου",
     "author": "甘格拉地方會議", "completeness": "complete",
     "loader": ("canons", "canons-gangra", 0, 0), "difficulty": 4,
     "goals": ["讀教會對極端禁欲主義的回應", "辨認絕罰條款的重複句型"]},
    {"category": CANON, "titleZh": "安提阿會議教規（341）", "titleGrc": "Κανόνες τῆς ἐν Ἀντιοχείᾳ Συνόδου",
     "author": "安提阿地方會議", "completeness": "complete",
     "loader": ("canons", "canons-antioch", 0, 0), "difficulty": 4,
     "goals": ["讀教省會議制度的規定", "辨認長條文中的從屬子句層次"]},
    {"category": CANON, "titleZh": "老底嘉會議教規（約 360）", "titleGrc": "Κανόνες τῆς ἐν Λαοδικείᾳ Συνόδου",
     "author": "老底嘉地方會議", "completeness": "complete",
     "loader": ("canons", "canons-laodicea", 0, 0), "difficulty": 3,
     "goals": ["讀禮儀與聖經目錄的規定", "辨認簡短禁令的祈使句式"]},
    {"category": CANON, "titleZh": "撒狄迦會議教規（343）", "titleGrc": "Κανόνες τῆς ἐν Σαρδικῇ Συνόδου",
     "author": "撒狄迦地方會議", "completeness": "complete",
     "loader": ("canons", "canons-sardica", 0, 0), "difficulty": 4,
     "goals": ["讀主教上訴制度的條文", "辨認會議紀錄體的發言引述"]},
    {"category": CANON, "titleZh": "迦太基會議教規 1–20（希臘文傳本）",
     "titleGrc": "Κανόνες τῆς ἐν Καρθαγένῃ Συνόδου 1–20",
     "author": "迦太基地方會議（希臘文傳本）", "completeness": "excerpt",
     "extent": "第 1–20 條（希臘文傳本全 133 條）",
     "loader": ("canons", "canons-carthage", 1, 20), "difficulty": 4,
     "goals": ["讀拉丁教會法規的希臘文傳本", "比較同一制度在兩個語言傳統中的用語"]},

    # --- Liturgical texts and hymnody --------------------------------------
    {"category": HYMN, "titleZh": "歡欣之光（晚禱頌歌）", "titleGrc": "Φῶς ἱλαρόν",
     "author": "無名（二至三世紀）", "completeness": "complete",
     "loader": ("phos",), "difficulty": 2, "wordRange": (30, 70),
     "goals": ["讀現存最早的基督徒頌歌之一", "辨認呼格與分詞的頌讚句型"]},
    {"category": HYMN, "titleZh": "大榮耀頌（晨禱）", "titleGrc": "Ἡ Μεγάλη Δοξολογία",
     "author": "無名（四世紀前後）", "completeness": "complete",
     "loader": ("hymn", "hymn-great-doxology"), "difficulty": 3, "wordRange": (240, 360),
     "goals": ["讀天使頌與三聖頌接成的頌讚", "辨認第二人稱單數的連續頌詞"]},
    {"category": HYMN, "titleZh": "晨禱起始禱文（三聖頌組）",
     "titleGrc": "Ἀρχὴ τοῦ Ὄρθρου· Τρισάγιον",
     "author": "拜占庭禮日課", "completeness": "excerpt", "extent": "自天上之王至主禱文的結束頌",
     "loader": ("goarch", "goarch-orthros.html", r"Βασιλεῦ Οὐράνιε",
                r"Δεῦτε, προσκυνήσωμεν", "https://glt.goarch.org/texts/Oro/Orthros.html"),
     "difficulty": 2, "wordRange": (100, 260),
     "goals": ["熟讀每日必誦的固定禱文", "辨認呼格加分詞的祈禱套語"]},
    {"category": HYMN, "titleZh": "卡西亞尼讚詞（聖週三晚禱）", "titleGrc": "Τροπάριον τῆς Κασσιανῆς",
     "author": "卡西亞尼（九世紀，現存最早留名的女性聖詩作者之一）",
     "completeness": "complete",
     "loader": ("hymn", "hymn-kassiani"), "difficulty": 4, "wordRange": (90, 150),
     "goals": ["讀拜占庭抒情聖詩的長句", "辨認呼格插入語打斷主句的節奏"]},
    {"category": HYMN, "titleZh": "聖母讚頌詞（阿卡提斯托斯頌）", "titleGrc": "Ἀκάθιστος Ὕμνος",
     "author": "無名（六世紀，傳為羅曼諾斯）", "completeness": "complete",
     "loader": ("hymn", "hymn-akathistos"), "difficulty": 4, "wordRange": (1200, 1900),
     "goals": ["讀二十四首字母離合詩的結構", "辨認 Χαῖρε 連禱的排比"]},
    {"category": HYMN, "titleZh": "復活節晨禱正典（大馬士革的約翰）",
     "titleGrc": "Ὁ Κανὼν τοῦ Πάσχα, ποίημα Ἰωάννου τοῦ Δαμασκηνοῦ",
     "author": "大馬士革的約翰（八世紀）", "completeness": "complete",
     "loader": ("goarch", "goarch-pascha.html", r"Ὁ Κανών, ποίημα Ἰωάννου τοῦ Δαμασκηνοῦ",
                r"Ἐξαποστειλάριον αὐτόμελον", "https://glt.goarch.org/texts/Oro/Pascha.html"),
     "difficulty": 4, "wordRange": (900, 2000),
     "goals": ["讀正典（κανών）九頌的體裁", "辨認頌歌對出埃及記與先知書的引用"]},
    {"category": HYMN, "titleZh": "聖誕晨禱（12 月 25 日）", "titleGrc": "Ἀκολουθία τοῦ Ὄρθρου τῆς Χριστοῦ Γεννήσεως",
     "author": "拜占庭禮節期日課", "completeness": "complete",
     "loader": ("hymn", "orthros-christmas"), "difficulty": 4, "wordRange": (3200, 4500),
     "goals": ["讀一整套節期日課的實際編排", "辨認唱詞、經課與鼓詞（rubric）的語域差異"]},
]


# Schaff prints the creed and his own apparatus in the same table cells, so a
# reading has to say which extracted segments are the creed.  These are
# curatorial decisions, recorded here rather than applied by a heuristic.
CREED_SEGMENTS: dict[str, set[int]] = {
    # Segment 2 is Schaff's Greek term index (νοῦς, πνεῦμα, θεοτόκος …), not
    # the Definition; segment 1 runs straight on into segment 3.
    "chalcedon-451": {1, 3},
}

CREED_EXCLUSIONS: dict[str, str] = {
    "chalcedon-451": "第 2 段是 Schaff 自編的希臘術語索引，不是信仰定義本文。",
}

CREED_REVIEW_NOTES: dict[str, str] = {
    "constantinople-381": (
        "第 3 段夾著 Schaff 的異文縮寫（τὸ κυρ. καὶ ζωοπ. …），"
        "排版前須由人工剔除，本檔不自行改動原文。"
    ),
}


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


_WIKISOURCE_MANIFEST: dict[str, dict] | None = None


def wikisource_url(stem: str) -> str:
    """The frozen source's own URL, read off the freeze manifest.

    Reconstructing it from the stem would be a second place where the page name
    lives, and the two would drift; the manifest is the one that was actually
    downloaded.
    """
    global _WIKISOURCE_MANIFEST
    if _WIKISOURCE_MANIFEST is None:
        path = CACHE / "sources" / "church-documents" / "manifest.json"
        if not path.exists():
            raise FileNotFoundError(
                f"缺少教會文獻凍結清單：{path}；先跑 fetch_greek_church_documents.py --write"
            )
        payload = json.loads(path.read_text(encoding="utf-8"))
        _WIKISOURCE_MANIFEST = {item["stem"]: item for item in payload["sources"]}
    entry = _WIKISOURCE_MANIFEST.get(stem)
    if entry is None:
        raise LookupError(f"凍結清單沒有 {stem}")
    return entry["sourceUrl"]


def paschal_homily() -> tuple[list[src.Segment], dict]:
    """The Paschal homily, from the witness that is not corrupt.

    glt.goarch.org carries the homily too, but its copy repeats half a clause
    ("εἰς τὴν ἐνάτηντις ὑστέρησεν εἰς τὴν"), a dittography that would ship a
    defective reading.  The clean witness is used, and the defect is recorded
    so the choice is auditable rather than silent.
    """
    segments = src.load_goarch_block(
        "katanixi-paschal-homily.html",
        r"Εἴ τις εὐσεβὴς",
        r"Κάνε ἐγγραφή",
    )
    return segments, {
        "source": "katanixi.gr（希臘正教會靈修網站）所刊《復活節教理講道》希臘原文",
        "sourceUrl": "https://katanixi.gr/katichitikos-logos-agioy-ioannoy-toy-ch/",
        "crossCheck": (
            "glt.goarch.org 同篇有重出衍文「εἰς τὴν ἐνάτηντις ὑστέρησεν εἰς τὴν」，"
            "正確讀法為「εἰς τὴν ἐννάτην, προσελθέτω」，故不採該版。"
        ),
    }


def phos_hilaron() -> tuple[list[src.Segment], dict]:
    segments = src.load_goarch_block(
        "goarch-esperinos.html", r"Φῶς ἱλαρὸν", r"Τῷ Σαββάτῳ ἑσπέρας"
    )
    return segments, {
        "source": src.GOARCH_EDITION,
        "sourceUrl": "https://glt.goarch.org/texts/Oro/Esperinos.html",
    }


def load(spec: dict) -> tuple[list[src.Segment], dict]:
    kind, *args = spec["loader"]
    if kind == "af":
        return src.load_apostolic_father(args[0]), {
            "source": src.AF_EDITION, "sourceUrl": src.AF_URL,
        }
    if kind == "af-slice":
        stem, first, last = args
        return src.slice_chapters(src.load_apostolic_father(stem), first, last), {
            "source": src.AF_EDITION, "sourceUrl": src.AF_URL,
        }
    if kind == "first1k":
        filename, first, last = args
        return src.load_first1k(filename, first, last), {
            "source": src.FIRST1K_EDITION, "sourceUrl": src.FIRST1K_URL,
        }
    if kind == "creed-file":
        segments, source = src.load_creed_greek(args[0])
        return segments, {"source": source or "repo data/creeds", "sourceUrl": ""}
    if kind == "creed-json":
        slug = args[0]
        payload = json.loads(CREEDS_GREEK.read_text(encoding="utf-8"))
        for document in payload["documents"]:
            if document["slug"] != slug:
                continue
            keep = CREED_SEGMENTS.get(slug)
            chosen = [
                item for item in document["segments"]
                if keep is None or item["ordinal"] in keep
            ]
            dropped = [
                item["ordinal"] for item in document["segments"]
                if keep is not None and item["ordinal"] not in keep
            ]
            segments = [
                src.Segment(str(item["ordinal"]), item["displayText"]) for item in chosen
            ]
            meta = {
                "source": document["edition"],
                "sourceUrl": document["sourceUrl"],
                "segmentsNeedingReview": [
                    item["ordinal"] for item in chosen
                    if item["reviewStatus"] != "auto_accepted"
                ],
            }
            if dropped:
                meta["segmentsExcluded"] = dropped
                meta["exclusionReason"] = CREED_EXCLUSIONS[slug]
            if slug in CREED_REVIEW_NOTES:
                meta["reviewNote"] = CREED_REVIEW_NOTES[slug]
            return segments, meta
        raise LookupError(f"creeds-greek.json 沒有 {args[0]}")
    if kind == "canons":
        stem, first, last = args
        segments = church.load_canons(stem, first, last)
        meta = {
            "source": church.WIKISOURCE_EDITION,
            "sourceUrl": wikisource_url(stem),
            "license": church.WIKISOURCE_LICENSE,
            "canonNumbers": [segment.ref for segment in segments],
        }
        if first:
            meta["canonTotal"] = church.canon_count(stem)
        return [src.Segment(s.ref, s.text) for s in segments], meta
    if kind == "hymn":
        stem = args[0]
        segments = church.load_hymn(stem)
        return [src.Segment(s.ref, s.text) for s in segments], {
            "source": church.WIKISOURCE_EDITION,
            "sourceUrl": wikisource_url(stem),
            "license": church.WIKISOURCE_LICENSE,
        }
    if kind == "goarch":
        filename, start, end, url = args
        return src.load_goarch_block(filename, start, end), {
            "source": src.GOARCH_EDITION,
            "sourceUrl": url,
        }
    if kind == "paschal":
        return paschal_homily()
    if kind == "phos":
        return phos_hilaron()
    raise ValueError(f"unknown loader {kind}")


def build() -> dict:
    if len(READINGS) != READING_COUNT:
        raise ValueError(f"讀文應為 {READING_COUNT} 篇，實得 {len(READINGS)}")

    patristic = [s for s in READINGS if s["category"] in PATRISTIC_CATEGORIES]
    if len(patristic) != PATRISTIC_COUNT:
        raise ValueError(f"教父讀文應為 {PATRISTIC_COUNT} 篇，實得 {len(patristic)}")
    if READINGS[:PATRISTIC_COUNT] != patristic:
        raise ValueError("教父讀文必須排在前 25 篇，教會文獻在後 25 篇")

    readings = []
    for index, spec in enumerate(READINGS):
        segments, meta = load(spec)
        words = sum(len(segment.text.split()) for segment in segments)
        if spec["completeness"] == "excerpt" and not spec.get("extent"):
            raise ValueError(f"{spec['titleZh']} 標為節錄卻沒有註明範圍")
        # An HTML block boundary that slips takes hundreds of unrelated words
        # with it and still looks like a successful parse, so anything scraped
        # from a page declares the size it should be.
        low, high = spec.get("wordRange", (0, 0))
        if low and not (low <= words <= high):
            raise ValueError(
                f"{spec['titleZh']}：{words} 詞不在預期的 {low}–{high} 詞範圍，"
                "多半是段落邊界抓錯"
            )
        reading = {
            "ordinal": index + 1,
            "volume": VOLUME,
            "lesson": FIRST_LESSON + index,
            "category": spec["category"],
            "categoryLabel": CATEGORY_LABELS[spec["category"]],
            "titleZh": spec["titleZh"],
            "titleGrc": spec["titleGrc"],
            "author": spec["author"],
            "completeness": spec["completeness"],
            "extent": spec.get("extent", "全篇"),
            "difficulty": spec["difficulty"],
            "learningGoals": spec["goals"],
            "segmentCount": len(segments),
            "wordCount": words,
            "translationPlan": "self-translated",
            "segments": [
                {"ref": segment.ref, "sourceText": segment.text, "displayText": nfc(segment.text)}
                for segment in segments
            ],
            **meta,
        }
        readings.append(reading)

    counts: dict[str, int] = {}
    for reading in readings:
        counts[reading["category"]] = counts.get(reading["category"], 0) + 1
    complete = sum(1 for r in readings if r["completeness"] == "complete")

    return {
        "schemaVersion": "1.0.0",
        "generatedOn": date.today().isoformat(),
        "status": "readings-frozen-translation-pending",
        "language": "Koine Greek",
        "languageCode": "grc",
        "curriculum": {
            "volume": VOLUME,
            "volumeTitle": "下冊《教父文獻與希臘教會文獻》",
            "lessonCount": 50,
            "readingCount": READING_COUNT,
            "lessonRange": f"{FIRST_LESSON}–{FIRST_LESSON + READING_COUNT - 1}",
            "note": (
                "下冊第 1–25 課配教父文獻一篇，第 26–50 課配希臘教會文獻或禮儀文本一篇；"
                "金口若望禮儀是另立的附錄，不算在這五十篇之內。"
            ),
        },
        "summary": {
            "readingCount": len(readings),
            "segmentCount": sum(r["segmentCount"] for r in readings),
            "wordCount": sum(r["wordCount"] for r in readings),
            "categoryCounts": counts,
            "completeWorks": complete,
            "excerpts": len(readings) - complete,
        },
        "translationNote": (
            "這 50 篇全部沒有可用的權威繁體中文譯本，一律自譯並標「自譯」；"
            "信經部分若與 /creeds 既有中譯重疊，另行標註來源。"
        ),
        "readings": readings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="建立希臘文讀本下冊五十篇教父與希臘教會文獻")
    parser.add_argument("--write", action="store_true", help="寫出 patristic-plan.json")
    args = parser.parse_args()

    plan = build()
    for reading in plan["readings"]:
        mark = "全" if reading["completeness"] == "complete" else "節"
        print(
            f"  {reading['lesson']:>2d}課 {reading['categoryLabel']:<6s}[{mark}]"
            f" {reading['segmentCount']:>4d}段 {reading['wordCount']:>5d}詞  {reading['titleZh']}"
        )
    summary = plan["summary"]
    print(
        f"  合計 {summary['readingCount']} 篇、{summary['segmentCount']} 段、"
        f"{summary['wordCount']} 詞；完整 {summary['completeWorks']} 篇、"
        f"節錄 {summary['excerpts']} 篇；分類 {summary['categoryCounts']}"
    )

    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"已寫出 {OUTPUT}")
    else:
        print("（未寫檔；加 --write 才會輸出）")


if __name__ == "__main__":
    main()
