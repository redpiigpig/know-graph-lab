#!/usr/bin/env node
/**
 * Reconcile a completed read-only Chenwei image audit with recycle-bin actions
 * that happened after its saved source-index snapshot.
 *
 * The raw audit is never overwritten. A new reconciled JSON/CSV/missing CSV
 * excludes those no-longer-current paths from active candidates and preserves
 * them in an explicit exclusion section/CSV.
 */

import fs from "node:fs/promises";
import fsSync from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(SCRIPT_DIR, "..");
const DEFAULT_LOG = path.join(REPO, "scripts", "logs", "chenwei_duplicate_delete_execution_20260804.jsonl");

function parseArgs(argv) {
  const opts = { report: null, executionLog: DEFAULT_LOG, outPrefix: null };
  for (const arg of argv) {
    const [name, ...rest] = arg.split("=");
    const value = rest.join("=");
    if (!value) throw new Error(`Incomplete option: ${arg}`);
    if (name === "--report") opts.report = path.resolve(REPO, value);
    else if (name === "--execution-log") opts.executionLog = path.resolve(REPO, value);
    else if (name === "--out-prefix") opts.outPrefix = path.resolve(REPO, value);
    else throw new Error(`Unknown option: ${name}`);
  }
  if (!opts.report) throw new Error("--report=PATH is required");
  if (!opts.outPrefix) opts.outPrefix = opts.report.replace(/\.json$/i, "") + ".reconciled";
  return opts;
}

function normalizedRelative(value) {
  return String(value || "").replaceAll("/", "\\").replace(/^\\+/, "").toLocaleLowerCase("en-US");
}

function folderForBucket(year, bucket) {
  if (/^(0[1-9]|1[0-2])$/.test(bucket)) return `${year}.${bucket}`;
  if (bucket === "screenshots") return `${year}截圖`;
  if (bucket === "downloads") return `${year}下載`;
  if (/^(0[1-9]|1[0-2])\//.test(bucket)) {
    const [month, event] = bucket.split("/");
    return `${year}.${month}\\${event}`;
  }
  return bucket;
}

function sourceForBucket(bucket) {
  if (bucket === "screenshots") return "screenshot";
  if (bucket === "downloads") return "download";
  if (/^(0[1-9]|1[0-2])$/.test(bucket)) return "photo";
  return "event";
}

function buildIndexMaps(index) {
  const byRelative = new Map();
  for (const [year, yearData] of Object.entries(index?.libraries?.chenwei?.years ?? {})) {
    for (const [bucket, files] of Object.entries(yearData.buckets ?? {})) {
      for (const file of files) {
        const relativePath = `${year}相片\\${folderForBucket(year, bucket)}\\${file.name}`;
        byRelative.set(normalizedRelative(relativePath), {
          ref: `${year}/${bucket}/${file.name}`,
          year,
          bucket,
          source: sourceForBucket(bucket),
          name: file.name,
          ext: file.ext,
          size: Number(file.size) || 0,
          mtime: Number(file.mtime) || 0,
          mtimeIso: file.mtime ? new Date(file.mtime).toISOString() : null,
          relativePath,
        });
      }
    }
  }
  return byRelative;
}

function parseSnapshotTime(value) {
  const text = String(value || "");
  if (!text) return NaN;
  // build_photo_index.py writes local wall time without an offset.
  return Date.parse(/[zZ]|[+-]\d\d:\d\d$/.test(text) ? text : `${text}+08:00`);
}

function parseEventTime(row) {
  return Date.parse(row.timestamp || row.ts || "");
}

async function loadLog(file) {
  const rows = [];
  for (const line of (await fs.readFile(file, "utf8")).split(/\r?\n/)) {
    if (!line.trim()) continue;
    try { rows.push(JSON.parse(line)); } catch { /* retain only valid durable log rows */ }
  }
  return rows;
}

