# Session 交接 — 語言教練「無 AI 確定性反饋」+ 整夜 vocab gloss（2026-06-14）

接手者請先讀本檔，再看 `.claude/skills/coach-language/SKILL.md`（功能細節已全部寫進去）。
本 session 做了兩件事：(A) 監督整夜 vocab gloss 背景任務；(B) 蓋了一整套「不靠 AI 的確定性反饋」功能。

---

## A. ⏳ 進行中：整夜 vocab gloss 背景任務（需繼續每半小時巡查）

`python scripts/coach_vocab_bank.py gloss all` 在背景把 6 語的共用字庫補繁中釋義。

### 目前進度（2026-06-14 ~13:0x）
| 語言 | 目標 | 狀態 |
|---|---|---|
| grc | 5400 | ✅ 完成 |
| hbo | 7537 | ✅ 完成 |
| la | 6000 詞元 | ✅ 完成（6009） |
| **ja** | ~8385 | ▶ 進行中（死過一次、已重啟續傳，約 5240） |
| de | 6000 | ⏳ 待跑 |
| fr | 6000 | ⏳ 待跑 |
| en | 30000 | ⏳ 待跑（最大、最後） |

順序 grc→hbo→la→ja→de→fr→en。**跳過批次（log「! batch N 全引擎失敗」）目前 15 個**＝全引擎同時瞬斷的批次，不寫 ledger、留在 pending。

### 巡查指令（每半小時一次）
```
python scripts/coach_vocab_bank.py status
tail C:/tmp/vocab_bank/overnight.log
# 程序存活：
Get-CimInstance Win32_Process | ? { $_.Name -eq 'python.exe' -and $_.CommandLine -like '*coach_vocab*gloss*' }
```
### 規則
- **程序死掉**（今晚因網路 ConnectionError 死過 2 次）且還有語言未達目標 → 重啟：
  `nohup ./_whisper_venv/Scripts/python.exe scripts/coach_vocab_bank.py gloss all >> C:/tmp/vocab_bank/overnight.log 2>&1 &`
  （腳本可重入，從 ledger 續傳，不重做已完成詞）
- **ledger 凍結 >3 分鐘才重啟**；只是「慢」不要重啟（Haiku 慢但會成功）。
- 引擎修正已上線（commit `6cfabbe2`）：NVIDIA 2-strike + 90s 逾時 + Haiku 快速救急（使用者訂 Claude Max，Haiku 為可靠後盾）。今晚三引擎時有降級故偶慢/偶跳批次屬正常。
- **全部 6 語跑完後，再跑一遍 `gloss all`** 補那 15 個跳過批次（第二遍 NVIDIA 多半已恢復、很快）。
- `C:/tmp/vocab_bank/` ledger 別清。

---

## B. ✅ 已完成並 push（origin/master）：語言教練「無 AI 確定性反饋」系列

> ⚠️ 本 repo 有多個並行背景任務（jung [loop]／apocrypha／panikkar…）同時在 commit master，
> `git log` 的 HEAD 可能瞬間看起來怪怪的，但下列 commit 都已確認在 **origin/master**（`git branch -r --contains <sha>` 驗過）。**別 force-reset master**。

| 功能 | commit | 頁面/端點 |
|---|---|---|
| 字母教學＋測驗（de/fr/ja/grc/la/hbo） | （早於下列） | `/coach/[lang]/alphabet`、`server/data/alphabets.ts`、端點 `alphabet` |
| 希臘文詞形判析（parse 新約 morph） | `a3187b78` | `/coach/[lang]/parse`、`parseGreek.json`、端點 `parse` |
| 希伯來文詞形判析（舊約 binyan） | `e7873586` | 同上 `parseHebrew.json`（RTL） |
| shadowing 零服務評分強化 | `9a0add9a` | `composables/usePronunciationScore.ts`（詞級對齊 hit/near/miss） |
| 句子重組（受限寫作題型） | `7df18d47` | `/coach/[lang]/compose`、端點 `compose`（en/grc/hbo） |
| 句子重組擴 de/fr/la（字庫例句） | `627af6c3` | 同上（ja 無詞間空白不支援） |
| LanguageTool 規則式文法檢查 | `db4d99e5` | 寫作頁 `grammar-check` 端點 + `nuxt.config` `languageToolUrl` |

引擎修正 commit：`6cfabbe2`（NVIDIA 2-strike+Haiku 救急，治 gloss 卡死）。
全部零 AI／零外部 LLM；測試：parse 19、pronunciation-score 10 passed。SKILL.md §一/§四/§八/§十 已更新。

### 使用者待辦（手動）
1. **完全關閉再重開瀏覽器** → grc/la 的單字、閱讀、跟讀就能發聲（已裝 Stefanos 希臘語 + Cosimo/Elsa 義大利語）。
2. **（可選）自架 LanguageTool** → 寫作「文法檢查」鈕才會啟用：Zeabur 加 `erikvl87/languagetool` Docker 服務，URL 填 env `LANGUAGETOOL_URL`（步驟見 SKILL §十-4）。

### 尚未做（使用者可能會再提）
- de/fr 的句子重組要等 gloss 補到 de/fr 把例句寫進字庫後才有題（頁面 total=0 時顯示「字庫建置中」）。
- ja 句子重組需引入 JP 斷詞器（如 TinySegmenter，~25KB 純 JS）才能做 → 後續再議。
- 寫作受限題型可再加「填空／翻譯比對」。

---

## C. ⏳ TTS 語音安裝（背景，Windows Update 下載中）
- ✅ 已裝：`el-GR`（Stefanos 希臘語）、`it-IT`（Cosimo/Elsa，拉丁用義式發音）
- ⏳ 下載中：`he-IL`、`de-DE`、`fr-FR`、`ja-JP`（安裝程序仍在跑，Windows Update 很慢）
- 查狀態：`Get-WindowsCapability -Online -Name "Language.TextToSpeech~~~he-IL~0.0.1.0"`
- 若安裝程序已死但語音未齊，可手動補：`Add-WindowsCapability -Online -Name "Language.TextToSpeech~~~<code>~0.0.1.0"`（需系統管理員）
- ⚠️ 古典語（grc/la/hbo）TTS 是現代語發音（非 Koine/Erasmian），消費級 TTS 沒有復原發音。
