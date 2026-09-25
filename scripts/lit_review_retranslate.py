#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""研究回顧逐段中譯（lit_review_sections 的 zh 版）清掉拒答／亂碼／漏譯，再逐段補譯。

2026-09-25 稽核：zh 欄裡有三種「看起來翻好了、其實沒有」的段落——
  ① 模型拒答或回話（〈Taixu〉一篇 512 段都是「請提供完整的文段內容…」）
  ② 亂碼：U+FFFD（多在段首第一字）與整段「??????」（〈Letter to Menoeceus〉）
  ③ 該譯卻還是外文（書目段除外——書目本來就該留原文）
使用者決定：全部清空、重新補譯（ebook-translate SKILL.md「拒答清空重譯」）。

「未翻」在這張表的表示法＝**沒有那一列 zh**（ingest_lit_review.missing_indices
就是這樣算缺口的；reader 對缺 zh 的段落只顯示原文、左欄一條「—」）。所以清空＝
刪掉那一列 zh，不是寫空字串。

亂碼根因（2026-09-25 查）：orig 欄 0 段含 U+FFFD、0 段含「????」，全部出在 zh 欄，
所以是**翻譯時**產生的，不是切段——原文不用修，重譯就好。U+FFFD 677 段是段首單一個
（全在 genesis-philosophy），「????」是譯文經過非 UTF-8 管道被換成問號。
另外有一批原文**本身就是亂碼**（PDF 自訂字型抽出來的控制字元，如
`\x01\x02\x07.\x06 F eb`）——模型對它們回「我注意到您提供的文本…」。這種重譯沒有
意義，本腳本把 zh 清掉後標 skip 留白，要救得從原 PDF 重抽（屬 lit_review.py 切段
那一層，不在本腳本範圍）。

子命令
------
  scan  [--refresh] [--samples 30]   偵測，印分母／命中數／抽樣，寫 hits.json
  clear                               先備份原值到 output/lit_review_backup_2026-09-25.json
                                      再刪掉命中的 zh 列（備份檔已存在就合併，不覆蓋）
  run   [--max-minutes N]             逐段補譯（可續跑；fleet_keeper lane `litreview-retrans`）
  status                              印進度

進度檔：output/lit_review_retrans/progress.json（本機，不進 git）。
全部補完（每一段都已寫入或判定留白）才印 LITREVIEW_RETRANS_COMPLETE；
引擎出錯而沒做完時絕不印。
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import random
import re
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

WORK = ROOT / "output" / "lit_review_retrans"
DUMP = WORK / "dump.json"
HITS = WORK / "hits.json"
PROGRESS = WORK / "progress.json"
BACKUP = ROOT / "output" / "lit_review_backup_2026-09-25.json"
DONE_MARKER = "LITREVIEW_RETRANS_COMPLETE"


def _env() -> None:
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_env()
URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}


# ── REST（一律帶 limit 分頁；PostgREST 不帶 limit 會靜默截在 1000）────────────
def rest_get(path: str) -> list:
    for attempt in range(5):
        try:
            r = requests.get(f"{URL}/rest/v1/{path}", headers=H, timeout=120)
            r.raise_for_status()
            return r.json()
        except requests.RequestException:
            if attempt == 4:
                raise
            time.sleep(5 * (attempt + 1))
    return []


def rest_paged(table: str, select: str, extra: str = "") -> list:
    rows, last = [], 0
    while True:
        b = rest_get(f"{table}?select={select}&id=gt.{last}&order=id&limit=1000{extra}")
        if not b:
            return rows
        rows += b
        last = b[-1]["id"]


def load_dump(refresh: bool) -> dict:
    if DUMP.exists() and not refresh:
        return json.loads(DUMP.read_text(encoding="utf-8"))
    WORK.mkdir(parents=True, exist_ok=True)
    d = {"sections": rest_paged("lit_review_sections", "id,entry_id,version_code,order_index,text"),
         "entries": rest_paged("lit_review_entries",
                               "id,project_slug,ref_key,authors,title,language,theme,fulltext_status")}
    DUMP.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    return d


# ── 偵測 ─────────────────────────────────────────────────────────────────────
# 主判準用共用工具 translation_fix.clear_reason（meta／think／fffd／untranslated）。
# 下面只補它漏掉、而本表實測有的：開場白變體（SUPP_HEAD）、埋在段中的任務話
# （META_ANYWHERE）、整段「????」、模型自己續寫原文沒有的英文，以及「原文本身
# 沒有可譯內容」（連結按鈕、PDF 控制字元）的留白判定。
import translation_fix as tf  # noqa: E402

