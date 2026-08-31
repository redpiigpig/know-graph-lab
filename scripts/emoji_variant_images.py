#!/usr/bin/env python3
"""同一個概念換一套畫法，讓「同一語言內一張圖只出現在一張卡上」做得到。

owner 2026-08-31：「那就不要圖重複，去找幾種不同的來源。」

**這一層跟上一輪的 Iconify 那層是兩回事，差別決定了要不要逐張審。**
上一輪是拿英文詞義去找「名字碰巧對得上的另一個概念」，所以配出來的是
垃圾桶配「永遠」、瑞士刀配「軍隊」——換掉的是意思，七成是錯的。
這一層**概念完全沒動**，換的只是畫法：twemoji 的狗還是狗，noto 的狗還是狗。
所以它不需要人一張一張看，只需要確認那一套的圖能正常上色（見下）。

九套彩色 emoji，命名互通（`dog`、`folded-hands`、`prohibited` 各套都叫同一個名
字），合計約兩萬四千張圖、七千多個概念：

    openmoji           4,544  CC BY-SA 4.0    本專案原本就在用的那套
    twemoji            3,988  CC BY 4.0       Twitter，平面
    noto               3,710  Apache 2.0      Google
    fluent-emoji-flat  3,145  MIT             Microsoft 平面版
    noto-v1            2,162  Apache 2.0      Google 舊版，畫法與新版不同
    emojione           1,834  CC BY 4.0
    emojione-v1        1,262  CC BY-SA 4.0
    fxemoji            1,034  Apache 2.0      Firefox OS
    streamline-emojis    787  CC BY 4.0       線條最細，排最後

**`fluent-emoji`（3D 那套，3,126 張）刻意不收。** 它的 SVG 用了漸層與內嵌點陣，
PyMuPDF 一律 render 成全黑剪影——五個概念抓下來全是黑影。那不會報錯，會安靜地
印出一張純黑的卡。任何新增的圖庫都要先跑 `--probe` 看圖再收。

    python scripts/emoji_variant_images.py --probe dog folded-hands   # 看各套畫法
    python scripts/emoji_variant_images.py --lang hbo                 # 只算不下載
    python scripts/emoji_variant_images.py --lang hbo --write
"""

from __future__ import annotations

import argparse
import collections
import importlib.util
import json
import time
import urllib.request
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output/source-cache/flashcards"
VARIANT_DIR = CACHE / "emoji-variants"
NAME_INDEX = CACHE / "iconify/_emoji-names.json"
API = "https://api.iconify.design"
UA = {"User-Agent": "know-graph-lab/1.0 (private study flashcards)"}

# 順序即偏好序：越前面畫法越接近 OpenMoji，所以最常被用到的那幾套看起來最像。
# streamline-emojis 線條最細、印出來最淡，排最後。
SET_ORDER = ["twemoji", "noto", "fluent-emoji-flat", "noto-v1",
             "emojione", "emojione-v1", "fxemoji", "streamline-emojis"]
ALL_SETS = ["openmoji"] + SET_ORDER

LICENSES = {
    "openmoji": "CC BY-SA 4.0 — OpenMoji",
    "twemoji": "CC BY 4.0 — Twitter Emoji",
    "noto": "Apache 2.0 — Noto Emoji",
    "fluent-emoji-flat": "MIT — Fluent Emoji Flat",
    "noto-v1": "Apache 2.0 — Noto Emoji (v1)",
    "emojione": "CC BY 4.0 — Emoji One",
    "emojione-v1": "CC BY-SA 4.0 — Emoji One (v1)",
    "fxemoji": "Apache 2.0 — Firefox OS Emoji",
    "streamline-emojis": "CC BY 4.0 — Streamline Emojis",
}

