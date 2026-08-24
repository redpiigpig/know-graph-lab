# -*- coding: utf-8 -*-
"""產生前置頁：書名頁、議程、工作人員名單佔位。"""
import os, re, sys, copy, shutil, zipfile
from lxml import etree
import ttbf
from ttbf import Q, CONF, ROLE, make_pPr, make_rPr, para_text, restyle_para, \
    classify, is_ref_heading
from build import new_sectPr, mk_para
from papers import PAPERS, SESSIONS

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
SRC, BUILD = os.path.join(HERE, "src"), os.path.join(HERE, "build")
BLANK = os.path.join(HERE, "blank.docx")

TIB_TITLE = "༄༅། །ཐའེ་ཝན་བོད་བརྒྱུད་ནང་བསྟན་སྐབས་གསུམ་པའི་གླེང་སྟེགས།"
TIB_THEME = "བོད་བརྒྱུད་ནང་བསྟན་དང་དེང་དུས་ཚན་རིག"


def write_doc(paras, dst):
    shutil.copyfile(BLANK, dst)
    z = zipfile.ZipFile(dst)
    parts = {n: z.read(n) for n in z.namelist()}
    z.close()
    root = etree.fromstring(parts["word/document.xml"])
    body = root.find(Q("body"))
    for ch in list(body):
        body.remove(ch)
    for p in paras:
        body.append(p)
    body.append(new_sectPr())
    parts["word/document.xml"] = etree.tostring(
        root, xml_declaration=True, encoding="UTF-8", standalone=True)
    zo = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
    for n, d in parts.items():
        zo.writestr(n, d)
    zo.close()
    return dst


def big(text, sz, east=ttbf.F_TITLE, after=180, before=0):
    # 藏文屬複合文字，ascii/hAnsi 也要指到藏文字型，否則 Word 落回西文字型出現空框
    asc = ttbf.F_TIB if east == ttbf.F_TIB else None
    pPr = make_pPr(jc="center", line=int(sz * 11), before=before, after=after,
                   rPr=make_rPr(east, sz, ascii_=asc))
    p = etree.Element(Q("p"))
    p.append(pPr)
    r = etree.SubElement(p, Q("r"))
    r.append(make_rPr(east, sz, ascii_=asc))
    t = etree.SubElement(r, Q("t"))
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = text
    return p


def tib(text, sz=28):
    return big(text, sz, east=ttbf.F_TIB, after=240)


def titlepage():
    ps = [big("", 22, after=0, before=1800)]
    ps.append(big("第三屆臺灣藏傳佛教論壇", 52, after=120))
    ps.append(tib(TIB_TITLE, 26))
    ps.append(big("會議主題：藏傳佛教現代化", 36, after=100))
    ps.append(tib(TIB_THEME, 24))
    ps.append(big("", 22, after=600))
    ps.append(big("會 議 論 文 集", 44, east=ttbf.F_HEAD, after=800))
    ps.append(big("中華民國 115 年（2026）9 月 3 日至 4 日", 24,
                  east=ttbf.F_KAI, after=100))
    ps.append(big("玄奘大學雲來社會教育中心多功能會議廳", 24,
                  east=ttbf.F_KAI, after=600))
    # 單位名稱依大會海報
    for line in ("指導單位：達賴喇嘛西藏宗教基金會",
                 "主辦單位：玄奘大學藏傳佛教研究中心・玄奘大學臺灣佛教研究中心",
                 "中華民國三學佛學院",
                 "協辦單位：中華民國國際藏傳佛教研究會",
                 "承辦單位：玄奘大學宗教與文化學系"):
        ps.append(big(line, 22, east=ttbf.F_KAI, after=60))
    return write_doc(ps, os.path.join(BUILD, "00a_titlepage.docx"))


COLS = (1600, 2750, 1750, 1950)        # 姓名／所屬單位／職銜／角色‧場次；合計＝版心寬


