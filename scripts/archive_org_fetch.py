#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""從 archive.org 抓公有領域的原典／研究到 Drive 電子圖書館，並建 ebooks 列。

給的是清單（WANTED），一筆一本：archive.org 的 identifier、書名、作者、分類。
腳本挑格式（pdf ＞ epub ＞ djvu.txt）、下載到
`G:/我的雲端硬碟/資料/知識圖工作室/電子圖書館/{category}/{subcategory}/`，
再 INSERT 一列 ebooks 指向 Drive 路徑，交給 `parse_worker.py` 解析出全文。

為什麼要有這支：獵表（z-lib）對近代學術專書的命中率不高，但**譜系學方法論的
幾本關鍵著作與東方諸教會的原典對照本，多數已進入公有領域**，archive.org 直接可取，
不必靠獵表。合法、免費、成功率高。

⚠️ 只放確定公有領域的東西。archive.org 上有大量「借閱制」（controlled digital
lending）的現代書，那些抓不到全檔也不該抓——腳本遇到只有 `_meta.xml` 沒有可下載
內文的項目會跳過並回報。

用法：
  python scripts/archive_org_fetch.py --list          # 只列清單與館內是否已有
  python scripts/archive_org_fetch.py --dry-run       # 查每一筆在 archive.org 有哪些檔
  python scripts/archive_org_fetch.py                 # 真的下載並建列
  python scripts/archive_org_fetch.py --only newman   # 只跑 key 含 newman 的
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DRIVE_ROOT = Path("G:/我的雲端硬碟/資料/知識圖工作室/電子圖書館")
UA = "Mozilla/5.0 (kglab-ingest)"
META = "https://archive.org/metadata/{ident}"
DL = "https://archive.org/download/{ident}/{name}"

