/**
 * GET /api/lang/briefing?language=en
 * 教練主動簡報：依目標 / 弱點 / 今日進度，給「今天該做什麼、加強什麼」+ 建議行動。
 */
import { getCoach } from "~/server/utils/lang-coaches";
import { coachGemini } from "~/server/utils/coach-ai";
import { parseJsonLoose } from "~/server/utils/gemini";

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const language = (getQuery(event).language as string) || "en";
  const coach = getCoach(language);
  if (!coach) throw createError({ statusCode: 400, message: "不支援的語言" });
  const today = new Date().toISOString().slice(0, 10);

  const [profileR, progR, memR, dueR, todayActR] = await Promise.all([
    supabase.from("lang_profile").select("goal_level, target_exam, exam_date, daily_goal_minutes, interests").eq("user_id", user.id).single(),
    supabase.from("lang_progress").select("level, streak_days").eq("user_id", user.id).eq("language", language).single(),
    supabase.from("lang_memory").select("highlights, briefing, briefing_date").eq("user_id", user.id).eq("language", language).single(),
    supabase.from("lang_vocab").select("id", { count: "exact", head: true }).eq("user_id", user.id).eq("language", language).lte("next_review", today),
    supabase.from("lang_activity").select("skill, minutes").eq("user_id", user.id).eq("language", language).eq("activity_date", today),
  ]);

  const profile = profileR.data ?? {};
  const hl = (memR.data?.highlights ?? {}) as any;
  const todayMin = (todayActR.data ?? []).reduce((s: number, a: any) => s + Number(a.minutes), 0);
  let daysToExam: number | null = null;
  if (profile.exam_date) daysToExam = Math.ceil((new Date(profile.exam_date).getTime() - Date.now()) / 86400000);

  const ctx = `學生資料：
- 目前等級 ${progR.data?.level || "B2"} → 目標 ${profile.goal_level || "C2"}
- 目標考試 ${profile.target_exam || "無"}${daysToExam !== null ? `（剩 ${daysToExam} 天）` : ""}
- 今日已學習 ${Math.round(todayMin)} 分 / 目標 ${profile.daily_goal_minutes || 90} 分；連續 ${progR.data?.streak_days || 0} 天
- 待複習單字 ${dueR.count ?? 0} 個
- 興趣：${Array.isArray(profile.interests) ? profile.interests.join("、") : "人文"}
- 反覆弱點：${(hl.weaknesses || []).join("、") || "（尚無紀錄）"}
- 建議加強：${(hl.next_focus || []).join("、") || "（尚無）"}`;

  // 每日快取：同一天只用 Gemini 生成一次簡報（統計仍每次即時算）
  let briefing: any = null;
  const force = getQuery(event).force === "1";
  if (!force && memR.data?.briefing_date === today && memR.data?.briefing) {
    briefing = memR.data.briefing;
  } else {
    const raw = await coachGemini(
      {
        system: `你是${coach.langLabel}教練 ${coach.name}，每次學生進來時主動給一段「今日簡報」。
依學生資料，只輸出 JSON：
{
  "greeting": "一句親切的繁體中文招呼（可帶今日狀態，如連續天數、距考試天數）",
  "focus": "今天最該做的一件事（繁體中文，具體，扣著目標與弱點）",
  "actions": [ { "label": "建議行動（如：做一篇 TOEFL 獨立寫作）", "route": "chat|smalltalk|practice|review|immersion" } ],
  "tip": "針對某個反覆弱點的一句小提醒（繁體中文，若無弱點可給通用進階建議）"
}
actions 給 2–3 個，route 從 chat/smalltalk/practice/review/immersion 擇一。語氣鼓勵、像真的教練。繁體中文不可簡體。`,
        contents: [{ role: "user", parts: [{ text: ctx }] }],
        json: true,
        temperature: 0.6,
        maxOutputTokens: 700,
      },
      { usePaid: false, userId: user.id, supabase }
    ).catch(() => null);

    if (raw) {
      try { briefing = parseJsonLoose(raw); } catch { briefing = null; }
    }
    // 快取今日簡報（不動 updated_at，那欄代表「記憶內容」的更新時間）
    if (briefing) {
      await supabase
        .from("lang_memory")
        .upsert(
          { user_id: user.id, language, briefing, briefing_date: today },
          { onConflict: "user_id,language" }
        );
    }
  }

  return {
    briefing,
    stats: {
      level: progR.data?.level || "B2",
      goalLevel: profile.goal_level || "C2",
      targetExam: profile.target_exam || null,
      daysToExam,
      todayMinutes: Math.round(todayMin),
      dailyGoal: profile.daily_goal_minutes || 90,
      streak: progR.data?.streak_days || 0,
      vocabDue: dueR.count ?? 0,
    },
  };
});
