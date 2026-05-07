/**
 * GET /api/pong/image/{key}
 * Proxy for R2 objects under the pong-archive/ prefix.
 * Only serves keys that start with "pong-archive/" to prevent arbitrary R2 access.
 */
import { GetObjectCommand } from "@aws-sdk/client-s3";
import { getR2Client } from "~/server/utils/r2";

export default defineEventHandler(async (event) => {
  const pathParam = event.context.params?.path ?? "";
  const key = `pong-archive/${pathParam}`;

  const client = getR2Client();
  const config = useRuntimeConfig();

  let obj: Awaited<ReturnType<typeof client.send>>;
  try {
    obj = await client.send(
      new GetObjectCommand({ Bucket: config.r2Bucket as string, Key: key })
    );
  } catch {
    throw createError({ statusCode: 404, message: "Image not found" });
  }

  const contentType = obj.ContentType ?? "image/jpeg";
  setHeader(event, "Content-Type", contentType);
  setHeader(event, "Cache-Control", "public, max-age=31536000, immutable");

  const stream = obj.Body as ReadableStream | NodeJS.ReadableStream;
  return sendStream(event, stream as any);
});
