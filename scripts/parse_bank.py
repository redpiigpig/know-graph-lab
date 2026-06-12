# ============================================================================
# 古典語「詞形 parsing 自動批改」題庫產生器（零 AI）。
# 用 STEPBible 黃金標註（TAGNT 希臘文新約 / TAHOT 希伯來文舊約，CC-BY）把每個字的
# morph 碼解成可批改的維度（格/數/性、時態/語態/語氣/人稱…），輸出靜態 JSON 題庫，
# 頁面端 dropdown 選答、純比對黃金答案、完全不碰 AI。
#
# 用法：python scripts/parse_bank.py greek   → 寫 server/data/parseGreek.json
# 測試：python -m pytest scripts/tests/test_parse_bank.py
#
# 純函式 `decode_greek_morph(code)` 可單測；harvest_* 才碰網路。
# ============================================================================
import json
import re
import sys
from pathlib import Path

import requests

STEP_BASE = ("https://raw.githubusercontent.com/STEPBible/STEPBible-Data/master/"
             "Translators%20Amalgamated%20OT%2BNT")
OUT_DIR = Path(__file__).resolve().parent.parent / "server" / "data"

# ── 希臘文 morph 碼 → 繁中維度 ──────────────────────────────────────────────
# 維度選項（頁面 dropdown 用同一份；key 對應 decode 回傳的 fields[].k）
GREEK_OPTIONS = {
    "case":   ["主格", "屬格", "與格", "賓格", "呼格"],
    "number": ["單數", "複數"],
    "gender": ["陽性", "陰性", "中性"],
    "tense":  ["現在", "未完成", "未來", "不定過去", "完成", "過去完成"],
    "voice":  ["主動", "關身", "被動"],
    "mood":   ["直說", "假設", "祈願", "命令", "不定詞", "分詞"],
    "person": ["第一", "第二", "第三"],
}
DIM_LABEL = {"case": "格", "number": "數", "gender": "性",
             "tense": "時態", "voice": "語態", "mood": "語氣", "person": "人稱"}

_GK_CASE = {"N": "主格", "G": "屬格", "D": "與格", "A": "賓格", "V": "呼格"}
_GK_NUM = {"S": "單數", "P": "複數"}
_GK_GEN = {"M": "陽性", "F": "陰性", "N": "中性"}
_GK_TENSE = {"P": "現在", "I": "未完成", "F": "未來", "A": "不定過去", "R": "完成", "L": "過去完成"}
_GK_VOICE = {"A": "主動", "M": "關身", "P": "被動"}  # 異相語態 E/N/D 不出題（黃金答案有爭議）
_GK_MOOD = {"I": "直說", "S": "假設", "O": "祈願", "M": "命令", "N": "不定詞", "P": "分詞"}
_GK_PERSON = {"1": "第一", "2": "第二", "3": "第三"}
_CNG_POS = {"N": "名詞", "A": "形容詞", "T": "冠詞"}  # 走 格/數/性


def _cng(seg):
    """3 碼 case-number-gender → fields 或 None。"""
    if len(seg) < 3 or seg[0] not in _GK_CASE or seg[1] not in _GK_NUM or seg[2] not in _GK_GEN:
        return None
    return [{"k": "case", "gold": _GK_CASE[seg[0]]},
            {"k": "number", "gold": _GK_NUM[seg[1]]},
            {"k": "gender", "gold": _GK_GEN[seg[2]]}]


def decode_greek_morph(code):
    """把 STEPBible 希臘文 morph 碼（如 N-NSF / V-2AAI-3S / V-PAP-NSM）解成
    {"pos": 繁中詞性, "fields": [{"k": 維度, "gold": 繁中答案}, ...]}；不可乾淨批改回 None。"""
    code = (code or "").strip()
    if not code:
        return None
    parts = code.split("-")
    pos = parts[0]

    # 名詞 / 形容詞 / 冠詞：格‧數‧性
    if pos in _CNG_POS:
        if len(parts) < 2:
            return None
        f = _cng(parts[1])
        return {"pos": _CNG_POS[pos], "fields": f} if f else None

    # 動詞
    if pos == "V":
        if len(parts) < 2:
            return None
        tvm = parts[1]
        i = 1 if tvm[:1].isdigit() else 0  # 去掉第二式（second aorist/perfect）前綴數字
        if len(tvm) - i < 3:
            return None
        t, v, m = tvm[i], tvm[i + 1], tvm[i + 2]
        if t not in _GK_TENSE or v not in _GK_VOICE or m not in _GK_MOOD:
            return None  # 含異相語態（E/N/D）或未知 → 跳過
        fields = [{"k": "tense", "gold": _GK_TENSE[t]},
                  {"k": "voice", "gold": _GK_VOICE[v]},
                  {"k": "mood", "gold": _GK_MOOD[m]}]
        if m == "P":  # 分詞：再加 格‧數‧性
            if len(parts) < 3:
                return None
            f = _cng(parts[2])
            if not f:
                return None
            fields += f
        elif m == "N":  # 不定詞：無人稱數
            pass
        else:  # 限定動詞：人稱 + 數
            if len(parts) < 3 or len(parts[2]) < 2:
                return None
            pn = parts[2]
            if pn[0] not in _GK_PERSON or pn[1] not in _GK_NUM:
                return None
            fields += [{"k": "person", "gold": _GK_PERSON[pn[0]]},
                       {"k": "number", "gold": _GK_NUM[pn[1]]}]
        return {"pos": "動詞", "fields": fields}

    return None  # 其他詞類（連接詞/介系詞/質詞/代名詞各式）暫不出題


