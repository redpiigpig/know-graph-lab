---
name: hellenika-fragments
description: 希臘羅馬大藏經（/hellenika）的殘篇綴輯與敵證還原 — 全書 250 種裡近四成的原書已佚，只活在別人的引文裡。本 skill 處理兩種：①殘篇（`status: fragment`）——查標準殘篇集定編號（PEG／M–W／DK／SVF／FGrHist／Kern-OF／Des Places／Fontenrose／Graf–Johnston）、確定轉引者、填 `via` 與 `extent`；②敵證（`status: hostile`）——把異教原文從基督教作家的駁論中析出，按直引／轉述／敵意框架三級分辨，並標明使用限制。Use when 要替某條殘篇補編號或轉引來源、要處理塞爾蘇斯／波菲利／尤利安／瓦羅這類只存於敵手引用的書、要判斷一段引文能不能當異教原話用、要新增殘篇類條目。體例底層見 [[hellenika-canon]]。
---

> 🏛️ 本 skill 屬《希臘羅馬大藏經》，與《基督教大藏經》無關。

# 殘篇與敵證 Skill

《希臘羅馬大藏經》最特別的處境：**近四成條目的原書不存在**。殘篇 89、敵證 9，合計 98／250。這不是資料不全，是這個宗教被取代之後的真實狀態——而本藏經的立場是「殘缺是內容的一部分」（[[hellenika-canon]] §1 第三條）。

本 skill 的工作只有一句話：**把「這段話從哪裡來、可信到什麼程度」查實並寫進資料檔。**

---

## A. 殘篇（`status: fragment`）

### A1. 必填三件

| 欄 | 內容 | 例 |
|---|---|---|
| `via` | 轉引來源，具名到書 | `'普羅克洛斯《文選》摘要'`／`'波菲利《論戒食》大段引錄'` |
| `extent` | **原書**規模而非殘存量 | `'傳為 11 卷'`／`'原 15 卷'` |
| `era` | 原著年代，非殘篇集出版年 | `'約前 7 世紀'` |

`via` 不可寫「後人引述」「諸家轉引」這種空話。查不到具名轉引者，就代表這一條還沒查完，不要先寫進去。

### A2. 各卷對應的標準殘篇集

查編號一律以現行標準本為準，舊編號若仍通用則雙標（格式 `PEG fr. 1 = Kern OF 60`）。

| 材料 | 標準本 | 縮寫 | 涉及卷次 |
|---|---|---|---|
| 史詩循環、俄耳甫斯殘篇 | Bernabé, *Poetae Epici Graeci* | **PEG** | Ε、Α |
| 俄耳甫斯（舊編，仍常見） | Kern, *Orphicorum Fragmenta* (1922) | **OF** | Α、Λ |
| 婦女名錄／赫西奧德殘篇 | Merkelbach–West, *Fragmenta Hesiodea* | **M–W** | Ζ |
| 前蘇格拉底 | Diels–Kranz, *Die Fragmente der Vorsokratiker* | **DK** | Φ、Υ（色諾芬尼、赫拉克利特、巴門尼德、恩培多克勒） |
| 斯多噶 | von Arnim, *Stoicorum Veterum Fragmenta* | **SVF** | Φ |
| 早期譜系家、地方史家 | Jacoby, *Die Fragmente der griechischen Historiker* | **FGrHist** | Α（阿庫西勞 =2、費瑞居德 =3）、Ν（雅典地方史 =323a–334） |
| 迦勒底神諭 | Des Places, *Oracles Chaldaïques* | **OC** | Υ |
| 德爾菲神諭 | Fontenrose, *The Delphic Oracle*（Q／H／L 三系編號）；Parke–Wormell | **PW / Fontenrose** | Τ |
| 金葉片 | Graf–Johnston, *Ritual Texts for the Afterlife*；Bernabé–Jiménez San Cristóbal | **GJ / BJ** | Λ |
| 波菲利《駁基督徒》 | Becker (2016) 為現行；Harnack (1916) 舊編 | **Becker / Harnack** | Ψ |
| 瓦羅《神事古事記》 | Cardauns, *Antiquitates rerum divinarum* | **Cardauns** | 羅馬卷 II |
| 悲劇殘篇 | Radt, *Tragicorum Graecorum Fragmenta* | **TrGF** | Ρ |
| 抒情詩殘篇 | Page, *Poetae Melici Graeci*；Voigt（莎孚） | **PMG / Voigt** | Ο |

