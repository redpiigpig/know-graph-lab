import type {
  OriginalReaderScriptureRef,
  OriginalReaderSelection,
  OriginalReaderSegment,
} from "~/data/originalReaders/types";
import {
  loadBibleBook,
  type BibleVerseEntry,
} from "~/server/utils/bible-verses";

type CorpusVersionCode = "wlc" | "sblgnt" | "lxx" | "vul";

const CORPUS_VERSION_ALIASES: Record<string, CorpusVersionCode> = {
  wlc: "wlc",
  sblgnt: "sblgnt",
  lxx: "lxx",
  "lxx-rh": "lxx",
  "lxx-tob-gii-s": "lxx",
  vul: "vul",
  latvuc: "vul",
};

const HEBREW_ORTHOGRAPHIC_WORD =
  /[\u05D0-\u05EA](?:[\u0591-\u05BD\u05BF\u05C1-\u05C2\u05C4-\u05C5\u05C7\u05D0-\u05EA\u05F3-\u05F4])*/gu;
const HEBREW_LETTER = /[\u05D0-\u05EA]/u;
const HEBREW_VOWEL_MARKS = [
  "\u05B1",
  "\u05B2",
  "\u05B3",
  "\u05B4",
  "\u05B5",
  "\u05B6",
  "\u05B7",
  "\u05B8",
  "\u05B9",
  "\u05BA",
  "\u05BB",
  "\u05C7",
  "\u05B0",
] as const;

interface HebrewCluster {
  base: string;
  marks: Set<string>;
}

function hebrewClusters(word: string): HebrewCluster[] {
  const clusters: HebrewCluster[] = [];
  let current: HebrewCluster | undefined;
  for (const character of word.normalize("NFD")) {
    if (HEBREW_LETTER.test(character)) {
      if (current) clusters.push(current);
      current = { base: character, marks: new Set<string>() };
      continue;
    }
    const codePoint = character.codePointAt(0) ?? 0;
    if (
      current &&
      codePoint >= 0x0591 &&
      codePoint <= 0x05c7 &&
      !(codePoint >= 0x0591 && codePoint <= 0x05af)
    ) {
      current.marks.add(character);
    }
  }
  if (current) clusters.push(current);
  return clusters;
}

function hebrewVowelMark(marks: Set<string>): string | undefined {
  return HEBREW_VOWEL_MARKS.find((mark) => marks.has(mark));
}

function isHebrewMater(clusters: HebrewCluster[], index: number): boolean {
  const { base, marks } = clusters[index];
  const vowel = hebrewVowelMark(marks);
  if (base === "ו" && (marks.has("\u05B9") || marks.has("\u05BA"))) {
    return true;
  }
  // Shureq is encoded as waw + U+05BC. A dagesh on any other letter does not
  // count as a vowel.
  if (base === "ו" && marks.has("\u05BC") && !vowel) return true;
  if (index === 0) return false;

  const previousVowel = hebrewVowelMark(clusters[index - 1].marks);
  if (
    base === "י" &&
    !vowel &&
    ["\u05B4", "\u05B5", "\u05B6"].includes(previousVowel ?? "")
  ) {
    return true;
  }
  return base === "ה" &&
    index === clusters.length - 1 &&
    !marks.has("\u05BC") &&
    !vowel &&
    ["\u05B5", "\u05B6", "\u05B8", "\u05B9", "\u05BA"].includes(
      previousVowel ?? "",
    );
}

function normalizedHebrewLetters(word: string): string {
  return [...word.normalize("NFD")].filter((character) =>
    HEBREW_LETTER.test(character)
  ).join("");
}

/**
 * Requires every internal consonantal cluster to carry a vowel/silent-shewa
 * mark or participate in a recognized mater construction. Final closed
 * consonants, normal matres, shureq, and the traditional YHWH spelling remain
 * valid; a single vowel elsewhere in a partly pointed word is not enough.
 */
