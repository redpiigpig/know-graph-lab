"""Translate an English ebook into traditional Chinese via Gemini Flash.

Currently scoped to the ACCS Apocrypha volume — the first English source the
library acquired (2026-05-21). Pipeline:
  1. Read EPUB (cleaner than OCR txt) → ordered list of (heading, body) chunks
  2. Per chunk, call Gemini Flash with a translation prompt that enforces
     traditional-Chinese theological terminology (教父、次經、巴錄、瑪加伯…)
  3. Write Chinese markdown chunks to local _chunks/ JSONL
  4. PATCH ebooks row: parsed_at, standardized_at, chunk_count, total_chars

Usage:
  python scripts/translate_ebook_to_zh.py <ebook_id> --inspect      # dump source chunks
  python scripts/translate_ebook_to_zh.py <ebook_id> --limit 3      # smoke test 3 chunks
  python scripts/translate_ebook_to_zh.py <ebook_id>                # full run
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup, NavigableString
from dotenv import load_dotenv
import ebooklib
from ebooklib import epub

try:
    import anthropic as _anthropic
    _HAS_ANTHROPIC = True
except ImportError:
    _HAS_ANTHROPIC = False

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")
sys.path.insert(0, str(Path(__file__).parent))

import standardize_ebook as se  # for URL/headers + push_to_r2 + update_db helpers
import standardize_pdf_lite as pl  # for collapse_cjk_spacing

URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H_GET = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
H_JSON = {**H_GET, "Content-Type": "application/json", "Prefer": "return=representation"}

CHUNKS_DIR = Path(os.environ.get("EBOOK_CHUNKS_DIR")
                  or r"G:\我的雲端硬碟\資料\電子書\_chunks")

# ── Gemini ────────────────────────────────────────────────────────────────

def _find_gemini_keys() -> list[str]:
    primary = ("GEMINI_API_KEY", "Gemini_API_Key", "gemini_api_key", "GOOGLE_API_KEY")
    raw = []
    for name in primary:
        v = os.environ.get(name)
        if v: raw.append(v); break
    for n in range(1, 11):
        for base in primary:
            v = os.environ.get(f"{base}_{n}")
            if v: raw.append(v); break
    keys, seen = [], set()
    for r in raw:
        for piece in r.split(","):
            k = piece.strip()
            if k and k not in seen:
                seen.add(k); keys.append(k)
    return keys


GEMINI_KEYS = _find_gemini_keys()
_key_idx = 0


# ── NVIDIA NIM (integrate.api.nvidia.com, OpenAI-compatible) ────────────────
# Reliable, high-quality 繁中 fallback that REPLACES Haiku (user 2026-06-03:
# 「haiku 全面停用」). Generous free tier → doesn't hit the rate-limit wall the
# Anthropic OAuth account did on long overnight batches.
def _find_nvidia_keys() -> list[str]:
    raw = []
    for name in ("NVIDIA_API_KEY", "NVIDIA_API_Key", "nvidia_api_key", "NVAPI_KEY"):
        v = os.environ.get(name)
        if v:
            raw.append(v); break
    for n in range(1, 11):
        for base in ("NVIDIA_API_Key", "NVIDIA_API_KEY", "nvidia_api_key", "NVAPI_KEY"):
            v = os.environ.get(f"{base}_{n}")
            if v:
                raw.append(v); break
    keys, seen = [], set()
    for r in raw:
        for piece in r.split(","):
            k = piece.strip()
            if k and k not in seen:
                seen.add(k); keys.append(k)
    return keys


NVIDIA_KEYS = _find_nvidia_keys()
_nv_key_idx = 0
# 2026-06-03 benchmark on the fathers pipeline (which REQUIRES blank-line
# paragraph alignment for 中英對照 + verbatim {{p:N}}/[^N] markers):
#   deepseek-v4-flash  ✅ paras 3→3, markers kept, 上帝 term, ~15-27s  ← ONLY safe one
#   qwen3-next-80b     ⚡2-3s but ✗ collapses 3→1 paras, ✗ {{p:N}}→{p:N}, hallucinated refs
#   llama-3.3-70b      ✗ collapses paras, ✗ drops {{p:N}}, slow ~35s
#   glm-5.1 ✗ 105s (reasoning) · qwen3.5-122b ✗ timeout
# So deepseek is the SOLE NVIDIA model; on its failure the chain falls to Gemini
# (also structurally correct), NOT to a paragraph-collapsing NVIDIA model.
NVIDIA_MODELS = ["deepseek-ai/deepseek-v4-flash"]
NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

# 緩慢呼叫 + 4 帳號輪換 (user 2026-06-03): 4 NVIDIA keys from 4 separate accounts,
# each with its own daily quota. Round-robin across them so no single account is
# called too often, with a global min-gap so total RPM stays low. A key that 429s
# is rested (cooldown) and skipped, so a depleted account doesn't waste retries.
NVIDIA_MIN_INTERVAL = 6.0      # seconds between ANY two NVIDIA calls (global)
NVIDIA_KEY_COOLDOWN = 120.0    # rest a key this long after it 429s
_nv_last_call = 0.0
_nv_rr = 0                     # round-robin pointer
_nv_key_cool: dict[int, float] = {}  # key idx -> epoch until which it's resting

def _nv_throttle() -> None:
    global _nv_last_call
    gap = NVIDIA_MIN_INTERVAL - (time.time() - _nv_last_call)
    if gap > 0:
        time.sleep(gap)
    _nv_last_call = time.time()

def _nv_pick_key() -> tuple[int, str] | None:
    """Round-robin the next NVIDIA key that isn't resting. None if all are cooling."""
    global _nv_rr
    now = time.time()
    for _ in range(len(NVIDIA_KEYS)):
        idx = _nv_rr % len(NVIDIA_KEYS)
        _nv_rr += 1
        if _nv_key_cool.get(idx, 0.0) <= now:
            return idx, NVIDIA_KEYS[idx]
    return None

def _nv_rest_key(idx: int, secs: float = NVIDIA_KEY_COOLDOWN) -> None:
    _nv_key_cool[idx] = time.time() + secs

# Gemini → Haiku 2-strike fallback + 6h cooldown.
# 連續兩次「跑完所有 keys 都 429/throttling」就視為配額耗盡，進入 Haiku-only 模式 6 小時。
# 6 小時後下個 chunk 會再試 Gemini；一旦成功，streak 歸零、cooldown 解除。
# 規則來源：使用者 2026-05-29 翻譯全域規則。
GEMINI_FAIL_STREAK_LIMIT = 2
GEMINI_COOLDOWN_SECONDS = 6 * 3600

