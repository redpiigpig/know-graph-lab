"""產生〈從使徒到大公〉譜系歸屬表的論文體 markdown，供 build_paper_docx.mjs 轉 Word。

    python scripts/build_genealogy_appendix_md.py
    node scripts/build_paper_docx.mjs christian-genealogy-attribution "<out.docx>"

論述部分手寫於本檔（正式論文語氣，繁體，不用表情符號與條列速記）；
二十七卷的逐段表與典外文獻表由 data/christian-genealogy/ 各檔生成，
以免文件與資料層走鐘。
"""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data/christian-genealogy"
OUT = ROOT / "public/content/works/christian-genealogy-attribution-revision-draft.md"

tree = json.loads((D / "traditions.json").read_text(encoding="utf-8"))
defs = json.loads((D / "nt-book-defaults.json").read_text(encoding="utf-8"))["books"]
peri = json.loads((D / "nt-pericopes.json").read_text(encoding="utf-8"))["books"]
bib = json.loads((D / "bibliography.json").read_text(encoding="utf-8"))["entries"]
gospels = json.loads((D / "apocryphal-gospels.json").read_text(encoding="utf-8"))["documents"]
ntapoc = json.loads((D / "nt-apocrypha.json").read_text(encoding="utf-8"))["documents"]
gc = json.loads((D / "gnostic-corpus.json").read_text(encoding="utf-8"))

names = {}
def walk(arr):
    for n in arr:
        names[n["code"]] = n["name"]
        for s in n.get("sub", []) or []:
            names[s["code"]] = s["name"]
for k in ("layer1", "layer2", "layer3"):
    walk(tree[k])

segs = {f.stem: json.loads(f.read_text(encoding="utf-8")) for f in sorted((D / "segments").glob("*.json"))}

tally, total = Counter(), 0
for code, doc in segs.items():
    vs = {f"{s['from'][0]}:{s['from'][1]}-{s['to'][0]}:{s['to'][1]}": s["verses"] for s in peri[code]}
    for ref, seg in doc["segments"].items():
        v = vs[ref]
        total += v
        for src in seg["sources"]:
            tally[src] += v / len(seg["sources"])

L = []
W = L.append

W("# 〈從使徒到大公〉譜系歸屬表：編製說明與逐卷歸屬")
W("### 《基督宗教譜系學》第二章附錄")
W("")
W("---")
W("")

W("## 一、編製緣起")
W("")
W("本書第二章主張，基督宗教在耶穌事件之後的第一個世紀裡，並非由一個統一的使徒團"
  "體逐代傳遞一套完整的制度，而是由數條各自保存不同記憶、各有不同權威來源的軌跡"
  "彼此競爭、混合而成。此一主張若僅以論述方式提出，讀者無從查證；因此本附錄把該"
  "章的分類架構落實為一份可逐條覆核的歸屬表，使每一節新約經文與每一份一二世紀文"
  "獻，都能指出它所出自的群體，並說明作此判斷的依據。〔註1〕")
W("")
W("表的編製原則有三。其一，凡有學者支持的歸屬，列出該學者的著作；其二，凡出於本"
  "表自行判斷者，明白標示為判斷，並寫出足以讓他人據以反駁的推論鏈；其三，凡材料"
  "不足以判斷者，欄位留空，並在說明中交代留空的理由。三者之中，第三項最易被忽"
  "略，卻最能防止一份看似完整的表格以猜測填滿其空缺。")
W("")

W("## 二、四層代號")
W("")
W("歸屬表使用四層代號。第一層為復活事件以前的地方見證網絡，以小寫希臘字母標示；"
  "字母取自該群體在文獻中的關鍵語詞，而非流水編號。第二層為復活以後圍繞「誰有資"
  "格解釋耶穌」而重新結盟的具名使徒軌跡，以大寫拉丁字母標示，其後代沿用同一字母"
  "加序號，不另立異端專用代號。第三層為八個地理神學中心，即城市傳統。第四層為不"
  "上承任何使徒、而自有存世文獻的獨立分支，以 G 標示。")
W("")
W("| 代號 | 群體 | 字母出處 |")
W("|---|---|---|")
for n in tree["layer1"]:
    W(f"| {n['code']} | {n['name']} | {n.get('etymon','')} |")
W("")
W("第二層七條軌跡及其次群體如下。")
W("")
W("| 代號 | 軌跡 | 次群體 |")
W("|---|---|---|")
for n in tree["layer2"]:
    sub = "、".join(f"{s['code']} {s['name']}" for s in n.get("sub", []))
    W(f"| {n['code']} | {n['name']} | {sub} |")
W("")
W("第三層八個城市傳統，人物線列至尼西亞會議（三二五年）；其中迦太基是唯一不上承"
  "任何使徒軌跡的一座，它沒有使徒創始傳說，而以拉丁語、殉道者與法學式神學自行形"
  "成。〔註2〕第四層四個獨立分支為塞特派諾斯底、瓦倫廷派、赫密士文集與摩尼教。")
