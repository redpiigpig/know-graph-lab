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
            "verse_words": verses[t["ref"]],
            "target_idx": t["_idx"],
            "surface": t["surface"], "translit": t["translit"],
            "lemma": t["lemma"], "gloss": t["gloss"],
            "pos": t["pos"], "code": t["code"], "fields": t["fields"],
        })
    return out


# ── 希伯來文 morph 碼 → 繁中維度（STEPBible TAHOT / OSHB 編碼）─────────────────
HEBREW_OPTIONS = {
    "stem":   ["Qal", "Niphal", "Piel", "Pual", "Hiphil", "Hophal", "Hithpael"],  # 七大字幹 binyanim
    "conj":   ["完成式", "未完成式", "敘事式", "命令式", "不定獨立", "不定附屬", "主動分詞", "被動分詞"],
    "person": ["第一", "第二", "第三"],
    "gender": ["陽性", "陰性", "通性"],
    "number": ["單數", "複數", "雙數"],
    "state":  ["絕對", "連屬"],
}
HEB_DIM_LABEL = {"stem": "字幹(binyan)", "conj": "動貌", "person": "人稱",
                 "gender": "性", "number": "數", "state": "狀態"}

_HB_STEM = {"q": "Qal", "N": "Niphal", "p": "Piel", "P": "Pual",
            "h": "Hiphil", "H": "Hophal", "t": "Hithpael"}  # 大小寫敏感
_HB_CONJ = {"p": "完成式", "i": "未完成式", "w": "敘事式", "v": "命令式",
            "a": "不定獨立", "c": "不定附屬", "r": "主動分詞", "s": "被動分詞"}
_HB_PERSON = {"1": "第一", "2": "第二", "3": "第三"}
_HB_GEN = {"m": "陽性", "f": "陰性", "c": "通性", "b": "通性"}
_HB_NUM = {"s": "單數", "p": "複數", "d": "雙數"}
_HB_STATE = {"a": "絕對", "c": "連屬"}  # d=確定 罕見 → 不出題


def decode_hebrew_morph(code):
    """STEPBible 希伯來文 morph 碼（如 HVqp3ms / HNcfsa）→ 可批改維度；不可乾淨批改回 None。
    只處理單一語素（呼叫端應先濾掉含 '/' 的多語素詞）。"""
    code = (code or "").strip()
    if code.startswith("H"):
        code = code[1:]
    if not code:
        return None
    pos = code[0]

    # 名詞：性‧數‧狀態（type 在 code[1]，不出題）
    if pos == "N" and len(code) >= 5:
        gen, num, st = code[2], code[3], code[4]
        if gen not in _HB_GEN or num not in _HB_NUM or st not in _HB_STATE:
            return None
        return {"pos": "名詞", "fields": [
            {"k": "gender", "gold": _HB_GEN[gen]},
            {"k": "number", "gold": _HB_NUM[num]},
            {"k": "state", "gold": _HB_STATE[st]}]}

    # 動詞：字幹 + 動貌 (+ 人稱性數 / 分詞性數 / 不定詞無)
    if pos == "V" and len(code) >= 3:
        stem, conj, rest = code[1], code[2], code[3:]
        if stem not in _HB_STEM or conj not in _HB_CONJ:
            return None
        fields = [{"k": "stem", "gold": _HB_STEM[stem]},
                  {"k": "conj", "gold": _HB_CONJ[conj]}]
        if conj in ("p", "i", "w", "v"):  # 限定式：人稱+性+數
            if len(rest) < 3 or rest[0] not in _HB_PERSON or rest[1] not in _HB_GEN or rest[2] not in _HB_NUM:
                return None
            fields += [{"k": "person", "gold": _HB_PERSON[rest[0]]},
                       {"k": "gender", "gold": _HB_GEN[rest[1]]},
                       {"k": "number", "gold": _HB_NUM[rest[2]]}]
        elif conj in ("r", "s"):  # 分詞：性+數
            if len(rest) < 2 or rest[0] not in _HB_GEN or rest[1] not in _HB_NUM:
                return None
            fields += [{"k": "gender", "gold": _HB_GEN[rest[0]]},
                       {"k": "number", "gold": _HB_NUM[rest[1]]}]
        # 不定詞（a/c）：無額外維度
        return {"pos": "動詞", "fields": fields}

    return None


