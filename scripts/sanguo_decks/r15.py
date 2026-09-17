# -*- coding: utf-8 -*-
"""第十五回　白帝城託孤（221–223）

夷陵之戰與劉備之死。第三回桃園結義那個約定，在這一回走完。
"""

TITLE = "三國第十五回"
MARK = "三國演義 · 第十五回"
SUB = "白帝城託孤"

SLIDES = [
{"cover": True,
 "html": """<div class="art">
   <div class="txt">
     <div class="eyebrow">第十五回</div>
     <h1>那個約定，<em>走完了</em></h1>
     <p class="sub">第三回他們說「不求同年同月同日生」。<br>三十九年後，三個人前後走了。</p>
     <div class="meta">
       <div><dt>時間</dt><dd>西元 221–223 年</dd></div>
       <div><dt>這一回</dt><dd>夷陵之戰與白帝城託孤</dd></div>
       <div><dt>今天要弄懂</dt><dd>生氣的時候可不可以做決定</dd></div>
     </div>
     <p class="credit">版畫與照片取自維基共享資源，出處見上方「圖片來源」</p>
   </div>
   <div class="cast">
     ${cf(chr({robe:"#8C2F1E",hat:"mian",cuff:"#6E2418",beard:"mo",sad:1}),"劉備","六十三歲")}
     ${im("fire","七百里連營")}
   </div>
 </div>""",
 "note": """<p>🚩 這一回三個主角走掉兩個，<b>情緒很重</b>。先說今天會比較難過。</p>
 <p class="ask">開場問：「很生氣的時候做的決定，後來會後悔嗎？」最後一頁回來對。</p>"""},

{"html": """<div class="eyebrow">一 · 出兵前</div>
 <h2>張飛也死了</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>關羽死後，張飛天天喝酒、脾氣更壞</li>
     <li>他命令部下<b>三天之內做好白色的旗幟和盔甲</b>，做不到就處罰</li>
     <li>兩個部下知道做不完，<b>半夜趁他喝醉把他殺了</b>，投奔東吳</li>
   </ul>
   <div class="callout">史書早就寫過他的毛病：<br><b>「對上面很尊敬，對下面很粗暴。」</b></div>
 </div>
 <div class="cast tight">${cf(chr({robe:"#3C3630",hat:"wu",beard:"long",fat:1,sad:1}),"張飛","五十五歲")}</div></div>""",
 "note": """<p>🚩 <b>張飛不是死在戰場上</b>，這一點孩子通常不知道，會很錯愕。</p>
 <p>第十三回講關羽「對敵人勇敢、對自己人不客氣」——<b>張飛是另一個版本的同一個問題。</b></p>"""},

{"html": """<div class="eyebrow">一之二 · 那個沒去救的人</div>
 <h2>劉封被賜死</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>第十三回關羽求救，<b>劉封沒有去</b></li>
     <li>後來上庸失守，他逃回成都</li>
     <li>劉備責備他兩件事：<b>見死不救</b>，還有<b>欺負孟達</b></li>
   </ul>
   <div class="callout">諸葛亮還加了一句：<b>這個人太剛強，以後不好管。</b><br>劉備賜他自盡——<b>然後為他哭了很久。</b></div>
   <p class="foot">劉封是劉備的養子。他自盡前說：「我後悔沒有聽孟達的話。」</p>
 </div>
 <div class="cast tight">${cf(chr({robe:"#8C2F1E",hat:"wu",sad:1,prop:"dao"}),"劉封","劉備的養子")}</div></div>""",
 "note": """<p>接第十三回「沒有人來」那一頁。<b>伏筆在這裡收。</b></p>
 <p class="ask">問：「他該死嗎？」（他的理由當時聽起來很合理——可是結果很嚴重）</p>"""},

{"html": """<div class="eyebrow">二 · 所有人都反對</div>
 <h2>他還是要打</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>劉備決定<b>全力伐吳</b>，替關羽報仇、拿回荊州</li>
     <li>趙雲說：<b>國賊是曹魏，不是孫權。打錯對象了。</b></li>
     <li>大臣秦宓也反對，<b>被關進牢裡</b></li>
   </ul>
   <div class="callout">諸葛亮沒有出聲。<br>後來他說：<b>「如果法正還在，一定攔得住主公。」</b></div>
 </div>
 <div class="cast tight">${im("sword","報仇")}${im("map","拿回荊州")}</div></div>""",
 "note": """<p>「打錯對象」這句要講重——趙雲說得很清楚，<b>但沒有人聽得進去</b>。</p>
 <p class="ask">問：「為什麼諸葛亮不攔他？」（攔不住；而且荊州確實該拿回來）</p>"""},

{"html": """<div class="eyebrow">三 · 兩個理由</div>
 <h2>為關羽，還是為荊州</h2>
 <div class="cols">
   <div class="card">${ic("sword")}<h3>感情</h3><p>三十九年的兄弟被殺，<b>不報仇說不過去</b>——對軍心也是</p></div>
   <div class="card">${ic("map")}<h3>算盤</h3><p>沒有荊州，<b>隆中對的「兩路北伐」就永遠做不到</b></p></div>
 </div>
 <div class="callout">兩個理由<b>都成立</b>。<br>可是加起來，就變成一個<b>停不下來</b>的決定。</div>""",
 "note": """<p>這一頁避免把劉備寫成只會衝動的人。<b>他有理性的理由，只是被情緒放大了。</b></p>"""},

{"html": """<div class="eyebrow">四 · 出兵</div>
 <h2>四萬多人，順江而下</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>221 年七月出兵，一路打得很順</li>
     <li>東吳求和，劉備<b>不答應</b></li>
     <li>孫權只好<b>向曹丕稱臣</b>（第十四回講過），再派人抵擋</li>
   </ul>
   <div class="callout">派去擋的人，<br>就是第十三回寫那封客氣信的<b>陸遜</b>。</div>
 </div>
 <div class="cast tight">${ph("ehon_015_001","江戶時代畫的三國","《繪本通俗三國志》插圖")}</div></div>""",
 "note": """<p>陸遜第十三回騙過關羽，<b>這一回要對付關羽的大哥</b>。同一個人，兩回。</p>"""},

{"html": """<div class="eyebrow">五 · 他不打</div>
 <h2>陸遜退了五百里</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>蜀軍氣勢正盛，陸遜<b>一路往後退</b>，退到山區才停</li>
     <li>吳軍的老將很生氣：<b>「一個書生，只會逃！」</b></li>
     <li>陸遜說：<b>他們現在最強，等他們累了再說。</b></li>
   </ul>
   <div class="callout">他等了<b>半年</b>。</div>
 </div>
 <div class="cast tight">${cf(chr({robe:"#4F7460",hat:"ru",beard:"mo",prop:"scroll"}),"陸遜","三十九歲")}${im("hourglass","等了半年")}</div></div>""",
 "note": """<p>第九回曹操在官渡也是撐半年。<b>「等」在三國是一種本事。</b></p>
 <p class="ask">問：「被自己人罵懦弱，還要繼續等，難不難？」</p>"""},

{"html": """<div class="eyebrow">六 · 夏天</div>
 <h2>七百里連營</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>六月，天氣熱到<b>士兵受不了</b></li>
     <li>劉備把水軍調上岸，在山林間<b>連紮了幾十座營寨</b>，前後綿延七百里</li>
     <li>消息傳到洛陽，曹丕看了地圖就說：<b>「劉備要輸了。」</b></li>
   </ul>
   <div class="callout">因為在樹林裡紮營，<br><b>最怕的就是火。</b></div>
 </div>
 <div class="cast tight">${ph("ehon_015_002","江戶時代畫的三國","《繪本通俗三國志》插圖")}</div></div>""",
 "note": """<p>第十回赤壁也是火、這一回也是火。<b>劉備在赤壁親眼看過那把火，卻犯了同樣的錯。</b></p>
 <p class="ask">問：「看過別人失敗，自己就不會犯嗎？」</p>"""},

{"html": """<div class="eyebrow">七 · 一把火</div>
 <h2>每個士兵帶一把茅草</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>陸遜先試攻一座營，確認<b>火攻可行</b></li>
     <li>當晚命令每個士兵<b>帶一把茅草</b>，順風點火</li>
     <li>幾十座營寨連在一起，<b>一燒就全部燒起來</b></li>
   </ul>
   <div class="callout">蜀漢的主力，<br><b>一夜之間沒有了。</b></div>
 </div>
 <div class="cast tight">${ph("shamoke","沙摩柯","替蜀漢打仗的部族首領，戰死")}</div></div>""",
 "note": """<p>「每人帶一把茅草」是史書寫的，<b>很具體、很好講</b>。</p>
 <p>這一戰蜀漢死了幾萬人，<b>是三國三大戰役的最後一場</b>（官渡、赤壁、夷陵）。</p>"""},

{"html": """<div class="eyebrow">八 · 三場大火</div>
 <h2>三國最重要的三場仗</h2>
 <div class="tier">
   <div><span class="lbl">官渡</span><span>200・曹操燒袁紹的糧——<b>北方統一</b></span></div>
   <div><span class="lbl">赤壁</span><span>208・周瑜燒曹操的船——<b>三國成形</b></span></div>
   <div><span class="lbl">夷陵</span><span>222・陸遜燒劉備的營——<b>三國定型</b></span></div>
 </div>
 <div class="callout">三場都是<b>以少打多</b>，<br>三場都是<b>用火</b>，<br>三場輸的都是<b>當時最強的那一邊</b>。</div>""",
 "note": """<p><b>整套課最好用的一張表。</b>三行唸完，孩子會自己看出規律。</p>
 <p class="ask">問：「為什麼強的那邊老是輸？」（因為強的人不小心）</p>"""},

{"html": """<div class="eyebrow">九 · 退</div>
 <h2>他退到白帝城，就不走了</h2>
 <div class="art wide"><div class="txt">
   <ul class="pts">
     <li>劉備一路撤退，靠著驛站燒車擋路才逃掉</li>
     <li>他退到<b>白帝城</b>，把地名改成「永安」</li>
     <li>他<b>沒有回成都</b>——史書說他「慚恚」，又羞愧又生氣</li>
   </ul>
   <div class="callout">六十二歲的人，<br><b>沒臉回家。</b></div>
 </div>
 ${mp("baidicheng","白帝城","長江邊上的城")}</div>""",
 "note": """<p>「沒臉回家」這一句很重。<b>孩子能理解這種心情。</b></p>"""},

{"html": """<div class="eyebrow">十 · 一句話</div>
 <h2>陸遜不追了</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>有人勸陸遜乘勝追擊，一舉滅掉蜀漢</li>
     <li>陸遜說：<b>不行，曹丕在後面看著</b></li>
     <li>他下令收兵——<b>果然幾個月後曹丕就南下打吳國了</b></li>
   </ul>
   <div class="callout">贏了以後<b>知道停下來</b>，<br>比贏本身更難。</div>
 </div>
 <div class="cast tight">${ph("shiting","石亭之戰","陸遜後來又打贏一場，清代版畫")}</div></div>""",
 "note": """<p>對照第十三回關羽「贏太多停不下來」。<b>陸遜是相反的例子。</b></p>
 <p class="ask">問：「為什麼贏了還要停？」</p>"""},

{"html": """<div class="eyebrow">十一 · 病</div>
 <h2>他在白帝城躺了八個月</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>222 年六月戰敗，他一直病到隔年春天</li>
     <li>他把諸葛亮從成都<b>叫到白帝城</b></li>
     <li>也把兒子<b>劉禪</b>的兩個弟弟帶來，但劉禪留在成都</li>
   </ul>
   <div class="callout">他知道自己要走了。</div>
 </div>
 <div class="cast tight">${ph("tuogutang","白帝城託孤堂","後人蓋的紀念堂")}</div></div>""",
 "note": """<p>照片可以講：<b>一千八百年後那個房間還在，而且叫「託孤堂」。</b></p>"""},

{"html": """<div class="eyebrow">十二 · 那四個字</div>
 <h2>「君可自取」</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>劉備對諸葛亮說：<b>「你的才能勝過曹丕十倍，一定能安定國家。」</b></li>
     <li>然後他說了讓一千多年的人吵到現在的一句話：</li>
   </ul>
   <div class="callout"><b>「如果我兒子值得輔佐，你就輔佐他；<br>如果他不行——你可以自己取代他。」</b></div>
   <p class="foot">諸葛亮當場<b>哭到叩頭流血</b>，說：「我一定盡全力，忠貞到死為止。」</p>
 </div>
 <div class="cast tight">${cf(chr({robe:"#EFE6D4",hat:"ru",beard:"mo",prop:"fu"}),"諸葛亮","四十三歲")}</div></div>""",
 "note": """<p>📄 原文就八個字：<b>「如其不才，君可自取。」</b>寫在黑板上。</p>
 <p class="ask">問：「他是真心的，還是在試探？」——<b>一千年來兩種說法都有人主張。</b>讓孩子選一邊，說理由。</p>"""},

{"html": """<div class="eyebrow">十三 · 對兒子說的話</div>
 <h2>不要因為壞事小就去做</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>他留了一封遺詔給劉禪</li>
     <li>裡面有一句話，後來變成中國人最常引用的家訓之一</li>
   </ul>
   <div class="callout"><b>「勿以惡小而為之，<br>勿以善小而不為。」</b></div>
   <p class="foot">——不要因為是小壞事就去做，<br>也不要因為是小好事就不做。</p>
 </div>
 <div class="cast tight">${im("books","遺詔")}${im("elder","給兒子的話")}</div></div>""",
 "note": """<p>📄 這兩句<b>一定要整句唸</b>，而且值得讓孩子抄下來。</p>
 <p>他還說：「勿以身長大而不勤學。」——不要因為長大了就不讀書。</p>"""},

{"html": """<div class="eyebrow">十四 · 走了</div>
 <h2>223 年四月，白帝城</h2>
 <div class="tl">
   <div><span class="yr">161</span><span>出生，家裡窮到要賣草鞋</span><span class="ago">第三回</span></div>
   <div><span class="yr">184</span><span>桃園結義，招了五百人</span><span class="ago">二十三歲</span></div>
   <div><span class="yr">208</span><span>三顧茅廬，有了計畫</span><span class="ago">四十七歲</span></div>
   <div><span class="yr">219</span><span>漢中王，人生最高點</span><span class="ago">五十八歲</span></div>
   <div class="now"><span class="yr">223</span><span>病死白帝城</span><span class="ago">六十三歲</span></div>
 </div>
 <div class="callout">他失敗的次數<b>比成功多太多</b>，<br>可是他<b>一次都沒有放棄</b>。</div>""",
 "note": """<p>五行走完一生。<b>這是整套課對劉備的總結。</b></p>
 <p>可以回頭翻第三回那個賣草鞋的畫面。</p>"""},

{"html": """<div class="eyebrow">十五 · 那個約定</div>
 <h2>不求同年同月同日生</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>第三回桃園結義時他們說：<b>不求同年同月同日生，但求同年同月同日死</b></li>
     <li>實際上：關羽 219 年冬、張飛 221 年、劉備 223 年</li>
     <li>前後<b>四年</b>，沒有同一天</li>
   </ul>
   <div class="callout">可是三十九年裡，<br><b>他們沒有一個人背叛過另外兩個。</b></div>
 </div>
 <div class="cast tight">${ph("ehon_015_003","江戶時代畫的三國","《繪本通俗三國志》插圖")}</div></div>""",
 "note": """<p>🚩 <b>整套課最該停下來的一頁。</b>第三回那個約定，走了十二回才收。</p>
 <p>對照呂布（第五、六、七回換了三個老闆）——<b>三十九年不背叛，才是這個約定的意思。</b></p>"""},

{"html": """<div class="eyebrow">十六 · 接下來誰管事</div>
 <h2>四十三歲的人，接了一個爛攤子</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>劉禪<b>十七歲</b>即位，國事全部交給諸葛亮</li>
     <li>蜀漢的家底：主力沒了、大將只剩趙雲、南方還在叛亂</li>
     <li>諸葛亮做的第一件事：<b>派人去跟東吳重新做朋友</b></li>
   </ul>
   <div class="callout">剛剛才殺得你死我活，<br><b>現在又要當盟友。</b></div>
 </div>
 <div class="cast tight">${ph("liushan","劉禪","十七歲即位")}</div></div>""",
 "note": """<p class="ask">問：「殺了你兄弟的人，還能當朋友嗎？」（在國家之間，可以——因為有更大的敵人）</p>
 <p>這是<b>隆中對的第一條</b>：孫權要當朋友。諸葛亮把它救回來了。</p>"""},

{"html": """<div class="eyebrow">十七 · 這一回的話</div>
 <h2>生氣的時候不要做大決定</h2>
 <div class="tier">
   <div><span class="lbl">關羽</span><span>贏太多，<b>停不下來</b>（第十三回）</span></div>
   <div><span class="lbl">張飛</span><span>太生氣，<b>對自己人動手</b>（這一回）</span></div>
   <div><span class="lbl">劉備</span><span>為了報仇，<b>把國家的本錢賭掉</b>（這一回）</span></div>
 </div>
 <div class="callout">三兄弟最後都倒在<b>同一件事</b>上——<br><b>情緒。</b></div>""",
 "note": """<p>三行指過去。回到開場「生氣時做的決定」那個問題。</p>
 <p>下一回預告：<b>接下來十一年，是一個人撐著一個國家。</b></p>"""},

{"html": """<div class="eyebrow">最後</div>
 <h2>今天哪些是編的</h2>
 <div class="cols">
   <div class="card"><h3>編的</h3><p>
     <b>關興、張苞替父報仇大殺四方</b>：小說加的<br><br>
     <b>諸葛亮擺八陣圖困住陸遜</b>：石陣是傳說<br><br>
     <b>劉備連營是被騙上山</b>：是天熱自己移的</p></div>
   <div class="card"><h3>真的</h3><p>
     <b>張飛被部下所殺</b>：真的<br><br>
     <b>趙雲反對伐吳</b>：真的<br><br>
     <b>陸遜退五百里、等半年</b>：真的<br><br>
     <b>七百里連營、曹丕看地圖就說會輸</b>：真的<br><br>
     <b>士兵各持一把茅草放火</b>：真的<br><br>
     <b>「君可自取」與遺詔那兩句</b>：真的，原文都留著</p></div>
 </div>
 <div class="callout">這一回<b>幾乎不用編</b>——<br>因為真實的結局，<br><b>已經比小說更讓人難過了。</b></div>""",
 "note": """<p>固定收尾頁。這一回情緒重，<b>結束前可以問問孩子今天的心情。</b></p>"""},
]
