---
name: coach-language
description: AI 語言教練（/coach）— 外語自學系統，多語言（英文 Emily / 德文 Lukas / 法文 Camille / 日文 櫻子 / 通用希臘文 Sophia / 教會拉丁文 Marcus / 聖經希伯來文 Miriam 全上線）。核心：Gemini 對話 + Web Speech 語音；每語言獨立空間（首頁/儀表板/記憶/功能各自客製）。功能含五種聊天模式（打字/口說/問答知識/情境角色/限時主題）、今日計畫（每日推薦單字測驗+5閱讀+5聽力+口說+任務）、分級文法課（CEFR/JLPT/古語言量表）、技能練習與 TOEFL/IELTS/GRE 考試模擬、翻譯遊戲、YouTube/文章沉浸（讀聽後 MCQ+討論+評分）、統整記憶庫、教練每日簡報與日誌、SRS 單字、轉寫鍵盤（希臘文打英文＝希臘字母／日文打羅馬字＝假名／希伯來文打英文＝希伯來字母 RTL）、雙 key 成本控管。Use when 改語言教練任何功能、加語言、調人設/難度/題材、改資安（OTP 登入/付費上限）、接 Gemini key、debug coach 端點或頁面。
---

> ⚙️ **引擎政策（2026-06-04 統一）**：所有 LLM 工作一律 **Gemini（主，4 keys 輪流）→ NVIDIA（輝達 `https://integrate.api.nvidia.com/v1`，文字模型 `deepseek-ai/deepseek-v4-flash`，4 把 key 輪流＋間隔節流避 429）→ Haiku（最後救急；前兩個免費池都用罄才動）**。`translate_ebook_to_zh.py --engine auto` 預設即此鏈。視覺／OCR 類仍走 Gemini Vision／Haiku Vision（NVIDIA vision 尚未驗證）。例外：/coach 互動聊天為 NVIDIA qwen3-next 主、Gemini 後備（見 [[feedback_coach_nvidia_engine]]）。見 [[feedback_engine_nvidia_no_haiku]]。

> 🚨 **截圖規則 — 絕對禁止 >2000px**：任一邊超過 2000px 會炸掉 session。

# AI 語言教練 Skill

使用者（宗教研究者）的外語自學系統。**現上線 7 語**：英文 **B2→C2→TOEFL**；德文 **A1（初學）**／法文 **A1（初學）**（皆現代活語言、有 STT/TTS）；日文 **N5→N4（初學）**；通用希臘文（Koine）／教會拉丁文（Ecclesiastical）／聖經希伯來文（Biblical）**三古典語皆入門（初學）**。題材**以宗教/神話/宗教學為主軸**，輔以人文，少量理工醫/生活/旅遊（考試模式走真實考題）；三古典語題材＝神學院教的版本（**非古典／非現代**），詳見下方「語言一覽」。相關偏好見 [[project_language_coach]]、[[feedback_language_coach_religious_studies]]、[[feedback_traditional_chinese_only]]、[[feedback_coach_nvidia_engine]]。

部署：**Zeabur**（GitHub master 自動部署）。DB：Supabase（Management API 跑 DDL，見 [[reference_supabase_management_api]]）。

---

## 〇、語言一覽（7 語上線 · 全部定義在 `server/utils/lang-coaches.ts`）

| code | 教練 | 量表·預設 | 語音 | 鍵盤 | TTS | 題材重點（皆宗教研究取向） |
|---|---|---|---|---|---|---|
| `en` | Emily 🗽 | CEFR·**B2** | 有 STT/TTS | — | en-US | 宗教/神話/宗教學為主＋人文；考試走 AWL/GRE/TOEFL |
| `de` | Lukas 🍺 | CEFR·**A1** | 有 STT/TTS | — | de-DE | 標準德語 Hochdeutsch；**A1 初學重單字×文法×輸入**（der/die/das 三性＋四格 Kasus＋變位＋語序）；A1 走日常/文化，隨程度再帶宗教（路德/宗改/聖經德譯） |
| `fr` | Camille 🥐 | CEFR·**A1** | 有 STT/TTS | — | fr-FR | 巴黎標準法語；**A1 初學重單字×文法×輸入**（陰陽性 le/la＋變位＋發音/liaison/鼻母音）；A1 走日常/文化，隨程度再帶宗教（天主教/主教座堂/laïcité） |
| `ja` | 櫻子 🌸 | JLPT·**N5** | 有 STT/TTS | **kana**（羅馬字→假名） | ja-JP | 關東標準語；N5→N4 初學，神社祭典/文化/宗教淺白題 |
| `grc` | Sophia 🦉 | 古·**入門** | voiceless | **greek**（英文→希臘字母 Beta Code） | el-GR | **通用希臘文 Koine（非古典 Attic/荷馬）**：新約／LXX／使徒教父／信經大公會議（公元初–中世紀前）／希臘化猶太（斐羅・約瑟夫斯）／哲學家／拜占庭官方文獻 |
| `la` | Marcus 🏛️ | 古·**入門** | voiceless | —（拉丁字母直打） | it-IT（教會式） | **教會拉丁文 Ecclesiastical（非古典）**：武加大／拉丁教父（奧古斯丁・耶柔米・安博…）／禮儀信經大公會議 →經院神哲學（安瑟倫・倫巴德・阿奎那… summae/quaestiones）→中世紀各學科（教會法／編年史聖徒傳／大學講義／自然哲學／醫學／七藝） |
| `hbo` | Miriam 🕎 | 古·**入門** | voiceless | **hebrew**（英文→希伯來字母，RTL） | he-IL | **舊約聖經希伯來文 Biblical（非現代以色列語）**：以舊約為起點（妥拉先讀創世記詩篇／先知書／智慧文學）→死海古卷昆蘭／米示拿‧拉比希伯來文／中世紀註釋（拉希）／禮儀碑銘；底本 BHS |

- **古典語三本柱（grc/la/hbo）共同政策**：`enabled:true`、`levelScale=ANCIENT(["入門","初級","中級","進階"])`、`defaultLevel="入門"`、`voiceless:true`（無 STT，chat 不顯示麥克風/自動朗讀）；人設一律「神學院版、非古典/非現代、初學者、逐字 parse、大量夾繁中」。**勿改回古典定向**（見 [[feedback_language_coach_religious_studies]]）。
- **德 `de`(Lukas🍺) / 法 `fr`(Camille🥐) 已於 2026-06-04 全面上線**（`enabled:true`）：A1 初學定向，人設明寫「打基礎＝單字×文法×輸入」、名詞一律連冠詞/性別教、隨程度再轉宗教題材；活語言有 STT/TTS、不 voiceless、無轉寫鍵盤（拉丁字母直打）。`review.vue` 的 `THEME_POOLS`/`TTS_LANG` 已補 de/fr（A1 高頻字＋日常，後段帶宗教詞）。
- 每語言 4–5 個 `personas`（聊天輪替）＋ `smalltalkTopics`/`scenarios`/`qaTopics`（首頁今日推薦 + chat 開場用），古典語皆為「精讀／文法／抄經／信經」類初學題。

---

