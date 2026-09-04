"""ACCS Vol 9（箴言‧傳道書‧雅歌）那本 Calibre 拆檔式 EPUB 的解析。

跟 Vol 12 的包裝完全不同：整本被 Calibre 打散成三千多個 index_split_NNN.html，
正文只在前十四檔，class 換成 blockNN / text_N。好處是欄位是明講的，不必像
parse_entry 那樣靠正則猜署名與作品名的邊界。

這裡釘住三個實際踩過的坑：
  1. 註腳是 <sup> 包的數字，不先拿掉就會把編號黏進正文
  2. 概述的教父名各自成 span，用空白接起來會變成「not yet ( Ambrose )」
  3. 段落範圍可以跨章（4:9–5:1）
"""
import accs_epub as A


COMMENT_P = (
    '<p class="block_41">'
    '<span lang="en" class="text_5">The Doves on the Water Indicate Baptism.</span>'
    '<span lang="en" class="text_"> Theodoret of Cyr</span>'
    '<span lang="en">: “His eyes like doves on pools of water,” once again here by '
    'mention of the “eyes.”<sup class="calibre6">3</sup>'
    '<sup class="calibre6"><a title="2322" href="index_split_2335.html#note_2322" '
    'class="noteref">2322</a>8</sup> Hence the bride says so. </span>'
    '<span lang="en" class="text_">Commentary on the Song of Songs</span>'
    '<span lang="en"> 5.3</span></p>'
)

OVERVIEW_P = (
    '<p class="block_32">'
    '<span lang="en" class="text_5">Overview:</span>'
    '<span lang="en"> The Word came leaping over the mountains, present already but not yet (</span>'
    '<span lang="en" class="text_">Cyril of Alexandria, Ambrose</span>'
    '<span lang="en">) and over every rebellious power (</span>'
    '<span lang="en" class="text_">Gregory of Nyssa</span>'
    '<span lang="en">).</span></p>'
)


class TestParseRefCalibre:
    def test_verse_range(self):
        r = A.parse_ref_calibre('<h2 class="block_33">2:8–17 SONGS AT THE BREAK OF SPRING</h2>')
        assert (r['chapter'], r['verse_start'], r['verse_end']) == (2, 8, 17)
        assert r['title'] == 'SONGS AT THE BREAK OF SPRING'

    def test_single_verse(self):
        r = A.parse_ref_calibre('<h3 class="block_40">5:12 The Dove’s Eyes</h3>')
        assert (r['chapter'], r['verse_start'], r['verse_end']) == (5, 12, 12)

    def test_range_crossing_a_chapter(self):
        # 4:9–5:1：chapter 記起始章，end_chapter 另外留著
        r = A.parse_ref_calibre('<h2 class="block_33">4:9–5:1 THE ENCLOSED GARDEN</h2>')
        assert (r['chapter'], r['verse_start'], r['verse_end']) == (4, 9, 1)
        assert r['end_chapter'] == 5

    def test_not_a_ref(self):
        assert A.parse_ref_calibre('<h2 class="block_33">Bibliography</h2>') is None


class TestParseEntryCalibre:
    def test_comment_fields(self):
        r = A.parse_entry_calibre(COMMENT_P)
        assert r['kind'] == 'comment'
        assert r['heading'] == 'The Doves on the Water Indicate Baptism'
        assert r['father'] == 'Theodoret of Cyr'
        assert r['work'].startswith('Commentary on the Song of Songs')

    def test_footnote_digits_never_reach_the_body(self):
        # 🚨 不先拿掉 <sup> 就會得到「…the “eyes.”32322 8 Hence…」
        body = A.parse_entry_calibre(COMMENT_P)['body']
        assert '2322' not in body
        assert 'eyes.” Hence the bride says so' in body

    def test_work_title_is_not_left_in_the_body(self):
        r = A.parse_entry_calibre(COMMENT_P)
        assert 'Commentary on the Song of Songs' not in r['body']

    def test_overview(self):
        r = A.parse_entry_calibre(OVERVIEW_P)
        assert r['kind'] == 'overview'
        assert r['heading'] == 'Overview'
        assert r['father'] == '' and r['work'] == ''

    def test_overview_keeps_cited_fathers_inline_without_stray_spaces(self):
        # 教父名各自成 span，接起來不可以變成「not yet ( Cyril …)」
        body = A.parse_entry_calibre(OVERVIEW_P)['body']
        assert '(Cyril of Alexandria, Ambrose)' in body
        assert '(Gregory of Nyssa)' in body
        assert '( ' not in body and ' )' not in body


class TestParseChapterCalibre:
    def test_entries_inherit_the_nearest_heading(self):
        html = (
            '<body class="calibre">'
            '<h2 class="block_33">2:8–17 SONGS AT THE BREAK OF SPRING</h2>'
            + OVERVIEW_P +
            '<h3 class="block_40">5:12 The Dove’s Eyes</h3>'
            + COMMENT_P +
            '</body>'
        )
        recs = A.parse_chapter_calibre(html, 'sng')
        assert [r['kind'] for r in recs] == ['overview', 'comment']
        assert all(r['book_code'] == 'sng' for r in recs)
        # 概述掛在段落層 2:8–17，引文掛在其下的逐節層 5:12
        assert (recs[0]['chapter'], recs[0]['verse_start'], recs[0]['verse_end']) == (2, 8, 17)
        assert (recs[1]['chapter'], recs[1]['verse_start'], recs[1]['verse_end']) == (5, 12, 12)
        # pericope_order 每遇一個標題就進位，兩者不可同號
        assert recs[0]['pericope_order'] != recs[1]['pericope_order']

    def test_entries_before_any_heading_are_dropped(self):
        recs = A.parse_chapter_calibre('<body>' + COMMENT_P + '</body>', 'sng')
        assert recs == []
