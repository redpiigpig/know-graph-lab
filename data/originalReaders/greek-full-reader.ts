import masterJson from "../../output/source-cache/original-readers/greek-full/greek-reader-two-volumes.json";
import liturgyJson from "../../output/source-cache/original-readers/greek-full/liturgy-chrysostom.json";
import interlinearJson from "../../output/source-cache/original-readers/greek-full/interlinear.json";

// The Greek master is assembled once by scripts/build_greek_reader_data.py and
// every surface reads that one file, so this module only types and slices it.
// It deliberately does not re-derive anything: if a count looks wrong here, the
// master is wrong, and fixing it here would hide that.
//
// The reader is two volumes of fifty lessons, so a lesson is identified by both
// numbers.  The route key is "v1-12"; a bare number still resolves, to the first
// volume, because that is what every link written before the second volume
// existed means.

export interface GreekVocabularyEntry {
  id: string;
  volume: number;
  ordinal: number;
  corpus: string;
  lesson: number;
  lessonSlot: number;
  printedEntry: string;
  headword: string;
  lemma: string;
  transliteration: string;
  textbookTransliteration: string;
  transliterationSystem: string;
  transliterationStatus: string;
  glossEn: string;
  glossZh: string;
  strong: string;
  frequency: number;
  withinKoine: boolean;
  isProperName: boolean;
  properNameTypes: string[];
  verification: string;
}

export interface GreekMemoryUnit {
  kind: "verse" | "sentence";
  lesson: number;
  slot: number;
  ref: string;
  corpus?: string;
  category?: string;
  book?: string;
  chapter?: number;
  verse?: number;
  readingTitleZh?: string;
  segmentRef?: string;
  matchMethod: string;
  wordCount: number;
  text: string;
  translationZh: string;
  matchCount: number;
  matchedCount: number;
  matchedTerms: string[];
  tokens?: GreekInterlinearToken[];
  knownCoverage: number;
  memorabilityFlags: string[];
  selectionReason: string;
  reviewStatus: string;
}

export interface GreekInterlinearToken {
  word: string;
  trailing: string;
  glossZh: string;
}

export interface GreekReadingSegment {
  ref: string;
  sourceText: string;
  displayText: string;
  translationZh?: string;
  translationNote?: string;
  verse?: number;
  wordCount?: number;
  tokens?: GreekInterlinearToken[];
}

export interface GreekLessonReading {
  kind: "scripture_chapter" | "patristic_reading";
  ordinal?: number;
  titleZh: string;
  titleGrc: string;
  difficulty: number;
  learningGoals: string[];
  wordCount: number;
  source: string;
  sourceUrl?: string;
  license?: string;
  corpusLabel?: string;
  categoryLabel?: string;
  author?: string;
  completeness?: string;
  extent?: string;
  ref?: string;
  verseCount?: number;
  segmentCount?: number;
  verses?: GreekReadingSegment[];
  segments?: GreekReadingSegment[];
  absentVerses?: { verse: number; ref: string; note: string }[];
  numberingNote?: string;
  verseNumberingNote?: string;
  canonNumbers?: string[];
  canonTotal?: number;
}

export interface GreekLesson {
  volume: number;
  lesson: number;
  id: string;
  title: string;
  vocabularySource: string;
  vocabularyCount: number;
  vocabulary: GreekVocabularyEntry[];
  memoryUnits: GreekMemoryUnit[];
  reading: GreekLessonReading;
}

export interface GreekLessonSummary {
  volume: number;
  lesson: number;
  key: string;
  id: string;
  title: string;
  vocabularySource: string;
  vocabularyCount: number;
  memoryUnitCount: number;
  memoryUnitKind: string;
  glossedCount: number;
  reading: {
    kind: GreekLessonReading["kind"];
    titleZh: string;
    titleGrc: string;
    difficulty: number;
    label: string;
    completeness: string;
    wordCount: number;
  };
  href: string;
}

interface GreekVolume {
  volume: number;
  slug: string;
  title: string;
  subtitle: string;
  memoryUnitKind: "verse" | "sentence";
  corpusByHalf: Record<string, string>;
  counts: Record<string, number>;
  lessons: GreekLesson[];
  appendices: {
    kind: string;
    key: string;
    title: string;
    titleGrc?: string;
    stepCount?: number;
    sectionCount?: number;
    placement?: string;
  }[];
}

