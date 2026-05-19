"""
episcopal-portrait-backfill.py — fetch Wikipedia portrait thumbnails for famous bishops.

Strategy
--------
1. Pull all `episcopal_succession` rows where `portrait_url IS NULL` and `name_en IS NOT NULL`.
2. For each row, build candidate Wikipedia page titles:
     a. `EXPLICIT_TITLES[name_en]`  ← curated overrides (popes, ambiguous names)
     b. `name_en`                    ← direct lookup
     c. `Pope <number>`, `Patriarch <name>`, `Saint <name>` heuristics
3. Hit `https://en.wikipedia.org/api/rest_v1/page/summary/<title>` for each candidate.
4. Validate the result:
     - HTTP 200
     - `type == 'standard'` (not disambiguation, not missing)
     - Has `thumbnail.source` or `originalimage.source`
     - Description / extract contains a bishop-related keyword
5. PATCH `portrait_url` to the thumbnail URL.

Rate-limit: 1 request/second (Wikipedia's polite guideline).
Resumable: skips bishops who already have `portrait_url`.

Usage
-----
    python scripts/episcopal-portrait-backfill.py            # all famous candidates
    python scripts/episcopal-portrait-backfill.py --dry      # log matches without writing DB
    python scripts/episcopal-portrait-backfill.py --limit 50 # cap iterations
    python scripts/episcopal-portrait-backfill.py --see 羅馬 # one see at a time
"""
from __future__ import annotations
import argparse, json, sys, time, urllib.parse
from pathlib import Path
import requests

# Windows console default cp950 cannot print CJK ── force UTF-8 stdout
try:
    sys.stdout.reconfigure(encoding='utf-8')  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding='utf-8')  # type: ignore[attr-defined]
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
ENV = {}
for line in (ROOT / '.env').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.lstrip().startswith('#'):
        k, v = line.split('=', 1)
        ENV[k.strip().lstrip('﻿')] = v.strip()

SUPABASE_URL = ENV['SUPABASE_URL']
SERVICE_KEY  = ENV['SUPABASE_SERVICE_ROLE_KEY']
PROJECT_REF  = SUPABASE_URL.split('//')[1].split('.')[0]
ADMIN_TOKEN  = ENV['SUPABASE_ACCESS_TOKEN']

WIKI_API = 'https://en.wikipedia.org/api/rest_v1/page/summary/{title}'
HEADERS  = {'User-Agent': 'know-graph-lab/1.0 (research; redpiigpig@gmail.com)'}
KEYWORDS = (
    'pope', 'patriarch', 'archbishop', 'bishop', 'metropolitan', 'catholicos',
    'saint', 'apostle', 'evangelist', 'martyr', 'cardinal', 'monk',
    'church father', 'theologian', 'reformer',
    'primate', 'see of', 'see in',
)