# key / archive.org identifier / 書名 / 作者 / 分類 / 子分類 / 為什麼要
WANTED = [
    # ── 譜系學方法論（本書第1章的骨架，館內一本都沒有）
    dict(key="nietzsche-genealogy", ident="genealogyofmoral00nietuoft",
         title="The Genealogy of Morals（論道德的譜系）", author="Friedrich Nietzsche",
         category="哲學", sub="哲學原典",
         why="譜系學一詞的來源；館內有尼采多種但獨缺這一本"),
    dict(key="newman-development", ident="a599872600newmuoft",
         title="An Essay on the Development of Christian Doctrine（論基督教教義的發展）",
         author="John Henry Newman", category="神學", sub="主題專論",
         why="本書第1章第2節的有機體比喻出處；原刊已引用但書不在館內"),
    dict(key="troeltsch-social-1", ident="in.ernet.dli.2015.189046",
         title="The Social Teaching of the Christian Churches, Vol. I",
         author="Ernst Troeltsch", category="宗教學", sub="宗教社會學",
         why="教會／教派類型論；第1章第3節與第5章的分化動力學"),
    dict(key="troeltsch-social-2", ident="in.ernet.dli.2015.238007",
         title="The Social Teaching of the Christian Churches, Vol. II",
         author="Ernst Troeltsch", category="宗教學", sub="宗教社會學",
         why="同上，第二卷"),
    dict(key="niebuhr-social-sources", ident="in.ernet.dli.2015.462204",
         title="The Social Sources of Denominationalism（宗派主義的社會來源）",
         author="H. Richard Niebuhr", category="宗教學", sub="宗教社會學",
         why="第5章新教裂變的主要分析工具；1929 年出版，美國已入公有領域。"
             "原先用的 socialsourcesofd0000nieb_w7z0 是借閱制、回 401；改用 DLI 那份，明確標公有領域"),

    # ── 宗教現象學的斷層：范德列烏的前輩與老師（2026-09-11 使用者批准補齊）
    # 這兩位是「宗教學」成為獨立學科的奠基者，站上原本一本都沒有。
    # 八個 identifier 都逐一驗過 access-restricted-item：全部可下載，非借閱館藏。
    dict(key="tiele-elements-en-1897", ident="elementsofthesci01tieluoft",
         title="Elements of the Science of Religion I（宗教學要義‧卷一）",
         author="Cornelis Petrus Tiele", category="宗教學", sub="宗教學史",
         why="蒂勒的吉福德講座；「宗教學」作為獨立學科的奠基文本之一"),
    dict(key="tiele-outlines-en-1888", ident="outlinesofthehi00tieluoft",
         title="Outlines of the History of Religion（宗教史綱要）",
         author="Cornelis Petrus Tiele", category="宗教學", sub="宗教學史",
         why="十九世紀流傳最廣的宗教史教本，各國譯本的母本"),
    dict(key="tiele-geschichte-de-1896", ident="geschichtederrel02tieluoft",
         title="Geschichte der Religion im Altertum II（古代宗教史‧卷二）",
         author="Cornelis Petrus Tiele", category="宗教學", sub="宗教學史",
         why="德文本；蒂勒的古代近東宗教史"),
    dict(key="tiele-einleitung-de-1899", ident="einleitungindie00gehrgoog",
         title="Einleitung in die Religionswissenschaft（宗教學導論）",
         author="Cornelis Petrus Tiele", category="宗教學", sub="宗教學史",
         why="書名本身就是這門學科的命名"),
    dict(key="chantepie-lehrbuch-de-1905", ident="lehrbuchderreli00sausgoog",
         title="Lehrbuch der Religionsgeschichte（宗教史教本）",
         author="Pierre Daniël Chantepie de la Saussaye", category="宗教學", sub="宗教學史",
         why="宗教現象學的第一部體系性著作；范德列烏的直接前身"),
    dict(key="chantepie-manual-en-1891", ident="manualofscienceo00chan",
         title="Manual of the Science of Religion（宗教學手冊）",
         author="Pierre Daniël Chantepie de la Saussaye", category="宗教學", sub="宗教學史",
         why="上書的英譯，1891"),
    # 🚨 書名要帶年份：1887 初版與 1905 二版**同名**，目標檔名一樣，
    # 下載器看到已存在就整本跳過（實測 1887 那本因此沒下到，而且真下了會蓋掉 1905）。
    dict(key="chantepie-lehrbuch-de-1887", ident="MN40163ucmf_1",
         title="Lehrbuch der Religionsgeschichte (1887 初版)（宗教史教本‧初版）",
         author="Pierre Daniël Chantepie de la Saussaye", category="宗教學", sub="宗教學史",
         why="初版 microform；與 1905 二版並存，看得出體系怎麼長出來"),
    dict(key="chantepie-vierschetsen-nl-1883", ident="vierschetsenuitd00chan",
         title="Vier Schetsen uit de Godsdienstgeschiedenis（宗教史四論）",
         author="Pierre Daniël Chantepie de la Saussaye", category="宗教學", sub="宗教學史",
         why="荷蘭文原著，1883；荷蘭宗教學派的起點"),

    # ── 聖經批判史十本公有領域原著（2026-09-26 使用者指定）
    # 每筆 identifier 都先用 advancedsearch 比過多個版本，挑掃描完整、非節錄、
    # 非借閱制的那份；Schweitzer《Quest of the Historical Jesus》館內已有一份
    # epub（ebooks 表 id b3db3469-…），故不重抓。
    dict(key="bc-spinoza-ttp", ident="chiefworksofbene01spin",
         title="The Chief Works of Benedict de Spinoza, Vol. I（含《神學政治論》Tractatus "
               "Theologico-Politicus, 1670；Elwes 英譯本）",
         author="Baruch Spinoza（R. H. M. Elwes 英譯）", category="神學", sub="聖經批判史",
         why="第一本用歷史批判法讀摩西五經的著作；Elwes 譯本公有領域"),
    dict(key="bc-simon-histoire", ident="histoirecritique01simo",
         title="Histoire critique du Vieux Testament（舊約批判史，1685 增訂新版）",
         author="Richard Simon", category="神學", sub="聖經批判史",
         why="首部以文獻批判法系統質疑摩西著作權的專著；1678 初版付印前即遭焚毀，"
             "1685 鹿特丹增訂版是學界通行的定本"),
    dict(key="bc-astruc-conjectures", ident="conjecturessurl00astr",
         title="Conjectures sur les mémoires originaux dont il paroit que Moyse s'est "
               "servi pour composer le livre de la Genèse（創世記原始底本臆測，1753）",
         author="Jean Astruc", category="神學", sub="聖經批判史",
         why="底本假說（Documentary Hypothesis）的起點，'耶和華／伊羅欣' 底本切分首見於此"),
    dict(key="bc-reimarus-fragmente", ident="fragmenteundant00reimgoog",
         title="Fragmente eines Ungenannten（無名氏殘篇，Lessing 編，1778）",
         author="Hermann Samuel Reimarus（G. E. Lessing 編）", category="神學", sub="聖經批判史",
         why="歷史耶穌研究的起點；Reimarus 死後由 Lessing 匿名發表，開啟「歷史耶穌」與"
             "「信仰基督」的分野"),
    dict(key="bc-eichhorn-at-1", ident="10410481bsb",
         title="Einleitung ins Alte Testament, Bd. 1（舊約導論‧卷一，1780 初版）",
         author="Johann Gottfried Eichhorn", category="神學", sub="聖經批判史",
         why="「舊約導論」（Introduction）作為學科體裁的奠基之作，三卷本第一卷"),
    dict(key="bc-eichhorn-at-2", ident="10410482bsb",
         title="Einleitung ins Alte Testament, Bd. 2（舊約導論‧卷二，1781 初版）",
         author="Johann Gottfried Eichhorn", category="神學", sub="聖經批判史",
         why="同上，第二卷"),
    dict(key="bc-eichhorn-at-3", ident="10410483bsb",
         title="Einleitung ins Alte Testament, Bd. 3（舊約導論‧卷三，1783 初版）",
         author="Johann Gottfried Eichhorn", category="神學", sub="聖經批判史",
         why="同上，第三卷"),
    dict(key="bc-semler-canon-1", ident="10412817bsb",
         title="Abhandlung von freier Untersuchung des Canons, Teil 1（論正典的自由考察‧"
               "第一部，1771）",
         author="Johann Salomo Semler", category="神學", sub="聖經批判史",
         why="首度把「正典」本身當作歷史形成物來考察，區分「聖經」與「神的話」；"
             "四部本第一部"),
    dict(key="bc-semler-canon-2", ident="10412821bsb",
         title="Abhandlung von freier Untersuchung des Canons, Teil 2（論正典的自由考察‧"
               "第二部，1772）",
         author="Johann Salomo Semler", category="神學", sub="聖經批判史",
         why="同上，第二部"),
    dict(key="bc-semler-canon-3", ident="10412822bsb",
         title="Abhandlung von freier Untersuchung des Canons, Teil 3（論正典的自由考察‧"
               "第三部，1773）",
         author="Johann Salomo Semler", category="神學", sub="聖經批判史",
         why="同上，第三部"),
    dict(key="bc-semler-canon-4", ident="10412823bsb",
         title="Abhandlung von freier Untersuchung des Canons, Teil 4（論正典的自由考察‧"
               "第四部，1775）",
         author="Johann Salomo Semler", category="神學", sub="聖經批判史",
         why="同上，第四部（完結）"),
    dict(key="bc-dewette-beitrage", ident="beitragezureinle00deweuoft",
         title="Beiträge zur Einleitung in das Alte Testament（舊約導論補篇，1806–07，"
               "兩卷合訂）",
         author="W. M. L. de Wette", category="神學", sub="聖經批判史",
         why="論歷代志史料價值遠遜摩西五經、質疑摩西著作權的關鍵早期論證；此版兩卷合訂一冊"),
    dict(key="bc-strauss-leben-jesu-1", ident="lifeofjesuscriti01stra",
         title="The Life of Jesus, Critically Examined, Vol. I（耶穌傳批判研究‧卷一，"
               "1860，George Eliot 英譯）",
         author="David Friedrich Strauss（George Eliot 英譯）", category="神學", sub="聖經批判史",
         why="以「神話」（Mythus）解釋福音書神蹟敘事的劃時代著作；引爆十九世紀最大神學論戰"),
    dict(key="bc-strauss-leben-jesu-2", ident="lifeofjesuscriti02stra",
         title="The Life of Jesus, Critically Examined, Vol. II（耶穌傳批判研究‧卷二，"
               "1860，George Eliot 英譯）",
         author="David Friedrich Strauss（George Eliot 英譯）", category="神學", sub="聖經批判史",
         why="同上，第二卷"),
    dict(key="bc-baur-paulus-1", ident="paultheapostle01bauruoft",
         title="Paul, the Apostle of Jesus Christ, Vol. I（保羅：耶穌基督的使徒‧卷一，"
               "1876 英譯）",
         author="Ferdinand Christian Baur", category="神學", sub="聖經批判史",
         why="杜賓學派歷史批判法用於保羅書信真偽考證的代表作，只認四封「真保羅書信」"),
    dict(key="bc-baur-paulus-2", ident="paulapostlejesu00baurgoog",
         title="Paul, the Apostle of Jesus Christ, Vol. II（保羅：耶穌基督的使徒‧卷二，"
               "1875 英譯）",
         author="Ferdinand Christian Baur", category="神學", sub="聖經批判史",
         why="同上，第二卷"),
]

