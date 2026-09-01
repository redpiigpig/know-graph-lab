#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""替站上的教父卷補上第三欄「原文」（拉丁／希臘），成為 中文 / 英文 / 原文 三欄對照。

  python scripts/fathers_add_original.py --work augustine-confessions          # 只驗，不寫
  python scripts/fathers_add_original.py --work augustine-confessions --apply  # 寫回 JSONL

站上教父卷本來就是兩欄：content 是繁中精修，source_text 是 Schaff 英譯。本腳本
補的是第三欄原典，對齊靠古典分章（liber.caput），不做語意對齊。

流程：
  ① 抓原典 → 按 卷.章 切段（scripts/fathers_original.py 的純函式）
  ② **覆蓋率閘**：站上章節 vs 原典章節，缺章或多章一律先報出來
  ③ 逐段組裝 sources[原文語言]；範圍內任何一章缺就整段留白
  ④ --apply 才寫回 {id}.jsonl，並鏡射 source_text/source_lang 給舊的兩欄 reader

🚨 覆蓋率閘不是形式。首跑《懺悔錄》就靠它抓到站上卷一只到第 18 章、第 19–20 章
   中英文都不存在。沒有閘的話那兩章拉丁文會被併進第 18 章那一段，三欄看起來齊、
   內容從那裡開始錯位，而畫面上完全看不出來。

🚨 只讀寫 {id}.jsonl。同目錄下的 .en.bak.jsonl 與 .bak_pre_merge 是翻譯前的英文
   原檔，段數對不上（Augustine Confessions 正式檔 68 段、英文備份 481 段）。
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path

import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "fathers_original", ROOT / "scripts" / "fathers_original.py")
FO = importlib.util.module_from_spec(_spec)
sys.modules["fathers_original"] = FO
_spec.loader.exec_module(FO)


