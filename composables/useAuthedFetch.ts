// Wraps $fetch with Authorization: Bearer <access_token>
export async function authedFetch<T = unknown>(
  url: string,
  opts: Record<string, unknown> = {}
): Promise<T> {
  const supabase = useSupabaseClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();
  const headers = {
    ...((opts.headers as Record<string, string>) ?? {}),
    Authorization: `Bearer ${session?.access_token ?? ""}`,
  };
  return $fetch<T>(url, { ...opts, headers });
}
