# -*- coding: utf-8 -*-
"""把人工審定結果編成 adjudication JSON（給 dazangjing_proposal.py 套用）。

判定鍵 = (source, title_zh, eraKey, collectionKey)。三組同鍵重出（比利時信條／
西敏準則／徐光啟集）本來就同判定，共用一筆即可。
"""
import json, sys
from pathlib import Path
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# verdict: drop_dup_existing / drop_person_or_folder / drop_anthology / drop_secondary / keep
# dup_of : 既有大藏經條目（時代/正外/藏 標在前）
# alias  : 要補進翻譯詞庫 theological_terms（entity_type 為 work）的同書異名組
V = []
# 撰寫時用簡稱，寫檔時展開成 ledger 裡 source_record.source 的實際值
SRC = {"trc": "trc", "zlz": "ziliaozhan"}

def d(src, title, era, coll, verdict, reason, dup_of=None, alias=None, patch=None):
    V.append(dict(source=SRC[src], title_zh=title, eraKey=era, collectionKey=coll,
                  verdict=verdict, reason=reason, dup_of=dup_of, alias=alias, patch=patch))

P = "drop_person_or_folder"; DE = "drop_dup_existing"
DA = "drop_anthology"; DS = "drop_secondary"; K = "keep"

# ─────────────── 古代 ───────────────
d("trc","希波的奧古斯丁","ancient","lun",P,"TRC 作者資料夾層，不是作品")
d("trc","殉教者遊斯丁","ancient","lun",P,"TRC 作者資料夾層；且譯名應依詞庫作「猶斯定」")
d("trc","羅馬的革利免","ancient","lun",P,"TRC 作者資料夾層")
d("trc","里昂的愛任紐","ancient","lun",P,"TRC 作者資料夾層")
d("trc","該撒利亞的優西比烏","ancient","shizhuan",P,"TRC 作者資料夾層")

d("trc","上帝之城","ancient","lun",DE,"已在藏","[古代/正/論] 上帝之城｜奧古斯丁")
d("zlz","傳道員指南","ancient","lun",DE,"同書異名，已在藏","[古代/正/論] 信望愛手冊｜希波的奧古斯丁",
  ["信望愛手冊","傳道員指南","論信望愛"])
d("trc","創世六日","ancient","lun",DE,"同書異名，已在藏","[古代/正/論] 六日創造講疏｜大巴西略",
  ["六日創造講疏","創世六日","六日創造解"])
d("trc","懺悔錄","ancient","lun",DE,"已在藏","[古代/正/史傳] 懺悔錄｜奧古斯丁")
d("zlz","懺悔錄","ancient","shiwen",DE,"已在藏","[古代/正/史傳] 懺悔錄｜奧古斯丁")
d("trc","聖奧思定主教聖詠釋義","ancient","lun",DE,"同書異名，已在藏","[古代/正/論] 詩篇詮釋｜希波的奧古斯丁",
  ["詩篇詮釋","聖奧思定主教聖詠釋義","詩篇註解"])
d("trc","聖靈論","ancient","lun",DE,"同書異名，已在藏","[古代/正/論] 論聖靈｜大巴西略",
  ["論聖靈","聖靈論"])
d("trc","論三位一體","ancient","lun",DE,"同書異名，已在藏（另有希拉流同名書，勿混）","[古代/正/論] 三位一體論｜奧古斯丁",
  ["三位一體論","論三位一體"])
d("trc","論信望愛","ancient","lun",DE,"同書異名，已在藏","[古代/正/論] 信望愛手冊｜希波的奧古斯丁")
d("zlz","論信望愛","ancient","lun",DE,"同書異名，已在藏","[古代/正/論] 信望愛手冊｜希波的奧古斯丁")
d("trc","論教師","ancient","lun",DE,"已在藏","[古代/正/論] 論教師｜希波的奧古斯丁")
d("zlz","論責任","ancient","lun",DE,"同書異名，已在藏","[古代/正/論] 論教牧職分｜安波羅修",
  ["論教牧職分","論責任"])
d("trc","論靈魂及其起源","ancient","lun",DE,"已在藏（既有作「源起」，建議正名為「起源」）","[古代/正/論] 論靈魂及其源起｜希波的奧古斯丁")
d("zlz","護教篇","ancient","lun",DE,"同書異名，已在藏","[古代/正/論] 特土良護教辯｜特土良",
  ["特土良護教辯","護教篇"])
d("zlz","駁塞爾修斯","ancient","lun",DE,"已在藏（既有重出兩筆，見稽核報告）","[古代/正/論] 駁塞爾修斯｜俄利根")
d("trc","沙漠教父言行錄","ancient","shiwen",DE,"同書異名，已在藏","[古代/正/宣道] 沙漠父老語錄｜沙漠教父",
  ["沙漠父老語錄","沙漠教父言行錄"])
d("zlz","沙漠教父言行錄","ancient","shiwen",DE,"同書異名，已在藏","[古代/正/宣道] 沙漠父老語錄｜沙漠教父")
d("zlz","牧靈指南","ancient","shiwen",DE,"同書異名，已在藏","[古代/正/論] 司牧守則｜大額我略",
  ["司牧守則","牧靈指南","教牧規則"])
