"""Set zh = en (verbatim) for every gnostic_section whose English source is a
trivial page/citation marker — undoes the LLM hallucinations deepseek produced
when handed a bare 'p. 126'. No LLM calls. Safe to re-run."""
import os, json
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.getcwd(), ".env"))
import sys; sys.path.insert(0, "scripts")
from ingest_gnostic import is_trivial_source

URL = os.environ["SUPABASE_URL"]; SK = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
ref = URL.split("//")[1].split(".")[0]
H_MGMT = {"Authorization": "Bearer " + os.environ["SUPABASE_ACCESS_TOKEN"], "Content-Type": "application/json"}
H_REST = {"apikey": SK, "Authorization": f"Bearer {SK}", "Content-Type": "application/json", "Prefer": "return=minimal"}

# Pull en+zh pairs where they differ (zh already translated/hallucinated).
rows = requests.post(f"https://api.supabase.com/v1/projects/{ref}/database/query", headers=H_MGMT, json={"query":
    "select z.doc_slug, z.order_index, e.text en, z.text zh "
    "from gnostic_sections z join gnostic_sections e "
    "on e.doc_slug=z.doc_slug and e.order_index=z.order_index and e.version_code='gnosis_en' "
    "where z.version_code='zh'"}).json()

fixed = 0
for r in rows:
    if is_trivial_source(r["en"]) and r["zh"] != r["en"]:
        pr = requests.patch(
            f"{URL}/rest/v1/gnostic_sections?doc_slug=eq.{r['doc_slug']}&version_code=eq.zh&order_index=eq.{r['order_index']}",
            headers=H_REST, data=json.dumps({"text": r["en"], "char_count": len(r["en"])}), timeout=60)
        if pr.status_code in (200, 204):
            fixed += 1
            if fixed <= 12:
                print(f"  {r['doc_slug']}#{r['order_index']}: {r['en'][:24]!r} (was {r['zh'][:30]!r})", flush=True)
print(f"reverted {fixed} trivial-source sections to verbatim")
