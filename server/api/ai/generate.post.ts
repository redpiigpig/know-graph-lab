import { createClient } from "@supabase/supabase-js";

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig();
  const body = await readBody(event);
  const { prompt, chartType } = body;

  // 驗證用戶並取得 token
  const token = getHeader(event, "authorization")?.replace("Bearer ", "");

  if (!token) {
    throw createError({ statusCode: 401, message: "Unauthorized" });
  }

  const supabase = createClient(
    config.public.supabaseUrl,
    config.public.supabaseKey,
    {
      global: {
        headers: { Authorization: `Bearer ${token}` },
      },
    },
  );

  const {
    data: { user },
    error: authError,
  } = await supabase.auth.getUser();

  if (authError || !user) {
    throw createError({ statusCode: 401, message: "Invalid token" });
  }

  // 從資料庫取得加密的 API key
  const { data: keyData, error: keyError } = await supabase
    .from("user_api_keys")
    .select("encrypted_gemini_key, encryption_iv")
    .eq("user_id", user.id)
    .single();

  if (keyError || !keyData?.encrypted_gemini_key) {
    throw createError({
      statusCode: 400,
      message: "Please set your API key in settings",
    });
  }

  // 解密 API key
  const geminiKey = decryptApiKey(
    keyData.encrypted_gemini_key,
    keyData.encryption_iv,
  );

  // 呼叫 Gemini API
  const response = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=${geminiKey}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [
          {
            parts: [{ text: prompt }],
          },
        ],
        generationConfig: {
          temperature: 0.7,
          responseMimeType: "application/json",
        },
      }),
    },
  );

  if (!response.ok) {
    const error = await response.json();
    throw createError({
      statusCode: response.status,
      message: error.error?.message || "Gemini API error",
    });
  }

  const data = await response.json();
  const content = data.candidates[0].content.parts[0].text;

  return {
    success: true,
    data: JSON.parse(content),
  };
});
