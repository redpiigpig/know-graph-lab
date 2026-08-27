import { readFile } from "node:fs/promises";
import { resolve } from "node:path";

// 逐詞詞形分析：希臘走 MorphGNT 標註的 SBLGNT，希伯來走 OSHB／morphhb 標註的
// WLC，兩邊都由 scripts/build_scripture_morphology.py 先分卷存好。一卷一檔是
// 刻意的：整本希伯來聖經的分析有 64 MB，一章的頁面沒有理由載那麼多。
//
// 中文詞義只給本專案自己覆核過的那一份（希臘 2,000 詞、希伯來 1,000 詞，
// 覆蓋到經文詞次的 87% 與 78%）。查不到就留白——詞形分析照樣顯示，意思空著
// 看得出來是空的，不拿別處的字典冒充。

interface MorphWord {
  text: string;
  lemma: string;
  strong?: string;
  pos: string;
  parsing: string;
  code: string;
  zh?: string;
  en?: string;
}

const cache = new Map<string, Record<string, MorphWord[]>>();

async function load(book: string): Promise<Record<string, MorphWord[]> | null> {
  if (cache.has(book)) return cache.get(book)!;
  // 卷名只允許字母與數字，路徑不接受任何來自查詢字串的目錄符號。
  if (!/^[0-9A-Za-z]{1,12}$/.test(book)) return null;
  const path = resolve(
    process.cwd(),
    "output/source-cache/scripture/morphology/books",
    `${book}.json`,
  );
  try {
    const parsed = JSON.parse(await readFile(path, "utf-8"));
    cache.set(book, parsed.byVerse || {});
    return cache.get(book)!;
  } catch {
    return null;
  }
}

export default defineEventHandler(async (event) => {
  // 同一章的經文本體走 chapter.get.ts，那支要求登入；逐詞層更要——信望愛的
  // 中文字典是「私人使用」授權，開著讓任何人取用就超出授權範圍了。
  setHeader(event, "X-Robots-Tag", "noindex, nofollow, noarchive");
  await requireAuth(event);

  const query = getQuery(event);
  const book = String(query.book || "");
  const chapter = Number(query.chapter || 0);
  if (!book || !chapter) {
    throw createError({ statusCode: 400, statusMessage: "book 與 chapter 為必填" });
  }

  const byVerse = await load(book);
  if (!byVerse) return { book, chapter, available: false, verses: {} };

  const verses: Record<number, MorphWord[]> = {};
  for (const [ref, words] of Object.entries(byVerse)) {
    const parts = ref.split(".");
    if (Number(parts[parts.length - 2]) !== chapter) continue;
    verses[Number(parts[parts.length - 1])] = words;
  }

  setHeader(event, "Cache-Control", "public, max-age=86400");
  return { book, chapter, available: Object.keys(verses).length > 0, verses };
});
