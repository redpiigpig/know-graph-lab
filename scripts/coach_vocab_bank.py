#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
共用學習單字庫建置器 — 為語言教練各語言建一份「權威頻率/語料庫 + LLM 補繁中釋義」的策展字庫。

來源（皆免費 / 公有領域 / CC-BY）：
  en/de/fr  FrequencyWords (hermitdave, OpenSubtitles 頻率表) → 取前 N，依頻率分 CEFR 級帶
  ja        jlpt-vocab-api (N5–N1)                          → 每級一類，含 furigana / romaji / EN 義
  grc       STEPBible TAGNT（譯者匯整希臘文新約 CC-BY）        → 詞元 + 英義 + 詞性 + 書卷，依新約頻率分帶
  hbo       STEPBible TAHOT（譯者匯整希伯來文舊約 CC-BY）      → 詞元 + 英義 + 詞性，依舊約頻率分帶
  la        Clementine Vulgate (seven1m/open-bibles, USFX)   → 表面詞頻 → LLM 還原詞元（武加大頻率分帶）
  arc       STEPBible TAHOT 的亞蘭文段落（morph 首字 A）       → 詞元 + 英義 + 詞性（聖經亞蘭文，~600 詞窮盡）
  att       STEPBible TAGNT（先共用 grc 新約語料為基底）        → 詞元 + 英義（古典希臘 Attic）
  ar        Quran JSON (risan/quran-json)                    → 表面詞頻 → LLM 還原詞元（古蘭阿拉伯文）
  sa        Bhagavad Gita (gita/gita, 天城體)                 → 表面詞頻 → LLM 還原詞元（梵文）
  pi        VRI Tipiṭaka XML (VipassanaTech, 羅馬轉寫 UTF-16)  → 表面詞頻 → LLM 還原詞元（巴利文）
  # 待補（語料零碎）：syr 敘利亞(SEDRA/CAL)、cop 科普特(Scriptorium CONLLU)、bo 藏文(OpenPecha)

流程：
  harvest <lang|all>          下載來源 + 解析 → ledger（C:/tmp/vocab_bank/<lang>.candidates.jsonl）
  gloss   <lang|all> [--limit N]  逐批呼叫 LLM 補繁中釋義/例句/詞性 → upsert 進 lang_vocab_bank
  run     <lang|all>          先 harvest 再 gloss
  status                      各語言 ledger / DB / 已補釋義 計數

引擎：NVIDIA deepseek-v4-flash（主，免費無上限、適合大量 JSON）→ Gemini（備）→ Haiku（救急）。
  ※ 本批次刻意 NVIDIA-first：6.6 萬條會瞬間燒爆 Gemini 免費日限（正是使用者遇到的 Gemini 過載）。
