// Shared spine-resolution helpers for the genealogy spine trees.
// Extracted from BiblicalSpineTree.vue / IslamicSpineTree.vue (was duplicated verbatim).
//
// 一條「脊柱」由一串 waypoint 名字定義；相鄰 waypoint 之間用 BFS 在 parent→child
// 圖上找最短下行路徑，串起來成完整脊柱。任一 waypoint 名字解析不到、或相鄰兩站
// 之間沒有下行路徑，整條脊柱回 []（呼叫端通常因此整棵樹空白）——所以 dev 模式下
// 會 warn 出「是哪個名字/哪一段」斷掉，避免只看到白畫面 debug 不到（findings B1/I1）。

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

export interface SpineWarnOptions {
  /** label used in the dev warning (e.g. 'A' / 'B' / 'spine') */
  label?: string
  /** force-enable/disable the dev warning; defaults to import.meta.dev */
  warn?: boolean
}

/**
 * Resolve a spine from an ordered list of waypoint NAMES.
 * `resolve` maps a name → person id (closure over the component's name index).
 * Returns the full id path, or [] if it cannot be resolved end-to-end.
 */
export function spineFromWaypoints(
  names: string[],
  ch: Map<string, string[]>,
  resolve: (name: string) => string | undefined,
  opts: SpineWarnOptions = {},
): string[] {
  const warn = opts.warn ?? (import.meta as any)?.env?.DEV ?? false
  const label = opts.label ? `[spine ${opts.label}] ` : '[spine] '

  const resolved = names.map(n => ({ name: n, id: resolve(n) }))
  const missing = resolved.filter(r => !r.id).map(r => r.name)
  if (warn && missing.length) {
    console.warn(`${label}找不到 ${missing.length} 個 waypoint 人物（已略過）：${missing.join('、')}`)
  }

  const ids = resolved.map(r => r.id).filter(Boolean) as string[]
  if (ids.length < 2) {
    if (warn) console.warn(`${label}可解析的 waypoint 不足 2 個 → 脊柱無法建立、整棵樹會空白`)
    return []
  }

  const idToName = new Map(resolved.filter(r => r.id).map(r => [r.id!, r.name]))
  const path: string[] = []
  for (let i = 0; i < ids.length - 1; i++) {
    const seg = bfsPath(ids[i], ids[i + 1], ch)
    if (!seg.length) {
      if (warn) {
        const from = idToName.get(ids[i]) ?? ids[i]
        const to = idToName.get(ids[i + 1]) ?? ids[i + 1]
        console.warn(`${label}「${from}」→「${to}」之間找不到下行路徑 → 脊柱斷裂、整棵樹會空白`)
      }
      return []
    }
    if (i === 0) path.push(...seg)
    else path.push(...seg.slice(1))
  }
  return path
}
