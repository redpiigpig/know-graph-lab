"""Focused regression tests for the Greek collected-works driver."""

import plato_build as pb
import pytest


def test_auto_engine_is_supported(monkeypatch, tmp_path):
    monkeypatch.setattr(pb, "CACHE", tmp_path)

    translate = pb.make_translate_fn("auto", "apology")

    assert callable(translate)
    assert (tmp_path / "apology_zh").is_dir()


# run() 讀 WORKS 條目時一定會用到的欄位。少一個就會在抓完 XML 之後才 KeyError，
# 而不是在檢查「有沒有可對齊的單位」時給出看得懂的訊息。
REQUIRED_WORK_KEYS = ("slug", "author", "title_zh", "anchor", "eng_anchor")


def test_run_rejects_a_work_with_no_aligned_units(monkeypatch):
    # 🚨 fixture 要帶齊 REQUIRED_WORK_KEYS。原本少了 eng_anchor（那是後來才加進
    #    run() 的欄位，測試沒跟上），於是 run() 在跑到空對照檢查之前就先 KeyError，
    #    把這條測試真正要驗的 RuntimeError 蓋掉——測試紅了，但紅的理由是錯的。
    monkeypatch.setitem(pb.WORKS, "empty-work", {
        "slug": "empty-work",
        "author": "柏拉圖",
        "title_zh": "空白測試",
        "anchor": "section",
        "eng_anchor": "section",
    })
    monkeypatch.setattr(pb, "fetch", lambda _slug: ("<body/>", "<body/>"))

    with pytest.raises(RuntimeError, match="避免把空白封面誤標為完成"):
        pb.run("empty-work")


def test_every_work_has_the_keys_run_needs():
    # 新增一篇對話錄時漏掉欄位，錯誤會等到 fetch 完才炸——那時已經打過網路了，
    # 而訊息只有一個 KeyError。在這裡先擋住
    missing = {slug: [k for k in REQUIRED_WORK_KEYS if k not in d]
               for slug, d in pb.WORKS.items()}
    assert {s: m for s, m in missing.items() if m} == {}
