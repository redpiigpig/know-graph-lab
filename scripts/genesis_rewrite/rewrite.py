# -*- coding: utf-8 -*-
"""創生哲學十五卷逐章改寫（引擎：Gemini，NVIDIA 備援）。

用法：
  python -X utf8 scripts/genesis_rewrite/rewrite.py --book V3 --limit 1 --dry-run
  python -X utf8 scripts/genesis_rewrite/rewrite.py --book V3
  python -X utf8 scripts/genesis_rewrite/rewrite.py --all

每章一個 API 呼叫，結果寫進帳本後才動檔案；重跑會跳過帳本裡已完成的章，
所以中斷可以直接續跑。帳本：c:/tmp/genesis_rewrite/ledger.jsonl

🚨 別跑 scripts/assemble_genesis_book.py——那支是 draft→HTML，
   會拿 c:/tmp 的舊草稿覆蓋掉這裡改好的部署檔。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
BOOKS = ROOT / "public" / "content" / "works" / "genesis"
HERE = Path(__file__).resolve().parent
WORK = Path("c:/tmp/genesis_rewrite")
LEDGER = WORK / "ledger.jsonl"
BACKUP = WORK / "backup"

SECTION_TAG_RE = re.compile(r"<section\b[^>]*>|</section\s*>")
H2_RE = re.compile(r"<h2[^>]*>(.*?)</h2>", re.S)


def split_chapters(doc: str) -> list[tuple[int, int]]:
    """回每個最外層 <section class="chapter"> 的 (起, 訖)。

    🚨 不能用 `<section class="chapter">.*?</section>` —— 每一章裡面都還有一個
    巢狀的 <section class="chapter-recap">（推論鏈那一塊），非貪婪比對會在 recap
    的 </section> 就收工，於是整章被截斷、後半段永遠不會被改寫，而且看起來完全正常。
    """
    spans, depth, start = [], 0, None
    for m in SECTION_TAG_RE.finditer(doc):
        if m.group(0).startswith("</"):
            depth -= 1
            if depth == 0 and start is not None:
                spans.append((start, m.end()))
                start = None
        else:
            if depth == 0 and 'class="chapter"' in m.group(0):
                start = m.start()
            depth += 1
    return spans
TAG_RE = re.compile(r"<[^>]+>")
FENCE_RE = re.compile(r"^\s*```(?:html)?\s*|\s*```\s*$", re.S)


# ---------------------------------------------------------------- 環境與引擎

def _load_env() -> None:
    """.env 是 KEY=VALUE 一行一筆；python-dotenv 不一定裝著，自己讀。"""
    f = ROOT / ".env"
    if not f.exists():
        return
    for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _find_keys(bases: tuple[str, ...]) -> list[str]:
    raw = []
    for b in bases:
        if os.environ.get(b):
            raw.append(os.environ[b])
    for n in range(1, 11):
        for b in bases:
            v = os.environ.get(f"{b}_{n}")
            if v:
                raw.append(v)
                break
    keys, seen = [], set()
    for r in raw:
        for piece in r.split(","):
            k = piece.strip()
            if k and k not in seen:
                seen.add(k)
                keys.append(k)
    return keys


_g_idx = 0
_n_idx = 0
GEMINI_KEYS: list[str] = []
NVIDIA_KEYS: list[str] = []

# 兩個模型的免費日額度是**分開的桶**（實測：同一把 key 在 flash-latest 已 429、
# 在 2.5-flash 仍 200），所以兩個都要吃。gemini-2.5-flash 對新帳號回 404
# （"no longer available to new users"），舊帳號的 key 才有——那也是額外的供給。
GEMINI_MODELS = ("gemini-flash-latest", "gemini-2.5-flash")
NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
NVIDIA_MODEL = "deepseek-ai/deepseek-v4-flash-0731"
_THINK_RE = re.compile(r"<think>.*?</think>", re.S)


class QuotaExhausted(RuntimeError):
    """今天的 Gemini 免費額度用完了。當天不會恢復，所以整輪就該收手。"""


# (model, key) 這一組今天已經沒了：429 是日額度耗盡，404 是這把 key 不支援該模型
_dead: set[tuple[str, str]] = set()


def gemini_chat(system: str, prompt: str) -> str:
    """依序試 (模型 × key) 的每一組合。

    🚨 不要長退避。免費層是 GenerateRequestsPerDayPerProjectPerModel-FreeTier=20，
    **日額度、當天不恢復**——睡再久也等不到，只會把整輪的時間耗光（實測整夜只前進一節）。
    額度用盡就丟 QuotaExhausted 讓整輪收手，排程半小時後自然會再來。
    """
    if not GEMINI_KEYS:
        raise RuntimeError("no gemini key")
    body = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.6,
            # 🚨 超過 8192 一律 503（實測 16384/24576/32768 全掛），別調高。
            "maxOutputTokens": 8192,
            "thinkingConfig": {"thinkingBudget": 1024},
        },
    }
    combos = [(m, k) for m in GEMINI_MODELS for k in GEMINI_KEYS if (m, k) not in _dead]
    if not combos:
        raise QuotaExhausted("所有 (模型×key) 組合今日皆已耗盡")

    last = ""
    for model, key in combos:
        base = (f"https://generativelanguage.googleapis.com/v1beta/models/"
                f"{model}:generateContent")
        for attempt in (1, 2):          # 只對暫時性錯誤重試一次
            try:
                r = requests.post(f"{base}?key={key}", json=body, timeout=900)
            except requests.exceptions.RequestException as e:
                last = type(e).__name__
                if attempt == 1:
                    time.sleep(5)
                    continue
                break
            if r.status_code == 200:
                data = r.json()
                try:
                    cand = data["candidates"][0]
                    txt = "".join(pt.get("text", "") for pt in cand["content"]["parts"])
                except (KeyError, IndexError):
                    last = f"bad resp {json.dumps(data)[:160]}"
                    break
                if cand.get("finishReason") not in (None, "STOP"):
                    last = f"finishReason={cand.get('finishReason')}"
                    break
                return txt.strip()
            if r.status_code in (429, 404):
                _dead.add((model, key))     # 今天不必再試這一組
                last = f"HTTP {r.status_code}"
                break
            if r.status_code in (500, 502, 503, 504):
                last = f"HTTP {r.status_code}"
                if attempt == 1:
                    time.sleep(5)
                    continue
                break
            raise RuntimeError(f"gemini HTTP {r.status_code}: {r.text[:200]}")

    if all((m, k) in _dead for m in GEMINI_MODELS for k in GEMINI_KEYS):
        raise QuotaExhausted(f"今日 Gemini 額度用盡（最後：{last}）")
    raise RuntimeError(f"gemini 全部組合皆敗，最後一次：{last}")


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
                      "temperature": 0.6, "max_tokens": 16000},
                # 🚨 逾時砍短：NVIDIA 這層目前整條是死的（deepseek flash/pro 都
                #    ReadTimeout、qwen3-next 410、nemotron/mistral 掛在清單上卻 404），
                #    留 600s 只會讓每一節白等十分鐘。
                timeout=60,
            )
        except requests.exceptions.RequestException:
            _n_idx = (_n_idx + 1) % len(NVIDIA_KEYS)
            time.sleep(5)
            continue
        if r.status_code == 200:
            msg = r.json()["choices"][0]["message"]
            # 推理模型有時 content 是 null、正文只在 reasoning_content 裡
            body = msg.get("content") or msg.get("reasoning_content") or ""
            body = _THINK_RE.sub("", body).strip()
            if body:
                return body
        _n_idx = (_n_idx + 1) % len(NVIDIA_KEYS)
        time.sleep(5)
    raise RuntimeError("all nvidia keys exhausted")


def llm(system: str, prompt: str) -> tuple[str, str]:
    """Gemini 主、NVIDIA 備援。回 (文字, 用了哪個引擎)。"""
    try:
        return gemini_chat(system, prompt), "gemini"
    except QuotaExhausted:
        raise                      # 整輪收手，交給排程下一次
    except Exception as e:  # noqa: BLE001
        print(f"    ⚠ gemini 失敗（{e}），改用 NVIDIA", flush=True)
        return nvidia_chat(system, prompt), "nvidia"


# ---------------------------------------------------------------- prompt

SYSTEM = (
    "你是使用者的哲學寫作助手。使用者是台灣的宗教研究學者，正在改寫他自己的原創哲學"
    "叢書《創生哲學》（十五卷）。你的工作是依他新確立的立場，改寫指定的一章。\n"
    "鐵則：\n"
    "1. 一律繁體中文。\n"
    "2. 一次只改寫使用者指定的那一塊，只輸出那一塊的 HTML 元素（通常是若干個 <p>）。"
    "不要複述整節、不要加 markdown 圍籬、不要加任何說明文字。\n"
    "3. 保留原有的 class 名稱與 HTML 結構；每個元素都要正確閉合。\n"
    "4. 保留哲普文風：可讀、有敘事、不堆術語。這次改的是論證，不是文體。\n"
    "5. 篇幅不得縮水。原塊多長，改寫後就要多長或更長。不可摘要、不可省略段落。\n"
    "6. 章名與章次編號不歸你管（<h2> 不會給你），不要自己補標題。\n"
    "7. 這是使用者自己的哲學，不是介紹別人的學說。用第一人稱的主張語氣，不要寫成綜述。"
)

TASK = """《{title}》（代號 {book}）這一節是〈{name}〉。

