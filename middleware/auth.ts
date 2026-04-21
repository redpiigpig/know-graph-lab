export default defineNuxtRouteMiddleware((to) => {
  const user = useSupabaseUser();
  const config = useRuntimeConfig();
  const allowedEmail = config.public.allowedEmail as string | undefined;

  // 未登入 → 去登入頁
  if (!user.value) {
    return navigateTo("/login");
  }

  // email 已知且不符合白名單 → 登出
  // 注意：email 可能尚未載入（undefined），此時跳過檢查避免誤踢
  if (allowedEmail && user.value.email && user.value.email !== allowedEmail) {
    const supabase = useSupabaseClient();
    supabase.auth.signOut(); // 不 await，避免 async middleware 問題
    return navigateTo("/login");
  }
});
