# -*- coding: utf-8 -*-
"""把 build/ 的各篇合成一本論文集：分節、頁首、連續頁碼、目錄。"""
import os, sys, time
import win32com.client as win32
from papers import PAPERS, SESSIONS
import front

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
OUT = os.path.join(HERE, "out")

CONF = "第三屆臺灣藏傳佛教論壇—藏傳佛教現代化"
PW, PH = 544.3, 737.1
MT, MB, ML, MR, MH, MF = 72.0, 72.0, 70.9, 70.9, 42.6, 49.6

wdSectionBreakNextPage, wdSectionBreakOddPage = 2, 5
wdHeaderFooterPrimary, wdHeaderFooterEvenPages = 1, 3
wdAlignParagraphLeft, wdAlignParagraphCenter, wdAlignParagraphRight = 0, 1, 2
wdFieldPage = 33
wdActiveEndAdjustedPageNumber, wdNumberOfPagesInDocument = 1, 4
wdStory, wdFormatXMLDocument, wdExportFormatPDF = 6, 12, 17


def paper_files():
    """(標籤, 檔名, 是否論文) 依序回傳。"""
    seq = [("front", "00a_titlepage.docx", False),
           ("toc",   "00b_toc.docx",       False),
           ("agenda", "00c_agenda.docx",   False),
           ("scholars", "00d_scholars.docx", False)]
    for i, pp in enumerate(PAPERS, 1):
        seq.append((pp["num"], "%02d_%s.docx" % (i, pp["num"].replace(".", "-")), True))
    seq.append(("staff", "99_staff.docx", False))
    return seq


def set_header(sec, kind, text, align, first_body_sec):
    """頁首只放書眉，頁碼另置於頁尾正中（沿用第二屆體例）。"""
    hf = sec.Headers(kind)
    hf.LinkToPrevious = False
    rng = hf.Range
    rng.Delete()
    if not text:
        return
    rng.Text = text
    rng.ParagraphFormat.Alignment = align
    rng.ParagraphFormat.SpaceAfter = 0
    # 中文用華康中黑體，英文與數字用 Times New Roman
    rng.Font.NameFarEast = "華康中黑體"
    rng.Font.NameAscii = "Times New Roman"
    rng.Font.NameOther = "Times New Roman"
    rng.Font.Size = 9
    rng.Font.Color = 0x333333


def set_footer(sec, kind, numbered):
    """頁尾正中頁碼。"""
    hf = sec.Footers(kind)
    hf.LinkToPrevious = False
    rng = hf.Range
    rng.Delete()
    if not numbered:
        return
    rng.ParagraphFormat.Alignment = wdAlignParagraphCenter
    rng.ParagraphFormat.SpaceBefore = 0
    rng.ParagraphFormat.SpaceAfter = 0
    fld = rng.Fields.Add(Range=rng, Type=wdFieldPage)
    fld.ShowCodes = False
    hf.Range.Fields.Update()
    # 字型一定要等功能變數插完再設，否則頁碼會套回樣式字型（實測變 Calibri）。
    # 含功能變數的 Range 設 NameFarEast 會炸 OLE 0x800a16d4，只設 Name 並個別 try。
    for rr in (fld.Result, hf.Range):
        try:
            rr.Font.Name = "Times New Roman"
            rr.Font.Size = 10
        except Exception as e:
            print("  頁尾字型：%s" % e)


def build(pages=None):
    if pages is None:
        front.toc_placeholder()
    else:
        front.toc_doc(pages)

    app = win32.Dispatch("Word.Application")
    app.Visible = False
    app.DisplayAlerts = 0

    # 前次中斷可能留下同名文件開著，SaveAs2 會被 Word 擋下
    master = os.path.join(OUT, "第三屆臺灣藏傳佛教論壇會議論文集.docx")
    for d in list(app.Documents):
        try:
            if os.path.normcase(d.FullName) == os.path.normcase(master):
                d.Close(0)
        except Exception:
            pass

    doc = app.Documents.Add()
    sel = app.Selection

    seq = paper_files()
    sec_of = {}
    for i, (tag, fn, is_paper) in enumerate(seq):
        sel.EndKey(wdStory)
        if i:
            sel.InsertBreak(wdSectionBreakOddPage if is_paper
                            else wdSectionBreakNextPage)
        sel.InsertFile(FileName=os.path.join(BUILD, fn),
                       ConfirmConversions=False, Link=False, Attachment=False)
        sec_of[tag] = doc.Range(0, sel.End).Sections.Count

    # 版面
    for sec in doc.Sections:
        ps = sec.PageSetup
        ps.PageWidth, ps.PageHeight = PW, PH
        ps.TopMargin, ps.BottomMargin = MT, MB
        ps.LeftMargin, ps.RightMargin = ML, MR
        ps.HeaderDistance, ps.FooterDistance = MH, MF
        ps.OddAndEvenPagesHeaderFooter = True
        ps.DifferentFirstPageHeaderFooter = False

    # 頁首與頁碼
    first_body = sec_of[PAPERS[0]["num"]]
    title_of = {pp["num"]: pp["title"] for pp in PAPERS}
    for tag, fn, is_paper in seq:
        idx = sec_of[tag]
        sec = doc.Sections(idx)
        if is_paper:
            set_header(sec, wdHeaderFooterPrimary, title_of[tag],
                       wdAlignParagraphRight, first_body)
            set_header(sec, wdHeaderFooterEvenPages, CONF,
                       wdAlignParagraphLeft, first_body)
        else:
            set_header(sec, wdHeaderFooterPrimary, "", wdAlignParagraphRight, first_body)
            set_header(sec, wdHeaderFooterEvenPages, "", wdAlignParagraphLeft, first_body)
        set_footer(sec, wdHeaderFooterPrimary, is_paper)
        set_footer(sec, wdHeaderFooterEvenPages, is_paper)

    # 本文自 1 起連續編碼；前置頁不編碼
    for k in (wdHeaderFooterPrimary, wdHeaderFooterEvenPages):
        pn = doc.Sections(first_body).Footers(k).PageNumbers
        pn.RestartNumberingAtSection = True
        pn.StartingNumber = 1

    doc.Repaginate()
    got = {}
    for pp in PAPERS:
        s = doc.Sections(sec_of[pp["num"]]).Range.Start
        got[pp["num"]] = doc.Range(s, s).Information(wdActiveEndAdjustedPageNumber)
    total = doc.Range().Information(wdNumberOfPagesInDocument)

    os.makedirs(OUT, exist_ok=True)
    doc.SaveAs2(master, FileFormat=wdFormatXMLDocument)
    doc.Close(0)
    if app.Documents.Count == 0:      # 別關掉使用者自己開著的 Word
        app.Quit()
    return got, total, master


if __name__ == "__main__":
    pages, total, path = build()          # 第一趟：取頁碼
    print("第一趟 頁數=%d" % total)
    pages, total, path = build(pages)     # 第二趟：帶入真頁碼的目錄
    print("第二趟 頁數=%d" % total)
    for pp in PAPERS:
        print("  %-6s p.%-4s %s" % (pp["num"], pages[pp["num"]], pp["title"][:34]))
    print("→", path)