const master = masterJson as unknown as {
  title: string;
  subtitle: string;
  languageCode: string;
  releaseStatus: string;
  textbook: string;
  counts: Record<string, number>;
  textPolicy: Record<string, string>;
  printProfile: Record<string, unknown>;
  sources: Record<string, unknown>;
  audio: { status: string; profile: string; policy: string };
  volumes: GreekVolume[];
  appendices: {
    kind: string;
    key: string;
    title: string;
    note: string;
    entryCount: number;
    entries: Record<string, unknown>[];
  }[];
  openProblems: string[];
};

const liturgy = liturgyJson as unknown as {
  title: string;
  titleGrc: string;
  placement: string;
  edition: string;
  sourceUrl: string;
  roleDerivationNote: string;
  printedTextNote: string;
  crossCheckNote: string;
  summary: { stepCount: number; wordCount: number; sectionCount: number };
  sections: { key: string; label: string; firstStep: number; lastStep: number; stepCount: number; wordCount: number }[];
  steps: {
    ordinal: number;
    section: string;
    sectionLabel: string;
    role: string;
    roleLabel: string;
    roleEvidence: string;
    kind: string;
    wordCount: number;
    displayText: string;
    repeatCount?: number;
  }[];
};

export const GREEK_READER_AUDIO_STATUS = {
  status: master.audio.status,
  label:
    master.audio.status === "not_recorded"
      ? "尚無真實錄音"
      : "已錄音並複核",
  recordedTrackCount: 0,
  profile: master.audio.profile,
  policy: master.audio.policy,
} as const;

function readingLabel(reading: GreekLessonReading): string {
  return reading.corpusLabel || reading.categoryLabel || "";
}

export function greekLessonKey(volume: number, lesson: number): string {
  return `v${volume}-${lesson}`;
}

/** Parse "v2-37", or a bare "37" written before the second volume existed. */
export function parseGreekLessonKey(raw: string): { volume: number; lesson: number } | null {
  const compound = /^v(\d)-(\d{1,2})$/u.exec(raw);
  if (compound) {
    return { volume: Number(compound[1]), lesson: Number(compound[2]) };
  }
  if (/^\d{1,2}$/u.test(raw)) {
    return { volume: 1, lesson: Number(raw) };
  }
  return null;
}

// The word-by-word layer is keyed the same way scripts/build_greek_interlinear.py
// keys it, so a segment finds its glosses by the id the builder used and nothing
// has to be re-tokenised here.  A segment with no entry simply shows no gloss
// row rather than a row of blanks.
const interlinear = (
  interlinearJson as unknown as {
    units: Record<string, { tokens: GreekInterlinearToken[]; translationZh?: string }>;
  }
).units;

function attachTokens(unitId: string, segment: GreekReadingSegment): GreekReadingSegment {
  const record = interlinear[unitId];
  if (!record?.tokens?.length) return segment;
  return {
    ...segment,
    tokens: record.tokens,
    translationZh: segment.translationZh || record.translationZh || "",
  };
}

function memoryUnitId(unit: GreekMemoryUnit): string {
  return unit.kind === "sentence" ? `sentence:${unit.ref}` : `memory:${unit.ref}`;
}

function withInterlinear(lesson: GreekLesson): GreekLesson {
  const reading = lesson.reading;
  const isScripture = reading.kind === "scripture_chapter";
  const rows = (isScripture ? reading.verses : reading.segments) || [];
  const glossed = rows.map((segment) =>
    attachTokens(
      isScripture
        ? `scripture:${segment.ref}`
        : `patristic:${reading.ordinal}:${segment.ref}`,
      segment,
    ),
  );
  return {
    ...lesson,
    memoryUnits: lesson.memoryUnits.map((unit) => ({
      ...unit,
      tokens: interlinear[memoryUnitId(unit)]?.tokens || [],
      translationZh: unit.translationZh || interlinear[memoryUnitId(unit)]?.translationZh || "",
    })),
    reading: isScripture
      ? { ...reading, verses: glossed }
      : { ...reading, segments: glossed },
  };
}

