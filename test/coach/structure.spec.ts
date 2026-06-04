// @vitest-environment node
import { describe, it, expect } from "vitest";
import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(__dirname, "../..");
const has = (p: string) => existsSync(resolve(root, p));

describe("語言教練檔案結構完整性", () => {
  it("所有 [lang] 頁面都存在", () => {
    const pages = ["index", "today", "chat", "smalltalk", "grammar", "courses", "practice", "review", "immersion", "dashboard"];
    for (const p of pages) {
      expect(has(`pages/coach/[lang]/${p}.vue`), `pages/coach/[lang]/${p}.vue`).toBe(true);
    }
    expect(has("pages/coach/index.vue")).toBe(true);
  });

  it("登入相關頁面與 middleware 存在", () => {
    expect(has("pages/login.vue")).toBe(true);
    expect(has("middleware/coach-auth.ts")).toBe(true);
  });

  it("關鍵 server 端點都存在", () => {
    const eps = [
      "chat.post.ts", "profile.get.ts", "profile.put.ts", "progress.get.ts", "progress.put.ts",
      "activity.post.ts", "dashboard.get.ts", "usage.get.ts", "assess.post.ts", "briefing.get.ts",
      "memory.get.ts", "memory/regenerate.post.ts", "journal.get.ts", "journal/generate.post.ts",
      "sessions.get.ts", "messages.get.ts", "coaches.get.ts",
      "vocab/index.get.ts", "vocab/generate.post.ts", "vocab/review.get.ts", "vocab/review.post.ts",
      "task/generate.post.ts", "task/[id]/answer.post.ts",
      "smalltalk/start.post.ts", "smalltalk/feedback.post.ts",
      "content/ingest.post.ts", "content/index.get.ts",
      "grammar/index.get.ts", "grammar/lesson.post.ts", "grammar/done.post.ts",
      "courses/index.get.ts", "courses/create.post.ts", "courses/[id].get.ts", "courses/lesson.post.ts", "courses/done.post.ts",
      "daily.get.ts", "daily/item.post.ts", "daily/done.post.ts",
    ];
    for (const e of eps) expect(has(`server/api/lang/${e}`), `server/api/lang/${e}`).toBe(true);
  });

  it("共用 util / composable 存在", () => {
    for (const u of ["gemini.ts", "coach-ai.ts", "lang-coaches.ts", "srs.ts"]) {
      expect(has(`server/utils/${u}`)).toBe(true);
    }
    for (const c of ["useCoachAi.ts", "useSpeech.ts", "useActivityTracker.ts"]) {
      expect(has(`composables/${c}`)).toBe(true);
    }
  });

  it("DB migration SQL 都存在", () => {
    const sqls = [
      "language-coach-schema", "language-coach-personalization", "language-coach-pillars-bcde",
      "language-coach-keys-usage", "language-coach-v2", "language-coach-journal",
      "language-coach-briefing-cache", "language-coach-grammar", "language-coach-daily",
      "language-coach-courses", "trusted-devices",
    ];
    for (const s of sqls) expect(has(`database/${s}.sql`), `database/${s}.sql`).toBe(true);
  });
});

describe("SKILL.md 準確性", () => {
  const skillPath = ".claude/skills/coach-language/SKILL.md";
  it("skill 存在且 frontmatter name=coach-language", () => {
    expect(has(skillPath)).toBe(true);
    const md = readFileSync(resolve(root, skillPath), "utf-8");
    expect(md).toMatch(/^---[\s\S]*name:\s*coach-language/);
  });

  it("skill 提到的關鍵頁面/功能字眼存在", () => {
    const md = readFileSync(resolve(root, ".claude/skills/coach-language/SKILL.md"), "utf-8");
    for (const kw of ["今日計畫", "主題教程", "文法課", "情境角色", "問答", "OTP", "付費", "gemini-flash-latest"]) {
      expect(md, `SKILL 應提到「${kw}」`).toContain(kw);
    }
  });
});
