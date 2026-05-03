#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pipeline: download PDFs from 1day3read3pray.com → extract text → parse → upload to Supabase
Usage: python scripts/lectionary_pipeline.py [--dry-run] [--year A|B|C] [--season advent]
"""

import os, re, sys, json, time, requests, io
from pathlib import Path
import pdfplumber

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ── .env loader ───────────────────────────────────────────────────────────────
def load_env():
    env = {}
    env_path = Path(__file__).parent.parent / '.env'
    for raw in env_path.read_text(encoding='utf-8').splitlines():
        line = raw.strip().strip('"').strip("'")
        m = re.match(r'^([^#=]+)=(.*)$', line)
        if m:
            k, v = m.group(1).strip(), m.group(2).strip().strip('"').strip("'")
            env[k] = v
    return env

ENV = load_env()
SB_URL  = ENV.get('VITE_SUPABASE_URL', '')
SB_KEY  = ENV.get('SUPABASE_SERVICE_KEY', '')
PDF_DIR = Path(__file__).parent.parent / 'stores' / '三讀三禱'
PDF_DIR.mkdir(exist_ok=True)

DRY_RUN   = '--dry-run' in sys.argv
FILTER_Y  = next((a.split('=')[1] for a in sys.argv if a.startswith('--year=')), None)
FILTER_S  = next((a.split('=')[1] for a in sys.argv if a.startswith('--season=')), None)

BASE = 'https://www.1day3read3pray.com/wp-content/uploads'

# ── Week manifest ─────────────────────────────────────────────────────────────
# url: use /download/XXXXX/ (no tmstv needed) or direct .pdf URL
# week_num: sequential starting from 1 within the season for a given year
# title: None means auto-extract from PDF cover/day header

WEEKS = [
  # ── 甲年 Year A 2025-2026 ──────────────────────────────────────────────────
  # Advent 1-4 already seeded, skipped here
  # Christmas
  {'year':'A','season':'christmas','week_num':1,'title':'聖誕期第一週',
   'date_range':'2025.12.28–2026.01.04','url':'https://www.1day3read3pray.com/download/11784/'},
  {'year':'A','season':'christmas','week_num':2,'title':'聖誕期第二週',
   'date_range':'2026.01.04–01.11','url':'https://www.1day3read3pray.com/download/12612/'},
  # Epiphany
  {'year':'A','season':'epiphany','week_num':1,'title':'顯現期第一週（耶穌受洗）',
   'date_range':'2026.01.11–01.18','url':'https://www.1day3read3pray.com/download/12737/'},
  {'year':'A','season':'epiphany','week_num':2,'title':'顯現期第二週',
   'date_range':'2026.01.18–01.25','url':'https://www.1day3read3pray.com/download/12958/'},
  {'year':'A','season':'epiphany','week_num':3,'title':'顯現期第三週',
   'date_range':'2026.01.25–02.01','url':'https://www.1day3read3pray.com/download/12981/'},
  {'year':'A','season':'epiphany','week_num':4,'title':'顯現期第四週',
   'date_range':'2026.02.01–02.08','url':'https://www.1day3read3pray.com/download/13013/'},
  {'year':'A','season':'epiphany','week_num':5,'title':'顯現期第五週',
   'date_range':'2026.02.08–02.15','url':'https://www.1day3read3pray.com/download/13023/'},
  {'year':'A','season':'epiphany','week_num':6,'title':'顯現期第六週（登山變像）',
   'date_range':'2026.02.15–02.22','url':'https://www.1day3read3pray.com/download/13080/'},
  # Lent
  {'year':'A','season':'lent','week_num':1,'title':'大齋期第一週',
   'date_range':'2026.02.22–03.01','url':'https://www.1day3read3pray.com/download/13180/'},
  {'year':'A','season':'lent','week_num':2,'title':'大齋期第二週',
   'date_range':'2026.03.01–03.08','url':'https://www.1day3read3pray.com/download/13190/'},
  {'year':'A','season':'lent','week_num':3,'title':'大齋期第三週',
   'date_range':'2026.03.08–03.15','url':'https://www.1day3read3pray.com/download/13206/'},
  {'year':'A','season':'lent','week_num':4,'title':'大齋期第四週',
   'date_range':'2026.03.15–03.22','url':'https://www.1day3read3pray.com/download/13281/'},
  {'year':'A','season':'lent','week_num':5,'title':'大齋期第五週',
   'date_range':'2026.03.22–03.29','url':'https://www.1day3read3pray.com/download/13293/'},
  {'year':'A','season':'lent','week_num':6,'title':'大齋期第六週（棕枝主日）',
   'date_range':'2026.03.29–04.05','url':'https://www.1day3read3pray.com/download/13303/'},
  # Easter
  {'year':'A','season':'easter','week_num':1,'title':'復活期第一週（復活節）',
   'date_range':'2026.04.05–04.12','url':'https://www.1day3read3pray.com/download/13315/'},
  {'year':'A','season':'easter','week_num':2,'title':'復活期第二週',
   'date_range':'2026.04.12–04.19','url':'https://www.1day3read3pray.com/download/13377/'},
  {'year':'A','season':'easter','week_num':3,'title':'復活期第三週',
   'date_range':'2026.04.19–04.26','url':'https://www.1day3read3pray.com/download/13387/'},
  {'year':'A','season':'easter','week_num':4,'title':'復活期第四週（善牧主日）',
   'date_range':'2026.04.26–05.03','url':'https://www.1day3read3pray.com/download/13525/'},

  # ── 丙年 Year C 2024-2025 ──────────────────────────────────────────────────
  # Advent
  {'year':'C','season':'advent','week_num':1,'title':'將臨期第一週（希望）',
   'date_range':'2024.12.01–12.08','url':f'{BASE}/2024/11/20241201-Year-C-Advent-wk1.pdf'},
  {'year':'C','season':'advent','week_num':2,'title':'將臨期第二週（平安）',
   'date_range':'2024.12.08–12.15','url':f'{BASE}/2024/12/20241208-Year-C-Advent-wk2.pdf'},
  {'year':'C','season':'advent','week_num':3,'title':'將臨期第三週（喜樂）',
   'date_range':'2024.12.15–12.22','url':f'{BASE}/2024/12/20241215-Year-C-Advent-wk3.pdf'},
  {'year':'C','season':'advent','week_num':4,'title':'將臨期第四週（愛）',
   'date_range':'2024.12.22–12.29','url':f'{BASE}/2024/12/20241222-Year-C-Advent-wk4.pdf'},
  # Christmas
  {'year':'C','season':'christmas','week_num':1,'title':'聖誕期第一週',
   'date_range':'2024.12.29–2025.01.05','url':f'{BASE}/2024/12/20241229-Year-C-Christmas-wk1.pdf'},
  {'year':'C','season':'christmas','week_num':2,'title':'聖誕期第二週',
   'date_range':'2025.01.05–01.12','url':f'{BASE}/2025/01/20250105-Year-C-Christmas-wk2.pdf'},
  # Epiphany
  {'year':'C','season':'epiphany','week_num':1,'title':'顯現期第一週（耶穌受洗）',
   'date_range':'2025.01.12–01.19','url':f'{BASE}/2025/01/20250112-Year-C-Epiphany-aft-wk1.pdf'},
  {'year':'C','season':'epiphany','week_num':2,'title':'顯現期第二週',
   'date_range':'2025.01.19–01.26','url':f'{BASE}/2025/01/20250119-Year-C-Epiphany-aft-wk2.pdf'},
  {'year':'C','season':'epiphany','week_num':3,'title':'顯現期第三週',
   'date_range':'2025.01.26–02.02','url':f'{BASE}/2025/01/20250126-Year-C-Epiphany-aft-wk3.pdf'},
  {'year':'C','season':'epiphany','week_num':4,'title':'顯現期第四週',
   'date_range':'2025.02.02–02.09','url':f'{BASE}/2025/02/20250202-Year-C-Epiphany-aft-wk4.pdf'},
  {'year':'C','season':'epiphany','week_num':5,'title':'顯現期第五週',
   'date_range':'2025.02.09–02.16','url':f'{BASE}/2025/02/20250209-Year-C-Epiphany-aft-wk5.pdf'},
  {'year':'C','season':'epiphany','week_num':6,'title':'顯現期第六週',
   'date_range':'2025.02.16–02.23','url':f'{BASE}/2025/02/20250216-Year-C-Epiphany-aft-wk6.pdf'},
  {'year':'C','season':'epiphany','week_num':7,'title':'顯現期第七週',
   'date_range':'2025.02.23–03.02','url':f'{BASE}/2025/02/20250223-Year-C-Epiphany-aft-wk7.pdf'},
  {'year':'C','season':'epiphany','week_num':8,'title':'顯現期第八週（登山變像）',
   'date_range':'2025.03.02–03.09','url':f'{BASE}/2025/03/20250302-Year-CTransfiguration.pdf'},
  # Lent
  {'year':'C','season':'lent','week_num':1,'title':'大齋期第一週',
   'date_range':'2025.03.09–03.16','url':f'{BASE}/2025/03/20250309-Year-C-Lent-wk1.pdf'},
  {'year':'C','season':'lent','week_num':2,'title':'大齋期第二週',
   'date_range':'2025.03.16–03.23','url':f'{BASE}/2025/03/20250316-Year-C-Lent-wk2.pdf'},
  {'year':'C','season':'lent','week_num':3,'title':'大齋期第三週',
   'date_range':'2025.03.23–03.30','url':f'{BASE}/2025/03/20250323-Year-C-Lent-wk3.pdf'},
  {'year':'C','season':'lent','week_num':4,'title':'大齋期第四週',
   'date_range':'2025.03.30–04.06','url':f'{BASE}/2025/03/20250330-Year-C-Lent-wk4.pdf'},
  {'year':'C','season':'lent','week_num':5,'title':'大齋期第五週',
   'date_range':'2025.04.06–04.13','url':f'{BASE}/2025/04/20250406-Year-C-Lent-wk5.pdf'},
  {'year':'C','season':'lent','week_num':6,'title':'大齋期第六週（棕枝主日）',
   'date_range':'2025.04.13–04.20','url':f'{BASE}/2025/04/20250413-Year-C-Lent-wk6Palm.pdf'},
  # Easter
  {'year':'C','season':'easter','week_num':1,'title':'復活期第一週（復活節）',
   'date_range':'2025.04.20–04.27','url':f'{BASE}/2025/04/20250420-Year-C-Easter.pdf'},
  {'year':'C','season':'easter','week_num':2,'title':'復活期第二週',
   'date_range':'2025.04.27–05.04','url':f'{BASE}/2025/04/20250427-Year-C-Easter-wk2.pdf'},
  {'year':'C','season':'easter','week_num':3,'title':'復活期第三週',
   'date_range':'2025.05.04–05.11','url':f'{BASE}/2025/05/20250504-Year-C-Easter-wk3.pdf'},
  {'year':'C','season':'easter','week_num':4,'title':'復活期第四週（善牧主日）',
   'date_range':'2025.05.11–05.18','url':f'{BASE}/2025/05/20250511-Year-C-Easter-wk4.pdf'},
  {'year':'C','season':'easter','week_num':5,'title':'復活期第五週',
   'date_range':'2025.05.18–05.25','url':f'{BASE}/2025/05/20250518-Year-C-Easter-wk5.pdf'},
  {'year':'C','season':'easter','week_num':6,'title':'復活期第六週',
   'date_range':'2025.05.25–06.01','url':f'{BASE}/2025/05/20250525-Year-C-Easter-wk6.pdf'},
  {'year':'C','season':'easter','week_num':7,'title':'復活期第七週（聖靈降臨節）',
   'date_range':'2025.06.01–06.08','url':f'{BASE}/2025/05/20250601-Year-C-Easter-wk7.pdf'},
  # Pentecost (sequential 1-25, starting from Trinity Sunday June 15)
  {'year':'C','season':'pentecost','week_num':1,'title':'聖靈降臨後第一週（三一主日）',
   'date_range':'2025.06.08–06.15','url':'https://www.1day3read3pray.com/download/9922/'},
  {'year':'C','season':'pentecost','week_num':2,'title':'聖靈降臨後第二週',
   'date_range':'2025.06.15–06.22','url':'https://www.1day3read3pray.com/download/9919/'},
  {'year':'C','season':'pentecost','week_num':3,'title':'聖靈降臨後第三週',
   'date_range':'2025.06.22–06.29','url':'https://www.1day3read3pray.com/download/9998/'},
  {'year':'C','season':'pentecost','week_num':4,'title':'聖靈降臨後第四週',
   'date_range':'2025.06.29–07.06','url':'https://www.1day3read3pray.com/download/10080/'},
  {'year':'C','season':'pentecost','week_num':5,'title':'聖靈降臨後第五週',
   'date_range':'2025.07.06–07.13','url':'https://www.1day3read3pray.com/download/10153/'},
  {'year':'C','season':'pentecost','week_num':6,'title':'聖靈降臨後第六週',
   'date_range':'2025.07.13–07.20','url':'https://www.1day3read3pray.com/download/10251/'},
  {'year':'C','season':'pentecost','week_num':7,'title':'聖靈降臨後第七週',
   'date_range':'2025.07.20–07.27','url':'https://www.1day3read3pray.com/download/10341/'},
  {'year':'C','season':'pentecost','week_num':8,'title':'聖靈降臨後第八週',
   'date_range':'2025.07.27–08.03','url':'https://www.1day3read3pray.com/download/10414/'},
  {'year':'C','season':'pentecost','week_num':9,'title':'聖靈降臨後第九週',
   'date_range':'2025.08.03–08.10','url':'https://www.1day3read3pray.com/download/10474/'},
  {'year':'C','season':'pentecost','week_num':10,'title':'聖靈降臨後第十週',
   'date_range':'2025.08.10–08.17','url':'https://www.1day3read3pray.com/download/10582/'},
  {'year':'C','season':'pentecost','week_num':11,'title':'聖靈降臨後第十一週',
   'date_range':'2025.08.17–08.24','url':'https://www.1day3read3pray.com/download/10646/'},
  {'year':'C','season':'pentecost','week_num':12,'title':'聖靈降臨後第十二週',
   'date_range':'2025.08.24–08.31','url':'https://www.1day3read3pray.com/download/10703/'},
  {'year':'C','season':'pentecost','week_num':13,'title':'聖靈降臨後第十三週',
   'date_range':'2025.08.31–09.07','url':'https://www.1day3read3pray.com/download/10766/'},
  {'year':'C','season':'pentecost','week_num':14,'title':'聖靈降臨後第十四週',
   'date_range':'2025.09.07–09.14','url':'https://www.1day3read3pray.com/download/10911/'},
  {'year':'C','season':'pentecost','week_num':15,'title':'聖靈降臨後第十五週',
   'date_range':'2025.09.14–09.21','url':'https://www.1day3read3pray.com/download/10949/'},
  {'year':'C','season':'pentecost','week_num':16,'title':'聖靈降臨後第十六週',
   'date_range':'2025.09.21–09.28','url':'https://www.1day3read3pray.com/download/11011/'},
  {'year':'C','season':'pentecost','week_num':17,'title':'聖靈降臨後第十七週',
   'date_range':'2025.09.28–10.05','url':'https://www.1day3read3pray.com/download/11052/'},
  {'year':'C','season':'pentecost','week_num':18,'title':'聖靈降臨後第十八週',
   'date_range':'2025.10.05–10.12','url':'https://www.1day3read3pray.com/download/11087/'},
  {'year':'C','season':'pentecost','week_num':19,'title':'聖靈降臨後第十九週',
   'date_range':'2025.10.12–10.19','url':'https://www.1day3read3pray.com/download/11127/'},
  {'year':'C','season':'pentecost','week_num':20,'title':'聖靈降臨後第二十週',
   'date_range':'2025.10.19–10.26','url':'https://www.1day3read3pray.com/download/11210/'},
  {'year':'C','season':'pentecost','week_num':21,'title':'聖靈降臨後第廿一週',
   'date_range':'2025.10.26–11.02','url':'https://www.1day3read3pray.com/download/11242/'},
  {'year':'C','season':'pentecost','week_num':22,'title':'聖靈降臨後第廿二週',
   'date_range':'2025.11.02–11.09','url':'https://www.1day3read3pray.com/download/11326/'},
  {'year':'C','season':'pentecost','week_num':23,'title':'聖靈降臨後第廿三週',
   'date_range':'2025.11.09–11.16','url':'https://www.1day3read3pray.com/download/11343/'},
  {'year':'C','season':'pentecost','week_num':24,'title':'聖靈降臨後第廿四週',
   'date_range':'2025.11.16–11.23','url':'https://www.1day3read3pray.com/download/11355/'},
  {'year':'C','season':'pentecost','week_num':25,'title':'聖靈降臨後第廿五週',
   'date_range':'2025.11.23–11.30','url':'https://www.1day3read3pray.com/download/11414/'},

  # ── 乙年 Year B 2023-2024 ──────────────────────────────────────────────────
  # Advent
  {'year':'B','season':'advent','week_num':1,'title':'將臨期第一週',
   'date_range':'2023.12.03–12.09','url':'#'},
  {'year':'B','season':'advent','week_num':2,'title':'將臨期第二週',
   'date_range':'2023.12.10–12.16','url':'#'},
  {'year':'B','season':'advent','week_num':3,'title':'將臨期第三週',
   'date_range':'2023.12.17–12.23','url':'#'},
  {'year':'B','season':'advent','week_num':4,'title':'將臨期第四週',
   'date_range':'2023.12.24–12.30','url':'#'},
  # Christmas
  {'year':'B','season':'christmas','week_num':1,'title':'聖誕節期第一週',
   'date_range':'2023.12.31–2024.01.06','url':'#'},
  # Epiphany
  {'year':'B','season':'epiphany','week_num':1,'title':'顯現節後第一週',
   'date_range':'2024.01.07–01.13','url':'#'},
  {'year':'B','season':'epiphany','week_num':2,'title':'顯現節後第二週',
   'date_range':'2024.01.14–01.20','url':'#'},
  {'year':'B','season':'epiphany','week_num':3,'title':'顯現節後第三週',
   'date_range':'2024.01.21–01.27','url':'#'},
  {'year':'B','season':'epiphany','week_num':4,'title':'顯現節後第四週',
   'date_range':'2024.01.28–02.03','url':'#'},
  {'year':'B','season':'epiphany','week_num':5,'title':'顯現節後第五週',
   'date_range':'2024.02.04–02.10','url':'#'},
  {'year':'B','season':'epiphany','week_num':6,'title':'顯現節後第六週及大齋期開始',
   'date_range':'2024.02.11–02.17','url':'#'},
  # Lent
  {'year':'B','season':'lent','week_num':1,'title':'大齋期第一週',
   'date_range':'2024.02.18–02.24','url':'#'},
  {'year':'B','season':'lent','week_num':2,'title':'大齋期第二週',
   'date_range':'2024.02.25–03.02','url':'#'},
  {'year':'B','season':'lent','week_num':3,'title':'大齋期第三週',
   'date_range':'2024.03.03–03.09','url':'#'},
  {'year':'B','season':'lent','week_num':4,'title':'大齋期第四週',
   'date_range':'2024.03.10–03.16','url':'#'},
  {'year':'B','season':'lent','week_num':5,'title':'大齋期第五週',
   'date_range':'2024.03.17–03.23','url':'#'},
  {'year':'B','season':'lent','week_num':6,'title':'聖週（棕枝主日）',
   'date_range':'2024.03.24–03.30','url':'#'},
  # Easter
  {'year':'B','season':'easter','week_num':1,'title':'復活期第一週（復活節）',
   'date_range':'2024.03.31–04.06','url':'#'},
  {'year':'B','season':'easter','week_num':2,'title':'復活期第二週',
   'date_range':'2024.04.07–04.13','url':'#'},
  {'year':'B','season':'easter','week_num':3,'title':'復活期第三週',
   'date_range':'2024.04.14–04.20','url':'#'},
  {'year':'B','season':'easter','week_num':4,'title':'復活期第四週（善牧主日）',
   'date_range':'2024.04.21–04.27','url':'#'},
  {'year':'B','season':'easter','week_num':5,'title':'復活期第五週',
   'date_range':'2024.04.28–05.04','url':'#'},
  {'year':'B','season':'easter','week_num':6,'title':'復活期第六週',
   'date_range':'2024.05.05–05.11','url':'#'},
  {'year':'B','season':'easter','week_num':7,'title':'復活期第七週',
   'date_range':'2024.05.12–05.18','url':'#'},
  # Pentecost
  {'year':'B','season':'pentecost','week_num':1,'title':'聖靈降臨期第一週',
   'date_range':'2024.05.19–05.25','url':'#'},
  {'year':'B','season':'pentecost','week_num':2,'title':'聖靈降臨期第二週',
   'date_range':'2024.05.26–06.01','url':'#'},
  {'year':'B','season':'pentecost','week_num':3,'title':'聖靈降臨期第三週',
   'date_range':'2024.06.02–06.08','url':'#'},
  {'year':'B','season':'pentecost','week_num':4,'title':'聖靈降臨期第四週',
   'date_range':'2024.06.09–06.15','url':'#'},
  {'year':'B','season':'pentecost','week_num':5,'title':'聖靈降臨期第五週',
   'date_range':'2024.06.16–06.22','url':'#'},
  {'year':'B','season':'pentecost','week_num':6,'title':'聖靈降臨期第六週',
   'date_range':'2024.06.23–06.29','url':'#'},
  {'year':'B','season':'pentecost','week_num':7,'title':'聖靈降臨期第七週',
   'date_range':'2024.06.30–07.06','url':'#'},
  {'year':'B','season':'pentecost','week_num':8,'title':'聖靈降臨期第八週',
   'date_range':'2024.07.07–07.13','url':'#'},
  {'year':'B','season':'pentecost','week_num':9,'title':'聖靈降臨期第九週',
   'date_range':'2024.07.14–07.20','url':'#'},
  {'year':'B','season':'pentecost','week_num':10,'title':'聖靈降臨期第十週',
   'date_range':'2024.07.21–07.27','url':'#'},
  {'year':'B','season':'pentecost','week_num':11,'title':'聖靈降臨期第十一週',
   'date_range':'2024.07.28–08.03','url':'#'},
  {'year':'B','season':'pentecost','week_num':12,'title':'聖靈降臨期第十二週',
   'date_range':'2024.08.04–08.10','url':'#'},
  {'year':'B','season':'pentecost','week_num':13,'title':'聖靈降臨期第十三週',
   'date_range':'2024.08.11–08.17','url':'#'},
  {'year':'B','season':'pentecost','week_num':14,'title':'聖靈降臨期第十四週',
   'date_range':'2024.08.18–08.24','url':'#'},
  {'year':'B','season':'pentecost','week_num':15,'title':'聖靈降臨期第十五週',
   'date_range':'2024.08.25–08.31','url':'#'},
  {'year':'B','season':'pentecost','week_num':16,'title':'聖靈降臨期第十六週',
   'date_range':'2024.09.01–09.07','url':'#'},
  {'year':'B','season':'pentecost','week_num':17,'title':'聖靈降臨期第十七週',
   'date_range':'2024.09.08–09.14','url':'#'},
  {'year':'B','season':'pentecost','week_num':18,'title':'聖靈降臨期第十八週',
   'date_range':'2024.09.15–09.21','url':'#'},
  {'year':'B','season':'pentecost','week_num':19,'title':'聖靈降臨期第十九週',
   'date_range':'2024.09.22–09.28','url':'#'},
  {'year':'B','season':'pentecost','week_num':20,'title':'聖靈降臨期第二十週',
   'date_range':'2024.09.29–10.05','url':'#'},
  {'year':'B','season':'pentecost','week_num':21,'title':'聖靈降臨期第二十一週',
   'date_range':'2024.10.06–10.12','url':'#'},
  {'year':'B','season':'pentecost','week_num':22,'title':'聖靈降臨期第二十二週',
   'date_range':'2024.10.13–10.19','url':'#'},
  {'year':'B','season':'pentecost','week_num':23,'title':'聖靈降臨期第二十三週',
   'date_range':'2024.10.20–10.26','url':'#'},
  {'year':'B','season':'pentecost','week_num':24,'title':'聖靈降臨期第二十四週',
   'date_range':'2024.10.27–11.02','url':'#'},
  {'year':'B','season':'pentecost','week_num':25,'title':'聖靈降臨期第二十五週',
   'date_range':'2024.11.03–11.09','url':'#'},
  {'year':'B','season':'pentecost','week_num':26,'title':'聖靈降臨期第二十六週',
   'date_range':'2024.11.10–11.16','url':'#'},
  {'year':'B','season':'pentecost','week_num':27,'title':'聖靈降臨期第二十七週',
   'date_range':'2024.11.17–11.23','url':'#'},
  {'year':'B','season':'pentecost','week_num':28,'title':'聖靈降臨期第二十八週',
   'date_range':'2024.11.24–11.30','url':'#'},
]

# ── Download ──────────────────────────────────────────────────────────────────
def download_pdf(url, dest_path):
    if dest_path.exists():
        return True
    print(f'  下載 {url}')
    r = requests.get(url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
    if r.status_code != 200 or b'%PDF' not in r.content[:10]:
        print(f'  ✗ 下載失敗 (status={r.status_code})')
        return False
    dest_path.write_bytes(r.content)
    return True

# ── PDF → text ────────────────────────────────────────────────────────────────
def pdf_to_text(pdf_path):
    pages = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for i, page in enumerate(pdf.pages):
            t = page.extract_text() or ''
            pages.append(f'=== PAGE {i+1} ===\n{t}')
    return '\n'.join(pages)

# ── Parser ────────────────────────────────────────────────────────────────────
DAY_ZH = {'日':0,'一':1,'二':2,'三':3,'四':4,'五':5,'六':6}

KEY_VERSE_TRIGGER2 = re.compile(r'請默禱[，,。]?並專注默想')
READING_TITLE_RE   = re.compile(r'^[一-鿿]{2,8}\s+\d+')
FOOTNOTE_RE        = re.compile(r'^[a-z]\s*\[')

def clean(s):
    return re.sub(r'\s+', ' ', s).strip()

def remove_tab_pages(raw_text):
    """Remove tab navigation pages (pages whose only non-numeric content is day-header lines).
    These 2-3 line pages (e.g. '星期日 (4/26)\\n星期一 (4/27)\\n8') are bookmarks in the
    32-page booklet format and must not be treated as actual day boundaries."""
    def is_tab_page(content):
        lines = [l.strip() for l in content.split('\n') if l.strip()]
        content_lines = [l for l in lines if not re.match(r'^\d{1,2}$', l)]
        return bool(content_lines) and all(
            re.match(r'^星期[日一二三四五六]', l) for l in content_lines
        )
    def replace_page(m):
        return '' if is_tab_page(m.group(1)) else m.group(0)
    return re.sub(
        r'=== PAGE \d+ ===\n((?:(?!=== PAGE)[\s\S])*)',
        replace_page, raw_text
    )

def _get_header_lines(day_text, ec_pos):
    """Return the 1-2 book-title lines that appear just before 【經文】."""
    before = day_text[:ec_pos]
    lines  = before.split('\n')
    result = []
    for line in reversed(lines):
        ls = line.strip()
        if not ls or re.match(r'^\d{1,2}$', ls) or re.match(r'^=== PAGE', ls):
            continue
        if re.match(r'^星期[日一二三四五六]', ls) or re.match(r'^回應', ls) or re.match(r'^預備', ls):
            break
        result.append(ls)
        if len(result) == 2:
            break
    return '\n'.join(reversed(result))

def _get_header_start_pos(day_text, ec_pos):
    """Return the position in day_text where the title before this 【經文】 starts.
    Used to determine where the PREVIOUS reading's content should end."""
    before = day_text[:ec_pos]
    lines  = before.split('\n')
    pos    = len(before)
    found  = 0
    result = 0
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i]
        ls   = line.strip()
        pos -= len(line) + 1
        actual_start = pos + 1
        if not ls or re.match(r'^\d{1,2}$', ls) or re.match(r'^=== PAGE', ls):
            continue
        if re.match(r'^星期[日一二三四五六]', ls) or re.match(r'^回應', ls) or re.match(r'^預備', ls):
            break
        found += 1
        if found == 1:
            result = actual_start
        elif found == 2:
            if READING_TITLE_RE.match(ls):
                result = actual_start  # two-line title
            break
    return max(0, result)

