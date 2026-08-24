#!/usr/bin/env python3
"""Pick one OpenMoji picture per Hebrew flashcard, or leave the card blank.

The deck is printed, so a wrong picture is worse than none: it teaches a sense
the word does not carry, and the learner cannot undo it. Matching therefore runs
in three passes, strictest first.

1. ``OVERRIDES`` — hand-chosen for the words that matter most, and named by the
   emoji's own name rather than a hexcode so a bad entry fails loudly instead of
   silently printing the wrong picture. Strong's English is archaic and lists
   every sense at once, so the frequent core vocabulary is picked by hand.
2. An exact match on the emoji's name, never on its tag list. Tags carry
   incidental words, which is how בַּיִת "house" first matched a potted plant and
   דֶּרֶךְ "way" matched an exploding head.
3. Nothing. The card prints without a picture.

``AMBIGUOUS_EN`` blocks English words whose senses diverge — "watch" the verb
against the wristwatch, "bear" the verb against the animal. Those may only come
from ``OVERRIDES``.

Licence: OpenMoji 17.0.0, CC BY-SA 4.0 (https://openmoji.org). The attribution
is printed on the deck's cover sheet.
"""

from __future__ import annotations

import argparse
import io
import json
import re
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOCAB = ROOT / "data/originalReaders/vocabulary/hebrew-1000.json"
GLOSSES = ROOT / "output/source-cache/original-readers/hebrew-full/hebrew-gloss-zh-reviewed-by-lemma.json"
CACHE = ROOT / "output/source-cache/flashcards"
OPENMOJI = CACHE / "openmoji.json"
IMAGE_DIR = CACHE / "openmoji-618"
OUTPUT = CACHE / "hebrew-card-images.json"

# English headwords whose senses split; only OVERRIDES may use them.
AMBIGUOUS_EN = {
    "watch", "bear", "close", "well", "right", "left", "kind", "fast", "light",
    "spring", "saw", "will", "may", "can", "lie", "mean", "fair", "fine", "just",
    "last", "like", "match", "mine", "present", "rest", "rose", "sound", "state",
    "second", "back", "bank", "bat", "bow", "box", "case", "count", "cross",
    "date", "draw", "even", "fall", "fly", "ground", "hide", "issue", "lead",
    "leaves", "mark", "mint", "order", "palm", "park", "part", "pitch", "plant",
    "point", "post", "race", "ring", "rock", "row", "scale", "seal", "set",
    "sign", "sink", "spell", "stalk", "stick", "story", "train", "wave", "wind",
    "yard", "arms", "band", "bill", "bolt", "charge", "club", "company", "court",
    "crane", "current", "die", "fan", "figure", "file", "form", "hand", "head",
    "jam", "key", "letter", "line", "log", "nail", "note", "novel", "object",
    "pen", "pool", "pupil", "reason", "record", "ruler", "school", "season",
    "space", "spirit", "star", "table", "tie", "tip", "trunk", "type",
}

