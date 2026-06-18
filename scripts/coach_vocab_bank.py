#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
共用學習單字庫建置器 — 為語言教練 7 語各建一份「權威頻率/語料庫 + LLM 補繁中釋義」的策展字庫。

來源（皆免費 / 公有領域 / CC-BY）：
  en/de/fr  FrequencyWords (hermitdave, OpenSubtitles 頻率表) → 取前 N，依頻率分 CEFR 級帶
  ja        jlpt-vocab-api (N5–N1)                          → 每級一類，含 furigana / romaji / EN 義
  grc       STEPBible TAGNT（譯者匯整希臘文新約 CC-BY）        → 詞元 + 英義 + 詞性 + 書卷，依新約頻率分帶
  hbo       STEPBible TAHOT（譯者匯整希伯來文舊約 CC-BY）      → 詞元 + 英義 + 詞性，依舊約頻率分帶
  la        Clementine Vulgate (seven1m/open-bibles, USFX)   → 表面詞頻 → LLM 還原詞元（武加大頻率分帶）

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
TARGETS = {"en": 30000, "de": 6000, "fr": 6000, "ja": 9000, "grc": 6000, "hbo": 8000, "la": 6000}
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


def db_count(lang, glossed_only=False):
    q = f"{_SB_URL}/rest/v1/lang_vocab_bank?language=eq.{lang}&select=id"
    if glossed_only:
        q += "&glossed=eq.true"
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


HARVESTERS = {
    "en": lambda: harvest_freqwords("en", TARGETS["en"]),
    "de": lambda: harvest_freqwords("de", TARGETS["de"]),
    "fr": lambda: harvest_freqwords("fr", TARGETS["fr"]),
    "ja": lambda: harvest_jlpt(TARGETS["ja"]),
    "grc": lambda: harvest_stepbible_greek(TARGETS["grc"]),
    "hbo": lambda: harvest_stepbible_hebrew(TARGETS["hbo"]),
    "la": lambda: harvest_vulgate(TARGETS["la"]),
}

LANG_LABEL = {"en": "英文", "de": "德文", "fr": "法文", "ja": "日文",
              "grc": "通用希臘文（新約 Koine）", "hbo": "聖經希伯來文", "la": "教會拉丁文（武加大）"}


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
    if lang == "la":
        return base + "給你的是武加大拉丁文的「表面字形」，請還原為字典詞元（lemma）後再解釋。"
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
    print(f"{'lang':5} {'candidates':>11} {'glossed(ledger)':>16} {'DB total':>9} {'DB glossed':>11}")
    for lang in TARGETS:
        cp, gpth = candidates_path(lang), glossed_path(lang)
        nc = sum(1 for _ in cp.open(encoding="utf-8")) if cp.exists() else 0
        ng = sum(1 for _ in gpth.open(encoding="utf-8")) if gpth.exists() else 0
        try:
            dt, dg = db_count(lang), db_count(lang, True)
        except Exception:  # noqa: BLE001
            dt = dg = -1
        print(f"{lang:5} {nc:>11} {ng:>16} {dt:>9} {dg:>11}")


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
    ORDER = ["grc", "hbo", "la", "ja", "de", "fr", "en"]
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
