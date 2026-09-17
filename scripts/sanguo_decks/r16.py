# -*- coding: utf-8 -*-
"""第十六回　七擒孟獲（225）

整套課唯一一回「打完之後大家都變好」。
和前面十五回的殺伐形成對比，也替第十七回的北伐鋪好後方。
"""

TITLE = "三國第十六回"
MARK = "三國演義 · 第十六回"
SUB = "七擒孟獲"

SLIDES = [
{"cover": True,
 "html": """<div class="art">
   <div class="txt">
     <div class="eyebrow">第十六回</div>
     <h1>抓到了，<em>又放掉</em></h1>
     <p class="sub">整套課打了十五回，<br>這一回是唯一一次——打完，兩邊都變好。</p>
     <div class="meta">
       <div><dt>時間</dt><dd>西元 225 年，南中</dd></div>
       <div><dt>這一回</dt><dd>諸葛亮南征</dd></div>
       <div><dt>今天要弄懂</dt><dd>什麼叫「打贏了還不夠」</dd></div>
     </div>
     <p class="credit">版畫與繡像取自維基共享資源，出處見上方「圖片來源」</p>
   </div>
   <div class="cast">
     ${cf(chr({robe:"#EFE6D4",hat:"ru",beard:"mo",prop:"fu"}),"諸葛亮","四十五歲")}
     ${im("mountain","南方的山")}
   </div>
 </div>""",
 "note": """<p>這一回<b>氣氛最輕鬆</b>，前一回太沉重，正好換口氣。</p>
 <p class="ask">開場問：「跟人吵架吵贏了，對方就服你了嗎？」最後一頁回來對。</p>"""},

{"html": """<div class="eyebrow">一 · 兩年準備</div>
 <h2>他先什麼都不做</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>劉備死後南方就反了，可是諸葛亮<b>兩年都沒有出兵</b></li>
     <li>這兩年他在做三件事：<b>和東吳重修盟約、發展農業、練兵</b></li>
     <li>史書說那兩年蜀漢<b>「農植穀，閉關息民」</b></li>
   </ul>
   <div class="callout">最急的事，<br><b>他反而先放著。</b></div>
 </div>
 <div class="cast tight">${im("rice","先種田")}${im("hourglass","等兩年")}</div></div>""",
 "note": """<p>接第十五回結尾的爛攤子。<b>他沒有急著證明自己。</b></p>
 <p class="ask">問：「家裡出事的時候，應該先解決哪一件？」</p>"""},

{"html": """<div class="eyebrow">二 · 為什麼要先打南方</div>
 <h2>不能背後留著火</h2>
 <div class="tier">
   <div><span class="lbl">北伐</span><span>要往北打魏國，<b>大軍會離開成都</b></span></div>
   <div><span class="lbl">南方</span><span>如果南中還在反，<b>後面就會被抄</b></span></div>
   <div><span class="lbl">資源</span><span>南中出<b>金、銀、銅、鹽、耕牛、戰馬</b></span></div>
 </div>
 <div class="callout">所以先南後北——<br><b>不是因為南方比較重要，是因為北伐需要它。</b></div>""",
 "note": """<p>三行講清楚戰略順序。<b>孩子常以為打仗就是誰惹我我打誰。</b></p>"""},

{"html": """<div class="eyebrow">三 · 送行時的四個字</div>
 <h2>馬謖說：攻心為上</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>出發前，參軍<b>馬謖</b>送了幾十里</li>
     <li>諸葛亮問他有什麼建議</li>
     <li>他說：南方靠著地遠山險，<b>今天打服了，明天還會反</b></li>
   </ul>
   <div class="callout">他說了八個字：<br><b>「攻心為上，攻城為下。」</b></div>
   <p class="foot">諸葛亮採納了他的話。</p>
 </div>
 <div class="cast tight">${ph("masu","馬謖","這一回他說對了")}</div></div>""",
 "note": """<p>📄 八個字寫黑板。<b>整回的方法就在這裡。</b></p>
 <p>🚩 記住馬謖這張臉——<b>第十八回他會犯下最有名的錯。</b>這一回他是對的，下一回他錯了，這個對比很重要。</p>"""},

{"html": """<div class="eyebrow">四 · 三路南下</div>
 <h2>他自己走最難走的那一路</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>三月出兵，兵分三路</li>
     <li>諸葛亮親自帶<b>西路</b>——要渡瀘水、穿過瘴氣區</li>
     <li>那時候南方有瘴氣（熱帶疾病），<b>很多士兵是病死的不是戰死的</b></li>
   </ul>
   <div class="callout">「五月渡瀘，深入不毛」——<br>這八個字<b>第十七回的出師表裡會再出現一次。</b></div>
 </div>
 <div class="cast tight">${ph("ehon_016_001","江戶時代畫的三國","《繪本通俗三國志》插圖")}</div></div>""",
 "note": """<p>這八個字<b>先在這裡出現，第十七回讀出師表時會回來</b>——那時候孩子會有「我知道這個！」的感覺。</p>"""},

{"html": """<div class="eyebrow">五 · 對手是誰</div>
 <h2>孟獲：南方人服他</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>南中的首領叫<b>孟獲</b>，當地的漢人和各族<b>都聽他的</b></li>
     <li>諸葛亮特別交代：<b>要活的，不要殺他</b></li>
     <li>因為殺了他，會再冒出第二個、第三個孟獲</li>
   </ul>
   <div class="callout">要平定一個地方，<br><b>要的不是那個人的命，是那個人的服氣。</b></div>
 </div>
 <div class="cast tight">${ph("menghuo","孟獲","南中首領")}</div></div>""",
 "note": """<p>「要活的」這個決定是整回的關鍵。<b>和前面十五回「抓到就殺」完全不同。</b></p>"""},

{"html": """<div class="eyebrow">六 · 第一次</div>
 <h2>抓到了，然後放了</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>第一仗孟獲就被抓了</li>
     <li>諸葛亮帶他<b>參觀蜀軍的營寨</b>，問他：你覺得怎麼樣？</li>
     <li>孟獲說：<b>「我以前不知道你們的虛實，現在看過了，我贏得了。」</b></li>
   </ul>
   <div class="callout">諸葛亮笑一笑，<br><b>放他回去。</b></div>
 </div>
 <div class="cast tight">${im("flag","放他走")}${im("horse","回去再來")}</div></div>""",
 "note": """<p>「帶敵人參觀自己的營寨」——<b>這一招孩子會覺得不可思議。</b></p>
 <p class="ask">問：「為什麼要給他看？」（因為他要的是孟獲心服，不是贏一場）</p>"""},

{"html": """<div class="eyebrow">七 · 一次又一次</div>
 <h2>七次抓到，七次放走</h2>
 <div class="tl">
   <div><span class="yr">一</span><span>正面被擒</span><span class="ago">不服</span></div>
   <div><span class="yr">二</span><span>被自己的部下綁來</span><span class="ago">不服</span></div>
   <div><span class="yr">三</span><span>弟弟詐降，一起被抓</span><span class="ago">不服</span></div>
   <div><span class="yr">四五六</span><span>換了各種辦法，都被識破</span><span class="ago">不服</span></div>
   <div class="now"><span class="yr">七</span><span>最後一次</span><span class="ago">不走了</span></div>
 </div>
 <div class="callout">⚠︎ <b>「七擒七縱」只有四個字在史書裡</b>：<br>「七縱七擒，而亮猶遣獲。」<br>過程全部是小說補的。</div>""",
 "note": """<p>五行快速帶過，不要一次一次細講，<b>會拖太久</b>。</p>
 <p>「七」在古代常常表示「很多次」，不一定剛好七次。</p>"""},

{"html": """<div class="eyebrow">八 · 最有名的那一段</div>
 <h2>藤甲兵</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>孟獲最後搬來救兵：<b>穿藤甲的烏戈國兵</b></li>
     <li>藤甲用油泡過，<b>刀砍不入、水泡不壞，掉進河裡還會浮起來</b></li>
     <li>可是有一個弱點：<b>怕火</b></li>
   </ul>
   <div class="callout">諸葛亮把他們引進山谷，<b>兩頭堵住點火</b>。<br>他看著山谷流下眼淚說：</div>
   <p class="foot"><b>「我雖然有功於國家，但一定會折壽。」</b></p>
 </div>
 <div class="cast tight">${ph("ehon_016_002","江戶時代畫的三國","《繪本通俗三國志》插圖")}</div></div>""",
 "note": """<p>⚠︎ 藤甲兵是<b>小說編的</b>，但這一段有它的意義：<b>連贏的人都覺得自己做得太過。</b></p>
 <p class="ask">問：「打贏了為什麼要哭？」</p>"""},

{"html": """<div class="eyebrow">九 · 第七次</div>
 <h2>他不走了</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>第七次被抓，諸葛亮照樣說：<b>「放你回去，再來一次。」</b></li>
     <li>孟獲站著不動，流著眼淚說：</li>
   </ul>
   <div class="callout"><b>「七擒七縱，自古沒有過。<br>我雖然是外族，也懂得禮義——<br>我不走了。」</b></div>
   <p class="foot">從此南中不再反叛。</p>
 </div>
 <div class="cast tight">${ph("menghuo2","孟獲","服了")}</div></div>""",
 "note": """<p>這一段照原文唸效果最好。<b>孩子會鬆一口氣。</b></p>
 <p>對照第七回白門樓：<b>呂布求饒被殺，孟獲不求饒反而活下來。</b></p>"""},

{"html": """<div class="eyebrow">十 · 最奇怪的決定</div>
 <h2>打完了，一個官都不留</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>部下問：要派哪些官員留下來管？</li>
     <li>諸葛亮說：<b>不留官、不留兵、不運糧</b></li>
     <li>理由：留官要留兵，留兵要運糧，<b>而且當地人剛失去親人，會恨我們</b></li>
   </ul>
   <div class="callout">他讓<b>當地人自己管自己</b>，<br>只要他們不反、願意供應資源就好。</div>
 </div>
 <div class="cast tight">${im("houses","自己管自己")}${im("cash","南中的資源")}</div></div>""",
 "note": """<p><b>這一頁是整回真正的重點</b>，比七擒七縱重要。史書原文就是「不留兵，不運糧」。</p>
 <p class="ask">問：「不派人管，他們不會又反嗎？」（諸葛亮賭的就是這個——而他賭對了）</p>"""},

{"html": """<div class="eyebrow">十一 · 帶回去的東西</div>
 <h2>金、銀、耕牛、戰馬</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>南中從此<b>穩定供應</b>蜀漢金銀、丹漆、耕牛、戰馬</li>
     <li>還有一支很能打的部隊，後來被編成<b>「無當飛軍」</b></li>
     <li>史書說：<b>「軍資所出，國以富饒。」</b></li>
   </ul>
   <div class="callout">三年後北伐的錢和兵，<br><b>很多是從這裡來的。</b></div>
 </div>
 <div class="cast tight">${ph("ehon_016_003","江戶時代畫的三國","《繪本通俗三國志》插圖")}</div></div>""",
 "note": """<p>回頭指第二頁的「北伐需要南中」。<b>兩年後就用上了。</b></p>"""},

{"html": """<div class="eyebrow">十二 · 留下來的東西</div>
 <h2>當地到現在還記得他</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>雲南很多地方有<b>諸葛亮的傳說</b>：教人種田、教人蓋房子、教人織布</li>
     <li>有些少數民族的頭飾叫<b>「孔明帽」</b></li>
     <li>當地還有「孔明燈」「武侯祠」的說法</li>
   </ul>
   <div class="callout">打進來的軍隊，<br><b>一千八百年後還被當地人紀念——這很少見。</b></div>
 </div>
 <div class="cast tight">${ph("wuhoucorridor","武侯祠","成都，後人紀念諸葛亮的地方")}</div></div>""",
 "note": """<p>這些傳說大多是後人附會，<b>但「當地人願意紀念他」這件事本身就是結果。</b></p>
 <p class="ask">問：「為什麼被打的人會紀念打他們的人？」</p>"""},

{"html": """<div class="eyebrow">十三 · 對照</div>
 <h2>兩種打完之後</h2>
 <div class="cols">
   <div class="card">${ic("fire")}<h3>前面十五回</h3><p>打完就<b>殺、搶、佔</b><br>過幾年<b>又反、又打</b></p></div>
   <div class="card">${ic("houses")}<h3>這一回</h3><p>打完<b>不留兵、不留官</b><br>從此<b>再也沒有反</b></p></div>
 </div>
 <div class="callout">同樣是打贏，<br><b>結果可以完全不一樣。</b></div>""",
 "note": """<p>兩張卡對照。<b>這是整套課少見的一堂「正面教材」。</b></p>"""},

{"html": """<div class="eyebrow">十四 · 他身邊的人</div>
 <h2>南征回來，人都齊了</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li><b>蔣琬</b>留守成都管後勤，做得很好</li>
     <li><b>馬謖</b>出了「攻心為上」的主意，被視為接班人選</li>
     <li><b>魏延</b>能打，但脾氣硬，和大家處不好</li>
   </ul>
   <div class="callout">這三個人，<br><b>第十七到十九回都會出事。</b></div>
 </div>
 <div class="cast tight">${ph("jiangwan","蔣琬","後來接諸葛亮的位子")}${ph("weiyan","魏延","很能打，很難相處")}</div></div>""",
 "note": """<p>三個人都先埋。<b>第十八回馬謖、第十九回魏延、第二十回蔣琬。</b></p>"""},

{"html": """<div class="eyebrow">十五 · 回到成都</div>
 <h2>十二月，他回來了</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>三月出兵、十二月回成都，<b>九個月</b></li>
     <li>南方安定、資源進來、軍隊練過了實戰</li>
     <li>蜀漢從第十五回那個爛攤子，<b>緩過來了</b></li>
   </ul>
   <div class="callout">接下來他要做的，<br><b>是劉備和他在草屋裡說好的那第三步。</b></div>
 </div>
 <div class="cast tight">${ph("zhugeliangcart","諸葛亮","傳統木刻版畫")}</div></div>""",
 "note": """<p>回頭指第十回隆中對的第三步（兩路北伐）。<b>下一回就是出師表。</b></p>"""},

{"html": """<div class="eyebrow">十五之二 · 另外兩家在做什麼</div>
 <h2>同一段時間的魏和吳</h2>
 <div class="cols">
   <div class="card">${pc("caozhen")}<h3>魏</h3><p>曹丕三次南征都沒成功。<b>226 年他病死</b>，只當了七年皇帝，四十歲。兒子曹叡即位。</p></div>
   <div class="card">${pc("dingfeng")}<h3>吳</h3><p>孫權守住長江，<b>229 年才正式稱帝</b>——比另外兩家晚了八、九年。</p></div>
 </div>
 <div class="callout">三個國家<b>誰也吃不掉誰</b>，<br>只好各自整理自己的家。</div>""",
 "note": """<p>這一頁讓孩子知道<b>同一段時間三邊都在動</b>，不是只有蜀漢在演。</p>
 <p>曹丕四十歲就死了——<b>比他逼退位的漢獻帝還早走八年。</b>（第十四回講過）</p>"""},

{"html": """<div class="eyebrow">十六 · 可是</div>
 <h2>有一件事已經回不去了</h2>
 <div class="tier">
   <div><span class="lbl">原計畫</span><span>荊州一路 ＋ 漢中一路，<b>兩路北伐</b></span></div>
   <div><span class="lbl">現在</span><span>荊州<b>沒了</b>（第十三回）</span></div>
   <div><span class="lbl">所以</span><span>只剩<b>一路</b>，而且要翻過秦嶺</span></div>
 </div>
 <div class="callout">隆中對的第三步，<br><b>從一開始就少了一半。</b></div>""",
 "note": """<p>🚩 <b>這一頁決定了後面四回的結局。</b>孩子要先知道：北伐一開始就很難。</p>
 <p class="ask">問：「明知很難還要做嗎？」——留到第十七回回答。</p>"""},

{"html": """<div class="eyebrow">十七 · 這一回的話</div>
 <h2>打贏了還不夠</h2>
 <div class="tier">
   <div><span class="lbl">打身體</span><span>贏一場，<b>對方會再來</b></span></div>
   <div><span class="lbl">打心</span><span>贏一次，<b>對方不來了</b></span></div>
 </div>
 <div class="callout">馬謖那八個字——<b>攻心為上</b>——<br>是整套課十六回裡<b>最有用的一句話</b>。</div>
 <p class="foot">可是說出這句話的人，下一回會用命證明：<b>懂道理，跟做得到，是兩回事。</b></p>""",
 "note": """<p>回到開場「吵贏了對方就服你了嗎」。</p>
 <p>最後那句 foot 是第十八回的引信，<b>講完就翻頁。</b></p>"""},

{"html": """<div class="eyebrow">最後</div>
 <h2>今天哪些是編的</h2>
 <div class="cols">
   <div class="card"><h3>編的</h3><p>
     <b>七擒的過程</b>：史書只有「七縱七擒」四個字<br><br>
     <b>藤甲兵、火燒藤甲</b>：小說編的<br><br>
     <b>祝融夫人</b>：小說人物<br><br>
     <b>饅頭的由來</b>：傳說，不是正史</p></div>
   <div class="card"><h3>真的</h3><p>
     <b>兩年不出兵，先種田</b>：真的<br><br>
     <b>馬謖「攻心為上」</b>：真的<br><br>
     <b>五月渡瀘、深入不毛</b>：真的（出師表原文）<br><br>
     <b>七縱七擒孟獲</b>：真的，只是過程不詳<br><br>
     <b>不留兵、不留官、不運糧</b>：真的<br><br>
     <b>南中資源讓蜀漢富饒</b>：真的</p></div>
 </div>
 <div class="callout">小說加了那麼多，<br>可是最厲害的一步<b>本來就在史書裡</b>——<br><b>打完之後，一個兵都不留。</b></div>""",
 "note": """<p>固定收尾頁。這一回可以問：<b>你覺得哪一種贏比較厲害？</b></p>"""},
]
