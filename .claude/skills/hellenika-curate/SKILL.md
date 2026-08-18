---
name: hellenika-curate
description: 希臘羅馬大藏經（/hellenika）的逐卷策展 — 三件事：①完整性核對（拿標準參考書把某一卷該有而漏掉的文獻找出來；本藏經的語料是封閉且已編目的，所以工作是「對表補漏」而非「上網找書」，這一點與基督教大藏經的普查根本不同）②書目補全（新條目的欄位規格）③`intro` 撰寫（100–200 字，有固定四件事與明確禁忌）。另含逐卷完整性檢查表與該卷的權威參考書。Use when 要把某一卷的書目補到完整、要替條目寫或改 intro、要檢查某卷有沒有漏收、要決定某部書該不該入藏、要做全書的 intro 補寫批次。體例底層見 [[hellenika-canon]]，取源見 [[hellenika-fragments]]／[[hellenika-epigraphy]]。
---

> 🏛️ 本 skill 屬《希臘羅馬大藏經》，與《基督教大藏經》無關。

> ⚙️ LLM 一律 Gemini → NVIDIA → Haiku。見 [[feedback_engine_nvidia_no_haiku]]。中文一律繁體，見 [[feedback_traditional_chinese_only]]。

# 逐卷策展 Skill

## 0. 這部藏經的語料是封閉的——策展方法因此不同

《基督教大藏經》要處理的是一個至今仍在生產文獻的宗教，所以它需要「上網普查候選書目」那套。**本藏經不是。**

希臘羅馬宗教文獻是一個**已經停止生產、且被學界徹底編目**的語料庫：史詩循環就那七篇、荷馬詩頌就 33 首、俄耳甫斯詩頌就 87 首、赫爾墨斯文集就 18 篇、埃庇道洛斯治癒銘文就那四石。

所以策展工作是**對表補漏**，不是探索：
1. 拿該卷的權威參考書（§2）列出「本來就該有的清單」
2. 與資料檔比對，找出漏收
3. 逐條判斷該不該收（§3 收錄門檻）
4. 補齊欄位、寫 `intro`

> 這代表：**不要為這部藏經寫「上網搜尋候選書目」的 workflow。** 那會抓回一堆現代研究著作與二手介紹頁，污染書目。要抓的是原典清單，而原典清單在參考書裡，不在搜尋引擎裡。

---

## 1. `intro` 撰寫規範（本 skill 最常用的部分）

100–200 字繁體中文，顯示於卷詳頁右欄。**必須包含四件事，順序不拘**：

| # | 要件 | 說明 |
|---|---|---|
| 1 | **這是什麼** | 內容、體裁、規模。一句話講完 |
| 2 | **為什麼入這一卷** | 它在本藏經的功能位置。這是 `intro` 與百科條目的根本差別 |
| 3 | **一個具體可查證的細節** | 一句原文、一個數字、一個場景。抽象概括讀者記不住 |
| 4 | **存世處境**（非 `whole` 時必寫） | 誰保存的、還原到什麼程度、能不能當證據用 |

### 寫得好的例子（已在資料檔中，可作範本）

> **金葉片**：「折疊塞入死者口中或置於胸前的薄金片，刻著幾行給亡魂的指示與口令：不要喝右邊那泓忘川，要走左邊記憶之泉，並向守衛者說『我是大地與星天之子，但我的族類屬天』。有些直接宣告『你已從人變成神』。這是古代世界唯一一批由信徒本人帶進墳墓的救贖文書，也是異教中最接近『因入教而得永生』的證據，分量極重。」
>
> ——①薄金片＋口令 ②唯一由信徒帶進墳墓的救贖文書 ③兩句原文引語 ④銘文性質已由 `status` 表達

> **真道**：「一位中期柏拉圖派學者對基督教的全面批判：耶穌是私生子與埃及術士、門徒是無知漁夫、復活只有歇斯底里的女人作證、基督徒拒服兵役與公職將使帝國崩解。奧利金七十年後為駁斥而逐段引錄，使原書得以幾乎完整還原——這是『敵證』層最典型的個案，也是本藏經必須另設此標記的原因。」
>
> ——①全面批判＋四項具體指控 ②敵證層典型 ③四項指控即具體細節 ④保存機制與還原程度

### 禁忌

- ❌ **百科式開頭**：「《神譜》是古希臘詩人赫西俄德所作的一部長詩，成書於……」——書目欄位已經寫了作者年代，不要重複
- ❌ **只有讚嘆沒有內容**：「這是希臘宗教史上極為重要的文獻」——重要在哪
- ❌ **把 `note` 抄長**：`note` 是一行提示，`intro` 是說明，兩者內容要互補不重疊（版面會把 `note` 顯示在 `intro` 上方）
- ❌ **抽象概括取代具體**：「反映了古希臘人的宇宙觀」→ 改寫成他們具體怎麼說
- ❌ **拿基督教作參照系來抬高它**：可以做結構對讀（本藏經整個體例就建立在對讀上），但不要寫成「這預示了基督教的……」
- ❌ 簡體字、日文詞、「中間點」用 `・` 而非 `‧`

