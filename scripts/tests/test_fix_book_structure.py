"""結構修復工程 — fix_book_structure 的純函式。

NO_TOC PDF 在 OCR 後逐頁分塊，需要：先機械剝除頁碼／固定頁眉(detect_header)，
再把逐頁首行濃縮成 skeleton 給 LLM 推目錄(infer_toc)，最後把 LLM/OCR 標題清乾淨
(clean_title)。這些都是「補目錄」前的純文字啟發式，無網路／DB／LLM。
"""
import fix_book_structure as fb


def page(content, page_number=None, chunk_index=0, chunk_type="page"):
    """造一個最小的 page chunk（pipeline 的 dict 形狀）。"""
    c = {"content": content, "chunk_index": chunk_index, "chunk_type": chunk_type}
    if page_number is not None:
        c["page_number"] = page_number
    return c


class TestStripPagenum:
    def test_leading_arabic_and_roman_stripped(self):
        assert fb.strip_leading_pagenum("12\n正文開始") == "正文開始"
        assert fb.strip_leading_pagenum("iv\n序言") == "序言"

    def test_trailing_pagenum_stripped(self):
        assert fb.strip_trailing_pagenum("正文結束\n88") == "正文結束"

    def test_non_pagenum_line_untouched(self):
        # 首行不是純頁碼 → 原樣保留。
        assert fb.strip_leading_pagenum("第一章 開端\n88") == "第一章 開端\n88"


class TestCleanTitle:
    def test_dotted_leaders_and_trailing_pagenum_dropped(self):
        # 目錄點點點 + 尾端頁碼「（101）」要清掉。
        assert fb.clean_title("第一章 緒論……………（101）") == "第一章 緒論"

    def test_english_meta_note_dropped(self):
        # 「(Family tree diagram)」這類說明性英文要拿掉。
        assert fb.clean_title("族譜 (Family tree diagram here)") == "族譜"

    def test_body_overflow_cut_at_sentence_end(self):
        # 超過 32 字的標題在句號處截斷（避免吞進整段內文）。
        long = "第一章導論在這一段冗長的描述裡面我們將會詳細討論許多事情。後面還有更多內容繼續延伸下去"
        out = fb.clean_title(long)
        assert out.endswith("。")
        assert len(out) <= 33


class TestLevelFromTitle:
    def test_part_is_level1(self):
        assert fb.level_from_title("第一部", fallback=2) == 1

    def test_chapter_is_level2(self):
        assert fb.level_from_title("第三章", fallback=1) == 2

    def test_unknown_uses_fallback(self):
        assert fb.level_from_title("沒有任何層級線索的標題", fallback=3) == 3


class TestDetectHeader:
    def test_constant_furniture_header_detected(self):
        # 每頁開頭都重複「世界宗教史」這個頁眉，>=30% 覆蓋 → 偵測為固定頁眉。
        pages = [page(f"世界宗教史 第{i}頁的正文內容在這裡延展開來。") for i in range(10)]
        header, cov, is_const = fb.detect_header(pages)
        assert header is not None
        assert "世界宗教史" in header
        assert cov >= 0.30

    def test_no_shared_prefix_returns_none(self):
        # 每頁開頭都不同（共 10 頁，無任何 4 字前綴達 30%）→ 不應誤判頁眉。
        # 註：30% 門檻是為大書設計的；頁數太少時單次出現就會過門檻，故用 10 頁。
        starts = "甲乙丙丁戊己庚辛壬癸"
        pages = [page(f"{ch}起首這裡是第{i}頁獨有的開頭文字內容。", page_number=i)
                 for i, ch in enumerate(starts)]
        header, cov, is_const = fb.detect_header(pages)
        assert header is None
        assert cov == 0.0


class TestBuildSkeleton:
    def test_skeleton_uses_page_number_and_first_line(self):
        pages = [page("第一章 開端的正文", page_number=5),
                 page("第二章 後續的正文", page_number=9)]
        sk = fb.build_skeleton(pages, header=None)
        lines = sk.split("\n")
        assert lines[0].startswith("p5│")
        assert "第一章 開端" in lines[0]
        assert lines[1].startswith("p9│")

    def test_skeleton_strips_header_prefix(self):
        header = "世界宗教史"
        pages = [page(f"{header} 第一章 開端", page_number=3)]
        sk = fb.build_skeleton(pages, header=header)
        # 頁眉被剝掉，只剩章節文字。
        assert header not in sk.split("│", 1)[1]
        assert "第一章 開端" in sk

    def test_rich_skeleton_surfaces_midpage_heading(self):
        # 首行非標題，但內文中段有「第二節」候選 → rich 版要用 ⟦⟧ 標出。
        body = "這是一段引言文字。\n\n第二節 論信德\n\n更多內文。"
        pages = [page(body, page_number=7)]
        sk = fb.build_skeleton_rich(pages, header=None)
        assert "⟦" in sk and "第二節" in sk
