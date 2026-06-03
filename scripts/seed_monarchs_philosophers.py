"""Seed the theologians table with two new figure_type groups for the
/translation-glossary page: 君主 (monarch) and 哲學家 (philosopher).

These are the Greek/Hellenistic kings + Roman emperors and the major Greek/
Roman philosophers that recur in patristic texts (persecutions, edicts,
apologetic engagement with philosophy). Reuses the theologians schema —
name_recommended is the ★ standard zh translation; tradition-variant columns
are left null (monarchs/philosophers rarely diverge across 新教/思高 like
biblical figures do).

Idempotent: skips name_english already present. born/died: BC = negative.
Usage: python scripts/seed_monarchs_philosophers.py [--dry-run]
"""
from __future__ import annotations
import argparse, os
from pathlib import Path
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
URL = os.environ["SUPABASE_URL"]; KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H_GET = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
H_JSON = {**H_GET, "Content-Type": "application/json", "Prefer": "return=minimal"}

# (name_english, name_original, name_recommended, born, died, nationality, role)
# born/died = reign or life years; BC negative. role 標身份。

MONARCHS = [
    # ── 希臘化／馬其頓君主 ──────────────────────────────────────────────
    ("Philip II of Macedon", "Φίλιππος", "馬其頓的腓力二世", -382, -336, "馬其頓", "馬其頓國王"),
    ("Alexander the Great", "Ἀλέξανδρος", "亞歷山大大帝", -356, -323, "馬其頓", "馬其頓國王／希臘化帝國"),
    ("Ptolemy I Soter", "Πτολεμαῖος Σωτήρ", "托勒密一世（救主）", -367, -283, "埃及", "托勒密王朝"),
    ("Ptolemy II Philadelphus", "Πτολεμαῖος Φιλάδελφος", "托勒密二世（費拉德爾甫斯）", -309, -246, "埃及", "托勒密王朝（七十士譯本贊助者）"),
    ("Ptolemy III Euergetes", "Πτολεμαῖος Εὐεργέτης", "托勒密三世（施惠者）", -284, -222, "埃及", "托勒密王朝"),
    ("Cleopatra VII", "Κλεοπάτρα", "克麗奧佩特拉七世", -69, -30, "埃及", "托勒密王朝末代女王"),
    ("Seleucus I Nicator", "Σέλευκος Νικάτωρ", "塞琉古一世（尼卡托）", -358, -281, "敘利亞", "塞琉古王朝"),
    ("Antiochus I Soter", "Ἀντίοχος Σωτήρ", "安條克一世（救主）", -324, -261, "敘利亞", "塞琉古王朝"),
    ("Antiochus III the Great", "Ἀντίοχος Μέγας", "安條克三世（大帝）", -241, -187, "敘利亞", "塞琉古王朝"),
    ("Antiochus IV Epiphanes", "Ἀντίοχος Ἐπιφανής", "安條克四世（埃皮法尼斯）", -215, -164, "敘利亞", "塞琉古王朝（瑪加伯起義迫害者）"),
    ("Antigonus I Monophthalmus", "Ἀντίγονος", "安提柯一世（獨眼）", -382, -301, "馬其頓", "安提柯王朝"),
    ("Lysimachus", "Λυσίμαχος", "利西馬科斯", -360, -281, "色雷斯", "繼業者"),
    ("Cassander", "Κάσσανδρος", "卡山德", -350, -297, "馬其頓", "繼業者"),
    ("Pyrrhus of Epirus", "Πύρρος", "伊庇魯斯的皮洛士", -319, -272, "伊庇魯斯", "伊庇魯斯國王"),
    ("Mithridates VI of Pontus", "Μιθριδάτης", "本都的米特拉達梯六世", -135, -63, "本都", "本都國王"),
    ("Attalus I", "Ἄτταλος", "阿塔羅斯一世", -269, -197, "帕加馬", "阿塔羅斯王朝"),
    ("Croesus", "Κροῖσος", "克羅伊斯", -595, -546, "呂底亞", "呂底亞國王"),
    ("Herod the Great", "Ἡρῴδης", "希律大帝", -73, -4, "猶太", "猶太王（羅馬附庸）"),

    # ── 羅馬皇帝（與教會史相關的主線）────────────────────────────────
    ("Augustus", "Augustus", "奧古斯都", -63, 14, "羅馬", "羅馬皇帝（首位）"),
    ("Tiberius", "Tiberius", "提庇留", -42, 37, "羅馬", "羅馬皇帝"),
    ("Caligula", "Caligula", "卡利古拉", 12, 41, "羅馬", "羅馬皇帝"),
    ("Claudius", "Claudius", "革老丟", -10, 54, "羅馬", "羅馬皇帝"),
    ("Nero", "Nero", "尼祿", 37, 68, "羅馬", "羅馬皇帝（首次大迫害）"),
    ("Vespasian", "Vespasianus", "維斯帕先", 9, 79, "羅馬", "羅馬皇帝（弗拉維王朝）"),
    ("Titus", "Titus", "提圖斯", 39, 81, "羅馬", "羅馬皇帝（毀耶路撒冷聖殿）"),
    ("Domitian", "Domitianus", "圖密善", 51, 96, "羅馬", "羅馬皇帝（迫害教會）"),
    ("Nerva", "Nerva", "涅爾瓦", 30, 98, "羅馬", "羅馬皇帝（五賢帝）"),
    ("Trajan", "Traianus", "圖拉真", 53, 117, "羅馬", "羅馬皇帝（依納爵殉道）"),
    ("Hadrian", "Hadrianus", "哈德良", 76, 138, "羅馬", "羅馬皇帝"),
    ("Antoninus Pius", "Antoninus Pius", "安東尼·庇護", 86, 161, "羅馬", "羅馬皇帝"),
    ("Marcus Aurelius", "Marcus Aurelius", "馬可·奧勒留", 121, 180, "羅馬", "羅馬皇帝／斯多噶哲人"),
    ("Commodus", "Commodus", "康茂德", 161, 192, "羅馬", "羅馬皇帝"),
    ("Septimius Severus", "Septimius Severus", "塞普蒂米烏斯·塞維魯", 145, 211, "羅馬", "羅馬皇帝（塞維魯王朝）"),
    ("Caracalla", "Caracalla", "卡拉卡拉", 188, 217, "羅馬", "羅馬皇帝"),
    ("Elagabalus", "Elagabalus", "埃拉伽巴路斯", 204, 222, "羅馬", "羅馬皇帝"),
    ("Severus Alexander", "Severus Alexander", "亞歷山大·塞維魯", 208, 235, "羅馬", "羅馬皇帝"),
    ("Maximinus Thrax", "Maximinus", "馬克西米努斯（色雷斯人）", 173, 238, "羅馬", "羅馬皇帝"),
    ("Philip the Arab", "Philippus Arabs", "阿拉伯人腓力", 204, 249, "羅馬", "羅馬皇帝"),
    ("Decius", "Decius", "德西烏斯", 201, 251, "羅馬", "羅馬皇帝（全帝國大迫害）"),
    ("Valerian", "Valerianus", "瓦勒良", 199, 260, "羅馬", "羅馬皇帝（迫害教會）"),
    ("Gallienus", "Gallienus", "加里恩努斯", 218, 268, "羅馬", "羅馬皇帝"),
    ("Aurelian", "Aurelianus", "奧勒良", 214, 275, "羅馬", "羅馬皇帝"),
    ("Diocletian", "Diocletianus", "戴克里先", 244, 311, "羅馬", "羅馬皇帝（戴克里先大迫害）"),
    ("Maximian", "Maximianus", "馬克西米安", 250, 310, "羅馬", "羅馬皇帝（四帝共治）"),
    ("Galerius", "Galerius", "伽列里烏斯", 258, 311, "羅馬", "羅馬皇帝（寬容敕令）"),
    ("Constantius I Chlorus", "Constantius", "君士坦提烏斯一世（克洛魯斯）", 250, 306, "羅馬", "羅馬皇帝（四帝共治）"),
    ("Constantine the Great", "Constantinus", "君士坦丁大帝", 272, 337, "羅馬", "羅馬皇帝（米蘭敕令／尼西亞會議）"),
    ("Licinius", "Licinius", "李錫尼", 263, 325, "羅馬", "羅馬皇帝（東部）"),
    ("Constantius II", "Constantius", "君士坦提烏斯二世", 317, 361, "羅馬", "羅馬皇帝（亞流派傾向）"),
    ("Julian the Apostate", "Iulianus", "背教者尤利安", 331, 363, "羅馬", "羅馬皇帝（復興異教）"),
    ("Jovian", "Iovianus", "約維安", 331, 364, "羅馬", "羅馬皇帝"),
    ("Valentinian I", "Valentinianus", "瓦倫提尼安一世", 321, 375, "羅馬", "羅馬皇帝（西部）"),
    ("Valens", "Valens", "瓦倫斯", 328, 378, "羅馬", "羅馬皇帝（東部，亞流派）"),
    ("Gratian", "Gratianus", "格拉提安", 359, 383, "羅馬", "羅馬皇帝"),
    ("Theodosius I", "Theodosius", "狄奧多西一世", 347, 395, "羅馬", "羅馬皇帝（立基督教為國教）"),
    ("Arcadius", "Arcadius", "阿卡狄烏斯", 377, 408, "東羅馬", "東羅馬皇帝"),
    ("Honorius", "Honorius", "霍諾留", 384, 423, "西羅馬", "西羅馬皇帝"),
    ("Theodosius II", "Theodosius", "狄奧多西二世", 401, 450, "東羅馬", "東羅馬皇帝（以弗所會議）"),
    ("Marcian", "Marcianus", "馬爾西安", 392, 457, "東羅馬", "東羅馬皇帝（迦克墩會議）"),
    ("Leo I the Thracian", "Leo", "利奧一世（色雷斯人）", 401, 474, "東羅馬", "東羅馬皇帝"),
    ("Zeno", "Zeno", "芝諾（皇帝）", 425, 491, "東羅馬", "東羅馬皇帝（合一諭令）"),
    ("Anastasius I", "Anastasius", "阿納斯塔修斯一世", 431, 518, "東羅馬", "東羅馬皇帝"),
    ("Justin I", "Iustinus", "查士丁一世", 450, 527, "東羅馬", "東羅馬皇帝"),
    ("Justinian I", "Iustinianus", "查士丁尼一世", 482, 565, "東羅馬", "東羅馬皇帝（聖索菲亞／法典）"),
]

