"""quality_sweep.fetch_chunks 的來源。同一個教訓，換了兩代實作。

**共同的要害：讀不到內容，絕不可以等於「這本書是空的」。**
harvest_signals 對 n==0 會判 blank/no_toc/tiny 全 100%、15 分、掛三個 flag，
而且 sweep 會正常結束、把分數寫回去、exit 0 —— 錯得無聲無息。

前一代（讀 `ebook_chunks`）踩過兩次：
  2026-09-04：`limit=10000` 遇上 PostgREST 的 max-rows 硬上限（1000），
    終止條件 `len(c) < step` 第一頁就成立，255,951 個 chunk 只掃到前 1000 個，
    其餘每一本都 n==0。那份「1,334 本低於 40 分」的評分就是這樣來的。
  2026-09-05：改 OFFSET 分頁後，chunk 從 25.6 萬長到 45.2 萬，
    翻到 offset=272000 開始回 500 —— OFFSET 越深越慢，重試幾次都一樣。

這一代（2026-09-16 起讀 Drive 上的 JSONL；`ebook_chunks` 已退場，
1,005,032 列在 500 MB 的免費層佔掉 503 MB）風險換成**檔案讀不到**：
G: 沒掛的話，每一本都會讀到 0 個 chunk —— 一模一樣的全館誤判。
所以下面每一條測的都是「讀不到要吵，不要默默給 0」。
"""
import json

import pytest

import quality_sweep


def _write_book(tmp_path, bid, chunks):
    p = tmp_path / f"{bid}.jsonl"
    p.write_text("\n".join(json.dumps(c, ensure_ascii=False) for c in chunks) + "\n",
                 encoding="utf-8")
    return p


def test_drive_not_mounted_raises_instead_of_reporting_empty_books(tmp_path, monkeypatch):
    """🚨 最重要的一條：G: 沒掛要當場拋例外，不可以回空桶子。

    回空桶子的話 sweep 會把全館每一本都評成 15 分並覆寫回 DB，
    而且一路綠燈 —— 跟 2026-09-04 那次事故一模一樣，只是換了觸發原因。
    """
    monkeypatch.setattr(quality_sweep, "CHUNKS_DIR", tmp_path / "沒有這個目錄")
    with pytest.raises(RuntimeError) as e:
        quality_sweep.fetch_chunks({}, {"book-a", "book-b"}, use_rest=True)
    assert "Drive" in str(e.value)


def test_every_book_missing_raises_too(tmp_path, monkeypatch):
    """目錄在、但一本都讀不到，同樣是環境問題而不是全館真的空了。"""
    monkeypatch.setattr(quality_sweep, "CHUNKS_DIR", tmp_path)
    with pytest.raises(RuntimeError):
        quality_sweep.fetch_chunks({}, {"book-a", "book-b"}, use_rest=True)


def test_one_missing_book_does_not_sink_the_rest(tmp_path, monkeypatch):
    """單一本沒有 JSONL 是那一本的事，其他書照常評分。"""
    monkeypatch.setattr(quality_sweep, "CHUNKS_DIR", tmp_path)
    _write_book(tmp_path, "book-a", [{"content": "有內容", "chapter_path": "第一章"}])
    got = quality_sweep.fetch_chunks({}, {"book-a", "book-b"}, use_rest=True)
    assert set(got) == {"book-a"}
    assert len(got["book-a"]) == 1


def test_char_count_comes_from_the_full_text_not_a_preview(tmp_path, monkeypatch):
    """char_count 要是全文長度。

    前一代是拿 DB 那份**前 100 字**的 preview 來算的，所以任何一段只要開頭
    像樣就過關；重複幻覺偏偏都藏在段落尾段（見 feedback_ocr_repetition_hallucination）。
    改讀 JSONL 之後看的是整段。
    """
    monkeypatch.setattr(quality_sweep, "CHUNKS_DIR", tmp_path)
    long_text = "字" * 5000
    _write_book(tmp_path, "book-a", [{"content": long_text, "chapter_path": "第一章"}])
    got = quality_sweep.fetch_chunks({}, {"book-a"}, use_rest=True)
    assert got["book-a"][0]["char_count"] == 5000
    assert len(got["book-a"][0]["content"]) == 5000


def test_fields_map_onto_what_harvest_signals_reads(tmp_path, monkeypatch):
    """harvest_signals 讀 char_count／chapter_path／chunk_type，欄位名不能漂。"""
    monkeypatch.setattr(quality_sweep, "CHUNKS_DIR", tmp_path)
    _write_book(tmp_path, "book-a", [
        {"content": "abc", "chapter_path": "序", "chunk_type": "chapter"},
        {"content": "", "chapter_path": None, "chunk_type": "page"},
    ])
    rows = quality_sweep.fetch_chunks({}, {"book-a"}, use_rest=True)["book-a"]
    assert [r["char_count"] for r in rows] == [3, 0]
    assert [r["chapter_path"] for r in rows] == ["序", None]
    assert [r["chunk_type"] for r in rows] == ["chapter", "page"]
    assert all(r["ebook_id"] == "book-a" for r in rows)


def test_a_corrupt_line_is_skipped_not_fatal(tmp_path, monkeypatch):
    """JSONL 裡有一行壞掉不該讓整本（或整場）陣亡。"""
    monkeypatch.setattr(quality_sweep, "CHUNKS_DIR", tmp_path)
    (tmp_path / "book-a.jsonl").write_text(
        json.dumps({"content": "好的"}) + "\n{ 這行壞了\n" + json.dumps({"content": "也好"}) + "\n",
        encoding="utf-8")
    rows = quality_sweep.fetch_chunks({}, {"book-a"}, use_rest=True)["book-a"]
    assert [r["content"] for r in rows] == ["好的", "也好"]
