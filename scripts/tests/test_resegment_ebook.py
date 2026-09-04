"""重分段：把「整本擠成一塊」的書切成可讀單位。

standardize 的邏輯是合併，對碎片有效、對巨塊幫倒忙（實測有一本最大塊從
985,174 字被合成 2,462,851 字）。這一支只切不合併，並且守住兩條線：
page_number 不可重編、不可切進段落中間。
"""
import resegment_ebook as R


class TestSplitSections:
    def test_no_heading_is_one_section(self):
        assert R.split_sections("just body text") == [(None, "just body text")]

    def test_heading_becomes_the_section_title(self):
        secs = R.split_sections("## 第一章\n\n內文甲\n\n## 第二章\n\n內文乙")
        assert [s[0] for s in secs] == ["第一章", "第二章"]
        assert "內文甲" in secs[0][1] and "內文乙" in secs[1][1]

    def test_text_before_the_first_heading_is_kept(self):
        secs = R.split_sections("前言未標題\n\n## 第一章\n\n內文")
        assert secs[0][0] is None
        assert "前言未標題" in secs[0][1]


class TestPackParagraphs:
    def test_never_splits_inside_a_paragraph(self):
        paras = ["段落" + str(i) + "。" * 400 for i in range(6)]
        pieces = R.pack_paragraphs("\n\n".join(paras), target=1000)
        # 每個原段落都必須完整出現在某一片裡
        joined = "\n\n".join(pieces)
        for p in paras:
            assert p in joined

    def test_pieces_stay_near_target(self):
        text = "\n\n".join("句" * 300 for _ in range(20))
        pieces = R.pack_paragraphs(text, target=1000)
        assert len(pieces) > 1
        assert max(len(p) for p in pieces) < 2500

    def test_oversized_single_paragraph_is_hard_split_at_sentence_ends(self):
        para = "這是一句話。" * 3000            # 一段一萬八千字、沒有空行
        pieces = R.pack_paragraphs(para, target=1000, max_piece=2000)
        assert max(len(p) for p in pieces) <= 2000
        # 切點落在句號之後，不會把「這是一句話」腰斬
        assert all(p.endswith("。") or p == pieces[-1] for p in pieces)

    def test_empty_input_returns_the_original(self):
        assert R.pack_paragraphs("x") == ["x"]


class TestResegment:
    def _chunk(self, content, **kw):
        base = {"chunk_index": 0, "chunk_type": "chapter", "page_number": None,
                "chapter_path": "致謝", "volume": None, "format": "markdown",
                "content": content}
        base.update(kw)
        return base

    def test_small_chunks_are_left_alone(self):
        cs = [self._chunk("短的"), self._chunk("也很短")]
        out = R.resegment(cs, giant=1000)
        assert len(out) == 2
        assert [c["content"] for c in out] == ["短的", "也很短"]

    def test_giant_chunk_is_split(self):
        cs = [self._chunk("\n\n".join("段" * 200 for _ in range(50)))]
        out = R.resegment(cs, giant=1000, target=1000)
        assert len(out) > 5
        assert max(len(c["content"]) for c in out) < 3000

    def test_page_number_is_copied_never_renumbered(self):
        # 🚨 逐頁 PDF 的頁碼是神聖的：切出來的每一片都必須帶著同一個 page_number
        big = "\n\n".join("段" * 200 for _ in range(50))
        cs = [self._chunk(big, page_number=137)]
        out = R.resegment(cs, giant=1000, target=1000)
        assert len(out) > 1
        assert all(c["page_number"] == 137 for c in out)

    def test_chunk_index_is_resequenced_without_gaps(self):
        cs = [self._chunk("短"), self._chunk("\n\n".join("段" * 200 for _ in range(20)))]
        out = R.resegment(cs, giant=1000, target=1000)
        assert [c["chunk_index"] for c in out] == list(range(len(out)))

    def test_headings_become_chapter_path(self):
        body = "## 第一章\n\n" + "甲" * 3000 + "\n\n## 第二章\n\n" + "乙" * 3000
        out = R.resegment([self._chunk(body)], giant=1000, target=5000)
        paths = {c["chapter_path"] for c in out}
        assert paths == {"第一章", "第二章"}

    def test_source_chapter_path_survives_when_there_is_no_heading(self):
        out = R.resegment([self._chunk("無標題" * 2000, chapter_path="致謝")],
                          giant=1000, target=1000)
        assert all(c["chapter_path"] == "致謝" for c in out)

    def test_no_content_is_lost(self):
        body = "\n\n".join(f"段落{i}內容" for i in range(200))
        out = R.resegment([self._chunk(body)], giant=100, target=200)
        joined = "".join(c["content"] for c in out)
        for i in range(200):
            assert f"段落{i}內容" in joined
