// Happy English 教學網站 middleware：獨立站台，限媽媽帳號（julia5868）與站長使用。
// 非允許名單者（即使有帳號）一律登出並導回登入頁。
const ALLOWED = ["julia5868@yahoo.com.tw", "redpiigpig@gmail.com"];

export default defineNuxtRouteMiddleware(() => {
  const user = useSupabaseUser();
  if (!user.value) {
    return navigateTo("/login?redirect=/english");
  }
  const email = (user.value.email || "").toLowerCase();
  if (!ALLOWED.includes(email)) {
    const supabase = useSupabaseClient();
    supabase.auth.signOut();
    return navigateTo("/login");
  }
});
