import { createClient } from "@supabase/supabase-js";

export async function requireAuth(event: Parameters<typeof defineEventHandler>[0]) {
  const config = useRuntimeConfig();
  const token = getHeader(event, "authorization")?.replace("Bearer ", "");

  if (!token) {
    throw createError({ statusCode: 401, message: "Unauthorized" });
  }

  const userClient = createClient(
    config.public.supabaseUrl,
    config.public.supabaseKey,
    { global: { headers: { Authorization: `Bearer ${token}` } } }
  );

  const {
    data: { user },
    error,
  } = await userClient.auth.getUser();

  if (error || !user) {
    throw createError({ statusCode: 401, message: "Invalid token" });
  }

  return user;
}

export function getAdminClient() {
  const config = useRuntimeConfig();
  return createClient(config.public.supabaseUrl, config.supabaseServiceRoleKey, {
    auth: { autoRefreshToken: false, persistSession: false },
  });
}
