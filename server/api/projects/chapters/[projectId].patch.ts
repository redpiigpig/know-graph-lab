// PATCH /api/projects/chapters/:projectId  — update chapter name
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const projectId = getRouterParam(event, "projectId")!;
  const body = await readBody(event) as { chapter_code: string; chapter_name: string; sort_order?: number };

  if (!body.chapter_code) throw createError({ statusCode: 400, message: "chapter_code required" });

  const sortOrder =
    typeof body.sort_order === "number" && !Number.isNaN(body.sort_order)
      ? body.sort_order
      : body.chapter_code
        ? extractChapterNum(body.chapter_code)
        : 0;

  const { error } = await supabase.from("project_chapters").upsert(
    {
      project_id: projectId,
      chapter_code: body.chapter_code,
      chapter_name: body.chapter_name ?? "",
      sort_order: sortOrder,
    },
    { onConflict: "project_id,chapter_code" }
  );

  if (error) throw createError({ statusCode: 500, message: error.message });
  return { success: true };
});

function extractChapterNum(code: string): number {
  const nums: Record<string, number> = { 一:1,二:2,三:3,四:4,五:5,六:6,七:7,八:8,九:9,十:10,
    十一:11,十二:12,十三:13,十四:14,十五:15,十六:16,十七:17,十八:18,十九:19,二十:20,
    二十一:21,二十二:22,二十三:23,二十四:24,二十五:25,二十六:26,二十七:27,二十八:28,二十九:29,三十:30 };
  const m = code.match(/第(.+)章/);
  return m ? (nums[m[1]] ?? 0) : 0;
}
