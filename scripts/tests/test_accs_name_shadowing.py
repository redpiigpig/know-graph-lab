"""教父署名解析：括號裸名不可蓋掉資料完整的正主。

2026-09-04 的事故：詞庫有四筆 Ambrose，其中兩筆是同一個人（俄利根的贊助者）
重複建檔。build_name_map 會把括號剝掉造「裸名」鍵，於是
`Ambrose (Origen's patron)` 的裸名 `Ambrose` 蓋掉了 `Ambrose of Milan`——
jer/lam/sng 有 83 列把米蘭的安波羅修的話掛到另一個人名下。

在教父文獻裡張冠李戴不是排版問題，所以這裡釘兩件事：
  1. 有世紀／身分的人優先佔鍵（setdefault 先到先得，順序就是正確性）
  2. ACCS 的 Ambrose 一律是米蘭的那位（ALIASES 明寫）
"""
import accs_ingest_epub as A


def fake_rows():
    """兩筆 Ambrose：一筆資料完整的正主，一筆只有名字的殘筆。"""
    return [
        {"name_english": "Ambrose (Origen's patron)",
         "name_latin_std": "Ambrose (Origen's patron)",
         "name_recommended": "安波羅斯（俄利根贊助者）", "century": None, "role": None},
        {"name_english": "Ambrose of Milan", "name_latin_std": "Ambrosius Mediolanensis",
         "name_recommended": "安波羅修", "century": "4c", "role": "教父；教會博士；米蘭主教"},
        {"name_english": "Ambrosiaster", "name_latin_std": "Ambrosiaster",
         "name_recommended": "安波羅修註釋者", "century": "4c", "role": "拉丁保羅書信註釋者"},
    ]


def build(monkeypatch):
    class R:
        status_code = 200
        def raise_for_status(self): pass
        def json(self): return fake_rows()
    monkeypatch.setattr(A.requests, "get", lambda *a, **k: R())
    return A.build_name_map()


class TestBareNameShadowing:
    def test_ambiguous_bare_name_is_not_registered_at_all(self, monkeypatch):
        """裸名 'Ambrose' 同時是 'Ambrose of Milan' 的開頭 → 含糊，不建鍵。

        建了就等於替語料做了一個沒有根據的決定，而且會是錯的那個：殘筆
        「Ambrose (Origen's patron)」剝括號後剛好長得像確定答案。
        不建鍵才能讓 resolve_father 的前綴比對看見「有多個候選」。
        """
        assert "ambrose" not in build(monkeypatch)

    def test_full_names_still_resolve_to_themselves(self, monkeypatch):
        m = build(monkeypatch)
        assert m["ambrose of milan"] == "安波羅修"
        assert m["ambrosiaster"] == "安波羅修註釋者"
        assert m["ambrose (origen's patron)"] == "安波羅斯（俄利根贊助者）"


class TestResolveFather:
    def test_plain_ambrose_is_the_bishop_of_milan(self, monkeypatch):
        # ACCS 引的 Ambrose 一律是米蘭主教；掃描本 63 卷用了 1,941 次
        assert A.resolve_father("Ambrose", build(monkeypatch))[0] == "安波羅修"

    def test_the_patron_is_still_reachable_by_full_name(self, monkeypatch):
        # 修掉蓋台問題不可以反過來讓另一個人查不到
        zh, _ = A.resolve_father("Ambrose (Origen's patron)", build(monkeypatch))
        assert zh == "安波羅斯（俄利根贊助者）"

    def test_ambrosiaster_is_not_ambrose(self, monkeypatch):
        # 安波羅修註釋者是四世紀佚名作者，跟米蘭主教是兩個人
        assert A.resolve_father("Ambrosiaster", build(monkeypatch))[0] == "安波羅修註釋者"

    def test_alias_survives_an_empty_glossary(self, monkeypatch):
        """就算詞庫查不到，ALIASES 也得把 Ambrose 導向米蘭那位——
        這條是最後一道保險，別因為詞庫改動又退回誤植。"""
        assert A.ALIASES["Ambrose"] == "Ambrose of Milan"
