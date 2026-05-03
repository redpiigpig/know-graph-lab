/**
 * 教會年曆計算工具
 * 以將臨期第一主日為教會年起點
 */

// 計算某年的復活節日期（Anonymous Gregorian algorithm）
export function easterDate(year) {
  const a = year % 19
  const b = Math.floor(year / 100)
  const c = year % 100
  const d = Math.floor(b / 4)
  const e = b % 4
  const f = Math.floor((b + 8) / 25)
  const g = Math.floor((b - f + 1) / 3)
  const h = (19 * a + b - d - g + 15) % 30
  const i = Math.floor(c / 4)
  const k = c % 4
  const l = (32 + 2 * e + 2 * i - h - k) % 7
  const m = Math.floor((a + 11 * h + 22 * l) / 451)
  const month = Math.floor((h + l - 7 * m + 114) / 31) - 1 // 0-indexed
  const day = ((h + l - 7 * m + 114) % 31) + 1
  return new Date(year, month, day)
}

// 找某日期之後（含）最近的週日
function nextSunday(date) {
  const d = new Date(date)
  d.setDate(d.getDate() + ((7 - d.getDay()) % 7))
  return d
}

// 找某日期之前（含）最近的週日
function prevSunday(date) {
  const d = new Date(date)
  d.setDate(d.getDate() - d.getDay())
  return d
}

// 加天數
function addDays(date, n) {
  const d = new Date(date)
  d.setDate(d.getDate() + n)
  return d
}

