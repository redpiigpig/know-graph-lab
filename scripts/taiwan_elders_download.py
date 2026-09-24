"""台灣長老全集下載器（線上全文 → 每冊一檔 txt，保留原書頁碼【頁 N】）。

來源（皆為公開網頁全文，個人研究用，不上傳網站公開區）：
  nanting  南亭和尚全集       https://nanting.dila.edu.tw/   （法鼓文理學院數位典藏組／華嚴蓮社）
  chengyi  成一和尚著作集     https://chengyi.dila.edu.tw/   （同上）
  zhiyu    智諭老和尚著作集   http://zhiyu.seeland.org.tw/   （西蓮淨苑，CBETA 格式）
  dongchu  東初老人全集       http://dongchu.dila.edu.tw/    （法鼓文理學院「東初老和尚紀念數位典藏專輯」）
  yanpei   演培法師全集（CBETA YP 已收部分） https://cbdata.dila.edu.tw/stable/

用法：
  python -X utf8 scripts/taiwan_elders_download.py nanting chengyi zhiyu dongchu yanpei
  python -X utf8 scripts/taiwan_elders_download.py --txt-only nanting   # 只從 _raw 重產 txt

客氣抓取：UA 帶聯絡信箱、每請求間隔 ≥1 秒、失敗重試 3 次；_raw 已有的檔跳過（可中斷續跑）。
"""
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser

ROOT = r"G:\我的雲端硬碟\資料\知識圖工作室\全集\佛學"
UA = "Mozilla/5.0 (kgl-research; personal Buddhist-history research; contact redpiigpig@gmail.com)"
DELAY = 1.2
_last = [0.0]
TXT_ONLY = False


def fetch(url, binary=False):
    for attempt in range(3):
        wait = DELAY - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                b = r.read()
            return b if binary else decode(b)
        except Exception as e:  # noqa: BLE001
            print(f"  ! {url} 第{attempt + 1}次失敗：{e}", flush=True)
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"三次失敗：{url}")


def decode(b):
    for enc in ("utf-8", "cp950", "big5-hkscs", "gb18030"):
        try:
            return b.decode(enc)
        except UnicodeDecodeError:
            pass
    return b.decode("utf-8", "replace")


def cached(url, path):
    """_raw 有就讀檔，沒有就抓（先寫 .part 再改名）。"""
    if os.path.exists(path) and os.path.getsize(path) > 0:
        with open(path, "rb") as f:
            return decode(f.read())
    if TXT_ONLY:
        return None
    b = fetch(url, binary=True)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path + ".part", "wb") as f:
        f.write(b)
    os.replace(path + ".part", path)
    return decode(b)


def safe(s, n=70):
    s = re.sub(r'[\\/:*?"<>|\r\n\t]', "", s).strip()
    return s[:n]


def cjk_count(t):
    return len(re.findall(r"[\u3400-\u9fff\uf900-\ufaff]", t))


def norm_page(p):
    p = p.strip()
    if p.upper().startswith("P."):
        p = p[2:]
    if re.fullmatch(r"\d+", p):
        p = str(int(p))
    return p


