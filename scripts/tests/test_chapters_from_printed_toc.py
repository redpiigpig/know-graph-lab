# -*- coding: utf-8 -*-
"""書前印刷目錄補章節（乾跑）的純函式測試。

覆蓋：目錄頁自動偵測（抬頭字樣＋跨頁續頁）、條目定位（錨點推算／內文搜尋兩條路
都要過驗證閘）、位移單調性過濾、覆蓋率門檻。跟 toc_from_toc_pages 共用的部分
（parse_toc_lines／resolve_page／verify）已有 test_hongshi_toc.py 覆蓋，這裡只測
本檔新加的三件事。
"""
import chapters_from_printed_toc as ct  # noqa: E402


def page(n, content, printed_page=None):
    c = {"chunk_index": n, "chunk_type": "page", "page_number": n, "content": content,
         "chapter_path": None}
    if printed_page is not None:
        c["printed_page"] = printed_page
    return c


class TestIsTocHeaderPage:
    def test_chinese_variants(self):
        assert ct.is_toc_header_page("目錄\n\n第一章 緒論 1")
        assert ct.is_toc_header_page("目　次\n序 1")

    def test_english(self):
        assert ct.is_toc_header_page("CONTENTS\nPreface xi")
        assert ct.is_toc_header_page("Table of Contents")

    def test_body_page_is_not_header(self):
        assert not ct.is_toc_header_page("第一章 緒論\n\n本章討論的是……")


class TestTocEntryRatio:
    def test_dense_entries_page(self):
        text = "第一章 緒論 1\n第二章 方法 12\n第三章 結論 30\n"
        assert ct.toc_entry_ratio(text) == 1.0

    def test_prose_page_low_ratio(self):
        text = "這是正文的第一段，講的是一件很長的事情，沒有任何頁碼條目。\n第二段接著講下去。"
        assert ct.toc_entry_ratio(text) < 0.3

    def test_empty_page(self):
        assert ct.toc_entry_ratio("") == 0.0


class TestFindTocPageRange:
    def test_single_toc_page(self):
        pages = [page(1, "書名頁")] + [page(2, "目錄\n第一章 緒論 1\n第二章 方法 12")] + \
                [page(i, f"第{i}頁正文，內容很長不是目錄條目而已。") for i in range(3, 20)]
        assert ct.find_toc_page_range(pages) == [2]

    def test_multi_page_toc_continuation(self):
        pages = ([page(1, "書名頁")] +
                 [page(2, "目錄\n第一章 緒論 1\n第二章 方法 12")] +
                 [page(3, "第三章 分析 30\n第四章 結論 55")] +
                 [page(i, f"第{i}頁正文內容一大段，完全不是條目格式。") for i in range(4, 20)])
        assert ct.find_toc_page_range(pages) == [2, 3]

    def test_no_toc_header_returns_none(self):
        pages = [page(i, f"第{i}頁正文，沒有標題字樣。") for i in range(1, 20)]
        assert ct.find_toc_page_range(pages) is None

    def test_toc_beyond_front_window_not_found(self):
        # 目錄抬頭出現在第 40 頁，遠超過前 8%／至少 15 頁的搜尋窗，不該被抓到。
        pages = [page(i, f"第{i}頁正文，沒有標題字樣。") for i in range(1, 40)] + \
                [page(40, "目錄\n第一章 緒論 41")] + \
                [page(i, f"第{i}頁正文") for i in range(41, 300)]
        assert ct.find_toc_page_range(pages) is None


class TestResolveEntries:
    def test_anchor_path_used_when_printed_page_matches(self):
        by_page = {
            2: page(2, "目錄"),
            10: page(10, "3", printed_page=3),    # 錨點：pdf 10 = 印刷 3
            16: page(16, "9", printed_page=9),    # 錨點：pdf 16 = 印刷 9（離目標印刷頁 8 較近）
            15: page(15, "第一章 緒論\n本章開始。"),
        }
        entries = [{"title": "第一章 緒論", "printed_page": 8, "level": 1}]
        anchors = [(10, 3), (16, 9)]
        resolved, dropped = ct.resolve_entries(entries, anchors, by_page, {2})
        assert not dropped
        assert resolved[0]["pdf_page"] == 15 and resolved[0]["how"] == "anchor"

    def test_content_search_fallback_when_no_anchor(self):
        by_page = {
            2: page(2, "目錄"),
            3: page(3, "封面"),
            9: page(9, "第一章 緒論\n本章開始。"),
        }
        entries = [{"title": "第一章 緒論", "printed_page": 5, "level": 1}]
        resolved, dropped = ct.resolve_entries(entries, [], by_page, {2})
        assert not dropped
        assert resolved[0]["pdf_page"] == 9 and resolved[0]["how"] == "content-search"

    def test_unfindable_title_is_dropped(self):
        by_page = {2: page(2, "目錄"), 9: page(9, "跟標題完全無關的內容")}
        entries = [{"title": "第九章 從缺", "printed_page": 5, "level": 1}]
        resolved, dropped = ct.resolve_entries(entries, [], by_page, {2})
        assert not resolved and dropped == entries