# ── 取源登錄 ────────────────────────────────────────────────────────────────
# 每一部著作登記：站上是哪一本 ebook、原文語言、原典從哪裡抓、每卷幾章。
# `chapters` 是原典的權威章數，用來判站上有沒有缺章——不可以拿站上的章數回填。
# `mode` 決定原典怎麼切、又怎麼放進中譯的段落格：
#   paragraph — 原典帶 `卷.章.節` 行標，中譯段落也帶同一組節號 → 逐節對齊（最細）
#   chapter   — 原典只有 `[I]` 這種章號，中譯只有「第N章」標題 → 逐章對齊（較粗）
#   greek     — 原典是 Migne PG 掃描本的自家 OCR 帳本（scripts/fathers_pg_ocr.py），
#               ΛΟΓΟΣ 分卷、α΄ β΄ γ΄ 分節，節號與中英譯的 1. 2. 是同一套編次 → 逐節
#   roman     — 原典行標是 `I. [1] …`（行首羅馬章號＋章內方括號節號），中譯只有
#               「第N章」標題 → 逐章對齊。特土良全集那一系。
# 四種都不猜：對不上就留空。
#
# 一冊裡收了好幾部各自獨立的著作時（特土良那冊 23 部），用 `parts` 逐部登記：
# 每部有自己的 chapter_path 前綴與原典網址，章號各自從一起算，不可混在一起。
WORKS: dict[str, dict] = {
    "augustine-confessions": {
        "label": "奧古斯丁《懺悔錄》",
        "ebook_id": "9edb7c37-4231-412b-83bd-78f3f793cc0a",
        "prefix": "懺悔錄",
        "lang": "la",
        "mode": "paragraph",
        "urls": [f"https://www.thelatinlibrary.com/augustine/conf{b}.shtml"
                 for b in range(1, 14)],
        "chapters": {1: 20, 2: 10, 3: 12, 4: 16, 5: 14, 6: 16, 7: 21,
                     8: 12, 9: 13, 10: 43, 11: 31, 12: 32, 13: 38},
        "source": "The Latin Library（Corpus Christianorum 系 Verheijen 校本，公有領域）",
    },
    "augustine-city-of-god": {
        "label": "奧古斯丁《上帝之城》",
        "ebook_id": "1eb50be9-34ac-4ce3-874d-1280975851fc",
        "prefix": "上帝之城",
        "lang": "la",
        "mode": "chapter",
        "urls": [f"https://www.thelatinlibrary.com/augustine/civ{b}.shtml"
                 for b in range(1, 23)],
        "source": "The Latin Library（Dombart–Kalb 校本，公有領域）",
    },
    "chrysostom-de-sacerdotio": {
        "label": "金口若望《論司祭職》",
        "ebook_id": "76df31fe-e732-4aa6-88c2-d650a09fb688",
        "prefix": "論司祭職",
        "lang": "grc",
        "mode": "greek",
        "ledger": "output/source-cache/pg-greek-ocr/pg48-de-sacerdotio.jsonl",
        # 站上這一部切成「論司祭職 第3章」…「第8章」，其實是六卷正文；前兩段是
        # 書名頁與導論。第N章 → 卷 N-2。
        "book_from_chapter": -2,
        "source": "Migne PG 48.623–692 掃描本，Gemini Vision 逐欄 OCR",
    },
    "tertullian-anf3": {
        "label": "特土良（ANF 第三卷）",
        "ebook_id": "364dac2e-410f-4906-be63-8bb86b4865ee",
        "lang": "la",
        "mode": "roman",
        "source": "The Latin Library（公有領域）",
        # 站上那一冊逐部切得很乾淨，每部都對得到 The Latin Library 的一篇。
        "parts": [(zh, f"https://www.thelatinlibrary.com/tertullian/tertullian.{slug}.shtml")
                  for zh, slug in (
                      ("特土良護教辭", "apol"),
                      ("特土良論偶像崇拜", "idololatria"),
                      ("特土良論觀劇", "spect"),
                      ("特土良論花冠", "corona"),
                      ("特土良致斯卡普拉", "scapulam"),
                      ("特土良致萬民", "nationes1"),
                      ("特土良致萬民", "nationes2"),
                      ("特土良駁猶太人", "iudaeos"),
                      ("特土良論靈魂的見證", "testimonia"),
                      ("特土良論靈魂", "anima"),
                      ("特土良駁異端的時效", "praescrip"),
                      ("特土良駁馬吉安", "marcionem1"),
                      ("特土良駁馬吉安", "marcionem2"),
                      ("特土良駁馬吉安", "marcionem3"),
                      ("特土良駁馬吉安", "marcionem4"),
                      ("特土良駁馬吉安", "marcionem5"),
                      ("特土良駁黑摩根", "herm"),
                      ("特土良駁瓦倫廷派", "valentinianos"),
                      ("特土良論基督的肉身", "carne"),
                      ("特土良論肉身復活", "resurrectione"),
                      ("特土良駁普拉克西亞斯", "praxean"),
                      ("特土良蝎傷解毒劑", "scorpiace"),
                      ("特土良駁諸異端附錄", "haereses"),
                      ("特土良論悔改", "paen"),
                      ("特土良論洗禮", "baptismo"),
                      ("特土良論禱告", "oratione"),
                      ("特土良致殉道者", "martyres"),
                      ("特土良論忍耐", "patientia"),
                  )],
    },
    "anf4-latin": {
        "label": "ANF 第四卷的拉丁篇（特土良後期著作＋密努修＋科摩狄安）",
        "ebook_id": "904661d3-16fc-4f37-bb04-f7c4aa7671e9",
        "lang": "la",
        "mode": "roman",
        "source": "The Latin Library（公有領域）",
        # 🚨 同一冊的俄利根八卷《駁塞爾蘇斯》與《論原理》是希臘文，要走 PG 掃描本
        #    的 OCR（見 fathers_pg_ocr.py），這裡只收拉丁的部分。
        # 🚨 兩部拉丁原文有、卻對不起來，先不收：
        #    ·《論逼迫中逃避》—— 站上那一整部塞在單一段落裡（465 個段落），
        #      一個「第N章」標題都沒有，我方沒有錨點可用。要收得先重新分章。
        #    ·科摩狄安《教誨集》—— 拉丁本（commodianus2）的每首詩只有詩題沒有
        #      編號，而中譯用 ANF 的章號。兩邊沒有共同的鍵，只能靠第幾首的次序
        #      硬對，那是另一種對齊機制。
        "parts": [
                      ("特土良《論婦女裝飾》", "https://www.thelatinlibrary.com/tertullian/tertullian.cultu1.shtml"),
                      ("特土良《論婦女裝飾》", "https://www.thelatinlibrary.com/tertullian/tertullian.cultu2.shtml"),
                      ("特土良《致妻書》", "https://www.thelatinlibrary.com/tertullian/tertullian.uxor1.shtml"),
                      ("特土良《致妻書》", "https://www.thelatinlibrary.com/tertullian/tertullian.uxor2.shtml"),
                      ("特土良《論貞女蒙頭》", "https://www.thelatinlibrary.com/tertullian/tertullian.virginibus.shtml"),
                      ("特土良《勸貞潔書》", "https://www.thelatinlibrary.com/tertullian/tertullian.castitatis.shtml"),
                      ("特土良《論獨婚》", "https://www.thelatinlibrary.com/tertullian/tertullian.monog.shtml"),
                      ("特土良《論貞操》", "https://www.thelatinlibrary.com/tertullian/tertullian.pudicitia.shtml"),
                      ("特土良《論禁食》", "https://www.thelatinlibrary.com/tertullian/tertullian.ieiunio.shtml"),
                      ("特土良《論披袍》", "https://www.thelatinlibrary.com/tertullian/tertullian.pallio.shtml"),
                      ("密努修《屋大維對話錄》", "https://www.thelatinlibrary.com/minucius.html"),
        ],
    },
    "anf1-greek": {
        "label": "ANF 第一卷的希臘原典（使徒教父＋猶斯定）",
        "ebook_id": "c98d358d-7066-4691-a896-b7232707b0db",
        "lang": "grc",
        "mode": "tei",
        "source": "Open Greek and Latin · First1KGreek（TEI，CC BY-SA）",
        # 🚨 愛任紐《駁異端》不在這裡：希臘文只存殘篇，完整本是拉丁譯本
        #    （PG 7）。硬拿 tlg1447 去配會讓五卷大部分留白而看不出原因。
        # 網址後面的 #N 是伊格那丟七封真書在同一個 TEI 檔裡的 epistle 序號。
        "parts": [
                      ("克勉致哥林多人前書", "https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/data/tlg1271/tlg001/tlg1271.tlg001.1st1K-grc1.xml"),
                      ("巴拿巴書信", "https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/data/tlg1216/tlg001/tlg1216.tlg001.opp-grc1.xml"),
                      ("致丟格那妥書", "https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/data/tlg0646/tlg004/tlg0646.tlg004.1st1K-grc1.xml"),
                      ("坡旅甲致腓立比人書", "https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/data/tlg1622/tlg001/tlg1622.tlg001.1st1K-grc1.xml"),
                      ("猶斯定第一護教辭", "https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/data/tlg0645/tlg001/tlg0645.tlg001.1st1K-grc1.xml"),
                      ("猶斯定第二護教辭", "https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/data/tlg0645/tlg002/tlg0645.tlg002.perseus-grc2.xml"),
                      ("與特里弗的對話", "https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/data/tlg0645/tlg003/tlg0645.tlg003.perseus-grc2.xml"),
                      ("依納爵致以弗所人書", "https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/data/tlg1443/tlg001/tlg1443.tlg001.1st1K-grc1.xml#1"),
                      ("依納爵致馬內夏人書", "https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/data/tlg1443/tlg001/tlg1443.tlg001.1st1K-grc1.xml#2"),
                      ("依納爵致特拉勒人書", "https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/data/tlg1443/tlg001/tlg1443.tlg001.1st1K-grc1.xml#3"),
                      ("依納爵致羅馬人書", "https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/data/tlg1443/tlg001/tlg1443.tlg001.1st1K-grc1.xml#4"),
                      ("依納爵致非拉鐵非人書", "https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/data/tlg1443/tlg001/tlg1443.tlg001.1st1K-grc1.xml#5"),
                      ("依納爵致士每拿人書", "https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/data/tlg1443/tlg001/tlg1443.tlg001.1st1K-grc1.xml#6"),
                      ("依納爵致坡旅甲書", "https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/data/tlg1443/tlg001/tlg1443.tlg001.1st1K-grc1.xml#7"),
        ],
    },
    "anf4-origen": {
        "label": "俄利根《駁塞爾蘇斯》（ANF 第四卷）",
        "ebook_id": "904661d3-16fc-4f37-bb04-f7c4aa7671e9",
        "lang": "grc",
        "mode": "tei",
        "source": "Open Greek and Latin · First1KGreek（TEI，CC BY-SA）",
        # 八卷共用一個 TEI 檔，卷次由 TEI 的 book 層與我方的「卷一…卷八」對上。
        # 站上那一冊的拉丁篇另立 anf4-latin；兩者寫同一個 JSONL，先後跑都可以，
        # build_sources 會保留已存在的語言欄。
        # 🚨 同一冊的《論原理》不收：希臘文只存 Philocalia 裡的殘篇，完整本是
        #    盧菲努的拉丁譯（PG 11），First1KGreek 沒有。硬拿殘篇去配會讓四卷
        #    大部分留白而看不出原因。
        "prefix": "俄利根《駁塞爾蘇斯》",
        "urls": ["https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/data/tlg2042/tlg001/tlg2042.tlg001.perseus-grc1.xml"],
    },
    "eusebius-church-history": {
        "label": "優西比烏《教會史》（NPNF2 第一卷）",
        "ebook_id": "91ff3a5e-cd1f-4ab4-acb7-70cb7a80c4b9",
        "prefix": "教會史",
        "lang": "grc",
        "mode": "tei",
        "source": "Perseus canonical-greekLit（TEI，公有領域）",
        # 🚨 取源用 Perseus 不用 First1KGreek：後者那份 grc 只有 4,815 個希臘
        #    字元（殘本），而且同一個目錄裡還混著英譯檔，盲取第一個 xml 會拿到
        #    英文。Perseus 這份 54.7 萬字元、十卷 13/27/39/30/29/46/33/18/11/9
        #    章，與《教會史》已知結構相符。
        # 🚨 站上的「卷N」不等於原典的卷N，而且位移不是固定的：卷一是譯者導論，
        #    卷十是附錄〈巴勒斯坦的殉道者〉（不是第九卷），卷十三是補充註釋。
        #    用固定偏移的話最後兩卷會配到別卷的希臘文而照樣顯示滿分，所以逐卷
        #    明列。沒列到的（1、10、13）不收。
        "book_map": {2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7, 9: 8, 11: 9, 12: 10},
        "urls": ["https://raw.githubusercontent.com/PerseusDL/canonical-greekLit/master/data/tlg2018/tlg002/tlg2018.tlg002.perseus-grc2.xml"],
    },
    "eusebius-constantine": {
        "label": "優西比烏《君士坦丁傳》與兩篇頌辭（NPNF2 第一卷）",
        "ebook_id": "91ff3a5e-cd1f-4ab4-acb7-70cb7a80c4b9",
        "lang": "grc",
        "mode": "tei",
        "source": "Open Greek and Latin · First1KGreek（TEI，CC BY-SA）",
        # 與 eusebius-church-history 同一本 ebook，分開登記是因為《教會史》的
        # 卷次要另外對照（見那一條的 book_map），這三部則是直接對應。
        "parts": [
                      ("君士坦丁傳", "https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/data/tlg2018/tlg020/tlg2018.tlg020.1st1K-grc1.xml"),
                      ("君士坦丁御前演說辭", "https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/data/tlg2018/tlg021/tlg2018.tlg021.1st1K-grc1.xml"),
                      ("優西比烏讚辭", "https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/data/tlg2018/tlg022/tlg2018.tlg022.1st1K-grc1.xml"),
        ],
    },
    "athanasius-orations": {
        "label": "亞他那修《駁亞流派講辭》四篇（NPNF2 第四卷）",
        "ebook_id": "e01917ab-7429-41a0-9859-eddad413ef60",
        "lang": "grc",
        "mode": "tei",
        "anchor": "section",
        "source": "Open Greek and Latin · First1KGreek（TEI，CC BY-SA）",
        # 這一部整卷沒有可用的章標題，錨點是連續節號——而四篇講辭的節號各自從一
        # 起算（64/82/67/36），靠 book_of() 的回頭偵測分篇。
        # 🚨 TEI 那邊把節叫做 chapter（章數 64/82/67/36 正好等於我方的節號上限），
        #    層級名不同但編號是同一套。
        "parts": [
                      ("駁亞流派講辭", "https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/data/tlg2035/tlg130/tlg2035.tlg130.1st1K-grc1.xml"),
                      ("駁亞流派講辭", "https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/data/tlg2035/tlg131/tlg2035.tlg131.1st1K-grc1.xml"),
                      ("駁亞流派講辭", "https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/data/tlg2035/tlg132/tlg2035.tlg132.1st1K-grc1.xml"),
                      ("駁亞流派講辭", "https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/data/tlg2035/tlg117/tlg2035.tlg117.1st1K-grc1.xml"),
        ],
    },
    "hippolytus-refutatio": {
        "label": "希波呂圖《駁諸異端》（ANF 第五卷）",
        "ebook_id": "0e08c662-540b-4186-b250-9bca0cfe1002",
        "prefix": "希波呂圖《駁諸異端》",
        "lang": "grc",
        "mode": "tei",
        "source": "Open Greek and Latin · First1KGreek（TEI，CC BY-SA）",
        # 卷次直接對應，不需 book_map：TEI 與我方都是卷 1、4–10（第二、三卷本來
        # 就佚失），章數 27/51/28/55/38/20/31/34 與我方的章標題數相符。
        # 🚨 同一個目錄有 opp-grc1 與 perseus-grc1 兩份；取希臘字元較多的 opp
        #    （45.7 萬 vs 36.4 萬）。
        # 🚨 同冊的「居普良 論述集」不收：那是把十二部各自獨立的著作壓成一個
        #    前綴（196 章），分不出哪一章屬哪一部。
        "urls": ["https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/data/tlg2115/tlg060/tlg2115.tlg060.opp-grc1.xml"],
    },
    "arnobius-adversus-nationes": {
        "label": "阿諾比烏《駁異教徒》七卷（ANF 第六卷）",
        "ebook_id": "dffaae40-e088-41c1-ab7f-9b96f9249661",
        "lang": "la",
        "mode": "dotted",
        "anchor": "both",
        "source": "The Latin Library（公有領域）",
        # 🚨 行標是「章.節 正文」寫在行首（1.1 Quoniam…），不獨佔一行，所以要走
        #    parse_dotted_chapters；用 parse_chapter_markers 七卷全部回 0 章，而
        #    腳本只會說「命中 0」，看起來像取源壞掉。
        "parts": [
            ("阿諾比烏《駁異教徒》", "https://www.thelatinlibrary.com/arnobius/arnobius1.shtml"),
            ("阿諾比烏《駁異教徒》", "https://www.thelatinlibrary.com/arnobius/arnobius2.shtml"),
            ("阿諾比烏《駁異教徒》", "https://www.thelatinlibrary.com/arnobius/arnobius3.shtml"),
            ("阿諾比烏《駁異教徒》", "https://www.thelatinlibrary.com/arnobius/arnobius4.shtml"),
            ("阿諾比烏《駁異教徒》", "https://www.thelatinlibrary.com/arnobius/arnobius5.shtml"),
            ("阿諾比烏《駁異教徒》", "https://www.thelatinlibrary.com/arnobius/arnobius6.shtml"),
            ("阿諾比烏《駁異教徒》", "https://www.thelatinlibrary.com/arnobius/arnobius7.shtml"),
        ],
    },
    "methodius-symposium": {
        "label": "美多德《十處女宴飲集》（ANF 第六卷）",
        "ebook_id": "dffaae40-e088-41c1-ab7f-9b96f9249661",
        "prefix": "美多德《十處女宴飲集／論童貞》",
        "lang": "grc",
        "mode": "tei",
        "anchor": "both",
        "source": "Open Greek and Latin · First1KGreek（TEI，CC BY-SA）",
        # 序＋十一篇講辭各自從第一章重來，站上卻是整部連續的第1-85章——與阿諾
        # 比烏同一種形狀，靠 resolve_continuous() 反推是哪一篇。
        "urls": ["https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/data/tlg2959/tlg001/tlg2959.tlg001.opp-grc1.xml"],
    },
    "basil-letters": {
        "label": "巴西流《書信集》（NPNF2 第八卷）",
        "ebook_id": "3c48472c-fbca-48fb-9db1-ca5a08827ef3",
        "prefix": "書信",
        "lang": "grc",
        "mode": "letter",
        "source": "Perseus canonical-greekLit（TEI，公有領域）",
        # 這一部沒有章可以對，只有「第幾封信的第幾段」。原文的分段不帶編號，
        # 所以順序就是唯一的鍵——段數對不上就整封空著，見 align_letter()。
        # 《論聖靈》三十章與《六日創世講道》九講的希臘本兩個 TEI 庫都沒有
        # （tlg2040 只有 tlg002、tlg004），要補得走 Migne PG 29/32 自家 OCR。
        "urls": ["https://raw.githubusercontent.com/PerseusDL/canonical-greekLit/master/data/tlg2040/tlg004/tlg2040.tlg004.perseus-grc2.xml"],
    },
    "sulpicius-chronica": {
        "label": "蘇皮丘‧塞維魯《編年史》兩卷（NPNF2 第十一卷）",
        "ebook_id": "24c53ede-8787-442e-a3ba-0cd55d0effac",
        "prefix": "蘇皮修《神聖歷史》",
        "lang": "la",
        "mode": "dotted",
        "marker": "paren",
        "source": "The Latin Library（公有領域）",
        # 行標是「章 (節) 正文」——章號在行首、節號用括號夾、同行接正文。
        # 中譯是整部連續的第1-106章，原典兩卷各自 1–54、1–51。
        "urls": ["https://www.thelatinlibrary.com/sulpiciusseveruschron1.html",
                 "https://www.thelatinlibrary.com/sulpiciusseveruschron2.html"],
    },
    "sulpicius-vita-martini": {
        "label": "蘇皮丘‧塞維魯《聖瑪爾定傳》（NPNF2 第十一卷）",
        "ebook_id": "24c53ede-8787-442e-a3ba-0cd55d0effac",
        "prefix": "蘇皮修《聖瑪爾定傳》",
        "lang": "la",
        "mode": "dotted",
        "marker": "paren",
        "source": "The Latin Library（公有領域）",
        # 站上宣告 31 章，原典 27 章——多出來的是序言與兩封書信，不是缺章。
        "urls": ["https://www.thelatinlibrary.com/sulpiciusseverusmartin.html"],
    },
    "vincent-commonitorium": {
        "label": "勒蘭的文森《勸誡錄》（NPNF2 第十一卷）",
        "ebook_id": "24c53ede-8787-442e-a3ba-0cd55d0effac",
        "prefix": "勒蘭的文生《勸誡錄》",
        "lang": "la",
        "mode": "roman",
        "source": "The Latin Library（公有領域）",
        "urls": ["https://www.thelatinlibrary.com/vicentius.html"],
    },
    "lactantius-de-mortibus": {
        "label": "拉克坦提烏《論逼迫者之死》（ANF 第七卷）",
        "ebook_id": "75d8aae0-7431-4be9-baee-c57d26599653",
        "prefix": "拉克坦提烏《論逼迫者之死》",
        "lang": "la",
        "mode": "chapter",
        "source": "The Latin Library（公有領域）",
        # 行標是方括號夾阿拉伯數字（`[1] Audivit dominus…`），不是羅馬數字。
        "urls": ["https://www.thelatinlibrary.com/lactantius/demort.shtml"],
    },
    "novatian-de-trinitate": {
        "label": "諾瓦提安《論三位一體》（ANF 第五卷）",
        "ebook_id": "0e08c662-540b-4186-b250-9bca0cfe1002",
        "prefix": "諾瓦提安《論三位一體》",
        "lang": "la",
        "mode": "roman",
        "source": "The Latin Library（公有領域）",
        "urls": ["https://www.thelatinlibrary.com/novatian.html"],
    },
    "lactantius-divinae-institutiones": {
        "label": "拉克坦提烏《神學原理》卷一（ANF 第七卷）",
        "ebook_id": "75d8aae0-7431-4be9-baee-c57d26599653",
        "prefix": "拉克坦提烏《神學原理》",
        "lang": "la",
        "mode": "roman",
        "source": "The Latin Library（公有領域）",
        # 🚨 那邊只收了七卷中的第一卷（23 章），而站上是七卷連號的第1-188章、
        #    中譯逐卷重編。只有卷一那 23 章填得上，其餘照實空著——別讓它把每一
        #    卷的第 N 章都配成卷一第 N 章（align_part 有一道專門擋這個的閘）。
        "urls": ["https://www.thelatinlibrary.com/lactantius/divinst1.shtml"],
    },
    "augustine-de-trinitate": {
        "label": "奧古斯丁《論三位一體》十五卷（NPNF1 第三卷）",
        "ebook_id": "d7f66759-3fa9-4633-abde-87003cdbcc06",
        "prefix": "奧古斯丁教義論集",
        "site_book": 1,
        "lang": "la",
        "mode": "chapter",
        "marker": "roman-section",
        "source": "The Latin Library（公有領域）",
        # 站上「奧古斯丁教義論集」一個前綴壓了七部著作，用卷一…卷七分開；卷一
        # 就是《論三位一體》十五卷。那個「卷」是第幾部著作，不是原典卷次，所以
        # site_book 挑完之後要把它拿掉。
        "urls": ["https://www.thelatinlibrary.com/augustine/trin1.shtml",
                 "https://www.thelatinlibrary.com/augustine/trin2.shtml",
                 "https://www.thelatinlibrary.com/augustine/trin3.shtml",
                 "https://www.thelatinlibrary.com/augustine/trin4.shtml",
                 "https://www.thelatinlibrary.com/augustine/trin5.shtml",
                 "https://www.thelatinlibrary.com/augustine/trin6.shtml",
                 "https://www.thelatinlibrary.com/augustine/trin7.shtml",
                 "https://www.thelatinlibrary.com/augustine/trin8.shtml",
                 "https://www.thelatinlibrary.com/augustine/trin9.shtml",
                 "https://www.thelatinlibrary.com/augustine/trin10.shtml",
                 "https://www.thelatinlibrary.com/augustine/trin11.shtml",
                 "https://www.thelatinlibrary.com/augustine/trin12.shtml",
                 "https://www.thelatinlibrary.com/augustine/trin13.shtml",
                 "https://www.thelatinlibrary.com/augustine/trin14.shtml",
                 "https://www.thelatinlibrary.com/augustine/trin15.shtml"],
    },
}

