# -*- coding: utf-8 -*-
"""簡報文字潤飾：把投影片上不通順、不合中文慣用法的句子改順。

課堂簡報的字是投影出去給全班看的，一句話不順，四十個人一起卡住。
本檔把 `course_slides_data*.py` 裡所有會投影的字送 LLM 重讀一遍，
只改「讀起來不像中文」的地方，改完寫回原始碼。

引擎依 repo 慣例 Gemini 主 → NVIDIA 備。

🚨 這是**改既有文字**，不是重寫，所以每一條改寫都要過閘（`acceptable`）：
   數字、拉丁字、書名號與引號內的字、全形對齊符號一律不准動，長度也不准差太多——
   簡報版面是照字數估行的，一句話多五個字就可能多一行、多一行就可能多一頁。
   過不了閘的一律丟掉，寧可不改。

用法：
  python scripts/course_slides_polish.py --scan          # 送 LLM，可中斷續跑
  python scripts/course_slides_polish.py --report        # 看改了哪些（不寫檔）
  python scripts/course_slides_polish.py --apply         # 寫回 data 檔
  python scripts/course_slides_polish.py --apply --limit 50
"""
import ast
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / 'output' / 'course-slides-polish' / 'ledger.json'
# 🚨 配圖對照表也要一起改：它是拿**投影片標題**當鍵的，標題被潤飾掉一個字，
#    對照表就靜靜對不上、那一頁的圖就消失了，而且不會報錯。
DATA_FILES = (sorted(Path(ROOT / 'scripts').glob('course_slides_data*.py'))
              + [Path(ROOT / 'scripts' / 'course_slide_illustrate.py'),
                 Path(ROOT / 'scripts' / 'course_slides_openers.py')])

BATCH = 20

PROMPT = """你是繁體中文的文字編輯，正在校訂一份要投影給大學部學生看的課堂簡報。

以下每一條都是投影片上的一行字。請逐條判斷它讀起來是不是通順、自然的臺灣繁體中文，
只有**確實需要修改**的才回報。需要修改的情形是：

‧ 錯字、別字（例如「的／地／得」用錯、同音字打錯）
‧ 語序不像中文（歐化語法、被動句過重、修飾語堆在名詞前面太長）
‧ 翻譯腔、書面語過硬，唸出來會卡（這是要站在台上唸給學生聽的）
‧ 冗贅或殘缺，句子讀不完整
‧ 標點誤用（頓號與逗號混用、破折號位置不對）

判準是：把這一行**唸出來**給大一學生聽，順不順、聽不聽得懂。順就不要動。

**絕對不可以做的事**：
‧ 不可改動任何數字、年代、外文（拉丁字母）原字
‧ 不可改動「」『』《》〈〉 裡面的任何字——那是引文與書名，必須逐字照舊
‧ 不可改動專有名詞、人名、地名、學術術語的譯名
‧ 不可改動全形空白、→、｜、／ 這些排版對齊符號的數量與位置
‧ 不可改變原意、不可補充原文沒有的資訊、不可刪掉原文有的資訊
‧ 字數要盡量與原文相當（版面是照字數估行的），不可大幅加長或縮短
‧ 一律繁體字，不可出現簡體字

回覆格式：只輸出 JSON 陣列，每個元素是 {{"i": 編號, "text": "改好的整行字"}}。
沒有任何一條需要改就輸出 []。不要輸出說明文字，不要用 markdown 圍欄。

要校訂的行：
{items}
"""

# ── 閘 ──────────────────────────────────────────────────────────────────────
TOKEN_RE = re.compile(r'[0-9A-Za-zÀ-ɏͰ-Ͽ\u0400-\u04FF]+')
QUOTED_RE = re.compile(r'[「『《〈][^」』》〉]*[」』》〉]')
MARKS = '　→｜／▍‧－—…（）()〔〕[]%＋'


def _tokens(s):
    return sorted(TOKEN_RE.findall(s))


def _quoted(s):
    return sorted(QUOTED_RE.findall(s))


def _marks(s):
    return {m: s.count(m) for m in MARKS}


def _new_simplified(old, new):
    """new 裡有沒有「原文沒有、而且是簡體」的字。

    🚨 不能直接拿 opencc 比對整句：s2t 會把 祢→禰、于→於、余→餘，
    原文本來就有的那些字會被誤判。所以只看**新增**的字。
    """
    try:
        import opencc
    except ImportError:
        return []
    conv = opencc.OpenCC('s2t')
    return [c for c in set(new) - set(old) if conv.convert(c) != c]


def acceptable(old, new):
    """回傳 None＝可以採用，否則回傳退件理由。"""
    new = (new or '').strip()
    if not new or new == old:
        return '沒變'
    if _tokens(old) != _tokens(new):
        return '動到數字或外文'
    if _quoted(old) != _quoted(new):
        return '動到引號／書名號內的字'
    if _marks(old) != _marks(new):
        return '動到排版符號'
    if abs(len(new) - len(old)) > max(3, len(old) * 0.25):
        return f'長度差太多（{len(old)}→{len(new)}）'
    bad = _new_simplified(old, new)
    if bad:
        return '出現簡體字 ' + ''.join(bad)
    return None


