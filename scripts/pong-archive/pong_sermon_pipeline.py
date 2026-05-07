#!/usr/bin/env python3
"""
pong_sermon_pipeline.py
流水線：YouTube URL  下載音訊  Whisper 轉錄  寫入 pong_media  連結 pong_sermons

用法（單筆）：
  python scripts/pong_sermon_pipeline.py <YouTube_URL>
  python scripts/pong_sermon_pipeline.py <YouTube_URL> --date 2024-12-01
  python scripts/pong_sermon_pipeline.py <YouTube_URL> --lang en
  python scripts/pong_sermon_pipeline.py <YouTube_URL> --title "自訂標題"

用法（批次）：
  python -u scripts/pong_sermon_pipeline.py --batch-file stores/城中教會講道清單/城中教會講道_2013.txt --yes
"""

import sys
import os
import re
import json
import argparse
import subprocess
import tempfile
import time
import random
from pathlib import Path

# Windows nohup 環境下 stdout 預設 cp950，強制 UTF-8 避免印出中文/� 時崩潰
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Windows：預載 Ollama 附帶的 CUDA v12 DLL，讓 ctranslate2 能找到
import ctypes as _ctypes
_CUDA_DLL_PATH = r'C:\Users\user\AppData\Local\Programs\Ollama\lib\ollama\cuda_v12'
if os.name == 'nt' and os.path.exists(_CUDA_DLL_PATH):
    os.add_dll_directory(_CUDA_DLL_PATH)
    for _dll in ['cudart64_12.dll', 'cublas64_12.dll', 'cublasLt64_12.dll']:
        try:
            _ctypes.CDLL(os.path.join(_CUDA_DLL_PATH, _dll))
        except OSError:
            pass

import requests
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / '.env')


#  資料庫（Supabase REST API）

def _sb_url():
    return os.environ['VITE_SUPABASE_URL'].rstrip('/')

def _sb_headers():
    return {
        'apikey': os.environ['SUPABASE_SERVICE_KEY'],
        'Authorization': f'Bearer {os.environ["SUPABASE_SERVICE_KEY"]}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation',
    }


#  YouTube