W("")

W("## 三、收錄與判斷規則")
W("")
W("### （一）立節點的條件")
W("")
W(f"本表立一節點的條件，是該群體須有存世的自產文獻；僅能自敵對者的引述回推者不"
  f"立。依此規則，馬吉安派、孟他努運動、巴西里底與尼哥拉一黨均不立節點。以巴西里"
  f"底為例，他確曾撰有《福音書》與《釋義》二十四卷，然全書已佚，現存僅亞歷山卓的"
  f"革利免《雜記》與希坡律陀所引之殘篇，故其殘篇歸入亞歷山大的諾斯底教師圈，而不"
  f"另立節點。〔註3〕")
W("")
W("### （二）來源欄所記者為口傳來源，非執筆者")
W("")
W("本表「來源」一欄所記，是該段材料的記憶由誰保存，而非由誰落筆成文。古代文本皆"
  "由識字者書寫，此一事實不分辨任何群體，故不進入來源欄。《羅馬書》十六章二十二"
  "節記有「我這代筆寫信的德丟，在主裡問你們安」，該書在本表仍歸保羅本人，不因有"
  "代筆者而改歸德丟；同理，十二使徒的口傳由他人筆錄，仍歸彼得軌跡。")
W("")
W("### （三）掛名與實際歸屬分欄")
W("")
W("典外文獻多有託名之作。本表將「掛名」與「實際歸屬」分為兩欄，二者可以完全不重"
  "疊。《腓力福音》掛腓力之名而內容為瓦倫廷派的聖禮神學，與《使徒行傳》第八章那"
  "位腓力並無關聯。分欄的用意在於：託名這件事本身即是譜系資料，它顯示二世紀有人"
  "認為掛上某一使徒的名字有用，而選擇託名的對象，往往不是關係最近者，而是權威最"
  "高且在正典中留白最多者。")
W("")

W("## 四、資料處理")
W("")
W(f"節次骨架取自本站經文資料，而非希臘文校訂本。校訂本略去二十六節存疑經文，其中"
  f"《約翰福音》七章五十三節至八章十一節（行淫時被拿的婦人）整段不在；而該段正是"
  f"譜系上最需要有歸屬列可掛的一種材料——一段在各抄本間漂浮、擺放位置不定的傳"
  f"統。全新約計 {total:,} 節。")
W("")
W(f"段落界線取自《古代基督信仰聖經註釋叢書》各段之總論，共 "
  f"{sum(len(v) for v in peri.values()):,} 段，逐節落段率為百分之百。採用既有出版分"
  f"段而不自行切分，理由在於界線須可覆核；自行切分七百餘段，無人能驗證其是否恰"
  f"當。〔註4〕")
W("")
W("一二世紀文獻母體取自《基督教大藏經》古代卷，以西元一至二百年為窗口，正藏、外"
  "藏相關者及經藏中非二十七卷的五卷合計，去重後為九十四種。")
W("")

W("## 五、逐節來源分佈")
W("")
W("下表為全新約逐節歸屬後的來源分佈。一段而有數個來源者，按等分攤計。")
W("")
W("| 代號 | 群體 | 節數 | 占比 |")
W("|---|---|---|---|")
for c, v in tally.most_common():
    W(f"| {c} | {names.get(c,'')} | {v:.1f} | {v/total*100:.1f}％ |")
W("")
W("此一分佈本身即構成本書核心主張的一項證據。保羅一系合計約占三成五，而保羅並未"
  "跟隨過地上的耶穌；其權威來自復活顯現、外邦宣教與親手建立的城市教會，而非師"
  "承。復活事件之後，判斷「一支」的依據已由「跟過誰」轉為「保存誰的記憶、經誰傳"
  "下」，此即本書所謂「每一次事件之後，譜系單位即更換一次」。相對地，第一層六個"
  "地方群體合計不足百分之八，然其所保存者為全部敘事中最關鍵的幾處：埋葬的地點、"
  "空墳、議會內部的審議，以及最後晚餐的那間樓房。")
W("")

W("## 六、逐卷歸屬")
W("")
W("以下依正典次序逐卷列出。每卷先述其編成群體、年代與寫作地，次列判斷依據，末附"
  "逐段來源表。凡與《基督教大藏經》所記傳統年代分歧者，另出其說以資對照。")
