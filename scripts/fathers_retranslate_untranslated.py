#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把教父卷裡「中文欄其實是英文」的段補譯回來。

  python scripts/fathers_retranslate_untranslated.py --scan              # 全庫盤點
  python scripts/fathers_retranslate_untranslated.py --book <id>         # 只驗一本
  python scripts/fathers_retranslate_untranslated.py --book <id> --apply
  python scripts/fathers_retranslate_untranslated.py --all --apply       # 續跑全部

## 病灶

2026-09-11 量 `/fathers` 的中譯填充率時查到：13,173 段的中文欄**非空率 100%**，
但其中 1,677 段（12.7%）的「中文」其實是英文原文。最嚴重的是 ANF 第二卷
（Hermas／Tatian／Athenagoras／Clement of Alexandria）2,035 段裡有 1,517 段，
**而那一卷在 `/fathers` 首頁標著「已精修」**。

往下追，病灶不是「翻壞了」而是**從來沒翻**：那些段**連 `sources.en` 都沒有**——
英文原樣寫進 `content` 就收工，英文欄留空。所以修法是兩步：

  1. `content` 搬回 `sources.en`（它本來就是英文）
  2. 翻譯成繁中寫回 `content`

🚨 **只搬「英文欄是空的」那些段。** 英文欄已經有東西卻與 content 不同，代表那是
   另一回事（對齊或重切留下的），亂搬會把真正的英文原文蓋掉。

🚨 判「這是英文不是中文」要**先切掉註腳**。教父卷的註腳大量是原樣保留的英文書目與
   經文出處，連同正文一起算漢字率，正文明明譯好的段也會被判成未譯（實測 ANF 第二卷
   #8 正文 483 個漢字、註腳 1,093 個拉丁字母，整段只有 0.26）。判準共用
   `audit_fathers_coverage.zh_flags`，不另寫一套。

可續跑：每翻完一段就寫回 JSONL，中斷再跑會自動跳過已完成的。
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from audit_fathers_coverage import fathers_books, load_env, zh_flags  # noqa: E402

ROOT = SCRIPT_DIR.parent


# ── 純函式（測試在 scripts/tests/test_fathers_retranslate.py）────────────────

def needs_retranslate(chunk: dict) -> bool:
    """這一段的中文欄是不是其實是英文。"""
    return zh_flags(chunk.get("content") or "", 0)["untranslated"]


def promote_content_to_en(chunk: dict) -> bool:
    """把躺在 content 的英文搬回 sources.en；有動到回 True。

    🚨 英文欄已經有東西就不動。那代表這一段的狀況不是「沒翻」，亂搬會把真正的
       英文原文蓋掉，而且蓋掉之後查不回來。
    """
    src = chunk.setdefault("sources", {})
    if (src.get("en") or "").strip():
        return False
    body = (chunk.get("content") or "").strip()
    if not body:
        return False
    src["en"] = body
    if not (chunk.get("source_lang") or ""):
        chunk["source_lang"] = "en"
    chunk["source_text"] = body
    return True


FATHERS_PROMPT = """你是教父學的專業譯者，正在翻譯 Schaff 編《尼西亞前後教父全集》的英譯本。把下列英文原文翻成**繁體中文**。

規則：
1. 嚴守繁體中文（禁簡體）；中間點用「‧」。
2. 只翻譯，不要加任何前言、說明、譯註或原文回抄。**看不懂也不要說明，照譯**。
3. 語域：教父原典的論說散文。句子長、子句層層相扣，中譯要斷得開、讀得懂，但不可拆掉論證層次。
4. 保留 Markdown：`## ` `### ` `#### ` 標題照留；`[^N]` 註釋號原樣保留，不可刪也不可改號。
5. 🚨 希臘文與拉丁文原詞**原樣保留**，不要翻也不要轉寫。
6. 人名地名一律查 `/translation-glossary` 的教父表：Justin Martyr→猶斯定、Irenaeus→愛任紐、Clement of Alexandria→亞歷山卓的革利免、Tertullian→特土良、Origen→俄利根、Hermas→黑馬、Tatian→塔提安、Athenagoras→雅典那哥拉、Theophilus→提阿非羅、Cyprian→居普良、Hippolytus→希波呂圖、Athanasius→亞他那修、Basil→巴西流、Chrysostom→金口若望、Jerome→耶柔米、Augustine→奧古斯丁、Eusebius→優西比烏。
7. 聖經人名地名書卷名依和合本；引用聖經的句子譯為和合本語體。
8. 專名一對一不可改：Logos→道／邏各斯（依語境）、gnostic→諾斯底、catechumen→慕道者、presbyter→長老、bishop→主教、deacon→執事、heresy→異端、schism→分裂、martyr→殉道者、conversion→歸信（**不可用「回心」**）、missionary→宣教士。
9. 只輸出翻譯後的繁體中文。

英文原文：
{source}"""


