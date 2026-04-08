export default defineEventHandler((event) => {
  const config = useRuntimeConfig();

  return {
    hasSupabaseUrl: !!config.public.supabaseUrl,
    hasSupabaseKey: !!config.public.supabaseKey,
    hasServiceRoleKey: !!config.supabaseServiceRoleKey,
    hasEncryptionKey: !!config.encryptionKey,
    hasResendKey: !!config.resendApiKey,
    appUrl: config.public.appUrl,

    // 顯示前幾個字元確認是否正確
    supabaseUrlPreview: config.public.supabaseUrl?.substring(0, 30) + "...",
    serviceRoleKeyPreview:
      config.supabaseServiceRoleKey?.substring(0, 20) + "...",
  };
});
