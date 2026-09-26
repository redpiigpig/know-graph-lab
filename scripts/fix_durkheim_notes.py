"""修補涂爾幹《宗教生活的基本形式（英繁對照）》的註腳缺漏。

ebook_id: 80000000-0000-4000-8000-000000000008
JSONL:    G:\\我的雲端硬碟\\資料\\知識圖工作室\\_chunks\\80000000-0000-4000-8000-000000000008.jsonl

本書結構（2026-09-26 勘查）：
  - chunk 0..300：正文＋書末索引。註號 `[N]` 以「內文引用」形式散在句子中間。
  - chunk 301..372：書末「FOOTNOTES:」區塊，1,319 條註文，每條段落開頭是
    `[N] `（`\\n\\n` 分段，全書這一段一律只用單一空行分段——已逐 chunk 驗證）。

兩類缺漏：
  1. 「註文漏翻」：footnote 區塊裡英文有 `[N] ...` 整段，中文完全找不到 `[N]`。
     → 用 gemini_translate/nvidia_translate 逐條譯出，插回 [N-1] 與 [N+1] 之間。
  2. 「正文註號遺失」：body/index 區塊裡英文句子夾雜 `[N]`，中文對應段落沒有
     這個編號。→ 用引擎判斷中文段落裡的對應位置，只插入「[N]」，其餘文字
     不可變動（用去除所有 [N] 後的逐字比對驗證）。

用法：
  python fix_durkheim_notes.py --dry-run
  python fix_durkheim_notes.py --apply [--category all|footnotes|refs] [--limit N]
  python fix_durkheim_notes.py --verify
  python fix_durkheim_notes.py --push          # 備份已存在時直接推 R2 + 更新 DB total_chars

節省用量：全程走 Gemini→NVIDIA 引擎鏈，不使用 Claude/Haiku。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import translate_ebook_to_zh as te  # gemini_translate / nvidia_translate / unusable_reason / R2 helpers
import translation_fix as tf        # clear_reason
import standardize_ebook as se      # push_to_r2

BOOK_ID = "80000000-0000-4000-8000-000000000008"
CHUNKS_PATH = te.CHUNKS_DIR / f"{BOOK_ID}.jsonl"
BACKUP_PATH = CHUNKS_PATH.with_suffix(CHUNKS_PATH.suffix + ".notes.bak")

DEF_HEAD_RE = re.compile(r"^\[(\d+)\]\s")
INLINE_NUM_RE = re.compile(r"\[(\d+)\]")
CHECKPOINT_EVERY = 5  # 條目數不多且引擎呼叫慢，checkpoint 密一點，避免中斷丟工

# 2026-09-26 勘查發現：部分註文確實已經翻譯，只是引擎把方括號寫成了全形
# 括號變體（〔N〕／【N】），不是真的漏翻——先歸一化成 ASCII「[N]」，
# 免得被誤判成「漏翻」而重譯出重複段落。純字形替換，不動文字內容。
_BRACKET_VARIANTS = [("〔", "〕"), ("【", "】")]  # 〔〕 【】
_BRACKET_VARIANT_RES = [
    (re.compile(re.escape(lb) + r"(\d+)" + re.escape(rb)), lb, rb)
    for lb, rb in _BRACKET_VARIANTS
]


def log(msg: str) -> None:
    print(msg, flush=True)


# ── I/O ──────────────────────────────────────────────────────────────────
def load_chunks(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def dump_chunks(path: Path, chunks: list[dict]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    tmp.replace(path)


def ensure_backup() -> None:
    if not BACKUP_PATH.exists():
        import shutil
        shutil.copy2(CHUNKS_PATH, BACKUP_PATH)
        log(f"備份完成 → {BACKUP_PATH}")
    else:
        log(f"備份已存在，跳過 → {BACKUP_PATH}")


# ── 分段 / 判準 ───────────────────────────────────────────────────────────
def paragraphs(text: str) -> list[str]:
    if not text:
        return []
    return text.split("\n\n")


def marker_present(text: str, n: int) -> bool:
    return re.search(rf"(?<!\d)\[{n}\](?!\d)", text or "") is not None


def normalize_brackets(chunks: list[dict]) -> int:
    """把 content 欄位裡的全形括號變體註號（〔N〕／【N】）改回 ASCII「[N]」。
    只動字形，不動文字內容。回傳歸一化掉的個數。"""
    total = 0
    for c in chunks:
        zh = c.get("content") or ""
        changed = False
        for pat, _lb, _rb in _BRACKET_VARIANT_RES:
            new_zh, n = pat.subn(r"[\1]", zh)
            if n:
                total += n
                zh = new_zh
                changed = True
        if changed:
            c["content"] = zh
    return total


def find_zone_start(chunks: list[dict]) -> int:
    for i, c in enumerate(chunks):
        if "FOOTNOTES:" in (c.get("source_text") or ""):
            return i
    raise RuntimeError("找不到 'FOOTNOTES:' 標記，book 結構跟預期不一樣，先停手")


def classify(chunks: list[dict]) -> tuple[int, list[dict], list[dict]]:
    """回傳 (zone_start, cat1_footnote_missing, cat2_inline_ref_missing)。"""
    zone_start = find_zone_start(chunks)
    cat1: list[dict] = []
    cat2: list[dict] = []
    for i, ch in enumerate(chunks):
        src = ch.get("source_text") or ""
        zh = ch.get("content") or ""
        if i >= zone_start:
            for p in paragraphs(src):
                m = DEF_HEAD_RE.match(p)
                if not m:
                    continue
                n = int(m.group(1))
                if not marker_present(zh, n):
                    cat1.append({"idx": i, "n": n, "en_para": p})
        else:
            seen: set[int] = set()
            for m in INLINE_NUM_RE.finditer(src):
                n = int(m.group(1))
                if n in seen:
                    continue
                seen.add(n)
                if not marker_present(zh, n):
                    cat2.append({"idx": i, "n": n})
    return zone_start, cat1, cat2


def find_positional_target(ch: dict, n: int) -> int | None:
    """在 EN/ZH 段落數相同的前提下，找出英文第 en_pi 段（開頭是 [n]）對應的
    中文段落 index。段落數不同就回傳 None（交給 LLM 全譯路徑）。"""
    ep = paragraphs(ch.get("source_text") or "")
    zp = paragraphs(ch.get("content") or "")
    if len(ep) != len(zp):
        return None
    for i, p in enumerate(ep):
        m = DEF_HEAD_RE.match(p)
        if m and int(m.group(1)) == n:
            return i
    return None


def resolve_positional_restores(chunks: list[dict], cat1: list[dict]) -> tuple[list[dict], list[dict]]:
    """分類 1 裡有一部分其實已經翻譯了，只是 [N] 前綴整段消失（模型吐出譯文時
    漏印編號，不是沒翻）。段落數對得上、且對應中文段落完全沒有任何括號編號
    的，直接補回「[N] 」前綴即可，不必再燒一次引擎重譯——重譯反而會跟已存在
    的譯文重複。段落數對不上、或對應段落已經有*不同*編號（真正的異常，不
    貿然覆寫）的，才落入 remaining，交給 LLM 全譯＋插入。"""
    restored: list[dict] = []
    remaining: list[dict] = []
    ANY_BRACKET_HEAD_RE = re.compile(r"^[\[〔【]\d")
    for it in cat1:
        idx, n = it["idx"], it["n"]
        ch = chunks[idx]
        pi = find_positional_target(ch, n)
        if pi is None:
            remaining.append(it)
            continue
        zp = paragraphs(ch["content"])
        target = zp[pi]
        if ANY_BRACKET_HEAD_RE.match(target):
            log(f"    [{n}] chunk_index={ch['chunk_index']} 對應段落已有其他編號，"
                f"不覆寫，記錄為異常：{target[:40]!r}")
            remaining.append(it)
            continue
        if not target.strip():
            remaining.append(it)
            continue
        zp[pi] = f"[{n}] {target}"
        ch["content"] = "\n\n".join(zp)
        restored.append(it)
    return restored, remaining


def dry_run() -> None:
    chunks = load_chunks(CHUNKS_PATH)
    norm_n = normalize_brackets(chunks)
    zone_start, cat1, cat2 = classify(chunks)
    restored, remaining = resolve_positional_restores(chunks, cat1)
    all_defs = set()
    for i in range(zone_start, len(chunks)):
        for p in paragraphs(chunks[i].get("source_text") or ""):
            m = DEF_HEAD_RE.match(p)
            if m:
                all_defs.add(int(m.group(1)))
    log(f"chunks 總數：{len(chunks)}；footnote 區塊起於 chunk_index={chunks[zone_start]['chunk_index']}"
        f"（第 {zone_start} 行）")
    log(f"英文註文總數（去重）：{len(all_defs)}（應為 1319）")
    log(f"括號字形歸一化（〔N〕／【N】→[N]，非漏翻）：{norm_n} 處")
    log("")
    log(f"[分類 1] 註文漏翻（歸一化後）：{len(cat1)} 條")
    log(f"  其中：位置還原即可（已翻譯只是漏印編號，不需再燒引擎）：{len(restored)} 條")
    log(f"        真的需要引擎全譯：{len(remaining)} 條")
    by_chunk1: dict[int, list[int]] = {}
    for it in remaining:
        by_chunk1.setdefault(it["idx"], []).append(it["n"])
    for idx in sorted(by_chunk1):
        ci = chunks[idx]["chunk_index"]
        log(f"  chunk_index={ci} (行 {idx})：漏 {by_chunk1[idx]}")
    log("")
    log(f"[分類 2] 正文註號遺失：{len(cat2)} 處")
    by_chunk2: dict[int, list[int]] = {}
    for it in cat2:
        by_chunk2.setdefault(it["idx"], []).append(it["n"])
    for idx in sorted(by_chunk2):
        ci = chunks[idx]["chunk_index"]
        log(f"  chunk_index={ci} (行 {idx})：缺 {by_chunk2[idx]}")


# ── Gemini 通用呼叫（給分類 2 的標記回補用，非固定翻譯 prompt）──────────────
def _gemini_raw(prompt: str, timeout: int = 60) -> str:
    if not te.GEMINI_KEYS:
        raise RuntimeError("no Gemini API key")
    base = f"https://generativelanguage.googleapis.com/v1beta/models/{te.GEMINI_MODEL}:generateContent"
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.0, "responseMimeType": "text/plain"},
    }
    last_err = "?"
    for key in te.GEMINI_KEYS:
        for attempt, wait in enumerate((0, 3), start=1):
            if wait:
                time.sleep(wait)
            try:
                r = requests.post(f"{base}?key={key}", json=body, timeout=timeout)
            except requests.exceptions.RequestException as e:
                last_err = f"{type(e).__name__}"
                continue
            if r.status_code == 200:
                try:
                    return r.json()["candidates"][0]["content"]["parts"][0]["text"]
                except (KeyError, IndexError):
                    last_err = "empty-parts"
                    continue
            if r.status_code in (429, 502, 503, 504):
                last_err = f"HTTP {r.status_code}"
                continue
            raise RuntimeError(f"Gemini HTTP {r.status_code}: {r.text[:200]}")
    raise RuntimeError(f"Gemini raw 全部失敗（最後: {last_err}）")


# ── 分類 1：補譯漏掉的註文 ─────────────────────────────────────────────────
# 🚨 Gemini 每天每 key 額度極少（免費層 ~20 次/天/key），撞到「全部 key 429」
# 代表當天配額真的用完了，同一輪跑下去每一條都會重新耗 7 把 key × 3 次重試才
# 肯放棄——白白燒時間。一旦看過一次「all N Gemini keys exhausted」，這次執行
# 剩下的條目直接跳過 Gemini、改走 NVIDIA，省時間也省 quota 探測次數。
_GEMINI_DEAD_THIS_RUN = False


def _gemini_try(source: str, label: str) -> str | None:
    global _GEMINI_DEAD_THIS_RUN
    if _GEMINI_DEAD_THIS_RUN:
        return None
    try:
        return te.gemini_translate(source)
    except Exception as e:
        msg = str(e)
        if "Gemini keys exhausted" in msg or "no Gemini API key" in msg:
            log(f"    {label} gemini 本輪額度已耗盡（{msg[:60]}…）— 本次執行後續全改走 NVIDIA")
            _GEMINI_DEAD_THIS_RUN = True
        else:
            log(f"    {label} gemini 失敗：{e}")
        return None


def translate_footnote(en_para: str, n: int) -> str | None:
    zh = _gemini_try(en_para, f"[{n}]")
    if zh is not None:
        bad = te.unusable_reason(zh, en_para) or tf.clear_reason(zh, en_para)
        if bad:
            log(f"    [{n}] gemini 輸出被擋：{bad}")
            zh = None
    if zh is None:
        try:
            zh = te.nvidia_translate(en_para)
        except Exception as e:
            log(f"    [{n}] nvidia 失敗：{e}")
            return None
        bad = te.unusable_reason(zh, en_para) or tf.clear_reason(zh, en_para)
        if bad:
            log(f"    [{n}] nvidia 輸出被擋：{bad}")
            return None
    zh = zh.strip()
    if not re.match(rf"^\[{n}\]\s", zh):
        zh = re.sub(r"^\[\d+\]\s*", "", zh).strip()
        zh = f"[{n}] {zh}"
    return zh


def insert_footnote(ch: dict, n: int, zh_para: str) -> str:
    """插回 [N-1] 與 [N+1] 之間；找不到鄰居就退而求其次，回傳插入策略字串。"""
    paras = paragraphs(ch["content"])
    nums: dict[int, int] = {}
    for pi, p in enumerate(paras):
        m = DEF_HEAD_RE.match(p)
        if m:
            nums[int(m.group(1))] = pi
    if (n - 1) in nums:
        insert_pi = nums[n - 1] + 1
        strategy = "after-prev"
    elif (n + 1) in nums:
        insert_pi = nums[n + 1]
        strategy = "before-next"
    elif nums:
        lesser = [v for k, v in nums.items() if k < n]
        greater = [v for k, v in nums.items() if k > n]
        if lesser:
            insert_pi = max(lesser) + 1
            strategy = "after-nearest-lesser"
        else:
            insert_pi = min(greater)
            strategy = "before-nearest-greater"
    else:
        insert_pi = len(paras)
        strategy = "append-chunk-end"
    remaining_before = list(paras)
    paras.insert(insert_pi, zh_para)
    remaining_after = paras[:insert_pi] + paras[insert_pi + 1:]
    assert remaining_after == remaining_before, "插入註文動到了既有段落，中止"
    ch["content"] = "\n\n".join(paras)
    return strategy


def apply_footnotes(chunks: list[dict], items: list[dict], limit: int | None, ckpt) -> dict:
    stats = {"ok": 0, "failed": 0}
    for i, it in enumerate(items):
        if limit and stats["ok"] + stats["failed"] >= limit:
            break
        n = it["n"]
        idx = it["idx"]
        ch = chunks[idx]
        log(f"  註文 [{n}] (chunk_index={ch['chunk_index']}) 翻譯中…")
        zh_para = translate_footnote(it["en_para"], n)
        if zh_para is None:
            log(f"    [{n}] 兩個引擎都失敗，跳過（保留缺漏，之後可重跑）")
            stats["failed"] += 1
            continue
        strategy = insert_footnote(ch, n, zh_para)
        log(f"    [{n}] 已插入（{strategy}）")
        stats["ok"] += 1
        if stats["ok"] % CHECKPOINT_EVERY == 0:
            ckpt()
    return stats


# ── 分類 2：補回正文缺漏的註號 ─────────────────────────────────────────────
MARKER_PROMPT = """你在做「原文腳注標記回補」的核對工作，不是翻譯。