## 一、頁面結構（每語言獨立空間）

選擇頁 `/coach`（只挑語言）→ 進入 `/coach/[lang]/`，之後全部專屬該語言（語言由路由決定，無語言下拉）：

- `/coach/[lang]`（index）= **語言首頁**：教練主動「今日簡報」、統計列、**📅今日計畫主入口**、聊天五磚、學習五磚、學習日曆+教練日誌、統整記憶庫
- `/coach/[lang]/today` = **今日計畫**（見下）
- `/coach/[lang]/chat` = 對話（`?mode=qa|scenario`、`?voice=1`）
- `/coach/[lang]/smalltalk` = 限時主題聊（3/5/10 分倒數 + 結束評分）
- `/coach/[lang]/alphabet` = **字母教學 + 字母測驗**（**僅非英文 6 語**：de/fr/ja/grc/la/hbo）
- `/coach/[lang]/parse` = **詞形判析（parsing）自動批改**（零 AI；grc 新約 + hbo 舊約）
- `/coach/[lang]/compose` = **句子重組（受限寫作題型）**（零 AI；en 情境句 + grc/hbo 經文 + de/fr/la 字庫例句；ja 無詞間空白暫不支援）
- `/coach/[lang]/grammar` = 分級文法課
- `/coach/[lang]/practice` = 技能練習 / 考試模擬 / 翻譯遊戲
- `/coach/[lang]/review` = 單字 SRS（翻卡 / 選擇題 / 克漏字，FSRS）；另有 `/reader` 點讀、`/shadowing` 跟讀、`/writing` 寫作批改
- `/coach/[lang]/immersion` = YouTube/文章沉浸
- `/coach/[lang]/dashboard` = 該語言儀表板 + Gemini 用量/成本

## 二、聊天五模式（chat.post.ts 依 mode 套 prompt；人格自動輪替）

- **打字 / 口說**（free，voice=1 自動朗讀）。🎤 語音輸入（`composables/useSpeech.ts`）為**連續聆聽**：`continuous=true` + onend keep-alive 自動重啟（`wantListening` 旗標），停頓思考不會關麥克風，**只有手動按停才停**；辨識文字即時附加到輸入框、不自動送出。`no-speech`/`aborted` 視為正常不報錯，僅權限/裝置錯誤（`not-allowed`/`audio-capture`…）才中止。
- **問答‧知識**（qa）：像一般 AI 答題教知識，corrections 通常空
- **情境角色**（scenario）：教練演對方角色（店員/面試官/神職…）
- **限時主題聊**（smalltalk 頁）
- 人格：`lang-coaches.ts` `personas[]`，新對話依 session 數輪替（`pickPersona`）。**7 語全部都有 personas**（各 4–5 種：英文閨蜜/面試官/辯論/教授/說書人；德/法 朋友/文法/單字/文化嚮導/讀經或發音；日文 姉さん/文法/單字/文化嚮導/敬語；古典語 精讀/文法/抄經/信經…），各依該語言程度與宗教研究取向設計。注入統整記憶 + 人格 + 本次摘要進 system prompt。⚠️ 加新語言一定要附 personas，否則 `pickPersona` 回 null、人格不輪替。
- **今日推薦（每天輪替，2026-06-04）**：語言首頁聊天磚下方「今日推薦 · 每天換」三排 chip — 💬聊話題（`smalltalkTopics`）/💡問知識（`qaTopics`）/🎭演情境（`scenarios`），各 3 個，以「當天日期種子」輪替（同天穩定、隔天換）。點 chip 直接 deep-link 進 chat（`?topic=` / `?mode=qa&topic=` / `?mode=scenario&scenario=`），`chat.vue` onMounted 讀 query 自動開場。資料每語言各一份（`lang-coaches.ts` 各 coach 的 `smalltalkTopics`/`scenarios`/`qaTopics`）：英文宗教學取向、日文 N5→N4 初學版（漢字附假名）、**古典語三本柱皆為初學的精讀／文法／信經題**（如 grc「逐字精讀約翰福音 1:1」、hbo「從希伯來字母讀起」、la「讀一則 quaestio 的論證結構」）。

## 三、今日計畫（today）— 每日自學核心

`lang_daily`（PK user+lang+date）一天生成一次 topics 快取。
- **進度**：已記住單字（mastery≥3）/ 待複習 / 占目標程度詞彙約 %（`daily.get` VOCAB_TARGET 概估，英文 C2≈8000）
- **今日任務** checklist + **今日 5 閱讀 + 5 聽力 + 5 口說**（點開才 `daily/item` 懶生成）
- 閱讀短文 / 聽力 TTS 朗讀 + **4 選 1 理解題**（自動對答案、記時間）
- **古典語 grc/la/hbo 閱讀/聽力＝策展經文短文庫（2026-06-18，零 AI）**：`server/data/coachPassages.ts` 三語各 8 篇公有領域經文（新約/七十士/武加大/BHS：約 1:1、約 3:16、創 1:1、主禱文、Shema、詩 23:1、祭司祝福…）＋繁中摘要＋理解題。`daily.get` 對 `CURATED_PASSAGE_LANGS` 用 `pickDailyPassages(lang, 台北日期+鹽, 5)` 確定性每日輪替挑題（閱讀/聽力種子加 `|r`/`|l` 分流），item 帶 `bankId`；`daily/item.post` 偵測 `bankId`→ 取 `passageById` 直接給 content（passage/audio_text/questions/summary），**零 AI**。⚠️ `today.vue` 的 MCQ 比對已改兼容兩種格式：AI 格式（選項「A. …」＋answer 字母）與策展格式（選項全文＋answer 全文），靠 `optLetter`/`ansKey`。其他語言（en/de/fr/ja）仍走 AI。
- 每項可**口說/打字討論**（/api/lang/chat 即時糾錯）+**結束給評分**（/api/lang/smalltalk/feedback）
- **沉浸（immersion）同此流程**：YouTube/文章 → 摘要/MCQ/抽單字 → 討論(語音/文字) → 評分；YT 片長計入聽力時間
- **YouTube 觀看記錄（2026-06-05）**：immersion 頁兩個動作鈕——「分析並出題」(走 Gemini 多模態) 與「只記錄觀看」(`content/watch`)。後者**純 fetch 不走 AI**：`server/utils/youtube-meta.ts` 用 oEmbed 抓標題 + watch 頁 `lengthSeconds` 抓時長（免 YouTube API key，本機 dev 無 AI key 也能用），記入 `lang_activity`(listening/youtube) + `lang_content`(analysis.watch_only)；抓不到時長則回 422 由前端手動輸入分鐘。頁頂橫幅顯示**今日／本月累積觀看時長 + 累計影片數**（`content/watch-stats`，從 lang_activity source=youtube 聚合）。歷史清單顯示時長與「僅記錄」標記。

## 四、其他功能

> 🎯 **設計原則：英文內容「策展優先」（2026-06-05）**。使用者不滿意 AI 即時生成的浮動品質，故**英文的文法課/學術單字/情境實用句/短文長文範例改為手工策展**（`server/data/enGrammar.ts`/`enVocab.ts`/`enSentences.ts`/`enPassages.ts`），策展內容為可靠核心、**AI 只負責「無限延伸／換一個」**（走 NVIDIA 主→Gemini）。加內容＝改對應 data 檔。其他語言仍走 AI 生成。

