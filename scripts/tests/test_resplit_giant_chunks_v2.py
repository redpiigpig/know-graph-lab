"""巨型 chunk 二次切分 v2 — resplit_giant_chunks_v2 的純函式。

超過 GIANT_THRESHOLD（40 萬字）的 chunk，依序試 md h2/h3、Book N、Chapter N、
中文 第N章 等 line-anchored 標記切開，並遞迴處理仍超標的子塊。

⚠️ 專案鐵則：任何重整流程都必須原樣保留 chunk.page_number（不可重編、不可遺失）。
   v2 用 `dict(chunk)` 複製整個 chunk，理應一併帶走 page_number — 這支測試把這條
   不變量鎖進測試套件。
"""
import resplit_giant_chunks_v2 as rs


T = rs.GIANT_THRESHOLD  # 400_000


def _pad(n):
    """產生 n 個非標題、非 line-start-marker 的填充字（句號連寫，不觸發任何 pattern）。"""
    return "內文填充" * n


def giant_with_chinese_sections(parts=4, pad_each=40_000):
    """造一個超過門檻、含 >=3 個中文「第N章」line-start 標記的內容。"""
    nums = "一二三四五六七八九"
    blocks = []
    for i in range(parts):
        # 第N章 開頭必須在行首，後接 CJK；再墊大量內文把整塊推過門檻。
        blocks.append(f"第{nums[i]}章 標題{i}\n{_pad(pad_each)}")
    return "\n\n".join(blocks)


class TestFirstHeadingText:
    def test_markdown_heading_wins(self):
        assert rs.first_heading_text("## 第一卷 開端\n\n正文") == "第一卷 開端"

    def test_inline_chinese_section_captured(self):
        out = rs.first_heading_text("一些前言\n第三章 論信德\n更多內文")
        assert out is not None
        assert "第三章" in out

    def test_inline_chapter_roman_captured(self):
        out = rs.first_heading_text("intro prose\nChapter IV. On Faith\nbody text")
        assert out is not None
        assert out.startswith("Chapter IV")

    def test_no_heading_returns_none(self):
        assert rs.first_heading_text("純粹一段沒有任何標題標記的內文文字。") is None


class TestResplitChunkV2:
    def test_below_threshold_not_split(self):
        chunk = {"content": "## 章一\n短內容\n## 章二\n短內容", "chunk_index": 0}
        sub, method = rs.resplit_chunk_v2(chunk)
        assert sub is None
        assert method is None

    def test_chinese_sections_split_into_multiple(self):
        chunk = {"content": giant_with_chinese_sections(parts=4),
                 "chunk_index": 0, "page_number": 12, "chapter_path": "卷甲"}
        sub, method = rs.resplit_chunk_v2(chunk)
        assert sub is not None
        assert method == "chinese_sec"
        assert len(sub) >= 4
        # 子塊內文總長度 >= 原內文（split_at_offsets 只 rstrip，不丟內容）。
        assert sum(len(s["content"]) for s in sub) >= len(chunk["content"]) - len(sub) * 2

    def test_chapter_path_inherits_base_for_non_leading(self):
        chunk = {"content": giant_with_chinese_sections(parts=3),
                 "chunk_index": 0, "page_number": 5, "chapter_path": "卷甲"}
        sub, _ = rs.resplit_chunk_v2(chunk)
        # 非首段的 chapter_path 應為「卷甲 / <子標題>」形式。
        non_leading = [s for s in sub if s["chapter_path"] and " / " in s["chapter_path"]]
        assert non_leading
        assert all(s["chapter_path"].startswith("卷甲 / ") for s in non_leading)

    def test_page_number_preserved_on_every_subchunk(self):
        # ⚠️ 鐵則不變量：切分後每個子塊都必須帶著原 chunk 的 page_number。
        chunk = {"content": giant_with_chinese_sections(parts=4),
                 "chunk_index": 0, "page_number": 777, "chapter_path": "卷甲"}
        sub, _ = rs.resplit_chunk_v2(chunk)
        assert sub is not None
        assert all(s.get("page_number") == 777 for s in sub), \
            "resplit 不可遺失或重編 page_number"


class TestResplitRecursively:
    def test_unsplittable_returns_self(self):
        # 超過門檻但無任何切分標記 → 原樣回傳自己。
        chunk = {"content": _pad(120_000), "chunk_index": 0, "page_number": 3}
        stats = {}
        out = rs.resplit_recursively(chunk, stats)
        assert out == [chunk]
        assert out[0] is chunk

    def test_recursive_split_flattens_and_keeps_page_number(self):
        chunk = {"content": giant_with_chinese_sections(parts=5),
                 "chunk_index": 0, "page_number": 42, "chapter_path": "卷甲"}
        stats = {}
        out = rs.resplit_recursively(chunk, stats)
        assert len(out) >= 5
        # 遞迴攤平後，每個子塊仍保留原 page_number（鐵則）。
        assert all(s.get("page_number") == 42 for s in out)
        assert stats.get("chinese_sec", 0) >= 1
