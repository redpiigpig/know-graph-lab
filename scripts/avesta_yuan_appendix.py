#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
元文琪譯《阿維斯塔》附錄的**五欄神名對照表** → 本站詞庫的權威依據。

    python scripts/avesta_yuan_appendix.py --parse        # 解析並列出
    python scripts/avesta_yuan_appendix.py --audit        # 與本站詞庫逐條比對
    python scripts/avesta_yuan_appendix.py --audit --out output/glossary_audit.md

═══════════ 為什麼這份附錄是關鍵 ═══════════

商務印書館元文琪譯本的附錄（掃描本 pp.574–594，共 21 頁）是兩張大表：
  一、《阿維斯塔》神話中的主要善神和惡魔
  二、瑣羅亞斯德教傳說中的先知聖徒和帝王英雄

每一列給的是**同一個神在五個語言階段的名字**，中文與羅馬轉寫並列：

    職司 │ 波斯文 │ 帕拉維文 │ 阿維斯塔文 │ 古波斯文 │ 吠陀梵文 │ 備註

🚨 **這解掉了「該用他的還是用阿維斯陀形式」這個假兩難。**
   他自己就給了阿維斯陀語形式的中文譯名——巴赫曼（波斯）與沃胡馬納（阿維斯陀）
   在同一列上。所以不必二選一：
     本站正文譯阿維斯陀語原典 → 主譯取他的**阿維斯塔文**欄
     波斯語形式               → 收為異名（讀者拿《列王紀》或他的譯文來對照時查得到）

🚨 而且會改掉一些本站現有的定名。實例：`Atar`（聖火之神）本站作「阿塔爾」，
   但那其實是他的**帕拉維文**欄（Ātar）；他的阿維斯塔文欄是「阿斯拉 Athra」。
   本站等於在阿維斯陀語文本裡用了中古波斯的形式而不自知。

═══════════ 🚨 OCR 這張表會遇到的三件事 ═══════════

一、**表頭是直排兩行併成一格**：「名稱職司」其實是「名稱／職司」，
    而真正的名字不在第一欄——第一欄只有職司，名字散在各語言欄裡。
二、**一格裡常有兩三個異寫**：「亞茲丹Yazdān埃澤德Eyzed」是兩個名字，
    要按「漢字＋羅馬字」的交替切開。
三、**羅馬轉寫有 OCR 缺字**：「mshāspandān」掉了首字母 A、「Amahraspandān}」多了括號。
    故比對時一律正規化（去變音符、去非字母、小寫），且**比對不上就標出來，不猜**。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSONL = r"G:/我的雲端硬碟/資料/知識圖工作室/_chunks/6d731f04-664d-4459-826e-0dba1dbefc4b.jsonl"
NAMES = ROOT / "data" / "avesta" / "sources" / "names.json"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

APPENDIX_FROM, APPENDIX_TO = 574, 594

# 欄序（表頭有時被 OCR 切歪，故以「第幾欄」為準，並在 --parse 時印出表頭供核對）
COL_PERSIAN, COL_PAHLAVI, COL_AVESTAN, COL_OLD_PERSIAN, COL_SANSKRIT = 1, 2, 3, 4, 5

CJK = r"\u4e00-\u9fff"
# 「漢字串＋羅馬字串」的交替。羅馬字含變音符與括號（他用括號標異讀，如 阿胡拉(伊)）。
PAIR = re.compile(
    rf"([{CJK}（）()·‧]+)\s*([A-Za-zĀāÂâÄäĒēÊêĪīÎîŌōÔôÖöŪūÛûÜüŠšŽžČčŌṇṣṭḥŗ'()\-]{{2,}})")


def normalise_roman(s: str) -> str:
    """羅馬轉寫正規化：去變音符、去非字母、小寫。供比對用，不供顯示。

    >>> normalise_roman('Ahurā-Mazdā')
    'ahuramazda'
    >>> normalise_roman('Θraētaona')
    'raetaona'
    >>> normalise_roman('Am(e)-shōspandān}')
    'ameshospandan'
    """
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z]", "", s.lower())


def split_names(cell: str) -> list[tuple[str, str]]:
    """把一格拆成 [(中文, 羅馬轉寫), …]。一格常有兩三個異寫。

    >>> split_names('亞茲丹Yazdān埃澤德Eyzed')
    [('亞茲丹', 'Yazdān'), ('埃澤德', 'Eyzed')]
    >>> split_names('亞扎塔Yazata')
    [('亞扎塔', 'Yazata')]
    >>> split_names('')
    []
    """
    return [(zh.strip(), ro.strip()) for zh, ro in PAIR.findall(cell or "")]