> Fontenrose 的分級（Q＝quasi-historical、H＝historical、L＝legendary）本身就是可信度判準，Τ 卷收德爾菲神諭時**一併記下級別**，讓讀者知道那則神諭有多可能是後人追造的。

### A3. 公有領域英譯（可直接進逐段對照管線）

殘篇集本身多為現代校本、有版權；但下列舊譯是 PD，可用來做對照欄底本：

| 譯本 | 涵蓋 | 用於 |
|---|---|---|
| Evelyn-White, *Hesiod, the Homeric Hymns and Homerica* (Loeb, 1914) | 赫西奧德全部＋荷馬詩頌＋**史詩循環殘篇** | Α、Β、Ε、Ζ、Ο、Π |
| Murray, *Iliad* (1924)／*Odyssey* (1919) | 荷馬 | Γ、Δ |
| Frazer, *Apollodorus: The Library* (1921) | 書庫＋節要，註釋極豐 | Ζ、Θ |
| Jones, *Pausanias: Description of Greece* (1918–35) | 希臘志全 10 卷 | Ξ |
| Godley, *Herodotus* (1920–25) | 歷史全 9 卷 | Ν、Τ |
| Oldfather, *Diodorus Siculus* (1933–) | 歷史叢書神話部 | Ξ |
| Taylor, *The Mystical Hymns of Orpheus* (1792/1824)、*Sallust on the Gods and the World* (1793) | 俄耳甫斯詩頌、薩盧斯提烏斯 | Ο、Φ |
| Mead, *Thrice-Greatest Hermes* (1906) | 赫密士文集 | Υ |
| MacKenna, *Plotinus: The Enneads* (1917–30) | 九章集 | Φ |
| W. C. Wright, *The Works of the Emperor Julian* (Loeb, 1913–23) | 尤利安全集含《駁加利利人》殘篇 | Ο、Φ、Ψ |
| Conybeare, *Philostratus: Life of Apollonius* (1912) | 阿波羅尼烏斯傳 | Χ |
| Chadwick 之前的 Crombie, *Origen Against Celsus* (ANF vol. 4) | 塞爾蘇斯《真道》的載體 | Ψ |
| Frazer, *Ovid's Fasti* (1931)／Miller, *Metamorphoses* (1916) | 奧維德 | 羅馬卷 III、希臘卷 Α |
| Fairclough, *Virgil* (1916) | 埃涅阿斯紀 | 羅馬卷 I |
| Perrin, *Plutarch's Lives* (1914–26) | 努瑪傳、羅慕路斯傳、忒修斯傳 | 羅馬卷 I／II、希臘卷 Θ |

> 1930 年之前的 Loeb 在美國屬公有領域；之後的卷不要拿。ANF／NPNF 全套 PD（站上已有，見 [[scripture-fathers]]），教父引錄的異教殘篇可直接從那裡取。

### A4. 綴輯條目的寫法

有些條目沒有單一原書，是編者從各家綴成的（如 Β 卷「丟卡利翁洪水」、Θ 卷「忒修斯諸傳」）。這類條目：

- `author` 寫 `'綴輯（品達、阿波羅多洛斯、奧維德等）'`，**具名列出主要來源**
- `title_orig` 用學界通用的英文題名（`'The Deluge of Deukalion'`），不要硬造希臘文書名
- `status: 'fragment'`
- `intro` 必須說明「此說散見諸家而無專書，本卷綴輯」——不要讓讀者以為古代有這麼一本書

---

## B. 敵證（`status: hostile`）

### B1. 為什麼要另立一級

有幾部異教最重要的書，今天只活在想消滅它們的人寫的駁論裡：

| 原書 | 存於 | 保存比例 |
|---|---|---|
| 塞爾蘇斯《真道》（約 178） | 奧利金《駁塞爾蘇斯》八卷（約 248） | 約七成逐字，**且大致保持原書順序** |
| 波菲利《駁基督徒》（原 15 卷） | 優西比烏、耶柔米、馬卡里烏斯等零星引用 | 極少；公元 448 年遭下令焚毀 |
| 希耶羅克勒斯《愛真理者》（303） | 優西比烏《駁希耶羅克勒斯》 | 少量 |
| 尤利安《駁加利利人》（362–363） | 亞歷山卓的區利羅《駁尤利安》 | 約首卷三分之一 |
| 瓦羅《神人事物古事記》（前 47，神事 16 卷） | 奧古斯丁《上帝之城》卷四至七 | 綱目＋大量引文，**但依奧古斯丁的論戰順序重排** |
| 各密教的口令與儀節 | 克萊門《勸勉希臘人》、菲爾米庫斯《論異教宗教之謬》 | 為揭穿而詳述，細節反而最完整 |

