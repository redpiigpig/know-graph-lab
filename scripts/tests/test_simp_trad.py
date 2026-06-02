"""簡→繁 conversion + detection (simp_to_trad_batch + parse_drive_inventory).

Pipeline B converts simplified-Chinese books in place with opencc s2tw +
TRAD_FIXES (no LLM). Two things must hold: detection must not false-positive
on traditional/English text, and TRAD_FIXES must repair opencc's known
over-conversions (历 → 曆 instead of 歷). Conversion must also be idempotent
on already-traditional text.
"""
import simp_to_trad_batch as stt
import parse_drive_inventory as pdi


class TestSimplifiedDetection:
    def test_detects_simplified_indicators(self):
        assert stt.is_simplified("这是简体中文的书")  # 这/简/书

    def test_traditional_text_not_flagged(self):
        # Pure traditional — none of the simplified-only indicators present.
        assert not stt.is_simplified("這是繁體中文的內容，沒有簡體字。")

    def test_english_not_flagged(self):
        assert not stt.is_simplified("This is an English paragraph only.")

    def test_empty(self):
        assert not stt.is_simplified("")


class TestTradFixes:
    def test_li_shi_overconversion_repaired(self):
        # opencc s2tw turns 历史 → 曆史; TRAD_FIXES must restore 歷史.
        out = pdi.to_traditional("历史")
        assert "歷史" in out
        assert "曆史" not in out

    def test_jingli_repaired(self):
        assert "經歷" in pdi.to_traditional("经历")

    def test_tuo_surname_repaired(self):
        # 托尔斯泰 should stay 托爾斯泰, not become 託爾斯泰.
        out = pdi.to_traditional("托尔斯泰")
        assert "托爾斯泰" in out
        assert "託爾斯泰" not in out

    def test_idempotent_on_traditional(self):
        # Running conversion on already-traditional text changes nothing
        # meaningful (skill: "對純繁中文本跑也沒副作用").
        already = "歷史的經歷與心路歷程"
        assert pdi.to_traditional(already) == already

    def test_empty_passthrough(self):
        assert pdi.to_traditional("") == ""