def parse_rows() -> list[dict]:
    """把附錄各頁的表格解析成列。每列：{'office', 'persian', 'pahlavi', 'avestan', …}。"""
    pages = {json.loads(l)["page_number"]: json.loads(l)
             for l in open(JSONL, encoding="utf-8") if l.strip()}
    out: list[dict] = []
    for pg in range(APPENDIX_FROM, APPENDIX_TO + 1):
        page = pages.get(pg)
        if not page:
            continue
        for tr in re.findall(r"<tr>(.*?)</tr>", page["content"], re.S):
            tds = [re.sub(r"<[^>]+>", "", d) for d in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
            if len(tds) < 6:
                continue
            # 表頭列略過
            if "波斯文" in tds[COL_PERSIAN] or "職司" in tds[0]:
                continue
            row = {
                "page": pg,
                "office": tds[0].strip(),
                "persian": split_names(tds[COL_PERSIAN]),
                "pahlavi": split_names(tds[COL_PAHLAVI]),
                "avestan": split_names(tds[COL_AVESTAN]) if len(tds) > COL_AVESTAN else [],
                "old_persian": split_names(tds[COL_OLD_PERSIAN]) if len(tds) > COL_OLD_PERSIAN else [],
                "sanskrit": split_names(tds[COL_SANSKRIT]) if len(tds) > COL_SANSKRIT else [],
                "note": tds[-1].strip(),
            }
            if row["persian"] or row["avestan"] or row["pahlavi"]:
                out.append(row)
    return out


def cmd_parse() -> int:
    rows = parse_rows()
    print(f"解析出 {len(rows)} 列（附錄 pp.{APPENDIX_FROM}–{APPENDIX_TO}）")
    have_av = [r for r in rows if r["avestan"]]
    print(f"其中有阿維斯塔文欄的 {len(have_av)} 列\n")
    for r in rows[:25]:
        av = "／".join(f"{z}（{o}）" for z, o in r["avestan"]) or "—"
        pe = "／".join(f"{z}（{o}）" for z, o in r["persian"]) or "—"
        print(f"  p{r['page']} 阿：{av:34s} 波：{pe}")
    return 0


SEEDER = ROOT / "scripts" / "seed_glossary_zoroastrian.py"


def seeder_entries() -> list[dict]:
    """從 seed_glossary_zoroastrian.py 讀出條目（含 name_original，names.json 沒有）。"""
    src = SEEDER.read_text(encoding="utf-8")
    out = []
    # 🚨 條目多半跨行，而且 reason 裡有括號，所以**不能**用「配到收尾的 )」去切。
    #    第一版那樣寫只解析到 36 條（詞庫實有 122），而稽核照樣印出漂亮的表——
    #    分母錯了，結論就全錯（見 [[feedback_silent_zero_is_a_bug]]：稽核要印分母）。
    #    改成以「行首的 D(／P(／T(」切塊，取到下一個行首為止。
    starts = [m.start() for m in re.finditer(r"^[DPT]\(", src, re.M)]
    for i, pos in enumerate(starts):
        block = src[pos:starts[i + 1] if i + 1 < len(starts) else len(src)]
        m = re.match(r'([DPT])\("([^"]+)",\s*"([^"]+)"', block)
        if not m:
            continue
        o = re.search(r'o="([^"]*)"', block)
        out.append({"kind": m.group(1), "en": m.group(2), "zh": m.group(3),
                    "orig": o.group(1) if o else ""})
    return out


def db_glossary() -> dict[str, str]:
    """整個 /translation-glossary 的 {name_english: name_recommended}，快取到 output/。

    🚨 比對「這個名字詞庫有沒有」**必須拿整個 DB 比**，不能只比
       seed_glossary_zoroastrian.py（122 筆）或 names.json（195 筆）。
       DB 的 deities 有 360 筆、涵蓋所有宗教——`Mithra / Mithras → 密特拉`
       就只存在於 DB 裡。只比 seeder 的話它會被當成「新的」，
       然後用元文琪的「密斯拉」覆蓋掉全站通用的定名，
       而密特拉不只祆教在用，羅馬密特拉教那邊也在用。
    """
    import urllib.request
    cache = ROOT / "output" / "glossary_db_cache.json"
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    env = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k] = v.strip().strip('"').strip("'")
    url, key = env["SUPABASE_URL"], env.get("SUPABASE_SERVICE_ROLE_KEY") or env["SUPABASE_KEY"]
    out: dict[str, str] = {}
    for table in ("deities", "place_names", "theological_terms"):
        req = urllib.request.Request(
            f"{url}/rest/v1/{table}?select=name_english,name_recommended&limit=2000",
            headers={"apikey": key, "Authorization": f"Bearer {key}"})
        for r in json.load(urllib.request.urlopen(req)):
            if r.get("name_english") and r.get("name_recommended"):
                out[r["name_english"]] = r["name_recommended"]
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


