#!/usr/bin/env python3
"""Build the word-by-word (interlinear) Traditional-Chinese layer for the
50-lesson Biblical Hebrew reader.

Every running-text unit in the reader — 25 complete Scripture chapters, the 100
memory verses, the 25 prayers/articles, and the fifteen-step Haggadah — is
tokenised from its *printed* display text, so the gloss row always aligns with
the row of Hebrew words the learner actually sees.  Each token then receives one
short Traditional-Chinese gloss, and every non-biblical unit additionally
receives a whole-segment Chinese rendering (the prayer/Haggadah masters ship
with ``translationZh`` empty).

The result is one cache-backed master, ``interlinear.json``; re-runs skip units
that are already complete, so a partial run is always resumable.

Engine: Claude Sonnet over the Claude Code OAuth credentials, reusing the client
pattern proven in ``translate_ebook_to_zh.py``.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Iterable

import anthropic


ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "hebrew-full"
SCRIPTURE_PLAN = CACHE / "scripture-plan.json"
PRAYERS = CACHE / "prayers-articles.json"
HAGGADAH = CACHE / "haggadah-full.json"
ASSEMBLED = CACHE / "hebrew-reader-50-lessons.json"
VOCAB = ROOT / "data" / "originalReaders" / "vocabulary" / "hebrew-1000.json"
REVIEWED_GLOSSES = CACHE / "hebrew-1000-gloss-zh-reviewed.json"
OUTPUT = CACHE / "interlinear.json"

# Rate limits are per model tier on this account: Sonnet can be exhausted while
# Haiku still answers.  Glossing runs on whichever tier is available and records
# the engine per unit, so a later Sonnet pass can upgrade exactly the units a
# cheaper tier produced.
SONNET_MODELS = ("claude-sonnet-5", "claude-sonnet-4-6")
HAIKU_MODELS = ("claude-haiku-4-5-20251001",)
MODEL_CHAINS = {"sonnet": SONNET_MODELS, "haiku": HAIKU_MODELS}

MAQQEF = "־"
SOF_PASUQ = "׃"
PASEQ = "׀"
HEBREW_LETTER_RE = re.compile(r"[א-ת]")
# Trailing marks that ride along with a word but are never glossed.
TRAILING_RE = re.compile(r"[׀׃,:;.!?。，：；]+$")


# --------------------------------------------------------------------------- #
# tokenisation
# --------------------------------------------------------------------------- #


def tokenize(text: str) -> list[dict[str, Any]]:
    """Split printed Hebrew into glossable tokens.

    Whitespace separates tokens; a maqqef additionally splits a chunk while
    staying attached to the word it follows, exactly as it prints.  Sof pasuq,
    paseq and modern punctuation are carried as ``trailing`` so they render after
    the word without ever consuming a gloss slot.
    """
    tokens: list[dict[str, Any]] = []
    for chunk in text.split():
        if not chunk:
            continue
        pieces = chunk.split(MAQQEF)
        for index, piece in enumerate(pieces):
            joined = index < len(pieces) - 1
            trailing_match = TRAILING_RE.search(piece)
            trailing = trailing_match.group(0) if trailing_match else ""
            word = piece[: len(piece) - len(trailing)] if trailing else piece
            if not HEBREW_LETTER_RE.search(word):
                # Pure punctuation (e.g. a standalone paseq): attach to the
                # previous token rather than emitting an unglossable slot.
                if tokens:
                    tokens[-1]["trailing"] += piece
                continue
            tokens.append(
                {
                    "ordinal": len(tokens) + 1,
                    "word": word,
                    "trailing": trailing + (MAQQEF if joined else ""),
                    "glossZh": "",
                }
            )
    return tokens


# --------------------------------------------------------------------------- #
# unit collection
# --------------------------------------------------------------------------- #


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_units() -> list[dict[str, Any]]:
    """One record per glossable running-text unit, in production order."""
    plan = load(SCRIPTURE_PLAN)
    prayers = load(PRAYERS)
    haggadah = load(HAGGADAH)
    assembled = load(ASSEMBLED)

    # The reader prints the learner-facing qere layer, while scripture-plan.json
    # preserves the source-oriented ketiv spellings; 96 verses differ.  Gloss the
    # text the page actually shows, or the two layers cannot be aligned at all.
    translation_by_ref: dict[str, str] = {}
    display_by_ref: dict[str, str] = {}
    for lesson in assembled["lessons"]:
        for verse in lesson.get("reading", {}).get("verses", []) or []:
            if verse.get("translationZh"):
                translation_by_ref[verse["ref"]] = verse["translationZh"].strip()
            if verse.get("text"):
                display_by_ref[verse["ref"]] = verse["text"]
        for verse in lesson.get("memoryVerses", []) or []:
            if verse.get("text"):
                display_by_ref[verse["ref"]] = verse["text"]
            if verse.get("translationZh"):
                translation_by_ref.setdefault(verse["ref"], verse["translationZh"].strip())

    units: list[dict[str, Any]] = []
    seen: set[str] = set()

    for chapter in plan["chapters"]:
        for verse in chapter["verses"]:
            key = f"bible:{verse['ref']}"
            if key in seen:
                continue
            seen.add(key)
            units.append(
                {
                    "id": key,
                    "kind": "bible_verse",
                    "ref": verse["ref"],
                    "group": f"bible:{chapter['ref']}",
                    "text": display_by_ref.get(verse["ref"], verse["text"]),
                    "reference_zh": translation_by_ref.get(verse["ref"], ""),
                    "need_sense": False,
                }
            )

    for lesson in plan["memoryLessons"]:
        for verse in lesson["verses"]:
            key = f"bible:{verse['ref']}"
            if key in seen:
                continue
            seen.add(key)
            units.append(
                {
                    "id": key,
                    "kind": "memory_verse",
                    "ref": verse["ref"],
                    "group": f"memory:{lesson['lesson']:02d}",
                    "text": display_by_ref.get(verse["ref"], verse["text"]),
                    "reference_zh": translation_by_ref.get(verse["ref"], ""),
                    "need_sense": False,
                }
            )

    for item in prayers["items"]:
        for segment in item["segments"]:
            units.append(
                {
                    "id": f"prayer:{segment['id']}",
                    "kind": "prayer_segment",
                    "ref": segment.get("sourcePath") or item["ref"],
                    "group": f"prayer:{item['id']}",
                    "title": item["title_zh"],
                    "text": segment.get("editorialPointedText") or segment["text"],
                    "reference_zh": "",
                    "need_sense": True,
                }
            )

    for step in haggadah["steps"]:
        for segment in step["segments"]:
            units.append(
                {
                    "id": f"haggadah:{segment['id']}",
                    "kind": "haggadah_segment",
                    "ref": segment.get("sourcePath") or step["ref"],
                    "group": f"haggadah:{step['key']}",
                    "title": step["title_zh"],
                    "text": segment.get("editorialPointedText") or segment["text"],
                    "reference_zh": "",
                    "need_sense": True,
                }
            )

    for unit in units:
        unit["tokens"] = tokenize(unit["text"])
    return [unit for unit in units if unit["tokens"]]


def batch_units(units: list[dict[str, Any]], max_words: int) -> list[list[dict[str, Any]]]:
    """Group consecutive units of one group into calls of bounded size."""
    batches: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    words = 0
    group = None
    for unit in units:
        size = len(unit["tokens"])
        if current and (unit["group"] != group or words + size > max_words):
            batches.append(current)
            current, words = [], 0
        current.append(unit)
        words += size
        group = unit["group"]
    if current:
        batches.append(current)
    return batches


# --------------------------------------------------------------------------- #
# vocabulary anchor
# --------------------------------------------------------------------------- #


def vocabulary_anchor() -> str:
    """A compact reviewed-gloss anchor so the interlinear agrees with the
    curriculum's own 1000-word list instead of inventing parallel wordings."""
    vocab = load(VOCAB)
    reviewed = {item["ordinal"]: item["glossZh"].strip() for item in load(REVIEWED_GLOSSES)["items"]}
    lines = []
    for entry in vocab:
        gloss = reviewed.get(entry["ordinal"], "").strip()
        if not gloss:
            continue
        primary = gloss.split("；")[0].split(";")[0].strip()
        lines.append(f"{entry['pointed']}={primary}")
    return "、".join(lines)


