# -*- coding: utf-8 -*-
"""第三屆臺灣藏傳佛教論壇 論文集排版核心：依樣稿規格重排單篇論文 docx。"""
import re, copy
from lxml import etree

NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = "{%s}" % NS


def Q(t):
    return W + t


CONF = "第三屆臺灣藏傳佛教論壇—藏傳佛教現代化"

F_BODY = "文鼎粗明"
F_HEAD = "全真粗圓體"
F_TITLE = "全真特明體"
F_KAI = "標楷體"
F_HEI = "全真中黑體"
F_TIB = "Microsoft Himalaya"
F_LAT = "Times New Roman"


def _sub(parent, tag, **attrs):
    e = etree.SubElement(parent, Q(tag))
    for k, v in attrs.items():
        e.set(Q(k), str(v))
    return e


def make_rPr(east=F_BODY, sz=22, bold=False, ascii_=None, color=None):
    rPr = etree.Element(Q("rPr"))
    rf = _sub(rPr, "rFonts")
    rf.set(Q("ascii"), ascii_ or F_LAT)
    rf.set(Q("hAnsi"), ascii_ or F_LAT)
    rf.set(Q("eastAsia"), east)
    rf.set(Q("cs"), F_TIB)
    if bold:
        _sub(rPr, "b")
        _sub(rPr, "bCs")
    if color:
        _sub(rPr, "color", val=color)
    _sub(rPr, "kern", val=0)
    _sub(rPr, "sz", val=sz)
    _sub(rPr, "szCs", val=sz)
    return rPr


def make_pPr(jc="both", line=360, rule="exact", before=None, beforeL=None,
             after=None, afterL=None, firstChars=None, first=None,
             leftChars=None, left=None, hangChars=None, hang=None, rPr=None,
             keepNext=False, pageBreak=False):
    pPr = etree.Element(Q("pPr"))
    if pageBreak:
        _sub(pPr, "pageBreakBefore")
    if keepNext:
        _sub(pPr, "keepNext")
    sp = _sub(pPr, "spacing")
    if beforeL is not None:
        sp.set(Q("beforeLines"), str(beforeL))
    if before is not None:
        sp.set(Q("before"), str(before))
    if afterL is not None:
        sp.set(Q("afterLines"), str(afterL))
    if after is not None:
        sp.set(Q("after"), str(after))
    sp.set(Q("line"), str(line))
    sp.set(Q("lineRule"), rule)
    if any(v is not None for v in (firstChars, first, leftChars, left, hangChars, hang)):
        ind = _sub(pPr, "ind")
        if leftChars is not None:
            ind.set(Q("leftChars"), str(leftChars))
        if left is not None:
            ind.set(Q("left"), str(left))
        if firstChars is not None:
            ind.set(Q("firstLineChars"), str(firstChars))
        if first is not None:
            ind.set(Q("firstLine"), str(first))
        if hangChars is not None:
            ind.set(Q("hangingChars"), str(hangChars))
        if hang is not None:
            ind.set(Q("hanging"), str(hang))
    if jc:
        _sub(pPr, "jc", val=jc)
    if rPr is not None:
        pPr.append(copy.deepcopy(rPr))
    return pPr


