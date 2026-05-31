// 語言教練 middleware（已鎖回站長專屬）：需登入且 email == allowedEmail。
// 非站長（即使有帳號）一律登出並導回登入頁。
export default defineNuxtRouteMiddleware(() => {
  const user = useSupabaseUser();
  const config = useRuntimeConfig();
  const allowedEmail = config.public.allowedEmail as string | undefined;

  if (!user.value) {
    return navigateTo("/login");
  }
  if (allowedEmail && user.value.email && user.value.email !== allowedEmail) {
    const supabase = useSupabaseClient();
    supabase.auth.signOut();
    return navigateTo("/login");
  }
});
