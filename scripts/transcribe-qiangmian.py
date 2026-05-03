"""
宗教史讀書會 YouTube 影片下載與轉錄流水線
- 使用 yt-dlp 從 YouTube 播放清單下載音訊
- 音訊超過 30 分鐘時自動用 ffmpeg 切段，避免 OOM
- 使用 faster-whisper 進行語音辨識
- 轉錄完成後上傳到 Supabase video_transcripts table
- 上傳成功後刪除音訊/WAV 檔案，節省磁碟空間

執行方式：python -u scripts/transcribe-qiangmian.py
"""

import sys, subprocess, re, requests
from pathlib import Path

PLAYLIST_URL  = "https://youtube.com/playlist?list=PLNdU3g_-OSshfnyOakO5exMMvnSNeuIjZ"
TMP_DIR       = Path(__file__).parent.parent / "_tmp_audio" / "qiangmian"
CHUNK_SECONDS = 1800  # 30 分鐘一段
TMP_DIR.mkdir(parents=True, exist_ok=True)

# 從 .env 讀取 Supabase 設定
_env = {}
for line in (Path(__file__).parent.parent / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        k, _, v = line.partition("=")
        _env[k.strip()] = v.strip().strip('"')

SUPABASE_URL     = _env["SUPABASE_URL"]
SERVICE_ROLE_KEY = _env["SUPABASE_SERVICE_ROLE_KEY"]


def install(pkg):
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])


try:
    import yt_dlp
except ImportError:
    print("Installing yt-dlp..."); install("yt-dlp"); import yt_dlp

try:
    from faster_whisper import WhisperModel
except ImportError:
    print("Installing faster-whisper..."); install("faster-whisper"); from faster_whisper import WhisperModel


# ── Supabase helpers ────────────────────────────────────────────

def episode_exists(episode: int) -> bool:
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/video_transcripts",
        params={"project_slug": "eq.qiangmian", "episode": f"eq.{episode}", "select": "id"},
        headers={"apikey": SERVICE_ROLE_KEY, "Authorization": f"Bearer {SERVICE_ROLE_KEY}"},
    )
    return resp.status_code == 200 and len(resp.json()) > 0


def upload_transcript(episode: int, title: str, content: str,
                       video_date: str = None, youtube_id: str = None) -> bool:
    data = {"project_slug": "qiangmian", "episode": episode,
            "title": title, "content": content}
    if video_date:
        data["video_date"] = video_date
    if youtube_id:
        data["youtube_id"] = youtube_id
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/video_transcripts",
        json=data,
        headers={
            "apikey": SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates",
        },
    )
    return resp.status_code in (200, 201)


# ── 取得播放清單 ─────────────────────────────────────────────────

def fetch_playlist():
    print("Fetching playlist...")
    with yt_dlp.YoutubeDL({"quiet": True, "extract_flat": True, "skip_download": True}) as ydl:
        info = ydl.extract_info(PLAYLIST_URL, download=False)
    entries = info.get("entries", [])
    print(f"Total: {len(entries)} videos")
    return entries


# ── 下載音訊 ────────────────────────────────────────────────────

def download_audio(video_id, safe_title):
    for ext in ["m4a", "webm", "opus", "mp4"]:
        p = TMP_DIR / f"{safe_title}.{ext}"
        if p.exists():
            print(f"  Audio exists: {p.name}")
            return p
    url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        with yt_dlp.YoutubeDL({
            "format": "bestaudio[ext=m4a]/bestaudio/best",
            "outtmpl": str(TMP_DIR / f"{safe_title}.%(ext)s"),
            "quiet": False, "noplaylist": True,
        }) as ydl:
            ydl.download([url])
        for ext in ["m4a", "webm", "opus", "mp4"]:
            p = TMP_DIR / f"{safe_title}.{ext}"
            if p.exists():
                return p
    except Exception as e:
        print(f"  Download failed: {e}")
    return None


# ── 音訊處理 ────────────────────────────────────────────────────

def get_duration(path):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except Exception:
        return 0.0