PROMPT = """你在製作一本聖經希伯來文讀本的「逐詞對譯」層。讀本是私人研讀用，讀者是中文母語者。

工作：把下列每一段希伯來文的**每一個詞**標上一個簡短的繁體中文詞義。

規則：
1. 每個詞給 1 個詞義，2–6 個中文字，取「在這個句子裡的實際意思」，不是字典裡所有義項。
2. 詞形上的前綴要一起譯進去：וְ＝並／而、בְּ＝在…、לְ＝向…／給…、מִ＝從…、הַ＝這、כְּ＝如同、שֶׁ＝那…的。人稱字尾也要譯出來（חַסְדּוֹ＝他的慈愛、לְפָנֶיךָ＝在你面前）。
2a. **每個詞義必須是該位置那個希伯來詞本身的意思，不可為了讓中文順而把相鄰兩詞的意思對調。**
    例：בְּיָד חֲזָקָה 要標成「在…手中」「強大的」，不可標成「在強大的」「手」；
    וּבִזְרוֹעַ נְטוּיָה 要標成「並用膀臂」「伸出的」。
2b. 不要用「……」或「...」當佔位符。כִּי 就寫「因為」，不要寫「因為……的」。詞義也不可以只有一個「…」。
2d. 沒有實義的虛詞照這樣標，不要用省略號帶過：
    אֲשֶׁר＝那…的（或依上下文「所」「就是」）、אֵת／אֶת＝（受詞記號）、
    הִנֵּה＝看哪、נָא＝請、לֹא＝不、אִם＝若、כֹּה＝如此。
2c. 同一個詞形在整批中出現多次，詞義必須前後一致（חַסְדּוֹ 一律「他的慈愛」，不要有時寫忠誠）。
3. 專名一律用通用中譯：יהוה＝耶和華、אֱלֹהִים＝上帝、יִשְׂרָאֵל＝以色列、יְרוּשָׁלַיִם＝耶路撒冷、מֹשֶׁה＝摩西、מִצְרַיִם＝埃及、אַבְרָהָם＝亞伯拉罕。
4. 只用繁體中文，不可出現英文、拼音、注音或簡體字。
5. 不要解釋、不要加註、不要標點符號當詞義。

{sense_rule}
輸出格式：只輸出一個 JSON 物件，不要任何其他文字、不要程式碼圍籬。
{{"units":[{{"id":"<單元 id>","glosses":["詞義1","詞義2", ...]{sense_field}}}]}}
glosses 的數量必須**剛好等於**該單元列出的詞數。

參考詞庫（本讀本已審定的譯法，遇到同形詞請沿用）：
{anchor}

以下是要處理的單元：
{payload}"""

