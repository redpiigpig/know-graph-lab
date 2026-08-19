# -*- coding: utf-8 -*-
"""Update interview page citations inside the existing first-edition DOCX footnotes.

This is a minimal OOXML edit: it changes only footnote text whose old A5 page
range is known, leaving the body, styles, pagination, and other footnotes intact.
"""
from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parent.parent
DOCX = ROOT / "public/content/works/mahaprajapati-revolution-book.docx"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"

# Old first-edition A5 citations -> current continuous three-volume pagination.
REPLACEMENTS = [
    ("頁152–165，引文見頁153", "頁385–402，引文見頁386"),
    ("頁152–165", "頁385–402"),
    ("頁114–130，引文見頁117", "頁336–357，引文見頁340"),
    ("頁72–83", "頁281–296"),
    ("頁33–43，引文見頁34", "頁40–53，引文見頁42"),
    ("頁104–110，引文見頁106", "頁132–140，引文見頁135"),
    ("頁86–97，引文見頁90", "頁521–535，引文見頁527"),
    ("頁16–23", "頁431–440"),
    ("頁24–34，引文見頁25", "頁441–454，引文見頁443"),
    ("頁98–108，引文見頁100", "頁536–549，引文見頁539"),
    ("頁44–59，引文見頁47", "頁54–75，引文見頁59"),
    ("頁33–43，引文見頁36", "頁40–53，引文見頁44"),
    ("頁56–65，引文見頁60", "頁482–494，引文見頁487"),
]


def update_footnotes(xml_bytes: bytes) -> tuple[bytes, int]:
    root = ET.fromstring(xml_bytes)
    changed = 0
    for footnote in root.findall(f"{W}footnote"):
        texts = footnote.findall(f".//{W}t")
        if not texts:
            continue
        old = "".join(t.text or "" for t in texts)
        new = old
        huang_meiyu_source = "黃美瑜、游雅婷居士口述訪談紀錄，張辰瑋訪問，2024年5月2日，佛教弘誓學院嵐園。"
        if huang_meiyu_source in new and "頁467–481" not in new:
            new = new.replace(
                huang_meiyu_source,
                huang_meiyu_source + "收入《人間佛教與印順學派訪談集》第三冊，頁467–481，引文見頁475。",
            )
        for source, target in REPLACEMENTS:
            new = new.replace(source, target)
        if new == old:
            continue
        texts[0].text = new
        texts[0].set(XML_SPACE, "preserve")
        for text in texts[1:]:
            text.text = ""
        changed += 1
    return ET.tostring(root, encoding="utf-8", xml_declaration=True), changed


def main() -> None:
    with zipfile.ZipFile(DOCX, "r") as source:
        updated, changed = update_footnotes(source.read("word/footnotes.xml"))
        if not changed:
            raise SystemExit("No matching footnote citations found")
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False, dir=DOCX.parent) as handle:
            temp_path = Path(handle.name)
        try:
            with zipfile.ZipFile(temp_path, "w") as target:
                for item in source.infolist():
                    data = updated if item.filename == "word/footnotes.xml" else source.read(item.filename)
                    target.writestr(item, data)
            shutil.move(str(temp_path), DOCX)
        finally:
            temp_path.unlink(missing_ok=True)
    print(f"Updated {changed} DOCX footnotes: {DOCX}")


if __name__ == "__main__":
    main()