# ── 採集 TAGNT → 題庫 ───────────────────────────────────────────────────────
_TAGNT = ["TAGNT%20Mat-Jhn%20-%20Translators%20Amalgamated%20Greek%20NT%20-%20STEPBible.org%20CC-BY.txt",
          "TAGNT%20Act-Rev%20-%20Translators%20Amalgamated%20Greek%20NT%20-%20STEPBible.org%20CC-BY.txt"]
_BOOK_ZH = {  # 新約書卷代碼 → 繁中
    "Mat": "馬太福音", "Mrk": "馬可福音", "Luk": "路加福音", "Jhn": "約翰福音",
    "Act": "使徒行傳", "Rom": "羅馬書", "1Co": "哥林多前書", "2Co": "哥林多後書",
    "Gal": "加拉太書", "Eph": "以弗所書", "Php": "腓立比書", "Col": "歌羅西書",
    "1Th": "帖撒羅尼迦前書", "2Th": "帖撒羅尼迦後書", "1Ti": "提摩太前書", "2Ti": "提摩太後書",
    "Tit": "提多書", "Phm": "腓利門書", "Heb": "希伯來書", "Jas": "雅各書",
    "1Pe": "彼得前書", "2Pe": "彼得後書", "1Jn": "約翰一書", "2Jn": "約翰二書",
    "3Jn": "約翰三書", "Jud": "猶大書", "Rev": "啟示錄",
}


def _zh_ref(ref):
    book, _, cv = ref.partition(".")
    return f"{_BOOK_ZH.get(book, book)} {cv}"


def harvest_greek(per_lemma_cap=4, total_cap=1500):
    """下載 TAGNT，逐字解碼，產出可批改題庫（含經文脈絡）。"""
    verses = {}   # ref -> [surface, ...]（重建經文）
    tokens = []   # 候選 token（先全收，最後再按 lemma cap + total cap 取樣）
    seen_header = re.compile(r"^#?\s*[1-3A-Za-z]{2,3}\.\d+\.\d+")
    for fn in _TAGNT:
        print(f"  下載 {fn[:24]}…", flush=True)
        r = requests.get(f"{STEP_BASE}/{fn}", timeout=180)
        r.encoding = "utf-8"
        for ln in r.text.splitlines():
            if "\t" not in ln or "#" not in ln[:14] or "." not in ln[:14]:
                continue
            cols = ln.split("\t")
            if len(cols) < 5 or "#" not in cols[0]:
                continue
            ref = cols[0].split("#")[0].strip()
            surface = cols[1].split("(")[0].strip()
            translit = ""
            mt = re.search(r"\(([^)]+)\)", cols[1])
            if mt:
                translit = mt.group(1)
            morph = cols[3].split("=")[-1].strip()
            lemma, _, base_gloss = cols[4].partition("=")
            lemma = lemma.strip()
            base_gloss = base_gloss.split(",")[0].strip(" :»").strip()
            verses.setdefault(ref, []).append(surface)
            decoded = decode_greek_morph(morph)
            if decoded:
                tokens.append({"ref": ref, "surface": surface, "translit": translit,
                               "lemma": lemma, "gloss": base_gloss, "code": morph,
                               "pos": decoded["pos"], "fields": decoded["fields"],
                               "_idx": len(verses[ref]) - 1})
    # 取樣：每 lemma 最多 per_lemma_cap（跑完整本 NT，不提早 break）
    per = {}
    capped = []
    for t in tokens:
        key = (t["pos"], t["lemma"])
        if per.get(key, 0) >= per_lemma_cap:
            continue
        per[key] = per.get(key, 0) + 1
        capped.append(t)
    # 等距抽樣 total_cap 筆 → 平均分散整本新約（不集中在馬太開頭）
    if len(capped) > total_cap:
        step = len(capped) / total_cap
        capped = [capped[int(i * step)] for i in range(total_cap)]
    out = []
    for t in capped:
        out.append({
            "ref": _zh_ref(t["ref"]),
            "verse": " ".join(verses[t["ref"]]),
            "target_idx": t["_idx"],
            "surface": t["surface"], "translit": t["translit"],
            "lemma": t["lemma"], "gloss": t["gloss"],
            "pos": t["pos"], "code": t["code"], "fields": t["fields"],
        })
    return out


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "greek"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if which == "greek":
        items = harvest_greek()
        payload = {"language": "grc", "options": GREEK_OPTIONS, "dimLabels": DIM_LABEL, "items": items}
        path = OUT_DIR / "parseGreek.json"
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        # 統計
        from collections import Counter
        pc = Counter(i["pos"] for i in items)
        print(f"寫入 {path}：{len(items)} 題（{dict(pc)}）")
    else:
        print(f"未知參數：{which}（目前支援 greek；hebrew 下一版）")


if __name__ == "__main__":
    main()
