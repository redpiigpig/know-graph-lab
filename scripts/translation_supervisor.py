#!/usr/bin/env python3
"""Deterministic local-first translation supervisor.

This process never asks an AI model what to run. It uses fixed safety rules:
  - AC power required
  - user must be idle
  - one bounded Ollama batch at a time
  - local drafts are checkpointed with provenance=ollama
  - no build/upload; an online review command must replace local drafts first
"""
from __future__ import annotations

import argparse
import ctypes
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from ctypes import wintypes
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATE_DIR = ROOT / "scripts" / "state"
STATE_PATH = STATE_DIR / "translation_supervisor.json"
LOCK_PATH = STATE_DIR / "translation_supervisor.lock"
STOP_PATH = STATE_DIR / "translation_supervisor.stop"
LOG_PATH = ROOT / "scripts" / "logs" / "translation_supervisor.log"
WORKER_LOG = ROOT / "scripts" / "logs" / "translation_supervisor_worker.log"
JOBS = (
    {
        "id": "sbe",
        "script": "sbe_translate.py",
        "args": ["--local-draft-step"],
    },
    {
        "id": "panikkar",
        "script": "panikkar_auto.py",
        "args": ["--draft-queue-step", "--backend", "ollama"],
    },
)
# Online-review jobs: replace provenance=ollama drafts with Gemini-first quality
# and publish a work once it has no local drafts left. Selected only when there
# is a backlog AND Gemini is reachable (see choose_mode); otherwise we draft.
REVIEW_JOBS = (
    {
        "id": "sbe",
        "script": "sbe_translate.py",
        "args": ["--review-local-step", "--backend", "gemini-first", "--upload"],
    },
    {
        "id": "panikkar",
        "script": "panikkar_auto.py",
        "args": ["--review-queue-step", "--backend", "gemini-first", "--upload"],
    },
)


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.UINT), ("dwTime", wintypes.DWORD)]


class SYSTEM_POWER_STATUS(ctypes.Structure):
    _fields_ = [
        ("ACLineStatus", wintypes.BYTE),
        ("BatteryFlag", wintypes.BYTE),
        ("BatteryLifePercent", wintypes.BYTE),
        ("SystemStatusFlag", wintypes.BYTE),
        ("BatteryLifeTime", wintypes.DWORD),
        ("BatteryFullLifeTime", wintypes.DWORD),
    ]


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def user_idle_seconds() -> float:
    if sys.platform != "win32":
        return 999999.0
    info = LASTINPUTINFO()
    info.cbSize = ctypes.sizeof(info)
    if not ctypes.windll.user32.GetLastInputInfo(ctypes.byref(info)):
        return 0.0
    elapsed_ms = (ctypes.windll.kernel32.GetTickCount() - info.dwTime) & 0xFFFFFFFF
    return elapsed_ms / 1000.0


def on_ac_power() -> bool:
    if sys.platform != "win32":
        return True
    status = SYSTEM_POWER_STATUS()
    if not ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(status)):
        return False
    return status.ACLineStatus == 1


def ollama_ready() -> bool:
    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=3) as response:
            data = json.loads(response.read().decode("utf-8"))
        return any((m.get("name") or "").startswith("qwen2.5:7b")
                   for m in data.get("models", []))
    except (OSError, ValueError, urllib.error.URLError):
        return False


def _gemini_key() -> str:
    try:
        for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if "=" in line and line.split("=", 1)[0].strip() in (
                    "Gemini_API_Key_1", "GEMINI_API_KEY_1"):
                return line.split("=", 1)[1].strip().strip("\"'")
    except OSError:
        pass
    return ""


def gemini_reachable() -> bool:
    """Cheap token-free health check: list one model. 200 → usable; 429/401/
    offline → treat as unavailable so the cycle drafts locally instead."""
    key = _gemini_key()
    if not key:
        return False
    url = ("https://generativelanguage.googleapis.com/v1beta/models?"
           + urllib.parse.urlencode({"key": key, "pageSize": 1}))
    try:
        with urllib.request.urlopen(url, timeout=6) as response:
            return response.status == 200
    except (OSError, urllib.error.URLError, ValueError):
        return False