d("zlz","神學演講錄","ancient","shiwen",DE,"同書異名，已在藏","[古代/正/論] 五篇神學講辭｜拿先斯的格列高理",
  ["五篇神學講辭","神學演講錄","神學講演錄"])
d("trc","神學講演錄","ancient","shiwen",DE,"同書異名，已在藏","[古代/正/論] 五篇神學講辭｜拿先斯的格列高理")
d("trc","聖奧思定主教講道詞","ancient","shiwen",DE,"同書異名，已在藏","[古代/正/宣道] 大眾講章集｜奧古斯丁",
  ["大眾講章集","聖奧思定主教講道詞"])
d("trc","聖安東尼傳","ancient","shiwen",DE,"已在藏","[古代/正/史傳] 安東尼傳｜亞他那修")
d("zlz","論四福音和諧","ancient","shiwen",DE,"同書異名，已在藏","[古代/正/遺教] 論福音書的和諧｜希波的奧古斯丁",
  ["論福音書的和諧","論四福音和諧"])
d("trc","金口若望：雕像講道詞選集","ancient","shiwen",DE,"同書異名，已在藏","[古代/正/宣道] 雕像講道｜金口若望",
  ["雕像講道","雕像講道詞選集"])
d("zlz","教會史","ancient","shizhuan",DE,"已在藏","[古代/正/史傳] 教會史｜優西比烏")
d("zlz","勸勉希臘人","ancient","xuandao",DE,"同書異名，已在藏","[古代/正/論] 亞歷山卓的克勉勸希臘人歸主辭｜亞歷山卓的克勉",
  ["勸希臘人歸主辭","勸勉希臘人"])
d("zlz","護教篇","ancient","xuandao",DE,"同書異名，已在藏；譯名依詞庫作「猶斯定」","[古代/正/論] 猶斯定第一護教詞・第二護教詞｜猶斯定",
  ["護教詞","護教篇"])

d("zlz","使徒教父著作","ancient","shiwen",DA,"三聯書店譯本合集；所收各篇（克勉書、伊格那丟書信、波利甲…）已分別在藏")
d("zlz","論基督教信仰；論聖靈；論復活；論奧秘；論悔改","ancient","lun",DA,
  "三聯書店安波羅修五篇合集；論信德致格拉提安皇帝、論懺悔、論奧祕均已在藏")
d("zlz","論自由意志；論本性與恩典","ancient","lun",DA,
  "譯本合集；論自由意志、駁伯拉糾論本性與恩典均已在藏")

d("trc","獨語錄","ancient","lun",K,"未在藏，奧古斯丁早期對話錄",None,None,
  {"title_orig":"Soliloquia","author":"希波的奧古斯丁","era":"約 386–387 年"})
d("trc","駁朱利安","ancient","lun",K,"未在藏，駁伊克拉農的儒略（伯拉糾派）之作",None,None,
  {"title_orig":"Contra Julianum","author":"希波的奧古斯丁","era":"約 421 年"})

# ─────────────── 中世紀 ───────────────
d("trc","哲學大全 Summa contra Gentiles 駁異大全","medieval","lun",DE,
  "書名欄是 TRC 資料夾名殘留；與《駁異大全》同書，且已在藏","[中世紀/正/論] 哲學大全（駁異教大全）｜托馬斯‧阿奎那",
  ["哲學大全","駁異大全","駁異教大全"])
d("zlz","駁異大全","medieval","lun",DE,"同書異名，已在藏（既有於論藏、宣道藏重出兩筆）","[中世紀/正/論] 哲學大全（駁異教大全）｜托馬斯‧阿奎那")
d("trc","師主篇","medieval","lun",DE,"同書異名，已在藏","[中世紀/正/論] 效法基督｜托馬斯‧厄‧肯培",
  ["效法基督","師主篇","輕世金書","遵主聖範"])
d("zlz","輕世金書","medieval","xuandao",DE,
  "與《師主篇》同書（De Imitatione Christi），已在藏；原提案作者欄有誤——原著為托馬斯‧厄‧肯培，"
  "陽瑪諾（Manuel Dias Jr.）是明末漢譯者，與利瑪竇圈、Gerhard of Zutphen 均無關",
  "[中世紀/正/論] 效法基督｜托馬斯‧厄‧肯培")
d("zlz","維護神聖靜修者三論集","medieval","lun",DE,"同書異名，已在藏","[中世紀/正/論] 為神聖靜修者辯護（三聯論）｜額我略‧帕拉瑪斯",
  ["為神聖靜修者辯護","維護神聖靜修者三論集","三聯論"])
d("zlz","聖女加大利納對話錄","medieval","lun",DE,"同書異名，已在藏","[中世紀/正/論] 對話錄（天主上智之書）｜錫耶納的加大利納",
  ["對話錄（天主上智之書）","聖女加大利納對話錄"])
d("zlz","法蘭克人史","medieval","shizhuan",DE,"同書異名，已在藏","[古代/正/史傳] 法蘭克人歷史｜都爾的格列高利",
  ["法蘭克人歷史","法蘭克人史"])
