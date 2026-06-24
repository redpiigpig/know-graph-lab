# Source Catalog Quality Audit

Snapshot: 2026-06-24

## Progress

- Expanded seed: `seed-records-expanded.json`
- Candidate records harvested: 267
- Classified unique records: 181
- Loop status: paused for prompt tightening after quality audit

## Classification Distribution

- `keep_primary_work`: 28
- `drop_secondary_study`: 114
- `drop_catalog_or_edition`: 15
- `needs_manual_review`: 22
- legacy invalid `reject`: 1

## Engine Distribution

- `nvidia`: 127
- `ollama+nvidia_review`: 20
- `gemini`: 15
- `none`: 16
- `ollama`: 2
- `ollama+gemini_review`: 1

## Quality Assessment

This ledger is useful for triage, but it is not insertion-ready.

Observed issues:

- Some records use edition/print date instead of the original work's composition era.
- Some `zheng/wai` classifications are overconfident and must be manually reviewed.
- Some Chinese titles are Simplified or rough literal titles rather than normalized Taiwan Traditional Chinese.
- Some SRU/MARC records parsed with blank titles and should be handled by source parsing review.
- One old row has an invalid `decision=reject`; schema validation now blocks this for new rows.
- Some edition, translation, or mixed catalogue records should be retained only as witnesses, not as primary works.

## Current Policy

Do not auto-insert from `classified-records.jsonl`.

Before insertion:

1. Filter `decision=keep_primary_work`.
2. Re-check `title_orig` and normalize `title_zh` in Traditional Chinese.
3. Reclassify by original composition era, not holding/edition date.
4. Set `canon=unknown` whenever zheng/wai depends on editorial judgment.
5. Deduplicate against the entire Dazangjing corpus using semantic `title_orig` + `title_zh`.
6. Preserve manuscript/edition records as source witnesses, not as works, unless the record uniquely identifies a primary text.

Prompt was tightened after this audit in `scripts/dazangjing_catalog_ai.py`.