def make_translate(backend: str = "auto"):
    import translate_ebook_to_zh as te
    te.PROMPT_TMPL = FATHERS_PROMPT

    def run(en: str) -> str:
        src = (en or "").strip()
        if not src:
            return ""
        pieces = te.split_oversized(src)
        for _ in range(3):
            out = " ".join(
                te.haiku_translate(p) if backend == "haiku"
                else te.gemini_translate(p) if backend == "gemini"
                else te.nvidia_translate(p) if backend == "nvidia"
                else te.gemini_with_nvidia_fallback(p)
                for p in pieces).strip()
            if out and not te._looks_like_prompt_echo(out):
                return out
        return ""

    return run


# ── 驅動 ────────────────────────────────────────────────────────────────────

def load_chunks(path: Path) -> list[dict]:
    chunks = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    chunks.sort(key=lambda c: c.get("chunk_index", 0))
    return chunks


def save_chunks(path: Path, chunks: list[dict]) -> None:
    tmp = path.with_suffix(".jsonl.tmp")
    tmp.write_text("\n".join(json.dumps(c, ensure_ascii=False) for c in chunks) + "\n",
                   encoding="utf-8")
    tmp.replace(path)


def run_book(path: Path, translate, apply: bool, limit: int = 0) -> tuple[int, int]:
    chunks = load_chunks(path)
    todo = [c for c in chunks if needs_retranslate(c)]
    if not todo or not apply:
        return len(todo), 0
    bak = path.with_suffix(".jsonl.bak_retranslate")
    if not bak.exists():
        shutil.copy2(path, bak)
    done = 0
    for c in todo:
        if limit and done >= limit:
            break
        promote_content_to_en(c)
        zh = translate((c.get("sources") or {}).get("en") or "")
        if not zh:
            print(f"    ✗ #{c['chunk_index']} 引擎沒回東西，跳過（留著下次再試）", flush=True)
            continue
        c["content"] = zh
        done += 1
        if done % 5 == 0:
            save_chunks(path, chunks)     # 可續跑：每五段落地一次
            print(f"    …{done}/{len(todo)}", flush=True)
    save_chunks(path, chunks)
    return len(todo), done


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--book")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--count", action="store_true",
                    help="只印還剩幾段（純數字，給排程腳本判斷要不要自我停用）")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0, help="每本最多翻幾段")
    ap.add_argument("--engine", default="auto")
    a = ap.parse_args()
    load_env()
    base = Path(os.environ["EBOOK_CHUNKS_DIR"])

    if a.book:
        targets = [{"id": a.book, "title": a.book[:8]}]
    else:
        targets = fathers_books()

    translate = make_translate(a.engine) if a.apply and not a.count else (lambda _s: "")
    total_todo = total_done = 0
    for b in sorted(targets, key=lambda x: x.get("title") or ""):
        p = base / f"{b['id']}.jsonl"
        if not p.exists():
            continue
        todo, done = run_book(p, translate, a.apply and not a.scan and not a.count, a.limit)
        total_todo += todo
        total_done += done
        if todo and not a.count:
            print(f"{(b.get('title') or '')[:52]:52} 待補 {todo:5}" +
                  (f"  本輪補了 {done}" if done else ""), flush=True)
    if a.count:
        # 純數字，不加任何裝飾——排程腳本靠它決定要不要自我停用。第一版讓它印
        # 中文句子再用 regex 去撈數字，撈到的是別的數字，keeper 於是永遠不停。
        print(total_todo)
        return 0
    print(f"\n合計待補 {total_todo} 段" + (f"；本輪補了 {total_done} 段" if total_done else ""))
    if not a.apply:
        print("（只驗不寫。確認無誤後加 --apply）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
