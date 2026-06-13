/**
 * GET /api/lang/compose?language=en&n=10
 * 「受限寫作題型」之一：句子重組（零 AI、確定性批改）。
 * 回傳若干題，每題給「提示 + 正確詞序」；頁面打散成詞卡讓使用者排回，比對詞序對錯。
 * 來源：en＝策展情境句 enSentences（中譯當提示）；grc/hbo＝詞形題庫的新約/舊約經文
 *（以原文詞序為答案，重組＝重建該節經文，適合熟讀原典）。其他語言暫無句源。
 */
import { scenariosForClient } from "~/server/data/enSentences";
import greek from "~/server/data/parseGreek.json";
import hebrew from "~/server/data/parseHebrew.json";

function sample<T>(arr: T[], n: number): T[] {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a.slice(0, n);
}

export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const q = getQuery(event);
  const language = (q.language as string) || "";
  const n = Math.min(Math.max(Number(q.n) || 10, 4), 30);

  if (language === "en") {
    const pool: any[] = [];
    for (const sc of scenariosForClient() as any[]) {
      for (const it of sc.items) {
        const words = String(it.en).trim().split(/\s+/);
        if (words.length >= 4 && words.length <= 12) pool.push({ prompt: it.zh, hint: it.situation, words });
      }
    }
    return { language, available: true, rtl: false, total: pool.length, items: sample(pool, n) };
  }

  if (language === "grc" || language === "hbo") {
    const bank: any = language === "grc" ? greek : hebrew;
    const seen = new Set<string>();
    const verses: any[] = [];
    for (const it of bank.items) {
      const w: string[] = it.verse_words;
      if (!w || w.length < 4 || w.length > 9) continue;
      const key = it.ref + "|" + w.join(" ");
      if (seen.has(key)) continue;
      seen.add(key);
      verses.push({ prompt: it.ref, hint: "重建這節經文的原文詞序", words: w });
    }
    return { language, available: true, rtl: language === "hbo", total: verses.length, items: sample(verses, n) };
  }

  return { language, available: false, rtl: false, total: 0, items: [] };
});
