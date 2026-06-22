#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
classify_genesis_philosophy.py
================================
把 AI 對話錄 (ai_dialogues_gemini / ai_dialogues_chatgpt) 裡關於「創生哲學」的對話
用 LLM 判讀後，掛上 ai_dialogue_entry_categories 標籤。

分類階層 (見 /ai-dialogues 側欄)：
    創生哲學 (父)
      ├ 倫理學   ├ 認識論   ├ 本體論   ├ 價值論   ├ 存有論

流程：
  1. 候選池 = 七個哲學關鍵詞 (創生/倫理學/認識論/本體論/價值論/存有論/形上學)
     在 prompt 或 response 命中的對話（逐詞抓 id、Python 端聯集，避開大 OR timeout）。
  2. 排除「已被本批六個分類標過」與「ledger 已處理過」的 id（可續跑）。
  3. 每 BATCH 筆送一次 LLM（Gemini→NVIDIA→Haiku），回傳 JSON：
        belongs (是否屬創生哲學) + facets (五子類子集)。
  4. belongs=true → 掛「創生哲學」父標 + 各 facet 子標。
  5. ledger 記在 c:/tmp，斷線可續。

引擎政策：Gemini(4 keys 輪流) → NVIDIA(deepseek-v4-flash, 4 keys) → Haiku 救急。

用法：
    python classify_genesis_philosophy.py --source chatgpt            # 跑 chatgpt
    python classify_genesis_philosophy.py --source gemini
    python classify_genesis_philosophy.py --source all --limit 50     # 只試前 50
    python classify_genesis_philosophy.py --source chatgpt --dry-run  # 不寫 DB
    python classify_genesis_philosophy.py --source chatgpt --count    # 只算候選數
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
import time
import urllib.parse
from pathlib import Path

import requests

# ── env ──────────────────────────────────────────────────────────────────
def _load_dotenv() -> None:
    root = Path(__file__).resolve().parent.parent
    env = root / ".env"
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"].rstrip("/")
SERVICE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
SB_HDR = {"apikey": SERVICE_KEY, "Authorization": f"Bearer {SERVICE_KEY}"}

KEYWORDS = ["創生", "倫理學", "認識論", "本體論", "價值論", "存有論", "形上學"]
FACETS = ["倫理學", "認識論", "本體論", "價值論", "存有論"]
PARENT_NAME = "創生哲學"

LEDGER_DIR = Path("c:/tmp")
LEDGER_DIR.mkdir(parents=True, exist_ok=True)


# ── Supabase REST helpers ────────────────────────────────────────────────
def sb_get(path: str, params: dict | None = None, prefer: str | None = None,
           rng: tuple[int, int] | None = None) -> requests.Response:
    h = dict(SB_HDR)
    if prefer:
        h["Prefer"] = prefer
    if rng:
        h["Range"] = f"{rng[0]}-{rng[1]}"
    return requests.get(f"{SUPABASE_URL}/rest/v1/{path}", headers=h, params=params, timeout=120)


def get_category_ids() -> dict[str, str]:
    """Return {name: id} for 創生哲學 父 + 5 子. Errors if not all present."""
    r = sb_get("ai_dialogue_categories", {"select": "id,name,parent_id"})
    r.raise_for_status()
    rows = r.json()
    parent = next((c for c in rows if c["name"] == PARENT_NAME and not c["parent_id"]), None)
    if not parent:
        sys.exit(f"找不到父分類「{PARENT_NAME}」——請先建立分類。")
    out = {PARENT_NAME: parent["id"]}
    for f in FACETS:
        c = next((x for x in rows if x["name"] == f and x["parent_id"] == parent["id"]), None)
        if not c:
            sys.exit(f"找不到子分類「{f}」(parent={PARENT_NAME})。")
        out[f] = c["id"]
    return out


