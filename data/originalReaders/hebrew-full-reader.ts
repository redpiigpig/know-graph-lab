import hebrewVocabularyJson from "./vocabulary/hebrew-1000.json";
import haggadahJson from "../../output/source-cache/original-readers/hebrew-full/haggadah-full.json";
import assembledReaderJson from "../../output/source-cache/original-readers/hebrew-full/hebrew-reader-50-lessons.json";
import reviewedGlossesJson from "../../output/source-cache/original-readers/hebrew-full/hebrew-gloss-zh-reviewed-by-lemma.json";
import prayersArticlesJson from "../../output/source-cache/original-readers/hebrew-full/prayers-articles.json";
import scripturePlanJson from "../../output/source-cache/original-readers/hebrew-full/scripture-plan.json";
import interlinearJson from "../../output/source-cache/original-readers/hebrew-full/interlinear.json";
import referenceTablesJson from "../../output/source-cache/original-readers/hebrew-full/appendix-tables.json";

export interface HebrewFullReaderAudioStatus {
  status: "not_recorded";
  label: string;
  recordedTrackCount: 0;
  policy: string;
}

export interface HebrewPronunciationReference {
  id: string;
  label: string;
  description: string;
  url: string;
  kind: "textbook_companion";
}

interface HebrewVocabularyEntry {
  ordinal: number;
  pointed: string;
  sourcePointed: string;
  unpointed: string;
  textbookTransliteration: string;
  transliterationSystem: string;
  transliterationStatus: string;
  glossEn: string;
  glossZh: string;
  sourceType: string;
  sourceChapter: number | null;
  sourceOrder: number | null;
  sourceOrders: number[];
  itemKind: string;
  frequency: number | null;
  strong: string;
  strongs: string[];
  partOfSpeech: string;
  isProperName: boolean;
  properNameTypes: string[];
  // Set only on the few name-flagged words that stay in the lessons because they
  // read as ordinary vocabulary; the value is the reason, in Chinese.
  keptInLessons?: string;
  verification: string;
  languageVariety: string;
  lesson: number;
  lessonSlot: number;
}

interface ReviewedGloss {
  strong: string;
  pointed: string;
  glossZh: string;
}

interface ScriptureVerse {
  bookCode: string;
  osisBook: string;
  chapter: number;
  verse: number;
  ref: string;
  source: string;
  version: string;
  sourceFile: string;
  sourceOsisId: string;
  wordCount?: number;
  text: string;
}

interface ScriptureChapter {
  ordinal: number;
  lessonStart: number;
  lessonEnd: number;
  bookCode: string;
  osisBook: string;
  chapter: number;
  ref: string;
  titleZh: string;
  titleHe: string;
  corpusSection: string;
  genre: string;
  difficulty: number;
  difficultyRank: number;
  source: string;
  version: string;
  sourceUrl: string;
  verseCount: number;
  wordCount: number;
  verses: ScriptureVerse[];
}

interface MemoryVerse extends ScriptureVerse {
  lesson: number;
  slot: number;
  displayReading: string;
  matchedCount: number;
  knownCoverage: number;
  selectionReason: string;
}

interface MemoryLesson {
  lesson: number;
  preferredChapterRef: string | null;
  verses: MemoryVerse[];
}

interface PrayerSegment {
  id: string;
  ordinal: number;
  kind: string;
  sourcePath: string;
  text: string;
  sourceText: string;
  editorialPointedText: string;
  translationZh: string;
  translationStatus: string;
}

interface PrayerArticle {
  ordinal: number;
  id: string;
  title_zh: string;
  title_he: string;
  source: string;
  ref: string;
  text: string;
  editorialPointedText: string;
  sourceText: string;
  fullPointingStatus: string;
  segments: PrayerSegment[];
  sourceUrl: string;
  license: string;
  privateAuthorization: string;
  summaryZh: string;
  translationStatus: string;
}

interface HaggadahSegment extends PrayerSegment {
  sourceMarkup: string;
}

interface HaggadahStep {
  ordinal: number;
  key: string;
  title_he: string;
  title_zh: string;
  ref: string;
  text: string;
  editorialPointedText: string;
  sourceText: string;
  fullPointingStatus: string;
  segments: HaggadahSegment[];
}

interface ScripturePlanMaster {
  status: string;
  source: {
    name: string;
    version: string;
    sourceUrl: string;
    license: string;
  };
  summary: {
    chapterCount: number;
    memoryVerseCount: number;
  };
  validation: { passed: boolean };
  chapters: ScriptureChapter[];
  memoryLessons: MemoryLesson[];
}

