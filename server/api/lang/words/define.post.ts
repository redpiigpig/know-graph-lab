/**
 * POST /api/lang/words/define
 * Body: { language, word, sentence?, usePaid? }
 * 點字即查：在「該句脈絡」下給這個詞的繁中釋義 + 原形 + 簡短例句（走 NVIDIA 主→Gemini）。
 */
import { getCoach } from "~/server/utils/lang-coaches";
import { coachGemini } from "~/server/utils/coach-ai";
import { parseJsonLoose } from "~/server/utils/gemini";

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const { language, word, sentence, usePaid } = (await readBody(event)) as {
    language: string;
    word: string;
    sentence?: string;
    usePaid?: boolean;
  };
  const coach = getCoach(language);
  if (!coach) throw createError({ statusCode: 400, message: "不支援的語言" });
  if (!word?.trim()) throw createError({ statusCode: 400, message: "缺少 word" });

  const raw = await coachGemini(
    {
      system: `你是${coach.langLabel}讀本助教。使用者在閱讀時點了一個詞，請在「該句脈絡」下解釋它。
只輸出 JSON：{ "lemma": "原形/字典形（${coach.langLabel}）", "reading": "音標/假名/羅馬拼音（無則空字串）", "meaning": "繁體中文釋義（在此句脈絡下，簡短）", "pos": "詞性", "example": "一句簡短${coach.langLabel}例句" }
繁體中文不可簡體。`,
      contents: [{ role: "user", parts: [{ text: `詞：「${word}」\n句子：${sentence || "（無上下文）"}` }] }],
      json: true,
      temperature: 0.3,
      maxOutputTokens: 400,
    },
    { usePaid: usePaid === true, userId: user.id, supabase }
  );

  let d: any;
  try {
    d = parseJsonLoose(raw);
  } catch {
    d = { lemma: word, reading: "", meaning: raw.slice(0, 80), pos: "", example: "" };
  }
  return {
    lemma: d.lemma || word,
    reading: d.reading || "",
    meaning: d.meaning || "",
    pos: d.pos || "",
    example: d.example || "",
  };
});
