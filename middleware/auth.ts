export default defineNuxtRouteMiddleware(async (to) => {
  const user = useSupabaseUser();
  const config = useRuntimeConfig();
  const allowedEmail = config.public.allowedEmail;

  // 未登入 → 去登入頁
  if (!user.value) {
    return navigateTo("/login");
  }

  // 已登入但 email 不符 → 登出並導回登入頁
  if (allowedEmail && user.value.email !== allowedEmail) {
    const supabase = useSupabaseClient();
    await supabase.auth.signOut();
    return navigateTo("/login");
  }
});
