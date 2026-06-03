/**
 * POST /api/lang/chat
 * Body: { language: string, sessionId?: string, message: string }
 * 教練對話迴圈：Gemini 2.5 Flash + 滑動窗口 + 結構化輸出
 * 回傳 { sessionId, reply, translation, corrections[], new_vocab[], homework? }
 * 並自動持久化訊息、寫入新單字、建立作業。
 */
import { getCoach, OUTPUT_CONTRACT, pickPersona } from "~/server/utils/lang-coaches";
import { parseJsonLoose } from "~/server/utils/gemini";
import { coachGemini } from "~/server/utils/coach-ai";

const WINDOW = 12; // 保留最近 12 則進 context（更早的壓進 session.summary）

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const { language, sessionId, message, usePaid, mode: reqMode } = (await readBody(event)) as {
    language: string;
    sessionId?: string;
    message: string;
    usePaid?: boolean;
    mode?: string; // free / qa / scenario（新對話用）
  };

  if (!message?.trim()) throw createError({ statusCode: 400, message: "訊息不可為空" });
  const coach = getCoach(language);
  if (!coach || !coach.enabled) throw createError({ statusCode: 400, message: "不支援的語言" });

  // 1. 取得或建立 session（含人格 + 模式）
  let sid = sessionId;
  let summary = "";
  let personaKey: string | null = null;
  let chatMode = ["free", "qa", "scenario"].includes(reqMode || "") ? reqMode! : "free";
  if (sid) {
    const { data: s } = await supabase
      .from("lang_sessions")
      .select("id, summary, user_id, persona, mode")
      .eq("id", sid)
      .single();
    if (!s || s.user_id !== user.id) throw createError({ statusCode: 404, message: "找不到對話" });
    summary = s.summary ?? "";
    personaKey = s.persona ?? null;
    if (s.mode) chatMode = s.mode;
  } else {
    // 新對話：依既有 session 數輪替挑一個人格（自動切換）
    const { count } = await supabase
      .from("lang_sessions")
      .select("id", { count: "exact", head: true })
      .eq("user_id", user.id)
      .eq("language", language);
    const persona = pickPersona(coach, count ?? 0);
    personaKey = persona?.key ?? null;
    const { data: s, error } = await supabase
      .from("lang_sessions")
      .insert({ user_id: user.id, language, title: null, persona: personaKey, mode: chatMode })
      .select("id")
      .single();
    if (error || !s) throw createError({ statusCode: 500, message: "建立對話失敗" });
    sid = s.id;
  }

  // 統整記憶庫（跨 session 的長期了解）
  const { data: memRow } = await supabase
    .from("lang_memory")
    .select("memory")
    .eq("user_id", user.id)
    .eq("language", language)
    .single();
  const persona = coach.personas?.find((p) => p.key === personaKey) ?? null;

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

  const modeInstr =
    chatMode === "qa"
      ? `【模式：問答・知識】學生會問你知識性問題（尤其宗教／宗教學／人文）。請像一位博學的助教，用${coach.langLabel}給清楚、有深度、正確的解說（可分點），reply 要資訊豐富；translation 給繁中對照。這個模式以「把知識講清楚」為主，corrections 通常留空，但你可以在最後附一個用字/表達的小提醒。`
      : chatMode === "scenario"
        ? `【模式：情境角色扮演】你要和學生進行角色扮演。依學生訊息設定的情境，你扮演對方角色（店員／面試官／神職人員／對話者…），保持角色、推進情境，自然對話。仍即時溫和糾正學生的錯誤（放 corrections）。`
        : "";

  const system = `${coach.systemPrompt}\n\n${
    modeInstr ? modeInstr + "\n\n" : ""
  }${
    persona && chatMode === "free" ? `【今日人格】${persona.label}：${persona.instruction}\n\n` : ""
  }${
    memRow?.memory ? `【你對這位學生的長期了解】\n${memRow.memory}\n\n` : ""
  }${
    summary ? `【本次對話先前摘要】\n${summary}\n\n` : ""
  }${OUTPUT_CONTRACT}`;

  // 4. 呼叫 Gemini
  const raw = await coachGemini(
    { system, contents, json: true, temperature: 0.85, maxOutputTokens: 2048 },
    { usePaid: usePaid === true, userId: user.id, supabase }
  );

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

  const today = tzToday();
  await supabase
    .from("lang_progress")
    .upsert(
      { user_id: user.id, language, last_active: today, updated_at: new Date().toISOString() },
      { onConflict: "user_id,language", ignoreDuplicates: false }
    );

  // 9. 背景壓縮摘要（每累積一定量就更新長期記憶；失敗不影響回覆）
  if ((count ?? 0) >= WINDOW + 8 && (count ?? 0) % 8 === 0) {
    summarizeSession(supabase, sid!, summary, coach.name, user.id, usePaid === true).catch(() => {});
  }

  return {
    sessionId: sid,
    reply: parsed.reply ?? "",
    translation: parsed.translation ?? "",
    corrections,
    new_vocab: newVocab,
    homework: homeworkRow,
    persona: persona ? { key: persona.key, label: persona.label, emoji: persona.emoji } : null,
  };
});

// 將窗口外的舊訊息壓縮進 session.summary（滾動式長期記憶，控制 token）
async function summarizeSession(supabase: any, sid: string, prevSummary: string, coachName: string, userId: string, usePaid: boolean) {
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
  const text = await coachGemini(
    {
      system:
        "你是學習記憶整理員。把以下語言課對話壓縮成 150 字內的繁體中文重點摘要，記錄：聊過的主題、學生的程度與常犯錯誤、已學的關鍵單字。只輸出摘要文字。",
      contents: [{ role: "user", parts: [{ text: `${prevSummary ? `【既有摘要】${prevSummary}\n\n` : ""}【新對話】\n${transcript}` }] }],
      temperature: 0.3,
      maxOutputTokens: 512,
    },
    { usePaid, userId, supabase }
  );
  await supabase.from("lang_sessions").update({ summary: text.trim() }).eq("id", sid);
}
