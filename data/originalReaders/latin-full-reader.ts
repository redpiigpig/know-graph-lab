import masterJson from "../../output/source-cache/original-readers/latin-full/latin-reader-two-volumes.json";
import interlinearJson from "../../output/source-cache/original-readers/latin-full/interlinear.json";
import exerciseSetV1Json from "../../output/source-cache/original-readers/latin-full/exercise-set-v1.json";
import exerciseSetV2Json from "../../output/source-cache/original-readers/latin-full/exercise-set-v2.json";

import { groupAppendixEntries } from "./appendixGroups";

// The Latin master is assembled once by scripts/build_latin_reader_data.py and
// every surface reads that one file, so this module only types and slices it.
// It deliberately re-derives nothing: if a count looks wrong here, the master is
// wrong, and computing around it here would hide that.
//
// Two volumes of fifty lessons, so a lesson is identified by both numbers. The
// route key is "v1-12"; a bare number resolves to the first volume.

export interface LatinVocabularyEntry {
  headword: string;
  forms: string;
  pos: string;
  glossZh: string;
  glossEn: string;
  ecclesiastical: boolean;
  attested: boolean;
}

export interface LatinMemoryUnit {
  ref: string;
  text: string;
  zh: string;
  readableFrom: number;
  tokens?: LatinToken[];
}

export interface LatinToken {
  word: string;
  trailing: string;
  glossZh: string;
}

export interface LatinReadingRow {
  latin: string;
  zh: string;
  // 逐詞對譯層（scripts/build_latin_interlinear.py）。還沒跑到的行是空陣列，
  // 頁面就照舊印整行拉丁文——缺就要看得出來缺，不要用整行中譯冒充。
  tokens?: LatinToken[];
}

/** One of the ten translation exercises of a lesson, as the reader shows it. */
export interface LatinExerciseItem {
  no: number;
  kind: "quoted" | "composed";
  /** Latin only.  A Chinese line here would be the answer to the question. */
  text: string;
  /** Where an anchored sentence comes from; null for a composed one. */
  ref: string | null;
  targetWords: Array<{ ordinal: number; headword: string }>;
}

export interface LatinLessonExercises {
  itemCount: number;
  quotedCount: number;
  composedCount: number;
  /** Why a lesson falls short: no quotable source, or words absent from the corpus. */
  note: string;
  coverage: { lessonWords: number; practised: number; notAttested: number };
  items: LatinExerciseItem[];
}

export interface LatinLesson {
  lesson: number;
  title: string;
  note: string;
  vocabulary: LatinVocabularyEntry[];
  memoryUnits: LatinMemoryUnit[];
  exercises: LatinLessonExercises;
  reading: LatinReadingRow[];
  readingWords: number;
}

export interface LatinVolume {
  volume: number;
  slug: string;
  name: string;
  title: string;
  blurb: string;
  counts: {
    words: number;
    memoryUnits: number;
    readingWords: number;
    lessonsMissingMemory: number[];
  };
  lessons: LatinLesson[];
  appendices: Record<string, { title: string; entries: Record<string, unknown>[] }>;
}

interface LatinMaster {
  schemaVersion: string;
  generatedOn: string;
  title: string;
  pronunciation: string;
  colophon: { label: string; text: string }[];
  volumes: LatinVolume[];
  terminal: {
    title: string;
    latinTitle: string;
    belongsTo: number;
    extent: string;
    translationNote: string;
    segments: LatinReadingRow[];
  };
}

interface RawExerciseItem {
  no: number;
  kind: string;
  text: string;
  ref?: string;
  targetWords?: Array<{ ordinal: number; headword: string }>;
}

interface RawExerciseLesson {
  lesson: number;
  note?: string;
  items: RawExerciseItem[];
  coverage?: { lessonWords: number; practised: number; notAttested?: unknown[] };
}

interface ExerciseSetMaster {
  direction: string;
  itemsPerLesson: number;
  volume: number;
  lessons: RawExerciseLesson[];
}

const master = masterJson as unknown as LatinMaster;

const exerciseSets: Record<number, ExerciseSetMaster> = {
  1: exerciseSetV1Json as unknown as ExerciseSetMaster,
  2: exerciseSetV2Json as unknown as ExerciseSetMaster,
};

const exerciseBlocks = new Map<string, RawExerciseLesson>();

function fail(message: string): never {
  throw new Error(`[latin-full-reader] ${message}`);
}

/**
 * Bind each exercise block to the lesson whose words it practises.
 *
 * On vocabulary ordinal, never on the lesson number the exercise file carries.
 * A lesson number is an output of the reading plan's sort; the ordinal is the
 * word's own identity, and this reader has already been bitten once by keying
 * on the former (see references/silent-failures.md §1).
 */