class TestEnforceMonotonic:
    def test_keeps_increasing_sequence(self):
        resolved = [{"pdf_page": 5}, {"pdf_page": 12}, {"pdf_page": 30}]
        kept, dropped = ct.enforce_monotonic(resolved)
        assert kept == resolved and not dropped

    def test_drops_big_backward_jump(self):
        resolved = [{"pdf_page": 5}, {"pdf_page": 200}, {"pdf_page": 12}]
        kept, dropped = ct.enforce_monotonic(resolved)
        assert [e["pdf_page"] for e in kept] == [5, 200]
        assert dropped == [{"pdf_page": 12}]

    def test_small_jitter_within_tolerance_kept(self):
        resolved = [{"pdf_page": 10}, {"pdf_page": 12}, {"pdf_page": 11}]
        kept, dropped = ct.enforce_monotonic(resolved, tolerance=3)
        assert kept == resolved and not dropped


class TestProcessBook:
    def _book(self, n_pages=30):
        chunks = [page(1, "書名頁"),
                  page(2, "目錄\n第一章 緒論 1\n第二章 方法 3\n第三章 結論 5")]
        chunks.append(page(3, "第一章 緒論\n" + "本章內容。" * 20, printed_page=1))
        chunks.append(page(4, "還在第一章裡繼續講。" * 20, printed_page=2))
        chunks.append(page(5, "第二章 方法\n" + "方法內容。" * 20, printed_page=3))
        chunks.append(page(6, "第三章 結論\n" + "結論內容。" * 20, printed_page=4))
        for i in range(7, n_pages + 1):
            chunks.append(page(i, "後面還有很多正文頁。" * 20, printed_page=i - 2))
        return chunks

    def test_ok_book_gets_merged_and_covered(self):
        res = ct.process_book("test-book", self._book())
        assert res["status"] == "ok"
        assert res["entries_parsed"] == 3
        assert res["entries_resolved"] == 3
        assert res["coverage_pct"] > 0.5
        assert res["merged_chunks"] is not None and res["merged_chunks"] <= res["orig_chunks"]

    def test_too_short_book(self):
        res = ct.process_book("tiny", [page(1, "只有一頁")])
        assert res["status"] == "too-short"

    def test_no_toc_page_found(self):
        chunks = [page(i, "完全沒有標題字樣的正文" * 5) for i in range(1, 20)]
        res = ct.process_book("no-toc", chunks)
        assert res["status"] == "no-toc-page-found"

    def test_duplicate_anchors_rejected_even_with_high_nominal_coverage(self):
        # 《以西結書註釋》真實案例的縮影：目次一堆條目，但每條都被 content-search
        # 誤配到同一個封面頁 —— coverage 算出來會很高，但那是假的，要在這一關擋下。
        chunks = [page(1, "封面標題重複句"),
                  page(2, "目錄\n封面標題重複句 1\n封面標題重複句 2\n封面標題重複句 3\n封面標題重複句 4")]
        for i in range(3, 20):
            chunks.append(page(i, "跟目次條目對不上的正文內容，沒有那句重複標題。"))
        res = ct.process_book("dup-anchor", chunks)
        assert res["status"].startswith("duplicate-anchors")

    def test_too_few_resolved_even_if_parsed_enough(self):
        chunks = [page(1, "書名頁"),
                  page(2, "目錄\n甲章 找得到 1\n乙章 找不到 2\n丙章 也找不到 3")]
        chunks.append(page(3, "甲章 找得到\n" + "內容。" * 20))
        for i in range(4, 20):
            chunks.append(page(i, "後面都是些跟目錄條目對不上的正文。" * 5))
        res = ct.process_book("few-resolved", chunks)
        assert res["status"].startswith("too-few-resolved")
