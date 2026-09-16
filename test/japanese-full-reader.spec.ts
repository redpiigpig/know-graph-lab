import { describe, expect, it } from "vitest";

import {
  getJapaneseLesson,
  getJapaneseReaderOverview,
  japaneseLessonKey,
  listJapaneseLessons,
  listJapaneseVolumes,
  parseJapaneseLessonKey,
} from "../data/originalReaders/japanese-full-reader";

// The Japanese reader was print-only until 2026-09-16, so this spec is its first
// machine check of anything. It pins the release contract's counts and the three
// rules this series has already broken once in the other readers: a lesson keyed
// by a number that moves, a translation joined by index, and an exercise printed
// beside its own answer.
describe("complete two-volume Japanese religious-studies reader", () => {
  const overview = getJapaneseReaderOverview();
  const volumes = listJapaneseVolumes();

  it("carries two volumes of fifty lessons and two thousand words", () => {
    expect(overview.counts.volumes).toBe(2);
    expect(overview.counts.lessons).toBe(100);
    expect(overview.counts.vocabulary).toBe(2000);
    for (const volume of volumes) {
      expect(volume.lessons, `第 ${volume.volume} 冊`).toHaveLength(50);
      for (const lesson of volume.lessons) {
        expect(lesson.vocabularyCount, `v${volume.volume}-${lesson.lesson}`).toBe(20);
      }
    }
  });

  it("names the volumes 第一冊／第二冊, never 上下冊", () => {
    expect(volumes.map((volume) => volume.label)).toEqual(["第一冊", "第二冊"]);
    expect(overview.subtitle).not.toContain("上冊");
    expect(overview.subtitle).not.toContain("下冊");
  });

  it("serves ten translation exercises per lesson, bound by word ordinal and carrying no Chinese", () => {
    let total = 0;
    for (const volume of volumes) {
      for (const row of volume.lessons) {
        const lesson = getJapaneseLesson(volume.volume, row.lesson)!;
        const exercises = lesson.exercises;
        expect(exercises.items, `v${volume.volume}-${row.lesson}`).toHaveLength(10);
        expect(exercises.itemCount).toBe(row.exerciseCount);
        total += exercises.items.length;

        // The join is the one thing that can be wrong while every page still
        // looks finished: ten sentences under a lesson whose words they do not
        // practise. The exercise set counts 1–100 and the printed lesson
        // restarts at 1 in the second volume, so check the words themselves.
        const headwords = new Set(
          lesson.vocabulary.map((word) => (word.kanji || "").trim() || (word.kana || "").trim()),
        );
        for (const item of exercises.items) {
          expect(item.text.trim(), `v${volume.volume}-${row.lesson} item ${item.no}`).toBeTruthy();
          expect(Object.keys(item)).not.toContain("chinese");
          expect(Object.keys(item)).not.toContain("answerKeyRef");
          expect(item.targetWords.length).toBeGreaterThan(0);
          for (const word of item.targetWords) {
            expect(headwords, `v${volume.volume}-${row.lesson} word ${word.ordinal}`)
              .toContain(word.headword);
          }
          if (item.kind === "quoted") {
            expect(item.ref, `v${volume.volume}-${row.lesson} item ${item.no}`).toBeTruthy();
          } else {
            expect(item.ref).toBeNull();
          }
        }
        // Falling short is allowed; saying nothing about it is not.
        if (exercises.quotedCount < 3 || exercises.coverage.notAttested > 0) {
          expect(
            exercises.note,
            `v${volume.volume}-${row.lesson} falls short and says nothing`,
          ).toBeTruthy();
        }
        expect(exercises.coverage.practised + exercises.coverage.notAttested)
          .toBe(exercises.coverage.lessonWords);
      }
    }
    expect(total).toBe(1000);
  });

  it("joins the whole-sentence Chinese by the sentence, not by its position", () => {
    // Two different lessons, and the reading of each has to carry its own
    // Chinese. An index join would still fill both — with each other's.
    for (const [volume, number] of [[1, 1], [2, 20]] as const) {
      const lesson = getJapaneseLesson(volume, number)!;
      expect(lesson.reading.length).toBeGreaterThan(0);
      for (const unit of lesson.reading) {
        expect(unit.text.trim(), `${lesson.key} ${unit.id}`).toBeTruthy();
        expect(unit.senseZh.trim(), `${lesson.key} ${unit.id} 沒有整句中譯`).toBeTruthy();
      }
    }
  });

  it("glosses every word it prints, or says the gloss is missing", () => {
    expect(overview.glossProgress.target).toBe(2000);
    expect(overview.glossProgress.glossed).toBe(2000);
    expect(overview.glossProgress.complete).toBe(true);
  });

  it("keys a lesson on both volume and lesson number", () => {
    expect(japaneseLessonKey(2, 7)).toBe("v2-7");
    expect(parseJapaneseLessonKey("v2-7")).toEqual({ volume: 2, lesson: 7 });
    // Links written before the second volume existed mean the first volume.
    expect(parseJapaneseLessonKey("7")).toEqual({ volume: 1, lesson: 7 });
    expect(parseJapaneseLessonKey("九")).toBeNull();
    expect(getJapaneseLesson(2, 7)?.lesson).toBe(7);
    expect(getJapaneseLesson(3, 1)).toBeNull();
    expect(getJapaneseLesson(1, 51)).toBeNull();
  });

  it("points every lesson at its own page", () => {
    const lessons = listJapaneseLessons();
    expect(lessons).toHaveLength(100);
    expect(new Set(lessons.map((lesson) => lesson.href)).size).toBe(100);
    expect(lessons[0].href).toBe("/original-readers/ja-lessons/v1-1");
  });
});
