#!/usr/bin/env node
/**
 * Build current-original contact sheets and an evidence-first review manifest
 * from a completed/reconciled Chenwei image duplicate audit.
 *
 * This is read-only with respect to the photo library. Automated labels are
 * deliberately preliminary; no output is an instruction to delete a file.
 */

import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import sharp from "sharp";

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(SCRIPT_DIR, "..");
const DEFAULT_PHOTOS_ROOT = "G:/我的雲端硬碟/資料/知識圖工作室/照片/辰瑋相片";
const CELL_WIDTH = 380;
const CELL_HEIGHT = 310;
const IMAGE_WIDTH = 350;
const IMAGE_HEIGHT = 230;
const MAX_PER_PAGE = 12;

function parseArgs(argv) {
  const opts = {
    report: null,
    photosRoot: DEFAULT_PHOTOS_ROOT,
    outDir: null,
    maxClusters: 0,
    concurrency: 2,
    readTimeoutMs: 60_000,
  };
  for (const arg of argv) {
    const [name, ...rest] = arg.split("=");
    const value = rest.join("=");
    if (!value) throw new Error(`Incomplete option: ${arg}`);
    if (name === "--report") opts.report = path.resolve(REPO, value);
    else if (name === "--photos-root") opts.photosRoot = path.resolve(REPO, value);
    else if (name === "--out-dir") opts.outDir = path.resolve(REPO, value);
    else if (name === "--max-clusters") opts.maxClusters = Number(value);
    else if (name === "--concurrency") opts.concurrency = Number(value);
    else if (name === "--read-timeout-ms") opts.readTimeoutMs = Number(value);
    else throw new Error(`Unknown option: ${name}`);
  }
  if (!opts.report) throw new Error("--report=PATH is required");
  if (!opts.outDir) opts.outDir = opts.report.replace(/\.json$/i, "") + "-review";
  if (!Number.isInteger(opts.maxClusters) || opts.maxClusters < 0) throw new Error("--max-clusters must be >= 0");
  if (!Number.isInteger(opts.concurrency) || opts.concurrency < 1 || opts.concurrency > 4) throw new Error("--concurrency must be 1..4");
  if (!Number.isInteger(opts.readTimeoutMs) || opts.readTimeoutMs < 1000) throw new Error("--read-timeout-ms must be >= 1000");
  return opts;
}

function resolveOriginalPath(item, photosRoot) {
  if (path.basename(item.name) !== item.name || item.name === "." || item.name === "..") {
    throw new Error("invalid indexed filename");
  }
  let folder;
  if (/^(0[1-9]|1[0-2])$/.test(item.bucket)) folder = `${item.year}.${item.bucket}`;
  else if (item.bucket === "screenshots") folder = `${item.year}截圖`;
  else if (item.bucket === "downloads") folder = `${item.year}下載`;
  else if (/^(0[1-9]|1[0-2])\//.test(item.bucket)) {
    const [month, event] = item.bucket.split("/");
    if (!event || event.includes("\\")) throw new Error("invalid month event");
    folder = path.join(`${item.year}.${month}`, event);
  } else {
    if (!item.bucket || item.bucket.includes("/") || item.bucket.includes("\\")) throw new Error("invalid event bucket");
    folder = item.bucket;
  }
  const root = path.resolve(photosRoot);
  const resolved = path.resolve(root, `${item.year}相片`, folder, item.name);
  if (!resolved.startsWith(root + path.sep)) throw new Error("indexed path escaped photo root");
  return resolved;
}

async function readWithTimeout(file, timeoutMs) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  try { return await fs.readFile(file, { signal: controller.signal }); }
  finally { clearTimeout(timeout); }
}

async function mapLimit(items, concurrency, handler) {
  const results = new Array(items.length);
  let cursor = 0;
  async function worker() {
    while (true) {
      const index = cursor++;
      if (index >= items.length) return;
      results[index] = await handler(items[index], index);
    }
  }
  await Promise.all(Array.from({ length: Math.min(items.length, concurrency) }, () => worker()));
  return results;
}