// 幾個名字的馬所拉寫法本身就有不帶母音的字母，那是文本的樣子而不是漏標：
// יִשָּׂשכָר（以薩迦）中間那個 שׂ 不發音，是這個名字有名的怪拼法。照經文抄下來
// 就會長這樣，把它判成「未標母音」等於要求資料比馬所拉本更整齊。比對輔音骨架。
const HEBREW_DEFECTIVE_SPELLINGS = new Set(["יששכר"]);

export function isFullyPointedHebrewWord(word: string): boolean {
  const letters = normalizedHebrewLetters(word);
  if (letters === "יהוה") return true;
  if (HEBREW_DEFECTIVE_SPELLINGS.has(letters)) return true;
  const clusters = hebrewClusters(word);
  if (!clusters.length) return false;

  for (let index = 0; index < clusters.length; index += 1) {
    const { base, marks } = clusters[index];
    const vowel = hebrewVowelMark(marks);
    const isShureq = base === "ו" && marks.has("\u05BC") && !vowel;
    const isFinal = index === clusters.length - 1;
    const previousVowel = index > 0
      ? hebrewVowelMark(clusters[index - 1].marks)
      : undefined;
    const isUnpointedAlephAfterVowel =
      base === "א" && !vowel && Boolean(previousVowel);
    const next = clusters[index + 1];
    const nextVowel = next ? hebrewVowelMark(next.marks) : undefined;
    const nextIsWawVowel = Boolean(
      next &&
      next.base === "ו" &&
      (
        next.marks.has("\u05B9") ||
        next.marks.has("\u05BA") ||
        (next.marks.has("\u05BC") && !nextVowel)
      ),
    );

    if (
      vowel ||
      isShureq ||
      isFinal ||
      nextIsWawVowel ||
      isUnpointedAlephAfterVowel ||
      isHebrewMater(clusters, index)
    ) {
      continue;
    }
    return false;
  }
  return true;
}

export function resolveOriginalReaderCorpusVersion(
  versionCode: string,
): CorpusVersionCode | undefined {
  return CORPUS_VERSION_ALIASES[versionCode.trim().toLowerCase()];
}

export function findUnpointedHebrewWords(sourceText: string): string[] {
  const words = sourceText.match(HEBREW_ORTHOGRAPHIC_WORD) ?? [];
  return words.filter((word) => !isFullyPointedHebrewWord(word));
}

function pickChineseTranslation(
  versions: Record<string, string>,
  _preferred?: string,
): string {
  const candidates = ["cuv2010"];
  for (const code of candidates) {
    const text = versions[code]?.trim();
    if (text) return text;
  }
  return "";
}

function segmentVerseNumber(
  segment: OriginalReaderSegment,
  verseFrom?: number,
): number | undefined {
  const explicit = /:(\d+)(?:\D|$)/u.exec(segment.ref)?.[1];
  if (explicit) return Number(explicit);
  if (!Number.isInteger(segment.ordinal) || segment.ordinal < 1) return undefined;
  return (verseFrom ?? 1) + segment.ordinal - 1;
}

function normalizeSegmentOrder(
  segments: OriginalReaderSegment[],
  verseFrom?: number,
): OriginalReaderSegment[] {
  return [...segments]
    .sort((left, right) => {
      const leftVerse = segmentVerseNumber(left, verseFrom);
      const rightVerse = segmentVerseNumber(right, verseFrom);
      if (leftVerse !== undefined && rightVerse !== undefined) {
        return leftVerse - rightVerse || left.ordinal - right.ordinal;
      }
      if (leftVerse !== undefined) return -1;
      if (rightVerse !== undefined) return 1;
      return left.ordinal - right.ordinal;
    })
    .map((segment, index) => ({ ...segment, ordinal: index + 1 }));
}

