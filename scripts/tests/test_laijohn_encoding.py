# -*- coding: utf-8 -*-
"""laijohn 抓取的編碼嗅探。

這一項屬於「看起來像成功的失敗」：`errors="replace"` 讓解錯碼也不會拋例外，
抓取、寫檔、產索引全都回報成功，只有內容是亂碼。實際代價是已收的 4,221 篇
裡有 1,930 篇題名壞掉，而且過了好幾個月才被發現。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import laijohn_biographies as lj  # noqa: E402

ZH = "洪瑞鋒函述洪茂德的裔"


def test_decodes_big5_pages():
    assert lj.decode(ZH.encode("big5")) == ZH


def test_decodes_utf8_pages():
    assert lj.decode(ZH.encode("utf-8")) == ZH


def test_decodes_utf8_with_bom():
    # /archives/pj/pj-contents.htm 就是這一種：沒有 meta charset、但帶 BOM
    assert lj.decode(b"\xef\xbb\xbf" + ZH.encode("utf-8")) == ZH


def test_never_returns_replacement_chars_for_valid_input():
    for enc in ("big5", "utf-8"):
        assert "\ufffd" not in lj.decode(ZH.encode(enc))


def test_utf8_is_not_mistaken_for_big5_on_long_text():
    """🚨 這是第一版漏掉的那 246 篇。

    Big5 幾乎接受任何位元組對，所以 UTF-8 內容用 Big5 解**不會**產生替換字元；
    拿替換字元數比大小就會一路倒向 Big5。文字越長越容易中，所以用長字串測。
    """
    long_zh = ("台灣基督長老教會的宣教與本土神學實況化運動，"
               "自黃彰輝以降歷經宋泉盛、王憲治、黃伯和諸位的開展。") * 20
    assert lj.decode(long_zh.encode("utf-8")) == long_zh
    assert lj.decode(long_zh.encode("big5")) == long_zh


def test_repair_mode_must_not_shrink_the_ledger(tmp_path, monkeypatch):
    """🚨 補抓模式不可以把帳本寫小。

    第一版把 `rows` 換成過濾後的子集，跑完結尾又整本寫回，
    帳本就從 4,234 筆變成 146 筆——其餘 4,088 筆的題名與字數全沒了，
    而且過程一句錯誤訊息都沒有。
    """
    import json

    ledger = tmp_path / "ledger.json"
    rows = [{"url": f"http://x/{i}.htm", "person": "P", "label": f"L{i}",
             "title": "壞掉的嚗題名" if i < 3 else f"正常題名{i}", "chars": 500}
            for i in range(10)]
    ledger.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(lj, "HARVEST", ledger)
    monkeypatch.setattr(lj, "get", lambda url: None)          # 不連網
    monkeypatch.setattr(lj.df, "r2_existing_keys", lambda p: set())
    monkeypatch.setattr(lj.time, "sleep", lambda s: None)

    lj.process(repair=True)

    after = json.loads(ledger.read_text(encoding="utf-8"))
    assert len(after) == 10, f"帳本被寫小了：{len(after)} 筆"
