# -*- coding: utf-8 -*-
"""千面上帝：用 Gemini 逐節寫出全書正文。

一章分三步：
  1. 分配 ── 把該章的書摘按標題分派到各節（只餵標題，省 token 也比較準）
  2. 寫作 ── 逐節寫，只餵該節分到的書摘全文＋近年研究＋作者讀書會講法
  3. 收尾 ── 章導言與章結語

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

WRITE = """你正在替一部七卷本的宗教通史《千面上帝》寫其中一節。

{voice}

【位置】
{volume}
第{no}章　{title}：{span}（{period}）
本節是全章第 {i}／{n} 節：{section}
上一節：{prev}
下一節：{next}

【素材一：書摘】（寫作時只能引用這些，編號要對）
{excerpts}

【素材二：近年研究】
{research}

【素材三：作者本人在讀書會上的講法】（用來抓觀點、判斷與關懷所在；口語不要照抄，也不能當註釋來源）
{talk}

{note_rule}

【篇幅】{length} 字。

直接輸出正文，不要標題、不要任何說明。"""

FRAME = """你正在替一部七卷本的宗教通史《千面上帝》寫第{no}章的{kind}。

{voice}

【位置】{volume}　第{no}章　{title}：{span}（{period}）
【本章各節依序是】
{sections}
【本章正文的開頭與結尾】
{peek}

{ask}

【篇幅】{length} 字。直接輸出正文，不要標題、不要說明。"""

INTRO_ASK = """請寫一段導言：用一個具體的場景、器物或人物開場，把讀者帶進這個時代，
點出本章要處理的核心問題，並且要讓讀者感覺到這一章和前一章的世界是連著的。
不要預告「本章將討論」，不要條列各節內容。"""

OUTRO_ASK = """請寫一段結語：收束本章的線索，指出這個時代留給後世的東西，
並且把讀者的目光帶向下一個時代。不要摘要各節，不要用「綜上所述」。"""


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
            plan = L.ask_json(prompt, temperature=0.2, max_tokens=65536)
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


def block_excerpts(ch, ids):
    out = []
    for eid in ids:
        m = re.fullmatch(r"E(\d+)", str(eid).strip())
        if not m:
            continue
        i = int(m.group(1))
        if not 1 <= i <= len(ch["excerpts"]):
            continue
        e = ch["excerpts"][i - 1]
        out.append(f"[E{i}]（{e['topic']}｜出處：{e['source'] or '未註明'}）\n{e['text']}")
    return "\n\n".join(out) or "（本節無指定書摘，請依綱要與近年研究撰寫，註釋只用 R 編號）"


def block_research(ch):
    if not ch["research"]:
        return "（無）"
    return "\n".join(
        f"[{r.get('id')}] {r.get('主題', '')}｜新見：{r.get('新見', '')}"
        f"｜舊說：{r.get('舊說', '')}｜依據：{r.get('依據', '')}" for r in ch["research"])


def block_talk(ch, limit=6000):
    t = "\n".join(x["text"] for x in ch["transcripts"])
    return (t[:limit] + "…") if t else "（本章沒有讀書會錄音）"


def resolve_notes(text, ch, citer, counter, notes, cap=10):
    """把 〔註:E12〕〔註:R3〕換成頁下註流水號，並累積註文。"""
    dropped, used = [], [0]

    def sub(m):
        tag = re.sub(r"\s+", "", m.group(1)).upper()
        if used[0] >= cap:          # 超過上限的一律拿掉，不進註釋
            return ""
        used[0] += 1
        body = None
        if tag.startswith("E"):
            i = int(tag[1:])
            if 1 <= i <= len(ch["excerpts"]):
                body = citer.format(ch["excerpts"][i - 1]["source"])
        else:
            for r in ch["research"]:
                if str(r.get("id", "")).upper() == tag:
                    body = (r.get("依據") or "").rstrip(" .。") + "。"
                    break
        if not body:
            dropped.append(tag)
            return ""
        counter[0] += 1
        notes.append((counter[0], body))
        return f"[^{counter[0]}]"

    return re.sub(r"〔註[:：]\s*([ERer]\s*\d+)\s*〕", sub, text), dropped


POLISH = """以下是一部宗教通史其中一章的定稿正文。請只做校對，不要改寫。