_gemini_consecutive_exhaust = 0
_gemini_cooldown_until = 0.0  # epoch seconds; 0 = no cooldown active

# NVIDIA streak/cooldown state lives next to nvidia_with_gemini_fallback below.

SONNET_MODEL = "claude-sonnet-4-6"
HAIKU_MODEL = "claude-haiku-4-5-20251001"


def _make_anthropic_client():
    if not _HAS_ANTHROPIC:
        raise RuntimeError("anthropic SDK not installed — run: pip install anthropic")
    common_kwargs = {"timeout": 600.0, "max_retries": 2}
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        return _anthropic.Anthropic(api_key=api_key, **common_kwargs)
    cred_path = Path(os.environ.get("USERPROFILE", os.environ.get("HOME", ""))) / ".claude" / ".credentials.json"
    if cred_path.exists():
        try:
            creds = json.loads(cred_path.read_text(encoding="utf-8"))
            token = creds.get("claudeAiOauth", {}).get("accessToken", "")
            if token:
                return _anthropic.Anthropic(auth_token=token, **common_kwargs)
        except Exception:
            pass
    raise RuntimeError("No Anthropic credentials")


_anthropic_client = None
_anthropic_client_cred_mtime = 0.0


def _refresh_anthropic_client_if_creds_changed() -> None:
    """Rebuild the client when credentials.json has been touched by Claude Code's
    interactive session (refresh tokens roll the access token every few hours).
    Without this, a long-running worker holds a stale token and every call 401s.
    Shared between Sonnet and Haiku — same OAuth account/token."""
    global _anthropic_client, _anthropic_client_cred_mtime
    cred = Path(os.environ.get("USERPROFILE", os.environ.get("HOME", ""))) / ".claude" / ".credentials.json"
    if cred.exists():
        m = cred.stat().st_mtime
        if m > _anthropic_client_cred_mtime:
            _anthropic_client = _make_anthropic_client()
            _anthropic_client_cred_mtime = m
    elif _anthropic_client is None:
        _anthropic_client = _make_anthropic_client()


def _anthropic_translate(model: str, label: str, source: str,
                         backoffs: tuple = (0, 60, 180, 300, 600)) -> str:
    """Shared Anthropic invocation used by Sonnet + Haiku wrappers. `label` only
    affects log lines so we can tell them apart in concurrent runs."""
    _refresh_anthropic_client_if_creds_changed()
    for attempt, wait in enumerate(backoffs, start=1):
        if wait:
            print(f"  {label} 429 — backoff {wait}s before attempt {attempt}", flush=True)
            time.sleep(wait)
        try:
            msg = _anthropic_client.messages.create(
                model=model,
                max_tokens=16000,
                messages=[{"role": "user", "content": PROMPT_TMPL.format(source=source)}],
            )
            text = "".join(block.text for block in msg.content if hasattr(block, "text"))
            return text.strip()
        except _anthropic.RateLimitError:
            print(f"  {label} rate-limit attempt {attempt}/{len(backoffs)}", file=sys.stderr, flush=True)
            if attempt >= len(backoffs):
                raise
        except (_anthropic.APIConnectionError, _anthropic.APITimeoutError) as e:
            print(f"  {label} conn error attempt {attempt}: {type(e).__name__}", file=sys.stderr, flush=True)
            if attempt >= len(backoffs):
                raise
        except _anthropic.AuthenticationError:
            print(f"  {label} 401 — re-reading credentials.json", file=sys.stderr, flush=True)
            global _anthropic_client_cred_mtime
            _anthropic_client_cred_mtime = 0.0
            _refresh_anthropic_client_if_creds_changed()
            if attempt >= len(backoffs):
                raise RuntimeError(f"Anthropic 401 even after token refresh ({label}) — Claude Code OAuth may need re-auth.")
    raise RuntimeError(f"{label} exhausted retries")


def sonnet_translate(source: str) -> str:
    """Translate via Claude Sonnet 4.6. Long backoff tolerates concurrent
    interactive Opus / OCR Haiku — they all share the OAuth account."""
    return _anthropic_translate(SONNET_MODEL, "Sonnet", source)


def haiku_translate(source: str) -> str:
    """Translate via Claude Haiku 4.5. Cheaper + faster than Sonnet; ~95% of
    Sonnet's translation quality on this task per spot-checks. Used as
    automatic fallback when Gemini exhausts its 4 keys."""
    return _anthropic_translate(HAIKU_MODEL, "Haiku", source,
                                backoffs=(0, 30, 90, 180))  # shorter — Haiku has higher RPM


MAX_CHUNK_CHARS = 20_000  # split source if larger — Sonnet 16K output cap + safety


def split_oversized(src: str, max_chars: int = MAX_CHUNK_CHARS) -> list[str]:
    """Split a single source chunk by paragraph break (\\n\\n) when over max_chars.
    Greedily packs paragraphs into pieces ≤ max_chars."""
    if len(src) <= max_chars:
        return [src]
    paras = src.split("\n\n")
    pieces, cur = [], []
    cur_len = 0
    for p in paras:
        if cur_len + len(p) + 2 > max_chars and cur:
            pieces.append("\n\n".join(cur))
            cur, cur_len = [p], len(p)
        else:
            cur.append(p)
            cur_len += len(p) + 2
    if cur:
        pieces.append("\n\n".join(cur))
    return pieces