def extract_youtube_id(url):
    patterns = [
        r'youtu\.be/([^?&/]+)',
        r'youtube\.com/watch\?v=([^&]+)',
        r'youtube\.com/embed/([^?&]+)',
        r'youtube\.com/shorts/([^?&/]+)',
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    raise ValueError(f'無法解析 YouTube ID：{url}')


def fetch_youtube_metadata(url):
    print(' 取得影片資訊...')
    # Try with cookies first; fall back to android_vr (no cookies) if n-challenge blocks
    attempts = [
        [YTDLP_PATH, '--dump-json', '--no-playlist',
         '--sleep-requests', '3', '--min-sleep-interval', '2',
         '--js-runtimes', 'node', *_cookie_args(), url],
        [YTDLP_PATH, '--dump-json', '--no-playlist',
         '--extractor-args', 'youtube:player_client=android_vr',
         '--sleep-requests', '3', '--min-sleep-interval', '2', url],
    ]
    for cmd in attempts:
        result = subprocess.run(cmd, capture_output=True)
        stdout = result.stdout.decode('utf-8', errors='replace')
        stderr = result.stderr.decode('utf-8', errors='replace')
        if result.returncode == 0 and stdout.strip():
            break
        print(f'  [yt-dlp WARN] {stderr[-400:].strip()}')
    else:
        print(f'  [yt-dlp ERROR] all attempts failed')
        raise subprocess.CalledProcessError(result.returncode, result.args, stdout, stderr)
    data = json.loads(stdout)
    upload_raw = data.get('upload_date', '')  # YYYYMMDD
    upload_date = (
        f"{upload_raw[:4]}-{upload_raw[4:6]}-{upload_raw[6:]}"
        if upload_raw else None
    )
    return {
        'title':       data.get('title', ''),
        'upload_date': upload_date,
        'duration':    int(data.get('duration') or 0),
        'description': (data.get('description') or '')[:500],
        'thumbnail':   data.get('thumbnail', ''),
    }


FFMPEG_PATH  = r'C:\Users\user\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin'
YTDLP_PATH   = r'C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\Scripts\yt-dlp.exe'
COOKIES_FILE = str(Path(__file__).parent.parent / 'cookies.txt')

def _cookie_args():
    """Firefox 優先（無 v20 加密問題），備援 cookies.txt"""
    # Firefox 使用標準 DPAPI，yt-dlp 可直接讀取，不需要 Chrome 關閉
    return ['--cookies-from-browser', 'firefox']

def download_audio(url, output_path):
    print('  下載音訊中...')
    base_args = ['-x', '--audio-format', 'mp3', '--audio-quality', '0',
                 '--ffmpeg-location', FFMPEG_PATH, '-o', str(output_path), '--no-playlist']
    attempts = [
        [YTDLP_PATH, *base_args, '--js-runtimes', 'node', *_cookie_args(), url],
        [YTDLP_PATH, *base_args, '--extractor-args', 'youtube:player_client=android_vr', url],
    ]
    for cmd in attempts:
        result = subprocess.run(cmd)
        if result.returncode == 0:
            return
        print(f'  [yt-dlp WARN] download attempt failed (code {result.returncode}), retrying...')
    raise subprocess.CalledProcessError(result.returncode, attempts[-1])


#  Whisper

_whisper_model = None

def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel
        print('  載入 Whisper large-v3 (int8_float16)...')
        _whisper_model = WhisperModel('large-v3-turbo', device='cuda', compute_type='int8_float16')
        print('  模型就緒')
    return _whisper_model

CHUNK_MINUTES = 20  # 長音訊切段上限（分鐘）

def _audio_duration_sec(audio_path):
    """用 ffprobe 取得音訊秒數"""
    ffprobe_exe = os.path.join(FFMPEG_PATH, 'ffprobe.exe')
    r = subprocess.run(
        [ffprobe_exe, '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'default=noprint_wrappers=1:nokey=1', str(audio_path)],
        capture_output=True, text=True,
    )
    try:
        sec = float(r.stdout.strip())
        print(f'  音訊長度：{sec/60:.1f} 分鐘')
        return sec
    except ValueError:
        print(f'  [警告] ffprobe 無法取得時長，改用分段保守值')
        return 9999.0   # 保守：總是切段


def _split_audio(audio_path, chunk_sec, tmpdir):
    """用 ffmpeg 把音訊切成 chunk_sec 秒的段落，回傳路徑列表"""
    ffmpeg_exe = os.path.join(FFMPEG_PATH, 'ffmpeg.exe')
    out_pattern = str(Path(tmpdir) / 'chunk_%03d.mp3')
    subprocess.run([
        ffmpeg_exe, '-y', '-i', str(audio_path),
        '-f', 'segment', '-segment_time', str(chunk_sec),
        '-c', 'copy', out_pattern,
    ], check=True, capture_output=True)
    chunks = sorted(Path(tmpdir).glob('chunk_*.mp3'))
    return chunks


def transcribe(audio_path, lang, max_chunks=None):
    label = lang if lang != 'auto' else '自動偵測'
    model = get_whisper_model()

    duration = _audio_duration_sec(audio_path)
    chunk_sec = CHUNK_MINUTES * 60
    if duration > chunk_sec:
        print(f'  音訊長度 {duration/60:.0f} 分鐘，切成 {CHUNK_MINUTES} 分鐘段落轉錄...')
        tmpdir = str(audio_path.parent)
        chunks = _split_audio(audio_path, chunk_sec, tmpdir)
        if max_chunks is not None:
            chunks = chunks[:max_chunks]
            print(f'  [triage 模式] 只轉錄前 {len(chunks)} 段')
        all_lines = []
        for i, chunk in enumerate(chunks, 1):
            print(f'  轉錄第 {i}/{len(chunks)} 段（RTX 4050 GPU large-v3-turbo int8_float16，語言：{label}）...')
            segs, _ = model.transcribe(
                str(chunk), language=lang if lang != 'auto' else None,
                beam_size=5, vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500),
            )
            all_lines.extend(seg.text.strip() for seg in segs if seg.text.strip())
        transcript = '\n'.join(all_lines)
    else:
        print(f'  轉錄中（RTX 4050 GPU large-v3-turbo int8_float16，語言：{label}）...')
        segments, _ = model.transcribe(
            str(audio_path),
            language=lang if lang != 'auto' else None,
            beam_size=5, vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
        )
        transcript = '\n'.join(seg.text.strip() for seg in segments if seg.text.strip())

    print(f' 轉錄完成，共 {len(transcript)} 字')
    return transcript


def reformat_whisper(text):
    """無標點 Whisper 輸出段落合併（每 10 行或碰到話題轉換詞即斷段）"""
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    TOPIC_RE = re.compile(
        r'^(那(麼)?|但[是]?|另外|接下來|今天|其實|所以|可是|而且|'
        r'第[一二三四五六七八九十]|首先|最後|讓我們|天父|'
        r'这是|另外|不过|但是|然后|所以|首先|最后|让我们|天父)'
    )
    paras, cur, chars, lc = [], [], 0, 0
    for i, line in enumerate(lines):
        cur.append(line); chars += len(line); lc += 1
        if i + 1 >= len(lines):
            break
        nxt = lines[i + 1]
        if (TOPIC_RE.match(nxt) and (lc >= 6 or chars >= 200)) or lc >= 10:
            paras.append(''.join(cur)); cur = []; chars = 0; lc = 0
    if cur:
        paras.append(''.join(cur))
    return '\n'.join(paras)


#  資料庫查詢（REST API）

def find_sermon_by_date(date_str):
    r = requests.get(
        f'{_sb_url()}/rest/v1/pong_sermons',
        headers=_sb_headers(),
        params={'select':'id,title,sermon_date,media_id,content', 'sermon_date':f'eq.{date_str}'},
    )
    rows = r.json()
    return rows[0] if rows else None


def insert_media(*, youtube_id, title, duration, transcript,
                 description, thumbnail, broadcast_date):
    r = requests.post(
        f'{_sb_url()}/rest/v1/pong_media',
        headers=_sb_headers(),
        json={
            'title': title, 'media_type': 'sermon_audio', 'platform': 'youtube',
            'youtube_id': youtube_id, 'duration_sec': duration,
            'transcript': transcript, 'description': description,
            'thumbnail_url': thumbnail, 'broadcast_date': broadcast_date,
            'is_published': True,
        },
    )
    return r.json()[0]['id']


def link_sermon(sermon_id, media_id, title, content):
    """連結 pong_sermons，同時更新 title 與 content（若還沒有內容）"""
    patch = {'media_id': media_id, 'has_recording': True}
    if title:
        patch['title'] = title
    if content:
        patch['content'] = content
    requests.patch(
        f'{_sb_url()}/rest/v1/pong_sermons',
        headers=_sb_headers(),
        params={'id': f'eq.{sermon_id}'},
        json=patch,
    )


def insert_sermon(date_str, title):
    """若 pong_sermons 沒有該日期，建立新記錄"""
    year = int(date_str[:4])
    month = int(date_str[5:7])
    # 教會年：12 月起算為新年（將臨期）
    church_year = year if month == 12 else year - 1
    # 以日期 YYYYMMDD 作為 ID
    sermon_id = int(date_str.replace('-', ''))
    r = requests.post(
        f'{_sb_url()}/rest/v1/pong_sermons',
        headers=_sb_headers(),
        json={
            'id': sermon_id,
            'sermon_date': date_str,
            'title': title,
            'church_year': church_year,
            'preacher': '龐君華牧師',
            'location': '城中教會',
            'is_published': False,
        },
    )
    if r.status_code in (200, 201):
        return r.json()[0]['id']
    # 衝突（已存在）直接查回來
    return sermon_id


#  批次檔案解析

def parse_batch_file(path):
    """
    解析格式：
        YYYY-MM-DD 標題
        https://www.youtube.com/...

        YYYY-MM-DD 標題
        ...
    回傳 list of {'date': str, 'title': str, 'url': str}
    """
    entries = []
    lines = Path(path).read_text(encoding='utf-8').splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        # 嘗試解析日期行
        m = re.match(r'^(\d{4}-\d{2}-\d{2})\s+(.*)', line)
        if m:
            date = m.group(1)
            title = re.sub(r'\.mpg|\.mp4|\.avi|\.mov', '', m.group(2).strip())
            # 下一行應為 URL
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and lines[j].strip().startswith('http'):
                url = lines[j].strip()
                entries.append({'date': date, 'title': title, 'url': url})
                i = j + 1
                continue
        i += 1
    return entries


#  單筆處理邏輯

def process_single(url, date_override, title_override, lang, auto_yes):
    youtube_id = extract_youtube_id(url)
    print(f'\n[YT] YouTube ID: {youtube_id}')

    meta  = fetch_youtube_metadata(url)
    title = title_override or meta['title']
    date  = date_override or meta['upload_date']

    print(f' 標題：{title}')
    print(f' 日期：{date}')
    print(f'  時長：{meta["duration"]} 秒（{meta["duration"]//60} 分鐘）')

    # 非龐牧師講道就跳過
    SKIP_KEYWORDS = ['別人', '來賓', '特別講員', '主持人', '他人講道']
    for kw in SKIP_KEYWORDS:
        if kw in title:
            print(f'[SKIP] 標題含「{kw}」，非龐牧師講道，跳過。')
            return False

    # 比對講道資料庫
    sermon = find_sermon_by_date(date) if date else None

    if sermon:
        print(f'\n[DB] 找到對應講道：[{sermon["id"]}] {sermon["title"]} ({sermon["sermon_date"]})')
        if sermon.get('media_id'):
            print(f'[SKIP] 此講道已有 media_id={sermon["media_id"]}，跳過。')
            return False
    else:
        print(f'\n[DB] 未找到 {date} 的講道記錄，自動建立 pong_sermons...')
        new_id = insert_sermon(date, title)
        sermon = {'id': new_id, 'title': title, 'sermon_date': date, 'media_id': None, 'content': None}
        print(f'[DB] 已建立 pong_sermons id={new_id}')

    # 下載音訊 + 轉錄
    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = Path(tmpdir) / f'{youtube_id}.mp3'
        download_audio(url, audio_path)
        transcript = transcribe(audio_path, lang)

    # 段落格式化
    content = reformat_whisper(transcript)
    para_count = content.count('\n') + 1

    # 預覽
    print('\n' + '─' * 60)
    print('逐字稿前 400 字：')
    print(transcript[:400])
    print(f'\n段落數：{para_count}')
    print('─' * 60 + '\n')

    if auto_yes:
        print('（--yes 自動確認）')
    else:
        confirm = input('確認寫入資料庫？(y/N) ').strip().lower()
        if confirm != 'y':
            print('已取消，未寫入任何資料。')
            return False

    # 寫入 pong_media
    media_id = insert_media(
        youtube_id=youtube_id,
        title=title,
        duration=meta['duration'],
        transcript=transcript,
        description=meta['description'],
        thumbnail=meta['thumbnail'],
        broadcast_date=date,
    )
    print(f'[OK] 已建立 pong_media id={media_id}')

    # 連結 pong_sermons（含 content 與 title）
    if sermon:
        existing_content = sermon.get('content') or ''
        write_content = content if not existing_content.strip() else None
        link_sermon(sermon['id'], media_id, title, write_content)
        wrote = '（已寫入 content）' if write_content else '（content 已有，略過）'
        print(f'[OK] 已連結 pong_sermons [{sermon["id"]}] <- media_id={media_id} {wrote}')
    else:
        print(f'[--] 未連結講道（pong_media id={media_id} 已儲存）')

    return True


#  主流程

def main():
    parser = argparse.ArgumentParser(
        description='龐會督講道流水線：YouTube  逐字稿  資料庫'
    )
    parser.add_argument('url', nargs='?', help='YouTube 影片網址（批次模式可省略）')
    parser.add_argument('--batch-file', help='批次清單 txt 路徑（每條：日期標題行 + URL 行）')
    parser.add_argument('--date',  help='講道日期 YYYY-MM-DD（不填則用影片上傳日）')
    parser.add_argument('--lang',  default='zh',
                        help='語言代碼（預設 zh，英文 en，自動偵測 auto）')
    parser.add_argument('--title', help='手動指定標題')
    parser.add_argument('--yes',   action='store_true', help='跳過確認，自動寫入')
    args = parser.parse_args()

    if args.batch_file:
        entries = parse_batch_file(args.batch_file)
        print(f'[批次] 共讀入 {len(entries)} 筆，開始處理...\n')
        ok = skipped = failed = 0
        for idx, entry in enumerate(entries, 1):
            print(f'\n{"="*60}')
            print(f'[{idx}/{len(entries)}] {entry["date"]} {entry["title"]}')
            print(f'{"="*60}')
            if '別人' in entry['title']:
                print('[SKIP] 非龐牧師講道，跳過。')
                skipped += 1
                continue
            # 先查資料庫，若已有 media_id 直接跳過（不呼叫 yt-dlp）
            existing = find_sermon_by_date(entry['date'])
            if existing and existing.get('media_id'):
                print(f'[SKIP] {entry["date"]} 已有 media_id={existing["media_id"]}，略過。')
                skipped += 1
                continue
            try:
                result = process_single(
                    url=entry['url'],
                    date_override=entry['date'],
                    title_override=entry['title'],
                    lang=args.lang,
                    auto_yes=args.yes,
                )
                if result:
                    ok += 1
                else:
                    skipped += 1
            except Exception as e:
                print(f'[ERROR] {entry["date"]} 失敗：{e}')
                failed += 1
            # 每筆完成後等一段時間，像人類一樣
            wait = random.uniform(15, 35)
            print(f'  [等待 {wait:.0f} 秒再處理下一筆...]')
            time.sleep(wait)
        print(f'\n[批次完成] 成功={ok} 跳過={skipped} 失敗={failed}')

    elif args.url:
        process_single(
            url=args.url,
            date_override=args.date,
            title_override=args.title,
            lang=args.lang,
            auto_yes=args.yes,
        )
        print('\n[完成]')

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
