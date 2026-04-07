import { createClient } from "@supabase/supabase-js";

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig();
  const body = await readBody(event);
  const { gemini_key, claude_key } = body;

  // 從 Authorization header 取得 token
  const token = getHeader(event, "authorization")?.replace("Bearer ", "");

  if (!token) {
    throw createError({ statusCode: 401, message: "Unauthorized" });
  }

  // 建立 Supabase client（使用用戶 token）
  const supabase = createClient(
    config.public.supabaseUrl,
    config.public.supabaseKey,
    {
      global: {
        headers: { Authorization: `Bearer ${token}` },
      },
    },
  );

  // 驗證用戶
  const {
    data: { user },
    error: authError,
  } = await supabase.auth.getUser();

  if (authError || !user) {
    throw createError({ statusCode: 401, message: "Invalid token" });
  }

  // 加密 API keys
  const encryptedGemini = gemini_key ? encryptApiKey(gemini_key) : null;
  const encryptedClaude = claude_key ? encryptApiKey(claude_key) : null;

  // 儲存到資料庫
  const { error } = await supabase.from("user_api_keys").upsert({
    user_id: user.id,
    encrypted_gemini_key: encryptedGemini?.encrypted,
    encrypted_claude_key: encryptedClaude?.encrypted,
    encryption_iv: encryptedGemini?.iv || encryptedClaude?.iv,
  });

  if (error) {
    throw createError({ statusCode: 500, message: error.message });
  }

  return { success: true, message: "API keys saved successfully" };
});