- **🔤 字母教學 + 字母測驗（`/coach/[lang]/alphabet`，2026-06-12，僅非英文 6 語）**：使用者要複習各語言字母。**純策展、無 AI、無 DB**——字母資料在 `server/data/alphabets.ts`（每語言一份 `AlphabetSpec`，分 group：de 26字母+變音/ß；fr 26字母+重音連字；ja 平假名清音/濁半濁/拗音+片假名清音；grc 24字母+呼氣重音；la 字母教會式發音+字母組合規則 ae/oe/gn/sc/ti…；hbo 22子音+5字尾形+母音點 niqqud，RTL）。每字 `char/name/sound/example/gloss`。端點 `alphabet`(GET，英文回 available:false)。頁兩模式：**教學**（字母卡格，點🔊用 `coach.ttsLang` 朗讀 example）＋**測驗**（看字母選讀音 / 看讀音選字母 / 混合，4 選 1 即時對答＋計分＋答錯字母回顧；干擾項依答案欄位去重避免兩個正解）。計時走 `useActivityTracker(... 'reading','alphabet')`。首頁學習磚 `v-if="lang!=='en'"`。加/改字母＝改 `alphabets.ts`。
  - **🎤 字母語音搶答（alphabet.vue 第三模式，2026-06-18，ja/grc/la/hbo）**：使用者要「看字母→限時用講的唸出名稱」。看字母→倒數 3/5/8 秒內用 Web Speech STT 唸字母名稱→純函式模糊比對（`heardMatches`：比對 name/sound/char/tts，含 Levenshtein≥0.6、子字串包含）唸對即過。**辨識語系**：古典語名稱皆羅馬轉寫（alpha/aleph…）故用 **en-US** 辨識最穩、ja 用 **ja-JP**（`RECOG` 表）。不支援/唸不出來→「看答案」fallback。零後端零 AI，屬「無 AI 確定性反饋」系列。
- **📕 字典瀏覽頁（`/coach/[lang]/dictionary`，2026-06-18，全 7 語，零 AI）**：使用者要「字庫做成字典，按分級/主題/字母排序」。翻閱共用字庫 `lang_vocab_bank`：四種排序（🔤字母 word.asc／🎯**語意主題** theme／📊分級 level／🗂️頻率分類 category，後三依 freq_rank）＋對應 facet chip 過濾＋單字/釋義搜尋（`or(word.ilike,meaning.ilike)`，去除破壞字元）＋分頁「載入更多」＋🔊TTS。端點 `dictionary`(GET，純 PostgREST filter/order/range/count，零 AI)；facet 走 `vocab_bank_levels`/`vocab_bank_categories`/`vocab_bank_themes` 三 RPC。hbo 自動 RTL。首頁學習區「📕字典」磚。
  - **🎯 語意主題分類（2026-06-18）**：`category` 是頻率帶、非語意；故新增 `theme` 欄＋18 類語意主題（神‧神學／聖經人物‧地名／敬拜‧禮儀／教會‧群體‧教派／罪‧救恩‧倫理／情感‧心智／人‧身體‧家庭／食物‧飲食／自然‧動植物／時間‧節期／空間‧方位／數量‧度量／言語‧文書／行動‧移動／社會‧政治‧律法／工藝‧器物‧建築／性質‧抽象／功能詞）。`scripts/coach_vocab_bank.py theme <lang|all>` 一次性 LLM 批次（100 字/call，依釋義挑唯一主題；`theme is null` 為 reentrant、失敗批次留 null 下次補；可 `--engine haiku`）→ 寫回 `theme` 欄（RPC `set_vocab_themes`）。跑完字典「主題」分頁＝純讀 DB 零 AI。宗教研究取向：宗教字優先歸宗教主題、功能詞獨立一類。
- **🔀 句子重組 / 受限寫作題型（`/coach/[lang]/compose`，2026-06-12，零 AI）**：使用者決策「寫作＝自架 LanguageTool ＋ 受限題型批改 兩個都做」之受限題型這塊。把寫作練習設計成「有標準答案鍵」的題型 → 確定性比對、即時對錯、零外部依賴。首發**句子重組**：看提示→把打散的詞卡點回正確順序→比對詞序。端點 `compose`(GET)；句源 en＝策展情境句 `enSentences`（中譯當提示），grc/hbo＝詞形題庫的經文 `verse_words`（以原文詞序為答案，重組＝重建該節經文，適合熟讀原典；hbo RTL）。頁面 client-side 逐位批改。**句源擴充（2026-06-12）**：de/fr/la 改抓 `lang_vocab_bank.example`（以空白斷詞；提示＝「用到『X（義）』的句子」；la 已有 548 例句、de/fr 待 gloss 補到才有題，頁面 total=0 時顯示「字庫建置中」並停用開始鈕）。**ja 不支援**（日文無詞間空白、空白斷詞失效，需 JP 斷詞器如 TinySegmenter，後續再議）。**可擴充題型**：填空/翻譯比對（後續）。
- **🧩 詞形判析 parsing 自動批改（`/coach/[lang]/parse`，2026-06-12，零 AI；目前 grc）**：使用者要「沒有 AI 也能即時反饋」（API 不穩怕爆）。用 **STEPBible 黃金標註**（TAGNT 希臘文新約 CC-BY）離線把每個字的 morph 碼解成可批改維度，做「看經文中的目標字→逐項判斷格/數/性、時態/語態/語氣/人稱→比對黃金答案」題型。**架構刻意零外部依賴**：① `scripts/parse_bank.py` 純函式 `decode_greek_morph()`（N/A/T→格數性；V→時態語態語氣+人稱數，分詞再加格數性，不定詞無人稱；第二式去數字前綴；異相語態 E/N/D 不出題免爭議）+ `harvest_greek()`（下載 TAGNT→逐字解碼→等距抽樣 1500 題分散全 NT，附經文脈絡 target_idx）→ 輸出**靜態 JSON** `server/data/parseGreek.json`（非 DB、非 API）；② 端點 `parse`(GET 隨機抽 n 題)；③ 頁面 dropdown 選答、**純比對黃金答案 client-side 批改**。測試 `scripts/tests/test_parse_bank.py`（19 passed）。**grc + hbo 皆已上線**：grc 走 TAGNT（格數性／時態語態語氣人稱），hbo 走 TAHOT `decode_hebrew_morph`（morph 如 `HVqp3ms`＝字幹 binyan＋動貌＋人稱性數；名詞性數狀態；只取單一語素內容詞免前綴混淆；RTL）；經文脈絡存 `verse_words` 陣列（非空白 join，避免含空白的字位移）。題庫 `parseGreek.json`/`parseHebrew.json` 各 1500 題分散全卷。**這是「無 AI 確定性反饋」系列第一塊**。使用者決策（2026-06-12）：口說＝**先強化現有 Web Speech shadowing（零服務）**；寫作＝**自架 LanguageTool ＋ 受限題型批改 兩個都做**。
- **分級文法課**（`lang_grammar` PK user+lang+**level**）：日文 N5–N1、古典語 入門/初級/中級/進階 各一套；**Gemini 依程度＋`langLabel` 自動生成**（不需手動 seed）。大綱循序 + 逐課懶生成（解說/例句/練習）+ 完成度。頁 `/coach/[lang]/grammar`。
  - **英文＝手工策展（2026-06-05，不走 AI）**：`server/data/enGrammar.ts` 9 大類 ~43 文法點（時態/語態/語氣/句型/子句/名詞冠詞/動詞/連接詞/介係詞），全策展解說+例句+練習（宗教研究取向）。`grammar/index.get.ts` 偵測 `language==='en'` → 用 `curatedSyllabus(level)`（依 CEFR level 過濾、**content 預嵌**，lesson 端點直接回不走 AI）、保留 done。要加/改文法點就改 `enGrammar.ts`。
  - **古典語 grc/la/hbo ＋ 活語言 de/fr/ja＝手工策展（2026-06-18，不走 AI）**：`server/data/coachGrammar.ts` 六語各 8 課策展文法（de/fr＝A1、ja＝N5/N4：de 三性四格/變位/sein-haben/V2語序/否定/所有/情態；fr 陰陽性冠詞/être-avoir/-er動詞/ne…pas/形容詞/疑問/所有/à·de縮合；ja です句型/助詞/動詞三類ます形/形容詞/指示詞/て形/過去式/數量詞）；古典語各 8 課入門/初級文法（grc：字母呼氣音→冠詞三性→五格→εἰμί→λύω 現在式→介系詞→形容詞一致→aorist；la：教會式發音→變格→sum→變位→形容詞一致→介系詞→屬/與格→完成式；hbo：字母母音點→冠詞名詞→וְ/בְּ前綴→連綴→代名詞詞尾→Qal qatal→Qal yiqtol→waw 敘事），例句取自新約/武加大/BHS，**content 預嵌**。`grammar/index.get.ts`：`CURATED_GRAMMAR_LANGS` 命中且該級別有策展（入門/初級）→ 直接回、零 AI；中級/進階暫無策展 → 落回 AI 生成（混合）。lesson 端點因 content 已嵌→直接回不走 AI（無需改）。加課＝改 `coachGrammar.ts`。
  - **🗺️ 文法地圖 `/coach/en/grammar-map`（限 en）**：分類瀏覽 + 即時關鍵字過濾 + **打字發問**（`grammar/lookup` = 關鍵字比對 + AI 分類到對應 topic id）+ 內嵌策展解說例句 + 深連回文法課（`grammar?open=<id>` 自動展開）。端點 `grammar/map`(GET 地圖資料) / `grammar/lookup`(POST 查詢)。首頁/文法課有入口（限 en）。
