/**
 * POST /api/lang/offline/import
 * Body: { language, text }  — text = 從 NotebookLM / Gemini 貼回的成果報告（可含整段對話）
 *
 * 零 AI：用 parseOfflineReport() 確定性解析，然後：
 *   1. lang_activity — 各技能分鐘（source=offline），日期用報告日期（限近 30 天，否則今天）
 *   2. lang_progress — streak／累計分鐘（報告日=今天才 bump streak，與 activity.post 同邏輯）
 *   3. lang_sessions — mode=offline 一筆（topic=練習內容、feedback=評分/強弱項）
 *   4. lang_messages — 一筆 user 訊息掛 corrections（教練日誌 generate 會撿到改錯）
 *   5. lang_vocab — 新學單字 upsert（source=offline）＋ 複習結果套 FSRS（對=good/錯=again）
 */
import { parseOfflineReport, reportHasData } from "~/utils/offlineReport";
import { fsrs } from "~/server/utils/srs";
import { getCoach } from "~/server/utils/lang-coaches";

const SKILLS = ["listening", "speaking", "reading", "writing"];

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const { language, text } = (await readBody(event)) as { language: string; text: string };
  const coach = getCoach(language);
  if (!coach) throw createError({ statusCode: 400, message: "不支援的語言" });
  if (!text?.trim()) throw createError({ statusCode: 400, message: "請貼上成果報告" });

  const report = parseOfflineReport(text);
  if (!report) {
    throw createError({ statusCode: 400, message: "找不到「【練習成果報告】」標記——請把 AI 輸出的報告整段貼上（含標題行）；若 AI 沒輸出報告，請它依練習包第四節的格式補一份。" });
  }
  if (!reportHasData(report)) {
    throw createError({ statusCode: 400, message: "報告解析成功但沒有可入庫的內容（技能時間／單字／改錯都是空的），請確認 AI 有如實填寫。" });
  }

  const today = tzToday();
  // 報告日期只收近 30 天內（避免 AI 亂填未來日或太舊的日期）
  let day = today;
  if (report.date && report.date <= today && report.date >= tzDaysAgo(30)) day = report.date;

  const detail = report.content || "FSI 離線練習";
  const skills = report.skills.filter((s) => SKILLS.includes(s.skill) && s.minutes > 0);
  const totalMin = Math.round(skills.reduce((s, a) => s + a.minutes, 0) * 100) / 100;

  // 1. 活動時間
  if (skills.length) {
    await supabase.from("lang_activity").insert(
      skills.map((s) => ({
        user_id: user.id,
        language,
        activity_date: day,
        skill: s.skill,
        minutes: Math.round(s.minutes * 100) / 100,
        source: "offline",
        detail,
      }))
    );

    // 2. 進度：累計分鐘一律加；streak 只在報告日=今天時比照 activity.post 邏輯
    const { data: prog } = await supabase
      .from("lang_progress")
      .select("streak_days, last_active, total_minutes")
      .eq("user_id", user.id)
      .eq("language", language)
      .single();
    const patch: Record<string, unknown> = {
      user_id: user.id,
      language,
      total_minutes: Math.round(((prog?.total_minutes || 0) + totalMin) * 100) / 100,
      updated_at: new Date().toISOString(),
    };
    if (day === today) {
      let streak = 1;
      if (prog?.last_active === today) streak = prog.streak_days || 1;
      else if (prog?.last_active === tzDaysAgo(1)) streak = (prog?.streak_days || 0) + 1;
      patch.streak_days = streak;
      patch.last_active = today;
    }
    await supabase.from("lang_progress").upsert(patch, { onConflict: "user_id,language" });
  }

  // 3. session（離線練習也留一筆對話紀錄，讓日誌／記憶統整撿得到）
  const feedback = {
    overall: report.overall,
    strengths: report.strengths,
    improvements: report.improvements,
    comment: `離線練習（NotebookLM/Gemini）：${detail}`,
  };
  const { data: sess } = await supabase
    .from("lang_sessions")
    .insert({
      user_id: user.id,
      language,
      title: `離線練習：${detail}`.slice(0, 80),
      mode: "offline",
      topic: detail,
      summary: [
        report.strengths.length ? `強項：${report.strengths.join("；")}` : "",
        report.improvements.length ? `待加強：${report.improvements.join("；")}` : "",
      ].filter(Boolean).join("\n") || null,
      feedback,
    })
    .select("id")
    .single();

  // 4. 改錯掛在一筆 user 訊息上（journal/generate 讀 lang_messages.corrections）
  if (sess?.id && report.corrections.length) {
    await supabase.from("lang_messages").insert({
      session_id: sess.id,
      user_id: user.id,
      role: "user",
      content: `（離線練習改錯回報：${detail}）`,
      corrections: report.corrections.map((c) => ({ original: c.original, fixed: c.fixed })),
    });
  }

  // 5a. 新學單字
  let wordsAdded = 0;
  if (report.newWords.length) {
    const rows = report.newWords
      .filter((w) => w.word)
      .map((w) => ({
        user_id: user.id,
        language,
        word: w.word.slice(0, 120),
        reading: w.reading,
        meaning: w.meaning ?? "",
        example: w.example,
        part_of_speech: null,
        source: "offline",
      }));
    if (rows.length) {
      await supabase.from("lang_vocab").upsert(rows, { onConflict: "user_id,language,word", ignoreDuplicates: true });
      wordsAdded = rows.length;
    }
  }

  // 5b. 複習結果 → FSRS（對=good(4)／錯=again(2)），逐字比對既有單字
  let reviewed = 0;
  let reviewMisses: string[] = [];
  if (report.reviews.length) {
    const words = [...new Set(report.reviews.map((r) => r.word))];
    const { data: owned } = await supabase
      .from("lang_vocab")
      .select("id, word, difficulty, stability, last_reviewed, repetitions")
      .eq("user_id", user.id)
      .eq("language", language)
      .in("word", words);
    const byWord = new Map((owned ?? []).map((v: any) => [String(v.word).toLowerCase(), v]));
    for (const r of report.reviews) {
      const v = byWord.get(r.word.toLowerCase());
      if (!v) { reviewMisses.push(r.word); continue; }
      let elapsed = 0;
      if (v.last_reviewed) {
        elapsed = Math.max(0, Math.round((new Date(today).getTime() - new Date(v.last_reviewed).getTime()) / 86400000));
      }
      const next = fsrs({ difficulty: v.difficulty ?? null, stability: v.stability ?? null }, r.correct ? 4 : 2, elapsed);
      await supabase
        .from("lang_vocab")
        .update({
          difficulty: next.difficulty,
          stability: next.stability,
          interval_days: next.interval_days,
          repetitions: (v.repetitions ?? 0) + 1,
          mastery_level: next.mastery_level,
          next_review: next.next_review,
          last_reviewed: today,
          updated_at: new Date().toISOString(),
        })
        .eq("id", v.id)
        .eq("user_id", user.id);
      reviewed++;
    }
  }

  return {
    ok: true,
    date: day,
    minutes: totalMin,
    skills: Object.fromEntries(skills.map((s) => [s.skill, s.minutes])),
    overall: report.overall,
    wordsAdded,
    reviewed,
    reviewMisses, // 報告裡有、但單字庫找不到的字（沒套 SRS，僅提示）
    corrections: report.corrections.length,
    sessionId: sess?.id ?? null,
  };
});
