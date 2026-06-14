# 東方聖書（Sacred Books of the East）— Session 交接

> **新 session 從這裡接手。** 馬克斯‧穆勒主編 50 卷東方經典英譯集；獨立 corpus／portal，不屬穆勒著作集。
> 引擎政策見 [[feedback_engine_nvidia_no_haiku]]；本案因環境無 Gemini key，實務上走 **Haiku(Claude Max)→Sonnet** 雙層。

## 一句話現況（2026-06-14）

6 卷代表卷（各宗教傳統一卷）**英文全上架可讀**，繁中翻譯**背景跑中**：奧義書/阿維斯陀 ≈99% 竣工、古蘭經進行中、法句經/易經/耆那排隊。Portal `/sacred-books-east` 已上線、分組瀏覽可用。其餘 44 卷在 store 掛 `planned`。

## 進度表（隨時用下方腳本重抓）

| 卷 | slug | ebookId 前綴 | archive.org en_id | tradition | 狀態 |
|---|---|---|---|---|---|
| 1 奧義書（上）| sbe-01-upanishads-1 | 55555501 | upanishads01mluoft | veda | ✅ done（99%）|
| 4 阿維斯陀（一）祓魔法典 | sbe-04-zend-avesta-1 | 55555504 | zendavesta00darmgoog | zoroastrian | ≈99%（收尾）|
| 6 古蘭經（上）| sbe-06-quran-1 | 55555506 | mlbd.koransacredbooks0000unse_w1m9 | islam | 進行中 |
| 10 法句經／經集 | sbe-10-dhammapada | 55555510 | mlbd.dhammapadasuttni0000fmax | buddhism | 排隊（會自動帶佛教術語表）|
| 16 易經 | sbe-16-yi-king | 55555516 | sacredbooksofchi16conf | china | 排隊 |
| 22 耆那教經典（一）| sbe-22-jaina-1 | 55555522 | mlbd.jainasutraspt1tr00vol-22.unse_m8x0 | jainism | 排隊 |

> ebookId 完整格式：`555555NN-5555-4555-8555-555555555555`（NN=卷號）。eid 命名空間 `555555NN` 專給 SBE，勿與穆勒 `4444444X` 撞。

## 架構（全部已上線、test 綠、已 push）

- **store**：[stores/sacredBooksEast.ts](../../../stores/sacredBooksEast.ts) — 50 卷權威卷目，按 7 大傳統分組（veda/buddhism/jainism/zoroastrian/china/islam/index），譯者中英並列。轉錄完一卷把該卷 `status` 改 `done`／`in-progress` + 填 `ebookId`/`archiveId`。
- **page**：[pages/sacred-books-east/index.vue](../../../pages/sacred-books-east/index.vue) — 簡介＋傳統 chips＋分組卷目卡。`resolveComponent('NuxtLink')` 綁定（**勿改回 `:is="'NuxtLink'"` 字串**，那會渲染成無 href 的死連結，整個 /collected-works 卡片點不進去就是這個 bug，已修）。
- **轉錄 driver**：[scripts/sbe_translate.py](../../../scripts/sbe_translate.py) — SBE 專屬 registry（**不污染** `mueller_auto.WORKS`），複用 mueller 的 ingest/translate/upload。`--list` / `--ingest <slug>` / `--loop --only <slugs>`。
- 穆勒 hub「東方聖書」row 用 `CwWork.externalUrl='/sacred-books-east'` 連過去（hub `linkTarget()` 優先 externalUrl）。

### 新增一卷 SOP
1. 找 archive.org 有**真 `_djvu.txt`** 的版本（小心：很多 id 回傳的是 HTML 錯誤頁，要實抓前幾百 bytes 確認不是 `<!doctype>`；也要確認是對的 Part）。
2. 在 `sbe_translate.py` 的 `WORKS` 加一行（slug/eid `555555NN`/title/title_en/author=**真實譯者**/tradition 在 `TRADITION` map/en_id/split="coarse"）。
3. `python scripts/sbe_translate.py --ingest <slug>`（英文秒上架）。
4. store 對應卷填 ebookId/archiveId、status 改 in-progress。
5. `python scripts/sbe_translate.py --loop --only <slug>` 背景翻。

## 引擎政策（2026-06-14 user 拍板）

**免費層不動 → 自動升級 Sonnet 轉錄。** 實作在 `make_sbe_engine`：
- Haiku（Claude Max）**快速失敗**（backoffs 0,20）→ 免費池 429/連線/空回 ~20s 內 escalate。
- **Sonnet fallback**：`_sonnet_translator()` — 若設 `ANTHROPIC_SONNET_API_KEY`（或 `ANTHROPIC_API_KEY`）用**專屬 paid client 繞過 Max 限額**；**目前 user 選擇不另付費** → Sonnet 也走 Max OAuth。
- ⚠️ **後果**：Max 被限流時（尤其我們在跑互動 Opus 對話搶同一帳號）Haiku 與 Sonnet 一起 429，log 出現 `Sonnet 429 — backoff 600s` → 偏慢。**閒置／隔夜時 Max 不被搶就會順跑。** 若 user 日後願付費，設 `ANTHROPIC_SONNET_API_KEY` 即真正繞過。

## 🚨 操作鐵則（上個 session 踩過的雷，務必遵守）

