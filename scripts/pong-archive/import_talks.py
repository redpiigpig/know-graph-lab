#!/usr/bin/env python3
"""
import_talks.py
下載演講音訊 → Whisper 轉錄 → 寫入 pong_media（media_type='talk'）

用法：
  python scripts/import_talks.py
"""

import os
import re
import sys
import json
import tempfile
import subprocess
import ctypes as _ctypes
from pathlib import Path

# Windows：預載 CUDA DLL
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

YTDLP_PATH = r'C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\Scripts\yt-dlp.exe'

TALKS = [
    {
        'youtube_id': '9aWpePHshxE',
        'youtube_start': 28,
        'media_type': 'talk',
        'title': '負責的恩典：當代門徒與受苦的世界',
        'broadcast_date': '2018-11-22',
        'source': '2018苦難神學研討會',
        'source_en': '2018 Theology of Suffering Symposium',
        'program_name': '身心障礙者與福音的對遇',
        'location': '天主教大坪林聖三堂',
        'interviewer': '董倫賢牧師（引言）',
        'description': '2018年苦難神學研討會主題演講。龐君華牧師探討當代門徒如何在受苦的世界中活出「負責的恩典」，並正視身心障礙者與福音相遇的神學課題。',
        'tags': ['苦難神學', '門徒訓練', '身心障礙', '恩典'],
        'lang': 'zh',
    },
    {
        'youtube_id': 'Px2I24CRPxo',
        'youtube_start': 23,
        'media_type': 'talk',
        'title': '門徒：有別於世界的信仰群體',
        'broadcast_date': '2019-10-01',
        'source': '聖光神學院',
        'source_en': 'Taiwan Theological Seminary and College',
        'program_name': '',
        'location': '聖光神學院',
        'interviewer': '',
        'description': '龐君華牧師於聖光神學院演講，探討門徒身分的核心意義——信仰群體如何成為「有別於世界」的見證。',
        'tags': ['門徒訓練', '信仰群體', '教會'],
        'lang': 'zh',
    },
    {
        'youtube_id': 'YrtfxTB6_i4',
        'youtube_start': 0,
        'media_type': 'talk',
        'title': '主共同體的成聖：約翰衛斯理小組和教會更新運動',
        'broadcast_date': '2015-03-24',
        'source': '衛斯理學術研討會',
        'source_en': 'Wesleyan Academic Symposium',
        'program_name': '',
        'location': '聖光神學院',
        'interviewer': '',
        'description': '龐君華牧師於衛斯理學術研討會發表，探討約翰衛斯理的小組傳統與教會更新運動，如何透過主共同體的實踐走向成聖。',
        'tags': ['成聖', '衛斯理神學', '信仰群體', '學術'],
        'lang': 'zh',
    },
]

# 短影音（media_type='short'，不需要 Whisper 轉錄）
SHORTS = [
    {
        'youtube_id': 'ELO7ztJints',
        'media_type': 'short',
        'title': '如果有人問：基督徒的「修道方式」是什麼？',
        'broadcast_date': '2025-12-04',
        'source': '台灣聖公會三一書院',
        'source_en': 'Trinity Institute, Episcopal Church in Taiwan',
        'description': '龐君華牧師簡答「基督徒的修道方式是什麼？」',
        'tags': ['修道主義', '靈修', '門徒訓練'],
    },
    {
        'youtube_id': 'uU1d2ZF_Eq8',
        'media_type': 'short',
        'title': '每天一點點，生命就開始翻轉',
        'broadcast_date': '2025-12-09',
        'source': '台灣聖公會三一書院',
        'source_en': 'Trinity Institute, Episcopal Church in Taiwan',
        'description': '龐君華牧師：每天一點點的靈修積累，生命就開始翻轉。',
        'tags': ['靈修', '門徒訓練', '生命成長'],
    },
    {
        'youtube_id': 'SC8Ae6NxwMU',
        'media_type': 'short',
        'title': '來自會督的問候',
        'broadcast_date': '2021-06-06',
        'source': '龐君華會督',
        'description': '龐君華會督親口向信眾問候。',
        'tags': ['問候', '會督信息'],
    },
]


def sb_url():
    return os.environ['VITE_SUPABASE_URL'].rstrip('/')

def sb_headers(prefer='return=minimal'):
    return {
        'apikey': os.environ['SUPABASE_SERVICE_KEY'],
        'Authorization': f'Bearer {os.environ["SUPABASE_SERVICE_KEY"]}',
        'Content-Type': 'application/json',
        'Prefer': prefer,
    }


def check_existing(youtube_id):
    r = requests.get(
        f'{sb_url()}/rest/v1/pong_media?youtube_id=eq.{youtube_id}&select=id,title,transcript',
        headers=sb_headers(),
        timeout=30,
    )
    data = r.json()
    return data[0] if data else None


def patch_transcript(item_id, transcript):
    r = requests.patch(
        f'{sb_url()}/rest/v1/pong_media?id=eq.{item_id}',
        headers=sb_headers(),
        json={'transcript': transcript},
        timeout=60,
    )
    if r.status_code in (200, 204):
        print(f'  ✅ 逐字稿更新成功，id={item_id}')
    else:
        print(f'  ❌ 更新失敗：{r.status_code} {r.text[:300]}')


def download_audio(youtube_id, start_sec, tmpdir):
    url = f'https://www.youtube.com/watch?v={youtube_id}'
    out = str(Path(tmpdir) / f'{youtube_id}.%(ext)s')
    cmd = [
        YTDLP_PATH,
        '--no-playlist',
        '-f', 'bestaudio[ext=m4a]/bestaudio/best',
        '-o', out,
        '--no-warnings',
        url,
    ]
    print(f'  下載音訊：{youtube_id} ...')
    subprocess.run(cmd, check=True)
    files = list(Path(tmpdir).glob(f'{youtube_id}.*'))
    if not files:
        raise FileNotFoundError(f'找不到下載的音訊：{youtube_id}')
    return str(files[0])