export function validateOriginalReaderSegments(
  language: string,
  segments: OriginalReaderSegment[],
): string | undefined {
  if (!segments.length) return "正文沒有任何可輸出的段落。";

  const ids = new Set<string>();
  for (const segment of segments) {
    if (!segment.id.trim()) return "正文含有缺少 ID 的段落。";
    if (ids.has(segment.id)) return `正文含有重複段落 ID：${segment.id}。`;
    ids.add(segment.id);

    if (!segment.ref.trim()) return `段落 ${segment.id} 缺少經文參照。`;
    if (!segment.sourceText.trim()) {
      return `${segment.ref} 的原文仍是空白；已阻止輸出不完整正文。`;
    }

    if (language === "hbo") {
      const HebrewWords = segment.sourceText.match(HEBREW_ORTHOGRAPHIC_WORD) ?? [];
      if (!HebrewWords.length) {
        return `${segment.ref} 沒有可辨識的希伯來文正字詞。`;
      }
      const unpointed = findUnpointedHebrewWords(segment.sourceText);
      if (unpointed.length) {
        return `${segment.ref} 含未標母音的希伯來文正字詞（${unpointed.slice(0, 3).join("、")}）；已阻止以無母音文字代替正文。`;
      }
    }
  }

  return undefined;
}

interface MergeResult {
  segments: OriginalReaderSegment[];
  corpusContributed: boolean;
  supplementedSourceCount: number;
  error?: string;
}

function mergeScriptureSegments(
  selection: OriginalReaderSelection,
  ref: OriginalReaderScriptureRef,
  verses: BibleVerseEntry[],
  corpusVersionCode: CorpusVersionCode,
): MergeResult {
  const manifestSegments = selection.segments ?? [];
  const manifestByVerse = new Map<number, OriginalReaderSegment>();

  for (const segment of manifestSegments) {
    const verseNumber = segmentVerseNumber(segment, ref.verseFrom);
    if (verseNumber === undefined) continue;
    if (manifestByVerse.has(verseNumber)) {
      return {
        segments: [],
        corpusContributed: false,
        supplementedSourceCount: 0,
        error: `manifest 內含重複的第 ${verseNumber} 節段落。`,
      };
    }
    manifestByVerse.set(verseNumber, segment);
  }

  const consumedManifest = new Set<OriginalReaderSegment>();
  const merged: OriginalReaderSegment[] = [];
  let corpusContributed = false;
  let supplementedSourceCount = 0;

  verses.forEach((verse, index) => {
    const manifest = manifestByVerse.get(verse.v);
    if (manifest) consumedManifest.add(manifest);

    const corpusSourceText = verse.t[corpusVersionCode]?.trim() || "";
    const corpusTranslation = pickChineseTranslation(
      verse.t,
      ref.translationVersionCode,
    );
    const useCorpusSource = !manifest?.sourceText.trim() && Boolean(corpusSourceText);
    const useCorpusTranslation =
      !manifest?.translationZh.trim() && Boolean(corpusTranslation);

    if (useCorpusSource) supplementedSourceCount += 1;
    if (useCorpusSource || useCorpusTranslation || !manifest) {
      corpusContributed = true;
    }

    merged.push({
      ...(manifest ?? {
        id: `${selection.id}-${verse.v}`,
        ordinal: index + 1,
        ref: `${ref.bookCode} ${ref.chapter}:${verse.v}`,
        sourceText: "",
        translationZh: "",
      }),
      sourceText: manifest?.sourceText.trim()
        ? manifest.sourceText
        : corpusSourceText,
      translationZh: manifest?.translationZh.trim()
        ? manifest.translationZh
        : corpusTranslation,
      ordinal: index + 1,
    });
  });

  // Keep a deliberately authored heading or a manifest verse unavailable in
  // the corpus. The validator still rejects it if its source text is blank.
  for (const segment of manifestSegments) {
    if (!consumedManifest.has(segment)) merged.push({ ...segment });
  }

  return {
    segments: normalizeSegmentOrder(merged, ref.verseFrom),
    corpusContributed,
    supplementedSourceCount,
  };
}

