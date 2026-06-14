"""Curate /gnostic corpus naming + structure (2026-06-14).

User-approved plan:
  (1) DELETE junk / nav / bookstore / prompt-echo entries (+ their sections).
  (2) MOVE modern scholars' secondary works into the `modern` category, sorted
      to the bottom (display_order >= 1000) so they sit 「放下面」.
  (3) RENAME title_zh to standardise proper nouns / book names / person names:
      - overlapping docs are aligned EXACTLY to their /apocrypha (黃根春 典外文獻)
        counterpart so the two libraries stay consistent and the authoritative
        Chinese can later be imported directly. The apocrypha doc slug is stored
        in gnostic_documents.apocrypha_slug.
      - non-overlapping docs are self-translated with glossary-authoritative names
        (Marcion=馬吉安, Clement=革利免, Celsus=塞爾蘇斯, Heracleon=赫拉克勒翁,
        Basilides=巴西理德, Faustus=米利夫的浮士德…) + biblical names from
        /apocrypha (Thomas=多馬, Mary=馬利亞, Andrew=安得烈, Stephen=司提反) +
        traditional-Chinese fixes (论→論).

Usage:
  python -X utf8 scripts/curate_gnostic_naming.py --dry     # preview (default)
  python -X utf8 scripts/curate_gnostic_naming.py --apply   # write to DB
"""
import os, sys, json, requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.getcwd(), ".env"))
URL = os.environ["SUPABASE_URL"]
SK = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
TOKEN = os.environ.get("SUPABASE_ACCESS_TOKEN")
H = {"apikey": SK, "Authorization": f"Bearer {SK}", "Content-Type": "application/json"}
APPLY = "--apply" in sys.argv

# ── (1) DELETE — junk / nav / bookstore / prompt-echo ──────────────────────
DELETE = [
    # dead_sea: every doc is a bookstore/timetable/resource nav page (verified
    # all start with 書店有售/書店/時間表). Real DSS texts live in /apocrypha Qumran.
    "texts-from-the-dead-sea-scrolls", "timetable-of-dead-sea-scroll-scholarship",
    "resources-for-further-study", "recommended-books", "available-in-the-bookstore",
    "dead-sea-scrolls-internet-resources", "selected-texts-from-the-dead-sea-scrolls",
    "dead-sea-scrolls-section", "texts", "timetable", "resources",
    # mead bookstore nav
    "mead-collection-bookstore", "g-r-s-mead-collection-bookstore",
    # valentinus nav / index
    "contents-of-the-valentinian-tradition-section", "virtual-library", "bibliography",
    # christian_apocrypha NHL index page
    "nag-hammadi-library",
]

# ── (2) MOVE to `modern` — named modern scholars' secondary works ──────────
MOVE_TO_MODERN = [
    "elaine-pagels-excellent-popular-introduction",
    "gnostic-gospels",
    "dr-marvin-meyer-s-introduction-to-the-gnostic-bible",
    "genesis-and-gnosis",
    "an-introduction-to-pistis-sophia-by-g-r-s-mead",
    "essay-on-popular-and-scholarly-response",
    "on-the-trail-of-the-winged-god-hermes-and-hermeticism-throughout-the-ages",
    "an-introduction-to-g-r-s-mead-s-translation-of-the-corpus-hermeticum",
    "kurt-rudolph-the-mandaean-religion",
    "e-s-drower-the-mandaeans-of-iraq-and-iran",
    "theology-of-the-leading-gnostic-christian-of-his-age-valentinus",
]

# ── (3a) APOCRYPHA-ALIGN — gnostic_slug -> apocrypha_slug ──────────────────
# title_zh / title_zh_short copied verbatim from the apocrypha doc.
APOC_ALIGN = {
    "gospel-of-thomas": "gthom",
    "gospel-of-philip": "gphilip",
    "gospel-of-truth": "gtruth",
    "gospel-of-mary": "gmary",
    "gospel-according-to-mary-magdalene": "gmary",
    "apocalypse-of-adam": "adam-apoc",
    "apocalypse-of-peter": "apoc-peter-cop",      # NHC: Coptic Apocalypse of Peter
    "letter-of-peter-to-philip": "peter-philip",
    "apocalypse-of-paul": "apoc-paul-cop",         # NHC: Coptic Apocalypse of Paul
    "apocalypse-of-james": "apoc-james-1",         # (First) Apocalypse of James
    "sophia-of-jesus-christ": "soph-jesus",
    "pistis-sophia": "pistis-sophia",
    "apocryphon-of-john": "john-apocryphon",
    "secret-book-of-john": "john-apocryphon",
    "acts-of-john": "acts-john",
    "acts-of-thomas": "acts-thomas",
    "odes-of-solomon": "odes-solomon",
    "secret-gospel-of-mark": "q-secret-mark",
    "gospel-of-james": "protoevangelium-james",
    "gospel-of-nicodemos": "gnicodemus",
    "an-arabic-infancy-gospel": "infancy-arabic",
    "revelation-of-paul": "apoc-paul",             # Visio Pauli
    "gospel-of-the-nativity-of-mary": "birth-mary",
}

