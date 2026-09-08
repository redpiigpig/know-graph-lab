# -*- coding: utf-8 -*-
"""課程資料夾裡那些文件（課程大綱、指定閱讀、自訂讀本、十五週計畫）的 HTML 產出。

原本這些都寫成 .md。使用者要看的是排好的頁面，不是原始碼——Windows 檔總管與
Drive 都不會渲染 markdown，點開就是一堆 `##` 和 `**`。所以一律出 .html：
點兩下就用瀏覽器開，列印直接是 B5。

用法（給其他腳本呼叫）：

    from course_html import write_html
    write_html(path, title, md_text)        # path 用 .html 結尾

這裡只認 markdown 的一小塊子集——標題、粗體、清單、表格、引言、水平線、連結。
不裝 markdown 套件：要的就這幾種，`re` 夠用（YAGNI）。
"""
from __future__ import annotations

import html
import re
from pathlib import Path

CSS = """
:root { color-scheme: light; }
* { box-sizing: border-box; }
body {
  margin: 0; padding: 2.4rem 1.2rem 5rem;
  background: #f6f5f2; color: #1c1b19;
  font-family: "Noto Serif TC", "Source Han Serif TC", "MS Mincho", "細明體",
               PMingLiU, Georgia, "Times New Roman", serif;
  font-size: 17px; line-height: 1.9;
}
main { max-width: 46rem; margin: 0 auto; background: #fff;
       padding: 3rem 3.2rem 4rem; border: 1px solid #e3e0da;
       box-shadow: 0 1px 3px rgba(0,0,0,.05); }
h1 { font-size: 1.72rem; line-height: 1.45; margin: 0 0 1.6rem;
     padding-bottom: .7rem; border-bottom: 2px solid #2f2c27; }
h2 { font-size: 1.24rem; margin: 2.4rem 0 .9rem;
     padding-left: .6rem; border-left: 4px solid #8a7f6d; }
h3 { font-size: 1.06rem; margin: 1.8rem 0 .7rem; color: #443f37; }
p { margin: 0 0 1.05rem; }
ul, ol { margin: 0 0 1.05rem; padding-left: 1.6rem; }
li { margin-bottom: .4rem; }
blockquote { margin: 0 0 1.2rem; padding: .7rem 1.1rem;
             background: #f3f1ec; border-left: 3px solid #b9b1a1; color: #4a453c; }
hr { border: 0; border-top: 1px solid #ddd8ce; margin: 2.2rem 0; }
a { color: #2f5d8a; }
code { font-family: Consolas, "Courier New", monospace; font-size: .92em;
       background: #f0eee9; padding: .1em .35em; border-radius: 3px; }
table { border-collapse: collapse; width: 100%; margin: 0 0 1.4rem; font-size: .94em; }
th, td { border: 1px solid #d8d3c8; padding: .48rem .7rem; text-align: left;
         vertical-align: top; }
th { background: #efece5; font-weight: 600; }
tbody tr:nth-child(even) { background: #faf9f6; }
.meta { color: #6b6459; font-size: .92em; }
@media print {
  @page { size: 182mm 257mm; margin: 16mm 15mm; }   /* JIS B5 */
  body { background: #fff; padding: 0; font-size: 11pt; line-height: 1.8; }
  main { max-width: none; border: 0; box-shadow: none; padding: 0; }
  h2 { page-break-after: avoid; }
  tr, li, blockquote { page-break-inside: avoid; }
}
"""

_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_BOLD = re.compile(r"\*\*(.+?)\*\*")
_CODE = re.compile(r"`([^`]+)`")
_BARE = re.compile(r"(?<![\"'=>])(https?://[^\s<）】」]+)")


def _inline(text: str) -> str:
    out = html.escape(text)
    out = _CODE.sub(r"<code>\1</code>", out)
    out = _BOLD.sub(r"<strong>\1</strong>", out)
    out = _LINK.sub(r'<a href="\2">\1</a>', out)
    out = _BARE.sub(r'<a href="\1">\1</a>', out)
    return out