【改寫綱要——全書共用的新地基】
{positions}

【本卷指令】
改寫等級：{level}
{focus}

【本節全文（脈絡用，不要整篇輸出）】
{context}

【要你改寫的片段——就是上面全文裡的第 {ci}/{ctotal} 塊】
{chunk}

請只改寫這一塊，並只輸出這一塊的 HTML。凡與新地基牴觸的論證一律改掉；
未被指令點到但仍與新地基一致的段落，保留原樣或僅作語句層級的順稿。
輸出必須是完整的 HTML 元素（每個 <p> 都要閉合），數量可以與原塊不同，
但總篇幅不得少於原塊。不要輸出這一塊以外的內容，不要加 markdown 圍籬。"""


# ---------------------------------------------------------------- 帳本

def load_ledger() -> dict[str, dict]:
    done = {}
    if LEDGER.exists():
        for line in LEDGER.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rec = json.loads(line)
                done[f"{rec['book']}#{rec['idx']}"] = rec
    return done


def append_ledger(rec: dict) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------- 主流程

def plain(html: str) -> str:
    return TAG_RE.sub("", html)


VOID = {"br", "hr", "img", "input", "meta", "link", "source", "track",
        "wbr", "col", "area", "base", "embed", "param"}
TAGPOS_RE = re.compile(r"<(/?)([a-zA-Z0-9]+)[^>]*?(/?)>")


def top_level_blocks(inner: str) -> list[str]:
    """把一節的內容切成最外層的元素（<p>、<h3>、<div class="chapter-fable">…）。
    用深度計數而非正則配對——章首故事引子是巢狀 div，正則的 .*?</div> 會切錯。"""
    blocks, depth, start = [], 0, None
    for m in TAGPOS_RE.finditer(inner):
        closing, name, selfclose = m.group(1), m.group(2).lower(), m.group(3)
        if name in VOID or selfclose:
            continue
        if not closing:
            if depth == 0:
                start = m.start()
            depth += 1
        else:
            depth -= 1
            if depth == 0 and start is not None:
                blocks.append(inner[start:m.end()])
                start = None
    return blocks


def blocks_or_die(inner: str) -> list[str]:
    """切不乾淨就直接失敗。少切了一半內容卻照樣往下跑，是這條管線最危險的失敗模式：
    產出看起來正常、實際上整章後半沒被改到。"""
    blocks = top_level_blocks(inner)
    got, want = sum(len(plain(b)) for b in blocks), len(plain(inner))
    if want and got < want * 0.98:
        raise RuntimeError(f"區塊只回收 {got:,}／{want:,} 字，切法對不上這一節的標記")
    return blocks


def chunk_blocks(blocks: list[str], budget: int = 4200) -> list[list[int]]:
    """把可改寫的區塊編組，每組正文不超過 budget 字。

    輸出上限是 8192 token；中文大約一字一 token，4200 字進、五千多字出仍有餘裕。
    budget 直接決定總呼叫次數（2200 字要 594 次、4200 字剩約 300 次），而
    Gemini 免費層是每 key 每天二十次的日額度，呼叫次數就是整批能不能跑完的瓶頸。"""
    groups, cur, size = [], [], 0
    for i, b in enumerate(blocks):
        n = len(plain(b))
        if cur and size + n > budget:
            groups.append(cur)
            cur, size = [], 0
        cur.append(i)
        size += n
    if cur:
        groups.append(cur)
    return groups


def rewrite_section(book, spec, positions, section, idx, name, args):
    """回 (新的 section HTML, 用到的引擎集合)；失敗回 (None, 原因)。"""
    head = section[:section.index(">") + 1]
    inner = section[len(head):-len("</section>")]
    try:
        blocks = blocks_or_die(inner)
    except RuntimeError as e:
        return None, str(e)
    if not blocks:
        return None, "切不出區塊"

    # h2 與章首故事引子原樣穿過去，不送給模型——七月那批成果不冒險
    frozen = {i for i, b in enumerate(blocks)
              if b.lstrip().startswith(('<h2', '<div class="chapter-fable"'))}
    editable = [i for i in range(len(blocks)) if i not in frozen]
    groups = chunk_blocks([blocks[i] for i in editable])
    # groups 的索引是 editable 的位置，換回 blocks 的真索引
    groups = [[editable[j] for j in g] for g in groups]

    context = plain(inner)[:12000]
    focus = "\n".join(f"- {x}" for x in spec["focus"])
    cache = WORK / "chunks"
    cache.mkdir(parents=True, exist_ok=True)
    engines = set()

    for ci, g in enumerate(groups, start=1):
        cf = cache / f"{book}_{idx}_{ci}.html"
        chunk = "\n".join(blocks[i] for i in g)
        if cf.exists():
            out = cf.read_text(encoding="utf-8")
            print(f"      · 塊 {ci}/{len(groups)} 用快取", flush=True)
        else:
            prompt = TASK.format(title=spec["title"], book=book, name=name,
                                 positions=positions, level=spec["level"], focus=focus,
                                 context=context, ci=ci, ctotal=len(groups), chunk=chunk)
            t0 = time.time()
            try:
                out, engine = llm(SYSTEM, prompt)
            except QuotaExhausted:
                raise              # 不是這一節的錯，別記進帳本
            except Exception as e:  # noqa: BLE001
                return None, f"塊 {ci}/{len(groups)}：{e}"
            engines.add(engine)
            out = FENCE_RE.sub("", out).strip()
            if len(plain(out)) < len(plain(chunk)) * 0.7:
                return None, (f"塊 {ci}/{len(groups)} 縮水到 "
                              f"{len(plain(out)):,}／{len(plain(chunk)):,} 字")
            if out.count("<") < 2:
                return None, f"塊 {ci}/{len(groups)} 不像 HTML"
            cf.write_text(out, encoding="utf-8")
            print(f"      · 塊 {ci}/{len(groups)} ✓ {engine} "
                  f"{len(plain(chunk)):,}→{len(plain(out)):,} 字 {time.time() - t0:.0f}s",
                  flush=True)
            time.sleep(4)
        for k, i in enumerate(g):
            blocks[i] = out if k == 0 else ""

    rebuilt = head + "\n".join(b for b in blocks if b) + "</section>"
    if 'data-fable-title' in section and 'data-fable-title' not in rebuilt:
        return None, "章首故事引子掉了"
    if len(plain(rebuilt)) < len(plain(section)) * 0.75:
        return None, (f"整節縮水到 {len(plain(rebuilt)):,}／{len(plain(section)):,} 字")
    return rebuilt, "+".join(sorted(engines)) or "cache"


def rewrite_book(book: str, spec: dict, positions: str, args) -> None:
    path = BOOKS / f"{book}.html"
    if not path.exists():
        print(f"  ✗ 找不到 {path}")
        return

    BACKUP.mkdir(parents=True, exist_ok=True)
    bak = BACKUP / f"{book}.html"
    if not bak.exists():
        shutil.copy2(path, bak)

    done = load_ledger()
    attempted = 0
    # 🚨 本輪已經試過的節要記下來——失敗的節帳本記 ok=False，若只看帳本就會
    #    在同一節上無限重試，整卷永遠走不下去。
    tried_now: set[int] = set()

    while True:
        doc = path.read_text(encoding="utf-8")
        spans = split_chapters(doc)
        todo = None
        for n, (s, e) in enumerate(spans):
            if done.get(f"{book}#{n}", {}).get("ok") or n in tried_now:
                continue
            todo = n
            break
        if todo is None:
            print(f"  · {book} 走完（{len(spans)} 節）")
            return
        if args.limit and attempted >= args.limit:
            return
        attempted += 1
        tried_now.add(todo)

        s, e = spans[todo]
        part = doc[s:e]
        h2 = H2_RE.search(part)
        name = plain(h2.group(1)).strip() if h2 else "（無標題節）"
        print(f"  → {book} [{todo}] {name[:30]}（原 {len(plain(part)):,} 字）", flush=True)

        if args.dry_run:
            head = part[:part.index(">") + 1]
            try:
                blocks = blocks_or_die(part[len(head):-len("</section>")])
                print(f"      [dry-run] {len(blocks)} 區塊 → "
                      f"{len(chunk_blocks(blocks))} 塊，未送出")
            except RuntimeError as ex:
                print(f"      [dry-run] ✗ {ex}")
            continue

        t0 = time.time()
        try:
            rebuilt, info = rewrite_section(book, spec, positions, part, todo, name, args)
        except QuotaExhausted as e:
            print(f"      · {e}；本輪收手，排程下次會續跑", flush=True)
            raise
        rec = {"book": book, "idx": todo, "name": name,
               "at": datetime.now(timezone.utc).isoformat()}
        if rebuilt is None:
            print(f"      ✗ {info}")
            rec.update(ok=False, err=info[:300])
            append_ledger(rec)
            done[f"{book}#{todo}"] = rec
            continue

        path.write_text(doc[:s] + rebuilt + doc[e:], encoding="utf-8")
        rec.update(ok=True, engine=info, chars_before=len(plain(part)),
                   chars_after=len(plain(rebuilt)), secs=round(time.time() - t0, 1))
        append_ledger(rec)
        done[f"{book}#{todo}"] = rec
        print(f"      ✓ {info} · {len(plain(part)):,}→{len(plain(rebuilt)):,} 字 · "
              f"{time.time() - t0:.0f}s", flush=True)


LOCK = WORK / "run.lock"


def take_lock() -> bool:
    """排程每半小時叫一次，重疊會讓同一批 key 被兩個行程同時打。
    🚨 鎖要記 PID：只看時間戳的話，上一輪被砍掉留下的殘骸會把後面每一輪都擋住。"""
    WORK.mkdir(parents=True, exist_ok=True)
    if LOCK.exists():
        try:
            pid = int(LOCK.read_text(encoding="utf-8").strip())
        except (ValueError, OSError):
            pid = -1
        alive = False
        if pid > 0:
            # 🚨 tasklist 的輸出是系統 ANSI codepage（這台是 Big5），
            #    os.popen() 會拿 UTF-8 去解而直接 UnicodeDecodeError，
            #    於是排程每一輪都在這裡崩掉、整批永遠不前進。要自己收 bytes。
            try:
                out = subprocess.run(
                    ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
                    capture_output=True, timeout=30,
                ).stdout.decode("utf-8", "replace")
                alive = str(pid) in out
            except (OSError, subprocess.SubprocessError):
                alive = False
        if alive:
            print(f"另一輪還在跑（pid {pid}），這輪跳過。")
            return False
        print(f"清掉殘骸鎖（pid {pid} 已不在）")
    LOCK.write_text(str(os.getpid()), encoding="utf-8")
    return True


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", help="只跑這一卷（M1/E2/V3…）")
    ap.add_argument("--all", action="store_true", help="十五卷全跑")
    ap.add_argument("--limit", type=int, default=0, help="每卷最多改幾節（0＝不限）")
    ap.add_argument("--dry-run", action="store_true", help="只組 prompt 不送出")
    args = ap.parse_args()

    _load_env()
    global GEMINI_KEYS, NVIDIA_KEYS
    GEMINI_KEYS = _find_keys(("GEMINI_API_KEY", "Gemini_API_Key", "GOOGLE_API_KEY"))
    NVIDIA_KEYS = _find_keys(("NVIDIA_API_KEY", "NVIDIA_API_Key", "NVAPI_KEY"))
    if not args.dry_run and not GEMINI_KEYS:
        sys.exit("找不到 GEMINI_API_KEY，停。")
    print(f"引擎：Gemini {GEMINI_MODEL} × {len(GEMINI_KEYS)} key"
          f"（備援 NVIDIA × {len(NVIDIA_KEYS)}）\n")

    if not args.dry_run and not take_lock():
        return

    positions = (HERE / "positions.md").read_text(encoding="utf-8")
    directives = json.loads((HERE / "directives.json").read_text(encoding="utf-8"))

    order = [b for b in directives if not b.startswith("_")]
    if args.book:
        order = [args.book]
    elif not args.all:
        sys.exit("要嘛 --book <卷>，要嘛 --all。")

    for book in order:
        spec = directives.get(book)
        if not spec:
            print(f"✗ directives.json 沒有 {book}")
            continue
        print(f"【{book}《{spec['title']}》 — {spec['level']}】", flush=True)
        try:
            rewrite_book(book, spec, positions, args)
        except QuotaExhausted:
            break
        print()

    if LOCK.exists():
        LOCK.unlink(missing_ok=True)
    print("本輪結束。")


if __name__ == "__main__":
    main()