# 🚨 《論三位一體》拉丁原文有（thelatinlibrary.com/augustine/trin1–15），但站上那一冊
#    （NPNF1 Vol 3, d7f66759-3fa9-4633-abde-87003cdbcc06）把它和《創世記字義解》等
#    併成一個「奧古斯丁教義論集」，共用同一組卷號，從 chapter_path 分不出哪一卷屬
#    哪一部。硬接會把《創世記字義解》的中譯配上《論三位一體》的拉丁文——三欄看起來
#    齊，內容卻是兩部不同的書。要收這一部，得先把那一冊重新分篇。


def load_greek_ledger(path: Path) -> dict[tuple[int | None, int], str]:
    """讀 fathers_pg_ocr.py 的帳本，按頁與欄的閱讀順序接稿，再切成 {(卷,節): 文字}。"""
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    # 🚨 同一個裁切可能有兩列：帳本是 append-only，兩個 OCR 程序同時跑就會各寫一
    #    次（實際發生過，4 個裁切重複）。不去重的話那幾塊的希臘文會被接兩遍，讀
    #    起來是同一段話講了兩次——通順、看不出錯。後寫的那筆勝出。
    rows = FO.dedupe_ledger(rows)
    order = {"c0h0": 0, "c0h1": 1, "c1h0": 2, "c1h1": 3}
    rows.sort(key=lambda r: (r["page"], order.get(r["crop"], 9)))
    text = FO.join_crops([r["text"] for r in rows])
    pages = len({r["page"] for r in rows})
    print(f"  OCR 帳本 {len(rows)} 塊 / {pages} 頁 → {len(text)} 字")
    return FO.parse_greek_sections(text)


