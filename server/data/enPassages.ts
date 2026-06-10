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