# ── 第二層：同概念的九套畫法用完之後，改用「同一件事的另一個符號」 ────────────
#
# 這一層跟上面那層**性質不同，所以要人看過**：它動到了概念。放進來的兄弟必須是
# 同一個語意場裡的另一個符號，而且不可以主張相反的意思、也不可以帶進一個具體的
# 錯值——`input numbers` 那一團的卡是「五十、十二、二十、三十」，給它 keycap-7
# 就是在教 7，所以那一團只收不指定數目的計數符號（算盤、尺、輸入符號）。
#
# 同理不收膚色變體（`folded-hands-dark` 那一類）：拿膚色去區分兩張卡，學的人
# 什麼也沒多學到，而且那不是這副卡要教的東西。
FAMILIES: dict[str, list[str]] = {
    # 功能詞：方向與關係的記號，本來就是任取一個，彼此不衝突。
    "right arrow": ["up-right-arrow", "right-arrow-curving-up", "right-arrow-curving-down",
                    "left-right-arrow", "up-down-arrow", "up-arrow", "soon-arrow",
                    "top-arrow", "on-arrow", "play-button", "fast-forward-button"],
    "end arrow": ["top-arrow", "soon-arrow", "on-arrow", "chequered-flag", "stop-button",
                  "last-track-button", "bullseye", "back-arrow"],
    "left-right arrow": ["up-down-arrow", "repeat-button", "clockwise-left-right-arrows",
                         "shuffle-tracks-button"],
    "down arrow": ["down-right-arrow", "down-left-arrow", "right-arrow-curving-down"],
    "arrow turn right": ["right-arrow-curving-up", "right-arrow-curving-left", "back-arrow"],
    "right arrow curving down": ["right-arrow-curving-up", "right-arrow-curving-left",
                                 "down-right-arrow"],
    "forward": ["fast-forward-button", "next-track-button", "play-button"],
    "counterclockwise arrows button": ["repeat-button", "repeat-single-button",
                                       "clockwise-vertical-arrows", "recycling-symbol"],
    "circled anticlockwise arrow": ["repeat-button", "recycling-symbol", "back-arrow"],
    "shuffle tracks button": ["clockwise-left-right-arrows", "repeat-button", "left-right-arrow",
                              "repeat-single-button"],
    # 否定：原本所有「不」字共用一個禁止符號，現在各拿一個不同的禁止記號。
    "prohibited": ["cross-mark", "no-entry", "person-gesturing-no", "cross-mark-button",
                   "no-pedestrians", "no-littering", "stop-sign", "japanese-prohibited-button"],
    "empty nest": ["hole", "wastebasket", "black-circle", "white-circle", "wilted-flower",
                   "broken-heart", "desert", "dashing-away"],
    # 祈禱與敬拜。
    "folded hands": ["raising-hands", "place-of-worship", "prayer-beads", "church",
                     "person-kneeling", "candle", "person-bowing", "synagogue", "menorah"],
    "raising hands": ["person-raising-hand", "clapping-hands", "heart-hands", "open-hands"],
    "person bowing": ["person-kneeling", "person-raising-hand", "place-of-worship"],
    "smiling face with halo": ["baby-angel", "dove", "sparkles", "glowing-star"],
    # 手與人際。
    "handshake": ["people-holding-hands", "people-hugging", "busts-in-silhouette",
                  "two-men-holding-hands", "two-women-holding-hands", "family",
                  "couple-with-heart", "link"],
    "open hands": ["palms-up-together", "clapping-hands", "hand-with-fingers-splayed",
                   "raising-hands", "heart-hands", "handshake"],
    "help others": ["handshake", "raising-hands", "person-raising-hand", "heart-hands",
                    "people-hugging", "hugging-face", "ring-buoy"],
    "people hugging": ["couple-with-heart", "people-holding-hands", "two-women-holding-hands",
                       "busts-in-silhouette"],
    "people holding hands": ["two-men-holding-hands", "two-women-holding-hands",
                             "couple-with-heart", "family"],
    "heart hands": ["red-heart", "sparkling-heart", "two-hearts", "growing-heart"],
    "raised fist": ["flexed-biceps", "oncoming-fist", "left-facing-fist", "right-facing-fist"],
    "busts in silhouette": ["bust-in-silhouette", "people-holding-hands", "family",
                            "people-hugging", "two-women-holding-hands", "person-standing",
                            "men-holding-hands"],
    "person standing": ["bust-in-silhouette", "person-walking", "older-person"],
    "man": ["bust-in-silhouette", "person-beard", "man-bald", "older-person"],
    "person raising hand": ["person-tipping-hand", "raising-hands", "person-gesturing-ok"],
    "person with crown": ["prince", "princess", "crown", "person-wearing-turban"],
    # 確認與真實。
    "check mark": ["check-mark-button", "heavy-check-mark", "white-heavy-check-mark",
                   "ok-button", "ok-hand", "thumbs-up", "ballot-box-with-check"],
    "check mark button": ["heavy-check-mark", "white-heavy-check-mark", "ok-button"],
    "hundred points": ["check-mark-button", "gem-stone", "trophy", "glowing-star",
                       "sparkles", "bullseye", "sports-medal"],
    "safety": ["shield", "ring-buoy", "rescue-workers-helmet", "locked"],
    # 疑問。
    "red question mark": ["white-question-mark", "question-mark", "exclamation-question-mark",
                          "thinking-face", "person-shrugging"],
    "white question mark": ["question-mark", "exclamation-question-mark", "thinking-face"],
    "red exclamation mark": ["white-exclamation-mark", "double-exclamation-mark",
                             "exclamation-mark"],
    "thinking face": ["thought-balloon", "face-with-monocle", "person-shrugging",
                      "nerd-face", "brain"],
    "thought balloon": ["speech-balloon", "left-speech-bubble", "eye-in-speech-bubble",
                        "brain"],
    "speech balloon": ["left-speech-bubble", "speaking-head", "thought-balloon",
                       "eye-in-speech-bubble"],
    "speaking head": ["left-speech-bubble", "megaphone", "loudspeaker", "postal-horn"],
    # 心智與知識。
    "brain": ["light-bulb", "thinking-face", "face-with-monocle", "nerd-face", "books",
              "open-book", "graduation-cap", "key", "eye-in-speech-bubble"],
    "eyes": ["eye", "eye-in-speech-bubble", "magnifying-glass-tilted-left",
             "magnifying-glass-tilted-right", "telescope", "glasses", "face-with-monocle"],
    # 數與量。這一團只收「不指定數目」的計數符號。
    "input numbers": ["abacus", "bar-chart", "chart-increasing", "straight-ruler"],
    "chart increasing": ["bar-chart", "heavy-plus-sign", "up-arrow", "up-right-arrow",
                         "top-arrow"],
    "sort": ["card-index-dividers", "bookmark-tabs", "abacus", "clipboard",
             "straight-ruler", "ladder"],
    "plus": ["heavy-plus-sign", "heavy-multiplication-x", "asterisk"],
    "infinity": ["hourglass-done", "hourglass-not-done", "alarm-clock", "timer-clock",
                 "mantelpiece-clock", "watch", "spiral-calendar", "recycling-symbol",
                 "evergreen-tree", "rock"],
    "keycap: 1": ["1st-place-medal", "top-arrow", "sunrise", "new-button", "egg",
                  "baby", "seedling"],
    "heavy equals sign": ["wavy-dash", "left-right-arrow", "repeat-button",
                          "heavy-minus-sign", "heavy-division-sign", "link"],
    # 器物與抽象。
    "hammer and wrench": ["hammer", "wrench", "carpentry-saw", "screwdriver", "pick",
                          "toolbox", "gear", "nut-and-bolt", "hammer-and-pick"],
    "balance scale": ["classical-building", "scroll", "ballot-box-with-ballot", "judge",
                      "police-officer", "chains"],
    "puzzle piece": ["gear", "abacus", "link", "chains", "nut-and-bolt", "clamp"],
    "round pushpin": ["pushpin", "triangular-flag", "world-map", "compass",
                      "globe-showing-europe-africa", "black-small-square"],
    "pinching hand": ["small-blue-diamond", "white-small-square", "black-small-square",
                      "droplet", "ant", "mouse"],
    "bullseye": ["direct-hit", "chequered-flag", "trophy", "goal-net"],
    "straight ruler": ["triangular-ruler", "abacus", "compass", "pencil"],
    "sparkles": ["glowing-star", "star", "dizzy", "high-voltage", "sun-with-face"],
    "rock": ["mountain", "brick", "moai", "gem-stone"],
    "receipt": ["scroll", "page-with-curl", "ledger", "clipboard"],
    "ring buoy": ["anchor", "shield", "rescue-workers-helmet", "locked"],
    "stairway": ["ladder", "mountain", "up-arrow", "office-building"],
    "smiling face with horns": ["angry-face-with-horns", "goblin", "ogre", "skull"],
    "face with symbols on mouth": ["angry-face", "pouting-face", "face-with-steam-from-nose",
                                   "right-anger-bubble"],
    "partying face": ["party-popper", "confetti-ball", "balloon"],
    "backhand index pointing right": ["backhand-index-pointing-up", "index-pointing-up",
                                      "backhand-index-pointing-down"],
}

