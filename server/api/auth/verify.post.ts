import { createClient } from "@supabase/supabase-js";

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig();
  const body = await readBody(event);
  const { token } = body;

  if (!token) {
    throw createError({
      statusCode: 400,
      message: "缺少驗證 token",
    });
  }

  const supabaseAdmin = createClient(
    config.public.supabaseUrl,
    config.supabaseServiceRoleKey,
    {
      auth: {
        autoRefreshToken: false,
        persistSession: false,
      },
    },
  );

  try {
    // 1. 查找用戶
    const { data: profile, error: profileError } = await supabaseAdmin
      .from("user_profiles")
      .select("*")
      .eq("verification_token", token)
      .single();

    if (profileError || !profile) {
      throw createError({
        statusCode: 400,
        message: "無效的驗證連結",
      });
    }

    // 2. 檢查是否過期
    if (new Date(profile.verification_token_expires_at) < new Date()) {
      throw createError({
        statusCode: 400,
        message: "驗證連結已過期",
      });
    }

    // 3. 檢查是否已驗證
    if (profile.email_verified) {
      throw createError({
        statusCode: 400,
        message: "Email 已驗證，請直接登入",
      });
    }

    // 4. 更新 Supabase Auth 用戶為已驗證
    const { error: confirmError } =
      await supabaseAdmin.auth.admin.updateUserById(profile.user_id, {
        email_confirm: true,
      });

    if (confirmError) {
      throw createError({
        statusCode: 500,
        message: "驗證失敗",
      });
    }

    // 5. 更新 profile
    await supabaseAdmin
      .from("user_profiles")
      .update({
        email_verified: true,
        verification_token: null,
        verification_token_expires_at: null,
      })
      .eq("user_id", profile.user_id);

    return {
      success: true,
      message: "Email 驗證成功！請登入",
    };
  } catch (error: any) {
    throw createError({
      statusCode: error.statusCode || 500,
      message: error.message || "驗證失敗",
    });
  }
});