# ---------------------------------------------------------------- HTML → txt
class Conv(HTMLParser):
    """通用轉換：pb→【頁 N】、標題→## 、段落換行；略過 lb 行號、選單、TEI header。"""

    BLOCK = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "table"}
    SKIP_IDS = {"tei_header", "menu", "endMenu"}
    SKIP_CLASS = {"lb", "lineInfo", "Menu_bookTitle", "menu"}

    def __init__(self, mode):
        super().__init__(convert_charrefs=True)
        self.mode = mode
        self.out = []
        self.stack = []  # (tag, kind) kind in {'skip','head','pbtext',None}
        self.skip = 0
        self.head = 0
        self.pbtext = 0
        self.cur_head = []
        self.last_page = None

    def page(self, p):
        p = norm_page(p)
        if not p or p == self.last_page:
            return
        self.last_page = p
        self.out.append(f"\n\n【頁 {p}】\n\n")

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = set((a.get("class") or "").split())
        kind = None
        if tag in ("script", "style", "head", "title"):
            kind = "skip"
        elif self.mode == "cbeta" and tag == "span" and "lb" in cls:
            m = re.search(r"_p(\d{4})[a-z]", a.get("id", ""))
            if m:
                self.page(m.group(1))
            kind = "skip"
        elif a.get("id") in self.SKIP_IDS or cls & self.SKIP_CLASS:
            kind = "skip"
        elif "pb" in cls and self.mode != "flow":
            if a.get("data-page"):
                self.page(a["data-page"])
                kind = "skip"
            elif a.get("title"):
                self.page(a["title"])
                kind = "skip"
            else:
                kind = "pbtext"  # <div class="pb">P.0017</div>
        elif tag == "a" and (a.get("onclick") or (a.get("href", "").startswith("#") and "head" not in cls)):
            kind = "skip"  # 顯示頁碼／回目錄 之類的按鈕
        elif cls & {"head", "inline_head"} or any(c.startswith("kepan-head") for c in cls) or (
            self.mode == "cbeta" and tag == "p" and "head" in cls
        ):
            kind = "head"
        elif tag == "img":
            if not self.skip and self.mode != "flow":
                self.out.append("〔缺字〕")
            return
        if tag in ("br", "hr", "img", "meta", "link", "input"):
            if tag == "br" and not self.skip and self.mode == "flow":
                self.out.append("\n")  # 網頁全文：br 即換行（原書換行則不保留，段落靠 p/div）
            return
        if tag in self.BLOCK and not self.skip and not self.head:
            self.out.append("\n")
        self.stack.append((tag, kind))
        if kind == "skip":
            self.skip += 1
        elif kind == "head":
            self.head += 1
            if self.head == 1:
                self.cur_head = []
        elif kind == "pbtext":
            self.pbtext += 1
            self.cur_head = []

    def handle_endtag(self, tag):
        # 找最近的同名 tag
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                break
        else:
            return
        popped = self.stack[i:]
        del self.stack[i:]
        for t, kind in reversed(popped):
            if kind == "skip":
                self.skip -= 1
            elif kind == "head":
                self.head -= 1
                if self.head == 0 and not self.skip:
                    h = re.sub(r"\s+", " ", "".join(self.cur_head)).strip()
                    if h:
                        self.out.append(f"\n\n## {h}\n\n")
            elif kind == "pbtext":
                self.pbtext -= 1
                if self.pbtext == 0:
                    self.page("".join(self.cur_head))
            if t in self.BLOCK and not self.skip and not self.head:
                self.out.append("\n")

    def handle_data(self, d):
        if self.skip:
            return
        if self.head or self.pbtext:
            self.cur_head.append(d)
            return
        self.out.append(re.sub(r"[\r\n\t]+", "", d))

    def text(self):
        t = "".join(self.out).replace(" ", " ")
        t = re.sub(r"[ \u3000]*\n[ \u3000]*", "\n", t)
        t = re.sub(r"\n{3,}", "\n\n", t)
        return t.strip() + "\n"


def to_text(h, mode="axian"):
    c = Conv(mode)
    c.feed(h)
    c.close()
    return c.text()


def write_txt(path, title, source_line, body):
    content = f"# {title}\n{source_line}\n\n{body}"
    with open(path + ".part", "w", encoding="utf-8") as f:
        f.write(content)
    os.replace(path + ".part", path)
    pages = len(re.findall(r"【頁 ", body))
    return {"file": os.path.basename(path), "cjk": cjk_count(body), "pages": pages}


