// 把 stores/collectedWorks.ts 的作者／著作清單倒成 JSON，給 Python 腳本用
// （collected_works_word.py 要知道每本書屬於哪個學科、哪位作者）。
//
// store 是 pinia setup store，裡面用到 ref／computed 與 `~/data/...` 匯入；
// 這裡用 esbuild 打包、把 pinia 與 vue 換成最小的假實作，直接執行 setup 拿資料。
//
//   node scripts/dump_collected_works_authors.mjs > output/collected_works_authors.json
import { build } from 'esbuild'
import { resolve, dirname, join } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
import { writeFileSync, mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..')

const stubs = {
  name: 'stubs',
  setup(b) {
    b.onResolve({ filter: /^~\// }, a => ({ path: resolve(ROOT, a.path.slice(2)) + (a.path.endsWith('.ts') ? '' : '.ts') }))
    b.onResolve({ filter: /^(pinia|vue)$/ }, a => ({ path: a.path, namespace: 'stub' }))
    b.onLoad({ filter: /.*/, namespace: 'stub' }, () => ({
      contents: `
        export const ref = v => ({ value: v })
        export const computed = f => ({ get value() { return f() } })
        export const defineStore = (_id, setup) => () => setup()`,
      loader: 'js',
    }))
  },
}

const out = await build({
  entryPoints: [resolve(ROOT, 'stores/collectedWorks.ts')],
  bundle: true, write: false, format: 'esm', platform: 'node', plugins: [stubs], logLevel: 'error',
  // ref／computed 在 Nuxt 是自動匯入，store 裡沒有 import 敘述，要當全域注入
  banner: { js: 'const ref = v => ({ value: v }); const computed = f => ({ get value() { return f() } });' },
})
const dir = mkdtempSync(join(tmpdir(), 'cw-dump-'))
const file = join(dir, 'store.mjs')
writeFileSync(file, out.outputFiles[0].text)
const mod = await import(pathToFileURL(file).href)
rmSync(dir, { recursive: true, force: true })
const store = mod.useCollectedWorksStore()
const authors = store.authors.value.map(a => ({
  slug: a.slug, name: a.name, nameEn: a.nameEn || '', nameOriginal: a.nameOriginal || '', disciplineGroup: a.disciplineGroup,
  works: (a.works || []).map(w => ({ title: w.title, titleOriginal: w.titleOriginal || '', ebookId: w.ebookId || '', category: w.category })),
}))
process.stdout.write(JSON.stringify(authors))