d("zlz","安瑟倫著作選","medieval","lun",DA,"宗教文化出版社選集；所收《上帝何以化身為人》《獨白篇》《論道篇》均已在藏")
d("zlz","神對他無所隱藏的人（艾克哈靈修著作選譯）","medieval","xuandao",DA,"光啟選譯本，非單一原典")
d("zlz","論隱秘的上帝","early-modern","lun",DA,
  "三聯譯叢庫薩文集（含論隱祕的上帝、論尋找上帝、論有學識的無知等）；"
  "原提案 title_orig 誤植 De Docta Ignorantia，該篇已在藏。缺口：De Deo abscondito 單篇尚未入藏")

d("zlz","宇宙間的靈智實體問題","medieval","lun",K,"未在藏（既有僅《論真理》辯論問題集）",None,None,
  {"author":"托馬斯‧阿奎那","era":"約 1267–1268 年"})
d("trc","安瑟倫論自由","medieval","lun",K,"未在藏（既有安瑟莫四種不含此篇）",None,None,
  {"title_orig":"De libertate arbitrii","author":"坎特伯里的安瑟莫","era":"約 1080–1086 年"})
d("zlz","盎格魯-撒克遜編年史","medieval","shizhuan",K,"未在藏",None,None,
  {"author":"佚名（多所修道院遞修）","era":"9–12 世紀"})

# ─────────────── 近代：信條與教理問答 ───────────────
d("trc","1560 蘇格蘭人信條","early-modern","lun",DE,"已在藏","[近代/正/律] 蘇格蘭信條｜諾克斯等六人")
d("trc","1619 多特信條","early-modern","lun",DE,"同書異名，已在藏","[近代/正/律] 多特信經｜多特會議",
  ["多特信經","多特信條","多特法典"])
d("trc","多特信條","early-modern","lun",DE,"同上","[近代/正/律] 多特信經｜多特會議")
d("trc","1646 西敏信綱","early-modern","lun",DE,"同書異名，已在藏","[近代/正/律] 西敏信條｜西敏會議",
  ["西敏信條","西敏信綱"])
d("trc","王瑞珍新譯西敏信條","early-modern","lun",DE,"同一信條的另一中譯本，非新作品","[近代/正/律] 西敏信條｜西敏會議")
d("trc","1647 西敏大問答","early-modern","lun",DE,"已在藏","[近代/正/律] 西敏大小要理問答｜西敏會議")
d("trc","1658 薩伏伊宣言","early-modern","lun",DE,"已在藏","[近代/正/律] 薩伏依宣言｜英格蘭公理會諸教會")
d("trc","比利時信條","early-modern","lun",DE,"已在藏（兩筆同判）","[近代/正/律] 比利時信條｜德布雷")
d("trc","第二瑞士信條","early-modern","lun",DE,"已在藏","[近代/正/律] 第二瑞士信條｜布林格")
d("trc","多特教會法規","early-modern","lun",DE,"同書異名，已在藏","[近代/正/律] 多特教會條例｜多特總會",
  ["多特教會條例","多特教會法規"])
d("zlz","脫利騰公議會教理問答","early-modern","lun",DE,"同書異名，已在藏","[近代/正/論] 羅馬要理問答｜特倫多會議奉命編纂",
  ["羅馬要理問答","脫利騰公議會教理問答","特倫多公議會教理問答"])
d("zlz","特倫多公議會教理問答","early-modern","xuandao",DE,"同上","[近代/正/論] 羅馬要理問答｜特倫多會議奉命編纂")
d("trc","1629 東方正教信仰告白","early-modern","xuandao",DE,"同書異名，已在藏","[近代/正/律] 盧卡里斯東方信仰宣認｜盧卡里斯",
  ["盧卡里斯東方信仰宣認","東方正教信仰告白"])
d("trc","1644 公眾敬拜指南","early-modern","liyi",DE,"同書異名，已在藏","[近代/正/禮儀] 公眾崇拜指南｜西敏會議",
  ["公眾崇拜指南","公眾敬拜指南"])
d("trc","神操","early-modern","lun",DE,"已在藏（既有那筆時代誤標現代，應為近代）","[現代/正/禮儀] 神操｜依納爵‧羅耀拉")
d("trc","簡易祈禱法","early-modern","lun",DE,"已在藏","[近代/正/禮儀] 簡易祈禱法｜蓋恩夫人")
d("zlz","不得已 附二種","early-modern","lun",DE,"已在藏，且楊光先為反教者應歸外藏","[近代/外/論] 不得已｜楊光先")
d("zlz","聖朝破邪集","early-modern","shizhuan",DE,"已在藏，且應歸外藏","[近代/外/論] 聖朝破邪集｜徐昌治 輯")

d("trc","1619 三項聯合信綱","early-modern","lun",DA,"三份信條（比利時／海德堡／多特）的合稱，三份均已在藏")
d("trc","三項聯合信綱","early-modern","lun",DA,"同上")
d("trc","西敏準則","early-modern","lun",DA,"西敏信條＋大小要理問答＋治理形式＋崇拜指南的合稱，各份均已在藏（兩筆同判）")
d("trc","歷代基督教信條","early-modern","lun",DA,"趙中輝譯信條選集，非單一作品")
d("trc","信綱及教理問答","modern","lun",P,"TRC 頂層分類資料夾名，不是作品")
d("trc","兒童簡明要理問答","modern","lun",DS,"西敏小要理問答的現代兒童簡化改編，屬次級教材")

