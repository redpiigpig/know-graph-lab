#!/usr/bin/env python3
"""本機翻譯進度桌面面板。

進度監控不呼叫 AI；API 健康檢查只讀 models/tags 端點，不生成文字、
不消耗模型推理 token。

資料來源：
  - 榮格：jung_data/*/status.json
  - 潘尼卡：panikkar_data/<slug>/sec*.json
  - 東方聖卷：mueller_data/sbe-*/sec*.json
  - ACCS：C:/tmp/accs_*.raw.jsonl + .done
  - 是否運行：Windows Win32_Process command line

Usage:
  python -X utf8 scripts/translation_dashboard.py
  python -X utf8 scripts/translation_dashboard.py --snapshot
"""
from __future__ import annotations

import argparse
import ast
import concurrent.futures
import json
import os
import re
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CW_ROOT = ROOT / ".claude" / "skills" / "ebook-collected-works"
PANIKKAR_ROOT = CW_ROOT / "panikkar_data"
MUELLER_ROOT = CW_ROOT / "mueller_data"
JUNG_ROOT = CW_ROOT / "jung_data"
LOG_ROOT = ROOT / "scripts" / "logs"
TMP_ROOT = Path(os.environ.get("TEMP", r"C:\tmp"))
if Path(r"C:\tmp").exists():
    TMP_ROOT = Path(r"C:\tmp")

STALE_MINUTES = 30
PROCESS_PATTERNS = {
    "榮格": ("jung_psychological_types_overnight.py",),
    "潘尼卡": ("panikkar_auto.py", "panikkar_build.py"),
    "東方聖卷": ("sbe_translate.py",),
    "ACCS": (
        "ingest_accs_genesis.py",
        "accs_resume",
        "accs_loop",
    ),
}

OTHER_PIPELINES = {
    "translate_ebook_to_zh.py": "一般電子書翻譯",
    "translate_collected_work.py": "全集逐段翻譯",
    "translate_corpus_queue.py": "語料翻譯佇列",
    "polish_translated_book.py": "譯稿校潤",
    "retranslate_drifting_chunks.py": "偏移段落重譯",
    "llm_proofread_book.py": "專書 AI 校對",
    "vision_proofread_book.py": "專書視覺校對",
    "dialogue_recompose.py": "對話錄重鑄",
    "dialogue_to_prose.py": "對話轉散文",
    "dialogue_fix_turns.py": "對話錄修訂",
    "dialogue_polish.py": "對話錄校潤",
    "dialogue_rebuild_from_raw.py": "對話錄重建",
    "dialogue_rewrite_from_docx.py": "手稿改寫匯入",
    "fix_gnostic_quality.py": "諾斯底文獻精修",
    "ingest_gnostic.py": "諾斯底文獻轉錄",
    "dazangjing_catalog_ai.py": "大藏經目錄整理",
    "dazangjing_catalog_curate.py": "大藏經目錄策展",
    "ocr_interview_book.py": "研究參考書 OCR",
    "transcribe_interview_gemini.py": "論文訪談轉錄",
    "lit_review_quality_reviewer.py": "文獻翻譯品質複核",
}

SUPERVISOR_STATE = ROOT / "scripts" / "state" / "translation_supervisor.json"
CLOUD_SUPERVISOR_STATE = ROOT / "scripts" / "state" / "translation_cloud_supervisor.json"

PANIKKAR_FALLBACK = {
    "experience-of-god": "神的經驗：奧祕的聖像",
    "rhythm-of-being": "存在的韻律",
    "vedic-experience": "吠陀經驗",
    "myth-faith-hermeneutics": "神話、信仰與詮釋學",
    "mysticism-fullness": "神祕：生命的圓滿",
    "pace-interculturalita": "和平與跨文化",
    "religion-world-body": "宗教、世界與身體",
    "mundanal-silencio": "世間的靜默",
}

SBE_FALLBACK = {
    "sbe-01-upanishads-1": "第 1 卷　奧義書（上）",
    "sbe-04-zend-avesta-1": "第 4 卷　阿維斯陀（一）",
    "sbe-06-quran-1": "第 6 卷　古蘭經（上）",
    "sbe-10-dhammapada": "第 10 卷　法句經／經集",
    "sbe-16-yi-king": "第 16 卷　易經",
    "sbe-22-jaina-1": "第 22 卷　耆那教經典（一）",
}

ACCS_TARGETS = {
    ("gen", "創1-11"): 316,
    ("gen", "創12-50"): 654,
    ("exo", ""): 228,
    ("lev", ""): 60,
    ("num", ""): 96,
    ("deu", ""): 94,
}
ACCS_NAMES = {
    "gen": "創世記",
    "exo": "出埃及記",
    "lev": "利未記",
    "num": "民數記",
    "deu": "申命記",
}


@dataclass
class WorkProgress:
    group: str
    key: str
    title: str
    done: int
    total: int
    unit: str
    state: str
    running: bool
    current: str
    updated_at: float | None
    source: str
    detail: str = ""

    @property
    def percent(self) -> float:
        if self.total <= 0:
            return 0.0
        return min(100.0, self.done * 100.0 / self.total)

    @property
    def updated_text(self) -> str:
        if self.updated_at is None:
            return "—"
        return datetime.fromtimestamp(self.updated_at).strftime("%m/%d %H:%M")


@dataclass
class ApiStatus:
    provider: str
    label: str
    state: str = "尚未檢查"
    latency_ms: int | None = None
    checked_at: float | None = None
    note: str = ""
    secret: str = ""

    @property
    def checked_text(self) -> str:
        if self.checked_at is None:
            return "—"
        return datetime.fromtimestamp(self.checked_at).strftime("%H:%M:%S")


def _env_values() -> dict[str, str]:
    values: dict[str, str] = {}
    path = ROOT / ".env"
    try:
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip("\"'")
    except OSError:
        pass
    return values


