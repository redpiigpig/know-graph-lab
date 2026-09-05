# -*- coding: utf-8 -*-
"""千面上帝：用 Gemini 把素材寫成全書正文。

一章跑三種呼叫，而且**刻意用三個不同型號**——免費層是每個型號各自 20 次/天/key，
分流之後正文那一層才吃得到完整的額度（見 qianmian_llm 的註解）：

  1. 分配（MODEL_ALLOC）  只餵書摘標題，把條目分派到各節
  2. 寫作（MODEL）        一章兩次：前半＋導言、後半＋結語
  3. 校對（MODEL_POLISH） 每次寫作之後接一道，只改錯字病句

寫作不逐節呼叫的原因有兩個：逐節要 ~15 次/章，排不進日額度；而且同一次生成
裡的節與節之間銜接得比較自然。代價是模型會壓縮篇幅，所以 prompt 要把「每節
都要寫足」講死，--length 也要開得比實際目標高。

註釋：模型只准標 〔註:E12〕〔註:R3〕這種指回素材編號的記號，不准自己寫參考書目。
腳本再把編號換成頁下註的流水號，註文由 qianmian_cite 依 DB 書目補成正式體例。
這樣註釋不可能是掰出來的——編號對不上的一律丟掉並回報。

可重跑：已經有 output/qianmian/chapters/chNN.md 的章直接跳過。
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qianmian_llm as L          # noqa: E402
from qianmian_cite import Citer   # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "output" / "qianmian"
SRC, PLAN, OUT = BASE / "sources", BASE / "plan", BASE / "chapters"
# 研究筆記是「刪掉重跑長不回來、而且是下一步的輸入」，所以進版控而不是 output/
RES = ROOT / "data" / "qianmian" / "research"

VOICE = """【全書旨趣】
《千面上帝》是一部七卷本的世界宗教通史。它把人類宗教史當成「史上最大型的故事接力賽」來寫：
不同宗教看似壁壘分明，其實神話、儀式與觀念不斷跨界流動，換一副面貌在另一個傳統裡重新出現。
書名的意思是——人類在不同時代、不同文明裡所看見的，可能是同一位上帝的不同面孔，
可能是諸神，甚至可能沒有神。作者不護教、不貶抑任何一方，以史家的同情理解落筆。

【文風要求】
- 繁體中文，台灣讀者的用語習慣。中間點一律用「‧」。
- 通俗史筆：可讀性優先，像《人類大歷史》《神的歷史》那樣講故事，不是教科書條列。
- 從具體的人、物、地點或場景切入，再把論點帶出來。禁用「首先／其次／再者／總之」。
- 不下小標、不用條列符號、不用 markdown 記號。整段是連貫散文。
- 專有名詞第一次出現時附原文或年代。譯名一律沿用素材裡既有的譯法，不要自創。
- 禁止出現「本節」「本章」「筆者」「我們可以看到」「值得注意的是」這類論文腔與過渡廢話。
- 收尾落在一個具體畫面或一句有重量的判斷上，不要堆金句、不要喊口號。
- 不要在正文裡提到本書書名，也不要用「接力賽」這個比喻——那是全書的構想，不是正文的說法。
- 用字與成語必須正確。錯一個字，整段的可信度就沒了。"""

NOTE_RULE = """【註釋規則】
- 引用具體說法、數據、斷代、他人論斷之處，在該句句末標 〔註:E12〕 或 〔註:R3〕。
- 全節註釋 6 至 10 個，最多 10 個。這是硬上限，寧可少也不要多。
- 只挑最需要交代出處的地方標；一般的敘述、過渡、描寫一律不標。
- 合法編號只有以下這些，一個都不准自創：
  {legal}"""

ALLOC = """以下是一部宗教通史其中一章的節次，以及手上所有的書摘（只列標題）。
請把每一條書摘分派給最合適的一節；一條只能進一節，與任何一節都無關的放進「棄用」。

【章】第{no}章　{title}：{span}（{period}）
【節次】
{sections}

【書摘】
{topics}

輸出 JSON：{{"1":["E1","E5"],"2":["E2"],…,"棄用":["E9"]}}　只輸出 JSON。"""

WRITE = """你正在替一部七卷本的宗教通史《千面上帝》寫其中一章的一部分。

{voice}

【位置】
{volume}
第{no}章　{title}：{span}（{period}）

