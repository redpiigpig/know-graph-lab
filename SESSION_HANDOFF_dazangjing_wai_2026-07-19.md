# 交接：基督教大藏經「外藏補全 campaign」

**日期**：2026-07-19～20　**分支**：master（已全數 push）
**權威 SOP**：`.claude/skills/scripture-canon/SKILL.md` §8.2 與其「⚠️ 踩雷」清單（本輪已更新第 12 條與外藏 campaign 段落）。本檔只記「這一輪的狀態與交接事項」，方法論以 SKILL.md 為準。

---

## 一、起點與目標

使用者問「除了經藏和前藏，每藏都補齊一百卷了嗎？」→ 實際清點結果：

- **正藏：全數達標** ✅ 古／中／近／今 × 九藏（律論宣函儀詩譯史類）正藏**全部 ≥100**，無一格未滿（經藏依正典封閉法則除外）。
- **外藏：普遍遠未達標** ❌ 除古代較有規模外，多為個位數。

因此本輪開啟 **外藏補全 campaign**，目標同 `VOLUME_TARGETS`：外藏原則上不少於同藏正藏（即朝 100 推進）。節奏＝**一次一格（era × 藏 × 外）穩扎打**。

---

## 二、本輪完成（3 格達標）

| 格 | 進度 | commit |
|---|---|---|
| 中‧律藏外藏 | 23 → **100** ✅ | `6b49fcf5` ＋ 修正 `cef4b0c9`(去德魯茲跨藏重複) |
| 中‧論藏外藏 | 12 → **100** ✅ | （中論外入庫 commit） |
| 近‧論藏外藏 | 13 → **100** ✅ | `9cb00c7b` |
| SKILL.md 紀錄 | — | `0cf664d1` |

各格入庫內容摘要見 SKILL.md「外藏補全 campaign」段落（含每格的 curation 判斷與剔除理由）。

### 最新卷數全表（2026-07-20）

```
藏     前    古(正/外)    中(正/外)    近(正/外)    今(正/外)
經藏   23    93/122      0/2         0/23        0/3
律藏   33    106/94      102/100 ✅   100/5       100/4
論藏   116   175/54      105/100 ✅   100/100 ✅   118/7
宣藏   27    105/6       100/4       102/4       100/5
函藏   17    107/2       101/4       100/3       100/3
儀藏   74    100/5       101/4       100/3       100/2
詩藏   55    101/9       101/6       101/3       101/3
譯藏   20    100/5       100/3       102/6       100/5
史藏   39    106/8       101/7       101/3       106/5
類藏   23    100/5       100/5       100/4       100/6
合計   427   1403        1146        1060        968
```

---

## 三、🚧 進行中：今‧論藏外藏（7 → 100）—— **research 已完成，只剩 curation 與入庫**

**research 已跑完且零錯誤**（run `wf_5145d9ee-e44`，259 agents、1,067 萬 tokens）：
275 候選 → 253 fresh → 250 merged → **250 筆全數通過 adversarial verify**。

### ✅ 成果已存檔（不必重跑 research，重跑很貴）
```
C:/tmp/dzj_modern_lun_wai_verified250.json   ← 250 筆已查核候選，含完整 metadata
```

### 傳統分佈（本輪多元性明顯改善：非西方 150 vs 西方 100）
| 傳統 | 候選數 | 建議入庫配額 |
|---|---|---|
| 西方世俗（新無神論／宗教社會學／現象學／心理學／人類學／存在主義） | 100 | **24** |
| 伊斯蘭（現代主義／復興運動／女性主義／蘇非／辯難） | 35 | **15** |
| 猶太（對話哲學／靈性神學／大屠殺神學／見證文學） | 33 | **16** |
| 印度（吠檀多復興／哲學辯護／整體瑜伽／甘地／克里希那穆提） | 24 | **12** |
| 新興宗教（教典／神智學與新時代／日本新宗教／非洲獨立教會／美洲原住民復振） | 23 | **7** |
| 佛教（佛耶對話 18／京都學派 9／禪學西傳／漢傳人間佛教） | 21 | **12** |
| 中國（近現代反教與宗教思想） | 14 | **8** |
| | | **合計 94** |

> 需 94 筆（既有 7 扣掉待移除的尼采《敵基督》＝6，6+94=100）。
> 配額為建議值，可依實際書目品質微調；重點是**別讓西方那 100 筆吃掉多數名額**。