# AUTO-PROMPT-PEOPLE:START — 自動從 /translation-glossary DB 同步（教父全集翻譯用）
AUTO_PROMPT_PEOPLE = '''
   - Clement of Rome → 羅馬的革利免
   - Ignatius of Antioch → 安提阿的依納爵
   - Papias of Hierapolis → 希拉波利的帕皮亞
   - Aristides of Athens → 雅典的亞里斯底德
   - Melito of Sardis → 撒狄的美利多
   - Mathetes → 瑪忒特
   - Pantaenus → 潘代諾
   - Hermas → 羅馬的黑馬
   - Polycarp of Smyrna → 士每拿的坡旅甲
   - Justin Martyr → 殉道者猶斯定
   - Tatian the Assyrian → 他提安
   - Theophilus of Antioch → 安提阿的提阿非羅
   - Athenagoras of Athens → 雅典那哥拉
   - Hermias → 赫爾米亞
   - Irenaeus of Lyon → 里昂的愛任紐
   - Clement of Alexandria → 亞歷山卓的革利免
   - Tertullian → 特土良
   - Hippolytus of Rome → 希波呂圖斯
   - Julius Africanus → 猶略‧阿弗里卡努斯
   - Minucius Felix → 密努修‧斐力克斯
   - Theognostus of Alexandria → 亞歷山卓的提奧格諾斯圖斯
   - Anatolius of Laodicea → 勞底基亞的亞納托利烏
   - Origen → 俄利根
   - Cyprian of Carthage → 居普良
   - Novatian → 諾窪天
   - Dionysius of Alexandria → 亞歷山卓的狄奧尼修
   - Commodian → 科摩狄安
   - Gregory Thaumaturgus → 奇蹟行者格列高利
   - Arnobius of Sicca → 阿爾諾比烏斯
   - Lactantius → 乳香者拉克坦提烏斯
   - Venantius → 維南提烏
   - Asterius the Sophist → 詭辯家亞斯特里烏
   - Pierius of Alexandria → 亞歷山卓的皮埃里烏斯
   - Methodius of Olympus → 奧林波斯的美多第烏
   - Eusebius of Caesarea → 該撒利亞的優西比烏
   - Aphrahat the Persian Sage → 波斯智者亞弗拉哈特
   - Pacian of Barcelona → 帕齊安
   - Hilary of Poitiers → 希拉里
   - Ephrem the Syrian → 敘利亞的艾弗冷
   - Athanasius of Alexandria → 亞他那修
   - Macrina the Younger → 小瑪克麗娜
   - Basil the Great → 大巴西略
   - Cyril of Jerusalem → 西瑞爾
   - Gregory of Nazianzus → 拿先斯的格列高理
   - Apollinaris of Laodicea → 亞波里那留
   - Diodore of Tarsus → 大數的狄奧多若
   - Pelagius → 伯拉糾
   - Gregory of Nyssa → 尼撒的格列高理
   - Ambrose of Milan → 安波羅修
   - Didymus the Blind → 狄第摩
   - Asterius of Amasea → 亞斯特里
   - Epiphanius of Salamis → 厄皮法尼
   - John Chrysostom → 金口若望
   - Jerome → 耶柔米
   - Sulpitius Severus → 蘇皮修
   - Theodore of Mopsuestia → 摩普綏提亞的狄奧多若
   - Augustine of Hippo → 希波的奧古斯丁
   - John Cassian → 若望‧格西安
   - Cyril of Alexandria → 亞歷山卓的西里爾
   - Vincent of Lerins → 勒蘭的文生
   - Nestorius → 聶斯脫里
   - Prosper of Aquitaine → 普洛斯培
   - Eutyches → 歐迪克
   - Leo the Great → 大良
   - Theodoret of Cyrus → 居魯斯的狄奧多雷特
   - Salvian of Marseille → 薩爾維安
   - Pseudo-Dionysius the Areopagite → 偽狄奧尼修斯
   - Philoxenus of Mabbug → 腓洛克塞努斯
   - Boethius → 波愛修
   - Fulgentius of Ruspe → 富爾根修
   - Severus of Antioch → 塞維魯斯
   - Caesarius of Arles → 凱撒略
   - Romanos the Melodist → 羅馬努斯‧梅洛迪斯特
   - Cassiodorus → 卡西奧多魯斯
   - Gregory the Great → 大額我略
   - Isidore of Seville → 依西多祿
   - John Climacus → 西奈的若望
   - Maximus the Confessor → 認信者馬克西姆
   - Germanus of Constantinople → 君士坦丁堡的日耳曼
   - Bede the Venerable → 可敬者比德
   - Andrew of Crete → 克里特的安德烈
   - John of Damascus → 大馬士革的若望
   - Alcuin of York → 艾爾昆
   - Theodore the Studite → 斯圖德修院的西奧多
   - Rabanus Maurus → 拉班‧毛魯斯
   - John Scotus Eriugena → 若望‧思高‧愛留根納
   - Photius of Constantinople → 君士坦丁堡的佛提烏
   - Symeon the New Theologian → 新神學家西蒙
   - Berengar of Tours → 貝倫加留斯
   - Anselm of Canterbury → 坎特伯里的安瑟倫
   - Anselm of Laon → 蘭的安塞姆
   - Hugh of Saint Victor → 聖維克多的修格
   - Peter Abelard → 伯多祿‧亞伯拉
   - Bernard of Clairvaux → 克萊爾沃的伯納德
   - Peter Lombard → 倫巴第的彼得
   - Richard of Saint Victor → 聖維克多的理查德
   - Hildegard of Bingen → 賓根的希爾德加德
   - Robert Grosseteste → 羅伯特‧格羅塞特斯特
   - Hugh of Saint-Cher → 聖凱爾的雨果
   - Thomas Aquinas → 多瑪斯‧阿奎那
   - Bonaventure → 文德
   - Albertus Magnus → 大亞爾伯特
   - Mechthild of Magdeburg → 美格德堡的梅希蒂爾德
   - Henry of Ghent → 根特的亨利
   - Roger Bacon → 羅傑‧培根
   - Duns Scotus → 董‧思高
   - Giles of Rome → 羅馬的埃吉迪烏斯
   - Meister Eckhart → 艾克哈特
   - Marsilius of Padua → 馬西略‧帕多瓦
   - Gregory of Sinai → 西奈的格列高理
   - William of Ockham → 奧坎的威廉
   - Gregory Palamas → 帕拉馬的格列高理
   - Johannes Tauler → 陶勒
   - Henry Suso → 蘇索
   - Catherine of Siena → 錫耶納的凱瑟琳
   - Julian of Norwich → 諾里奇的朱利安
   - John Wycliffe → 威克里夫
   - Nicholas Cabasilas → 尼古拉‧卡巴西拉
   - Jan Hus → 揚‧胡斯
   - Lorenzo Valla → 洛倫佐‧瓦拉
   - Nicholas of Cusa → 庫薩的尼古拉
   - Thomas à Kempis → 多瑪斯‧肯皮斯
   - Gabriel Biel → 比耶爾
'''
# AUTO-PROMPT-PEOPLE:END

_PROMPT_TMPL_HEAD = """你是基督教神學翻譯專家。把下列英文段落翻譯成「繁體中文」。

關鍵要求：
1. **嚴守繁體中文**：所有用字必須繁體。
2. **教父／神學家人名對齊**（自動同步自 /translation-glossary DB；以下 ★建議譯名為使用者校過的標準）：
"""