def split_reading(block):
    """Given text of one reading (everything from book-title to next book-title),
    return {book, passage, title, text, meditation, key_verse}."""
    # Split at 【經文】
    if '【經文】' not in block:
        return None
    header, rest = block.split('【經文】', 1)
    # Split at 【默想】
    if '【默想】' not in rest:
        scripture = rest.strip()
        meditation = ''
        key_verse = ''
    else:
        scripture, med_block = rest.split('【默想】', 1)
        # Extract key verse: after "請默禱，並專注默想以下經文"
        kv_match = KEY_VERSE_TRIGGER2.search(med_block)
        if kv_match:
            trigger_pos   = kv_match.start()
            after_trigger = med_block[kv_match.end():]
            kv_lines = []
            for l in after_trigger.split('\n'):
                ls = l.strip()
                if not ls:
                    if kv_lines:
                        break
                    continue
                if FOOTNOTE_RE.match(ls) or re.match(r'^=== PAGE', ls):
                    break
                kv_lines.append(ls)
            meditation = med_block[:trigger_pos].strip()
            key_verse  = '\n'.join(kv_lines)
        else:
            meditation = med_block.strip()
            key_verse = ''

    # Parse header: last line(s) before 【經文】
    header_lines = [l.strip() for l in header.split('\n') if l.strip()]
    # Remove page number lines (single digits)
    header_lines = [l for l in header_lines if not re.match(r'^\d{1,2}$', l)]
    # Remove day-header lines
    header_lines = [l for l in header_lines if not re.match(r'^星期[日一二三四五六]', l)]
    # Remove transition lines ("回應...")
    header_lines = [l for l in header_lines if not re.match(r'^回應', l)]
    if not header_lines:
        return None

    # Last 1-2 lines form the reading title
    # Pattern: "以賽亞書 11:1-10 帶來公義與和平的統治者"
    # or split across lines
    reading_title_line = ' '.join(header_lines[-2:]) if len(header_lines) >= 2 else header_lines[-1]
    # Extract book, passage, title
    m = re.match(r'^(.+?)\s+(\d+[\d:,\-–\.\sa-z]*(?:節)?)\s+(.+)$', reading_title_line)
    if m:
        book    = m.group(1).strip()
        passage = m.group(2).strip()
        title   = m.group(3).strip()
    else:
        # Try simpler: first token = book, rest = passage (no separate title)
        parts = reading_title_line.split(None, 1)
        book    = parts[0] if parts else reading_title_line
        passage = parts[1] if len(parts) > 1 else ''
        title   = ''

    return {
        'book':       book,
        'passage':    passage,
        'title':      title,
        'text':       scripture.strip(),
        'meditation': meditation.strip(),
        'key_verse':  key_verse.strip(),
    }

