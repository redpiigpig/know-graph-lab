#!/usr/bin/env python3
"""
Batch-translate historical-states.geojson polygon names → 繁體中文 via Gemini.

Reads `public/maps/historical-states.geojson`, extracts unique `NAME` values,
filters out names already covered by:
  - NE admin_0 NAME_ZHT/NAME_ZH
  - wikidata-states.json (name_en match)
  - STATE_DETAILS in data/maps/historical-states-db.ts
  - SUPPLEMENT_ZH in components/maps/HistoricalBordersMap.vue
  - already in public/maps/polygon-names-zh.json (incremental)

Then batches the rest (40 per call) to Gemini 2.5 Flash, asks for a JSON
mapping of {english: 繁體中文}, and writes back to polygon-names-zh.json.

Usage:
  python scripts/translate_polygon_names_gemini.py            # full run
  python scripts/translate_polygon_names_gemini.py --limit 200
  python scripts/translate_polygon_names_gemini.py --batch 30 --rpm 8

Env: GEMINI_API_KEY (single, or comma-separated, or _1.._10 numbered slots).
"""
from __future__ import annotations
import os, re, json, time, argparse, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"

# ---- minimal .env loader ----
ENV: dict[str, str] = {}
if ENV_FILE.exists():
    for line in ENV_FILE.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line: continue
        k, _, v = line.partition('=')
        ENV[k.strip()] = v.strip().strip('"').strip("'")

def find_gemini_keys() -> list[str]:
    raw = []
    primary = ("GEMINI_API_KEY", "Gemini_API_Key", "gemini_api_key", "GOOGLE_API_KEY")
    for n in primary:
        v = os.environ.get(n) or ENV.get(n)
        if v: raw.append(v); break
    for i in range(1, 11):
        for base in primary:
            v = os.environ.get(f"{base}_{i}") or ENV.get(f"{base}_{i}")
            if v: raw.append(v); break
    keys, seen = [], set()
    for r in raw:
        for piece in r.split(','):
            k = piece.strip()
            if k and k not in seen: seen.add(k); keys.append(k)
    return keys

# ---- file paths ----
STATES_GEOJSON = ROOT / 'public' / 'maps' / 'historical-states.geojson'
WIKIDATA_JSON = ROOT / 'public' / 'maps' / 'wikidata-states.json'
ADM0_GEOJSON = ROOT / 'public' / 'maps' / 'ne_50m_admin_0_countries.geojson'
DB_TS = ROOT / 'data' / 'maps' / 'historical-states-db.ts'
COMPONENT_VUE = ROOT / 'components' / 'maps' / 'HistoricalBordersMap.vue'
OUT_JSON = ROOT / 'public' / 'maps' / 'polygon-names-zh.json'

PROMPT_TMPL = """You are translating world history place / state / culture / tribe names into 繁體中文 (Traditional Chinese, Taiwan style).

Translate each English name below into the most common 繁體中文 name used in Chinese-language history scholarship. Rules:
- Output **繁體中文 only** (no Simplified, no Pinyin, no parentheses, no English).
- Use the established Chinese name when one exists (e.g. "Khmer Empire" → "高棉帝國", "Đại Việt" → "大越", "Champa" → "占婆").
- For tribes / cultures / hunter-gatherer groups, use the established Chinese ethnonym (e.g. "Ainu" → "愛努人", "Saami" → "薩米人", "Polynesians" → "玻里尼西亞人").
- For obscure names with no established Chinese name, do a faithful 音譯 (transliteration).
- For dynasty / state names, append the appropriate suffix (王國/帝國/汗國/王朝 etc.) if present in English.
- Keep responses concise (typically 2-6 漢字).
- DO NOT translate generic descriptors like "Hunter-Foragers" literally — output 「狩獵採集者」.
- DO NOT include English in output values.

Output **only** a JSON object (no markdown fences, no commentary) mapping each English input to its 繁體中文 translation:

{{ "English Name 1": "中文 1", "English Name 2": "中文 2", ... }}

English names to translate:
{names_json}
"""

def load_already_translated() -> dict[str, str]:
    """Load polygon-names-zh.json (existing translations)."""
    if not OUT_JSON.exists(): return {}
    try: return json.loads(OUT_JSON.read_text(encoding='utf-8'))
    except Exception: return {}

