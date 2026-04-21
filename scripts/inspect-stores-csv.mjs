import fs from "node:fs";
import path from "node:path";

const dir = path.join(process.cwd(), "stores");
const files = fs.readdirSync(dir).filter((f) => f.toLowerCase().endsWith(".csv"));

function preview(text) {
  return text.slice(0, 240).replace(/\r/g, "\\r").replace(/\n/g, "\\n\n");
}

for (const f of files) {
  const full = path.join(dir, f);
  const buf = fs.readFileSync(full);
  const utf8 = new TextDecoder("utf-8").decode(buf);
  const big5 = new TextDecoder("big5").decode(buf);
  const u16 = new TextDecoder("utf-16le").decode(buf);

  console.log(`\n=== ${f} (${buf.length} bytes) ===`);
  console.log("[utf8]", preview(utf8));
  console.log("[big5]", preview(big5));
  console.log("[utf16le]", preview(u16));
}