- **💬 情境實用句 + 短文/長文範例（英文，2026-06-05）**：頁 `/coach/en/sentences`，頂部「單句／短文／長文」切換，口說/寫作兩用。
  - **單句**：`server/data/enSentences.ts` 9 情境（機場/學校辦事/學術場合/稅務局/醫院/日常辦事/出國留學/國外旅遊/分享想法）×12 = **108 句**（情境繁中／範例英文／中譯／用法提示）。流程：看情境→**先試答**（STT 或寫作）→**看建議解答**（TTS＋中譯＋提示）→🎙️複述比對／✨換類似句／下一句。
  - **短文/長文**：`server/data/enPassages.ts` 6 主題（自我介紹/留學動機/分享想法/旅遊分享/學術發表）× 短文+長文 = **12 篇策展範文**（任務繁中／範文／中譯／重點句型）。流程：看任務→試寫一段→看範文→換一篇/下一篇。
  - 練到底自動用 AI（`sentences/more`：kind=sentence 或 passage+length，NVIDIA 主）補更多 → 寫作口說**無限練**。端點 `sentences`(index GET 句庫+範文 / more POST AI 延伸)。要加內容改 `enSentences.ts`/`enPassages.ts`。首頁入口（限 en），與文法課/情境角色交叉連結。
