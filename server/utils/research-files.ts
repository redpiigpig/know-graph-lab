import fs from "node:fs";
import path from "node:path";

/**
 * 研究資料原檔的取檔策略：**Drive 正本優先，R2 只是雲端後備**。
 *
 * R2 只有 10GB、Drive 有 5TB，所以大宗掃描原檔（福嚴會訊、弘誓雙月刊、國家檔案局
 * 卷宗…約 8.5GB）一律不上 R2。本機跑站時 G: 槽掛著 Drive，直接讀檔案系統即可，
 * 下載功能完全不受影響。詳見 docs/r2-policy.md。
 *
 * R2 key 與 Drive 相對路徑大多一致，但站上會重新歸類（例如「研究回顧」是站上的
 * 分類、Drive 上該檔實際放在「作者/林建德/」），所以路徑找不到時再退回檔名索引。
 */

const PREFIX_TO_SUBDIR: Record<string, string> = {
  "dadaodao-materials/": path.join("大愛道革命", "論文資料"),
  "yinshun-hongshi/": "印順學派與弘誓",
  "mukyokai/": "日本無教會主義",
};

export const RESEARCH_PREFIXES = Object.keys(PREFIX_TO_SUBDIR);

function rootFor(key: string): { root: string; rel: string } | null {
  const base = useRuntimeConfig().researchDataRoot as string;
  if (!base) return null;
  for (const [prefix, subdir] of Object.entries(PREFIX_TO_SUBDIR)) {
    if (key.startsWith(prefix)) {
      return { root: path.join(base, subdir), rel: key.slice(prefix.length) };
    }
  }
  return null;
}

/** 檔名 → 完整路徑（同名多檔則全收）。第一次呼叫才走訪，之後快取。 */
const nameIndexCache = new Map<string, Map<string, string[]>>();
function nameIndex(root: string): Map<string, string[]> {
  const cached = nameIndexCache.get(root);
  if (cached) return cached;
  const index = new Map<string, string[]>();
  const walk = (dir: string) => {
    let entries: fs.Dirent[];
    try {
      entries = fs.readdirSync(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const e of entries) {
      const full = path.join(dir, e.name);
      if (e.isDirectory()) walk(full);
      else index.set(e.name, [...(index.get(e.name) ?? []), full]);
    }
  };
  walk(root);
  nameIndexCache.set(root, index);
  return index;
}

/** 回傳 Drive 上的原檔路徑；找不到（或非本機環境）回 null，由呼叫端退回 R2。 */
export function resolveResearchFile(key: string): string | null {
  if (key.includes("..")) return null;
  const loc = rootFor(key);
  if (!loc) return null;

  const direct = path.join(loc.root, ...loc.rel.split("/"));
  if (fs.existsSync(direct) && fs.statSync(direct).isFile()) return direct;

  const candidates = nameIndex(loc.root).get(loc.rel.split("/").pop() ?? "");
  return candidates?.length === 1 ? candidates[0] : (candidates?.[0] ?? null);
}