interface AssembledReaderMaster {
  releaseStatus: string;
  audio: {
    status: "not_recorded";
    recordedTrackCount: 0;
    policy: string;
  };
  sources: {
    chineseBible: {
      versionCode: string;
      titleZh: string;
      titleEn: string;
      variant: string;
      publisher: string;
      sourceUrl: string;
      rights: string;
    };
  };
  lessons: Array<{
    lesson: number;
    reading: {
      kind: string;
      verses?: Array<{
        ref: string;
        translationZh: string;
        translationCrosswalk?: Record<string, unknown>;
      }>;
    };
  }>;
}

interface ReviewedGlossMaster {
  status: string;
  keyedBy: string;
  items: ReviewedGloss[];
}

export interface HebrewReferenceTableEntry {
  glossZh: string;
  strong: string | null;
  attestation: string;
  value?: string;
  order?: string;
  note?: string;
  pointed?: string;
  transliteration?: string;
  wlcSpellingCount?: number;
  formSource?: string;
  frequency?: number;
  firstOccurrence?: string;
  lesson?: number;
  types?: string[];
  masculine?: { pointed: string; transliteration: string; wlcSpellingCount: number };
  feminine?: { pointed: string; transliteration: string; wlcSpellingCount: number };
}

export interface HebrewReferenceTableGroup {
  id: string;
  titleZh: string;
  shape: string;
  note?: string;
  source?: string;
  entries: HebrewReferenceTableEntry[];
}

export interface HebrewReferenceTable {
  id: string;
  titleZh: string;
  titleHe: string;
  intro: string;
  groups: HebrewReferenceTableGroup[];
  entryCount: number;
}

interface HebrewReferenceTableMaster {
  note: string;
  sources: Record<string, string>;
  tables: HebrewReferenceTable[];
}

interface PrayerArticleMaster {
  itemCount: number;
  pointingGapCount: number;
  pointingStatus: string;
  items: PrayerArticle[];
}

interface HaggadahMaster {
  title: string;
  title_he: string;
  source: string;
  ref: string;
  sourceUrl: string;
  versionSource: string;
  license: string;
  privateAuthorization: string;
  stepCount: number;
  segmentCount: number;
  pointingGapCount: number;
  pointingStatus: string;
  steps: HaggadahStep[];
}

export interface HebrewLessonVocabularyEntry extends HebrewVocabularyEntry {
  glossZh: string;
}

export interface HebrewMemoryVerse extends MemoryVerse {
  tokens: HebrewInterlinearToken[];
}

export interface HebrewInterlinearToken {
  /** Printed Hebrew word, niqqud intact. */
  word: string;
  /** Maqqef, sof pasuq or modern punctuation that prints after the word. */
  trailing: string;
  /** Traditional-Chinese meaning of this word in this sentence. */
  glossZh: string;
}

export interface HebrewLessonReadingSegment {
  id: string;
  ordinal: number;
  ref: string;
  text: string;
  sourceText: string;
  translationZh: string;
  /** Word-by-word Chinese layer; empty while a unit is still being glossed. */
  tokens: HebrewInterlinearToken[];
  translationCrosswalk?: Record<string, unknown>;
  translationContinuation?: boolean;
  translationRange?: string;
}

export interface HebrewLessonReading {
  kind: "scripture_chapter" | "prayer_article";
  titleZh: string;
  titleHe: string;
  ref: string;
  summaryZh: string;
  difficulty: number | null;
  genre: string;
  segmentCount: number;
  wordCount: number | null;
  pointingStatus: string;
  source: {
    edition: string;
    version?: string;
    sourceUrl: string;
    license: string;
    privateAuthorization?: string;
  };
  segments: HebrewLessonReadingSegment[];
}

export interface HebrewFullLessonSummary {
  lesson: number;
  track: "scripture" | "prayer_article";
  titleZh: string;
  titleHe: string;
  ref: string;
  difficulty: number | null;
  genre: string;
  vocabularyCount: number;
  properNameCount: number;
  memoryRefs: string[];
  readingSegmentCount: number;
  audioStatus: HebrewFullReaderAudioStatus;
}

export interface HebrewFullLesson extends HebrewFullLessonSummary {
  chineseBible: AssembledReaderMaster["sources"]["chineseBible"];
  vocabulary: HebrewLessonVocabularyEntry[];
  memoryVerses: HebrewMemoryVerse[];
  reading: HebrewLessonReading;
  pronunciationReferences: HebrewPronunciationReference[];
  previousLesson: number | null;
  nextLesson: number | null;
}