# Hand-picked pictures, keyed by Strong number.  The comment is the Chinese
# sense the picture carries — always the word's commonest one.
#
# יְהוָה is deliberately absent: putting a picture on the Divine Name is the
# reader's decision, not this script's.
OVERRIDES: dict[str, str] = {
    # 人與親屬
    "H120": "person",
    "H1": "man",
    "H517": "woman",
    "H1121": "boy",
    "H1323": "girl",
    "H251": "men holding hands",
    "H269": "women holding hands",
    "H376": "man",
    "H802": "woman",
    "H4940": "family",
    "H3206": "child",
    "H5288": "boy",
    "H5291": "girl",
    "H490": "older person",
    "H2205": "older person",
    "H5971": "busts in silhouette",
    "H5650": "construction worker",
    "H4428": "crown",
    "H3548": "raising hands",
    "H5030": "loudspeaker",
    "H4397": "envelope with arrow",
    "H7453": "handshake",
    "H1616": "luggage",
    # 身體
    "H3820": "red heart",
    "H5869": "eye",
    "H6310": "mouth",
    "H3027": "hand with fingers splayed",
    "H7218": "brain",
    "H1818": "drop of blood",
    "H6106": "bone",
    "H1320": "cut of meat",
    "H5315": "lungs",
    "H6440": "slightly smiling face",
    "H639": "nose",
    # 自然與天象
    "H776": "globe showing Europe-Africa",
    "H8064": "cloud",
    "H8121": "sun",
    "H3394": "crescent moon",
    "H3556": "star",
    "H216": "light bulb",
    "H2822": "new moon",
    "H4325": "droplet",
    "H784": "fire",
    "H7307": "wind face",
    "H2022": "mountain",
    "H3220": "water wave",
    "H5104": "national park",
    "H875": "hole",
    "H4057": "desert",
    "H7704": "sheaf of rice",
    "H6086": "deciduous tree",
    "H68": "rock",
    "H1653": "cloud with rain",
    "H4306": "cloud with rain",
    "H3915": "night with stars",
    "H1242": "sunrise",
    "H6153": "sunset",
    "H3117": "sun",
    "H8141": "spiral calendar",
    "H2320": "new moon",
    # 動物
    "H5483": "horse",
    "H6629": "ewe",
    "H1241": "cow",
    "H7794": "ox",
    "H2543": "horse face",
    "H5175": "snake",
    "H3123": "dove",
    # 器物與建築
    "H1004": "house",
    "H5892": "cityscape",
    "H168": "tent",
    "H8179": "door",
    "H7023": "brick",
    "H4196": "moai",
    "H3627": "amphora",
    "H3563": "cup with straw",
    "H899": "t-shirt",
    "H2719": "dagger",
    "H5612": "scroll",
    "H8451": "scroll",
    "H2091": "gem stone",
    "H3701": "coin",
    "H1270": "chains",
    # 食物
    "H3899": "bread",
    "H3196": "wine glass",
    "H2132": "olive",
    "H8492": "grapes",
    "H8184": "sheaf of rice",
    # 動作
    "H1980": "person walking",
    "H3212": "person walking",
    "H3427": "chair",
    "H5975": "person standing",
    "H7901": "bed",
    "H398": "fork and knife",
    "H8354": "cup with straw",
    "H1058": "crying face",
    "H7832": "grinning face with smiling eyes",
    "H3372": "fearful face",
    "H157": "two hearts",
    "H8130": "angry face",
    "H1984": "raising hands",
    "H6419": "folded hands",
    "H3789": "writing hand",
    "H7121": "loudspeaker",
    "H559": "speech balloon",
    "H1696": "speaking head",
    "H8085": "ear",
    "H7200": "eyes",
    "H3045": "brain",
    "H2803": "thinking face",
    "H1245": "magnifying glass tilted left",
    "H4672": "magnifying glass tilted left",
    "H5414": "wrapped gift",
    "H3947": "raised fist",
    "H7971": "outbox tray",
    "H935": "door",
    "H3318": "person walking",
    "H5927": "up arrow",
    "H3381": "down arrow",
    "H7725": "counterclockwise arrows button",
    "H4191": "skull",
    "H4194": "skull",
    "H2421": "beating heart",
    "H2416": "seedling",
    "H3205": "baby",
    "H1129": "building construction",
    "H6213": "hammer and wrench",
    "H5647": "hammer and wrench",
    "H4399": "hammer and wrench",
    "H8104": "shield",
    "H4390": "bucket",
    "H5674": "bridge at night",
    "H6605": "unlocked",
    "H5462": "locked",
    "H7311": "up arrow",
    "H1288": "raising hands",
    "H779": "speaking head",
    "H7462": "dog",
    "H2076": "ewe",
    "H5930": "fire",
    "H4503": "wrapped gift",
    "H3898": "crossed swords",
    "H5162": "people hugging",
    "H3467": "ring buoy",
    # 抽象
    "H1697": "speech balloon",
    "H6963": "speaker high volume",
    "H2451": "brain",
    "H2617": "revolving hearts",
    "H571": "hundred points",
    "H539": "handshake",
    "H6664": "balance scale",
    "H4941": "balance scale",
    "H8199": "balance scale",
    "H7965": "dove",
    "H1285": "handshake",
    "H6944": "sparkles",
    "H6942": "sparkles",
    "H2403": "broken heart",
    "H2398": "broken heart",
    "H5771": "broken heart",
    "H4421": "crossed swords",
    "H7451": "angry face",
    "H2896": "thumbs up",
    "H1419": "snow-capped mountain",
    "H6996": "ant",
    "H7227": "chart increasing",
    "H3966": "collision",
    "H3605": "bar chart",
    "H3477": "straight ruler",
    "H7676": "couch and lamp",
    "H6453": "ewe",
    "H2233": "seedling",
    # 數詞
    "H702": "keycap: 4",
    "H2568B": "keycap: 5",
    "H8337": "keycap: 6",
    "H8083": "keycap: 8",
    "H6235": "keycap: 10",
    "H6242": "input numbers",
    "H7970": "input numbers",
    "H705": "input numbers",
    "H2572": "input numbers",
    "H4557": "input numbers",
    "H5608": "abacus",
    "H7223": "1st place medal",
    "H8145": "2nd place medal",
    "H7992": "3rd place medal",
    "H2677": "last quarter moon",
    # 身體與人
    "H3824": "anatomical heart",
    "H7272": "foot",
    "H3709": "raised hand",
    "H241": "ear",
    "H905": "bust in silhouette",
    "H587": "people holding hands",
    "H3162": "people holding hands",
    "H1368": "person fencing",
    "H2450": "graduation cap",
    "H1060": "keycap: 1",
    # 動作
    "H6485": "clipboard",
    "H3772": "scissors",
    "H2388": "flexed biceps",
    "H3581": "flexed biceps",
    "H5186": "open hands",
    "H5800": "waving hand",
    "H5337": "SOS button",
    "H7812": "person bowing",
    "H995": "puzzle piece",
    "H977": "ballot box with ballot",
    "H2026": "skull and crossbones",
    "H5127": "person running",
    "H7323": "person running",
    "H7291": "footprints",
    "H8055": "partying face",
    "H5437": "clockwise vertical arrows",
    "H6437": "clockwise vertical arrows",
    "H3680": "umbrella",
    "H7665": "hammer",
    "H7843": "bomb",
    "H5265": "backpack",
    "H6912": "coffin",
    "H7993": "baseball",
    "H954": "flushed face",
    "H3513": "person lifting weights",
    "H6": "wilted flower",
    "H1540": "spiral notepad",
    "H4687": "spiral notepad",
    # 名物
    "H6256": "hourglass done",
    "H227": "hourglass done",
    "H4150": "calendar",
    "H2428": "money bag",
    "H3423": "key",
    "H5159": "house with garden",
    "H7931": "house with garden",
    "H3559": "anchor",
    "H4264": "camping",
    "H2583": "camping",
    "H2691": "houses",
    "H4639": "briefcase",
    "H2142": "thought balloon",
    "H3519": "glowing star",
    "H929": "water buffalo",
    "H3532": "ram",
    "H2077": "goat",
    "H2351": "railway track",
    "H1366": "world map",
    "H520": "triangular ruler",
    "H7393": "racing car",
    "H6529": "red apple",
    "H4467": "castle",
    "H5982": "classical building",
    "H6083": "dashing away",
    "H4758": "crystal ball",
    "H622": "basket",
    # 品格與抽象
    "H7563": "smiling face with horns",
    "H6662": "smiling face with halo",
    "H2930": "biohazard",
    "H2490": "biohazard",
    "H8441": "nauseated face",
    "H8267": "lying face",
    "H2534": "anger symbol",
    "H389": "red exclamation mark",
    "H7535": "red exclamation mark",
    "H3644": "heavy equals sign",
    "H6435": "warning",
    "H3201": "check mark",
    "H3426": "check mark",
    "H5178": "3rd place medal",
    "H5045": "desert",
    "H2005": "eyes",
    "H5493": "arrow turn right",
    "H341": "angry face with horns",
    "H6862": "angry face with horns",
    "H4616": "bullseye",
    "H4294": "axe",
    "H7626": "axe",
    "H7235": "chart increasing",
    "H1431": "chart increasing",
    "H7230": "chart increasing",
    "H7130": "package",
    "H127": "brown circle",
    "H3254": "plus",
    "H8081": "oil drum",
    "H3706": "memo",
    "H2706": "memo",
    "H2708": "memo",
    "H5608": "abacus",
    "H2346": "brick",
    "H6908": "basket",
    "H5712": "busts in silhouette",
    "H6951": "busts in silhouette",
    "H5656": "hammer and wrench",
    "H5066": "right arrow",
    "H5060": "index pointing up",
    "H5048": "left-right arrow",
    "H8432": "left-right arrow",
    "H3225": "backhand index pointing right",
    "H4605": "up arrow",
    "H4908": "tent",
    "H5158": "water wave",
    "H1116": "mountain",
    "H4054": "herb",
    "H6666": "balance scale",
    "H6918": "sparkles",
    "H3722": "folded hands",
    "H1350": "handshake",
    "H8548": "repeat button",
    "H3498": "package",
    "H7604": "package",
    "H8313": "fire",
    "H6999": "fire",
    "H8210": "droplet",
    "H3847": "t-shirt",
    "H3190": "thumbs up",
    "H1115": "prohibited",
    "H3034": "raising hands",
    "H5012": "loudspeaker",
    "H982": "handshake",
    "H3920": "raised fist",
    "H312": "shuffle tracks button",
    "H1875": "magnifying glass tilted left",
    "H7592": "red question mark",
    "H6607": "door",
    "H2351": "railway track",
    "H1755": "family",
    "H4193": "skull",
    "H7650": "person raising hand",
    "H4639": "briefcase",
    # 虛詞、代名詞、數詞 —— 以符號會意
    "H853": "backhand index pointing right",
    "H5921": "up arrow",
    "H413": "right arrow",
    "H4480": "left arrow",
    "H834": "link",
    "H3808": "prohibited",
    "H369": "hole",
    "H3588": "right arrow curving down",
    "H3651": "end arrow",
    "H518": "shuffle tracks button",
    "H5704": "stop sign",
    "H5973": "handshake",
    "H2088": "backhand index pointing down",
    "H1931": "backhand index pointing right",
    "H859": "index pointing at the viewer",
    "H589": "person raising hand",
    "H2009": "eyes",
    "H8033": "round pushpin",
    "H6311": "round pushpin",
    "H1961": "counterclockwise arrows button",
    "H8034": "name badge",
    "H1571": "plus",
    "H4100": "red question mark",
    "H428": "backhand index pointing down",
    "H408": "prohibited",
    "H310": "BACK arrow",
    "H1870": "motorway",
    "H5375": "person lifting weights",
    "H6965": "person standing",
    "H2063": "backhand index pointing down",
    "H7760": "pushpin",
    "H3967": "abacus",
    "H3541": "backhand index pointing down",
    "H1471": "globe with meridians",
    "H1992": "busts in silhouette",
    "H8478": "down arrow",
    "H505": "abacus",
    "H5221": "oncoming fist",
    "H3318": "door",
    "H6440": "slightly smiling face",
    "H430": "palms up together",
    "H410": "palms up together",
    "H136": "palms up together",
    "H7999": "check mark",
    "H1980": "footprints",
    "H7126": "arrow turn right",
    "H5307": "person kneeling",
    "H3615": "end arrow",
    "H4325": "droplet",
    "H6680": "megaphone",
    "H5750": "repeat button",
    "H6635": "military helmet",
    "H5769": "infinity",
    "H6258": "alarm clock",
    "H4310": "red question mark",
    "H8432": "left-right arrow",
    "H996": "left-right arrow",
    "H4994": "folded hands",
    "H4725": "round pushpin",
    "H7651": "keycap: 7",
    "H2568": "keycap: 5",
    "H6240": "keycap: 10",
    "H5002": "right anger bubble",
    "H5046": "megaphone",
    "H595": "person raising hand",
    "H4427": "crown",
    "H6030": "speech balloon",
    "H113": "necktie",
    "H176": "shuffle tracks button",
    "H3548B": "raising hands",
    "H4390B": "bucket",
    "H259": "keycap: 1",
    "H8147": "keycap: 2",
    "H7969": "keycap: 3",
}


