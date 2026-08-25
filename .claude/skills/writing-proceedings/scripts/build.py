# -*- coding: utf-8 -*-
"""逐篇重排：讀 src/ 原稿 → 套樣稿版式 → 寫 build/NN_編號.docx"""
import os, re, sys, copy, shutil, zipfile
from lxml import etree
import ttbf
from ttbf import Q, W, CONF, ROLE, make_pPr, make_rPr, restyle_para, \
    para_text, classify, is_ref_heading, F_BODY, F_LAT, F_TIB
from papers import PAPERS, SESSIONS

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
SRC, BUILD = os.path.join(HERE, "src"), os.path.join(HERE, "build")
BLANK = os.path.join(HERE, "blank.docx")

# 大會決定不收發表人簡歷／照片，只按議程順序排論文
SHOW_BIO = False

PGSZ = dict(w="10886", h="14742")
PGMAR = dict(top="1440", right="1418", bottom="1440", left="1418",
             header="851", footer="992", gutter="0")


def new_sectPr():
    s = etree.Element(Q("sectPr"))
    e = etree.SubElement(s, Q("pgSz"))
    for k, v in PGSZ.items():
        e.set(Q(k), v)
    e = etree.SubElement(s, Q("pgMar"))
    for k, v in PGMAR.items():
        e.set(Q(k), v)
    etree.SubElement(s, Q("cols")).set(Q("space"), "425")
    g = etree.SubElement(s, Q("docGrid"))
    g.set(Q("type"), "lines")
    g.set(Q("linePitch"), "360")
    return s


FN_CT = ("application/vnd.openxmlformats-officedocument"
         ".wordprocessingml.footnotes+xml")
FN_REL = ("http://schemas.openxmlformats.org/officeDocument/2006"
          "/relationships/footnotes")
FN_MIN = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<w:footnotes xmlns:w="%s">'
    '<w:footnote w:type="separator" w:id="-1"><w:p><w:pPr>'
    '<w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr>'
    '<w:r><w:separator/></w:r></w:p></w:footnote>'
    '<w:footnote w:type="continuationSeparator" w:id="0"><w:p><w:pPr>'
    '<w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr>'
    '<w:r><w:continuationSeparator/></w:r></w:p></w:footnote>'
    '</w:footnotes>') % ttbf.NS


def ensure_footnotes(parts):
    """原稿若沒有註腳部件就補一份，作者簡介才能真的掛成頁末註腳。"""
    if "word/footnotes.xml" in parts:
        return
    parts["word/footnotes.xml"] = FN_MIN.encode("utf-8")

    CT = "{http://schemas.openxmlformats.org/package/2006/content-types}"
    ct = etree.fromstring(parts["[Content_Types].xml"])
    o = etree.SubElement(ct, CT + "Override")
    o.set("PartName", "/word/footnotes.xml")
    o.set("ContentType", FN_CT)
    parts["[Content_Types].xml"] = etree.tostring(
        ct, xml_declaration=True, encoding="UTF-8", standalone=True)

    RS = "{http://schemas.openxmlformats.org/package/2006/relationships}"
    rels = etree.fromstring(parts["word/_rels/document.xml.rels"])
    used = {r.get("Id") for r in rels}
    n = 1
    while ("rId%d" % n) in used:
        n += 1
    r = etree.SubElement(rels, RS + "Relationship")
    r.set("Id", "rId%d" % n)
    r.set("Type", FN_REL)
    r.set("Target", "footnotes.xml")
    parts["word/_rels/document.xml.rels"] = etree.tostring(
        rels, xml_declaration=True, encoding="UTF-8", standalone=True)


CJK_SPACE = re.compile(r"(?<=[㐀-鿿　-〿])\s+(?=[㐀-鿿])")
SENT_END = "。！？；」』）》?!;:：、，,."
HEAD_START = re.compile(r"^(第|[（(]|[一二三四五六七八九十]{1,3}[、.]|\d|摘要|Abstract"
                        r"|關鍵|Key)")


