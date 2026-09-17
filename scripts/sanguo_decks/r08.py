# -*- coding: utf-8 -*-
"""第八回　把皇帝請回家（196）

「招牌」這個詞第三次出現，這次是正面用法。
第一回埋、第四回成立、這一回被人真正用起來。
"""

TITLE = "三國第八回"
MARK = "三國演義 · 第八回"
SUB = "把皇帝請回家"

SLIDES = [
{"cover": True,
 "html": """<div class="art">
   <div class="txt">
     <div class="eyebrow">第八回</div>
     <h1>把皇帝<em>請回家</em></h1>
     <p class="sub">所有人都覺得那是個累贅。<br>只有一個人看出那是一塊招牌。</p>
     <div class="meta">
       <div><dt>時間</dt><dd>西元 196 年，洛陽→許縣</dd></div>
       <div><dt>這一回</dt><dd>曹操迎天子</dd></div>
       <div><dt>今天要弄懂</dt><dd>「名義」為什麼有用</dd></div>
     </div>
     <p class="credit">版畫與繡像取自維基共享資源，出處見上方「圖片來源」</p>
   </div>
   <div class="cast">
     ${cf(chr({robe:"#C9A227",hat:"mian",cuff:"#8A6E18",small:1,sad:1}),"漢獻帝","十六歲")}
     ${im("scroll","蓋皇帝印的命令")}
   </div>
 </div>""",
 "note": """<p>這一回<b>幾乎沒有打仗</b>，是整套課裡最「用腦」的一回。</p>
 <p class="ask">開場問：「如果班長說的話跟老師說的話一樣，大家比較聽誰的？」最後回來對。</p>"""},

{"html": """<div class="eyebrow">一 · 那個小孩長大了</div>
 <h2>他已經被搶了七年</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>第四回董卓把他立為皇帝時，他<b>九歲</b></li>
     <li>董卓死後，他被李傕、郭汜<b>搶來搶去</b></li>
     <li>現在他<b>十六歲</b>，決定逃回洛陽</li>
   </ul>
   <div class="callout">他是皇帝，<br>可是他從來<b>沒有一天說了算</b>。</div>
 </div>
 <div class="cast tight">${ph("xiandi2","漢獻帝","清代繡像")}</div></div>""",
 "note": """<p>回頭數年份：189 立、196 逃，<b>整整七年</b>。孩子對「同一個人長大了」很有感覺。</p>"""},

{"html": """<div class="eyebrow">二 · 逃亡</div>
 <h2>一路上沒有東西吃</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>李傕、郭汜追上來，<b>在後面邊追邊打</b></li>
     <li>過黃河時船不夠，<b>爬上船的人手指被砍斷</b></li>
     <li>皇后身上的絹被士兵搶走，<b>宮女被留在岸上</b></li>
   </ul>
   <div class="callout">走了<b>一年</b>才到洛陽。<br>皇帝身邊，只剩下幾十個人。</div>
 </div>
 <div class="cast tight">${ph("ehon_004_003","江戶時代畫的三國","《繪本通俗三國志》插圖")}</div></div>""",
 "note": """<p>🚩 手指那一段是史書寫的，但<b>不要細講</b>。重點是：<b>當皇帝也可以慘成這樣。</b></p>"""},

{"html": """<div class="eyebrow">三 · 回到家</div>
 <h2>洛陽只剩斷牆</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>第四回董卓燒掉的洛陽，<b>六年來沒有人修</b></li>
     <li>皇宮沒有了，皇帝住在一個舊官署裡</li>
     <li>官員<b>在草叢裡上朝</b>，餓死的人就躺在旁邊</li>
   </ul>
   <div class="callout">尚書郎以下的官員<b>自己出去挖野菜</b>。<br>有人就這樣死在牆邊。</div>
 </div>
 <div class="cast tight">${cf(wall(),"洛陽","燒完六年了")}${im("grain","挖野菜")}</div></div>""",
 "note": """<p>接第四回那把火。<b>燒掉一座城的後果，六年後還在。</b>回頭指一下。</p>"""},

{"html": """<div class="eyebrow">四 · 沒有人去接</div>
 <h2>最大的那個人說：接來幹嘛</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>袁紹的謀士<b>沮授</b>勸他：把皇帝接來，以後發號施令名正言順</li>
     <li>可是另一派說：接來以後<b>什麼事都要先問他，很麻煩</b></li>
     <li>袁紹想了想，<b>沒有去</b></li>
   </ul>
   <div class="callout">當時天下最強的人，<br><b>覺得皇帝是個累贅。</b></div>
 </div>
 <div class="cast tight">${ph("jushou","沮授","勸袁紹去接皇帝")}</div></div>""",
 "note": """<p>這一頁是<b>整回的樞紐</b>。同一件事，兩個人看到完全不同的東西。</p>
 <p>沮授<b>第九回還會出現</b>——他還會勸袁紹一次，袁紹還是不聽。</p>
 <p class="ask">問：「你覺得誰對？」</p>"""},

{"html": """<div class="eyebrow">五 · 有人去了</div>
 <h2>曹操說：我去</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>曹操的謀士<b>荀彧</b>說了一句話：現在去接，<b>是天下人都會記得的事</b></li>
     <li>曹操馬上出兵洛陽</li>
     <li>他把皇帝接到自己的地盤<b>許縣</b>——從此那裡叫「許都」</li>
   </ul>
   <div class="callout">他做的第一件事，<br>是<b>讓皇帝吃飽飯</b>。</div>
 </div>
 <div class="cast tight">${ph("xunyu","荀彧","勸曹操去接皇帝")}</div></div>""",
 "note": """<p>荀彧是<b>曹操最重要的謀士</b>，第十四回他的結局會很讓人難過。先記住臉。</p>
 <p>「先讓皇帝吃飽飯」——這是曹操厲害的地方：<b>他知道要先做什麼。</b></p>"""},

{"html": """<div class="eyebrow">六 · 招牌</div>
 <h2>從此命令上都蓋著皇帝的印</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>曹操要打誰，就用<b>皇帝的名義</b>下令</li>
     <li>對方如果不聽，就變成<b>抗旨</b>——名義上是造反</li>
     <li>對方如果聽了，就等於<b>承認曹操說了算</b></li>
   </ul>
   <div class="callout">這就是後來那句話：<br><b>挾天子以令諸侯。</b></div>
   <p class="foot">「招牌」這個詞第一回埋、第四回成立，<b>這一回第三次</b>——這次是有人真的把它用起來了。</p>
 </div>
 <div class="cast tight">${ph("mirror2","蓋印","漢代銅鏡，出土文物")}${im("envelope","發出去的命令")}</div></div>""",
 "note": """<p>「招牌」第三次，整套課請固定用這個詞。回頭指第一回和第四回。</p>
 <p class="ask">問：「聽也不是、不聽也不是——那要怎麼辦？」（這就是別人的難處）</p>"""},

{"html": """<div class="eyebrow">七 · 另一件事</div>
 <h2>讓兵自己種田</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>那時候打仗最大的問題不是兵，是<b>糧</b></li>
     <li>有的軍隊吃桑葚、有的吃河蚌，<b>吃完就散了</b></li>
     <li>曹操把荒地分給流民和士兵種，收成官民分——叫<b>屯田</b></li>
   </ul>
   <div class="callout">第一年，許都附近就收到<b>一百萬斛</b>糧。</div>
   <p class="foot">第五回聯軍是怎麼散的？<b>糧沒了。</b>曹操記住了那一課。</p>
 </div>
 <div class="cast tight">${im("farmer","兵也種田")}${im("rice","一百萬斛")}</div></div>""",
 "note": """<p>接第五回「糧食沒了，人也散了」。<b>同樣一件事，別人吃過虧就算了，曹操把它變成制度。</b></p>"""},

{"html": """<div class="eyebrow">八 · 劉備在他家裡</div>
 <h2>兩個人一起吃飯</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>第七回結束時，劉備沒有地盤，投靠曹操</li>
     <li>曹操對他很好，<b>出門同車、坐下同席</b></li>
     <li>但劉備每天在後院<b>種菜</b>，什麼話都不說</li>
   </ul>
   <div class="callout">他在<b>裝作沒有志氣</b>。<br>（第六回王允也裝過——記得嗎？）</div>
 </div>
 <div class="cast tight">${cf(chr({robe:"#8C2F1E",hat:"ze",beard:"mo",prop:"hoe"}),"劉備","在後院種菜")}</div></div>""",
 "note": """<p>回頭指第六回王允「白天笑晚上哭」。<b>裝，是弱的人唯一的武器。</b></p>"""},

{"html": """<div class="eyebrow">九 · 那場酒</div>
 <h2>煮酒論英雄</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>有一天下雨，曹操請劉備喝酒，問他：<b>「你覺得現在誰算英雄？」</b></li>
     <li>劉備一個一個說：袁紹、袁術、劉表、孫策……</li>
     <li>曹操全部搖頭，最後用手指指他、再指自己：</li>
   </ul>
   <div class="callout"><b>「天下英雄，只有你和我兩個。」</b></div>
   <p class="foot">劉備手裡的筷子掉在地上。剛好打了一個雷，他說：「打雷嚇到了。」曹操就笑了。</p>
 </div>
 <div class="cast tight">${ph("ehon_005_003","江戶時代畫的三國","《繪本通俗三國志》插圖")}</div></div>""",
 "note": """<p><b>全回最有名的一頁。</b>「筷子掉了」那一秒要停住，問孩子：<b>他為什麼嚇成這樣？</b></p>
 <p>（因為被看穿了。曹操等於在說：我知道你在裝。）</p>
 <p>這一段史書有記，<b>是真的</b>——只是沒有打雷。</p>"""},

{"html": """<div class="eyebrow">十 · 腰帶裡的東西</div>
 <h2>衣帶詔</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>皇帝吃飽了，可是<b>什麼都不能決定</b></li>
     <li>他咬破手指寫了一道密令，<b>縫在腰帶裡</b>送出宮</li>
     <li>內容是：請大家一起除掉曹操</li>
   </ul>
   <div class="callout">拿到腰帶的人裡面，<b>有劉備</b>。</div>
 </div>
 <div class="cast tight">${ph("fuwan","伏完","皇后的父親，也在名單裡")}${im("dagger","藏在腰帶裡")}</div></div>""",
 "note": """<p>這一頁要讓孩子明白：<b>被當成招牌的人，自己也在想辦法。</b></p>
 <p class="ask">問：「皇帝為什麼要用咬破手指寫？」（因為他連筆墨都不敢用——會被看到）</p>"""},

{"html": """<div class="eyebrow">十一 · 一個醫生</div>
 <h2>下毒的那碗藥</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>參與的人裡有一位太醫叫<b>吉平</b></li>
     <li>曹操頭痛，他負責煎藥——他在藥裡下了毒</li>
     <li>事情敗露，他被抓起來，<b>一個名字都沒有說</b></li>
   </ul>
   <div class="callout">整件事被查出來，<br>參與的人<b>全家都被殺了</b>。</div>
 </div>
 <div class="cast tight">${ph("jiping","吉平","一個名字都沒說")}</div></div>""",
 "note": """<p>🚩 「全家被殺」點到就好。重點是<b>吉平沒有供出別人</b>——和第七回陳宮是同一種人。</p>"""},

{"html": """<div class="eyebrow">十二 · 他跑了</div>
 <h2>劉備找了個藉口離開</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>衣帶詔的事還沒爆發，劉備就請命<b>去攔袁術</b></li>
     <li>曹操答應了，等他走遠才後悔</li>
     <li>派人去追，<b>追不回來了</b></li>
   </ul>
   <div class="callout">曹操身邊的人說：<br><b>「放走劉備，等於放虎歸山。」</b></div>
   <p class="foot">這一次分開之後，兩個人再見面就是敵人了。</p>
 </div>
 <div class="cast tight">${ph("guojia","郭嘉","曹操最年輕的謀士")}${im("horse","走了就不回來")}</div></div>""",
 "note": """<p>郭嘉<b>第九回會大放異彩</b>，可惜他三十八歲就死了。先記住臉。</p>"""},

{"html": """<div class="eyebrow">十三 · 罵人的那個人</div>
 <h2>禰衡：脫光衣服擊鼓</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>有個很有才華的年輕人<b>禰衡</b>，看不起所有人</li>
     <li>曹操叫他來打鼓，他<b>當眾脫光衣服換裝</b>，把曹操羞辱一頓</li>
     <li>曹操沒殺他——<b>把他送給劉表</b></li>
   </ul>
   <div class="callout">劉表也受不了，<b>再把他送給黃祖</b>。<br>黃祖是個急脾氣，<b>當場把他殺了</b>。</div>
   <p class="foot">曹操聽到消息笑了：「借別人的刀。」</p>
 </div>
 <div class="cast tight">${ph("miheng","禰衡","二十六歲")}</div></div>""",
 "note": """<p>這一頁講<b>「不用自己動手」</b>——和第六回王允的離間是同一類思路。</p>
 <p class="ask">問：「曹操為什麼不自己殺他？」（殺了會被說容不下人）</p>"""},

{"html": """<div class="eyebrow">十四 · 還有人講骨氣</div>
 <h2>孔融：孔子的後代</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>就是<b>「孔融讓梨」</b>那個孔融，這時候是北海的太守</li>
     <li>他一直反對曹操，講話也不客氣</li>
     <li>後來曹操找了理由，<b>把他全家殺了</b></li>
   </ul>
   <div class="callout">他兩個孩子正在下棋。<br>有人叫他們快跑，孩子說：<br><b>「鳥巢翻了，蛋還能完好嗎？」</b></div>
 </div>
 <div class="cast tight">${ph("kongrong","孔融","讓梨的那個孔融")}</div></div>""",
 "note": """<p>孩子一定知道「孔融讓梨」，<b>會很驚訝他是這個下場</b>。這一頁的衝擊力很強。</p>
 <p>「覆巢之下無完卵」這句成語就是從這裡來的，可以寫在黑板上。</p>"""},

{"html": """<div class="eyebrow">十五 · 這一回的話</div>
 <h2>同一塊招牌，兩種下場</h2>
 <div class="cols">
   <div class="card">${ic("crown")}<h3>袁術</h3><p>拿到玉璽就<b>自己當皇帝</b>——沒人承認，兩年就完了（第七回）</p></div>
   <div class="card">${ic("scroll")}<h3>曹操</h3><p>拿到皇帝<b>還是當臣子</b>——所有命令都名正言順</p></div>
 </div>
 <div class="callout">差別不在<b>誰比較壞</b>，<br>在<b>誰忍得住不把招牌拆下來戴在自己頭上</b>。</div>""",
 "note": """<p>兩張卡對照。這是整套課<b>關於權力最重要的一課</b>。</p>
 <p>可以預告：曹操忍了一輩子都沒稱帝。<b>他兒子第十四回就做了。</b></p>"""},

{"html": """<div class="eyebrow">十五之二 · 一封罵人的信</div>
 <h2>袁紹請人寫了一篇文章罵曹操</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>開戰之前，袁紹請文章高手<b>陳琳</b>寫了一篇檄文</li>
     <li>從曹操的祖父罵到他本人，<b>一句都沒有客氣</b></li>
     <li>曹操那時正在頭痛，看完文章<b>出了一身汗，頭不痛了</b></li>
   </ul>
   <div class="callout">他說：<b>「寫得真好。」</b><br>後來抓到陳琳，<b>沒有殺他</b>，還讓他繼續寫文章。</div>
 </div>
 <div class="cast tight">${cf(chr({robe:"#8A7B52",hat:"ru",beard:"mo",prop:"scroll"}),"陳琳","寫文章罵人的人")}${im("envelope","那篇檄文")}</div></div>""",
 "note": """<p>陳琳<b>第四回講稿裡出現過</b>（「倒持干戈，授人以柄」就是他勸何進的話）。回頭指一下——<b>同一個人，換了三個老闆。</b></p>
 <p class="ask">問：「被罵得那麼難聽，為什麼不殺他？」（因為會寫文章的人有用；也因為罵得真的好）</p>"""},

{"html": """<div class="eyebrow">十六 · 剩下的對手</div>
 <h2>北方只剩兩個人</h2>
 <div class="tier">
   <div><span class="lbl">袁紹</span><span class="bar" style="width:72%"></span><span class="n">四州・十萬兵</span></div>
   <div><span class="lbl">曹操</span><span class="bar" style="width:26%"></span><span class="n">兩萬兵・一個皇帝</span></div>
 </div>
 <div class="callout">兵差<b>五倍</b>。<br>可是曹操手上有一樣袁紹沒有的東西。</div>
 <p class="foot">下一回：他們在一條河邊碰面。那一戰叫<b>官渡</b>。</p>""",
 "note": """<p>長條圖一眼就看得懂差距。最後留白一句，讓孩子自己說「招牌」。</p>"""},

{"html": """<div class="eyebrow">十七 · 一句話總結</div>
 <h2>別人嫌麻煩的東西</h2>
 <div class="tl">
   <div><span class="yr">196</span><span>皇帝走了一年才回到洛陽，餓得半死</span><span class="ago">沒人理</span></div>
   <div><span class="yr">196</span><span>袁紹說：接來很麻煩</span><span class="ago">放棄</span></div>
   <div><span class="yr">196</span><span>曹操去接，先讓他吃飽飯</span><span class="ago">出手</span></div>
   <div class="now"><span class="yr">196</span><span>從此命令上都有皇帝的印</span><span class="ago">結果</span></div>
 </div>
 <div class="callout">最有價值的東西，<br>常常<b>看起來最麻煩</b>。</div>""",
 "note": """<p>回到開場那個「班長和老師」的問題，讓孩子自己說。</p>"""},

{"html": """<div class="eyebrow">最後</div>
 <h2>今天哪些是編的</h2>
 <div class="cols">
   <div class="card"><h3>編的</h3><p>
     <b>煮酒論英雄打雷</b>：那句話是真的，<b>打雷是小說加的</b><br><br>
     <b>吉平下毒</b>：史書只說太醫吉本參與起事，沒有下毒這段<br><br>
     <b>「挾天子以令諸侯」</b>：是別人罵曹操的話，曹操自己說的是「奉天子以令不臣」</p></div>
   <div class="card"><h3>真的</h3><p>
     <b>皇帝逃亡一年、官員挖野菜</b>：真的<br><br>
     <b>袁紹拒絕接皇帝</b>：真的，沮授真的勸過<br><br>
     <b>屯田</b>：真的，第一年百萬斛<br><br>
     <b>衣帶詔</b>：真的<br><br>
     <b>禰衡擊鼓、孔融被殺</b>：都是真的</p></div>
 </div>
 <div class="callout">「奉天子」和「挾天子」差在哪？<br><b>差在誰在說這句話。</b></div>""",
 "note": """<p>最後那個對比很值得講：<b>同一件事，自己說跟別人說，用的詞完全不一樣。</b></p>
 <p>這是整套課教「立場」的第一課。</p>"""},
]
