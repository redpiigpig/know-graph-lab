import { createHash } from "node:crypto";

import readingsJson from "../../output/source-cache/original-readers/japanese-full/readings.json";
import interlinearJson from "../../output/source-cache/original-readers/japanese-full/interlinear.json";
import senseJson from "../../output/source-cache/original-readers/japanese-full/unit-sense.json";
import vocabularyJson from "./vocabulary/japanese-2000.json";
import exerciseSetJson from "../../output/source-cache/original-readers/japanese-full/exercise-set.json";

// The Japanese reader was print-only until 2026-09-16 — four bound volumes and
// no web layer at all — so this module is the whole of it.  It reads the same
// four files the typesetter reads and slices them; it re-derives nothing, so a
// count that looks wrong here is wrong in the master rather than here.
//
// Two numbering systems meet in this file and must never be confused.  The
// reader is 第一冊／第二冊 (never 上下冊 — the owner's wording), each of fifty
// lessons; the vocabulary, the corpus gate and the exercise set all count
// straight through from 1 to 100.  A route key carries both: "v2-7" is the
// seventh lesson of the second volume, which is lesson 57 to the exercise set.

export interface JapaneseVocabularyEntry {
  ordinal: number;
  volume: number;
  readerLesson: number;
  kanji: string;
  kana: string;
  /** u-biq's own pitch-break marking (は・や・い), not an accent number. */
  accentBreaks: number[];
  pos: string;
  glossZh: string;
  glossEn: string;
}

export interface JapaneseToken {
  word: string;
  trailing: string;
  glossZh: string;
}

export interface JapaneseUnit {
  id: string;
  label: string;
  text: string;
  senseZh: string;
  tokens: JapaneseToken[];
}

/** One of the ten translation exercises of a lesson, as the reader shows it. */
export interface JapaneseExerciseItem {
  no: number;
  kind: "quoted" | "composed";
  /** Japanese only.  A Chinese line here would be the answer to the question. */
  text: string;
  /** Where a quoted sentence comes from; null for a composed one. */
  ref: string | null;
  targetWords: Array<{ ordinal: number; headword: string }>;
}

export interface JapaneseLessonExercises {
  itemCount: number;
  quotedCount: number;
  composedCount: number;
  /** Why a lesson falls short: no quotable source, or words the tokeniser cannot return. */
  note: string;
  coverage: { lessonWords: number; practised: number; notAttested: number };
  items: JapaneseExerciseItem[];
}

export interface JapaneseLesson {
  volume: number;
  lesson: number;
  key: string;
  title: string;
  author: string;
  orthography: string;
  extent: string;
  sourceUrl: string;
  chars: number;
  vocabulary: JapaneseVocabularyEntry[];
  memoryUnits: JapaneseUnit[];
  exercises: JapaneseLessonExercises;
  reading: JapaneseUnit[];
}

export interface JapaneseLessonSummary {
  volume: number;
  lesson: number;
  key: string;
  title: string;
  author: string;
  orthography: string;
  extent: string;
  chars: number;
  vocabularyCount: number;
  memoryUnitCount: number;
  exerciseCount: number;
  glossedCount: number;
  href: string;
}

interface RawLesson {
  lesson: number;
  workId: string;
  title: string;
  author: string;
  orthography: string;
  extent: string;
  sourceUrl: string;
  chars: number;
  units: Array<{ id: string; label: string; text: string }>;
  memoryUnits: Array<{ label: string; text: string }>;
}

interface RawVolume {
  volume: number;
  register: string;
  lessons: RawLesson[];
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
  volume: number;
  note?: string;
  items: RawExerciseItem[];
  coverage?: { lessonWords: number; practised: number; notAttested?: unknown[] };
}

const readings = readingsJson as unknown as { volumes: RawVolume[] };
const interlinear =
  (interlinearJson as { units?: Record<string, { tokens: JapaneseToken[] }> }).units || {};
const sense = senseJson as unknown as Record<string, string>;
const vocabulary = (vocabularyJson as unknown as { entries: JapaneseVocabularyEntry[] }).entries;
const exerciseSet = exerciseSetJson as unknown as {
  direction: string;
  itemsPerLesson: number;
  lessons: RawExerciseLesson[];
};

const LESSONS_PER_VOLUME = 50;
/** 第一冊／第二冊 — never 上下冊; the owner named them and the books are printed that way. */
export const JAPANESE_VOLUME_LABELS = ["第一冊", "第二冊"] as const;