ROLE = {
    "conf": lambda: (make_pPr(jc="right", line=320, rule="atLeast",
                              rPr=make_rPr(F_HEI, 18, color="333333")),
                     make_rPr(F_HEI, 18, color="333333")),
    "title": lambda: (make_pPr(jc="center", beforeL=100, before=360, afterL=50,
                               after=180, line=400, keepNext=True,
                               rPr=make_rPr(F_TITLE, 40)),
                      make_rPr(F_TITLE, 40)),
    "author": lambda: (make_pPr(jc="center", line=360, afterL=50, after=180,
                                rPr=make_rPr(F_KAI, 32)),
                       make_rPr(F_KAI, 32)),
    "h1": lambda: (make_pPr(beforeL=70, before=252, afterL=50, after=180,
                            line=400, keepNext=True,
                            rPr=make_rPr(F_HEAD, 28)),
                   make_rPr(F_HEAD, 28, bold=True)),
    "h2": lambda: (make_pPr(beforeL=50, before=180, afterL=20, after=72,
                            line=380, keepNext=True,
                            rPr=make_rPr(F_HEAD, 24)),
                   make_rPr(F_HEAD, 24, bold=True)),
    "abshead": lambda: (make_pPr(beforeL=50, before=180, afterL=50, after=180,
                                 line=400, keepNext=True,
                                 rPr=make_rPr(F_HEAD, 28)),
                        make_rPr(F_HEAD, 28, bold=True)),
    "absbody": lambda: (make_pPr(line=460, firstChars=200, first=440,
                                 rPr=make_rPr(F_BODY, 22)),
                        make_rPr(F_BODY, 22)),
    "keyword": lambda: (make_pPr(line=360, rPr=make_rPr(F_BODY, 22)),
                        make_rPr(F_BODY, 22, bold=True)),
    "body": lambda: (make_pPr(line=360, firstChars=200, first=440,
                              rPr=make_rPr(F_BODY, 22)),
                     make_rPr(F_BODY, 22)),
    "quote": lambda: (make_pPr(beforeL=50, before=180, afterL=50, after=180,
                               line=360, leftChars=300, left=720,
                               rPr=make_rPr(F_BODY, 22)),
                      make_rPr(F_KAI, 22)),
    "ref": lambda: (make_pPr(jc=None, line=380, left=440, hangChars=200,
                             hang=440, rPr=make_rPr(F_BODY, 22)),
                    make_rPr(F_BODY, 22)),
    "sign": lambda: (make_pPr(jc="right", line=380, left=440, hangChars=200,
                              hang=440, rPr=make_rPr(F_BODY, 22)),
                     make_rPr(F_BODY, 22)),
    # 行高一定要 auto：exact 會把行內圖片裁成一條（第三屆 29 張圖全中招）
    "figure": lambda: (make_pPr(jc="center", line=240, rule="auto",
                                afterL=30, after=108,
                                rPr=make_rPr(F_BODY, 20)),
                       make_rPr(F_BODY, 20)),
    "cell": lambda: (make_pPr(line=300, rPr=make_rPr(F_BODY, 20)),
                     make_rPr(F_BODY, 20)),
    "note": lambda: (make_pPr(line=260, rPr=make_rPr(F_BODY, 20)),
                     make_rPr(F_BODY, 20)),
    # 議程首頁的置中標題區
    "ctitle": lambda: (make_pPr(jc="center", line=440, afterL=30, after=108,
                                rPr=make_rPr(F_HEAD, 32)),
                       make_rPr(F_HEAD, 32, bold=True)),
    "csub": lambda: (make_pPr(jc="center", line=380, afterL=25, after=90,
                              rPr=make_rPr(F_HEAD, 26)),
                     make_rPr(F_HEAD, 26, bold=True)),
    "ctib": lambda: (make_pPr(jc="center", line=400, afterL=25, after=90,
                              rPr=make_rPr(F_TIB, 24, ascii_=F_TIB)),
                     make_rPr(F_TIB, 24, ascii_=F_TIB)),
    "ccell": lambda: (make_pPr(jc="center", line=320,
                               rPr=make_rPr(F_HEAD, 22)),
                      make_rPr(F_HEAD, 22, bold=True)),
}

FRONT = r"(摘\s*要|Abstract|關鍵詞|關鍵字|Key\s*words?)"
H1_WORD = (r"(引\s*言|前\s*言|導\s*言|導\s*論|緒\s*論|結\s*論|結\s*語|附\s*錄"
           r"|參考文獻|參考書目|徵引文獻|References?|Bibliography|註\s*釋"
           r"|誌\s*謝|後\s*記)")
H1_NUM = (r"^(第[一二三四五六七八九十百\d]+[章節篇部、.．]"
          r"|[一二三四五六七八九十]{1,3}[、.．]"
          r"|[壹貳參肆伍陸柒捌玖拾]{1,2}[、.．]"
          r"|[IVX]{1,5}[.、])")
# 阿拉伯數字起首者容易與「書目清單」混淆，另設嚴格條件
H1_ARABIC = r"^\d{1,2}[.、]\s*\S"
LISTY = r"[《〈]|著作$|譯$|出版|頁\s*\d|https?://"
H2_NUM = (r"^([（(][一二三四五六七八九十]{1,3}[)）]"
          r"|[（(]\d{1,2}[)）]"
          r"|\d{1,2}\.\d{1,2}(\.\d{1,2})?\s*[^\d])")