def save_log(outdir, rows):
    with open(os.path.join(outdir, "_下載紀錄.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    tot = sum(r["cjk"] for r in rows)
    print(f"  => {len(rows)} 檔，{tot:,} 字", flush=True)


# ---------------------------------------------------------------- axian 平台（南亭／成一）
def dila_axian(key, name, base, org, coll):
    outdir = os.path.join(ROOT, name)
    raw = os.path.join(outdir, "_raw")
    vd = cached(base + "search.php?vol_dump=yes", os.path.join(raw, "vol_dump.js"))
    vols = json.loads(vd[vd.index("{"): vd.rindex("}") + 1])
    groups = {}
    for k, title in vols.items():
        v = k.split("-")[0]
        groups.setdefault(v, []).append((k, title))
    rows = []
    for v, items in groups.items():
        parts, titles = [], []
        for k, title in items:
            h = cached(base + f"html/{k}.html", os.path.join(raw, f"{k}.html"))
            if h is None:
                continue
            t = re.sub(r"^第[一二三四五六七八九十百]+冊\s*", "", title).strip()
            titles.append(t)
            parts.append(f"## 【{t}】\n來源：{base}main.html?doc={k}\n\n" + to_text(h))
            print(f"  {name} {k} {t}", flush=True)
        vnum = f"{int(v):02d}" if v.isdigit() else v
        fn = f"第{vnum}冊_{safe('、'.join(dict.fromkeys(re.sub(r'[《》〈〉]', '', x) for x in titles)))}.txt"
        src = f"來源：{coll} {base}（{org}）；【頁 N】為原書頁碼（a/b 等前綴為前置頁）"
        rows.append(write_txt(os.path.join(outdir, fn), f"{coll} 第{vnum}冊", src, "\n\n".join(parts)))
    save_log(outdir, rows)


# ---------------------------------------------------------------- 智諭（西蓮淨苑）
def zhiyu():
    name, base = "智諭法師", "http://zhiyu.seeland.org.tw/"
    outdir = os.path.join(ROOT, name)
    raw = os.path.join(outdir, "_raw")
    init = cached(base + "js/init.js", os.path.join(raw, "init.js"))
    books = re.findall(r"(ZY\d+n\d+|works_\d)\s*:\s*'([^']+)'", init)
    groups = {}
    for k, title in books:
        v = "00" if k.startswith("works") else re.match(r"ZY(\d+)n", k).group(1)
        groups.setdefault(v, []).append((k, title))
    rows = []
    for v, items in groups.items():
        parts, titles = [], []
        for k, title in items:
            h = cached(base + f"html/{k}.htm", os.path.join(raw, f"{k}.htm"))
            if h is None:
                continue
            titles.append(title)
            parts.append(f"## 【{title}】\n來源：{base}?book={k}\n\n" + to_text(h))
            print(f"  {name} {k} {title}", flush=True)
        vt = "著作年表" if v == "00" else f"第{v}冊"
        fn = f"{'00' if v == '00' else v}_{vt}_{safe('、'.join(titles))}.txt"
        src = f"來源：智諭老和尚著作集 {base}（西蓮淨苑提供，CBETA 格式）；【頁 N】為原書頁碼"
        rows.append(write_txt(os.path.join(outdir, fn), f"智諭老和尚著作集 {vt}", src, "\n\n".join(parts)))
    save_log(outdir, rows)


# ---------------------------------------------------------------- 東初老人全集
def dongchu():
    name, base = "東初法師", "http://dongchu.dila.edu.tw/"
    outdir = os.path.join(ROOT, name)
    raw = os.path.join(outdir, "_raw")
    idx = cached(base + "web/No2/DonChun2.html", os.path.join(raw, "DonChun2.html"))
    entries = re.findall(r'href="\.\./\.\./html/02/([^"]+)"[^>]*>\s*([^<]+?)\s*<', idx)
    rows, missing = [], []
    # 依資料夾分冊（cwdc_04 一冊含四部書）
    groups = {}
    for rel, title in entries:
        d = rel.split("/")[0] if "/" in rel else "00"
        groups.setdefault(d, []).append((rel, title.strip()))
    for d, items in groups.items():
        titles = [t for _, t in items]
        starts = {rel.split("/")[-1]: (rel, t) for rel, t in items}
        rel0 = items[0][0]
        first = cached(base + "html/02/" + rel0, os.path.join(raw, rel0.replace("/", "__")))
        if first is None:
            continue
        files = []
        m = re.search(r'id="menu".*?id="endMenu"', first, re.S)
        if m and "/" in rel0:  # 同一資料夾＝同一冊，menu 列出整冊的分檔，依序處理一次
            for f in re.findall(r'href="([^"#]+\.html)', m.group(0)):
                if f not in files:
                    files.append(f)
        for f in starts:
            if f not in files:
                files.append(f)
        if "/" not in rel0:  # ps.html＝「未收錄至全集之單篇文章」目次，逐篇展開
            for f0 in list(files):
                h0 = cached(base + "html/02/" + f0, os.path.join(raw, f0))
                for f in re.findall(r'href="(\d+\.html)"', h0 or ""):
                    if f not in files:
                        files.append(f)
        parts = []
        for f in files:
            sub = d + "/" + f if "/" in rel0 else f
            if f in starts:
                parts.append(f"## 【{starts[f][1]}】\n來源：{base}html/02/{starts[f][0]}")
            rawp = os.path.join(raw, sub.replace("/", "__"))
            if os.path.exists(rawp + ".404"):
                h = None
            else:
                try:
                    h = cached(base + "html/02/" + sub, rawp)
                except RuntimeError:
                    h = None
                    if not TXT_ONLY:
                        open(rawp + ".404", "w").close()
            if h is None:
                if os.path.exists(rawp + ".404"):
                    missing.append(sub)
                    parts.append(f"〔缺檔：{base}html/02/{sub} 站上 404〕")
                continue
            parts.append(to_text(h, "dongchu"))
        print(f"  {name} {d} {'、'.join(titles)} ({len(files)} 檔)", flush=True)
        num = re.sub(r"\D", "", d) or "00"
        fn = f"{num}_{safe('、'.join(titles))}.txt"
        src = (f"來源：東初老人全集 {base}（法鼓文理學院「臨濟、曹洞法脈東初老和尚紀念數位典藏專輯」）；"
               "【頁 N】為原書頁碼（每篇首頁未標，自該篇起算）")
        rows.append(write_txt(os.path.join(outdir, fn), f"東初老人全集 {'、'.join(titles)}", src, "\n\n".join(parts)))
    rows.append({"file": "_缺檔（站上404）", "cjk": 0, "pages": 0, "missing": missing})
    save_log(outdir, rows)


# ---------------------------------------------------------------- 演培（CBETA YP）
def yanpei():
    name = "演培法師"
    api = "https://cbdata.dila.edu.tw/stable/"
    outdir = os.path.join(ROOT, name)
    raw = os.path.join(outdir, "_raw")
    works = []
    for q in ["orig-YP"] + [f"orig-YP.00{i}" for i in (4, 5, 6)]:
        j = json.loads(cached(api + f"catalog_entry?q={q}", os.path.join(raw, f"catalog_{q}.json")))
        works += [r["work"] for r in j["results"] if r.get("work")]
    rows = []
    for w in works:
        info = json.loads(cached(api + f"works?work={w}", os.path.join(raw, f"{w}_info.json")))["results"][0]
        body, vol_seen = [], None
        for jn in info["juan_list"].split(","):
            j = cached(api + f"juans?work={w}&juan={jn}", os.path.join(raw, f"{w}_{int(jn):03d}.json"))
            if j is None:
                continue
            h = json.loads(j)["results"][0]
            m = re.search(r'id="(YP\d+)n', h)
            if m and m.group(1) != vol_seen:
                vol_seen = m.group(1)
                body.append(f"\n【冊 {vol_seen}】\n")
            body.append(to_text(h, "cbeta"))
        vol = info["vol"].replace("YP", "").replace("..", "-")
        fn = f"YP{vol}_{w}_{safe(info['title'])}.txt"
        src = (f"來源：CBETA 演培法師全集 https://cbetaonline.dila.edu.tw/{w} （中華電子佛典協會，API cbdata.dila.edu.tw）；"
               "【頁 N】為《演培法師全集》原書頁碼，【冊 YPnn】標冊次")
        rows.append(write_txt(os.path.join(outdir, fn), f"{info['title']}（{info['byline']}）", src, "\n".join(body)))
        print(f"  {name} {w} {info['title']} {info['juan']}卷", flush=True)
    save_log(outdir, rows)


# ---------------------------------------------------------------- 通用：網頁正文抽取
def page_text(h, start_pat=None, end_pats=()):
    if start_pat:
        i = h.find(start_pat)
        if i >= 0:
            h = h[h.find(">", i) + 1:]
    for e in end_pats:
        j = h.find(e)
        if j > 0:
            h = h[:j]
    return to_text(h, "flow")


def post_id(u):
    m = re.search(r"/post/(\d{6,})", u) or re.search(r"/posts/13(\d{6,})", u)
    return m.group(1) if m else None


# ---------------------------------------------------------------- 煮雲（普陀精舍 pixnet 部落格全文）
def zhuyun():
    name = "煮雲法師"
    blog = "https://taiwanpotalaka.pixnet.net/blog/post/"
    outdir = os.path.join(ROOT, name)
    raw = os.path.join(outdir, "_raw")
    toc = cached(blog + "361587840", os.path.join(raw, "361587840.html"))
    seg = toc[toc.find('id="article-content-inner"'):]
    seg = seg[: seg.find("創作者介紹")]
    books = []
    for m in re.finditer(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', seg, re.S):
        pid = post_id(m.group(1))
        t = re.sub(r"<[^>]+>|&nbsp;", " ", m.group(2))
        t = re.sub(r"\s+", " ", t).strip()
        if pid and t and pid not in [b[0] for b in books]:
            books.append((pid, t))
    rows = []
    for n, (pid, title) in enumerate(books, 1):
        th = cached(blog + pid, os.path.join(raw, f"{pid}.html"))
        if th is None:
            continue
        tseg = th[th.find('id="article-content-inner"'):]
        tseg = tseg[: tseg.find("創作者介紹")]
        chaps = []
        for m in re.finditer(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', tseg, re.S):
            cid = post_id(m.group(1))
            if cid and cid != pid and cid not in chaps and "taiwanpotalaka" in m.group(1):
                chaps.append(cid)
        body = [f"## 目次\n\n" + page_text(tseg, 'id="article-content-inner"')]
        for cid in chaps:
            ch = cached(blog + cid, os.path.join(raw, f"{cid}.html"))
            if ch is None:
                continue
            body.append(f"\n〔原文網址：{blog}{cid}〕\n" + page_text(ch, 'id="article-content-inner"', ("創作者介紹", 'class="article-footer"')))
        fn = f"{n:02d}_{safe(title)}.txt"
        src = f"來源：普陀精舍部落格〈煮雲法師全集目錄〉{blog}361587840 （網頁全文，無原書頁碼）"
        rows.append(write_txt(os.path.join(outdir, fn), f"煮雲法師全集·{title}", src, "\n\n".join(body)))
        print(f"  {name} {n:02d} {title}：{len(chaps)} 篇", flush=True)
    save_log(outdir, rows)


# ---------------------------------------------------------------- 廣欽（承天禪寺官網 PDF）
def guangqin():
    name = "廣欽老和尚"
    items = [(47, "廣公上人事蹟續編（隨身版）"), (2, "廣欽老和尚開示錄1_對在家居士開示"), (5, "廣欽老和尚開示錄2_對來訪出家法師開示"),
             (6, "廣欽老和尚開示錄3_對出家弟子開示")] + [(i, f"廣欽老和尚的法藥{k}") for k, i in enumerate([7, 9, 10, 11, 12, 13, 14], 1)]
    outdir = os.path.join(ROOT, name)
    os.makedirs(outdir, exist_ok=True)
    rows = []
    for i, title in items:
        p = os.path.join(outdir, f"{safe(title)}.pdf")
        if not (os.path.exists(p) and os.path.getsize(p) > 0):
            b = fetch(f"https://www.ctbm.org.tw/download/downloadfile/{i}/1.htm", binary=True)
            if not b.startswith(b"%PDF"):
                print(f"  ! {title} 不是 PDF", flush=True)
                continue
            with open(p + ".part", "wb") as f:
                f.write(b)
            os.replace(p + ".part", p)
        rows.append({"file": os.path.basename(p), "bytes": os.path.getsize(p), "cjk": 0, "pages": 0,
                     "source": f"https://www.ctbm.org.tw/download/downloadfile/{i}/1.htm"})
        print(f"  {name} {title}", flush=True)
    save_log(outdir, rows)


# ---------------------------------------------------------------- 斌宗（般若文海「斌宗法師網路專輯」）
def bingzong():
    name = "斌宗法師"
    base = "http://www.bfnn.org/pintsung/"
    outdir = os.path.join(ROOT, name)
    raw = os.path.join(outdir, "_raw")
    links = []
    for page in ("life.htm", "article.htm", "poem.htm"):
        h = cached(base + page, os.path.join(raw, page))
        for u, t in re.findall(r'href="(http://book\.bfnn\.org/article2/\d+\.htm)"[^>]*>(.*?)</a>', h, re.S):
            if u not in [x[0] for x in links]:
                links.append((u, re.sub(r"<[^>]+>", "", t).strip() or page))
    parts = []
    for u, t in links:
        h = cached(u, os.path.join(raw, u.rsplit("/", 1)[-1]))
        full = re.findall(r'href="\.\./books2/(\d+\.htm)"', h)
        if full:  # article2 只是目次卡，全文在 books2
            fu = "http://book.bfnn.org/books2/" + full[0]
            h = cached(fu, os.path.join(raw, "books2_" + full[0]))
            u = fu
        parts.append(f"## 【{t}】\n來源：{u}\n\n" + page_text(h))
        print(f"  {name} {t}", flush=True)
    src = f"來源：般若文海「斌宗法師網路專輯」{base} （網頁全文，無原書頁碼；非全集，為專輯選錄）"
    rows = [write_txt(os.path.join(outdir, "01_斌宗法師網路專輯（文章會集）.txt"), "斌宗法師網路專輯", src, "\n\n".join(parts))]
    save_log(outdir, rows)


# ---------------------------------------------------------------- 李炳南（明倫月刊資訊網「雪公專集」/1pt/ 全站）
def minlun(limit=8000):
    name = "李炳南居士"
    host = "http://www.minlun.org.tw"
    outdir = os.path.join(ROOT, name)
    raw = os.path.join(outdir, "_raw")
    seeds = [f"{host}/1pt/1-dreamweaver/{p}.htm" for p in
             ("20-01", "21-1", "22-1", "24-01", "25-01", "26-1", "23-01", "27-01", "29-01",
              "20-01-2", "20-01-3", "20-01-4", "20-01-05", "20-01-7", "20-01-8", "20-01-9")]
    seen, queue, order = set(), list(seeds), []
    while queue and len(order) < limit:
        u = queue.pop(0)
        u = u.split("#")[0]
        if u in seen:
            continue
        seen.add(u)
        rel = u[len(host) + 1:]
        try:
            h = cached(u, os.path.join(raw, rel.replace("/", os.sep)))
        except Exception as e:  # noqa: BLE001
            print(f"  ! 略過 {u}：{e}", flush=True)
            continue
        if h is None:
            continue
        order.append((rel, h))
        for m in re.finditer(r'(?:href|src)\s*=\s*["\']?([^"\'\s>]+)', h, re.I):
            v = urllib.parse.urljoin(u, html.unescape(m.group(1))).split("#")[0]
            if v.startswith(host + "/1pt/") and re.search(r"\.html?$", v, re.I) and v not in seen:
                queue.append(v)
        if len(order) % 100 == 0:
            print(f"  {name} 已抓 {len(order)} 頁，佇列 {len(queue)}", flush=True)
    groups = {}
    for rel, h in order:
        d = rel.split("/")[1] if rel.count("/") >= 2 else "_root"
        if d == "1-dreamweaver":
            continue  # 導覽框架頁
        groups.setdefault(d, []).append((rel, h))
    rows = []
    for d, pages in groups.items():
        m = re.search(r"<title>(.*?)</title>", pages[0][1], re.S | re.I)
        title = re.sub(r"\s+", "", html.unescape(m.group(1)).replace("\xa0", "")) if m else d
        title = re.sub(r"^明倫/|/雪公$", "", title)
        body = []
        for rel, h in pages:
            t = page_text(h)
            if cjk_count(t) < 20:
                continue
            body.append(f"〔{host}/{rel}〕\n" + t)
        if not body:
            continue
        src = f"來源：明倫月刊資訊網「雪公專集」{host}/1pt/{d}/ （台中蓮社明倫社；網頁全文，無原書頁碼；每段前〔〕為原網頁）"
        rows.append(write_txt(os.path.join(outdir, f"{d}_{safe(title, 50)}.txt"), f"{title}（李炳南）", src, "\n\n".join(body)))
    save_log(outdir, rows)
    print(f"  {name} 共 {len(order)} 頁，{'達上限' if queue else '已抓完'}（剩 {len(queue)}）", flush=True)


# ---------------------------------------------------------------- 道源（海會寺舊站，Wayback 僅存 4 份 .doc）
def daoyuan():
    name = "道源法師"
    outdir = os.path.join(ROOT, name)
    raw = os.path.join(outdir, "_raw")
    rows = []
    for ts, path in [("20110727180827", "word/112802.doc"), ("20110721042732", "word/112807.doc"),
                     ("20110921000737", "word03/112804.doc"), ("20110915044849", "word03/112814.doc")]:
        u = f"https://web.archive.org/web/{ts}id_/http://www.daoyuan-keelung.org/{path}"
        p = os.path.join(raw, path.replace("/", "_"))
        try:
            cached(u, p)
            rows.append({"file": "_raw/" + os.path.basename(p), "bytes": os.path.getsize(p), "cjk": 0, "pages": 0, "source": u})
        except Exception as e:  # noqa: BLE001
            print(f"  ! {u}：{e}", flush=True)
    save_log(outdir, rows)


# ---------------------------------------------------------------- 廣化（GitHub adbdao/VinayaBooksAsJsHtml 的全集 epub／html）
def guanghua():
    name = "廣化律師"
    base = "https://adbdao.github.io/VinayaBooksAsJsHtml/"
    outdir = os.path.join(ROOT, name)
    raw = os.path.join(outdir, "_raw")
    os.makedirs(outdir, exist_ok=True)
    rows = []
    for fn in ("廣化律師全集.epub", "廣化律師全集.html"):
        p = os.path.join(outdir if fn.endswith(".epub") else raw, fn)
        cached(base + urllib.parse.quote(fn), p)
        rows.append({"file": fn, "bytes": os.path.getsize(p), "cjk": 0, "pages": 0, "source": base + fn})
    h = cached(base + urllib.parse.quote("廣化律師全集.html"), os.path.join(raw, "廣化律師全集.html"))
    src = f"來源：{base}廣化律師全集.html （GitHub adbdao/VinayaBooksAsJsHtml 網頁版；無原書頁碼）"
    rows.append(write_txt(os.path.join(outdir, "01_廣化律師全集（網頁版全文）.txt"), "廣化律師全集", src, page_text(h, "<body")))
    save_log(outdir, rows)


# ---------------------------------------------------------------- 懺雲（蓮因寺官網「法寶下載／文字檔」，Dropbox PDF）
CHANYUN = [
    ("01-2015.pdf", "普門品旨要略示"), ("03-2018.pdf", "念佛圓通章旨要略示"), ("02-2017.pdf", "十大願王旨要略示"),
    ("41-2013.pdf", "淨土要義（第一期）"), ("05.pdf", "大乘起信論附表"), ("06.pdf", "大乘起信論旨要略示"),
    ("01.PDF", "佛說八大人覺經表解"), ("02.PDF", "四諦表解"), ("03.PDF", "十二因緣表解"),
    ("04.pdf", "淨土三要述義（懺雲老和尚圈點書籍）"), ("10.pdf", "佛祖開示修行法語（懺雲老和尚輯）"),
    ("31.PDF", "佛七開示第一期（蓮因北齋八十三年）"), ("32-2013.pdf", "佛七開示第二期"), ("33-2016.pdf", "佛七開示第三期"),
    ("05-2011.pdf", "孟子節錄略釋"),
    ("21.pdf", "懺雲老和尚開示錄第一輯"), ("22.pdf", "懺雲老和尚開示錄第二輯"), ("23.pdf", "懺雲老和尚開示錄第三輯"),
    ("11.pdf", "附_蓮音一至十期合刊"), ("12.pdf", "附_蓮音第十二期"), ("13.pdf", "附_蓮音第十三期"),
]


def chanyun():
    name = "懺雲法師"
    outdir = os.path.join(ROOT, name)
    os.makedirs(outdir, exist_ok=True)
    links = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "taiwan_elders_lienyin_links.json"), encoding="utf-8"))
    by_name = {}
    for _, _, u in links:
        by_name.setdefault(u.split("?")[0].rsplit("/", 1)[-1], u)
    rows = []
    for fn, title in CHANYUN:
        u = by_name.get(fn)
        if not u:
            print(f"  ! 找不到連結 {fn}", flush=True)
            continue
        p = os.path.join(outdir, f"{safe(title)}.pdf")
        if not (os.path.exists(p) and os.path.getsize(p) > 0):
            b = fetch(u, binary=True)
            if not b.startswith(b"%PDF"):
                print(f"  ! {title} 不是 PDF（{len(b)} bytes）", flush=True)
                continue
            with open(p + ".part", "wb") as f:
                f.write(b)
            os.replace(p + ".part", p)
        rows.append({"file": os.path.basename(p), "bytes": os.path.getsize(p), "cjk": 0, "pages": 0, "source": u})
        print(f"  {name} {title}", flush=True)
    save_log(outdir, rows)


JOBS = {
    "chanyun": chanyun,
    "guanghua": guanghua,
    "zhuyun": zhuyun,
    "guangqin": guangqin,
    "bingzong": bingzong,
    "minlun": minlun,
    "daoyuan": daoyuan,
    "nanting": lambda: dila_axian("nanting", "南亭法師", "https://nanting.dila.edu.tw/", "法鼓文理學院數位典藏組／華嚴蓮社", "南亭和尚全集"),
    "chengyi": lambda: dila_axian("chengyi", "成一法師", "https://chengyi.dila.edu.tw/", "法鼓文理學院數位典藏組／華嚴蓮社", "成一和尚著作集"),
    "zhiyu": zhiyu,
    "dongchu": dongchu,
    "yanpei": yanpei,
}

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--txt-only" in args:
        TXT_ONLY = True
        args.remove("--txt-only")
    for a in args:
        print(f"== {a}", flush=True)
        JOBS[a]()