_PROMPT_TMPL_TAIL = """
3. **聖經書卷／神學術語／諾斯底專名對齊**：
   - Patristic / Church Fathers → 教父
   - Apocrypha / Deuterocanonical → 次經 / 第二正典
   - Wisdom of Solomon → 智慧篇
   - Sirach / Ecclesiasticus → 德訓篇 / 便西拉智訓
   - Tobit → 多俾亞傳 / 多比傳
   - Baruch → 巴錄
   - Judith → 友弟德傳 / 猶滴傳
   - 1-2 Maccabees → 瑪加伯上下 / 馬加比上下
   - Marcion / Valentinus / Basilides → 馬吉安 / 瓦倫提努 / 巴西理德
   - 諾斯底人物（Saturninus / Cerinthus / Carpocrates / Menander / Simon Magus）→ 撒土爾尼努 / 克林妥 / 加爾頗克拉底 / 米南德 / 行邪術的西門
   - Demiurge → 巨匠造物者
   - Pleroma → 普累若麻 / 充滿
   - Aeon (Gnostic) → 永世 / 伊翁（諾斯底專名，非時間義）
   - Recapitulation (anakephalaiosis) → 復歸 / 總歸於一
   - rule of faith (regula fidei) → 信仰準則
   - apostolic succession → 使徒統緒
   - Against Heresies → 駁異端
   - Didache → 十二使徒遺訓
   - Shepherd of Hermas → 黑馬牧者書
   - Dialogue with Trypho → 與特里弗的對話
4. **保留原文 Markdown 結構與段落分界**：## / ### / **粗體** / *斜體* / > 引文 / - 列表全部對應翻譯。**段落必須逐一對應** — 原文以空行分隔成幾個段落，譯文就輸出幾個段落，不可合併、不可拆分、不可增刪空行。reader 的中英對照是逐段左右並排，段落數一旦不一致整篇就會錯位。
5. **聖經引用格式**：把英文 (1 Mac 4:18) 翻成繁體（瑪加伯上 4:18）。
6. **章節標題簡潔**：別把 "Chapter 1" 翻成囉嗦句子，直譯「第一章」即可。
7. **腳註標記原樣保留**（極重要 — reader 靠這些 markers 做跳轉與引用）：
   - `[^N]`（如 `[^1445]`）= 內文腳註 ref。**逐字原樣輸出**，不要翻譯數字、不要拆 `^`、不要替換成中文括號。位置維持在對應的字後面。
   - `{{p:N}}`（如 `{{p:25}}`）= 原書頁碼 marker。**逐字原樣輸出**，位置維持在文字流中對應處。讀者複製文字時這標記產生芝加哥引用的頁碼。
   - 末尾若有 `————————…` 分隔線後跟 `(1) text` `(2) text` 區段 = 腳註正文區塊：
       · 分隔線原樣保留
       · 每行的 `(N)` 編號原樣保留（順序、數字皆不動）
       · 編號後的本文翻成繁中
       · 不要合併、不要省略

只輸出翻譯後的繁體中文 markdown，不要加說明、不要 wrap 在程式碼塊裡。

--- 原文 ---

{source}
"""

# AUTO_PROMPT_PEOPLE 在 AUTO-PROMPT-PEOPLE marker 區內，由 export_glossary_from_db.py 維護
PROMPT_TMPL = _PROMPT_TMPL_HEAD + AUTO_PROMPT_PEOPLE + _PROMPT_TMPL_TAIL


def gemini_translate(source: str, model: str = "gemini-2.5-flash") -> str:
    global _key_idx
    if not GEMINI_KEYS:
        raise RuntimeError("no Gemini API key")
    body = {
        "contents": [{"parts": [{"text": PROMPT_TMPL.format(source=source)}]}],
        "generationConfig": {"temperature": 0.2, "responseMimeType": "text/plain"},
    }
    base = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    keys_tried = 0
    while keys_tried < len(GEMINI_KEYS):
        key = GEMINI_KEYS[_key_idx]
        keys_tried += 1
        for attempt, wait in enumerate((0, 3, 12), start=1):
            if wait:
                time.sleep(wait)
            try:
                r = requests.post(f"{base}?key={key}", json=body, timeout=90)
            except requests.exceptions.RequestException as e:
                print(f"  Gemini conn-err key#{_key_idx} attempt {attempt}: {type(e).__name__}", file=sys.stderr, flush=True)
                if attempt >= 3:
                    break
                continue
            if r.status_code == 200:
                data = r.json()
                try:
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                except (KeyError, IndexError):
                    raise RuntimeError(f"unexpected Gemini response: {json.dumps(data)[:300]}")
                return text.strip()
            if r.status_code in (429, 502, 503, 504):
                print(f"  Gemini {r.status_code} key#{_key_idx} attempt {attempt}", file=sys.stderr, flush=True)
                if attempt >= 3:
                    break
                continue
            raise RuntimeError(f"Gemini HTTP {r.status_code}: {r.text[:300]}")
        # All attempts on this key failed — rotate
        _key_idx = (_key_idx + 1) % len(GEMINI_KEYS)
    raise RuntimeError(f"all {len(GEMINI_KEYS)} Gemini keys exhausted (timeouts/throttling)")


_THINK_RE = re.compile(r"<think>.*?</think>", re.S)

# Phrases that appear in our translation prompts but never in real translated
# content — their presence means the model parroted the instructions.
_PROMPT_ECHO_MARKERS = (
    "只輸出這一段", "只輸出翻譯", "只輸出中文", "請提供您想翻譯", "請提供您要翻譯",
    "我準備好為您", "準備好為您進行翻譯", "不要前言", "逐字翻成繁體中文",
    "逐字翻譯為繁體中文", "台灣用語、中間點", "台灣用語，中間點", "中間點用「‧」",
    "你是諾斯底", "專業譯者", "請貼上", "請輸入您想翻譯",
)


def _looks_like_prompt_echo(text: str) -> bool:
    return any(m in text for m in _PROMPT_ECHO_MARKERS)


def _to_traditional(text: str) -> str:
    """Best-effort 繁體化 — Qwen/DeepSeek/GLM occasionally slip Simplified. opencc
    is lazy-imported; if unavailable we return text unchanged (prompt already
    asks for 繁體)."""
    try:
        from opencc import OpenCC
        if not hasattr(_to_traditional, "_cc"):
            _to_traditional._cc = OpenCC("s2tw")
        return _to_traditional._cc.convert(text)
    except Exception:
        return text


