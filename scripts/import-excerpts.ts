/**
 * 書摘 CSV → Supabase 匯入腳本
 *
 * 使用方式：
 *   1. 把 Excel 另存為 CSV（UTF-8 格式，每個 sheet 存一個 CSV）
 *   2. 修改下方 CONFIG 區塊，對應你的 CSV 欄位名稱
 *   3. 執行：npx ts-node scripts/import-excerpts.ts <your-file.csv>
 *
 * 注意：執行前確保 .env 中的 SUPABASE_URL 和 SUPABASE_SERVICE_ROLE_KEY 正確
 */

import fs from "fs";
import path from "path";
import { createClient } from "@supabase/supabase-js";
import * as dotenv from "dotenv";

dotenv.config();

// ============================================================
// CONFIG：修改這裡對應你的 CSV 欄位名稱
// ============================================================
const COLUMN_MAP = {
  title: "標題",           // 摘文標題欄位名
  content: "內文",         // 摘文內文欄位名（必填）
  author: "作者",          // 作者欄位名
  bookTitle: "書名",       // 書名欄位名
  chapter: "章節",         // 章節欄位名
  pageNumber: "頁數",      // 頁數欄位名
  projectType: "專案類型", // 選填：'待寫著作' | '待寫文章' | '書摘'
  translator: "譯者",      // 選填
  publishPlace: "出版地",  // 選填，例如「臺北」
  publisher: "出版社",     // 選填，例如「聯經」
  publishYear: "出版年份", // 選填，例如「2021」
  edition: "版次",         // 選填，例如「第二版」
};

// 若 CSV 沒有專案類型欄位，這裡設定預設類型
const DEFAULT_PROJECT_TYPE: "書摘" | "待寫著作" | "待寫文章" = "書摘";
// ============================================================

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!,
  { auth: { autoRefreshToken: false, persistSession: false } }
);

// 簡易 CSV 解析（支援雙引號包住的欄位，內含逗號或換行）
function parseCSV(raw: string): Record<string, string>[] {
  const lines: string[] = [];
  let current = "";
  let inQuotes = false;

  for (let i = 0; i < raw.length; i++) {
    const ch = raw[i];
    if (ch === '"') {
      if (inQuotes && raw[i + 1] === '"') {
        current += '"';
        i++;
      } else {
        inQuotes = !inQuotes;
      }
    } else if (ch === "\n" && !inQuotes) {
      lines.push(current.replace(/\r$/, ""));
      current = "";
    } else {
      current += ch;
    }
  }
  if (current.trim()) lines.push(current);

  if (lines.length < 2) return [];

  const headers = lines[0].split(",").map((h) => h.trim().replace(/^"|"$/g, ""));
  return lines.slice(1).map((line) => {
    const values: string[] = [];
    let val = "";
    let inQ = false;
    for (let i = 0; i < line.length; i++) {
      const ch = line[i];
      if (ch === '"') {
        if (inQ && line[i + 1] === '"') { val += '"'; i++; }
        else inQ = !inQ;
      } else if (ch === "," && !inQ) {
        values.push(val.trim());
        val = "";
      } else {
        val += ch;
      }
    }
    values.push(val.trim());
    return Object.fromEntries(headers.map((h, i) => [h, values[i] ?? ""]));
  });
}

async function getOrCreateBook(
  title: string,
  author: string,
  extra?: {
    translator?: string;
    publishPlace?: string;
    publisher?: string;
    publishYear?: string;
    edition?: string;
  }
): Promise<string | null> {
  if (!title) return null;
  const { data: existing } = await supabase
    .from("books")
    .select("id")
    .eq("title", title)
    .single();

  if (existing) return existing.id;

  const year = extra?.publishYear ? parseInt(extra.publishYear) : null;

  const { data: created, error } = await supabase
    .from("books")
    .insert({
      title,
      author: author || "不詳",
      translator: extra?.translator || null,
      publish_place: extra?.publishPlace || null,
      publisher: extra?.publisher || null,
      publish_year: isNaN(year!) ? null : year,
      edition: extra?.edition || null,
    })
    .select("id")
    .single();

  if (error) { console.error("建立書籍失敗:", error.message); return null; }
  return created.id;
}

async function getOrCreateProject(type: string): Promise<string | null> {
  const validType = ["待寫著作", "待寫文章", "書摘"].includes(type)
    ? type
    : DEFAULT_PROJECT_TYPE;

  const { data: existing } = await supabase
    .from("book_projects")
    .select("id")
    .eq("type", validType)
    .limit(1)
    .single();

  if (existing) return existing.id;

  const { data: created, error } = await supabase
    .from("book_projects")
    .insert({ name: `${validType}素材`, type: validType })
    .select("id")
    .single();

  if (error) { console.error("建立分類失敗:", error.message); return null; }
  return created.id;
}

async function main() {
  const csvPath = process.argv[2];
  if (!csvPath) {
    console.error("請指定 CSV 檔案路徑，例如：npx ts-node scripts/import-excerpts.ts data.csv");
    process.exit(1);
  }

  const raw = fs.readFileSync(path.resolve(csvPath), "utf-8");
  const rows = parseCSV(raw);
  console.log(`讀取到 ${rows.length} 筆資料`);

  let success = 0;
  let failed = 0;

  for (const row of rows) {
    const content = row[COLUMN_MAP.content]?.trim();
    if (!content) { failed++; continue; }

    const bookId = await getOrCreateBook(
      row[COLUMN_MAP.bookTitle]?.trim(),
      row[COLUMN_MAP.author]?.trim(),
      {
        translator: row[COLUMN_MAP.translator]?.trim(),
        publishPlace: row[COLUMN_MAP.publishPlace]?.trim(),
        publisher: row[COLUMN_MAP.publisher]?.trim(),
        publishYear: row[COLUMN_MAP.publishYear]?.trim(),
        edition: row[COLUMN_MAP.edition]?.trim(),
      }
    );

    const { data: excerpt, error: excerptError } = await supabase
      .from("excerpts")
      .insert({
        title: row[COLUMN_MAP.title]?.trim() || null,
        content,
        book_id: bookId,
        chapter: row[COLUMN_MAP.chapter]?.trim() || null,
        page_number: row[COLUMN_MAP.pageNumber]?.trim() || null,
      })
      .select("id")
      .single();

    if (excerptError) {
      console.error("新增摘文失敗:", excerptError.message, row);
      failed++;
      continue;
    }

    const projectType = COLUMN_MAP.projectType
      ? row[COLUMN_MAP.projectType]?.trim()
      : DEFAULT_PROJECT_TYPE;
    const projectId = await getOrCreateProject(projectType);

    if (projectId) {
      await supabase.from("excerpt_book_projects").insert({
        excerpt_id: excerpt.id,
        book_project_id: projectId,
      });
    }

    success++;
    if (success % 10 === 0) console.log(`已匯入 ${success} 筆...`);
  }

  console.log(`\n完成！成功: ${success} 筆，失敗: ${failed} 筆`);
}

main().catch(console.error);
