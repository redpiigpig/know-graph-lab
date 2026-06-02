"""Translation — oversized source splitting (split_oversized).

Big EPUB source chunks (>20K chars) get split on paragraph breaks before
translation, then re-joined. A split that loses or reorders paragraphs
silently breaks the 逐段對照 alignment downstream, so the invariant under
test is: splitting then re-joining reconstructs the original paragraph
sequence exactly.
"""
import translate_ebook_to_zh as t


def test_short_input_returned_whole():
    src = "短文。\n\n第二段。"
    assert t.split_oversized(src, max_chars=1000) == [src]


def test_split_produces_multiple_pieces():
    paras = [f"段落{i}：" + "字" * 50 for i in range(40)]
    src = "\n\n".join(paras)
    pieces = t.split_oversized(src, max_chars=500)
    assert len(pieces) > 1


def test_no_content_loss_round_trips():
    paras = [f"段落{i}：" + "內容" * 30 for i in range(60)]
    src = "\n\n".join(paras)
    pieces = t.split_oversized(src, max_chars=400)
    # Re-joining the pieces must reproduce the original paragraph sequence.
    assert "\n\n".join(pieces) == src


def test_paragraph_count_preserved():
    paras = [f"P{i}" + "x" * 100 for i in range(30)]
    src = "\n\n".join(paras)
    pieces = t.split_oversized(src, max_chars=350)
    total = sum(p.count("\n\n") + 1 for p in pieces)
    assert total == len(paras)


def test_single_oversized_paragraph_not_dropped():
    # One paragraph larger than max_chars can't be split further — it must
    # still come back as its own piece, not be discarded.
    src = "字" * 5000
    pieces = t.split_oversized(src, max_chars=1000)
    assert "".join(pieces) == src
    assert len(pieces) == 1