function bindExercises(): Map<string, RawExerciseLesson> {
  if (exerciseBlocks.size) return exerciseBlocks;
  const bound = new Map<string, RawExerciseLesson>();
  for (const volume of master.volumes) {
    const set = exerciseSets[volume.volume];
    if (!set) fail(`第 ${volume.volume} 冊沒有練習題主檔`);
    if (set.direction !== "original-to-chinese") fail(`第 ${volume.volume} 冊練習題不是原文譯中文`);
    if (set.itemsPerLesson !== 10) fail(`第 ${volume.volume} 冊練習題不是每課十題`);
    if (set.lessons.length !== volume.lessons.length) {
      fail(`第 ${volume.volume} 冊練習題 ${set.lessons.length} 課，讀本 ${volume.lessons.length} 課`);
    }
    const byOrdinal = new Map<number, number>();
    volume.lessons.forEach((lesson, index) => {
      lesson.vocabulary.forEach((_entry, slot) => {
        byOrdinal.set(index * 20 + slot + 1, lesson.lesson);
      });
    });
    for (const block of set.lessons) {
      const hosts = new Set<number>();
      for (const item of block.items) {
        for (const word of item.targetWords || []) {
          const host = byOrdinal.get(word.ordinal);
          if (host === undefined) {
            fail(`第 ${volume.volume} 冊練習題的第 ${word.ordinal} 詞不在詞表內`);
          }
          hosts.add(host);
        }
      }
      if (hosts.size !== 1) {
        fail(`第 ${volume.volume} 冊練習題第 ${block.lesson} 課橫跨課次 ${[...hosts].sort().join("、")}`);
      }
      const key = latinLessonKey(volume.volume, [...hosts][0]);
      if (bound.has(key)) fail(`${key} 被兩組練習題認領`);
      bound.set(key, block);
    }
  }
  for (const [key, block] of bound) exerciseBlocks.set(key, block);
  return exerciseBlocks;
}

function exercisesFor(volume: number, lesson: number): LatinLessonExercises {
  const block = bindExercises().get(latinLessonKey(volume, lesson));
  if (!block) fail(`第 ${volume} 冊第 ${lesson} 課沒有練習題`);
  const items: LatinExerciseItem[] = block.items.map((item) => ({
    no: item.no,
    kind: item.kind === "quoted" ? "quoted" : "composed",
    text: item.text,
    // Only the reference travels.  `answerKeyRef` and the composed drafts' own
    // Chinese stay in the data layer, where an answer booklet can reach them;
    // neither is sent to a page that prints the exercise.
    ref: item.kind === "quoted" ? item.ref || null : null,
    targetWords: (item.targetWords || []).map((word) => ({
      ordinal: word.ordinal,
      headword: word.headword,
    })),
  }));
  return {
    itemCount: items.length,
    quotedCount: items.filter((item) => item.kind === "quoted").length,
    composedCount: items.filter((item) => item.kind === "composed").length,
    note: (block.note || "").trim(),
    coverage: {
      lessonWords: block.coverage?.lessonWords ?? 0,
      practised: block.coverage?.practised ?? 0,
      notAttested: (block.coverage?.notAttested || []).length,
    },
    items,
  };
}

const interlinear = (interlinearJson as { units?: Record<string, { tokens: LatinToken[] }> }).units || {};

/** 逐詞對譯掛回一課的讀文與背誦；鍵是 build_latin_interlinear.py 寫的那一個。 */
function withInterlinear(volume: number, lesson: LatinLesson): LatinLesson {
  const key = latinLessonKey(volume, lesson.lesson);
  return {
    ...lesson,
    exercises: exercisesFor(volume, lesson.lesson),
    reading: lesson.reading.map((row, index) => ({
      ...row,
      tokens: interlinear[`reading:${key}:${index + 1}`]?.tokens || [],
    })),
    memoryUnits: lesson.memoryUnits.map((unit, index) => ({
      ...unit,
      tokens: interlinear[`memory:${key}:${index + 1}`]?.tokens || [],
    })),
  };
}

export function latinLessonKey(volume: number, lesson: number): string {
  return `v${volume}-${lesson}`;
}

export function parseLatinLessonKey(raw: string): { volume: number; lesson: number } | null {
  const compound = /^v(\d)-(\d{1,2})$/u.exec(raw);
  if (compound) return { volume: Number(compound[1]), lesson: Number(compound[2]) };
  if (/^\d{1,2}$/u.test(raw)) return { volume: 1, lesson: Number(raw) };
  return null;
}

