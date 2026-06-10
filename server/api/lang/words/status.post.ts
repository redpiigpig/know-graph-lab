/**
 * POST /api/lang/words/status
 * Body: { language, word, status: 'known'|'learning'|'none', lemma?, meaning?, reading?, example?, sentence? }
 * 設定詞的狀態（閱讀器著色）。status=learning 時自動把該詞（含原句脈絡）加入單字庫進 FSRS；
 * status=none 時移除標記（並不刪 lang_vocab，靠 SRS 自然淡出）。
 */
export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const body = (await readBody(event)) as {
    language: string;
    word: string;
    status: "known" | "learning" | "none";
    lemma?: string;
    meaning?: string;
    reading?: string;
    example?: string;
    sentence?: string;
  };
  const { language, status } = body;
  const word = (body.word || "").trim();
  if (!language || !word) throw createError({ statusCode: 400, message: "缺少 language/word" });
  const key = word.toLowerCase();

  if (status === "none") {
    await supabase.from("lang_word_status").delete().eq("user_id", user.id).eq("language", language).eq("word", key);
    return { ok: true, status: "none" };
  }

  await supabase.from("lang_word_status").upsert(
    { user_id: user.id, language, word: key, status, updated_at: new Date().toISOString() },
    { onConflict: "user_id,language,word" }
  );

  // learning → 加入單字庫（FSRS）；以原形為單字、原句為例句脈絡
  if (status === "learning") {
    const lemma = (body.lemma || word).trim();
    await supabase.from("lang_vocab").upsert(
      {
        user_id: user.id,
        language,
        word: lemma,
        reading: body.reading || null,
        meaning: body.meaning || "",
        example: body.sentence || body.example || null,
        part_of_speech: null,
        source: "reading",
        list_key: "reader",
      },
      { onConflict: "user_id,language,word", ignoreDuplicates: true }
    );
  }
  return { ok: true, status };
});