- **主題教程**（`lang_courses`）：可選預設或自建主題（宗教文獻精讀/學術寫作/TOEFL口說/敬語/宗教神話日語…），生成循序課表，**每課標預估分鐘**，逐課懶生成 + 進度條。頁 `/coach/[lang]/courses`；端點 courses(index/create/[id]/lesson/done)。
- **單字 SRS**（`lang_vocab`，**FSRS v4.5**，`server/utils/srs.ts`，2026-06-05 由 SM-2 改）：`fsrs()` 用 difficulty/stability/retrievability 三參數（`lang_vocab` 加 `difficulty`/`stability` 欄位），依距上次複習天數算 R；同記憶率複習量少 ~20-30%、答錯不再反覆轟炸。`review.post` 已改用 fsrs；`sm2()` 保留不刪。review **三模式**：翻卡／選擇題／**克漏字**（看中文+挖空例句→打單字，對=good 錯=again；不自動朗讀免洩答案）。不足時從整庫補未精熟字；`vocab/generate` 依**目前程度**生成主題詞組——**非初學者採「程度下限」策略**：挑符合或略高於目前程度的字，**嚴格排除低於該程度的基礎／日常常見字**（英文 B2 就不出 heartbeat/happy 這類 A1–B1 早已熟悉的字，寧難勿易；初學者 A1/A2/N5/入門 仍給基礎高頻字）。既有的太簡單卡片不批次刪（使用者要保留自己拼錯／想練的字），靠評「簡單」拉長間隔自然淡出。
  - **英文預設主題＝手工策展單字（2026-06-05，不走 AI）**：`server/data/enVocab.ts` 7 預設主題（AWL/GRE/哲學/歷史/神學/文學批評/學術寫作連接詞）×15 = 105 個 B2+ 學術字（宗教研究取向，繁中釋義+例句+詞性）。`vocab/generate` 偵測 `en` + 策展主題 → 直接 upsert 策展字（**零延遲、永遠有題**），自訂主題才走 AI（NVIDIA 主→Gemini）。`review.vue` 無限模式 `THEME_POOLS.en.auto` 已改成**全策展主題** → 不再卡 AI（修無限模式不出題）。已預先 seed 105 字進站長單字庫。
  - **♾️ 無限刷題模式（預設開，2026-06-04）**：`review.vue` 右上開關。佇列剩 ≤4 張就背景用 `vocab/generate` 生一批新學術單字（英文走策展、零成本秒回；其他語言走 NVIDIA）接到佇列尾，預抓藏延遲、本 session 去重，永不停。主題池 `THEME_POOLS` **依語言**：英文走 AWL/GRE/學術；**德文（de）／法文（fr）走 A1 高頻字＋日常生活（家庭/食物/城市/數字/問候…），名詞連冠詞，後段才帶教堂節慶與宗教/神學基礎詞**；日文走 N5/N4 基礎・日常・神社祭典等初學主題（別給日文出英文考試詞）；**希臘文（grc）走 新約高頻字／約翰福音／LXX／信經術語／教父／斐羅／拜占庭**；**拉丁文（la）走 武加大／福音書／信經禮儀／拉丁教父／經院術語（ens·esse·essentia）／教會法／中世紀各學科**；**希伯來文（hbo）走 舊約高頻字／創世記出埃及記／詩篇／binyanim 動詞／三母音字根／昆蘭／拉比／中世紀註釋** 等入門題材。`TTS_LANG` 也要補對應 BCP-47（de=`de-DE`、fr=`fr-FR`、grc=`el-GR`、la=`it-IT` 教會式、hbo=`he-IL`），否則 🔊 會用英文聲念。⚠️ **同一份 `TTS`/`TTS_LANG` 語系對照表散落在多個頁面**（`review.vue`/`practice.vue`/`immersion.vue`/`smalltalk.vue`/`grammar.vue`/`today.vue`/`courses.vue`，其中 immersion/practice 另有 `LANG_LABEL`），**新增活語言時 7 個檔都要補齊**（活語言若漏補會用英文聲念外語，2026-06-04 已全數補上 de/fr）。測過或沒過的卡都進 `lang_vocab`（generate upsert + review 記 SRS），各語言獨立列表。
  - **📚 共用預備字庫 `lang_vocab_bank`（2026-06-12，全語言）**：解決「只有英文有預備字庫、其他語言只能即時生成 → AI 一過載就斷糧」（使用者遇到的 grc 生成失敗）。共用表（非 per-user，RLS 已登入可讀、service role 寫）每語言一份**權威頻率/語料庫 + LLM 補繁中釋義+例句+詞性**的策展字庫，依頻率分類帶。
    - **來源**（皆免費/公有領域/CC-BY，腳本自動下載解析）：en/de/fr＝FrequencyWords（OpenSubtitles 頻率，取前 N，分 A1→C2 帶）；ja＝jlpt-vocab-api（N5–N1，每級一類，附 furigana/romaji/EN 義）；**grc＝STEPBible TAGNT**（新約 5,400 詞元，含英義/詞性/書卷，分新約頻率帶）；**hbo＝STEPBible TAHOT**（舊約 7,537 詞元）；**la＝Clementine Vulgate**（表面詞頻 → LLM 還原詞元，分武加大頻率帶）。目標：en 30k／de·fr·la 6k／ja ~9k／grc·hbo 整部語料窮盡。
    - **腳本 `scripts/coach_vocab_bank.py`**：`harvest <lang|all>`（下載+解析→`C:/tmp/vocab_bank/<lang>.candidates.jsonl`）／`gloss <lang|all> [--limit N]`（逐批 LLM 補繁中→upsert，**每批 flush 進 DB 與 ledger 同步、可重入**）／`run`／`status`。引擎 **NVIDIA deepseek-v4-flash 主→Gemini→Haiku**（6.6 萬條會燒爆 Gemini 免費日限，正是過載主因）；批量 40 字/call、~30s/call。`gloss all` 順序＝grc,hbo,la,ja,de,fr,en（古典/被卡語言先跑，英文最大擺最後）。**c:/tmp ledger 別清**（[[feedback_tmp_cleanup]] 例外）。
      - **⚡ NVIDIA 2-strike + 90s 逾時 + Haiku 快速救急（2026-06-12 修；llm_json）**：原本 `nvidia_chat` 內建 **10 分鐘** deadline，NVIDIA 連線一卡死（ReadTimeout/ConnError）整批苦等 10 分、整個 run 凍結要手動重啟。修正：① `nvidia_chat` 加 `deadline_s` 參數，bank 端傳 **90s**（逾時即換引擎，不再苦等）；② `llm_json` 加 **NVIDIA 2-strike**——連續 2 批 NVIDIA 失敗就**暫停 NVIDIA 15 分**、直接走 Gemini→Haiku（log 印「↳ NVIDIA 連續 2 次失敗 — 暫停 15 分」），冷卻後再探、成功即重置。NVIDIA 退場後走 **Haiku 直送可達 ~400 字/分**（使用者訂 Claude Max，Haiku 為可靠後盾，見 [[feedback_nvidia_engine_haiku_retired]]）。`_haiku_json` 走 `T._anthropic_client`（Max OAuth）。NVIDIA 正常時仍優先用它（免費無上限）。
    - **後端優先抽字庫（全語言）**：`vocab/generate` 在英文策展之後、AI 之前插一段「先 `pick_vocab_bank`（隨機抽使用者尚未擁有的字；主題符合某分類就限定該類，否則跨類補題）→ 有就 upsert 進 `lang_vocab` 回傳 `bank:true`，AI 只當最後手段」。新增 RPC `pick_vocab_bank`/`vocab_bank_categories` + 端點 `vocab/categories`。**∴ 無限模式/手動生成全語言永遠有題、AI 全掛也不斷糧**。
    - **複習頁分類 chip 每天輪替（2026-06-12）**：`review.vue` 開頁 `loadBankCats()` 抓該語言真實字庫分類，`PRESETS` 改成「有字庫→`rotateDaily(8)`（台北日期種子、同天穩定隔天換）／無→fallback 內建 `THEME_POOLS.presets`」；無限模式 `auto` 主題也優先用字庫分類。
    - **✅ 全 7 語 gloss 完成（2026-06-18）**：en 30000／de 6000／fr 6000／ja 8101（候選 8385 餘為重複表面詞，無缺工）／grc 5400／hbo 7537／la 6011 — 每字皆有繁中釋義＋詞性＋例句，全語言 SRS／點讀／無限刷題不再靠即時 AI、永遠有題。**收尾關鍵**：en 最後 ~5000 字 NVIDIA/Gemini 免費額度耗盡，改 `gloss en --engine haiku` 用 Claude Max 跑完；同時修好 `_haiku_json`（補 401 token 輪替重讀＋429 等待＋連線瞬斷重試，原本只要 token 一輪替或連線瞬斷整批就被跳過）。要重補或加字時可 `--engine haiku` 直攻、不必苦等其他引擎。
    - **▶ 監督續傳（gloss 仍在跑時用）**：背景任務跑 `python scripts/coach_vocab_bank.py gloss all`（順序 grc→hbo→la→ja→de→fr→en），log 在 `C:/tmp/vocab_bank/overnight.log`。
      - **監督**：`python scripts/coach_vocab_bank.py status`（看各語言 candidates / ledger / DB / 已補釋義 計數）＋ `tail C:/tmp/vocab_bank/overnight.log`。確認 process 還活著：`Get-CimInstance Win32_Process | ? { $_.Name -eq 'python.exe' -and $_.CommandLine -like '*coach_vocab*' }`。
      - **目標數**：en 30000／de·fr 6000／ja ~8385／grc 5400／hbo 7537／la 6000（詞元，從 15000 表面去重）。**已完成判定**：某語言 `DB glossed ≈ 目標` 即該語言完成。
      - **續傳/重跑**：腳本可重入（ledger 在 `C:/tmp/vocab_bank/<lang>.glossed.jsonl`，重跑自動略過已完成詞，flush-every-batch 保證 ledger=DB 不留孤兒）。**中斷後**直接再跑 `gloss all` 或單語 `gloss <lang>` 即接續。**全引擎失敗被跳過的 batch（log 出現「! batch N 全引擎失敗」，通常 NVIDIA 連線瞬斷）不會寫 ledger** → 全跑完後**再跑一次 `gloss all` 補做跳過的批次**（第二遍只剩零星未補字、很快）。`C:/tmp` ledger 別清。
      - **若要重啟整個背景任務**：先確認沒有別人的程序（[[feedback_no_kill_other_tasks]]），只停自己的 `coach_vocab*` python，再 `python scripts/coach_vocab_bank.py gloss all`（建議用背景執行）。
      - **🛠️ 手動輔助腳本（2026-06-15，未掛排程）**：`scripts/coach_vocab_secondpass.ps1`（守門：有 gloss 在跑就跳過＋可重入 gloss all，補第一輪被跳過的 batch）與 `scripts/coach_vocab_relaunch_loop.ps1`（崩潰自動重啟 gloss all 直到 en 達標，對抗 OS 執行緒耗盡）皆**供手動執行用、不註冊 Windows 排程**——gloss 整夜 run 由站長自己的 session 起跑（多 session 同跑會搶同一份免費 API 額度＝Gemini 日限被燒爆、彼此拖累，故勿自行另起 gloss）。⚠️ 整夜 run 是「父啟動器＋子工作程序」父子鏈（父程序 CPU≈0 只掛著等），別誤當兩份重複而去停父程序，會連帶殺掉真正在跑的子程序；也別停別的 session 的 python（[[feedback_no_kill_other_tasks]]）。
