---
name: scripture-tripitaka
description: 佛教大藏經（/tripitaka）—— 把 CBETA 的《大正新脩大藏經》與《漢譯南傳大藏經》全文收進站內，並掛上梵／巴利／藏原典對照。含 CBETA TEI P5 的解析規矩（缺字、異文、夾註、偈頌、悉曇）、佛典「段」該怎麼切與怎麼編號（學界對此沒有共識，本站定調為大正藏頁欄行）、SuttaCentral 平行經目的對接與其陷阱、以及三級對照來源的分辨。Use when 要補抓／重解析某部經、要新增一種原文對照（梵本、藏譯、漢譯南傳、白話）、要改 /tripitaka 的頁面或 schema、要處理某部經解析成 0 段或字數異常少、或使用者提到「大藏經」「CBETA」「阿含」「巴利對照」。與 [[scripture-canon]] 的基督教區平行，同掛在 /scripture-canon 之下。
---

# 佛教大藏經 /tripitaka

`/scripture-canon` → 佛教 → **佛教大藏經**。與基督教區的八個子工具、希臘羅馬的
《希臘羅馬大藏經》平行並列。

## 現況（2026-08-28 建置完成）

| | |
|---|---|
| 收錄 | 大正藏 T01–T55 ＋ T85（2,471 部）／漢譯南傳 N01–N70（83 冊） |
| 規模 | **2,554 部・97,879,719 字・1,014,824 段**，零空檔 |
| 分類 | 大正藏 31 部門（按經號區間）＋南傳 8 分部（按**冊號**） |
| 原文對照 | 見下表 |

### 原文對照現況（去重後的實際落地數）

| 層 | 區塊 | 行 | 掛在漢文段 | 涵蓋 | 來源 |
|---|---|---|---|---|---|
| 巴利原文 | 4,582 | 536,901 | 1,755 | 20 部 | SuttaCentral 逐段本 |
| 漢譯南傳 | 1,974 | 63,916 | 1,395 | 17 部 | CBETA N 部（元亨寺版） |
| 梵文原文 | 94 | 15,117 | 94 | 7 部 | GRETIL |
| 藏文原文 | 29 | 4,871 | 29 | 3 部 | 84000 翻譯記憶（TMX） |
| 平行經目 | 23,321 筆 | — | 87% 對到段落 | 172 部 | SuttaCentral parallels |
| 漢梵巴詞條 | 29,930 組 | — | 逐詞 | 142 部 | CBETA `<cb:tt>` |
| 大正藏原註 | 1,597 條 | — | 99.8% 貼回段落 | 21 部 | 大正藏編者 1924–34 |

⚠ 建置時的 `--build` 輸出是**去重前**的筆數（同一部巴利經若是多部漢文經的
平行本會被重複計，例如巴利那層報 8,309 筆但實際落地 4,582 個區塊）。
對外講數字要用上表，不要抄 stdout。
| 存放 | 目錄進 Supabase（2,554 列）；正文 JSONL 在 Drive `_tripitaka/`，R2 `tripitaka/` 為線上後備 |

## 🚨 段怎麼切、怎麼編號（使用者定調，別再改）

**漢文佛典沒有聖經那樣的章節制。**章節是 13 世紀 Langton、16 世紀 Estienne
硬加的內容邏輯切分，全教會統一採用；佛典從來沒有過這樣一次性的統一編碼工程。

本站的定調：

```
段的鍵 ＝ 該段第一行的大正藏頁欄行     T09n0262_p0008a13
段的邊界 ＝ CBETA 新式標點本的 <p>／<lg>（編輯判斷，非原典自帶，凡例須註明）
```

行號是版面座標不是文本單位（換一個藏本就對不上），但它是學界引用漢文佛典的
**唯一標準**，所以拿來當鍵與引用式都對，拿來當跨語言對齊鍵則錯（梵藏本沒有
大正藏頁碼）。

### 對齊軸是分層的

```
L1 卷／會    <milestone unit="juan"> / <cb:juan fun="open">
L2 品        <cb:div type="pin">     ← 跨語言主對齊層（梵 parivarta／藏 le'u）
L3 依文類分歧
     阿含類 → 經  <cb:div type="jing">          雜阿含 1,355 經
     論頌類 → 頌  <lg>/<l>                      中論 27 品 362 偈頌組
     律部   → 條                                 有編號共識
     大乘經 → 品以下無共識                       只能對到品
L4 引用座標（顯示用，不當對齊鍵）
     漢 大正頁欄行 p.0008a13ㅤ巴 PTS／SC segment idㅤ藏 德格 folio
```

### 對照來源分三級，UI 分色，**絕不可混為一談**

