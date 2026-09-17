# -*- coding: utf-8 -*-
"""全集 20 卷是不是都轉錄完了？完了回 0、還有沒轉的回 1。

夜班 bat 拿這個離開碼決定要不要把排程關掉。抽成一支小腳本，是因為原本那行
內嵌的 `python -c "...regex..."` 在 cmd 裡被引號與百分號咬到，等於永遠判不出來。
"""
from __future__ import annotations

import os
import sys

import requests
from dotenv import load_dotenv
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
load_dotenv(REPO / ".env")
URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}


def main() -> int:
    ids = [f"d0000001-0000-4000-8000-{v:012d}" for v in range(1, 21)]
    try:
        r = requests.get(f"{URL}/rest/v1/ebooks?select=id,chunk_count"
                         f"&id=in.({','.join(ids)})&limit=100", headers=H, timeout=30)
        rows = r.json()
    except Exception:
        return 1                      # 查不到就當「還沒完」，不要誤關排程
    if not isinstance(rows, list) or len(rows) < 20:
        return 1
    return 0 if all((x.get("chunk_count") or 0) > 0 for x in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
