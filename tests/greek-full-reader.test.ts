import { describe, expect, it } from "vitest";

import {
  getGreekLesson,
  getGreekLiturgy,
  getGreekReaderOverview,
  listGreekLessons,
} from "../data/originalReaders/greek-full-reader";

describe("complete 50-lesson New Testament Greek private reader", () => {
  const overview = getGreekReaderOverview();

  it("carries the frozen release counts", () => {
    expect(overview.counts.lessons).toBe(50);
    expect(overview.counts.vocabulary).toBe(1000);
    expect(overview.counts.memoryVerses).toBe(100);
    expect(overview.counts.scriptureChapters).toBe(25);
    expect(overview.counts.patristicReadings).toBe(25);
  });

  it("keeps the lesson sizes uneven while the textbook lasts", () => {
    const lessons = listGreekLessons();
    expect(lessons).toHaveLength(50);
    const textbookLessons = lessons.slice(0, 30);
    const sizes = new Set(textbookLessons.map((lesson) => lesson.vocabularyCount));
    // A single size across the textbook lessons would mean the curriculum had
    // been re-sliced into equal quotas, which is exactly what must not happen.
    expect(sizes.size).toBeGreaterThan(1);
    expect(textbookLessons.every((lesson) => lesson.vocabularySource.startsWith("BBG"))).toBe(true);

    const extensionLessons = lessons.slice(30);
    expect(extensionLessons).toHaveLength(20);
    expect(
      extensionLessons.every((lesson) => lesson.vocabularySource === "Mounce 頻率延伸"),
    ).toBe(true);
  });

  it("puts a complete chapter in lessons 1-25 and a patristic reading in 26-50", () => {
    const lessons = listGreekLessons();
    expect(lessons.slice(0, 25).every((lesson) => lesson.reading.kind === "scripture_chapter")).toBe(true);
    expect(lessons.slice(25).every((lesson) => lesson.reading.kind === "patristic_reading")).toBe(true);
  });

  it("gives every lesson exactly two memory verses", () => {
    for (const summary of listGreekLessons()) {
      const lesson = getGreekLesson(summary.lesson);
      expect(lesson, `lesson ${summary.lesson} missing`).toBeTruthy();
      expect(lesson!.memoryVerses).toHaveLength(2);
      expect(new Set(lesson!.memoryVerses.map((verse) => verse.ref)).size).toBe(2);
    }
  });

  it("never labels an excerpt as a complete work", () => {
    for (const summary of listGreekLessons()) {
      const reading = getGreekLesson(summary.lesson)!.reading;
      if (reading.completeness === "excerpt") {
        expect(reading.extent, `${reading.titleZh} excerpt without extent`).toBeTruthy();
        expect(reading.extent).not.toBe("全篇");
      }
    }
  });

  it("reads every corpus the contract promised", () => {
    const corpora = new Set(
      listGreekLessons()
        .slice(0, 25)
        .map((lesson) => lesson.reading.label),
    );
    expect(corpora).toContain("新約");
    expect(corpora).toContain("七十士譯本（正典）");
    expect(corpora).toContain("次經");
    expect(corpora).toContain("偽經");
  });

  it("ships no empty reading segment", () => {
    for (const summary of listGreekLessons()) {
      const reading = getGreekLesson(summary.lesson)!.reading;
      const segments = reading.verses || reading.segments || [];
      expect(segments.length, `${reading.titleZh} has no segments`).toBeGreaterThan(0);
      for (const segment of segments) {
        const text = segment.displayText || segment.sourceText || "";
        expect(text.trim(), `${reading.titleZh} ${segment.ref} is empty`).not.toBe("");
      }
    }
  });

  it("pairs Chinese with every Scripture verse that has a Chinese counterpart", () => {
    for (const summary of listGreekLessons().slice(0, 25)) {
      const reading = getGreekLesson(summary.lesson)!.reading;
      if (reading.corpusLabel === "偽經") continue;
      for (const verse of reading.verses || []) {
        if (verse.translationNote) continue;
        expect(
          (verse.translationZh || "").trim(),
          `${reading.ref} ${verse.ref} has no Chinese`,
        ).not.toBe("");
      }
    }
  });

  it("states the release status honestly while the gloss layer is incomplete", () => {
    if (overview.glossProgress.complete) {
      expect(overview.releaseStatus).not.toBe("source_frozen");
    } else {
      expect(overview.releaseStatus).toBe("source_frozen");
      expect(overview.glossProgress.glossed).toBeLessThan(overview.glossProgress.target);
    }
  });

  it("declares no recorded audio until real tracks exist", () => {
    expect(overview.audioStatus.status).toBe("not_recorded");
    expect(overview.audioStatus.recordedTrackCount).toBe(0);
  });

  it("carries the whole liturgy in celebration order", () => {
    const liturgy = getGreekLiturgy();
    expect(liturgy.summary.stepCount).toBeGreaterThan(300);
    expect(liturgy.sections.length).toBeGreaterThanOrEqual(20);

    const keys = liturgy.sections.map((section) => section.key);
    for (const required of ["great-litany", "trisagion", "creed", "anaphora", "lords-prayer", "dismissal"]) {
      expect(keys, `liturgy missing ${required}`).toContain(required);
    }
    expect(keys.indexOf("creed")).toBeLessThan(keys.indexOf("anaphora"));
    expect(keys.indexOf("anaphora")).toBeLessThan(keys.indexOf("lords-prayer"));
    expect(keys[keys.length - 1]).toBe("dismissal");

    const ordinals = liturgy.steps.map((step) => step.ordinal);
    expect(ordinals).toEqual([...ordinals].sort((a, b) => a - b));
    expect(liturgy.steps.every((step) => step.displayText.trim())).toBe(true);
  });

  it("rejects a lesson number outside 1-50", () => {
    expect(getGreekLesson(0)).toBeNull();
    expect(getGreekLesson(51)).toBeNull();
    expect(getGreekLesson(1.5)).toBeNull();
  });
});