const scripturePlan = scripturePlanJson as unknown as ScripturePlanMaster;
const assembledReader = assembledReaderJson as unknown as AssembledReaderMaster;
const prayersArticles = prayersArticlesJson as unknown as PrayerArticleMaster;
const haggadah = haggadahJson as unknown as HaggadahMaster;
const reviewedGlosses = reviewedGlossesJson as unknown as ReviewedGlossMaster;
const vocabulary = hebrewVocabularyJson as unknown as HebrewVocabularyEntry[];
const referenceTables = referenceTablesJson as unknown as HebrewReferenceTableMaster;

interface InterlinearUnit {
  id: string;
  kind: string;
  ref: string;
  text: string;
  tokens: HebrewInterlinearToken[];
  senseZh: string;
}

const interlinear = (interlinearJson as unknown as { units: Record<string, InterlinearUnit> }).units;

const HEBREW_LETTER = /[א-ת]/;
const TRAILING_MARKS = /[׀׃,:;.!?。，：；]+$/;
const MAQQEF = "־";

/** Same tokenisation contract as scripts/build_hebrew_interlinear.py. */
function printedTokens(text: string): HebrewInterlinearToken[] {
  const output: HebrewInterlinearToken[] = [];
  for (const chunk of text.split(/\s+/).filter(Boolean)) {
    const pieces = chunk.split(MAQQEF);
    pieces.forEach((piece, index) => {
      const joined = index < pieces.length - 1;
      const match = piece.match(TRAILING_MARKS);
      const trailing = match ? match[0] : "";
      const word = trailing ? piece.slice(0, piece.length - trailing.length) : piece;
      if (!HEBREW_LETTER.test(word)) {
        if (output.length) output[output.length - 1].trailing += piece;
        return;
      }
      output.push({ word, trailing: trailing + (joined ? MAQQEF : ""), glossZh: "" });
    });
  }
  return output;
}

/**
 * Glossed tokens for exactly the string a page prints.  Some prayer and
 * Haggadah segments print with their Hebrew title stripped, so the printed run
 * can be a suffix of the glossed unit; align by word sequence rather than
 * assuming both layers start together.  Returns [] when the unit has not been
 * glossed yet, which the reader renders as a plain Hebrew line.
 */
function glossesFor(printedText: string, unitId: string): HebrewInterlinearToken[] {
  const record = interlinear[unitId];
  if (!record?.tokens?.length) return [];
  const printed = printedTokens(printedText);
  if (!printed.length) return [];
  const words = record.tokens.map((token) => token.word);
  const target = printed.map((token) => token.word);
  for (let offset = 0; offset <= words.length - target.length; offset += 1) {
    let matched = true;
    for (let index = 0; index < target.length; index += 1) {
      if (words[offset + index] !== target[index]) {
        matched = false;
        break;
      }
    }
    if (matched) {
      return printed.map((token, index) => ({
        ...token,
        glossZh: record.tokens[offset + index].glossZh,
      }));
    }
  }
  return [];
}

function senseFor(unitId: string): string {
  return interlinear[unitId]?.senseZh?.trim() || "";
}

export const HEBREW_FULL_READER_AUDIO_STATUS: HebrewFullReaderAudioStatus = {
  status: assembledReader.audio.status,
  label: "校訂錄音尚未匯入",
  recordedTrackCount: assembledReader.audio.recordedTrackCount,
  policy: assembledReader.audio.policy,
};

export const HEBREW_PRONUNCIATION_REFERENCES: HebrewPronunciationReference[] = [
  {
    id: "bbh2-companion",
    label: "BBH2 教材網站／發音參考",
    description: "Pratico–Van Pelt《Basics of Biblical Hebrew》教材配套入口；本課音標採同一教材系統。",
    url: "https://hebrewsyntax.org/bbh2new/",
    kind: "textbook_companion",
  },
];

let validated = false;

function invariant(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(`[hebrew-full-reader] ${message}`);
}

