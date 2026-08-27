#!/usr/bin/env python3
"""Give every Greek vocabulary entry an English gloss as well as a Chinese one.

The reader's Chinese is the main gloss and stays that way; the English is the
row that lets the reader reach BDAG, LSJ and the English-language secondary
literature, and it was present on only 500 of the 2,000 entries — while the
lesson page printed an 英文 column that was three-quarters dashes.

Two sources, strongest first, and each entry records which one answered:

1. **Dodson** (*Greek-English Lexicon of the New Testament*, public domain,
   5,407 entries) — a published lexicon's own brief definition, matched on the
   lemma and then, failing that, on the lemma with its accents folded away.
   This is evidence rather than recall and covers 1,272 of the gap.
2. **Rendered from the reviewed Chinese** for what Dodson does not carry: the
   oblique pronoun forms the vocabulary lists separately (σέ, ὑμῶν) and the
   Septuagint and patristic words a New Testament lexicon has no reason to
   hold. The model is given the reviewed Chinese and asked to render *it*, not
   to recall the word — the Chinese is the reviewed layer, so the English must
   agree with it rather than wander off on its own.

    python -X utf8 scripts/fill_greek_gloss_en.py            # 報告，不寫
    python -X utf8 scripts/fill_greek_gloss_en.py --write
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import original_reader_llm as llm

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output/source-cache/original-readers/greek-full"
MASTER = CACHE / "greek-reader-two-volumes.json"
VOCAB = ROOT / "data/originalReaders/vocabulary/greek-2000.json"
DODSON = CACHE / "sources/dodson/dodson.xml"
RENDERED = CACHE / "gloss-en-rendered.json"

GREEK_RE = re.compile(r"[Ͱ-Ͽἀ-῿]")

PROMPT = """You are editing a Koine Greek reader's English gloss column.

For each numbered item below you are given the Greek headword and the reviewed
Traditional-Chinese gloss that the reader prints. Return a short English gloss
that means the same as the Chinese — you are rendering the Chinese, not
recalling the word.

Rules:
1. Return one JSON object: {{"glosses":[{{"index":1,"en":"..."}}]}}.
2. Same count, same indexes, same order.
3. Two to six words. No Greek letters, no Chinese, no explanation.
4. For a pronoun form, say which person, number and case it is, e.g.
   "you (sg. acc.)", "of us".