W("")
ORDER = "mat mrk luk jhn act rom 1co 2co gal eph php col 1th 2th 1ti 2ti tit phm heb jas 1pe 2pe 1jn 2jn 3jn jud rev".split()
CN = "一二三四五六七八九十"
for i, code in enumerate(ORDER, 1):
    b = defs[code]
    doc = segs[code]
    nseg = len(doc["segments"])
    nv = sum(s["verses"] for s in peri[code])
    W(f"### （{i}）{b['name']}")
    W("")
    line = (f"本卷編成群體為{b['editor_name']}（{b['editor']}），成書年代{b['date']}，"
            f"寫作地為{b['place']}，全卷 {nv} 節、分 {nseg} 段。")
    if b.get("dating_divergence"):
        line += (f"《基督教大藏經》另記其年代為{b['date_traditional']}、寫作地為"
                 f"{b['place_traditional']}，與本表分歧。")
    W(line)
    W("")
    sup = "、".join(b["support"])
    W(f"歸屬依據：{sup}。" + ("本卷之歸屬屬本表判斷，非既有定論。" if b["own_judgment"] else ""))
    W("")
    rat = b["rationale"].replace("🚨 ", "").replace("⚠️ ", "").replace("**", "")
    W(rat)
    W("")
    if doc["meta"].get("layers"):
        W(doc["meta"]["layers"].replace("／", "、"))
        W("")
    W("| 節 | 主題 | 來源 |")
    W("|---|---|---|")
    for ref, seg in doc["segments"].items():
        src = "、".join(seg["sources"])
        title = seg["title"].replace("|", "｜")
        W(f"| {ref} | {title} | {src} |")
    W("")

W("## 七、典外文獻歸屬")
W("")
W(f"典外文獻部分計六十六種，其中福音書三十種、非福音三十六種。分類同時並列三套學"
  f"界體例：Ehrman 與 Pleše 依耶穌生平階段分類，Hennecke–Schneemelcher《新約次經》"
  f"採形式史十類，Markschies 與 Schröter 二〇一二年新版則改依正典本身的三大文類重"
  f"編。〔註5〕")
W("")
W("| 文獻 | 年代 | 寫作地 | 掛名 | 實際歸屬 |")
W("|---|---|---|---|---|")
allap = [(k, v, "福音書") for k, v in gospels.items()] + [(k, v, "非福音") for k, v in ntapoc.items()]
allap.sort(key=lambda x: (x[1]["date"][0], x[1]["date"][1]))
for k, v, grp in allap:
    at = "、".join(v.get("attributed", [])) or "—"
    ac = "、".join(v.get("actual", [])) or "無傳承"
    pk = {"findspot": "（僅知出土地）", "claimed": "（文獻自稱）", "scattered": ""}.get(v.get("place_kind"), "")
    W(f"| {v['title']} | {v['date'][0]}–{v['date'][1]} | {v.get('place','')}{pk} | {at} | {ac} |")
W("")
W("紙草殘片一律標示為「僅知出土地」而非寫作地。此類文獻悉數出土於埃及，原因在於"
  "埃及乾燥的氣候使紙草得以保存，而非其皆撰於埃及；二者若混為一談，將得出「早期"
  "基督教文獻多產自埃及」此一與事實不符的結論。")
W("")
W("諾斯底文庫二百八十七種，其中逐份歸屬五十種，依類別規則處理一百七十五種，指回"
  "典外檔二十種，另有四十二種經查證並非古代文本而予排除。該四十二種為現代介紹文"
  "與網頁導覽，其首節內容為網站的麵包屑導覽列，不可作為史料。")
W("")

W("## 八、檢驗、限制與已知缺口")
W("")
W("### （一）自動檢驗")
W("")
W("本表附三支檢驗工具，每支均列印分母：其一核對文獻母體與逐筆歸屬及代號主檔；其"
  "二核對段落骨架、逐段歸屬與書卷層；其三核對典外文獻各欄位與書目引用。三者現均"
  "通過。列印分母之要求，源於本專案數次「稽核回報零筆而實為查詢本身失效」的教"
  "訓。")
W("")
W("### （二）方法上的限制")
W("")
W("第一，樣本過小者不計算密度。《約翰福音》二十一章二十四至二十五節僅四十三字，"
  "任何每千詞密度在此皆無意義（一次出現即為千分之二十三）；可用者為計數型證據，"
  "即某詞在整個對照語料中出現零次，此種證據不受樣本大小影響。本表判定該章與約翰"
  "書信非出同一批材料，所據即為：該章有二十六個詞為《約翰福音》一至二十章所無，"
  "而此二十六詞在三封書信中出現零次。")
W("")
W("第二，Q 典群體之性質，本表定為「本地的巡迴傳道人，被驅趕之後回頭詛咒本地」，"
  "從 Theissen 之巡迴激進主義說。〔註6〕Arnal 主張其編寫者為定居之村落書記，本表"
  "未從，理由在於其論據為「撰寫此種希臘文需具書記訓練」，而此一條件對古代任何一"
  "份希臘文文本均成立，不足以分辨 Q 與其他文本。本表另作一項檢驗：Q 中行路語彙的"
  "十六個命令句幾乎全數集中於差遣指令，係對自己人所下之指令；書記語彙的十六個直"
  "說句則散見於比喻與禍哉之中，係論及他人的世界；而「文士」一詞在 Q 中出現零"
  "次。")