d("trc","1559 高盧信綱","early-modern","lun",DE,
  "同書異名，已在藏——藏內作《法國信條》。首輪人工審定誤判為「未在藏」，"
  "是自動全藏比對抓回來的：查了高盧／Gallicana／法蘭西信條卻沒查「法國信條」",
  "[近代/正/律] 法國信條｜法國改革宗教會首屆全國總會（加爾文草稿）",
  ["法國信條","高盧信綱","拉羅歇爾信條"])
d("trc","海德堡要理問答註釋__扎哈利亞斯·烏爾西努博士","early-modern","lun",K,
  "未在藏；烏爾西努正是該要理問答執筆者，非後世次級註釋",None,None,
  {"title_zh":"海德堡要理問答註釋","author":"匝加利亞‧烏爾西努斯（Zacharias Ursinus）","era":"1584 年"})
d("trc","基督教信仰告白","unknown","lun",K,"未在藏；係貝扎 1558 年信仰告白",None,None,
  {"eraKey":"early-modern","title_orig":"Confessio Christianae fidei","author":"泰奧多爾‧德‧貝扎（Théodore de Bèze）","era":"1558 年"})
d("trc","聖言小學的開端","early-modern","lun",K,"未在藏，荷蘭改革宗要理教本",None,None,
  {"author":"亞伯拉罕‧海倫布魯克（Abraham Hellenbroek）","era":"1706 年"})

# ─────────────── 近代：漢語天主教文獻（本輪最有價值的一批） ───────────────
d("zlz","天學初函","early-modern","leishu",K,"未在藏，明末耶穌會漢文著述總集",None,None,
  {"author":"李之藻 輯","era":"1628 年（崇禎元年）","extent":"理編十種‧器編十種，共二十種"})
d("zlz","天主實義","early-modern","lun",K,"未在藏；明末天主教漢語神學奠基之作",None,None,
  {"author":"利瑪竇（Matteo Ricci）","era":"1603 年"})
d("zlz","天主降生引義","early-modern","lun",K,"未在藏",None,None,
  {"author":"艾儒略（Giulio Aleni）","era":"1635 年"})
d("zlz","七克真訓","early-modern","xuandao",K,"未在藏（七克真訓為清刻本題名，正名作《七克》）",None,None,
  {"title_zh":"七克","title_orig":"","author":"龐迪我（Diego de Pantoja）","era":"1614 年"})
d("zlz","新法表異","early-modern","xuandao",K,"未在藏",None,None,
  {"title_orig":"","author":"湯若望（Johann Adam Schall von Bell）","era":"明末（17 世紀）"})
d("zlz","救靈箴言","early-modern","xuandao",K,"未在藏",None,None,{"title_orig":"","author":"李杖（問漁）","era":"1890 年"})
d("zlz","中國年報 1606-1607年","early-modern","shizhuan",K,"未在藏，在華耶穌會年信",None,None,
  {"author":"在華耶穌會士（年信編者）","era":"1606–1607 年"})
d("zlz","安德烈·李神父日記 1746-1748年","early-modern","shizhuan",K,"未在藏；首位華籍司鐸的拉丁文日記",None,None,
  {"title_zh":"李安德日記（1746–1748）","author":"李安德（André Ly）","era":"1746–1748 年","language":"拉丁文"})
d("zlz","徐光啟集","early-modern","shuxin",K,"未在藏（既有僅《辨學章疏》單篇）；兩筆合併為一",None,None,
  {"title_orig":"","author":"徐光啟","era":"明末（1562–1633）"})
d("zlz","萊布尼茨與克拉克論戰書信集","early-modern","shuxin",K,"未在藏",None,None,
  {"author":"萊布尼茲；塞繆爾‧克拉克","era":"1715–1716 年"})
d("zlz","基督的憂傷","early-modern","shiwen",K,"未在藏（既有莫爾的《患難慰藉對話錄》《獄中書信》不含此篇）",None,None,
  {"author":"托馬斯‧莫爾","era":"1534–1535 年（獄中）"})
d("zlz","光與愛的話語","early-modern","shiwen",K,"未在藏",None,None,
  {"title_orig":"Dichos de luz y amor","author":"十字若望","era":"16 世紀"})
d("zlz","靈歌","early-modern","shiwen",K,"未在藏",None,None,
  {"title_orig":"Cántico espiritual","author":"十字若望","era":"1578–1586 年"})
d("zlz","登上嘉默羅山","early-modern","xuandao",K,"未在藏",None,None,
  {"title_orig":"Subida del Monte Carmelo","author":"十字若望","era":"約 1578–1585 年"})
d("trc","聖依納爵自述小傳心靈日記","early-modern","shiwen",K,"未在藏",None,None,
  {"title_orig":"Autobiografía; Diario espiritual","author":"依納爵‧羅耀拉","era":"1553–1555 年（自述）；1544–1545 年（日記）"})
