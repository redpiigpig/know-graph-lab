/**
 * POST /api/lang/task/[id]/answer
 * Body: { response?, answers?: string[], minutes? }
 * comprehension（讀/聽）→ 自動批改選擇題；production（寫/說）→ Gemini Pro rubric 評分。
 * 並記錄該技能練習時間。
 */
import { getCoach } from "~/server/utils/lang-coaches";
import { parseJsonLoose } from "~/server/utils/gemini";
import { coachGemini } from "~/server/utils/coach-ai";

// 各考試的評分標準（rubric）
function rubricFor(exam: string | null, skill: string) {
  if (exam === "TOEFL" && skill === "speaking")
    return "TOEFL iBT Speaking rubric（0–4，再換算 0–30）：Delivery（流暢/發音）、Language Use（文法/詞彙）、Topic Development（內容完整/連貫）。";
  if (exam === "TOEFL" && skill === "writing")
    return "TOEFL iBT Writing rubric（0–5，再換算 0–30）：Development（論述展開）、Organization（組織連貫）、Language Use（句法/詞彙準確）。";
  if (exam === "IELTS")
    return "IELTS rubric（band 0–9）：Task Achievement/Response、Coherence & Cohesion、Lexical Resource、Grammatical Range & Accuracy。band 給到 0.5。";
  if (exam === "GRE" && skill === "writing")
    return "GRE Analytical Writing rubric（0–6）：論點清晰度、論證與例證、組織、語言掌控。";
  return "一般學術 rubric（0–100）：內容與論述、組織連貫、詞彙豐富度、文法準確度。";
}

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const id = getRouterParam(event, "id");
  const { response, answers, minutes, usePaid } = (await readBody(event)) as {
    response?: string;
    answers?: string[];
    minutes?: number;
    usePaid?: boolean;
  };

  const { data: task } = await supabase
    .from("lang_tasks")
    .select("*")
    .eq("id", id)
    .eq("user_id", user.id)
    .single();
  if (!task) throw createError({ statusCode: 404, message: "找不到題目" });

  const coach = getCoach(task.language);
  const questions = task.materials?.questions as any[] | undefined;
  let scores: any = {};
  let band: number | null = null;
  let feedback = "";

  if (questions?.length) {
    // 自動批改選擇題
    const sel = Array.isArray(answers) ? answers : [];
    let correct = 0;
    const detail = questions.map((q: any, i: number) => {
      const pick = (sel[i] || "").toUpperCase().slice(0, 1);
      const ans = String(q.answer || "").toUpperCase().slice(0, 1);
      const ok = pick === ans;
      if (ok) correct++;
      return { q: q.q, your: pick, answer: ans, correct: ok };
    });
    const total = questions.length;
    band = Math.round((correct / total) * 100);
    scores = { correct_count: correct, total, detail };
    feedback = `答對 ${correct}/${total} 題。`;
  } else if (task.skill === "translation") {
    // 翻譯遊戲評分
    if (!response?.trim()) throw createError({ statusCode: 400, message: "請先作答" });
    const src = task.materials?.source_text ?? "";
    const toZh = task.materials?.direction === "target2zh";
    const raw = await coachGemini({
      model: useRuntimeConfig().geminiGradeModel as string,
      system: `你是${coach?.langLabel}翻譯評分老師。評學生的翻譯（方向：${toZh ? coach?.langLabel + "→繁中" : "繁中→" + coach?.langLabel}）。
只輸出 JSON：{
  "band": 0-100 總分,
  "scores": { "accuracy": 0-100, "fluency": 0-100, "register": 0-100 },
  "model_translation": "你的參考翻譯（${toZh ? "繁體中文" : coach?.langLabel}）",
  "feedback": "繁體中文回饋：翻得好的地方、誤譯/不自然處（舉原句）、更道地的說法"
}
繁體中文不可簡體。`,
      contents: [{ role: "user", parts: [{ text: `【原文】\n${src}\n\n【學生翻譯】\n${response}` }] }],
      json: true,
      temperature: 0.3,
      maxOutputTokens: 2048,
    }, { usePaid: usePaid === true, userId: user.id, supabase });
    try {
      const p = parseJsonLoose(raw);
      band = typeof p.band === "number" ? p.band : null;
      scores = p.scores ?? {};
      feedback = (p.feedback ?? "") + (p.model_translation ? `\n\n📝 參考翻譯：${p.model_translation}` : "");
    } catch {
      feedback = raw;
    }
  } else {
    // 產出型 → Gemini rubric 評分
    if (!response?.trim()) throw createError({ statusCode: 400, message: "請先作答" });
    const rubric = rubricFor(task.exam, task.skill);
    const raw = await coachGemini({
      model: useRuntimeConfig().geminiGradeModel as string,
      system: `你是${coach?.langLabel}${task.exam ? task.exam + " " : ""}評分官。依下列 rubric 評分學生作答。
Rubric：${rubric}
只輸出 JSON：{ "band": 分數數字（依 rubric 量表）, "scores": { 各分項: 分數 }, "feedback": "繁體中文回饋：強項、弱項、如何提升到下一級（具體、可附目標語言示範）" }`,
      contents: [{ role: "user", parts: [{ text: `【題目】${task.prompt}\n\n【學生作答】\n${response}` }] }],
      json: true,
      temperature: 0.3,
      maxOutputTokens: 2048,
    }, { usePaid: usePaid === true, userId: user.id, supabase });
    try {
      const p = parseJsonLoose(raw);
      band = typeof p.band === "number" ? p.band : null;
      scores = p.scores ?? {};
      feedback = p.feedback ?? "";
    } catch {
      feedback = raw;
    }
  }

  const { data: updated } = await supabase
    .from("lang_tasks")
    .update({
      response: response ?? (answers ? JSON.stringify(answers) : null),
      scores,
      band,
      feedback,
      status: "scored",
      updated_at: new Date().toISOString(),
    })
    .eq("id", id)
    .eq("user_id", user.id)
    .select("*")
    .single();

  // 記錄練習時間（翻譯歸入「寫」技能統計）
  const mins = Math.max(0.5, Number(minutes) || 0);
  const activitySkill = task.skill === "translation" ? "writing" : task.skill;
  await supabase.from("lang_activity").insert({
    user_id: user.id,
    language: task.language,
    skill: activitySkill,
    minutes: Math.round(mins * 100) / 100,
    source: task.mode === "exam" ? "exam" : task.skill === "translation" ? "translation" : "practice",
    detail: task.topic,
  });
  // 更新 streak/last_active
  const today = tzToday();
  const { data: prog } = await supabase
    .from("lang_progress")
    .select("streak_days, last_active, total_minutes")
    .eq("user_id", user.id)
    .eq("language", task.language)
    .single();
  let streak = 1;
  if (prog?.last_active) {
    const yest = tzDaysAgo(1);
    streak = prog.last_active === today ? prog.streak_days || 1 : prog.last_active === yest ? (prog.streak_days || 0) + 1 : 1;
  }
  await supabase.from("lang_progress").upsert(
    { user_id: user.id, language: task.language, streak_days: streak, last_active: today, total_minutes: Math.round(((prog?.total_minutes || 0) + mins) * 100) / 100, updated_at: new Date().toISOString() },
    { onConflict: "user_id,language" }
  );

  return { task: updated };
});