SENSE_RULE_ON = "6. 每個單元另外給一句 senseZh：整段的繁體中文意思，通順成句，忠於希伯來原文，不要加原文沒有的話。\n"
SENSE_RULE_OFF = ""


# A single Haggadah or Ashrei segment can run past 250 words.  Asking for one
# gloss list that long makes the model lose count — it kept returning three
# short — so oversized units are glossed a window at a time and reassembled.
WINDOW_TOKENS = 60


def build_window_prompt(
    unit: dict[str, Any],
    window: list[dict[str, Any]],
    start: int,
    is_last: bool,
    anchor: str,
) -> str:
    need_sense = is_last and unit["need_sense"]
    listing = "　".join(f"{token['ordinal']}.{token['word']}" for token in window)
    block = "\n".join(
        [
            f"單元 id：{unit['id']}",
            f"出處：{unit['ref']}",
            f"（本段完整原文，僅供理解上下文）：{unit['text']}",
            f"本段共 {len(unit['tokens'])} 詞；這一次只標第 {start + 1}–{start + len(window)} 詞，共 {len(window)} 個。",
            f"逐詞：{listing}",
            f"glosses 必須剛好 {len(window)} 個，順序與上面完全相同，不要多也不要少。",
        ]
    )
    return PROMPT.format(
        sense_rule=SENSE_RULE_ON if need_sense else SENSE_RULE_OFF,
        sense_field=',"senseZh":"整段意思"' if need_sense else "",
        anchor=anchor,
        payload=block,
    )


