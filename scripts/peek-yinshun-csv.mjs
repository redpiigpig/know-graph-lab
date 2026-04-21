import fs from "node:fs";
import path from "node:path";

const dir = path.join(process.cwd(), "stores");
const skip = new Set(["中年之路.csv", "反穀.csv", "儀式的科學.csv"]);
const name = fs
  .readdirSync(dir)
  .filter((f) => f.endsWith(".csv") && !skip.has(f))
  .find((f) => {
    const b = fs.readFileSync(path.join(dir, f));
    const head = new TextDecoder("big5").decode(b.slice(0, 400));
    return head.includes("人間佛教") || head.includes("印順");
  });
if (!name) {
  console.error("CSV not found");
  process.exit(1);
}
const buf = fs.readFileSync(path.join(dir, name));
const t = new TextDecoder("big5").decode(buf);

function parseCsv(text) {
  const out = [];
  let row = [];
  let cur = "";
  let q = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (c === '"') {
      if (q && text[i + 1] === '"') {
        cur += '"';
        i++;
      } else q = !q;
    } else if (c === "," && !q) {
      row.push(cur);
      cur = "";
    } else if ((c === "\n" || c === "\r") && !q) {
      if (c === "\r" && text[i + 1] === "\n") i++;
      row.push(cur);
      cur = "";
      if (row.some((v) => v !== "")) out.push(row);
      row = [];
    } else cur += c;
  }
  if (cur.length || row.length) {
    row.push(cur);
    if (row.some((v) => v !== "")) out.push(row);
  }
  return out;
}

const rows = parseCsv(t);
console.log("file:", name, "rows:", rows.length);
for (let i = 0; i < 20; i++) {
  const r = rows[i];
  const title = (r[0] || "").slice(0, 50);
  const last = (r[r.length - 1] || "").replace(/\s+/g, " ").slice(-80);
  console.log(i, "cols", r?.length, "title:", title, "| tail:", last);
}
