/**
 * 把 R2 上既有的 photos/thumb/{key}_1600.webp 重壓成 _1024.webp（q65）。
 *   - 直接讀 R2 現成 webp 再改寫，不碰 G: 原檔（Drive 串流太慢）。
 *   - R2 對外流量免費；讀 Class B / 寫 Class A 都在免費額度內。
 *   - 純新增：不刪 _1600。確認站上換用 1024 後再另行清除。
 * 用法： node scripts/r2_shrink_photo_thumbs.mjs [--concurrency=12] [--limit=N]
 */
import { S3Client, GetObjectCommand, PutObjectCommand, HeadObjectCommand } from "@aws-sdk/client-s3";
import sharp from "sharp";
import fs from "node:fs";

const WIDTH = 1024, QUALITY = 65;
const arg = (n, d) => { const m = process.argv.find(a => a.startsWith(`--${n}=`)); return m ? Number(m.split("=")[1]) : d; };
const CONC = arg("concurrency", 12);
const LIMIT = arg("limit", Infinity);

const env = Object.fromEntries(fs.readFileSync(".env", "utf8").split(/\r?\n/)
  .filter(l => l.includes("=") && !l.startsWith("#"))
  .map(l => { const i = l.indexOf("="); return [l.slice(0, i).trim(), l.slice(i + 1).trim().replace(/^["']|["']$/g, "")]; }));
const client = new S3Client({ region: "auto", endpoint: env.R2_ENDPOINT, maxAttempts: 5,
  credentials: { accessKeyId: env.R2_ACCESS_KEY, secretAccessKey: env.R2_SECRET_KEY } });
const B = env.R2_BUCKET;

const keys = JSON.parse(fs.readFileSync("C:/tmp/r2audit/live_1600.json", "utf8")).slice(0, LIMIT);
const STATE = "C:/tmp/r2audit/shrink_done.json";
const done = new Set(fs.existsSync(STATE) ? JSON.parse(fs.readFileSync(STATE, "utf8")) : []);
const todo = keys.filter(k => !done.has(k));
console.log(`待處理 ${todo.length.toLocaleString()} / 全部 ${keys.length.toLocaleString()}（已完成 ${done.size.toLocaleString()}）`);

let i = 0, ok = 0, skip = 0, fail = 0, inBytes = 0, outBytes = 0;
const t0 = Date.now();

async function worker() {
  while (i < todo.length) {
    const key = todo[i++];
    const dst = key.replace(/_1600\.webp$/, `_${WIDTH}.webp`);
    try {
      try { await client.send(new HeadObjectCommand({ Bucket: B, Key: dst })); done.add(key); skip++; continue; } catch {}
      const r = await client.send(new GetObjectCommand({ Bucket: B, Key: key }));
      const buf = Buffer.from(await r.Body.transformToByteArray());
      const out = await sharp(buf).resize(WIDTH, null, { fit: "inside", withoutEnlargement: true })
        .webp({ quality: QUALITY, effort: 5 }).toBuffer();
      await client.send(new PutObjectCommand({ Bucket: B, Key: dst, Body: out, ContentType: "image/webp" }));
      inBytes += buf.length; outBytes += out.length; ok++; done.add(key);
    } catch (e) { fail++; console.error(`✗ ${key}: ${e.name ?? e}`); }
    const n = ok + skip + fail;
    if (n % 500 === 0) {
      fs.writeFileSync(STATE, JSON.stringify([...done]));
      const rate = n / ((Date.now() - t0) / 1000);
      const eta = Math.round((todo.length - n) / Math.max(rate, .01) / 60);
      console.log(`${n.toLocaleString()}/${todo.length.toLocaleString()}  ok=${ok} skip=${skip} fail=${fail}  ` +
        `${(inBytes / 1e9).toFixed(2)}→${(outBytes / 1e9).toFixed(2)} GB  ${rate.toFixed(1)}/s  ETA ${eta}m`);
    }
  }
}
await Promise.all(Array.from({ length: CONC }, worker));
fs.writeFileSync(STATE, JSON.stringify([...done]));
console.log(`\n完成 ok=${ok} skip=${skip} fail=${fail}`);
console.log(`本次 ${(inBytes / 1e9).toFixed(2)} GB → ${(outBytes / 1e9).toFixed(2)} GB` +
  (inBytes ? `（${(outBytes / inBytes * 100).toFixed(0)}%）` : ""));
