#!/usr/bin/env python3
"""Eight-lane deterministic cloud translation supervisor.

Four Gemini keys and four NVIDIA keys are pinned one-per-process. Literature
review entries are assigned by stable SHA-256 sharding, so lanes never write the
same entry. No model decides scheduling.
"""
from __future__ import annotations

import argparse
import ctypes
import json
import os
import signal
import subprocess
import sys
import time
from ctypes import wintypes
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATE_DIR = ROOT / "scripts" / "state"
STATE_PATH = STATE_DIR / "translation_cloud_supervisor.json"
LOCK_PATH = STATE_DIR / "translation_cloud_supervisor.lock"
STOP_PATH = STATE_DIR / "translation_cloud_supervisor.stop"
LOG_DIR = ROOT / "scripts" / "logs" / "cloud-lanes"
CLAIMS_PATH = STATE_DIR / "translation_lane_claims.json"
PROJECT = "genesis-philosophy"
SHARD_COUNT = 7


class SYSTEM_POWER_STATUS(ctypes.Structure):
    _fields_ = [
        ("ACLineStatus", wintypes.BYTE), ("BatteryFlag", wintypes.BYTE),
        ("BatteryLifePercent", wintypes.BYTE), ("SystemStatusFlag", wintypes.BYTE),
        ("BatteryLifeTime", wintypes.DWORD), ("BatteryFullLifeTime", wintypes.DWORD),
    ]


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def on_ac_power() -> bool:
    if sys.platform != "win32":
        return True
    status = SYSTEM_POWER_STATUS()
    return bool(ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(status))
                and status.ACLineStatus == 1)


def process_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return pid > 0
    except OSError:
        return False


def acquire_lock() -> bool:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    if LOCK_PATH.exists():
        try:
            pid = int(LOCK_PATH.read_text(encoding="utf-8").strip())
        except (OSError, ValueError):
            pid = 0
        if process_alive(pid):
            return False
    LOCK_PATH.write_text(str(os.getpid()), encoding="utf-8")
    return True


def release_lock() -> None:
    try:
        if LOCK_PATH.read_text(encoding="utf-8").strip() == str(os.getpid()):
            LOCK_PATH.unlink()
    except OSError:
        pass


def lanes() -> list[dict]:
    result = []
    for idx in range(3):
        result.append({
            "id": f"gemini-{idx + 1}", "provider": "gemini",
            "slot": idx + 1, "shard": idx, "engine": "gemini-only",
            "kind": "translate",
        })
    for idx in range(4):
        result.append({
            "id": f"nvidia-{idx + 1}", "provider": "nvidia",
            "slot": idx + 1, "shard": idx + 3, "engine": "nvidia",
            "kind": "translate",
        })
    result.append({
        "id": "gemini-4-reviewer", "provider": "gemini",
        "slot": 4, "shard": None, "engine": "gemini-review",
        "kind": "review",
    })
    return result


GEMINI_PROBE = ROOT / "scripts" / "gemini_probe.py"
# 免費 Gemini 乾掉時，lane 原本就只是空轉：起來、四把 key 全 429、退出、冷卻 30 分，
# 整夜什麼都沒翻（2026-08-24 實測一晚只推進 203 段）。Sonnet 也不是答案——Max 上的
# Sonnet 額度撐不住長跑，掛整晚照樣被 429 打死；同一個帳號的 Haiku 卻能連續工作一整天
# （2026-08-25 實測 16 小時 +3,694 段）。所以 Gemini 乾掉就改用 Haiku（user 2026-08-26）。
# 探測結果快取 15 分鐘，免得每次 spawn 都多打一次 API。
_gemini_probe_cache = {"at": 0.0, "alive": True}


def gemini_alive(ttl: float = 900.0) -> bool:
    now = time.time()
    if now - _gemini_probe_cache["at"] < ttl:
        return _gemini_probe_cache["alive"]
    try:
        rc = subprocess.run(
            [sys.executable, "-X", "utf8", str(GEMINI_PROBE)],
            cwd=ROOT, capture_output=True, timeout=180).returncode
        alive = rc == 0
    except Exception:  # noqa: BLE001  探測本身失敗不該讓 lane 停擺
        alive = False
    _gemini_probe_cache.update(at=now, alive=alive)
    return alive