d("zlz","聖女耶穌大德蘭自傳","early-modern","shizhuan",K,"未在藏（既有僅書信集與詩）",None,None,
  {"title_orig":"Libro de la vida","author":"亞維拉的德蘭","era":"1562–1565 年"})
d("zlz","真誠孝愛聖母","early-modern","xuandao",K,"未在藏",None,None,
  {"title_orig":"Traité de la vraie dévotion à la Sainte Vierge","author":"蒙福的路易‧瑪利（Louis-Marie Grignion de Montfort）","era":"約 1712 年"})
d("zlz","父，隨你安排","early-modern","xuandao",K,"未在藏",None,None,
  {"title_orig":"L'Abandon à la Providence divine","author":"高薩德（Jean-Pierre de Caussade）","era":"18 世紀"})
d("trc","聖依納爵特輯","early-modern","shuxin",DS,"來源為不明編選之「特輯」，非單一原典；依納爵書信集與會憲已在藏")
d("zlz","謝國楨編：稗說、出劫記略、利瑪竇日記","early-modern","shizhuan",DA,
  "1982 年三種明清史料合刊；利瑪竇日記部分已由既有《基督教遠征中國史》涵蓋")

# 時代標錯：清末民初的材料被誤放進「近代」
d("zlz","庚子教會華人流血史","early-modern","shizhuan",K,"未在藏；時代改標現代（庚子＝1900）",None,None,
  {"eraKey":"modern","title_orig":"","era":"1900 年庚子教難紀事"})
d("zlz","教務紀略","early-modern","shizhuan",K,"未在藏；時代改標現代（光緒三十一年＝1905）",None,None,
  {"eraKey":"modern","title_orig":"","author":"李剛己 輯","era":"1905 年"})
d("zlz","景教碑考","early-modern","shizhuan",K,"未在藏（既有景教條目均為原始殘卷，非近人考證）；時代改標現代",None,None,
  {"eraKey":"modern","title_orig":"","author":"馮承鈞","era":"民國（20 世紀前半）"})
d("zlz","明末奉使羅馬教廷耶穌會士卜彌格傳","early-modern","shizhuan",K,"未在藏；沙不烈原著係近人研究，時代改標現代",None,None,
  {"eraKey":"modern","title_orig":"Le P. Michel Boym, jésuite polonais","author":"沙不烈（Robert Chabrié）著；馮承鈞 譯","era":"1933 年（原著）"})
d("zlz","聖五傷方濟各行實","early-modern","shizhuan",K,"未在藏；約根森原著 1907、中譯 1949，時代改標現代",None,None,
  {"eraKey":"modern","title_orig":"Den hellige Frans af Assisi","author":"約翰內斯‧約根森（Johannes Jørgensen）著；何芳理 譯","era":"1907 年（原著）／1949 年（漢譯）"})
d("zlz","聖女瑪德肋納素非拔拉傳","early-modern","shizhuan",K,"未在藏；土山灣民國本，時代改標現代",None,None,
  {"eraKey":"modern","title_orig":"","author":"耶穌聖心末僕 譯","era":"民國（土山灣印書館本）"})
d("zlz","彌撒祭考","early-modern","liyi",K,
  "未在藏；時代改標現代。作者存疑：英千里生於 1900，館藏標 1912 出版與之不合，疑為其父英斂之或年份有誤",None,None,
  {"eraKey":"modern","title_orig":"","author":"英千里（待考，見審定註）","era":"民國初年（待考）"})

# ─────────────── 現代 ───────────────
d("zlz","《百年通諭》","modern","lun",DE,"已在藏","[現代/正/書信] 百年通諭｜教宗若望保祿二世")
d("zlz","《貞潔婚姻》通諭","modern","lun",DE,"同書異名，已在藏","[現代/正/書信] 論基督徒婚姻通諭｜教宗庇護十一世",
  ["論基督徒婚姻通諭","貞潔婚姻通諭"])
d("zlz","上主的話","modern","lun",DE,"已在藏","[現代/正/書信] 上主的話勸諭｜教宗本篤十六世")
d("zlz","福音的喜樂","modern","lun",DE,"已在藏","[現代/正/書信] 福音的喜樂勸諭｜教宗方濟各")
d("trc","上帝存在嗎？","modern","lun",DE,"已在藏","[現代/正/論] 上帝存在嗎？今日的解答｜孔漢思")
d("trc","做基督徒","modern","lun",DE,"同書異名，已在藏","[現代/正/論] 論作基督徒｜孔漢思",
  ["論作基督徒","做基督徒","論基督徒"])
d("trc","論基督徒","modern","lun",DE,"同上（兩筆同判）","[現代/正/論] 論作基督徒｜孔漢思")
d("zlz","論基督徒","modern","lun",DE,"同上（兩站各一本）","[現代/正/論] 論作基督徒｜孔漢思")
d("trc","回到正統","modern","lun",DE,"同書異名，已在藏","[現代/正/詩文] 正統｜G.K.切斯特頓",
  ["正統","回到正統"])