要改的：錯別字、成語誤用、贅字、語序不順、明顯的病句、簡體字。
不准動的：內容、論點、段落數、任何 [^數字] 形式的註釋記號（位置與數字都要原樣保留）。
不要加標題、不要加說明、不要改小標。

直接輸出校對後的全文。

---
{text}"""


def polish(text):
    """校對一遍。註釋記號少一個就整段退回原稿——寧可有錯字，不能掉註。"""
    marks = re.findall(r"\[\^\d+\]", text)
    try:
        out, _ = L.ask(POLISH.replace("{text}", text), temperature=0.2, max_tokens=65536)
    except Exception as e:
        print(f"    ⚠ 校對失敗，保留原稿：{e}", flush=True)
        return text
    out = out.strip()
    if re.findall(r"\[\^\d+\]", out) != marks or len(out) < len(text) * 0.85:
        print("    ⚠ 校對後註釋記號或篇幅對不上，保留原稿", flush=True)
        return text
    return out


def write_chapter(no, length):
    ch = load(no)
    dest = OUT / f"ch{no:02d}.md"
    if dest.exists():
        print(f"  第{no}章 已有，跳過")
        return
    plan = allocate(ch)
    citer, counter, notes, dropped = Citer(), [0], [], []
    secs = ch["sections"]
    body = []

    for i, section in enumerate(secs, 1):
        ids = plan.get(str(i)) or plan.get(f"第{i}節") or []
        legal = "、".join([f"E{int(re.fullmatch(r'E(\d+)', str(x).strip()).group(1))}"
                          for x in ids if re.fullmatch(r"E\d+", str(x).strip())]
                         + [str(r.get("id")) for r in ch["research"]]) or "（無，本節不標註釋）"
        prompt = WRITE.format(
            voice=VOICE, note_rule=NOTE_RULE.format(legal=legal),
            i=i, n=len(secs), section=section,
            prev=secs[i - 2] if i > 1 else "（本章開頭）",
            next=secs[i] if i < len(secs) else "（本章結尾）",
            excerpts=block_excerpts(ch, ids), research=block_research(ch),
            talk=block_talk(ch), length=length, **meta(ch))
        text, _ = L.ask(prompt, temperature=0.85, max_tokens=16384)
        text = polish(text.strip())
        text, drop = resolve_notes(text, ch, citer, counter, notes)
        dropped += drop
        body.append((section, text))
        print(f"    第{i}/{len(secs)}節 {section[:18]} — {len(text)} 字，累計註 {counter[0]}",
              flush=True)

    peek = (body[0][1][:600] + "\n……\n" + body[-1][1][-600:]) if body else ""
    frames = {}
    for kind, ask, ln in (("導言", INTRO_ASK, 800), ("結語", OUTRO_ASK, 600)):
        t, _ = L.ask(FRAME.format(voice=VOICE, kind=kind, ask=ask, length=ln, peek=peek,
                                  sections="\n".join(f"- {s}" for s in secs), **meta(ch)),
                     temperature=0.85, max_tokens=8192)
        t, drop = resolve_notes(t.strip(), ch, citer, counter, notes)
        dropped += drop
        frames[kind] = t

    OUT.mkdir(parents=True, exist_ok=True)
    md = [f"# 第{no}章　{ch['title']}", f"### {ch['span']}（{ch['period']}）", "",
          f"<!-- {ch['volume']} -->", "", frames["導言"], ""]
    for section, text in body:
        md += [f"## {section}", "", text, ""]
    md += ["## 結語", "", frames["結語"], "", "---", ""]
    md += [f"[^{n}]: {t}" for n, t in notes]
    dest.write_text("\n".join(md), encoding="utf-8")

    total = sum(len(t) for _, t in body) + sum(len(v) for v in frames.values())
    print(f"  ✓ 第{no}章 {ch['title']}：{total} 字、{len(notes)} 個頁下註"
          + (f"，丟棄無效註號 {len(dropped)}" if dropped else ""), flush=True)
    if citer.misses:
        p = BASE / "missing_books.txt"
        had = set(p.read_text(encoding="utf-8").splitlines()) if p.exists() else set()
        p.write_text("\n".join(sorted(had | citer.misses)), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapters", default="1-28", help="例 1-28 或 3,5,9")
    ap.add_argument("--length", default="2500–3200")
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
