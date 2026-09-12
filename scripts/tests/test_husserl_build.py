# -*- coding: utf-8 -*-
"""胡塞爾《觀念一》Vision OCR 後處理的純函式測試。

樣本取自實跑（gemini-2.5-flash 對 in.ernet.dli.2015.188260 的 pp60–65、pp98–101），
包含真的出現過的兩種毛病：書眉黏在頁碼後面、行末斷詞沒接回。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from husserl_build import (  # noqa: E402
    batches, check_structure, dedupe_pages, is_chapter_head, looks_line_broken,
    page_fingerprint, paged_units, parse_page, parse_toc, restore_missing_heads,
    split_glued, split_head_from_body, split_sections, strip_back_matter,
    strip_toc, title_zh_for, toc_span, TITLES_ZH,
)


# ── batches ─────────────────────────────────────────────────────────────────

def test_batches_covers_every_page_once():
    bs = batches(20, 8)
    assert bs == [(1, 8), (9, 16), (17, 20)]
    assert sum(hi - lo + 1 for lo, hi in bs) == 20


def test_batches_exact_multiple():
    assert batches(16, 8) == [(1, 8), (9, 16)]


# ── parse_page ──────────────────────────────────────────────────────────────

def test_parse_page_pulls_folio_and_body():
    folio, units = parse_page("[[p 62]]\nthe function of supplying a logical ground.")
    assert folio == "62"
    assert units == [{"kind": "body", "text": "the function of supplying a logical ground."}]


def test_parse_page_unknown_folio_is_none_not_guessed():
    """🚨 章首頁沒印頁碼就是沒有。假頁碼比沒有更糟——會讓人照著寫進論文。"""
    folio, _units = parse_page("[[p ?]]\n## FIRST CHAPTER")
    assert folio is None


def test_parse_page_separates_notes_and_puts_them_last():
    folio, units = parse_page(
        "[[p 63]]\nbody one\n[note] 1 Cf. Logische Untersuchungen II\nbody two")
    assert [u["kind"] for u in units] == ["body", "body", "note"]
    assert units[-1]["text"] == "1 Cf. Logische Untersuchungen II"


def test_parse_page_joins_soft_hyphen_left_by_ocr():
    """實跑殘留：「I experi- ence it」。真連字號後面不會有空白，所以分得開。"""
    _f, units = parse_page("[[p 61]]\nI discover it immediately, I experi- ence it.")
    assert units[0]["text"] == "I discover it immediately, I experience it."


def test_parse_page_keeps_real_hyphens():
    _f, units = parse_page("[[p 61]]\nof temporo-spatial reality and self-evidence")
    assert units[0]["text"] == "of temporo-spatial reality and self-evidence"


def test_parse_page_strips_stray_folio_markers_mid_page():
    """同一批偶爾把兩頁併成一則，殘留的 [[p N]] 不可以留在正文裡。"""
    _f, units = parse_page("[[p 61]]\nfirst page body\n[[p 62]] second page body")
    assert all("[[p" not in u["text"] for u in units)


def test_parse_page_blank():
    folio, units = parse_page("")
    assert folio is None and units == []


def test_parse_page_drops_empty_note():
    _f, units = parse_page("[[p 1]]\nbody\n[note]   ")
    assert [u["kind"] for u in units] == ["body"]


# ── paged_units ─────────────────────────────────────────────────────────────

def test_paged_units_fills_chapter_opening_folio_backwards():
    """章首頁不印書眉；由下一頁減一推回來。"""
    pages = [{"page": 1, "text": "[[p ?]]\n## FIRST CHAPTER"},
             {"page": 2, "text": "[[p 102]]\nbody"}]
    units = paged_units(pages)
    assert [u["page"] for u in units] == ["101", "102"]


def test_paged_units_carries_folio_to_notes_on_same_page():
    pages = [{"page": 1, "text": "[[p 20]]\nbody\n[note] 1 Cf. Marett"}]
    units = paged_units(pages)
    assert all(u["page"] == "20" for u in units)


def test_paged_units_leaves_unknown_folio_null_when_nothing_to_infer_from():
    units = paged_units([{"page": 1, "text": "[[p ?]]\nfront matter"}])
    assert units[0]["page"] is None


# ── 章節切分 ────────────────────────────────────────────────────────────────

def test_is_chapter_head_accepts_chapter_level_titles():
    assert is_chapter_head("FIRST CHAPTER")
    assert is_chapter_head("SECOND SECTION")
    assert is_chapter_head("INTRODUCTION")
    assert is_chapter_head("Author's Preface")


def test_is_chapter_head_rejects_section_level_titles():
    """🚨 § 是章內小節。拿它當章界會切出兩百多個只有一段的「章」。"""
    assert not is_chapter_head("§ 27. THE WORLD OF THE NATURAL STANDPOINT")
    assert not is_chapter_head("§ 8. INTERDEPENDENCE OF THE SCIENCES")


def test_split_sections_breaks_only_on_chapter_heads():
    units = [
        {"kind": "body", "text": "## FIRST CHAPTER", "page": "101"},
        {"kind": "body", "text": "## § 27. THE WORLD OF THE NATURAL STANDPOINT", "page": "101"},
        {"kind": "body", "text": "Our first outlook upon life", "page": "101"},
        {"kind": "body", "text": "## SECOND CHAPTER", "page": "120"},
        {"kind": "body", "text": "next chapter body", "page": "120"},
    ]
    secs = split_sections(units)
    assert [s["heading"] for s in secs] == ["FIRST CHAPTER", "SECOND CHAPTER"]
    # § 標題留在正文裡當一行，不被吃掉
    assert secs[0]["paras"][0].startswith("## § 27.")
    assert len(secs[0]["paras"]) == 2


def test_split_sections_keeps_the_subtitle_line_as_the_sections_subtitle():
    """🚨「FIRST CHAPTER」在這本書裡出現四次。只留章標題，reader 的目錄就是四個
    「第一章」，分不出是哪一章——頁面完全正常，目錄卻沒有意義。"""
    units = [
        {"kind": "body", "text": "## FIRST CHAPTER", "page": "51"},
        {"kind": "body", "text": "## FACT AND ESSENCE", "page": "51"},
        {"kind": "body", "text": "## § 1. NATURAL KNOWLEDGE AND EXPERIENCE", "page": "51"},
        {"kind": "body", "text": "Natural knowledge begins with experience", "page": "51"},
    ]
    secs = split_sections(units)
    assert secs[0]["heading"] == "FIRST CHAPTER"
    assert secs[0]["subtitle"] == "FACT AND ESSENCE"
    # 副標仍留在正文裡——書上就印著這一行
    assert secs[0]["paras"][0] == "## FACT AND ESSENCE"


def test_split_sections_does_not_take_a_section_number_as_the_subtitle():
    units = [{"kind": "body", "text": "## THIRD CHAPTER", "page": "255"},
             {"kind": "body", "text": "## § 87. INTRODUCTORY REMARKS", "page": "255"},
             {"kind": "body", "text": "body", "page": "255"}]
    assert split_sections(units)[0]["subtitle"] == ""


def test_curated_chinese_titles_cover_every_chapter_of_the_toc():
    """章名寫死是為了不讓引擎每次翻得不一樣，也為了不讓四個「第一章」撞名。"""
    assert title_zh_for({"heading": "FIRST CHAPTER",
                         "subtitle": "THE THESIS OF THE NATURAL STANDPOINT AND ITS SUSPENSION"}) \
        == "第一章　自然態度的總設定及其懸置"
    assert title_zh_for({"heading": "FIRST CHAPTER", "subtitle": "FACT AND ESSENCE"}) \
        == "第一章　事實與本質"
    assert title_zh_for({"heading": "NO SUCH CHAPTER", "subtitle": ""}) is None
    assert len({v for v in TITLES_ZH.values()}) == len(TITLES_ZH)   # 沒有兩章同名


def test_split_sections_keeps_pages_aligned_with_paras():
    units = [{"kind": "body", "text": f"para {i}", "page": str(100 + i)} for i in range(4)]
    secs = split_sections(units)
    assert len(secs) == 1
    assert len(secs[0]["paras"]) == len(secs[0]["pages"]) == 4


def test_split_sections_drops_trailing_empty_chapter():
    units = [{"kind": "body", "text": "## INDEX", "page": "460"}]
    assert split_sections(units) == []


# ── 一行一段閘門（真跑出來才發現的第一號坑）────────────────────────────────

def _para(t):
    return {"kind": "body", "text": t}


def test_looks_line_broken_catches_line_per_paragraph():
    """實跑 b0017：中位段長 64、句尾完整率 6%。每一「段」其實是半句話，
    逐句送去翻譯會得到把殘句當完整句翻的胡話。"""
    lines = ["menological reduction, that is, through Epoché. I might have",
             "been better advised if, without altering the essential connexions",
             "of the exposition, I had left open the final decision in favour of",
             "transcendental Idealism, and contented myself with making clear"]
    assert looks_line_broken([_para(t) for t in lines * 6])


def test_looks_line_broken_passes_real_paragraphs():
    """實跑 b0009：中位段長 593。跨頁續段讓句尾完整率只有 50%，不可誤判。"""
    para = ("Our first outlook upon life is that of natural human beings, imaging, judging, "
            "feeling, willing, from the natural standpoint. " * 6)
    units = [_para(para) for _ in range(20)] + [_para("continues onto the next page and")] * 20
    assert not looks_line_broken(units)


def test_looks_line_broken_spares_short_front_matter():
    """🚨 扉頁、目錄、獻詞本來就是短行且句句完整。只看段長會把它們全誤判掉
    （實跑 b0001：中位 64 字，但句尾完整率 81%）。"""
    units = [_para(f"CHAPTER {i}. THE THESIS OF THE NATURAL STANDPOINT.") for i in range(30)]
    assert not looks_line_broken(units)


def test_looks_line_broken_ignores_tiny_batches():
    """樣本太少判不準，一律放行——寧可漏，不可把好的批砍掉重跑燒配額。"""
    assert not looks_line_broken([_para("short") for _ in range(5)])


def test_looks_line_broken_ignores_headings():
    units = [{"kind": "body", "text": "## § 27. THE WORLD"} for _ in range(30)]
    assert not looks_line_broken(units)


# ── 重複掃描頁（archive.org 這份把印刷頁 176–177 拍了兩次）──────────────────

_LONG = ("concern. And however he conceives concepts and propositions, draws inferences, "
         "and so forth, that which formal logic decrees with formal generality concerning "
         "meanings of this type and classes of such meanings concerns him in the same way "
         "as it does every special worker. Therefore it concerns the phenomenologist also. "
         "Every pure experience also finds its place under the widest logical meaning of "
         "object. Thus—so it would seem—we cannot suspend formal logic and formal ontology.")


def test_dedupe_drops_the_second_photograph_of_the_same_page():
    """🚨 兩張照片、像素不同（雜湊比不出來），OCR 忠實地各轉錄一次。不丟掉的話
    站上就是一整頁一字不差的重複，而頁碼齊、頁面完全正常。"""
    pages = [{"page": 175, "text": f"[[p 176]]\n{_LONG}"},
             {"page": 176, "text": f"[[p 177]]\nWith this understanding we attain at once "
                                   f"the explicit knowledge that a descriptive phenomenology "
                                   f"is in principle independent of all those disciplines. "
                                   f"{_LONG}"},
             {"page": 177, "text": f"[[p 176]]\n{_LONG}"}]
    keep, dropped = dedupe_pages(pages)
    assert [p["page"] for p in keep] == [175, 176]
    assert dropped == [177]


def test_dedupe_keeps_pages_that_merely_start_alike():
    a = {"page": 1, "text": f"[[p 10]]\n{_LONG} And then the argument turns to essences."}
    b = {"page": 2, "text": f"[[p 11]]\n{_LONG[:60]} but here it takes another turn entirely, "
                            f"one that has nothing whatever to do with the preceding page, "
                            f"as the reader will presently see for himself in due course."}
    keep, dropped = dedupe_pages([a, b])
    assert len(keep) == 2 and dropped == []


def test_dedupe_never_touches_short_pages():
    """章首頁、分部頁本來就短又長得像。寧可漏一張重複，也不要刪掉正文。"""
    pages = [{"page": 1, "text": "[[p ?]]\n## FIRST CHAPTER"},
             {"page": 2, "text": "[[p ?]]\n## FIRST CHAPTER"}]
    keep, dropped = dedupe_pages(pages)
    assert len(keep) == 2 and dropped == []
    assert page_fingerprint("[[p ?]]\n## FIRST CHAPTER") == ""


# ── 黏成一行（Vision 偶爾整頁不換行）────────────────────────────────────────

def test_split_glued_breaks_three_headings_and_the_body_after_them():
    """實測 scan146 一行裡黏了四件事。切不開的話這一章的章界就沒了。"""
    line = ("## THIRD CHAPTER## THE REGION OF PURE CONSCIOUSNESS## § 47. THE NATURAL "
            "WORLD AS CORRELATE OF CONSCIOUSNESSIn connexion with the results of the "
            "last chapter we add the following consideration.")
    assert split_glued(line) == [
        "## THIRD CHAPTER",
        "## THE REGION OF PURE CONSCIOUSNESS",
        "## § 47. THE NATURAL WORLD AS CORRELATE OF CONSCIOUSNESS",
        "In connexion with the results of the last chapter we add the following consideration.",
    ]


def test_split_glued_breaks_a_footnote_glued_mid_line():
    line = ("but if we question the essential conditions of its validity, the kind of "
            "evidence[note] modifications, but the ambiguities that arise therefrom are "
            "not dangerous.")
    got = split_glued(line)
    assert len(got) == 2
    assert got[0].endswith("the kind of evidence")
    assert got[1].startswith("[note] modifications")


def test_split_glued_leaves_an_ordinary_line_alone():
    line = "Our first outlook upon life is that of natural human beings."
    assert split_glued(line) == [line]


def test_split_glued_keeps_a_footnote_that_starts_the_line():
    assert split_glued("[note] 1 Cf. Logische Untersuchungen II") == [
        "[note] 1 Cf. Logische Untersuchungen II"]


def test_split_head_from_body_spares_title_case_toc_entries():
    """🚨 目次那一層是 Title Case，照「大寫接大寫小寫」的接縫去切會切爛條目。"""
    entry = "## § 29. The “other” Ego-subjects and the intersubjective natural world 105"
    assert split_head_from_body(entry) == [entry]


def test_split_head_from_body_spares_a_clean_heading():
    head = "## § 88. REAL (REELLE) AND INTENTIONAL FACTORS OF EXPERIENCE. THE NOEMA"
    assert split_head_from_body(head) == [head]


def test_split_head_from_body_needs_a_long_enough_tail():
    """尾巴太短多半是排印怪字，不是黏上來的正文。"""
    head = "## THE REGION OF PURE CONSCIOUSNESSIn"
    assert split_head_from_body(head) == [head]


# ── 頁碼讀錯（fill 補不到，要先 repair）──────────────────────────────────────

def test_paged_units_knocks_out_a_misread_folio_and_infers_it_back():
    """🚨 實測 scan100 的書眉被讀成「4」，那一章的頁碼範圍就長成 p4–111。
    `fill_folios` 救不了它——它有值，只是值是錯的。"""
    pages = [{"page": i, "text": f"[[p {96 + i}]]\nbody {i}"} for i in range(1, 6)]
    pages.append({"page": 6, "text": "[[p 4]]\nthe chapter opening page"})
    pages.append({"page": 7, "text": "[[p 103]]\nbody after"})
    assert [u["page"] for u in paged_units(pages)] == \
        ["97", "98", "99", "100", "101", "102", "103"]


# ── 目次＝權威目錄 ──────────────────────────────────────────────────────────

def _toc_units():
    """實際目次的形狀（p35–40）：CONTENTS、每頁一個 PAGE 欄頭、章標題與副標分兩行，
    副標偶爾漏印頁碼（『THE THESIS OF…』那一行就是）。"""
    lines = [
        ("CONTENTS", "35"), ("PAGE", "35"),
        ("AUTHOR'S PREFACE TO THE ENGLISH EDITION 11", "35"),
        ("TRANSLATOR'S PREFACE 31", "35"),
        ("INTRODUCTION 41", "35"),
        ("## FIRST SECTION", "35"),
        ("## THE NATURE AND KNOWLEDGE OF ESSENTIAL BEING", "35"),
        ("## FIRST CHAPTER", "35"),
        ("## FACT AND ESSENCE 51", "35"),
        ("## § 1. Natural knowledge and experience 51", "35"),
        ("## § 2. Fact. Inseparability of fact and essence 52", "35"),
        ("## § 3. Essential insight and individual intuition 54", "35"),
        ("## § 4. Essential insight and the play of fancy 57", "35"),
        ("## § 5. Judgments about essence 58", "35"),
        ("## § 6. Some fundamental concepts 59", "35"),
        ("## § 7. Sciences of facts and sciences of the essence 61", "35"),
        ("## § 8. Interdependence of the sciences 63", "35"),
        ("## § 9. Region and regional eidetics 64", "35"),
        ("## § 10. Region and category 66", "35"),
        ("## § 11. Syntactical objectivities 69", "35"),
        ("## SECOND CHAPTER", "35"),
        ("## NATURALISTIC MISCONSTRUCTIONS 80", "35"),
        ("## § 18. Introduction to the critical discussions 80", "35"),
        ("## SECOND SECTION", "36"),
        ("## THE FUNDAMENTAL PHENOMENOLOGICAL OUTLOOK", "36"),
        ("## FIRST CHAPTER", "36"),
        ("PAGE", "36"),
        ("## THE THESIS OF THE NATURAL STANDPOINT AND ITS SUSPENSION", "36"),
        ("## § 27. The world of the natural standpoint 101", "36"),
        ("## § 28. The cogito 103", "36"),
        ("ANALYTICAL INDEX 429", "40"),
        ("INDEX TO PROPER NAMES 466", "40"),
    ]
    return [{"kind": "body", "text": t, "page": p} for t, p in lines]


def _body_units():
    return [
        {"kind": "body", "text": "## INTRODUCTION", "page": "41"},
        {"kind": "body", "text": "Pure Phenomenology, to which we are here seeking the way,",
         "page": "41"},
    ]


def test_toc_span_stops_before_the_body_and_keeps_its_first_heading():
    """🚨 目次以『最後一個帶頁碼的條目』收尾。往後多吃一行就會把正文的
    `## INTRODUCTION` 也吃掉——章數看起來還是對的，第一章卻沒了標題。"""
    units = _toc_units() + _body_units()
    lo, hi = toc_span(units)
    assert lo == 0
    assert units[hi - 1]["text"] == "INDEX TO PROPER NAMES 466"
    rest, dropped = strip_toc(units)
    assert dropped == len(_toc_units())
    assert [u["text"] for u in rest] == [u["text"] for u in _body_units()]


def test_toc_span_returns_none_when_there_is_no_contents_page():
    assert toc_span(_body_units()) is None
    assert strip_toc(_body_units())[1] == 0


def test_toc_span_needs_enough_entries_to_believe_it():
    """一兩行像目次不代表是目次。判錯就會丟掉正文。"""
    units = [{"kind": "body", "text": "CONTENTS", "page": "3"},
             {"kind": "body", "text": "PREFACE 5", "page": "3"}]
    assert toc_span(units) is None


def test_parse_toc_reads_chapter_titles_subtitles_and_pages():
    spec = parse_toc(_toc_units() + _body_units())
    assert [(e["title"], e["subtitle"], e["page"]) for e in spec] == [
        ("AUTHOR'S PREFACE TO THE ENGLISH EDITION", "", 11),
        ("TRANSLATOR'S PREFACE", "", 31),
        ("INTRODUCTION", "", 41),
        ("FIRST SECTION", "THE NATURE AND KNOWLEDGE OF ESSENTIAL BEING", None),
        ("FIRST CHAPTER", "FACT AND ESSENCE", 51),
        ("SECOND CHAPTER", "NATURALISTIC MISCONSTRUCTIONS", 80),
        ("SECOND SECTION", "THE FUNDAMENTAL PHENOMENOLOGICAL OUTLOOK", None),
        # 副標漏印頁碼 → 用該章第一個 § 的頁碼
        ("FIRST CHAPTER", "THE THESIS OF THE NATURAL STANDPOINT AND ITS SUSPENSION", 101),
        ("ANALYTICAL INDEX", "", 429),
        ("INDEX TO PROPER NAMES", "", 466),
    ]


# ── 後附索引 ────────────────────────────────────────────────────────────────

def test_strip_back_matter_cuts_at_the_page_the_toc_declares():
    spec = [{"title": "THIRD CHAPTER", "subtitle": "GRADES", "page": 404},
            {"title": "ANALYTICAL INDEX", "subtitle": "", "page": 429},
            {"title": "INDEX TO PROPER NAMES", "subtitle": "", "page": 466}]
    units = [{"kind": "body", "text": "last of the argument", "page": "427"},
             {"kind": "body", "text": "## ANALYTICAL INDEX", "page": "429"},
             {"kind": "body", "text": "Absolute, logical A. 15 b", "page": "429"}]
    kept, dropped = strip_back_matter(units, spec)
    assert dropped == 2
    assert [u["page"] for u in kept] == ["427"]


def test_strip_back_matter_refuses_when_the_toc_looks_wrong():
    """索引的頁碼竟然落在最後一章之前＝目次讀壞了。這時砍下去會砍掉正文。"""
    spec = [{"title": "THIRD CHAPTER", "subtitle": "", "page": 404},
            {"title": "ANALYTICAL INDEX", "subtitle": "", "page": 42}]
    units = [{"kind": "body", "text": "body", "page": "404"}]
    assert strip_back_matter(units, spec) == (units, 0)


# ── 章首頁被吞掉的章標題 ────────────────────────────────────────────────────

def test_restore_inserts_a_chapter_title_the_ocr_swallowed():
    """🚨 章首頁沒有書眉，而 prompt 叫模型丟掉最上面那一行——模型就把章標題當書眉
    丟了（實測 p171 的 FOURTH CHAPTER）。少一個章界，兩章就併成一章。"""
    spec = [{"title": "FOURTH CHAPTER", "subtitle": "THE PHENOMENOLOGICAL REDUCTIONS",
             "page": 171}]
    units = [{"kind": "body", "text": "## THE PHENOMENOLOGICAL REDUCTIONS", "page": "171"},
             {"kind": "body", "text": "## § 56. THE QUESTION CONCERNING", "page": "171"}]
    out, log = restore_missing_heads(units, spec)
    assert [u["text"] for u in out] == [
        "## FOURTH CHAPTER",
        "## THE PHENOMENOLOGICAL REDUCTIONS",
        "## § 56. THE QUESTION CONCERNING",
    ]
    assert len(log) == 1 and "FOURTH CHAPTER" in log[0]


def test_restore_inserts_both_lines_when_both_were_swallowed():
    spec = [{"title": "SECOND CHAPTER", "subtitle": "GENERAL STRUCTURES OF PURE CONSCIOUSNESS",
             "page": 212}]
    units = [{"kind": "body", "text": "## § 76. THE THEME OF THE FOLLOWING STUDIES",
              "page": "212"}]
    out, log = restore_missing_heads(units, spec)
    assert [u["text"] for u in out] == [
        "## SECOND CHAPTER",
        "## GENERAL STRUCTURES OF PURE CONSCIOUSNESS",
        "## § 76. THE THEME OF THE FOLLOWING STUDIES",
    ]
    assert len(log) == 2


def test_restore_puts_a_missing_subtitle_after_the_title_not_before():
    spec = [{"title": "SECOND CHAPTER", "subtitle": "PHENOMENOLOGY OF THE REASON",
             "page": 379}]
    units = [{"kind": "body", "text": "## SECOND CHAPTER", "page": "379"},
             {"kind": "body", "text": "## § 136. THE FIRST BASIC FORM", "page": "379"}]
    out, _log = restore_missing_heads(units, spec)
    assert [u["text"] for u in out] == [
        "## SECOND CHAPTER",
        "## PHENOMENOLOGY OF THE REASON",
        "## § 136. THE FIRST BASIC FORM",
    ]


def test_restore_does_nothing_when_the_heads_are_already_there():
    spec = [{"title": "FIRST CHAPTER", "subtitle": "FACT AND ESSENCE", "page": 51}]
    units = [{"kind": "body", "text": "## FIRST CHAPTER", "page": "51"},
             {"kind": "body", "text": "## FACT AND ESSENCE", "page": "51"}]
    out, log = restore_missing_heads(units, spec)
    assert len(out) == 2 and log == []


def test_restore_skips_an_entry_whose_page_is_not_in_the_body():
    """後附索引先砍掉了，它那兩筆 spec 就不該再去正文裡亂插。"""
    spec = [{"title": "ANALYTICAL INDEX", "subtitle": "", "page": 429}]
    units = [{"kind": "body", "text": "body", "page": "427"}]
    out, log = restore_missing_heads(units, spec)
    assert out == units and log == []


# ── 目次對帳（產物驗證，不是流程驗證）──────────────────────────────────────

def test_check_structure_flags_a_missing_chapter():
    spec = [{"title": "FIRST CHAPTER", "subtitle": "FACT AND ESSENCE", "page": 51},
            {"title": "SECOND CHAPTER", "subtitle": "NATURALISTIC", "page": 80}]
    secs = [{"heading": "", "subtitle": "", "paras": [], "pages": []},
            {"heading": "FIRST CHAPTER", "subtitle": "FACT AND ESSENCE",
             "paras": ["x"], "pages": ["51"]}]
    rows = check_structure(secs, spec)
    assert rows[0].startswith("✓")
    assert rows[1].startswith("✗")


def test_check_structure_ignores_the_index_entries():
    spec = [{"title": "THIRD CHAPTER", "subtitle": "", "page": 404},
            {"title": "ANALYTICAL INDEX", "subtitle": "", "page": 429}]
    secs = [{"heading": "THIRD CHAPTER", "subtitle": "NOESIS AND NOEMA",
             "paras": ["x"], "pages": ["404"]}]
    spec[0]["subtitle"] = "NOESIS AND NOEMA"
    assert check_structure(secs, spec) == ["✓ THIRD CHAPTER／NOESIS AND NOEMA　→ 第三章　能思與所思"]
