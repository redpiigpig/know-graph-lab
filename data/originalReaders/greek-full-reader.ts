import masterJson from "../../output/source-cache/original-readers/greek-full/greek-reader-50-lessons.json";
import liturgyJson from "../../output/source-cache/original-readers/greek-full/liturgy-chrysostom.json";

// The Greek master is assembled once by scripts/build_greek_reader_data.py and
// every surface reads that one file, so this module only types and slices it.
// It deliberately does not re-derive anything: if a count looks wrong here, the
// master is wrong, and fixing it here would hide that.

export interface GreekVocabularyEntry {
  id: string;
  ordinal: number;
  lesson: number;
  lessonSlot: number;
  printedEntry: string;
  headword: string;
  lemma: string;
  transliteration: string;
  textbookTransliteration: string;
  glossEn: string;
  glossZh: string;
  strong: string;
  isProperName: boolean;
  properNameTypes: string[];
  verification: string;
}

export interface GreekMemoryVerse {
  lesson: number;
  slot: number;
  ref: string;
  book: string;
  chapter: number;
  verse: number;
  corpus: string;
  matchMethod: string;
  wordCount: number;
  text: string;
  translationZh: string;
  matchCount: number;
  matchedCount: number;
  matchedTerms: string[];
  knownCoverage: number;
  memorabilityFlags: string[];
  selectionReason: string;
  reviewStatus: string;
}

export interface GreekReadingSegment {
  ref: string;
  sourceText: string;
  displayText: string;
  translationZh?: string;
  translationNote?: string;
  verse?: number;
  wordCount?: number;
}

export interface GreekLessonReading {
  kind: "scripture_chapter" | "patristic_reading";
  titleZh: string;
  titleGrc: string;
  difficulty: number;
  learningGoals: string[];
  wordCount: number;
  source: string;
  sourceUrl?: string;
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
}

export interface GreekLesson {
  lesson: number;
  id: string;
  title: string;
  vocabularySource: string;
  vocabularyCount: number;
  vocabulary: GreekVocabularyEntry[];
  memoryVerses: GreekMemoryVerse[];
  reading: GreekLessonReading;
}

export interface GreekLessonSummary {
  lesson: number;
  id: string;
  title: string;
  vocabularySource: string;
  vocabularyCount: number;
  memoryVerseCount: number;
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
  lessons: GreekLesson[];
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

export function getGreekLesson(lesson: number): GreekLesson | null {
  if (!Number.isInteger(lesson) || lesson < 1 || lesson > master.lessons.length) return null;
  return master.lessons.find((item) => item.lesson === lesson) ?? null;
}

export function listGreekLessons(): GreekLessonSummary[] {
  return master.lessons.map((lesson) => ({
    lesson: lesson.lesson,
    id: lesson.id,
    title: lesson.title,
    vocabularySource: lesson.vocabularySource,
    vocabularyCount: lesson.vocabularyCount,
    memoryVerseCount: lesson.memoryVerses.length,
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
    href: `/original-readers/grc-lessons/${lesson.lesson}`,
  }));
}

export function getGreekReaderOverview() {
  const lessons = listGreekLessons();
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
    liturgy: {
      title: liturgy.title,
      titleGrc: liturgy.titleGrc,
      stepCount: liturgy.summary.stepCount,
      sectionCount: liturgy.summary.sectionCount,
      href: "/original-readers/grc-lessons/liturgy",
    },
    lessons,
  };
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
    steps: liturgy.steps,
  };
}
