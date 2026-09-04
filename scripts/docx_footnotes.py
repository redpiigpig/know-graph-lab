# -*- coding: utf-8 -*-
"""給 python-docx 補上「真的隨頁註腳」。

python-docx 1.2 沒有註腳 API，只能自己塞 word/footnotes.xml 這個 part 進去。
國史館體例要求「註腳號碼每頁接續，並採隨頁附註」——章節附註（endnote）或把註文
排在段落後面都不算，一定要 Word 認得的 footnote，才會排到當頁下緣、才會自動編號。

🚨 footnotes.xml 的前兩筆是分隔線本身（separator／continuationSeparator），
   不是使用者的註。Word 找不到它們時整份文件會被判成毀損，所以 id 0、1 固定留給
   它們，正文的註一律從 2 起算。

用法：
    fn = Footnotes(doc)
    fn.add(paragraph, "侯坤宏，《太虛時代》（臺北：政大出版社，2018年），頁12。")
    fn.save()          # 一定要在 doc.save() 之前呼叫
"""
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.opc.packuri import PackURI
from docx.opc.part import Part
from docx.oxml.ns import qn
from docx.shared import Pt

CT = ("application/vnd.openxmlformats-officedocument"
      ".wordprocessingml.footnotes+xml")
NS = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"')

# 分隔線那兩筆的固定內容
SEP = ('<w:footnote w:type="separator" w:id="0"><w:p><w:pPr><w:spacing w:after="0" '
       'w:line="240" w:lineRule="auto"/></w:pPr><w:r><w:separator/></w:r></w:p></w:footnote>'
       '<w:footnote w:type="continuationSeparator" w:id="1"><w:p><w:pPr>'
       '<w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr>'
       '<w:r><w:continuationSeparator/></w:r></w:p></w:footnote>')

EN_FONT, CJK_FONT = "Times New Roman", "新細明體"


def _esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


class Footnotes:
    def __init__(self, doc):
        self.doc = doc
        self.items = []          # [(id, 註文)]
        self._next = 2           # 0、1 留給分隔線

    def add(self, par, text, *, size=10):
        """在段落尾端插入註腳參照，回傳註號。"""
        fid = self._next
        self._next += 1
        self.items.append((fid, text))
        run = par.add_run()
        run.font.size = Pt(size)
        run.font.name = EN_FONT
        rpr = run._element.get_or_add_rPr()
        rpr.rFonts.set(qn("w:eastAsia"), CJK_FONT)
        # 沒有 FootnoteReference 樣式時，註號要自己設成上標，否則會排成一般數字
        va = rpr.makeelement(qn("w:vertAlign"), {qn("w:val"): "superscript"})
        rpr.append(va)
        ref = run._element.makeelement(qn("w:footnoteReference"), {qn("w:id"): str(fid)})
        run._element.append(ref)
        return fid

    def _xml(self):
        body = [SEP]
        for fid, text in self.items:
            body.append(
                f'<w:footnote w:id="{fid}"><w:p><w:pPr>'
                f'<w:spacing w:after="0" w:line="240" w:lineRule="auto"/>'
                f'<w:ind w:left="284" w:hanging="284"/></w:pPr>'
                f'<w:r><w:rPr><w:rFonts w:ascii="{EN_FONT}" w:hAnsi="{EN_FONT}" '
                f'w:eastAsia="{CJK_FONT}"/><w:sz w:val="20"/>'
                f'<w:vertAlign w:val="superscript"/></w:rPr><w:footnoteRef/></w:r>'
                f'<w:r><w:rPr><w:rFonts w:ascii="{EN_FONT}" w:hAnsi="{EN_FONT}" '
                f'w:eastAsia="{CJK_FONT}"/><w:sz w:val="20"/></w:rPr>'
                f'<w:t xml:space="preserve"> {_esc(text)}</w:t></w:r></w:p></w:footnote>')
        return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                f'<w:footnotes {NS}>{"".join(body)}</w:footnotes>').encode("utf-8")

    def save(self):
        if not self.items:
            return
        dp = self.doc.part
        part = Part(PackURI("/word/footnotes.xml"), CT, self._xml(), dp.package)
        dp.relate_to(part, RT.FOOTNOTES)