_te = None


def te():
    """translate_ebook_to_zh（引擎鏈）。工作樹版若正被別的 session 改到 import 不了，
    退回 git HEAD 版載入——不動那個檔。"""
    global _te
    if _te is None:
        try:
            import translate_ebook_to_zh as m
        except Exception as e:  # noqa: BLE001
            import subprocess
            import types
            print(f"  (translate_ebook_to_zh 工作樹版 import 失敗：{type(e).__name__}；改用 git HEAD 版)",
                  flush=True)
            src = subprocess.run(["git", "-C", str(ROOT), "show", "HEAD:scripts/translate_ebook_to_zh.py"],
                                 capture_output=True, check=True).stdout.decode("utf-8")
            m = types.ModuleType("translate_ebook_to_zh")
            m.__file__ = str(ROOT / "scripts" / "translate_ebook_to_zh.py")
            sys.modules["translate_ebook_to_zh"] = m
            exec(compile(src, m.__file__, "exec"), m.__dict__)
        _te = m
    return _te


META_WINDOW = 40
SUPP_HEAD = ("(空白)", "（空白）", "(No output)", "（無輸出）", "無法進行此翻譯", "我無法辨識",
             "我感謝您", "感謝您的詳細", "I appreciate you", "I notice", "I'd be happy", "We need to")
META_ANYWHERE = (
    "請提供完整的", "請提供需要翻譯", "請提供您需要", "請提供您要", "請提供要翻譯",
    "請提供具體的", "我將按照您的要求", "按照您的要求進行", "您提供的文本", "您提供的文字",
    "您提供的原文", "您提供的內容", "您提供的段落", "僅輸出繁體中文翻譯", "只輸出翻譯",
    "provide the text you", "provide the academic text", "text you'd like me to translate",
    "text you would like me to translate", "ready to translate",
)

_FFFD = "�"
_QRUN = re.compile(r"\?{3,}")
_CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_CJK = re.compile(r"[一-鿿]")
_LAT = re.compile(r"[A-Za-zÀ-ɏ]")
_WORD = re.compile(r"[A-Za-zÀ-ɏ]+")
_DE_FR_FUNC = re.compile(
    r"\b(der|die|das|und|nicht|ist|ein|eine|mit|von|zu|auf|für|dass|sich|den|dem|des"
    r"|le|la|les|et|est|une|un|des|du|dans|pour|qui|que|pas|sur|avec|ce|ne)\b", re.I)
_EN_FUNC = re.compile(
    r"\b(the|of|and|to|is|are|was|were|that|which|with|from|this|these|there|we|it|in|by"
    r"|as|not|but|have|has|been|would|could)\b", re.I)

# 參考文獻連結按鈕、網頁殼。這些**本來就沒有可譯的內容**。
_LINK_LABEL_TOKENS = {
    "article", "cas", "pubmed", "central", "google", "scholar", "ads", "mathscinet", "math",
    "search", "author", "on", "crossref", "web", "of", "science", "isi", "zentralblatt",
    "scopus", "view", "full", "text", "pdf", "doi", "link", "open", "access", "download",
    "citation", "cite", "this", "abstract", "html", "and", "online", "library", "wiley",
}
_BIB_HINTS = re.compile(
    r"\b(19|20)\d\d[a-z]?\b|\bpp?\.\s*\d|\bvol\.|\bed(s)?\.|\bet al\.|\bdoi\b|doi\.org|"
    r"\bJournal\b|\bPress\b|\bUniversity\b|\bProceedings\b|\bIn:|\bRev\.|\bISBN\b|\bISSN\b"
    r"|\b\d+\s*[–-]\s*\d+\b|\(\d{4}\)")


_PROSE_RUN = re.compile(r"[A-Za-zÀ-ɏ][A-Za-zÀ-ɏ\s,;:'’\"“”()\-\.]{119,}")


def _norm(s: str) -> str:
    return re.sub(r"[^a-z]", "", s.lower())


def cjk_ratio(s: str) -> float:
    return len(_CJK.findall(s)) / max(1, len(s))