OPENMOJI_VERSION = "17.0.0"
OPENMOJI_DATA = "https://raw.githubusercontent.com/hfg-gmuend/openmoji/master/data/openmoji.json"
OPENMOJI_ZIP = f"https://github.com/hfg-gmuend/openmoji/releases/download/{OPENMOJI_VERSION}/openmoji-618x618-color.zip"
USER_AGENT = {"User-Agent": "know-graph-lab/1.0 (private study flashcards)"}


def ensure_openmoji() -> None:
    """Fetch the artwork if it is not on disk; it is deliberately not in git."""

    CACHE.mkdir(parents=True, exist_ok=True)
    if not OPENMOJI.exists():
        print("  下載 openmoji.json …")
        request = urllib.request.Request(OPENMOJI_DATA, headers=USER_AGENT)
        OPENMOJI.write_bytes(urllib.request.urlopen(request, timeout=180).read())
    if not IMAGE_DIR.exists() or not any(IMAGE_DIR.glob("*.png")):
        print(f"  下載 OpenMoji {OPENMOJI_VERSION} 618×618 圖檔（約 44 MB）…")
        request = urllib.request.Request(OPENMOJI_ZIP, headers=USER_AGENT)
        payload = urllib.request.urlopen(request, timeout=900).read()
        IMAGE_DIR.mkdir(parents=True, exist_ok=True)
        zipfile.ZipFile(io.BytesIO(payload)).extractall(IMAGE_DIR)


