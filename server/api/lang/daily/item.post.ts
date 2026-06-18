/**
 * POST /api/lang/daily/item
 * Body: { language, kind: 'reading'|'listening'|'speaking', id, usePaid? }
 * 生成某個今日項目的內容（懶生成，存回 plan）。閱讀/聽力含短文/聽稿 + 選擇題 + 討論 session。
 */
import { getCoach } from "~/server/utils/lang-coaches";
import { coachGemini } from "~/server/utils/coach-ai";
import { parseJsonLoose } from "~/server/utils/gemini";
import { CURATED_PASSAGE_LANGS, passageById } from "~/server/data/coachPassages";

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const { language, kind, id, usePaid } = (await readBody(event)) as {
    language: string;
    kind: "reading" | "listening" | "speaking";
    id: string;
    usePaid?: boolean;
  };
  const coach = getCoach(language);
  if (!coach) throw createError({ statusCode: 400, message: "不支援的語言" });
  const today = tzToday();

  const { data: row } = await supabase
    .from("lang_daily")
    .select("plan")
    .eq("user_id", user.id)
    .eq("language", language)
    .eq("plan_date", today)
    .single();
  if (!row?.plan) throw createError({ statusCode: 404, message: "今日計畫不存在" });
  const plan = row.plan;
  const list = plan[kind] as any[];
  const idx = (list || []).findIndex((x) => x.id === id);
  if (idx < 0) throw createError({ statusCode: 404, message: "找不到項目" });
  const item = list[idx];
  if (item.content) return { item };

  const { data: prog } = await supabase
    .from("lang_progress").select("level").eq("user_id", user.id).eq("language", language).single();
  const lv = prog?.level || coach.defaultLevel || coach.levelScale[0];

  let content: any = {};
  if (kind === "speaking") {
    content = { prompt: item.prompt };
  } else {
    const isReading = kind === "reading";
    // 古典語：item 帶 bankId → 直接取策展經文短文，零 AI
    const bankP = item.bankId && CURATED_PASSAGE_LANGS.has(language) ? passageById(language, item.bankId) : null;
    if (bankP) {
      content = isReading
        ? { title: bankP.title, passage: bankP.text, questions: bankP.questions, summary: bankP.summary }
        : { title: bankP.title, audio_text: bankP.text, questions: bankP.questions, summary: bankP.summary };
    } else {
      const raw = await coachGemini(
        {
          system: `你是${coach.langLabel}出題老師，為「${lv}」程度、做宗教研究的學生產一則${isReading ? "閱讀短文" : "聽力段落"}。主題：「${item.topic}」。
只輸出 JSON：{
  "title": "標題（${coach.langLabel}）",
  "${isReading ? "passage" : "audio_text"}": "${isReading ? "閱讀短文" : "聽力稿（將由系統朗讀，學生看不到）"}（${coach.langLabel}，貼合 ${lv} 程度，200–300 字）",
  "questions": [ { "q": "理解題（${coach.langLabel}）", "options": ["A. ...","B. ...","C. ...","D. ..."], "answer": "A" } ],
  "summary": "繁中一句摘要"
}
questions 出 4 題單選。繁體中文不可簡體。`,
          contents: [{ role: "user", parts: [{ text: item.topic }] }],
          json: true,
          temperature: 0.6,
          maxOutputTokens: 2048,
        },
        { usePaid: usePaid === true, userId: user.id, supabase }
      );
      try { content = parseJsonLoose(raw); } catch { throw createError({ statusCode: 502, message: "生成失敗，請重試" }); }
    }
  }

  // 建立討論 session（讀完/聽完/口說都可延伸討論）
  const seedText =
    kind === "speaking"
      ? `學生要練口說題：「${item.prompt}」。請你扮演對話者，先用${coach.langLabel}回應或追問，引導學生開口，並即時溫和糾錯。`
      : `學生剛${kind === "reading" ? "讀完一篇文章" : "聽完一段"}：「${content.title || item.topic}」。摘要：${content.summary || ""}。接下來請以這個內容為基礎，用${coach.langLabel}跟學生討論、追問、辯論，並即時糾錯。`;
  const { data: sess } = await supabase
    .from("lang_sessions")
    .insert({ user_id: user.id, language, title: `今日${kind === "reading" ? "閱讀" : kind === "listening" ? "聽力" : "口說"}：${content.title || item.topic || item.prompt}`, mode: "smalltalk", topic: item.topic || item.prompt, summary: seedText })
    .select("id")
    .single();

  list[idx] = { ...item, content, session_id: sess?.id ?? null };
  plan[kind] = list;
  await supabase
    .from("lang_daily")
    .update({ plan })
    .eq("user_id", user.id)
    .eq("language", language)
    .eq("plan_date", today);

  return { item: list[idx] };
});