# ── Curated explicit Wikipedia titles ──────────────────────────────
# Maps DB.name_en → Wikipedia page slug (URL-safe).
# Add entries here when auto-resolve picks the wrong article or fails.
EXPLICIT_TITLES: dict[str, str] = {
    # Apostles & 1st-century
    'Saint Peter':        'Saint_Peter',
    'Andrew the Apostle': 'Andrew_the_Apostle',
    'Mark the Evangelist': 'Mark_the_Evangelist',
    'Saint Mark the Evangelist': 'Mark_the_Evangelist',
    'James, son of Zebedee': 'James,_son_of_Zebedee',
    'John the Apostle':   'John_the_Apostle',
    'Bartholomew':        'Bartholomew_the_Apostle',
    'Thomas':             'Thomas_the_Apostle',
    'Thaddaeus':          'Jude_the_Apostle',
    'Paul':               'Paul_the_Apostle',
    'Barnabas':           'Barnabas',
    'James the Just':     'James,_brother_of_Jesus',
    # Roman popes — Wikipedia uses "Pope <Name> <Roman numeral>"
    'Pope Linus':            'Pope_Linus',
    'Pope Clement I':        'Pope_Clement_I',
    'Pope Sixtus I':         'Pope_Sixtus_I',
    'Pope Pius I':           'Pope_Pius_I',
    'Pope Eleutherius':      'Pope_Eleutherius',
    'Pope Victor I':         'Pope_Victor_I',
    'Pope Callixtus I':      'Pope_Callixtus_I',
    'Pope Stephen I':        'Pope_Stephen_I',
    'Pope Sylvester I':      'Pope_Sylvester_I',
    'Pope Damasus I':        'Pope_Damasus_I',
    'Pope Leo I':            'Pope_Leo_I',
    'Pope Gregory I':        'Pope_Gregory_I',
    'Pope Gregory I (the Great)': 'Pope_Gregory_I',
    'Pope Gregory VII':      'Pope_Gregory_VII',
    'Pope Urban II':         'Pope_Urban_II',
    'Pope Innocent III':     'Pope_Innocent_III',
    'Pope Boniface VIII':    'Pope_Boniface_VIII',
    'Pope Pius IX':          'Pope_Pius_IX',
    'Pope Leo XIII':         'Pope_Leo_XIII',
    'Pope Pius X':           'Pope_Pius_X',
    'Pope Pius XI':          'Pope_Pius_XI',
    'Pope Pius XII':         'Pope_Pius_XII',
    'Pope John XXIII':       'Pope_John_XXIII',
    'Pope Paul VI':          'Pope_Paul_VI',
    'Pope John Paul I':      'Pope_John_Paul_I',
    'Pope John Paul II':     'Pope_John_Paul_II',
    'Pope Benedict XVI':     'Pope_Benedict_XVI',
    'Pope Francis':          'Pope_Francis',
    'Pope Leo XIV':          'Pope_Leo_XIV',
    # Constantinople
    'John Chrysostom':       'John_Chrysostom',
    'Gregory of Nazianzus':  'Gregory_of_Nazianzus',
    'Nestorius':             'Nestorius',
    'Photios I of Constantinople': 'Photios_I_of_Constantinople',
    'Michael I Cerularius':  'Michael_I_Cerularius',
    'Gennadius Scholarius':  'Gennadius_Scholarius',
    'Bartholomew I of Constantinople': 'Bartholomew_I_of_Constantinople',
    # Alexandria
    'Athanasius':            'Athanasius_of_Alexandria',
    'Athanasius of Alexandria': 'Athanasius_of_Alexandria',
    'Cyril of Alexandria':   'Cyril_of_Alexandria',
    'Dioscorus':             'Dioscorus_I_of_Alexandria',
    'Tawadros II':           'Pope_Tawadros_II_of_Alexandria',
    'Shenouda III':          'Pope_Shenouda_III_of_Alexandria',
    'Cyril VI':              'Pope_Cyril_VI_of_Alexandria',
    # Antioch
    'Ignatius of Antioch':   'Ignatius_of_Antioch',
    'John of Antioch':       'John_of_Antioch',
    'Severus of Antioch':    'Severus_of_Antioch',
    'Ignatius Aphrem II':    'Ignatius_Aphrem_II',
    # Jerusalem
    'James the Just':        'James,_brother_of_Jesus',
    'Cyril of Jerusalem':    'Cyril_of_Jerusalem',
    'Sophronius':            'Sophronius_of_Jerusalem',
    # Armenia (Etchmiadzin / Catholicos)
    'Gregory the Illuminator': 'Gregory_the_Illuminator',
    'Nerses I':              'Nerses_I',
    'Sahak I':               'Sahak_of_Armenia',
    'Mesrop Mashtots':       'Mesrop_Mashtots',
    'Karekin II':            'Karekin_II',
    # Assyria / Church of the East
    'Mar Mari':              'Mar_Mari',
    'Mar Aprem':             'Aprem_Mooken',
    # Cappadocian fathers
    'Basil of Caesarea':     'Basil_of_Caesarea',
    'Basil the Great':       'Basil_of_Caesarea',
    'Gregory of Nyssa':      'Gregory_of_Nyssa',
    'Eusebius of Caesarea':  'Eusebius',
    # Western Fathers
    'Augustine of Hippo':    'Augustine_of_Hippo',
    'Ambrose':               'Ambrose',
    'Ambrose of Milan':      'Ambrose',
    'Jerome':                'Jerome',
    'Polycarp':              'Polycarp',
    'Irenaeus':              'Irenaeus',
    'Cyprian':               'Cyprian',
    'Hippolytus of Rome':    'Hippolytus_of_Rome',
    # Anglican reformers
    'Thomas Cranmer':        'Thomas_Cranmer',
    'Hugh Latimer':          'Hugh_Latimer',
    'Nicholas Ridley':       'Nicholas_Ridley_(martyr)',
    'John Jewel':            'John_Jewel',
    'Lancelot Andrewes':     'Lancelot_Andrewes',
    'John Fisher':           'John_Fisher',
    'Matthew Parker':        'Matthew_Parker',
    'Robert Grosseteste':    'Robert_Grosseteste',
    'John Cosin':            'John_Cosin',
    # Methodist / Lutheran
    'John Wesley':           'John_Wesley',
    'Thomas Coke':           'Thomas_Coke_(bishop)',
    'Francis Asbury':        'Francis_Asbury',
    'Martin Luther':         'Martin_Luther',
    'Philipp Melanchthon':   'Philip_Melanchthon',
    'Olaus Petri':           'Olaus_Petri',
    # Eastern / Slavic patriarchs
    'Tikhon of Moscow':      'Tikhon_of_Moscow',
    'Sergius of Moscow':     'Patriarch_Sergius_of_Moscow',
    'Kirill of Moscow':      'Patriarch_Kirill_of_Moscow',
    'Aleksey II':            'Patriarch_Alexy_II_of_Moscow',
    # Canterbury
    'Augustine of Canterbury': 'Augustine_of_Canterbury',
    'Anselm':                'Anselm_of_Canterbury',
    'Thomas Becket':         'Thomas_Becket',
    'William Laud':          'William_Laud',
    'Justin Welby':          'Justin_Welby',
    'Rowan Williams':        'Rowan_Williams',
    'Michael Ramsey':        'Michael_Ramsey',
    'George Carey':          'George_Carey',
    # Modern Anglican / activists
    'Desmond Tutu':          'Desmond_Tutu',
    # Theodoret / Theodore
    'Theodoret':             'Theodoret',
    'Theodore of Mopsuestia': 'Theodore_of_Mopsuestia',
    'Theodore of Studios':   'Theodore_the_Studite',
    # Misc
    'Albertus Magnus':       'Albertus_Magnus',
    'Bonaventure':           'Bonaventure',
    'Thomas Aquinas':        'Thomas_Aquinas',
    'Hosius of Cordoba':     'Hosius_of_Corduba',
    'Papias':                'Papias_of_Hierapolis',
}