- **📖 點讀閱讀器（`/coach/[lang]/reader`，2026-06-05，全語言）**：貼任意外語文字→逐字可點，點詞用 NVIDIA/Gemini 在「該句脈絡」給釋義+原形+例句（`words/define`）；標「學習中」自動把原形(含原句)加入 `lang_vocab` 進 FSRS、標「已知」著灰，狀態存 `lang_word_status`（`words/status` GET+POST）、下次遇到自動著色。LingQ 式可理解輸入，適合讀原典/論文。
- **🗣️ 發音跟讀 shadowing（`/coach/[lang]/shadowing`，全語言）**：目標句（en 可隨機抽策展句）→🔊聽範例/🐢慢速→🎤跟讀 STT→逐詞比對著色+吻合%；🧑‍🏫 AI 點評（`pronunciation` 端點，可選）。
  - **🔧 零服務確定性評分強化（2026-06-12）**：使用者要「API 不穩也能即時反饋」→ 把原本二元 LCS（綠=唸到/紅=漏）升級成 `composables/usePronunciationScore.ts` 純函式 `scorePronunciation()`：**詞級編輯距離對齊 + 回溯**，每個目標詞判 **hit(唸對)/near(近似，附「聽成 X」)/miss(漏或錯)**，near 用 Levenshtein 相似度≥0.6 判定並給半分；插入的多餘辨識詞不扣分；標點不計分；跨語言（拉丁/希臘/希伯來/假名）走 Unicode 字母正規化。頁面三色著色 + 「✅唸對/🟡近似/❌漏錯」統計列。**完全不呼叫任何 AI/雲端**。測試 `test/coach/pronunciation-score.spec.ts`（10 passed）。AI 點評仍保留為可選。屬「無 AI 確定性反饋」系列。
- **✍️ 寫作批改（`/coach/[lang]/writing`，全語言）**：寫一段→**逐句 inline 批改**（原句刪除線/修正後綠字/為何錯）+整體點評+評分+潤飾版 TTS（`writing/correct` 端點，NVIDIA 主）。
  - **🔍 LanguageTool 規則式文法檢查（零 AI，2026-06-12）**：寫作頁多一顆「文法檢查（零 AI）」按鈕，與 AI 逐句批改並存。走 `grammar-check` 端點代理到**自架 LanguageTool**（開源、上千條規則、無 LLM、穩定無額度 → 使用者「怕 API 爆」的解）。回傳每處 match（錯字片段／建議替換／規則說明），頁面 inline 顯示。只支援現代活語言（en/de/fr/es/it/ja…，`LT_LANGS`）；古典語不支援（用詞形判析／經文重組）。**需 env `LANGUAGETOOL_URL`**（Zeabur 加一個 `erikvl87/languagetool` Docker 服務，填內網 URL）；未設則按鈕回明確提示、不報錯。`level=picky`。屬「無 AI 確定性反饋」系列，與 [[feedback_engine_nvidia_no_haiku]] 的 AI 批改互補。
- **技能練習/考試**（`lang_tasks`）：`task/generate`（TOEFL/IELTS/GRE + 一般，聽說讀寫 + 翻譯）/ `task/[id]/answer`（選擇題自動批改、寫說/翻譯用 Gemini rubric 評分）。
- **記憶/簡報/日誌**：`lang_memory`（跨 session 長期了解 + highlights 強弱項，注入對話）；`briefing`（今日簡報，每日快取）；`lang_journal`（教練每日日誌，日曆點閱）。
- **難度依「目前程度」非目標**：生成都讀 `lang_progress.level`；量表 `coach.levelScale`（CEFR / JLPT / 入門初中進）；`progress.put` 設目前程度。

## 五、資安（鎖回站長專屬）

- **登入 = Email OTP 6 碼**（login.vue：signInWithOtp→verifyOtp，shouldCreateUser:false）。⚠️ **Supabase Email Template「Magic Link」必須含 `{{ .Token }}`** 否則收不到碼。
- **裝置核准閘門已於 2026-06-03 移除**（單人私站、登入已靠 email OTP + allowedEmail 白名單，多一層只會把站長自己鎖在外）。`trusted_devices` 表保留但不再使用；middleware/頁面/API 皆已刪。
- **付費 key 僅站長**（coach-ai `isOwner` 比對 allowedEmail）；coach-auth 站長專屬；`/signup` 關閉。
- **付費每月上限 NT$500**（env `GEMINI_PAID_MONTHLY_CAP_TWD`）：超過自動退免費；儀表板顯示+警示。

## 六、模型與 key（成本）

- **🔑 線上／線下 key 分離（2026-06-04）**：線上各 AI 功能（coach 全部、族譜解析、YouTube 沉浸）**只讀「線上專用」key** `NVIDIA_API_Key_OLINE_ONLY` / `Gemini_API_Key_OLINE_ONLY`（拼字 OLINE 為既定變數名，**僅在 Zeabur 設定**）。`nuxt.config.ts` 的 `nvidiaApiKeys`/`geminiApiKeys`/`geminiApiKey` 三者皆改成只讀 `_OLINE_ONLY`。本機 `.env` 刻意**不放**這兩支，`_1..4` 共享池完全留給線下批次腳本（OCR/translate/dialogues）→ 線上線下額度徹底分離。⚠️ 三支 `dialogue_*.py` 用 `startswith('NVIDIA_API_KEY')` 前綴比對撈 key，所以 `_OLINE_ONLY` 一旦留在本機 `.env` 會被當第 5 把 key 輪進去燒掉線上額度——故必須從本機移除，不能只靠命名。⚠️ 線上為「專用」模式＝**無 `_1..4` fallback**，`_OLINE_ONLY` 失效則線上 AI 全斷；換 key 或要加保險絲時改 `nuxt.config.ts`。
  - **本機 dev fallback（2026-06-05）**：`nuxt.config.ts` 改為「OLINE key 存在用 OLINE，**不存在才退到 `_1..4` 池**」。因 Zeabur 沒設 `_1..4`，線上仍只讀 OLINE（分離政策不變）；本機 dev 沒 OLINE → 自動用 `_1..4`，coach 生成/聊天/沉浸在 localhost 也能測（之前本機跑會報「尚未設定 Gemini key」就是因為兩池皆空）。
