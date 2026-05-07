---
name: qiangmian-transcribe
description: Transcribe 宗教史讀書會 YouTube videos with Gemini Audio + PPT context and upsert into Supabase video_transcripts. Use when the user wants to re-transcribe one or more episodes of 千面上帝 宗教史讀書會.
---

# 宗教史讀書會 — Gemini 轉錄流水線

End-to-end workflow: yt-dlp download → Gemini 2.5 Flash audio transcription (with PPT as context) → Supabase upsert.

Replaces the old Whisper-based `scripts/transcribe-qiangmian.py` which produced simplified-Chinese, no-punctuation, run-on output.

## Quality result

Gemini output is properly formatted Traditional Chinese with correct punctuation, paragraph breaks, and proper nouns from PPT. See ep 1 live at:
`http://localhost:3002/works/qiangmian/reading-club/fd987720-e07f-43c0-ab30-2907235abb42`

## Files

| File | Role |
|---|---|
| [`scripts/transcribe_qiangmian_gemini.py`](../../../scripts/transcribe_qiangmian_gemini.py) | Main CLI |
| `G:/我的雲端硬碟/創作/千面上帝/宗教史讀書會/*.pptx` | PPT context files (sorted by YYYY.MM.DD prefix → ep 1, 2, 3…) |
| `_tmp_audio/qiangmian/` | Temp audio (deleted after successful upsert) |

## Playlist

YouTube playlist: `https://www.youtube.com/playlist?list=PLNdU3g_-OSshfnyOakO5exMMvnSNeuIjZ`
25 videos. PPT files: 29 (some chapters split over multiple sessions).
Episodes 1–25 = playlist position 1–25; PPT index i = ep i.

## Commands

```bash
# List all episodes + matching PPT
python scripts/transcribe_qiangmian_gemini.py --list

# Re-transcribe single episode
python scripts/transcribe_qiangmian_gemini.py --episode 1

# Re-transcribe range
python scripts/transcribe_qiangmian_gemini.py --episode 1-5

# All episodes (takes a long time — ~3-5 min per ep)
python scripts/transcribe_qiangmian_gemini.py --all
```

## Supabase table

Table: `video_transcripts`
Upsert key: `(project_slug, episode)` → `on_conflict=project_slug,episode`
Content format:
```
[title]
Episode: N
Date: YYYY-MM-DD

[Gemini transcript — formatted paragraphs, Traditional Chinese]
```

## Key fixes vs old script

1. `on_conflict=project_slug,episode` needed in POST URL for upsert to work (not just `Prefer: resolution=merge-duplicates`)
2. Gemini Files API state must be ACTIVE before calling generate_content — poll with `client.files.get()`
3. PPT sorted by `YYYY.MM.DD` filename prefix, matched 1:1 to playlist position

## Model

`gemini-2.5-flash` — handles 100MB audio files. Uses Gemini_API_Key_1 through _4 from .env (no rotation currently; add if quota hit).