def nvidia_translate(source: str) -> str:
    """Translate via NVIDIA NIM (OpenAI-compatible). Round-robins across the 4
    account keys (skipping any that recently 429'd), with a global min-gap so we
    never burst. A depleted key is rested NVIDIA_KEY_COOLDOWN secs and skipped, so
    it costs one quick request, not a long backoff. Output → opencc s2tw 繁體 net.
    Gives up (→ Gemini) only if every key stays 429 for the whole deadline."""
    if not NVIDIA_KEYS:
        raise RuntimeError("no NVIDIA API key")
    prompt = PROMPT_TMPL.format(source=source)
    model = NVIDIA_MODELS[0]
    last_err = "?"
    echoes = 0  # times the model parroted the prompt instead of translating
    deadline = time.time() + 900   # 15 min across all keys, then fall to Gemini
    while time.time() < deadline:
        picked = _nv_pick_key()
        if picked is None:  # every key is resting — wait for the soonest to free up
            soonest = min(_nv_key_cool.values()) if _nv_key_cool else time.time() + 5
            time.sleep(max(1.0, min(soonest - time.time(), 30.0)))
            continue
        idx, key = picked
        _nv_throttle()  # 緩慢呼叫 — global min-gap between any two NVIDIA calls
        try:
            r = requests.post(
                NVIDIA_URL,
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={"model": model, "messages": [{"role": "user", "content": prompt}],
                      "temperature": 0.2, "max_tokens": 8000},
                timeout=600,  # deepseek-v4-flash can need >180s on 15-20K char pieces
            )
        except requests.exceptions.RequestException as e:
            last_err = f"conn {type(e).__name__} key#{idx}"
            _nv_rest_key(idx, 30)  # brief rest, try another key
            continue
        if r.status_code == 200:
            text = _THINK_RE.sub("", r.json()["choices"][0]["message"]["content"]).strip()
            if _looks_like_prompt_echo(text):
                # deepseek sometimes parrots the instructions on trivial input
                # (a lone byline/header). Retry a couple times, then degrade to
                # the source so alignment holds instead of showing prompt junk.
                echoes += 1
                last_err = f"prompt-echo key#{idx}"
                print(f"  NVIDIA prompt-echo key#{idx} (#{echoes}) — retrying", file=sys.stderr, flush=True)
                if echoes >= 3:
                    return source
                _nv_rest_key(idx, 3)
                continue
            return _to_traditional(text)
        if r.status_code == 404:
            raise RuntimeError(f"{model} 404 — model unavailable")
        if r.status_code in (429, 500, 502, 503, 504):
            last_err = f"NVIDIA {r.status_code} key#{idx}"
            print(f"  NVIDIA {r.status_code} key#{idx} — resting {NVIDIA_KEY_COOLDOWN:.0f}s, rotating", file=sys.stderr, flush=True)
            _nv_rest_key(idx)
            continue
        last_err = f"NVIDIA HTTP {r.status_code}: {r.text[:200]}"
        _nv_rest_key(idx)
        continue
    raise RuntimeError(f"NVIDIA translate failed (last: {last_err})")


def nvidia_chat(prompt: str, max_tokens: int = 2000, system: str | None = None,
                temperature: float = 0.2) -> str:
    """Generic NVIDIA NIM chat call (OpenAI-compatible) for NON-translation tasks
    (proofreading / titling / cleanup) that previously used Haiku — Haiku is fully
    retired (user 2026-06-03). Rotates keys + NVIDIA_MODELS; strips <think> blocks.
    Does NOT run opencc (caller may need raw JSON). Raises on total failure.
    Same 4-key round-robin + per-key cooldown + global throttle as nvidia_translate."""
    if not NVIDIA_KEYS:
        raise RuntimeError("no NVIDIA API key")
    msgs = ([{"role": "system", "content": system}] if system else []) + \
           [{"role": "user", "content": prompt}]
    model = NVIDIA_MODELS[0]
    last_err = "?"
    deadline = time.time() + 600
    while time.time() < deadline:
        picked = _nv_pick_key()
        if picked is None:
            soonest = min(_nv_key_cool.values()) if _nv_key_cool else time.time() + 5
            time.sleep(max(1.0, min(soonest - time.time(), 30.0)))
            continue
        idx, key = picked
        _nv_throttle()
        try:
            r = requests.post(
                NVIDIA_URL,
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={"model": model, "messages": msgs,
                      "temperature": temperature, "max_tokens": max_tokens},
                timeout=300,
            )
        except requests.exceptions.RequestException as e:
            last_err = f"conn {type(e).__name__} key#{idx}"
            _nv_rest_key(idx, 30)
            continue
        if r.status_code == 200:
            return _THINK_RE.sub("", r.json()["choices"][0]["message"]["content"]).strip()
        if r.status_code == 404:
            raise RuntimeError(f"{model} 404 — model unavailable")
        if r.status_code in (429, 500, 502, 503, 504):
            last_err = f"NVIDIA {r.status_code} key#{idx}"
            _nv_rest_key(idx)
            continue
        last_err = f"NVIDIA HTTP {r.status_code}: {r.text[:200]}"
        _nv_rest_key(idx)
        continue
    raise RuntimeError(f"NVIDIA chat failed (last: {last_err})")


def _secondary_translate(source: str) -> str:
    """Tier-2 → Tier-3 fallback used when Gemini (primary) is exhausted:
    NVIDIA deepseek (2nd) → on its failure, Haiku 救急 (3rd, user 2026-06-04:
    「Gemini 和 NVIDIA 都跑完了就換 Haiku」). Haiku shares the Claude Max OAuth
    account, so it only fires when BOTH free pools are dry."""
    try:
        return nvidia_translate(source)
    except RuntimeError as e:
        print(f"  ↳ NVIDIA exhausted ({str(e)[:50]}…) — 救急 fallback to Haiku", flush=True)
        return haiku_translate(source)