### 批次補寫

用 Gemini 批次時，prompt 必須帶：該卷 `summary`、該條目全部欄位、上面四要件與禁忌、以及**同卷已寫好的兩三筆作為 few-shot**。逐卷跑而非全書一次跑——卷的功能位置是 `intro` 第二要件的依據，跨卷混在一起會寫散。

輸出一律進 dry-run 檔先看，確認再寫入 `data/hellenika/*.ts`。

---

## 2. 逐卷完整性檢查表與權威參考書

比對時以「本藏經該不該收」為準，不是「該卷有多少篇文獻」——參考書會列出大量本藏經不收的東西（§3）。

| 卷 | 該有的骨架 | 權威參考書 |
|---|---|---|
| Α 神譜 | 赫西俄德本文＋四系異版（俄耳甫斯三種神譜、費瑞居德、阿庫西勞、斯多噶寓意） | West, *The Orphic Poems*；Betegh, *The Derveni Papyrus* |
| Β 人類世代記 | 工作與時日神話段、普羅米修斯三母題、丟卡利翁洪水 | West, *Hesiod: Works and Days* 註釋本 |
| Γ／Δ | 荷馬兩部，不會有遺漏 | — |
| Ε 循環補遺 | 特洛伊循環六篇＋底比斯循環三篇＋拉丁續典 | Bernabé **PEG**；West, *The Epic Cycle* (2013) |
| Ζ 列祖傳 | 列國表＋六大家系＋彙編本三種 | Merkelbach–West **M–W**；Hard, *Routledge Handbook of Greek Mythology* |
| Η 遷徙與建城 | 三大遷徙＋建城詩＋建城神諭 | Malkin, *Religion and Colonization in Ancient Greece* |
| Θ 英雄志 | 赫拉克勒斯五種＋四位英雄＋英雄崇拜銘文 | Gantz, *Early Greek Myth*；Ekroth, *The Sacrificial Rituals of Greek Hero-Cults* |
| Ι 遠征記 | 阿爾戈三種＋卡呂冬 | — |
| **Κ 祭儀法** | 淨罪法、祭曆、祭儀理論三部 | **CGRN 全庫**；Parker, *Miasma*；Lupu, *Greek Sacred Law* |
| **Λ 祕儀書** | 厄琉息斯、俄耳甫斯－酒神、外來密教、敵證四部 | Burkert, *Ancient Mystery Cults*；Graf–Johnston, *Ritual Texts for the Afterlife* |
| Μ 分族記 | 回歸、殖民二部 | Malkin, *Myth and Territory in the Spartan Mediterranean* |
| Ν 城邦紀年 | 立法者與神諭、編年、神意史 | Parker, *Athenian Religion: A History* |
| **Ξ 聖所志** | 保薩尼亞斯＋狄奧多羅斯＋還願／認罪銘文 | Pritchett／Habicht, *Pausanias' Guide to Ancient Greece* |
| **Ο 詩頌集** | 五個年代段各不可缺 | Furley–Bremer, *Greek Hymns*（**兩卷本，本卷最重要的工具書**） |
| Π 箴言 | 農時、德爾菲箴言與七賢、格言詩 | Oikonomides, *Records of the Delphic Maxims* |
| Ρ 受苦者之書 | 抗辯、神的可畏、順服三部（選段而非全本） | Mikalson, *Honor Thy Gods*；Parker, *Polytheism and Society at Athens* |
| Σ 虛空篇 | 歌隊、墓誌、諷刺三部 | Lattimore, *Themes in Greek and Latin Epitaphs* |
| **Τ 神諭書** | 德爾菲、多多納、小亞、西比拉、沉默五部 | Fontenrose, *The Delphic Oracle*；Parke–Wormell；Eidinow, *Oracles, Curses, and Risk* |
| **Υ 啟示書** | 早期異象、柏拉圖末世神話、帝國期文集、召神術 | Copenhaver, *Hermetica*；Majercik, *The Chaldean Oracles* |
| Φ 論神書 | 要理提綱＋六個學派段 | Gerson (ed.), *The Cambridge History of Philosophy in Late Antiquity* |
| Χ 聖徒傳與神蹟簿 | 神蹟銘文＋六部聖徒傳 | LiDonnici, *The Epidaurian Miracle Inscriptions*；Fowden, *The Egyptian Hermes* |
| Ψ 爭辯書 | 攻勢、復興、請命三段，按年代 | Wilken, *The Christians as the Romans Saw Them* |
| Ω 終卷 | 最後神諭→關閉編年→最後作品→529 | Chuvin, *A Chronicle of the Last Pagans*（**本卷骨架即出於此**）；Watts, *City and School in Late Antique Athens and Alexandria* |
| 羅馬 I–VI | 見 [[hellenika-epigraphy]] §2 | Beard–North–Price, *Religions of Rome*（**兩卷，羅馬卷總綱**）；Scheid, *An Introduction to Roman Religion* |

---

## 3. 收錄門檻：這部書該不該入藏