def book_text() -> str:
    """全書 OCR 文字，供頻率校驗用。"""
    return "".join(json.loads(l)["content"]
                   for l in open(JSONL, encoding="utf-8") if l.strip())


def cmd_audit(out: Path | None) -> int:
    import difflib

    rows = parse_rows()
    entries = seeder_entries()
    full = book_text()

    # 他的阿維斯陀語條目；一列可能有數個異寫，全部收進來當配對候選。
    cands: list[dict] = []
    for r in rows:
        for zh, ro in r["avestan"]:
            cands.append({"zh": zh, "ro": ro, "key": normalise_roman(ro),
                          "pe": r["persian"][0][0] if r["persian"] else "",
                          "pa": r["pahlavi"][0][0] if r["pahlavi"] else "",
                          "office": r["office"], "page": r["page"]})

    def best_match(*keys: str) -> dict | None:
        """以羅馬轉寫配對：先求完全相同，再退而求相似度 ≥ 0.82。
        🚨 配不上就回 None，不硬湊——祆教神名彼此形近者極多
           （Ameretat／Ameshaspenta、Asha／Ashi），湊錯會把兩位神混成一位。"""
        norm = [normalise_roman(k) for k in keys if k]
        for c in cands:
            if c["key"] and c["key"] in norm:
                return c
        best, score = None, 0.0
        for c in cands:
            for k in norm:
                r = difflib.SequenceMatcher(None, k, c["key"]).ratio()
                if r > score:
                    best, score = c, r
        return best if score >= 0.82 else None

    same, diff, missing = [], [], []
    for e in entries:
        hit = best_match(e["orig"], e["en"])
        if not hit:
            missing.append((e["en"], e["zh"]))
            continue
        his, ours = hit["zh"], e["zh"]
        # 🚨 頻率校驗：表格是 OCR 出來的，字可能多一個少一個
        #    （實測「阿沙·瓦希什阿塔」多一個阿、「彭塔·阿爾邁蒂」少一個斯）。
        #    全書出現次數能分辨：他真正在用的寫法會在導讀裡反覆出現。
        n_his, n_ours = full.count(his), full.count(ours)
        flag = "" if n_his >= 2 else ("⚠ 全書僅 1 次，疑 OCR 損" if n_his else "⚠ 全書查無")
        row = (e["en"], ours, his, hit["pe"], hit["pa"], n_his, n_ours, flag, hit["page"])
        (same if normalise_cjk(his) == normalise_cjk(ours) else diff).append(row)

    lines = ["# 詞庫稽核：本站定名 vs 元文琪附錄的阿維斯塔文欄", "",
             f"依據：元文琪譯《阿維斯塔》附錄（掃描本 pp.{APPENDIX_FROM}–{APPENDIX_TO}），",
             "五欄對照表的**阿維斯塔文**欄。本站正文譯的是阿維斯陀語原典，",
             "故主譯應取該欄；波斯文欄收為異名。", "",
             f"- 一致：{len(same)} 條", f"- **不一致：{len(diff)} 條**",
             f"- 附錄查無對應：{len(missing)} 條（多為經典篇名、地名、概念詞，附錄只收神名與人名）", "",
             "## 不一致，建議改從元文琪", "",
             "全書出現次數是校驗欄：表格是 OCR 的，字可能多一個少一個；",
             "他真正在用的寫法會在導讀裡反覆出現，本站現行的寫法若為 0 次即表示不是他的。", "",
             "| 英文 | 本站現行 | 次 | 元文琪‧阿維斯塔文 | 次 | 波斯文 | 帕拉維文 | 頁 | |",
             "|---|---|---:|---|---:|---|---|---:|---|"]
    for en, ours, his, pe, pa, n_his, n_ours, flag, pg in sorted(diff):
        lines.append(f"| {en} | {ours} | {n_ours} | **{his}** | {n_his} | "
                     f"{pe or '—'} | {pa or '—'} | {pg} | {flag} |")
    lines += ["", "## 一致（不必動）", "", "| 英文 | 兩邊同 |", "|---|---|"]
    for r in sorted(same):
        lines.append(f"| {r[0]} | {r[1]} |")

    text = "\n".join(lines)
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"寫出 → {out.relative_to(ROOT)}")
    print(f"一致 {len(same)}　不一致 {len(diff)}　附錄查無 {len(missing)}")
    return 0


