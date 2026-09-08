# -*- coding: utf-8 -*-
"""《諸宗教的對話神學》七卷初稿產生器。

讀 `scripts/data/dialogical_theology_outline.json`（七卷各十二章的綱要，人工編寫），
逐章請 Gemini 寫成 `public/content/works/dialogical-theology/chapters-dN/chNN.html`
的 fragment，再由 `assemble_lecture_books.mjs` 串成 D1…D7.html。

引擎沿用千面上帝那一套（qianmian_llm.ask，七把 Gemini key 輪流 + 退避重試）。

🚨 **初稿一律不掛註釋、不附參考書目**。理由不是省事，是安全：叫模型寫書目，它會
   生出格式完美、出版社與年份俱全、但根本不存在的條目，而這種錯不會報錯，會一路
   安靜長到成書。正文裡提到人名、經典名、學派名沒問題（那是常識層），但凡出版社、
   年份、頁碼、卷期一律禁止。註釋等初稿定稿後，照《神學研究宣言》那套「先策展再
   逐筆核實」的流程另外補。
   輸出若混進 <sup>／footnote／參考資料，本檔會判為不合格並重寫一次。

🚨 每卷第一章不是導論而已，它要立該卷的張力；每章結尾都要回扣。這些寫在 prompt 裡，
   因為模型放著不管就會寫成百科條目式的並排介紹——那正是本書明講不要的東西。

  python -X utf8 scripts/dialogical_theology_write.py                 # 全部（跳過已存在）
  python -X utf8 scripts/dialogical_theology_write.py --volume D3     # 只跑一卷
  python -X utf8 scripts/dialogical_theology_write.py --chapter D3:5  # 只跑一章
  python -X utf8 scripts/dialogical_theology_write.py --force         # 覆寫已存在的
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import qianmian_llm as llm  # noqa: E402

OUTLINE = ROOT / "scripts/data/dialogical_theology_outline.json"
BASE = ROOT / "public/content/works/dialogical-theology"
# 免費層是每天每把 key 幾次在管；2.5-flash 是額度撐得起整夜批次的那一檔
MODEL = "gemini-2.5-flash"
MIN_CHARS = 2500          # 低於此才判為根本沒寫完、值得整章重來
MIN_KEEP = 6000           # 加厚兩輪後仍不到這個數才算失敗
EXPAND_BELOW = 8200       # 不到這個數就送進加厚（不重寫，保留既有論證）
TARGET = "九千到一萬一千字"

# 已由人手寫成、當作全書文風基準的那一章；節錄前段餵給模型當範例
STYLE_REF = BASE / "chapters-d1/ch01.html"

BANNED = re.compile(r"<sup|footnote|參考資料|參考書目|註釋", re.I)

# 🚨 七把 Gemini key 撐不完 84 章。2026-09-06 實測跑到第 41 章時全數 429，而且
#    qianmian_llm.ask 是直接拋例外——整場就這樣停在半路。所以這裡自備兩層備援，
#    並且讓單章失敗只算那一章失敗，絕不中斷整場（跑一整晚的東西不能一顆石頭絆倒）。
NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
OR_URL = "https://openrouter.ai/api/v1/chat/completions"
OR_MODEL = "google/gemma-4-26b-a4b-it:free"


def _keys(prefix: str) -> list[str]:
    import os
    return [os.environ[f"{prefix}{i}"] for i in range(1, 9)
            if os.environ.get(f"{prefix}{i}")]


# 🚨 每次都從 keys[0] 打起，平行跑的時候所有 worker 會擠在同一把 key 上，
#    等於七把 key 只用得到一把。用一個全域計數器讓起點輪流。
_rr_lock = __import__("threading").Lock()
_rr = 0


def _openai_style(url: str, keys: list[str], model: str, prompt: str) -> str:
    """NVIDIA NIM 與 OpenRouter 都是 OpenAI 相容介面，同一支打完。"""
    global _rr
    import requests
    body = {"model": model, "temperature": 0.85, "max_tokens": 16000,
            "messages": [{"role": "user", "content": prompt}]}
    last = "?"
    with _rr_lock:
        _rr += 1
        start = _rr
    for i in range(len(keys)):
        key = keys[(start + i) % len(keys)]
        try:
            r = requests.post(url, headers={"Authorization": f"Bearer {key}"},
                              json=body, timeout=600)
        except Exception as e:                       # noqa: BLE001
            last = f"conn {type(e).__name__}"
            continue
        if r.status_code != 200:
            last = f"HTTP {r.status_code}"
            continue
        try:
            txt = r.json()["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            last = "回應沒有 content"
            continue
        if txt and txt.strip():
            return re.sub(r"<think>.*?</think>", "", txt, flags=re.S).strip()
        last = "空回應"
    raise RuntimeError(f"{len(keys)} 把 key 全失敗，最後：{last}")


def ask_any(prompt: str) -> tuple[str, str]:
    """Gemini → NVIDIA → OpenRouter，先成功先回。回 (文字, 用了哪個引擎)。"""
    import translate_ebook_to_zh as engines
    try:
        text, _ = llm.ask(prompt, model=MODEL, temperature=0.85, max_tokens=32768)
        return text, "gemini"
    except Exception as e:                           # noqa: BLE001
        print(f"      ⚠ Gemini 不通（{str(e)[:60]}），改走 NVIDIA", flush=True)
    try:
        return _openai_style(NVIDIA_URL, engines.NVIDIA_KEYS,
                             engines.NVIDIA_MODELS[0], prompt), "nvidia"
    except Exception as e:                           # noqa: BLE001
        print(f"      ⚠ NVIDIA 不通（{str(e)[:60]}），改走 OpenRouter", flush=True)
    return _openai_style(OR_URL, _keys("OPENROUTER_API_Key_"), OR_MODEL, prompt), "openrouter"


def style_sample() -> str:
    if not STYLE_REF.exists():
        return ""
    raw = STYLE_REF.read_text(encoding="utf-8")
    body = re.sub(r"<sup class=\"footnote-ref\".*?</sup>", "", raw, flags=re.S)
    return body[:2600]


def build_prompt(book, vol, ch, sample) -> str:
    sibling = "、".join(f"第{c['n']}章{c['title']}" for c in vol["chapters"])
    # 🚨 不把七卷全名寫進 prompt，模型就會自己發明——實測它把卷一叫成《終極實在論》。
    volumes = "、".join(f"卷{v['no']}《{v['title']}》（{v['tension']}）" for v in book["volumes"])
    return f"""你是《{book['book']}》的作者，一位台灣的宗教學者。現在要寫**卷{vol['no']}《{vol['title']}》第{ch['n']}章〈{ch['title']}〉**的初稿。

