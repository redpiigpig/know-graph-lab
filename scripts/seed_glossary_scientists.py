"""Seed scientists for /translation-glossary (「科學家」tab) — HAND-CURATED.
extras: field 領域 / era 時期 / nationality 國籍。台譯★、陸譯/異譯放變體。
Usage: python scripts/seed_glossary_scientists.py [--dry]
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


def S(en, rec, *, o="", lang="", var="", reason="", root="", field="", era="",
      nat="", by=None, dy=None):
    global _order
    _order += 10
    ROWS.append({"name_english": en, "name_original": o or None,
        "name_original_lang": lang or None, "name_recommended": rec,
        "name_variants": var or None, "recommendation_reason": reason or None,
        "name_root": root or None, "field": field or None, "era": era or None,
        "nationality": nat or None, "born_year": by, "died_year": dy,
        "sort_order": _order})


# ── 古典（希臘羅馬）────────────────────────────────────────────────────────────
_order = 1000
S("Hippocrates", "希波克拉底", o="Ἱπποκράτης", lang="grc", field="醫學",
  era="古典希臘", nat="希臘", by=-460, dy=-370, reason="醫學之父")
S("Euclid", "歐幾里得", o="Εὐκλείδης", lang="grc", var="歐基里德", field="數學",
  era="希臘化", nat="希臘", by=-325, dy=-265, reason="《幾何原本》")
S("Archimedes", "阿基米德", o="Ἀρχιμήδης", lang="grc", field="數學／物理",
  era="希臘化", nat="希臘", by=-287, dy=-212)
S("Eratosthenes", "埃拉托斯特尼", o="Ἐρατοσθένης", lang="grc", field="地理／數學",
  era="希臘化", nat="希臘", by=-276, dy=-194, reason="測地球周長")
S("Aristarchus of Samos", "阿里斯塔克斯", o="Ἀρίσταρχος", lang="grc", field="天文",
  era="希臘化", nat="希臘", by=-310, dy=-230, reason="最早日心說")
S("Hipparchus", "喜帕恰斯", o="Ἵππαρχος", lang="grc", var="希帕求斯", field="天文",
  era="希臘化", nat="希臘", by=-190, dy=-120)
S("Claudius Ptolemy", "托勒密", o="Πτολεμαῖος", lang="grc", var="克勞狄烏斯‧托勒密",
  root="托勒密", field="天文／地理", era="羅馬", nat="希臘／埃及", by=100, dy=170,
  reason="《天文學大成》地心說；名根「托勒密」")
S("Galen", "蓋倫", o="Γαληνός", lang="grc", var="加倫", field="醫學", era="羅馬",
  nat="希臘", by=129, dy=216)
S("Pliny the Elder", "老普林尼", o="Plinius", lang="lat", field="博物學",
  era="羅馬帝國", nat="羅馬", by=23, dy=79, reason="《自然史》")
# ── 伊斯蘭黃金時代 ───────────────────────────────────────────────────────────
_order = 1400
S("Al-Khwarizmi", "花拉子米", lang="ar", var="花剌子模", field="數學／天文",
  era="中世紀", nat="波斯", by=780, dy=850, reason="代數(algebra)、演算法(algorithm)語源")
S("Al-Razi (Rhazes)", "拉齊", lang="ar", var="拉澤斯；累塞斯", field="醫學／化學",
  era="中世紀", nat="波斯", by=854, dy=925)
S("Ibn al-Haytham (Alhazen)", "海什木", lang="ar", var="阿爾哈曾", field="光學／物理",
  era="中世紀", nat="阿拉伯", by=965, dy=1040, reason="《光學書》，科學方法先驅")
S("Al-Biruni", "比魯尼", lang="ar", var="比魯泥", field="天文／地理", era="中世紀",
  nat="波斯", by=973, dy=1048)
S("Omar Khayyam", "奧瑪‧海亞姆", lang="fa", var="歐瑪爾‧海亞姆", field="數學／天文",
  era="中世紀", nat="波斯", by=1048, dy=1131)
# ── 科學革命 ─────────────────────────────────────────────────────────────────
_order = 1700
S("Copernicus", "哥白尼", o="Copernicus", lang="lat", field="天文", era="文藝復興",
  nat="波蘭", by=1473, dy=1543, reason="日心說")
S("Tycho Brahe", "第谷", o="Tycho Brahe", lang="da", var="布拉赫", field="天文",
  era="科學革命", nat="丹麥", by=1546, dy=1601)
S("Johannes Kepler", "克卜勒", o="Kepler", lang="de", var="開普勒（陸）", field="天文",
  era="科學革命", nat="德國", by=1571, dy=1630, reason="行星運動定律；台作克卜勒，陸作開普勒")
S("Galileo Galilei", "伽利略", o="Galileo", lang="it", field="天文／物理",
  era="科學革命", nat="義大利", by=1564, dy=1642)
S("William Harvey", "哈維", o="Harvey", lang="en", field="醫學／生理",
  era="科學革命", nat="英格蘭", by=1578, dy=1657, reason="血液循環")
S("Robert Boyle", "波以耳", o="Boyle", lang="en", var="玻意耳（陸）", field="化學／物理",
  era="科學革命", nat="愛爾蘭", by=1627, dy=1691)
S("Isaac Newton", "牛頓", o="Newton", lang="en", field="物理／數學", era="科學革命",
  nat="英格蘭", by=1643, dy=1727, reason="萬有引力、運動定律")
# ── 近現代 ───────────────────────────────────────────────────────────────────
_order = 2000
S("Carl Linnaeus", "林奈", o="Linnæus", lang="la", var="林奈烏斯", field="生物分類",
  era="近代", nat="瑞典", by=1707, dy=1778, reason="二名法")
S("Antoine Lavoisier", "拉瓦節", o="Lavoisier", lang="fr", var="拉瓦錫（陸）",
  field="化學", era="近代", nat="法國", by=1743, dy=1794, reason="近代化學之父")
S("John Dalton", "道爾頓", o="Dalton", lang="en", var="道耳吞", field="化學／物理",
  era="近代", nat="英格蘭", by=1766, dy=1844, reason="原子論")
S("Michael Faraday", "法拉第", o="Faraday", lang="en", field="物理／化學",
  era="近代", nat="英格蘭", by=1791, dy=1867, reason="電磁感應")
S("Charles Darwin", "達爾文", o="Darwin", lang="en", field="生物／演化",
  era="近代", nat="英格蘭", by=1809, dy=1882, reason="《物種起源》天擇說")
S("Gregor Mendel", "孟德爾", o="Mendel", lang="de", var="孟德爾", field="遺傳學",
  era="近代", nat="奧地利", by=1822, dy=1884, reason="遺傳定律；奧斯定會修士")
S("Louis Pasteur", "巴斯德", o="Pasteur", lang="fr", field="微生物／化學",
  era="近代", nat="法國", by=1822, dy=1895, reason="細菌論、巴氏消毒")
S("James Clerk Maxwell", "馬克士威", o="Maxwell", lang="en", var="麥克斯韋（陸）",
  field="物理", era="近代", nat="蘇格蘭", by=1831, dy=1879,
  reason="電磁方程；台作馬克士威，陸作麥克斯韋")
S("Dmitri Mendeleev", "門得列夫", o="Менделеев", lang="ru", var="門捷列夫（陸）",
  field="化學", era="近代", nat="俄國", by=1834, dy=1907, reason="週期表")
# ── 現代 ─────────────────────────────────────────────────────────────────────
_order = 2300
S("Marie Curie", "居禮夫人", o="Curie", lang="fr", var="瑪麗‧居里（陸）；瑪麗‧居禮",
  field="物理／化學", era="現代", nat="波蘭／法國", by=1867, dy=1934,
  reason="放射性研究；台作居禮，陸作居里")
S("Albert Einstein", "愛因斯坦", o="Einstein", lang="de", field="物理", era="現代",
  nat="德國／美國", by=1879, dy=1955, reason="相對論")
S("Niels Bohr", "波耳", o="Bohr", lang="da", var="玻爾（陸）", field="物理",
  era="現代", nat="丹麥", by=1885, dy=1962, reason="量子原子模型；台作波耳，陸作玻爾")
S("Werner Heisenberg", "海森堡", o="Heisenberg", lang="de", var="海森伯（陸）",
  field="物理", era="現代", nat="德國", by=1901, dy=1976, reason="測不準原理")
S("Edwin Hubble", "哈伯", o="Hubble", lang="en", var="哈勃（陸）", field="天文",
  era="現代", nat="美國", by=1889, dy=1953, reason="宇宙膨脹；台作哈伯，陸作哈勃")


# ── Main ─────────────────────────────────────────────────────────────────────
def check_roots():
    return [(r["name_english"], r["name_recommended"], r["name_root"])
            for r in ROWS if r.get("name_root") and r["name_root"] not in (r.get("name_recommended") or "")]

def upsert(rows):
    for i in range(0, len(rows), 100):
        b = rows[i:i+100]
        r = requests.post(f"{URL}/rest/v1/scientists?on_conflict=name_english",
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
    print(f"共 {len(ROWS)} 筆 scientists")
    if args.dry:
        for r in ROWS: print(f"  [{r['sort_order']:>4}] {r['name_english']:<28} → {r['name_recommended']}")
        sys.exit(0)
    if upsert(ROWS): print("Done.")
