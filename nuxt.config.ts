export default defineNuxtConfig({
  devtools: { enabled: true },

  modules: [
    "@nuxtjs/tailwindcss",
    "@nuxtjs/supabase", // 新增
  ],

  supabase: {
    redirect: false, // 我們自己處理重導向
  },

  runtimeConfig: {
    encryptionKey: process.env.ENCRYPTION_KEY,

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
    },
  },

  css: ["~/assets/css/main.css"],

  compatibilityDate: "2024-07-24",
});