Items:
{items}
"""


def fold(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", text) if not unicodedata.combining(c)
    ).lower()


def dodson() -> tuple[dict[str, str], dict[str, str]]:
    xml = DODSON.read_text(encoding="utf-8")
    exact: dict[str, str] = {}
    for headword, body in re.findall(r'<entry n="([^"|]+)\s*\|[^"]*">(.*?)</entry>', xml, re.S):
        match = re.search(r'<def role="brief">(.*?)</def>', body, re.S)
        if not match:
            continue
        gloss = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", match.group(1))).strip()
        if gloss:
            exact.setdefault(headword.strip(), gloss)
    folded: dict[str, str] = {}
    for lemma, gloss in exact.items():
        folded.setdefault(fold(lemma), gloss)
    return exact, folded


PAIR_RE = re.compile(r'"index"\s*:\s*(\d+)\s*,\s*"en"\s*:\s*"(.*?)"\s*[,}]', re.S)


def parse_answers(raw: str) -> dict[int, str]:
    """Read index/en pairs out of the reply, strict JSON or not.

    An English gloss is full of apostrophes and the occasional quoted sense, so
    a fifth of the batches came back as JSON that ``json.loads`` refuses. The
    pairs are still perfectly readable; discarding the whole batch over a stray
    quote just means paying for it again.
    """

    block = re.search(r"\{.*\}", raw, re.S)
    if block:
        try:
            payload = json.loads(block.group(0))
            answers = {
                int(item["index"]): str(item.get("en", "")).strip()
                for item in payload.get("glosses", [])
                if str(item.get("index", "")).strip().isdigit()
            }
            if answers:
                return answers
        except (ValueError, TypeError, AttributeError):
            pass
    return {int(index): gloss.strip() for index, gloss in PAIR_RE.findall(raw)}


def render_missing(rows: list[dict], batch: int = 20) -> dict[str, str]:
    """English for what Dodson does not carry, rendered from the reviewed Chinese."""

    done: dict[str, str] = {}
    if RENDERED.exists():
        done = json.loads(RENDERED.read_text(encoding="utf-8")).get("glosses", {})
    pending = [row for row in rows if row["lemma"] not in done]
    print(f"  需要轉寫的 {len(rows)}，已快取 {len(rows) - len(pending)}")

    for start in range(0, len(pending), batch):
        chunk = pending[start : start + batch]
        items = "\n".join(
            f'{i + 1}. {row["lemma"]} — {row["glossZh"]}' for i, row in enumerate(chunk)
        )
        try:
            raw = llm.call_model(PROMPT.format(items=items), max_tokens=1600)
        except Exception as error:  # noqa: BLE001 - retried on the next run
            print(f"  ✗ 第 {start + 1}–{start + len(chunk)} 批：{error}")
            continue
        answers = parse_answers(raw)
        if not answers:
            print(f"  ✗ 第 {start + 1}–{start + len(chunk)} 批：回應讀不出 index/en")
            continue
        for index, row in enumerate(chunk, start=1):
            gloss = answers.get(index, "")
            if not gloss or GREEK_RE.search(gloss) or re.search(r"[一-鿿]", gloss):
                continue
            done[row["lemma"]] = gloss
        RENDERED.write_text(
            json.dumps({"schemaVersion": "1.0.0", "engine": llm.current_model(),
                        "note": "Dodson 未收的詞，依已覆核的繁中詞義轉寫成英文",
                        "glosses": done}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"  … {min(start + batch, len(pending))}/{len(pending)}", flush=True)
    return done


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--model", choices=sorted(llm.MODEL_CHAINS), default="auto")
    parser.add_argument("--no-render", action="store_true", help="只補 Dodson 查得到的")
    args = parser.parse_args()
    llm.select_chain(args.model)

    master = json.loads(MASTER.read_text(encoding="utf-8"))
    words = [w for v in master["volumes"] for l in v["lessons"] for w in l["vocabulary"]]
    missing = [w for w in words if not (w.get("glossEn") or "").strip()]
    print(f"詞條 {len(words)}，缺英文 {len(missing)}")

    exact, folded = dodson()
    filled: dict[str, tuple[str, str]] = {}
    for word in missing:
        lemma = word["lemma"]
        gloss = exact.get(lemma) or folded.get(fold(lemma))
        if gloss:
            filled[lemma] = (gloss, "dodson")
    print(f"  Dodson 補上 {len(filled)}")

    rest = [
        {"lemma": w["lemma"], "glossZh": w.get("glossZh", "")}
        for w in missing
        if w["lemma"] not in filled
    ]
    if rest and not args.no_render:
        for lemma, gloss in render_missing(rest).items():
            filled.setdefault(lemma, (gloss, "rendered"))
    print(f"  合計可補 {len(filled)}／{len(missing)}")

    if not args.write:
        print("（未寫入；加 --write）")
        return 0

    for word in words:
        entry = filled.get(word["lemma"])
        if entry and not (word.get("glossEn") or "").strip():
            word["glossEn"], word["glossEnSource"] = entry
    MASTER.write_text(json.dumps(master, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    vocab = json.loads(VOCAB.read_text(encoding="utf-8"))
    for entry in vocab["entries"]:
        found = filled.get(entry["lemma"])
        if found and not (entry.get("glossEn") or "").strip():
            entry["glossEn"], entry["glossEnSource"] = found
    VOCAB.write_text(json.dumps(vocab, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    still = sum(1 for w in words if not (w.get("glossEn") or "").strip())
    print(f"已寫入主檔與詞表；仍缺英文 {still}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
