/** 「第一章」形式視為章節；其餘（含人間佛教等）視為主題。「（未分章）」歸主題側。 */
export function isChapterNavName(name: string): boolean {
  const t = name.trim();
  if (!t || t === "（未分章）") return false;
  return /^第.+章$/.test(t);
}

export type NavChapterRow = { name: string; count: number; chapterName?: string };

export function chapterNavRows(rows: NavChapterRow[]) {
  return rows.filter((c) => isChapterNavName(c.name));
}

export function topicNavRows(rows: NavChapterRow[]) {
  return rows.filter((c) => !isChapterNavName(c.name));
}

const CN_NUM: Record<string, number> = {
  一: 1,
  二: 2,
  三: 3,
  四: 4,
  五: 5,
  六: 6,
  七: 7,
  八: 8,
  九: 9,
  十: 10,
  十一: 11,
  十二: 12,
  十三: 13,
  十四: 14,
  十五: 15,
  十六: 16,
  十七: 17,
  十八: 18,
  十九: 19,
  二十: 20,
  二十一: 21,
  二十二: 22,
  二十三: 23,
  二十四: 24,
  二十五: 25,
  二十六: 26,
  二十七: 27,
  二十八: 28,
  二十九: 29,
  三十: 30,
};

/** 「第…章」→ 阿拉伯章序，無法辨識則 null */
export function chapterOrderIndex(name: string): number | null {
  const m = name.trim().match(/^第(.+)章$/);
  if (!m) return null;
  const inner = m[1];
  if (CN_NUM[inner] != null) return CN_NUM[inner];
  const n = Number(inner);
  return Number.isFinite(n) && n > 0 ? n : null;
}

/** 專案 description 可為 JSON：卷標、每卷章數、備註、或明確單排章節 */
export type ExcerptLayoutMeta = {
  volumeLabels?: string[];
  volumeChapterSize?: number;
  publicNote?: string;
  /** 已按「取消分卷」：不要套用書名預設分卷 */
  flatChapters?: boolean;
};

export function parseExcerptLayoutMeta(description: string | null | undefined): ExcerptLayoutMeta | null {
  const t = description?.trim();
  if (!t || !t.startsWith("{")) return null;
  try {
    const o = JSON.parse(t) as unknown;
    if (!o || typeof o !== "object") return null;
    const rec = o as Record<string, unknown>;
    const out: ExcerptLayoutMeta = {};
    if (rec.flatChapters === true) out.flatChapters = true;
    if (Array.isArray(rec.volumeLabels) && rec.volumeLabels.every((x) => typeof x === "string")) {
      out.volumeLabels = rec.volumeLabels as string[];
    }
    if (typeof rec.volumeChapterSize === "number" && rec.volumeChapterSize > 0) {
      out.volumeChapterSize = rec.volumeChapterSize;
    }
    if (typeof rec.publicNote === "string") out.publicNote = rec.publicNote;

    if (out.volumeLabels?.length) {
      if (!out.volumeChapterSize) out.volumeChapterSize = 4;
      return out;
    }
    if (out.flatChapters) return { flatChapters: true };
    return null;
  } catch {
    return null;
  }
}

/** 《千面上帝》：未在資料庫設定分卷時，仍預設 7 卷 × 4 章（可被 flatChapters 關閉） */
export const PRESET_THOUSAND_FACES_VOLUMES: string[] = [
  "遠古時代卷",
  "古風時代卷",
  "軸心時代卷",
  "古典時代卷",
  "中古時代卷",
  "近世改革卷",
  "近現代卷",
];

function defaultVolumeMetaForProject(projectName: string | null | undefined): ExcerptLayoutMeta | null {
  if ((projectName || "").trim() === "千面上帝") {
    return {
      volumeChapterSize: 4,
      volumeLabels: [...PRESET_THOUSAND_FACES_VOLUMES],
    };
  }
  return null;
}

/**
 * 實際用於分卷 UI：先讀 description；若無 volumeLabels 且未 flatChapters，則對特定書名給預設。
 */
export function resolveExcerptLayoutMeta(
  description: string | null | undefined,
  projectName: string | null | undefined
): ExcerptLayoutMeta | null {
  const parsed = parseExcerptLayoutMeta(description);
  if (parsed?.volumeLabels?.length) return parsed;
  if (parsed?.flatChapters) return null;
  return defaultVolumeMetaForProject(projectName);
}

/** 若 description 為版面 JSON，文章頁不應把整段 JSON 當一般說明顯示 */
export function excerptLayoutPublicNote(description: string | null | undefined): string | null {
  const meta = parseExcerptLayoutMeta(description);
  if (!meta) return null;
  const n = (meta.publicNote || "").trim();
  return n.length ? n : null;
}

export function isExcerptLayoutDescription(description: string | null | undefined): boolean {
  return parseExcerptLayoutMeta(description) != null;
}

export type ChapterVolumeGroup = { title: string; chapters: NavChapterRow[] };

/** 章名落在第幾個分卷區塊（無則 null） */
export function volumeGroupIndexForChapter(
  groups: ChapterVolumeGroup[],
  chapterName: string
): number | null {
  for (let i = 0; i < groups.length; i++) {
    if (groups[i].chapters.some((c) => c.name === chapterName)) return i;
  }
  return null;
}

/**
 * 依章序將「第…章」列每 volumeChapterSize 章一組；有 volumeLabels 時作為小標題。
 * 無 meta 或無 volumeLabels 時回傳單一區塊（title 空字串＝不顯示標題）。
 */
export function groupChaptersByVolume(
  chapterNavItems: NavChapterRow[],
  meta: ExcerptLayoutMeta | null
): ChapterVolumeGroup[] {
  const items = chapterNavItems.filter((c) => isChapterNavName(c.name));
  if (!meta?.volumeLabels?.length) {
    return [{ title: "", chapters: items }];
  }
  const size = meta.volumeChapterSize ?? 4;
  const sorted = [...items].sort((a, b) => {
    const ia = chapterOrderIndex(a.name) ?? 9999;
    const ib = chapterOrderIndex(b.name) ?? 9999;
    return ia - ib;
  });
  const groups: ChapterVolumeGroup[] = [];
  for (let i = 0; i < sorted.length; i += size) {
    const chunk = sorted.slice(i, i + size);
    const volIdx = Math.floor(i / size);
    const label =
      meta.volumeLabels![volIdx] ??
      `第${volIdx + 1}卷`;
    groups.push({ title: label, chapters: chunk });
  }
  return groups;
}
