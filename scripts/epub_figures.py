#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 EPUB 的插圖放回電子圖書館的正文（2026-10-01 使用者：「圖說要不然把圖放進來，要不然刪掉」）。

解析入庫時圖都丟了、只剩圖說文字孤零零一段。這裡照原 EPUB 的閱讀順序找每張圖，
  - 有圖說（緊接在圖後的短段，或 class 像 tushuo／caption）→ 在正文裡找到那段圖說，換成「圖＋圖說」；
  - 沒圖說 → 插在它前一段正文之後（用前一段結尾的字當錨點）；
  - 都找不到位置就不放（不亂插）。
比對前兩邊都轉成簡體再去標點：EPUB 多半是簡體、入庫時轉成了繁體，繁轉簡是多對一，比簡轉繁穩。

正文裡寫成 `![圖說](/api/ebooks/{id}/image/{檔名})`，閱讀器畫成 <figure>；
圖檔縮到最寬 1200px 推 R2 `ebook-images/{id}/{檔名}`（server/api/ebooks/[id]/image/[name].get.ts 串流）。
"""
from __future__ import annotations

import io
import posixpath
import re
import zipfile
from dataclasses import dataclass

MIN_BYTES = 8_000                  # 小於這個多半是裝飾線、項目符號
CAPTION_CLASS = re.compile(r"tushuo|caption|figcap|pic|tuzhu|imgnote|ts", re.I)
BLOCKS = ("p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li", "blockquote", "figcaption", "td")

_t2s = None


def to_simp(s: str) -> str:
    global _t2s
    if _t2s is None:
        import opencc
        _t2s = opencc.OpenCC("t2s")
    return _t2s.convert(s)


def norm(s: str) -> str:
    s = re.sub(r"\{\{[ps]:[^}]*\}\}|\[\^\d+\]|!\[[^\]]*\]\([^)]*\)", "", s or "")
    return re.sub(r"[\W_]+", "", to_simp(s))


@dataclass
class Figure:
    name: str          # 在 R2 上的檔名（去掉資料夾）
    member: str        # EPUB 內的路徑
    caption: str       # 原文（可能是簡體）
    before: str        # 前一段正文的正規化結尾（錨點）


def spine_docs(z: zipfile.ZipFile) -> list[str]:
    """照 OPF spine 的閱讀順序列出 xhtml；讀不到 OPF 就照檔名排序。"""
    try:
        container = z.read("META-INF/container.xml").decode("utf-8", "ignore")
        opf = re.search(r'full-path="([^"]+)"', container).group(1)
        text = z.read(opf).decode("utf-8", "ignore")
        base = posixpath.dirname(opf)
        items = dict(re.findall(r'<item\b[^>]*\bid="([^"]+)"[^>]*\bhref="([^"]+)"', text))
        items.update({i: h for h, i in re.findall(r'<item\b[^>]*\bhref="([^"]+)"[^>]*\bid="([^"]+)"', text)})
        order = re.findall(r'<itemref\b[^>]*\bidref="([^"]+)"', text)
        docs = [posixpath.normpath(posixpath.join(base, items[i])) for i in order if i in items]
        if docs:
            return docs
    except Exception:  # noqa: BLE001
        pass
    return sorted(n for n in z.namelist() if n.lower().endswith((".xhtml", ".html", ".htm")))


def find_figures(epub_path: str) -> list[Figure]:
    from bs4 import BeautifulSoup
    z = zipfile.ZipFile(epub_path)
    names = set(z.namelist())
    figs: list[Figure] = []
    seen: set[str] = set()
    for doc in spine_docs(z):
        if doc not in names:
            continue
        soup = BeautifulSoup(z.read(doc), "html.parser")
        last_text = ""
        for el in soup.find_all(list(BLOCKS) + ["img", "image"]):
            if el.name in ("img", "image"):
                src = el.get("src") or el.get("xlink:href") or el.get("href") or ""
                member = posixpath.normpath(posixpath.join(posixpath.dirname(doc), src))
                if member not in names or member in seen or "cover" in member.lower():
                    continue
                if z.getinfo(member).file_size < MIN_BYTES:
                    continue
                seen.add(member)
                block = el.find_parent(BLOCKS)
                cap = ""
                nxt = block.find_next_sibling() if block else None
                if nxt is not None:
                    t = nxt.get_text(" ", strip=True)
                    cls = " ".join(nxt.get("class") or [])
                    if t and (CAPTION_CLASS.search(cls) or (len(t) <= 100 and not (block.get_text(strip=True)))):
                        cap = t
                alt = (el.get("alt") or "").strip()
                if not cap and alt and not re.search(r"\.(jpe?g|png|gif)$|^image\d*$", alt, re.I):
                    cap = alt
                figs.append(Figure(posixpath.basename(member), member, cap, norm(last_text)[-20:]))
            elif el.find(BLOCKS) is None:
                t = el.get_text(" ", strip=True)
                if len(t) >= 20:
                    last_text = t
    return figs


def place_figures(chunks: list[dict], figs: list[Figure], book_id: str) -> tuple[list[dict], list[Figure], int]:
    """回傳 (改過的 chunks, 實際放進去的圖, 找不到位置的張數)。圖說段換成圖；沒圖說的插在錨點段之後。"""
    paras = [re.split(r"\n{2,}", c.get("content") or "") for c in chunks]
    keys = [[norm(p) for p in ps] for ps in paras]
    used: list[Figure] = []
    miss = 0
    for f in figs:
        url = f"/api/ebooks/{book_id}/image/{f.name}"
        cap_n = norm(f.caption)
        done = False
        if cap_n:
            for ci, ks in enumerate(keys):
                for pi, k in enumerate(ks):
                    if k and (k == cap_n or (len(cap_n) >= 8 and k.startswith(cap_n) and len(k) - len(cap_n) <= 4)):
                        lead = "".join(re.findall(r"\{\{p:[^}]*\}\}", paras[ci][pi]))
                        cap = re.sub(r"\{\{p:[^}]*\}\}", "", paras[ci][pi]).strip()
                        cap = re.sub(r"^#+\s*", "", cap)          # 圖說曾被誤判成小標
                        paras[ci][pi] = f"{lead}![{cap}]({url})"
                        keys[ci][pi] = ""
                        done = True
                        break
                if done:
                    break
        if not done and f.before and len(f.before) >= 10:
            for ci, ks in enumerate(keys):
                for pi, k in enumerate(ks):
                    if k.endswith(f.before):
                        while pi + 1 < len(paras[ci]) and paras[ci][pi + 1].lstrip().startswith("!["):
                            pi += 1                         # 同一錨點後已放過圖：接在後面，保持原書順序
                        paras[ci].insert(pi + 1, f"![]({url})" if not f.caption else f"![{f.caption}]({url})")
                        keys[ci].insert(pi + 1, "")
                        done = True
                        break
                if done:
                    break
        if done:
            used.append(f)
        else:
            miss += 1
    out = [dict(c, content="\n\n".join(ps)) for c, ps in zip(chunks, paras)]
    return out, used, miss


def image_bytes(epub_path: str, member: str) -> tuple[bytes, str]:
    """縮到最寬 1200px；有透明就留 PNG，其餘 JPEG q82。回傳 (bytes, content-type)。"""
    from PIL import Image
    raw = zipfile.ZipFile(epub_path).read(member)
    im = Image.open(io.BytesIO(raw))
    if im.width > 1200:
        im = im.resize((1200, round(im.height * 1200 / im.width)))
    buf = io.BytesIO()
    if im.mode in ("RGBA", "LA", "P") and member.lower().endswith(".png"):
        im.save(buf, "PNG", optimize=True)
        return buf.getvalue(), "image/png"
    im.convert("RGB").save(buf, "JPEG", quality=82, optimize=True)
    return buf.getvalue(), "image/jpeg"
