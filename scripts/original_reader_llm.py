#!/usr/bin/env python3
"""Shared language-model client for the original-language reader builds.

Engine order follows the repository's standing policy: **Gemini first, then
NVIDIA, and Anthropic Haiku only as a last resort.**

The first version of this module was Anthropic-only, inherited from the Hebrew
interlinear.  That was a mistake: the Claude Max account is shared with the
overnight fleet — two dozen jobs at a time — so the Greek gloss and interlinear
layers sat at 429 for seventeen straight hours and produced nothing, while seven
Gemini keys and seven NVIDIA keys went unused.  A reader build has no business
queueing behind the fleet when it does not need that tier at all.

Each tier is tried in turn on every call, and the engine that actually answered
is recorded, so a cache entry always says which model produced it.
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
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))

import translate_ebook_to_zh as engines


GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
GEMINI_MODEL = engines.GEMINI_MODEL

HAIKU_MODELS = ("claude-haiku-4-5-20251001",)
SONNET_MODELS = ("claude-sonnet-5", "claude-sonnet-4-6")
# Kept so callers can still ask for a specific Anthropic tier explicitly; the
# default chain does not start there.
MODEL_CHAINS = {"auto": (), "sonnet": SONNET_MODELS, "haiku": HAIKU_MODELS}

_lock = threading.Lock()
_gemini_index = 0
# When every Gemini key is rate-limited, sweeping all seven on the next call
# only wastes a couple of seconds each time; sit out a while instead.
_gemini_rested_until = 0.0
GEMINI_COOLDOWN = 600
_last_engine = "gemini:" + GEMINI_MODEL
_anthropic_chain: tuple[str, ...] = HAIKU_MODELS
_forced_chain = ""


def select_chain(name: str) -> str:
    """Pick which Anthropic tier the last-resort step uses.

    ``auto`` (the default) keeps the full Gemini -> NVIDIA -> Haiku order.
    Naming a tier explicitly forces it and skips the other engines, which is
    what an upgrade pass over already-glossed units wants.
    """
    global _anthropic_chain, _forced_chain
    if name == "auto":
        _anthropic_chain = HAIKU_MODELS
        _forced_chain = ""
    else:
        _anthropic_chain = MODEL_CHAINS[name]
        _forced_chain = name
    return current_model()


def current_model() -> str:
    return _last_engine


# --------------------------------------------------------------------------
# Anthropic, kept for the last-resort tier
# --------------------------------------------------------------------------

_client_lock = threading.Lock()
_client: anthropic.Anthropic | None = None
_client_mtime = 0.0


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


def _anthropic_call(prompt: str, max_tokens: int) -> str:
    global _client_mtime
    last_error: Exception | None = None
    for model in _anthropic_chain:
        try:
            message = client().messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return "".join(block.text for block in message.content if hasattr(block, "text")).strip()
        except anthropic.AuthenticationError as error:
            with _client_lock:
                _client_mtime = 0.0
            last_error = error
        except (anthropic.NotFoundError, anthropic.RateLimitError,
                anthropic.APIConnectionError, anthropic.APITimeoutError) as error:
            last_error = error
    raise last_error or RuntimeError("no Anthropic tier configured")


# --------------------------------------------------------------------------
# Gemini
# --------------------------------------------------------------------------

def _gemini_call(prompt: str, max_tokens: int) -> str:
    global _gemini_index, _gemini_rested_until
    if not engines.GEMINI_KEYS:
        raise RuntimeError("no Gemini API key")
    if _gemini_rested_until > time.time():
        raise RuntimeError("Gemini resting after every key was rate-limited")
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": max_tokens,
            "responseMimeType": "text/plain",
        },
    }
    url = GEMINI_URL.format(model=GEMINI_MODEL)
    last = "?"
    for _ in range(len(engines.GEMINI_KEYS)):
        with _lock:
            key = engines.GEMINI_KEYS[_gemini_index]
            _gemini_index = (_gemini_index + 1) % len(engines.GEMINI_KEYS)
        try:
            response = requests.post(f"{url}?key={key}", json=body, timeout=180)
        except requests.exceptions.RequestException as error:
            last = f"conn {type(error).__name__}"
            continue
        if response.status_code == 200:
            payload = response.json()
            candidates = payload.get("candidates") or []
            if not candidates:
                last = "empty candidates"
                continue
            parts = candidates[0].get("content", {}).get("parts") or []
            text = "".join(part.get("text", "") for part in parts).strip()
            if text:
                return text
            last = "empty text"
            continue
        last = f"HTTP {response.status_code}"
    with _lock:
        _gemini_rested_until = time.time() + GEMINI_COOLDOWN
    raise RuntimeError(f"Gemini failed on every key (last: {last})")


# --------------------------------------------------------------------------
# NVIDIA
# --------------------------------------------------------------------------

NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
# The house default first, then two that were verified alive when the default
# was not.  A saturated NIM model does not fail fast: it accepts the request and
# never answers, so a model that times out is set aside for a while instead of
# costing every later call another read timeout.  On 2026-08-21
# deepseek-v4-flash-0731 hung on all seven keys while both llama tiers answered
# in under a second.
NVIDIA_MODELS = (
    "deepseek-ai/deepseek-v4-flash-0731",
    "meta/llama-3.1-70b-instruct",
)
# llama-3.1-8b is reachable but not good enough for this work: asked for the
# meaning of ἄγγελος it answered "從而指牧羊人", and θεός came back as
# "神的官司".  A wrong gloss in a vocabulary list is worse than a slow one, so
# the small tier is deliberately not in the chain.
NVIDIA_TIMEOUT = 40
NVIDIA_COOLDOWN = 1800

_nvidia_index = 0
_nvidia_rested: dict[str, float] = {}
_nvidia_preferred = ""


def _nvidia_keys() -> list[str]:
    return list(engines.NVIDIA_KEYS)


def _nvidia_call(prompt: str, max_tokens: int) -> tuple[str, str]:
    """Return (model, text) from the first NVIDIA model that actually answers."""
    global _nvidia_index, _nvidia_preferred
    keys = _nvidia_keys()
    if not keys:
        raise RuntimeError("no NVIDIA API key")
    now = time.time()
    order = [_nvidia_preferred] if _nvidia_preferred else []
    order += [m for m in NVIDIA_MODELS if m != _nvidia_preferred]
    last = "?"
    for model in order:
        if _nvidia_rested.get(model, 0) > now:
            continue
        with _lock:
            key = keys[_nvidia_index % len(keys)]
            _nvidia_index += 1
        try:
            response = requests.post(
                NVIDIA_URL,
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": min(max_tokens, 4000),
                    "temperature": 0.2,
                },
                timeout=NVIDIA_TIMEOUT,
            )
        except requests.exceptions.RequestException as error:
            # A hang means the model is saturated; stop paying for it this run.
            _nvidia_rested[model] = time.time() + NVIDIA_COOLDOWN
            last = f"{model}: {type(error).__name__}"
            continue
        if response.status_code == 200:
            text = response.json()["choices"][0]["message"]["content"]
            _nvidia_preferred = model
            return model, engines._THINK_RE.sub("", text).strip()
        if response.status_code in (404, 410):
            # Retired or not served here; never try it again this run.
            _nvidia_rested[model] = time.time() + 10 ** 9
        last = f"{model}: HTTP {response.status_code}"
    raise RuntimeError(f"NVIDIA failed on every model (last: {last})")


def _nvidia_labelled(prompt: str, max_tokens: int) -> tuple[str, str]:
    model, text = _nvidia_call(prompt, max_tokens)
    return "nvidia:" + model, text


# --------------------------------------------------------------------------
# The chain
# --------------------------------------------------------------------------

def call_model(
    prompt: str,
    max_tokens: int = 16000,
    backoffs: Iterable[int] = (0, 20, 60, 180, 300),
) -> str:
    """Ask the cheapest available engine, in the repository's standing order."""
    global _last_engine

    if _forced_chain:
        text = _anthropic_call(prompt, max_tokens)
        _last_engine = _anthropic_chain[0]
        return text

    # Each tier reports the engine that actually answered, because the NVIDIA
    # tier picks its own model and the cache must record the real one.
    tiers = (
        ("gemini", lambda: ("gemini:" + GEMINI_MODEL, _gemini_call(prompt, max_tokens))),
        ("nvidia", lambda: _nvidia_labelled(prompt, max_tokens)),
        ("anthropic", lambda: (HAIKU_MODELS[0], _anthropic_call(prompt, max_tokens))),
    )

    errors: list[str] = []
    for attempt, wait in enumerate(tuple(backoffs), start=1):
        if wait:
            time.sleep(wait)
        for tier, call in tiers:
            try:
                label, text = call()
            except Exception as error:  # noqa: BLE001 - fall through to the next tier
                errors.append(f"{tier}: {type(error).__name__} {error}")
                continue
            if text:
                _last_engine = label
                return text
        print(
            f"  三個引擎都沒回應（第 {attempt} 輪）：{errors[-3:]}",
            file=sys.stderr,
            flush=True,
        )
    raise RuntimeError(f"所有引擎都失敗：{errors[-3:]}")
