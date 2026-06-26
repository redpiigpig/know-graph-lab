export const meta = {
  name: 'genesis-dialogue-maps',
  description: '創生哲學剩餘章逐節盟友/foil/旁證研究（每波6章、每章重試）',
  phases: [{ title: 'Research', detail: '剩餘章平行研究寫報告檔' }],
}
const WORK = [{"vol": "V1", "rc": 5, "t": "第五章　美的相對客觀性（relative objectivity）與文化主觀性（cultural subjectivity）", "n": 4}, {"vol": "V1", "rc": 6, "t": "第六章　真善美聖的四向度階層", "n": 5}, {"vol": "V2", "rc": 1, "t": "第一章　意義的困難問題", "n": 4}, {"vol": "V2", "rc": 2, "t": "第二章　虛無主義的價值論診斷", "n": 4}, {"vol": "V2", "rc": 3, "t": "第三章　愛作為願然的最高運動", "n": 4}, {"vol": "V2", "rc": 4, "t": "第四章　神聖性與空無美學", "n": 4}, {"vol": "V2", "rc": 5, "t": "第五章　主體作為最高價值", "n": 4}, {"vol": "V2", "rc": 6, "t": "第六章　結語：願然與第二軸心時代", "n": 4}, {"vol": "V3", "rc": 1, "t": "第一章　在場世界論：潛生界、意想界、存在界", "n": 6}, {"vol": "V3", "rc": 2, "t": "第二章　心為工畫師：唯識、心理學與世界的生成", "n": 3}, {"vol": "V3", "rc": 3, "t": "第三章　藝術與文學作為世界創造", "n": 3}, {"vol": "V3", "rc": 4, "t": "第四章　科幻、電影與動畫：意想界的工程學", "n": 3}, {"vol": "V3", "rc": 5, "t": "第五章　結語：世界理論在價值論中的位置", "n": 2}, {"vol": "B1", "rc": 1, "t": "第一章　導論：存有論作為「默然」之學", "n": 4}, {"vol": "B1", "rc": 2, "t": "第二章　空無的本體地位", "n": 5}, {"vol": "B1", "rc": 3, "t": "第三章　創生前態：存在的第三態", "n": 4}, {"vol": "B1", "rc": 4, "t": "第四章　存有者的分類學", "n": 5}, {"vol": "B1", "rc": 5, "t": "第五章　超限存在者與不可通約的臨在", "n": 5}, {"vol": "B1", "rc": 6, "t": "第六章　創生剃刀：可意向性即存有條件", "n": 4}, {"vol": "B1", "rc": 7, "t": "第七章　結語：存有的邊界地形學（Boundary Topography of Being）", "n": 5}, {"vol": "B2", "rc": 1, "t": "第一章　默然向度：語言與意向性失效之處", "n": 4}, {"vol": "B2", "rc": 2, "t": "第二章　語言的自我創生與否定性自指", "n": 4}, {"vol": "B2", "rc": 3, "t": "第三章　空無刺透存有：哥德爾縫隙作為創生起點", "n": 5}, {"vol": "B2", "rc": 4, "t": "第四章　銜尾蛇：存有的動態自指實在", "n": 4}, {"vol": "B2", "rc": 5, "t": "第五章　空無的數學形式化：零、無限與 ת", "n": 4}, {"vol": "B2", "rc": 6, "t": "第六章　結語：維摩一默", "n": 4}, {"vol": "B3", "rc": 1, "t": "第一章　神聖性：空無以神聖的方式臨在", "n": 4}, {"vol": "B3", "rc": 2, "t": "第二章　空無神學：神是不存在的，但也是創生的", "n": 5}, {"vol": "B3", "rc": 3, "t": "第三章　空無的三一結構與神聖語言", "n": 3}, {"vol": "B3", "rc": 4, "t": "第四章　虛無主義的存有論診斷", "n": 4}, {"vol": "B3", "rc": 5, "t": "第五章　永恆的不可能與死亡的存有論", "n": 5}, {"vol": "B3", "rc": 6, "t": "第六章　宇宙的終末與自我創生", "n": 4}, {"vol": "B3", "rc": 7, "t": "第七章　結語：神人互構與默然的承擔", "n": 4}]
const RULES = `
## 嚴格準則
- 用 WebSearch/WebFetch 查證每一筆；作者/年份/刊名要正確；不確定標「（細節待核）」或捨棄，寧缺勿杜撰。
- 優先 SEP/IEP/DOI/OA/arXiv/PMC；前沿只取公認里程碑（避偽科學/working paper）。
- 摘要一律繁體中文 2–3 句：論點 + 為何盟友/foil/旁證。中文權威文獻可標 語言：中文。
- 立場三選一：支持(盟友)/補充(旁證)/反例(foil)。
## 每節要求：3–5 筆（盟友/foil/旁證各1–2），每節至少 1 反例 + 1 支持或補充。
## 輸出格式（領域標頭：自然科學/心理學/哲學/宗教與神話 擇一，同領域同一 ## 下）
【Surname, Initials】（YYYY）〈Title〉，《Journal/Publisher》
語言：英文
所屬面向：<該小節標籤，一字不差照抄清單字串>
立場：支持
摘要：（繁中2–3句）
> **全文**：[label](https://doi.org/...)
`
function buildPrompt(it){return `你是替「創生哲學」建立逐節文獻對話地圖的學術館員。
卷代號 **${it.vol}**，本章＝**${it.t}**。
先用 Read：(1) 讀 c:/tmp/genesis_research/thesis.json 取 ["${it.vol}"] 的 domain 與 thesis；(2) 讀 c:/tmp/genesis_research/clean_inv.json，在 ["${it.vol}"] 找 title=="${it.t}" 的章，取其 sections 陣列（約 ${it.n} 節）。所屬面向一字不差照抄 sections 字串。
為每一小節找盟友(支持/補充)/foil(反例)/旁證文獻。
${RULES}
交付：用 Write 寫入 c:/Users/user/Desktop/know-graph-lab/scripts/data/lit_review_genesis_${it.vol}_dialogue_ch${it.rc}.md。回傳一行：節數/總筆數/立場分布/待核數。`}
function runOne(it){
  return agent(buildPrompt(it),{label:`${it.vol}-ch${it.rc}`,phase:'Research'})
    .then(r=>({vol:it.vol,rc:it.rc,ok:r!=null}))
    .catch(()=>agent(buildPrompt(it),{label:`${it.vol}-ch${it.rc}#r`,phase:'Research'})
      .then(r=>({vol:it.vol,rc:it.rc,ok:r!=null})).catch(()=>({vol:it.vol,rc:it.rc,ok:false})))
}
phase('Research')
log(`剩餘 ${WORK.length} 章開跑（每波6）`)
const WAVE=6, results=[]
for(let i=0;i<WORK.length;i+=WAVE){
  const r=await parallel(WORK.slice(i,i+WAVE).map(it=>()=>runOne(it)))
  results.push(...r)
  log(`進度 ${results.length}/${WORK.length}（成功 ${results.filter(x=>x&&x.ok).length}）`)
}
const failed=results.filter(r=>!r||!r.ok)
return {total:WORK.length,done:results.length-failed.length,failed:failed.map(f=>`${f.vol}-ch${f.rc}`)}
