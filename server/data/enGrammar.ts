// ============================================================================
// 英文文法「手工策展」課程 + 文法地圖資料（2026-06-05）
//   - 取代 en 文法課的 AI 即時生成：syllabus 與每課內容（解說/例句/練習）全人工策展，
//     品質穩定可控；例句偏宗教研究 / 人文取向。
//   - 同時作為「文法地圖」(/coach/en/grammar-map) 的分類瀏覽 + 查詢索引來源。
//   - 每個 topic 帶 keywords（中英＋觸發詞）供地圖即時關鍵字搜尋；自然語言提問再交給
//     /api/lang/grammar/lookup 的 AI 分類，回傳對應 topic id。
//   - levels：該文法點通常在哪些 CEFR 級別教/複習；en 文法課依所選 level 過濾。
// 加新文法點：在對應 category.topics 補一筆即可，前後端（課程/地圖/查詢）自動帶。
// ============================================================================

export interface GrammarExample {
  target: string;       // 英文例句
  translation: string;  // 繁中翻譯
  note?: string;        // 重點提示（繁中）
}
export interface GrammarPractice {
  q: string;            // 練習題（繁中說明）
  answer: string;       // 參考答案
}
export interface GrammarContent {
  explanation: string;        // 繁中解說
  examples: GrammarExample[];
  practice: GrammarPractice[];
}
export interface GrammarTopic {
  id: string;                 // 穩定 id（= 文法課 lessonId）
  en: string;                 // 英文名稱
  title: string;              // 繁中標題
  levels: string[];           // 適用 CEFR 級別
  summary: string;            // 一句話（繁中）
  keywords: string[];         // 搜尋用：中英別名＋觸發詞
  content: GrammarContent;
}
export interface GrammarCategory {
  key: string;
  label: string;              // 繁中＋英文
  icon: string;
  blurb: string;              // 分類簡介（繁中）
  topics: GrammarTopic[];
}

