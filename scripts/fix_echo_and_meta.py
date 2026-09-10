# -*- coding: utf-8 -*-
"""清掉譯文欄裡的三種殘渣：原文回抄、引擎的拒譯回覆、傍點行。

三種都有同一個特徵——**頁面完全正常**，reader 照排，只有讀的人會發現中文欄裡
是日文。2026-09-09 全庫掃出 160 段假名外洩，《基督信徒的慰藉》一本就有 13 段。

  echo   引擎把原文抄一遍再接譯文（「五、汝今衣食を…、 五、你如今為衣食…」）。
         正解是切掉前面那一段回抄。切點取**最後一段連續的日文**之後——不能只找
         原文字串，因為引擎常把原文重寫過（「いかなれば艱難におる者に」抄成
         「何ぞ患難に在る者に」）。
  meta   引擎不翻，改用對話語氣回「申し訳ありませんが…英文です」。這種一律留白，
         不硬翻（[[feedback_haiku_meta_reply_pollution]]：硬翻會生出更難查的錯）。
  bouten 青空文庫的傍点（ヽヽヽ）自成一行。那不是文字，是排版記號，原樣保留。

🚨 **不可一律砍掉譯文裡的日文**。有些段落在**討論**日文詞本身（「馬可傳一章十二節
   『往かしめし』は英語の Driveth…」），那裡的假名是引文，砍掉就毀了那一句。
   判準：假名出現在引號／括號裡就留著。

  python -X utf8 scripts/fix_echo_and_meta.py --author uchimura --work consolations --dry
  python -X utf8 scripts/fix_echo_and_meta.py --author uchimura --work consolations --apply
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KANA = re.compile(r"[ぁ-ゟ゠-ヿ]")
BOUTEN = re.compile(r"^[ヽヾ゛゜\s]+$")

# 拒譯回覆：對話語氣＋談翻譯任務本身，兩個條件同時成立才算
# （只看語氣會誤殺正文——「我已準備妥當，要往耶路撒冷去」被丟掉過）。
_META_TONE = re.compile(r"申し訳|恐れ入り|お応えできません|ご提供ください|"
                        r"我注意到您|您提供的|您未提供|請提供|請貼上|I'm sorry|I cannot")
_META_TASK = re.compile(r"翻訳|翻譯|テキスト|原文|日文|英文|translate")

# 假名被引號或括號包住＝正文在討論那個日文詞，不是沒翻
_QUOTED_KANA = re.compile(r"[「『（(\"'][^」』）)\"']*[ぁ-ゟ゠-ヿ][^」』）)\"']*[」』）)\"']")


def is_meta_reply(zh: str) -> bool:
    """譯文欄裝的是引擎的拒絕回覆嗎？"""
    z = zh or ""
    return bool(_META_TONE.search(z) and _META_TASK.search(z))


# 回抄後面那一段譯文，至少要有原文的這個比例長，才算「一段完整的譯文」。
# 🚨 沒有這道閘，「翻一半」會被誤判成回抄而**截斷**：
#    「獨逸國に生れたる世界の市民」→ 只剩「市民」
#    「我信那或是死…或是今ある者…都不能叫我們與神的愛隔絕」→ 只剩最後半句。
#    截斷比留著日文更糟——頁面一樣正常，但內容真的少了。
MIN_TAIL_RATIO = 0.4


def tail_after_last_kana(zh: str) -> str:
    """最後一個假名之後的那一段（去掉開頭黏著的標點與分隔線）。"""
    z = (zh or "").strip()
    if not KANA.search(z):
        return z
    last = max(m.start() for m in KANA.finditer(z))
    tail = z[last + 1:]
    m = re.search(r"[一-鿿]", tail)
    if not m:
        return ""
    return re.sub(r"^[\s、。，,\-—―─]+", "", tail[m.start():]).strip()


def strip_kana_echo(zh: str, src: str = "") -> str:
    """切掉「原文回抄 ＋ 譯文」裡的回抄那一段。

    作法是從尾巴往前找**最後一個假名**，之後的第一個中文字起算就是譯文。
    引擎的回抄常經過重寫（「いかなれば艱難におる者に」抄成「何ぞ患難に在る者に」），
    所以不能拿原文去比對字串——但可以拿原文比**長度**，見 MIN_TAIL_RATIO。"""
    z = (zh or "").strip()
    tail = tail_after_last_kana(z)
    if not tail or (src and len(tail) < MIN_TAIL_RATIO * len(src)):
        return z
    return tail


def classify(src: str, zh) -> str:
    """一段 → 要做什麼：meta / bouten / echo / partial / ok。純函式。

    partial＝譯文裡夾著假名、但後半不足以獨立成篇。那是「翻一半」，
    只能重譯或人工補，**不可自動切**。"""
    if BOUTEN.match(src or ""):
        return "bouten"
    if zh and is_meta_reply(zh):
        return "meta"
    if zh and KANA.search(zh) and not _QUOTED_KANA.search(zh):
        if strip_kana_echo(zh, src) != zh.strip():
            return "echo"
        return "partial"
    return "ok"


def repair(src: str, zh):
    """一段 → 修好的譯文（或 None 表示留白）。partial 原樣退回，交給人。"""
    kind = classify(src, zh)
    if kind == "bouten":
        return src                      # 排版記號原樣保留
    if kind == "meta":
        return None                     # 留白，不硬翻
    if kind == "echo":
        return strip_kana_echo(zh, src)
    return zh


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--author", default="uchimura")
    ap.add_argument("--work", required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    import uchimura_auto as ua
    ua.use_author(args.author)
    data_root = SCRIPT_DIR.parent / ".claude" / "skills" / "ebook-collected-works" / \
        getattr(ua.ub, "DATA_DIRNAME", "uchimura_data")

    tally = {}
    for i in range(len(ua.ub.load_work_sections(args.work))):
        cp = data_root / args.work / f"sec{i}.json"
        if not cp.exists():
            continue
        c = json.loads(cp.read_text(encoding="utf-8"))
        src, zh = c.get("src") or [], c.get("zh") or []
        touched = False
        for j, (s, z) in enumerate(zip(src, zh)):
            kind = classify(s, z)
            if kind == "ok":
                continue
            tally[kind] = tally.get(kind, 0) + 1
            new = repair(s, z)
            print(f"  {kind:6} sec{i}[{j}]")
            print(f"         舊 {str(z)[:90]}")
            print(f"         新 {str(new)[:90]}")
            if args.apply:
                zh[j] = new
                touched = True
        if touched:
            c["zh"] = zh
            cp.write_text(json.dumps(c, ensure_ascii=False, indent=1), encoding="utf-8")

    print("\n" + ("已修" if args.apply else "可修") + "：" +
          "、".join(f"{k} {v} 段" for k, v in tally.items()) or "沒有要修的")
    if not args.apply:
        print("加 --apply 才會真的寫入")


if __name__ == "__main__":
    main()
