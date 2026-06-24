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
    for (const t of ["review_1_5", "review_6_10", "review_11_15", "review_16_20", "review_all"]) {
      expect(home.includes(t), `home review ${t}`).toBe(true);
    }
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

  it("課程資料 JSON 為 20 課、每課 50 字", () => {
    const p = resolve(root, "public/content/english/lessons.json");
    expect(existsSync(p), "public/content/english/lessons.json").toBe(true);
    const data = JSON.parse(readFileSync(p, "utf8"));
    expect(data.length).toBe(20);
    for (const l of data) {
      expect(l.words.length, `Lesson ${l.no} words`).toBe(50);
      expect(Array.isArray(l.sentences)).toBe(true);
      expect(l.reading, `Lesson ${l.no} reading`).toBeTruthy();
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