d("zlz","基督教導論","modern","lun",DE,"已在藏","[現代/正/論] 基督教導論：使徒信經講釋｜拉辛格")
d("zlz","默觀生活探秘","modern","xuandao",DE,"同書異名，已在藏","[現代/正/論] 默觀的種子｜牟敦",
  ["默觀的種子","默觀生活探秘"])
d("zlz","教宗若望二十三世靈心日記","modern","shuxin",DE,"同書異名，已在藏","[現代/正/史傳] 靈魂日記｜若望二十三世",
  ["靈魂日記","靈心日記"])

d("zlz","禮儀的真諦","modern","liyi",K,
  "未在藏。勿與既有瓜爾迪尼《禮儀精神》相混——同名不同書，拉辛格此書是對前者的呼應",None,None,
  {"title_orig":"Der Geist der Liturgie","author":"若瑟‧拉辛格（後為教宗本篤十六世）","era":"2000 年"})
d("zlz","愛的聖事","modern","lun",K,"未在藏",None,None,{"author":"教宗本篤十六世","era":"2007 年"})
d("zlz","納匝肋人耶穌","modern","lun",K,"未在藏；原提案 title_orig「Nazarener Jesus」有誤",None,None,
  {"title_orig":"Jesus von Nazareth","author":"教宗本篤十六世（若瑟‧拉辛格）","era":"2007–2012 年"})
d("zlz","天主與世界","modern","lun",K,"未在藏",None,None,
  {"title_orig":"Gott und die Welt","author":"若瑟‧拉辛格；彼得‧西瓦爾德 訪談","era":"2000 年"})
d("zlz","耶穌基督","modern","lun",K,"未在藏；title_orig 補德文原題",None,None,
  {"title_orig":"Jesus der Christus","author":"華特‧卡斯培（Walter Kasper）","era":"1974 年"})
d("zlz","基督之律","modern","lun",K,"未在藏",None,None,
  {"title_orig":"Das Gesetz Christi","author":"白舍客（Bernhard Häring）","era":"1954 年"})
d("trc","世界倫理構想","modern","lun",K,"未在藏；作者名統一（既有藏內孔漢思／龔漢斯兩式並存，見稽核報告）",None,None,
  {"title_orig":"Projekt Weltethos","author":"孔漢思（Hans Küng）","era":"1990 年"})
d("trc","為何耶穌很重要？","modern","lun",K,"未在藏",None,None,
  {"title_orig":"Why Is He Important?","author":"丹尼爾‧哈靈頓（Daniel J. Harrington）"})
d("zlz","癖基督抹殺論","modern","lun",K,
  "未在藏；書名 OCR 誤字——「癖」應作「闢」，係駁幸德秋水《基督抹殺論》之護教書",None,None,
  {"title_zh":"闢基督抹殺論","title_orig":"","author":"殷雅各","era":"1925 年（廣學會）"})
d("zlz","評基督抹殺論","modern","lun",K,"未在藏；與上書同為民國護教文獻，作者不同勿併",None,None,
  {"title_orig":"","author":"沈嗣莊","era":"1925 年"})
d("zlz","創世論","modern","lun",K,"未在藏（既有同名者為五世紀維克託利烏斯的詩作，非同書）",None,None,
  {"title_orig":"","author":"湯漢","era":"現代"})
d("zlz","聖域門檻：洗禮、堅振、感恩聖事、聖秩","modern","lun",K,
  "未在藏；作者欄有誤——Joseph Martos 不是明清耶穌會士「馬若瑟」（Joseph de Prémare）",None,None,
  {"title_orig":"Doors to the Sacred","author":"若瑟‧馬托斯（Joseph Martos）著；劉國清 譯"})
d("zlz","關於祈求天主治癒的訓令","modern","lun",K,"未在藏",None,None,{"author":"教廷信理部","era":"2000 年"})
d("zlz","從共融的觀點看教會","modern","lun",K,"未在藏",None,None,
  {"title_orig":"Communionis notio","author":"教廷信理部","era":"1992 年"})
d("zlz","一九九九年基督降生第三個千年的司鐸","modern","lun",K,"未在藏",None,None,
  {"title_orig":"","author":"教廷聖職部；天主教臺灣地區主教團秘書處 編譯","era":"1999 年"})
d("zlz","耶穌會第卅五屆大會文獻","modern","lun",K,"未在藏",None,None,{"author":"耶穌會第三十五屆全體大會","era":"2008 年"})

d("zlz","2004年救贖聖事訓令","modern","lu",K,"未在藏",None,None,
  {"title_zh":"救贖聖事訓令","title_orig":"Redemptionis Sacramentum","author":"教廷禮儀及聖事部","era":"2004 年"})
d("zlz","一九九三年大公指南：大公運動原則與規範之應用指南","modern","lu",K,"未在藏",None,None,
  {"title_zh":"大公指南：大公運動原則與規範之應用指南","title_orig":"Directory for the Application of Principles and Norms on Ecumenism",
   "author":"宗座促進基督徒合一委員會","era":"1993 年"})
d("zlz","司鐸聖召的禮物：司鐸培育基本方案","modern","lu",K,"未在藏",None,None,
  {"title_orig":"Ratio Fundamentalis Institutionis Sacerdotalis","author":"教廷聖職部","era":"2016 年"})
