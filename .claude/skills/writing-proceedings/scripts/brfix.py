# -*- coding: utf-8 -*-
"""換行整理：
   ① 段首／段尾的 w:br（多出來的空行）拿掉
   ② 段落中間連續兩個以上 w:br＝作者用 Shift+Enter 代替分段 → 真的拆成數段
   單一 w:br 不動（偈頌分句、圖說分行、篇名副題都靠它）。
   拆段時保留原有的 run 與其字型（藏文、拉丁字、註腳參照都在 run 裡）。"""
import copy, os, re, sys, zipfile
from lxml import etree
from ttbf import Q, para_text
sys.stdout.reconfigure(encoding="utf-8")


def tokens_of(p):
    """把段落攤平成 token 序列；遇到不是 w:r 的內容（hyperlink、sdt…）就放棄拆這段。"""
    toks = []
    SKIP = {Q("pPr"), Q("proofErr"), Q("bookmarkStart"), Q("bookmarkEnd"),
            Q("commentRangeStart"), Q("commentRangeEnd")}
    for el in p:
        tag = el.tag
        if tag in SKIP:            # 校對標記與書籤，拆段時直接略過
            continue
        if tag != Q("r"):          # hyperlink／sdt 等包了 run 的結構，不動這段
            return None
        rPr = el.find(Q("rPr"))
        for child in el:
            if child.tag == Q("rPr"):
                continue
            toks.append(("br" if child.tag == Q("br") else "node", rPr, child))
    return toks


def build_para(pPr, group):
    p = etree.Element(Q("p"))
    if pPr is not None:
        p.append(copy.deepcopy(pPr))
    cur_rPr, cur_run = object(), None
    for kind, rPr, node in group:
        if rPr is not cur_rPr or cur_run is None:
            cur_run = etree.SubElement(p, Q("r"))
            if rPr is not None:
                cur_run.append(copy.deepcopy(rPr))
            cur_rPr = rPr
        cur_run.append(copy.deepcopy(node))
    return p


def fix(body):
    n_edge = n_split = 0
    for p in list(body.findall(Q("p"))):
        toks = tokens_of(p)
        if toks is None or not any(k == "br" for k, _, _ in toks):
            continue
        # 段首／段尾的 br 去掉
        a, b = 0, len(toks)
        while a < b and toks[a][0] == "br":
            a += 1
        while b > a and toks[b - 1][0] == "br":
            b -= 1
        trimmed = (a != 0 or b != len(toks))
        toks = toks[a:b]
        # 連續 2 個以上 br → 分段
        groups, cur, run_br = [], [], 0
        for tk in toks:
            if tk[0] == "br":
                run_br += 1
                cur.append(tk)
                continue
            if run_br >= 2:
                while cur and cur[-1][0] == "br":
                    cur.pop()
                if cur:
                    groups.append(cur)
                cur = []
            run_br = 0
            cur.append(tk)
        while cur and cur[-1][0] == "br":
            cur.pop()
        if cur:
            groups.append(cur)
        if not groups:
            p.getparent().remove(p)
            n_edge += 1
            continue
        if len(groups) == 1 and not trimmed:
            continue
        pPr = p.find(Q("pPr"))
        for g in groups:
            p.addprevious(build_para(pPr, g))
        p.getparent().remove(p)
        if len(groups) > 1:
            n_split += len(groups) - 1
        else:
            n_edge += 1
    return n_edge, n_split


if __name__ == "__main__":
    for f in sorted(os.listdir("build")):
        if not re.match(r"^(0[1-9]|1[0-6])_", f):
            continue
        dst = os.path.join("build", f)
        z = zipfile.ZipFile(dst)
        parts = {k: z.read(k) for k in z.namelist()}
        z.close()
        root = etree.fromstring(parts["word/document.xml"])
        e, s = fix(root.find(Q("body")))
        if not (e or s):
            continue
        parts["word/document.xml"] = etree.tostring(
            root, xml_declaration=True, encoding="UTF-8", standalone=True)
        zo = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
        for k, d in parts.items():
            zo.writestr(k, d)
        zo.close()
        print("  %-14s 去掉多餘空行 %d 處，拆出 %d 段" % (f, e, s))
    print("done")
