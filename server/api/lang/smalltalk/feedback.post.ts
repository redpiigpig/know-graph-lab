/**
 * POST /api/lang/smalltalk/feedback
 * Body: { sessionId, usePaid? }
 * 限時討論結束 → Gemini 依學生發言評分（流暢/文法/詞彙/論述）+ 強項/改進/總評。存進 session.feedback。
 */
import { getCoach } from "~/server/utils/lang-coaches";
import { coachGemini } from "~/server/utils/coach-ai";
import { parseJsonLoose } from "~/server/utils/gemini";

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const { sessionId, usePaid } = (await readBody(event)) as { sessionId: string; usePaid?: boolean };
  if (!sessionId) throw createError({ statusCode: 400, message: "缺少 sessionId" });

  const { data: sess } = await supabase
    .from("lang_sessions")
    .select("id, user_id, language, topic")
    .eq("id", sessionId)
    .single();
  if (!sess || sess.user_id !== user.id) throw createError({ statusCode: 404, message: "找不到對話" });
  const coach = getCoach(sess.language);

  const { data: msgs } = await supabase
    .from("lang_messages")
    .select("role, content")
    .eq("session_id", sessionId)
    .eq("role", "user")
    .order("created_at", { ascending: true });
  const studentTurns = (msgs ?? []).map((m: any) => m.content);
  if (studentTurns.length < 1) throw createError({ statusCode: 400, message: "還沒開口，先聊幾句再看反饋" });

  const raw = await coachGemini(
    {
      system: `你是${coach?.langLabel}口語評分官。學生剛完成一場關於「${sess.topic}」的限時討論。
依學生的發言評分，只輸出 JSON：
{
  "scores": { "fluency": 0-100, "grammar": 0-100, "vocabulary": 0-100, "topic_development": 0-100 },
  "overall": 0-100,
  "strengths": ["這場表現的強項1","強項2"],
  "improvements": ["可改進1（具體，舉學生原句）","可改進2"],
  "comment": "繁體中文總評（鼓勵 + 一個最該優先改的點）"
}
繁體中文不可簡體。`,
      contents: [{ role: "user", parts: [{ text: `【議題】${sess.topic}\n\n【學生發言】\n${studentTurns.map((t, i) => `${i + 1}. ${t}`).join("\n")}` }] }],
      json: true,
      temperature: 0.3,
      maxOutputTokens: 1024,
    },
    { usePaid: usePaid === true, userId: user.id, supabase }
  );

  let fb: any;
  try { fb = parseJsonLoose(raw); } catch { fb = { comment: raw, scores: {} }; }

  await supabase.from("lang_sessions").update({ feedback: fb }).eq("id", sessionId);
  return { feedback: fb };
});
