// @vitest-environment node
import { describe, it, expect } from "vitest";
import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(__dirname, "../..");
const has = (p: string) => existsSync(resolve(root, p));

describe("Happy English 教學網站結構完整性", () => {
  it("portal 頁面都存在", () => {
    for (const p of [
      "pages/english/index.vue",
      "pages/english/[no]/index.vue",
      "pages/english/[no]/[quiz].vue",
      "pages/english/review/[range].vue",
      "components/EnglishQuizRunner.vue",
      "utils/englishQuiz.ts",
    ]) {
      expect(has(p), p).toBe(true);
    }
  });

  it("複習測驗：段考 + 總複習，計分 API 接受 review_*", () => {
    const score = readFileSync(resolve(root, "server/api/english/score.post.ts"), "utf8");
    expect(score).toMatch(/review_\(all/); // isReviewType regex
    const home = readFileSync(resolve(root, "pages/english/index.vue"), "utf8");
    // 段考清單改成依 LESSON_COUNT 每 5 課生一組（原本是寫死的五個字面字串），
    // 課數再變也不用改這裡；總複習仍是固定的 review_all。
    expect(home).toContain("const LESSON_COUNT = 50");
    expect(home).toContain("review_${from}_${to}");
    expect(home).toContain("review_all");
  });

  it("段考分組覆蓋全部 50 課且不重疊", () => {
    const total = 50;
    const groups = Array.from({ length: Math.ceil(total / 5) }, (_, i) => {
      const from = i * 5 + 1;
      return [from, Math.min(from + 4, total)];
    });
    expect(groups.length).toBe(10);
    expect(groups[0]).toEqual([1, 5]);
    expect(groups.at(-1)).toEqual([46, 50]);
    expect(groups.flatMap(([a, b]) =>
      Array.from({ length: b - a + 1 }, (_, k) => a + k),
    )).toEqual(Array.from({ length: total }, (_, i) => i + 1));
  });

  it("單元頁顯示學習計時（⏱）", () => {
    const hub = readFileSync(resolve(root, "pages/english/[no]/index.vue"), "utf8");
    expect(hub).toContain("activeSeconds");
    expect(hub).toContain("⏱");
  });

  it("登入 middleware 限定 julia5868 與站長", () => {
    expect(has("middleware/english-auth.ts")).toBe(true);
    const mw = readFileSync(resolve(root, "middleware/english-auth.ts"), "utf8");
    expect(mw).toContain("julia5868@yahoo.com.tw");
  });

  it("server 端點都存在", () => {
    for (const e of ["activity.post.ts", "progress.get.ts", "score.post.ts", "scores.get.ts"]) {
      expect(has(`server/api/english/${e}`), e).toBe(true);
    }
  });

  it("時間追蹤 composable 與資料表 schema 存在", () => {
    expect(has("composables/useEnglishTracker.ts")).toBe(true);
    expect(has("database/english-learning.sql")).toBe(true);
    expect(has("scripts/apply-english-schema.mjs")).toBe(true);
  });

  // 2026-09-08 起網站跟課本、單字卡一致，都是 50 課 × 20 字（原本 20 課 × 50 字）
  it("課程資料 JSON 為 50 課、每課 20 字", () => {
    const p = resolve(root, "public/content/english/lessons.json");
    expect(existsSync(p), "public/content/english/lessons.json").toBe(true);
    const data = JSON.parse(readFileSync(p, "utf8"));
    expect(data.length).toBe(50);
    expect(data.map((l: any) => l.no)).toEqual(
      Array.from({ length: 50 }, (_, i) => i + 1),
    );
    for (const l of data) {
      expect(l.words.length, `Lesson ${l.no} words`).toBe(20);
      expect(Array.isArray(l.sentences)).toBe(true);
      expect(l.reading, `Lesson ${l.no} reading`).toBeTruthy();
    }
  });

  it("測驗題庫要抽得到題：每課都有選擇題與造句題", () => {
    const p = resolve(root, "public/content/english/lessons.json");
    const data = JSON.parse(readFileSync(p, "utf8"));
    for (const l of data) {
      const types = new Set(l.exercises.map((e: any) => e.type));
      // utils/englishQuiz.ts 的 grammarMCQ 吃 choice、sentenceItems 吃這三種
      for (const t of ["choice", "fill", "unscramble", "translate"]) {
        expect(types.has(t), `Lesson ${l.no} 缺 ${t}`).toBe(true);
      }
      for (const ex of l.exercises) {
        if (ex.type !== "choice") continue;
        for (const it of ex.items) {
          expect(it.opts, `Lesson ${l.no} 選項`).toHaveLength(4);
          expect(it.opts, `Lesson ${l.no} 答案不在選項內`).toContain(it.ans);
        }
      }
    }
  });

  it("5 種測驗 type 都在 quiz 產生器被處理", () => {
    const src = readFileSync(resolve(root, "utils/englishQuiz.ts"), "utf8");
    for (const t of ["vocab", "listening", "speaking", "sentence", "comprehensive"]) {
      expect(src.includes(`"${t}"`), `quiz type ${t}`).toBe(true);
    }
  });

  it("朗讀速度為 0.75 倍", () => {
    const runner = readFileSync(resolve(root, "components/EnglishQuizRunner.vue"), "utf8");
    expect(runner).toContain("0.75");
  });
});
