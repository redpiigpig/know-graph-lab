export default defineNuxtRouteMiddleware((to, from) => {
  const user = useSupabaseUser();

  // 如果未登入，重導向到登入頁
  if (!user.value) {
    return navigateTo("/login");
  }
});
