// PATCH /api/journal-articles/:id
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const id = getRouterParam(event, "id")!;
  const body = await readBody(event) as Record<string, unknown>;

  const allowed = ["title", "venue", "author", "publish_year", "issue_label"] as const;
  const patch: Record<string, unknown> = {};
  for (const k of allowed) {
    if (body[k] !== undefined) patch[k] = body[k];
  }
  if (!Object.keys(patch).length) throw createError({ statusCode: 400, message: "no valid fields" });

  const { error } = await supabase.from("journal_articles").update(patch).eq("id", id);
  if (error) throw createError({ statusCode: 500, message: error.message });
  return { success: true };
});
