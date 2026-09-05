"""ACCS 卷十五（次經）的版式變體。

檔名格式跟卷十二（耶利米）一模一樣（p*chap*.html），所以原本以為同一支 parser
就能用 —— 實測整卷 221 個章節檔只解析出 3 則，而且署名全是碎片。差別有三處，
每一處都足以讓整卷靜默地解析不出東西：

  1. 小型大寫外面多包一層 <span class="mev3/mev4">，把 <b> 從字串開頭擠開
  2. 小標被拆成連續多段 <b>，因為經文引詞用斜體另起一段
  3. 小標的收尾標點偶爾落到署名那一側

三者的共同點是「不會報錯，只會少東西」。
"""
import accs_epub as A


class TestSpanWrappedSmallcaps:
    """卷十五把小型大寫包在 <span class="mev3"> 裡；不剝掉就整段解析不出來。"""

    P = ('<p class="txt_courant_ssalinea">'
         '<span class="mev3"><b>O<small>VERVIEW:</small></b></span> '
         'The pericope begins with the imitation of God, '
         '<span class="mev4">D<small>HUODA</small></span>.</p>')

    def test_overview_is_found_through_the_span_wrapper(self):
        r = A.parse_entry(self.P)
        assert r is not None, "被 span 擋住就會回 None，整卷靜默歸零"
        assert r["kind"] == "overview"

    def test_span_wrapped_father_name_is_unsmallcapped(self):
        assert "Dhuoda" in A.parse_entry(self.P)["body"]


class TestHeadingSplitAcrossBoldRuns:
    """經文引詞用斜體另起一段，小標因此被拆成好幾個 <b>。"""

    P = ('<p class="txt_courant_ssalinea">'
         '<b><i>H<small>EAVEN</small></i></b>'
         '<span class="mev3"><b> <small>AND</small> </b></span>'
         '<b><i>F<small>IRMAMENT</small></i></b>'
         '<span class="mev3"><b> A<small>RE </small>N<small>OT THE </small>S<small>AME. </small></b></span>'
         '<span class="mev4">A<small>MBROSE: </small></span>'
         'It should not astonish us that he speaks about the heavens. '
         '<span class="mev4">S<small>IX </small>D<small>AYS OF </small>'
         'C<small>REATION</small></span> 2.4.15.</p>')

    def test_all_leading_bold_runs_become_the_heading(self):
        r = A.parse_entry(self.P)
        assert r["heading"] == "Heaven AND Firmament Are Not the Same"

    def test_the_father_is_not_polluted_by_the_rest_of_the_heading(self):
        # 只吃第一段 <b> 的話，署名會變成
        # "AND Firmament Are Not the Same. Ambrose"（署名取到第一個冒號為止）
        assert A.parse_entry(self.P)["father"] == "Ambrose"

    def test_body_starts_after_the_attribution(self):
        assert A.parse_entry(self.P)["body"].startswith("It should not astonish us")


class TestAttributionNeverStartsWithPunctuation:
    def test_trailing_heading_period_is_not_kept_on_the_father(self):
        p = ('<p class="txt_courant_ssalinea"><b>Kosmos. </b>'
             '<span class="mev4">O<small>RIGEN</small></span>: '
             'The world is called kosmos in Greek.</p>')
        assert A.parse_entry(p)["father"] == "Origen"

    def test_curly_quotes_are_stripped_too(self):
        p = ('<p class="txt_courant_ssalinea">'
             '<b><small>“</small>Earth” Means All of Humankind. </b>'
             'Hilary of Poitiers: So as not to refer these words to the earth.</p>')
        assert A.parse_entry(p)["father"] == "Hilary of Poitiers"


class TestDeuterocanonBookCodes:
    """書名對到站上 bible_books.code。"""

    def test_the_seven_books_this_volume_covers(self):
        for en, code in (("Sirach", "sir"), ("Wisdom", "wis"), ("Tobit", "tob"),
                         ("Baruch", "bar"), ("Susanna", "sus"),
                         ("Bel and the Dragon", "bel")):
            h = f'<h1 class="chap_tit"><a href="...search={en.replace(" ", "+")}+1%3A1-5">X</a></h1>'
            assert A.parse_passage_ref(h)["book_code"] == code, en

    def test_song_of_the_three_maps_to_the_prayer_of_azariah(self):
        # 兩者在希臘文但以理補篇裡是同一段連續文字（達 3:24–90），站上以一個 aza 涵蓋
        h = ('<h1 class="chap_tit"><a href="...search=Song+of+the+Three+Young+Men+1%3A1-5">X</a></h1>')
        assert A.parse_passage_ref(h)["book_code"] == "aza"

    def test_longer_book_name_wins_over_its_prefix(self):
        # 退路是比對標題文字；"Wisdom" 不可以先吃掉 "Wisdom of Solomon"
        h = '<h1 class="chap_tit">THE SEARCH FOR GOD Wisdom of Solomon 1:1-15</h1>'
        assert A.parse_passage_ref(h)["book_code"] == "wis"
