# -*- coding: utf-8 -*-
"""英文版 ACCS EPUB 解析的純函式測試。片段全部取自實際的
ACCS_Jeremiah_Lamentations.epub，不是手編的。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from accs_epub import (parse_chapter, parse_entry, parse_passage_ref,
                       parse_subheading, unsmallcaps)

H1 = ('<h1 class="chap_tit"><span><a id="page_12"/><a class="renvlnk" id="R_12"/>'
      'JEREMIAH’S INSPIRATION AND\xa0ISRAEL’S APOSTASY<br/>'
      '<a class="url" href="https://www.biblegateway.com/passage/'
      '?search=Jeremiah+2%3A1-8&amp;version=RSV">JEREMIAH 2:1-8</a></span></h1>')

H2 = '<h2 class="int_niv1">2:1-4 <i>Israel Faithful in\xa0Its\xa0Youth</i></h2>'

P_OVERVIEW = ('<p class="txt_courant_ssalinea"><b>O<small>VERVIEW:</small></b> '
              'The Word of the Lord coming to the prophets defends the eternity '
              'of Christ (A<small>THANASIUS</small>).</p>')

P_COMMENT = ('<p class="txt_courant_ssalinea"><b>P<small>ROPHETIC </small>'
             'I<small>NSPIRATION. </small></b>A<small>THANASIUS: </small>'
             'The prophets say, “And the Word of the Lord came to me.” '
             'D<small>ISCOURSES </small>A<small>GAINST THE </small>'
             'A<small>RIANS</small> 2.18.32.</p>')


def test_unsmallcaps_restores_normal_case():
    # 直接去標籤會得到「A THANASIUS」，必須先併回來
    assert unsmallcaps('A<small>THANASIUS: </small>') == 'Athanasius: '
    assert unsmallcaps('G<small>OD’S </small>W<small>AYS </small>') == 'God’s Ways '


def test_passage_ref_from_biblegateway_link():
    ref = parse_passage_ref(H1)
    assert ref == {'book_code': 'jer', 'chapter': 2, 'verse_start': 1,
                   'verse_end': 8, 'passage': 'Jeremiah 2:1-8'}


def test_passage_ref_falls_back_to_title_text():
    no_link = '<h1 class="chap_tit"><span>SOMETHING<br/>LAMENTATIONS 3:22</span></h1>'
    ref = parse_passage_ref(no_link)
    assert ref['book_code'] == 'lam'
    assert (ref['chapter'], ref['verse_start'], ref['verse_end']) == (3, 22, 22)


def test_subheading_gives_verse_span_and_title():
    assert parse_subheading(H2) == {'chapter': 2, 'verse_start': 1, 'verse_end': 4,
                                    'title': 'Israel Faithful in Its Youth'}


def test_overview_entry():
    rec = parse_entry(P_OVERVIEW)
    assert rec['kind'] == 'overview'
    assert rec['father'] == ''
    assert rec['body'].startswith('The Word of the Lord')


def test_comment_splits_heading_father_body_and_work():
    rec = parse_entry(P_COMMENT)
    assert rec['kind'] == 'comment'
    assert rec['heading'] == 'Prophetic Inspiration'
    assert rec['father'] == 'Athanasius'
    assert rec['work'] == 'Discourses Against the Arians 2.18.32'
    assert rec['body'].startswith('The prophets say')
    # 出處不可留在正文裡
    assert 'Discourses' not in rec['body']


def test_parse_chapter_scopes_entries_to_the_subheading():
    doc = f'<html><body><div class="chap">{H1}{P_OVERVIEW}{H2}{P_COMMENT}</div></body></html>'
    recs = parse_chapter(doc)
    assert [r['kind'] for r in recs] == ['overview', 'comment']
    # 總論掛在 h1 的整段範圍
    assert (recs[0]['verse_start'], recs[0]['verse_end']) == (1, 8)
    # 引文掛在 h2 的小節範圍
    assert (recs[1]['verse_start'], recs[1]['verse_end']) == (1, 4)
    assert all(r['book_code'] == 'jer' and r['chapter'] == 2 for r in recs)