def fetch_candidate_ids(table: str) -> set[str]:
    """逐關鍵詞抓命中 id，Python 端聯集（避開 14-clause OR 的 statement timeout）。"""
    ids: set[str] = set()
    for kw in KEYWORDS:
        # raw value — requests url-encodes params once; PostgREST decodes %2A→* etc.
        flt = f"prompt.ilike.*{kw}*,response.ilike.*{kw}*"
        offset = 0
        page = 1000
        while True:
            r = sb_get(table, {"select": "id", "or": f"({flt})"},
                       rng=(offset, offset + page - 1))
            if r.status_code not in (200, 206):
                print(f"  ⚠ {table} kw={kw} HTTP {r.status_code}: {r.text[:160]}", flush=True)
                break
            rows = r.json()
            for row in rows:
                ids.add(row["id"])
            if len(rows) < page:
                break
            offset += page
        print(f"  候選累計 [{kw}] → {len(ids)}", flush=True)
    return ids


def fetch_already_tagged(cat_ids: list[str]) -> set[str]:
    tagged: set[str] = set()
    inlist = "(" + ",".join(cat_ids) + ")"
    offset = 0
    page = 1000
    while True:
        r = sb_get("ai_dialogue_entry_categories",
                   {"select": "dialogue_id", "category_id": f"in.{inlist}"},
                   rng=(offset, offset + page - 1))
        if r.status_code not in (200, 206):
            break
        rows = r.json()
        for row in rows:
            tagged.add(row["dialogue_id"])
        if len(rows) < page:
            break
        offset += page
    return tagged


def fetch_dialogues(table: str, ids: list[str]) -> list[dict]:
    out: list[dict] = []
    for i in range(0, len(ids), 200):
        chunk = ids[i:i + 200]
        inlist = "(" + ",".join(chunk) + ")"
        r = sb_get(table, {"select": "id,prompt,response", "id": f"in.{inlist}"})
        r.raise_for_status()
        out.extend(r.json())
    return out


def insert_tags(rows: list[dict]) -> None:
    """rows = [{dialogue_id, category_id}, ...] — upsert, ignore dups."""
    if not rows:
        return
    h = dict(SB_HDR)
    h["Content-Type"] = "application/json"
    h["Prefer"] = "resolution=ignore-duplicates,return=minimal"
    body = json.dumps(rows).encode("utf-8")
    r = requests.post(f"{SUPABASE_URL}/rest/v1/ai_dialogue_entry_categories",
                      headers=h, data=body, timeout=120)
    if r.status_code not in (200, 201, 204):
        print(f"  ⚠ insert tags HTTP {r.status_code}: {r.text[:200]}", flush=True)


# ── LLM engines (Gemini → NVIDIA → Haiku) ────────────────────────────────
def _find_keys(bases: tuple[str, ...]) -> list[str]:
    raw = []
    for b in bases:
        v = os.environ.get(b)
        if v:
            raw.append(v); break
    for n in range(1, 11):
        for b in bases:
            v = os.environ.get(f"{b}_{n}")
            if v:
                raw.append(v); break
    keys, seen = [], set()
    for r in raw:
        for piece in r.split(","):
            k = piece.strip()
            if k and k not in seen:
                seen.add(k); keys.append(k)
    return keys


GEMINI_KEYS = _find_keys(("GEMINI_API_KEY", "Gemini_API_Key", "GOOGLE_API_KEY"))
NVIDIA_KEYS = _find_keys(("NVIDIA_API_KEY", "NVIDIA_API_Key", "NVAPI_KEY"))
_g_idx = 0
_n_idx = 0

NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
NVIDIA_MODEL = "deepseek-ai/deepseek-v4-flash"