function unavailable(
  selection: OriginalReaderSelection,
  warning: string,
): MaterializedReaderSelection {
  return {
    selection: { ...selection, segments: undefined },
    source: "unavailable",
    warning,
  };
}

export interface MaterializedReaderSelection {
  selection: OriginalReaderSelection;
  source: "manifest" | "bible-corpus" | "unavailable";
  warning?: string;
}

/**
 * Expands scripture-backed entries from the private Bible corpus, merging them
 * verse by verse with any authored sample. Imported source text is never
 * normalized, so WLC niqqud and cantillation survive unchanged. No segment is
 * returned until all source text, IDs, references, and Hebrew pointing pass the
 * output validator.
 */
export async function materializeOriginalReaderSelection(
  language: string,
  selection: OriginalReaderSelection,
): Promise<MaterializedReaderSelection> {
  if (!selection.scripture) {
    if (!selection.segments?.length) {
      return unavailable(selection, "本篇已列入目錄，授權原文尚待匯入。");
    }
    const segments = normalizeSegmentOrder(selection.segments);
    const validationError = validateOriginalReaderSegments(language, segments);
    if (validationError) return unavailable(selection, validationError);
    return { selection: { ...selection, segments }, source: "manifest" };
  }

  const ref = selection.scripture;
  const corpusVersionCode = resolveOriginalReaderCorpusVersion(ref.versionCode);
  if (!corpusVersionCode && !selection.segments?.length) {
    return unavailable(
      selection,
      `版本代碼 ${ref.versionCode} 尚未映射到私人聖經語料庫。`,
    );
  }

  const book = corpusVersionCode ? await loadBibleBook(ref.bookCode) : null;
  const chapterVerses = book?.chapters?.[String(ref.chapter)] ?? [];
  const selectedVerses = chapterVerses.filter((verse) =>
    (ref.verseFrom === undefined || verse.v >= ref.verseFrom) &&
    (ref.verseTo === undefined || verse.v <= ref.verseTo),
  );

  const merged: MergeResult = corpusVersionCode
    ? mergeScriptureSegments(
        selection,
        ref,
        selectedVerses,
        corpusVersionCode,
      )
    : {
        segments: normalizeSegmentOrder(
          selection.segments ?? [],
          ref.verseFrom,
        ),
        corpusContributed: false,
        supplementedSourceCount: 0,
      };

  if (merged.error) return unavailable(selection, merged.error);
  if (!merged.segments.length) {
    return unavailable(
      selection,
      `私人語料庫尚無 ${corpusVersionCode ?? ref.versionCode} 的這一章。`,
    );
  }

  if (ref.verseFrom !== undefined && ref.verseTo !== undefined) {
    const covered = new Set(
      merged.segments
        .map((segment) => segmentVerseNumber(segment, ref.verseFrom))
        .filter((verse): verse is number => verse !== undefined),
    );
    const missing: number[] = [];
    for (let verse = ref.verseFrom; verse <= ref.verseTo; verse += 1) {
      if (!covered.has(verse)) missing.push(verse);
    }
    if (missing.length) {
      return unavailable(
        selection,
        `指定範圍缺少第 ${missing.join("、")} 節；已阻止輸出不完整正文。`,
      );
    }
  }

  const validationError = validateOriginalReaderSegments(
    language,
    merged.segments,
  );
  if (validationError) return unavailable(selection, validationError);

  const warning = selection.segments?.length && merged.supplementedSourceCount
    ? `已與私人聖經語料庫逐節合併，補入或補齊 ${merged.supplementedSourceCount} 節原文。`
    : undefined;

  return {
    selection: { ...selection, segments: merged.segments },
    source: merged.corpusContributed ? "bible-corpus" : "manifest",
    warning,
  };
}
