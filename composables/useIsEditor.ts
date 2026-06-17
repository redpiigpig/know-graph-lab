// Client-side editor gate. True only when the logged-in user is the site owner
// (runtimeConfig.public.allowedEmail, default redpiigpig@gmail.com). Mirrors the
// server-side requireAdmin / getIsAdmin check in server/utils/auth-helper.ts —
// the server is the real lock; this just hides edit affordances for everyone else.
export function useIsEditor() {
  const user = useSupabaseUser();
  const config = useRuntimeConfig();
  const allowed = config.public.allowedEmail as string | undefined;
  return computed(
    () => !!user.value?.email && (!allowed || user.value.email === allowed)
  );
}
