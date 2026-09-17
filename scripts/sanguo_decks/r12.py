# -*- coding: utf-8 -*-
"""第十二回　入西川（211–219）

隆中對的第二塊地。劉備一生最風光的八年，收在漢中王。
下一回就是斷崖。
"""

TITLE = "三國第十二回"
MARK = "三國演義 · 第十二回"
SUB = "入西川"

SLIDES = [
{"cover": True,
 "html": """<div class="art">
   <div class="txt">
     <div class="eyebrow">第十二回</div>
     <h1>他終於<em>有家了</em></h1>
     <p class="sub">五十歲那年進四川，<br>五十八歲那年當上漢中王。</p>
     <div class="meta">
       <div><dt>時間</dt><dd>西元 211–219 年</dd></div>
       <div><dt>這一回</dt><dd>取益州與漢中之戰</dd></div>
       <div><dt>今天要弄懂</dt><dd>什麼叫「請神容易送神難」</dd></div>
     </div>
     <p class="credit">版畫與繡像取自維基共享資源，出處見上方「圖片來源」</p>
   </div>
   <div class="cast">
     ${cf(chr({robe:"#8C2F1E",hat:"mian",cuff:"#6E2418",beard:"mo"}),"劉備","五十八歲當上漢中王")}
     ${im("mountain","四面是山")}
   </div>
 </div>""",
 "note": """<p>這一回是<b>劉備一生的高點</b>。下一回開始急轉直下，所以這一回要讓孩子<b>先高興起來</b>。</p>
 <p class="ask">開場問：「請別人來家裡幫忙，結果他不走了，怎麼辦？」最後回來對。</p>"""},

{"html": """<div class="eyebrow">一 · 那塊地</div>
 <h2>四面都是山的地方</h2>
 <div class="art wide"><div class="txt">
   <ul class="pts">
     <li>益州就是今天的四川，<b>四面被高山圍住</b></li>
     <li>進出只有幾條路，最有名的一條叫<b>劍門關</b></li>
     <li>裡面土地很肥，<b>自己就養得活自己</b></li>
   </ul>
   <div class="callout">易守難攻，糧食充足——<br><b>隆中對說的第二塊地，就是這裡。</b></div>
 </div>
 ${mp("jianmen","劍門關","進四川最重要的那道關")}</div>""",
 "note": """<p>照片要指給孩子看：<b>路就在兩片絕壁中間</b>。一夫當關萬夫莫開就是講這種地方。</p>"""},

{"html": """<div class="eyebrow">二 · 那個守不住的人</div>
 <h2>劉璋自己請人進來</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>北邊的<b>張魯</b>占著漢中，一直威脅四川</li>
     <li>又聽說曹操要來打，劉璋很害怕</li>
     <li>有人出主意：<b>請劉備進來幫忙打張魯</b>——他也姓劉，是自己人</li>
   </ul>
   <div class="callout">劉璋答應了。<br><b>他親自出城去迎接劉備。</b></div>
 </div>
 <div class="cast tight">${ph("ehon_011_001","江戶時代畫的三國","《繪本通俗三國志》插圖")}</div></div>""",
 "note": """<p>這一頁就是開場那個問題的答案：<b>他自己請人進來的。</b></p>
 <p class="ask">問：「你覺得劉備會乖乖幫他打完就走嗎？」</p>"""},

{"html": """<div class="eyebrow">三 · 帶地圖出門的人</div>
 <h2>張松：把四川的地形圖送出去</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>劉璋的官員<b>張松</b>本來想把四川獻給曹操</li>
     <li>他去見曹操，<b>曹操嫌他長得醜、態度傲慢，沒理他</b></li>
     <li>他一氣之下轉頭去找劉備——<b>把四川的地形圖給了他</b></li>
   </ul>
   <div class="callout">一張地圖，<br><b>決定了一個國家的命運。</b></div>
 </div>
 <div class="cast tight">${im("map","四川地形圖")}${im("scroll","獻圖")}</div></div>""",
 "note": """<p>「因為看不起一個人而失去一整塊地」——這一課很好講。</p>
 <p class="ask">問：「曹操做錯了什麼？」（以貌取人）</p>"""},

{"html": """<div class="eyebrow">四 · 另一個聰明人</div>
 <h2>龐統：和諸葛亮齊名的人</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>當年水鏡先生說：<b>「臥龍、鳳雛，得一可安天下。」</b></li>
     <li>臥龍是諸葛亮，<b>鳳雛就是龐統</b></li>
     <li>他長得不好看，一開始也不被重用，後來成了劉備入川的軍師</li>
   </ul>
   <div class="callout">諸葛亮留守荊州，<br><b>龐統跟著劉備進四川。</b></div>
 </div>
 <div class="cast tight">${ph("pangtong","龐統","鳳雛")}</div></div>""",
 "note": """<p>「得一可安天下」孩子聽過，<b>但很多人不知道鳳雛是誰</b>。</p>
 <p>再一次出現「以貌取人」——<b>這一回出現兩次。</b></p>"""},

{"html": """<div class="eyebrow">五 · 翻臉</div>
 <h2>幫忙變成開打</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>劉備進川後<b>沒有馬上打張魯</b>，反而到處收買人心</li>
     <li>一年後兩邊翻臉，劉備<b>回頭打劉璋</b></li>
     <li>張松的事情敗露，被劉璋<b>處死</b></li>
   </ul>
   <div class="callout">🚩 這一段<b>劉備做得不光彩</b>。<br>他自己也知道——史書說他事後<b>很不安</b>。</div>
 </div>
 <div class="cast tight">${ph("liuzhang","劉璋","請人進來的那個人")}</div></div>""",
 "note": """<p>🚩 <b>不要幫劉備找理由。</b>這是整套課第三次問「好人壞人」（第五回曹操、第七回徐州、這裡）。</p>
 <p class="ask">問：「劉備是好人嗎？」——一樣不要給答案。</p>"""},

{"html": """<div class="eyebrow">六 · 那個山坡</div>
 <h2>落鳳坡</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>進軍途中要通過一條狹窄的山路</li>
     <li>龐統走在前面，<b>被埋伏的箭射中</b></li>
     <li>死的時候<b>三十六歲</b></li>
   </ul>
   <div class="callout">那個地方後來叫<b>落鳳坡</b>——<br>鳳雛死在那裡。</div>
   <p class="foot">劉備哭了很久。他只好把諸葛亮、張飛、趙雲都從荊州調進來。</p>
 </div>
 <div class="cast tight">${ph("zhangren","張任","射死龐統的那一方")}</div></div>""",
 "note": """<p>「落鳳坡」這個地名是小說安排的（真實地名不確定），<b>但龐統中箭而死是真的</b>。</p>
 <p>🚩 這一調兵<b>種下第十三回的禍根</b>：荊州從此只剩關羽一個人守。</p>"""},

{"html": """<div class="eyebrow">七 · 老將</div>
 <h2>張飛也有動腦的時候</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>張飛帶兵入川，遇到老將<b>嚴顏</b>死守江州</li>
     <li>攻破後嚴顏被綁來，大罵：<b>「我們這裡只有斷頭將軍，沒有投降將軍！」</b></li>
     <li>張飛不但沒殺他，<b>親自替他鬆綁，請他上座</b></li>
   </ul>
   <div class="callout">嚴顏投降了。<br>接下來一路上的關卡，<b>都是他去勸降的。</b></div>
 </div>
 <div class="cast tight">${ph("yanyan","嚴顏","斷頭將軍")}</div></div>""",
 "note": """<p>孩子印象中的張飛只會吼。<b>這一頁要翻案：他也會敬重對手。</b></p>
 <p>和第七回陳宮、第九回關羽放在一起——<b>三國的人很重視「不投降」這件事。</b></p>"""},

{"html": """<div class="eyebrow">八 · 成都</div>
 <h2>圍了幾十天，城開了</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>諸葛亮、張飛、趙雲三路會師成都城下</li>
     <li>城裡還有<b>三萬精兵、一年的糧</b>，可以再撐</li>
     <li>可是劉璋說：<b>「打了三年，死的都是我的百姓，我不忍心。」</b></li>
   </ul>
   <div class="callout">他自己開城投降。<br>史書說那天<b>城裡的人都哭了</b>。</div>
 </div>
 <div class="cast tight">${ph("madai","馬岱","馬超的堂弟，一起歸順")}</div></div>""",
 "note": """<p>劉璋這句話要唸出來。<b>他不會打仗，但這一句話是這一回最有品的一句。</b></p>
 <p class="ask">問：「他是懦弱還是善良？」</p>"""},

{"html": """<div class="eyebrow">九 · 加入的人</div>
 <h2>馬超來了，成都就開了</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>第十一回被曹操打散的<b>馬超</b>，輾轉來投靠劉備</li>
     <li>劉備讓他直接帶兵到成都城下</li>
     <li>城裡一看見馬超的旗號，<b>士氣就垮了</b>——他太有名了</li>
   </ul>
   <div class="callout">有時候一個人的<b>名字</b>，<br>比一萬個兵有用。</div>
 </div>
 <div class="cast tight">${ph("ehon_011_002","江戶時代畫的三國","《繪本通俗三國志》插圖")}</div></div>""",
 "note": """<p>接第十一回的馬超線。<b>他從報父仇的人，變成劉備的大將。</b></p>"""},

{"html": """<div class="eyebrow">十 · 北邊也在動</div>
 <h2>曹操先拿下漢中</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>劉備剛拿下成都，曹操就<b>去打漢中的張魯</b></li>
     <li>張魯投降。漢中在四川<b>正上方</b>，等於刀架在脖子上</li>
     <li>有人勸曹操趁勝直接打四川，<b>他沒有</b></li>
   </ul>
   <div class="callout">他說了一句很有名的話：<br><b>「人就是不知足——得到隴，又想要蜀。」</b></div>
   <p class="foot">「得隴望蜀」這句成語就是從這裡來的。</p>
 </div>
 <div class="cast tight">${im("mountain","漢中")}${im("crown")}</div></div>""",
 "note": """<p>成語出處可以寫黑板。<b>而且曹操是用它來說「我不要那麼貪心」——和現在的用法不太一樣。</b></p>
 <p class="ask">問：「他不打，是謙虛還是打不動？」（他那年六十一歲，兵也累了）</p>"""},

{"html": """<div class="eyebrow">十一 · 拚漢中</div>
 <h2>兩邊都拿出全部</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>劉備知道漢中不拿下來，四川就永遠不安全</li>
     <li>他<b>親自帶兵</b>去打，諸葛亮在後方<b>男人當兵、女人運糧</b></li>
     <li>打了整整<b>兩年</b></li>
   </ul>
   <div class="callout">這是劉備一生中<b>唯一一次</b><br>正面打贏曹操。</div>
 </div>
 <div class="cast tight">${ph("jianmenmt","蜀道","山路就是這樣")}</div></div>""",
 "note": """<p>「男人當兵、女人運糧」是史書寫的，<b>說明這一戰有多拚</b>。</p>
 <p>「唯一一次打贏曹操」要講重——從第五回到現在，<b>三十年了。</b></p>"""},

{"html": """<div class="eyebrow">十二 · 定軍山</div>
 <h2>老黃忠斬了夏侯淵</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>曹操的大將<b>夏侯淵</b>守定軍山</li>
     <li>黃忠占住高處，<b>等到對方最鬆懈的時候衝下去</b></li>
     <li>一刀把夏侯淵斬了——那年黃忠<b>七十歲左右</b></li>
   </ul>
   <div class="callout">曹操聽到消息親自趕來，<br><b>可是已經來不及了。</b></div>
 </div>
 <div class="cast tight">${ph("xiahouyuan","夏侯淵","曹操的大將")}</div></div>""",
 "note": """<p>「七十歲還在第一線砍人」——孩子會很興奮。<b>這是老黃忠最有名的一戰。</b></p>
 <p>京劇有一齣戲就叫《定軍山》，是中國第一部電影拍的內容。</p>"""},

{"html": """<div class="eyebrow">十三 · 雞肋</div>
 <h2>兩個字就退兵了</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>曹操想守守不住，想退又不甘心</li>
     <li>那天晚上口令是<b>「雞肋」</b>——雞的肋骨，<b>沒有肉但丟了可惜</b></li>
     <li>主簿<b>楊修</b>聽到就開始收行李：他說主公要退兵了</li>
   </ul>
   <div class="callout">曹操真的退兵了，<br>但他<b>把楊修殺了</b>——理由是動搖軍心。</div>
 </div>
 <div class="cast tight">${ph("yangxiu","楊修","猜對了，然後死了")}</div></div>""",
 "note": """<p>孩子會問「猜對為什麼還要殺」。答：<b>因為被看穿的人會不高興</b>——和第八回煮酒論英雄那一頁對照。</p>
 <p class="ask">問：「聰明可以表現出來嗎？」</p>"""},

{"html": """<div class="eyebrow">十四 · 漢中王</div>
 <h2>五十八歲，他戴上了王冠</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>拿下漢中後，部下推舉劉備當<b>漢中王</b></li>
     <li>從第三回賣草鞋的年輕人，到現在<b>三十五年</b></li>
     <li>他派人把印信送回許都，<b>形式上還是漢朝的臣子</b></li>
   </ul>
   <div class="callout">第一回那句話還記得嗎——<br><b>他小時候指著屋前的大樹說：我以後要坐那種有蓋子的車。</b></div>
 </div>
 <div class="cast tight">${ph("ehon_012_001","江戶時代畫的三國","《繪本通俗三國志》插圖")}</div></div>""",
 "note": """<p><b>全套課最該讓孩子高興的一頁。</b>翻回第三回那個賣草鞋的畫面，落差才出得來。</p>
 <p>三十五年——<b>比孩子的年紀大好幾倍。</b>可以換算給他們聽。</p>"""},

{"html": """<div class="eyebrow">十五 · 五個人</div>
 <h2>五虎將</h2>
 <div class="cast tight">
   ${cf(chr({robe:"#4F7460",hat:"jin",beard:"long",prop:"dao"}),"關羽","鎮守荊州")}
   ${cf(chr({robe:"#3C3630",hat:"wu",beard:"long",fat:1,prop:"spear"}),"張飛","鎮守閬中")}
   ${cf(chr({robe:"#B8BEC2",hat:"wu",beard:"mo",prop:"spear"}),"馬超","西涼來的")}
   ${cf(chr({robe:"#9C7C24",hat:"wu",beard:"long",prop:"dao"}),"黃忠","定軍山那位")}
   ${cf(chr({robe:"#DDD8CB",hat:"wu",prop:"spear"}),"趙雲","長坂坡那位")}
 </div>
 <div class="callout">⚠︎ 正史裡<b>沒有「五虎將」這個說法</b>——那是小說把五個人的傳記放在同一卷，後人取的名字。</div>""",
 "note": """<p>孩子多半以為五虎將是官方封號。<b>破這個梗效果很好。</b></p>
 <p>順便提：關羽聽說馬超來了很不服氣，寫信問諸葛亮「馬超比得上我嗎」。<b>他很在意排名。</b>（第十三回會接）</p>"""},

{"html": """<div class="eyebrow">十五之二 · 守荊州的那個人</div>
 <h2>荊州只剩他一個</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>諸葛亮、張飛、趙雲<b>都調進四川了</b>（第六頁龐統一死就調的）</li>
     <li>荊州剩下<b>關羽一個人</b>總管</li>
     <li>他要同時面對<b>北邊的曹操</b>和<b>東邊的孫權</b></li>
   </ul>
   <div class="callout">一個人，守一塊<b>借來的地</b>，<br><b>夾在兩個大國中間。</b></div>
 </div>
 <div class="cast tight">${ph("guanyuhorse","關羽","塑像")}</div></div>""",
 "note": """<p>🚩 <b>這一頁是第十三回的引信</b>，三個條件要一條一條講：人少、地是借的、兩面受敵。</p>
 <p>回頭指第六頁（調兵）和第十一回（借荊州）。<b>兩個伏筆在這裡合起來。</b></p>"""},

{"html": """<div class="eyebrow">十六 · 隆中對走到哪了</div>
 <h2>兩塊地都拿到了</h2>
 <div class="tier">
   <div><span class="lbl">第一步</span><span>✅ 取荊州——第十一回拿到（用借的）</span></div>
   <div><span class="lbl">第二步</span><span>✅ 取益州——這一回拿到</span></div>
   <div><span class="lbl">第三步</span><span>⬜ 等機會，<b>兩路一起北伐</b></span></div>
 </div>
 <div class="callout">十二年前那張地圖，<br><b>兩步走完了。</b></div>
 <p class="foot">可是第一塊地是「借」的，而且只剩一個人在守。</p>""",
 "note": """<p>回頭指第十回的隆中對。<b>這是整套課計畫進度最好的一刻。</b></p>
 <p>最後那句 foot 是<b>引信</b>，不要多解釋，留著下一回炸。</p>"""},

{"html": """<div class="eyebrow">十七 · 這一回的話</div>
 <h2>最好的八年</h2>
 <div class="tl">
   <div><span class="yr">211</span><span>被請進四川</span><span class="ago">五十歲</span></div>
   <div><span class="yr">214</span><span>拿下成都</span><span class="ago">五十三歲</span></div>
   <div><span class="yr">219</span><span>漢中大勝，唯一一次正面贏曹操</span><span class="ago">五十八歲</span></div>
   <div class="now"><span class="yr">219</span><span>當上漢中王</span><span class="ago">人生最高點</span></div>
 </div>
 <div class="callout">從賣草鞋到戴王冠，<b>三十五年</b>。<br>而距離他失去一切，<b>只剩幾個月。</b></div>""",
 "note": """<p>最後一句<b>一定要講</b>，但講完就翻頁，不要解釋——下一回開場就是麥城。</p>"""},

{"html": """<div class="eyebrow">最後</div>
 <h2>今天哪些是編的</h2>
 <div class="cols">
   <div class="card"><h3>編的</h3><p>
     <b>五虎將</b>：正史沒有這個封號<br><br>
     <b>落鳳坡</b>：地名是小說安排的<br><br>
     <b>張松獻圖的細節</b>：獻圖是真的，過程被加了很多戲<br><br>
     <b>楊修猜雞肋</b>：猜中是真的，但他被殺另有原因</p></div>
   <div class="card"><h3>真的</h3><p>
     <b>劉璋自己請劉備入川</b>：真的<br><br>
     <b>龐統中箭而死、三十六歲</b>：真的<br><br>
     <b>張飛義釋嚴顏</b>：真的<br><br>
     <b>劉璋不忍百姓受苦而開城</b>：真的<br><br>
     <b>黃忠定軍山斬夏侯淵</b>：真的<br><br>
     <b>「得隴望蜀」</b>：真的，曹操說的</p></div>
 </div>
 <div class="callout">這一回最該記住的不是打仗，<br>是那句<b>「請神容易送神難」</b>——<br>劉璋<b>自己把人請進來的</b>。</div>""",
 "note": """<p>固定收尾頁。回到開場那個問題。</p>"""},
]
