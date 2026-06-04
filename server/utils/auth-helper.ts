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

export async function requireAdmin(event: Parameters<typeof defineEventHandler>[0]) {
  const user = await requireAuth(event);
  const config = useRuntimeConfig();
  const allowedEmail = config.public.allowedEmail as string | undefined;
  if (allowedEmail && user.email !== allowedEmail) {
    throw createError({ statusCode: 403, message: "Forbidden" });
  }
  return user;
}

// Soft admin check — never throws. Returns true only for the allowed account.
// Use when an endpoint should degrade gracefully for unauthed callers (e.g.
// strip private content) instead of returning 401.
export async function getIsAdmin(event: Parameters<typeof defineEventHandler>[0]) {
  const config = useRuntimeConfig();
  const token = getHeader(event, "authorization")?.replace("Bearer ", "");
  if (!token) return false;
  try {
    const userClient = createClient(config.public.supabaseUrl, config.public.supabaseKey, {
      global: { headers: { Authorization: `Bearer ${token}` } },
    });
    const {
      data: { user },
    } = await userClient.auth.getUser();
    const allowedEmail = config.public.allowedEmail as string | undefined;
    return !!user && (!allowedEmail || user.email === allowedEmail);
  } catch {
    return false;
  }
}

export function getAdminClient() {
  const config = useRuntimeConfig();
  return createClient(config.public.supabaseUrl, config.supabaseServiceRoleKey, {
    auth: { autoRefreshToken: false, persistSession: false },
  });
}
