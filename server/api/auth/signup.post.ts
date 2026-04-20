import { createClient } from "@supabase/supabase-js";
import { Resend } from "resend";
import crypto from "crypto";

export default defineEventHandler(async (_event) => {
  throw createError({
    statusCode: 403,
    message: "此為私人專案，不開放公開註冊。",
  });

  // 以下程式碼已停用
  const config = useRuntimeConfig();
  const body = await readBody(_event);

  const { email, password, displayName, academicFields, ageRange } = body;

  // 驗證必填欄位
  if (!email || !password || !displayName) {
    throw createError({
      statusCode: 400,
      message: "Email、密碼和姓名為必填欄位",
    });
  }

  // 建立 Supabase Admin Client
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
    // 1. 建立 Supabase Auth 用戶
    const { data: authData, error: authError } =
      await supabaseAdmin.auth.admin.createUser({
        email,
        password,
        email_confirm: false,
        user_metadata: {
          display_name: displayName,
        },
      });

    if (authError) {
      throw createError({
        statusCode: 400,
        message: authError.message,
      });
    }

    // 2. 生成驗證 token
    const verificationToken = crypto.randomBytes(32).toString("hex");
    const expiresAt = new Date();
    expiresAt.setHours(expiresAt.getHours() + 24);

    // 3. 建立用戶資料（academicFields 現在是陣列）
    const { error: profileError } = await supabaseAdmin
      .from("user_profiles")
      .insert({
        user_id: authData.user.id,
        display_name: displayName,
        academic_field: academicFields || [], // 陣列格式
        age_range: ageRange,
        email_verified: false,
        verification_token: verificationToken,
        verification_token_expires_at: expiresAt.toISOString(),
      });

    if (profileError) {
      await supabaseAdmin.auth.admin.deleteUser(authData.user.id);
      throw createError({
        statusCode: 500,
        message: "建立用戶資料失敗：" + profileError.message,
      });
    }

    // 4. 發送驗證郵件
    const resend = new Resend(config.resendApiKey);
    const verificationUrl = `${config.public.appUrl}/auth/verify?token=${verificationToken}`;

    // 格式化學術領域顯示
    const fieldLabels: Record<string, string> = {
      computer_science: "資訊科學",
      engineering: "工程學",
      natural_sciences: "自然科學",
      physics: "物理學",
      chemistry: "化學",
      biology: "生物學",
      mathematics: "數學",
      social_sciences: "社會科學",
      psychology: "心理學",
      sociology: "社會學",
      economics: "經濟學",
      political_science: "政治學",
      humanities: "人文學科",
      history: "歷史學",
      philosophy: "哲學",
      literature: "文學",
      linguistics: "語言學",
      medicine: "醫學",
      nursing: "護理學",
      pharmacy: "藥學",
      business: "商學",
      management: "管理學",
      finance: "財務金融",
      education: "教育學",
      arts: "藝術",
      design: "設計",
      law: "法律",
      architecture: "建築",
      agriculture: "農業",
      environmental_science: "環境科學",
      other: "其他",
    };

    const selectedFields = academicFields
      ? academicFields.map((f: string) => fieldLabels[f] || f).join("、")
      : "未選擇";

    await resend.emails.send({
      from: "Know Graph Lab <onboarding@resend.dev>",
      to: email,
      subject: "歡迎加入 Know Graph Lab - 請驗證你的 Email",
      html: `
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset="utf-8">
            <style>
              body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
              .container { max-width: 600px; margin: 0 auto; padding: 20px; }
              .header { text-align: center; padding: 20px 0; background: linear-gradient(135deg, #2563eb, #10b981); color: white; border-radius: 10px 10px 0 0; }
              .content { background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }
              .button { display: inline-block; padding: 12px 30px; background: #2563eb; color: white; text-decoration: none; border-radius: 6px; font-weight: bold; }
              .info-box { background: white; padding: 15px; border-radius: 6px; margin: 20px 0; border-left: 4px solid #2563eb; }
              .footer { text-align: center; margin-top: 30px; color: #666; font-size: 14px; }
            </style>
          </head>
          <body>
            <div class="container">
              <div class="header">
                <h1 style="margin: 0;">歡迎加入 Know Graph Lab！</h1>
              </div>
              
              <div class="content">
                <p>親愛的 <strong>${displayName}</strong>，</p>
                
                <p>感謝你註冊 Know Graph Lab！我們很高興你加入我們的知識視覺化社群。</p>
                
                <div class="info-box">
                  <h3 style="margin-top: 0;">你的個人資料</h3>
                  <p style="margin: 5px 0;"><strong>姓名：</strong>${displayName}</p>
                  <p style="margin: 5px 0;"><strong>Email：</strong>${email}</p>
                  <p style="margin: 5px 0;"><strong>學術領域：</strong>${selectedFields}</p>
                  ${ageRange ? `<p style="margin: 5px 0;"><strong>年齡層：</strong>${ageRange}</p>` : ""}
                </div>
                
                <p>請點擊下方按鈕驗證你的 Email 地址：</p>
                
                <p style="text-align: center; margin: 30px 0;">
                  <a href="${verificationUrl}" class="button">驗證 Email</a>
                </p>
                
                <p style="font-size: 14px; color: #666;">
                  或複製此連結到瀏覽器：<br>
                  <a href="${verificationUrl}" style="color: #2563eb;">${verificationUrl}</a>
                </p>
                
                <p style="font-size: 14px; color: #666; margin-top: 20px; padding: 10px; background: #fff3cd; border-radius: 4px;">
                  ⏱️ 此驗證連結將在 24 小時後失效。
                </p>
              </div>
              
              <div class="footer">
                <p>此郵件由 Know Graph Lab 自動發送，請勿直接回覆。</p>
                <p>如有任何問題，請訪問我們的 <a href="${config.public.appUrl}/guide" style="color: #2563eb;">使用指南</a></p>
              </div>
            </div>
          </body>
        </html>
      `,
    });

    return {
      success: true,
      message: "註冊成功！請檢查您的 Email 收件匣",
    };
  } catch (error: any) {
    console.error("Signup error:", error);
    throw createError({
      statusCode: 500,
      message: error.message || "註冊失敗",
    });
  }
});
