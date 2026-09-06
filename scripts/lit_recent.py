# -*- coding: utf-8 -*-
"""寫作計畫的「近年中外重要研究」——原有書目之外要補的那一批。

原本只服務兩本改寫計畫（碩論與學士論文），2026-09 加入《神學研究宣言》：那本
還沒有正文，需要的不是「補書目」而是「照十二章章目各建一座資料庫」，所以它的
每一組查詢就是一章，topic 直接寫章名，撈回來按 topic 分群即是分章書目。

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
    # 這本談的是學科本身，題材橫跨全部宗教，收窄不到某一傳統或某一地域；
    # 錨詞只求「題名真的在講宗教／神學這一行」，把生態學的 sacred grove、
    # 管理學的 ritual 那類同形詞擋掉就夠。
    "theological-studies-manifesto": [
        ["theolog", "religio", "sacred", "divine", "interreligious", "interfaith",
         "god", "spiritual", "faith", "ritual", "myth", "secular", "church",
         "buddhis", "islam", "christian", "hindu", "pilgrim", "mystic"],
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
    # 十二組＝十二章。topic 就是章名，之後直接當研究回顧的 theme。
    "theological-studies-manifesto": [
        ("一　神學為何需要第二次出發",
         "(theology AND (discipline OR method OR methodology) AND (crisis OR future OR rethinking OR reimagining))"),
        ("二　神學、宗教學與公共大學",
         "(theology AND \"religious studies\" AND (university OR academy OR discipline OR curriculum))"),
        ("三　「神聖」作為開放而有爭議的研究對象",
         "((sacred OR sacrality OR holy) AND (category OR concept OR construction OR critique) AND religion)"),
        ("四　觀看者的旅程：從城邦見證到跨宗教方法",
         "(religion AND (insider OR outsider OR reflexivity OR positionality OR \"participant observation\") AND (method OR fieldwork))"),
        ("五　神學現象學：臨在、缺席與不可掌握",
         "((\"phenomenology of religion\" OR \"theological phenomenology\") OR (apophatic AND theology) OR (theology AND (presence OR absence OR givenness)))"),
        ("六　神學敘事學：人如何住進神聖故事",
         "((narrative AND theology) OR (myth AND ritual AND (narrative OR story)) AND religion)"),
        ("七　神學人類學：從跨文化現象到可修正命題",
         "((\"anthropology of christianity\" OR \"anthropology of religion\" OR \"ethnographic theology\" OR \"theological anthropology\") AND (method OR comparison OR fieldwork OR ethnography))"),
        ("八　神學心理學：宗教經驗、療癒與創傷",
         "((\"psychology of religion\" OR \"religious experience\" OR \"religious trauma\" OR \"spiritual abuse\") AND (conversion OR healing OR trauma OR mystical OR wellbeing))"),
        ("九　神學社會學：制度、權力與反抗",
         "(religion AND (institution OR authority OR power OR resistance) AND (sociology OR movement OR politics))"),
        ("十　比較神學：越界、深讀與回返",
         "((\"comparative theology\" OR \"interreligious theology\" OR \"theology of religions\" OR \"scriptural reasoning\") AND (method OR dialogue OR learning OR hermeneutic))"),
        ("十一　世俗、無神論與非人格神傳統中的神學問題",
         "((atheism OR secularity OR nontheistic OR \"buddhist theology\" OR humanism) AND (theology OR ultimate OR transcendence OR sacred))"),
        ("十二　神學研究所：課程、田野與公共責任",
         "((\"theological education\" OR \"religious education\") AND (curriculum OR pedagogy OR \"public theology\" OR interreligious))"),
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
