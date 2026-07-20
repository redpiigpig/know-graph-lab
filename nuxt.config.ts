// 線上 AI key 解析（語言教練、族譜解析、YouTube 沉浸共用）。
// 政策：線上（Zeabur）只設 *_OLINE_ONLY；本機 dev 刻意不放 OLINE。
// 為了讓本機 dev 也能測 coach，OLINE 不存在時才 fallback 到既有 _1..4 共享池
// （Zeabur 沒設 _1..4，所以線上仍只會讀 OLINE，線上/線下額度分離不受影響）。
const onlineGeminiKey =
  process.env.Gemini_API_Key_OLINE_ONLY || process.env.GEMINI_API_KEY_OLINE_ONLY;
const onlineNvidiaKey =
  process.env.NVIDIA_API_Key_OLINE_ONLY || process.env.NVIDIA_API_KEY_OLINE_ONLY;
const geminiPool = [1, 2, 3, 4]
  .map((i) => process.env[`Gemini_API_Key_${i}`])
  .filter(Boolean) as string[];
const nvidiaPool = [1, 2, 3, 4]
  .map((i) => process.env[`NVIDIA_API_Key_${i}`])
  .filter(Boolean) as string[];
// 線上有 OLINE 用 OLINE；本機（無 OLINE）才退到 _1..4 池。
const geminiKeys = onlineGeminiKey ? [onlineGeminiKey] : geminiPool;
const nvidiaKeys = onlineNvidiaKey ? [onlineNvidiaKey] : nvidiaPool;

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
    // 聖經經文 gz JSON（bible_verses 已搬出 DB — 2026-07-08 超量救援）；
    // dev 直讀 Drive，production 由 server/utils/bible-verses.ts fallback 到 R2。
    bibleVersesDir: process.env.BIBLE_VERSES_DIR || "G:/我的雲端硬碟/資料/聖經/_verses",
    photosRoot: process.env.PHOTOS_ROOT || "G:/我的雲端硬碟/資料/知識圖工作室/照片/辰瑋相片",
    // 照片來源後端：'local'＝直讀本機 G: 槽（dev 預設）；'r2'＝雲端從 R2 讀 index + 縮圖
    // （Zeabur 設 PHOTO_BACKEND=r2，原檔仍留 Drive，只有縮圖上 R2）。見 sync_photos_to_r2.mjs。
    photoBackend: process.env.PHOTO_BACKEND || "local",
    // Gemini key：線上讀 OLINE，本機 dev 退到 _1..4 池（見檔首 geminiKeys 解析）。
    geminiApiKey: geminiKeys[0],
    geminiApiKeys: geminiKeys,
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
    // 同 Gemini 政策：線上只讀 NVIDIA_API_Key_OLINE_ONLY（僅 Zeabur 設定）；
    // _1..4 留給線下批次腳本（含三支用前綴比對撈 key 的 dialogue_*.py）。
    nvidiaApiKeys: nvidiaKeys,
    nvidiaModel: process.env.NVIDIA_MODEL || "qwen/qwen3-next-80b-a3b-instruct",
    // NVIDIA 呼叫逾時（ms）：超時就 abort → 落到 Gemini fallback，避免 Zeabur gateway 先回 502。
    nvidiaTimeoutMs: Number(process.env.NVIDIA_TIMEOUT_MS || 14000),
    // 語言教練專用雙 key：先用免費，免費額度用完 → 前端確認後改用付費。
    // 兩支都還沒填時，免費層 fallback 用既有的 Gemini_API_Key_* 共用池。
    geminiCoachFreeKey: process.env.GEMINI_COACH_FREE_KEY,
    geminiCoachPaidKey: process.env.GEMINI_COACH_PAID_KEY,
    // 付費 key 每月成本上限（NT$）；本月付費估計成本超過就自動退回免費。改上限：設此 env。
    geminiPaidMonthlyCapTwd: Number(process.env.GEMINI_PAID_MONTHLY_CAP_TWD || 500),
    // 自架 LanguageTool 服務 URL（寫作文法檢查，零 AI、規則式）。空＝功能不啟用。
    // Zeabur 加一個 erikvl87/languagetool Docker 服務，把它的內網 URL 填這裡。
    languageToolUrl: process.env.LANGUAGETOOL_URL || "",

    // 公開配置（前端和後端都可用）
    public: {
      supabaseUrl: process.env.SUPABASE_URL,
      supabaseKey: process.env.SUPABASE_KEY,
      appUrl: process.env.APP_URL || "http://localhost:3000",
      allowedEmail: process.env.ALLOWED_EMAIL || "redpiigpig@gmail.com",
      // 前端用：r2 後端時影片無法播（原檔不在 R2），改顯示占位。
      photoBackend: process.env.PHOTO_BACKEND || "local",
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