function xml(value) {
  return String(value).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
}

function shortRef(ref, max = 47) {
  return ref.length <= max ? ref : `${ref.slice(0, 19)}…${ref.slice(-(max - 20))}`;
}

async function currentVisual(item, opts) {
  const originalPath = resolveOriginalPath(item, opts.photosRoot);
  const bytes = await readWithTimeout(originalPath, opts.readTimeoutMs);
  const image = sharp(bytes, { failOn: "none", limitInputPixels: 100_000_000 }).rotate();
  const display = await image.clone()
    .resize(IMAGE_WIDTH, IMAGE_HEIGHT, { fit: "contain", background: { r: 22, g: 22, b: 22 } })
    .flatten({ background: { r: 22, g: 22, b: 22 } })
    .jpeg({ quality: 88 })
    .toBuffer();
  const comparison = await image.clone()
    .resize(96, 96, { fit: "fill" })
    .removeAlpha()
    .toColourspace("srgb")
    .raw()
    .toBuffer();
  return {
    ok: true,
    item,
    originalPath,
    originalSha256: crypto.createHash("sha256").update(bytes).digest("hex"),
    displaySha256: crypto.createHash("sha256").update(display).digest("hex"),
    display,
    comparison,
  };
}

function pixelMetrics(left, right) {
  if (!left?.comparison || !right?.comparison || left.comparison.length !== right.comparison.length) return null;
  let absolute = 0;
  let squared = 0;
  let max = 0;
  for (let index = 0; index < left.comparison.length; index++) {
    const delta = Math.abs(left.comparison[index] - right.comparison[index]);
    absolute += delta;
    squared += delta * delta;
    if (delta > max) max = delta;
  }
  return {
    meanAbsoluteError: Math.round(absolute / left.comparison.length * 1000) / 1000,
    rootMeanSquareError: Math.round(Math.sqrt(squared / left.comparison.length) * 1000) / 1000,
    maxChannelDelta: max,
  };
}

function burstStem(name) {
  return name.toLocaleLowerCase("en-US")
    .replace(/\.[^.]+$/, "")
    .replace(/\(\d+\)$/, "")
    .replace(/(?:[_ -](?:dup|copy|edited|edit|副本)\d*)$/i, "");
}

function sameBurstFamily(left, right) {
  return left.bucket === right.bucket && burstStem(left.name) === burstStem(right.name);
}

function pairClassification(candidate, pixels, leftVisual, rightVisual) {
  const currentByteIdentical = leftVisual?.originalSha256 &&
    leftVisual.originalSha256 === rightVisual?.originalSha256;
  if (currentByteIdentical) {
    return {
      classification: "safe_delete_candidate_exact_current_bytes",
      strength: "strong",
      evidence: "fresh current-original SHA-256 is identical",
    };
  }
  const sameFreshRender = leftVisual?.displaySha256 && leftVisual.displaySha256 === rightVisual?.displaySha256;
  if (sameFreshRender) {
    return {
      classification: "safe_delete_candidate_identical_current_render",
      strength: "strong",
      evidence: "fresh current-original 480px render SHA-256 is identical; original bytes differ",
    };
  }
  if (pixels && pixels.meanAbsoluteError <= 2.5 && pixels.rootMeanSquareError <= 6) {
    return {
      classification: "safe_delete_candidate_near_identical_current_pixels",
      strength: "moderate",
      evidence: `fresh 96px RGB MAE=${pixels.meanAbsoluteError}, RMSE=${pixels.rootMeanSquareError}`,
    };
  }
  if (sameBurstFamily(candidate.left, candidate.right)) {
    return {
      classification: "must_keep_likely_distinct_burst_pose_frame",
      strength: "moderate",
      evidence: `same filename burst family but current pixels differ (MAE=${pixels?.meanAbsoluteError ?? "n/a"})`,
    };
  }
  if (pixels && pixels.meanAbsoluteError <= 6 &&
      (candidate.originalMetrics?.pHashDistance ?? 99) <= 2 &&
      (candidate.originalMetrics?.dHashDistance ?? 99) <= 3) {
    return {
      classification: "manual_review_probable_reencode_or_micro_edit",
      strength: "review",
      evidence: `very close current pixels/hashes but not identical (MAE=${pixels.meanAbsoluteError})`,
    };
  }
  return {
    classification: "must_keep_or_manual_review_distinct_scene_pose_frame",
    strength: "review",
    evidence: `current images exceed near-identical pixel gate (MAE=${pixels?.meanAbsoluteError ?? "n/a"})`,
  };
}

