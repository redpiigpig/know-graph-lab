# -*- coding: utf-8 -*-
"""兩本改寫計畫的「近年中外重要研究」——原論文書目之外要補的那一批。

外文走 OpenAlex（免金鑰、有被引數可排重要性）。
🚨 不要用 OpenAlex 的 `search=`：那是模糊全文檢索，查「Taiwanese Buddhist nuns」
   會回阿茲海默症飲食研究。一定要用 `filter=title_and_abstract.search:(...)`，
   而且用布林式把「主題詞 AND 地域詞」綁在一起，否則整個佛教研究都會進來。
🚨 布林式命中不等於題目相關。OpenAlex 是把整段摘要丟進索引，`charismatic` 會撈到
   生態學的 charismatic megafauna，`(gender OR women) AND chinese` 會撈到《劍橋中國史》；
   而且**被引數最高的往往就是這些泛論**，照被引排序等於把雜訊排到最前面。
   所以每組再設一組「必須真的出現的錨詞」，逐筆核對題名與摘要，核不過就丟掉。
🚨 也不要放萬用字元。那個欄位是 stemmed 的，站方直接回 Invalid query 擋掉；
   詞幹處理本來就吃得下單複數，buddhism 一個詞就涵蓋 buddhist。

中文走臺灣博碩士論文（thesis_ndltd.py，另一支）與各校典藏，不在這裡重做。

  python -X utf8 scripts/lit_recent.py            # 兩組都查
  python -X utf8 scripts/lit_recent.py --group ma
"""
import argparse
import json
import subprocess
import time
import urllib.parse
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "public/content/works/degree-recent-lit.json"
SINCE = "2018-01-01"          # 「這幾年」：原碩論寫到 2025，外文回溯到 2018 才接得上
MAIL = "redpiigpig@gmail.com"  # OpenAlex 禮貌池，帶了才不會被丟進慢速佇列

# 每組的錨詞：題名或摘要至少要各命中一項，才算真的在講這件事
ANCHORS = {
    "mahaprajapati-revolution": [
        ["buddh", "bhiksuni", "bhikkhuni", "sangha", "vinaya", "dharma"],
    ],
    "bachelor-evangelical": [
        ["christian", "evangelic", "church", "missionar", "mission",
         "protestant", "pentecostal", "charismatic christian", "presbyterian",
         "catholic", "gospel", "theolog"],
    ],
}

# 地域條件：題名不一定寫得出地名，這一項核題名＋摘要
REGION = {
    "bachelor-evangelical": ["taiwan", "formosa", "chinese", "china", "sinophone", "hong kong"],
}

QUERIES = {
    "mahaprajapati-revolution": [
        ("八敬法與比丘尼戒", "(buddhism AND (nun OR bhiksuni OR bhikkhuni) AND (ordination OR precept OR vinaya OR garudhamma))"),
        ("台灣比丘尼與教團", "(buddhism AND (nun OR bhiksuni OR bhikkhuni) AND taiwan)"),
        ("佛教與性別", "(buddhism AND (gender OR feminism OR feminist OR women) AND (taiwan OR chinese))"),
        ("人間佛教", "(\"humanistic buddhism\" OR \"engaged buddhism\") AND (taiwan OR yinshun OR taixu)"),
        ("昭慧與弘誓", "((chao-hwei OR zhaohui OR hongshi) AND buddhism)"),
        ("佛教動物倫理與社運", "(buddhism AND (animal OR \"social movement\" OR activism) AND taiwan)"),
    ],
    "bachelor-evangelical": [
        ("台灣基督教", "((christianity OR protestant OR church) AND taiwan AND (history OR movement))"),
        ("華人福音派", "(evangelical AND (chinese OR taiwan OR sinophone))"),
        ("台灣宗教與政治", "((religion OR christianity OR church) AND taiwan AND (politics OR political OR state OR authoritarian))"),
        ("長老教會", "(presbyterian AND taiwan)"),
        ("靈恩與五旬節運動", "((pentecostal OR charismatic) AND (taiwan OR chinese))"),
        ("在台宣教史", "((missionary OR mission) AND taiwan AND christianity)"),
    ],
}


