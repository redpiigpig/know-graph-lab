/**
 * POST /api/lang/chat
 * Body: { language: string, sessionId?: string, message: string }
 * 教練對話迴圈：Gemini 2.5 Flash + 滑動窗口 + 結構化輸出
 * 回傳 { sessionId, reply, translation, corrections[], new_vocab[], homework? }
 * 並自動持久化訊息、寫入新單字、建立作業。
 */
import { getCoach, OUTPUT_CONTRACT } from "~/server/utils/lang-coaches";
import { callGemini, parseJsonLoose } from "~/server/utils/gemini";

const WINDOW = 12; // 保留最近 12 則進 context（更早的壓進 session.summary）

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const { language, sessionId, message } = (await readBody(event)) as {
    language: string;
    sessionId?: string;
    message: string;
  };

  if (!message?.trim()) throw createError({ statusCode: 400, message: "訊息不可為空" });
  const coach = getCoach(language);
  if (!coach || !coach.enabled) throw createError({ statusCode: 400, message: "不支援的語言" });

  // 1. 取得或建立 session
  let sid = sessionId;
  let summary = "";
  if (sid) {
    const { data: s } = await supabase
      .from("lang_sessions")
      .select("id, summary, user_id")
      .eq("id", sid)
      .single();
    if (!s || s.user_id !== user.id) throw createError({ statusCode: 404, message: "找不到對話" });
    summary = s.summary ?? "";
  } else {
    const { data: s, error } = await supabase
      .from("lang_sessions")
      .insert({ user_id: user.id, language, title: null })
      .select("id")
      .single();
    if (error || !s) throw createError({ statusCode: 500, message: "建立對話失敗" });
    sid = s.id;
  }

  // 2. 載入最近窗口的歷史
  const { data: history } = await supabase
    .from("lang_messages")
    .select("role, content")
    .eq("session_id", sid)
    .order("created_at", { ascending: false })
    .limit(WINDOW);
  const recent = (history ?? []).reverse();

  // 3. 組 Gemini contents
  const contents = recent.map((m: any) => ({
    role: (m.role === "coach" ? "model" : "user") as "user" | "model",
    parts: [{ text: m.content }],
  }));
  contents.push({ role: "user" as const, parts: [{ text: message }] });

  const system = `${coach.systemPrompt}\n\n${
    summary ? `【先前對話摘要（長期記憶）】\n${summary}\n\n` : ""
  }${OUTPUT_CONTRACT}`;

  // 4. 呼叫 Gemini
  const raw = await callGemini({
    model: "gemini-2.5-flash",
    system,
    contents,
    json: true,
    temperature: 0.85,
    maxOutputTokens: 2048,
  });

  let parsed: {
    reply: string;
    translation?: string;
    corrections?: any[];
    new_vocab?: any[];
    homework?: { topic: string; prompt: string; hw_type?: string } | null;
  };
  try {
    parsed = parseJsonLoose(raw);
  } catch {
    parsed = { reply: raw, translation: "", corrections: [], new_vocab: [], homework: null };
  }
  const corrections = Array.isArray(parsed.corrections) ? parsed.corrections : [];
  const newVocab = Array.isArray(parsed.new_vocab) ? parsed.new_vocab : [];

  // 5. 持久化：使用者訊息 + 教練訊息
  await supabase.from("lang_messages").insert([
    { session_id: sid, user_id: user.id, role: "user", content: message, corrections },
    {
      session_id: sid,
      user_id: user.id,
      role: "coach",
      content: parsed.reply ?? "",
      translation: parsed.translation ?? null,
      corrections: [],
    },
  ]);

  // 6. 寫入新單字（去重靠 unique 約束，用 upsert ignore）
  if (newVocab.length) {
    const rows = newVocab
      .filter((v) => v?.word)
      .map((v) => ({
        user_id: user.id,
        language,
        word: String(v.word).trim(),
        reading: v.reading ?? null,
        meaning: v.meaning ?? "",
        example: v.example ?? null,
        part_of_speech: v.part_of_speech ?? null,
        source: "chat",
      }));
    if (rows.length) {
      await supabase
        .from("lang_vocab")
        .upsert(rows, { onConflict: "user_id,language,word", ignoreDuplicates: true });
    }
  }

  // 7. 作業
  let homeworkRow = null;
  if (parsed.homework?.prompt) {
    const { data: hw } = await supabase
      .from("lang_homework")
      .insert({
        user_id: user.id,
        language,
        topic: parsed.homework.topic ?? "練習",
        prompt: parsed.homework.prompt,
        hw_type: parsed.homework.hw_type ?? "writing",
        status: "assigned",
      })
      .select("*")
      .single();
    homeworkRow = hw;
  }

  // 8. 更新 session 計數/時間 + 進度
  const { count } = await supabase
    .from("lang_messages")
    .select("id", { count: "exact", head: true })
    .eq("session_id", sid);
  await supabase
    .from("lang_sessions")
    .update({ message_count: count ?? 0, updated_at: new Date().toISOString() })
    .eq("id", sid);

  const today = new Date().toISOString().slice(0, 10);
  await supabase
    .from("lang_progress")
    .upsert(
      { user_id: user.id, language, last_active: today, updated_at: new Date().toISOString() },
      { onConflict: "user_id,language", ignoreDuplicates: false }
    );

  // 9. 背景壓縮摘要（每累積一定量就更新長期記憶；失敗不影響回覆）
  if ((count ?? 0) >= WINDOW + 8 && (count ?? 0) % 8 === 0) {
    summarizeSession(supabase, sid!, summary, coach.name).catch(() => {});
  }

  return {
    sessionId: sid,
    reply: parsed.reply ?? "",
    translation: parsed.translation ?? "",
    corrections,
    new_vocab: newVocab,
    homework: homeworkRow,
  };
});

// 將窗口外的舊訊息壓縮進 session.summary（滾動式長期記憶，控制 token）
async function summarizeSession(supabase: any, sid: string, prevSummary: string, coachName: string) {
  const { data: older } = await supabase
    .from("lang_messages")
    .select("role, content")
    .eq("session_id", sid)
    .order("created_at", { ascending: true });
  if (!older?.length) return;
  const trimmed = older.slice(0, Math.max(0, older.length - WINDOW));
  if (!trimmed.length) return;

  const transcript = trimmed
    .map((m: any) => `${m.role === "coach" ? coachName : "學生"}：${m.content}`)
    .join("\n");
  const text = await callGemini({
    model: "gemini-2.5-flash",
    system:
      "你是學習記憶整理員。把以下語言課對話壓縮成 150 字內的繁體中文重點摘要，記錄：聊過的主題、學生的程度與常犯錯誤、已學的關鍵單字。只輸出摘要文字。",
    contents: [{ role: "user", parts: [{ text: `${prevSummary ? `【既有摘要】${prevSummary}\n\n` : ""}【新對話】\n${transcript}` }] }],
    temperature: 0.3,
    maxOutputTokens: 512,
  });
  await supabase.from("lang_sessions").update({ summary: text.trim() }).eq("id", sid);
}
