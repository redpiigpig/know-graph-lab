export const BORDER_STYLES = [
  { id: 'solid-sm',    label: '細實線圓角',  borderWidth: 1, borderStyle: 'solid',  borderRadius: 12 },
  { id: 'solid-md',    label: '標準實線圓角', borderWidth: 2, borderStyle: 'solid',  borderRadius: 12 },
  { id: 'solid-lg',    label: '粗實線圓角',  borderWidth: 3, borderStyle: 'solid',  borderRadius: 12 },
  { id: 'dashed-md',   label: '虛線圓角',   borderWidth: 2, borderStyle: 'dashed', borderRadius: 12 },
  { id: 'dotted-md',   label: '點線圓角',   borderWidth: 2, borderStyle: 'dotted', borderRadius: 12 },
  { id: 'double-md',   label: '雙重線圓角', borderWidth: 4, borderStyle: 'double', borderRadius: 12 },
  { id: 'solid-sharp', label: '實線方角',   borderWidth: 2, borderStyle: 'solid',  borderRadius: 4 },
  { id: 'dashed-sharp',label: '虛線方角',   borderWidth: 2, borderStyle: 'dashed', borderRadius: 4 },
] as const

export const EDGE_COLORS = [
  '#ef4444', '#f97316', '#f59e0b', '#eab308',
  '#84cc16', '#22c55e', '#14b8a6', '#06b6d4',
  '#3b82f6', '#6366f1', '#8b5cf6', '#a855f7',
  '#ec4899', '#f43f5e', '#6b7280', '#111827',
] as const

export const EDGE_DASH_STYLES = [
  { id: 'solid',    label: '實線',   dasharray: '' },
  { id: 'dashed',   label: '虛線',   dasharray: '8,4' },
  { id: 'dotted',   label: '點線',   dasharray: '2,4' },
  { id: 'longdash', label: '長虛線', dasharray: '16,4,4,4' },
] as const

export const EDGE_LINE_TYPES = [
  { id: 'smoothstep', label: '曲折線',    desc: '轉角平滑' },
  { id: 'step',       label: '直角折線',  desc: '90° 折角' },
  { id: 'straight',   label: '直線',      desc: '端點直連' },
  { id: 'default',    label: '貝塞爾曲線', desc: '弧形曲線' },
] as const

export type BorderStyleId = typeof BORDER_STYLES[number]['id']
export type EdgeDashStyleId = typeof EDGE_DASH_STYLES[number]['id']
export type EdgeLineTypeId = typeof EDGE_LINE_TYPES[number]['id']

export interface LegendState {
  colors: Record<string, string>      // hex → 使用者命名
  lineStyles: Record<string, string>  // dashStyleId → 使用者命名
}
