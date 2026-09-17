# -*- coding: utf-8 -*-
"""第十四回　漢朝結束了（220–221）

「招牌」這條線在這一回收尾：曹操忍了一輩子沒拆，他兒子上台就拆了。
四百年的漢朝到此為止。
"""

TITLE = "三國第十四回"
MARK = "三國演義 · 第十四回"
SUB = "漢朝結束了"

SLIDES = [
{"cover": True,
 "html": """<div class="art">
   <div class="txt">
     <div class="eyebrow">第十四回</div>
     <h1>四百年，<em>到此為止</em></h1>
     <p class="sub">那塊招牌，第一回就掛上了。<br>這一回，有人把它拆下來戴在自己頭上。</p>
     <div class="meta">
       <div><dt>時間</dt><dd>西元 220–221 年</dd></div>
       <div><dt>這一回</dt><dd>曹丕篡漢與劉備稱帝</dd></div>
       <div><dt>今天要弄懂</dt><dd>一個朝代怎麼「結束」</dd></div>
     </div>
     <p class="credit">版畫與繡像取自維基共享資源，出處見上方「圖片來源」</p>
   </div>
   <div class="cast">
     ${cf(chr({robe:"#2E4A63",hat:"mian",cuff:"#1A2F40",beard:"mo"}),"曹丕","三十四歲")}
     ${im("crown","皇帝")}
   </div>
 </div>""",
 "note": """<p>這一回幾乎沒有打仗，<b>但它是整套課最重要的一回</b>——「招牌」的故事在這裡結束。</p>
 <p class="ask">開場問：「一間店換了老闆，還是同一間店嗎？」最後一頁回來對。</p>"""},

{"html": """<div class="eyebrow">一 · 一個月後</div>
 <h2>關羽死後不久，曹操也走了</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>西元 <b>220 年正月</b>，曹操病死在洛陽，<b>六十六歲</b></li>
     <li>他打了三十多年仗，掌權二十四年</li>
     <li>從<b>第五回</b>那個帶刀去見董卓的小官，到現在</li>
   </ul>
   <div class="callout">而他<b>一輩子都沒有當皇帝</b>。</div>
 </div>
 <div class="cast tight">${ph("ehon_014_003","江戶時代畫的三國","《繪本通俗三國志》插圖")}</div></div>""",
 "note": """<p>翻回第五回那個三十五歲的曹操。<b>孩子跟著他走了十回。</b></p>
 <p class="ask">問：「他有能力當皇帝，為什麼不當？」——先不要給答案，下一頁講。</p>"""},

{"html": """<div class="eyebrow">二 · 他為什麼不稱帝</div>
 <h2>「我當周文王就好」</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>有人勸他稱帝，他說：<b>「如果天命在我，我就當周文王吧。」</b></li>
     <li>周文王一生沒有稱王，是<b>他兒子</b>建立了周朝</li>
     <li>意思很清楚：<b>這件事留給兒子做。</b></li>
   </ul>
   <div class="callout">第八回那一頁還記得嗎——<br><b>忍得住不把招牌戴在頭上的人，才用得久。</b></div>
 </div>
 <div class="cast tight">${im("crown")}${im("scroll","留給兒子")}</div></div>""",
 "note": """<p>回頭指第八回「袁術 vs 曹操」那一頁。<b>這是同一課的最後一段。</b></p>
 <p class="ask">問：「他是不想，還是不敢？」（兩個都有）</p>"""},

{"html": """<div class="eyebrow">三 · 留下來的遺囑</div>
 <h2>他交代的是香和鞋子</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>史書留下他的遺令：喪事要<b>簡單</b>，不要放金玉珠寶</li>
     <li>他交代把剩下的<b>香分給幾位夫人</b></li>
     <li>又說：住在銅雀台的女眷<b>可以學織鞋，自己賺錢養活自己</b></li>
   </ul>
   <div class="callout">一個打了一輩子仗的人，<br><b>最後在交代鞋子怎麼賣。</b></div>
 </div>
 <div class="cast tight">${ph("ladyzhen","甄夫人","曹丕的妻子")}${im("robe","分香賣履")}</div></div>""",
 "note": """<p>「分香賣履」這個典故很有名。有人笑他婆婆媽媽，<b>也有人說這才是真實的人。</b></p>
 <p class="ask">問：「你覺得這樣的遺言，是小氣還是溫柔？」</p>"""},

{"html": """<div class="eyebrow">四 · 兄弟</div>
 <h2>七步詩</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>曹操有個很會寫文章的兒子叫<b>曹植</b>，曾經差點被選為繼承人</li>
     <li>曹丕即位後，命令他<b>走七步之內作一首詩</b>，作不出來就處死</li>
     <li>曹植走了幾步就唸出來了</li>
   </ul>
   <div class="callout"><b>「本是同根生，相煎何太急？」</b><br>——我們是同一個根長出來的，<br>何必這樣逼我？</div>
 </div>
 <div class="cast tight">${ph("caozhi","曹植","七步成詩")}</div></div>""",
 "note": """<p>📄 這首詩<b>整首唸出來</b>：煮豆燃豆萁，豆在釜中泣。本是同根生，相煎何太急。</p>
 <p>⚠︎ 七步詩<b>最早見於《世說新語》，不是正史</b>。但兄弟相逼是真的。</p>"""},

{"html": """<div class="eyebrow">五 · 那場典禮</div>
 <h2>十月，皇帝「讓位」了</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>曹丕即位當年十月，大臣們<b>三次上書</b>請漢獻帝讓位</li>
     <li>獻帝<b>三次下詔</b>要讓，曹丕<b>三次推辭</b>，第四次才接受</li>
     <li>這套流程叫<b>禪讓</b>——表面上是自願的</li>
   </ul>
   <div class="callout">每個人都知道是怎麼回事，<br><b>但每個人都要照著演完。</b></div>
 </div>
 <div class="cast tight">${ph("caopi2","曹丕","傳唐人畫")}</div></div>""",
 "note": """<p>「三讓三辭」這套儀式要講清楚：<b>形式很重要，因為它讓事情「看起來合法」。</b></p>
 <p class="ask">問：「大家都知道是假的，為什麼還要演？」</p>"""},

{"html": """<div class="eyebrow">六 · 走下台階</div>
 <h2>四百年，在這一天結束</h2>
 <div class="tl">
   <div><span class="yr">前202</span><span>劉邦建立漢朝</span><span class="ago">開始</span></div>
   <div><span class="yr">9</span><span>王莽篡漢，中斷十五年</span><span class="ago"></span></div>
   <div><span class="yr">25</span><span>光武帝劉秀重建，叫東漢</span><span class="ago"></span></div>
   <div class="now"><span class="yr">220</span><span>漢獻帝讓位給曹丕</span><span class="ago">結束</span></div>
 </div>
 <div class="callout">加起來<b>四百零五年</b>。<br>第一回說的那個「漢」，到這一天沒有了。</div>""",
 "note": """<p>回頭指第一回「那時候的國家叫漢」。<b>整套課的第一頁，在這裡收掉。</b></p>
 <p>四百年有多長？可以換算：<b>比台灣有文字記載的歷史還長。</b></p>"""},

{"html": """<div class="eyebrow">七 · 他後來呢</div>
 <h2>獻帝活得比曹丕久</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>讓位後他被封為<b>山陽公</b>，可以繼續用漢朝的禮儀</li>
     <li>他在封地學醫，<b>替百姓看病不收錢</b>，當地人很喜歡他</li>
     <li>他活到<b>西元 234 年</b>——比曹丕還多活八年</li>
   </ul>
   <div class="callout">第四回他<b>九歲</b>被董卓立為皇帝，<br>這一年他<b>四十歲</b>，終於不用當招牌了。</div>
 </div>
 <div class="cast tight">${cf(chr({robe:"#8A7B52",hat:"jin",beard:"mo"}),"劉協","不再是皇帝以後")}${im("tea","替人看病")}</div></div>""",
 "note": """<p>🚨 第四回講稿說「他會活到第十四回，當了三十一年傀儡」——<b>就是這一頁。</b></p>
 <p class="ask">問：「不當皇帝以後，他過得比較好還是比較差？」</p>"""},

{"html": """<div class="eyebrow">八 · 那個謀士的結局</div>
 <h2>荀彧為什麼死</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>第八回勸曹操去接皇帝、第九回寫信留住曹操的<b>荀彧</b></li>
     <li>他一生幫曹操，<b>可是他真心想的是恢復漢朝</b></li>
     <li>曹操要進爵魏公時他反對。不久後<b>曹操送來一個空的食盒</b></li>
   </ul>
   <div class="callout">盒子裡什麼都沒有。<br>荀彧看懂了——<b>沒有東西給你吃了。</b><br>他自盡，五十歲。</div>
 </div>
 <div class="cast tight">${ph("xunyu2","荀彧","跟了曹操二十年")}</div></div>""",
 "note": """<p>🚩 <b>這一頁很難，但很值得講。</b>荀彧幫曹操是為了救漢朝，結果曹操成了取代漢朝的人。</p>
 <p class="ask">問：「他到底幫錯了，還是幫對了？」</p>"""},

{"html": """<div class="eyebrow">九 · 消息傳到成都</div>
 <h2>傳成了「皇帝被殺了」</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>四川離中原很遠，消息<b>走樣了</b></li>
     <li>成都聽到的版本是：<b>漢獻帝已經被害</b></li>
     <li>劉備<b>穿上孝服，替皇帝辦了喪事</b></li>
   </ul>
   <div class="callout">他哭的那個人，<br><b>其實還活著，而且會再活十四年。</b></div>
 </div>
 <div class="cast tight">${im("envelope","走樣的消息")}${im("rain","發喪")}</div></div>""",
 "note": """<p>這一頁講<b>「消息會走樣」</b>——古代沒有電話，一千公里的消息可以完全變樣。</p>
 <p class="ask">問：「如果劉備知道獻帝還活著，他還會稱帝嗎？」</p>"""},

{"html": """<div class="eyebrow">十 · 他也稱帝了</div>
 <h2>221 年，成都</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>部下勸了很多次，劉備<b>六十一歲</b>那年即位</li>
     <li>國號還是叫<b>「漢」</b>——他說自己是繼承，不是新開一國</li>
     <li>史書為了區分，把它叫做<b>蜀漢</b></li>
   </ul>
   <div class="callout">曹丕說：漢朝結束了，換我。<br>劉備說：<b>漢朝沒有結束，在我這裡。</b></div>
 </div>
 <div class="cast tight">${ph("liubei4","劉備","傳唐人畫")}</div></div>""",
 "note": """<p>兩句對照要唸出來。<b>「誰才是正統」這個問題，吵了一千多年。</b></p>
 <p class="ask">問：「你覺得誰說得比較有道理？」</p>"""},

{"html": """<div class="eyebrow">十一 · 第三個人在等</div>
 <h2>孫權兩邊都稱臣</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>孫權剛殺了關羽，<b>知道劉備一定會來報仇</b></li>
     <li>他做了一件很難堪但很聰明的事：<b>向曹丕稱臣</b></li>
     <li>曹丕封他為<b>吳王</b>——這樣他就不會腹背受敵</li>
   </ul>
   <div class="callout">三個人裡面，<br><b>他是最能忍的那一個。</b></div>
 </div>
 <div class="cast tight">${ph("sunquan2","孫權","歷代名臣像冊")}</div></div>""",
 "note": """<p>孫權<b>八年後（229）才稱帝</b>，是三個人裡最晚的。<b>能忍是他最大的本事。</b></p>
 <p class="ask">問：「向仇人低頭，很丟臉嗎？」</p>"""},

{"html": """<div class="eyebrow">十二 · 三個國家</div>
 <h2>正式的名字和年號</h2>
 <div class="three">
   <div class="wei">${chr({robe:"#EFE6D4",hat:"mian",cuff:"#8A6E18",beard:"mo"})}<div class="n">魏</div><div class="who">曹丕　220 年</div><div class="where">洛陽・最大</div></div>
   <div class="shu">${chr({robe:"#EFE6D4",hat:"mian",cuff:"#6E2418",beard:"mo"})}<div class="n">漢</div><div class="who">劉備　221 年</div><div class="where">成都・最小</div></div>
   <div class="wu">${chr({robe:"#EFE6D4",hat:"mian",cuff:"#2A4A3A"})}<div class="n">吳</div><div class="who">孫權　229 年</div><div class="where">建業・靠長江</div></div>
 </div>
 <div class="callout">第一回地圖上的<b>藍、紅、綠</b>，到這一回<b>都有了正式的名字</b>。</div>""",
 "note": """<p>三色從第一回埋到現在。<b>整整十四回，終於名正言順。</b></p>
 <p>提醒：蜀漢自己叫「漢」不叫「蜀」，<b>「蜀」是別人叫的。</b></p>"""},

{"html": """<div class="eyebrow">十二之二 · 新皇帝做的第一件事</div>
 <h2>他改了「怎麼選官」</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>曹丕上台後定了一套制度：每個郡設一個<b>中正官</b>，把當地的人<b>分成九等</b></li>
     <li>等第高的做大官，等第低的做小官——叫<b>九品中正制</b></li>
     <li>本意是要公平，可是評等的人自己就是世家大族</li>
   </ul>
   <div class="callout">結果幾十年後變成：<br><b>「上品沒有窮人家，下品沒有大族。」</b></div>
   <p class="foot">第一回說過「那時候當官不用考試」——這套制度又用了<b>三百多年</b>，到隋朝才被科舉取代。</p>
 </div>
 <div class="cast tight">${im("scroll","分成九等")}${im("books","一直用到隋朝")}</div></div>""",
 "note": """<p>回頭指第一回「當官不用考試」和第十一回曹操的「唯才是舉」。<b>爸爸想打破的東西，兒子把它制度化了。</b></p>
 <p class="ask">問：「由大人物來評分，會公平嗎？」</p>"""},

{"html": """<div class="eyebrow">十三 · 一個人的三十年</div>
 <h2>那塊招牌的旅程</h2>
 <div class="tier">
   <div><span class="lbl">189</span><span>董卓立獻帝——<b>招牌掛上去</b>（第四回）</span></div>
   <div><span class="lbl">196</span><span>曹操迎天子——<b>招牌被用起來</b>（第八回）</span></div>
   <div><span class="lbl">197</span><span>袁術自己稱帝——<b>把招牌丟了，兩年就完</b>（第七回）</span></div>
   <div><span class="lbl">220</span><span>曹丕受禪——<b>招牌被拆下來戴在頭上</b>（這一回）</span></div>
 </div>
 <div class="callout">整套課用了<b>十四回</b>講這一件事。<br>「招牌」這個詞，到這裡<b>功成身退</b>。</div>""",
 "note": """<p>四行一行一行指過去。<b>這是整套課最重要的一條線，到這裡收完。</b></p>
 <p>後面六回不會再用「招牌」這個詞了。</p>"""},

{"html": """<div class="eyebrow">十四 · 那個問題</div>
 <h2>曹操到底是好人還是壞人</h2>
 <div class="cols">
   <div class="card"><h3>他做過的壞事</h3><p>殺呂伯奢一家（第五回）<br>報父仇傷害徐州百姓（第七回）<br>殺孔融、殺楊修（第八、十二回）<br>逼死荀彧（這一回）</p></div>
   <div class="card"><h3>他做過的好事</h3><p>屯田讓幾十萬人吃飽（第八回）<br>燒掉通敵的信（第九回）<br>唯才是舉（第十一回）<br>厚葬敵人關羽（第十三回）</p></div>
 </div>
 <div class="callout">第五回問過、第七回問過、第十二回也問過。<br><b>現在你有答案了嗎？</b></div>""",
 "note": """<p>🚩 <b>整套課問了四次，這一頁是結算。</b>還是不要給答案，讓孩子自己說。</p>
 <p>提醒他們：<b>同一個人可以兩樣都做。</b>這才是真實的人。</p>"""},

{"html": """<div class="eyebrow">十五 · 這一年發生了什麼</div>
 <h2>219 到 221，三年換了一個世界</h2>
 <div class="tl">
   <div><span class="yr">219</span><span>關羽死</span><span class="ago">第十三回</span></div>
   <div><span class="yr">220</span><span>曹操死</span><span class="ago">正月</span></div>
   <div><span class="yr">220</span><span>漢朝結束</span><span class="ago">十月</span></div>
   <div><span class="yr">221</span><span>劉備稱帝</span><span class="ago">四月</span></div>
   <div class="now"><span class="yr">221</span><span>劉備決定伐吳</span><span class="ago">下一回</span></div>
 </div>
 <div class="callout">三年之內，<br><b>舊時代的人一個一個走了。</b></div>""",
 "note": """<p>五行指過去。最後一行是<b>下一回的開場</b>。</p>"""},

{"html": """<div class="eyebrow">十六 · 剩下誰</div>
 <h2>第一回那些人，還剩幾個</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>董卓、呂布、袁紹、袁術、孫策、周瑜、關羽、曹操——<b>都走了</b></li>
     <li>還在的：<b>劉備六十一歲、孫權四十歲、諸葛亮四十一歲</b></li>
     <li>剛上場的：曹丕三十五歲、陸遜三十九歲、司馬懿四十三歲</li>
   </ul>
   <div class="callout">故事還沒完，<br><b>但演員換了一批。</b></div>
 </div>
 <div class="cast tight">${ph("sunquan3","孫權","歷代名臣像冊，另一幅")}</div></div>""",
 "note": """<p>名字一個一個唸過去，<b>讓孩子感覺到時間真的過去了</b>。</p>
 <p>司馬懿這個名字要特別提——<b>他會活到第十九回，而且贏到最後。</b></p>"""},

{"html": """<div class="eyebrow">十七 · 這一回的話</div>
 <h2>一個朝代是怎麼結束的</h2>
 <div class="tier">
   <div><span class="lbl">不是</span><span>被外國打敗</span></div>
   <div><span class="lbl">不是</span><span>被起義推翻</span></div>
   <div><span class="lbl">而是</span><span><b>一場人人都知道是假的典禮</b></span></div>
 </div>
 <div class="callout">四百年的漢朝，<br>結束在<b>一個下午的儀式</b>裡。</div>""",
 "note": """<p>回到開場「換了老闆還是同一間店嗎」的問題。</p>
 <p>這一頁講完停一下再翻，<b>讓孩子消化一下。</b></p>"""},

{"html": """<div class="eyebrow">最後</div>
 <h2>今天哪些是編的</h2>
 <div class="cols">
   <div class="card"><h3>編的</h3><p>
     <b>七步詩</b>：出自《世說新語》，不是正史<br><br>
     <b>曹操遺命七十二疑塚</b>：後人傳說，考古已找到他的墓<br><br>
     <b>曹丕逼殺曹彰</b>：小說寫的，正史沒有</p></div>
   <div class="card"><h3>真的</h3><p>
     <b>曹操「我為周文王」</b>：真的<br><br>
     <b>分香賣履的遺令</b>：真的<br><br>
     <b>三讓三辭的禪讓儀式</b>：真的<br><br>
     <b>獻帝當山陽公、行醫、活到 234</b>：真的<br><br>
     <b>荀彧與空食盒</b>：食盒出自裴松之注，自盡是真的<br><br>
     <b>孫權向曹丕稱臣</b>：真的</p></div>
 </div>
 <div class="callout">小說最想讓你討厭曹丕，<br>可是真正決定漢朝命運的，<br><b>是第八回那個去接皇帝的人。</b></div>""",
 "note": """<p>固定收尾頁。最後那句把第八回和這一回接起來——<b>二十四年前就決定了。</b></p>"""},
]
