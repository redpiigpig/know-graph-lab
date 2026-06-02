"""Translation pain point #2 — 逐段對照 (bilingual paragraph alignment).

The reader's 中英對照 mode pairs paragraphs row-by-row, so source_text (EN)
and content (ZH) must keep matching paragraph structure. paragraph_drift()
(extracted from scan_translated_book's T11 gate) is the metric; these tests
lock its behavior and act as the contract for a post-translation alignment
gate.
"""
import scan_translated_book as scan


class TestParaCount:
    def test_counts_blank_line_delimited_blocks(self):
        assert scan.para_count("A\n\nB\n\nC") == 3

    def test_ignores_empty_blocks(self):
        assert scan.para_count("A\n\n\n\nB\n\n   \n\n") == 2

    def test_empty_string(self):
        assert scan.para_count("") == 0
        assert scan.para_count(None) == 0


class TestParagraphDrift:
    def test_perfectly_aligned_is_zero(self):
        zh = "\n\n".join(f"中{i}" for i in range(8))
        en = "\n\n".join(f"en{i}" for i in range(8))
        assert scan.paragraph_drift(zh, en) == 0.0

    def test_short_text_returns_none(self):
        # < 4 paragraphs either side → unmeasurable.
        assert scan.paragraph_drift("A\n\nB", "x\n\ny\n\nz\n\nw\n\nv") is None

    def test_misalignment_detected(self):
        # 8 ZH paragraphs vs 4 EN paragraphs → 50% drift (LLM merged paras).
        zh = "\n\n".join(f"中{i}" for i in range(8))
        en = "\n\n".join(f"en{i}" for i in range(4))
        drift = scan.paragraph_drift(zh, en)
        assert drift == 0.5
        assert drift > scan.BILINGUAL_DRIFT_RATIO

    def test_small_drift_within_tolerance(self):
        # 10 vs 9 → 10% drift, under the 25% gate.
        zh = "\n\n".join(f"中{i}" for i in range(10))
        en = "\n\n".join(f"en{i}" for i in range(9))
        drift = scan.paragraph_drift(zh, en)
        assert drift is not None
        assert drift <= scan.BILINGUAL_DRIFT_RATIO


class TestAlignmentGate:
    """The reusable 逐段對照 re-translation worklist."""

    def _chunk(self, idx, n_zh, n_en, path="第一章"):
        return {
            "chunk_index": idx,
            "chapter_path": path,
            "content": "\n\n".join(f"中{i}" for i in range(n_zh)),
            "source_text": "\n\n".join(f"en{i}" for i in range(n_en)),
        }

    def test_flags_only_drifting_chunks(self):
        chunks = [
            self._chunk(0, 8, 8),    # aligned
            self._chunk(1, 12, 5),   # 58% drift → flagged
            self._chunk(2, 10, 9),   # 10% drift → ok
        ]
        flagged = scan.alignment_gate(chunks)
        assert [f["chunk_index"] for f in flagged] == [1]
        assert flagged[0]["zh_paras"] == 12 and flagged[0]["en_paras"] == 5

    def test_monolingual_chunks_ignored(self):
        # No source_text (simp→trad book, or a ZH-only chunk) → never flagged.
        chunks = [{"chunk_index": 0, "content": "中\n\n文\n\n段\n\n落\n\n多", "source_text": ""}]
        assert scan.alignment_gate(chunks) == []

    def test_threshold_is_tunable(self):
        chunks = [self._chunk(0, 10, 8)]  # 20% drift
        assert scan.alignment_gate(chunks, threshold=0.25) == []     # under default
        assert len(scan.alignment_gate(chunks, threshold=0.10)) == 1  # over stricter


class TestT11Integration:
    """The drift metric must drive a T11 issue inside the real scan rules."""

    def test_misaligned_chunk_would_flag(self):
        # Simulate what scan() evaluates per chunk.
        chunk = {
            "chunk_index": 3,
            "content": "\n\n".join(f"中文段{i}" for i in range(12)),
            "source_text": "\n\n".join(f"English para {i}" for i in range(5)),
        }
        drift = scan.paragraph_drift(chunk["content"], chunk["source_text"])
        assert drift is not None and drift > scan.BILINGUAL_DRIFT_RATIO
