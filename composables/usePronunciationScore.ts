// ============================================================================
// 發音跟讀「零服務」確定性評分（不呼叫任何 AI／雲端）。
// 把目標句與 Web Speech 辨識結果做「詞級序列對齊」(edit-distance + 回溯)，
// 每個目標詞判為 hit(唸對) / near(近似，附聽成什麼) / miss(漏或錯)，
// near 用 Levenshtein 相似度判定並給半分。純函式，可單元測試。
//   scorePronunciation(target, heard) -> { tokens, score, hits, near, miss, total }
// 適用所有語言（拉丁字母、希臘、希伯來、假名…）：比對走 Unicode 字母正規化。
// ============================================================================

export interface WordVerdict {
  text: string;        // 原樣顯示（含大小寫/標點）
  isWord: boolean;     // 是否為可比對的詞（false = 標點）
  status?: "hit" | "near" | "miss";
  heardAs?: string;    // near/miss 時，辨識實際聽到的詞（若有對到一個近似詞）
}
export interface PronScore {
  tokens: WordVerdict[];
  score: number;       // 0–100，hit=1 near=0.5 miss=0 加權
  hits: number;
  near: number;
  miss: number;
  total: number;       // 目標詞總數
}

const NEAR_THRESHOLD = 0.6; // Levenshtein 相似度 ≥ 此值算「近似」(發音接近但不準)

// 顯示用切詞：詞 + 標點（不含空白）。詞 = 連續字母（含 ' ’ - 內嵌）。
export function displayTokens(s: string): string[] {
  return s.match(/[\p{L}\p{M}][\p{L}\p{M}'’\-]*|[^\p{L}\p{M}\s]+/gu) || [];
}

// 正規化一個詞供比對：小寫、只留字母與結合附加符號。
function norm(w: string): string {
  return (w.toLowerCase().match(/[\p{L}\p{M}]/gu) || []).join("");
}

function isWordToken(t: string): boolean {
  return /[\p{L}\p{M}]/u.test(t);
}

// Levenshtein 距離 → 相似度比例 (0–1)。
export function similarity(a: string, b: string): number {
  if (!a && !b) return 1;
  if (!a || !b) return 0;
  const m = a.length, n = b.length;
  const dp = Array.from({ length: m + 1 }, (_, i) => i);
  for (let j = 1; j <= n; j++) {
    let prev = dp[0];
    dp[0] = j;
    for (let i = 1; i <= m; i++) {
      const tmp = dp[i];
      dp[i] = a[i - 1] === b[j - 1] ? prev : 1 + Math.min(prev, dp[i], dp[i - 1]);
      prev = tmp;
    }
  }
  return 1 - dp[m] / Math.max(m, n);
}

// 對目標詞序列 T 與辨識詞序列 H 做最小編輯距離對齊，回每個 T[i] 的判定。
// 回傳陣列長度 = T.length，元素 { status, heardAs? }。
function alignWords(T: string[], H: string[]): { status: "hit" | "near" | "miss"; heardAs?: string }[] {
  const m = T.length, n = H.length;
  const dp = Array.from({ length: m + 1 }, () => new Array(n + 1).fill(0));
  for (let i = 0; i <= m; i++) dp[i][0] = i;
  for (let j = 0; j <= n; j++) dp[0][j] = j;
  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      const sub = dp[i - 1][j - 1] + (T[i - 1] === H[j - 1] ? 0 : 1);
      dp[i][j] = Math.min(sub, dp[i - 1][j] + 1, dp[i][j - 1] + 1);
    }
  }
  // 回溯
  const res: { status: "hit" | "near" | "miss"; heardAs?: string }[] = new Array(m);
  let i = m, j = n;
  while (i > 0 || j > 0) {
    if (i > 0 && j > 0 && dp[i][j] === dp[i - 1][j - 1] + (T[i - 1] === H[j - 1] ? 0 : 1)) {
      if (T[i - 1] === H[j - 1]) {
        res[i - 1] = { status: "hit" };
      } else {
        const sim = similarity(T[i - 1], H[j - 1]);
        res[i - 1] = { status: sim >= NEAR_THRESHOLD ? "near" : "miss", heardAs: H[j - 1] };
      }
      i--; j--;
    } else if (i > 0 && dp[i][j] === dp[i - 1][j] + 1) {
      res[i - 1] = { status: "miss" }; // 目標詞沒被唸到（刪除）
      i--;
    } else {
      j--; // 辨識多出的詞（插入）→ 不影響目標詞判定
    }
  }
  return res;
}

export function scorePronunciation(target: string, heard: string): PronScore {
  const disp = displayTokens(target);
  const tokens: WordVerdict[] = disp.map((t) => ({ text: t, isWord: isWordToken(t) }));
  const wordPositions: number[] = [];
  const T: string[] = [];
  tokens.forEach((tk, idx) => {
    if (tk.isWord) {
      const nw = norm(tk.text);
      if (nw) { T.push(nw); wordPositions.push(idx); }
      else tk.isWord = false; // 純標點被誤判 → 當非詞
    }
  });
  const H = displayTokens(heard).filter(isWordToken).map(norm).filter(Boolean);

  if (!heard.trim() || T.length === 0) {
    return { tokens, score: 0, hits: 0, near: 0, miss: T.length, total: T.length };
  }

  const verdicts = alignWords(T, H);
  let hits = 0, near = 0, miss = 0;
  verdicts.forEach((v, k) => {
    const tk = tokens[wordPositions[k]];
    tk.status = v.status;
    if (v.heardAs) tk.heardAs = v.heardAs;
    if (v.status === "hit") hits++;
    else if (v.status === "near") near++;
    else miss++;
  });
  const total = T.length;
  const score = Math.round(((hits + near * 0.5) / total) * 100);
  return { tokens, score, hits, near, miss, total };
}