LANGS = {
    "hbo": {"decks": ["hbo"], "output": CACHE / "hebrew-card-variants.json"},
    "grc": {"decks": ["grc1", "grc2"], "output": CACHE / "greek-card-variants.json"},
    "lat": {"decks": ["lat1", "lat2"], "output": CACHE / "latin-card-variants.json"},
}


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fetch(url: str) -> bytes:
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()


def emoji_names() -> dict[str, set[str]]:
    """九套的完整名字清單，抓一次存本機，之後全在本機比對。"""

    if NAME_INDEX.exists():
        return {k: set(v) for k, v in json.loads(NAME_INDEX.read_text(encoding="utf-8")).items()}
    index: dict[str, list[str]] = {}
    for prefix in ALL_SETS:
        payload = json.loads(fetch(f"{API}/collection?prefix={prefix}"))
        listed = list(payload.get("uncategorized") or [])
        for group in (payload.get("categories") or {}).values():
            listed.extend(group)
        index[prefix] = sorted(listed)
        time.sleep(0.3)
    NAME_INDEX.parent.mkdir(parents=True, exist_ok=True)
    NAME_INDEX.write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
    return {k: set(v) for k, v in index.items()}


def slug(name: str) -> str:
    """OpenMoji 的名字用空白（`folded hands`），Iconify 用連字號（`folded-hands`）。

    不正規化就會 93% 對得上變成 33%，而「對不上」看起來就只是「這個概念比較冷門」。
    """

    return name.lower().replace(" ", "-")


