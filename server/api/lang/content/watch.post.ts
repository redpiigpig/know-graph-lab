/**
 * POST /api/lang/content/watch
 * Body: { language, url, minutes? }
 * 「只記錄觀看」輕量路徑：貼上 YouTube 網址即記下影片（標題＋時長），把片長計入
 * 今日聽力時間 — 不跑 Gemini 出題/討論。純 fetch，本機 dev 無 AI key 也能用。
 * 時長自動抓不到時，可由前端傳 minutes 手動指定。
 */
import { getCoach } from "~/server/utils/lang-coaches";
import { fetchYoutubeMeta } from "~/server/utils/youtube-meta";

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const { language, url, minutes } = (await readBody(event)) as {
    language: string;
    url?: string;
    minutes?: number;
  };
  const coach = getCoach(language);
  if (!coach) throw createError({ statusCode: 400, message: "不支援的語言" });
  if (!url?.trim()) throw createError({ statusCode: 400, message: "請提供 YouTube 網址" });

  const meta = await fetchYoutubeMeta(url);
  if (!meta.videoId) throw createError({ statusCode: 400, message: "無法辨識 YouTube 網址，請確認連結正確" });

  // 時長：優先用前端手動指定（minutes），否則用抓到的片長換算分鐘
  const manual = Math.round(Number(minutes) || 0);
  const autoMin = meta.durationSeconds ? Math.round(meta.durationSeconds / 60) : 0;
  const watchedMinutes = Math.max(0, manual > 0 ? manual : autoMin);

  // 抓不到時長又沒手動給 → 回報需要手動輸入分鐘（前端顯示一個分鐘輸入框）
  if (watchedMinutes <= 0) {
    throw createError({
      statusCode: 422,
      data: { code: "duration_unknown", title: meta.title },
      message: "抓不到影片長度，請手動輸入觀看分鐘數再記錄",
    });
  }

  const title = meta.title || `YouTube 影片 ${meta.videoId}`;

  // 存進沉浸內容清單（標記 watch_only，與「分析過」的內容共用一張表/歷史）
  const { data: saved } = await supabase
    .from("lang_content")
    .insert({
      user_id: user.id,
      language,
      source_type: "youtube",
      url: url.trim(),
      title,
      summary: null,
      analysis: {
        watch_only: true,
        duration_minutes: watchedMinutes,
        author: meta.author ?? null,
        video_id: meta.videoId,
      },
      session_id: null,
    })
    .select("id, source_type, url, title, summary, session_id, created_at")
    .single();

  // 片長計入今日「聽力」時間（source=youtube）
  await supabase.from("lang_activity").insert({
    user_id: user.id,
    language,
    skill: "listening",
    minutes: watchedMinutes,
    source: "youtube",
    detail: title,
  });

  // 更新最後活躍 + 累計分鐘（與 ingest 一致）
  const today = tzToday();
  const { data: prog } = await supabase
    .from("lang_progress")
    .select("total_minutes")
    .eq("user_id", user.id)
    .eq("language", language)
    .single();
  await supabase.from("lang_progress").upsert(
    {
      user_id: user.id,
      language,
      last_active: today,
      total_minutes: Math.round(((prog?.total_minutes || 0) + watchedMinutes) * 100) / 100,
      updated_at: new Date().toISOString(),
    },
    { onConflict: "user_id,language" }
  );

  return { content: saved, watchedMinutes, title, durationKnown: autoMin > 0 };
});
