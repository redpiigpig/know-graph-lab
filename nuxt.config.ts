export default defineNuxtConfig({
  devtools: { enabled: true },

  modules: ["@nuxtjs/tailwindcss", "@nuxtjs/supabase"],

  supabase: {
    redirect: false, // 我們自己處理重導向
  },

  runtimeConfig: {
    // 私有配置（只在後端可用）
    encryptionKey: process.env.ENCRYPTION_KEY,
    supabaseServiceRoleKey: process.env.SUPABASE_SERVICE_ROLE_KEY,
    resendApiKey: process.env.RESEND_API_KEY,

    // 公開配置（前端和後端都可用）
    public: {
      supabaseUrl: process.env.SUPABASE_URL,
      supabaseKey: process.env.SUPABASE_KEY,
      appUrl: process.env.APP_URL || "http://localhost:3000",
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
      link: [{ rel: "icon", type: "image/x-icon", href: "/favicon.ico" }],
    },
  },

  css: ["~/assets/css/main.css"],

  compatibilityDate: "2024-07-24",
});