// 日期格式化 YYYY-MM-DD
export function fmt(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

// 計算某教會年（church_year）的所有主日槽位
// church_year = 將臨期第一主日所在的公曆年（如 2024 表示 2024-2025 教會年）
export function getChurchYearSundays(churchYear) {
  // 將臨期第一主日：聖誕節前第四個週日
  // 用 Dec 24 當上限，確保聖誕日本身（即使是週日）不被算成將臨期主日
  const christmas = new Date(churchYear, 11, 25) // Dec 25
  const advent1 = addDays(prevSunday(addDays(christmas, -1)), -21)

  // 下一教會年的將臨期第一主日
  const christmas2 = new Date(churchYear + 1, 11, 25)
  const nextAdvent1 = addDays(prevSunday(addDays(christmas2, -1)), -21)

  // 復活節
  const easter = easterDate(churchYear + 1)
  const ashWednesday = addDays(easter, -46)
  const lent1 = nextSunday(addDays(ashWednesday, 1))   // 大齋期第一主日
  const palmSunday = addDays(easter, -7)               // 棕枝主日（大齋期第六主日）
  const pentecost = addDays(easter, 49)                // 聖靈降臨節
  const trinitySunday = addDays(pentecost, 7)          // 三一主日

  const slots = []

  // ── 將臨期 1–4 ────────────────────────────────────────
  for (let w = 1; w <= 4; w++) {
    slots.push({
      season: 'advent',
      seasonZh: '將臨期',
      week: w,
      label: `將臨期第${w}週`,
      sunday: addDays(advent1, (w - 1) * 7),
    })
  }

  // ── 聖誕期 ─────────────────────────────────────────────
  // 聖誕日（12/25）本身及之後的主日
  const epiphanyDay = new Date(churchYear + 1, 0, 6) // Jan 6 主顯節
  const christmasSunday1 = nextSunday(addDays(christmas, 1))
  const christmasSunday2 = addDays(christmasSunday1, 7)
  slots.push({ season: 'christmas', seasonZh: '聖誕期', week: 1, label: '聖誕期第一週', sunday: christmasSunday1 })
  // 聖誕期第二週：僅在 Jan 2-5 有主日時存在（Jan 6 = 主顯節，不算入聖誕期）
  if (christmasSunday2 < epiphanyDay) {
    slots.push({ season: 'christmas', seasonZh: '聖誕期', week: 2, label: '聖誕期第二週', sunday: christmasSunday2 })
  } else {
    slots.push({ season: 'christmas', seasonZh: '聖誕期', week: 2, label: '聖誕期第二週', sunday: null, optional: true })
  }

  // ── 顯現期 1–9 ────────────────────────────────────────
  // 第一主日：耶穌受洗主日（顯現節後第一個主日）
  const epiphany = new Date(churchYear + 1, 0, 6) // Jan 6
  const epiphany1 = nextSunday(addDays(epiphany, 1))
  for (let w = 1; w <= 9; w++) {
    const sunday = addDays(epiphany1, (w - 1) * 7)
    // 第 9 週固定是登山變相（最後一個顯現期主日），但只有 sunday < lent1
    const isTransfiguration = (w === 9)
    const available = sunday < lent1
    slots.push({
      season: 'epiphany',
      seasonZh: '顯現期',
      week: w,
      label: w === 1 ? '顯現期第1週（耶穌受洗）' : w === 9 ? '顯現期第9週（登山變相）' : `顯現期第${w}週`,
      sunday: available ? sunday : null,
      optional: !available,
    })
  }

  // ── 大齋期 1–6 ────────────────────────────────────────
  for (let w = 1; w <= 6; w++) {
    const sunday = addDays(lent1, (w - 1) * 7)
    slots.push({
      season: 'lent',
      seasonZh: '大齋期',
      week: w,
      label: w === 6 ? '大齋期第6週（棕枝主日）' : `大齋期第${w}週`,
      sunday,
    })
  }

  // ── 復活期 1–7 ────────────────────────────────────────
  for (let w = 1; w <= 7; w++) {
    slots.push({
      season: 'easter',
      seasonZh: '復活期',
      week: w,
      label: w === 1 ? '復活期第1週（復活節）' : w === 7 ? '復活期第7週（聖靈降臨節）' : `復活期第${w}週`,
      sunday: addDays(easter, (w - 1) * 7),
    })
  }

  // ── 聖靈降臨後 Proper 1–29 ────────────────────────────
  // Proper 對應日期範圍（主日落在這個範圍內才適用）
  const properRanges = [
    [5, 11], [12, 18], [19, 25], [26, 1, true], // May 29-Jun 1 跨月用 true
  ]
  // Proper 1: May 24-28, Proper 2: May 29-Jun 4, ..., Proper 29: Nov 20-26
  const properStart = [
    [4, 24], [4, 29], [5, 5], [5, 12], [5, 19], [5, 26],
    [6, 2],  [6, 9],  [6, 16],[6, 23], [6, 30], [7, 7],
    [7, 14], [7, 21], [7, 28],[8, 4],  [8, 11], [8, 18],
    [8, 25], [9, 1],  [9, 8], [9, 15], [9, 22], [9, 29],
    [10, 6], [10, 13],[10, 20],[10, 27],[11, 20],
  ] // [month(0-indexed), day]

  const yr2 = churchYear + 1
  for (let p = 1; p <= 29; p++) {
    const [mo, dy] = properStart[p - 1]
    // 找該週日：從 properStart 日期往後找當週的週日
    const rangeStart = new Date(yr2, mo, dy)
    const sun = nextSunday(rangeStart)
    // 判斷這個主日是否在聖靈降臨後（在 trinitySunday 之後，在 nextAdvent1 之前）
    const available = sun >= trinitySunday && sun < nextAdvent1
    slots.push({
      season: 'pentecost',
      seasonZh: '聖靈降臨後',
      week: p,
      label: p === 1 ? '聖靈降臨後第1週（三一主日）' : `聖靈降臨後第${p}週`,
      sunday: available ? sun : null,
      optional: !available,
    })
  }

  return slots
}

// 判斷甲乙丙年
// 慣例：2022-2023 教會年 = 甲年（Year A），2023-2024 = 乙年，2024-2025 = 丙年
export function getLectionaryYear(churchYear) {
  const cycle = ((churchYear - 2022) % 3 + 3) % 3
  return ['甲', '乙', '丙'][cycle]
}

export function getLectionaryYearEn(churchYear) {
  const cycle = ((churchYear - 2022) % 3 + 3) % 3
  return ['A', 'B', 'C'][cycle]
}

// 根據日期找當前教會年
export function getCurrentChurchYear(date = new Date()) {
  const year = date.getFullYear()
  const christmas = new Date(year, 11, 25)
  const advent1 = addDays(prevSunday(addDays(christmas, -1)), -21)
  return date >= advent1 ? year : year - 1
}

// 找今天屬於哪個槽位
export function findTodaySlot(date = new Date()) {
  const churchYear = getCurrentChurchYear(date)
  const slots = getChurchYearSundays(churchYear)
  const today = new Date(date.getFullYear(), date.getMonth(), date.getDate())

  for (let i = 0; i < slots.length; i++) {
    if (!slots[i].sunday) continue
    const slotStart = new Date(slots[i].sunday)
    const slotEnd = slots[i + 1]?.sunday
      ? new Date(slots[i + 1].sunday)
      : new Date(slotStart.getFullYear(), slotStart.getMonth(), slotStart.getDate() + 7)
    if (today >= slotStart && today < slotEnd) return { churchYear, slot: slots[i] }
  }
  return { churchYear, slot: null }
}

// 固定 57 週結構（通用，不綁定任何年份日期）
export function getFixedLectionarySlots() {
  const slots = []
  const add = (season, count, labelFn) => {
    for (let w = 1; w <= count; w++) slots.push({ season, week: w, label: labelFn(w) })
  }
  add('advent',    4,  w => `將臨期第${w}週`)
  add('christmas', 2,  w => w === 1 ? '聖誕期第1週' : '聖誕期第2週')
  add('epiphany',  9,  w => w === 1 ? '顯現期第1週（耶穌受洗）' : w === 9 ? '顯現期第9週（登山變相）' : `顯現期第${w}週`)
  add('lent',      6,  w => w === 6 ? '大齋期第6週（棕枝主日）' : `大齋期第${w}週`)
  add('easter',    7,  w => w === 1 ? '復活期第1週（復活節）' : w === 7 ? '復活期第7週（聖靈降臨節）' : `復活期第${w}週`)
  add('pentecost', 29, w => w === 1 ? '聖靈降臨後第1週（三一主日）' : `聖靈降臨後第${w}週`)
  return slots // 4+2+9+6+7+29 = 57
}

export const SEASON_COLORS = {
  advent:    { bg: '#4A3580', light: '#6B52B0', text: '#fff', name: '將臨期' },
  christmas: { bg: '#8B6914', light: '#C4971E', text: '#fff', name: '聖誕期' },
  epiphany:  { bg: '#1A6B3A', light: '#2A9B55', text: '#fff', name: '顯現期' },
  lent:      { bg: '#6B2060', light: '#9B3088', text: '#fff', name: '大齋期' },
  easter:    { bg: '#A07820', light: '#D4A830', text: '#fff', name: '復活期' },
  pentecost: { bg: '#1E5A2E', light: '#2E8A45', text: '#fff', name: '聖靈降臨後' },
}