def openalex(expr, per_page=50):
    f = f"title_and_abstract.search:{expr},from_publication_date:{SINCE}"
    url = ("https://api.openalex.org/works?filter=" + urllib.parse.quote(f, safe=":,()*\"")
           + f"&sort=cited_by_count:desc&per-page={per_page}&mailto={MAIL}")
    r = subprocess.run(["curl", "-sk", "-m", "90", url], capture_output=True)
    try:
        d = json.loads(r.stdout.decode("utf-8"))
    except Exception:                       # noqa: BLE001
        d = {}
    if "meta" not in d:                     # 站方把錯誤也用 200 回，別當成 0 筆吞掉
        print(f"    ⚠ 查詢被拒：{str(d.get('message', r.stdout[:120]))[:110]}", flush=True)
        return {"meta": {"count": 0}, "results": []}
    return d


def abstract_of(w):
    """OpenAlex 只給倒排索引，要還原成文字才能核錨詞。"""
    inv = w.get("abstract_inverted_index") or {}
    if not inv:
        return ""
    pos = {}
    for word, ps in inv.items():
        for i in ps:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def relevant(w, key):
    """🚨 錨詞只核摘要不夠——泛論書的摘要順口提一句 church 或 buddhism 就過關了
    （《牛津瑪利亞手冊》《劍橋中國史》都是這樣混進來的）。真正以這個題目為主題的
    研究，題名幾乎一定說得出來，所以錨詞一律核**題名**；摘要只用來補地域條件。"""
    title = (w.get("title") or "").lower()
    if not all(any(t in title for t in group) for group in ANCHORS[key]):
        return False
    region = REGION.get(key)
    if region:
        blob = title + " " + abstract_of(w).lower()
        return any(t in blob for t in region)
    return True


def row(w, topic):
    ids = w.get("ids") or {}
    loc = (w.get("primary_location") or {}).get("source") or {}
    return {
        "topic": topic,
        "title": w.get("title") or "",
        "authors": [a["raw_author_name"] for a in w.get("authorships", [])][:6],
        "year": w.get("publication_year"),
        "type": w.get("type"),
        "venue": loc.get("display_name") or "",
        "cited": w.get("cited_by_count", 0),
        "doi": (w.get("doi") or "").replace("https://doi.org/", ""),
        # 有 OA 全文才可能循「同樣的途徑」抓下來，沒有的只能列書目
        "oaUrl": ((w.get("best_oa_location") or {}) or {}).get("pdf_url") or "",
        "isOa": bool(w.get("open_access", {}).get("is_oa")),
        "openalex": ids.get("openalex", ""),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--group")
    a = ap.parse_args()

    out = {}
    for key, qs in QUERIES.items():
        if a.group and a.group not in key:
            continue
        seen, items = set(), []
        for topic, expr in qs:
            d = openalex(expr)
            n = 0
            drop = 0
            for w in d.get("results", []):
                oid = (w.get("ids") or {}).get("openalex", "")
                if oid in seen:
                    continue
                seen.add(oid)
                if not relevant(w, key):
                    drop += 1
                    continue
                items.append(row(w, topic))
                n += 1
            print(f"  {key[:14]:16s} {topic:14s} 命中 {d['meta']['count']:5d} → 收 {n}、濾掉 {drop}",
                  flush=True)
            time.sleep(1)
        items.sort(key=lambda r: (-r["cited"], -(r["year"] or 0)))
        out[key] = {"count": len(items), "oa": sum(1 for r in items if r["isOa"]),
                    "since": SINCE, "items": items}

    if a.group and OUT.exists():                 # 只跑一組時不要洗掉另一組
        prev = json.loads(OUT.read_text(encoding="utf-8")).get("groups", {})
        prev.update(out)
        out = prev
    OUT.write_text(json.dumps({"note": "OpenAlex 檢索的近年外文研究，依被引數排序；"
                                       "isOa 為真者可直接取得全文。",
                               "groups": out}, ensure_ascii=False, indent=1), encoding="utf-8")
    for k, v in out.items():
        print(f"{k}：{v['count']} 筆（可取得全文 {v['oa']}）")
    print(f"→ {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