SYSTEM = (
    "你是一位嚴謹的哲學文獻分類助理。使用者（一位哲學創始者）長期與 AI 對話，"
    "發展自己原創的一套形上學體系，自稱「創生哲學」——核心關懷是存在/創生/生成"
    "（創生態、生成模式、being qua being）、意識與感質、現象學與泛心論、量子形上學、"
    "實在的本體結構、知識與真理的根基、價值與意義、道德的形上基礎等。\n\n"
    "請判斷每則對話是否屬於『使用者本人的創生哲學式哲學思辨』(belongs)。\n"
    "  belongs=true：真正在做哲學/形上學思辨、建構或辯證概念、追問存在與意識的本質。\n"
    "  belongs=false：寫程式/技術問答、生成圖片、論文計畫與行政格式、文獻書目/翻譯/校勘、"
    "宗教學或神學的資料整理（非哲學思辨）、純資訊查詢、閒聊。夾帶哲學詞彙但本質是上述事務者一律 false。\n\n"
    "若 belongs=true，再標 facets（依創生哲學 v2 領域邊界，務必嚴格區分）：\n"
    "  倫理學（應然）＝道德/善惡/誠實(誠實度 hi)/愛/主體的倫理生成/個人·群體·生物宇宙的倫理。\n"
    "  認識論（識然）＝知識/真理/如何認識世界/意向性/邏輯/數學的本質/語言/他心·感質·AI 的『認識』。\n"
    "  本體論＝存在『如何生成』的結構/創生公式/生成三要素(關係性·身體性·歷時性)/量子(觀察即坍縮·實在結構)/意識與主體的本體生成。\n"
    "  價值論（願然）＝願然/意欲/價值/美·美學/意義(願然面)/虛無(願然枯竭診斷)。\n"
    "  存有論（默然）＝空無/創生前態/默然·不可言說/神聖/虛無(存有面)/終極·永恆·死亡·終末/being qua being。\n"
    "  關鍵分界（最常錯，務必照此）：量子→本體論(非存有論)；數學→認識論；空無·默然·神聖·終極→存有論；"
    "願然·美→價值論；誠實·善→倫理學；創生公式·生成三要素·『生成的結構』→本體論(非存有論)。\n"
    "facets 只挑『最核心的 1～2 個』，不要把五個全填；若無明確面向可給 []。"
)

PROMPT_TMPL = (
    "以下是若干則對話（每則含使用者提問 prompt 與 AI 回應節錄）。"
    "請逐則判斷。嚴格只輸出 JSON 陣列，元素格式：\n"
    '  {{"i": <編號>, "belongs": true/false, "facets": ["倫理學",...]}}\n'
    "facets 只能用：倫理學, 認識論, 本體論, 價值論, 存有論，且最多 2 個。不要任何說明文字。\n\n"
    "對話：\n{items}"
)


def _build_items(batch: list[dict]) -> str:
    parts = []
    for i, d in enumerate(batch):
        p = (d.get("prompt") or "").strip().replace("\n", " ")[:600]
        rsp = (d.get("response") or "").strip().replace("\n", " ")[:900]
        parts.append(f"[{i}] 提問：{p}\n    回應：{rsp}")
    return "\n\n".join(parts)


def gemini_chat(system: str, prompt: str) -> str:
    global _g_idx
    if not GEMINI_KEYS:
        raise RuntimeError("no gemini key")
    body = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"},
    }
    base = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    tried = 0
    while tried < len(GEMINI_KEYS):
        key = GEMINI_KEYS[_g_idx]
        tried += 1
        for attempt, wait in enumerate((0, 3, 12), start=1):
            if wait:
                time.sleep(wait)
            try:
                r = requests.post(f"{base}?key={key}", json=body, timeout=90)
            except requests.exceptions.RequestException:
                if attempt >= 3:
                    break
                continue
            if r.status_code == 200:
                data = r.json()
                try:
                    return data["candidates"][0]["content"]["parts"][0]["text"].strip()
                except (KeyError, IndexError):
                    raise RuntimeError(f"bad gemini resp: {json.dumps(data)[:200]}")
            if r.status_code in (429, 500, 502, 503, 504):
                if attempt >= 3:
                    break
                continue
            raise RuntimeError(f"gemini HTTP {r.status_code}: {r.text[:200]}")
        _g_idx = (_g_idx + 1) % len(GEMINI_KEYS)
    raise RuntimeError("all gemini keys exhausted")


