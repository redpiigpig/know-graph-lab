// ============================================================================
// 「今天」一律用站長所在時區（Asia/Taipei）計算。
// Zeabur 伺服器跑 UTC，若用 new Date().toISOString().slice(0,10) 會在台灣
// 凌晨 0–8 點把日期算成「昨天」→ streak/今日時間/日曆/到期單字全錯一天。
// 單人私站，時區直接寫死台北即可。
// ============================================================================
const TZ = "Asia/Taipei";

// 現在（台北）的日期，格式 YYYY-MM-DD（en-CA locale 剛好給這個格式）
export function tzToday(): string {
  return new Date().toLocaleDateString("en-CA", { timeZone: TZ });
}

// 現在（台北）的月份，格式 YYYY-MM
export function tzMonth(): string {
  return tzToday().slice(0, 7);
}

// 台北日期往前 n 天，格式 YYYY-MM-DD（台灣無 DST，扣毫秒再轉時區即精確）
export function tzDaysAgo(n: number): string {
  return new Date(Date.now() - n * 86400000).toLocaleDateString("en-CA", { timeZone: TZ });
}