# ── LLM ─────────────────────────────────────────────────────────────────────
def _ask(prompt):
    """Gemini 主、NVIDIA 備。回傳純文字。"""
    try:
        import qianmian_llm
        txt, _ = qianmian_llm.ask(prompt, model='gemini-2.5-flash',
                                  temperature=0.2, max_tokens=8192)
        if txt and txt.strip():
            return txt
    except Exception as e:                       # noqa: BLE001
        print(f'　gemini 失敗（{type(e).__name__}: {e}），改走 NVIDIA')
    import translate_ebook_to_zh as engines
    return engines.nvidia_chat(prompt, max_tokens=8192)


def _parse(txt):
    txt = re.sub(r'^```(?:json)?|```$', '', (txt or '').strip(),
                 flags=re.M).strip()
    m = re.search(r'\[.*\]', txt, re.S)
    if not m:
        return []
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return []


def load_ledger():
    if LEDGER.exists():
        return json.loads(LEDGER.read_text(encoding='utf-8'))
    return {'done': [], 'fixes': {}, 'rejected': {}}


def save_ledger(led):
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(json.dumps(led, ensure_ascii=False, indent=1),
                      encoding='utf-8')


def scan(limit=None):
    import course_slides_strings as S
    texts = [t for t in S.collect() if len(t) >= 6]
    led = load_ledger()
    done = set(led['done'])
    todo = [t for t in texts if t not in done]
    if limit:
        todo = todo[:limit]
    print(f'待校訂 {len(todo)} 條（全部 {len(texts)} 條，已看過 {len(done)} 條）')
    for start in range(0, len(todo), BATCH):
        chunk = todo[start:start + BATCH]
        listing = '\n'.join(f'{i + 1}. {t}' for i, t in enumerate(chunk))
        try:
            out = _parse(_ask(PROMPT.format(items=listing)))
        except Exception as e:                   # noqa: BLE001
            print(f'　批次 {start // BATCH + 1} 失敗：{type(e).__name__}: {e}')
            time.sleep(5)
            continue
        for item in out:
            try:
                old = chunk[int(item['i']) - 1]
            except (KeyError, ValueError, IndexError, TypeError):
                continue
            new = str(item.get('text', ''))
            why = acceptable(old, new)
            if why:
                led['rejected'][old] = f'{new}　←　{why}'
            else:
                led['fixes'][old] = new
        led['done'].extend(chunk)
        save_ledger(led)
        print(f'　{start + len(chunk)}/{len(todo)}　'
              f'採用 {len(led["fixes"])}　退件 {len(led["rejected"])}')
    return led


# ── 寫回原始碼 ──────────────────────────────────────────────────────────────
def _literal(text):
    """把字串寫成 Python 字面值。內含單引號才改用雙引號。"""
    if "'" in text and '"' not in text:
        return '"' + text.replace('\\', '\\\\').replace('\n', '\\n') + '"'
    body = text.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n')
    return "'" + body + "'"


def _spans(path):
    """{字串值: [(起, 迄), ...]}——含隱式相連的多段字串，整段一起換掉。"""
    src = path.read_text(encoding='utf-8')
    lines = src.splitlines(keepends=True)
    offs, at = [], 0
    for ln in lines:
        offs.append(at)
        at += len(ln)
    out = {}
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            a = offs[node.lineno - 1] + node.col_offset
            b = offs[node.end_lineno - 1] + node.end_col_offset
            out.setdefault(node.value, []).append((a, b))
    return src, out


def apply_fixes(fixes, dry=False):
    changed, hit = {}, set()
    for path in DATA_FILES:
        src, spans = _spans(path)
        edits = []
        for old, new in fixes.items():
            for a, b in spans.get(old, []):
                edits.append((a, b, _literal(new)))
                hit.add(old)
        if not edits:
            continue
        for a, b, lit in sorted(edits, reverse=True):
            src = src[:a] + lit + src[b:]
        ast.parse(src)                    # 寫壞了就在這裡炸，不要留到執行時
        changed[path] = src
        if not dry:
            path.write_text(src, encoding='utf-8')
    return changed, hit


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    args = sys.argv[1:]
    limit = int(args[args.index('--limit') + 1]) if '--limit' in args else None
    if '--scan' in args:
        scan(limit)
    led = load_ledger()
    if '--report' in args:
        for old, new in list(led['fixes'].items())[:limit or 40]:
            print(f'－ {old}\n＋ {new}\n')
        print(f'採用 {len(led["fixes"])} 條，退件 {len(led["rejected"])} 條')
    if '--apply' in args:
        changed, hit = apply_fixes(led['fixes'])
        print(f'改寫 {len(hit)} 條，動到 {len(changed)} 個檔：')
        for p in changed:
            print('　', p.name)
        missing = set(led['fixes']) - hit
        if missing:
            print(f'⚠ 有 {len(missing)} 條在原始碼裡找不到（多半是動態組出來的字）')