def is_junk_source(orig: str) -> str:
    """原文本身沒有可譯內容時回原因（留白就是正確答案）。"""
    o = (orig or "").strip()
    if not o:
        return "empty-orig"
    if len(_CTRL.findall(o)) >= 3 or len(_CTRL.findall(o)) / len(o) > 0.02:
        return "garbled-orig"  # PDF 自訂字型抽出的控制字元
    letters = _LAT.findall(o) + _CJK.findall(o)
    if len(letters) < 2:
        return "no-letters"
    words = [w.lower() for w in _WORD.findall(o)]
    if words and len(words) <= 20 and all(w in _LINK_LABEL_TOKENS for w in words):
        return "link-labels"
    return ""


_BIB_START = re.compile(
    r"^(?:\[?\d{1,3}[\].]?\s*)?(?:"
    r"[–—\-_―]{2,}|―|↑|\^ |\d+[–-]\d+,|\d{4}[a-z]?,|“"                      # 同上作者／維基註腳／頁碼起首
    r"|[A-Za-zÀ-ÿ'’\-]+(?: [A-Za-zÀ-ÿ'’\-]+){0,2},\s*[A-ZÀ-Þ]"   # Strasser, Stephan / vander Waerdt, P.
    r"|[A-Z][A-Za-zÀ-ÿ'’\-]+\s+[A-Z]{1,3}\b[ ,.(]"              # Dennett DC (2018)
    r")")
_YEAR = re.compile(r"\b(1[5-9]|20)\d\d[a-z]?\b|\bn\.d\.|\bforthcoming\b")


def is_bib(orig: str) -> bool:
    """原文是書目／參考文獻條目：譯文保留原文是對的，不算漏譯。
    判準看**開頭長得像「姓, 名」**＋有年份，不看全段有沒有 University/Press——
    後者在正文裡也常見，會把真正漏譯的英文散文放行。"""
    o = (orig or "").strip()
    if not o or len(o) > 1200:
        return False
    if _BIB_START.match(o) and _YEAR.search(o):
        return True
    hints = len(_BIB_HINTS.findall(o))
    caps_names = len(re.findall(r"\b[A-Z][a-zà-ÿ'’\-]+,\s*(?:[A-Z]\.\s*)+", o))  # Smith, J. K.
    if caps_names >= 1 and hints >= 2:
        return True
    if len(re.findall(r"\b[A-Z]{3,}\b", o)) >= 2 and hints >= 1:
        return True
    return False


def func_density(s: str) -> float:
    lat = len(_LAT.findall(s))
    if lat < 30:
        return 0.0
    return (len(_EN_FUNC.findall(s)) + len(_DE_FR_FUNC.findall(s))) / (lat / 100)


def classify(orig: str, zh: str) -> str:
    """zh 不可用就回原因，可用回空字串。只給非中文來源文獻用。"""
    z = (zh or "").strip()
    o = (orig or "").strip()
    if not z:
        return ""
    base = tf.clear_reason(z, o)
    if base in ("meta", "think", "fffd"):
        return base
    if any(m in z[:META_WINDOW] and m.lower() not in o.lower() for m in SUPP_HEAD):
        return "meta+"
    if any(m in z and m not in o for m in META_ANYWHERE):
        return "meta+"
    if _QRUN.search(z) and not _QRUN.search(o):
        return "garble-qmark"
    # 模型把標題譯完後自己續寫一段英文、或吐出別段的英文：原文裡沒有的長串外文散文。
    for run in _PROSE_RUN.findall(z):
        if func_density(run) >= 6.0 and _norm(run)[:50] not in _norm(o):
            return "foreign-invented"
    # clear_reason 的 untranslated 會把「中譯（Original title）」大量括註原文的譯文也算進來，
    # 在本表誤判過半；這裡要求原文是散文、而譯文真的把原文散文抄回來（或幾乎沒有漢字）。
    if base != "untranslated" or is_junk_source(o) or is_bib(o):
        return ""
    if func_density(o) < 6.0 or len(_LAT.findall(o)) < 60:
        return ""  # 原文不是散文（公式、書名、目次、書眉）
    copied = sum(len(r) for r in _PROSE_RUN.findall(z)
                 if func_density(r) >= 6.0 and _norm(r)[:50] in _norm(o))
    if copied >= 0.5 * len(o) or cjk_ratio(z) < 0.08:
        return "untranslated"
    return ""


def build_index(d: dict):
    E = {e["id"]: e for e in d["entries"]}
    S = collections.defaultdict(dict)
    ids = {}
    for r in d["sections"]:
        S[(r["entry_id"], r["order_index"])][r["version_code"]] = r["text"] or ""
        ids[(r["entry_id"], r["order_index"], r["version_code"])] = r["id"]
    return E, S, ids


