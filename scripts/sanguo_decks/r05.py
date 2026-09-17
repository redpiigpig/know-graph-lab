# -*- coding: utf-8 -*-
"""第五回　十八路諸侯（西元 190 年）

接第四回結尾：洛陽燒了、皇帝被董卓帶去長安。
這一回是主角群第一次站到同一個畫面裡，也是「大家一起做一件事，
結果誰都不肯先動」的第一個例子。

體例見 docs/sanguo-tutoring-20-lessons.md。
"""

TITLE = "三國第五回"
MARK = "三國演義 · 第五回"
SUB = "十八路諸侯"

SLIDES = [
{"cover": True,
 "html": """<div class="art">
   <div class="txt">
     <div class="eyebrow">第五回</div>
     <h1>十八路<em>諸侯</em></h1>
     <p class="sub">全國的軍隊都來了，圍住同一個壞人。<br>可是沒有一個人肯先往前走。</p>
     <div class="meta">
       <div><dt>時間</dt><dd>西元 190 年，洛陽以東</dd></div>
       <div><dt>這一回</dt><dd>聯軍討董卓</dd></div>
       <div><dt>今天要弄懂</dt><dd>人多，為什麼反而做不成事</dd></div>
     </div>
     <p class="credit">版畫與繡像取自維基共享資源，出處見上方「圖片來源」</p>
   </div>
   <div class="cast">
     ${cf(chr({robe:"#2E4A63",hat:"ze",beard:"mo",prop:"jian"}),"曹操","這一回他第一次出場")}
     ${im("flag","十八面旗子")}
   </div>
 </div>""",
 "note": """<p>這一回的主角群第一次<b>全部到齊</b>：曹操、袁紹、孫堅、呂布，劉關張也會出現。跟孩子說「今天人很多」，先有心理準備。</p>
 <p class="ask">開場問：「分組打掃，全班都在，結果掃得比較乾淨還是比較髒？」記下答案，最後一頁回來對。</p>"""},

{"html": """<div class="eyebrow">一 · 上次講到哪</div>
 <h2>洛陽，已經沒有了</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>董卓把皇帝<b>換成九歲的劉協</b>（漢獻帝）</li>
     <li>他把兩百年的洛陽<b>一把火燒掉</b>，帶著皇帝搬去<b>長安</b></li>
     <li>皇帝變成一塊<b>招牌</b>——誰手上有他，誰說的話就算數</li>
   </ul>
   <div class="callout">上一回最後那個問題：<br><b>沒有人能管董卓了嗎？</b></div>
 </div>
 <div class="cast tight">${cf(wall(),"洛陽","燒掉以前的樣子")}${im("fire","一把火")}</div></div>""",
 "note": """<p>「招牌」這個詞第四回正式成立，這一回要<b>再用一次</b>——整套課固定用這個詞，不要換成「傀儡」。</p>
 <p>小孩可能會問「皇帝為什麼不跑」。答：他才九歲，而且外面全是董卓的兵。</p>"""},

{"html": """<div class="eyebrow">二 · 有人不服氣</div>
 <h2>一個管首都治安的小官</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>他叫<b>曹操</b>，那年三十五歲</li>
     <li>爸爸花錢買過很大的官，所以家裡有錢，但<b>被人看不起</b></li>
     <li>他做過洛陽北邊的城門官，<b>誰犯規就打誰</b>——連大官的親戚也打</li>
   </ul>
   <div class="callout">董卓想拉攏他，給他官做。<br>曹操的回答是：<b>我不要。</b></div>
 </div>
 <div class="cast tight">${ph("caocao","曹操","清代繡像")}</div></div>""",
 "note": """<p>曹操是<b>整套課的第二主角</b>，這一頁是他的自我介紹，要講慢一點。</p>
 <p>「爸爸買官」呼應第四回的漢靈帝賣官——<b>買官的錢就是從那裡來的</b>。可以回頭指一下。</p>
 <p class="ask">問：「家裡有錢，為什麼還會被看不起？」（因為錢是買來的，不是考來的）</p>"""},

{"html": """<div class="eyebrow">三 · 小說裡的那一刀</div>
 <h2>他帶了一把刀去見董卓</h2>
 <div class="art wide"><div class="txt">
   <ul class="pts">
     <li>小說說：曹操借了一把<b>七寶刀</b>，說要獻給董卓</li>
     <li>董卓躺著休息，背對著他——<b>機會來了</b></li>
     <li>可是董卓從鏡子裡<b>看見了</b></li>
     <li>曹操馬上跪下說：「我是來<b>獻刀</b>的。」</li>
   </ul>
   <div class="callout">一秒之內，<b>刺客變成送禮的人</b>。<br>他說完就走，走出門就拚命跑。</div>
 </div>
 ${mp("presentblade","曹孟德謀殺董卓","清代版畫：右邊躺著的是董卓，跪著的是曹操")}</div>""",
 "note": """<p>孩子最愛這一段，講的時候<b>停在「董卓從鏡子裡看見」那一秒</b>，讓他們緊張一下。</p>
 <p>要先講明白：<b>這一段是小說編的</b>，但先不要破壞氣氛，最後一頁再說。</p>
 <p class="ask">問：「如果是你，被看到的那一秒會說什麼？」</p>"""},

{"html": """<div class="eyebrow">四 · 逃</div>
 <h2>路上有人認出他</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>曹操往東逃，被一個縣的官抓到</li>
     <li>那個官叫<b>陳宮</b>，他認得曹操，也知道抓他有賞</li>
     <li>可是陳宮問了一句：<b>「你為什麼要殺董卓？」</b></li>
     <li>聽完答案，陳宮<b>把官丟了，跟他一起跑</b></li>
   </ul>
   <div class="callout">這一段也是小說編的。<br>但它要說的事是真的：<b>那時候很多人願意為一句話賭上全部。</b></div>
 </div>
 <div class="cast tight">${ph("chengong","陳宮","清代繡像")}${im("horse","連夜逃走")}</div></div>""",
 "note": """<p>陳宮這個人<b>第七回還會再出現一次</b>（白門樓），而且死得很有骨氣。這裡先讓孩子記住臉。</p>"""},

{"html": """<div class="eyebrow">五 · 最難講的一段</div>
 <h2>他殺了一家人</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>兩人逃到曹操爸爸的老朋友<b>呂伯奢</b>家借住</li>
     <li>半夜聽見後面有<b>磨刀的聲音</b>，還有人說「綁起來再殺」</li>
     <li>曹操以為要抓他，<b>先動手了</b>——結果那家人在<b>殺豬請客</b></li>
   </ul>
   <div class="callout">陳宮罵他。曹操說了一句很有名的話：<br><b>「寧可我對不起別人，不要別人對不起我。」</b></div>
   <p class="foot">陳宮聽完，半夜自己走了。</p>
 </div>
 <div class="cast tight">${ph("luboshe","呂伯奢","清代繡像")}</div></div>""",
 "note": """<p>🚩 <b>這一頁不要講得太快，也不要幫他找理由。</b>問孩子怎麼想，聽他們說完就好。</p>
 <p>史書上有三種說法：一種說呂家人真的要搶他，一種說是誤殺，那句話出自其中一種。<b>小說把最狠的那一種選進去了。</b></p>
 <p class="ask">問：「曹操是壞人嗎？」——不要給答案。這個問題會跟著整套課走到第十四回。</p>"""},

{"html": """<div class="eyebrow">六 · 一封信</div>
 <h2>他寫了一封假的聖旨</h2>
 <div class="art wide"><div class="txt">
   <ul class="pts">
     <li>曹操逃回老家，<b>把家產全部賣掉</b>，招了五千人</li>
     <li>可是五千人打不過董卓的幾十萬</li>
     <li>所以他做了一件很大膽的事：<b>寫一封假的皇帝命令</b>，送到各地</li>
   </ul>
   <div class="callout">信上寫：<b>皇帝有難，請大家一起來救。</b><br>皇帝其實不知道有這封信。</div>
 </div>
 ${mp("jiaozhao","發矯詔響應曹公","清代版畫")}</div>""",
 "note": """<p>「矯詔」＝假造的皇帝命令。用<b>「假聖旨」</b>三個字就好，不要教文言詞。</p>
 <p>這是第二次用到「招牌」的邏輯：<b>他手上沒有皇帝，就自己做一塊。</b></p>
 <p class="ask">問：「用假的命令做對的事，可以嗎？」</p>"""},

{"html": """<div class="eyebrow">七 · 來了</div>
 <h2>十八支軍隊，同時出發</h2>
 <div class="art wide"><div class="txt">
   <ul class="pts">
     <li>信送出去以後，各地的太守、刺史<b>真的帶兵來了</b></li>
     <li>小說說<b>十八路</b>，史書上數得出來的<b>大概十一路</b></li>
     <li>加起來<b>十幾萬人</b>，在洛陽東邊集合</li>
   </ul>
   <div class="callout">這是整個故事裡，<b>好人們唯一一次站在同一邊</b>。<br>以後再也沒有了。</div>
 </div>
 ${mp("map_warlords","他們從這些地方來","漢末群雄割據圖")}</div>""",
 "note": """<p>指地圖：<b>他們從四面八方來，但都在洛陽東邊。</b>洛陽西邊是董卓的老家（涼州），沒人敢從那邊來。</p>
 <p>「唯一一次站在同一邊」這句話要講重，<b>整回的悲哀都在這裡</b>。</p>"""},

{"html": """<div class="eyebrow">八 · 誰當老大</div>
 <h2>選了家世最好的那一個</h2>
 <div class="cols">
   <div class="card">${chr({robe:"#7A6A4F",hat:"jin",beard:"mo",prop:"jian"})}<h3>袁紹　盟主</h3><p>家裡<b>四代出大官</b>，認識的人最多。第四回出主意叫董卓進京的，就是他。</p></div>
   <div class="card">${pc("caocao")}<h3>曹操　跟班</h3><p>發信的人是他，兵最少，<b>連座位都排在後面</b>。</p></div>
 </div>
 <div class="callout">選老大的標準不是<b>誰最會打</b>，<br>是<b>誰的爸爸和爺爺比較有名</b>。</div>
 <p class="foot">第一回說過：那時候當官不用考試，看的是家世。這裡又出現一次。</p>""",
 "note": """<p>回頭指第一回<b>「當官不用考試」</b>那一頁，這是同一件事的後果。</p>
 <p>提醒：袁紹就是第四回出餿主意的人。<b>害事情變這樣的人，現在當了老大。</b>孩子會覺得很不公平——那就對了。</p>"""},

{"html": """<div class="eyebrow">九 · 真的在打的人</div>
 <h2>只有一支軍隊往前走</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>江東來的<b>孫堅</b>，自願打頭陣</li>
     <li>他是這一群人裡<b>最會打仗</b>的</li>
     <li>可是負責送糧的人<b>故意不給他糧食</b>——怕他立功</li>
   </ul>
   <div class="callout">前面在打仗，後面在算計。<br><b>這就是這支聯軍的樣子。</b></div>
 </div>
 <div class="cast tight">${ph("sunjian","孫堅","清代繡像")}${im("flag","打頭陣")}</div></div>""",
 "note": """<p>孫堅是<b>吳國的爺爺輩</b>——第七回他兒子孫策會接手，第十回孫權就是吳國的老闆。先讓孩子記住這個姓。</p>
 <p class="ask">問：「自己人為什麼不給他糧食？」（怕他功勞太大）</p>"""},

{"html": """<div class="eyebrow">十 · 擋路的人</div>
 <h2>對面有個很強的將軍</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>董卓派出<b>華雄</b>守關口</li>
     <li>聯軍派了幾個人上去，<b>一個一個被打倒</b></li>
     <li>大家都不敢出聲了</li>
   </ul>
   <div class="callout">這時候，有一個<b>沒有官位</b>的人站起來說：<br><b>「我去。」</b></div>
 </div>
 <div class="cast tight">${im("sword","誰敢去")}${im("shield","沒有人動")}</div></div>""",
 "note": """<p>這一頁是<b>鋪梗</b>，不要提關羽的名字，讓孩子自己猜。</p>
 <p>「沒有官位」很重要——下一頁的重點就是<b>大家看不起他</b>。</p>"""},

{"html": """<div class="eyebrow">十一 · 那杯酒</div>
 <h2>酒還是熱的</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>站起來的是<b>關羽</b>——當時只是劉備手下的<b>弓馬手</b></li>
     <li>袁紹那邊的人笑他：<b>「一個小兵也敢說話？」</b></li>
     <li>曹操倒了一杯熱酒給他：<b>「喝完再去。」</b></li>
     <li>關羽說：<b>「酒先放著，我回來再喝。」</b></li>
   </ul>
   <div class="callout">他提著華雄的頭回來的時候，<br><b>那杯酒還是熱的。</b></div>
 </div>
 <div class="cast tight">${ph("guanyu","關羽","清代繡像")}${im("tea","還沒涼")}</div></div>""",
 "note": """<p><b>全回最有畫面的一頁</b>，慢慢講，「還是熱的」四個字要停一下。</p>
 <p>這一段是小說編的（史書上華雄是<b>孫堅</b>殺的），但先不要說破，最後一頁再講。</p>
 <p>順便提：第三回說過關羽是<b>紅臉綠袍</b>，這裡可以指圖對照。</p>"""},

{"html": """<div class="eyebrow">十二 · 最後一關</div>
 <h2>虎牢關前，來了一個人</h2>
 <div class="art wide"><div class="txt">
   <ul class="pts">
     <li>華雄死了，董卓親自帶兵出來</li>
     <li>擋在關前的是<b>呂布</b></li>
     <li>聯軍一連派出好幾個有名的將軍，<b>沒有一個撐得住</b></li>
   </ul>
   <div class="callout">那時候流行一句話：<br><b>人裡面最強的是呂布，馬裡面最好的是赤兔。</b></div>
 </div>
 ${mp("hulao","虎牢關前的呂布","清代版畫")}</div>""",
 "note": """<p>「人中呂布，馬中赤兔」這句話<b>是真的流傳下來的</b>，可以寫在黑板上。</p>"""},

{"html": """<div class="eyebrow">十三 · 他是誰</div>
 <h2>最會打的人，也最會換老闆</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>呂布本來是<b>丁原</b>的手下，認丁原當義父</li>
     <li>董卓送他<b>一匹赤兔馬</b>和很多金子</li>
     <li>他就<b>殺了丁原</b>，改認董卓當義父</li>
   </ul>
   <div class="callout">一匹馬，換一個爸爸。<br><b>這件事第六回還會再發生一次。</b></div>
 </div>
 <div class="cast tight">${ph("lvbu","呂布","清代繡像")}${ph("dingyuan","丁原","被他殺掉的義父")}</div></div>""",
 "note": """<p>「義父」這個詞<b>第六回會出現三次</b>，這裡第一次埋。整套課固定用「義父」，不要換成「乾爹」。</p>
 <p class="ask">問：「為什麼有人肯為了一匹馬殺人？」（因為那匹馬代表『有人看得起我』）</p>"""},

{"html": """<div class="eyebrow">十四 · 三個打一個</div>
 <h2>三兄弟一起上</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>張飛先衝出去，打了五十幾回合<b>沒有輸</b></li>
     <li>關羽看不下去，<b>加進來</b></li>
     <li>還是分不出勝負，劉備<b>也衝上去</b></li>
   </ul>
   <div class="callout">三個人圍著一個人打，<br><b>呂布還是全身而退。</b></div>
   <p class="foot">這是三兄弟第一次打出名號——雖然是三個打一個。</p>
 </div>
 <div class="cast tight">${cf(chr({robe:"#8C2F1E",hat:"ze",beard:"mo"}),"劉備")}${cf(chr({robe:"#4F7460",hat:"jin",beard:"long",prop:"dao"}),"關羽")}${cf(chr({robe:"#3C3630",hat:"wu",beard:"long",fat:1,prop:"spear"}),"張飛")}</div></div>""",
 "note": """<p>這一段<b>完全是小說編的</b>，但它是三國最有名的畫面之一，孩子在電動和漫畫裡都看過。</p>
 <p class="ask">問：「三個打一個，很厲害還是很丟臉？」——小說其實在誇呂布。</p>"""},

{"html": """<div class="eyebrow">十五 · 然後呢</div>
 <h2>然後就沒有然後了</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>打贏了前哨戰，董卓退回長安</li>
     <li>曹操說：<b>現在追，一次就能解決。</b></li>
     <li>其他人說：<b>兵累了，明天再說。</b></li>
     <li>曹操自己追出去，<b>被打得只剩幾百人</b></li>
   </ul>
   <div class="callout">他回來的時候，<br><b>其他人正在營裡喝酒。</b></div>
 </div>
 <div class="cast tight">${im("lantern","營裡的燈")}${im("bowl","還在喝")}</div></div>""",
 "note": """<p><b>整回的轉折在這裡。</b>前面講了那麼多熱血，這一頁把它戳破。</p>
 <p>曹操這次差點死掉（被箭射中，堂弟曹洪把馬讓給他）。<b>他從此不再相信「大家一起來」。</b>這是他後來所有選擇的起點。</p>"""},

{"html": """<div class="eyebrow">十六 · 散了</div>
 <h2>糧食沒了，人也散了</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>十幾萬人每天要吃飯，<b>誰出糧</b>吵不完</li>
     <li>有人開始<b>搶別人的地盤</b>——本來是來打董卓的</li>
     <li>其中一路的老大，<b>被另一路的老大殺掉</b></li>
   </ul>
   <div class="callout">聯軍成立不到<b>一年</b>就散了。<br>董卓還活著，在長安，好好的。</div>
 </div>
 <div class="cast tight">${im("grain","糧食")}${im("flag","各回各家")}</div></div>""",
 "note": """<p>回到開場那個掃地的問題：<b>人多不一定做得成事，要看有沒有人願意先動。</b></p>
 <p>「本來是來打董卓的」這句要講重——<b>目標不見了，就開始互相打。</b></p>"""},

{"html": """<div class="eyebrow">十七 · 井裡的東西</div>
 <h2>孫堅在井裡撈到一塊石頭</h2>
 <div class="art wide"><div class="txt">
   <ul class="pts">
     <li>孫堅的兵最早進洛陽，看見一口井<b>冒著光</b></li>
     <li>撈上來是一個宮女的屍體，身上綁著一個小盒子</li>
     <li>盒子裡是<b>傳國玉璽</b>——皇帝蓋章用的那顆印</li>
   </ul>
   <div class="callout">誰有這顆印，誰就像是<b>真的皇帝</b>。<br>孫堅把它<b>藏起來</b>，偷偷回家了。</div>
 </div>
 ${mp("jadeseal","孫堅背約奪玉璽","清代版畫：左下角是井和宮女")}</div>""",
 "note": """<p>「招牌」在這一回的<b>第三種樣子</b>：第四回是皇帝本人，第六頁是假聖旨，這裡是一顆印。</p>
 <p>這顆印<b>第七回會害死孫堅一家</b>（袁術用它當皇帝）。先埋著。</p>
 <p class="ask">問：「撿到就變成皇帝，這樣合理嗎？」</p>"""},

{"html": """<div class="eyebrow">十八 · 這一回的話</div>
 <h2>大家都在，等別人先走</h2>
 <div class="tl">
   <div><span class="yr">190</span><span>十八路諸侯集合</span><span class="ago">熱血</span></div>
   <div><span class="yr">190</span><span>關羽斬華雄、三英戰呂布</span><span class="ago">高潮</span></div>
   <div><span class="yr">190</span><span>曹操要追，沒有人跟</span><span class="ago">轉折</span></div>
   <div><span class="yr">191</span><span>糧盡、內鬨、自己人殺自己人</span><span class="ago">散場</span></div>
   <div class="now"><span class="yr">191</span><span>董卓還活著，天下多了十幾個軍閥</span><span class="ago">結果</span></div>
 </div>
 <div class="callout">這一回沒有壞人贏，<br>也<b>沒有好人贏</b>——因為好人們<b>沒有真的一起做事</b>。</div>""",
 "note": """<p>五行一行一行指過去，這是整回的<b>總結</b>。</p>
 <p>最後接回開場的掃地問題，讓孩子自己說答案。</p>
 <p>下一回預告：<b>打不倒董卓的人這麼多，最後動手的只有一個——而且用的不是刀。</b></p>"""},

{"html": """<div class="eyebrow">最後</div>
 <h2>今天哪些是編的</h2>
 <div class="cols">
   <div class="card"><h3>編的</h3><p>
     <b>曹操獻刀</b>：史書上他只是<b>不接受董卓給的官，直接跑了</b><br><br>
     <b>陳宮放他</b>：陳宮是後來才跟曹操的<br><br>
     <b>溫酒斬華雄</b>：華雄是<b>孫堅</b>殺的<br><br>
     <b>三英戰呂布</b>：完全沒有這件事</p></div>
   <div class="card"><h3>真的</h3><p>
     <b>各地起兵打董卓</b>：真的，大約十一路<br><br>
     <b>人中呂布，馬中赤兔</b>：當時真的這樣說<br><br>
     <b>曹操自己追出去慘敗</b>：真的<br><br>
     <b>聯軍自己打起來</b>：真的<br><br>
     <b>孫堅得到玉璽</b>：史書有記，但說法不一</p></div>
 </div>
 <div class="callout">小說為什麼要編？<br>因為它想讓<b>關羽和劉備早一點變厲害</b>——<br>史書上這時候，他們還沒有人注意到。</div>""",
 "note": """<p>固定收尾頁。<b>先問孩子記得哪一段最清楚</b>，再揭曉那段多半是編的——他們會笑。</p>
 <p>重點不是「小說騙人」，是<b>「小說想讓你喜歡誰」</b>。這句話整套課會用二十次。</p>"""},
]
