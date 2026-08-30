#!/usr/bin/env node
/**
 * 把 data/dazangjing/*.ts 的全藏書目倒成一份 JSON，供 Python 端（去重、分類、
 * 提案清理）讀取。
 *
 *   node scripts/dazangjing_dump_corpus.mjs [out.json]
 *
 * 預設寫到 c:/tmp/dz_corpus.json。資料檔是 TS 且互相 import，所以先用 esbuild
 * bundle 成一支 esm 再 import——比在 Python 端硬解 TS 可靠得多。
 */
import { build } from 'esbuild'
import { writeFileSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import path from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const out = process.argv[2] || 'c:/tmp/dz_corpus.json'
const bundle = path.join(tmpdir(), `dz-corpus-${process.pid}.mjs`)

await build({
  entryPoints: [path.join(root, 'data/dazangjing/index.ts')],
  bundle: true, platform: 'node', format: 'esm', outfile: bundle, logLevel: 'error',
})
const { ERAS } = await import(pathToFileURL(bundle).href)
rmSync(bundle, { force: true })

const works = []
for (const era of ERAS)
  for (const coll of era.collections)
    for (const canon of ['zheng', 'wai'])
      for (const div of coll[canon].divisions)
        for (const w of div.works)
          works.push({
            era: era.key, coll: coll.key, canon, div: div.key,
            title_zh: w.title_zh, title_orig: w.title_orig ?? '',
            author: w.author ?? '', link: w.link ?? '',
            has_intro: Boolean(w.intro),
          })

writeFileSync(out, JSON.stringify(works), 'utf-8')
console.log(`${works.length} 卷 → ${out}`)
