#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 archive.org 的 `_djvu.txt` 清成可入庫的純文字。

什麼時候需要：archive.org 同一筆有時給 EPUB 也給 djvu.txt，但**那個 EPUB 可能只是
掃描頁影像沒有文字層**——奧托《論「聖」》就是，parse_worker 直接回
「no extractable text」。這種時候文字在 djvu.txt 裡，而且品質往往不差
（那一份是 Antiqua 不是 Fraktur，德文常見詞命中率正常）。

djvu.txt 的三種機械性雜訊，都與內容無關：
  1. 行尾軟連字號 `¬`（有時是 `-`）把一個字拆成兩行
  2. 字與字之間被塞成兩個以上的空格
  3. 頁碼行、書眉行、archive.org 自己的掃描聲明

🚨 只做機械性清理，不改字。OCR 真正認錯的字（Fraktur 的 ſ→f 那類）留著，
別在這一層自作聰明——看得見的錯遠好過被掩蓋的錯。

  python scripts/archive_djvu_clean.py <in.txt> <out.txt>
  python scripts/archive_djvu_clean.py <in.txt> <out.txt> --drop-headers "DAS HEILIGE"
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

# Google／archive.org 掃描件開頭那一大段聲明，到第一個空行為止
BOILERPLATE = re.compile(
    r"^.*?(?:This is a digital copy of a book|about this book|Über dieses Buch)"
    r".*?(?:\n\s*\n)", re.S | re.I)


def dehyphenate(text: str) -> str:
    """行尾的 `¬` 或 `-` 接下一行行首 → 接回同一個字。"""
    return re.sub(r"[¬\-]\s*\n\s*", "", text)


def collapse_spaces(text: str) -> str:
    """djvu 逐字定位造成的多重空格收成一個；不動換行。"""
    return re.sub(r"[ \t]{2,}", " ", text)


def is_noise_line(line: str, headers: list[str]) -> bool:
    s = line.strip()
    if not s:
        return False
    if re.fullmatch(r"[\dIVXLCivxlc]{1,6}\*?", s):        # 純頁碼（含羅馬數字、9* 這種）
        return True
    if any(h and h.lower() in s.lower() and len(s) < len(h) + 12 for h in headers):
        return True                                       # 書眉：只比書名長一點點
    return False


def clean(text: str, headers: list[str] | None = None) -> str:
    headers = headers or []
    text = BOILERPLATE.sub("", text, count=1)
    text = dehyphenate(text)
    kept = [ln for ln in text.splitlines() if not is_noise_line(ln, headers)]
    text = "\n".join(kept)
    text = collapse_spaces(text)
    # 三個以上換行收成段落分隔
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


# 各語言的常見虛詞。比值＝命中總數 ÷（字元數/10000），低於 80 就該疑心。
PROBE = {
    "en": ["the", "and", "of", "that"],
    "de": ["und", "der", "die", "ist"],
    "fr": ["de", "la", "les", "est"],
    "sv": ["och", "att", "som", "för"],
    "nl": ["de", "het", "een", "van"],
}


def quality(text: str, lang: str = "en") -> dict:
    """判 OCR 是不是整本壞掉。回傳判準數字與結論。

    兩道檢查，缺一不可：

    1. **虛詞比值**——抓「整本被當成別種字體讀」的那種全毀。

    2. 🚨 **長 s 檢查（只對德文）**——抓虛詞比值**漏掉**的那種半毀。
       Fraktur 的長 s（ſ）常被 OCR 讀成 f 或 j，於是 `ist`→`ift`、`sich`→`fich`。
       可是 `und`／`der`／`die` 三個詞**剛好都不含長 s**，所以四詞比值會被它們撐住而
       合格——瑟德布盧姆《Das Werden des Gottesglaubens》(1916) 比值 139.9 看似漂亮，
       實際 `ist` 全書只出現 2 次而 `ift`+`ijt` 有 934 次，整本不能用。
       這一條是 2026-09-11 實測補上的，光看比值會放行。
    """
    words = PROBE.get(lang, PROBE["en"])
    n = lambda w: len(re.findall(r"\b" + w + r"\b", text, re.I))
    per10k = sum(n(w) for w in words) / (len(text) / 10000) if text else 0.0
    out = {"per10k": round(per10k, 1), "counts": {w: n(w) for w in words}}

    if lang == "de":
        ist, ift = n("ist"), n("ift") + n("ijt")
        sich, fich = n("sich"), n("fich")
        out["long_s"] = {"ist": ist, "ift/ijt": ift, "sich": sich, "fich": fich}
        if (ift > ist * 2 and ift > 50) or (fich > sich * 2 and fich > 30):
            out["verdict"] = "fraktur-long-s"
            return out
    out["verdict"] = "ok" if per10k >= 80 else ("weak" if per10k >= 25 else "garbage")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst", nargs="?")
    ap.add_argument("--check", metavar="LANG",
                    help="只驗 OCR 品質不清理（en/de/fr/sv/nl）")
    ap.add_argument("--drop-headers", nargs="*", default=[],
                    help="要當書眉刪掉的字串（書名、章名）")
    a = ap.parse_args()

    raw = Path(a.src).read_text(encoding="utf-8", errors="replace")

    if a.check:
        q = quality(raw, a.check)
        mark = {"ok": "✅ 可用", "weak": "⚠ 偏低",
                "garbage": "✗ 整本廢掉",
                "fraktur-long-s": "🚨 Fraktur 長 s 誤讀（比值會騙人）"}[q["verdict"]]
        print(f"{Path(a.src).name}　{len(raw):,} 字元　每萬字虛詞 {q['per10k']}　{mark}")
        print(f"   {q['counts']}")
        if "long_s" in q:
            print(f"   長 s 檢查 {q['long_s']}")
        return

    if not a.dst:
        raise SystemExit("要清理就得給 dst，或改用 --check LANG 只驗品質")
    out = clean(raw, a.drop_headers)
    Path(a.dst).write_text(out, encoding="utf-8")
    print(f"{len(raw):,} → {len(out):,} 字元　({len(raw.splitlines()):,} → {len(out.splitlines()):,} 行)")
    print(f"→ {a.dst}")


if __name__ == "__main__":
    main()
