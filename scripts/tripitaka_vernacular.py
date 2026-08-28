"""佛教大藏經 /tripitaka —— 漢文古譯 → 現代繁體白話。

漢譯佛典的文言對一般讀者是門檻。這一層在原文欄旁再開一欄現代白話，
讓「鳩摩羅什的文言」與「今人看得懂的話」並排 —— 這是使用者點名要的一欄。

引擎沿用既有的 Gemini → NVIDIA → Haiku 三層鏈（見 translate_ebook_to_zh），
只把 PROMPT_TMPL 換成文言→白話的版本，金鑰輪替／退避／配額處理全部照舊。
免費池乾了就 `--engine haiku`（Claude Max，直打 Haiku）。

🚨 這一支最容易靜默出錯的地方是**段落錯位**。一次送多段可以省呼叫數，
   但模型很容易把兩段併成一段、或漏掉一段，結果白話欄整批往前位移，
   而頁面看起來完全正常。所以：
     ① 每段標【N】記號送出，回來後**逐一比對記號集合**
     ② 記號對不上就把整批拆成單段重譯（不猜、不補、不丟）
     ③ 仍失敗的段留空，`--audit` 會列出來

輸出另存 `{id}.zhmod.json`（段 uid → 白話），不改動正文 JSONL：
正文是 CBETA 的原始資料，白話是本站產物，兩者分開才好各自重建。

  python scripts/tripitaka_vernacular.py --audit
  python scripts/tripitaka_vernacular.py --run T0251
  python scripts/tripitaka_vernacular.py --run-all --engine haiku
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import translate_ebook_to_zh as te  # noqa: E402

SEG_DIR = Path(os.environ.get("TRIPITAKA_LOCAL", "C:/tmp/cbeta/out"))
CATALOG = Path(os.environ.get("TRIPITAKA_CATALOG", "C:/tmp/cbeta/catalog.json"))

# 起手書單：流通最廣、白話化收益最高的一批。擴充直接加 id。
# （全藏 9,788 萬字不可能全譯，也不該全譯 —— 疏鈔、經錄、音義白話化沒有意義。）
WORKS = [
    "T0251",  # 般若波羅蜜多心經
    "T0235",  # 金剛般若波羅蜜經
    "T0366",  # 佛說阿彌陀經
    "T0784",  # 四十二章經
    "T0450",  # 藥師琉璃光如來本願功德經
    "T0353",  # 勝鬘師子吼一乘大方便方廣經
    "T0842",  # 大方廣圓覺修多羅了義經
    "T1666",  # 大乘起信論
    "T0246",  # 仁王護國般若波羅蜜多經
    "T2008",  # 六祖大師法寶壇經
    "T0475",  # 維摩詰所說經
    "T1564",  # 中論
    "T0159",  # 大乘本生心地觀經
    "T0262",  # 妙法蓮華經
]

# 一批送出的原文字數上限。給太多，模型併段漏段的機率明顯上升。
BATCH_CHARS = 1200
# 只譯這幾種段；標題與署名不必白話化
TRANSLATABLE = {"prose", "verse"}

PROMPT = """你是漢傳佛典的白話翻譯者。把下列**文言佛經**譯成現代繁體中文白話。

規矩：
1. 一律繁體中文。逐段對譯，不增不減、不加解釋、不加註腳。
2. 每段前面的【數字】記號**原樣保留**，數量與順序都不可更動。
   絕不可把兩段併成一段，也絕不可漏掉任何一段。
3. 佛教專有名詞**保留原譯不譯白**：佛號（阿彌陀佛、觀世音菩薩）、
   人名地名（舍利弗、祇樹給孤獨園）、音譯術語（般若波羅蜜、
   阿耨多羅三藐三菩提、涅槃、比丘、如是我聞）皆照抄。
4. 偈頌保持原有的分行，不要併成散文。
5. 只輸出譯文，不要任何前言、說明或標題。