def cmd_scan(args) -> None:
    d = load_dump(args.refresh)
    E, S, ids = build_index(d)
    zh_all = [k for k, v in S.items() if "zh" in v]
    zh_lang = [k for k in zh_all if (E.get(k[0]) or {}).get("language") == "zh"]
    denom = [k for k in zh_all if (E.get(k[0]) or {}).get("language") != "zh"]
    print(f"zh 列總數 {len(zh_all)}；language=zh 排除 {len(zh_lang)}；分母 {len(denom)}")
    hits = []
    for k in denom:
        v = S[k]
        why = classify(v.get("orig", ""), v["zh"])
        if why:
            hits.append({"id": ids[(k[0], k[1], "zh")], "entry_id": k[0], "order_index": k[1],
                         "reason": why, "orig": v.get("orig", ""), "zh": v["zh"],
                         "junk_source": is_junk_source(v.get("orig", ""))})
    by = collections.Counter(h["reason"].split("-")[0] for h in hits)
    fine = collections.Counter(h["reason"] for h in hits)
    print(f"命中 {len(hits)} 段，分布在 {len({h['entry_id'] for h in hits})} 篇")
    print("  大類:", dict(by))
    print("  細類:", dict(fine))
    print("  其中原文本身無可譯內容（清空後留白不重譯）:",
          dict(collections.Counter(h["junk_source"] for h in hits if h["junk_source"])))
    bib_kept = sum(1 for k in denom if is_bib(S[k].get("orig", "")))
    print(f"  書目段（保留原文、不列問題）{bib_kept}")
    top = collections.Counter(h["entry_id"] for h in hits).most_common(10)
    print("  最多的 10 篇:", [(e, (E[e]['title'] or '')[:30], n) for e, n in top])
    HITS.write_text(json.dumps(hits, ensure_ascii=False), encoding="utf-8")
    random.seed(args.seed)
    for h in random.sample(hits, min(args.samples, len(hits))):
        print(f"--- [{h['reason']}] entry {h['entry_id']} #{h['order_index']}")
        print("   orig:", repr(h["orig"][:110]))
        print("   zh  :", repr(h["zh"][:110]))


# ── 清空 ─────────────────────────────────────────────────────────────────────
def cmd_clear(args) -> None:
    hits = json.loads(HITS.read_text(encoding="utf-8"))
    backup = {}
    if BACKUP.exists():
        for r in json.loads(BACKUP.read_text(encoding="utf-8"))["rows"]:
            backup[r["id"]] = r
    # 刪之前再讀一次現值：dump 可能已過時，備份要存「刪掉的那一刻」的原值。
    ids = [h["id"] for h in hits]
    reason = {h["id"]: h for h in hits}
    live = {}
    for i in range(0, len(ids), 200):
        chunk = ",".join(map(str, ids[i:i + 200]))
        for r in rest_get(f"lit_review_sections?select=id,entry_id,version_code,order_index,text"
                          f"&id=in.({chunk})&limit=1000"):
            live[r["id"]] = r
    todel = []
    for i, r in live.items():
        if r["version_code"] != "zh" or r["text"] != reason[i]["zh"]:
            continue  # 已被別人改過，不動
        backup.setdefault(i, {**r, "reason": reason[i]["reason"],
                              "junk_source": reason[i]["junk_source"],
                              "orig": reason[i]["orig"]})
        todel.append(i)
    BACKUP.write_text(json.dumps({"note": "lit_review_sections zh 列清空前原值（2026-09-25 拒答/亂碼/漏譯稽核）",
                                  "count": len(backup), "rows": list(backup.values())},
                                 ensure_ascii=False, indent=0), encoding="utf-8")
    # 讀回驗證備份
    chk = json.loads(BACKUP.read_text(encoding="utf-8"))
    assert all(i in {r["id"] for r in chk["rows"]} for i in todel), "backup verify failed"
    print(f"備份 {len(backup)} 列 → {BACKUP}；本次要刪 {len(todel)} 列（dump 命中 {len(hits)}，"
          f"現值已變動而略過 {len(hits) - len(todel)}）")
    if args.dry_run:
        return
    n = 0
    for i in range(0, len(todel), 100):
        chunk = ",".join(map(str, todel[i:i + 100]))
        r = requests.delete(f"{URL}/rest/v1/lit_review_sections?id=in.({chunk})&version_code=eq.zh",
                            headers={**H, "Prefer": "return=minimal"}, timeout=120)
        r.raise_for_status()
        n += len(todel[i:i + 100])
    print(f"已刪 {n} 列 zh")