def parse_pdf_text(raw_text, meta):
    """Parse full PDF text into structured week data."""
    # Remove form feeds, normalise page markers
    text = raw_text.replace('\f', '\n')
    # Remove tab navigation pages (booklet format has pages listing only day headers)
    text = remove_tab_pages(text)

    # ── Intro letter ────────────────────────────────────────────────────
    intro_letter = ''
    intro_m = re.search(r'各位讀者[：:].+', text, re.DOTALL)
    if intro_m:
        intro_start = intro_m.start()
        # Intro ends at theme essay (look for a line that is just a title + author)
        # Heuristic: intro ends when we see a blank-line + short title + blank-line + author name
        after_intro = text[intro_start:]
        # Find the essay section: typically "主題文標題\n龐君華\n..." or similar
        essay_m = re.search(
            r'\n([一-鿿：、！？，。…A-Za-z\s「」『』《》〈〉—\-–\(\)（）]+)\n'
            r'(龐君華|陳繼賢|林\S{1,2}|鄭\S{1,2}|黃\S{1,2}|李\S{1,2}|王\S{1,2}|方\S{1,2})\n',
            after_intro
        )
        if essay_m:
            intro_raw = after_intro[:essay_m.start()]
        else:
            intro_raw = after_intro[:3000]  # fallback: first 3000 chars
        # Clean up: remove page markers, donation info, etc.
        intro_raw = re.sub(r'=== PAGE \d+ ===', '', intro_raw)
        intro_raw = re.sub(r'\d+\n', '', intro_raw)  # page numbers
        # Remove donation block
        intro_raw = re.sub(r'戶名：.*?帳號：\S+', '', intro_raw, flags=re.DOTALL)
        intro_raw = re.sub(r'新的一年.*?帳號.*?\n', '', intro_raw, flags=re.DOTALL)
        intro_raw = re.sub(r'本事工.*?帳號.*?\n', '', intro_raw, flags=re.DOTALL)
        intro_raw = re.sub(r'敬請留意.*?\n', '', intro_raw)
        intro_raw = re.sub(r'請註明.*?\n', '', intro_raw)
        intro_letter = re.sub(r'\n{3,}', '\n\n', intro_raw).strip()

    # ── Theme essay ─────────────────────────────────────────────────────
    theme_essay_title = ''
    theme_essay = ''
    essay_m2 = re.search(
        r'\n([一-鿿：、！？，。…A-Za-z\s「」『』《》〈〉—\-–\(\)（）]{4,60})\n'
        r'(龐君華|陳繼賢|林\S{1,2}|鄭\S{1,2}|黃\S{1,2}|李\S{1,2}|王\S{1,2}|方\S{1,2})\n',
        text
    )
    if essay_m2:
        theme_essay_title = essay_m2.group(1).strip()
        essay_author = essay_m2.group(2)
        essay_start = essay_m2.end()
        # Essay ends at first day header or appendix
        day_m = re.search(r'\n星期[日一二三四五六][\s（\(]', text[essay_start:])
        app_m = re.search(r'\n附錄[一二三四五]', text[essay_start:])
        end_pos = min(
            day_m.start() if day_m else len(text),
            app_m.start() if app_m else len(text)
        )
        essay_raw = text[essay_start:essay_start + end_pos]
        # Remove RCL table section
        essay_raw = re.sub(r'附錄一[：:].*?(?=\n附錄[二三四五]|\n星期)', '', essay_raw, flags=re.DOTALL)
        essay_raw = re.sub(r'=== PAGE \d+ ===', '', essay_raw)
        essay_raw = re.sub(r'^\d{1,2}$', '', essay_raw, flags=re.MULTILINE)
        theme_essay = re.sub(r'\n{3,}', '\n\n', essay_raw).strip()

    # ── Daily readings ───────────────────────────────────────────────────
    days = []
    # Split text by day headers
    day_pattern = re.compile(
        r'(?m)^星期([日一二三四五六])[\s（\(]*(\d{1,2})[/／](\d{1,2})[^\n]*'
    )
    day_matches = list(day_pattern.finditer(text))

    for i, dm in enumerate(day_matches):
        dow  = DAY_ZH.get(dm.group(1), 0)
        month = int(dm.group(2))
        day_n = int(dm.group(3))
        day_label_raw = dm.group(0).strip()
        # Extract just the label: 主日（12/07）or 星期一（12/08）
        day_label = re.sub(r'\s+', '', day_label_raw)
        day_label = re.sub(r'[A-Za-z].*$', '', day_label).strip()  # remove English

        # Text for this day: from this match to next day match (or end)
        end = day_matches[i+1].start() if i+1 < len(day_matches) else len(text)
        day_text = text[dm.start():end]

        # Extract individual readings using backward-scan for boundaries
        readings    = []
        ec_positions = [m.start() for m in re.finditer(r'【經文】', day_text)]
        for j, ec_pos in enumerate(ec_positions):
            header = _get_header_lines(day_text, ec_pos)
            if j + 1 < len(ec_positions):
                content_end = _get_header_start_pos(day_text, ec_positions[j + 1])
            else:
                content_end = len(day_text)
            content    = day_text[ec_pos:content_end]
            full_block = header + '\n' + content
            r = split_reading(full_block)
            if r:
                readings.append(r)

        if readings:
            days.append({
                'day_of_week': dow,
                'day_label':   day_label,
                'readings':    readings,
            })

    # ── Appendices ───────────────────────────────────────────────────────
    appendices = []
    # Find candle liturgy
    candle_m = re.search(r'附錄[二]?[：:]?.*?點燭儀式', text)
    if not candle_m:
        candle_m = re.search(r'點燭儀式', text)

    # Discussion appendix
    disc_m = re.search(r'附錄[三四五]?[：:]?.*?小組討論.*?\n([\s\S]+?)(?:=== PAGE|\Z)', text)
    if not disc_m:
        # Try: after last day section
        if day_matches:
            last_day_end = day_matches[-1].start()
            after_days = text[last_day_end + 500:]
            disc_m2 = re.search(r'(小組討論|討論問題|討論|反思)([\s\S]+)', after_days)
            if disc_m2:
                disc_body = disc_m2.group(0)
            else:
                disc_body = ''
        else:
            disc_body = ''
    else:
        disc_body = disc_m.group(1)

    if disc_body.strip():
        disc_body = re.sub(r'=== PAGE \d+ ===', '', disc_body)
        disc_body = re.sub(r'^\d{1,2}$', '', disc_body, flags=re.MULTILINE)
        disc_body = re.sub(r'\n{3,}', '\n\n', disc_body).strip()
        appendices.append({'title': '本週小組討論', 'body': disc_body})

    return {
        'intro_letter':       intro_letter,
        'theme_essay_title':  theme_essay_title,
        'theme_essay':        theme_essay,
        'appendices':         appendices,
        'days':               days,
    }