W("")
W("第三，凡本表自行判斷者均已標示。二十七卷中有六卷屬此，合計二千八百餘節，約占"
  "全新約三成五。")
W("")
W("### （三）已知缺口")
W("")
W("《猶大福音》之全文不見於《基督教典外文獻》。該書第二冊僅有一頁簡介，末句明言"
  "「這書的文本已經失傳」，緣其出版早於二〇〇六年查科抄本公布。本表另據 gospels.net "
  "所刊之公有領域英譯（依查科抄本第三卷）收入，並自譯繁體中文；該中譯係轉譯自英"
  "譯本而非科普特原文，引用時應予註明。")
W("")
W("《阿拉伯語耶穌嬰孩時期福音》與《拉丁語耶穌嬰孩時期福音》二篇，原書頁碼分別為"
  "第一冊一一〇至一三二頁與一五〇至一五四頁，現有掃描檔雖具文字層，然該層本身即"
  "為品質不堪使用之舊有光學辨識結果，須重新辨識後方能收入。")
W("")
W("譯名方面另有二十七筆待定。凡本站譯名詞庫未收者，本表留空而不自創譯名，其中包"
  "括亞流、安提阿的路迦努、以弗所的波利克拉底、安提阿的塞拉皮翁與珀佩圖亞等。")
W("")

W("## 註釋")
W("")
W("1. 本附錄之分類架構見本書第二章各節。相關方法論討論參 James D. G. Dunn, "
  "*Unity and Diversity in the New Testament*, 3rd ed. (London: SCM Press, 2006)；"
  "Wayne A. Meeks, “Social and Ecclesial Life of the Earliest Christians,” in "
  "*The Cambridge History of Christianity*, Vol. 1 (Cambridge: Cambridge University Press, 2006), 145–173.")
W("2. 迦太基一線之發展參 Geoffrey D. Dunn, *Tertullian* (London: Routledge, 2004)；"
  "J. Patout Burns, *Cyprian the Bishop* (London: Routledge, 2002).")
W("3. 巴西里底殘篇之保存情形參 M. David Litwa, *Early Christianity in Alexandria: "
  "From Its Beginnings to the Late Second Century* (Cambridge: Cambridge University Press, 2023).")
W("4. 分段依據為 accs_commentary 資料表中 section_kind 為 overview 之各列，"
  "即《古代基督信仰聖經註釋叢書》各段之總論。該叢書之段落總論為巢狀結構，"
  "章級總論之下另有小段總論；若逐段相加而不處理其重疊，將得出超過百分之百的覆蓋"
  "率，本表以「每節指派予包含它的最短範圍」處理之。")
W("5. Bart D. Ehrman and Zlatko Pleše, *The Apocryphal Gospels: Texts and Translations* "
  "(Oxford: Oxford University Press, 2011)；Wilhelm Schneemelcher, ed., "
  "*New Testament Apocrypha*, Vol. 1, rev. ed., trans. R. McL. Wilson "
  "(Louisville: Westminster John Knox, 1991)；Christoph Markschies and Jens Schröter, eds., "
  "*Antike christliche Apokryphen in deutscher Übersetzung*, I: *Evangelien und Verwandtes*, "
  "7. Aufl. (Tübingen: Mohr Siebeck, 2012).")
W("6. Gerd Theissen, *Soziologie der Jesusbewegung* (München: Kaiser, 1977)；"
  "英譯 *The Sociology of Early Palestinian Christianity*, trans. John Bowden "
  "(Philadelphia: Fortress, 1978)。反對意見見 William E. Arnal, *Jesus and the Village "
  "Scribes: Galilean Conflicts and the Setting of Q* (Minneapolis: Fortress, 2001).")
W("")

W("## 參考書目")
W("")
art = [(k, v) for k, v in bib.items() if v["provenance"] == "article-footnote"]
add = [(k, v) for k, v in bib.items() if v["provenance"] != "article-footnote"]
W("本表所據書目共 %d 種，其中 %d 種出自本章註釋，%d 種為編製本表時另補。"
  % (len(bib), len(art), len(add)))
W("")
for k, v in sorted(bib.items()):
    W(v["ref"])
W("")

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
txt = OUT.read_text(encoding="utf-8")
print(f"寫出 → {OUT.relative_to(ROOT)}")
print(f"  {len(txt):,} 字元、{len(L):,} 行")
print(f"  二十七卷逐段表共 {sum(len(v['segments']) for v in segs.values()):,} 列")
print(f"  典外文獻表 {len(allap)} 列、書目 {len(bib)} 種")
