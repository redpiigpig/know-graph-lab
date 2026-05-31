/**
 * POST /api/lang/memory/regenerate
 * Body: { language, usePaid? }
 * 從近期對話發言、改錯、單字、等級、作業，用 Gemini 統整出「長期記憶 + highlights」。
 * 給語言首頁顯示，並注入每次對話的 system prompt（跨 session 記憶）。
 */
import { getCoach } from "~/server/utils/lang-coaches";
import { coachGemini } from "~/server/utils/coach-ai";
import { parseJsonLoose } from "~/server/utils/gemini";

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const { language, usePaid } = (await readBody(event)) as { language: string; usePaid?: boolean };
  const coach = getCoach(language);
  if (!coach) throw createError({ statusCode: 400, message: "不支援的語言" });

  // 蒐集素材：session 摘要 + 近期改錯 + 近期單字 + 等級 + 既有記憶
  const { data: sess } = await supabase
    .from("lang_sessions")
    .select("id, summary, topic")
    .eq("user_id", user.id)
    .eq("language", language)
    .order("updated_at", { ascending: false })
    .limit(10);
  const sessionIds = (sess ?? []).map((s) => s.id);

  let corrections: any[] = [];
  if (sessionIds.length) {
    const { data: msgs } = await supabase
      .from("lang_messages")
      .select("corrections")
      .in("session_id", sessionIds)
      .eq("role", "user")
      .order("created_at", { ascending: false })
      .limit(60);
    corrections = (msgs ?? []).flatMap((m: any) => m.corrections || []).slice(0, 40);
  }

  const { data: vocab } = await supabase
    .from("lang_vocab")
    .select("word")
    .eq("user_id", user.id)
    .eq("language", language)
    .order("created_at", { ascending: false })
    .limit(40);

  const { data: prog } = await supabase
    .from("lang_progress")
    .select("level")
    .eq("user_id", user.id)
    .eq("language", language)
    .single();

  const { data: prevMem } = await supabase
    .from("lang_memory")
    .select("memory")
    .eq("user_id", user.id)
    .eq("language", language)
    .single();

  const material = [
    prevMem?.memory ? `【既有記憶】\n${prevMem.memory}` : "",
    `【目前等級】${prog?.level || "B2"}`,
    sess?.length ? `【近期主題與摘要】\n${sess.map((s: any) => `- ${s.topic || "對話"}：${s.summary || ""}`).join("\n")}` : "",
    corrections.length ? `【近期常犯錯誤】\n${corrections.map((c: any) => `「${c.original}」→「${c.fixed}」（${c.note || ""}）`).join("\n")}` : "",
    vocab?.length ? `【近期單字】${vocab.map((v: any) => v.word).join("、")}` : "",
  ].filter(Boolean).join("\n\n");

  const raw = await coachGemini(
    {
      system: `你是語言學習記憶整理員，為一位學「${coach.langLabel}」的學生統整長期學習記憶。
根據素材，只輸出 JSON：
{
  "memory": "200字內的繁體中文長期記憶：學生的程度、學習風格、聊過哪些主題、口語/寫作特徵、目標。寫成教練「對這位學生的了解」。",
  "highlights": {
    "strengths": ["優勢1","優勢2"],
    "weaknesses": ["反覆出現的弱點/文法錯誤類型1","弱點2"],
    "topics": ["聊過的主題1","主題2"],
    "next_focus": ["建議下一步加強1","加強2"]
  }
}
weaknesses 要specific（例如「冠詞 a/the 漏用」「過去完成式用錯」），不要空泛。繁體中文不可簡體。`,
      contents: [{ role: "user", parts: [{ text: material || "（素材很少，先給初步評估）" }] }],
      json: true,
      temperature: 0.4,
      maxOutputTokens: 1024,
    },
    { usePaid: usePaid === true, userId: user.id, supabase }
  );

  let parsed: any;
  try {
    parsed = parseJsonLoose(raw);
  } catch {
    parsed = { memory: raw, highlights: {} };
  }

  const { data: saved } = await supabase
    .from("lang_memory")
    .upsert(
      {
        user_id: user.id,
        language,
        memory: parsed.memory ?? "",
        highlights: parsed.highlights ?? {},
        updated_at: new Date().toISOString(),
      },
      { onConflict: "user_id,language" }
    )
    .select("memory, highlights, updated_at")
    .single();

  return { memory: saved };
});
