# -*- coding: utf-8 -*-
"""OpenCC 把「咸」無條件轉成「鹹」——專名要還原，真的鹹味不可回轉。

2026-09-11。韓國無教會領袖**咸錫憲**（함석헌）在無教會書目裡 19 處全被寫成
「鹹錫憲」，等於把一個真人的名字寫錯。實測 s2tw／s2twp／s2t 三種配置行為一致，
連「咸豐」「咸興」都會中，沒有哪個配置能避開。

反向同樣要顧：全集語料裡 31 處「鹹」**全部是對的**（鹹水、鹹味、鹹魚、
鹹海＝Aral Sea）。一律回轉會把它們全毀掉，所以還原表只收專名。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from translate_ebook_to_zh import _to_traditional  # noqa: E402


# ── 專名要還原 ────────────────────────────────────────────────────────────────
def test_ham_sokhon():
    assert _to_traditional("咸錫憲的種子思想") == "咸錫憲的種子思想"
    assert _to_traditional("鹹錫憲的種子思想") == "咸錫憲的種子思想"


def test_place_and_era_names():
    assert "咸興" in _to_traditional("咸興出身")
    assert "咸鏡" in _to_traditional("咸鏡道")
    assert "咸豐" in _to_traditional("咸豐十年")
    assert "咸陽" in _to_traditional("秦都咸陽")


def test_classical_idiom():
    assert _to_traditional("群賢畢至，少長咸集") == "群賢畢至，少長咸集"


# ── 真的「鹹」不可回轉 ────────────────────────────────────────────────────────
def test_genuine_salty_is_untouched():
    """🚨 全集語料裡 31 處「鹹」全部是這一類，一律回轉會把它們全毀掉。"""
    for s in ("海水是鹹的", "鹹味", "鹹魚", "鹹水湖", "鹹海延伸至興都庫什",
              "鹽若失了鹹味，還能叫它再鹹呢"):
        assert _to_traditional(s) == s


def test_divine_second_person_pronoun():
    """🚨 同一個病的第二例：OpenCC 把對神的敬稱「祢」轉成「禰」（另一個字）。

    全集語料實測 祢 247／禰 224，同一本書兩種寫法混用——差別只在那一段
    走的是 Gemini（原樣）還是 NVIDIA（過 _to_traditional）。
    """
    assert _to_traditional("求祢賜予") == "求祢賜予"
    assert _to_traditional("求禰賜予") == "求祢賜予"
    assert _to_traditional("願祢的旨意成就") == "願祢的旨意成就"


def test_negi_is_not_the_pronoun():
    """禰宜是神道的祭司，不可回轉——日文題材遲早會用到。"""
    assert "禰宜" in _to_traditional("神社的禰宜")


def test_still_converts_simplified():
    """還原表不能把正常的簡轉繁弄壞。"""
    assert _to_traditional("无教会主义") == "無教會主義"