def cell_para(txt, bold=False, center=False, sz=20):
    pPr = make_pPr(jc="center" if center else None, line=300,
                   rPr=make_rPr(ttbf.F_BODY, sz))
    p = etree.Element(Q("p"))
    p.append(pPr)
    for i, line in enumerate(str(txt or "").split("\n")):
        r = etree.SubElement(p, Q("r"))
        r.append(make_rPr(ttbf.F_HEAD if bold else ttbf.F_BODY, sz, bold=bold))
        if i:
            etree.SubElement(r, Q("br"))
        t = etree.SubElement(r, Q("t"))
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        t.text = line
    return p


def table_row(values, header=False):
    tr = etree.Element(Q("tr"))
    trPr = etree.SubElement(tr, Q("trPr"))
    etree.SubElement(trPr, Q("cantSplit"))       # 同一列不跨頁拆開
    if header:                                   # 跨頁時重複標題列
        etree.SubElement(trPr, Q("tblHeader"))
    for w, v in zip(COLS, values):
        tc = etree.SubElement(tr, Q("tc"))
        tcPr = etree.SubElement(tc, Q("tcPr"))
        e = etree.SubElement(tcPr, Q("tcW"))
        e.set(Q("w"), str(w))
        e.set(Q("type"), "dxa")
        etree.SubElement(tcPr, Q("vAlign")).set(Q("val"), "center")
        tc.append(cell_para(v, bold=header, center=header))
    return tr


def make_table(rows):
    tbl = etree.Element(Q("tbl"))
    tblPr = etree.SubElement(tbl, Q("tblPr"))
    w = etree.SubElement(tblPr, Q("tblW"))
    w.set(Q("w"), str(sum(COLS)))
    w.set(Q("type"), "dxa")
    etree.SubElement(tblPr, Q("tblLayout")).set(Q("type"), "fixed")
    bd = etree.SubElement(tblPr, Q("tblBorders"))
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = etree.SubElement(bd, Q(side))
        e.set(Q("val"), "single")
        e.set(Q("sz"), "4")
        e.set(Q("color"), "808080")
    mar = etree.SubElement(tblPr, Q("tblCellMar"))
    for side, v in (("top", 40), ("left", 80), ("bottom", 40), ("right", 80)):
        e = etree.SubElement(mar, Q(side))
        e.set(Q("w"), str(v))
        e.set(Q("type"), "dxa")
    grid = etree.SubElement(tbl, Q("tblGrid"))
    for c in COLS:
        etree.SubElement(grid, Q("gridCol")).set(Q("w"), str(c))
    for r in rows:
        tbl.append(r)
    return tbl


# 資料庫譯名與論文署名不一致時，一律以論文本身為準
NAME_FIX = {"阿旺赤列": "昂望聽列"}

# 學者資料庫停在舊議程，以下依 0820 版議程更正
ROLE_FIX = {"A03": ("開幕致詞", "開幕式")}          # 場次二主持人已換人
RANK_FIX = {"A19": "執行長"}                       # 資料庫作「負責人」，議程已更新
INSERT_BEFORE = {
    "A14": ("光持法師",
            "玄奘大學宗教與文化學系；玄奘大學國際暨兩岸事務處／專任助理教授；國際長",
            "主持人", "場次二：社會、情緒與倫理學習（SEE Learning）"),
}


TITLES = ("法師", "仁波切", "堪布", "格西", "上師")


def short_session(ses):
    """場次全名太長，表格內只留「場次一」「開幕式」這層；全名見議程表。"""
    out = []
    for s in " ".join(str(ses or "").split()).split("；"):
        s = s.strip()
        if not s:
            continue
        out.append(s.split("：")[0])
    return "、".join(out)


