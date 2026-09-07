# -*- coding: utf-8 -*-
"""畔上賢造（1884–1938）—— NDL 掃描本 → ja＋繁中的 registry 模組。

無教會第一代、內村鑑三的助手與文筆傳道者，全球公有領域（卒 1938）。
青空文庫沒收、libgen 也沒有，只有國立國會圖書館的掃描本，所以取源那一段
走 `ndl_build.py`（IIIF 影像 → Gemini Vision OCR → 目次分章）；
本模組只負責把已經 build 好的 `ndl_data/{slug}/secN.json` 交給
`uchimura_auto.py` 去翻譯與上架。

🚨 **與其他 author 模組的差別**：howes／uchimura 的 `load_work_sections` 是現場
從 PDF／HTML 解析出來的，本模組是**讀 ndl_build 已經寫好的 JSON**。這是刻意的：
OCR 很貴而且要過幻覺閘（見 ndl_build.toc_match_ratio），不可以每次翻譯都重跑。
換句話說 `ndl_data/{slug}/` 這個目錄同時是 ndl_build 的產出與這裡的 checkpoint，
`src` 由 ndl_build 寫、`zh` 由 uchimura_auto 填。

見 .claude/skills/ebook-collected-works/ndl_open_scans.md。
"""
from __future__ import annotations

import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
_SKILL_DATA = SCRIPT_DIR.parent / ".claude" / "skills" / "ebook-collected-works"

SOURCE_LANG = "ja"
AUTHOR_ZH = "畔上賢造"
AUTHOR_EN = "Azegami Kenzō"
CATEGORY = "神學"
DATA_DIRNAME = "ndl_data"

REGISTRY: dict[str, dict] = {
    "muky-shugi": {
        # 內村命名空間 d0000000-…-0001..0009 已用掉；畔上另起 e0000000-…
        "ebook_id": "e0000000-0000-4000-8000-000000000001",
        "title": "無教會主義",
        "original_title": "無教會主義",
        "subtitle": "畔上賢造 1934（NDL 掃描本．日文原文＋繁中對照）",
        "year": 1934,
        "parent_volume": "無教會主義論",
        "ndl_pid": "1099766",
    },
}

QUEUE = ["muky-shugi"]


def load_work_sections(slug: str) -> list[dict]:
    """讀 ndl_build 產出的 secN.json → [{heading, title_zh, paras}]。

    `paras` 就是 OCR 出來的日文原文（`src`）。這裡不做任何切段或改寫——
    段落在 ndl_build 那邊已經按「跨頁不換段」的規則接好了，
    再切一次只會把接好的句子又拆開。
    """
    d = _SKILL_DATA / DATA_DIRNAME / slug
    secs = []
    for p in sorted(d.glob("sec*.json"), key=lambda x: int(x.stem[3:])):
        j = json.loads(p.read_text(encoding="utf-8"))
        secs.append({"heading": j["heading"], "title_zh": j.get("title_zh"),
                     "paras": list(j.get("src") or [])})
    if not secs:
        raise RuntimeError(
            "%s 底下沒有 secN.json —— 先跑 ndl_build.py --ocr / --build" % d)
    return secs


AZEGAMI_PROMPT_TMPL = """你是日本近代基督教史的專業譯者，正在翻譯畔上賢造（1884–1938）
一九三四年的著作《無教會主義》。原文是戰前日文，直排、舊字體、舊假名遣。
把下列日文原文翻成**繁體中文**。

規則：
1. 嚴守繁體中文（禁簡體）；中間點用「‧」。
2. 只翻譯，不要加任何前言、說明、譯註或原文回抄。
3. 舊假名遣（「といふ」「なつてきた」「ゐる」）照現代語意理解，不要逐字直譯成怪中文。
4. **無教會主義的專門語彙照既有定名**：無教會主義／教派／宗派／傳道／
   信仰第一主義／聖書（不譯成「聖經」，這是無教會的用語習慣）。
5. 人名地名用既有中譯：內村鑑三、畔上賢造、新渡戶稻造、矢內原忠雄。
6. 日本事物不可西化：天皇不是皇帝，神社不是廟。
7. 原文是論說文，語氣是說理不是抒情，不要加原文沒有的感嘆。

日文原文：
{source}"""


def make_engine(backend: str = "auto"):
    """translate_para(ja)->zh。引擎鏈沿用 translate_ebook_to_zh，只換 prompt。"""
    import translate_ebook_to_zh as te
    import uchimura_build as ub
    te.PROMPT_TMPL = AZEGAMI_PROMPT_TMPL

    def translate_para(ja: str) -> str:
        src = (ja or "").strip()
        if not src:
            return ""
        pieces = te.split_oversized(src)

        def translate_piece(piece: str) -> str:
            if backend == "haiku":
                return te.haiku_translate(piece)
            if backend == "gemini":
                return te.gemini_translate(piece)
            if backend == "nvidia":
                return te.nvidia_translate(piece)
            return te.gemini_with_nvidia_fallback(piece)

        return ub.clean_zh_output(" ".join(translate_piece(p) for p in pieces))

    return translate_para