export const EN_GRAMMAR_CATEGORIES: GrammarCategory[] = [
  // ── 1. 時態 ────────────────────────────────────────────────────────────
  {
    key: "tense",
    label: "時態 Tenses",
    icon: "🕐",
    blurb: "動詞在時間軸上的形式：現在/過去/未來 × 簡單/進行/完成/完成進行。",
    topics: [
      {
        id: "tense-present-simple",
        en: "Present Simple",
        title: "現在簡單式",
        levels: ["A2", "B1"],
        summary: "習慣、事實、普遍真理；第三人稱單數加 -s。",
        keywords: ["present simple", "現在式", "現在簡單式", "habit", "習慣", "事實", "always", "usually", "第三人稱單數", "-s"],
        content: {
          explanation:
            "表示：①習慣與規律（every day, usually）②普遍真理或恆常狀態（神學/科學陳述）③時刻表式的未來。\n關鍵：主詞第三人稱單數時動詞加 -s/-es（he believes, she goes）；否定與疑問用 do/does。",
          examples: [
            { target: "Christians believe that God is love.", translation: "基督徒相信神是愛。", note: "普遍/教義性陳述用現在簡單式" },
            { target: "The service usually begins at ten on Sundays.", translation: "禮拜通常在週日十點開始。", note: "習慣 + 第三人稱單數 begins" },
            { target: "Water boils at 100 degrees Celsius.", translation: "水在攝氏一百度沸騰。", note: "普遍真理" },
          ],
          practice: [
            { q: "填入正確形式：He ___ (study) early Christian liturgy.", answer: "studies" },
            { q: "改否定：The monastery opens to visitors.", answer: "The monastery does not (doesn't) open to visitors." },
          ],
        },
      },
      {
        id: "tense-present-continuous",
        en: "Present Continuous",
        title: "現在進行式",
        levels: ["A2", "B1"],
        summary: "此刻正在進行、暫時的狀態、已安排的未來。",
        keywords: ["present continuous", "現在進行式", "be + ing", "now", "正在", "暫時", "安排的未來"],
        content: {
          explanation:
            "be (am/is/are) + V-ing。表示：①說話當下正在發生 ②近期暫時的情況 ③已確定安排的未來計畫。\n注意狀態動詞（know, believe, belong）一般不用進行式。",
          examples: [
            { target: "She is writing a thesis on Gnostic texts.", translation: "她正在寫一篇關於諾斯底文獻的論文。", note: "目前持續進行的一段時期" },
            { target: "We are meeting the bishop next week.", translation: "我們下週要見主教。", note: "已安排的未來" },
          ],
          practice: [
            { q: "填空：Listen — the choir ___ (sing) the Kyrie now.", answer: "is singing" },
            { q: "判斷對錯並改正：I am knowing the answer.", answer: "錯。狀態動詞不用進行式 → I know the answer." },
          ],
        },
      },
      {
        id: "tense-present-perfect",
        en: "Present Perfect",
        title: "現在完成式",
        levels: ["B1", "B2"],
        summary: "過去發生但與「現在」相關：經驗、未完成時段、剛完成的結果。",
        keywords: ["present perfect", "現在完成式", "have/has + p.p.", "經驗", "ever", "never", "already", "yet", "since", "for", "just"],
        content: {
          explanation:
            "have/has + 過去分詞。用於：①人生經驗（have you ever…）②從過去持續到現在（since/for）③過去動作對現在的結果（I've lost my notes = 現在沒有）。\n與過去簡單式的差別：完成式不指明確切過去時間點；一旦講出 yesterday/in 1900 等明確過去時間就用過去簡單式。",
          examples: [
            { target: "Scholars have debated this doctrine for centuries.", translation: "學者們已爭論這教義數百年。", note: "for + 持續到現在" },
            { target: "I have never read the Nag Hammadi codices in full.", translation: "我從未完整讀過拿戈瑪第經集。", note: "經驗" },
            { target: "She has just submitted her dissertation.", translation: "她剛交出論文。", note: "just + 剛完成的結果" },
          ],
          practice: [
            { q: "完成式或過去式？They ___ (publish) the critical edition in 1998.", answer: "published（有明確過去時間 1998 → 過去式）" },
            { q: "填空：We ___ (know) each other since seminary.", answer: "have known" },
          ],
        },
      },
      {
        id: "tense-present-perfect-continuous",
        en: "Present Perfect Continuous",
        title: "現在完成進行式",
        levels: ["B2"],
        summary: "從過去持續到現在、且強調「過程/持續時間」的動作。",
        keywords: ["present perfect continuous", "現在完成進行式", "have been + ing", "持續", "for hours", "all day"],
        content: {
          explanation:
            "have/has been + V-ing。強調動作的「持續過程」而非完成結果，常和 for / since / all day 連用，也可解釋眼前的後果（你怎麼滿頭大汗？I've been running）。",
          examples: [
            { target: "He has been translating the Vulgate passages all morning.", translation: "他整個早上都在翻譯武加大譯本的段落。", note: "強調持續過程" },
            { target: "They have been researching this manuscript since 2019.", translation: "他們自 2019 年起一直在研究這份手稿。" },
          ],
          practice: [
            { q: "選擇：Your eyes are red. — I ___ (read) old microfilms.", answer: "have been reading（強調持續過程/眼前後果）" },
          ],
        },
      },
      {
        id: "tense-past-simple",
        en: "Past Simple",
        title: "過去簡單式",
        levels: ["A2", "B1"],
        summary: "過去某個明確時間點完成的動作；規則動詞加 -ed。",
        keywords: ["past simple", "過去式", "過去簡單式", "-ed", "yesterday", "ago", "in 1900", "不規則動詞過去式"],
        content: {
          explanation:
            "規則動詞 +ed，不規則動詞需背（go→went, write→wrote）。用於過去明確時間發生且已結束的事。否定/疑問用 did + 原形。",
          examples: [
            { target: "Constantine convened the Council of Nicaea in 325.", translation: "君士坦丁於 325 年召開尼西亞大公會議。", note: "明確過去時間 → 過去式" },
            { target: "Augustine did not write the Confessions overnight.", translation: "奧古斯丁不是一夜寫成《懺悔錄》。", note: "否定 did not + 原形 write" },
          ],
          practice: [
            { q: "填過去式：Jerome ___ (translate) the Bible into Latin.", answer: "translated" },
            { q: "改疑問：They founded the monastery.", answer: "Did they found the monastery?" },
          ],
        },
      },
      {
        id: "tense-past-continuous",
        en: "Past Continuous",
        title: "過去進行式",
        levels: ["B1"],
        summary: "過去某時刻正在進行；常作另一動作的背景。",
        keywords: ["past continuous", "過去進行式", "was/were + ing", "while", "背景動作"],
        content: {
          explanation:
            "was/were + V-ing。表過去某一刻正在進行的動作，常與過去簡單式並用：較長的背景（過去進行）被一個較短的事件（過去簡單）打斷，用 when / while 連接。",
          examples: [
            { target: "While he was lecturing on patristics, the lights went out.", translation: "他正在講教父學時，燈熄了。", note: "while + 進行（背景）/ 過去式（打斷事件）" },
          ],
          practice: [
            { q: "填空：They ___ (debate) the creed when the messenger arrived.", answer: "were debating" },
          ],
        },
      },
      {
        id: "tense-past-perfect",
        en: "Past Perfect",
        title: "過去完成式",
        levels: ["B1", "B2"],
        summary: "「過去的過去」：在另一個過去動作之前已完成。",
        keywords: ["past perfect", "過去完成式", "had + p.p.", "過去的過去", "before", "after", "already had"],
        content: {
          explanation:
            "had + 過去分詞。用來標明兩個過去事件的先後：先發生的用過去完成式，後發生的用過去簡單式（常用 before/after/by the time 釐清順序）。",
          examples: [
            { target: "By the time the council met, the heresy had already spread widely.", translation: "大公會議召開時，異端早已廣為流傳。", note: "had spread 先於 met" },
          ],
          practice: [
            { q: "填空：She realized she ___ (leave) her notes in the archive.", answer: "had left" },
          ],
        },
      },
      {
        id: "tense-future-forms",
        en: "Future Forms",
        title: "未來的表達（will / be going to / 進行式）",
        levels: ["B1", "B2"],
        summary: "will（當下決定/預測）、be going to（計畫/有跡象）、現在進行（已安排）。",
        keywords: ["future", "未來式", "will", "be going to", "shall", "預測", "計畫", "未來進行", "future continuous"],
        content: {
          explanation:
            "英文沒有單一「未來時態」，而是多種表達：①will = 當下決定、承諾、預測 ②be going to = 既定計畫或有現時跡象的預測 ③現在進行式 = 已敲定的安排 ④future continuous (will be V-ing) = 未來某時正在進行。",
          examples: [
            { target: "I think the seminar will run late.", translation: "我想研討會會拖晚。", note: "預測用 will" },
            { target: "We are going to publish the translation next year.", translation: "我們打算明年出版譯本。", note: "既定計畫 be going to" },
            { target: "This time tomorrow I will be presenting my paper.", translation: "明天這時候我正在發表論文。", note: "future continuous" },
          ],
          practice: [
            { q: "選 will 或 be going to：Look at those clouds — it ___ rain.", answer: "is going to rain（有現時跡象）" },
          ],
        },
      },
    ],
  },

  // ── 2. 語態 ────────────────────────────────────────────────────────────
  {
    key: "voice",
    label: "語態 Voice",
    icon: "🔄",
    blurb: "主動 vs 被動：誰是焦點。學術寫作大量使用被動與使役結構。",
    topics: [
      {
        id: "voice-passive-basic",
        en: "Passive Voice (basics)",
        title: "被動語態基礎",
        levels: ["B1", "B2"],
        summary: "be + 過去分詞；強調動作承受者，施事者用 by 帶出（或省略）。",
        keywords: ["passive", "被動", "被動語態", "be + p.p.", "by", "受詞變主詞"],
        content: {
          explanation:
            "結構：be + 過去分詞。當動作的承受者比施事者重要、或施事者不明/不重要時使用（學術文體常見）。施事者若需提及用 by。\n各時態被動：is written / was written / has been written / will be written。",
          examples: [
            { target: "The codex was discovered near Nag Hammadi in 1945.", translation: "該抄本於 1945 年在拿戈瑪第附近被發現。", note: "焦點在抄本，施事者不重要" },
            { target: "These letters are attributed to Paul.", translation: "這些書信被歸於保羅。", note: "現在被動" },
          ],
          practice: [
            { q: "改被動：Scholars have edited the text.", answer: "The text has been edited (by scholars)." },
            { q: "改被動：They will publish the findings.", answer: "The findings will be published." },
          ],
        },
      },
      {
        id: "voice-passive-advanced",
        en: "Advanced Passive",
        title: "進階被動（情態/完成/雙受詞）",
        levels: ["B2", "C1"],
        summary: "情態被動 (must be done)、完成被動 (have been done)、雙受詞被動。",
        keywords: ["advanced passive", "情態被動", "modal passive", "完成被動", "雙受詞被動", "must be done"],
        content: {
          explanation:
            "①情態 + be + p.p.：must be preserved, can be argued。②完成式被動：have/had been + p.p.。③雙受詞動詞（give, offer）可有兩種被動，通常以「人」當主詞較自然。",
          examples: [
            { target: "The manuscripts must be handled with care.", translation: "這些手稿必須小心處理。", note: "情態被動" },
            { target: "He was given access to the Vatican archives.", translation: "他獲准進入梵蒂岡檔案館。", note: "雙受詞被動，以人當主詞" },
          ],
          practice: [
            { q: "改情態被動：We should cite primary sources.", answer: "Primary sources should be cited." },
          ],
        },
      },
      {
        id: "voice-causative",
        en: "Causative (have/get something done)",
        title: "使役被動（have / get sth done）",
        levels: ["B2", "C1"],
        summary: "請/讓別人做某事：have/get + 受詞 + 過去分詞。",
        keywords: ["causative", "使役", "have something done", "get something done", "請人做", "讓某事被做"],
        content: {
          explanation:
            "have/get + 受詞 + 過去分詞：表示「安排/促成某事被（他人）完成」，主詞不親自做。也有主動使役 have/make/let + 人 + 原形。",
          examples: [
            { target: "She had the fragile folios digitized.", translation: "她請人把脆弱的對開頁數位化。", note: "have sth done" },
            { target: "The abbot made the novices copy the psalter.", translation: "院長要見習修士抄寫聖詠集。", note: "主動使役 make + 人 + 原形" },
          ],
          practice: [
            { q: "用使役改寫：A specialist restored the icon (for her).", answer: "She had the icon restored (by a specialist)." },
          ],
        },
      },
      {
        id: "voice-passive-reporting",
        en: "Impersonal / Reporting Passive",
        title: "報導式被動（It is said that… / be said to…）",
        levels: ["C1"],
        summary: "客觀引述普遍說法：It is believed that… / X is thought to be…",
        keywords: ["reporting passive", "報導被動", "it is said that", "be said to", "impersonal passive", "客觀引述"],
        content: {
          explanation:
            "兩種句式表「一般認為/據說」：①It + be + p.p. + that 子句（It is believed that…）②主詞 + be + p.p. + to 不定詞（X is thought to be…）。學術寫作用來保持客觀、不指明來源。",
          examples: [
            { target: "It is widely held that the text predates the fourth century.", translation: "一般普遍認為這文本早於四世紀。" },
            { target: "The author is believed to have been a convert.", translation: "據信作者曾是改宗者。", note: "be believed to have + p.p." },
          ],
          practice: [
            { q: "改報導被動：People say the relic is genuine.", answer: "The relic is said to be genuine. / It is said that the relic is genuine." },
          ],
        },
      },
    ],
  },

  // ── 3. 語氣與情態 ──────────────────────────────────────────────────────
  {
    key: "mood",
    label: "語氣與情態 Mood & Modality",
    icon: "🎚️",
    blurb: "確定性、可能性、義務、假設、緩和語氣——學術論證的核心。",
    topics: [
      {
        id: "mood-modals-core",
        en: "Core Modal Verbs",
        title: "核心情態動詞",
        levels: ["B1", "B2"],
        summary: "can/could/may/might/must/should/will/would 表能力、可能、義務、許可。",
        keywords: ["modal verbs", "情態動詞", "can", "could", "may", "might", "must", "should", "would", "可能", "義務", "許可", "能力"],
        content: {
          explanation:
            "情態動詞後接原形，無第三人稱 -s。功能：能力(can)、可能性(may/might/could)、義務/必要(must/have to/should)、許可(may/can)、推測(must = 必然, can't = 不可能)。",
          examples: [
            { target: "This reading may reflect a later redaction.", translation: "這個讀法可能反映後期的編修。", note: "may = 可能性（學術 hedging）" },
            { target: "A historian must weigh the sources carefully.", translation: "史家必須謹慎衡量史料。", note: "must = 必要" },
          ],
          practice: [
            { q: "填情態：The inscription ___ be genuine — the evidence is overwhelming.（必然）", answer: "must" },
          ],
        },
      },
      {
        id: "mood-modal-perfect",
        en: "Modal Perfect",
        title: "情態完成（對過去的推測/評論）",
        levels: ["B2", "C1"],
        summary: "must/should/could/might + have + p.p.：對過去的推測或事後評論。",
        keywords: ["modal perfect", "情態完成", "must have", "should have", "could have", "might have", "過去推測", "後悔"],
        content: {
          explanation:
            "情態 + have + 過去分詞，談論過去：must have（過去必然）、can't have（過去不可能）、might/could have（過去也許）、should have（本該但沒做，含遺憾/批評）。",
          examples: [
            { target: "The scribe must have copied from an earlier exemplar.", translation: "抄寫者一定是抄自更早的底本。", note: "對過去的必然推測" },
            { target: "They should have preserved the original binding.", translation: "他們本該保留原來的裝幀（卻沒有）。", note: "should have = 本該卻沒" },
          ],
          practice: [
            { q: "填空（過去不可能）：He ___ written this — he died before the events.", answer: "can't have" },
          ],
        },
      },
      {
        id: "mood-conditionals",
        en: "Conditionals (0–3 + mixed)",
        title: "條件句（零/一/二/三/混合）",
        levels: ["B1", "B2", "C1"],
        summary: "從普遍真理到與事實相反的假設，四型＋混合型。",
        keywords: ["conditionals", "條件句", "if", "zero conditional", "first conditional", "second conditional", "third conditional", "mixed conditional", "假設", "與事實相反"],
        content: {
          explanation:
            "0型：if + 現在, 現在（普遍真理）。1型：if + 現在, will（可能的未來）。2型：if + 過去, would + 原形（與現在事實相反/不太可能）。3型：if + had p.p., would have p.p.（與過去事實相反）。混合型：過去條件→現在結果，或反之。",
          examples: [
            { target: "If you heat wax, it melts.", translation: "蠟加熱就會融化。", note: "0型 普遍真理" },
            { target: "If Britain had intervened in 1936, history might have changed.", translation: "若英國 1936 年介入，歷史也許會改變。", note: "3型 與過去相反" },
            { target: "If the text were authentic, it would settle the debate.", translation: "倘若這文本是真的，就能了結這場爭論。", note: "2型 were + would（不太可能）" },
          ],
          practice: [
            { q: "完成 3 型：If they ___ (catalogue) it properly, we ___ (not lose) it.", answer: "had catalogued … would not have lost" },
          ],
        },
      },
      {
        id: "mood-subjunctive",
        en: "Subjunctive & Unreal Uses",
        title: "假設/虛擬語氣（wish, if only, suggest that…）",
        levels: ["B2", "C1"],
        summary: "wish/if only + 過去；建議/要求動詞後接原形虛擬。",
        keywords: ["subjunctive", "虛擬語氣", "假設語氣", "wish", "if only", "suggest that", "demand that", "were", "I were", "原形虛擬"],
        content: {
          explanation:
            "①wish / if only + 過去式（對現在的遺憾）或 + had p.p.（對過去的遺憾）。②現代虛擬：suggest / demand / insist / recommend + that + 主詞 + 原形動詞（I suggest that he be ordained）。③固定虛擬 were：If I were you…",
          examples: [
            { target: "I wish I had access to the original manuscript.", translation: "真希望我能取得原始手稿（但沒有）。", note: "wish + 過去 = 對現在的遺憾" },
            { target: "The committee recommended that the canon be revised.", translation: "委員會建議修訂正典（be 原形虛擬）。", note: "recommend that + 原形 be" },
          ],
          practice: [
            { q: "填空：The dean insists that every student ___ (submit) sources.", answer: "submit（原形虛擬）" },
          ],
        },
      },
      {
        id: "mood-imperative",
        en: "Imperative",
        title: "祈使句",
        levels: ["A2", "B1"],
        summary: "命令、指示、邀請、禁令；以原形動詞開頭。",
        keywords: ["imperative", "祈使句", "命令", "原形動詞開頭", "don't", "let's"],
        content: {
          explanation:
            "以動詞原形開頭，省略主詞 you。否定用 Don't + 原形；建議共同行動用 Let's。常見於禮儀指示、戒律、食譜。",
          examples: [
            { target: "Honour your father and your mother.", translation: "當孝敬父母。", note: "誡命=祈使句" },
            { target: "Let us pray.", translation: "讓我們禱告。", note: "Let us/Let's = 共同行動" },
          ],
          practice: [
            { q: "改否定祈使：Touch the relics.", answer: "Don't touch the relics." },
          ],
        },
      },
      {
        id: "mood-hedging",
        en: "Hedging & Academic Stance",
        title: "緩和語氣與學術立場（hedging）",
        levels: ["C1", "C2"],
        summary: "用情態、副詞、句式弱化斷言，表達謹慎與客觀。",
        keywords: ["hedging", "緩和語氣", "學術立場", "it could be argued", "seem", "tend to", "arguably", "謹慎", "弱化斷言"],
        content: {
          explanation:
            "學術英文避免絕對斷言，用 hedging：情態(may/might/could)、模糊動詞(seem, appear, tend to, suggest)、副詞(arguably, presumably, broadly)、句式(It could be argued that…)。讓主張可辯護、不武斷。",
          examples: [
            { target: "This evidence suggests, rather than proves, a Syrian origin.", translation: "這證據暗示而非證明其敘利亞起源。", note: "suggest vs prove 的分寸" },
            { target: "It could be argued that the dating is too early.", translation: "或可主張這個斷代過早。", note: "It could be argued that… 經典 hedging 句式" },
          ],
          practice: [
            { q: "弱化斷言：This proves the author was a woman.", answer: "例：This may suggest that the author was a woman. / Arguably, the author was a woman." },
          ],
        },
      },
    ],
  },

  // ── 4. 句型 ────────────────────────────────────────────────────────────
  {
    key: "sentence",
    label: "句型 Sentence Patterns",
    icon: "🧩",
    blurb: "句子的骨架與變化：五大句型、存在句、強調、倒裝、疑問。",
    topics: [
      {
        id: "sent-five-patterns",
        en: "Five Basic Sentence Patterns",
        title: "五大基本句型",
        levels: ["B1", "B2"],
        summary: "SV / SVO / SVC / SVOO / SVOC——英文句子的五種骨架。",
        keywords: ["sentence patterns", "五大句型", "SVO", "SVC", "SVOO", "SVOC", "主詞動詞受詞", "補語"],
        content: {
          explanation:
            "①SV：主詞+完全不及物動詞（The congregation prayed.）②SVO：+受詞（He read the gospel.）③SVC：+主詞補語（連綴動詞 be/seem，The text is ancient.）④SVOO：+間接+直接受詞（give, offer）⑤SVOC：+受詞補語（They called him heretic.）。",
          examples: [
            { target: "The council declared the teaching heretical.", translation: "大公會議宣告該教導為異端。", note: "SVOC：him=O, heretical=受詞補語" },
            { target: "She gave the library a rare codex.", translation: "她送給圖書館一部珍稀抄本。", note: "SVOO：間接受詞 the library + 直接受詞 a codex" },
          ],
          practice: [
            { q: "判斷句型：The manuscript seems incomplete.", answer: "SVC（seem 為連綴動詞，incomplete 為主詞補語）" },
          ],
        },
      },
      {
        id: "sent-there-be",
        en: "There is / There are",
        title: "存在句 There is / are",
        levels: ["A2", "B1"],
        summary: "引介「存在/有」；be 與後面的真主詞單複數一致。",
        keywords: ["there is", "there are", "存在句", "有", "introductory there"],
        content: {
          explanation:
            "There + be + 真主詞，引出某物的存在。be 的單複數跟「後面的名詞」一致：There is a chapel / There are two chapels。否定 There isn't / aren't。",
          examples: [
            { target: "There are several recensions of this creed.", translation: "這個信經有好幾個傳本。", note: "are 配複數 recensions" },
            { target: "There is no reference to the event in the chronicle.", translation: "編年史中沒有提到這事件。" },
          ],
          practice: [
            { q: "填 is/are：There ___ many lacunae in the papyrus.", answer: "are" },
          ],
        },
      },
      {
        id: "sent-cleft",
        en: "Cleft Sentences",
        title: "分裂句（It / What 強調句）",
        levels: ["C1"],
        summary: "把要強調的成分挑出來：It was X that… / What… is…",
        keywords: ["cleft", "分裂句", "強調句", "it was ... that", "what ... is", "emphasis", "強調"],
        content: {
          explanation:
            "①It-分裂句：It + be + 強調成分 + that/who…（It was Jerome who translated it. 強調是「耶柔米」）。②Wh-分裂句：What + 子句 + be + 重點（What matters is the manuscript tradition.）。用來凸顯資訊焦點。",
          examples: [
            { target: "It was at Nicaea that the term homoousios was adopted.", translation: "正是在尼西亞，homoousios 一詞被採用。", note: "強調地點" },
            { target: "What the editor changed was the punctuation, not the wording.", translation: "編者更動的是標點，而非用字。", note: "Wh-分裂句強調" },
          ],
          practice: [
            { q: "用 It-cleft 強調主詞：Paul wrote to the Romans.（強調 Paul）", answer: "It was Paul who wrote to the Romans." },
          ],
        },
      },
      {
        id: "sent-inversion",
        en: "Inversion",
        title: "倒裝句",
        levels: ["C1", "C2"],
        summary: "否定副詞/條件省略 if 時，助動詞移到主詞前。",
        keywords: ["inversion", "倒裝", "倒裝句", "never had I", "not only", "no sooner", "hardly", "should you", "強調倒裝"],
        content: {
          explanation:
            "①否定/限制副詞置句首 → 主詞與（助）動詞倒裝：Never had I seen…, Not only did he…, Hardly had…when…, No sooner…than…。②條件句省略 if 的倒裝：Had I known…, Should you need…。多用於正式/書面強調。",
          examples: [
            { target: "Not only did he edit the text, but he also translated it.", translation: "他不僅校訂了文本，還翻譯了它。", note: "Not only + 倒裝 did he" },
            { target: "Had the colophon survived, the dating would be certain.", translation: "若題記留存下來，斷代就會確定。", note: "省略 if 的倒裝 = If the colophon had survived" },
          ],
          practice: [
            { q: "倒裝改寫：I have never read a clearer argument.", answer: "Never have I read a clearer argument." },
          ],
        },
      },
      {
        id: "sent-question-types",
        en: "Question Types",
        title: "疑問句型（Yes/No、Wh-、附加、間接）",
        levels: ["B1"],
        summary: "是非問、wh- 問、附加問句、間接問句的語序。",
        keywords: ["questions", "疑問句", "yes/no question", "wh question", "tag question", "indirect question", "附加問句", "間接問句", "語序"],
        content: {
          explanation:
            "①Yes/No：助動詞前移（Did he…?）②Wh-：疑問詞 + 助動詞 + 主詞（Why did…?）③附加問句：陳述句 + 反向簡短問句（…, isn't it?）④間接問句：嵌入子句用「直述語序」（I wonder why he left. 不用倒裝、不用 do）。",
          examples: [
            { target: "Could you tell me where the archive is?", translation: "能告訴我檔案館在哪嗎？", note: "間接問句：where the archive is（直述語序，非 where is the archive）" },
            { target: "The codex is genuine, isn't it?", translation: "這抄本是真的，對吧？", note: "附加問句" },
          ],
          practice: [
            { q: "改間接問句：Where did she find it?（I asked …）", answer: "I asked where she had found it." },
          ],
        },
      },
    ],
  },

  // ── 5. 子句 ────────────────────────────────────────────────────────────
  {
    key: "clause",
    label: "子句 Clauses",
    icon: "🔗",
    blurb: "把句子接長、加資訊：關係子句、名詞子句、副詞子句、分詞構句。",
    topics: [
      {
        id: "clause-relative",
        en: "Relative Clauses",
        title: "關係子句（限定 / 非限定）",
        levels: ["B1", "B2"],
        summary: "who/which/that/whose/where 修飾名詞；非限定用逗號。",
        keywords: ["relative clause", "關係子句", "who", "which", "that", "whose", "where", "defining", "non-defining", "限定", "非限定", "逗號"],
        content: {
          explanation:
            "限定關係子句（無逗號）提供辨識必要資訊，可用 that；非限定（有逗號）補充資訊、不可用 that、不可省略關代。關代：人 who/whom、物 which、所屬 whose、地點 where、時間 when。",
          examples: [
            { target: "The scholar who edited the text is a Coptologist.", translation: "校訂這文本的學者是科普特學家。", note: "限定：辨識是哪位學者" },
            { target: "The codex, which dates to the fourth century, is fragmentary.", translation: "這部抄本（年代為四世紀）是殘篇。", note: "非限定：逗號 + which，補充資訊" },
          ],
          practice: [
            { q: "填關代：The monastery ___ houses the library is in Egypt.", answer: "which / that" },
            { q: "合併（非限定）：Origen wrote the Hexapla. He was from Alexandria.", answer: "Origen, who was from Alexandria, wrote the Hexapla." },
          ],
        },
      },
      {
        id: "clause-reduced-relative",
        en: "Reduced Relative / Participle",
        title: "簡化關係子句（分詞）",
        levels: ["B2", "C1"],
        summary: "省略關代 + be，用現在/過去分詞精簡修飾。",
        keywords: ["reduced relative", "簡化關係子句", "participle", "分詞修飾", "the man standing", "the book written"],
        content: {
          explanation:
            "主動意義 → 現在分詞（the scholars editing the text = who are editing）；被動意義 → 過去分詞（the text edited by Schaff = which was edited）。讓句子更精簡、學術。",
          examples: [
            { target: "The fragments found at Qumran reshaped textual criticism.", translation: "在昆蘭發現的殘篇重塑了文本批評。", note: "found = which were found（被動，過去分詞）" },
            { target: "Anyone citing this edition should note the sigla.", translation: "凡引用此版本者都應留意符號表。", note: "citing = who cites（主動，現在分詞）" },
          ],
          practice: [
            { q: "簡化：The manuscript that was written in uncials…", answer: "The manuscript written in uncials…" },
          ],
        },
      },
      {
        id: "clause-noun",
        en: "Noun Clauses",
        title: "名詞子句（that / whether / wh-）",
        levels: ["B2"],
        summary: "整個子句當主詞、受詞或補語。",
        keywords: ["noun clause", "名詞子句", "that clause", "whether", "if", "what", "間接陳述", "當主詞受詞"],
        content: {
          explanation:
            "由 that / whether / if / wh- 引導，整體扮演名詞角色：當受詞（I think that…）、主詞（That he forged it is doubtful）、補語（The question is whether…）。whether/if 表「是否」。",
          examples: [
            { target: "Whether the letter is authentic remains disputed.", translation: "這封信是否真實仍有爭議。", note: "名詞子句當主詞" },
            { target: "Scholars disagree about what the term originally meant.", translation: "學者對這詞原意為何意見不一。", note: "wh- 名詞子句當介詞受詞" },
          ],
          practice: [
            { q: "用名詞子句改寫：His authorship is uncertain.（用 Whether…）", answer: "Whether he was the author is uncertain." },
          ],
        },
      },
      {
        id: "clause-adverbial",
        en: "Adverbial Clauses",
        title: "副詞子句（時間/原因/讓步/目的）",
        levels: ["B2"],
        summary: "when/because/although/so that… 表時間、原因、讓步、目的、條件。",
        keywords: ["adverbial clause", "副詞子句", "when", "because", "although", "though", "so that", "while", "讓步", "原因", "目的", "時間"],
        content: {
          explanation:
            "由從屬連接詞引導，修飾主句：時間(when, while, as, after)、原因(because, since, as)、讓步(although, though, even though)、目的(so that, in order that)、條件(if, unless)。注意 although 接子句、despite 接名詞。",
          examples: [
            { target: "Although the colophon is damaged, the date is legible.", translation: "雖然題記受損，年代仍可辨讀。", note: "讓步 although + 子句" },
            { target: "He learned Syriac so that he could read the Peshitta.", translation: "他學敘利亞文，以便能讀別西大譯本。", note: "目的 so that" },
          ],
          practice: [
            { q: "用 although 或 despite：___ the damage, the text survives. / ___ it was damaged, the text survives.", answer: "Despite the damage… / Although it was damaged…" },
          ],
        },
      },
      {
        id: "clause-participle",
        en: "Participle Clauses",
        title: "分詞構句",
        levels: ["C1"],
        summary: "用分詞精簡並列或副詞子句，常見於正式書面。",
        keywords: ["participle clause", "分詞構句", "having done", "doing", "done", "分詞片語開頭", "精簡子句"],
        content: {
          explanation:
            "用分詞取代連接詞+主詞+動詞，使句子精簡：現在分詞表主動/同時（Reading the colophon, she dated the codex）、過去分詞表被動（Written in Coptic, the text…）、having + p.p. 表先後（Having edited the text, he wrote a commentary）。分詞主詞須與主句一致，否則為「懸垂分詞」錯誤。",
          examples: [
            { target: "Having compared the witnesses, the editor chose the older reading.", translation: "比對過各版本後，編者選了較古的讀法。", note: "having + p.p. 表先發生" },
            { target: "Written on papyrus, the letter has barely survived.", translation: "寫在莎草紙上的這封信幾乎沒能留存。", note: "過去分詞開頭=被動" },
          ],
          practice: [
            { q: "用分詞構句精簡：Because he was trained in palaeography, he dated it easily.", answer: "Trained in palaeography, he dated it easily." },
          ],
        },
      },
    ],
  },

  // ── 6. 名詞與冠詞 ──────────────────────────────────────────────────────
  {
    key: "noun",
    label: "名詞與冠詞 Nouns & Articles",
    icon: "📦",
    blurb: "可數性、冠詞、數量詞、所有格、學術名詞化。",
    topics: [
      {
        id: "noun-countability",
        en: "Countable / Uncountable",
        title: "可數與不可數名詞",
        levels: ["A2", "B1"],
        summary: "可數有單複數；不可數（抽象/物質）無複數、配 much/little。",
        keywords: ["countable", "uncountable", "可數", "不可數", "much", "many", "information", "evidence", "research"],
        content: {
          explanation:
            "不可數名詞（information, evidence, research, knowledge, advice）無複數、不加 a，量化用 much / a piece of。許多學術常用詞為不可數（evidence 沒有 evidences）。",
          examples: [
            { target: "There is little evidence for an early date.", translation: "支持早期斷代的證據很少。", note: "evidence 不可數 → little，不是 few" },
            { target: "She gave me a useful piece of advice.", translation: "她給了我一個有用的建議。", note: "a piece of advice" },
          ],
          practice: [
            { q: "改正：He published many researches and informations.", answer: "much research and information（皆不可數）" },
          ],
        },
      },
      {
        id: "noun-articles",
        en: "Articles (a/an/the/zero)",
        title: "冠詞 a / an / the / 零冠詞",
        levels: ["B1", "B2"],
        summary: "不定冠詞（首次/泛指）、定冠詞（特指/獨一）、零冠詞（泛指複數/抽象）。",
        keywords: ["articles", "冠詞", "a", "an", "the", "zero article", "定冠詞", "不定冠詞", "the Bible", "泛指"],
        content: {
          explanation:
            "a/an：首次提到、泛指單數可數。the：特指、雙方已知、獨一無二（the Pope, the Trinity）、後接限定修飾。零冠詞：泛指複數/不可數（Christians believe…）、多數專有名詞。注意慣用：go to church（做禮拜，零冠詞）vs go to the church（去那棟教堂）。",
          examples: [
            { target: "The author quotes the Septuagint, not a later version.", translation: "作者引用的是七十士譯本，而非後期版本。", note: "the = 特指獨一；a later version = 泛指某個" },
            { target: "Monks copied manuscripts by hand.", translation: "修士以手抄寫手稿。", note: "零冠詞泛指複數 + by hand 慣用語" },
          ],
          practice: [
            { q: "填冠詞或 ∅：He studied ___ theology at ___ University of Oxford.", answer: "∅ theology（抽象零冠詞）, the University of Oxford" },
          ],
        },
      },
      {
        id: "noun-quantifiers",
        en: "Quantifiers",
        title: "數量詞（much/many/few/little/some/any）",
        levels: ["B1"],
        summary: "依可數性選用；some/any 的肯定否定分工。",
        keywords: ["quantifiers", "數量詞", "much", "many", "few", "little", "a few", "a little", "some", "any", "several"],
        content: {
          explanation:
            "可數：many / few / a few / several；不可數：much / little / a little。a few/a little = 還有一些（正面）；few/little = 幾乎沒有（負面）。some 多用於肯定與邀請/請求；any 多用於否定與疑問。",
          examples: [
            { target: "Few manuscripts survive, but a little patience reveals much.", translation: "留存的手稿很少，但一點耐心能揭示很多。", note: "few(可數,負面)/a little(不可數,正面)/much(不可數)" },
          ],
          practice: [
            { q: "選 much/many：How ___ extant copies are there?", answer: "many（copies 可數）" },
          ],
        },
      },
      {
        id: "noun-possessive",
        en: "Possessives & Genitive",
        title: "所有格（'s / of）",
        levels: ["A2", "B1"],
        summary: "人用 's，物多用 of；複數所有格 's'。",
        keywords: ["possessive", "所有格", "genitive", "apostrophe s", "of", "'s", "所屬"],
        content: {
          explanation:
            "①'s 多用於人/動物/組織（the author's intent, the Church's teaching）。②of 多用於無生命/抽象（the meaning of the term）。③複數以 s 結尾 → 加 '（the scholars' debate）。",
          examples: [
            { target: "The editor's preface explains the apparatus.", translation: "編者的序言說明校勘符號。", note: "人用 's" },
            { target: "The structure of the argument is clear.", translation: "論證的結構很清楚。", note: "抽象多用 of" },
          ],
          practice: [
            { q: "改寫：the conclusions of the scholars（用 's）", answer: "the scholars' conclusions" },
          ],
        },
      },
      {
        id: "noun-nominalization",
        en: "Nominalization",
        title: "名詞化（學術文體）",
        levels: ["C1", "C2"],
        summary: "把動詞/形容詞轉成名詞，使文體抽象、緊湊、客觀。",
        keywords: ["nominalization", "名詞化", "abstract noun", "academic style", "the development of", "緊湊", "抽象文體"],
        content: {
          explanation:
            "把動作/性質改寫為名詞（develop→the development, analyse→the analysis, important→the importance），讓資訊密度提高、語氣客觀，是學術英文的標誌。但過度名詞化會使句子笨重、難讀，須拿捏。",
          examples: [
            { target: "The reconstruction of the archetype depends on careful collation.", translation: "原型的重建有賴仔細的校勘。", note: "reconstruct→the reconstruction（名詞化）" },
            { target: "Her analysis led to a reassessment of the dating.", translation: "她的分析促成對斷代的重新評估。" },
          ],
          practice: [
            { q: "名詞化改寫：Because scholars collated the witnesses carefully, …", answer: "例：Careful collation of the witnesses led to…" },
          ],
        },
      },
    ],
  },

  // ── 7. 動詞變化 ────────────────────────────────────────────────────────
  {
    key: "verb",
    label: "動詞變化 Verb Forms",
    icon: "🔧",
    blurb: "動名詞與不定詞、不規則動詞、片語動詞、間接引述、動詞句型。",
    topics: [
      {
        id: "verb-gerund-infinitive",
        en: "Gerund vs Infinitive",
        title: "動名詞 vs 不定詞",
        levels: ["B1", "B2"],
        summary: "哪些動詞後接 -ing、哪些接 to V，意義有時不同。",
        keywords: ["gerund", "infinitive", "動名詞", "不定詞", "to do", "doing", "enjoy doing", "want to", "remember to/doing", "stop"],
        content: {
          explanation:
            "①只接動名詞：enjoy, avoid, consider, suggest, finish, mind。②只接不定詞：want, decide, hope, agree, refuse, manage。③兩者皆可但意義不同：remember/forget/stop（to do=要去做；doing=做過/正在做）、try（to=設法/doing=試試看）。",
          examples: [
            { target: "He stopped to pray.", translation: "他停下來去禱告。", note: "stop to do = 停下來為了做" },
            { target: "He stopped praying.", translation: "他停止禱告。", note: "stop doing = 停止正在做的事" },
            { target: "I suggest consulting the apparatus.", translation: "我建議參閱校勘欄。", note: "suggest + 動名詞（不接 to）" },
          ],
          practice: [
            { q: "填 to read / reading：Remember ___ the footnotes before citing.（別忘了要去讀）", answer: "to read" },
          ],
        },
      },
      {
        id: "verb-irregular",
        en: "Irregular Verbs",
        title: "不規則動詞",
        levels: ["A2", "B1"],
        summary: "三態需記憶：原形—過去式—過去分詞。",
        keywords: ["irregular verbs", "不規則動詞", "三態", "go went gone", "write wrote written", "過去分詞"],
        content: {
          explanation:
            "常用不規則動詞的三態須背熟，過去分詞用於完成式與被動：write-wrote-written, speak-spoke-spoken, take-took-taken, give-gave-given, become-became-become, read-read-read（發音變化）。",
          examples: [
            { target: "The text was written in Greek and later translated.", translation: "該文本以希臘文寫成，後來被翻譯。", note: "write 的過去分詞 written（被動）" },
            { target: "The doctrine had become orthodox by then.", translation: "到那時這教義已成為正統。", note: "become 的過去分詞 become（完成式）" },
          ],
          practice: [
            { q: "三態：begin / ___ / ___", answer: "begin – began – begun" },
          ],
        },
      },
      {
        id: "verb-phrasal",
        en: "Phrasal Verbs",
        title: "片語動詞",
        levels: ["B2", "C1"],
        summary: "動詞 + 介副詞，意義常不可從字面推；可分/不可分。",
        keywords: ["phrasal verbs", "片語動詞", "look up", "carry out", "point out", "可分", "不可分", "介副詞"],
        content: {
          explanation:
            "動詞 + 介系詞/副詞，整體有新義（carry out = 執行、point out = 指出、draw on = 援引）。可分片語動詞，受詞為代名詞時須插在中間（look it up，不可 look up it）。學術寫作偏好較正式的單字動詞，但理解片語動詞仍必要。",
          examples: [
            { target: "The author draws on earlier rabbinic traditions.", translation: "作者援引了更早的拉比傳統。", note: "draw on = 援引（不可分）" },
            { target: "She pointed out an error in the apparatus.", translation: "她指出校勘欄中的一個錯誤。", note: "point out = 指出" },
          ],
          practice: [
            { q: "代名詞位置改正：Please look up it in the lexicon.", answer: "Please look it up in the lexicon.（可分，代名詞插中間）" },
          ],
        },
      },
      {
        id: "verb-reported-speech",
        en: "Reported Speech",
        title: "間接引述",
        levels: ["B2"],
        summary: "把直接引語轉述：時態後移、人稱與時間地點詞調整。",
        keywords: ["reported speech", "間接引述", "indirect speech", "backshift", "時態後移", "said that", "told", "asked if"],
        content: {
          explanation:
            "轉述他人話語時：①時態通常後移（is→was, will→would, have done→had done）②人稱、時間地點詞調整（today→that day）③問句改間接（用 if/whether + 直述語序）。陳述普遍真理時時態可不後移。",
          examples: [
            { target: "He said that the manuscript was a forgery.", translation: "他說那份手稿是偽造的。", note: "is→was 時態後移" },
            { target: "She asked whether the colophon had survived.", translation: "她問題記是否留存。", note: "問句→ whether + 直述語序，has→had" },
          ],
          practice: [
            { q: "改間接：\"I will publish the edition,\" she said.", answer: "She said (that) she would publish the edition." },
          ],
        },
      },
      {
        id: "verb-patterns",
        en: "Verb Complementation Patterns",
        title: "動詞句型（verb + that / + sb + to…）",
        levels: ["B2", "C1"],
        summary: "報導/思考動詞後常接 that 子句或 + 受詞 + 不定詞。",
        keywords: ["verb patterns", "動詞句型", "verb + that", "verb + object + to", "argue that", "claim that", "expect sb to", "complementation"],
        content: {
          explanation:
            "學術常用動詞的接法：①argue/claim/maintain/suggest/note + that 子句（argue that the dating is wrong）②expect/allow/enable/cause + 受詞 + to V（enable scholars to access…）。掌握搭配可避免中式直譯。",
          examples: [
            { target: "He maintains that the two recensions are independent.", translation: "他主張這兩個傳本各自獨立。", note: "maintain that + 子句" },
            { target: "Digitization has enabled researchers to compare witnesses.", translation: "數位化使研究者得以比對各版本。", note: "enable + 受詞 + to V" },
          ],
          practice: [
            { q: "選句型：The evidence allows us ___ a firm conclusion.（draw）", answer: "to draw（allow + 受詞 + to V）" },
          ],
        },
      },
    ],
  },

  // ── 8. 連接詞 ──────────────────────────────────────────────────────────
  {
    key: "conjunction",
    label: "連接詞 Conjunctions",
    icon: "➕",
    blurb: "把字、片語、子句接起來：對等、從屬、相關、轉折語。",
    topics: [
      {
        id: "conj-coordinating",
        en: "Coordinating Conjunctions",
        title: "對等連接詞（FANBOYS）",
        levels: ["A2", "B1"],
        summary: "for/and/nor/but/or/yet/so 連接對等成分；前常加逗號。",
        keywords: ["coordinating conjunctions", "對等連接詞", "FANBOYS", "and", "but", "or", "so", "yet", "for", "nor"],
        content: {
          explanation:
            "FANBOYS = for, and, nor, but, or, yet, so，連接「對等」的字/片語/獨立子句。連接兩個獨立子句時，連接詞前加逗號（…, but …）。",
          examples: [
            { target: "The papyrus is fragmentary, yet its value is immense.", translation: "這莎草紙是殘篇，但其價值極大。", note: "yet 連接兩獨立子句，前加逗號" },
          ],
          practice: [
            { q: "選 but/so：The text is late, ___ it preserves an early tradition.", answer: "but（轉折）" },
          ],
        },
      },
      {
        id: "conj-subordinating",
        en: "Subordinating Conjunctions",
        title: "從屬連接詞",
        levels: ["B1", "B2"],
        summary: "because/although/while/if/when… 引出從屬子句。",
        keywords: ["subordinating conjunctions", "從屬連接詞", "because", "although", "while", "if", "when", "since", "unless", "whereas"],
        content: {
          explanation:
            "引導從屬（副詞）子句，表原因(because, since)、讓步(although, though)、對比(whereas, while)、條件(if, unless)、時間(when, after)。從屬子句置句首時，後面加逗號（Although…, the main clause）。",
          examples: [
            { target: "Whereas Mark is terse, John is reflective.", translation: "馬可簡練，約翰則富思辨。", note: "whereas 表對比" },
          ],
          practice: [
            { q: "用 unless 改寫：If you don't cite sources, the claim is weak.", answer: "Unless you cite sources, the claim is weak." },
          ],
        },
      },
      {
        id: "conj-correlative",
        en: "Correlative Conjunctions",
        title: "相關連接詞",
        levels: ["B2"],
        summary: "成對使用：both…and, either…or, not only…but also。",
        keywords: ["correlative conjunctions", "相關連接詞", "both and", "either or", "neither nor", "not only but also", "成對", "平行結構"],
        content: {
          explanation:
            "成對連接詞須維持「平行結構」（兩邊詞性/結構對稱）：both A and B、either A or B、neither A nor B、not only A but also B。動詞與「最近的主詞」一致（neither…nor）。",
          examples: [
            { target: "The work is not only learned but also readable.", translation: "這部作品不僅淵博，也好讀。", note: "not only + 形容詞 / but also + 形容詞（平行）" },
            { target: "Neither the date nor the author is certain.", translation: "年代與作者都不確定。", note: "neither…nor，動詞配最近主詞 author→is" },
          ],
          practice: [
            { q: "改正平行：He both edited the text and a commentary.", answer: "He both edited the text and wrote a commentary.（兩邊都是動詞片語）" },
          ],
        },
      },
      {
        id: "conj-conjunctive-adverbs",
        en: "Conjunctive Adverbs / Linkers",
        title: "連接副詞與轉折語",
        levels: ["B2", "C1"],
        summary: "however, therefore, moreover… 連接概念，標點不同於連接詞。",
        keywords: ["conjunctive adverbs", "連接副詞", "轉折語", "however", "therefore", "moreover", "nevertheless", "thus", "in addition", "discourse markers", "標點"],
        content: {
          explanation:
            "however/therefore/moreover/nevertheless/thus 等連接「概念」，不是文法連接詞。連接兩個獨立子句時，前用分號、後加逗號（…; however, …），或另起一句（However, …）。表遞進(moreover)、結果(therefore/thus)、轉折(however/nevertheless)、對比(in contrast)。",
          examples: [
            { target: "The dating is uncertain; however, the provenance is clear.", translation: "斷代不確定；然而出處是清楚的。", note: "分號 + however + 逗號" },
            { target: "The witnesses disagree; therefore, an eclectic text is needed.", translation: "各版本互異；因此需要折衷文本。" },
          ],
          practice: [
            { q: "標點改正：The text is late however it is valuable.", answer: "The text is late; however, it is valuable." },
          ],
        },
      },
    ],
  },

  // ── 9. 介係詞 ──────────────────────────────────────────────────────────
  {
    key: "preposition",
    label: "介係詞 Prepositions",
    icon: "📍",
    blurb: "時間、地點、方向，以及固定動詞/形容詞 + 介係詞搭配。",
    topics: [
      {
        id: "prep-time",
        en: "Prepositions of Time",
        title: "時間介係詞 at / on / in",
        levels: ["A2", "B1"],
        summary: "at（鐘點/節慶）、on（日期/星期）、in（月/年/世紀/時段）。",
        keywords: ["prepositions of time", "時間介係詞", "at", "on", "in", "at noon", "on Sunday", "in 1945", "in the fourth century"],
        content: {
          explanation:
            "at：精確時點與某些節期（at noon, at Easter）。on：特定日子/日期/星期（on Sunday, on 25 December）。in：較長時段—月、年、季節、世紀（in 1945, in the fourth century）。",
          examples: [
            { target: "The codex was found in 1945, on a December day, at dawn.", translation: "該抄本於 1945 年十二月某日的黎明被發現。", note: "in 年 / on 日 / at 時點，由大到小" },
          ],
          practice: [
            { q: "填 at/on/in：The council met ___ 325, ___ the summer.", answer: "in 325, in the summer" },
          ],
        },
      },
      {
        id: "prep-place",
        en: "Prepositions of Place",
        title: "地點介係詞 at / on / in",
        levels: ["A2", "B1"],
        summary: "at（點）、on（面/接觸）、in（內部/範圍）。",
        keywords: ["prepositions of place", "地點介係詞", "at", "on", "in", "at the door", "on the wall", "in the library"],
        content: {
          explanation:
            "at：一個點/地址/地標（at the monastery）。on：表面接觸（on the page, on the wall）。in：封閉空間/範圍內（in the archive, in Egypt）。",
          examples: [
            { target: "The marginal note is on folio 12, in the lower margin.", translation: "這條旁註在第 12 葉、下緣處。", note: "on（表面）/ in（範圍內）" },
          ],
          practice: [
            { q: "填介係詞：The inscription is ___ the wall ___ the crypt.", answer: "on the wall, in the crypt" },
          ],
        },
      },
      {
        id: "prep-movement",
        en: "Prepositions of Movement",
        title: "移動方向介係詞",
        levels: ["B1"],
        summary: "to, into, onto, through, across, towards 表方向與路徑。",
        keywords: ["prepositions of movement", "方向介係詞", "to", "into", "onto", "through", "across", "towards", "移動"],
        content: {
          explanation:
            "to（目的地）、into（進入內部）、onto（移上表面）、through（穿過）、across（橫越）、towards（朝向）。注意 arrive in/at（不用 arrive to）。",
          examples: [
            { target: "The relics were carried into the basilica.", translation: "聖髑被抬進大殿。", note: "into = 進入內部" },
            { target: "Pilgrims travelled across Anatolia to Jerusalem.", translation: "朝聖者橫越安納托利亞前往耶路撒冷。" },
          ],
          practice: [
            { q: "改正：They arrived to the monastery at dusk.", answer: "They arrived at the monastery at dusk.（arrive at/in）" },
          ],
        },
      },
      {
        id: "prep-dependent",
        en: "Dependent Prepositions",
        title: "固定搭配介係詞",
        levels: ["B2", "C1"],
        summary: "特定動詞/形容詞/名詞固定接某介係詞，須整組記。",
        keywords: ["dependent prepositions", "固定搭配", "collocation", "depend on", "consist of", "based on", "different from", "interested in"],
        content: {
          explanation:
            "許多動詞/形容詞/名詞與特定介係詞固定搭配，無邏輯可循，須整組記憶：depend on, consist of, result in, based on, derived from, different from, an influence on, evidence for/of。用錯介係詞是常見錯誤。",
          examples: [
            { target: "The argument is based on internal evidence.", translation: "這論證以內證為依據。", note: "based on" },
            { target: "This tradition derives from a Semitic source.", translation: "這傳統源自一個閃語來源。", note: "derive from" },
          ],
          practice: [
            { q: "填介係詞：The dating depends ___ the script and consists ___ several criteria.", answer: "on … of" },
          ],
        },
      },
    ],
  },
];

