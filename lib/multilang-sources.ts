/**
 * Multi-language parallel sources — schema contract for collected-works books
 * (德 GW + 英 CW + 繁中, etc.). See .claude/skills/collected-works-multilang/.
 *
 * A chunk's display text is `content` (always the 繁中 translation). Source
 * languages live in `sources` (lang-code → text) with `source_order` giving the
 * column order. For BACK-COMPAT with the legacy two-column reader, every chunk
 * also mirrors its PRIMARY source into the old `source_text` / `source_lang`
 * fields, and a chunk that only has those old fields is treated as a one-source
 * book. These pure helpers are the single source of truth for that contract and
 * are shared by the writer (translate script), the API passthrough, and the
 * reader's view-mode toggle.
 */

export interface MultilangFields {
  source_lang?: string | null;
  source_text?: string | null;
  sources?: Record<string, string> | null;
  source_order?: string[] | null;
}

export interface NormalizedSources {
  sources: Record<string, string>;
  source_order: string[];
}

/**
 * Canonicalize a chunk's multilang fields into `{ sources, source_order }`.
 *
 * - Explicit `sources` wins. `source_order` is honoured but filtered to keys
 *   that actually exist, and any source key missing from the order is appended
 *   (stable) so no column is silently dropped.
 * - Otherwise fall back to the legacy single source (`source_text`+`source_lang`).
 * - Monolingual chunk (front matter, plain 中文 book) → empty.
 */
export function normalizeSources(c: MultilangFields): NormalizedSources {
  if (c.sources && Object.keys(c.sources).length) {
    const present = c.sources;
    const order: string[] = [];
    for (const l of c.source_order ?? []) {
      if (l in present && !order.includes(l)) order.push(l);
    }
    for (const k of Object.keys(present)) {
      if (!order.includes(k)) order.push(k);
    }
    return { sources: { ...present }, source_order: order };
  }
  if (c.source_text != null && c.source_lang) {
    return { sources: { [c.source_lang]: c.source_text }, source_order: [c.source_lang] };
  }
  return { sources: {}, source_order: [] };
}

/**
 * Writer-side: return a copy of the chunk with `sources`/`source_order`
 * normalized AND the legacy `source_text`/`source_lang` mirrored to the primary
 * (first) source, so the old reader and bilingual books keep working unchanged.
 * Monolingual chunks pass through with old fields preserved (null-coalesced).
 */
export function mirrorPrimarySource<T extends MultilangFields>(c: T): T {
  const { sources, source_order } = normalizeSources(c);
  if (!source_order.length) {
    return { ...c, source_lang: c.source_lang ?? null, source_text: c.source_text ?? null };
  }
  const primary = source_order[0];
  return { ...c, sources, source_order, source_lang: primary, source_text: sources[primary] };
}

export type ViewMode = string; // "zh" | "parallel" | `src:${lang}`

/**
 * Reader-side: which view modes a chunk offers.
 *   monolingual → just 中.
 *   ≥1 source   → 中 / 對照 / one single-column mode per source.
 */
export function availableViewModes(source_order: string[]): ViewMode[] {
  if (!source_order.length) return ["zh"];
  return ["zh", "parallel", ...source_order.map((l) => `src:${l}`)];
}

/**
 * Reader-side: clamp a saved/desired mode to what this chunk actually offers,
 * falling back to 中 (zh). Stops a stale localStorage `src:de` from blanking the
 * page when the current chunk has no German.
 */
export function resolveViewMode(desired: string | null | undefined, source_order: string[]): ViewMode {
  const avail = availableViewModes(source_order);
  return desired && avail.includes(desired) ? desired : "zh";
}

/**
 * Reader-side: migrate a legacy persisted view-mode value to the generalized
 * vocabulary. Old reader stored only "zh" | "bi" | "en":
 *   "bi" → "parallel"
 *   "en" → the primary source's single-column mode ("src:<primary>")
 * Already-generalized values ("zh" / "parallel" / "src:*") pass through. The
 * result is NOT clamped — callers still run it through resolveViewMode against
 * the current chunk's source_order.
 */
export function migrateLegacyViewMode(saved: string | null | undefined, source_order: string[]): ViewMode {
  if (!saved) return "zh";
  if (saved === "bi") return "parallel";
  if (saved === "en") return source_order.length ? `src:${source_order[0]}` : "zh";
  return saved;
}

/** Short CJK label for the toggle button of a language code. */
export const LANG_LABEL: Record<string, string> = {
  zh: "中", de: "德", en: "英", la: "拉", fr: "法",
  el: "希", grc: "希臘", he: "希伯來", it: "義", es: "西",
  ja: "日", ko: "韓", ru: "俄",
};
export function langLabel(code: string): string {
  return LANG_LABEL[code] ?? code.toUpperCase();
}

export interface ParallelRow {
  zh: string;
  cols: Record<string, string>;
}

/**
 * Reader-side parallel grid: zip the 繁中 paragraphs with each source language's
 * paragraphs BY INDEX, padding short columns with "" so one missing paragraph
 * never shifts every following row in another column (same posture as the
 * align-by-number footnote rows). Upstream alignment is responsible for making
 * the per-language paragraph lists line up; the reader only zips + pads.
 */
export function zipParallel(
  zhParas: string[],
  sourcesParas: Record<string, string[]>,
  source_order: string[]
): ParallelRow[] {
  const lengths = [zhParas.length, ...source_order.map((l) => sourcesParas[l]?.length ?? 0)];
  const n = lengths.reduce((a, b) => Math.max(a, b), 0);
  const rows: ParallelRow[] = [];
  for (let i = 0; i < n; i++) {
    const cols: Record<string, string> = {};
    for (const l of source_order) cols[l] = sourcesParas[l]?.[i] ?? "";
    rows.push({ zh: zhParas[i] ?? "", cols });
  }
  return rows;
}