def covered_by_existing_sources() -> set[str]:
    """Names already covered by adm0 NAME_ZHT / wikidata / STATE_DETAILS / SUPPLEMENT_ZH."""
    covered: set[str] = set()
    # 1. NE admin_0 NAME_ZHT/NAME_ZH
    adm0 = json.loads(ADM0_GEOJSON.read_text(encoding='utf-8'))
    for f in adm0.get('features', []):
        p = f.get('properties', {})
        if not (p.get('NAME_ZHT') or p.get('NAME_ZH')): continue
        for k in ('NAME','NAME_EN','NAME_LONG','ADMIN','SOVEREIGNT','BRK_NAME'):
            v = p.get(k)
            if v: covered.add(v)
    # 2. wikidata
    wd = json.loads(WIKIDATA_JSON.read_text(encoding='utf-8'))
    for w in wd:
        if w.get('name_zh') and w.get('name_en'): covered.add(w['name_en'])
    # 3. STATE_DETAILS keys (TS source)
    ts = DB_TS.read_text(encoding='utf-8')
    for m in re.finditer(r"^  '([^']+)': \{", ts, re.M):
        covered.add(m.group(1))
    # 4. SUPPLEMENT_ZH (vue source)
    vue = COMPONENT_VUE.read_text(encoding='utf-8')
    sup_block = re.search(r'SUPPLEMENT_ZH:[^=]*=\s*\{([\s\S]*?)\n\}', vue)
    if sup_block:
        for m in re.finditer(r"^\s*'([^']+)':", sup_block.group(1), re.M):
            covered.add(m.group(1))
    return covered

def list_polygon_names() -> set[str]:
    states = json.loads(STATES_GEOJSON.read_text(encoding='utf-8'))
    return { f['properties']['name'] for f in states.get('features', []) if f.get('properties', {}).get('name') }

def call_gemini(model_name: str, key: str, names: list[str]) -> dict[str, str]:
    """Call Gemini, parse JSON response, return mapping."""
    import google.generativeai as genai
    genai.configure(api_key=key)
    model = genai.GenerativeModel(model_name)
    prompt = PROMPT_TMPL.format(names_json=json.dumps(names, ensure_ascii=False, indent=2))
    resp = model.generate_content(
        prompt,
        generation_config={'temperature': 0.0, 'response_mime_type': 'application/json'},
    )
    txt = (resp.text or '').strip()
    # strip markdown fences if any
    txt = re.sub(r'^```(?:json)?\s*|\s*```$', '', txt, flags=re.M).strip()
    try:
        data = json.loads(txt)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"JSON parse failed: {e}\nResponse:\n{txt[:500]}")
    return { k: v for k, v in data.items() if isinstance(k, str) and isinstance(v, str) and v.strip() }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--batch', type=int, default=40, help='names per Gemini call')
    ap.add_argument('--rpm', type=int, default=10, help='requests per minute')
    ap.add_argument('--limit', type=int, default=0, help='stop after N untranslated names (0 = all)')
    ap.add_argument('--model', default='gemini-2.5-flash')
    args = ap.parse_args()

    keys = find_gemini_keys()
    if not keys:
        print('[ERR] No GEMINI_API_KEY found in env or .env', file=sys.stderr); sys.exit(1)
    print(f'[OK] {len(keys)} API key(s) loaded')

    print('Loading existing translations + coverage…')
    existing = load_already_translated()
    covered = covered_by_existing_sources()
    all_names = list_polygon_names()
    print(f'  total polygon names: {len(all_names)}')
    print(f'  covered by adm0/wikidata/details/supplement: {sum(1 for n in all_names if n in covered)}')
    print(f'  already in polygon-names-zh.json: {sum(1 for n in all_names if n in existing)}')

    todo = sorted(n for n in all_names if n not in covered and n not in existing)
    if args.limit > 0: todo = todo[:args.limit]
    print(f'  TO TRANSLATE NOW: {len(todo)}')
    if not todo:
        print('Nothing to do.'); return

    delay = 60.0 / args.rpm
    saved = dict(existing)
    key_idx = 0
    batches = [todo[i:i+args.batch] for i in range(0, len(todo), args.batch)]
    print(f'Batching {len(batches)} requests (~{args.rpm} rpm, ~{len(todo)/args.rpm:.1f} min)')

    for i, batch in enumerate(batches, 1):
        key = keys[key_idx % len(keys)]; key_idx += 1
        print(f'[{i}/{len(batches)}] {len(batch)} names...', end=' ', flush=True)
        attempts = 0
        while True:
            attempts += 1
            try:
                got = call_gemini(args.model, key, batch)
                added = 0
                for n in batch:
                    if n in got and got[n] and got[n] != n:
                        saved[n] = got[n]; added += 1
                print(f'+{added} ({added}/{len(batch)})')
                break
            except Exception as e:
                msg = str(e)[:160]
                if attempts >= len(keys) + 1:
                    print(f'FAIL after {attempts} attempts: {msg}')
                    break
                print(f'retry/rotate ({msg})...', end=' ', flush=True)
                key = keys[key_idx % len(keys)]; key_idx += 1
                time.sleep(2)

        # incremental save every batch (so a crash doesn't lose progress)
        OUT_JSON.write_text(json.dumps(saved, ensure_ascii=False, sort_keys=True, indent=2), encoding='utf-8')
        if i < len(batches): time.sleep(delay)

    print(f'\nDone. polygon-names-zh.json now has {len(saved)} entries.')
    print(f'Coverage on full polygon set: {sum(1 for n in all_names if n in saved or n in covered)}/{len(all_names)} = {100*sum(1 for n in all_names if n in saved or n in covered)/len(all_names):.1f}%')

if __name__ == '__main__':
    main()