def fetch_original(spec: dict) -> tuple[dict, dict]:
    """抓原典。回傳 (逐章, 逐節, 逐卷逐章)。

    第三項只有多卷的 roman 模式用得到：原典每卷的章號都從一起算，而中譯有兩種
    習慣——《駁馬吉安》整部連續編號 1–145，《論婦女裝飾》卻每卷從第一章重來。
    機器分不出是哪一種，所以兩種鍵都備好，對齊時各試一次、取命中高的那個。
    """
    if spec["mode"] == "greek":
        paragraphs = load_greek_ledger(Path(spec["ledger"]))
        return {}, paragraphs, {}
    if spec["mode"] == "letter":
        s = requests.Session()
        s.headers["User-Agent"] = "Mozilla/5.0 (know-graph-lab fathers-original)"
        r = s.get(spec["urls"][0], timeout=180)
        r.raise_for_status()
        letters = FO.parse_tei_letters(r.text)
        print(f"  抓 {spec['urls'][0].rsplit('/', 1)[-1]:22} → {len(letters)} 封")
        return {}, letters, {}
    s = requests.Session()
    s.headers["User-Agent"] = "Mozilla/5.0 (know-graph-lab fathers-original)"
    chapters: dict[tuple[int | None, int], str] = {}
    by_book: dict[tuple[int | None, int], str] = {}
    sections: dict[tuple[int | None, int, int | None], str] = {}
    unit = "節" if spec["mode"] == "paragraph" else "章"
    for i, url in enumerate(spec["urls"], 1):
        # 伊格那丟七封真書共用一個 TEI 檔，網址後面的 #N 是 epistle 序號
        url, _, epistle = url.partition("#")
        r = s.get(url, timeout=90)
        if r.status_code != 200:
            # 一個取源壞掉不該讓整輪中止——其餘幾十部照樣做得完，缺的那一部會在
            # 命中率那一行看得出來。
            print(f"  ⚠ 取源 {r.status_code}：{url}")
            continue
        text = FO.strip_html(r.text)
        shown = None      # got 有時會被清空（見 tei 分支），印出來的數目要另外記
        if spec["mode"] == "paragraph":
            got = FO.parse_numbered_text(text, default_book=i)
            sections.update(got)
        elif spec["mode"] == "tei":
            got = FO.parse_tei_chapters(r.text, epistle or None)
            # 🚨 一部著作分成好幾個 TEI 檔（亞他那修四篇《駁亞流派講辭》各一檔）
            #    而檔內沒有 book 那一層時，四篇的章號都是 1.. 會互相覆蓋。用網址
            #    序號當卷次補上去。
            if len(spec["urls"]) > 1 and all(k[0] is None for k in got):
                by_book.update({(i, k[1]): v for k, v in got.items()})
                # got 清空是為了不讓四篇的章號互相覆蓋，但下面印的是 len(got)，
                # 清空後會印「0 章」，看起來像取源壞掉。
                shown = len(got)
                got = {}
            elif any(k[0] is not None for k in got):
                # TEI 有 book 那一層，而中譯的 chapter_path 不一定跟著分卷：美多德
                # 《十處女宴飲集》站上是整部連續的第1-85章，內文編號卻逐篇重來。
                # 兩種鍵都放進去，align_part 會自己挑分數高的那一種。
                by_book.update(got)
                bases = cumulative_bases(got)
                chapters.update({(None, k[1] + bases[k[0]]): v
                                 for k, v in got.items()})
            chapters.update(got)

        elif spec["mode"] == "dotted":
            # 行標是「章.節 正文」寫在行首、不獨佔一行。原典每卷章號從一起算，
            # 而中譯是整部連續編號，所以與 roman 一樣累計接續。
            got = FO.parse_dotted_chapters(
                text, mark=(FO.PAREN_MARK if spec.get("marker") == "paren"
                            else FO.DOTTED_MARK))
            base = max((k[1] for k in chapters), default=0)
            by_book.update({(i, k[1]): v for k, v in got.items()})
            chapters.update({(None, k[1] + base): v for k, v in got.items()})
            print(f"  抓 {url.rsplit('/', 1)[-1]:22} → {len(got)} 章")
            continue
        elif spec["mode"] == "roman":
            got = FO.parse_chapter_markers(text)
            # 多卷的著作（《駁馬吉安》五卷、《致萬民》兩卷）原典每卷的章號都從
            # 一重新起算，但站上的中譯是整部連續編號（駁馬吉安 29+29+24+43+20
            # ＝145，正好是中譯的 1–145）。所以第二卷起要接著前面累計的章數。
            base = max((k[1] for k in chapters), default=0)
            by_book.update({(i, k[1]): v for k, v in got.items()})
            got = {(None, k[1] + base): v for k, v in got.items()}
            chapters.update(got)
        elif spec.get("marker") == "roman-section":
            # 每一卷的章號都從 I 重新起算，而中譯是整部連續編號，所以累計接續；
            # 逐卷的鍵也留著，align_part 會挑分數高的。
            got = FO.parse_roman_bracketed_chapters(text)
            by_book.update({(i, k[1]): v for k, v in got.items()})
            base = max((k[1] for k in chapters), default=0)
            chapters.update({(None, k[1] + base): v for k, v in got.items()})
        else:
            # 單卷著作要鍵成 (None, 章)，不然 chapter_path 沒有卷次的那些查不到。
            got = FO.parse_bracketed_chapters(
                text, i if len(spec["urls"]) > 1 else None)
            chapters.update(got)
        print(f"  抓 {url.rsplit('/', 1)[-1]:16} → "
              f"{len(got) if shown is None else shown} {unit}")
    if spec["mode"] == "paragraph":
        chapters = FO.by_chapter(sections)
    return chapters, FO.by_paragraph(sections), by_book


