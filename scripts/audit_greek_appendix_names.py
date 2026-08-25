#!/usr/bin/env python3
"""把專名附錄裡「不是名字」的中文清掉。

專名的中文有五條取得路徑（詞庫、信望愛 Strong 中文字典、Strong 英文名對
``biblical_people``、中文聖經逐節對位、音譯），照理只填名字。逐條讀過 340 筆
之後發現兩類錯誤，都出在信望愛那一條：**取到的是字典的釋義而不是名字**
（Ἄζωτος→「非利士人的五個重」、Σήμ→「閃的意思是」、Νηρ→「空氣」），或者
**對到別的條目**（Ισμαηλ→「以色列」、Ιθαμαρ→「亞倫」）。另有幾筆根本不是專名，
是被大小寫判定誤收的普通詞（ὄζω「聞起來」、Ἰουδαϊσμός「猶太教」）。

清單是逐筆看過後列的，不是規則猜的；每一筆都記下當初填進去的錯誤內容，日後修好
取名管線時可以拿來回頭核對。清掉之後那一格是空的——依約定，沒有登錄可依據時空著
才是正確狀態，印出來是「（中文待定）」。

修根因（信望愛回應的解析取錯行）另計，見交接文件。
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APPENDICES = ROOT / "data" / "originalReaders" / "vocabulary" / "greek-appendices.json"
NAME_APPENDIX = "人名、地名與國族"

# lemma -> 當初填進去的錯誤中文。比對用：內容不同就不動，表示來源已經改過。
REJECTED: dict[str, str] = {
    # 取到釋義而不是名字
    "Χεβρων": "更糟",
    "Ιωας": "帶子",
    "Βαλαάμ": "舊約的一個先知",
    "Συμεών": "雅各和利亞所生",
    "ἀλληλούϊα": "你們要讚美神",
    "Αδερ": "沒有",
    "Ναυη": "大型船隻",
    "Ἄζωτος": "非利士人的五個重",
    "Ευαῖος": "橄欖油",
    "Κῦρος": "使生效",
    "Σαφαν": "字意",
    "Σήμ": "閃的意思是",
    "Σηλω": "腐爛",
    "Εφρων": "愚昧",
    "Εφραθα": "打開吧",
    "Ερμα": "旅行用馬車",
    "Νηρ": "空氣",
    "Πόντιος": "將耶穌釘死十字架",
    "Φῆστος": "接續腓力斯的猶大",
    "Αρραν": "男的",
    "Ρομελιας": "利瑪利的兒子",
    "Ἐφέσιος": "以弗所出生的或居",
    "Ωγ": "巴珊王噩",
    "Ηλα": "希伯來文",
    "Ημαθ": "我們",
    "Βαλλα": "投擲",
    "Βαμα": "丘壇",
    # 對到別的條目
    "Κααθ": "瑪押",
    "Ισμαηλ": "以色列",
    "ὄρειος": "烏利亞",
    "Ονιας": "烏西亞",
    "Ιωσεδεκ": "書亞",
    "Ναβατ": "羅波安",
    "Ιθαμαρ": "亞倫",
    "Γεδσων": "基甸",
    "Σαβα": "沙拉",
    "Μελχα": "麥基",
    "Μηδία": "米甸",
    "Ιδουμαῖος": "東人",
    "Μισαηλ": "米迦勒",
    "Βαρουχ": "西鹿",
    "Σηων": "錫安",
    "Ισσααρ": "斯哈",
    "Φαραν": "法老",
    "Ῥαψάκης": "亞述",
    # 兩個名字被併成一格
    "Ζεβεε": "西巴和撒慕拿",
    "Σελμανα": "西巴和撒慕拿",
    # 這兩筆根本不是專名，是大小寫判定誤收的普通詞
    "ὄζω": "驅除味道",
    "Ἰουδαϊσμός": "猶太教",
}

NOTE = (
    "逐筆複核後判定不是這個名字的中文（取到字典釋義、對到別的條目，或根本不是專名），"
    "已清空待取名管線修好後重填。"
)


def main() -> None:
    parser = argparse.ArgumentParser(description="清掉專名附錄裡誤填的中文")
    parser.add_argument("--write", action="store_true", help="寫回 greek-appendices.json")
    args = parser.parse_args()

    payload = json.loads(APPENDICES.read_text(encoding="utf-8"))
    table = next(
        item for item in payload["appendices"] if item["title"] == NAME_APPENDIX
    )

    cleared = []
    changed = []
    missing = set(REJECTED)
    for entry in table["entries"]:
        expected = REJECTED.get(entry["lemma"])
        if expected is None:
            continue
        missing.discard(entry["lemma"])
        current = entry.get("zh", "").strip()
        if current != expected:
            # The source has moved on; leave it alone rather than clearing
            # something this review never looked at.
            changed.append((entry["lemma"], current))
            continue
        entry["zh"] = ""
        entry["zhSource"] = ""
        entry["zhRoute"] = ""
        entry["zhRejected"] = expected
        entry["zhRejectedNote"] = NOTE
        entry["zhRejectedOn"] = date.today().isoformat()
        cleared.append(entry["lemma"])

    named = sum(1 for entry in table["entries"] if entry.get("zh", "").strip())
    print(f"  清空 {len(cleared)} 筆；附錄現有中文 {named}／{len(table['entries'])}")
    if changed:
        print(f"  來源已改、未動 {len(changed)} 筆：{changed[:5]}")
    if missing:
        print(f"  清單裡有 {len(missing)} 筆在附錄找不到：{sorted(missing)[:5]}")

    if args.write:
        APPENDICES.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"已寫回 {APPENDICES}")
    else:
        print("（未寫檔；加 --write 才會更新）")


if __name__ == "__main__":
    main()