### ⚠️ 入庫前必做
1. **187 / 250 筆 intro 不足 40 字**（test 會 fail）——這批 agent 普遍寫得極簡。**選定 94 筆後逐筆補寫 intro**（這是本格最大的工作量，前一格只需補 16 筆）。
2. **移除今‧論外既有的「敵基督」（尼采）**：與已入庫的近‧論外「敵基督者——對基督教的詛咒」是同一本書；尼采（1888）依斷代屬**近代**，故現代那筆刪除。
3. 照第四節 curation 四動作：合併同書異譯／剔現代編譯本與全集編卷／必要時展開合集／砍單一作者過度代表。
4. **檢查中國與佛教切片的必收書是否齊全**（西文目錄查不到漢籍，前一格《聖朝破邪集》《不得已》就整個漏掉）。例如非基督教運動（1922）文獻、太虛／印順著作等，缺就手動補寫。

### 若要重跑 research
**fresh 重跑並重傳完整結構化 args**（切勿 bare-resume，會搞丟 args）。args 見 run diagnostics 或依第五節自組。

**⚠️ 入庫時必須順手修掉的既有問題**：
- 現有今‧論外的「**敵基督**」（尼采）與我已放進**近**‧論外的「敵基督者——對基督教的詛咒」是**同一本書跨時代重出**。尼采（1888）依斷代屬**近代**，故**今‧論外那筆應移除**。移除後既有剩 6 筆，需補 94 筆才到 100。

**現有今‧論外 7 卷**（偏英美無神論與新興宗教，需大幅補非西方）：
敵基督(尼采,待移除)／我為甚麼不是基督徒(羅素)／上帝錯覺(道金斯)／新世紀運動文獻／原理講論(統一教)／拉斯塔法里神學文獻／宗教多元論(希克)

---

## 四、本輪確立的作業流程（三格實證有效）

```
1. 清點        node 腳本 eval 各代 .ts → 算 era×藏×正外 卷數（見第六節）
2. 取去重清單   同上 eval 抽 title_zh；只取「會與本格碰撞」的子集即可
3. research    Workflow({name:'dazangjing-research', args:{結構化物件}})
4. salvage     若 verify 撞額度 → 從 journal 撈（欄位見下）
5. curation    ★最關鍵★ 合併同書異譯／剔現代編譯本／展開合集分卷／地域配額
6. 自審 metadata（知名正典幻覺風險低時可取代 adversarial verify）
7. patch       node 腳本 eval 既有 → 重組 divisions → JSON.stringify 覆寫該 wai 物件
8. 驗證        npx vitest run test/dazangjing.spec.ts 必綠
9. commit+push（pre-push hook 會跑全套 229 測試）
```

### curation 的四種常見動作（每格都會用到）
1. **合併同書異譯**：多個 research agent 各自列同一書（al-Hidaya 回了 7 版、al-Kāfī 8 版）→ 按 `title_orig` 認同一書，留 metadata 最完整者。
2. **剔現代編譯本／全集編卷**：Butterworth 2001《法拉比政治著作集》、Nemoy 1952《卡拉派文選》、辨喜全集九卷 → 都不是原典或會與個別作品重複。
3. **展開合集分卷**（衝卷數的正當主力）：塔木德按篇、密西拿妥拉十四卷、圖爾四部、**安薩里《宗教學的復興》四十卷**、精誠兄弟會書信四部。
4. **地域配額**（候選過剩時）：見下。

---

## 五、⚠️ 本輪新增踩雷（已寫入 SKILL.md，此處摘要）

1. **啟動必自組結構化 args 物件、直接 `Workflow({name, args:{...}})`**
   別用 `Skill dazangjing-research` 帶自然語言字串——wrapper 會把字串原樣塞進 workflow，`JSON.parse` 失敗 → `target={}` → scope/sources 全落空 → agents 去查「權威學術全集」通用清單（實測回一批 Migne PL/PG、Corpus Christianorum 等離題論藏工具書，全數作廢）。
   args 必含：`era / eraName / boundary / collection / collectionName / canon / canonLabel / goal:{goal, waiScope|zhengScope, sources} / existingTitles`。
   **外藏的 `goal.sources` 要換成該格專屬查詢視角**，別沿用 `collection-goals.ts` 內偏正藏的 sources。

2. **journal salvage 的實際欄位**
   result line＝`{type,key,agentId,result}`，**無 label**、值在 `result` 不在 `value`；
   consolidate 結果＝眾多 `{works:[...]}` 中**筆數最多**那筆（研究批次各 24–34、consolidate 48）。

3. **候選過剩時要按多元性配額挑，否則歐洲吃掉全部**
   近‧論外實測：213 個通過查核的候選中歐洲佔 **111**。採配額＝歐洲 30／猶太 18／伊斯蘭 15／印度南亞 15／東亞 9。
   並砍**單一作者過度代表**（霍爾巴赫 14、伍爾斯頓 8 篇神蹟論、費爾巴哈 8、鮑威爾 8、凱沙布 7）→ 每位留 1–2 部代表作。

4. **非西方文獻目錄覆蓋率差，canonical must-have 會漏**
   prompt 明列了《聖朝破邪集》《不得已》，research 仍沒回（DNB/BnF/OpenLibrary 等西文目錄查不到漢籍）。
   → **跑非西方切片後，務必自行檢查該傳統的必收書是否在列，缺的手動補寫**（本輪手補這 2 部）。

