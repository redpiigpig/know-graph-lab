"""Seed philosophers for /translation-glossary (「哲學家」tab) — HAND-CURATED.
同 places/rulers 政策：純人工策展。台譯為 name_recommended，陸譯/異譯放 name_variants。
extras: school 學派 / era 時期 / nationality 國籍。
Usage: python scripts/seed_glossary_philosophers.py [--dry]
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


def F(en, rec, *, o="", lang="", var="", reason="", root="", school="", era="",
      nat="", by=None, dy=None):
    global _order
    _order += 10
    ROWS.append({"name_english": en, "name_original": o or None,
        "name_original_lang": lang or None, "name_recommended": rec,
        "name_variants": var or None, "recommendation_reason": reason or None,
        "name_root": root or None, "school": school or None, "era": era or None,
        "nationality": nat or None, "born_year": by, "died_year": dy,
        "sort_order": _order})


# ── 蘇格拉底前（希臘古典）────────────────────────────────────────────────────
_order = 1000
F("Thales", "泰利斯", o="Θαλῆς", lang="grc", var="泰勒斯（陸）", school="米利都學派",
  era="蘇格拉底前", nat="希臘", by=-624, dy=-546)
F("Anaximander", "阿那克西曼德", o="Ἀναξίμανδρος", lang="grc", school="米利都學派",
  era="蘇格拉底前", nat="希臘", by=-610, dy=-546)
F("Anaximenes", "阿那克西美尼", o="Ἀναξιμένης", lang="grc", school="米利都學派",
  era="蘇格拉底前", nat="希臘", by=-586, dy=-526)
F("Pythagoras", "畢達哥拉斯", o="Πυθαγόρας", lang="grc", var="畢氏", school="畢達哥拉斯學派",
  era="蘇格拉底前", nat="希臘", by=-570, dy=-495)
F("Heraclitus", "赫拉克利特", o="Ἡράκλειτος", lang="grc", var="赫拉克里特斯", school="以弗所學派",
  era="蘇格拉底前", nat="希臘", by=-535, dy=-475)
F("Parmenides", "巴門尼德", o="Παρμενίδης", lang="grc", school="伊利亞學派",
  era="蘇格拉底前", nat="希臘", by=-515, dy=-450)
F("Zeno of Elea", "伊利亞的芝諾", o="Ζήνων", lang="grc", var="芝諾", root="芝諾",
  school="伊利亞學派", era="蘇格拉底前", nat="希臘", by=-490, dy=-430,
  reason="名根「芝諾」與斯多噶季蒂昂的芝諾共享")
F("Empedocles", "恩培多克勒", o="Ἐμπεδοκλῆς", lang="grc", era="蘇格拉底前",
  nat="希臘", by=-494, dy=-434)
F("Anaxagoras", "阿那克薩哥拉", o="Ἀναξαγόρας", lang="grc", era="蘇格拉底前",
  nat="希臘", by=-500, dy=-428)
F("Democritus", "德謨克利特", o="Δημόκριτος", lang="grc", var="德謨克利圖斯", school="原子論",
  era="蘇格拉底前", nat="希臘", by=-460, dy=-370)
F("Protagoras", "普羅塔哥拉", o="Πρωταγόρας", lang="grc", school="辯士（智者）派",
  era="蘇格拉底前", nat="希臘", by=-490, dy=-420)
# ── 雅典古典三哲 ─────────────────────────────────────────────────────────────
_order = 1300
F("Socrates", "蘇格拉底", o="Σωκράτης", lang="grc", school="古典", era="古典希臘",
  nat="希臘", by=-470, dy=-399)
F("Plato", "柏拉圖", o="Πλάτων", lang="grc", school="柏拉圖學園（理型論）",
  era="古典希臘", nat="希臘", by=-428, dy=-348)
F("Aristotle", "亞里斯多德", o="Ἀριστοτέλης", lang="grc", var="亞里士多德（陸）",
  school="逍遙學派", era="古典希臘", nat="希臘", by=-384, dy=-322,
  reason="台作亞里斯多德，陸作亞里士多德")
# ── 希臘化各派 ───────────────────────────────────────────────────────────────
_order = 1500
F("Antisthenes", "安提斯泰尼", o="Ἀντισθένης", lang="grc", school="犬儒學派",
  era="希臘化", nat="希臘", by=-446, dy=-366)
F("Diogenes of Sinope", "第歐根尼", o="Διογένης", lang="grc", var="戴奧吉尼斯；錫諾普的第歐根尼",
  school="犬儒學派", era="希臘化", nat="希臘", by=-412, dy=-323)
F("Epicurus", "伊比鳩魯", o="Ἐπίκουρος", lang="grc", var="伊壁鳩魯（陸）",
  school="伊比鳩魯學派", era="希臘化", nat="希臘", by=-341, dy=-270,
  reason="台作伊比鳩魯，陸作伊壁鳩魯")
F("Zeno of Citium", "季蒂昂的芝諾", o="Ζήνων", lang="grc", var="芝諾（斯多噶創始）",
  root="芝諾", school="斯多噶學派", era="希臘化", nat="希臘", by=-334, dy=-262,
  reason="斯多噶學派創始者；名根「芝諾」")
F("Chrysippus", "克律西波斯", o="Χρύσιππος", lang="grc", var="克里西波斯",
  school="斯多噶學派", era="希臘化", nat="希臘", by=-279, dy=-206)
F("Pyrrho", "皮浪", o="Πύρρων", lang="grc", var="皮羅", school="懷疑論",
  era="希臘化", nat="希臘", by=-360, dy=-270)
F("Sextus Empiricus", "塞克斯都‧恩披里柯", lang="grc", var="塞克斯圖斯",
  school="懷疑論", era="羅馬", nat="希臘", by=160, dy=210)
# ── 羅馬時期 ─────────────────────────────────────────────────────────────────
_order = 1700
F("Cicero", "西塞羅", o="Cicero", lang="lat", var="西塞祿", school="折衷／斯多噶",
  era="羅馬共和", nat="羅馬", by=-106, dy=-43)
F("Lucretius", "盧克萊修", o="Lucretius", lang="lat", school="伊比鳩魯學派",
  era="羅馬共和", nat="羅馬", by=-99, dy=-55)
F("Seneca the Younger", "塞內卡", o="Seneca", lang="lat", var="塞涅卡（陸）",
  school="斯多噶學派", era="羅馬帝國", nat="羅馬", by=-4, dy=65)
F("Epictetus", "愛比克泰德", o="Ἐπίκτητος", lang="grc", var="埃皮克提圖",
  school="斯多噶學派", era="羅馬帝國", nat="希臘", by=50, dy=135)
# ── 猶太／亞歷山大 + 新柏拉圖（與教父關係密切）──────────────────────────────
_order = 1900
F("Philo of Alexandria", "亞歷山大的斐洛", o="Φίλων", lang="grc", var="斐羅；費羅；斐洛",
  root="斐洛", school="中期柏拉圖／猶太化", era="希臘化猶太", nat="亞歷山大猶太",
  by=-25, dy=50, reason="影響教父寓意解經甚鉅")
F("Plotinus", "普羅提諾", o="Πλωτῖνος", lang="grc", var="柏羅丁", school="新柏拉圖主義",
  era="羅馬帝國", nat="埃及／希臘", by=204, dy=270, reason="新柏拉圖主義奠基者，影響奧古斯丁")
F("Porphyry", "波菲利", o="Πορφύριος", lang="grc", var="波斐利；波非利", school="新柏拉圖主義",
  era="羅馬帝國", nat="腓尼基／希臘", by=234, dy=305, reason="著《駁基督徒》")
F("Iamblichus", "楊布里科斯", o="Ἰάμβλιχος", lang="grc", var="楊布利可斯",
  school="新柏拉圖主義", era="羅馬帝國", nat="敘利亞", by=245, dy=325)
F("Proclus", "普羅克洛斯", o="Πρόκλος", lang="grc", var="普洛克勒斯", school="新柏拉圖主義",
  era="古典晚期", nat="希臘", by=412, dy=485, reason="影響偽狄奧尼修斯")
# ── 伊斯蘭哲學（Falsafa）─────────────────────────────────────────────────────
_order = 2100
F("Al-Kindi", "肯迪", lang="ar", var="金迪", school="伊斯蘭亞里斯多德主義",
  era="中世紀", nat="阿拉伯", by=801, dy=873)
F("Al-Farabi", "法拉比", lang="ar", var="阿爾法拉比", school="伊斯蘭新柏拉圖主義",
  era="中世紀", nat="中亞／波斯", by=872, dy=950)
F("Avicenna", "阿維森納", lang="ar", var="伊本‧西那(Ibn Sina)", root="阿維森納",
  school="伊斯蘭亞里斯多德主義", era="中世紀", nat="波斯", by=980, dy=1037,
  reason="《治療論》《醫典》；影響經院神學")
F("Al-Ghazali", "安薩里", lang="ar", var="加札利；安薩理", school="蘇菲／阿什爾里",
  era="中世紀", nat="波斯", by=1058, dy=1111, reason="《哲學家的矛盾》")
F("Averroes", "阿威羅伊", lang="ar", var="伊本‧魯世德(Ibn Rushd)", school="伊斯蘭亞里斯多德主義",
  era="中世紀", nat="安達盧斯", by=1126, dy=1198, reason="影響拉丁阿威羅伊主義")
F("Maimonides", "邁蒙尼德", lang="he", var="摩西‧本‧邁蒙；拉姆巴姆(Rambam)", root="邁蒙",
  school="猶太亞里斯多德主義", era="中世紀", nat="安達盧斯猶太", by=1138, dy=1204,
  reason="《迷途指津》")
# ── 近代（與宗教／詮釋學相關優先）────────────────────────────────────────────
_order = 2400
F("Descartes", "笛卡兒", o="Descartes", lang="fr", var="笛卡爾（陸）", school="理性論",
  era="近代", nat="法國", by=1596, dy=1650, reason="台作笛卡兒，陸作笛卡爾")
F("Spinoza", "斯賓諾莎", o="Spinoza", lang="nl", var="史賓諾莎", school="理性論",
  era="近代", nat="荷蘭猶太", by=1632, dy=1677)
F("Leibniz", "萊布尼茲", o="Leibniz", lang="de", var="萊布尼茨（陸）", school="理性論",
  era="近代", nat="德國", by=1646, dy=1716)
F("John Locke", "洛克", o="Locke", lang="en", school="經驗論", era="近代",
  nat="英格蘭", by=1632, dy=1704)
F("David Hume", "休謨", o="Hume", lang="en", var="休姆", school="經驗論／懷疑論",
  era="近代", nat="蘇格蘭", by=1711, dy=1776)
F("Immanuel Kant", "康德", o="Kant", lang="de", school="德國觀念論（批判哲學）",
  era="近代", nat="德國", by=1724, dy=1804)
F("Hegel", "黑格爾", o="Hegel", lang="de", school="德國觀念論", era="近代",
  nat="德國", by=1770, dy=1831)
F("Schopenhauer", "叔本華", o="Schopenhauer", lang="de", school="意志哲學",
  era="近代", nat="德國", by=1788, dy=1860)
F("Karl Marx", "馬克思", o="Marx", lang="de", var="馬克斯", school="辯證唯物論",
  era="近代", nat="德國", by=1818, dy=1883)
F("Nietzsche", "尼采", o="Nietzsche", lang="de", var="尼采", school="生命哲學",
  era="近代", nat="德國", by=1844, dy=1900)
# ── 現代（現象學／詮釋學／宗教哲學）──────────────────────────────────────────
_order = 2700
F("Edmund Husserl", "胡塞爾", o="Husserl", lang="de", school="現象學", era="現代",
  nat="德國", by=1859, dy=1938)
F("Martin Heidegger", "海德格", o="Heidegger", lang="de", var="海德格爾（陸）",
  school="現象學／存在哲學", era="現代", nat="德國", by=1889, dy=1976,
  reason="台作海德格，陸作海德格爾")
F("Ludwig Wittgenstein", "維根斯坦", o="Wittgenstein", lang="de", var="維特根斯坦（陸）",
  school="分析哲學", era="現代", nat="奧地利", by=1889, dy=1951,
  reason="台作維根斯坦，陸作維特根斯坦")
F("Jean-Paul Sartre", "沙特", o="Sartre", lang="fr", var="薩特（陸）",
  school="存在主義", era="現代", nat="法國", by=1905, dy=1980,
  reason="台作沙特，陸作薩特")
F("Emmanuel Levinas", "列維納斯", o="Levinas", lang="fr", var="勒維納斯",
  school="現象學／他者倫理", era="現代", nat="法國猶太", by=1906, dy=1995)
F("Hans-Georg Gadamer", "高達美", o="Gadamer", lang="de", var="伽達默爾（陸）",
  school="詮釋學", era="現代", nat="德國", by=1900, dy=2002,
  reason="《真理與方法》；台作高達美，陸作伽達默爾")
F("Paul Ricoeur", "呂格爾", o="Ricœur", lang="fr", var="利科（陸）", school="詮釋學",
  era="現代", nat="法國", by=1913, dy=2005, reason="台作呂格爾，陸作利科")


# ── Main ─────────────────────────────────────────────────────────────────────
def check_roots():
    return [(r["name_english"], r["name_recommended"], r["name_root"])
            for r in ROWS if r.get("name_root") and r["name_root"] not in (r.get("name_recommended") or "")]

def upsert(rows):
    for i in range(0, len(rows), 100):
        b = rows[i:i+100]
        r = requests.post(f"{URL}/rest/v1/philosophers?on_conflict=name_english",
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
    print(f"共 {len(ROWS)} 筆 philosophers")
    if args.dry:
        for r in ROWS: print(f"  [{r['sort_order']:>4}] {r['name_english']:<26} → {r['name_recommended']}")
        sys.exit(0)
    if upsert(ROWS): print("Done.")
