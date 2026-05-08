// GET /api/works/projects/[slug] — public read single
// Returns content_json only when authed (notes is login-only)
export default defineEventHandler(async (event) => {
  const slug = getRouterParam(event, "slug");
  if (!slug) throw createError({ statusCode: 400, message: "slug required" });

  const supabase = getAdminClient();
  const { data, error } = await supabase
    .from("writing_projects")
    .select(
      "id, slug, title, subtitle, description, emoji, color, status, sort_order, content_json, updated_at"
    )
    .eq("slug", slug)
    .maybeSingle();

  if (error) throw createError({ statusCode: 500, message: error.message });
  if (!data) throw createError({ statusCode: 404, message: "project not found" });

  // Check auth — strip content_json for unauthed callers
  const config = useRuntimeConfig();
  const allowedEmail = config.public.allowedEmail as string | undefined;
  const token = getHeader(event, "authorization")?.replace("Bearer ", "");

  let isAdmin = false;
  if (token) {
    try {
      const { createClient } = await import("@supabase/supabase-js");
      const userClient = createClient(config.public.supabaseUrl, config.public.supabaseKey, {
        global: { headers: { Authorization: `Bearer ${token}` } },
      });
      const {
        data: { user },
      } = await userClient.auth.getUser();
      isAdmin = !!user && (!allowedEmail || user.email === allowedEmail);
    } catch {
      isAdmin = false;
    }
  }

  if (!isAdmin) {
    return { project: { ...data, content_json: null } };
  }
  return { project: data };
});