# Patrologia Orientalis：東方諸教會原典的對照譯本（敘利亞／科普特／亞美尼亞／
# 衣索比亞／阿拉伯語原文＋法譯或拉丁譯）。archive.org 上多卷公有領域。
# 卷次很多，先抓與第4章直接相關的幾卷，之後可再擴。
for _vol, _ident in [
    (4, "patrologiaorien04grafplgo"),
    (13, "patrologia-orientalis-volume-13"),
    (17, "patrologia-orientalis-volume-17"),
]:
    WANTED.append(dict(
        key=f"po-{_vol}", ident=_ident,
        title=f"Patrologia Orientalis, Tome {_vol}",
        author="R. Graffin & F. Nau (eds.)",
        category="世界宗教", sub="基督教/東方教會原典",
        why="東方諸教會原典對照譯本；第4章科普特、敘利亞、亞美尼亞三支的一手材料"))

PREFER = (".pdf", ".epub", "_djvu.txt")


def load_env() -> dict:
    env = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def pick_file(files: list[dict], ident: str = "") -> tuple[str, str, int] | None:
    """挑一個可下載的內文檔。回傳 (檔名, 副檔名, 位元組)。

    🚨 Google 掃描的項目（identifier 以 `goog` 結尾）**PDF 沒有文字層**。
    下載回來 527 頁的《Einleitung in die Religionswissenschaft》全書只有 3,467 字，
    而且那些字全是 Google 的版權聲明（"This is a digital copy of a book…"）——
    檔案大小、頁數、下載流程全部正常，只有內容是空的。同一個項目的 `_djvu.txt`
    才有正文（1.1 MB）。所以這類項目把 djvu.txt 排到 PDF 前面。

    🚨 巴伐利亞邦立圖書館（MDZ，identifier 以 `bsb` 結尾）的德文古籍掃描同理，
    只是反過來浪費：PDF 是逐頁高解析度全彩掃描，一冊動輒 150–400 MB，
    而同一項目的 `_djvu.txt` 已經是 OCR 好的全文（幾百 KB～1 MB）。2026-09-26
    抓 Eichhorn／Semler 那批德文原典時實測過（例：10412821bsb 的 PDF 357 MB，
    djvu.txt 只有 944 KB，OCR 品質可用）。故 bsb 項目也把 djvu.txt 排到 PDF 前面，
    不然一本書要收半小時以上還佔滿 Drive 空間。
    """
    prefer = ("_djvu.txt", ".pdf", ".epub") if ident.lower().endswith(("goog", "bsb")) else PREFER
    best = None
    for ext in prefer:
        for f in files:
            name = f.get("name", "")
            if not name.lower().endswith(ext):
                continue
            # archive.org 的縮圖／中繼檔不要
            if "_text.pdf" in name or name.endswith("_meta.txt"):
                continue
            size = int(f.get("size") or 0)
            if size < 50_000:          # 太小的多半是目錄或空殼
                continue
            if best is None or size > best[2]:
                best = (name, ".pdf" if ext == ".pdf" else (".epub" if ext == ".epub" else ".txt"), size)
        if best:
            return best
    return None


