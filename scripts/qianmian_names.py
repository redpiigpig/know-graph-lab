# -*- coding: utf-8 -*-
"""千面上帝：拿翻譯定名詞庫掃章稿，把該統一而沒統一的譯名揪出來。

一部七卷本的通史裡，同一個人前面叫「邁蒙尼德」後面叫「麥摩尼德」，是最傷可信度
的那種錯——每一章單獨看都沒問題，合起來才露餡。而站上的 /translation-glossary
已經有 2,200 個定名，正好拿來當權威（見 [[feedback_glossary_strict_authority]]）。

作法：把詞庫的 variants（異名）當成待查字串，在章稿裡找；找到就報告該換成哪個
name_recommended。**只報告不自動改**——譯名是使用者定奪的事，而且同形異義的風險
太高（例如某個異名剛好是另一個詞的一部分）。

用法：python scripts/qianmian_names.py            # 掃全部
      python scripts/qianmian_names.py --fix 邁蒙尼德   # 把某個定名的異名一次換掉
"""
import argparse
import json
import re
import sys
from pathlib import Path

import requests

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
CH = ROOT / "output" / "qianmian" / "chapters"
CACHE = ROOT / "output" / "qianmian" / "glossary.json"
TABLES = ("deities", "historical_rulers", "philosophers", "place_names",
          "scientists", "theologians", "theological_terms", "biblical_people")


def load_glossary():
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    env = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.startswith("#"):
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip().strip('"')
    key = env.get("SUPABASE_SERVICE_KEY") or env["SUPABASE_SERVICE_ROLE_KEY"]
    head = {"apikey": key, "Authorization": f"Bearer {key}"}
    out = {}
    for t in TABLES:
        r = requests.get(f"{env['SUPABASE_URL']}/rest/v1/{t}",
                         params={"select": "*", "limit": "5000"}, headers=head, timeout=60)
        r.raise_for_status()
        for x in r.json():
            rec = x.get("name_recommended") or x.get("name_zh") or x.get("name")
            if not rec:
                continue
            # 異名散在好幾欄：name_variants 是通用的，神學家表另有新教／天主教／
            # 東正教／港／台／陸學界各自的譯法，全部都算「該換成定名」的候選。
            vs = []
            for col in ("name_variants", "name_protestant", "name_catholic_sgs",
                        "name_orthodox", "name_hk", "name_tw", "name_china_academic"):
                raw = x.get(col)
                if not raw:
                    continue
                for v in re.split(r"[,，、/／;；]", str(raw)):
                    v = re.sub(r"[（(].*?[)）]", "", v).strip()   # 去掉「（陸）」這種註記
                    if v:
                        vs.append(v)
            out[rec] = {"variants": sorted(set(vs)), "table": t}
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


def build_index(gloss):
    """異名 → 定名。三個門檻擋掉會出事的替換：

    1. 太短的不查（兩個字的誤判率太高）
    2. 異名本身也是別的條目的定名 → 它是合法的獨立詞，不是誰的異名。
       「拜占庭」是帝國、「君士坦丁堡」是城，「征服者」是稱號、「穆罕默德二世」是人；
       這種對子套下去會毀掉整本書。
    3. 一個異名對到兩個定名 → 詞庫自己有歧義，不碰
    """
    canonical = set(gloss)
    idx, clash = {}, set()
    for rec, info in gloss.items():
        for v in info["variants"]:
            v = v.strip()
            if len(v) < 3 or v == rec or v in canonical:
                continue
            if not re.fullmatch(r"[一-鿿‧·・]+", v):
                continue
            if v in idx and idx[v] != rec:
                clash.add(v)
            idx[v] = rec
    return {k: v for k, v in idx.items() if k not in clash}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", metavar="定名", help="把這個定名的所有異名換成定名")
    a = ap.parse_args()

    idx = build_index(load_glossary())
    print(f"詞庫裡可查的異名 {len(idx)} 個\n")

    hits = {}
    for f in sorted(CH.glob("ch*.md")):
        text = f.read_text(encoding="utf-8")
        for variant, rec in idx.items():
            n = text.count(variant)
            if n:
                hits.setdefault(rec, []).append((f.stem, variant, n))

    if a.fix:
        rec = a.fix
        targets = [v for v, r in idx.items() if r == rec]
        if not targets:
            print(f"詞庫裡沒有「{rec}」，或它沒有登記異名")
            return
        total = 0
        for f in sorted(CH.glob("ch*.md")):
            old = f.read_text(encoding="utf-8")
            lines = old.split("
")
            for i, line in enumerate(lines):
                # `## 節標題` 是對回目錄的鍵，一個字都不能動（稽核就是靠它比對）
                if line.startswith("##"):
                    continue
                for v in targets:
                    # 「馬克斯」不能無差別換成「馬克思」——馬克斯‧繆勒、馬克斯‧韋伯
                    # 都會被改壞。後面接著中間點的一律跳過。
                    line = re.sub(re.escape(v) + r"(?![‧·・])", rec, line)
                lines[i] = line
            text = "
".join(lines)
            if text != old:
                n = sum(old.count(v) for v in targets)
                total += n
                f.write_text(text, encoding="utf-8")
                print(f"  {f.stem}：換掉 {n} 處")
        print(f"\n共 {total} 處改成「{rec}」")
        return

    if not hits:
        print("沒有發現與詞庫定名不符的譯名。")
        return
    print("以下譯名與詞庫的定名不同（只報告，不自動改）：\n")
    for rec, rows in sorted(hits.items(), key=lambda kv: -sum(n for _, _, n in kv[1])):
        total = sum(n for _, _, n in rows)
        where = "、".join(f"{c}×{n}" for c, _, n in rows[:6])
        variants = "／".join(sorted({v for _, v, _ in rows}))
        print(f"  {variants}  →  {rec}    共 {total} 處（{where}）")
    print(f"\n要一次換掉某一個：python scripts/qianmian_names.py --fix 定名")


if __name__ == "__main__":
    main()
