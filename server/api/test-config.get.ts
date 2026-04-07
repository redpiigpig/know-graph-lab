export default defineEventHandler((event) => {
  const config = useRuntimeConfig();

  return {
    // 公開配置（可以顯示）
    public: {
      supabaseUrl: config.public.supabaseUrl,
      appUrl: config.public.appUrl,
    },
    // 私有配置（只顯示是否存在）
    private: {
      hasServiceRoleKey: !!config.supabaseServiceRoleKey,
      hasResendKey: !!config.resendApiKey,
      hasEncryptionKey: !!config.encryptionKey,
    },
  };
});