def build_prompt(batch: list[dict[str, Any]], anchor: str) -> str:
    need_sense = any(unit["need_sense"] for unit in batch)
    blocks = []
    for unit in batch:
        lines = [f"單元 id：{unit['id']}", f"出處：{unit['ref']}"]
        if unit.get("title"):
            lines.append(f"篇名：{unit['title']}")
        lines.append(f"希伯來原文：{unit['text']}")
        if unit["reference_zh"]:
            lines.append(f"（和合本修訂版參考譯文，僅供理解上下文）：{unit['reference_zh']}")
        lines.append(f"詞數：{len(unit['tokens'])}")
        listing = "　".join(f"{token['ordinal']}.{token['word']}" for token in unit["tokens"])
        lines.append(f"逐詞：{listing}")
        blocks.append("\n".join(lines))
    return PROMPT.format(
        sense_rule=SENSE_RULE_ON if need_sense else SENSE_RULE_OFF,
        sense_field=',"senseZh":"整段意思"' if need_sense else "",
        anchor=anchor,
        payload="\n\n".join(blocks),
    )


# --------------------------------------------------------------------------- #
# engine
# --------------------------------------------------------------------------- #


_client_lock = threading.Lock()
_client: anthropic.Anthropic | None = None
_client_mtime = 0.0
_model = SONNET_MODELS[0]
_model_chain = SONNET_MODELS


def _credentials_path() -> Path:
    home = os.environ.get("USERPROFILE") or os.environ.get("HOME") or ""
    return Path(home) / ".claude" / ".credentials.json"


def _make_client() -> anthropic.Anthropic:
    common = {"timeout": 600.0, "max_retries": 2}
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        return anthropic.Anthropic(api_key=api_key, **common)
    path = _credentials_path()
    if path.exists():
        creds = json.loads(path.read_text(encoding="utf-8"))
        token = creds.get("claudeAiOauth", {}).get("accessToken", "")
        if token:
            return anthropic.Anthropic(auth_token=token, **common)
    raise RuntimeError("找不到 Anthropic 憑證（ANTHROPIC_API_KEY 或 ~/.claude/.credentials.json）")


def client() -> anthropic.Anthropic:
    """Rebuild whenever Claude Code rolls the OAuth access token."""
    global _client, _client_mtime
    with _client_lock:
        path = _credentials_path()
        if path.exists():
            mtime = path.stat().st_mtime
            if _client is None or mtime > _client_mtime:
                _client = _make_client()
                _client_mtime = mtime
        elif _client is None:
            _client = _make_client()
        return _client


# The Claude Max account is shared with the interactive session and the
# overnight translation fleet, so a 429 means "everyone waits", not "this batch
# failed".  One shared gate holds every worker until the window reopens; the run
# is designed to be left going and to resume from the cache after any stop.
_gate_lock = threading.Lock()
_gate_until = 0.0
_gate_streak = 0
GATE_WAITS = (300, 600, 900, 1200, 1800)


def _wait_for_gate() -> None:
    while True:
        with _gate_lock:
            remaining = _gate_until - time.time()
        if remaining <= 0:
            return
        time.sleep(min(remaining, 30))


def _trip_gate() -> float:
    global _gate_until, _gate_streak
    with _gate_lock:
        wait = GATE_WAITS[min(_gate_streak, len(GATE_WAITS) - 1)]
        _gate_streak += 1
        _gate_until = max(_gate_until, time.time() + wait)
        return wait


def _clear_gate() -> None:
    global _gate_streak
    with _gate_lock:
        _gate_streak = 0


