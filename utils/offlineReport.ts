// ============================================================================
// FSI 離線練習 · 成果報告（零 AI 純函式）
//   工作流：下載 Word 練習包 → 上傳 NotebookLM/Gemini 練習 → AI 依模板輸出
//   成果報告 → 貼回 /coach/[lang]/offline → parseOfflineReport() 確定性解析入庫。
//   模板與解析器放同一檔，格式改動兩邊永遠同步；前端（顯示模板）與
//   server（docx 匯出、import 端點）共用。
// ============================================================================

export const REPORT_BEGIN = "【練習成果報告】";
export const REPORT_END = "【報告結束】";

export interface OfflineReportWord {
  word: string;
  reading: string | null;
  meaning: string;
  example: string | null;
}

export interface OfflineReport {
  date: string | null; // YYYY-MM-DD（報告沒寫或格式錯 → null，由呼叫端補今天）
  content: string; // 練習內容一句話
  skills: { skill: string; minutes: number }[]; // canonical: listening/speaking/reading/writing
  overall: number | null; // 0–100
  strengths: string[];
  improvements: string[];
  newWords: OfflineReportWord[];
  reviews: { word: string; correct: boolean }[];
  corrections: { original: string; fixed: string }[];
}

/** 給外部 AI（NotebookLM / Gemini）在練習結束時原樣填寫的模板 */
export function reportTemplate(langLabel: string): string {
  return `${REPORT_BEGIN}
語言：${langLabel}
日期：YYYY-MM-DD
練習內容：（一句話：這次練了哪些 drill / 主題）
技能時間：口說 20 分、寫作 10 分、閱讀 10 分、聽力 0 分
整體評分：75
強項：
- （這次表現好的點）
待加強：
- （反覆出錯的文法或詞彙點）
新學單字：
- 單字｜讀音｜繁體中文釋義｜例句
複習結果：
- 單字｜對
- 單字｜錯
改錯紀錄：
- 原句 → 修正句
${REPORT_END}`;
}

const SKILL_ALIAS: Record<string, string> = {
  聽力: "listening", 聽: "listening", listening: "listening",
  口說: "speaking", 口語: "speaking", 會話: "speaking", speaking: "speaking",
  閱讀: "reading", 讀: "reading", reading: "reading",
  寫作: "writing", 寫: "writing", writing: "writing",
};

const SECTION_ALIAS: Record<string, keyof OfflineReport | "strengths" | "improvements" | "newWords" | "reviews" | "corrections"> = {
  強項: "strengths",
  待加強: "improvements", 需加強: "improvements", 弱點: "improvements",
  新學單字: "newWords", 學會單字: "newWords", 新單字: "newWords",
  複習結果: "reviews",
  改錯紀錄: "corrections", 改錯: "corrections",
};

const hasCjk = (s: string) => /[㐀-鿿]/.test(s);

const CORRECT_MARKS = ["對", "正確", "會", "✓", "✔", "o", "correct", "right", "pass"];
const WRONG_MARKS = ["錯", "不會", "忘", "×", "✗", "x", "wrong", "fail", "again"];