function clusterPriority(candidates) {
  if (candidates.some((candidate) => candidate.originalByteIdentical)) return 0;
  if (candidates.some((candidate) => candidate.type === "exact_thumbnail")) return 1;
  if (candidates.some((candidate) => candidate.type === "normalized_pixels_identical")) return 2;
  if (candidates.some((candidate) => candidate.type === "fingerprint_identical")) return 3;
  return 4;
}

function clusterPreliminaryClass(pairEvidence) {
  if (pairEvidence.length && pairEvidence.every((pair) => pair.classification.startsWith("safe_delete_candidate_"))) {
    return "safe_delete_candidate_cluster_human_confirmation_required";
  }
  if (pairEvidence.some((pair) => pair.classification === "must_keep_likely_distinct_burst_pose_frame")) {
    return "must_keep_likely_distinct_burst_pose_frame";
  }
  return "manual_visual_review_required";
}

function labelSvg(width, height, lines, color = "#ffffff") {
  const tspans = lines.map((line, index) =>
    `<tspan x="12" dy="${index === 0 ? 0 : 19}">${xml(line)}</tspan>`).join("");
  return Buffer.from(`<svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
    <rect width="100%" height="100%" fill="#111827"/>
    <text x="12" y="21" fill="${color}" font-family="Microsoft JhengHei, Segoe UI, sans-serif" font-size="14">${tspans}</text>
  </svg>`);
}

async function buildSheetPage(cluster, pageMembers, pageNumber, pageCount, visuals, classification, outFile) {
  const columns = Math.min(3, pageMembers.length);
  const rows = Math.ceil(pageMembers.length / columns);
  const headerHeight = 82;
  const width = columns * CELL_WIDTH;
  const height = headerHeight + rows * CELL_HEIGHT;
  const composites = [{
    input: labelSvg(width, headerHeight, [
      `${cluster.id}  members=${cluster.size} edges=${cluster.edgeCount}  page ${pageNumber}/${pageCount}`,
      `PRELIMINARY: ${classification}`,
      "Fresh current originals; human review required; no automatic deletion",
    ], classification.startsWith("safe_delete") ? "#86efac" : classification.startsWith("must_keep") ? "#fca5a5" : "#fde68a"),
    left: 0,
    top: 0,
  }];
  for (let index = 0; index < pageMembers.length; index++) {
    const member = pageMembers[index];
    const visual = visuals.get(member.ref);
    const column = index % columns;
    const row = Math.floor(index / columns);
    const left = column * CELL_WIDTH;
    const top = headerHeight + row * CELL_HEIGHT;
    composites.push({ input: visual.display, left: left + 15, top: top + 8 });
    composites.push({
      input: labelSvg(CELL_WIDTH - 12, 67, [
        `${index + 1 + (pageNumber - 1) * MAX_PER_PAGE}. [${member.source}] ${member.name}`,
        shortRef(member.ref),
        `mtime=${member.mtimeIso ?? "unknown"}`,
      ]),
      left: left + 6,
      top: top + IMAGE_HEIGHT + 14,
    });
  }
  await sharp({ create: { width, height, channels: 3, background: { r: 9, g: 12, b: 20 } } })
    .composite(composites)
    .png({ compressionLevel: 8 })
    .toFile(outFile);
}

