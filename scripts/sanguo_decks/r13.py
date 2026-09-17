# -*- coding: utf-8 -*-
"""第十三回　敗走麥城（219）

最高點和最低點在同一回。
🚨 第三回講稿原本寫「關公廟留到第十五回」，已改為第十三回＝這一回。
"""

TITLE = "三國第十三回"
MARK = "三國演義 · 第十三回"
SUB = "敗走麥城"

SLIDES = [
{"cover": True,
 "html": """<div class="art">
   <div class="txt">
     <div class="eyebrow">第十三回</div>
     <h1>最高的那一年，<em>也是最後一年</em></h1>
     <p class="sub">半年前他讓整個北方發抖。<br>半年後，他只剩幾百個人。</p>
     <div class="meta">
       <div><dt>時間</dt><dd>西元 219 年，荊州</dd></div>
       <div><dt>這一回</dt><dd>水淹七軍到敗走麥城</dd></div>
       <div><dt>今天要弄懂</dt><dd>為什麼贏太多反而危險</dd></div>
     </div>
     <p class="credit">版畫與繡像取自維基共享資源，出處見上方「圖片來源」</p>
   </div>
   <div class="cast">
     ${cf(chr({robe:"#4F7460",hat:"jin",beard:"long",prop:"dao"}),"關羽","鎮守荊州十年")}
     ${im("rain","下了十幾天雨")}
   </div>
 </div>""",
 "note": """<p>🚩 這一回<b>結局很悲傷</b>，先跟孩子預告一聲，不要突然打擊他們。</p>
 <p class="ask">開場問：「一直贏、一直贏，會發生什麼事？」最後一頁回來對。</p>"""},

{"html": """<div class="eyebrow">一 · 他的處境</div>
 <h2>三個問題，一個人扛</h2>
 <div class="tier">
   <div><span class="lbl">人少</span><span>諸葛亮、張飛、趙雲<b>都調去四川了</b></span></div>
   <div><span class="lbl">地借的</span><span>東吳<b>一直在等著要回去</b></span></div>
   <div><span class="lbl">兩面</span><span>北邊曹操、東邊孫權，<b>兩邊都要防</b></span></div>
 </div>
 <div class="callout">第十二回結尾那三條，<br><b>這一回全部爆開。</b></div>""",
 "note": """<p>回頭指第十二回最後一頁。<b>這三條不是突然出現的，是十年前就埋好的。</b></p>"""},

{"html": """<div class="eyebrow">二 · 他出兵了</div>
 <h2>往北打襄陽、樊城</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>劉備剛拿下漢中當上漢中王，蜀漢的氣勢最旺</li>
     <li>關羽決定<b>往北打</b>——這就是隆中對說的「兩路北伐」</li>
     <li>可是另一路（劉備從漢中出兵）<b>並沒有動</b></li>
   </ul>
   <div class="callout">說好的兩路，<br><b>只出了一路。</b></div>
 </div>
 <div class="cast tight">${ph("guanping","關平","關羽的兒子，跟著出征")}</div></div>""",
 "note": """<p>回頭指第十回隆中對「兩路北伐」。<b>計畫的第三步，只走了一半。</b></p>
 <p class="ask">問：「一個人走兩個人的路，會怎麼樣？」</p>"""},

{"html": """<div class="eyebrow">三 · 那場雨</div>
 <h2>下了十幾天</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>曹操派<b>于禁</b>、<b>龐德</b>帶七支軍隊來救樊城</li>
     <li>他們紮營在低窪的地方</li>
     <li>八月，漢水<b>連下十幾天大雨</b>，河水暴漲好幾丈</li>
   </ul>
   <div class="callout">關羽早就準備好了船。<br>水一來，<b>他坐船去收人。</b></div>
 </div>
 <div class="cast tight">${im("rain","十幾天")}${im("wave","水漲好幾丈")}</div></div>""",
 "note": """<p>「水淹七軍」不是他<b>放</b>的水，是他<b>算準了</b>會淹——和第十回「等東風」是同一種本事。</p>
 <p class="ask">問：「這算不算作弊？」（他只是比別人早知道會下雨）</p>"""},

{"html": """<div class="eyebrow">四 · 兩種人</div>
 <h2>一個投降，一個不降</h2>
 <div class="cols">
   <div class="card">${chr({robe:"#2E4A63",hat:"wu",beard:"mo",sad:1})}<h3>于禁</h3><p>跟曹操<b>三十年</b>的老將，當場投降。曹操知道後嘆氣說：我認識他三十年，<b>想不到他還不如龐德</b>。</p></div>
   <div class="card">${chr({robe:"#8A7B52",hat:"wu",beard:"long"})}<h3>龐德</h3><p>來之前就<b>帶了一口棺材</b>。被抓後站著不跪，被殺。</p></div>
 </div>
 <div class="callout">同一場仗、同一個處境，<br><b>兩個人選了不一樣的路。</b></div>""",
 "note": """<p>兩張卡對照。<b>不要說誰對誰錯</b>，讓孩子自己想。</p>
 <p>可以提：于禁後來被放回魏國，看到牆上畫著他投降的畫，<b>羞愧而死</b>。</p>"""},

{"html": """<div class="eyebrow">五 · 威震華夏</div>
 <h2>曹操想搬家了</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>七軍全沒了，樊城被圍，附近好幾股勢力<b>都響應關羽</b></li>
     <li>消息傳到許都，曹操<b>認真考慮把首都搬走</b></li>
     <li>史書上用四個字形容那時候的關羽：<b>威震華夏</b></li>
   </ul>
   <div class="callout">整個中國北方，<br><b>都在怕一個人。</b></div>
 </div>
 <div class="cast tight">${ph("guanyubig","關羽","許昌春秋樓十五公尺塑像")}</div></div>""",
 "note": """<p>「威震華夏」四個字<b>正史只給過關羽一個人</b>。要講重。</p>
 <p>這是<b>整回的最高點</b>，接下來一路往下掉。</p>"""},

{"html": """<div class="eyebrow">六 · 刮骨</div>
 <h2>一邊開刀，一邊下棋</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>關羽手臂中過一箭，<b>毒已經進到骨頭</b></li>
     <li>醫生說要割開肉、刮掉骨頭上的毒</li>
     <li>開刀的時候，他<b>照樣和人喝酒下棋</b>，血流了一盆</li>
   </ul>
   <div class="callout">史書真的有這一段——<br><b>只是沒說醫生是華佗。</b>⚠︎</div>
 </div>
 <div class="cast tight">${ph("ehon_012_002","江戶時代畫的三國","《繪本通俗三國志》插圖")}</div></div>""",
 "note": """<p>孩子一定聽過「刮骨療毒」。<b>破的梗只有「醫生不是華佗」</b>——華佗那時候已經死了。</p>"""},

{"html": """<div class="eyebrow">七 · 東邊在想什麼</div>
 <h2>魯肅死了，換人了</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>第十一回那個主張「跟劉備當朋友」的<b>魯肅</b>，兩年前病死了</li>
     <li>接他位子的是<b>呂蒙</b>——他的想法完全相反</li>
     <li>呂蒙說：關羽早晚是禍害，<b>不如趁現在拿回荊州</b></li>
   </ul>
   <div class="callout">第十一回那一頁還記得嗎——<br><b>「魯肅一死，荊州馬上出事。」</b></div>
 </div>
 <div class="cast tight">${ph("lvmeng2","呂蒙","接魯肅位子的人")}</div></div>""",
 "note": """<p>回頭指第十一回「換人，路線就變了」那一頁。<b>伏筆在這裡收。</b></p>"""},

{"html": """<div class="eyebrow">八 · 裝病</div>
 <h2>呂蒙說他生病了</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>關羽一直防著呂蒙，留了不少兵在後方</li>
     <li>呂蒙<b>對外宣稱重病</b>，回建業養病</li>
     <li>接替他的是一個<b>沒有名氣的年輕人</b>：陸遜</li>
   </ul>
   <div class="callout">關羽聽說對面換了個年輕人，<br><b>就把後方的兵調到前線了。</b></div>
 </div>
 <div class="cast tight">${ph("luxun","陸遜","那年三十七歲，沒有名氣")}</div></div>""",
 "note": """<p>這是<b>第三次「離間／欺敵」</b>（第六回貂蟬、第十一回塗改書信、這一回裝病）。整套課的手法整理。</p>
 <p class="ask">問：「為什麼派沒名氣的人反而有用？」</p>"""},

{"html": """<div class="eyebrow">九 · 一封很客氣的信</div>
 <h2>陸遜寫信誇他</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>陸遜一上任就寫信給關羽，滿篇都是<b>佩服與恭維</b></li>
     <li>說自己是個書生，只希望將軍多多照顧</li>
     <li>關羽看完<b>放心了</b>，把留守的兵幾乎全部調走</li>
   </ul>
   <div class="callout">第四回埋的那句話，<br><b>這一回第三次收：太有把握的人最好騙。</b></div>
 </div>
 <div class="cast tight">${im("envelope","一封客氣的信")}${im("flag","後方空了")}</div></div>""",
 "note": """<p>回頭指第四回、第九回（袁紹）、第十回（曹操）。<b>這是同一條線的第三次，而且這次輪到關羽。</b></p>"""},

{"html": """<div class="eyebrow">十 · 白衣渡江</div>
 <h2>商船裡坐的是兵</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>呂蒙病是裝的。他挑選精兵，<b>全部換上白色的商人衣服</b></li>
     <li>划著商船沿江而上，<b>沿途的烽火台守兵全部被綁了</b></li>
     <li>所以荊州<b>一個警訊都沒有發出去</b></li>
   </ul>
   <div class="callout">等關羽知道的時候，<br><b>荊州已經換了主人。</b></div>
 </div>
 <div class="cast tight">${ph("ehon_013_001","江戶時代畫的三國","《繪本通俗三國志》插圖")}</div></div>""",
 "note": """<p>「白衣」＝平民的衣服，不是白色鎧甲。<b>這個詞要解釋。</b></p>
 <p>烽火台是古代的警報系統，<b>被一個一個拔掉</b>——這才是最可怕的地方。</p>"""},

{"html": """<div class="eyebrow">十一 · 不戰而散</div>
 <h2>他的兵自己走了</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>呂蒙進城後<b>一個人都沒有殺</b>，還派醫生照顧老人</li>
     <li>他讓城裡的家屬<b>寫信給前線的士兵</b>，說家裡都好</li>
     <li>關羽的兵看完信，<b>一個一個離開了</b>——家在那邊</li>
   </ul>
   <div class="callout">呂蒙沒有打，<br><b>他把關羽的軍隊「請」回家了。</b></div>
 </div>
 <div class="cast tight">${im("envelope","家書")}${im("houses","家在城裡")}</div></div>""",
 "note": """<p><b>全回最厲害的一段。</b>不用刀，用「家」把一支大軍解散。</p>
 <p class="ask">問：「如果你是那些士兵，你會走嗎？」</p>"""},

{"html": """<div class="eyebrow">十二 · 麥城</div>
 <h2>從幾萬人變成幾百人</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>關羽往回走，一路上兵愈來愈少</li>
     <li>退到一座小城<b>麥城</b>時，身邊只剩<b>幾百人</b></li>
     <li>他向附近的劉封、孟達求救，<b>沒有人來</b></li>
   </ul>
   <div class="callout">半年前他讓整個北方發抖，<br><b>現在他守著一座沒有人聽過的小城。</b></div>
 </div>
 <div class="cast tight">${ph("ehon_014_001","江戶時代畫的三國","《繪本通俗三國志》插圖")}</div></div>""",
 "note": """<p>對比要唸出來：<b>威震華夏 → 幾百人。中間只隔了不到半年。</b></p>"""},

{"html": """<div class="eyebrow">十二之二 · 沒有人來</div>
 <h2>最近的援兵，在山那一邊</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>離麥城最近的蜀漢部隊在<b>上庸</b>，由<b>劉封</b>和孟達駐守</li>
     <li>關羽派人去求救，兩次</li>
     <li>他們說：<b>上庸剛拿下來，人心不穩，走不開。</b></li>
   </ul>
   <div class="callout">劉封是<b>劉備的養子</b>。<br>他沒有去救——這件事<b>後來要了他自己的命</b>。</div>
 </div>
 <div class="cast tight">${im("mountain","山那一邊")}${im("envelope","求救的信")}</div></div>""",
 "note": """<p>劉封後來被劉備賜死，罪名之一就是<b>見死不救</b>。第十五回會提一句。</p>
 <p class="ask">問：「他們的理由聽起來合理嗎？」（合理——可是人還是死了）</p>"""},

{"html": """<div class="eyebrow">十三 · 最後</div>
 <h2>那條小路上有埋伏</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>他在城頭插滿旗子、做了假人，趁夜從小路突圍</li>
     <li>走到臨沮的一條夾道，<b>兩邊都是東吳的兵</b></li>
     <li>他和兒子<b>關平</b>一起被俘，孫權勸降，他不肯</li>
   </ul>
   <div class="callout">父子兩人同一天被殺。<br>關羽那年<b>大約六十歲</b>。</div>
 </div>
 <div class="cast tight">${cf(chr({robe:"#4F7460",hat:"jin",beard:"long",sad:1}),"關羽","走完了")}</div></div>""",
 "note": """<p>🚩 <b>講完停一下</b>，不要馬上翻頁。這是整套課第一個主角離開。</p>
 <p>從第三回桃園結義到現在，孩子跟他走了十回。</p>"""},

{"html": """<div class="eyebrow">十四 · 一顆頭</div>
 <h2>孫權把頭送給曹操</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>孫權知道劉備一定會報復，想<b>把責任推給曹操</b></li>
     <li>他把關羽的頭送到洛陽</li>
     <li>曹操看穿了，<b>用諸侯的禮節厚葬</b>，還親自去拜</li>
   </ul>
   <div class="callout">所以民間有一句話：<br><b>「頭枕洛陽，身臥當陽，魂歸山西。」</b></div>
 </div>
 <div class="cast tight">${ph("ehon_014_002","江戶時代畫的三國","《繪本通俗三國志》插圖")}</div></div>""",
 "note": """<p>三個地方分別是：洛陽（頭）、當陽（身）、山西解州（老家）。<b>孩子會覺得很神奇。</b></p>
 <p>曹操這個舉動很有意思：<b>敵人也可以被尊敬。</b></p>"""},

{"html": """<div class="eyebrow">十五 · 為什麼他變成神</div>
 <h2>一千八百年後，還有人拜</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>他的廟從中國蓋到台灣、東南亞、<b>全世界的華人街</b></li>
     <li>商人拜他（重信用）、警察拜他（講義氣）、讀書人也拜他</li>
     <li>他從將軍變成<b>關公、關帝、伏魔大帝</b></li>
   </ul>
   <div class="callout">第三回說過：<b>他們的廟，到現在還有人拜。</b><br>那一回埋的，這一回終於講清楚為什麼。</div>
 </div>
 <div class="cast tight">${ph("guanxing","關興","關羽的另一個兒子，後來替父報仇")}</div></div>""",
 "note": """<p>🚩 <b>第三回講稿原本寫「關公廟留到第十五回」，現在改在這一回（第十三回）。</b></p>
 <p class="ask">問：「為什麼是他變成神，不是更會打的呂布？」（因為大家看重的是<b>他怎麼做人</b>，不是他多會打）</p>"""},

{"html": """<div class="eyebrow">十六 · 他自己的問題</div>
 <h2>不只是被騙</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>孫權曾想幫兒子娶關羽的女兒，關羽<b>罵使者滾出去</b></li>
     <li>後方守將糜芳、傅士仁怕他責罰，<b>直接開城投降</b></li>
     <li>第十二回提過：他聽說馬超來了，還寫信問<b>「馬超比得上我嗎」</b></li>
   </ul>
   <div class="callout">他對敵人很勇敢，<br><b>可是對自己人很不客氣。</b></div>
 </div>
 <div class="cast tight">${ph("zhangbao","張苞","張飛的兒子，下一回會出現")}</div></div>""",
 "note": """<p>🚩 <b>這一頁很重要，不要跳過。</b>不能只講「他被騙了」——他自己也有責任。</p>
 <p class="ask">問：「一個人很厲害，可是脾氣不好，會怎麼樣？」</p>"""},

{"html": """<div class="eyebrow">十七 · 這一回的話</div>
 <h2>贏太多，是危險的</h2>
 <div class="tl">
   <div><span class="yr">219 七月</span><span>出兵北伐</span><span class="ago">開始</span></div>
   <div><span class="yr">219 八月</span><span>水淹七軍，威震華夏</span><span class="ago">最高點</span></div>
   <div><span class="yr">219 十月</span><span>後方空虛，白衣渡江</span><span class="ago">轉折</span></div>
   <div class="now"><span class="yr">219 十二月</span><span>敗走麥城</span><span class="ago">結束</span></div>
 </div>
 <div class="callout">從最高到最低，<br><b>只花了五個月。</b></div>""",
 "note": """<p>四行走完五個月。回到開場「一直贏會怎樣」的問題。</p>
 <p>下一回預告：<b>這一年還沒完。再過一個月，曹操也死了。</b></p>"""},

{"html": """<div class="eyebrow">最後</div>
 <h2>今天哪些是編的</h2>
 <div class="cols">
   <div class="card"><h3>編的</h3><p>
     <b>華佗刮骨療毒</b>：刮骨是真的，<b>華佗早就死了</b><br><br>
     <b>單刀赴會</b>：是真的，但主角是<b>魯肅</b>，他才是那個一個人去談判的人<br><br>
     <b>玉泉山顯聖</b>：小說加的</p></div>
   <div class="card"><h3>真的</h3><p>
     <b>水淹七軍、于禁投降、龐德抬棺</b>：真的<br><br>
     <b>威震華夏、曹操想遷都</b>：真的<br><br>
     <b>呂蒙裝病、陸遜寫信</b>：真的<br><br>
     <b>白衣渡江、家書散兵</b>：真的<br><br>
     <b>關羽罵孫權的使者</b>：真的<br><br>
     <b>曹操厚葬關羽</b>：真的</p></div>
 </div>
 <div class="callout">小說把關羽寫成完人，<br>可是史書寫他<b>脾氣很差</b>——<br><b>那個有缺點的關羽，反而更像一個真的人。</b></div>""",
 "note": """<p>固定收尾頁。最後那句是整回的重點，也是整套課看人的方法。</p>"""},
]
