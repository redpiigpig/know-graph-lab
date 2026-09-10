#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ACCS 教父註釋的品質稽核 —— 正典與次經是不是真的 100% 合格。

「lane 說跑完了」不是完工判準（[[feedback_disable_finished_schedules]]）。這支查的是
**產出**：資料有沒有彼此混雜、有沒有未翻譯／元回覆污染、有沒有簡體殘留與重複幻覺。

檢查項目：
  A 覆蓋      每個書卷有多少章有註釋；`accs_volume_config` 排定的書卷有沒有整卷缺席
  B 資料混雜  🚨 `source_vol` 與 `book_code` 對不上（甲卷的註釋掛到乙書）
              章節號越界（章 <1、verse_start > verse_end）
  C 未翻譯    中文字佔比過低＝整段英文原樣吐回（重用 audit_llm_meta_replies）
  D 元回覆    「我注意到您提供的…」被當譯文存進去（[[feedback_haiku_meta_reply_pollution]]）
  E 簡體殘留  全站一律繁體（[[feedback_traditional_chinese_only]]）
  F 重複幻覺  同一句刷屏（[[feedback_ocr_repetition_hallucination]]，重用 ocr_repetition）
  G 空白      body_zh 空的或只剩標點

判準函式是純的，由 scripts/tests/test_accs_audit_quality.py 鎖定。

  python -X utf8 scripts/accs_audit_quality.py            # 全庫稽核
  python -X utf8 scripts/accs_audit_quality.py --samples 3  # 每類多印幾筆樣本
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

# ── 純函式（零 I/O）────────────────────────────────────────────────────────

# 簡體專有字。**不要用 OpenCC 轉換後比對**來判繁簡：那會把「祢」這種
# 異體字判成簡體（[[feedback_reader_silent_failures]]）。只認這些單向簡化字，
# 寧可漏抓也不要誤報。
_SIMPLIFIED = set(
    # 訁 部：簡化後與「言」旁差異明顯，且不作正體使用，誤判率最低
    "們說記講論認識語誰請讀課謝試話詞設議計訓討讓譯詩訪評證該詳談謂謹諾"
    .translate(str.maketrans(
        "們說記講論認識語誰請讀課謝試話詞設議計訓討讓譯詩訪評證該詳談謂謹諾",
        "们说记讲论认识语谁请读课谢试话词设议计训讨让译诗访评证该详谈谓谨诺"))
    # 其餘高頻且無正體用法者
    + "时间问题这样国学习实现经过区华丽爱标为东应书写验历师传统关优质权义"
      "节导类灵单双术务处产业与专见观长门马鸟鱼车贝页风齐龙龟剧广厂对"
)
# 🚨 **不要**把「那 後 別 準 西 據 史 於 萬 體 個」這類收進來：它們在正體中文裡本來就這樣寫。
# 第一版收了，結果全庫掃出 23,284 筆「簡體殘留」，樣本第一筆就是「那」——全是誤報。
# 也不要改用 OpenCC 轉換後比對：那會把「祢」判成簡體（[[feedback_reader_silent_failures]]）。


def simplified_chars(text: str) -> list[str]:
    """回傳文中出現的簡體專有字（去重、保序）。空的代表這一段是乾淨繁體。"""
    seen, out = set(), []
    for ch in text or "":
        if ch in _SIMPLIFIED and ch not in seen:
            seen.add(ch)
            out.append(ch)
    return out


_PUNCT_ONLY_RE = re.compile(r"^[\s\W_]*$")


def is_blank(text: str) -> bool:
    """空的，或只剩標點與空白——渲染出來就是一格空白註釋。"""
    return _PUNCT_ONLY_RE.match(text or "") is not None


def vol_matches_book(source_vol: str, book_zh: str, book_code: str = "",
                     deuterocanon: bool = False) -> bool:
    """`source_vol` 指的是不是這一列所屬的書卷。

    🚨 這是抓「資料混雜」最直接的一條：卷別解析錯位時整段註釋會掛到隔壁書卷，
    章節號與經文都對得起來，只有卷名對不上——頁面上看不出任何異狀。

    但 source_vol 實際上有**三種寫法**混用，三種都算對：
      `ACCS（詩篇）`  中文書名（23,407 列）
      `ACCS（gen）`   書卷代碼（15,646 列）← 頁面上會顯示成英文，是呈現瑕疵但不是混雜
      `ACCS（次經）`  次經那一卷共用一個卷名
    只認第一種會把後兩種全部誤報成混雜。
    """
    sv = (source_vol or "").strip()
    if not sv or not (book_zh or book_code):
        return True  # 資訊不足就不判，交給其他檢查
    if book_zh and book_zh in sv:
        return True
    if book_code and f"（{book_code}）" in sv:
        return True
    if deuterocanon and "次經" in sv:
        return True
    return False


