#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""稽核「LLM 把拒譯說明當成譯文存進去」這一類污染，可選擇清成空白。

為什麼需要這支
--------------
Haiku 遇到它判定「不是英文／是亂碼」的來源時**不會回空**，而是回一段中文說明：

    我注意到您提供的「英文原文」實際上是梵文文本（使用 IAST 音譯法），而非英文。
    我無法完成這個翻譯任務，因為提供的英文原文……

管線把那段說明當成譯文存進 `zh[i]`。於是段數對得齊、覆蓋率 100%、品質分數正常——
只有真的去讀內容才看得出來，是最典型的「看起來成功的失敗」。

2026-09-08 首次全掃 `mueller_data`：**49,554 段裡 2,001 段（4.04%）是元回覆**，
而且已經上線（阿維斯陀 266 段 DB preview 裡 32 段開頭就是）。重災區
`sbe-04-zend-avesta-1` 10.7%、`auld-lang-syne` 10.0%、`comparative-mythology` 8.9%。

三類污染
--------
1. **元回覆**（META）：譯文開頭是 LLM 在跟你說話，不是譯文。判準看開頭 40 字。
   🚨 中英文都要掃——`I'm ready to translate the English text from…` 一樣是元回覆。
2. **整段未翻譯**（RAW-EN）：LLM 把英文原文原樣吐回來。判準是中文字佔比 <5%。
3. **臆造**（HALLU）：來源極短、譯文卻長好幾倍。`Introduction.` 一個字生出一整段導論；
   `140 LECTURE in.`（書眉）生出 1,118 字的講稿；`Bastholm ........`（索引行）生出
   1,575 字的虛構章節。這一類是啟發式判斷，`--meta-only` 會保留它們待人工看過。

清成空白為什麼是對的
--------------------
高發來源是**被 OCR 打爛的梵文／阿維斯陀轉寫**與**書眉**（`Ixx THE QUR'AN.`、
`xl DHAMMAPADA.`）。這種來源本來就沒有可譯的內容，硬翻只會得到錯譯——
`Ixxx THE QURAN.` → 「第十章《古蘭經》」（lxxx 是頁碼不是章號）。留白時 reader
只顯示英文，那是誠實的；留著錯譯則是靜默的錯誤。要補譯請走 Gemini，別再用 Haiku。

用法
----
    python scripts/audit_llm_meta_replies.py                    # 全掃，只報告
    python scripts/audit_llm_meta_replies.py --root mueller_data
    python scripts/audit_llm_meta_replies.py --samples 5        # 每本印幾筆樣本
    python scripts/audit_llm_meta_replies.py --fix              # 把命中的清成空白
    python scripts/audit_llm_meta_replies.py --fix --meta-only  # 只清元回覆，留臆造

`--fix` 會就地改寫 sec*.json 的 `zh[i]`，改完**不會自動上傳**——上傳是整本重寫，
清完一次再上傳一次比較省。上傳路徑見各 driver（🚨 sbe-* 在 sbe_translate.WORKS，
不在 mueller_auto.WORKS，用錯會 KeyError）。
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CW = ROOT / ".claude" / "skills" / "ebook-collected-works"

