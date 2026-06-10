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
- `/coach/[lang]/grammar` = 分級文法課
- `/coach/[lang]/practice` = 技能練習 / 考試模擬 / 翻譯遊戲
- `/coach/[lang]/review` = 單字 SRS（翻卡 / 選擇題）
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
- 每項可**口說/打字討論**（/api/lang/chat 即時糾錯）+**結束給評分**（/api/lang/smalltalk/feedback）
- **沉浸（immersion）同此流程**：YouTube/文章 → 摘要/MCQ/抽單字 → 討論(語音/文字) → 評分；YT 片長計入聽力時間
- **YouTube 觀看記錄（2026-06-05）**：immersion 頁兩個動作鈕——「分析並出題」(走 Gemini 多模態) 與「只記錄觀看」(`content/watch`)。後者**純 fetch 不走 AI**：`server/utils/youtube-meta.ts` 用 oEmbed 抓標題 + watch 頁 `lengthSeconds` 抓時長（免 YouTube API key，本機 dev 無 AI key 也能用），記入 `lang_activity`(listening/youtube) + `lang_content`(analysis.watch_only)；抓不到時長則回 422 由前端手動輸入分鐘。頁頂橫幅顯示**今日／本月累積觀看時長 + 累計影片數**（`content/watch-stats`，從 lang_activity source=youtube 聚合）。歷史清單顯示時長與「僅記錄」標記。

## 四、其他功能

- **分級文法課**（`lang_grammar` PK user+lang+**level**）：日文 N5–N1、古典語 入門/初級/中級/進階 各一套；**Gemini 依程度＋`langLabel` 自動生成**（不需手動 seed）。大綱循序 + 逐課懶生成（解說/例句/練習）+ 完成度。頁 `/coach/[lang]/grammar`。
  - **英文＝手工策展（2026-06-05，不走 AI）**：`server/data/enGrammar.ts` 9 大類 ~43 文法點（時態/語態/語氣/句型/子句/名詞冠詞/動詞/連接詞/介係詞），全策展解說+例句+練習（宗教研究取向）。`grammar/index.get.ts` 偵測 `language==='en'` → 用 `curatedSyllabus(level)`（依 CEFR level 過濾、**content 預嵌**，lesson 端點直接回不走 AI）、保留 done。要加/改文法點就改 `enGrammar.ts`。
  - **🗺️ 文法地圖 `/coach/en/grammar-map`（限 en）**：分類瀏覽 + 即時關鍵字過濾 + **打字發問**（`grammar/lookup` = 關鍵字比對 + AI 分類到對應 topic id）+ 內嵌策展解說例句 + 深連回文法課（`grammar?open=<id>` 自動展開）。端點 `grammar/map`(GET 地圖資料) / `grammar/lookup`(POST 查詢)。首頁/文法課有入口（限 en）。
- **💬 情境實用句 + 短文/長文範例（英文，2026-06-05）**：頁 `/coach/en/sentences`，頂部「單句／短文／長文」切換，口說/寫作兩用。
  - **單句**：`server/data/enSentences.ts` 9 情境（機場/學校辦事/學術場合/稅務局/醫院/日常辦事/出國留學/國外旅遊/分享想法）×12 = **108 句**（情境繁中／範例英文／中譯／用法提示）。流程：看情境→**先試答**（STT 或寫作）→**看建議解答**（TTS＋中譯＋提示）→🎙️複述比對／✨換類似句／下一句。
  - **短文/長文**：`server/data/enPassages.ts` 6 主題（自我介紹/留學動機/分享想法/旅遊分享/學術發表）× 短文+長文 = **12 篇策展範文**（任務繁中／範文／中譯／重點句型）。流程：看任務→試寫一段→看範文→換一篇/下一篇。
  - 練到底自動用 AI（`sentences/more`：kind=sentence 或 passage+length，NVIDIA 主）補更多 → 寫作口說**無限練**。端點 `sentences`(index GET 句庫+範文 / more POST AI 延伸)。要加內容改 `enSentences.ts`/`enPassages.ts`。首頁入口（限 en），與文法課/情境角色交叉連結。
