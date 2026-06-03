/**
 * GET /api/lang/daily?language=en
 * 今日計畫：推薦 5 篇閱讀 / 5 段聽力 / 口說題 + 每日任務（生成一次快取），
 * 加單字進度（已記住 / 待複習 / 占目標程度約幾 %）。
 */
import { getCoach } from "~/server/utils/lang-coaches";
import { coachGemini } from "~/server/utils/coach-ai";
import { parseJsonLoose } from "~/server/utils/gemini";

// 各程度「主動詞彙量」概估（占比用），英文 CEFR；其餘語言用近似
const VOCAB_TARGET: Record<string, number> = {
  A1: 500, A2: 1000, B1: 2000, B2: 3250, C1: 5000, C2: 8000,
  N5: 800, N4: 1500, N3: 3000, N2: 6000, N1: 10000,
};

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const language = (getQuery(event).language as string) || "en";
  const coach = getCoach(language);
  if (!coach) throw createError({ statusCode: 400, message: "不支援的語言" });
  const today = tzToday();

  const { data: prog } = await supabase
    .from("lang_progress")
    .select("level")
    .eq("user_id", user.id)
    .eq("language", language)
    .single();
  const lv = prog?.level || coach.defaultLevel || coach.levelScale[0];
  const goalLevel = coach.levelScale[coach.levelScale.length - 1];

  // 單字進度
  const today_ = today;
  const [{ data: allVocab }, { count: dueCount }] = await Promise.all([
    supabase.from("lang_vocab").select("mastery_level").eq("user_id", user.id).eq("language", language),
    supabase.from("lang_vocab").select("id", { count: "exact", head: true }).eq("user_id", user.id).eq("language", language).lte("next_review", today_),
  ]);
  const totalVocab = (allVocab ?? []).length;
  const memorized = (allVocab ?? []).filter((v: any) => (v.mastery_level || 0) >= 3).length;
  const goalTarget = VOCAB_TARGET[goalLevel] || 8000;
  const pctOfGoal = Math.min(100, Math.round((memorized / goalTarget) * 1000) / 10);

  // 今日計畫（快取）
  const { data: existing } = await supabase
    .from("lang_daily")
    .select("plan")
    .eq("user_id", user.id)
    .eq("language", language)
    .eq("plan_date", today)
    .single();

  let plan: any = existing?.plan;
  if (!plan?.reading?.length) {
    const interests = "宗教／宗教學／神話為主軸，輔以人文，偶爾理工醫/生活/旅遊";
    const raw = await coachGemini(
      {
        system: `你是${coach.langLabel}學習規劃師，為「${lv}」程度、做宗教研究的學生排今天的內容。題材：${interests}。
只輸出 JSON：{
  "reading": ["5 個適合該程度的閱讀主題（${coach.langLabel}文章方向，繁中標題即可）"],
  "listening": ["5 個聽力段落主題"],
  "speaking": ["5 個口說討論題（繁中）"]
}
各 5 個，難度貼合 ${lv}。繁體中文不可簡體。`,
        contents: [{ role: "user", parts: [{ text: "排今天的閱讀/聽力/口說推薦。" }] }],
        json: true,
        temperature: 0.7,
        maxOutputTokens: 1024,
      },
      { usePaid: false, userId: user.id, supabase }
    ).catch(() => null);

    let g: any = { reading: [], listening: [], speaking: [] };
    if (raw) { try { g = parseJsonLoose(raw); } catch { /* keep empty */ } }

    const mk = (arr: any[], prefix: string) =>
      (arr || []).slice(0, 5).map((t: string, i: number) => ({ id: `${prefix}${i + 1}`, topic: t, content: null, session_id: null, done: false }));

    plan = {
      tasks: [
        { id: "t1", label: `複習 ${Math.min(20, dueCount ?? 0) || 10} 個到期單字`, done: false },
        { id: "t2", label: "讀完 1 篇推薦文章並討論", done: false },
        { id: "t3", label: "聽完 1 段並作答", done: false },
        { id: "t4", label: "完成 1 題口說", done: false },
        { id: "t5", label: "上 1 堂文法課", done: false },
      ],
      reading: mk(g.reading, "r"),
      listening: mk(g.listening, "l"),
      speaking: (g.speaking || []).slice(0, 5).map((p: string, i: number) => ({ id: `s${i + 1}`, prompt: p, done: false })),
    };

    await supabase
      .from("lang_daily")
      .upsert({ user_id: user.id, language, plan_date: today, plan }, { onConflict: "user_id,language,plan_date" });
  }

  return {
    level: lv,
    goalLevel,
    plan,
    vocab: { total: totalVocab, memorized, due: dueCount ?? 0, goalTarget, pctOfGoal },
  };
});
