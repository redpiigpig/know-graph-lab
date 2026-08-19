#!/usr/bin/env node

/**
 * Export the authorized RCUV 2010 verses needed by the full Hebrew reader.
 *
 * The command reads the official HKBS RCUV2 chapter payloads for only the
 * chapters referenced by the approved 25 chapters and 100 memory verses.
 * It also records the matching private R2 book-object hashes as an independent
 * provenance checkpoint.  The official payload is authoritative because the
 * older R2 ingestion omitted poetic continuation lines and combined ranges.
 */

import { createHash } from "node:crypto";
import { readFile, writeFile, mkdir } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { gunzipSync } from "node:zlib";
import { GetObjectCommand, S3Client } from "@aws-sdk/client-s3";
import { decodeHTML } from "entities";

const ROOT = resolve(import.meta.dirname, "..");
const DEFAULT_PLAN = resolve(
  ROOT,
  "output/source-cache/original-readers/hebrew-full/scripture-plan.json",
);
const DEFAULT_OUTPUT = resolve(
  ROOT,
  "output/source-cache/original-readers/hebrew-full/RCUV2010.json",
);

const OSIS_TO_R2 = {
  Gen: "gen", Exod: "exo", Lev: "lev", Num: "num", Deut: "deu",
  Josh: "jos", Judg: "jdg", Ruth: "rut", "1Sam": "1sa", "2Sam": "2sa",
  "1Kgs": "1ki", "2Kgs": "2ki", "1Chr": "1ch", "2Chr": "2ch",
  Ezra: "ezr", Neh: "neh", Esth: "est", Job: "job", Ps: "psa",
  Prov: "pro", Eccl: "ecc", Song: "sng", Isa: "isa", Jer: "jer",
  Lam: "lam", Ezek: "ezk", Dan: "dan", Hos: "hos", Joel: "jol",
  Amos: "amo", Obad: "oba", Jonah: "jon", Mic: "mic", Nah: "nam",
  Hab: "hab", Zeph: "zep", Hag: "hag", Zech: "zec", Mal: "mal",
};

const OSIS_TO_NAME = {
  Gen: "Genesis", Exod: "Exodus", Lev: "Leviticus", Num: "Numbers",
  Deut: "Deuteronomy", Josh: "Joshua", Judg: "Judges", Ruth: "Ruth",
  "1Sam": "I Samuel", "2Sam": "II Samuel", "1Kgs": "I Kings",
  "2Kgs": "II Kings", "1Chr": "I Chronicles", "2Chr": "II Chronicles",
  Ezra: "Ezra", Neh: "Nehemiah", Esth: "Esther", Job: "Job",
  Ps: "Psalms", Prov: "Proverbs", Eccl: "Ecclesiastes",
  Song: "Song of Solomon", Isa: "Isaiah", Jer: "Jeremiah",
  Lam: "Lamentations", Ezek: "Ezekiel", Dan: "Daniel", Hos: "Hosea",
  Joel: "Joel", Amos: "Amos", Obad: "Obadiah", Jonah: "Jonah",
  Mic: "Micah", Nah: "Nahum", Hab: "Habakkuk", Zeph: "Zephaniah",
  Hag: "Haggai", Zech: "Zechariah", Mal: "Malachi",
};

const OFFICIAL_BASE = "https://rcuv.hkbs.org.hk/bb/info/RCUV2";

function cleanOfficialHtml(value) {
  return decodeHTML(
    value
      .replace(/<sup\b[^>]*>[\s\S]*?<\/sup>/giu, "")
      .replace(/<br\s*\/?\s*>/giu, "")
      .replace(/<[^>]+>/gu, "")
      .replace(/\s+/gu, " ")
      .trim(),
  );
}

function htmlBlocks(html, tag) {
  const pattern = new RegExp(`<${tag}\\b[^>]*>([\\s\\S]*?)<\\/${tag}>`, "giu");
  return [...html.matchAll(pattern)]
    .map((match) => cleanOfficialHtml(match[1]))
    .filter(Boolean);
}