def call_model(prompt: str, backoffs: Iterable[int] = (0, 30, 90, 180, 300, 600)) -> str:
    global _client, _client_mtime, _model
    backoffs = tuple(backoffs)
    for attempt, wait in enumerate(backoffs, start=1):
        if wait:
            time.sleep(wait)
        _wait_for_gate()
        try:
            message = client().messages.create(
                model=_model,
                max_tokens=16000,
                messages=[{"role": "user", "content": prompt}],
            )
            _clear_gate()
            return "".join(block.text for block in message.content if hasattr(block, "text")).strip()
        except anthropic.NotFoundError:
            with _client_lock:
                index = _model_chain.index(_model) if _model in _model_chain else 0
                if index + 1 < len(_model_chain):
                    _model = _model_chain[index + 1]
                    print(f"  模型改用 {_model}", flush=True)
                else:
                    raise
        except anthropic.AuthenticationError:
            print("  401 — 重讀 credentials.json", file=sys.stderr, flush=True)
            with _client_lock:
                _client_mtime = 0.0
            if attempt >= len(backoffs):
                raise
        except anthropic.RateLimitError:
            held = _trip_gate()
            print(f"  429 額度用盡 — 全體暫停 {held // 60} 分鐘後續跑", file=sys.stderr, flush=True)
            if attempt >= len(backoffs):
                raise
        except (anthropic.APIConnectionError, anthropic.APITimeoutError) as error:
            print(f"  {type(error).__name__} 第 {attempt}/{len(backoffs)} 次", file=sys.stderr, flush=True)
            if attempt >= len(backoffs):
                raise
    raise RuntimeError("重試次數用盡")


JSON_RE = re.compile(r"\{.*\}", re.S)


def parse_response(raw: str) -> dict[str, dict[str, Any]]:
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text).strip()
    match = JSON_RE.search(text)
    if not match:
        raise ValueError("回應不含 JSON")
    try:
        payload = json.loads(match.group(0))
    except json.JSONDecodeError:
        # A stray quote inside one gloss should not cost the whole window.
        # The shape we need is simple enough to recover positionally.
        payload = salvage_payload(match.group(0))
    return {unit["id"]: unit for unit in payload.get("units", []) if unit.get("id")}


GLOSS_ARRAY_RE = re.compile(r'"glosses"\s*:\s*\[(.*?)\]', re.S)
SENSE_RE = re.compile(r'"senseZh"\s*:\s*"(.*?)"\s*[,}]', re.S)
UNIT_ID_RE = re.compile(r'"id"\s*:\s*"([^"]+)"')


def salvage_payload(text: str) -> dict[str, Any]:
    array = GLOSS_ARRAY_RE.search(text)
    if not array:
        raise ValueError("回應的 JSON 無法修復")
    glosses = [item.strip().strip('"').strip() for item in array.group(1).split('",')]
    glosses = [gloss.strip('"').strip() for gloss in glosses if gloss.strip()]
    unit_id = UNIT_ID_RE.search(text)
    sense = SENSE_RE.search(text)
    return {
        "units": [
            {
                "id": unit_id.group(1) if unit_id else "",
                "glosses": glosses,
                "senseZh": sense.group(1) if sense else "",
            }
        ]
    }


BAD_GLOSS_RE = re.compile(r"[A-Za-z֐-׿]")
# An ellipsis inside a gloss is legitimate and often required: 「在…手中」 for a
# prefixed noun, 「那…的」 for a relative pronoun.  Only a gloss that is *nothing
# but* an ellipsis carries no meaning and must be sent back.
FILLER_RE = re.compile(r"^(?:…|\.\.\.)+\s*的?$")
MAX_GLOSS_CHARS = 10


def normalize_gloss(value: Any) -> str:
    """Keep the printed gloss typographically tidy: one ellipsis character."""
    return re.sub(r"…{2,}|\.\.\.", "…", str(value).strip())