def choose_mode(drafts_waiting: int, gemini_up: bool) -> str:
    """REVIEW when there's an Ollama-draft backlog and Gemini is reachable (drain
    it to final quality fast); otherwise DRAFT locally (Ollama never 429s)."""
    if drafts_waiting > 0 and gemini_up:
        return "review"
    return "draft"


def process_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def acquire_lock() -> bool:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    if LOCK_PATH.exists():
        try:
            old_pid = int(LOCK_PATH.read_text(encoding="utf-8").strip())
        except (OSError, ValueError):
            old_pid = 0
        if process_alive(old_pid):
            return False
    LOCK_PATH.write_text(str(os.getpid()), encoding="utf-8")
    return True


def release_lock() -> None:
    try:
        if LOCK_PATH.read_text(encoding="utf-8").strip() == str(os.getpid()):
            LOCK_PATH.unlink()
    except OSError:
        pass


def write_state(status: str, **extra) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "pid": os.getpid(),
        "status": status,
        "updated_at": now_iso(),
        "policy": "deterministic-supervisor + bounded Ollama drafts + online review gate",
        **extra,
    }
    tmp = STATE_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, STATE_PATH)


def log(message: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(f"[{now_iso()}] {message}\n")


def conflicting_worker(script_name: str) -> bool:
    if sys.platform != "win32":
        return False
    script = (
        "Get-CimInstance Win32_Process | Where-Object {"
        "$_.ProcessId -ne $PID -and "
        f"$_.CommandLine -match '{script_name}' -and "
        "$_.CommandLine -notmatch 'translation_supervisor.py'} | "
        "Select-Object -ExpandProperty ProcessId"
    )
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    try:
        cp = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", script],
            capture_output=True, text=True, timeout=8, creationflags=flags,
            check=False)
        return any(line.strip().isdigit() for line in cp.stdout.splitlines())
    except (OSError, subprocess.TimeoutExpired):
        return True


def _draft_count(root: Path) -> int:
    count = 0
    for path in root.glob("*/sec*.json"):
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
            count += sum(value == "ollama" for value in (obj.get("engines") or []))
        except (OSError, json.JSONDecodeError):
            continue
    return count


def local_draft_counts() -> dict[str, int]:
    root = ROOT / ".claude" / "skills" / "ebook-collected-works"
    return {
        "panikkar": _draft_count(root / "panikkar_data"),
        "sbe": _draft_count(root / "mueller_data"),
    }


def run_local_step(job: dict, paragraphs: int,
                   timeout_minutes: int) -> tuple[int, int, str]:
    command = [
        sys.executable, "-X", "utf8", str(ROOT / "scripts" / job["script"]),
        *job["args"], "--max-total-paras", str(paragraphs),
    ]
    flags = (getattr(subprocess, "CREATE_NO_WINDOW", 0)
             | getattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0))
    started = time.time()
    try:
        cp = subprocess.run(
            command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=timeout_minutes * 60, creationflags=flags,
            check=False)
        output = (cp.stdout or "") + (cp.stderr or "")
        with WORKER_LOG.open("a", encoding="utf-8") as fh:
            fh.write(f"\n===== {now_iso()} rc={cp.returncode} =====\n{output}")
        matches = re.findall(r"(?:translated|reviewed)=(\d+)", output)
        translated = int(matches[-1]) if matches else 0
        return cp.returncode, translated, f"{time.time() - started:.1f}s"
    except subprocess.TimeoutExpired as exc:
        output = ((exc.stdout or "") if isinstance(exc.stdout, str) else "")
        with WORKER_LOG.open("a", encoding="utf-8") as fh:
            fh.write(f"\n===== {now_iso()} TIMEOUT =====\n{output}")
        return 124, 0, f"timeout>{timeout_minutes}m"