## 這套書是什麼
把基督教系統神學的科目分類，改寫成一套跨宗教的對話神學，共七卷，每卷由一組彼此對立的主題撐開。

**七卷是**：{volumes}。（卷名務必照這個寫，不要自己改名或發明別的卷名。）

**本卷**：卷{vol['no']}《{vol['title']}》，張力是「{vol['tension']}」。{vol['maps']}。
**本卷主張**：{vol['thesis']}

## 三個原則
{chr(10).join('- ' + p for p in book['principles'])}

## 方法（這幾條決定文章的體質，違反了就是寫壞了）
{chr(10).join('- ' + m for m in book['method'])}

## 本章要寫什麼
第{ch['n']}章〈{ch['title']}〉
{ch['brief']}

本卷各章：{sibling}
（其他章各有分工，本章不要越界去寫別章的主題，必要時可以一句話交叉指涉。）

## 文風範例（只學它的語氣、節奏與論證方式，**不要沿用它的例子**）
{sample}

🚨 上面那段是卷一第一章的開頭。**它舉的台灣家庭餐桌、母親禱告、父親拜天公那組例子已經用過了，
本章絕對不要再用**，請自己另找一個具體的切入點。

## 硬性規定
1. **繁體中文**，台灣用語。中文標點。專有名詞第一次出現可括號附原文。
2. **輸出純 HTML 片段**，格式固定為：
   `<section class="chapter"><h2>第{ch['n']}章　{ch['title']}</h2>` 開頭，`</section>` 結尾。
   內文用 `<p>` 段落，分節用 `<h3>一、小節名</h3>`（中文數字），全章分 5 到 8 節，最後一節是〈結語〉。
   強調用 `<strong>`，外文與書名用 `<em>`。不要 markdown，不要 ``` 圍欄。
3. **長度 {TARGET}**（不含標籤）。這是初稿，寧可厚一點。
4. 🚨 **絕對不要寫註釋、上標註號、參考資料或參考書目**。正文裡提到人名、經典名、學派名、
   概念名沒問題，但**不得寫出版社、出版年份、頁碼、期刊卷期**，也不要說「見某某書第幾頁」。
   凡是你不確定的具體年代、數字或引文原文，改用概括的說法，或者乾脆不寫。
   寧可少一個例子，也不要生一個看起來很像真的但其實是編的細節。
5. **開頭不要用「本章將討論……」這種空話**。用一個具體的場景、一個實例、或一個尖銳的問題起手，
   像文風範例那樣。
5b. **不要用第二人稱「你」**，不要寫「你會發現」「我們可以說」「想像一下」「值得注意的是」
   這類填充語。要直接陳述。也不要在段落開頭反覆用同一個連接詞。
5c. **每一節至少一千二百字**，全章五到八節。單薄的節寧可併掉，不要為了湊節數而寫空話。
6. **不要寫成百科條目的並排介紹**（「基督教認為……佛教認為……伊斯蘭認為……」）。
   要論證：呈現張力、指出各家為什麼往不同方向走、指出同一條張力如何存在於各傳統**內部**。
7. **結尾要回扣本卷的張力與主張**，並且可以用一句話帶到下一章。
8. 不要做萬教合一，不要說「其實各家講的是同一件事」。相似之處要指出來，但立刻要問
   「這個相似是真的相同，還是我們的分類太粗糙」。

現在直接輸出那個 HTML 片段，不要任何前言或說明。"""


def head_html(vol) -> str:
    chs = vol["chapters"]
    toc = "／".join(f"{c['n']}.{c['title']}" for c in chs)
    return (
        f'<header class="book-head"><p class="book-kicker">諸宗教的對話神學‧卷{vol["no"]}</p>'
        f'<h1 class="book-title">{vol["title"]}</h1>'
        f'<p class="book-sub">{vol["tension"]}的張力</p>'
        f'<p class="book-thesis">{vol["maps"]}。<br /><br />{vol["thesis"]}<br /><br />'
        f'全卷十二章：{toc}。<br /><br />'
        f'本卷不做裁決，也不做整合。對話性神學與整合性神學的差別在於：整合性會說「兩者結構相似，'
        f'可見相容」；對話性則會問「這個相似究竟意味著本來就只有這幾種模式，還是意味著我們的分類'
        f'太粗糙」。呈現張力，不消解張力。</p>'
        f'<p class="book-meta">張辰瑋　　本卷為寫作中的初稿，線上版隨寫作進度修訂。</p></header>\n'
    )


def clean(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    i = t.find("<section")
    if i > 0:
        t = t[i:]
    j = t.rfind("</section>")
    if j >= 0:
        t = t[: j + len("</section>")]
    return t.strip()


def body_chars(html: str) -> int:
    return len(re.sub(r"\s", "", re.sub(r"<[^>]+>", "", html)))


def write_chapter(book, vol, ch, sample, force: bool) -> str:
    d = BASE / f"chapters-{vol['id'].lower()}"
    d.mkdir(parents=True, exist_ok=True)
    out = d / f"ch{ch['n']:02d}.html"
    if ch.get("skip"):
        return "跳過（人手寫成）"
    if out.exists() and not force:
        return "已存在"

    prompt = build_prompt(book, vol, ch, sample)
    html = None
    for attempt in (1, 2):
        text, eng = ask_any(prompt if attempt == 1 else prompt + _RETRY_NOTE)
        cand = clean(text)
        n = body_chars(cand)
        bad = BANNED.search(cand)
        if not cand.startswith("<section"):
            reason = "開頭不是 <section>"
        elif bad:
            reason = f"混進了禁止的元素：{bad.group(0)}"
        elif n < MIN_CHARS:
            reason = f"只有 {n} 字，太短"
        else:
            html = cand
            break
        if attempt == 1:
            print(f"      ↻ 重寫（{reason}）", flush=True)
    if html is None:
        return f"✗ 兩次都不合格（{reason}）"

    # 🚨 一次成稿的長度看引擎：Gemini 多半六到八千，NVIDIA 常常只有三到五千。
    #    早期版本把「不足六千」判退重寫，結果 NVIDIA 那一輪 25 章失敗 17 章——
    #    重寫出來的還是短稿，而加厚這道有效的手段反而只對「已經夠長」的稿子開放。
    #    現在改成：短稿不丟，直接送進加厚，最多兩輪。加厚實測能把 4,000 拉到 9,000 以上。
    n = body_chars(html)
    for rnd in (1, 2):
        if n >= EXPAND_BELOW:
            break
        print(f"      ＋ 加厚第{rnd}輪（現有 {n} 字）", flush=True)
        try:
            text, _ = ask_any(_expand_prompt(html, n))
            cand = clean(text)
            m = body_chars(cand)
            # 加厚失敗（變短、跑掉格式、混進禁止元素）就保留原稿，不要越改越糟
            if cand.startswith("<section") and not BANNED.search(cand) and m > n:
                html, n = cand, m
            else:
                print("      ！ 加厚無效，保留原稿", flush=True)
                break
        except Exception as e:                      # noqa: BLE001
            print(f"      ！ 加厚失敗（{type(e).__name__}），保留原稿", flush=True)
            break

    if n < MIN_KEEP:
        return f"✗ 加厚後仍只有 {n} 字"
    out.write_text(html + "\n", encoding="utf-8")
    return f"✓ {n} 字"


def _expand_prompt(html: str, n: int) -> str:
    return f"""下面是一章書稿的初稿，目前約 {n} 字，**偏薄**。請把它加厚到 {TARGET}。

## 加厚的方式
- **保留現有的結構、論點與小節標題**，不要換題目、不要重寫成另一篇。
- 在既有論證上補：更具體的歷史case、各傳統**內部**的爭論、反例與難處、
  以及「這種說法配的是哪一種人」的追問。
- 把過於概括的斷言寫實：與其說「各傳統對此有不同看法」，不如指名道姓說出是哪幾家、
  分歧在哪一點。
- 刪掉空話與填充語（「你會發現」「值得注意的是」「我們可以說」「想像一下」），
  刪掉的字數用實質內容補回來。

## 硬性規定（與原稿相同）
- 繁體中文、台灣用語。
- 純 HTML 片段，`<section class="chapter">` 開頭、`</section>` 結尾，`<h3>` 分節，`<p>` 段落。
- 🚨 **不要註釋、不要上標、不要參考資料或參考書目**；不得寫出版社、年份、頁碼、卷期。
  不確定的具體年代數字寧可不寫。
- 不用第二人稱「你」。

直接輸出加厚後的完整 HTML 片段，不要任何說明。

---

{html}"""


_RETRY_NOTE = """

## 重寫提醒
上一次的輸出不合格。請務必：以 `<section class="chapter">` 開頭、`</section>` 結尾；
**絕對不要有 <sup>、註釋、參考資料、參考書目**；長度要夠（至少六千字，目標九千以上）。直接輸出 HTML，不要說明。"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--volume", help="只跑某一卷，如 D3")
    ap.add_argument("--chapter", help="只跑某一章，如 D3:5")
    ap.add_argument("--force", action="store_true", help="覆寫已存在的章")
    ap.add_argument("--workers", type=int, default=4,
                    help="並行條數（預設 4）。Gemini 掛掉只剩 NVIDIA 時，"
                         "單章要二十幾分鐘，序列跑一天寫不完十章")
    a = ap.parse_args()

    # 🚨 單一實例鎖。排程每半小時醒來一次，而一輪要跑好幾個小時；沒有鎖的話
    #    第二個實例會挑到同一批「還沒寫」的章，兩邊各寫各的、白燒一份額度。
    #    不用查 PID 是否存活（那條路踩過 Big5 解碼的坑），改看鎖檔多久沒更新。
    lock = ROOT / "output" / "dialogical_write.lock"
    lock.parent.mkdir(parents=True, exist_ok=True)
    if lock.exists() and time.time() - lock.stat().st_mtime < 3600:
        print(f"另一個實例還在跑（{lock.name} 於 "
              f"{time.strftime('%H:%M', time.localtime(lock.stat().st_mtime))} 更新過），本次跳過")
        return
    lock.write_text(str(time.time()), encoding="utf-8")

    book = json.loads(OUTLINE.read_text(encoding="utf-8"))
    sample = style_sample()
    only_v, only_c = None, None
    if a.chapter:
        only_v, only_c = a.chapter.split(":")
        only_c = int(only_c)
    elif a.volume:
        only_v = a.volume

    # 先把待寫的章排出來（順便把各卷書頭補上），再決定要不要平行跑。
    pending = []
    for vol in book["volumes"]:
        if only_v and vol["id"] != only_v:
            continue
        d = BASE / f"chapters-{vol['id'].lower()}"
        d.mkdir(parents=True, exist_ok=True)
        head = d / "_head.html"
        if not head.exists() or a.force:
            # 卷一的書頭是人手寫的，不要被覆蓋
            if vol["id"] != "D1" or not head.exists():
                head.write_text(head_html(vol), encoding="utf-8")
        for ch in vol["chapters"]:
            if only_c and ch["n"] != only_c:
                continue
            if ch.get("skip"):
                continue
            if (d / f"ch{ch['n']:02d}.html").exists() and not a.force:
                continue
            pending.append((vol, ch))

    print(f"待寫 {len(pending)} 章，{a.workers} 條線並行", flush=True)

    def run(item):
        vol, ch = item
        t0 = time.time()
        try:
            r = write_chapter(book, vol, ch, sample, a.force)
        except Exception as e:                       # noqa: BLE001
            # 跑一整晚的東西不能被一顆石頭絆倒：記下來，換下一章
            r = f"✗ 例外：{type(e).__name__} {str(e)[:70]}"
        return (f"  {vol['id']} 第{ch['n']:2d}章 {ch['title'][:24]:24s} {r}"
                f"　{time.time()-t0:.0f}s"), r

    done = fail = 0
    if a.workers <= 1:
        results = (run(it) for it in pending)
    else:
        # 各章之間沒有相依，天生可平行；瓶頸是 API 端，不是本機。
        from concurrent.futures import ThreadPoolExecutor
        pool = ThreadPoolExecutor(max_workers=a.workers)
        results = pool.map(run, pending)
    for line, r in results:
        print(line, flush=True)
        lock.write_text(str(time.time()), encoding="utf-8")   # 心跳，免得長跑被判成殭屍
        if r.startswith("✓"):
            done += 1
        elif r.startswith("✗"):
            fail += 1
    lock.unlink(missing_ok=True)
    print(f"\n完成 {done} 章，失敗 {fail} 章")


if __name__ == "__main__":
    main()
