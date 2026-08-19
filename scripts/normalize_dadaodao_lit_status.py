"""Make full-text status agree with the section rows actually stored."""
from __future__ import annotations

from collections import Counter

from ingest_lit_review import rest_get, rest_patch


PROJECT = "mahaprajapati-revolution"


def main() -> None:
    entries = rest_get(
        "lit_review_entries",
        f"project_slug=eq.{PROJECT}&select=id,ref_key,fulltext_url,fulltext_status&order=id",
    )

    sections: list[dict] = []
    page_size = 1000
    ids = ",".join(str(row["id"]) for row in entries)
    while True:
        batch = rest_get(
            "lit_review_sections",
            f"entry_id=in.({ids})&select=id,entry_id,version_code&order=id&limit={page_size}&offset={len(sections)}",
        )
        sections.extend(batch)
        if len(batch) < page_size:
            break
    counts = Counter((row["entry_id"], row["version_code"]) for row in sections)

    for entry in entries:
        orig = counts[(entry["id"], "orig")]
        zh = counts[(entry["id"], "zh")]
        if orig and orig == zh:
            desired = "translated"
        elif orig:
            desired = "fetched"
        elif entry["ref_key"] == "center-for-religion-and-civic-culture-usc-chao-hwei-shih-buddhist-nun-leads-asia-s-fight-for-gay":
            desired = "unavailable"
        elif entry["fulltext_status"] in {"translated", "fetched"}:
            desired = "pending" if entry.get("fulltext_url") else "unavailable"
        else:
            desired = entry["fulltext_status"]
        if desired != entry["fulltext_status"]:
            rest_patch("lit_review_entries", f"id=eq.{entry['id']}", {"fulltext_status": desired})
            print(f"{entry['ref_key']}: {entry['fulltext_status']} -> {desired} ({orig}/{zh})")


if __name__ == "__main__":
    main()