1. **不要頻繁 kill/重啟 pass。** `translate_work` 每次從 sec0 重掃，重啟＝重做殘段、永遠到不了未譯的尾段。上個 session 因反覆重啟造成「假停滯」。**啟動一次就讓它跑**，靠監測腳本看進度、靠 half-hourly 排程抓硬停滯。
2. **判斷是否在跑看「▶ translate」行 + sec 號是否單調前進**，**不要看 pid 數**——`python` shim 會 re-exec，一個 pass 常顯示 2–4 個 python.exe，不代表有多個 pass。真要確認單一 worker：數 log 裡 `▶ translate` 出現次數。
3. **多任務只動自己啟動的 process**（[[feedback_no_kill_other_tasks]]）。並行有 jung/coach session，commit 用 pathspec 只提交 SBE 相關檔。
4. **autostash 防進度被吞**：抽查時 `git add mueller_data && git commit`；pull 用 `--rebase --autostash`。並行 session 的非 SBE 檔（accs/jung）勿動。

## 監測腳本（每半小時或被問「目前如何」就跑）

```bash
cd "c:/Users/user/Desktop/know-graph-lab" && PYTHONIOENCODING=utf-8 PYTHONUTF8=1 python -c "
import os,glob,json
root='.claude/skills/ebook-collected-works/mueller_data'
books=[('奧義書','sbe-01-upanishads-1'),('阿維斯陀','sbe-04-zend-avesta-1'),('古蘭經','sbe-06-quran-1'),('法句經','sbe-10-dhammapada'),('易經','sbe-16-yi-king'),('耆那','sbe-22-jaina-1')]
gt=gd=0
for name,slug in books:
    t=dn=0
    for s in glob.glob(os.path.join(root,slug,'sec*.json')):
        j=json.load(open(s,encoding='utf-8')); zh=j.get('zh') or []
        t+=len(zh); dn+=sum(1 for z in zh if (z or '').strip())
    gt+=t; gd+=dn; print(f'{name:8s} {dn*100//t if t else 0:3d}%  {dn}/{t}')
print(f'總計 {gd*100//gt if gt else 0}%  {gd}/{gt}')"
```

## 續跑 / 重啟指令（當機或重開機後）

```bash
# 先確認沒有殘留 pass（避免雙跑互搶 Max 額度）：
#   PowerShell: Get-CimInstance Win32_Process -Filter "Name='python.exe'" | ? {$_.CommandLine -match 'sbe_translate'}
# 乾淨後啟動一次（resumable，從 sec 快取續）：
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 python scripts/sbe_translate.py --loop --only sbe-04-zend-avesta-1,sbe-06-quran-1,sbe-10-dhammapada,sbe-16-yi-king,sbe-22-jaina-1
```

## 佛教術語入詞庫（2026-06-14，已完成）

- **119 條漢傳佛教標準譯名**入 `deities` 表 `religion=佛教`（`/translation-glossary` 神祇與宗教名詞 tab 可查/編輯）：佛號／諸佛菩薩／弟子／三寶／核心教義／天部六道／經典／教派；梵巴二式並收。Seed：[scripts/seed_glossary_buddhist.py](../../../scripts/seed_glossary_buddhist.py)（`--dry` 預覽，idempotent on_conflict=name_english）。
- 來源說明：佛光大辭典**無公開批次 API**（只能單條查），故依**漢傳標準傳統譯名**（佛光所 codify 那套）人工策展；佛光特有/異體放 variants。user 可在編輯模式調整 `name_recommended`（[[feedback_glossary_strict_authority]]）。
- **已接上翻譯**：`sbe_translate.make_sbe_engine` 對佛教卷（tradition=buddhism）自動把這 119 條注入 prompt 鎖譯名。實測：Nirvana→涅槃、bhikkhu→比丘、八正道、世尊、舍衛城 全正確。法句經輪到時即生效。

## 順手修過的兩個 bug（已 push，勿回退）

- **卡片點不進去**：`<component :is="'NuxtLink'">` 字串綁定→死連結；改 `resolveComponent('NuxtLink')`（hub + sbe 兩頁）。
- **ebook_chunks 預覽不全**：cover chunk 的 `chunk_type='cover'` 違反 CHECK 約束（只允 page/chapter/section），cover 在 batch 0→整批被拒，每本掉 ~25 列。`mueller_auto.sync_previews` 已 coerce 預覽 chunk_type + 每批重試+驗證；穆勒全書已重灌對齊。

## 下一步（建議順序）

1. **顧好正在跑的 5 卷**：翻完一卷就把 store 該卷 status→done。法句經翻完抽幾段檢查佛教專名（user 想看）。
2. **鋪滿其餘 44 卷**：store 已列全 50 卷卷目；逐卷照「新增一卷 SOP」找源、ingest、翻譯。建議先補各傳統的下一卷（吠陀群最多 20+ 卷）。
3. （日後）若 user 改主意付費，設 `ANTHROPIC_SONNET_API_KEY` 讓 Sonnet 繞過 Max。

## See also
- [mueller_collected_works.md](mueller_collected_works.md) — 穆勒著作集（16 卷全竣）；SBE 從這裡分出
- [SKILL.md](SKILL.md) — 多語對照 pipeline 主文件
- [[translation-glossary]] — 詞庫權威；佛教詞條在 deities 表 religion=佛教
- [[feedback_engine_nvidia_no_haiku]] / [[feedback_no_kill_other_tasks]] / [[feedback_glossary_strict_authority]]
