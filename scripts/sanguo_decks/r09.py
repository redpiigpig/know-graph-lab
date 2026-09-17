# -*- coding: utf-8 -*-
"""第九回　以少打多（200）

官渡。第四回埋的「太有把握的人最好騙」這條線，在這裡第一次收。
"""

TITLE = "三國第九回"
MARK = "三國演義 · 第九回"
SUB = "官渡之戰"

SLIDES = [
{"cover": True,
 "html": """<div class="art">
   <div class="txt">
     <div class="eyebrow">第九回</div>
     <h1>兩萬人打<em>十萬人</em></h1>
     <p class="sub">兵少的那一邊贏了。<br>不是因為比較勇敢，是因為對方太有把握。</p>
     <div class="meta">
       <div><dt>時間</dt><dd>西元 200 年，官渡</dd></div>
       <div><dt>這一回</dt><dd>官渡之戰</dd></div>
       <div><dt>今天要弄懂</dt><dd>為什麼強的那邊會輸</dd></div>
     </div>
     <p class="credit">版畫與繡像取自維基共享資源，出處見上方「圖片來源」</p>
   </div>
   <div class="cast">
     ${cf(chr({robe:"#7A6A4F",hat:"jin",beard:"mo",prop:"jian"}),"袁紹","十萬兵")}
     ${cf(chr({robe:"#2E4A63",hat:"ze",beard:"mo",prop:"dao"}),"曹操","兩萬兵")}
   </div>
 </div>""",
 "note": """<p>這一回是<b>整套課第一場大戰</b>。前八回都在鋪路，從這裡開始每一回都有一場決定命運的仗。</p>
 <p class="ask">開場問：「打球的時候，人多的那隊一定贏嗎？」最後一頁回來對。</p>"""},

{"html": """<div class="eyebrow">一 · 攤開來看</div>
 <h2>兩邊有什麼</h2>
 <div class="cols">
   <div class="card">${chr({robe:"#7A6A4F",hat:"jin",beard:"mo"})}<h3>袁紹</h3><p><b>十萬兵</b>・河北四州<br>糧食夠吃好幾年<br>家裡四代出大官</p></div>
   <div class="card">${chr({robe:"#2E4A63",hat:"ze",beard:"mo"})}<h3>曹操</h3><p><b>兩萬兵</b>・中原殘破<br>糧食只夠幾個月<br>手上有<b>一個皇帝</b></p></div>
 </div>
 <div class="callout">兵差<b>五倍</b>，糧差更多。<br>幾乎所有人都覺得曹操<b>撐不過三個月</b>。</div>""",
 "note": """<p>兩張卡對照，數字要唸出來。<b>讓孩子先站在「袁紹一定贏」那一邊</b>，後面才有落差。</p>"""},

{"html": """<div class="eyebrow">二 · 地圖</div>
 <h2>一條河，一個渡口</h2>
 <div class="art wide"><div class="txt">
   <ul class="pts">
     <li>袁紹在<b>黃河北邊</b>，曹操在南邊</li>
     <li>中間只有幾個地方可以過河</li>
     <li>曹操把主力放在<b>官渡</b>——擋住通往許都的路</li>
   </ul>
   <div class="callout">守在這裡，等於用<b>一個點</b>擋住<b>一整片</b>。</div>
 </div>
 ${mp("map_guandu","官渡之戰形勢","上面是袁紹，下面是曹操")}</div>""",
 "note": """<p>指地圖：<b>曹操沒有守整條河，只守一個點。</b>兵少的人不能到處守。</p>
 <p class="ask">問：「為什麼不守整條河？」（兵不夠，守到處等於到處都守不住）</p>"""},

{"html": """<div class="eyebrow">三 · 他在曹操這邊</div>
 <h2>關羽怎麼會替曹操打仗</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>第八回劉備逃走後被曹操打散，<b>三兄弟走散了</b></li>
     <li>關羽保護著劉備的家人，被圍在土山上</li>
     <li>他答應投降，但講了三個條件——其中一個是：<b>一知道大哥在哪裡，馬上就走</b></li>
   </ul>
   <div class="callout">曹操答應了。<br>他把關羽當貴賓，<b>送金子、送美女、送赤兔馬</b>。</div>
 </div>
 <div class="cast tight">${ph("guanyustatue","關羽","大相國寺塑像")}</div></div>""",
 "note": """<p>「土山約三事」是小說寫的，史書只說關羽被擒後投降。<b>但「他一直想走」是真的。</b></p>
 <p class="ask">問：「投降了還可以講條件嗎？」</p>"""},

{"html": """<div class="eyebrow">四 · 白馬</div>
 <h2>那一刀</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>袁紹的大將<b>顏良</b>圍住白馬，曹操的人打不過</li>
     <li>關羽遠遠看見顏良的傘蓋，<b>直接騎馬衝進去</b></li>
     <li>在萬人之中<b>把顏良斬了</b>，割下頭顱回來</li>
   </ul>
   <div class="callout">史書上寫著這一段——<br><b>這是真的。</b></div>
   <p class="foot">袁紹另一員大將文醜，也在接下來的仗裡死了。</p>
 </div>
 <div class="cast tight">${ph("yanliang","顏良","被關羽斬了")}${ph("wenchou","文醜","接著也死了")}</div></div>""",
 "note": """<p>這一段<b>是真的</b>，而且是三國正史裡<b>唯一一次明確記載的「萬軍中斬將」</b>。可以強調。</p>
 <p>第五回的「溫酒斬華雄」是假的，這一次是真的。<b>對照著講。</b></p>"""},

{"html": """<div class="eyebrow">五 · 他走了</div>
 <h2>金子全部留下，人走了</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>關羽打聽到劉備在袁紹那邊</li>
     <li>他把曹操送的東西<b>一件一件包好</b>，封存在庫房</li>
     <li>留下一封信，帶著劉備的家人走了</li>
   </ul>
   <div class="callout">曹操的手下要去追。<br>曹操說：<b>「各為其主，讓他走。」</b></div>
   <p class="foot">小說裡的「過五關斬六將」是編的——那條路線在地圖上走不通。</p>
 </div>
 <div class="cast tight">${ph("chunqiulou","許昌春秋樓","傳說關羽在這裡夜讀")}</div></div>""",
 "note": """<p>「東西一件一件包好」是史書寫的，<b>這個細節比打仗更能說明關羽是什麼人</b>。</p>
 <p>春秋樓那張照片可以講：<b>一千八百年後還有人替他蓋樓。</b>（第十三回會接）</p>"""},

{"html": """<div class="eyebrow">六 · 對峙</div>
 <h2>撐了半年</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>袁紹堆土山、射箭雨；曹操造<b>投石車</b>反擊</li>
     <li>袁紹挖地道；曹操在營前<b>挖一條長溝</b></li>
     <li>兩邊你來我往，<b>誰也過不去</b></li>
   </ul>
   <div class="callout">可是時間拖得愈久，<br><b>對糧少的那一邊愈不利。</b></div>
 </div>
 <div class="cast tight">${ph("crossbow","弩機","東漢青銅弩機，出土文物")}${im("shield","守了半年")}</div></div>""",
 "note": """<p>弩機那張可以講：<b>扣下去箭就射出去，不用很大力氣</b>——漢朝軍隊靠它打贏很多仗。</p>"""},

{"html": """<div class="eyebrow">七 · 想放棄</div>
 <h2>曹操寫信說：我撐不下去了</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>糧只剩一個月，士兵開始逃跑</li>
     <li>曹操寫信回許都給荀彧，說想撤退</li>
     <li>荀彧回信：<b>現在誰先退，誰就輸了</b></li>
   </ul>
   <div class="callout">信上寫：<b>「這是關鍵時刻，一定會有變化。」</b><br>曹操咬牙撐住。</div>
 </div>
 <div class="cast tight">${ph("ehon_006_001","江戶時代畫的三國","《繪本通俗三國志》插圖")}</div></div>""",
 "note": """<p><b>這一頁很重要</b>：主角也會想放棄。孩子通常以為厲害的人不會軟弱。</p>
 <p>荀彧第八回出現過，<b>這一封信救了曹操</b>。他的結局在第十四回。</p>"""},

{"html": """<div class="eyebrow">八 · 沒有人聽的建議</div>
 <h2>袁紹那邊，有人一直在說對的話</h2>
 <div class="cols">
   <div class="card">${pc("tianfeng")}<h3>田豐</h3><p>勸袁紹<b>不要急著決戰</b>，慢慢拖就會贏。袁紹嫌他掃興，<b>把他關起來</b>。</p></div>
   <div class="card">${chr({robe:"#8A7B52",hat:"ru",beard:"long",prop:"scroll"})}<h3>許攸</h3><p>發現曹操糧盡，建議<b>分兵直接偷襲許都</b>。袁紹說：我要正面打贏他。</p></div>
 </div>
 <div class="callout">兩個好建議，<b>兩次都沒有被採用</b>。<br>（第八回沮授勸他去接皇帝——也沒有被採用。）</div>""",
 "note": """<p>回頭指第八回的沮授。<b>袁紹身邊不缺聰明人，缺的是會聽的人。</b></p>
 <p class="ask">問：「為什麼他都不聽？」（因為他覺得自己一定會贏）</p>"""},

{"html": """<div class="eyebrow">九 · 半夜來的人</div>
 <h2>許攸投奔過來了</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>許攸家人犯事被抓，他一氣之下<b>跑到曹操那邊</b></li>
     <li>曹操正在睡覺，聽到消息<b>光著腳跑出來迎接</b></li>
     <li>許攸問他：<b>「你的糧還剩幾天？」</b></li>
   </ul>
   <div class="callout">曹操說一年。許攸說：不對。<br>曹操說半年。許攸站起來要走。<br>曹操才說：<b>「只剩一個月。」</b></div>
 </div>
 <div class="cast tight">${im("hourglass","只剩一個月")}${im("lantern","半夜")}</div></div>""",
 "note": """<p>「光著腳跑出來」是史書寫的，<b>這個細節要講</b>——曹操知道這個人有多重要。</p>
 <p>三問三答那段節奏很好，可以跟孩子一來一往演。</p>"""},

{"html": """<div class="eyebrow">十 · 烏巢</div>
 <h2>五千人，去燒對方的糧</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>許攸說：袁紹的糧全部堆在<b>烏巢</b>，守備很鬆</li>
     <li>曹操親自帶<b>五千人</b>，打著袁紹軍的旗號連夜出發</li>
     <li>路上有人盤問，他們就說：<b>袁將軍怕曹操偷襲，派我們去加強守備</b></li>
   </ul>
   <div class="callout">天亮的時候，<br><b>烏巢的糧全部燒起來了。</b></div>
 </div>
 <div class="cast tight">${ph("ehon_006_003","江戶時代畫的三國","《繪本通俗三國志》插圖")}${im("fire","燒了")}</div></div>""",
 "note": """<p>「打著對方旗號」孩子很愛，講得像特務行動。</p>
 <p class="ask">問：「五千人去打十萬人的糧倉，怕不怕？」（曹操自己去了——這就是差別）</p>"""},

{"html": """<div class="eyebrow">十一 · 最後一個決定</div>
 <h2>袁紹選錯了</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>烏巢起火的消息傳來，有人說：<b>快去救糧</b></li>
     <li>另一個人說：不如趁曹操不在，<b>直接打他的大營</b></li>
     <li>袁紹兩邊都做——<b>救糧派少數，打營派主力</b></li>
   </ul>
   <div class="callout">結果：大營<b>沒打下來</b>，<br>烏巢的糧<b>全燒光了</b>。</div>
 </div>
 <div class="cast tight">${ph("zhanghe","張郃","主張去救糧的人，後來投降曹操")}</div></div>""",
 "note": """<p><b>整回的勝負在這一頁。</b>不是他選了錯的那一邊，是他<b>兩邊都要，結果兩邊都不夠力</b>。</p>
 <p>張郃這個人記住——<b>第十八回街亭斷馬謖水源的就是他。</b></p>"""},

{"html": """<div class="eyebrow">十二 · 崩</div>
 <h2>一夜之間，十萬人散了</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>糧沒了，張郃投降，消息傳開</li>
     <li>袁紹的大軍<b>不是被打敗，是自己散掉的</b></li>
     <li>袁紹帶著八百騎兵渡河逃走</li>
   </ul>
   <div class="callout">來的時候十萬人，<br><b>回去的時候八百人。</b></div>
 </div>
 <div class="cast tight">${ph("xuchu","許褚","曹操的貼身護衛")}${im("horse","八百騎")}</div></div>""",
 "note": """<p>「十萬 → 八百」這個對比要唸出來。</p>
 <p>第五回的聯軍也是這樣散的——<b>糧一沒，人就走。</b>回頭指。</p>"""},

{"html": """<div class="eyebrow">十三 · 那一把火</div>
 <h2>曹操燒掉一箱信</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>打掃戰場時，搜出<b>一大箱信</b></li>
     <li>全是自己人偷偷寫給袁紹的——內容是「我願意投降」</li>
     <li>有人說：一封一封查出來，全部處理掉</li>
   </ul>
   <div class="callout">曹操說：<b>「當時連我自己都不確定能贏，何況別人。」</b><br>當場<b>一把火燒掉，一封都沒看。</b></div>
 </div>
 <div class="cast tight">${im("envelope","一整箱信")}${im("fire","全燒了")}</div></div>""",
 "note": """<p><b>全回最重要的一頁。</b>孩子最記得的通常是這一段，不是打仗。</p>
 <p class="ask">問：「如果是你，你會不會想看？」——大部分人會想看。這就是差別。</p>"""},

{"html": """<div class="eyebrow">十四 · 被關起來的那個人</div>
 <h2>田豐猜到自己會死</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>牢裡有人恭喜田豐：主公打敗了，<b>證明你是對的，他一定會重用你</b></li>
     <li>田豐說：不會。<b>他贏了會放我，輸了會殺我。</b></li>
     <li>袁紹回來後，第一件事就是<b>把他殺了</b></li>
   </ul>
   <div class="callout">因為看見自己輸的人還活著，<br><b>太難堪了。</b></div>
 </div>
 <div class="cast tight">${cf(chr({robe:"#4F7460",hat:"ru",beard:"long",sad:1}),"田豐","他猜對了")}</div></div>""",
 "note": """<p>這一頁講<b>「輸不起的人」</b>。和第八回袁紹不聽沮授、這一回不聽許攸，是同一個人。</p>
 <p>袁紹兩年後就吐血死了，兒子們自己打起來——<b>河北四州最後全歸曹操。</b></p>"""},

{"html": """<div class="eyebrow">十五 · 這條線</div>
 <h2>太有把握的人最好騙</h2>
 <div class="tier">
   <div><span class="lbl">第四回</span><span>何進太有把握，一個人走進宮裡——被殺</span></div>
   <div><span class="lbl">第七回</span><span>袁術太有把握，拿到玉璽就稱帝——沒人理</span></div>
   <div><span class="lbl">這一回</span><span>袁紹太有把握，好建議一個都不聽——輸掉全部</span></div>
 </div>
 <div class="callout">第四回埋的那條線，<b>在這裡第一次收</b>。<br>第十回會再收一次——<b>那次輪到曹操自己。</b></div>""",
 "note": """<p>三行指過去。<b>這是整套課的主旋律之一</b>，第十回赤壁還會再用。</p>
 <p>預告下一回：<b>這一回贏的那個人，下一回會用一模一樣的方式輸。</b></p>"""},

{"html": """<div class="eyebrow">十五之二 · 同一年，南方</div>
 <h2>江東換了老闆</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>就在官渡打得最緊的時候，<b>孫策在打獵時被刺客射傷</b></li>
     <li>他本來想趁曹操分身乏術偷襲許都，<b>來不及了</b></li>
     <li>臨死前把位子交給弟弟<b>孫權</b>——那年孫權<b>十八歲</b></li>
   </ul>
   <div class="callout">孫策說：<b>「打天下你不如我，<br>守住這裡、用對人，我不如你。」</b></div>
 </div>
 <div class="cast tight">${ph("yuji","于吉","傳說孫策殺了他，之後就出事了")}</div></div>""",
 "note": """<p>這一頁是<b>第十回的鋪陳</b>：赤壁時孫權二十七歲，就是從這裡接手的。</p>
 <p>于吉是個道士，小說說孫策殺他之後被鬼纏身而死——<b>那是小說</b>，史實是箭傷感染。</p>
 <p class="ask">問：「哥哥為什麼說弟弟比自己強？」（因為打天下和守天下要的能力不一樣）</p>"""},

{"html": """<div class="eyebrow">十六 · 北方統一</div>
 <h2>七年後，他把整個北方拿下來了</h2>
 <div class="tl">
   <div><span class="yr">200</span><span>官渡大勝</span><span class="ago">這一回</span></div>
   <div><span class="yr">202</span><span>袁紹病死，兒子們互相打</span><span class="ago"></span></div>
   <div><span class="yr">207</span><span>遠征烏桓，掃平最後的殘部</span><span class="ago"></span></div>
   <div class="now"><span class="yr">208</span><span>當上丞相，帶兵南下</span><span class="ago">第十回</span></div>
 </div>
 <div class="callout">四十七歲的曹操，<br><b>已經沒有對手了。</b></div>""",
 "note": """<p>四行走完八年。最後一句要講重——<b>「沒有對手」正是下一回他輸掉的原因。</b></p>"""},

{"html": """<div class="eyebrow">十七 · 這一回的話</div>
 <h2>贏的不是兵多的那邊</h2>
 <div class="cols">
   <div class="card">${ic("shield")}<h3>袁紹輸在哪</h3><p>不是兵不夠<br>是<b>有人說對的話，他不聽</b></p></div>
   <div class="card">${ic("scroll")}<h3>曹操贏在哪</h3><p>不是比較聰明<br>是<b>想放棄的時候有人拉住他</b></p></div>
 </div>
 <div class="callout">兩個人身邊<b>都有聰明人</b>。<br>差別只在：<b>一個聽，一個不聽。</b></div>""",
 "note": """<p>回到開場「人多的隊一定贏嗎」，讓孩子自己說。</p>"""},

{"html": """<div class="eyebrow">最後</div>
 <h2>今天哪些是編的</h2>
 <div class="cols">
   <div class="card"><h3>編的</h3><p>
     <b>土山約三事</b>：史書只說關羽被擒後降曹<br><br>
     <b>過五關斬六將</b>：完全沒有，路線在地圖上走不通<br><br>
     <b>曹操贈赤兔馬</b>：赤兔是呂布的馬，呂布死後下落不明</p></div>
   <div class="card"><h3>真的</h3><p>
     <b>關羽萬軍中斬顏良</b>：真的，正史明確記載<br><br>
     <b>封金掛印而去</b>：真的<br><br>
     <b>曹操想撤退、荀彧寫信</b>：真的<br><br>
     <b>許攸來降、火燒烏巢</b>：真的<br><br>
     <b>燒掉那箱通敵的信</b>：真的<br><br>
     <b>田豐猜到自己會死</b>：真的</p></div>
 </div>
 <div class="callout">這一回<b>真的比編的精彩</b>。<br>小說加的那些，反而<b>沒有史書好看</b>。</div>""",
 "note": """<p>固定收尾頁。這一回可以問：<b>你比較喜歡哪一個版本？</b></p>"""},
]
