#!/usr/bin/env python3
"""
talks_pipeline.py
演講批次處理：下載 → Whisper 轉錄 → 存 txt
（不碰資料庫，DB 寫入由 db_write_from_transcripts.cjs 處理）

音訊存在 stores/audio/，逐字稿存在 stores/transcripts/
"""
import os, sys, ctypes, subprocess
from pathlib import Path

_CUDA_DLL_PATH = r'C:\Users\user\AppData\Local\Programs\Ollama\lib\ollama\cuda_v12'
if os.name == 'nt' and os.path.exists(_CUDA_DLL_PATH):
    os.add_dll_directory(_CUDA_DLL_PATH)
    for _dll in ['cudart64_12.dll', 'cublas64_12.dll', 'cublasLt64_12.dll']:
        try: ctypes.CDLL(os.path.join(_CUDA_DLL_PATH, _dll))
        except OSError: pass

YTDLP_PATH  = r'C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\Scripts\yt-dlp.exe'
FFMPEG_PATH = r'C:\Users\user\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin'
ROOT        = Path(__file__).parent.parent
AUDIO_DIR   = ROOT / 'stores' / 'audio'
TRANS_DIR   = ROOT / 'stores' / 'transcripts'

TALKS = [
    {'youtube_id': '9aWpePHshxE', 'youtube_start': 28, 'lang': 'zh'},
    {'youtube_id': 'Px2I24CRPxo', 'youtube_start': 23, 'lang': 'zh'},
    {'youtube_id': 'YrtfxTB6_i4', 'youtube_start': 0,  'lang': 'zh'},
]


def download(youtube_id):
    url = f'https://www.youtube.com/watch?v={youtube_id}'
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    out = AUDIO_DIR / f'{youtube_id}.mp3'
    if out.exists():
        print(f'  已有音訊：{out}，跳過下載')
        return out
    print(f'  下載音訊：{url}')
    subprocess.run([
        YTDLP_PATH, '-x', '--audio-format', 'mp3', '--audio-quality', '0',
        '--ffmpeg-location', FFMPEG_PATH,
        '-o', str(out), '--no-playlist', url
    ], check=True)
    print(f'  下載完成：{out}')
    return out


def transcribe(youtube_id, audio_path, lang='zh', start_sec=0):
    from faster_whisper import WhisperModel
    TRANS_DIR.mkdir(parents=True, exist_ok=True)
    out = TRANS_DIR / f'{youtube_id}.txt'
    if out.exists() and out.stat().st_size > 100:
        print(f'  已有逐字稿：{out}（{out.stat().st_size} bytes），跳過轉錄')
        return

    print(f'  載入 Whisper large-v3-turbo (cuda, float16)...')
    model = WhisperModel('large-v3-turbo', device='cuda', compute_type='float16')
    print(f'  開始轉錄（lang={lang}, start={start_sec}s）...')
    segments, _ = model.transcribe(
        str(audio_path), language=lang,
        condition_on_previous_text=True, vad_filter=True,
        clip_timestamps=[start_sec] if start_sec else [],
    )
    parts = [seg.text.strip() for seg in segments]
    text = '\n'.join(p for p in parts if p)
    print(f'  轉錄完成，共 {len(text)} 字元')

    out.write_text(text, encoding='utf-8')
    print(f'  💾 已存檔：{out}')
    del model


def main():
    for talk in TALKS:
        yid  = talk['youtube_id']
        lang = talk.get('lang', 'zh')
        start = talk.get('youtube_start', 0)
        print(f'\n═══ {yid} ═══')
        try:
            audio = download(yid)
            transcribe(yid, audio, lang=lang, start_sec=start)
        except Exception as e:
            import traceback
            print(f'  ❌ 錯誤：{e}')
            traceback.print_exc()

    print('\n全部轉錄完成。請執行：')
    print('  node scripts/db_write_from_transcripts.cjs')


if __name__ == '__main__':
    main()