def png_for(prefix: str, name: str) -> Path:
    """抓成 618 px PNG。彩色的 SVG 會保留原色，不像 iconify 那批要另外染。"""

    path = VARIANT_DIR / f"{prefix}-{name}.png"
    if path.exists():
        return path
    VARIANT_DIR.mkdir(parents=True, exist_ok=True)
    svg = VARIANT_DIR / f"{prefix}-{name}.svg"
    if not svg.exists():
        svg.write_bytes(fetch(f"{API}/{prefix}/{name}.svg?height=618"))
        time.sleep(0.15)
    page = fitz.open(svg)[0]
    scale = 618 / max(page.rect.width, page.rect.height)
    page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=True).save(path)
    return path


def probe(concepts: list[str], out: Path) -> None:
    """把一個概念在各套裡的畫法排成一列，看過再決定收不收那一套。

    `fluent-emoji` 就是這樣被擋下來的——名字對、檔案有、render 出來全黑。
    """

    from PIL import Image, ImageDraw, ImageFont

    label = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 12)
    cell, row_h = 132, 150
    sheet = Image.new("RGB", (len(ALL_SETS) * cell, len(concepts) * row_h), "white")
    draw = ImageDraw.Draw(sheet)
    for row, concept in enumerate(concepts):
        for column, prefix in enumerate(ALL_SETS):
            x, y = column * cell, row * row_h
            try:
                art = Image.open(png_for(prefix, concept)).convert("RGBA").resize((100, 100))
                tile = Image.new("RGBA", art.size, "white")
                tile.alpha_composite(art)
                sheet.paste(tile.convert("RGB"), (x + 16, y + 6))
            except Exception:
                draw.text((x + 20, y + 50), "—", font=label, fill="#bbbbbb")
            draw.text((x + 4, y + 112), prefix[:20], font=label, fill="#888888")
        draw.text((4, row * row_h + 130), concept, font=label, fill="black")
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    print(f"樣張 → {out}")


