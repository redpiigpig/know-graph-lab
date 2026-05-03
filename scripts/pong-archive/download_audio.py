#!/usr/bin/env python3
"""
download_audio.py
只負責用 yt-dlp 下載音訊到指定路徑（不做轉錄）
用法：
  python scripts/download_audio.py <youtube_url_or_id> <output_path.mp3>
  python scripts/download_audio.py 9aWpePHshxE stores/audio/9aWpePHshxE.mp3
"""
import sys, subprocess
from pathlib import Path

YTDLP_PATH = r'C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\Scripts\yt-dlp.exe'
FFMPEG_PATH = r'C:\Users\user\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin'

def download(yt_id_or_url, output_path):
    url = yt_id_or_url if yt_id_or_url.startswith('http') else f'https://www.youtube.com/watch?v={yt_id_or_url}'
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    print(f'[download] 下載：{url} -> {output_path}')
    subprocess.run([
        YTDLP_PATH, '-x', '--audio-format', 'mp3', '--audio-quality', '0',
        '--ffmpeg-location', FFMPEG_PATH,
        '-o', str(output_path), '--no-playlist', url
    ], check=True)
    print(f'[download] 完成')

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('用法: python download_audio.py <yt_id_or_url> <output.mp3>')
        sys.exit(1)
    download(sys.argv[1], sys.argv[2])
