// GET /api/tripitaka/work?id=T0262&juan=1
//
// 一部經的閱讀資料：目錄樹 + 指定卷的段落 + 該卷的漢梵巴詞條。
// 大般若經一部近 190 萬字，整部一次送會拖垮瀏覽器 —— 一律按卷取。
import {
  isValidWorkId,
  loadSegments,
  loadToc,
  loadTerms,
  loadEquivalents,
  loadOriginals,
} from "~/server/utils/tripitaka";

export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const q = getQuery(event);
  const id = String(q.id || "").trim();
  if (!isValidWorkId(id)) {
    throw createError({ statusCode: 400, message: "invalid work id" });
  }

  const supabase = getAdminClient();
  const { data: work, error } = await supabase
    .from("tripitaka_works")
    .select("*")
    .eq("id", id)
    .maybeSingle();
  if (error) throw createError({ statusCode: 500, message: error.message });
  if (!work) throw createError({ statusCode: 404, message: "work not found" });

  const [tocFile, allSegs, terms, originals] = await Promise.all([
    loadToc(id),
    loadSegments(id),
    loadTerms(id),
    loadOriginals(id),
  ]);
  if (!allSegs) {
    // 目錄有這部經、正文檔卻不在 —— 是資料缺漏，不可當成空經悄悄呈現
    throw createError({
      statusCode: 503,
      message: `《${work.title_zh}》正文尚未上架（${id}.jsonl 不在 Drive 也不在 R2）`,
    });
  }

  const juans = [...new Set(allSegs.map((s) => s.juan).filter(Boolean))] as number[];
  const juan = q.juan === "all" ? null : Number(q.juan) || juans[0] || null;
  const segments = juan == null ? allSegs : allSegs.filter((s) => s.juan === juan);

  // 詞條只送這一卷用得到的（長阿含 402 條，全送也還好；密教部可上千）
  const segIds = new Set(segments.map((s) => s.seg));
  const juanTerms = terms.filter((t) => t.seg && segIds.has(t.seg));

  // 平行經目（巴／梵／藏／中期印度語）。DB 尚未建表時退回空陣列，
  // 讓漢文照樣讀得到 —— 對照缺席不該讓整部經打不開。
  let parallels: any[] = [];
  try {
    const { data } = await supabase
      .from("tripitaka_parallels")
      .select("seg,lang,ref,src,note")
      .eq("work_id", id)
      .limit(5000);
    parallels = (data ?? []).filter((p: any) => !p.seg || segIds.has(p.seg));
  } catch {
    parallels = [];
  }

  // 原典全文只送本卷用得到的：雜阿含整部的巴利原文有 7.7 MB，
  // 一次全送會讓 reader 卡死
  const juanOriginals: Record<string, any[]> = {};
  for (const [seg, items] of Object.entries(originals)) {
    if (segIds.has(seg)) juanOriginals[seg] = items;
  }

  return {
    work,
    toc: tocFile?.toc ?? [],
    originals: juanOriginals,
    original_total: Object.keys(originals).length,
    juans,
    juan,
    segments,
    terms: juanTerms,
    parallels,
    term_total: terms.length,
    equiv_total: (await loadEquivalents(id)).length,
    seg_total: allSegs.length,
  };
});