d("zlz","有關傳教區派遣司鐸出國並居留之訓令","modern","lu",K,"未在藏",None,None,
  {"title_orig":"","author":"教廷萬民福音傳播部","era":"2001 年"})
d("zlz","權威的服務及服從","modern","lu",K,"未在藏",None,None,
  {"title_orig":"Faciem tuam, Domine, requiram","author":"教廷獻身生活及使徒團體部","era":"2008 年"})
d("zlz","聽告解者指南：論婚姻生活中的某些倫理問題","modern","lu",K,"未在藏",None,None,
  {"author":"宗座家庭委員會","era":"1997 年"})
d("zlz","論主教團之神學及法律性質","modern","lu",K,"未在藏",None,None,
  {"author":"教宗若望保祿二世","era":"1998 年"})

# 教宗文告一律改歸書信藏，與既有通諭／勸諭條目同列
d("zlz","《我要給你們牧者》勸諭","modern","shiwen",K,"未在藏；改歸書信藏（宗座勸諭）",None,None,
  {"collectionKey":"shuxin","title_zh":"我要給你們牧者勸諭","title_orig":"Pastores Dabo Vobis","author":"教宗若望保祿二世","era":"1992 年"})
d("zlz","主，請同我們一起住下罷","modern","shiwen",K,"未在藏；改歸書信藏（宗座牧函）",None,None,
  {"collectionKey":"shuxin","title_orig":"Mane Nobiscum Domine","author":"教宗若望保祿二世","era":"2004 年"})
d("zlz","活於感恩祭的教會","modern","shiwen",K,"未在藏；改歸書信藏（通諭）",None,None,
  {"collectionKey":"shuxin","title_zh":"教會活於感恩祭通諭","title_orig":"Ecclesia de Eucharistia","author":"教宗若望保祿二世","era":"2003 年"})
d("zlz","論天主仁慈自動諭牧函","modern","shiwen",K,"未在藏；改歸書信藏",None,None,
  {"collectionKey":"shuxin","title_orig":"Misericordia Dei","author":"教宗若望保祿二世","era":"2002 年"})
d("zlz","《奉獻生活》宗座勸諭","modern","xuandao",K,"未在藏；改歸書信藏（宗座勸諭）",None,None,
  {"collectionKey":"shuxin","title_zh":"奉獻生活勸諭","title_orig":"Vita Consecrata","author":"教宗若望保祿二世","era":"1996 年"})
d("zlz","《教會在亞洲》勸諭","modern","xuandao",K,"未在藏；改歸書信藏（宗座勸諭）",None,None,
  {"collectionKey":"shuxin","title_zh":"教會在亞洲勸諭","title_orig":"Ecclesia in Asia","author":"教宗若望保祿二世","era":"1999 年"})
d("zlz","《第三個千年降臨之際》文告","modern","xuandao",K,"未在藏；改歸書信藏（宗座牧函）",None,None,
  {"collectionKey":"shuxin","title_zh":"第三個千年將臨之際牧函","title_orig":"Tertio Millennio Adveniente","author":"教宗若望保祿二世","era":"1994 年"})
d("zlz","主的日子","modern","lun",K,"未在藏；改歸書信藏（宗座牧函）",None,None,
  {"collectionKey":"shuxin","title_orig":"Dies Domini","author":"教宗若望保祿二世","era":"1998 年"})
d("zlz","一九九五年致全球司鐸書","modern","shuxin",K,"未在藏",None,None,
  {"title_zh":"致全球司鐸書（1995）","title_orig":"","author":"教宗若望保祿二世","era":"1995 年"})
d("zlz","禮物與奧蹟","modern","shuxin",K,"未在藏；教宗晉鐸五十週年回憶錄",None,None,
  {"title_orig":"Dono e Mistero","author":"教宗若望保祿二世","era":"1996 年"})
d("zlz","教宗若望保祿二世元旦文告集","modern","shiwen",K,"未在藏；改歸書信藏（歷年世界和平日文告）",None,None,
  {"collectionKey":"shuxin","title_zh":"世界和平日文告集","title_orig":"Messaggi per la Giornata Mondiale della Pace",
   "author":"教宗若望保祿二世","era":"1979–2005 年"})
d("zlz","第十六屆世界主教代表常務會議大會第一會期《綜合報告》：以福傳為使命的共議性的教會","modern","shiwen",K,
  "未在藏；改歸律藏（世界主教會議文獻，與既有《世界正義文件》同類）",None,None,
  {"collectionKey":"lu","title_zh":"共議同行：第十六屆世界主教會議第一會期綜合報告",
   "title_orig":"Una Chiesa sinodale in missione: Relazione di sintesi","author":"世界主教代表會議","era":"2023 年"})

d("zlz","禮者，履也","modern","liyi",K,"未在藏",None,None,{"title_orig":"","author":"羅國輝","era":"現代"})
d("zlz","耶穌會團體祈禱手冊","modern","liyi",K,"未在藏",None,None,{"title_orig":"","author":"耶穌會中華省","era":"1978 年"})
d("zlz","袖珍每日禮讚","modern","liyi",K,"未在藏（既有《時辰祈禱禮》為拉丁通用本，此為華語簡編本）",None,None,
  {"title_orig":"","author":"天主教主教團禮儀委員會 編譯","era":"1991 年"})
