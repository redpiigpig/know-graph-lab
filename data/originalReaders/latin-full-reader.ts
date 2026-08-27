import masterJson from "../../output/source-cache/original-readers/latin-full/latin-reader-two-volumes.json";

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
}

export interface LatinReadingRow {
  latin: string;
  zh: string;
}

export interface LatinLesson {
  lesson: number;
  title: string;
  note: string;
  vocabulary: LatinVocabularyEntry[];
  memoryUnits: LatinMemoryUnit[];
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

const master = masterJson as unknown as LatinMaster;

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
  return found?.lessons.find((entry) => entry.lesson === lesson) || null;
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
