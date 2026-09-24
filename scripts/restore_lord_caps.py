#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""把欽定本（kjva）與 NIV 語料裡被抹平的 LORD 還原回來。

站上的欽定本、NIV 語料把全大寫的 LORD（上帝聖名 יהוה 的代稱）都寫成了一般的「Lord」，
跟 Adonai（主）分不出來。使用者 2026-09-24：「用原文或和合本來對照，是聖名的就寫上主，
標回 LORD」、「舊約中 主和上主還是要別」。所以中文直譯要分「上主」（聖名）與「主」（Adonai），
得先把英文原文的 LORD 還原。

判斷：舊約每一節，按出現順序把英文的 Lord 對上和合本（cuv1919）的神名：
  耶和華       → 聖名：KJV／NIV 都作 LORD
  主耶和華     → Adonai＋聖名：KJV 印「Lord GOD」、NIV 印「Sovereign LORD」
  主（單獨）    → Adonai：保留 Lord
數目對不上的節不硬改，列進 unresolved 報告。希伯來原文（wlc）有沒有 יהוה 當第二道閘：
原文沒有聖名卻要改成 LORD 的，不改。

    python scripts/restore_lord_caps.py audit     # 試算，印統計與抽樣
    python scripts/restore_lord_caps.py apply     # 寫回本機卷檔（之後 repair_bible_versions.py upload）
    python scripts/restore_lord_caps.py verify /c/tmp/KJV_caps.json   # 拿保留大寫的欽定本驗準確率