_THINK_RE = re.compile(r"<think>.*?</think>", re.S)


def nvidia_chat(system: str, prompt: str) -> str:
    global _n_idx
    if not NVIDIA_KEYS:
        raise RuntimeError("no nvidia key")
    tried = 0
    while tried < len(NVIDIA_KEYS):
        key = NVIDIA_KEYS[_n_idx]
        tried += 1
        try:
            r = requests.post(
                NVIDIA_URL,
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={"model": NVIDIA_MODEL,
                      "messages": [{"role": "system", "content": system},
                                   {"role": "user", "content": prompt}],
                      "temperature": 0.1, "max_tokens": 4000},
                timeout=300,
            )
        except requests.exceptions.RequestException:
            _n_idx = (_n_idx + 1) % len(NVIDIA_KEYS)
            time.sleep(3)
            continue
        if r.status_code == 200:
            return _THINK_RE.sub("", r.json()["choices"][0]["message"]["content"]).strip()
        _n_idx = (_n_idx + 1) % len(NVIDIA_KEYS)
        time.sleep(3)
    raise RuntimeError("all nvidia keys exhausted")


_haiku_client = None
_haiku_cred_mtime = 0.0


def _cred_path() -> Path:
    return Path(os.environ.get("USERPROFILE", os.environ.get("HOME", ""))) / ".claude" / ".credentials.json"


def _refresh_haiku_client(force: bool = False) -> None:
    """OAuth access token rotates every few hours while the interactive Claude Code
    session is open. Rebuild the client whenever credentials.json changes (or on
    force after a 401), so a long batch run never holds a stale token."""
    global _haiku_client, _haiku_cred_mtime
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        if _haiku_client is None:
            import anthropic
            _haiku_client = anthropic.Anthropic(api_key=api_key, timeout=300, max_retries=2)
        return
    cred = _cred_path()
    if not cred.exists():
        raise RuntimeError("no anthropic creds")
    m = cred.stat().st_mtime
    if force or _haiku_client is None or m > _haiku_cred_mtime:
        import anthropic
        tok = json.loads(cred.read_text(encoding="utf-8"))["claudeAiOauth"]["accessToken"]
        _haiku_client = anthropic.Anthropic(auth_token=tok, timeout=300, max_retries=2)
        _haiku_cred_mtime = m


def haiku_chat(system: str, prompt: str) -> str:
    import anthropic
    _refresh_haiku_client()
    for attempt in range(2):
        try:
            msg = _haiku_client.messages.create(
                model="claude-haiku-4-5-20251001", max_tokens=4000, system=system,
                messages=[{"role": "user", "content": prompt}],
            )
            return "".join(b.text for b in msg.content if hasattr(b, "text")).strip()
        except anthropic.AuthenticationError:
            if attempt == 0:
                _refresh_haiku_client(force=True)  # token rotated — re-read & retry once
                continue
            raise
    raise RuntimeError("haiku auth failed")


def llm_classify(batch: list[dict], max_rounds: int = 4, wait: int = 90) -> list[dict]:
    """Try Gemini→NVIDIA→Haiku. If ALL three fail (transient rate-limit storm or
    token rotation), wait and retry the whole chain rather than dropping the batch."""
    prompt = PROMPT_TMPL.format(items=_build_items(batch))
    for rnd in range(max_rounds):
        for name, fn in (("Gemini", gemini_chat), ("NVIDIA", nvidia_chat), ("Haiku", haiku_chat)):
            try:
                return _parse_json(fn(SYSTEM, prompt))
            except Exception as e:
                print(f"  · {name} 失敗：{type(e).__name__} {str(e)[:120]}", flush=True)
        if rnd < max_rounds - 1:
            print(f"  三引擎全失敗，等待 {wait}s 後重試（第 {rnd + 1}/{max_rounds} 輪）", flush=True)
            time.sleep(wait)
    raise RuntimeError("三引擎連續多輪全失敗")