d("trc","《華文聖體降福經文》雷鳴遠神父編","unknown","liyi",K,"未在藏；時代改標現代",None,None,
  {"eraKey":"modern","title_zh":"華文聖體降福經文","title_orig":"","author":"雷鳴遠（Vincent Lebbe）編","era":"民國（20 世紀前半）"})
d("zlz","心語融入靜默","modern","xuandao",K,"未在藏",None,None,
  {"title_orig":"Worte ins Schweigen","author":"卡爾‧拉納（Karl Rahner）","era":"1938 年"})
d("zlz","沒有人是一座孤島","modern","xuandao",K,"未在藏",None,None,
  {"author":"托馬斯‧牟敦（Thomas Merton）","era":"1955 年"})
d("zlz","為什麼要告解","modern","xuandao",K,"未在藏",None,None,
  {"title_orig":"Perché la confessione?","author":"布魯諾‧福爾泰（Bruno Forte）"})
d("zlz","與主接觸","modern","xuandao",K,"未在藏",None,None,
  {"title_orig":"Contact with God","author":"戴邁樂（Anthony de Mello）"})
d("zlz","青蛙的禱聲","modern","xuandao",K,"未在藏",None,None,
  {"title_orig":"The Prayer of the Frog","author":"戴邁樂（Anthony de Mello）","era":"1988 年"})
d("zlz","內心平安之道","modern","xuandao",K,"未在藏",None,None,
  {"title_orig":"La paix intérieure","author":"雅克‧菲利普（Jacques Philippe）"})
d("zlz","慕道者指南","modern","xuandao",K,"未在藏",None,None,{"title_orig":"","author":"李善修","era":"現代"})
d("zlz","基督之友","modern","xuandao",K,"未在藏",None,None,{"title_orig":"","author":"文助華","era":"現代"})
d("zlz","沒有意外這回事","modern","shiwen",K,"未在藏",None,None,
  {"author":"葛羅謝爾（Benedict J. Groeschel）、畢夏普（John Bishop）；沈映志 譯","era":"2004 年"})
d("zlz","聖女小德蘭二十一篇祈禱","modern","shiwen",K,"未在藏",None,None,
  {"title_orig":"Prières de sainte Thérèse de l'Enfant-Jésus","author":"里修的德蘭（聖女小德蘭）","era":"1893–1897 年"})
d("zlz","聖女小德蘭回憶錄","modern","shizhuan",K,"未在藏",None,None,
  {"title_orig":"Histoire d'une âme","author":"里修的德蘭（聖女小德蘭）；張秀亞 譯","era":"1895–1897 年"})
d("zlz","中國天主教傳教史","modern","shizhuan",K,"未在藏",None,None,
  {"title_orig":"","author":"德禮賢（Pasquale d'Elia）","era":"1930 年代"})
d("zlz","聖董文學神父傳","modern","shizhuan",K,"未在藏；董文學＝遣使會士 Jean-Gabriel Perboyre，1840 年殉道於武昌",None,None,
  {"title_orig":"","author":"佚名（公教出版社本）","era":"民國"})
d("zlz","超越東西方","modern","shizhuan",K,"未在藏（既有吳經熊條目均為聖經漢譯）",None,None,
  {"author":"吳經熊","era":"1951 年"})
d("zlz","馬相伯集","modern","shizhuan",K,"未在藏",None,None,{"title_orig":"","author":"馬相伯","era":"1840–1939"})
d("trc","方濟各傳阿奎那傳","modern","shiwen",K,"未在藏；改歸史傳藏（兩篇聖徒傳合刊，非文學創作）",None,None,
  {"collectionKey":"shizhuan","title_zh":"方濟各傳‧阿奎那傳","title_orig":"St. Francis of Assisi; St. Thomas Aquinas",
   "author":"G.K.切斯特頓","era":"1923 年／1933 年"})

d("trc","甜蜜的家—羅馬","unknown","lun",DS,
  "已識定為史考特‧韓與金柏莉‧韓《Rome Sweet Home》（1993）——由改革宗轉信天主教的通俗歸信見證，"
  "非原典層級，建議剔除。若使用者決定保留，應歸「現代／正藏／史傳藏」，作者「史考特‧韓、金柏莉‧韓」")

out = {
    "generated": "2026-08-30",
    "source_proposal": "PROPOSAL_2026-08-28.md",
    "match_key": ["source", "title_zh", "eraKey", "collectionKey"],
    "note": "人工審定結果。verdict 為 keep 者套用 patch 後入提案；drop_* 者不入提案。"
            "alias 欄的同書異名要補進翻譯詞庫 theological_terms（entity_type 為 work）。",
    "verdicts": V,
}
p = Path("data/dazangjing/source-catalog/adjudication-2026-08-30.json")
p.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
from collections import Counter
c = Counter(v["verdict"] for v in V)
print(f"寫出 {len(V)} 條判定 -> {p}")
for k, n in c.most_common():
    print(f"  {k}: {n}")
print(f"  alias 組: {sum(1 for v in V if v['alias'])}")
