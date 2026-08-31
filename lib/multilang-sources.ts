/**
 * Multi-language parallel sources — schema contract for collected-works books
 * (德 GW + 英 CW + 繁中, etc.). See .claude/skills/ebook-collected-works/.
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
 * Filler for a source paragraph that has no counterpart at that index.
 *
 * The parallel grid zips columns BY INDEX, and the reader builds each column by
 * splitting on blank lines and dropping empties — so an empty paragraph would
 * be discarded and shift every later row in that column. A writer that can only
 * fill SOME positions (e.g. a Latin original aligned to the 繁中 by the classical
 * paragraphus number: numbered body paragraphs match, headings and footnote
 * blocks have no Latin) must emit this instead of "" to hold the slot.
 *
 * U+200B ZERO WIDTH SPACE specifically: it survives `String.trim()` (unlike NBSP
 * and ordinary spaces) so it is not filtered out, and renders as nothing.
 */
export const BLANK_PARAGRAPH = "​";

// ── Anchor alignment ────────────────────────────────────────────────────────
// Index zipping assumes both columns were split into the same number of
// paragraphs. Across the 教父 corpus that holds for only 30% of chunks: the
// 繁中 translation merges and splits paragraphs freely, and the two sides do not
// always agree on where the footnote section starts. The result is a 對照 grid
// whose rows drift apart while looking perfectly normal.
//
// Both sides do, however, carry the same markers. Three keys, tried in order of
// how finely they cut, cover 65% of chunks between them:
//   n:  a leading section number — 「17. 我自幼就聽聞了…」 / "17. Even as a boy…"
//       (the classical paragraphus; the same number the Latin original uses)  29%
//   p:  a page marker — {{p:226}} — emitted on both sides by the parser        27%
//   c:  a chapter heading — 「第二章——…」 / "Chapter 2.—…" or "Chapter II."      9%
// The remaining 35% carry no shared marker (mostly front matter) and keep the
// old index zip.

const LEADING_NUMBER = /^\s*(\d+)\.\s/;
const PAGE_MARKER = /\{\{p:(\d+)\}\}/;
// Chapter headings are matched with or without the markdown hashes: the 繁中
// side sometimes loses them when a heading gets merged into the paragraph body.
const ZH_CHAPTER = /^#{0,4}\s*第([零〇一二三四五六七八九十百]+)章/;
const EN_CHAPTER = /^#{0,4}\s*Chapter\s+([IVXLCDM]+|\d+)\b/i;

const ZH_DIGIT: Record<string, number> = {
  零: 0, 〇: 0, 一: 1, 二: 2, 三: 3, 四: 4, 五: 5, 六: 6, 七: 7, 八: 8, 九: 9,
};
const ROMAN: Record<string, number> = { I: 1, V: 5, X: 10, L: 50, C: 100, D: 500, M: 1000 };

/** 「二十一」→ 21. Returns null for anything it cannot read exactly. */
export function chineseNumeral(s: string): number | null {
  if (!s) return null;
  if (!/[十百]/.test(s)) {
    let v = 0;
    for (const ch of s) {
      if (!(ch in ZH_DIGIT)) return null;
      v = v * 10 + ZH_DIGIT[ch];
    }
    return v;
  }
  let acc = 0;
  let digit = 0;
  for (const ch of s) {
    if (ch in ZH_DIGIT) digit = ZH_DIGIT[ch];
    else if (ch === "十") { acc += (digit || 1) * 10; digit = 0; }
    else if (ch === "百") { acc += (digit || 1) * 100; digit = 0; }
    else return null;
  }
  return acc + digit;
}

/** "XXI" → 21, "21" → 21. Returns null for anything it cannot read exactly. */
export function romanNumeral(s: string): number | null {
  if (!s) return null;
  if (/^\d+$/.test(s)) return parseInt(s, 10);
  let total = 0;
  let highest = 0;
  for (const ch of [...s.toUpperCase()].reverse()) {
    const v = ROMAN[ch];
    if (!v) return null;
    total += v >= highest ? v : -v;
    highest = Math.max(highest, v);
  }
  return total;
}

/** Paragraphs carrying a *unique* anchor of one kind, in document order. */
function anchorsOf(
  paras: string[],
  re: RegExp,
  toKey: (raw: string) => string | null = (raw) => raw
): { key: string; index: number }[] {
  const found: { key: string; index: number }[] = [];
  paras.forEach((p, index) => {
    const m = p.match(re);
    if (!m) return;
    const key = toKey(m[1]);
    if (key !== null) found.push({ key, index });
  });
  const seen = new Map<string, number>();
  for (const a of found) seen.set(a.key, (seen.get(a.key) ?? 0) + 1);
  // A repeated marker cannot say which occurrence is which — drop it rather
  // than pick one and risk anchoring the column to the wrong place.
  return found.filter((a) => seen.get(a.key) === 1);
}