- **主引擎＝NVIDIA NIM（2026-06-03 起）**：`server/utils/nvidia.ts` `callNvidiaFull`（OpenAI 相容、key 輪替、剝 `<think>`）。`coach-ai.ts` `coachGemini` 先試 NVIDIA → 失敗才落 Gemini。env `nvidiaApiKeys`=線上專用 `NVIDIA_API_Key_OLINE_ONLY`（見上「線上／線下 key 分離」；全部不可用才落 Gemini）、`nvidiaModel` 預設 **`qwen/qwen3-next-80b-a3b-instruct`**（繁中佳、支援 JSON、穩定）。無限量、零成本，用量記 tier=`nvidia`。
  - ⚠️ **不要改回 `deepseek-ai/deepseek-v4-flash`**：該模型在 NVIDIA 免費層長期 429（互動式教練不可靠）；deepseek 只適合 translate 腳本那種可退避重試的批次。其餘 NVIDIA 模型（qwen3-next、llama-3.1）正常 200。
  - **fileData（YouTube 等多模態 part）NVIDIA 不支援** → `coachGemini` 偵測到自動跳過走 Gemini。**∴ YouTube 沉浸一定要有 Gemini key**；缺 key 時 `content/ingest` 回明確訊息（含「伺服器偵測到 N 把 Gemini key」），並提示可改「貼上文章」（純文字走 NVIDIA）。
- **Fallback＝Gemini**：`server/utils/gemini.ts`（callGemini/callGeminiFull + key 輪替 + usageMetadata）；`coach-ai.ts` `coachGemini`（tier 選 key + owner/budget 守門 + 用量寫 `lang_api_usage`）。
- 預設模型 **`gemini-flash-latest`**（固定 ID 2.5-flash 免費日限 20 太低；alias 配額桶分開）。env `GEMINI_MODEL`/`GEMINI_GRADE_MODEL` 可覆寫。
- **Gemini key 命名容錯（2026-06-04）**：`nuxt.config` 的 `geminiApiKeys`/`geminiApiKey` 同時接受 `Gemini_API_Key_OLINE_ONLY` 與全大寫 `GEMINI_API_KEY_OLINE_ONLY`（Zeabur 變數區分大小寫，打錯就讀不到 → YouTube 誤報缺 key）。付費層已停用（`GEMINI_COACH_PAID_KEY` 移除），現役＝線上專用 `NVIDIA_API_Key_OLINE_ONLY` 主 + `Gemini_API_Key_OLINE_ONLY` fallback（皆僅 Zeabur）。
- 雙 key env：`GEMINI_COACH_FREE_KEY`（空則 fallback `Gemini_API_Key_*` 池）/ `GEMINI_COACH_PAID_KEY`。Gemini 免費用完→前端 `useCoachAi.aiFetch` 跳確認→切付費重試（NVIDIA 為主後此路徑幾乎不觸發）。
- 前端 AI 呼叫一律走 `useCoachAi().aiFetch`（自動帶 usePaid + free_exhausted 處理）。⚠️ **`aiFetch` 對 GET/HEAD 不能塞 body**（瀏覽器會丟 "Request with GET/HEAD method cannot have body" → 頁面整個拿不到資料，例如文法課曾全空白）。已修：`aiFetch` 偵測 method，GET/HEAD 把 `usePaid` 放 **query string**、其餘方法才放 body。新增「用 aiFetch 打 GET 的端點」務必從 query 讀 usePaid（多數 GET 端點根本不需要 usePaid，直接用 `authedFetch` 更乾淨）。

## 六之二、時區・計時器・日曆（2026-06-04）

- **時區一律 Asia/Taipei**：Zeabur 跑 UTC，原本 `new Date().toISOString().slice(0,10)` 會把台灣凌晨算成昨天 → streak/今日時間/日曆/到期單字全錯一天。新增 `server/utils/today.ts`（`tzToday`/`tzMonth`/`tzDaysAgo`，寫死台北），**所有「今天」日期計算都改用它**（dashboard/activity/daily/journal/briefing/chat/task/vocab/ingest…）；`srs.ts` next_review 也台北。前端日曆與月份改用 `toLocaleDateString("en-CA")`（瀏覽器本地＝台北）對齊。⚠️ 新增任何用到「今天」的端點都要用 `today.ts`，別再寫 `toISOString().slice(0,10)`。
- **計時器**：`components/CoachTimer.vue`（吃 `useActivityTracker().activeSeconds`，⏱ mm:ss，分頁切走暫停）。chat/smalltalk/review/practice/immersion + **courses/grammar/grammar-map（2026-06-05 補）** 皆有。從進頁開始算，flush 進 `lang_activity`（review/grammar/courses→reading、practice→當前 skill、chat→speaking、immersion→listening）。**immersion onMounted 就起計時** → 只記錄觀看後的作答/討論時間也算入聽力。
  - ⚠️ **連續計時（2026-06-05 修）**：`useActivityTracker` 把「顯示累計秒數 `activeSeconds`（單調遞增、永不歸零）」與「送 server 的增量」分開——flush 只送 `activeSeconds - sentSeconds`、成功才推進 `sentSeconds`（失敗重送不重複計）。**別再讓 flush 把 activeSeconds 歸零**（會害計時器每 30/60 秒跳回 0、看似一直重新計）。離開頁面/切分頁用 `fetch(keepalive:true)` beacon 帶 Bearer header 送殘餘增量（authedFetch 是 header 認證，不能用 sendBeacon）。
- ⚠️ **NVIDIA 逾時保護（2026-06-05）**：`server/utils/nvidia.ts` fetch 加 AbortController 逾時（`nvidiaTimeoutMs` 預設 14s），超時 abort → 落 Gemini fallback，避免 Zeabur gateway 先回 **502 Bad Gateway**（聊天卡住連帶 activity 也 502）。⚠️ 若線上「總是」走 Gemini 並 429：八成是 **Zeabur 沒設 `NVIDIA_API_Key_OLINE_ONLY`** → NVIDIA 池空 → 每次跳過 NVIDIA 走 Gemini（key 本身測過 200/407ms 有效）。
- **日曆標今天**：語言首頁日曆今天格加 ring + 「今」徽章，標題顯示「今天 X月X日（週X）」。

## 七、DB 表（Supabase，全 RLS 依 user_id）