def engine_for(lane: dict) -> str:
    """Gemini 初譯 lane 在額度乾掉時降級到 Haiku。審查 lane 與 NVIDIA lane 不動。"""
    if (lane["kind"] == "translate" and lane["provider"] == "gemini"
            and not gemini_alive()):
        return "haiku"
    return lane["engine"]


def command_for(lane: dict, project: str) -> list[str]:
    if lane["kind"] == "review":
        return [
            sys.executable, "-X", "utf8",
            str(ROOT / "scripts" / "lit_review_quality_reviewer.py"),
            "--project", project, "--pace", "1",
        ]
    return [
        sys.executable, "-X", "utf8", str(ROOT / "scripts" / "ingest_lit_review.py"),
        "--fetch-fulltext", "--project", project, "--resume",
        "--engine", engine_for(lane), "--pace", "1",
        "--shard-index", str(lane["shard"]), "--shard-count", str(SHARD_COUNT),
    ]


# 回傳 pid（找到）／0（確定沒有）／-1（查不出來，例如逾時）。-1 絕不可當成 0：
# 那等於「查不到就再開一個」，而 Get-CimInstance Win32_Process 全表掃描在機器忙的時候
# 很容易超過逾時（2026-08-26 實測 shard 0 與 shard 1 各長出兩個 worker：我手動掛的
# Haiku 一個、supervisor 沒認出來又開的 Gemini 一個，兩個同時翻同一批段落）。
# 順手把 WMI 查詢用 Name 收窄到 python*，讓它在 WMI 端就過濾掉幾百個無關程序。
def find_existing_lane(lane: dict, project: str) -> int:
    if sys.platform != "win32":
        return 0
    if lane["kind"] == "review":
        matcher = "$_.CommandLine -match 'lit_review_quality_reviewer.py'"
    else:
        matcher = (
            "$_.CommandLine -match 'ingest_lit_review.py' -and "
            f"$_.CommandLine -match '--shard-index {lane['shard']}' -and "
            f"$_.CommandLine -match '--shard-count {SHARD_COUNT}'")
    script = (
        "Get-CimInstance Win32_Process -Filter \"Name LIKE '%python%'\" | Where-Object {"
        "$_.ProcessId -ne $PID -and "
        f"$_.CommandLine -match '--project {project}' -and "
        f"{matcher}"
        "} | Select-Object -First 1 -ExpandProperty ProcessId"
    )
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    try:
        cp = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", script],
            capture_output=True, text=True, timeout=45, creationflags=flags,
            check=False)
        if cp.returncode != 0:
            return -1
        return next((int(x) for x in cp.stdout.split() if x.isdigit()), 0)
    except (OSError, subprocess.TimeoutExpired):
        return -1


def write_state(status: str, lane_states: dict[str, dict], **extra) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1, "pid": os.getpid(), "status": status,
        "updated_at": now_iso(), "project": extra.pop("project", PROJECT),
        "shard_count": SHARD_COUNT, "lanes": lane_states, **extra,
    }
    tmp = STATE_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, STATE_PATH)


def terminate_workers(runtime: dict[str, dict]) -> None:
    for item in runtime.values():
        proc = item.get("process")
        if proc and proc.poll() is None:
            proc.terminate()
        handle = item.get("log_handle")
        if handle:
            handle.close()


