export default defineNuxtConfig({
  devtools: { enabled: true },

  modules: ["@nuxtjs/tailwindcss", "@nuxtjs/supabase", "@vueuse/nuxt", "@pinia/nuxt"],

  supabase: {
    redirect: false, // 我們自己處理重導向
  },

  runtimeConfig: {
    // 私有配置（只在後端可用）
    encryptionKey: process.env.ENCRYPTION_KEY,
    supabaseServiceRoleKey: process.env.SUPABASE_SERVICE_ROLE_KEY,
    resendApiKey: process.env.RESEND_API_KEY,
    r2AccessKey: process.env.R2_ACCESS_KEY,
    r2SecretKey: process.env.R2_SECRET_KEY,
    r2Endpoint: process.env.R2_ENDPOINT,
    r2Bucket: process.env.R2_BUCKET,
    ebookChunksDir: process.env.EBOOK_CHUNKS_DIR,
    photosRoot: process.env.PHOTOS_ROOT || "G:/我的雲端硬碟/資料/儲存資料夾/辰瑋相片",
    // Gemini（4 把 key，輪替使用；語言教練、族譜解析等共用）
    geminiApiKey: process.env.Gemini_API_Key_1,
    geminiApiKeys: [
      process.env.Gemini_API_Key_1,
      process.env.Gemini_API_Key_2,
      process.env.Gemini_API_Key_3,
      process.env.Gemini_API_Key_4,
    ].filter(Boolean) as string[],
    // 語言教練模型：固定 ID gemini-2.5-flash 免費層每日僅 20 次、且被 OCR 自動化共用耗盡；
    // 改用 rolling alias `gemini-flash-latest`（2026-05-31 實測免費層可用，且配額桶與 OCR 用的固定 ID 分開）。
    // 升付費後可設 GEMINI_MODEL=gemini-2.5-flash、GEMINI_GRADE_MODEL=gemini-2.5-pro 免改碼升級。
    geminiModel: process.env.GEMINI_MODEL || "gemini-flash-latest",
    geminiGradeModel: process.env.GEMINI_GRADE_MODEL || "gemini-flash-latest",
    // 語言教練主引擎：NVIDIA NIM（無限量），Gemini 降為 fallback。
    // 2026-06-03 改用 NVIDIA 為主：成本 0、無每日配額牆。fileData（YouTube）NVIDIA 不支援 → 自動走 Gemini。
    // 模型：qwen3-next-80b-a3b-instruct（繁中佳、支援 JSON、穩定可用）。
    //   ⚠️ 不用 deepseek-v4-flash：該模型在 NVIDIA 免費層長期 429，互動式教練不可靠
    //   （deepseek 只適合翻譯腳本那種可退避重試的批次場景）。
    nvidiaApiKeys: [
      process.env.NVIDIA_API_Key_1,
      process.env.NVIDIA_API_Key_2,
      process.env.NVIDIA_API_Key_3,
    ].filter(Boolean) as string[],
    nvidiaModel: process.env.NVIDIA_MODEL || "qwen/qwen3-next-80b-a3b-instruct",
    // 語言教練專用雙 key：先用免費，免費額度用完 → 前端確認後改用付費。
    // 兩支都還沒填時，免費層 fallback 用既有的 Gemini_API_Key_* 共用池。
    geminiCoachFreeKey: process.env.GEMINI_COACH_FREE_KEY,
    geminiCoachPaidKey: process.env.GEMINI_COACH_PAID_KEY,
    // 付費 key 每月成本上限（NT$）；本月付費估計成本超過就自動退回免費。改上限：設此 env。
    geminiPaidMonthlyCapTwd: Number(process.env.GEMINI_PAID_MONTHLY_CAP_TWD || 500),

    // 公開配置（前端和後端都可用）
    public: {
      supabaseUrl: process.env.SUPABASE_URL,
      supabaseKey: process.env.SUPABASE_KEY,
      appUrl: process.env.APP_URL || "http://localhost:3000",
      allowedEmail: process.env.ALLOWED_EMAIL || "redpiigpig@gmail.com",
    },
  },

  app: {
    head: {
      title: "Workspace",
      meta: [
        { charset: "utf-8" },
        { name: "viewport", content: "width=device-width, initial-scale=1" },
        // 私人網站：不開放搜尋引擎索引、不對外提示內容
        { name: "robots", content: "noindex, nofollow, noarchive, nosnippet" },
        { name: "googlebot", content: "noindex, nofollow" },
      ],
      link: [{ rel: "icon", type: "image/jpeg", href: "/logo_image.jpg" }],
    },
  },

  css: [
    "~/assets/css/main.css",
  ],

  compatibilityDate: "2024-07-24",
});
