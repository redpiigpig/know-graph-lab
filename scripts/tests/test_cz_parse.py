"""城中週報解析純函式測試。

cz_parse.py 在 import 時只呼叫 sys.stdout.reconfigure（無網路/DB/環境變數需求），
所有檔案 I/O 都在 main() 內。本檔測欄位抽取啟發式：parse_roles / parse_record /
find_season/color/service/sermon/scriptures/hymns / easter / resolve_special_date。
"""
import datetime

import cz_parse as cz


# ── easter — Anonymous Gregorian algorithm ─────────────────────────────
class TestEaster:
    def test_known_easter_dates(self):
        assert cz.easter(2024) == datetime.date(2024, 3, 31)
        assert cz.easter(2000) == datetime.date(2000, 4, 23)
        assert cz.easter(2025) == datetime.date(2025, 4, 20)


# ── resolve_special_date — 由復活節相對特別禮拜 + 路徑年份推日期 ───────────
class TestResolveSpecialDate:
    def test_good_friday_two_days_before_easter(self):
        # 受難節 = 復活節前 2 天；2024 復活節 3/31 → 受難節 3/29。
        d, label = cz.resolve_special_date("c:/x/2024受難節週報.docx", "受難週", "")
        assert d == "2024-03-29"
        assert label == "受難節禮拜"

    def test_palm_sunday_seven_days_before(self):
        d, label = cz.resolve_special_date("c:/x/2023棕枝主日.docx", "", "")
        assert d == "2023-04-02"
        assert label == "棕枝主日"

    def test_no_year_in_path_returns_none(self):
        assert cz.resolve_special_date("c:/x/平安夜.docx", "", "") == (None, None)


# ── is_personish — 人名判定（含稱謂 或 1-4 字）────────────────────────
class TestIsPersonish:
    def test_with_title(self):
        assert cz.is_personish("龐君華牧師") is True

    def test_short_name(self):
        assert cz.is_personish("王明") is True

    def test_long_phrase_not_person(self):
        assert cz.is_personish("這是一個很長的句子不可能是人名啦啦啦啦啦啦") is False


# ── parse_roles — 敬拜服事表 cell-pair 抽取 ─────────────────────────
class TestParseRoles:
    def test_extracts_roles_from_worship_table(self):
        tables = [[
            ["主禮/證道：龐君華牧師", "司會：王小明"],
            ["司琴：李四", "領詩：張三"],
        ]]
        roles = cz.parse_roles([], tables)
        # 主禮/證道 同值雙寫
        assert roles["主禮"] == "龐君華牧師"
        assert roles["證道"] == "龐君華牧師"
        assert roles["司會"] == "王小明"
        assert roles["司琴"] == "李四"

    def test_non_worship_table_ignored(self):
        # 缺 司會/司琴 與 主禮/證道 訊號 → 非敬拜表，不抽取。
        tables = [[["聚會名稱", "目前狀況"], ["小組", "需要人數"]]]
        assert cz.parse_roles([], tables) == {}


# ── find_season / find_color / find_service ───────────────────────────
class TestFindSeasonColorService:
    def test_season(self):
        paras = ["中華基督教衛理公會城中教會", "聖靈降臨後第五主日", "龐君華"]
        assert cz.find_season(paras) == "聖靈降臨後第五主日"

    def test_color(self):
        assert cz.find_color(["本日禮儀顏色用於聖靈降臨節象徵紅色"]) == "紅"

    def test_service_explicit(self):
        assert cz.find_service(["晚堂崇拜程序"], "x.docx") == "晚堂"

    def test_service_default(self):
        assert cz.find_service(["一般內容無服務字樣"], "x.docx") == "主日崇拜"


# ── find_sermon — 標題抽取（label 優先，再 worship-order line）────────
class TestFindSermon:
    def test_explicit_label(self):
        assert cz.find_sermon(["講道題目：信心的力量"], {}) == "信心的力量"

    def test_worship_order_line_long_title(self):
        # SERMON_LINE：「證道 <標題> <講員>」；清掉講員名尾後須 >4 字（否則被
        # is_personish 當人名濾掉 — 見 report 註記的 quirk）。
        out = cz.find_sermon(["證道 從曠野到應許之地的旅程 龐君華牧師"], {})
        assert out == "從曠野到應許之地的旅程"

    def test_no_sermon_returns_none(self):
        assert cz.find_sermon(["一般敬拜內容沒有講題"], {}) is None


# ── find_scriptures — 標籤經課集 vs 貪婪未標籤清單 ────────────────────
class TestFindScriptures:
    def test_labeled_lectionary_set(self):
        paras = ["經課一：創世記1:1-5", "經課二：詩篇23:1-6", "福音書：約翰福音3:16"]
        refs, ref_str, is_labeled = cz.find_scriptures(paras)
        assert refs == ["創世記1:1-5", "詩篇23:1-6", "約翰福音3:16"]
        assert is_labeled is True
        assert "經課一：創世記1:1-5" in ref_str
        assert "福音書：約翰福音3:16" in ref_str

    def test_no_scripture_paras(self):
        refs, ref_str, is_labeled = cz.find_scriptures(["這段沒有任何經文引用"])
        assert refs == []
        assert ref_str == ""
        assert is_labeled is False


# ── find_hymns — 詩本 + 編號 + 標題抽取與去重 ─────────────────────────
class TestFindHymns:
    def test_extracts_and_dedupes(self):
        paras = [
            "新普天頌讚 第123首 「奇異恩典」",
            "普天頌讚 第45首 讚美主",
            "新普天頌讚 第123首 「奇異恩典」",  # 重複 (book,no) → 去重
        ]
        hymns = cz.find_hymns(paras)
        assert len(hymns) == 2
        assert hymns[0] == {"book": "新普天頌讚", "no": "123", "title": "奇異恩典"}
        assert hymns[1]["book"] == "普天頌讚"

    def test_no_hymns(self):
        assert cz.find_hymns(["這段沒有詩歌"]) == []


# ── parse_record — 端到端組裝（不碰檔案 I/O）─────────────────────────
class TestParseRecord:
    def test_happy_path_record(self):
        rec = {
            "file": "c:/x/2024-03-10.docx",
            "fname": "24-3-10.docx",
            "date": None,
            "paras": [
                "中華基督教衛理公會城中教會",
                "主後二○二四年三月十日主日",
                "聖靈降臨後第五主日",
                "講道題目：信心的力量",
                "經課一：詩篇23:1-6",
                "經課二：約翰福音3:16",
                "新普天頌讚 第123首 奇異恩典",
            ],
            "tables": [[["證道：龐君華牧師", "司會：王小明"]]],
            "nchars": 100,
            "ext": "docx",
        }
        r = cz.parse_record(rec)
        # date 由 fname 的 loose date 24-3-10 → 2024-03-10
        assert r["date"] == "2024-03-10"
        assert r["preacher"] == "龐君華牧師"
        assert r["sermon_title"] == "信心的力量"
        assert r["season"] == "聖靈降臨後第五主日"
        assert r["scripture_labeled"] is True
        assert len(r["hymns"]) == 1

    def test_fullwidth_date_normalized(self):
        # 全形數字日期會被 translate 成半形。
        rec = {
            "file": "c:/x/foo.docx",
            "fname": "foo.docx",
            "date": "２０２４-０３-１０",
            "paras": ["一般內容"],
            "tables": [],
            "nchars": 10,
            "ext": "docx",
        }
        r = cz.parse_record(rec)
        assert r["date"] == "2024-03-10"
