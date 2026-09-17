# -*- coding: utf-8 -*-
"""第十八回　空城計（228）

街亭失守與揮淚斬馬謖。
空城計是虛構的，但它是整套課示範「為什麼假故事會流傳」的最好案例。
"""

TITLE = "三國第十八回"
MARK = "三國演義 · 第十八回"
SUB = "空城計"

SLIDES = [
{"cover": True,
 "html": """<div class="art">
   <div class="txt">
     <div class="eyebrow">第十八回</div>
     <h1>一個決定，<em>毀掉一整場</em></h1>
     <p class="sub">命令講得清清楚楚，<br>可是到了現場，他改了主意。</p>
     <div class="meta">
       <div><dt>時間</dt><dd>西元 228 年，街亭</dd></div>
       <div><dt>這一回</dt><dd>街亭失守與揮淚斬馬謖</dd></div>
       <div><dt>今天要弄懂</dt><dd>「懂道理」和「做得到」的差別</dd></div>
     </div>
     <p class="credit">版畫與繡像取自維基共享資源，出處見上方「圖片來源」</p>
   </div>
   <div class="cast">
     ${cf(chr({robe:"#8A7B52",hat:"ru",beard:"mo",prop:"scroll"}),"馬謖","三十九歲")}
     ${im("mountain","那座山")}
   </div>
 </div>""",
 "note": """<p>上一回賣的關子，這一回揭曉。<b>先問孩子：你猜他做了什麼？</b></p>
 <p class="ask">開場問：「有人交代你怎麼做，可是你覺得有更好的方法，你會照做嗎？」</p>"""},

{"html": """<div class="eyebrow">一 · 那個路口</div>
 <h2>街亭長什麼樣子</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>兩邊是山，中間一條谷道，<b>路口有一口井、有水源</b></li>
     <li>諸葛亮的命令：<b>在路口紮營，把路堵死</b></li>
     <li>只要堵住，魏國的援軍就進不來</li>
   </ul>
   <div class="callout">任務很單純：<br><b>不用贏，只要擋住。</b></div>
 </div>
 <div class="cast tight">${im("mountain","兩邊是山")}${im("houses","路口紮營")}</div></div>""",
 "note": """<p>「不用贏，只要擋住」——<b>這句話是整回的關鍵</b>。馬謖想的是贏。</p>"""},

{"html": """<div class="eyebrow">二 · 他改了主意</div>
 <h2>馬謖說：我們上山</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>到了現場，馬謖決定<b>把大軍帶到山上紮營</b></li>
     <li>他的理由聽起來很有道理：<b>居高臨下，衝下來勢不可擋</b></li>
     <li>他還引用兵法：<b>「憑高視下，勢如破竹。」</b></li>
   </ul>
   <div class="callout">他讀的兵書<b>比誰都多</b>。<br>他說的每一句，<b>書上都有。</b></div>
 </div>
 <div class="cast tight">${ph("ehon_018_003","江戶時代畫的三國","《繪本通俗三國志》插圖")}</div></div>""",
 "note": """<p>🚩 <b>不要把馬謖講成笨蛋。</b>他的理由是有依據的——問題在他沒有考慮這座山的實際情況。</p>
 <p class="ask">問：「他說得有道理嗎？」（有——但漏了一件事）</p>"""},

{"html": """<div class="eyebrow">三 · 有人反對</div>
 <h2>王平說了三次</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>副將<b>王平</b>當場反對，一連勸了好幾次</li>
     <li>他的理由很簡單：<b>山上沒有水</b></li>
     <li>馬謖不聽。王平只好要了五千人，<b>自己在山下另外紮營</b></li>
   </ul>
   <div class="callout">王平<b>不認識幾個字</b>，<br>可是他打過很多仗。</div>
 </div>
 <div class="cast tight">${ph("wangjing","王經","魏國官員")}${im("bowl","山上沒有水")}</div></div>""",
 "note": """<p><b>這一頁是整回的對比核心</b>：讀很多書的人 vs 打過很多仗的人。</p>
 <p>王平後來當上蜀漢的大將，<b>因為他這一天做對了。</b></p>"""},

{"html": """<div class="eyebrow">四 · 對面來了</div>
 <h2>張郃看一眼就知道怎麼打</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>魏軍主將<b>張郃</b>趕到，看見蜀軍在山上</li>
     <li>他沒有攻山，只做了一件事：<b>把山圍起來，切斷水源</b></li>
     <li>然後<b>什麼都不做，等著</b></li>
   </ul>
   <div class="callout">兵法上叫「置之死地而後生」，<br>可是——<b>士兵渴了不會變勇敢，只會逃。</b></div>
 </div>
 <div class="cast tight">${ph("zhonghui","鍾會","魏國後起將領，第二十回會出現")}</div></div>""",
 "note": """<p>張郃第九回、第十七回都出現過，<b>這是他的高光時刻。</b></p>
 <p class="ask">問：「為什麼不衝上去打？」（不用打，斷水就夠了）</p>"""},

{"html": """<div class="eyebrow">五 · 一天</div>
 <h2>撐不過一天</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>水斷了以後，山上的士兵<b>很快就亂了</b></li>
     <li>馬謖下令衝下山，<b>沒有人跟上</b></li>
     <li>蜀軍潰散，很多人直接投降</li>
   </ul>
   <div class="callout">只有山下的王平——<b>五千人擂鼓虛張聲勢</b>，<br>張郃怕有埋伏不敢追，<b>他把散兵收攏帶回來了</b>。</div>
 </div>
 <div class="cast tight">${im("sick","渴")}${im("flag","散了")}</div></div>""",
 "note": """<p>王平那一段是真的。<b>全軍潰敗裡唯一守住建制的人。</b></p>"""},

{"html": """<div class="eyebrow">六 · 全部要吐出來</div>
 <h2>三個郡又回去了</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>街亭一失，魏軍長驅直入，蜀軍<b>失去據點</b></li>
     <li>剛投降的南安、天水、安定<b>三個郡全部丟回去</b></li>
     <li>諸葛亮只好撤軍——並把<b>一千多戶西縣百姓帶回漢中</b></li>
   </ul>
   <div class="callout">打了幾個月，<br><b>最後只帶回一千多戶人。</b></div>
 </div>
 <div class="cast tight">${ph("ehon_018_004","江戶時代畫的三國","《繪本通俗三國志》插圖")}</div></div>""",
 "note": """<p>「帶回一千多戶人」——<b>撤退時還記得帶走百姓</b>，這個細節值得講。</p>
 <p>第十回劉備也是這樣（十萬百姓跟著走）。<b>同一種做法，隔了二十年。</b></p>"""},

{"html": """<div class="eyebrow">七 · 那個很有名的故事</div>
 <h2>空城計</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>小說說：司馬懿十五萬大軍逼近，城裡只剩兩千多人</li>
     <li>諸葛亮下令<b>大開城門，派人掃地</b>，自己在城樓上焚香彈琴</li>
     <li>司馬懿看了半天，<b>下令撤退</b></li>
   </ul>
   <div class="callout">⚠︎ <b>這件事沒有發生過。</b><br>那年司馬懿人在<b>一千多里外的荊州</b>。</div>
 </div>
 <div class="cast tight">${ph("rtk2","三國演義插圖","清代版畫")}</div></div>""",
 "note": """<p>🚩 <b>先把故事講完整、講精彩，再破梗。</b>順序很重要。</p>
 <p>這個故事出自《郭沖三事》，<b>裴松之當時就一條一條駁斥過</b>——連年代都對不上。</p>"""},

{"html": """<div class="eyebrow">八 · 那為什麼大家喜歡</div>
 <h2>假的故事，為什麼會流傳一千年</h2>
 <div class="tier">
   <div><span class="lbl">因為</span><span>它讓<b>弱的一方靠腦子贏</b></span></div>
   <div><span class="lbl">因為</span><span>它讓<b>最緊張的時刻變成一場表演</b></span></div>
   <div><span class="lbl">因為</span><span>它讓人相信：<b>沒有兵也還有辦法</b></span></div>
 </div>
 <div class="callout">故事是假的，<br><b>可是人們需要那個故事。</b></div>""",
 "note": """<p><b>整套課最好的一堂「怎麼看故事」的課。</b>不要只說「這是假的」就結束。</p>
 <p class="ask">問：「知道是假的以後，你還喜歡這個故事嗎？」</p>"""},

{"html": """<div class="eyebrow">九 · 真的那一段</div>
 <h2>他做的是另一件事</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>史書上諸葛亮撤退時做的，是<b>有秩序地收攏部隊</b></li>
     <li>他把責任<b>全部攬在自己身上</b>，沒有推給任何人</li>
     <li>還下令<b>檢討整個作戰過程</b>，要大家直接批評他</li>
   </ul>
   <div class="callout">沒有彈琴，沒有奇蹟。<br><b>只有一個把爛攤子收好的人。</b></div>
 </div>
 <div class="cast tight">${ph("rtkc1","三國志傳插圖","清代版畫")}</div></div>""",
 "note": """<p>這一頁和上一頁對照。<b>真實比較不好看，但比較有用。</b></p>"""},

{"html": """<div class="eyebrow">十 · 揮淚</div>
 <h2>他把馬謖殺了</h2>
 <div class="art wide"><div class="txt">
   <ul class="pts">
     <li>馬謖被下獄處死（一說死於獄中），<b>三十九歲</b></li>
     <li>行刑前馬謖寫信給諸葛亮：<b>「您待我像兒子，我也把您當父親……我死而無恨。」</b></li>
     <li>諸葛亮親自去送，<b>哭了</b></li>
   </ul>
   <div class="callout">十萬大軍<b>都為他流淚</b>。</div>
 </div>
 ${mp("executemasu","孔明揮淚斬馬謖","清代版畫")}</div>""",
 "note": """<p>🚩 <b>這一頁停久一點。</b>諸葛亮不是在懲罰一個敵人，是在殺一個他很喜歡的晚輩。</p>
 <p class="ask">問：「可以因為喜歡他就不殺嗎？」</p>"""},

{"html": """<div class="eyebrow">十一 · 為什麼一定要殺</div>
 <h2>不是因為生氣</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>蜀漢是三國裡<b>最小的一國</b>，禁不起第二次這樣的錯</li>
     <li>如果馬謖不受罰，以後<b>沒有人會照命令做</b></li>
     <li>有人勸他：人才難得，留著吧。他說：<b>國家的法，比人才重要。</b></li>
   </ul>
   <div class="callout">他哭著把最喜歡的學生殺掉，<br><b>是為了讓其他人相信規矩。</b></div>
 </div>
 <div class="cast tight">${ph("rtkc2","三國志傳插圖","清代版畫")}</div></div>""",
 "note": """<p>這一頁要把邏輯講清楚，不然孩子只覺得殘忍。</p>
 <p class="ask">問：「如果班長犯規沒被處罰，其他人會怎麼想？」</p>"""},

{"html": """<div class="eyebrow">十二 · 他也罰了自己</div>
 <h2>丞相自貶三級</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>他上書皇帝：<b>用人不當是我的錯，請降我的職</b></li>
     <li>劉禪把他從丞相降為<b>右將軍</b>，但仍然代理丞相的事</li>
     <li>同一時間，<b>王平升官了</b>——因為他做對了</li>
   </ul>
   <div class="callout">賞和罰<b>同一天發布</b>。<br>這就是他要的效果。</div>
 </div>
 <div class="cast tight">${ph("rtkc3","三國志傳插圖","清代版畫")}</div></div>""",
 "note": """<p>「自己也罰」是關鍵。<b>只罰別人不罰自己，規矩就沒有用。</b></p>
 <p class="ask">問：「老闆會處罰自己嗎？」</p>"""},

{"html": """<div class="eyebrow">十三 · 兩個人的對照</div>
 <h2>同一個人，兩回</h2>
 <div class="cols">
   <div class="card">${ic("books")}<h3>第十六回的馬謖</h3><p>說出<b>「攻心為上」</b><br>諸葛亮採納，南方大成功</p></div>
   <div class="card">${ic("sick")}<h3>這一回的馬謖</h3><p>不照命令、<b>把軍隊帶上山</b><br>北伐全盤皆輸</p></div>
 </div>
 <div class="callout">同一個腦袋，<br><b>出主意很準，做事情不行。</b></div>""",
 "note": """<p>回頭指第十六回。<b>兩回對照是我特地安排的</b>——這比單講「他失敗了」有意思得多。</p>
 <p class="ask">問：「會說跟會做，是同一件事嗎？」</p>"""},

{"html": """<div class="eyebrow">十四 · 劉備早就說過</div>
 <h2>「言過其實，不可大用」</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>第十五回劉備臨終交代過這句話</li>
     <li>諸葛亮<b>沒有聽</b>——因為他真的很欣賞馬謖</li>
     <li>事後他自己也承認：<b>用人是我的問題</b></li>
   </ul>
   <div class="callout">最聰明的人，<br><b>也會在喜歡的人身上看走眼。</b></div>
 </div>
 <div class="cast tight">${cf(chr({robe:"#EFE6D4",hat:"ru",beard:"mo",sad:1,prop:"fu"}),"諸葛亮","四十八歲")}</div></div>""",
 "note": """<p>回頭指第十五回和第十七回。<b>這條伏筆拉了三回。</b></p>
 <p class="ask">問：「為什麼喜歡一個人就容易看錯？」</p>"""},

{"html": """<div class="eyebrow">十五 · 那個等的人</div>
 <h2>司馬懿是誰</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>他比諸葛亮大兩歲，出身河內名門</li>
     <li>曹操找他做官，他<b>裝病躺了七年</b>不出來</li>
     <li>後來出仕，一路小心，<b>很少犯錯，也很少出鋒頭</b></li>
   </ul>
   <div class="callout">他的本事只有一個字：<br><b>等。</b></div>
   <p class="foot">這一年他還沒和諸葛亮正面交手。第十九回才會。</p>
 </div>
 <div class="cast tight">${ph("simayi","司馬懿","清代繡像")}</div></div>""",
 "note": """<p>司馬懿<b>第十九、二十回會愈來愈重要</b>，最後贏的是他家。</p>
 <p>「裝病七年」和第十三回呂蒙裝病對照——<b>三國很多事靠裝。</b></p>"""},

{"html": """<div class="eyebrow">十五之二 · 一個先走的人</div>
 <h2>趙雲過世了</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>229 年，<b>趙雲病逝</b>——距離街亭那一仗只隔一年</li>
     <li>從第十回長坂坡抱阿斗、第十二回入川、第十五回勸劉備不要伐吳</li>
     <li>到第十七回七十歲還去當疑兵，<b>他一次都沒有讓人失望過</b></li>
   </ul>
   <div class="callout">五虎將到這一年<b>全部走完了</b>。<br>蜀漢能打的老將，<b>一個都不剩。</b></div>
 </div>
 <div class="cast tight">${cf(chr({robe:"#DDD8CB",hat:"wu",beard:"mo",sad:1,prop:"spear"}),"趙雲","跟了劉備三十年")}${im("flag","五虎將走完")}</div></div>""",
 "note": """<p>回頭數五虎將：關羽 219、黃忠 220、張飛 221、馬超 222、趙雲 229。<b>十年之內全走了。</b></p>
 <p>這一頁解釋<b>為什麼後面的北伐愈打愈難</b>——不是諸葛亮變差，是人沒了。</p>"""},

{"html": """<div class="eyebrow">十六 · 接下來</div>
 <h2>他又打了四次</h2>
 <div class="tl">
   <div><span class="yr">228 春</span><span>第一次・街亭失守</span><span class="ago">這一回</span></div>
   <div><span class="yr">228 冬</span><span>第二次・圍陳倉二十天不下</span><span class="ago">糧盡而退</span></div>
   <div><span class="yr">229</span><span>第三次・拿下武都、陰平</span><span class="ago">小勝</span></div>
   <div><span class="yr">231</span><span>第四次・打敗司馬懿，射殺張郃</span><span class="ago">糧盡而退</span></div>
   <div class="now"><span class="yr">234</span><span>第五次・五丈原</span><span class="ago">下一回</span></div>
 </div>
 <div class="callout">六年五次，<br><b>每一次都因為同一個原因退兵。</b></div>""",
 "note": """<p>五行快速帶過。最後那句留給孩子猜——<b>答案是糧食。</b>（第十九回主題）</p>
 <p>張郃就是死在第四次北伐，<b>從第九回活到第十九回，跨了十回。</b></p>"""},

{"html": """<div class="eyebrow">十七 · 這一回的話</div>
 <h2>懂道理，和做得到</h2>
 <div class="tier">
   <div><span class="lbl">馬謖</span><span>道理講得比誰都好，<b>做的時候全錯</b></span></div>
   <div><span class="lbl">王平</span><span>不認識幾個字，<b>每一步都對</b></span></div>
 </div>
 <div class="callout">讀書是為了<b>做得到</b>，<br>不是為了<b>說得好聽</b>。</div>""",
 "note": """<p>回到開場那個問題。<b>這是整套課對孩子最實用的一句話。</b></p>"""},

{"html": """<div class="eyebrow">最後</div>
 <h2>今天哪些是編的</h2>
 <div class="cols">
   <div class="card"><h3>編的</h3><p>
     <b>空城計</b>：出自《郭沖三事》，裴松之當場駁斥——<b>那年司馬懿在一千多里外</b><br><br>
     <b>司馬懿與諸葛亮在街亭對決</b>：沒有，對手是張郃<br><br>
     <b>馬謖被當眾斬首</b>：史書說法有三種，包括病死獄中</p></div>
   <div class="card"><h3>真的</h3><p>
     <b>違眾拔謖</b>：真的<br><br>
     <b>馬謖不照命令上山、王平力勸</b>：真的<br><br>
     <b>張郃斷水源</b>：真的<br><br>
     <b>王平收攏散兵</b>：真的，因此升官<br><br>
     <b>諸葛亮自貶三級</b>：真的<br><br>
     <b>帶回一千多戶百姓</b>：真的</p></div>
 </div>
 <div class="callout">最有名的那一段是假的，<br>最該學的那一段<b>沒什麼人記得</b>——<br><b>他把錯誤攬在自己身上。</b></div>""",
 "note": """<p>固定收尾頁。這一回的收尾特別有力，<b>慢慢唸。</b></p>"""},
]