export function listGreekVolumes() {
  return master.volumes.map((volume) => ({
    volume: volume.volume,
    slug: volume.slug,
    title: volume.title,
    subtitle: volume.subtitle,
    memoryUnitKind: volume.memoryUnitKind,
    corpusByHalf: volume.corpusByHalf,
    counts: volume.counts,
    appendices: volume.appendices,
    lessons: summarise(volume),
  }));
}

function summarise(volume: GreekVolume): GreekLessonSummary[] {
  return volume.lessons.map((lesson) => ({
    volume: volume.volume,
    lesson: lesson.lesson,
    key: greekLessonKey(volume.volume, lesson.lesson),
    id: lesson.id,
    title: lesson.title,
    vocabularySource: lesson.vocabularySource,
    vocabularyCount: lesson.vocabularyCount,
    memoryUnitCount: lesson.memoryUnits.length,
    memoryUnitKind: volume.memoryUnitKind,
    glossedCount: lesson.vocabulary.filter((word) => word.glossZh.trim()).length,
    reading: {
      kind: lesson.reading.kind,
      titleZh: lesson.reading.titleZh,
      titleGrc: lesson.reading.titleGrc,
      difficulty: lesson.reading.difficulty,
      label: readingLabel(lesson.reading),
      completeness: lesson.reading.completeness || "complete",
      wordCount: lesson.reading.wordCount,
    },
    href: `/original-readers/grc-lessons/${greekLessonKey(volume.volume, lesson.lesson)}`,
  }));
}

export function getGreekLesson(volume: number, lesson: number): GreekLesson | null {
  const found = master.volumes.find((item) => item.volume === volume);
  if (!found) return null;
  const match = found.lessons.find((item) => item.lesson === lesson);
  return match ? withInterlinear(match) : null;
}

export function listGreekLessons(): GreekLessonSummary[] {
  return master.volumes.flatMap((volume) => summarise(volume));
}

export function getGreekReaderOverview() {
  const volumes = listGreekVolumes();
  const lessons = volumes.flatMap((volume) => volume.lessons);
  const glossed = lessons.reduce((total, lesson) => total + lesson.glossedCount, 0);
  return {
    title: master.title,
    subtitle: master.subtitle,
    languageCode: master.languageCode,
    textbook: master.textbook,
    releaseStatus: master.releaseStatus,
    counts: master.counts,
    textPolicy: master.textPolicy,
    audioStatus: GREEK_READER_AUDIO_STATUS,
    // Surfaced rather than hidden: a reader that is still missing its Chinese
    // gloss layer should say so on its own front page.
    glossProgress: {
      glossed,
      target: master.counts.vocabulary,
      complete: glossed >= master.counts.vocabulary,
    },
    openProblems: master.openProblems,
    appendices: master.appendices.map((table) => ({
      key: table.key,
      title: table.title,
      note: table.note,
      entryCount: table.entryCount,
    })),
    liturgy: {
      title: liturgy.title,
      titleGrc: liturgy.titleGrc,
      stepCount: liturgy.summary.stepCount,
      sectionCount: liturgy.summary.sectionCount,
      href: "/original-readers/grc-lessons/liturgy",
    },
    volumes,
    lessons,
  };
}

export function getGreekAppendix(key: string) {
  return master.appendices.find((table) => table.key === key) || null;
}

export function getGreekLiturgy() {
  return {
    title: liturgy.title,
    titleGrc: liturgy.titleGrc,
    placement: liturgy.placement,
    edition: liturgy.edition,
    sourceUrl: liturgy.sourceUrl,
    notes: {
      roleDerivation: liturgy.roleDerivationNote,
      printedText: liturgy.printedTextNote,
      crossCheck: liturgy.crossCheckNote,
    },
    summary: liturgy.summary,
    sections: liturgy.sections,
    steps: liturgy.steps.map((step) => ({
      ...step,
      tokens: interlinear[`liturgy:${step.ordinal}`]?.tokens || [],
      translationZh: interlinear[`liturgy:${step.ordinal}`]?.translationZh || "",
    })),
  };
}