function csvCell(value) {
  if (value === null || value === undefined) return "";
  const text = typeof value === "object" ? JSON.stringify(value) : String(value);
  return /[",\r\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

function toCsv(rows, columns) {
  return [columns.join(","), ...rows.map((row) => columns.map((column) => csvCell(row[column])).join(","))].join("\r\n") + "\r\n";
}

function candidateCsvRows(candidates) {
  return candidates.map((candidate) => ({
    reviewClusterId: candidate.reviewClusterId,
    type: candidate.type,
    generationConfidence: candidate.generationConfidence,
    validationStatus: candidate.validationStatus,
    originalByteIdentical: candidate.originalByteIdentical,
    score: candidate.score,
    pHashDistance: candidate.pHashDistance,
    dHashDistance: candidate.dHashDistance,
    totalHashDistance: candidate.totalHashDistance,
    aspectDelta: candidate.aspectDelta,
    brightnessDelta: candidate.brightnessDelta,
    colorDistance: candidate.colorDistance,
    originalPHashDistance: candidate.originalMetrics?.pHashDistance,
    originalDHashDistance: candidate.originalMetrics?.dHashDistance,
    originalTotalHashDistance: candidate.originalMetrics?.totalHashDistance,
    originalAspectDelta: candidate.originalMetrics?.aspectDelta,
    originalBrightnessDelta: candidate.originalMetrics?.brightnessDelta,
    originalColorDistance: candidate.originalMetrics?.colorDistance,
    leftCachedThumbnailStale: candidate.leftCurrentOriginal?.cachedThumbnailMateriallyStale,
    rightCachedThumbnailStale: candidate.rightCurrentOriginal?.cachedThumbnailMateriallyStale,
    deletionRecommendation: candidate.deletionRecommendation,
    earliestIndexMtimeRef: candidate.earliestIndexMtimeRef,
    earliestIndexMtimeCaveat: candidate.earliestIndexMtimeCaveat,
    leftRef: candidate.left.ref,
    leftYear: candidate.left.year,
    leftBucket: candidate.left.bucket,
    leftSource: candidate.left.source,
    leftName: candidate.left.name,
    leftSize: candidate.left.size,
    leftMtimeIso: candidate.left.mtimeIso,
    rightRef: candidate.right.ref,
    rightYear: candidate.right.year,
    rightBucket: candidate.right.bucket,
    rightSource: candidate.right.source,
    rightName: candidate.right.name,
    rightSize: candidate.right.size,
    rightMtimeIso: candidate.right.mtimeIso,
    leftSignatureGroupSize: candidate.leftSignatureGroupSize ?? candidate.signatureGroupSize ??
      candidate.exactGroupSize ?? candidate.normalizedGroupSize ?? 1,
    rightSignatureGroupSize: candidate.rightSignatureGroupSize ?? 1,
  }));
}

const CANDIDATE_COLUMNS = [
  "reviewClusterId", "type", "generationConfidence", "validationStatus", "originalByteIdentical", "score",
  "pHashDistance", "dHashDistance", "totalHashDistance", "aspectDelta", "brightnessDelta", "colorDistance",
  "originalPHashDistance", "originalDHashDistance", "originalTotalHashDistance", "originalAspectDelta",
  "originalBrightnessDelta", "originalColorDistance", "leftCachedThumbnailStale", "rightCachedThumbnailStale",
  "deletionRecommendation", "earliestIndexMtimeRef", "earliestIndexMtimeCaveat",
  "leftRef", "leftYear", "leftBucket", "leftSource", "leftName", "leftSize", "leftMtimeIso",
  "rightRef", "rightYear", "rightBucket", "rightSource", "rightName", "rightSize", "rightMtimeIso",
  "leftSignatureGroupSize", "rightSignatureGroupSize",
];

const MISSING_COLUMNS = ["ref", "year", "bucket", "source", "name", "ext", "size", "mtimeIso", "cacheKey", "r2Key", "reason"];

function filterThumbnailGroups(groups, excludedRefs) {
  return (groups ?? []).map((group) => {
    const members = (group.members ?? []).filter((member) => !excludedRefs.has(member.ref));
    return { ...group, size: members.length, members };
  }).filter((group) => group.members.length > 1);
}

async function main() {
  const opts = parseArgs(process.argv.slice(2));
  const report = JSON.parse(await fs.readFile(opts.report, "utf8"));
  if (report.config?.limit || report.config?.years || report.config?.buckets) {
    throw new Error("Reconciliation currently requires a full unfiltered image audit");
  }
  const sourceIndexPath = path.resolve(REPO, report.sourceIndex?.snapshotPath || "");
  if (!fsSync.existsSync(sourceIndexPath)) throw new Error("Saved source-index snapshot is missing");
  const index = JSON.parse(await fs.readFile(sourceIndexPath, "utf8"));
  const byRelative = buildIndexMaps(index);
  const snapshotTime = parseSnapshotTime(report.sourceIndex.generatedAt);
  const logRows = await loadLog(opts.executionLog);
  const exclusions = [];
  for (const row of logRows) {
    if (!(parseEventTime(row) > snapshotTime)) continue;
    const indexed = byRelative.get(normalizedRelative(row.relativePath));
    if (!indexed) continue;
    const fullPath = row.fullPath || path.join(
      "G:/我的雲端硬碟/資料/知識圖工作室/照片/辰瑋相片", indexed.relativePath,
    );
    let absentNow = false;
    try { await fs.stat(fullPath); } catch (error) { absentNow = error?.code === "ENOENT"; }
    if (!absentNow) continue;
    exclusions.push({
      ...indexed,
      loggedAt: row.timestamp || row.ts,
      logClusterId: row.clusterId ?? null,
      logReason: row.reason ?? "post_snapshot_recycle_bin_action",
      fullPath,
      absentNow: true,
      reconciliationReason: "recycled_after_source_index_snapshot",
    });
  }
  const uniqueExclusions = [...new Map(exclusions.map((row) => [row.ref, row])).values()];
  const excludedRefs = new Set(uniqueExclusions.map((row) => row.ref));
  const excludedCandidates = (report.candidates ?? []).filter((candidate) =>
    excludedRefs.has(candidate.left.ref) || excludedRefs.has(candidate.right.ref));
  const activeCandidates = (report.candidates ?? []).filter((candidate) =>
    !excludedRefs.has(candidate.left.ref) && !excludedRefs.has(candidate.right.ref));
  const activePairKeys = new Set(activeCandidates.map((candidate) =>
    [candidate.left.ref, candidate.right.ref].sort().join("\u0000")));
  const activeClusters = (report.reviewClusters ?? []).map((cluster) => {
    const members = cluster.members.filter((member) => !excludedRefs.has(member.ref));
    const edges = cluster.edges.filter((edge) => activePairKeys.has([edge.leftRef, edge.rightRef].sort().join("\u0000")));
    return { ...cluster, size: members.length, edgeCount: edges.length, members, edges };
  }).filter((cluster) => cluster.members.length > 1 && cluster.edges.length > 0);

  const missingByRef = new Map((report.missingObjects ?? []).map((row) => [row.ref, row]));
  const currentErrorsByRef = new Map((report.currentOriginalValidationErrors ?? []).map((row) => [row.ref, row]));
  for (const exclusion of uniqueExclusions) {
    const row = {
      ref: exclusion.ref,
      year: exclusion.year,
      bucket: exclusion.bucket,
      source: exclusion.source,
      name: exclusion.name,
      ext: exclusion.ext,
      size: exclusion.size,
      mtimeIso: exclusion.mtimeIso,
      cacheKey: "",
      r2Key: "",
      reason: "excluded_post_snapshot_recycle_bin_action",
    };
    missingByRef.set(row.ref, row);
    currentErrorsByRef.set(row.ref, row);
  }
  const candidatePairsByType = {};
  for (const candidate of activeCandidates) {
    candidatePairsByType[candidate.type] = (candidatePairsByType[candidate.type] ?? 0) + 1;
  }
  const originalCandidateCount = report.stats?.candidatePairs ?? report.candidates?.length ?? 0;
  report.reconciledAt = new Date().toISOString();
  report.reconciliation = {
    executionLog: path.relative(REPO, opts.executionLog).replaceAll("\\", "/"),
    sourceSnapshotTime: report.sourceIndex.generatedAt,
    postSnapshotAbsentPaths: uniqueExclusions.length,
    excludedCandidatePairs: excludedCandidates.length,
    note: "Post-snapshot recycle-bin paths are excluded from active candidates and retained below for auditability.",
  };
  report.limitations = [...new Set([
    "Scope is limited to media represented in the saved source-index snapshot; unindexed nested files and top-level staging are excluded.",
    ...(report.limitations ?? []),
  ])];
  report.stats.candidatePairsBeforePostSnapshotExclusion = originalCandidateCount;
  report.stats.excludedPostSnapshotRecycleBinPairs = excludedCandidates.length;
  report.stats.postSnapshotRecycleBinPaths = uniqueExclusions.length;
  report.stats.candidatePairs = activeCandidates.length;
  report.stats.candidatePairsByType = candidatePairsByType;
  report.stats.missingObjects = missingByRef.size;
  report.stats.currentOriginalValidationErrors = currentErrorsByRef.size;
  if (report.stats.currentOriginalValidation) {
    report.stats.currentOriginalValidation.candidatePairsBeforePostSnapshotExclusion =
      report.stats.currentOriginalValidation.candidatePairs;
    report.stats.currentOriginalValidation.candidatePairs = activeCandidates.length;
    report.stats.currentOriginalValidation.postSnapshotRecycleBinPaths = uniqueExclusions.length;
    report.stats.currentOriginalValidation.excludedPostSnapshotRecycleBinPairs = excludedCandidates.length;
    report.stats.currentOriginalValidation.unvalidatedPairs = activeCandidates.filter((candidate) =>
      candidate.validationStatus === "unvalidated_current_original_error").length;
    report.stats.currentOriginalValidation.reviewClusters = activeClusters.length;
    report.stats.currentOriginalValidation.largestReviewCluster = activeClusters.reduce((size, cluster) => Math.max(size, cluster.size), 0);
  }
  report.candidates = activeCandidates;
  report.reviewClusters = activeClusters;
  report.exactThumbnailGroups = filterThumbnailGroups(report.exactThumbnailGroups, excludedRefs);
  report.normalizedPixelGroups = filterThumbnailGroups(report.normalizedPixelGroups, excludedRefs);
  report.identicalFingerprintGroups = filterThumbnailGroups(report.identicalFingerprintGroups, excludedRefs);
  report.currentOriginalValidationErrors = [...currentErrorsByRef.values()];
  report.missingObjects = [...missingByRef.values()];
  report.postSnapshotRecycleBinExclusions = uniqueExclusions.map((exclusion) => ({
    ...exclusion,
    excludedCandidatePairCount: excludedCandidates.filter((candidate) =>
      candidate.left.ref === exclusion.ref || candidate.right.ref === exclusion.ref).length,
  }));
  report.excludedPostSnapshotCandidatePairs = excludedCandidates.map((candidate) => ({
    ...candidate,
    deletionRecommendation: "excluded_path_absent_after_snapshot",
    reviewClusterId: null,
  }));

  const jsonPath = `${opts.outPrefix}.json`;
  const csvPath = `${opts.outPrefix}.csv`;
  const missingPath = `${opts.outPrefix}.missing.csv`;
  const exclusionsPath = `${opts.outPrefix}.post-snapshot-exclusions.csv`;
  await fs.mkdir(path.dirname(opts.outPrefix), { recursive: true });
  await fs.writeFile(jsonPath, JSON.stringify(report, null, 2) + "\n", "utf8");
  await fs.writeFile(csvPath, toCsv(candidateCsvRows(activeCandidates), CANDIDATE_COLUMNS), "utf8");
  await fs.writeFile(missingPath, toCsv(report.missingObjects, MISSING_COLUMNS), "utf8");
  await fs.writeFile(exclusionsPath, toCsv(report.postSnapshotRecycleBinExclusions, [
    "ref", "relativePath", "loggedAt", "logClusterId", "logReason", "absentNow",
    "reconciliationReason", "excludedCandidatePairCount",
  ]), "utf8");
  console.log(JSON.stringify({
    rawCandidatePairs: originalCandidateCount,
    activeCandidatePairs: activeCandidates.length,
    postSnapshotAbsentPaths: uniqueExclusions.length,
    excludedCandidatePairs: excludedCandidates.length,
    jsonPath,
    csvPath,
    missingPath,
    exclusionsPath,
  }, null, 2));
}

main().catch((error) => {
  console.error(`FATAL ${String(error?.message || error).slice(0, 500)}`);
  process.exitCode = 1;
});