# ── (3b) RENAME — explicit self-translated titles (glossary-authoritative) ──
RENAME = {
    # nag_hammadi
    "tripartite-tractate": "三部論文",
    "book-of-thomas-the-contender": "多馬爭辯者之書",
    "apocryphon-of-james": "雅各藏經",
    "thought-of-norea": "諾蕾亞的思想",
    "a-valentinian-exposition": "瓦倫廷派的闡釋",
    # gnostic_scriptures
    "greek-gospel-of-thomas-texts-papyrus-oxyrhynchus": "希臘文多馬福音：俄西林古蒲草紙",
    "basilides-fragments-from-his-writings": "巴西理德著作殘卷",
    "ptolemy-commentary-on-the-gospel-of-john-prologue": "托勒密：約翰福音序言評註",
    "ptolemy-letter-to-flora": "托勒密致芙蘿拉書",
    "epiphanes-on-righteousness": "埃皮法內斯論正義",
    "theodotus-the-excerpta-ex-theodoto": "狄奧多托語錄（Excerpta ex Theodoto）",
    "heracleon-fragments-from-his-commentary-on-the-gospel-of-john": "赫拉克勒翁：約翰福音評註殘篇",
    "translation-of-the-naassene-psalm": "拿俄賽尼派讚美詩譯文",
    "marcion-the-gospel-of-the-lord-and-other-writings": "馬吉安：主福音及其他著作",
    # valentinus (kept)
    "valentinian-school": "瓦倫廷派學派",
    # mead — untranslated titles
    "did-jesus-live-100-bc": "耶穌活在公元前 100 年嗎？",
    "commentary-on-pymander": "《牧人者》評註",
    "introduction-to-marcion": "馬吉安導論",
    "concerning-h-p-b": "論 H.P.B.（布拉瓦茨基夫人）",
    "brief-biographical-introduction": "簡要生平導論",
    "simon-magus": "行邪術的西門（西門·馬古斯）",
    # polemics — series normalisation + name fixes
    "against-the-valentinians": "駁瓦倫廷派",
    "against-all-heresies-book-1": "駁斥諸異端 第一卷",
    "against-all-heresies-book-2": "駁斥諸異端 第二卷",
    "against-all-heresies-book-3": "駁斥諸異端 第三卷",
    "against-all-heresies-book-4": "駁斥諸異端 第四卷",
    "against-all-heresies-book-5": "駁斥諸異端 第五卷",
    "against-marcion-book-1": "駁馬吉安 第一卷",
    "against-marcion-book-2": "駁馬吉安 第二卷",
    "against-marcion-book-3": "駁馬吉安 第三卷",
    "against-marcion-book-4": "駁馬吉安 第四卷",
    "against-marcion-book-5": "駁馬吉安 第五卷",
    "against-hermogenes": "駁赫摩根尼",
    "against-praxeas": "駁普拉克塞亞",
    "prescriptions-against-heretics": "駁異端規範",
    "appendix-against-all-heresy": "附錄：駁一切異端",
    "scorpiace": "解蠍毒（Scorpiace）",
    "refutations-of-all-heresies-book-1": "駁斥一切異端 第一卷",
    "refutations-of-all-heresies-book-4": "駁斥一切異端 第四卷",
    "refutations-of-all-heresies-book-5": "駁斥一切異端 第五卷",
    "refutations-of-all-heresies-book-6": "駁斥一切異端 第六卷",
    "refutations-of-all-heresies-book-7": "駁斥一切異端 第七卷",
    "refutations-of-all-heresies-book-8": "駁斥一切異端 第八卷",
    "refutations-of-all-heresies-book-9": "駁斥一切異端 第九卷",
    "refutations-of-all-heresies-book-10": "駁斥一切異端 第十卷",
    "contra-faustum-manichaeum-books-1-15": "駁摩尼教徒浮士德 第一至十五卷",
    "contra-faustum-manichaeum-books-16-22": "駁摩尼教徒浮士德 第十六至二十二卷",
    "contra-faustum-manichaeum-books-23-33": "駁摩尼教徒浮士德 第二十三至三十三卷",
    "homily-against-marcionists-and-manichaeans": "駁馬吉安派與摩尼教徒講道",
    "third-discourse-to-hypatius-against-mani-marcion-and-bardaisan": "致海帕蒂烏斯第三論：駁摩尼、馬吉安與巴爾戴桑",
    "clement-of-alexandria-and-the-secret-gospel-of-mark": "亞歷山卓的革利免與馬可的神秘福音",
    "stromata-book-3": "雜記 第三卷",
    "stromata-book-6": "雜記 第六卷",
    "recognitions-book-2": "認信錄 第二卷",
    "recognitions-book-3": "認信錄 第三卷",
    "contra-celsum-book-1": "駁塞爾蘇斯 第一卷",
    "contra-celsum-book-2": "駁塞爾蘇斯 第二卷",
    "contra-celsum-book-3": "駁塞爾蘇斯 第三卷",
    "contra-celsum-book-4": "駁塞爾蘇斯 第四卷",
    "contra-celsum-book-5": "駁塞爾蘇斯 第五卷",
    "contra-celsum-book-6": "駁塞爾蘇斯 第六卷",
    "contra-celsum-book-7": "駁塞爾蘇斯 第七卷",
    "contra-celsum-book-8": "駁塞爾蘇斯 第八卷",
    "lost-commentary-of-heracleon": "赫拉克勒翁遺失的評註",
    "commentary-on-the-gospel-of-john-book-i": "約翰福音評註 第一卷",
    "commentary-on-the-gospel-of-john-book-ii": "約翰福音評註 第二卷",
    "commentary-on-the-gospel-of-john-book-iv": "約翰福音評註 第四卷",
    "commentary-on-the-gospel-of-john-book-v": "約翰福音評註 第五卷",
    "commentary-on-the-gospel-of-john-book-vi": "約翰福音評註 第六卷",
    "commentary-on-the-gospel-of-john-book-x": "約翰福音評註 第十卷",
    # manichaean — Augustine anti-Manichaean (Latin titles): keep Latin sense, fix names
    "contra-faustum-manichaeum-books-i-xv": "駁摩尼教徒浮士德 第一至十五卷",
    "contra-faustum-manichaeum-books-xvi-xxii": "駁摩尼教徒浮士德 第十六至二十二卷",
    "contra-faustum-manichaeum-books-xxiii-xxxiii": "駁摩尼教徒浮士德 第二十三至三十三卷",
    # christian_apocrypha — biblical name fixes
    "acts-and-martyrdom-of-andrew": "安得烈行傳與殉道記",
    "acts-of-andrew-and-matthew": "安得烈與馬太行傳",
    "acts-and-martyrdom-of-matthew": "馬太行傳與殉道記",
    "acts-of-peter-and-andrew": "彼得與安得烈行傳",
    "acts-of-peter-and-paul": "彼得與保羅行傳",
    "consummation-of-thomas": "多馬的圓滿",
    "revelation-of-stephen": "司提反啟示錄",
    "infancy-gospel-of-thomas-greek-text-a": "多馬的耶穌嬰孩時期福音：希臘文本甲",
    "infancy-gospel-of-thomas-greek-text-b": "多馬的耶穌嬰孩時期福音：希臘文本乙",
    "infancy-gospel-of-thomas-latin-text": "多馬的耶穌嬰孩時期福音：拉丁文本",
    "infancy-gospels-of-jesus": "耶穌嬰孩時期福音書",
    "gospel-of-the-lord-by-marcion": "馬吉安的主福音",
    "teaching-of-addaeus-the-apostle": "使徒阿達伊的教導",
    "gospel-of-pseudo-matthew": "偽馬太福音",
}