def _table(rows: list[str]) -> str:
    """markdown 表格。第二列是對齊列，丟掉。"""
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
    body = [c for c in cells[1:] if not all(set(x) <= set("-: ") for x in c)]
    out = ["<table><thead><tr>"]
    out += [f"<th>{_inline(c)}</th>" for c in cells[0]]
    out.append("</tr></thead><tbody>")
    for row in body:
        out.append("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in row) + "</tr>")
    out.append("</tbody></table>")
    return "".join(out)


def md_to_html(md: str) -> str:
    lines = md.splitlines()
    out: list[str] = []
    i = 0
    list_tag: str | None = None

    def close_list() -> None:
        nonlocal list_tag
        if list_tag:
            out.append(f"</{list_tag}>")
            list_tag = None

    while i < len(lines):
        ln = lines[i]
        stripped = ln.strip()

        if not stripped:
            close_list()
            i += 1
            continue

        if stripped.startswith("|") and i + 1 < len(lines) and lines[i + 1].strip().startswith("|"):
            close_list()
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i])
                i += 1
            out.append(_table(block))
            continue

        if re.fullmatch(r"-{3,}|\*{3,}|_{3,}", stripped):
            close_list()
            out.append("<hr>")
            i += 1
            continue

        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            close_list()
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{_inline(m.group(2))}</h{lvl}>")
            i += 1
            continue

        if stripped.startswith(">"):
            close_list()
            quote = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip().lstrip("> ").rstrip())
                i += 1
            out.append("<blockquote>" + "<br>".join(_inline(q) for q in quote) + "</blockquote>")
            continue

        m = re.match(r"^[-*]\s+(.*)$", stripped)
        if m:
            if list_tag != "ul":
                close_list()
                out.append("<ul>")
                list_tag = "ul"
            out.append(f"<li>{_inline(m.group(1))}</li>")
            i += 1
            continue

        m = re.match(r"^\d+[.、]\s*(.*)$", stripped)
        if m:
            if list_tag != "ol":
                close_list()
                out.append("<ol>")
                list_tag = "ol"
            out.append(f"<li>{_inline(m.group(1))}</li>")
            i += 1
            continue

        # 縮排的續行（清單的第二層說明）併進前一個 li
        if ln.startswith(("  ", "\t")) and list_tag:
            out.append(f"<li class=meta>{_inline(stripped.lstrip('- '))}</li>")
            i += 1
            continue

        close_list()
        out.append(f"<p>{_inline(stripped)}</p>")
        i += 1

    close_list()
    return "\n".join(out)


def render(title: str, md: str) -> str:
    return (
        "<!doctype html>\n"
        '<html lang="zh-Hant"><head><meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{html.escape(title)}</title>\n"
        f"<style>{CSS}</style></head>\n"
        f"<body><main>\n{md_to_html(md)}\n</main></body></html>\n"
    )


def write_html(path: str | Path, title: str, md: str) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(render(title, md), encoding="utf-8")
    return p


def html_to_md(raw: str) -> str:
    """反向：把本模組出的 HTML 拆回近似 markdown，給下游解析用。

    讀本產生器要從這些檔案取出正文與出處欄位。與其在下游寫一套 HTML 解析，
    不如在這裡還原成它本來就認得的 markdown 形狀。
    """
    body = raw.split("<main>", 1)[-1].split("</main>", 1)[0]
    body = re.sub(r"<h1>(.*?)</h1>", r"\n# \1\n", body, flags=re.S)
    body = re.sub(r"<h2>(.*?)</h2>", r"\n## \1\n", body, flags=re.S)
    body = re.sub(r"<h3>(.*?)</h3>", r"\n### \1\n", body, flags=re.S)
    body = re.sub(r"<strong>(.*?)</strong>", r"**\1**", body, flags=re.S)
    body = re.sub(r"<li[^>]*>(.*?)</li>", r"\n- \1", body, flags=re.S)
    body = re.sub(r"<blockquote>(.*?)</blockquote>", r"\n> \1\n", body, flags=re.S)
    body = body.replace("<br>", "\n")
    body = re.sub(r"</?(p|ul|ol|hr|table|thead|tbody|tr|th|td|div)[^>]*>", "\n", body)
    body = re.sub(r"<a [^>]*>(.*?)</a>", r"\1", body, flags=re.S)
    body = re.sub(r"<[^>]+>", "", body)
    body = html.unescape(body)
    return re.sub(r"\n{3,}", "\n\n", body).strip()