【本章完整節次】（給你掌握全章走向，這一次只寫下面指定的部分）
{all_sections}

【這一次要寫的】
{tasks}

【素材一：書摘】（按節分好了，寫作時只能引用這些，編號要對）
{excerpts}

【素材二：近年研究】
{research}

【素材三：作者本人在讀書會上的講法】（用來抓觀點、判斷與關懷所在；口語不要照抄，也不能當註釋來源）
{talk}

{note_rule}

【輸出格式】
每一部分之前用 `## 標題` 標出它是哪一節，標題必須與上面給的**一字不差**。
導言寫 `## 導言`，結語寫 `## 結語`。除了這些 `##` 標題，全文不要有任何其他標記。

【篇幅與素材覆蓋】這一次要交 {count} 段。每一節寫 {length} 字，導言約 800 字、結語約 600 字。
**每一節分到的書摘都要用上**——那些材料是作者多年讀書累積下來的，只挑三五條敷衍
就等於把整章的厚度丟掉。寧可整體長，也不要每節都只寫個大概。

直接輸出正文，不要任何說明。"""

INTRO_ASK = """導言：用一個具體的場景、器物或人物開場，把讀者帶進這個時代，點出這一章要處理的
核心問題，並讓讀者感覺到這一章和前一章的世界是連著的。不要預告「本章將討論」，不要條列各節。"""

OUTRO_ASK = """結語：收束整章的線索，指出這個時代留給後世的東西，並把讀者的目光帶向下一個時代。
不要摘要各節，不要用「綜上所述」。"""


def meta(ch):
    """只留樣板要用的欄位——直接 **ch 會和 sections/excerpts/research 這些關鍵字撞名。"""
    return {k: ch[k] for k in ("no", "volume", "title", "span", "period")}


def load(no):
    ch = json.loads((SRC / f"ch{no:02d}.json").read_text(encoding="utf-8"))
    rf = RES / f"ch{no:02d}.json"
    ch["research"] = json.loads(rf.read_text(encoding="utf-8")) if rf.exists() else []
    return ch


def allocate(ch):
    PLAN.mkdir(parents=True, exist_ok=True)
    f = PLAN / f"ch{ch['no']:02d}.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    if not ch["excerpts"]:
        f.write_text("{}", encoding="utf-8")
        return {}
    secs = "\n".join(f"{i}. {s}" for i, s in enumerate(ch["sections"], 1))
    topics = "\n".join(f"E{i} {e['topic'] or e['text'][:24]}"
                       for i, e in enumerate(ch["excerpts"], 1))
    prompt = ALLOC.format(sections=secs, topics=topics, **meta(ch))
    for attempt in range(3):
        try:
            plan = L.ask_json(prompt, model=L.MODEL_ALLOC, temperature=0.2, max_tokens=65536)
            break
        except (ValueError, TypeError) as e:     # JSON 被截斷或格式跑掉
            print(f"    分配第 {attempt + 1} 次解析失敗（{e}），重試", flush=True)
    else:
        # 三次都不成就平均分，寧可分配得笨一點，也不要整章寫不出來
        n = len(ch["sections"])
        plan = {str(i + 1): [f"E{j + 1}" for j in range(len(ch["excerpts"])) if j % n == i]
                for i in range(n)}
        print("    ⚠ 分配失敗三次，改用平均分配", flush=True)
    f.write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    return plan


def ids_of(plan, i):
    """第 i 節分到的書摘編號（1-based）。"""
    out = []
    for eid in plan.get(str(i)) or plan.get(f"第{i}節") or []:
        m = re.fullmatch(r"E(\d+)", str(eid).strip())
        if m:
            out.append(int(m.group(1)))
    return out


def block_excerpts(ch, sections, plan):
    """把這一批節各自分到的書摘，按節標出來——不分節餵，模型會把材料全倒進第一節。"""
    out = []
    for i, name in sections:
        rows = []
        for n in ids_of(plan, i):
            if not 1 <= n <= len(ch["excerpts"]):
                continue
            e = ch["excerpts"][n - 1]
            rows.append(f"[E{n}]（{e['topic']}｜出處：{e['source'] or '未註明'}）\n{e['text']}")
        out.append(f"〔{name}〕\n" + ("\n\n".join(rows) if rows
                                    else "（這一節沒有書摘，請依綱要與近年研究撰寫，註釋只用 R 編號）"))
    return "\n\n".join(out)


def block_research(ch):
    if not ch["research"]:
        return "（無）"
    return "\n".join(
        f"[{r.get('id')}] {r.get('主題', '')}｜新見：{r.get('新見', '')}"
        f"｜舊說：{r.get('舊說', '')}｜依據：{r.get('依據', '')}" for r in ch["research"])


def block_talk(ch, limit=6000):
    t = "\n".join(x["text"] for x in ch["transcripts"])
    return (t[:limit] + "…") if t else "（本章沒有讀書會錄音）"


def cite_of(tag, ch, citer):
    """一個素材編號 → 一條註文。查不到回 None。"""
    tag = tag.upper()
    if tag.startswith("E"):
        i = int(tag[1:])
        if 1 <= i <= len(ch["excerpts"]):
            return citer.format(ch["excerpts"][i - 1]["source"])
        return None
    for r in ch["research"]:
        if str(r.get("id", "")).upper() == tag:
            return (r.get("依據") or "").rstrip(" .。") + "。"
    return None


# 模型常把幾個來源塞進同一個記號：〔註:E92, E107〕。一個記號＝一條註，
# 裡面的來源用「；」併起來，不要拆成兩個註號黏在一起。
NOTE_MARK = re.compile(r"〔註[:：]\s*([ERer]\s*\d+(?:\s*[,，、]\s*[ERer]\s*\d+)*)\s*〕")


def resolve_notes(text, ch, citer, counter, notes, cap=10):
    """把 〔註:E12〕〔註:R3, E40〕換成頁下註流水號，並累積註文。"""
    dropped, used = [], [0]

    def sub(m):
        tags = [re.sub(r"\s+", "", t) for t in re.split(r"[,，、]", m.group(1))]
        if used[0] >= cap:          # 超過上限的一律拿掉，不進註釋
            return ""
        bodies = []
        for t in tags:
            body = cite_of(t, ch, citer)
            if body:
                bodies.append(body.rstrip("。"))
            else:
                dropped.append(t)
        if not bodies:
            return ""
        used[0] += 1
        counter[0] += 1
        notes.append((counter[0], "；".join(bodies) + "。"))
        return f"[^{counter[0]}]"

    return NOTE_MARK.sub(sub, text), dropped


POLISH = """以下是一部宗教通史其中一章的定稿正文。請只做校對，不要改寫。

