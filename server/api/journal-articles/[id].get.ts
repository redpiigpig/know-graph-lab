// GET /api/journal-articles/:id — single source + excerpts (library-style payload)
import { journalArticleMergeKey } from "../../utils/journal-merge";

export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const id = getRouterParam(event, "id");

  const { data: ja, error: jaErr } = await supabase
    .from("journal_articles")
    .select("id, title, venue, author, publish_year, issue_label, created_at")
    .eq("id", id!)
    .single();

  if (jaErr || !ja) throw createError({ statusCode: 404, message: "找不到此篇目" });

  const { data: allJa, error: allErr } = await supabase
    .from("journal_articles")
    .select("id, title, venue, author, issue_label");

  if (allErr) throw createError({ statusCode: 500, message: allErr.message });

  const mergeKey = journalArticleMergeKey(ja);
  const clusterIds = (allJa ?? [])
    .filter((row) => journalArticleMergeKey(row) === mergeKey)
    .map((row) => row.id);

  const { data: excerpts, error: exErr } = await supabase
    .from("excerpts")
    .select(`
        id, title, content, chapter, page_number, created_at,
        excerpt_book_projects(
          book_projects(id, name, type)
        )
      `)
    .in("journal_article_id", clusterIds)
    .order("created_at");

  if (exErr) throw createError({ statusCode: 500, message: exErr.message });

  const enriched = (excerpts ?? []).map((e: any) => ({
    id: e.id,
    title: e.title,
    content: e.content,
    chapter: e.chapter,
    chapterName: "",
    page_number: e.page_number,
    created_at: e.created_at,
    projects: (e.excerpt_book_projects ?? []).map((ebp: any) => ebp.book_projects).filter(Boolean),
  }));

  return { ...ja, excerpts: enriched, chapterNameMap: {} };
});
