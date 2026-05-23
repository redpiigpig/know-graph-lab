"""Sequential corpus translator — drives translate_ebook_to_zh.py across an ordered
queue of Schaff ebook IDs (ANF 1-10 → NPNF1 1-14 → NPNF2 1-14, 37 books / ~104M chars).

Usage:
    python scripts/translate_corpus_queue.py --engine gemini
    python scripts/translate_corpus_queue.py --engine gemini --start ANF:2   # skip to ANF Vol 2
    python scripts/translate_corpus_queue.py --status                         # don't run; print progress

State file: scripts/logs/corpus_queue_state.json
Per-book log: scripts/logs/translate_<ebook_id>_<timestamp>.log
"""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = ROOT / "scripts" / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
STATE_FILE = LOGS_DIR / "corpus_queue_state.json"

# Queue order: ANF 1-10 → NPNF1 1-14 → NPNF2 1-14
QUEUE: list[tuple[str, int, str, str]] = [
    # (series, vol, ebook_id, short_title)
    ("ANF", 1, "c98d358d-7066-4691-a896-b7232707b0db", "Apostolic Fathers / Justin / Irenaeus"),
    ("ANF", 2, "4e3d16fc-ef4f-420f-a3ec-56e2e92d659f", "Fathers of 2c (Hermas/Tatian/Athen/Theoph/Clement)"),
    ("ANF", 3, "364dac2e-410f-4906-be63-8bb86b4865ee", "Latin Christianity / Tertullian Apologetic"),
    ("ANF", 4, "904661d3-16fc-4f37-bb04-f7c4aa7671e9", "Tertullian IV / Minucius / Commodian / Origen"),
    ("ANF", 5, "0e08c662-540b-4186-b250-9bca0cfe1002", "Hippolytus / Cyprian / Caius / Novatian"),
    ("ANF", 6, "dffaae40-e088-41c1-ab7f-9b96f9249661", "Gregory Thaumaturgus / Dionysius / Africanus / Anatolius"),
    ("ANF", 7, "75d8aae0-7431-4be9-baee-c57d26599653", "Lactantius / Venantius / Asterius / Methodius / Arnobius"),
    ("ANF", 8, "d09946ab-154b-4a97-853f-751cbb346221", "Twelve Patriarchs / Apostolic Constitutions / Homilies"),
    ("ANF", 9, "72cb2f94-da86-4e16-bbbd-4cf3391031df", "Gospel of Peter / Diatessaron / Apocalypses / Visio Pauli"),
    ("ANF", 10, "243ff253-54b6-4cb3-af4b-ba647254dbc1", "Bibliography / General Index"),

    ("NPNF1", 1, "9edb7c37-4231-412b-83bd-78f3f793cc0a", "Augustine - Confessions and Letters"),
    ("NPNF1", 2, "1eb50be9-34ac-4ce3-874d-1280975851fc", "Augustine - City of God / Christian Doctrine"),
    ("NPNF1", 3, "d7f66759-3fa9-4633-abde-87003cdbcc06", "Augustine - On the Holy Trinity / Doctrinal Treatises"),
    ("NPNF1", 4, "56ef3d65-c559-41f8-8d68-ba6c13e47876", "Augustine - Anti-Manichaean / Anti-Donatist"),
    ("NPNF1", 5, "df789501-5620-4833-a0a0-6e8f1a031bb1", "Augustine - Anti-Pelagian Writings"),
    ("NPNF1", 6, "7bff8a13-3c35-43d4-9b4c-b7c3c9f81076", "Augustine - Sermon on the Mount / Harmony of Gospels"),
    ("NPNF1", 7, "0069932a-7b27-4c06-9874-b74d51ad564e", "Augustine - Homilies on John / 1 John / Soliloquies"),
    ("NPNF1", 8, "2accee20-5f9d-4099-9ce9-3dda0726a74b", "Augustine - Expositions on the Psalms"),
    ("NPNF1", 9, "76df31fe-e732-4aa6-88c2-d650a09fb688", "Chrysostom - On the Priesthood / Statues"),
    ("NPNF1", 10, "0d160c29-8d61-4dbc-8f8e-d47fee694eab", "Chrysostom - Homilies on Matthew"),
    ("NPNF1", 11, "4d73c561-aa4e-46b2-8e29-d331c5b9d28d", "Chrysostom - Homilies on Acts / Romans"),
    ("NPNF1", 12, "bf2dd1b2-ae53-43c2-8fac-7ce10e137c10", "Chrysostom - Homilies on 1-2 Corinthians"),
    ("NPNF1", 13, "9192cb77-3ce2-4adb-9d90-76200e452763", "Chrysostom - Homilies on Gal-Eph-Phil-Col-Thess-Tim-Tit-Phlm"),
    ("NPNF1", 14, "91c7023f-2e63-4b16-897a-43bdf7d5e290", "Chrysostom - Homilies on John / Hebrews"),

    ("NPNF2", 1, "91ff3a5e-cd1f-4ab4-acb7-70cb7a80c4b9", "Eusebius - Church History / Life of Constantine"),
    ("NPNF2", 2, "29782dd6-ece9-446a-83ed-9cc0892d7cc7", "Socrates / Sozomenus - Ecclesiastical Histories"),
    ("NPNF2", 3, "a7e5956e-8851-4d0f-b3d2-1f823d1bdc81", "Theodoret / Jerome / Gennadius / Rufinus - Historical Writings"),
    ("NPNF2", 4, "e01917ab-7429-41a0-9859-eddad413ef60", "Athanasius - Select Works and Letters"),
    ("NPNF2", 5, "9b94e7c1-fa82-4910-a31f-9db1e2e040bb", "Gregory of Nyssa - Dogmatic Treatises"),
    ("NPNF2", 6, "d229a6d4-14de-4e28-92de-4855c75cbf68", "Jerome - Letters and Select Works"),
    ("NPNF2", 7, "af2cf8a7-b169-432c-863d-632647c8ab67", "Cyril of Jerusalem / Gregory Nazianzen - Select Writings"),
    ("NPNF2", 8, "3c48472c-fbca-48fb-9db1-ca5a08827ef3", "Basil - Letters and Select Works"),
    ("NPNF2", 9, "709f43f9-724c-4cd5-b6b0-570d26083d24", "Hilary of Poitiers / John of Damascus - Select Works"),
    ("NPNF2", 10, "fd8a09e7-a6ab-4818-a6d7-6722e50da773", "Ambrose - Select Works and Letters"),
    ("NPNF2", 11, "24c53ede-8787-442e-a3ba-0cd55d0effac", "Sulpitius Severus / Vincent of Lerins / John Cassian"),
    ("NPNF2", 12, "02a08547-6fb5-44b2-8a59-9b1f625f3a54", "Leo the Great / Gregory the Great"),
    ("NPNF2", 13, "90b55879-7179-41d7-9f6c-f6587a3dd429", "Gregory the Great Part II / Ephraim Syrus / Aphrahat"),
    ("NPNF2", 14, "63853a97-68be-441c-8dce-063ae89405c5", "The Seven Ecumenical Councils"),
]


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8-sig"))
    return {"completed": [], "failed": [], "started_at": None, "current": None}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def fmt_dur(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:d}h{m:02d}m{s:02d}s"