以下是一段英文原文段落（其中 [{n}] 是腳注標記，出現在某個字詞後面），
以及它對應的繁體中文譯文段落（已翻譯完成，但漏掉了 [{n}] 這個標記）。

--- 英文原文段落 ---
{en_para}

--- 繁體中文譯文段落（目前沒有 [{n}]）---
{zh_para}

請找出中文段落裡「語意上對應英文 [{n}] 出現位置」的地方（通常是同一句話
句尾標點前後），把「[{n}]」原封不動插入該處。

規則（極重要）：
- 只能插入「[{n}]」這幾個字元本身，中文段落其餘部分一字不能更動、不能改
  標點、不能改換行、不能翻譯、不能潤飾、不能刪減。
- 直接輸出插入後的完整中文段落，不要加任何說明文字，不要用程式碼區塊包住。
"""


def _strip_code_fence(t: str) -> str:
    t = t.strip()
    t = re.sub(r"^```\w*\n?", "", t)
    t = re.sub(r"\n?```$", "", t)
    return t.strip()


def _strip_markers(t: str) -> str:
    return re.sub(r"\[\d+\]\s?", "", t or "")


def request_marker_insert(en_para: str, zh_para: str, n: int) -> str | None:
    global _GEMINI_DEAD_THIS_RUN
    prompt = MARKER_PROMPT.format(n=n, en_para=en_para, zh_para=zh_para)

    def _try_gemini_raw():
        global _GEMINI_DEAD_THIS_RUN
        if _GEMINI_DEAD_THIS_RUN:
            raise RuntimeError("gemini 本輪已耗盡，跳過")
        try:
            return _gemini_raw(prompt)
        except Exception as e:
            if "Gemini raw 全部失敗" in str(e) or "no Gemini API key" in str(e):
                log(f"    [{n}] gemini 本輪額度已耗盡（{str(e)[:60]}…）— 本次執行後續全改走 NVIDIA")
                _GEMINI_DEAD_THIS_RUN = True
            raise

    attempts = (
        ("gemini", _try_gemini_raw),
        ("nvidia", lambda: te.nvidia_chat(prompt, max_tokens=1500, thinking=False, deadline_s=90)),
    )
    for engine_name, fn in attempts:
        try:
            out = fn()
        except Exception as e:
            log(f"    [{n}] {engine_name} 失敗：{e}")
            continue
        out = _strip_code_fence(out)
        if not marker_present(out, n):
            log(f"    [{n}] {engine_name} 輸出沒有 [{n}]，捨棄")
            continue
        if _strip_markers(out) != _strip_markers(zh_para):
            log(f"    [{n}] {engine_name} 輸出動到了段落文字，捨棄")
            continue
        return out
    return None


def apply_refs(chunks: list[dict], items: list[dict], limit: int | None, ckpt) -> dict:
    stats = {"inserted": 0, "appended_para": 0, "appended_chunk": 0}
    count = 0
    for it in items:
        if limit and count >= limit:
            break
        count += 1
        n = it["n"]
        idx = it["idx"]
        ch = chunks[idx]
        src_paras = paragraphs(ch.get("source_text") or "")
        zh_paras = paragraphs(ch.get("content") or "")
        en_pi = next((i for i, p in enumerate(src_paras) if marker_present(p, n)), None)
        log(f"  正文註號 [{n}] (chunk_index={ch['chunk_index']}) 定位中…")
        if en_pi is not None and len(src_paras) == len(zh_paras):
            zh_target = zh_paras[en_pi]
            out = request_marker_insert(src_paras[en_pi], zh_target, n)
            if out is not None:
                zh_paras[en_pi] = out
                ch["content"] = "\n\n".join(zh_paras)
                log(f"    [{n}] 已插入對應句尾")
                stats["inserted"] += 1
            else:
                zh_paras[en_pi] = zh_target.rstrip() + f"[{n}]"
                ch["content"] = "\n\n".join(zh_paras)
                log(f"    [{n}] 找不到對應句，放在該段落結尾（已記錄）")
                stats["appended_para"] += 1
        else:
            ch["content"] = (ch.get("content") or "").rstrip() + f" [{n}]"
            log(f"    [{n}] 段落數對不上英文，放在整個 chunk 結尾（已記錄）")
            stats["appended_chunk"] += 1
        total = stats["inserted"] + stats["appended_para"] + stats["appended_chunk"]
        if total % CHECKPOINT_EVERY == 0:
            ckpt()
    return stats


# ── 驗證 ─────────────────────────────────────────────────────────────────
def verify(chunks: list[dict] | None = None) -> tuple[set[int], set[int]]:
    """回傳 (en_only, zh_only) 兩邊註號集合的差集，理想上兩者皆空。"""
    if chunks is None:
        chunks = load_chunks(CHUNKS_PATH)
    zone_start = find_zone_start(chunks)
    en_all: set[int] = set()
    zh_all: set[int] = set()
    for i, ch in enumerate(chunks):
        src = ch.get("source_text") or ""
        zh = ch.get("content") or ""
        if i >= zone_start:
            for p in paragraphs(src):
                m = DEF_HEAD_RE.match(p)
                if m:
                    en_all.add(int(m.group(1)))
            for p in paragraphs(zh):
                m = DEF_HEAD_RE.match(p)
                if m:
                    zh_all.add(int(m.group(1)))
        else:
            for m in INLINE_NUM_RE.finditer(src):
                en_all.add(int(m.group(1)))
            for m in INLINE_NUM_RE.finditer(zh):
                zh_all.add(int(m.group(1)))
    en_only = en_all - zh_all
    zh_only = zh_all - en_all
    log(f"英文註號集合：{len(en_all)}；中文註號集合：{len(zh_all)}")
    log(f"僅英文有（中文缺）：{sorted(en_only)}")
    log(f"僅中文有（英文沒有，理論上不該發生）：{sorted(zh_only)}")
    return en_only, zh_only


# ── 推 R2 + 更新 DB ─────────────────────────────────────────────────────
def push_and_update_db() -> None:
    chunks = load_chunks(CHUNKS_PATH)
    size = se.push_to_r2(BOOK_ID, CHUNKS_PATH)
    log(f"已推 R2：{size} bytes (gzip)")
    total_chars = sum(len(c.get("content") or "") for c in chunks)
    now = __import__("datetime").datetime.utcnow().isoformat() + "Z"
    r = requests.patch(
        f"{te.URL}/rest/v1/ebooks?id=eq.{BOOK_ID}",
        headers=te.H_JSON,
        json={"total_chars": total_chars, "standardized_at": now},
        timeout=30,
    )
    r.raise_for_status()
    log(f"DB total_chars 已更新為 {total_chars}")


# ── main ─────────────────────────────────────────────────────────────────
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--category", choices=["all", "footnotes", "refs"], default="all")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--push", action="store_true")
    args = ap.parse_args()

    if args.dry_run:
        dry_run()
        return

    if args.verify:
        verify()
        return

    if args.push:
        push_and_update_db()
        return

    if args.apply:
        ensure_backup()
        chunks = load_chunks(CHUNKS_PATH)
        norm_n = normalize_brackets(chunks)
        if norm_n:
            log(f"括號字形歸一化：{norm_n} 處（〔N〕／【N】→[N]）")
            dump_chunks(CHUNKS_PATH, chunks)
        zone_start, cat1, cat2 = classify(chunks)
        log(f"待補：註文漏翻 {len(cat1)} 條 / 正文註號遺失 {len(cat2)} 處")

        def ckpt():
            dump_chunks(CHUNKS_PATH, chunks)
            log("  …checkpoint 已寫回 JSONL")

        if args.category in ("all", "footnotes") and cat1:
            restored, remaining = resolve_positional_restores(chunks, cat1)
            if restored:
                log(f"位置還原（已翻譯只是漏印編號，不需引擎）：{len(restored)} 條")
                ckpt()
            log(f"=== 分類 1：補譯真正漏翻的註文（{len(remaining)} 條）===")
            stats1 = apply_footnotes(chunks, remaining, args.limit, ckpt)
            log(f"分類 1 完成：成功 {stats1['ok']} / 失敗 {stats1['failed']}")
            ckpt()

        if args.category in ("all", "refs") and cat2:
            log("=== 分類 2：補回正文缺漏的註號 ===")
            stats2 = apply_refs(chunks, cat2, args.limit, ckpt)
            log(f"分類 2 完成：插入對應句 {stats2['inserted']} / "
                f"段落結尾 {stats2['appended_para']} / chunk 結尾 {stats2['appended_chunk']}")
            ckpt()

        log("=== 收工，重新分類確認剩餘缺漏 ===")
        _, cat1_after, cat2_after = classify(load_chunks(CHUNKS_PATH))
        log(f"剩餘：註文漏翻 {len(cat1_after)} 條 / 正文註號遺失 {len(cat2_after)} 處")
        return

    ap.print_help()


if __name__ == "__main__":
    main()
