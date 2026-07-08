import { describe, it, expect } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { setActivePinia, createPinia } from 'pinia'
import { useCollectedWorksStore } from '~/stores/collectedWorks'

// 全集/圖書館資料隔離契約：
// - stores/collectedWorks.ts 的每個 work.ebookId 都要被 backfill regex 抽得到
//   （scripts/apply-ebooks-quality-collection.mjs 靠同一條 regex 標 collection）
// - routeForEbook 是圖書館 reader 302 到全集 reader 的唯一判準

const BACKFILL_RE = /ebookId:\s*['"]([0-9a-f-]{36})['"]/g

describe('collected-works isolation', () => {
  setActivePinia(createPinia())
  const store = useCollectedWorksStore()

  const storeIds = new Set<string>()
  for (const a of store.authors) for (const w of a.works) if (w.ebookId) storeIds.add(w.ebookId)

  it('backfill regex 抽取數 = store 內實際 ebookId 數（migration 不漏標）', () => {
    const src = readFileSync(resolve(__dirname, '../../stores/collectedWorks.ts'), 'utf8')
    const regexIds = new Set([...src.matchAll(BACKFILL_RE)].map((m) => m[1]))
    expect(regexIds).toEqual(storeIds)
    expect(regexIds.size).toBeGreaterThan(300)
  })

  it('routeForEbook：全集卷回傳全集 reader 路由', () => {
    const anyAuthor = store.authors.find((a) => a.works.some((w) => w.ebookId))!
    const anyWork = anyAuthor.works.find((w) => w.ebookId)!
    expect(store.routeForEbook(anyWork.ebookId!)).toBe(
      `/collected-works/${anyAuthor.slug}/${anyWork.ebookId}`
    )
  })

  it('routeForEbook：非全集書回傳 null（圖書館書不 redirect）', () => {
    expect(store.routeForEbook('00000000-0000-0000-0000-000000000000')).toBeNull()
    expect(store.routeForEbook('')).toBeNull()
  })
})