可重入：glossed 結果另存 <lang>.glossed.jsonl，重跑自動略過已完成詞。c:/tmp ledger 別清（[[feedback_tmp_cleanup]] 例外）。
"""
import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    os.system("pip install requests -q")
    import requests

# 重用 translate 腳本的引擎層（key 輪替 / 節流 / cooldown 全現成）
sys.path.insert(0, str(Path(__file__).resolve().parent))
import translate_ebook_to_zh as T  # noqa: E402

LEDGER_DIR = Path("C:/tmp/vocab_bank")
LEDGER_DIR.mkdir(parents=True, exist_ok=True)

# ── 目標字數（grc/hbo 取語料庫實有詞元，可能略少於目標即整部語料窮盡）──────────────
TARGETS = {"en": 30000, "de": 6000, "fr": 6000, "ja": 9000, "grc": 6000, "hbo": 8000, "la": 6000,
           "arc": 1000, "att": 6000, "ar": 6000, "sa": 3000, "pi": 6000,
           "cop": 4000, "bo": 4000, "es": 6000, "syr": 4000, "hy": 4000, "ka": 4000,
           "nan": 6000, "hak": 6000, "peo": 100, "phn": 100, "uga": 100, "chu": 100, "gez": 100,
           "akk": 100, "egy": 100, "ae": 100, "pra": 100, "mid": 100, "ami": 100, "tay": 100}
GLOSS_BATCH = 40          # 每次 LLM 一批詞數（deepseek ~30s/call，加大批量攤平延遲）
UPSERT_BATCH = 200        # 每次寫 DB 筆數

STEP_BASE = "https://raw.githubusercontent.com/STEPBible/STEPBible-Data/master/Translators%20Amalgamated%20OT%2BNT"
FREQ_BASE = "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018"

# 希臘文/希伯來文書卷縮寫 → 繁中（僅供標記，目前分類用頻率帶）
GK_BOOK = {"Mat": "馬太福音", "Mrk": "馬可福音", "Luk": "路加福音", "Jhn": "約翰福音",
           "Act": "使徒行傳", "Rom": "羅馬書", "Rev": "啟示錄"}


# ════════════════════════════════════════════════════════════════════════════
#  env / Supabase
# ════════════════════════════════════════════════════════════════════════════
def load_env():
    env = {}
    with open(".env", "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


_ENV = load_env()
_SB_URL = _ENV["SUPABASE_URL"]
_SB_KEY = _ENV["SUPABASE_SERVICE_ROLE_KEY"]
_SB_HEADERS = {"apikey": _SB_KEY, "Authorization": f"Bearer {_SB_KEY}", "Content-Type": "application/json"}


def upsert_rows(rows):
    """Upsert 進 lang_vocab_bank（衝突 language,word 則合併）。"""
    for i in range(0, len(rows), UPSERT_BATCH):
        chunk = rows[i:i + UPSERT_BATCH]
        r = requests.post(
            f"{_SB_URL}/rest/v1/lang_vocab_bank?on_conflict=language,word",
            headers={**_SB_HEADERS, "Prefer": "resolution=merge-duplicates,return=minimal"},
            data=json.dumps(chunk).encode("utf-8"),
            timeout=120,
        )
        if r.status_code not in (200, 201, 204):
            print(f"  ! upsert HTTP {r.status_code}: {r.text[:300]}", flush=True)
            r.raise_for_status()


def db_count(lang, glossed_only=False, themed_only=False):
    q = f"{_SB_URL}/rest/v1/lang_vocab_bank?language=eq.{lang}&select=id"
    if glossed_only:
        q += "&glossed=eq.true"
    if themed_only:
        q += "&glossed=eq.true&theme=not.is.null"
    r = requests.get(q, headers={**_SB_HEADERS, "Prefer": "count=exact", "Range": "0-0"}, timeout=60)
    cr = r.headers.get("content-range", "*/0")
    return int(cr.split("/")[-1]) if "/" in cr else 0


# ════════════════════════════════════════════════════════════════════════════
#  LLM：NVIDIA → Gemini → Haiku，回 JSON 陣列
# ════════════════════════════════════════════════════════════════════════════
_GEM_IDX = 0


def _gemini_json(prompt, system):
    global _GEM_IDX
    if not T.GEMINI_KEYS:
        raise RuntimeError("no Gemini key")
    body = {"contents": [{"parts": [{"text": (system + "\n\n" + prompt)}]}],
            "generationConfig": {"temperature": 0.3, "responseMimeType": "application/json"}}
    base = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
    for _ in range(len(T.GEMINI_KEYS)):
        key = T.GEMINI_KEYS[_GEM_IDX]
        try:
            r = requests.post(f"{base}?key={key}", json=body, timeout=120)
        except requests.exceptions.RequestException:
            _GEM_IDX = (_GEM_IDX + 1) % len(T.GEMINI_KEYS)
            continue
        if r.status_code == 200:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        _GEM_IDX = (_GEM_IDX + 1) % len(T.GEMINI_KEYS)
    raise RuntimeError("all Gemini keys exhausted")


def _haiku_json(prompt, system, _tries=4):
    """Haiku（Claude Max OAuth）。401＝token 已輪替 → 強制重讀 credentials.json 再試；
    429＝Max rolling-window → 等過再試（與 translate 的 _anthropic_translate 同策略）。"""
    last = None
    for attempt in range(_tries):
        T._refresh_anthropic_client_if_creds_changed()
        try:
            msg = T._anthropic_client.messages.create(
                model=T.HAIKU_MODEL, max_tokens=8000,
                system=system, messages=[{"role": "user", "content": prompt}])
            return "".join(b.text for b in msg.content if hasattr(b, "text")).strip()
        except T._anthropic.AuthenticationError:
            T._anthropic_client_cred_mtime = 0.0  # 逼下次 refresh 重建 client（讀新 token）
            last = "401"
            continue
        except T._anthropic.RateLimitError:
            time.sleep(20 * (attempt + 1))
            last = "429"
            continue
        except (T._anthropic.APIConnectionError, T._anthropic.APITimeoutError):
            time.sleep(5 * (attempt + 1))  # 連線瞬斷 → 短退避再試，避免整批被跳過
            last = "conn"
            continue
    raise RuntimeError(f"Haiku failed after {_tries} tries (last={last})")


def _parse_json_array(text):
    text = T._THINK_RE.sub("", text).strip()
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    m = re.search(r"\[.*\]", text, re.S)
    if m:
        text = m.group(0)
    data = json.loads(text)
    if isinstance(data, dict):
        for v in data.values():
            if isinstance(v, list):
                return v
        return [data]
    return data


# NVIDIA 2-strike → Haiku 快速救急（避免 nvidia_chat 內建 10 分鐘 deadline 把整個 run 卡死）：
#   · 每次 NVIDIA 嘗試只給 90s（deadline_s），逾時就換下一個引擎，不再苦等 10 分鐘。
#   · 連續 _NV_STREAK_LIMIT 次 NVIDIA 失敗 → 暫停 NVIDIA _NV_COOLDOWN_S 秒，直接走 Gemini→Haiku
#     （使用者訂 Claude Max，NVIDIA/Gemini 都掛時 Haiku 為可靠後盾）。冷卻後再探 NVIDIA、成功即重置。
_NV_STREAK_LIMIT = 2
_NV_COOLDOWN_S = 900
_nv_fail_streak = 0
_nv_cooldown_until = 0.0


def llm_json(prompt, system, engine="auto"):
    """回 list[dict]；engine=auto 走 NVIDIA→Gemini→Haiku（NVIDIA 2-strike 後暫停改走 Gemini→Haiku）；
    engine=haiku/nvidia/gemini 則強制單一引擎（用於某些引擎已耗盡額度時直攻可用的那個）。"""
    global _nv_fail_streak, _nv_cooldown_until
    errs = []
    _ENG = {
        "nvidia": ("NVIDIA", lambda: T.nvidia_chat(prompt, max_tokens=7000, system=system, temperature=0.3, deadline_s=90)),
        "gemini": ("Gemini", lambda: _gemini_json(prompt, system)),
        "haiku": ("Haiku", lambda: _haiku_json(prompt, system)),
    }
    if engine in _ENG:
        engines = [_ENG[engine]]
    else:
        engines = []
        if time.time() >= _nv_cooldown_until:  # 冷卻期內就跳過 NVIDIA
            engines.append(_ENG["nvidia"])
        engines.append(_ENG["gemini"])
        engines.append(_ENG["haiku"])
    for name, fn in engines:
        try:
            out = _parse_json_array(fn())
            if name == "NVIDIA":
                _nv_fail_streak = 0
            return out
        except Exception as e:  # noqa: BLE001
            errs.append(f"{name}:{type(e).__name__}:{str(e)[:80]}")
            if name == "NVIDIA":
                _nv_fail_streak += 1
                if _nv_fail_streak >= _NV_STREAK_LIMIT:
                    _nv_cooldown_until = time.time() + _NV_COOLDOWN_S
                    print(f"  ↳ NVIDIA 連續 {_nv_fail_streak} 次失敗 — 暫停 {_NV_COOLDOWN_S // 60} 分，直接走 Gemini→Haiku", flush=True)
            continue
    raise RuntimeError("all engines failed → " + " | ".join(errs))


# ════════════════════════════════════════════════════════════════════════════
#  頻率帶 → 分類標籤
# ════════════════════════════════════════════════════════════════════════════
def _cefr_band(rank):
    if rank <= 1000:
        return "A1 基礎高頻字"
    if rank <= 2000:
        return "A2 高頻字"
    if rank <= 4000:
        return "B1 常用字"
    if rank <= 8000:
        return "B2 進階字"
    if rank <= 15000:
        return "C1 學術低頻字"
    return "C2 罕用精準字"


def _corpus_band(rank, corpus):
    if rank <= 100:
        return f"{corpus}最高頻字"
    if rank <= 300:
        return f"{corpus}高頻字"
    if rank <= 700:
        return f"{corpus}常用字"
    if rank <= 1500:
        return f"{corpus}次常用字"
    return f"{corpus}進階字"


# ════════════════════════════════════════════════════════════════════════════
#  harvest 解析器（每個回 list[candidate dict]）
#  candidate: {word, reading, pos, en_gloss, category, level, freq_rank, source}
# ════════════════════════════════════════════════════════════════════════════
def _http_text(url):
    r = requests.get(url, timeout=300)
    r.raise_for_status()
    r.encoding = "utf-8"
    return r.text


def harvest_freqwords(lang, target):
    txt = _http_text(f"{FREQ_BASE}/{lang}/{lang}_50k.txt")
    word_re = re.compile(r"^[a-zà-öø-ÿäöüßçéèêëàâîïôûùœ'’\-]{2,}$", re.I)
    out, rank = [], 0
    for line in txt.splitlines():
        parts = line.split()
        if len(parts) != 2:
            continue
        w = parts[0].strip().lower()
        if not word_re.match(w) or w.startswith("'") or w.endswith("'"):
            continue
        rank += 1
        if rank > target:
            break
        out.append({"word": w, "reading": None, "pos": None, "en_gloss": None,
                    "category": _cefr_band(rank), "level": _cefr_band(rank).split()[0],
                    "freq_rank": rank, "source": "freqwords"})
    return out


def harvest_jlpt(target):
    out = []
    for lvl in (5, 4, 3, 2, 1):
        try:
            data = json.loads(_http_text(f"https://jlpt-vocab-api.vercel.app/api/words/all?level={lvl}"))
        except Exception as e:  # noqa: BLE001
            print(f"  ! JLPT N{lvl} 取得失敗：{e}", flush=True)
            continue
        seen = set()
        for d in data:
            w = (d.get("word") or "").strip()
            if not w or w in seen:
                continue
            seen.add(w)
            out.append({"word": w, "reading": (d.get("furigana") or d.get("romaji") or None),
                        "pos": None, "en_gloss": d.get("meaning"),
                        "category": f"JLPT N{lvl} 單字", "level": f"N{lvl}",
                        "freq_rank": None, "source": "jlpt"})
        print(f"  JLPT N{lvl}: {len(data)} 筆", flush=True)
        if len(out) >= target:
            break
    return out


_GK_POS = {"N": "名詞", "A": "形容詞", "V": "動詞", "D": "副詞", "C": "連接詞",
           "P": "介系詞", "R": "代名詞", "T": "冠詞", "X": "質詞", "I": "感嘆詞"}


def harvest_stepbible_greek(target):
    files = ["TAGNT%20Mat-Jhn%20-%20Translators%20Amalgamated%20Greek%20NT%20-%20STEPBible.org%20CC-BY.txt",
             "TAGNT%20Act-Rev%20-%20Translators%20Amalgamated%20Greek%20NT%20-%20STEPBible.org%20CC-BY.txt"]
    freq, info = {}, {}
    lemma_re = re.compile(r"([Ͱ-Ͽἀ-῿]{2,})=([^\t]+)")
    for fn in files:
        txt = _http_text(f"{STEP_BASE}/{fn}")
        for line in txt.splitlines():
            if not line or line[0] in "#\t =" or "." not in line[:12]:
                continue
            cols = line.split("\t")
            if len(cols) < 5 or "#" not in cols[0]:
                continue
            ref = cols[0].split("#")[0]
            book = ref.split(".")[0]
            # 詞元 + 英義在「字典形=英義」欄（通常第 5 欄 index 4）
            mfield = next((c for c in cols[3:6] if lemma_re.search(c)), None)
            if not mfield:
                continue
            mm = lemma_re.search(mfield)
            lemma, gloss = mm.group(1), mm.group(2).strip()
            # 詞性：morph 欄 like G0976=N-NSF
            pos = None
            for c in cols[2:5]:
                pm = re.search(r"=([A-Z])-?", c)
                if pm:
                    pos = _GK_POS.get(pm.group(1))
                    break
            freq[lemma] = freq.get(lemma, 0) + 1
            if lemma not in info:
                info[lemma] = {"gloss": gloss, "pos": pos, "book": book}
    ranked = sorted(freq.items(), key=lambda kv: -kv[1])
    out = []
    for rank, (lemma, _cnt) in enumerate(ranked[:target], start=1):
        meta = info[lemma]
        out.append({"word": lemma, "reading": None, "pos": meta["pos"], "en_gloss": meta["gloss"],
                    "category": _corpus_band(rank, "新約"), "level": "入門" if rank <= 700 else "進階",
                    "freq_rank": rank, "source": "stepbible"})
    return out


_HEB_POS = {"N": "名詞", "V": "動詞", "A": "形容詞", "D": "副詞", "C": "連接詞",
            "R": "介系詞", "P": "代名詞", "T": "冠詞"}


def harvest_stepbible_hebrew(target):
    files = ["TAHOT%20Gen-Deu%20-%20Translators%20Amalgamated%20Hebrew%20OT%20-%20STEPBible.org%20CC%20BY.txt",
             "TAHOT%20Jos-Est%20-%20Translators%20Amalgamated%20Hebrew%20OT%20-%20STEPBible.org%20CC%20BY.txt",
             "TAHOT%20Job-Sng%20-%20Translators%20Amalgamated%20Hebrew%20OT%20-%20STEPBible.org%20CC%20BY.txt",
             "TAHOT%20Isa-Mal%20-%20Translators%20Amalgamated%20Hebrew%20OT%20-%20STEPBible.org%20CC%20BY.txt"]
    # 詞元段：{H1254A=בָּרָא=to create} 或 H7225G=רֵאשִׁית=: beginning ；跳過 H9xxx 文法語素
    seg_re = re.compile(r"\{?(H\d{4}[A-Z]?)=([֐-׿][֐-׿֑-ׇ]*)=([^/}=]*)")
    freq, info = {}, {}
    for fn in files:
        txt = _http_text(f"{STEP_BASE}/{fn}")
        for line in txt.splitlines():
            if not line or "." not in line[:12] or "#" not in line[:12]:
                continue
            cols = line.split("\t")
            if len(cols) < 6:
                continue
            morph = cols[5] if len(cols) > 5 else ""
            # 詞元段落散在尾欄（可能有多個空白尾欄）→ 直接掃整行，只有詞元欄含 =希伯來文=英義
            for m in seg_re.finditer(line):
                strong, lemma, gloss = m.group(1), m.group(2), m.group(3).strip(" :»").split("»")[0].strip()
                if strong.startswith("H9"):
                    continue
                pos = None
                pm = re.search(r"H[A-Z]?([A-Z])", morph)
                if pm:
                    pos = _HEB_POS.get(pm.group(1))
                freq[lemma] = freq.get(lemma, 0) + 1
                if lemma not in info:
                    info[lemma] = {"gloss": gloss or None, "pos": pos}
    ranked = sorted(freq.items(), key=lambda kv: -kv[1])
    out = []
    for rank, (lemma, _cnt) in enumerate(ranked[:target], start=1):
        meta = info[lemma]
        out.append({"word": lemma, "reading": None, "pos": meta["pos"], "en_gloss": meta["gloss"],
                    "category": _corpus_band(rank, "舊約"), "level": "入門" if rank <= 700 else "進階",
                    "freq_rank": rank, "source": "stepbible"})
    return out


def harvest_vulgate(target):
    """Clementine Vulgate USFX → 表面詞頻（詞元由 gloss 階段 LLM 還原）。多取 2.5x 緩衝去重。"""
    xml = _http_text("https://raw.githubusercontent.com/seven1m/open-bibles/master/lat-clementine.usfx.xml")
    xml = re.sub(r"<[^>]+>", " ", xml)
    # 武加大用 æ œ 與分音符 ë ï（Israël/Beëlzebub）— 一併納入再正規化，避免在重音處被切斷
    diac = str.maketrans({"æ": "ae", "œ": "oe", "ë": "e", "ï": "i", "ü": "u",
                          "â": "a", "ê": "e", "î": "i", "ô": "o", "û": "u", "é": "e", "è": "e"})
    freq = {}
    for tok in re.findall(r"[A-Za-zÆæŒœËëÏïÜüÂâÊêÎîÔôÛûÉéÈè]+", xml):
        w = tok.lower().translate(diac)
        if len(w) < 3:
            continue
        freq[w] = freq.get(w, 0) + 1
    ranked = sorted(freq.items(), key=lambda kv: -kv[1])
    out = []
    for rank, (surf, _cnt) in enumerate(ranked[:int(target * 2.5)], start=1):
        out.append({"word": surf, "reading": None, "pos": None, "en_gloss": None,
                    "category": _corpus_band(rank, "武加大"), "level": "入門" if rank <= 700 else "進階",
                    "freq_rank": rank, "source": "vulgate-surface"})
    return out


def harvest_stepbible_aramaic(target):
    """聖經亞蘭文：但以理／以斯拉的亞蘭文段落（TAHOT 中 morph 以 A 開頭者）。整部窮盡 ~700 詞元。"""
    files = ["TAHOT%20Jos-Est%20-%20Translators%20Amalgamated%20Hebrew%20OT%20-%20STEPBible.org%20CC%20BY.txt",  # Ezra
             "TAHOT%20Isa-Mal%20-%20Translators%20Amalgamated%20Hebrew%20OT%20-%20STEPBible.org%20CC%20BY.txt"]  # Daniel
    seg_re = re.compile(r"\{?(H\d{4}[A-Z]?)=([֐-׿][֐-׿֑-ׇ]*)=([^/}=]*)")
    freq, info = {}, {}
    for fn in files:
        txt = _http_text(f"{STEP_BASE}/{fn}")
        for line in txt.splitlines():
            head = line[:12]
            if "." not in head or "#" not in head:
                continue
            cols = line.split("\t")
            if len(cols) < 6 or not cols[5].startswith("A"):  # 只取亞蘭文（morph 首字 A）
                continue
            pos = None
            pm = re.match(r"A([A-Z])", cols[5])
            if pm:
                pos = _HEB_POS.get(pm.group(1))
            for m in seg_re.finditer(line):
                strong, lemma, gloss = m.group(1), m.group(2), m.group(3).strip(" :»").split("»")[0].strip()
                if strong.startswith("H9"):
                    continue
                freq[lemma] = freq.get(lemma, 0) + 1
                if lemma not in info:
                    info[lemma] = {"gloss": gloss or None, "pos": pos}
    ranked = sorted(freq.items(), key=lambda kv: -kv[1])
    out = []
    for rank, (lemma, _c) in enumerate(ranked[:target], start=1):
        meta = info[lemma]
        out.append({"word": lemma, "reading": None, "pos": meta["pos"], "en_gloss": meta["gloss"],
                    "category": _corpus_band(rank, "聖經亞蘭文"), "level": "入門" if rank <= 300 else "進階",
                    "freq_rank": rank, "source": "stepbible"})
    return out


def _http_raw(url):
    r = requests.get(url, timeout=300)
    r.raise_for_status()
    return r.content


def _rank_surface(freq, target, corpus, source):
    """表面詞頻 → 候選（詞元由 gloss 階段 LLM 還原，仿武加大）。多取 2.5x 緩衝。"""
    ranked = sorted(freq.items(), key=lambda kv: -kv[1])
    out = []
    for rank, (surf, _c) in enumerate(ranked[:int(target * 2.5)], start=1):
        out.append({"word": surf, "reading": None, "pos": None, "en_gloss": None,
                    "category": _corpus_band(rank, corpus), "level": "入門" if rank <= 700 else "進階",
                    "freq_rank": rank, "source": source})
    return out


def harvest_quran_arabic(target):
    """古蘭阿拉伯文表面詞頻（去 harakat／tatweel，alef-wasla 正規化）。"""
    data = json.loads(_http_text("https://raw.githubusercontent.com/risan/quran-json/main/data/quran.json"))
    text = json.dumps(data, ensure_ascii=False).replace("ٱ", "ا")
    text = re.sub(r"[ً-ْٰـ]", "", text)
    freq = {}
    for w in re.findall(r"[ء-ي]{2,}", text):
        freq[w] = freq.get(w, 0) + 1
    return _rank_surface(freq, target, "古蘭", "quran-surface")


def harvest_sanskrit(target):
    """梵文天城體表面詞頻（《薄伽梵歌》語料；去 danda 與數字）。"""
    data = json.loads(_http_text("https://raw.githubusercontent.com/gita/gita/main/data/verse.json"))
    text = re.sub(r"[।॥०-९]", " ", " ".join(v.get("text", "") for v in data))
    freq = {}
    for w in re.findall(r"[ऀ-ॿ]{2,}", text):
        freq[w] = freq.get(w, 0) + 1
    return _rank_surface(freq, target, "梵典", "gita-surface")


def harvest_pali(target):
    """巴利文羅馬轉寫表面詞頻（VRI 三藏 XML；自動辨識 UTF-16）。"""
    raw = _http_raw("https://raw.githubusercontent.com/VipassanaTech/tipitaka-xml/main/romn/s0201m.mul.xml")
    txt = raw.decode("utf-16") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else raw.decode("utf-8", "ignore")
    txt = re.sub(r"<[^>]+>", " ", txt)
    freq = {}
    for w in re.findall(r"[a-zA-ZāīūṅñṭḍṇḷṃĀĪŪṄÑṬḌṆḶṂ]{2,}", txt):
        w = w.lower()
        freq[w] = freq.get(w, 0) + 1
    return _rank_surface(freq, target, "三藏", "tipitaka-surface")


def harvest_coptic(target):
    """科普特文表面詞頻（eBible 科普特新約 copcnt，薩希德/波海里）。"""
    txt = _http_text("https://raw.githubusercontent.com/BibleNLP/ebible/main/corpus/cop-copcnt.txt")
    freq = {}
    for w in re.findall(r"[Ⲁ-ⳳϢ-ϯ̀-ͯ]{2,}", txt):
        freq[w] = freq.get(w, 0) + 1
    return _rank_surface(freq, target, "科普特新約", "ebible-cop-surface")


def harvest_tibetan(target):
    """藏文表面詞頻（eBible 藏文聖經 bodn）；以 tsheg ་ 斷音節（多數核心詞為單／雙音節）。"""
    txt = _http_text("https://raw.githubusercontent.com/BibleNLP/ebible/main/corpus/bod-bodn.txt")
    freq = {}
    for syl in re.findall(r"[ཀ-ྼཱ-྄]+", txt):
        freq[syl] = freq.get(syl, 0) + 1
    return _rank_surface(freq, target, "藏文聖經", "ebible-bo-surface")


BEBLIA = "https://raw.githubusercontent.com/Beblia/Holy-Bible-XML-Format/master"

def harvest_beblia(fn, char_class, corpus, source, target, strip_marks=None):
    """Beblia 聖經 XML（<verse number=N>…</verse>）→ 指定字符類表面詞頻。"""
    xml = _http_text(f"{BEBLIA}/{fn}")
    joined = " ".join(re.findall(r"<verse[^>]*>([^<]+)</verse>", xml))
    if strip_marks:
        joined = re.sub(strip_marks, "", joined)
    freq = {}
    for w in re.findall(char_class, joined):
        freq[w] = freq.get(w, 0) + 1
    return _rank_surface(freq, target, corpus, source)


# ── 人工策展核心詞庫（無乾淨語料的死語言；word/讀音/繁中義/詞性/attested 例句）──
# 例句一律取自實際銘文／經典，不杜撰文法。每筆：(word, reading, meaning, pos, example)
CURATED = {
    # 古波斯文（阿契美尼德楔形）— 詞彙與例句取自貝希斯敦銘文（DB）等王室銘文
    "peo": [
        ("𐎠𐎭𐎶", "adam", "我", "代名詞", "𐎠𐎭𐎶 𐎭𐎠𐎼𐎹𐎺𐎢𐏁 = adam Dārayavauš（我，大流士）"),
        ("𐎭𐎠𐎼𐎹𐎺𐎢𐏁", "Dārayavauš", "大流士（王名）", "專有名詞", "adam Dārayavauš xšāyaθiya（我大流士王）"),
        ("𐎧𐏁𐎠𐎹𐎰𐎡𐎹", "xšāyaθiya", "王", "名詞", "xšāyaθiya xšāyaθiyānām（萬王之王）"),
        ("𐎧𐏁𐏂", "xšaça", "王權／國度", "名詞", "Auramazdā xšaçam manā frābara（阿胡拉馬茲達賜我王權）"),
        ("𐎲𐎥", "baga", "神", "名詞", "baga vazraka Auramazdā（偉大的神阿胡拉馬茲達）"),
        ("𐎠𐎢𐎼𐎶𐏀𐎭𐎠", "Auramazdā", "阿胡拉‧馬茲達（至高神）", "專有名詞", "vašnā Auramazdāha（藉阿胡拉馬茲達的恩寵）"),
        ("𐎺𐏀𐎼𐎣", "vazraka", "偉大的", "形容詞", "baga vazraka（偉大的神）"),
        ("𐎲𐎴𐎡𐎹", "būmi", "地", "名詞", "imām būmim（這片大地）"),
        ("𐎠𐎿𐎶𐎠𐎴", "asmān", "天", "名詞", "avam asmānam（那天）"),
        ("𐎶𐎼𐎫𐎡𐎹", "martiya", "人／男子", "名詞", "martiya hya drujana（說謊的人）"),
        ("𐎭𐀷𐎹𐎠𐎢𐏁", "dahyāuš", "國／行省", "名詞", "imā dahyāva（這些行省）"),
        ("𐎣𐎠𐎼", "kāra", "軍隊／人民", "名詞", "kāra Pārsa（波斯軍民）"),
        ("𐎠𐎼𐎫", "arta", "真理／正義（Asha）", "名詞", "artāvā（正義者）"),
        ("𐎭𐎼𐎢𐎥", "drauga", "謊言（Druj）", "名詞", "drauga dahyauvā vasiy abava（謊言在國中大增）"),
        ("𐎰𐎠𐎫𐎡𐎹", "θātiy", "說（他說）", "動詞", "θātiy Dārayavauš xšāyaθiya（大流士王說）"),
        ("𐎠𐎤𐎢𐎴𐎺𐎶", "akunavam", "我做了／建造", "動詞", "ima taya adam akunavam（這是我所做的）"),
        ("𐎺𐏁𐎴𐎠", "vašnā", "藉…的恩寵", "名詞", "vašnā Auramazdāha（藉阿胡拉馬茲達的恩寵）"),
        ("𐎱𐎿𐎠𐎺", "pasāva", "然後", "副詞", "pasāva adam（然後我…）"),
        ("𐎲𐎢𐎷𐎡𐎹", "bumiš", "土地", "名詞", "—"),
        ("𐎰𐎼𐎭", "θard", "年", "名詞", "—"),
    ],
    # 腓尼基-布匿文 — 詞彙與套語取自腓尼基/布匿銘文（Ahiram, Kilamuwa, Karatepe, 迦太基還願碑）
    "phn": [
        ("𐤀𐤋", "ʾl", "神（El）", "名詞", "𐤋𐤓𐤁𐤕 = l-rbt（獻給女神…）"),
        ("𐤁𐤏𐤋", "bʿl", "主／巴力", "名詞", "𐤁𐤏𐤋 𐤔𐤌𐤌 = baʿal šamem（天主巴力）"),
        ("𐤌𐤋𐤊", "mlk", "王", "名詞", "𐤀𐤍𐤊 𐤊𐤋𐤌𐤅 𐤌𐤋𐤊 = ʾnk klmw mlk（我是王基拉姆瓦）"),
        ("𐤒𐤓𐤕", "qrt", "城", "名詞", "𐤒𐤓𐤕 𐤇𐤃𐤔𐤕 = Qart-ḥadašt（新城＝迦太基）"),
        ("𐤕𐤍𐤕", "tnt", "塔尼特（女神）", "專有名詞", "𐤋𐤓𐤁𐤕 𐤋𐤕𐤍𐤕 = l-rbt l-tnt（獻給塔尼特女神）"),
        ("𐤏𐤔𐤕𐤓𐤕", "ʿštrt", "阿斯塔特（女神）", "專有名詞", "—"),
        ("𐤌𐤋𐤒𐤓𐤕", "mlqrt", "美刻爾特（推羅主神）", "專有名詞", "—"),
        ("𐤊𐤄𐤍", "khn", "祭司", "名詞", "—"),
        ("𐤏𐤁𐤃", "ʿbd", "僕人", "名詞", "𐤏𐤁𐤃 𐤌𐤋𐤒𐤓𐤕 = ʿbd-mlqrt（美刻爾特的僕人）"),
        ("𐤁𐤍", "bn", "兒子", "名詞", "𐤁𐤍 𐤀𐤇𐤓𐤌 = bn ʾḥrm（阿希拉姆之子）"),
        ("𐤀𐤁", "ʾb", "父", "名詞", "—"),
        ("𐤁𐤕", "bt", "房屋／家／殿", "名詞", "—"),
        ("𐤀𐤓𐤑", "ʾrṣ", "地", "名詞", "—"),
        ("𐤔𐤌𐤔", "šmš", "太陽", "名詞", "—"),
        ("𐤔𐤌", "šm", "名", "名詞", "—"),
        ("𐤆𐤁𐤇", "zbḥ", "獻祭", "名詞", "—"),
        ("𐤍𐤃𐤓", "ndr", "還願", "名詞", "𐤀𐤔 𐤍𐤃𐤓 = ʾš ndr（所許之願）"),
        ("𐤁𐤓𐤊", "brk", "祝福", "動詞", "𐤉𐤁𐤓𐤊 = ybrk（願…賜福）"),
        ("𐤔𐤌𐤏", "šmʿ", "聽", "動詞", "𐤊 𐤔𐤌𐤏 𐤒𐤋 = kī šamaʿ qōl（因他聽了聲音）"),
        ("𐤀𐤃𐤌", "ʾdm", "人", "名詞", "—"),
    ],
    # 烏加列文 — 詞彙取自《巴力史詩》等 RS 泥板（楔形字母）
    "uga": [
        ("𐎛𐎍", "ʾil", "神（El，眾神之父）", "名詞", "𐎛𐎍 𐎎𐎍𐎋 = ʾil malku（厄勒王）"),
        ("𐎁𐎓𐎍", "bʿl", "巴力（風暴神）", "名詞", "𐎀𐎍𐎊𐎐 𐎁𐎓𐎍 = ʾalʾiyānu baʿlu（大能的巴力）"),
        ("𐎓𐎐𐎚", "ʿnt", "阿娜特（戰神女）", "專有名詞", "𐎁𐎚𐎍𐎚 𐎓𐎐𐎚 = batultu ʿanatu（少女阿娜特）"),
        ("𐎀𐎘𐎗𐎚", "aṯrt", "阿舍拉（母神）", "專有名詞", "—"),
        ("𐎊𐎎", "ym", "海／亞姆（海神）", "名詞", "𐎏𐎁𐎍 𐎊𐎎 = zbl ym（海王子亞姆）"),
        ("𐎎𐎚", "mt", "死／莫特（死神）", "名詞", "𐎁𐎐 𐎛𐎍𐎎 𐎎𐎚 = bn ʾilm mt（神子莫特）"),
        ("𐎌𐎔𐎌", "špš", "沙帕舒（太陽女神）", "專有名詞", "—"),
        ("𐎎𐎍𐎋", "mlk", "王", "名詞", "—"),
        ("𐎀𐎁", "ab", "父", "名詞", "𐎀𐎁 𐎌𐎐𐎎 = ʾabu šanīma（歲月之父，El 的稱號）"),
        ("𐎁𐎐", "bn", "兒子", "名詞", "𐎁𐎐 𐎛𐎍𐎎 = banū ʾilīma（諸神之子）"),
        ("𐎁𐎚", "bt", "房屋／家", "名詞", "𐎁𐎚 𐎁𐎓𐎍 = bētu baʿli（巴力的殿）"),
        ("𐎀𐎗𐎕", "arṣ", "地", "名詞", "—"),
        ("𐎌𐎎𐎎", "šmm", "天", "名詞", "—"),
        ("𐎌𐎎", "šm", "名", "名詞", "—"),
        ("𐎓𐎁𐎄", "ʿbd", "僕人", "名詞", "—"),
        ("𐎄𐎁𐎈", "dbḥ", "獻祭", "名詞", "—"),
        ("𐎗𐎁", "rb", "大／首領", "形容詞", "𐎗𐎁 𐎋𐎅𐎐𐎎 = rabbu kāhinīma（大祭司）"),
        ("𐎉𐎁", "ṭb", "好", "形容詞", "—"),
    ],
    # 教會斯拉夫文 — 禮儀核心詞（西里爾），例句取自主禱文／禮儀套語
    "chu": [
        ("Богъ", "Bog", "神", "名詞", "вѣрую во единаго Бога（我信獨一的神）"),
        ("Господь", "Gospodĭ", "主", "名詞", "Господи помилуй（主，憐憫）"),
        ("Христосъ", "Hristos", "基督", "名詞", "Іисусъ Христосъ（耶穌基督）"),
        ("Духъ", "Duh", "靈", "名詞", "Духъ Святый（聖靈）"),
        ("святъ", "svęt", "聖的", "形容詞", "Святъ, Святъ, Святъ（聖哉，聖哉，聖哉）"),
        ("слово", "slovo", "道／話語", "名詞", "въ началѣ бѣ Слово（太初有道）"),
        ("небо", "nebo", "天", "名詞", "Ѻтче нашъ, иже еси на небесѣхъ（我們在天上的父）"),
        ("земля", "zemlja", "地", "名詞", "—"),
        ("человѣкъ", "člověk", "人", "名詞", "—"),
        ("отецъ", "otĭc", "父", "名詞", "Ѻтче нашъ（我們的父）"),
        ("сынъ", "syn", "子", "名詞", "Сынъ Божій（神之子）"),
        ("мати", "mati", "母", "名詞", "Мати Божія（神之母）"),
        ("царь", "carĭ", "王", "名詞", "Царю Небесный（天上的君王）"),
        ("вѣра", "věra", "信德", "名詞", "—"),
        ("любы", "ljuby", "愛", "名詞", "—"),
        ("миръ", "mir", "和平／世界", "名詞", "миръ всѣмъ（願眾人平安）"),
        ("ангелъ", "angel", "天使", "名詞", "—"),
        ("церковь", "crĭky", "教會", "名詞", "—"),
        ("молитва", "molitva", "禱告", "名詞", "—"),
        ("крестъ", "krĭst", "十字架", "名詞", "—"),
        ("слава", "slava", "榮耀", "名詞", "слава Тебѣ（榮耀歸於你）"),
        ("аминь", "aminĭ", "阿們", "感嘆詞", "—"),
    ],
    # 吉茲文 — 禮儀核心詞（fidäl），例句取自衣索比亞正教禮儀套語
    "gez": [
        ("እግዚአብሔር", "ʾəgziʾabəḥer", "神／主", "名詞", "ስብሐት ለእግዚአብሔር（榮耀歸於神）"),
        ("ክርስቶስ", "krəstos", "基督", "名詞", "ኢየሱስ ክርስቶስ（耶穌基督）"),
        ("መንፈስ", "mänfäs", "靈", "名詞", "መንፈስ ቅዱስ（聖靈）"),
        ("ቅዱስ", "qəddus", "聖的", "形容詞", "ቅዱስ ቅዱስ ቅዱስ（聖哉，聖哉，聖哉）"),
        ("ሰማይ", "sämay", "天", "名詞", "—"),
        ("ምድር", "mədr", "地", "名詞", "ሰማየ ወምድረ（天與地）"),
        ("ሰብእ", "säbʾ", "人", "名詞", "—"),
        ("አብ", "ʾab", "父", "名詞", "አብ ወወልድ ወመንፈስ ቅዱስ（父、子、聖靈）"),
        ("ወልድ", "wäld", "子", "名詞", "ወልደ እግዚአብሔር（神之子）"),
        ("እም", "ʾəm", "母", "名詞", "—"),
        ("ንጉሥ", "nəguś", "王", "名詞", "ንጉሠ ነገሥት（萬王之王）"),
        ("ሃይማኖት", "haymanot", "信仰", "名詞", "—"),
        ("ፍቅር", "fəqr", "愛", "名詞", "—"),
        ("ሰላም", "sälam", "平安", "名詞", "ሰላም ለኪ（向你問安）"),
        ("ጸሎት", "ṣälot", "禱告", "名詞", "—"),
        ("መስቀል", "mäsqäl", "十字架", "名詞", "—"),
        ("ቤት", "bet", "房屋／殿", "名詞", "ቤተ ክርስቲያን（教會）"),
        ("ሕግ", "ḥəg", "律法", "名詞", "—"),
        ("መልአክ", "mälʾak", "天使", "名詞", "—"),
        ("ብርሃን", "bərhan", "光", "名詞", "—"),
    ],
    # 阿卡德文 — 學界以拉丁轉寫為詞頭（normalized）；例句取自漢摩拉比法典／埃努瑪埃利什
    "akk": [
        ("ilu", "𒀭 DINGIR", "神", "名詞", "ilū rabûtu（偉大的諸神）"),
        ("šarru", "𒈗 LUGAL", "王", "名詞", "šar Bābili（巴比倫之王）"),
        ("bēlu", "EN", "主", "名詞", "bēl mātāti（萬國之主）"),
        ("bītu", "𒂍 É", "房屋／神廟", "名詞", "bīt ili（神的殿）"),
        ("mātu", "𒆳 KUR", "地／國", "名詞", "māt Aššur（亞述地）"),
        ("awīlu", "𒇽 LÚ", "人／自由民", "名詞", "šumma awīlum（倘若一個人…，法典套語）"),
        ("šamû", "AN", "天", "名詞", "enūma eliš lā nabû šamāmū（當高天尚未命名時）"),
        ("erṣetu", "KI", "地", "名詞", "šamû u erṣetu（天與地）"),
        ("abu", "AD", "父", "名詞", "—"),
        ("ummu", "AMA", "母", "名詞", "—"),
        ("māru", "DUMU", "兒子", "名詞", "mār šarri（王子）"),
        ("ūmu", "UD", "日", "名詞", "—"),
        ("libbu", "ŠÀ", "心", "名詞", "—"),
        ("qātu", "ŠU", "手", "名詞", "—"),
        ("rabû", "GAL", "大的", "形容詞", "ilu rabû（偉大的神）"),
        ("damqu", "SIG₅", "好的", "形容詞", "—"),
        ("alāku", "DU", "走／去", "動詞", "—"),
        ("qabû", "DUG₄", "說", "動詞", "—"),
        ("epēšu", "DÙ", "做／建造", "動詞", "—"),
        ("balāṭu", "TIN", "生命", "名詞", "balāṭ ūmī rūqūti（長壽）"),
        ("mūtu", "ÚŠ", "死", "名詞", "—"),
        ("dīnu", "DI", "判決／律法", "名詞", "dīnāt mīšarim（公義的判決）"),
    ],
    # 古埃及文 — 學界以轉寫為詞頭（不寫母音）；例句取自金字塔文/亡靈書套語
    "egy": [
        ("nṯr", "neter", "神", "名詞", "nṯr ꜥꜣ（偉大的神）"),
        ("nswt", "nesut", "王", "名詞", "nswt-bjtj（上下埃及之王）"),
        ("pr", "per", "房屋／宮殿", "名詞", "pr-ꜥꜣ（大宅＝法老 pharaoh）"),
        ("rmṯ", "remetj", "人", "名詞", "—"),
        ("tꜣ", "ta", "地", "名詞", "tꜣ.wj（兩地＝上下埃及）"),
        ("pt", "pet", "天", "名詞", "—"),
        ("rꜥ", "Ra", "太陽／拉神", "名詞", "rꜥ nb（每日／拉是主）"),
        ("mꜣꜥt", "maat", "瑪阿特（真理/秩序）", "名詞", "mꜣꜥt nb（真理之主）"),
        ("ꜥnḫ", "ankh", "生命／活", "名詞", "ꜥnḫ wḏꜣ snb（生命、繁榮、健康，王名套語）"),
        ("jt", "it", "父", "名詞", "jt nṯr（神之父）"),
        ("mwt", "mut", "母", "名詞", "—"),
        ("sꜣ", "sa", "兒子", "名詞", "sꜣ rꜥ（拉之子，王銜）"),
        ("nb", "neb", "主／一切", "名詞", "nb tꜣ.wj（兩地之主）"),
        ("ḥm", "hem", "陛下／僕", "名詞", "ḥm=f（其陛下）"),
        ("kꜣ", "ka", "卡（生命力/靈）", "名詞", "—"),
        ("bꜣ", "ba", "巴（魂）", "名詞", "—"),
        ("ḏt", "djet", "永恆（不變）", "名詞", "ḏt nḥḥ（永永遠遠）"),
        ("wsjr", "Osiris", "歐西里斯", "名詞", "—"),
        ("ḥrw", "Horus", "荷魯斯", "名詞", "—"),
        ("ḥtp", "hetep", "供奉／平安", "名詞", "ḥtp dj nswt（王所賜的供品，祭文套語）"),
    ],
    # 阿維斯陀文 — 學界以拉丁轉寫為詞頭；例句取自《迦薩》與核心禱文
    "ae": [
        ("ahura", "ahura", "主／阿胡拉", "名詞", "ahurō mazdā（主智者）"),
        ("mazdā", "mazdā", "馬茲達（智慧）", "名詞", "ahura mazdā（阿胡拉馬茲達）"),
        ("aṣ̌a", "aša", "真理／正義（Asha）", "名詞", "aṣ̌əm vohū（真理是善，禱文）"),
        ("vohu", "vohu", "善的", "形容詞", "vohu manah（善思）"),
        ("manah", "manah", "心思", "名詞", "vohu manah（善思 Vohu Manah）"),
        ("spəṇta", "spənta", "神聖的／增益的", "形容詞", "spəṇta mainyu（神聖之靈）"),
        ("mainiiu", "mainyu", "靈", "名詞", "aŋra mainyu（惡靈 Angra Mainyu）"),
        ("aŋra", "aŋra", "惡的", "形容詞", "aŋra mainyu（惡靈）"),
        ("daēuua", "daēva", "惡神／魔", "名詞", "—"),
        ("druj", "druj", "謊言／欺（Druj）", "名詞", "—"),
        ("yasna", "yasna", "祭祀／崇拜", "名詞", "—"),
        ("gāθā", "gāθā", "迦薩（頌歌）", "名詞", "—"),
        ("zaraθuštra", "Zaraθuštra", "查拉圖斯特拉", "名詞", "—"),
        ("ātar", "ātar", "火", "名詞", "ātarš（聖火）"),
        ("ap", "ap", "水", "名詞", "—"),
        ("xšaθra", "xšaθra", "王權／國度", "名詞", "xšaθrəm vairīm（可選的王國，禱文）"),
        ("ārmaiti", "ārmaiti", "虔敬", "名詞", "—"),
        ("ahu", "ahu", "存有／主宰", "名詞", "yaθā ahū vairyō（如至上的主宰，Ahuna Vairya）"),
        ("ratu", "ratu", "典範／導師", "名詞", "—"),
        ("haurvatāt", "haurvatāt", "完整／健全", "名詞", "—"),
    ],
    # 半摩揭陀俗語 — 天城體＋轉寫；耆那核心術語，例句取自《阿含經》概念
    "pra": [
        ("जीव", "jīva", "命／靈魂", "名詞", "savve jīvā（一切眾生）"),
        ("अजीव", "ajīva", "非命／無情物", "名詞", "jīva ajīva（命與非命）"),
        ("धम्म", "dhamma", "法", "名詞", "—"),
        ("अहिंसा", "ahiṃsā", "不害", "名詞", "ahiṃsā paramo dhammo（不害是最高的法）"),
        ("कम्म", "kamma", "業", "名詞", "—"),
        ("मोक्ख", "mokkha", "解脫", "名詞", "—"),
        ("संसार", "saṃsāra", "輪迴", "名詞", "—"),
        ("जिण", "jiṇa", "耆那／勝者", "名詞", "—"),
        ("तित्थयर", "titthayara", "祖師（渡津者）", "名詞", "—"),
        ("आया", "āyā", "我／自我（ātman）", "名詞", "ege āyā（唯一的我）"),
        ("णाण", "ṇāṇa", "智（jñāna）", "名詞", "ṇāṇa daṃsaṇa（智與見）"),
        ("दंसण", "daṃsaṇa", "見（darśana）", "名詞", "—"),
        ("चरित्त", "caritta", "行（cāritra）", "名詞", "—"),
        ("दुक्ख", "dukkha", "苦", "名詞", "—"),
        ("सुह", "suha", "樂", "名詞", "—"),
        ("सव्व", "savva", "一切", "形容詞", "savve pāṇā（一切生靈）"),
        ("पाण", "pāṇa", "生靈／氣息", "名詞", "—"),
        ("तव", "tava", "苦行（tapas）", "名詞", "—"),
    ],
    # 曼達文 — 曼達字母＋轉寫；曼達教核心詞（諾斯底）
    "mid": [
        ("ࡌࡀࡍࡃࡀ", "manda", "知識／覺知（gnosis）", "名詞", "manda d-hiia（生命的知識）"),
        ("ࡄࡉࡉࡀ", "hiia", "生命", "名詞", "hiia rbia（大生命，至高存有）"),
        ("ࡍࡄࡅࡓࡀ", "nhura", "光", "名詞", "alma d-nhura（光明界）"),
        ("ࡄࡔࡅࡊࡀ", "hšuka", "黑暗", "名詞", "alma d-hšuka（黑暗界）"),
        ("ࡀࡋࡌࡀ", "alma", "世界／界域", "名詞", "alma d-nhura（光明界）"),
        ("ࡊࡅࡔࡈࡀ", "kušṭa", "真理／真實", "名詞", "—"),
        ("ࡌࡀࡋࡊࡀ", "malka", "王", "名詞", "malka d-nhura（光明之王）"),
        ("ࡓࡅࡄࡀ", "ruha", "靈（亦指墮落女靈）", "名詞", "—"),
        ("ࡉࡀࡓࡃࡍࡀ", "yardna", "約旦河／活水", "名詞", "masbuta b-yardna（在活水中受洗）"),
        ("ࡕࡀࡓࡌࡉࡃࡀ", "tarmida", "祭司", "名詞", "—"),
        ("ࡌࡔࡉࡄࡀ", "mšiha", "彌賽亞", "名詞", "—"),
        ("ࡀࡃࡀࡌ", "adam", "亞當／人", "名詞", "—"),
        ("ࡌࡀࡍࡀ", "mana", "心智／器皿（靈魂）", "名詞", "—"),
        ("ࡁࡉࡕ", "bit", "房屋", "名詞", "—"),
        ("ࡔࡅࡌࡀ", "šuma", "名", "名詞", "b-šuma d-hiia（奉生命之名）"),
    ],
    # 阿美語 — 教育部族語書寫系統核心詞（保守高把握：數字/親屬/自然/信仰）；例句從略（不杜撰文法）
    "ami": [
        ("cecay", None, "一", "數詞", "—"), ("tosa", None, "二", "數詞", "—"),
        ("tolo", None, "三", "數詞", "—"), ("sepat", None, "四", "數詞", "—"),
        ("lima", None, "五", "數詞", "—"), ("enem", None, "六", "數詞", "—"),
        ("pito", None, "七", "數詞", "—"), ("falo", None, "八", "數詞", "—"),
        ("siwa", None, "九", "數詞", "—"), ("mo'tep", None, "十", "數詞", "—"),
        ("tamdaw", None, "人", "名詞", "—"), ("wama", None, "父親", "名詞", "—"),
        ("wina", None, "母親", "名詞", "—"), ("wawa", None, "孩子", "名詞", "—"),
        ("loma'", None, "家／房屋", "名詞", "—"), ("cidal", None, "太陽／日", "名詞", "—"),
        ("folad", None, "月亮", "名詞", "—"), ("nanom", None, "水", "名詞", "—"),
        ("riyar", None, "海", "名詞", "—"), ("kilang", None, "樹", "名詞", "—"),
        ("Kawas", None, "神靈／祖靈（傳統信仰）", "名詞", "—"),
        ("Nga'ay ho", None, "你好（問候語）", "片語", "—"),
    ],
    # 泰雅語 — 教育部族語書寫系統核心詞（保守高把握）；例句從略
    "tay": [
        ("qutux", None, "一", "數詞", "—"), ("sazing", None, "二", "數詞", "—"),
        ("cyugal", None, "三", "數詞", "—"), ("payat", None, "四", "數詞", "—"),
        ("magal", None, "五", "數詞", "—"),
        ("squliq", None, "人", "名詞", "—"), ("yaba", None, "父親", "名詞", "—"),
        ("yaya", None, "母親", "名詞", "—"), ("laqi", None, "孩子", "名詞", "—"),
        ("mlikuy", None, "男人", "名詞", "—"), ("kneril", None, "女人", "名詞", "—"),
        ("ngasal", None, "家／房屋", "名詞", "—"), ("wagi", None, "太陽", "名詞", "—"),
        ("qsya'", None, "水", "名詞", "—"), ("rgyax", None, "山", "名詞", "—"),
        ("llyung", None, "河", "名詞", "—"),
        ("utux", None, "祖靈／神靈（傳統信仰）", "名詞", "—"),
        ("gaga", None, "祖訓／規範（gaya）", "名詞", "—"),
    ],
}


def harvest_curated(lang):
    out = []
    for rank, (w, rd, mean, pos, ex) in enumerate(CURATED[lang], start=1):
        out.append({"word": w, "reading": rd, "meaning": mean, "pos": pos,
                    "example": (ex if ex and ex != "—" else None),
                    "category": "核心詞", "level": "入門", "freq_rank": rank,
                    "source": "curated", "preglossed": True})
    return out


def _moedict_example(exs):
    """萌典例句標記：台語 ￹漢字￺台羅￻華義 或 客語 ￹客語￻華義 → 清成可讀字串。"""
    if not exs:
        return None
    m = re.match(r"￹(.+?)￺(.+?)￻(.*)", exs[0]) or re.match(r"￹(.+?)￻(.*)", exs[0])
    if not m:
        return exs[0].replace("￹", "").replace("￺", "（").replace("￻", "）")[:160]
    g = m.groups()
    out = f"{g[0]}（{g[1]}）{g[2]}" if len(g) == 3 else f"{g[0]}　{g[1]}"
    return out.strip()[:160]


def _parse_moedict(url, source, corpus, limit, hakka=False):
    """g0v 萌典資料（台語/客語）→ 已含繁中釋義+例句的完整候選（preglossed，免 LLM）。
    客語多腔讀音取四縣腔；跳過本字未定（□）詞條。"""
    data = json.loads(_http_text(url))
    rows = []
    for entry in data:
        title = (entry.get("title") or "").strip()
        hets = entry.get("heteronyms") or []
        if not title or "□" in title or not hets:   # 本字未定字跳過
            continue
        het = hets[0]
        trs = (het.get("trs") or het.get("pinyin") or "").strip()
        if hakka and trs:                            # 客語多腔，取四縣腔（四⃞…）
            mm = re.search("四⃞(\\S+)", trs)
            trs = mm.group(1) if mm else trs.split()[0]
        reading = re.sub("[⃞⃣]", "", trs) or None  # 去除腔別方框標記
        defs = het.get("definitions") or []
        meaning = "；".join(d.get("def", "").strip() for d in defs if d.get("def"))[:200]
        if not meaning:
            continue
        pos = (defs[0].get("type") if defs else None) or None
        example = None
        for d in defs:
            example = _moedict_example(d.get("example"))
            if example:
                break
        rows.append({"word": title, "reading": reading, "meaning": meaning, "pos": pos,
                     "example": example, "category": corpus, "level": "入門",
                     "stroke": entry.get("stroke_count") or 99, "source": source, "preglossed": True})
    rows.sort(key=lambda r: r["stroke"])  # 筆畫少者（≈較基礎）優先
    out = rows[:limit]
    for rank, r in enumerate(out, start=1):
        r["freq_rank"] = rank
        r.pop("stroke", None)
    return out


HARVESTERS = {
    "en": lambda: harvest_freqwords("en", TARGETS["en"]),
    "es": lambda: harvest_freqwords("es", TARGETS["es"]),
    "nan": lambda: _parse_moedict("https://raw.githubusercontent.com/g0v/moedict-data-twblg/master/dict-twblg.json", "moedict-twblg", "臺灣閩南語常用詞", TARGETS["nan"]),
    "hak": lambda: _parse_moedict("https://raw.githubusercontent.com/g0v/moedict-data-hakka/master/dict-hakka.json", "moedict-hakka", "臺灣客家語常用詞", TARGETS["hak"], hakka=True),
    "peo": lambda: harvest_curated("peo"),   # 古波斯文（人工策展，貝希斯敦銘文核心詞）
    "phn": lambda: harvest_curated("phn"),   # 腓尼基-布匿文（銘文核心詞）
    "uga": lambda: harvest_curated("uga"),   # 烏加列文（巴力史詩核心詞）
    "chu": lambda: harvest_curated("chu"),   # 教會斯拉夫文（禮儀核心詞）
    "gez": lambda: harvest_curated("gez"),   # 吉茲文（禮儀核心詞）
    "akk": lambda: harvest_curated("akk"),   # 阿卡德文（轉寫核心詞）
    "egy": lambda: harvest_curated("egy"),   # 古埃及文（轉寫核心詞）
    "ae": lambda: harvest_curated("ae"),     # 阿維斯陀文（轉寫核心詞）
    "pra": lambda: harvest_curated("pra"),   # 半摩揭陀俗語（天城體核心詞）
    "mid": lambda: harvest_curated("mid"),   # 曼達文（曼達字母核心詞）
    "ami": lambda: harvest_curated("ami"),   # 阿美語（族語書寫系統核心詞）
    "tay": lambda: harvest_curated("tay"),   # 泰雅語（族語書寫系統核心詞）
    "de": lambda: harvest_freqwords("de", TARGETS["de"]),
    "fr": lambda: harvest_freqwords("fr", TARGETS["fr"]),
    "ja": lambda: harvest_jlpt(TARGETS["ja"]),
    "grc": lambda: harvest_stepbible_greek(TARGETS["grc"]),
    "hbo": lambda: harvest_stepbible_hebrew(TARGETS["hbo"]),
    "la": lambda: harvest_vulgate(TARGETS["la"]),
    # 2026-06-22 新增 8 乾淨語料中的 5 個（其餘 syr/cop/bo 語料零碎，後補）
    "arc": lambda: harvest_stepbible_aramaic(TARGETS["arc"]),     # 聖經亞蘭文（重用 TAHOT，A 開頭 morph）
    "att": lambda: harvest_stepbible_greek(TARGETS["att"]),       # 古典希臘文（先共用 grc 新約語料為基底）
    "ar": lambda: harvest_quran_arabic(TARGETS["ar"]),            # 古典阿拉伯文（古蘭表面詞頻）
    "sa": lambda: harvest_sanskrit(TARGETS["sa"]),                # 梵文（薄伽梵歌天城體表面詞頻）
    "pi": lambda: harvest_pali(TARGETS["pi"]),                    # 巴利文（三藏羅馬轉寫表面詞頻）
    "cop": lambda: harvest_coptic(TARGETS["cop"]),                # 科普特文（eBible 科普特新約表面詞頻）
    "bo": lambda: harvest_tibetan(TARGETS["bo"]),                 # 藏文（eBible 藏文聖經，tsheg 斷音節）
    "syr": lambda: harvest_beblia("AramaicBible.xml", r"[܀-ݏ]{2,}", "敘利亞聖經", "beblia-syr-surface",
                                  TARGETS["syr"], strip_marks=r"[ܰ-݊]"),   # Peshitta（敘利亞字體），去母音點
    "hy": lambda: harvest_beblia("ArmenianBible.xml", r"[Ա-Ֆա-և]{2,}", "亞美尼亞聖經", "beblia-hy-surface", TARGETS["hy"]),
    "ka": lambda: harvest_beblia("GeorgianBible.xml", r"[ა-ჿ]{2,}", "喬治亞聖經", "beblia-ka-surface", TARGETS["ka"]),
}

LANG_LABEL = {"en": "英文", "de": "德文", "fr": "法文", "ja": "日文",
              "grc": "通用希臘文（新約 Koine）", "hbo": "聖經希伯來文", "la": "教會拉丁文（武加大）",
              "arc": "聖經亞蘭文", "att": "古典希臘文（Attic）", "ar": "古典阿拉伯文（古蘭）",
              "sa": "梵文", "pi": "巴利文", "cop": "科普特文", "bo": "藏文",
              "es": "西班牙文", "syr": "古典敘利亞文", "hy": "古典亞美尼亞文", "ka": "古典喬治亞文",
              "nan": "台語（臺灣閩南語）", "hak": "客語（臺灣客家語）", "peo": "古波斯文",
              "phn": "腓尼基-布匿文", "uga": "烏加列文", "chu": "教會斯拉夫文", "gez": "吉茲文",
              "akk": "阿卡德文", "egy": "古埃及文", "ae": "阿維斯陀文", "pra": "半摩揭陀俗語", "mid": "曼達文",
              "ami": "阿美語", "tay": "泰雅語"}


def candidates_path(lang):
    return LEDGER_DIR / f"{lang}.candidates.jsonl"


def glossed_path(lang):
    return LEDGER_DIR / f"{lang}.glossed.jsonl"


def cmd_harvest(lang, force=False):
    path = candidates_path(lang)
    if path.exists() and not force:
        n = sum(1 for _ in path.open(encoding="utf-8"))
        print(f"[{lang}] candidates 已存在 {n} 筆（--force 重抓）", flush=True)
        return
    print(f"[{lang}] harvest {LANG_LABEL[lang]} …", flush=True)
    rows = HARVESTERS[lang]()
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"[{lang}] harvested {len(rows)} 候選 → {path}", flush=True)


# ════════════════════════════════════════════════════════════════════════════
#  gloss：逐批補繁中釋義/例句/詞性 → upsert
# ════════════════════════════════════════════════════════════════════════════
def _gloss_system(lang):
    base = (f"你是{LANG_LABEL[lang]}詞彙教師，為做宗教/神話/宗教學研究的學生編字庫。"
            "務必輸出繁體中文（台灣用語，不可簡體）。")
    if lang in ("la", "ar", "sa", "pi", "cop", "bo", "syr", "hy", "ka"):
        src = {"la": "武加大拉丁文", "ar": "古蘭阿拉伯文", "sa": "梵文天城體", "pi": "巴利文",
               "cop": "科普特文（薩希德/波海里）", "bo": "藏文（音節）",
               "syr": "敘利亞文（Peshitta）", "hy": "亞美尼亞文", "ka": "喬治亞文"}[lang]
        extra = "藏文是以 tsheg 斷出的音節，請判斷其所屬詞並還原。" if lang == "bo" else ""
        return base + f"給你的是{src}的「表面字形」，請還原為字典詞元（lemma）後再解釋。{extra}"
    if lang in ("de", "fr"):
        g = "der/die/das 與複數" if lang == "de" else "le/la 陰陽性"
        return base + f"名詞請在 reading 標出冠詞與性別（{g}）。"
    return base


def _gloss_prompt(lang, batch):
    lines = []
    for i, c in enumerate(batch):
        hint = f"（英義參考：{c['en_gloss']}）" if c.get("en_gloss") else ""
        rd = f"［讀音：{c['reading']}］" if c.get("reading") else ""
        lines.append(f"{i+1}. {c['word']}{rd}{hint}")
    items = "\n".join(lines)
    schema = ('每個字回一物件：{"word":"原字（拉丁文回字典詞元）","reading":"讀音/假名/音標/冠詞，無則空字串",'
              '"meaning":"繁體中文釋義（簡潔，可多義以；分隔）","pos":"繁中詞性","example":"一句'
              f'{LANG_LABEL[lang]}例句（簡短、貼近宗教/經典題材尤佳）"}}')
    return (f"為下列 {len(batch)} 個{LANG_LABEL[lang]}單字補釋義。只輸出 JSON 陣列，順序與輸入一致。\n"
            f"{schema}\n\n單字：\n{items}")


def _load_done(lang):
    done = set()
    p = glossed_path(lang)
    if p.exists():
        for line in p.open(encoding="utf-8"):
            try:
                done.add(json.loads(line)["word"])
            except Exception:  # noqa: BLE001
                continue
    return done


def cmd_gloss(lang, limit=None, engine="auto"):
    cands = [json.loads(l) for l in candidates_path(lang).open(encoding="utf-8")]
    done = _load_done(lang)
    pending = [c for c in cands if c["word"] not in done]

    # 預先策展（moedict 台/客語）：候選已含繁中釋義+例句，直接 upsert，不呼叫 LLM
    if cands and cands[0].get("preglossed"):
        if limit:
            pending = pending[:limit]
        print(f"[{lang}] 預策展 upsert：候選 {len(cands)}、已完成 {len(done)}、待處理 {len(pending)}", flush=True)
        gp = glossed_path(lang)
        buf = []
        with gp.open("a", encoding="utf-8") as gf:
            for c in pending:
                buf.append({
                    "language": lang, "word": c["word"],
                    "reading": c.get("reading") or None,
                    "meaning": T._to_traditional(c.get("meaning") or ""),
                    "example": T._to_traditional(c.get("example") or "") or None,
                    "part_of_speech": c.get("pos") or None,
                    "category": c.get("category"), "level": c.get("level"),
                    "freq_rank": c.get("freq_rank"), "source": c["source"], "glossed": True,
                })
                gf.write(json.dumps({"word": c["word"]}, ensure_ascii=False) + "\n")
                if len(buf) >= UPSERT_BATCH:
                    upsert_rows(buf); buf = []
        if buf:
            upsert_rows(buf)
        print(f"[{lang}] 預策展完成，upsert {len(pending)} 字", flush=True)
        return

    is_lemma_dedup = lang == "la"  # 拉丁文按 LLM 還原的詞元去重
    if is_lemma_dedup:
        done_lemmas = set(done)  # done 已是詞元
        target = TARGETS["la"]
    if limit:
        pending = pending[:limit]
    print(f"[{lang}] gloss：候選 {len(cands)}、已完成 {len(done)}、待處理 {len(pending)}", flush=True)
    gp = glossed_path(lang)
    upsert_buf = []
    processed = 0
    for i in range(0, len(pending), GLOSS_BATCH):
        batch = pending[i:i + GLOSS_BATCH]
        try:
            res = llm_json(_gloss_prompt(lang, batch), _gloss_system(lang), engine=engine)
        except Exception as e:  # noqa: BLE001
            print(f"  ! batch {i//GLOSS_BATCH} 全引擎失敗，跳過：{str(e)[:120]}", flush=True)
            continue
        with gp.open("a", encoding="utf-8") as gf:
            for j, c in enumerate(batch):
                r = res[j] if j < len(res) and isinstance(res[j], dict) else {}
                meaning = T._to_traditional((r.get("meaning") or "").strip())
                word = (r.get("word") or c["word"]).strip() if is_lemma_dedup else c["word"]
                if not meaning:
                    continue
                if is_lemma_dedup:
                    if word in done_lemmas:
                        continue
                    done_lemmas.add(word)
                row = {
                    "language": lang, "word": word,
                    "reading": (r.get("reading") or c.get("reading") or None) or None,
                    "meaning": meaning,
                    "example": T._to_traditional((r.get("example") or "").strip()) or None,
                    "part_of_speech": (r.get("pos") or c.get("pos") or None) or None,
                    "category": c["category"], "level": c.get("level"),
                    "freq_rank": c.get("freq_rank"), "source": c["source"], "glossed": True,
                }
                gf.write(json.dumps({"word": word}, ensure_ascii=False) + "\n")
                upsert_buf.append(row)
                processed += 1
        # 每批就 flush 進 DB（與 ledger 同步）：中途被中斷時 ledger 標記 done 的字必已在 DB，避免孤兒
        if upsert_buf:
            upsert_rows(upsert_buf)
            upsert_buf = []
        if (i // GLOSS_BATCH) % 10 == 0:
            extra = f"、詞元 {len(done_lemmas)}/{target}" if is_lemma_dedup else ""
            print(f"  [{lang}] 進度 {processed} 字{extra}", flush=True)
        if is_lemma_dedup and len(done_lemmas) >= target:
            print(f"  [{lang}] 已達 {target} 詞元，停止", flush=True)
            break
    if upsert_buf:
        upsert_rows(upsert_buf)
    print(f"[{lang}] gloss 完成，本次新增 {processed} 字（DB 已補釋義 {db_count(lang, True)}）", flush=True)


# ════════════════════════════════════════════════════════════════════════════
#  語意主題分類（theme）— 一次性 LLM 批次把每個已 gloss 字打上固定主題標籤
#  跑完後字典「主題」分頁＝純讀 DB、零 AI。reentrant：只抓 theme is null 的字。
# ════════════════════════════════════════════════════════════════════════════
THEME_LIST = [
    "神‧神學", "聖經人物‧地名", "敬拜‧禮儀", "教會‧群體‧教派", "罪‧救恩‧倫理",
    "情感‧心智", "人‧身體‧家庭", "食物‧飲食", "自然‧動植物", "時間‧節期",
    "空間‧方位", "數量‧度量", "言語‧文書", "行動‧移動", "社會‧政治‧律法",
    "工藝‧器物‧建築", "性質‧抽象", "功能詞",
]
THEME_SET = set(THEME_LIST)
THEME_BATCH = 100


def _theme_system():
    return ("你是詞彙語意分類員，服務做宗教/神話/宗教學研究的學生。"
            "依每個字的繁中釋義，從固定主題清單挑**唯一最貼切**的一個主題。"
            "宗教相關字優先歸到對應的宗教主題；連接詞/介系詞/冠詞/代名詞等歸「功能詞」。"
            "務必只用清單內的主題字串，不可自創。")


def _theme_prompt(batch):
    lines = []
    for i, r in enumerate(batch):
        pos = f"（{r['part_of_speech']}）" if r.get("part_of_speech") else ""
        lines.append(f"{i+1}. {r['word']}{pos}：{r.get('meaning') or ''}")
    items = "\n".join(lines)
    themes = "｜".join(THEME_LIST)
    return (f"主題清單（只能從中選一）：{themes}\n\n"
            f"為下列 {len(batch)} 個字各選一個主題。只輸出 JSON 陣列，順序與輸入一致，"
            f'每項：{{"word":"原字","theme":"主題（清單內字串）"}}\n\n字：\n{items}')


def classify_theme(batch, engine="auto"):
    res = llm_json(_theme_prompt(batch), _theme_system(), engine=engine)
    out = []
    for i, r in enumerate(batch):
        d = res[i] if i < len(res) and isinstance(res[i], dict) else {}
        theme = (d.get("theme") or "").strip()
        if theme not in THEME_SET:
            theme = "性質‧抽象"  # 落在清單外就丟通用桶，避免污染主題
        out.append({"word": r["word"], "theme": theme})
    return out


def fetch_unthemed(lang, limit, offset):
    q = (f"{_SB_URL}/rest/v1/lang_vocab_bank?language=eq.{lang}&glossed=eq.true"
         f"&theme=is.null&select=word,meaning,part_of_speech&order=freq_rank.asc.nullslast"
         f"&limit={limit}&offset={offset}")
    r = requests.get(q, headers=_SB_HEADERS, timeout=60)
    r.raise_for_status()
    return r.json()


def set_themes(lang, pairs):
    r = requests.post(
        f"{_SB_URL}/rest/v1/rpc/set_vocab_themes",
        headers={**_SB_HEADERS, "Prefer": "return=minimal"},
        data=json.dumps({"p_language": lang, "p_pairs": pairs}).encode("utf-8"),
        timeout=120,
    )
    if r.status_code not in (200, 204):
        print(f"  ! set_themes HTTP {r.status_code}: {r.text[:200]}", flush=True)


def cmd_theme(lang, limit=None, engine="auto"):
    # 一次抓齊所有未分類字（分頁進記憶體），失敗的批次留 null、下次重跑補上
    pending, off = [], 0
    while True:
        page = fetch_unthemed(lang, 1000, off)
        if not page:
            break
        pending.extend(page)
        off += len(page)
        if len(page) < 1000:
            break
    if limit:
        pending = pending[:limit]
    print(f"[{lang}] theme：待分類 {len(pending)} 字", flush=True)
    done = 0
    for i in range(0, len(pending), THEME_BATCH):
        batch = pending[i:i + THEME_BATCH]
        try:
            pairs = classify_theme(batch, engine=engine)
        except Exception as e:  # noqa: BLE001
            print(f"  ! batch {i//THEME_BATCH} 分類失敗，跳過（下次補）：{str(e)[:100]}", flush=True)
            continue
        set_themes(lang, pairs)
        done += len(pairs)
        if (i // THEME_BATCH) % 5 == 0:
            print(f"  [{lang}] 已分類 {done}/{len(pending)}", flush=True)
    print(f"[{lang}] theme 完成，本次分類 {done} 字", flush=True)


def cmd_status():
    print(f"{'lang':5} {'candidates':>11} {'glossed(ledger)':>16} {'DB total':>9} {'DB glossed':>11} {'DB themed':>11}")
    for lang in TARGETS:
        cp, gpth = candidates_path(lang), glossed_path(lang)
        nc = sum(1 for _ in cp.open(encoding="utf-8")) if cp.exists() else 0
        ng = sum(1 for _ in gpth.open(encoding="utf-8")) if gpth.exists() else 0
        try:
            dt, dg, dth = db_count(lang), db_count(lang, True), db_count(lang, themed_only=True)
        except Exception:  # noqa: BLE001
            dt = dg = dth = -1
        print(f"{lang:5} {nc:>11} {ng:>16} {dt:>9} {dg:>11} {dth:>11}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["harvest", "gloss", "theme", "run", "status"])
    ap.add_argument("lang", nargs="?", default="all")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--engine", choices=["auto", "haiku", "nvidia", "gemini"], default="auto")
    a = ap.parse_args()
    if a.cmd == "status":
        cmd_status()
        return
    # all 的順序：使用者最常用/被卡住的古典語與較小語言先跑，英文（3 萬）量最大擺最後
    ORDER = ["arc", "att", "ar", "sa", "pi", "cop", "bo", "syr", "hy", "ka", "nan", "hak",
             "grc", "hbo", "la", "ja", "de", "fr", "es", "en"]
    langs = ORDER if a.lang == "all" else [a.lang]
    for lang in langs:
        if a.cmd in ("harvest", "run"):
            cmd_harvest(lang, force=a.force)
        if a.cmd in ("gloss", "run"):
            cmd_gloss(lang, limit=a.limit, engine=a.engine)
        if a.cmd == "theme":
            cmd_theme(lang, limit=a.limit, engine=a.engine)


if __name__ == "__main__":
    main()