def classify(text, prev_role, in_refs, has_drawing, in_table):
    t = text.strip()
    if in_table:
        return "cell"
    if has_drawing and len(t) < 60:   # 要在 not t 之前判：純圖段落沒有文字
        return "figure"
    if not t:
        return "body"
    plain = re.sub(r"[\s：:]", "", t)
    if re.fullmatch(FRONT + r"[：:]?", plain, re.I):
        return "abshead" if re.match(r"^(摘要|Abstract)$", plain, re.I) else "keyword"
    if re.match(r"^(關鍵詞|關鍵字|Key\s*words?)\s*[：:【]", t, re.I) or \
       re.match(r"^【(關鍵詞|關鍵字)】", t):
        return "keyword"
    if re.match(r"^(摘\s*要|Abstract)\s*[：:]\s*$", t, re.I):
        return "abshead"
    # 「導論：從佛教女性教育到……」這類帶副題的關鍵詞標題
    if re.match(r"^\s*" + H1_WORD + r"\s*[：:—－]", t) and len(t) <= 48:
        return "h1"
    if len(t) <= 48:
        if re.search(H1_WORD, plain) and len(plain) <= 14:
            return "h1"
        if re.match(H1_NUM, t):
            return "h1"
        if re.match(H2_NUM, t):
            return "h2"
        if (re.match(H1_ARABIC, t) and not re.search(LISTY, t)
                and not t.endswith("。") and not in_refs):
            return "h1"
    if in_refs:
        return "ref"
    if len(t) > 16 and t[0] in "「『“\"" and t[-1] in "」』”\"。":
        return "quote"
    return "body"


SCHEMES = [
    ("chapter",   r"^第[一二三四五六七八九十百\d]+[章篇部]"),
    ("section",   r"^第[一二三四五六七八九十百\d]+節"),
    ("dihao",     r"^第[一二三四五六七八九十百\d]+[、.．]"),
    ("da",        r"^[壹貳參肆伍陸柒捌玖拾]{1,2}[、.．]"),
    ("zh",        r"^[一二三四五六七八九十]{1,3}[、.．]"),
    ("paren_zh",  r"^[（(][一二三四五六七八九十]{1,3}[)）]"),
    ("dotted",    r"^\d{1,2}\.\d{1,2}"),
    ("paren_num", r"^[（(]\d{1,2}[)）]"),
    ("arabic",    r"^\d{1,2}[.、]"),
    ("roman",     r"^[IVX]{1,5}[.、]"),
]


def scheme_of(text):
    """回傳該標題所用的編號體系代號；純文字標題（前言／結論…）回傳 None。"""
    t = text.strip()
    for name, pat in SCHEMES:
        if re.match(pat, t):
            return name
    return None


def is_ref_heading(text):
    p = re.sub(r"[\s：:]", "", text.strip())
    if len(p) > 20:
        return False
    return bool(re.match(
        r"(參考文獻|參考書目|徵引文獻|引用文獻|References?|Bibliography|參考資料)",
        p, re.I))


def para_text(p):
    out = []
    for el in p.iter():
        if el.tag == Q("t"):
            out.append(el.text or "")
        elif el.tag == Q("tab"):
            out.append("\t")
        elif el.tag == Q("br"):
            out.append("\n")
    return "".join(out)


def restyle_para(p, role, keep_bold=True):
    """就地重設段落與 run 格式；保留 run 內容（含圖、註腳參照、藏文）。"""
    pPr_new, rPr_new = ROLE[role]()
    old = p.find(Q("pPr"))
    if old is not None:
        # 只留清單編號；原稿的分節符一律丟掉，否則合本時會多出節、頁首套錯
        keep = [old.find(Q("numPr"))]
        p.remove(old)
        for k in keep:
            if k is not None:
                pPr_new.append(copy.deepcopy(k))
    p.insert(0, pPr_new)
    for r in p.iter(Q("r")):
        txt = "".join(x.text or "" for x in r.iter(Q("t")))
        rp = r.find(Q("rPr"))
        was_bold = rp is not None and rp.find(Q("b")) is not None
        vert = rp.find(Q("vertAlign")) if rp is not None else None
        new = copy.deepcopy(rPr_new)
        if keep_bold and was_bold and role in ("body", "cell", "ref", "absbody") \
           and new.find(Q("b")) is None:
            new.append(etree.Element(Q("b")))
        if vert is not None:
            new.append(copy.deepcopy(vert))
        if txt and any("ༀ" <= c <= "࿿" for c in txt):
            rf = new.find(Q("rFonts"))
            for a in ("ascii", "hAnsi", "eastAsia", "cs"):
                rf.set(Q(a), F_TIB)
        if rp is not None:
            r.remove(rp)
        r.insert(0, new)
