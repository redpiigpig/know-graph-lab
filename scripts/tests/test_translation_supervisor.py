"""Tests for the supervisor's draft-vs-review decision (pure logic)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from translation_supervisor import choose_mode


def test_review_when_backlog_and_gemini_up():
    assert choose_mode(318, True) == "review"


def test_draft_when_gemini_down_even_with_backlog():
    # Gemini 429/offline → keep drafting locally (Ollama never rate-limits)
    assert choose_mode(318, False) == "draft"


def test_draft_when_no_backlog():
    assert choose_mode(0, True) == "draft"
    assert choose_mode(0, False) == "draft"