def normalise_cjk(s: str) -> str:
    """比對中文名時忽略間隔號與括號的差異。

    >>> normalise_cjk('阿胡拉‧馬茲達') == normalise_cjk('阿胡拉·馬茲達')
    True
    """
    return re.sub(r"[·‧•（）()\s]", "", s or "")


# 🚨 音譯用「里」不用「裡」。本站的簡轉繁（opencc s2tw）會把
#    「法里东→法裡東」「阿赫里曼→阿赫裡曼」誤轉，但「瓦伊里亚→瓦伊里亞」又對。
#    所以從這本 OCR 取來的專名一律過這道閘，否則會把自己的轉換錯誤當成他的寫法。
def fix_li(name: str) -> str:
    """把音譯裡誤轉的「裡」改回「里」。

    >>> fix_li('法裡東'), fix_li('阿赫裡曼'), fix_li('瓦伊裡亞')
    ('法里東', '阿赫里曼', '瓦伊里亞')
    """
    return name.replace("裡", "里")


def looks_damaged(zh: str, ro: str) -> str:
    """這一格看起來是不是 OCR 壞的？回傳原因，沒問題回空字串。

    🚨 附錄是掃描出來的，實測「阿沙·瓦希什阿塔」多一字、「彭塔·阿爾邁蒂」少一字、
       羅馬轉寫「mshāspandān」掉首字母。壞的格不可入庫——
       一個多一字的神名入了庫，之後每一次校對都會照著它改，錯得無法回頭。

    >>> looks_damaged('亞扎塔', 'Yazata')
    ''
    >>> looks_damaged('阿', 'Yazata')
    '中文過短'
    >>> looks_damaged('亞扎塔', 'Yz')
    '轉寫過短'
    >>> looks_damaged('亞扎塔（', 'Yazata')
    '括號不成對'
    """
    if len(re.sub(r"[·‧（）()]", "", zh)) < 2:
        return "中文過短"
    if len(re.sub(r"[^A-Za-z]", "", ro)) < 3:
        return "轉寫過短"
    if zh.count("（") != zh.count("）") or zh.count("(") != zh.count(")"):
        return "括號不成對"
    if ro.count("(") != ro.count(")") or ro.count("（") != ro.count("）"):
        return "轉寫括號不成對"
    # 🚨 轉寫首字母會被隔壁欄吃掉。實測「卡維 Kavi」的 K 跑到職司欄尾
    #    （「凱揚王朝諸帝王的稱號K」），這一欄只剩 avi。
    #    首字母小寫就是這種情形——他的轉寫一律大寫開頭。
    if ro[:1].islower():
        return "轉寫首字母被鄰欄吃掉"
    return ""


