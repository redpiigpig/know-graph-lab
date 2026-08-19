#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""希臘羅馬大藏經 — 逐卷補寫條目簡介（intro）。

規範見 .claude/skills/hellenika-curate/SKILL.md §1：
  100–200 字繁體，必含四件事（這是什麼／為何入這一卷／一個具體可查證的細節／
  存世處境），並避開六條禁忌。

引擎鏈 Gemini → NVIDIA（見 feedback_engine_nvidia_no_haiku）。
逐卷跑而非全書一次跑——卷的功能位置是第二要件的依據。

產物寫進 data/hellenika/intros.json（鍵為 corpus id），由 data/hellenika/index.ts
於載入時掛回 work 物件，因此不需改動 greek.ts / roman.ts 的物件字面量。

用法：
    python scripts/hellenika_intro.py --volume A            # 只跑 Α 卷
    python scripts/hellenika_intro.py --volume A --dry-run  # 只出 staging 不合併
    python scripts/hellenika_intro.py --all                 # 依待補數由多到少跑完
    python scripts/hellenika_intro.py --status              # 只看進度
"""
from __future__ import annotations

import argparse
import io
import json
import os
import random
import re
import sys
import time

import requests

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data', 'hellenika')
INTROS = os.path.join(DATA, 'intros.json')
CORPUS = 'c:/tmp/hellenika/corpus.json'
STAGING_DIR = 'c:/tmp/hellenika/staging'

BATCH = 4
MIN_LEN, MAX_LEN = 80, 260


# ─────────────────────────── env / engine ───────────────────────────

def _load_env() -> None:
    path = os.path.join(ROOT, '.env')
    if not os.path.exists(path):
        return
    for line in io.open(path, encoding='utf-8', errors='ignore'):
        m = re.match(r'\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)', line)
        if m:
            os.environ.setdefault(m.group(1), m.group(2).strip().strip('"').strip("'"))


_load_env()

# Windows 的 os.environ 會把鍵一律轉大寫，故比對不分大小寫
GEMINI_KEYS = [v for k, v in sorted(os.environ.items())
               if re.fullmatch(r'gemini_api_key_\d+', k, re.I) and v]
NVIDIA_KEYS = [v for k, v in sorted(os.environ.items())
               if re.fullmatch(r'nvidia_api_key_\d+', k, re.I) and v]
GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-flash-latest')
NVIDIA_URL = os.environ.get('NVIDIA_URL', 'https://integrate.api.nvidia.com/v1')
# 2026-08-19：舊名 deepseek-ai/deepseek-v4-flash-0731 已下架（HTTP 410），改 -0731
NVIDIA_MODEL = os.environ.get('NVIDIA_MODEL', 'deepseek-ai/deepseek-v4-flash-0731')

_gi = 0
_ni = 0
_gcool: dict[int, float] = {}   # key index → 冷卻到期時間
_last_nv = 0.0


def ask_gemini(prompt: str) -> str:
    global _gi
    if not GEMINI_KEYS:
        raise RuntimeError('no Gemini key')
    body = {'contents': [{'parts': [{'text': prompt}]}],
            'generationConfig': {'temperature': 0.25, 'responseMimeType': 'application/json'}}
    base = f'https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent'
    now = time.time()
    for _ in range(len(GEMINI_KEYS)):
        key = GEMINI_KEYS[_gi]
        if _gcool.get(_gi, 0) > now:          # 這把 key 還在冷卻，跳過
            _gi = (_gi + 1) % len(GEMINI_KEYS)
            continue
        for attempt, wait in enumerate((0, 5, 20), start=1):
            if wait:
                time.sleep(wait)
            try:
                r = requests.post(f'{base}?key={key}', json=body, timeout=120)
            except requests.exceptions.RequestException as e:
                print(f'    gemini conn-err key#{_gi}: {type(e).__name__}', file=sys.stderr, flush=True)
                continue
            if r.status_code == 200:
                try:
                    return r.json()['candidates'][0]['content']['parts'][0]['text'].strip()
                except (KeyError, IndexError):
                    print(f'    gemini empty-parts key#{_gi} attempt {attempt}', file=sys.stderr, flush=True)
                    continue
            if r.status_code == 429:
                # 額度用罄，重試無益 —— 冷卻此 key 一小時直接換下一把
                _gcool[_gi] = time.time() + 3600
                print(f'    gemini 429 key#{_gi} → 冷卻 1h', file=sys.stderr, flush=True)
                break
            if r.status_code in (500, 502, 503, 504):
                print(f'    gemini {r.status_code} key#{_gi} attempt {attempt}', file=sys.stderr, flush=True)
                continue
            raise RuntimeError(f'gemini HTTP {r.status_code}: {r.text[:200]}')
        else:
            _gcool[_gi] = time.time() + 600   # 連 5xx 三次，短冷卻
        _gi = (_gi + 1) % len(GEMINI_KEYS)
    raise RuntimeError('all gemini keys exhausted/cooling')


def ask_nvidia(prompt: str) -> str:
    global _ni
    if not NVIDIA_KEYS:
        raise RuntimeError('no NVIDIA key')
    global _last_nv
    for _ in range(len(NVIDIA_KEYS)):
        key = NVIDIA_KEYS[_ni]
        gap = float(os.environ.get('NVIDIA_MIN_INTERVAL', '2'))
        if (wait_for := _last_nv + gap - time.time()) > 0:
            time.sleep(wait_for)
        _last_nv = time.time()
        try:
            r = requests.post(
                f'{NVIDIA_URL}/chat/completions',
                headers={'Authorization': f'Bearer {key}'},
                json={'model': NVIDIA_MODEL,
                      'messages': [{'role': 'user', 'content': prompt}],
                      'temperature': 0.25, 'max_tokens': 3000},
                timeout=float(os.environ.get('NVIDIA_TIMEOUT', '420')))
        except requests.exceptions.RequestException as e:
            print(f'    nvidia conn-err key#{_ni}: {type(e).__name__}', file=sys.stderr, flush=True)
            _ni = (_ni + 1) % len(NVIDIA_KEYS)
            continue
        if r.status_code == 200:
            return r.json()['choices'][0]['message']['content'].strip()
        print(f'    nvidia {r.status_code} key#{_ni}', file=sys.stderr, flush=True)
        _ni = (_ni + 1) % len(NVIDIA_KEYS)
        time.sleep(3)
    raise RuntimeError('all NVIDIA keys exhausted')


def ask(prompt: str) -> str:
    try:
        return ask_gemini(prompt)
    except Exception as e:  # noqa: BLE001 — 整條 Gemini 鏈乾了才降級
        print(f'  ⤷ Gemini 失敗（{e}），改走 NVIDIA', file=sys.stderr, flush=True)
        return ask_nvidia(prompt)


# ─────────────────────────── prompt ───────────────────────────

STATUS_ZH = {
    'whole': '全本（完整傳世）',
    'fragment': '殘篇（原書已佚，靠引文／摘要／紙草綴輯）',
    'inscription': '銘文／紙草（非書籍傳抄，出自石刻、鉛片、金葉或紙草）',
    'hostile': '敵證（僅存於基督教作家為駁斥而作的引用，敘述框架受敵手支配）',
}

PROMPT = """你在替《希臘羅馬大藏經》撰寫書目條目的簡介。這是一部替希臘傳統宗教（它從未有過正典）補做的正典編纂：希臘卷以字母 Α–Ω 立廿四卷，仿聖經的文類光譜編次；羅馬宗教自成一系另立六卷續典。全書斷限公元 529 年。

