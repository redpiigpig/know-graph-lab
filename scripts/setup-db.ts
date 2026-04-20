/**
 * 自動在 Supabase 建立書摘管理系統所需的資料表
 *
 * 使用方式（兩種選一）：
 *
 * 方法一：Personal Access Token（推薦）
 *   1. 前往 https://supabase.com/dashboard/account/tokens
 *   2. 點 "Generate new token"，複製 token
 *   3. 執行：npx ts-node scripts/setup-db.ts <your-access-token>
 *
 * 方法二：直接在 Supabase SQL Editor 貼上 database/schema.sql 內容執行
 */

import * as dotenv from "dotenv";
dotenv.config();

const SUPABASE_URL = process.env.SUPABASE_URL!;
const PROJECT_REF = SUPABASE_URL.replace("https://", "").split(".")[0];
const ACCESS_TOKEN = process.argv[2];

if (!ACCESS_TOKEN) {
  console.error("❌ 請提供 Access Token，例如：npx ts-node scripts/setup-db.ts eyJ...");
  console.error("   前往 https://supabase.com/dashboard/account/tokens 取得");
  process.exit(1);
}

const SQL_STATEMENTS = [
  `create table if not exists books (
    id uuid primary key default gen_random_uuid(),
    title text not null,
    author text not null,
    translator text,
    publish_place text,
    publisher text,
    publish_year int,
    edition text,
    created_at timestamptz default now()
  )`,
  `create table if not exists projects (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    type text not null check (type in ('待寫著作', '待寫文章', '書摘')),
    description text,
    created_at timestamptz default now()
  )`,
  `create table if not exists excerpts (
    id uuid primary key default gen_random_uuid(),
    title text,
    content text not null,
    book_id uuid references books(id) on delete set null,
    chapter text,
    page_number text,
    created_at timestamptz default now(),
    updated_at timestamptz default now()
  )`,
  `create table if not exists excerpt_projects (
    excerpt_id uuid references excerpts(id) on delete cascade,
    project_id uuid references projects(id) on delete cascade,
    primary key (excerpt_id, project_id)
  )`,
  `create index if not exists excerpts_content_idx on excerpts using gin(to_tsvector('simple', coalesce(content, '')))`,
  `create index if not exists excerpts_title_idx on excerpts using gin(to_tsvector('simple', coalesce(title, '')))`,
  `insert into projects (name, type, description) values
    ('書摘收藏', '書摘', '純粹收集書中值得記錄的段落'),
    ('待寫文章素材', '待寫文章', '未來寫文章時可以引用的摘文'),
    ('待寫著作素材', '待寫著作', '未來寫書時可以引用的摘文')
  on conflict do nothing`,
];

async function runSQL(sql: string): Promise<void> {
  const res = await fetch(
    `https://api.supabase.com/v1/projects/${PROJECT_REF}/database/query`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${ACCESS_TOKEN}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query: sql }),
    }
  );

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`HTTP ${res.status}: ${body}`);
  }
}

async function main() {
  console.log(`🔗 連線到專案：${PROJECT_REF}`);

  for (let i = 0; i < SQL_STATEMENTS.length; i++) {
    const preview = SQL_STATEMENTS[i].trim().split("\n")[0].substring(0, 60);
    process.stdout.write(`  [${i + 1}/${SQL_STATEMENTS.length}] ${preview}... `);
    try {
      await runSQL(SQL_STATEMENTS[i]);
      console.log("✅");
    } catch (err: any) {
      console.log("❌");
      console.error("    錯誤:", err.message);
    }
  }

  console.log("\n✨ 完成！");
}

main().catch(console.error);