function validateMasters() {
  if (validated) return;
  invariant(vocabulary.length === 1000, `詞彙主檔應有 1000 詞，實得 ${vocabulary.length}`);
  invariant(reviewedGlosses.items.length === 1000, "繁中詞義覆核檔不是 1000 詞");
  invariant(scripturePlan.validation.passed, "經文章節／背誦主檔驗證未通過");
  invariant(scripturePlan.chapters.length === 25, "完整章主檔不是 25 章");
  invariant(assembledReader.lessons.length === 50, "排印主檔不是 50 課");
  invariant(assembledReader.releaseStatus === "content_complete_audio_pending", "讀本狀態未誠實標示音訊待錄");
  invariant(assembledReader.audio.status === "not_recorded", "音訊主檔狀態與實際不符");
  invariant(assembledReader.sources.chineseBible.versionCode === "cuv2010", "繁中聖經不是和合本修訂版2010");
  invariant(assembledReader.sources.chineseBible.variant === "RCUV2（上帝版）", "繁中聖經不是核定的RCUV2上帝版");
  invariant(scripturePlan.memoryLessons.length === 50, "背誦主檔不是 50 課");
  invariant(prayersArticles.items.length === 25, "禱文／文章主檔不是 25 篇");
  invariant(prayersArticles.pointingGapCount === 0, "禱文／文章排印正文仍有附點缺口");
  invariant(haggadah.steps.length === 15, "Haggadah 不是完整十五步");
  invariant(haggadah.pointingGapCount === 0, "Haggadah 排印正文仍有附點缺口");

  const glossByLemma = new Map(
    reviewedGlosses.items.map((item) => [`${item.strong}|${item.pointed}`, item.glossZh.trim()]),
  );
  for (let lesson = 1; lesson <= 50; lesson += 1) {
    const lessonVocabulary = vocabulary.filter((item) => item.lesson === lesson);
    invariant(lessonVocabulary.length === 20, `第 ${lesson} 課不是 20 詞`);
    invariant(
      lessonVocabulary.every((item, index) => item.lessonSlot === index + 1),
      `第 ${lesson} 課詞彙 slot 不連續`,
    );
    invariant(
      lessonVocabulary.every((item) => Boolean(glossByLemma.get(`${item.strong}|${item.pointed}`))),
      `第 ${lesson} 課仍有空白繁中詞義`,
    );
    const memory = scripturePlan.memoryLessons.find((item) => item.lesson === lesson);
    invariant(memory?.verses.length === 2, `第 ${lesson} 課不是 2 節背誦經文`);
  }

  scripturePlan.chapters.forEach((chapter, index) => {
    invariant(chapter.lessonStart === index + 1, `第 ${index + 1} 章未對應同號課次`);
    invariant(chapter.verses.length === chapter.verseCount, `${chapter.ref} 章節數不完整`);
    invariant(chapter.verses.every((verse) => verse.text.trim()), `${chapter.ref} 有空白經節`);
  });
  prayersArticles.items.forEach((item, index) => {
    invariant(item.ordinal === index + 1, `禱文／文章 ${index + 1} 次序不連續`);
    invariant(item.segments.length > 0, `${item.id} 沒有正文段落`);
    invariant(item.segments.every((segment) => segment.editorialPointedText.trim()), `${item.id} 有空白正文段落`);
  });
  invariant(
    haggadah.steps.reduce((total, step) => total + step.segments.length, 0) === haggadah.segmentCount,
    "Haggadah 段落總數與主檔宣告不符",
  );
  validated = true;
}

// Keyed by lemma, not by position: lifting the proper names out of the word
// list renumbered every ordinal, and a position-keyed lookup would have shifted
// all 1,000 meanings by one without any error surfacing.
function vocabularyForLesson(lesson: number): HebrewLessonVocabularyEntry[] {
  const glossByLemma = new Map(
    reviewedGlosses.items.map((item) => [`${item.strong}|${item.pointed}`, item.glossZh.trim()]),
  );
  return vocabulary
    .filter((item) => item.lesson === lesson)
    .sort((left, right) => left.lessonSlot - right.lessonSlot)
    .map((item) => {
      const glossZh = glossByLemma.get(`${item.strong}|${item.pointed}`) || "";
      invariant(glossZh, `第 ${lesson} 課的 ${item.pointed} 沒有繁中義`);
      return { ...item, glossZh };
    });
}

function memoryForLesson(lesson: number): HebrewMemoryVerse[] {
  return [...(scripturePlan.memoryLessons.find((item) => item.lesson === lesson)?.verses || [])]
    .sort((left, right) => left.slot - right.slot)
    .map((verse) => ({ ...verse, tokens: glossesFor(verse.text, `bible:${verse.ref}`) }));
}

