// GET /api/transcription-progress
// 重轉錄佇列＋全集翻譯的統一進度（scripts/push_transcription_progress.py 定期彙整）。
// dev 直讀 c:/tmp/transcription_progress.json；production 讀 R2 progress/transcription.json。
import { promises as fs } from "node:fs";
import { GetObjectCommand, S3Client } from "@aws-sdk/client-s3";

let _r2: S3Client | null = null;
function getR2(): S3Client | null {
  const cfg = useRuntimeConfig();
  if (!cfg.r2Endpoint || !cfg.r2AccessKey || !cfg.r2SecretKey || !cfg.r2Bucket) return null;
  if (_r2) return _r2;
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
  await requireAuth(event);

  try {
    const raw = await fs.readFile("c:/tmp/transcription_progress.json", "utf8");
    return JSON.parse(raw);
  } catch { /* 非本機（Zeabur）→ R2 */ }

  const client = getR2();
  if (client) {
    try {
      const res = await client.send(new GetObjectCommand({
        Bucket: useRuntimeConfig().r2Bucket as string,
        Key: "progress/transcription.json",
      }));
      const buffers: Buffer[] = [];
      for await (const chunk of res.Body as AsyncIterable<Uint8Array>) {
        buffers.push(Buffer.from(chunk));
      }
      return JSON.parse(Buffer.concat(buffers).toString("utf8"));
    } catch { /* fallthrough */ }
  }
  throw createError({ statusCode: 404, message: "進度資料尚未產生（跑 scripts/push_transcription_progress.py）" });
});
