# -*- coding: utf-8 -*-
"""把 Drive 上已下載的一貫道檔案影像盤成站上可讀的清單。

    python -X utf8 scripts/yiguandao_inventory.py

來源是 archives_images.py 下載時同步寫下的 `_書目.txt`（每個資料夾一份，
內容是檔案局書目頁的欄位）。這支腳本只讀那些書目與 jpg 張數，不碰影像本身。

輸出兩層：
  cases  ── 獨立案卷（檔號沒有被別的檔號當前綴的那些），附底下的件數與總張數
  files  ── 案卷底下逐件分開的檔次，掛在所屬案卷下

🚨 影像本身不上站、不上 R2，只留 Drive（政治檔案含大量第三人姓名，檔案局的
   利用說明要求再公開前自行評估）。站上只放這份書目層的清單。

🚨 「補鼠案」在檔案局的寫法是「補」不是「捕」——搜尋時兩個都要試。
"""
import json
import re
from collections import defaultdict
from pathlib import Path

SRC = Path(r"G:/我的雲端硬碟/資料/知識圖工作室/研究資料/國家檔案調閱/影像/yiguandao")
CATALOG = Path(__file__).resolve().parents[1] / "public/content/research-data/archives/yiguandao.json"
OUT = Path(__file__).resolve().parents[1] / "public/content/research-data/yiguandao/inventory.json"

FIELDS = ("案由", "檔號", "全宗", "起訖", "提供方式", "內容摘要")


def read_meta(folder: Path) -> dict:
    """_書目.txt 是 `欄位：值` 的純文字。沒有的欄位就不放進來。"""
    meta = {}
    path = folder / "_書目.txt"
    if not path.exists():
        return meta
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if "：" not in line:
            continue
        key, value = line.split("：", 1)
        key = key.strip()
        if key in FIELDS:
            meta[key] = value.strip()
    return meta


def scan() -> list[dict]:
    rows = []
    for folder in sorted(p for p in SRC.iterdir() if p.is_dir()):
        meta = read_meta(folder)
        if not meta.get("檔號"):
            continue
        rows.append({
            "archiveNo": meta["檔號"],
            "title": meta.get("案由", ""),
            "fonds": meta.get("全宗", ""),
            "dateRange": meta.get("起訖", ""),
            "summary": meta.get("內容摘要", ""),
            "pages": len(list(folder.glob("*.jpg"))),
        })
    return rows


def split_cases(rows: list[dict]) -> list[dict]:
    """把下載回來的資料夾歸到所屬「案」底下。

    誰是案、誰是件，以檔案局書目的 level 欄為準（案 98 筆、件 319 筆），不自己
    從檔號猜——斜線數目靠不住：`A301000000A/0039/B12215/4-1` 是案（四段），
    `AA09000000E/0069/ED37/A1` 也是四段，`A387130000C/0039/D144/2/0003/009`
    六段的才是件。

    🚨 **件層影像是案層影像的重複，不可相加。** archives_images.py 當初把案與
       件都各下載一次；實測 A301000000A/0054/B12215/4-1 案層 195 張、其下一件
       21 張，逐張比對 md5 後 21 張全部落在案層那 195 張裡（檔名編號不同，內容
       相同）。所以某一案的實得張數＝案層資料夾的張數；只有案層沒下載時，才改
       用件層的加總。整批直接加會多算 949 張（4,433 → 實得 3,484）。
    """
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))["groups"][0]["items"]
    case_numbers = sorted(
        {i["archiveNo"].strip() for i in catalog if i.get("level") == "案" and i.get("archiveNo")},
        key=len, reverse=True)

    def parent_of(number: str) -> str:
        for case in case_numbers:                       # 最長前綴優先
            if number == case or number.startswith(case + "/"):
                return case
        return number

    grouped: dict[str, dict] = {}
    children: dict[str, list] = defaultdict(list)
    for row in rows:
        parent = parent_of(row["archiveNo"])
        if row["archiveNo"] == parent:
            grouped[parent] = dict(row)
        else:
            children[parent].append(row)

    cases = []
    for number in sorted(set(grouped) | set(children)):
        case = grouped.get(number) or {
            **{k: v for k, v in children[number][0].items() if k != "pages"},
            "archiveNo": number, "pages": 0,
            "title": children[number][0]["title"].split("/")[0],
        }
        kids = sorted(children[number], key=lambda r: r["archiveNo"])
        case["files"] = kids
        case["filePages"] = sum(k["pages"] for k in kids)
        # 案層有下載就以案層為準；沒有才用件層加總（見上方 🚨）
        case["totalPages"] = case["pages"] or case["filePages"]
        cases.append(case)
    return sorted(cases, key=lambda c: -c["totalPages"])


def pending(cases: list[dict]) -> list[dict]:
    """書目說「可線上閱覽」但還沒下載的 —— 這是待辦清單，不是統計誤差。"""
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))["groups"][0]["items"]
    have = {c["archiveNo"] for c in cases} | {
        f["archiveNo"] for c in cases for f in c["files"]}
    rows = [{
        "archiveNo": i["archiveNo"], "title": i["title"],
        "fonds": i["fonds"], "dateRange": i.get("dateRange", ""),
        "pages": i.get("pages", 0),
    } for i in catalog if i.get("online") and i["archiveNo"] not in have]
    return sorted(rows, key=lambda r: -r["pages"])


def year_histogram() -> list[dict]:
    """按檔案年度（檔號裡的四位數年度）分佈。

    🚨 這條曲線量的是國家的注意力，不是一貫道的活動；民國 42–48 年幾乎空白，
       是那幾年的公文尚未解密或尚未編目，不是查禁停了。
    """
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))["groups"][0]["items"]
    counts = defaultdict(int)
    for item in catalog:
        m = re.search(r"/(\d{4})/", item.get("archiveNo", "") or "")
        if not m:
            m = re.search(r"民國(\d+)年", item.get("dateRange", "") or "")
        if m:
            counts[int(m.group(1))] += 1
    return [{"roc": y, "count": counts[y]} for y in sorted(counts)]


def main() -> None:
    rows = scan()
    cases = split_cases(rows)
    data = {
        "name": "已取得的一貫道國家檔案影像",
        "note": "檔案局國家檔案資訊網「可線上閱覽」者。影像只落地 Drive 供研究，"
                "不上網站也不上 R2；站上僅提供書目與摘要。",
        "source": "國家發展委員會檔案管理局，國家檔案資訊網（https://aa.archives.gov.tw/）",
        "caseCount": len(cases),
        "folderCount": len(rows),
        # 實得張數：案層優先，件層只在案層缺席時才計（件層與案層重複，見 split_cases）
        "pageCount": sum(c["totalPages"] for c in cases),
        "folderPageCount": sum(r["pages"] for r in rows),
        "cases": cases,
        "pending": pending(cases),
        "years": year_histogram(),
    }
    data["pendingPages"] = sum(p["pages"] for p in data["pending"])
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{OUT.name}: {data['caseCount']} 案 / {data['folderCount']} 資料夾 / "
          f"實得 {data['pageCount']:,} 張"
          f"（資料夾張數合計 {data['folderPageCount']:,}，件層與案層重複故不等）；"
          f"待下載 {len(data['pending'])} 筆 {data['pendingPages']:,} 頁")


if __name__ == "__main__":
    main()
