import { createClient } from "@supabase/supabase-js";

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig();
  const body = await readBody(event);
  const { id, provider, api_key, nickname, key_type, priority, usage_limit } =
    body;

  if (!provider || !api_key) {
    throw createError({
      statusCode: 400,
      message: "provider 和 api_key 為必填",
    });
  }

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

  // 加密 API key
  const { encrypted, iv } = encryptApiKey(api_key);

  if (id) {
    // 更新現有 key
    const { error } = await supabase
      .from("api_keys")
      .update({
        provider,
        encrypted_key: encrypted,
        encryption_iv: iv,
        nickname: nickname || null,
        key_type: key_type || "free",
        priority: priority ?? 1,
        usage_limit: usage_limit || null,
      })
      .eq("id", id)
      .eq("user_id", user.id);

    if (error) {
      throw createError({ statusCode: 500, message: error.message });
    }
  } else {
    // 新增 key
    const { error } = await supabase.from("api_keys").insert({
      user_id: user.id,
      provider,
      encrypted_key: encrypted,
      encryption_iv: iv,
      nickname: nickname || null,
      key_type: key_type || "free",
      priority: priority ?? 1,
      usage_limit: usage_limit || null,
      current_usage: 0,
      is_active: true,
      is_exhausted: false,
    });

    if (error) {
      throw createError({ statusCode: 500, message: error.message });
    }
  }

  return { success: true, message: "API key saved successfully" };
});