| 來源 | 是什麼 | 色 |
|---|---|---|
| `taisho-equiv` | 大正藏編者（1924–34）在腳註標的巴利對應，最權威 | 綠 |
| `cbeta-term` | CBETA 在專名旁附的梵巴原語形，逐詞非逐段 | 藍 |
| `suttacentral` | SuttaCentral 跨語系平行經目 | 靛 |
| `site` | 無現成資料時本站自行切分，屬編輯判斷 | 琥珀 |

## 檔案

```
scripts/tripitaka_cbeta.py          CBETA TEI P5 → 目錄 rows ＋ 逐段 JSONL ＋ 詞條 ＋ 對應註
scripts/tripitaka_parallels.py      SuttaCentral 平行經目 → 對照 rows
scripts/tripitaka_original_text.py  平行經目的「指標」→ 巴利原典全文（SuttaCentral）
scripts/tripitaka_sanskrit.py       梵文原典（GRETIL）逐品掛上，含品數對齊閘
scripts/tripitaka_nanchuan.py      漢譯南傳（元亨寺版）掛成對照欄，含經數硬閘
scripts/tripitaka_tibetan.py       藏譯原典（84000 TMX）逐章掛上，含章數對齊閘
scripts/tripitaka_db.py             建表 SQL／目錄入庫／Drive 同步／R2 上傳
scripts/sql/tripitaka_schema.sql    DDL（Management API token 掛掉時手動貼 Dashboard）
scripts/tests/test_tripitaka_*.py   純函式測試（54 個，鎖住下列所有陷阱）

data/tripitaka/divisions.ts         部類標籤／配色／語言與來源分級（顯示層）
server/utils/tripitaka.ts           file-backed 讀取器（本機 Drive → R2 → null）
server/api/tripitaka/{works,work,stats}.get.ts
pages/tripitaka/{index,[division]}.vue ＋ pages/tripitaka/w/[id].vue
pages/scripture-canon/buddhism.vue
components/ParallelChips.vue
```

本機快取（可重下，不進 git 不進 Drive）：

```
C:/tmp/cbeta/xml-p5/       cbeta-org/xml-p5 sparse clone（T 829M ＋ N 55M）
C:/tmp/cbeta/gaiji.json    CBETA 缺字表 31,659 筆
C:/tmp/cbeta/sc-data/      suttacentral/sc-data sparse clone（巴利逐段本 7,288 部）
C:/tmp/cbeta/out/          產出的 JSONL（401 MB），同步到 Drive 後即可刪
```

## 常用指令

```bash
python scripts/tripitaka_cbeta.py --inspect T/T02/T02n0099.xml   # 單檔檢視
python scripts/tripitaka_cbeta.py --build-all --canon T,N        # 全藏 → JSONL
python scripts/tripitaka_cbeta.py --catalog --out C:/tmp/cbeta/catalog.json

python scripts/tripitaka_parallels.py --audit    # 對得上多少（不寫檔）
python scripts/tripitaka_parallels.py --build
python scripts/tripitaka_original_text.py --pali
python scripts/tripitaka_sanskrit.py --audit      # 梵品數 vs 漢品數（不寫）
python scripts/tripitaka_sanskrit.py --build
python scripts/tripitaka_nanchuan.py --audit      # 驗五尼柯耶經數（不寫）
python scripts/tripitaka_nanchuan.py --build
python scripts/tripitaka_tibetan.py --probe toh113  # 報某 Toh 的書名與章數（建表用）
python scripts/tripitaka_tibetan.py --audit
python scripts/tripitaka_tibetan.py --build

python scripts/tripitaka_db.py --push            # 目錄 → Supabase（走 PostgREST）
python scripts/tripitaka_db.py --sync-drive --push-r2
```

## 🚨 踩過的坑（每一個都是「看起來成功的失敗」）

全部由 `scripts/tests/test_tripitaka_*.py` 鎖住。動這批程式前先讀這一節。

1. **`<cb:div type="equiv-notes">` 在 cb: 命名空間下。**
   用 `root.iter("{TEI}div")` 找會**靜默回 0 筆**、不報錯。要比對 local name。
   雜阿含的 917 條巴利對應就是這樣整批消失過。

2. **南傳的經號是「冊內序號」。**
   `N01n0001` 與 `N02n0001` 是兩部不同的書。分部只能按**冊號**，
   作品 id 也必須帶冊號（`N09n0001`）。按經號分部會把整套書分錯。

3. **`sa-2.180` 是別譯雜阿含第 180 經，不是雜阿含 2.180。**
   正規式切前綴會把它併進 `sa`，再被「取小數點前」的退路默默對到
   雜阿含第 2 經 —— 而且**會被統計成命中**。必須用已知集號做最長前綴比對。