保存比例天差地遠，可信度也是。**這一級不是「殘篇的一種」，它有自己的問題**：材料經過敵手的選擇、切割與重排。

### B2. 三級分辨（處理任何敵證條目時逐段判定）

| 級 | 判準 | 可否當異教原話 |
|---|---|---|
| **一‧直引** | 引述動詞（φησί／「他寫道」）＋第一人稱／原作語域；奧利金常標「塞爾蘇斯說」並隨即逐句反駁 | ✅ 可，但仍須標 `via` |
| **二‧轉述** | 間接引語、敵手壓縮後的摘要；常見「他的意思不過是」「他們主張」 | ⚠️ 須在 `intro` 中標明為轉述，不得引為原文 |
| **三‧敵意框架** | 駁斥者自己的刻畫、動機推測、修辭羞辱 | ❌ **絕不作為異教內容入藏** |

實務上：
- **奧利金**逐句引後逐句駁，一二級界線清楚，是最好處理的一部。
- **區利羅**大量壓縮，二級佔比高。
- **奧古斯丁引瓦羅**最麻煩——引文本身多屬一級，但**編排順序完全是奧古斯丁的**，不能據以還原瓦羅原書結構。羅馬卷 II 的瓦羅條目 `intro` 已載明此點，不要拿掉。
- **菲爾米庫斯**的儀節描述屬一級但帶強烈醜化，取儀節、棄評價。

### B3. 條目寫法

```ts
{
  title_zh: '真道',
  status: 'hostile',
  via: '奧利金《駁塞爾蘇斯》（約公元 248 年）逐段引錄',   // 必填，具名到書並記年代
  intro: '……奧利金七十年後為駁斥而逐段引錄，使原書得以幾乎完整還原——'
       + '這是「敵證」層最典型的個案。',                  // 必須交代保存機制
}
```

`intro` 的三件事，缺一不可：①原書是什麼、②誰為什麼引它、③還原到什麼程度。第三點決定讀者能不能拿它當證據用。

### B4. 敵證與續典的交叉

菲爾米庫斯《論異教宗教之謬》既是拉丁文（`track: 'latin'`）又是敵證（`status: 'hostile'`）。這種雙標是允許的，版面會同時顯示玫瑰色圓點與「續」標。

跨卷收錄時擇一為正文、另一列互見（`seealso`），不要兩邊都放全文：
- 菲爾米庫斯：正文在希臘卷 **Λ 祕儀書**（儀節資料最有價值處），羅馬卷 VI 互見
- 敘馬庫斯《第三陳情》：正文在**羅馬卷 VI**，希臘卷 Ψ 互見

---

## C. 常見錯誤

1. **把殘篇集的出版年寫進 `era`。** `era` 是原著年代。Bernabé 1987 不是史詩循環的年代。
2. **`via` 寫成「見於古代文獻」。** 沒具名＝沒查完。
3. **拿三級敵意框架當異教說法。** 例：奧利金說塞爾蘇斯「像個醉漢一樣胡言」——這是奧利金，不是塞爾蘇斯。
4. **漏標 `status`。** 預設值是 `whole`，漏標等於宣稱它完整傳世。
5. **替綴輯條目硬造希臘文書名。** 沒有這本書就不要給它書名。
6. **用 1930 年後的 Loeb 譯文。** 有版權。

---

## D. 待辦

- ⏳ 全部 89 條 `fragment` 尚未填標準殘篇集編號（PEG／M–W／DK／SVF／FGrHist…）。建議按卷推進，Ε 循環補遺與 Ζ 列祖傳優先（編號體系最成熟）。
- ⏳ Τ 卷德爾菲神諭尚未附 Fontenrose 分級。
- ⏳ Λ 卷金葉片尚未附 Graf–Johnston 編號與出土地逐片對照。
- ⏳ 9 條 `hostile` 的 `intro` 已寫，但尚未逐段做 §B2 三級標註（那需要取原文，屬下一階段）。
