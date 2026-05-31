export default defineNuxtRouteMiddleware((to) => {
  const user = useSupabaseUser();
  const config = useRuntimeConfig();
  const allowedEmail = config.public.allowedEmail as string | undefined;

  // 未登入 → 去登入頁
  if (!user.value) {
    return navigateTo("/login");
  }

  // email 已知且不符合白名單 → 這是站長專屬的 lab 工具，非站長導去語言教練（不登出，保留其 session）
  // 注意：email 可能尚未載入（undefined），此時跳過檢查避免誤踢
  if (allowedEmail && user.value.email && user.value.email !== allowedEmail) {
    return navigateTo("/coach");
  }
});
