// ============================================================================
// 英文「情境實用句」策展庫（2026-06-05）
//   - 給寫作/口說練習：每句先給「情境（你想表達什麼）」讓使用者試答，再看「建議解答」
//     （範例英文 + 中譯 + 用法/禮貌提示），可朗讀複述、或請 AI 換一句類似的。
//   - 策展為可靠核心；自訂情境或「再多給我幾句」走 AI（NVIDIA 主→Gemini）無限延伸。
// 每句：situation(繁中情境/你想說的) / en(範例英文) / zh(中譯) / note?(用法提示)
// 加情境或句子：在 EN_SCENARIOS 補即可。scenario key 對齊頁面 chip。
// ============================================================================

export interface SentenceItem {
  id: string;
  situation: string; // 繁中：你想表達什麼 / 情境
  en: string;        // 範例英文（建議解答）
  zh: string;        // 中譯
  note?: string;     // 用法 / 禮貌 / 道地提示
}
export interface SentenceScenario {
  key: string;
  label: string;     // 繁中＋英文
  icon: string;
  blurb: string;
  items: SentenceItem[];
}

export const EN_SCENARIOS: SentenceScenario[] = [
  {
    key: "airport",
    label: "機場 At the Airport",
    icon: "✈️",
    blurb: "報到、安檢、轉機、行李、入境海關的實用對應。",
    items: [
      { id: "air-1", situation: "在報到櫃台說你要靠走道的位子", en: "Could I have an aisle seat, please?", zh: "可以給我靠走道的位子嗎？", note: "aisle [aɪl] 走道；window seat 靠窗" },
      { id: "air-2", situation: "問這班飛機在哪個登機門", en: "Which gate does this flight board at?", zh: "這班飛機在哪個登機門登機？", note: "board 登機（動詞）" },
      { id: "air-3", situation: "告訴櫃台你只有一件隨身行李", en: "I only have one carry-on bag.", zh: "我只有一件隨身行李。", note: "carry-on 隨身；checked baggage 託運行李" },
      { id: "air-4", situation: "說你的轉機時間只有四十分鐘，會不會太趕", en: "I have only a forty-minute layover — will that be enough?", zh: "我只有四十分鐘轉機時間，夠嗎？", note: "layover 轉機停留" },
      { id: "air-5", situation: "在安檢說你筆電要不要拿出來", en: "Do I need to take my laptop out of the bag?", zh: "我需要把筆電從包包拿出來嗎？" },
      { id: "air-6", situation: "跟海關說你來是參加學術研討會", en: "I'm here to attend an academic conference.", zh: "我來是為了參加一場學術研討會。", note: "海關問訪問目的時的標準回答" },
      { id: "air-7", situation: "說你會待兩週，然後回台灣", en: "I'll be staying for two weeks and then returning to Taiwan.", zh: "我會待兩週，然後回台灣。" },
      { id: "air-8", situation: "你的行李沒出來，要去申報遺失", en: "My checked luggage didn't arrive — I'd like to report it missing.", zh: "我的託運行李沒到，我要申報遺失。" },
      { id: "air-9", situation: "問登機門臨時改了嗎", en: "Has the gate been changed?", zh: "登機門有改嗎？" },
      { id: "air-10", situation: "請對方說慢一點，你沒聽懂", en: "Sorry, could you say that more slowly?", zh: "抱歉，可以說慢一點嗎？", note: "比 'speak slowly' 更禮貌自然" },
      { id: "air-11", situation: "說你想把這班改到明天", en: "Is it possible to change this flight to tomorrow?", zh: "這班可以改到明天嗎？" },
      { id: "air-12", situation: "問免稅店在安檢之後嗎", en: "Are the duty-free shops past security?", zh: "免稅店在安檢之後嗎？", note: "past security 過了安檢" },
    ],
  },
  {
    key: "school-admin",
    label: "在學校辦事 School Admin",
    icon: "🎓",
    blurb: "註冊、找指導教授、圖書館、成績單、延期等校務對應。",
    items: [
      { id: "sch-1", situation: "說你想跟指導教授約見面", en: "I'd like to schedule a meeting with my advisor.", zh: "我想跟我的指導教授約個時間見面。", note: "advisor 指導教授；supervisor（英式）" },
      { id: "sch-2", situation: "問這門課還可以加選嗎", en: "Is it still possible to enrol in this course?", zh: "這門課還可以加選嗎？", note: "enrol in / register for a course" },
      { id: "sch-3", situation: "請對方幫你開一份正式成績單", en: "Could you issue an official transcript for me?", zh: "可以幫我開一份正式成績單嗎？", note: "transcript 成績單；issue 開立" },
      { id: "sch-4", situation: "說你想申請報告延期一週", en: "I'd like to request a one-week extension on my paper.", zh: "我想申請報告延期一週。", note: "extension 延期；on the deadline 對截止日" },
      { id: "sch-5", situation: "問借書最多可以借多久", en: "How long can I borrow these books for?", zh: "這些書最多可以借多久？" },
      { id: "sch-6", situation: "說你的學生證不見了，要補辦", en: "I've lost my student ID and need a replacement.", zh: "我的學生證不見了，需要補辦。", note: "replacement 補發" },
      { id: "sch-7", situation: "問這份文件要交到哪個辦公室", en: "Which office should I submit this form to?", zh: "這份表格要交到哪個辦公室？" },
      { id: "sch-8", situation: "禮貌地問截止日期是哪天", en: "Could you tell me when the deadline is?", zh: "可以告訴我截止日是什麼時候嗎？", note: "間接問句語序：when the deadline is" },
      { id: "sch-9", situation: "說你想旁聽這門研討課", en: "Would it be possible to audit this seminar?", zh: "我可以旁聽這門研討課嗎？", note: "audit 旁聽（不計學分）" },
      { id: "sch-10", situation: "請對方確認你的學費已經繳了", en: "Could you confirm that my tuition has been paid?", zh: "可以幫我確認學費已經繳了嗎？" },
      { id: "sch-11", situation: "問哪裡可以拿到館際互借的書", en: "Where can I pick up an interlibrary loan?", zh: "館際互借的書要去哪裡拿？", note: "interlibrary loan 館際互借" },
      { id: "sch-12", situation: "說你想換指導教授，想請教程序", en: "I'd like to change supervisors — could you walk me through the procedure?", zh: "我想換指導教授，可以說明一下流程嗎？", note: "walk me through 帶我走一遍/說明" },
    ],
  },
  {
    key: "academic",
    label: "學術場合 Academic Settings",
    icon: "🏛️",
    blurb: "研討會發問、發表、辦公時間、交流的學術用語。",
    items: [
      { id: "aca-1", situation: "在 Q&A 禮貌地提問前先謝講者", en: "Thank you for a fascinating paper — I have a question about your sources.", zh: "謝謝你精彩的論文，我想請教關於你史料的問題。", note: "Q&A 開場慣用語" },
      { id: "aca-2", situation: "問講者怎麼處理某個反對意見", en: "How would you respond to the objection that the dating is too early?", zh: "對於斷代過早這個質疑，你會怎麼回應？", note: "the objection that… 反對意見是…" },
      { id: "aca-3", situation: "說你大致同意但有個保留", en: "I largely agree, though I have one reservation.", zh: "我大致同意，不過有一點保留。", note: "reservation 保留意見" },
      { id: "aca-4", situation: "請對方再說明剛剛那個概念", en: "Could you elaborate on the point you made about typology?", zh: "可以再說明一下你剛剛提到的預表論嗎？", note: "elaborate on 詳細說明" },
      { id: "aca-5", situation: "發表開場介紹你要講什麼", en: "Today I'll argue that the two recensions are independent.", zh: "今天我要論證這兩個傳本是各自獨立的。", note: "發表常用 'I'll argue that…'" },
      { id: "aca-6", situation: "承認那超出你研究範圍", en: "That falls outside the scope of my study, but it's a fair point.", zh: "那超出我研究的範圍，但你說得有道理。", note: "scope 範圍；學術謙遜措辭" },
      { id: "aca-7", situation: "在辦公時間說想討論論文方向", en: "I came to discuss the direction of my dissertation.", zh: "我來是想討論我論文的方向。", note: "office hours 辦公時間" },
      { id: "aca-8", situation: "禮貌地不同意對方詮釋", en: "I see it slightly differently, if I may.", zh: "容我說，我的看法略有不同。", note: "if I may 委婉表達異議" },
      { id: "aca-9", situation: "請與會者推薦相關文獻", en: "Could you recommend any further reading on this?", zh: "這方面你能推薦一些延伸閱讀嗎？" },
      { id: "aca-10", situation: "交換聯絡方式以便日後合作", en: "I'd love to stay in touch — could we exchange emails?", zh: "我很想保持聯絡，可以交換 email 嗎？", note: "stay in touch 保持聯絡" },
      { id: "aca-11", situation: "說你的研究在處理某個空白", en: "My research addresses a gap in the scholarship on this text.", zh: "我的研究在補這個文本研究上的一個空白。", note: "a gap in the scholarship 研究空白" },
      { id: "aca-12", situation: "時間不夠，請把問題留到會後", en: "In the interest of time, perhaps we can discuss this afterwards.", zh: "為了顧及時間，這個或許我們會後再談。", note: "in the interest of time 為了時間考量" },
    ],
  },
  {
    key: "tax-office",
    label: "稅務局 Tax Office",
    icon: "🧾",
    blurb: "報稅、居留身分、扣除額、預約等稅務對應。",
    items: [
      { id: "tax-1", situation: "說你是來報所得稅的", en: "I'm here to file my income tax return.", zh: "我來報所得稅。", note: "file a tax return 報稅；return 報稅表" },
      { id: "tax-2", situation: "問你是不是稅務上的居民", en: "Am I considered a tax resident here?", zh: "我在這裡算是稅務居民嗎？", note: "tax resident 稅務居民" },
      { id: "tax-3", situation: "問你的獎學金要不要課稅", en: "Is my scholarship taxable?", zh: "我的獎學金要課稅嗎？", note: "taxable 應課稅的" },
      { id: "tax-4", situation: "問你可以申報哪些扣除額", en: "What deductions am I entitled to?", zh: "我可以申報哪些扣除額？", note: "deduction 扣除額；be entitled to 有資格享有" },
      { id: "tax-5", situation: "說你想預約一個諮詢時間", en: "I'd like to make an appointment for a consultation.", zh: "我想預約一個諮詢時間。" },
      { id: "tax-6", situation: "問需要帶哪些文件", en: "Which documents do I need to bring?", zh: "我需要帶哪些文件？" },
      { id: "tax-7", situation: "說你去年是部分時間在國外", en: "I was abroad for part of last year.", zh: "我去年有一部分時間在國外。", note: "abroad 在國外（副詞，不加 in）" },
      { id: "tax-8", situation: "問截止日是什麼時候、能不能延", en: "When is the filing deadline, and can it be extended?", zh: "報稅截止日是什麼時候？可以延嗎？" },
      { id: "tax-9", situation: "說你覺得算錯了，想申訴", en: "I believe there's been a miscalculation — I'd like to appeal.", zh: "我認為計算有誤，我想提出申訴。", note: "appeal 申訴；miscalculation 計算錯誤" },
      { id: "tax-10", situation: "問退稅大概多久會下來", en: "How long does a refund usually take?", zh: "退稅通常要多久？", note: "refund 退稅/退款" },
      { id: "tax-11", situation: "說你需要一份完稅證明", en: "I need a certificate of tax payment.", zh: "我需要一份完稅證明。" },
      { id: "tax-12", situation: "請對方用簡單的方式解釋", en: "Could you explain that in simpler terms?", zh: "可以用簡單一點的方式解釋嗎？", note: "in simpler terms 用更簡單的說法" },
    ],
  },
  {
    key: "hospital",
    label: "醫院 Hospital & Clinic",
    icon: "🏥",
    blurb: "掛號、描述症狀、領藥、預約、保險等就醫對應。",
    items: [
      { id: "hos-1", situation: "說你要掛號看診", en: "I'd like to register to see a doctor.", zh: "我要掛號看醫生。", note: "register 掛號；see a doctor 看醫生" },
      { id: "hos-2", situation: "說你這三天頭一直很痛", en: "I've had a bad headache for the past three days.", zh: "我這三天一直頭很痛。", note: "have had（現在完成）強調持續到現在" },
      { id: "hos-3", situation: "形容是悶痛還是刺痛", en: "It's more of a dull ache than a sharp pain.", zh: "比較像悶痛，不是刺痛。", note: "dull ache 悶痛；sharp pain 刺痛" },
      { id: "hos-4", situation: "說你對某種藥過敏", en: "I'm allergic to penicillin.", zh: "我對盤尼西林過敏。", note: "be allergic to 對…過敏" },
      { id: "hos-5", situation: "問這個藥怎麼吃", en: "How should I take this medication?", zh: "這個藥要怎麼吃？", note: "take medication 服藥" },
      { id: "hos-6", situation: "問一天吃幾次、飯前還飯後", en: "How many times a day, and before or after meals?", zh: "一天吃幾次？飯前還是飯後？" },
      { id: "hos-7", situation: "問這個保險有沒有給付", en: "Is this covered by my insurance?", zh: "這個我的保險有給付嗎？", note: "covered by insurance 保險有給付" },
      { id: "hos-8", situation: "說你想預約下週回診", en: "I'd like to book a follow-up appointment for next week.", zh: "我想預約下週回診。", note: "follow-up 回診/後續" },
      { id: "hos-9", situation: "問藥局在哪裡領藥", en: "Where do I go to pick up my prescription?", zh: "我要去哪裡領處方藥？", note: "prescription 處方（藥）" },
      { id: "hos-10", situation: "說你最近覺得很累、沒胃口", en: "I've been feeling very tired and have lost my appetite.", zh: "我最近一直很累，也沒胃口。", note: "lose one's appetite 沒胃口" },
      { id: "hos-11", situation: "問需不需要空腹抽血", en: "Do I need to fast before the blood test?", zh: "抽血前需要空腹嗎？", note: "fast 空腹（動詞）" },
      { id: "hos-12", situation: "請對方寫下診斷名稱給你", en: "Could you write down the diagnosis for me?", zh: "可以把診斷名稱寫給我嗎？", note: "diagnosis 診斷" },
    ],
  },
  {
    key: "daily-errands",
    label: "日常辦事 Banks · Renting · Dining",
    icon: "🏦",
    blurb: "銀行、租屋、餐廳等日常生活辦事的實用句。",
    items: [
      { id: "day-1", situation: "在銀行說你想開一個帳戶", en: "I'd like to open a bank account.", zh: "我想開一個銀行帳戶。" },
      { id: "day-2", situation: "問開戶需要帶什麼證件", en: "What ID do I need to open an account?", zh: "開戶需要帶什麼證件？", note: "ID 證件" },
      { id: "day-3", situation: "說你的卡被吞了/不能用", en: "My card isn't working — could you help?", zh: "我的卡不能用了，可以幫我嗎？" },
      { id: "day-4", situation: "租屋時問押金是多少", en: "How much is the deposit?", zh: "押金是多少？", note: "deposit 押金" },
      { id: "day-5", situation: "問水電網路有沒有含在租金裡", en: "Are utilities included in the rent?", zh: "水電網路有含在租金裡嗎？", note: "utilities 水電瓦斯等公用事業費" },
      { id: "day-6", situation: "請房東修理漏水", en: "There's a leak — could you have it fixed?", zh: "這裡漏水，可以請人來修嗎？", note: "have it fixed 使役被動：請人修" },
      { id: "day-7", situation: "餐廳訂位兩人今晚七點", en: "I'd like to book a table for two at seven tonight.", zh: "我想訂今晚七點兩位的位子。", note: "book a table for two 訂兩人桌" },
      { id: "day-8", situation: "說你吃素，問有沒有素食選擇", en: "I'm vegetarian — do you have any vegetarian options?", zh: "我吃素，有素食選擇嗎？", note: "options 選項；vegan 全素" },
      { id: "day-9", situation: "請對方幫你把帳單分開算", en: "Could we get separate checks, please?", zh: "可以幫我們分開結帳嗎？", note: "separate checks 分開結帳（美式）" },
      { id: "day-10", situation: "問可不可以刷卡", en: "Do you take cards?", zh: "你們可以刷卡嗎？", note: "比 'can I pay by card' 更口語" },
      { id: "day-11", situation: "說這個跟你點的不一樣", en: "I'm sorry, but this isn't what I ordered.", zh: "不好意思，這不是我點的。", note: "委婉客訴開頭 'I'm sorry, but…'" },
      { id: "day-12", situation: "請對方把退租流程寄給你", en: "Could you email me the move-out procedure?", zh: "可以把退租流程 email 給我嗎？", note: "move-out 退租/搬出" },
    ],
  },
  {
    key: "study-abroad",
    label: "出國留學 Studying Abroad",
    icon: "🌍",
    blurb: "申請、面試、抵達、選課、宿舍、融入的留學情境。",
    items: [
      { id: "abr-1", situation: "面試說你為什麼想來這間學校", en: "What draws me to your program is its strength in late antique studies.", zh: "吸引我來貴系的，是你們在晚期古代研究上的實力。", note: "What draws me to… 強調句，面試加分" },
      { id: "abr-2", situation: "說你的研究興趣是早期教會史", en: "My research focuses on the history of the early Church.", zh: "我的研究聚焦在早期教會史。", note: "focus on 聚焦於" },
      { id: "abr-3", situation: "問獎學金涵蓋哪些費用", en: "What does the scholarship cover?", zh: "獎學金涵蓋哪些費用？" },
      { id: "abr-4", situation: "抵達後去辦國際學生報到", en: "I'm here to check in as an international student.", zh: "我來辦國際學生報到。", note: "check in 報到" },
      { id: "abr-5", situation: "問怎麼辦居留證/簽證延期", en: "Where do I go to extend my residence permit?", zh: "我要去哪裡辦居留證延期？", note: "residence permit 居留證" },
      { id: "abr-6", situation: "跟室友說你想討論一下公共空間怎麼用", en: "Could we talk about how we'll share the common areas?", zh: "我們可以聊一下公共空間怎麼分配使用嗎？", note: "common areas 公共空間" },
      { id: "abr-7", situation: "禮貌請教授收你進他的研討課", en: "Would you be willing to take me on in your seminar?", zh: "您願意收我進您的研討課嗎？", note: "take someone on 收某人（學生）" },
      { id: "abr-8", situation: "說你還在適應這裡的學術寫作風格", en: "I'm still adjusting to the academic writing style here.", zh: "我還在適應這裡的學術寫作風格。", note: "adjust to 適應" },
      { id: "abr-9", situation: "問課程的評分方式", en: "How is this course assessed?", zh: "這門課怎麼評分？", note: "be assessed 被評分（被動）" },
      { id: "abr-10", situation: "跟同學提議組讀書會", en: "Would anyone be interested in forming a reading group?", zh: "有人有興趣組個讀書會嗎？", note: "form a reading group 組讀書會" },
      { id: "abr-11", situation: "向系辦問怎麼開銀行帳戶/報到流程", en: "Could you point me to the steps for settling in?", zh: "可以告訴我安頓下來要辦哪些手續嗎？", note: "settle in 安頓下來" },
      { id: "abr-12", situation: "婉謝邀約因為要趕論文", en: "I'd love to, but I'm on a deadline with my paper.", zh: "我很想去，但我論文趕著截稿。", note: "on a deadline 趕截止日" },
    ],
  },
  {
    key: "travel",
    label: "國外旅遊 Travelling Abroad",
    icon: "🧳",
    blurb: "問路、訂房、交通、參觀、求助的旅遊情境。",
    items: [
      { id: "trv-1", situation: "禮貌問路怎麼去大教堂", en: "Excuse me, could you tell me how to get to the cathedral?", zh: "不好意思，請問大教堂怎麼走？", note: "how to get to… 怎麼去；間接問句" },
      { id: "trv-2", situation: "問這附近有沒有推薦的在地餐廳", en: "Is there a good local restaurant around here?", zh: "這附近有推薦的在地餐廳嗎？" },
      { id: "trv-3", situation: "在櫃台說你有訂房，報名字", en: "I have a reservation under the name Lee.", zh: "我有訂房，名字是 Lee。", note: "under the name… 以…的名字" },
      { id: "trv-4", situation: "問退房時間是幾點", en: "What time is check-out?", zh: "退房時間是幾點？", note: "check-out 退房" },
      { id: "trv-5", situation: "問這班車有沒有到舊城區", en: "Does this bus go to the old town?", zh: "這班車有到舊城區嗎？" },
      { id: "trv-6", situation: "買票問學生有沒有優惠", en: "Is there a student discount?", zh: "有學生優惠嗎？", note: "discount 折扣" },
      { id: "trv-7", situation: "問修道院/博物館幾點關門", en: "What time does the monastery close?", zh: "修道院幾點關門？" },
      { id: "trv-8", situation: "請對方幫你拍張照", en: "Would you mind taking a photo of us?", zh: "可以幫我們拍張照嗎？", note: "Would you mind + V-ing 委婉請求" },
      { id: "trv-9", situation: "說你迷路了，想回車站", en: "I think I'm lost — I'm trying to get back to the station.", zh: "我好像迷路了，我想回車站。", note: "get back to 回到" },
      { id: "trv-10", situation: "問可不可以用英文溝通", en: "Do you happen to speak English?", zh: "請問您會說英文嗎？", note: "happen to 委婉，比直接問客氣" },
      { id: "trv-11", situation: "說這道菜不要加肉", en: "Could I have this without meat?", zh: "這道可以不要加肉嗎？", note: "without… 不加…" },
      { id: "trv-12", situation: "請對方幫你叫計程車", en: "Could you call a taxi for me?", zh: "可以幫我叫計程車嗎？" },
    ],
  },
  {
    key: "sharing-ideas",
    label: "分享想法 Sharing Ideas & Opinions",
    icon: "💡",
    blurb: "表達看法、同意/反對、舉例、追問、緩和語氣的討論用語。",
    items: [
      { id: "idea-1", situation: "禮貌帶出你的看法", en: "If I may, I'd like to offer a different perspective.", zh: "容我說，我想提出一個不同的觀點。", note: "offer a perspective 提出觀點" },
      { id: "idea-2", situation: "說你部分同意但有保留", en: "I see your point, but I'm not entirely convinced.", zh: "我懂你的意思，但我還不太信服。", note: "not entirely convinced 還不太信服" },
      { id: "idea-3", situation: "舉個例子支持你的說法", en: "Take the early creeds, for example.", zh: "就拿早期信經來說。", note: "Take… for example 舉例引導" },
      { id: "idea-4", situation: "用緩和語氣表達主張（學術 hedging）", en: "It could be argued that the influence runs the other way.", zh: "或可主張影響其實是反方向的。", note: "It could be argued that… 學術緩和主張" },
      { id: "idea-5", situation: "追問對方理由", en: "What makes you say that?", zh: "你為什麼會這麼說？", note: "比 'why' 更自然口語" },
      { id: "idea-6", situation: "把話題拉回重點", en: "To bring us back to the main point…", zh: "讓我們把話題拉回重點…", note: "bring us back to 拉回" },
      { id: "idea-7", situation: "承認你之前說錯了", en: "On reflection, I think I overstated that.", zh: "再想想，我覺得我剛剛講得太絕對了。", note: "on reflection 再想想；overstate 誇大" },
      { id: "idea-8", situation: "邀對方先說", en: "I'd be interested to hear your take first.", zh: "我想先聽聽你的看法。", note: "your take 你的看法（口語）" },
      { id: "idea-9", situation: "客氣地不同意", en: "I'd put it slightly differently.", zh: "我會用稍微不同的方式說。", note: "委婉表達異議的緩衝句" },
      { id: "idea-10", situation: "總結你的立場", en: "So, on balance, I lean towards the later dating.", zh: "所以整體而言，我傾向較晚的斷代。", note: "on balance 整體權衡；lean towards 傾向" },
      { id: "idea-11", situation: "請對方說明他的依據", en: "What's that based on?", zh: "這是根據什麼？", note: "based on 根據" },
      { id: "idea-12", situation: "表達你覺得這點很關鍵", en: "I think that's the crux of the matter.", zh: "我認為那是問題的核心。", note: "the crux of the matter 問題核心" },
    ],
  },
];

export function scenarioByKey(key: string): SentenceScenario | undefined {
  return EN_SCENARIOS.find((s) => s.key === key);
}
export function allSentences(): SentenceItem[] {
  return EN_SCENARIOS.flatMap((s) => s.items);
}
// 給前端的精簡資料（情境清單 + 句子）
export function scenariosForClient() {
  return EN_SCENARIOS.map((s) => ({
    key: s.key,
    label: s.label,
    icon: s.icon,
    blurb: s.blurb,
    count: s.items.length,
    items: s.items,
  }));
}