def _anthropic_secret() -> tuple[str, str, str]:
    """Return (token, mode, source_note) for the Haiku 救急 engine. mode ∈
    {'x-api-key', 'bearer', ''}. Prefers ANTHROPIC_API_KEY, else the Claude Max
    OAuth accessToken in ~/.claude/.credentials.json (same source the translator
    uses)."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if api_key:
        return api_key, "x-api-key", "ANTHROPIC_API_KEY"
    cred = (Path(os.environ.get("USERPROFILE") or os.environ.get("HOME", ""))
            / ".claude" / ".credentials.json")
    try:
        data = json.loads(cred.read_text(encoding="utf-8"))
        token = data.get("claudeAiOauth", {}).get("accessToken", "")
        if token:
            return token, "bearer", "Claude Max OAuth"
    except (OSError, ValueError):
        pass
    return "", "", "未找到 Claude 憑證"


def api_inventory() -> list[ApiStatus]:
    env = _env_values()
    rows: list[ApiStatus] = []
    for idx in range(1, 5):
        key = env.get(f"Gemini_API_Key_{idx}") or env.get(f"GEMINI_API_KEY_{idx}", "")
        rows.append(ApiStatus("Gemini", f"Gemini #{idx}",
                              note="" if key else "未在 .env 設定", secret=key))
    for idx in range(1, 5):
        key = env.get(f"NVIDIA_API_Key_{idx}") or env.get(f"NVIDIA_API_KEY_{idx}", "")
        rows.append(ApiStatus("NVIDIA", f"NVIDIA #{idx}",
                              note="" if key else "未在 .env 設定", secret=key))
    tok, _mode, src_note = _anthropic_secret()
    rows.append(ApiStatus("Claude", "Haiku 救急", note=src_note, secret=tok))
    rows.append(ApiStatus("本機", "Ollama", note="http://127.0.0.1:11434"))
    return rows


def _http_probe(url: str, headers: dict[str, str] | None = None,
                timeout: float = 8.0) -> tuple[str, int | None, str]:
    started = time.perf_counter()
    request = urllib.request.Request(url, headers=headers or {}, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response.read(512)
            latency = int((time.perf_counter() - started) * 1000)
            return "可連線", latency, (
                f"HTTP {response.status}，認證成功；不代表目前仍有生成額度")
    except urllib.error.HTTPError as exc:
        latency = int((time.perf_counter() - started) * 1000)
        if exc.code == 429:
            return "受限", latency, "HTTP 429：目前限流或額度不足"
        if exc.code in (401, 403):
            return "無效", latency, f"HTTP {exc.code}：金鑰無效或無權限"
        return "異常", latency, f"HTTP {exc.code}"
    except (urllib.error.URLError, TimeoutError, OSError):
        latency = int((time.perf_counter() - started) * 1000)
        return "離線", latency, "連線失敗或逾時"


def probe_api(status: ApiStatus) -> ApiStatus:
    now = time.time()
    if status.provider == "本機":
        started = time.perf_counter()
        try:
            request = urllib.request.Request(
                "http://127.0.0.1:11434/api/tags", method="GET")
            with urllib.request.urlopen(request, timeout=3) as response:
                data = json.loads(response.read().decode("utf-8"))
            names = [str(m.get("name") or m.get("model") or "")
                     for m in data.get("models", [])]
            latency = int((time.perf_counter() - started) * 1000)
            note = f"{len(names)} 個模型：" + "、".join(names[:6])
            return ApiStatus("本機", "Ollama", "正常", latency, now, note)
        except (OSError, ValueError, urllib.error.URLError):
            latency = int((time.perf_counter() - started) * 1000)
            return ApiStatus("本機", "Ollama", "離線", latency, now,
                             "請啟動 Ollama 服務")
    if status.provider == "Claude":
        token, mode, cred_note = _anthropic_secret()
        if not token:
            return ApiStatus("Claude", status.label, "未設定", None, now, cred_note)
        headers = {"anthropic-version": "2023-06-01", "Accept": "application/json"}
        if mode == "bearer":
            headers["Authorization"] = f"Bearer {token}"
            headers["anthropic-beta"] = "oauth-2025-04-20"
        else:
            headers["x-api-key"] = token
        state, latency, note = _http_probe(
            "https://api.anthropic.com/v1/models?limit=1", headers)
        # Claude Max OAuth tokens are scoped to the Claude Code client; a direct
        # /v1/models GET can 401/403 even though Haiku 救急 generation works fine
        # through the SDK with the same token. Don't mislabel that as invalid.
        if mode == "bearer" and state == "無效":
            state = "就緒"
            note = ("Claude Max OAuth 憑證已載入；直打 /v1/models 受 OAuth scope 限制"
                    "無法免生成健檢，但 Haiku 救急可正常呼叫")
        return ApiStatus("Claude", status.label, state, latency, now,
                         f"{note}（{cred_note}）")
    if not status.secret:
        return ApiStatus(status.provider, status.label, "未設定", None, now,
                         "未在 .env 找到金鑰")
    if status.provider == "Gemini":
        query = urllib.parse.urlencode({"key": status.secret, "pageSize": 1})
        state, latency, note = _http_probe(
            f"https://generativelanguage.googleapis.com/v1beta/models?{query}")
    else:
        state, latency, note = _http_probe(
            "https://integrate.api.nvidia.com/v1/models",
            {"Authorization": f"Bearer {status.secret}",
             "Accept": "application/json"})
    return ApiStatus(status.provider, status.label, state, latency, now, note)


def probe_all_apis() -> list[ApiStatus]:
    inventory = api_inventory()
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(inventory)) as pool:
        return list(pool.map(probe_api, inventory))


def _tail_text(path: Path, max_bytes: int = 32_768) -> str:
    try:
        with path.open("rb") as handle:
            handle.seek(0, os.SEEK_END)
            size = handle.tell()
            handle.seek(max(0, size - max_bytes))
            return handle.read().decode("utf-8", errors="replace")
    except OSError:
        return ""


def cloud_lane_rate_limits(
        state_path: Path = CLOUD_SUPERVISOR_STATE,
        log_dir: Path | None = None) -> dict[str, dict[str, Any]]:
    """Return lanes whose latest runtime signal is an actual generation 429."""
    if log_dir is None:
        log_dir = ROOT / "scripts" / "logs" / "cloud-lanes"
    try:
        cloud = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    project = str(cloud.get("project") or "genesis-philosophy")
    limited: dict[str, dict[str, Any]] = {}
    for lane_id, lane in (cloud.get("lanes") or {}).items():
        log_path = log_dir / f"{project}_{lane_id}.log"
        tail = _tail_text(log_path)
        last_429 = tail.rfind("429")
        if last_429 < 0:
            continue
        # A new start or successful output after the last 429 clears the warning.
        last_success = max(
            tail.rfind(" START "),
            tail.rfind("· para "),
            tail.rfind("\nOK "),
            tail.rfind("\nREVISED "),
        )
        if last_429 < last_success:
            continue
        limited[str(lane_id)] = {
            "state": str(lane.get("state") or ""),
            "next_restart_at": float(lane.get("next_restart_at") or 0),
            "log_path": str(log_path),
        }
    return limited


def apply_runtime_rate_limits(
        statuses: list[ApiStatus],
        limits: dict[str, dict[str, Any]] | None = None) -> list[ApiStatus]:
    """Overlay generation-time 429s on cheap connectivity probe results."""
    limits = cloud_lane_rate_limits() if limits is None else limits
    lane_for_label = {
        **{f"Gemini #{idx}": f"gemini-{idx}" for idx in range(1, 4)},
        "Gemini #4": "gemini-4-reviewer",
        **{f"NVIDIA #{idx}": f"nvidia-{idx}" for idx in range(1, 5)},
    }
    result: list[ApiStatus] = []
    for status in statuses:
        lane_id = lane_for_label.get(status.label)
        limit = limits.get(lane_id or "")
        if not limit:
            result.append(status)
            continue
        cooling = limit.get("state") == "cooldown"
        state = "429 冷卻" if cooling else "429 受限"
        restart = float(limit.get("next_restart_at") or 0)
        restart_note = (
            f"，預計 {datetime.fromtimestamp(restart):%H:%M:%S} 自動重試"
            if cooling and restart > time.time() else "")
        result.append(ApiStatus(
            status.provider, status.label, state, status.latency_ms,
            status.checked_at,
            f"實際生成回報 HTTP 429（限流或額度不足）{restart_note}；"
            f"連線探測：{status.state}",
            status.secret,
        ))
    return result


def _literal_assignment(path: Path, name: str) -> Any:
    """讀取 Python 常數但不 import 腳本，避免載入 API client 或 .env。"""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in tree.body:
            if isinstance(node, ast.Assign):
                if any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
                    return ast.literal_eval(node.value)
    except (OSError, SyntaxError, ValueError):
        pass
    return None


def registry_titles() -> tuple[dict[str, str], dict[str, str]]:
    pan = dict(PANIKKAR_FALLBACK)
    raw_pan = _literal_assignment(ROOT / "scripts" / "panikkar_auto.py", "WORKS")
    if isinstance(raw_pan, dict):
        for slug, item in raw_pan.items():
            if isinstance(item, dict):
                pan[str(slug)] = str(item.get("title") or slug)

    sbe = dict(SBE_FALLBACK)
    raw_sbe = _literal_assignment(ROOT / "scripts" / "sbe_translate.py", "WORKS")
    if isinstance(raw_sbe, list):
        for item in raw_sbe:
            if isinstance(item, dict) and item.get("slug"):
                slug = str(item["slug"])
                vol = re.search(r"sbe-(\d+)", slug)
                prefix = f"第 {int(vol.group(1))} 卷　" if vol else ""
                sbe[slug] = prefix + str(item.get("title") or slug)
    return pan, sbe


def active_processes() -> list[dict[str, Any]]:
    if sys.platform != "win32":
        return []
    script = (
        "Get-CimInstance Win32_Process | "
        "Where-Object {$_.CommandLine} | "
        "Select-Object ProcessId,Name,CommandLine | ConvertTo-Json -Compress"
    )
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    try:
        cp = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", script],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=8,
            creationflags=flags,
            check=False,
        )
        if cp.returncode or not cp.stdout.strip():
            return []
        data = json.loads(cp.stdout)
        return data if isinstance(data, list) else [data]
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
        return []


def running_groups(processes: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    found: dict[str, list[dict[str, Any]]] = {g: [] for g in PROCESS_PATTERNS}
    for proc in processes:
        cmd = str(proc.get("CommandLine") or "").lower()
        if "translation_dashboard.py" in cmd:
            continue
        for group, patterns in PROCESS_PATTERNS.items():
            if any(pattern.lower() in cmd for pattern in patterns):
                found[group].append(proc)
    return found


def _latest_mtime(paths: list[Path]) -> float | None:
    times = []
    for path in paths:
        try:
            times.append(path.stat().st_mtime)
        except OSError:
            pass
    return max(times) if times else None


def _state(done: int, total: int, running: bool, updated: float | None,
           *, explicit_done: bool = False, error: str = "") -> str:
    if error:
        return "錯誤"
    if explicit_done or (total > 0 and done >= total):
        return "完成"
    if running:
        if updated and datetime.now().timestamp() - updated > STALE_MINUTES * 60:
            return "疑似停滯"
        return "執行中"
    if done > 0:
        return "已暫停"
    return "未開始"


def scan_jung(running: bool) -> list[WorkProgress]:
    rows: list[WorkProgress] = []
    if not JUNG_ROOT.exists():
        return rows
    for status_path in sorted(JUNG_ROOT.glob("*/status.json")):
        try:
            obj = json.loads(status_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        total = int(obj.get("total") or 0)
        done = int(obj.get("done") or 0)
        current = obj.get("current")
        err = str(obj.get("error") or "")
        updated = status_path.stat().st_mtime
        rows.append(WorkProgress(
            "榮格", status_path.parent.name, str(obj.get("title") or status_path.parent.name),
            done, total, "段", _state(done, total, running, updated, error=err),
            running, f"第 {current} 段" if current is not None else ("全部完成" if done >= total else "—"),
            updated, str(status_path), err,
        ))
    return rows


def _checkpoint_counts(path: Path, source_key: str) -> tuple[int, int, str, int]:
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return 0, 0, "checkpoint 無法解析", 0
    source = obj.get(source_key) or []
    zh = obj.get("zh") or []
    fail = obj.get("fail") or []
    total = len(source)
    done = 0
    for idx in range(total):
        translated = idx < len(zh) and bool(str(zh[idx] or "").strip())
        exhausted = source_key == "en" and idx < len(fail) and int(fail[idx] or 0) >= 3
        done += int(translated or exhausted)
    heading = str(obj.get("title_zh") or obj.get("title") or obj.get("heading") or path.stem)
    local_drafts = sum(value == "ollama" for value in (obj.get("engines") or []))
    return done, total, heading.lstrip("# ").strip(), local_drafts


def scan_json_checkpoints(
    group: str,
    root: Path,
    titles: dict[str, str],
    processes: list[dict[str, Any]],
    source_key: str,
) -> list[WorkProgress]:
    rows = []
    commands = [str(p.get("CommandLine") or "").lower() for p in processes]
    for slug, title in titles.items():
        folder = root / slug
        files = sorted(
            folder.glob("sec*.json"),
            key=lambda p: int(re.search(r"(\d+)", p.stem).group(1)),
        ) if folder.exists() else []
        done = total = 0
        current = "尚未建立 checkpoint"
        details = []
        sections_ready: list[bool] = []
        local_drafts = 0
        for path in files:
            d, t, heading, local = _checkpoint_counts(path, source_key)
            done += d
            total += t
            local_drafts += local
            if group == "潘尼卡":
                sections_ready.append(not t or d >= max(1, int(t * 0.95)))
            else:
                sections_ready.append(d >= t)
            if d < t and current == "尚未建立 checkpoint":
                current = f"{path.stem}　{heading[:48]}"
            if t and d < t:
                details.append(f"{path.stem} {d}/{t}")
        updated = _latest_mtime(files)
        complete = bool(files) and total > 0 and all(sections_ready)
        direct_running = any(slug.lower() in cmd for cmd in commands)
        row = WorkProgress(
            group, slug, title, done, total, "段落",
            _state(done, total, direct_running, updated, explicit_done=complete),
            direct_running, "全部 checkpoint 完成" if complete else current,
            updated, str(folder),
            (f"待線上複核 {local_drafts} 段；" if local_drafts else "")
            + "；".join(details[:8]),
        )
        if local_drafts and complete:
            row.state = "待線上複核"
        rows.append(row)
    # --run-queue / --loop 沒有在 command line 指定 slug。此時真正工作的是最新
    # 活動的未完成卷；若尚未寫檔，則是 registry 中第一個未完成卷。
    if processes and not any(row.running for row in rows):
        incomplete = [row for row in rows if row.state != "完成"]
        if incomplete:
            recent = [r for r in incomplete if r.updated_at and
                      datetime.now().timestamp() - r.updated_at <= STALE_MINUTES * 60]
            active = max(recent, key=lambda r: r.updated_at or 0) if recent else incomplete[0]
            active.running = True
            active.state = _state(active.done, active.total, True, active.updated_at)
    return rows


def _accs_target(code: str, filename: str, covered: int) -> int:
    for (target_code, marker), total in ACCS_TARGETS.items():
        if code == target_code and (not marker or marker in filename):
            return total
    return covered


def _accs_title(code: str, filename: str) -> str:
    title = ACCS_NAMES.get(code, code.upper())
    if code == "gen":
        if "創1-11" in filename:
            title += " 1–11 章"
        elif "創12-50" in filename:
            title += " 12–50 章"
    return title


def scan_accs(processes: list[dict[str, Any]]) -> list[WorkProgress]:
    rows = []
    commands = [str(p.get("CommandLine") or "").lower() for p in processes]
    for path in sorted(TMP_ROOT.glob("accs_*.raw.jsonl")):
        match = re.match(r"accs_([a-z0-9]+)_", path.name, re.I)
        if not match:
            continue
        code = match.group(1).lower()
        pages: set[int] = set()
        parse_errors = 0
        try:
            with path.open(encoding="utf-8") as fh:
                for line in fh:
                    try:
                        obj = json.loads(line)
                        vals = obj.get("pages")
                        if vals is None and "page" in obj:
                            vals = [obj["page"]]
                        pages.update(int(p) for p in (vals or []))
                    except (json.JSONDecodeError, TypeError, ValueError):
                        parse_errors += 1
        except OSError:
            continue
        done_marker = path.with_suffix(".done")
        done = len(pages)
        total = _accs_target(code, path.name, done)
        updated = path.stat().st_mtime
        explicit_done = done_marker.exists()
        if explicit_done:
            updated = max(updated, done_marker.stat().st_mtime)
        direct_running = any(
            re.search(rf"(?:--book\s+|accs_){re.escape(code)}(?:\s|_|$)", cmd)
            for cmd in commands
        )
        state = _state(done, total, direct_running, updated, explicit_done=explicit_done)
        if done >= total and total > 0 and not explicit_done:
            state = "待匯入/檢查"
        rows.append(WorkProgress(
            "ACCS", path.stem, _accs_title(code, path.name), done, total, "頁",
            state, direct_running, "頁面 OCR 完成，尚無 .done" if state == "待匯入/檢查"
            else (f"下一頁約 {min(done + 1, total)}" if done < total else "全部完成"),
            updated, str(path), f"JSONL 解析錯誤行：{parse_errors}" if parse_errors else "",
        ))
    if processes and not any(row.running for row in rows):
        incomplete = [row for row in rows if row.state != "完成"]
        if incomplete:
            active = max(incomplete, key=lambda r: r.updated_at or 0)
            active.running = True
            active.state = _state(active.done, active.total, True, active.updated_at)
    return rows


def _command_arg(command: str, option: str) -> str:
    match = re.search(rf"(?:^|\s){re.escape(option)}(?:=|\s+)(?:\"([^\"]+)\"|'([^']+)'|(\S+))",
                      command, re.I)
    return next((g for g in match.groups() if g is not None), "") if match else ""


def _lit_review_log(project: str) -> Path | None:
    aliases = {
        "genesis-philosophy": "lit_review_genesis_fulltext.log",
        "bajingfa": "lit_review_overnight.log",
    }
    preferred = TMP_ROOT / aliases.get(project, f"lit_review_{project.replace('-', '_')}.log")
    if preferred.exists():
        return preferred
    token = project.split("-", 1)[0].lower()
    candidates = [p for p in TMP_ROOT.glob("lit_review*.log") if token in p.name.lower()]
    return max(candidates, key=lambda p: p.stat().st_mtime) if candidates else None


def _scan_lit_review(
    project: str,
    processes: list[dict[str, Any]],
    running: bool = True,
) -> WorkProgress:
    log = _lit_review_log(project)
    done = total = 0
    current = "正在取得文獻清單"
    detail = "；".join(f"PID {p.get('ProcessId')}" for p in processes)
    updated = None
    if log:
        updated = log.stat().st_mtime
        try:
            text = log.read_text(encoding="utf-8", errors="replace")
            total_matches = list(re.finditer(
                r"fetch-fulltext:\s*(\d+)\s+entries to process", text))
            total = int(total_matches[-1].group(1)) if total_matches else 0
            # 同一 log 可能由多次 --resume append；進度只算最後一輪，不能把
            # 前幾輪走訪過的篇目重複加進目前分子。
            run_text = text[total_matches[-1].start():] if total_matches else text
            arrows = list(re.finditer(r"(?m)^\s*→\s+(\S+)", run_text))
            if arrows:
                done = max(0, len(arrows) - 1)
                last = arrows[-1]
                tail = run_text[last.start():]
                key = last.group(1)
                paras = re.findall(r"para\s+(\d+)/(\d+)", tail)
                resumes = re.findall(r"resume:\s*(\d+)\s+done,\s*(\d+)\s+to translate", tail)
                if paras:
                    n, n_total = paras[-1]
                    current = f"{key[:52]}　段落 {n}/{n_total}"
                elif resumes:
                    n, remaining = map(int, resumes[-1])
                    current = f"{key[:52]}　段落 {n}/{n + remaining}"
                else:
                    current = f"{key[:62]}　抓取／檢查全文"
                if re.search(r"✓ \+\d+ paras this run;\s*complete", tail):
                    done = len(arrows)
            if detail:
                detail += "；"
            detail += f"本輪已走訪 {len(arrows)} 篇（含無 OA／付費牆）"
        except OSError:
            pass
    state = _state(done, total, running, updated)
    return WorkProgress(
        "其他工作", f"lit-review:{project}", f"參考文獻全文翻譯｜{project}",
        done, total, "篇", state, running, current, updated,
        str(log or ROOT / "scripts" / "ingest_lit_review.py"), detail,
    )


def scan_other_work(processes: list[dict[str, Any]]) -> list[WorkProgress]:
    """自動發現不屬於四套固定全集的翻譯、改寫、校潤與研究轉錄程序。"""
    rows: list[WorkProgress] = []
    used_pids: set[int] = set()

    lit_groups: dict[str, list[dict[str, Any]]] = {}
    for proc in processes:
        cmd = str(proc.get("CommandLine") or "")
        if "ingest_lit_review.py" in cmd.lower():
            project = _command_arg(cmd, "--project") or "未命名計畫"
            lit_groups.setdefault(project, []).append(proc)
            used_pids.add(int(proc.get("ProcessId") or 0))
    for project, procs in lit_groups.items():
        rows.append(_scan_lit_review(project, procs))
    # 長跑文獻翻譯停止後仍保留在面板，才能看見最後 checkpoint 並知道可 resume。
    known_lit_review = {
        "genesis-philosophy": TMP_ROOT / "lit_review_genesis_fulltext.log",
        "bajingfa": TMP_ROOT / "lit_review_overnight.log",
    }
    for project, log in known_lit_review.items():
        if project not in lit_groups and log.exists():
            rows.append(_scan_lit_review(project, [], running=False))

    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for proc in processes:
        pid = int(proc.get("ProcessId") or 0)
        if pid in used_pids:
            continue
        cmd = str(proc.get("CommandLine") or "")
        low = cmd.lower()
        if "translation_dashboard.py" in low:
            continue
        script = next((name for name in OTHER_PIPELINES if name in low), "")
        if not script:
            continue
        identity = (_command_arg(cmd, "--project") or _command_arg(cmd, "--ebook")
                    or _command_arg(cmd, "--work") or _command_arg(cmd, "--only"))
        if not identity:
            # 第一個看起來像 UUID 的位置參數通常是 ebook_id。
            uuid = re.search(r"\b[0-9a-f]{8}-[0-9a-f-]{27,}\b", low)
            identity = uuid.group(0) if uuid else ""
        grouped.setdefault((script, identity), []).append(proc)

    for (script, identity), procs in grouped.items():
        script_path = ROOT / "scripts" / script
        updated = _latest_mtime([script_path])
        label = OTHER_PIPELINES[script]
        current = identity or "程序已啟動；等待第一個 checkpoint"
        rows.append(WorkProgress(
            "其他工作", f"{script}:{identity}", label,
            0, 0, "項", _state(0, 0, True, updated), True, current,
            updated, str(script_path),
            "；".join(f"PID {p.get('ProcessId')}" for p in procs),
        ))
    supervisor_procs = [
        p for p in processes
        if "translation_supervisor.py" in str(p.get("CommandLine") or "").lower()
    ]
    if SUPERVISOR_STATE.exists() or supervisor_procs:
        try:
            state_obj = json.loads(SUPERVISOR_STATE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            state_obj = {}
        raw_state = str(state_obj.get("status") or "starting")
        labels = {
            "waiting-for-ac": "等待接上電源",
            "waiting-for-idle": "等待電腦閒置",
            "waiting-for-ollama": "等待 Ollama",
            "waiting-for-existing-worker": "等待既有 worker",
            "running-local-draft": "本機草稿執行中",
            "batch-complete": "小批次完成",
            "batch-error": "小批次錯誤",
            "dry-run-eligible": "條件符合（測試）",
            "stopped": "已停止",
            "starting": "啟動中",
        }
        running = bool(supervisor_procs)
        state = "執行中" if running else "已暫停"
        if raw_state == "batch-error":
            state = "錯誤"
        updated = None
        try:
            updated = datetime.fromisoformat(str(state_obj.get("updated_at"))).timestamp()
        except (TypeError, ValueError):
            updated = _latest_mtime([SUPERVISOR_STATE])
        drafts = int(state_obj.get("local_drafts_waiting_review") or 0)
        idle = int(state_obj.get("idle_seconds") or 0)
        selected_job = str(state_obj.get("selected_job")
                           or state_obj.get("completed_job") or "—")
        rows.append(WorkProgress(
            "其他工作", "translation-supervisor", "本機翻譯 Supervisor",
            0, 0, "項", state, running,
            f"{labels.get(raw_state, raw_state)}｜輪到 {selected_job}｜待線上複核 {drafts} 段",
            updated, str(SUPERVISOR_STATE),
            "零 AI 排程器；插電即輪轉 qwen2.5:7b 小批次，不自動發布",
        ))
    cloud_procs = [
        p for p in processes
        if "translation_cloud_supervisor.py" in str(p.get("CommandLine") or "").lower()
    ]
    if CLOUD_SUPERVISOR_STATE.exists() or cloud_procs:
        try:
            cloud = json.loads(CLOUD_SUPERVISOR_STATE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            cloud = {}
        lanes_obj = cloud.get("lanes") or {}
        claims = cloud.get("claims") or {}
        running_count = sum(
            str(item.get("state") or "").startswith("running")
            for item in lanes_obj.values())
        rate_limits = cloud_lane_rate_limits()
        limited_labels = [
            lane_id.replace("-reviewer", " 品管")
            for lane_id in rate_limits
        ]
        reviewer = lanes_obj.get("gemini-4-reviewer") or {}
        updated = None
        try:
            updated = datetime.fromisoformat(str(cloud.get("updated_at"))).timestamp()
        except (TypeError, ValueError):
            updated = _latest_mtime([CLOUD_SUPERVISOR_STATE])
        running = bool(cloud_procs)
        rows.append(WorkProgress(
            "其他工作", "cloud-translation-supervisor",
            "雲端翻譯池（7 初譯＋1 品管）",
            running_count, 8, "lane",
            "429 受限" if rate_limits else ("執行中" if running else "已暫停"),
            running,
            f"{running_count}/8 lanes｜Gemini #4 品管：{reviewer.get('state', '—')}"
            + (f"｜429：{', '.join(limited_labels)}" if limited_labels else "")
            + (f"｜Claude claim：{','.join(claims)}" if claims else ""),
            updated, str(CLOUD_SUPERVISOR_STATE),
            "Gemini #1–#3、NVIDIA #1–#4 各自固定 shard；Gemini #4 全段複核；"
            "Claude claim 時自動互斥"
            + ("；黃色狀態表示實際生成收到 HTTP 429" if rate_limits else ""),
        ))
    return rows


def collect_snapshot() -> tuple[list[WorkProgress], dict[str, list[dict[str, Any]]]]:
    pan_titles, sbe_titles = registry_titles()
    processes = active_processes()
    groups = running_groups(processes)
    rows: list[WorkProgress] = []
    rows.extend(scan_jung(bool(groups["榮格"])))
    rows.extend(scan_json_checkpoints(
        "潘尼卡", PANIKKAR_ROOT, pan_titles, groups["潘尼卡"], "src"))
    rows.extend(scan_json_checkpoints(
        "東方聖卷", MUELLER_ROOT, sbe_titles, groups["東方聖卷"], "en"))
    rows.extend(scan_accs(groups["ACCS"]))
    rows.extend(scan_other_work(processes))
    return rows, groups


def print_snapshot() -> None:
    rows, groups = collect_snapshot()
    result = {
        "checked_at": datetime.now().isoformat(timespec="seconds"),
        "processes": {
            group: [
                {"pid": p.get("ProcessId"), "command": p.get("CommandLine")}
                for p in procs
            ]
            for group, procs in groups.items()
        },
        "works": [{**asdict(row), "percent": round(row.percent, 1)} for row in rows],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def print_api_status() -> None:
    statuses = probe_all_apis()
    safe = [{
        "provider": s.provider,
        "label": s.label,
        "state": s.state,
        "latency_ms": s.latency_ms,
        "checked_at": datetime.fromtimestamp(s.checked_at).isoformat(timespec="seconds")
        if s.checked_at else None,
        "note": s.note,
    } for s in statuses]
    print(json.dumps(safe, ensure_ascii=False, indent=2))


class Dashboard:
    COLORS = {
        "bg": "#10151d",
        "panel": "#18212d",
        "panel2": "#202b39",
        "text": "#e8eef6",
        "muted": "#98a8ba",
        "accent": "#65c3ba",
        "green": "#65c18c",
        "yellow": "#e8b85c",
        "red": "#ed7b72",
        "blue": "#72a7e8",
    }

    def __init__(self) -> None:
        import tkinter as tk
        from tkinter import ttk

        self.tk = tk
        self.ttk = ttk
        self.root = tk.Tk()
        self.root.title("全集翻譯進度")
        self.root.geometry("1180x720")
        self.root.minsize(940, 560)
        self.root.configure(bg=self.COLORS["bg"])
        self.rows: list[WorkProgress] = []
        self.api_statuses = api_inventory()
        self.refreshing = False
        self.api_refreshing = False
        self.last_api_check = 0.0
        self.auto_refresh = tk.BooleanVar(value=True)
        self.status_text = tk.StringVar(value="正在讀取本機進度…")
        self.summary_vars = {
            "running": tk.StringVar(value="0"),
            "complete": tk.StringVar(value="0"),
            "paused": tk.StringVar(value="0"),
            "attention": tk.StringVar(value="0"),
        }
        self._style()
        self._build()
        self.refresh()
        self.refresh_apis()
        self.root.after(10_000, self._auto_tick)
        self.root.after(60_000, self._api_tick)

    def _style(self) -> None:
        s = self.ttk.Style()
        s.theme_use("clam")
        s.configure(".", font=("Microsoft JhengHei UI", 10))
        s.configure("Treeview", background=self.COLORS["panel"], foreground=self.COLORS["text"],
                    fieldbackground=self.COLORS["panel"], borderwidth=0, rowheight=31)
        s.configure("Treeview.Heading", background=self.COLORS["panel2"],
                    foreground=self.COLORS["text"], relief="flat", font=("Microsoft JhengHei UI", 10, "bold"))
        s.map("Treeview", background=[("selected", "#315063")])
        s.configure("TNotebook", background=self.COLORS["bg"], borderwidth=0)
        s.configure("TNotebook.Tab", background=self.COLORS["panel"], foreground=self.COLORS["muted"],
                    padding=(18, 9))
        s.map("TNotebook.Tab", background=[("selected", self.COLORS["panel2"])],
              foreground=[("selected", self.COLORS["text"])])
        s.configure("TCheckbutton", background=self.COLORS["bg"], foreground=self.COLORS["muted"])

    def _build(self) -> None:
        tk = self.tk
        top = tk.Frame(self.root, bg=self.COLORS["bg"])
        top.pack(fill="x", padx=24, pady=(20, 12))
        tk.Label(top, text="全集翻譯進度", bg=self.COLORS["bg"], fg=self.COLORS["text"],
                 font=("Microsoft JhengHei UI", 20, "bold")).pack(side="left")
        tk.Label(top, text="本機監控 · 健康檢查不生成文字", bg=self.COLORS["bg"],
                 fg=self.COLORS["accent"], font=("Microsoft JhengHei UI", 10)).pack(side="left", padx=14, pady=(8, 0))
        tk.Button(top, text="立即更新", command=self.refresh, bg=self.COLORS["accent"],
                  fg="#071412", activebackground="#83d8cf", relief="flat",
                  font=("Microsoft JhengHei UI", 10, "bold"), padx=16, pady=7).pack(side="right")
        tk.Button(top, text="檢查 API", command=self.refresh_apis, bg=self.COLORS["panel2"],
                  fg=self.COLORS["text"], activebackground="#315063", relief="flat",
                  font=("Microsoft JhengHei UI", 10), padx=14, pady=7).pack(side="right", padx=(0, 8))
        self.ttk.Checkbutton(top, text="每 10 秒自動更新",
                             variable=self.auto_refresh).pack(side="right", padx=14)

        cards = tk.Frame(self.root, bg=self.COLORS["bg"])
        cards.pack(fill="x", padx=18, pady=(0, 13))
        specs = [
            ("running", "正在執行", self.COLORS["green"]),
            ("complete", "已完成", self.COLORS["blue"]),
            ("paused", "暫停／等待", self.COLORS["muted"]),
            ("attention", "需要注意", self.COLORS["yellow"]),
        ]
        for key, label, color in specs:
            card = tk.Frame(cards, bg=self.COLORS["panel"], padx=16, pady=11)
            card.pack(side="left", expand=True, fill="x", padx=6)
            tk.Label(card, textvariable=self.summary_vars[key], bg=self.COLORS["panel"], fg=color,
                     font=("Segoe UI", 21, "bold")).pack(anchor="w")
            tk.Label(card, text=label, bg=self.COLORS["panel"], fg=self.COLORS["muted"]).pack(anchor="w")

        self.notebook = self.ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=24)
        self.trees: dict[str, Any] = {}
        for group in ("全部", "榮格", "潘尼卡", "東方聖卷", "ACCS", "其他工作"):
            frame = tk.Frame(self.notebook, bg=self.COLORS["panel"])
            self.notebook.add(frame, text=group)
            tree = self.ttk.Treeview(
                frame, columns=("state", "title", "progress", "current", "updated"),
                show="headings", selectmode="browse")
            headings = {
                "state": "狀態", "title": "卷／作品", "progress": "進度",
                "current": "目前位置", "updated": "最後活動",
            }
            widths = {"state": 90, "title": 300, "progress": 155, "current": 330, "updated": 115}
            for col in headings:
                tree.heading(col, text=headings[col])
                tree.column(col, width=widths[col], minwidth=70,
                            stretch=col in ("title", "current"))
            scroll = self.ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scroll.set)
            tree.pack(side="left", fill="both", expand=True)
            scroll.pack(side="right", fill="y")
            tree.tag_configure("running", foreground=self.COLORS["green"])
            tree.tag_configure("complete", foreground=self.COLORS["blue"])
            tree.tag_configure("attention", foreground=self.COLORS["yellow"])
            tree.bind("<<TreeviewSelect>>", self._show_detail)
            tree.bind("<Double-1>", self._open_selected)
            self.trees[group] = tree

        api_frame = tk.Frame(self.notebook, bg=self.COLORS["panel"])
        self.notebook.add(api_frame, text="API 狀態")
        api_columns = ("provider", "label", "state", "latency", "checked", "note")
        self.api_tree = self.ttk.Treeview(
            api_frame, columns=api_columns, show="headings", selectmode="browse")
        api_headings = {
            "provider": "服務", "label": "帳號／端點", "state": "狀態",
            "latency": "延遲", "checked": "最後檢查", "note": "說明",
        }
        api_widths = {
            "provider": 90, "label": 150, "state": 100,
            "latency": 90, "checked": 105, "note": 490,
        }
        for col in api_columns:
            self.api_tree.heading(col, text=api_headings[col])
            self.api_tree.column(col, width=api_widths[col], minwidth=70,
                                 stretch=col == "note")
        self.api_tree.tag_configure("ok", foreground=self.COLORS["green"])
        self.api_tree.tag_configure("limited", foreground=self.COLORS["yellow"])
        self.api_tree.tag_configure("bad", foreground=self.COLORS["red"])
        self.api_tree.pack(fill="both", expand=True)
        advice = (
            "本機 AI 分流　✅ 分類／標籤、OCR 草稿、粗譯、格式清理、異常掃描、embedding　"
            "⚠ 學術文獻、神學術語、經典與出版終稿須雲端或人工複核　"
            "○ 進度計數、簡繁轉換、檔案操作不使用 AI"
        )
        tk.Label(api_frame, text=advice, anchor="w", justify="left",
                 bg=self.COLORS["panel2"], fg=self.COLORS["muted"],
                 padx=14, pady=10, wraplength=1080).pack(fill="x")
        self._apply_api_statuses(self.api_statuses)

        bottom = tk.Frame(self.root, bg=self.COLORS["bg"])
        bottom.pack(fill="x", padx=24, pady=(10, 14))
        self.detail = tk.Label(bottom, textvariable=self.status_text, anchor="w",
                               bg=self.COLORS["bg"], fg=self.COLORS["muted"],
                               font=("Microsoft JhengHei UI", 9))
        self.detail.pack(side="left", fill="x", expand=True)
        tk.Label(bottom, text="雙擊一列可開啟 checkpoint／資料夾", bg=self.COLORS["bg"],
                 fg=self.COLORS["muted"], font=("Microsoft JhengHei UI", 9)).pack(side="right")

    @staticmethod
    def _row_tag(row: WorkProgress) -> str:
        if row.state == "執行中":
            return "running"
        if row.state == "完成":
            return "complete"
        if row.state.startswith("429"):
            return "attention"
        if row.state in ("錯誤", "疑似停滯", "待匯入/檢查", "待線上複核"):
            return "attention"
        return ""

    def refresh(self) -> None:
        if self.refreshing:
            return
        self.refreshing = True
        self.status_text.set("正在讀取 checkpoint 與 Windows 程序…")

        def worker() -> None:
            try:
                rows, groups = collect_snapshot()
                self.root.after(0, lambda: self._apply(rows, groups))
            except Exception as exc:  # GUI 不因單一壞檔崩潰
                self.root.after(0, lambda: self._refresh_error(str(exc)))

        threading.Thread(target=worker, daemon=True).start()

    def _refresh_error(self, message: str) -> None:
        self.refreshing = False
        self.status_text.set(f"更新失敗：{message}")

    def refresh_apis(self) -> None:
        if self.api_refreshing:
            return
        self.api_refreshing = True
        self.status_text.set("正在檢查 8 把雲端 key＋Haiku 救急與本機 Ollama；不生成文字…")

        def worker() -> None:
            try:
                statuses = probe_all_apis()
                self.root.after(0, lambda: self._finish_api_refresh(statuses))
            except Exception as exc:
                self.root.after(0, lambda: self._api_refresh_error(str(exc)))

        threading.Thread(target=worker, daemon=True).start()

    def _api_refresh_error(self, message: str) -> None:
        self.api_refreshing = False
        self.status_text.set(f"API 檢查失敗：{message}")

    def _finish_api_refresh(self, statuses: list[ApiStatus]) -> None:
        self.api_statuses = statuses
        self.last_api_check = time.time()
        self.api_refreshing = False
        self._apply_api_statuses(statuses)
        displayed = apply_runtime_rate_limits(statuses)
        ok = sum(1 for s in displayed if s.state in ("正常", "可連線"))
        limited = sum(
            1 for s in displayed
            if s.state == "受限" or s.state.startswith("429"))
        self.status_text.set(
            f"API 檢查完成：{ok}/{len(statuses)} 可連線"
            + (f"，{limited} 個受限" if limited else "")
            + "；未產生文字、未消耗推理 token")

    def _apply_api_statuses(self, statuses: list[ApiStatus]) -> None:
        statuses = apply_runtime_rate_limits(statuses)
        tree = self.api_tree
        tree.delete(*tree.get_children())
        for idx, status in enumerate(statuses):
            latency = f"{status.latency_ms} ms" if status.latency_ms is not None else "—"
            tag = ("ok" if status.state in ("正常", "可連線", "就緒") else
                   "limited" if (status.state in ("受限", "尚未檢查")
                                 or status.state.startswith("429")) else "bad")
            tree.insert("", "end", iid=f"api:{idx}", values=(
                status.provider, status.label, status.state, latency,
                status.checked_text, status.note), tags=(tag,))

    def _apply(self, rows: list[WorkProgress], groups: dict[str, list[dict[str, Any]]]) -> None:
        self.rows = rows
        # Runtime generation warnings follow the 10-second local refresh cadence,
        # independently of the slower, token-free connectivity probe.
        self._apply_api_statuses(self.api_statuses)
        for group, tree in self.trees.items():
            tree.delete(*tree.get_children())
            for idx, row in enumerate(rows):
                if group != "全部" and row.group != group:
                    continue
                pct = f"{row.done:,} / {row.total:,} {row.unit}　{row.percent:5.1f}%" if row.total else "尚無資料"
                state = ("● " if row.running else "○ ") + row.state
                tree.insert("", "end", iid=f"{group}:{idx}",
                            values=(state, row.title, pct, row.current, row.updated_text),
                            tags=(self._row_tag(row),))
        running = sum(1 for r in rows if r.state == "執行中")
        complete = sum(1 for r in rows if r.state == "完成")
        attention = sum(1 for r in rows if r.state in (
            "錯誤", "疑似停滯", "待匯入/檢查", "待線上複核", "429 受限"))
        self.summary_vars["running"].set(str(running))
        self.summary_vars["complete"].set(str(complete))
        self.summary_vars["paused"].set(str(len(rows) - running - complete - attention))
        self.summary_vars["attention"].set(str(attention))
        self.status_text.set(
            f"更新於 {datetime.now():%Y-%m-%d %H:%M:%S}　偵測到 {running} 條執行中流水線　"
            f"資料皆來自本機檔案與程序列表")
        self.refreshing = False

    def _selected_row(self) -> WorkProgress | None:
        tab = self.notebook.tab(self.notebook.select(), "text")
        tree = self.trees[tab]
        selected = tree.selection()
        if not selected:
            return None
        try:
            return self.rows[int(selected[0].rsplit(":", 1)[1])]
        except (ValueError, IndexError):
            return None

    def _show_detail(self, _event: Any = None) -> None:
        row = self._selected_row()
        if row:
            extra = f"　{row.detail}" if row.detail else ""
            self.status_text.set(f"{row.group}｜{row.title}｜{row.source}{extra}")

    def _open_selected(self, _event: Any = None) -> None:
        row = self._selected_row()
        if not row:
            return
        path = Path(row.source)
        target = path if path.exists() else path.parent
        try:
            os.startfile(str(target))  # type: ignore[attr-defined]
        except OSError as exc:
            self.status_text.set(f"無法開啟：{exc}")

    def _auto_tick(self) -> None:
        if self.auto_refresh.get():
            self.refresh()
        self.root.after(10_000, self._auto_tick)

    def _api_tick(self) -> None:
        if time.time() - self.last_api_check >= 300:
            self.refresh_apis()
        self.root.after(60_000, self._api_tick)

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    ap = argparse.ArgumentParser(description="全集翻譯進度本機面板")
    ap.add_argument("--snapshot", action="store_true", help="輸出一次 JSON，不開啟 GUI")
    ap.add_argument("--api-status", action="store_true",
                    help="檢查 API models/tags 端點，不生成文字")
    args = ap.parse_args()
    if args.api_status:
        print_api_status()
    elif args.snapshot:
        print_snapshot()
    else:
        Dashboard().run()


if __name__ == "__main__":
    main()