def monastic_name(name, rank):
    """名錄一律作「某某法師」：去掉「釋」字，法師身分則在名後綴「法師」。
    姓名已含法師時，職銜欄裡重複的「法師」一併去掉。"""
    name = name.lstrip("釋").strip()
    ranks = [r.strip() for r in str(rank or "").split("；") if r.strip()]
    if "法師" in ranks and not name.endswith(TITLES):
        name += "法師"
    if name.endswith("法師"):
        ranks = [r for r in ranks if r != "法師"]
    return name, "；".join(ranks)


def scholars():
    """依學者資料庫產生「與會學者名錄」；個資欄位一律不收。"""
    import openpyxl
    wb = openpyxl.load_workbook(os.path.join(SRC, "scholars.xlsx"), data_only=True)
    ws = wb["發表人 與談人"]
    ps = [big("與會學者名錄", 40, east=ttbf.F_HEAD, before=600, after=120),
          big("（依大會議程順序排列）", 20, east=ttbf.F_BODY, after=320)]
    rows = [table_row(("姓　名", "所屬單位", "職　銜", "角色（場次）"), header=True)]
    seen = set()

    def add(name, org, rank, role, ses):
        role_txt = str(role).replace("；", "、").strip()
        ses_txt = short_session(ses)
        tail = "%s\n（%s）" % (role_txt, ses_txt) if ses_txt else role_txt
        rows.append(table_row((name, org or "－", rank or "－", tail)))

    for row in ws.iter_rows(min_row=2, values_only=True):
        code = str(row[0] or "").strip()
        if code in INSERT_BEFORE:
            n2, o2, r2, s2 = INSERT_BEFORE[code]
            o2, _, k2 = o2.partition("／")
            add(n2, o2, k2, r2, s2)
        name, org, rank, role, ses = (row[1], row[2], row[3], row[5], row[6])
        if code in ROLE_FIX:
            role, ses = ROLE_FIX[code]
        if not name or not role:            # 無角色者為重複列，略過
            continue
        key = (str(name).strip(), str(role).strip())
        if key in seen:
            continue
        seen.add(key)
        name = NAME_FIX.get(str(name).strip(), str(name).strip())
        org = " ".join(str(org or "").split()).replace("；", "、")
        rank = RANK_FIX.get(code, str(rank or "").strip())
        name, rank = monastic_name(name, rank)
        add(name, org, rank.replace("；", "、"), role, ses)

    ps.append(make_table(rows))
    ps.append(mk_para("body", ""))
    return write_doc(ps, os.path.join(BUILD, "00d_scholars.docx"))


def staffpage():
    """把大會提供的「頁尾_工作人員清單」套上論文集版式。"""
    dst = os.path.join(BUILD, "99_staff.docx")
    shutil.copyfile(os.path.join(SRC, "staff.docx"), dst)
    z = zipfile.ZipFile(dst)
    parts = {n: z.read(n) for n in z.namelist()}
    z.close()
    root = etree.fromstring(parts["word/document.xml"])
    body = root.find(Q("body"))
    for p in body.iter(Q("p")):
        txt = para_text(p)
        new = re.sub(r"釋([一-鿿]{2})(?!法師)", r"\1法師", txt)
        if new != txt:                       # 名單一律作「某某法師」
            for r in p.findall(Q("r")):
                p.remove(r)
            r = etree.SubElement(p, Q("r"))
            t = etree.SubElement(r, Q("t"))
            t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
            t.text = new
        restyle_para(p, "h1" if txt.strip() == "工作人員名單" else "ref")
    for s in root.iter(Q("sectPr")):
        s.getparent().remove(s)
    body.insert(0, big("第三屆臺灣藏傳佛教論壇", 32, east=ttbf.F_HEAD,
                       before=600, after=120))
    body.append(new_sectPr())
    parts["word/document.xml"] = etree.tostring(
        root, xml_declaration=True, encoding="UTF-8", standalone=True)
    zo = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
    for n, d in parts.items():
        zo.writestr(n, d)
    zo.close()
    return dst


