"""aquinas_build 純函式測試（零 network/DB）— quaestio 切段與四段標記。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import aquinas_build as ab  # noqa: E402

# 仿中華道明會譯本一節：opener → 質疑編號 → 反之…卻說 → 正解我解答如下 → 釋疑編號。
ARTICLE = """有關第一節，我們討論如下:
質疑似乎並不需要另一種學問。因為:
1 .理性已足夠。是以不需要。
2. 此外，哲學已涵蓋一切。所以多餘。
反之
《弟茂德後書》第三章16節卻說: 聖經有益於教導。
正解我解答如下:為了得救，需要天主啟示的學問。
這是第一個理由。
釋疑
1 雖然理性有限，但啟示可補足。
2. 不同原理產生不同學問。"""


def test_chinese_to_int_basic():
    assert ab.chinese_to_int("四十三") == 43
    assert ab.chinese_to_int("十") == 10
    assert ab.chinese_to_int("一一四") == 114
    assert ab.chinese_to_int("九十九") == 99


def test_split_articles_by_opener():
    full = "前付垃圾" + ARTICLE + "\n有關第二節，我們討論如下:\n質疑X。反之Y。正解我解答如下:Z。"
    arts = ab.split_articles(full)
    assert len(arts) == 2
    assert arts[0]["sec"] == 1 and arts[1]["sec"] == 2


def test_mark_zones_four_roles():
    rows = ab.mark_zones(ARTICLE.split("如下:", 1)[1])
    labels = [lab for lab, _ in rows]
    assert labels.count("異議") == 2      # 兩條難題各一段
    assert "反之" in labels
    assert "正解" in labels
    assert labels.count("答覆") == 2      # 兩條釋疑各一段


def test_mark_zones_objection_numbered_split():
    rows = ab.mark_zones(ARTICLE.split("如下:", 1)[1])
    objs = [p for lab, p in rows if lab == "異議"]
    assert objs[0].startswith("1.") and objs[1].startswith("2.")


def test_mark_zones_non_standard_returns_plain():
    # 無「正解我解答如下」→ 回傳無標段落，維持可讀
    rows = ab.mark_zones("這是一段沒有經院結構的說明文字。")
    assert all(lab is None for lab, _ in rows)


def test_clean_ocr_light_drops_pagenum_lines():
    out = ab.clean_ocr_light("正文一\n- 307 -\n正文二\n42")
    assert "307" not in out and "42" not in out
    assert "正文一" in out and "正文二" in out
