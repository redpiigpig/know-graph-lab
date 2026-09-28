#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""電子圖書館外文書中譯佇列（2026-09-28 使用者定：宗教學與宗教史先、跟博論碩論有關的最先）。

書單：output/translation_queue/religion_queue.tsv（scripts/build_translation_queue.py 產生，已排序）。

為什麼不直接用 translate_ebook_to_zh.py：
  - 它從原檔重新解析（PDF 靠書籤切章、page_number 一律 None）——會丟掉 09-27 補回的印刷頁碼、
    一節一塊與 {{p:N}} 標記；掃描書也不能翻。
  - 它的輸出檔就是該書 JSONL：翻到一半網站只剩已翻章節；--resume 還會把英文原文當成已完成。
這支：
  1. 第一次處理時把現有 JSONL 另存 `{id}.jsonl.src_en`（翻譯唯一來源，之後不再動）
  2. 逐塊翻（同 translate_ebook_to_zh：split_oversized 分片、截短閘），每塊譯好就寫進
     output/translation_queue/progress/{id}.jsonl（fsync，可續跑）
  3. 全書每塊都有譯文才一次換掉 `{id}.jsonl`＋推 R2＋更新 DB；翻譯期間網站維持完整原書
  4. 每塊的 chapter_path／page_number／page_numbers／printed_page(s)／chunk_type 原樣帶過去；
     content＝繁中、source_text＝原文、source_lang＝en（reader 的「中／對照／外」切換）
引擎：Gemini → NVIDIA，**不接 Haiku**（大量翻譯不耗 Claude 額度，[[feedback_save_claude_usage]]）。
失敗的塊留著，下一輪再翻；整本完成印 `LIBRARY_BOOK_DONE`，全佇列完成印 `LIBRARY_QUEUE_COMPLETE`。

  python -X utf8 scripts/library_translate_queue.py [--max-books N] [--rank 0] [--dry-run]