def transcribe(audio_path, youtube_id, lang='zh', start_sec=0):
    from faster_whisper import WhisperModel
    print(f'  載入 Whisper 模型...')
    model = WhisperModel('large-v3-turbo', device='cuda', compute_type='float16')
    print(f'  開始轉錄（語言：{lang}，從第 {start_sec} 秒）...')
    segments, info = model.transcribe(
        audio_path,
        language=lang,
        condition_on_previous_text=True,
        vad_filter=True,
        clip_timestamps=[start_sec] if start_sec else None,
    )
    text_parts = []
    for seg in segments:
        text_parts.append(seg.text.strip())
    full_text = '\n'.join(t for t in text_parts if t)
    print(f'  轉錄完成，共 {len(full_text)} 字元')

    # 立即存檔，在 GPU 資源釋放前完成
    out = Path(__file__).parent.parent / 'stores' / 'transcripts' / f'{youtube_id}.txt'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(full_text, encoding='utf-8')
    print(f'  💾 已存檔：{out}')

    del model  # 明確釋放 GPU 資源
    return full_text


def get_upload_date(youtube_id):
    """從 yt-dlp 取得影片上傳日期（YYYY-MM-DD），用於沒有明確日期的短影音。"""
    try:
        result = subprocess.run(
            [YTDLP_PATH, '--dump-json', '--no-playlist',
             f'https://www.youtube.com/watch?v={youtube_id}'],
            capture_output=True, text=True, check=True, encoding='utf-8'
        )
        data = json.loads(result.stdout)
        raw = data.get('upload_date', '')
        if raw and len(raw) == 8:
            return f'{raw[:4]}-{raw[4:6]}-{raw[6:]}'
    except Exception as e:
        print(f'  ⚠ 無法取得上傳日期：{e}')
    return None


def save_transcript_file(youtube_id, transcript):
    out = Path(__file__).parent.parent / 'stores' / 'transcripts' / f'{youtube_id}.txt'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(transcript, encoding='utf-8')
    print(f'  💾 逐字稿備份：{out}')


def insert_to_db(item, transcript=None):
    youtube_id = item['youtube_id']
    broadcast_date = item.get('broadcast_date')
    if not broadcast_date:
        broadcast_date = get_upload_date(youtube_id)

    is_short = item.get('media_type') == 'short'
    url = (f'https://www.youtube.com/shorts/{youtube_id}'
           if is_short else f'https://www.youtube.com/watch?v={youtube_id}')

    if transcript:
        save_transcript_file(youtube_id, transcript)

    payload = {
        'title': item['title'],
        'source': item.get('source', ''),
        'source_en': item.get('source_en', '') or None,
        'program_name': item.get('program_name', '') or None,
        'interviewer': item.get('interviewer', '') or None,
        'media_type': item.get('media_type', 'talk'),
        'platform': 'youtube',
        'youtube_id': youtube_id,
        'youtube_start': item.get('youtube_start', 0) or None,
        'url': url,
        'broadcast_date': broadcast_date,
        'transcript': transcript,
        'description': item.get('description', ''),
        'tags': item.get('tags', []),
        'is_published': True,
    }
    print('  正在寫入資料庫...')
    r = requests.post(
        f'{sb_url()}/rest/v1/pong_media',
        headers=sb_headers(),
        json=payload,
        timeout=60,
    )
    print(f'  HTTP {r.status_code}')
    if r.status_code not in (200, 201):
        print(f'  ❌ 寫入失敗：{r.text[:300]}')
        return None
    print(f'  ✅ 寫入成功')
    return True


def process_talk(talk):
    print(f'\n═══ 處理演講：{talk["title"]} ({talk["broadcast_date"]}) ═══')
    existing = check_existing(talk['youtube_id'])
    if existing:
        if existing.get('transcript'):
            print(f'  已存在且有逐字稿：id={existing["id"]}，跳過')
            return
        else:
            print(f'  已存在但無逐字稿（id={existing["id"]}），補跑轉錄...')
            with tempfile.TemporaryDirectory() as tmpdir:
                audio_path = download_audio(talk['youtube_id'], talk.get('youtube_start', 0), tmpdir)
                transcript = transcribe(audio_path, talk['youtube_id'], lang=talk.get('lang', 'zh'), start_sec=talk.get('youtube_start', 0))
                patch_transcript(existing['id'], transcript)
            return

    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = download_audio(talk['youtube_id'], talk.get('youtube_start', 0), tmpdir)
        transcript = transcribe(audio_path, talk['youtube_id'], lang=talk.get('lang', 'zh'), start_sec=talk.get('youtube_start', 0))
        insert_to_db(talk, transcript)


def process_short(short):
    print(f'\n═══ 處理短影音：{short["title"]} ═══')
    existing = check_existing(short['youtube_id'])
    if existing:
        print(f'  已存在：id={existing["id"]}，跳過')
        return
    insert_to_db(short, transcript=None)


if __name__ == '__main__':
    for talk in TALKS:
        try:
            process_talk(talk)
        except Exception as e:
            print(f'  ❌ 錯誤：{e}')
            import traceback; traceback.print_exc()

    for short in SHORTS:
        try:
            process_short(short)
        except Exception as e:
            print(f'  ❌ 錯誤：{e}')
            import traceback; traceback.print_exc()

    print('\n全部完成。')