# 開頭 40 字內出現就算——LLM 的拒譯說明一律是開場白，不會埋在中段。
# 放寬到全文會誤傷正常譯文（經文裡本來就有「我無法……」這種句子）。
META_MARKERS = (
    "我注意到", "我無法翻譯", "我無法完成", "您提供的", "請提供",
    "我需要澄清", "我很遺憾", "並非英文", "不是英文", "似乎不是",
    "抱歉", "作為一個", "無法進行翻譯", "這段文字似乎",
    # 🚨 元回覆不一定是中文。2026-09-08 抽樣抓到 "I'm ready to translate the
    # English text from…" 與 "I appreciate your detailed instructions, but I
    # notice…" 被當成譯文存著——只掃中文標記會整批漏掉。
    "I'm ready to", "I am ready to", "I appreciate your", "I notice",
    "I apologize", "I cannot translate", "I can't translate", "I'm unable to",
    "As an AI", "It appears that the", "The text you provided",
    "Please provide", "I need to clarify",
    # 🚨 第二批（2026-09-08 15:20 清完四小時後又長回 35 段時補的）。挑選原則是
    # **只收指涉「任務／輸入」的字串，不收指涉題材的**——這批書本身就在談語言學，
    # 光憑「英文」「原文」這種詞會誤殺真譯文（science-language 整本都在講英文字源）。
    # 下面每一條都是模型在跟你說話才會出現的講法。
    "提供的英文", "提供的文本", "提供的原文", "您給的", "你提供",
    "無法提供準確翻譯", "無法進行準確", "無法提供翻譯",
    "我在提供的", "我需要指出", "這段文字似乎", "似乎是亂碼",
    "非標準拼寫", "似乎不完整", "看起來是梵文", "而非英文",
)
META_WINDOW = 40

# 臆造判準：來源短、譯文卻長很多。中文比英文短是常態，反過來就不對。
#
# 🚨 `HALLU_MIN_OUT` 從 30 提到 120 是實測改的：`Saranyu=Erinuys, 73.`（20 字）
# 譯成「薩蘭尤（Saranyu）= 厄里倪厄斯（Erinuys），第73頁。」（34 字）是**正確譯文**，
# 只是中文音譯加括號本來就會變長。真正的臆造抽樣全部落在 334–2,280 字，
# 門檻放在 120 就乾淨切開。誤刪真譯文比漏掉一段臆造糟。
HALLU_SRC_MAX = 45
HALLU_RATIO = 1.6
HALLU_MIN_OUT = 120

# 整段沒翻譯：LLM 直接把英文原文吐回來（抽樣抓到 2,280 字的 "Magic and
# Witchcraft, though often confounded with Religion…"）。中文字佔比極低即是。
UNTRANSLATED_MIN_LEN = 80
UNTRANSLATED_CJK_RATIO = 0.05


def _cjk_ratio(s: str) -> float:
    if not s:
        return 0.0
    return sum(1 for c in s if "一" <= c <= "鿿") / len(s)


def is_untranslated(zh: str) -> bool:
    return (len(zh) >= UNTRANSLATED_MIN_LEN
            and _cjk_ratio(zh) < UNTRANSLATED_CJK_RATIO)


def is_meta(zh: str) -> bool:
    head = zh[:META_WINDOW]
    return any(m in head for m in META_MARKERS)


def is_hallucinated(en: str, zh: str) -> bool:
    return (len(en) < HALLU_SRC_MAX
            and len(zh) > len(en) * HALLU_RATIO
            and len(zh) > HALLU_MIN_OUT)


def scan_sec_file(path: str) -> list[tuple[int, str, str, str]]:
    """回傳 [(index, kind, en, zh)]。讀不動的檔案跳過而不是炸掉整輪。"""
    try:
        j = json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError):
        return []
    if not isinstance(j, dict):
        return []
    zh_l = j.get("zh") or []
    en_l = j.get("en") or []
    out = []
    for i in range(len(zh_l)):
        zh = (zh_l[i] or "").strip()
        if not zh:
            continue
        en = ((en_l[i] if i < len(en_l) else "") or "").strip()
        if is_meta(zh):
            out.append((i, "META", en, zh))
        elif is_untranslated(zh):
            out.append((i, "RAW-EN", en, zh))
        elif en and is_hallucinated(en, zh):
            out.append((i, "HALLU", en, zh))
    return out