# ── 補譯 ─────────────────────────────────────────────────────────────────────
BUDDHIST = ("bajingfa", "mahaprajapati-revolution", "yinshun-shengyan")
PROMPT = """你是學術翻譯者。把下面「原文」逐段譯成**繁體中文**（台灣學術用語）。

這篇文獻：{title}（{authors}）
脈絡：{context}

規則：
1. 忠實、完整，不增不減；保留論證結構。每一段都要譯，不可跳過，不可摘要。
2. 譯名依脈絡：{naming}
   專名首次出現可括註原文，例：大愛道（Mahāpajāpatī）。同一篇譯名前後一致；下方「本篇已用譯名」照用。
   人名中間點一律用「‧」。
3. 數字：西元年月日一律阿拉伯數字（1969年2月18日、1960年代）；四位數以上的非整數盡量用阿拉伯數字（1,382人）；整數可照中文（四千年、兩萬人）；章名序號與經文照中文。
4. 書目、參考文獻條目（作者、書名、刊名、卷期頁碼、DOI）原樣保留原文，不要翻譯。數學式、LaTeX、程式碼原樣保留。
5. 原文若只是頁眉、頁碼或網頁按鈕文字，照字面譯出即可，不要評論。
6. 只輸出譯文。不要寒暄、不要說明、不要說「以下是翻譯」、不要反問、不要要求提供更多內容。
7. 輸出格式：每段前面照抄原文的段落標記（例如 ⟦1⟧），標記單獨一行，後面接該段譯文。標記數量與順序必須和原文完全一樣。
{glossary}
原文：
{body}"""


def naming_rule(entry: dict) -> tuple[str, str]:
    slug = entry.get("project_slug") or ""
    title = f"{entry.get('title') or ''} {entry.get('theme') or ''}"
    if slug in BUDDHIST or re.search(r"Buddh|bhikkhu|Dharma|Sūtra|Sutta|Taixu|Yinshun|Mahā|佛", title, re.I):
        return ("佛教學", "佛學文獻用佛學慣用譯名（比丘尼、八敬法、僧團、律藏、阿含、大愛道、太虛、印順；"
                "巴利／梵文術語括註原拼寫）。")
    if slug == "theological-studies-manifesto" or re.search(
            r"Christ|Church|Theolog|Bible|Gospel|Catholic|Protestant|Orthodox|Augustine|Aquinas|Luther|Calvin",
            title, re.I):
        return ("基督宗教神學", "基督宗教文獻依教派用語：天主教脈絡用天主教譯名（天主、伯多祿、梅瑟、聖神、"
                "彌撒、額我略）；新教脈絡用和合本譯名（上帝／神、彼得、摩西、聖靈）；東正教依東正教慣用。"
                "判斷不出教派時用學界通用譯名。")
    return ("學術論文（哲學／科學／宗教學）", "哲學家、科學家、宗教人物用學界通行中譯；"
            "佛學概念用佛學慣用譯名，基督宗教概念依所屬教派用語。")


_MARK_RE = re.compile(r"⟦(\d+)⟧")
_GLOSS_RE = re.compile(r"([一-鿿‧·]{2,12})（([A-Z][A-Za-zÀ-ɏ'’\-\. ]{2,40})）")


def entry_glossary(zh_texts: list[str], limit: int = 40) -> str:
    """從同一篇**已通過檢查的**既有譯文抽「中譯（Original）」對，供新譯文照用。"""
    seen = collections.OrderedDict()
    for t in zh_texts:
        for zh, en in _GLOSS_RE.findall(t or ""):
            en = en.strip()
            if en not in seen:
                seen[en] = zh
            if len(seen) >= limit:
                break
        if len(seen) >= limit:
            break
    if not seen:
        return ""
    return "\n本篇已用譯名：" + "；".join(f"{en}＝{zh}" for en, zh in seen.items()) + "\n"


def gate(zh: str, orig: str) -> str:
    """寫入前的檢查關卡：回原因＝不可寫。"""
    z = (zh or "").strip()
    if not z:
        return "empty"
    if _MARK_RE.search(z):
        return "stray-marker"
    why = classify(orig, z)
    if why:
        return why
    if "<think" in z.lower() or "</think" in z.lower():
        return "think"
    o = (orig or "").strip()
    # 必須是中文：原文有實質散文而譯文幾乎沒有漢字＝沒譯（書目、公式段除外）
    if not is_bib(o) and func_density(o) >= 4.0 and len(_LAT.findall(o)) >= 40 and cjk_ratio(z) < 0.15:
        return "not-chinese"
    if len(o) >= 200 and len(z) < len(o) * 0.12:
        return "too-short"
    if len(z) > max(400, len(o) * 3):
        return "too-long"
    return ""