def review_sheet(lang: str, out: Path, columns: int = 12, size: int = 132,
                 skip: int = 0) -> None:
    """把「改用同語意場別的符號」那一層排成樣張。

    同概念換畫法那一層不必看——狗還是狗。要看的是這一層：它把 `folded hands`
    換成了 `prayer beads`、把 `prohibited` 換成了 `cross mark`，概念動了。
    """

    from PIL import Image, ImageDraw, ImageFont

    ledger = json.loads(LANGS[lang]["output"].read_text(encoding="utf-8"))["cards"]
    builder = load("build_flashcards", ROOT / "scripts/build_flashcards.py")
    chinese = {}
    for deck in LANGS[lang]["decks"]:
        for card in builder.load_cards(builder.DECKS[deck]):
            chinese[card["key"]] = card["glossZh"]

    rows = [(key, record) for key, record in sorted(ledger.items())
            if record.get("layer") == "family"][skip:skip + size]
    label = ImageFont.truetype("C:/Windows/Fonts/mingliu.ttc", 15)
    small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 10)
    cell, caption = 132, 46
    lines = (len(rows) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * cell, lines * (cell + caption)), "white")
    draw = ImageDraw.Draw(sheet)
    for index, (key, record) in enumerate(rows):
        x, y = (index % columns) * cell, (index // columns) * (cell + caption)
        art = Image.open(VARIANT_DIR / record["file"]).convert("RGBA").resize((cell - 30, cell - 30))
        tile = Image.new("RGBA", art.size, "white")
        tile.alpha_composite(art)
        sheet.paste(tile.convert("RGB"), (x + 15, y + 6))
        draw.text((x + 4, y + cell - 12), f"{skip + index + 1}. {chinese.get(key, '')[:11]}",
                  font=label, fill="black")
        draw.text((x + 4, y + cell + 8), record["name"][:26], font=small, fill="#888888")
        draw.text((x + 4, y + cell + 22), f"←{record['concept'][:24]}", font=small, fill="#bbbbbb")
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    print(f"{lang}：家族層 {sum(1 for r in ledger.values() if r.get('layer') == 'family')} 張，"
          f"本張排了 {len(rows)} 張 → {out}")


def verify(lang: str, builder) -> int:
    """驗收：同一語言內，還有幾張卡跟別張卡印出同一張圖。

    比的是**（圖庫, 概念名）**而不是檔名。檔名會騙人：OpenMoji 本地下載的 `link`
    叫 `1F517.png`，同一張圖從 Iconify 抓來叫 `openmoji-link.png`，檔名不同、
    畫面相同。這支驗收要是照檔名比，會回報「零重複」而卡片上明明有兩張一樣的。
    """

    matcher = load("match_flashcard_images", ROOT / "scripts/match_flashcard_images.py")
    by_hexcode = {record["hexcode"]: name for name, record in matcher.load_openmoji().items()}
    used: dict[tuple[str, str], list[str]] = collections.defaultdict(list)
    blank = 0
    for deck in LANGS[lang]["decks"]:
        config = builder.DECKS[deck]
        variants = (json.loads(config["variants"].read_text(encoding="utf-8"))["cards"]
                    if "variants" in config and config["variants"].exists() else {})
        icons = (json.loads(config["icons"].read_text(encoding="utf-8"))["cards"]
                 if "icons" in config and config["icons"].exists() else {})
        images = json.loads(config["images"].read_text(encoding="utf-8"))["images"]
        for card in builder.load_cards(config):
            key = card["key"]
            if key in icons:
                identity = ("iconify", icons[key]["icon"])
            elif key in variants:
                identity = (variants[key]["set"], variants[key]["name"])
            elif key in images:
                identity = ("openmoji", slug(by_hexcode.get(images[key]["hexcode"], "")))
            else:
                blank += 1
                continue
            used[identity].append(card["glossZh"])

    repeats = {identity: glosses for identity, glosses in used.items() if len(glosses) > 1}
    extra = sum(len(glosses) - 1 for glosses in repeats.values())
    print(f"  {lang}：用到 {len(used)} 張不同的圖、留白 {blank} 張；"
          f"仍與別張卡共用的 {extra} 張（{len(repeats)} 團）")
    for identity, glosses in sorted(repeats.items(), key=lambda kv: -len(kv[1]))[:8]:
        print(f"      {identity[0]}:{identity[1]} × {len(glosses)}　{'、'.join(glosses[:4])[:44]}")
    return extra


def cards_by_picture(decks: list[str], builder) -> dict[str, list[dict]]:
    """同一張 OpenMoji 圖底下有哪些卡。第二層審過的 Iconify 圖各自獨立，不動。

    **要看的是「原本的 OpenMoji 圖」，不是 `load_cards` 解出來的那張。** 印卡端已經
    會讀本腳本寫出的換圖帳本，所以第二次跑的時候 `card["picture"]` 早就換成
    twemoji 了，照它分組會看到「幾乎沒有重複」，然後把帳本重寫成只剩這一輪的
    十幾筆——前一輪的兩千張無聲消失。改成直接讀 OpenMoji 配圖表，這支腳本就
    每次都從同一個起點重算，跑幾次結果都一樣。
    """

    groups: dict[str, list[dict]] = collections.defaultdict(list)
    for deck in decks:
        config = builder.DECKS[deck]
        icons = (json.loads(config["icons"].read_text(encoding="utf-8"))["cards"]
                 if "icons" in config and config["icons"].exists() else {})
        images = json.loads(config["images"].read_text(encoding="utf-8"))["images"]
        for card in builder.load_cards(config):
            key = card["key"]
            if key in icons:                     # 審過的 Iconify 圖，本來就各自獨立
                continue
            record = images.get(key)
            if not record:
                continue
            groups[Path(record["file"]).stem].append(
                {"key": key, "glossZh": card["glossZh"]})
    return groups


def main() -> None:
    parser = argparse.ArgumentParser(description="同概念換一套畫法，消掉語言內的重複")
    parser.add_argument("--lang", choices=sorted(LANGS), help="hbo／grc／lat")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--probe", nargs="*", help="只看這幾個概念在各套裡長什麼樣")
    parser.add_argument("--verify", action="store_true",
                        help="驗收：同語言內還有幾張卡印出同一張圖（比概念身分，不比檔名）")
    parser.add_argument("--review", action="store_true",
                        help="把「改用同語意場別的符號」那一層排成樣張（同概念換畫法那層不必看）")
    parser.add_argument("--size", type=int, default=132, help="--review 一張排幾個")
    parser.add_argument("--skip", type=int, default=0)
    parser.add_argument("--out", default=str(ROOT / "output/flashcards/emoji-variants.png"))
    args = parser.parse_args()

    if args.probe:
        probe(args.probe, Path(args.out))
        return
    if not args.lang:
        raise SystemExit("要 --lang，或用 --probe 看樣張")
    if args.review:
        review_sheet(args.lang, Path(args.out), size=args.size, skip=args.skip)
        return
    if args.verify:
        verify(args.lang, load("build_flashcards", ROOT / "scripts/build_flashcards.py"))
        return

    names = emoji_names()
    builder = load("build_flashcards", ROOT / "scripts/build_flashcards.py")
    matcher = load("match_flashcard_images", ROOT / "scripts/match_flashcard_images.py")
    by_hexcode = {record["hexcode"]: name for name, record in matcher.load_openmoji().items()}

    config = LANGS[args.lang]
    groups = cards_by_picture(config["decks"], builder)
    shared = {h: rows for h, rows in groups.items() if len(rows) > 1}
    need = sum(len(rows) - 1 for rows in shared.values())
    print(f"  {args.lang}：用到 {len(groups)} 張 OpenMoji 圖，其中 {len(shared)} 張被兩張以上的卡共用，"
          f"要換掉 {need} 張")

    # 佔用表記的是「哪一張圖已經被用掉了」，鍵是（圖庫, 概念名）而**不是檔名**。
    # 用檔名會漏掉這一種撞法：A 卡原本就用 OpenMoji 的 `link`（檔名 1F517.png），
    # B 卡循 handshake 的家族借到 `openmoji:link`（檔名 openmoji-link.png）——
    # 兩個檔名不同，印出來卻是同一張圖。這正是使用者要禁掉的情形。
    taken: set[tuple[str, str]] = set()
    for hexcode, rows in groups.items():
        concept = by_hexcode.get(hexcode)
        if concept:
            taken.add(("openmoji", slug(concept)))   # 每一團的第一張都留著原圖

    assigned: dict[str, dict] = {}
    by_layer: collections.Counter = collections.Counter()

    # 每一團的第一張留著原本的 OpenMoji（那是有人特地挑的），其餘要換。
    # 詞義最短的那張最配得上原圖，所以它排第一。
    queue: list[tuple[str, str, list[dict]]] = []
    unnamed = 0
    for hexcode, rows in sorted(shared.items()):
        concept = by_hexcode.get(hexcode)
        if not concept:
            unnamed += len(rows) - 1
            continue
        rows = sorted(rows, key=lambda row: (len(row["glossZh"]), row["key"]))
        queue.append((concept, slug(concept), rows[1:]))

    def take(row: dict, concept: str, prefix: str, name: str, layer: str) -> None:
        taken.add((prefix, name))
        by_layer[layer] += 1
        assigned[row["key"]] = {"set": prefix, "name": name,
                                "file": f"{prefix}-{name}.png",
                                "concept": concept, "layer": layer}

    # **兩趟，順序有意義。** 第一趟先把所有團的「同概念換畫法」發完，第二趟才發
    # 家族借圖。反過來一趟做完會出事：`end arrow` 那一團循家族借走了 top-arrow 的
    # 各套畫法，等輪到 `top arrow` 自己那一團時，它自己的畫法已經被借光，只好整團
    # 維持共用。驗收看到的「openmoji:top-arrow × 6」就是這樣來的。
    for concept, key, rows in queue:
        pool = [prefix for prefix in SET_ORDER
                if key in names[prefix] and (prefix, key) not in taken]
        for row, prefix in zip(rows, pool):
            take(row, concept, prefix, key, "set")

    short = unnamed
    for concept, key, rows in queue:
        pool = [(prefix, sibling) for sibling in FAMILIES.get(concept, [])
                for prefix in ALL_SETS if sibling in names[prefix]]
        for row in rows:
            if row["key"] in assigned:
                continue
            choice = next((item for item in pool if item not in taken), None)
            if choice is None:
                short += 1
                continue
            take(row, concept, choice[0], choice[1], "family")

    print(f"  換掉 {len(assigned)} 張（同概念換畫法 {by_layer['set']}、"
          f"改用同語意場的別的符號 {by_layer['family']}），仍不足 {short} 張")

    if not args.write:
        print("\n（未寫檔；加 --write 才會下載並輸出）")
        return

    failed = []
    for index, (card_key, record) in enumerate(sorted(assigned.items()), start=1):
        try:
            png_for(record["set"], record["name"])
        except Exception as error:
            failed.append((card_key, record, str(error)))
        if index % 200 == 0:
            print(f"    已抓 {index}／{len(assigned)}")
    for card_key, _, error in failed:
        assigned.pop(card_key, None)
        print(f"    ⚠ {card_key} 取不到：{error}")

    config["output"].write_text(
        json.dumps(
            {
                "schemaVersion": "1.0.0",
                "sources": {prefix: LICENSES[prefix] for prefix in ALL_SETS},
                "note": "同一個概念換另一套 emoji 的畫法，只為了讓同語言內一張圖不重複出現。"
                        "概念沒有改變，所以這一層不需要逐張審圖；要審的是新收的圖庫會不會"
                        "render 成全黑（見 --probe）。",
                "cards": assigned,
            },
            ensure_ascii=False, indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    print(f"\n已寫出 {config['output']}（{len(assigned)} 張）")


if __name__ == "__main__":
    main()