function fail(message: string): never {
  throw new Error(`[japanese-full-reader] ${message}`);
}

export function japaneseLessonKey(volume: number, lesson: number): string {
  return `v${volume}-${lesson}`;
}

export function parseJapaneseLessonKey(
  raw: string,
): { volume: number; lesson: number } | null {
  const keyed = /^v(\d+)-(\d+)$/.exec(raw.trim());
  if (keyed) return { volume: Number(keyed[1]), lesson: Number(keyed[2]) };
  // A bare number means the first volume, the way every link written before the
  // second volume existed meant it.  Same rule as Greek and Latin.
  const bare = /^(\d+)$/.exec(raw.trim());
  return bare ? { volume: 1, lesson: Number(bare[1]) } : null;
}

const exerciseBlocks = new Map<string, RawExerciseLesson>();

/**
 * Bind each exercise block to the lesson whose words it practises.
 *
 * On vocabulary ordinal and headword, never on the lesson number: the exercise
 * set counts 1–100 straight through and the printed lesson restarts at 1 in the
 * second volume, so joining on the number means doing that conversion in one
 * more place, and a conversion done wrong leaves every page looking right.
 * This is the same rule the printed book uses (`build_japanese_full_reader.py`)
 * and the same one the other three readers use.
 */
function bindExercises(): Map<string, RawExerciseLesson> {
  if (exerciseBlocks.size) return exerciseBlocks;
  if (exerciseSet.direction !== "original-to-chinese") fail("練習題不是原文譯中文");
  if (exerciseSet.itemsPerLesson !== 10) fail("練習題不是每課十題");
  const byOrdinal = new Map<number, { key: string; headword: string }>();
  for (const entry of vocabulary) {
    byOrdinal.set(entry.ordinal, {
      key: japaneseLessonKey(entry.volume, entry.readerLesson),
      headword: (entry.kanji || "").trim() || (entry.kana || "").trim(),
    });
  }
  for (const block of exerciseSet.lessons) {
    const hosts = new Set<string>();
    for (const item of block.items) {
      for (const word of item.targetWords || []) {
        const found = byOrdinal.get(word.ordinal);
        if (!found) fail(`練習題的第 ${word.ordinal} 詞不在詞表內`);
        if (found.headword !== word.headword) {
          fail(
            `練習題的第 ${word.ordinal} 詞寫作 ${word.headword}，` +
              `詞表寫作 ${found.headword}：兩邊對的不是同一個詞`,
          );
        }
        hosts.add(found.key);
      }
    }
    if (hosts.size !== 1) {
      fail(`練習題第 ${block.lesson} 課橫跨課次 ${[...hosts].sort().join("、")}`);
    }
    const key = [...hosts][0];
    if (exerciseBlocks.has(key)) fail(`${key} 被兩組練習題認領`);
    exerciseBlocks.set(key, block);
  }
  return exerciseBlocks;
}

