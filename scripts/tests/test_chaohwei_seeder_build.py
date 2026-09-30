import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from chaohwei_seeder_build import align_note_numbers, section_titles  # noqa: E402


def test_align_note_numbers_follows_body_markers():
    # 頁底圈號印得小，OCR 讀成 ❶；正文是 ❷ → 以正文為準
    text = "說話都是怯生生的。」[^2]\n在功課方面……\n[^1]: 印順法師：《華雨香雲》，頁一四四。"
    assert align_note_numbers(text).endswith("[^2]: 印順法師：《華雨香雲》，頁一四四。")


def test_align_note_numbers_multiple_in_order():
    text = "甲[^7]乙[^8]\n[^1]: 註甲\n[^1]: 註乙"
    assert align_note_numbers(text).split("\n")[1:] == ["[^7]: 註甲", "[^8]: 註乙"]


def test_align_note_numbers_leaves_count_mismatch_alone():
    # 數量對不上（跨頁註、漏讀）不猜
    text = "甲[^3]乙[^4]\n[^1]: 只有一條"
    assert align_note_numbers(text) == text


def test_align_note_numbers_keeps_continuation():
    text = "[^續]: 上一頁接下來\n正文[^5]\n[^1]: 註"
    out = align_note_numbers(text).split("\n")
    assert out[0] == "[^續]: 上一頁接下來" and out[2] == "[^5]: 註"


def test_section_titles_joins_wrapped_lines_and_skips_chapter_names():
    toc = ("五・求法、教學的生涯\n23 閩院求學/開始寫作/由學而講/人生佛教/不同見解\n"
           "九・顛沛流離\n繞道西北/大師示寂/隨喜戒會/香港三年/擬建\n精舍/望重香江")
    keys = section_titles(toc)
    assert {"閩院求學", "不同見解", "擬建精舍", "望重香江"} <= keys
    assert "擬建" not in keys


def test_unwrap_print_lines_joins_full_lines_only():
    from chaohwei_seeder_build import unwrap_print_lines
    full = "甲" * 24
    text = "\n".join([full, full, "段尾。", "　" + "乙" * 23, full, "又一段尾。",
                      full, full, "丙丙。", "[^1]: 註"])
    out = unwrap_print_lines(text).split("\n")
    assert out[0] == full * 2 + "段尾。"
    assert out[-1] == "[^1]: 註"
    assert len(out) == 4


def test_unwrap_print_lines_leaves_paragraph_pages_alone():
    from chaohwei_seeder_build import unwrap_print_lines
    text = "\n".join(["長" * 120] * 9)
    assert unwrap_print_lines(text) == text
