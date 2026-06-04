"""Seed deities for /translation-glossary (「神祇與宗教名詞」tab) — HAND-CURATED.
既有 37 筆多為諾斯底術語；本批補主流神系 + 聖經 ANE 神祇（不動既有，on_conflict=name_english）。
extras: religion 宗教 / entity_type 類型 / domain_of 掌管。
聖經出現過的神祇 → 和合本譯為 name_recommended，史學音譯放 name_variants。
Usage: python scripts/seed_glossary_deities.py [--dry]
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


def D(en, rec, *, o="", lang="", var="", reason="", root="", religion="",
      etype="deity", domain=""):
    global _order
    _order += 10
    ROWS.append({"name_english": en, "name_original": o or None,
        "name_original_lang": lang or None, "name_recommended": rec,
        "name_variants": var or None, "recommendation_reason": reason or None,
        "name_root": root or None, "religion": religion or None,
        "entity_type": etype or None, "domain_of": domain or None,
        "sort_order": _order})


# ── 聖經/古近東神祇（使用者領域重點；和合本譯為★）────────────────────────────
_order = 500
R_ANE = "古近東／聖經"
D("Baal", "巴力", o="בַּעַל", lang="heb", var="巴爾", religion=R_ANE, domain="風暴／豐饒",
  reason="迦南主神，聖經屢斥拜巴力")
D("Asherah", "亞舍拉", o="אֲשֵׁרָה", lang="heb", var="阿舍拉", religion=R_ANE,
  domain="母神／豐饒", reason="聖經之亞舍拉木偶")
D("Ashtoreth", "亞斯她錄", o="עַשְׁתֹּרֶת", lang="heb", var="阿斯塔特(Astarte)；伊絲塔關聯",
  religion=R_ANE, domain="愛與戰爭", reason="王上11:5；腓尼基女神")
D("Dagon", "大袞", o="דָּגוֹן", lang="heb", religion=R_ANE, domain="穀物／豐饒",
  reason="非利士人之神（士16；撒上5）")
D("Molech", "摩洛", o="מֹלֶךְ", lang="heb", var="摩力克；瑪拉客(思高)", religion=R_ANE,
  domain="火祭之神", reason="獻嬰之神（利18:21）")
D("Chemosh", "基抹", o="כְּמוֹשׁ", lang="heb", religion=R_ANE, domain="摩押主神",
  reason="摩押人之神（民21:29）")
D("Milcom", "米勒公", o="מִלְכֹּם", lang="heb", religion=R_ANE, domain="亞捫主神",
  reason="亞捫人之神（王上11:5）")
D("Tammuz", "搭模斯", o="תַּמּוּז", lang="heb", var="杜姆茲(Dumuzid)", religion=R_ANE,
  domain="牧神／復生", reason="結8:14婦女哭搭模斯")
D("Marduk", "馬爾杜克", o="𒀭𒀫𒌓", lang="akk", var="米羅達(Merodach,聖經)", religion="米所波大米",
  domain="巴比倫主神", reason="耶50:2「米羅達」即此；巴比倫城邦主神")
D("Ishtar", "伊絲塔", o="𒀭𒈹", lang="akk", var="伊師塔；伊絲塔爾", religion="米所波大米",
  domain="愛與戰爭", reason="蘇美稱伊南娜(Inanna)")
D("Anu", "安努", lang="akk", religion="米所波大米", domain="天神（眾神之父）")
D("Enlil", "恩利爾", lang="akk", religion="米所波大米", domain="風／大氣")
D("Enki", "恩基", lang="akk", var="埃阿(Ea)", religion="米所波大米", domain="水／智慧")
D("Ashur", "亞述爾", lang="akk", var="阿淑爾", religion="米所波大米", domain="亞述主神",
  reason="亞述帝國主神，與城同名")
D("Sin (deity)", "辛", lang="akk", var="南納(Nanna)", religion="米所波大米", domain="月神")

# ── 希臘神祇 ─────────────────────────────────────────────────────────────────
_order = 1000
R_GR = "希臘"
D("Hera", "赫拉", o="Ἥρα", lang="grc", religion=R_GR, domain="婚姻／天后")
D("Poseidon", "波塞頓", o="Ποσειδῶν", lang="grc", var="波塞冬（陸）", religion=R_GR, domain="海洋")
D("Apollo", "阿波羅", o="Ἀπόλλων", lang="grc", religion=R_GR, domain="太陽／音樂／預言")
D("Artemis", "阿緹米絲", o="Ἄρτεμις", lang="grc", var="阿耳忒彌斯（陸）；亞底米(徒19和合)",
  religion=R_GR, domain="狩獵／月", reason="徒19:28以弗所「大亞底米」")
D("Athena", "雅典娜", o="Ἀθηνᾶ", lang="grc", religion=R_GR, domain="智慧／戰爭")
D("Ares", "阿瑞斯", o="Ἄρης", lang="grc", religion=R_GR, domain="戰爭")
D("Aphrodite", "阿芙羅黛蒂", o="Ἀφροδίτη", lang="grc", var="阿佛洛狄忒（陸）",
  religion=R_GR, domain="愛與美")
D("Hephaestus", "赫菲斯托斯", o="Ἥφαιστος", lang="grc", religion=R_GR, domain="火／鍛造")
D("Hermes", "赫密士", o="Ἑρμῆς", lang="grc", var="赫爾墨斯（陸）；希耳米(徒14和合)",
  religion=R_GR, domain="使者／商旅", reason="徒14:12稱保羅為「希耳米」")
D("Demeter", "狄蜜特", o="Δημήτηρ", lang="grc", var="得墨忒耳（陸）", religion=R_GR, domain="農穀")
D("Dionysus", "戴奧尼索斯", o="Διόνυσος", lang="grc", var="狄俄倪索斯（陸）；巴克斯",
  religion=R_GR, domain="酒／狂歡")
D("Hades", "黑帝斯", o="ᾍδης", lang="grc", var="哈得斯；陰間(聖經作陰間)", religion=R_GR,
  domain="冥界")
D("Cronus", "克洛諾斯", o="Κρόνος", lang="grc", var="克羅諾斯", religion=R_GR, domain="泰坦／時間")
D("Gaia", "蓋亞", o="Γαῖα", lang="grc", var="蓋婭", religion=R_GR, domain="大地母神")

# ── 羅馬神祇 ─────────────────────────────────────────────────────────────────
_order = 1400
R_RO = "羅馬"
D("Jupiter", "朱庇特", o="Iuppiter", lang="lat", var="朱比特；丟斯(徒14和合)", religion=R_RO,
  domain="主神／天空", reason="對應希臘宙斯；徒14:12和合作「丟斯」")
D("Juno", "朱諾", o="Iuno", lang="lat", religion=R_RO, domain="天后／婚姻")
D("Neptune", "涅普頓", o="Neptunus", lang="lat", var="尼普頓", religion=R_RO, domain="海洋")
D("Minerva", "米娜瓦", o="Minerva", lang="lat", var="密涅瓦", religion=R_RO, domain="智慧")
D("Mars", "瑪爾斯", o="Mars", lang="lat", var="馬爾斯", religion=R_RO, domain="戰爭")
D("Venus", "維納斯", o="Venus", lang="lat", religion=R_RO, domain="愛與美")
D("Mercury", "墨丘利", o="Mercurius", lang="lat", religion=R_RO, domain="使者／商旅")
D("Diana", "黛安娜", o="Diana", lang="lat", religion=R_RO, domain="狩獵／月")
D("Saturn", "薩圖恩", o="Saturnus", lang="lat", var="薩圖爾努斯", religion=R_RO, domain="農／時間")
D("Janus", "雅努斯", o="Ianus", lang="lat", religion=R_RO, domain="門戶／始末（雙面）")

# ── 埃及神祇 ─────────────────────────────────────────────────────────────────
_order = 1700
R_EG = "埃及"
D("Ra", "拉", var="瑞", religion=R_EG, domain="太陽神")
D("Osiris", "歐西里斯", var="奧西里斯（陸）", religion=R_EG, domain="冥界／復生")
D("Isis", "伊西斯", var="伊希斯", religion=R_EG, domain="母神／魔法")
D("Horus", "荷魯斯", var="何露斯", religion=R_EG, domain="王權／天空（鷹首）")
D("Anubis", "阿努比斯", religion=R_EG, domain="死者守護（胡狼首）")
D("Thoth", "托特", var="圖特", religion=R_EG, domain="智慧／書寫（䴉首）")
D("Set (Egyptian)", "賽特", var="塞特（埃及神，勿與諾斯底塞特混）", religion=R_EG,
  domain="混亂／風暴", reason="埃及神 Set；與諾斯底之 Seth 同英拼須區別")
D("Amun", "阿蒙", var="阿蒙‧拉(Amun-Ra)", religion=R_EG, domain="底比斯主神")
D("Ptah", "卜塔", var="普塔", religion=R_EG, domain="孟斐斯創造神")
D("Hathor", "哈索爾", religion=R_EG, domain="愛／音樂（牛角）")

# ── 北歐神祇 ─────────────────────────────────────────────────────────────────
_order = 2000
R_NO = "北歐"
D("Odin", "奧丁", var="沃登(Woden)", religion=R_NO, domain="主神／智慧／戰爭")
D("Thor", "索爾", var="托爾", religion=R_NO, domain="雷神")
D("Loki", "洛基", religion=R_NO, domain="詭計之神")
D("Freyja", "芙蕾雅", var="弗蕾亞", religion=R_NO, domain="愛／豐饒")
D("Baldr", "巴德爾", var="巴德", religion=R_NO, domain="光明／純潔")

# ── 印度教神祇 ───────────────────────────────────────────────────────────────
_order = 2200
R_HI = "印度教"
D("Brahma", "梵天", var="布茹阿瑪", religion=R_HI, domain="創造神")
D("Vishnu", "毗濕奴", var="維濕奴", religion=R_HI, domain="維護神")
D("Shiva", "濕婆", var="希瓦", religion=R_HI, domain="毀滅／轉化")
D("Krishna", "克里希那", o="कृष्ण", lang="sa", var="黑天；奎師那；克里須那", root="克里希那",
  religion=R_HI, domain="毗濕奴化身", reason="《薄伽梵歌》之神")
D("Ganesha", "象頭神", var="伽內什；甘尼許", religion=R_HI, domain="除障／智慧")
D("Indra", "因陀羅", var="帝釋天（佛教）", religion=R_HI, domain="雷雨／天界之王")
D("Lakshmi", "吉祥天女", var="拉克什米", religion=R_HI, domain="財富／幸運")
D("Devi", "提毗", var="女神（總稱）", religion=R_HI, domain="母神")

# ── 瑣羅亞斯德教 ─────────────────────────────────────────────────────────────
_order = 2400
R_ZO = "祆教（瑣羅亞斯德）"
D("Zarathustra", "查拉圖斯特拉", o="𐬰𐬀𐬭𐬀𐬚𐬎𐬱𐬙𐬭𐬀", lang="ae", var="瑣羅亞斯德（英文轉譯）；蘇魯支（唐古譯）；查拉圖斯特拉",
  religion=R_ZO, etype="教主", domain="祆教先知／教主",
  reason="按原文：阿維斯陀語 Zaraθuštra → 查拉圖斯特拉，較英文 Zoroaster 經希臘轉來的「瑣羅亞斯德」更貼近原文")
D("Ahura Mazda", "阿胡拉‧馬茲達", var="奧爾穆茲德(Ohrmazd)", religion=R_ZO, domain="至善光明之主")
D("Angra Mainyu", "安格拉‧曼紐", var="阿里曼(Ahriman)", religion=R_ZO, domain="惡靈／黑暗")
D("Mithra / Mithras", "密特拉", o="Μίθρας", lang="grc", var="密特拉斯；密司拉", root="密特",
  religion="祆教／羅馬密特拉密儀", domain="契約／太陽",
  reason="名根「密特」與密特里達迪一致；羅馬密特拉密儀")


# ── Main ─────────────────────────────────────────────────────────────────────
def check_roots():
    return [(r["name_english"], r["name_recommended"], r["name_root"])
            for r in ROWS if r.get("name_root") and r["name_root"] not in (r.get("name_recommended") or "")]

def upsert(rows):
    for i in range(0, len(rows), 100):
        b = rows[i:i+100]
        r = requests.post(f"{URL}/rest/v1/deities?on_conflict=name_english",
                          headers=H_UPSERT, json=b, timeout=90)
        if r.status_code >= 300:
            print(f"  ERROR {r.status_code}: {r.text[:400]}"); return False
        print(f"  ✓ upserted {len(b)}")
    return True

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()
    seen = {}
    for r in ROWS: seen[r["name_english"]] = seen.get(r["name_english"], 0) + 1
    dups = {k: v for k, v in seen.items() if v > 1}
    if dups: print(f"⚠️  重複：{dups}")
    bad = check_roots()
    print("✓ 名根一致" if not bad else f"⚠️ 名根不一致：{bad}")
    print(f"共 {len(ROWS)} 筆 deities（新增/更新）")
    if args.dry:
        for r in ROWS: print(f"  [{r['sort_order']:>4}] {r['name_english']:<20} → {r['name_recommended']}  @{r.get('religion')}")
        sys.exit(0)
    if upsert(ROWS): print("Done.")