要改的：錯別字、成語誤用、贅字、語序不順、明顯的病句、簡體字。
不准動的：內容、論點、段落數、`## 開頭的小標`（一字都不能改）、
　　　　　以及任何 〔註:E12〕〔註:R3〕 形式的註釋記號（位置與編號都要原樣保留）。
不要加標題、不要加說明。

直接輸出校對後的全文。

---
{text}"""

# 校對時要原樣留住的東西：註釋記號與小標。少一個就退回原稿。
GUARDS = (NOTE_MARK, re.compile(r"(?m)^##.*$"))


def polish(text):
    """校對一遍。註釋記號或小標對不上就整段退回原稿——寧可有錯字，不能掉註、掉節。"""
    before = [g.findall(text) for g in GUARDS]
    try:
        out, _ = L.ask(POLISH.replace("{text}", text), model=L.MODEL_POLISH,
                       temperature=0.2, max_tokens=65536)
    except Exception as e:
        print(f"    ⚠ 校對失敗，保留原稿：{e}", flush=True)
        return text
    out = out.strip()
    if [g.findall(out) for g in GUARDS] != before or len(out) < len(text) * 0.85:
        print("    ⚠ 校對後註釋記號、小標或篇幅對不上，保留原稿", flush=True)
        return text
    return out


def split_output(text, wanted):
    """把 `## 標題` 分段的輸出拆回 {標題: 內文}，標題比對容忍空白與全半形差異。"""
    key = lambda s: re.sub(r"[\s　]+", "", s)
    index = {key(w): w for w in wanted}
    out, cur = {}, None
    for line in text.splitlines():
        t = line.strip()
        if t.startswith("##"):
            cur = index.get(key(t.lstrip("#")))
            if cur:
                out[cur] = []
            continue
        if cur and t:
            out[cur].append(t)
    return {k: "\n".join(v) for k, v in out.items() if v}


def write_chapter(no, length):
    ch = load(no)
    dest = OUT / f"ch{no:02d}.md"
    if dest.exists():
        print(f"  第{no}章 已有，跳過")
        return
    plan = allocate(ch)
    citer, counter, notes, dropped = Citer(), [0], [], []
    secs = ch["sections"]
    # 一次最多兩節。一次寫四節以上模型就開始壓縮（七節一次只給 10,900 字、
    # 四節一次 12,900 字），兩節一次才寫得到每節三千字。
    groups = [list(enumerate(secs, 1))[i:i + 2] for i in range(0, len(secs), 2)]
    parts = [(g, i == 0, i == len(groups) - 1) for i, g in enumerate(groups)]

    pieces = {}
    for sections, with_intro, with_outro in parts:
        wanted = (["導言"] if with_intro else []) + [n for _, n in sections] \
            + (["結語"] if with_outro else [])
        tasks = "\n".join(
            (["## 導言\n" + INTRO_ASK] if with_intro else [])
            + [f"## {n}" for _, n in sections]
            + (["## 結語\n" + OUTRO_ASK] if with_outro else []))
        legal = "、".join([f"E{n}" for i, _ in sections for n in ids_of(plan, i)]
                         + [str(r.get("id")) for r in ch["research"]]) or "（無，這一段不標註釋）"
        prompt = WRITE.format(
            voice=VOICE, note_rule=NOTE_RULE.format(legal=legal),
            all_sections="\n".join(f"{i}. {n}" for i, n in enumerate(secs, 1)),
            tasks=tasks, count=len(wanted), excerpts=block_excerpts(ch, sections, plan),
            research=block_research(ch), talk=block_talk(ch), length=length, **meta(ch))
        # 整批沒回來是會發生的（模型偶爾回空、或標題全走樣）。只印警告就落檔的話，
        # 檔案看起來很正常、其實少了半章——第 2 章連續兩次栽在這裡。重試到齊為止。
        got = {}
        for attempt in range(3):
            text, _ = L.ask(prompt, temperature=0.85, max_tokens=65536)
            got = split_output(polish(text.strip()), wanted)
            missing = [w for w in wanted if w not in got]
            if not missing:
                break
            print(f"    ⚠ 第 {attempt + 1} 次少了 {len(missing)} 段：{missing}，重試", flush=True)
        if missing:
            raise RuntimeError(f"這一批三次都缺 {missing}，整章不落檔，留待重跑")
        for w in wanted:
            if w in got:
                body, drop = resolve_notes(got[w], ch, citer, counter, notes,
                                           cap=12 if w in ("導言", "結語") else 10)
                pieces[w] = body
                dropped += drop
        print(f"    寫完 {len(got)}/{len(wanted)} 段，累計註 {counter[0]}", flush=True)

    if not pieces:
        raise RuntimeError("整章都沒寫出來")

    OUT.mkdir(parents=True, exist_ok=True)
    md = [f"# 第{no}章　{ch['title']}", f"### {ch['span']}（{ch['period']}）", "",
          f"<!-- {ch['volume']} -->", ""]
    if "導言" in pieces:
        md += [pieces["導言"], ""]
    for name in secs:
        if name in pieces:
            md += [f"## {name}", "", pieces[name], ""]
    if "結語" in pieces:
        md += ["## 結語", "", pieces["結語"], ""]
    md += ["---", ""] + [f"[^{n}]: {t}" for n, t in notes]
    dest.write_text("\n".join(md), encoding="utf-8")

    total = sum(len(v) for v in pieces.values())
    print(f"  ✓ 第{no}章 {ch['title']}：{total} 字、{len(notes)} 個頁下註"
          + (f"，丟棄無效註號 {len(dropped)}" if dropped else ""), flush=True)
    if citer.misses:
        f = BASE / "missing_books.txt"
        had = set(f.read_text(encoding="utf-8").splitlines()) if f.exists() else set()
        f.write_text("\n".join(sorted(had | citer.misses)), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapters", default="1-28", help="例 1-28 或 3,5,9")
    ap.add_argument("--length", default="3500–4000")   # 模型一律寫不到要求，開高才落在三千上下
    a = ap.parse_args()
    nos = []
    for part in a.chapters.split(","):
        if "-" in part:
            s, e = part.split("-")
            nos += list(range(int(s), int(e) + 1))
        else:
            nos.append(int(part))
    for no in nos:
        try:
            write_chapter(no, a.length)
        except Exception as e:
            print(f"  ✗ 第{no}章：{type(e).__name__} {e}", flush=True)


if __name__ == "__main__":
    main()
