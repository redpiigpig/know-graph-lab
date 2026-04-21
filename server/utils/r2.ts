/**
 * Cloudflare R2 storage utility (S3-compatible)
 *
 * Folder structure:
 *   ebooks/epub/{bookId}.epub      — EPUB 原檔
 *   ebooks/pdf/{bookId}.pdf        — PDF 原檔
 *   pages/{bookId}/{pageNum}.jpg   — 解析用頁面圖片（OCR）
 *   covers/{bookId}.jpg            — 書封圖
 */

import {
  S3Client,
  PutObjectCommand,
  GetObjectCommand,
  DeleteObjectCommand,
  ListObjectsV2Command,
  HeadObjectCommand,
} from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

let _client: S3Client | null = null;

export function getR2Client(): S3Client {
  if (_client) return _client;
  const config = useRuntimeConfig();
  _client = new S3Client({
    region: "auto",
    endpoint: config.r2Endpoint as string,
    credentials: {
      accessKeyId: config.r2AccessKey as string,
      secretAccessKey: config.r2SecretKey as string,
    },
  });
  return _client;
}

function getBucket(): string {
  return useRuntimeConfig().r2Bucket as string;
}

/** Upload a file (Buffer or string) to R2 */
export async function r2Upload(
  key: string,
  body: Buffer | string,
  contentType: string
): Promise<string> {
  const client = getR2Client();
  await client.send(
    new PutObjectCommand({
      Bucket: getBucket(),
      Key: key,
      Body: body,
      ContentType: contentType,
    })
  );
  return key;
}

/** Generate a short-lived signed URL for downloading a private object */
export async function r2SignedUrl(key: string, expiresIn = 3600): Promise<string> {
  const client = getR2Client();
  return getSignedUrl(
    client,
    new GetObjectCommand({ Bucket: getBucket(), Key: key }),
    { expiresIn }
  );
}

/** Delete an object from R2 */
export async function r2Delete(key: string): Promise<void> {
  const client = getR2Client();
  await client.send(new DeleteObjectCommand({ Bucket: getBucket(), Key: key }));
}

/** Check if an object exists in R2 */
export async function r2Exists(key: string): Promise<boolean> {
  try {
    const client = getR2Client();
    await client.send(new HeadObjectCommand({ Bucket: getBucket(), Key: key }));
    return true;
  } catch {
    return false;
  }
}

/** List objects under a prefix */
export async function r2List(prefix: string): Promise<{ key: string; size: number }[]> {
  const client = getR2Client();
  const res = await client.send(
    new ListObjectsV2Command({ Bucket: getBucket(), Prefix: prefix })
  );
  return (res.Contents ?? []).map((o) => ({ key: o.Key!, size: o.Size ?? 0 }));
}

// ── Key helpers ──────────────────────────────────────────────────────────────

export const R2Keys = {
  epub: (bookId: string) => `ebooks/epub/${bookId}.epub`,
  pdf:  (bookId: string) => `ebooks/pdf/${bookId}.pdf`,
  cover:(bookId: string) => `covers/${bookId}.jpg`,
  page: (bookId: string, page: number) =>
    `pages/${bookId}/${String(page).padStart(4, "0")}.jpg`,
};