# ── Supabase upload ───────────────────────────────────────────────────────────
def sb_headers():
    return {
        'apikey': SB_KEY,
        'Authorization': f'Bearer {SB_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation',
    }

def week_exists(year, season, week_num):
    r = requests.get(
        f'{SB_URL}/rest/v1/pong_lectionary_weeks',
        params={'lectionary_year': f'eq.{year}', 'season': f'eq.{season}',
                'week_num': f'eq.{week_num}', 'select': 'id'},
        headers=sb_headers(), timeout=10
    )
    data = r.json()
    return data[0]['id'] if data else None

def upsert_week(meta, parsed):
    payload = {
        'lectionary_year':    meta['year'],
        'season':             meta['season'],
        'week_num':           meta['week_num'],
        'title':              meta['title'],
        'date_range':         meta['date_range'],
        'intro_letter':       parsed['intro_letter'],
        'theme_essay_title':  parsed['theme_essay_title'],
        'theme_essay':        parsed['theme_essay'],
        'appendices':         parsed['appendices'],
        'is_published':       True,
    }
    r = requests.post(
        f'{SB_URL}/rest/v1/pong_lectionary_weeks',
        json=payload,
        headers={**sb_headers(), 'Prefer': 'resolution=merge-duplicates,return=representation'},
        params={'on_conflict': 'lectionary_year,season,week_num'},
        timeout=15
    )
    if r.status_code not in (200, 201):
        raise Exception(f'upsert week failed: {r.status_code} {r.text[:300]}')
    return r.json()[0]['id']

