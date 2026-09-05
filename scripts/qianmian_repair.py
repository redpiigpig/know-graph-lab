# -*- coding: utf-8 -*-
"""千面上帝：把已經寫好的章稿裡沒解析掉的註記號補上，並把註號重排成閱讀順序。

為什麼需要這一支：模型有時把幾個來源塞進同一個記號（`〔註:E92, E107〕`），
舊版的正規式只吃單一編號，那些記號就原樣留在正文裡——頁面看起來正常，
但讀者會看到內部記號。寫作端已經修好，這一支負責回頭修已經產出的章。

順便重排註號：修補進來的註如果直接接在最大號之後，正文裡的號碼就會忽大忽小。
Word 的頁下註是照位置自動編號的，所以檔案裡的號碼只是鍵；但網站是照號碼列的，
重排過才不會亂。

用法：python scripts/qianmian_repair.py          # 全部
      python scripts/qianmian_repair.py 2 12     # 只修某幾章
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from qianmian_cite import Citer          # noqa: E402
from qianmian_write import NOTE_MARK, cite_of, load   # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
CH = ROOT / "output" / "qianmian" / "chapters"
FN_DEF = re.compile(r"(?m)^\[\^(\d+)\]:\s*(.+)$")
ANY_MARK = re.compile(r"\[\^(\d+)\]|" + NOTE_MARK.pattern)


def repair(no):
    f = CH / f"ch{no:02d}.md"
    if not f.exists():
        return None
    text = f.read_text(encoding="utf-8")
    ch = load(no)
    citer = Citer()

    old = {int(n): t.strip() for n, t in FN_DEF.findall(text)}
    body = FN_DEF.sub("", text).rstrip()
    body = re.sub(r"\n{3,}", "\n\n", body).rstrip("-\n ") + "\n"

    notes, fixed, lost = [], 0, 0

    def sub(m):
        nonlocal fixed, lost
        if m.group(1):                                  # 已經是 [^n]
            t = old.get(int(m.group(1)))
            if not t:
                lost += 1
                return ""
        else:                                           # 還沒解析的 〔註:…〕
            bodies = []
            for tag in re.split(r"[,，、]", m.group(2)):
                c = cite_of(re.sub(r"\s+", "", tag), ch, citer)
                if c:
                    bodies.append(c.rstrip("。"))
            if not bodies:
                lost += 1
                return ""
            t = "；".join(bodies) + "。"
            fixed += 1
        notes.append(t)
        return f"[^{len(notes)}]"

    body = ANY_MARK.sub(sub, body)
    # 剩下的都是壞掉的記號：沒有 E/R 前綴、或引到不能當出處的東西（讀書會講法）。
    # 一律拿掉——寧可少一個註，也不能把內部記號印進書裡。猜編號比不標更糟。
    body, junk = re.subn(r"〔註[^〕]{0,60}〕", "", body)
    out = body.rstrip() + "\n\n---\n\n" + "\n".join(
        f"[^{i}]: {t}" for i, t in enumerate(notes, 1)) + "\n"
    f.write_text(out, encoding="utf-8")
    return {"no": no, "fixed": fixed, "lost": lost + junk, "notes": len(notes)}


def main():
    want = [int(a) for a in sys.argv[1:]] or list(range(1, 29))
    total = 0
    for no in want:
        r = repair(no)
        if not r:
            continue
        total += r["fixed"]
        if r["fixed"] or r["lost"]:
            print(f"  第{no}章：補回 {r['fixed']} 個殘留記號"
                  + (f"、丟棄 {r['lost']} 個查無來源" if r["lost"] else "")
                  + f"，共 {r['notes']} 註")
    print(f"\n總共補回 {total} 個原本會印在正文裡的內部記號。")


if __name__ == "__main__":
    main()
