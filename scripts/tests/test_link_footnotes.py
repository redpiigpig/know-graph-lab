# -*- coding: utf-8 -*-
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import link_footnotes as lf  # noqa: E402


def test_extract_notes_block_rule_style_already_toggled():
    content = ("正文提到[12]這件事，後面又講注13的事。\n\n"
               "———————————————\n\n(12) 這是第十二條註。\n\n(13) 這是第十三條註，"
               "分兩行\n接著寫。")
    info = lf.extract_notes_block(content)
    assert info["kind"] == "rule"
    assert info["entries"] == [(12, "這是第十二條註。"),
                                (13, "這是第十三條註，分兩行\n接著寫。")]
    assert info["body"].startswith("正文提到[12]")


def test_extract_notes_block_heading_no_rule_is_detected_as_broken():
    # denzinger 型：標題後直接接 (N)，中間沒有分隔線 → reader 不會切換進註釋模式。
    content = "正文正文正文。\n\n## 註釋\n\n(1) 註一。\n\n(2) 註二。"
    info = lf.extract_notes_block(content)
    assert info["kind"] == "heading_no_rule"
    assert info["entries"] == [(1, "註一。"), (2, "註二。")]
    assert info["body"].endswith("## 註釋")


def test_extract_notes_block_bracket_style_entries_normalized():
    content = "正文。\n\n———————————————\n\n[5] 用方括號寫的註。"
    info = lf.extract_notes_block(content)
    assert info["kind"] == "rule"
    assert info["entries"] == [(5, "用方括號寫的註。")]


def test_extract_notes_block_multi_region_is_skipped():
    content = ("body1\n\n———————————————\n\n(1) 註一\n\n———————————————\n\n"
               "body2\n\n———————————————\n\n(2) 註二\n\n———————————————\n\nbody3")
    info = lf.extract_notes_block(content)
    assert info["kind"] is None and info["multi_region"] is True


def test_extract_notes_block_no_notes_returns_none():
    info = lf.extract_notes_block("只是普通正文，沒有任何註釋。")
    assert info["kind"] is None and info["entries"] == []


def test_link_explicit_markers_bracket_and_zhu_and_superscript():
    body = "正文講到某事[5]，後面又提到某事注8，再來是上標⁹的例子。"
    out, found = lf.link_explicit_markers(body, [5, 8, 9])
    assert found == [5, 8, 9]
    assert "[^5]" in out and "[^8]" in out and "[^9]" in out
    assert "[5]" not in out and "注8" not in out and "⁹" not in out


def test_link_explicit_markers_does_not_touch_unrelated_numbers():
    body = "1990年發生的事情與[999]這個引用無關。"
    out, found = lf.link_explicit_markers(body, [5])
    assert found == [] and out == body


def test_link_explicit_markers_requires_cjk_or_punct_left_context():
    # 句首方括號常是條列/程式碼，不是註標；左邊沒有中文或標點時不轉。
    body = "[3] 這其實是條列開頭，不是行內註標。"
    out, found = lf.link_explicit_markers(body, [3])
    assert found == [] and out == body


def test_link_footnotes_chunk_full_pipeline_links_body_and_normalizes_bracket_entries():
    content = ("正文提到某事[7]之後結束。\n\n"
               "———————————————\n\n[7] 這是方括號寫的註釋內容。")
    r = lf.link_footnotes_chunk(content)
    assert r["kind"] == "rule" and r["entries"] == 1 and r["linked"] == 1
    assert "[^7]" in r["new_content"]
    assert "(7) 這是方括號寫的註釋內容。" in r["new_content"]
    assert r["changed"] is True


def test_link_footnotes_chunk_inserts_rule_after_heading_no_rule():
    content = "本章正文。\n\n## 註釋\n\n(1) 第一條，正文裡有註1可對。"
    body_with_ref = "本章正文提到註1的地方。\n\n## 註釋\n\n(1) 第一條註。"
    r = lf.link_footnotes_chunk(body_with_ref)
    assert r["kind"] == "heading_no_rule"
    assert lf.FOOT_RULE in r["new_content"]
    # 標題保留在分隔線之前，分隔線在標題與條列之間
    idx_heading = r["new_content"].index("## 註釋")
    idx_rule = r["new_content"].index(lf.FOOT_RULE)
    idx_entry = r["new_content"].index("(1) 第一條註。")
    assert idx_heading < idx_rule < idx_entry
    assert "[^1]" in r["new_content"]


def test_link_footnotes_chunk_credits_already_linked_refs_without_touching_them():
    # 有些書已經跑過一輪，正文早就是 [^N]；regex 認不得 `[^N]` 這個寫法，
    # 不能再拿裸數字／方括號規則去猜，要先算進「已連上」、也不能誤傷它。
    content = ("正文認識[^1]創造天地的神，後面又提到[2]另一件事。\n\n"
               "———————————————\n\n(1) 第一條註。\n\n(2) 第二條註。")
    r = lf.link_footnotes_chunk(content)
    assert r["entries"] == 2 and r["linked"] == 2
    assert r["new_content"].count("[^1]") == 1 and "[^2]" in r["new_content"]


def test_link_footnotes_chunk_reverts_bare_number_false_friend_century():
    # 人工核對 d3dc422b 書時抓到的真實誤判：借用 cp.link_markers 的裸數字啟發式
    # 把「公元1世紀」「18世紀劍橋柏拉圖倫理學派」的「1」「18」也當成註號連走。
    content = ("公元1世紀已經出現的新畢達哥拉斯主義，以及18世紀劍橋柏拉圖倫理學派"
               "都提到這件事。\n\n———————————————\n\n(1) 這是第一條註。\n\n"
               "(18) 這是第十八條註。")
    r = lf.link_footnotes_chunk(content)
    assert "[^1]" not in r["new_content"] and "[^18]" not in r["new_content"]
    assert "1世紀" in r["new_content"] and "18世紀" in r["new_content"]
    assert r["linked"] == 0


def test_link_footnotes_chunk_skips_consolidate_page_chunks_territory():
    # 這種「頁尾分隔線＋裸數字」是 consolidate_page_chunks.split_page 的地盤，
    # 本工具刻意不碰，避免跟另一支正在改同一批檔案的批次程式互相覆蓋。
    content = "正文正文50這件事。\n\n———————————————\n50譯註：這是裸數字頁尾註。"
    r = lf.link_footnotes_chunk(content)
    assert r["kind"] == "page-rule-other-tool"
    assert r["changed"] is False and r["new_content"] == content


def test_eligible_book_skips_bilingual():
    chunks = [{"content": "x", "source_text": "y"}]
    assert lf.eligible_book(chunks) == "bilingual-skip"


def test_eligible_book_ok():
    chunks = [{"content": "x"}]
    assert lf.eligible_book(chunks) == ""