原文：
{source}"""

_MARK = re.compile(r"【(\d+)】")


def load_segments(work_id: str) -> list[dict]:
    p = SEG_DIR / f"{work_id}.jsonl"
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def out_path(work_id: str) -> Path:
    return SEG_DIR / f"{work_id}.zhmod.json"


def load_done(work_id: str) -> dict[str, str]:
    p = out_path(work_id)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def make_batches(segs: list[dict], done: dict[str, str]) -> list[list[dict]]:
    """把待譯段落分批，單批原文不超過 BATCH_CHARS。"""
    todo = [s for s in segs
            if s.get("kind") in TRANSLATABLE
            and s["sources"].get("lzh")
            and not done.get(s["uid"])]
    batches, cur, size = [], [], 0
    for s in todo:
        n = len(s["sources"]["lzh"])
        if cur and size + n > BATCH_CHARS:
            batches.append(cur)
            cur, size = [], 0
        cur.append(s)
        size += n
    if cur:
        batches.append(cur)
    return batches


def render(batch: list[dict]) -> str:
    return "\n\n".join(f"【{i + 1}】{s['sources']['lzh']}" for i, s in enumerate(batch))


def parse_reply(reply: str, n: int) -> list[str] | None:
    """回覆 → n 段譯文。記號集合對不上就回 None（交由呼叫端拆單段重譯）。

    🚨 這道檢查是這一支的命門：模型併段或漏段時，若照順序硬分，
    白話欄會整批往前位移而頁面看不出異狀。
    """
    marks = [int(m) for m in _MARK.findall(reply)]
    if marks != list(range(1, n + 1)):
        return None
    parts = _MARK.split(reply)
    # split 後：[前言, '1', 內容1, '2', 內容2, …]
    out = [parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)]
    return out if len(out) == n and all(out) else None


def translate_work(work_id: str, translator, *, limit: int | None = None) -> dict:
    segs = load_segments(work_id)
    if not segs:
        return {"id": work_id, "error": "找不到正文檔"}
    done = load_done(work_id)
    batches = make_batches(segs, done)
    if limit:
        batches = batches[:limit]
    title = next((s["sources"]["lzh"] for s in segs if s.get("kind") == "head"), work_id)
    total_chars = sum(len(s["sources"]["lzh"]) for b in batches for s in b)
    print(f"\n=== {work_id} {title[:28]}　{len(batches)} 批／"
          f"{sum(len(b) for b in batches)} 段／{total_chars:,} 字（已完成 {len(done)}）", flush=True)

    ok = split_retry = failed = 0
    for i, batch in enumerate(batches, 1):
        try:
            reply = translator(render(batch))
        except Exception as e:  # noqa: BLE001
            print(f"  [{i}/{len(batches)}] 整批失敗 {type(e).__name__}: {str(e)[:80]}", flush=True)
            failed += len(batch)
            continue
        parts = parse_reply(reply, len(batch))
        if parts is None:
            # 記號對不上 → 拆成單段重譯，絕不照順序硬分
            split_retry += 1
            print(f"  [{i}/{len(batches)}] 記號不符（{len(batch)} 段）→ 拆單段重譯", flush=True)
            parts = []
            for s in batch:
                try:
                    one = translator(f"【1】{s['sources']['lzh']}")
                    got = parse_reply(one, 1)
                    parts.append(got[0] if got else "")
                except Exception:  # noqa: BLE001
                    parts.append("")
        for s, zh in zip(batch, parts):
            if zh:
                done[s["uid"]] = zh
                ok += 1
            else:
                failed += 1
        out_path(work_id).write_text(json.dumps(done, ensure_ascii=False), encoding="utf-8")
        if i % 10 == 0 or i == len(batches):
            print(f"  … {i}/{len(batches)} 批　完成 {ok}　拆批 {split_retry}　失敗 {failed}",
                  flush=True)
    return {"id": work_id, "title": title, "ok": ok, "split_retry": split_retry,
            "failed": failed, "total_done": len(done)}


def cmd_audit():
    rows = {r["id"]: r for r in json.loads(CATALOG.read_text(encoding="utf-8"))}
    print(f"{'經號':8s} {'經名':26s} {'可譯段':>7s} {'已譯':>7s} {'進度':>7s}")
    print("─" * 66)
    t_todo = t_done = 0
    for wid in WORKS:
        segs = load_segments(wid)
        todo = [s for s in segs if s.get("kind") in TRANSLATABLE and s["sources"].get("lzh")]
        done = load_done(wid)
        t_todo += len(todo)
        t_done += len(done)
        pct = f"{len(done) / len(todo):.0%}" if todo else "—"
        name = (rows.get(wid) or {}).get("title_zh", "")[:24]
        print(f"{wid:8s} {name:26s} {len(todo):>7,} {len(done):>7,} {pct:>7s}")
    print("─" * 66)
    print(f"{'合計':34s} {t_todo:>7,} {t_done:>7,} "
          f"{t_done / t_todo:.0%}" if t_todo else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", action="store_true")
    ap.add_argument("--run", type=str, help="單部，如 T0251")
    ap.add_argument("--run-all", action="store_true")
    ap.add_argument("--engine", default="auto",
                    choices=["auto", "haiku", "gemini", "nvidia"])
    ap.add_argument("--limit", type=int, help="每部只跑前 N 批（試跑用）")
    a = ap.parse_args()

    if a.audit:
        cmd_audit()
        return

    # 把三層鏈的提示詞換成文言→白話；其餘（金鑰輪替、退避、配額）照舊
    te.PROMPT_TMPL = PROMPT
    translator = {"haiku": te.haiku_first, "nvidia": te.nvidia_translate,
                  "gemini": te.gemini_with_nvidia_fallback}.get(
                      a.engine, te.gemini_with_nvidia_fallback)
    print(f"引擎：{a.engine}（{translator.__name__}）", flush=True)

    targets = [a.run] if a.run else (WORKS if a.run_all else [])
    if not targets:
        ap.print_help()
        return
    t0 = time.time()
    results = [translate_work(w, translator, limit=a.limit) for w in targets]
    print(f"\n{'':=<66}")
    for r in results:
        if r.get("error"):
            print(f"  ⚠ {r['id']}: {r['error']}")
        else:
            print(f"  {r['id']} {r.get('title','')[:24]:26s} 完成 {r['ok']:>5,}　"
                  f"拆批 {r['split_retry']:>3}　失敗 {r['failed']:>4}")
    print(f"耗時 {int(time.time() - t0)}s")


if __name__ == "__main__":
    main()
