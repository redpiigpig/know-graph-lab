/**
 * PUT /api/ebooks/:id/chunks/:index
 * Body: { content?: string; source_text?: string; chapter_path?: string }
 *
 * In-place edit of a single chunk's translated content / English source /
 * heading. The reader's ✏️ edit button posts here. Writes are:
 *   1. Rewrite the JSONL line on the local Drive (canonical store)
 *   2. Push the full JSONL to R2 (gzipped) so production / cold serve gets fresh data
 *   3. Update the matching ebook_chunks preview row in Supabase
 *   4. Invalidate the in-memory LRU (the localMtime change handles this on next load)
 *
 * Only the fields present in the body are touched; others are preserved
 * (page_numbers, footnotes, volume, etc.).
 *
 * Auth: requires logged-in user — these edits are book-level, not per-user.
 */
import { promises as fs } from "node:fs";
import path from "node:path";
import { exec } from "node:child_process";
import { promisify } from "node:util";

const execAsync = promisify(exec);

interface EditBody {
  content?: string;
  source_text?: string;
  chapter_path?: string;
}

export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const ebookId = getRouterParam(event, "id");
  const indexStr = getRouterParam(event, "index");
  if (!ebookId || !indexStr) {
    throw createError({ statusCode: 400, message: "ebook id + chunk index required" });
  }
  const chunkIdx = parseInt(indexStr, 10);
  if (!Number.isFinite(chunkIdx) || chunkIdx < 0) {
    throw createError({ statusCode: 400, message: "chunk index must be non-negative integer" });
  }

  const body = (await readBody(event)) as EditBody;
  if (
    body.content === undefined &&
    body.source_text === undefined &&
    body.chapter_path === undefined
  ) {
    throw createError({ statusCode: 400, message: "no editable field provided" });
  }

  const cfg = useRuntimeConfig();
  const chunksDir = cfg.ebookChunksDir as string;
  const jsonlPath = path.join(chunksDir, `${ebookId}.jsonl`);

  // Read JSONL
  let raw: string;
  try {
    raw = await fs.readFile(jsonlPath, "utf8");
  } catch (err: any) {
    throw createError({
      statusCode: 404,
      message: `JSONL not found at ${jsonlPath}: ${err.message}`,
    });
  }
  const lines = raw.split(/\r?\n/);
  // Trailing empty line from .split() — drop only for index-range check
  const dataLines = lines.filter(Boolean);
  if (chunkIdx >= dataLines.length) {
    throw createError({
      statusCode: 404,
      message: `chunk_index ${chunkIdx} out of range (have ${dataLines.length})`,
    });
  }

  // Locate the actual line index for this chunk in the FULL lines array
  // (preserves trailing newline + any blanks). The JSONL is one chunk per
  // non-empty line so we count those.
  let lineIdx = -1;
  let nonEmptyCount = -1;
  for (let i = 0; i < lines.length; i++) {
    if (lines[i]) {
      nonEmptyCount++;
      if (nonEmptyCount === chunkIdx) {
        lineIdx = i;
        break;
      }
    }
  }
  if (lineIdx < 0) {
    throw createError({ statusCode: 500, message: "chunk locate failed" });
  }

  let chunk: any;
  try {
    chunk = JSON.parse(lines[lineIdx]);
  } catch (err: any) {
    throw createError({ statusCode: 500, message: `chunk parse failed: ${err.message}` });
  }

  // Apply edits
  if (body.content !== undefined) chunk.content = body.content;
  if (body.source_text !== undefined) chunk.source_text = body.source_text;
  if (body.chapter_path !== undefined) chunk.chapter_path = body.chapter_path;
  chunk.edited_at = new Date().toISOString();

  lines[lineIdx] = JSON.stringify(chunk);
  await fs.writeFile(jsonlPath, lines.join("\n"), "utf8");

  // Update DB preview row (best-effort; failure shouldn't block the edit)
  try {
    const supabase = getAdminClient();
    await supabase
      .from("ebook_chunks")
      .update({
        content: (chunk.content || "").slice(0, 200),
        char_count: (chunk.content || "").length,
        chapter_path: chunk.chapter_path,
      })
      .eq("ebook_id", ebookId)
      .eq("chunk_index", chunkIdx);
  } catch (err: any) {
    console.warn(`[chunks.put] preview update failed: ${err.message ?? err}`);
  }

  // Push JSONL to R2 in the background — don't block the response.
  // We shell out to standardize_ebook's push_to_r2 via a tiny Python
  // one-liner so we reuse the existing gzip + Content-Encoding logic.
  (async () => {
    try {
      const py = `import sys, pathlib; sys.path.insert(0, r'${process.cwd().replace(/\\/g, "\\\\")}\\scripts'); import standardize_ebook as se; se.push_to_r2('${ebookId}', pathlib.Path(r'${jsonlPath.replace(/\\/g, "\\\\")}'))`;
      await execAsync(`python -c "${py.replace(/"/g, '\\"')}"`, {
        cwd: process.cwd(),
        timeout: 60_000,
      });
    } catch (err: any) {
      console.warn(`[chunks.put] R2 push failed (non-fatal): ${err.message ?? err}`);
    }
  })();

  return {
    ok: true,
    chunk_index: chunkIdx,
    edited_at: chunk.edited_at,
  };
});