def gemini_with_nvidia_fallback(source: str) -> str:
    """Default engine for English → 繁中 long-running jobs. 3-tier per-piece chain:
    Gemini (primary, fast + free) → NVIDIA deepseek (2nd) → Haiku (3rd 救急).

    2-strike rule: after GEMINI_FAIL_STREAK_LIMIT consecutive `all keys exhausted`
    events, stop probing Gemini and route to the NVIDIA→Haiku chain for
    GEMINI_COOLDOWN_SECONDS, then re-probe Gemini; success resets the streak."""
    global _gemini_consecutive_exhaust, _gemini_cooldown_until
    now = time.time()
    if now < _gemini_cooldown_until:
        return _secondary_translate(source)  # Gemini-cooldown: NVIDIA→Haiku window
    try:
        result = gemini_translate(source)
        _gemini_consecutive_exhaust = 0
        return result
    except RuntimeError as e:
        msg = str(e)
        if "Gemini keys exhausted" in msg or "no Gemini API key" in msg:
            _gemini_consecutive_exhaust += 1
            if _gemini_consecutive_exhaust >= GEMINI_FAIL_STREAK_LIMIT:
                _gemini_cooldown_until = now + GEMINI_COOLDOWN_SECONDS
                print(f"  ↳ Gemini hit {_gemini_consecutive_exhaust} consecutive exhaustions "
                      f"— switching to NVIDIA-only for {GEMINI_COOLDOWN_SECONDS/3600:.0f}h "
                      f"(retry after {time.strftime('%H:%M', time.localtime(_gemini_cooldown_until))})",
                      flush=True)
            else:
                print(f"  ↳ Gemini failed ({msg[:80]}…) — falling back to NVIDIA→Haiku "
                      f"[{_gemini_consecutive_exhaust}/{GEMINI_FAIL_STREAK_LIMIT} strikes]", flush=True)
            return _secondary_translate(source)
        raise


# NVIDIA → Gemini 2-strike fallback. NVIDIA is PRIMARY per 2026-06-03 benchmark
# (deepseek-v4-flash ~14s vs Gemini ~22s, and immune to Gemini's quota 429 wall
# which was already firing during the bench). Gemini is the per-piece fallback.
# Haiku fully retired — never touched.
NVIDIA_FAIL_STREAK_LIMIT = 2
NVIDIA_COOLDOWN_SECONDS = 6 * 3600
_nvidia_consecutive_exhaust = 0
_nvidia_cooldown_until = 0.0


def nvidia_with_gemini_fallback(source: str) -> str:
    """Default engine (2026-06-03 onward): NVIDIA NIM deepseek-v4-flash first —
    faster and not subject to Gemini's quota wall — with per-piece fallback to
    Gemini Flash when NVIDIA is unavailable. 2-strike: after
    NVIDIA_FAIL_STREAK_LIMIT consecutive NVIDIA exhaustions, route everything to
    Gemini for NVIDIA_COOLDOWN_SECONDS, then re-probe NVIDIA; success resets the
    streak. Haiku is fully retired (user 2026-06-03) — never invoked."""
    global _nvidia_consecutive_exhaust, _nvidia_cooldown_until
    now = time.time()
    if now < _nvidia_cooldown_until:
        return gemini_translate(source)  # Gemini-only cooldown window
    try:
        result = nvidia_translate(source)
        _nvidia_consecutive_exhaust = 0  # success resets streak
        return result
    except RuntimeError as e:
        msg = str(e)
        _nvidia_consecutive_exhaust += 1
        if _nvidia_consecutive_exhaust >= NVIDIA_FAIL_STREAK_LIMIT:
            _nvidia_cooldown_until = now + NVIDIA_COOLDOWN_SECONDS
            print(f"  ↳ NVIDIA hit {_nvidia_consecutive_exhaust} consecutive failures "
                  f"— switching to Gemini-only for {NVIDIA_COOLDOWN_SECONDS/3600:.0f}h "
                  f"(retry after {time.strftime('%H:%M', time.localtime(_nvidia_cooldown_until))})",
                  flush=True)
        else:
            print(f"  ↳ NVIDIA failed ({msg[:80]}…) — falling back to Gemini "
                  f"[{_nvidia_consecutive_exhaust}/{NVIDIA_FAIL_STREAK_LIMIT} strikes]", flush=True)
        return gemini_translate(source)  # if Gemini also dies, RuntimeError bubbles → resume later


# Back-compat alias: existing callers import gemini_with_haiku_fallback.
# Now points at the NVIDIA-first chain (Haiku retired 2026-06-03).
gemini_with_haiku_fallback = nvidia_with_gemini_fallback


# ── EPUB → ordered chunks ─────────────────────────────────────────────────

def epub_to_chunks(epub_path: Path) -> list[dict]:
    """Walk EPUB items in document order, emitting one source chunk per
    non-empty ITEM_DOCUMENT. Source markdown is ENRICHED with CCEL markers
    that the bare get_text() would strip:

      - `<a class="Note" href="#fnf_...">N</a>`         → `[^N]`
        (inline footnote reference, preserved verbatim through translation)

      - `<span class="pb" id="..Page_N"/>`              → `{{p:N}}`
        (print-edition page break marker — citation handler picks the
        nearest one before the selected text)

      - `<div class="mnote"> ... <span class="Footnote">body</span>`
        → appended at end of chunk as `\n\n————————…\n\n(N) body`
        (translator's prompt instructs to translate the body text but
        keep the (N) prefix and order intact)

    This was previously a SEPARATE post-translate step
    (`extract_epub_extras.py`), but doing it pre-translation lets the LLM
    translate footnote bodies into Chinese too. Otherwise the Chinese
    side ends up with no refs and no footnote section.
    """
    book = epub.read_epub(str(epub_path))
    chunks: list[dict] = []
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_content(), "lxml")

        # ─ (1) Strip footnote <div class="mnote"> out of body flow.
        #   Collect {N: body_text} for emission at chunk end.
        footnotes: dict[int, str] = {}
        for div in soup.find_all("div", class_="mnote"):
            sup = div.find("sup", class_="NoteRef")
            anchor = div.find("a", class_="Note")
            body_span = div.find("span", class_="Footnote")
            num: int | None = None
            if sup and sup.get_text(strip=True).isdigit():
                num = int(sup.get_text(strip=True))
            elif anchor and anchor.get_text(strip=True).isdigit():
                num = int(anchor.get_text(strip=True))
            if num is None:
                div.decompose()
                continue
            body = body_span.get_text(separator=" ", strip=True) if body_span else ""
            body = re.sub(r"\s+", " ", body).strip()
            if body:
                footnotes[num] = body
            div.decompose()

        # ─ (2) Replace pagebreak <span class="pb"> with {{p:N}} sentinel
        for sp in soup.find_all("span", class_="pb"):
            page_id = sp.get("id", "")
            m = re.search(r"Page[_\-](\d+)", page_id)
            if m:
                sp.replace_with(NavigableString(f" __PB_{m.group(1)}__ "))
            else:
                sp.decompose()

        # ─ (3) Replace inline footnote refs <a class="Note">N</a> with [^N]
        for a in soup.find_all("a", class_="Note"):
            txt = a.get_text(strip=True)
            if txt.isdigit():
                a.replace_with(NavigableString(f"[^{txt}]"))
            else:
                a.decompose()

        # ─ (4) Build markdown
        md_parts: list[str] = []
        for el in soup.find_all(["h1", "h2", "h3", "h4", "p", "blockquote", "li"]):
            text = el.get_text(separator=" ", strip=True)
            if not text:
                continue
            tag = el.name
            if tag == "h1":   md_parts.append(f"## {text}")
            elif tag == "h2": md_parts.append(f"### {text}")
            elif tag in ("h3", "h4"): md_parts.append(f"#### {text}")
            elif tag == "blockquote": md_parts.append(f"> {text}")
            elif tag == "li": md_parts.append(f"- {text}")
            else:             md_parts.append(text)
        content = "\n\n".join(md_parts).strip()
        # Finalize page-break sentinels and collapse runs of spaces
        content = re.sub(r"__PB_(\d+)__", r"{{p:\1}}", content)
        content = re.sub(r" +", " ", content)

        if not content:
            continue

        # ─ (5) Append footnote section if any
        if footnotes:
            lines = ["", "—" * 30, ""]
            for n in sorted(footnotes.keys()):
                lines.append(f"({n}) {footnotes[n]}")
                lines.append("")
            content = content.rstrip() + "\n" + "\n".join(lines)

        # Derive title from first heading
        m = re.search(r"^(#{2,4})\s+(.+)", content, re.M)
        title = m.group(2).strip() if m else item.get_name()
        title = title.split("\n", 1)[0].strip()

        chunks.append({
            "src_file": item.get_name(),
            "title_en": title,
            "content_en": content,
        })
    return chunks


