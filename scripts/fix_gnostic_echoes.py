"""Re-translate gnostic_sections whose zh text is a prompt-echo (deepseek parroted
the instructions instead of translating, on trivial/noise source paragraphs).
The new echo-guard in nvidia_translate degrades to the source on persistent echo,
so this both fixes existing rows and is safe to re-run."""
import os, sys, json
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.getcwd(), ".env"))
sys.path.insert(0, "scripts")
import translate_ebook_to_zh as te
import ingest_gnostic as ig

te.PROMPT_TMPL = ig.GNOSTIC_PROMPT_TMPL
URL = os.environ["SUPABASE_URL"]
SK = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
ref = URL.split("//")[1].split(".")[0]
H_MGMT = {"Authorization": "Bearer " + os.environ["SUPABASE_ACCESS_TOKEN"], "Content-Type": "application/json"}
H_REST = {"apikey": SK, "Authorization": f"Bearer {SK}", "Content-Type": "application/json", "Prefer": "return=minimal"}

MARKERS = ["只輸出這一段", "請提供您想翻譯", "我準備好為您", "準備好為您進行翻譯",
           "逐字翻成繁體中文", "逐字翻譯為繁體中文", "專業譯者", "不要前言",
           "請提供", "我已準備好", "無須翻譯", "請貼上", "請輸入您"]


def main():
    conds = " OR ".join("z.text LIKE '%" + m + "%'" for m in MARKERS)
    q = ("select z.doc_slug, z.order_index, e.text en from gnostic_sections z "
         "join gnostic_sections e on e.doc_slug=z.doc_slug and e.order_index=z.order_index "
         "and e.version_code='gnosis_en' where z.version_code='zh' and (" + conds + ") "
         "order by z.doc_slug, z.order_index")
    rows = requests.post(f"https://api.supabase.com/v1/projects/{ref}/database/query",
                         headers=H_MGMT, json={"query": q}).json()
    print(f"re-translating {len(rows)} echoed sections...", flush=True)
    fixed = 0
    for r in rows:
        en = r["en"]
        try:
            zh = te.nvidia_translate(en).strip()
        except Exception as ex:  # noqa: BLE001
            zh = en
            print("  err->source:", str(ex)[:60], flush=True)
        pr = requests.patch(
            f"{URL}/rest/v1/gnostic_sections?doc_slug=eq.{r['doc_slug']}&version_code=eq.zh&order_index=eq.{r['order_index']}",
            headers=H_REST, data=json.dumps({"text": zh, "char_count": len(zh)}), timeout=60)
        ok = pr.status_code in (200, 204)
        fixed += ok
        print(f"  {'OK' if ok else 'XX'} {r['doc_slug']}#{r['order_index']}: {en[:28]!r} -> {zh[:40]!r}", flush=True)
    print(f"fixed {fixed}/{len(rows)}")


if __name__ == "__main__":
    main()
