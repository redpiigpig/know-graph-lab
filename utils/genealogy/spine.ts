// Shared spine-resolution helpers for the genealogy spine trees.
// Extracted from BiblicalSpineTree.vue / IslamicSpineTree.vue (was duplicated verbatim).
//
// 一條「脊柱」由一串 waypoint 名字定義；相鄰 waypoint 之間用 BFS 在 parent→child
// 圖上找最短下行路徑，串起來成完整脊柱。任一 waypoint 名字解析不到、或相鄰兩站之間
// 沒有下行路徑，會「降級」回傳能解析到的前綴（而非整條 []），呼叫端據此畫出可解析的
// 部分並標記斷點，不再一個壞名字就整棵空白。dev 模式同時 console.warn 點名斷點。
// （findings B1/I1）

/** BFS shortest descent path from src to dst over a parent→children adjacency map. */
export function bfsPath(src: string, dst: string, ch: Map<string, string[]>): string[] {
  if (src === dst) return [src]
  const queue: string[][] = [[src]]
  const vis = new Set<string>()
  while (queue.length) {
    const path = queue.shift()!
    const cur = path[path.length - 1]
    if (cur === dst) return path
    if (vis.has(cur)) continue
    vis.add(cur)
    for (const c of ch.get(cur) ?? []) if (!vis.has(c)) queue.push([...path, c])
  }
  return []
}

export interface SpineDiagnostics {
  /** longest resolvable spine prefix (may be partial when full === false) */
  path: string[]
  /** true when every waypoint resolved AND every segment connected end-to-end */
  full: boolean
  /** waypoint names that could not be resolved to a person id */
  missing: string[]
  /** the first segment that had no descent path, by waypoint name */
  brokenAt?: { from: string; to: string }
}

export interface SpineOptions {
  /** label used in the dev warning (e.g. 'A' / 'B' / 'spine') */
  label?: string
  /** force-enable/disable the dev warning; defaults to import.meta.env.DEV */
  warn?: boolean
}

/**
 * Resolve a spine from an ordered list of waypoint NAMES, degrading gracefully.
 * `resolve` maps a name → person id (closure over the component's name index).
 *
 * On a broken/unresolvable spine it returns the path resolved SO FAR (the
 * resolvable prefix) + diagnostics, instead of collapsing to []. The caller can
 * then render its resolvable part and mark the break, rather than going blank on
 * one bad waypoint. When the data is complete, `full === true` and `path` is the
 * exact same end-to-end path the old resolver produced — so the happy path is
 * unchanged. dev 模式下也 console.warn 點名斷點（findings B1/I1）。
 */
export function resolveSpineWithDiagnostics(
  names: string[],
  ch: Map<string, string[]>,
  resolve: (name: string) => string | undefined,
  opts: SpineOptions = {},
): SpineDiagnostics {
  const warn = opts.warn ?? (import.meta as any)?.env?.DEV ?? false
  const tag = opts.label ? `[spine ${opts.label}] ` : '[spine] '

  const resolved = names.map(n => ({ name: n, id: resolve(n) }))
  const missing = resolved.filter(r => !r.id).map(r => r.name)
  if (warn && missing.length) {
    console.warn(`${tag}找不到 ${missing.length} 個 waypoint 人物：${missing.join('、')}（脊柱會降級成可解析的部分）`)
  }

  const ids = resolved.filter(r => r.id).map(r => r.id!) as string[]
  const idToName = new Map(resolved.filter(r => r.id).map(r => [r.id!, r.name]))
  if (ids.length < 2) {
    if (warn) console.warn(`${tag}可解析的 waypoint 不足 2 個 → 脊柱無法建立`)
    return { path: [], full: false, missing }
  }

  const path: string[] = []
  for (let i = 0; i < ids.length - 1; i++) {
    const seg = bfsPath(ids[i], ids[i + 1], ch)
    if (!seg.length) {
      if (!path.length) path.push(ids[i])  // keep at least the prefix anchor
      const from = idToName.get(ids[i]) ?? ids[i]
      const to = idToName.get(ids[i + 1]) ?? ids[i + 1]
      if (warn) console.warn(`${tag}「${from}」→「${to}」之間找不到下行路徑 → 脊柱在此斷裂，只畫到「${from}」`)
      return { path, full: false, missing, brokenAt: { from, to } }
    }
    if (i === 0) path.push(...seg)
    else path.push(...seg.slice(1))
  }
  return { path, full: missing.length === 0, missing }
}
