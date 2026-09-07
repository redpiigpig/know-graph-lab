# -*- coding: utf-8 -*-
"""Test-first lock for the proper-name consistency repairer.

Machine translation of a 1,442-paragraph biography renders the same person's
name differently from chapter to chapter — 內村鑑三's first wife Take came out
as 武子／武／武江／武惠, his son Yûshi as 雄士／雄志／有島雄士. Nothing crashes and
every page still reads fine, so this is the [[feedback_reader_silent_failures]]
class of defect: it can only be caught by cross-checking against the source.

The rule these tests pin down: a variant is rewritten ONLY inside paragraphs
whose ENGLISH source actually names that person. That guard is what keeps
有島 (＝有島武郎 Arishima Takeo, a real and separate figure appearing 20 times)
from being destroyed while fixing the 7 paragraphs where the translator
wrongly borrowed his surname for 內村祐之.

See .claude/skills/ebook-collected-works/howes_uchimura_biography.md.
"""
import name_lock as nl


def lock(**kw):
    base = dict(key="t", en=r"\bTake\b", repl=[("武子", "武")], canon="武")
    base.update(kw)
    return nl.Lock(**base)


class TestRepairParagraph:
    def test_variant_replaced_when_english_names_the_person(self):
        zh, n = nl.repair_paragraph("Kanzô married Take.", "鑑三與武子結婚。", [lock()])
        assert zh == "鑑三與武結婚。"
        assert n == 1

    def test_variant_left_alone_when_english_does_not_name_the_person(self):
        """沒有英文佐證就不動 —— 這是不誤傷同形字的唯一保險。"""
        zh, n = nl.repair_paragraph("His mother objected.", "他的母親反對武子。", [lock()])
        assert zh == "他的母親反對武子。"
        assert n == 0

    def test_canonical_form_is_not_touched(self):
        zh, n = nl.repair_paragraph("Take arrived.", "武抵達了。", [lock()])
        assert (zh, n) == ("武抵達了。", 0)

    def test_counts_every_occurrence_in_one_paragraph(self):
        zh, n = nl.repair_paragraph("Take and Take.", "武子與武子。", [lock()])
        assert (zh, n) == ("武與武。", 2)


class TestLongestVariantFirst:
    """短變體是長變體的子字串時，順序錯了會把長的切成兩半。"""

    def test_surnamed_variant_rewritten_before_bare_one(self):
        lk = lock(key="y", en=r"\bY[uû]shi\b",
                  repl=[("雄士", "祐之"), ("有島雄士", "祐之")], canon="祐之")
        zh, n = nl.repair_paragraph("Yûshi grew up.", "有島雄士長大了。", [lk])
        assert zh == "祐之長大了。"  # 順序錯會留下「有島祐之」
        assert n == 1

    def test_bare_variant_still_handled_in_the_same_pass(self):
        lk = lock(key="y", en=r"\bY[uû]shi\b",
                  repl=[("雄士", "祐之"), ("有島雄士", "祐之")], canon="祐之")
        zh, _ = nl.repair_paragraph("Yûshi and Yûshi.", "有島雄士與雄士。", [lk])
        assert zh == "祐之與祐之。"


class TestCollisionSafety:
    def test_arishima_takeo_survives_the_yushi_repair(self):
        """有島武郎 是真人，只有『有島雄士』才是污染 —— 別把姓氏連根拔掉。"""
        lk = lock(key="y", en=r"\bY[uû]shi\b",
                  repl=[("雄士", "祐之"), ("有島雄士", "祐之")], canon="祐之")
        src = "Arishima Takeo joined Uchimura early."
        zh, n = nl.repair_paragraph(src, "有島武郎早年加入內村。", [lk])
        assert zh == "有島武郎早年加入內村。"
        assert n == 0

    def test_arishima_and_yushi_in_one_paragraph(self):
        lk = lock(key="y", en=r"\bY[uû]shi\b",
                  repl=[("雄士", "祐之"), ("有島雄士", "祐之")], canon="祐之")
        src = "Arishima Takeo and Yûshi both."
        zh, n = nl.repair_paragraph(src, "有島武郎與有島雄士二人。", [lk])
        assert zh == "有島武郎與祐之二人。"
        assert n == 1


class TestAudit:
    def test_reports_surviving_variants(self):
        pairs = [("Take married.", "武子結婚。"), ("Take left.", "武離開。")]
        issues = nl.audit(pairs, [lock()])
        assert len(issues) == 1
        assert issues[0].variant == "武子"
        assert issues[0].index == 0

    def test_clean_corpus_reports_nothing(self):
        pairs = [("Take married.", "武結婚。"), ("Nothing here.", "無關。")]
        assert nl.audit(pairs, [lock()]) == []

    def test_audit_ignores_variants_without_english_evidence(self):
        assert nl.audit([("Nothing.", "武子。")], [lock()]) == []


class TestRegistry:
    """實際掛在豪斯傳記上的六條鎖 —— 改動要有意識。"""

    def test_six_locks_and_all_shapes_valid(self):
        assert len(nl.HOWES_LOCKS) == 6
        for lk in nl.HOWES_LOCKS:
            assert lk.canon and lk.en and lk.repl
            for frm, to in lk.repl:
                assert frm != to
            # canonical form must never itself be a replacement source
            assert all(frm != lk.canon for frm, _ in lk.repl)

    def test_take_and_yushi_and_nobu_are_locked(self):
        keys = {lk.key for lk in nl.HOWES_LOCKS}
        assert {"take", "yushi", "nobu", "parmalee", "gundert"} <= keys


class TestTally:
    def test_nested_variant_is_not_double_counted(self):
        """「延子」本來就包在「淺田延子」裡，分開數會多算一次。"""
        lk = lock(key="n", en=r"\bNobu\b",
                  repl=[("淺田延子", "淺田信"), ("延子", "淺田信")], canon="淺田信")
        t = {}
        zh, n = nl.repair_paragraph("Nobu wrote. Nobu left.",
                                    "淺田延子寫信。延子離開。", [lk], tally=t)
        assert zh == "淺田信寫信。淺田信離開。"
        assert n == 2
        assert t == {("n", "淺田延子", "淺田信"): 1, ("n", "延子", "淺田信"): 1}