# ── (3c) GLOBAL safety-net substitutions (applied to every final title) ────
GLOBAL_SUBS = {
    "托馬斯": "多馬", "多瑪斯": "多馬",          # Thomas
    "瑪麗亞": "馬利亞", "瑪利亞": "馬利亞",        # Mary
    "馬吉翁": "馬吉安",                          # Marcion (glossary ★)
    "凱爾蘇斯": "塞爾蘇斯",                       # Celsus (glossary ★)
    "史蒂芬": "司提反",                          # Stephen (biblical)
    "安德魯": "安得烈",                          # Andrew (biblical)
    "论": "論",                                 # leaked simplified
}


def mgmt_ddl(sql):
    if not TOKEN:
        print("  ! no SUPABASE_ACCESS_TOKEN — skipping DDL"); return
    ref = URL.replace("https://", "").split(".")[0]
    ep = f"https://api.supabase.com/v1/projects/{ref}/database/query"
    r = requests.post(ep, headers={"content-type": "application/json", "Authorization": f"Bearer {TOKEN}"},
                      data=json.dumps({"query": sql}), timeout=60)
    print(f"  DDL {r.status_code}: {sql[:60]}…")
    r.raise_for_status()


def apply_subs(s):
    if not s:
        return s
    for a, b in GLOBAL_SUBS.items():
        s = s.replace(a, b)
    return s


