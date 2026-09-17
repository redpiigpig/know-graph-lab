# -*- coding: utf-8 -*-
"""第六回　連環計（西元 192 年）

接第五回結尾：聯軍散了，董卓還活著、在長安。
十幾萬大軍做不到的事，三個人在屋子裡做到了。

用圖原則見 docs/sanguo-tutoring-20-lessons.md：真圖每張只用一次，
重複出現的角色在其他回改用 Q 版 SVG。
"""

TITLE = "三國第六回"
MARK = "三國演義 · 第六回"
SUB = "連環計"

SLIDES = [
{"cover": True,
 "html": """<div class="art">
   <div class="txt">
     <div class="eyebrow">第六回</div>
     <h1>一個計謀，<em>兩個人</em></h1>
     <p class="sub">十幾萬大軍做不到的事，<br>三個人在一間屋子裡做到了。</p>
     <div class="meta">
       <div><dt>時間</dt><dd>西元 192 年，長安</dd></div>
       <div><dt>這一回</dt><dd>王允與連環計</dd></div>
       <div><dt>今天要弄懂</dt><dd>什麼叫「離間」</dd></div>
     </div>
     <p class="credit">版畫與繡像取自維基共享資源，出處見上方「圖片來源」</p>
   </div>
   <div class="cast">
     ${cf(chr({robe:"#7A6A4F",hat:"ru",beard:"long"}),"王允","六十歲的老臣")}
     ${im("lantern","一場夜宴")}
   </div>
 </div>""",
 "note": """<p>這一回<b>沒有大場面</b>，全部發生在室內。跟孩子講清楚：今天看的是「用嘴巴打仗」。</p>
 <p class="ask">開場問：「兩個很要好的人，怎麼樣會吵架？」把答案記在旁邊，最後一頁回來對。</p>"""},

{"html": """<div class="eyebrow">一 · 上次講到哪</div>
 <h2>十幾萬人，什麼都沒改變</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>十八路諸侯<b>散了</b>，還自己打起來</li>
     <li>董卓<b>好好的</b>，帶著皇帝住在長安</li>
     <li>他現在比以前<b>更不怕任何人</b></li>
   </ul>
   <div class="callout">打不贏的時候，<br><b>還有別的方法嗎？</b></div>
 </div>
 <div class="cast tight">${ph("dongzhuo2","董卓","清代繡像")}</div></div>""",
 "note": """<p>這一頁是橋。第五回講「人多也沒用」，這一回要講「人少也可以」。</p>"""},

{"html": """<div class="eyebrow">二 · 他給自己蓋的城</div>
 <h2>郿塢：牆和長安一樣高</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>董卓在長安西邊蓋了一座<b>私人的城</b>，叫郿塢</li>
     <li>城牆的厚度和高度，<b>和首都一樣</b></li>
     <li>裡面存了<b>夠吃三十年</b>的糧食</li>
   </ul>
   <div class="callout">他說：事情成了，我就統治天下；<br>不成，<b>我就守在這裡過完一輩子。</b></div>
 </div>
 <div class="cast tight">${ph("granary","存糧","東漢陶倉，出土文物")}${im("grain","三十年份")}</div></div>""",
 "note": """<p>陶倉那張圖要指給孩子看：<b>漢朝人真的用這種倉存糧</b>，墓裡放一個縮小版陪葬。</p>
 <p class="ask">問：「一個人要存三十年的糧食做什麼？」（因為他知道很多人想殺他）</p>"""},

{"html": """<div class="eyebrow">三 · 沒有人敢</div>
 <h2>朝廷上，沒有人說話</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>有人在宴會上講錯一句話，<b>當場被拖出去</b></li>
     <li>大臣們<b>手抖到拿不住筷子</b>，還要裝作沒事</li>
     <li>大家都在等別人先動手——<b>和第五回一模一樣</b></li>
   </ul>
   <div class="callout">全長安只有一個人在想辦法，<br>而且他<b>誰都沒有告訴</b>。</div>
 </div>
 <div class="cast tight">${ph("ehon_006_002","江戶時代的三國插圖","《繪本通俗三國志》")}</div></div>""",
 "note": """<p>「等別人先動手」這條線<b>第五回埋的</b>，這裡收一次。回頭指一下。</p>"""},

{"html": """<div class="eyebrow">四 · 那個老臣</div>
 <h2>王允：白天笑，晚上哭</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>他在朝廷上<b>對董卓很客氣</b>，還幫他辦事</li>
     <li>董卓因此很信任他</li>
     <li>可是每天晚上，他一個人在院子裡<b>哭到天亮</b></li>
   </ul>
   <div class="callout">他已經<b>六十歲</b>了。<br>他知道自己<b>打不動，也跑不掉</b>。</div>
 </div>
 <div class="cast tight">${ph("wangyun","王允","清代繡像")}${im("tea","裝作沒事")}</div></div>""",
 "note": """<p>「白天笑、晚上哭」這一句要講慢。孩子對「假裝」這件事很有感覺。</p>
 <p class="ask">問：「為什麼他要對壞人客氣？」（因為他在等機會）</p>"""},

{"html": """<div class="eyebrow">五 · 小說裡的那個人</div>
 <h2>一個十六歲的女孩</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>小說說：王允家裡有個養女，叫<b>貂蟬</b></li>
     <li>那天晚上她看見王允在哭，問他怎麼了</li>
     <li>她說：<b>「有什麼我做得到的，我去做。」</b></li>
   </ul>
   <div class="callout">王允跪下來拜她。<br>一個六十歲的大官，<b>跪一個十六歲的女孩。</b></div>
 </div>
 <div class="cast tight">${ph("diaochan","貂蟬","清代繡像")}</div></div>""",
 "note": """<p>貂蟬<b>是小說創造的人物</b>——史書上只寫「董卓有個侍女，呂布和她有來往」，連名字都沒有。最後一頁會講。</p>
 <p>🚩 這一段不要講成「用美色」。重點放在<b>她是自願的、她知道自己在做什麼</b>。</p>"""},

{"html": """<div class="eyebrow">六 · 兩個人的關係</div>
 <h2>他們是「義父子」</h2>
 <div class="cols">
   <div class="card">${pc("dongzhuo2")}<h3>董卓</h3><p>五十幾歲，全國最有權力的人。<b>怕死</b>，所以到哪裡都帶著呂布。</p></div>
   <div class="card">${pc("lvbu2")}<h3>呂布</h3><p>三十幾歲，全國最會打的人。<b>已經為了一匹馬換過一次義父。</b></p></div>
 </div>
 <div class="callout">第五回說過：一匹馬，換一個爸爸。<br><b>那這一次呢？</b></div>""",
 "note": """<p>「義父」這個詞<b>第五回埋的</b>，這一回會出現三次。整套課固定用「義父」不要換詞。</p>
 <p class="ask">問：「你覺得呂布真的把董卓當爸爸嗎？」</p>"""},

{"html": """<div class="eyebrow">七 · 計謀</div>
 <h2>把同一個人，許給兩個人</h2>
 <div class="tier">
   <div><span class="lbl">第一步</span><span>先請<b>呂布</b>到家裡，說要把貂蟬嫁給他</span></div>
   <div><span class="lbl">第二步</span><span>再請<b>董卓</b>到家裡，說要把貂蟬送給他</span></div>
   <div><span class="lbl">第三步</span><span><b>什麼都不用做</b>，等他們自己發現</span></div>
 </div>
 <div class="callout">這叫<b>連環計</b>——<br>一個扣一個，前面那一步會拉動後面那一步。</div>
 <p class="foot">王允全程沒有說過任何一句假話。他只是<b>沒有告訴他們對方的事</b>。</p>""",
 "note": """<p><b>整回最重要的一頁。</b>三步一步一步指過去，讓孩子先想想這樣會發生什麼。</p>
 <p>「沒有說假話，只是沒說全部」——這句話值得停一下。</p>"""},

{"html": """<div class="eyebrow">八 · 第一場</div>
 <h2>先請呂布</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>王允擺了一桌很好的酒菜，只請呂布一個人</li>
     <li>席間叫貂蟬出來敬酒</li>
     <li>呂布看呆了。王允說：<b>「送給你，挑個日子來娶。」</b></li>
   </ul>
   <div class="callout">呂布高興得站起來<b>謝了又謝</b>。</div>
 </div>
 <div class="cast tight">${ph("mirror","梳妝","漢代銅鏡，出土文物")}${im("cash","一桌好酒菜")}</div></div>""",
 "note": """<p>銅鏡那張可以順便講：<b>漢朝人照的鏡子是銅做的，磨亮才照得出人。</b>孩子會覺得新鮮。</p>"""},

{"html": """<div class="eyebrow">九 · 第二場</div>
 <h2>過幾天，再請董卓</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>同樣一桌酒，同樣叫貂蟬出來</li>
     <li>王允說：<b>「送給太師吧。」</b></li>
     <li>董卓當天晚上就<b>把人帶回家了</b></li>
   </ul>
   <div class="callout">王允從頭到尾<b>沒有提過呂布</b>。<br>董卓也<b>沒有問</b>。</div>
 </div>
 <div class="cast tight">${ph("lamp","那天的燈","漢代青銅燈，出土文物")}</div></div>""",
 "note": """<p>「沒有提、沒有問」——王允算準了<b>兩個人都不會查</b>。</p>
 <p class="ask">問：「如果董卓多問一句，會怎麼樣？」（整個計謀就破了）</p>"""},

{"html": """<div class="eyebrow">十 · 發現</div>
 <h2>呂布去問，被罵回來</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>呂布等著娶親，結果聽說人在董卓家裡</li>
     <li>他跑去問王允。王允裝作很驚訝：<b>「太師說要替你辦喜事啊。」</b></li>
     <li>呂布去問董卓，董卓<b>當場翻臉</b></li>
   </ul>
   <div class="callout">從這一天起，<br>呂布看董卓的眼神<b>就不一樣了</b>。</div>
 </div>
 <div class="cast tight">${im("dagger","心裡有刺")}${im("flag","裂痕")}</div></div>""",
 "note": """<p>這就是<b>「離間」</b>——不用打，讓對方自己裂開。把這兩個字寫在黑板上。</p>"""},

{"html": """<div class="eyebrow">十一 · 那座亭子</div>
 <h2>鳳儀亭</h2>
 <div class="art wide"><div class="txt">
   <ul class="pts">
     <li>有一天董卓生病，呂布去探望</li>
     <li>他在後花園的亭子裡遇見貂蟬</li>
     <li>兩個人正在說話——<b>董卓醒了，走出來看見</b></li>
   </ul>
   <div class="callout">董卓抄起呂布的<b>方天畫戟</b>，<br>從後面<b>直接丟過去</b>。</div>
   <p class="foot">呂布躲開了，一路跑出府外。</p>
 </div>
 ${mp("ehon_009_002","江戶時代畫的三國","《繪本通俗三國志》插圖")}</div>""",
 "note": """<p>「用他自己的武器丟他」這個細節很有戲，慢慢講。</p>
 <p>這一段小說寫得非常精彩，但<b>史書只有一句</b>：呂布和董卓的侍女有來往，怕被發現，心裡不安。</p>"""},

{"html": """<div class="eyebrow">十二 · 最後一句話</div>
 <h2>王允只補了一句</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>呂布氣得發抖，跑去找王允</li>
     <li>王允沒有勸他，也沒有罵董卓</li>
     <li>他只問了一句：<b>「將軍姓呂，太師姓董，這算哪門子父子？」</b></li>
   </ul>
   <div class="callout">一句話，<b>把「義父」這兩個字拆掉了</b>。</div>
 </div>
 <div class="cast tight">${cf(chr({robe:"#7A6A4F",hat:"ru",beard:"long"}),"王允","只說了一句")}${cf(chr({robe:"#2E4A63",hat:"wu",prop:"spear"}),"呂布","聽進去了")}</div></div>""",
 "note": """<p><b>全回最厲害的一頁。</b>王允等了好幾個月，就為了說這一句。</p>
 <p>「義父」第三次出現——而且是<b>被拆掉</b>的那一次。</p>"""},

{"html": """<div class="eyebrow">十三 · 動手</div>
 <h2>宮門口，呂布在等</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>王允假傳消息：<b>皇帝要把皇位讓給太師</b></li>
     <li>董卓高興得馬上進宮</li>
     <li>車子壞了兩次、馬也受驚，他<b>都沒有回頭</b></li>
   </ul>
   <div class="callout">走到宮門口，四面的兵圍上來。<br>他大喊：<b>「呂布在哪裡？」</b><br>呂布從後面走出來：<b>「在這裡。」</b></div>
 </div>
 <div class="cast tight">${ph("ehon_013_002","江戶時代畫的三國","《繪本通俗三國志》插圖")}</div></div>""",
 "note": """<p>「呂布在哪裡／在這裡」——<b>這兩句照原文唸</b>，不要改寫。孩子會起雞皮疙瘩。</p>
 <p>車壞馬驚那幾個細節，古人記下來當作「老天在警告他」。可以順便講古人怎麼看預兆。</p>"""},

{"html": """<div class="eyebrow">十四 · 那盞燈</div>
 <h2>百姓在他身上點燈</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>董卓的屍體被丟在街上</li>
     <li>他很胖，看守的人<b>在他肚臍上插了一根燈芯</b></li>
     <li>史書說那盞燈<b>燒了好幾天</b></li>
   </ul>
   <div class="callout">長安城裡的人把衣服首飾賣了換酒，<br><b>在街上慶祝了好幾天。</b></div>
 </div>
 <div class="cast tight">${im("fire","燒了好幾天")}${im("bowl","街上在慶祝")}</div></div>""",
 "note": """<p>🚩 這一段很殘忍，但<b>史書真的這樣寫</b>。可以講，但不要停太久，重點放在「百姓有多恨他」。</p>
 <p class="ask">問：「一個人要做到什麼程度，別人才會這樣高興？」</p>"""},

{"html": """<div class="eyebrow">十五 · 一個嘆息</div>
 <h2>有人只是嘆了一口氣</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>有位很有學問的老先生叫<b>蔡邕</b>，董卓生前很看重他</li>
     <li>聽到死訊，他<b>嘆了一口氣</b></li>
     <li>王允聽說了，把他抓起來</li>
   </ul>
   <div class="callout">很多人求情，王允不肯。<br>蔡邕死在牢裡——<b>他正在寫的漢朝歷史，也沒寫完。</b></div>
 </div>
 <div class="cast tight">${cf(chr({robe:"#8A7B52",hat:"ru",beard:"long",prop:"scroll"}),"蔡邕","只嘆了一口氣")}${im("books","沒寫完的書")}</div></div>""",
 "note": """<p><b>這一頁是這一回的良心。</b>剛剛還是英雄的王允，這一頁做了一件很小氣的事。</p>
 <p class="ask">問：「王允是好人嗎？」——和第五回問曹操那一題是同一種。不要給答案。</p>"""},

{"html": """<div class="eyebrow">十六 · 兩個月後</div>
 <h2>殺回來的那兩個人</h2>
 <div class="art wide"><div class="txt">
   <ul class="pts">
     <li>董卓的舊部下<b>李傕、郭汜</b>本來要解散逃走</li>
     <li>有人跟他們說：<b>散了會被一個個抓走，不如打回去</b></li>
     <li>他們真的打回長安——王允被殺，呂布逃走</li>
   </ul>
   <div class="callout">董卓死了兩個月，<br><b>長安又回到原來的樣子。</b></div>
 </div>
 ${mp("sackchangan","李傕郭汜犯長安","清代版畫")}</div>""",
 "note": """<p>這一頁把前面的快樂整個推翻。<b>殺掉一個壞人，不等於事情變好。</b></p>
 <p>這條線第八回會收——皇帝就是從這一團混亂裡逃出來的。</p>"""},

{"html": """<div class="eyebrow">十七 · 他又跑了</div>
 <h2>呂布這一生都在逃</h2>
 <div class="tl">
   <div><span class="yr">189</span><span>殺義父丁原，投靠董卓</span><span class="ago">第五回</span></div>
   <div><span class="yr">192</span><span>殺義父董卓，當上大官</span><span class="ago">這一回</span></div>
   <div><span class="yr">192</span><span>長安失守，帶著幾百人逃走</span><span class="ago">兩個月後</span></div>
   <div class="now"><span class="yr">198</span><span>白門樓</span><span class="ago">第七回</span></div>
 </div>
 <div class="callout">他每一次都贏了眼前那一場，<br><b>每一次都失去下一個地方。</b></div>""",
 "note": """<p>四行指過去。孩子會自己看出規律——<b>不用你講。</b></p>
 <p>第七回預告：他會遇到一個<b>不肯逃的人</b>（陳宮）。</p>"""},

{"html": """<div class="eyebrow">十八 · 這一回的話</div>
 <h2>不用打，讓對方自己裂開</h2>
 <div class="cols">
   <div class="card">${ic("sword")}<h3>第五回</h3><p>十幾萬人，打了一年<br><b>什麼都沒做成</b></p></div>
   <div class="card">${ic("lantern")}<h3>第六回</h3><p>三個人，一桌酒<br><b>做成了</b></p></div>
 </div>
 <div class="callout">差別不在<b>力氣</b>，在<b>有沒有找到那條裂縫</b>。</div>
 <p class="foot">可是王允也證明了另一件事：<b>會拆東西的人，不一定會蓋東西。</b>他只撐了兩個月。</p>""",
 "note": """<p>回到開場那個「好朋友怎麼會吵架」的問題，讓孩子自己說。</p>
 <p>最後那句「會拆不一定會蓋」是<b>整回的重點</b>，講完再翻下一頁。</p>"""},

{"html": """<div class="eyebrow">最後</div>
 <h2>今天哪些是編的</h2>
 <div class="cols">
   <div class="card"><h3>編的</h3><p>
     <b>貂蟬</b>：小說創造的人物。史書只寫「董卓有個侍女，呂布和她有來往」，<b>連名字都沒有</b><br><br>
     <b>連環計</b>：王允確實去說服呂布，但沒有這一套設計<br><br>
     <b>鳳儀亭擲戟</b>：董卓確實丟過戟，但是因為呂布辦事不力</p></div>
   <div class="card"><h3>真的</h3><p>
     <b>郿塢存糧三十年</b>：真的<br><br>
     <b>王允說「將軍姓呂，太師姓董」</b>：史書有記<br><br>
     <b>肚臍點燈</b>：真的<br><br>
     <b>蔡邕因為嘆氣而死</b>：真的<br><br>
     <b>李傕郭汜反攻、王允被殺</b>：真的</p></div>
 </div>
 <div class="callout">小說為什麼要加一個貂蟬？<br>因為史書那一句<b>太短了</b>——<br>它想讓這件事<b>有人在做選擇</b>，不是剛好發生。</div>""",
 "note": """<p>固定收尾頁。先問孩子記得哪一段最清楚，再揭曉。</p>
 <p>「小說想讓你喜歡誰」「小說想讓誰有選擇」——這兩句整套課會一直用。</p>"""},
]
