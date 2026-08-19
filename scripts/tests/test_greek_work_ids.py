"""Cross-pipeline identity invariants for the Greek collected works."""

import epicurus_build
import epictetus_build
import plato_build
import plotinus_build


def test_ebook_ids_are_unique_across_greek_pipelines():
    grouped = {
        "plato_aristotle": [work["ebook_id"] for work in plato_build.WORKS.values()],
        "epicurus": [work["ebook_id"] for work in epicurus_build.WORKS.values()],
        "epictetus": [work["ebook_id"] for work in epictetus_build.WORKS.values()],
        "plotinus": [work["ebook_id"] for work in plotinus_build.WORKS.values()],
    }
    ids = [ebook_id for group in grouped.values() for ebook_id in group]

    assert len(ids) == len(set(ids)), grouped
