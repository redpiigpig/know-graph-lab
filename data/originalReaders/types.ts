export type OriginalReaderLanguage = "hbo" | "grc" | "la";

export type OriginalReaderSelectionKind =
  | "orientation"
  | "vocabulary"
  | "memory_unit"
  | "bible_chapter"
  | "prayer"
  | "creed"
  | "liturgy"
  | "haggadah"
  | "rabbinic"
  | "patristic"
  | "bridge_text"
  | "appendix";

export type OriginalReaderContentStatus =
  | "planned"
  | "source_ready"
  | "sample_ready"
  | "edited"
  | "audio_ready"
  | "complete";

export interface OriginalReaderPrintProfile {
  trim: "JIS_B5";
  widthMm: 182;
  heightMm: 257;
  marginTopMm: number;
  marginBottomMm: number;
  marginInsideMm: number;
  marginOutsideMm: number;
  mirroredMargins: true;
}

export interface OriginalReaderSource {
  edition: string;
  editor?: string;
  sourceUrl?: string;
  versionCode?: string;
  licenseNote: string;
  authorization: "private-authorized";
  checksum?: string;
}

export interface OriginalReaderScriptureRef {
  bookCode: string;
  chapter: number;
  verseFrom?: number;
  verseTo?: number;
  versionCode: string;
  translationVersionCode?: string;
  parallelGroup?: string;
}

export interface OriginalReaderAudioCue {
  tokenId?: string;
  segmentId: string;
  startMs: number;
  endMs: number;
}

export interface OriginalReaderAudioTrack {
  id: string;
  label: string;
  pronunciation: string;
  speed: "slow" | "natural" | "chant";
  role?: "reader" | "priest" | "deacon" | "assembly";
  src?: string;
  durationMs?: number;
  checksum?: string;
  cues?: OriginalReaderAudioCue[];
}

export interface OriginalReaderToken {
  id: string;
  ordinal: number;
  /** Exact form printed in the running text. For Hebrew this retains niqqud. */
  surface: string;
  /** Pointed dictionary form when the script supports pointing. */
  lemmaPointed?: string;
  /** Search/index form only; never replaces pointed Hebrew in the reader. */
  lemmaUnpointed?: string;
  normalized?: string;
  lemma: string;
  root?: string;
  reading?: string;
  /** Transliteration generated with the named textbook's published system. */
  textbookTransliteration?: string;
  transliterationSystem?: string;
  transliterationStatus?: string;
  /** Source-language lexicon gloss; kept separate from the working Chinese gloss. */
  glossEn?: string;
  glossZh: string;
  partOfSpeech?: string;
  strong?: string;
  strongs?: string[];
  isProperName?: boolean;
  properNameTypes?: string[];
  /** Exact curriculum entry when it contains more than the headword. */
  printedEntry?: string;
  sourceType?: string;
  sourceChapter?: number;
  sourcePage?: number;
  sourceOrder?: number;
  sourceOrders?: number[];
  frequency?: number;
  bbgChapter?: number;
  lesson?: number;
  lessonSlot?: number;
  productionGroup?: number;
  groupSlot?: number;
  verification?: string;
  morphology?: Record<string, string>;
  syntaxNote?: string;
}

export interface OriginalReaderSegment {
  id: string;
  ordinal: number;
  ref: string;
  sourceText: string;
  translationZh: string;
  transliteration?: string;
  literalGloss?: string;
  grammarNotes?: string[];
  textualNotes?: string[];
  tokens?: OriginalReaderToken[];
  audio?: OriginalReaderAudioTrack[];
}

export interface OriginalReaderSelection {
  id: string;
  ordinal: number;
  partId: string;
  kind: OriginalReaderSelectionKind;
  title: string;
  titleOriginal?: string;
  subtitle?: string;
  difficulty: 1 | 2 | 3 | 4;
  track: "core" | "advanced" | "reference";
  estimatedPages: number;
  status: OriginalReaderContentStatus;
  source: OriginalReaderSource;
  scripture?: OriginalReaderScriptureRef;
  segments?: OriginalReaderSegment[];
  learningGoals?: string[];
  tags?: string[];
}

export interface OriginalReaderPart {
  id: string;
  ordinal: number;
  title: string;
  description: string;
}

export interface OriginalReaderVolume {
  id: string;
  slug: OriginalReaderLanguage;
  language: OriginalReaderLanguage;
  title: string;
  subtitle: string;
  privateUse: true;
  rtl: boolean;
  print: OriginalReaderPrintProfile;
  pronunciationProfiles: Array<{
    id: string;
    label: string;
    description: string;
    /** Authoritative external pronunciation guide; never treated as a local audio track. */
    referenceUrl?: string;
  }>;
  textPolicy?: {
    scriptStandard: string;
    requiredMarks?: string[];
    prohibitedSubstitutions?: string[];
    notes: string;
  };
  vocabularyCurriculum?: {
    lessonCount: number;
    wordsPerLesson?: number;
    orderingRule: string;
    primarySources: string[];
    exactOrderingStatus: "verified" | "awaiting-authorized-source";
  };
  parts: OriginalReaderPart[];
  selections: OriginalReaderSelection[];
}

export const JIS_B5_READER_PROFILE: OriginalReaderPrintProfile = {
  trim: "JIS_B5",
  widthMm: 182,
  heightMm: 257,
  marginTopMm: 18,
  marginBottomMm: 20,
  marginInsideMm: 24,
  marginOutsideMm: 17,
  mirroredMargins: true,
};