`lang_profile`/`lang_progress`/`lang_sessions`(persona/mode/topic/duration/feedback)/`lang_messages`/`lang_vocab`(FSRS：difficulty/stability)/`lang_vocab_bank`(共用預備字庫·非per-user·category/freq_rank/glossed)/`lang_word_status`(known/learning 著色)/`lang_homework`/`lang_activity`/`lang_level_history`/`lang_api_usage`(+bump_lang_usage RPC)/`lang_memory`(memory/highlights/briefing/briefing_date)/`lang_journal`/`lang_word_lists`/`lang_tasks`/`lang_content`/`lang_grammar`/`lang_daily`/`trusted_devices`。migration SQL 在 `database/coach-language-*.sql` 等，用 Supabase Management API 套用。

## 八、端點（`server/api/lang/*` + `server/api/devices/*`）

chat / profile(get,put) / progress(get,put) / activity / dashboard / usage / assess / briefing / memory(get,regenerate) / journal(get, generate) / sessions / messages / coaches / vocab(index,generate,**categories**,review get/post,[id] patch/delete) / homework / task(generate, [id]/answer) / smalltalk(start, feedback) / content(ingest, watch, index, watch-stats) / grammar(index, lesson, done, **map, lookup**) / **alphabet** / **parse** / **compose** / daily(get, item, done) / devices(check, index, [id] patch) / **words(define, status get/post)** / **pronunciation** / **sentences(index, more)** / **writing(correct)** / **grammar-check**（LanguageTool 規則式，零 AI）。

## 九、加語言 / 擴充

- 加語言 = `server/utils/lang-coaches.ts` 加一筆 `Coach`（language/levelScale/defaultLevel/name/langLabel/bcp47/ttsLang/accent/blurb/systemPrompt + personas/scenarios/smalltalkTopics/qaTopics），設 `enabled:true`。**前後端自動支援**：選單、首頁、chat、文法、單字、今日推薦全靠這筆資料驅動。文法課 `grammar/index.get.ts` 已泛用（`入門/初級` 自動視為初學者，依 `langLabel` 生成，不用 seed）。
- 各語言定向／題材／鍵盤／voiceless／TTS 一覽見上方「〇、語言一覽」；**古語言定向勿改回古典/現代**。新增語言別忘了同步補 `review.vue` 的 `THEME_POOLS` 與 `TTS_LANG`（見 §四）。
- **轉寫鍵盤（`keyboard` 欄位，目前 `"greek"` / `"kana"` / `"hebrew"`）**：打英文/羅馬字即時轉成目標文字。`chat.vue` 偵測 `coach.keyboard` 顯示「⌨️ 鍵盤」開關＋對照表面板，綁 textarea `@keydown`（`onInputKeydown` 依 keyboard 分派 greek/kana/hebrew；Enter 前先 `kana.finalize` 收殘留 ん）。訊息泡泡加 `dir="auto"`、希伯來輸入框 `dir="rtl"`。
  - **希臘文 `composables/useGreekKeyboard.ts`**：TLG **Beta Code**（h=η q=θ c=ξ x=χ y=ψ w=ω f=φ）；母音後按 `) ( / \ = | +` 加多調符號 polytonic；字尾 σ→ς + NFC。1:1 無狀態。grc 教練用。
  - **日文 `composables/useKanaKeyboard.ts`**：romaji→かな 迷你 IME，**有狀態**（`pendingLen` 暫存游標前未成假名的羅馬字，湊成即替換）。拗音(kya)、促音(雙子音→っ、tch)、撥音(nn→ん／n+子音→ん、`'` 分隔)、濁半濁、平/片切換(`kata` ref，+0x60)、片假名長音 `-`→ー。⚠️ 偵測 `e.isComposing`/`key==='Process'` 自動讓行，**不與系統 IME 衝突**。ja 教練用。
  - **希伯來文 `composables/useHebrewKeyboard.ts`**：22 子音單鍵（學術轉寫，1:1），字尾形 sofit 自動（כ→ך מ→ם נ→ן פ→ף צ→ץ，詞尾換／詞中還原，類比希臘字尾 σ），母音點 niqqud 走點選面板。**RTL**（輸入框 dir=rtl、字串/游標仍邏輯順序）。hbo 教練用。
  - 純函式有單元測試 `test/coach/keyboard.spec.ts`（`romajiToKana` / `normalizeSigma` / `normalizeFinals`）。要再加古語言鍵盤（科普特、敘利亞文…）就照 useGreekKeyboard 模式擴充 + coach 設 `keyboard`。

## 十、使用者要手動做（部署前）

1. **Supabase Auth → Email Templates → Magic Link 加 `{{ .Token }}`**（最關鍵，否則驗證碼收不到）
2. Supabase Auth 關「Allow new signups」；建議設自訂 SMTP（預設寄信額度低）
3. **Zeabur Variables（線上專用，本機 .env 不放）**：`NVIDIA_API_Key_OLINE_ONLY`（主引擎，無限量）+ `Gemini_API_Key_OLINE_ONLY`（fallback；**YouTube 沉浸必須**，否則只能用貼上文章）。⚠️ 變數名稱**區分大小寫**，現支援 `Gemini_API_Key_OLINE_ONLY` 或全大寫 `GEMINI_API_KEY_OLINE_ONLY` 兩種拼法。`_1..4` 為線下批次腳本專用、不需放 Zeabur。付費 key 已棄用。
4. **（可選）自架 LanguageTool（寫作文法檢查，零 AI）**：Zeabur 新增一個服務，Docker image `erikvl87/languagetool`（埠 8010，建議設 `Java_Xmx=512m`），部署後把它的內網 URL（如 `http://languagetool.zeabur.internal:8010`）填到變數 `LANGUAGETOOL_URL`。沒設也不影響其他功能，只是寫作頁的「文法檢查」按鈕會提示未啟用。本機測試：`docker run -d -p 8010:8010 erikvl87/languagetool` 後設 `LANGUAGETOOL_URL=http://localhost:8010`。

## 待辦（次要）

Live2D、雲端 TTS、速率限制、MFA、用量異常 email 通知、%C2 換真實 C2 wordlist。

**功能藍圖（2026-06-05 競品調查後，已做打✓）**：
- ✓ FSRS 取代 SM-2、✓ 點讀閱讀器（known/learning 著色+建卡）、✓ 發音跟讀 shadowing、✓ 克漏字 cloze、✓ 寫作逐句批改、✓ 英文內容策展化。
- ☐ **影片字幕逐句精讀**（YouTube 抓字幕逐句切→逐句播放+點字查+跟讀+存句；目前只記觀看時長）。
- ☐ **語塊/搭配詞（collocation）學習**（寫作批改/沉浸抽詞時一併抽固定搭配，獨立成一類詞庫；研究者寫作很需要）。
- ☐ **沉浸抽單字→自動進 SRS**（目前抽完是斷點，沒形成「讀→抽→複習」閉環；可仿點讀閱讀器把抽到的詞含原句進 FSRS）。
- ☐ **儀表板加「已知字成長曲線」**（用 `lang_word_status` known 計數，對長期讀原典超有感）。
- ☐ **今日計畫納入 shadowing 與 cloze**（5 口說可指定 shadowing 句；新增每日 cloze 量）。
