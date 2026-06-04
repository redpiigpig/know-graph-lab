/**
 * POST /api/lang/vocab/generate
 * Body: { language, theme, count?, level? }
 * 用 Gemini 生成一組學術單字（AWL/GRE/人文主題），含繁中釋義/音標/例句，寫入使用者單字庫（SRS 起始）。
 */
import { getCoach } from "~/server/utils/lang-coaches";
import { parseJsonLoose } from "~/server/utils/gemini";
import { coachGemini } from "~/server/utils/coach-ai";

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const { language, theme, count, level, usePaid } = (await readBody(event)) as {
    language: string;
    theme: string;
    count?: number;
    level?: string;
    usePaid?: boolean;
  };
  const coach = getCoach(language);
  if (!coach) throw createError({ statusCode: 400, message: "不支援的語言" });
  if (!theme?.trim()) throw createError({ statusCode: 400, message: "請提供主題" });
  const n = Math.min(30, Math.max(5, count || 15));

  // 帶入使用者「目前程度」（不是目標）與興趣 → 難度貼合現況、逐步提升
  const [{ data: profile }, { data: prog }] = await Promise.all([
    supabase.from("lang_profile").select("interests").eq("user_id", user.id).single(),
    supabase.from("lang_progress").select("level").eq("user_id", user.id).eq("language", language).single(),
  ]);
  const lv = level || prog?.level || coach.defaultLevel || "A1";

  const beginner = ["A1", "A2", "N5", "N4", "入門", "初級"].includes(lv);
  const raw = await coachGemini({
    system: `你是${coach.langLabel}詞彙老師，為「${lv}」程度的學生挑選單字（學生做宗教研究）。
只輸出 JSON：{ "words": [ { "word": "", "reading": "音標/假名（無則空字串）", "meaning": "繁體中文釋義", "example": "${coach.langLabel}例句", "part_of_speech": "詞性" } ] }
要求：挑 ${n} 個符合主題的字。${beginner ? `這是初學者，請給基礎、高頻、日常／入門的常用字，不要太難。` : `學生已達 ${lv} 程度，請挑**符合或略高於 ${lv}** 的詞彙：以學術、抽象、進階搭配詞、低頻精準用字為主。**嚴格排除低於 ${lv} 的基礎／日常常見字**（如英文 B2 就不要出 heartbeat、happy、city 這類 A1–B1 早已熟悉的字，複習它們是浪費時間）。寧可難一點、冷僻一點，也不要太簡單。`}繁體中文，不可簡體。`,
    contents: [{ role: "user", parts: [{ text: `主題：${theme}` }] }],
    json: true,
    temperature: 0.6,
    maxOutputTokens: 3072,
  }, { usePaid: usePaid === true, userId: user.id, supabase });

  let words: any[] = [];
  try {
    words = parseJsonLoose<{ words: any[] }>(raw).words || [];
  } catch {
    throw createError({ statusCode: 502, message: "生成解析失敗，請重試" });
  }

  const listKey = theme.trim().slice(0, 40);
  const rows = words
    .filter((w) => w?.word)
    .map((w) => ({
      user_id: user.id,
      language,
      word: String(w.word).trim(),
      reading: w.reading ?? null,
      meaning: w.meaning ?? "",
      example: w.example ?? null,
      part_of_speech: w.part_of_speech ?? null,
      source: "list",
      list_key: listKey,
    }));
  if (!rows.length) throw createError({ statusCode: 502, message: "未生成任何單字" });

  await supabase.from("lang_vocab").upsert(rows, { onConflict: "user_id,language,word", ignoreDuplicates: true });

  return { added: rows.length, theme: listKey, words: rows.map((r) => ({ word: r.word, meaning: r.meaning })) };
});
