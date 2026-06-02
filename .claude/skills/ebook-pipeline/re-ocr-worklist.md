# Re-OCR 工作清單（96 本：47 OCR-fail + 49 空白正文）

> 產生於 2026-06-03。「重新 OCR」= 已經 OCR 過但結果不堪用，要重打。

> 不含 77 本「從沒 OCR 過」的正規佇列（那走 daily bat / `ocr_with_gemini.py run`）。

> 跑法：`python scripts/ocr_with_gemini.py run --engine gemini --book <id>`（預設 Gemini；撞牆才 `--engine haiku` 一次一本）。


## A. OCR 永久失敗 — 47 本（`parse_error ILIKE 'OCR%'`）


### other（需逐本看 parse_error） — 37 本

- `768842fc-67a6-4f42-8a7b-39637551cc81` [世界宗教/東亞宗教] **「儒教國家」日本的實像** (pdf) — `OCR (Haiku >50MB): 'NoneType' object has no attribute 'content'`
- `c1a4bd47-4477-4aaa-8735-0462c8ab78b4` [世界宗教/基督教] **中國天主教傳教史概論** (pdf) — `OCR (Haiku >50MB): 'NoneType' object has no attribute 'content'`
- `34e021f5-64af-4299-8306-90bcc1fc660e` [世界宗教/基督教] **信仰與古典文明** (pdf) — `OCR (Haiku >50MB): 'NoneType' object has no attribute 'content'`
- `932d45e5-21f0-4543-b4e7-f8d07b0aa317` [世界宗教/東亞宗教] **北京道教石刻** (pdf) — `OCR (Haiku >50MB): 'NoneType' object has no attribute 'content'`
- `16bf6000-8b1d-489b-ab2f-3542928e520a` [世界宗教/基督教 / IVP - 古代基督信仰聖經註釋叢書] **古代基督信仰聖經註釋叢書48-50 加 弗 腓** (pdf) — `OCR (Haiku >50MB): 'NoneType' object has no attribute 'content'`
- `0fef76fe-b64c-4b48-8fa8-cdf45dd349d8` [世界宗教/基督教 / IVP - 古代基督信仰聖經註釋叢書] **古代基督信仰聖經註釋叢書58 來** (pdf) — `OCR (Haiku >50MB): 'NoneType' object has no attribute 'content'`
- `b43da28e-9c5d-4575-9d94-c38bf8e90a32` [世界宗教] **啟示的理性 歐洲哲學與基督宗教思想** (pdf) — `OCR: 400 INVALID_ARGUMENT. {'error': {'code': 400, 'message': 'Request contains `
- `974cbe95-ea9e-4199-872c-15fe14592a14` [世界宗教] **從天王傳統到佛王傳統** (pdf) — `OCR (Haiku >50MB): 'NoneType' object has no attribute 'content'`
- `da99b3eb-5c6f-4b73-a4fb-4bc5c0b63fa7` [世界宗教/東亞宗教] **苯教史綱要** (pdf) — `OCR (Haiku >50MB): 'NoneType' object has no attribute 'content'`
- `715733b6-acf4-41c4-92f9-a766fe9f960b` [人類生物學/考古學] **[上海三聯人文經典書庫 027]考古學導論** (pdf) — `OCR (Haiku >50MB): 'NoneType' object has no attribute 'content'`
- `51f1192f-aab2-4edd-94da-fb177054abad` [人類生物學/人類大歷史] **世界文明史** (pdf) — `OCR (Haiku >50MB): 'NoneType' object has no attribute 'content'`
- `816b65c0-5f5d-4316-9a8f-5327d0d8fe7d` [哲學/近代哲學] **二十世紀法國哲學** (pdf) — `OCR (Haiku >50MB): 'NoneType' object has no attribute 'content'`
- `bb1d63e8-f7c0-4f77-83db-5806113ffb7e` [哲學] **笛卡爾的精靈** (pdf) — `OCR (Haiku >50MB): 'NoneType' object has no attribute 'content'`
- `0b2be072-1af7-448a-b483-650123218616` [哲學/歷史哲學] **論歷史的起源與目標** (pdf) — `OCR (Haiku >50MB): 'NoneType' object has no attribute 'content'`
- `2edea5ec-4ed7-4017-bd30-1c6bbe229401` [哲學/經典與解釋輯刊] **讀陶淵明集札記** (pdf) — `OCR (Haiku >50MB): 'NoneType' object has no attribute 'content'`
- `c873c07f-7a48-44d8-ba96-3fed7d5c4b06` [哲學] **面對他者** (pdf) — `OCR (Haiku >50MB): 'NoneType' object has no attribute 'content'`
- `15c61e00-0ed1-4e8b-90ee-5c0937ca0869` [宗教學/神話學] **二十世紀的四種神話理論** (pdf) — `OCR (Haiku >50MB): 'NoneType' object has no attribute 'content'`
- `8bd496cf-f61a-4944-88c2-0db778fd07d2` [宗教學/宗教史] **劍橋宗教史** (pdf) — `OCR (Haiku >50MB): 'NoneType' object has no attribute 'content'`
- `e06a957a-e340-4912-af7e-8b7a8996363d` [宗教學] **英美文學和藝術中的古典神話** (pdf) — `OCR (Haiku >50MB): 'NoneType' object has no attribute 'content'`
- `79e70949-01ce-40e9-a2c3-fda5325e7841` [歷史學/美州界域史] **不可不知的美國史** (pdf) — `OCR (Haiku >50MB): 'NoneType' object has no attribute 'content'`
- `80e9bbbb-6a9a-421e-a0c1-0d28f7703da6` [歷史學/中央界域史] **古埃及托勒密王朝專制王權研究** (pdf) — `OCR (Haiku >50MB): 'NoneType' object has no attribute 'content'`
- `0ee18386-b73b-4651-9ac2-13182687d2e9` [歷史學/全球通史] **尼日利亞史** (pdf) — `OCR (Haiku >50MB): 'NoneType' object has no attribute 'content'`
- `84791d07-c9db-4c64-b50a-a08856c01c34` [歷史學] **戰國時代的古史記憶──虞夏之際篇** (pdf) — `OCR (Haiku >50MB): 'NoneType' object has no attribute 'content'`
- `320989c9-de76-4afc-99f4-25ff013250a2` [歷史學] **斯里蘭卡史 The History of Sri Lanka** (pdf) — `OCR (Haiku >50MB): 'NoneType' object has no attribute 'content'`
- `aa54b395-f4b7-470d-aa54-307f9074b506` [歷史學/美州界域史] **殺母的文化** (pdf) — `OCR (Haiku >50MB): 'NoneType' object has no attribute 'content'`
- `8d3775aa-4005-4d96-9bc1-42e3f11d7659` [歷史學/近代史] **法國革命的思想起源(1715-1787)** (pdf) — `OCR (Haiku >50MB): 'NoneType' object has no attribute 'content'`
- `84dbd342-595f-456e-978b-a574afc867c8` [歷史學] **瑞士史** (pdf) — `OCR (Haiku >50MB): 'NoneType' object has no attribute 'content'`
- `f1b49360-818a-4509-abaf-6dda85d61b83` [歷史學/史料原典] **羅馬史** (pdf) — `OCR (Haiku >50MB): 'NoneType' object has no attribute 'content'`
- `c2032eb0-3d19-4253-aab8-53a7f272ad6f` [社會政治學] **當社會主義遇到危機** (pdf) — `OCR (Haiku >50MB): 'NoneType' object has no attribute 'content'`
- `34feebc9-c9ff-4539-98e1-7e35298ad2cd` [神學/本地化處境神學] **1949年前大同_朔州天主教的傳播與本地化** (pdf) — `OCR: 400 Bad Request. {'message': 'Upload has already been terminated.', 'status`
- `45647aeb-d911-4213-8187-41e8660b93f3` [神學/主題專論] **克爾愷郭爾** (pdf) — `OCR: 400 Bad Request. {'message': 'Upload has already been terminated.', 'status`
- `45ae3534-464a-432a-a7e2-ce9165590229` [神學/中世紀著作] **基督之友** (pdf) — `OCR: 400 Bad Request. {'message': 'Upload has already been terminated.', 'status`
- `5a6aebd7-455f-43c3-937a-312c608da158` [神學/神學詮釋/哲學] **牆上的書寫 尼采與基督教** (pdf) — `OCR: 400 Bad Request. {'message': 'Upload has already been terminated.', 'status`
- `db40e09e-1449-4ea1-8cd0-ef262061f954` [神學/神學詮釋/哲學] **聖言人言神學詮釋學** (pdf) — `OCR: 400 Bad Request. {'message': 'Upload has already been terminated.', 'status`
- `8cbf945b-e05d-4f1a-88a1-a49713adc403` [神學/中世紀著作] **親吻神學+中世紀修道院情書選** (pdf) — `OCR: 400 Bad Request. {'message': 'Upload has already been terminated.', 'status`
- `072366c9-987c-4e02-804e-ef4c159b79b7` [神學/靈修神學] **記憶與光照** (pdf) — `OCR: [WinError 10053] 連線已被您主機上的軟體中止。`
- `7a678a11-37f7-41ec-a6e2-34c5389d7700` [自然科學] **從封閉世界到無限宇宙** (pdf) — `OCR (Haiku >50MB): 'NoneType' object has no attribute 'content'`

