#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《神的歷史》OCR 錯字修正（2026-10-01，使用者核准三批全改）。

原書是簡體版低解析 1-bit 掃描，站上繁體是「簡體 OCR → 簡轉繁」，錯有兩個來源：
形近誤讀（撒/撤、士/土、入/人、己/已）與簡轉繁過度轉換（音譯的「里」→「裡」、
念→唸、征→徵、干→幹、面→麵）。稽核表見 output/god_history_ocr_audit.md。

改三處（成品放多處要一起更新）：Drive JSONL 正本、R2 衍生物、Drive「分章朗讀」13 個
docx（就地改命中字，不從 JSONL 重建覆蓋；有 ~$ 鎖檔就不動）。

🚨「人／入」一類不能盲換：「促進人類」會被「進人→進入」改壞。所以這類規則帶
排除條件，而且 --dry-run 會逐處印上下文，看過才跑 --apply。

以下是原書影像核過、**原書就這樣印**而不改的：芋海（譯者把 Yam 直譯成芋）、
腹中儉陋、滬德(Hud)、寒魯羅(Cerullo)、「某些深人聚集」(p.277)。

  python -X utf8 scripts/fix_god_history_ocr.py --dry-run
  python -X utf8 scripts/fix_god_history_ocr.py --apply
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

EBOOK_ID = "1b974fa3-88a6-4f10-974e-9b32400af433"
JSONL = Path(rf"G:\我的雲端硬碟\資料\知識圖工作室\_chunks\{EBOOK_ID}.jsonl")
DOCX_DIR = Path(r"G:\我的雲端硬碟\神的歷史\神的歷史（分章朗讀）")

