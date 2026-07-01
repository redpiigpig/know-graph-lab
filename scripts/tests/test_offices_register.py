"""Test-first contract for the 官制與行政區 (offices & administrative divisions)
register layer in scripts/glossary_naming.py — the 「翻譯定名」widening that maps a
foreign polity/era to a Han-dynastic administrative *register* (商周/秦/漢/唐/明清…)
so official titles & divisions render from that register instead of flattening to
總督/行省. See .claude/skills/translation-glossary/offices_register_blueprint.md.

Covers:
  - `offices` added to DOMAINS → its own table official_titles
  - ADMIN_REGISTERS profile shape + the 7 proposed registers
  - register_for_polity default mapping (Rome→漢制, Byzantium→唐制, Persia→秦制…)
  - check_register_valid — register must be one of the 7 (typo guard)
  - check_register_matches_polity — a polity's offices must carry its register
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import glossary_naming as gn  # noqa: E402


# ── Domain wiring ───────────────────────────────────────────────────────────
def test_offices_domain_added_with_own_table():
    by = {d["key"]: d for d in gn.DOMAINS}
    assert "offices" in by
    assert by["offices"]["table"] == "official_titles"
    assert by["offices"]["label_zh"]                      # has a Chinese label
    # other domains untouched
    assert by["rulers"]["table"] == "historical_rulers"


# ── Register taxonomy ───────────────────────────────────────────────────────
def test_dev_stage_registers_span_shangzhou_to_mingqing_plus_song_liaoyuan_feudal():
    labels = {r["label_zh"] for r in gn.ADMIN_REGISTERS}
    assert {"商周制", "春秋制", "戰國秦制", "漢制", "魏晉制", "唐制", "宋制",
            "遼金元制", "明清制", "周封建五等爵"} <= labels


def test_liaojinyuan_register_carries_nomadic_dual_admin_vocab():
    # 游牧/征服王朝：南北面官雙軌 + 十進位軍事編制 + 達魯花赤
    ljy = gn.REGISTER_BY_KEY["liao_jin_yuan"]
    assert "達魯花赤" in ljy["local"] and "萬戶" in ljy["local"]


def test_each_register_has_profile_fields():
    for r in gn.ADMIN_REGISTERS:
        assert r["key"] and r["label_zh"] and r["source"]
        assert isinstance(r["central"], list)
        assert isinstance(r["local"], list) and r["local"]   # every register has 地方詞
        assert r["note"]


def test_mingqing_register_owns_the_flat_governor_words():
    # the whole point: 總督/行省/副王-type words belong to the 明清 register only
    mq = gn.REGISTER_BY_KEY["ming_qing"]
    assert "總督" in mq["local"]


def test_weijin_register_carries_the_three_tier_ladder():
    # 羅馬晚期 大區行臺→州→郡 is the 魏晉 three-tier structure
    wj = gn.REGISTER_BY_KEY["weijin"]
    assert "行臺尚書令" in wj["central"] or "大區行臺" in wj["local"]


# ── Polity → register defaults (the developed 漢譯世界史 mapping) ─────────────
def test_register_for_polity_follows_dev_stage_mapping():
    assert gn.register_for_polity("古埃及") == "商周制"
    assert gn.register_for_polity("新亞述帝國") == "戰國秦制"
    assert gn.register_for_polity("阿契美尼德-波斯帝國") == "戰國秦制"
    assert gn.register_for_polity("鄂圖曼-土耳其帝國") == "明清制"


def test_nomadic_empires_map_to_liaojinyuan():
    # 游牧帝國用遼金元詞（使用者 2026-07-01）
    assert gn.register_for_polity("安息-帕提亞帝國") == "遼金元制"
    assert gn.register_for_polity("蒙古帝國") == "遼金元制"
    assert gn.register_for_polity("帖木兒帝國") == "遼金元制"


def test_byzantium_spans_tang_theme_then_song_civil():
    assert gn.registers_for_polity("拜占庭帝國") == ["唐制", "宋制"]
    assert gn.register_for_polity("拜占庭帝國") == "唐制"


def test_hre_is_feudal_and_sasanian_is_tang():
    # 神羅＝諸侯共主(周天子御諸侯)；薩珊＝四方都督(拜占庭之鏡像對手)
    assert gn.register_for_polity("神聖羅馬帝國") == "周封建五等爵"
    assert gn.register_for_polity("薩珊-波斯帝國") == "唐制"


def test_more_empires_mapped_by_gestalt():
    # 迦太基商業寡頭/孔雀法家集權/笈多封建盛世/草原汗國/卡洛林分封建國
    assert gn.register_for_polity("迦太基") == "春秋制"
    assert gn.register_for_polity("孔雀-印度帝國") == "戰國秦制"
    assert gn.register_for_polity("笈多-印度帝國") == "魏晉制"
    assert gn.register_for_polity("匈奴帝國") == "遼金元制"
    assert gn.register_for_polity("突厥汗國") == "遼金元制"
    assert gn.register_for_polity("查理曼-卡洛林帝國") == "周封建五等爵"


def test_rome_spans_two_registers_early_han_late_weijin():
    assert gn.registers_for_polity("羅馬帝國") == ["漢制", "魏晉制"]
    assert gn.register_for_polity("羅馬帝國") == "漢制"     # first is the default


def test_register_for_polity_trims_and_handles_unknown():
    assert gn.register_for_polity("  拜占庭帝國 ") == "唐制"
    assert gn.registers_for_polity("不存在的國") == []
    assert gn.register_for_polity(None) is None
    assert gn.registers_for_polity("") == []


# ── Validity: register must be one of the seven ─────────────────────────────
def test_check_register_valid_flags_typos_only():
    entries = [
        {"id": 1, "register": "漢制"},          # ok
        {"id": 2, "register": "唐制"},          # ok
        {"id": 3, "register": "漢代制"},        # ✗ typo, not a defined register
        {"id": 4, "register": ""},              # ignored (no register)
        {"id": 5},                              # ignored (no register key)
    ]
    assert {b["id"] for b in gn.check_register_valid(entries)} == {3}


# ── Consistency: polity's offices must carry the polity's register ──────────
def test_check_register_matches_polity_flags_wrong_register():
    entries = [
        {"id": 1, "polity": "羅馬帝國", "register": "漢制"},    # ok (early)
        {"id": 2, "polity": "羅馬帝國", "register": "魏晉制"},  # ok (late) — Rome spans both
        {"id": 3, "polity": "拜占庭帝國", "register": "唐制"},  # ok
        {"id": 4, "polity": "羅馬帝國", "register": "唐制"},    # ✗ Rome is 漢制/魏晉制
    ]
    bad = gn.check_register_matches_polity(entries)
    assert {b["id"] for b in bad} == {4}
    assert bad[0]["_expected_register"] == "漢制／魏晉制"


def test_check_register_matches_polity_ignores_unmapped_or_blank():
    entries = [
        {"id": 1, "polity": "某虛構政權", "register": "漢制"},  # polity unmapped → ignore
        {"id": 2, "polity": "羅馬帝國", "register": ""},        # no register → ignore
        {"id": 3, "polity": "羅馬帝國"},                        # no register key → ignore
    ]
    assert gn.check_register_matches_polity(entries) == []
