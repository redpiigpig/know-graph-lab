// @vitest-environment node
import { describe, it, expect } from "vitest";
import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(__dirname, "../..");
const has = (p: string) => existsSync(resolve(root, p));

describe("Happy English 教學網站結構完整性", () => {
  it("portal 頁面都存在", () => {
    for (const p of ["pages/english/index.vue", "pages/english/[no]/index.vue", "pages/english/[no]/[quiz].vue"]) {
      expect(has(p), p).toBe(true);
    }
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

  it("5 種測驗 type 都在 quiz 頁面被處理", () => {
    const src = readFileSync(resolve(root, "pages/english/[no]/[quiz].vue"), "utf8");
    for (const t of ["vocab", "listening", "speaking", "sentence", "comprehensive"]) {
      expect(src.includes(`"${t}"`), `quiz type ${t}`).toBe(true);
    }
    // 朗讀速度 0.75 倍
    expect(src).toContain("0.75");
  });
});