### oversized/頁數過多 — 7 本

- `f5f4ff52-5d23-4461-9376-7e3502a142c4` [世界宗教] **追尋一己之福 中國古代的信仰世界** (pdf) — `OCR: 'page'`
- `1c747cef-7c40-4286-989e-9c671becdbe1` [哲學/中國思想史] **儒家的心學傳統** (pdf) — `OCR: 400 INVALID_ARGUMENT. {'error': {'code': 400, 'message': 'The document has `
- `cde1ca44-a5cf-46d9-a102-61f2a1b6a759` [哲學/近代哲學] **康德、費希特和青年黑格爾論倫理神學** (pdf) — `OCR: 400 INVALID_ARGUMENT. {'error': {'code': 400, 'message': 'The document has `
- `532b0e5a-2592-4a7e-8ebe-e099744fe067` [心理學/生死學] **存在心理治療** (epub) — `OCR: 400 INVALID_ARGUMENT. {'error': {'code': 400, 'message': 'The document has `
- `50ec8887-43e3-4f58-a631-e70ab213e9a8` [歷史學/東方界域史] **從城市國家到中華** (epub) — `OCR: 400 INVALID_ARGUMENT. {'error': {'code': 400, 'message': 'The document has `
- `77abccf7-a7a1-43f3-b8c9-492c8d35b6a6` [歷史學/西方界域史] **法蘭西全史** (epub) — `OCR: 400 INVALID_ARGUMENT. {'error': {'code': 400, 'message': 'The document has `
- `d4942e79-eaf2-4b48-9167-86b9b5ade24b` [社會政治學/政治學] **觀念史研究** (pdf) — `OCR: 400 INVALID_ARGUMENT. {'error': {'code': 400, 'message': 'The document has `