def merge_back(prev, cur):
    """被頁碼切斷的句子接回上一段；確定是新段落就不接。"""
    a, b = para_text(prev).strip(), para_text(cur).strip()
    if not a or not b:
        return False
    if a[-1] in SENT_END or HEAD_START.match(b):
        return False
    if len(a) < 12:                      # 太短者多半本來就是獨立短行
        return False
    for r in list(cur.findall(Q("r"))):
        prev.append(r)
    return True


def despace(p):
    """清掉中文字之間的空格（多為 PDF／Google Docs 轉出時的斷行殘跡）。"""
    ts = [t for t in p.iter(Q("t"))]
    for i, t in enumerate(ts):
        s = t.text or ""
        if not s:
            continue
        s2 = CJK_SPACE.sub("", s)
        # 跨 run 邊界：前一段結尾是漢字、本段去掉前導空白後仍以漢字起頭
        if i and s2[:1].isspace():
            prev = (ts[i - 1].text or "").rstrip()
            head = s2.lstrip()
            if prev and "㐀" <= prev[-1] <= "鿿" and head[:1] \
               and "㐀" <= head[0] <= "鿿":
                s2 = head
        if s2 != s:
            t.text = s2
            t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")


def bold_heading(p, txt):
    """無編號但整段粗體且短——原稿慣用的小標寫法。"""
    t = txt.strip()
    if not (2 <= len(t) <= 40) or t[-1] in "。，、；：？！,.;:":
        return False
    if re.search(ttbf.LISTY, t):        # 書名號／頁碼／年份＝引註，不是標題
        return False
    runs = [r for r in p.findall(Q("r"))
            if "".join(x.text or "" for x in r.iter(Q("t"))).strip()]
    if not runs:
        return False
    return all(r.find(Q("rPr")) is not None and r.find(Q("rPr")).find(Q("b")) is not None
               for r in runs)


def mk_para(role, text, runs=None):
    """runs: [(text, bold)] 覆寫；否則整段同一格式。"""
    pPr, rPr = ROLE[role]()
    p = etree.Element(Q("p"))
    p.append(pPr)
    for chunk, bold in (runs or [(text, False)]):
        for i, line in enumerate(chunk.split("\n")):
            r = etree.SubElement(p, Q("r"))
            rp = copy.deepcopy(rPr)
            if bold and rp.find(Q("b")) is None:
                rp.append(etree.Element(Q("b")))
            r.append(rp)
            if i:
                etree.SubElement(r, Q("br"))
            t = etree.SubElement(r, Q("t"))
            t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
            t.text = line
    return p


def add_bio_footnote(fn_root, author_p, bio):
    """以自訂符號 ＊ 掛作者簡介註腳，避免動到原稿註腳編號。"""
    ids = [int(f.get(Q("id"))) for f in fn_root.findall(Q("footnote"))
           if f.get(Q("id")) and f.get(Q("id")).lstrip("-").isdigit()]
    nid = max(ids + [0]) + 1
    fn = etree.SubElement(fn_root, Q("footnote"))
    fn.set(Q("id"), str(nid))
    fn.append(mk_para("note", "＊　" + bio))
    r = etree.SubElement(author_p, Q("r"))
    rp = make_rPr(ttbf.F_KAI, 32)
    etree.SubElement(rp, Q("vertAlign")).set(Q("val"), "superscript")
    r.append(rp)
    ref = etree.SubElement(r, Q("footnoteReference"))
    ref.set(Q("customMarkFollows"), "1")
    ref.set(Q("id"), str(nid))
    t = etree.SubElement(r, Q("t"))
    t.text = "＊"
    return nid