function csvCell(value) {
  if (value === null || value === undefined) return "";
  const text = typeof value === "object" ? JSON.stringify(value) : String(value);
  return /[",\r\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

function toCsv(rows, columns) {
  return [columns.join(","), ...rows.map((row) => columns.map((column) => csvCell(row[column])).join(","))].join("\r\n") + "\r\n";
}

async function main() {
  const opts = parseArgs(process.argv.slice(2));
  const report = JSON.parse(await fs.readFile(opts.report, "utf8"));
  const candidateByPair = new Map((report.candidates ?? []).map((candidate) => [
    [candidate.left.ref, candidate.right.ref].sort().join("\u0000"), candidate,
  ]));
  const ranked = (report.reviewClusters ?? []).map((cluster) => {
    const candidates = cluster.edges.map((edge) =>
      candidateByPair.get([edge.leftRef, edge.rightRef].sort().join("\u0000"))).filter(Boolean);
    return { cluster, candidates, priority: clusterPriority(candidates) };
  }).sort((left, right) => left.priority - right.priority || right.cluster.size - left.cluster.size ||
    left.cluster.id.localeCompare(right.cluster.id));
  const selected = opts.maxClusters ? ranked.slice(0, opts.maxClusters) : ranked;
  const sheetsDir = path.join(opts.outDir, "contact-sheets");
  await fs.mkdir(sheetsDir, { recursive: true });
  const clusterReviews = [];
  const allPairEvidence = [];
  let completed = 0;

  await mapLimit(selected, opts.concurrency, async ({ cluster, candidates, priority }) => {
    const visualsArray = await mapLimit(cluster.members, Math.min(2, opts.concurrency), async (member) => {
      try { return await currentVisual(member, opts); }
      catch (error) { return { ok: false, item: member, reason: String(error?.code || error?.name || "read_error") }; }
    });
    const visuals = new Map(visualsArray.filter((visual) => visual.ok).map((visual) => [visual.item.ref, visual]));
    const pairEvidence = candidates.map((candidate) => {
      const pixels = pixelMetrics(visuals.get(candidate.left.ref), visuals.get(candidate.right.ref));
      return {
        clusterId: cluster.id,
        leftRef: candidate.left.ref,
        rightRef: candidate.right.ref,
        type: candidate.type,
        originalByteIdentical: candidate.originalByteIdentical,
        originalPHashDistance: candidate.originalMetrics?.pHashDistance,
        originalDHashDistance: candidate.originalMetrics?.dHashDistance,
        currentByteIdenticalNow: Boolean(visuals.get(candidate.left.ref)?.originalSha256 &&
          visuals.get(candidate.left.ref)?.originalSha256 === visuals.get(candidate.right.ref)?.originalSha256),
        currentRenderIdenticalNow: Boolean(visuals.get(candidate.left.ref)?.displaySha256 &&
          visuals.get(candidate.left.ref)?.displaySha256 === visuals.get(candidate.right.ref)?.displaySha256),
        ...pixels,
        ...pairClassification(candidate, pixels, visuals.get(candidate.left.ref), visuals.get(candidate.right.ref)),
        humanReviewRequired: true,
      };
    });
    allPairEvidence.push(...pairEvidence);
    const classification = clusterPreliminaryClass(pairEvidence);
    const readableMembers = cluster.members.filter((member) => visuals.has(member.ref));
    const pageCount = Math.max(1, Math.ceil(readableMembers.length / MAX_PER_PAGE));
    const sheetFiles = [];
    for (let page = 0; page < pageCount; page++) {
      const pageMembers = readableMembers.slice(page * MAX_PER_PAGE, (page + 1) * MAX_PER_PAGE);
      if (!pageMembers.length) continue;
      const suffix = pageCount > 1 ? `-p${String(page + 1).padStart(2, "0")}` : "";
      const name = `${cluster.id}${suffix}.png`;
      await buildSheetPage(cluster, pageMembers, page + 1, pageCount, visuals, classification, path.join(sheetsDir, name));
      sheetFiles.push(`contact-sheets/${name}`);
    }
    clusterReviews.push({
      clusterId: cluster.id,
      priority,
      prioritySource: priority === 0 ? "current_byte_identical" : priority === 1 ? "cached_exact_thumbnail" :
        priority === 2 ? "cached_normalized_pixels" : priority === 3 ? "cached_fingerprint_identical" : "perceptual_near_match",
      memberCount: cluster.members.length,
      edgeCount: candidates.length,
      readableCurrentOriginals: readableMembers.length,
      currentOriginalReadErrors: visualsArray.filter((visual) => !visual.ok).map((visual) => ({ ref: visual.item.ref, reason: visual.reason })),
      preliminaryClassification: classification,
      humanReviewRequired: true,
      deletionRecommendation: "none_until_contact_sheet_human_adjudication",
      sheetFiles,
      members: cluster.members,
      pairEvidence,
    });
    completed++;
    if (completed % 25 === 0 || completed === selected.length) console.log(`[sheets ${completed}/${selected.length}]`);
  });

  clusterReviews.sort((left, right) => left.priority - right.priority || left.clusterId.localeCompare(right.clusterId));
  allPairEvidence.sort((left, right) => left.clusterId.localeCompare(right.clusterId) || left.leftRef.localeCompare(right.leftRef));
  const manifest = {
    schemaVersion: 1,
    generatedAt: new Date().toISOString(),
    readonly: true,
    sourceReport: path.relative(REPO, opts.report).replaceAll("\\", "/"),
    automatedLabelsArePreliminary: true,
    humanReviewRequired: true,
    deletionPerformed: false,
    scope: {
      totalReviewClustersInReport: ranked.length,
      selectedClusters: selected.length,
      priorityOrder: ["current byte-identical", "cached exact thumbnail", "cached normalized pixels", "cached fingerprint-identical", "near match"],
    },
    classificationRules: {
      safeDeleteCandidate: "fresh byte identity, identical fresh render, or very-low fresh pixel error; still requires human confirmation",
      mustKeepLikelyDistinct: "same burst filename family with non-identical fresh current pixels",
      manualReview: "all other visual-similarity clusters",
    },
    clusterReviews,
  };
  await fs.writeFile(path.join(opts.outDir, "review-manifest.json"), JSON.stringify(manifest, null, 2) + "\n", "utf8");
  await fs.writeFile(path.join(opts.outDir, "cluster-review.csv"), toCsv(clusterReviews.map((review) => ({
    clusterId: review.clusterId,
    priority: review.priority,
    prioritySource: review.prioritySource,
    memberCount: review.memberCount,
    edgeCount: review.edgeCount,
    readableCurrentOriginals: review.readableCurrentOriginals,
    preliminaryClassification: review.preliminaryClassification,
    humanReviewRequired: review.humanReviewRequired,
    deletionRecommendation: review.deletionRecommendation,
    sheetFiles: review.sheetFiles.join(";"),
  })), [
    "clusterId", "priority", "prioritySource", "memberCount", "edgeCount", "readableCurrentOriginals",
    "preliminaryClassification", "humanReviewRequired", "deletionRecommendation", "sheetFiles",
  ]), "utf8");
  await fs.writeFile(path.join(opts.outDir, "pair-evidence.csv"), toCsv(allPairEvidence, [
    "clusterId", "leftRef", "rightRef", "type", "originalByteIdentical", "currentByteIdenticalNow",
    "currentRenderIdenticalNow", "originalPHashDistance",
    "originalDHashDistance", "meanAbsoluteError", "rootMeanSquareError", "maxChannelDelta",
    "classification", "strength", "evidence", "humanReviewRequired",
  ]), "utf8");
  console.log(JSON.stringify({
    clusters: clusterReviews.length,
    pairEvidence: allPairEvidence.length,
    outDir: opts.outDir,
  }));
}

main().catch((error) => {
  console.error(`FATAL ${String(error?.message || error).slice(0, 500)}`);
  process.exitCode = 1;
});