本批屬 **{canon}‧{sigil} {volume}**{parallel}
本卷定位：{volume_summary}
本部（卷內子分類）：{division}{division_desc}

## 撰寫規範

每筆 **100–200 字繁體中文**，一段到底不分段。**必須包含四件事**（順序不拘）：
1. **這是什麼** —— 內容、體裁、規模，一句話講完。
2. **為什麼入這一卷** —— 它在本藏經的功能位置。這是本簡介與百科條目的根本差別。
3. **一個具體可查證的細節** —— 但**只能取自下面條目欄位裡已經給你的東西**（規模、年代、地點、載體、轉引來源、note 裡提到的事）。欄位沒給的，就不要寫。
4. **存世處境** —— 若存世狀態不是「全本」，必須交代誰保存的、還原到什麼程度、能不能當證據用。

## 禁忌（違反即重寫）

- 禁百科式開頭：「《X》是古希臘詩人 Y 所作的一部長詩，成書於……」——作者與年代欄位已經寫了，不要重複。
- 禁只有讚嘆沒有內容：「這是希臘宗教史上極為重要的文獻」——重要在哪。
- 禁把提示句抄長：下面給的 note 是一行提示，簡介要與它互補而非重述（版面會把 note 顯示在簡介上方）。
- 禁抽象概括取代具體：「反映了古希臘人的宇宙觀」→ 改寫成他們具體怎麼說。
- 禁拿基督教作參照系來抬高它：可以做結構對讀，但不要寫成「這預示了基督教的……」。
- 禁簡體字、日文詞彙、日文漢字寫法。中間點一律用「‧」不用「・」。
- 🚨 **最重要的一條 —— 禁引入欄位以外的事實**：不得寫出條目欄位中沒有出現的專有名詞、數字、書名、人名、地名、引語或具體事件。你對這部書的既有印象一律不得使用，因為那是幻覺的來源。
  · 錯誤示範：欄位只說「現存最早的散文神譜」，你卻寫出「現存約四十則殘篇」「以風、天、地解釋原始諸神」——這兩件事欄位都沒給，一律不准。
  · 若欄位給的資訊不足以寫出具體細節，就改寫該書的**體裁與在本卷的功能**，把篇幅用在第 2 與第 4 點上。寧可平實，不可編造。