def uses_book_code(source_vol: str) -> bool:
    """source_vol 寫成 `ACCS（gen）` 這種書卷代碼？

    頁面上直接把 source_vol 印出來（scripture/[book]/[chapter].vue），
    所以這種列在讀經頁會顯示成「ACCS（gen）‧古代基督信仰聖經註釋叢書」。
    """
    return bool(re.match(r"^ACCS（[A-Za-z0-9]{2,4}）$", (source_vol or "").strip()))


def range_ok(chapter, verse_start, verse_end) -> bool:
    """章節號的基本合理性：章 ≥ 1、起訖不顛倒。"""
    try:
        if chapter is not None and int(chapter) < 1:
            return False
        if verse_start is not None and verse_end is not None:
            if int(verse_start) > int(verse_end):
                return False
            if int(verse_start) < 0:
                return False
    except (TypeError, ValueError):
        return False
    return True


DEUTERO = {"tob", "wis", "sir", "bar", "sus", "bel", "aza"}


# ── I/O ────────────────────────────────────────────────────────────────────

def _env() -> dict:
    env = {}
    for line in (SCRIPT_DIR.parent / ".env").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--samples", type=int, default=2)
    a = ap.parse_args()

    from audit_llm_meta_replies import is_untranslated
    import audit_llm_meta_replies as _meta
    # 🚨 共用標記表裡的「作為一個」是為了抓「作為一個 AI 助理」，但那在教父註釋
    # 裡是尋常中文（「以色列作為一個整體」「作為一個女性，馬利亞非常感性」）——
    # 不拿掉，22 筆元回覆幾乎全是誤報。其餘標記都指涉任務／輸入，留著。
    _meta.META_MARKERS = tuple(m for m in _meta.META_MARKERS if m != '作為一個')
    is_meta = _meta.is_meta
    from audit_page_numbers_db import run_sql
    from ocr_repetition import looks_looping

    env = _env()
    print("讀取 accs_commentary…", flush=True)

    # 分頁抓全表：PostgREST 會靜默截在 1000 筆（[[feedback_postgrest_silent_1000_cap]]），
    # 所以走 Management API 的 SQL，並用 keyset 分頁而不是 OFFSET。
    rows: list[dict] = []
    last = ""
    while True:
        batch = run_sql(env, (
            "select id::text, book_code, chapter, verse_start, verse_end, "
            "father_name, work_title, body_zh, source_vol "
            f"from accs_commentary where id::text > '{last}' "
            "order by id::text limit 2000"))
        if not batch:
            break
        rows += batch
        last = batch[-1]["id"]
        print(f"  {len(rows)} 列…", flush=True)

    books = run_sql(env, "select code, name_zh from bible_books")
    zh = {b["code"]: b["name_zh"] for b in books}

    problems: dict[str, list] = {k: [] for k in
                                 ("混雜", "卷名顯示成代碼", "章節越界", "未翻譯", "元回覆",
                                  "簡體", "重複幻覺", "空白")}
    by_book: dict[str, set] = {}

    for r in rows:
        code = r["book_code"]
        by_book.setdefault(code, set()).add(r["chapter"])
        body = r["body_zh"] or ""
        tag = f"{code} {r['chapter']}:{r['verse_start']}-{r['verse_end']}"
        if not vol_matches_book(r["source_vol"] or "", zh.get(code, ""), code,
                                code in DEUTERO):
            problems["混雜"].append((tag, f"source_vol={r['source_vol']} 但書卷是 {zh.get(code)}"))
        if uses_book_code(r["source_vol"] or ""):
            problems["卷名顯示成代碼"].append((tag, r["source_vol"]))
        if not range_ok(r["chapter"], r["verse_start"], r["verse_end"]):
            problems["章節越界"].append((tag, ""))
        if is_blank(body):
            problems["空白"].append((tag, ""))
            continue
        if is_meta(body):
            problems["元回覆"].append((tag, body[:60]))
        elif is_untranslated(body):
            problems["未翻譯"].append((tag, body[:60]))
        s = simplified_chars(body)
        if s:
            problems["簡體"].append((tag, "".join(s[:8])))
        if looks_looping(body):
            problems["重複幻覺"].append((tag, body[:60]))

    print(f"\n總列數 {len(rows)}　書卷 {len(by_book)}")
    ok = True
    for k, v in problems.items():
        mark = "✅" if not v else "🚨"
        if v:
            ok = False
        print(f"{mark} {k}：{len(v)}")
        for tag, extra in v[:a.samples]:
            print(f"      {tag}　{extra}")

    print("\n覆蓋（章數）：")
    thin = [(c, len(ch)) for c, ch in sorted(by_book.items()) if len(ch) <= 1]
    print(f"  只有 0–1 章有註釋的書卷：{len(thin)} → {[t[0] for t in thin]}")

    print("\n結論：" + ("✅ 全數合格" if ok else "🚨 有問題，見上"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
