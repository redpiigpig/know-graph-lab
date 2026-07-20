/**
 * Stream an ebook's ORIGINAL file (PDF/EPUB/MOBI…) straight from the Google
 * Drive mount (G:) to the browser. The public site runs on the user's own
 * machine where G: is mounted, so no upload / no R2 / no public Drive share is
 * needed — the server reads the file at `ebooks.file_path` and streams it.
 *
 *   GET /api/ebooks/{id}/original            → inline (view in browser)
 *   GET /api/ebooks/{id}/original?download=1 → attachment (download)
 *
 * Web-sourced books (gnostic / papal / apocrypha…) have no file_path → 404.
 * Auth-gated like the reader itself; the file_path comes from our own DB and is
 * asserted to live under the ebook Drive root before opening (no path traversal).
 */
import { createReadStream } from "node:fs";
import { stat } from "node:fs/promises";
import { resolve, sep, extname } from "node:path";

// Canonical Drive root for the library; only files under here may be served.
const DRIVE_ROOTS = [
  "G:\\我的雲端硬碟\\資料\\知識圖工作室\\電子圖書館",
  "G:/我的雲端硬碟/資料/知識圖工作室/電子圖書館",
];

const CONTENT_TYPE: Record<string, string> = {
  ".pdf": "application/pdf",
  ".epub": "application/epub+zip",
  ".mobi": "application/x-mobipocket-ebook",
  ".azw3": "application/vnd.amazon.ebook",
  ".azw": "application/vnd.amazon.ebook",
};

function sanitize(name: string): string {
  return name.replace(/[\\/:*?"<>|\n\r]+/g, "_").slice(0, 180);
}

export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const id = getRouterParam(event, "id");
  const supabase = getAdminClient();

  const { data: ebook, error } = await supabase
    .from("ebooks")
    .select("id, title, author, file_type, file_path")
    .eq("id", id!)
    .single();

  if (error || !ebook) {
    throw createError({ statusCode: 404, message: "找不到電子書" });
  }
  if (!ebook.file_path) {
    // Web-sourced transcription with no original file.
    throw createError({ statusCode: 404, message: "此書無原始檔案（網頁來源）" });
  }

  // Path-traversal guard: the stored path must resolve under the Drive root.
  const abs = resolve(ebook.file_path);
  const underRoot = DRIVE_ROOTS.some((root) => {
    const r = resolve(root);
    return abs === r || abs.startsWith(r + sep);
  });
  if (!underRoot) {
    throw createError({ statusCode: 403, message: "檔案路徑不在允許範圍" });
  }

  const ext = extname(abs).toLowerCase();
  let size: number;
  try {
    const st = await stat(abs);
    if (!st.isFile()) throw new Error("not a file");
    size = st.size;
  } catch {
    throw createError({ statusCode: 404, message: "原始檔案不存在或無法讀取（Drive 可能未掛載）" });
  }

  const q = getQuery(event);
  const wantDownload = q.download === "1" || q.download === "true";
  const dispType = wantDownload ? "attachment" : "inline";

  const author = (ebook.author || "").trim();
  const base = author ? `${author}，${ebook.title}` : ebook.title;
  const filename = sanitize(`${base}${ext}`);

  setHeader(event, "Content-Type", CONTENT_TYPE[ext] || "application/octet-stream");
  setHeader(event, "Content-Length", String(size));
  setHeader(event, "Cache-Control", "private, max-age=3600");
  setHeader(
    event,
    "Content-Disposition",
    `${dispType}; filename="ebook-${id}${ext}"; filename*=UTF-8''${encodeURIComponent(filename)}`
  );

  return sendStream(event, createReadStream(abs));
});