PHILOSOPHERS = [
    # ── 蘇格拉底前哲學家 ────────────────────────────────────────────
    ("Thales of Miletus", "Θαλῆς", "泰利斯", -624, -546, "米利都", "蘇格拉底前哲學家"),
    ("Anaximander", "Ἀναξίμανδρος", "阿那克西曼德", -610, -546, "米利都", "蘇格拉底前哲學家"),
    ("Anaximenes", "Ἀναξιμένης", "阿那克西美尼", -586, -526, "米利都", "蘇格拉底前哲學家"),
    ("Pythagoras", "Πυθαγόρας", "畢達哥拉斯", -570, -495, "薩摩斯", "畢達哥拉斯學派"),
    ("Heraclitus", "Ἡράκλειτος", "赫拉克利特", -535, -475, "以弗所", "蘇格拉底前哲學家"),
    ("Parmenides", "Παρμενίδης", "巴門尼德", -515, -450, "埃利亞", "埃利亞學派"),
    ("Zeno of Elea", "Ζήνων ὁ Ἐλεάτης", "埃利亞的芝諾", -490, -430, "埃利亞", "埃利亞學派（悖論）"),
    ("Empedocles", "Ἐμπεδοκλῆς", "恩培多克勒", -494, -434, "阿克拉加斯", "蘇格拉底前哲學家"),
    ("Anaxagoras", "Ἀναξαγόρας", "阿那克薩哥拉", -500, -428, "克拉佐美納", "蘇格拉底前哲學家"),
    ("Leucippus", "Λεύκιππος", "留基伯", -480, -420, "米利都", "原子論"),
    ("Democritus", "Δημόκριτος", "德謨克利特", -460, -370, "阿布德拉", "原子論"),
    ("Protagoras", "Πρωταγόρας", "普羅泰戈拉", -490, -420, "阿布德拉", "智者派"),
    ("Gorgias", "Γοργίας", "高爾吉亞", -483, -375, "倫蒂尼", "智者派"),
    # ── 古典時期 ────────────────────────────────────────────────────
    ("Socrates", "Σωκράτης", "蘇格拉底", -470, -399, "雅典", "古典哲學家"),
    ("Plato", "Πλάτων", "柏拉圖", -428, -348, "雅典", "學園派創始人"),
    ("Aristotle", "Ἀριστοτέλης", "亞里斯多德", -384, -322, "斯塔基拉", "逍遙學派創始人"),
    ("Xenophon", "Ξενοφῶν", "色諾芬", -430, -354, "雅典", "蘇格拉底門徒"),
    ("Antisthenes", "Ἀντισθένης", "安提西尼", -445, -365, "雅典", "犬儒學派創始人"),
    ("Diogenes of Sinope", "Διογένης", "錫諾普的第歐根尼", -412, -323, "錫諾普", "犬儒學派"),
    # ── 希臘化時期 ──────────────────────────────────────────────────
    ("Epicurus", "Ἐπίκουρος", "伊壁鳩魯", -341, -270, "薩摩斯", "伊壁鳩魯學派創始人"),
    ("Zeno of Citium", "Ζήνων ὁ Κιτιεύς", "季蒂昂的芝諾", -334, -262, "季蒂昂", "斯多噶學派創始人"),
    ("Cleanthes", "Κλεάνθης", "克里安西斯", -330, -230, "阿索斯", "斯多噶學派"),
    ("Chrysippus", "Χρύσιππος", "克律西波斯", -279, -206, "索利", "斯多噶學派"),
    ("Pyrrho", "Πύρρων", "皮浪", -360, -270, "埃利斯", "懷疑學派創始人"),
    ("Carneades", "Καρνεάδης", "卡爾涅阿德斯", -214, -129, "昔蘭尼", "新學園懷疑派"),
    # ── 羅馬時期 ────────────────────────────────────────────────────
    ("Cicero", "Cicero", "西塞羅", -106, -43, "羅馬", "折衷主義／演說家"),
    ("Lucretius", "Lucretius", "盧克萊修", -99, -55, "羅馬", "伊壁鳩魯派詩人"),
    ("Philo of Alexandria", "Φίλων", "亞歷山卓的斐洛", -25, 50, "亞歷山卓", "猶太化柏拉圖主義"),
    ("Seneca the Younger", "Seneca", "塞內卡", -4, 65, "羅馬", "斯多噶學派"),
    ("Epictetus", "Ἐπίκτητος", "愛比克泰德", 50, 135, "希拉波利斯", "斯多噶學派"),
    ("Plutarch", "Πλούταρχος", "普魯塔克", 46, 120, "凱羅尼亞", "中期柏拉圖主義"),
    ("Sextus Empiricus", "Σέξτος", "塞克斯圖斯·恩丕里柯", 160, 210, "希臘", "懷疑學派"),
    # ── 新柏拉圖主義 ────────────────────────────────────────────────
    ("Plotinus", "Πλωτῖνος", "普羅提諾", 204, 270, "埃及", "新柏拉圖主義創始人"),
    ("Porphyry", "Πορφύριος", "波菲利", 234, 305, "提爾", "新柏拉圖主義（反基督教）"),
    ("Iamblichus", "Ἰάμβλιχος", "楊布里科斯", 245, 325, "敘利亞", "新柏拉圖主義"),
    ("Hypatia", "Ὑπατία", "希帕提婭", 360, 415, "亞歷山卓", "新柏拉圖主義"),
    ("Proclus", "Πρόκλος", "普羅克洛斯", 412, 485, "君士坦丁堡", "新柏拉圖主義"),
]