def one_cycle(idle_required: int, paragraphs: int, timeout_minutes: int,
              review_paras: int = 6, dry_run: bool = False) -> str:
    previous: dict = {}
    try:
        previous = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        pass
    idle = int(user_idle_seconds())
    draft_counts = local_draft_counts()
    waiting = sum(draft_counts.values())
    gemini_up = gemini_reachable()
    mode = choose_mode(waiting, gemini_up)             # 'review' | 'draft'
    jobs = REVIEW_JOBS if mode == "review" else JOBS
    batch = review_paras if mode == "review" else paragraphs
    job_index = int(previous.get("next_job_index") or 0) % len(jobs)
    job = jobs[job_index]
    next_job_index = (job_index + 1) % len(jobs)
    common = {
        "mode": mode,
        "idle_seconds": idle,
        "idle_required": idle_required,
        "on_ac_power": on_ac_power(),
        "ollama_ready": ollama_ready(),
        "gemini_reachable": gemini_up,
        "local_drafts_waiting_review": waiting,
        "drafts_by_job": draft_counts,
        "selected_job": job["id"],
        "next_job_index": job_index,
    }
    if idle < idle_required:
        write_state("waiting-for-idle", **common)
        return "waiting-for-idle"
    # Ollama is only needed to DRAFT; a review cycle runs on Gemini.
    if mode == "draft" and not common["ollama_ready"]:
        write_state("waiting-for-ollama", **common)
        return "waiting-for-ollama"
    if conflicting_worker(job["script"]):
        write_state("waiting-for-existing-worker", **common)
        return "waiting-for-existing-worker"
    if dry_run:
        write_state("dry-run-eligible", **common)
        return "dry-run-eligible"

    write_state(f"running-{'online-review' if mode == 'review' else 'local-draft'}",
                batch_paragraphs=batch, **common)
    rc, translated, duration = run_local_step(job, batch, timeout_minutes)
    status = "batch-complete" if rc == 0 else "batch-error"
    current_counts = local_draft_counts()
    write_state(
        status, return_code=rc, translated=translated, duration=duration,
        completed_job=job["id"], next_job_index=next_job_index,
        local_drafts_waiting_review=sum(current_counts.values()),
        drafts_by_job=current_counts, **{
            k: v for k, v in common.items()
            if k not in ("local_drafts_waiting_review", "drafts_by_job",
                         "next_job_index")
        })
    log(f"{status} job={job['id']} rc={rc} translated={translated} duration={duration}")
    return status


def print_status() -> None:
    if not STATE_PATH.exists():
        print(json.dumps({"status": "not-started"}, ensure_ascii=False, indent=2))
        return
    print(STATE_PATH.read_text(encoding="utf-8"))


def main() -> None:
    ap = argparse.ArgumentParser(description="Local-first deterministic translation supervisor")
    ap.add_argument("action", nargs="?", choices=["run", "once", "status", "stop"],
                    default="run")
    ap.add_argument("--interval", type=int, default=60)
    ap.add_argument("--idle-seconds", type=int, default=0)
    ap.add_argument("--step-paras", type=int, default=3)
    ap.add_argument("--review-paras", type=int, default=6,
                    help="paragraphs per online-review batch. Kept SMALL so a "
                         "batch finishes and checkpoints well inside the timeout "
                         "even when cloud engines are throttled (~30-160s/para "
                         "via the NVIDIA/Haiku fallback); a 40-para batch used to "
                         "hit the 45-min timeout (rc=124) and waste the whole run.")
    ap.add_argument("--timeout-minutes", type=int, default=45)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.action == "status":
        print_status()
        return
    if args.action == "stop":
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        STOP_PATH.write_text(now_iso(), encoding="utf-8")
        print("stop requested")
        return
    if not acquire_lock():
        print("translation supervisor is already running", file=sys.stderr)
        raise SystemExit(2)
    try:
        STOP_PATH.unlink(missing_ok=True)
        log(f"started pid={os.getpid()} idle={args.idle_seconds}s step={args.step_paras}")
        while True:
            status = one_cycle(
                max(0, args.idle_seconds), max(1, args.step_paras),
                max(1, args.timeout_minutes), max(1, args.review_paras),
                args.dry_run)
            if args.action == "once":
                print(status)
                break
            if STOP_PATH.exists():
                counts = local_draft_counts()
                write_state("stopped", local_drafts_waiting_review=sum(counts.values()),
                            drafts_by_job=counts)
                STOP_PATH.unlink(missing_ok=True)
                log("stopped by request")
                break
            time.sleep(max(10, args.interval))
    finally:
        release_lock()


if __name__ == "__main__":
    main()