4. **四部阿含的經號位置各不相同。** 硬套一種會整批對錯：

   | | 經號在哪 | SC 編號式 |
   |---|---|---|
   | T0001 長阿含 | 標題「（一）」 | `da1`–`da30` |
   | T0026 中阿含 | 標題「（二二二）」 | `ma1`–`ma222` |
   | T0099 雜阿含 | `<cb:mulu n="1267">` | `sa1267` |
   | T0100 別譯雜 | 標題，且 div type 是 `other` 不是 `jing` | `sa-2.180` |
   | T0125 增壹阿含 | n 是**品內**序號 | `ea32.2`＝品32經2 |

5. **大正藏標題的漢數字是逐位排列**（二二二＝222、三〇＝30），不是十百進位。
   兩種都要吃。

6. **`t213.4` 的品號不可丟。** 只取 213 會把法句經群（T210／T212／T213 ↔ 巴利
   Dhammapada ↔ 梵文 Udānavarga ↔ 藏譯甘珠爾，本藏最完整的四語對照）
   四千多筆逐品對照全塌成「整部」。段落級命中率會從 87% 掉到 30%。

7. **`<cb:tt>` 在正文中出現時，三種語言會串成一團。**
   「長阿含經Dīrgha-āgamaDīgha-nikāya」。正文只取 `zh-Hant` 那一支。

8. **目錄部的經錄把書目寫成 `<item><title>`，底下沒有 `<p>`。**
   只收 `<p>/<lg>` 會讓整批目錄部解析成 0 段或十幾個字。`cb:jhead` 同理。

9. **對不到段落的對照不要收。**
   律典的 uid 是逐條學處（`lzh-mi-bi-vb-pc12`），對不到段落時全部塌成
   「十誦律 ↔ 巴利律藏」，同一句話重複三萬七千次。那不是對照，是噪音。
   捨棄的 143,763 筆在 `--audit` 輸出中明列，不靜默丟。

10. **原文與漢文不可左右並排。**
    原文那一側是「一整部經」，漢文這一側只是該經的起首段。並排會讓讀者
    以為第 n 段漢文正對第 n 段巴利 —— 漢巴兩本的段落數本來就不一樣。
    故做成可展開區塊，並在區塊內明寫「同源異流的兩個本子，段落非一一對應」。

11. **`t2917A`／`t2917B` 是同號兩本。** 經號有字母後綴，`int()` 會直接炸。

12. **法句經那類在 SuttaCentral 是區間檔名**（`dhp1-20`、`dhp100-115`）。
    單經 uid（`dhp21`）直接查索引會漏掉 1,640 筆，要另建區間索引。

13. **梵漢照品序對齊是本專案最危險的一招。**
    法華梵本 27 品、羅什漢譯 28 品（提婆達多品在梵本併入見寶塔品），照順序對
    會讓第 12 品以後全體位移一格，**而頁面看起來完全正常**。
    `tripitaka_sanskrit.py` 的規矩：品數不合一律拒絕逐品對齊、退回整部層級並
    在 `--audit` 明列；要逐品對就得手寫 `chapter_map`。絕不用「長度差不多就湊」。

14. **GRETIL 的頌號標在偈的末行**（`d e f // MMK_1.2 //`）。
    逐行判品會讓每一品的首半偈被算進上一品 —— 要以偈頌組（`<lg>`）為單位取標記。

15. **不要自編看起來像引用式的行號。** 一度把梵文行號寫成 `MMK_1:3`（自編序號），
    那長得像頌號卻不是。現在只用原書真有的頌號，抓不到就留空。

16. **CBETA 有時不給 div 的 `type`。** 道行般若 T0224 只有第一品標了 `pin`，
    其餘 29 品是空字串 —— 只認 `type=='pin'` 會把整部書判成「無品層」。

17. **法華的梵漢差異有兩處，不是一處。** 我第一版只處理了「提婆達多品併入
    見寶塔品」那一處，寫成「梵 12 起加一」—— 結果尾段**四個品全配錯**
    （陀羅尼、妙莊嚴王、普賢、囑累），而頁面完全正常。
    真相是羅什另把**囑累品移到第 22**、陀羅尼排到第 26；梵藏本則陀羅尼在 21、
    囑累在最末 27。正確對照見 `tripitaka_sanskrit.REGISTRY` 的 T0262 那一筆
    （藏譯 Toh 113 章序與梵本一致，`tripitaka_tibetan` 直接取用同一張表，
    不各抄一份）。教訓：**手寫的對照表本身也要驗**，閘只擋得住數量不符，
    擋不住數量相同但次序不同。

18. **84000 TMX 的「This concludes … the Nth chapter」是章尾不是章首。**
    當成章首會讓章數翻倍且內容錯位。