function scriptureReading(lesson: number): HebrewLessonReading {
  const chapter = scripturePlan.chapters.find((item) => item.lessonStart === lesson);
  invariant(chapter, `找不到第 ${lesson} 課完整章`);
  const assembledLesson = assembledReader.lessons.find((item) => item.lesson === lesson);
  invariant(assembledLesson?.reading.kind === "bible_chapter", `排印主檔第 ${lesson} 課不是完整章`);
  const translationByRef = new Map(
    (assembledLesson.reading.verses || []).map((verse) => [verse.ref, verse]),
  );
  invariant(
    chapter.verses.every((verse) => Boolean(translationByRef.get(verse.ref)?.translationZh.trim())),
    `${chapter.ref} 線上對照仍有空白繁中經文`,
  );
  const seenTranslationRefs = new Set<string>();
  const segments = chapter.verses.map((verse, index) => {
    const assembledVerse = translationByRef.get(verse.ref);
    const crosswalk = assembledVerse?.translationCrosswalk;
    const translationRef = String(crosswalk?.translationRef || "");
    const translationContinuation = Boolean(
      crosswalk?.combinedVerseRange && translationRef && seenTranslationRefs.has(translationRef),
    );
    if (translationRef) seenTranslationRefs.add(translationRef);
    return {
      id: `${chapter.osisBook}-${chapter.chapter}-${verse.verse}`,
      ordinal: index + 1,
      ref: verse.ref,
      text: verse.text,
      sourceText: verse.text,
      tokens: glossesFor(verse.text, `bible:${verse.ref}`),
      translationZh: assembledVerse?.translationZh.trim() || "",
      translationCrosswalk: crosswalk,
      translationContinuation,
      translationRange: String(crosswalk?.translationRange || ""),
    };
  });
  return {
    kind: "scripture_chapter",
    titleZh: chapter.titleZh,
    titleHe: chapter.titleHe,
    ref: chapter.ref,
    summaryZh: "",
    difficulty: chapter.difficulty,
    genre: chapter.genre,
    segmentCount: chapter.verses.length,
    wordCount: chapter.wordCount,
    pointingStatus: "wlc_pointed_complete",
    source: {
      edition: chapter.source,
      version: chapter.version,
      sourceUrl: chapter.sourceUrl,
      license: scripturePlan.source.license,
    },
    segments,
  };
}

function prayerReading(lesson: number): HebrewLessonReading {
  const item = prayersArticles.items[lesson - 26];
  invariant(item, `找不到第 ${lesson} 課禱文／文章`);
  return {
    kind: "prayer_article",
    titleZh: item.title_zh,
    titleHe: item.title_he,
    ref: item.ref,
    summaryZh: item.summaryZh,
    difficulty: null,
    genre: item.id.includes("article") ? "rabbinic_article" : "jewish_prayer",
    segmentCount: item.segments.length,
    wordCount: null,
    pointingStatus: item.fullPointingStatus,
    source: {
      edition: item.source,
      sourceUrl: item.sourceUrl,
      license: item.license,
      privateAuthorization: item.privateAuthorization,
    },
    segments: item.segments.map((segment) => {
      const text = segment.editorialPointedText || segment.text;
      return {
        id: segment.id,
        ordinal: segment.ordinal,
        ref: segment.sourcePath,
        text,
        sourceText: segment.sourceText,
        tokens: glossesFor(text, `prayer:${segment.id}`),
        translationZh: segment.translationZh || senseFor(`prayer:${segment.id}`),
      };
    }),
  };
}

function readingForLesson(lesson: number): HebrewLessonReading {
  return lesson <= 25 ? scriptureReading(lesson) : prayerReading(lesson);
}

export function getHebrewFullLesson(lesson: number): HebrewFullLesson | null {
  validateMasters();
  if (!Number.isInteger(lesson) || lesson < 1 || lesson > 50) return null;
  const reading = readingForLesson(lesson);
  const lessonVocabulary = vocabularyForLesson(lesson);
  const memoryVerses = memoryForLesson(lesson);
  return {
    lesson,
    track: reading.kind === "scripture_chapter" ? "scripture" : "prayer_article",
    titleZh: reading.titleZh,
    titleHe: reading.titleHe,
    ref: reading.ref,
    difficulty: reading.difficulty,
    genre: reading.genre,
    vocabularyCount: lessonVocabulary.length,
    properNameCount: lessonVocabulary.filter((item) => item.isProperName).length,
    memoryRefs: memoryVerses.map((verse) => verse.ref),
    readingSegmentCount: reading.segmentCount,
    audioStatus: HEBREW_FULL_READER_AUDIO_STATUS,
    chineseBible: assembledReader.sources.chineseBible,
    vocabulary: lessonVocabulary,
    memoryVerses,
    reading,
    pronunciationReferences: HEBREW_PRONUNCIATION_REFERENCES,
    previousLesson: lesson > 1 ? lesson - 1 : null,
    nextLesson: lesson < 50 ? lesson + 1 : null,
  };
}

