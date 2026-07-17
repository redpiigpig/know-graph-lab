"""Test-first lock for the Uchimura Kanzō (內村鑑三) Aozora Bunko build module.

Uchimura (d. 1930) is public domain worldwide; the first wave = 11 Aozora Bunko
XHTML texts (clean digital text, no OCR). These pin the PURE parser helpers
(decode_aozora / parse_aozora / split_long_paras / registry shape) — zero
network, LLM, or DB. See
.claude/skills/ebook-collected-works/uchimura_collected_works.md.
"""
import uchimura_build as ub

# A minimal Aozora-XHTML-shaped fixture: ruby annotation, editor notes span,
# gaiji imgs (U+hex form + ※ form), midashi heading, 底本 block after main_text.
FIXTURE = """<html><head><title>t</title></head><body>
<h1 class="title">デンマルク国の話</h1>
<h2 class="subtitle">信仰と樹木とをもって国を救いし話</h2>
<h2 class="author">内村鑑三</h2>
<div id="contents" style="display:none"></div><div class="main_text"><br />
　これは前置きの段落であります。<br />
<h4 class="naka-midashi"><a class="midashi_anchor" id="midashi10">第一講</a></h4>
　彼は<ruby><rb>甦</rb><rp>（</rp><rt>よみがえ</rt><rp>）</rp></ruby>りました。<br />
そうであろう<span class="notes">［＃「あろう」は底本では「あらう」］</span>と思います。<br />
<img src="../../../gaiji/others/xxxx.png" alt="「言＋卒」、U+8AB6" width=32 height=32 />られた言葉。<br />
記号<img src="../../../gaiji/1-06/1-06-87.png" alt="※(小書き片仮名ホ、1-6-87)" class="gaiji" />付き。<br />
</div>
<div class="bibliographical_information">底本：「後世への最大遺物・デンマルク国の話」岩波文庫</div>
</body></html>"""


class TestDecode:
    def test_shift_jis_bytes_decode(self):
        raw = "＜デンマルク＞甦り".encode("cp932")
        assert ub.decode_aozora(raw) == "＜デンマルク＞甦り"

    def test_utf8_bytes_decode(self):
        raw = "デンマルク国の話".encode("utf-8")
        assert ub.decode_aozora(raw) == "デンマルク国の話"


class TestParseAozora:
    def setup_method(self):
        self.doc = ub.parse_aozora(FIXTURE)

    def test_title_and_subtitle(self):
        assert self.doc["title"] == "デンマルク国の話"
        assert self.doc["subtitle"] == "信仰と樹木とをもって国を救いし話"

    def test_sections_split_on_midashi(self):
        heads = [s["heading"] for s in self.doc["sections"]]
        assert heads == ["(front)", "第一講"]

    def test_front_paragraph_kept(self):
        assert self.doc["sections"][0]["paras"] == ["これは前置きの段落であります。"]

    def test_ruby_reading_stripped_base_kept(self):
        paras = self.doc["sections"][1]["paras"]
        assert paras[0] == "彼は甦りました。"
        assert "よみがえ" not in "".join(paras)

    def test_editor_notes_removed(self):
        joined = "".join(self.doc["sections"][1]["paras"])
        assert "底本では" not in joined and "［＃" not in joined
        assert "そうであろうと思います。" in joined

    def test_gaiji_unicode_alt_becomes_char(self):
        joined = "".join(self.doc["sections"][1]["paras"])
        assert "誶られた言葉。" in joined  # U+8AB6

    def test_gaiji_kome_fallback(self):
        joined = "".join(self.doc["sections"][1]["paras"])
        assert "記号※付き。" in joined

    def test_bibliographical_information_excluded(self):
        all_text = "".join(p for s in self.doc["sections"] for p in s["paras"])
        assert "底本" not in all_text and "岩波文庫" not in all_text

    def test_leading_fullwidth_indent_stripped(self):
        for s in self.doc["sections"]:
            for p in s["paras"]:
                assert not p.startswith("　")


class TestSplitLongParas:
    def test_short_para_untouched(self):
        assert ub.split_long_paras(["短い。"], max_chars=100) == ["短い。"]

    def test_long_para_split_on_sentence_boundary(self):
        p = ("あ" * 80 + "。") + ("い" * 80 + "。")
        out = ub.split_long_paras([p], max_chars=100)
        assert len(out) == 2
        assert out[0].endswith("。") and out[1].endswith("。")
        assert "".join(out) == p

    def test_order_preserved_across_paras(self):
        paras = ["一。", ("う" * 90 + "。") * 2, "二。"]
        out = ub.split_long_paras(paras, max_chars=100)
        assert out[0] == "一。" and out[-1] == "二。" and len(out) == 4


class TestRegistry:
    def test_all_eleven_aozora_files_covered(self):
        files = [f for w in ub.REGISTRY.values() for f in w["files"]]
        assert len(files) == len(set(files)) == 11

    def test_ebook_ids_unique_and_namespaced(self):
        ids = [w["ebook_id"] for w in ub.REGISTRY.values()]
        assert len(ids) == len(set(ids))
        for i in ids:
            assert i.startswith("d0000000-0000-4000-8000-")

    def test_queue_covers_registry(self):
        assert sorted(ub.QUEUE) == sorted(ub.REGISTRY.keys())


class TestPieceSections:
    def test_merge_piece_into_single_section(self):
        # a short piece: whatever its internal structure, collapse to ONE section
        # headed by the piece title, internal headings inlined as ## lines
        doc = {"title": "問答二三", "subtitle": None, "sections": [
            {"heading": "(front)", "paras": ["前文。"]},
            {"heading": "其一", "paras": ["答え。"]},
        ]}
        sec = ub.piece_as_section(doc)
        assert sec["heading"] == "問答二三"
        assert sec["paras"] == ["前文。", "## 其一", "答え。"]
