# -*- coding: utf-8 -*-
"""第十七回　出師表（227–228）

📄 範文頁：出師表原文要整段放上去，不只講解。
（memory: feedback_lecture_first_order_before_second／project_lecture_quote_pages）
"""

TITLE = "三國第十七回"
MARK = "三國演義 · 第十七回"
SUB = "出師表"

SLIDES = [
{"cover": True,
 "html": """<div class="art">
   <div class="txt">
     <div class="eyebrow">第十七回</div>
     <h1>一封信，<em>唸了一千八百年</em></h1>
     <p class="sub">出兵之前，他寫了一封信給十七歲的皇帝。<br>那封信，到現在還有人背。</p>
     <div class="meta">
       <div><dt>時間</dt><dd>西元 227–228 年</dd></div>
       <div><dt>這一回</dt><dd>出師表與第一次北伐</dd></div>
       <div><dt>今天要弄懂</dt><dd>明知很難，為什麼還要做</dd></div>
     </div>
     <p class="credit">版畫與照片取自維基共享資源，出處見上方「圖片來源」</p>
   </div>
   <div class="cast">
     ${cf(chr({robe:"#EFE6D4",hat:"ru",beard:"mo",prop:"scroll"}),"諸葛亮","四十七歲")}
     ${im("books","出師表")}
   </div>
 </div>""",
 "note": """<p>這一回有<b>三頁範文</b>（📄），原文要唸出來，不要只講解。範文頁不趕時間。</p>
 <p class="ask">開場問：「明明知道做不到，還要不要做？」最後一頁回來對。</p>"""},

{"html": """<div class="eyebrow">一 · 先算一下</div>
 <h2>兩邊差多少</h2>
 <div class="tier">
   <div><span class="lbl">魏</span><span class="bar" style="width:84%"></span><span class="n">十三州・四百多萬人</span></div>
   <div><span class="lbl">吳</span><span class="bar" style="width:34%"></span><span class="n">三州・兩百多萬人</span></div>
   <div><span class="lbl">蜀</span><span class="bar" style="width:18%"></span><span class="n">一州・九十幾萬人</span></div>
 </div>
 <div class="callout">蜀漢的人口<b>大約是魏國的五分之一</b>。<br>而且荊州沒了，只剩一條路可以北上。</div>""",
 "note": """<p>長條圖一眼看懂。<b>這一頁要讓孩子先覺得「不可能吧」。</b></p>
 <p class="ask">問：「這樣還要打嗎？」</p>"""},

{"html": """<div class="eyebrow">二 · 那為什麼還要打</div>
 <h2>守著等，會等到什麼</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>魏國地大人多，<b>時間拖愈久，差距愈大</b></li>
     <li>蜀漢的人才會一個一個老去——趙雲已經七十歲了</li>
     <li>而且「光復漢室」是這個政權存在的理由，<b>不打就沒有理由</b></li>
   </ul>
   <div class="callout">他自己說得很清楚：<br><b>「不去打，坐著等，也是滅亡。」</b></div>
 </div>
 <div class="cast tight">${ph("wuhougate","成都武侯祠","後人紀念他的地方")}</div></div>""",
 "note": """<p><b>這一頁回答開場那個問題。</b>不是他不知道難，是「不做也一樣完」。</p>
 <p class="ask">問：「如果一定會輸，還要努力嗎？」</p>"""},

{"html": """<div class="eyebrow">三 · 那封信</div>
 <h2>出師表：寫給一個十七歲的孩子</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>出兵前，諸葛亮上了一封奏表給劉禪</li>
     <li>這封信<b>不是講軍事</b>，是講<b>他走了以後皇帝要怎麼做</b></li>
     <li>全文<b>七百多字</b>，提到「先帝」<b>十三次</b></li>
   </ul>
   <div class="callout">他不是在報告工作，<br><b>他在交代一個人怎麼長大。</b></div>
 </div>
 <div class="cast tight">${cf(chr({robe:"#C9A227",hat:"mian",cuff:"#8A6E18",small:1}),"劉禪","二十一歲了")}${im("books","七百多字")}</div></div>""",
 "note": """<p>「提到先帝十三次」可以讓孩子數。<b>這封信其實是寫給死去的劉備看的。</b></p>"""},

{"html": """<div class="eyebrow">四 · 範文（一）</div>
 <h2>先帝創業未半而中道崩殂</h2>
 <div class="callout" style="font-family:var(--serif);font-size:clamp(1.05rem,1.9vw,1.6rem);line-height:1.9">
   先帝創業未半，而中道崩殂。<br>
   今天下三分，益州疲弊，此誠危急存亡之秋也。<br>
   然侍衛之臣，不懈於內；忠志之士，忘身於外者，<br>
   蓋追先帝之殊遇，欲報之於陛下也。
 </div>
 <p class="foot">先帝的事業做到一半就走了。現在天下分成三塊，我們這一塊最弱——<b>這真是生死關頭</b>。
 可是宮裡的侍衛沒有懈怠，外面的將士拼命打仗，因為他們記得先帝對他們的好，想報答在您身上。</p>""",
 "note": """<p>📄 <b>原文先唸一遍，再唸白話。</b>不要跳過原文——文言文的節奏本身就是重點。</p>
 <p>「危急存亡之秋」這五個字現在還在用，可以問孩子有沒有聽過。</p>"""},

{"html": """<div class="eyebrow">五 · 範文（二）</div>
 <h2>親賢臣，遠小人</h2>
 <div class="callout" style="font-family:var(--serif);font-size:clamp(1.05rem,1.9vw,1.6rem);line-height:1.9">
   親賢臣，遠小人，此先漢所以興隆也；<br>
   親小人，遠賢臣，此後漢所以傾頹也。<br>
   先帝在時，每與臣論此事，<br>
   未嘗不歎息痛恨於桓、靈也。
 </div>
 <p class="foot">親近好人、遠離小人，前半段的漢朝就是這樣強起來的；
 親近小人、遠離好人，後半段的漢朝就是這樣垮掉的。<b>先帝每次跟我談到這件事，都會嘆氣。</b></p>""",
 "note": """<p>📄 原文唸完再解釋。<b>「桓、靈」就是第一回那個十二歲的漢靈帝。</b>整套課從第一回繞回來了。</p>
 <p class="ask">問：「怎麼分辨誰是好人誰是小人？」——這也是劉禪的問題。</p>"""},

{"html": """<div class="eyebrow">六 · 範文（三）</div>
 <h2>臣本布衣，躬耕於南陽</h2>
 <div class="callout" style="font-family:var(--serif);font-size:clamp(1.05rem,1.9vw,1.6rem);line-height:1.9">
   臣本布衣，躬耕於南陽，<br>
   苟全性命於亂世，不求聞達於諸侯。<br>
   先帝不以臣卑鄙，猥自枉屈，三顧臣於草廬之中，<br>
   諮臣以當世之事，由是感激，遂許先帝以驅馳。
 </div>
 <p class="foot">我本來是個普通人，在南陽自己種田，只想在亂世裡活下去，沒想過出名。
 先帝不嫌我出身低，<b>親自跑了三趟到我的草屋</b>，問我天下大事。我很感動，才答應為他奔走。</p>""",
 "note": """<p>📄 這一段就是<b>第十回三顧茅廬那三頁</b>——當事人自己的說法。回頭翻給孩子看。</p>
 <p>「三顧臣於草廬之中」——<b>史書上那四個字「凡三往，乃見」的另一個版本。</b></p>"""},

{"html": """<div class="eyebrow">七 · 還有一句</div>
 <h2>五月渡瀘，深入不毛</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>信裡回顧他這些年做過的事，其中一句是：<b>「五月渡瀘，深入不毛。」</b></li>
     <li>就是<b>第十六回</b>南征那一段——五月渡過瀘水，深入荒涼的地方</li>
     <li>接著他說：<b>「今南方已定，兵甲已足。」</b></li>
   </ul>
   <div class="callout">第十六回做的事，<br><b>就是為了這一句話。</b></div>
 </div>
 <div class="cast tight">${ph("ehon_017_001","江戶時代畫的三國","《繪本通俗三國志》插圖")}</div></div>""",
 "note": """<p>第十六回講過這八個字，<b>孩子這時候會有「我知道！」的反應</b>。那個時刻很重要。</p>"""},

{"html": """<div class="eyebrow">八 · 最後一段</div>
 <h2>今當遠離，臨表涕零</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>信的最後，他說自己受先帝託付，<b>日夜擔心做不好</b></li>
     <li>又交代：如果我北伐沒有成效，<b>就治我的罪</b></li>
     <li>結尾八個字：<b>「今當遠離，臨表涕零。」</b></li>
   </ul>
   <div class="callout">——我就要出遠門了，<br>對著這封表，<b>眼淚掉下來。</b></div>
 </div>
 <div class="cast tight">${ph("wuhoustele","武侯祠碑刻","一千多年來的紀念")}</div></div>""",
 "note": """<p>「臨表涕零」四個字唸完停一下。<b>一個四十七歲的丞相，寫信寫到哭。</b></p>
 <p>⚠︎ 順帶說明：<b>「鞠躬盡瘁，死而後已」不在這封信裡</b>，那是後出師表，而且後出師表是不是他寫的還有爭議。</p>"""},

{"html": """<div class="eyebrow">九 · 出兵</div>
 <h2>大軍開進漢中</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>227 年春天，諸葛亮率軍進駐漢中，準備了一年</li>
     <li>228 年正式出兵——這是<b>第一次北伐</b></li>
     <li>他先放出消息：<b>要從斜谷道取郿城</b></li>
   </ul>
   <div class="callout">魏國果然把主力調過去。<br><b>其實那是假的。</b></div>
 </div>
 <div class="cast tight">${im("mountain","翻過秦嶺")}${im("flag","放假消息")}</div></div>""",
 "note": """<p>這是<b>聲東擊西</b>。孩子在前面幾回看過很多次（第九回打旗號、第十三回裝病）。</p>"""},

{"html": """<div class="eyebrow">十 · 疑兵</div>
 <h2>七十歲的趙雲去演那一路</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>負責假裝主力的是<b>趙雲</b>和鄧芝，帶著少量兵力</li>
     <li>魏國大將曹真帶重兵去擋他們</li>
     <li>趙雲兵少打不過，但<b>親自斷後，部隊沒有潰散</b></li>
   </ul>
   <div class="callout">撤退時軍用物資<b>幾乎沒有損失</b>。<br>諸葛亮要賞他，他說：<b>打輸了還領賞，不合適。</b></div>
 </div>
 <div class="cast tight">${cf(chr({robe:"#B9B4AC",hat:"wu",beard:"mo",prop:"spear"}),"趙雲","七十歲，最後一仗")}</div></div>""",
 "note": """<p>趙雲這時候<b>七十歲左右</b>，隔年就過世了。<b>這是他最後一場仗。</b></p>
 <p>從第十回長坂坡到現在，孩子跟著他走了七回。</p>"""},

{"html": """<div class="eyebrow">十一 · 真正的那一路</div>
 <h2>三個郡投降了</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>主力其實走<b>西邊的祁山道</b>，目標是隴右</li>
     <li>魏國完全沒防備——<b>南安、天水、安定三個郡直接投降</b></li>
     <li>整個關中震動，魏明帝<b>親自趕到長安坐鎮</b></li>
   </ul>
   <div class="callout">開局好得<b>超出所有人預期</b>。</div>
   <p class="foot">也是在這時候，一個二十六歲的魏國小將投降過來——他叫<b>姜維</b>。</p>
 </div>
 <div class="cast tight">${ph("jiangwei","姜維","二十六歲歸降")}</div></div>""",
 "note": """<p>姜維<b>第十九、二十回是主角</b>。他是諸葛亮收的最後一個學生。先記住臉。</p>"""},

{"html": """<div class="eyebrow">十二 · 一條路</div>
 <h2>街亭：所有東西都要從那裡過</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>魏國的援軍要從關中進隴右，<b>只能走街亭那條路</b></li>
     <li>守住街亭，隴右三郡就能慢慢消化</li>
     <li>守不住，<b>前面拿到的全部要吐出來</b></li>
   </ul>
   <div class="callout">整場北伐的勝負，<br><b>押在一個地名上。</b></div>
 </div>
 <div class="cast tight">${im("mountain","咽喉")}${im("map","只有一條路")}</div></div>""",
 "note": """<p>「咽喉」這個比喻要講清楚——<b>像吃東西一定要過喉嚨。</b></p>"""},

{"html": """<div class="eyebrow">十三 · 派誰去</div>
 <h2>所有人都以為會選那兩個</h2>
 <div class="cols">
   <div class="card">${chr({robe:"#8C2F1E",hat:"wu",beard:"mo",prop:"dao"})}<h3>魏延</h3><p>資歷最深、最能打。<b>大家都覺得是他。</b></p></div>
   <div class="card">${chr({robe:"#8A7B52",hat:"wu",beard:"mo",prop:"dao"})}<h3>吳懿</h3><p>另一個老將，也很穩。</p></div>
 </div>
 <div class="callout">可是諸葛亮選了<b>馬謖</b>——<br>第十六回說「攻心為上」的那一位。</div>""",
 "note": """<p>史書明寫：<b>「違眾拔謖」</b>——不顧大家的意見提拔馬謖。</p>
 <p class="ask">問：「為什麼要選一個沒帶過兵的人？」（因為他講的話最合諸葛亮的意）</p>"""},

{"html": """<div class="eyebrow">十四 · 劉備說過</div>
 <h2>「馬謖言過其實，不可大用」</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>第十五回劉備臨終前，特別交代過一句話</li>
     <li>他說馬謖<b>「言過其實」</b>——講得比做得到的多，不能重用</li>
     <li>諸葛亮<b>沒有聽進去</b></li>
   </ul>
   <div class="callout">整套課裡，<br><b>諸葛亮很少有沒聽劉備話的時候。</b></div>
 </div>
 <div class="cast tight">${cf(chr({robe:"#8A7B52",hat:"ru",beard:"mo",prop:"scroll"}),"馬謖","三十九歲")}${ph("wangshuang","王雙","魏國將領")}</div></div>""",
 "note": """<p>🚩 <b>這一頁是整回的伏筆爆點。</b>劉備看人很準——第十五回沒講，這裡補上。</p>
 <p class="ask">問：「為什麼諸葛亮不聽？」（因為他喜歡馬謖，而且馬謖真的很會講）</p>"""},

{"html": """<div class="eyebrow">十五 · 交代</div>
 <h2>出發前說得清清楚楚</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>諸葛亮交代：<b>當道紮營</b>——擋住路，不要上山</li>
     <li>還派了<b>王平</b>當副手，王平打仗經驗豐富</li>
     <li>馬謖帶著幾萬人出發了</li>
   </ul>
   <div class="callout">命令很明確，<br>人選有備援。<br><b>照理說不會出事。</b></div>
 </div>
 <div class="cast tight">${ph("ehon_017_002","江戶時代畫的三國","《繪本通俗三國志》插圖")}</div></div>""",
 "note": """<p><b>這一頁是懸念。</b>故意讓孩子覺得「應該沒問題」，下一回才有落差。</p>"""},

{"html": """<div class="eyebrow">十六 · 後面的事</div>
 <h2>今天先不說</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>馬謖到了街亭，做了一個決定</li>
     <li>那個決定，讓這一次北伐<b>前面所有的成果都沒了</b></li>
     <li>也讓諸葛亮做了一件他一輩子最難過的事</li>
   </ul>
   <div class="callout">下一回再說。</div>
 </div>
 <div class="cast tight">${im("hourglass","下一回")}${im("sick","最難過的事")}</div></div>""",
 "note": """<p><b>故意賣關子。</b>孩子會追問，讓他們帶著問題離開。</p>
 <p>如果他們硬要問，可以說：「他沒有照交代做。」到此為止。</p>"""},

{"html": """<div class="eyebrow">十六之二 · 對面是誰</div>
 <h2>魏國派了一個很會等的人</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>擋住街亭援軍那一路的魏軍主將是<b>張郃</b>——第九回官渡那個投降曹操的人</li>
     <li>他打了三十年仗，<b>最擅長看地形</b></li>
     <li>而魏國真正的靈魂人物，這時候還在荊州方向：<b>司馬懿</b></li>
   </ul>
   <div class="callout">諸葛亮派了一個<b>沒帶過兵的人</b>，<br>去對上一個<b>打了三十年仗的人</b>。</div>
 </div>
 <div class="cast tight">${cf(chr({robe:"#2E4A63",hat:"wu",beard:"mo",prop:"dao"}),"張郃","打了三十年仗")}${ph("xiahouba","夏侯霸","魏國將領，後來會投奔蜀漢")}</div></div>""",
 "note": """<p>張郃第九回出現過（主張去救烏巢的那個）。<b>從 200 年到 228 年，他還在。</b>回頭指一下。</p>
 <p>司馬懿先提名字，<b>第十八回才正式登場。</b></p>"""},

{"html": """<div class="eyebrow">十七 · 這一回的話</div>
 <h2>一千八百年後還有人背它</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>出師表被收進歷代的課本，到今天台灣的國文課還在教</li>
     <li>宋朝的文天祥說：<b>「讀出師表不哭的人，不是忠臣。」</b></li>
     <li>可是這封信裡<b>沒有一句在講怎麼打仗</b></li>
   </ul>
   <div class="callout">被記住的不是計謀，<br><b>是一個人明知很難還要去做的樣子。</b></div>
 </div>
 <div class="cast tight">${ph("ehon_017_003","江戶時代畫的三國","《繪本通俗三國志》插圖")}</div></div>""",
 "note": """<p>回到開場「明知做不到還要不要做」。<b>讓孩子自己說。</b></p>"""},

{"html": """<div class="eyebrow">最後</div>
 <h2>今天哪些是編的</h2>
 <div class="cols">
   <div class="card"><h3>編的</h3><p>
     <b>後出師表「鞠躬盡瘁」</b>：不在這封信裡，而且是不是他寫的有爭議<br><br>
     <b>七擒孟獲後南方立刻大富</b>：有幫助，但小說誇大了<br><br>
     <b>魏延獻「子午谷奇謀」被否決</b>：史書有記，但細節出自注引，爭議很大</p></div>
   <div class="card"><h3>真的</h3><p>
     <b>出師表全文</b>：真的，原文完整流傳<br><br>
     <b>提到「先帝」十三次</b>：真的，可以數<br><br>
     <b>三郡投降、魏明帝親赴長安</b>：真的<br><br>
     <b>姜維歸降</b>：真的<br><br>
     <b>劉備說馬謖言過其實</b>：真的<br><br>
     <b>違眾拔謖</b>：真的，史書原話</p></div>
 </div>
 <div class="callout">這一回<b>最重要的東西是真的</b>——<br>那七百多個字，<b>一個字都沒有改。</b></div>""",
 "note": """<p>固定收尾頁。可以讓孩子挑一句最喜歡的原文抄下來。</p>"""},
]
