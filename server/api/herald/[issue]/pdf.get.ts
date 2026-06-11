/**
 * Stream a 衛報 issue's original scanned PDF from R2 to the browser.
 *
 * 衛報 is served as static assets (public/herald/{issue}/) with no DB row, so the
 * R2 key is derived straight from the (validated, numeric) issue param:
 *   herald/issue-{issue}.pdf
 * Same private-bucket + server-proxy pattern as server/api/pong-writing/[id]/pdf.
 *
 *   GET /api/herald/55/pdf            → inline (view in browser)
 *   GET /api/herald/55/pdf?download=1 → attachment (download)
 */
import { GetObjectCommand, S3Client } from "@aws-sdk/client-s3";

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
  const raw = getRouterParam(event, "issue") || "";
  if (!/^\d+$/.test(raw)) {
    throw createError({ statusCode: 400, message: "期號格式錯誤" });
  }
  const issue = String(parseInt(raw, 10));
  const cfg = useRuntimeConfig();
  const key = `herald/issue-${issue}.pdf`;

  const r2 = getR2();
  let res;
  try {
    res = await r2.send(
      new GetObjectCommand({ Bucket: cfg.r2Bucket as string, Key: key })
    );
  } catch (err: any) {
    if (err.name === "NoSuchKey" || err.$metadata?.httpStatusCode === 404) {
      throw createError({ statusCode: 404, message: "此期 PDF 不存在於儲存區" });
    }
    throw createError({ statusCode: 502, message: "R2 fetch failed: " + (err.message || err) });
  }

  const body = res.Body;
  if (!body) {
    throw createError({ statusCode: 502, message: "R2 returned empty body" });
  }

  const q = getQuery(event);
  const wantDownload = q.download === "1" || q.download === "true";
  const dispType = wantDownload ? "attachment" : "inline";
  const filename = `衛報-第${issue}期.pdf`;

  setHeader(event, "Content-Type", "application/pdf");
  setHeader(event, "Cache-Control", "public, max-age=86400");
  setHeader(
    event,
    "Content-Disposition",
    `${dispType}; filename="herald-${issue}.pdf"; filename*=UTF-8''${encodeURIComponent(filename)}`
  );
  if (res.ContentLength) {
    setHeader(event, "Content-Length", String(res.ContentLength));
  }

  return sendStream(event, body as any);
});