def title_block(pp, fn_root):
    # 會議名不在這裡印：合本後書眉已單雙輪流（單數頁篇名／雙數頁會議名），
    # 篇首頁再印一行就變成兩個頁首
    out = []
    if pp["sub"]:
        out.append(mk_para("title", "", runs=[(pp["title"] + "\n" + pp["sub"], False)]))
    else:
        out.append(mk_para("title", pp["title"]))
    ap = mk_para("author", pp["author"])
    if SHOW_BIO and pp["bio"]:
        if fn_root is not None:
            add_bio_footnote(fn_root, ap, pp["bio"])
        else:
            out.append(mk_para("note", pp["bio"]))
    out.append(ap)
    return out


# w:pPr 的子元素有固定順序，插錯位置 Word 會當成壞檔
PPR_ORDER = ["pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr",
             "widowControl", "numPr", "suppressLineNumbers", "pBdr", "shd",
             "tabs", "suppressAutoHyphens", "kinsoku", "wordWrap",
             "overflowPunct", "topLinePunct", "autoSpaceDE", "autoSpaceDN",
             "bidi", "adjustRightInd", "snapToGrid", "spacing", "ind"]


def pPr_of(p):
    pPr = p.find(Q("pPr"))
    if pPr is None:
        pPr = etree.Element(Q("pPr"))
        p.insert(0, pPr)
    return pPr


def ensure_flag(p, name):
    """在 pPr 裡補一個旗標元素，並放到 schema 規定的位置。"""
    pPr = pPr_of(p)
    if pPr.find(Q(name)) is not None:
        return
    rank = PPR_ORDER.index(name)
    at = len(pPr)
    for i, el in enumerate(pPr):
        tag = etree.QName(el).localname
        if tag not in PPR_ORDER or PPR_ORDER.index(tag) > rank:
            at = i
            break
    pPr.insert(at, etree.Element(Q(name)))


def is_h1_para(p):
    """判斷是不是節標題：本 pipeline 產出的 h1 版式＝全真粗圓體 14pt。"""
    rPr = p.find(Q("pPr") + "/" + Q("rPr"))
    if rPr is None:
        return False
    rf, sz = rPr.find(Q("rFonts")), rPr.find(Q("sz"))
    return (rf is not None and sz is not None
            and rf.get(Q("eastAsia")) == ttbf.F_HEAD and sz.get(Q("val")) == "28")


def refs_on_new_page(body):
    """參考文獻／References 一律另起一頁。"""
    n = 0
    for p in body.findall(Q("p")):
        if is_ref_heading(para_text(p).strip()):
            ensure_flag(p, "pageBreakBefore")
            n += 1
    return n


def blank_line_between_sections(body):
    """節與節之間空一行：節標題前面若不是空段落就補一個（已有的不重複補）。"""
    n = 0
    for p in list(body.findall(Q("p"))):
        if not is_h1_para(p) or p.getprevious() is None:
            continue
        # 摘要／Abstract 緊接在署名之下，不是「節」，前面不補空行
        if re.fullmatch(r"(摘\s*要|Abstract)[：:]?", para_text(p).strip(), re.I):
            continue
        prev = p.getprevious()
        if prev.tag == Q("p") and not para_text(prev).strip():
            continue
        if prev.tag != Q("p") and prev.tag != Q("tbl"):
            continue
        gap = mk_para("body", "")
        p.addprevious(gap)
        n += 1
    return n


def strip_lead_space(body):
    """段首手打的空白（半形／全形／tab）清掉。表格內的段落不動。"""
    n = 0
    for p in body.findall(Q("p")):
        hit = False
        for t in p.iter(Q("t")):
            s = t.text or ""
            if not s.strip():          # 整段都是空白的 run，清掉再看下一個
                if s:
                    t.text, hit = "", True
                continue
            new = s.lstrip(" \u3000\t")
            if new != s:
                t.text, hit = new, True
            break
        n += 1 if hit else 0
    return n


