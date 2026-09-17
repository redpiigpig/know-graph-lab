# -*- coding: utf-8 -*-
"""第十九回　五丈原（228–234）

諸葛亮之死。整套課情感的最高點。
📄 收尾放杜甫〈蜀相〉。
"""

TITLE = "三國第十九回"
MARK = "三國演義 · 第十九回"
SUB = "五丈原"

SLIDES = [
{"cover": True,
 "html": """<div class="art">
   <div class="txt">
     <div class="eyebrow">第十九回</div>
     <h1>他一直沒有<em>等到那一天</em></h1>
     <p class="sub">六年五次，每一次都因為同一個原因退兵。<br>第六次，他沒有回來。</p>
     <div class="meta">
       <div><dt>時間</dt><dd>西元 228–234 年</dd></div>
       <div><dt>這一回</dt><dd>北伐與諸葛亮之死</dd></div>
       <div><dt>今天要弄懂</dt><dd>為什麼輸的人反而被記住</dd></div>
     </div>
     <p class="credit">版畫與照片取自維基共享資源，出處見上方「圖片來源」</p>
   </div>
   <div class="cast">
     ${cf(chr({robe:"#EFE6D4",hat:"ru",beard:"mo",sad:1,prop:"fu"}),"諸葛亮","五十四歲")}
     ${im("lantern","五丈原的燈")}
   </div>
 </div>""",
 "note": """<p>🚩 <b>整套課情感最重的一回。</b>先告訴孩子今天主角會走。</p>
 <p class="ask">開場問：「沒有做到的事，算不算白做？」最後一頁回來對。</p>"""},

{"html": """<div class="eyebrow">一 · 真正的敵人</div>
 <h2>不是魏國，是那條路</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>從漢中到關中要<b>翻過秦嶺</b>，只有幾條窄谷道</li>
     <li>一斛糧食從成都運到前線，路上<b>就吃掉大半</b></li>
     <li>所以每次北伐<b>都不是被打退的，是糧吃完了自己退</b></li>
   </ul>
   <div class="callout">五次北伐，<br><b>四次敗在同一件事上。</b></div>
 </div>
 <div class="cast tight">${im("mountain","秦嶺")}${im("grain","運不上去")}</div></div>""",
 "note": """<p>接第十八回最後那個問題。<b>答案是糧食。</b></p>
 <p class="ask">問：「為什麼不多帶一點糧？」（帶糧的人也要吃飯——路愈長愈划不來）</p>"""},

{"html": """<div class="eyebrow">二 · 他想的辦法</div>
 <h2>木牛流馬</h2>
 <div class="art wide"><div class="txt">
   <ul class="pts">
     <li>為了解決運糧，他發明了<b>木牛</b>和<b>流馬</b></li>
     <li>史書說：一台木牛可以載<b>一個人一年的糧</b>，走山路不用餵草料</li>
     <li>⚠︎ 它不是機器人——<b>是一種特別設計的獨輪車或四輪車</b></li>
   </ul>
   <div class="callout">「不用餵草料」的意思是：<br><b>它不是牛，是車。</b></div>
 </div>
 ${mp("woodenox","蜀軍造木牛流馬","清代版畫")}</div>""",
 "note": """<p>孩子常以為木牛流馬是自動機械。<b>破這個梗，順便講「古人怎麼解決問題」。</b></p>"""},

{"html": """<div class="eyebrow">三 · 現在還看得到</div>
 <h2>後人照著做的複製品</h2>
 <div class="cols">
   <div class="card">${pc("woodenoxreplica")}<h3>木牛</h3><p>五丈原武侯祠的複製品</p></div>
   <div class="card">${pc("flowinghorse")}<h3>流馬</h3><p>一樣是後人依記載重做的</p></div>
 </div>
 <div class="callout">史書留下了<b>尺寸</b>，<br>可是<b>製法失傳了</b>——所以每個人做出來都不太一樣。</div>""",
 "note": """<p>兩張照片對照。可以問：<b>為什麼會失傳？</b>（因為蜀漢亡了，沒有人再需要）</p>"""},

{"html": """<div class="eyebrow">四 · 他還做了別的</div>
 <h2>連弩和八陣圖</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li><b>元戎弩</b>：一次可以連射十支箭的強弩</li>
     <li><b>八陣圖</b>：一套讓少數步兵能擋住騎兵的陣法</li>
     <li>司馬懿後來看了蜀軍的營壘遺址，說了四個字：<b>「天下奇才。」</b></li>
   </ul>
   <div class="callout">敵人給的評價，<br><b>通常最準。</b></div>
 </div>
 <div class="cast tight">${ph("guanlu","管輅","當時有名的術士")}${im("bow","一次十支箭")}</div></div>""",
 "note": """<p>「天下奇才」是<b>司馬懿說的</b>，這一點要強調——和第十三回曹操厚葬關羽同一種。</p>"""},

{"html": """<div class="eyebrow">五 · 第四次</div>
 <h2>他真的打贏過司馬懿</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>231 年第四次北伐，兩個人<b>第一次正面交手</b></li>
     <li>司馬懿一開始堅守，被部下譏笑「畏蜀如虎」，只好出戰</li>
     <li>結果大敗——魏軍損失<b>三千多副鎧甲、五千多張弩</b></li>
   </ul>
   <div class="callout">可是蜀軍還是退了。<br><b>因為後方的糧沒有運上來。</b></div>
   <p class="foot">撤退時張郃追擊，中箭而死——從第九回活到這裡，三十一年。</p>
 </div>
 <div class="cast tight">${ph("weiriver","魏蜀渭水之戰","清代版畫")}</div></div>""",
 "note": """<p><b>這一頁要講</b>：很多人以為諸葛亮打不過司馬懿，其實正面交手他贏了。</p>
 <p>張郃從第九回官渡出場，到這裡結束。<b>可以回頭翻那幾頁。</b></p>"""},

{"html": """<div class="eyebrow">六 · 最後一次</div>
 <h2>這次他準備了三年</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>234 年，第五次北伐，<b>十萬大軍出斜谷</b></li>
     <li>這次他改了策略：<b>在五丈原就地屯田</b>，讓士兵和當地百姓一起種</li>
     <li>意思是——<b>他打算長期待下去</b></li>
   </ul>
   <div class="callout">糧食的問題，<br><b>他終於想到辦法了。</b></div>
 </div>
 <div class="cast tight">${im("rice","就地屯田")}${im("farmer","跟百姓一起種")}</div></div>""",
 "note": """<p>第八回曹操用屯田解決糧的問題，<b>二十八年後諸葛亮在敵國境內用同一招。</b>回頭指一下。</p>"""},

{"html": """<div class="eyebrow">七 · 對面不出來</div>
 <h2>司馬懿的辦法：什麼都不做</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>他很清楚：蜀軍<b>遠道而來，拖久了一定撐不住</b></li>
     <li>所以不管怎麼挑釁，<b>就是不出營門</b></li>
     <li>兩軍在渭水兩岸<b>對峙了一百多天</b></li>
   </ul>
   <div class="callout">第十五回陸遜等了半年，<br><b>這一回司馬懿等了一百多天。</b></div>
 </div>
 <div class="cast tight">${ph("ehon_021_003","江戶時代畫的三國","《繪本通俗三國志》插圖")}</div></div>""",
 "note": """<p>「等」這條線：第九回曹操、第十五回陸遜、這一回司馬懿。<b>三國最後贏的都是會等的人。</b></p>"""},

{"html": """<div class="eyebrow">八 · 那件衣服</div>
 <h2>諸葛亮送他一套女人的衣服</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>為了逼他出戰，諸葛亮派人送去<b>女人的衣服和頭飾</b></li>
     <li>意思很明白：<b>你不敢出來，跟女人一樣。</b></li>
     <li>魏軍將領全部氣炸，司馬懿<b>笑著收下了</b></li>
   </ul>
   <div class="callout">然後他做了一件很妙的事：<br><b>寫信給皇帝請求出戰。</b></div>
   <p class="foot">皇帝當然說不准——他早就套好了。這樣他就能對部下說：不是我不敢，是皇帝不准。</p>
 </div>
 <div class="cast tight">${cf(chr({robe:"#2E4A63",hat:"jin",beard:"long"}),"司馬懿","笑著收下了")}${im("robe","女人的衣服")}</div></div>""",
 "note": """<p>「寫信請戰其實是演給部下看」——<b>這一招孩子會覺得很賊。</b></p>
 <p class="ask">問：「被羞辱還笑得出來，是懦弱還是厲害？」</p>"""},

{"html": """<div class="eyebrow">九 · 一句問話</div>
 <h2>他問使者：丞相吃得多嗎</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>蜀漢的使者來，司馬懿<b>不問軍情</b>，只問生活</li>
     <li>使者老實回答：丞相<b>很早起、很晚睡，罰二十軍杖以上的事都親自看</b>，可是<b>一天吃不到幾升米</b></li>
     <li>使者走了以後，司馬懿對左右說：</li>
   </ul>
   <div class="callout"><b>「吃得那麼少，管得那麼多——<br>他撐不久了。」</b></div>
 </div>
 <div class="cast tight">${im("bowl","吃很少")}${im("scroll","什麼都自己看")}</div></div>""",
 "note": """<p>「食少事煩」是史書原文。<b>這一頁很殘忍，但也是整回最關鍵的一頁。</b></p>
 <p class="ask">問：「為什麼他什麼事都要自己做？」（因為他不放心，也因為沒有人可以接）</p>"""},

{"html": """<div class="eyebrow">十 · 最後的日子</div>
 <h2>八月，他病倒在營中</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>他把後事交代給楊儀、費禕、姜維</li>
     <li>他交代：<b>我死後不要發喪，慢慢退兵</b></li>
     <li>皇帝派人來問：<b>您走了以後，誰可以接？</b></li>
   </ul>
   <div class="callout">他說：<b>蔣琬。</b><br>又問：蔣琬之後呢？<b>費禕。</b><br>再問：費禕之後呢？<br><b>——他沒有回答。</b></div>
 </div>
 <div class="cast tight">${ph("ehon_022_003","江戶時代畫的三國","《繪本通俗三國志》插圖")}</div></div>""",
 "note": """<p>🚩 「他沒有回答」——有兩種說法：<b>他已經說不出話了，或者他知道後面沒有人了。</b>兩種都講。</p>"""},

{"html": """<div class="eyebrow">十一 · 那一夜</div>
 <h2>234 年八月，五丈原</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>他死在軍中，<b>五十四歲</b></li>
     <li>從二十七歲出草廬到現在，<b>二十七年</b>——剛好是他出山前的年紀</li>
     <li>他的遺言是：把我葬在<b>漢中的定軍山</b>，墓穴只要能放進棺材就好</li>
   </ul>
   <div class="callout">「因山為墳，不用器物」——<br><b>不要陪葬品，不要修大墓。</b></div>
 </div>
 <div class="cast tight">${cf(chr({robe:"#EFE6D4",hat:"ru",beard:"mo",sad:1}),"諸葛亮","走完了")}</div></div>""",
 "note": """<p>🚩 <b>停下來。</b>從第十回三顧茅廬到現在，孩子跟了他十回。</p>
 <p>「二十七歲出山、二十七年後走」這個對稱，可以讓孩子算一下。</p>"""},

{"html": """<div class="eyebrow">十二 · 退兵</div>
 <h2>死諸葛走生仲達</h2>
 <div class="art wide"><div class="txt">
   <ul class="pts">
     <li>蜀軍照他的交代，<b>安靜地退兵</b></li>
     <li>司馬懿發現後追上來。蜀軍<b>忽然掉頭擺出作戰陣勢</b></li>
     <li>司馬懿以為他還活著，<b>立刻掉頭跑掉</b></li>
   </ul>
   <div class="callout">當地人編了一句話笑他：<br><b>「死諸葛嚇走活仲達。」</b><br>司馬懿聽了自己也笑：<b>「我能料生，不能料死。」</b></div>
 </div>
 ${mp("fleezhongda","死諸葛走生仲達","清代版畫")}</div>""",
 "note": """<p>這一段<b>史書有記，是真的</b>。而且司馬懿自嘲那一句也是真的——他很有幽默感。</p>"""},

{"html": """<div class="eyebrow">十三 · 他的家產</div>
 <h2>八百株桑樹，十五頃田</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>他生前曾上表給皇帝，<b>主動申報自己的財產</b></li>
     <li>內容是：成都有<b>桑樹八百株、薄田十五頃</b>，足夠家人生活</li>
     <li>他說：我在外面當官，<b>不另外經營產業</b>；我死的時候，不會多出一分錢</li>
   </ul>
   <div class="callout">他死後清點，<br><b>果然和他寫的一模一樣。</b></div>
 </div>
 <div class="cast tight">${im("houses","八百株桑樹")}${im("books","自己申報")}</div></div>""",
 "note": """<p><b>這一頁比打仗重要。</b>一個掌握全國大權十一年的人，家產和他自己說的分毫不差。</p>
 <p class="ask">問：「為什麼要自己先講？」</p>"""},

{"html": """<div class="eyebrow">十四 · 最後一個學生</div>
 <h2>姜維接下來了</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li><b>姜維</b>是第十七回投降過來的魏國青年，那年二十六歲</li>
     <li>諸葛亮很喜歡他，說他<b>「心存漢室，而且才兼於人」</b></li>
     <li>現在他三十二歲，接下了那面旗子</li>
   </ul>
   <div class="callout">諸葛亮北伐五次，<br><b>姜維後來打了十一次。</b></div>
 </div>
 <div class="cast tight">${cf(chr({robe:"#8C2F1E",hat:"wu",beard:"mo",prop:"spear"}),"姜維","三十二歲")}${im("flag","接下那面旗子")}</div></div>""",
 "note": """<p>姜維是<b>第二十回的主角</b>。這一頁交棒。</p>"""},

{"html": """<div class="eyebrow">十五 · 有人不服</div>
 <h2>魏延的下場</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>魏延資歷最老、最能打，<b>他不肯聽楊儀的撤退命令</b></li>
     <li>他說：丞相死了，還有我啊，怎麼可以就這樣回去？</li>
     <li>兩邊互相上書說對方造反，<b>最後魏延被殺，還被誅了三族</b></li>
   </ul>
   <div class="callout">🚩 ⚠︎ 小說說他<b>「腦後有反骨」</b>——<br>那是編的。<b>史書說他不是要投降魏國，只是不服楊儀。</b></div>
 </div>
 <div class="cast tight">${ph("zhugeke","諸葛恪","東吳的權臣，後來也死於內鬥")}</div></div>""",
 "note": """<p>🚩 <b>這一頁一定要翻案。</b>「反骨」是小說給的標籤，害魏延背了一千年的黑鍋。</p>
 <p class="ask">問：「一個人被貼標籤以後，還洗得掉嗎？」</p>"""},

{"html": """<div class="eyebrow">十六 · 為什麼是他</div>
 <h2>他沒有成功，可是大家記得他</h2>
 <div class="tier">
   <div><span class="lbl">曹操</span><span>統一北方——<b>被寫成奸雄</b></span></div>
   <div><span class="lbl">司馬懿</span><span>笑到最後——<b>沒有人替他蓋廟</b></span></div>
   <div><span class="lbl">諸葛亮</span><span>一次都沒成功——<b>廟蓋到現在</b></span></div>
 </div>
 <div class="callout">被記住的不是<b>結果</b>，<br>是<b>他做事情的樣子</b>。</div>""",
 "note": """<p>三行指過去。回到開場「沒做到算不算白做」。</p>
 <p class="ask">問：「如果你只能被記住一件事，你希望是什麼？」</p>"""},

{"html": """<div class="eyebrow">十六之二 · 他走了以後</div>
 <h2>蜀漢又撐了二十九年</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>很多人以為諸葛亮一死蜀漢就完了，<b>其實沒有</b></li>
     <li><b>蔣琬</b>接手十二年、<b>費禕</b>接手七年，兩個人都不主張大打</li>
     <li>那二十年蜀漢<b>比北伐時期還安定</b>，百姓過得比較好</li>
   </ul>
   <div class="callout">他挑的接班人，<br><b>挑對了。</b></div>
   <p class="foot">可是這二十年也沒有拉近和魏國的差距——問題從一開始就不是誰在管事。</p>
 </div>
 <div class="cast tight">${cf(chr({robe:"#8A7B52",hat:"jin",beard:"mo",prop:"scroll"}),"蔣琬","接手十二年")}${cf(chr({robe:"#7A6A4F",hat:"ru",beard:"mo"}),"費禕","再接七年")}</div></div>""",
 "note": """<p>回頭指第十頁「誰可以接」那一段。<b>他臨終挑的兩個人，一共撐了十九年。</b></p>
 <p class="ask">問：「不打仗是不是比較好？」（百姓過得好，但國家沒有變強）</p>"""},

{"html": """<div class="eyebrow">十七 · 一千五百年後</div>
 <h2>杜甫寫的那首詩</h2>
 <div class="callout" style="font-family:var(--serif);font-size:clamp(1.05rem,1.9vw,1.6rem);line-height:2">
   丞相祠堂何處尋？錦官城外柏森森。<br>
   映階碧草自春色，隔葉黃鸝空好音。<br>
   三顧頻煩天下計，兩朝開濟老臣心。<br>
   <b>出師未捷身先死，長使英雄淚滿襟。</b>
 </div>
 <p class="foot">——丞相的祠堂在哪裡？成都城外那片柏樹林。<br>
 當年三顧茅廬談的是天下大計，兩代君王他都撐住了。<br>
 <b>出兵還沒成功，人就先走了，讓後來的人一想到就掉眼淚。</b></p>""",
 "note": """<p>📄 <b>整首唸出來</b>，唸完再講白話。這首詩叫〈蜀相〉，杜甫寫於 760 年。</p>
 <p>「出師未捷身先死」是<b>整套課最有名的一句</b>，可以讓孩子抄下來。</p>"""},

{"html": """<div class="eyebrow">最後</div>
 <h2>今天哪些是編的</h2>
 <div class="cols">
   <div class="card"><h3>編的</h3><p>
     <b>五丈原禳星續命</b>：小說編的<br><br>
     <b>木牛流馬是自動機械</b>：是人力推的車<br><br>
     <b>魏延「腦後有反骨」</b>：完全是小說編的</p></div>
   <div class="card"><h3>真的</h3><p>
     <b>五次北伐多半因糧退兵</b>：真的<br><br>
     <b>231 年正面打敗司馬懿</b>：真的<br><br>
     <b>「食少事煩，其能久乎」</b>：真的<br><br>
     <b>死諸葛走生仲達</b>：真的<br><br>
     <b>桑八百株、田十五頃</b>：真的</p></div>
 </div>
 <div class="callout">小說把他寫成會呼風喚雨的人，<br>真正讓人記一千八百年的，<b>是那八百株桑樹。</b></div>""",
 "note": """<p>固定收尾頁。<b>這一回的收尾是整套課最好的一個。</b>慢慢唸。</p>
 <p>送女人衣服、木牛流馬存在、死諸葛走生仲達——都是真的，講稿裡已經逐頁標過。</p>"""},
]
