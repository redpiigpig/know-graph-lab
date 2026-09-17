# -*- coding: utf-8 -*-
"""第十回　火燒赤壁（207–208）

全套課內容最多的一回：三顧茅廬＋隆中對＋長坂坡＋孫劉聯盟＋赤壁。
壓在 20 頁裡，靠的是把「軍事細節」讓給「人的選擇」。
第九回贏的人，這一回用一模一樣的方式輸。
"""

TITLE = "三國第十回"
MARK = "三國演義 · 第十回"
SUB = "火燒赤壁"

SLIDES = [
{"cover": True,
 "html": """<div class="art">
   <div class="txt">
     <div class="eyebrow">第十回</div>
     <h1>火燒<em>赤壁</em></h1>
     <p class="sub">上一回他靠著燒糧贏了十萬人。<br>這一回，換別人燒他。</p>
     <div class="meta">
       <div><dt>時間</dt><dd>西元 207–208 年</dd></div>
       <div><dt>這一回</dt><dd>三顧茅廬到赤壁之戰</dd></div>
       <div><dt>今天要弄懂</dt><dd>為什麼三個國家會出現</dd></div>
     </div>
     <p class="credit">浮世繪與繡像取自維基共享資源，出處見上方「圖片來源」</p>
   </div>
   <div class="cast">
     ${cf(chr({robe:"#EFE6D4",hat:"ru",beard:"mo",prop:"fu"}),"諸葛亮","二十七歲")}
     ${im("wave","長江")}
   </div>
 </div>""",
 "note": """<p>這一回<b>內容最多</b>，如果時間不夠可以分兩堂：前十頁講三顧茅廬到長坂坡，後十頁講赤壁。</p>
 <p class="ask">開場問：「兩個人都打不過第三個人，那要怎麼辦？」最後一頁回來對。</p>"""},

{"html": """<div class="eyebrow">一 · 他四十六歲了</div>
 <h2>劉備還是沒有地盤</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>官渡之後他投靠荊州的<b>劉表</b>，住在小城新野</li>
     <li>有一天上廁所，發現<b>大腿上長肉了</b>——因為太久沒騎馬</li>
     <li>他當場哭了出來</li>
   </ul>
   <div class="callout">他說：<b>「日子一天天過去，我卻什麼都還沒做成。」</b></div>
   <p class="foot">這一段史書有記，叫「髀肉復生」。</p>
 </div>
 <div class="cast tight">${ph("liubei3","劉備","歷代名臣像冊")}</div></div>""",
 "note": """<p>「大腿長肉所以哭了」孩子會覺得很奇怪，<b>正好可以講「一個人怎麼知道自己在浪費時間」</b>。</p>
 <p>算一下：第三回二十三歲，現在四十六歲。<b>整整一半的人生過去了。</b></p>"""},

{"html": """<div class="eyebrow">二 · 有人告訴他</div>
 <h2>你身邊缺一個人</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>一位隱居的長輩<b>司馬徽</b>（外號水鏡先生）告訴他：你打了半輩子仗，<b>身邊都是武將，沒有一個能想事情的人</b></li>
     <li>後來又有個叫<b>徐庶</b>的人來幫他，一來就打了勝仗</li>
     <li>可是曹操把徐庶的母親抓走，徐庶只好走</li>
   </ul>
   <div class="callout">臨走前徐庶回頭說：<br><b>「有一個人比我強十倍，他就住在這附近。」</b></div>
 </div>
 <div class="cast tight">${ph("simahui","司馬徽","水鏡先生")}${ph("xushu","徐庶","走之前推薦了一個人")}</div></div>""",
 "note": """<p>這一頁是<b>鋪梗</b>。「比我強十倍」要唸出來，孩子會期待。</p>
 <p class="ask">問：「為什麼劉備打了二十年都贏不了？」（因為只有力氣沒有計畫）</p>"""},

{"html": """<div class="eyebrow">三 · 第一次</div>
 <h2>走了很遠，人不在</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>那個人叫<b>諸葛亮</b>，住在隆中，自己種田</li>
     <li>劉備帶著關羽、張飛親自去請</li>
     <li>到了，小童說：<b>「先生今天早上出門了，不知道去哪、不知道幾時回來。」</b></li>
   </ul>
   <div class="callout">四十六歲的人，<br>去請一個<b>二十六歲、沒有官、沒有名氣</b>的年輕人。</div>
 </div>
 <div class="cast tight">${im("mountain","隆中")}${im("houses","一間草屋")}</div></div>""",
 "note": """<p>年齡差要強調：<b>劉備大他二十歲</b>，而且是有名的將軍。</p>
 <p class="ask">問：「你會為了一個沒聽過的人跑三趟嗎？」</p>"""},

{"html": """<div class="eyebrow">四 · 第二次</div>
 <h2>下著大雪，還是不在</h2>
 <div class="art wide"><div class="txt">
   <ul class="pts">
     <li>過了一陣子，天下大雪，劉備又去</li>
     <li>張飛在後面抱怨：<b>「這種天氣不如回家！」</b></li>
     <li>到了還是不在，只留下一封信就回去了</li>
   </ul>
   <div class="callout">關羽和張飛都不高興。<br>劉備說：<b>「我們是去求人，不是去叫人。」</b></div>
 </div>
 ${mp("threevisits2","玄德雪中訪孔明","月岡芳年浮世繪")}</div>""",
 "note": """<p>浮世繪那張要指給孩子看：<b>後面那個生氣的就是張飛。</b>日本人畫的三國，看起來很不一樣。</p>"""},

{"html": """<div class="eyebrow">五 · 第三次</div>
 <h2>他在睡午覺</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>第三次去，人在，可是<b>正在睡覺</b></li>
     <li>劉備叫大家不要吵，<b>站在台階下等</b></li>
     <li>等了很久，諸葛亮才醒過來</li>
   </ul>
   <div class="callout">張飛氣到說要放火燒屋子。<br>關羽把他拉住。</div>
   <p class="foot">這一年，劉備四十七歲，諸葛亮二十七歲。</p>
 </div>
 <div class="cast tight">${ph("zhugeliang","諸葛亮","明《三才圖會》刻本")}</div></div>""",
 "note": """<p>「站在台階下等一個在睡覺的年輕人」——<b>這一幕就是劉備這個人</b>。</p>
 <p>「三顧茅廬」史書只有四個字：<b>「凡三往，乃見。」</b>細節都是小說寫的，但事情是真的。</p>"""},

{"html": """<div class="eyebrow">六 · 那張地圖</div>
 <h2>隆中對：一個二十七歲的人的計畫</h2>
 <div class="tier">
   <div><span class="lbl">北邊</span><span>曹操已經太強，<b>現在不能碰</b></span></div>
   <div><span class="lbl">東邊</span><span>孫權有長江、有人心，<b>要當朋友不要當敵人</b></span></div>
   <div><span class="lbl">中間</span><span><b>先拿荊州</b>——劉表守不住</span></div>
   <div><span class="lbl">西邊</span><span><b>再拿益州</b>——四面是山，好守</span></div>
 </div>
 <div class="callout">拿到兩塊地以後等機會，<br><b>兩路同時北伐。</b></div>
 <p class="foot">劉備聽完說：「我遇到孔明，就像魚遇到水。」</p>""",
 "note": """<p><b>整套課最重要的一頁之一。</b>四行一行一行指過去——<b>後面十回都在走這張圖。</b></p>
 <p>第十一回拿荊州、第十二回拿益州、第十七回北伐，都是這裡說好的。</p>
 <p class="ask">問：「一個在家種田的人，怎麼知道天下的事？」（因為他一直在讀書、一直在想）</p>"""},

{"html": """<div class="eyebrow">七 · 計畫趕不上變化</div>
 <h2>劉表死了，兒子投降了</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>諸葛亮才剛來幾個月，曹操就<b>帶著大軍南下</b></li>
     <li>劉表剛好病死，繼位的小兒子劉琮<b>直接投降</b></li>
     <li>而且<b>沒有人告訴劉備</b>——他是最後才知道的</li>
   </ul>
   <div class="callout">說好要拿的荊州，<br><b>一天之內變成曹操的。</b></div>
 </div>
 <div class="cast tight">${ph("ehon_007_002","江戶時代畫的三國","《繪本通俗三國志》插圖")}</div></div>""",
 "note": """<p>第七回埋的「劉表只想守住現在的日子」，<b>在這裡收</b>。回頭指一下。</p>"""},

{"html": """<div class="eyebrow">八 · 十萬個人跟著走</div>
 <h2>一天走十里</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>劉備往南逃，沿路的百姓<b>自己跟上來</b>，愈跟愈多</li>
     <li>最後變成<b>十幾萬人</b>，一天只能走十幾里</li>
     <li>有人勸他：丟下百姓，快走</li>
   </ul>
   <div class="callout">劉備說：<b>「做大事要以人為本。<br>現在這些人跟著我，我怎麼能丟下他們？」</b></div>
   <p class="foot">這一段史書有記。曹操的騎兵一天一夜追了三百里。</p>
 </div>
 <div class="cast tight">${im("houses","十幾萬人")}${im("baby","連小孩都跟著")}</div></div>""",
 "note": """<p>這是<b>劉備和曹操最大的差別</b>：第七回曹操為報父仇打徐州傷及百姓，這裡劉備寧可被追上也不丟下百姓。</p>
 <p class="ask">問：「帶著十萬人跑得動嗎？」（跑不動——他知道，還是帶著）</p>"""},

{"html": """<div class="eyebrow">九 · 長坂坡</div>
 <h2>兩個人擋住一支大軍</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>曹操的騎兵追上來，劉備的隊伍<b>被沖散</b>，妻兒失散</li>
     <li><b>趙雲</b>單騎殺回去，把劉備的兒子阿斗抱了出來</li>
     <li><b>張飛</b>帶二十騎守在橋上，大吼一聲——追兵<b>沒有一個人敢過去</b></li>
   </ul>
   <div class="callout">劉備接過阿斗，<b>往地上一丟</b>：<br>「為了你這小子，差點害我損失一員大將！」</div>
 </div>
 <div class="cast tight">${ph("zhaoyun","趙雲","清代繡像")}</div></div>""",
 "note": """<p>「七進七出」是小說誇大，史書寫的是<b>趙雲護著甘夫人和阿斗突圍</b>——一樣厲害。</p>
 <p>張飛據橋是<b>真的</b>，史書有記。</p>
 <p class="ask">問：「劉備為什麼要摔兒子？」（讓趙雲知道自己被看重——也可能是真的氣）</p>"""},

{"html": """<div class="eyebrow">十 · 過江</div>
 <h2>諸葛亮說：我去找孫權</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>劉備已經沒有兵、沒有地盤，<b>只剩一萬多人</b></li>
     <li>曹操號稱<b>八十萬大軍</b>（實際約二十萬）順江而下</li>
     <li>諸葛亮說：<b>只剩一條路——去跟孫權結盟</b></li>
   </ul>
   <div class="callout">這就是隆中對說的：<br><b>孫權可以當朋友，不要當敵人。</b></div>
 </div>
 <div class="cast tight">${ph("lusu","魯肅","主張聯合的人")}${im("wave","過江")}</div></div>""",
 "note": """<p>魯肅很重要：<b>他是東吳那邊第一個主張聯合劉備的人</b>，第十一回會再出現。</p>"""},

{"html": """<div class="eyebrow">十一 · 東吳在吵架</div>
 <h2>投降還是打</h2>
 <div class="cols">
   <div class="card">${pc("sunquan")}<h3>孫權　二十七歲</h3><p>哥哥孫策留下的江東六郡。<b>他還沒決定。</b></p></div>
   <div class="card">${pc("zhouyu")}<h3>周瑜　三十四歲</h3><p>大都督。他說：<b>曹操號稱八十萬，其實沒那麼多，而且北方人不會水戰。</b></p></div>
 </div>
 <div class="callout">文官大多主張投降——<b>投降了他們還是官</b>。<br>可是孫權投降了，<b>就什麼都不是了</b>。</div>""",
 "note": """<p>這一頁講<b>「立場不同，建議就不同」</b>：文官投降沒損失，老闆投降就沒了。</p>
 <p class="ask">問：「為什麼大家勸他投降？」（因為對他們自己最安全）</p>"""},

{"html": """<div class="eyebrow">十二 · 砍桌角</div>
 <h2>孫權做了決定</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>他聽完周瑜的分析，<b>抽出佩刀砍掉桌角</b></li>
     <li>說：<b>「再有人敢說投降，就像這張桌子。」</b></li>
     <li>他派周瑜帶三萬人，和劉備的一萬多人一起上</li>
   </ul>
   <div class="callout">五萬人，<br><b>對上二十萬人。</b></div>
 </div>
 <div class="cast tight">${ph("ehon_007_003","江戶時代畫的三國","《繪本通俗三國志》插圖")}</div></div>""",
 "note": """<p>「砍桌角」是真的，史書有記。<b>二十七歲做這個決定，很不容易。</b></p>
 <p>第九回官渡是二萬對十萬，這裡是五萬對二十萬——<b>又是一次以少打多。</b></p>"""},

{"html": """<div class="eyebrow">十三 · 那些很有名的計謀</div>
 <h2>草船借箭、苦肉計、連環船</h2>
 <div class="cols">
   <div class="card">${ic("bow")}<h3>草船借箭</h3><p>⚠︎ <b>編的。</b>史書裡受箭的是<b>孫權</b>，而且是意外，不是計畫</p></div>
   <div class="card">${pc("huanggai")}<h3>苦肉計</h3><p>黃蓋詐降是<b>真的</b>，但沒有被打一頓那段</p></div>
   <div class="card">${ic("wave")}<h3>連環船</h3><p><b>半真</b>：曹操確實把船連起來，但是為了讓北方兵不暈船</p></div>
 </div>
 <div class="callout">最有名的三個計謀，<br><b>只有一個半是真的。</b></div>""",
 "note": """<p>把三個一起處理，省下三頁。孩子最熟的就是這三個，<b>當場破梗效果很好</b>。</p>
 <p>「借東風」也是編的，下一頁講。</p>"""},

{"html": """<div class="eyebrow">十四 · 東南風</div>
 <h2>冬天怎麼會吹東南風</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>火攻要成功，<b>風必須從東南往西北吹</b>——那是曹操的方向</li>
     <li>可是冬天大多吹西北風</li>
     <li>小說說諸葛亮搭壇作法<b>借來東風</b>⚠︎</li>
   </ul>
   <div class="callout">實際上：長江中游的冬天<b>本來就偶爾會吹東南風</b>。<br>他不是借風，<b>是在等風</b>。</div>
 </div>
 <div class="cast tight">${im("wave","東南風")}${im("hourglass","等了好幾天")}</div></div>""",
 "note": """<p><b>這一頁很重要</b>：把「法術」還原成「知識」。懂得天氣的人，看起來就像會法術。</p>
 <p class="ask">問：「知道什麼時候會下雨，算不算特異功能？」</p>"""},

{"html": """<div class="eyebrow">十五 · 那把火</div>
 <h2>十艘船衝進去</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>黃蓋寫信詐降，說要帶糧船過來投靠</li>
     <li>船上裝的是<b>乾柴、油、硫磺</b></li>
     <li>接近曹軍時<b>同時點火</b>，順著東南風直衝連在一起的船隊</li>
   </ul>
   <div class="callout">江面全部燒起來，<br><b>連岸上的營寨都燒著了。</b></div>
 </div>
 <div class="cast tight">${ph("ehon_008_002","江戶時代畫的三國","《繪本通俗三國志》插圖")}${im("fire","燒了一整夜")}</div></div>""",
 "note": """<p>「船連在一起」＋「風向對了」＋「詐降騙開防線」——<b>三件事缺一不可</b>。</p>
 <p>可以回頭對第九回：<b>烏巢也是燒的。曹操最會用火，這次被火燒。</b></p>"""},

{"html": """<div class="eyebrow">十六 · 退兵</div>
 <h2>他從華容道走了</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>曹操從陸路撤退，遇到<b>大雨、爛泥</b>，士兵倒在路上</li>
     <li>他還笑了三次，說周瑜和諸葛亮不夠聰明</li>
     <li>小說寫關羽在華容道把他放走 ⚠︎——<b>史書沒有這件事</b></li>
   </ul>
   <div class="callout">二十萬人南下，<br><b>回去的時候剩不到一半。</b></div>
 </div>
 <div class="cast tight">${ph("ehon_008_003","江戶時代畫的三國","《繪本通俗三國志》插圖")}</div></div>""",
 "note": """<p>「笑了三次」是小說的設計（笑一次來一支伏兵）。史書只記他說了一句：<b>「是我自己燒船退走的，讓周瑜白得了名聲。」</b>——輸不起。</p>"""},

{"html": """<div class="eyebrow">十七 · 這條線又收了</div>
 <h2>這一次輪到他</h2>
 <div class="tier">
   <div><span class="lbl">第九回</span><span>袁紹太有把握，不聽勸——<b>被燒糧</b></span></div>
   <div><span class="lbl">第十回</span><span>曹操太有把握，不信會有東南風——<b>被燒船</b></span></div>
 </div>
 <div class="callout">第四回埋的那句話，<br><b>兩回之內收了兩次。</b></div>
 <p class="foot">而且贏的方法一模一樣：<b>燒掉對方最重要的東西。</b></p>""",
 "note": """<p>兩行對照。<b>這是整套課最漂亮的一次呼應</b>，一定要講。</p>
 <p class="ask">問：「贏過一次的人，為什麼還會犯一樣的錯？」</p>"""},

{"html": """<div class="eyebrow">十八 · 三個國家的開始</div>
 <h2>沒有人吃掉別人</h2>
 <div class="three">
   <div class="wei">${chr({robe:"#2E4A63",hat:"ze",beard:"mo"})}<div class="n">魏</div><div class="who">曹操</div><div class="where">退回北方</div></div>
   <div class="wu">${chr({robe:"#4F7460",hat:"ze"})}<div class="n">吳</div><div class="who">孫權</div><div class="where">守住長江</div></div>
   <div class="shu">${chr({robe:"#8C2F1E",hat:"ze",beard:"mo"})}<div class="n">蜀</div><div class="where">劉備</div><div class="who">拿到荊州幾個郡</div></div>
 </div>
 <div class="callout">赤壁之後，<b>誰都吃不掉誰</b>——三分天下，從這一把火開始。</div>""",
 "note": """<p>三種顏色第一回地圖用過（魏藍、蜀紅、吳綠），<b>這裡正式成立</b>。</p>
 <p>回到開場那個問題：「兩個人都打不過第三個人怎麼辦？」——<b>聯手。</b></p>"""},

{"html": """<div class="eyebrow">最後</div>
 <h2>今天哪些是編的</h2>
 <div class="cols">
   <div class="card"><h3>編的</h3><p>
     <b>草船借箭</b>：受箭的是孫權，而且是意外<br><br>
     <b>借東風</b>：是等風，不是借風<br><br>
     <b>舌戰群儒</b>：沒有這場辯論<br><br>
     <b>華容道放曹操</b>：完全沒有<br><br>
     <b>趙雲七進七出</b>：誇大了</p></div>
   <div class="card"><h3>真的</h3><p>
     <b>三顧茅廬</b>：真的（史書四個字：凡三往，乃見）<br><br>
     <b>隆中對</b>：真的，原文留下來了<br><br>
     <b>十幾萬百姓跟著劉備逃</b>：真的<br><br>
     <b>張飛據橋</b>：真的<br><br>
     <b>孫權砍桌角</b>：真的<br><br>
     <b>黃蓋詐降、火燒連船</b>：真的</p></div>
 </div>
 <div class="callout">小說為什麼要加這麼多計謀？<br>因為它想讓<b>諸葛亮像神一樣</b>——<br>可是真正的他，厲害在<b>那張二十七歲畫的地圖</b>。</div>""",
 "note": """<p>固定收尾頁。最後那句是<b>整回的總結</b>：真實的諸葛亮不靠法術，靠的是計畫。</p>"""},
]