function parseOfficialChapter(body, osisBook, chapter) {
  const firstTag = body.indexOf("<");
  if (firstTag < 0) throw new Error(`official response has no HTML: ${osisBook}.${chapter}`);
  const metadata = body.slice(0, firstTag).trim();
  if (!metadata.startsWith("RCUV2|和合本2010")) {
    throw new Error(`unexpected official version metadata: ${osisBook}.${chapter}`);
  }
  const html = body.slice(firstTag);
  const markerPattern = /<b>(\d+)(?:\s*[-–]\s*(\d+))?<\/b>/giu;
  const markers = [...html.matchAll(markerPattern)];
  const verses = [];
  for (let index = 0; index < markers.length; index += 1) {
    const marker = markers[index];
    const verse = Number(marker[1]);
    const verseEnd = Number(marker[2] ?? marker[1]);
    const start = marker.index + marker[0].length;
    const end = index + 1 < markers.length ? markers[index + 1].index : html.length;
    const spanTexts = htmlBlocks(html.slice(start, end), "span");
    const text = spanTexts.join("").trim();
    if (!text) throw new Error(`empty official verse: ${osisBook}.${chapter}.${verse}`);
    verses.push({ verse, verseEnd, text });
  }
  if (!verses.length) throw new Error(`no official verses: ${osisBook}.${chapter}`);
  return {
    verses,
    superscriptions: htmlBlocks(html, "h6"),
    sectionHeadings: htmlBlocks(html, "h3"),
    metadata,
    responseSha256: createHash("sha256").update(body).digest("hex"),
  };
}

async function fetchOfficialChapter(osisBook, chapter) {
  const code = OSIS_TO_R2[osisBook].toUpperCase();
  const sourceUrl = `${OFFICIAL_BASE}/${code}/${chapter}/`;
  const response = await fetch(sourceUrl, {
    headers: { "user-agent": "private-authorized-original-reader/1.0" },
  });
  if (response.status === 403 || response.status === 429) {
    throw new Error(`official source stopped with HTTP ${response.status}: ${sourceUrl}`);
  }
  if (!response.ok) throw new Error(`official source HTTP ${response.status}: ${sourceUrl}`);
  const body = await response.text();
  return { sourceUrl, ...parseOfficialChapter(body, osisBook, chapter) };
}

function delay(milliseconds) {
  return new Promise((resolvePromise) => setTimeout(resolvePromise, milliseconds));
}

function parseArgs(argv) {
  const result = { plan: DEFAULT_PLAN, output: DEFAULT_OUTPUT, write: false };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--write") result.write = true;
    else if (arg === "--plan") result.plan = resolve(argv[++index]);
    else if (arg === "--output") result.output = resolve(argv[++index]);
    else throw new Error(`unknown argument: ${arg}`);
  }
  return result;
}

async function loadEnv() {
  const text = await readFile(resolve(ROOT, ".env"), "utf8");
  const values = {};
  for (const rawLine of text.split(/\r?\n/u)) {
    const line = rawLine.trim();
    if (!line || line.startsWith("#")) continue;
    const separator = line.indexOf("=");
    if (separator < 1) continue;
    const key = line.slice(0, separator).trim();
    let value = line.slice(separator + 1).trim();
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) value = value.slice(1, -1);
    values[key] = value;
  }
  for (const key of ["R2_ENDPOINT", "R2_ACCESS_KEY", "R2_SECRET_KEY", "R2_BUCKET"]) {
    if (!values[key]) throw new Error(`missing ${key} in .env`);
  }
  return values;
}

async function bodyBuffer(body) {
  const chunks = [];
  for await (const chunk of body) chunks.push(Buffer.from(chunk));
  return Buffer.concat(chunks);
}