5. **test 有 `intro >= 40 字` 檢查**
   research agent 常寫 31–39 字的精簡 intro 而 fail（近論外一次 16 筆）。**insert 前先掃 `intro.length < 40` 補寫**。

6. **patch 腳本不可在已 patch 的檔上重跑**（它會讀當前檔的既有 works → 疊加）。
   修正流程＝**還原備份 → 改 JSON → 重跑 patch**。動 `.ts` 前先 `cp` 備份（該檔已有其他未提交變更，不能靠 git revert）。

7. **同書跨藏／跨代重出，test 抓不到**
   `test/dazangjing.spec.ts` 只比對 **exact `title_zh`**。異譯同書（「智慧書信」vs「智慧書信（德魯茲法度）」）不會被抓。
   → **異譯同書要自己防**。已修：德魯茲《智慧書信》原在中論外，我一度又放進中律外，已改補塔木德替換篇。
   → **待修**：尼采《敵基督》今論外 vs 近論外（見第三節）。

8. **verify 階段最耗額度**
   中律外那輪 196 個 verify agent 全撞 session limit（研究成果沒丟，可 salvage）。
   近論外那輪則 222 agents 零錯誤跑完。→ 大批候選寧可自審或分小批 verify。
   **撞額度 ≠ 529 Overloaded**（後者秒死 0 token，退避 ~90s 重跑即可）。

---

## 六、可重用的工具腳本

本輪 scratchpad 腳本已隨 session 結束失效，但**邏輯很簡單，重寫成本低**。核心是同一個 `extractObject()` brace-matching + `eval` 手法：

```js
// 從 data/dazangjing/{ancient,medieval,early-modern,modern}.ts 或 index.ts(前藏)
// 抽出 *_ERA 物件字面量並 eval，即可清點／取書名／改結構
function extractObject(s, name) {
  const idx = s.indexOf('const ' + name);
  const eq = s.indexOf('=', idx);
  let i = s.indexOf('{', eq), depth = 0, inStr = false, ch = '', esc = false;
  const start = i;
  for (; i < s.length; i++) {
    const c = s[i];
    if (inStr) { if (esc) { esc = false; continue; }
                 if (c === '\\') { esc = true; continue; }
                 if (c === ch) inStr = false; continue; }
    if (c === '"' || c === "'" || c === '`') { inStr = true; ch = c; continue; }
    if (c === '{') depth++;
    else if (c === '}') { depth--; if (depth === 0) return s.slice(start, i + 1); }
  }
}
const era = (0, eval)('(' + extractObject(src, 'MEDIEVAL_ERA') + ')');
```

- **const 名**：`PRE_CHRISTIAN_ERA`(在 index.ts)／`ANCIENT_ERA`／`MEDIEVAL_ERA`／`EARLY_MODERN_ERA`／`MODERN_ERA`
- **清點**：`era.collections[].{zheng,wai}.divisions[].works[]` 長度加總
- **回寫**：重組 divisions → `'wai: ' + JSON.stringify(newWai, null, 2).replace(/\n/g, '\n    ')` → 用同樣 brace-match 定位舊 `wai: {...}` 整段替換。JSON 是合法 TS，可免去中文/引號跳脫問題。
- ⚠️ `scripts/dazangjing_titles.py` 的終端輸出在此環境會 Big5 亂碼，**改用上述 node 方式抽書名**。

---

## 七、下一步建議

1. **完成今‧論外**（見第三節，含移除尼采《敵基督》）。
2. 之後仍薄的外藏格（普遍個位數），建議依序：
   - 各代**宣道藏外**（4–6）、**禮儀藏外**（2–5）、**史傳藏外**（3–8）、**譯校藏外**（3–6）、**類書藏外**（4–6）、**詩藝藏外**（3–9）、**書函藏外**（2–4）
   - **近/今的律藏外**（5／4）
   - 古代論外（54）、古代律外（94）離 100 不遠，可優先收尾
3. 每格都套用第四節流程與第五節踩雷檢查表。
4. **提案永不自動 merge，一律人工過目後入庫**（鐵則）。

---

## 八、相關檔案

- `data/dazangjing/{index,types,collection-goals,ancient,medieval,early-modern,modern}.ts` — 資料與收錄目標規格
- `.claude/skills/scripture-canon/SKILL.md` §8.2 — 權威 SOP 與完整踩雷清單
- `.claude/workflows/dazangjing-{research,sweep,verify-only}.js` — 三個 workflow（args 格式註解在檔頭）
- `test/dazangjing.spec.ts` — 結構鐵則（跨藏去重、intro ≥40 字等），insert 後必跑
- `pages/dazangjing/` — 前台頁面（本輪未動）
