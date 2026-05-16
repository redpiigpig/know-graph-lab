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
      title: "Know Graph Lab - 知識圖工作室",
      meta: [
        { charset: "utf-8" },
        { name: "viewport", content: "width=device-width, initial-scale=1" },
        {
          name: "description",
          content: "AI-powered academic visualization tool",
        },
      ],
      link: [{ rel: "icon", type: "image/jpeg", href: "/logo_image.jpg" }],
    },
  },

  css: [
    "~/assets/css/main.css",
  ],

  compatibilityDate: "2024-07-24",
});