def load_chunks(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def _both_anchors(body):
    """章標題與節號合併。阿諾比烏的中譯多半只寫「17. …」，偶爾才寫「# 第十七章」；
    只取其中一種會漏掉另一種（章標題 44 vs 節號 283）。同一段兩種都中時以章標題為準。"""
    out = dict(FO.section_numbers(body))
    # 同一章兩種寫法都在時（「# 第五章」後面接「5. 你們這無知的人哪…」），只留
    # 正文那一段；兩段都給會讓同一段拉丁文重複出現在兩列。
    taken = set(out.values())
    for i, n in FO.chapter_headings(body):
        if n not in taken:
            out[i] = n
    return sorted(out.items())


ANCHORS = {"section": FO.section_numbers, "both": _both_anchors}


def cumulative_bases(by_book: dict) -> dict[int, int]:
    """各卷在「整部連續編號」裡的起算基底。第三卷的基底＝第一、二卷的章數和。"""
    sizes: dict[int, int] = {}
    for b, n in by_book:
        sizes[b] = max(sizes.get(b, 0), n)
    bases, run = {}, 0
    for b in sorted(sizes):
        bases[b] = run
        run += sizes[b]
    return bases


def resolve_continuous(n: int, sp, bases: dict[int, int]) -> int | None:
    """逐卷重編的章號 n 落在這一段宣告的章範圍內時，反推它的整部連續號。

    各卷基底相差都大於一段涵蓋的章數，所以答案唯一。不唯一或無解就回 None——
    寧可少對一章，也不要猜。
    """
    fit = [b for b, base in bases.items() if sp.first <= n + base <= sp.last]
    return n + bases[fit[0]] if len(fit) == 1 else None


def align_part(chunks, spans, chapters, by_book, extract=None):
    """對整部做逐章對齊，兩種編號法各試一次，取命中高的那個。

    多卷著作的中譯有兩種編號習慣，同一冊裡都有：《駁馬吉安》五卷整部連續編號
    1–145（→ 用累計後的 chapters），《論婦女裝飾》兩卷每卷從第一章重來（→ 用
    逐卷的 by_book，卷次靠章號回頭偵測）。機器分不出是哪一種，所以兩種都跑，
    看誰命中多。猜錯的那一種通常是 0 命中，差距非常明顯。
    """
    seq = []
    for c in chunks:
        sp = spans.get(c["chunk_index"])
        if not sp:
            continue
        body = FO.split_body(c.get("content") or "")
        for i, n in (extract or FO.chapter_headings)(body):
            seq.append((c["chunk_index"], i, n, sp))
    if not seq:
        return {}, 0, 0

    flat: dict[int, list] = {}
    n_flat = 0
    for ci, i, n, sp in seq:
        book = sp.book
        # 🚨 卷次一定要帶進查表。少了它，《上帝之城》卷十三的第一章會拿到卷一
        #    第一章的拉丁文——命中率照樣很高，三欄照樣排得整整齊齊，內容卻是別
        #    一卷的。只有在完全沒有卷這一層時（單卷著作）才退回 (None, n)。
        text = chapters.get((book, n)) if book is not None else None
        if text is None:
            text = chapters.get((None, n))
        if text:
            flat.setdefault(ci, []).append((i, text))
            n_flat += 1

    # 🚨 命中率高不代表配對正確。阿諾比烏的中譯 chapter_path 是整部連續號
    #    （第71-80章），行內編號卻是逐卷重編的（第二卷第六章寫成「6.」）——直接
    #    拿「6」查整部第 6 章，七卷全部查得到，報 100%，內容卻全是第一卷的。
    #    分得出來的是「編號整體遞不遞增」：整部連續編號的著作（《駁馬吉安》五卷
    #    連續 1–145）幾乎全串遞增，逐卷重編的則每換一卷掉回小數字，最長遞增子序
    #    列只剩最長那一卷。不能只數「掉了幾次」——《駁黑摩根》正文裡一個誤讀的
    #    「21.」就掉兩次，那本其實是乾淨的 1–45。chapter_path 自己帶卷次時不算：
    #    那時 flat 查的是 (卷, 章)，本來就對。
    #    而且只有分卷的著作才談得上「逐卷重編」。依納爵那幾封書信的編號會從頭再走
    #    一次（短、長兩種抄本各編一次號：6…12、1…6），但兩次走的是同一封信，flat
    #    給的是對的。
    ns = [x[2] for x in seq]
    lis = len(FO._longest_increasing([(0, 0, n) for n in ns]))
    if (len({b for b, _ in by_book}) > 1 and lis < len(ns) * 0.6
            and all(x[3].book is None for x in seq)):
        n_flat = 0

    # 🚨 另一種同樣安靜的錯配：原典電子本只收了整部著作的第一卷。拉克坦提烏
    #    《神學原理》站上是七卷連在一起的第1-188章、中譯逐卷重編（1–23、1–20、
    #    1–30…），而 The Latin Library 只有第一卷 23 章——每一卷的第 5 章都會配到
    #    第一卷第 5 章，七卷份的錯配，而且上面那條規則擋不住（原典只有一卷）。
    #    站上宣告的章數遠超過原典的章數就是這種情形。
    declared = max((x[3].last for x in seq), default=0)
    largest = max((k[1] for k in chapters), default=0)
    if largest and declared > largest * 1.5 and all(x[3].book is None for x in seq):
        n_flat = 0

    # 第三種：chapter_path 是整部連續號、行內編號卻逐卷重編（阿諾比烏《駁異教徒》
    # 七卷，中譯標「第71-80章」而內文寫「6.」）。用宣告的章範圍反推是哪一卷——
    # 各卷累計基底相差都大於一段的章數，所以答案唯一；不唯一或無解就不算命中，
    # 不猜。只在 chapter_path 沒有卷次時才試，否則《上帝之城》卷十三會被算成卷一。
    # 第四種：中譯每卷從第一節重編，而 chapter_path 連個範圍都給不出來（亞他那修
    # 《駁亞流派講辭》的「第1章…第35章」只是分段序號）。原典自己知道每卷幾節，
    # 拿去切最省事也最穩，見 assign_books()。
    sizes_by_book = {}
    for b, n in by_book:
        sizes_by_book[b] = max(sizes_by_book.get(b, 0), n)
    order = sorted(sizes_by_book)
    fit: dict[int, list] = {}
    n_fit = 0
    if len(order) > 1 and all(x[3].book is None for x in seq):
        by_chunk: dict[int, list] = {}
        for ci, i, n, _ in seq:
            by_chunk.setdefault(ci, []).append((i, n))
        cis = list(by_chunk)
        got = FO.assign_books([[n for _, n in by_chunk[ci]] for ci in cis],
                              [sizes_by_book[b] for b in order])
        for ci, (bk, used) in zip(cis, got):
            if bk is None:
                continue
            for pos in used:
                i, n = by_chunk[ci][pos]
                text = by_book.get((order[bk - 1], n))
                if text:
                    fit.setdefault(ci, []).append((i, text))
                    n_fit += 1

    bases = cumulative_bases(by_book)
    off: dict[int, list] = {}
    n_off = 0
    if bases and all(x[3].book is None for x in seq):
        for ci, i, n, sp in seq:
            cont = resolve_continuous(n, sp, bases)
            text = chapters.get((None, cont)) if cont else None
            if text:
                off.setdefault(ci, []).append((i, text))
                n_off += 1

    per: dict[int, list] = {}
    n_per = 0
    for (ci, i, n, _), b in zip(seq, FO.book_of([x[2] for x in seq])):
        text = by_book.get((b, n))
        if text:
            per.setdefault(ci, []).append((i, text))
            n_per += 1

    if os.environ.get("ALIGN_DEBUG"):
        print(f"    [debug] seq={len(seq)} flat={n_flat} "
              f"lis={lis}/{len(ns)} per={n_per} off={n_off} fit={n_fit} "
              f"spans={[ (x[0], x[3].book, x[3].first, x[3].last) for x in seq[:3] ]} "
              f"ns={[x[2] for x in seq[:8]]}")
    hits, n_hit = max(((flat, n_flat), (per, n_per), (off, n_off), (fit, n_fit)),
                      key=lambda x: x[1])
    return hits, n_hit, len(seq)


def parts_of(spec: dict) -> list[tuple[str, dict]]:
    """把 spec 正規化成 [(chapter_path 前綴, 該部的 spec)]。單一著作就是一部。

    同一個前綴登記多個網址＝那一部原典分成好幾卷（《駁馬吉安》五卷）。這裡要
    把它們併成同一部再交出去——拆成好幾部的話，每一卷的章號都會從一重新起算，
    而站上的中譯是整部連續編號，第二卷起就全部對不上。
    """
    if "parts" not in spec:
        return [(spec["prefix"], spec)]
    grouped: dict[str, list[str]] = {}
    for prefix, url in spec["parts"]:
        grouped.setdefault(prefix, []).append(url)
    return [(prefix, {**spec, "prefix": prefix, "urls": urls})
            for prefix, urls in grouped.items()]


def spans_for(chunks: list[dict], part: dict) -> dict[int, FO.Span]:
    out: dict[int, FO.Span] = {}
    for c in chunks:
        cp = c.get("chapter_path") or ""
        if FO.work_name(cp) != part["prefix"]:
            continue
        # 「卷二」整卷一段時要餵該卷章數才解得出範圍
        book_hint = None
        m = FO.CHAPTER_PATH.search(cp)
        if m and m.group(2) is None:
            book_hint = (part.get("chapters") or {}).get(FO.zh_numeral(m.group(1)))
        if part.get("site_book"):
            # 站上把好幾部著作壓成一個前綴、用「卷N」分開（奧古斯丁教義論集的
            # 卷一是《論三位一體》、卷二是《信望愛手冊》…）。挑出那一卷，並把卷次
            # 拿掉——它是「第幾部著作」，不是原典的卷次，留著會讓查表用錯鍵。
            sp0 = FO.parse_chapter_path(cp)
            if not sp0 or sp0.book != part["site_book"]:
                continue
            out[c["chunk_index"]] = FO.Span(None, sp0.first, sp0.last)
            continue
        if part["mode"] == "letter":
            m = FO.LETTER_PATH.search(cp)
            if m:
                out[c["chunk_index"]] = FO.Span(int(m.group(1)), 1, 1)
            continue
        s = FO.parse_chapter_path(cp, chapters_in_book=book_hint)
        if s and part.get("book_map"):
            # 站上的卷次與原典卷次不是固定偏移（優西比烏《教會史》的卷一是譯者
            # 導論、卷十是附錄）。逐卷明列，沒列到的不收——比錯配安全。
            mapped = part["book_map"].get(s.book)
            if mapped is None:
                continue
            s = FO.Span(mapped, s.first, s.last)
        if s and part["mode"] == "greek":
            # 這一部的 chapter_path 是「論司祭職 第3章」，第 N 章其實是第 N-2 卷
            s = FO.Span(s.first + part["book_from_chapter"], s.first, s.last)
            if s.book < 1:
                continue
        if s is None and part["mode"] in ("chapter", "roman", "tei"):
            # 逐章模式的錨點是內文裡的「第N章」標題，不是 chapter_path 的後綴。
            # 只用一段收完的著作（依納爵致羅馬人書、致坡旅甲書）路徑上沒有那個
            # 後綴，硬要它就會整部被跳過而毫無訊號。
            s = FO.Span(None, 1, 1)
        if s:
            out[c["chunk_index"]] = s
    return out


def coverage_for(chunks: list[dict], spans: dict[int, FO.Span], part: dict,
                 chapters: dict, paragraphs: dict, by_book: dict | None = None) -> list:
    """依模式挑對的比對層級。

    🚨 章模式不可以拿 chapter_path 的範圍標籤當「站上有哪些章」——標籤會湊整
       （該卷只到第 35 章，標籤照樣寫「第31-40章」），拿它比對會冒出一堆不存在的
       「多出章」，把真正的缺章淹掉。要數內文裡真的出現的章標題。
    """
    if part["mode"] == "letter":
        return []
    if part["mode"] == "greek":
        found = []
        for c in chunks:
            s = spans.get(c["chunk_index"])
            if not s:
                continue
            for p in FO.split_body(c.get("content") or ""):
                m = FO.LEADING_NO.match(p)
                if m:
                    found.append(FO.Span(s.book, int(m.group(1)), int(m.group(1))))
        return FO.coverage(found, {k: "x" for k in paragraphs})
    if part["mode"] in ("chapter", "roman", "tei", "dotted"):
        extract = ANCHORS.get(part.get("anchor"), FO.chapter_headings)
        bases = cumulative_bases(by_book or {})
        if len(bases) < 2:
            bases = {}
        found = []
        for c in chunks:
            s = spans.get(c["chunk_index"])
            if not s:
                continue
            for _, n in extract(FO.split_body(c.get("content") or "")):
                # 🚨 中譯逐卷重編、chapters 卻是整部連續號時要先換算。不換算的話
                #    報告會列出兩百多章根本不存在的「站上中譯沒有第 N 章」，把真正
                #    的缺口（原典電子本第七卷只收到第 34 章）淹掉。
                if bases and s.book is None:
                    cont = resolve_continuous(n, s, bases)
                    if cont:
                        found.append(FO.Span(None, cont, cont))
                    continue
                found.append(FO.Span(s.book, n, n))
        return FO.coverage(found, chapters)
    return FO.coverage(list(spans.values()), chapters)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True, choices=sorted(WORKS))
    ap.add_argument("--chunks-dir", default=None)
    ap.add_argument("--apply", action="store_true", help="寫回 JSONL（預設只驗不寫）")
    ap.add_argument("--only", help="只跑某一部（chapter_path 前綴），試跑用")
    a = ap.parse_args()

    spec = WORKS[a.work]
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"'))
    raw = a.chunks_dir or os.environ.get("EBOOK_CHUNKS_DIR") or ""
    # 🚨 別偷懶寫 Path(raw).is_dir()——Path("") 等於「.」，在 Windows 上是存在的，
    # 環境變數沒讀到時會安靜地把工作目錄當成 chunks 目錄，然後報「找不到檔案」。
    if not raw:
        print("EBOOK_CHUNKS_DIR 沒設（.env 讀不到？）")
        return 1
    chunks_dir = Path(raw)
    if not chunks_dir.is_dir():
        print(f"找不到 chunks 目錄 {chunks_dir}（Drive 沒掛？）")
        return 1
    path = chunks_dir / f"{spec['ebook_id']}.jsonl"
    if not path.exists():
        print(f"找不到 {path}")
        return 1

    parts = parts_of(spec)
    if a.only:
        parts = [x for x in parts if x[0] == a.only]
        if not parts:
            print(f"沒有前綴為「{a.only}」的部")
            return 1
    print(f"《{spec['label']}》 原文 {spec['lang']} ← {spec['source']}"
          f"（{'逐節' if spec['mode'] in ('paragraph', 'greek', 'letter') else '逐章'}對齊）"
          + (f"，共 {len(parts)} 部" if len(parts) > 1 else ""))

    chunks = load_chunks(path)
    cols: dict[int, list[str]] = {}
    hit_total = num_total = 0
    skipped: list[str] = []
    for prefix, part in parts:
        chapters, paragraphs, by_book = fetch_original(part)
        spans = spans_for(chunks, part)
        if not spans:
            print(f"  ⚠ 「{prefix}」站上找不到對應段落，跳過")
            continue
        bad = [c for c in coverage_for(chunks, spans, part, chapters, paragraphs, by_book)
               if not c.ok]
        note = ""
        for c in bad:
            bits = []
            if c.missing:
                bits.append(f"站上中譯沒有第 {c.missing} 章")
            if c.extra:
                # 這一側是原典電子本的缺口，不是我們的問題——civ18 那頁就從
                # [XXXI] 直接跳到 [XLVII]，中間 15 章根本沒收。分開講才不會
                # 誤判責任歸屬。
                bits.append(f"原典電子本沒有第 {c.extra} 章")
            note += "\n      ⚠ 卷 " + str(c.book) + "：" + "；".join(bits)

        hit = num = 0
        if part["mode"] == "letter":
            for c in chunks:
                sp = spans.get(c["chunk_index"])
                if not sp or sp.book not in paragraphs:
                    continue
                body = FO.split_body(c.get("content") or "")
                col, h, n = FO.align_letter(body, paragraphs[sp.book])
                hit += h
                num += n
                if h:
                    cols[c["chunk_index"]] = col
                elif n:
                    skipped.append(f"{c['chapter_path']}（節數與原文段數對不上）")
        elif part["mode"] in ("paragraph", "greek"):
            for c in chunks:
                sp = spans.get(c["chunk_index"])
                if not sp:
                    continue
                body = FO.split_body(c.get("content") or "")
                col, h, n = FO.align_by_paragraph_number(body, sp.book, paragraphs)
                hit += h
                num += n
                if h:
                    cols[c["chunk_index"]] = col
                else:
                    skipped.append(f"{c['chapter_path']}（{n} 個錨點全對不上）")
        else:
            extract = ANCHORS.get(part.get("anchor"), FO.chapter_headings)
            placed, hit, num = align_part(chunks, spans, chapters, by_book, extract)
            for c in chunks:
                if c["chunk_index"] not in spans:
                    continue
                got = placed.get(c["chunk_index"])
                size = len(FO.split_body(c.get("content") or ""))
                if got:
                    cols[c["chunk_index"]] = FO.fill_column(size, got)
                else:
                    skipped.append(f"{c['chapter_path']}（錨點全對不上）")
        hit_total += hit
        num_total += num
        pct = f"{hit / num:.0%}" if num else "—"
        print(f"  {prefix:22} 段 {len(spans):3}  命中 {hit:4}/{num:<4} {pct:>4}{note}")

    updated: list[dict] = []
    for c in chunks:
        col = cols.get(c["chunk_index"])
        if not col:
            updated.append(c)
            continue
        sources, order = FO.build_sources(
            c.get("sources"), c.get("source_text"), c.get("source_lang"),
            FO.render_column(col), spec["lang"])
        updated.append({**c, "sources": sources, "source_order": order,
                        # 舊的兩欄 reader 讀 source_text/source_lang，主欄仍是英譯
                        "source_lang": order[0], "source_text": sources[order[0]]})

    pct = f"{hit_total / num_total:.0%}" if num_total else "—"
    print(f"\n補上原文欄 {len(cols)} 段；錨點命中 {hit_total} / {num_total}（{pct}）")
    if skipped:
        print(f"錨點全對不上而跳過的 {len(skipped)} 段：")
        for x in skipped[:12]:
            print(f"  · {x}")
        if len(skipped) > 12:
            print(f"  …另外 {len(skipped) - 12} 段")

    if not a.apply:
        print("\n（只驗不寫。確認無誤後加 --apply）")
        return 0

    backup = path.with_suffix(".jsonl.bak_pre_original")
    if not backup.exists():
        shutil.copy2(path, backup)
        print(f"備份 → {backup.name}")
    path.write_text(
        "\n".join(json.dumps(c, ensure_ascii=False) for c in updated) + "\n",
        encoding="utf-8")
    print(f"寫回 {path.name}（{len(updated)} 段）")
    print("🚨 線上還要把 JSONL 推到 R2 才會生效（見 server/utils/ebook-chunks.ts）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
