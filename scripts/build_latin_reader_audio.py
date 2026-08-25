#!/usr/bin/env python3
"""A first-cut audio track for the Latin reader, and an honest label on it.

The release contract for this series says plainly that synthetic speech does not
satisfy the audio gate: a real track records the pronunciation profile, the
reader, the rate, a checksum, the rights, and the segment cues. This is not that
track and does not pretend to be. It exists so the owner can hear the reader
while the recorded one is arranged, and every file it writes is stamped
``draft`` in the manifest for exactly that reason.

The voice is Italian, not English. Ecclesiastical Latin is pronounced the Roman
way -- *caelum* as CHEH-loom, *excelsis* as ek-SHEL-sees, *regina* as reh-JEE-nah
-- and an English voice reads it as neither Latin nor anything else. An Italian
voice is wrong in its own ways (it will not lengthen a vowel that the macrons
mark) but it is wrong in the right direction, and the macrons are stripped before
synthesis because the voice would otherwise stumble over characters it has no
rule for.

What is rendered is what is short enough to be worth hearing repeatedly: the ten
liturgical formulas of the upper volume, and every memory unit in both. The
readings are not rendered; an hour of synthetic Latin is not a study aid.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import unicodedata
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "latin-full"
MASTER = CACHE / "latin-reader-two-volumes.json"
OUT_DIR = ROOT / "output" / "original-readers" / "audio" / "latin"
MANIFEST = OUT_DIR / "manifest.json"

VOICE = "Microsoft Elsa Desktop"     # it-IT
RATE = -2                            # SAPI scale; slower than speech, near reading pace


def speakable(text: str) -> str:
    """Strip what the voice cannot read, keep what changes the sound.

    Macrons mark vowel length, which this voice does not implement, and leaving
    them in makes it spell characters out. Verse numbers and the V./R. markers
    are page furniture, not words.
    """
    text = text.replace("V.", " ").replace("R.", " ")
    text = "".join(ch for ch in unicodedata.normalize("NFD", text)
                   if not unicodedata.combining(ch))
    text = "".join(ch for ch in text if not ch.isdigit())
    return " ".join(text.split())


def synthesise(text: str, wav: Path) -> bool:
    script = (
        "Add-Type -AssemblyName System.Speech; "
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        f"$s.SelectVoice('{VOICE}'); $s.Rate = {RATE}; "
        f"$s.SetOutputToWaveFile('{wav.as_posix()}'); "
        f"$s.Speak([System.IO.File]::ReadAllText('{wav.with_suffix('.txt').as_posix()}', "
        "[System.Text.Encoding]::UTF8)); $s.Dispose()"
    )
    wav.with_suffix(".txt").write_text(text, encoding="utf-8")
    result = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
                            capture_output=True, text=True)
    wav.with_suffix(".txt").unlink(missing_ok=True)
    return result.returncode == 0 and wav.exists() and wav.stat().st_size > 1000


def to_mp3(wav: Path) -> Path | None:
    mp3 = wav.with_suffix(".mp3")
    result = subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-codec:a", "libmp3lame",
         "-qscale:a", "5", str(mp3)],
        capture_output=True, text=True)
    if result.returncode == 0 and mp3.exists():
        wav.unlink(missing_ok=True)
        return mp3
    return None


def clips() -> list[dict]:
    master = json.loads(MASTER.read_text(encoding="utf-8"))
    out: list[dict] = []
    for volume in master["volumes"]:
        for lesson in volume["lessons"]:
            if volume["volume"] == 1 and lesson["lesson"] <= 10 and lesson["reading"]:
                out.append({
                    "id": f"v{volume['volume']}-l{lesson['lesson']:02d}-liturgy",
                    "kind": "liturgy", "volume": volume["volume"],
                    "lesson": lesson["lesson"], "title": lesson["title"],
                    "text": " ".join(row["latin"] for row in lesson["reading"]),
                })
            for index, unit in enumerate(lesson["memoryUnits"], start=1):
                out.append({
                    "id": f"v{volume['volume']}-l{lesson['lesson']:02d}-mem{index}",
                    "kind": "memory", "volume": volume["volume"],
                    "lesson": lesson["lesson"], "title": unit.get("ref", ""),
                    "text": unit["text"],
                })
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {"clips": {}}
    pending = [clip for clip in clips() if clip["id"] not in manifest["clips"]]
    if args.limit:
        pending = pending[: args.limit]
    print(f"待合成 {len(pending)}；已有 {len(manifest['clips'])}")

    made = failed = 0
    for clip in pending:
        text = speakable(clip["text"])
        if len(text) < 4:
            continue
        wav = OUT_DIR / f"{clip['id']}.wav"
        if not synthesise(text, wav):
            failed += 1
            continue
        mp3 = to_mp3(wav) or wav
        manifest["clips"][clip["id"]] = {
            **{k: v for k, v in clip.items() if k != "text"},
            "spoken": text,
            "file": mp3.name,
            "bytes": mp3.stat().st_size,
            "sha256": hashlib.sha256(mp3.read_bytes()).hexdigest(),
        }
        made += 1
        if made % 20 == 0:
            print(f"  {made}/{len(pending)}", flush=True)

    manifest.update({
        "generatedOn": date.today().isoformat(),
        "status": "draft",
        "voice": VOICE,
        "profile": "羅馬式教會發音的近似（義大利文語音合成）",
        "policy": "合成語音，僅供辨音參考。發行版必須錄製真人羅馬式教會發音，"
                  "並記錄朗讀者、語速、段落提示與著作權；本軌不得充當發行音軌。",
    })
    print(f"完成 {made}，失敗 {failed}，總計 {len(manifest['clips'])} 段")
    if args.write:
        MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
        total = sum(c["bytes"] for c in manifest["clips"].values())
        print("->", MANIFEST.relative_to(ROOT), f"{total / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