def validate(unit: dict[str, Any], answer: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    glosses = answer.get("glosses")
    if not isinstance(glosses, list):
        return [f"{unit['id']}：缺 glosses"]
    if len(glosses) != len(unit["tokens"]):
        problems.append(f"{unit['id']}：詞義數 {len(glosses)} ≠ 詞數 {len(unit['tokens'])}")
    for index, gloss in enumerate(glosses, start=1):
        value = normalize_gloss(gloss)
        if not value:
            problems.append(f"{unit['id']}：第 {index} 詞義空白")
        elif BAD_GLOSS_RE.search(value):
            problems.append(f"{unit['id']}：第 {index} 詞義含英文或希伯來文「{value}」")
        elif FILLER_RE.search(value):
            problems.append(f"{unit['id']}：第 {index} 詞義含佔位符「{value}」")
        elif len(value) > MAX_GLOSS_CHARS:
            problems.append(f"{unit['id']}：第 {index} 詞義過長「{value}」")
    if unit["need_sense"] and not str(answer.get("senseZh", "")).strip():
        problems.append(f"{unit['id']}：缺整段意思")
    return problems


# --------------------------------------------------------------------------- #
# driver
# --------------------------------------------------------------------------- #


def consistency_report(records: dict[str, Any]) -> None:
    """Same printed form, different gloss.  Legitimate homographs exist, so this
    is a review list for the release gate rather than an automatic rewrite."""
    from collections import defaultdict

    forms: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for record in records.values():
        for token in record.get("tokens", []):
            forms[token["word"]][token.get("glossZh", "")].append(record["id"])
    divergent = {word: glosses for word, glosses in forms.items() if len(glosses) > 1}
    print(f"已標詞形 {len(forms)}，其中 {len(divergent)} 個詞形譯法不一致", flush=True)
    for word, glosses in sorted(divergent.items(), key=lambda item: -sum(len(v) for v in item[1].values())):
        summary = "　".join(
            f"{gloss}×{len(units)}（{units[0]}…）" for gloss, units in sorted(glosses.items(), key=lambda kv: -len(kv[1]))
        )
        print(f"  {word}　{summary}", flush=True)


def load_master() -> dict[str, Any]:
    if OUTPUT.exists():
        return load(OUTPUT)
    return {"schemaVersion": 1, "engine": "", "units": {}}


def save_master(master: dict[str, Any]) -> None:
    """Merge with whatever is on disk before writing.

    A run holds the whole master in memory, so two runs writing blindly means
    the slower one silently reverts the other's units — that is exactly how a
    998/1000 pass fell back to 861.  Disk wins for units this run did not
    produce; the write itself is atomic so a kill cannot truncate the file.
    """
    if OUTPUT.exists():
        try:
            on_disk = json.loads(OUTPUT.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            on_disk = {"units": {}}
        merged = dict(on_disk.get("units", {}))
        merged.update(master["units"])
        master["units"] = merged
    temporary = OUTPUT.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(master, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(OUTPUT)


def unit_complete(record: dict[str, Any] | None, unit: dict[str, Any], *, require_engine: str = "") -> bool:
    if not record:
        return False
    if require_engine and record.get("engine") != require_engine:
        return False
    tokens = record.get("tokens") or []
    if len(tokens) != len(unit["tokens"]):
        return False
    if any(token.get("word") != source["word"] for token, source in zip(tokens, unit["tokens"])):
        return False
    if any(not str(token.get("glossZh", "")).strip() for token in tokens):
        return False
    if unit["need_sense"] and not str(record.get("senseZh", "")).strip():
        return False
    return True


MIN_WINDOW_TOKENS = 8


def gloss_window(
    unit: dict[str, Any],
    window: list[dict[str, Any]],
    start: int,
    is_last: bool,
    anchor: str,
) -> tuple[list[str], str]:
    """Gloss one span, halving it whenever the model loses count.

    Ashrei is an acrostic full of repeated words and maqqef pairs, and the model
    kept returning one gloss short for it however the instruction was worded.
    A shorter list is easier to count than a better prompt is to write.
    """
    answers = parse_response(call_model(build_window_prompt(unit, window, start, is_last, anchor)))
    answer = answers.get(unit["id"]) or (next(iter(answers.values())) if answers else None)
    glosses = answer.get("glosses") if answer else None
    if isinstance(glosses, list) and len(glosses) == len(window):
        return [str(gloss) for gloss in glosses], str(answer.get("senseZh", "")).strip()
    if len(window) <= MIN_WINDOW_TOKENS:
        got = len(glosses) if isinstance(glosses, list) else "無"
        raise ValueError(f"{unit['id']}：第 {start + 1}–{start + len(window)} 詞回了 {got} 個詞義")
    middle = len(window) // 2
    left, _ = gloss_window(unit, window[:middle], start, False, anchor)
    right, sense = gloss_window(unit, window[middle:], start + middle, is_last, anchor)
    return left + right, sense


def run_long_unit(unit: dict[str, Any], anchor: str) -> tuple[dict[str, dict[str, Any]], list[str]]:
    """Gloss one oversized unit window by window."""
    tokens = unit["tokens"]
    glosses: list[str] = []
    sense = ""
    for start in range(0, len(tokens), WINDOW_TOKENS):
        window = tokens[start : start + WINDOW_TOKENS]
        is_last = start + len(window) >= len(tokens)
        try:
            window_glosses, window_sense = gloss_window(unit, window, start, is_last, anchor)
        except ValueError as error:
            return {}, [str(error)]
        glosses.extend(window_glosses)
        if is_last:
            sense = window_sense
    answer = {"glosses": glosses, "senseZh": sense}
    problems = validate(unit, answer)
    if problems:
        return {}, problems
    return {
        unit["id"]: {
            "id": unit["id"],
            "kind": unit["kind"],
            "ref": unit["ref"],
            "text": unit["text"],
            "tokens": [
                {**token, "glossZh": normalize_gloss(gloss)}
                for token, gloss in zip(tokens, glosses)
            ],
            "senseZh": sense,
            "engine": _model,
        }
    }, []


def run_batch(batch: list[dict[str, Any]], anchor: str) -> tuple[dict[str, dict[str, Any]], list[str]]:
    long_units = [unit for unit in batch if len(unit["tokens"]) > WINDOW_TOKENS]
    if long_units:
        results: dict[str, dict[str, Any]] = {}
        problems: list[str] = []
        for unit in long_units:
            unit_results, unit_problems = run_long_unit(unit, anchor)
            results.update(unit_results)
            problems.extend(unit_problems)
        rest = [unit for unit in batch if len(unit["tokens"]) <= WINDOW_TOKENS]
        if rest:
            rest_results, rest_problems = run_batch(rest, anchor)
            results.update(rest_results)
            problems.extend(rest_problems)
        return results, problems
    prompt = build_prompt(batch, anchor)
    raw = call_model(prompt)
    answers = parse_response(raw)
    results: dict[str, dict[str, Any]] = {}
    problems: list[str] = []
    for unit in batch:
        answer = answers.get(unit["id"])
        if not answer:
            problems.append(f"{unit['id']}：回應缺此單元")
            continue
        issues = validate(unit, answer)
        if issues:
            problems.extend(issues)
            continue
        tokens = [
            {**token, "glossZh": normalize_gloss(gloss)}
            for token, gloss in zip(unit["tokens"], answer["glosses"])
        ]
        results[unit["id"]] = {
            "id": unit["id"],
            "kind": unit["kind"],
            "ref": unit["ref"],
            "text": unit["text"],
            "tokens": tokens,
            "senseZh": str(answer.get("senseZh", "")).strip(),
            "engine": _model,
        }
    return results, problems


def main() -> None:
    parser = argparse.ArgumentParser(description="建置希伯來文讀本逐詞對譯層")
    parser.add_argument("--kinds", default="all",
                        help="all｜bible｜memory｜prayer｜haggadah（可逗號並列）")
    parser.add_argument("--max-words", type=int, default=110, help="每次呼叫的最大詞數")
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--limit", type=int, default=0, help="只跑前 N 批（試跑用）")
    parser.add_argument("--rounds", type=int, default=6, help="未完成單元最多重跑幾輪")
    parser.add_argument("--probe-attempts", type=int, default=24, help="試跑批次最多重試幾次")
    parser.add_argument("--model", choices=sorted(MODEL_CHAINS), default="sonnet",
                        help="sonnet（品質優先）｜haiku（Sonnet 額度用盡時仍可跑）")
    parser.add_argument("--upgrade", action="store_true",
                        help="連已完成但由別的引擎產出的單元一起重跑，用來把 Haiku 那批換成 Sonnet")
    parser.add_argument("--stats", action="store_true", help="只報告覆蓋率，不呼叫模型")
    parser.add_argument("--report", action="store_true",
                        help="稽核：列出同一詞形在不同單元被譯得不一致者，不呼叫模型")
    args = parser.parse_args()

    units = collect_units()
    wanted = args.kinds.strip()
    if wanted != "all":
        keys = {key.strip() for key in wanted.split(",") if key.strip()}
        units = [unit for unit in units if unit["kind"].split("_")[0] in keys]

    global _model, _model_chain
    _model_chain = MODEL_CHAINS[args.model]
    _model = _model_chain[0]

    master = load_master()
    require_engine = _model if args.upgrade else ""
    pending = [
        unit for unit in units
        if not unit_complete(master["units"].get(unit["id"]), unit, require_engine=require_engine)
    ]
    total_words = sum(len(unit["tokens"]) for unit in units)
    print(f"單元 {len(units)}／詞 {total_words}；已完成 {len(units) - len(pending)}，待處理 {len(pending)}", flush=True)
    if args.report:
        consistency_report(master["units"])
        return
    if args.stats or not pending:
        return

    anchor = vocabulary_anchor()
    write_lock = threading.Lock()
    failures: list[str] = []

    # Prove one batch before committing a long unattended run: a prompt or
    # parsing fault should surface in minutes, not after a night of retries.
    if not args.limit:
        probe = batch_units(pending, args.max_words)[0]
        results: dict[str, dict[str, Any]] = {}
        problems: list[str] = []
        # An exhausted quota must not kill an unattended run before it starts:
        # keep re-offering the probe, since the shared gate already spaces the
        # attempts out by up to half an hour.
        for attempt in range(1, args.probe_attempts + 1):
            try:
                results, problems = run_batch(probe, anchor)
            except Exception as error:  # noqa: BLE001 - keep waiting for capacity
                print(f"試跑第 {attempt}/{args.probe_attempts} 次未成：{type(error).__name__}", flush=True)
                continue
            if results:
                break
            print(f"試跑第 {attempt}/{args.probe_attempts} 次被驗證退回：", flush=True)
            for line in problems[:6]:
                print(f"  {line}", flush=True)
        if not results:
            # One stubborn batch must not cancel the other 999 units; report it
            # and let the rounds carry on, since it stays in the pending list.
            print("試跑批次始終沒過，改為直接進入正式輪次", flush=True)
        if results:
            master["units"].update(results)
            master["engine"] = _model
            save_master(master)
            print(f"試跑通過（{_model}）：{probe[0]['group']} → {len(results)}/{len(probe)} 單元", flush=True)
        pending = [
            unit for unit in units
            if not unit_complete(master["units"].get(unit["id"]), unit, require_engine=require_engine)
        ]

    # Rounds, not one pass: a batch that 429s or comes back malformed is retried
    # in the next round instead of silently dropping its verses from the book.
    for round_index in range(1, args.rounds + 1):
        batches = batch_units(pending, args.max_words)
        if args.limit:
            batches = batches[: args.limit]
        print(f"第 {round_index} 輪：{len(pending)} 單元分成 {len(batches)} 批", flush=True)
        failures = []
        done = 0
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = {pool.submit(run_batch, batch, anchor): batch for batch in batches}
            for future in as_completed(futures):
                batch = futures[future]
                try:
                    results, problems = future.result()
                except Exception as error:  # noqa: BLE001 - retried next round
                    failures.append(f"{batch[0]['id']}…：{type(error).__name__} {error}")
                    continue
                failures.extend(problems)
                with write_lock:
                    master["units"].update(results)
                    master["engine"] = _model
                    save_master(master)
                    done += 1
                    print(f"[{done}/{len(batches)}] {batch[0]['group']} → {len(results)}/{len(batch)} 單元", flush=True)
        pending = [
            unit for unit in units
            if not unit_complete(master["units"].get(unit["id"]), unit, require_engine=require_engine)
        ]
        if not pending or args.limit:
            break
        print(f"第 {round_index} 輪結束，仍缺 {len(pending)} 單元", flush=True)

    remaining = [
        unit for unit in units
        if not unit_complete(master["units"].get(unit["id"]), unit, require_engine=require_engine)
    ]
    print(f"完成：{len(units) - len(remaining)}／{len(units)}；未完成 {len(remaining)}", flush=True)
    if failures:
        print("--- 需重跑 ---", flush=True)
        for line in failures[:40]:
            print(f"  {line}", flush=True)
        if len(failures) > 40:
            print(f"  …另有 {len(failures) - 40} 筆", flush=True)


if __name__ == "__main__":
    main()