def fix_sec_file(path: str, hits: list[tuple[int, str, str, str]], meta_only: bool) -> int:
    j = json.load(open(path, encoding="utf-8"))
    zh_l = j["zh"]
    n = 0
    # meta_only＝只清判準明確的兩類（元回覆、整段沒翻譯），保留啟發式的 HALLU。
    SURE = ("META", "RAW-EN")
    for i, kind, _en, _zh in hits:
        if meta_only and kind not in SURE:
            continue
        zh_l[i] = ""
        n += 1
    if n:
        j["zh"] = zh_l
        json.dump(j, open(path, "w", encoding="utf-8"), ensure_ascii=False)
    return n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="", help="只掃某個 *_data（例：mueller_data）")
    ap.add_argument("--fix", action="store_true", help="把命中的 zh 清成空白")
    ap.add_argument("--meta-only", action="store_true",
                    help="只清判準明確的（元回覆＋整段未翻譯），保留啟發式的疑似臆造")
    ap.add_argument("--samples", type=int, default=2, help="每本印幾筆樣本")
    a = ap.parse_args()

    roots = [d for d in sorted(CW.glob("*_data")) if d.is_dir()]
    if a.root:
        roots = [d for d in roots if d.name == a.root]
        if not roots:
            print(f"找不到 {a.root}")
            return 2

    grand = collections.Counter()
    fixed_total = 0
    print(f"{'書':<34}{'元回覆':>7}{'未翻譯':>7}{'臆造':>7}{'有譯文':>9}   佔比")
    for root in roots:
        for book in sorted(os.listdir(root)):
            bp = root / book
            if not bp.is_dir():
                continue
            hits_by_file: dict[str, list] = {}
            total_zh = 0
            for s in sorted(glob.glob(str(bp / "sec*.json"))):
                try:
                    j = json.load(open(s, encoding="utf-8"))
                    total_zh += sum(1 for z in (j.get("zh") or []) if (z or "").strip())
                except (OSError, ValueError):
                    pass
                h = scan_sec_file(s)
                if h:
                    hits_by_file[s] = h
            n_meta = sum(1 for h in hits_by_file.values() for x in h if x[1] == "META")
            n_raw = sum(1 for h in hits_by_file.values() for x in h if x[1] == "RAW-EN")
            n_hal = sum(1 for h in hits_by_file.values() for x in h if x[1] == "HALLU")
            if not (n_meta or n_raw or n_hal):
                continue
            grand["meta"] += n_meta
            grand["raw"] += n_raw
            grand["hallu"] += n_hal
            grand["zh"] += total_zh
            pct = (n_meta + n_raw + n_hal) / total_zh * 100 if total_zh else 0
            print(f"  {root.name}/{book:<24}"[:34].ljust(34)
                  + f"{n_meta:>7}{n_raw:>7}{n_hal:>7}{total_zh:>9}   {pct:5.1f}%")
            shown = 0
            for s, h in hits_by_file.items():
                for i, kind, en, zh in h:
                    if shown >= a.samples:
                        break
                    print(f"      [{kind}] {os.path.basename(s)}#{i}  en={en[:40]!r}")
                    print(f"             zh={zh[:60]!r}")
                    shown += 1
                if shown >= a.samples:
                    break
            if a.fix:
                for s, h in hits_by_file.items():
                    fixed_total += fix_sec_file(s, h, a.meta_only)

    tz = grand["zh"] or 1
    total_bad = grand["meta"] + grand["raw"] + grand["hallu"]
    print(f"\n合計：元回覆 {grand['meta']}、整段未翻譯 {grand['raw']}、"
          f"疑似臆造 {grand['hallu']}"
          f"（受影響書的有譯文段共 {grand['zh']}，{total_bad / tz * 100:.2f}%）")
    if a.fix:
        print(f"已清成空白 {fixed_total} 段"
              f"{'（只清判準明確的兩類）' if a.meta_only else ''}")
        print("🚨 尚未上傳。清完要重新 assemble_and_upload 才會反映到站上。")
    else:
        print("（只報告；要清請加 --fix）")
    return 1 if total_bad else 0


if __name__ == "__main__":
    sys.exit(main())
