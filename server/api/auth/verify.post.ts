import { createClient } from "@supabase/supabase-js";

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig();

  // 檢查環境變數
  if (!config.supabaseServiceRoleKey) {
    console.error("❌ SUPABASE_SERVICE_ROLE_KEY not configured");
    throw createError({
      statusCode: 500,
      message: "伺服器配置錯誤：缺少必要的環境變數",
    });
  }

  let body;
  try {
    body = await readBody(event);
  } catch (error) {
    throw createError({
      statusCode: 400,
      message: "無效的請求內容",
    });
  }

  const { token } = body;

  if (!token) {
    throw createError({
      statusCode: 400,
      message: "缺少驗證 token",
    });
  }

  console.log("🔍 Verifying token:", token.substring(0, 10) + "...");

  let supabaseAdmin;
  try {
    supabaseAdmin = createClient(
      config.public.supabaseUrl,
      config.supabaseServiceRoleKey,
      {
        auth: {
          autoRefreshToken: false,
          persistSession: false,
        },
      },
    );
  } catch (error) {
    console.error("❌ Failed to create Supabase client:", error);
    throw createError({
      statusCode: 500,
      message: "伺服器連接失敗",
    });
  }

  try {
    // 1. 查找用戶
    console.log("🔍 Looking up user profile...");
    const { data: profile, error: profileError } = await supabaseAdmin
      .from("user_profiles")
      .select("*")
      .eq("verification_token", token)
      .single();

    if (profileError) {
      console.error("❌ Profile lookup error:", profileError);
      throw createError({
        statusCode: 400,
        message: "無效的驗證連結",
      });
    }

    if (!profile) {
      console.error("❌ No profile found for token");
      throw createError({
        statusCode: 400,
        message: "無效的驗證連結",
      });
    }

    console.log("✅ Profile found:", profile.display_name);

    // 2. 檢查是否過期
    const expiresAt = new Date(profile.verification_token_expires_at);
    const now = new Date();

    if (expiresAt < now) {
      console.error("❌ Token expired:", expiresAt, "<", now);
      throw createError({
        statusCode: 400,
        message: "驗證連結已過期，請重新註冊",
      });
    }

    // 3. 檢查是否已驗證
    if (profile.email_verified) {
      console.log("⚠️ Already verified");
      throw createError({
        statusCode: 400,
        message: "Email 已驗證，請直接登入",
      });
    }

    // 4. 更新 Supabase Auth 用戶為已驗證
    console.log("🔄 Updating auth user...");
    const { error: confirmError } =
      await supabaseAdmin.auth.admin.updateUserById(profile.user_id, {
        email_confirm: true,
      });

    if (confirmError) {
      console.error("❌ Auth update error:", confirmError);
      throw createError({
        statusCode: 500,
        message: "驗證失敗：" + confirmError.message,
      });
    }

    // 5. 更新 profile
    console.log("🔄 Updating profile...");
    const { error: updateError } = await supabaseAdmin
      .from("user_profiles")
      .update({
        email_verified: true,
        verification_token: null,
        verification_token_expires_at: null,
      })
      .eq("user_id", profile.user_id);

    if (updateError) {
      console.error("❌ Profile update error:", updateError);
      throw createError({
        statusCode: 500,
        message: "更新用戶資料失敗：" + updateError.message,
      });
    }

    console.log("✅ Verification successful for:", profile.display_name);

    return {
      success: true,
      message: "Email 驗證成功！請登入",
    };
  } catch (error: any) {
    console.error("❌ Verification error:", error);

    // 如果錯誤已經是 createError 創建的，直接拋出
    if (error.statusCode) {
      throw error;
    }

    // 否則包裝為標準錯誤
    throw createError({
      statusCode: 500,
      message: error.message || "驗證失敗",
    });
  }
});
