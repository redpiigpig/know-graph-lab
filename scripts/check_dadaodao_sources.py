"""Read-only audit of foreign-language literature coverage for the book project."""
from __future__ import annotations

from collections import Counter
import json
import os
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def load_env(path: Path) -> None:
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def rest_get(path: str, params: dict[str, str]) -> list[dict]:
    root = Path(__file__).resolve().parent.parent
    load_env(root / ".env")
    base = os.environ["SUPABASE_URL"].rstrip("/")
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    query = urlencode(params)
    req = Request(
        f"{base}/rest/v1/{path}?{query}",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
    )
    with urlopen(req, timeout=60) as response:
        return json.load(response)


def main() -> None:
    rows = rest_get(
        "lit_review_entries",
        {
            "project_slug": "eq.mahaprajapati-revolution",
            "select": "id,ref_key,title,language,fulltext_status,fulltext_url,theme",
            "order": "display_order.asc",
        },
    )
    sections: list[dict] = []
    page_size = 1000
    while True:
        batch = rest_get(
            "lit_review_sections",
            {
                "entry_id": "in.(" + ",".join(str(row["id"]) for row in rows) + ")",
                "select": "entry_id,version_code",
                "order": "id.asc",
                "limit": str(page_size),
                "offset": str(len(sections)),
            },
        )
        sections.extend(batch)
        if len(batch) < page_size:
            break
    section_counts = Counter((section["entry_id"], section["version_code"]) for section in sections)
    foreign = [row for row in rows if row["language"] != "zh"]
    print(f"TOTAL\t{len(rows)}")
    print(f"STATUS\t{dict(Counter(row['fulltext_status'] for row in rows))}")
    print(f"FOREIGN\t{len(foreign)}")
    print(f"FOREIGN_STATUS\t{dict(Counter(row['fulltext_status'] for row in foreign))}")
    for row in foreign:
        print(
            "\t".join(
                [
                    row["language"],
                    row["fulltext_status"],
                    row["ref_key"],
                    row["title"],
                    str(section_counts[(row["id"], "orig")]),
                    str(section_counts[(row["id"], "zh")]),
                    row.get("fulltext_url") or "",
                ]
            )
        )


if __name__ == "__main__":
    main()