def main():
    docs = requests.get(f"{URL}/rest/v1/gnostic_documents", headers=H,
                        params={"select": "slug,title_zh,title_zh_short,category,display_order"}, timeout=60).json()
    by_slug = {d["slug"]: d for d in docs}
    apoc = requests.get(f"{URL}/rest/v1/apocrypha_documents", headers=H,
                        params={"select": "slug,title_zh,title_zh_short"}, timeout=60).json()
    apoc_by_slug = {a["slug"]: a for a in apoc}

    print(f"=== {'APPLY' if APPLY else 'DRY-RUN'} === ({len(docs)} docs)\n")

    # (1) DELETE
    print(f"--- DELETE {len(DELETE)} docs ---")
    for s in DELETE:
        if s in by_slug:
            print(f"  ✗ {s} | {by_slug[s]['title_zh'][:30]}")
        else:
            print(f"  ? {s} (not found)")
    if APPLY:
        for s in DELETE:
            requests.delete(f"{URL}/rest/v1/gnostic_sections", headers=H, params={"doc_slug": f"eq.{s}"}, timeout=60)
            requests.delete(f"{URL}/rest/v1/gnostic_documents", headers=H, params={"slug": f"eq.{s}"}, timeout=60)

    # (2) MOVE to modern (bottom)
    print(f"\n--- MOVE to `modern` {len(MOVE_TO_MODERN)} docs (display_order 1000+) ---")
    for i, s in enumerate(MOVE_TO_MODERN):
        if s in by_slug:
            print(f"  → modern: {s} | {by_slug[s]['title_zh'][:34]} (was {by_slug[s]['category']})")
            if APPLY:
                requests.patch(f"{URL}/rest/v1/gnostic_documents", headers=H, params={"slug": f"eq.{s}"},
                               data=json.dumps({"category": "modern", "display_order": 1000 + i}), timeout=60)
        else:
            print(f"  ? {s} (not found)")

    # (3) RENAME — apocrypha-align then explicit then global subs
    print(f"\n--- RENAME titles ---")
    changes = 0
    for d in docs:
        s = d["slug"]
        if s in DELETE:
            continue
        new_title, new_short, apoc_slug = d["title_zh"], d["title_zh_short"], None
        if s in APOC_ALIGN:
            a = apoc_by_slug.get(APOC_ALIGN[s])
            if a:
                new_title, new_short, apoc_slug = a["title_zh"], a["title_zh_short"], APOC_ALIGN[s]
        elif s in RENAME:
            new_title = RENAME[s]
        new_title = apply_subs(new_title)
        new_short = apply_subs(new_short)
        if new_title != d["title_zh"] or new_short != d["title_zh_short"] or apoc_slug:
            changes += 1
            tag = f"  [apoc:{apoc_slug}]" if apoc_slug else ""
            if new_title != d["title_zh"]:
                print(f"  {s}: {d['title_zh'][:30]}  →  {new_title}{tag}")
            elif apoc_slug:
                print(f"  {s}: (link only) {new_title}{tag}")
            if APPLY:
                payload = {"title_zh": new_title, "title_zh_short": new_short}
                if apoc_slug:
                    payload["apocrypha_slug"] = apoc_slug
                requests.patch(f"{URL}/rest/v1/gnostic_documents", headers=H, params={"slug": f"eq.{s}"},
                               data=json.dumps(payload), timeout=60)
    print(f"\n  {changes} title/link changes")
    print(f"\n=== {'APPLIED' if APPLY else 'DRY-RUN complete — re-run with --apply'} ===")


if __name__ == "__main__":
    if APPLY:
        print("Adding apocrypha_slug column…")
        mgmt_ddl("ALTER TABLE gnostic_documents ADD COLUMN IF NOT EXISTS apocrypha_slug TEXT;")
    main()
