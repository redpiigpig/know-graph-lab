# -*- coding: utf-8 -*-
# 依「磁碟上尚未產出的章」重生 research_workflow.mjs（WORK 內嵌剩餘章）
import json
from pathlib import Path
work=json.load(open('c:/tmp/genesis_research/worklist.json',encoding='utf-8'))
DATA=Path('c:/Users/user/Desktop/know-graph-lab/scripts/data')
remaining=[{'vol':w['vol'],'rc':w['realch'],'t':w['title'],'n':w['nsec']}
           for w in work
           if not (DATA/f"lit_review_genesis_{w['vol']}_dialogue_ch{w['realch']}.md").exists()]
work_js=json.dumps(remaining,ensure_ascii=False)
tmpl=r'''export const meta = {
  name: 'genesis-dialogue-maps',
  description: '創生哲學剩餘章逐節盟友/foil/旁證研究（每波6章、每章重試）',
  phases: [{ title: 'Research', detail: '剩餘章平行研究寫報告檔' }],
}
const WORK = __WORK__
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
'''
out=tmpl.replace('__WORK__',work_js)
Path('c:/tmp/genesis_research/research_workflow.mjs').write_text(out,encoding='utf-8')
print(f'wrote workflow with {len(remaining)} remaining chapters')