# (pattern, replacement, risky)。依序套用；特例在前。pattern 是 regex。
RULES: list[tuple[str, str, bool]] = [
    # ── 特例（兩個錯疊在一起）
    (r"融入入性", "融入人性", False),
    (r"進人入", "進入", False),
    # ── 專名：形近
    (r"亞[裡果][士土上1七]多德", "亞里士多德", False),
    (r"耶路撤冷", "耶路撒冷", False),
    (r"撤巴臺", "撒巴臺", False),
    (r"撤旦", "撒旦", False),
    (r"拿撤勒", "拿撒勒", False),
    (r"以撤出發", "以撒出發", False),
    (r"瑞土", "瑞士", False),
    (r"博佩榮", "傅佩榮", False),
    (r"耶纖", "耶穌", False),
    (r"仟悔錄", "懺悔錄", False),
    (r"拉廠文", "拉丁文", False),
    (r"人土學習", "人士學習", False),
    # ── 專名：音譯的「里」被簡轉繁成「裡」（使用者核准一律改回「里」）
    (r"哈裡發", "哈里發", False),
    (r"格裡高利|格里高裡", "格里高利", False),
    (r"歐幾裡德", "歐幾里德", False),
    (r"阿裡烏", "阿里烏", False),
    (r"安薩裡", "安薩里", False),
    (r"阿沙裡", "阿沙里", False),
    (r"鮑遜姆裡", "鮑遜姆里", False),
    (r"溫斯坦裡", "溫斯坦里", False),
    (r"沙裡阿", "沙里阿", False),
    (r"聶斯托裡", "聶斯托里", False),
    (r"艾裡(?=[札亞])", "艾里", False),
    (r"弗裡幾亞", "弗里幾亞", False),
    (r"凱撒裡亞", "凱撒里亞", False),
    (r"卡拉布裡亞", "卡拉布里亞", False),
    (r"薩裡(?=\s*[(（]Sal)", "薩里", False),   # Salih；原書「萨里」
    # ── 一般詞：形近
    (r"自已", "自己", False),
    (r"白己", "自己", False),
    (r"它白身", "它自身", False),
    (r"持已見", "持己見", False),
    (r"神衹", "神祇", False),
    (r"字宙", "宇宙", False),
    (r"宇面", "字面", False),
    (r"文宇", "文字", False),
    (r"水恆", "永恆", False),
    (r"間題", "問題", False),
    (r"祟拜", "崇拜", False),
    (r"頤抖", "顫抖", False),
    (r"柑比", "相比", False),
    (r"蹂蹢", "蹂躪", False),
    (r"眈耽", "眈眈", False),
    (r"浩翰", "浩瀚", False),
    (r"哆嘯", "哆嗦", False),
    (r"円素", "元素", False),
    (r"叮哼", "叮嚀", False),
    (r"違揹", "違背", False),
    (r"更槽", "更糟", False),
    (r"於涸", "乾涸", False),
    (r"榨於", "榨乾", False),
    (r"一殷被稱", "一般被稱", False),
    (r"丙為它", "因為它", False),
    (r"僅仁", "僅有", False),
    (r"黃鍋", "黃銅", False),
    (r"鹼海", "鹹海", False),          # Tiamat 鹹水；原書「咸海」
    (r"“禰”", "“祢”", False),
    # ── 一般詞：簡轉繁過度轉換
    (r"(?<=[觀概懸])唸", "念", False),   # 「誦唸」合法，不動
    (r"東徵", "東征", False),
    (r"關系", "關係", False),
    (r"麵積", "面積", False),
    (r"兼容幷蓄", "兼容並蓄", False),
    (r"被髮現", "被發現", False),
    (r"斷髮出", "斷發出", False),
    (r"傢伙伴", "家夥伴", False),       # 原書「神学家伙伴」
    (r"幹(?=[預涉擾])", "干", False),
    # ── 人→入（有誤傷風險：逐處看）
    (r"(?<![引促增激])進人(?![類民口才員])", "進入", True),   # 激進人士
    (r"融人", "融入", True),
    (r"(?<!麥)加人(?![口數類])", "加入", True),
    (r"陷人(?![於])", "陷入", True),
    (r"(?<![一攜])帶人(?![民])", "帶入", True),
    (r"投人", "投入", True),
    (r"納人", "納入", True),
    (r"注人", "注入", True),
    (r"推人(?![及])", "推入", True),
    (r"滲人", "滲入", True),
    (r"介人", "介入", True),
    (r"轉人地下", "轉入地下", True),
    (r"插人", "插入", True),
    (r"溶人", "溶入", True),
    (r"證人涅槃", "證入涅槃", True),
    (r"排人祠", "排入祠", True),
    (r"丟人的焚", "丟入的焚", True),
    (r"關人布", "關入布", True),
    (r"引人人勝", "引人入勝", True),
    (r"放人《", "放入《", True),
    (r"流人，", "流入，", True),
    (r"吸人", "吸入", True),
    (r"(?<!某些)深人", "深入", True),
    # ── 入→人
    (r"(?<![納歸融進])入類", "人類", True),
    (r"(?<![進融納])入們", "人們", True),
    (r"(?<=[猶詩窮男女])入(?![侵])", "人", True),   # 猶太入／詩入／窮入／男入／女入
    (r"(?<=猶太)入", "人", True),
    (r"擬入化", "擬人化", True),
    (r"(?<=[伯方他])入(?=[這傾則])", "人", True),   # 阿拉伯入這樣／西方入傾向／其他入則
    (r"(?<=代代)入的", "人的", True),
    (r"(?<=宗教的)入不", "人不", True),
    (r"(?<=許多)入對", "人對", True),
    (r"(?<=一些)入則", "人則", True),
    (r"(?<=你的)入生", "人生", True),
    (r"(?<=相信)入生", "人生", True),
    (r"(?<=所有)入都", "人都", True),
    (r"(?<=世俗之)入", "人", True),
    (r"(?<=社會的)入(?=不需要)", "人", True),
    (r"(?<=黑)入(?=神學)", "人", True),
    (r"(?<=，)入(?=類來自)", "人", True),
]
_COMPILED = [(re.compile(p), r, risky) for p, r, risky in RULES]