def download_resumable(url: str, target: Path, expect: int, tries: int = 6) -> bool:
    """邊收邊寫、斷了用 Range 續傳。

    archive.org 的大檔（50-70 MB）在這條線上常常收到一半就斷（IncompleteRead），
    整檔重來只會再斷一次。改成寫到 .part、記錄已收位元組、用 Range 從斷點續，
    收滿 expect 才改名。這也順帶避免把 70 MB 讀進記憶體。
    """
    part = target.with_suffix(target.suffix + ".part")
    target.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(1, tries + 1):
        have = part.stat().st_size if part.exists() else 0
        if expect and have >= expect:
            break
        headers = {"User-Agent": UA}
        if have:
            headers["Range"] = f"bytes={have}-"
        try:
            req = urllib.request.Request(url, headers=headers)
            t0 = time.time()
            with urllib.request.urlopen(req, timeout=180) as r, open(part, "ab") as fh:
                while True:
                    block = r.read(1 << 20)
                    if not block:
                        break
                    fh.write(block)
            got = part.stat().st_size
            print(f"   ↓ {got/1024/1024:.1f} MB（第 {attempt} 次，{time.time()-t0:.0f}s）")
            if not expect or got >= expect:
                break
        except Exception as e:
            got = part.stat().st_size if part.exists() else 0
            print(f"   … 第 {attempt} 次中斷於 {got/1024/1024:.1f} MB：{type(e).__name__}")
            if attempt == tries:
                print("   ✕ 放棄；.part 留著，下次再跑會從斷點續")
                return False
            time.sleep(5 * attempt)
    if expect and part.stat().st_size < expect:
        print(f"   ✕ 收不齊（{part.stat().st_size}/{expect}）")
        return False
    part.replace(target)
    print(f"   ✓ {target}")
    return True


