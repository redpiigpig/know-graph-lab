from __future__ import annotations

import html
import re
import subprocess
from pathlib import Path

import fitz
import mammoth


ROOT = Path(r"C:\Users\user\Desktop\know-graph-lab")
DOCX = ROOT / "output" / "documents" / "張辰瑋_博士論文研究計畫_第二版草案.docx"
QA = ROOT / "output" / "qa" / "doctoral_v2_fallback"
HTML = QA / "proposal.html"
PDF = QA / "張辰瑋_博士論文研究計畫_第二版草案_檢查版.pdf"
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")


CSS = r"""
@page { size: Letter; margin: 1in; }
* { box-sizing: border-box; }
body { font-family: Calibri, "Microsoft JhengHei", sans-serif; color: #222; font-size: 11pt; line-height: 1.55; }
p { margin: 0 0 8pt; text-align: justify; }
h1 { color: #2E74B5; font-size: 16pt; margin: 18pt 0 10pt; break-after: avoid; }
h2 { color: #2E74B5; font-size: 13pt; margin: 12pt 0 6pt; break-after: avoid; }
h3 { color: #1F4D78; font-size: 12pt; margin: 8pt 0 4pt; break-after: avoid; }
ul, ol { margin: 4pt 0 8pt 0.38in; padding: 0; }
li { margin-bottom: 5pt; }
table { width: 100%; border-collapse: collapse; table-layout: fixed; margin: 7pt 0 12pt; font-size: 8.5pt; }
th, td { border: 0.5pt solid #B8C2CC; padding: 4pt 6pt; vertical-align: top; overflow-wrap: anywhere; }
tr:first-child td { background: #DCE6F1; font-weight: 700; text-align: center; }
tr:nth-child(odd) td { background: #F4F6F9; }
tr { break-inside: avoid; }
.cover { height: 8.4in; page-break-after: always; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.cover .school { color: #1F4D78; font-size: 13pt; margin-bottom: 0.7in; }
.cover .title { color: #1F4D78; font-size: 24pt; font-weight: 700; margin-bottom: 8pt; }
.cover .subtitle { color: #2E74B5; font-size: 16pt; font-weight: 700; margin-bottom: 12pt; }
.cover .figures { color: #1F4D78; font-size: 11.5pt; margin-bottom: 18pt; }
.cover .eng { color: #777; font-size: 10.5pt; font-style: italic; margin-bottom: 5pt; }
.cover .status { color: #777; margin-top: 12pt; }
.toc { page-break-after: always; }
.toc p { margin-left: 0.25in; margin-bottom: 7pt; }
.main-h1 { page-break-before: always; }
.main-h1.first-main { page-break-before: always; }
.bibliography p { margin-left: 0.28in; text-indent: -0.28in; font-size: 10pt; line-height: 1.25; margin-bottom: 4pt; }
"""


def build_cover() -> str:
    return """
<section class="cover">
  <div class="school">玄奘大學宗教與文化學系博士班</div>
  <div class="title">入世轉向的兩條譜系</div>
  <div class="subtitle">台灣人間佛教與以長老教會為核心之本土神學的歷史比較及神學比較</div>
  <div class="figures">以太虛、印順、傳道、昭慧與黃彰輝、宋泉盛、王憲治、黃伯和為核心</div>
  <div class="eng">Two Genealogies of This-Worldly Engagement</div>
  <div class="eng">A Historical and Theological Comparison of Humanistic Buddhism and Presbyterian-Centered Taiwanese Contextual Theology</div>
  <p><strong>博士論文研究計畫（第二版草案）</strong></p>
  <p>研究生：張辰瑋</p>
  <p>日期：2026 年 7 月 24 日</p>
  <p class="status">狀態：未發表草案，供指導與修訂使用</p>
</section>
"""


def clean_converted_body(body: str) -> str:
    school = re.escape("玄奘大學宗教與文化學系博士班")
    start = re.search(rf"<p>{school}</p>", body)
    abstract = body.find("<h1>摘要</h1>")
    if start and abstract > start.start():
        body = body[: start.start()] + body[abstract:]
    body = body.replace("<h1>目錄</h1>", '<section class="toc"><h1>目錄</h1>', 1)
    marker = "<h1>摘要</h1>"
    body = body.replace(marker, "</section>" + marker, 1)
    for title in (
        "一、研究背景、動機與問題意識",
        "二、研究回顧",
        "三、研究對象、範圍與分期",
        "四、研究方法與材料",
        "五、主要史料與分析程序",
        "六、預期研究成果與貢獻",
        "七、論文章節大綱",
        "八、研究進度規劃",
        "九、核心參考文獻",
    ):
        body = body.replace(f"<h1>{html.escape(title)}</h1>", f'<h1 class="main-h1">{html.escape(title)}</h1>')
    return body


def main() -> None:
    QA.mkdir(parents=True, exist_ok=True)
    with DOCX.open("rb") as f:
        result = mammoth.convert_to_html(f)
    body = clean_converted_body(result.value)
    page = f"<!doctype html><html lang='zh-Hant'><head><meta charset='utf-8'><style>{CSS}</style></head><body>{build_cover()}{body}</body></html>"
    HTML.write_text(page, encoding="utf-8")
    args = [
        str(CHROME),
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={PDF}",
        HTML.as_uri(),
    ]
    subprocess.run(args, check=True, capture_output=True, text=True, timeout=120)
    pdf = fitz.open(PDF)
    for i, page_obj in enumerate(pdf):
        pix = page_obj.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
        pix.save(QA / f"page-{i + 1:02d}.png")
    print(f"PDF={PDF}")
    print(f"PAGES={len(pdf)}")
    print(f"WARNINGS={len(result.messages)}")
    for message in result.messages[:10]:
        print(message)


if __name__ == "__main__":
    main()
