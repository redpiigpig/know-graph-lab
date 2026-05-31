/**
 * POST /api/lang/journal/generate
 * Body: { language, date?, usePaid? }   date 預設今天
 * 從當天的活動（對話、改錯、單字、作業、各技能時間）用 Gemini 寫一篇「教練日誌」：
 * 今天做了什麼 + 接下來該往哪走。存進 lang_journal（每日一篇，可覆寫更新）。
 */
import { getCoach } from "~/server/utils/lang-coaches";
import { coachGemini } from "~/server/utils/coach-ai";
import { parseJsonLoose } from "~/server/utils/gemini";

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const { language, date, usePaid } = (await readBody(event)) as { language: string; date?: string; usePaid?: boolean };
  const coach = getCoach(language);
  if (!coach) throw createError({ statusCode: 400, message: "不支援的語言" });
  const day = date || new Date().toISOString().slice(0, 10);

  // 當天活動
  const { data: acts } = await supabase
    .from("lang_activity")
    .select("skill, minutes, source, detail")
    .eq("user_id", user.id)
    .eq("language", language)
    .eq("activity_date", day);
  const totalMin = (acts ?? []).reduce((s: number, a: any) => s + Number(a.minutes), 0);

  if (!acts?.length || totalMin < 1) {
    // 當天沒活動，不產生日誌
    return { journal: null, skipped: true };
  }

  // 當天 session 摘要 + 改錯
  const dayStart = `${day}T00:00:00`;
  const dayEnd = `${day}T23:59:59`;
  const { data: sess } = await supabase
    .from("lang_sessions")
    .select("id, topic, mode, feedback")
    .eq("user_id", user.id)
    .eq("language", language)
    .gte("updated_at", dayStart)
    .lte("updated_at", dayEnd);
  const sessionIds = (sess ?? []).map((s: any) => s.id);
  let corrections: any[] = [];
  if (sessionIds.length) {
    const { data: msgs } = await supabase
      .from("lang_messages")
      .select("corrections, created_at")
      .in("session_id", sessionIds)
      .eq("role", "user")
      .gte("created_at", dayStart)
      .lte("created_at", dayEnd);
    corrections = (msgs ?? []).flatMap((m: any) => m.corrections || []).slice(0, 20);
  }

  const skillMin: Record<string, number> = {};
  for (const a of acts) skillMin[a.skill] = (skillMin[a.skill] || 0) + Number(a.minutes);

  const ctx = `日期：${day}
各技能時間：${Object.entries(skillMin).map(([k, v]) => `${k} ${Math.round(v)}分`).join("、")}（共 ${Math.round(totalMin)} 分）
做的活動：${[...new Set((acts).map((a: any) => a.source))].join("、")}
聊過主題：${(sess ?? []).map((s: any) => s.topic).filter(Boolean).join("、") || "（自由對話）"}
今日改錯：${corrections.map((c: any) => `「${c.original}」→「${c.fixed}」`).join("；") || "（無）"}`;

  const raw = await coachGemini(
    {
      system: `你是${coach.langLabel}教練 ${coach.name}，每天為學生寫一篇簡短「學習日誌」。
依當天活動，只輸出 JSON：
{
  "summary": "繁體中文，2–3 句：今天學生做了什麼、表現如何（教練第一人稱、溫暖具體）",
  "direction": "繁體中文一句：根據今天的狀況，接下來最該往哪個方向加強"
}
繁體中文不可簡體。`,
      contents: [{ role: "user", parts: [{ text: ctx }] }],
      json: true,
      temperature: 0.6,
      maxOutputTokens: 600,
    },
    { usePaid: usePaid === true, userId: user.id, supabase }
  );

  let j: any;
  try { j = parseJsonLoose(raw); } catch { j = { summary: raw, direction: "" }; }

  const { data: saved } = await supabase
    .from("lang_journal")
    .upsert(
      {
        user_id: user.id,
        language,
        journal_date: day,
        summary: j.summary ?? "",
        direction: j.direction ?? "",
        minutes: Math.round(totalMin * 100) / 100,
        generated_at: new Date().toISOString(),
      },
      { onConflict: "user_id,language,journal_date" }
    )
    .select("journal_date, summary, direction, minutes")
    .single();

  return { journal: saved };
});