def fetch_bishops(see_filter: str | None = None) -> list[dict]:
    """Pull bishops that need portraits."""
    where = "portrait_url IS NULL AND name_en IS NOT NULL"
    if see_filter:
        where += f" AND see = '{see_filter.replace(chr(39), chr(39) * 2)}'"
    sql = f"""
    SELECT id, name_zh, name_en, see, succession_number
    FROM episcopal_succession
    WHERE {where}
    ORDER BY see, succession_number NULLS LAST, start_year NULLS LAST;
    """
    r = requests.post(
        f'https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query',
        headers={'Authorization': f'Bearer {ADMIN_TOKEN}', 'Content-Type': 'application/json'},
        json={'query': sql},
        timeout=30,
    )
    if r.status_code != 201:
        raise RuntimeError(f'DB query failed: {r.status_code} {r.text[:300]}')
    return r.json()


def candidate_titles(name_en: str) -> list[str]:
    """Return ordered list of Wikipedia page title candidates."""
    if name_en in EXPLICIT_TITLES:
        return [EXPLICIT_TITLES[name_en]]
    titles: list[str] = []
    # Direct
    titles.append(name_en.replace(' ', '_'))
    # Strip trailing parenthetical
    clean = name_en.split('(')[0].strip()
    if clean != name_en:
        titles.append(clean.replace(' ', '_'))
    # If looks like a pope but lacks "Pope " prefix
    if not name_en.startswith('Pope') and any(name_en.startswith(p) for p in ('John ', 'Leo ', 'Pius ', 'Benedict ', 'Gregory ', 'Innocent ', 'Clement ', 'Urban ')):
        titles.append(f'Pope_{clean.replace(" ", "_")}')
    return titles