def set_keep_next(p):
    """讓這一段與下一段黏在同一頁。"""
    pPr = p.find(Q("pPr"))
    if pPr is None:
        pPr = etree.Element(Q("pPr"))
        p.insert(0, pPr)
    if pPr.find(Q("keepNext")) is None:
        pPr.insert(0, etree.Element(Q("keepNext")))


def keep_tables_whole(body):
    """表格整塊不跨頁：每列不可分頁，末列以外都黏住下一段，
    表格正上方的小標（如「甘丹寺」）也一併黏住，免得標題與表身被拆到兩頁。"""
    for tbl in body.iter(Q("tbl")):
        rows = tbl.findall(Q("tr"))
        if not rows:
            continue
        for r in rows:
            trPr = r.find(Q("trPr"))
            if trPr is None:
                trPr = etree.Element(Q("trPr"))
                r.insert(0, trPr)
            if trPr.find(Q("cantSplit")) is None:
                trPr.insert(0, etree.Element(Q("cantSplit")))
        for r in rows[:-1]:
            for p in r.iter(Q("p")):
                set_keep_next(p)
        prev = tbl.getprevious()
        if prev is not None and prev.tag == Q("p"):
            set_keep_next(prev)


def drop_blank_paras(plan):
    """原稿拿空段落當行距用；版式已有固定行高，空段落一律拿掉。
    表格內的空儲存格段落要留，兩個表格之間的空段也要留（否則 Word 會把表格併成一個）。"""
    n = 0
    for p, role, txt in plan:
        if txt.strip():
            continue
        par = p.getparent()
        if par is None or any(a.tag == Q("tc") for a in p.iterancestors()):
            continue
        i = list(par).index(p)
        if 0 < i < len(par) - 1 and par[i - 1].tag == Q("tbl") \
           and par[i + 1].tag == Q("tbl"):
            continue
        par.remove(p)
        n += 1
    return n