- **主題教程**（`lang_courses`）：可選預設或自建主題（宗教文獻精讀/學術寫作/TOEFL口說/敬語/宗教神話日語…），生成循序課表，**每課標預估分鐘**，逐課懶生成 + 進度條。頁 `/coach/[lang]/courses`；端點 courses(index/create/[id]/lesson/done)。
- **單字 SRS**（`lang_vocab`，SM-2，`server/utils/srs.ts`）：到期佇列；review 預設選擇題（對=good 錯=again→複習）；不足時從整庫補未精熟字；`vocab/generate` 依**目前程度**生成主題詞組——**非初學者採「程度下限」策略**：挑符合或略高於目前程度的字，**嚴格排除低於該程度的基礎／日常常見字**（英文 B2 就不出 heartbeat/happy 這類 A1–B1 早已熟悉的字，寧難勿易；初學者 A1/A2/N5/入門 仍給基礎高頻字）。既有的太簡單卡片不批次刪（使用者要保留自己拼錯／想練的字），靠評「簡單」拉長間隔自然淡出。
  - **英文預設主題＝手工策展單字（2026-06-05，不走 AI）**：`server/data/enVocab.ts` 7 預設主題（AWL/GRE/哲學/歷史/神學/文學批評/學術寫作連接詞）×15 = 105 個 B2+ 學術字（宗教研究取向，繁中釋義+例句+詞性）。`vocab/generate` 偵測 `en` + 策展主題 → 直接 upsert 策展字（**零延遲、永遠有題**），自訂主題才走 AI（NVIDIA 主→Gemini）。`review.vue` 無限模式 `THEME_POOLS.en.auto` 已改成**全策展主題** → 不再卡 AI（修無限模式不出題）。已預先 seed 105 字進站長單字庫。
  - **♾️ 無限刷題模式（預設開，2026-06-04）**：`review.vue` 右上開關。佇列剩 ≤4 張就背景用 `vocab/generate` 生一批新學術單字（英文走策展、零成本秒回；其他語言走 NVIDIA）接到佇列尾，預抓藏延遲、本 session 去重，永不停。主題池 `THEME_POOLS` **依語言**：英文走 AWL/GRE/學術；**德文（de）／法文（fr）走 A1 高頻字＋日常生活（家庭/食物/城市/數字/問候…），名詞連冠詞，後段才帶教堂節慶與宗教/神學基礎詞**；日文走 N5/N4 基礎・日常・神社祭典等初學主題（別給日文出英文考試詞）；**希臘文（grc）走 新約高頻字／約翰福音／LXX／信經術語／教父／斐羅／拜占庭**；**拉丁文（la）走 武加大／福音書／信經禮儀／拉丁教父／經院術語（ens·esse·essentia）／教會法／中世紀各學科**；**希伯來文（hbo）走 舊約高頻字／創世記出埃及記／詩篇／binyanim 動詞／三母音字根／昆蘭／拉比／中世紀註釋** 等入門題材。`TTS_LANG` 也要補對應 BCP-47（de=`de-DE`、fr=`fr-FR`、grc=`el-GR`、la=`it-IT` 教會式、hbo=`he-IL`），否則 🔊 會用英文聲念。⚠️ **同一份 `TTS`/`TTS_LANG` 語系對照表散落在多個頁面**（`review.vue`/`practice.vue`/`immersion.vue`/`smalltalk.vue`/`grammar.vue`/`today.vue`/`courses.vue`，其中 immersion/practice 另有 `LANG_LABEL`），**新增活語言時 7 個檔都要補齊**（活語言若漏補會用英文聲念外語，2026-06-04 已全數補上 de/fr）。測過或沒過的卡都進 `lang_vocab`（generate upsert + review 記 SRS），各語言獨立列表。
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
- 前端 AI 呼叫一律走 `useCoachAi().aiFetch`（自動帶 usePaid + free_exhausted 處理）。

## 六之二、時區・計時器・日曆（2026-06-04）

