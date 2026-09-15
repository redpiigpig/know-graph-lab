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
    "Tob": "多比傳", "Tbs": "多比傳（西奈抄本）", "Wis": "所羅門智訓",
    "Sir": "便西拉智訓", "Bar": "巴錄書", "1Es": "以斯拉續篇上卷",
    "1Ma": "馬加比一書", "3Ma": "馬加比三書", "4Ma": "馬加比四書",
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
    return f"{BOOK_ZH[book]} {locus.replace('.', ':')}"