// ── 衍生工具 ───────────────────────────────────────────────────────────
export function allTopics(): GrammarTopic[] {
  return EN_GRAMMAR_CATEGORIES.flatMap((c) => c.topics);
}
export function topicById(id: string): GrammarTopic | undefined {
  return allTopics().find((t) => t.id === id);
}
export function categoryOf(id: string): GrammarCategory | undefined {
  return EN_GRAMMAR_CATEGORIES.find((c) => c.topics.some((t) => t.id === id));
}

// en 文法課 syllabus：依 CEFR level 過濾（topic.levels 含該級別），帶入策展 content。
export function curatedSyllabus(level: string): any[] {
  return allTopics()
    .filter((t) => t.levels.includes(level))
    .map((t) => ({
      id: t.id,
      title: t.title,
      summary: t.summary,
      content: t.content,   // 預嵌策展內容 → lesson 端點直接回，不走 AI
      done: false,
    }));
}

// 地圖瀏覽資料（分類 + 各 topic 精簡欄位；不含 practice 答案以縮小傳輸）
export function mapForClient() {
  return EN_GRAMMAR_CATEGORIES.map((c) => ({
    key: c.key,
    label: c.label,
    icon: c.icon,
    blurb: c.blurb,
    topics: c.topics.map((t) => ({
      id: t.id,
      en: t.en,
      title: t.title,
      levels: t.levels,
      summary: t.summary,
      keywords: t.keywords,
      explanation: t.content.explanation,
      examples: t.content.examples,
    })),
  }));
}

// 給 lookup 的精簡索引（id + 名稱 + 關鍵字），供 AI 分類與關鍵字比對
export function lookupIndex() {
  return allTopics().map((t) => ({
    id: t.id,
    en: t.en,
    title: t.title,
    category: categoryOf(t.id)?.label ?? "",
    keywords: t.keywords,
  }));
}