def already_in_library(env, title_fragment: str) -> str | None:
    import requests
    r = requests.get(
        f'{env["SUPABASE_URL"]}/rest/v1/ebooks',
        headers={"apikey": env["SUPABASE_SERVICE_ROLE_KEY"],
                 "Authorization": f'Bearer {env["SUPABASE_SERVICE_ROLE_KEY"]}'},
        params={"select": "id,title", "title": f"ilike.*{title_fragment}*", "limit": "1"},
        timeout=30,
    )
    rows = r.json() if r.status_code == 200 else []
    return rows[0]["title"] if rows else None


def insert_row(env, item: dict, ext: str, path: Path) -> str | None:
    import requests
    key = env["SUPABASE_SERVICE_ROLE_KEY"]
    r = requests.post(
        f'{env["SUPABASE_URL"]}/rest/v1/ebooks',
        headers={"apikey": key, "Authorization": f"Bearer {key}",
                 "Prefer": "return=representation,resolution=ignore-duplicates",
                 "Content-Type": "application/json"},
        json=[{"title": item["title"], "author": item["author"],
               "file_type": ext.lstrip("."), "category": item["category"],
               "subcategory": item["sub"], "file_path": str(path).replace("/", "\\")}],
        timeout=30,
    )
    if r.status_code in (200, 201):
        rows = r.json()
        return rows[0]["id"] if rows else None
    print(f"    [DB] insert HTTP {r.status_code}: {r.text[:200]}", file=sys.stderr)
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", help="只跑 key 含這個字串的")
    args = ap.parse_args()

    env = load_env()
    items = [w for w in WANTED if not args.only or args.only in w["key"]]

    if args.list:
        for w in items:
            probe = w["title"].split("（")[0].strip()
            hit = already_in_library(env, probe)
            print(f'{"已有" if hit else "缺  "} {w["key"]:24s} {w["title"][:46]}')
            if hit:
                print(f'       館內：{hit[:60]}')
            print(f'       用途：{w["why"]}')
        return 0

    ok = skipped = failed = 0
    for w in items:
        print(f'\n── {w["key"]}  {w["title"][:56]}')
        try:
            meta = fetch_json(META.format(ident=w["ident"]))
        except Exception as e:
            print(f"   中繼取不到：{e}")
            failed += 1
            continue
        files = meta.get("files") or []
        if not files:
            print("   ✕ 沒有可下載的檔（多半是借閱制項目）")
            failed += 1
            continue
        pick = pick_file(files, w["ident"])
        if not pick:
            print(f"   ✕ 沒有合用的內文檔（共 {len(files)} 個檔，可能是借閱制）")
            failed += 1
            continue
        name, ext, size = pick
        print(f'   選檔 {name}  {size/1024/1024:.1f} MB')
        if args.dry_run:
            continue

        target = DRIVE_ROOT / w["category"] / w["sub"] / (
            w["title"].split("（")[0].strip().replace("/", "／")[:80] + ext)
        if target.exists() and target.stat().st_size > 50_000:
            # 檔在但 DB 沒列的話，光 continue 會讓那本書永遠是「看不見的書」——
            # PO 第17卷就是這樣：55 MB 躺在 Drive 上，DB 連一列都沒有。
            print(f"   SKIP 已存在 {target.stat().st_size//1024} KB")
            if not already_in_library(env, w["title"].split("（")[0].strip()):
                print(f'   DB 缺列，補建 → {insert_row(env, w, ext, target)}')
            skipped += 1
            continue
        url = DL.format(ident=w["ident"], name=urllib.parse.quote(name))
        if not download_resumable(url, target, size):
            failed += 1
            continue
        eid = insert_row(env, w, ext, target)
        print(f'   DB {eid or "（未建列，可能已存在）"}')
        ok += 1
        time.sleep(2)

    print(f"\n下載 {ok}／略過 {skipped}／失敗 {failed}")
    if ok:
        print("接著跑 `python scripts/parse_worker.py run` 或等三小時一次的排程解析全文。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