class EngineDown(RuntimeError):
    pass


_gemini_dead_until = 0.0
_nvidia_dead_until = 0.0


def call_chain(prompt: str) -> tuple[str, str]:
    """Gemini → NVIDIA（repo 設定的模型名）→ Haiku。回 (text, engine)。
    這裡只管「拿到一段文字」；內容對不對由呼叫端逐段過 gate。"""
    global _gemini_dead_until, _nvidia_dead_until
    t = te()
    errs = []
    now = time.time()
    if now >= _gemini_dead_until and t.GEMINI_KEYS:
        try:
            old = t.PROMPT_TMPL
            t.PROMPT_TMPL = "{source}"
            try:
                return t.gemini_translate(prompt), "gemini"
            finally:
                t.PROMPT_TMPL = old
        except Exception as e:  # noqa: BLE001
            errs.append(f"gemini: {str(e)[:120]}")
            if "exhausted" in str(e) or "HTTP 4" in str(e):
                _gemini_dead_until = time.time() + 3600
    if now >= _nvidia_dead_until and t.NVIDIA_KEYS:
        try:
            out = t.nvidia_chat(prompt, max_tokens=8000, thinking=False, deadline_s=420)
            return t._to_traditional(out), "nvidia"
        except Exception as e:  # noqa: BLE001
            errs.append(f"nvidia: {str(e)[:160]}")
            if "404 on all" in str(e) or "410" in str(e):
                _nvidia_dead_until = time.time() + 3600
    try:
        old = t.PROMPT_TMPL
        t.PROMPT_TMPL = "{source}"
        try:
            out = t._anthropic_translate(t.HAIKU_MODEL, "Haiku", prompt, backoffs=(0, 60))
        finally:
            t.PROMPT_TMPL = old
        return t._to_traditional(out), "haiku"
    except Exception as e:  # noqa: BLE001
        errs.append(f"haiku: {str(e)[:120]}")
    raise EngineDown(" | ".join(errs))


def split_marked(text: str, n: int) -> list[str] | None:
    parts = _MARK_RE.split(text)
    # parts = [前綴, "1", 段1, "2", 段2, ...]
    if len(parts) != 2 * n + 1 or parts[0].strip():
        return None
    nums = parts[1::2]
    if nums != [str(i + 1) for i in range(n)]:
        return None
    return [t.strip() for t in parts[2::2]]


def load_progress() -> dict:
    if PROGRESS.exists():
        return json.loads(PROGRESS.read_text(encoding="utf-8"))
    return {"done": {}, "skip": {}, "fail": {}, "dead": {}}


