#!/usr/bin/env python3
"""
whisper_only.py
只做 Whisper 轉錄 → 存到 stores/transcripts/<youtube_id>.txt
不碰資料庫，不下載（需要已有音訊）
用法：
  python scripts/whisper_only.py <youtube_id> <audio_path> [--lang zh] [--start 28]
"""
import os, sys, ctypes, argparse
from pathlib import Path

_CUDA_DLL_PATH = r'C:\Users\user\AppData\Local\Programs\Ollama\lib\ollama\cuda_v12'
if os.name == 'nt' and os.path.exists(_CUDA_DLL_PATH):
    os.add_dll_directory(_CUDA_DLL_PATH)
    for _dll in ['cudart64_12.dll', 'cublas64_12.dll', 'cublasLt64_12.dll']:
        try: ctypes.CDLL(os.path.join(_CUDA_DLL_PATH, _dll))
        except OSError: pass

def run(youtube_id, audio_path, lang='zh', start_sec=0):
    from faster_whisper import WhisperModel
    print(f'[whisper_only] 載入 large-v3-turbo (float16, cuda)...')
    model = WhisperModel('large-v3-turbo', device='cuda', compute_type='float16')
    print(f'[whisper_only] 開始轉錄 {youtube_id} lang={lang} start={start_sec}s')
    segments, _ = model.transcribe(
        str(audio_path),
        language=lang,
        condition_on_previous_text=True,
        vad_filter=True,
        clip_timestamps=[start_sec] if start_sec else None,
    )
    parts = [seg.text.strip() for seg in segments]
    text = '\n'.join(p for p in parts if p)
    print(f'[whisper_only] 完成，共 {len(text)} 字元')

    out = Path(__file__).parent.parent / 'stores' / 'transcripts' / f'{youtube_id}.txt'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding='utf-8')
    print(f'[whisper_only] 已存檔：{out}')

    del model
    print('[whisper_only] 完成，可安全退出。')

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('youtube_id')
    ap.add_argument('audio_path')
    ap.add_argument('--lang', default='zh')
    ap.add_argument('--start', type=int, default=0)
    args = ap.parse_args()
    run(args.youtube_id, args.audio_path, lang=args.lang, start_sec=args.start)
