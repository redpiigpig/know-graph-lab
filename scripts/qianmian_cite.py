# -*- coding: utf-8 -*-
"""把書摘那一欄粗略的出處字串，補成頁下註用的正式書目。

書摘的出處長這樣：「游斌，希伯來聖經的文本、歷史與思想世界，頁25」
DB 的 books 表有出版地／出版者／年，補上去才是完整的註：
    游斌，《希伯來聖經的文本、歷史與思想世界》（北京：宗教文化出版社，2007年），頁25。

查不到書目的就只加書名號，不硬掰出版資訊。
"""
import json
import re
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "output" / "qianmian" / "books.json"


def _norm(s):
    return re.sub(r"[\s、。．.，,：:；;（）()《》〈〉「」『』\-─—_]", "", (s or "")).lower()


def load_books():
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    env = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.startswith("#"):
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip().strip('"')
    key = env.get("SUPABASE_SERVICE_KEY") or env["SUPABASE_SERVICE_ROLE_KEY"]
    r = requests.get(f"{env['SUPABASE_URL']}/rest/v1/books",
                     params={"select": "title,author,translator,publish_place,publisher,publish_year",
                             "limit": "3000"},
                     headers={"apikey": key, "Authorization": f"Bearer {key}"}, timeout=60)
    r.raise_for_status()
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(r.json(), ensure_ascii=False, indent=1), encoding="utf-8")
    return r.json()


class Citer:
    def __init__(self):
        self.by_title = {}
        for b in load_books():
            self.by_title.setdefault(_norm(b["title"]), b)
        self.misses = set()

    def format(self, raw):
        """出處字串 → 頁下註全文。"""
        raw = (raw or "").strip().rstrip("。")
        if not raw:
            return ""
        if raw.startswith("http"):
            return raw

        # 拆出頁碼
        page = ""
        m = re.search(r"[，,]?\s*(頁\s*[\d\-–~－至,，、\s]+)$", raw)
        if m:
            page = re.sub(r"\s+", "", m.group(1))
            raw = raw[: m.start()].rstrip("，, ")

        # 第一個逗號前當作者，其後當書名（書摘一律這樣寫）
        author, _, title = raw.partition("，")
        if not title:
            author, _, title = raw.partition(",")
        if not title:                       # 沒有作者，整串就是出處
            return raw + ("，" + page if page else "") + "。"

        title = title.strip().strip("《》〈〉")
        book = self.by_title.get(_norm(title))
        if book:
            bits = []
            if book.get("translator"):
                bits.append(f"{book['translator']}譯")
            imprint = ""
            if book.get("publisher"):
                place = book.get("publish_place") or ""
                year = f"{book['publish_year']}年" if book.get("publish_year") else ""
                imprint = "（" + "：".join(x for x in (place, book["publisher"]) if x) + \
                          ("，" + year if year else "") + "）"
            head = f"{author.strip()}，《{title}》"
            if bits:
                head += "，" + "，".join(bits)
            out = head + imprint
        else:
            self.misses.add(f"{author.strip()}，{title}")
            out = f"{author.strip()}，《{title}》"
        return out + ("，" + page if page else "") + "。"
