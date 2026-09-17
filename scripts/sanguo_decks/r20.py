# -*- coding: utf-8 -*-
"""第二十回　三國歸晉（234–280）

全套課收尾。最後要回到第一回那張地圖。
收尾頁是整套課二十回的虛構清單總表。
"""

TITLE = "三國第二十回"
MARK = "三國演義 · 第二十回"
SUB = "三國歸晉"

SLIDES = [
{"cover": True,
 "html": """<div class="art">
   <div class="txt">
     <div class="eyebrow">第二十回</div>
     <h1>六十年，<em>回到一個國家</em></h1>
     <p class="sub">吵了六十年，死了幾百萬人。<br>最後贏的，不是那三個人裡的任何一個。</p>
     <div class="meta">
       <div><dt>時間</dt><dd>西元 234–280 年</dd></div>
       <div><dt>這一回</dt><dd>三國歸晉</dd></div>
       <div><dt>今天要弄懂</dt><dd>誰才算真的贏</dd></div>
     </div>
     <p class="credit">版畫與繡像取自維基共享資源，出處見上方「圖片來源」</p>
   </div>
   <div class="cast">
     ${cf(chr({robe:"#EFE6D4",hat:"mian",cuff:"#5A5248",beard:"mo"}),"司馬炎","統一天下的人")}
     ${im("map","又變成一塊")}
   </div>
 </div>""",
 "note": """<p><b>最後一回。</b>今天要把前面十九回全部串起來，留時間給最後三頁。</p>
 <p class="ask">開場問：「打贏的人就是贏家嗎？」最後一頁回來對。</p>"""},

{"html": """<div class="eyebrow">一 · 接棒的人</div>
 <h2>姜維：老師的計畫，他一個人扛</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>蔣琬、費禕在的時候，姜維<b>每次要兵都給不到一萬</b></li>
     <li>253 年費禕被刺身亡，姜維才真正掌握兵權</li>
     <li>接下來十年，他<b>前後北伐十一次</b></li>
   </ul>
   <div class="callout">諸葛亮五次，<br><b>姜維十一次。</b></div>
 </div>
 <div class="cast tight">${cf(chr({robe:"#8C2F1E",hat:"wu",beard:"mo",prop:"spear"}),"姜維","諸葛亮最後的學生")}</div></div>""",
 "note": """<p>接第十九回的交棒。<b>姜維是外來的降將，卻比誰都堅持。</b></p>
 <p class="ask">問：「為什麼一個魏國人這麼拚命打魏國？」</p>"""},

{"html": """<div class="eyebrow">二 · 打不動</div>
 <h2>勝多敗少，可是沒有用</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>姜維的戰績其實<b>贏的比輸的多</b></li>
     <li>可是每贏一次，蜀漢就<b>耗掉一次家底</b>，魏國卻補得回來</li>
     <li>國內開始反對：有大臣寫文章說<b>「再打下去，國家會先垮」</b></li>
   </ul>
   <div class="callout">小的一方每贏一次，<br><b>離輸就更近一步。</b></div>
 </div>
 <div class="cast tight">${ph("zhugejin","諸葛瑾","諸葛亮的哥哥，在東吳做官")}</div></div>""",
 "note": """<p>第十七回那張人口長條圖可以翻回去。<b>差距不是靠打仗補得回來的。</b></p>"""},

{"html": """<div class="eyebrow">三 · 北邊那家人</div>
 <h2>司馬懿等到了</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>239 年魏明帝死，八歲的皇帝即位，由<b>曹爽</b>和司馬懿一起輔政</li>
     <li>曹爽把他架空，司馬懿<b>又開始裝病</b>——這次裝了十年</li>
     <li>249 年正月，曹爽陪皇帝出城掃墓——<b>司馬懿發動政變，關了城門</b></li>
   </ul>
   <div class="callout">這一天叫<b>高平陵之變</b>。<br>從此魏國的兵權，<b>姓司馬。</b></div>
 </div>
 <div class="cast tight">${ph("simashi","司馬師","司馬懿的長子")}</div></div>""",
 "note": """<p>「裝病」第三次出現（第十三回呂蒙、第十八回司馬懿早年、這一回）。<b>三國最有效的武器是演技。</b></p>
 <p>司馬懿那年七十歲，<b>他等了一輩子。</b></p>"""},

{"html": """<div class="eyebrow">四 · 同一件事再來一次</div>
 <h2>皇帝又變成招牌了</h2>
 <div class="tier">
   <div><span class="lbl">189</span><span>董卓控制漢獻帝（第四回）</span></div>
   <div><span class="lbl">196</span><span>曹操迎天子（第八回）</span></div>
   <div><span class="lbl">220</span><span>曹丕取代漢朝（第十四回）</span></div>
   <div class="now"><span class="lbl">249</span><span>司馬懿控制魏國皇帝——<b>一模一樣</b></span></div>
 </div>
 <div class="callout">曹家對漢朝做的事，<br><b>三十年後有人對曹家做一次。</b></div>""",
 "note": """<p>🚩 <b>整套課最漂亮的一個循環。</b>四行指過去，孩子會自己看出來。</p>
 <p class="ask">問：「為什麼一樣的事會一直發生？」</p>"""},

{"html": """<div class="eyebrow">五 · 那句話</div>
 <h2>司馬昭之心，路人皆知</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>司馬懿死後，兒子司馬師、司馬昭接著掌權</li>
     <li>年輕的魏帝<b>曹髦</b>受不了，說了一句很有名的話</li>
     <li>他帶著幾百個僕人衝出宮去，<b>當街被殺</b></li>
   </ul>
   <div class="callout"><b>「司馬昭之心，路人皆知也。」</b><br>——他想幹什麼，<b>連路上的人都看得出來。</b></div>
 </div>
 <div class="cast tight">${ph("simazhao","司馬昭","清代繡像")}</div></div>""",
 "note": """<p>這句成語孩子一定聽過，<b>但多半不知道說的人當場就死了。</b></p>
 <p>一個皇帝被自己的臣子當街殺掉——<b>整個三國最難堪的一天。</b></p>"""},

{"html": """<div class="eyebrow">六 · 滅蜀</div>
 <h2>263 年，三路大軍南下</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>司馬昭要立威，決定<b>先滅蜀漢</b></li>
     <li>主力由<b>鍾會</b>帶領，正面攻打漢中</li>
     <li>姜維退守<b>劍門關</b>——十幾萬大軍卡在關前，<b>過不去</b></li>
   </ul>
   <div class="callout">第十二回那張劍門關的照片還記得嗎？<br><b>一夫當關，萬夫莫開。</b></div>
 </div>
 <div class="cast tight">${cf(chr({robe:"#2E4A63",hat:"jin",beard:"mo",prop:"jian"}),"鍾會","主力統帥")}${im("mountain","劍門關")}</div></div>""",
 "note": """<p>回頭翻第十二回劍門關那張照片。<b>五十年後，同一個地方。</b></p>"""},

{"html": """<div class="eyebrow">七 · 那條沒有路的路</div>
 <h2>鄧艾走陰平</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>另一路的<b>鄧艾</b>做了一個瘋狂的決定：走沒有人走的<b>陰平小道</b></li>
     <li>七百里無人區，<b>遇到懸崖就鑿路、沒有路就用繩子吊下去</b></li>
     <li>最險的地方，他<b>用毯子裹著自己滾下山</b>——士兵跟著滾</li>
   </ul>
   <div class="callout">他從一個<b>沒有人設防的方向</b>，<br>忽然出現在成都平原上。</div>
 </div>
 <div class="cast tight">${ph("dengai","鄧艾","清代繡像")}</div></div>""",
 "note": """<p><b>這一段孩子會很興奮。</b>鄧艾那年六十七歲，還自己裹毯子滾下山。</p>
 <p>他小時候口吃、家裡很窮、放過牛——<b>這是整套課最勵志的一個人。</b></p>"""},

{"html": """<div class="eyebrow">八 · 開城</div>
 <h2>還有兵，可是投降了</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>鄧艾兵力其實不多，但成都<b>完全沒有準備</b></li>
     <li>大臣<b>譙周</b>主張投降；劉禪的兒子<b>劉諶</b>反對，在昭烈廟哭完就自殺了</li>
     <li>劉禪選擇<b>開城投降</b>——姜維還在劍門關，一仗都沒輸</li>
   </ul>
   <div class="callout">蜀漢立國<b>四十三年</b>，<br>從第三回桃園結義算起<b>七十九年</b>。</div>
 </div>
 <div class="cast tight">${cf(chr({robe:"#C9A227",hat:"mian",cuff:"#8A6E18"}),"劉禪","在位四十一年")}${im("castle","成都開城")}</div></div>""",
 "note": """<p>🚩 劉諶自殺那一段很重，但<b>不要細講</b>。重點是：<b>同一個國家裡有人選擇死，有人選擇活。</b></p>
 <p class="ask">問：「投降是不是一定不對？」（成都因此沒有被屠城）</p>"""},

{"html": """<div class="eyebrow">九 · 最後一計</div>
 <h2>姜維還想救回來</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>接到投降命令時，蜀軍將士<b>氣得拿刀砍石頭</b></li>
     <li>姜維假裝投降鍾會，<b>慫恿他自立</b>——打算趁亂復國</li>
     <li>結果計畫敗露，<b>鍾會、姜維、鄧艾都死在那場混亂裡</b></li>
   </ul>
   <div class="callout">他死的時候<b>六十二歲</b>。<br>史書說他<b>「死於亂軍之中」</b>。</div>
 </div>
 <div class="cast tight">${ph("ehon_011_004","江戶時代畫的三國","《繪本通俗三國志》插圖")}</div></div>""",
 "note": """<p>姜維這一計如果成功，歷史會完全不同。<b>他到死都在執行諸葛亮的計畫。</b></p>"""},

{"html": """<div class="eyebrow">十 · 那句話</div>
 <h2>樂不思蜀</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>劉禪被送到洛陽。有一天司馬昭辦宴會，故意演<b>蜀國的音樂舞蹈</b></li>
     <li>跟著來的蜀漢舊臣都掉眼淚，只有劉禪<b>笑得很開心</b></li>
     <li>司馬昭問他：想不想蜀國？他說：<b>「此間樂，不思蜀。」</b></li>
   </ul>
   <div class="callout">——這裡很快樂，<b>我不想蜀國。</b></div>
   <p class="foot">司馬昭說：「一個人怎麼可以沒良心到這種地步。」從此不再防他。劉禪活到六十四歲，善終。</p>
 </div>
 <div class="cast tight">${im("bowl","宴會")}${im("tea","笑得很開心")}</div></div>""",
 "note": """<p>🚩 <b>這一頁一定要問：他是真傻還是裝傻？</b>兩種說法都有人主張。</p>
 <p>（如果他表現得想念蜀國，很可能當場就被殺了。）</p>"""},

{"html": """<div class="eyebrow">十一 · 換朝代</div>
 <h2>266 年，司馬炎受禪</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>司馬昭死後，兒子<b>司馬炎</b>要魏國最後一個皇帝讓位</li>
     <li>流程和<b>第十四回曹丕逼漢獻帝</b>一模一樣：三讓三辭</li>
     <li>國號改為<b>晉</b></li>
   </ul>
   <div class="callout">曹家用這一套<b>取代了漢朝</b>，<br>四十六年後，<b>司馬家用同一套取代了曹家。</b></div>
 </div>
 <div class="cast tight">${ph("yanghu","羊祜","晉朝名將，主張善待吳國")}</div></div>""",
 "note": """<p>回頭指第十四回那場禪讓典禮。<b>連流程都一樣——這是整套課最諷刺的一頁。</b></p>"""},

{"html": """<div class="eyebrow">十二 · 最後一個</div>
 <h2>280 年，王濬的船開進建業</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>吳國最後一個皇帝<b>孫皓</b>殘暴無道，人心已散</li>
     <li>晉軍分六路南下，長江上的鐵鏈被<b>大火炬燒斷</b></li>
     <li>孫皓<b>反綁雙手、抬著棺材</b>出城投降</li>
   </ul>
   <div class="callout">從 184 年黃巾之亂算起，<br><b>九十六年。</b></div>
 </div>
 <div class="cast tight">${ph("sunhao","孫皓","吳國最後一個皇帝")}</div></div>""",
 "note": """<p>「抬著棺材投降」是古代的投降儀式，<b>表示任憑處置</b>。</p>
 <p>第十三回龐德也抬過棺材——<b>一個是不降，一個是降。同一個東西，兩種意思。</b></p>"""},

{"html": """<div class="eyebrow">十三 · 那首詩</div>
 <h2>一片降幡出石頭</h2>
 <div class="callout" style="font-family:var(--serif);font-size:clamp(1.05rem,1.9vw,1.6rem);line-height:2">
   王濬樓船下益州，金陵王氣黯然收。<br>
   千尋鐵鎖沉江底，<b>一片降幡出石頭。</b><br>
   人世幾回傷往事，山形依舊枕寒流。<br>
   今逢四海為家日，故壘蕭蕭蘆荻秋。
 </div>
 <p class="foot">——王濬的大船從四川開下來，南京的帝王氣就散了。<br>
 千丈長的鐵鏈沉到江底，<b>石頭城上升起一面投降的白旗。</b><br>
 人世間多少次為往事傷心，山還是那座山，靜靜靠著冰冷的江水。</p>""",
 "note": """<p>📄 <b>整首唸出來。</b>劉禹錫〈西塞山懷古〉，寫於 824 年——<b>離三國結束已經五百多年。</b></p>
 <p>「山形依舊枕寒流」那一句：<b>人來人去，山還在那裡。</b></p>"""},

{"html": """<div class="eyebrow">十四 · 回到第一回</div>
 <h2>那張地圖，又變成一塊</h2>
 <div class="art wide"><div class="txt">
   <ul class="pts">
     <li>第一回我們看的是<b>東漢十三州</b>，一個國家</li>
     <li>中間分成三塊，打了六十年</li>
     <li>280 年之後，<b>又變回一個國家</b>——只是換了姓</li>
   </ul>
   <div class="callout">繞了一大圈，<br><b>回到原來的地方。</b></div>
 </div>
 ${mp("map_jin","西晉統一疆域圖","280 年，又變回一塊")}</div>""",
 "note": """<p>🚩 <b>整套課的收束。</b>翻回第一回那張地圖對照。</p>
 <p class="ask">問：「那這六十年到底是為了什麼？」——這個問題沒有標準答案。</p>"""},

{"html": """<div class="eyebrow">十五 · 誰贏了</div>
 <h2>三個主角，沒有一個</h2>
 <div class="three">
   <div class="wei">${chr({robe:"#EFE6D4",hat:"ze",beard:"mo"})}<div class="n">曹</div><div class="who">曹操沒稱帝</div><div class="where">被司馬家取代</div></div>
   <div class="shu">${chr({robe:"#EFE6D4",hat:"ze",beard:"mo"})}<div class="n">劉</div><div class="who">劉備稱帝兩年</div><div class="where">兒子投降</div></div>
   <div class="wu">${chr({robe:"#EFE6D4",hat:"ze"})}<div class="n">孫</div><div class="who">孫權最長壽</div><div class="where">孫子抬棺投降</div></div>
 </div>
 <div class="callout">最後坐上那個位子的人，<b>第一回的時候還沒有出生。</b></div>""",
 "note": """<p>回到開場「打贏的人就是贏家嗎」。<b>司馬炎生於 236 年——比整個故事晚了五十年。</b></p>"""},

{"html": """<div class="eyebrow">十六 · 後來呢</div>
 <h2>晉朝也沒有撐很久</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>統一之後<b>只太平了十年</b></li>
     <li>接著晉朝的皇族自己打起來（八王之亂），<b>比三國還亂</b></li>
     <li>然後是三百年的分裂，一直到<b>隋朝</b>才再統一</li>
   </ul>
   <div class="callout">所以「三國歸晉」不是快樂結局，<br><b>只是一個逗號。</b></div>
 </div>
 <div class="cast tight">${ph("zhugedan","諸葛誕","諸葛亮的族弟，在魏國起兵反司馬")}</div></div>""",
 "note": """<p>🚩 <b>不要給孩子一個假的圓滿結局。</b>歷史沒有結束，只有下一段。</p>"""},

{"html": """<div class="eyebrow">十七 · 二十回走完了</div>
 <h2>我們跟著誰走了這一程</h2>
 <div class="tl">
   <div><span class="yr">184</span><span>三個人在桃花樹下結拜</span><span class="ago">第三回</span></div>
   <div><span class="yr">208</span><span>一把火燒出三個國家</span><span class="ago">第十回</span></div>
   <div><span class="yr">220</span><span>四百年的漢朝結束</span><span class="ago">第十四回</span></div>
   <div><span class="yr">234</span><span>五丈原的燈滅了</span><span class="ago">第十九回</span></div>
   <div class="now"><span class="yr">280</span><span>又變回一個國家</span><span class="ago">今天</span></div>
 </div>
 <div class="callout">二十堂課，<br><b>走了九十六年。</b></div>""",
 "note": """<p>五行慢慢指過去。<b>讓孩子說出他最記得的一頁。</b></p>"""},

{"html": """<div class="eyebrow">十八 · 最後一句</div>
 <h2>為什麼一千八百年後還在講</h2>
 <div class="art"><div class="txt">
   <ul class="pts">
     <li>因為裡面的人<b>都做過對的事，也都做過錯的事</b></li>
     <li>因為最厲害的人<b>沒有成功</b>，最後贏的人<b>沒有人喜歡</b></li>
     <li>因為每一個選擇，<b>你都可以問「換成我會怎麼做」</b></li>
   </ul>
   <div class="callout">歷史不是用來背的，<br><b>是用來問問題的。</b></div>
 </div>
 <div class="cast tight">${ph("ehon_002_001","《繪本通俗三國志》","江戶刊本書名頁")}</div></div>""",
 "note": """<p><b>整套課的最後一頁。</b>可以請孩子說：這二十回裡，他最想成為誰、最不想成為誰，為什麼。</p>"""},

{"html": """<div class="eyebrow">最後</div>
 <h2>二十回的虛構總表</h2>
 <div class="cols">
   <div class="card"><h3>最有名的假的</h3><p>
     桃園結義（第三回）・三英戰呂布（五）<br>
     貂蟬與連環計（六）・過五關斬六將（九）<br>
     草船借箭、借東風、華容道（十）<br>
     既生瑜何生亮（十一）・空城計（十八）<br>
     魏延反骨（十九）</p></div>
   <div class="card"><h3>最該記得的真的</h3><p>
     曹操燒掉通敵的信（九）<br>
     十萬百姓跟著劉備逃（十）<br>
     呂蒙用家書解散一支大軍（十三）<br>
     「勿以惡小而為之」（十五）<br>
     打完不留一兵一官（十六）<br>
     諸葛亮自貶三級（十八）<br>
     桑八百株、田十五頃（十九）</p></div>
 </div>
 <div class="callout">二十回下來你會發現：<br><b>編的那些比較好看，真的那些比較耐想。</b></div>""",
 "note": """<p>🚩 <b>整套課的收尾頁。</b>兩欄慢慢唸完。</p>
 <p>最後一句是二十回的總結——<b>唸完就結束，不要再補充。</b></p>"""},
]