def print_status(state: dict) -> None:
    done = set(state["completed"])
    fail = {f["id"] for f in state["failed"]}
    print(f"\n=== Corpus translation status ===")
    print(f"  Started: {state.get('started_at') or 'never'}")
    print(f"  Current: {state.get('current') or '(none)'}")
    print(f"  Completed: {len(done)}/{len(QUEUE)}")
    print(f"  Failed: {len(fail)}")
    for series_name in ["ANF", "NPNF1", "NPNF2"]:
        items = [q for q in QUEUE if q[0] == series_name]
        d = sum(1 for q in items if q[2] in done)
        f = sum(1 for q in items if q[2] in fail)
        bar = "█" * d + ("·" * (len(items) - d))
        print(f"  {series_name:>6} [{bar}] {d}/{len(items)} done, {f} failed")
    if state.get("current"):
        for s, v, eid, t in QUEUE:
            if eid == state["current"]:
                print(f"  Currently translating: {s} Vol {v} — {t}")
                break


def run_one(series: str, vol: int, ebook_id: str, title: str, engine: str) -> tuple[bool, str]:
    """Run translate_ebook_to_zh.py --resume on one book. Returns (success, log_path)."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    log_path = LOGS_DIR / f"translate_{series}_vol{vol:02d}_{timestamp}.log"
    cmd = [
        sys.executable, "-u",
        str(ROOT / "scripts" / "translate_ebook_to_zh.py"),
        ebook_id,
        "--engine", engine,
        "--resume",
    ]
    print(f"\n┌────────────────────────────────────────────────────────────────")
    print(f"│ {series} Vol {vol} — {title}")
    print(f"│ ebook_id={ebook_id}")
    print(f"│ engine={engine}  log={log_path.name}")
    print(f"└────────────────────────────────────────────────────────────────", flush=True)
    t0 = time.time()
    with open(log_path, "w", encoding="utf-8") as logf:
        logf.write(f"# {series} Vol {vol} | {title}\n# {ebook_id}\n# engine={engine}\n# started {datetime.now().isoformat()}\n\n")
        logf.flush()
        proc = subprocess.Popen(cmd, stdout=logf, stderr=subprocess.STDOUT, cwd=str(ROOT))
        # We don't capture output here; tail the log to see progress.
        rc = proc.wait()
    elapsed = time.time() - t0
    ok = rc == 0
    status = "OK" if ok else f"FAILED (exit {rc})"
    print(f"\n  → {status}  duration={fmt_dur(elapsed)}  log={log_path}", flush=True)
    return ok, str(log_path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default="gemini", choices=["sonnet", "gemini", "haiku"],
                    help="LLM engine (default: gemini — has Haiku fallback built-in)")
    ap.add_argument("--start", default=None,
                    help="Start at a specific book, format 'SERIES:VOL' e.g. 'ANF:5' or 'NPNF1:1'")
    ap.add_argument("--only", default=None,
                    help="Translate only the specified book, format 'SERIES:VOL'")
    ap.add_argument("--status", action="store_true", help="Print state and exit, don't translate")
    ap.add_argument("--reset", action="store_true", help="Reset state (re-evaluates all books from scratch)")
    ap.add_argument("--skip-failed", action="store_true",
                    help="When restarting, skip books that previously failed (default: retry them)")
    args = ap.parse_args()

    state = load_state()
    if args.reset:
        state = {"completed": [], "failed": [], "started_at": None, "current": None}
        save_state(state)
        print("State reset.", flush=True)

    if args.status:
        print_status(state)
        return

    # Filter queue
    queue = QUEUE
    if args.start:
        ser, vol = args.start.split(":")
        vol = int(vol)
        for i, (s, v, _, _) in enumerate(queue):
            if s == ser and v == vol:
                queue = queue[i:]
                break
        else:
            print(f"--start {args.start} not found in queue.")
            return
    if args.only:
        ser, vol = args.only.split(":")
        vol = int(vol)
        queue = [q for q in queue if q[0] == ser and q[1] == int(vol)]
        if not queue:
            print(f"--only {args.only} not found in queue.")
            return

    if not state.get("started_at"):
        state["started_at"] = datetime.now().isoformat()
        save_state(state)

    done_ids = set(state["completed"])
    failed_ids = {f["id"] for f in state["failed"]}
    print_status(state)

    for series, vol, ebook_id, title in queue:
        if ebook_id in done_ids:
            print(f"  ✓ skip (already done): {series} Vol {vol}", flush=True)
            continue
        if args.skip_failed and ebook_id in failed_ids:
            print(f"  ⊘ skip (previously failed): {series} Vol {vol}", flush=True)
            continue
        state["current"] = ebook_id
        save_state(state)
        ok, log = run_one(series, vol, ebook_id, title, args.engine)
        # Refresh state from disk (in case a parallel viewer wrote to it)
        state = load_state()
        if ok:
            if ebook_id not in state["completed"]:
                state["completed"].append(ebook_id)
            state["failed"] = [f for f in state["failed"] if f["id"] != ebook_id]
        else:
            entry = {"id": ebook_id, "series": series, "vol": vol, "title": title,
                     "log": log, "at": datetime.now().isoformat()}
            state["failed"] = [f for f in state["failed"] if f["id"] != ebook_id] + [entry]
            print(f"  ⚠ book failed — continuing to next book. Re-run with --only {series}:{vol} to retry.", flush=True)
        state["current"] = None
        save_state(state)

    print(f"\n=== Queue complete ===")
    print_status(state)


if __name__ == "__main__":
    main()
