/**
 * POST /api/lang/smalltalk/start
 * Body: { language, topic, duration, usePaid? }
 * 建立一個限時 small-talk session（指定議題 + 分鐘），教練主動開場破題。
 * 之後用 /api/lang/chat（帶該 sessionId）繼續對話；結束後呼叫 /smalltalk/feedback。
 */
import { getCoach, OUTPUT_CONTRACT, pickPersona } from "~/server/utils/lang-coaches";
import { coachGemini } from "~/server/utils/coach-ai";
import { parseJsonLoose } from "~/server/utils/gemini";

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const { language, topic, duration, usePaid } = (await readBody(event)) as {
    language: string;
    topic: string;
    duration?: number;
    usePaid?: boolean;
  };
  const coach = getCoach(language);
  if (!coach || !coach.enabled) throw createError({ statusCode: 400, message: "不支援的語言" });
  if (!topic?.trim()) throw createError({ statusCode: 400, message: "請提供議題" });
  const dur = [3, 5, 10].includes(Number(duration)) ? Number(duration) : 5;

  // small-talk 偏向辯論/討論人格
  const { count } = await supabase
    .from("lang_sessions")
    .select("id", { count: "exact", head: true })
    .eq("user_id", user.id)
    .eq("language", language);
  const persona = pickPersona(coach, (count ?? 0) + 2); // 偏移避免每次都同一個

  const { data: sess, error } = await supabase
    .from("lang_sessions")
    .insert({
      user_id: user.id,
      language,
      title: `限時聊：${topic}`,
      mode: "smalltalk",
      topic,
      duration_target: dur,
      persona: persona?.key ?? null,
    })
    .select("id")
    .single();
  if (error || !sess) throw createError({ statusCode: 500, message: "建立失敗" });

  // 教練開場破題
  const raw = await coachGemini(
    {
      system: `${coach.systemPrompt}\n\n${persona ? `【人格】${persona.label}：${persona.instruction}\n\n` : ""}這是一場限時 ${dur} 分鐘、針對議題「${topic}」的 small-talk 練習。請用${coach.langLabel}主動開場：拋出你的觀點或一個尖銳的開放問題，引學生開口。${OUTPUT_CONTRACT}`,
      contents: [{ role: "user", parts: [{ text: `開始這場關於「${topic}」的限時討論。` }] }],
      json: true,
      temperature: 0.85,
      maxOutputTokens: 1024,
    },
    { usePaid: usePaid === true, userId: user.id, supabase }
  );

  let opening: any = { reply: "", translation: "" };
  try { opening = parseJsonLoose(raw); } catch { opening = { reply: raw, translation: "" }; }

  // 存教練開場訊息
  await supabase.from("lang_messages").insert({
    session_id: sess.id,
    user_id: user.id,
    role: "coach",
    content: opening.reply ?? "",
    translation: opening.translation ?? null,
  });
  await supabase.from("lang_sessions").update({ message_count: 1 }).eq("id", sess.id);

  return {
    sessionId: sess.id,
    topic,
    duration: dur,
    persona: persona ? { key: persona.key, label: persona.label, emoji: persona.emoji } : null,
    opening: { reply: opening.reply ?? "", translation: opening.translation ?? "" },
  };
});
