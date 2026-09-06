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
        """出處字串 → 頁下註全文。

        🚨 書摘的出處欄裡有換行（書名在儲存格裡折行）。不先攤平的話，註文會帶著
           換行寫進 markdown，把一條註裂成兩行——前半成了殘缺的註，後半變成孤兒行，
           在 Word 裡會被當成正文印在章末。踩過，見 qianmian_repair.py --stitch。
        """
        raw = re.sub(r"\s*\n\s*", "", raw or "")
        raw = re.sub(r"[ \t]+", " ", raw).strip().rstrip("。")
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

        title = title.strip()
        # 出處欄常常自己就帶了標點：〈篇名〉，《期刊》第N期 這種。再包一層 《》
        # 會生出「《…〉，《…》》」這種怪東西——ch09、ch14 全毀在這裡。
        # 已經有書名號／篇名號的就原樣用，不要再包。
        marked = any(c in title for c in "《》〈〉")
        title = title if marked else title.strip("《》〈〉")
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
            head = f"{author.strip()}，{title}" if marked else f"{author.strip()}，《{title}》"
            if bits:
                head += "，" + "，".join(bits)
            out = head + imprint
        else:
            self.misses.add(f"{author.strip()}，{title}")
            out = f"{author.strip()}，{title}" if marked else f"{author.strip()}，《{title}》"
        return out + ("，" + page if page else "") + "。"