"""
from __future__ import annotations

import gzip
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import repair_bible_versions as rbv  # noqa: E402

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

OT = list(rbv.RCUV_BOOKS)[:39]
_NIQQUD = re.compile(r"[֑-ׇ]")
# 和合本的神名，照出現順序。「主」要排掉當一般名詞用的（主人、主母、君主、作主…）。
_CUV_TOK = re.compile(r"主耶和華|耶和華|(?<![君作為做公家店債物東盟霸])主(?![人母子意張日持管婦宰席僕顧])")
_LORD = re.compile(r"\bLord\b")


def cuv_tokens(cuv: str) -> list[str]:
    out = []
    for m in _CUV_TOK.finditer(re.sub(r"\s", "", cuv or "")):
        out.append({"主耶和華": "AY", "耶和華": "Y"}.get(m.group(0), "A"))
    return out


def fix_verse(text: str, cuv: str, wlc: str, style: str) -> tuple[str, str]:
    """回傳（改好的經文, 狀態）。狀態：none／ok／unresolved。
    style＝"kjv"：AY 的那個 Lord 後面接 God → 改成「Lord GOD」；Y → LORD。
    style＝"niv"：AY 的 Lord（前面是 Sovereign）→ LORD；Y → LORD。A 一律不動。"""
    if "יהוה" not in _NIQQUD.sub("", wlc or ""):
        return text, "none"                      # 原文沒有聖名：不動
    toks = cuv_tokens(cuv)
    lords = list(_LORD.finditer(text))
    if not lords:
        return text, "none"
    if "Y" not in toks and "AY" not in toks:
        return text, "none"
    # 數目對得上就照順序對；對不上時：
    #   英文 Lord 不多於和合本「耶和華」的次數 → 全是聖名。和合本常把主詞補寫成耶和華
    #   （創 15:6「亞伯蘭信耶和華，耶和華就以此為他的義」，英文只有一個 Lord），
    #   而和合本的「主」也不一定對到英文 Lord（創 14:22「天地的主」＝possessor）。
    #   「Lord God」要判是主耶和華（Adonai YHWH）還是耶和華神（YHWH Elohim）：
    #   和合本有「主耶和華」而沒有「耶和華神」才算前者。
    yh = [t for t in toks if t in ("Y", "AY")]
    if len(lords) != len(toks):
        if len(lords) > len(yh):
            # 和合本用代名詞省掉了重複的「耶和華」（創 8:21 英文兩個 Lord、和合本一個）。
            # 改數希伯來原文：יהוה 夠多、又完全沒有 אדני（Adonai）→ 英文的 Lord 全是聖名。
            h = _NIQQUD.sub("", wlc or "")
            if "אדני" not in h and h.count("יהוה") >= len(lords):
                return _LORD.sub("LORD", text), "ok"
            return text, "unresolved"
        c = re.sub(r"\s", "", cuv or "")
        ay = "AY" in toks and not re.search(r"耶和華[─—]?神", c)
        toks = ["AY" if ay and re.match(r"\s+God\b", text[m.end():]) else "Y" for m in lords]
    out, last = [], 0
    for m, t in zip(lords, toks):
        out.append(text[last:m.start()])
        if t == "Y":
            out.append("LORD")
        elif t == "AY":
            if style == "kjv":
                # KJV：Adonai YHWH →「Lord GOD」（Lord 是 Adonai，GOD 是聖名）
                out.append("Lord")
                rest = text[m.end():]
                g = re.match(r"(\s+)God\b", rest)
                if g:
                    out.append(g.group(1) + "GOD")
                    last = m.end() + g.end()
                    continue
            else:
                out.append("LORD")               # NIV：Sovereign LORD
        else:
            out.append("Lord")
        last = m.end()
    out.append(text[last:])
    return "".join(out), "ok"


def run(apply: bool) -> None:
    import collections
    stat = collections.Counter()
    samples = collections.defaultdict(list)
    for bk in OT:
        f = rbv.CACHE / f"{bk}.json.gz"
        doc = json.loads(gzip.decompress(f.read_bytes()))
        changed = False
        for ch, rows in doc["chapters"].items():
            for r in rows:
                t = r["t"]
                for ver, style in (("kjva", "kjv"), ("niv", "niv")):
                    src = t.get(ver)
                    if not src:
                        continue
                    new, st = fix_verse(src, t.get("cuv1919", ""), t.get("wlc", ""), style)
                    stat[f"{ver}:{st}"] += 1
                    if st == "unresolved" and len(samples[ver]) < 6:
                        samples[ver].append(f"{bk} {ch}:{r['v']}  {src[:90]}")
                    if new != src:
                        stat[f"{ver}:changed"] += 1
                        if apply:
                            t[ver] = new
                            changed = True
        if apply and changed:
            f.write_bytes(gzip.compress(json.dumps(doc, ensure_ascii=False).encode("utf-8"), 9))
    for k in sorted(stat):
        print(f"  {k:22} {stat[k]:,}")
    for ver, ss in samples.items():
        print(f"== {ver} 對不上的節（抽樣）")
        for s in ss:
            print("   ", s)


def verify(path: str) -> None:
    """拿保留大寫的欽定本逐節比：還原後的 kjva 跟它的 LORD／GOD 位置一不一樣。"""
    ref = json.loads(Path(path).read_text(encoding="utf-8"))
    books = list(rbv.RCUV_BOOKS)
    good = bad = unres = 0
    ex = []
    for bk, book in zip(books[:39], ref["books"][:39]):
        doc = json.loads(gzip.decompress((rbv.CACHE / f"{bk}.json.gz").read_bytes()))
        rows = {(c, r["v"]): r["t"] for c, rs in doc["chapters"].items() for r in rs}
        for c in book["chapters"]:
            for v in c["verses"]:
                t = rows.get((str(c["chapter"]), v["verse"]))
                if not t or not t.get("kjva") or "LORD" not in v["text"] and "GOD" not in v["text"]:
                    continue
                new, st = fix_verse(t["kjva"], t.get("cuv1919", ""), t.get("wlc", ""), "kjv")
                want = re.findall(r"\b(?:LORD|GOD|Lord|God)\b", v["text"])
                got = re.findall(r"\b(?:LORD|GOD|Lord|God)\b", new)
                if st == "unresolved":
                    unres += 1
                elif want == got:
                    good += 1
                else:
                    bad += 1
                    if len(ex) < 8:
                        ex.append(f"{bk} {c['chapter']}:{v['verse']}  要 {want}  得 {got}")
    n = good + bad + unres
    print(f"含 LORD／GOD 的節 {n:,}：完全一致 {good:,}（{good / n:.1%}）、改錯 {bad:,}、對不上沒改 {unres:,}")
    for e in ex:
        print("   ", e)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "audit"
    if cmd == "verify":
        verify(sys.argv[2])
    else:
        run(apply=(cmd == "apply"))