def agenda():
    """把大會議程 docx 套上論文集版式。"""
    dst = os.path.join(BUILD, "00c_agenda.docx")
    shutil.copyfile(os.path.join(SRC, "agenda_0820.docx"), dst)
    z = zipfile.ZipFile(dst)
    parts = {n: z.read(n) for n in z.namelist()}
    z.close()
    root = etree.fromstring(parts["word/document.xml"])
    body = root.find(Q("body"))
    for p in body.iter(Q("p")):
        txt = para_text(p).strip()
        in_tbl = any(a.tag == Q("tc") for a in p.iterancestors())
        has_tib = any("ༀ" <= c <= "࿿" for c in txt)
        flat = txt.replace(" ", "").replace("　", "")
        if in_tbl:
            # 表首的「議程表」與會議日期也是標題，一併置中
            role = "ccell" if (flat == "議程表" or flat.startswith("中華民國115年")) \
                else "cell"
        elif txt.startswith("第三屆臺灣藏傳佛教論壇"):
            role = "ctitle"          # 大會名稱置中
        elif txt.startswith("會議主題"):
            role = "csub"            # 會議主題置中（同行可含藏文）
        elif has_tib:
            role = "ctib"            # 純藏文行置中
        elif txt.startswith("◆") or txt.startswith("■"):
            role = "cell"
        else:
            role = "h2" if len(txt) <= 30 and txt else "body"
        restyle_para(p, role)
    for s in body.findall(Q("sectPr")):
        body.remove(s)
    # 原議程表格首列已有「議 程 表」，不再另加標題以免重複
    body.append(new_sectPr())
    parts["word/document.xml"] = etree.tostring(
        root, xml_declaration=True, encoding="UTF-8", standalone=True)
    zo = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
    for n, d in parts.items():
        zo.writestr(n, d)
    zo.close()
    return dst


def toc_placeholder():
    return write_doc([big("目 錄", 40, east=ttbf.F_HEAD, before=600, after=400)],
                     os.path.join(BUILD, "00b_toc.docx"))


TEXT_W = 10886 - 1418 * 2          # 版心寬（twips），目錄右定位點


def toc_line(num, title, author, page):
    """條目左、頁碼右，中間點狀前導。"""
    pPr = make_pPr(jc=None, line=380, left=560, hangChars=0, hang=560,
                   rPr=make_rPr(ttbf.F_BODY, 22))
    tabs = etree.Element(Q("tabs"))
    tb = etree.SubElement(tabs, Q("tab"))
    tb.set(Q("val"), "right")
    tb.set(Q("leader"), "dot")
    tb.set(Q("pos"), str(TEXT_W))
    pPr.insert(0, tabs)
    p = etree.Element(Q("p"))
    p.append(pPr)

    def run(txt, tab=False):
        r = etree.SubElement(p, Q("r"))
        r.append(make_rPr(ttbf.F_BODY, 22))
        if tab:
            etree.SubElement(r, Q("tab"))
        else:
            t = etree.SubElement(r, Q("t"))
            t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
            t.text = txt

    run("%s %s／%s" % (num, title, author))
    run("", tab=True)
    run(str(page))
    return p


def toc_doc(pages):
    """pages: {num: 頁碼}；依議程順序輸出目錄。"""
    ps = [big("目 錄", 40, east=ttbf.F_HEAD, before=600, after=400)]
    last_ses = None
    for pp in PAPERS:
        if pp["ses"] != last_ses:
            ps.append(mk_para("h1", SESSIONS[pp["ses"]]))
            last_ses = pp["ses"]
        pg = "（稿件未到）" if pp["src"] is None else pages.get(pp["num"], "")
        ps.append(toc_line(pp["num"], pp["title"], pp["author"], pg))
    return write_doc(ps, os.path.join(BUILD, "00b_toc.docx"))


if __name__ == "__main__":
    print(titlepage())
    print(scholars())
    print(toc_placeholder())
    print(agenda())
    print(staffpage())