# ── Pipeline ──────────────────────────────────────────────────────────────

def find_epub_for_book(book: dict) -> Path:
    pdf = Path(book["file_path"])
    # Sister .epub in same dir
    epub_p = pdf.with_suffix(".epub")
    if epub_p.exists():
        return epub_p
    # Otherwise search sibling
    for f in pdf.parent.iterdir():
        if f.suffix.lower() == ".epub":
            return f
    raise FileNotFoundError(f"no epub for {pdf}")


def fetch_book(ebook_id: str) -> dict:
    r = requests.get(f"{URL}/rest/v1/ebooks?id=eq.{ebook_id}&select=*", headers=H_GET, timeout=30)
    r.raise_for_status()
    rows = r.json()
    if not rows:
        raise SystemExit(f"no ebooks row for {ebook_id}")
    return rows[0]


def translate_book(ebook_id: str, limit: int | None, inspect: bool, dry_run: bool,
                   engine: str = "gemini", resume: bool = False) -> None:
    # Always unbuffered so background-mode logs show progress live.
    try:
        sys.stdout.reconfigure(line_buffering=True)
        sys.stderr.reconfigure(line_buffering=True)
    except Exception:
        pass

    book = fetch_book(ebook_id)
    print(f"Book: {book['title']}", flush=True)
    epub_path = find_epub_for_book(book)
    print(f"EPUB: {epub_path}", flush=True)

    src_chunks = epub_to_chunks(epub_path)
    print(f"Source chunks: {len(src_chunks)}", flush=True)
    total_en_chars = sum(len(c["content_en"]) for c in src_chunks)
    print(f"Source total: {total_en_chars:,} chars", flush=True)

    if inspect:
        for i, c in enumerate(src_chunks[:8]):
            print(f"\n[{i}] {c['title_en'][:60]}  ({len(c['content_en'])} chars)")
            print(c["content_en"][:400])
        print(f"... and {max(0, len(src_chunks)-8)} more")
        return

    target = src_chunks[:limit] if limit else src_chunks

    # Resume: if a JSONL already exists, load it and skip those chunks.
    # Match on title_en (English source heading) — chapter_path is the
    # translated Chinese heading which never matches the English source iter,
    # so using chapter_path here would reprocess every H2 chunk on each resume
    # (observed 2026-05-21: 10 lines but 7 unique sources after 2 resumes).
    out_path = CHUNKS_DIR / f"{ebook_id}.jsonl"
    out_chunks: list[dict] = []
    done_titles: set[str] = set()
    if resume and out_path.exists():
        try:
            for line in out_path.read_text(encoding="utf-8").splitlines():
                obj = json.loads(line)
                out_chunks.append(obj)
                # title_en added 2026-05-21; legacy chunks fall back to chapter_path
                done_titles.add(obj.get("title_en") or obj.get("chapter_path", ""))
            print(f"Resume: loaded {len(out_chunks)} existing chunks (skip-set size {len(done_titles)})", flush=True)
        except Exception as e:
            print(f"Resume failed: {e} — restarting from scratch", file=sys.stderr, flush=True)
            out_chunks = []

    if engine == "sonnet":
        translator, model_label = sonnet_translate, SONNET_MODEL
    elif engine == "nvidia":
        translator, model_label = nvidia_translate, NVIDIA_MODELS[0]
    elif engine == "gemini":
        # Explicit Gemini-first chain (Gemini → NVIDIA → Haiku per-piece fallback).
        translator, model_label = gemini_with_nvidia_fallback, "gemini-2.5-flash → nvidia → haiku"
    elif engine == "haiku":
        # Haiku 現為第三層救急 (user 2026-06-04) — 走預設 3-tier 鏈即可。
        translator, model_label = gemini_with_nvidia_fallback, "gemini-2.5-flash → nvidia → haiku"
    else:  # default: 3-tier per-piece chain (user 2026-06-04).
        # Gemini 4 keys (primary, fast+free) → NVIDIA deepseek 4-account (2nd) →
        # Haiku 救急 (3rd, Claude Max OAuth — only when both free pools are dry).
        # deepseek is NVIDIA's sole model (only one preserving paras + {{p:N}}/[^N]).
        translator, model_label = gemini_with_nvidia_fallback, "gemini-2.5-flash → nvidia → haiku"
    print(f"Engine: {engine}  Model: {model_label}", flush=True)

    t_total = time.time()
    n_processed = 0
    consecutive_failures = 0
    FAIL_PAUSE_AFTER = 3       # n chunks in a row before sleeping
    FAIL_PAUSE_SEC = 30 * 60   # sleep duration on rate-limit wall
    for i, c in enumerate(target):
        en = c["content_en"]
        if not en.strip() or len(en) < 30:
            continue
        if c["title_en"] in done_titles:
            # Already translated in a prior run
            continue
        n_processed += 1
        elapsed_total = time.time() - t_total
        rate = n_processed / elapsed_total if elapsed_total else 0
        eta = (len(target) - i - 1) / rate if rate else 0
        print(f"\n[{i+1}/{len(target)}] {c['title_en'][:50]}  ({len(en)} en chars)  ETA {int(eta)}s", flush=True)
        if dry_run:
            print("  (dry-run, skipped translation call)", flush=True)
            continue
        t0 = time.time()
        pieces = split_oversized(en)
        if len(pieces) > 1:
            print(f"  ↳ source split into {len(pieces)} pieces (>{MAX_CHUNK_CHARS} chars)", flush=True)
        zh_parts = []
        failed = False
        for j, piece in enumerate(pieces, start=1):
            try:
                zh_part = translator(piece)
                zh_parts.append(zh_part)
                if len(pieces) > 1:
                    print(f"    piece {j}/{len(pieces)}: {len(zh_part)} zh chars", flush=True)
            except Exception as e:
                print(f"  ⚠ translation failed (piece {j}/{len(pieces)}): {e}", file=sys.stderr, flush=True)
                failed = True
                break
        if failed:
            consecutive_failures += 1
            if consecutive_failures >= FAIL_PAUSE_AFTER:
                mins = FAIL_PAUSE_SEC // 60
                print(f"\n  💤 {consecutive_failures} consecutive failures — pausing {mins} min "
                      f"(likely Anthropic / Gemini rate-limit wall). Will resume automatically.",
                      flush=True)
                time.sleep(FAIL_PAUSE_SEC)
                consecutive_failures = 0  # give it another shot
            continue
        consecutive_failures = 0  # reset on any successful chunk
        zh = "\n\n".join(zh_parts)
        zh = se.to_traditional(zh)
        zh = pl.collapse_cjk_spacing(zh)
        elapsed = time.time() - t0
        new_chunk = {
            "chunk_index": len(out_chunks),
            "chunk_type": "chapter",
            "page_number": None,
            "chapter_path": (re.search(r"^(#{2,4})\s+(.+)", zh, re.M).group(2).strip()
                             if re.search(r"^(#{2,4})\s+", zh, re.M) else c["title_en"]),
            "format": "markdown",
            "source_lang": "en",
            "title_en": c["title_en"],  # source heading; used by --resume to dedupe across runs
            "source_text": en,
            "content": zh,
        }
        out_chunks.append(new_chunk)
        # Append-write so an interrupted run keeps its partial output (resume).
        with open(out_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(new_chunk, ensure_ascii=False) + "\n")
        print(f"  ✓ {len(zh)} zh chars  in {elapsed:.1f}s  (total so far: {len(out_chunks)})", flush=True)

    if dry_run or not out_chunks:
        return

    # Sort by source order before final rewrite. Append-write puts chunks in
    # completion order, which diverges from source order whenever a chunk
    # fails on first attempt and gets resumed later (observed 2026-05-21:
    # TOBIT 1:3-22 failed and was retried after TOBIT 2:1-3:6, so the TOC
    # showed them out of biblical order). title_en is the source heading,
    # so source.index(title_en) gives the correct row.
    src_order = {c["title_en"]: i for i, c in enumerate(src_chunks)}
    def src_idx(chunk: dict) -> int:
        return src_order.get(chunk.get("title_en", ""), 10**9)
    out_chunks.sort(key=src_idx)

    # Rewrite JSONL with renumbered chunk_index (the append-write above may
    # have produced non-contiguous indices if resume hit duplicates).
    for i, c in enumerate(out_chunks):
        c["chunk_index"] = i
    with open(out_path, "w", encoding="utf-8") as f:
        for c in out_chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"\nWrote {out_path}  ({out_path.stat().st_size//1024} KB)  [sorted to source order]", flush=True)

    # R2 + DB previews
    try:
        se.push_to_r2(ebook_id, out_path)
        print("  ✓ pushed R2")
    except Exception as e:
        print(f"  ⚠ R2 push failed: {e}", file=sys.stderr)

    # Update DB
    total_chars = sum(len(c["content"]) for c in out_chunks)
    now = datetime.utcnow().isoformat() + "Z"
    patch = {
        "chunk_count": len(out_chunks),
        "total_chars": total_chars,
        "total_pages": len(out_chunks),
        "parsed_at": now,
        "standardized_at": now,
    }
    r = requests.patch(f"{URL}/rest/v1/ebooks?id=eq.{ebook_id}", headers=H_JSON, json=patch, timeout=30)
    r.raise_for_status()
    print(f"  ✓ ebooks row updated  chunk_count={len(out_chunks)}  total_chars={total_chars:,}")

    # Refresh ebook_chunks previews
    requests.delete(f"{URL}/rest/v1/ebook_chunks?ebook_id=eq.{ebook_id}", headers=H_GET, timeout=30)
    rows = [{
        "ebook_id": ebook_id,
        "chunk_index": c["chunk_index"],
        "chunk_type": c["chunk_type"],
        "page_number": c["page_number"],
        "chapter_path": c["chapter_path"],
        "content": c["content"][:200],
        "char_count": len(c["content"]),
    } for c in out_chunks]
    BATCH = 25
    for i in range(0, len(rows), BATCH):
        rr = requests.post(f"{URL}/rest/v1/ebook_chunks", headers=H_JSON, json=rows[i:i+BATCH], timeout=60)
        if not rr.ok:
            print(f"  ⚠ chunk preview insert: {rr.status_code}: {rr.text[:200]}", file=sys.stderr)
    print("  ✓ ebook_chunks previews refreshed")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("ebook_id")
    p.add_argument("--inspect", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--limit", type=int)
    p.add_argument("--engine", choices=["auto", "nvidia", "gemini", "sonnet", "haiku"], default="auto",
                   help="Translation engine. DEFAULT 'auto' = NVIDIA NIM "
                        f"({NVIDIA_MODELS[0]}) first with per-piece Gemini fallback "
                        "(2026-06-03 benchmark: NVIDIA faster + no quota wall). "
                        "'nvidia' = NVIDIA only. 'gemini' = Gemini-first w/ NVIDIA fallback. "
                        "'sonnet' = Claude Sonnet. 'haiku' is RETIRED → routes to 'auto'.")
    p.add_argument("--resume", action="store_true",
                   help="Skip chapter_path already in the on-disk JSONL")
    args = p.parse_args()
    translate_book(args.ebook_id, args.limit, args.inspect, args.dry_run,
                   engine=args.engine, resume=args.resume)


if __name__ == "__main__":
    main()
