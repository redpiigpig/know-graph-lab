// PATCH /api/concepts/:id — update + re-parse [[wiki links]] if body changed.
import { rebuildConceptLinks } from "../../utils/concept-links";

export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const id = getRouterParam(event, "id")!;
  const body = await readBody(event) as Record<string, unknown>;

  const allowed = ["name", "slug", "aliases", "summary", "body", "color"] as const;
  const patch: Record<string, unknown> = { updated_at: new Date().toISOString() };
  for (const k of allowed) if (body[k] !== undefined) patch[k] = body[k];

  const { error } = await supabase.from("concepts").update(patch).eq("id", id);
  if (error) throw createError({ statusCode: 500, message: error.message });

  let linkInfo: any = null;
  if (typeof body.body === "string") {
    linkInfo = await rebuildConceptLinks(supabase, id, body.body);
  }

  return { success: true, links: linkInfo };
});
