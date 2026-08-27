#!/usr/bin/env python3
"""Pick a picture for each Latin flashcard, and leave the card blank rather than guess.

Same rule as the other two decks: strictest first, and a wrong picture is worse
than none. A picture printed on a card teaches a sense the word does not carry
and the learner cannot undo it.

Latin arrives third, which is its advantage. Both earlier decks are curated
against the same Traditional-Chinese gloss vocabulary, so a Latin word whose
meaning either of them has already pictured takes that picture: *ignis*, אֵשׁ and
πῦρ are all 「火」 and all want the flame. That transfer is free and it is exact,
because the match is on the Chinese meaning a human already approved, not on a
resemblance between the words.

Latin also carries a real English definition on every entry — Collins's for the
upper volume, Whitaker's for the lower — which the other two decks largely do
not. That makes name matching worth more here, and also more dangerous:
Whitaker's definitions run to six senses separated by semicolons, so only the
senses are tried, never the whole line, and the ambiguous-English blocklist the
Hebrew deck built applies unchanged.

Order:

1. hand-picked overrides, named by the emoji's own name so a bad entry fails loudly
2. Chinese-meaning transfer from the Hebrew and Greek maps
3. exact match on the emoji's own name, from the English gloss's senses
4. nothing
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import latin_source_texts as L  # noqa: E402
import match_flashcard_images as base  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output/source-cache/flashcards"
VOCAB = ROOT / "data/originalReaders/vocabulary/latin-2000.json"
OUTPUT = CACHE / "latin-card-images.json"

# Named by the emoji's own annotation, never by hexcode: a typo then fails loudly
# instead of printing whatever art happens to sit at that code point.  This is
# where the core vocabulary lives, and where the function words get the symbol
# that stands in for them.
OVERRIDES: dict[str, str] = {
    # 天主與教會
    "deus": "folded hands", "dominus": "folded hands", "christus": "latin cross",
    "spiritus": "dove", "ecclesia": "church", "sanctus": "smiling face with halo",
    "angelus": "baby angel", "diabolus": "smiling face with horns",
    "caelum": "cloud", "infernus": "fire", "anima": "dove",
    "gratia": "sparkles", "gloria": "glowing star", "fides": "latin cross",
    "spes": "anchor", "caritas": "red heart", "peccatum": "black heart",
    "oratio": "folded hands", "benedictio": "raised hand",
    # 禮儀
    "missa": "church", "altare": "church", "sacramentum": "sparkles",
    "baptismus": "droplet", "eucharistia": "bread", "hostia": "bread",
    "calix": "wine glass", "panis": "bread", "vinum": "wine glass",
    "crux": "latin cross", "campana": "bell", "candela": "candle",
    "liber": "closed book", "codex": "closed book", "epistula": "envelope",
    "psalmus": "musical notes", "cantus": "musical notes", "hymnus": "musical notes",
    # 聖統
    "papa": "man", "episcopus": "man", "sacerdos": "man", "presbyter": "older person",
    "diaconus": "man", "monachus": "man", "abbas": "older person",
    "frater": "man", "soror": "woman", "populus": "busts in silhouette",
    "rex": "crown", "regina": "crown", "regnum": "castle",
    # 人與身體
    "homo": "bust in silhouette", "vir": "man", "mulier": "woman",
    "puer": "boy", "puella": "girl", "infans": "baby", "senex": "older person",
    "pater": "man", "mater": "woman", "filius": "boy", "filia": "girl",
    "corpus": "bust in silhouette", "caro": "cut of meat", "sanguis": "drop of blood",
    "cor": "anatomical heart", "manus": "hand with fingers splayed",
    "pes": "foot", "oculus": "eye", "auris": "ear", "os": "mouth",
    "caput": "bust in silhouette", "lingua": "tongue", "dens": "tooth",
    # 自然
    "aqua": "droplet", "ignis": "fire", "terra": "globe showing Europe-Africa",
    "mare": "water wave", "sol": "sun", "luna": "crescent moon",
    "stella": "star", "lux": "light bulb", "tenebrae": "new moon",
    "ventus": "wind face", "pluvia": "cloud with rain", "nix": "snowflake",
    "nubes": "cloud", "mons": "mountain", "lapis": "rock", "arbor": "deciduous tree",
    "lignum": "wood", "flos": "cherry blossom", "herba": "herb",
    "fructus": "red apple", "semen": "seedling", "vinea": "grapes",
    "oliva": "olive", "triticum": "sheaf of rice", "hortus": "cherry blossom",
    "ager": "sheaf of rice", "desertum": "desert", "flumen": "water wave",
    "fons": "potable water", "via": "motorway", "porta": "door", "murus": "brick",
    # 動物
    "agnus": "ewe", "ovis": "ewe", "pastor": "man", "grex": "ewe",
    "bos": "ox", "equus": "horse", "asinus": "donkey", "canis": "dog face",
    "leo": "lion", "lupus": "wolf", "serpens": "snake", "columba": "dove",
    "avis": "bird", "piscis": "fish", "gallus": "rooster", "vermis": "worm",
    # 時間
    "dies": "sun", "nox": "night with stars", "annus": "calendar",
    "mensis": "calendar", "hora": "watch", "tempus": "hourglass done",
    "hodie": "calendar", "cras": "calendar", "vesper": "night with stars",
    "mane": "sunrise", "aeternus": "infinity",
    # 器物與生活
    "domus": "house", "civitas": "cityscape", "urbs": "cityscape",
    "templum": "classical building", "turris": "tokyo tower",
    "navis": "sailboat", "currus": "wheel", "gladius": "dagger",
    "scutum": "shield", "corona": "crown", "vestis": "t-shirt",
    "calceus": "running shoe", "mensa": "fork and knife with plate",
    "cibus": "fork and knife with plate", "lac": "glass of milk",
    "mel": "honey pot", "sal": "salt", "oleum": "olive",
    "aurum": "coin", "argentum": "coin", "pecunia": "money bag",
    "clavis": "key", "littera": "envelope",
    "nomen": "label", "numerus": "input numbers", "signum": "flagged point",
    # 動作
    "ambulo": "person walking", "curro": "person running", "sedeo": "person in lotus position",
    "dormio": "sleeping face", "video": "eye", "audio": "ear", "loquor": "speaking head",
    "scribo": "writing hand", "lego": "open book", "canto": "musical notes",
    "manduco": "fork and knife", "bibo": "cup with straw", "laboro": "hammer",
    "aedifico": "building construction", "pugno": "crossed swords",
    "morior": "skull", "nascor": "baby", "vivo": "sparkling heart",
    "amo": "red heart", "timeo": "fearful face", "gaudeo": "grinning face",
    "fleo": "crying face", "rideo": "grinning face", "doceo": "teacher",
    "disco": "student", "iudico": "balance scale", "rego": "crown",
    "sano": "hospital", "lavo": "shower", "veniо": "person walking",
    # 抽象與功能詞
    "non": "prohibited", "nullus": "prohibited", "omnis": "globe with meridians",
    "totus": "globe with meridians", "multus": "plus",
    "magnus": "up arrow", "parvus": "down arrow", "primus": "1st place medal",
    "novus": "new button", "vetus": "hourglass done", "verus": "check mark button",
    "falsus": "cross mark", "bonus": "thumbs up", "malus": "thumbs down",
    "sanctus_adj": "smiling face with halo", "beatus": "smiling face with halo",
    "pax": "dove", "bellum": "crossed swords", "mors": "skull",
    "vita": "sparkling heart", "veritas": "check mark button", "via_abstract": "motorway",
    "lex": "balance scale", "iustitia": "balance scale", "iudicium": "balance scale",
    "potestas": "flexed biceps", "virtus": "flexed biceps",
    "sapientia": "owl", "scientia": "graduation cap", "ratio": "brain",
    "quaestio": "red question mark", "responsum": "speech balloon",
    "initium": "green circle", "finis": "end arrow",
    "et": "plus", "sed": "left-right arrow", "si": "red question mark",
    "quia": "right arrow", "ergo": "right arrow", "usque": "right arrow",
    "semper": "infinity", "numquam": "prohibited", "iterum": "counterclockwise arrows button",
    # The second round: the highest-frequency words the corpus left uncovered.
    # Function words get the symbol that stands in for them, the way the Hebrew
    # deck gives לֹא the prohibition sign; an abstract noun gets a picture only
    # where one sense is plainly the word's own -- persona takes the theatre
    # masks because that is what the word first meant.
    "ab": "left arrow", "ad": "right arrow", "ex": "left arrow",
    "per": "right arrow", "post": "right arrow", "ante": "left arrow",
    "supra": "up arrow", "infra": "down arrow", "inter": "left-right arrow",
    "contra": "crossed swords", "sine": "prohibited", "cum": "people holding hands",
    "jus": "balance scale", "ius": "balance scale", "canon": "straight ruler",
    "persona": "performing arts", "officium": "briefcase",
    "auctoritas": "judge", "concilium": "busts in silhouette",
    "synodus": "busts in silhouette", "societas": "people holding hands",
    "monasterium": "castle", "claustrum": "castle",
    "doctrina": "open book", "doctor": "teacher", "magister": "teacher",
    "discipulus": "student", "schola": "school", "studium": "open book",
    "scriptura": "scroll", "textus": "scroll", "verbum": "speech balloon",
    "sermo": "speaking head", "vox": "megaphone", "silentium": "shushing face",
    "memoria": "brain", "mens": "brain", "intellectus": "brain",
    "voluntas": "flexed biceps", "libertas": "dove",
    "labor": "hammer and wrench", "opus": "hammer and wrench",
    "instrumentum": "gear", "ordo": "input numbers", "gradus": "ladder",
    "locus": "round pushpin", "spatium": "world map", "orbis": "globe with meridians",
    "provincia": "world map", "dioecesis": "world map",
    "sepulcrum": "headstone", "sepultura": "coffin", "medicus": "hospital",
    "morbus": "pill", "sanitas": "green heart", "dolor": "crying face",
    "gaudium": "grinning face", "tristitia": "crying face", "ira": "angry face",
    "misericordia": "smiling face with open hands", "iustus": "balance scale",
    "sacrificium": "fire", "incensum": "fire", "cinis": "fire",
    "clamor": "megaphone", "cantica": "musical note", "tuba": "trumpet",
    "cithara": "harp", "tympanum": "drum",
    "numerus_ord": "input numbers", "mensura": "straight ruler",
    "figura": "triangular ruler", "linea": "straight ruler",
    "initium_alt": "green circle", "medius": "record button",
    # Third round.  An abstract adverb is left blank on purpose -- quasi, modo,
    # scilicet, potius have no picture that is theirs rather than an
    # illustration of a sentence they might appear in -- but a concrete noun
    # buried among them does not have to be.
    "uxor": "couple with heart", "maritus": "couple with heart",
    "matrimonium": "ring", "nuptiae": "ring", "sponsa": "ring",
    "religio": "folded hands", "haereticus": "cross mark",
    "epistola": "envelope", "historia": "books", "fabula": "books",
    "provincia_civil": "world map", "negotium": "briefcase",
    "possessio": "money bag", "pecunia_alt": "money bag",
    "periculum": "warning", "error": "confused face", "iniuria": "anguished face",
    "injuria": "anguished face", "aetas": "hourglass not done",
    "futurus": "spiral calendar", "praesentia": "round pushpin",
    "communitas": "people hugging", "populus_alt": "busts in silhouette",
    "civilis": "office building", "politicus": "classical building",
    "publicus": "busts in silhouette", "legatus": "postal horn",
    "consilium": "thought balloon", "consensus": "handshake",
    "concordia": "handshake", "pactum": "handshake",
    "fundamentum": "building construction", "aedificium": "office building",
    "status": "placard", "habitus": "t-shirt", "vestimentum": "t-shirt",
    "occasio": "door", "nomino": "label", "appello": "megaphone",
    "clamo": "megaphone", "nolo": "prohibited", "veto": "prohibited",
    "probo": "victory hand", "approbo": "victory hand",
    "praefero": "victory hand", "opera": "hammer and wrench",
    "soleo": "counterclockwise arrows button", "mos": "counterclockwise arrows button",
    "consuetudo": "counterclockwise arrows button",
    "forma": "triangular ruler", "figura_alt": "triangular ruler",
    "canonicus": "straight ruler", "moralis": "balance scale",
    "praesum": "crown", "praesideo": "crown", "dux": "crown",
    "longus": "straight ruler", "brevis": "pencil",
    "quaero": "magnifying glass tilted left", "invenio": "magnifying glass tilted left",
    "cur": "red question mark", "utrum": "red question mark",
    "necesse": "double exclamation mark", "certus": "check mark button",
    "dubito": "thinking face", "taceo": "shushing face",
    # Transfer inherits another deck's choice, which is the point of it, but a
    # borrowed picture can still be wrong here: itaque came back with the END
    # sign because some card glossed 因此、所以 carries it.  A conclusion is an
    # arrow forward, not a stop.
    "itaque": "right arrow", "ergo": "right arrow", "igitur": "right arrow",
    # The enclitic and the free-standing conjunction are the same idea and
    # should carry the same sign; -que had inherited a handshake.
    "-que": "plus", "atque": "plus", "ac": "plus",
    "ideo": "right arrow", "propterea": "right arrow",
}

# Homographs that only a macron separates need different pictures, so those are
# keyed on the whole dictionary line instead of the headword.
# 2026-08-27：逐義項借圖之後，接觸表看出來的錯配。借來的圖對得起借方的那個
# 義項，卻對不起這個字——「釋放」借到揮手、「留下」借到房子、ut 借到 🔚（跟
# itaque 當初一樣，結果的箭頭不是終點）。覆蓋規則先於借用，所以寫在這裡就好。
OVERRIDES.update({
    "libero": "raising hands",          # 解放：揮手是道別，不是釋放
    "reddo": "right arrow curving left",  # 歸還：不是「站著的人」
    "condo": "building construction",   # 創建：錨是望德，不是建立
    "resto": "hourglass not done",      # 殘留：房子是「留在家」，不是「尚存」
    "clino": "person bowing",           # 傾斜、躬身：露營帳篷純屬誤配
    "inclino": "person bowing",
    "ut": "bullseye",                 # 目的連接詞，與希臘 ἵνα 同符號
    "baptisma": "droplet",              # 與同冊 baptismus 同圖，浴缸不是洗禮
})

OVERRIDES_BY_FORMS: dict[str, str] = {
    "occīdō, occīdere, occīdī, occīsus": "dagger",
    "occidō, occidere, occidī, occāsus": "sunset",
    "praedicō, praedicāre, praedicāvī, praedicātus": "speaking head",
    "praedīcō, praedīcere, praedīxī, praedictus": "crystal ball",
}


def key_of(entry: dict) -> str:
    """The identity the vocabulary master itself deduplicates on."""
    return L.fold(entry.get("forms") or entry["headword"])


# 拉丁那本的中文用思高本，希伯來與希臘那兩本用《和合本修訂版》，所以同一個概念
# 在兩邊寫法不同，圖就借不過來。這張表只放兩邊確實同指一物的對子；不確定的不放。
CATHOLIC_TO_PROTESTANT = {
    "宗徒": "使徒", "聖神": "聖靈", "天神": "天使", "恩寵": "恩典",
    "默西亞": "彌賽亞", "法利塞": "法利賽", "撒殫": "撒但", "聖詠": "詩篇",
    "司祭": "祭司", "盟約": "約", "光榮": "榮耀", "義德": "公義",
}

SENSE_SPLIT = re.compile(r"[；、，,;]")


def senses(gloss: str) -> list[str]:
    """The gloss's senses, in the order it writes them.

    A Latin word's Chinese is usually several senses long, and only the first
    was ever looked up — so `libero`「解放、釋放」 borrowed nothing although
    「釋放」 was pictured, and `canticum`「聖歌、讚美詩」 nothing although
    「讚美詩」 was. Order matters and is preserved: the first sense is the
    word's core meaning and gets first refusal on a picture.
    """

    seen: list[str] = []
    for part in SENSE_SPLIT.split(gloss):
        part = part.strip()
        if part and part not in seen:
            seen.append(part)
    return seen


def borrowed_meanings() -> dict[str, str]:
    """Chinese meanings the Hebrew and Greek decks have already pictured."""
    meanings: dict[str, str] = {}
    for name in ("hebrew-card-images.json", "greek-card-images.json"):
        path = CACHE / name
        if not path.exists():
            continue
        for record in json.loads(path.read_text(encoding="utf-8"))["images"].values():
            gloss = (record.get("glossZh") or "").strip()
            for meaning in (gloss, gloss.split("；")[0].strip(), gloss.split("、")[0].strip()):
                if meaning:
                    meanings.setdefault(meaning, record["hexcode"])
    return meanings


def main() -> None:
    parser = argparse.ArgumentParser(description="替教會拉丁文單字卡挑圖，挑不到就留空")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    base.ensure_openmoji()
    entries = json.loads(VOCAB.read_text(encoding="utf-8"))["entries"]
    by_name = base.load_openmoji()
    borrowed = borrowed_meanings()
    print(f"  可借用的中文詞義 {len(borrowed)} 個")

    assigned: dict[str, dict] = {}
    borrowed_via: dict[str, str] = {}
    unresolved: list[str] = []
    sources = {"override": 0, "zh_transfer": 0, "annotation": 0, "none": 0}

    for entry in entries:
        card = key_of(entry)
        chosen = None
        source = "none"

        wanted = (OVERRIDES_BY_FORMS.get(entry.get("forms", ""))
                  or OVERRIDES.get(L.fold(entry["headword"])))
        if wanted:
            found = by_name.get(wanted.lower())
            if found and base.image_path(found["hexcode"]):
                chosen, source = found["hexcode"], "override"
            else:
                unresolved.append(f"{entry['headword']} -> {wanted!r}")

        if not chosen:
            gloss = (entry.get("glossZh") or "").strip()
            # Deliberately not named `key`: that holds this card's own identity,
            # and the Hebrew matcher once wrote a hundred and thirty-two entries
            # under their Chinese meaning by shadowing it here.
            for sense in [gloss, *senses(gloss)]:
                candidates = [sense]
                for catholic, protestant in CATHOLIC_TO_PROTESTANT.items():
                    if catholic in sense:
                        candidates.append(sense.replace(catholic, protestant))
                for candidate in candidates:
                    hexcode = borrowed.get(candidate)
                    if hexcode and base.image_path(hexcode):
                        chosen, source = hexcode, "zh_transfer"
                        borrowed_via[key_of(entry)] = candidate
                        break
                if chosen:
                    break

        if not chosen:
            for candidate in base.english_candidates(entry.get("glossEn") or ""):
                if candidate in base.AMBIGUOUS_EN:
                    continue
                found = by_name.get(candidate)
                if found and base.image_path(found["hexcode"]):
                    chosen, source = found["hexcode"], "annotation"
                    break

        sources[source] += 1
        if chosen:
            assigned[card] = {
                "hexcode": chosen,
                "file": base.image_path(chosen).name,
                "source": source,
                "headword": entry["headword"],
                "glossZh": entry.get("glossZh", ""),
                # 借來的圖記下是循哪一個義項借的，之後回頭稽核時才看得出
                # 這張圖對的是這個字的核心義還是末位義。
                **({"borrowedVia": borrowed_via[card]} if card in borrowed_via else {}),
            }

    # Every key must resolve, or the deck builder silently prints a blank card.
    identities = {key_of(entry) for entry in entries}
    stray = sorted(set(assigned) - identities)
    assert not stray, f"圖表出現詞表沒有的鍵：{stray[:5]}"

    total = len(entries)
    print(f"  人工指定 {sources['override']}，中文詞義轉移 {sources['zh_transfer']}，"
          f"本名比對 {sources['annotation']}，留空 {sources['none']}")
    print(f"  有圖合計 {len(assigned)} / {total} = {len(assigned) * 100 // total}%")
    for volume in ("上冊", "下冊"):
        rows = [e for e in entries if e["volume"] == volume]
        got = sum(1 for e in rows if key_of(e) in assigned)
        print(f"    {volume} {got}/{len(rows)} = {got * 100 // max(len(rows), 1)}%")
    if unresolved:
        print(f"  ⚠ 人工指定但查無此圖：{len(unresolved)}")
        for item in sorted(set(unresolved))[:20]:
            print(f"      {item}")

    uncovered = [
        (entry.get("corpusFrequency") or 0, entry["volume"], entry["lesson"],
         entry["headword"], entry.get("glossZh", ""))
        for entry in entries if key_of(entry) not in assigned
    ]
    uncovered.sort(reverse=True)
    print("\n  仍無圖、語料出現次數最高的 25 個：")
    for frequency, volume, lesson, headword, zh in uncovered[:25]:
        print(f"      {frequency:>6} {volume} L{lesson:<3} {headword:<18} {zh}")

    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(
            json.dumps({
                "schemaVersion": "1.0.0",
                "source": "OpenMoji 17.0.0",
                "licence": "CC BY-SA 4.0 — https://openmoji.org",
                "note": "每張卡最多一張圖，取該詞最常見的義項；挑不到就留空，不以近似圖充數。",
                "keyedOn": "詞條的完整字典形式（折疊拼寫），與詞表的去重鍵相同",
                "images": assigned,
            }, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"\n已寫出 {OUTPUT}")
    else:
        print("\n（未寫檔；加 --write 才會輸出）")


if __name__ == "__main__":
    main()