export function getLatinLesson(volume: number, lesson: number): LatinLesson | null {
  const found = master.volumes.find((entry) => entry.volume === volume);
  const match = found?.lessons.find((entry) => entry.lesson === lesson);
  return match ? withInterlinear(volume, match) : null;
}

export function listLatinVolumes() {
  return master.volumes.map((volume) => ({
    volume: volume.volume,
    slug: volume.slug,
    name: volume.name,
    title: volume.title,
    blurb: volume.blurb,
    counts: volume.counts,
    lessons: volume.lessons.map((lesson) => ({
      lesson: lesson.lesson,
      title: lesson.title,
      words: lesson.vocabulary.length,
      memoryUnits: lesson.memoryUnits.length,
      exercises: exercisesFor(volume.volume, lesson.lesson).itemCount,
      readingWords: lesson.readingWords,
      href: `/original-readers/lat-lessons/${latinLessonKey(volume.volume, lesson.lesson)}`,
    })),
  }));
}

// What is not finished is part of the overview, not a footnote to it. A reader
// that shows only its completed parts invites someone to treat a draft as a
// release, which is exactly the mistake this series keeps guarding against.
export function getLatinReaderOverview() {
  const volumes = listLatinVolumes();
  const glossed = master.volumes.reduce(
    (total, volume) =>
      total + volume.lessons.reduce(
        (count, lesson) => count + lesson.vocabulary.filter((word) => word.glossZh).length,
        0,
      ),
    0,
  );
  const untranslated = master.volumes.reduce(
    (total, volume) =>
      total + volume.lessons.reduce(
        (count, lesson) => count + lesson.reading.filter((row) => !row.zh).length,
        0,
      ),
    0,
  );
  const missingMemory = master.volumes.flatMap((volume) =>
    volume.counts.lessonsMissingMemory.map((lesson) => `${volume.name} 第 ${lesson} 課`),
  );

  const openProblems: string[] = [];
  if (glossed < 2000) openProblems.push(`繁體中文詞義 ${glossed}／2000，尚未補完`);
  if (untranslated) openProblems.push(`讀本尚有 ${untranslated} 段未附中譯`);
  if (missingMemory.length) {
    openProblems.push(`記憶單元不足兩句的課：${missingMemory.slice(0, 6).join("、")}` +
      (missingMemory.length > 6 ? ` 等 ${missingMemory.length} 課` : ""));
  }
  openProblems.push("全書譯文與詞義尚未經人工覆核");

  return {
    title: master.title,
    subtitle: "上冊《武加大譯本》・下冊《從教父到教廷》，兩冊各五十課、每課二十詞",
    pronunciation: master.pronunciation,
    generatedOn: master.generatedOn,
    colophon: master.colophon,
    volumes,
    glossProgress: { glossed, target: 2000, complete: glossed >= 2000 },
    audioStatus: {
      label: "音訊：初版朗讀",
      policy: "以合成語音製作，僅供辨音參考；正式版須錄製真人羅馬式教會發音，本軌不作為發行音軌。",
    },
    terminal: {
      ...master.terminal,
      href: "/original-readers/lat-lessons/terminal",
      segmentCount: master.terminal.segments.length,
    },
    openProblems,
  };
}

export function getLatinAppendices(volume: number) {
  const found = master.volumes.find((entry) => entry.volume === volume);
  return found ? found.appendices : {};
}

export function getLatinAppendixTables() {
  // 兩冊各有自己的附錄，與希臘那本（五張表索引全書）不同，所以按冊分開列。
  return {
    title: master.title,
    note: "各冊附錄。專名表按九類分節，其餘各表依原有分組，次序與紙本讀本相同。中文用思高本。",
    volumes: master.volumes.map((volume) => ({
      volume: volume.volume,
      title: volume.title,
      tables: Object.entries(volume.appendices).map(([key, table]) => ({
        key: `v${volume.volume}-${key}`,
        title: table.title,
        entryCount: table.entries.length,
        groups: groupAppendixEntries(table.entries).map((group) => ({
          title: group.title,
          entries: group.entries.map((entry) => ({
            headword: String(entry.forms ?? entry.headword ?? ""),
            // 中文缺就留空。先前印表程式退到 glossEn，於是一本繁體中文讀本的
            // 附錄印出整頁英文；缺就該看得出來缺。
            zh: String(entry.zh ?? entry.glossZh ?? ""),
            frequency:
              typeof entry.vulgateFrequency === "number"
                ? entry.vulgateFrequency
                : typeof entry.corpusFrequency === "number"
                  ? entry.corpusFrequency
                  : null,
          })),
        })),
      })),
    })),
  };
}

export function getLatinTerminal() {
  return master.terminal;
}