def fix_text(text: str) -> tuple[str, list[tuple[int, str]]]:
    """套用全部規則。回傳（新文字，[(規則序號, 命中原文)]）。純函式。"""
    hits: list[tuple[int, str]] = []
    for i, (rx, rep, _risky) in enumerate(_COMPILED):
        def _sub(m: re.Match, i=i, rep=rep) -> str:
            hits.append((i, m.group(0)))
            return rep
        text = rx.sub(_sub, text)
    return text, hits


def _contexts(text: str, i: int) -> list[str]:
    rx = _COMPILED[i][0]
    return [text[max(0, m.start() - 12):m.end() + 12].replace("\n", "⏎")
            for m in rx.finditer(text)]


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    rows = [json.loads(l) for l in JSONL.read_text(encoding="utf-8").splitlines() if l.strip()]
    print(f"JSONL {len(rows)} 段、{sum(len(r.get('content') or '') for r in rows):,} 字")

    # 規則逐條計數（規則是依序套的，所以計數要在同一條流水線上算）
    counts = [0] * len(RULES)
    ctx: dict[int, list[str]] = {}
    new_rows = []
    for r in rows:
        text = r.get("content") or ""
        cur = text
        for i, (rx, rep, risky) in enumerate(_COMPILED):
            n = len(rx.findall(cur))
            if n:
                counts[i] += n
                if risky:
                    ctx.setdefault(i, []).extend(f"p{r.get('page_number')} {c}" for c in _contexts(cur, i))
                cur = rx.sub(rep, cur)
        new_rows.append({**r, "content": cur})

    for i, (p, rep, risky) in enumerate(RULES):
        flag = "⚠" if risky else " "
        print(f"{flag} {counts[i]:>4}  {p} → {rep}")
    print(f"合計 {sum(counts)} 處；0 筆的規則 {sum(1 for c in counts if not c)} 條")
    if a.dry_run:
        print("\n── 有風險規則的逐處上下文 ──")
        for i in sorted(ctx):
            print(f"[{RULES[i][0]} → {RULES[i][1]}]")
            for c in ctx[i]:
                print("   ", c)
        return 0

    # ── apply
    bak = Path("c:/tmp") / f"{EBOOK_ID}.jsonl.bak-2026-10-01"
    if not bak.exists():
        shutil.copy2(JSONL, bak)
    for old, new in zip(rows, new_rows):   # 只動 content，其他欄位（page_number）原樣
        assert {k: v for k, v in old.items() if k != "content"} == \
               {k: v for k, v in new.items() if k != "content"}
    JSONL.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in new_rows),
                     encoding="utf-8")
    print(f"✓ JSONL 寫回（備份 {bak}）")

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import translate_ebook_to_zh as te
    te.se.push_to_r2(EBOOK_ID, JSONL)
    print("✓ R2")

    _fix_docx()
    return 0


def _fix_docx() -> None:
    import docx
    if any(DOCX_DIR.glob("~$*")):
        print("⚠ 分章朗讀資料夾有 ~$ 鎖檔（Word 開著），docx 一律不動")
        return
    total = leftover = 0
    for f in sorted(DOCX_DIR.glob("*.docx")):
        d = docx.Document(str(f))
        n = 0
        for para in d.paragraphs:
            # 就地改：逐 run 換，保留格式；跨 run 的命中留給下面的檢查報出來
            for run in para.runs:
                new, hits = fix_text(run.text)
                if hits:
                    run.text = new
                    n += len(hits)
            _, rest = fix_text(para.text)
            leftover += len(rest)
            if rest:
                print(f"  ⚠ {f.name}：跨 run 未改 {[h for _, h in rest]} ｜ {para.text[:40]}")
        if n:
            d.save(str(f))
        total += n
        print(f"  {f.name}：{n} 處")
    print(f"✓ docx 共 {total} 處；跨 run 沒改到 {leftover} 處")


if __name__ == "__main__":
    raise SystemExit(main())
