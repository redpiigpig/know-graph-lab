/**
 * Stream the thesis PDF from R2 to the browser.
 *
 * Why server proxy: R2 bucket has no public CDN domain configured, so we can't
 * just embed `https://r2.../pong-writings/{slug}.pdf` directly in the reader.
 * Server fetches with credentials and streams the body back. Browser caches
 * via Cache-Control.
 */
import { GetObjectCommand, S3Client } from "@aws-sdk/client-s3";
import { createClient } from "@supabase/supabase-js";

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
  const id = getRouterParam(event, "id");
  const cfg = useRuntimeConfig();
  const supabase = createClient(
    cfg.public.supabaseUrl as string,
    cfg.supabaseServiceRoleKey as string
  );

  const { data, error } = await supabase
    .from("pong_writings")
    .select("pdf_r2_key, title, is_published")
    .eq("id", id)
    .single();

  if (error || !data) {
    throw createError({ statusCode: 404, message: "找不到此篇文章" });
  }
  if (!data.is_published) {
    throw createError({ statusCode: 404, message: "此篇文章未公開" });
  }
  if (!data.pdf_r2_key) {
    throw createError({ statusCode: 404, message: "本篇文章沒有 PDF" });
  }

  const r2 = getR2();
  let res;
  try {
    res = await r2.send(
      new GetObjectCommand({
        Bucket: cfg.r2Bucket as string,
        Key: data.pdf_r2_key,
      })
    );
  } catch (err: any) {
    if (err.name === "NoSuchKey" || err.$metadata?.httpStatusCode === 404) {
      throw createError({ statusCode: 404, message: "PDF 不存在於儲存區" });
    }
    throw createError({ statusCode: 502, message: "R2 fetch failed: " + (err.message || err) });
  }

  const body = res.Body;
  if (!body) {
    throw createError({ statusCode: 502, message: "R2 returned empty body" });
  }

  setHeader(event, "Content-Type", "application/pdf");
  setHeader(event, "Cache-Control", "public, max-age=86400");
  setHeader(event, "Content-Disposition", `inline; filename="thesis-${id}.pdf"`);
  if (res.ContentLength) {
    setHeader(event, "Content-Length", String(res.ContentLength));
  }

  return sendStream(event, body as any);
});