def fetch_summary(title: str) -> dict | None:
    url = WIKI_API.format(title=urllib.parse.quote(title, safe='_'))
    r = requests.get(url, headers=HEADERS, timeout=15)
    if r.status_code != 200:
        return None
    return r.json()


def validate(summary: dict) -> tuple[bool, str | None]:
    """Return (ok, thumbnail_url or None)."""
    if summary.get('type') != 'standard':
        return False, None
    img = (summary.get('thumbnail') or {}).get('source') or (summary.get('originalimage') or {}).get('source')
    if not img:
        return False, None
    text = ((summary.get('description') or '') + ' ' + (summary.get('extract') or '')).lower()
    if not any(k in text for k in KEYWORDS):
        return False, None
    return True, img


def patch_portrait(bid: str, url: str) -> bool:
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/episcopal_succession?id=eq.{bid}",
        headers={
            'apikey': SERVICE_KEY,
            'Authorization': f'Bearer {SERVICE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal',
        },
        json={'portrait_url': url},
        timeout=15,
    )
    return r.status_code in (200, 204)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry', action='store_true', help='Log matches without writing DB')
    ap.add_argument('--limit', type=int, default=0, help='Cap iterations (0=unlimited)')
    ap.add_argument('--see', type=str, default=None, help='Restrict to one see (e.g. 羅馬)')
    ap.add_argument('--only-curated', action='store_true', help='Skip rows not in EXPLICIT_TITLES')
    ap.add_argument('--sleep', type=float, default=1.0, help='Seconds between Wikipedia calls')
    args = ap.parse_args()

    bishops = fetch_bishops(see_filter=args.see)
    print(f'Got {len(bishops)} candidate bishops')

    n_done = 0
    n_hit = 0
    n_miss = 0
    log_path = Path('c:/tmp/portrait_backfill.log')
    log_path.write_text('', encoding='utf-8')

    for b in bishops:
        if args.limit and n_done >= args.limit:
            break
        name_en = b['name_en']
        name_zh = b['name_zh']
        if args.only_curated and name_en not in EXPLICIT_TITLES:
            continue
        n_done += 1
        titles = candidate_titles(name_en)
        hit = False
        for t in titles:
            summary = fetch_summary(t)
            time.sleep(args.sleep)
            if not summary:
                continue
            ok, img = validate(summary)
            if ok and img:
                tag = 'DRY' if args.dry else 'HIT'
                print(f'[{tag}] {name_zh} | {name_en} → {t} → {img.rsplit("/", 1)[-1][:50]}')
                log_path.open('a', encoding='utf-8').write(f'{tag}\t{b["id"]}\t{name_zh}\t{name_en}\t{t}\t{img}\n')
                if not args.dry:
                    if patch_portrait(b['id'], img):
                        n_hit += 1
                    else:
                        print(f'  ⚠ PATCH failed for {name_zh}')
                else:
                    n_hit += 1
                hit = True
                break
        if not hit:
            n_miss += 1

    print(f'\n=== Done. iterations={n_done}, hits={n_hit}, misses={n_miss} ===')


if __name__ == '__main__':
    main()