"""
from __future__ import annotations

import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import translate_ebook_to_zh as te  # noqa: E402
import standardize_ebook as se  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CH = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\_chunks")
QUEUE = ROOT / "output/translation_queue/religion_queue.tsv"
PROG = ROOT / "output/translation_queue/progress"
KEEP = ("chunk_index", "chunk_type", "page_number", "page_numbers", "printed_page", "printed_pages",
        "chapter_path", "volume", "parent_volume", "format")


def translate_piece(piece: str) -> str:
    """Gemini 先、NVIDIA 後；都失敗 raise。截短閘同 translate_ebook_to_zh（中文字 <0.15×原文長度＝截短）。"""
    last = None
    for fn in (te.gemini_translate, te.nvidia_translate):
        for _ in range(2):
            try:
                out = fn(piece)
            except Exception as e:  # noqa: BLE001
                last = e
                break                                   # 這個引擎不行，換下一個
            cjk = len(re.findall(r"[\u4e00-\u9fff]", out or ""))
            if out and not (len(piece) >= 1500 and cjk < 0.15 * len(piece)):
                return out
            last = RuntimeError(f"truncated ({cjk} CJK / {len(piece)})")
    raise RuntimeError(str(last)[:200])


_AMBIG = {"里": "裡", "干": "幹", "后": "後", "面": "麵", "余": "餘", "台": "臺", "云": "雲", "系": "係"}
_orig_to_trad = te._to_traditional


def _smart_to_traditional(text: str) -> str:
    """只有真的混進簡體才轉。09-28 測試：已是繁體的「聶斯脫里」被 s2tw 轉成「聶斯脫裡」。
    判準：轉換後改動的字，扣掉「里→裡」這類本身就是正體字的歧義對，少於 3 個＝原本就是繁體，原樣回傳。"""
    conv = _orig_to_trad(text)
    if len(text) != len(conv):
        return conv
    real = sum(1 for a, b in zip(text, conv) if a != b and _AMBIG.get(a) != b)
    return conv if real >= 3 else text.translate(te._JUNK_CHARS)


te._to_traditional = _smart_to_traditional          # NVIDIA 路徑內部也用這支


def translate_chunk(content: str) -> str:
    parts = [translate_piece(p) for p in te.split_oversized(content, max_chars=te.MAX_CHUNK_CHARS)]
    zh = _smart_to_traditional("\n\n".join(parts))
    return te.pl.collapse_cjk_spacing(zh)


def load_progress(bid: str) -> dict[int, str]:
    p = PROG / f"{bid}.jsonl"
    done = {}
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            try:
                o = json.loads(line)
                done[int(o["i"])] = o["zh"]
            except (json.JSONDecodeError, KeyError, ValueError):
                continue                                # 斷電寫壞的行略過
    return done


def append_progress(bid: str, i: int, zh: str) -> None:
    PROG.mkdir(parents=True, exist_ok=True)
    with open(PROG / f"{bid}.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps({"i": i, "zh": zh}, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def translatable(c: dict) -> bool:
    t = (c.get("content") or "").strip()
    return len(t) >= 30 and len(re.findall(r"[A-Za-z]", t)) > 0.3 * len(t)


def run_book(bid: str, dry: bool) -> bool | None:
    live = CH / f"{bid}.jsonl"
    src = CH / f"{bid}.jsonl.src_en"
    if not src.exists():
        if not live.exists():
            print(f"  ✗ 沒有 JSONL：{bid}", flush=True)
            return False
        cur = [json.loads(l) for l in live.open(encoding="utf-8") if l.strip()]
        if any("source_text" in c for c in cur):
            print("  已是雙語，略過", flush=True)
            return True
        import consolidate_page_chunks as cp
        if cp.eligible(cur) == "no-chapters":
            # chapters_via_llm_toc 還會改寫這本（補章節＋合併）；現在拿快照去翻，翻完寫回會蓋掉章節
            print("  還沒補章節（一頁一塊），先跳過，等章節批次處理完再翻", flush=True)
            return None
        if not dry:
            shutil.copy2(live, src)
    chunks = [json.loads(l) for l in (src if src.exists() else live).open(encoding="utf-8") if l.strip()]
    done = load_progress(bid)
    todo = [i for i, c in enumerate(chunks) if translatable(c) and i not in done]
    print(f"  {len(chunks)} 塊，已譯 {len(done)}，待譯 {len(todo)}", flush=True)
    if dry:
        return False
    fails = 0
    for i in todo:
        try:
            zh = translate_chunk(chunks[i]["content"])
        except Exception as e:  # noqa: BLE001
            fails += 1
            print(f"  ✗ 塊 {i}：{str(e)[:100]}", flush=True)
            if fails >= 5:
                print("  連續失敗 5 塊，本輪先停（引擎多半沒額度）", flush=True)
                return False
            continue
        fails = 0
        append_progress(bid, i, zh)
        done[i] = zh
        print(f"  ✓ 塊 {i}（{len(chunks[i]['content'])}→{len(zh)}）", flush=True)
    if any(translatable(c) and i not in done for i, c in enumerate(chunks)):
        return False
    out = []
    for i, c in enumerate(chunks):
        o = {k: c[k] for k in KEEP if k in c}
        if i in done:
            o.update(content=done[i], source_text=c["content"], source_lang="en", format="markdown",
                     translation="self")          # reader：中文欄頁碼寫 t.N
        else:
            o["content"] = c.get("content") or ""        # 封面、空頁等不需翻的塊原樣
        out.append(o)
    path = se.write_jsonl(bid, out)
    se.push_to_r2(bid, path)
    se.update_db(bid, out)
    print(f"LIBRARY_BOOK_DONE {bid}", flush=True)
    return True


def main() -> int:
    dry = "--dry-run" in sys.argv
    max_books = int(sys.argv[sys.argv.index("--max-books") + 1]) if "--max-books" in sys.argv else None
    rank = sys.argv[sys.argv.index("--rank") + 1] if "--rank" in sys.argv else None
    rows = [l.split("\t") for l in QUEUE.read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    if rank is not None:
        rows = [r for r in rows if r[0] == rank]
    seen_titles: set[str] = set()
    handled = skipped = 0
    for r in rows:
        bid, title = r[1], r[2]
        key = re.sub(r"\W", "", title.lower())[:40]
        if key in seen_titles:                           # 同書重複館藏只翻一次
            continue
        seen_titles.add(key)
        live = CH / f"{bid}.jsonl"
        if live.exists() and not (CH / f"{bid}.jsonl.src_en").exists():
            with live.open(encoding="utf-8") as f:
                if '"source_text"' in f.readline() + f.readline():
                    continue                             # 已翻完的
        elif (CH / f"{bid}.jsonl.src_en").exists():
            with live.open(encoding="utf-8") as f:
                if '"source_text"' in f.readline():
                    continue
        print(f"\n▶ [{r[0]}] {title}", flush=True)
        ok = run_book(bid, dry)
        if ok is None:
            skipped += 1                                 # 等補章節，之後的輪次再翻
            continue
        handled += 1
        if not ok and not dry:
            return 0                                     # 沒翻完就結束本輪，fleet keeper 下次接著跑
        if max_books and handled >= max_books:
            return 0
    if not dry and not skipped:                          # 有跳過的就不退役（fleet keeper 會再拉起來）
        print("LIBRARY_QUEUE_COMPLETE", flush=True)
    elif skipped:
        print(f"本輪跳過 {skipped} 本（等補章節），不印完成標記", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