def load_openmoji() -> dict[str, dict]:
    entries = json.loads(OPENMOJI.read_text(encoding="utf-8"))
    by_name: dict[str, dict] = {}
    preferred = {"objects", "animals-nature", "food-drink", "travel-places", "symbols", "activities"}
    for entry in entries:
        if entry.get("group") == "flags" or entry.get("skintone"):
            continue
        name = (entry.get("annotation") or "").strip().lower()
        if not name:
            continue
        current = by_name.get(name)
        if current is None or (entry.get("group") in preferred and current.get("group") not in preferred):
            by_name[name] = entry
    return by_name


def english_candidates(gloss_en: str) -> list[str]:
    text = re.sub(r"\([^)]*\)", " ", (gloss_en or "").lower())
    out: list[str] = []
    for segment in re.split(r"[;,]", text):
        segment = re.sub(r"[^a-z\s\-]", " ", segment).strip()
        segment = re.sub(r"^(a|an|the|to be|to|of|by|in)\s+", "", segment).strip()
        if not segment:
            continue
        out.append(segment)
        words = segment.split()
        if len(words) > 1:
            out.append(words[-1])
    return out


def image_path(hexcode: str) -> Path | None:
    for candidate in (hexcode, f"{hexcode}-FE0F"):
        path = IMAGE_DIR / f"{candidate}.png"
        if path.exists():
            return path
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="替希伯來單字卡挑圖，挑不到就留空")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    ensure_openmoji()
    vocab = json.loads(VOCAB.read_text(encoding="utf-8"))
    glosses = {
        (item["strong"], item["pointed"]): item["glossZh"]
        for item in json.loads(GLOSSES.read_text(encoding="utf-8"))["items"]
    }
    by_name = load_openmoji()

    assigned: dict[str, dict] = {}
    unresolved: list[str] = []
    sources = {"override": 0, "annotation": 0, "none": 0}

    for entry in vocab:
        key = f"{entry['strong']}|{entry['pointed']}"
        chosen = None
        source = "none"
        wanted = OVERRIDES.get(entry["strong"])
        if wanted:
            found = by_name.get(wanted.lower())
            path = image_path(found["hexcode"]) if found else None
            if path:
                chosen, source = found["hexcode"], "override"
            else:
                unresolved.append(f"{entry['strong']} -> {wanted!r}")
        if not chosen:
            for candidate in english_candidates(entry.get("glossEn") or ""):
                if candidate in AMBIGUOUS_EN:
                    continue
                found = by_name.get(candidate)
                if found:
                    path = image_path(found["hexcode"])
                    if path:
                        chosen, source = found["hexcode"], "annotation"
                        break
        sources[source] += 1
        if chosen:
            assigned[key] = {
                "hexcode": chosen,
                "file": image_path(chosen).name,
                "source": source,
                "glossZh": glosses[(entry["strong"], entry["pointed"])],
            }

    print(f"  人工指定 {sources['override']}，本名比對 {sources['annotation']}，留空 {sources['none']}")
    print(f"  有圖合計 {len(assigned)} / {len(vocab)} = {len(assigned) * 100 // len(vocab)}%")
    if unresolved:
        print(f"  ⚠ 人工指定但查無此圖：{len(unresolved)}")
        for item in sorted(set(unresolved))[:20]:
            print(f"      {item}")

    uncovered = [
        (entry.get("frequency") or 0, entry["pointed"], glosses[(entry["strong"], entry["pointed"])], entry["strong"])
        for entry in vocab
        if f"{entry['strong']}|{entry['pointed']}" not in assigned
    ]
    uncovered.sort(reverse=True)
    print("\n  仍無圖、出現次數最高的 25 個：")
    for frequency, pointed, zh, strong in uncovered[:25]:
        print(f"      {frequency:>5} {strong:<7} {pointed:<12} {zh}")

    if args.write:
        OUTPUT.write_text(
            json.dumps(
                {
                    "schemaVersion": "1.0.0",
                    "source": "OpenMoji 17.0.0",
                    "licence": "CC BY-SA 4.0 — https://openmoji.org",
                    "note": "每張卡最多一張圖，取該詞最常見的義項；挑不到就留空，不以近似圖充數。",
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
