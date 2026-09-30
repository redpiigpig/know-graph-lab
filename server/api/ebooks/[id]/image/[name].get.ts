/**
 * 串流電子圖書館書內插圖（EPUB 解析時丟掉、scripts/epub_figures.py 放回正文的那些）。
 *
 *   GET /api/ebooks/{ebook_id}/image/image00147.jpeg
 *
 * 服務用縮圖在 R2 `ebook-images/{ebook_id}/{檔名}`（restructure_chapters.py --apply 上傳）；
 * 正本仍是 Drive 上的 EPUB。<img> 帶不了 Authorization header，所以認登入 cookie。
 *
 * ⚠️ id 與檔名都會拼進 R2 key，一律限定字元集，不擋就是一條目錄遍歷。
 */
import { GetObjectCommand, S3Client } from "@aws-sdk/client-s3";
import path from "node:path";
import { serverSupabaseUser } from "#supabase/server";

const SAFE_NAME = /^[A-Za-z0-9][A-Za-z0-9._~-]{0,120}\.(jpe?g|png|gif|webp)$/i;
const SAFE_ID = /^[0-9a-f-]{36}$/i;

let _r2: S3Client | null = null;
function getR2() {
  if (_r2) return _r2;
  const cfg = useRuntimeConfig();
  _r2 = new S3Client({
    region: "auto",
    endpoint: cfg.r2Endpoint as string,
    credentials: {
      accessKeyId: cfg.r2AccessKey as string,
      secretAccessKey: cfg.r2SecretKey as string,
    },
  });
  return _r2;
}

export default defineEventHandler(async (event) => {
  const user = await serverSupabaseUser(event).catch(() => null);
  if (!user) throw createError({ statusCode: 401, message: "Unauthorized" });

  const id = getRouterParam(event, "id") || "";
  const name = path.basename(decodeURIComponent(getRouterParam(event, "name") || ""));
  if (!SAFE_ID.test(id) || !SAFE_NAME.test(name)) {
    throw createError({ statusCode: 400, message: "圖檔名格式錯誤" });
  }

  try {
    const res = await getR2().send(
      new GetObjectCommand({ Bucket: useRuntimeConfig().r2Bucket as string, Key: `ebook-images/${id}/${name}` }),
    );
    if (res.Body) {
      setHeader(event, "Content-Type", res.ContentType || "image/jpeg");
      setHeader(event, "Cache-Control", "private, max-age=31536000, immutable");
      if (res.ContentLength) setHeader(event, "Content-Length", String(res.ContentLength));
      return sendStream(event, res.Body as any);
    }
  } catch {
    /* fallthrough */
  }
  throw createError({ statusCode: 404, message: "找不到這張圖" });
});