- **時區一律 Asia/Taipei**：Zeabur 跑 UTC，原本 `new Date().toISOString().slice(0,10)` 會把台灣凌晨算成昨天 → streak/今日時間/日曆/到期單字全錯一天。新增 `server/utils/today.ts`（`tzToday`/`tzMonth`/`tzDaysAgo`，寫死台北），**所有「今天」日期計算都改用它**（dashboard/activity/daily/journal/briefing/chat/task/vocab/ingest…）；`srs.ts` next_review 也台北。前端日曆與月份改用 `toLocaleDateString("en-CA")`（瀏覽器本地＝台北）對齊。⚠️ 新增任何用到「今天」的端點都要用 `today.ts`，別再寫 `toISOString().slice(0,10)`。
- **計時器**：`components/CoachTimer.vue`（吃 `useActivityTracker().activeSeconds`，⏱ mm:ss，分頁切走暫停）。chat/smalltalk/review/practice/immersion + **courses/grammar/grammar-map（2026-06-05 補）** 皆有。從進頁開始算，flush 進 `lang_activity`（review/grammar/courses→reading、practice→當前 skill、chat→speaking、immersion→listening）。**immersion onMounted 就起計時** → 只記錄觀看後的作答/討論時間也算入聽力。
  - ⚠️ **連續計時（2026-06-05 修）**：`useActivityTracker` 把「顯示累計秒數 `activeSeconds`（單調遞增、永不歸零）」與「送 server 的增量」分開——flush 只送 `activeSeconds - sentSeconds`、成功才推進 `sentSeconds`（失敗重送不重複計）。**別再讓 flush 把 activeSeconds 歸零**（會害計時器每 30/60 秒跳回 0、看似一直重新計）。離開頁面/切分頁用 `fetch(keepalive:true)` beacon 帶 Bearer header 送殘餘增量（authedFetch 是 header 認證，不能用 sendBeacon）。
- ⚠️ **NVIDIA 逾時保護（2026-06-05）**：`server/utils/nvidia.ts` fetch 加 AbortController 逾時（`nvidiaTimeoutMs` 預設 14s），超時 abort → 落 Gemini fallback，避免 Zeabur gateway 先回 **502 Bad Gateway**（聊天卡住連帶 activity 也 502）。⚠️ 若線上「總是」走 Gemini 並 429：八成是 **Zeabur 沒設 `NVIDIA_API_Key_OLINE_ONLY`** → NVIDIA 池空 → 每次跳過 NVIDIA 走 Gemini（key 本身測過 200/407ms 有效）。
- **日曆標今天**：語言首頁日曆今天格加 ring + 「今」徽章，標題顯示「今天 X月X日（週X）」。

## 七、DB 表（Supabase，全 RLS 依 user_id）

`lang_profile`/`lang_progress`/`lang_sessions`(persona/mode/topic/duration/feedback)/`lang_messages`/`lang_vocab`(SM-2)/`lang_homework`/`lang_activity`/`lang_level_history`/`lang_api_usage`(+bump_lang_usage RPC)/`lang_memory`(memory/highlights/briefing/briefing_date)/`lang_journal`/`lang_word_lists`/`lang_tasks`/`lang_content`/`lang_grammar`/`lang_daily`/`trusted_devices`。migration SQL 在 `database/coach-language-*.sql` 等，用 Supabase Management API 套用。

## 八、端點（`server/api/lang/*` + `server/api/devices/*`）

chat / profile(get,put) / progress(get,put) / activity / dashboard / usage / assess / briefing / memory(get,regenerate) / journal(get, generate) / sessions / messages / coaches / vocab(index,generate,review get/post,[id] patch/delete) / homework / task(generate, [id]/answer) / smalltalk(start, feedback) / content(ingest, watch, index, watch-stats) / grammar(index, lesson, done) / daily(get, item, done) / devices(check, index, [id] patch)。

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

## 待辦（次要）

Live2D、雲端 TTS、AWL/GRE 詞庫實際 seed、速率限制、MFA、用量異常 email 通知、%C2 換真實 C2 wordlist。
