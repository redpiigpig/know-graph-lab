"""獵表的「期刊單篇」濾網 —— z-library 是書站，單篇它沒有。

本檔的重點是**鎖住誤判**。2026-09-16 第一版判準用了頁碼範圍、期刊名、「初探」
這些訊號，140 筆命中裡大半其實是專書；錯濾比漏濾嚴重得多（一本書從此不再被獵，
而且清單上看不出來），所以下面 TestNotArticles 那批一定要維持不命中。
"""
import zlib_wanted as zw


def matches(title: str) -> bool:
    return bool(zw.ARTICLE_FORMS.search(title))


class TestArticles:
    """這些是期刊／通訊上的單篇，不該排進書站的獵表。"""

    def test_interview_note(self):
        assert matches("釋心謙口述《弘誓的傳承與永續經營：釋心謙法師訪談記》")

    def test_interview_record(self):
        assert matches("邱敏捷訪問《「印順學派的成立、分流與發展」訪談錄》")

    def test_author_conducted_interview(self):
        assert matches("侯坤宏口述、筆者訪問《台灣佛教研究的史家視角：侯坤宏教授訪談記》")

    def test_side_note(self):
        assert matches("釋昭慧《一個溫馨的歷史性會面——陪陳總統拜會印順導師側記》")

    def test_report(self):
        assert matches("陳逸凡報導《走過坎坷葉菊蘭受洗》")

    def test_visit_note(self):
        assert matches("釋傳法報導《冥契經驗的宗教對話——古倫神父蒞院記》")


class TestNotArticles:
    """🚨 全部是**書**。第一版判準把它們誤判成單篇，這裡把那些坑釘住。"""

    def test_year_range_in_subtitle_is_not_a_page_range(self):
        # 「c. 680-850」是年代，不是頁碼
        assert not matches("Leslie Brubaker《Byzantium in the Iconoclast Era, c. 680-850》")

    def test_chapter_range_in_commentary_title(self):
        # 韋斯特曼的創世記註釋，分冊就叫 1-11
        assert not matches("韋斯特曼《創世記 1-11 註釋》")

    def test_studies_in_is_part_of_a_book_title(self):
        # J. Z. Smith 的書名本來就有 Studies in the History of Religions
        assert not matches("Smith《Map Is Not Territory: Studies in the History of Religions》")

    def test_chutan_is_a_book_title(self):
        # 「初探」照樣可以是書名
        assert not matches("容世誠《戲曲人類學初探：儀式、劇場與社群》")

    def test_angle_brackets_may_quote_a_book_inside_a_book(self):
        assert not matches("巫白慧譯解《〈梨俱吠陀〉神曲選》")

    def test_plain_monograph(self):
        assert not matches("Peter Brown《The Rise of Western Christendom》")


class TestWiring:
    def test_articles_go_to_their_own_file_not_the_hunt_list(self):
        assert zw.ARTICLES_OUT.name == "zlib_wanted_articles.jsonl"
        assert zw.ARTICLES_OUT != zw.OUT
