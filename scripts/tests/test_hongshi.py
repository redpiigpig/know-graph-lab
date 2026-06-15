# -*- coding: utf-8 -*-
"""Test-first contract for scripts/hongshi.py (印順學派與弘誓研究資料 pipeline).

Pure functions only — no network. Covers the parsing/cleanup logic that actually
caused bugs while building the collection:
  - magazine PDF filename has THREE variants → one issue number
  - EDM old issues use .htm (not .html), across multiple folders
  - Cloudflare challenge / nav / footer-stub pages must be rejected as non-content
  - PDF text-layer sufficiency drives the OCR decision
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import hongshi as h  # noqa: E402


# ── magazine issue number (3 filename patterns) ─────────────────────────────────
def test_magazine_issue_standard_hyphenated():
    assert h.magazine_issue("admin/upload/file/hongshi-magazine-187-20240215.pdf") == 187


def test_magazine_issue_no_hyphen_after_magazine():
    # the variant that produced gaps 188-190
    assert h.magazine_issue("admin/upload/file/magazine190-20240815.pdf") == 190


def test_magazine_issue_number_first_hongshi_roc_date():
    # the variant for 177-180 (number-first, ROC date)
    assert h.magazine_issue("admin/upload/file/180hongshi-1111216.pdf") == 180


def test_magazine_issue_canonical_local_name_and_part():
    assert h.magazine_issue("弘誓雙月刊-188.pdf") == 188
    assert h.magazine_issue("弘誓雙月刊-200-p2.pdf") == 200


def test_magazine_issue_none_for_unrelated():
    assert h.magazine_issue("常住115年度行事曆-信眾版150315-v2.pdf") is None


def test_magazine_ad_date():
    assert h.magazine_ad_date("hongshi-magazine-187-20240215.pdf") == "2024/02"
    assert h.magazine_ad_date("180hongshi-1111216.pdf") == ""   # ROC date not AD


# ── EDM issue number (.htm vs .html, folder-scoped) ─────────────────────────────
def test_edm_issue_recent_html():
    assert h.edm_issue("https://www.hongshi.org.tw/EDM/542.html") == 542


def test_edm_issue_old_htm():
    # the bug: old issues use .htm (no 'l') — these were ALL missed
    assert h.edm_issue("/userfiles/epaper/hongshi%20pic2/99.htm") == 99
    assert h.edm_issue("/userfiles/epaper/hongshi pic/98.htm") == 98


def test_edm_issue_ignores_non_edm_numbered_pages():
    # teacher-page.php?n=2 etc must NOT be treated as an EDM issue
    assert h.edm_issue("https://hongshi.org.tw/teacher-page.php?n=2") is None
    assert h.edm_issue("https://hongshi.org.tw/alumni.php?n=288") is None


# ── content validity (challenge / nav / footer-stub rejection) ──────────────────
def test_rejects_cloudflare_challenge_capture():
    cap = "www.hongshi.org.tw\n正在執行安全驗證\n\n此網站使用安全服務抵禦惡意機器人"
    assert h.is_challenge_page(cap)
    assert not h.is_real_content(cap)


def test_rejects_contact_footer_stub():
    stub = "與我們聯繫   電　話：886-3-4987325  傳　真：886-3-4986123  意 見"
    assert not h.is_real_content(stub)


def test_accepts_genuine_long_content():
    body = "115.1.18\n■上午，本院舉行歲末感恩祈福法會……" + "佛" * 500
    assert h.is_real_content(body)
    assert not h.is_challenge_page(body)


def test_parse_edm_meta():
    text = "542 2026年5月17日 本 期 目 錄 ■ 學團日誌 ■ 賀！本院學眾光持法師升等副教授"
    date, title = h.parse_edm_meta(text)
    assert date == "2026/05/17"
    assert title and "學團日誌" in title


# ── OCR decision ────────────────────────────────────────────────────────────────
def test_pdf_text_sufficient_true_for_text_layer():
    assert h.pdf_text_sufficient("x" * 6000, n_pages=20)   # 300/pg ≥ 60


def test_pdf_text_sufficient_false_for_scanned():
    assert not h.pdf_text_sufficient("封面", n_pages=40)    # ~0/pg → needs OCR
    assert not h.pdf_text_sufficient("anything", n_pages=0)
