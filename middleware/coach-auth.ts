// 語言教練專用 middleware：只要求「已登入」，不限站長白名單。
// 任何註冊用戶都能使用 /coach（各自獨立資料）；lab 工具仍用 owner-only 的 `auth`。
export default defineNuxtRouteMiddleware(() => {
  const user = useSupabaseUser();
  if (!user.value) {
    return navigateTo("/login");
  }
});