function requiredChapters(plan) {
  const required = new Map();
  const add = (osisBook, chapter) => {
    if (!OSIS_TO_R2[osisBook]) throw new Error(`unsupported OSIS book: ${osisBook}`);
    const chapters = required.get(osisBook) ?? new Set();
    chapters.add(Number(chapter));
    required.set(osisBook, chapters);
  };
  for (const chapter of plan.chapters ?? []) add(chapter.osisBook, chapter.chapter);
  for (const verse of plan.memoryVerses ?? []) add(verse.osisBook, verse.chapter);
  // MT Hosea 14:1 is numbered Hosea 13:16 in common Protestant editions.
  if (required.get("Hos")?.has(14)) add("Hos", 13);
  return required;
}

function canonicalJson(value) {
  return JSON.stringify(value, null, 2) + "\n";
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  const plan = JSON.parse(await readFile(options.plan, "utf8"));
  const env = await loadEnv();
  const client = new S3Client({
    region: "auto",
    endpoint: env.R2_ENDPOINT,
    credentials: {
      accessKeyId: env.R2_ACCESS_KEY,
      secretAccessKey: env.R2_SECRET_KEY,
    },
  });
  const required = requiredChapters(plan);
  const books = [];
  const sourceFiles = [];
  let verseUnitCount = 0;
  let coveredVerseCount = 0;

  for (const osisBook of [...required.keys()].sort()) {
    const bookCode = OSIS_TO_R2[osisBook];
    const key = `bible-verses/${bookCode}.json.gz`;
    const response = await client.send(new GetObjectCommand({ Bucket: env.R2_BUCKET, Key: key }));
    if (!response.Body) throw new Error(`empty R2 object: ${key}`);
    const compressed = await bodyBuffer(response.Body);
    const sourceHash = createHash("sha256").update(compressed).digest("hex");
    const document = JSON.parse(gunzipSync(compressed).toString("utf8"));
    const chapters = [];
    for (const chapterNumber of [...required.get(osisBook)].sort((a, b) => a - b)) {
      const entries = document.chapters?.[String(chapterNumber)];
      if (!Array.isArray(entries) || !entries.length) {
        throw new Error(`missing ${osisBook}.${chapterNumber} in ${key}`);
      }
      const official = await fetchOfficialChapter(osisBook, chapterNumber);
      verseUnitCount += official.verses.length;
      coveredVerseCount += official.verses.reduce(
        (sum, verse) => sum + verse.verseEnd - verse.verse + 1,
        0,
      );
      chapters.push({ chapter: chapterNumber, ...official });
      await delay(150);
    }
    books.push({ code: osisBook, name: OSIS_TO_NAME[osisBook], chapters });
    sourceFiles.push({
      bookCode,
      osisBook,
      r2Key: key,
      compressedSha256: sourceHash,
      selectedChapters: [...required.get(osisBook)].sort((a, b) => a - b),
    });
  }

  const payload = {
    schemaVersion: "1.0",
    translation: {
      versionCode: "cuv2010",
      titleZh: "和合本修訂版（2010）",
      titleEn: "Revised Chinese Union Version (RCUV) 2010",
      variant: "RCUV2（上帝版）",
      publisher: "香港聖經公會",
      sourceUrl: "https://rcuv.hkbs.org.hk/",
      useScope: "private-authorized",
      canonicalStore: "official-hkbs-with-private-r2-provenance",
    },
    generatedFrom: {
      plan: options.plan.replaceAll("\\", "/"),
      planSha256: createHash("sha256").update(await readFile(options.plan)).digest("hex"),
      sourceFiles,
    },
    counts: {
      books: books.length,
      chapters: books.reduce((sum, book) => sum + book.chapters.length, 0),
      verseUnits: verseUnitCount,
      coveredVerseNumbers: coveredVerseCount,
    },
    books,
  };

  const serialized = canonicalJson(payload);
  console.log(JSON.stringify({
    output: options.output,
    write: options.write,
    counts: payload.counts,
    contentSha256: createHash("sha256").update(serialized).digest("hex"),
  }));
  if (options.write) {
    await mkdir(dirname(options.output), { recursive: true });
    await writeFile(options.output, serialized, "utf8");
  }
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : error);
  process.exitCode = 1;
});
