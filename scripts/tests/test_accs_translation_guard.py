"""譯文守門：擋掉「模型把提示詞覆述當輸出」這類看起來像成功的失敗。

2026-09-04 雅歌那輪，腳本回報 204/204 全數完成，其中 3 則的內容是
「We need to translate the given English passage into Traditional Chinese,
following rules: ...」——原文 707 字，譯出 19,599 字。沒有任何錯誤訊息。
"""
import accs_ingest_epub as A


SRC = "Come with me from Lebanon, my bride, with me from Lebanon."
GOOD = "「我的新婦，求你與我一同離開黎巴嫩，與我一同離開黎巴嫩。」"


class TestLooksLikeATranslation:
    def test_accepts_a_real_translation(self):
        assert A.looks_like_a_translation(SRC, GOOD)

    def test_rejects_prompt_restated_as_output(self):
        bad = ("We need to translate the given English passage into Traditional "
               "Chinese, following rules:\n\n- Strict Traditional Chinese…")
        assert not A.looks_like_a_translation(SRC, bad)

    def test_rejects_other_meta_openers(self):
        for bad in ("Let me translate this passage.", "以下是我的翻譯：", "好的，翻譯如下",
                    "I will now render the text.", "Here is the translation:"):
            assert not A.looks_like_a_translation(SRC, bad), bad

    def test_rejects_runaway_length(self):
        # 中譯通常比英文短；長成三倍以上必是失控。
        # 用貼近真實失敗的長度：原文 707 字譯出 19,599 字。
        long_src = SRC * 13                       # ~750 字
        assert not A.looks_like_a_translation(long_src, "譯" * 19599)

    def test_short_source_is_exempt_from_the_length_gate(self):
        # 一句話的原文譯出來相對變長很正常，400 字以下不套長度閘，
        # 否則「Amen.」→「阿們」這種正常譯文會被誤殺
        assert A.looks_like_a_translation("Selah.", "細拉。（詩篇中的音樂術語，意義不明）")

    def test_rejects_untranslated_english(self):
        assert not A.looks_like_a_translation(SRC, SRC)

    def test_rejects_empty(self):
        assert not A.looks_like_a_translation(SRC, "")
        assert not A.looks_like_a_translation(SRC, "   ")

    def test_short_source_still_allows_a_reasonable_expansion(self):
        # 極短的原文譯出來難免相對變長，不該被長度閘誤殺
        assert A.looks_like_a_translation("Amen.", "阿們。這是全體會眾的回應。")


class TestTranslateRetries:
    def test_returns_empty_rather_than_writing_garbage(self, monkeypatch):
        """三次都吐垃圾就回空字串 —— 讓那一則留在待譯清單裡，下次重跑補上，
        比寫一段垃圾進資料庫好。"""
        monkeypatch.setattr(A.te, "gemini_with_nvidia_fallback",
                            lambda _t: "We need to translate the passage…")
        assert A.translate(SRC, tries=3) == ""

    def test_accepts_once_a_retry_comes_back_clean(self, monkeypatch):
        calls = {"n": 0}

        def flaky(_t):
            calls["n"] += 1
            return "We need to translate…" if calls["n"] == 1 else GOOD

        monkeypatch.setattr(A.te, "gemini_with_nvidia_fallback", flaky)
        assert A.translate(SRC, tries=3) == GOOD
        assert calls["n"] == 2