_TAHOT = ["TAHOT%20Gen-Deu%20-%20Translators%20Amalgamated%20Hebrew%20OT%20-%20STEPBible.org%20CC%20BY.txt",
          "TAHOT%20Jos-Est%20-%20Translators%20Amalgamated%20Hebrew%20OT%20-%20STEPBible.org%20CC%20BY.txt",
          "TAHOT%20Job-Sng%20-%20Translators%20Amalgamated%20Hebrew%20OT%20-%20STEPBible.org%20CC%20BY.txt",
          "TAHOT%20Isa-Mal%20-%20Translators%20Amalgamated%20Hebrew%20OT%20-%20STEPBible.org%20CC%20BY.txt"]
_HEB_BOOK_ZH = {
    "Gen": "創世記", "Exo": "出埃及記", "Lev": "利未記", "Num": "民數記", "Deu": "申命記",
    "Jos": "約書亞記", "Jdg": "士師記", "Rut": "路得記", "1Sa": "撒母耳記上", "2Sa": "撒母耳記下",
    "1Ki": "列王紀上", "2Ki": "列王紀下", "1Ch": "歷代志上", "2Ch": "歷代志下", "Ezr": "以斯拉記",
    "Neh": "尼希米記", "Est": "以斯帖記", "Job": "約伯記", "Psa": "詩篇", "Pro": "箴言",
    "Ecc": "傳道書", "Sng": "雅歌", "Isa": "以賽亞書", "Jer": "耶利米書", "Lam": "耶利米哀歌",
    "Eze": "以西結書", "Dan": "但以理書", "Hos": "何西阿書", "Jol": "約珥書", "Amo": "阿摩司書",
    "Oba": "俄巴底亞書", "Jon": "約拿書", "Mic": "彌迦書", "Nah": "那鴻書", "Hab": "哈巴谷書",
    "Zep": "西番雅書", "Hag": "哈該書", "Zec": "撒迦利亞書", "Mal": "瑪拉基書",
}


def _heb_zh_ref(ref):
    book, _, cv = ref.partition(".")
    return f"{_HEB_BOOK_ZH.get(book, book)} {cv}"


def harvest_hebrew(per_lemma_cap=4, total_cap=1500):
    """下載 TAHOT，只取單一語素的內容詞（N/V），解碼成題庫（含經文脈絡，RTL）。"""
    verses, tokens = {}, []
    for fn in _TAHOT:
        print(f"  下載 {fn[:24]}…", flush=True)
        r = requests.get(f"{STEP_BASE}/{fn}", timeout=240)
        r.encoding = "utf-8"
        for ln in r.text.splitlines():
            if "\t" not in ln or "#" not in ln[:12] or "." not in ln[:12]:
                continue
            cols = ln.split("\t")
            if len(cols) < 6 or "#" not in cols[0]:
                continue
            ref = cols[0].split("#")[0].strip()
            surface = cols[1].replace("/", "").strip()  # 去掉語素分隔，併成整字
            translit = cols[2].replace("/", "").strip()
            gloss = cols[3].replace("/", " ").strip()
            morph = cols[5].strip()
            verses.setdefault(ref, []).append(surface)
            if "/" in morph:  # 多語素（含前綴）→ 黃金答案易混淆，跳過
                continue
            decoded = decode_hebrew_morph(morph)
            if decoded:
                tokens.append({"ref": ref, "surface": surface, "translit": translit,
                               "gloss": gloss, "code": morph, "pos": decoded["pos"],
                               "fields": decoded["fields"], "_idx": len(verses[ref]) - 1})
    per, capped = {}, []
    for t in tokens:
        key = (t["pos"], t["translit"])
        if per.get(key, 0) >= per_lemma_cap:
            continue
        per[key] = per.get(key, 0) + 1
        capped.append(t)
    if len(capped) > total_cap:
        step = len(capped) / total_cap
        capped = [capped[int(i * step)] for i in range(total_cap)]
    out = []
    for t in capped:
        out.append({
            "ref": _heb_zh_ref(t["ref"]),
            "verse_words": verses[t["ref"]],
            "target_idx": t["_idx"],
            "surface": t["surface"], "translit": t["translit"],
            "lemma": t["surface"], "gloss": t["gloss"],
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
        from collections import Counter
        print(f"寫入 {path}：{len(items)} 題（{dict(Counter(i['pos'] for i in items))}）")
    elif which == "hebrew":
        items = harvest_hebrew()
        payload = {"language": "hbo", "rtl": True, "options": HEBREW_OPTIONS,
                   "dimLabels": HEB_DIM_LABEL, "items": items}
        path = OUT_DIR / "parseHebrew.json"
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        from collections import Counter
        print(f"寫入 {path}：{len(items)} 題（{dict(Counter(i['pos'] for i in items))}）")
    else:
        print(f"未知參數：{which}（支援 greek / hebrew）")


if __name__ == "__main__":
    main()
