// @vitest-environment node

import { readFileSync } from 'node:fs'

import { describe, expect, it } from 'vitest'
import {
  buildDialogueKeywordFilter,
  normalizeDialogueSearchTerms,
} from '../server/utils/dialogue-search'

describe('AI dialogue loose keyword search', () => {
  it('normalizes Chinese and Latin keywords while preserving their order', () => {
    expect(normalizeDialogueSearchTerms('  創世  philosophy，世界  ')).toEqual([
      '創世',
      'philosophy',
      '世界',
    ])
  })

  it('deduplicates case-insensitively after Unicode normalization', () => {
    expect(normalizeDialogueSearchTerms('Faith faith ＦＡＩＴＨ')).toEqual(['Faith'])
  })

  it('removes PostgREST grammar and ILIKE wildcard characters', () => {
    const filter = buildDialogueKeywordFilter('存在%, 回應_(測試). "\u005c')
    expect(filter).toBe([
      'prompt.ilike.%存在%',
      'response.ilike.%存在%',
      'prompt.ilike.%回應%',
      'response.ilike.%回應%',
      'prompt.ilike.%測試%',
      'response.ilike.%測試%',
    ].join(','))
  })

  it('matches any term against both prompt and response', () => {
    expect(buildDialogueKeywordFilter('創世 哲學')).toBe([
      'prompt.ilike.%創世%',
      'response.ilike.%創世%',
      'prompt.ilike.%哲學%',
      'response.ilike.%哲學%',
    ].join(','))
  })

  it('returns no filter for blank or punctuation-only input', () => {
    expect(buildDialogueKeywordFilter('  ，（）%_  ')).toBeNull()
  })

  it('caps the number of loose terms', () => {
    expect(normalizeDialogueSearchTerms('一 二 三 四 五 六 七 八 九 十')).toHaveLength(8)
  })

  it('keeps keyword search visible by default and gates code input behind the modal', () => {
    const page = readFileSync(new URL('../pages/ai-dialogues/index.vue', import.meta.url), 'utf8')
    const modalStart = page.indexOf('v-if="lookupOpen"')
    const codeInput = page.indexOf('placeholder="例如 C-00241 或 G-00789"')

    expect(page).toContain('placeholder="搜尋提問或回應的關鍵字"')
    expect(page).toContain('@click="openLookup"')
    expect(modalStart).toBeGreaterThan(-1)
    expect(codeInput).toBeGreaterThan(modalStart)
  })

  it('preserves authenticated sequence deep links and server-side keyword filtering', () => {
    const page = readFileSync(new URL('../pages/ai-dialogues/index.vue', import.meta.url), 'utf8')
    const api = readFileSync(new URL('../server/api/ai-dialogues/index.get.ts', import.meta.url), 'utf8')

    expect(page).toContain('useRoute().query.seq')
    expect(page).toContain('$fetch("/api/ai-dialogues/by-seq", { query: { seq }, headers: h })')
    expect(api).toContain('query = query.or(keywordFilter)')
    expect(api).toContain("if (keywordFilter && uncategorized === '1')")
  })
})
