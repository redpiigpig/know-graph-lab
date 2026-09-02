# -*- coding: utf-8 -*-
"""語料層：跨刊物的關鍵詞年表與脈絡取樣。

這一層存在的理由，是原站做不到的三件事：逐年頻次曲線、跨語料交叉、以及把
某個詞的全部上下文一次攤開。單看某一本刊物的官網只能一次查一個詞、拿到一串
沒有計數的分頁結果，做不成概念史的證據。

掃描 R2 上各語料的全文，對一份策展詞表算出：
  詞 × 語料 × 年 的「提及次數」與「有提到的篇數」，另存每個詞的少量脈絡（KWIC）。

年份來源逐語料不同，取不到年份的篇目一律歸到 "" 這一桶，不做內插——刊期不規則
（妙心早年月刊、後改雙月刊），內插出來的年表看起來像對的，其實是假的。

  python -X utf8 scripts/corpus_terms.py --build [--corpus tcnn]
  python -X utf8 scripts/corpus_terms.py --publish
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dadaodao_fulltext as df  # noqa: E402  .env / s3

REPO = Path(__file__).resolve().parents[1]
CONTENT = REPO / "public/content/research-data"
TERMS_FILE = REPO / "public/content/research-data/corpus-terms.json"
COUNTS_KEY = "corpus-index/term-counts.json"
KWIC_PER_TERM = 6          # 每個詞每個語料留幾則脈絡
KWIC_WINDOW = 60           # 脈絡前後各取幾個字

# 策展詞表：概念史的兩組關鍵詞 + 八人系譜 + 議題結盟的場域詞。
# 要加詞就改這裡再 --build；沒有必要做成任意詞查詢——那需要全文索引，
# 而這批語料的用途是回答特定的歷史問題，不是當搜尋引擎。
TERM_GROUPS = {
    "佛教概念": ["人生佛教", "人間佛教", "此時、此地、此人", "人間淨土", "護生", "緣起", "契理契機"],
    "基督教概念": ["本色化", "本土化", "實況化", "處境化", "鄉土神學", "出頭天", "上帝國", "自決"],
    "佛教系譜": ["太虛", "印順", "傳道法師", "昭慧", "性廣", "妙心寺", "弘誓"],
    "基督教系譜": ["黃彰輝", "宋泉盛", "王憲治", "黃伯和", "長老教會", "普世教會協會", "南神"],
    "公共議題": ["反核", "動物保護", "廢除死刑", "同志", "性別平權", "反賭", "八敬法", "人權宣言", "跨宗教"],
    "無教會": ["無教會", "無教会", "內村鑑三", "内村鑑三", "矢內原忠雄", "矢内原忠雄", "金教臣", "無境界"],
}
# 日文語料照原樣收，所以「無教会」「内村鑑三」這種日文字形要各自成詞——
# 同一個概念在中日文寫法不同，合併計數會讓兩邊的曲線互相污染。


def all_terms():
    return [t for group in TERM_GROUPS.values() for t in group]


# ── 各語料的讀法：回傳 (doc_id, 年, 標題, 全文) ──────────────────────────
def iter_tcnn():
    for key in sorted(df.r2_existing_keys("pct-fulltext/tcnn")):
        body = df.r2_get_text(key)
        for line in body.splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            yield str(r["id"]), r["date"][:4], r["title"], r["text"]


def _iter_txt(prefix, meta_by_key):
    """逐篇一個 .txt 的語料；年份與標題由 index 檔提供（沒有就留空）。"""
    for key in sorted(df.r2_existing_keys(prefix)):
        meta = meta_by_key.get(key, {})
        text = df.r2_get_text(key)
        yield key, meta.get("year", ""), meta.get("title", Path(key).stem), text


def _load_index(path):
    p = CONTENT / path
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []


def iter_miaoxin():
    meta = {}
    for issue in _load_index("yinshun-hongshi/miaoxin-index.json"):
        for a in issue["articles"]:
            meta[f"yinshun-hongshi-fulltext/妙心雜誌/{a['srcKey'].split('/')[-1]}.txt"] = {
                "year": (a.get("date") or "")[:4], "title": a["title"]}
    return _iter_txt("yinshun-hongshi-fulltext/妙心雜誌", meta)


def iter_new_messenger():
    meta = {}
    for issue in _load_index("pct/new-messenger-index.json"):
        year = (issue.get("date") or "")[:4]      # 期別出刊日，站方「發行日期」欄
        for a in issue["articles"]:
            meta[a["textKey"]] = {"year": year, "title": a["title"]}
    return _iter_txt("pct-fulltext/new-messenger", meta)


def iter_hongshi_magazine():
    meta = {}
    for it in _load_index("yinshun-hongshi/magazine-index.json"):
        year = str(it.get("date", ""))[:4]
        for part in it.get("parts", []):
            stem = Path(part["key"]).stem
            meta[f"yinshun-hongshi-fulltext/弘誓雙月刊/{stem}.txt"] = {
                "year": year, "title": f"第{it['issue']}期"}
    return _iter_txt("yinshun-hongshi-fulltext/弘誓雙月刊", meta)


def iter_xuanzang():
    meta = {}
    for it in _load_index("yinshun-hongshi/xuanzang-index.json"):
        for a in it["articles"]:
            stem = Path(a["pdfKey"]).stem
            meta[f"yinshun-hongshi-fulltext/玄奘佛學研究/{stem}.txt"] = {
                "year": "", "title": a["title"]}
    return _iter_txt("yinshun-hongshi-fulltext/玄奘佛學研究", meta)


def iter_faryin():
    meta = {}
    for it in _load_index("yinshun-hongshi/faryin-index.json"):
        for a in it["articles"]:
            if not a.get("pdfKey"):
                continue
            stem = Path(a["pdfKey"]).stem
            meta[f"yinshun-hongshi-fulltext/法印學報/{stem}.txt"] = {
                "year": "", "title": a["title"]}
    return _iter_txt("yinshun-hongshi-fulltext/法印學報", meta)



def iter_pct_documents():
    meta = {}
    for r in _load_index("pct/documents-index.json"):
        meta[r["textKey"]] = {"year": r.get("year", ""), "title": r["title"]}
    return _iter_txt("pct-fulltext/pct-documents", meta)


def iter_laijohn():
    meta = {}
    for p in _load_index("pct/laijohn-index.json"):
        for a in p["articles"]:
            meta[a["textKey"]] = {"year": "", "title": a["title"]}
    return _iter_txt("pct-fulltext/laijohn", meta)


def iter_mukyokai():
    meta = {}
    for r in _load_index("mukyokai/index.json"):
        meta[r["textKey"]] = {"year": r.get("year", ""), "title": r["title"]}
    return _iter_txt("mukyokai-fulltext", meta)


def iter_nonchurch():
    meta = {}
    for r in _load_index("mukyokai/nonchurch-index.json"):
        meta[r["textKey"]] = {"year": "", "title": f"第{r['issue']}期 {r['title']}"}
    return _iter_txt("mukyokai-fulltext/nonchurch", meta)


def iter_ct():
    """《基督教論壇報》。日期只在列表頁上，所以年份一律由篇目清單提供。"""
    meta = {f"evangelical-fulltext/ct/{r['id']}.txt":
            {"year": (r.get("date") or "")[:4], "title": r["title"]}
            for r in _load_index("evangelical/ct-articles.json")}
    return _iter_txt("evangelical-fulltext/ct", meta)


def iter_krt():
    """《國度復興報》。按快照年打包在 evangelical-fulltext/krt/<年>.jsonl.gz。

    🚨 **年份一律回空字串**。這批只有 capturedAt（Wayback 快照日）而沒有發布日期
    ——三種欄位都驗過是站台固定值或快照日（見 press_krt.py）。快照日是「發布日的
    上限」不是發布日，拿它當年份會讓年代曲線看起來成立而其實是假的。
    語料層本來就把取不到年份的歸到 "" 那一桶，這裡照辦。
    """
    for key in sorted(df.r2_existing_keys("evangelical-fulltext/krt")):
        for line in df.r2_get_text(key).splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            yield str(r["id"]), "", r.get("title", ""), r["text"]


CORPORA = {
    "tcnn": {"name": "台灣教會公報新聞網", "side": "基督教", "iter": iter_tcnn},
    "ct": {"name": "基督教論壇報", "side": "基督教", "iter": iter_ct},
    "krt": {"name": "國度復興報", "side": "基督教", "iter": iter_krt},
    "new-messenger": {"name": "新使者", "side": "基督教", "iter": iter_new_messenger},
    "miaoxin": {"name": "妙心雜誌", "side": "佛教", "iter": iter_miaoxin},
    "hongshi": {"name": "弘誓雙月刊", "side": "佛教", "iter": iter_hongshi_magazine},
    "xuanzang": {"name": "玄奘佛學研究", "side": "佛教", "iter": iter_xuanzang},
    "faryin": {"name": "法印學報", "side": "佛教", "iter": iter_faryin},
    "pct-documents": {"name": "長老教會總會文獻", "side": "基督教", "iter": iter_pct_documents},
    "laijohn": {"name": "本土信徒傳記", "side": "基督教", "iter": iter_laijohn},
    "mukyokai": {"name": "無教會研究", "side": "基督教", "iter": iter_mukyokai},
    "nonchurch": {"name": "無境界者", "side": "基督教", "iter": iter_nonchurch},
}


def kwic(text, term, window=KWIC_WINDOW):
    i = text.find(term)
    if i < 0:
        return ""
    a, b = max(0, i - window), min(len(text), i + len(term) + window)
    return re.sub(r"\s+", " ", text[a:b]).strip()


def build(only=None):
    terms = all_terms()
    counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))   # term→corpus→year
    docs = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    samples = defaultdict(lambda: defaultdict(list))                       # term→corpus→[..]
    totals = {}

    chars = defaultdict(lambda: defaultdict(int))          # corpus→year→總字數
    for cid, conf in CORPORA.items():
        if only and cid != only:
            continue
        n = 0
        for doc_id, year, title, text in conf["iter"]():
            n += 1
            chars[cid][year] += len(text)
            for t in terms:
                c = text.count(t)
                if not c:
                    continue
                counts[t][cid][year] += c
                docs[t][cid][year] += 1
                if len(samples[t][cid]) < KWIC_PER_TERM:
                    samples[t][cid].append({"docId": doc_id, "year": year,
                                            "title": title[:60], "text": kwic(text, t)})
        totals[cid] = n
        print(f"{conf['name']}：掃過 {n} 篇 / {sum(chars[cid].values()):,} 字", flush=True)

    out = {
        "groups": TERM_GROUPS,
        # 各語料規模差到兩個數量級（教會公報 38,451 篇 vs 法印學報 30 篇），
        # 所以絕對次數不能直接橫向比；chars 讓前端算得出每萬字的相對頻率。
        "corpora": {k: {"name": v["name"], "side": v["side"], "docs": totals.get(k, 0),
                        "chars": sum(chars[k].values()),
                        "charsByYear": dict(chars[k])}
                    for k, v in CORPORA.items()},
        "counts": {t: {c: dict(y) for c, y in cs.items()} for t, cs in counts.items()},
        "docs": {t: {c: dict(y) for c, y in cs.items()} for t, cs in docs.items()},
        "samples": {t: dict(cs) for t, cs in samples.items()},
    }
    if only:
        # 🚨 單一語料的結果不能寫回計數表——build() 產出的是整份表，只掃一個語料
        # 就上傳等於把其他八個語料的計數清成空的。--corpus 只作試跑用。
        hits = sum(1 for t in terms if counts.get(t))
        print(f"\n[試跑] 只掃了 {only}，{hits} 個詞有命中；**未寫回計數表**。"
              f"\n要更新請跑不帶 --corpus 的完整 --build。")
        return

    # 全文計數表不大（策展詞表），但仍放 R2 由 API 供應，repo 只留詞表設定
    df.r2_put_text(COUNTS_KEY, json.dumps(out, ensure_ascii=False))
    TERMS_FILE.parent.mkdir(parents=True, exist_ok=True)
    TERMS_FILE.write_text(json.dumps({"groups": TERM_GROUPS}, ensure_ascii=False, indent=1),
                          encoding="utf-8")
    hits = sum(1 for t in terms if counts.get(t))
    print(f"\n{len(terms)} 個詞、{hits} 個有命中 → R2 {COUNTS_KEY}")


def publish():
    body = df.s3.get_object(Bucket=df.R2_BUCKET, Key=COUNTS_KEY)["Body"].read().decode("utf-8")
    d = json.loads(body)
    for cid, c in d["corpora"].items():
        got = sum(sum(y.values()) for t in d["counts"].values() for k, y in t.items() if k == cid)
        print(f"  {c['name']}：{c['docs']} 篇，命中 {got} 次")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--corpus", choices=sorted(CORPORA))
    args = ap.parse_args()
    if args.build:
        build(args.corpus)
    if args.publish:
        publish()
    if not (args.build or args.publish):
        ap.print_help()


if __name__ == "__main__":
    main()
