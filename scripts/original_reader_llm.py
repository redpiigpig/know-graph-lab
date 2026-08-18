#!/usr/bin/env python3
"""Shared Anthropic client for the original-language reader builds.

Extracted from ``build_hebrew_interlinear.py`` so the Greek gloss and
interlinear jobs share one rate-limit gate instead of each inventing its own.

The Claude Max account is shared with the interactive session and the overnight
translation fleet, so a 429 means "everyone waits", not "this batch failed".
One shared gate holds every worker until the window reopens, and every caller is
expected to cache its results so a stopped run resumes instead of restarting.
"""

from __future__ import annotations

import json
import os
import sys
import threading
import time
from pathlib import Path
from typing import Iterable

import anthropic


SONNET_MODELS = ("claude-sonnet-5", "claude-sonnet-4-6")
HAIKU_MODELS = ("claude-haiku-4-5-20251001",)
MODEL_CHAINS = {"sonnet": SONNET_MODELS, "haiku": HAIKU_MODELS}

_client_lock = threading.Lock()
_client: anthropic.Anthropic | None = None
_client_mtime = 0.0
_model = SONNET_MODELS[0]
_model_chain = SONNET_MODELS


def select_chain(name: str) -> str:
    global _model, _model_chain
    _model_chain = MODEL_CHAINS[name]
    _model = _model_chain[0]
    return _model


def current_model() -> str:
    return _model


def _credentials_path() -> Path:
    home = os.environ.get("USERPROFILE") or os.environ.get("HOME") or ""
    return Path(home) / ".claude" / ".credentials.json"


def _make_client() -> anthropic.Anthropic:
    common = {"timeout": 600.0, "max_retries": 2}
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        return anthropic.Anthropic(api_key=api_key, **common)
    path = _credentials_path()
    if path.exists():
        creds = json.loads(path.read_text(encoding="utf-8"))
        token = creds.get("claudeAiOauth", {}).get("accessToken", "")
        if token:
            return anthropic.Anthropic(auth_token=token, **common)
    raise RuntimeError("找不到 Anthropic 憑證（ANTHROPIC_API_KEY 或 ~/.claude/.credentials.json）")


def client() -> anthropic.Anthropic:
    """Rebuild whenever Claude Code rolls the OAuth access token."""
    global _client, _client_mtime
    with _client_lock:
        path = _credentials_path()
        if path.exists():
            mtime = path.stat().st_mtime
            if _client is None or mtime > _client_mtime:
                _client = _make_client()
                _client_mtime = mtime
        elif _client is None:
            _client = _make_client()
        return _client


_gate_lock = threading.Lock()
_gate_until = 0.0
_gate_streak = 0
GATE_WAITS = (300, 600, 900, 1200, 1800)


def _wait_for_gate() -> None:
    while True:
        with _gate_lock:
            remaining = _gate_until - time.time()
        if remaining <= 0:
            return
        time.sleep(min(remaining, 30))


def _trip_gate() -> float:
    global _gate_until, _gate_streak
    with _gate_lock:
        wait = GATE_WAITS[min(_gate_streak, len(GATE_WAITS) - 1)]
        _gate_streak += 1
        _gate_until = max(_gate_until, time.time() + wait)
        return wait


def _clear_gate() -> None:
    global _gate_streak
    with _gate_lock:
        _gate_streak = 0


def call_model(
    prompt: str,
    max_tokens: int = 16000,
    backoffs: Iterable[int] = (0, 30, 90, 180, 300, 600),
) -> str:
    global _client_mtime, _model
    backoffs = tuple(backoffs)
    for attempt, wait in enumerate(backoffs, start=1):
        if wait:
            time.sleep(wait)
        _wait_for_gate()
        try:
            message = client().messages.create(
                model=_model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            _clear_gate()
            return "".join(block.text for block in message.content if hasattr(block, "text")).strip()
        except anthropic.NotFoundError:
            with _client_lock:
                index = _model_chain.index(_model) if _model in _model_chain else 0
                if index + 1 < len(_model_chain):
                    _model = _model_chain[index + 1]
                    print(f"  模型改用 {_model}", flush=True)
                else:
                    raise
        except anthropic.AuthenticationError:
            print("  401 — 重讀 credentials.json", file=sys.stderr, flush=True)
            with _client_lock:
                _client_mtime = 0.0
            if attempt >= len(backoffs):
                raise
        except anthropic.RateLimitError:
            held = _trip_gate()
            print(f"  429 額度用盡 — 全體暫停 {held // 60} 分鐘後續跑", file=sys.stderr, flush=True)
            if attempt >= len(backoffs):
                raise
        except (anthropic.APIConnectionError, anthropic.APITimeoutError) as error:
            print(f"  {type(error).__name__} 第 {attempt}/{len(backoffs)} 次", file=sys.stderr, flush=True)
            if attempt >= len(backoffs):
                raise
    raise RuntimeError("重試次數用盡")
