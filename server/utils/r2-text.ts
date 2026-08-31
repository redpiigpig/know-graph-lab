import { S3Client, GetObjectCommand } from '@aws-sdk/client-s3'
import { gunzipSync } from 'node:zlib'

/**
 * 從 R2 讀一份文字（JSONL／txt），自動處理 gzip。
 *
 * 為什麼壓：時間幾乎全花在 R2→伺服器的下載上，不是解析。實測教會公報 2011 整包
 *   原樣  下載 5.6 MB 1,829 ms ｜ 解析  5 ms          ｜ 合計 1,834 ms
 *   gzip  下載 2.5 MB   795 ms ｜ 解壓 42 ms ｜ 解析 17 ms ｜ 合計   855 ms
 * 所以壓縮同時省容量（43%）又快一倍以上，而瀏覽器端拿到的東西完全不變。
 *
 * 🚨 一定要「先試 .gz、沒有才退回原檔」。遷移是逐個語料進行的，中途 bucket 上
 *    兩種形式並存；只認一種的話，還沒轉的那些會整批讀不出來而頁面照樣顯示
 *    「尚未轉錄」——看起來很正常的壞掉。
 */
let client: S3Client | null = null

function s3(): S3Client {
  if (client) return client
  const config = useRuntimeConfig()
  client = new S3Client({
    region: 'auto',
    endpoint: config.r2Endpoint,
    credentials: { accessKeyId: config.r2AccessKey, secretAccessKey: config.r2SecretKey },
  })
  return client
}

async function fetchOne(key: string): Promise<Buffer | null> {
  try {
    const config = useRuntimeConfig()
    const r = await s3().send(new GetObjectCommand({ Bucket: config.r2Bucket, Key: key }))
    const bytes = await r.Body?.transformToByteArray()
    return bytes ? Buffer.from(bytes) : null
  } catch {
    return null
  }
}

/** 讀 `key`：先找 `key + '.gz'`，沒有再找 `key` 本身。都沒有回 null。 */
export async function r2Text(key: string): Promise<string | null> {
  const buf = (await fetchOne(`${key}.gz`)) ?? (await fetchOne(key))
  if (!buf) return null
  // 認魔術位元組而不是副檔名：R2 有時會替我們解掉 Content-Encoding，
  // 那時拿到的已經是明文，硬 gunzip 會炸。
  const isGzip = buf.length > 2 && buf[0] === 0x1f && buf[1] === 0x8b
  return (isGzip ? gunzipSync(buf) : buf).toString('utf-8')
}

/** JSONL → 陣列。單行壞掉不該讓整包讀不出來。 */
export function parseJsonl<T>(body: string): T[] {
  const out: T[] = []
  for (const line of body.split('\n')) {
    if (!line.trim()) continue
    try {
      out.push(JSON.parse(line) as T)
    } catch { /* 略過壞行 */ }
  }
  return out
}