function parseDate(s: string): string | null {
  const m = s.match(/(\d{4})\s*[-/年.]\s*(\d{1,2})\s*[-/月.]\s*(\d{1,2})/);
  if (!m) return null;
  const [y, mo, d] = [Number(m[1]), Number(m[2]), Number(m[3])];
  if (mo < 1 || mo > 12 || d < 1 || d > 31) return null;
  return `${y}-${String(mo).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
}

function parseSkills(s: string): { skill: string; minutes: number }[] {
  const out: Record<string, number> = {};
  const re = /(聽力|口說|口語|會話|閱讀|寫作|listening|speaking|reading|writing|聽|讀|寫)\s*[:：]?\s*(\d+(?:\.\d+)?)\s*分/gi;
  for (const m of s.matchAll(re)) {
    const key = SKILL_ALIAS[m[1].toLowerCase()] ?? SKILL_ALIAS[m[1]];
    const min = Number(m[2]);
    if (key && min > 0) out[key] = (out[key] || 0) + min;
  }
  return Object.entries(out).map(([skill, minutes]) => ({ skill, minutes }));
}

/** 「單字｜讀音｜繁中釋義｜例句」，容忍 2–3 欄與半形 | */
function parseWordLine(s: string): OfflineReportWord | null {
  const parts = s.split(/[｜|]/).map((p) => p.trim());
  if (!parts[0]) return null;
  const blank = (v?: string) => !v || v === "－" || v === "-" || v === "—";
  if (parts.length >= 4) {
    return { word: parts[0], reading: blank(parts[1]) ? null : parts[1], meaning: parts[2] ?? "", example: blank(parts[3]) ? null : parts.slice(3).join("｜") };
  }
  if (parts.length === 3) {
    // 第二欄是繁中 → 視為 單字｜釋義｜例句；否則 單字｜讀音｜釋義
    if (hasCjk(parts[1])) return { word: parts[0], reading: null, meaning: parts[1], example: blank(parts[2]) ? null : parts[2] };
    return { word: parts[0], reading: blank(parts[1]) ? null : parts[1], meaning: parts[2] ?? "", example: null };
  }
  if (parts.length === 2) return { word: parts[0], reading: null, meaning: parts[1], example: null };
  return null;
}

function parseReviewLine(s: string): { word: string; correct: boolean } | null {
  const parts = s.split(/[｜|]/).map((p) => p.trim());
  let word = parts[0];
  let mark = parts.length > 1 ? parts[parts.length - 1] : "";
  if (parts.length === 1) {
    // 「word ✓」尾標式
    const m = s.match(/^(.*?)\s*([✓✔×✗ox對錯])\s*$/i);
    if (!m) return null;
    word = m[1].trim();
    mark = m[2];
  }
  if (!word) return null;
  const low = mark.toLowerCase();
  if (CORRECT_MARKS.includes(low) || CORRECT_MARKS.includes(mark)) return { word, correct: true };
  if (WRONG_MARKS.includes(low) || WRONG_MARKS.includes(mark)) return { word, correct: false };
  return null;
}

function parseCorrectionLine(s: string): { original: string; fixed: string } | null {
  const parts = s.split(/\s*(?:→|⇒|➔|=>)\s*/);
  if (parts.length < 2 || !parts[0].trim() || !parts[1].trim()) return null;
  return { original: parts[0].trim(), fixed: parts.slice(1).join(" → ").trim() };
}

/**
 * 從任意貼上的文字（可含整段對話）找出成果報告區塊並解析。
 * 找不到 REPORT_BEGIN 標記 → null。缺 REPORT_END 則解析到文末。
 */
export function parseOfflineReport(text: string): OfflineReport | null {
  const begin = text.indexOf(REPORT_BEGIN);
  if (begin < 0) return null;
  let block = text.slice(begin + REPORT_BEGIN.length);
  const end = block.indexOf(REPORT_END);
  if (end >= 0) block = block.slice(0, end);

  const report: OfflineReport = {
    date: null, content: "", skills: [], overall: null,
    strengths: [], improvements: [], newWords: [], reviews: [], corrections: [],
  };

  let mode: string | null = null;
  for (const raw of block.split(/\r?\n/)) {
    const line = raw.trim();
    if (!line) continue;

    // key: value 行
    const kv = line.match(/^(語言|日期|練習內容|總時間|技能時間|整體評分)\s*[:：]\s*(.*)$/);
    if (kv) {
      mode = null;
      const [, key, val] = kv;
      if (key === "日期") report.date = parseDate(val);
      else if (key === "練習內容") report.content = val.trim();
      else if (key === "技能時間") report.skills.push(...parseSkills(val));
      else if (key === "總時間" && !report.skills.length) {
        // 只給總時間沒拆技能 → 歸口說（離線練習主體是會話 drill）
        const m = val.match(/(\d+(?:\.\d+)?)/);
        if (m && Number(m[1]) > 0) report.skills.push({ skill: "speaking", minutes: Number(m[1]) });
      } else if (key === "整體評分") {
        const m = val.match(/(\d+(?:\.\d+)?)/);
        if (m) report.overall = Math.min(100, Math.max(0, Number(m[1])));
      }
      continue;
    }

    // 分節標題行
    const sec = line.match(/^[#＃\s]*(強項|待加強|需加強|弱點|新學單字|學會單字|新單字|複習結果|改錯紀錄|改錯)\s*[:：]?\s*$/);
    if (sec) { mode = SECTION_ALIAS[sec[1]] as string; continue; }

    // 清單項
    const item = line.match(/^\s*(?:[-•‧*·]|\d+[.)、])\s*(.+)$/);
    if (!item || !mode) continue;
    const body = item[1].trim();
    if (/^（.*）$/.test(body)) continue; // 模板占位文字沒被替換 → 略過
    if (mode === "strengths") report.strengths.push(body);
    else if (mode === "improvements") report.improvements.push(body);
    else if (mode === "newWords") { const w = parseWordLine(body); if (w) report.newWords.push(w); }
    else if (mode === "reviews") { const r = parseReviewLine(body); if (r) report.reviews.push(r); }
    else if (mode === "corrections") { const c = parseCorrectionLine(body); if (c) report.corrections.push(c); }
  }

  return report;
}

/** 報告是否有任何可入庫的內容 */
export function reportHasData(r: OfflineReport): boolean {
  return r.skills.length > 0 || r.newWords.length > 0 || r.reviews.length > 0 || r.corrections.length > 0;
}