def upsert_days(week_id, days):
    for d in days:
        payload = {
            'week_id':     week_id,
            'day_of_week': d['day_of_week'],
            'day_label':   d['day_label'],
            'readings':    d['readings'],
        }
        r = requests.post(
            f'{SB_URL}/rest/v1/pong_lectionary_days',
            json=payload,
            headers={**sb_headers(), 'Prefer': 'resolution=merge-duplicates,return=representation'},
            params={'on_conflict': 'week_id,day_of_week'},
            timeout=15
        )
        if r.status_code not in (200, 201):
            raise Exception(f'upsert day {d["day_of_week"]} failed: {r.status_code} {r.text[:200]}')

# ── Main loop ─────────────────────────────────────────────────────────────────
def process_week(meta):
    yr, season, wk = meta['year'], meta['season'], meta['week_num']
    label = f"{yr}年 {season} wk{wk} ({meta['title']})"
    print(f'\n▶ {label}')

    # Check if already seeded
    existing_id = week_exists(yr, season, wk)
    if existing_id:
        print(f'  ✓ 已存在 (id={existing_id})，跳過')
        return True

    # Derive filename: {Year}-{Season}-wk{NN}.pdf
    url = meta['url']
    fname = f"{yr}-{season.capitalize()}-wk{wk:02d}.pdf"
    pdf_path = PDF_DIR / fname

    # Download
    if not download_pdf(url, pdf_path):
        return False

    # Extract text
    print('  解析 PDF...')
    raw_text = pdf_to_text(pdf_path)

    # Save TXT for reference
    txt_path = PDF_DIR / fname.replace('.pdf', '-text.txt')
    txt_path.write_text(raw_text, encoding='utf-8')

    # Parse
    parsed = parse_pdf_text(raw_text, meta)
    day_count = len(parsed['days'])
    reading_counts = [len(d['readings']) for d in parsed['days']]
    print(f'  解析完成：{day_count} 天，讀經數 {reading_counts}')

    if day_count == 0:
        print('  ✗ 解析失敗：未找到任何日期，跳過')
        return False

    if DRY_RUN:
        print('  [dry-run] 不上傳')
        # Save JSON preview
        preview_path = PDF_DIR / fname.replace('.pdf', '-parsed.json')
        preview_path.write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'  已儲存預覽：{preview_path.name}')
        return True

    # Upload
    print('  上傳 Supabase...')
    week_id = upsert_week(meta, parsed)
    upsert_days(week_id, parsed['days'])
    print(f'  ✓ 上傳完成 (week_id={week_id}, {day_count} 天)')
    return True

def main():
    print(f'三讀三禱 Pipeline  dry_run={DRY_RUN}')
    print(f'Supabase: {SB_URL[:40]}...')
    print(f'共 {len(WEEKS)} 週待處理\n')

    ok = fail = skip = 0
    for meta in WEEKS:
        if FILTER_Y and meta['year'] != FILTER_Y:
            continue
        if FILTER_S and meta['season'] != FILTER_S:
            continue
        try:
            result = process_week(meta)
            if result:
                ok += 1
            else:
                fail += 1
        except Exception as e:
            print(f'  ✗ 錯誤：{e}')
            fail += 1
        time.sleep(0.5)  # be gentle to server

    print(f'\n完成：成功 {ok}，失敗 {fail}')

if __name__ == '__main__':
    main()
