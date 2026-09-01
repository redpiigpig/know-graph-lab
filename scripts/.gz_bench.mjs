import { S3Client, GetObjectCommand, PutObjectCommand, DeleteObjectCommand } from "@aws-sdk/client-s3"
import { gzipSync, gunzipSync } from "node:zlib"
import fs from "node:fs"; import path from "node:path"
const env = Object.fromEntries(fs.readFileSync(path.join(process.cwd(), ".env"), "utf8")
  .split(/\r?\n/).filter(l => l && !l.startsWith("#"))
  .map(l => { const i = l.indexOf("="); return [l.slice(0, i), l.slice(i + 1).trim().replace(/^["']|["']$/g, "")] }))
const s3 = new S3Client({ region: "auto", endpoint: env.R2_ENDPOINT,
  credentials: { accessKeyId: env.R2_ACCESS_KEY, secretAccessKey: env.R2_SECRET_KEY } })
const B = env.R2_BUCKET, KEY = "pct-fulltext/tcnn/2011.jsonl", GZK = "corpus-index/_bench_2011.jsonl.gz"

const get = async (k) => {
  const t0 = performance.now()
  const r = await s3.send(new GetObjectCommand({ Bucket: B, Key: k }))
  const buf = Buffer.from(await r.Body.transformToByteArray())
  return { ms: performance.now() - t0, buf }
}
const parse = (txt) => { const t0 = performance.now()
  const n = txt.split("\n").filter(Boolean).map(l => JSON.parse(l)).length
  return { ms: performance.now() - t0, n } }

const a = await get(KEY)
const pa = parse(a.buf.toString("utf-8"))
console.log(`原樣   ：下載 ${a.buf.length/1048576|0}.${((a.buf.length/1048576)%1*10|0)} MB  ${a.ms.toFixed(0)} ms ｜ 解析 ${pa.ms.toFixed(0)} ms ｜ 合計 ${(a.ms+pa.ms).toFixed(0)} ms  (${pa.n} 列)`)

const gz = gzipSync(a.buf, { level: 6 })
await s3.send(new PutObjectCommand({ Bucket: B, Key: GZK, Body: gz }))
const b = await get(GZK)
const t1 = performance.now(); const un = gunzipSync(b.buf); const unz = performance.now() - t1
const pb = parse(un.toString("utf-8"))
console.log(`gzip   ：下載 ${(b.buf.length/1048576).toFixed(1)} MB  ${b.ms.toFixed(0)} ms ｜ 解壓 ${unz.toFixed(0)} ms ｜ 解析 ${pb.ms.toFixed(0)} ms ｜ 合計 ${(b.ms+unz+pb.ms).toFixed(0)} ms  (${pb.n} 列)`)
await s3.send(new DeleteObjectCommand({ Bucket: B, Key: GZK }))
console.log("（測試檔已刪除）")
