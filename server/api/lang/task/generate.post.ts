/**
 * POST /api/lang/task/generate
 * Body: { language, mode:'practice'|'exam', exam?, skill, taskType?, topic? }
 * 用 Gemini 生成一道練習/考試題（聽說讀寫）。
 * reading/listening → 文章/聽稿 + 選擇題；writing/speaking → 題目指示。
 */
import { getCoach } from "~/server/utils/lang-coaches";
import { callGemini, parseJsonLoose } from "~/server/utils/gemini";

const SKILLS = ["listening", "speaking", "reading", "writing"];

// 各考試 / 技能的題型描述（餵給生成器）
function taskBrief(exam: string | undefined, skill: string, taskType: string | undefined) {
  if (exam === "TOEFL") {
    const map: Record<string, string> = {
      reading: "TOEFL iBT 學術閱讀：一段 250–350 字學術短文 + 4 題單選（含詞彙題、推論題）。",
      listening: "TOEFL iBT 校園/講座聽力：一段 200–300 字講座聽稿 + 4 題單選。",
      writing: taskType === "email" ? "TOEFL 2026 Write an Email 題型：情境 email 寫作。" : "TOEFL Independent Writing：一個論述題，要求 300 字以上短文。",
      speaking: taskType === "interview" ? "TOEFL 2026 Interview Speaking：訪談式口說問題。" : "TOEFL Independent Speaking：一個 45 秒準備、口說回答的題目。",
    };
    return map[skill];
  }
  if (exam === "IELTS") {
    const map: Record<string, string> = {
      reading: "IELTS Academic Reading：一段學術短文 + 4 題單選。",
      listening: "IELTS Listening：一段聽稿 + 4 題單選。",
      writing: "IELTS Academic Writing Task 2：論述 essay（250 字以上）。",
      speaking: "IELTS Speaking Part 2/3：cue card 主題 + 延伸討論。",
    };
    return map[skill];
  }
  if (exam === "GRE") {
    const map: Record<string, string> = {
      reading: "GRE Verbal Reading Comprehension：一段較密的學術短文 + 4 題單選（含推論、主旨）。",
      writing: "GRE Analytical Writing (Issue)：針對一個議題提出論點。",
      speaking: "進階學術口說：針對一個抽象議題即席論述。",
      listening: "進階學術聽力：一段密集論述聽稿 + 4 題單選。",
    };
    return map[skill];
  }
  // 一般練習
  const map: Record<string, string> = {
    reading: "一段該程度的人文學術短文（200–300 字）+ 4 題單選理解題。",
    listening: "一段該程度的人文主題聽稿（150–250 字）+ 4 題單選理解題。",
    writing: "一個人文相關的寫作題目，要求短文回應。",
    speaking: "一個人文相關、可口說 1–2 分鐘的獨白題目。",
  };
  return map[skill];
}

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const { language, mode, exam, skill, taskType, topic } = (await readBody(event)) as {
    language: string;
    mode?: string;
    exam?: string;
    skill: string;
    taskType?: string;
    topic?: string;
  };
  const coach = getCoach(language);
  if (!coach) throw createError({ statusCode: 400, message: "不支援的語言" });
  if (!SKILLS.includes(skill)) throw createError({ statusCode: 400, message: "skill 不正確" });

  const { data: profile } = await supabase
    .from("lang_profile")
    .select("goal_level, interests")
    .eq("user_id", user.id)
    .single();
  const lv = profile?.goal_level || "C1";
  const interests = Array.isArray(profile?.interests) && profile!.interests.length ? profile!.interests.join("、") : "人文（哲學/歷史/文學）";
  const isComprehension = skill === "reading" || skill === "listening";

  const system = `你是${coach.langLabel}${exam ? exam + " 考試" : "學術"}出題老師。為 CEFR ${lv}、興趣為「${interests}」的學生出一題。
題型：${taskBrief(exam, skill, taskType)}
只輸出 JSON：
{
  "topic": "主題",
  "prompt": "給學生的指示（${coach.langLabel}題目本體；可附繁中簡短說明）",
  ${skill === "reading" ? '"passage": "閱讀短文（目標語言）",' : ""}
  ${skill === "listening" ? '"audio_text": "聽力稿（目標語言，將由系統朗讀，學生看不到）",' : ""}
  ${isComprehension ? '"questions": [ { "q": "題目", "options": ["A. ...","B. ...","C. ...","D. ..."], "answer": "A" } ],' : ""}
  "tip": "作答提示（繁中）"
}
${isComprehension ? "questions 出 4 題單選，answer 用 A/B/C/D。" : "這是產出型題目，不要 questions。"}
繁體中文不可簡體。`;

  const raw = await callGemini({
    system,
    contents: [{ role: "user", parts: [{ text: topic ? `指定主題：${topic}` : "請出題。" }] }],
    json: true,
    temperature: 0.7,
    maxOutputTokens: 3072,
  });

  let g: any;
  try {
    g = parseJsonLoose(raw);
  } catch {
    throw createError({ statusCode: 502, message: "出題解析失敗，請重試" });
  }

  const materials: any = {};
  if (g.passage) materials.passage = g.passage;
  if (g.audio_text) materials.audio_text = g.audio_text;
  if (Array.isArray(g.questions)) materials.questions = g.questions;
  if (g.tip) materials.tip = g.tip;

  const { data: task } = await supabase
    .from("lang_tasks")
    .insert({
      user_id: user.id,
      language,
      mode: mode === "exam" ? "exam" : "practice",
      exam: mode === "exam" ? exam ?? null : null,
      skill,
      task_type: taskType ?? null,
      level: lv,
      topic: g.topic ?? topic ?? null,
      prompt: g.prompt ?? "",
      materials,
      status: "generated",
    })
    .select("*")
    .single();

  return { task };
});