/** Anchor pairs shared by both sides, kept strictly increasing on both. */
function pairAnchors(
  zh: { key: string; index: number }[],
  src: { key: string; index: number }[]
): [number, number][] {
  const byKey = new Map(src.map((a) => [a.key, a.index]));
  const pairs: [number, number][] = [];
  let lastSrc = -1;
  for (const a of zh) {
    const si = byKey.get(a.key);
    if (si === undefined || si <= lastSrc) continue;
    pairs.push([a.index, si]);
    lastSrc = si;
  }
  return pairs;
}

/**
 * Re-lay a source column onto the 繁中 column's paragraph slots using shared
 * anchors. Returns an array the same length as `zhParas`, or null when there is
 * nothing reliable to anchor on (fewer than two shared markers) — the caller
 * then falls back to plain index zipping.
 *
 * Within a stretch, paragraphs are zipped from its start — the two sides agree
 * at the anchor, so drift can only accumulate until the next one, where it is
 * reset. A stretch with more source paragraphs than 繁中 slots folds the overflow
 * into its LAST slot, so no source text is ever dropped and no row after it
 * shifts.
 */
export function alignByAnchors(zhParas: string[], srcParas: string[]): string[] | null {
  if (!zhParas.length || !srcParas.length) return null;

  const num = (n: number | null) => (n === null ? null : String(n));
  const schemes: [
    [RegExp, (raw: string) => string | null],
    [RegExp, (raw: string) => string | null],
  ][] = [
    [[LEADING_NUMBER, (r) => r], [LEADING_NUMBER, (r) => r]],
    [[PAGE_MARKER, (r) => r], [PAGE_MARKER, (r) => r]],
    // The two sides number their chapters in different scripts, so both are
    // normalised to an integer before they are compared.
    [[ZH_CHAPTER, (r) => num(chineseNumeral(r))], [EN_CHAPTER, (r) => num(romanNumeral(r))]],
  ];

  // Take the scheme that produces the MOST pairs, not the first that produces
  // any: more anchors means shorter stretches between them, so less room to
  // drift. 《上帝之城》卷十三 has three shared page markers but four shared chapter
  // numbers — stopping at the first hit would have used the coarser one and left
  // the chapter headings a row out of step.
  let pairs: [number, number][] = [];
  for (const [[zhRe, zhKey], [srcRe, srcKey]] of schemes) {
    const p = pairAnchors(anchorsOf(zhParas, zhRe, zhKey), anchorsOf(srcParas, srcRe, srcKey));
    if (p.length > pairs.length) pairs = p;
  }
  if (pairs.length < 2) return null;

  const out = new Array<string>(zhParas.length).fill("");
  const fill = (zFrom: number, zTo: number, sFrom: number, sTo: number) => {
    const src = srcParas.slice(sFrom, sTo);
    if (!src.length) return;
    const span = zTo - zFrom;
    if (span <= 0) {
      // 繁中 has no slot here; hang the text off the previous one rather than
      // dropping it — the source column must never lose text.
      if (zFrom > 0) {
        out[zFrom - 1] = [out[zFrom - 1], ...src].filter(Boolean).join("\n\n");
      }
      return;
    }
    if (src.length <= span) {
      src.forEach((p, k) => { out[zFrom + k] = p; });
      return;
    }
    for (let k = 0; k < span - 1; k++) out[zFrom + k] = src[k];
    out[zTo - 1] = src.slice(span - 1).join("\n\n");
  };

  // Each anchored stretch, first…
  for (let i = 0; i < pairs.length; i++) {
    const [z, s] = pairs[i];
    const zEnd = i + 1 < pairs.length ? pairs[i + 1][0] : zhParas.length;
    const sEnd = i + 1 < pairs.length ? pairs[i + 1][1] : srcParas.length;
    fill(z, zEnd, s, sEnd);
  }
  // …then whatever precedes the first anchor. It runs last because when the
  // first anchor sits at 繁中 index 0 there is no slot of its own to write into,
  // and the text has to be prepended to that anchor's cell — which must already
  // hold its own text by then, or the preamble would be overwritten and lost.
  const [z0, s0] = pairs[0];
  if (z0 === 0) {
    const pre = srcParas.slice(0, s0);
    if (pre.length) out[0] = [...pre, out[0]].filter(Boolean).join("\n\n");
  } else {
    fill(0, z0, 0, s0);
  }
  return out;
}

/**
 * Reader-side parallel grid: zip the 繁中 paragraphs with each source language's
 * paragraphs BY INDEX, padding short columns with "" so one missing paragraph
 * never shifts every following row in another column (same posture as the
 * align-by-number footnote rows). Callers should run `alignByAnchors` first;
 * the reader only zips + pads.
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