def _parse_json(raw: str) -> list[dict]:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-z]*\n?|\n?```$", "", raw).strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\[.*\]", raw, re.S)
        if not m:
            raise
        data = json.loads(m.group(0))
    if isinstance(data, dict):
        data = data.get("results") or data.get("data") or [data]
    return data


# ── main ─────────────────────────────────────────────────────────────────
def process_source(source: str, cat: dict[str, str], batch_size: int,
                   limit: int | None, dry: bool) -> dict:
    table = f"ai_dialogues_{source}"
    print(f"\n=== {source} ===", flush=True)
    cand = fetch_candidate_ids(table)
    print(f"候選聯集：{len(cand)} 筆", flush=True)

    tagged = fetch_already_tagged(list(cat.values()))
    ledger = LEDGER_DIR / f"genesis_classify_{source}.jsonl"
    done: set[str] = set()
    if ledger.exists():
        for line in ledger.read_text(encoding="utf-8").splitlines():
            try:
                done.add(json.loads(line)["id"])
            except Exception:
                pass

    todo = [i for i in cand if i not in tagged and i not in done]
    todo.sort()
    if limit:
        todo = todo[:limit]
    print(f"已標 {len(tagged)}・ledger 已處理 {len(done)}・待判 {len(todo)}", flush=True)

    stats = {"judged": 0, "belongs": 0, "tags": 0}
    lf = None if dry else ledger.open("a", encoding="utf-8")
    try:
        for i in range(0, len(todo), batch_size):
            ids = todo[i:i + batch_size]
            rows = fetch_dialogues(table, ids)
            if not rows:
                continue
            try:
                verdicts = llm_classify(rows)
            except Exception as e:
                print(f"  batch {i // batch_size} 跳過：{e}", flush=True)
                continue
            vmap = {v.get("i"): v for v in verdicts if isinstance(v, dict)}
            tag_rows = []
            for idx, d in enumerate(rows):
                v = vmap.get(idx, {})
                belongs = bool(v.get("belongs"))
                facets = [f for f in (v.get("facets") or []) if f in FACETS]
                stats["judged"] += 1
                if belongs:
                    stats["belongs"] += 1
                    tag_rows.append({"dialogue_id": d["id"], "category_id": cat[PARENT_NAME]})
                    for f in facets:
                        tag_rows.append({"dialogue_id": d["id"], "category_id": cat[f]})
                if lf:
                    lf.write(json.dumps({"id": d["id"], "belongs": belongs,
                                         "facets": facets}, ensure_ascii=False) + "\n")
            if lf:
                lf.flush()
            stats["tags"] += len(tag_rows)
            if not dry:
                insert_tags(tag_rows)
            print(f"  進度 {min(i + batch_size, len(todo))}/{len(todo)}"
                  f"・本批 belongs {sum(1 for d in rows if vmap.get(rows.index(d), {}).get('belongs'))}"
                  f"・累計掛標 {stats['tags']}", flush=True)
    finally:
        if lf:
            lf.close()
    return stats


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["chatgpt", "gemini", "all"], default="chatgpt")
    ap.add_argument("--batch", type=int, default=10)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--count", action="store_true", help="只算候選數就離開")
    args = ap.parse_args()

    cat = get_category_ids()
    print("分類 id：", {k: v[:8] for k, v in cat.items()}, flush=True)

    sources = ["chatgpt", "gemini"] if args.source == "all" else [args.source]

    if args.count:
        for s in sources:
            c = fetch_candidate_ids(f"ai_dialogues_{s}")
            print(f"{s} 候選聯集：{len(c)}", flush=True)
        return

    total = {"judged": 0, "belongs": 0, "tags": 0}
    for s in sources:
        st = process_source(s, cat, args.batch, args.limit, args.dry_run)
        for k in total:
            total[k] += st[k]
    print(f"\n完成：判讀 {total['judged']}・屬創生哲學 {total['belongs']}"
          f"・掛標 {total['tags']}（dry-run={args.dry_run}）", flush=True)


if __name__ == "__main__":
    main()