## 文風

沉著、具體、有判斷。可以下判語（「分量極重」「古代唯一一部」），但判語後面必須跟著理由。不要學術論文腔，也不要導覽手冊腔。

## 範例（同一部藏經已定稿者）

{shots}

## 本批條目

{items}

## 輸出

只輸出 JSON 物件，鍵為條目的 id，值為簡介字串。不要 markdown 圍欄、不要任何說明。
"""


def fmt_item(w: dict) -> str:
    k = w['work']
    lines = [f"id: {w['id']}", f"漢語定名: {k['title_zh']}"]
    for field, label in (('title_orig', '原題'), ('author', '作者'), ('era', '年代'),
                         ('place', '地點'), ('language', '語言'), ('extent', '規模'),
                         ('parent', '母合集'), ('via', '轉引來源'), ('note', 'note（一行提示）')):
        if k.get(field):
            lines.append(f'{label}: {k[field]}')
    lines.append(f"存世狀態: {STATUS_ZH.get(k.get('status') or 'whole')}")
    if k.get('track') == 'latin':
        lines.append('收錄軌道: 拉丁續典')
    return '\n'.join(lines)


# ─────────────────────────── validate ───────────────────────────

try:
    from opencc import OpenCC
    _cc = OpenCC('s2tw')
except Exception:  # noqa: BLE001
    _cc = None

BAD_OPENERS = re.compile(r'^《[^》]+》(是|為)')
BANNED = ('・', '预', '这', '为了', '国', '经', '书', '关', '现', '实', '从', '会', '发', '过')


def source_blob(w: dict) -> str:
    k = w['work']
    return ' '.join(str(k.get(f) or '') for f in
                    ('title_zh', 'title_orig', 'author', 'era', 'era_narrated', 'place',
                     'language', 'extent', 'parent', 'note', 'via', 'seealso'))


def fabrication(text: str, w: dict) -> str:
    """防編造閘：文中的數字與引語必須在來源欄位裡找得到，否則視為無中生有。

    這是本管線最重要的一道檢查——LLM 會寫出「現存約四十則殘篇」這種
    看起來很像真的、但欄位根本沒給的數字。工具書裡這比空白危險得多。
    """
    src = source_blob(w)
    for num in set(re.findall(r'\d+', text)):
        if num not in src:
            return f'編造數字「{num}」'
    for quote in set(re.findall(r'[「『]([^」』]{2,})[」』]', text)):
        if quote not in src:
            return f'編造引語「{quote}」'
    return ''


def check(text: str, w: dict) -> tuple[str | None, str]:
    """回傳 (清理後文字 or None, 理由)。"""
    t = text.strip().replace('\n', '').replace('・', '‧')
    if _cc:
        conv = _cc.convert(t)
        if conv != t:
            t = conv
    n = len(t)
    if n < MIN_LEN:
        return None, f'太短 {n} 字'
    if n > MAX_LEN:
        return None, f'太長 {n} 字'
    if BAD_OPENERS.match(t):
        return None, '百科式開頭'
    hit = [c for c in BANNED if c in t]
    if hit:
        return None, f'簡體殘留 {hit}'
    note = (w['work'].get('note') or '').strip()
    if note and note.rstrip('。') in t and len(note) > 12:
        return None, 'note 被整句重述'
    if (why := fabrication(t, w)):
        return None, why
    return t, ''


# ─────────────────────────── run ───────────────────────────

def load_json(path: str, default):
    if os.path.exists(path):
        return json.loads(io.open(path, encoding='utf-8').read())
    return default


def save_intros(d: dict) -> None:
    os.makedirs(os.path.dirname(INTROS), exist_ok=True)
    io.open(INTROS, 'w', encoding='utf-8').write(
        json.dumps(d, ensure_ascii=False, indent=1, sort_keys=True) + '\n')


def pending(corpus: dict, intros: dict, volume: str | None):
    out = []
    for w in corpus['works']:
        if volume and w['volume_key'] != volume:
            continue
        if w['work'].get('intro') or w['id'] in intros:
            continue
        out.append(w)
    return out


def shots_for(corpus: dict, intros: dict, volume: str) -> str:
    """優先取同卷已定稿者作 few-shot，同卷不足才向外借。"""
    same = [w for w in corpus['works'] if w['volume_key'] == volume and w['work'].get('intro')]
    other = [w for w in corpus['works'] if w['volume_key'] != volume and w['work'].get('intro')]
    random.shuffle(other)
    picked = (same + other)[:3]
    return '\n\n'.join(
        f"【{w['work']['title_zh']}｜{w['volume_sigil']} {w['volume_name']}】\n{w['work']['intro']}"
        for w in picked)


def run_volume(corpus: dict, intros: dict, volume: str, dry: bool) -> int:
    todo = pending(corpus, intros, volume)
    if not todo:
        return 0
    vol = todo[0]
    print(f"\n=== {vol['volume_sigil']} {vol['volume_name']}（{vol['canon_name']}）待補 {len(todo)} 筆 ===",
          flush=True)

    shots = shots_for(corpus, intros, volume)
    os.makedirs(STAGING_DIR, exist_ok=True)
    staging = os.path.join(STAGING_DIR, f'{volume}.jsonl')
    written = 0

    by_div: dict[str, list] = {}
    for w in todo:
        by_div.setdefault(w['division_key'], []).append(w)

    for div_key, items in by_div.items():
        d0 = items[0]
        for i in range(0, len(items), BATCH):
            chunk = items[i:i + BATCH]
            prompt = PROMPT.format(
                canon=d0['canon_name'], sigil=d0['volume_sigil'], volume=d0['volume_name'],
                parallel=f"（聖經對位：{d0['volume_parallel']}）" if d0.get('volume_parallel') else '',
                volume_summary=d0['volume_summary'],
                division=d0['division_label'],
                division_desc=f"——{d0['division_desc']}" if d0.get('division_desc') else '',
                shots=shots,
                items='\n\n---\n\n'.join(fmt_item(w) for w in chunk),
            )
            try:
                raw = ask(prompt)
            except Exception as e:  # noqa: BLE001
                print(f'  ✗ 整批失敗：{e}', file=sys.stderr, flush=True)
                return written
            raw = re.sub(r'^```(?:json)?|```$', '', raw.strip(), flags=re.M).strip()
            try:
                got = json.loads(raw)
            except json.JSONDecodeError:
                print('  ✗ 回傳非 JSON，跳過本批', file=sys.stderr, flush=True)
                continue

            for w in chunk:
                text = got.get(w['id'])
                if not isinstance(text, str):
                    print(f"  ✗ {w['work']['title_zh']}：無回應", flush=True)
                    continue
                cleaned, why = check(text, w)
                if not cleaned:
                    print(f"  ✗ {w['work']['title_zh']}：{why}", flush=True)
                    continue
                intros[w['id']] = cleaned
                written += 1
                with io.open(staging, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({'id': w['id'], 'title': w['work']['title_zh'],
                                        'intro': cleaned}, ensure_ascii=False) + '\n')
                print(f"  ✓ {w['work']['title_zh']}（{len(cleaned)} 字）", flush=True)
            if not dry:
                save_intros(intros)          # 逐批落地，中途中斷不白做
            time.sleep(2)

    if not dry:
        save_intros(intros)
    return written


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--volume')
    ap.add_argument('--all', action='store_true')
    ap.add_argument('--status', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    corpus = load_json(CORPUS, None)
    if corpus is None:
        raise SystemExit('先跑 python scripts/hellenika_dump.py')
    intros = load_json(INTROS, {})

    if args.status:
        total = len(corpus['works'])
        done = sum(1 for w in corpus['works'] if w['work'].get('intro') or w['id'] in intros)
        print(f'intro {done}/{total}')
        for c in corpus['canons']:
            for v in c['volumes']:
                ws = [w for w in corpus['works'] if w['volume_key'] == v['key']]
                d = sum(1 for w in ws if w['work'].get('intro') or w['id'] in intros)
                flag = '✓' if d == len(ws) else ' '
                print(f"  {flag} {v['sigil']:>3} {v['name']:<12} {d}/{len(ws)}")
        return

    if args.volume:
        run_volume(corpus, intros, args.volume, args.dry_run)
        return

    if args.all:
        order = []
        for c in corpus['canons']:
            for v in c['volumes']:
                n = len(pending(corpus, intros, v['key']))
                if n:
                    order.append((n, v['key']))
        order.sort(reverse=True)
        for n, key in order:
            run_volume(corpus, intros, key, args.dry_run)
        return

    ap.print_help()


if __name__ == '__main__':
    main()
