#!/usr/bin/env python3
"""逐張審第二層圖庫配到的圖：這張圖對不對得上這個中文詞義。

owner 2026-08-30 定的路線：**先清錯圖，共用暫時照舊。** 理由是他自己定過的
「錯圖比共用圖更糟」——共用只是兩張卡指向同一個意思，錯圖是背進一個不存在的
意思，而且背了改不掉。所以這一輪只做一個判斷：對／錯。對的放行進 `cards`，
錯的從帳本整條刪掉，那張卡就退回原本共用的 OpenMoji 圖，不強求一圖一卡。

要審的是 2,938 張：`pendingReview` 2,507 張（同概念換畫法猜出來的），加上
`cards` 那 431 張——放行的判準只問「圖示本名相不相符」，沒問相符在第幾個義項，
所以 בָּרָא「to create ... to cut down」在第二義上命中剪刀也算相符。

判斷分兩趟，缺一不可：

1. **讀名字**。四個圖庫的命名多半直述其圖，`mdi:delete-forever` 對「永遠」、
   `game-icons:swiss-army-knife` 對「軍隊」光看名字就知道錯。
2. **看圖**。名字會騙人：`ph:finn-the-human` 是卡通《探險活寶》主角、
   `game-icons:life-bar` 是電玩血條、`mdi:dog-service` 是導盲犬。這一層只有
   `--sheet` 排出樣張、用眼睛看才擋得住。

判決存在 `icon-review-decisions.json`，連「當時判的是哪一張圖」一起存：帳本裡
的圖換了，舊判決就自動失效重審——判決是對某一張圖的判決，不是對某張卡的。

    python scripts/review_card_icons.py --list --size 200          # 下一批待審
    python scripts/review_card_icons.py --sheet --size 40          # 同一批排成樣張
    python scripts/review_card_icons.py --apply                    # 判決寫回帳本
    python scripts/review_card_icons.py --status                   # 進度
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output/source-cache/flashcards"
ICON_DIR = CACHE / "iconify"
DECISIONS = CACHE / "icon-review-decisions.json"
LANGS = ("hebrew", "greek", "latin")


# 第三層備援是拿「這張卡現在共用的那張圖」的 OpenMoji 概念名再去找圖，而那個
# 概念名被切成一個個單詞後，**功能詞也算候選**。於是 `eye of horus` 的 `of`、
# `pokemon go` 的 `go`、`power socket it` 的 `it` 都成了命中理由，配出來的圖與
# 卡片的意思毫無關係：律例配荷魯斯之眼、行走配 Pokémon Go、他配義大利插座。
#
# 命中理由是功能詞或單字母時，那張圖不可能是為這個意思挑的——會對只能是巧合。
# 所以這一類整批判錯，不逐張看；例外是「卡片本身就是那個功能詞」（不、沒有），
# 那種要人看過，見 --filter stopword 的樣張。
STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "of", "to", "in", "on", "at", "by",
    "for", "from", "with", "as", "is", "be", "am", "are", "was", "it", "its", "he",
    "she", "they", "them", "his", "her", "up", "down", "out", "off", "over", "under",
    "into", "onto", "than", "then", "that", "this", "these", "those", "there", "here",
    "so", "such", "very", "too", "also", "just", "only", "even", "still", "yet",
    "any", "some", "each", "every", "both", "who", "whom", "what", "which", "when",
    "where", "why", "how", "shall", "will", "may", "can", "do", "does", "did",
}


def is_stopword_match(row: dict) -> bool:
    """命中理由是功能詞或單一字母 → 這張圖不是為這個意思挑的。"""

    words = row["matched"].replace("-", " ").split()
    return bool(words) and all(word in STOPWORDS or len(word) == 1 for word in words)


# 除了功能詞，逐張看下來還有三類不必一張一張判——判準寫在圖示本名裡，不是猜的。
#
# negated：名字帶 -off／-disabled／no-／not-，畫的是「打了叉的那個東西」。
#   gift-off 是被劃掉的禮物、food-off 是被劃掉的食物、assembly-off 是被劃掉的
#   集會。這種圖教的是相反的意思，比配錯還糟。
# brand：名字是商標、電玩、動漫、塔羅。death-star 是星際大戰、death-note 是死亡
#   筆記本、finn-the-human 是探險活寶、tarot-* 是塔羅牌、humble-bundle 是遊戲
#   商城。學的人背到的是那個作品，不是這個字。
# software：名字是介面元件或檔案格式。file-word 是 Word 檔、http-put 是 HTTP
#   動詞、git-fork 是版本控制、wifi-strength-2 是訊號強度、subset-of 是集合論。
#   古典語言的單字卡上沒有一個字的意思是這些。
NEGATED_PARTS = {"off", "disabled"}
BRAND_PARTS = {
    "brand", "logo", "tarot", "pokemon", "xbox", "google", "adobe", "humble",
    "bundle", "schrodingers", "finn", "pac", "meeple", "gnome", "hobbit",
    "companion", "cube", "deathstar", "gokart", "geographic",
}
BRAND_NAMES = {
    "death-star", "death-note", "dev-to", "dev-to-logo", "go-kart",
    "companion-cube", "national-geographic", "swiss-army-knife",
}
#   keyboard／letter／mail 這幾個字**不能**放進來：musical-keyboard 是鋼琴鍵盤、
#   love-letter 是插著心的信封、mail-forward 是信件，都是真實名物，`愛` 配
#   love-letter 是好圖。字母框那一類改用字首比對抓（letter-a、alpha-i、
#   square-letter-i），才不會連帶掃掉真名物。
SOFTWARE_PARTS = {
    "file", "http", "git", "wifi", "api", "app", "playlist", "dock", "css",
    "html", "sql", "url", "json", "folder", "clipboard",
    "subset", "superset", "congruent", "math", "logic",
    "code", "relation", "input", "select", "view", "table", "page",
    "zoom", "crop", "set", "sort", "socket", "screen", "scan", "server",
}
SOFTWARE_PREFIXES = ("letter-", "alpha-", "square-letter", "hexagon-letter",
                     "circle-letter", "rounded-letter")


def rule_reason(row: dict) -> str | None:
    """這張圖能不能靠圖示本名直接判錯，不必逐張看。回傳規則名，或 None。"""

    if is_stopword_match(row):
        return "stopword"
    name = row["icon"].split(":", 1)[1]
    parts = set(name.split("-"))
    if name.startswith(("no-", "not-")) or parts & NEGATED_PARTS:
        return "negated"
    if name in BRAND_NAMES or parts & BRAND_PARTS:
        return "brand"
    if parts & SOFTWARE_PARTS or name.startswith(SOFTWARE_PREFIXES):
        return "software"
    return None


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def ledger_path(lang: str) -> Path:
    return CACHE / f"{lang}-card-icons.json"


def read_decisions() -> dict:
    if not DECISIONS.exists():
        return {lang: {} for lang in LANGS}
    payload = json.loads(DECISIONS.read_text(encoding="utf-8"))
    return {lang: dict(payload.get("decisions", {}).get(lang) or {}) for lang in LANGS}


def write_decisions(decisions: dict) -> None:
    DECISIONS.write_text(
        json.dumps(
            {
                "schemaVersion": "1.0.0",
                "note": "逐張審圖的判決。verdict=ok 放行進 cards，verdict=wrong 從帳本刪掉、"
                        "那張卡退回原本共用的 OpenMoji 圖。icon 欄記的是判決當時看的那張圖，"
                        "帳本換圖後舊判決自動失效。",
                "decisions": decisions,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def pending_rows(lang: str, decisions: dict, audit) -> list[dict]:
    """還沒判、或判過但帳本已換圖的那些。"""

    icon_mod = load("iconify_card_images", ROOT / "scripts/iconify_card_images.py")
    matcher = load("match_flashcard_images", ROOT / "scripts/match_flashcard_images.py")
    ledger = json.loads(ledger_path(lang).read_text(encoding="utf-8"))
    rows = {row["key"]: row for row in icon_mod.cards_for(audit.LANGS[lang]["code"])}
    chinese = audit.chinese_by_card_key(lang, icon_mod)

    out = []
    for section in ("cards", "pendingReview"):
        for key, record in (ledger.get(section) or {}).items():
            verdict = decisions[lang].get(key)
            if verdict and verdict.get("icon") == record["icon"]:
                continue                       # 判過而且判的就是這張圖
            gloss_en = (rows.get(key) or {}).get("glossEn", "")
            segments = matcher.english_candidates(gloss_en)
            out.append({
                "lang": lang,
                "key": key,
                "headword": key.split("|")[-1],
                "zh": chinese.get(key, ""),
                "icon": record["icon"],
                "file": record["file"],
                "matched": record["glossEn"],
                "first": segments[0] if segments else "",
                "section": section,
            })
    # 已放行的先審：那些現在就印在卡片上，錯的話立刻在教錯。
    out.sort(key=lambda row: (row["section"] != "cards", row["key"]))
    return out


def render_sheet(rows: list[dict], out: Path, columns: int = 8) -> None:
    """排成樣張。名字會騙人，這一步是唯一擋得住的關卡。"""

    from PIL import Image, ImageDraw, ImageFont

    label_font = ImageFont.truetype("C:/Windows/Fonts/mingliu.ttc", 15)
    name_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 11)
    cell, caption = 132, 36
    lines = (len(rows) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * cell, lines * (cell + caption)), "white")
    draw = ImageDraw.Draw(sheet)
    for index, row in enumerate(rows):
        x, y = (index % columns) * cell, (index // columns) * (cell + caption)
        art = Image.open(ICON_DIR / row["file"]).convert("RGBA").resize((cell - 30, cell - 30))
        tile = Image.new("RGBA", art.size, "white")
        tile.alpha_composite(art)
        sheet.paste(tile.convert("RGB"), (x + 15, y + 6))
        draw.text((x + 4, y + cell - 12), f"{index + 1}. {row['zh'][:11]}", font=label_font, fill="black")
        draw.text((x + 4, y + cell + 8), row["icon"].split(":", 1)[1][:26], font=name_font, fill="#888888")
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)


def apply_decisions() -> None:
    """判決寫回三本帳本。ok 進 cards，wrong 兩區都刪。"""

    decisions = read_decisions()
    for lang in LANGS:
        path = ledger_path(lang)
        ledger = json.loads(path.read_text(encoding="utf-8"))
        approved = dict(ledger.get("cards") or {})
        pending = dict(ledger.get("pendingReview") or {})
        moved = dropped = stale = 0
        for key, verdict in decisions[lang].items():
            record = approved.get(key) or pending.get(key)
            if not record:
                continue
            if record["icon"] != verdict.get("icon"):
                stale += 1                     # 帳本換圖了，這條判決不算數
                continue
            if verdict["verdict"] == "ok":
                if key in pending:
                    approved[key] = pending.pop(key)
                    moved += 1
            else:
                approved.pop(key, None)
                pending.pop(key, None)
                dropped += 1
        ledger["cards"] = approved
        ledger["pendingReview"] = pending
        path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"  {lang}：放行 {len(approved)}（本次 +{moved}）、待審 {len(pending)}、"
              f"判錯刪掉 {dropped}" + (f"、判決過期 {stale}" if stale else ""))


def main() -> None:
    parser = argparse.ArgumentParser(description="逐張審卡片配圖")
    parser.add_argument("--list", action="store_true", help="印出下一批待審")
    parser.add_argument("--sheet", action="store_true", help="把下一批排成樣張看圖")
    parser.add_argument("--apply", action="store_true", help="判決寫回帳本")
    parser.add_argument("--status", action="store_true", help="只看進度")
    parser.add_argument("--record", metavar="WRONG",
                        help="記下這一批的判決：給錯的編號（逗號隔開，可空字串代表全對）。"
                             "編號就是 --list／--sheet 印出來的那組，所以 --skip/--size/--lang "
                             "必須跟當時完全一樣，否則記到別張卡上。")
    parser.add_argument("--reason", default="", help="這一批判錯的共同理由，寫進判決檔備查")
    parser.add_argument("--filter",
                        choices=("stopword", "negated", "brand", "software", "ruled", "other"),
                        help="只看某一條規則判得出來的那一批，或只看規則判不出來、必須逐張看的（other）")
    parser.add_argument("--lang", choices=LANGS + ("all",), default="all")
    parser.add_argument("--size", type=int, default=200)
    parser.add_argument("--skip", type=int, default=0, help="跳過前 N 筆")
    parser.add_argument("--columns", type=int, default=12,
                        help="樣張欄數。整張圖任一邊超過 2000 px 會炸掉 session，"
                             "格子固定 132 px 寬、168 px 高，所以欄數上限 15、列數上限 11。")
    parser.add_argument("--out", default=str(ROOT / "output/flashcards/icon-review.png"))
    args = parser.parse_args()

    if args.apply:
        apply_decisions()
        return

    audit = load("audit_card_icons", ROOT / "scripts/audit_card_icons.py")
    decisions = read_decisions()
    languages = LANGS if args.lang == "all" else (args.lang,)
    rows: list[dict] = []
    for lang in languages:
        rows.extend(pending_rows(lang, decisions, audit))

    if args.filter == "ruled":
        rows = [row for row in rows if rule_reason(row)]
    elif args.filter == "other":
        rows = [row for row in rows if not rule_reason(row)]
    elif args.filter:
        rows = [row for row in rows if rule_reason(row) == args.filter]

    judged = sum(len(decisions[lang]) for lang in languages)
    print(f"待審 {len(rows)} 張，已判 {judged} 張")
    if args.status:
        return

    batch = rows[args.skip : args.skip + args.size]

    if args.record is not None:
        wrong = {int(piece) for piece in args.record.replace(" ", "").split(",") if piece}
        outside = {n for n in wrong if not 1 <= n <= len(batch)}
        if outside:
            raise SystemExit(f"編號超出這一批（1–{len(batch)}）：{sorted(outside)}")
        for index, row in enumerate(batch, start=1):
            decisions[row["lang"]][row["key"]] = {
                "icon": row["icon"],           # 判的是這一張圖，帳本換圖就作廢
                "verdict": "wrong" if index in wrong else "ok",
                **({"reason": args.reason} if index in wrong and args.reason else {}),
            }
        write_decisions(decisions)
        print(f"記下 {len(batch)} 張：判錯 {len(wrong)}、判對 {len(batch) - len(wrong)}")
        return

    if args.sheet:
        render_sheet(batch, Path(args.out), columns=args.columns)
        print(f"樣張 → {args.out}（{len(batch)} 張，編號與下面清單相同）")
    if args.list or args.sheet:
        for index, row in enumerate(batch, start=1):
            print(f"{index}\t{row['lang']}\t{row['section']}\t{row['key']}\t{row['zh']}\t"
                  f"{row['icon']}\t配到「{row['matched']}」\t第一義項：{row['first'][:40]}")


if __name__ == "__main__":
    main()