def active_claims() -> dict[str, dict]:
    try:
        claims = json.loads(CLAIMS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    now = time.time()
    return {
        lane: claim for lane, claim in claims.items()
        if float(claim.get("expires_at_epoch") or 0) > now
    }


def stop_lane(item: dict, state: dict) -> None:
    proc = item.pop("process", None)
    pid = int(state.get("pid") or 0)
    if proc and proc.poll() is None:
        proc.terminate()
    elif process_alive(pid):
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            pass
    handle = item.pop("log_handle", None)
    if handle:
        handle.close()
    state["pid"] = 0


def main() -> None:
    ap = argparse.ArgumentParser(description="8-lane cloud translation supervisor")
    ap.add_argument("action", nargs="?", choices=["run", "status", "stop", "plan"],
                    default="run")
    ap.add_argument("--project", default=PROJECT)
    ap.add_argument("--cooldown-seconds", type=int, default=1800)
    args = ap.parse_args()
    if args.action == "status":
        print(STATE_PATH.read_text(encoding="utf-8") if STATE_PATH.exists()
              else json.dumps({"status": "not-started"}))
        return
    if args.action == "stop":
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        STOP_PATH.write_text(now_iso(), encoding="utf-8")
        print("stop requested")
        return
    if args.action == "plan":
        for lane in lanes():
            print(f"{lane['id']}: shard={lane['shard']}/{SHARD_COUNT} "
                  f"engine={lane['engine']} key-slot={lane['slot']}")
        return
    if not acquire_lock():
        raise SystemExit("cloud supervisor already running")

    runtime: dict[str, dict] = {}
    lane_states: dict[str, dict] = {}
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    STOP_PATH.unlink(missing_ok=True)
    try:
        while True:
            if STOP_PATH.exists():
                terminate_workers(runtime)
                write_state("stopped", lane_states, project=args.project)
                STOP_PATH.unlink(missing_ok=True)
                break
            ac = on_ac_power()
            claims = active_claims()
            claude_active = any(
                str(claim.get("owner") or "").lower().startswith("claude")
                for claim in claims.values())
            for lane in lanes():
                lane_id = lane["id"]
                item = runtime.setdefault(lane_id, {})
                state = lane_states.setdefault(lane_id, {
                    **lane, "pid": 0, "state": "waiting", "next_restart_at": 0,
                })
                proc = item.get("process")
                pid = int(state.get("pid") or 0)
                claim = claims.get(lane_id)
                reviewer_paused = lane["kind"] == "review" and claude_active
                if claim or reviewer_paused:
                    stop_lane(item, state)
                    state.update({
                        "state": "claimed-by-claude",
                        "claim": claim or {
                            "owner": "claude-quality-interlock",
                            "note": "paused while Claude owns another lane",
                        },
                        "next_restart_at": 0,
                    })
                    continue
                state.pop("claim", None)
                alive = proc.poll() is None if proc else process_alive(pid)
                if alive:
                    state["state"] = "running"
                    continue
                if proc:
                    rc = proc.poll()
                    state["last_exit_code"] = rc
                    state["last_exit_at"] = now_iso()
                    state["next_restart_at"] = time.time() + max(60, args.cooldown_seconds)
                    handle = item.pop("log_handle", None)
                    if handle:
                        handle.close()
                    item.pop("process", None)
                    state["pid"] = 0
                if time.time() < float(state.get("next_restart_at") or 0):
                    state["state"] = "cooldown"
                    continue
                existing = find_existing_lane(lane, args.project)
                if existing < 0:
                    # 查不出來就這輪不開，等下一輪再查——寧可少跑一輪，也不要開出
                    # 第二個寫同一 shard 的 worker。
                    state["state"] = "probe-failed"
                    continue
                if existing:
                    state.update({"pid": existing, "state": "running-existing"})
                    continue
                env = os.environ.copy()
                if lane["provider"] == "gemini":
                    env["KGL_GEMINI_SLOT"] = str(lane["slot"])
                else:
                    env["KGL_NVIDIA_SLOT"] = str(lane["slot"])
                log_path = LOG_DIR / f"{args.project}_{lane_id}.log"
                handle = log_path.open("a", encoding="utf-8")
                used_engine = engine_for(lane)
                handle.write(f"\n===== {now_iso()} START kind={lane['kind']} "
                             f"shard={lane['shard']} engine={used_engine} =====\n")
                handle.flush()
                flags = (getattr(subprocess, "CREATE_NO_WINDOW", 0)
                         | getattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0))
                child = subprocess.Popen(
                    command_for(lane, args.project), cwd=ROOT, env=env,
                    stdout=handle, stderr=subprocess.STDOUT, text=True,
                    creationflags=flags)
                item.update({"process": child, "log_handle": handle})
                state.update({
                    "pid": child.pid, "state": "running",
                    "started_at": now_iso(), "log": str(log_path),
                    "engine_in_use": used_engine,
                })
            running = sum(s.get("state", "").startswith("running")
                          for s in lane_states.values())
            write_state("running" if running else "waiting", lane_states,
                        project=args.project, on_ac_power=ac,
                        running_lanes=running, claims=claims)
            time.sleep(10)
    finally:
        terminate_workers(runtime)
        release_lock()


if __name__ == "__main__":
    main()