def save_progress(p: dict) -> None:
    tmp = PROGRESS.with_suffix(".tmp")
    tmp.write_text(json.dumps(p, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, PROGRESS)


def keyof(eid: int, oi: int) -> str:
    return f"{eid}:{oi}"


MAX_GATE_FAIL = 6
BATCH_CHARS = 3500
BATCH_N = 6


def cmd_run(args) -> int:
    rows = json.loads(BACKUP.read_text(encoding="utf-8"))["rows"]
    p = load_progress()
    queue = collections.defaultdict(list)
    for r in rows:
        k = keyof(r["entry_id"], r["order_index"])
        if k in p["done"] or k in p["skip"] or k in p["dead"]:
            continue
        if r.get("junk_source"):
            p["skip"][k] = r["junk_source"]
            continue
        queue[r["entry_id"]].append(r)
    # U+FFFD 根因是模型 byte-fallback 多吐一個替換字元、後面的字是完整的（原文欄 0 例）。
    # 剝掉那個字元後若整段過得了關卡，就是一段正確的譯文，不必再花一次 LLM 呼叫。
    fixed = []
    for eid, rs in queue.items():
        for r in list(rs):
            if r.get("reason") != "fffd":
                continue
            z = tf.strip_fffd(r["text"] or "")
            if z and not gate(z, r["orig"]):
                fixed.append((r, z))
                rs.remove(r)
    for i in range(0, len(fixed), 200):
        part = fixed[i:i + 200]
        cur_zh = set()
        for eid in {r["entry_id"] for r, _ in part}:
            for x in rest_get(f"lit_review_sections?select=order_index&entry_id=eq.{eid}"
                              f"&version_code=eq.zh&limit=20000"):
                cur_zh.add((eid, x["order_index"]))
        payload = [{"entry_id": r["entry_id"], "version_code": "zh", "order_index": r["order_index"],
                    "text": z, "char_count": len(z)} for r, z in part
                   if (r["entry_id"], r["order_index"]) not in cur_zh]
        if payload:
            resp = requests.post(
                f"{URL}/rest/v1/lit_review_sections?on_conflict=entry_id,version_code,order_index",
                headers={**H, "Prefer": "resolution=merge-duplicates,return=minimal"},
                data=json.dumps(payload), timeout=120)
            resp.raise_for_status()
        for r, _ in part:
            p["done"][keyof(r["entry_id"], r["order_index"])] = "fffd-strip"
        save_progress(p)
    if fixed:
        print(f"[fffd] 剝掉替換字元即可用、直接寫回 {len(fixed)} 段", flush=True)
    queue = {e: rs for e, rs in queue.items() if rs}
    save_progress(p)
    total_left = sum(len(v) for v in queue.values())
    print(f"[start] {time.strftime('%m-%d %H:%M')} 待補 {total_left} 段／{len(queue)} 篇；"
          f"已補 {len(p['done'])}、留白 {len(p['skip'])}、放棄 {len(p['dead'])}", flush=True)
    t_end = time.time() + args.max_minutes * 60 if args.max_minutes else None
    engine_errors = 0
    entries: dict = {}
    for eid in sorted(queue, key=lambda e: len(queue[e])):
        if t_end and time.time() > t_end:
            break
        if eid not in entries:
            got = rest_get(f"lit_review_entries?select=id,project_slug,title,authors,theme,language"
                           f"&id=eq.{eid}&limit=1")
            if not got:
                for r in queue[eid]:
                    p["skip"][keyof(eid, r["order_index"])] = "entry-gone"
                save_progress(p)
                continue
            entries[eid] = got[0]
        entry = entries[eid]
        ctx_name, naming = naming_rule(entry)
        # 同一篇的現值：原文（重譯前比對有沒有被重新切段）＋已通過檢查的譯文（抽譯名）
        cur = collections.defaultdict(dict)
        last = 0
        while True:
            b = rest_get(f"lit_review_sections?select=id,order_index,version_code,text&entry_id=eq.{eid}"
                         f"&id=gt.{last}&order=id&limit=1000")
            if not b:
                break
            for r in b:
                cur[r["order_index"]][r["version_code"]] = r["text"] or ""
            last = b[-1]["id"]
        good_zh = [v["zh"] for oi, v in sorted(cur.items())
                   if v.get("zh") and not classify(v.get("orig", ""), v["zh"])]
        gloss = entry_glossary(good_zh)
        todo = []
        for r in sorted(queue[eid], key=lambda r: r["order_index"]):
            k = keyof(eid, r["order_index"])
            now = cur.get(r["order_index"], {})
            if now.get("orig", "") != r["orig"]:
                p["skip"][k] = "orig-changed"  # 被重新切段：舊 order_index 已不是這段原文
                continue
            if now.get("zh"):
                if not classify(now.get("orig", ""), now["zh"]):
                    p["done"][k] = "external"
                    continue
                # 別的流程又寫進壞譯文：不刪別人的，記下來
                p["skip"][k] = "bad-zh-written-by-other"
                continue
            todo.append(r)
        save_progress(p)
        # 分批
        batches, cur_b, cur_len = [], [], 0
        for r in todo:
            L = len(r["orig"])
            if cur_b and (cur_len + L > BATCH_CHARS or len(cur_b) >= BATCH_N):
                batches.append(cur_b)
                cur_b, cur_len = [], 0
            cur_b.append(r)
            cur_len += L
        if cur_b:
            batches.append(cur_b)
        print(f"[entry {eid}] {(entry.get('title') or '')[:50]} ｜ {ctx_name} ｜ {len(todo)} 段 {len(batches)} 批",
              flush=True)
        stack = list(reversed(batches))
        while stack:
            if t_end and time.time() > t_end:
                break
            batch = stack.pop()
            body = "\n\n".join(f"⟦{i + 1}⟧\n{r['orig']}" for i, r in enumerate(batch))
            prompt = PROMPT.format(title=entry.get("title") or "", authors=entry.get("authors") or "",
                                   context=f"{ctx_name}；主題：{entry.get('theme') or ''}",
                                   naming=naming, glossary=gloss, body=body)
            try:
                out, eng = call_chain(prompt)
            except EngineDown as e:
                engine_errors += 1
                print(f"  ! engine down ({engine_errors}): {e}", flush=True)
                if engine_errors >= 3:
                    print("[stop] 三個引擎連續失敗；未完成，不印完成標記", flush=True)
                    save_progress(p)
                    return 2
                time.sleep(120)
                stack.append(batch)
                continue
            engine_errors = 0
            pieces = split_marked(out.strip(), len(batch))
            if pieces is None:
                if len(batch) > 1:
                    print(f"  · 批次標記對不上（{eng}）→ 拆成單段", flush=True)
                    for r in reversed(batch):
                        stack.append([r])
                    continue
                pieces = [_MARK_RE.sub("", out).strip()]
            rows_ok = []
            for r, z in zip(batch, pieces):
                k = keyof(eid, r["order_index"])
                z = tf.strip_fffd(z) or z
                why = gate(z, r["orig"])
                if why:
                    p["fail"][k] = p["fail"].get(k, 0) + 1
                    print(f"  ✗ #{r['order_index']} gate={why} ({eng}) 第 {p['fail'][k]} 次：{z[:40]!r}", flush=True)
                    if p["fail"][k] >= MAX_GATE_FAIL:
                        p["dead"][k] = why
                    elif len(batch) > 1:
                        stack.insert(0, [r])  # 之後單段重試
                    else:
                        stack.insert(0, [r])
                    continue
                rows_ok.append((r, z, eng))
            if rows_ok:
                payload = [{"entry_id": eid, "version_code": "zh", "order_index": r["order_index"],
                            "text": z, "char_count": len(z)} for r, z, _ in rows_ok]
                resp = requests.post(
                    f"{URL}/rest/v1/lit_review_sections?on_conflict=entry_id,version_code,order_index",
                    headers={**H, "Prefer": "resolution=merge-duplicates,return=minimal"},
                    data=json.dumps(payload), timeout=120)
                resp.raise_for_status()
                for r, z, e in rows_ok:
                    p["done"][keyof(eid, r["order_index"])] = e
                print(f"  ✓ {len(rows_ok)} 段（{eng}）#{','.join(str(r['order_index']) for r, _, _ in rows_ok)}"
                      f" ｜ 累計補 {len(p['done'])}", flush=True)
            save_progress(p)
            time.sleep(args.pace)
    # 結算
    left = 0
    for r in rows:
        k = keyof(r["entry_id"], r["order_index"])
        if k not in p["done"] and k not in p["skip"] and k not in p["dead"]:
            left += 1
    print(f"[end] {time.strftime('%m-%d %H:%M')} 已補 {len(p['done'])}、留白 {len(p['skip'])}、"
          f"放棄 {len(p['dead'])}、剩 {left}", flush=True)
    if left == 0:
        print(DONE_MARKER, flush=True)
    return 0


def cmd_status(args) -> None:
    rows = json.loads(BACKUP.read_text(encoding="utf-8"))["rows"]
    p = load_progress()
    ks = {keyof(r["entry_id"], r["order_index"]) for r in rows}
    done = ks & set(p["done"])
    print(f"清空 {len(ks)}；已補 {len(done)}（{dict(collections.Counter(p['done'][k] for k in done))}）；"
          f"留白 {len(ks & set(p['skip']))}（{dict(collections.Counter(p['skip'][k] for k in ks & set(p['skip'])))}）；"
          f"放棄 {len(ks & set(p['dead']))}；"
          f"剩 {len(ks - set(p['done']) - set(p['skip']) - set(p['dead']))}")


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan")
    s.add_argument("--refresh", action="store_true")
    s.add_argument("--samples", type=int, default=30)
    s.add_argument("--seed", type=int, default=7)
    c = sub.add_parser("clear")
    c.add_argument("--dry-run", action="store_true")
    r = sub.add_parser("run")
    r.add_argument("--max-minutes", type=float, default=0)
    r.add_argument("--pace", type=float, default=1.0)
    sub.add_parser("status")
    a = ap.parse_args()
    if a.cmd == "scan":
        cmd_scan(a)
    elif a.cmd == "clear":
        cmd_clear(a)
    elif a.cmd == "run":
        return cmd_run(a)
    else:
        cmd_status(a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