def make_chunk_wav(src, start, duration, out_path):
    if out_path.exists():
        return True
    ret = subprocess.call(
        ["ffmpeg", "-i", str(src), "-ss", str(start), "-t", str(duration),
         "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", str(out_path), "-y"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return ret == 0


def to_wav(audio_path):
    wav = audio_path.with_suffix(".wav")
    if wav.exists():
        return wav
    print("  Converting to WAV...")
    subprocess.call(
        ["ffmpeg", "-i", str(audio_path), "-ar", "16000", "-ac", "1",
         "-c:a", "pcm_s16le", str(wav), "-y"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return wav


def transcribe_wav(model, wav_path):
    segs, info = model.transcribe(
        str(wav_path), language="zh", beam_size=1,
        vad_filter=True, vad_parameters={"min_silence_duration_ms": 1000})
    segs = list(segs)
    print(f"    lang:{info.language} dur:{info.duration:.0f}s segs:{len(segs)}")
    return segs


def segs_to_blocks(segments):
    blocks, current, prev_end = [], [], 0.0
    for seg in segments:
        if seg.start - prev_end > 2.0 and current:
            blocks.append("".join(current).strip())
            current = []
        current.append(seg.text)
        prev_end = seg.end
    if current:
        blocks.append("".join(current).strip())
    return blocks


# ── 格式化逐字稿 ─────────────────────────────────────────────────

def format_transcript(title, episode, upload_date, blocks):
    lines = [title, f"Episode: {episode}"]
    if upload_date and len(upload_date) == 8:
        lines.append(f"Date: {upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}")
    lines += ["", "[Auto-transcribed. Needs editing.]", ""]
    for b in blocks:
        if b:
            lines += [b, ""]
    return "\n".join(lines)


def safe_name(s):
    return re.sub(r'[\\/:*?"<>|]', '_', s)[:80].strip()


# ── 刪除音訊檔案 ─────────────────────────────────────────────────

def cleanup_audio(safe_title):
    for ext in ["m4a", "webm", "opus", "mp4", "wav"]:
        p = TMP_DIR / f"{safe_title}.{ext}"
        if p.exists():
            p.unlink()
            print(f"  Deleted: {p.name}")
    # 刪除 chunk WAV
    for p in TMP_DIR.glob(f"{safe_title}_chunk*.wav"):
        p.unlink()
        print(f"  Deleted: {p.name}")


# ── 主程式 ──────────────────────────────────────────────────────

def main():
    entries = fetch_playlist()
    if not entries:
        print("Playlist empty or unavailable"); return

    print("\nLoading Whisper model (small)...")
    model = WhisperModel("small", device="cpu", compute_type="int8")
    print("Model loaded\n")

    total = len(entries)
    for i, entry in enumerate(entries, 1):
        video_id  = entry.get("id") or ""
        raw_title = entry.get("title") or f"Episode {i}"
        upload_date = entry.get("upload_date")
        safe_title  = f"{i:02d} {safe_name(raw_title)}"

        print(f"[{i}/{total}] {raw_title}")

        # 已在 Supabase → 跳過
        if episode_exists(i):
            print(f"  Already in Supabase, skip")
            cleanup_audio(safe_title)  # 確保音訊也刪除
            continue

        # 下載
        audio_path = download_audio(video_id, safe_title)
        if not audio_path:
            continue

        duration = get_duration(audio_path)
        print(f"  Duration: {duration/60:.1f} min")

        all_blocks = []

        if duration <= CHUNK_SECONDS:
            wav_path = to_wav(audio_path)
            print("  Transcribing...")
            try:
                segs = transcribe_wav(model, wav_path)
                all_blocks = segs_to_blocks(segs)
            except Exception as e:
                print(f"  Transcription failed: {e}"); continue
        else:
            n_chunks = int(duration // CHUNK_SECONDS) + 1
            print(f"  Long audio, splitting into {n_chunks} chunks (30 min each)")
            for c in range(n_chunks):
                start = c * CHUNK_SECONDS
                chunk_wav = TMP_DIR / f"{safe_title}_chunk{c:02d}.wav"
                print(f"  [{c+1}/{n_chunks}] chunk {start//60:.0f}-{(start+CHUNK_SECONDS)//60:.0f} min...")
                if not make_chunk_wav(audio_path, start, CHUNK_SECONDS, chunk_wav):
                    print("    Chunk failed"); continue
                try:
                    segs = transcribe_wav(model, chunk_wav)
                    all_blocks.extend(segs_to_blocks(segs))
                except Exception as e:
                    print(f"    Transcription failed: {e}")
                chunk_wav.unlink(missing_ok=True)

        if not all_blocks:
            print("  No content, skipping"); continue

        content = format_transcript(raw_title, i, upload_date, all_blocks)

        # 上傳 Supabase
        print(f"  Uploading to Supabase ({len(content):,} chars)...")
        if upload_transcript(i, raw_title, content, upload_date, video_id):
            print(f"  Uploaded OK")
            # 刪除音訊檔案
            cleanup_audio(safe_title)
        else:
            print(f"  Upload FAILED, keeping audio files")

    print(f"\nDone!")


if __name__ == "__main__":
    main()