def process(pp, idx):
    dst = os.path.join(BUILD, "%02d_%s.docx" % (idx, pp["num"].replace(".", "-")))
    src = os.path.join(SRC, pp["src"]) if pp["src"] else BLANK
    shutil.copyfile(src, dst)

    zin = zipfile.ZipFile(dst)
    parts = {n: zin.read(n) for n in zin.namelist()}
    zin.close()

    root = etree.fromstring(parts["word/document.xml"])
    body = root.find(Q("body"))
    if SHOW_BIO and pp["bio"]:
        ensure_footnotes(parts)
    fn_root = (etree.fromstring(parts["word/footnotes.xml"])
               if "word/footnotes.xml" in parts else None)

    INNER = {Q("txbxContent"), Q("drawing"), Q("pict"), Q("object")}

    def nested(p):
        """圖說／文字方塊內的段落維持原樣，不套內文版式。"""
        return any(a.tag in INNER for a in p.iterancestors())

    paras = [p for p in body.iter(Q("p")) if not nested(p)]
    # 1) 丟掉原稿標題區：切到「起始標記」那一段為止
    cut = 0
    if pp.get("start"):
        pat = re.compile(pp["start"])
        for i, p in enumerate(paras):
            if pat.match(para_text(p).strip()):
                cut = i
                break
        else:
            raise SystemExit("！%s 找不到起始標記 %r" % (pp["num"], pp["start"]))
    for p in paras[:cut]:
        p.getparent().remove(p)
    paras = paras[cut:]

    # 原稿殘留的雜訊段（如 Google Docs 匯出的「第 N 頁」）；
    # 這類頁碼常把一個句子切成兩段，移除後要把被切斷的句子接回去
    if pp.get("strip"):
        junk = re.compile(pp["strip"])
        keep, cut_here = [], False
        for p in paras:
            if junk.match(para_text(p).strip()):
                p.getparent().remove(p)
                cut_here = True
                continue
            if cut_here and keep and merge_back(keep[-1], p):
                p.getparent().remove(p)
            else:
                keep.append(p)
            cut_here = False
        paras = keep

    # 2) 先分類一輪，順便判定本篇的標題層級
    # 若原稿大量段落整段粗體（多為轉檔所致），粗體就不足以當標題訊號
    bolds = sum(1 for p in paras if bold_heading(p, para_text(p)))
    use_bold = bolds < max(6, len(paras) * 0.12)

    plan, in_refs, prev = [], False, None
    for p in paras:
        despace(p)
        txt = para_text(p)
        if is_ref_heading(txt):
            in_refs = True
        in_tbl = any(a.tag == Q("tc") for a in p.iterancestors())
        drawn = (p.find(".//" + Q("drawing")) is not None
                 or p.find(".//" + Q("pict")) is not None)
        role = classify(txt, prev, in_refs, drawn, in_tbl)
        if use_bold and role == "body" and not in_tbl and not in_refs \
           and bold_heading(p, txt):
            role = "h1"
        if role in ("h1", "h2") and in_refs and not is_ref_heading(txt):
            role = "ref"
        plan.append([p, role, txt])
        prev = role

    top = None                       # 最先出現的編號體系＝第一層
    for _, role, txt in plan:
        if role in ("h1", "h2"):
            s = ttbf.scheme_of(txt)
            if s:
                top = s
                break

    stats = {}
    for p, role, txt in plan:
        if role in ("h1", "h2"):
            s = ttbf.scheme_of(txt)
            role = "h1" if (s is None or s == top) else "h2"
        # 該篇粗體不可靠時（整段整段地粗），內文就不沿用原稿粗體
        restyle_para(p, role, keep_bold=use_bold)
        stats[role] = stats.get(role, 0) + 1

    if pp.get("squeeze"):
        print("      清掉空段落 %d 段" % drop_blank_paras(plan))
    strip_lead_space(body)
    keep_tables_whole(body)
    refs_on_new_page(body)
    blank_line_between_sections(body)

    # 3) 加上新的標題區
    for i, p in enumerate(title_block(pp, fn_root)):
        body.insert(i, p)

    # 4) 版面：清掉所有殘留分節符，全篇一節
    for s in root.iter(Q("sectPr")):
        par = s.getparent()
        if par is not None:
            par.remove(s)
    body.append(new_sectPr())

    # 5) 註腳一律小一號
    if fn_root is not None:
        for i, p in enumerate(fn_root.iter(Q("p"))):
            if p.getparent().get(Q("id")) in ("0", "1", "-1"):
                continue
            restyle_para(p, "note")
        parts["word/footnotes.xml"] = etree.tostring(
            fn_root, xml_declaration=True, encoding="UTF-8", standalone=True)

    parts["word/document.xml"] = etree.tostring(
        root, xml_declaration=True, encoding="UTF-8", standalone=True)

    zout = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
    for n, d in parts.items():
        zout.writestr(n, d)
    zout.close()
    return dst, len(paras), stats


if __name__ == "__main__":
    os.makedirs(BUILD, exist_ok=True)
    # 只清本腳本產生的論文檔；前置頁由 front.py 管，別誤刪
    if not sys.argv[1:]:
        for f in os.listdir(BUILD):
            if re.match(r"^\d{2}_", f):
                os.remove(os.path.join(BUILD, f))
    only = sys.argv[1:]          # 給編號就只重排那幾篇，其餘沿用既有 build/
    for i, pp in enumerate(PAPERS, 1):
        if only and pp["num"] not in only:
            continue
        if pp["src"] is None:
            print("%2d  %-6s ⚠ 稿件未到，產生佔位頁：%s" % (i, pp["num"], pp["title"]))
        dst, n, stats = process(pp, i)
        top = ", ".join("%s=%d" % kv for kv in
                        sorted(stats.items(), key=lambda x: -x[1])[:6])
        print("%2d  %-6s %-34s 段=%3d  %s"
              % (i, pp["num"], pp["author"], n, top))