19. **漢譯南傳的五尼柯耶編號方式互不相同**，且相應部有三個疊在一起的陷阱：
    ① 相應號**每冊重新編**（N17 從「第八 聚落主相應」起，跨篇又跳回
       「第三 念處相應」）→ 不能讀標題序數，要跨六冊照文件順序連號。
    ② N14 把相應與其下的品**放在同一深度**，父子鏈是斷的 → 不能用
       parent 往上找，改用「文件順序上最近的前一個相應」。
    ③ 判別相應要看**標題結尾是不是「相應」**，看深度會把「食品」也算成相應。
    任一條沒處理好，1,691 經整批位移而頁面看不出來。
    閘：長部必須恰好 34 經、中部 152 經、相應部 56 相應 —— 都是巴利藏的定數，
    對不上就整個尼柯耶不掛。

20. **大正藏行號不唯一。** 同一行可以起頭好幾段 —— 全藏 **65,483 段（6.5%）、
    672 部**如此。行號是段的*引用式*（使用者定調，不改），但不能當鍵：
    拿它 join 對照／詞條，同行的段會互相串；當 DOM anchor 會出現重複 id。
    故每段有兩個欄位：

    | 欄 | 是什麼 | 用途 |
    |---|---|---|
    | `seg` | 大正藏行號 `T02n0099_p0001a06` | 顯示與引用，允許重複 |
    | `uid` | 同行第二段起加 `.2`／`.3` | 對照／詞條／anchor 的**唯一鍵** |

    DB 的 `tripitaka_parallels.seg_uid` 存的是 uid，不是 seg。

## 尚未完成（誠實列出，別當成已完成）

- **梵文原文只完成 4 部**。GRETIL 有 194 部佛教梵本，已接的是中論（27 品，
  頌號 MMK 1.1 逐頌可引）、法華（27 品，含手寫品對照表）、方廣大莊嚴經（27 品）、
  華嚴入法界品。另有 6 部被對齊閘擋下（辯中邊論 5 vs 7、大乘莊嚴經論 20 vs 24、
  菩提行經 10 vs 8、寶性論、道行般若 32 vs 30、佛所行讚），這些是**真的**梵漢
  分品不同，要逐部手寫 `chapter_map` 才能對，不可自動化。REGISTRY 待擴充。
- **藏文原文只完成 3 部**（法華 27 章、心經、藥師）。來源是
  **84000/data-translation-memory** 的 TMX（按 Toh 號命名的藏英逐句對齊，
  383 部）—— 注意 84000/data-tei 是**英譯**，藏文只在術語表，不能拿來當正文源。
  多數 Toh 的 TMX 英文側**沒有章標記**（解深密、維摩詰都是平鋪句段），
  漢本有品時會被閘擋下，要逐部手寫 `chapter_map` 才能對。
  Esukhia/derge-kangyur 有完整德格版但按函冊葉碼編排且已封存，暫不採用。
- **漢譯南傳只接了三部尼柯耶**（長部 34 經、中部 152 經、相應部 56 相應
  1,691 經，皆通過經數硬閘）。**增支部與小部尚未接** —— 增支部的「集」號不在
  標題層級裡，得另定判別法；小部各書結構互異。5,166 筆巴利對應因此查不到
  漢譯南傳。
- **繁中白話**。尚未起跑。走既有 Gemini→NVIDIA→Haiku 引擎（見
  [[feedback_engine_nvidia_no_haiku]]），量大，宜逐部類分批。
- **T56–T84 日本撰述部**。CBETA 未提供 XML，非本站遺漏，凡例已註明。
- **律部的條級對齊**。SC 有逐條學處編號，CBETA 的目錄樹沒有可對的鍵；
  要對上得自建「廣律條號 → 段」索引。
- **Supabase 建表**。2026-08-28 當下 `SUPABASE_ACCESS_TOKEN`（Management API
  那把）已失效回 403，DDL 跑不了。SQL 已備在 `scripts/sql/tripitaka_schema.sql`，
  在 Dashboard SQL Editor 貼一次即可；資料寫入走 PostgREST（service role key
  正常），不需要那把 token。

## 相關

- 體例上與 [[hellenika-canon]]（希臘羅馬大藏經）、[[project_dazangjing]]
  （基督教大藏經）並列 —— 三者都是替一個傳統做藏經式編纂，但佛教這一套
  **本來就有**藏經體例，是唯一「照抄既有體例」而非「補做」的一區。
- 譯名一律過 [[translation-glossary]]；佛教 119 詞已入庫。
- 大檔存放遵守 [[feedback_r2_small_derivatives_only]] 與
  [[feedback_supabase_no_storage]]：正文絕不進 DB。