function exercisesFor(volume: number, lesson: number): JapaneseLessonExercises {
  const block = bindExercises().get(japaneseLessonKey(volume, lesson));
  if (!block) fail(`第 ${volume} 冊第 ${lesson} 課沒有練習題`);
  const items: JapaneseExerciseItem[] = block.items.map((item) => ({
    no: item.no,
    kind: item.kind === "quoted" ? "quoted" : "composed",
    text: item.text,
    // Only the reference travels.  `answerKeyRef` and the composed drafts' own
    // Chinese stay in the data layer, where an answer booklet can reach them;
    // neither is sent to a page that prints the question.
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

function wordsFor(volume: number, lesson: number): JapaneseVocabularyEntry[] {
  return vocabulary.filter(
    (entry) => entry.volume === volume && entry.readerLesson === lesson,
  );
}

function unitFor(id: string, label: string, text: string): JapaneseUnit {
  return {
    id,
    label,
    text,
    // The whole-sentence Chinese is keyed by a hash of the sentence, not by the
    // unit id — lesson numbers move and segmentation gets redone, and an index
    // join puts one sentence's translation under another one while every page
    // still looks right.  `build_japanese_full_reader.py` joins the same way;
    // if the two ever disagreed, the book and the page would disagree silently.
    senseZh: sense[senseKey(text)] || "",
    tokens: interlinear[id]?.tokens || [],
  };
}

function senseKey(text: string): string {
  return createHash("sha256").update(text, "utf8").digest("hex").slice(0, 16);
}

function memoryId(volume: number, lesson: number, index: number): string {
  return `v${volume}-l${String(lesson).padStart(2, "0")}-m${String(index).padStart(3, "0")}`;
}

export function getJapaneseLesson(volume: number, lesson: number): JapaneseLesson | null {
  const found = readings.volumes.find((item) => item.volume === volume);
  if (!found) return null;
  const row = found.lessons.find((item) => item.lesson === lesson);
  if (!row) return null;
  return {
    volume,
    lesson,
    key: japaneseLessonKey(volume, lesson),
    title: row.title,
    author: row.author,
    orthography: row.orthography,
    extent: row.extent,
    sourceUrl: row.sourceUrl,
    chars: row.chars,
    vocabulary: wordsFor(volume, lesson),
    memoryUnits: row.memoryUnits.map((unit, index) =>
      unitFor(memoryId(volume, lesson, index + 1), unit.label, unit.text),
    ),
    exercises: exercisesFor(volume, lesson),
    reading: row.units.map((unit) => unitFor(unit.id, unit.label, unit.text)),
  };
}

function summarise(volume: RawVolume): JapaneseLessonSummary[] {
  return volume.lessons.map((row) => {
    const words = wordsFor(volume.volume, row.lesson);
    return {
      volume: volume.volume,
      lesson: row.lesson,
      key: japaneseLessonKey(volume.volume, row.lesson),
      title: row.title,
      author: row.author,
      orthography: row.orthography,
      extent: row.extent,
      chars: row.chars,
      vocabularyCount: words.length,
      memoryUnitCount: row.memoryUnits.length,
      exerciseCount: exercisesFor(volume.volume, row.lesson).itemCount,
      glossedCount: words.filter((word) => (word.glossZh || "").trim()).length,
      href: `/original-readers/ja-lessons/${japaneseLessonKey(volume.volume, row.lesson)}`,
    };
  });
}

export function listJapaneseVolumes() {
  return readings.volumes.map((volume) => ({
    volume: volume.volume,
    label: JAPANESE_VOLUME_LABELS[volume.volume - 1] || `第 ${volume.volume} 冊`,
    register: volume.register,
    lessons: summarise(volume),
  }));
}

export function listJapaneseLessons(): JapaneseLessonSummary[] {
  return readings.volumes.flatMap((volume) => summarise(volume));
}

export function getJapaneseReaderOverview() {
  const volumes = listJapaneseVolumes();
  const lessons = volumes.flatMap((volume) => volume.lessons);
  const glossed = lessons.reduce((total, lesson) => total + lesson.glossedCount, 0);
  return {
    title: "日文宗教學讀本",
    subtitle: "第一冊現代語・第二冊文語與舊字舊假名，各五十課、每課二十詞",
    languageCode: "ja",
    counts: {
      volumes: volumes.length,
      lessons: lessons.length,
      vocabulary: vocabulary.length,
      exercises: lessons.reduce((total, lesson) => total + lesson.exerciseCount, 0),
      chars: lessons.reduce((total, lesson) => total + lesson.chars, 0),
    },
    // Surfaced rather than hidden: a reader still missing part of a layer says
    // so on its own front page.
    glossProgress: {
      glossed,
      target: vocabulary.length,
      complete: glossed >= vocabulary.length,
    },
    textPolicy: [
      "詞序依《大家的日本語》課次，經 u-biq 逐課頁重建；專名不佔課內詞額，另立附錄專名表。",
      "重音欄印的是來源頁面自己的斷點（は・や・い），不是重音型編號——斷點是抓得到的事實，編號是推論。",
      "讀本一律取宗教學、宗教史或宗教典籍；詞照課本，文照領域。",
      "聖書用文語訳（明治元訳舊約、大正改訳新約，公有領域），不用口語訳或新共同訳。",
      "佛典尚未收入：素材抓得到，但訓読者與年份查不到，且混著漢文與梵文轉寫；依合約寧缺勿濫。",
    ],
    volumes,
    lessons,
  };
}

export const JAPANESE_READER_PRINT = {
  books: 4,
  pages: [394, 404, 350, 366],
  note: "紙本分四冊（第一冊 1–30、31–50 課，第二冊 1–32、33–50 課），一冊不超過 500 頁；分冊只是印刷單位，不改變課次。",
} as const;

export { LESSONS_PER_VOLUME as JAPANESE_LESSONS_PER_VOLUME };
