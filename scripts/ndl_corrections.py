# -*- coding: utf-8 -*-
"""逐字精修的人工更正 —— 存成資料，重生 OCR 後自動重套。

🚨 **這支存在的理由**：`ocr-ndl/*.txt` 是 `ndl_official_text.py` 的**產出**，
不是原始資料。直接在上面手改，下一次重生就整批消失，而且**重生完一切看起來正常**
——章數對、字數對、canary 過，只是你對照原圖逐字改過的地方默默變回亂碼。
2026-09-08 真的踩到：三行 ruby 亂碼改好後，為了補 `_titles.json` 重生一次，
兩行修正就沒了。

所以人工更正一律寫在這裡，由 `apply()` 在重生後重套一次。

    python scripts/ndl_corrections.py            # 對所有有更正的書重套
    python scripts/ndl_corrections.py 1033439    # 只套一本

每一條的格式：(pid, 影像號, 錯的字串, 對的字串, 依據)
**依據欄不可省**：日後有人問「你憑什麼改」，答案要在檔案裡。
"""
from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import ndl_build as nb  # noqa: E402

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# (pid, img, 錯, 對, 依據)
CORRECTIONS = [
    # ── 畔上賢造《初代の人々》1931 ────────────────────────────────
    # 三行都是被振り仮名（ruby）打散的：小字注音混進正文字序。
    # NDL 沒有把 ruby 另外標 TYPE，擋不掉，只能事後對照原圖改。
    ("1033439", 9,
     "男子的にそれれ敎言はしたる亦然あれ",
     "男子胎にやどれりと言ひし夜も亦然あれ",
     "對照 IIIF 原圖影像9（ruby「をのこ」在「男子」上）逐字讀出"),
    ("1033439", 9,
     "···何そ我は時より死に山何とて胎より",
     "……何とて我は胎より死にて出でざりしや、何とて胎より",
     "同上；約伯記三章的引文"),
    ("1033439", 10,
     "「ことかのとろよろのひとる如をそて項の上よ取數な子に授と小麥わが",
     "「こゝにかのセラピムのひとり鉗をもて壇の上より取りたる熱炭を手に携へて我にとび來り、わが",
     "對照原圖影像10（ruby「ひばし」在「鉗」上、「あかき」在「熱炭」上）；以賽亞書六章"),
    ("1033439", 55,
     "「創說の子」この人知知あらながれれを會も其金を持求も使徒たの",
     "「勸慰の子」、この人田畑ありけるが其れを賣りて其金を持ち來り使徒たちの足下に置けり。",
     "對照原圖影像55（ruby「なぐさめ」在「勸慰」上）；使徒行傳四章"),

    ("1033439", 5,
     "上賢著畔造",
     "",                       # 刪除型：整段拿掉
     "章首頁的作者署名『畔上賢造 著』被讀成亂序，在版面上自成一段。"
     "同頁的『ルカ傳五章一節-十一節』是該章的經文範圍副標，要保留"),

    # ── 畔上賢造《無教會主義》1934 ────────────────────────────────
    ("1099766", 14,
     "みなもとが〓くも",
     "みなもとが淸くも",
     "對照原圖影像14；對句「みなもと濁りて末の淸からう筈がない」已指明"),
    ("1099766", 14, "たま〴〵", "たま〳〵", "原圖的くの字点無濁點"),
]


def apply(pid_filter: str = None, cache_dir: Path = None) -> int:
    """把更正重套回 ocr-ndl。回傳實際套用的條數。"""
    cache_dir = cache_dir or nb.CACHE_DIR
    n_ok = n_miss = 0
    for pid, img, bad, good, why in CORRECTIONS:
        if pid_filter and pid != pid_filter:
            continue
        f = cache_dir / pid / "ocr-ndl" / ("%07d.txt" % img)
        if not f.exists():
            continue
        t = f.read_text(encoding="utf-8")
        if good and good in t and bad not in t:
            n_ok += 1                      # 已經是對的
            continue
        # 🚨 刪除型更正（good 為空）不能用 `good in t` 判斷已完成 ——
        #    空字串永遠 in，會被誤判成做完而跳過。只看 bad 還在不在。
        if bad not in t:
            n_miss += 1
            print("  ⚠️ %s 影像%-3d 找不到要改的字串（OCR 版本變了？）：%s"
                  % (pid, img, bad[:24]))
            continue
        f.write_text(t.replace(bad, good), encoding="utf-8")
        n_ok += 1
        print("  ✅ %s 影像%-3d %s" % (pid, img, good[:30]))
    if n_miss:
        print("🚨 有 %d 條對不上 —— 這代表 OCR 產出變了，更正要重新確認，"
              "不要放著不管。" % n_miss)
    return n_ok


def main() -> int:
    pid = sys.argv[1] if len(sys.argv) > 1 else None
    n = apply(pid)
    print("套用 %d 條人工更正" % n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
