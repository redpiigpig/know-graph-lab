#!/usr/bin/env python3
"""把希臘讀本的內部出處代碼翻成書上與網頁都印得出來的出處。

紙本與網頁必須印出同一行字。把對照表放在排版腳本裡，網頁那一層就得自己
再寫一份 52 條的書卷表，兩份遲早會走岔——這個系列已經在「同一份成品放兩處」
上吃過虧。所以表只有這一份：`assemble_greek_exercises.py` 在組題時就把
refLabel 寫進題庫，排版與網頁都照著印。
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "greek-full"
PATRISTIC_PLAN_PATH = CACHE / "patristic-plan.json"


# 52 種書卷代碼 → 繁體書名。定錨題的出處橫跨新約、七十士譯本、次經與偽經，
# 而語料用的是 Swete 的代碼（Pss 是《所羅門詩篇》不是詩篇，Tbs 是西奈抄本的
# 多比傳），對照表只能一條一條寫。查不到就在排版時報錯——書上印一串
# 「Pss.15:14」不是出處，是沒做完。
BOOK_ZH = {
    "Gen": "創世記", "Exo": "出埃及記", "Num": "民數記", "Deu": "申命記",
    "Jos": "約書亞記", "Jdg": "士師記", "1Sa": "撒母耳記上", "2Sa": "撒母耳記下",
    "1Ki": "列王紀上", "2Ki": "列王紀下", "1Ch": "歷代志上", "2Ch": "歷代志下",
    "Neh": "尼希米記", "Job": "約伯記", "Psa": "詩篇", "Pro": "箴言",
    "Ecc": "傳道書", "Isa": "以賽亞書", "Jer": "耶利米書", "Lam": "耶利米哀歌",
    "Eze": "以西結書", "Dan": "但以理書", "Hos": "何西阿書", "Nah": "那鴻書",
    # 次經書名以 bible_books 表的 name_sigao（思高譯本，本讀本課題已採用此名）為
    # 準；該表沒有思高名的（3Ma／4Ma／1Es 不屬思高／天主教正典），改用該表的
    # name_zh。2026-09-27 統一：Tob「多比傳」→「多俾亞傳」、Sir「便西拉智訓」→
    # 「德訓篇」、Wis「所羅門智訓」→「智慧篇」、1Ma「馬加比一書」→「瑪加伯上」、
    # 1Es「以斯拉續篇上卷」→「厄斯德拉一書」，修正練習出處與課題目錄不一致。
    "Tob": "多俾亞傳", "Tbs": "多俾亞傳（西奈抄本）", "Wis": "智慧篇",
    "Sir": "德訓篇", "Bar": "巴錄書", "1Es": "厄斯德拉一書",
    "1Ma": "瑪加伯上", "3Ma": "馬加比三書", "4Ma": "馬加比四書",
    "Pss": "所羅門詩篇", "1En": "以諾一書",
    "Matt": "馬太福音", "Mark": "馬可福音", "Luke": "路加福音", "John": "約翰福音",
    "Acts": "使徒行傳", "Rom": "羅馬書", "1Cor": "哥林多前書", "2Cor": "哥林多後書",
    "Gal": "加拉太書", "Eph": "以弗所書", "Phil": "腓立比書", "Col": "歌羅西書",
    "1Thess": "帖撒羅尼迦前書", "1Tim": "提摩太前書", "Heb": "希伯來書",
    "Jas": "雅各書", "Rev": "啟示錄",
}

def _plan_titles() -> dict[int, str]:
    plan = json.loads(PATRISTIC_PLAN_PATH.read_text(encoding="utf-8"))
    return {row["ordinal"]: row["titleZh"] for row in plan["readings"]}


def _liturgy_steps() -> dict[int, dict]:
    payload = json.loads((CACHE / "liturgy-chrysostom.json").read_text(encoding="utf-8"))
    return {step["ordinal"]: step for step in payload["steps"]}


_REF_CACHE: dict[str, dict] = {}


def anchor_label(ref: str) -> str:
    """把定錨題的內部代碼翻成書上印得出來的出處。

    `patristic-plan:21:2.2#3` 與 `liturgy-chrysostom:127#1` 是讀本計畫自己的
    識別碼，不是任何人查得到的出處；照印就等於沒標。經文那一側用的是書卷代碼，
    查表翻成繁體書名，章節之間一律用冒號——語料裡 Matt.5.27 與 1Sa.2:4 是同
    一種東西，兩種寫法而已。
    """
    if ref.startswith("patristic-plan:"):
        _, ordinal, rest = ref.split(":", 2)
        titles = _REF_CACHE.setdefault("patristic", _plan_titles())
        title = titles.get(int(ordinal))
        if title is None:
            raise SystemExit(f"練習題出處 {ref} 對不到教父讀本計畫的第 {ordinal} 篇")
        return f"{title}　{rest.split('#')[0]}"
    if ref.startswith("liturgy-chrysostom:"):
        ordinal = int(ref.split(":", 1)[1].split("#")[0])
        steps = _REF_CACHE.setdefault("liturgy", _liturgy_steps())
        step = steps.get(ordinal)
        if step is None:
            raise SystemExit(f"練習題出處 {ref} 對不到聖禮儀的第 {ordinal} 則")
        return f"金口約翰聖禮儀・{step['sectionLabel']}　第 {ordinal} 則"
    book, _, locus = ref.partition(".")
    if book not in BOOK_ZH:
        raise SystemExit(f"練習題出處 {ref} 的書卷代碼 {book} 不在對照表裡")
    if book == "Psa":
        # 七十士詩篇編號與馬所拉／中文聖經編號多數差一號（見
        # export_reader_rcuv2010_greek.psalm_crosswalk）；節號還可能因標題節
        # 算不算入而再差一號，換算節號須配 RCUV 逐節核對，這裡沒有那份資料。
        # 體例（本書第 2 頁）是「七十士編號一律換算成馬所拉編號」，練習題出處
        # 也要照做，否則學生會拿著「詩篇 23:1」去找詩篇 23 篇，卻應該找的是
        # 詩篇 24 篇。篇號換算了就不會找錯書；節號不確定的，寫出七十士原節號
        # 供對照，不假裝算出一個可能錯的節號。
        import sys as _sys
        _sys.path.insert(0, str(ROOT / "scripts"))
        from export_reader_rcuv2010_greek import psalm_crosswalk

        chapter_str, _, verse_str = locus.partition(":")
        lxx_chapter = int(chapter_str)
        lxx_verse = int(verse_str) if verse_str else None
        mt_chapter, _mt_verse, _note = psalm_crosswalk(lxx_chapter, lxx_verse)
        lxx_locus = str(lxx_chapter) if lxx_verse is None else f"{lxx_chapter}:{lxx_verse}"
        if mt_chapter == lxx_chapter:
            return f"{BOOK_ZH[book]} {lxx_locus}"
        return f"{BOOK_ZH[book]} {mt_chapter} 篇（七十士 {lxx_locus}）"
    return f"{BOOK_ZH[book]} {locus.replace('.', ':')}"