def existing() -> set[str]:
    r = requests.get(f"{URL}/rest/v1/theologians?select=name_english", headers=H_GET, timeout=30)
    r.raise_for_status()
    return {(x.get("name_english") or "").lower() for x in r.json()}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    ex = existing()
    rows = []
    for ft, data in [("monarch", MONARCHS), ("philosopher", PHILOSOPHERS)]:
        for en, orig, zh, born, died, nat, role in data:
            if en.lower() in ex:
                continue
            rows.append({
                "name_english": en, "name_original": orig, "name_latin_std": en,
                "name_recommended": zh, "born_year": born, "died_year": died,
                "nationality": nat, "role": role, "figure_type": ft,
                "first_source": "希臘羅馬君主／哲學家",
            })
    n_m = sum(1 for r in rows if r["figure_type"] == "monarch")
    n_p = sum(1 for r in rows if r["figure_type"] == "philosopher")
    print(f"Insert {len(rows)} ({n_m} monarchs, {n_p} philosophers); skipped {len(MONARCHS)+len(PHILOSOPHERS)-len(rows)}")
    if args.dry_run:
        for r in rows: print(f"  {r['figure_type']:11s} {r['name_english']:32s} → {r['name_recommended']}")
        return
    for i in range(0, len(rows), 25):
        r = requests.post(f"{URL}/rest/v1/theologians", headers=H_JSON, json=rows[i:i+25], timeout=60)
        print(f"  POST [{i}:{i+25}] {r.status_code}", r.text[:200] if r.status_code not in (200,201) else "")
    print("done")


if __name__ == "__main__":
    main()