def cmd_new(out: Path) -> int:
    """列出附錄有、而本站詞庫還沒有的神名／人名，產出可貼進 seeder 的條目。"""
    import difflib

    rows = parse_rows()
    entries = seeder_entries()
    full = book_text()
    known = [normalise_roman(e["orig"]) for e in entries if e["orig"]]
    known += [normalise_roman(e["en"]) for e in entries]
    known_zh = {normalise_cjk(e["zh"]) for e in entries}
    # 🚨 詞庫裡有五筆**既有權威條目不在 seeder 裡**（查拉圖斯特拉／阿胡拉‧馬茲達／
    #    安格拉‧曼紐／密特拉／祆教，見 seeder 檔首「既有條目一律不動」）。
    #    只比 seeder 的話，它們會被當成「新的」而重複入庫，
    #    而且會用元文琪的寫法覆蓋掉全站通用的定名（密特拉→密斯拉）——
    #    密特拉不只用在祆教，羅馬密特拉教那邊也在用，不能只看這本書就改。
    protected = db_glossary()
    for k, v in protected.items():
        # 「Mithra / Mithras」這種一格兩名的鍵要拆開比
        known += [normalise_roman(p) for p in re.split(r"[/;,]", k)]
        known_zh |= {normalise_cjk(p) for p in re.split(r"[/；;，,]", v)}

    new_rows, skipped = [], []
    seen: set[str] = set()
    for r in rows:
        if not r["avestan"]:
            continue
        zh_raw, ro = r["avestan"][0]
        why = looks_damaged(zh_raw, ro)
        if why:
            skipped.append((zh_raw, ro, why))
            continue
        # 🚨 不可用 strip("（）()")——那會把「阿胡拉(伊)」的收尾括號剝掉變成
        #    「阿胡拉(伊」，一個本來完好的名字反而被弄壞。只去掉整個被包起來的情形。
        zh = fix_li(re.sub(r"^[（(](.+)[）)]$", r"", zh_raw))
        key = normalise_roman(ro)
        if key in seen:
            continue
        seen.add(key)
        # 已在詞庫？羅馬轉寫完全相同或高度相似、或中文相同，都算已有。
        if key in known or normalise_cjk(zh) in known_zh:
            continue
        if any(difflib.SequenceMatcher(None, key, k).ratio() >= 0.86 for k in known if k):
            continue
        new_rows.append({
            "zh": zh, "ro": ro.strip("()"),
            "pe": fix_li(r["persian"][0][0]) if r["persian"] else "",
            "pa": fix_li(r["pahlavi"][0][0]) if r["pahlavi"] else "",
            "office": re.sub(r"\s+", "", r["office"])[:40],
            "note": re.sub(r"\s+", "", r["note"])[:60],
            "n": full.count(zh), "page": r["page"],
        })

    lines = ["# 元文琪附錄有、本站詞庫還沒有的神名／人名", "",
             f"共 {len(new_rows)} 條（另有 {len(skipped)} 格判定為 OCR 損而略過）。", "",
             "主譯取他的**阿維斯塔文**欄，波斯文／帕拉維文收為異名。",
             "「全書次」是該寫法在 595 頁裡出現幾次——只在附錄出現（1 次）者要人再確認。", "",
             "| 阿維斯塔文 | 轉寫 | 全書次 | 波斯文 | 帕拉維文 | 職司 | 頁 |",
             "|---|---|---:|---|---|---|---:|"]
    for r in sorted(new_rows, key=lambda x: -x["n"]):
        lines.append(f"| **{r['zh']}** | {r['ro']} | {r['n']} | {r['pe'] or '—'} | "
                     f"{r['pa'] or '—'} | {r['office']} | {r['page']} |")
    lines += ["", "## 判定為 OCR 損而略過", "", "| 中文 | 轉寫 | 原因 |", "|---|---|---|"]
    for zh, ro, why in skipped:
        lines.append(f"| {zh} | {ro} | {why} |")

    lines += ["", "## 可貼進 seed_glossary_zoroastrian.py 的條目", "", "```python"]
    for r in sorted(new_rows, key=lambda x: -x["n"]):
        var = "；".join(x for x in [
            f"{r['pe']}（波斯語）" if r["pe"] else "",
            f"{r['pa']}（帕拉維語）" if r["pa"] else ""] if x)
        lines.append(
            f'D("{r["ro"]}", "{r["zh"]}", o="{r["ro"]}",'
            + (f' var="{var}",' if var else "")
            + f' etype="deity", domain="{r["office"]}",'
            + f' reason="元文琪譯《阿維斯塔》附錄阿維斯塔文欄（掃描本 p.{r["page"]}）。")')
    lines.append("```")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"新增候選 {len(new_rows)} 條、OCR 損略過 {len(skipped)} 格 → {out.relative_to(ROOT)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="元文琪附錄神名表 → 詞庫稽核")
    ap.add_argument("--parse", action="store_true")
    ap.add_argument("--audit", action="store_true")
    ap.add_argument("--new", action="store_true", help="列出附錄有而詞庫沒有的")
    ap.add_argument("--out", default=str(ROOT / "output" / "glossary_audit.md"))
    a = ap.parse_args()
    if a.parse:
        return cmd_parse()
    if a.new:
        return cmd_new(ROOT / "output" / "glossary_new.md")
    if a.audit:
        return cmd_audit(Path(a.out))
    ap.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