**收**：
- 古代原典（含殘篇、敵證中可還原者）
- 儀式現場文本（銘文、紙草、金葉、鉛片）
- 古代作者對本宗教的系統論述（神學、祭儀理論、神話彙編）
- 符合 [[hellenika-canon]] §5 準則的拉丁續典

**不收**：
- ❌ **現代學術著作**——參考書列在本 skill，不進資料檔
- ❌ **純文學而無宗教功能的作品**（多數抒情詩、喜劇、演說）。例外：悲劇的神義論段落入 Ρ，但作**選段**不作全本
- ❌ **後古代的改編與重述**（拜占庭以降、文藝復興神話手冊）
- ❌ **早期基督教文獻本身**——那是 `/dazangjing` 的事。本藏經只在它保存異教材料時（敵證）才收，且收的是被引的那部分
- ❌ **年代晚於 529 年者**。唯一許可的例外是**記述 529 年以前之事的稍晚史源**（阿伽提亞斯記七哲東走、大額我略記本篤伐聖林），這類條目 `era` 要標成書年並註明所記年代
- ❌ **與希臘羅馬宗教無關的東方宗教文獻**。伊西斯、密特拉、大母神只在其**希臘化／羅馬化形態**入藏（希臘文的自述文、羅馬的軍中密特拉），不收埃及本土與伊朗本土材料——那些屬 `/dazangjing` 前藏或別的 portal

**邊界個案的判法**：問「它有沒有在希臘羅馬的宗教生活裡被使用過」。伊西斯自述文用希臘文刻在希臘城市裡供人誦讀 → 收。埃及本土的《亡靈書》→ 不收。

---

## 4. 新條目欄位規格

必填：`title_zh`（過詞庫）、`title_orig`、`author`、`era`、`language`、`note`。
強烈建議：`place`（銘文為必填）、`extent`、`intro`。
條件必填：`status` 非 `whole` 時的 `via`（見 [[hellenika-fragments]]）；`inscription` 的 `place`（見 [[hellenika-epigraphy]]）。

- `title_zh`：**先過 `/translation-glossary`**。不要在資料檔裡自創譯名。
- `title_orig`：希臘文用原文並附拉丁轉寫（`Θεογονία / Theogonia`）；無定本書名的綴輯條目用學界通用英文題名。
- `author`：佚名者寫傳統或社群（`'託名俄耳甫斯'`、`'塞利農特城邦'`、`'各地問卜者'`），不寫「佚名」了事。託名作品寫「託名 X」。
- `era`：成書／定型年代。層積文本（西比拉神諭、魔法紙草、赫爾墨斯文集、俄耳甫斯詩頌）按**現存文本定型年代**歸位，材料更早者在 `intro` 註明。
- `note`：一行，是提示不是摘要。寫最勾人的那一點（「隨葬薄金片，刻著在冥府該說的話」）。
- 插入位置：依 [[hellenika-canon]] §3 兩個時鐘決定，不依所敘事件年代。

---

## 5. 一輪策展的流程

1. 挑一卷。讀該卷 `summary` 與既有條目，確認這一卷「在講什麼」。
2. 開該卷的權威參考書（§2），列出應有清單。
3. 與 `data/hellenika/greek.ts`／`roman.ts` 比對，標出漏收。
4. 逐條過 §3 收錄門檻，剔掉不該收的。
5. 該收的補齊欄位（§4）；非 `whole` 者先跑 [[hellenika-fragments]]／[[hellenika-epigraphy]] 查實 `via`／`place`／編號。
6. 批次補 `intro`（§1），dry-run 先看。
7. 驗：`npx vue-tsc --noEmit -p .nuxt/tsconfig.json`（只看非 `scripts/` 的報錯）＋ `npx vitest run`。
8. 站上目視該卷一遍，確認狀態圓點、`via` 顯示、文字沒溢出（[[feedback_ui_no_text_overflow]]）。
9. commit + push（[[feedback_auto_push]]），並更新 [[hellenika-canon]] §10 現況。

---

## 6. 待辦與建議順序

`intro` 目前寫了 41／250 筆。建議按**讀者最先點進去**的順序補：

1. **Α 神譜**（入口卷，四版對觀是全書招牌）
2. **Λ 祕儀書**（金葉片、厄琉息斯——最有故事、與救贖論對讀價值最高）
3. **Ω 終卷**（結尾的力量在細節，最後神諭、諾努斯、529 三條已寫，其餘待補）
4. **Κ 祭儀法**（中文世界全空白，原創價值最高，但需先跑 [[hellenika-epigraphy]] 取原文）
5. **Ψ 爭辯書**（九條敵證，`intro` 需交代還原程度，工最重但最不能馬虎）
6. 其餘按卷序推進

另：`Ρ 受苦者之書`（7 條）、`Σ 虛空篇`（6 條）、`Μ 分族記`（4 條）、`Ξ 聖所志`（4 條）目前條目偏少，對照 §2 參考書應可再補；`Ο 詩頌集` 的希臘化與帝國期兩段偏薄，Furley–Bremer 兩卷本裡還有可收的祭典聖詩。
