// ============================================================================
// 英文「短文 / 長文」範例庫（2026-06-05）
//   - 給寫作/口說練習不同長度的整段示範：同一個任務有「短文」與「長文」兩版，
//     讓使用者看到如何把想法展開成段落，先自己試寫/試說，再對照範文。
//   - 策展為可靠核心；「換一篇 / 給我另一個版本」走 AI（NVIDIA 主→Gemini）無限延伸。
// 每篇：topic(繁中主題) / length(短文|長文) / prompt(繁中任務情境) / en(範文) / zh(中譯) / note(重點句型)
// ============================================================================

export type PassageLength = "短文" | "長文";

export interface PassageItem {
  id: string;
  topic: string;       // 繁中主題（也當分類 chip）
  topicEn: string;
  length: PassageLength;
  prompt: string;      // 繁中：任務/情境
  en: string;          // 範文
  zh: string;          // 中譯
  note?: string;       // 重點句型/用語（繁中）
}

export const EN_PASSAGES: PassageItem[] = [
  // ── 自我介紹（學術場合）──
  {
    id: "intro-s",
    topic: "自我介紹", topicEn: "Self-introduction",
    length: "短文",
    prompt: "在研討會的場合，用 3–4 句簡短自我介紹（姓名、研究領域、來自哪裡）。",
    en: "Hello, I'm Hsin-Cheng Lee, a doctoral researcher from Taiwan. My work focuses on the history of the early Church, especially the development of the creeds. I'm here to learn from this community and to share part of my current project. It's a pleasure to meet you all.",
    zh: "大家好，我是李信政，來自台灣的博士研究生。我的研究聚焦在早期教會史，特別是信經的發展。我來這裡是想向各位學習，也分享我目前計畫的一部分。很高興認識大家。",
    note: "開場 'I'm X, a … from …'；'My work focuses on …' 帶出領域；結尾 'It's a pleasure to meet you'。",
  },
  {
    id: "intro-l",
    topic: "自我介紹", topicEn: "Self-introduction",
    length: "長文",
    prompt: "在系上歡迎會，用一段較完整的話自我介紹（背景、研究興趣、為何來這裡、期待）。",
    en: "Good afternoon, everyone. My name is Hsin-Cheng Lee, and I've come from Taiwan to begin doctoral research here. My background is in religious studies, and over the past few years my interests have narrowed to the history of the early Church — in particular, how the great creeds took shape amid the controversies of the fourth century. What drew me to this department was its strength in late antique studies and its remarkable manuscript collection. Beyond my own project, I'm hoping to learn the craft of textual criticism more rigorously and to take part in the reading groups here. I'd be glad to talk with anyone working on related questions, so please do come and find me.",
    zh: "大家午安。我是李信政，從台灣來這裡開始博士研究。我的背景是宗教學，過去幾年我的興趣逐漸收斂到早期教會史——尤其是幾大信經如何在四世紀的爭論中成形。吸引我來這個系的，是你們在晚期古代研究上的實力，以及那批了不起的手稿收藏。除了自己的計畫，我也希望更扎實地學會文本批評的功夫，並參與這裡的讀書會。我很樂意和任何研究相關問題的人交流，歡迎來找我。",
    note: "長文結構：問候→我是誰→背景與興趣收斂→為何來這（What drew me to…）→期待→邀請交流。",
  },

  // ── 留學動機（SOP）──
  {
    id: "sop-s",
    topic: "留學動機", topicEn: "Statement of Purpose",
    length: "短文",
    prompt: "用 3–4 句說明你為什麼想申請這個博士學程。",
    en: "I'm applying to this program because of its exceptional strength in patristics and textual criticism. My research on the early creeds requires close work with manuscripts, which your collection and faculty are ideally suited to support. I'm especially eager to work with scholars who treat philology and theology as one inquiry. This is, for me, the natural place to pursue these questions.",
    zh: "我申請這個學程，是因為它在教父學與文本批評上的卓越實力。我對早期信經的研究需要密切處理手稿，而你們的館藏與師資正適合支援這樣的工作。我特別渴望與那些把語文學與神學視為同一探究的學者共事。對我而言，這裡就是追問這些問題的不二之選。",
    note: "申請理由三段式：學程強項→與我研究的契合→與誰共事；結尾收束 'the natural place to…'。",
  },
  {
    id: "sop-l",
    topic: "留學動機", topicEn: "Statement of Purpose",
    length: "長文",
    prompt: "寫一段較完整的留學動機（你的研究問題、為何是這個學程、未來方向）。",
    en: "My central question is deceptively simple: how did the early Church move from a living oral confession to fixed, authoritative creeds? Answering it means reading the fourth-century controversies not as abstract theology but as a textual process — councils editing, scribes copying, communities remembering. Over the past three years I have built the philological foundations for this work, but I have reached the limits of what I can do without sustained access to manuscripts and to scholars who think across philology, history, and doctrine. That is precisely what your program offers. Working here, I hope to produce a critical study of how creedal language was negotiated and transmitted, and ultimately to bring that method back to scholarship in Taiwan, where this field is still taking root.",
    zh: "我的核心問題看似簡單：早期教會如何從一個活的口傳告白，走向固定、具權威的信經？要回答它，就得把四世紀的爭論讀成一個文本過程——大公會議的編修、抄寫者的傳抄、群體的記憶——而非抽象的神學。過去三年我為這項工作打下語文學的基礎，但若沒有持續接觸手稿、沒有能跨語文學、歷史與教義一起思考的學者，我已到達自己能做到的極限。而這正是貴學程所提供的。在這裡，我希望完成一部關於信經語言如何被協商與傳遞的批判性研究，最終把這套方法帶回台灣——這個領域在那裡仍在生根。",
    note: "SOP 長文骨架：研究問題→方法視角→現有基礎與瓶頸→為何是這裡→未來貢獻。用 'That is precisely what…' 銜接。",
  },

  // ── 分享對議題的看法 ──
  {
    id: "opinion-s",
    topic: "分享想法", topicEn: "Sharing an Opinion",
    length: "短文",
    prompt: "用 3–4 句表達你對一個議題的看法（含一個理由與一點保留）。",
    en: "On the whole, I think the text is later than most scholars assume. The vocabulary points to a fourth-century setting, and the theological concerns fit that period well. That said, I wouldn't rule out an earlier core that was later expanded. So I'd hold the position lightly until we have firmer manuscript evidence.",
    zh: "整體而言，我認為這文本比多數學者假設的更晚。它的用語指向四世紀的背景，神學關懷也很符合那個時期。話雖如此，我不排除有一個更早的核心後來被擴充。所以在有更確切的手稿證據之前，我會謹慎地持守這個立場。",
    note: "表態框架：立場(On the whole…)→理由→保留(That said…)→收束(hold lightly until…)。學術緩和語氣。",
  },
  {
    id: "opinion-l",
    topic: "分享想法", topicEn: "Sharing an Opinion",
    length: "長文",
    prompt: "用一段話完整論述你對某議題的立場（主張、兩個理由、反方、回應、結論）。",
    en: "Let me state my position and then defend it. I'd argue that this text belongs to the late fourth century rather than the second, as the traditional attribution claims. Two considerations point this way. First, the vocabulary — especially the technical terms for the divine nature — only became standard after the great councils. Second, the very anxieties the author addresses are those of a community already living with a fixed creed. Now, one might object that an early core could have been expanded later, and I take that seriously; archaic phrases do survive in the opening lines. But isolated survivals are not the same as an early composition, and the document as we have it reads as a unified late work. On balance, then, the weight of internal evidence favours the later date, though I'd happily revise that if a securely early manuscript came to light.",
    zh: "讓我先表明立場，再加以辯護。我主張這文本屬於四世紀晚期，而非傳統歸屬所稱的二世紀。有兩點理由指向這個方向。第一，它的用語——尤其是描述神性的術語——是在幾次大公會議之後才成為標準。第二，作者所處理的那些焦慮，正是一個已經與固定信經共處的群體才有的。當然，有人可能反駁說，一個更早的核心後來被擴充了，這點我認真看待；開頭幾行確實留有古老的措辭。但零星的殘留並不等於早期的成書，而我們手上的這份文件讀來是一部統一的晚期作品。因此整體權衡，內證的份量傾向較晚的年代——不過若有一份確定早期的手稿出現，我也樂意修正。",
    note: "論述長文：表態→理由一→理由二→反方(one might object…)→回應(But…)→結論(On balance…)＋可修正姿態。",
  },

  // ── 旅遊經驗分享 ──
  {
    id: "travel-s",
    topic: "旅遊分享", topicEn: "Sharing a Travel Experience",
    length: "短文",
    prompt: "用 3–4 句分享一次難忘的旅遊經驗。",
    en: "Last summer I spent a week in Ravenna, mostly to see the early Christian mosaics. Standing under the dome of the Mausoleum of Galla Placidia, with that deep blue and the golden stars, was unforgettable. Photographs really don't do it justice. I came away understanding why people travelled so far to worship in places like that.",
    zh: "去年夏天我在拉溫納待了一週，主要是去看早期基督教的鑲嵌畫。站在加拉‧普拉奇迪亞陵墓的穹頂下，看著那片深藍與金色的繁星，令人難忘。照片真的拍不出那種感覺。離開時我才明白，為什麼人們願意千里迢迢來這樣的地方敬拜。",
    note: "經驗分享：時間地點目的→最難忘的一刻→評語(Photographs don't do it justice)→體會。過去式為主。",
  },
  {
    id: "travel-l",
    topic: "旅遊分享", topicEn: "Sharing a Travel Experience",
    length: "長文",
    prompt: "用一段話完整描述一次旅程（行前、過程、轉折、感受、收穫）。",
    en: "I had planned the trip to Ravenna for months, mainly to study its early Christian mosaics in person. The journey itself was awkward — two delayed trains and a long wait under a grey sky — and by the time I arrived I was tired and a little disheartened. But the moment I stepped into the Mausoleum of Galla Placidia, all of that fell away. The small room glows with a deep, almost midnight blue, scattered with golden stars, and the light shifts as you move. I stood there far longer than I had intended, scribbling notes I would never quite be able to read later. What struck me most was how the images were meant to be experienced, not merely studied; the space does something to you that no reproduction can. I left with a quieter, humbler sense of what these communities were trying to say in stone and glass.",
    zh: "我為這趟拉溫納之行規劃了好幾個月，主要是想親眼研究它早期基督教的鑲嵌畫。旅程本身並不順——兩班誤點的火車，加上在灰濛濛的天空下久候——等我抵達時，已經又累又有點氣餒。但就在我踏進加拉‧普拉奇迪亞陵墓的那一刻，這一切都消失了。那個小空間散發著深邃、近乎午夜的藍，點綴著金色的星辰，光線隨你移動而變化。我在那裡站得遠比預期久，潦草地寫著日後幾乎讀不出來的筆記。最讓我震動的是：這些圖像本是用來「經歷」的，而不只是被研究；那個空間會對你產生某種任何複製品都無法替代的作用。我離開時，對這些群體想用石與玻璃訴說的東西，多了一份更安靜、更謙卑的體會。",
    note: "敘事長文：行前期待→過程不順(awkward)→轉折(But the moment…)→細節描寫→體會(What struck me most…)→收穫。",
  },

  // ── 學術發表開場 ──
  {
    id: "talk-s",
    topic: "學術發表", topicEn: "Conference Talk Opening",
    length: "短文",
    prompt: "用 3–4 句做學術發表的開場（謝意、題目、你要論證什麼）。",
    en: "Thank you for the kind introduction, and thank you all for coming. In the next twenty minutes I'll argue that the two recensions of this creed are independent rather than derived one from the other. I'll do so in three steps: the manuscript evidence, the vocabulary, and the theological framing. Let me begin with the manuscripts.",
    zh: "謝謝你親切的介紹，也謝謝各位前來。在接下來二十分鐘，我要論證這個信經的兩個傳本是各自獨立的，而非彼此衍生。我會分三步進行：手稿證據、用語、以及神學框架。讓我從手稿開始。",
    note: "發表開場：謝意→主張(I'll argue that…)→路線圖(in three steps)→轉場(Let me begin with…)。",
  },
  {
    id: "talk-l",
    topic: "學術發表", topicEn: "Conference Talk Opening",
    length: "長文",
    prompt: "用一段較完整的話開場（謝意、問題的重要性、研究空白、你的主張與路線圖）。",
    en: "Thank you for that generous introduction, and thank you all for being here. I'd like to begin with a question that sounds settled but isn't: where did this creed actually come from? For over a century the standard view has been that the shorter recension is simply an abridgement of the longer one. That assumption has shaped how we edit the text, how we date it, and how we tell the story of its theology — and yet, surprisingly, it has never been tested against the full manuscript evidence. That is the gap this paper addresses. My claim, which I'll defend in three steps, is that the two recensions are in fact independent witnesses to a common source. First I'll lay out the manuscript tradition; then I'll turn to the distinctive vocabulary of each; and finally I'll show how the theological framing pulls in two different directions. If I'm right, we'll need to rethink not just the stemma but the history we've built on top of it. Let me begin, then, with the manuscripts.",
    zh: "謝謝你慷慨的介紹，也謝謝各位蒞臨。我想用一個聽起來已成定論、其實不然的問題開場：這個信經到底從何而來？一個多世紀以來，標準的看法是較短的傳本不過是較長那本的節縮。這個假設形塑了我們如何校訂文本、如何斷代、如何講述它的神學故事——然而出人意料的是，它從未被拿去對照完整的手稿證據檢驗。這正是本文要補的空白。我的主張——我會分三步辯護——是：這兩個傳本其實是同一來源的「各自獨立」的見證。首先我會鋪陳手稿傳統；接著轉向各自獨特的用語；最後說明神學框架如何朝兩個不同方向拉扯。如果我是對的，我們要重新思考的就不只是譜系圖，還有我們在其上建立的整段歷史。那麼，讓我從手稿開始。",
    note: "發表長文：謝意→以問題切入→既有共識→指出此共識未被檢驗(the gap)→主張＋三步路線圖→若成立的影響→轉場。",
  },

  // ── 感謝 email ──
  {
    id: "thanks-s",
    topic: "感謝 email", topicEn: "Thank-you Email",
    length: "短文",
    prompt: "寫一封 3–4 句的短 email，謝謝教授在辦公時間給你的建議。",
    en: "Dear Professor Hart, thank you for taking the time to meet with me yesterday. Your suggestions on framing my chapter were exactly what I needed, and I've already started revising along those lines. I'm grateful for your guidance. Best wishes, Hsin-Cheng.",
    zh: "親愛的 Hart 教授，謝謝您昨天撥空與我見面。您對我章節架構的建議正是我所需要的，我已經依此開始修改。感謝您的指導。祝好，信政。",
    note: "感謝信框架：稱呼→謝具體的事→說明影響→致謝→結尾敬語。'take the time to…' 撥空。",
  },
  {
    id: "thanks-l",
    topic: "感謝 email", topicEn: "Thank-you Email",
    length: "長文",
    prompt: "寫一封較完整的感謝 email，謝謝在研討會認識的學者給你建議與文獻。",
    en: "Dear Dr Okoye, I wanted to write and thank you properly for our conversation after my paper at the conference last week. Your question about the manuscript tradition has stayed with me — I think you put your finger on a weakness I had been reluctant to confront, and I'm now reworking that section more carefully. I'm also grateful for the references you mentioned; I've tracked down the Brock article, which is proving invaluable. It was a real pleasure to meet someone working on adjacent questions, and I hope our paths cross again. Please don't hesitate to let me know if I can ever be of help to you. With warm regards, Hsin-Cheng Lee.",
    zh: "親愛的 Okoye 博士，我想正式寫信，謝謝您上週在研討會我發表後與我的交談。您關於手稿傳統的提問一直縈繞在我心上——我想您點出了一個我一直不願面對的弱點，我現在正更仔細地重做那一節。我也很感謝您提到的參考文獻；我已找到 Brock 那篇文章，它非常有用。能認識一位研究相鄰問題的人，實在是莫大的榮幸，希望日後還能再相遇。若有任何我能幫上忙的地方，請別客氣。謹致問候，李信政。",
    note: "長感謝信：說明緣由→謝具體建議與其影響→謝文獻→表達相識之喜→回饋意願→敬語。'put your finger on…' 精準點出。",
  },

  // ── 請求 email ──
  {
    id: "request-s",
    topic: "請求 email", topicEn: "Request Email",
    length: "短文",
    prompt: "寫一封 3–4 句短 email，禮貌請教授幫你寫推薦信。",
    en: "Dear Professor Lindberg, I'm applying for a doctoral fellowship and would be honoured if you might write me a letter of recommendation. The deadline is 15 March, and I'm happy to send my draft proposal and a summary of our work together. Thank you very much for considering this. Best, Hsin-Cheng.",
    zh: "親愛的 Lindberg 教授，我正在申請一個博士獎助，若您願意為我寫一封推薦信，我將深感榮幸。截止日是 3 月 15 日，我很樂意附上我的計畫草稿與我們合作的摘要。非常感謝您的考慮。祝好，信政。",
    note: "請求信：背景→請求(would be honoured if you might…)→提供協助資訊→致謝。委婉用 might / would。",
  },
  {
    id: "request-l",
    topic: "請求 email", topicEn: "Request Email",
    length: "長文",
    prompt: "寫一封較完整的請求 email，向圖書館特藏部申請調閱一份手稿。",
    en: "Dear Special Collections team, I am a doctoral researcher working on the textual transmission of the early creeds, and I am writing to request access to MS Add. 1742, which your catalogue lists as a fourth-century fragment. My research involves close comparison of readings across witnesses, and this manuscript appears to preserve a variant that is central to my argument. I would need to consult the original rather than the digitized images, as I hope to examine the script and any erasures directly. I can travel to you on any weekday in April and am happy to provide a letter of support from my supervisor, as well as any documentation you require. Could you let me know the procedure for arranging a visit, and whether an appointment is necessary? Thank you for your time and assistance. Yours sincerely, Hsin-Cheng Lee.",
    zh: "親愛的特藏部團隊，我是一名博士研究生，研究早期信經的文本傳遞，來信是想申請調閱 MS Add. 1742——你們的目錄將它列為四世紀殘篇。我的研究需要密切比對各版本的讀法，而這份手稿似乎保存了一個對我論證至關重要的異文。我需要查閱原件而非數位影像，因為我希望直接檢視字體與任何刮改痕跡。我四月任何平日都能前往，並樂意提供指導教授的推薦信及你們所需的任何文件。可否告知安排參訪的流程、以及是否需要預約？感謝您的時間與協助。敬上，李信政。",
    note: "正式請求長信：自我說明→具體請求→為何需原件→可配合的條件→具體提問→敬語。學術調閱信範本。",
  },

  // ── 研究計畫摘要 ──
  {
    id: "abstract-s",
    topic: "研究摘要", topicEn: "Research Abstract",
    length: "短文",
    prompt: "用 3–4 句寫一段研究摘要（問題、做法、貢獻）。",
    en: "This study asks how fixed creeds emerged from the oral confession of the early Church. Drawing on a fresh collation of the manuscript witnesses, it argues that two recensions long thought dependent are in fact independent. The findings call for a revised stemma and, with it, a new account of how creedal language was transmitted. The method offers a model for similar problems in late antique texts.",
    zh: "本研究探問固定的信經如何從早期教會的口傳告白中浮現。透過對手稿見證的重新校勘，本文主張兩個長久被認為彼此依存的傳本其實各自獨立。此一發現要求修訂譜系圖，並隨之提出信經語言傳遞的新說明。其方法為晚期古代文本的類似問題提供了一個範式。",
    note: "摘要四要素：問題→做法(Drawing on…)→主張/發現(it argues that…)→貢獻/意義。現在式為主。",
  },
  {
    id: "abstract-l",
    topic: "研究摘要", topicEn: "Research Abstract",
    length: "長文",
    prompt: "寫一段較完整的研究計畫摘要（背景、空白、問題、方法、預期貢獻）。",
    en: "The creeds of the early Church are among the most studied texts in Christian history, yet a basic question about their formation remains surprisingly unsettled: how did a living, oral confession become a fixed and authoritative formula? Scholarship has long assumed that the shorter recension of the creed in question is an abridgement of the longer one, an assumption that underpins the standard editions and the histories built upon them. Yet that view has never been tested against the complete manuscript evidence. This project supplies that test. Through a full collation of the surviving witnesses, combined with attention to the distinctive vocabulary and theological framing of each recension, it argues that the two are independent witnesses to a common source rather than versions of one another. If the argument holds, the consequences extend well beyond the stemma: they require us to rethink how creedal language was negotiated, remembered, and transmitted across communities. Methodologically, the study models how philology, history, and doctrine can be read together, offering an approach applicable to a range of late antique texts.",
    zh: "早期教會的信經是基督教史上研究最多的文本之一，然而關於其形成的一個基本問題卻出人意料地懸而未決：一個活的、口傳的告白，如何成為固定且具權威的定式？學界長久以來假設所討論信經的較短傳本是較長那本的節縮，這個假設支撐了標準校訂本及在其上建立的歷史。然而這個看法從未對照完整的手稿證據加以檢驗。本計畫提供此一檢驗。透過對現存見證的全面校勘，並關注各傳本獨特的用語與神學框架，本文主張二者是同一來源的各自獨立見證，而非彼此的版本。若論證成立，其後果遠超出譜系圖：它要求我們重新思考信經語言如何在群體間被協商、記憶與傳遞。在方法上，本研究示範語文學、歷史與教義如何能一起閱讀，提供一套可應用於各種晚期古代文本的取徑。",
    note: "計畫摘要長版：研究對象重要性→既有假設→空白(never been tested)→本計畫補上→方法→主張→影響→方法論貢獻。",
  },

  // ── 書評 / 讀書摘要 ──
  {
    id: "review-s",
    topic: "書評摘要", topicEn: "Book Review",
    length: "短文",
    prompt: "用 3–4 句摘要並評價一本你讀過的學術著作。",
    en: "In this book, Williams sets out to trace how Arian controversy reshaped Christian language about God. The great strength of the work is its patient close reading of often-neglected sources. If there is a weakness, it is that the social context occasionally drops out of view. Even so, it remains the most illuminating treatment of the subject I have read.",
    zh: "在這本書裡，Williams 著手追溯亞流爭議如何重塑了基督教關於神的語言。本作的最大優點，是它對常被忽略的史料耐心的細讀。若說有什麼缺點，那就是社會脈絡偶爾從視野中消失。即便如此，它仍是我讀過對此主題最具啟發性的論述。",
    note: "書評框架：作者要做什麼→優點(The great strength is…)→不足(If there is a weakness…)→總評。客觀加肯定。",
  },
  {
    id: "review-l",
    topic: "書評摘要", topicEn: "Book Review",
    length: "長文",
    prompt: "寫一段較完整的書評（主旨、方法、貢獻、不足、總評）。",
    en: "Williams's study sets itself an ambitious task: to show how the Arian controversy was not merely a dispute about doctrine but a crisis in religious language itself. The book proceeds through a series of close readings, moving from the polemical treatises to the liturgical fragments that are too often passed over, and it is in these neglected texts that Williams is at his most illuminating. His central claim — that the controversy forced a new precision on words the Church had used loosely for generations — is argued with real care and is, to my mind, largely convincing. The work is not without limitations. The social and institutional context occasionally recedes, so that ideas can seem to develop in a vacuum, and readers without Greek will find some passages hard going. These are, however, the costs of a book that takes its sources seriously on their own terms. The result is the most searching account of the controversy now available, and it will repay close study by anyone working on the period.",
    zh: "Williams 的研究為自己設下了一個雄心勃勃的任務：證明亞流爭議不只是一場教義之爭，更是宗教語言本身的危機。本書透過一系列細讀展開，從論戰性的論著走向那些太常被略過的禮儀殘篇，而正是在這些被忽略的文本中，Williams 最具啟發性。他的核心主張——這場爭議迫使教會對幾個世代以來鬆散使用的詞語產生新的精確性——論證得極為用心，在我看來大致令人信服。本書並非沒有侷限。社會與制度脈絡偶爾退場，使得觀念彷彿在真空中發展；不諳希臘文的讀者也會覺得某些段落吃力。然而，這些是一本認真對待其史料的書所必須付出的代價。其成果是目前對這場爭議最為深入的論述，凡研究這個時期的人都值得細讀。",
    note: "書評長版：主旨抱負→方法與亮點→核心主張與評價→侷限(not without limitations)→為侷限辯護→總評。先肯定後保留再總評。",
  },

  // ── 比較對照 ──
  {
    id: "compare-s",
    topic: "比較對照", topicEn: "Compare & Contrast",
    length: "短文",
    prompt: "用 3–4 句比較兩個對象的異同。",
    en: "Mark and John tell the same story in strikingly different ways. Where Mark is terse and urgent, hurrying from scene to scene, John lingers, turning each episode into extended reflection. Yet both, in the end, drive towards the cross as the moment of revelation. The contrast is one of style and pace rather than of ultimate purpose.",
    zh: "馬可與約翰以截然不同的方式講述同一個故事。馬可簡練而急切，從一幕匆匆趕往下一幕；約翰則徘徊流連，把每個段落化為綿長的省思。然而二者最終都朝向十字架，視之為啟示的時刻。這種對比是風格與節奏上的，而非終極目的上的。",
    note: "比較框架：總述差異→用 Where A…, B… 對照→指出共同點(Yet both…)→收束差異性質。",
  },
  {
    id: "compare-l",
    topic: "比較對照", topicEn: "Compare & Contrast",
    length: "長文",
    prompt: "寫一段較完整的比較對照（兩對象在數個面向上的異同與評價）。",
    en: "At first glance, the Gospels of Mark and John could hardly be more different, and yet a careful comparison reveals as much convergence as contrast. The most obvious difference is one of tempo. Mark writes with breathless urgency; his favourite word is 'immediately', and scenes collide one after another with little pause for reflection. John, by contrast, slows everything down, allowing a single conversation or sign to unfold across an entire chapter. A second difference is theological idiom: Mark shows us who Jesus is largely through action and reticence, while John states it openly in soaring discourses. And yet beneath these differences lies a shared architecture. Both Gospels are built around a movement towards the cross, which each presents — in its own register — as the decisive disclosure of God. Both, too, demand a response from the reader rather than mere assent. The comparison, then, is instructive precisely because it shows how two authors, working with very different tools, can pursue the same end. To read them side by side is to see that form and meaning are not so easily separated.",
    zh: "乍看之下，馬可福音與約翰福音再不同不過，然而仔細比較會發現，趨同之處不亞於對比。最明顯的差異在於節奏。馬可寫得喘不過氣地急切，他最愛的詞是「立刻」，一幕接一幕相撞，少有停下省思的餘地。相對地，約翰把一切放慢，讓單一的對話或神蹟在整整一章中展開。第二個差異是神學語彙：馬可主要透過行動與緘默讓我們看見耶穌是誰，約翰則在高昂的論述中直接道出。然而在這些差異之下，藏著共同的結構。兩部福音都圍繞著朝向十字架的運動而建構，各自以其特有的語調，將之呈現為神的決定性彰顯。二者也都要求讀者回應，而非僅僅同意。因此這項比較之所以有啟發，正因它顯示兩位作者如何以截然不同的工具追求同一個目的。並列而讀，便會看見：形式與意義並不那麼容易分開。",
    note: "比較長版：總括(as much convergence as contrast)→差異一(tempo)→差異二(idiom)→共同結構(beneath these differences)→評價與啟發。用 by contrast / And yet 銜接。",
  },

  // ── 摘要他人論點 ──
  {
    id: "summary-s",
    topic: "摘要論點", topicEn: "Summarizing an Argument",
    length: "短文",
    prompt: "用 3–4 句客觀摘要某位學者的論點（不加自己評價）。",
    en: "Brown argues that late antique holy men gained authority precisely because they stood outside ordinary social structures. As outsiders, he suggests, they could arbitrate disputes that insiders could not. Their power, on this account, was a function of their detachment. The argument reframes asceticism as a social role rather than a purely spiritual one.",
    zh: "Brown 主張，晚期古代的聖人之所以獲得權威，正因為他們站在一般社會結構之外。他認為，作為局外人，他們能仲裁局內人無法處理的紛爭。依此說法，他們的權力來自於他們的超然。這個論點把禁慾重新框定為一種社會角色，而非純粹屬靈的角色。",
    note: "客觀摘要：用 argues/suggests/on this account 等報導動詞；不放入自己立場；末句點出論點的意義。",
  },
  {
    id: "summary-l",
    topic: "摘要論點", topicEn: "Summarizing an Argument",
    length: "長文",
    prompt: "用一段話完整摘要某學者論點的脈絡、主張、論據與意涵（仍保持客觀）。",
    en: "In a now-classic essay, Peter Brown sets out to explain a puzzle: why did the holy man become such a central figure in the society of late antiquity? His answer turns on the notion of the outsider. Brown observes that the ascetic deliberately severed the ordinary ties of kinship, property, and patronage that bound everyone else into networks of obligation. Precisely because he stood apart from these networks, Brown argues, the holy man could act as a neutral arbitrator, settling disputes and brokering favours in a way that no embedded local figure could. His authority, on this reading, was not despite his marginality but because of it. Brown supports the claim with cases drawn from Syrian and Egyptian sources, showing the holy man functioning as judge, patron, and broker. The wider implication, which Brown draws out carefully, is that asceticism must be understood as a social role with concrete functions, and not merely as an interior spiritual discipline. The essay thus reframes a religious phenomenon in social terms without reducing it to them.",
    zh: "在一篇如今已成經典的文章中，Peter Brown 著手解釋一個謎題：為何聖人在晚期古代社會中成為如此核心的人物？他的答案繫於「局外人」這個概念。Brown 觀察到，禁慾者刻意切斷了把其他人都綁進義務網絡的那些尋常聯繫——親屬、財產與恩庇。Brown 主張，正因為他置身這些網絡之外，聖人才能作為中立的仲裁者，以任何嵌在地方關係中的人都無法做到的方式調解糾紛、斡旋人情。依此解讀，他的權威不是儘管邊緣、而正是因為邊緣。Brown 以敘利亞與埃及史料中的案例支持此說，顯示聖人作為法官、恩主與仲介的功能。Brown 仔細推導出的更廣意涵是：禁慾必須被理解為一種具有具體功能的社會角色，而不只是一種內在的屬靈操練。這篇文章因而以社會的語彙重新框定了一個宗教現象，卻未將它化約為社會。",
    note: "客觀長摘要：點出問題→核心概念→論點推導(Brown argues/observes)→論據(supports with cases)→更廣意涵→末句評其分寸(without reducing it to them)。全程報導動詞、不表自己立場。",
  },

  // ── 學習反思 ──
  {
    id: "reflect-s",
    topic: "學習反思", topicEn: "Reflection",
    length: "短文",
    prompt: "用 3–4 句反思這學期/這段時間的學習收穫與不足。",
    en: "Looking back on this term, I've grown more confident in reading unvocalized manuscripts than I expected. What I underestimated was how much patience textual criticism demands. If I were starting again, I'd build my vocabulary base earlier. Still, I leave with a clearer sense of the kind of scholar I want to become.",
    zh: "回顧這學期，我在閱讀未標母音的手稿上，變得比預期更有信心。我低估的是，文本批評需要多少耐心。若能重來，我會更早打好我的詞彙基礎。儘管如此，我帶著對自己想成為哪一種學者更清晰的認識離開。",
    note: "反思框架：回顧成長(Looking back…)→低估之處(What I underestimated…)→若重來(If I were starting again…)→收束(Still, I leave with…)。",
  },
  {
    id: "reflect-l",
    topic: "學習反思", topicEn: "Reflection",
    length: "長文",
    prompt: "寫一段較完整的學習反思（具體事件、學到什麼、如何改變你、下一步）。",
    en: "When I began this term, I assumed that progress in my field would come mainly from reading more — more sources, more secondary literature, more languages. Looking back now, I think that assumption was only half right. The turning point came when a supervisor returned a draft chapter covered in queries, not about my conclusions but about the evidence I had quietly skipped over. It was an uncomfortable moment, but a clarifying one: I realized that I had been collecting material faster than I could actually weigh it. Since then I have worked more slowly and, I think, more honestly, learning to sit with a difficult reading rather than explain it away. The change has been as much about temperament as technique. I am still impatient by nature, and the discipline does not come easily. But I leave the term with a clearer picture of the scholar I want to become — one who is willing to be slowed down by the evidence — and with concrete habits, like keeping a collation log, that I intend to carry into next year.",
    zh: "這學期剛開始時，我以為在我這個領域的進步，主要來自讀得更多——更多史料、更多二手文獻、更多語言。如今回頭看，我想那個假設只對了一半。轉捩點發生在一位指導老師把一份草稿章節還給我，上面滿是疑問——不是針對我的結論，而是針對我悄悄略過的證據。那是個令人不安卻使人清醒的時刻：我意識到，我蒐集材料的速度，遠快於我真正能衡量它們的速度。自那之後，我做事更慢了，我想也更誠實了，學會與一個棘手的讀法共處，而非把它解釋掉。這個改變關乎性情，不亞於關乎技術。我天性仍然急躁，這份紀律得來不易。但我帶著對自己想成為哪一種學者更清晰的圖像離開這學期——一個願意被證據放慢腳步的學者——也帶著像「校勘日誌」這樣具體的習慣，打算把它帶進明年。",
    note: "反思長版：原本的假設→轉捩事件(The turning point came when…)→領悟→改變(Since then…)→性情層面→坦承未竟→收束與下一步。敘事＋自省。",
  },
];

export function passagesByLength(length: PassageLength): PassageItem[] {
  return EN_PASSAGES.filter((p) => p.length === length);
}
export function passageTopics(): string[] {
  return [...new Set(EN_PASSAGES.map((p) => p.topic))];
}
export function passagesForClient() {
  return EN_PASSAGES;
}
