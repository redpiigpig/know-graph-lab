/**
 * 串流《佛光大辭典》的插圖與缺字圖。
 *
 *   GET /api/glossary/image/31129_1-p93.jpg
 *
 * 正本在 Drive `_corpus/fgs-dictionary/images/`，服務用副本在 R2
 * `fgs-dictionary/`（3,252 張、29.3 MB，由 scripts/fgs_dictionary_ingest.py --r2 上傳）。
 *
 * 先讀 R2，讀不到再回退到 Drive——正式站（Zeabur）讀不到 G:，本機開發則
 * 常常還沒上傳就想先看。兩邊都沒有才 404。
 *
 * ⚠️ `name` 一律只取 basename 並限定字元集：這個值會直接拼進 R2 key 與本機路徑，
 * 不擋就是一條目錄遍歷。
 */
import { GetObjectCommand, S3Client } from "@aws-sdk/client-s3";
import fs from "node:fs";
import path from "node:path";

const SAFE = /^[A-Za-z0-9][A-Za-z0-9._@~-]{0,95}\.(jpe?g|png|gif)$/i;
const PREFIX = "fgs-dictionary/";

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

function mime(name: string) {
  const e = name.toLowerCase().split(".").pop();
  return e === "png" ? "image/png" : e === "gif" ? "image/gif" : "image/jpeg";
}

export default defineEventHandler(async (event) => {
  const raw = getRouterParam(event, "name") || "";
  const name = path.basename(decodeURIComponent(raw));
  if (!SAFE.test(name)) {
    throw createError({ statusCode: 400, message: "圖檔名格式錯誤" });
  }

  // 這批圖不會變動，快取可以放長
  setHeader(event, "Content-Type", mime(name));
  setHeader(event, "Cache-Control", "public, max-age=31536000, immutable");

  const cfg = useRuntimeConfig();
  try {
    const res = await getR2().send(
      new GetObjectCommand({ Bucket: cfg.r2Bucket as string, Key: PREFIX + name }),
    );
    if (res.Body) {
      if (res.ContentLength) setHeader(event, "Content-Length", String(res.ContentLength));
      return sendStream(event, res.Body as any);
    }
  } catch {
    /* R2 沒有或沒設定：往下回退到 Drive */
  }

  const local = path.join(
    cfg.corpusRoot as string, "fgs-dictionary", "images", name,
  );
  try {
    const buf = fs.readFileSync(local);
    setHeader(event, "Content-Length", String(buf.length));
    return buf;
  } catch {
    throw createError({ statusCode: 404, message: "找不到這張圖" });
  }
});