### network — 2 本

- `d8995919-d0b0-446c-9509-dccc0c10602f` [世界宗教/基督教] **亞伯拉罕** (pdf) — `OCR (Haiku >50MB): Connection error.`
- `1eb97c7d-e4f1-487b-8cec-7b47a624b1e8` [自然科學] **現代科學的起源** (pdf) — `OCR (Haiku >50MB): Connection error.`

### JSON/parse 截斷 — 1 本

- `094548bf-fcb9-480f-bec8-c492b13640b2` [歷史學/全球通史] **世界文明大系11** (pdf) — `OCR: the JSON object must be str, bytes or bytearray, not NoneType`

## B. 正文抽取失敗（>50% chunks 空白/碎片）— 49 本

（來源：ocr-rescue-candidates.md；parsed_at 有值但正文是空的，要重 OCR 補正文）

- 100.0% 空白 (6/6) [世界宗教/] **追尋一己之福 中國古代的信仰世界** — `蒲慕州，追尋一己之福 中國古代的信仰世界.pdf`
- 100.0% 空白 (33/33) [世界宗教/伊斯蘭教] **天人合一物我還真** — `王俊榮，天人合一物我還真.pdf`
- 100.0% 空白 (473/473) [世界宗教/基督教] **走向十字架上的真** — `劉曉楓，走向十字架上的真.pdf`
- 100.0% 空白 (26/26) [世界宗教/基督教] **神秘神學** — `狄奧尼修斯，神秘神學.pdf`
- 100.0% 空白 (205/205) [世界宗教/東亞宗教] **國家與祭祀** — `子安宣邦，國家與祭祀.pdf`
- 100.0% 空白 (10/10) [世界宗教/波斯宗教] **阿維斯塔** — `選編，阿維斯塔.pdf`
- 100.0% 空白 (11/11) [世界宗教/猶太教] **猶太教的本質** — `拜克，猶太教的本質.pdf`
- 100.0% 空白 (9/9) [人類生物學/] **原始活態文化** — `郭淑雲，原始活態文化.pdf`
- 100.0% 空白 (16/16) [哲學/] **經典與解釋的張力** — `劉小楓，經典與解釋的張力.pdf`
- 100.0% 空白 (13/13) [哲學/哲學原典] **快樂的科學** — `尼采，快樂的科學.pdf`
- 100.0% 空白 (6/6) [哲學/經典與解釋輯刊] **古典傳統與自由教育** — `劉小楓，古典傳統與自由教育.pdf`
- 100.0% 空白 (6/6) [哲學/經典與解釋輯刊] **荷爾德林的新神話** — `劉小楓，荷爾德林的新神話.pdf`
- 100.0% 空白 (5/5) [哲學/經典與解釋輯刊] **美德可教嗎** — `劉小楓，美德可教嗎.pdf`
- 100.0% 空白 (112/112) [哲學/近代哲學] **尼采到底說了什麼？** — `羅伯特‧所羅門，尼采到底說了什麼？.pdf`
- 100.0% 空白 (68/68) [哲學/近代哲學] **現代性與後現代性十五講** — `陳嘉明，現代性與後現代性十五講.pdf`
- 100.0% 空白 (6/6) [文學/] **柏拉圖的哲學戲劇** — `劉小楓，柏拉圖的哲學戲劇.pdf`
- 100.0% 空白 (28/28) [社會政治學/] **中國人文主義新論** — `龍佳解，中國人文主義新論.pdf`
- 100.0% 空白 (572/572) [社會政治學/名家作品] **文化與帝國主義** — `愛德華·薩義德，文化與帝國主義.pdf`
- 100.0% 空白 (378/378) [社會政治學/政治學] **民主與城邦的衰落** — `菲利普‧內莫，民主與城邦的衰落.pdf`
- 100.0% 空白 (7/7) [社會政治學/政治學] **政治觀念史稿(三)** — `沃格林，政治觀念史稿(三).pdf`
- 100.0% 空白 (5/5) [社會政治學/政治學] **政治觀念史稿(五)** — `沃格林，政治觀念史稿(五).pdf`
- 96.7% 空白 (380/393) [文學/] **浮士德** — `歌德，浮士德.pdf`
- 95.5% 空白 (85/89) [世界宗教/] **誰為伊斯蘭講話？十幾億穆斯林的真實想法** — `[美]約翰.L.埃斯波西託  [美]達麗亞·莫格海德   晏瓊英王宇傑李維建 譯，誰為伊斯蘭講話？十幾億穆斯林的真實想法.pdf`
- 94.4% 空白 (51/54) [宗教學/] **敵人與鄰居：阿拉伯人和猶太人在巴勒斯坦和以色列，1917—2017** — `世界史的拼圖（7冊）.epub`
- 93.8% 空白 (75/80) [哲學/近代哲學] **海德格與禪道的跨文化溝通** — `賴賢宗，海德格與禪道的跨文化溝通.pdf`
- 90.9% 空白 (10/11) [世界宗教/] **啟示的理性 歐洲哲學與基督宗教思想** — `張憲，啟示的理性 歐洲哲學與基督宗教思想.pdf`
- 83.3% 空白 (5/6) [宗教學/宗教史] **宗教思想史** — `伊利亞德，宗教思想史.pdf`
- 80.6% 空白 (29/36) [歷史學/西方界域史] **古典歐洲的誕生：從特洛伊到奧古斯丁** — `企鵝歐洲史系列（套裝7冊）.epub`
- 79.5% 空白 (31/39) [世界宗教/佛教] **日本佛教史** — `末木文美士，日本佛教史.pdf`
- 79.1% 空白 (253/320) [世界宗教/佛教] **中國佛教史（卷3）** — `周貴華，世界佛教通史（14卷）.epub`
- 78.6% 空白 (11/14) [社會政治學/] **回訪歷史：新東歐之旅** — `巴巴拉·塔奇曼弗朗西斯·福山納爾遜·曼德拉奧蘭多·費吉斯，理想國譯叢系列 套裝32冊（MIRROR系列）.epub`
- 72.7% 空白 (16/22) [歷史學/全球通史] **雅典的勝利：文明的奠基** — `世界史的拼圖（7冊）.epub`
- 71.4% 空白 (5/7) [社會政治學/政治學] **政治觀念史稿(一)** — `沃格林，政治觀念史稿(一).pdf`
- 71.4% 空白 (5/7) [社會政治學/政治學] **政治觀念史稿(二)** — `沃格林，政治觀念史稿(二).pdf`
- 67.1% 空白 (100/149) [社會政治學/政治學] **秩序與歷史(全五卷)** — `埃裡克‧沃格林，秩序與歷史(全五卷).epub`
- 66.7% 空白 (12/18) [世界宗教/基/教會史] **十字軍史** — `喬納森·史密斯，十字軍史.pdf`
- 66.7% 空白 (28/42) [歷史學/全球通史] **奧斯曼帝國六百年：土耳其帝國的興衰** — `世界史的拼圖（7冊）.epub`
- 65.0% 空白 (13/20) [社會政治學/] **克里米亞戰爭：被遺忘的帝國博弈** — `巴巴拉·塔奇曼弗朗西斯·福山納爾遜·曼德拉奧蘭多·費吉斯，理想國譯叢系列 套裝32冊（MIRROR系列）.epub`
- 60.7% 空白 (65/107) [世界宗教/基/聖經抄本學-抄寫傳統] **非凡抄本尋訪錄** — `克里斯托弗‧哈梅爾，非凡抄本尋訪錄.epub`
- 60.7% 空白 (17/28) [歷史學/西方界域史] **追逐榮耀：1648—1815** — `企鵝歐洲史系列（套裝7冊）.epub`
- 60.0% 空白 (3/5) [世界宗教/佛教] **印度佛教史** — `沃德爾，印度佛教史.pdf`
- 59.0% 空白 (23/39) [社會政治學/] **教宗與墨索里尼：庇護十一世與法西斯崛起秘史** — `巴巴拉·塔奇曼弗朗西斯·福山納爾遜·曼德拉奧蘭多·費吉斯，理想國譯叢系列 套裝32冊（MIRROR系列）.epub`
- 57.1% 空白 (4/7) [宗教學/宗教對話] **Faith and power religion and politics in the Middle Eas** — `Lewis Bernard，Faith and power religion and politics in the Middle East.epub`
- 57.1% 空白 (12/21) [歷史學/] **城市發展史──起源、演變和前景** — `劉易斯·芒福德，城市發展史──起源、演變和前景.epub`
- 55.6% 空白 (10/18) [心理學/生死學] **活著有多久** — `理查德·金格拉斯，活著有多久.pdf`
- 55.3% 空白 (26/47) [歷史學/西方界域史] **希臘與羅馬兩部曲** — `安東尼·艾福瑞特，希臘與羅馬兩部曲.epub`
- 54.5% 空白 (24/44) [人類生物學/生物學] **我們人類的宇宙** — `克里斯托弗·波特，我們人類的宇宙.epub`
- 51.4% 空白 (54/105) [歷史學/西方界域史] **國王的兩個身體** — `恩斯特·坎託洛維奇，國王的兩個身體.epub`
- 50.4% 空白 (60/119) [歷史學/全球通史] **大西洋的故事** — `西蒙·溫撤斯特，大西洋的故事.epub`