export function listHebrewFullLessons(): HebrewFullLessonSummary[] {
  validateMasters();
  return Array.from({ length: 50 }, (_, index) => {
    const lesson = getHebrewFullLesson(index + 1);
    invariant(lesson, `找不到第 ${index + 1} 課`);
    const {
      vocabulary: _vocabulary,
      memoryVerses: _memoryVerses,
      reading: _reading,
      chineseBible: _chineseBible,
      pronunciationReferences: _pronunciationReferences,
      previousLesson: _previousLesson,
      nextLesson: _nextLesson,
      ...summary
    } = lesson;
    return summary;
  });
}

export function getHebrewFullReaderOverview() {
  validateMasters();
  return {
    title: "希伯來文原文讀本・50課私人線上版",
    subtitle: "每課20詞、2節背誦與1篇完整主讀文，共1,000詞；詞序依 BBH2 第3–35章，其後接語料頻率延伸。第1–25課讀完整聖經章，第26–50課讀禱文與拉比文章。人名地名等專名不佔課內詞額，另立分類專名表。",
    language: "hbo",
    rtl: true,
    privateUse: true,
    chineseBible: assembledReader.sources.chineseBible,
    counts: {
      lessons: 50,
      vocabulary: 1000,
      memoryVerses: 100,
      scriptureChapters: 25,
      prayersArticles: 25,
      haggadahSteps: haggadah.stepCount,
      haggadahSegments: haggadah.segmentCount,
    },
    audioStatus: HEBREW_FULL_READER_AUDIO_STATUS,
    pronunciationReferences: HEBREW_PRONUNCIATION_REFERENCES,
    haggadah: {
      titleZh: haggadah.title,
      titleHe: haggadah.title_he,
      href: "/original-readers/hbo-lessons/haggadah",
      stepCount: haggadah.stepCount,
      segmentCount: haggadah.segmentCount,
      pointingStatus: haggadah.pointingStatus,
    },
    referenceTables: referenceTables.tables.map((table) => ({
      id: table.id,
      titleZh: table.titleZh,
      titleHe: table.titleHe,
      groupCount: table.groups.length,
      entryCount: table.entryCount,
      href: `/original-readers/hbo-lessons/tables#${table.id}`,
    })),
    lessons: listHebrewFullLessons(),
  };
}

export function getHebrewReferenceTables() {
  validateMasters();
  return {
    titleZh: "附錄參考表",
    sources: referenceTables.sources,
    note: referenceTables.note,
    tables: referenceTables.tables,
  };
}

export function getHebrewFullHaggadah() {
  validateMasters();
  return {
    titleZh: haggadah.title,
    titleHe: haggadah.title_he,
    ref: haggadah.ref,
    stepCount: haggadah.stepCount,
    segmentCount: haggadah.segmentCount,
    pointingStatus: haggadah.pointingStatus,
    source: {
      edition: haggadah.source,
      sourceUrl: haggadah.sourceUrl,
      versionSource: haggadah.versionSource,
      license: haggadah.license,
      privateAuthorization: haggadah.privateAuthorization,
    },
    audioStatus: HEBREW_FULL_READER_AUDIO_STATUS,
    pronunciationReferences: HEBREW_PRONUNCIATION_REFERENCES,
    steps: haggadah.steps.map((step) => ({
      ordinal: step.ordinal,
      key: step.key,
      titleZh: step.title_zh,
      titleHe: step.title_he,
      ref: step.ref,
      text: step.editorialPointedText || step.text,
      sourceText: step.sourceText,
      pointingStatus: step.fullPointingStatus,
      segments: step.segments.map((segment) => {
        const text = segment.editorialPointedText || segment.text;
        return {
          id: segment.id,
          ordinal: segment.ordinal,
          ref: segment.sourcePath,
          text,
          sourceText: segment.sourceText,
          tokens: glossesFor(text, `haggadah:${segment.id}`),
          translationZh: segment.translationZh || senseFor(`haggadah:${segment.id}`),
        };
      }),
    })),
  };
}
