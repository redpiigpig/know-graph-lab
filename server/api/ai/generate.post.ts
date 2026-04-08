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

  // 從 api_keys 表智能選擇最佳 Gemini key
  const result = await selectBestApiKey(
    user.id,
    "gemini",
    config.public.supabaseUrl,
    config.public.supabaseKey,
  );

  if (!result) {
    throw createError({
      statusCode: 400,
      message: "Please set your Gemini API key in settings",
    });
  }

  const { key: geminiKey, keyId } = result;

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

  const success = response.ok;
  let errorMessage: string | null = null;
  let data: any = null;

  if (!response.ok) {
    const errData = await response.json();
    errorMessage = errData.error?.message || "Gemini API error";
  } else {
    data = await response.json();
  }

  // 記錄使用
  await logApiUsage(
    keyId,
    user.id,
    "/api/ai/generate",
    0,
    success,
    errorMessage,
    config.public.supabaseUrl,
    config.public.supabaseKey,
  );

  if (!success) {
    throw createError({ statusCode: 502, message: errorMessage! });
  }

  const content = data.candidates[0].content.parts[0].text;

  return {
    success: true,
    data: JSON.parse(content),
  };
});
