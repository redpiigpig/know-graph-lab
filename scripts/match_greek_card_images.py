#!/usr/bin/env python3
"""Pick one OpenMoji picture per Greek flashcard, or leave the card blank.

Same rule as the Hebrew deck: a wrong picture on a printed card teaches a sense
the word does not carry, so the matcher would rather leave a blank. Greek adds
one pass the Hebrew deck could not use.

The two decks share a Chinese gloss vocabulary. When a Greek word's Chinese
meaning is one a Hebrew card already carries, the Hebrew card's picture is the
right picture for it too — πῦρ and אֵשׁ are both 「火」 and both want the flame.
That transfer costs nothing and inherits the hand-curation already done.

After it come the same English-name pass and the same refusal to guess.

Licence: OpenMoji 17.0.0, CC BY-SA 4.0 (https://openmoji.org).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from match_flashcard_images import (  # noqa: E402
    AMBIGUOUS_EN,
    CACHE,
    IMAGE_DIR,
    english_candidates,
    ensure_openmoji,
    image_path,
    load_openmoji,
)

ROOT = Path(__file__).resolve().parents[1]
VOCAB = ROOT / "data/originalReaders/vocabulary/greek-2000.json"
GLOSSES = ROOT / "output/source-cache/original-readers/greek-full/greek-2000-gloss-zh-by-lemma.json"
HEBREW_IMAGES = CACHE / "hebrew-card-images.json"
OUTPUT = CACHE / "greek-card-images.json"

# Greek words whose picture is worth naming by hand: the ones every reader meets
# first, and the function words no English gloss will match.
OVERRIDES: dict[str, str] = {
    "θεός": "palms up together",
    "κύριος": "crown",
    "Ἰησοῦς": "person",
    "ἄνθρωπος": "person",
    "ἀνήρ": "man",
    "γυνή": "woman",
    "υἱός": "boy",
    "θυγάτηρ": "girl",
    "πατήρ": "man",
    "μήτηρ": "woman",
    "ἀδελφός": "men holding hands",
    "ἀδελφή": "women holding hands",
    "τέκνον": "child",
    "παιδίον": "child",
    "λαός": "busts in silhouette",
    "ὄχλος": "busts in silhouette",
    "βασιλεύς": "crown",
    "δοῦλος": "construction worker",
    "ἄγγελος": "envelope with arrow",
    "προφήτης": "loudspeaker",
    "ἀπόστολος": "outbox tray",
    "μαθητής": "graduation cap",
    "ἱερεύς": "raising hands",
    "οἶκος": "house",
    "οἰκία": "house",
    "πόλις": "cityscape",
    "ἱερόν": "classical building",
    "ναός": "classical building",
    "θύρα": "door",
    "ὁδός": "motorway",
    "γῆ": "globe showing Europe-Africa",
    "οὐρανός": "cloud",
    "θάλασσα": "water wave",
    "ὄρος": "mountain",
    "ἔρημος": "desert",
    "ὕδωρ": "droplet",
    "πῦρ": "fire",
    "φῶς": "light bulb",
    "σκοτία": "new moon",
    "ἥλιος": "sun",
    "ἀστήρ": "star",
    "ἡμέρα": "sun",
    "νύξ": "night with stars",
    "ὥρα": "hourglass done",
    "ἔτος": "spiral calendar",
    "χρόνος": "hourglass done",
    "ἄρτος": "bread",
    "οἶνος": "wine glass",
    "ἰχθύς": "fish",
    "πρόβατον": "ewe",
    "ἀμνός": "ewe",
    "ποιμήν": "dog",
    "καρδία": "red heart",
    "ὀφθαλμός": "eye",
    "στόμα": "mouth",
    "χείρ": "hand with fingers splayed",
    "πούς": "foot",
    "κεφαλή": "brain",
    "οὖς": "ear",
    "αἷμα": "drop of blood",
    "σάρξ": "cut of meat",
    "σῶμα": "person standing",
    "ψυχή": "lungs",
    "πνεῦμα": "wind face",
    "φωνή": "speaker high volume",
    "λόγος": "speech balloon",
    "ῥῆμα": "speech balloon",
    "ὄνομα": "name badge",
    "βιβλίον": "open book",
    "γραφή": "scroll",
    "νόμος": "scroll",
    "ἐπιστολή": "envelope with arrow",
    "ἀργύριον": "coin",
    "χρυσός": "gem stone",
    "ἱμάτιον": "t-shirt",
    "ὑπόδημα": "man’s shoe",
    "μάχαιρα": "dagger",
    "σταυρός": "latin cross",
    "ποτήριον": "cup with straw",
    "τράπεζα": "fork and knife",
    "θρόνος": "chair",
    "λίθος": "rock",
    "δένδρον": "deciduous tree",
    "καρπός": "red apple",
    "σπέρμα": "seedling",
    "ἀγρός": "sheaf of rice",
    "ἄμπελος": "grapes",
    "λέγω": "speech balloon",
    "λαλέω": "speaking head",
    "ἀκούω": "ear",
    "βλέπω": "eyes",
    "ὁράω": "eyes",
    "γινώσκω": "brain",
    "οἶδα": "brain",
    "πιστεύω": "handshake",
    "ἀγαπάω": "two hearts",
    "φιλέω": "two hearts",
    "μισέω": "angry face",
    "θέλω": "thinking face",
    "ἔρχομαι": "door",
    "πορεύομαι": "person walking",
    "περιπατέω": "person walking",
    "τρέχω": "person running",
    "ἵστημι": "person standing",
    "κάθημαι": "chair",
    "ἐσθίω": "fork and knife",
    "πίνω": "cup with straw",
    "γράφω": "writing hand",
    "δίδωμι": "wrapped gift",
    "λαμβάνω": "raised fist",
    "ἀποστέλλω": "outbox tray",
    "εὑρίσκω": "magnifying glass tilted left",
    "ζητέω": "magnifying glass tilted left",
    "ποιέω": "hammer and wrench",
    "ἐργάζομαι": "hammer and wrench",
    "οἰκοδομέω": "building construction",
    "ἀποθνῄσκω": "skull",
    "θάνατος": "skull",
    "ζάω": "beating heart",
    "ζωή": "seedling",
    "γεννάω": "baby",
    "σῴζω": "ring buoy",
    "σωτηρία": "ring buoy",
    "κρίνω": "balance scale",
    "κρίσις": "balance scale",
    "δικαιοσύνη": "balance scale",
    "δίκαιος": "smiling face with halo",
    "ἅγιος": "sparkles",
    "ἁμαρτία": "broken heart",
    "ἁμαρτάνω": "broken heart",
    "εἰρήνη": "dove",
    "χαρά": "partying face",
    "χαίρω": "partying face",
    "κλαίω": "crying face",
    "φοβέομαι": "fearful face",
    "προσεύχομαι": "folded hands",
    "εὐχαριστέω": "raising hands",
    "δόξα": "glowing star",
    "δύναμις": "flexed biceps",
    "ἐξουσία": "crown",
    "σοφία": "brain",
    "ἀλήθεια": "hundred points",
    "πίστις": "handshake",
    "ἐλπίς": "seedling",
    "ἀγάπη": "two hearts",
    "χάρις": "wrapped gift",
    "διαθήκη": "handshake",
    "βασιλεία": "castle",
    "ἐκκλησία": "busts in silhouette",
    "εὐαγγέλιον": "megaphone",
    "πόλεμος": "crossed swords",
    "διάβολος": "smiling face with horns",
    "πονηρός": "smiling face with horns",
    "κακός": "angry face",
    "ἀγαθός": "thumbs up",
    "καλός": "thumbs up",
    "μέγας": "snow-capped mountain",
    "μικρός": "ant",
    "πολύς": "chart increasing",
    "πρῶτος": "1st place medal",
    "δεύτερος": "2nd place medal",
    "τρίτος": "3rd place medal",
    # 虛詞以符號會意
    "οὐ (οὐκ": "prohibited",
    "οὐ": "prohibited",
    "μή": "prohibited",
    "εἰς": "right arrow",
    "ἐκ (ἐξ)": "left arrow",
    "ἐν": "input latin letters",
    "ἐπί": "up arrow",
    "ὑπό": "down arrow",
    "σύν": "handshake",
    "μετά": "handshake",
    "διά": "right arrow curving down",
    "γάρ": "right arrow curving down",
    "ὅτι": "right arrow curving down",
    "ἵνα": "bullseye",
    "ἐάν": "shuffle tracks button",
    "εἰ": "shuffle tracks button",
    "ὥστε": "end arrow",
    "οὖν": "end arrow",
    "καί": "plus",
    "ἀλλά": "left-right arrow",
    "νῦν": "alarm clock",
    "ἤδη": "repeat button",
    "ἰδού": "eyes",
    "ἴδε": "eyes",
    "ἐγώ": "person raising hand",
    "σύ": "index pointing at the viewer",
    "ἡμεῖς": "people holding hands",
    "ὑμεῖς": "busts in silhouette",
    "οὗτος": "backhand index pointing down",
    "ἐκεῖνος": "backhand index pointing right",
    "τίς": "red question mark",
    "πᾶς": "bar chart",
    "εἷς": "keycap: 1",
    "δύο": "keycap: 2",
    "τρεῖς": "keycap: 3",
    "ὧδε": "round pushpin",
    "ἐκεῖ": "round pushpin",
    "οὐδείς": "hole",
    "ἀμήν": "check mark",
}


def first_sense(gloss: str) -> str:
    return gloss.split("；")[0].strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="替希臘文單字卡挑圖，挑不到就留空")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    ensure_openmoji()
    entries = json.loads(VOCAB.read_text(encoding="utf-8"))["entries"]
    glosses = {
        lemma: record["glossZh"]
        for lemma, record in json.loads(GLOSSES.read_text(encoding="utf-8"))["glosses"].items()
    }
    by_name = load_openmoji()

    hebrew = json.loads(HEBREW_IMAGES.read_text(encoding="utf-8"))["images"]
    # Chinese meaning -> picture, taken from the Hebrew deck's curated choices.
    by_meaning: dict[str, str] = {}
    for record in hebrew.values():
        for key in (record["glossZh"].strip(), first_sense(record["glossZh"])):
            by_meaning.setdefault(key, record["hexcode"])

    assigned: dict[str, dict] = {}
    unresolved: list[str] = []
    sources = {"override": 0, "zh_transfer": 0, "annotation": 0, "none": 0}

    for entry in entries:
        lemma = entry["lemma"]
        gloss = glosses.get(lemma, "")
        chosen = None
        source = "none"

        wanted = OVERRIDES.get(lemma)
        if wanted:
            found = by_name.get(wanted.lower())
            if found and image_path(found["hexcode"]):
                chosen, source = found["hexcode"], "override"
            else:
                unresolved.append(f"{lemma} -> {wanted!r}")

        if not chosen and gloss:
            for key in (gloss.strip(), first_sense(gloss)):
                hexcode = by_meaning.get(key)
                if hexcode and image_path(hexcode):
                    chosen, source = hexcode, "zh_transfer"
                    break

        if not chosen:
            for candidate in english_candidates(entry.get("glossEn") or ""):
                if candidate in AMBIGUOUS_EN:
                    continue
                found = by_name.get(candidate)
                if found and image_path(found["hexcode"]):
                    chosen, source = found["hexcode"], "annotation"
                    break

        sources[source] += 1
        if chosen:
            assigned[lemma] = {
                "hexcode": chosen,
                "file": image_path(chosen).name,
                "source": source,
                "glossZh": gloss,
                "volume": entry["volume"],
            }

    total = len(entries)
    print(f"  人工指定 {sources['override']}，中文詞義轉移 {sources['zh_transfer']}，"
          f"本名比對 {sources['annotation']}，留空 {sources['none']}")
    print(f"  有圖合計 {len(assigned)} / {total} = {len(assigned) * 100 // total}%")
    for volume in (1, 2):
        in_volume = [entry for entry in entries if entry["volume"] == volume]
        covered = sum(1 for entry in in_volume if entry["lemma"] in assigned)
        print(f"      第{volume}冊 {covered}/{len(in_volume)}")
    if unresolved:
        print(f"  ⚠ 人工指定但查無此圖：{len(unresolved)}")
        for item in sorted(set(unresolved))[:20]:
            print(f"      {item}")

    if args.write:
        OUTPUT.write_text(
            json.dumps(
                {
                    "schemaVersion": "1.0.0",
                    "source": "OpenMoji 17.0.0",
                    "licence": "CC BY-SA 4.0 — https://openmoji.org",
                    "note": "每張卡最多一張圖，取該詞最常見的義項；挑不到就留空。"
                            "zh_transfer 表示沿用中文詞義相同的希伯來卡用圖。",
                    "images": assigned,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"\n已寫出 {OUTPUT}")
    else:
        print("\n（未寫檔；加 --write 才會輸出）")


if __name__ == "__main__":
    main()
