const MAX_QUERY_LENGTH = 160
const MAX_TERMS = 8
const MAX_TERM_LENGTH = 60

/**
 * Turn a loose user query into grammar-safe PostgREST search terms.
 * Keeping only Unicode letters, marks, and numbers prevents raw `.or()`
 * delimiters and ILIKE wildcards from changing the intended filter.
 */
export function normalizeDialogueSearchTerms(input: unknown): string[] {
  const normalized = String(input ?? '')
    .normalize('NFKC')
    .slice(0, MAX_QUERY_LENGTH)

  const candidates = normalized.match(/[\p{L}\p{M}\p{N}]+/gu) ?? []
  const terms: string[] = []
  const seen = new Set<string>()

  for (const candidate of candidates) {
    const term = candidate.slice(0, MAX_TERM_LENGTH)
    const key = term.toLocaleLowerCase()
    if (!term || seen.has(key)) continue
    seen.add(key)
    terms.push(term)
    if (terms.length >= MAX_TERMS) break
  }

  return terms
}

/**
 * Loose matching means ANY normalized term may occur in either the prompt or
 * the response. The returned value is safe to pass to Supabase `.or()`.
 */
export function buildDialogueKeywordFilter(input: unknown): string | null {
  const terms = normalizeDialogueSearchTerms(input)
  if (terms.length === 0) return null

  return terms
    .flatMap((term) => [
      `prompt.ilike.%${term}%`,
      `response.ilike.%${term}%`,
    ])
    .join(',')
}
