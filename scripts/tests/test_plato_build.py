"""Focused regression tests for the Greek collected-works driver."""

import plato_build as pb
import pytest


def test_auto_engine_is_supported(monkeypatch, tmp_path):
    monkeypatch.setattr(pb, "CACHE", tmp_path)

    translate = pb.make_translate_fn("auto", "apology")

    assert callable(translate)
    assert (tmp_path / "apology_zh").is_dir()


def test_run_rejects_a_work_with_no_aligned_units(monkeypatch):
    monkeypatch.setitem(pb.WORKS, "empty-work", {
        "slug": "empty-work",
        "author": "柏拉圖",
        "title_zh": "空白測試",
        "anchor": "section",
    })
    monkeypatch.setattr(pb, "fetch", lambda _slug: ("<body/>", "<body/>"))

    with pytest.raises(RuntimeError, match="避免把空白封面誤標為完成"):
        pb.run("empty-work")
