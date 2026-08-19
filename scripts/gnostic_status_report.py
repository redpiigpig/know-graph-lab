"""Print a compact status report for the Gnostic Library DB."""
from __future__ import annotations

import io
import json
import os
import sys

import requests
from dotenv import load_dotenv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
PROJECT_REF = SUPABASE_URL.split("//")[1].split(".")[0]
MGMT_QUERY = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"
HEADERS = {
    "Authorization": f"Bearer {os.environ['SUPABASE_ACCESS_TOKEN']}",
    "Content-Type": "application/json",
}


def query(sql: str):
    res = requests.post(MGMT_QUERY, headers=HEADERS, json={"query": sql}, timeout=120)
    res.raise_for_status()
    return res.json()


summary_sql = """
SELECT
  (SELECT count(*) FROM gnostic_documents) AS docs,
  (SELECT count(*) FROM gnostic_documents WHERE apocrypha_slug IS NOT NULL) AS linked_apocrypha,
  (SELECT count(*) FROM gnostic_sections WHERE version_code='gnosis_en') AS en_sections,
  (SELECT count(*) FROM gnostic_sections WHERE version_code='zh') AS zh_sections,
  (
    SELECT count(*)
    FROM gnostic_sections e
    JOIN gnostic_sections z
      ON z.doc_slug=e.doc_slug
     AND z.order_index=e.order_index
     AND z.version_code='zh'
    WHERE e.version_code='gnosis_en'
  ) AS aligned_pairs;
"""

category_sql = """
SELECT d.category,
       count(DISTINCT d.slug) AS docs,
       count(e.id) AS en_sections,
       count(z.id) AS zh_sections
FROM gnostic_documents d
LEFT JOIN gnostic_sections e
  ON e.doc_slug=d.slug
 AND e.version_code='gnosis_en'
LEFT JOIN gnostic_sections z
  ON z.doc_slug=d.slug
 AND z.version_code='zh'
 AND z.order_index=e.order_index
GROUP BY d.category
ORDER BY d.category;
"""

print(json.dumps({"summary": query(summary_sql), "categories": query(category_sql)}, ensure_ascii=False, indent=2))
