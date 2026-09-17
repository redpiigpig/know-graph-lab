# -*- coding: utf-8 -*-
"""第七回　群雄割據（192–198）

董卓死後，天下沒有中心。這一回節奏最快，是整套課的「洗牌」。
結尾收在白門樓——呂布的線從第五回拉到這裡結束。
"""

TITLE = "三國第七回"
MARK = "三國演義 · 第七回"
SUB = "群雄割據"

SLIDES = [
{"cover": True,
 "html": """<div class="art">
   <div class="txt">
     <div class="eyebrow">第七回</div>
     <h1>每個人<em>都在搶</em></h1>
     <p class="sub">中間那個人倒了，<br>結果不是天下太平，是大家開始互相搶。</p>
     <div class="meta">
       <div><dt>時間</dt><dd>西元 192–198 年</dd></div>
       <div><dt>這一回</dt><dd>群雄割據</dd></div>
       <div><dt>今天要弄懂</dt><dd>什麼叫「地盤」</dd></div>
     </div>
     <p class="credit">版畫與繡像取自維基共享資源，出處見上方「圖片來源」</p>
   </div>
   <div class="cast">
     ${cf(chr({robe:"#2E4A63",hat:"ze",beard:"mo",prop:"jian"}),"曹操","這一回他長大了")}
     ${im("map","天下被切成很多塊")}
   </div>
 </div>""",
 "note": """<p>這一回<b>人很多、事很多、節奏很快</b>。跟孩子先說：今天不用記住每個人的名字，記住<b>「地盤」</b>兩個字就好。</p>
 <p class="ask">開場問：「班上最大的那個人轉學了，會怎麼樣？」最後一頁回來對。</p>"""},

{"html": """<div class="eyebrow">一 · 上次講到哪</div>
 <h2>殺掉壞人之後，更亂了</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>董卓死了，王允也死了</li>
     <li>李傕、郭汜在長安<b>互相打了兩年</b></li>
     <li>皇帝被他們搶來搶去，<b>沒有人在管天下</b></li>
   </ul>
   <div class="callout">沒有人管，<br><b>就每個人自己管自己那一塊。</b></div>
 </div>
 <div class="cast tight">${ph("ehon_003_001","江戶時代畫的三國","《繪本通俗三國志》插圖")}</div></div>""",
 "note": """<p>接第六回結尾。「殺掉壞人不等於變好」這句可以再講一次。</p>"""},

{"html": """<div class="eyebrow">二 · 什麼叫地盤</div>
 <h2>誰的兵在那裡，那裡就是誰的</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>朝廷還在，但<b>命令傳不出去</b></li>
     <li>各地的太守、刺史<b>自己收稅、自己招兵</b></li>
     <li>名義上還是漢朝的官，實際上是<b>自己的老闆</b></li>
   </ul>
   <div class="callout">第一回說的<b>州、郡、縣</b>還在，<br>只是上面那個人<b>不管用了</b>。</div>
 </div>
 <div class="cast tight">${im("houses","自己的城")}${im("shield","自己的兵")}${im("money","自己收稅")}</div></div>""",
 "note": """<p>回頭指第一回的州郡縣那一頁。<b>制度沒變，是人不聽了。</b></p>
 <p class="ask">問：「一個人自己有兵、有錢、有城，他還需要皇帝嗎？」（需要——當招牌）</p>"""},

{"html": """<div class="eyebrow">三 · 撿到三十萬人</div>
 <h2>曹操的第一塊地盤</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>山東那邊還有<b>幾十萬黃巾軍</b>在流竄（第二回那批人的後代）</li>
     <li>曹操把他們打敗，然後做了一件別人沒做的事：<b>收編</b></li>
     <li>挑出能打的編成軍隊，其餘的<b>給田讓他們種</b></li>
   </ul>
   <div class="callout">別人看到流民只想趕走，<br>曹操看到的是<b>兵和糧</b>。</div>
   <p class="foot">這支部隊叫「青州兵」，是他後來打天下的老本。</p>
 </div>
 <div class="cast tight">${ph("granary2","收成","東漢陶囷，出土文物")}</div></div>""",
 "note": """<p>這是曹操和別人<b>第一個明顯的差別</b>：他會算「人可以拿來做什麼」。</p>
 <p>接回第二回結尾那句「兵，回不去了」——<b>現在有人給他們地方去了。</b></p>"""},

{"html": """<div class="eyebrow">四 · 最難講的一段</div>
 <h2>他爸爸在路上被殺了</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>曹操派人去接爸爸來享福</li>
     <li>路過徐州時，護送的兵<b>見財起意，把人殺了</b></li>
     <li>曹操認為是徐州的陶謙害的，<b>發兵報仇</b></li>
   </ul>
   <div class="callout">🚩 這一次出兵，<b>傷到很多沒有打仗的人</b>。<br>史書上的記載很難看。</div>
 </div>
 <div class="cast tight">${cf(chr({robe:"#2E4A63",hat:"ze",beard:"mo",sad:1}),"曹操","為父報仇")}${im("rain","徐州")}</div></div>""",
 "note": """<p>🚩 <b>點到為止就好，不要描述細節。</b>只要讓孩子知道：<b>打仗會傷到沒在打仗的人</b>，而且做這件事的正是我們一直在講的主角。</p>
 <p class="ask">問：「他很傷心，所以可以這樣嗎？」——不要給答案。這是第五回「曹操是壞人嗎」的第二次。</p>"""},

{"html": """<div class="eyebrow">五 · 劉備在哪裡</div>
 <h2>他終於有了一座城</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>陶謙擋不住曹操，向各地求救</li>
     <li>劉備帶著幾千人去了——<b>他跟陶謙非親非故</b></li>
     <li>陶謙病死前，把<b>整個徐州讓給他</b></li>
   </ul>
   <div class="callout">從第三回到現在，<b>十年</b>。<br>劉備第一次有了自己的地方。</div>
 </div>
 <div class="cast tight">${ph("liubei2","劉備","歷代名臣像冊")}${im("castle","徐州")}</div></div>""",
 "note": """<p>回頭數：第三回丟了小官，第四、五回打仗沒地盤，這裡才有城。<b>整整十年。</b></p>
 <p class="ask">問：「陶謙為什麼把城給一個外人？」（因為只有他肯來）</p>"""},

{"html": """<div class="eyebrow">六 · 收留他的人</div>
 <h2>呂布來投靠了</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>呂布從長安逃出來以後，<b>到處被拒絕</b></li>
     <li>劉備收留了他，讓他住在小沛</li>
     <li>結果劉備出兵在外時，呂布<b>把徐州拿走了</b></li>
   </ul>
   <div class="callout">第五回：為一匹馬殺義父。<br>第六回：為一個女孩殺義父。<br><b>這一回：為一座城，背叛收留他的人。</b></div>
 </div>
 <div class="cast tight">${ph("ehon_003_002","江戶時代畫的三國","《繪本通俗三國志》插圖")}</div></div>""",
 "note": """<p>三行一起唸。孩子會自己歸納出呂布的規律——<b>不要幫他們講出來。</b></p>"""},

{"html": """<div class="eyebrow">七 · 他也有講理的時候</div>
 <h2>轅門射戟</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>袁術派大軍要滅掉劉備，劉備向呂布求救</li>
     <li>呂布把兩邊都請來，把自己的戟插在一百五十步外</li>
     <li>他說：<b>我一箭射中小枝，你們就各自回家。</b></li>
   </ul>
   <div class="callout">他射中了。<br><b>兩邊真的都回去了。</b></div>
   <p class="foot">呂布不想任何一邊變太大——對他最好的，是他們一直吵下去。</p>
 </div>
 <div class="cast tight">${ph("yuanshu","袁術","清代繡像")}${im("bow","一百五十步")}</div></div>""",
 "note": """<p>孩子會覺得很帥。可以問：<b>他是為了幫劉備嗎？</b>（不是，是為了自己）</p>
 <p>這一頁示範<b>「同一件事可以有兩種讀法」</b>——整套課很重要的能力。</p>"""},

{"html": """<div class="eyebrow">八 · 十七歲的那個人</div>
 <h2>孫策：用一塊玉璽換三千兵</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>第五回孫堅撿到玉璽，後來<b>在打仗時中箭死了</b></li>
     <li>兒子孫策才十七歲，寄人籬下</li>
     <li>他把玉璽<b>押給袁術</b>，換來三千兵，回江東打天下</li>
   </ul>
   <div class="callout">兩年之內，他打下了<b>江東六個郡</b>。<br>那時候他<b>二十歲</b>。</div>
 </div>
 <div class="cast tight">${ph("sunce","孫策","清代繡像")}${ph("taishici","太史慈","被他打服的對手")}</div></div>""",
 "note": """<p>「二十歲打下六個郡」要講重——孫策是<b>整套課裡最年輕的狠角色</b>。</p>
 <p>那塊玉璽第五回埋的，這裡換掉了。<b>它會害死袁術。</b></p>"""},

{"html": """<div class="eyebrow">九 · 自己當皇帝的人</div>
 <h2>袁術：拿到玉璽就稱帝了</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>他覺得有玉璽＝天命在我，<b>直接自己當皇帝</b></li>
     <li>結果<b>沒有一個人承認他</b>——連他哥哥袁紹都不理</li>
     <li>大家聯手打他，兩年就完了</li>
   </ul>
   <div class="callout">他最後生病想喝一口<b>蜜水</b>，<br>廚房說：只有水，沒有蜜。</div>
   <p class="foot">他躺在床上大叫一聲，吐血死了。</p>
 </div>
 <div class="cast tight">${ic("crown")}${im("bowl","連蜜水都沒有")}</div></div>""",
 "note": """<p>「招牌」這條線的<b>反面教材</b>：拿著招牌卻自己稱帝，等於把招牌丟了。</p>
 <p class="ask">問：「有玉璽為什麼還不算皇帝？」（因為要別人承認才算）</p>"""},

{"html": """<div class="eyebrow">十 · 那一晚</div>
 <h2>曹操最痛的一次失敗</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>張繡本來已經投降，曹操做錯了一件事，張繡<b>半夜反叛</b></li>
     <li>曹操的<b>長子、姪子</b>都死在那一晚</li>
     <li>保護他逃出來的猛將<b>典韋</b>，守在門口戰死</li>
   </ul>
   <div class="callout">後來張繡<b>再一次投降</b>，<br>曹操<b>沒有殺他</b>，還讓兒子娶了他的女兒。</div>
 </div>
 <div class="cast tight">${ph("dianwei","典韋","戰死在門口")}${ph("zhangxiu","張繡","降了又反，反了又降")}</div></div>""",
 "note": """<p>這一頁講<b>曹操的另一面</b>：他會為了大局，忍下殺子之仇。和第五回那句「寧可我對不起別人」放在一起看，很有意思。</p>
 <p class="ask">問：「你做得到嗎？」</p>"""},

{"html": """<div class="eyebrow">十一 · 圍城</div>
 <h2>曹操和劉備聯手打呂布</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>呂布搶了徐州，四面都是敵人</li>
     <li>曹操圍下邳圍了<b>三個月</b>打不下來</li>
     <li>最後<b>引河水灌城</b>——城牆泡爛了</li>
   </ul>
   <div class="callout">城破那天，呂布的部下<b>趁他睡覺把他綁了</b>，<br>開城投降。</div>
 </div>
 <div class="cast tight">${ph("ehon_004_001","江戶時代畫的三國","《繪本通俗三國志》插圖")}</div></div>""",
 "note": """<p>「部下把他綁了」——呂布背叛過很多人，<b>最後被部下背叛。</b>不用點破，孩子會懂。</p>"""},

{"html": """<div class="eyebrow">十二 · 白門樓</div>
 <h2>他開口求饒了</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>呂布被綁在樓下，對曹操說：<b>「你帶步兵，我帶騎兵，天下就是你的。」</b></li>
     <li>曹操看起來有點動搖</li>
     <li>他回頭問旁邊的劉備：<b>「你覺得呢？」</b></li>
   </ul>
   <div class="callout">劉備只說了一句：<br><b>「你忘了丁原和董卓嗎？」</b></div>
   <p class="foot">曹操點了頭。呂布被吊死在白門樓。</p>
 </div>
 <div class="cast tight">${cf(chr({robe:"#2E4A63",hat:"wu",prop:"spear"}),"呂布","三十九歲")}${cf(chr({robe:"#8C2F1E",hat:"ze",beard:"mo"}),"劉備","說了一句話")}</div></div>""",
 "note": """<p><b>全回最重的一頁。</b>「你忘了丁原和董卓嗎」要慢慢唸——這句話<b>要了呂布的命</b>。</p>
 <p>丁原是第五回、董卓是第六回。<b>三回的線在這裡打結。</b></p>
 <p class="ask">問：「劉備為什麼要說這句話？」</p>"""},

{"html": """<div class="eyebrow">十三 · 不肯求饒的人</div>
 <h2>陳宮：我不說話</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>第五回放走曹操的那個陳宮，後來跟了呂布</li>
     <li>曹操問他：<b>「你這麼聰明，怎麼會落到這樣？」</b></li>
     <li>陳宮說：<b>「他不聽我的。」</b></li>
   </ul>
   <div class="callout">曹操問他家裡的老母親怎麼辦。<br>陳宮說：<b>「聽說以孝治天下的人不會殺人家的母親——那就看你了。」</b></div>
   <p class="foot">說完自己走向刑場，一次都沒有回頭。曹操哭著送他，養了他的家人一輩子。</p>
 </div>
 <div class="cast tight">${ph("ehon_004_002","江戶時代畫的三國","《繪本通俗三國志》插圖")}</div></div>""",
 "note": """<p>陳宮第五回出現過，<b>這裡收尾</b>。可以翻回去看他那張臉。</p>
 <p>同一天、同一座樓，<b>一個求饒、一個不求饒</b>。這個對比不用解釋。</p>"""},

{"html": """<div class="eyebrow">十三之二 · 北邊那個人</div>
 <h2>袁紹也沒有閒著</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>北方本來還有一個很強的人叫<b>公孫瓚</b>，外號「白馬將軍」</li>
     <li>兩個人打了<b>七年</b></li>
     <li>最後公孫瓚被圍在自己蓋的高樓裡，<b>放火自焚</b></li>
   </ul>
   <div class="callout">袁紹從此拿下<b>河北四個州</b>——<br>那時候天下最大的一塊。</div>
 </div>
 <div class="cast tight">${ph("gongsunzan","公孫瓚","白馬將軍")}${im("castle","自己蓋的高樓")}</div></div>""",
 "note": """<p>公孫瓚很重要的一點：<b>劉備年輕時跟他同學</b>（第三回提過的盧植門下），趙雲本來也是他的部下。</p>
 <p>這一頁是第九回官渡的鋪陳：<b>曹操要面對的，是一個剛打贏七年仗的人。</b></p>"""},

{"html": """<div class="eyebrow">十四 · 剩下誰</div>
 <h2>洗牌洗完了</h2>
 <div class="map">
   <div class="row"><span class="hi">曹操</span><span>兗州・豫州・徐州</span></div>
   <div class="row"><span class="hi">袁紹</span><span>河北四州（最大）</span></div>
   <div class="row"><span>孫策</span><span>江東六郡</span><span>劉表</span><span>荊州</span></div>
   <div class="row"><span>劉璋</span><span>益州</span><span>馬騰韓遂</span><span>西涼</span></div>
   <div class="row"><span class="cap">劉備</span><span>沒有地盤，寄住在曹操家裡</span></div>
 </div>
 <div class="callout">六年前有<b>十幾個</b>，現在剩<b>五、六個</b>。<br>而最大的那兩個，<b>在同一個方向</b>。</div>""",
 "note": """<p>一排一排指過去。最後一行要停一下：<b>劉備又沒有地盤了。</b></p>
 <p>下一回預告：曹操要做一件<b>其他人都想不到的事</b>。</p>"""},

{"html": """<div class="eyebrow">十五 · 兩個人的差別</div>
 <h2>同樣是打仗，想的不一樣</h2>
 <div class="cols">
   <div class="card">${pc("liubiao")}<h3>劉表　荊州</h3><p>地最好、糧最多、沒打過大仗。<b>只想守住現在的日子。</b></p></div>
   <div class="card">${pc("jiaxu")}<h3>賈詡　謀士</h3><p>張繡的軍師。他勸張繡<b>投降曹操</b>，理由是「曹操需要有人證明他容得下人」。</p></div>
 </div>
 <div class="callout">賈詡算的不是<b>誰比較強</b>，<br>是<b>對方現在需要什麼</b>。</div>""",
 "note": """<p>劉表是<b>「什麼都不做」的代表</b>，第十回他一死荊州就沒了。先埋。</p>
 <p>賈詡那一句很深，講不動就跳過，但可以問：「投降給誰比較安全？」</p>"""},

{"html": """<div class="eyebrow">十六 · 一個人的十年</div>
 <h2>劉備這十年在幹嘛</h2>
 <div class="tl">
   <div><span class="yr">184</span><span>桃園結義，招了五百人</span><span class="ago">第三回</span></div>
   <div><span class="yr">190</span><span>跟著聯軍打董卓，沒有座位</span><span class="ago">第五回</span></div>
   <div><span class="yr">194</span><span>接下徐州——第一塊地盤</span><span class="ago">這一回</span></div>
   <div><span class="yr">196</span><span>被呂布搶走</span><span class="ago">這一回</span></div>
   <div class="now"><span class="yr">198</span><span>又沒有地方去，投靠曹操</span><span class="ago">現在</span></div>
 </div>
 <div class="callout">十四年，<b>得到一次，失去一次</b>。<br>而他<b>還沒有放棄</b>。</div>""",
 "note": """<p>五行指過去。這是<b>劉備這個人的重點</b>——不是很會打，是<b>一直沒有放棄</b>。</p>
 <p>整套課到第十五回他死掉為止，這條線會一直拉著。</p>"""},

{"html": """<div class="eyebrow">十七 · 這一回的話</div>
 <h2>最大的那個人倒了，然後呢</h2>
 <div class="tier">
   <div><span class="lbl">192</span><span>董卓死，大家以為天下要太平了</span></div>
   <div><span class="lbl">193</span><span>各地自己收稅、自己招兵</span></div>
   <div><span class="lbl">196</span><span>互相吞併，十幾個變五、六個</span></div>
   <div><span class="lbl">198</span><span>呂布死，最會打的人也活不下來</span></div>
 </div>
 <div class="callout">沒有人管的時候，<br><b>不是每個人都自由，是大的吃掉小的。</b></div>""",
 "note": """<p>回到開場那個「最大的人轉學了」的問題，讓孩子自己說答案。</p>"""},

{"html": """<div class="eyebrow">最後</div>
 <h2>今天哪些是編的</h2>
 <div class="cols">
   <div class="card"><h3>編的</h3><p>
     <b>陶謙三讓徐州</b>：史書只說他臨終前交代把徐州給劉備，沒有三次<br><br>
     <b>白門樓劉備那一句</b>：史書有記，但寫得比較簡單<br><br>
     <b>袁術喊「蜜水」</b>：史書寫的是他想喝蜜漿而不可得，小說加了戲</p></div>
   <div class="card"><h3>真的</h3><p>
     <b>青州兵</b>：真的，三十萬人收編<br><br>
     <b>曹操為父報仇打徐州</b>：真的<br><br>
     <b>轅門射戟</b>：真的，史書有記<br><br>
     <b>孫策二十歲平江東</b>：真的<br><br>
     <b>陳宮不肯求饒、曹操養他家人</b>：真的</p></div>
 </div>
 <div class="callout">這一回<b>真的比編的多</b>——<br>因為這六年的事<b>本身就夠亂了</b>，小說不用加。</div>""",
 "note": """<p>固定收尾頁。這一回可以強調：<b>有時候真實比小說還精彩。</b></p>"""},
]
